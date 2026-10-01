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

from setec_runner import run_surface_cli  # noqa: E402

SURFACE = "punctuation_cadence_audit"


def main(argv: list[str]) -> int:
    # Route the surface through SETEC's normalized dispatcher (R2): the
    # dispatcher resolves the surface from its capabilities manifest, enforces
    # the per-surface version floor + dependencies (returning R3 errors), runs
    # the script, and guarantees a schema_version 1.0 envelope on stdout. No
    # consumer-side floor pre-check: the dispatcher is the single runtime
    # authority (resolve_floor / the vendored manifest stay for the offline
    # drift gate + capability introspection, not a redundant runtime check).
    return run_surface_cli(SURFACE, argv)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
