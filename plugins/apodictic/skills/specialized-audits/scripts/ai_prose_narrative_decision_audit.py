#!/usr/bin/env python3
"""
ai_prose_narrative_decision_audit.py — SETEC subprocess shim.

Narrative-Decision audit (StoryScope, SETEC Surface 6) for the APODICTIC
Development Editor. Forwards to SETEC Voiceprint's
`narrative_decision_audit.py`, which scores prose against the 30 core
narrative-decision features (33 signals) from Russell et al. 2026's
StoryScope paper and emits a schema_version 1.0 envelope under the
`narrative_decision_audit` task_surface. All CLI arguments pass through
unchanged; see SETEC's `--help` for the full surface (judge-backend
selection, prompt-version pinning, baseline manifest, etc.).

Where the texture-level shims (variance/repetition/voice) measure how a
manuscript's sentences are *phrased*, this surface measures how its
story is *built* — themes, plot structure, sensory register, reader
stance, temporal arrangement. It is a structure-level complement to
AI-Prose Calibration, not a substitute. See narrative-decision-audit.md
for the audit-level contract and the framing note.

Version floor: NOT hardcoded here, and NOT pre-checked consumer-side. Per
the R1 acceptance criterion and docs/setec-dependency-posture.md Decision 2,
this surface's floor is a property of the surface in SETEC's capabilities
manifest (`narrative_decision_audit`'s `min_setec_version`, currently 1.107.0
— the plugin-version at which Surface 6 / StoryScope shipped, PRs
#128/#129/#130). With R2 adoption, the normalized dispatcher ENFORCES that
floor at runtime: an out-of-floor SETEC comes back as an R3 `version_floor`
error envelope (available=False, naming both the required floor and the
observed version) rather than a missing-script error. The consumer no longer
runs resolve_floor as a redundant runtime pre-check; resolve_floor + the
vendored manifest remain the authority for the offline drift gate and
capability introspection only.

Handoff posture: the surface carries `handoff: experimental` in SETEC's
capabilities manifest. The envelope shape and the
target/baseline/results/claim_license block are committed; the
aggregate-score math and the judge-prompt pipeline may evolve before a
v0.2 stabilization. APODICTIC pins the per-signal `contributions`
payload and the claim_license block; it does NOT pin verdicts to SETEC's
aggregate `score` or to a specific judge model (see
narrative-decision-audit.md §Aggregate posture and §Judge provenance).
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from setec_runner import run_surface_cli  # noqa: E402

SURFACE = "narrative_decision_audit"


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
