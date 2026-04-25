# Output Policy

*Reference file for the APODICTIC Development Editor. Loaded by core orchestrator.*

---

## Author-Facing Language (Required)

All DE outputs are author-facing documents. Framework shorthand — pass numbers (e.g., "Pass 11F"), quality codes (e.g., "QF-7"), prose tier labels (e.g., "P1"), confidence tags (e.g., "[HIGH CONFIDENCE]"), escalation thresholds, and internal scoring systems — must be translated into plain language on first use in every output file. The author should never need to consult the framework documentation to understand a finding.

**Rule:** If a term exists only in the DE framework and not in general editorial vocabulary, define it inline or replace it with a descriptive phrase. Internal codes may appear in parentheses after the plain-language version for cross-referencing, but never as the primary label.

**Examples:**
- ❌ "Prose Tier: P1"
- ✅ "Prose Tier: P1 — strong foundation with local weaknesses that need targeted polish (not a page-one rewrite)"
- ❌ "QF-7: Clustering detected"
- ✅ "Several individually minor issues cluster in the same section, compounding their effect"
- ❌ "[HIGH CONFIDENCE]"
- ✅ "All three evaluative lenses agree on this point"

---

## Output Constraints

- Maximum 5 root causes
- Maximum 10 revision checklist items (Core DE); 15 (Full DE)
- Maximum 10 must-fix flags
- Every flag requires 2-4 specific scene/page references
- Quote budget: ≤25 words per excerpt, or paraphrase + pointer
- Every proposed fix must list what it risks harming
- **Fix-Diagnosis Coherence Test (required):** Before finalizing any proposed intervention, verify that the fix addresses the *mechanism* of the diagnosed problem, not just its surface symptom. If the diagnosis is "Character X lacks narrative agency," a fix that adds more male-gaze contemplation of Character X deepens the problem. Ask: "Does this intervention change the mechanism, or does it add surface content that leaves the mechanism intact?" If the latter, revise the intervention class or flag it as insufficient.
- **Evidence Density Self-Check (required):** Before finalizing each flag, count its specific scene/page references. If a flag cites fewer than 2 references, either locate additional textual evidence to support it or downgrade confidence (not severity — a real problem with thin evidence is still a real problem, but the author needs to know the evidence base is narrow). This check runs at the flag level during triage, not as a separate pass. *Per-Must-Fix evidence density is mechanically validated as Check 5 of `scripts/validate.sh decision-layer-check`; the validator counts chapter/scene/line/page/audit-code references in the 6-line window from each Must-Fix mention. Manual self-check remains the editorial step (downgrade confidence, not severity); the validator is the gate. Override marker: `<!-- override: decision-layer-evidence-density — <rationale> -->` in the body downgrades ERROR → WARN.*

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

`{project-root}` is the active project output context. For new projects, this is created by `/new-project`. For existing projects, it is the folder that already contains the manuscript's APODICTIC output. The project folder name should use the manuscript's working title in Title_Case with underscores (e.g., `Regrets_Only`, `Chain_of_Command`).

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

---

## Confidence Calibration

All flags and diagnoses should carry confidence markers:

```
[HIGH CONFIDENCE] — Multiple passes converge on same diagnosis; textual evidence clear
[MEDIUM CONFIDENCE] — Single pass flags; awaiting corroboration from other passes or author
[LOW CONFIDENCE] — Inference from limited evidence; requires author verification
[UNCERTAIN] — Conflicting signals; presenting both interpretations
```

**Usage Guidelines:**
- HIGH requires evidence from 2+ passes or unambiguous textual proof
- MEDIUM is the default for single-pass flags
- LOW should prompt "My hypothesis is X—is this accurate?" framing
- UNCERTAIN should present the tension explicitly and ask author to clarify intent

**Never present LOW or UNCERTAIN findings as definitive diagnoses.** Frame them as hypotheses requiring verification.

---

## Epistemic Humility Reminders

Before finalizing any major diagnosis:
1. Have I checked this against stated author intent?
2. Could this be an intentional craft choice I'm misreading as error?
3. Is my genre/subgenre calibration correct for this work?
4. Am I flagging something because it violates convention, or because it actually harms the work?

When uncertain, surface the uncertainty rather than forcing false clarity.

---

## When to Engage Deep Analysis

Standard passes provide sufficient analysis for most issues. Engage extended, deliberate analysis when:

**Complexity Triggers:**
- Contradictory flags from different passes (e.g., Pass 1 says "too slow," Pass 4 says "emotional build working")
- Root cause count approaching limit (4-5 causes suggest deeper synthesis needed)
- Author disputes system diagnosis with textual evidence
- Register uncertainty in literary mode (multiple genres pulling in different directions)
- Revision loop signal (author reports rewriting same section multiple times)

**When triggered:** Pause output. Synthesize across all pass findings. Look for underlying pattern that explains surface contradictions. Consider whether apparent problems are actually intentional craft choices.

---

## Severity Honesty Protocol (v0.4.14.3)

*Canonical home for anti-sycophancy / no-self-revise rule. Other surfaces (`adversarial-stress-test.md §Lock-then-test protocol` / §Anti-softening rule, `specialized-audits/references/craft/reception-risk.md §Lock-then-classify` / §Forbidden #6, `run-synthesis.md §Step 5 Adversarial Self-Check`) reference here and add only context-specific elaborations (stress-test ordering, audit lock-then-classify discipline, self-check up/down pressure). The general principle — LLMs reliably talk themselves out of hard findings; severity locks before steelmanning — lives here. Per-audit Deficit-First Diagnostic Rule blocks (each tailored to the audit's failure modes) are the operational expression of this principle and stay in their audit reference files.*

LLMs have a documented tendency to soften negative findings in editorial analysis. This manifests as:

- Rating axes "Mixed" to avoid saying "Weak"
- Assigning Should-Fix to avoid Must-Fix
- Inflating Strengths to Protect to compensate for hard findings
- Using hedged language ("could perhaps be strengthened") for clear failures
- Finding one positive passage and using it to downgrade a systemic flag

These are diagnostic errors. The author needs honest severity to make informed revision decisions. A softened Must-Fix that becomes a Should-Fix may cause the author to skip a revision that would have saved the book.

Rules:
1. If an axis evaluation wavers between two ratings, state both and explain why you're uncertain. Do not default to the gentler option.
2. If a flag's evidence meets Must-Fix criteria per its severity guidance, assign Must-Fix. Do not downgrade based on the overall "feel" of the manuscript.
3. Strengths must be specific and evidence-based. "Strong voice" is not a strength finding. "Voice consistency in chapters 4-7 creates reliable POV trust" is.
4. Never use severity assignment to manage the author's feelings. The framework's job is accurate diagnosis.
5. **Evidence-first, verifier-backed underdiagnosis checks:** Do not assume a text is structurally sound simply because the prose flows well. Absence of structural friction must be proven, not assumed. A text is only "structurally clean" if the Reader Stress Test, the Rejection Memo, and the Absence/Blind-Spot Inventory explicitly fail to surface deep flaws.

---

## Severity Floor Rules (v0.4.14.3)

*Canonical home for severity-floor rules. Mechanical check: `scripts/validate.sh severity-floor <editorial_letter_file>`. Other framework surfaces (e.g., `run-synthesis.md` Step 10, `specialized-audits/references/craft/reception-risk.md` §7) reference these rules rather than restating them; if a surface appears to encode a fourth rule, treat that as a duplication bug and consolidate here.*

These rules prevent diagnostic softening from producing incoherent verdicts:

1. If any core-promise axis is rated Weak at High or Medium intensity, at least one flag must be Must-Fix. (A Weak core-promise axis with no Must-Fix flags means either the axis rating is wrong or the flag severity is wrong. Reconcile before proceeding.) At Low intensity or for peripheral axes, a Weak rating may stand with Should-Fix flags only, but must be explicitly justified.

2. If any Must-Fix flag has Systemic blast radius, the verdict cannot exceed Partial Fit (for tag audits) or equivalent ceiling for passes.

3. If three or more flags are Should-Fix or above, the verdict cannot be the highest positive band without explicit justification of why the flag volume doesn't impair the core contract.

**Override path:** A run that intentionally deviates from a rule (e.g., a Weak axis the model judges does not warrant a Must-Fix because the underlying issue is editorial-stance not craft-failure) must record the deviation via a structured marker placed **in the letter body** (not in an appendix), plus a parallel narrative entry in Appendix B (Severity Calibration). Marker syntax (one per rule):

```
<!-- override: severity-floor-weak-axis — <one-sentence rationale> -->
<!-- override: severity-floor-systemic — <one-sentence rationale> -->
<!-- override: severity-floor-band-cap — <one-sentence rationale> -->
```

Markers in appendix bodies are non-canonical (synthesis body is canonical for findings; appendices hold evidence) and the validator will not honor them. Absence of marker and rationale = blocked synthesis: re-tier or override-with-reason in the body, but do not silently violate the floor.

---

## Editorial Letter Tone and Voice

The editorial letter should sound like a knowledgeable editor who has read the book carefully and is being direct. Avoid:
- Framework jargon in the main text (severity labels, pass numbers, protocol names)
- Mechanistic transition language ("Moving to the next finding..." / "As identified in Pass 2...")
- Strength-padding or diplomatic qualifiers ("While the pacing could perhaps be strengthened...")
- Formulaic openings ("This manuscript demonstrates..." / "The analysis reveals...")

Use:
- Specific scene references embedded in prose (not in separate evidence blocks)
- Direct, declarative assessment ("The problem is that the book only does this once, and late.")
- The book's own language and imagery when it clarifies the point
- Bolded thesis statements as section headings for scannability

---

## Cross-Reference Convention

When the editorial letter references evidence from a pass data artifact — a table, inventory, matrix, timeline, or other structured data — include a parenthetical cross-reference directing the author to the artifact:

> *(see [Pass Name], §[Section or Table Name])*

**Examples:**
- *(see Character Audit, Agency Assessment table)*
- *(see Reveal Economy, Fairness Test #1)*
- *(see Structural Mapping, §Causal Gaps)*
- *(see Reverse Outline, SFF Rule Ledger, entries #10-14)*

Cross-references appear inline within the prose argument. They do not replace the argument — the letter must still make its case in plain language. The cross-reference tells the author where to find the supporting evidence if they want to verify, push back, or use the data during revision.

**When to cross-reference:** Use cross-references when the pass artifact contains structured data (tables, inventories, matrices) that the author can use as a revision tool. Do not cross-reference for every claim — only when pointing the author to a specific artifact adds value beyond the prose argument itself.

**Tone:** Cross-references should feel like a knowledgeable editor saying "I've documented this in detail — here's where to find it." They should not feel like a framework generating citations.

---

## Pass-Level Output Protocol (v0.4.14.3)

Each individual pass that produces findings (Pass 1, Pass 2, Pass 5, Pass 8, and all Full DE passes) must follow this output ordering:

1. **Analysis / Findings** — the pass's primary diagnostic content
2. **Rejection Memo** — 2-4 sentences stating the strongest structural case against the manuscript based on this pass's findings. Required. Must reference evidence from the pass; no uncited new claims. Write as: "The strongest [structural / reader-experience / character-level] case against this manuscript is..."
3. **Priority Leaks** — flagged issues with severity assignments
4. **Strengths** — specific, evidence-based strengths with citations. Cap: if the pass surfaces more leaks than strengths, strengths ≤ leaks count; otherwise max(leaks, 3).

Pass 0 (Reverse Outline) and Pass 10 (Entity Tracking) are data-building passes and produce reference artifacts rather than evaluative findings. They do not require rejection memos or strengths sections.

---

## Mandatory Appendices (v0.4.15)

Every editorial letter must include the following appendices. These are not optional even when the letter is otherwise strong — they provide the author with diagnostic transparency and the framework owner with reproducibility data.

*Appendix presence is mechanically validated by `scripts/validate.sh decision-layer-check <editorial_letter_file>`. The validator surfaces missing A/B/C as ERROR; an override marker placed in the synthesis body — `<!-- override: decision-layer-appendices — <rationale> -->` — downgrades to WARN per the body-vs-appendix override discipline established in §Severity Floor Rules. The validator does not check appendix content; that remains an editorial step.*

1. **Appendix A: Diagnostic Detail.** Pointers to companion pass files and supplementary audit findings, with brief descriptions of what each contains. This tells the author where to find the evidence and revision tools behind the letter's arguments. If any auto-recommend or user-accepted audits completed **after** synthesis was written, list them separately as: "**Post-synthesis audits** (findings not integrated into triage — review independently):" followed by the audit name and findings file pointer. Auto-run audits should never appear in this post-synthesis section — they are synthesis dependencies and must complete before synthesis begins (see `pass-dependencies.md` §4c). If any high-risk audit was deferred or declined, Appendix A must also name that blind spot and state how it limits confidence, readiness, or interpretive certainty.

2. **Appendix B: Severity Calibration.** Compressed summary of the adversarial self-check — which findings were tested for softening or over-escalation, in which direction, and whether any severities were adjusted. This is the author's assurance that severity assignments were stress-tested, not just assigned.

3. **Appendix C: Framework Notes.** Analysis version, model, run date, passes completed, protocol flags, prior analyses on file, cross-version stability notes (if applicable). This is the run's metadata — it makes results reproducible and lets the framework owner track behavior across versions.

If a letter omits any of these appendices, the omission is a framework compliance failure regardless of the letter's analytical quality.
