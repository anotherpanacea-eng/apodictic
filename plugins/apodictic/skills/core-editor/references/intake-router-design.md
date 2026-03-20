# Intake Router — Design Notes

**Status:** Reference documentation (not loaded at runtime)
**For:** APODICTIC Development Editor v0.5
**Last updated:** 2026-03-19 (nonfiction routing patch)

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

## Nonfiction Routing Protocol

The original router treated `constraint:nonfiction` as a broad gap. That is no longer correct for prose-bearing argument work. The remaining gap is **Nonfiction Pre-Draft** for idea-stage projects. For existing nonfiction pages, the router should now distinguish among three built destinations:

1. **Nonfiction Argument Engine** — claim/support material where argument dominates
2. **Narrative Nonfiction Craft** — scene-led or reported nonfiction where reader experience and factual scene construction dominate
3. **Memoir & Creative Nonfiction** — first-person, memory, truth-craft, and ethical-obligation work where experiential authority is central

### Nonfiction classification signals

Route to the **Nonfiction Argument Engine** when at least two of the following are true:

1. the material makes an extractable main claim
2. the prose is organized around support, comparison, evaluation, or recommendation
3. the writer's purpose is to persuade, propose, testify, defend, or argue
4. the dominant reading question is "does this case hold?" rather than "does this story work?"

Route to **Narrative Nonfiction Craft** when:

1. scenes, chronology, source integration, and reader experience dominate
2. the prose may imply an argument, but the reading contract is primarily narrative

Route to **Memoir & Creative Nonfiction** when:

1. first-person witness or memory is central
2. truth-craft, narrator reliability, and ethical obligation are foregrounded
3. argument may be present, but experience remains the primary delivery vehicle

### Hybrid rule

For Franklin Classification 3 material, route:

1. to Dialectical Clarity when argument dominates and narrative supports it
2. to Narrative Nonfiction Craft when narrative dominates and argument is secondary

### Default activation by form

| Form | Default route |
|---|---|
| Op-ed / persuasive essay / open letter | Nonfiction Argument Engine |
| Policy brief / recommendation memo / white paper | Nonfiction Argument Engine |
| Testimony | Nonfiction Argument Engine |
| Academic article / review essay / legal-style argument | Nonfiction Argument Engine |
| Reported feature / scene-led journalism | Narrative Nonfiction Craft |
| Memoir / personal essay / witness-driven CNF | Memoir & CNF, with Dialectical Clarity added when explicit claim burden dominates |

---

## Implementation Notes

### Router as specification

This router is a specification executed by the LLM, not application code. The LLM reads the runtime file, asks the questions, classifies the answers, and routes to the appropriate workflow. There is no separate router engine.

### Router output format

The router produces a structured classification that downstream workflows consume:

```
artifact: [idea | fragments | partial | full_draft | series]
goal: [draft | repair | submit | coach]
concern: [specific concern if targeted, else "general"]
constraints: [list of active constraint flags]
operator: [author | editor | facilitator | team]
route: [workflow name from route map]
nonfiction_route: [argument_engine | narrative_nonfiction | memoir_cnf | none]
gap_flags: [any gaps acknowledged]
```

Downstream workflows (run-core.md, pre-writing-pathway) should accept this output and skip redundant intake questions.

---

*This file is reference documentation. The runtime specification is in `intake-router-runtime.md`.*
