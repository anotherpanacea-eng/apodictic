# APODICTIC Post-Publication Roadmap

**Date:** 2026-02-22
**Current version:** See `plugins/apodictic/.claude-plugin/plugin.json`

What to build next, organized by priority. UX work gates 1.0; feature additions follow.

---

## v0.5 — UX Overhaul (Pre-1.0)

The command structure reflects framework internals. This release makes the plugin feel like a product. These items gate the 1.0 label — the framework is built, but a newcomer can't navigate it yet.

### Query-Driven Pass Architecture (P1)

Replace the fixed Core DE / Full DE tiering with automatic dependency resolution. Instead of running a predetermined pass sequence, the system resolves "what do I need to run to answer this user's question?" and executes the minimum pass set.

**The problem:** Core DE runs 5 passes. Full DE runs 12. A writer who only has a character question still loads the entire diagnostic machine. Meanwhile, the Core/Full split is an engine-designer distinction — users don't think in terms of "I need the Full DE," they think "my characters feel flat."

**Three layers:**

**1. User-facing macro blocks.** Group the 12 passes into question-shaped clusters that match how writers actually talk about their manuscripts:

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

**2. Dependency tree.** The execution engine that determines what actually runs. Pass 0 (Reverse Outline) is the keystone — almost every other pass depends on it. Two passes have no upstream dependencies and can run in parallel:

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

**3. Execution tiers.** Passes group into three tiers by dependency depth:

- **Tier 1 — Read:** Passes 0, 1, 10. No dependencies on each other. Can run in parallel. Every diagnostic starts here (or a subset).
- **Tier 2 — Analyze:** Passes 2, 3, 4, 5, 6, 7, 8, 9. Each depends on one or more Tier 1 passes. Run only what the query requires.
- **Tier 3 — Synthesize:** Synthesis + Pass 11. Runs after all selected Tier 2 passes complete.

**Query-to-pass routing table:**

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

**What this replaces:** The Core DE / Full DE split disappears. "Core" was just "the passes we run first." "Full" was "Core plus everything else." With query-driven routing, scope is determined by the question, not by a tier label. A character-focused run touches 4 passes; a full diagnostic touches 12. Both are valid scopes — neither is a "lite" or "full" version.

**Skill organization implications:**

The current plugin has one large `core-editor` skill containing all passes. Query-driven execution suggests restructuring:

- **Option A — Dependency map within a single skill.** Keep one `core-editor` skill but add an explicit dependency map (machine-readable YAML or structured markdown) that the execution engine consults. Passes remain defined inline. Simplest to implement; skill file gets longer but stays unified.
- **Option B — Tier-based skill decomposition.** Split into `tier-1-read`, `tier-2-analyze`, `tier-3-synthesize` skills. Each tier loads only when needed. Reduces context window pressure for partial runs but creates coordination overhead.
- **Option C — Pass-cluster skills.** Each macro block becomes its own skill file, with the dependency map in a shared reference. `structure-map` skill loads Passes 0 + 2; `reader-dynamics` loads 1 + 3; etc. Most modular, but risks fragmentation.

**Recommended:** Start with Option A (dependency map within the existing skill). Migrate to Option C only if context window pressure makes single-skill loading impractical. The dependency map is the critical deliverable regardless of which option ships — it's the engine that makes query-driven routing possible.

**What to build:**
- Dependency map (structured reference file: `references/pass-dependencies.md` or `.yaml`)
- Query resolver: given a user concern, output the minimum pass set plus execution order
- Update the intake router to accept concern-based routing (extends Q2 in `intake-router.md`)
- Update `run-core.md` and `run-full.md` to become execution profiles generated from the dependency map rather than fixed pass lists
- Macro block definitions for user-facing output organization (pass results grouped by block, not by number)

**Sequencing note:** This item depends on the Intake Router. The router determines the user's concern; the dependency map determines which passes to run. Build the router first, then layer query-driven execution on top. The two can share a release if the dependency map ships as a reference file and the router adds a concern-classification step to Q2.

### Router Runtime / Design Split (P2)

`intake-router.md` currently serves as both runtime decision table and design document. The full file (~13K bytes) loads on every `/start` invocation, but only the question flow, option sets, and route map are needed at runtime. The design notes, rationale, and gap flags are valuable documentation but consume context window space unnecessarily in early turns — space that could hold more manuscript text.

**What to build:**
- Split `intake-router.md` into two files: `intake-router-runtime.md` (question flow, option tables, route map — the minimum the LLM needs to execute routing) and `intake-router-design.md` (axis model rationale, design notes, gap flags, relationship to commands — reference documentation)
- Update `/start` command to load only the runtime file
- Update all references across the plugin (SKILL.md, changelog, etc.)
- Evaluate other large reference files for similar splits (`run-core.md` at ~26K, `run-full.md` at ~34K, `specialized-audits/SKILL.md` at ~15K)

**Context:** Identified in Codex review (P2 #5, v0.4.17). Deferred because the split touches every file that references `intake-router.md` and benefits most from being done alongside the broader context-window optimization in Query-Driven Pass Architecture below.

### Intake Router Implementation

The router is fully specified in `intake-router.md` — four-axis classification (Artifact × Goal × Operator × Constraint), conditional question flow, deterministic routing, gap-handling protocol. What remains is implementation:

- Wire `/start` to execute the router question sequence
- Update each workflow's intake protocol to accept router output (artifact, goal, constraint flags)
- Build graceful degradation for gap routes (acknowledge honestly, offer closest built workflow, name what won't be covered)
- Decide whether old commands remain as power-user shortcuts or get retired

### Command Restructuring

Current 9 commands expose framework internals. After the router ships, evaluate whether the command set should shrink. Options:

- **Keep all as shortcuts:** `/start` is primary; `/develop-edit`, `/audit`, etc. remain for users who know what they want
- **Retire most:** Only `/start` and `/audit [name]` survive; everything else routes through intake
- **Alias model:** Old commands become aliases that pass arguments to the router

### Scene-Level Handoff Protocol

When the DE diagnoses a scene-level problem, the writer needs a clean exit from framework mode to work with Claude directly on execution. The Firewall stays during diagnosis; after diagnosis, the DE explicitly unloads.

- Define handoff language ("Diagnosis complete. I'm stepping out of editor mode — you can now work with Claude directly on this scene.")
- Ensure the DE skill doesn't accidentally stay loaded during the execution phase
- Consider a `/handoff` command or automatic deactivation trigger

### Framework Overview Dashboard (HTML)

A static, single-file HTML overview of the plugin's capabilities — the map at the trailhead. Not interactive beyond hover/click for descriptions. Not an intake form.

**Build after** the router and command restructuring are settled, so it reflects the final UX.

**Spec (from Publication_Requirements §9):**
- System-at-a-glance: visual layout (flowchart or nested diagram) showing passes, audits, modules, and their relationships
- Routes through the system: highlighted paths for common workflows
- One-sentence descriptions on hover/click
- The Firewall in user-facing language
- The axis model as orientation (not intake)
- Self-contained HTML, no build step, works from filesystem

---

## v1.0 — Public Release Gate ✓

Shipped 2026-02-22. v0.5 UX overhaul complete: query-driven passes, intake router, scene-level handoff, command alias model, overview dashboard. Plugin is navigable by newcomers.

---

## v1.1 — Immediate Post-1.0

High-value additions that extend what's already built. No new architectural decisions required.

### Submission Readiness Workflow (P1)

The most-requested missing workflow. A writer with a finished draft asks "is this ready to submit?" Currently they'd need to know to run Core DE and then separately request Pass 11. The workflow should be a single entry point that runs Core DE → Synthesis → Pass 11, and produces a unified readiness assessment covering structural health, market positioning, and query/synopsis diagnostics.

**What to build:**
- A `/submit` command (or integrate into `/start` routing for `full_draft + submit`)
- Unified output artifact: `[Project]_Submission_Readiness_[runlabel].md`
- Query letter/synopsis diagnostic (currently not built — new capability)
- Readiness verdict: structured recommendation with caveats

### Fast Triage Mode (P2)

A 30-60 minute go/no-go assessment for deadline-constrained writers. Runs Pass 1 (Reader Experience) only, produces a triage memo with maximum 3 interventions. Defers the full diagnostic machine.

**What to build:**
- A `constraint:time` modifier in the intake router (spec exists in `intake-router.md`)
- Truncated Core DE: Pass 1 → triage memo → exit
- Triage memo output template with strict caps (3 interventions, 1-2 pages)
- Clear language: "This is a quick read, not a full edit. Come back when the deadline passes."

---

## v1.2 — Artifact Coverage

Extend the plugin to handle manuscript states beyond "complete draft" and "idea."

### Partial Manuscript Diagnostic (P3)

Writers who are stuck mid-draft. Run passes on available material without penalizing missing structure. Block diagnosis, structural forecasting, "here's what you have and where it's heading."

- Modify Core DE intake to accept partial manuscripts (flag for truncated analysis)
- Pass 0 (Reverse Outline) runs on what exists
- Pass 1 (Reader Experience) notes where momentum stops
- Synthesis focuses on "what's working, what's stalling, where to go next" rather than full triage

### Fragment Synthesis Mode (P3)

Writers with scattered scenes, notes, and fragments but no continuous narrative. Pre-processing step that clusters fragments into candidate contract/spine before Core DE runs.

- Intake: accept multiple files or a single file with marked fragments
- Analysis: identify recurring characters, settings, tensions, tonal patterns
- Output: candidate contract (provisional), recommended spine, fragment map showing what connects and what doesn't
- Route to Pre-Writing Pathway or Core DE depending on what emerges

### Cross-Volume Series Continuity (P3)

Series writers working across multiple books. Diagnostic state persists across volumes. Continuity tracking for character state, world rules, unresolved threads.

- Series-aware intake (load previous volume's diagnostic state)
- Character state tracking across volumes (where did we leave them?)
- World rule ledger that spans books
- Unresolved thread inventory (promises made in book 1 that book 3 still hasn't paid)
- Hope calibration per volume (series-specific)

---

## v1.3 — Goal & Constraint Expansion

### Feedback Triage Workflow (P3)

Writers returning with beta reader or critique group feedback. The DE should help sort, validate, and prioritize external feedback — not rubber-stamp it.

- Intake format for external feedback (paste or file upload)
- Targeted pass execution to test specific claims ("my beta reader says the pacing is off in Act II")
- Prioritized response plan: which feedback to act on, which to question, which to ignore
- Conflict resolution when feedback contradicts itself

### Nonfiction Pre-Draft Pathway (P3)

Argument spine + source/evidence map + scene ethics plan. Separate from fiction pre-writing because nonfiction structure differs fundamentally (thesis-driven, not character-driven).

- Argument spine builder (thesis → evidence → counterargument → synthesis)
- Source/evidence inventory
- Scene ethics plan (for memoir and narrative nonfiction: what to include, what to protect, who gets hurt)
- Routes to Memoir/CNF audit or Narrative Nonfiction audit after drafting

### Formal Risk Register (P4)

Legal/sensitivity risk register for manuscripts with potentially actionable content — defamation concerns, privacy issues, representation risks.

- Extends existing Research Modes (Representation Context, Factual Verification)
- Produces a risk register output with severity levels and escalation triggers
- Clear language: "I'm flagging areas that may need expert review. I am not a lawyer."

---

## v1.4 — Operator Expansion

### Editor Scaffolding Mode (P4)

For human developmental editors using the framework as an analytical assist. Output framing shifts: "here's what I found that you might have missed" rather than "here's what the author should fix."

- Modify output templates: findings framed as "for your editorial letter" not direct-to-author advice
- Suppress prescriptive language (the editor decides what to prescribe)
- Add blind-spot emphasis: highlight things the framework catches that human editors commonly miss (continuity, proportion, promise/payoff economy)

### Diagnostic Vocabulary Mode (P4)

For writing group facilitators who want to teach structural feedback vocabulary. Lightweight framework mode that explains concepts rather than diagnosing manuscripts.

- Glossary/cheat sheet output
- Discussion prompts tied to structural concepts
- "How to talk about pacing without saying 'it feels slow'" — translates framework concepts into workshop vocabulary

### Multi-Party Intake (P4)

For co-authoring teams. Priority conflict resolution, sign-off workflow, change ledger.

- When authors disagree on the contract, surface the disagreement rather than averaging
- Change ledger: track who approved what
- Not expected to be high-demand. Build only if user feedback indicates need.

---

## v1.5 — Format & Cadence

### Episode Cadence Workflow (P4)

For web serial and newsletter fiction writers. Hook debt tracking, recap burden analysis, season pivots, retention checkpoints.

- Serialization-specific diagnostics (does each installment work standalone AND advance the series?)
- Hook debt inventory (promises made across episodes)
- Recap burden analysis (how much re-establishing does each episode need?)
- Season arc structure (if applicable)

---

## Ongoing: Genre Audit Expansion

New specialized audits should be built from real editorial engagements, not hypothetical coverage. Each manuscript-in-genre that runs through the plugin surfaces what a genre's audit actually needs.

**Expansion protocol** (codified in `Specialized_Audit_Expansion_Stub_TEMPLATE.md`):
1. Level-setting research phase (cognitive narratology, genre theory, reader-experience evidence, positive cases)
2. Structural spec phase (named flags, dimensions, hard gates, subgenre calibrations, distinguish framework)
3. Three-model synthesis for quality assurance

**Seeded candidates** — reference texts identified, ready for level-setting when manuscripts demand them:

**YA / Kidlit (genre module).** No age-targeted module exists. Needs: protagonist age-authority dynamics, voice register calibration (too-adult vs. condescending), first-experience plot drivers, pacing expectations distinct from adult fiction. One module with MG/YA subgenre variation (like Literary handles realist vs. experimental), since pass modifications overlap and differences are mostly severity thresholds and voice calibration.
- Mary Kole — *Writing Irresistible Kidlit*
- Deborah Halverson — *Writing Young Adult Fiction For Dummies*

**Supernatural Horror (genre module).** Explicitly flagged in `genre-horror.md` as distinct from Psychological Horror and not yet built. Needs different machinery from psych horror: rule consistency for supernatural systems (borrows SFF Rule Ledger logic), escalation through revelation rather than destabilization, uncanny-to-confirmed spectrum. Shares the Horror Craft audit but loads different pass modifications.
- Tim Waggoner — *Writing in the Dark*
- Mort Castle (ed.) — *On Writing Horror*
- Dan Coxon (ed.) — *Writing the Uncanny* (strongest for uncanny/supernatural logic flags)

**Grimdark / Dark Fantasy (tag audit, not genre module).** Tonal modifier that layers onto Fantasy, Historical Fiction, or Literary — same architecture as Cozy Tag and Philosophical Tag. Core diagnostic: is grimness load-bearing or decorative? Is consequence functioning as world-logic or aesthetic wallpaper?
- Rayne Hall — *Writing Dark Stories* (darkness dial / consequence calibration)
- Jeff VanderMeer — *Wonderbook* (world texture / strangeness-as-craft — also has SFF worldbuilding value)

**Military / War Fiction Plausibility (audit or research mode — scope TBD).** Narrower than the others. Needs: tactical plausibility, violence-meaning relationship (Force Architecture covers some), institutional voice, deployment-narrative pacing. May be better as a subgenre variation within Historical Fiction or as a specialized research mode rather than a full standalone audit. Build only if demand materializes.
- Benjamin Sobieck — *The Writer's Guide to Weapons* (plausibility/risk-flag reference)

**Dialectical Clarity enrichment (audit deepening, not new build).** Dialectical Clarity and Banister audits already exist. Graff & Birkenstein and Heinrichs would enrich the existing audit rather than create something new. The larger gap is the Franklin Class 3 path ("Argument With Embedded Narrative"), which is stubbed but not built — that's a v1.3 item (Nonfiction Pre-Draft Pathway). Deepen the existing audit first; let Class 3 come with v1.3.
- Graff & Birkenstein — *They Say / I Say*
- Jay Heinrichs — *Thank You for Arguing*

**Unseeded candidates** (no reference texts yet — build when manuscripts demand them):
- Western
- Thriller subtypes (medical, techno, eco)
- Children's/Middle Grade (structural differences from YA — may fold into YA/Kidlit module)
- Poetry (entirely different analytical framework)
- Graphic novel/comics (visual storytelling integration)
- Interactive fiction / game narrative
- Translations (diagnostic for prose that's been through a translation layer)

---

## Not Planned (Tracked for Reference)

These have been discussed but are not on the roadmap:

- **Live project dashboard** (reads from output files to show diagnostic state in real time) — separate product, not a plugin feature
- **Prose execution mode** (the DE rewrites scenes) — violates the Firewall; explicitly out of scope
- **Line editing / copyediting** — different discipline, different tooling
- **Commercial viability guarantees** — the plugin diagnoses structure, not market outcomes
