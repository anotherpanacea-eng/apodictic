# Editor Scaffolding (operator mode)

**Status:** v1 (Increment 1 + dual-output + per-pass + blind-spot ranking)
**Trigger:** `operator:editor` flag from the intake router (Question 3 option E — "I'm editing someone else's work"), or any Core DE command carrying `operator:editor`.
**Applies to:** the Core DE editorial letter (synthesis) and — via the `--per-pass` arm — an individual Core DE pass artifact (see §Per-pass scaffolding).
**Does not change:** which passes run, what is diagnosed, or how severe a finding is. This is a presentation overlay, not a different analysis.

---

## Purpose

The reader is a **human developmental editor** using APODICTIC as an analytical assistant, not the editor of record. They have already read the manuscript and formed a view; what they want is a second pair of eyes that surfaces **what their own read might have under-weighted** — not a finished author-facing edit letter that competes with the one they will write.

The default editorial letter is author-facing: it addresses the author, hands the author a revision plan, and translates every framework term into plain language the editor does not need. Editor Scaffolding re-aims the same diagnosis at the editor.

**What this is:** an editor-facing reframe of the synthesis letter — peer handoff, blind-spot emphasis, prescription left to the human editor.

**What this is not:** a different diagnosis, a softer one, or a license to invent content. Severity honesty and the Firewall hold exactly as in the author-facing letter.

---

## The three shifts

Editor Scaffolding is a **superset overlay** on the standard letter (`run-synthesis.md §Presentation Format`). Every mandatory section the author-facing letter requires is still present — Protected Elements, Author Decisions, Control Questions, Appendices A/B/C, per-Must-Fix evidence density — so the standard gates (`decision-layer-check`, `severity-floor`, `softness-check`, `finding-trace`) still apply unchanged. On top of that:

1. **Audience reorientation — the Editor Brief.** Replace "The Short Version" with an **Editor Brief**: a peer handoff that names the asset, the liability, and the verdict class, and then names *where my read and yours are most likely to diverge*. Address the editor, not the author. Because the reader is a professional, the author-facing-language translation requirement (`output-policy.md §Author-Facing Language`) is **relaxed, not waived** — framework vocabulary (Must-Fix / Should-Fix / Could-Fix, pass names) may appear in the body; genuinely obscure internal codes still get a one-time gloss.

2. **Blind-spot emphasis — "What You Might Have Missed."** Add a section that surfaces the findings most likely to be under-weighted on a confident first editorial read: low-salience structural issues, problems *masked by strong prose*, findings that cut against the manuscript's apparent strengths, and cross-pass patterns no single read assembles. Draw from the Findings Ledger's notable findings and the Adversarial Reader Stress Test. This is the reason an editor runs the tool — surface the blind spots, don't re-list the obvious.

3. **Prescription deferral — the Intervention Menu.** The Firewall forbids inventing content; scaffolding extends the boundary one step at the presentation layer: the framework does not hand the **author** a revision plan, because the human editor — who knows this author, this relationship, and this market — will author and phrase the prescription. Reframe the author-facing "Revision Checklist" as an **Intervention Menu (editor's discretion)**: option-classes the editor can adopt, modify, sequence, or reject. Keep author-directed second-person imperatives ("you should rewrite…", "add a scene where…") out of the body — they address the author, whom the editor, not the framework, is speaking to.

---

## What is preserved (non-negotiable)

Scaffolding changes *framing and addressee*, never *severity or evidence*:

- **Severity honesty.** The Deficit Lock and `softness-check` run unchanged. Reframing for an editor audience is a recognized softening vector ("the editor can decide how bad it is") — it is forbidden. A locked Must-Fix is delivered as a Must-Fix.
- **The Firewall** (`core-editor/SKILL.md §The Firewall`). No new plot, characters, imagery, or prose. Intervention *classes* only.
- **The decision layer and mandatory appendices.** Protected Elements (3–6), Author Decisions (3–7), Control Questions (exactly 7), Appendices A/B/C, and ≥2 references per Must-Fix all remain. The Author Decisions intro is reframed as decisions to *surface with the author* (the editor runs that conversation), but the section and its counts stay.

---

## Scaffolded letter — section map

| # | Section | vs. author-facing default |
|---|---------|---------------------------|
| — | `<!-- mode: editor-scaffolding -->` marker (place near the title block) | new — declares the mode |
| 1 | Title Block | unchanged |
| 2 | **Editor Brief** | replaces "The Short Version"; addressee = editor; names divergence zones |
| 3 | What the Book Does Best | unchanged (still the protect-list basis) |
| 4 | What Needs Work | unchanged; severity tokens kept |
| 5 | **What You Might Have Missed** | new — blind-spot inventory; order by blind-spot gap (§Blind-spot ranking) |
| 6 | **Intervention Menu — editor's discretion** | reframes "Revision Checklist" as option-classes |
| 7 | Protected Elements | unchanged |
| 8 | Author Decisions | unchanged headings; intro reframed ("surface with the author") |
| 9 | Control Questions | unchanged (still exactly 7) |
| 10 | The Strongest Case Against | unchanged |
| 11 | Adversarial Reader Stress Test | unchanged |
| 12 | Appendices A/B/C | unchanged |

Worked example: `references/example-editorial-letter-scaffolded.md`.

---

## Mechanical check

`scripts/validate.sh editor-scaffolding <editorial_letter>` enforces the operator-mode contract **only when the letter declares the mode marker** (a letter without it is an ordinary author-facing letter and passes as a no-op):

- **E1** mode marker + a non-empty Editor Brief; **E2** a non-empty "What You Might Have Missed"; **E3** an "Intervention Menu" heading (override `<!-- override: scaffolding-checklist — … -->`); **E4** at least one canonical severity token survives. All four are evaluated over the **body** (before Appendix A), so an appendix heading can't satisfy a required scaffold section.
- **W1** (advisory; ERROR under `--strict`) author-directed prescription in the body — modal ("you should rewrite") or a bare line-start imperative ("Add a scene…", "Cut the prologue"); intervention classes and Keep/Cut/Unsure labels are exempt (override `<!-- override: scaffolding-prescription — … -->`).

Run it alongside `decision-layer-check`, `severity-floor`, and `softness-check` — they all still apply to a scaffolded letter. Design + ownership boundary: [`docs/editor-scaffolding.md`](../../../docs/editor-scaffolding.md).

### Blind-spot ranking (opt-in)

Order the "What You Might Have Missed" section by the **gap** between a finding's structural severity and its surface **salience** (how easy it is to miss), largest gap first — so a high-severity finding that a confident read *glides past* (masked by strong prose) leads, not the obvious ones the editor already caught. Declare the order with one `apodictic.blind_spot_ranking.v1` block per entry, **in display order**, each `{finding_id, severity, salience}` where `salience ∈ {prominent, moderate, subtle}` (mirror the optional `salience` field on `apodictic.finding.v1`). The E2/P2 sub-check then enforces, **only when blocks are present** (no blocks → unranked, still valid): **R1** each block schema-valid; **R2** descending-gap order (`gap = rank(severity) − rank(salience)`, Must-Fix/prominent = 3 … Could-Fix/subtle = 1; ties break by descending severity); **R3** (with `--ledger=<ledger.md>`) each `finding_id` exists in the ledger and its severity matches the locked tier (a laundered severity fails). The model owns severity *and* salience; the validator checks only the arithmetic + order. See [`docs/editor-scaffolding.md` §Blind-spot ranking](../../../docs/editor-scaffolding.md).

## Dual-output (editor ↔ author)

An editor who wants **both** letters — the scaffolded one to work from *and* the author-facing one to hand the author — runs one diagnosis into two letters and validates the pair with the same validator's two-file arm:

`scripts/validate.sh editor-scaffolding --dual <editor_letter> <author_letter>`

- **D1** the editor letter declares the mode and passes E1–E4.
- **D2** the author letter is in **author register** — no editor marker, no Editor Brief / What You Might Have Missed / Intervention Menu, and it carries a **Revision Checklist** heading. (The framework never authors the checklist *content* — D2 only checks register; the Firewall holds.)
- **D3** the highest severity band (Must-Fix > Should-Fix > Could-Fix) matches across both letters — the verdict class can't soften on either side.

Worked pair: `references/example-editorial-letter-scaffolded.md` (editor) + `references/example-editorial-letter-dual-author.md` (author). See [`docs/editor-scaffolding.md` §Dual-output](../../../docs/editor-scaffolding.md).

## Per-pass scaffolding

When an editor wants a **single pass** re-aimed at them — not the whole letter — reframe that pass artifact (`[Project]_Pass<N>_<Name>_<runlabel>.md`) for the editor and validate it with the same validator's single-file per-pass arm:

`scripts/validate.sh editor-scaffolding --per-pass <pass_artifact>`

A pass is a single diagnostic lens, so the reframe is a right-sized subset of the letter's E1–E4 (and marker-conditional, exactly like the letter path — a pass artifact without `<!-- mode: editor-scaffolding -->` is an ordinary diagnostic artifact and passes as a no-op):

- **P1** the marker is present **and** the pass carries a non-empty **Editor Note** — the editor addressee for this pass (what it surfaces + where the editor's read of this layer is likely to under-weight). A distinct heading from the letter's Editor Brief; a pass artifact is not the letter.
- **P2** a non-empty **What You Might Have Missed** section — the per-pass value-add. Carries the **same opt-in blind-spot ranking** as the letter's E2 (§Blind-spot ranking above): if the section has `apodictic.blind_spot_ranking.v1` blocks they must be in descending-gap order; no blocks → unranked, still valid.
- **W1** the same author-directed prescription scan as the letter path (advisory; ERROR under `--strict`; same override). A pass has no Revision Checklist to reframe into an Intervention Menu, so there is no positive per-pass E3, and severity honesty stays owned downstream (the pass flags are locked in the Findings Ledger by `softness-check` / `deficit-lock`) — so there is no mandatory per-pass severity token either (a Pass 0 reverse outline is legitimately severity-free).

All three are evaluated over the **body** (before Appendix A), so an appendix section can't satisfy P1/P2 or hide a W1 leak. Worked example: `references/example-pass-scaffolded.md` (a scaffolded Pass 2 Structural Mapping artifact). See [`docs/editor-scaffolding.md` §Per-pass scaffolding](../../../docs/editor-scaffolding.md).
