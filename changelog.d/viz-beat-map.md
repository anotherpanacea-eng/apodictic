### Manuscript Visualizations — Beat-Map Against Spine (chart 7-fiction)

Built the beat-map-against-spine (chart 7-fiction) over a new `apodictic.story_spine.v1` **producer**:
the chosen fiction spine and its ordered beats (`beats: [{beat, scene_id, anchor}]` + a top-level
`spine_framework`). The `spine_framework` is a token in the **closed 50-spine plot-coach taxonomy** —
`plot-architecture/SKILL.md` §Spine Families (50 Spines, 12 Families) — and each spine's own named,
ordered beats live in its "On the page" line in `plot-architecture-audit.md` (e.g. Seven-Point (Dan
Wells): Hook → Plot Turn 1 → Pinch 1 → Midpoint → Pinch 2 → Plot Turn 2 → Resolution). The `beat` name
stays a **free non-empty string** because beats are open per framework and are not exhaustively
enumerated (the `scene_roster.v1` character-name precedent). The `manuscript-viz` gate gains **X9**
(beats byte-checked against the producer + Timeline: beat → producer beat; manifest scene_id == producer
scene_id and resolves to a Timeline row; producer spine_framework ∈ closed 50-spine enum; producer beat
+ anchor non-empty and, when line-range-shaped, overlapping the scene's Timeline line-range), and the
**X8** producer-present rule so a present `beats[]` is legitimate iff it byte-checks against the
producer — **retiring the last producer-gated chart** (no producer-gated chart remains). The renderer
draws a deterministic beat-map along a single spine rail (one node per beat, in spine order, at its
mapped scene, with the framework as caption — no style in the manifest, no time/random). Beats are keyed
directly on `scene_id` (per-scene, like scene_roster/scene_function/tension_point) — no `evidence_ref →
scene_id` resolution. Adds the `apodictic.story_spine.v1` schema + its `_coverage.json` binding
(`closed_keys:true`), the new `beats[]` manifest array on `apodictic.viz_manifest.v1`, and the worked
`example-story-spine.md` fixture (paired to `example-timeline.md`), gated by `--check-all`. No new
validator — the count stays DERIVED.
