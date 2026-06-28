# Scene roster — worked example (chart-5 co-presence producer)

*Canonical worked example for the `apodictic.scene_roster.v1` **producer** — the per-scene cast that
gates Viz Chart 5, the character co-presence network (see
[`manuscript-visualizations.md`](../../../docs/manuscript-visualizations.md) §The chart set, chart 5).
ONE block per manuscript. It is paired with [`example-timeline.md`](example-timeline.md): every
`scene_id` below resolves to a Timeline Event-Ledger row, and each scene's Timeline POV character
appears in its roster (the X2 cross-check). The
[`example-structure-map-manifest.md`](example-structure-map-manifest.md)'s `co_presence[]` array copies
**bare canonical names** from these rosters and byte-checks against them (`viz_manifest.py` X2); the
renderer computes edges/weights mechanically (an edge iff two characters co-occur in ≥1 scene; weight =
the count of shared scenes). Validate with*
`scripts/validate.sh manuscript-viz example-structure-map-manifest.md example-timeline.md example-findings-ledger.md example-argument-state-predraft.md example-scene-roster.md`
*(run by `--check-all`).*

**The present-vs-mentioned rule (the firewall crux).** A character is **present** in a scene iff they
take on-page action, speak, or are a POV/thought subject **within the scene's Timeline line-range** — and
that presence is made auditable by the **required, non-empty `anchor`** (a line-range or short on-page
quote where they act). A character named only in another's speech/thought, in narrative summary, or by
reference is **mentioned** → **no roster entry, no co-presence edge**. This reading is
**producer/author-enforced**; the validator enforces the anchor + provenance closure, not the prose.

**What this worked example exercises** (the chart-5 acceptance negatives):

- **≥1 edge:** Mara and Adrian share Ch 1 §1 *and* Ch 1 §2 → one edge, **weight 2**.
- **Mentioned-not-present (the firewall fixture):** *Eleanor* is named in dialogue in Ch 1 §1 ("Eleanor
  warned us about the harbor") but never appears on-page → **no roster entry → no node, no edge**.
- **Solo / isolated node:** *Jon* is alone in Ch 2 §1 (he is the POV and the only character present) and
  appears in no other scene → he renders as an **isolated node**, not dropped.
- **Alias collapse:** Ch 1 §2 lists the surface form *"Mara Voss"*, which the `character_aliases` table
  maps to the canonical *"Mara"* → the two surface forms collapse to **one node** (the Mara–Adrian edge
  is reinforced, not split into a phantom third node).

<!-- apodictic:scene_roster
{
  "schema": "apodictic.scene_roster.v1",
  "project": "The Lighthouse Year",
  "character_aliases": [
    {"surface": "Mara Voss", "canonical": "Mara"}
  ],
  "rosters": [
    {"scene_id": "Ch 1 §1", "characters": [
      {"name": "Mara", "anchor": "lines 1-118: \"She set the kettle down and faced him.\""},
      {"name": "Adrian", "anchor": "lines 1-118: \"Adrian leaned in the doorway, arms folded.\""}
    ]},
    {"scene_id": "Ch 1 §2", "characters": [
      {"name": "Mara Voss", "anchor": "lines 119-240: \"Mara signed the last page without reading it.\""},
      {"name": "Adrian", "anchor": "lines 119-240: \"'You can't be serious,' Adrian said.\""}
    ]},
    {"scene_id": "Ch 2 §1", "characters": [
      {"name": "Jon", "anchor": "lines 241-372: \"Jon paced the empty platform alone.\""}
    ]}
  ]
}
-->
