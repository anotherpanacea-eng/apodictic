# Editor Scaffolding — analytical assist for human developmental editors

**Status:** Increment 1 **built**; the **Editor ↔ author dual-output** increment **built** (see §Dual-output). Per-pass scaffolding and blind-spot ranking remain deferred. Roadmap: `ROADMAP.md` → Operators → Editor Scaffolding. Implementation: `plugins/apodictic/skills/core-editor/references/editor-scaffolding.md` (mode contract), `run-synthesis.md §Operator Mode: Editor Scaffolding` (synthesis hook), the intake-router `operator:editor` flip (gap → built), `scripts/editor_scaffolding.py`, `validate.sh editor-scaffolding` (+ `--dual` arm and canonical `--check-all` gate), and the worked examples `references/example-editorial-letter-scaffolded.md` (editor side) + `references/example-editorial-letter-dual-author.md` (author side).

A human developmental editor is using APODICTIC as an *analytical assistant*, not as the editor of record. They have already read the manuscript and formed their own view; what they want from the framework is **a second pair of eyes that surfaces what their own read might have under-weighted** — not a finished author-facing edit letter that competes with the one they will write. The author-facing default letter is the wrong artifact for this reader: it addresses the author, hands the author a revision plan, and translates every framework term into plain language the editor does not need. Editor Scaffolding re-aims the same diagnosis at the editor.

This is an **operator mode**, not a workflow or a command. It is reached by the existing `/start` router (`operator:editor`, Question 3 option E) or by any Core DE command carrying the `operator:editor` flag. It changes how the editorial letter is **framed and addressed** — it does not change which passes run, what gets diagnosed, or how severe a finding is.

## The three shifts (the contract)

Editor Scaffolding is a **superset overlay** on the standard Core DE editorial letter (`run-synthesis.md §Presentation Format`). Every mandatory section the author-facing letter requires is still present — Protected Elements, Author Decisions, Control Questions, Appendices A/B/C, per-Must-Fix evidence density — so the standard gates (`decision-layer-check`, `severity-floor`, `softness-check`, `finding-trace`) still apply unchanged. On top of that, three things shift:

1. **Audience reorientation (addressee = the editor).** The letter opens with an **Editor Brief** rather than "The Short Version": a peer handoff that names the asset, the liability, the verdict class, and — the part a fellow editor actually wants — *where my read and yours are most likely to diverge*. Because the reader is a professional editor, the author-facing-language translation requirement (`output-policy.md §Author-Facing Language`) is **relaxed, not waived**: framework vocabulary (Must-Fix / Should-Fix / Could-Fix, pass names) may appear in the body; obscure internal codes still get a gloss on first use.

2. **Blind-spot emphasis (the value-add).** A required **What You Might Have Missed** section surfaces the findings most likely to be under-weighted on a confident first editorial read: low-salience structural issues, problems *masked by strong prose*, findings that cut against the manuscript's apparent strengths, and cross-pass patterns no single read assembles. This is the reason an editor runs the tool — not to re-list the obvious, but to catch the blind spots. It draws from the Findings Ledger's notable findings and the Adversarial Reader Stress Test.

3. **Prescription deferral (the human editor owns the fix).** The Firewall already forbids content invention; scaffolding extends the boundary one step at the *presentation* layer: the framework does not hand the **author** a revision plan, because the human editor — who knows this author, this relationship, and this market — will author and phrase the prescription. The author-facing "Revision Checklist" is reframed as an **Intervention Menu (editor's discretion)**: option-classes the editor can adopt, modify, sequence, or reject. Author-directed second-person imperatives ("you should rewrite…", "add a scene where…") are out of register here; they address the author, whom the editor — not the framework — is speaking to.

## What is preserved (non-negotiable)

Scaffolding changes *framing and addressee*, never *severity or evidence*. The following hold exactly as in the author-facing letter:

- **Severity honesty.** The Deficit Lock and `softness-check` run unchanged. Reframing for an editor audience is a recognized softening vector ("the editor can decide how bad it is") — it is explicitly forbidden. A locked Must-Fix is delivered as a Must-Fix.
- **The Firewall.** No new plot, characters, imagery, or prose. Intervention *classes* only.
- **Evidence density, the decision layer, and the mandatory appendices.** Protected Elements (3–6), Author Decisions (3–7), Control Questions (exactly 7), Appendices A/B/C, and ≥2 references per Must-Fix all remain — the scaffolded letter is a superset, so `decision-layer-check` passes on it.

## The scaffolded letter (section map)

| # | Section | vs. author-facing default | Gated by |
|---|---------|---------------------------|----------|
| — | `<!-- mode: editor-scaffolding -->` marker | new (declares the mode) | `editor-scaffolding` E1 |
| 1 | Title Block | unchanged | — |
| 2 | **Editor Brief** | replaces "The Short Version"; addressee = editor; names divergence zones | `editor-scaffolding` E1 |
| 3 | What the Book Does Best | unchanged (still the protect-list basis) | — |
| 4 | What Needs Work | unchanged; severity tokens kept | `severity-floor`, `editor-scaffolding` E4 |
| 5 | **What You Might Have Missed** | new (blind-spot inventory) | `editor-scaffolding` E2 |
| 6 | **Intervention Menu — editor's discretion** | reframes "Revision Checklist" as option-classes | `editor-scaffolding` E3 |
| 7 | Protected Elements | unchanged | `decision-layer-check` |
| 8 | Author Decisions | unchanged headings; intro reframed ("surface with the author") | `decision-layer-check` |
| 9 | Control Questions | unchanged (still exactly 7; these are explicitly "for the author and editor") | `decision-layer-check` |
| 10 | The Strongest Case Against | unchanged | — |
| 11 | Adversarial Reader Stress Test | unchanged | — |
| 12 | Appendices A/B/C | unchanged | `decision-layer-check` |

## The `editor-scaffolding` validator (Increment 1)

`validate.sh editor-scaffolding <editorial_letter> [--strict]` (or a run folder; it resolves the newest `*_Editorial_Letter_*.md` / `*_Synthesis_*.md`). Delegates to `scripts/editor_scaffolding.py`; degrades to an advisory `WARN` without `python3`.

**Conditional enforcement.** The validator only enforces the scaffolding contract when the letter **declares** the mode (`<!-- mode: editor-scaffolding -->`). A letter without the marker is an ordinary author-facing letter — the validator reports "not in editor-scaffolding mode" and exits `0`. This makes it safe to run over *every* letter (e.g., in a batch gate) without false positives on author-facing runs.

| ID | Severity | Rule |
|---|---|---|
| **E1 — mode + addressee** | ERROR | The mode marker is present **and** the letter carries the editor addressee: a non-empty `## Editor Brief` section **in the body**. A bare marker with no Editor Brief, or an Editor Brief with no marker on an otherwise scaffolded-looking letter, fails. |
| **E2 — blind-spot section** | ERROR | A non-empty **What You Might Have Missed** section is present **in the body** (heading match, ≥1 content line). The scaffolding value-add cannot be silently dropped — and an appendix heading does not satisfy it. |
| **E3 — prescription deferral** | ERROR | An **Intervention Menu** heading is present **in the body** (the editor-discretion reframe of the revision guidance). Override: `<!-- override: scaffolding-checklist — <rationale> -->` in the body, for a run that deliberately keeps an author-facing checklist. |
| **E4 — severity preserved** | ERROR | At least one canonical severity token (`Must-Fix` / `Should-Fix` / `Could-Fix`) still appears in the body. Scaffolding reframes the addressee, it does not strip severity. (Locked→delivered fidelity stays owned by `softness-check`; E4 only guards against a scaffolded letter that drops the vocabulary entirely.) |
| **W1 — author-directed prescription leak** | WARN (ERROR under `--strict`) | An author-directed prescriptive imperative appears in the body, in either form: **modal second-person** ("you should rewrite", "you need to add", "you must cut") or a **bare imperative at a line / list-item start** ("Add a scene where…", "Cut the prologue", "Rewrite the climax"). In scaffolding mode the prescription belongs to the human editor; these address the author. The bare form is anchored to a line start so it can't fire on a mid-sentence substring, and the verb set is direct manuscript-mutation verbs only — intervention *classes* ("Restore the causal beat", "Redistribute the aftermath") and the Keep/Cut/Unsure Author-Decisions labels are not in it. Advisory because prose detection is heuristic and legitimate quotation exists; override `<!-- override: scaffolding-prescription — <rationale> -->`; `--strict` makes it a gate. |

**Body scope.** E1–E3 (the required scaffold sections), E4 (severity vocabulary), and W1 (prescription scan) are all evaluated over the **body** — everything before the first `Appendix A` heading, the same boundary `softness-check` uses — so an appendix can neither satisfy a required body section nor (for W1) trip the prescription scan.

**Report.** A one-line mode banner plus one line per check. Exit `0` clean / WARN-only, `1` on any ERROR (or WARN under `--strict`), `2` usage.

**Ownership boundary.** `editor-scaffolding` owns the **operator-mode presentation contract** — the addressee reorientation, the blind-spot surfacing, the prescription-deferral reframe, and severity-vocabulary preservation — classes no other validator raises. It does **not** re-check severity fidelity (`softness-check`), the decision-layer counts (`decision-layer-check`), the Firewall content-invention rule (an editorial QA gate), or weak-axis coherence (`severity-floor`). Those validators run **alongside** it on the same scaffolded letter, unchanged.

## Canonical `--check-all` gate

`references/example-editorial-letter-scaffolded.md` is a contract-conformant worked example of a scaffolded letter. `validate.sh --check-all` runs `editor-scaffolding` **and** `decision-layer-check` **and** `severity-floor` against it — proving the overlay *composes* with the standard gates on the canonical framework's own example, not merely that the validator passes its own fixtures. (This is the "canonical-framework validator runs as release gate" discipline, ROADMAP §Deferred.)

## Dual-output (Editor ↔ author)

An editor who wants **both** artifacts — the editor-scaffolded letter to work from *and* the author-facing letter to hand the author — runs a **dual-output** run: one diagnosis, emitted as two letters. The editor letter carries the mode marker and the three scaffold sections (Editor Brief / What You Might Have Missed / Intervention Menu); the author letter is an ordinary author-facing synthesis (The Short Version / What Needs Work / Revision Checklist) — no editor marker, no editor-only sections. The **same `editor-scaffolding` validator** validates the pair (no new validator; the derived count is unchanged) via a two-file arm:

`validate.sh editor-scaffolding --dual <editor_letter> <author_letter> [--strict]`

The convention is a **two-file flag**, not a second marker, because the invariant is *cross-file* — it relates two artifacts — and the fleet's other cross-artifact gates (`finding-trace <ledger> <letter>`, `softness-check <letter> <ledger>`, `continuity-bible <bible> <timeline>`) already take positional file pairs. A marker embedded in one file can't point at the other.

| ID | Severity | Rule |
|---|---|---|
| **D1 — editor side** | ERROR | The editor letter **declares** the mode (`<!-- mode: editor-scaffolding -->`) **and** passes the full E1–E4 contract (reuses `check`; `--strict` propagates, so a W1 leak on the editor side fails under `--strict`). A no-op author-facing letter can't stand in for the editor side. |
| **D2 — author side (register)** | ERROR | The author letter is in **author register**: it does **not** carry the editor marker or any of the three editor-only section headings (Editor Brief / What You Might Have Missed / Intervention Menu) — the leak scan runs over the **whole** author document, so a leak hidden in an appendix still fails — **and** it **does** carry a `Revision Checklist` heading in the body (the positive register anchor, so D2 can't pass vacuously on a file that merely omits editor scaffolding). D2 never inspects the *content* of the checklist — the framework does not author the author-facing prescription (**Firewall preserved**); D2 only checks the letter is in the right register. |
| **D3 — verdict consistency** | ERROR | The **highest canonical severity band** (Must-Fix > Should-Fix > Could-Fix) present in each letter's **body** must **match**. Both letters derive from one diagnosis, so the verdict class can't be softened on either side (a Must-Fix on the editor side can't quietly become a Should-Fix for the author). |

**Why D3 is a hard gate, not advisory.** The invariant is purely mechanical — token extraction plus a fixed rank, no prose reading — and it enforces the same severity-honesty principle the single-file E4 and `softness-check` protect, now *across* the two outputs. Because there is no semantic judgment involved, a mismatch is always a real inconsistency, so D3 is an ERROR. (The "share a manuscript identifier" alternative was rejected as the primary invariant: filenames/titles drift for benign reasons, so it would be a weaker, false-positive-prone signal than the severity band.)

`validate.sh --check-all` runs the `--dual` arm over the canonical pair (`example-editorial-letter-scaffolded.md` as the editor side, `example-editorial-letter-dual-author.md` as its author companion — same manuscript, same Must-Fix verdict), alongside the single-file scaffolded gate.

## Increment boundaries

**Increment 1:** the mode contract, the synthesis hook, the router flip, the validator (E1–E4 + W1), the worked example, and the `--check-all` composition gate.

**Editor ↔ author dual-output (built):** the `--dual` two-file arm (D1/D2/D3 above), the author-facing worked example, and its `--check-all` gate — generating the editor-scaffolded letter *and* the author-facing letter from one diagnosis, for an editor who wants both.

**Future increments (not built):**
- **Per-pass editor scaffolding** — reframing individual pass artifacts (not just the synthesis letter) for the editor audience.
- **Blind-spot ranking** — ordering the "What You Might Have Missed" section by the gap between a finding's structural severity and its surface salience (how easy it is to miss), rather than by severity alone.
- The sibling operators **Diagnostic Vocabulary Mode** (`operator:facilitator`) and **Multi-Party Intake** (`operator:team`) remain separate ROADMAP gaps.
