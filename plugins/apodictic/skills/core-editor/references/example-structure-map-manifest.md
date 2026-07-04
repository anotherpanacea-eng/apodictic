# Structure Map manifest — worked example

*Canonical worked example for the `manuscript-viz` validator (Manuscript-Structure Visualizations).
The `apodictic.viz_manifest.v1` block below copies — **verbatim** — the three scenes of
[`example-timeline.md`](example-timeline.md) Section 1 and the single `F-RR-01` finding of
[`example-findings-ledger.md`](example-findings-ledger.md). It proves provenance closure (E2),
byte-equal copy fidelity (E4), Must-Fix completeness (E3, `F-RR-01` is a Must-Fix), and the
chapter-honesty parse (its `evidence_refs: ["Chapter 9"]` → the `Ch 9` bin, which has no scenes —
findings bin by chapter independently of the Timeline). Validate with
`scripts/validate.sh manuscript-viz <this file> example-timeline.md example-findings-ledger.md example-argument-state-predraft.md example-scene-roster.md example-scene-function.md example-tension-points.md example-story-spine.md`
(run by `--check-all`). Render with `scripts/viz_manifest.py render <this file> example-timeline.md example-findings-ledger.md example-argument-state-predraft.md example-scene-roster.md example-scene-function.md example-tension-points.md example-story-spine.md -o out.html`.*

The manifest carries **only traceable data** — no per-finding color, size, or emphasis. The
severity→encoding map is hardcoded in the renderer, so there is structurally nothing to soften.

**Chart 5 — the character co-presence network.** The `co_presence[]` array below is the chart-5
render deliverable. Each entry is copied — **verbatim** — from the
[`example-scene-roster.md`](example-scene-roster.md) producer (`apodictic.scene_roster.v1`): the
`scene_id` matches a roster entry and a Timeline row, and the `characters[]` are the **bare canonical
names** of that scene's roster (the auditable `{name, anchor}` richness lives in the producer, not
here). It proves X2 (every name is a rostered/present character; the Timeline POV is in the roster; the
scene resolves to a Timeline row) and X8 (the producer must exist). The render computes edges/weights
**mechanically** — Mara + Adrian share two scenes (an edge, weight 2), *Eleanor* (mentioned in dialogue,
never rostered) draws no edge, *Jon* is an isolated node, and the *"Mara Voss"* surface form collapses
to *Mara* via the producer's alias table.

**Chart 6 — the scene-function heatmap.** The `scene_functions[]` array below is the chart-6 render
deliverable. Each entry is copied — **verbatim** — from the
[`example-scene-function.md`](example-scene-function.md) producer (`apodictic.scene_function.v1`): the
`scene_id` matches a producer classification and a Timeline row, and the `function` is that scene's
declared scene-turn Step-1 Unit Classification (the auditable `anchor` lives in the producer, not here).
It proves X3 (every function byte-equals the producer's classification, which is in the closed
`scene | sequel | hybrid | non-unit` enum with a non-empty anchor; the scene resolves to a Timeline row)
and X8 (the producer must exist). The render draws a scenes × functions grid **mechanically** — one row
per scene, one shaded cell at its declared function column.

**Chart 4 — the reveal-economy / tension timeline.** The `reveal_points[]` array below is the chart-4
render deliverable. Each entry is copied — **verbatim** — from the
[`example-tension-points.md`](example-tension-points.md) producer (`apodictic.tension_point.v1`): the
`scene_id` matches a producer score and a Timeline row, and the `tension` is that scene's declared
reader-dynamics Pass-1 level on the closed **1–5 reader-intensity scale** (the auditable `anchor` lives
in the producer, not here). It proves X4 (every tension byte-equals the producer's level, which is in the
closed `1 | 2 | 3 | 4 | 5` enum with a non-empty anchor; the scene resolves to a Timeline row) and X8
(the producer must exist). The render draws a tension-over-scene-order timeline **mechanically** — one
point per scene at its declared level, connected in scene order. Tension points are keyed directly on
`scene_id` (per-scene) — **no** `evidence_ref → scene_id` resolution, so that overlay stays out of scope.

**Chart 7-fiction — the beat-map against spine.** The `beats[]` array below is the chart-7-fiction
render deliverable. Each entry is copied — **verbatim** — from the
[`example-story-spine.md`](example-story-spine.md) producer (`apodictic.story_spine.v1`): the `beat` is
one of that manuscript's ordered spine beats and the `scene_id` matches the producer's mapping for that
beat and a Timeline row (the auditable `anchor` and the chosen `spine_framework` live in the producer,
not here). It proves X9 (every beat matches a producer beat, its scene_id byte-equals the producer's
mapping and resolves to a Timeline row; the producer's `spine_framework` is in the closed 50-spine
plot-coach taxonomy with non-empty beats and anchors) and X8 (the producer must exist). The render draws
a beat-map along the spine **mechanically** — one node per beat, in spine order, at its mapped scene. The
worked spine is **Seven-Point (Dan Wells)**; its first three beats (Hook, Plot Turn 1, Pinch 1) map to
the Timeline's three scenes. Beats are keyed directly on `scene_id` (per-scene) — **no** `evidence_ref →
scene_id` resolution.

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
  "co_presence": [
    {"scene_id": "Ch 1 §1", "characters": ["Mara", "Adrian"]},
    {"scene_id": "Ch 1 §2", "characters": ["Mara", "Adrian"]},
    {"scene_id": "Ch 2 §1", "characters": ["Jon"]}
  ],
  "scene_functions": [
    {"scene_id": "Ch 1 §1", "function": "scene"},
    {"scene_id": "Ch 1 §2", "function": "sequel"},
    {"scene_id": "Ch 2 §1", "function": "hybrid"}
  ],
  "reveal_points": [
    {"scene_id": "Ch 1 §1", "tension": "2"},
    {"scene_id": "Ch 1 §2", "tension": "4"},
    {"scene_id": "Ch 2 §1", "tension": "3"}
  ],
  "beats": [
    {"beat": "Hook", "scene_id": "Ch 1 §1"},
    {"beat": "Plot Turn 1", "scene_id": "Ch 1 §2"},
    {"beat": "Pinch 1", "scene_id": "Ch 2 §1"}
  ],
  "claim_ladder": [
    {"claim_id": "C1", "label": "missing curb cuts are a documented, daily mobility barrier for wheelchair and stroller users", "support": [{"support_type": "DATA", "status": "to-acquire"}]},
    {"claim_id": "C2", "label": "the phased cost fits within the existing capital-improvement budget without new taxes", "support": [{"support_type": "AUTHORITY", "status": "in-hand"}]},
    {"claim_id": "C3", "label": "piecemeal complaint-driven installation has failed to close the gap for a decade", "support": [{"support_type": "DATA", "status": "to-acquire"}]}
  ]
}
-->
