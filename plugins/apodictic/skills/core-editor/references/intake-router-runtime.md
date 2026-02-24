# Intake Router — Runtime

**Status:** Implementation-ready
**For:** APODICTIC Development Editor v0.5
**Last updated:** 2026-02-22

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

**Swarm mode recommendation:** When the user selects option B (submission readiness), suggest swarm mode in §3 if they haven't already selected it: "Since this is a final-round assessment before submission, you may want to consider swarm mode — it produces deeper analysis at higher token cost. Want to add that?" This is a suggestion, not a default.

### If Artifact = `series`

"What kind of series help?"

| Option | Label | Route |
|--------|-------|-------|
| A | Work on one book (the current volume) | Re-ask Q1 for the specific volume, with series context noted |
| B | Check continuity across volumes | Series Continuity Audit |
| C | Plan the series arc or the next volume | Pre-Writing Pathway (series-aware mode) |

---

## §3. Question 3: Anything that should change how we work?

*Axis: Constraint + Operator modifiers*

Always asked after routing, before work begins. Multiple selections allowed.

"Before we start — anything I should know?"

| Option | Label | Internal flag | Effect on workflow |
|--------|-------|--------------|-------------------|
| A | I'm on a deadline | `constraint:time` | Truncate to fast triage: Pass 1 only → triage memo with max 3 interventions. |
| B | Parts of this were written with AI | `constraint:ai` | Add AI-Prose Calibration overlay. |
| C | This is nonfiction | `constraint:nonfiction` | Swap fiction-specific passes for nonfiction equivalents. **Gap: nonfiction pathway not yet built.** |
| D | There's sensitive or legally risky content | `constraint:risk` | Add risk register output. **Gap: risk register not yet built.** |
| E | I'm editing someone else's work | `operator:editor` | Shift output to editor scaffolding. **Gap: editor mode not yet built.** |
| F | I'm facilitating a writing group | `operator:facilitator` | Shift to diagnostic vocabulary mode. **Gap: facilitator mode not yet built.** |
| G | We're co-authoring (multiple writers) | `operator:team` | Note conflicting-vision risk. **Gap: multi-party intake not yet built.** |
| H | Use swarm mode (deeper analysis, higher token cost) | `execution:swarm` | Each pass runs as an independent subagent. ~2x findings, ~5x token cost. See `run-core.md` §Execution Mode. |
| I | No constraints — let's go | (none) | Proceed with standard workflow. |

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

## §5. Command Shortcuts

Existing commands bypass the router with pre-filled values. The router is the recommended entry for new users; shortcuts are for users who know what they want.

| Command | Router equivalent |
|---------|-------------------|
| `/start` | The router itself |
| `/develop-edit` | artifact=`full_draft`, goal=`repair` |
| `/new-project` | Initialize project, then run router |
| `/pre-writing` | artifact=`idea`, goal=`draft` |
| `/diagnose` | Any artifact, goal=`repair` (targeted) |
| `/revision-plan` | Post-diagnostic (not an intake question) |
| `/plot-coach` | Callable from within workflows |
| `/audit [name]` | Callable from within workflows |
| `/research [mode]` | Callable from within workflows |

---

## §6. Complete Route Map

| Artifact | Goal | Constraint/Operator | Workflow | Status |
|----------|------|-------------------|----------|--------|
| idea | draft | — | Pre-Writing Pathway | **Built** |
| idea | draft (fast-track) | — | Pre-Writing Pathway (skip to Phase 4) | **Built** |
| idea | draft | nonfiction | Nonfiction Pre-Writing | Gap |
| fragments | draft | — | Fragment Synthesis → Pre-Writing | Gap (Pre-Writing fallback available) |
| fragments | draft | ai | Fragment Synthesis → Pre-Writing + AI-Prose Calibration | Gap (partial) |
| fragments | repair | — | Core DE (partial flag) | Gap: partial manuscript diagnostic |
| partial | repair (diagnostic) | — | Core DE (partial flag) | Gap: partial manuscript diagnostic |
| partial | repair (targeted) | — | Core DE (partial flag, targeted) | Gap: partial manuscript diagnostic |
| partial | draft (rethink) | — | Pre-Writing Pathway (re-entry) | **Built** |
| partial | repair | time | Fast Triage | Gap |
| full_draft | repair | — | Core DE | **Built** |
| full_draft | repair | swarm | Core DE (swarm mode) | **Built** |
| full_draft | repair | time | Fast Triage | Gap |
| full_draft | repair | ai | Core DE + AI-Prose Calibration | **Built** |
| full_draft | repair | risk | Core DE + Risk Register | Gap |
| full_draft | submit | — | Core DE → Pass 11 (swarm suggested) | Gap: unified submission workflow |
| full_draft | submit | swarm | Core DE → Pass 11 (swarm mode) | **Built** |
| full_draft | submit | time | Fast Triage (submission focus) | Gap |
| full_draft | repair | editor | Core DE (editor scaffolding) | Gap |
| full_draft | repair | facilitator | Core DE (diagnostic vocabulary) | Gap |
| full_draft | repair (feedback) | — | Feedback Triage → Core DE | Gap |
| series | repair (single vol) | — | Core DE (series context) | Partially built |
| series | repair (continuity) | — | Series Continuity Audit | Gap |
| series | draft (plan next) | — | Pre-Writing Pathway (series-aware) | Partially built |

## §7. Gap Handling Protocol

When the router resolves to a gap route:

1. **Acknowledge honestly.** Name the specific workflow that doesn't exist yet.
2. **Offer the closest built workflow.** State what it will cover and what it won't.
3. **Name what won't be covered.** Be specific: "This won't include [X] because that workflow isn't built yet."

Never silently downgrade. The user should always know when they're getting a substitute.

---

*This file is a runtime reference. Design rationale is in `intake-router-design.md`.*
