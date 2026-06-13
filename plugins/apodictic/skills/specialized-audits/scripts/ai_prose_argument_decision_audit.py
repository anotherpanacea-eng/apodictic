#!/usr/bin/env python3
"""
ai_prose_argument_decision_audit.py — SETEC subprocess shim.

Argument-Decision audit (ArgScope) for the APODICTIC Development Editor.
Forwards to SETEC Voiceprint's `argument_decision_audit.py`, which scores a
public-debate / op-ed-register essay's argumentative STRUCTURE against Kim,
Chang, Pham & Iyyer 2026's human / LLM group means ("Argument Collapse",
arXiv:2606.01736) and emits a schema_version 1.0 envelope under the
`argument_decision_audit` task_surface. All CLI arguments pass through
unchanged; see SETEC's `--help` for the full surface (judge-backend
selection — manifest/mock/anthropic/openai/gemini — and the label manifest).

This is the argument-domain SIBLING of the narrative_decision_audit
(StoryScope) shim. Where the texture-level shims (variance/repetition/voice)
measure how sentences are *phrased*, and narrative-decision measures how a
*story* is built, this surface measures how an *argument* is built — the B1
structural arc (paragraph-role transition rates: support→proposal,
support→support, thesis-opening) and the B2 discourse-mode mix (argumentation
share). It measures argumentative DIVERSITY, not quality, accuracy, or
provenance. It is a structure-level complement to the dialectical-clarity /
warrant audits, not a substitute, and never issues a soundness verdict (it may
PRE-FLAG whether a dialectical-clarity run is informative, but never
adjudicates). See argument-decision-audit.md for the audit-level contract, the
3-tier register map, and the framing note.

Version floor: NOT hardcoded here, and NOT pre-checked consumer-side. Per the
R1 acceptance criterion and docs/setec-dependency-posture.md Decision 2, this
surface's floor is a property of the surface in SETEC's capabilities manifest
(`argument_decision_audit`'s `min_setec_version`, currently 1.116.0 — the
plugin-version at which ArgScope Increment A1 shipped, the first release tag
carrying this surface being `v1.116.0`). With R2 adoption, the normalized
dispatcher ENFORCES that floor at runtime: an out-of-floor SETEC comes back as
an R3 `version_floor` error envelope (available=False, naming both the
required floor and the observed version) rather than a missing-script error.
The consumer no longer runs resolve_floor as a redundant runtime pre-check;
resolve_floor + the vendored manifest remain the authority for the offline
drift gate and capability introspection only.

Handoff posture: the surface carries `handoff: experimental` in SETEC's
capabilities manifest. The envelope shape and the
target/results/claim_license block are committed; the aggregate-score math,
the B3/B4 `reused_signals`, and the judge-prompt pipeline may evolve before a
v0.2 stabilization. APODICTIC pins the per-signal `contributions` payload and
the claim_license block; it does NOT pin verdicts to SETEC's aggregate `score`
or to a specific judge model (see argument-decision-audit.md §Aggregate
posture and §Judge provenance).
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from setec_runner import run_surface_cli  # noqa: E402

SURFACE = "argument_decision_audit"


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
