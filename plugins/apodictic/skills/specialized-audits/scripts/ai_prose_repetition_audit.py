#!/usr/bin/env python3
"""
ai_prose_repetition_audit.py — SETEC subprocess shim.

Vocabulary over-representation against a baseline (Lexical Convergence
candidates for AIC-7). Forwards to SETEC Voiceprint's `repetition_audit.py`.
See ai-prose-calibration.md for the audit-level contract.
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

SURFACE = "repetition_audit"


def main(argv: list[str]) -> int:
    try:
        # Floor is data-driven from SETEC's capabilities manifest (R1),
        # not hardcoded. resolve_floor asserts the discovered
        # setec_version satisfies this surface's manifest
        # min_setec_version; the validated location is reused so the
        # script is not re-discovered at the bootstrap floor.
        _cap, manifest = resolve_floor(SURFACE)
        result = run_setec_script(
            "repetition_audit.py", argv, location=manifest.location
        )
    except (SetecDiscoveryError, SetecCapabilitiesError) as e:
        print(str(e), file=sys.stderr)
        return 2
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
