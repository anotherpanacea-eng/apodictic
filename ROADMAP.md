# APODICTIC Roadmap

**Current version:** See `plugins/apodictic/.claude-plugin/plugin.json`

---

## v0.5 — UX Overhaul

The command structure reflects framework internals. This release makes the plugin feel like a product to newcomers.

### Query-Driven Pass Architecture

Replace the fixed Core DE / Full DE tiering with automatic dependency resolution. Instead of running a predetermined pass sequence, the system resolves "what do I need to run to answer this user's question?" and executes the minimum pass set.

**The problem:** Core DE runs 5 passes. Full DE runs 12. A writer who only has a character question still loads the entire diagnostic machine. The Core/Full split is an engine-designer distinction — users think "my characters feel flat," not "I need the Full DE."

**The approach:** Group the 12 passes into question-shaped macro blocks (Structure Map, Reader Dynamics, Character Architecture, Scene Delivery, Reveal Economy, Theme & Continuity, Submission Readiness). Build a dependency tree so the engine resolves pass sets from user concerns — a character question runs {0, 1, 5, 7}, not all 12. Start with a dependency map inside the existing skill; migrate to per-block skills only if context window pressure demands it.

**What to build:** Dependency map (structured reference file), query resolver, intake router integration, updated `run-core.md` and `run-full.md` as execution profiles generated from the dependency map, macro block definitions for user-facing output organization. Full design spec with dependency tree, routing table, and skill organization options in [`docs/query-driven-pass-architecture.md`](docs/query-driven-pass-architecture.md).

### Intake Router Implementation

The router is fully specified in `intake-router.md` — four-axis classification, conditional question flow, deterministic routing, gap-handling protocol. What remains: wire `/start` to execute the question sequence, update each workflow's intake protocol to accept router output, build graceful degradation for gap routes, decide whether old commands remain as shortcuts or get retired.

### Command Restructuring

Current 9 commands expose framework internals. After the router ships, evaluate whether to keep all as shortcuts, retire most (only `/start` and `/audit [name]` survive), or use an alias model.

### Scene-Level Handoff Protocol

When the DE diagnoses a scene-level problem, the writer needs a clean exit from framework mode to work with Claude directly on execution. Define handoff language, ensure the DE skill doesn't accidentally stay loaded during the execution phase, consider a `/handoff` command or automatic deactivation trigger.

### Framework Overview Dashboard (HTML)

A static, single-file HTML overview of the plugin's capabilities — the map at the trailhead. System-at-a-glance visual layout, highlighted workflow paths, one-sentence descriptions on hover/click, the Firewall in user-facing language. Build after the router and command restructuring are settled.

---

## v1.1 — Immediate Post-1.0

High-value additions that extend what's already built. No new architectural decisions required.

### Submission Readiness Workflow

The most-requested missing workflow. A writer with a finished draft asks "is this ready to submit?" Currently they'd need to know to run Core DE and then separately request Pass 11. Build a single entry point (`/submit` or integrated into `/start` routing) that runs Core DE → Synthesis → Pass 11, and produces a unified readiness assessment with query letter/synopsis diagnostic and structured readiness verdict.

### Submission Triage

A fast go/no-go assessment for deadline-constrained writers. Runs Pass 1 (Reader Experience) only, applies SR codes to what surfaces, and produces a triage memo. No artificial intervention cap — if Pass 1 surfaces more than 3 P1-severity issues, the answer is "no go" with reasons. Three or fewer means "go, fix these."

Includes a mandatory **blind spots** section naming what a single-pass read cannot assess (spine integrity, subplot load-bearing, act-ratio calibration, entity continuity). Not a disclaimer footer — a specific inventory of what's dark.

---

## v1.2 — Artifact Coverage

Extend the plugin to handle manuscript states beyond "complete draft" and "idea."

### Partial Manuscript Diagnostic

Writers stuck mid-draft. Run passes on available material without penalizing missing structure. Pass 0 runs on what exists, Pass 1 notes where momentum stops, synthesis focuses on "what's working, what's stalling, where to go next."

### Fragment Synthesis Mode

Writers with scattered scenes, notes, and fragments but no continuous narrative. Pre-processing step that clusters fragments into candidate contract/spine before Core DE runs. Output: candidate contract (provisional), recommended spine, fragment map showing what connects and what doesn't.

### Cross-Volume Series Continuity

Series writers working across multiple books. Diagnostic state persists across volumes. Character state tracking, world rule ledger, unresolved thread inventory, hope calibration per volume.

---

## v1.3 — Goal & Constraint Expansion

### Feedback Triage Workflow

Writers returning with beta reader or critique group feedback. The DE helps sort, validate, and prioritize external feedback. Targeted pass execution to test specific claims, prioritized response plan, conflict resolution when feedback contradicts itself.

### Nonfiction Pre-Draft Pathway

Argument spine + source/evidence map + scene ethics plan. Separate from fiction pre-writing because nonfiction structure differs fundamentally (thesis-driven, not character-driven).

### Legal Risk Register

Legal risk register for manuscripts with potentially actionable content — defamation concerns in memoir/autofiction, privacy issues for identifiable individuals, rights clearance flags for quoted material. Reception Risk (v1.0.9) already covers the cultural/reception side; this addresses the legal side. Produces a legal risk register with severity levels and escalation triggers. Clear language: "I'm flagging areas that may need legal review. I am not a lawyer."

---

## v1.4 — Operator Expansion

### Editor Scaffolding Mode

For human developmental editors using the framework as analytical assist. Output framing shifts to "here's what I found that you might have missed." Suppress prescriptive language, add blind-spot emphasis.

### Diagnostic Vocabulary Mode

For writing group facilitators who want to teach structural feedback vocabulary. Glossary/cheat sheet output, discussion prompts tied to structural concepts.

### Multi-Party Intake

For co-authoring teams. Priority conflict resolution, sign-off workflow, change ledger. Build only if user feedback indicates need.

---

## v1.5 — Format & Cadence

### Episode Cadence Workflow

For web serial and newsletter fiction writers. Hook debt tracking, recap burden analysis, season pivots, retention checkpoints. Each installment must work standalone AND advance the series.

---

## v2.0 — Revision Coach

The diagnostic editor tells you what's wrong. The coaching editor helps you figure out what to do about it — without doing it for you. v2.0 adds a coaching layer that draws on existing diagnostic state to help writers move from diagnosis to the next productive draft session.

The core design constraint: coaching stays on the writer's side of the line. "Here's a way to think about solving this" rather than "here's the solution." A coach that writes your revision is a ghostwriter with extra steps. A coach that helps you see your own path through a diagnosed problem is something writers come back to.

### Revision Coach

Time-boxed revision planning built on diagnostic state. "You have an hour — here's where to spend it." Not a diagnostic; a prioritization layer that assumes you've already run some or all of the edit. Time-budget input, priority engine ranking issues by leverage, session plan output, re-assessment trigger.

### Writer's Block & Rut-Breaking

Structurally informed prompts for writers who are stuck. Unlike generic writing prompts, these are tied to specific diagnosed problems — "you're stuck because the protagonist's choice in chapter 12 isn't a real choice; here are three ways to think about making it one." Stuck-point diagnosis, prompt generation tied to SR codes and pass findings, escalation path.

### Deadline Management

For writers with a hard deadline and a diagnosed manuscript. Produces a revision calendar that sequences interventions by priority and available time. Honest about what's achievable and what isn't.

---

## Execution Architecture (Ongoing)

Architectural changes to how the plugin executes, not what it diagnoses.

### Pre-Skill Context Compaction

Before loading the skill and manuscript, compact prior conversation history to reclaim context space. Currently requires the user to manually run `/compact`. Ideally would be a pre-skill hook in the plugin manifest — request this as a platform feature.

### Token-Adaptive Run Profiles

The execution engine detects available context budget and adjusts the run profile accordingly. Short manuscripts get full subagent treatment; long manuscripts get selective reading; very long manuscripts get a warning and a recommendation to use Submission Triage (v1.1) instead.

---

## Ongoing: Genre Audit Expansion

New specialized audits should be built from real editorial engagements, not hypothetical coverage. Each manuscript-in-genre that runs through the plugin surfaces what a genre's audit actually needs.

**Expansion protocol** (codified in `Specialized_Audit_Expansion_Stub_TEMPLATE.md`):
1. Level-setting research phase (cognitive narratology, genre theory, reader-experience evidence, positive cases)
2. Structural spec phase (named flags, dimensions, hard gates, subgenre calibrations, distinguish framework)
3. Three-model synthesis for quality assurance — validated with Reception Risk (v1.0.9): Opus 4.6 and Codex 5.3 independently produced research from identical expansion stubs, outputs compared and synthesized, Gemini 2.5 Pro contributed Stuart Hall's encoding/decoding model as a third-source addition

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

## Not Planned

These have been discussed but are not on the roadmap:

- **Live project dashboard** (reads from output files to show diagnostic state in real time) — separate product, not a plugin feature
- **Prose execution mode** (the DE rewrites scenes) — violates the Firewall; explicitly out of scope
- **Line editing / copyediting** — different discipline, different tooling
- **Commercial viability guarantees** — the plugin diagnoses structure, not market outcomes

---

## Completed

### v1.0 — Public Release (2026-02-22)

v0.5 UX overhaul complete: query-driven passes, intake router, scene-level handoff, command alias model, overview dashboard. Plugin is navigable by newcomers.

- **Router Runtime / Design Split.** Split completed. `intake-router-runtime.md` handles execution; `intake-router-design.md` holds rationale. `/start` loads only the runtime file.

### v1.0.4

- **Subagent Pass Orchestration** (optional swarm mode). Each pass runs as an independent subagent with its own context window. The Findings Ledger serves as the inter-agent communication protocol. User-invoked at intake with "run in swarm mode." Default remains single-context. Protocol in `references/run-core.md` §Execution Mode. Design rationale in `docs/subagent-architecture-design.md`.

### v1.0.8

- **Compression Audit.** Expendable material identification, cut list generation, word-savings map, retained scaffolding diagnosis. Craft audit with level-setting brief.

### v1.0.9

- **Reception Risk Audit.** Cultural-context reception risk (17 flags across 5 channels: RR, EX, PF, CR, HW). Risk Map, Pattern Summary, Sensitivity Reader Handoff Memo artifacts. Two-pass procedure, 8 mode calibrations, 5 hard gates, Directional Check. Level-setting brief (Jauss, Iser, Fish, Hall, Booth, Genette, Phelan). Built via three-model synthesis (Opus 4.6, Codex 5.3, Gemini 2.5 Pro).
- **Voice Distinctiveness Comparison** (Pass 7). Six comparison dimensions for multi-POV manuscripts, two new flags (under-individuation, selective individuation).
- **Title/Framing Architecture** (Pass 3). Conditional evaluation for manuscripts with deliberate titling conceits, epigraph sequences, or section-header systems. Four tests (deepening, counterpoint, coherence, ornamental). Finding-driven trigger to Literary Craft audit.
- **Release tooling.** `release-registry.json` as single source of truth, `release-generate.mjs` for cross-repo propagation, `release-verify.mjs` for drift detection, `release.sh` orchestrating the full pipeline.
