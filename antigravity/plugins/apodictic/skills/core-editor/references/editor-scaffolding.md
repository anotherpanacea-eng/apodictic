# Editor Scaffolding (operator mode)

**Status:** v1 (Increment 1)
**Trigger:** `operator:editor` flag from the intake router (Question 3 option E — "I'm editing someone else's work"), or any Core DE command carrying `operator:editor`.
**Applies to:** the Core DE editorial letter (synthesis). Pass artifacts are unchanged in this increment.
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
| 5 | **What You Might Have Missed** | new — blind-spot inventory |
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
