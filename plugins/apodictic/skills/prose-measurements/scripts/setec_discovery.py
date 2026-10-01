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

Version floors are NO LONGER hardcoded per surface here. Per
docs/setec-dependency-posture.md Decision 2 and the R1 acceptance
criterion, each surface's floor is a property of the surface, read from
SETEC's capabilities manifest (`capabilities.py emit --json`) by
setec_capabilities.resolve_floor — not from a constant in this module or
in a shim. The historical framework-wide `MIN_SETEC_VERSION = (1, 86, 0)`
constant and the narrative-decision shim's `(1, 107, 0)` constant are
gone; floor decisions route through the manifest.

What remains here is a single BOOTSTRAP floor: the minimal version that
guarantees the `capabilities emit` command + the R1 field bundle
(per-entry min_setec_version/json_delivery/inputs) exist, so the consumer
can run the query at all. A SETEC older than the bootstrap floor predates
R1 and fails discovery with an upgrade message (computational surfaces
hard-require SETEC — never a silent fallback). The bootstrap value lives
in setec_capabilities.BOOTSTRAP_SETEC_VERSION and is re-exported here as
the default floor for `discover_setec` / `run_setec_script`.

--------------------------------------------------------------------------
C3 thin-wrapper note (fleet-coordination/specs/setec-consumer-client-
contract.md): this module is now a thin POLICY wrapper over the runtime
vendored shared client, `_vendored_setec_client.py` (byte-identical to
setec-voiceprint's `scripts/setec/consumer_client.py`, refreshed by
`scripts/sync_setec.py`). The MECHANISM — the SemVer-subset parser/floor
semantics, the envelope dataclasses, and the subprocess runner — lives
there and is imported, not re-implemented. What stays LOCAL (consumer-
owned, not moved, per the spec's decision line) is APODICTIC's OWN policy:
  * the resolver order (SETEC_VOICEPRINT_DIR env var, then a marketplace
    search) — voicewright's sibling-checkout candidate does not apply here;
  * the BOOTSTRAP_SETEC_VERSION / MIN_SETEC_VERSION floor constants;
  * the CLI shim glue (`_cli_main`).
See tests/setec-contract/setec-client-symbol-inventory.json for the full
shared vs. apodictic_policy classification of every public symbol across
this module and its two siblings (setec_runner.py, setec_capabilities.py).
--------------------------------------------------------------------------
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _vendored_setec_client import (  # noqa: E402
    SetecDiscoveryError,
    SetecLocation,
    VersionParseError,
    build_location,
    meets_floor,
    parse_version,
    read_plugin_manifest,
    run_setec_script,
    version_precedence_key,
)

# BOOTSTRAP_SETEC_VERSION is the single source of truth for the discovery
# floor — "the version where `capabilities emit` + the R1 field bundle
# (per-entry min_setec_version/json_delivery/inputs) first exist", NOT the
# floor of any individual surface (those come from the manifest, via
# setec_capabilities). FINALIZED: pinned to the v1.113.0 SETEC release, the
# first release carrying R1 (capabilities emit) + R5 (contract fixtures); see
# setec-plugin.lock (provisional: false). It lives here (not in
# setec_capabilities) so this module has no import-time dependency on
# setec_capabilities, which imports from this module.
#
# CONSUMER-OWNED, NOT MOVED (spec C3's decision line): the shared vendored
# client never hardcodes a version floor, so this constant stays here even
# though the client supplies the mechanism that checks it.
BOOTSTRAP_SETEC_VERSION = (1, 114, 0)

# Backward-compatible module constant: the framework-wide default discovery
# floor is now the bootstrap floor, not the retired per-surface (1, 86, 0).
# Surfaces never read this for their own floor — that comes from the manifest.
MIN_SETEC_VERSION = BOOTSTRAP_SETEC_VERSION


def _install_instructions(min_version: tuple[int, ...] = MIN_SETEC_VERSION) -> str:
    """Render the install/upgrade message for a given required floor.

    The floor is parameterized so a caller can surface a *specific surface's*
    manifest floor (resolved via ``setec_capabilities.resolve_floor``) in the
    upgrade message, rather than always showing the bootstrap floor. Per-surface
    floors now come from SETEC's capabilities manifest (R1), not hardcoded
    constants."""
    return """\
SETEC Voiceprint is required for this APODICTIC AI-prose audit.

Install one of:
  1. Add SETEC's marketplace and install:
       /plugin marketplace add anotherpanacea-eng/setec-voiceprint
       /plugin install setec-voiceprint
     (then restart Claude Code so the marketplace path appears.)
  2. Or set SETEC_VOICEPRINT_DIR to point at a local SETEC checkout, e.g.:
       export SETEC_VOICEPRINT_DIR=/path/to/setec-voiceprint/plugins/setec-voiceprint

Minimum required version: {min_ver}
""".format(min_ver=".".join(str(p) for p in min_version))


# Backward-compatible module constant (framework-wide default floor).
INSTALL_INSTRUCTIONS = _install_instructions()


def _parse_version(version_str: str) -> tuple[int, ...]:
    """Legacy release-only accessor kept for callers that only need the
    release tuple for DISPLAY (never for a floor comparison — use
    `meets_floor` for that). Raises VersionParseError on an unparseable
    string; there is no more silent partial-parse ``()`` result. Thin
    wrapper over the vendored client's `parse_version`."""
    return tuple(parse_version(version_str)["release"])


def _looks_like_setec_root(path: Path) -> bool:
    """APODICTIC's own plugin-root recognition: requires BOTH a `scripts/`
    subdirectory AND a plugin.json named `setec-voiceprint` at THIS exact
    path (no nested-repo-root normalization — unlike the vendored client's
    more permissive `normalize_to_plugin_root`, which also accepts a repo
    root containing `plugins/setec-voiceprint`). Kept local + narrower than
    the shared mechanism so `discover_setec`'s existing candidate-by-
    candidate error behavior is unchanged by C3 (a refactor-in-place, not
    a behavior broadening)."""
    if not path.is_dir():
        return False
    if not (path / "scripts").is_dir():
        return False
    manifest = read_plugin_manifest(path)
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
    """Locate SETEC using APODICTIC's OWN resolver order (env var, then
    marketplace search — this repo's C3 policy, never moved into the shared
    client). Raises SetecDiscoveryError on failure. Candidate VALIDATION
    (recognizing a plugin root, parsing its version, checking the floor,
    building the SetecLocation) delegates to the vendored client's
    `build_location` mechanism."""
    env_root = _candidate_from_env()
    if env_root is not None:
        if not _looks_like_setec_root(env_root):
            raise SetecDiscoveryError(
                f"SETEC_VOICEPRINT_DIR is set to {env_root}, but that path is "
                f"not a SETEC plugin root (missing scripts/ or plugin.json with "
                f"name='setec-voiceprint').\n\n{_install_instructions(min_version)}"
            )
        return build_location(
            env_root, "env", min_version,
            install_instructions=lambda: _install_instructions(min_version),
        )

    for candidate in _candidates_from_marketplace():
        if _looks_like_setec_root(candidate):
            return build_location(
                candidate, "marketplace", min_version,
                install_instructions=lambda: _install_instructions(min_version),
            )

    raise SetecDiscoveryError(
        "SETEC Voiceprint plugin not found. Searched: SETEC_VOICEPRINT_DIR "
        "env var, ~/.claude/plugins/marketplaces/*/plugins/setec-voiceprint."
        f"\n\n{_install_instructions(min_version)}"
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
