#!/usr/bin/env python3
"""Fresh packet-only drafting through the documented Claude Code bare runtime.

No model call runs on import or during capability discovery. The isolated call
accepts packet and contract bytes; only the outer coordinator knows the project
and ledger head. Requires Claude Code >= 2.1.286 and an explicitly configured
ANTHROPIC_API_KEY. It never falls back to an ambient agent or subscription session.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from typing import Mapping, Sequence


MINIMUM_CLAUDE_VERSION = (2, 1, 286)
# Operational environment and explicitly configured API credentials only. In
# particular, do not carry NODE_OPTIONS, PYTHONPATH, CLAUDE*, MCP*, provider
# endpoint overrides, project settings or inherited agent/session identifiers.
_ENVIRONMENT_KEYS = frozenset({
    "PATH", "SYSTEMROOT", "SYSTEMDRIVE", "WINDIR", "TEMP", "TMP", "TMPDIR", "HOME",
    "USERPROFILE", "APPDATA", "LOCALAPPDATA", "COMSPEC", "PATHEXT",
    "LANG", "LC_ALL", "SSL_CERT_FILE", "SSL_CERT_DIR", "NODE_EXTRA_CA_CERTS",
    "HTTPS_PROXY", "HTTP_PROXY", "NO_PROXY", "ANTHROPIC_API_KEY",
})
_REQUIRED_FLAGS = (
    "--bare", "--tools", "--disallowedTools", "--strict-mcp-config",
    "--setting-sources", "--disable-slash-commands", "--no-session-persistence",
    "--system-prompt", "--output-format", "--no-chrome",
)


class DrafterError(Exception):
    def __init__(self, code: str, message: str, input_files: dict | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.input_files = input_files


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _load_json(text: str):
    def invalid_constant(value):
        raise ValueError("non-JSON numeric constant")
    return json.loads(text, object_pairs_hook=_unique_object,
                      parse_constant=invalid_constant)


def _utf8(raw: bytes, label: str) -> str:
    try:
        if not isinstance(raw, bytes):
            raise TypeError("not bytes")
        return raw.decode("utf-8", errors="strict")
    except (UnicodeError, TypeError) as exc:
        raise DrafterError("DRAFTER-INPUT-INVALID", f"{label} must be strict UTF-8 bytes") from exc


def _environment(source: Mapping[str, str]) -> dict[str, str]:
    # Windows environment names are case-insensitive; preserve canonical names.
    upper = {key.upper(): value for key, value in source.items()}
    result = {key: upper[key] for key in _ENVIRONMENT_KEYS if key in upper}
    result["CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC"] = "1"
    return result


def _response(raw: bytes) -> tuple[bytes, bytes]:
    """Require an empty runtime tool inventory and one successful raw response."""
    try:
        text = raw.decode("utf-8", errors="strict")
        events = [_load_json(line) for line in text.split("\n") if line.strip()]
        if not events or any(not isinstance(event, dict) for event in events):
            raise ValueError("invalid event stream")
        initializations = [event for event in events
                           if event.get("type") == "system" and event.get("subtype") == "init"]
        if len(initializations) != 1:
            raise ValueError("missing runtime inventory")
        initialization = initializations[0]
        # These arrays are mandatory in the supported CLI's system/init grammar,
        # including when empty (CLI 2.1.288 serializer and SDKSystemMessage).
        if any(initialization.get(key) != [] for key in ("tools", "mcp_servers", "plugins", "skills")):
            raise DrafterError("DRAFTER-ISOLATION-UNAVAILABLE", "runtime reported tools, MCP servers, plugins or skills")
        for event in events:
            if event.get("type") in {"tool_use", "tool_result", "server_tool_use"} or event.get("parent_tool_use_id"):
                raise DrafterError("DRAFTER-ISOLATION-UNAVAILABLE", "runtime emitted a forbidden tool or delegation exchange")
            if event.get("type") == "system" and event.get("subtype") in {
                "hook_started", "hook_progress", "hook_response", "plugin_install",
            }:
                raise DrafterError("DRAFTER-ISOLATION-UNAVAILABLE", "runtime executed an ambient startup hook or plugin")
            message = event.get("message")
            if isinstance(message, dict):
                content = message.get("content", [])
                if isinstance(content, list) and any(isinstance(block, dict) and
                        block.get("type") in {"tool_use", "tool_result", "server_tool_use"}
                        for block in content):
                    raise DrafterError("DRAFTER-ISOLATION-UNAVAILABLE", "runtime emitted a forbidden tool exchange")
        results = [event for event in events if event.get("type") == "result"]
        if len(results) != 1:
            raise ValueError("one result required")
        result = results[0]
        if result.get("is_error") is not False or result.get("subtype") != "success":
            raise DrafterError("DRAFTER-RUNTIME-FAILED", "isolated drafting did not return a successful result")
        if not isinstance(result.get("result"), str):
            raise ValueError("missing result text")
        returned = _load_json(result["result"])
        if not isinstance(returned, dict) or set(returned) != {"draft", "passage_map"}:
            raise ValueError("return only draft and passage_map")
        if any(not isinstance(returned[key], str) for key in ("draft", "passage_map")):
            raise ValueError("draft/map must be strings")
        return (returned["draft"].encode("utf-8", errors="strict"),
                returned["passage_map"].encode("utf-8", errors="strict"))
    except DrafterError:
        raise
    except (ValueError, TypeError, UnicodeError) as exc:
        # Do not repeat model responses or runtime diagnostics into error messages.
        raise DrafterError("DRAFTER-OUTPUT-INVALID", "runtime must return one strict JSON draft/map response with an empty tool inventory") from exc


class ClaudeBareRuntime:
    """A configurable Claude executable (or trusted executable wrapper).

    Configuration belongs to the invoker. It is not accepted from packet strings.
    Supplying a command prefix also supports installation wrappers and synthetic
    subprocess fixtures; all isolation flags are appended by this adapter.
    """

    def __init__(self, command: Sequence[str] | None = None,
                 environ: Mapping[str, str] | None = None, timeout: float = 300):
        executable = shutil.which("claude") if command is None else None
        self.command = tuple(command) if command is not None else ((executable,) if executable else ())
        self.environ = _environment(os.environ if environ is None else environ)
        self.timeout = timeout

    def _check(self, cwd: str) -> None:
        if (not self.command or any(not isinstance(part, str) or not part or part.startswith("-") for part in self.command)
                or not isinstance(self.timeout, (int, float)) or isinstance(self.timeout, bool)
                or not 0 < self.timeout <= 3600):
            raise DrafterError("DRAFTER-ISOLATION-UNAVAILABLE", "a supported Claude executable and bounded timeout are required")
        try:
            version = subprocess.run([*self.command, "--version"], cwd=cwd, env=self.environ,
                                     capture_output=True, timeout=15, check=False)
            match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+) \(Claude Code\)\s*",
                                 version.stdout.decode("utf-8", errors="strict"))
            if version.returncode or not match or tuple(map(int, match.groups())) < MINIMUM_CLAUDE_VERSION:
                raise DrafterError("DRAFTER-ISOLATION-UNAVAILABLE", "Claude Code 2.1.286 or later is required for bare context isolation")
            help_result = subprocess.run([*self.command, "--help"], cwd=cwd, env=self.environ,
                                        capture_output=True, timeout=15, check=False)
            help_text = help_result.stdout.decode("utf-8", errors="strict")
            if help_result.returncode or any(flag not in help_text for flag in _REQUIRED_FLAGS):
                raise DrafterError("DRAFTER-ISOLATION-UNAVAILABLE", "runtime does not advertise the required isolation controls")
        except DrafterError:
            raise
        except (OSError, subprocess.TimeoutExpired, UnicodeError) as exc:
            raise DrafterError("DRAFTER-ISOLATION-UNAVAILABLE", "runtime capability discovery failed without drafting") from exc
        if not self.environ.get("ANTHROPIC_API_KEY", "").strip():
            raise DrafterError("DRAFTER-ISOLATION-UNAVAILABLE", "bare drafting requires an explicitly configured ANTHROPIC_API_KEY; subscription sessions are not an isolation fallback")

    def invoke_drafter(self, packet_bytes: bytes, contract_bytes: bytes) -> tuple[bytes, bytes]:
        packet = _utf8(packet_bytes, "packet")
        contract = _utf8(contract_bytes, "contract")
        if not packet.strip() or not contract.strip():
            raise DrafterError("DRAFTER-INPUT-INVALID", "packet and drafting contract must be nonempty")
        # The child starts outside every project and receives no filenames, head,
        # digest, chat history, tool output, delegated-agent definition or resume ID.
        with tempfile.TemporaryDirectory(prefix="apodictic-drafter-") as neutral:
            self._check(neutral)
            command = [*self.command, "--bare", "--print", "--tools", "",
                       "--disallowedTools", "*", "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}',
                       "--setting-sources", "", "--settings", '{"disableAllHooks":true}',
                       "--disable-slash-commands", "--no-session-persistence", "--no-chrome",
                       "--system-prompt", contract, "--output-format", "stream-json", "--verbose"]
            try:
                completed = subprocess.run(command, input=packet_bytes, cwd=neutral,
                                           env=self.environ, capture_output=True,
                                           timeout=self.timeout, check=False)
            except (OSError, subprocess.TimeoutExpired) as exc:
                raise DrafterError("DRAFTER-RUNTIME-FAILED", "isolated drafting process failed or timed out") from exc
            if completed.returncode:
                raise DrafterError("DRAFTER-RUNTIME-FAILED", "isolated drafting process returned an error")
            return _response(completed.stdout)


def _contract_bytes() -> bytes:
    path = Path(__file__).resolve().parents[1] / "skills/core-editor/references/craft/reconstruction-drafting.md"
    try:
        return path.read_bytes()
    except OSError as exc:
        raise DrafterError("DRAFTER-CONTRACT-UNAVAILABLE", "the shipped reconstruction drafting contract is unavailable") from exc


def run_project(project: str | Path, runtime: ClaudeBareRuntime | None = None) -> dict:
    """Freeze packet/head together, draft in isolation, then ask the engine to emit."""
    import approval_graph
    import reconstruction_draft

    snapshot = reconstruction_draft.export_snapshot(project)
    digest = hashlib.sha256(snapshot.packet_bytes).hexdigest()
    draft, passage_map = (runtime or ClaudeBareRuntime()).invoke_drafter(
        snapshot.packet_bytes, _contract_bytes())
    root = approval_graph._project_root(project)
    # Ordinary retained inputs, not a transaction/cache authority. Preserve them
    # after either success or refusal so mixed-pair recovery has the returned bytes.
    directory = Path(tempfile.mkdtemp(prefix="Reconstruction_Input_", dir=root))
    inputs = {"draft_file": str(directory / "draft.md"), "map_file": str(directory / "passage-map.md")}
    try:
        for key, raw in (("draft_file", draft), ("map_file", passage_map)):
            with open(inputs[key], "xb") as stream:
                approval_graph._write_all(stream, raw)
                stream.flush()
                os.fsync(stream.fileno())
        result = reconstruction_draft.emit(
            project, inputs["draft_file"], inputs["map_file"], snapshot.ledger_count,
            snapshot.ledger_hash, digest)
    except approval_graph.ApprovalGraphError as exc:
        raise DrafterError(exc.code, exc.message, inputs) from exc
    except OSError as exc:
        raise DrafterError("DRAFTER-INPUT-PRESERVATION-FAILED", "returned inputs could not be fully preserved", inputs) from exc
    return {**result, "input_files": inputs}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project")
    parser.add_argument("--run", action="store_true", required=True)
    parser.add_argument("--claude", help="trusted Claude executable; defaults to claude on PATH")
    parser.add_argument("--timeout", type=float, default=300)
    args = parser.parse_args(argv)
    try:
        runtime = ClaudeBareRuntime((args.claude,) if args.claude else None, timeout=args.timeout)
        result = run_project(args.project, runtime)
        sys.stdout.buffer.write((json.dumps(result, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8"))
        # Successful production and semantic acceptance are distinct. emit()
        # reports ACTION-REQUIRED even though both artifacts were produced.
        return 0
    except DrafterError as exc:
        result = {"verdict": "ACTION-REQUIRED", "findings": [{"code": exc.code, "message": exc.message}]}
        if exc.input_files is not None:
            result["input_files"] = exc.input_files
        sys.stderr.buffer.write((json.dumps(result, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8"))
        return 1
    except Exception as exc:
        # Engine refusal before invocation has no returned inputs to preserve.
        import approval_graph
        if isinstance(exc, approval_graph.ApprovalGraphError):
            result = {"verdict": "ACTION-REQUIRED", "findings": [{"code": exc.code, "message": exc.message}]}
            sys.stderr.buffer.write((json.dumps(result, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8"))
            return 1
        raise


if __name__ == "__main__":
    raise SystemExit(main())
