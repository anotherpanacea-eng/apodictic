# Beta-Reader Instrument — workflow protocol

*Reference file for the APODICTIC Revision Coach. Loaded by `/reader-questions` (and `/coach` → Beta-Reader Instrument mode). The **upstream** complement to Feedback Triage: it generates the questions, then [Feedback Triage](feedback-triage.md) ingests the answers. Spec + validator: `docs/beta-reader-instrument.md`, `scripts/validate.sh reader-instrument`. Worked example: `../../core-editor/references/example-beta-reader-instrument.md` (paired with `example-uncertainty-ledger.md`).*

---

## When to use

A writer has a diagnosis and is about to circulate the draft to beta readers. Handing readers "tell me what you think" returns noise — typo notes, taste opinions, plot fan-fiction — while the questions the diagnosis actually left *open* go unasked. This mode turns the framework's own uncertainties into a targeted, non-leading questionnaire, so the feedback that comes back is worth triaging.

It closes the reader loop end to end: **diagnose → (this) ask the right questions → collect → [triage](feedback-triage.md) → revise.**

## Firewall (inherited, restated) + content-neutrality

The coach **structures** questions from the existing diagnosis; it never re-diagnoses. Two extra rules apply at the question wording, because generating a question generates *text*:

- **Content-neutral.** A question may probe the reader's experience of what is *on the page*; it may never introduce a plot event, character, image, or solution that isn't. "Did you find the dragon's ice-breath powerful?" invents the ice-breath — forbidden. Reference only the author's existing elements (in the finding's own terms) and the reader's reaction.
- **Non-leading.** No smuggled verdict or fix. "Don't you think the prologue drags?", "Wouldn't it be better if…", "Did you like how the pacing improved?" pre-load the answer and corrupt the signal.

## Severity honesty — the hard boundary

The instrument tests **uncertainty, not certainty.** A locked verdict (severity ∈ {Must-Fix, Should-Fix} **and** confidence ∈ {HIGH, MEDIUM}) is **not** a reader poll — turning one into "did this bother you?" uses reader opinion to soften a severity the diagnosis locked. Draw only from:

1. **Low-confidence findings** — `apodictic.finding.v1` blocks with `confidence` of `LOW`/`UNCERTAIN`. The engine's own "I think, but I'm not sure." The prime targets.
2. **Unresolved Questions** — the Findings Ledger's `### Unresolved Questions` bullets (free prose, no id scheme).
3. **Tradeoff zones** — a finding's `risk_if_fixed`, where the fix has a real cost worth checking before committing.

**Not a source: the editorial letter's Control Questions.** They are explicitly "not 'reader questions' and not workshop prompts" (`../../core-editor/references/run-synthesis.md`) — author/editor-facing, often leading if handed to a reader. A Control Question may *inspire* a reader question only after being rewritten into a non-leading experiential probe; it is never a direct source.

The legitimate exception — testing *how* to fix, not *whether* it is broken — is available by explicit override (`how-to-fix`), so the boundary is visible when crossed.

## The structured record

Each question is one `apodictic.reader_question.v1` block (HTML-comment envelope, real JSON, same engine as `apodictic.finding.v1` / `apodictic.feedback_item.v1`) in `[Project]_Beta_Reader_Instrument_[runlabel].md`:

- **`source_kind`** — `low-confidence-finding` / `unresolved-question` / `tradeoff` (selects which provenance field is required).
- **`targets`** — the `F-…` finding id, **required for `low-confidence-finding`/`tradeoff`**, resolved against the Ledger. Omitted for `unresolved-question`.
- **`source_note`** — free-prose pointer to the Unresolved-Questions bullet, **required for `unresolved-question`**.
- **`uncertainty`** — the framework-side doubt being tested, in the framework's own words.
- **`probe_type`** — `experiential` / `comprehension` / `attention` / `preference` / `recall`.
- **`question`** — reader-facing wording: open, non-leading, content-neutral.
- **`expected_signal`** — what a confirming vs. refuting answer looks like, so returned answers map cleanly to `assessment` values in Feedback Triage.

`id` is `RQ-<NN>` (unique). Canonical field set: `schemas/apodictic.reader_question.v1.schema.json`.

## Protocol

1. **Harvest uncertainties.** Scan the Ledger for `LOW`/`UNCERTAIN` findings, the Unresolved Questions, and `risk_if_fixed` tradeoffs. (Not the Control Questions — see above.)
2. **Draft questions.** One `reader_question` per uncertainty, content-neutral and non-leading, with an `expected_signal`. Skip (or `how-to-fix`-override) locked targets. Flag any Unresolved Question that is really a proxy for a locked finding — the `B5` gate is a finding-confidence check and cannot see a UQ that hides one.
3. **Gate.** `scripts/validate.sh reader-instrument <run_folder>` (`--strict` for CI). Resolve ERRORs (broken contract / dangling provenance); review B4 (leading / invented content), B5 (relitigating a locked verdict), W1 (an uncertainty left untested).
4. **Field & collect.** The writer circulates the instrument.
5. **Hand off to triage.** Returned answers enter [Feedback Triage](feedback-triage.md) as `feedback_item`s; each item's `evidence_refs` cite the `RQ-…` and the original `F-…` by prose convention. Crucially, `assessment` is set by **APODICTIC's own targeted re-analysis, not by reader vote** — a locked verdict stays locked regardless of the answers; the instrument only gathers evidence for the next triage.

## Output

`[Project]_Beta_Reader_Instrument_[runlabel].md`:
- **Reader-facing preamble** — "these are questions about *your* experience; answer before discussing with others; there are no right answers."
- **The questions** — the prose list, each carrying its `reader_question` block, grouped by `probe_type` or by manuscript region.

See `../../core-editor/references/example-beta-reader-instrument.md` for a contract-conformant worked example (a `LOW`-finding experiential probe + an Unresolved-Question probe), paired with `example-uncertainty-ledger.md`.

## Degrade path

Without `python3`, `reader-instrument` is advisory: perform the checks inline — every finding-sourced question's `targets` resolves to a real ledger finding; every unresolved-question carries a `source_note` and no `targets`; no question is leading or introduces off-page content; and no question targets a locked verdict (Must-Fix/Should-Fix at HIGH/MEDIUM). The blocks stay human-readable.
