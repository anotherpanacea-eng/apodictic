---
description: Recommended entry point — routes to the right workflow in 2-3 questions (zero for a resumed project)
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# /start — Intake Router + Resume Gate

The recommended entry point for APODICTIC. On a **cold start** it routes users in 2-3 questions using the four-axis model (Artifact x Goal x Operator x Constraint). For a **bound project** (`/start <project>`) it is state-driven (Step 0.5): it derives the project's lifecycle node and resumes via a two-option prompt — zero intake questions. A mode-aware resume check runs before routing.

## Required skills

Load `../skills/core-editor/SKILL.md` first (thin orchestrator). Do NOT preload companion skills.

## Required references

- `../skills/core-editor/references/intake-router-runtime.md` — runtime router spec
- `../skills/core-editor/references/handoff-protocol.md` — execution-mode resume behavior

## Procedure

### Step 0 — Project binding (runs before the resume gate)

`/start` is project-aware. Binding sets the **active project output context** (per `../skills/core-editor/references/output-structure.md`) to a specific project's root and loads its `Diagnostic_State.md` + `Diagnostic_State.meta.json`, so the resume gate below operates on a *chosen* book rather than whatever folder is underfoot. The registry is the workspace-relative `.apodictic/registry.json` (see `/projects` and `docs/project-addressability.md`).

- **`/start <project>`** — resolve `<project>` against the registry by `id` or title (fuzzy match). If it resolves, bind it. If `<project>` is a filesystem path to a project root, register-then-bind it. If nothing resolves, say so and fall through to cold-start intake.
- **`/start` (no argument)** — locate the workspace registry by walking up from cwd for a `.apodictic/` dir, then branch on registry size:
  - **0 projects** (or no workspace) → cold start: proceed to the resume gate / intake exactly as today.
  - **exactly 1 project** → bind it, then continue to the resume gate.
  - **more than 1** → list projects (title, where each stands, last-touched — the `/projects` view) and ask which to bind; then continue.
- **Cold start is unchanged.** When no project is bound, the resume gate and the full intake router run exactly as before — binding only *adds* the ability to select an existing book; it never gates a new one.

After binding, continue to **Step 0.5** (state-driven dispatch). On cold start, skip to the resume gate (step 1) / full intake.

### Step 0.5 — State-driven dispatch (bound projects; before the resume gate)

For a **bound** project, routing is driven by the project's state, not by re-asking intake. This promotes the `next_action` dispatch (see §Resume Target) from a resume *exception* to the *primary* path:

1. **Contract-hash precondition (scoped).** If the sidecar carries a non-empty `contract_hash`, verify it before any zero-question dispatch: locate the contract via the newest `runs/*/[Project]_Contract_*.md` and run `../scripts/validate.sh contract-check <contract_file> <contract_hash>`. On mismatch (manuscript/contract changed out-of-band), do **not** silently resume — fall to a confirming re-ground or full intake. A pre-contract sidecar (`pre_writing`, or a fresh `diagnosing` with `contract_hash: ""`) has no hash and **skips** this check.
2. **Derive the lifecycle node.** Run `../scripts/validate.sh lifecycle-node <project-root>/Diagnostic_State.meta.json [run_folder]`, or derive inline by the precedence (first match wins): `cold → blocked_gate → execution → pre_writing → submission → revising → diagnosed → diagnosing`.
3. **Dispatch by node** — present a **two-option** prompt, never a bare yes/no:
   - **Resume here** → load the workflow for the node (via §Resume Target / the `next_action` table); artifact and goal are read from the contract + sidecar, so Q1/Q2 are skipped.
   - **Start fresh (full intake)** → drop to the intake router (step 2+), for when the writer's intent changed (a new task on an old book).

   | Node | Resume-here dispatch |
   |---|---|
   | `blocked_gate` | resolve the pending gate first (§Resume Target "Resolve a pending gate first") |
   | `execution` | the execution-mode resume gate below (Check the fix / Keep working) |
   | `pre_writing` | load `../skills/pre-writing-pathway/SKILL.md` |
   | `submission` | submission-readiness (`../skills/core-editor/references/submission-readiness.md`) / triage |
   | `revising` | the stored `next_action` (`revision_round` → `state-lifecycle.md`, or `coaching` → `revision-coach/SKILL.md`) |
   | `diagnosed` | offer `/coach` |
   | `diagnosing` | the stored `next_action` (`run_passes` / `run_synthesis` / `run_audits`) |
   | `cold` | no bound project — run the resume gate / full intake below |

4. A bound project's **overlays** (`ai`, `editor`, …) still come from the Q3 / §6 Table B layer, not from the node.

The execution-mode resume gate (step 1) remains the detailed handler for the `execution` node; cold start runs the full router unchanged.

1. **Resume gate (runs before Q1):**
   - Check for existing state in the active project output context. The active project output context is the project root folder (see `../skills/core-editor/references/output-structure.md` §Folder Architecture), not the plugin repo. Reuse an existing project root when one is already in use. For legacy projects that used an `Outputs/` sibling, treat that folder as the project root.
   - **State detection priority:** Check for `Diagnostic_State.meta.json` first (machine-readable sidecar). If it exists, read it for fast structured routing. If only `Diagnostic_State.md` exists (no sidecar — expected for projects created before v1.7), fall back to parsing the markdown directly: read the Mode section, scan Session History for session count, and check whether Root Causes or Control Questions are populated. This fallback path does not require `state_lines`, `revision_progress`, or `next_action` — present what's available and skip what isn't.
   - **If state exists and mode is `execution`**, do NOT run router questions yet. Present:
     - **Check the fix** — reload editor mode and run re-entry delta check on active scene (from sidecar's `active_scene_scope`, or from the markdown's `Active scene scope` field)
     - **Keep working** — stay in execution mode on current scene
     - **Start fresh** — continue to full intake router
   - **If state exists and mode is `diagnostic`**, present a summary of available state. When the sidecar is available, include: session count, root cause count, revision progress, and the resume target. When falling back to markdown-only, include whatever is parseable (root cause count, pass completion status). Then offer:
     - **Continue** — resume the next logical step (see §Resume Target below)
     - **Start fresh** — continue to full intake router
   - **State gardening check (sidecar only):** If `state_lines` > 500, run state gardening before proceeding (see `../skills/core-editor/references/state-lifecycle.md` §State Gardening Protocol). If 300-500, advise the user that gardening is available. Skip this check when falling back to markdown-only (gardening requires the sidecar to track line counts).
   - Route by user choice:
     - Check the fix -> follow `../skills/core-editor/references/handoff-protocol.md` §5b re-entry procedure
     - Keep working -> remain in execution mode, stop `/start` flow
     - Continue -> load the workflow for the resume target
     - Start fresh -> continue to step 2

### Resume Target

**Runner state (preferred when present).** If the sidecar carries an `execution` block (written by `scripts/validate.sh gate` — Runner-Governed Execution), resume from it. With `state_version >= 2`, `execution.gate_events[]` is the canonical append-only gate log and the rest of the block is a recomputable resume pointer: `execution.phase` is the **gate frontier** (the last gate that cleanly cleared) and `execution.allowed_next` lists the authorized next phases. Load the workflow for the current/next phase via the dispatch table below — the phase keys are the same `next_action` values.

- **Resolve a pending gate first.** If `execution.pending_gate` is present, that gate's latest event is not a clearing pass — resolve **it** (not `execution.phase`) before advancing. If its latest event is `mechanical-passed`, confirm the attested checklist with `validate.sh gate --attest <pending_gate> <run_folder>`; otherwise re-run `validate.sh gate <pending_gate> <run_folder>` (resolving the WARN/ERROR). An empty `execution.allowed_next` always co-occurs with a `pending_gate`.
- **Per-gate status**, when needed, is the latest `gate_events[]` entry for that gate (fold the log); you may also run `validate.sh gate-state <sidecar>` to validate the log and confirm the pointer matches the fold (on drift, the log wins).
- **Legacy fallback.** A sidecar with `state_version` absent/`1` (no `gate_events`) uses the deprecated `execution.gates` map: a phase recorded `blocked`/`pass-with-warn`, or an empty `allowed_next`, means re-run `validate.sh gate <phase> <run_folder>` first.

Fall back to `next_action` (below) when there is no `execution` block (pre-runner projects).

The sidecar's `next_action` field uses an enumerated dispatch key (not free text) to identify the workflow to load on resume. Valid values:

| `next_action` value | Loads | When set |
|---|---|---|
| `pre_writing` | `../skills/pre-writing-pathway/SKILL.md` | Pre-writing project (minimal sidecar); no diagnostic run yet — resume the pathway |
| `run_passes` | `run-core.md` | After intake, before passes begin |
| `run_synthesis` | `run-synthesis.md` | After all passes complete, before synthesis |
| `run_spot_check` | `run-synthesis.md` | After synthesis, before evidence spot-check |
| `deliver` | (none — present editorial letter) | After spot-check complete |
| `revision_round` | `state-lifecycle.md` | After editorial letter delivered, author returns with revised draft |
| `run_audits` | `specialized-audits/SKILL.md` | After core passes, before deferred audits |
| `coaching` | `revision-coach/SKILL.md` | After editorial letter, author requests coaching |
| `handoff_reentry` | `handoff-protocol.md` | After execution mode, author says "back to editor" |

When the sidecar does not exist (markdown fallback), determine the resume target by inspecting the state: if passes are listed but no editorial letter artifact exists, resume target is `run_synthesis`; if an editorial letter exists but no revision round has run, resume target is `revision_round` or `coaching` (ask the user which). If state is ambiguous, ask the user.

The `next_action` field also accepts a human-readable `description` subfield for display purposes (e.g., `"description": "resume Tier 2 passes — Pass 5 next"`), but routing uses only the enumerated key.

2. Read `../skills/core-editor/references/intake-router-runtime.md` in full.
3. Ask **Question 1** (Artifact): "What do you have right now?" using runtime options.
4. If user provides material instead of self-reporting, classify with runtime artifact thresholds.
5. Ask **Question 2** (Goal): use the conditional option set for the selected artifact.
6. Ask **Question 3** (Constraint/Operator modifiers): "Before we start - anything I should know?"
7. If artifact/goal pairing is ambiguous, apply the runtime fallback disambiguator.
8. Route to the target workflow per the runtime route map.
9. Load the routed target only now:
   - Pre-writing route -> load `../skills/pre-writing-pathway/SKILL.md`
   - Development edit route -> load `../skills/core-editor/references/run-core.md`
   - Submission readiness route -> load `../skills/core-editor/references/submission-readiness.md`
   - Submission triage route -> load `../skills/core-editor/references/submission-triage.md`
   - Audit route -> load `../skills/specialized-audits/SKILL.md`
   - Plot coaching route -> load `../skills/plot-architecture/SKILL.md`
10. If route target is a gap, execute the runtime gap-handling protocol (acknowledge, offer closest, name missing coverage).
11. Pass router output (`artifact`, `goal`, `concern`, `base_route`, `forks`, `overlays`, `gap_flags`) to the routed workflow intake and skip redundant questions. (Output contract: `../skills/core-editor/references/intake-router-design.md` §Router output format.)

## Output location

No direct output. `/start` routes into the selected workflow, which writes run artifacts into `runs/` and updates rolling state at the project root per `../skills/core-editor/references/output-structure.md` §Folder Architecture. Never write to the plugin repo.
