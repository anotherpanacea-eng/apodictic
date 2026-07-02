---
description: Sort, validate, and prioritize external feedback (beta readers, critique group, editor)
argument-hint: paste or point to the feedback, or no argument
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

Feedback Triage. For writers returning with external feedback — beta readers, a critique group, an agent or editor — that is often contradictory, uneven, and unvalidated. Sorts each note, checks it against the diagnosis, prioritizes, and resolves contradictions before any revision time is spent.

Load `../skills/revision-coach/SKILL.md` and follow `../skills/revision-coach/references/feedback-triage.md`.

**Firewall:** the coach structures and prioritizes feedback and routes *validation* of a claim to a targeted Core Editor pass (it never runs passes or re-diagnoses itself). A claim our analysis confirms becomes a candidate finding for the ledger.

**Mode selection:**

1. **No `Diagnostic_State.md` at the project root** → run the validation passes you need via `/start` first, or proceed in "structure-only" triage (capture + conflict-resolve now; mark every item `assessment: pending` until a pass confirms it).

2. **Feedback provided or pointed to** → Intake. Capture each note as an `apodictic.feedback_item.v1` block (`source`, `claim`; `assessment: pending`, `triage: monitor`) in `[Project]_Feedback_Triage_[runlabel].md`.

3. **Then:** validate each claim (route to Core Editor targeted passes) → map validated claims to ledger findings → resolve every `conflicts_with` pair (never leave both sides actionable) → set `triage` and produce the prioritized list → hand the act-now set to Session Planning (`/coach`).

4. **Decline reconciliation (engine dispositions):** when an item is triaged `decline` **and** its `evidence_refs` cite a ledger `F-…` id, offer to record an engine finding disposition — `{disposition: declined, source: triage, reason: <item claim + assessment>}` — via the dual-writer path (`../skills/core-editor/references/state-lifecycle.md` §Finding Dispositions): write the pinned `<!-- declined: F-… — <reason> -->` marker in this triage artifact and (non-governed) the sidecar record directly / (governed) let it fold at the next `revision_round` clear. The author decides; the offer is the mechanism. An FB-item decline with no ledger id (external feedback about no engine finding) records nothing — dispositions attach to ledger findings only.

**Gate before finalizing:** `scripts/validate.sh feedback-triage <run_folder>` (add `--strict` for CI). Resolve any ERROR (broken contract / dangling conflict reference) and review W1 (a contradiction left actionable on both sides) / W2 (acting now on an unvalidated claim) / W3 (a declined item citing a ledger `F-…` id with no disposition recorded — the decline lives only in this artifact). See `docs/feedback-triage.md`.

**State and output locations** (per `../skills/core-editor/references/output-structure.md` §Folder Architecture):
- Read `Diagnostic_State.md`, `SYNTHESIS.md`, and the Findings Ledger from the **project root**
- Write the active `[Project]_Feedback_Triage_[runlabel].md` to the **project root**; archive into `runs/YYYY-MM-DD_{model}_coaching/` on completion
- Never write to the plugin repo

If feedback is pasted or a path is provided: $ARGUMENTS
