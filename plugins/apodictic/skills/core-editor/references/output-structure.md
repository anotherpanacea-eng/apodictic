# Output Structure & Filesystem Conventions

*Reference file for the APODICTIC Development Editor. Loaded on demand at write/persist time — not during diagnostic reasoning. Holds the folder architecture, run-folder and output naming, the model-tag table, and lifecycle conventions extracted from `output-policy.md` so the always-loaded judgment file carries only editorial rules.*

---

## Folder Architecture (v0.5.0)

All APODICTIC work for a manuscript lives under a single **project root**. The `Outputs/` sibling convention from earlier versions is deprecated.

### Project Root

```
{project-root}/
├── Diagnostic_State.md          # Rolling state (updated across runs + sessions)
├── Diagnostic_State.meta.json   # Machine-readable sidecar
├── SYNTHESIS.md                 # Master revision plan (consolidated from all runs)
├── Session_Plan_{NN}.md         # Coaching session plans, numbered sequentially
├── README.md                    # Project manifest (auto-generated, see below)
└── runs/                        # Immutable run archive
    └── {run-folders}
```

`{project-root}` is the active project output context. For new projects, this is created by `/new-project`. For existing projects, it is the folder that already contains the manuscript's APODICTIC output. The project folder name should use the manuscript's working title in Title_Case with underscores (e.g., `My_Novel`, `Policy_Brief_Draft`).

**Migration from `Outputs/`:** If an existing project has an `Outputs/` folder with APODICTIC artifacts, treat that folder as the project root. Create `runs/` inside it and continue.

Never write project artifacts or rolling state files to the plugin repo, installed plugin cache, or any other APODICTIC framework directory.

### Project Registry (workspace-level)

Project roots are made **addressable** — selectable by name rather than only by being the ambient folder — through a workspace-level registry (Project Addressability, Increment 2; `docs/project-addressability.md`).

```
{workspace-root}/
├── .apodictic/
│   └── registry.json           # apodictic.project_registry.v1 (one entry per project)
├── My_Novel/                   # a project root (sidecar canonical)
│   ├── Diagnostic_State.meta.json
│   └── ...
└── Policy_Brief_Draft/         # another project root
    └── ...
```

- **Location.** `.apodictic/registry.json` in the **workspace root** — the nearest ancestor of the cwd that contains a `.apodictic/` directory (discovered by walking up, like `.git`). Not in the plugin repo/cache; `~` is not used (sandbox-unsafe).
- **Canonical vs. cache.** Each project's `Diagnostic_State.meta.json` is canonical; the registry is a *recomputable cache* of `{id, title, root, volume, denormalized mode/next_action, last_touched, series_root}`. On drift, the sidecar wins; a lost registry is rebuilt by scanning the workspace for sidecars and `*_Structural_Plan_*.md` artifacts.
- **Writers.** `/new-project` appends an entry; `/projects` lists/rebuilds/tidies; `/start <project>` binds a session to one entry's root. Pre-writing projects carry a **minimal sidecar** (`mode: diagnostic`, `next_action: pre_writing`) so they register before any Core DE run.
- **Validator.** `scripts/validate.sh registry-check <registry.json | workspace_dir>` (R1 schema, R2 root/sidecar resolution, R3 drift, R4 duplicate id).

### Rolling State Files

These files live at the project root and are updated in place:

| File | Created By | Updated By |
|------|-----------|------------|
| `Diagnostic_State.md` | `/new-project` or first DE run | Every subsequent run, coaching session, and author revision |
| `Diagnostic_State.meta.json` | `/new-project` or first DE run | Every time `Diagnostic_State.md` is updated |
| `SYNTHESIS.md` | First DE synthesis | Each subsequent run's synthesis; carries a methodology note listing contributing runs |
| `Session_Plan_{NN}.md` | `/coach` | Archived to coaching run folder on session completion; new file for each session |
| `README.md` | `/new-project` or first run | Each new run (manifest table appended) |

What does NOT live at project root: individual pass artifacts, contracts, findings ledgers, audit outputs, results guides. Those belong in `runs/`.

### Series Structure

For series projects, each volume gets its own project folder. A parent series folder holds the shared `Series_State.md`:

```
{series-root}/
├── Series_State.md
├── {Volume_One}/
│   ├── Diagnostic_State.md
│   ├── SYNTHESIS.md
│   ├── README.md
│   └── runs/
├── {Volume_Two}/
│   └── ...
```

`Series_State.md` lives at the series root, not duplicated inside each volume.

### Run Folder Naming

```
runs/YYYY-MM-DD_{model-tag}_{run-type}/
```

**Date:** ISO 8601, the date the run started.

**Model tag:** Required. From the model tag table below.

**Run type:** Required. One of:

| Type | When Used |
|------|-----------|
| `full-de` | Full development edit (all 11 passes + contract audits) |
| `core-de` | Core development edit (6 passes) |
| `partial-de` | Partial manuscript diagnostic |
| `fragment-de` | Fragment synthesis |
| `audit` | Standalone audit(s) without a DE run |
| `consolidated` | Cross-model or cross-run consolidation/comparison work |
| `coaching` | Revision coaching session outputs |

**Collision rule:** If a second run of the same date + model + type occurs, append `-2` (then `-3`, etc.):
```
runs/2026-04-04_opus46_audit/
runs/2026-04-04_opus46_audit-2/
```

**Multi-model runs:** For consolidation work, use the consolidating model's tag. For swarm-mode, use the synthesis model's tag. Every pass file in a run **shares the run's single `runlabel`** (see the runlabel grammar below) — `artifact-names` validates every artifact against exactly one runlabel per run, so per-file model tags **do not exist in the filenames**. The run-folder / runlabel tag is the synthesis-or-consolidating model's; the record of which model each individual **dispatched** step was issued to lives in the `dispatch_log` sidecar object (the per-dispatch SSoT — see §Machine-Readable Sidecar), which the run-level runlabel structurally cannot carry.

### Project Manifest (README.md)

Auto-generated or updated after each run:

```markdown
# {Project Title} — APODICTIC Development Editor Files

## Start Here

| File | Purpose |
|------|---------|
| **SYNTHESIS.md** | Master revision plan. Open this to revise. |
| **Diagnostic_State.md** | Rolling state: findings, progress, decisions, change log. |
| **Session_Plan_{NN}.md** | Current coaching session plan. |

## Run Archive

| Folder | Date | Model | Type | Passes/Audits | Notes |
|--------|------|-------|------|---------------|-------|
| `runs/YYYY-MM-DD_model_type/` | YYYY-MM-DD | Model Name | full-de | 11 passes + N audits | ... |
```

The run archive table is append-only. Each new run adds a row.

---

## Output Naming Convention (v0.5.0)

Use these filenames within run folders:

**Core DE:**
- `[Project]_Contract_[runlabel].md`
- `[Project]_Manuscript_Snapshot_[runlabel].md` (frozen LF-normalized copy, written at intake; the Annotated-Manuscript deliverable's immutable reference — see `run-core.md` §Intake Protocol → Step 1)
- `[Project]_Pass0_Reverse_Outline_[runlabel].md`
- `[Project]_Pass1_Reader_Experience_[runlabel].md`
- `[Project]_Pass2_Structural_Mapping_[runlabel].md`
- `[Project]_Pass5_Character_Audit_[runlabel].md`
- `[Project]_Pass8_Reveal_Economy_[runlabel].md`
- `[Project]_Findings_Ledger_[runlabel].md`
- `[Project]_Synthesis_Read_Manifest_[runlabel].md` — artifact-read manifest written **before** the editorial letter (by the parent orchestrator at synthesis dispatch in multi-agent modes; by the agent immediately before letter-writing in single-agent mode). Row grammar and denominator: `run-synthesis.md` §Processing Protocol step 9b; reconciled by `validate.sh synthesis-coverage <run_folder>`
- `[Project]_Core_DE_Synthesis_[runlabel].md`
- `[Project]_Annotation_Manifest_[runlabel].md` — Annotated-Manuscript deliverable, **offered at run-end** (only when a `*_DE_Synthesis_*` letter was written; see `run-synthesis.md §Annotated Manuscript + Crosslinked Letter`)
- `[Project]_Annotated_Manuscript_[runlabel].md` — the snapshot with CriticMarkup margin comments (one per finding)
- `[Project]_Crosslinked_Letter_[runlabel].md` — the editorial letter back-linked to the margin comments
- `[Project]_Contract_Map_[runlabel].md` — Reader-Contract Reverse Outline plumbing: one `apodictic.contract_map.v1` block (ids-only clause→scene localization), gated before the outline projector consumes it (**offered at run-end** with the outline; see `run-synthesis.md §Reader-Contract Reverse Outline`)
- `[Project]_Reader_Contract_Outline_[runlabel].md` — the book scene by scene, mapped against its reader contract; a byte-deterministic projection of Pass 0 + Contract + Ledger + the gated Contract Map (see `references/reader-contract-outline.md`)

**Full DE (additional):**
- `[Project]_Pass3_Rhythm_Modulation_[runlabel].md`
- `[Project]_Pass4_Emotional_Value_Tracking_[runlabel].md`
- `[Project]_Pass6_Scene_Function_[runlabel].md`
- `[Project]_Pass7_POV_Voice_[runlabel].md`
- `[Project]_Pass9_Thematic_Coherence_[runlabel].md`
- `[Project]_Pass10_Entity_Tracking_[runlabel].md`
- `[Project]_Pass11_Critical_Quality_[runlabel].md`
- `[Project]_Diagnostic_Dashboard_[runlabel].md`
- `[Project]_Full_DE_Synthesis_[runlabel].md`

`runlabel` format: `YYYY-MM-DD_[model-tag]`

The model tag is **required**, not optional. It identifies which model generated the analysis.

| Model family | Tag |
|-------------|-----|
| Codex 5.4 | `codex54` |
| ChatGPT o3 | `o3` |
| Gemini 3.1 | `gemini31` |
| Claude Opus 4.6 (historical compatibility) | `opus46` |
| Claude Sonnet 4.6 (historical compatibility) | `sonnet46` |
| Claude Haiku 4.5 (historical compatibility) | `haiku45` |

**Examples:** `2026-03-18_codex54`, `2026-03-18_o3`

**Derivation:** Read the model identifier at runtime and derive the tag (for example, `codex-5-4` → `codex54`, `claude-opus-4-6` → `opus46`). If the model identifier is unavailable, use `unknown`.

**Multi-model runs:** All output files in a run share the run's **single `runlabel`** (one tag per run — the runlabel grammar admits exactly one). That tag is the **synthesis/consolidating model's**; in swarm mode where different passes run on different models, the per-pass model identities are **not** recoverable from the filenames (which all carry the one runlabel). Which model each **dispatched** step was actually issued to is recorded in the `dispatch_log` sidecar object — the per-dispatch SSoT (see §Machine-Readable Sidecar). Note `dispatch_log` records the dispatch **instruction as issued** (parent-requested, not platform-verified).

**Partial Manuscript Diagnostic (when `artifact=partial`):**
- `[Project]_Partial_Diagnostic_[runlabel].md` (replaces `Core_DE_Synthesis`)
- All pass artifacts use standard naming but follow partial-manuscript modifications (see `references/partial-manuscript.md`)

**Fragment Synthesis (when `artifact=fragments`, goal=`draft`):**
- `[Project]_Fragment_Map_[runlabel].md`
- `[Project]_Contract_[runlabel].md` (marked as provisional)
- `[Project]_Recommended_Spine_[runlabel].md`

**Diagnostic Vocabulary (when `operator:facilitator`):**
- `[Project]_Vocabulary_Guide_[runlabel].md` — facilitator teaching aid (glossary + discussion prompts), produced alongside the editorial letter (see `references/diagnostic-vocabulary.md`)

**Nonfiction Argument Engine (when argument-shaped):**
- `Argument_State.md` — shared argument artifact at the project root (§§1–10; see `docs/argument-state-schema.md`). The Dialectical Clarity audit populates it from a draft; the **Nonfiction Pre-Draft Pathway** seeds §1/§2/§3/§4 (+ §6 Objection 1) from `apodictic.argument_spine.v1` / `support_plan.v1` / `warrant_plan.v1` blocks *before* a draft exists (see `pre-writing-pathway/references/nonfiction-pre-draft.md`). Re-runs archive the prior state as `Argument_State_v[N].md`.
- `[Project]_Scene_Ethics_Plan_[runlabel].md` — Nonfiction Pre-Draft scene-ethics plan (Increment 4): the writer's pre-draft ethical plan for each identifiable real person depicted (`apodictic.scene_ethics.v1` — consent, handling, fairness), distinct from and cross-referencing the Legal Risk Register. See `pre-writing-pathway/references/nonfiction-pre-draft.md`.

**Legal Risk Register (when memoir / autofiction / nonfiction portrays identifiable real people):**
- `[Project]_Legal_Risk_Register_[runlabel].md` — flags legal-exposure areas (defamation / privacy / rights-clearance) with a legal-escalation severity and escalation triggers; not legal advice (see `references/legal-risk-register.md`)

**Series Continuity (when active):**
- `[Project]_Series_Continuity_Audit_[runlabel].md`

**Revision Coach (when active):**
- `[Project]_Session_Plan_[runlabel].md`
- `[Project]_Revision_Calendar_[runlabel].md` (deadline mode only)
- `[Project]_Retcon_Plan_[runlabel].md` (Retcon Planning mode — ranked Door-B candidate readings + setup-debt ledger + commitment budget; see `revision-coach/references/retcon-planning.md`)

**Rolling state files** (live at project root, not inside run folders):
- `Diagnostic_State.md` — per-volume diagnostic state at the project root. If missing, initialize from `references/diagnostic-state-template.md`.
- `Diagnostic_State.meta.json` — machine-readable sidecar at the project root. If missing, initialize from `references/diagnostic-state-meta-template.json`.
- `SYNTHESIS.md` — master revision plan at the project root. Created from the first run's synthesis; updated by subsequent runs with a methodology note listing contributing runs.
- `Series_State.md` — cross-volume series state at the series root (not inside each volume's project root). If missing, initialize from `references/series-state-template.md`. Persists across volumes; updated after each volume is analyzed.
- `[Project]_State_Card_[runlabel].md` — Retcon Planning State Card (F2), a rolling structured artifact (`apodictic.state_card.v1`, one block per round) at the project root. Diff'd across revision rounds by `validate.sh state-card-diff <prior> <current>` (Pass-10-class rolling-structured-artifact pattern). See `revision-coach/references/retcon-planning.md`.

### Results Guide

Per-run artifact, not a rolling file. Lives inside its run folder alongside the pass artifacts it references. See §Results Guide Artifact in SKILL.md for format.

### Lifecycle Summary

| Workflow | Creates Run Folder | Updates Rolling State |
|----------|-------------------|----------------------|
| `/new-project` | No (initializes project root) | Creates `Diagnostic_State.md`, `README.md` |
| `/start` (full edit) | `runs/YYYY-MM-DD_{model}_{type}/` | Updates `Diagnostic_State.md`, `SYNTHESIS.md`, `README.md` |
| `/audit` | `runs/YYYY-MM-DD_{model}_audit/` | Updates `Diagnostic_State.md`, `SYNTHESIS.md` (if findings alter plan), `README.md` |
| `/coach` | `runs/YYYY-MM-DD_{model}_coaching/` (on session completion) | Updates `Diagnostic_State.md` coaching log, `README.md` |
| Consolidation | `runs/YYYY-MM-DD_{model}_consolidated/` | Updates `SYNTHESIS.md` (typically the most significant update), `Diagnostic_State.md`, `README.md` |


---

## Rolling State Updates & Machine-Readable Sidecar (Post-Synthesis)

*Extracted from `run-synthesis.md` §Core DE Deliverables. Performed at the write/persist step after the editorial letter is written.*

### Run Folder and Rolling State

All run artifacts (editorial letter, pass reports, contract, findings ledger, audit invocation log, results guide) are written to the **run folder** (`runs/YYYY-MM-DD_{model}_{type}/`) inside the project root. See `references/output-structure.md` §Folder Architecture.

After writing the editorial letter to the run folder, update the **rolling state at the project root:**

1. **Update `Diagnostic_State.md`** with:
   - Findings from this session
   - Keep / Cut / Unsure decisions
   - Control Questions
   - Change log

2. **Update `SYNTHESIS.md`** at the project root:
   - If this is the first run: copy the synthesis to the project root as `SYNTHESIS.md`
   - If prior runs exist: update `SYNTHESIS.md` to incorporate new findings, with a methodology note listing contributing runs (e.g., "Consolidated from runs: 2026-03-15_opus46_full-de, 2026-04-04_opus46_core-de")

3. **Append a row** to the `README.md` run archive table.

`Diagnostic_State.md` lives at the project root, not inside run folders. If it does not exist, create it from `references/diagnostic-state-template.md` first. Never write rolling state to the plugin repo or installed plugin cache.

### Machine-Readable Sidecar (Required)

Alongside `Diagnostic_State.md`, maintain a sidecar file `Diagnostic_State.meta.json` in the same directory. This file is machine-readable state for fast resume routing, revision coaching, and state gardening. The author never reads it; the system reads it instead of parsing the markdown when it needs structured data.

**When to write:** Initialize from `references/diagnostic-state-meta-template.json` when creating `Diagnostic_State.md`. Update the sidecar every time `Diagnostic_State.md` is updated.

**What to update:**
- `mode` and `active_scene_scope` — on every mode transition (diagnostic ↔ execution)
- `last_session` — after each session (date, focus, tier, execution_mode, passes_completed, runlabel)
- `root_causes` — after synthesis (list of root cause names, max 5)
- `triage_summary` — after synthesis (counts of must-fix, should-fix, could-fix). Required whenever `findings[]` is populated; its counts must equal the `findings[]` severity tally (`validate.sh structured-findings`).
- `findings` — after Triage/synthesis, mirror the synthesis-bound (Must-Fix/Should-Fix) ledger findings here as `apodictic.finding.v1` objects (the same locks recorded in the Findings Ledger; see `findings-ledger-format.md`). Leave `[]` only when there are no such findings.
- `audit_triggers` — after audit consolidation, mirror the ledger's `apodictic.audit_trigger.v1` records here. `[]` when none.
- `readiness` — after a readiness pass (Pass 11 / submission readiness), record `apodictic.readiness.v1` verdicts here. `[]` when not assessed.
- `control_questions` — after synthesis and after each revision round (open/answered/deferred counts)
- `revision_progress` — after each revision round (steps_complete, current_step)
- `session_count` and `handoff_count` — increment on each new session or handoff
- `state_lines` — line count of `Diagnostic_State.md` (used by state gardening to trigger archival)
- `contract_hash` — SHA-256 of the contract file, set at intake, checked at pre-pass re-grounding (see `run-core.md` §Mechanical Validation)
- `synthesis_coverage` — at the Synthesis Coverage Manifest step (`run-synthesis.md` §Processing Protocol step 9b), on every run that writes a full editorial letter: the sidecar projection of the `[Project]_Synthesis_Read_Manifest_[runlabel].md` (provenance `dispatch-derived` in sequential/hybrid/swarm, `declared` in single-agent; `coverage` must equal the letter's `<!-- coverage: ok|degraded -->` marker; the `artifacts_*` tallies and `spans_outside_active_context` must equal the manifest rows; `verification_excerpt_count` multi-agent only, `estimated_context_utilization` single-agent only). Audited by `validate.sh synthesis-coverage <run_folder>`; leave the template stub untouched on runs without a full letter. **Post-re-grounding (step 9c, `docs/synthesis-regrounding.md` M2):** artifacts/spans re-read by the Pre-Letter Re-Grounding step flip their manifest row `status` to `verbatim`/`in-context` with a `regrounded: true` annotation, so this sidecar projection improves to match — disclosure gets *better* because contact with the text actually happened. Re-grounding is additive: it never lets a `degraded` coverage read `ok` (M1's V5 masking check still fires) and the object's fields are otherwise unchanged
- `dispatch_log` — **optional** array (Model-Capacity Exploitation M1, `docs/model-capacity-dispatch-log.md`): one entry per delegated-agent dispatch the parent orchestrator issued during the run (Execution Protocol steps 7 and 10), recording **which model each dispatched step was issued to** — the join key between model identity and every outcome signal already on disk. Each entry: `{ seq, step, model_tag, execution_mode, max_turns, provenance }`. `step` uses the v1 grammar `pass<N>` / `pass0+1` (the combined triage subagent) / `synthesis` / `all-passes` (single-agent's one subagent); `model_tag` is a tag from the model-tag table above **or the literal `unknown`** (the documented derivation fallback — a sanctioned value); `execution_mode` is the mode at dispatch; `max_turns` is the host-dependent turn budget (or `null`). **Provenance honesty (binding on every consumer):** `provenance: dispatch-derived` attests the dispatch **instruction** — the model parameter the parent requested — it is **parent-requested, not platform-verified** (no host API attests which model actually served the subagent, so this is deliberately weaker than `synthesis_coverage`'s manifest-reconciled coverage); `provenance: declared` = a step that ran inline with no dispatch event (no-shell hosts, or a genuinely inline step) — legitimate under any `execution_mode`, since provenance tracks the host's **per-entry dispatch capability**, not the run's mode. The log records the model **tag**, never a "tier" label. **Grandfather:** the field's **absence** is the pre-adoption marker (no obligation); a present-but-**empty** `[]` is a post-adoption recording failure. Audited by `validate.sh dispatch-record <run_folder>` (R1 presence advisory-first; R2 pass-artifact + synthesis-letter coverage; R3 tag vocabulary; R4 shape; R5 escalation cross-check) and surfaced cross-run by `validate.sh dispatch-record --report <project_dir>`. `dispatch_log` is the **per-dispatch SSoT** the single-runlabel filename grammar structurally cannot carry; the editorial letter never discusses model allocation (provenance is not epistemics).
- `next_action.key` — enumerated dispatch key for resume routing. Valid values: `run_passes`, `run_synthesis`, `run_spot_check`, `deliver`, `revision_round`, `run_audits`, `coaching`, `handoff_reentry`. See `commands/start.md` §Resume Target for the full dispatch table.
- `next_action.description` — human-readable context for display (e.g., "resume Tier 2 passes — Pass 5 next"). Not used for routing.

