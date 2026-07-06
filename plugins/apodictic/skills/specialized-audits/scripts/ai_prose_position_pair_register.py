#!/usr/bin/env python3
"""
ai_prose_position_pair_register.py — SETEC subprocess shim.

Position-Pair Register (stance-consistency consumer) for the APODICTIC
Development Editor. Forwards to SETEC Voiceprint's
`position_pair_register.py`, which reads ONE long nonfiction argument-shaped
work with an LLM judge and emits a **register of passage PAIRS that address
the same question Q** — each pair carrying a neutral interrogative
`question` and both passages' verbatim loci (`{doc, start_char, end_char,
quote}`), in DOCUMENT ORDER, under the `position_pair_register` task_surface
(schema_version 1.0). All CLI arguments pass through unchanged; see SETEC's
`--help` for the full surface (judge-backend selection —
manifest/mock/anthropic/openai/gemini/agent_host — the pair caps, and the
judge manifest).

THE POSTURE (and the wall this does NOT cross). This is the fleet's
deliberate NON-step across the content-verdict wall. The surface NEVER
asserts a relation between the two passages — not agreement, not conflict,
not contradiction, not tension, and it does not rank pairs by disagreement.
It points at two passages sharing a question; the HUMAN reads both and owns
100% of the conflict call. APODICTIC presents the register to the writer —
"these passages address the same question; read both, and you decide whether
they conflict, evolved, or were mischaracterized" — and adds no severity,
disposition, or finding of its own (`disposition: pre_flag` posture). The
posture is carried by mechanical gates, not prose: the consumer-side
`position-pair-register` validator (position_pair_gates.py) enforces the
no-relation register (a two-layer banned-key walk over the envelope), a
verbatim re-check of every quote against the manuscript the consumer holds
(the drift catch — a fabricated or paraphrased quote drops the pair), the
Content-Advisory A3/X-gate (no Must/Should/Could-Fix token, no
apodictic:finding block on the register artifact), and the F5
presentation-prose gate (the consumer's own framing text must itself carry
no relation vocabulary). See position-pair-register.md for the audit-level
contract, the register-artifact template, and the framing note.

Version floor: NOT hardcoded here, and NOT pre-checked consumer-side. Per the
R1 acceptance criterion and docs/setec-dependency-posture.md Decision 2, this
surface's floor is a property of the surface in SETEC's capabilities manifest
(`position_pair_register`'s `min_setec_version`, currently 1.121.0 — the
plugin-version at which the surface shipped, the first release tag carrying
it being `v1.121.0`). With R2 adoption, the normalized dispatcher ENFORCES
that floor at runtime: an out-of-floor SETEC comes back as an R3
`version_floor` error envelope (available=False, naming both the required
floor and the observed version) rather than a missing-script error. The
consumer no longer runs resolve_floor as a redundant runtime pre-check;
resolve_floor + the vendored manifest remain the authority for the offline
drift gate and capability introspection only.

Handoff posture: the surface carries `handoff: experimental` in SETEC's
capabilities manifest and ships `calibration_status: uncalibrated` (an LLM
extraction surface is not bit-deterministic — human re-review absorbs the
drift). The envelope shape and the target/results/claim_license block are
committed; the judge-prompt pipeline and the pair-selection heuristics may
evolve before a v0.2 stabilization. APODICTIC pins the `results` payload
(the `pairs` array + the refusal/cap disclosures) and the claim_license
block; it never pins a verdict, a relation, or an aggregate — there is no
aggregate for this surface, by design.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from setec_runner import run_surface_cli  # noqa: E402

SURFACE = "position_pair_register"


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
