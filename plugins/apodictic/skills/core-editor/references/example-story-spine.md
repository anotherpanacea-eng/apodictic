# Story spine — worked example (chart-7-fiction beat-map-against-spine producer)

*Canonical worked example for the `apodictic.story_spine.v1` **producer** — the chosen fiction spine
framework and its ordered beats that gate Viz Chart 7-fiction, the beat-map-against-spine (see
[`manuscript-visualizations.md`](../../../docs/manuscript-visualizations.md) §The chart set, chart
7-fiction). ONE block per manuscript. It is paired with [`example-timeline.md`](example-timeline.md):
every `scene_id` below resolves to a Timeline Event-Ledger row. The
[`example-structure-map-manifest.md`](example-structure-map-manifest.md)'s `beats[]` array copies
**bare `{beat, scene_id}`** from these beats and byte-checks against them (`viz_manifest.py` X9); the
renderer draws a beat-map along the spine (beats in spine order, each mapped to its scene) mechanically.
Validate with*
`scripts/validate.sh manuscript-viz example-structure-map-manifest.md example-timeline.md example-findings-ledger.md example-argument-state-predraft.md example-scene-roster.md example-scene-function.md example-tension-points.md example-story-spine.md`
*(run by `--check-all`).*

**The spine vocabulary (the firewall crux).** The manuscript's chosen **`spine_framework`** is a token
in the **closed 50-spine taxonomy** the plot-architecture skill (plot-coach) names —
[`plot-architecture/SKILL.md`](../../plot-architecture/SKILL.md) §Spine Families (50 Spines, 12
Families). Each spine carries its own named, ordered beats in its *"On the page"* line
([`plot-architecture-audit.md`](../../plot-architecture/references/plot-architecture-audit.md)). This
worked example uses **Seven-Point (Dan Wells)** — an explicitly ordered beat sequence: *Hook → Plot Turn
1 → Pinch 1 → Midpoint → Pinch 2 → Plot Turn 2 → Resolution*. The `beat` is that framework's named beat,
kept a **free non-empty string** because beats are open *per* framework and are not exhaustively
enumerated (the `scene_roster.v1` character-name precedent — a beat is author-declared, made auditable
by its anchor, not enum-closed).

A `spine_framework` outside the closed 50-spine set is a schema failure (an invented framework
plot-coach never names). The spine + beat reading is **producer/author-enforced** (a validator cannot
read prose to adjudicate *which* spine a manuscript follows or *which* beat a scene is); it is made
**auditable by the required, non-empty `anchor`** — a Timeline-relative line-range or short on-page
quote witnessing the beat. The validator enforces the framework enum + beat/anchor non-empty +
provenance closure (every `scene_id` resolves to a Timeline row), **not** the prose reading.

**Scope note (evidence_ref overlay is out of scope).** Beats are keyed **directly on `scene_id`**
(per-scene, exactly like `scene_roster` / `scene_function` / `tension_point`) — there is **no**
`evidence_ref → scene_id` resolution here. That overlay stays out of scope.

**What this worked example exercises:**

- **Framework enum:** `spine_framework` is `Seven-Point (Dan Wells)`, a member of the closed 50-spine
  taxonomy (SKILL.md §Spine Families) — not an invented framework.
- **Ordered beats:** the first three Seven-Point beats — **Hook**, **Plot Turn 1**, **Pinch 1** — in
  spine order, so the render draws them left→right along the spine as beats 1, 2, 3.
- **Provenance closure:** all three `scene_id`s (`Ch 1 §1`, `Ch 1 §2`, `Ch 2 §1`) resolve to
  `example-timeline.md` Event-Ledger rows.
- **Anchor bounding:** each `anchor` is a line-range form that falls **within** its beat-scene's Timeline
  line-range (the X9(e) tightening), so an anchor cannot point outside the scene it witnesses.

<!-- apodictic:story_spine
{
  "schema": "apodictic.story_spine.v1",
  "project": "The Lighthouse Year",
  "spine_framework": "Seven-Point (Dan Wells)",
  "beats": [
    {"beat": "Hook", "scene_id": "Ch 1 §1", "anchor": "lines 40-90: \"She set the kettle down and faced him — 'You lied about the harbor.'\""},
    {"beat": "Plot Turn 1", "scene_id": "Ch 1 §2", "anchor": "lines 150-200: \"'You can't be serious,' Adrian said, and she signed anyway.\""},
    {"beat": "Pinch 1", "scene_id": "Ch 2 §1", "anchor": "lines 300-350: \"Jon watched the train pull in and let out a breath he'd been holding.\""}
  ]
}
-->
