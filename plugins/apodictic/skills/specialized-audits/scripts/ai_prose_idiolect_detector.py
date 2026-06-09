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

SURFACE = "idiolect_detector"


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
