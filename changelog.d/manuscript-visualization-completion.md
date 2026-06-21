### Workflows — Manuscript-Structure Visualizations

Chart 7-nonfiction — the **claim ladder** — now ships render-only (Manuscript-Visualization
Completion, M1). The `apodictic.viz_manifest.v1` manifest gains four OPTIONAL, additive arrays
(`co_presence` / `scene_functions` / `reveal_points` / `claim_ladder`); the M1 render-only chart is
the claim ladder over `apodictic.argument_spine.v1` (C0 thesis + C1…Cn subclaims) annotated with
support coverage from `apodictic.support_plan.v1` (support type + in-hand/to-acquire, or a
bare-assertion marker). The `manuscript-viz` validator gains gates **X1** (new-array schema + the
no-scene-axis firewall — a `scene_ids`/`scene_id`/`section` key on a `claim_ladder[]` object is a
hard failure), **X5/X6** (claim-ladder provenance — `claim_id` resolves via the reused
`argument_spine.spine_subclaim_ids()` leading-`Cn`-token parser, `label` byte-equals the subclaim
string minus its `Cn:` token, each `support[]` item byte-copies a real `support_plan.v1` block),
**X7** (no duplicate rung), **X8** (producer-present — no producer, no chart), and **W3** (chart
coverage). No new schema and no new validator — the validator count stays DERIVED. Charts
4/5/6/7-fiction remain producer-gated; a claim-to-scene overlay is out of scope (no subclaim→location
producer exists). The canonical `--check-all` Structure Map gate now exercises the claim ladder
against the pre-draft Argument_State spine. Render-only and firewall-clean: no renderer or validator
in this layer calls a model.
