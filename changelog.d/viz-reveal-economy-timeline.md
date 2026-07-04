### Manuscript Visualizations — Reveal-Economy / Tension Timeline (chart 4)

Built the reveal-economy / tension timeline (chart 4) over a new `apodictic.tension_point.v1`
**producer**: a per-scene reader-tension pass (`points: [{scene_id, tension, anchor}]`) whose `tension`
is a token on the closed reader-dynamics **Pass 1 (Reader Experience) 1–5 intensity scale** — the Pacing
Heat Map's "intensity level (1-5 scale derived from Pass 1 emotional tracking)" (1 = flat, 5 = peak). The
`manuscript-viz` gate gains **X4** (reveal_points byte-checked against the producer + Timeline: scene_id
→ producer + Timeline row; manifest tension == producer level; producer tension ∈ closed 1–5 enum;
producer anchor non-empty and, when line-range-shaped, overlapping the scene's Timeline line-range), and
the **X8 flip** so a present `reveal_points[]` is legitimate iff it byte-checks against the producer —
retiring the last producer-gated hard-fail array (only chart 7-fiction's beat-map remains gated, and it
has no manifest array). The renderer draws a deterministic tension-over-scene-order timeline (tension
level on the y-axis, scene order on the x-axis, a polyline through one point per scene at its declared
level, from a hardcoded level → y-position map — no style in the manifest, no time/random). Tension
points are keyed directly on `scene_id` (per-scene, like scene_roster/scene_function) — no
`evidence_ref → scene_id` resolution, so that overlay stays explicitly out of scope. Adds the
`apodictic.tension_point.v1` schema + its `_coverage.json` binding (`closed_keys:true`) and the worked
`example-tension-points.md` fixture (paired to `example-timeline.md`), gated by `--check-all`. No new
validator — the count stays DERIVED.
