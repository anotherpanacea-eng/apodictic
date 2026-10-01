#!/usr/bin/env python3
"""
ai_prose_agd_move_scan.py — SETEC subprocess shim.

AGD Move Scan (R3B producer/consumer seam) for the APODICTIC Development
Editor. Forwards to SETEC Voiceprint's `agd_move_scan.py`, which reports
LOCATED, verbatim-anchored candidate AGD move observations for an
argument-shaped nonfiction passage — each performative move a pluggable LLM
judge identifies: ASSURING (authority/certainty in place of support), GUARDING
(a claim weakened to shrink its commitment), DISCOUNTING (an objection
anticipated and set aside, including cue-free structural dismissal) — with its
family, verbatim span, paragraph index, and surface cue (null = cue-free). It
emits a schema_version 1.0 envelope under the `agd_move_scan` task_surface. All
CLI arguments pass through unchanged; see SETEC's `--help` for the full surface
(judge-backend selection — manifest/mock/anthropic/openai/gemini/agent_host —
and the observation manifest).

OBSERVATIONS ONLY (R4A ADR D5). The surface is a POINTER, not a finding: every
observation is a legitimate move's LOCATION, never a code, verdict, score, or
aggregate. The AGD Move Audit (argument-agd; Argument_State §10.9) ALONE
challenges each move and assigns codes. Observation COUNT is location data, not
a quality signal. This shim consumes the located observations as a candidate
inventory for that audit's own Layer-1 identification pass; it adjudicates
nothing. See argument-agd-audit.md for the audit-level consumption contract
(the Layer-1 pre-pass, the §10.9 `Scan:` coverage line, and the cross-check
procedure).

Artifact transport (ORCHESTRATION, not shim code): this shim is the canonical
3-line stdout forwarder — `run_surface_cli` is stdout-only and persists no
file. The AGD Move Audit's Layer-1 pre-pass reads `<run folder>/agd_move_scan.json`;
the audit/skill INSTRUCTION produces that file by running this shim and
redirecting its stdout there before the audit begins (a non-zero exit or an
unparseable capture ⇒ the artifact is absent/malformed ⇒ the §10.9 manifest
records `Scan: not consulted (error)`). See argument-agd-audit.md § Layer-1
scan pre-pass.

Version floor: NOT hardcoded here, and NOT pre-checked consumer-side. Per the
R1 acceptance criterion and docs/setec-dependency-posture.md Decision 2, this
surface's floor is a property of the surface in SETEC's capabilities manifest
(`agd_move_scan`'s `min_setec_version`, currently 1.124.0 — the plugin-version
at which the R3B producer surface shipped, the first release tag carrying it
being `v1.124.0`). With R2 adoption, the normalized dispatcher ENFORCES that
floor at runtime: an out-of-floor SETEC comes back as an R3 `version_floor`
error envelope (available=False, naming both the required floor and the
observed version) rather than a missing-script error. The consumer no longer
runs resolve_floor as a redundant runtime pre-check; resolve_floor + the
vendored manifest remain the authority for the offline drift gate and
capability introspection only.

Handoff posture: the surface carries `handoff: experimental` in SETEC's
capabilities manifest. The located-observation envelope (family + verbatim span
+ paragraph_index + cue, plus the `results.observations` list and the
claim_license refusals) is committed; the judge-prompt pipeline may evolve
before a v0.2 stabilization. APODICTIC pins `results.observations` and the
claim_license block; it does NOT pin verdicts to any aggregate (the surface
emits none — no counts, no tallies, no rollups) or to a specific judge model
(read `judge.judge_identity`; a `mock` judge is a deterministic test stub).
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from setec_runner import run_surface_cli  # noqa: E402

SURFACE = "agd_move_scan"


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
