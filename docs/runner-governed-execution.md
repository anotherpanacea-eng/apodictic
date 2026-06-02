# Runner-Governed Execution — Design Spec

**Status:** design only (not built). Roadmap: `ROADMAP.md` → Harness Engineering → Runner-Governed Execution. This is the heavyweight item of the priority set; it is specced here before any build because it changes *where enforcement lives*.

## Problem

APODICTIC's execution gates are **prompt-governed**: the orchestration prose tells the model to run `validate.sh` checks at the right moments (pre-synthesis gate, Step 9 underdiagnosis retry, Step 10 pre-output, the Deficit Lock at Triage). The model is a conscientious but fallible runtime — a gate that "the model should run" can be skipped under context pressure, and the same evidence can fire a gate for one model and not another (the original CR-6 finding: the underdiagnosis retry loop fired for Opus, not for Codex). Phase 4 made the *triggers* detectable (condition-triggered, not model-emergent); the gates themselves are still self-invoked.

## Goal

Move **enforcement** out of the prompt and into a lightweight **runner** that the model defers to. The model still does all the editorial reasoning; the runner owns execution state and refuses illegal transitions — e.g. *"synthesis cannot start until the Findings Ledger exists, every synthesis-bound finding is locked, and `--check-all` passes."* Enforcement becomes external and model-independent.

## What the runner owns

A small, inspectable execution-state record (an extension of the existing `Diagnostic_State.meta.json` sidecar — already a contract under `apodictic.diagnostic-state.v1`):

- **current phase** (intake → passes → audits → triage/lock → synthesis → letter → spot-check → revision)
- **required artifacts** for the current and next phase (contract, ledger, audit invocation log, locked findings, letter)
- **gate status** — which gates have passed/failed/are pending (severity-floor, audit-signal-propagation, underdiagnosis-triggers, decision-layer-check, softness-check, deficit-lock)
- **fired retry triggers** and their resolution (upgraded vs. override-marked)
- **allowed next actions** — the only transitions legal from the current state

## How it builds on v2.0.0

The runner is now *tractable* because the v2.0.0 work gave it the substrate it needs:

- **Harness Contracts v2** — runner state and every artifact it inspects are JSON-Schema-validated (`apodictic_artifacts.py`), so the runner reasons over typed objects, not prose.
- **Finding Lifecycle IDs** — the runner tracks each finding by durable `id` across phases (locked → delivered → revised), which is exactly the cross-phase state a runner must hold.
- **`validate.sh --check-all` + the validator suite** — the runner's gate checks already exist as mechanical commands; the runner orchestrates *when* they must pass, rather than trusting the model to invoke them.

## Architecture options

1. **Gate-manifest + state file (recommended first step).** A declarative `gates.json` maps each phase to its precondition checks (artifact existence + validator pass). A thin `validate.sh gate <phase>` reads the sidecar + runs the required checks and exits non-zero if the transition is illegal. The orchestration prose changes from "run these checks" to "you may not enter <phase> until `validate.sh gate <phase>` passes." Still cooperative, but the *gate definition* is external and uniform.
2. **External orchestrator (full version).** A process that drives phase transitions, invokes the model per phase with a scoped context, and hard-blocks transitions. Maximum enforcement; largest departure from the current plugin execution model (the plugin runs *inside* the model today, so this needs a real host harness).

Recommended path: ship option 1 (declarative gate manifest + `gate` subcommand) as the next increment, measure how often it catches a skipped gate, then decide whether option 2's cost is justified.

## Phased adoption

1. **Gate manifest** — encode the existing pre-synthesis / Step 9 / Step 10 gates as data; add `validate.sh gate <phase>`; reference it from `run-synthesis.md` as a hard precondition.
2. **Runner state in the sidecar** — extend `apodictic.diagnostic-state.v1` with `phase`, `gates`, `allowed_next`; the `gate` command reads/writes it.
3. **Finding-ID lifecycle tracking** — record each finding's state (`locked` / `delivered` / `revised`) by ID; the softness/deficit gates already match by ID.
4. **External orchestrator** — only if 1–3 show residual skipped-gate incidents.

## Open questions / risks

- **Execution model.** The plugin currently runs inside the model; a true runner needs a host that can invoke validators between phases. Option 1 stays within today's model (cooperative gate command); option 2 requires the SDK/host harness.
- **Author-interactive phases.** Intake and revision are conversational; the runner must allow human-in-the-loop transitions without over-gating.
- **Degradation.** On hosts without shell execution, gates fall back to inline checks today; the runner must degrade to "model attests" with a recorded blind spot, not silently skip.
- **Scope creep vs. the model's judgment.** The runner enforces *ordering and artifact/gate existence*, never editorial content. The line must stay there.
