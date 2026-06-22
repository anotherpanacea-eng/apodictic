# Structure Map manifest — worked example

*Canonical worked example for the `manuscript-viz` validator (Manuscript-Structure Visualizations).
The `apodictic.viz_manifest.v1` block below copies — **verbatim** — the three scenes of
[`example-timeline.md`](example-timeline.md) Section 1 and the single `F-RR-01` finding of
[`example-findings-ledger.md`](example-findings-ledger.md). It proves provenance closure (E2),
byte-equal copy fidelity (E4), Must-Fix completeness (E3, `F-RR-01` is a Must-Fix), and the
chapter-honesty parse (its `evidence_refs: ["Chapter 9"]` → the `Ch 9` bin, which has no scenes —
findings bin by chapter independently of the Timeline). Validate with
`scripts/validate.sh manuscript-viz <this file> example-timeline.md example-findings-ledger.md example-argument-state-predraft.md`
(run by `--check-all`). Render with `scripts/viz_manifest.py render <this file> example-timeline.md example-findings-ledger.md example-argument-state-predraft.md -o out.html`.*

The manifest carries **only traceable data** — no per-finding color, size, or emphasis. The
severity→encoding map is hardcoded in the renderer, so there is structurally nothing to soften.

**Chart 7-nonfiction — the claim ladder.** The `claim_ladder[]` array below is the render-only M1
deliverable of the Manuscript-Visualization Completion increment. Each rung is copied — **verbatim** —
from [`example-argument-state-predraft.md`](example-argument-state-predraft.md): the `claim_id` is a
declared spine subclaim (`C1`/`C2`/`C3`, resolved via `argument_spine.spine_subclaim_ids()`); the
`label` is that subclaim string with its leading `Cn:` token stripped; and each `support[]` item
(`support_type` + `status`) is copied from a real `apodictic.support_plan.v1` block keyed on that
`subclaim_id`. It proves X1 (the array carries **no scene axis** — no `scene_ids`/`scene_id`/`section`
key), X5/X6 (every rung byte-traces to the spine + support plan), and X7 (no duplicate rung). This is
the **declared** claim ladder and its support coverage — *not* a claim-to-scene map (no producer maps
a subclaim to a location, by design).

<!-- apodictic:viz_manifest
{
  "schema": "apodictic.viz_manifest.v1",
  "project": "The Lighthouse Year",
  "scenes": [
    {"scene_id": "Ch 1 §1", "chapter": "Ch 1", "line_range": "1-118", "word_count": "1480", "pov": "Mara", "span": "3 hours", "gap": "n/a"},
    {"scene_id": "Ch 1 §2", "chapter": "Ch 1", "line_range": "119-240", "word_count": "1390", "pov": "Mara", "span": "2 hours", "gap": "3 hours"},
    {"scene_id": "Ch 2 §1", "chapter": "Ch 2", "line_range": "241-372", "word_count": "1610", "pov": "Jon", "span": "1 hour", "gap": "16 hours"}
  ],
  "findings": [
    {"id": "F-RR-01", "severity": "Must-Fix", "confidence": "HIGH", "chapter": "Ch 9"}
  ],
  "claim_ladder": [
    {"claim_id": "C1", "label": "missing curb cuts are a documented, daily mobility barrier for wheelchair and stroller users", "support": [{"support_type": "DATA", "status": "to-acquire"}]},
    {"claim_id": "C2", "label": "the phased cost fits within the existing capital-improvement budget without new taxes", "support": [{"support_type": "AUTHORITY", "status": "in-hand"}]},
    {"claim_id": "C3", "label": "piecemeal complaint-driven installation has failed to close the gap for a decade", "support": [{"support_type": "DATA", "status": "to-acquire"}]}
  ]
}
-->
