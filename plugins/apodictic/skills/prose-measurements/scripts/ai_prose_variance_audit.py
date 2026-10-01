#!/usr/bin/env python3
"""
ai_prose_variance_audit.py — SETEC subprocess shim.

Layer A distributional diagnostics for the AI-Prose Calibration audit.
Forwards to SETEC Voiceprint's `variance_audit.py`. All CLI arguments
pass through unchanged; see SETEC's `--help` for the full surface
(includes new options unavailable in the pre-shim APODICTIC version,
e.g. `--tier4`, `--aic7/8/9`, `--window-size`, `--bootstrap`).

The substrate swap was decided in Phase 1 of the APODICTIC ↔ SETEC
integration (2026-05-17) and implemented in Phase 2: APODICTIC retires
its in-tree variance code and delegates to SETEC so stylometry develops
in one place. See ai-prose-calibration.md for the audit-level contract.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from setec_runner import run_surface_cli  # noqa: E402

SURFACE = "variance_audit"


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
