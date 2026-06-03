# Runner-Governed Execution — Design Spec

**Status:** increments **1–3 built** (cooperative gate manifest + engine + sidecar state + finding-ID lifecycle); increment **4** (external host orchestrator) remains future; increment **5** (structured gate-event records) is **designed (§Increment 5 below), not yet built**. Roadmap: `ROADMAP.md` → Harness Engineering → Runner-Governed Execution. Implementation: `plugins/apodictic/schemas/execution-gates.v1.json`, `scripts/run_gate.py`, `validate.sh gate`.

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
- **Increment 5 — structured gate-event records (designed; build pending).** The v1 `execution.gates` map is current-state-only and lossy, and Validator Architecture Hardening Track C deliberately left it unschema'd *until this track designed a real per-event record* ("option 2, after design"). That design is now complete — see **§Increment 5 — Structured gate-event records (design spec)** below. The current round is **spec-only**; the build is a later increment.

## Increment 5 — Structured gate-event records (design spec)

> **Status:** designed, not built. Scope this round is the spec; the build plan is at the end of this section. Track C of Validator Architecture Hardening deliberately left `execution.gates` unschema'd "until this track takes it up with a real design" — this is that design.

### Problem with the v1 shape

`execution.gates[<phase>]` is a bare status string and the schema types it as an untyped `object`. It is **current-state-only** and **lossy**: a gate that failed, got fixed, and re-passed leaves only `passed` — the retry is invisible. There is no auditable record of *when* each gate ran, *how* it was decided (mechanically vs. attested inline on a no-shell host), or *why* an exception was taken. The runner-governed track exists precisely because gates get skipped under context pressure and fire differently across models; an append-only record of gate decisions is the missing audit trail.

### Decisions (the five runner-owned questions)

| Question | Decision |
|---|---|
| **State vs. history** | **History-only.** A new append-only `execution.gate_events[]` is the canonical record. The per-phase `gates` map is **removed** — it is fully derivable from the log (the redundant, drift-prone duplication). |
| **Phase identity** | **Fixed enum** = the `next_action` dispatch keys (`intake … handoff_reentry`, the same set `/start` routes on). Not free strings (a typo'd phase should be invalid, not silently logged), not a new namespace (there is one runner). |
| **Status vocabulary** | A **lifecycle vocabulary**, split into *stored event results* and *derived labels* (table below). Now enum-tightened — Track C's deferral was pending exactly this design. |
| **`allowed_next` placement** | **Derived runner state**, not per-event. It is a pure function of the manifest + current phase; duplicating it per event invites drift. It lives once, on the thin resume pointer. |
| **Degrade path** | **Minimal required fields; ordering = array append position (no monotonic `seq` for a model to compute).** The no-shell path appends one flat, hand-authorable event. |

### Status vocabulary — stored events vs. derived labels

Every lifecycle state is either a **stored event** (something that happened at a point in time — append-only) or a **derived label** (a view computed by folding the log — never written, so the log is never mutated):

| State | Kind | Notes |
|---|---|---|
| `passed` | stored event `result` | × `provenance` `mechanical` / `attested` |
| `pass-with-warn` | stored event `result` | cleared with an unresolved soft warning; does **not** authorize a transition |
| `blocked` | stored event `result` | failed |
| `skipped` | **stored event** `result` | deliberate bypass — **requires `reason` + an Audit-Invocation-Log blind-spot line** |
| `deferred` | **stored event** `result` | postponed to a later session — **requires `reason`**, optional `until` |
| `not-run` | **derived label** | no events for the phase (do not write a "nothing happened" event) |
| `superseded` | **derived label** | a later event shares the phase — never mutate the prior event |
| `current` | **derived label** | the phase of the latest cleared (`passed`) event |

`skipped` / `deferred` are the genuinely *new stored* states (the audit value). The guardrail against a silent-bypass honeypot: they require a recorded `reason` (and `skipped` a blind-spot line), and a `gate --strict` / CI mode returns nonzero if the log carries any unresolved `skipped` / `deferred` / `pass-with-warn` — so the exception is recorded and CI-blockable, never silent. `provenance` (mechanical | attested) is an orthogonal axis on any cleared event: an *attested pass* is `result: passed` + `provenance: attested` (this subsumes the v1 `"attested"` status).

### The event record — `apodictic.gate_event.v1`

Inlined under `execution.gate_events.items` in `apodictic.diagnostic-state.v1` (no cross-file `$ref` — the stdlib JSON-Schema subset checker may not support it; one home, no new carrier). Events live in the sidecar JSON only — there is no markdown-embedded gate-event block.

| Field | Required? | Type / values | Notes |
|---|---|---|---|
| `phase` | **required** | enum (dispatch keys) | which phase's gate this event records |
| `result` | **required** | `passed` \| `pass-with-warn` \| `blocked` \| `skipped` \| `deferred` | the outcome |
| `provenance` | **required** | `mechanical` \| `attested` | how decided; `skipped` / `deferred` are always `attested` |
| `ts` | **required** | ISO-8601 string | informational/ordering aid; day-granularity acceptable on the degrade path |
| `reason` | **required iff** `result ∈ {skipped, deferred}` | string | the exception rationale |
| `until` | optional | string | for `deferred`: when it is expected to resume |
| `run_folder` | optional | string | the run folder the gate ran against |
| `checks` | optional (python-only) | `[{"validator": str, "result": "ok"\|"warn"\|"error"}]` | per-validator breakdown |
| `attested_items` | optional | string[] | confirmed attested-checklist items (attested / degrade) |
| `finding_deltas` | optional (python-only) | `{finding_id: state}` | finding-lifecycle advances this event made |
| `note` | optional | string | free text |

**Ordering is array append position** (the array *is* the order); `ts` is advisory and may be coarse on the degrade path. There is no `seq` counter for a model to maintain. **Required minimum** (degrade-path hand-authorable): `phase`, `result`, `provenance`, `ts` (+ `reason` when skipped/deferred).

```jsonc
// engine-written event (full)
{
  "phase": "run_synthesis",
  "result": "pass-with-warn",
  "provenance": "mechanical",
  "ts": "2026-06-03T14:22:00Z",
  "run_folder": "runs/2026-06-02_opus_full-de",
  "checks": [
    {"validator": "ledger-check",   "result": "ok"},
    {"validator": "softness-check", "result": "warn"}
  ],
  "finding_deltas": {"F-P5-01": "locked"},
  "note": "softness WARN on F-P5-01; re-word before deliver"
}
```

```jsonc
// degrade-path event (no shell) — one flat, copy-pasteable object
{"phase":"run_synthesis","result":"passed","provenance":"attested","ts":"2026-06-03",
 "attested_items":["selected passes complete","auto-run audits complete","blind spots recorded"],
 "note":"no shell; inline checks"}
```

### Derived current-state — the thin checkable pointer

The log is canonical; the engine also writes a small resume pointer so `/start` and the no-shell path read current state in one glance instead of folding the log every resume. Each pointer field is **recomputable from the log**, so it is an index, not a competing source of truth:

- `execution.phase` = phase of the last event with `result == "passed"` (mechanical or attested). `pass-with-warn` does **not** advance it (soft-block — matches the current engine).
- `execution.allowed_next` = `execution-gates.v1.json` → `phases[execution.phase].allowed_next`; emptied whenever the latest event for the intended phase did not cleanly pass.
- `execution.finding_states` = forward-only fold of every event's `finding_deltas`.

**Invariant.** A `gate-state` check (and `/start` itself) asserts `pointer == fold(gate_events)`. On mismatch the **log wins** — recompute the pointer from the log and note the self-heal. Drift is therefore a *checked invariant*, not a hazard.

**Derived labels** (computed, never stored): `not-run(phase)` = no event for the phase; `superseded(event)` = a later event shares its phase; `current` = phase of the last `passed` event; `status(phase)` = result+provenance of the last event for the phase (this replaces the v1 `gates[phase]` read).

### `/start` read changes

- Read `execution.phase` + `execution.allowed_next` (the pointer) as today; **empty `allowed_next` ⇒ the current phase is not cleared, re-run `validate.sh gate <phase> <run_folder>`** (the v1 `gates[phase] ∈ {blocked, pass-with-warn}` check is dropped — emptiness already encodes it).
- For per-phase status display, fold `gate_events[]` → `status(phase)` (cheap; a single run has only a handful of events).
- Optionally assert the pointer against the fold and self-heal (log wins).
- **Legacy fallback:** a sidecar with no `gate_events` (pre-Increment-5 project) falls back to the v1 `gates` map, so old projects still resume.

### Migration / backward-compat (no schema version bump)

Adding `execution.gate_events` is additive; deprecating `gates` (kept optional for back-compat reads) is non-breaking — so `apodictic.diagnostic-state.v1` stays **v1**.

- **Schema:** add `execution.gate_events` (array; inline `apodictic.gate_event.v1` item shape). Keep `execution.gates` as `{"type": "object"}` with a `$comment: deprecated by gate_events; readers fall back to it when gate_events is absent`.
- **Reader rule:** `gate_events` present ⇒ use it; absent ⇒ use the legacy `gates` map.
- **Writer rule (Increment-5 engine):** first write creates `gate_events[]` and stops writing the `gates` map. Optionally seed one synthetic `provenance: attested` event per legacy `gates` entry (`note: "migrated from legacy gates map"`, coarse `ts`) so a migrated project's history isn't blank.

### Build plan (later increment — not this round)

1. Extend `apodictic.diagnostic-state.v1`: inline `gate_event.v1` under `execution.gate_events.items`; deprecate `gates`. (Optionally ship a standalone `apodictic.gate_event.v1.schema.json` as documentation kept in sync.)
2. `run_gate.py`: **append** an event per run instead of overwriting `gates[phase]`; recompute the pointer (`phase`, `allowed_next`, `finding_states`) from the log; author `skipped` / `deferred` events (with required `reason` + Audit-Invocation-Log blind-spot) and add `gate --strict` (nonzero on any unresolved `skipped` / `deferred` / `pass-with-warn`).
3. `run_gate.py --check-state <sidecar>` (or a `gate-state` validator arm): conform events to the schema; assert `pointer == fold(log)`; assert the `phase` enum == the dispatch keys. Register in `--self-test-all` (17 → 18; bump the count strings + usage + docblocks in lockstep).
4. `commands/start.md`: read the thin pointer; per-phase status via fold; legacy `gates` fallback; the self-heal note.
5. Degrade-path prose (run-core.md / run-synthesis.md §Degradation): append one minimal event + update the pointer (replaces the v1 one-word `gates[<phase>] = "attested"`).
6. Regenerate `codex/` + `antigravity/` mirrors; `--check-all`, `build-*.mjs --check`, `release-verify`.

### Out of scope

- **Increment 4 (external orchestrator).** Events are still written cooperatively by the model/engine; nothing here makes the host *drive* phase transitions.
- **Markdown-embedded gate-event carriers.** Events live in the sidecar JSON only.
- **Code.** This round is the spec; no implementation lands until the build increment above is scheduled.

## Open questions

- **Run-folder discovery.** Should `gate` take `<run_folder>` explicitly (simplest, proposed) or read it from the sidecar? Proposed: explicit arg, default to the sidecar's `run_folder` when omitted.
- **Audit gate.** `run_audits` entry conditions are contract/finding-driven (not a fixed artifact set); model judgment likely stays here in increment 1, with the manifest covering only the deterministic `run_synthesis` / `run_spot_check` gates.
- **Where the manifest lives.** `schemas/` (proposed — it is a contract) vs. `references/`. If `schemas/`, it is data, not a JSON-Schema document; the `$id` convention should make that clear (`execution-gates`, not `*.schema.json`).
