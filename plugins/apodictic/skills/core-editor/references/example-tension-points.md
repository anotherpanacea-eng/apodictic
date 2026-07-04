# Tension points — worked example (chart-4 reveal-economy / tension-timeline producer)

*Canonical worked example for the `apodictic.tension_point.v1` **producer** — the per-scene reader
tension that gates Viz Chart 4, the reveal-economy / tension timeline (see
[`manuscript-visualizations.md`](../../../docs/manuscript-visualizations.md) §The chart set, chart 4).
ONE block per manuscript. It is paired with [`example-timeline.md`](example-timeline.md): every
`scene_id` below resolves to a Timeline Event-Ledger row. The
[`example-structure-map-manifest.md`](example-structure-map-manifest.md)'s `reveal_points[]` array
copies **bare `{scene_id, tension}`** from these scores and byte-checks against them (`viz_manifest.py`
X4); the renderer draws a tension-over-scene-order timeline mechanically (tension level on the y-axis,
scene order on the x-axis). Validate with*
`scripts/validate.sh manuscript-viz example-structure-map-manifest.md example-timeline.md example-findings-ledger.md example-argument-state-predraft.md example-scene-roster.md example-scene-function.md example-tension-points.md`
*(run by `--check-all`).*

**The tension vocabulary (the firewall crux).** Each scene is scored on the **reader-dynamics Pass 1
(Reader Experience)** reading — the closed ordinal **1–5 reader-intensity scale**. This is the scale the
pass already uses: Pass 1 tracks the reader's emotional/cognitive response (`run-core.md` §Pass 1), and
that emotional tracking surfaces as an explicit ordinal scale in the Pacing Heat Map (Dashboard
Component 1) — *"intensity level (1-5 scale derived from Pass 1 emotional tracking)"* (`run-full.md`
§Component 1). The scale is monotone: **1** = flat / no felt tension, **5** = peak.

A `tension` outside the closed set `1 | 2 | 3 | 4 | 5` is a schema failure. The score is
**producer/author-enforced** (a validator cannot read prose to adjudicate how tense a scene *feels*); it
is made **auditable by the required, non-empty `anchor`** — a Timeline-relative line-range or short
on-page quote witnessing the reading. The validator enforces the enum + anchor + provenance closure
(every `scene_id` resolves to a Timeline row), **not** the prose reading.

**Scope note (evidence_ref overlay is out of scope).** Tension points are keyed **directly on
`scene_id`** (per-scene, exactly like `scene_roster` / `scene_function`) — there is **no** `evidence_ref
→ scene_id` resolution here. The docs' chart-4 caveat about an `evidence_ref → scene_id` resolution is
about scene-*precise* placement of free-text refs (a chart-3 concern); tension points carry their own
`scene_id`, so no such resolution is needed and none is performed. That overlay stays out of scope.

**What this worked example exercises:**

- **Provenance closure:** all three `scene_id`s (`Ch 1 §1`, `Ch 1 §2`, `Ch 2 §1`) resolve to
  `example-timeline.md` Event-Ledger rows.
- **Enum coverage across the scale:** `Ch 1 §1` scores **2** (building), `Ch 1 §2` scores **4** (high),
  `Ch 2 §1` scores **3** (a partial release) — a rise-then-ease timeline shape drawn from three
  distinct levels, not a flat line.
- **Anchor bounding:** each `anchor` is a line-range form that falls **within** its scene's Timeline
  line-range (the X4(e) tightening), so an anchor cannot point outside the scene it scores.

<!-- apodictic:tension_point
{
  "schema": "apodictic.tension_point.v1",
  "project": "The Lighthouse Year",
  "points": [
    {"scene_id": "Ch 1 §1", "tension": "2", "anchor": "lines 40-90: \"She set the kettle down and faced him — 'You lied about the harbor.'\""},
    {"scene_id": "Ch 1 §2", "tension": "4", "anchor": "lines 150-200: \"'You can't be serious,' Adrian said, and she signed anyway.\""},
    {"scene_id": "Ch 2 §1", "tension": "3", "anchor": "lines 300-350: \"Jon watched the train pull in and let out a breath he'd been holding.\""}
  ]
}
-->
