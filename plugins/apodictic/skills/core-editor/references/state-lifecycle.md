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
- **Active finding dispositions** — the declined/deferred markers and their reason lines (§Finding Dispositions): load-bearing state, never archived — they are what prevents re-flagging (same class as the Author Decisions section)
- All coaching log entries (append-only, not compressed — the revision coach depends on the full log; the disposition markers ride along)
- The current Mode section

### What Gardening Compresses

- Completed session history → one-line summaries with archive pointers
- Resolved handoff history → one-line summaries with archive pointers
- Answered control questions → question + answer only (rationale archived)
- Completed revision steps → checkbox + session reference
- **Superseded finding dispositions** (the id has reached `revised`) → the one-line archive form, like resolved handoffs:
  ```markdown
  - F-P5-01: declined session 12, later revised session 15. Full record: Diagnostic_State_Archive_[datetime].md
  ```
  Active dispositions are never compressed (see Preserves above). The sidecar record is untouched — JSON is not gardened; supersedence already handles precedence.
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
3. **Which flags were declined or deferred?** — Read the engine record first: `execution.finding_dispositions` + the pinned disposition markers (§Finding Dispositions below) carry the prior rounds' set-aside decisions with reasons and triggers. Ask the author only about gaps (a set-aside they mention that was never recorded), and record any new answer as a disposition, not a prose-only note
4. **New concerns?** — What does the author now suspect isn't working?

### Revision Round Constraints

**DO NOT:**
- Re-flag issues the author explicitly declined to address (respect their choices — the declined set is the engine record, `execution.finding_dispositions` + its markers, §Finding Dispositions below; this constraint is applied by the round *workflow* when composing the report — `regression-diff` stays evidence-only)
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

### Finding Dispositions (`declined` / `deferred`) — the engine-level set-aside record

A finding the author deliberately sets aside is recorded as a **finding disposition** (`docs/finding-dispositions.md`) — an **overlay** on the lifecycle, never a fourth lifecycle state: `execution.finding_states` stays exactly `locked → delivered → revised`, and the disposition lives beside it in `execution.finding_dispositions` (a map `F-id → apodictic.finding_disposition.v1` record). A declined Must-Fix **remains** `delivered` — the diagnostic truth is untouched; only the author's decision about it is recorded.

**Durable markers (the canonical source; pinned grammar, sibling of `<!-- resolved: F-… -->`):**

```
<!-- declined: F-P5-01 — <one-line reason> -->
<!-- deferred: F-P5-01 until: <trigger> — <one-line reason> -->
```

Marker homes (the home determines the record's `source`): the Coaching Log section of `Diagnostic_State.md` and the Revision Report → `source: author`; a triage-written marker homes in the `*_Feedback_Triage_*.md` artifact itself → `source: triage`. As with `revised`, the markers are canonical and the sidecar map is the mechanical mirror — consumers read the map when present and fall back to the markers.

**Two writers — the same dual-writer rule as `revised` above, exactly:**

- **Runner-governed project** (the sidecar carries `execution.gate_events`): hand-writing the fold-owned map is **forbidden**. Dispositions ride the gate log — the `revision_round` clear scans the run's disposition markers (Revision Report, `*_Feedback_Triage_*.md`, the project Coaching Log) and freezes each **full record** (reason, source, session, ts, trigger) into the clearing event's `disposition_deltas`, so `execution.finding_dispositions` is fold-derived (last-event-wins per id) and `pointer == fold` holds by construction. Sidecar lag between a marker write and the next round clear is acceptable — consumers fall back to the markers.
- **Non-governed project** (no `gate_events` — the common case): the coach / triage workflow writes `execution.finding_dispositions[<id>] = {record}` **directly**, alongside the marker, exactly as the direct `finding_states[<id>] = "revised"` write works. **Validate before writing:** the record must satisfy `apodictic.finding_disposition.v1` (closed-key) **plus** the trigger-iff-deferred conditional and a non-empty reason — the same record-shape gate the governed path gets from `gate --check-state`.

**Write preconditions (both writers):** a disposition may only be recorded for a finding whose lifecycle state is `delivered` (or `locked` on a non-governed project that never gated — degrade honestly). Declining a finding that was never delivered is synthesis-softening, not an author decision. A disposition on a `revised` id is a no-op-with-warning (supersedence). **Never machine-proposed:** a disposition is an author decision the engine records — nothing auto-declines or auto-defers (the Firewall; the round-trip resume proposes `resolved` candidates only).

**Supersedence (normative):** `finding_states[<id>] == "revised"` supersedes any disposition for that id. The record is **kept** (history); every consumer checks `finding_states` first. There is no deletion channel — a disposition is superseded by `revised` or overwritten by a newer disposition (last-write-wins per id), never removed.

**What reads dispositions:** the coach's Loop Dispatch (skip declined / trigger-review deferred; `revision-coach/SKILL.md`), Revision Round Intake (above), `/ready`'s verdict caveat (`submission-readiness.md`), and the `disposition-check` validator (`scripts/validate.sh disposition-check <run_folder|sidecar> [assessment] [--strict]` — DP0 record shape, DP1 the declined/deferred-Must-Fix readiness caveat, DP2 no-laundering incl. the bidirectional marker/sidecar sync). **What deliberately does not:** every honesty gate — `softness-check`, `deficit-lock`, `severity-floor`, `structured-findings`, `finding-trace` E1–E3/W1, `regression-diff` — reads dispositions **nowhere**. A disposition is not an override marker (`<!-- override: softness-downgrade … -->` remains the only severity-relief channel), grants no relief in any honesty gate, and never decrements a count.

### Cross-Round Regression Check (on re-diagnosis)

When a revised draft is **re-diagnosed** into a new run folder (the `revision_round` gate's `allowed_next: run_synthesis` — a fresh ledger with renumbered `F-…` ids), run the cross-round regression diff before closing the round:

```
scripts/validate.sh regression-diff <prior_run_folder> <this_run_folder>
```

It heuristically matches this round's findings against the prior round's (same origin code + chapter token + ≥1 shared mechanism token — finding ids are per-run, so the match is a **candidate**, never an assertion) and surfaces two signals a single-round diagnosis structurally cannot: **W1 recurrence-candidate** — a finding the prior round marked `<!-- resolved: F-… -->` that re-appears, so the fix may not have held (it reverts to the prior round's severity once the editor confirms the match) — and **W2 new-in-quiet-chapter** — a finding in a chapter the prior round left quiet, i.e. candidate fix-induced breakage (clear a false positive with `<!-- override: regression-cleared <runlabel>:<chapter> — investigated, not fix-induced -->`). Both are advisory (re-diagnosing a *changed* manuscript legitimately drops, adds, and moves findings); `--strict` gates them at round close. Fold a confirmed recurrence into this round's ledger at the reverted severity, and record the regression candidates in the Revision Report (the validator prints to stdout — it writes no file). See `docs/draft-regression-testing.md`.

### Round-Trip Re-Anchoring (carry last round's margin notes onto the revised draft)

`regression-diff` works at the **finding** level. The complementary move at the **anchor/text** level — when the prior round produced an annotated copy (`*_Annotated_Manuscript_*` + its `*_Annotation_Manifest_*`, the Annotated-Manuscript deliverable) — is to **carry those margin notes onto the revised draft** *before* a re-diagnosis exists, so the writer opens their new draft already marked with which of last round's notes still apply, which moved, and which point at prose that's now gone. This is the round-trip the deliverable's one-run snapshot otherwise can't do; it makes the annotated copy revision-aware. Run it at **Revision Round Intake** (it needs only the prior run's manifest + the new draft — no new ledger), then cross-reference it against the regression diff at round-close. `/start` now surfaces this flow as the **round-trip resume offer** at the bound-project `revising` and `diagnosed` nodes (`commands/start.md` — the conditional-offer note; eligibility is the prior-manifest glob + `python3`, no new `next_action`).

**The flow (four steps; pure projection — the model never re-authors a comment, and it proposes; the operator disposes):**

1. **Snapshot the revised draft** into the new run folder as `[Project]_Manuscript_Snapshot_[runlabel].md` — line endings → LF, a trailing newline ensured, no other change (the same intake-snapshot discipline as a fresh run; see `run-core.md` §Intake). This frozen copy is the line index the re-anchor resolves against.

2. **Classify, then emit the revision-aware marked-up copy.** First inspect the classification:

   ```
   scripts/validate.sh reanchor <prior_run_folder> <new_snapshot>
   ```

   It partitions every prior-round annotation into **held** (same locus), **moved** (`quote` only — verbatim+unique at a new offset), **vanished** (prose gone — a candidate the finding was addressed), **ambiguous** (now duplicated — re-anchor refused), and **not-re-anchorable** (`line-range` — bare line numbers carry no text to find). RA1–RA3 (the mechanical re-anchor contract) are hard; the `vanished` (W1) and `ambiguous`/`not-re-anchorable` (W2) signals are advisory. Then **emit** the artifacts — the re-anchored manifest plus the rendered annotated copy of the *revised* draft, held/moved only (each comment carried **byte-identical** from the prior manifest — relocate, never re-author):

   ```
   scripts/reanchor.py emit <prior_run_folder> <new_snapshot> [-o <run_folder>]
   ```

   It writes `[Project]_Reanchored_Manifest_[runlabel].md` + `[Project]_Reanchored_Annotated_Manuscript_[runlabel].md` (the `Reanchored_` infix keeps them distinct from a fresh-diagnosis `_Annotation_Manifest_` / `_Annotated_Manuscript_`, so a carried-over copy is never mistaken for a re-diagnosed one). `emit` **re-gates RA1–RA3 before writing** — it refuses to write an unverified re-anchor. The `vanished` / `ambiguous` / `not-re-anchorable` notes are **not** silently dropped: they stay in the `reanchor` report for editor placement (RA3 guarantees none is lost). On a host without `python3`, run `reanchor` for the classification and place the surviving notes by hand from the prior manifest — never re-author a comment to fit the new prose.

3. **Cross-reference anchor evidence against the regression diff (round-close).** Once the revised draft *is* re-diagnosed into the new run folder (so a fresh ledger exists), join the two diffs by `finding_id` — the only key they share:

   ```
   scripts/reanchor.py crossref <prior_run_folder> <new_snapshot> <this_run_folder>
   ```

   It corroborates the heuristic regression signal with anchor ground truth: a **vanished** anchor on a finding `regression-diff` classes **resolved-and-held** is two-source evidence the fix landed; a **held/moved** anchor (prose persists verbatim) on a **recurrence-candidate** is evidence the fix did *not* hold (the `crossref:contradicted-resolution` / `X1` signal — advisory, ERROR under `--strict`). Record the corroborations in the Revision Report beside the regression candidates. The validators stay strictly within their own evidence (anchor-level vs. finding-level); this join is the **orchestrator's** job by design (`docs/annotated-manuscript-reanchoring.md` §Q2), which is why it lives here in the round flow, not inside either validator.

4. **Disposition & round-close.** Present a **per-finding disposition table**: each prior-round finding with its anchor class, its regression class when a crossref join matched it (`none` otherwise — a carry-only round has no ledger yet and records at most `needs-placement` triage), and a **proposed** disposition. A `vanished` anchor or a `resolved-and-held` class is evidence *presented*, never a resolution *asserted* — the model proposes; the operator confirms or overrides **each row**. The record is orchestrator-written into the **new** run folder as `[Project]_Roundtrip_Disposition_[runlabel].md` (marker-based — the human table is presentation; the HTML-comment rows are the machine record):

   ```
   <!-- disposition: <finding_id> anchor=<held|moved|vanished|ambiguous|not-re-anchorable> regression=<persisted|resolved-and-held|recurrence-candidate|unexplained-drop|new|new-in-quiet-chapter|none> decision=<confirm-resolved|keep-open|needs-placement|declined|pending> -->
   ```

   The `compares: <prior runlabel> → <this runlabel>` header is **derived from the input paths, never hand-typed** (the validator recomputes it). **The confirmation token is hard-sequenced:** write `<!-- disposition-confirmed: operator <ISO-8601, minutes, hyphenated> -->` (e.g. `operator 2026-07-01T14-30`) **only after every row has been presented to the operator and confirmed — never alongside the table, never before it, never on a partially reviewed table.** This is a sequencing rule, not a soft checkpoint: no decision other than `pending` may exist on the record without the token (RT2). Then write `<!-- resolved: <id> -->` markers into the Revision Report **for `confirm-resolved` rows only** — a resolved marker for any other row is the vanished-anchor auto-close the gate exists to prevent (RT3) — and gate the record:

   ```
   scripts/validate.sh roundtrip-disposition <prior_run_folder> <new_snapshot> <this_run_folder>
   ```

   RT1 recompute alignment / RT2 confirmation record present / RT3 confirmed-writes-only are hard; RT4 partition coverage (every recomputed prior finding must have a disposition row — a missing row is a finding silently omitted from round-close review, named by id) and W1 (rows still `pending`, or `confirm-resolved` rows not yet reflected as markers — work legitimately stages across sessions) are advisory, ERROR under `--strict` at round close. Lifecycle advancement then goes through the **existing two writers unchanged** (§Revision Round Output above): the `revision_round` gate (`gate` → `gate --attest`, where the operator personally attests **rev-a4** — every disposition was confirmed, no vanished-anchor auto-close) for runner-governed projects, the scoped direct `finding_states[<id>] = "revised"` write for non-governed. This step adds **no third writer** — only a confirmation precondition upstream of both. **The model's proposed disposition is never `declined` (or a deferral)** — proposals draw on `confirm-resolved` / `keep-open` / `needs-placement` / `pending` only; `decision=declined` is an operator choice (author-initiated, the Firewall). When the operator chooses it, record the durable **engine disposition** (§Finding Dispositions above — the pinned marker + the dual-writer record); the roundtrip row is the per-round audit trail, the finding disposition is the cross-round record the coach and `/ready` read. `revised` stays terminal-per-id — a regressed finding gets a fresh id via re-diagnosis, never a demotion.

A `--check-all` chain gate (`round-trip glue chain`) exercises emit → A-gate the emitted copy → crossref end-to-end on the canonical fixture, and a sibling step gates the canonical disposition record (RT1–RT4, plus hostile token-stripped / unconfirmed-marker / omitted-row arms), so the flow is proven to compose, not just the individual validators. See `docs/annotated-manuscript-reanchoring.md`.

### When to Reset to Full Analysis

Abandon Revision Round Protocol and run fresh full analysis when:
- Structural changes exceed 40% of manuscript
- POV, tense, or timeline has changed
- Core contract has shifted
- Author reports "I basically rewrote it"
- Previous diagnostic is >6 months old
