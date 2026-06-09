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

Version floor: NOT hardcoded here. Per the R1 acceptance criterion and
docs/setec-dependency-posture.md Decision 2, this surface's floor is read
from SETEC's capabilities manifest (`narrative_decision_audit`'s
`min_setec_version`, currently 1.107.0 — the plugin-version at which
Surface 6 / StoryScope shipped, PRs #128/#129/#130). The shim resolves the
floor via setec_capabilities.resolve_floor, which asserts the discovered
setec_version satisfies the manifest floor, then passes the validated
location to run_setec_script (which would otherwise re-discover at the
bootstrap floor), so an out-of-floor SETEC fails with an upgrade message
naming the surface's required minimum rather than a missing-script error.

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

from setec_discovery import SetecDiscoveryError, run_setec_script  # noqa: E402
from setec_capabilities import (  # noqa: E402
    SetecCapabilitiesError,
    resolve_floor,
)

SURFACE = "narrative_decision_audit"


def main(argv: list[str]) -> int:
    try:
        # Floor is data-driven from SETEC's capabilities manifest, not
        # hardcoded. resolve_floor() discovers SETEC at the bootstrap floor,
        # queries `capabilities emit --json`, and asserts the discovered
        # setec_version >= this surface's manifest min_setec_version (raising
        # a floor-aware upgrade message otherwise). The validated location is
        # reused so run_setec_script does not re-discover at the bootstrap
        # floor.
        _cap, manifest = resolve_floor(SURFACE)
        result = run_setec_script(
            "narrative_decision_audit.py", argv, location=manifest.location
        )
    except (SetecDiscoveryError, SetecCapabilitiesError) as e:
        print(str(e), file=sys.stderr)
        return 2
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
