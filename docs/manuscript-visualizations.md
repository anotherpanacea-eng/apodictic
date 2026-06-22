# Manuscript-Structure Visualizations — render the diagnosis, invent nothing

**Status:** **Increment 1 built** (charts 1–3: pacing/word-count curve, POV time-share, finding-severity-by-chapter) **+ chart 7-nonfiction (claim ladder) built render-only** (Manuscript-Visualization Completion, M1). Roadmap: `ROADMAP.md` → [Horizon Capacities](../ROADMAP.md#horizon-capacities) Tier 1, item 1. Implementation surface: the `viz` reference module `core-editor/references/manuscript-visualizations.md`, the `scripts/viz_manifest.py` extractor/validator, `validate.sh manuscript-viz` (+ `--check-all` gate), the new single-file SVG renderer (`viz_manifest.py render`), and a worked example (`example-structure-map-manifest.md` paired with `example-timeline.md` + `example-findings-ledger.md` + `example-argument-state-predraft.md` as the claim-ladder spine). The claim ladder (gates X1/X5/X6/X7/X8 + W3) reuses `argument_spine.v1` + `support_plan.v1` — no new schema, no new validator, no scene axis. **Producer-gated (not built):** the character co-presence network, scene-function heatmap, reveal-economy timeline, and beat-map-against-spine charts (each gated on a producer increment that makes its upstream artifact machine-readable — see §The chart set).
<!-- built-when: scripts/viz_manifest.py -->

A finished development edit already *contains* most of the numbers a structural picture needs — they are just locked inside prose and tables. The Findings Ledger knows where the Must-Fixes cluster; `Timeline.md` Section 1 knows the word-count, POV, span, and gap of every scene. What APODICTIC cannot do today is **show** that shape at a glance. This is the single biggest externally-validated gap: structural-editing tools in the field (Fictionary) treat "15+ automated story visualizations" as their headline, and a manuscript-shape picture is something the editorial letter's prose can describe but never *display*.

This capability adds **no new analysis**. It is a presentation layer: a deterministic render of data the passes already produced. That is the whole point of the firewall posture below — a chart that introduces a single data point not already in a finding block or a Timeline row would be inventing content, and is forbidden.

## What this is not

- **Not** the [Framework Overview Dashboard](../ROADMAP.md#framework-overview-dashboard) (planned). That visualizes the *plugin's* capabilities — the route explorer, the macro-block map (`overview-dashboard.html`, `route-explorer.html`). This visualizes a *specific manuscript's* structure. Different artifact, different data source, different audience. (Those two files are cited only as the **static-HTML house pattern**, not as a renderer to extend.)
- **Not** a new diagnostic. It reads the Findings Ledger and `Timeline.md`; it runs no pass and reaches no conclusion the letter did not already reach.
- **Not** a softening of the letter. The editorial letter remains the artifact of record; the visualization is a companion, gated so its encoding cannot under-state a locked severity (see §Severity honesty).

## The artifact

A single, self-contained `[Project]_Structure_Map_[runlabel].html` — the same static-HTML house pattern as `overview-dashboard.html`: **no external dependencies, no network calls, no script-loaded fonts, no telemetry**. Charts are inline SVG generated from a structured manifest; the file opens offline. (The no-network constraint is not incidental — it is the *non-commercial / local / no-telemetry* commitment expressed in the deliverable.) There is no existing editorial-letter render pipeline to reuse — the editorial letter is a markdown artifact — so Increment 1 builds a **new** renderer; the named dashboards establish only the single-file-inline-SVG convention it follows.

The HTML is a **pure function of a manifest**, never hand-drawn. The manifest is the contract; the render is mechanical. This mirrors the Harness Contracts v2 direction (`ROADMAP.md` → Harness Engineering): the structured artifact is the source of truth, the human-facing surface is generated from it.

### The manifest (`apodictic.viz_manifest.v1`)

One structured block (real JSON, like `apodictic.finding.v1`) holding only **traceable** data points copied from existing artifacts. Increment 1 draws from exactly the two sources that are already machine-readable — the Timeline Event-Ledger pipe-table and the `apodictic.finding.v1` blocks — so every datum can be verified verbatim:

| Field | Source of truth (Increment 1) | Example |
|---|---|---|
| `scenes[]` (scene_id, chapter, line_range, word_count, pov, span, gap) | `Timeline.md` Section 1 Event Ledger — copied verbatim from its columns | `Ch 1 §2`, 1390 wd, POV Mara |
| `findings[]` (id, severity, confidence, chapter) | `apodictic.finding.v1` blocks in the Findings Ledger; `chapter` parsed conservatively from the finding's `evidence_refs` (see below) | `F-RR-01`, Must-Fix, HIGH, Ch 9 |

The schema carries **no visual-style fields** — no per-finding color, size, or emphasis. The severity→encoding mapping lives in the renderer and is fixed (see §Severity honesty), so a run cannot recolor a finding to soften it; there is structurally nothing to soften.

**Finding placement is chapter-level and conservative.** The `apodictic.finding.v1` schema has no `locus` or `scene_id` field — loci live only as free strings inside `evidence_refs` (e.g., `["Chapter 9"]`, see `example-findings-ledger.md`). The manifest therefore parses a **chapter** from `evidence_refs` with a strict pattern (`Chapter N` / `Ch N`) and places the finding in that chapter's bin. An `evidence_ref` that does not yield a chapter token is placed in an explicit **`unplaced`** bin and shown as such — the render never *guesses* a scene or a position. Scene-precise finding placement (a validated `evidence_ref → scene_id` resolution) is a future increment, not a v1 promise; the spec does not pretend a free-text ref mechanically resolves to a Timeline `Scene ID`.

### The chart set

Increment 1 charts join only on data that exists verbatim in the two structured sources:

1. **Pacing / word-count curve** — bar/area over scene order; `word_count` and `gap` from the Timeline Event Ledger. (Where the draft expands and compresses.)
2. **POV-time distribution** — share of `word_count` by `pov`, computed by summing the Timeline Event Ledger's own per-scene `word_count` grouped by its `pov` column (a join *within* one table, not across artifacts). (Whether a POV vanishes for 80 pages.) *(Note: this is POV **time-share** from the Timeline, not the `pov-voice-profile` audit's stylometric distance — a different measurement from a different artifact.)*
3. **Finding-severity-by-chapter map** — Must/Should/Could findings binned by chapter (per the conservative parse above), severity as the dominant channel. (Where the problems cluster.)

Charts 4–7 are the Manuscript-Visualization Completion increment. One ships render-only today; the other three are producer-gated.

7. **Claim ladder** *(nonfiction; built — render-only, no scene axis)* — C0 (the `apodictic.argument_spine.v1` thesis) + the C1…Cn subclaim rungs, each annotated with its **support coverage** from the `apodictic.support_plan.v1` blocks keyed on that subclaim (support type + in-hand/to-acquire, or a **bare-assertion** marker when a declared subclaim has no support plan — the same W2 condition `argument_spine.py` computes). The `claim_id` resolves via `argument_spine.spine_subclaim_ids()` (the leading-`Cn`-token parse — *no second parser*); the `label` is that subclaim string minus its leading `Cn:` token; every datum byte-traces to the spine + support plan (gates X1/X5/X6/X7/X8 + W3). This is the **declared** claim ladder and its planned support — **not** a claim-to-scene map: no structured artifact maps a subclaim to a scene/section, so the `claim_ladder[]` array carries *no scene axis at all* (a `scene_ids`/`scene_id`/`section` key is a hard X1 failure). A claim-to-scene overlay would be a separate producer increment and is out of scope.

Producer-gated charts (each ships only after its upstream artifact becomes machine-readable — building any render-first would fabricate data and breach the firewall):

4. **Reveal-economy / tension timeline** *(producer-gated)* — tension levels over scene order, sourced from the **reader-dynamics pass (Pass 1)** artifact once it emits a structured `apodictic.tension_point.v1` ledger.
5. **Character co-presence network** *(producer-gated)* — which characters share scenes, once scene rosters are structured as `apodictic.scene_roster.v1` (the Timeline carries POV/setting but not a full roster).
6. **Scene-function heatmap** *(producer-gated)* — scene-by-function from the scene-function audits (`scene-turn`) once that output emits a structured `apodictic.scene_function.v1` block.
7-fiction. **Beat-map-against-spine** *(producer-gated)* — the chosen fiction spine + its beats, once plot-coach emits a structured `apodictic.story_spine.v1` (it produces prose spine selection today).

Charts 1–3 are Increment 1 because their data is already fully structured; chart 7-nonfiction (the claim ladder) ships render-only because `argument_spine.v1` + `support_plan.v1` are already structured; 4/5/6/7-fiction wait on their upstream producers, in the Harness Contracts v2 spirit. Until a producer lands, a present `co_presence`/`scene_functions`/`reveal_points` array is a hard X8 failure (no producer to byte-check it against).

## Firewall compliance

The visualization is firewall-safe **by construction**, and the construction is enforced, not promised:

- **Render-only.** The renderer consumes the manifest and emits SVG. It has no model call, no prose, no interpretation step. It cannot add a plot event, a character, or a "the problem here is…" gloss, because it never reasons.
- **Provenance-closed.** Every visual element traces to a manifest entry, and every manifest entry is copied verbatim from a structured source (validator `E2`/`E4`). A chart cannot show a value the Timeline or a finding block did not contain.
- **No annotation invention.** Labels are the *author's* scene IDs, the *findings'* own IDs and severities, the *Timeline's* POV names — never new copy. (Same boundary the [Annotated-Manuscript](annotated-manuscript.md) deliverable holds: anchor to existing data, add no prose.)

## Severity honesty

A picture can soften a verdict more quietly than a sentence can, so the encoding is fixed in the renderer and the manifest cannot override it:

- **Severity is the dominant, size-independent channel.** Must-Fix renders in the most salient encoding (color + largest marker); the mapping `{Must-Fix, Should-Fix, Could-Fix} → encoding` is **hardcoded in the renderer**, not read from the manifest, so no run can recolor a Must-Fix to comfort. The legend names the canonical scale.
- **Confidence never suppresses severity.** Confidence may modulate only a secondary, non-suppressing channel (e.g., border style: solid/dashed) — **never marker size**. A LOW-confidence Must-Fix is still rendered at full Must-Fix salience; it is not shrunk. (This closes the confidence-as-size softening vector: high-severity/low-confidence findings stay visually loud.)
- **Every locked Must-Fix appears.** The finding-severity map must include all body Must-Fix findings; a manifest that drops one fails (`E3`). This is the visual analogue of `softness-check`'s locked→delivered rule.
- **The chart is a companion, not a replacement.** The HTML header links back to the editorial letter and states the letter is the artifact of record. No verdict lives only in a chart.

## The `manuscript-viz` validator

`validate.sh manuscript-viz <run_folder>` (resolves the newest manifest + its source artifacts). Delegates to `scripts/viz_manifest.py`; degrades to advisory `WARN` without `python3`. It validates the **manifest**, not the pixels — pixel fidelity follows from the render being a pure function over a style-free manifest with a hardcoded encoding.

| ID | Severity | Rule |
|---|---|---|
| **E1 — manifest schema** | ERROR | The `apodictic.viz_manifest.v1` block parses and satisfies the field schema (scene/finding arrays well-formed; **no visual-style fields present** — their presence is itself a failure, since style is the renderer's, not the run's). A present-but-unparseable block is an E1 failure, **not** a silent no-op; `--require-block` additionally fails an absent block (the `--check-all` canonical-example gate runs with it so the gate cannot pass vacuously). |
| **E2 — provenance closure** | ERROR | Every `findings[].id` resolves to a real `apodictic.finding.v1` in the Findings Ledger; every `scenes[].scene_id` resolves to a Timeline Event-Ledger row; every `findings[].chapter` is either a chapter the conservative `evidence_refs` parse actually yields, or the literal `unplaced` bin. A dangling or *guessed* placement is the "invented data point" failure. Complements `finding-trace` (which owns letter/ledger/revision integrity) — `manuscript-viz` owns manifest↔source. |
| **E3 — Must-Fix completeness** | ERROR | Every body Must-Fix finding in the Ledger appears in `findings[]`. The render cannot drop a locked severity. |
| **E4 — no orphan data** | ERROR | Every `scenes[]` value (`word_count`, `pov`, `gap`, `line_range`) is byte-equal to the corresponding Timeline Event-Ledger cell, and every `findings[]` severity/confidence is byte-equal to its source block — i.e., the manifest copied, it did not compute or embellish. (Implementable stdlib-only: the Timeline pipe-table is already parsed by `timeline_checks.py`'s header-driven column mapping; finding blocks by the `apodictic_artifacts` engine.) |
| **E5 — no duplicate entry** | ERROR | A `scenes[].scene_id` or `findings[].id` appears at most once. A repeated scene double-draws the pacing bar and inflates the POV time-share; a repeated finding double-counts a chapter's severity bar — a chart element showing a value the sources did not contain. The per-id E2/E4 checks pass on a duplicate (each copy resolves and byte-matches), so uniqueness is its own gate. |
| **W1 — coverage** | WARN (ERROR under `--strict`) | A present `Timeline.md` exists but is not represented in `scenes[]` (silent under-rendering). Advisory: a partial map is legitimate. W1 checks *inclusion only* — it does **not** re-validate the Timeline's arithmetic or anchors (that is `timeline-*`'s job). |
| **W2 — scene order** | WARN (ERROR under `--strict`) | The `scenes[]` order follows the Timeline's document order. The pacing curve's x-axis is raw `scenes[]` order, so a reordered manifest draws a false pacing shape while passing every per-id check — order is a data channel the set-based E-checks don't close. |

**Ownership boundary.** `manuscript-viz` owns **manifest↔source provenance** for the visualization artifact: schema, verbatim-copy fidelity, chapter-placement honesty, and Must-Fix inclusion. It does **not** re-check severity fidelity in the letter (`softness-check`), cross-artifact letter integrity (`finding-trace`), or Timeline arithmetic/anchors (`timeline-arithmetic`, `timeline-anchor-conflict`). It *consumes* the Timeline's already-validated rows; it does not re-derive them.

## Canonical `--check-all` gate

A worked example — `references/example-structure-map-manifest.md` (the manifest) paired with the existing `example-timeline.md` and `example-findings-ledger.md` as its sources, plus `example-argument-state-predraft.md` as the claim-ladder spine — is added, and `validate.sh --check-all` runs `manuscript-viz` against it. This proves provenance closure, verbatim fidelity, and Must-Fix completeness on the canonical framework's own worked artifacts, not merely on the validator's fixtures (the "canonical-framework validator runs as release gate" discipline, `ROADMAP.md` §Deferred). The example exercises the `F-RR-01` Must-Fix (a `Chapter 9` finding) landing in the Ch-9 bin, the Timeline's three scenes feeding charts 1–2, and the **claim ladder** (C1/C2/C3) byte-traced to the pre-draft Argument_State spine + its support plan (X1/X5/X6/X7).

## Increment plan

**Increment 1:** the `apodictic.viz_manifest.v1` schema (added to `schemas/`, auto-discovered by `apodictic_artifacts.known_schema_ids()` — which globs the directory — so `structured-findings` recognizes the block, exactly as the finding/feedback schemas are), `scripts/viz_manifest.py` (extractor + validator), `validate.sh manuscript-viz`, the new single-file SVG renderer for charts 1–3, the worked example, and the `--check-all` gate.

**Manuscript-Visualization Completion (built — render-only M1):** the four OPTIONAL, additive `apodictic.viz_manifest.v1` arrays (`co_presence`/`scene_functions`/`reveal_points`/`claim_ladder`); the `manuscript-viz` gates X1/X5/X6/X7/X8 + W3; and the **render-only claim-ladder chart** (chart 7-nonfiction) over `argument_spine.v1` + `support_plan.v1` (no new schema, no new validator, no scene axis — the validator count stays DERIVED). The three producer-gated arrays exist in the schema but render nothing until their producer lands (a present array fails X8).

**Future increments (not built — producer-gated):**
- Charts 4–6 (reveal/tension timeline, character co-presence network, scene-function heatmap) and chart 7-fiction (beat-map-against-spine) — each gated on a **producer** increment (`apodictic.tension_point.v1` / `apodictic.scene_roster.v1` / `apodictic.scene_function.v1` / `apodictic.story_spine.v1`) that makes its upstream artifact machine-readable, plus (for charts 4/5/6) a validated `evidence_ref → scene_id` resolution for scene-precise placement.
- **Claim-to-scene overlay** *(out of scope)* — a future `apodictic.claim_locus.v1` (or `support_plan.loci[]`) mapping a subclaim to the scene(s)/section(s) that advance it; no such producer exists today, so the claim ladder is the declared ladder only.
- **Draft-over-draft visual diff** — render two manifests side by side, highlighting structural change between revision rounds. Natural pairing with [Draft-over-Draft Structural Regression Testing](../ROADMAP.md#horizon-capacities) (Horizon item 6); the manifest is the diff unit.
- **Letter-embedded thumbnails** — inline the pacing curve and severity map into the editorial letter.

## Open questions

- **Render location.** Pure-Python SVG emission (stdlib, no deps — consistent with the runtime's stdlib-only constraint) vs. a templated static HTML with inline SVG. Leaning Python-emits-SVG so the render stays adjacent to the manifest it validates.
- **Partial manuscripts.** On a partial draft, the pacing curve is honest but incomplete. The header must label it partial (reuse the Partial Manuscript Diagnostic framing) so the shape is not read as a finished arc.
- **Viewer variance.** "Self-contained" means no network/deps; exact rendering still depends on the viewer's SVG/CSS support. The artifact targets evergreen browsers and does not promise pixel-identity across all viewers.
