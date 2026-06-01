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

**Multi-model runs:** For consolidation work, use the consolidating model's tag. For swarm-mode, use the synthesis model's tag. Individual pass files still carry their own model tags per file naming rules.

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
- `[Project]_Pass0_Reverse_Outline_[runlabel].md`
- `[Project]_Pass1_Reader_Experience_[runlabel].md`
- `[Project]_Pass2_Structural_Mapping_[runlabel].md`
- `[Project]_Pass5_Character_Audit_[runlabel].md`
- `[Project]_Pass8_Reveal_Economy_[runlabel].md`
- `[Project]_Findings_Ledger_[runlabel].md`
- `[Project]_Core_DE_Synthesis_[runlabel].md`

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

**Multi-model runs:** Each output file carries the tag of the model that wrote it. In swarm mode where different passes run on different models, the synthesis file carries the tag of the model that wrote the synthesis.

**Partial Manuscript Diagnostic (when `artifact=partial`):**
- `[Project]_Partial_Diagnostic_[runlabel].md` (replaces `Core_DE_Synthesis`)
- All pass artifacts use standard naming but follow partial-manuscript modifications (see `references/partial-manuscript.md`)

**Fragment Synthesis (when `artifact=fragments`, goal=`draft`):**
- `[Project]_Fragment_Map_[runlabel].md`
- `[Project]_Contract_[runlabel].md` (marked as provisional)
- `[Project]_Recommended_Spine_[runlabel].md`

**Series Continuity (when active):**
- `[Project]_Series_Continuity_Audit_[runlabel].md`

**Revision Coach (when active):**
- `[Project]_Session_Plan_[runlabel].md`
- `[Project]_Revision_Calendar_[runlabel].md` (deadline mode only)

**Rolling state files** (live at project root, not inside run folders):
- `Diagnostic_State.md` — per-volume diagnostic state at the project root. If missing, initialize from `references/diagnostic-state-template.md`.
- `Diagnostic_State.meta.json` — machine-readable sidecar at the project root. If missing, initialize from `references/diagnostic-state-meta-template.json`.
- `SYNTHESIS.md` — master revision plan at the project root. Created from the first run's synthesis; updated by subsequent runs with a methodology note listing contributing runs.
- `Series_State.md` — cross-volume series state at the series root (not inside each volume's project root). If missing, initialize from `references/series-state-template.md`. Persists across volumes; updated after each volume is analyzed.

### Results Guide

Per-run artifact, not a rolling file. Lives inside its run folder alongside the pass artifacts it references. See §Results Guide Artifact in SKILL.md for format.

### Lifecycle Summary

| Workflow | Creates Run Folder | Updates Rolling State |
|----------|-------------------|----------------------|
| `/new-project` | No (initializes project root) | Creates `Diagnostic_State.md`, `README.md` |
| `/develop-edit` | `runs/YYYY-MM-DD_{model}_{type}/` | Updates `Diagnostic_State.md`, `SYNTHESIS.md`, `README.md` |
| `/audit` | `runs/YYYY-MM-DD_{model}_audit/` | Updates `Diagnostic_State.md`, `SYNTHESIS.md` (if findings alter plan), `README.md` |
| `/coach` | `runs/YYYY-MM-DD_{model}_coaching/` (on session completion) | Updates `Diagnostic_State.md` coaching log, `README.md` |
| Consolidation | `runs/YYYY-MM-DD_{model}_consolidated/` | Updates `SYNTHESIS.md` (typically the most significant update), `Diagnostic_State.md`, `README.md` |

