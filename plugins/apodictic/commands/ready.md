---
description: Run the Submission Readiness Workflow — full diagnostic + verdict + query/synopsis assessment
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch, Agent
---

# /ready — Submission Readiness Workflow

A single entry point for "is this ready to submit?" Runs Core DE → Synthesis → Pass 11 as a unified workflow and produces a structured readiness assessment.

## Required skills

Load the `core-editor` skill first (thin orchestrator). Do NOT preload companion skills.

## Required references

- `references/submission-readiness.md` — full workflow specification
- `references/run-core.md` — execution mode and pass dispatch
- `references/pass-dependencies.md` — pass resolution
- `references/pass-11.md` — Pass 11 sub-pass specifications

## Procedure

1. Load the `core-editor` skill.
2. Read `references/submission-readiness.md` in full.
3. Run the Submission Readiness Workflow as specified:
   - **Intake:** Abbreviated intake (artifact is `full_draft`, goal is `submit`). Confirm publication path (traditional, hybrid, self-pub). Ask about query/synopsis materials if available.
   - **Execution mode selection:** Run pre-flight. Select execution mode per `run-core.md` §Execution Mode. Default recommendation: single-agent or hybrid, depending on context window and manuscript length. If the writer explicitly requests swarm, honor it.
   - **Core DE passes:** Run the baseline pass set (0, 1, 2, 5, 8) per `run-core.md`.
   - **Synthesis:** Run synthesis per `run-core.md`, producing the editorial letter.
   - **Pass 11:** Run Pass 11 with sub-passes 11A, 11B always active; 11C (Market Reality Check) and 11D (First-50 Conversion Gate) active by default for submission workflow; 11E (Revision Economics) active if verdict is not READY.
   - **Unified Readiness Assessment:** Produce the combined output per `submission-readiness.md` §Output Template.
4. Write all artifacts to `Outputs/[Project]/`.

## When to use

- Writer asks "is this ready to submit?" or "submission readiness"
- Writer mentions querying agents, submitting to publishers, or checking market readiness
- `/start` routes here when artifact = `full_draft` and goal = `submit` (no time constraint)

## When NOT to use

- Writer is on a deadline → route to Submission Triage (faster, single-pass)
- Writer wants craft diagnosis without market intent → route to Core DE
- Manuscript is partial → Core DE only; Pass 11 requires complete arc

## Relationship to Submission Triage

`/ready` is the thorough path. Submission Triage (accessed via `constraint:time` in the router) is the fast path. If a writer invokes `/ready` but mentions deadline pressure, offer the triage as an alternative: "The full submission workflow takes a complete diagnostic. If you're on a deadline, I can run a quick single-pass triage instead. Which do you prefer?"

## Output location

All artifacts to `Outputs/[Project]/`:
- Core DE pass artifacts and Findings Ledger (standard locations)
- Editorial letter (standard)
- `Submission_Readiness_Assessment_[date].md` — the unified output
