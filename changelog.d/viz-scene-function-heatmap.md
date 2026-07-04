### Manuscript Visualizations — Scene-Function Heatmap (chart 6)

Built the scene-function heatmap (chart 6) over a new `apodictic.scene_function.v1` **producer**: a
per-scene structural-function pass (`functions: [{scene_id, function, anchor}]`) whose `function` is the
scene-turn audit's Step-1 Unit Classification — the closed set `scene | sequel | hybrid | non-unit`. The
`manuscript-viz` gate gains **X3** (scene_functions byte-checked against the producer + Timeline:
scene_id → producer + Timeline row; manifest function == producer classification; producer function ∈
closed enum; producer anchor non-empty and, when line-range-shaped, overlapping the scene's Timeline
line-range), and the **X8 flip** so a present `scene_functions[]` is legitimate iff it byte-checks
against the producer (`reveal_points` stays producer-gated). The renderer draws a deterministic
scenes × functions grid (one shaded cell per scene at its declared function column, from a hardcoded
function → colour band — no style in the manifest). Adds the `apodictic.scene_function.v1` schema + its
`_coverage.json` binding (`closed_keys:true`) and the worked `example-scene-function.md` fixture (paired
to `example-timeline.md`), gated by `--check-all`. No new validator — the count stays DERIVED.
