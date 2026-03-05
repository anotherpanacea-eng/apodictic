# Query-Driven Pass Architecture — Design Spec

**Status:** Planned (v0.5)
**Summary in ROADMAP.md:** [link](../ROADMAP.md#query-driven-pass-architecture)

---

## Problem

Core DE runs 5 passes. Full DE runs 12. A writer who only has a character question still loads the entire diagnostic machine. The Core/Full split is an engine-designer distinction — users don't think in terms of "I need the Full DE," they think "my characters feel flat."

## Three Layers

### 1. User-Facing Macro Blocks

Group the 12 passes into question-shaped clusters that match how writers actually talk about their manuscripts:

| Macro Block | Internal Passes | User Question |
|-------------|----------------|---------------|
| Structure Map | 0 + 2 | "Is the structure working?" |
| Reader Dynamics | 1 + 3 | "Does the pacing hold?" |
| Character Architecture | 5 (+ 4 when emotionally driven) | "Are my characters landing?" |
| Scene Delivery | 6 + 7 | "Are the scenes doing their jobs?" |
| Reveal Economy | 8 | "Is the information flow right?" |
| Theme & Continuity | 9 + 10 | "Does it cohere?" |
| Submission Readiness | 11 | "Is this ready?" |

Writers see 7 blocks, not 12 passes. Each block has a plain-language name and a question it answers.

### 2. Dependency Tree

The execution engine that determines what actually runs. Pass 0 (Reverse Outline) is the keystone — almost every other pass depends on it. Two passes have no upstream dependencies and can run in parallel:

| Pass | Depends on |
|------|-----------|
| 0 (Reverse Outline) | nothing — reads the manuscript |
| 1 (Reader Experience) | nothing — reads the manuscript |
| 10 (Entity Tracking) | nothing — reads the manuscript |
| 2 (Structural Mapping) | 0 |
| 3 (Rhythm & Modulation) | 0, 1 |
| 4 (Emotional Dynamics) | 0, 1 |
| 5 (Character Audit) | 0 |
| 6 (Scene Function) | 0, 2 |
| 7 (Dialogue & Voice) | 0, 5 |
| 8 (Reveal Economy) | 0 |
| 9 (Thematic Coherence) | 0, 5 |
| 11 (Market Positioning) | 0, 1, 2, 5 (runs after synthesis) |

When a user asks a character question, the engine resolves: Pass 5 needs Pass 0. Pass 7 (Dialogue) needs Pass 0 and Pass 5. Pass 1 adds reader-experience grounding. Result: run {0, 1, 5, 7}, skip the other eight.

### 3. Execution Tiers

Passes group into three tiers by dependency depth:

- **Tier 1 — Read:** Passes 0, 1, 10. No dependencies on each other. Can run in parallel. Every diagnostic starts here (or a subset).
- **Tier 2 — Analyze:** Passes 2, 3, 4, 5, 6, 7, 8, 9. Each depends on one or more Tier 1 passes. Run only what the query requires.
- **Tier 3 — Synthesize:** Synthesis + Pass 11. Runs after all selected Tier 2 passes complete.

## Query-to-Pass Routing Table

| User concern | Minimum pass set |
|-------------|-----------------|
| Structure / architecture | 0, 2 |
| Pacing / momentum | 0, 1, 3 |
| Characters / agency / arc | 0, 1, 5, 7 |
| Information flow / reveals | 0, 1, 8 |
| Scene craft / function | 0, 2, 6, 7 |
| Theme / coherence / meaning | 0, 5, 9, 10 |
| Emotional dynamics / interiority | 0, 1, 4 |
| "Everything" / full diagnostic | all passes |
| "Is this ready to submit?" | all passes + 11 |

## What This Replaces

The Core DE / Full DE split disappears. "Core" was just "the passes we run first." "Full" was "Core plus everything else." With query-driven routing, scope is determined by the question, not by a tier label. A character-focused run touches 4 passes; a full diagnostic touches 12. Both are valid scopes — neither is a "lite" or "full" version.

## Skill Organization Options

The current plugin has one large `core-editor` skill containing all passes. Query-driven execution suggests restructuring:

- **Option A — Dependency map within a single skill.** Keep one `core-editor` skill but add an explicit dependency map (machine-readable YAML or structured markdown) that the execution engine consults. Passes remain defined inline. Simplest to implement; skill file gets longer but stays unified.
- **Option B — Tier-based skill decomposition.** Split into `tier-1-read`, `tier-2-analyze`, `tier-3-synthesize` skills. Each tier loads only when needed. Reduces context window pressure for partial runs but creates coordination overhead.
- **Option C — Pass-cluster skills.** Each macro block becomes its own skill file, with the dependency map in a shared reference. `structure-map` skill loads Passes 0 + 2; `reader-dynamics` loads 1 + 3; etc. Most modular, but risks fragmentation.

**Recommended:** Start with Option A (dependency map within the existing skill). Migrate to Option C only if context window pressure makes single-skill loading impractical. The dependency map is the critical deliverable regardless of which option ships — it's the engine that makes query-driven routing possible.

## What to Build

- Dependency map (structured reference file: `references/pass-dependencies.md` or `.yaml`)
- Query resolver: given a user concern, output the minimum pass set plus execution order
- Update the intake router to accept concern-based routing (extends Q2 in `intake-router.md`)
- Update `run-core.md` and `run-full.md` to become execution profiles generated from the dependency map rather than fixed pass lists
- Macro block definitions for user-facing output organization (pass results grouped by block, not by number)

## Sequencing

This item depends on the Intake Router. The router determines the user's concern; the dependency map determines which passes to run. Build the router first, then layer query-driven execution on top. The two can share a release if the dependency map ships as a reference file and the router adds a concern-classification step to Q2.
