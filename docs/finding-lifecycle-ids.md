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

**Completion is an explicit marker, not a bare mention.** The Revision Report names findings in **both** *Flags resolved* and *Flags still present* (a worked-but-unresolved finding whose fix didn't land). So completion cannot key on "the ID appears in the report" — a still-present finding is named there and must **not** count as completed. A finding is marked completed only by an explicit `<!-- resolved: F-XX-NN -->` HTML-comment marker (mirroring the letter's `<!-- finding: … -->` discipline). Bare mentions still feed E4/W2 (a still-present finding is "planned" coverage), but only the marker drives E5/W3.

**Two checks:**
- **E5 phantom completion** (ERROR) — an **in-scope contradiction**: a completed-revision (`*_Revision_*.md`) artifact *mentions* a ledger finding (bare — e.g. under *Flags still present*) whose `finding_states` is `revised`, but carries **no** `<!-- resolved: … -->` marker for it. The report and the sidecar disagree. E5 is scoped to IDs the **current** report mentions, because `finding_states` is a rolling all-session map: a finding resolved in an earlier (out-of-scope) round is durably `revised` and simply won't appear in this report — flagging it would be a false-positive (PR #32 re-review, P1). (A `revised` key that isn't a ledger ID is already E2; `revised` is a valid `_STATES` value so it is never E3.)
- **W3 completion follow-through** (advisory; ERROR under `--strict`) — a ledger finding *marked resolved* in a completed-revision artifact whose `finding_states` entry is not `revised` (still `locked`/`delivered`/absent). The round resolved it but the lifecycle wasn't advanced. Advisory because the state write may lag the artifact; `--strict` gates it. Skipped when no completion artifact is present, or when there is no parseable sidecar to judge advancement against.

**Report.** The per-ID `rev=` column gains completion resolution: `done` (carries a resolved marker) / `planned` (mentioned in a revision plan/report but **not** marked resolved) / `—` (no reference) / `n/a` (no revision artifacts). The `state=` column already surfaces `revised`.

**Ownership boundary.** W2 asks "did the plan pick it up?"; W3 asks "the report resolved it — was the lifecycle advanced?"; E5 asks "the report mentions it as unresolved — why does the sidecar say `revised`?" Each is a class no other check raises. Severity fidelity stays `softness-check`'s; intra-ledger hygiene stays `structured-findings`'.

### Self-review (Increment 3)

- *Bare-mention false-positive (PR #32 review, P1)* — the first cut keyed completion on **any** `F-…` token in a `*_Revision_*.md` artifact. But the Revision Report template lists *Flags still present* alongside *Flags resolved*, so a legitimate report ("`F-P5-01` remains present; the attempted fix did not land") was classified `rev=done` and W3-failed under `--strict` unless the sidecar wrongly marked the unresolved finding `revised` — pushing the lifecycle toward a false state. Fixed by requiring an explicit `<!-- resolved: F-… -->` marker for completion; a still-present mention stays `planned` and triggers nothing. Regression-tested (`w3_skips_unresolved_mention`, `w3_strict_ok_on_still_present`, `still_present_not_done`).
- *E5 cross-session scope (PR #32 re-review, P1)* — the first cut gated E5 only on "≥1 completion artifact present" and checked **every** `revised` sidecar ID against that artifact's resolved markers. But `finding-trace <run_folder>` walks up to the project-root sidecar (a rolling all-session `finding_states`) while the completion artifacts are just the current run folder's — so a later round resolving only `F-P5-02` would hard-fail E5 for an already-`revised` `F-P5-01`. Fixed by scoping E5 to IDs the **current** report actually mentions (`comp_mentioned`): an out-of-scope resolution isn't named here, so it's left alone. Regression-tested (`e5_no_falsepos_out_of_scope`). The principled alternative — run/event-scoped state instead of the rolling sidecar — is a Runner-Governed Execution concern, deferred to that track.
- *plan vs completion by filename* — the role split keys on the established naming convention (`_Session_Plan_` = intent, `_Revision_` = completed round) from `output-structure.md`. A misnamed artifact degrades to the safe direction (treated as plan-only), so at worst a W3/E5 is **not** raised — never a false ERROR.
- *W3 vs W2 overlap* — distinct artifacts, distinct questions: W2 reads any revision artifact for *plan* coverage; W3 reads only completion artifacts for *lifecycle advancement*. A finding can be W2-clean (planned) yet W3-warn (worked but state not advanced).
- *monotonic ordering not asserted* — `finding-trace` holds no event history, so it does not assert that `revised` implies a prior `delivered` (the letter may be absent from scope). Ordering is the runner/gate's job; this increment audits completion reconciliation only.

## Cross-track addition — Retcon Planning F3 source provenance (E6)

`finding-trace` is the project's owner of cross-artifact `F-…` referential integrity, so the Retcon Planning **F3** increment homes its provenance check here rather than rebuilding ledger access in `retcon-plan`. **E6 — dangling retcon source** (ERROR): a Retcon Plan (`*_Retcon_Plan_*.md`) `apodictic.retcon_item.v1` block with an optional `source` finding-ref (primarily a Pass-8 Reveal-Economy finding, e.g. `F-P8-03`) whose `source` does **not** resolve to a ledger finding. Only schema-shaped `F-…` refs are checked — a malformed `source` is the `retcon-plan` schema's job (R1), not E6's, so the two validators don't double-report a format error. The run-folder resolver picks up Retcon Plans alongside the ledger/letter/revision artifacts; the report header notes how many retcon sources were traced. See [`docs/retcon-planning.md`](retcon-planning.md) §F3.

## Out of scope (later increments)

- **`deficit-lock` / `softness-check` by-ID consolidation.** Folding their residual prose heuristics fully onto IDs is a separate hardening pass.
- **Runner-advanced `revised` writes.** Increment 3 *audits* the `revised` state; having the execution gate itself write `finding_states[id] = revised` on a verified revision round (rather than the coach updating the sidecar) is a Runner-Governed Execution concern, deferred to that track.

## Self-review (pre-build)

- *Overlap risk with `softness-check`* — resolved by the ownership-boundary table: `finding-trace` raises only classes no other validator raises (dangling refs, phantom/invalid sidecar state). Forward omission/softening is left entirely to `softness-check`.
- *False failures on partial runs* — each artifact is optional; a ledger-only or pre-synthesis run skips the dimensions it can't evaluate (W1 is advisory, gated on the sidecar showing synthesis cleared). The default is permissive; `--strict` is the release/CI tightening.
- *Validator-count collision* — this branch bases on `main` (17 validators). PR #28 (gate-event records) independently bumps to 18; if it merges first, this increment rebases to 18 → 19 and the AGG list gains both `gate-state` and `finding-trace`.
- *Parser reuse* — IDs are read via the shared `apodictic_artifacts.parse_blocks` (the one block grammar), and bare `F-…` tokens via an exact-boundary regex (so `F-P5-01` ≠ `F-P5-011`), matching `honesty_check.py`'s `_id_present` discipline.
