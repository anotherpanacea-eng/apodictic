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

from setec_runner import run_surface_cli  # noqa: E402

SURFACE = "pov_voice_profile"


def main(argv: list[str]) -> int:
    # Route the surface through SETEC's normalized dispatcher (R2): the
    # dispatcher resolves the surface from its capabilities manifest, enforces
    # the per-surface version floor + dependencies (returning R3 errors), runs
    # the script, and guarantees a schema_version 1.0 envelope on stdout. For
    # pov_voice_profile specifically, the underlying script writes its envelope
    # to a private file artifact (default-private policy for voice-cloning
    # input); the dispatcher PROJECTS that artifact to stdout, so this shim
    # does NOT pass --json-out, allocate an ai-prose-baselines-private/
    # tempdir, or set the old json_out=True special-case. One stdout path. No
    # consumer-side floor pre-check: the dispatcher is the single runtime
    # authority (resolve_floor / the vendored manifest stay for the offline
    # drift gate + capability introspection, not a redundant runtime check).
    return run_surface_cli(SURFACE, argv)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
