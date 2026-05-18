#!/usr/bin/env python3
"""
setec_discovery.py

Locate the SETEC Voiceprint plugin on disk and shell out to its scripts.

APODICTIC delegates AI-prose and voice-coherence work to SETEC. This helper
finds the SETEC scripts directory, validates the minimum version, and runs
SETEC scripts as subprocesses.

Discovery order:
  1. SETEC_VOICEPRINT_DIR env var (explicit override). Points at the plugin
     root (the directory that contains `.claude-plugin/plugin.json` and
     `scripts/`). Required to be valid when set; no silent fallback.
  2. Standard marketplace install: ~/.claude/plugins/marketplaces/*/plugins/setec-voiceprint
  3. Hard error with install instructions.

Min version: 1.86.0 — the SETEC release in which schema_version 1.0 JSON
envelope coverage completed across every script APODICTIC delegates to
(variance_audit, manuscript_audit, repetition_audit, voice_distance,
voice_profile). The four-tier ThresholdSpec calibration taxonomy that
APODICTIC's audit-interpretation logic also depends on was in place
earlier (1.66.0); the 1.86.0 floor exists because below it the consumed
JSON shape differs across entry points and downstream parsing breaks.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

MIN_SETEC_VERSION = (1, 86, 0)
INSTALL_INSTRUCTIONS = """\
SETEC Voiceprint is required for the AI-Prose Calibration audit.

Install one of:
  1. Add SETEC's marketplace and install:
       /plugin marketplace add anotherpanacea-eng/setec-voiceprint
       /plugin install setec-voiceprint
     (then restart Claude Code so the marketplace path appears.)
  2. Or set SETEC_VOICEPRINT_DIR to point at a local SETEC checkout, e.g.:
       export SETEC_VOICEPRINT_DIR=/path/to/setec-voiceprint/plugins/setec-voiceprint

Minimum required version: {min_ver}
""".format(min_ver=".".join(str(p) for p in MIN_SETEC_VERSION))


@dataclass
class SetecLocation:
    plugin_root: Path
    scripts_dir: Path
    version: tuple[int, ...]
    version_str: str
    source: str  # "env" | "marketplace"


class SetecDiscoveryError(RuntimeError):
    """Raised when SETEC cannot be located or fails the version check."""


def _read_plugin_manifest(plugin_root: Path) -> dict | None:
    """Return the parsed plugin.json for a SETEC plugin root, or None if
    the manifest is missing or unreadable."""
    candidates = [
        plugin_root / ".claude-plugin" / "plugin.json",
        plugin_root / "plugin.json",
    ]
    for path in candidates:
        if path.exists():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                return None
    return None


def _parse_version(version_str: str) -> tuple[int, ...]:
    """Parse a semver-ish version string into a tuple of ints. Non-numeric
    suffixes are dropped (e.g. '1.66.0-beta' -> (1, 66, 0))."""
    parts: list[int] = []
    for component in version_str.split("."):
        digits = ""
        for ch in component:
            if ch.isdigit():
                digits += ch
            else:
                break
        if not digits:
            break
        parts.append(int(digits))
    return tuple(parts)


def _looks_like_setec_root(path: Path) -> bool:
    if not path.is_dir():
        return False
    if not (path / "scripts").is_dir():
        return False
    manifest = _read_plugin_manifest(path)
    if not manifest:
        return False
    return manifest.get("name") == "setec-voiceprint"


def _candidate_from_env() -> Path | None:
    value = os.environ.get("SETEC_VOICEPRINT_DIR")
    if not value:
        return None
    return Path(value).expanduser().resolve()


def _candidates_from_marketplace() -> list[Path]:
    home = Path.home()
    base = home / ".claude" / "plugins" / "marketplaces"
    if not base.is_dir():
        return []
    return sorted(base.glob("*/plugins/setec-voiceprint"))


def discover_setec(min_version: tuple[int, ...] = MIN_SETEC_VERSION) -> SetecLocation:
    """Locate SETEC. Raises SetecDiscoveryError on failure."""
    env_root = _candidate_from_env()
    if env_root is not None:
        if not _looks_like_setec_root(env_root):
            raise SetecDiscoveryError(
                f"SETEC_VOICEPRINT_DIR is set to {env_root}, but that path is "
                f"not a SETEC plugin root (missing scripts/ or plugin.json with "
                f"name='setec-voiceprint').\n\n{INSTALL_INSTRUCTIONS}"
            )
        return _build_location(env_root, "env", min_version)

    for candidate in _candidates_from_marketplace():
        if _looks_like_setec_root(candidate):
            return _build_location(candidate, "marketplace", min_version)

    raise SetecDiscoveryError(
        "SETEC Voiceprint plugin not found. Searched: SETEC_VOICEPRINT_DIR "
        "env var, ~/.claude/plugins/marketplaces/*/plugins/setec-voiceprint."
        f"\n\n{INSTALL_INSTRUCTIONS}"
    )


def _build_location(
    plugin_root: Path, source: str, min_version: tuple[int, ...]
) -> SetecLocation:
    manifest = _read_plugin_manifest(plugin_root)
    if not manifest:
        raise SetecDiscoveryError(
            f"Found SETEC plugin root at {plugin_root}, but plugin.json is "
            f"unreadable.\n\n{INSTALL_INSTRUCTIONS}"
        )
    version_str = str(manifest.get("version", ""))
    version = _parse_version(version_str)
    if not version:
        raise SetecDiscoveryError(
            f"SETEC plugin.json at {plugin_root} has missing or unparseable "
            f"version: {version_str!r}.\n\n{INSTALL_INSTRUCTIONS}"
        )
    if version < min_version:
        min_str = ".".join(str(p) for p in min_version)
        raise SetecDiscoveryError(
            f"SETEC version {version_str} found at {plugin_root}, but APODICTIC "
            f"requires {min_str} or newer.\n\n{INSTALL_INSTRUCTIONS}"
        )
    return SetecLocation(
        plugin_root=plugin_root,
        scripts_dir=plugin_root / "scripts",
        version=version,
        version_str=version_str,
        source=source,
    )


def run_setec_script(
    script_name: str,
    args: list[str],
    *,
    location: SetecLocation | None = None,
    check: bool = False,
    capture_output: bool = False,
) -> subprocess.CompletedProcess:
    """Run a SETEC script as a subprocess.

    `script_name` is the bare filename inside SETEC's scripts/ dir
    (e.g. 'variance_audit.py'). `args` is the argument list passed after it.

    cwd is intentionally inherited from the caller so user-supplied
    relative paths (the input file, --baseline-dir, --out, --anchors)
    resolve where the user expects. SETEC scripts import sibling modules
    via Python's automatic sys.path[0]=script-dir and read internal data
    files via Path(__file__), so they don't need cwd at the plugin root.
    """
    if location is None:
        location = discover_setec()
    script_path = location.scripts_dir / script_name
    if not script_path.is_file():
        raise SetecDiscoveryError(
            f"SETEC script {script_name} not found at {script_path}. "
            f"SETEC version {location.version_str} may be missing this entry "
            f"point; verify the script name or upgrade SETEC."
        )
    cmd = [sys.executable, str(script_path), *args]
    return subprocess.run(
        cmd,
        check=check,
        capture_output=capture_output,
        text=True,
    )


def _cli_main() -> int:
    """`python setec_discovery.py` prints the discovered SETEC location.

    Useful for debugging path/version problems from the shell."""
    try:
        loc = discover_setec()
    except SetecDiscoveryError as e:
        print(str(e), file=sys.stderr)
        return 2
    payload = {
        "plugin_root": str(loc.plugin_root),
        "scripts_dir": str(loc.scripts_dir),
        "version": loc.version_str,
        "source": loc.source,
        "min_version_required": ".".join(str(p) for p in MIN_SETEC_VERSION),
    }
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli_main())
