# State Lifecycle & Revision Rounds

*Reference file for the APODICTIC Development Editor. Loaded by `/start` (resume gate), `/coach` (revision coaching), and revision round workflows.*
*See also: `handoff-protocol.md` for scene-level execution mode transitions.*

---

## State Gardening Protocol

Over multiple revision rounds, `Diagnostic_State.md` accumulates session history, handoff history, coaching log entries, and resolved material. Unchecked growth crowds active context and makes the resume gate slower. State gardening prevents this entropy.

### Trigger

State gardening runs at the resume gate in `/start`. The trigger is the `state_lines` field in `Diagnostic_State.meta.json` (updated by `scripts/validate.sh state-lines`).

| State Lines | Action |
|---|---|
| < 300 | No gardening needed |
| 300–500 | Advisory: "State file is growing. Consider archiving after this session." |
| > 500 | Required: run gardening before proceeding |

### Gardening Procedure

When gardening is required (or when the user accepts the advisory):

1. **Archive the full state.** Copy `Diagnostic_State.md` to `Diagnostic_State_Archive_[datetime].md` in the project root (same directory as the active state file), where `[datetime]` is ISO 8601 format truncated to minutes (e.g., `2026-04-01T14-30`). Use hyphens instead of colons for filesystem safety. This prevents collision if gardening runs twice on the same day. This is the permanent record — never modify archives.

2. **Compress completed sessions.** Replace each completed session entry in the Session History with a one-line summary:
   ```markdown
   ### Session [N] (archived)
   - [Date]: [Focus]. [Key outcome in one sentence]. Full record: Diagnostic_State_Archive_[datetime].md
   ```

3. **Compress resolved handoffs.** Replace each resolved handoff (Outcome = "resolved") with a one-line summary:
   ```markdown
   ### Handoff [N] (archived)
   - [Scene]: Resolved [date]. Full record: Diagnostic_State_Archive_[datetime].md
   ```
   Unresolved and partially-resolved handoffs remain in full.

4. **Archive resolved control questions.** Move questions with status "answered" to an "Archived Questions" subsection at the bottom of the Control Questions section. Keep only the question text and answer — drop the "why it matters" rationale. Open and deferred questions remain in full.

5. **Compress completed revision steps.** In the Revision Progress checklist, replace completed steps with:
   ```markdown
   1. [x] Contract drift (resolved Session 3)
   ```
   Remove the Change Log entries that correspond to archived sessions. Keep only entries from active (non-archived) sessions.

6. **Update the sidecar.** Set `state_lines` to the new line count. Update `session_count` and `handoff_count` if entries were archived.

7. **Verify.** The gardened state file should be < 300 lines. If it isn't, the manuscript may have unusually many active handoffs or unresolved questions — this is information, not a failure.

### What Gardening Preserves

- All unresolved material (open control questions, active handoffs, in-progress revision steps)
- The full Root Causes table (always active — never archived)
- The full Triage Summary (always active)
- The full Author Decisions section (always active — these are live revision commitments)
- All coaching log entries (append-only, not compressed — the revision coach depends on the full log)
- The current Mode section

### What Gardening Compresses

- Completed session history → one-line summaries with archive pointers
- Resolved handoff history → one-line summaries with archive pointers
- Answered control questions → question + answer only (rationale archived)
- Completed revision steps → checkbox + session reference
- Old change log entries → archived with their sessions

### Design Principle

State gardening is to `Diagnostic_State.md` what garbage collection is to a codebase: pay down entropy continuously in small increments rather than letting it compound. The archive preserves everything; the active state file keeps only what the system needs to make its next decision.

---

## Revision Round Protocol

When re-analyzing a manuscript after author revision, use this protocol instead of starting fresh.

### Revision Round Intake

Before running passes, gather:

1. **What changed?** — List major revisions since last analysis (structural changes, added/cut scenes, character modifications)
2. **Which flags were addressed?** — Mark which previous flags the author attempted to fix
3. **Which flags were declined?** — Note which previous flags the author intentionally chose not to address (and why, if provided)
4. **New concerns?** — What does the author now suspect isn't working?

### Revision Round Constraints

**DO NOT:**
- Re-flag issues the author explicitly declined to address (respect their choices)
- Run full fresh analysis unless structural changes exceed 40% of manuscript
- Apply stricter standards to revised sections than to original analysis

**DO:**
- Focus analysis on changed material + ripple effects
- Check whether addressed flags are now resolved
- Track whether fixes created new problems
- Compare current state to previous Diagnostic State

### Revision Round Passes

**Targeted Pass Sequence:**
1. **Delta Scan:** Identify all changed sections (author-reported + text comparison if available)
2. **Ripple Check:** For each major change, trace downstream effects (Does cutting Chapter 3 break setup for Chapter 12?)
3. **Resolution Verification:** For each "addressed" flag, confirm fix landed (Did the added motivation scene actually establish motivation?)
4. **New Issue Detection:** Run standard passes ONLY on changed sections
5. **Integration Check:** Verify changed sections integrate with unchanged material

### Revision Round Output

**Revision Report** (not full diagnostic) — save as `[Project]_Revision_Report_[runlabel].md` at the run folder (the `revision_round` gate's `revision_report` artifact; the distinct name keeps it from colliding with the deadline-coaching `[Project]_Revision_Calendar_[runlabel].md`):
- Flags resolved: [list with verification notes]
- Flags still present: [list with updated evidence]
- New issues introduced: [list with locations]
- Ripple effects detected: [list with severity]
- Next priority: [single most important remaining issue]

**Lifecycle advance.** For each finding the round confirms **resolved** (the *Flags resolved* list — **not** *Flags still present*), mark it resolved in the Revision Report with an explicit marker `<!-- resolved: <id> -->`, then advance its **Finding Lifecycle ID** to `revised` (the third lifecycle state, `locked → delivered → revised`) by **one of two writers**, depending on whether the project is runner-governed:

- **Runner-governed project** (the sidecar carries an `execution.gate_events` log): clear the round through the gate — `scripts/validate.sh gate revision_round <run_folder>` then `scripts/validate.sh gate --attest revision_round <run_folder>`. The gate folds the resolved-marker ids into `execution.finding_states[<id>] = "revised"`. Writing the field by hand is **forbidden** for these projects — it would drift from the gate fold and fail `gate --check-state`'s `pointer == fold` invariant.
- **Non-runner-governed project** (no `gate_events`): write `execution.finding_states[<id>] = "revised"` **directly**, as before — there is no gate log to fold and no `pointer == fold` invariant, so the direct write is correct and remains the path for the common case.

A finding under *Flags still present* / *New issues introduced* is named (bare) but carries **no** resolved marker, so it correctly stays `delivered`. A finding that **regresses** in a later round is **not** demoted in place (`revised` is terminal per ledger id; the fold is forward-only) — re-diagnosis (the `revision_round` gate's `allowed_next` is `run_synthesis`) gives it a fresh `F-…` id. `scripts/validate.sh finding-trace <run_folder>` then audits completion by ID — a finding marked resolved but left below `revised` in the sidecar is W3 (advisory; ERROR under `--strict`), and a finding the report **mentions as unresolved** while the sidecar marks it `revised` is E5. See `docs/finding-lifecycle-ids.md` §Increment 3 and `docs/revision-round-gate.md`.

### Cross-Round Regression Check (on re-diagnosis)

When a revised draft is **re-diagnosed** into a new run folder (the `revision_round` gate's `allowed_next: run_synthesis` — a fresh ledger with renumbered `F-…` ids), run the cross-round regression diff before closing the round:

```
scripts/validate.sh regression-diff <prior_run_folder> <this_run_folder>
```

It heuristically matches this round's findings against the prior round's (same origin code + chapter token + ≥1 shared mechanism token — finding ids are per-run, so the match is a **candidate**, never an assertion) and surfaces two signals a single-round diagnosis structurally cannot: **W1 recurrence-candidate** — a finding the prior round marked `<!-- resolved: F-… -->` that re-appears, so the fix may not have held (it reverts to the prior round's severity once the editor confirms the match) — and **W2 new-in-quiet-chapter** — a finding in a chapter the prior round left quiet, i.e. candidate fix-induced breakage (clear a false positive with `<!-- override: regression-cleared <runlabel>:<chapter> — investigated, not fix-induced -->`). Both are advisory (re-diagnosing a *changed* manuscript legitimately drops, adds, and moves findings); `--strict` gates them at round close. Fold a confirmed recurrence into this round's ledger at the reverted severity, and record the regression candidates in the Revision Report (the validator prints to stdout — it writes no file). See `docs/draft-regression-testing.md`.

### When to Reset to Full Analysis

Abandon Revision Round Protocol and run fresh full analysis when:
- Structural changes exceed 40% of manuscript
- POV, tense, or timeline has changed
- Core contract has shifted
- Author reports "I basically rewrote it"
- Previous diagnostic is >6 months old
