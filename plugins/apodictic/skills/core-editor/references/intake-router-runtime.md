# Intake Router — Runtime

**Status:** Implementation-ready
**For:** APODICTIC Development Editor v0.5
**Last updated:** 2026-03-19 (nonfiction routing patch)

This file is loaded on every `/start` invocation. It contains the question flow, route map, and gap-handling protocol — everything the LLM needs to execute routing. For design rationale, see `intake-router-design.md`.

---

## Entry Point

`/start` triggers this router. All existing commands remain functional as direct-access shortcuts (see §5).

---

## §1. Question 1: What do you have right now?

*Axis: Artifact*

Present these options:

| Option | Label | Internal value |
|--------|-------|----------------|
| A | An idea — no writing yet | `idea` |
| B | Scattered notes, scenes, or fragments | `fragments` |
| C | A draft in progress — started but not finished | `partial` |
| D | A complete draft | `full_draft` |
| E | Multiple books in a series | `series` |

### Artifact thresholds

When the user provides material rather than self-reporting, use these deterministic thresholds:

| Artifact | Threshold | Distinguishing test |
|----------|-----------|-------------------|
| `idea` | No prose exists. The user describes the project verbally or provides a logline, premise, or pitch. May have a mood board, comp list, or thematic notes — but no narrative sentences. | If you can't find a scene, a character speaking, or a narrator narrating, it's an idea. |
| `fragments` | Prose exists but lacks continuous narrative. Disconnected scenes, character sketches, dialogue experiments, world-building documents, abandoned openings. No single thread runs for more than ~2,000 words. | Multiple pieces that don't connect into a reading sequence. The writer couldn't hand you a chapter order. |
| `partial` | Continuous narrative exists but the draft is incomplete. The writer has a beginning (and possibly a middle) but not an ending — or has an ending but major gaps. More than ~2,000 words of connected prose with a discernible forward movement. | The writer could hand you pages in order but would say "it's not done." |
| `full_draft` | The draft has a beginning, middle, and end. It may be rough, over-long, structurally unsound — but the writer considers it complete enough to be read start-to-finish. Word count is not the criterion; completeness of arc is. | The writer would say "it's done, but I know it needs work." |
| `series` | Two or more books (any combination of draft states) that share a fictional world, recurring characters, or a series arc. | The writer is thinking across volumes, not just within one. |

### Edge cases

- A detailed outline with no prose → `idea`
- A complete first act with nothing after → `partial`
- One finished novel plus notes for book 2 → `series`
- A 90K-word draft missing the last chapter → `full_draft`
- 50 disconnected scenes totaling 40K words → `fragments`

---

## §2. Question 2: What do you want next?

*Axis: Goal (conditional on Artifact)*

Options change based on the Artifact answer.

### If Artifact = `idea`

"What kind of help do you need?"

| Option | Label | Route |
|--------|-------|-------|
| A | Help figuring out what to write and how to structure it | Pre-Writing Pathway |
| B | I already know my structure — I just need to start drafting | Pre-Writing Pathway (fast-track: skip to Phase 4 Spine Selection) |

### If Artifact = `fragments`

"What do you want to do with these pieces?"

| Option | Label | Route |
|--------|-------|-------|
| A | Figure out what they add up to — find the book in the fragments | Fragment Synthesis → Pre-Writing Pathway |
| B | I know what the book is — help me fill in the gaps | Core DE (partial-manuscript flag) |

### If Artifact = `partial`

"What's going on with the draft?"

| Option | Label | Route |
|--------|-------|-------|
| A | I'm stuck — something isn't working but I don't know what | Core DE (partial-manuscript flag, diagnostic focus) |
| B | I know what's wrong — I need help fixing a specific problem | Core DE (partial-manuscript flag, targeted: ask what the problem is) |
| C | I want to step back and rethink the structure before writing more | Pre-Writing Pathway (re-entry: import existing decisions) |

### If Artifact = `full_draft`

"What do you need?"

| Option | Label | Route |
|--------|-------|-------|
| A | Figure out what's wrong and how to fix it | Core DE |
| B | Check if it's ready to submit (query, submission, self-pub) | Core DE → Pass 11 (Submission Readiness) |
| C | Clean up AI-generated or AI-assisted prose | Core DE + AI-Prose Calibration |
| D | I have beta reader feedback — help me sort through it | Feedback Triage → Core DE |
| E | I have a diagnosis — help me plan revision | Revision Coach |

**Execution mode:** For `full_draft` manuscripts over 40k words, §2b will fire after this question to surface the execution mode choice. No need to mention execution mode here.

### If Artifact = `series`

"What kind of series help?"

| Option | Label | Route |
|--------|-------|-------|
| A | Work on one book (the current volume) | Re-ask Q1 for the specific volume, with series context noted |
| B | Check continuity across volumes | Series Continuity Audit |
| C | Plan the series arc or the next volume | Pre-Writing Pathway (series-aware mode) |

---

## §2b. Execution Mode (conditional — manuscripts over 40k words)

*Fires when: Artifact is `full_draft`, `partial`, or `series` (single volume selected) AND estimated word count exceeds 40,000. Skip for shorter manuscripts and for `idea` or `fragments` (no manuscript to analyze).*

*Context-aware behavior: If the parent orchestrator has ≥1M context tokens and the pre-flight estimated single-agent load is under 600K tokens, single-agent mode is the automatic default. In this case, §2b still fires for manuscripts over 40K words, but the options shift — single-agent replaces sequential as option A, and the question focuses on whether the user wants to upgrade to swarm for deeper analysis.*

*When to ask: After Q2 resolves the goal, before Q3 constraints. If the user has already selected an execution mode via §3 options H/I or by stating "run this in swarm mode" at any point, skip this question.*

**Large-context version (≥1M tokens, manuscript fits in single-agent):**

"Your manuscript is long enough that you might want a more thorough read. Two options:"

| Option | Label | Plain-language description | Internal value |
|--------|-------|---------------------------|----------------|
| A | Standard read (recommended) | I run all my analysis in one continuous session, keeping the full manuscript in view the whole time. Fast and thorough for most drafts. | `execution:single-agent` |
| B | Full independent read (final-round insurance) | Every analytical lens reads the entire manuscript independently, so they can't influence each other — an independent-lens verification pass. Roughly 5x the cost (a 2026-06 re-test measured ~8.5×+ on long fiction). Best for final submission prep, not everyday depth. | `execution:swarm` |

**Large-context recommendation by context:**

| Condition | Recommendation |
|-----------|---------------|
| Any length, goal = `repair` | Default to A. Mention B exists for final polish. |
| Any length, goal = `submit` | Recommend B. "Since you're checking submission readiness, the independent-lens read is worth the cost." |
| User selects B | Confirm: "That's roughly 5x the token cost — just making sure you're good with that." |
| User selects A or skips | Proceed with single-agent. No friction. |

**Standard-context version (<1M tokens):**

"Your manuscript is long enough that how I read it matters. Three options:"

| Option | Label | Plain-language description | Internal value |
|--------|-------|---------------------------|----------------|
| A | Standard read (fastest) | I read the whole manuscript once, then run all my analysis in sequence. Good for most drafts. Some findings may be thinner on very long novels because earlier analysis fades as I work. | `execution:sequential` |
| B | Targeted deep read (recommended for novels) | I read the whole manuscript once to map it, then send each analytical lens to the specific scenes that need it most. Each lens works independently, so they can't parrot each other. Costs roughly 2–3x as much as a standard read. | `execution:hybrid` |
| C | Full independent read (final-round insurance) | Every analytical lens reads the entire manuscript independently — an independent-lens verification pass. Roughly 5x the cost of a standard read (a 2026-06 re-test measured ~8.5×+ on long fiction). Best for final submission prep, not everyday depth. | `execution:swarm` |

**Standard-context recommendation by context:**

| Condition | Recommendation |
|-----------|---------------|
| 40k–80k words, goal = `repair` | Mention option B exists; don't push it. Sequential handles this range adequately. |
| 80k+ words, goal = `repair` | Recommend B. "For a manuscript this length, the targeted read catches things the standard read misses." |
| Any length, goal = `submit` | Recommend B or C. "Since you're checking submission readiness, the independent-lens verification read is worth the cost." |
| User selects B or C | Confirm: "That adds to the token cost — just making sure you're good with that." |
| User selects A or skips | Proceed with sequential. No friction. |

**What this question does NOT do:**

- It does not explain architectural details (subagents, focus maps, context windows). The user doesn't need to understand the mechanism — just the tradeoff between depth and cost.
- It does not ask about token budgets. The user rarely knows their budget in tokens. "Roughly 2–3x" and "roughly 5x" are sufficient framing.
- It does not override the user's choice. If they pick standard read on a 120k novel, that's their call.

**Quality-risk overlay (router-side detection).** Before presenting §2b options, the router scans the contract draft and intake answers for the five quality-risk triggers (Q1-Q5) defined in `run-core.md` §Quality-Risk Mode Selection. Detection is mechanical — based on contract fields and intake values, not model judgment:

- **Q1 — Consent/governance risk:** genre = Horror or Erotic; OR `Consent Complexity` / `Reception Risk` audits on the recommended list; OR `darkness level: HIGH` in contract.
- **Q2 — Argument-shaped nonfiction with high stakes:** `constraint:nonfiction` set AND form is policy brief / testimony / op-ed / academic argument / open letter / white paper (per §4a Form table); OR `Dialectical Clarity` audit recommended with submission readiness signaled.
- **Q3 — Many POVs or non-linear structure:** contract POV count ≥3; OR intake notes non-linear chronology / fragmented structure / nested narratives.
- **Q4 — Prior thin synthesis:** prior-run `Diagnostic_State.meta.json` shows Underdiagnosis Retry Loop fired in prior runs; OR user states "last round felt thin."
- **Q5 — Submission readiness:** Q2 goal = `submit`; OR Pass 11 in resolved pass set.

When any trigger fires, the router pre-fills its mode recommendation at the trigger's escalation target (per `run-core.md` §Quality-Risk Mode Selection) and surfaces the rationale to the user *before* §2b's recommendation table. Stacking triggers cap at swarm. The user retains the override path (explicit acknowledgment recorded in run metadata as `quality_risk_override`). See `run-core.md` §Quality-Risk Mode Selection for the canonical rationale per trigger and `scripts/validate.sh quality-risk-triggers` for the mechanical check.

---

## §3. Question 3: Anything that should change how we work?

*Axis: Constraint + Operator modifiers*

Always asked after routing, before work begins. Multiple selections allowed.

"Before we start — anything I should know?"

| Option | Label | Internal flag | Kind | Effect on workflow |
|--------|-------|--------------|------|-------------------|
| A | I'm on a deadline | `constraint:time` | **Fork** (workflow) | Route to Submission Triage: Pass 1 → SR codes (detectable subset) → go/no-go memo with blind spots. See `references/submission-triage.md`. |
| B | Parts of this were written with AI | `constraint:ai` | **Overlay** (lens) | Add AI-Prose Calibration overlay. |
| C | This is nonfiction | `constraint:nonfiction` | **Fork** (engine) | Run nonfiction triage. Route argument-shaped work to the Nonfiction Argument Engine, scene-led nonfiction to Narrative Nonfiction Craft, and memoir / witness-led work to Memoir & CNF. Idea-stage Nonfiction Pre-Draft remains a gap. |
| D | There's sensitive or legally risky content | `constraint:risk` | **Overlay** (output) | **Built.** Offer the Legal Risk Register; on accept, attach `[Project]_Legal_Risk_Register_[runlabel].md` (`references/legal-risk-register.md`; synthesis hook in `run-synthesis.md §Constraint mode`). Direct entry: `/legal-risk`. |
| E | I'm editing someone else's work | `operator:editor` | **Overlay** (output) | Shift output to editor scaffolding (editor-facing reframe of the synthesis letter). **Built** — see `references/editor-scaffolding.md`. |
| F | I'm facilitating a writing group | `operator:facilitator` | **Overlay** (output) | Shift to diagnostic vocabulary mode (produce a teaching Vocabulary Guide: glossary + discussion prompts). **Built** — see `references/diagnostic-vocabulary.md`. |
| G | We're co-authoring (multiple writers) | `operator:team` | **Fork** (intake) | Note conflicting-vision risk. **Gap: multi-party intake not yet built.** |
| H | Use hybrid mode (better analysis, moderate token cost) | `execution:hybrid` | **Overlay** (execution) | Pass 0+1 reads full manuscript and builds a focus map; later passes read the outline + targeted excerpts as independent subagents. ~2–3x token cost. See `run-core.md` §Execution Mode. |
| I | Use swarm mode (final-round verification, highest token cost) | `execution:swarm` | **Overlay** (execution) | Each pass runs as an independent subagent with full manuscript — architectural isolation for a verification pass. ~5x token cost (a 2026-06 N=1 re-test measured ~8.5×+ on long fiction and did not reproduce a depth advantage); reserve for final submission prep. See `run-core.md` §Execution Mode. |
| J | No constraints — let's go | (none) | — | Proceed with standard workflow. |

**Execution mode note:** For manuscripts over 40k words, §2b handles the execution mode question before §3. Options H and I below remain as a safety net — if the user didn't get §2b (shorter manuscript, direct command entry) but knows to ask for hybrid or swarm, these options catch it.

### §3a. Fork vs. Overlay — routing algebra

The Q3 options are two different kinds of thing, and the router composes them differently (design rationale: `intake-router-design.md` §Modifiers: forks vs. overlays):

- A **Fork** *selects* the workflow — it changes which engine runs or the terminal artifact. Forks reconcile with the Q1/Q2 base route and are **mutually exclusive within a class** (you run Submission Triage *or* full Core DE, never both). A fork is a route-map decision (§6 Table A).
- An **Overlay** *modifies* a selected workflow — it reskins the output, adds a diagnostic lens, or changes execution depth, leaving the engine and workflow shape intact. Overlays **compose**: any number stack on the base route and on each other. An overlay is never a route-map row (§6 Table B).

**Composition order.** Resolve the base route from Q1/Q2 → apply any **fork** (reconcile against the base; if forks of different classes are both selected, e.g. `time` + `nonfiction`, fork to the workflow first, then run it under the engine) → **stack** all selected overlays. Worked case: "I'm on a deadline" (`time` → fork to Submission Triage) + "I'm editing someone else's work" (`editor` → overlay) = fork to Submission Triage, then apply the editor-scaffolding overlay to the Triage output.

---

## §4. Fallback Disambiguator

When the router can't confidently classify (vague or contradictory answer, ambiguous artifact/goal pairing), ask one tiebreaker:

> "Just to make sure I send you to the right place — which is closest to what you need right now?"
>
> - **Start drafting** — help me build something new
> - **Improve existing pages** — help me fix what I've got
> - **Evaluate readiness** — help me decide if this is done

Mapping:
- Start drafting → `draft` (Pre-Writing Pathway or Fragment Synthesis)
- Improve existing pages → `repair` (Core DE, with appropriate artifact flag)
- Evaluate readiness → `submit` (Core DE + Pass 11)

---

## §4a. Nonfiction Routing Rules

When `constraint:nonfiction` is active and the user has prose pages rather than an idea-only project, do not treat nonfiction as a generic gap. Apply this triage:

### Route to the Nonfiction Argument Engine when:

1. the manuscript makes an extractable main claim
2. support, comparison, evaluation, proposal, or testimony dominates the structure
3. the user is working on an op-ed, policy brief, testimony, academic argument, open letter, advocacy argument, recommendation memo, white paper, legal-style brief, or other claim-bearing prose

### Route to Narrative Nonfiction Craft when:

1. the material is primarily scene-led, reportorial, or chronologically narrative
2. the reader's main question is about scene construction, pacing, source integration, and factual storytelling experience

### Route to Memoir & Creative Nonfiction when:

1. first-person witness, memory, truth-craft, and ethical obligation are central
2. experiential authority dominates even if an argument is present

### Hybrid rule

If the manuscript is Franklin Classification 3:

1. choose Dialectical Clarity when argument dominates and narrative is serving evidence or stakes
2. choose Narrative Nonfiction Craft when narrative dominates and the argument is secondary

### Default activation by form

| Form | Default route |
|---|---|
| Op-ed / persuasive essay / open letter | Dialectical Clarity |
| Policy brief / recommendation memo / white paper | Dialectical Clarity; offer Red Team next |
| Testimony | Dialectical Clarity; offer Red Team next |
| Academic argument / review essay / legal brief | Dialectical Clarity |
| Reported feature / scene-led journalism | Narrative Nonfiction Craft |
| Memoir / personal essay / witness-led CNF | Memoir & CNF; add Dialectical Clarity when explicit claim burden dominates |

### Post-diagnostic offer

After Dialectical Clarity on nonfiction argument work, surface the next likely action:

1. `/audit argument-red-team` for hostile pressure testing
2. `/audit argument-evidence` when evidence legitimacy is the likely bottleneck
3. `/audit argument-persuasion` when audience fit is the likely bottleneck
4. `/coach` for revision sequencing

---

## §5. Command Shortcuts

All commands work as direct entry points. `/start` is recommended for new users; the other commands are shortcuts for writers who know what they want.

| Command | What it does | Router equivalent |
|---------|-------------|-------------------|
| `/start` | Routes to the right workflow in 2–3 questions (including a full edit on a `full_draft` and a targeted diagnostic via `goal=repair`) | The router itself |
| `/ready` | Submission readiness check | artifact=`full_draft`, goal=`submit` |
| `/audit [name]` | Run a specific deep-dive analysis | Callable from within workflows |
| `/research [mode]` | Internet-assisted verification | Callable from within workflows |
| `/coach` | Post-diagnostic revision coaching | Post-diagnostic (not an intake question) |
| `/plot-coach` | Plot structure coaching | Callable from within workflows |
| `/pre-writing` | Idea to draftable structure | artifact=`idea`, goal=`draft` |
| `/new-project` | Initialize a new project | Initialize project, then run router |

---

## §6. Route Map

Routing has two entry modes. **Bound project** (a known book selected via `/start <project>` — Project Addressability): routing is *state-driven* — derive the lifecycle node from the sidecar and dispatch via the Lifecycle transition table below, skipping the intake questions (`commands/start.md` Step 0.5). **Cold start** (no bound project): pick **one base route** from Table A (applying any fork from the Artifact/Goal answers + Q3), then **stack any compatible overlays** from Table B. Overlays never appear as base-route rows — their applicability and status live once, in Table B, and compose onto whatever base route the forks (cold) or node (bound) selected.

### §6 Lifecycle transition table (bound projects — state-driven dispatch)

The destination for a *bound* project is its **lifecycle node**, derived from the sidecar by a single first-match precedence (`cold → blocked_gate → execution → pre_writing → submission → revising → diagnosed → diagnosing`; total, with `diagnosing` the default). Mechanized + tested by `scripts/validate.sh lifecycle-node`. Full derivation table and rationale: `docs/project-addressability.md` §Increment 3.

| Lifecycle node | Primary next action → workflow |
|---|---|
| `blocked_gate` | resolve the pending gate first (§Resume Target) |
| `execution` | execution-mode resume (Check the fix / Keep working) — `handoff-protocol.md` |
| `pre_writing` | `pre-writing-pathway/SKILL.md` |
| `submission` | Submission Readiness (`references/submission-readiness.md`) / triage |
| `revising` | revision-loop dispatcher (`revision-coach/SKILL.md` §Loop Dispatch) proposes the next leverage action; the stored `next_action` (`revision_round` → `state-lifecycle.md`, or `coaching` → `revision-coach`) is its default |
| `diagnosed` | offer `/coach` |
| `diagnosing` | stored `next_action`: `run_passes` / `run_synthesis` / `run_audits` |
| `cold` | no bound project → cold-start entry map (Table A) |

Overlays for a bound project still come from Table B (not re-derived per node).

### §6 Table A — Base routes (cold-start entry map: Artifact × Goal, forks resolved)

The **cold-start** workflow-selection decisions — the path for a project with no lifecycle node yet (a bound, in-progress project routes via the Lifecycle transition table above instead). The `Fork` column names a workflow-selecting modifier when one applies (engine = which diagnostic engine; workflow = which workflow shape; intake = which intake). Forks are mutually exclusive within a class.

| Artifact | Goal | Fork | Workflow | Status |
|----------|------|------|----------|--------|
| idea | draft | — | Pre-Writing Pathway | **Built** |
| idea | draft (fast-track) | — | Pre-Writing Pathway (skip to Phase 4) | **Built** |
| idea | draft | engine=nonfiction | Nonfiction Pre-Writing | Gap |
| fragments | draft | — | Fragment Synthesis → Pre-Writing | **Built** (v1.2.0) |
| fragments | repair | — | Core DE (partial flag) | **Built** (v1.2.0) |
| partial | repair (diagnostic) | — | Core DE (partial flag) | **Built** (v1.2.0) |
| partial | repair (targeted) | — | Core DE (partial flag, targeted) | **Built** (v1.2.0) |
| partial | repair | engine=nonfiction (argument-shaped) | Nonfiction Argument Engine (`dialectical-clarity.md`) on available sections | **Built** (v1.0) |
| partial | draft (rethink) | — | Pre-Writing Pathway (re-entry) | **Built** |
| partial | repair | workflow=time | Submission Triage | Gap: triage requires complete manuscript. Offer a targeted `/start` (goal=repair). |
| full_draft | repair | — | Core DE | **Built** |
| full_draft | repair | engine=nonfiction (argument-shaped) | Nonfiction Argument Engine (`dialectical-clarity.md`) | **Built** (v1.0) |
| full_draft | repair | engine=nonfiction (scene-led) | Narrative Nonfiction Craft | **Built** |
| full_draft | repair | engine=nonfiction (memoir / witness-led) | Memoir & CNF | **Built** |
| full_draft | repair | workflow=time | Submission Triage | **Built** (v1.1) |
| full_draft | repair | workflow=feedback | Feedback Triage → Core DE | **Built** (v2.2.0, direct via `/triage-feedback`) |
| full_draft | submit | — | Submission Readiness Workflow (`references/submission-readiness.md`) | **Built** (v1.1) |
| full_draft | submit | workflow=time | Submission Triage | **Built** (v1.1) |
| full_draft | coach | — | Revision Coach (`revision-coach/SKILL.md`) | **Built** (v1.1.2) |
| full_draft | coach (deadline) | — | Revision Coach (deadline mode) | **Built** (v1.1.2) |
| series | repair (single vol) | — | Core DE (series context) | Partially built |
| series | repair (continuity) | — | Series Continuity Audit (`craft/series-continuity.md`) | **Built** (v1.2) |
| series | draft (plan next) | — | Pre-Writing Pathway (series-aware) | Partially built |

### §6 Table B — Overlays (orthogonal; compose onto any compatible base route)

Workflow-*modifying* modifiers. Each composes onto any compatible Table A base route; multiple overlays stack. Status lives here once — it is **not** re-asserted per base route (this is what kept the old single table's `ai` / `hybrid` / `swarm` / `editor` / `facilitator` / `risk` rows in sync drift). The nine former `base × overlay` rows are computed from this table, not enumerated.

| Overlay | Flag | Effect | Composes onto | Status |
|---------|------|--------|---------------|--------|
| AI-Prose Calibration | `constraint:ai` | Adds AI-prose lens + findings (`craft/ai-prose-calibration.md`) | Any prose-bearing repair/submit base route (on `fragments \| draft`, calibration deferred to post-synthesis) | **Built** |
| Editor Scaffolding | `operator:editor` | Re-aims the editorial letter at a human editor | Any Core DE letter (`references/editor-scaffolding.md`) | **Built** |
| Diagnostic Vocabulary | `operator:facilitator` | Adds a teaching Vocabulary Guide alongside the letter | Any Core DE letter (`references/diagnostic-vocabulary.md`) | **Built** |
| Legal Risk Register | `constraint:risk` | Adds a Legal Risk Register output (offer-then-attach) | Any repair/submit base route (`references/legal-risk-register.md`) | **Built** |
| Hybrid execution | `execution:hybrid` | Focus-map depth; ~2–3x token cost; content-invariant | Any pass-based run >40k words (`run-core.md` §Execution Mode) | **Built** |
| Swarm execution | `execution:swarm` | Independent-lens depth; ~5x token cost; content-invariant | Any pass-based run (`run-core.md` §Execution Mode) | **Built** |

## §7. Gap Handling Protocol

When the router resolves to a gap route:

1. **Acknowledge honestly.** Name the specific workflow that doesn't exist yet.
2. **Offer the closest built workflow.** State what it will cover and what it won't.
3. **Name what won't be covered.** Be specific: "This won't include [X] because that workflow isn't built yet."

Never silently downgrade. The user should always know when they're getting a substitute.

---

*This file is a runtime reference. Design rationale is in `intake-router-design.md`.*
