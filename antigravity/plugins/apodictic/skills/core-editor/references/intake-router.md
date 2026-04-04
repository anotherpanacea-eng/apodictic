# Intake Router v1

> DEPRECATED (v0.4.19)
>
> This file is retained for archival reference only.
> Runtime routing now lives in `references/intake-router-runtime.md`.
> Design rationale now lives in `references/intake-router-design.md`.
> Do not load this file for `/start`.

**Status:** Draft
**For:** APODICTIC Development Editor v0.4.14.3
**Last updated:** March 2026 (nonfiction routing patch)

---

## Purpose

Replace the current command-selection model (`/develop-edit`, `/new-project`, `/pre-writing`, etc.) with a single entry point that routes users to the right workflow in 2–3 questions. Users should never need to know framework internals.

The router implements the four-axis classification model (Artifact × Goal × Operator × Constraint) from the Publication Requirements. It asks about Artifact first, then Goal (conditional on Artifact), then Constraint/Operator modifiers.

---

## Entry Point

A single command — `/start` or simply beginning a conversation with the plugin — triggers the router. All existing commands remain functional as direct-access shortcuts for users who already know what they want.

---

## Question 1: What do you have right now?

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

**Edge cases:**

- A detailed outline with no prose → `idea` (outlines are structural plans, not narrative material)
- A complete first act with nothing after → `partial`
- One finished novel plus notes for book 2 → `series` (even if book 2 is only an idea)
- A 90K-word draft missing the last chapter → `full_draft` (functionally complete; the missing chapter is a revision problem, not a completeness problem)
- 50 disconnected scenes totaling 40K words → `fragments` (word count doesn't matter; connection does)

---

## Question 2: What do you want next?

*Axis: Goal (conditional on Artifact)*

The options change based on the Artifact answer. This prevents offering goals that don't make sense for the user's state.

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
| E | Run a focused audit on a specific concern | Specialized Audit (list audits, user selects) |

### If Artifact = `series`

"What kind of series help?"

| Option | Label | Route |
|--------|-------|-------|
| A | Work on one book (the current volume) | Re-ask Q1 for the specific volume, with series context noted |
| B | Check continuity across volumes | Series Continuity Audit |
| C | Plan the series arc or the next volume | Pre-Writing Pathway (series-aware mode) |

---

## Question 3: Anything that should change how we work?

*Axis: Constraint + Operator modifiers*

Always asked after routing, before work begins. Multiple selections allowed.

"Before we start — anything I should know?"

| Option | Label | Internal flag | Effect on workflow |
|--------|-------|--------------|-------------------|
| A | I'm on a deadline | `constraint:time` | Truncate to fast triage: Pass 1 only → triage memo with max 3 interventions. Skip full diagnostic. |
| B | Parts of this were written with AI | `constraint:ai` | Add AI-Prose Calibration overlay to whatever workflow was selected. |
| C | This is nonfiction | `constraint:nonfiction` | Run nonfiction triage. Route argument-shaped work to the Nonfiction Argument Engine, scene-led nonfiction to Narrative Nonfiction Craft, and memoir / witness-led work to Memoir & CNF. Idea-stage nonfiction pre-draft remains a gap. |
| D | There's sensitive or legally risky content | `constraint:risk` | Add risk register output. Flag for human expert referral where appropriate. |
| E | I'm editing someone else's work | `operator:editor` | Shift output framing: scaffolding for the editor's practice, not direct advice to the author. Flag recommendations as "findings for your editorial letter" rather than "you should fix." |
| F | I'm facilitating a writing group | `operator:facilitator` | Shift to diagnostic vocabulary mode: teach structural concepts, provide discussion prompts, frame issues as questions rather than prescriptions. |
| G | We're co-authoring (multiple writers) | `operator:team` | Note conflicting-vision risk. When priorities conflict, surface the disagreement rather than averaging. **Gap: multi-party intake not yet built; degrades to standard Core DE with team context noted.** |
| H | No constraints — let's go | (none) | Proceed with standard workflow. |

---

## Fallback Disambiguator

When the router can't confidently classify (user gives a vague or contradictory answer, or the artifact/goal pairing is ambiguous), ask one tiebreaker:

> "Just to make sure I send you to the right place — which is closest to what you need right now?"
>
> - **Start drafting** — help me build something new
> - **Improve existing pages** — help me fix what I've got
> - **Evaluate readiness** — help me decide if this is done

These three map cleanly to the Goal axis:
- Start drafting → `draft` (Pre-Writing Pathway or Fragment Synthesis)
- Improve existing pages → `repair` (Core DE, with appropriate artifact flag)
- Evaluate readiness → `submit` (Core DE + Pass 11)

---

## Complete Route Map

| Artifact | Goal | Constraint/Operator | Workflow | Status |
|----------|------|-------------------|----------|--------|
| idea | draft | — | Pre-Writing Pathway | **Built (v0.4.5.0)** |
| idea | draft (fast-track) | — | Pre-Writing Pathway (skip to Phase 4) | **Built (v0.4.5.0)** |
| idea | draft | nonfiction | Nonfiction Pre-Writing | Gap |
| fragments | draft | — | Fragment Synthesis → Pre-Writing | Gap (Pre-Writing fallback available) |
| fragments | draft | ai | Fragment Synthesis → Pre-Writing + AI-Prose Calibration | Gap (partial) |
| fragments | repair | — | Core DE (partial flag) | Gap: partial manuscript diagnostic |
| partial | repair (diagnostic) | — | Core DE (partial flag) | Gap: partial manuscript diagnostic |
| partial | repair (targeted) | — | Core DE (partial flag, targeted) | Gap: partial manuscript diagnostic |
| partial | repair | nonfiction (argument-shaped) | Nonfiction Argument Engine (`dialectical-clarity.md`) on available sections | **Built (v1.0)** |
| partial | draft (rethink) | — | Pre-Writing Pathway (re-entry) | **Built (v0.4.5.0)** |
| partial | repair | time | Fast Triage | Gap |
| full_draft | repair | — | Core DE | **Built (v0.4.5.0)** |
| full_draft | repair | time | Fast Triage | Gap |
| full_draft | repair | ai | Core DE + AI-Prose Calibration | **Built (v0.4.5.0)** |
| full_draft | repair | nonfiction (argument-shaped) | Nonfiction Argument Engine (`dialectical-clarity.md`) | **Built (v1.0)** |
| full_draft | repair | nonfiction (scene-led) | Narrative Nonfiction Craft | **Built** |
| full_draft | repair | nonfiction (memoir / witness-led) | Memoir & CNF | **Built** |
| full_draft | audit | — | Specialized Audit (user selects) | **Built (v0.4.17)** |
| full_draft | repair | risk | Core DE + Risk Register | Gap |
| full_draft | submit | — | Core DE → Pass 11 | Gap: unified submission workflow |
| full_draft | submit | time | Fast Triage (submission focus) | Gap |
| full_draft | repair | editor | Core DE (editor scaffolding) | Gap: editor mode |
| full_draft | repair | facilitator | Core DE (diagnostic vocabulary) | Gap: facilitator mode |
| full_draft | repair (feedback) | — | Feedback Triage → Core DE | Gap |
| series | repair (single vol) | — | Core DE (series context) | Partially built |
| series | repair (continuity) | — | Series Continuity Audit | Gap |
| series | draft (plan next) | — | Pre-Writing Pathway (series-aware) | Partially built |

---

## Relationship to Existing Commands

Existing commands become direct-access shortcuts. The router is the recommended entry point, but power users can bypass it.

| Current command | Router equivalent | Kept as shortcut? |
|----------------|-------------------|-------------------|
| `/start` | The router itself | Yes (primary entry) |
| `/develop-edit` | full_draft + repair | Yes |
| `/new-project` | Initializes project workspace, then runs router | Yes (infrastructure) |
| `/pre-writing` | idea + draft | Yes |
| `/diagnose` | Any artifact + repair (targeted) | Yes |
| `/revision-plan` | Post-diagnostic; not an intake question | Yes |
| `/plot-coach` | Callable from within Pre-Writing or Core DE | Yes |
| `/audit [name]` | Callable from within any workflow | Yes |
| `/research [mode]` | Callable from within any workflow | Yes |

---

## Design Notes

**Why Artifact first.** Writers know what they have before they know what they need. "I have a complete draft" is a fact; "I need structural repair" is a judgment the writer may not be equipped to make. Starting with Artifact grounds the conversation in the concrete.

**Why Goal is conditional.** Offering "check submission readiness" to someone with only an idea wastes their time and suggests the tool doesn't understand their situation. Conditional options demonstrate competence and reduce cognitive load.

**Why Operator is in Q3, not Q1.** Most users are authors. Asking "who are you?" first front-loads a question that 80%+ of users will find trivially obvious. Folding Operator into the modifier question lets editors and facilitators self-identify without burdening the majority.

**Why Constraint is post-routing.** Constraints modify workflows; they don't select them. A deadline doesn't change whether you need Core DE — it changes how Core DE runs. Asking constraints after routing keeps the routing logic clean and the constraint logic modular.

**Gap flags in the route map.** Routes marked "Gap" represent workflows that don't yet exist. When the router hits a gap, it should: (1) acknowledge the gap honestly, (2) offer the closest available workflow, and (3) name what won't be covered. Never silently downgrade.

---

## Implementation Notes

**This document is a specification, not code.** Implementation requires:

1. A new `/start` command file that runs the question sequence
2. Router logic (can be a decision tree in the command file or a separate reference)
3. Updates to each workflow's intake protocol to accept router output (artifact, goal, constraint flags)
4. Dashboard integration (if the HTML dashboard is built, it replaces the text-based question flow)
5. Update to README with the new primary entry point

**Version note:** The router should ship when at least the built workflows (Core DE, Pre-Writing, AI-Prose Calibration) can accept router output. Gap workflows can gracefully degrade to the closest built alternative.
