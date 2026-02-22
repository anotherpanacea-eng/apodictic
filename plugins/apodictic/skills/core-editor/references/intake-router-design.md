# Intake Router — Design Notes

**Status:** Reference documentation (not loaded at runtime)
**For:** APODICTIC Development Editor v0.5
**Last updated:** 2026-02-22

This file contains the design rationale, axis model, and implementation notes for the intake router. It is not loaded during runtime — the LLM uses `intake-router-runtime.md` for execution.

---

## The Four-Axis Model

The router implements a four-axis classification from the Publication Requirements:

**Artifact × Goal × Operator × Constraint**

- **Artifact:** What the user has (idea, fragments, partial, full_draft, series)
- **Goal:** What the user wants next (draft, repair, submit)
- **Operator:** Who the user is (author, editor, facilitator, co-authoring team)
- **Constraint:** What modifies how we work (time, AI-assisted, nonfiction, risk)

The axes are asked in this order for specific reasons:

### Why Artifact first

Writers know what they have before they know what they need. "I have a complete draft" is a fact; "I need structural repair" is a judgment the writer may not be equipped to make. Starting with Artifact grounds the conversation in the concrete.

### Why Goal is conditional on Artifact

Offering "check submission readiness" to someone with only an idea wastes their time and suggests the tool doesn't understand their situation. Conditional options demonstrate competence and reduce cognitive load.

### Why Operator is in Q3, not Q1

Most users are authors. Asking "who are you?" first front-loads a question that 80%+ of users will find trivially obvious. Folding Operator into the modifier question lets editors and facilitators self-identify without burdening the majority.

### Why Constraint is post-routing

Constraints modify workflows; they don't select them. A deadline doesn't change whether you need Core DE — it changes how Core DE runs. Asking constraints after routing keeps the routing logic clean and the constraint logic modular.

---

## Gap Strategy

Routes marked "Gap" in the route map represent workflows that don't yet exist. The gap-handling protocol requires honest acknowledgment, nearest-available substitution, and explicit naming of what won't be covered.

### Current gap inventory (v0.5)

| Gap | Closest available | What's lost |
|-----|-------------------|-------------|
| Fragment Synthesis | Pre-Writing Pathway (user self-organizes fragments) | Automated fragment clustering and candidate contract generation |
| Partial Manuscript Diagnostic | Core DE (runs on available material, penalizes missing structure) | Truncated-analysis mode that doesn't flag incompleteness as a problem |
| Fast Triage | Core DE (user can ask for abbreviated output) | Hard caps on output length, forced prioritization |
| Unified Submission Workflow | Core DE + manually requesting Pass 11 | Single-command flow, query/synopsis diagnostic |
| Feedback Triage | Core DE (user provides feedback context manually) | Structured feedback intake, conflict resolution |
| Nonfiction Pre-Draft Pathway | Pre-Writing Pathway (fiction-oriented) | Argument spine, evidence map, scene ethics |
| Risk Register | Core DE + manual flagging | Structured risk output, escalation triggers |
| Editor Scaffolding Mode | Core DE (author-facing output) | Editor-facing framing, blind-spot emphasis |
| Facilitator/Vocabulary Mode | Core DE (full diagnostic) | Workshop-ready language, discussion prompts |
| Multi-Party Intake | Core DE (single-author) | Conflict surfacing, sign-off workflow |
| Series Continuity Audit | Core DE per volume (no cross-volume state) | Persistent character/world/thread tracking across books |

### Gap prioritization

Gaps are addressed in the roadmap: Fast Triage and Submission Readiness in v1.1; Partial Manuscript and Fragment Synthesis in v1.2; Feedback Triage and Nonfiction Pre-Draft in v1.3; Editor/Facilitator modes in v1.4.

---

## Implementation Notes

### Router as specification

This router is a specification executed by the LLM, not application code. The LLM reads the runtime file, asks the questions, classifies the answers, and routes to the appropriate workflow. There is no separate router engine.

### Router output format

The router produces a structured classification that downstream workflows consume:

```
artifact: [idea | fragments | partial | full_draft | series]
goal: [draft | repair | submit]
concern: [specific concern if targeted, else "general"]
constraints: [list of active constraint flags]
operator: [author | editor | facilitator | team]
route: [workflow name from route map]
gap_flags: [any gaps acknowledged]
```

Downstream workflows (run-core.md, pre-writing-pathway) should accept this output and skip redundant intake questions.

---

*This file is reference documentation. The runtime specification is in `intake-router-runtime.md`.*
