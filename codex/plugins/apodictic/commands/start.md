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
   - Check for an existing `Diagnostic_State.md` in the active project output context.
   - The active project output context is the manuscript's external output folder, not the plugin repo. Reuse an existing manuscript output folder when one is already in use; otherwise default to an `Outputs/` sibling next to the manuscript.
   - If state exists and the Mode section shows `**Current:** execution`, do NOT run router questions yet. Present:
     - **Check the fix** — reload editor mode and run re-entry delta check on active scene
     - **Keep working** — stay in execution mode on current scene
     - **Start fresh** — continue to full intake router
   - Route by user choice:
     - Check the fix -> follow `../skills/core-editor/references/handoff-protocol.md` §5b re-entry procedure
     - Keep working -> remain in execution mode, stop `apodictic-start` flow
     - Start fresh -> continue to step 2

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
