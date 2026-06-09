# Gated `revision_round` phase — spec (Increment 4a)

**Status:** Spec (not yet built). Follow-up to Project Addressability Increment 4 (`docs/project-addressability.md` §Increment 4 build split). Adds a gated `revision_round` phase so the runner-governed gate engine writes `revised` **fold-consistently** for governed projects, while the existing direct write is retained as the fallback for non-governed projects. Touches `schemas/execution-gates.v1.json`, `scripts/run_gate.py` (+ root mirror), `references/state-lifecycle.md`, `revision-coach/SKILL.md`, `docs/project-addressability.md`, `docs/finding-lifecycle-ids.md`, and the `--check-all` gate fixture. No new validator; reuses the gate engine + `finding-trace`.

## The contradiction — and its true scope (spec-review Blocker 1)

The revision-round protocol writes the third finding-lifecycle state **directly** into the sidecar: `execution.finding_states[<id>] = "revised"` (`state-lifecycle.md:120`). The gate engine, separately, derives `finding_states` *only* by folding the append-only `gate_events[]` log (`run_gate.py:328-332`), and `_PHASE_FINDING_STATE` stops at `delivered` (`run_gate.py:49`).

These collide **only for runner-governed projects.** `check_state` early-returns ("nothing to check") unless the sidecar has `gate_events` (`run_gate.py:562-563`). So:

- **Non-governed project (the common case — no `gate_events`):** the direct write is the *only* mechanism that records `revised`, and `check_state` never runs, so there is no `pointer == fold` invariant to violate. **This path must keep the direct write** — removing it would silently strip the ability to record `revised` from the majority of projects. (This was the original spec's mistake.)
- **Runner-governed project (has `gate_events`):** a direct `revised` write the fold can't reproduce *is* drift → `check_state` exits 1 (`run_gate.py:662-663`; the `finding_states_drift_detected` self-test guards it). These projects must route `revised` **through the gate**.

So 4a does not remove the direct write — it **scopes** it. The gate becomes the `revised` writer when (and only when) the project is already runner-governed; otherwise the direct write stands. Both produce the same sidecar field; 4b's dispatcher reads `finding_states.revised` either way.

## The delicate part: selective per-finding marking

Every existing phase marks **all** ledger findings with one state (`_finding_deltas`, `run_gate.py:414-419`). `revision_round` must mark **only the resolved subset** — the ids carrying a `<!-- resolved: F-… -->` marker in the run folder — leaving still-present findings `delivered`. This is the one genuinely new code path in the fold.

The reusable surface is **`finding_trace`'s run-folder aggregation** (`finding_trace.py:186-188`): resolve the run folder's completion artifacts, then union `resolved_cited_ids(text)` across them. (Not the leaf `resolved_cited_ids`, which takes a single text — spec-review nit 7.) `run_gate.py` can `import finding_trace` directly — it's a sibling module on the same `sys.path` as the existing `import apodictic_artifacts`, and `finding_trace` imports only `apodictic_artifacts`, so there is no circular-import risk (spec-review §2, confirmed).

## Re-revision is terminal-by-id (spec-review Blocker 2 — normative, not open)

The fold raises a finding's state only when the new delta's rank ≥ current (`run_gate.py:331`, `_STATE_RANK`). So once `revised`, a finding **cannot** fold back to `delivered`. This is correct and must stay — `check_state` and the forward-only lifecycle depend on that monotonicity.

**Contract (normative):** `revised` is **terminal for a given ledger id.** A finding that regresses in a later round is handled as a **new finding** — re-diagnosis (round 2 re-runs `run_synthesis`, per `allowed_next` below) produces a fresh `F-…` id with its own `locked` delta. There is **no** lower-ranked delta and no in-place demotion (either would break the monotonicity invariant). This is a documented v1 behavior, not an open question.

## Build

**1. Manifest (`execution-gates.v1.json`).** Add a `revision_round` phase:
- `allowed_next: ["run_synthesis"]` — a cleared round authorizes re-diagnosing the revised draft (round 2). Non-empty is required (an empty `allowed_next` co-occurs with a `pending_gate` in the fold). The "earlier-phase target" is already an established pattern (`run_spot_check.allowed_next: ["deliver"]`), so the fold handles it (spec-review §4).
- `entry_requires.artifacts: ["findings_ledger", "revision_report"]` — add a `revision_report` artifact_key (`*_Revision_*.md`) so the gate's `finding-trace` check and the resolved-id scan have a concrete target.
- `entry_requires.attested`: `rev-a1` delta scan complete (resolved / still-present / new); `rev-a2` every confirmed-resolved finding carries a `<!-- resolved: <id> -->` marker; `rev-a3` declined items are not silently re-flagged.
- `entry_requires.checks: [{validator: "finding-trace", targets: ["run_folder"]}]` — mechanizes report↔sidecar consistency (W3/E5) at the gate.

**2. `run_gate.py` (+ root `scripts/` mirror — the Increment-2 lesson).**
- `_PHASE_FINDING_STATE["revision_round"] = "revised"` (`_STATE_RANK` already ranks `revised: 3`).
- `_finding_deltas`: branch `if phase == "revision_round"` → aggregate the run folder's resolved ids (the `finding_trace.py:186-188` path) → `{fid: "revised" for fid in resolved_ids}`. Other phases unchanged. `revision_round` has attested items, so the delta lands via `cmd_attest`'s clearing event (`run_gate.py:510`).

**3. `state-lifecycle.md` (scope the direct write — do NOT remove it).** Reframe `:120`: keep writing the `<!-- resolved: <id> -->` markers; then — **if the project is runner-governed (the sidecar has `gate_events`)** — clear the round through the gate (`validate.sh gate revision_round <run_folder>` then `gate --attest …`), which folds the resolved-marker ids into `finding_states.revised`. **Otherwise** (non-governed) write `finding_states[<id>] = "revised"` directly, as today. `finding-trace` W3/E5 audits consistency in both cases.

**4. Reconcile the now-conditional contract elsewhere (spec-review §6 — touch list was incomplete).**
- `revision-coach/SKILL.md:87` ("written directly per state-lifecycle.md") → "written directly (non-governed) or folded by the `revision_round` gate (runner-governed)."
- `docs/project-addressability.md:146` (the 4b source-of-truth rule, same phrasing) → same conditional.
- `docs/finding-lifecycle-ids.md:124` (runner-advanced `revised` "deferred to that track") → mark built in this increment.

**5. Self-tests (`run_gate.py`) — additive only (spec-review §5 correction).** The existing two-phase tests do **not** need editing: `_seed_migration` only seeds gates present in the legacy `gates` map, so the `len(seeds) == 2` assertion (`:809-811`) stays green — do **not** touch it. Add new tests: (a) clearing `revision_round` advances **only** the resolved-subset ids to `revised`, still-present findings stay `delivered`; (b) the written pointer equals the fold with a `revised` delta present (`pointer == fold`); (c) zero resolved markers → no-op on `finding_states`; (d) **a backward-moving frontier** — round 2's `run_synthesis` re-clear becomes the last-clearing, so `phase` regresses `revision_round → run_synthesis` and `allowed_next → ["run_spot_check"]` (spec-review §4 trap). Confirm 4b's dispatcher tolerates this oscillation (it reads `phase`/`pending_gate`; the regression is correct loop behavior).

**6. `--check-all` gate fixture (spec-review §5 — three coupled edits, all mandatory).** To exercise `revision_round` via the read-only `gate-state` check on the committed `example-run-folder`: (i) add a `revision_round` clearing event to the sidecar `gate_events`; (ii) add a `*_Revision_*.md` artifact carrying `<!-- resolved: F-P5-01 -->`; (iii) update the fixture's **pointer block** (`phase`, `allowed_next`, `finding_states.F-P5-01 → revised`) to the new fold — otherwise `gate-state` fails `pointer == fold`. Confirm `--check-all` green.

**7. Docs.** Mark Increment 4a built in `docs/project-addressability.md` + ROADMAP; simplify 4b's source-of-truth note (governed projects now read a gate-folded `finding_states.revised`). Changelog fragment. **No validator count change** — `revision_round` is a gate phase, `finding-trace` is its check (spec-review §6 confirmed).

## Decisions locked by review

- The direct write is **retained, scoped to non-governed projects** (Blocker 1) — not removed.
- `revised` is **terminal per ledger id**; regression → new id via re-`run_synthesis` (Blocker 2) — no lower-ranked delta.
- Existing self-tests are **not** edited; only additive tests (incl. the backward-frontier case).

---

*Design spec. If adopted, the runtime changes land in `execution-gates.v1.json`, `run_gate.py` (+ root mirror), `state-lifecycle.md`, the three reconciled docs, and the `--check-all` gate fixture.*
