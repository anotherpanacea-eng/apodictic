# Gated `revision_round` phase — spec (Increment 4a)

**Status:** Spec (not yet built). Follow-up to Project Addressability Increment 4 (`docs/project-addressability.md` §Increment 4 build split). Makes the runner-governed gate engine the canonical writer of the `revised` finding-state, resolving a direct-write-vs-fold contradiction. Touches `schemas/execution-gates.v1.json`, `scripts/run_gate.py` (+ root mirror), `references/state-lifecycle.md`, and the `--check-all` gate fixture. No new validator; reuses the gate engine + `finding-trace`.

## The contradiction this resolves

Today the revision-round protocol writes the third finding-lifecycle state **directly** into the sidecar: `execution.finding_states[<id>] = "revised"` (`state-lifecycle.md:120`). The runner-governed gate engine, meanwhile, derives `finding_states` purely by *folding* the append-only `gate_events[]` log (`run_gate.py:328-332`), and `_PHASE_FINDING_STATE` stops at `delivered` (`run_gate.py:49`) — no phase emits `revised`.

These coexist only because a revision-stage project usually has **no** `gate_events`, so `gate --check-state` early-returns ("nothing to check"). The moment a project *is* runner-governed, the two disagree: the fold won't reproduce the direct write, and `check-state`'s `pointer == fold` invariant (`run_gate.py:662`) fails (exit 1) — the regression the `finding_states_drift_detected` self-test guards.

4a makes the **gate** the single writer of `revised`, and **removes** the direct write — so `finding_states.revised` is always fold-consistent. 4b's loop dispatcher then reads `finding_states.revised` as a first-class field (it already prefers it, falling back to markers).

## The delicate part: selective per-finding marking

Every existing phase marks **all** ledger findings with one state (`_finding_deltas`, `run_gate.py:414-419`: `{fid: _PHASE_FINDING_STATE[phase] for fid in _ledger_finding_ids(led)}`). `run_synthesis` → every finding `locked`; `run_spot_check` → every finding `delivered`.

`revision_round` is different: a round resolves **only a subset** of findings (the *Flags resolved* list). So its deltas must mark **only the ids carrying a `<!-- resolved: F-… -->` marker** in the run folder — the rest correctly stay `delivered`. This is the one genuinely new code path in the fold.

`finding-trace` already computes exactly this set: `resolved_cited_ids(text)` (`finding_trace.py:114`), aggregated across run-folder artifacts (`finding_trace.py:187`). So `revision_round`'s `_finding_deltas` **reuses that resolution** rather than inventing a revision-report glob.

## Build

**1. Manifest (`execution-gates.v1.json`).** Add a `revision_round` phase:
- `allowed_next: ["run_synthesis"]` — a cleared round authorizes re-diagnosing the revised draft. (Not `[]`: an empty `allowed_next` co-occurs with a `pending_gate` in the fold's semantics, so it must be non-empty for a cleared frontier.)
- `entry_requires.artifacts: ["findings_ledger"]` (the ledger the resolved ids are checked against; the revision report is located via `finding-trace`'s run-folder scan, so no new artifact_key is strictly required — add an optional `revision_report` key only if a stable `*_Revision_Report_*.md` convention is confirmed).
- `entry_requires.attested`: e.g. `rev-a1` delta scan complete (resolved vs. still-present vs. new), `rev-a2` every confirmed-resolved finding carries a `<!-- resolved: <id> -->` marker, `rev-a3` declined items are not silently re-flagged.
- `entry_requires.checks: [{validator: "finding-trace", targets: ["run_folder"]}]` — mechanizes report↔sidecar consistency (W3/E5) at the gate.

**2. `run_gate.py` (+ root `scripts/` mirror — the Increment-2 lesson).**
- `_PHASE_FINDING_STATE["revision_round"] = "revised"` (`_STATE_RANK` already ranks `revised: 3`).
- `_finding_deltas`: branch `if phase == "revision_round"` → resolve the run-folder resolved ids via `finding_trace.resolved_cited_ids` (aggregated as in `finding_trace.py:187`) → `{fid: "revised" for fid in resolved_ids}`. All other phases unchanged.
- Both call sites already pass through this helper: `cmd_gate` (no-attest path, `:456`) and `cmd_attest` (attested clearing, `:510`). `revision_round` has attested items, so it clears via `--attest` — deltas land at `:510`.

**3. `state-lifecycle.md` (remove the direct write).** Replace the "advance its Finding Lifecycle ID in the sidecar: `execution.finding_states[<id>] = "revised"`" instruction (`:120`) with: keep writing the `<!-- resolved: <id> -->` markers (now the gate's *input*), then **clear the round through the gate** — `validate.sh gate revision_round <run_folder>` then `gate --attest revision_round <run_folder>` — which folds the resolved-marker ids into `finding_states.revised`. The `finding-trace` W3/E5 audit still applies (now as the gate's check). This is the behavioral half of the contradiction fix and must land in the same change.

**4. Self-tests (`run_gate.py`).** Add: (a) clearing `revision_round` advances **only** the resolved-subset ids to `revised`, leaving still-present findings `delivered`; (b) the pointer the engine writes equals the fold (the `pointer == fold` invariant holds with a `revised` delta present); (c) a round with zero resolved markers is a no-op on `finding_states`. Existing two-phase self-tests (e.g. the `len(seeds) == 2` migration assertion, `:809-811`) must be updated to expect the third phase.

**5. `--check-all` gate fixture.** Add a `revision_round` clearing event to the canonical `references/example-run-folder` sidecar (or a sibling fixture) so `gate-state` exercises the new phase and proves `pointer == fold` with a folded `revised` state. Confirm `--check-all` stays green.

**6. Docs.** Mark Increment 4a built in `docs/project-addressability.md` + ROADMAP; simplify 4b's "source of truth" note (now `finding_states.revised` is canonical, markers are the gate's input). Changelog fragment.

## Out of scope / open questions

1. **Revision-report artifact_key.** Whether to add a `revision_report` glob to `artifact_keys` or rely solely on `finding-trace`'s run-folder scan for resolved ids. Recommendation: reuse `finding-trace` (no new key) unless a stable filename convention already exists — confirm during build.
2. **Re-revision rounds.** A finding resolved in round 1, regressed and re-flagged in round 2: the fold is monotonic by `_STATE_RANK` (`:331`), so once `revised` it can't drop back to `delivered` via the fold. If round 2 must demote a finding, that needs an explicit lower-ranked delta or a documented "new finding id" convention — flag for the build review.
3. **No validator count change.** `revision_round` is a gate phase, not a new validator; `finding-trace` is its check. Confirm the `gate`/`gate-state` self-tests cover it without a 37→38 bump.

---

*Design spec. If adopted, the runtime changes land in `execution-gates.v1.json`, `run_gate.py` (+ root mirror), `state-lifecycle.md`, and the `--check-all` gate fixture.*
