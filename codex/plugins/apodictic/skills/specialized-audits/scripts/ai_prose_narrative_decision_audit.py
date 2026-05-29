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

Version floor: SETEC >= 1.107.0. Surface 6 shipped in SETEC v1.107.0
(StoryScope integration, PRs #128/#129/#130) and is absent from the
1.86.0 floor that the texture-level shims delegate to. This shim
discovers with its own higher floor and passes the validated location to
run_setec_script (which would otherwise re-discover at the lower floor),
so an older SETEC fails with an upgrade message rather than a missing-
script error.

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

from setec_discovery import (  # noqa: E402
    SetecDiscoveryError,
    discover_setec,
    run_setec_script,
)

# Surface 6 (narrative_decision_audit) shipped in SETEC v1.107.0, higher
# than the framework-wide 1.86.0 floor in setec_discovery. The shim
# discovers with its own floor and passes the validated location through
# so the version check is enforced before the script is invoked.
MIN_SETEC_VERSION = (1, 107, 0)


def main(argv: list[str]) -> int:
    try:
        location = discover_setec(min_version=MIN_SETEC_VERSION)
        result = run_setec_script(
            "narrative_decision_audit.py", argv, location=location
        )
    except SetecDiscoveryError as e:
        print(str(e), file=sys.stderr)
        return 2
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
