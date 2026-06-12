#!/usr/bin/env python3
"""
ai_prose_idiolect_detector.py — SETEC subprocess shim.

Idiolect detection + preservation list: surfaces the keyness-distinctive
words and collocations a writer uses idiosyncratically relative to a
reference corpus. The preservation list (`--preservation-output`) tells
downstream revision work which phrases NOT to normalize away.

Drives the /coach revision-coaching path: when a revision plan is built,
the coach can show this list so line-editing passes don't sand off
signature moves. Forwards to SETEC Voiceprint's `idiolect_detector.py`;
see ai-prose-calibration.md and the idiolect-preservation reference for
the audit-level contract.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from setec_discovery import SetecDiscoveryError, run_setec_script  # noqa: E402
from setec_capabilities import (  # noqa: E402
    SetecCapabilitiesError,
    resolve_floor,
)

SURFACE = "idiolect_detector"

# Help/usage requests must reach SETEC's own argparse so `--help`/`-h` render
# idiolect_detector's real help — never the consumer's required-group error.
_HELP_FLAGS = frozenset({"-h", "--help"})


def _enforce_required_groups(argv: list[str]) -> bool:
    """Whether to enforce required_groups for this invocation. A help/usage
    request (``-h`` / ``--help`` anywhere in argv) passes straight through to
    SETEC instead of being blocked by the group check — required_groups only
    gates an actual detection run."""
    return _HELP_FLAGS.isdisjoint(argv)


def main(argv: list[str]) -> int:
    try:
        # Floor is data-driven from SETEC's capabilities manifest (R1),
        # not hardcoded. resolve_floor asserts the discovered
        # setec_version satisfies this surface's manifest
        # min_setec_version; the validated location is reused so the
        # script is not re-discovered at the bootstrap floor.
        cap, manifest = resolve_floor(SURFACE)
        # R1 required_groups: the manifest declares idiolect needs one source
        # from each named group (one `target`, one `reference`). Validate the
        # forwarded argv satisfies them — except for help/usage requests, which
        # pass through so `--help` shows SETEC's real help, not a group error —
        # giving a clear, manifest-driven error rather than a confusing
        # downstream failure.
        if _enforce_required_groups(argv):
            missing = cap.missing_required_groups(argv)
            if missing:
                print(
                    f"idiolect_detector: missing a required input group: "
                    f"{', '.join(missing)}. Per SETEC's R1 manifest this "
                    f"surface requires one flag from each of "
                    f"{', '.join(cap.required_groups)} (e.g. one --target-* "
                    f"source and one --reference-* source).",
                    file=sys.stderr,
                )
                return 2
        result = run_setec_script(
            "idiolect_detector.py", argv, location=manifest.location
        )
    except (SetecDiscoveryError, SetecCapabilitiesError) as e:
        print(str(e), file=sys.stderr)
        return 2
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
