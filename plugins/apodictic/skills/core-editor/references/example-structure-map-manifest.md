# Structure Map manifest — worked example

*Canonical worked example for the `manuscript-viz` validator (Manuscript-Structure Visualizations).
The `apodictic.viz_manifest.v1` block below copies — **verbatim** — the three scenes of
[`example-timeline.md`](example-timeline.md) Section 1 and the single `F-RR-01` finding of
[`example-findings-ledger.md`](example-findings-ledger.md). It proves provenance closure (E2),
byte-equal copy fidelity (E4), Must-Fix completeness (E3, `F-RR-01` is a Must-Fix), and the
chapter-honesty parse (its `evidence_refs: ["Chapter 9"]` → the `Ch 9` bin, which has no scenes —
findings bin by chapter independently of the Timeline). Validate with
`scripts/validate.sh manuscript-viz <this file> example-timeline.md example-findings-ledger.md`
(run by `--check-all`). Render with `scripts/viz_manifest.py render <this file> example-timeline.md example-findings-ledger.md -o out.html`.*

The manifest carries **only traceable data** — no per-finding color, size, or emphasis. The
severity→encoding map is hardcoded in the renderer, so there is structurally nothing to soften.

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
  ]
}
-->
