# /start — Intake Router

The recommended entry point for APODICTIC. Routes users to the right workflow in 2–3 questions using the four-axis classification model (Artifact × Goal × Operator × Constraint).

## Required skills

Load the `core-editor` skill first (thin orchestrator). Do NOT preload companion skills — load the routed target skill only after the route decision.

## Required references

- `intake-router.md` — full router specification, artifact thresholds, conditional goal options, constraint/operator modifiers, route map, fallback disambiguator, and gap-handling protocol

## Procedure

1. Read `intake-router.md` in full.
2. Ask **Question 1** (Artifact): "What do you have right now?" Present the five options.
3. If the user provides material instead of self-reporting, classify using the deterministic artifact thresholds.
4. Ask **Question 2** (Goal): Use the conditional option set for the user's artifact. If the artifact/goal pairing is ambiguous, use the fallback disambiguator.
5. Ask **Question 3** (Constraint/Operator modifiers): "Before we start — anything I should know?" Multiple selections allowed.
6. Route to the target workflow per the route map.
7. **Load the target skill now:**
   - Pre-writing route → load `pre-writing-pathway`
   - Development edit route → core skill already loaded; load `references/run-core.md`
   - Audit route → load `specialized-audits`
   - Plot coaching route → load `plot-architecture`
8. If the route target is a gap, follow gap protocol: acknowledge honestly, offer the closest built workflow, name what won't be covered.
9. Pass the router output (artifact, goal, constraint flags, operator flags) to the target workflow's intake protocol.

## Output location

No direct output — the router hands off to the routed workflow, which produces its own artifacts in `Outputs/[Project]/`.
