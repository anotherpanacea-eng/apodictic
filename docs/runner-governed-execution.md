# Runner-Governed Execution — Design Spec

**Status:** increments **1–3 built** (cooperative gate manifest + engine + sidecar state + finding-ID lifecycle); increment **4** (external host orchestrator) remains future. Roadmap: `ROADMAP.md` → Harness Engineering → Runner-Governed Execution. Implementation: `plugins/apodictic/schemas/execution-gates.v1.json`, `scripts/run_gate.py`, `validate.sh gate`.

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
          {"validator": "ledger-check",          "targets": ["findings_ledger"]},
          {"validator": "ledger-consolidation",  "targets": ["findings_ledger"]},
          {"validator": "structured-findings",   "targets": ["findings_ledger"]},
          {"validator": "deficit-lock",          "targets": ["findings_ledger"]},
          {"validator": "artifact-names",        "targets": ["run_folder", "$project", "$runlabel"]}
        ],
        "attested": [
          "all selected Tier-2 passes are complete and appended to the ledger",
          "all auto-run audits (per contract + constraint flags) are complete and in the ledger",
          "every deferred/declined high-risk audit is recorded as an explicit blind spot"
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
        ],
        "attested": [
          "each root cause cites >= 1 specific ledger finding (findings integration)",
          "root-cause / revision-checklist / must-fix caps are within limits (cap compliance)",
          "every deferred/declined high-risk audit is named where it limits confidence or readiness (blind-spot disclosure)"
        ]
      },
      "allowed_next": ["deliver"]
    }
  }
}
```

`checks[].targets` is an ordered list of artifact keys → the file arguments passed to the validator (so `softness-check <letter> <ledger>` is expressible). The reserved keys `run_folder`, `$project`, and `$runlabel` pass the run-folder path and the project / runlabel derived from the findings-ledger filename (used by `artifact-names <dir> <project> <runlabel>`). Phases not listed have no mechanical entry gate.

**Mechanical vs. attested — the gate does not claim to replace human judgment.** `entry_requires.checks` are validator-backed and run by `gate`. `entry_requires.attested` are preconditions that are **contract-driven or judgment-based and have no validator** — selected-pass / auto-run-audit completeness and blind-spot recording (pre-synthesis), and findings-integration / cap-compliance / blind-spot disclosure (pre-delivery). The gate cannot verify these mechanically; it prints them as a required checklist the model must confirm. Naming them in the manifest is the point: it keeps the gate from *silently narrowing* the existing pre-synthesis / Step-10 gates to only their mechanical subset.

## Artifact resolution

`gate` resolves each `artifact_key` to a file by globbing `<run_folder>` with the pattern(s) from `artifact_keys` (the `output-structure.md` naming conventions). Disambiguation when multiple runlabels are present: prefer the file whose `runlabel` matches the sidecar's `last_session.runlabel`; else newest by mtime. Zero matches for a **required** artifact ⇒ the gate fails (the phase cannot begin). The sidecar at the project root is itself an `artifact_key` and the index of record.

## `validate.sh gate <phase> <run_folder>` — contract

- **Reads** `execution-gates.v1.json`, looks up `<phase>`.
- For `entry_requires.artifacts`: confirm each resolves to a file.
- For `entry_requires.checks`: resolve each `targets` to files and run `"$0" <validator> <file>...`; collect exit codes.
- For each check `gate` captures **both the exit code and stdout** (not exit code alone — a validator can exit 0 while printing a WARN-level blocker).
  - **ERROR** (exit 1) or a **missing required artifact** ⇒ hard block; `gate` exits 1 with a per-requirement PASS/FAIL summary.
  - **WARN** (exit 0 with a `WARN` line — e.g. `softness-check` on a hedged-but-delivered locked finding, which is intentionally exit-0-with-WARN *and* a softness trigger per `run-synthesis.md` Step 9) ⇒ **soft block**: by default `gate` prints `GATE-WARN` and exits 0, and the prose requires the model to resolve the warning (re-word / upgrade) or record an acknowledgment before transitioning — the same discipline as the underdiagnosis retry loop. `gate --strict-warnings` promotes any WARN to a hard block (exit 1) for release/CI use.
- **Attested requirements** (`entry_requires.attested`): `gate` prints them as a required checklist; the model confirms each and records the confirmed items in **`execution.attested[<phase>]`** (a list) — separate from `execution.gates[<phase>]`, which the gate owns as the mechanical result string and would overwrite. The gate preserves `execution.attested`. The gate's exit code reflects only the mechanical checks — the prose makes the attested confirmations a hard precondition (un-attested ⇒ do not transition).
- **Overrides** ride the *validator* level — body markers (`softness-downgrade`, `severity-floor-*`, `underdiagnosis-trigger-*`) downgrade a validator's ERROR→WARN, so a properly-marked exception passes (or soft-warns) the gate without a separate gate-level override. Missing *artifacts* cannot be override-marked (you cannot synthesize without a ledger).
- **`gate --self-test`** runs against bundled fixture run-folders (pass; fail-on-missing-lock; warn-on-hedged-delivery) — gated in `--self-test-all` (validator count 15 → 16).

## Sidecar state — extend `apodictic.diagnostic-state.v1`

```json
"execution": {
  "phase": "run_synthesis",
  "run_folder": "runs/2026-06-02_opus_full-de",
  "gates": { "run_synthesis": "passed", "run_spot_check": "pending" },
  "allowed_next": ["run_spot_check"]
}
```

**Increment 2 (built):** `gate` *writes* this block — `gates[<phase>]` = result, plus `phase` + `allowed_next` on a pass — by walking up from the run folder to the project-root sidecar. **Increment 3 (built):** a passing gate also advances `finding_states` (`finding_id` → `locked`/`delivered`, forward-only) from the ledger's `apodictic.finding` IDs. `--no-write` disables the write. `/start` resume uses `phase` + `allowed_next` (a superset of today's `next_action.key`).

## Prose rewrite (run-core.md / run-synthesis.md)

- Pre-synthesis gate → "**Do not begin synthesis until `validate.sh gate run_synthesis <run_folder>` exits 0 AND every `attested` item is confirmed.**" The gate replaces the *mechanical* pre-synthesis checklist; the contract-driven completeness checks (selected passes, auto-run audits, blind-spot recording) remain as `attested` items named in the manifest so they are not dropped.
- Step 10/12/13 (pre-output + sections + tone) → "**Do not deliver until `validate.sh gate run_spot_check <run_folder>` exits 0, no `GATE-WARN` is left unresolved, and every `attested` item is confirmed.**" The non-validator Step 10 checks (findings integration, cap compliance, blind-spot disclosure) are the `attested` items.
- The individual `validate.sh <validator>` invocations stay valid (the gate calls them); the prose stops enumerating the *mechanical* checks (the manifest is the list) but keeps the attested checklist explicit.

## Degradation (no-shell hosts)

When shell/python is unavailable, `gate` cannot run. The prose instructs the model to: read the manifest for the phase, perform the equivalent inline checks, and **record a blind spot** — set `execution.gates[<phase>] = "attested"` (checks done inline) and list the confirmed items in `execution.attested[<phase>]`, plus an Audit Invocation Log line — never silently skip. This mirrors the existing "or the equivalent inline check on hosts without shell execution" pattern.

## Increment 1 build plan (for the follow-up, once this spec is approved)

1. `schemas/execution-gates.v1.json` (+ schema-load support in `apodictic_artifacts.py` is already generic).
2. `validate.sh gate <phase> <run_folder>` arm + `gate --self-test`; add `gate` to `--self-test-all` (15 → 16) and the count strings/usage/docblock.
3. `test_fixtures/run_folder_pass/` and `run_folder_fail_missing_lock/` for the self-test.
4. Extend `apodictic.diagnostic-state.v1` (+ template) with the `execution` block.
5. Rewrite the two gate sites in `run-synthesis.md` (+ the pre-synthesis gate in `run-core.md`) to call `gate`.
6. Regenerate mirrors; `--check-all`, builds, `release-verify`.

## Later increments

- **Increment 3 — finding-ID lifecycle states (built).** `execution.finding_states` maps each finding ID to `locked` (set by `gate run_synthesis`) → `delivered` (set by `gate run_spot_check`), forward-only. The `revised` state awaits a gated `revision_round` phase (not yet defined). `softness-check` already *enforces* delivery; `finding_states` is the auditable trail.
- **Increment 4 — external orchestrator (future).** Increments 1–3 are still cooperative (the model chooses to run `gate`; it writes state but does not *block* the process). True enforcement needs a host (the Agent SDK or a wrapper) that drives phase transitions and invokes `gate` itself between phases — a larger effort that leaves the "plugin runs inside the model" model. Revisit if increments 1–3 show residual skipped-gate incidents.

## Open questions

- **Run-folder discovery.** Should `gate` take `<run_folder>` explicitly (simplest, proposed) or read it from the sidecar? Proposed: explicit arg, default to the sidecar's `run_folder` when omitted.
- **Audit gate.** `run_audits` entry conditions are contract/finding-driven (not a fixed artifact set); model judgment likely stays here in increment 1, with the manifest covering only the deterministic `run_synthesis` / `run_spot_check` gates.
- **Where the manifest lives.** `schemas/` (proposed — it is a contract) vs. `references/`. If `schemas/`, it is data, not a JSON-Schema document; the `$id` convention should make that clear (`execution-gates`, not `*.schema.json`).
