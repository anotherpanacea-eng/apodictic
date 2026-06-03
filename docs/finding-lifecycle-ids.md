# Finding Lifecycle IDs — cross-artifact trace

**Status:** Increment 1 (this doc + `finding-trace` validator) **built**. Roadmap: `ROADMAP.md` → Harness Engineering → Finding Lifecycle IDs. Implementation: `scripts/finding_trace.py`, `validate.sh finding-trace`.

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

## Out of scope (later increments)

- **Increment 2 — revision follow-through.** Trace IDs into the revision plan / coaching artifacts (dangling-ref + Must-Fix coverage) once those artifacts carry ID citations.
- **Increment 2 — canonical `--check-all` gating.** Run `finding-trace` against the shipped `example-editorial-letter.md` + a paired canonical ledger so a citation drift is a release-gate failure (the synthetic self-test is the gate this increment).
- **`deficit-lock` / `softness-check` by-ID consolidation.** Already partly done; folding their residual prose heuristics fully onto IDs is a separate hardening pass.

## Self-review (pre-build)

- *Overlap risk with `softness-check`* — resolved by the ownership-boundary table: `finding-trace` raises only classes no other validator raises (dangling refs, phantom/invalid sidecar state). Forward omission/softening is left entirely to `softness-check`.
- *False failures on partial runs* — each artifact is optional; a ledger-only or pre-synthesis run skips the dimensions it can't evaluate (W1 is advisory, gated on the sidecar showing synthesis cleared). The default is permissive; `--strict` is the release/CI tightening.
- *Validator-count collision* — this branch bases on `main` (17 validators). PR #28 (gate-event records) independently bumps to 18; if it merges first, this increment rebases to 18 → 19 and the AGG list gains both `gate-state` and `finding-trace`.
- *Parser reuse* — IDs are read via the shared `apodictic_artifacts.parse_blocks` (the one block grammar), and bare `F-…` tokens via an exact-boundary regex (so `F-P5-01` ≠ `F-P5-011`), matching `honesty_check.py`'s `_id_present` discipline.
