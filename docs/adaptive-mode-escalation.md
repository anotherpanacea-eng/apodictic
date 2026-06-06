# Adaptive Mid-Run Mode Escalation

**Status:** spec + `escalation-check` validator + run-core integration — **built**, now including **de-escalation** (the symmetric case). Roadmap: `ROADMAP.md` → Infrastructure → Adaptive Mid-Run Mode Escalation. Implementation: `scripts/escalation_check.py`, `validate.sh escalation-check`, `run-core.md §Mid-Run Escalation Check`.

## Problem

The execution mode (`single-agent` / `sequential` / `hybrid` / `swarm`) is chosen at **preflight**, from coarse heuristics (word count, a pronoun-frequency POV guess). After **Tier 1** (Pass 0 Structure Map + Pass 1 Reader Orientation), the system knows far more — the *actual* POV count, timeline shape, and analytical density. The preflight mode may now be wrong: a manuscript that looked simple (single-agent) but turns out to be a 5-POV nonlinear braid will suffer salience decay if the remaining Tier 2 passes run in one context.

This is a **condition-triggered, not model-emergent** gate (the §Future Work discipline): the escalation *triggers* must be mechanically detectable, not "the model should notice it got complicated." Without that, the check fires for one model and not another on the same manuscript.

## Design

A checkpoint **after Tier 1, before the first Tier 2 pass** that compares revealed complexity against the preflight estimate and, if materially higher, **recommends** (never forces) escalating the mode for the remaining passes.

### Mechanical detector — `validate.sh escalation-check <run_folder>`

`scripts/escalation_check.py` reads the run folder and evaluates the four roadmap triggers, then computes a recommendation. It is **advisory**: the recommendation goes to the author, who confirms before any mode switch.

**Inputs:**
- **Sidecar** (`Diagnostic_State.meta.json`): `last_session.execution_mode` (the current mode) and an optional `complexity_signals` object that Pass 0/1 record — `{pov_count, nonlinear_timeline, belief_failures, orientation_failures}`.
- **Findings Ledger**: `tier1_finding_count` is computed **directly and reliably** from the ledger — the number of `apodictic.finding.v1` blocks whose `id` origin is a Tier-1 pass (`F-P0-…` / `F-P1-…`). This never depends on the model recording it.

**Triggers** (per the roadmap):

| | Trigger | Source |
|---|---|---|
| **T1** | `pov_count > 3` (preflight's pronoun heuristic underestimated) | sidecar `complexity_signals.pov_count` |
| **T2** | `nonlinear_timeline` (non-linear or nested-frame structure) | sidecar `complexity_signals.nonlinear_timeline` |
| **T3** | `belief_failures > 5` **or** `orientation_failures > 3` (higher-than-expected analytical density) | sidecar `complexity_signals` |
| **T4** | `tier1_finding_count > 20` (Pass 0+1 combined notable items) | **ledger** (computed) |

A signal absent from the sidecar makes its trigger **unevaluable** (not fired), and the detector says so — so the model knows to assess that dimension by hand rather than silently passing. `tier1_finding_count` (T4) is always evaluable.

**Recommendation** — escalation paths (single-agent → sequential; sequential → hybrid / swarm):

- `single-agent` + any trigger ⇒ **sequential** (architectural isolation removes the salience-decay risk of one shared context).
- `sequential` + any trigger ⇒ **swarm** when the manuscript is *architecturally* complex — `pov_count > 3` **and** (`tier1_finding_count > 20` **or** `nonlinear_timeline`) — where cross-pass anchoring on a complex book is the risk; otherwise **hybrid** (a focus map meaningfully reduces noise for later passes).
- `hybrid` / `swarm` ⇒ no escalation (already at/above the ceiling).

The hybrid-vs-swarm boundary is a documented heuristic, tunable in one place.

**De-escalation (the symmetric case).** When **no** trigger fires *and* every complexity dimension is measured and in a **"clearly simple" band**, an over-provisioned expensive mode is recommended **down** to `sequential`:

- `swarm` / `hybrid` + *all* of `pov_count ≤ 2`, `¬nonlinear_timeline`, `belief_failures ≤ 2`, `orientation_failures ≤ 1`, `tier1_finding_count ≤ 8` ⇒ **sequential** (the preflight mode is over-provisioned; Tier-2 tokens are wasted).
- `single-agent` / `sequential` ⇒ no de-escalation (already cheap; `sequential → single-agent` is withheld because that is where salience-decay risk lives).

The simple band sits **well below** the escalation thresholds, leaving a **neutral zone** between them (e.g. `pov_count = 3`, or `9 ≤ tier1_finding_count ≤ 20`) where neither direction fires — so the checkpoint never thrashes near a boundary. De-escalation is **strictly more conservative** than escalation: *every* dimension must be present and well-typed; a single absent or malformed signal blocks the recommendation. The asymmetry is deliberate — wrongly de-escalating a genuinely complex manuscript risks cross-pass anchoring (**wrong analysis**), which is worse than the wasted tokens of over-provisioning. Like escalation, it is advisory (exit 0) and author-confirmed; `--strict` exits 1.

**Exit codes.** `0` always by default — escalation is a recommendation, not a gate (mirrors the roadmap constraint "not automatic"). `--strict` returns `1` when escalation is recommended, for an orchestrator/CI that wants the checkpoint to *halt* until the author decides. `--self-test` exercises the trigger + recommendation matrix. Degrades to an advisory `WARN` without `python3` (the model evaluates the triggers inline from the same signals).

### Sidecar contract

`apodictic.diagnostic-state.v1` gains an optional `complexity_signals` object (additive; `additionalProperties: true`, no version bump):

```jsonc
"complexity_signals": {
  "pov_count": 5,
  "nonlinear_timeline": true,
  "belief_failures": 7,
  "orientation_failures": 2
}
```

Pass 0 records `pov_count` (refining preflight's guess from the Structure Map) and `nonlinear_timeline`; Pass 1 records `belief_failures` / `orientation_failures`. `tier1_finding_count` is **not** stored — it is computed from the ledger so it can't drift.

### Prose integration — `run-core.md §Mid-Run Escalation Check`

A new section between **§Execution Protocol** and **§Pre-Pass Re-Grounding** (where the roadmap specifies), plus a one-line instruction in the Pass 0/1 output spec to record `complexity_signals`. The check runs **once**, after Tier 1, before the first Tier 2 dispatch:

1. Run `escalation-check <run_folder>` (or evaluate the triggers inline on a no-shell host).
2. If escalation **or de-escalation** is recommended, present the author a brief summary — *"Tier 1 found [fired triggers / no triggers and all signals simple]. I'd recommend switching from [current] to [recommended] for the remaining passes (cost difference ~[N]K tokens). Proceed?"* — and switch only on confirmation, writing the new `execution_mode` to the sidecar.

**Constraints** (enforced by where it runs, not by the validator): escalation is safe **only between Tier 1 and Tier 2** — never retroactively re-run completed passes; the existing Tier-1 Findings Ledger entries carry forward unchanged (only the Tier-2 dispatch method changes); the recommendation is never automatic.

## Out of scope

- **Genre-hybridization trigger.** The roadmap names it narratively but gives no threshold; deferred until it has a detectable condition.
- **Automatic switching.** Out of scope by design — the author always confirms.

## Self-review (pre-build)

- *Signal availability.* The three judgment signals (POV, timeline, belief/orientation) come from the sidecar, which the model populates; an unrecorded signal is reported **unevaluable** and does not fire (conservative — never a false escalation), while `tier1_finding_count` is always computed from the ledger so the check is never fully blind. This is the honest failure mode: under-trigger, never over-trigger, and say which dimensions weren't machine-checkable.
- *Advisory vs. gate.* Default exit 0 matches the roadmap's "recommendation, not automatic"; `--strict` exists for a host that wants to enforce the checkpoint, mirroring the `finding-trace` W1/W2 posture.
- *Condition-triggered discipline.* Every trigger is a count or a boolean read from a named field — no "the model should notice." This is exactly the CR-6 lesson (a model-emergent gate that fired for Opus and not Codex) applied to mode selection.
- *No retroactive work.* The validator only reads state; the prose constrains the switch to the Tier-1→Tier-2 boundary, so completed passes are never re-run.
- *Hybrid-vs-swarm heuristic.* A judgment call encoded as one condition (`pov>3 ∧ (findings>20 ∨ nonlinear)`); documented and tunable. Worst case it recommends hybrid where swarm was marginally better — still an escalation, still author-confirmed.
- *De-escalation conservatism.* The simple band is set below the escalation thresholds with a neutral zone between, and de-escalation requires *every* signal present, well-typed, and simple (a missing/malformed signal blocks it) — so the failure mode is "we keep an over-provisioned mode" (wasted tokens), never "we strip architectural isolation off a complex manuscript" (wrong analysis). De-escalation targets only `sequential`, never `single-agent`, keeping a salience-safe floor. Author-confirmed like escalation.
