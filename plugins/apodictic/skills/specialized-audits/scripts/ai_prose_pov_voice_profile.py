#!/usr/bin/env python3
"""
ai_prose_pov_voice_profile.py — SETEC subprocess shim.

Per-POV-character voiceprints for multi-POV fiction. Reports pairwise
POV distance + voice-collapse verdict (a Burrows-Delta-driven check
on whether two POVs' voices have flattened into one).

**Opt-in audit.** Requires a JSONL manifest with `pov` annotations on
selected entries; weight is non-trivial (per-POV stylometric fit). Run
when a manuscript has 2+ POV characters AND voice singularity is a
suspected risk (Pass 7 Blind Swap fails, or AIC-1 + AIC-5 co-occur in
AI-Prose Calibration). Forwards to SETEC Voiceprint's
`pov_voice_profile.py`; see the pov-voice-profile reference for the
audit-level contract.
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

SURFACE = "pov_voice_profile"


def main(argv: list[str]) -> int:
    try:
        # Floor is data-driven from SETEC's capabilities manifest (R1),
        # not hardcoded. resolve_floor asserts the discovered
        # setec_version satisfies this surface's manifest
        # min_setec_version; the validated location is reused so the
        # script is not re-discovered at the bootstrap floor.
        _cap, manifest = resolve_floor(SURFACE)
        result = run_setec_script(
            "pov_voice_profile.py", argv, location=manifest.location
        )
    except (SetecDiscoveryError, SetecCapabilitiesError) as e:
        print(str(e), file=sys.stderr)
        return 2
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
