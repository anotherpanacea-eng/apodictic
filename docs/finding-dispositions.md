# Spec 03 — Engine-level `declined`/`deferred` finding dispositions (apodictic)

**Status:** **Built** (this PR; spec-review pass 1 folded 2026-07-01, verdict BUILD-READY-WITH-FIXES, 0 P1; Opus build-review READY-TO-PR, 0 P1/P2, 3 P3s folded). Built in the `apodictic.finding_disposition.v1` schema + `_coverage.json` row, `apodictic_artifacts.py` (marker-grammar + `FID_RE` SSoT), `run_gate.py` (`disposition_deltas` freeze/fold/pointer/`check_state`), the new `disposition_check.py` validator + `validate.sh` dispatcher (+ root mirrors), `feedback_triage.py` W3, `structured_findings.py` (`severity_tally` factored shared), the §A–§D consumers, and the canonical fixture `references/example-run-folder-dispositions/` wired into `--check-all` (green). **Owner of the decision:** craft/editorial boundary.
<!-- built-when: scripts/disposition_check.py -->
**Provenance:** Fable pick #3. Sequenced directly after stub 01 (shared state-lifecycle surface;
the resume flow should display dispositions).
**Doc home at build time:** `docs/finding-dispositions.md` (this spec, updated with build-time corrections — the `docs/revision-round-gate.md` pattern).

**Build-time corrections (found while building — the `docs/revision-round-gate.md` pattern):**
- **The boundary-guarded id regex is `apodictic_artifacts.FID_RE`, single-sourced.** The spec's §C.1 grammar cited "the existing `finding_trace._ID_RE`"; as built, the compiled pattern is hosted in `apodictic_artifacts.py` as `FID_RE` (dependency direction: `finding_trace`/`regression_diff`/`disposition_check` all import `apodictic_artifacts`, never the reverse — the same rationale that homed the marker grammar there), and `finding_trace._ID_RE` / `regression_diff._ID_RE` are **re-pointed to that object** (each keeps a byte-equal literal only as its art-less degraded fallback). The `apodictic_artifacts --self-test` `fid_re_lockstep` case pins all three patterns equal so the fallbacks cannot drift.
- **Governed-detection is NON-EMPTY `gate_events`, not key presence.** The sidecar template ships `"gate_events": []`, so a presence check would read every fresh-from-template project as runner-governed and forbid the direct write everywhere. As built, `governed = bool(ex.get("gate_events"))` (`disposition_check.py`; the template `$comment` states the same rule).
- **Freeze-time marker filtering in `_disposition_deltas`.** A marker naming an off-ledger id, an id in the same clear's resolved subset (`exclude_ids` — the same-event launder), an id whose lifecycle state is not `delivered`, or a record failing validation is **skipped at freeze time** — never frozen into a poisoned append-only event. The skip surfaces as marker/sidecar lag via DP2.5; and because DP1's active set reads **markers ∪ records**, a skipped decline still forces the readiness caveat — filtering opens no laundering window.
- **Marker-home precedence, pinned:** triage artifacts → Coaching Log → revision report, a later home wins per id (and within a home the last marker wins) — the report is the round's freshest author decision. The spec named the homes but no order; the order is normative **where the record is frozen** (`_disposition_deltas`, the governed write path — its docstring states it). `disposition-check`'s own marker scan gathers all three homes but keys its checks on id sets (DP1/DP2.5) and the report home (DP2.1), so it takes no precedence dependency.
- **DP2.1 is report-scoped by design** (see the sentence added to §Mechanical guards DP2.1): both the resolved ids and the disposition markers DP2.1 compares are gathered from the run's completion artifacts (report home) only — a live contradiction whose marker homes in the Coaching Log or a triage artifact is deliberately out of scope, backstopped by `finding-trace` E5/W3 (completion-side consistency) and DP2.5 (marker/sidecar sync).
- **Two stale-claim doc reconciles beyond the touch list**, both in `docs/roundtrip-resume.md`: its `decision=declined` row note and its non-goals bullet each claimed "there is no engine-level declined finding state" / "a named future increment" — both now point here (the roundtrip row stays the per-round audit trail; its proposal column still never proposes `declined`/`deferred`).
- **Post-build hardening (2026-07-02, `docs/disposition-supersedence-recompute.md`):** the as-specced `active = finding_states[id] != "revised"` trusted a self-reported sidecar field — the PR #161 fabricated-budget class (one JSON edit waived the DP1 caveat, silenced DP2.5, and no validator on the enforcement path corroborated; finding-trace E5 is deliberately report-mention-scoped and `/ready` runs only `disposition-check` at verdict time). Supersedence is now recomputed from `<!-- resolved -->` markers in reachable completion artifacts (DP2.6; see the §Schema 2 amendment).

---

## Problem & verified evidence (anchors re-verified 2026-07-01)

- `plugins/apodictic/skills/revision-coach/SKILL.md:94` (stalled off-ramp, verbatim): *"(There is no engine-level "declined" finding state today; the Coaching Log note is the durable record.)"* — a deliberately-set-aside finding survives only as prose a later session must remember to read.
- **Anchor correction:** `plugins/apodictic/scripts/feedback_triage.py:249` is a **self-test comment** (`# resolved conflict: one side declined -> clean`), not the conflict-resolution logic. The real surfaces are: the `triage: "decline"` enum value in `schemas/apodictic.feedback_item.v1.schema.json` (enum `["act-now", "act-later", "monitor", "decline"]`), and the W1 conflict check at `feedback_triage.py:126-133`, which treats a conflict as resolved when one side's `triage` leaves `_ACTIONABLE = ("act-now", "act-later")` — i.e. `decline` resolves a conflict *inside the triage artifact* and flows nowhere else. No engine finding is ever marked.
- **The current finding-state enum, mapped from code (not docs):** `execution.finding_states` values are exactly `locked → delivered → revised` — `_PHASE_FINDING_STATE` / `_STATE_RANK` at `plugins/apodictic/scripts/run_gate.py:52-54`, enforced fold-side by `check_state` ("not a lifecycle state", `run_gate.py:659-661`) and artifact-side by `finding-trace` **E3** ("Every `finding_states` value ∈ `{locked, delivered, revised}`", `docs/finding-lifecycle-ids.md`). The fold is **forward-only monotonic** (`run_gate.py:334-336`; `revised` is terminal per ledger id — `docs/revision-round-gate.md` Blocker 2, normative).
- `plugins/apodictic/skills/core-editor/references/state-lifecycle.md:86` — Revision Round Intake asks *"Which flags were declined?"* and `:92` forbids re-flagging them — but both run on author memory + prose; nothing mechanical carries the answer between rounds. The `revision_round` gate's attestation `rev-a3` ("declined items are not silently re-flagged", `docs/revision-round-gate.md` §Build 1) attests to a record that doesn't exist.
- Consequence: to every mechanical consumer — `/ready`'s verdict (`references/submission-readiness.md`), the coach's Loop Dispatch ladder (`revision-coach/SKILL.md:88-97`), `finding-trace` W1 coverage, `regression-diff` — a *deliberately declined* Must-Fix is indistinguishable from an *unaddressed* one.

## Decision it changes

What the coach plans next session (stop re-offering a deliberate pass; resurface a deferral when its recorded trigger fires), and how a submission-readiness verdict treats declined-with-reason versus ignored findings.

---

## Design decision 0 — a disposition is an **overlay**, not a lifecycle state

The single load-bearing choice, made here so the build never faces it: `declined`/`deferred` do **not** extend the `finding_states` enum. They live in a **parallel sidecar map**, `execution.finding_dispositions`.

Why (all verified against code):
1. The `finding_states` fold is rank-monotonic and forward-only (`run_gate.py:334-336`). `deferred` is *re-openable by design* (a fired trigger resurfaces it; it later becomes `revised` or `declined`), so it cannot occupy a rank without breaking the monotonicity `check_state` and `docs/revision-round-gate.md` depend on.
2. A declined Must-Fix **remains** `delivered` in the lifecycle — that is the non-goal made structural: the finding's diagnostic truth (locked → delivered, never revised) is untouched; only the *author's decision about it* is recorded. `finding-trace` E3 and W1, `softness-check`, `deficit-lock`, `structured-findings`' severity tally, and `regression-diff` all keep their exact current semantics with **zero** relaxation — which is precisely the anti-laundering property (§Guards).
3. **Name collision, disambiguated now:** the gate engine already has a *phase-level* `deferred` (`gate --defer`, event `result: "deferred"`, `run_gate.py:22,56`). That defers a **gate**; this spec defers a **finding**. Everywhere in code and docs the new concept is a *finding disposition* (`finding_dispositions`, `disposition_deltas`, `disposition-check`) — never a bare "deferred state".

---

## Schema

### 1. Disposition record — new `schemas/apodictic.finding_disposition.v1.schema.json`

```json
{
  "$id": "apodictic.finding_disposition.v1",
  "type": "object",
  "required": ["schema", "id", "disposition", "reason", "source", "session", "ts"],
  "additionalProperties": false,
  "properties": {
    "schema":      {"const": "apodictic.finding_disposition.v1"},
    "id":          {"type": "string", "pattern": "^F-[A-Za-z0-9]+-[0-9]{2,}$"},
    "disposition": {"enum": ["declined", "deferred"]},
    "reason":      {"type": "string"},
    "source":      {"enum": ["author", "triage"]},
    "session":     {"type": "integer"},
    "ts":          {"type": "string"},
    "trigger":     {"type": "string"},
    "artifact":    {"type": "string"}
  }
}
```

- `trigger` is **required iff `disposition == "deferred"`** — the stdlib subset checker (`apodictic_artifacts.py`) can't express conditionals, so the conditional is enforced by the `disposition-check` validator (DP0 below), the same split as `gate_event`'s cross-field rules living in `check_state`.
- `reason` must be non-empty (DP0). `session` = sidecar `session_count` at write time. `artifact` = optional provenance (which file carried the marker).
- Register in `schemas/_coverage.json`: `{"schema": "apodictic.finding_disposition.v1", "validators": ["disposition-check"], "canonical_gate": "example-run-folder-dispositions", "closed_keys": true}` (fixture in §Fixtures; satisfies meta-linter M4 — a schema nothing consumes is an error).

### 2. Sidecar — `execution.finding_dispositions`

Map `F-id → apodictic.finding_disposition.v1 record` in `Diagnostic_State.meta.json`, sibling of `execution.finding_states`. Add to `references/diagnostic-state-meta-template.json` with a `$comment` stating the dual-writer rule and the supersedence rule (below). Absent map = valid older sidecar (the template's existing omit-to-stay-valid convention).

**Supersedence (normative; amended 2026-07-02):** `finding_states[id] == "revised"` supersedes any disposition for `id`. The record is *kept* (history), but every consumer checks `finding_states` first. There is no deletion channel — a disposition is superseded by `revised`, or overwritten by a newer disposition (last-write-wins per id), never removed. **Recompute amendment (`docs/disposition-supersedence-recompute.md`, the PR #161 recorded-field rule):** in `disposition-check`, a `revised` state supersedes **only when corroborated** by a `<!-- resolved: F-id -->` marker in a reachable completion artifact (run folder, project root, or `runs/*` archives); an uncorroborated `revised` leaves the disposition ACTIVE — DP1 still owes its caveat, DP2.5 still audits sync — and is surfaced as **DP2.6** (WARN; ERROR under `--strict`). The sidecar state is a claim to verify, never an input.

### 3. Durable markers — the canonical record (sibling of `<!-- resolved: F-… -->`)

Pinned grammar (the `<!-- finding: … -->` pinning precedent, `output-policy.md:142`):

```
<!-- declined: F-P5-01 — <one-line reason> -->
<!-- deferred: F-P5-01 until: <trigger> — <one-line reason> -->
```

- **One shared grammar helper (single SSoT):** the marker regex and parser live in `apodictic_artifacts.py` as `_DISPOSITION_RE` + `parse_disposition_markers()`, following the `finding_trace._RESOLVED_RE` family (`finding_trace.py:71`), and are imported by **both** `run_gate.py` and `disposition_check.py` — neither script defines a local copy. Host verified against both candidate modules: `run_gate.py` already imports `apodictic_artifacts` as `art` (`run_gate.py:42`) but keeps `finding_trace` a deliberately **lazy** import ("Lazy import keeps run_gate free of a hard finding_trace dependency" — comment at `run_gate.py:439-441`); hosting the grammar in `finding_trace` would force exactly the hard dependency that comment exists to avoid, so `apodictic_artifacts.py` (which already hosts shared regexes, e.g. `BLOCK_RE`) is the host. `apodictic_artifacts.py` is therefore in the PR touched-files and the dual-mirror list.
- Case-insensitive scan; no collision with `resolved:`/`override:`/`finding:` families (grepped: no existing `<!-- declined:`/`<!-- deferred:` markers in the repo; the one prose hit in `franklin-pathway.md` is not a marker).
- Code-span stripping in the scanner goes through the `override_marker` SSoT (`override_marker.strip_code_spans`, `override_marker.py:53`) — a local stripper violates meta-linter **M6** (`docs/validator-conventions.md`).
- **Marker homes** (determines `source`): the Coaching Log section of `Diagnostic_State.md` (coach off-ramp) and the Revision Report → `source: author`; triage-written markers home in the `*_Feedback_Triage_*.md` artifact **itself** → `source: triage`.

As with `revised` (`docs/project-addressability.md:138`), **the markers are the canonical source**; the sidecar map is the mechanical mirror. Consumers read the map when present and fall back to markers — the established Loop-Dispatch idiom (`revision-coach/SKILL.md:87`).

---

## The write path — same dual-writer gate as `revised` (named precisely)

Mirror `state-lifecycle.md:120-123` exactly:

- **Runner-governed project** (sidecar carries `execution.gate_events`): hand-writing fold-owned fields is forbidden (`pointer == fold`, `gate --check-state`). Dispositions ride the gate log: a **new event field `disposition_deltas`** (`{F-id: <full disposition record>}`), populated at append time by a `_disposition_deltas(phase, run_folder, …)` sibling of `_finding_deltas` (`run_gate.py:431`) — active for the `revision_round` phase only. At clear (`validate.sh gate revision_round <run_folder>` → `gate --attest`), it scans the disposition markers in: the gate's `revision_report` artifact, any `*_Feedback_Triage_*.md` in the run folder, and the project `Diagnostic_State.md` Coaching Log (reachable via the existing `_find_sidecar` walk-up, `run_gate.py:100`). **Builder note — anchor-verify before relying on this hop:** `_find_sidecar` walks up to `Diagnostic_State.meta.json` (the sidecar JSON), not the `.md`; the Coaching Log lives in the **sibling** `Diagnostic_State.md`, derived from the sidecar's dirname — verify that derivation at build time rather than assuming `_find_sidecar` locates the `.md` itself. The **full record** — reason, source (inferred from marker home), session (sidecar `session_count`), ts, trigger — is **frozen into the event**, so `fold_pointer` (extended to also derive `finding_dispositions`, last-event-wins) recomputes deterministically from the log alone; `pointer == fold` holds by construction. Sidecar lag between marker-write and next round-clear is acceptable — consumers fall back to markers (the `revised` idiom).
- **Non-governed project** (no `gate_events` — the common case): the coach / triage workflow writes `execution.finding_dispositions[id] = {record}` **directly**, alongside the marker, exactly as the direct `finding_states[...] = "revised"` write stands today. Before writing the sidecar, the direct writer validates the record via `art.validate_obj` against `apodictic.finding_disposition.v1` **plus** the trigger-iff-deferred conditional — the same record-shape gate the governed path gets from `check_state`.

**`check_state` additions** (`run_gate.py` §check_state, beside the `finding_deltas` block at `:655-661`):
- `disposition_deltas` only on a **clearing passed** (same rule as `finding_deltas`).
- Each record validates against `apodictic.finding_disposition.v1` via `art.validate_obj` + the trigger-iff-deferred conditional.
- **No simultaneous launder:** one event carrying both `finding_deltas[F-X] = "revised"` and `disposition_deltas[F-X]` is an ERROR (a finding cannot be revised and disclaimed by the same clear).
- Pointer write mirrors `finding_states` handling (`run_gate.py:383-398`): write `finding_dispositions` exactly as the fold computes it; clear it when the fold no longer supports it. Explicitly (option c, previously implied): a pointer/fold write **leaves superseded sidecar records untouched** — supersedence is a read-time precedence rule (`finding_states` checked first), never a write-time deletion or rewrite of the superseded record.
- `apodictic.gate_event.v1.schema.json`: declare `disposition_deltas: {"type": "object"}` (schema is `additionalProperties: true`, but declared-field + `$comment` is the house style) and extend the `$comment` cross-field list.

**Write preconditions (enforced at write time by both writers; audited by DP2):** a disposition may only be recorded for a finding whose lifecycle state is `delivered` (or `locked` on a non-governed project that never gated — degrade honestly). Declining a finding that was never delivered is synthesis-softening, not an author decision. A disposition on a `revised` id is a no-op-with-warning (supersedence). "Enforced at write time by both writers" covers **record shape as well as lifecycle preconditions**: both writers validate the full record (`art.validate_obj` + trigger-iff-deferred) before it lands — governed via `check_state`, non-governed via the direct-writer validation above.

---

## Consumers — per-surface behavior changes

### A. revision-coach Loop Dispatch (`plugins/apodictic/skills/revision-coach/SKILL.md`)

1. **Inputs line (`:85`):** add `execution.finding_dispositions` (+ the disposition markers as fallback) to the on-disk inputs.
2. **Ladder step 3 (`:92-94`):** the "delivered but not revised" selector **skips** ids with an active `declined` disposition; for `deferred` ids it first runs a **trigger review** — a trigger that parses as an ISO date (`YYYY-MM` / `YYYY-MM-DD`) fires mechanically when the date has passed; any other trigger text is a coach judgment call against the session context ("you deferred F-P5-03 until 'after the POV decision' — that decision is now recorded; resurface it?"). A fired deferral re-enters step 3 at normal leverage rank; an unfired one is skipped. New terminal clause: if **every** open Must-Fix is declined/deferred-unfired, fall through to step 4 (Should-Fix tier) with a one-line note naming the set-aside findings.
3. **Stalled off-ramp (`:94`):** replace the prose-only instruction and **delete the parenthetical** ("There is no engine-level 'declined' finding state today…"). New text: on "set it aside," record the disposition — write the pinned marker in the Coaching Log **and** (non-governed) the sidecar record directly / (governed) note it folds at the next `revision_round` clear. Offer `declined` vs `deferred`+trigger explicitly; never choose for the writer (Firewall: the dispatcher proposes, the writer disposes).
4. **Step 5 (`/ready` offer):** condition becomes "all findings `revised` **or actively dispositioned**, and `control_questions.open == 0`" — with the sentence "declined Must-Fixes will be listed, with reasons, in the readiness verdict; they are not absorbed."

### B. feedback_triage reconciliation (`plugins/apodictic/scripts/feedback_triage.py` + `docs/feedback-triage.md` + `commands/triage-feedback.md` workflow prose)

1. **Workflow prose:** when a feedback item is triaged `decline` **and** its `evidence_refs` cite a ledger `F-…` id (the existing cross-reference field), the triage step offers to record an engine disposition `{disposition: declined, source: triage, reason: <item claim + assessment>}` for that finding via the dual-writer path. The FB-item decline itself (external feedback about no engine finding) records nothing — dispositions attach to ledger findings only.
2. **Mechanical nudge — new check `W3 unreconciled decline` in `feedback_triage.py`:** an item with `triage == "decline"` whose `evidence_refs` contain an `F-…`-pattern token, with no matching disposition marker in the same artifact → WARN (ERROR under `--strict`), message "declined feedback maps to engine finding F-… but no disposition was recorded — the decline lives only in this artifact." Advisory severity follows the W1/W2 family convention. Self-test cases added (§Fixtures). **Ownership boundary (W3 vs DP2.2):** W3 is feedback-triage-artifact-scoped **advisory** — it never reads the sidecar; DP2.2 is sidecar-scoped **ledger-integrity** — it never reads triage artifacts. Cross-reference comments stating this boundary go in both `feedback_triage.py` (at W3) and `disposition_check.py` (at DP2.2).
3. `docs/feedback-triage.md`: document W3 + the reconciliation flow.

### C. `/ready` verdict visibility (`plugins/apodictic/skills/core-editor/references/submission-readiness.md`; `commands/ready.md` needs no change — it's a thin pointer to this reference)

1. **Output template (§Output Template, near `:159-172`):** after **Blind Spots**, add a pinned, mechanically-checkable caveat block, required whenever an active (non-superseded) declined/deferred Must-Fix exists:

   ```
   **Declined Must-Fixes:** F-P5-01 — <reason> (declined, session 12); …
   **Deferred Must-Fixes:** F-DP-02 — until: <trigger> — <reason>; …
   ```

   One line per family, every active id named. **Pinned caveat-line scan grammar (what DP1 parses):** a caveat line is a line matching `^\*\*(Declined|Deferred) Must-Fixes:\*\*` followed by `; `-separated `F-… — …` entries; ids are extracted from the line remainder with the boundary-guarded id regex `(?<![\w-])F-[A-Za-z0-9]+-[0-9]{2,}(?![\w-])` (`apodictic_artifacts.FID_RE` — the single compiled source as built; `finding_trace._ID_RE` and `regression_diff._ID_RE` re-point to it, lockstep-tested — same pattern as the schema's `id`), one capture per id. "Every active id named" is therefore a mechanical **id-set comparison** (active-disposition set ⊆ captured set), not a substring check. Should-Fix/Could-Fix dispositions appear in the Diagnostic Summary table, not the caveat block (the caveat is the Must-Fix teeth; lower tiers are informational).
   The `/ready` workflow runs `validate.sh disposition-check <sidecar> <assessment>` (DP1) **before** delivering the verdict; a DP1 ERROR blocks the verdict — DP1 only has teeth if it runs at verdict time, not just in CI `--check-all`.
2. **Ceiling rule (extend the existing "Confidence and ceiling rule", `:113`):** an active declined Must-Fix caps the verdict at `CONDITIONALLY VIABLE` unless the caveat line carries a per-id rationale for why submission is viable despite it — the exact structure of the existing blind-spot ceiling. A deferred Must-Fix whose trigger has fired is treated as open (no READY). This is an LLM-followed prose rule; the *presence* of the caveat is the mechanical part (DP1).
3. **Sidecar mirror:** no change to `readiness[]` — dispositions are already in the sidecar; duplicating them into readiness entries would create a second source of truth.

### D. Integration with spec 01 (roundtrip-resume) — sequencing dependency

Builds **after** spec 01: both touch the `/start` `revising` dispatch (`commands/start.md:50`) and `state-lifecycle.md`. The 01 resume surface gains one line: the resume summary displays active dispositions ("2 declined, 1 deferred — trigger 'beta reads back' not yet fired"), and 01's per-finding disposition-proposal step must **never** propose `declined`/`deferred` (those are author-initiated only; 01 proposes `resolved` candidates). If 03 somehow builds first, the display line degrades to nothing — but plan the order, don't rely on the degrade.

---

## Mechanical guards — new validator `disposition-check` (+ what existing gates deliberately ignore)

**One new validator, three named checks.** Python helper `scripts/disposition_check.py` (mirrored), dispatched as `validate.sh disposition-check <run_folder|sidecar> [readiness_assessment] [--strict]`. Python, not bash: it must parse JSON sidecar maps, ledger blocks via `apodictic_artifacts`, and cross-reference three artifact classes — well above the bash ceiling (the repo pattern: bash cases delegate anything beyond grep/awk-level checks to a Python sibling — `finding_trace`, `honesty_check`). **Degrade path:** without `python3`, WARN-advisory, never a false failure (the `finding-trace` precedent, `docs/finding-lifecycle-ids.md`).

- **DP0 — record shape.** Every `finding_dispositions` record validates against the schema; `trigger` present iff `deferred`; `reason` non-empty; `disposition` ∈ {declined, deferred}. ERROR.
- **DP1 — declined-Must-Fix caveat (the /ready teeth).** When a readiness assessment artifact is present (`Submission_Readiness_Assessment_*.md` glob) and an **active** declined/deferred Must-Fix exists (sidecar map or markers; active = not superseded, where supersedence requires `finding_states[id] == "revised"` **corroborated by a resolved marker** — the §Schema 2 recompute amendment, audited as DP2.6), the assessment must contain the pinned caveat line(s) naming **every** such id. Missing line, or a line missing an id → ERROR ("declined Must-Fix F-… absent from the readiness caveat — a verdict is absorbing a declined finding"). Presence check by the pinned caveat-line grammar in §C.1 (line-anchor regex + per-id `_ID_RE` capture → id-set comparison) — same family as `softness-check`'s marker discipline. No assessment artifact → the check is skipped with a note (never a false failure). Runs at verdict time via the `/ready` workflow (§C.1), not only in `--check-all`.
- **DP2 — no severity laundering / no deficit improvement.** Five sub-assertions:
  1. **Contradiction:** the same run's completion artifacts carry both `<!-- resolved: F-X -->` and an active declined/deferred marker for `F-X` → ERROR (each direction launders the other). DP2.1 gathers both sides from the completion artifacts (report home) **only, by design** — a live contradiction whose disposition marker homes in the Coaching Log or a triage artifact is deliberately out of scope, backstopped by `finding-trace` E5/W3 (completion-side consistency) and DP2.5 (marker/sidecar sync).
  2. **Phantom:** every `finding_dispositions` key resolves to a ledger `apodictic.finding.v1` id → ERROR otherwise (the `finding-trace` E2 pattern, applied to the new map). DP2.2 is sidecar-scoped ledger-integrity and never reads triage artifacts — the triage-artifact side belongs to W3 (§B.2; cross-reference comments in both scripts).
  3. **Severity immutability:** the record schema is closed-key with **no severity field** — a disposition structurally *cannot* carry a severity; DP2 additionally ERRORs if any dispositioned id's ledger block severity token differs from the severity recorded in the letter's Severity Calibration for that id (reuses the `softness-check` ID-match approach, read-only).
  4. **Tally guard:** recompute the ledger severity tally; ERROR if `triage_summary.<sev>` is **less than** the ledger count at that severity for any severity with a dispositioned finding — a disposition write that "improved" the deficit count. (Equality overall is `structured-findings`' job; DP2 owns only the disposition-shaped decrement.) DP2.4 must **reuse — or factor into a shared helper — the exact severity-count logic `structured_findings.py` uses** (the `validate_sidecar_obj` tally, `structured_findings.py:71`, counting at `:108-114`: severity keys seeded from `art.load_severity_values()`, mapped `Must-Fix/Should-Fix/Could-Fix → must_fix/should_fix/could_fix`), so the tally guard cannot drift from the tally it audits.
  5. **Bidirectional marker/sidecar sync (DP2.5):** every **active** declined/deferred marker in the three marker homes (Coaching Log, Revision Report, `*_Feedback_Triage_*.md`) has a matching `finding_dispositions` entry, **and** every active `finding_dispositions` entry has a matching marker in some home. WARN by default, ERROR under `--strict`; honors the acceptable-lag window for governed projects between marker-write and the next `revision_round` clear (§Write path) — a marker awaiting its fold is lag, not divergence.
- Governed projects get the same guarantees fold-side via the `check_state` additions (§Write path) — `disposition-check` is the artifact-side audit, `check_state` the log-side one, mirroring the `finding-trace` / `gate-state` ownership split.

**What deliberately does NOT change (the laundering firewall, stated normatively):** `softness-check`, `deficit-lock`, `severity-floor`, `structured-findings`, `finding-trace` E1–E3/W1, and `regression-diff` read dispositions **nowhere**. A disposition is not an override marker (`<!-- override: softness-downgrade … -->` remains the only severity-relief channel, ID-scoped, per `output-policy.md:140`), grants no relief in any honesty gate, and never decrements a count. The only surfaces that *read* dispositions are the three consumers above plus `disposition-check` itself. The `revision_round` constraint "don't re-flag declined" (`state-lifecycle.md:92`) is applied by the *round workflow* when composing the report — `regression-diff` stays evidence-only.

**Registration (repo norms, all mandatory):**
- `validate.sh`: new `disposition-check)` dispatcher case handling `--self-test`; append to the `Commands:` usage line (`validate.sh:231`); append to `AGG_VALIDATORS` (`validate.sh:181`) — the count is **derived** (`AGG_COUNT`), never hand-bumped (meta-linter M3); wire the canonical fixture into `--check-all`.
- **Dual script mirror:** every touched script (`disposition_check.py` new, `apodictic_artifacts.py` — the `_DISPOSITION_RE`/`parse_disposition_markers()` host, `run_gate.py`, `feedback_triage.py`, `validate.sh`) is copied by hand `plugins/apodictic/scripts/` → `scripts/`, byte-identical, verified by `validate.sh check-mirror` (CI runs the root copy — `AGENTS.md` §Platform parity).
- Meta-linter compliance by construction: M1 (self-test case), M2 (classify on parsed blocks via `art.parse_blocks`/`_has_block`, never a raw `apodictic:` substring), M4 (schema consumed + `_coverage.json` row), M5/M6 (no bare override scans; reuse `override_marker` helpers if stripping).

---

## State gardening (`state-lifecycle.md` §State Gardening)

- **Active dispositions are load-bearing state — never archived.** A declined finding's marker + reason line stays in the active state file (it is what prevents re-flagging; same class as the always-active Author Decisions section, `state-lifecycle.md:58`). Coaching Log entries remain append-only and uncompressed (existing rule, `:59` — the markers ride along for free).
- **Superseded dispositions compress like resolved handoffs** (`:34-38`): when `finding_states[id]` reaches `revised`, gardening replaces the disposition's state-file presence with the one-line archive form:
  ```markdown
  - F-P5-01: declined session 12, later revised session 15. Full record: Diagnostic_State_Archive_[datetime].md
  ```
  The sidecar record is untouched (JSON is not gardened; supersedence already handles precedence).
- "What Gardening Preserves" gains one bullet (active dispositions); "What Gardening Compresses" gains one bullet (superseded dispositions).
- **Gardening self-test coverage:** a `disposition_check.py --self-test` case exercises a post-gardening state file that still carries **active** disposition markers — the scanner must still find them (preservation is load-bearing), and a superseded disposition compressed to the one-line archive form must **not** parse as an active marker (§Fixtures).

---

## Fixtures & self-test plan

1. **`run_gate.py --self-test` — additive only** (the 4a lesson: never edit existing cases): (a) a `revision_round` clear with a declined marker in the revision report folds the full record into `finding_dispositions`, `pointer == fold`; (b) last-write-wins — `deferred` then `declined` for one id across two clears; (c) supersedence — `revised` delta lands, disposition record retained, pointer unchanged in `finding_states` semantics; (d) `disposition_deltas` on a non-clearing event → `check_state` ERROR; (e) same-event `revised` + disposition for one id → ERROR; (f) malformed record (missing trigger on deferred) → ERROR; (g) marker in a Feedback Triage artifact folds with `source: triage`.
2. **`disposition_check.py --self-test`:** DP0 (bad enum / empty reason / missing trigger), DP1 (caveat present / absent / missing one id / no-assessment skip / superseded-id exempt), DP2 (resolved+declined contradiction, phantom id, tally decrement, severity mismatch; DP2.5: marker-without-record, record-without-marker, `--strict` escalation, governed-lag exemption), gardening (active markers in a gardened state file still found; compressed archive line not parsed as active), python3-degrade path exercised via the bash case.
3. **`feedback_triage.py --self-test`:** W3 fires (decline + `F-…` evidence_ref, no marker), W3 clean (marker present; or no `F-…` ref), `--strict` gating.
4. **New canonical fixture `references/example-run-folder-dispositions/`** — a **non-governed** sidecar (no `gate_events` — deliberately avoids the coupled pointer/event/artifact edits that make the governed `example-run-folder` fragile, per `docs/revision-round-gate.md` §6), a small ledger, a Coaching Log excerpt with one declined + one deferred marker, and a readiness-assessment excerpt carrying the pinned caveat. Wired into `--check-all` as `disposition-check`'s real-file invariant and named as the schema's `canonical_gate`. The committed governed fixture is left untouched; governed-path coverage lives in the `run_gate` self-tests (the 4a build-time correction, reused).
5. `bash scripts/validate.sh --check-all` green is the exit gate for every session (run the root copy — what CI runs).

---

## Non-goals

- **No auto-declining, ever.** Disposition is an author decision the engine records. Spec 01's resume flow proposes `resolved` candidates only; nothing machine-proposes `declined`/`deferred` (Firewall: `references/firewall.md` — the system diagnoses and records; it does not decide for the writer).
- **Not a severity change.** A declined Must-Fix remains a Must-Fix that was declined — structurally guaranteed (no severity field in the record; DP2.3/DP2.4; no honesty-gate relief).
- **No new lifecycle state** — `finding_states` enum, `_STATE_RANK`, finding-trace E3, and fold monotonicity are untouched.
- No periodic "revisit your declines" review ritual (a future coach mode, if ever; /ready's caveat is the standing visibility).
- No mechanical trigger DSL beyond the ISO-date fast path; trigger text is coach-judged in M1.

## Failure modes if built badly

- **Severity laundering (the headline).** Declining a Must-Fix quietly improves the readiness verdict — one click to make the letter agree with the author. Teeth: DP1 (caveat forced, per-id), DP2 (contradiction/phantom/tally/severity), the ceiling rule, the no-relief rule in every honesty gate, and the same-event launder check in `check_state`. **All guards land in the same PR as the state — the map never exists without its validator.**
- **Fold drift.** A governed project's dispositions written by hand → `pointer == fold` breaks silently if the pointer-write path isn't extended symmetrically (`run_gate.py:383-398`). Covered by self-test (a) and `check_state`.
- **Deferral black hole.** A deferred finding whose trigger never gets reviewed is a decline with extra steps. Covered by the ladder's trigger review at every dispatch + the fired-trigger = open rule in `/ready`.
- **Marker/sidecar divergence.** Non-governed direct writes without the marker (or vice versa) split the record. Covered by the write-path instruction (always both), DP2.2's phantom check, and DP2.5's bidirectional sync audit (WARN, `--strict` ERROR, governed-lag exempt); residual divergence surfaces as the consumers' marker-fallback disagreeing — acceptable advisory-level exposure, same as today's `revised` dual-source.

## Build increments & PR shape

**One PR, after the spec-01 build merges** (shared touch surface: `start.md` `revising` dispatch, `state-lifecycle.md`; 01's resume summary displays dispositions).

- **Session 1 — engine + guards:** schema + `_coverage.json`; sidecar template; `apodictic_artifacts.py` (`_DISPOSITION_RE` + `parse_disposition_markers()` — the shared marker-grammar SSoT); `run_gate.py` (`_disposition_deltas`, fold, pointer write, `check_state`) + self-tests; `disposition_check.py` + dispatcher case + `AGG_VALIDATORS`; `feedback_triage.py` W3; mirror `cp` + `check-mirror`; `--check-all` green.
- **Session 2 — consumers + fixtures + docs:** `revision-coach/SKILL.md` (inputs, ladder, off-ramp rewrite); `state-lifecycle.md` (§Finding Dispositions, intake/constraint rewiring to the engine record, gardening bullets); `submission-readiness.md` (caveat block + ceiling rule); `docs/feedback-triage.md`; canonical fixture + `--check-all` wiring; `docs/finding-dispositions.md` (this spec, as built); reconcile `docs/project-addressability.md:138` + `docs/finding-lifecycle-ids.md` (dispositions ≠ lifecycle states; E3 unchanged) + `docs/runner-governed-execution.md` (`disposition_deltas`); changelog fragment (`changelog.d/`).

Codex gate applies (authored logic). Merge via merge commit.

## Open questions (operator calls)

1. **Confidence interaction:** should an active declined Must-Fix also cap **Confidence** at `MEDIUM` (as unresolved blind spots do, `submission-readiness.md:113`), or does the verdict ceiling + caveat suffice? **Operator call (default folded 2026-07-01): verdict ceiling suffices, no confidence cap; override before build if disagreed** — a declined finding is *more* legible than a blind spot, not less.
