# Runner-Governed Execution — Design Spec

**Status:** design only (not built). Roadmap: `ROADMAP.md` → Harness Engineering → Runner-Governed Execution. This is the concretized spec for **increment 1** (the cooperative gate manifest + state); it is intended to be implementation-ready and approved before code. Later increments (host-orchestrator) are sketched at the end.

## Problem

APODICTIC's execution gates are **prompt-governed**: the orchestration prose tells the model to run `validate.sh` checks at the right moments (pre-synthesis gate, Step 9 underdiagnosis retry, Step 10 pre-output, Step 12 section validation, Step 13 tone, the Deficit Lock at Triage). The model is a conscientious but fallible runtime — a gate that "the model should run" can be skipped under context pressure, and the same evidence can fire a gate for one model and not another (the original CR-6 finding). Phase 4 made the *triggers* detectable; the gates themselves are still self-invoked and scattered across the prose.

## Goal

Move the **gate definitions** out of prose into one declarative manifest, and consolidate "the checks for this transition" behind a single command the model must pass: `validate.sh gate <phase> <run_folder>`. The model still does all editorial reasoning; it can no longer *enter a phase* without the gate passing (or recording an explicit, marked exception). Increment 1 stays **cooperative** (the model invokes the gate) — true external enforcement is increment 4 (host harness), called out honestly below.

## Phase model (grounds on the existing dispatch)

The sidecar's `next_action.key` is already the de-facto phase enumeration (`commands/start.md §Resume Target`). The runner adopts it verbatim and attaches an **entry gate** (preconditions that must hold before the phase begins) and an **allowed-next** set to each phase:

| Phase (`next_action.key`) | Entry gate (must pass to begin) | Produces | allowed_next |
|---|---|---|---|
| `intake` *(implicit)* | — | Contract, `Diagnostic_State` + sidecar | `run_passes` |
| `run_passes` | contract exists; `contract_hash` set | Pass artifacts, Findings Ledger | `run_audits`, `run_synthesis` |
| `run_audits` | required passes complete | Audit findings, Audit Invocation Log | `run_synthesis` |
| `run_synthesis` | **ledger ready + every synthesis-bound finding locked** | Editorial letter | `run_spot_check` |
| `run_spot_check` | **letter passes all delivery checks** | Spot-check appended | `deliver` |
| `deliver` | spot-check complete | (present letter) | `revision_round`, `coaching` |
| `revision_round` / `coaching` | editorial letter delivered | Revision plan / session | `run_passes`, `deliver` |
| `handoff_reentry` | — (state reconciliation) | — | prior phase |

The two load-bearing gates are **`run_synthesis`** (the pre-synthesis lock gate) and **`run_spot_check`** (the consolidated letter-delivery gate, which subsumes today's scattered Step 10 / Step 12 / Step 13 checks).

## Gate manifest — `plugins/apodictic/schemas/execution-gates.v1.json`

Declarative; the source of truth for *what each transition requires*. `run-core.md` / `run-synthesis.md` reference it instead of restating per-step checks.

```json
{
  "$id": "apodictic.execution-gates.v1",
  "artifact_keys": {
    "contract":             "*_Contract_*.md",
    "findings_ledger":      "*_Findings_Ledger_*.md",
    "audit_invocation_log": "*_Audit_Invocation_Log_*.md",
    "editorial_letter":     ["*_Core_DE_Synthesis_*.md", "*_Full_DE_*.md", "*_Editorial_Letter_*.md"],
    "sidecar":              "Diagnostic_State.meta.json"
  },
  "phases": {
    "run_synthesis": {
      "entry_requires": {
        "artifacts": ["findings_ledger", "audit_invocation_log"],
        "checks": [
          {"validator": "ledger-check",         "targets": ["findings_ledger"]},
          {"validator": "structured-findings",  "targets": ["findings_ledger"]},
          {"validator": "deficit-lock",         "targets": ["findings_ledger"]}
        ]
      },
      "allowed_next": ["run_spot_check"]
    },
    "run_spot_check": {
      "entry_requires": {
        "artifacts": ["editorial_letter", "findings_ledger"],
        "checks": [
          {"validator": "synthesis-sections",        "targets": ["editorial_letter"]},
          {"validator": "severity-floor",            "targets": ["editorial_letter"]},
          {"validator": "decision-layer-check",      "targets": ["editorial_letter"]},
          {"validator": "audit-signal-propagation",  "targets": ["editorial_letter"]},
          {"validator": "underdiagnosis-triggers",   "targets": ["editorial_letter"]},
          {"validator": "softness-check",            "targets": ["editorial_letter", "findings_ledger"]},
          {"validator": "tone-check",                "targets": ["editorial_letter"]}
        ]
      },
      "allowed_next": ["deliver"]
    }
  }
}
```

`checks[].targets` is an ordered list of artifact keys → the file arguments passed to the validator (so `softness-check <letter> <ledger>` is expressible). Phases not listed have no mechanical entry gate.

## Artifact resolution

`gate` resolves each `artifact_key` to a file by globbing `<run_folder>` with the pattern(s) from `artifact_keys` (the `output-structure.md` naming conventions). Disambiguation when multiple runlabels are present: prefer the file whose `runlabel` matches the sidecar's `last_session.runlabel`; else newest by mtime. Zero matches for a **required** artifact ⇒ the gate fails (the phase cannot begin). The sidecar at the project root is itself an `artifact_key` and the index of record.

## `validate.sh gate <phase> <run_folder>` — contract

- **Reads** `execution-gates.v1.json`, looks up `<phase>`.
- For `entry_requires.artifacts`: confirm each resolves to a file.
- For `entry_requires.checks`: resolve each `targets` to files and run `"$0" <validator> <file>...`; collect exit codes.
- **Exit 0** iff every required artifact exists and every check exits 0 (transition permitted); **exit 1** on any missing artifact or failing check (transition blocked, with a per-requirement PASS/FAIL summary); **exit 2** usage.
- **Overrides** are handled at the *validator* level — the individual validators already honor body override markers (e.g. `softness-downgrade`, `severity-floor-*`, `underdiagnosis-trigger-*`) that downgrade ERROR→WARN; `gate` simply respects each validator's exit code, so a properly-marked exception passes the gate without a separate gate-level override. Missing *artifacts* cannot be override-marked (you cannot synthesize without a ledger).
- **`gate --self-test`** runs the gate against bundled fixture run-folders (one that passes, one that fails for a missing lock) — gated in `--self-test-all` (validator count 15 → 16).

## Sidecar state — extend `apodictic.diagnostic-state.v1`

```json
"execution": {
  "phase": "run_synthesis",
  "run_folder": "runs/2026-06-02_opus_full-de",
  "gates": { "run_synthesis": "passed", "run_spot_check": "pending" },
  "allowed_next": ["run_spot_check"]
}
```

Increment 1: `gate` *reads* `run_folder`/`phase` and *reports*; the model updates `execution` after a passing gate. Increment 2: `gate` writes it. `/start` resume uses `phase` + `allowed_next` (a superset of today's `next_action.key`).

## Prose rewrite (run-core.md / run-synthesis.md)

- Pre-synthesis gate → "**Do not begin synthesis until `validate.sh gate run_synthesis <run_folder>` exits 0.**" (replaces the per-item pre-synthesis checklist; the manifest is the list).
- Step 10/12/13 (pre-output + sections + tone) → "**Do not deliver until `validate.sh gate run_spot_check <run_folder>` exits 0.**"
- The individual `validate.sh <validator>` invocations stay valid (the gate calls them); the prose stops enumerating them and points at the gate + manifest as the single source.

## Degradation (no-shell hosts)

When shell/python is unavailable, `gate` cannot run. The prose instructs the model to: read the manifest for the phase, perform the equivalent inline checks, and **record a blind spot** in the sidecar `execution.gates[<phase>] = "attested"` plus an Audit Invocation Log line — never silently skip. This mirrors the existing "or the equivalent inline check on hosts without shell execution" pattern.

## Increment 1 build plan (for the follow-up, once this spec is approved)

1. `schemas/execution-gates.v1.json` (+ schema-load support in `apodictic_artifacts.py` is already generic).
2. `validate.sh gate <phase> <run_folder>` arm + `gate --self-test`; add `gate` to `--self-test-all` (15 → 16) and the count strings/usage/docblock.
3. `test_fixtures/run_folder_pass/` and `run_folder_fail_missing_lock/` for the self-test.
4. Extend `apodictic.diagnostic-state.v1` (+ template) with the `execution` block.
5. Rewrite the two gate sites in `run-synthesis.md` (+ the pre-synthesis gate in `run-core.md`) to call `gate`.
6. Regenerate mirrors; `--check-all`, builds, `release-verify`.

## Out of scope here (later increments)

- **Increment 3 — finding-ID lifecycle states** (`locked` → `delivered` → `revised`) tracked in `execution`/`findings[]`, so the runner can assert "every locked finding was delivered or marked."
- **Increment 4 — external orchestrator.** Increment 1 is still cooperative (the model chooses to run `gate`). True enforcement needs a host (the Agent SDK or a wrapper) that drives phase transitions and invokes `gate` itself between phases — a larger, different effort that leaves the "plugin runs inside the model" model. Specced separately if/when increments 1–3 show residual skipped-gate incidents.

## Open questions

- **Run-folder discovery.** Should `gate` take `<run_folder>` explicitly (simplest, proposed) or read it from the sidecar? Proposed: explicit arg, default to the sidecar's `run_folder` when omitted.
- **Audit gate.** `run_audits` entry conditions are contract/finding-driven (not a fixed artifact set); model judgment likely stays here in increment 1, with the manifest covering only the deterministic `run_synthesis` / `run_spot_check` gates.
- **Where the manifest lives.** `schemas/` (proposed — it is a contract) vs. `references/`. If `schemas/`, it is data, not a JSON-Schema document; the `$id` convention should make that clear (`execution-gates`, not `*.schema.json`).
