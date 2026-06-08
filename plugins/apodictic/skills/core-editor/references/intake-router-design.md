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

### Why Constraint is post-routing — and the fork/overlay correction

The original principle was: *constraints modify workflows; they don't select them. A deadline doesn't change whether you need Core DE — it changes how Core DE runs.* That holds for **overlays** (`ai`, `editor`, `facilitator`, `risk`, `hybrid`, `swarm`) but was never true of the whole modifier axis: `constraint:time` routes to Submission Triage and `constraint:nonfiction` routes to a different engine — both *select* a workflow outright. The Q3 axis carries two different kinds of modifier (see §Modifiers: forks vs. overlays). Q3 is still asked post-routing because most users are authors with no modifier — but a **fork** answer reconciles back against the Q1/Q2 base route, while an **overlay** answer simply stacks.

### Modifiers: forks vs. overlays

The Q3 "Constraint/Operator" options split into two kinds with different routing algebra. Full proposal and worked migration: [`docs/router-fork-overlay-split.md`](../../../../../docs/router-fork-overlay-split.md).

- **Fork** — *selects* the workflow. Changes which engine runs or the terminal artifact. Belongs in the route map (runtime §6 Table A), mutually exclusive within a class, may be conditional or sub-resolve. Forks: `time` (workflow), `nonfiction` (engine, sub-resolves to argument / narrative / memoir), `feedback` (workflow, prepends Feedback Triage), `team` (intake — gap).
- **Overlay** — *modifies* a selected workflow. Reskins output, adds a lens, or changes execution depth; leaves engine and workflow shape intact. Never a route-map row (runtime §6 Table B); composes freely. Overlays: `ai` (lens), `editor` / `facilitator` / `risk` (output), `hybrid` / `swarm` (execution).

**Classification test.** Does the modifier replace the primary diagnostic engine or change the workflow's terminal artifact? → Fork. Does it leave the pass/engine selection intact and only reskin output, add a lens, or change depth/cost? → Overlay.

The payoff: overlays stop appearing as route-map rows (the old single table enumerated the `base × overlay` cross-product, which is why a capability like the Legal Risk Register drifted to "Gap" in some cells while its module was built). Status now lives once per overlay (§6 Table B).

---

## Gap Strategy

Routes marked "Gap" in the route map represent workflows that don't yet exist. The gap-handling protocol requires honest acknowledgment, nearest-available substitution, and explicit naming of what won't be covered.

### Current gap inventory

**Superseded — see the live status columns in `intake-router-runtime.md` §6 Table A (base routes) / Table B (overlays) and the `ROADMAP.md` Done column.** The historical v0.5 inventory once listed Fragment Synthesis, Partial Manuscript, Fast/Submission Triage, Feedback Triage, Editor Scaffolding, Diagnostic Vocabulary, Series Continuity, and the Legal Risk Register module as gaps; all have since shipped (v1.1–v2.2.0). Maintaining a parallel gap list here only invites the drift this section is meant to avoid, so the route-map status columns are now the single source of truth.

Genuinely remaining gaps:

- **Multi-Party Intake** (`operator:team`, fork=intake) — co-authoring intake; conflict surfacing / sign-off. Closest: single-author Core DE.
- **Nonfiction Pre-Draft, idea-stage** (`engine=nonfiction` at `artifact:idea`) — the prose-stage nonfiction engines (argument / narrative / memoir) are built; only the idea-stage pre-draft pathway entry remains a router gap. (The Nonfiction Pre-Draft *module* itself is built per `ROADMAP.md`; the open item is its router wiring.)
- **Legal Risk Register router wiring** — the module is built (`references/legal-risk-register.md`); auto-attaching it as an overlay from `constraint:risk` is the pending increment.

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

The router has **two entry modes** (Project Addressability, Increment 3 — `docs/project-addressability.md`):

- **Bound project** (`/start <project>`): routing is *state-driven*. The router derives a **lifecycle node** from the project's sidecar (`scripts/validate.sh lifecycle-node`) and dispatches via the `§6` Lifecycle transition table + the sidecar `next_action` — the Artifact/Goal classification below is *not* recomputed (it is known from the contract + sidecar). Overlays still come from the Q3 / Table B layer. Output in this mode is effectively `{ lifecycle_node, next_action, overlays }`.
- **Cold start** (no bound project): the router produces the full Artifact×Goal classification below.

The cold-start classification downstream workflows consume:

```
artifact:   [idea | fragments | partial | full_draft | series]
goal:       [draft | repair | submit | coach]
concern:    [specific concern if targeted, else "general"]
base_route: [workflow name from §6 Table A]
forks:      { engine?:   nonfiction-argument | nonfiction-narrative | nonfiction-memoir,
              workflow?: time | feedback,
              intake?:   team }
overlays:   [ai, editor, facilitator, risk, hybrid, swarm]   # 0..n, composable
gap_flags:  [any forks/overlays acknowledged as gaps]
```

The shape mirrors the fork/overlay algebra: `base_route` is the resolved Table A selection, `forks` carries the workflow/engine/intake selectors, and `overlays` is the composable list from Table B. This replaces the prior flat `constraints: [...]` + `operator: [...]` lists (whose elements had incompatible routing semantics) and folds the bespoke `nonfiction_route` field into `forks.engine`. Downstream workflows (run-core.md, pre-writing-pathway) accept this output and skip redundant intake questions.

---

*This file is reference documentation. The runtime specification is in `intake-router-runtime.md`.*
