---
description: Recommended entry point — routes to the right workflow in 2-3 questions
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# apodictic-start — Intake Router + Resume Gate

The recommended entry point for APODICTIC. Routes users in 2-3 questions using the four-axis model (Artifact x Goal x Operator x Constraint), with a mode-aware resume check before routing.

## Required skills

Load `../skills/core-editor/SKILL.md` first (thin orchestrator). Do NOT preload companion skills.

## Required references

- `../skills/core-editor/references/intake-router-runtime.md` — runtime router spec
- `../skills/core-editor/references/handoff-protocol.md` — execution-mode resume behavior

## Procedure

1. **Resume gate (runs before Q1):**
   - Check for existing state in the active project output context. The active project output context is the manuscript's external output folder, not the plugin repo. Reuse an existing manuscript output folder when one is already in use; otherwise default to an `Outputs/` sibling next to the manuscript.
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
     - Keep working -> remain in execution mode, stop `apodictic-start` flow
     - Continue -> load the workflow for the resume target
     - Start fresh -> continue to step 2

### Resume Target

The sidecar's `next_action` field uses an enumerated dispatch key (not free text) to identify the workflow to load on resume. Valid values:

| `next_action` value | Loads | When set |
|---|---|---|
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
11. Pass router output (`artifact`, `goal`, `concern`, `constraints`, `operator`, `gap_flags`) to the routed workflow intake and skip redundant questions.

## Output location

No direct output. `apodictic-start` routes into the selected workflow, which writes artifacts and rolling state files to the active project output context beside the manuscript, never to the plugin repo.
