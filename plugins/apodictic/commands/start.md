---
description: Recommended entry point — routes to the right workflow in 2-3 questions
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# /start — Intake Router + Resume Gate

The recommended entry point for APODICTIC. Routes users in 2-3 questions using the four-axis model (Artifact x Goal x Operator x Constraint), with a mode-aware resume check before routing.

## Required skills

Load the `core-editor` skill first (thin orchestrator). Do NOT preload companion skills.

## Required references

- `references/intake-router-runtime.md` — runtime router spec
- `references/handoff-protocol.md` — execution-mode resume behavior

## Procedure

1. **Resume gate (runs before Q1):**
   - Check for an existing `Diagnostic_State.md` in active project context.
   - If state exists and `Mode.Current` is `execution`, do NOT run router questions yet. Present:
     - **Check the fix** — reload editor mode and run re-entry delta check on active scene
     - **Keep working** — stay in execution mode on current scene
     - **Start fresh** — continue to full intake router
   - Route by user choice:
     - Check the fix -> follow `handoff-protocol.md` §5b re-entry procedure
     - Keep working -> remain in execution mode, stop `/start` flow
     - Start fresh -> continue to step 2

2. Read `references/intake-router-runtime.md` in full.
3. Ask **Question 1** (Artifact): "What do you have right now?" using runtime options.
4. If user provides material instead of self-reporting, classify with runtime artifact thresholds.
5. Ask **Question 2** (Goal): use the conditional option set for the selected artifact.
6. Ask **Question 3** (Constraint/Operator modifiers): "Before we start - anything I should know?"
7. If artifact/goal pairing is ambiguous, apply the runtime fallback disambiguator.
8. Route to the target workflow per the runtime route map.
9. Load the routed target only now:
   - Pre-writing route -> load `pre-writing-pathway`
   - Development edit route -> load `references/run-core.md`
   - Audit route -> load `specialized-audits`
   - Plot coaching route -> load `plot-architecture`
10. If route target is a gap, execute the runtime gap-handling protocol (acknowledge, offer closest, name missing coverage).
11. Pass router output (`artifact`, `goal`, `concern`, `constraints`, `operator`, `gap_flags`) to the routed workflow intake and skip redundant questions.

## Output location

No direct output. `/start` routes into the selected workflow, which writes artifacts to `Outputs/[Project]/`.
