---
description: Generate a targeted beta-reader questionnaire from the diagnosis's open uncertainties
argument-hint: point to the run folder / Findings Ledger, or no argument
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

Beta-Reader Instrument Generation. The upstream complement to Feedback Triage: instead of handing beta readers "tell me what you think" and getting back noise, this turns the diagnosis's *own* open uncertainties into a focused, non-leading reader questionnaire — so the feedback that comes back is the feedback worth triaging.

Load `../skills/revision-coach/SKILL.md` and follow `../skills/revision-coach/references/beta-reader-instrument.md`.

**Firewall (coaching + content-neutral):** the coach *structures* questions from existing diagnosis; it never re-diagnoses, and a question never introduces a plot event, character, or fix that is not already on the page, and never smuggles a verdict ("don't you think the prologue drags?"). It probes the reader's experience of what exists.

**Severity honesty — the hard boundary:** the instrument tests **uncertainty, not certainty**. It draws only from `LOW`/`UNCERTAIN` findings, Unresolved Questions, and `risk_if_fixed` tradeoffs. It does **not** turn a locked verdict (Must-Fix/Should-Fix at HIGH/MEDIUM confidence) into a "did this bother you?" reader poll — that softens a severity by survey. Testing *how* to fix (not *whether* it is broken) is available by explicit override.

**Mode selection:**

1. **No Findings Ledger / `Diagnostic_State.md` at the project root** → run `/diagnose` first; the instrument needs a diagnosis to harvest uncertainty from.

2. **Harvest uncertainties** → scan the Findings Ledger for `LOW`/`UNCERTAIN` `apodictic.finding.v1` blocks, the `### Unresolved Questions` bullets, and `risk_if_fixed` tradeoffs. (Not the editorial letter's Control Questions — those are author/editor-facing, not reader questions.)

3. **Draft questions** → one `apodictic.reader_question.v1` block per uncertainty in `[Project]_Beta_Reader_Instrument_[runlabel].md`: `source_kind` + provenance (`targets` a finding id, or `source_note` for an Unresolved Question), a non-leading content-neutral `question`, and an `expected_signal` (what a confirming vs. refuting answer looks like). Skip or override locked targets.

4. **Then:** field the instrument to readers → returned answers re-enter through Feedback Triage (`/triage-feedback`) as `feedback_item`s, where APODICTIC's own re-analysis (not reader vote) sets the assessment.

**Gate before finalizing:** `scripts/validate.sh reader-instrument <run_folder>` (add `--strict` for CI). Resolve any ERROR (broken contract / dangling provenance) and review B4 (leading / invented content), B5 (relitigating a locked verdict), and W1 (an uncertainty left untested). See `docs/beta-reader-instrument.md`.

**State and output locations** (per `../skills/core-editor/references/output-structure.md` §Folder Architecture):
- Read `Diagnostic_State.md`, `SYNTHESIS.md`, and the Findings Ledger from the **project root**
- Write the active `[Project]_Beta_Reader_Instrument_[runlabel].md` to the **project root**; archive into `runs/YYYY-MM-DD_{model}_coaching/` on completion
- Never write to the plugin repo

If a run folder or Findings Ledger path is provided: $ARGUMENTS
