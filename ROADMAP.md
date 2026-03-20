# APODICTIC Roadmap

**Current version:** See `plugins/apodictic/.claude-plugin/plugin.json`

---

## Board

| In Progress | Planned | Done | Backlog |
|-------------|---------|------|---------|
| [Genre Audit Expansion](#genre--audit-expansion) | [Editor Scaffolding](#editor-scaffolding) | [v1.2.1](#v121--audit-sequencing--model-tags) | [Feedback Triage](#feedback-triage) |
| [Coaching Deepening](#coaching-deepening) | [Diagnostic Vocabulary](#diagnostic-vocabulary-mode) | [v1.2.0](#v120--artifact-coverage) | [Nonfiction Pre-Draft](#nonfiction-pre-draft-pathway) |
| [Nonfiction Argument Engine](#nonfiction-argument-engine) | [Writer's Block & Rut-Breaking](#writers-block--rut-breaking) | [v1.1.3](#v113--coaching-deepening) | [Legal Risk Register](#legal-risk-register) |
| | | [v1.1.2](#v112--revision-coach) | [Multi-Party Intake](#multi-party-intake) |
| | | [v1.1.1](#v111--series-continuity--pass-9) | [Episode Cadence](#episode-cadence) |
| | | [v1.1.0](#v110--token-aware-agent-usage) | [Collaborative Revision Coaching](#collaborative-revision-coaching) |
| | | [v1.0.9](#v109) | [Framework Overview Dashboard](#framework-overview-dashboard) |
| | | [v1.0.8](#v108) | [Pre-Skill Context Compaction](#pre-skill-context-compaction) |
| | | [v1.0.4](#v104) | [Command Surface Evaluation](#command-surface-evaluation) |
| | | [v1.0](#v10--public-release) | [Output Organization by Question](#output-organization-by-question) |
| | | | [Skill Boundary Evaluation](#skill-boundary-evaluation) |

---

## Genre & Audit Expansion

New specialized audits built from real editorial engagements, not hypothetical coverage. Each manuscript-in-genre that runs through the plugin surfaces what a genre's audit actually needs.

**Expansion protocol** (codified in `Specialized_Audit_Expansion_Stub_TEMPLATE.md`):
1. Level-setting research phase (cognitive narratology, genre theory, reader-experience evidence, positive cases)
2. Structural spec phase (named flags, dimensions, hard gates, subgenre calibrations, distinguish framework)
3. Three-model synthesis for quality assurance — validated with Reception Risk (v1.0.9)

**Seeded candidates** — reference texts identified, ready for level-setting:

**YA / Kidlit (genre module).** Protagonist age-authority dynamics, voice register calibration (too-adult vs. condescending), first-experience plot drivers, pacing expectations distinct from adult fiction. One module with MG/YA subgenre variation.
- Mary Kole — *Writing Irresistible Kidlit*
- Deborah Halverson — *Writing Young Adult Fiction For Dummies*

**Supernatural Horror (genre module).** Rule consistency for supernatural systems (borrows SFF Rule Ledger logic), escalation through revelation rather than destabilization, uncanny-to-confirmed spectrum. Shares Horror Craft audit but loads different pass modifications.
- Tim Waggoner — *Writing in the Dark*
- Mort Castle (ed.) — *On Writing Horror*
- Dan Coxon (ed.) — *Writing the Uncanny*

**Grimdark / Dark Fantasy (tag audit).** Tonal modifier layering onto Fantasy, Historical Fiction, or Literary. Core diagnostic: is grimness load-bearing or decorative?
- Rayne Hall — *Writing Dark Stories*
- Jeff VanderMeer — *Wonderbook*

**Military / War Fiction Plausibility (scope TBD).** Tactical plausibility, violence-meaning relationship, institutional voice. May be a subgenre variation within Historical Fiction or a specialized research mode. Build only if demand materializes.
- Benjamin Sobieck — *The Writer's Guide to Weapons*

**Nonfiction Argument Engine (codex54 build in progress).** Dialectical Clarity has been promoted into the core argument kernel and now has a shared `Argument_State` schema. Next build phases are Argument Red Team, nonfiction routing in intake, Argument Persuasion, Evidence Deep-Dive, and Revision Coach argument mode.
- Core shipped: Dialectical Clarity v2.0 + `docs/argument-state-schema.md`
- Next: `argument-red-team.md`, router integration, persuasion and evidence companions, revision-coach argument mode

**Unseeded candidates** (build when manuscripts demand them):
- Western
- Thriller subtypes (medical, techno, eco)
- Children's/Middle Grade (may fold into YA/Kidlit)
- Poetry (entirely different analytical framework)
- Graphic novel/comics
- Interactive fiction / game narrative
- Translations (diagnostic for prose through a translation layer)

---

## Nonfiction Argument Engine

APODICTIC now has the kernel of a full nonfiction and persuasive-argument workflow:

1. Dialectical Clarity v2.0 as the canonical diagnostic audit
2. `Argument_State.md` as the shared artifact
3. companion-module architecture for red-team, persuasion, evidence, and coaching

### Current status

**Built**

1. Dialectical Clarity v2.0 + level-setting research
2. `docs/argument-state-schema.md` (v0.1.1)
3. Argument Red Team (v1.0) + level-setting research
4. Argument Persuasion + level-setting research
5. Argument Evidence Deep-Dive
6. Nonfiction routing in intake (runtime + design docs)
7. Revision Coach argument mode (8 coaching tracks + argument session plan template)

**Next**

1. Argument Engine Benchmark Suite

### Benchmark Suite

Validate that the engine works on real argument-shaped nonfiction, not just in theory. Corpus-based testing against manuscripts where the correct structural diagnosis is already known.

**Corpus buckets:**
1. Op-eds
2. Policy briefs
3. Testimony (legislative, judicial, administrative)
4. Personal essays with implicit argument
5. Academic argument
6. Advocacy journalism
7. Argument-with-embedded-narrative hybrids

**Test questions:**
1. Did the system recover the actual main claim?
2. Did it correctly distinguish support failure from warrant failure?
3. Did it identify the strongest real objection?
4. Did audience calibration improve rather than distort diagnosis?
5. Did red-team output surface genuinely dangerous weaknesses?
6. Did coaching produce a useful repair order?
7. Did the system avoid penalizing unconventional but effective form?

**Success condition:** Two serious editors using the engine independently should usually converge on the core claim, the top 1–3 structural failures, the main burden mismatch, and the strongest objection zone.

### Design principle

Treat Dialectical Clarity as the kernel, not the whole operating system. Companion modules should read `Argument_State.md` rather than rebuilding the argument from scratch.

---

## Coaching Deepening

The core Revision Coach shipped in v1.1.2 with four modes (Session Planning, Stuck-Point Coaching, Momentum Tracking, Deadline Coaching) and was deepened in v1.1.3 (Guidance Without Specification stance, block diagnosis, exercise library) and v1.2.0 (partial manuscript coaching). Further deepening based on real usage:

### Multi-Session Revision Arc Planning

Session Planning currently operates one session at a time. Arc Planning would produce a multi-week revision strategy: phase 1 tackles structural root causes, phase 2 handles downstream consequences, phase 3 addresses polish. The arc adapts as earlier phases reveal new issues.

### Genre-Specific Coaching Calibration

Adjust coaching behavior by genre: romance coaching emphasizes emotional-arc leverage; thriller coaching emphasizes pacing-first sequencing; literary coaching allows longer stuck-point exploration. Builds on the existing genre module system.

### Writer's Block & Rut-Breaking

Structurally informed prompts tied to specific diagnosed problems. Extends Stuck-Point Coaching from reactive reframing to proactive prompt generation (still within the firewall — prompts surface structural possibility, not content).

### Coaching History and Pattern Recognition

Over multiple revision cycles, surface patterns: "You tend to defer character-agency work — three consecutive session plans without completion." Privacy-sensitive — observations, not judgments.

---

## Operators

### Editor Scaffolding

For human developmental editors using the framework as analytical assist. Output framing shifts to "here's what I found that you might have missed." Suppress prescriptive language, add blind-spot emphasis.

### Diagnostic Vocabulary Mode

For writing group facilitators who want to teach structural feedback vocabulary. Glossary/cheat sheet output, discussion prompts tied to structural concepts.

### Multi-Party Intake

For co-authoring teams. Priority conflict resolution, sign-off workflow, change ledger. Build only if user feedback indicates need.

---

## Workflows

### Feedback Triage

Writers returning with beta reader or critique group feedback. Sort, validate, and prioritize external feedback. Targeted pass execution to test specific claims, conflict resolution when feedback contradicts itself.

### Nonfiction Pre-Draft Pathway

Argument spine + source/evidence map + scene ethics plan. Separate from fiction pre-writing because nonfiction structure is thesis-driven, not character-driven.

### Legal Risk Register

Defamation concerns in memoir/autofiction, privacy issues for identifiable individuals, rights clearance flags. Produces a legal risk register with severity levels and escalation triggers. "I'm flagging areas that may need legal review. I am not a lawyer."

### Episode Cadence

For web serial and newsletter fiction writers. Hook debt tracking, recap burden analysis, season pivots, retention checkpoints. Each installment must work standalone AND advance the series.

### Collaborative Revision Coaching

For co-authoring teams or author-editor pairs working through a diagnostic together. Priority conflict resolution, sign-off workflow, change ledger. Build only if demand materializes.

---

## Infrastructure

### Framework Overview Dashboard

Static, single-file HTML overview of the plugin's capabilities. System-at-a-glance visual layout, highlighted workflow paths, the Firewall in user-facing language. Build after command restructuring is settled.

### Pre-Skill Context Compaction

**Status:** Largely resolved by platform. 1M context on Opus 4.6 + Claude Code's built-in auto-compression. A dedicated pre-skill compaction hook remains a nice-to-have if Claude Code adds skill-lifecycle events.

---

## UX & Command Restructuring

Continuing the v0.5 vision: the plugin should be organized around writer questions, not framework internals. The query-driven pass architecture and intake router shipped in v1.0, but the command surface, output naming, and skill boundaries still reflect build history.

### Command Surface Evaluation

Are 11 commands the right surface? The alias model works (most commands are shortcuts into `/start` with pre-filled values) but hasn't been evaluated against real usage. Questions to answer: Do writers use the shortcuts, or do they always go through `/start`? Should most commands retire in favor of `/start` + `/audit`? Is the current command set discoverable or overwhelming?

### Output Organization by Question

The editorial letter groups findings by macro block (Structure Map, Reader Dynamics, Character Architecture, etc.), but pass artifacts are still named by pass number (`Pass5_Character_Audit`, `Pass7_POV_Voice`). A writer looking for "what's wrong with my characters" has to know that means Pass 5 + Pass 7. Evaluate whether output artifacts should be named by macro block instead of pass number — or whether the current naming is fine because writers interact with the editorial letter, not individual pass files.

### Skill Boundary Evaluation

Five skills (core-editor, pre-writing-pathway, plot-architecture, specialized-audits, revision-coach) reflect the order they were built, not necessarily how writers navigate. Evaluate whether the boundaries match usage patterns. The main question: does a writer ever hit a skill boundary and feel lost? If skill loading is invisible to the user (which it mostly is), this may be a non-issue.

---

## Not Planned

- **Live project dashboard** — separate product, not a plugin feature
- **Prose execution mode** — violates the Firewall; explicitly out of scope
- **Line editing / copyediting** — different discipline, different tooling
- **Commercial viability guarantees** — the plugin diagnoses structure, not market outcomes

---

## Done

### v1.2.1 — Audit Sequencing & Model Tags
Auto-run audits as synthesis dependencies (fixes multi-story collection sequencing bug). Model-tag required in output filenames.

### v1.2.0 — Artifact Coverage
Partial Manuscript Diagnostic (six stall causes, momentum report, setup inventory). Fragment Synthesis Mode (clustering, connection mapping, candidate structure). Router gaps filled for fragments and partial drafts.

### v1.1.3 — Coaching Deepening
Guidance Without Specification stance. Three-way stuck-point block diagnosis. Exercise library (6 exercises). Anti-chronological revision. Pause/Paraphrase/Probe.

### v1.1.2 — Revision Coach
Fourth companion skill. Session Planning, Stuck-Point Coaching, Momentum Tracking, Deadline Coaching. Coaching firewall with drift check.

### v1.1.1 — Series Continuity & Pass 9
Cross-Volume Series Continuity Audit (5 channels, 24 flags, 7 decision tests). Pass 9 deepened (8 failure modes, semantic threading). Three-model level-setting brief.

### v1.1.0 — Token-Aware Agent Usage
Submission Readiness Workflow. Submission Triage. Context-aware single-agent execution for 1M windows.

### v1.0.9
Reception Risk Audit (17 flags, 5 channels, three-model synthesis). Voice Distinctiveness Comparison. Title/Framing Architecture. Release tooling.

### v1.0.8
Compression Audit.

### v1.0.4
Subagent Pass Orchestration (swarm mode).

### v1.0 — Public Release
Query-driven passes, intake router, scene-level handoff, command alias model, overview dashboard.
