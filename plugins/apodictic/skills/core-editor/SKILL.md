---
name: core-editor
description: >
  AI developmental editing framework for fiction, narrative nonfiction, and
  argument-shaped nonfiction; owns the Nonfiction Argument Engine.
  Use when the user asks to "run a development edit," "analyze my manuscript,"
  "diagnose structural issues," "start a new project," "generate a contract,"
  "run the passes," "do a revision round," or any request involving manuscript
  analysis, structural diagnosis, or editorial feedback. Also triggers on
  "APODICTIC," "APDE," or "development editor."
version: 2.15.0
---

# APODICTIC Development Editor — Core Orchestrator

---

## Canonical Source

`SKILL.md` is the thin orchestrator. It defines workflow, routing, and policy.
Execution details live in reference files loaded on demand.
Dedicated reference files (genre modules, specialized audits, `references/pass-11.md`) win for module-specific rules.

**Branding note:** Public-facing name is `APODICTIC Development Editor`. Tagline: *Developmental editing that listens before diagnosing.* The plugin author's identity must never be confused with the manuscript author's identity.

**Model note:** This framework is designed for strong frontier models with reliable instruction-following and ample context. On weaker models, expect degraded severity honesty, weaker thematic interpretation, and lower fix quality.

---

## Author adjudication entry point

For `/adjudicate`, load `references/craft/approval-workflow.md` and follow that
workflow directly. It presents an existing reconstruction graph and records
explicit author decisions. Do not start Core DE passes or generic audit output
routing. Semantic exclusion screening remains unavailable; never override a
blocked approval or represent this partial workflow as drafting acceptance.

## Reconstruction drafting entry point

For `/reconstruct`, load `references/craft/reconstruction-drafting.md`. Export
only the eligible approved packet and invoke the supported isolated drafter.
Follow the existing author adjudication workflow when readiness is blocked.
Draft and receipt production requires subsequent semantic review; unavailable
semantic screening and comparison must remain explicit.

## The Firewall

Firewall: `references/firewall.md` (canonical; applies in all modes).

---

## Pass Resolution

Pass execution is concern-driven, not hardwired to a single fixed sequence.

- Resolve the user's concern to a minimum pass set using `references/pass-dependencies.md`.
- Pull required upstream dependencies automatically from the same file.
- Execute by dependency tier (parallel where permitted), then synthesize.
- If concern is unspecified or ambiguous, default to **General diagnostic floor**: Passes 0, 1, 2, 5, 8.
- If findings indicate interconnected systemic issues, recommend expansion to the full pass set per auto-escalation rules.

---

## Workflow Contract

### 1. Intake (always runs)
Draft-then-validate contract from text analysis. Hypothesis-driven questions. Output: `[Project]_Contract_[runlabel].md`.
If router output is available (`artifact`, `goal`, `concern`, `constraints`, `operator`), treat those fields as pre-filled and skip redundant intake questions.

### 2. Synthesis
Load `references/run-synthesis.md`. Root cause analysis (max 5), triage (Must-Fix / Should-Fix / Could-Fix), adversarial self-check, adversarial reader stress test, editorial letter. After writing: mechanical section validation, then evidence spot-check (5 claims verified against manuscript).

### 3. Expansion Recommendation
Apply auto-escalation rules from `references/pass-dependencies.md` §2b. Recommend expansion to full pass set when issue density/complexity exceeds the scoped run.

### 4. Revision Round (when re-analyzing)
Load `references/state-lifecycle.md`. Delta scan, ripple check, resolution verification, new issue detection.

### 5. Submission Readiness (when submitting)
When the writer asks "is this ready to submit?", run the Submission Readiness Workflow: Core DE → Synthesis → Pass 11 → Compression Test → Unified Readiness Assessment. Entry point: `/ready` command or `full_draft + submit` route. Load `references/submission-readiness.md` for full specification. For deadline-constrained writers, route to Submission Triage instead (`references/submission-triage.md`).

**Execution details:** Load `references/run-core.md` for intake, pass execution, and Findings Ledger protocol. Load `references/run-synthesis.md` after passes complete for audit integration, synthesis, and deliverables. Load `references/state-lifecycle.md` for revision rounds and state gardening. Use `references/pass-dependencies.md` for pass resolution. For full expansion: load `references/run-full.md`.

**Execution mode** (single-agent, sequential, hybrid, swarm) is selected automatically from context window and manuscript size; the user can override at intake. See `references/run-core.md` §Execution Mode.

---

## Output Policy

Each pass artifact opens with the §3-sourced header (`references/run-core.md` §What each pass subagent returns; checked by `pass-header`).

### Results Guide Artifact

After synthesis, produce the Results Guide per `references/output-structure.md` §Results Guide.

**Full output policy (tone, evidence burden, caps, anti-sycophancy, severity floors, pass-level output protocol):** Load `references/output-policy.md`.

---

## Project Integration

When operating within a manuscript project, the **active project output context** is the project root folder that holds the manuscript's APODICTIC artifacts and rolling state. See `references/output-structure.md` §Folder Architecture for the canonical folder structure.

**Key rules:**
- Rolling state (`Diagnostic_State.md`, `SYNTHESIS.md`, `Session_Plan_{NN}.md`, `README.md`) lives at the **project root**
- Run artifacts (pass outputs, contracts, findings ledgers, audit reports, results guides) live inside **`runs/YYYY-MM-DD_{model}_{type}/`**
- The `Outputs/` sibling convention is deprecated. For existing projects with an `Outputs/` folder, treat it as the project root and create `runs/` inside it.
- Never write project state inside the plugin repo, the installed plugin cache, or any other APODICTIC framework directory.

When operating within a project:

1. **CHECK** for existing contract artifact before running intake
2. **REFERENCE** character portraits during Pass 5 for consistency
3. **REFERENCE** story guides during Pass 9 for controlling idea alignment
4. **CREATE** the run folder (`runs/YYYY-MM-DD_{model}_{type}/`) at the start of each run
5. **OUTPUT** all run artifacts (pass reports, contract, findings ledger, results guide) into the run folder
6. **INITIALIZE** `Diagnostic_State.md` at the project root from `references/diagnostic-state-template.md` if it does not exist
7. **SET** the Mode section's `**Current:**` field to `diagnostic` unless an active handoff is explicitly in effect
8. **APPEND** handoff entries to `Handoff History` (never overwrite prior cycles)
9. **UPDATE** `Diagnostic_State.md` at the project root with cumulative findings across sessions, including author decisions and control questions when synthesis produces them
10. **UPDATE** `SYNTHESIS.md` at the project root — if this is the first run, copy synthesis there; if prior runs exist, incorporate new findings with a methodology note listing contributing runs
11. **APPEND** a row to `README.md` run archive table

When no project context exists, proceed with intake from scratch.

### Pass-10-Class Rolling Structured Artifacts

A project-level rolling artifact that is structured, diffed across runs, validator-paired, and consumed by synthesis. Instances: `Diagnostic_State.md`, `SYNTHESIS.md`, `Argument_State.md`, `Series_State.md`, `Timeline.md` (schema and validators in `references/pass-10.md`). Pattern and authoring notes: `docs/pass-10-class-artifacts.md`.

---

## Definition of a Scene

**Scene** = a continuous unit of time/space with a POV holder, a local goal, and a detectable turn (change in value, knowledge, or strategy).

If there is no turn, it's a **beat**. Beats get grouped until a scene exists.

### Units Terminology
- **Lines** = manuscript line numbers (for scene/passage references)
- **Words** = actual word count (for length and proportion analysis)
Never conflate these.

---

## Delegation Rules

### Pre-Writing
Writer has idea but no manuscript → Start the pre-writing pathway.

### Plot Structure
Spine diagnosis (which of the 50 spines / 12 families governs the whole-work shape), selection coaching, structural triage on stuck drafts, hybrid design, fantasy/series architecture → Start plot coaching (`plot-architecture` skill).

This is distinct from **Pass 2: Structural Mapping** (Tier 2 pass within a development edit run), which maps on-page act/movement boundaries, beat presence, missing-beat lists, and structural causality. Pass 2 answers "is the structure I have on the page working"; Plot Architecture answers "which spine is this and does that paradigm hold." See `plot-architecture/SKILL.md §Plot Architecture vs. Pass 2 (Structural Mapping) — Boundary` for cross-reference and sequencing.

### Nonfiction Argument Engine
When intake resolves `constraint=nonfiction` AND the declared form is in the persuasive-argument family (op-ed, policy brief, testimony, academic argument, open letter, white paper, advocacy argument, legal brief, regulatory comment, expert affidavit — per `references/intake-router-runtime.md §6 Table A`), delegate to the **`nonfiction-argument-engine` skill**. Pass the full run-shape (form, audience burden, stakes, high-stakes flag); receive the standard artifact set (editorial letter + Findings Ledger + `Argument_State.md` + marked-up manuscript). The fiction path and the argument path share the core editorial spine; this delegation makes the argument route explicit rather than implicit.

### Specialized Audits
Any deep-dive audit, tag audit, or research mode → Run the audit. The specialized-audits workflow maintains its own routing table and trigger logic.

### Scene-Level Handoff
When the writer requests prose-level execution help for a diagnosed scene, follow `references/handoff-protocol.md` (confirmation template, mode switch, state persistence, re-entry).

### Pass 11: Critical Quality & Market Viability
Author states publication/submission goal, requests honest assessment, or mentions query materials → Load `references/pass-11.md`.

### Character Architecture (Deep)
Psychology engine, arc types, agency quotient, genre tuning packs → Load `references/character-architecture.md`.

---

## Genre Module Routing

During intake, identify the manuscript's genre and load the corresponding module. Genre modules modify pass behavior (recalibrate thresholds, add tracking, adjust false positive warnings).

| Genre | Reference File | Key Modification |
|-------|---------------|------------------|
| Literary Fiction | `references/genre-literary.md` | Pass 9 priority; Literary Mode for genre-bending; Register Uncertainty diagnostic |
| Horror (Psychological) | `references/genre-horror.md` | Certainty axis priority; dread escalation tracking; reality anchoring |
| Science Fiction / Fantasy | `references/genre-sff.md` | Rule Ledger (Pass 10); Sanderson's Laws; integration tests |
| Romance | `references/genre-romance.md` | Relationship engine; trust-rupture-repair cycle; 15 named flags |
| Mystery | `references/genre-mystery.md` | Information pressure; clue economy; fair play tests |
| Thriller | `references/genre-thriller.md` | Threat escalation; clock pressure; protagonist competence |

**If manuscript includes erotic/intimate content:** Activate the **Erotic Content tag** via specialized-audits. Adds heat level, consent calculus, escalation vs. repetition audit, erotic-specific flags.

**If Literary Fiction is primary with other genre modules active:** Activate **Literary Mode** (see `references/genre-literary.md`). Genre conventions become available tools, not requirements.

---

## Reference Files (Load on Demand)

Compact routing map below. Full index — templates, deprecated files, and per-file descriptions — in `references/reference-index.md`.

**Execution:** `run-core.md` (every run: intake, pass execution, ledger protocol) · `run-synthesis.md` (after passes: audit integration, synthesis, deliverables, evidence spot-check) · `pass-dependencies.md` (concern → scoped pass set + order) · `run-full.md` (advanced passes 3/4/6/7/9/10) · `output-policy.md` (before writing output) · `output-structure.md` (folders, naming, lifecycle, sidecar — at write time) · `adversarial-stress-test.md` (letter §7) · `state-lifecycle.md` (revision rounds, state gardening) · situational: `partial-manuscript.md`, `editor-scaffolding.md` (`operator:editor`), `diagnostic-vocabulary.md` (`operator:facilitator`), `fragment-synthesis.md`, `handoff-protocol.md`, `character-architecture.md`, `pass-11.md`.

**Genre modules** (load by detected genre, primary or secondary): `genre-literary.md` · `genre-horror.md` · `genre-sff.md` · `genre-romance.md` · `genre-mystery.md` · `genre-thriller.md`.

**Templates, other references, and deprecated files:** see `references/reference-index.md`.

---

*This skill provides developmental editing methodology. It diagnoses structure; the author invents content. The system surfaces patterns, asks questions, and proposes intervention classes. Creative authority remains entirely with the author.*
