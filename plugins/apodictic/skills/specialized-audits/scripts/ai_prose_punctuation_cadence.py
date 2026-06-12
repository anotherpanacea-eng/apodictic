#!/usr/bin/env python3
"""
ai_prose_punctuation_cadence.py — SETEC subprocess shim.

Punctuation rhythm + interruption-grammar audit. Catches the
regularization patterns AI editing and professional copyediting often
produce before lexical-diversity signals fire (sentence-final
distribution, comma/period share, dash density, parenthetical
frequency).

Subsumes the territory the standalone em-dash-reduction skill covers
and reads it against a baseline, so the diagnosis goes beyond
"too many em-dashes" to "this passage's punctuation rhythm is
regularized against your own register." Forwards to SETEC Voiceprint's
`punctuation_cadence_audit.py`; see the punctuation-cadence reference
for the audit-level contract.
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

SURFACE = "punctuation_cadence_audit"


def main(argv: list[str]) -> int:
    try:
        # Floor is data-driven from SETEC's capabilities manifest (R1),
        # not hardcoded. resolve_floor asserts the discovered
        # setec_version satisfies this surface's manifest
        # min_setec_version; the validated location is reused so the
        # script is not re-discovered at the bootstrap floor.
        _cap, manifest = resolve_floor(SURFACE)
        result = run_setec_script(
            "punctuation_cadence_audit.py", argv, location=manifest.location
        )
    except (SetecDiscoveryError, SetecCapabilitiesError) as e:
        print(str(e), file=sys.stderr)
        return 2
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
