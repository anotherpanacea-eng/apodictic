# Finding Lifecycle IDs — cross-artifact trace

**Status:** Increments 1–3 **built**. Roadmap: `ROADMAP.md` → Harness Engineering → Finding Lifecycle IDs. Implementation: `scripts/finding_trace.py`, `validate.sh finding-trace` (+ canonical `--check-all` gate).

Every material finding already carries a durable **Finding Lifecycle ID** — `apodictic.finding.v1.id`, pattern `F-<ORIGIN>-<NN>` (e.g. `F-P5-01`, `F-DP-02`), described in the schema's `$comment` as following the finding *pass → ledger → Deficit Lock → editorial letter → revision/coaching*. The ID exists; this track makes the **lifecycle itself auditable by ID** instead of prose matching.

## What already exists (and what owns what)

The ID is not new, and several validators already key on it. The point of this increment is to fill the *un-owned* gap without duplicating them:

| Validator | Owns (by ID) |
|---|---|
| `structured-findings` | **Intra-ledger ID hygiene** — every `apodictic.finding.v1` block has a well-formed, unique `id` (pattern + per-run uniqueness). |
| `softness-check` | **Severity fidelity (forward)** — for each *locked* ledger finding, its delivery in the letter: downgrade, *buried* (absent from body), *dropped* (absent from both), read by exact ID + `apodictic.severity_calibration.v1` blocks. |
| `deficit-lock` | **Lock completeness** — every synthesis-bound finding was locked at Triage. |
| (none) | **Cross-artifact referential integrity + sidecar lifecycle coherence** ← *this increment*. |

ID citation surfaces in the artifacts (already conventional):
- **Ledger:** `apodictic.finding.v1` blocks carry `id`.
- **Letter:** `<!-- finding: F-XX-NN -->` HTML comments near the delivered finding, and `apodictic.severity_calibration.v1` blocks (`id` field) in the Severity Calibration appendix. IDs never appear in author-facing prose.
- **Sidecar:** `execution.finding_states` is a map `id → lifecycle state` (`locked` / `delivered` / `revised`), advanced forward-only by the execution gate (Runner-Governed Execution increment 3).

## The gap this increment fills

`softness-check` traces *ledger → letter* and judges severity. Nothing traces the **reverse and orthogonal** directions:

1. **Dangling references.** A letter HTML comment or a `severity_calibration` block (or a revision artifact) that cites an `F-…` ID **not present in the ledger** — a typo or a phantom calibration entry — passes every current check. `softness-check` iterates *locked* findings forward; it never asks "does every *cited* ID resolve to a real finding?"
2. **Phantom / incoherent sidecar state.** `execution.finding_states` can carry an ID that isn't in the ledger, or a non-lifecycle state value, with nothing to catch it. Nothing checks the sidecar's ID-keyed lifecycle against the ledger at all.
3. **No single lifecycle view.** There is no artifact-spanning report of *where each ID is* (ledger severity → sidecar state → cited in letter?).

## The `finding-trace` validator (Increment 1)

`validate.sh finding-trace <run_folder>` (or explicit files). Resolves the ledger, the editorial letter, and the sidecar from a run folder (graceful — each is optional; a missing artifact skips its dimension with a note, never a false failure). Backed by `scripts/finding_trace.py`, reusing `apodictic_artifacts.parse_blocks` for the embedded blocks. Degrades to an advisory `WARN` without `python3`.

**Inventory.** Parse the ledger's `apodictic.finding.v1` blocks → `{id: severity}`. This is the **authoritative ID set** for the run.

**Checks:**

| ID | Severity | Rule |
|---|---|---|
| **E1 — dangling reference** | ERROR | Every `F-…` ID *cited* in the letter (HTML `<!-- finding: … -->` comments **and** `apodictic.severity_calibration.v1` block `id`s) must resolve to a ledger ID. A citation to an unknown ID is a broken trace. |
| **E2 — phantom sidecar state** | ERROR | Every key of `execution.finding_states` must be a ledger ID. |
| **E3 — invalid sidecar state** | ERROR | Every `finding_states` value ∈ `{locked, delivered, revised}`. |
| **W1 — lifecycle coverage** | WARN (ERROR under `--strict`) | Once the run has cleared synthesis (sidecar `execution.phase` ⊇ `run_synthesis`, i.e. findings are locked), every Must-Fix / Should-Fix ledger ID should have a `finding_states` entry. Advisory because the sidecar may legitimately lag mid-run. |

**Report.** One trace line per ledger ID — `severity · sidecar state · cited-in-letter?` — so a human (or `/start`) sees each finding's journey at a glance. Exit `0` clean / WARN-only, `1` on any ERROR (or WARN under `--strict`), `2` usage.

**Explicitly not duplicated:** forward severity fidelity (downgrade/buried/dropped) stays `softness-check`'s; intra-ledger ID uniqueness/format stays `structured-findings`'. `finding-trace` is referential integrity + sidecar coherence only — a thin, orthogonal layer.

## Ownership boundary check (why this is additive, not overlapping)

- A finding **softened** in the letter → `softness-check` ERROR; `finding-trace` is silent (severity isn't its job).
- A finding **omitted** from the letter → `softness-check` ERROR (buried/dropped); `finding-trace` W1 only flags the *sidecar* coverage, not the letter (no double-judgement of omission).
- A letter citing a **typo'd / phantom** ID → **only `finding-trace`** (E1) catches it.
- A sidecar `finding_states` key with **no ledger finding** → **only `finding-trace`** (E2).

So every `finding-trace` ERROR is a class no other validator raises.

## Degrade path

Without `python3`: `finding-trace` prints an advisory `WARN` and the model performs the trace inline (the rules above are simple set-membership checks). Mirrors the established degrade pattern of the other Python-backed arms.

## Build plan (this increment)

1. `scripts/finding_trace.py` — inventory + E1–E3 + W1 + report + `--self-test`; reuse `apodictic_artifacts`.
2. `validate.sh finding-trace` arm (run-folder or explicit files; `--strict`); register in `--self-test-all` (**17 → 18**; bump count strings + usage + docblock in lockstep).
3. Self-test fixtures: clean trace; dangling letter ref (E1); phantom sidecar state (E2); invalid state (E3); coverage gap pre- vs post-synthesis (W1 advisory vs `--strict`); ledger-only run (graceful skips).
4. Light prose pointer: the `finding-trace` arm in `findings-ledger-format.md` §Finding Lifecycle ID (the citation convention already documented there).
5. Regenerate `codex/` + `antigravity/` mirrors; sync root `scripts/`; `--check-all`, `build-*.mjs --check`, `release-verify`.

## Increment 2 — revision follow-through + canonical release-gate (built)

Two additions, both extending `finding-trace` — no new validator, no count change (stays 19/19).

**A. Revision-plan / coaching follow-through.** `finding-trace` now also traces finding IDs into revision artifacts (`*_Session_Plan_*.md`, `*_Revision_*.md`) — the lifecycle stage after the letter. Unlike the letter (where IDs live only in HTML comments to keep author-facing prose clean), revision plans are working documents, so IDs are matched **anywhere** in the text (inline prose references count). Two checks:
- **E4 dangling revision reference** (ERROR) — a revision artifact cites an `F-…` ID not in the ledger.
- **W2 follow-through coverage** (advisory; ERROR under `--strict`) — a **Must-Fix** ledger finding not referenced in any revision plan, when a revision plan is present. The "did the revision plan actually pick up the must-fix findings" audit. Advisory by default because an author may legitimately stage must-fix work across sessions; `--strict` makes it a CI gate. Skipped entirely when no revision artifact is present.

**B. Canonical `--check-all` release gate — both directions.** Ships a canonical ledger (`core-editor/references/example-findings-ledger.md`) paired with the existing `example-editorial-letter.md` (which cites `F-RR-01`), and wires **two** complementary checks into `validate.sh --check-all`: `finding-trace <ledger> <letter>` (**forward** — every cited ID resolves to a ledger finding) **and** `softness-check <letter> <ledger>` (**reverse** — every locked ledger finding is delivered in the letter). `finding-trace` reports `letter=UNCITED` but exits 0 when a ledger finding is *absent* from the letter — omission/deletion is `softness-check`'s job (review fix — Codex #30 P2: gating only the forward direction would not catch deleting the worked example's canonical citation; the reverse `softness-check` does). A drift in either direction now fails at release time. *(Wiring `softness-check` onto the pair surfaced a latent `softness-check` fragility: its body/appendix boundary regex `Appendix\s+A\b` matches that string in prose/comments, not only headings, so the example letter's header note must avoid the literal appendix-heading words — noted inline in the example letter. Heading-anchoring that boundary is a separate `softness-check` hardening, out of scope here.)*

### Self-review (Increment 2)

- *W2 false-positive risk* — a Must-Fix legitimately deferred across sessions would W2-warn; kept advisory (not ERROR) by default for exactly that reason, with `--strict` as the opt-in gate. Mirrors W1's posture.
- *Revision ID surface* — revision plans have no comment-only convention, so IDs match anywhere in the text; the exact-boundary regex still prevents `F-P5-01` ≠ `F-P5-011`. A passing mention ("superseded F-RR-01") counts as addressing it — acceptable for a coverage signal.
- *Canonical-gate scope* — the gate asserts **referential integrity** (every cited ID resolves) on the worked example, not severity (`softness-check` owns that on the same letter); no overlap, and the example ledger is itself a valid `apodictic.finding.v1` carrier.

## Increment 3 — revision-completion (`revised`) lifecycle (built)

Gives the third lifecycle state `revised` its first real meaning and teaches `finding-trace` to audit revision **completion** by ID — not just plan coverage (W2). Like Increment 2, this extends `finding-trace` with **no new validator and no count change**.

**Artifact-role split.** The revision-stage globs already in use split into two roles by filename:
- **plan** (`*_Session_Plan_*.md`) — *intent*. A finding referenced here is planned (W2 coverage, Increment 2).
- **completion** (`*_Revision_*.md`) — a *completed* revision round (the Revision Report, `state-lifecycle.md §Revision Round Output`). A finding referenced in a completed-revision artifact is worked.

E4 (dangling) and W2 (plan coverage) keep treating **both** globs as "a revision artifact is present" — unchanged. The completion checks below read only the `*_Revision_*.md` subset.

**The `revised` state.** `execution.finding_states[id]` advances `locked → delivered → revised`. The revision coach advances a finding to `revised` when a revision round confirms it resolved (`state-lifecycle.md §Revision Round Output → Flags resolved`). Until this increment `revised` was a valid-but-unreached enum value.

**Two checks:**
- **E5 phantom completion** (ERROR) — `finding_states[id] == "revised"` for a *ledger* finding, but the ID is not referenced in any completed-revision (`*_Revision_*.md`) artifact, when at least one such artifact is present. A sidecar claiming a finding revised with no completed-revision artifact behind it is an incoherent completion claim. (A `revised` key that isn't a ledger ID is already E2; `revised` is a valid `_STATES` value so it is never E3.)
- **W3 completion follow-through** (advisory; ERROR under `--strict`) — a ledger finding referenced in a completed-revision artifact whose `finding_states` entry is not `revised` (still `locked`/`delivered`/absent). The round worked it but the lifecycle wasn't advanced. Advisory because the state write may lag the artifact; `--strict` gates it. Skipped when no completion artifact is present.

**Report.** The per-ID `rev=` column gains completion resolution: `done` (referenced in a completed-revision artifact) / `planned` (in a session plan only) / `—` (no reference) / `n/a` (no revision artifacts). The `state=` column already surfaces `revised`.

**Ownership boundary.** W2 asks "did the plan pick it up?"; W3 asks "did a completed round work it, and was the lifecycle advanced?"; E5 asks "does a `revised` claim have a completed-revision artifact behind it?" Each is a class no other check raises. Severity fidelity stays `softness-check`'s; intra-ledger hygiene stays `structured-findings`'.

### Self-review (Increment 3)

- *E5 false-positive on cross-session revisions* — a finding revised in an earlier session whose `*_Revision_*.md` is not in the current scope would look like a phantom completion. E5 is gated on ≥1 completion artifact being **present in scope** and fires only for a `revised` ID missing from the completion set that is present — so a folder with no completion artifact never E5s. Same permissive-by-default / `--strict`-tightening posture as W1/W2.
- *plan vs completion by filename* — the role split keys on the established naming convention (`_Session_Plan_` = intent, `_Revision_` = completed round) from `output-structure.md`. A misnamed artifact degrades to the safe direction (treated as plan-only), so at worst a W3/E5 is **not** raised — never a false ERROR.
- *W3 vs W2 overlap* — distinct artifacts, distinct questions: W2 reads any revision artifact for *plan* coverage; W3 reads only completion artifacts for *lifecycle advancement*. A finding can be W2-clean (planned) yet W3-warn (worked but state not advanced).
- *monotonic ordering not asserted* — `finding-trace` holds no event history, so it does not assert that `revised` implies a prior `delivered` (the letter may be absent from scope). Ordering is the runner/gate's job; this increment audits completion reconciliation only.

## Out of scope (later increments)

- **`deficit-lock` / `softness-check` by-ID consolidation.** Folding their residual prose heuristics fully onto IDs is a separate hardening pass.
- **Runner-advanced `revised` writes.** Increment 3 *audits* the `revised` state; having the execution gate itself write `finding_states[id] = revised` on a verified revision round (rather than the coach updating the sidecar) is a Runner-Governed Execution concern, deferred to that track.

## Self-review (pre-build)

- *Overlap risk with `softness-check`* — resolved by the ownership-boundary table: `finding-trace` raises only classes no other validator raises (dangling refs, phantom/invalid sidecar state). Forward omission/softening is left entirely to `softness-check`.
- *False failures on partial runs* — each artifact is optional; a ledger-only or pre-synthesis run skips the dimensions it can't evaluate (W1 is advisory, gated on the sidecar showing synthesis cleared). The default is permissive; `--strict` is the release/CI tightening.
- *Validator-count collision* — this branch bases on `main` (17 validators). PR #28 (gate-event records) independently bumps to 18; if it merges first, this increment rebases to 18 → 19 and the AGG list gains both `gate-state` and `finding-trace`.
- *Parser reuse* — IDs are read via the shared `apodictic_artifacts.parse_blocks` (the one block grammar), and bare `F-…` tokens via an exact-boundary regex (so `F-P5-01` ≠ `F-P5-011`), matching `honesty_check.py`'s `_id_present` discipline.
