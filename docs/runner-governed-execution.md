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
| **State vs. history** | **History-only.** A new append-only `execution.gate_events[]` is the canonical record. The per-phase `gates` map is **removed** — fully derivable from the log (the redundant, drift-prone duplication). |
| **Event identity** | A gate event names the **`gate`** it records, enum = the manifest's `phases` keys (today `run_synthesis`, `run_spot_check`) — *the gates the runner can actually execute*, not the full 9-key `next_action` dispatch set. Gate identity ≠ workflow phase (see *Gate identity vs. workflow phase* below). |
| **Status vocabulary** | A **lifecycle vocabulary**, split into *stored event results* and *derived labels* (table below). Enum-tightened — Track C's deferral was pending exactly this design. |
| **`allowed_next` placement** | **Derived runner state**, not per-event — a pure function of the manifest + cleared frontier; duplicating it per event invites drift. Lives once, on the thin resume pointer. |
| **Degrade path** | **Minimal required fields; ordering = array append position (no monotonic `seq` for a model to compute).** The no-shell path appends one flat, hand-authorable event. |

#### Gate identity vs. workflow phase (review fix — Codex P1)

The first draft set the event's identity field to the full `next_action` dispatch enum (`intake … handoff_reentry`). That conflated two different things and was wrong: the **runner can only execute the gates the manifest defines** — today exactly `run_synthesis` and `run_spot_check` (`execution-gates.v1.json` → `phases`), and `run_gate.py` rejects any other phase with exit 2. An event keyed `deliver` or `coaching` would name a gate the engine cannot run, and would pretend non-gated workflow steps are gate decisions. So the spec separates the two axes:

- **`gate`** (the event's identity) — enum = manifest `phases` keys. A gate event records a decision about a gate the runner can execute. Non-gated workflow steps (`intake`, `run_passes`, `deliver`, `revision_round`, `coaching`, `handoff_reentry`) **do not** produce gate events — there is no gate to record; their progress is tracked as today (artifact presence + `next_action` in `/start`), not in this log.
- **`execution.phase`** (the resume pointer) — the **gate frontier**: the last gate that cleanly passed. Unchanged from today (`run_gate.py` only ever sets `execution.phase` to a manifest gate key), drawing from the same small gate set — so the two axes stay consistent, and neither spans the 9-key dispatch set.

The gate set is **sourced from the manifest**, so adding a future gate is one manifest entry + the enum (a consistency check asserts `gate_event` enum == manifest `phases` keys ⊆ dispatch keys). Generalizing the log to *all* workflow phases — every dispatch phase with defined transition semantics — is the larger Increment-4 manifest expansion, explicitly out of scope here.

### Status vocabulary — stored events vs. derived labels

Every lifecycle state is either a **stored event** (something that happened at a point in time — append-only) or a **derived label** (a view computed by folding the log — never written, so the log is never mutated):

| State | Kind | Notes |
|---|---|---|
| `passed` | stored event `result` | × `provenance` `mechanical` / `attested`; **clears** a gate only with attestation coverage (see Attestation) |
| `mechanical-passed` | **stored event** `result` | python-path intermediate: mechanical checks green, attestation still owed — **non-clearing** (does not advance the frontier) |
| `pass-with-warn` | stored event `result` | cleared with an unresolved soft warning; does **not** authorize a transition |
| `blocked` | stored event `result` | failed |
| `skipped` | **stored event** `result` | deliberate bypass of a gate — **requires `reason` + an Audit-Invocation-Log blind-spot line** |
| `deferred` | **stored event** `result` | gate postponed to a later session — **requires `reason`**, optional `until` |
| `not-run` | **derived label** | no events for the gate (do not write a "nothing happened" event) |
| `superseded` | **derived label** | a later event shares the gate — never mutate the prior event |
| `current` | **derived label** | the gate frontier — `execution.phase` |

`skipped` / `deferred` are the genuinely *new stored* states (the audit value). Guardrail against a silent-bypass honeypot: they require a recorded `reason` (and `skipped` a blind-spot line), and `gate --strict` / CI returns nonzero while any gate has an **open exception** (formalized below) — so the bypass is recorded and CI-blockable, never silent. `provenance` (mechanical | attested) is an orthogonal axis on any cleared event: an *attested pass* is `result: passed` + `provenance: attested` (this subsumes the v1 `"attested"` status). `skipped` / `deferred` are always `provenance: attested` (a human/model decision, never a mechanical outcome).

### The event record — `apodictic.gate_event.v1`

A **standalone** schema file `apodictic.gate_event.v1.schema.json`, referenced from the diagnostic-state schema as `"gate_events": {"type": "array", "items": {"$schema_ref": "apodictic.gate_event.v1"}}` — the **same `items.$schema_ref` extension** that already documents `findings[]` / `audit_triggers[]` / `readiness[]`. *(This corrects the first draft's "inline, no `$ref`, the checker may not support it": `$schema_ref` is the project's established stdlib extension for arrays of typed objects. It is **not** auto-validated "for free" here, though — `gate_events` is nested under `execution`, which the top-level `validate_sidecar_obj` walker does not reach, so per-item structural validation is driven by `gate-state` calling the shared `validate_obj`; see Enforcement.)* Events live in the sidecar JSON only — there is no markdown-embedded gate-event block.

| Field | Required? | Type / values | Notes |
|---|---|---|---|
| `gate` | **required** | enum = manifest `phases` keys | which gate this event records |
| `result` | **required** | `passed` \| `mechanical-passed` \| `pass-with-warn` \| `blocked` \| `skipped` \| `deferred` | the outcome (`mechanical-passed` is the python-path "attestation owed" intermediate) |
| `provenance` | **required** | `mechanical` \| `attested` | how decided; `skipped` / `deferred` are always `attested` |
| `ts` | **required** | ISO-8601 string | informational/ordering aid; day-granularity acceptable on the degrade path |
| `reason` | **required iff** `result ∈ {skipped, deferred}` | string | the exception rationale (enforced by `gate-state`, not the subset schema) |
| `until` | optional | string | for `deferred`: when it is expected to resume |
| `run_folder` | optional | string | the run folder the gate ran against |
| `checks` | optional (python-only) | `[{"validator": str, "result": "ok"\|"warn"\|"error"}]` | per-validator breakdown |
| `attested_items` | optional* | string[] | confirmed attested-checklist **IDs** (from the manifest `attested[*].id`). *\*Must cover the gate's checklist for a **clearing** `passed` when that list is non-empty (see Attestation); enforced by `gate-state`.* |
| `attested_snapshots` | optional | `{id: text}` | point-in-time text of each confirmed item, so a later manifest re-wording doesn't rewrite history |
| `finding_deltas` | optional (python-only) | `{finding_id: state}` | finding-lifecycle advances this event made |
| `migrated` | optional | boolean | seeded from the legacy `gates` map (see Migration) |
| `note` | optional | string | free text |

**Ordering is array append position** (the array *is* the order); `ts` is advisory and may be coarse on the degrade path. There is no `seq` counter for a model to maintain. **Required minimum** (degrade-path hand-authorable): `gate`, `result`, `provenance`, `ts` (+ `reason` when skipped/deferred).

```jsonc
// engine-written event (full)
{
  "gate": "run_spot_check",
  "result": "pass-with-warn",
  "provenance": "mechanical",
  "ts": "2026-06-03T14:22:00Z",
  "run_folder": "runs/2026-06-02_opus_full-de",
  "checks": [
    {"validator": "softness-check", "result": "warn"},
    {"validator": "tone-check",     "result": "ok"}
  ],
  "finding_deltas": {"F-P5-01": "delivered"},
  "note": "softness WARN on F-P5-01; re-word before deliver"
}
```

```jsonc
// degrade-path event (no shell) — one flat, copy-pasteable combined clearing pass.
// attested_items are the manifest IDs; the optional snapshot records the text confirmed.
{"gate":"run_synthesis","result":"passed","provenance":"attested","ts":"2026-06-03",
 "attested_items":["syn-a1","syn-a2","syn-a3"],
 "attested_snapshots":{"syn-a3":"every deferred/declined high-risk audit is recorded as a blind spot"},
 "note":"no shell; inline checks"}
```

### Attestation is part of a clean pass (review fix — Codex P1)

The manifest's `entry_requires.attested` lists are non-mechanical preconditions the gate cannot check by running a validator — *"all selected Tier-2 passes are complete," "every deferred high-risk audit is recorded as a blind spot,"* etc. The v1 prose makes confirming them a hard precondition for transitioning, even though the gate's exit code reflects only the mechanical half. If a `passed` event advanced the frontier on `result == "passed"` alone (with `attested_items` merely optional), it would re-create the exact failure this whole track exists to prevent: *the model says the gate passed, but only the mechanical half did.*

So attestation is folded into the definition of a **clearing pass**, with a deterministic coverage contract and an explicit two-step handshake.

**Deterministic coverage by stable IDs (review fix — Codex P2).** The manifest `attested` entries become `{id, text}` objects with author-assigned stable IDs (e.g. `syn-a1 … syn-a3`, `spot-a1 …`) instead of bare strings — so coverage is a set-inclusion test, not brittle exact-string or fuzzy matching. An event's `attested_items` records the confirmed **IDs**; coverage is `set(event.attested_items) ⊇ set(manifest.phases[gate].attested[*].id)`. (Optionally the event also stores `attested_snapshots` — `{id: text}` of what was confirmed — so a later manifest re-wording doesn't rewrite history.) `gate-state` enforces both the inclusion test and that recorded IDs are a subset of the manifest's current IDs (a stale/renamed-item drift guard).

**The two-step handshake (review fix — Codex P1).** Mechanical success and attestation are recorded as a lifecycle, so "mechanical checks passed, waiting for attestation" is a real, valid event rather than an undefined gap (with the current enum there was no legal event for it):

- `validate.sh gate <gate> <run_folder>` runs the mechanical checks and appends one event reflecting *only* the mechanical outcome: `blocked` (error/missing), `pass-with-warn` (WARN), or — for a gate **with** a non-empty `attested` list — the new non-clearing **`mechanical-passed`** (checks green, attestation still owed). For a gate with **no** attested requirements, mechanical success is a clearing `passed` directly (nothing to attest).
- `validate.sh gate --attest <gate> <run_folder>` is the handshake that records the **clearing `passed`**: the model confirms the printed checklist, and the engine appends one `passed` event carrying `attested_items` (the confirmed IDs), re-asserting the mechanical `checks[]`. Provenance stays `mechanical` (the checks ran mechanically); the `attested_items` carry the judgment half. The forward-only `finding_deltas` ride this clearing event, not the `mechanical-passed` one.
- **Degrade path (no shell)** writes the *combined* clearing `passed` directly — provenance `attested`, `attested_items` covering the checklist — in one event; there is no separate `mechanical-passed` step (the model did the mechanical checks inline). So `mechanical-passed` is a python-path intermediate only.

**Enforcement.** A `passed` event is a **clearing pass** iff its `attested_items` cover the gate's manifest checklist (vacuously true when that checklist is empty). `gate-state` treats a `passed` lacking coverage as a hard error (same standing as a missing required field), and — defensively — the frontier fold and `open_exceptions` (below) count only clearing passes, so even a malformed log cannot advertise an un-attested or mechanical-only gate as cleared.

### Derived current-state — the thin checkable pointer

The log is canonical; the engine also writes a small resume pointer so `/start` and the no-shell path read current state in one glance instead of folding the log every resume. Each field is **recomputable from the log**, so it is an index, not a competing source of truth:

- `execution.phase` — the **gate frontier**: the `gate` of the last event that **clears** — `result == "passed"` *and*, for a gate with manifest `attested` requirements, `attested_items` covering that checklist (see Attestation above). `pass-with-warn` does **not** advance it (soft-block — matches the current engine).
- `execution.allowed_next` — `execution-gates.v1.json` → `phases[execution.phase].allowed_next` when `pending_gate` is absent; **empty whenever `pending_gate` is present** (an open exception exists), matching the v1 engine's retraction of `allowed_next` after any non-passing gate. So `allowed_next` is non-empty ⟺ there is no pending gate — the two pointer fields are complementary, never contradictory.
- `execution.pending_gate` — **(review fix — Codex P1#2)** the gate `/start` must resolve next: the manifest-order-earliest gate whose **latest** event is *not* a clearing pass (`result ∈ {blocked, pass-with-warn, skipped, deferred}`, or a `passed` that fails attestation coverage). **Omitted entirely when there is none** — never written as `null` (the subset validator has no null/union type; see schema plan). Without this field the dropped `gates` map left no signal for *which* gate is in trouble: after `run_synthesis` passes and `run_spot_check` returns `pass-with-warn`, the frontier is still `run_synthesis` and `allowed_next` is empty — so "empty ⇒ re-run `gate <phase>`" would wrongly re-run the *passed* `run_synthesis` instead of the warned `run_spot_check`. `pending_gate` names `run_spot_check`.
- `execution.finding_states` — forward-only fold of every event's `finding_deltas`.
- `execution.state_version` — **(review fix — Codex P3)** integer marking the gate-events model (`2`); absent / `1` = legacy `gates`-map sidecar. Readers branch on it instead of sniffing for `gate_events`.

**Invariant.** A `gate-state` check (and `/start`) asserts `pointer == fold(gate_events)` for `phase`, `allowed_next`, `pending_gate`, and `finding_states`. On mismatch the **log wins** — recompute from the log and note the self-heal. Drift is a *checked invariant*, not a hazard.

**Derived labels** (computed, never stored): `not-run(gate)` = no event for the gate; `superseded(event)` = a later event shares its gate; `current` = the frontier `execution.phase`; `status(gate)` = result+provenance of the gate's latest event (replaces the v1 `gates[gate]` read).

### Open exceptions — the formal resolution rule (review fix — Codex P2#2)

"Unresolved" is load-bearing (it gates strict CI), so define it by a fold, not by vibes. First define a **clearing pass** once, then derive the open set from it. Per gate, take its **latest** event (highest array index for that gate):

```
clearing_pass(e) ≡ e.result == passed ∧ attested_items(e) ⊇ manifest.attested_ids(e.gate)
                   (the coverage test is vacuously true when the gate has no attested items)
open_exceptions   = { gate : latest_event(gate) exists ∧ ¬ clearing_pass(latest_event(gate)) }
```

So a gate is open whenever its latest event is anything other than a clearing pass — that subsumes `blocked`, `pass-with-warn`, `skipped`, `deferred`, the non-clearing `mechanical-passed`, **and** a malformed `passed` that fails attestation coverage. (Review fix — Codex P2: the earlier formal set enumerated only the four bad-result values and silently excluded `mechanical-passed` / un-attested `passed`, contradicting the prose; "not a clearing pass" closes that.)

- A gate's exception is **resolved** exactly when a *later* event for the same gate is a clearing pass — it supersedes the exception. That is the only way to clear `skipped` / `deferred` / `mechanical-passed`: re-running (and, where required, attesting) the gate to a clearing pass. An attested pass counts, so a no-shell host can resolve its own deferral. There is no "mark resolved" event — resolution is always a real clearing pass, which keeps the audit honest.
- `gate --strict` / CI: nonzero while `open_exceptions` is non-empty. `blocked` is already a hard failure; `skipped` / `deferred` / `pass-with-warn` / `mechanical-passed` are the *soft* exceptions this mode refuses to ship unresolved. So strict CI is red until every gate's latest event is a clearing pass — it neither stays red forever (a clearing re-pass clears it) nor clears casually (only a real clearing pass clears it).
- `execution.pending_gate` = the manifest-order-earliest member of `open_exceptions` (resolve first); **omitted when `open_exceptions` is empty** (never `null`).

### `/start` read changes

- Read the pointer. **If `pending_gate` is set, resolve *that* gate** — *not* `execution.phase` (Review fix — Codex P1#2: the v1 "empty `allowed_next` ⇒ re-run `gate <phase>`" re-ran the last *passed* gate). The resolution depends on the gate's latest result: `mechanical-passed` ⇒ confirm the checklist via `validate.sh gate --attest <pending_gate> <run_folder>`; anything else ⇒ re-run `validate.sh gate <pending_gate> <run_folder>` (or, on a no-shell host, author the combined clearing event inline).
- Else proceed along `allowed_next` from the frontier.
- For per-gate status display, fold `gate_events[]` → `status(gate)` (cheap; a run has a handful of events).
- Optionally assert the pointer against the fold and self-heal (log wins).
- **Legacy fallback:** `state_version` absent / `1` (no `gate_events`) ⇒ read the v1 `gates` map, so old projects still resume.

### Enforcement — structural reuse vs. `gate-state` semantics (review fix — Codex P2/P3)

The subset checker exposes a reusable **per-object** validator, `apodictic_artifacts.validate_obj`, honoring `required` / `const` / `enum` / `type` / `minItems` / item-`type` / `pattern`. Enforcement is two layers with a clean split:

- **Structural (reuse `validate_obj` per item).** `gate-state` **iterates `execution.gate_events[]` itself and calls the shared `validate_obj(item, apodictic.gate_event.v1)` per element** — giving the unconditional required minimum (`gate`, `result`, `provenance`, `ts`), the `result` / `provenance` / `gate` **enums**, and field **types** from the one shared validator (same engine that checks finding blocks). *(Correction — Codex P2: this is **not** "for free" via `validate_sidecar_obj`. That helper's `array_item_schemas` discovers only **top-level** sidecar arrays from the schema's `properties`; `gate_events` is nested under `execution`, so the existing walker won't reach it. The structural layer therefore reuses `validate_obj` but `gate-state` owns the iteration — or, alternatively, the shared walker is extended to recurse one level into `execution`. The first is lower-risk and self-contained; the build plan takes it.)*
- **Semantic (new `gate-state` Python validator).** `validate_obj` has **no conditional-required, no cross-field rules, no null/union types, and does not recurse into nested array-objects or object-map values** — so `gate-state` owns everything the subset checker cannot express, each with positive + negative fixtures (mirroring the `run_gate.py` / `apodictic_artifacts.py` self-test style):
  - **attestation coverage (Codex P1/P2):** a `passed` event on a gate with a non-empty manifest `attested` list must have `attested_items` whose **ID set ⊇ the manifest's `attested[*].id`** (deterministic inclusion, not string matching) — else it is not a clearing pass (hard error); plus the **drift guard** that recorded IDs are a subset of the manifest's *current* IDs (catches stale/renamed items);
  - `reason` **required iff** `result ∈ {skipped, deferred}`;
  - `provenance == attested` whenever `result ∈ {skipped, deferred}`;
  - the Audit-Invocation-Log **blind-spot line** exists for each `skipped`;
  - **inner shapes (Codex P3):** each `checks[]` element is `{validator: str, result ∈ {ok, warn, error}}`, and every `finding_deltas` value is a lifecycle state (`locked` / `delivered` / `revised`) on a finding-ID key — neither is reachable by the subset schema;
  - `pointer == fold(gate_events)` (phase / allowed_next / pending_gate / finding_states);
  - the `open_exceptions` computation behind `gate --strict`;
  - `gate` enum == manifest `phases` keys ⊆ dispatch keys (drift guard).

### Migration / backward-compat (no schema version bump)

Adding `gate_events` (plus `pending_gate` / `state_version`) is additive, and the sidecar schema is `additionalProperties: true`; deprecating `gates` (kept optional for back-compat reads) is non-breaking — so `apodictic.diagnostic-state.v1` stays **v1**. `state_version` is the *internal* model marker (distinct from the schema `$id`) Codex suggested.

- **Schema:** add `gate_events` (`items.$schema_ref: apodictic.gate_event.v1`, documenting the item shape), `pending_gate` (`{"type": "string"}` — present only when a gate is pending, **omitted otherwise**; no `null`, which the subset validator can't type), `state_version` (integer) to the `execution` block; ship `apodictic.gate_event.v1.schema.json`. Keep `execution.gates` as `{"type": "object"}` with `$comment: deprecated by gate_events; read only when state_version < 2`. (Per-item validation is driven by `gate-state` calling `validate_obj`, since `gate_events` is nested under `execution` — see Enforcement.)
- **Reader rule:** `state_version >= 2` ⇒ use `gate_events`; else fall back to the legacy `gates` map.
- **Writer rule (Increment-5 engine):** first write sets `state_version: 2`, creates `gate_events[]`, and stops writing the `gates` map. Migration seeding is **faithful, not blanket-attested** (review fix — Codex P3): seed one event per legacy `gates` entry mapping the recorded value to its *real* provenance — legacy `"attested"` → `{result: passed, provenance: attested}`; legacy `passed` / `pass-with-warn` / `blocked` (all engine-written) → that result with `provenance: mechanical` — each flagged `"migrated": true`, `note: "migrated from legacy gates map"`, coarse `ts`. (The earlier draft's blanket `provenance: attested` would have mislabeled mechanically-written results as model-attested.) Seeding is recommended for history continuity but optional; the conservative alternative is no seed (history starts at the first Increment-5 gate run).

### Build plan (later increment — not this round)

1. Ship `apodictic.gate_event.v1.schema.json`; add `gate_events` (`items.$schema_ref`), `pending_gate`, `state_version` to the `execution` block of `apodictic.diagnostic-state.v1`; deprecate `gates`. The structural layer is `gate-state` iterating `execution.gate_events[]` and calling the shared `validate_obj` per item (the array is nested under `execution`, so `validate_sidecar_obj`'s top-level walker won't reach it — or extend that walker; the proposal takes the iterate-in-`gate-state` route).
2. **Manifest:** change `execution-gates.v1.json` `entry_requires.attested` from bare strings to `{id, text}` objects with stable IDs (Codex P2); update `run_gate.py` to print the `text` and record the `id`s. (The manifest is data, not a versioned schema, so this is a localized format change.)
3. `run_gate.py`: **append** an event per run instead of overwriting `gates[<phase>]`; recompute the pointer (`phase`, `allowed_next`, `pending_gate`, `finding_states`) from the log; set `state_version: 2`. **Attestation handshake (Codex P1):** mechanical success on a gate with attested items writes the non-clearing **`mechanical-passed`**; a new `gate --attest <gate> <run_folder>` records the clearing `passed` with the confirmed `attested_items` (and the mechanical `checks[]`); `finding_deltas` ride the clearing event. Gates with no attested items clear directly on mechanical success. Author `skipped` / `deferred` events (required `reason` + Audit-Invocation-Log blind-spot); add `gate --strict` (nonzero while `open_exceptions` is non-empty).
4. New **`gate-state`** validator (its own arm, or `run_gate.py --check-state <sidecar>`) owning the semantic invariants listed under *Enforcement* — attestation coverage by ID-set inclusion + manifest-ID drift guard, conditional `reason`, provenance constraints, blind-spot presence, `checks[]` / `finding_deltas` inner shapes, the pointer/fold invariant, `open_exceptions` (= "latest event is not a clearing pass"), and the enum drift guard — each with positive + negative fixtures. Register in `--self-test-all` (17 → 18; bump the count strings + usage + docblocks in lockstep).
5. `commands/start.md`: resolve `pending_gate` first, else proceed along `allowed_next`; per-gate status via fold; `state_version` legacy fallback; the self-heal note.
6. Degrade-path prose (run-core.md / run-synthesis.md §Degradation): append one combined clearing `passed` (provenance `attested`, `attested_items` covering the checklist) + update the pointer (`phase`, `allowed_next`, `pending_gate`) — replacing the v1 one-word `gates[<phase>] = "attested"`.
7. Migration: faithful seeding from any legacy `gates` map; reader keys off `state_version`.
8. Regenerate `codex/` + `antigravity/` mirrors; `--check-all`, `build-*.mjs --check`, `release-verify`.

### Out of scope

- **Increment 4 (external orchestrator).** Events are still written cooperatively by the model/engine; nothing here makes the host *drive* phase transitions.
- **Markdown-embedded gate-event carriers.** Events live in the sidecar JSON only.
- **Code.** This round is the spec; no implementation lands until the build increment above is scheduled.

## Open questions

- **Run-folder discovery.** Should `gate` take `<run_folder>` explicitly (simplest, proposed) or read it from the sidecar? Proposed: explicit arg, default to the sidecar's `run_folder` when omitted.
- **Audit gate.** `run_audits` entry conditions are contract/finding-driven (not a fixed artifact set); model judgment likely stays here in increment 1, with the manifest covering only the deterministic `run_synthesis` / `run_spot_check` gates.
- **Where the manifest lives.** `schemas/` (proposed — it is a contract) vs. `references/`. If `schemas/`, it is data, not a JSON-Schema document; the `$id` convention should make that clear (`execution-gates`, not `*.schema.json`).
