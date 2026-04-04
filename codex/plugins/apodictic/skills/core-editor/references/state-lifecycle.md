# State Lifecycle & Revision Rounds

*Reference file for the APODICTIC Development Editor. Loaded by `apodictic-start` (resume gate), `apodictic-coach` (revision coaching), and revision round workflows.*
*See also: `handoff-protocol.md` for scene-level execution mode transitions.*

---

## State Gardening Protocol

Over multiple revision rounds, `Diagnostic_State.md` accumulates session history, handoff history, coaching log entries, and resolved material. Unchecked growth crowds active context and makes the resume gate slower. State gardening prevents this entropy.

### Trigger

State gardening runs at the resume gate in `apodictic-start`. The trigger is the `state_lines` field in `Diagnostic_State.meta.json` (updated by `scripts/validate.sh state-lines`).

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

**Revision Report** (not full diagnostic):
- Flags resolved: [list with verification notes]
- Flags still present: [list with updated evidence]
- New issues introduced: [list with locations]
- Ripple effects detected: [list with severity]
- Next priority: [single most important remaining issue]

### When to Reset to Full Analysis

Abandon Revision Round Protocol and run fresh full analysis when:
- Structural changes exceed 40% of manuscript
- POV, tense, or timeline has changed
- Core contract has shifted
- Author reports "I basically rewrote it"
- Previous diagnostic is >6 months old
