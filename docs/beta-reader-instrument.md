# Beta-Reader Instrument Generation — ask readers the right questions

**Status:** **Built.** Roadmap: `ROADMAP.md` → [Horizon Capacities](../ROADMAP.md#horizon-capacities) Tier 1, item 3. Implementation surface: the `revision-coach/references/beta-reader-instrument.md` mode, the `commands/reader-questions.md` command (`/reader-questions`), `scripts/reader_instrument.py`, `validate.sh reader-instrument` (+ `--check-all` gate), and a worked example with a paired uncertainty-fixture ledger. Schema: `apodictic.reader_question.v1`.

[Feedback Triage](feedback-triage.md) solved the *downstream* half of the reader loop: a writer returns with a pile of beta feedback and the coach sorts, validates, and prioritizes it. But nothing helps the writer *get the right feedback in the first place*. A writer who hands beta readers "tell me what you think" gets back noise — typo notes, taste opinions, plot fan-fiction — while the questions the diagnosis actually left open ("does the midpoint reversal land, or did I only think it lands?") go unasked. The instrument is the **upstream complement**: it turns the diagnosis's own *open uncertainties* into a targeted reader questionnaire, so the feedback that comes back is the feedback worth triaging.

This closes the loop end to end: **diagnose → (this) ask the right questions → collect → [triage](feedback-triage.md) → revise.** It lives in the **revision-coach** skill and inherits the coaching firewall (it structures and routes; it never re-diagnoses).

## What it tests — and what it must never test

The instrument operationalizes the places the framework is **genuinely uncertain**, drawn from artifacts that already exist *and carry the structure the validator needs*:

1. **Low-confidence findings** — `apodictic.finding.v1` blocks with `confidence` of `LOW` or `UNCERTAIN`. The engine's own "I think, but I'm not sure." These are the prime targets, and the only ones with durable IDs (`F-…`) the validator can resolve by reference.
2. **Unresolved Questions** — the Findings Ledger's `### Unresolved Questions` section (see `findings-ledger-format.md`), questions a pass surfaced but could not settle from the text. These are **free-prose bullets with no ID scheme**, so a question seeded from one records its prose source in `source_note`; it is *not* a referential `targets` (see schema + `B3`).
3. **Tradeoff zones** — a finding's `risk_if_fixed`, where the fix has a real cost worth checking with readers before committing.

**Not a source: the letter's Control Questions.** It is tempting to harvest the editorial letter's seven Control Questions, but the canonical spec is explicit that they are **"not 'reader questions' and not workshop prompts"** — they are control questions *for the author and editor* (`run-synthesis.md`). Handing them to a beta reader would import author-facing, often leading framings — the exact failure `B4` exists to prevent. A Control Question may *inspire* an RQ only after being rewritten into a non-leading experiential probe; it is never a direct source, and the instrument does not treat it as one.

**The hard boundary (severity honesty).** The instrument **does not relitigate locked verdicts.** Turning a locked Must-Fix into a "did this bother you?" reader poll is the [author-editor concession antipattern](../ROADMAP.md#horizon-capacities) (Horizon item 16, *surfaced but not viable*) wearing a survey costume: it uses reader opinion to soften a severity the Deficit Lock locked. This capability is viable **precisely because** it tests uncertainty and refuses to test certainty. A finding is "locked" when its severity is **Must-Fix or Should-Fix** at **HIGH or MEDIUM** confidence; targeting one trips `B5`. Only `LOW`/`UNCERTAIN` findings (genuine doubt) are freely testable. The legitimate exception — testing *how* to fix, not *whether* it is broken — is available by explicit override, so the boundary is visible when crossed.

## The structured artifact

Each question is a real-JSON `apodictic.reader_question.v1` block (same envelope + schema engine as `apodictic.finding.v1` / `apodictic.feedback_item.v1`) in a `[Project]_Beta_Reader_Instrument_[runlabel].md` artifact:

```markdown
<!-- apodictic:reader_question
{
  "schema": "apodictic.reader_question.v1",
  "id": "RQ-01",
  "source_kind": "low-confidence-finding",
  "targets": "F-P5-02",
  "source_note": "",
  "uncertainty": "Pass 5 suspects the midpoint reversal under-lands but confidence is LOW.",
  "probe_type": "experiential",
  "question": "At the point where the lead changes course midway through, what did you expect to happen next — and did the story go there?",
  "expected_signal": "Readers who can't locate a midway change, or report no shift in expectation, corroborate the under-landing; readers who name the turn refute it."
}
-->
```

- **`source_kind`** — `low-confidence-finding` / `unresolved-question` / `tradeoff`. A closed enum; determines which provenance field is required (`B3`).
- **`targets`** — the `F-…` finding ID, **required when `source_kind` is `low-confidence-finding` or `tradeoff`** (both come from findings), and resolved by reference (`B3`). Omitted/empty for `unresolved-question`.
- **`source_note`** — free-prose pointer to the Unresolved-Questions bullet, **required when `source_kind` is `unresolved-question`** (since those have no ID).
- **`uncertainty`** — the framework-side doubt being tested, in the framework's own words (not new content).
- **`probe_type`** — `experiential` / `comprehension` / `attention` / `preference` / `recall`. A closed enum.
- **`question`** — the reader-facing wording: **open and non-leading** (see Firewall).
- **`expected_signal`** — what a confirming vs. refuting answer looks like, so returned answers map cleanly to `assessment` values in Feedback Triage.

`id` is `RQ-<NN>` (unique per instrument). The flat, all-string/enum field set is within the subset schema engine's capability. The field set is canonical in `schemas/apodictic.reader_question.v1.schema.json`.

## Firewall compliance

Generating a question generates *text*, so the firewall applies at the question wording:

- **Content-neutral.** A question may probe the reader's experience of what is *on the page*; it may never introduce a plot event, character, image, or solution that is not. "Did you find the dragon's ice-breath powerful?" invents the ice-breath — forbidden. The question references only the author's existing elements (by the finding's own terms) and the reader's reaction to them.
- **Non-leading.** The question must not smuggle a verdict or a fix. Leading constructions ("Don't you think the prologue drags?", "Wouldn't it be better if…", "Did you like how the pacing improved?") pre-load the answer and corrupt the signal.
- **No prescription.** `expected_signal` describes how to *read* an answer; it never tells the reader or author what to change.

`B4` is the **partial** mechanical proxy for these rules, and the spec is honest about which half is real: the **leading-construction** scan is a finite phrase blocklist (sound, like `tone-check`'s superlative blocklist); the **content-neutrality** scan is a *coarse* heuristic (flag quoted or capitalized noun phrases in the `question` that do not appear in the target finding's text), not a true manuscript-traceability check — it catches the blatant cases and will miss subtle invention. Advisory by default, so the heuristic never hard-blocks on a false positive.

## Severity honesty

- **Tests uncertainty, not certainty.** Targets are `LOW`/`UNCERTAIN` findings, open questions, and tradeoffs. Targeting a *locked* finding (Must-Fix/Should-Fix at HIGH/MEDIUM confidence) trips `B5` — overridable for "how to fix," never silently. *Known gap:* an RQ sourced from an Unresolved Question carries no confidence, so `B5` cannot reach a UQ that is secretly a proxy for a locked finding; the workflow protocol (step 2) flags such proxies for the coach, but `B5` is a finding-confidence gate and does not claim to catch them.
- **A locked verdict stays locked regardless of the answers.** The instrument gathers evidence for the *next* triage; it has no authority to downgrade a finding. Returned answers re-enter through Feedback Triage as `feedback_item`s, where `assessment` is set by *APODICTIC's own targeted re-analysis*, not by reader vote.
- **No leading toward the desired answer.** `B4`'s non-leading rule is also a severity-honesty rule: an instrument that fishes for "actually it was fine" is softening by survey design.

## The `reader-instrument` validator

`validate.sh reader-instrument <run_folder>` (resolves the `*_Beta_Reader_Instrument_*.md` artifact + the Findings Ledger it targets). Delegates to `scripts/reader_instrument.py`; degrades to advisory `WARN` without `python3`. Report lines namespaced `reader-instrument:<ID>`.

| ID | Severity | Rule |
|---|---|---|
| **B1 — invalid item** | ERROR | A `reader_question` block fails its schema (bad `source_kind`/`probe_type` enum, malformed `id`, missing required field, broken JSON). Delegated to the schema engine. |
| **B2 — duplicate id** | ERROR | Two questions share an `RQ-NN` id. |
| **B3 — provenance integrity** | ERROR | Provenance matches `source_kind`: a `low-confidence-finding`/`tradeoff` question carries a `targets` that **resolves to a real `apodictic.finding.v1` ID** in the Ledger (reused from `finding_trace`'s ID resolver); an `unresolved-question` question carries a non-empty `source_note` and **no** `targets`. (Referential integrity is enforced only where stable IDs exist — findings; UQ targeting is intentionally non-referential because the ledger has no UQ-ID scheme, and inventing brittle prose-matching here is exactly what the Validator Hardening track forbids.) |
| **B4 — leading / invented content** | WARN (ERROR under `--strict`) | The `question` matches a leading construction (finite blocklist) **or** introduces a quoted/capitalized noun phrase absent from the target finding's text (coarse content-neutrality heuristic). Firewall made *partly* checkable; advisory because both detections are heuristic — override `<!-- override: leading-question RQ-NN — <rationale> -->`; `--strict` gates. |
| **B5 — relitigating a locked verdict** | WARN (ERROR under `--strict`) | A `targets` finding is **locked** — severity ∈ {Must-Fix, Should-Fix} **and** confidence ∈ {HIGH, MEDIUM}. (Gating on *locked severity*, not just HIGH confidence, closes the MEDIUM-Must-Fix hole.) Override `<!-- override: how-to-fix RQ-NN — testing fix approach, not the verdict -->`; `--strict` gates. |
| **W1 — coverage** | WARN (ERROR under `--strict`) | A `LOW`/`UNCERTAIN` finding or an Unresolved-Questions bullet has no reader question — a genuine uncertainty left untested. Advisory: a focused instrument is legitimate. |

**Report.** One line per question — `id · source_kind · targets/source · probe_type · flags`. Exit `0` clean / WARN-only, `1` on any ERROR (or WARN under `--strict`), `2` usage. Overrides honored for B4/B5, matching `editor-scaffolding` / `feedback-triage`.

**Ownership boundary.** `reader-instrument` owns the **question-contract**: schema hygiene, provenance integrity (where IDs exist), the non-leading/content-neutral firewall scan, and the anti-relitigation severity gate — classes no other validator raises. It does **not** judge the *findings* it targets (the finding/severity validators own those), re-check letter↔ledger integrity (`finding-trace`), or process *returned answers* (those become `feedback_item`s governed by `feedback-triage`). It is the upstream mirror of `feedback-triage`, exactly as `feedback-triage` is the thin orthogonal layer over `structured-findings`.

## Workflow (revision-coach)

`/reader-questions` (or `/coach` routing to Beta-Reader Instrument mode); full protocol in `revision-coach/references/beta-reader-instrument.md`:

1. **Harvest uncertainties.** Scan the Ledger for `LOW`/`UNCERTAIN` findings, the Unresolved Questions, and `risk_if_fixed` tradeoffs. (Not the Control Questions — see above.)
2. **Draft questions.** One `reader_question` per uncertainty, content-neutral and non-leading, with `expected_signal`. Skip (or override) locked targets; flag any Unresolved Question that is really a proxy for a locked finding (the gap `B5` cannot see).
3. **Gate.** `validate.sh reader-instrument <run_folder>` (`--strict` in CI) before the instrument goes to readers.
4. **Field & collect.** The writer circulates the instrument (render targets in §Future increments).
5. **Hand off to triage.** Returned answers enter [Feedback Triage](feedback-triage.md) as `feedback_item`s; each item's `evidence_refs` cite the `RQ-…` and the original `F-…` **by prose convention** (the `feedback_item` schema's `evidence_refs` is a free string array — nothing yet cross-checks the RQ exists; structured RQ→FB cross-checking is the Increment-2 `maps_to`, mirroring Feedback Triage's own Increment-2 plan).

## Canonical `--check-all` gate

A worked example — `references/example-beta-reader-instrument.md` paired with **a net-new fixture Findings Ledger** (`references/example-uncertainty-ledger.md`) carrying one `LOW`-confidence finding and one Unresolved-Questions bullet — is added, and `validate.sh --check-all` runs `reader-instrument` resolving **both files together**. It proves `B3` provenance integrity on a real `LOW` finding, a `source_note`-only UQ question, a clean non-leading `B4`, and an uncertainty-targeted question that does **not** trip `B5`. (The shipped `example-findings-ledger.md` carries only a single HIGH-confidence Must-Fix — which would *correctly* trip `B5` — and `### Unresolved Questions: none`, so it cannot host this gate; the dedicated fixture supplies the uncertainty the worked example needs, per the "canonical-framework validator runs as release gate" discipline, `ROADMAP.md` §Deferred.)

## Increment plan

**Increment 1 (this spec):** the `apodictic.reader_question.v1` schema (added to `schemas/`, auto-discovered by `apodictic_artifacts.known_schema_ids()`, which globs the directory), `scripts/reader_instrument.py` (extractor + validator), `validate.sh reader-instrument`, the `/reader-questions` command + revision-coach reference, **both** the worked example and the paired fixture ledger, and the `--check-all` gate. Validators +1 (running total fixed at build).

**Future increments (not built):**
- **RQ → FB id linking.** A structured `maps_to` on the returned `feedback_item`, cross-checked against the instrument (a triaged answer must point at a real `RQ-…`), pairing with Finding Lifecycle IDs — the symmetric move to Feedback Triage's own Increment-2 `maps_to`.
- **Probe-type templates.** A small library of non-leading question stems per `probe_type`, to make content-neutral phrasing the path of least resistance (and shrink `B4`'s false-positive surface).
- **Survey export.** Render the instrument to plain text / Google Forms / a printable sheet over the same structured artifact.
- **Persona-targeted instruments.** Pair with [Reader-Persona Simulation](../ROADMAP.md#horizon-capacities) (Horizon item 5): persona-specific question sets where the diagnosis predicts the experience diverges by audience.

## Self-review (Increment 1)

- *Why a new validator, not `feedback-triage`* — they are mirror images across the reader loop (questions out vs. answers in) with disjoint invariants: `feedback-triage` owns conflict integrity and act-on-unvalidated; `reader-instrument` owns provenance integrity, non-leading firewall, and anti-relitigation. Folding them would conflate the two halves the loop deliberately separates.
- *Why B3 only enforces finding-ID targets* — findings have durable `F-…` IDs; Unresolved Questions and Control Questions do not. Enforcing referential integrity only where stable IDs exist (and recording UQ provenance as prose) is the honest design; minting brittle UQ/CQ prose-matchers is the regex fragility the Validator Hardening track exists to remove.
- *Why B5 gates on locked severity, not HIGH confidence alone* — a MEDIUM-confidence Must-Fix is still a locked verdict; gating on {Must-Fix, Should-Fix} × {HIGH, MEDIUM} closes that hole. The residual UQ-proxy gap is named, not hidden.
- *Why the firewall scan (B4) is advisory and only half-mechanical* — leading-phrase detection is a sound finite blocklist; content-neutrality against a whole manuscript is not stdlib-precise, so it is a coarse heuristic. Advisory-with-override + `--strict` matches the house posture for heuristic prose detection (`editor-scaffolding` W1).
