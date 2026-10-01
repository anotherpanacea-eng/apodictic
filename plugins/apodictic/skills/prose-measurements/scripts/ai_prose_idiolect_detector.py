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

from setec_runner import run_surface_cli  # noqa: E402
from setec_capabilities import (  # noqa: E402
    SetecCapabilitiesError,
    query_capabilities,
)
from setec_discovery import SetecDiscoveryError  # noqa: E402

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
    # The R2 dispatcher (run_surface_cli) is the single runtime authority for
    # the version floor, dependencies, and the schema_version 1.0 envelope. It
    # does NOT enforce R1 `required_groups`, so the consumer pre-checks those
    # here — manifest-driven (flag->group from `inputs[]`), skipping help/usage
    # requests — to give a clear error before handoff rather than a confusing
    # downstream failure. This is capability introspection, not a redundant
    # floor check (the dispatcher owns the floor).
    if _enforce_required_groups(argv):
        try:
            cap = query_capabilities().require(SURFACE)
        except (SetecDiscoveryError, SetecCapabilitiesError) as e:
            print(str(e), file=sys.stderr)
            return 2
        missing = cap.missing_required_groups(argv)
        if missing:
            print(
                f"idiolect_detector: missing a required input group: "
                f"{', '.join(missing)}. Per SETEC's R1 manifest this surface "
                f"requires one flag from each of "
                f"{', '.join(cap.required_groups)} (e.g. one --target-* source "
                f"and one --reference-* source).",
                file=sys.stderr,
            )
            return 2
    # Route through SETEC's normalized dispatcher (R2).
    return run_surface_cli(SURFACE, argv)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
