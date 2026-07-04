# Scene function — worked example (chart-6 scene-function-heatmap producer)

*Canonical worked example for the `apodictic.scene_function.v1` **producer** — the per-scene structural
function that gates Viz Chart 6, the scene-function heatmap (see
[`manuscript-visualizations.md`](../../../docs/manuscript-visualizations.md) §The chart set, chart 6).
ONE block per manuscript. It is paired with [`example-timeline.md`](example-timeline.md): every
`scene_id` below resolves to a Timeline Event-Ledger row. The
[`example-structure-map-manifest.md`](example-structure-map-manifest.md)'s `scene_functions[]` array
copies **bare `{scene_id, function}`** from these classifications and byte-checks against them
(`viz_manifest.py` X3); the renderer draws a scenes × functions grid mechanically (one shaded cell per
scene at its declared function column). Validate with*
`scripts/validate.sh manuscript-viz example-structure-map-manifest.md example-timeline.md example-findings-ledger.md example-argument-state-predraft.md example-scene-roster.md example-scene-function.md`
*(run by `--check-all`).*

**The function vocabulary (the firewall crux).** Each scene is classified into the scene-turn audit's
**Step 1 Unit Classification** (`craft/scene-turn.md` §Step 1) — the closed set:

- **scene** — an *action unit*: goal → conflict → outcome (the situation changes on-page).
- **sequel** — a *processing unit*: reaction → dilemma → decision (the bridge between scenes).
- **hybrid** — contains both, one incomplete.
- **non-unit** — exposition / montage / vignette (no attempt, no processing, no decision).

A `function` outside this closed set is a schema failure. The classification is
**producer/author-enforced** (a validator cannot read prose to adjudicate a scene's function); it is
made **auditable by the required, non-empty `anchor`** — a Timeline-relative line-range or short on-page
quote witnessing the reading. The validator enforces the enum + anchor + provenance closure (every
`scene_id` resolves to a Timeline row), **not** the prose reading.

**What this worked example exercises:**

- **Provenance closure:** all three `scene_id`s (`Ch 1 §1`, `Ch 1 §2`, `Ch 2 §1`) resolve to
  `example-timeline.md` Event-Ledger rows.
- **Enum coverage:** `Ch 1 §1` is a **scene** (Mara confronts Adrian — a goal met with opposition),
  `Ch 1 §2` is a **sequel** (Mara processes the confrontation and decides), `Ch 2 §1` is a **hybrid**
  (Jon reacts *and* pursues a fresh goal in one unit).
- **Anchor bounding:** each `anchor` is a line-range form that falls **within** its scene's Timeline
  line-range (the X3(e) tightening), so an anchor cannot point outside the scene it classifies.

<!-- apodictic:scene_function
{
  "schema": "apodictic.scene_function.v1",
  "project": "The Lighthouse Year",
  "functions": [
    {"scene_id": "Ch 1 §1", "function": "scene", "anchor": "lines 1-118: \"She set the kettle down and faced him — 'You lied about the harbor.'\""},
    {"scene_id": "Ch 1 §2", "function": "sequel", "anchor": "lines 119-240: \"Mara sat with the signed page a long while, then reached for the phone.\""},
    {"scene_id": "Ch 2 §1", "function": "hybrid", "anchor": "lines 241-372: \"Jon paced the platform, then bought the ticket he'd sworn he wouldn't.\""}
  ]
}
-->
