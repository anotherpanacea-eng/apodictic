#!/usr/bin/env python3
"""
setec_runner.py — pass-side helper for SETEC subprocess supplementation.

Wraps the common "discover SETEC, invoke a script, parse the
schema_version 1.0 envelope, classify warnings, return a structured
result" plumbing. APODICTIC passes that bolster their analysis with
SETEC measurements (Pass 3 Rhythm/Modulation, Pass 7 POV/Voice, the
AI-Prose Calibration audit, idiolect preservation, etc.) call into
this module rather than reimplementing the flow.

See docs/pass3-pass7-setec-supplement-spec.md §6.6 for the design and
§6.4 for the three-tier warnings classification.

Usage (caller builds the SETEC arg list; the runner adds --json and
handles the envelope):

    from setec_runner import run_supplement

    result = run_supplement(
        "variance_audit.py",
        ["draft.md", "--baseline-dir", "/path/to/baseline", "--no-tier3"],
    )

    if not result.available:
        # SETEC ran but couldn't produce a measurement
        print("SETEC N/A:", result.blocking_warnings)
        return

    print(result.results["tier1"]["sentence_length"]["burstiness_B"])
    for w in result.reliability_warnings:
        # Render these inline near the cited measurement
        ...
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from setec_discovery import (  # noqa: E402
    SetecDiscoveryError,
    SetecLocation,
    discover_setec,
    run_setec_script,
)


EXPECTED_SCHEMA_VERSION = "1.0"


# Three-tier warnings classification per spec §6.4. Patterns are
# matched case-insensitively against each warning string. The list is
# expected to grow as new SETEC scripts surface new warning shapes;
# unmatched warnings on an available=True envelope default to
# "cosmetic" tier (silent in pass output, available on drill-in).
RELIABILITY_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"text too short", re.IGNORECASE),
    re.compile(r"text length .* below", re.IGNORECASE),
    re.compile(r"below (?:the )?recommended (?:length |word )?threshold", re.IGNORECASE),
    re.compile(r"signal .* noisy", re.IGNORECASE),
    re.compile(r"signals? skipped", re.IGNORECASE),
    re.compile(r"tier \d+ (?:skipped|fell back|unavailable)", re.IGNORECASE),
    re.compile(r"(?:spacy|sentence-transformers|sklearn|transformers|torch) (?:not |un)available", re.IGNORECASE),
    re.compile(r"fell back to (?:tf-?idf|heuristic)", re.IGNORECASE),
    re.compile(r"insufficient (?:sentences|tokens|words)", re.IGNORECASE),
    re.compile(r"baseline (?:too small|insufficient)", re.IGNORECASE),
    re.compile(r"(?:dependency|dep) missing", re.IGNORECASE),
)


class SetecRunnerError(RuntimeError):
    """Raised when SETEC runs but the envelope is unparseable or invalid.

    Discovery and version-floor errors propagate as SetecDiscoveryError
    from the underlying setec_discovery module — callers should catch
    both. See spec §6.4 (blocking tier) for the recommended pass-side
    handling when SETEC cannot supply measurements.
    """


@dataclass
class SupplementResult:
    """Structured result of one SETEC subprocess call.

    The pass reads the fields it needs, renders reliability warnings
    inline next to measurements, and respects claim_license bounds
    when stating findings.
    """

    schema_version: str
    task_surface: str
    tool: str
    version: str
    available: bool
    target: dict[str, Any]
    baseline: dict[str, Any] | None
    results: dict[str, Any]
    claim_license: dict[str, Any] | None
    claim_license_rendered: str | None
    blocking_warnings: list[str] = field(default_factory=list)
    reliability_warnings: list[str] = field(default_factory=list)
    cosmetic_warnings: list[str] = field(default_factory=list)
    ai_status: str | None = None
    envelope: dict[str, Any] = field(default_factory=dict)
    returncode: int = 0


def classify_warning(warning: str) -> str:
    """Return 'reliability' if the warning matches a known reliability
    pattern, else 'cosmetic'. Blocking classification is decided by
    the envelope's `available` flag, not by warning text."""
    for pattern in RELIABILITY_PATTERNS:
        if pattern.search(warning):
            return "reliability"
    return "cosmetic"


def _classify_warnings(
    warnings: list[str], available: bool
) -> tuple[list[str], list[str], list[str]]:
    """Return (blocking, reliability, cosmetic). When available=False,
    every warning is treated as blocking — the envelope itself signaled
    that SETEC could not produce a measurement, so the warnings carry
    the explanation."""
    if not available:
        return list(warnings), [], []
    reliability: list[str] = []
    cosmetic: list[str] = []
    for w in warnings:
        if classify_warning(w) == "reliability":
            reliability.append(w)
        else:
            cosmetic.append(w)
    return [], reliability, cosmetic


def _coerce_envelope(envelope: dict[str, Any]) -> None:
    """Validate the minimum required keys of schema_version 1.0. Raises
    SetecRunnerError on malformed envelopes (defense-in-depth; the
    setec_discovery version floor should prevent this in practice)."""
    sv = envelope.get("schema_version")
    if sv != EXPECTED_SCHEMA_VERSION:
        raise SetecRunnerError(
            f"SETEC envelope schema_version={sv!r}, expected "
            f"{EXPECTED_SCHEMA_VERSION!r}. setec_discovery's version "
            f"floor should prevent this; check that the discovered "
            f"SETEC is recent enough."
        )
    required = ("task_surface", "tool", "version", "available", "target",
                "baseline", "results", "claim_license",
                "claim_license_rendered", "warnings")
    missing = [k for k in required if k not in envelope]
    if missing:
        raise SetecRunnerError(
            f"SETEC envelope missing required keys: {missing!r}. "
            f"Envelope keys present: {sorted(envelope.keys())!r}"
        )


def run_supplement(
    script: str,
    args: list[str],
    *,
    location: SetecLocation | None = None,
    min_version: tuple[int, ...] | None = None,
    json_out: bool = False,
) -> SupplementResult:
    """Run a SETEC script and return a SupplementResult.

    By default adds ``--json`` to the arg list if not already present and
    parses the schema_version 1.0 envelope from stdout. Classifies the
    warnings array per spec §6.4 and returns the result for the caller to
    consume.

    ``min_version`` enforces a per-script SETEC version floor higher
    than the framework-wide default in setec_discovery. Surface 6
    (``narrative_decision_audit.py``) shipped in SETEC 1.107.0, above the
    1.86.0 floor the texture-level surfaces use; callers consuming it
    pass ``min_version=(1, 107, 0)`` so an older SETEC fails discovery
    with the intended upgrade message rather than reaching the script and
    failing "script not found". When ``location`` is supplied the caller
    has already resolved discovery, so ``min_version`` is ignored.

    ``json_out`` selects the file-based JSON strategy for SETEC scripts
    whose ``--json`` surface writes the envelope to a path rather than to
    stdout. ``pov_voice_profile.py`` is the current case: it exposes
    ``--json-out <path>`` (argparse prefix-matching makes a bare
    ``--json`` resolve to ``--json-out`` and fail "expected one
    argument"). When ``json_out=True`` the runner allocates a temp path,
    injects ``--json-out <path>`` if absent, runs the script, reads the
    envelope back from the file, and removes the temp file. A
    caller-supplied ``--json-out`` path is honored and left in place.

    Raises ``SetecDiscoveryError`` if SETEC cannot be located or fails
    the version-floor check (callers handle this as the blocking tier
    per spec §6.4: pass falls back to LLM-only with the gap recorded).

    Raises ``SetecRunnerError`` if SETEC ran but produced output that
    does not conform to schema_version 1.0 (defense-in-depth; should
    not happen at the supported SETEC version floor).
    """
    if location is None and min_version is not None:
        location = discover_setec(min_version=min_version)
    args_with_json = list(args)
    tmp_json_path: str | None = None
    if json_out:
        if "--json-out" not in args_with_json:
            fd, tmp_json_path = tempfile.mkstemp(prefix="setec_", suffix=".json")
            os.close(fd)
            args_with_json = ["--json-out", tmp_json_path, *args_with_json]
    elif "--json" not in args_with_json:
        args_with_json = ["--json", *args_with_json]
    try:
        completed: subprocess.CompletedProcess = run_setec_script(
            script,
            args_with_json,
            location=location,
            capture_output=True,
        )
        if json_out:
            read_path = tmp_json_path
            if read_path is None:
                # Caller supplied their own --json-out path; recover it.
                read_path = args_with_json[args_with_json.index("--json-out") + 1]
            try:
                raw = Path(read_path).read_text(encoding="utf-8")
            except OSError as exc:
                raise SetecRunnerError(
                    f"SETEC {script} did not write a JSON envelope to "
                    f"{read_path} (returncode={completed.returncode}). "
                    f"Stderr (truncated): {completed.stderr[:500]!r}"
                ) from exc
            if not raw.strip():
                raise SetecRunnerError(
                    f"SETEC {script} wrote an empty JSON envelope to "
                    f"{read_path} (returncode={completed.returncode}). "
                    f"Stderr (truncated): {completed.stderr[:500]!r}"
                )
        else:
            if not completed.stdout.strip():
                raise SetecRunnerError(
                    f"SETEC {script} produced no stdout (returncode="
                    f"{completed.returncode}). Stderr (truncated): "
                    f"{completed.stderr[:500]!r}"
                )
            raw = completed.stdout
        try:
            envelope = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise SetecRunnerError(
                f"SETEC {script} JSON output did not parse: {exc}. "
                f"First 500 chars: {raw[:500]!r}"
            ) from exc
    finally:
        if tmp_json_path is not None:
            try:
                os.unlink(tmp_json_path)
            except OSError:
                pass
    _coerce_envelope(envelope)
    available = bool(envelope["available"])
    blocking, reliability, cosmetic = _classify_warnings(
        list(envelope.get("warnings") or []), available
    )
    return SupplementResult(
        schema_version=envelope["schema_version"],
        task_surface=envelope["task_surface"],
        tool=envelope["tool"],
        version=envelope["version"],
        available=available,
        target=envelope["target"],
        baseline=envelope.get("baseline"),
        results=envelope.get("results") or {},
        claim_license=envelope.get("claim_license"),
        claim_license_rendered=envelope.get("claim_license_rendered"),
        blocking_warnings=blocking,
        reliability_warnings=reliability,
        cosmetic_warnings=cosmetic,
        ai_status=envelope.get("ai_status"),
        envelope=envelope,
        returncode=completed.returncode,
    )


def _cli_main() -> int:
    """`python setec_runner.py SCRIPT [SETEC_ARG ...]` — convenience CLI.

    Useful for debugging the runner from a shell. Forwards args to the
    named SETEC script, prints the classified warning buckets and a
    compact summary, then exits with the SETEC script's return code.
    """
    if len(sys.argv) < 2:
        print(
            "Usage: setec_runner.py SCRIPT [SETEC_ARG ...]\n"
            "Example: setec_runner.py variance_audit.py draft.md --no-tier2",
            file=sys.stderr,
        )
        return 2
    script = sys.argv[1]
    args = sys.argv[2:]
    try:
        result = run_supplement(script, args)
    except SetecDiscoveryError as e:
        print(str(e), file=sys.stderr)
        return 2
    except SetecRunnerError as e:
        print(f"SETEC runner error: {e}", file=sys.stderr)
        return 3
    summary = {
        "schema_version": result.schema_version,
        "tool": result.tool,
        "version": result.version,
        "task_surface": result.task_surface,
        "available": result.available,
        "target": result.target,
        "baseline_present": result.baseline is not None,
        "blocking_warnings": result.blocking_warnings,
        "reliability_warnings": result.reliability_warnings,
        "cosmetic_warnings": result.cosmetic_warnings,
        "results_top_keys": sorted((result.results or {}).keys()),
    }
    print(json.dumps(summary, indent=2, default=str))
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(_cli_main())
