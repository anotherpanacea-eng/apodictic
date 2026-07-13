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
version: 2.10.0
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

## Plugin Structure

This skill is the core of the APODICTIC plugin. Three companion workflows handle specialized functions:
- **Plot coaching** — Spine diagnosis (50 spines), selection coaching, fantasy & series architecture
- **Specialized audits** — Deep-dive audits, tag audits, and research modes (loaded on demand)
- **Revision coaching** — Post-diagnostic revision coaching: session planning, stuck-point coaching, momentum tracking, deadline management (loaded via `/coach`)

**Delegation principle:** Core runs the development edit workflow. Everything else delegates to companion workflows or reference files. Core does not carry audit catalogs, tag-audit internals, or genre deep-dives.

---

## The Firewall

<!-- Firewall definition has been extracted to `references/firewall.md` (single canonical source).
     Load `references/firewall.md` for the full no-content-invention firewall definition.
     The `nonfiction-argument-engine` skill references the same file. -->

*See `references/firewall.md` for the canonical Firewall definition. The no-content-invention rule applies in all modes — editorial, argument, coaching. Other surfaces (`revision-coach/SKILL.md §The Coaching Firewall`, `adversarial-stress-test.md §Firewall Compliance`, `run-full.md` §QA gate, `pass-11.md` §Forbidden) add only context-specific elaborations; the definition lives in `references/firewall.md` only.*

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

### 2. Pass Resolution
Load `references/pass-dependencies.md`, resolve concern to minimum pass set, add dependencies, then run selected passes in dependency order.

### 3. Synthesis
Load `references/run-synthesis.md`. Root cause analysis (max 5), triage (Must-Fix / Should-Fix / Could-Fix), adversarial self-check, adversarial reader stress test, editorial letter. After writing: mechanical section validation, then evidence spot-check (5 claims verified against manuscript).

### 4. Expansion Recommendation
Apply auto-escalation rules from `references/pass-dependencies.md` §2b. Recommend expansion to full pass set when issue density/complexity exceeds the scoped run.

### 5. Revision Round (when re-analyzing)
Load `references/state-lifecycle.md`. Delta scan, ripple check, resolution verification, new issue detection.

### 6. Submission Readiness (when submitting)
When the writer asks "is this ready to submit?", run the Submission Readiness Workflow: Core DE → Synthesis → Pass 11 → Compression Test → Unified Readiness Assessment. Entry point: `/ready` command or `full_draft + submit` route. Load `references/submission-readiness.md` for full specification. For deadline-constrained writers, route to Submission Triage instead (`references/submission-triage.md`).

### 7. Scene-Level Handoff (when requested)
When diagnosis is complete for a scoped scene and the writer wants execution help, follow `references/handoff-protocol.md` for mode switch, state persistence, and re-entry.

**Execution details:** Load `references/run-core.md` for intake, pass execution, and Findings Ledger protocol. Load `references/run-synthesis.md` after passes complete for audit integration, synthesis, and deliverables. Load `references/state-lifecycle.md` for revision rounds and state gardening. Use `references/pass-dependencies.md` for pass resolution. For full expansion: load `references/run-full.md`.

**Execution mode:** The system supports context-aware execution. **Single-agent** (default when ≥1M context tokens and manuscript fits): one subagent runs all passes sequentially in a single context, with the Findings Ledger persisted to disk after each pass. **Sequential** (default for standard-context or very large manuscripts): each pass runs as an independent subagent with the full manuscript. **Hybrid** (optional): Pass 0+1 produces a focus map; later passes run as independent subagents with targeted excerpts (~2–3x token cost). **Swarm** (optional): independent subagents with parallel execution (~5x token cost; architectural isolation for a final-round verification pass — reserve for submission prep, not everyday depth). Mode selection is automatic based on context window size and manuscript token load; the user can override at intake. See `references/run-core.md` §Execution Mode for protocol details; `references/hybrid-mode.md` for the focus map specification.

---

## Pass Architecture

Pass dependency and parallelization rules are canonical in `references/pass-dependencies.md`:

- Tier 1 (read passes) can run in parallel.
- Tier 2 (analysis passes) require resolved Tier 1 dependencies.
- Tier 3 synthesis runs after selected Tier 2 passes complete.
- Pass 11 runs only when submission readiness is in scope.

Never synthesize before all selected passes and their dependencies are complete.

---

## Output Policy (Summary)

- Maximum 5 root causes; 10 revision checklist items (Core DE), 15 (Full DE); 10 must-fix flags
- Every flag requires 2-4 specific scene/page references
- Quote budget: ≤25 words per excerpt, or paraphrase + pointer
- Every proposed fix must list what it risks harming
- All outputs are author-facing. Translate framework shorthand on first use. The author should never need to consult framework documentation.
- Confidence markers: HIGH / MEDIUM / LOW / UNCERTAIN — never present LOW or UNCERTAIN as definitive
- Severity honesty: do not soften Must-Fix to Should-Fix. Apply severity floor rules.

### Pass-Detail Artifact Headers

Every pass-detail output artifact must begin with a one-line blockquote header that makes the file legible without framework knowledge:

```
> **Macro block:** [block name from §3 of pass-dependencies.md] · **Writer question:** [the §3 User Question for this block] · **Legacy pass id:** Pass [N]
```

The three values are **read from `references/pass-dependencies.md §3` (Macro Block Definitions) — never authored.** §3 is the single source of truth for the 8 blocks, the pass→block map, and each block's User Question. `scripts/validate.sh pass-header` checks the header against §3 (see `references/run-core.md §What each pass subagent returns` and the canonical `references/example-pass-artifact-header.md`).

Mapping (**derived from §3 — reconcile here only by re-deriving from §3, do not hand-edit against it**):

| Pass | Macro Block | Writer Question |
|------|-------------|-----------------|
| 0 | Structure Map | Is the structure working? |
| 1 | Reader Dynamics | Does the pacing hold? |
| 2 | Structure Map | Is the structure working? |
| 3 | Reader Dynamics | Does the pacing hold? |
| 4 | Emotional Dynamics | Are the emotional beats earning their weight? |
| 5 | Character Architecture | Are my characters landing? |
| 6 | Scene Delivery | Are the scenes doing their jobs? |
| 7 | Character Architecture | Are my characters landing? |
| 8 | Reveal Economy | Is the information flow right? |
| 9 | Theme & Continuity | Does it cohere? |
| 10 | Theme & Continuity | Does it cohere? |
| 11 | Submission Readiness | Is this ready? |

### Results Guide Artifact

After synthesis, produce `[Project]_Results_Guide_[runlabel].md` — a map from writer questions to the relevant artifacts from the run. This is the first file after the editorial letter and helps the writer navigate their results without framework knowledge.

Include only blocks and artifacts from passes that actually ran. Format:

```markdown
# Results Guide — [Project Name]
_Run: [runlabel]_

## How to use this guide
Start with the **Editorial Letter** for the diagnosis and priority repairs.
Use this guide to find the detailed analysis behind each finding.

---

## Your results by question

### [Writer question — e.g., "Is the structure working?"]
- Editorial Letter § [Macro block name]
- Detail: `[pass artifact filename]`
- Detail: `[pass artifact filename]`

[... repeat for each macro block that ran ...]

## Specialized audits run
- [Audit Name]: `[artifact filename]`

## State files
- Diagnostic State: `Diagnostic_State.md`
- Findings Ledger: `[Project]_Findings_Ledger_[runlabel].md`

## What to do next
- `/coach` — plan revision sessions from this diagnosis
- `/audit [name]` — run a focused deep-dive on a specific concern
```

Omit the "Specialized audits run" section if no audits ran. Omit "Argument State" from state files unless the nonfiction engine was active.

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

*Canonical home for the Pass-10-Class artifact pattern. Other surfaces (`pass-dependencies.md §1 Tier 1 Pass 10 row`, `run-synthesis.md §Step 2 Pass-10-Class artifact integration`, `references/pass-10.md`) reference this section's definition and add only artifact-instance specifics (Timeline schema, Argument_State schema, etc.).*

A recognized class of project-level rolling artifacts the framework uses to track manuscript state across runs. Pass-10-class artifacts share these properties:

- **Project-level**, not run-folder-scoped (lives at the project root, persists across runs)
- **Structured**, machine-readable or near-machine-readable (schema specified per artifact)
- **Diffable** across runs (subsequent runs produce a diff section showing what changed)
- **Validator-paired** (each instance has a mechanical validator that surfaces drift, conflicts, or schema violations)
- **Synthesis-layer integrated** (the synthesis step consumes the artifact and may treat numeric drift as severity input)

This contrasts with run-folder-scoped pass artifacts (e.g., individual pass reports, audit findings files), which are run-specific and not designed for cross-run diff.

Recognized instances:
- `Diagnostic_State.md` — rolling diagnostic state at project root (already exists)
- `SYNTHESIS.md` — master revision plan at project root (already exists)
- `Argument_State.md` — argument-shaped nonfiction state at project root (already exists; see argument-state-schema)
- `Series_State.md` — cross-volume continuity at series root (already exists)
- `Timeline.md` — temporal architecture for fiction with Pass 10 (live; schema in `references/pass-10.md`; three mechanical validators in `scripts/validate.sh`: `timeline-diff`, `timeline-arithmetic`, `timeline-anchor-conflict`)
- `Plot_Spine.md` — spine-driven fiction state (future; intersects Plot Architecture skill)

When adding a new project-level rolling artifact, instantiate it against this class: define its schema, pair it with a validator, specify the synthesis-layer integration. `Timeline.md` (Phase 6 Wave 1) is the first live instance added under the named pattern; `Plot_Spine.md` is the next planned instance.

---

## Definition of a Scene

**Scene** = a continuous unit of time/space with a POV holder, a local goal, and a detectable turn (change in value, knowledge, or strategy).

If there is no turn, it's a **beat**. Beats get grouped until a scene exists.

### Units Terminology
- **Lines** = manuscript line numbers (for scene/passage references)
- **Words** = actual word count (for length and proportion analysis)
Never conflate these.

### Quantitative Verification (Required)
Before reporting any word counts or proportions:
1. Measure, don't estimate. Run `wc -w [manuscript]` to get total word count.
2. Measure parts separately. Extract each section and count individually.
3. Verify before analysis. All proportional analysis must use measured values.
4. State measurements explicitly.

---

## Delegation Rules

### Pre-Writing
Writer has idea but no manuscript → Start the pre-writing pathway.

### Plot Structure
Spine diagnosis (which of the 50 spines / 12 families governs the whole-work shape), selection coaching, structural triage on stuck drafts, hybrid design, fantasy/series architecture → Start plot coaching (`plot-architecture` skill).

This is distinct from **Pass 2: Structural Mapping** (Tier 2 pass within a development edit run), which maps on-page act/movement boundaries, beat presence, missing-beat lists, and structural causality. Pass 2 answers "is the structure I have on the page working"; Plot Architecture answers "which spine is this and does that paradigm hold." See `plot-architecture/SKILL.md §Plot Architecture vs. Pass 2 (Structural Mapping) — Boundary` for cross-reference and sequencing.

### Nonfiction Argument Engine
When intake resolves `constraint=nonfiction` AND the declared form is in the persuasive-argument family (op-ed, policy brief, testimony, academic argument, open letter, white paper, advocacy argument, legal brief, regulatory comment, expert affidavit — per `references/intake-router-runtime.md §6 Table A`), delegate to the **`nonfiction-argument-engine` skill**. Pass the full run-shape (form, audience burden, stakes, high-stakes flag); receive the standard artifact set (editorial letter + Findings Ledger + `Argument_State.md` + marked-up manuscript). The fiction path and the argument path share the core editorial spine; this delegation makes the argument route explicit rather than implicit.

Do NOT remove or bypass the existing specialized-audits dispatch (§4a/§4b routing) — the nonfiction-argument-engine itself calls specialized-audits for its argument-cluster audits (Dialectical Clarity, Red Team, Evidence, Field Recon, Citation Verifier). This delegation is additive, not a replacement.

### Specialized Audits
Any deep-dive audit, tag audit, or research mode → Run the audit. The specialized-audits workflow maintains its own routing table and trigger logic.

### Scene-Level Handoff
When the writer requests prose-level execution help for a diagnosed scene:
- Load `references/handoff-protocol.md`
- Offer handoff using the required confirmation template
- Write context into `Diagnostic_State.md` in the active project output context and set mode to `execution`
- Suspend core-editor constraints for execution mode
- Re-enter diagnostic mode only via explicit phrase trigger or `/start` resume check

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

## QA Guardrails

1. Verify word counts before proportional claims.
2. Apply severity floor rules (see `references/output-policy.md`).
3. Log uncertainty explicitly — never force false clarity.
4. Run adversarial self-check before writing editorial letter.
5. Check every flag against stated author intent before finalizing.
6. Run mechanical validation (plugin-bundled `scripts/validate.sh`, or inline fallback) at each checkpoint (see `references/run-core.md` §Mechanical Validation Protocol).
7. Run evidence spot-check after synthesis — verify 5 claims against manuscript before delivering (see `references/run-synthesis.md` §Evidence Spot-Check).

---

*This skill provides developmental editing methodology. It diagnoses structure; the author invents content. The system surfaces patterns, asks questions, and proposes intervention classes. Creative authority remains entirely with the author.*
