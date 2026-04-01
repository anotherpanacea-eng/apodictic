# Pass Dependencies, Query Resolution & Audit Resolution

**Status:** Implementation-ready
**For:** APODICTIC Development Editor v0.6
**Last updated:** 2026-02-23

This file is loaded at runtime when the query-driven pass architecture is active. It replaces the fixed Core DE / Full DE tier model with concern-driven resolution.

---

## §1. Pass Dependency Map

### Tier 1 — Read (no dependencies, parallel-capable)

| Pass | Name | Depends on | Output artifact |
|------|------|-----------|-----------------|
| 0 | Reverse Outline | manuscript only | `[Project]_Pass0_Reverse_Outline_[runlabel].md` |
| 1 | Reader Experience | manuscript only | `[Project]_Pass1_Reader_Experience_[runlabel].md` |
| 10 | Entity Tracking | manuscript only | `[Project]_Pass10_Entity_Tracking_[runlabel].md` |

Tier 1 passes read the manuscript directly. They have no upstream dependencies and can execute in parallel.

### Tier 2 — Analyze (each depends on ≥1 Tier 1 pass)

| Pass | Name | Depends on | Output artifact |
|------|------|-----------|-----------------|
| 2 | Structural Mapping | 0 | `[Project]_Pass2_Structural_Mapping_[runlabel].md` |
| 3 | Rhythm & Modulation | 0, 1 | `[Project]_Pass3_Rhythm_[runlabel].md` |
| 4 | Emotional Value Tracking | 0, 1 | `[Project]_Pass4_Emotional_[runlabel].md` |
| 5 | Character Audit | 0 | `[Project]_Pass5_Character_Audit_[runlabel].md` |
| 6 | Scene Function Audit | 0, 2 | `[Project]_Pass6_Scene_Function_[runlabel].md` |
| 7 | POV & Voice | 0, 5 | `[Project]_Pass7_POV_Voice_[runlabel].md` |
| 8 | Reveal Economy | 0 | `[Project]_Pass8_Reveal_Economy_[runlabel].md` |
| 9 | Thematic Coherence | 0, 5 | `[Project]_Pass9_Thematic_[runlabel].md` |

Tier 2 passes run only when selected by the query resolver. Each depends on one or more Tier 1 passes, which are automatically included when a Tier 2 pass is selected.

### Tier 3 — Synthesize

| Pass | Name | Depends on | Output artifact |
|------|------|-----------|-----------------|
| Synthesis | Root cause analysis + editorial letter + results guide | All selected Tier 2 passes | `[Project]_Synthesis_[runlabel].md` + `[Project]_Results_Guide_[runlabel].md` |
| 11 | Critical Quality & Market Viability | 0, 1, 2, 5, Synthesis | `[Project]_Pass11_Critical_Quality_[runlabel].md` |

Synthesis always runs after all selected passes **and all auto-run audits** complete. Auto-run audits (§4a) are synthesis dependencies — synthesis MUST NOT begin until their findings are in the Findings Ledger. Pass 11 runs only when submission readiness is in scope.

### Running Artifacts (not passes)

| Artifact | Type | Built by | Output |
|----------|------|----------|--------|
| Findings Ledger | Running document | Appended by each evaluative pass (1, 2, 5, 8, and Full DE passes) after completion | `[Project]_Findings_Ledger_[runlabel].md` |

The Findings Ledger is not a pass. It has no tier. It is appended to by every pass that produces evaluative findings. Pass 0 and Pass 10 are data-building passes and do not append to the ledger unless they surface an observation that warrants it (e.g., a Rule Ledger inconsistency in an SFF run). The Synthesis step reads the Findings Ledger as its primary input for root cause analysis.

---

## §2. Query-to-Pass Resolver

### Resolution logic

1. Router output includes a **concern** (from Q2 or from targeted intake).
2. Look up the concern in the table below to get the minimum pass set.
3. For each selected pass, resolve its dependencies from §1. Add all upstream passes.
4. Deduplicate. Order by tier (Tier 1 first, Tier 2 second, Tier 3 last).
5. Within a tier, passes with no mutual dependencies can run in parallel.

### Concern → Minimum pass set

| User concern | Minimum passes | Macro block |
|--------------|----------------|-------------|
| Structure / architecture | 0, 2 | Structure Map |
| Pacing / momentum | 0, 1, 3 | Reader Dynamics |
| Characters / agency / arc | 0, 1, 5, 7 | Character Architecture |
| Information flow / reveals | 0, 1, 8 | Reveal Economy |
| Scene craft / function | 0, 2, 6 | Scene Delivery |
| Theme / coherence / meaning | 0, 5, 9, 10 | Theme & Continuity |
| Emotional dynamics / interiority | 0, 1, 4 | Emotional Dynamics |
| General diagnostic ("what's wrong?") | 0, 1, 2, 5, 8 | **Baseline (see §2a)** |
| Full diagnostic ("everything") | all passes | Full |
| Submission readiness | all + 11 | Submission Readiness |

### §2a-partial. Partial manuscript pass behavior

When `artifact=partial` is set, the standard resolver applies but all passes operate under modified expectations defined in `references/partial-manuscript.md`. Key differences:

- **Pass 0** adds a Momentum Report (where the draft stops, what's building)
- **Pass 1** adds stall detection and momentum tracking; marks undelivered promises as "open" not "broken"
- **Pass 2** maps available structure without projecting complete architecture; reports trajectory not template
- **Pass 5** tracks arc trajectory without penalizing incomplete arcs
- **Pass 8** includes a Setup Inventory; marks unresolved setups as assets not failures
- **Synthesis** produces a Partial Diagnostic Letter focused on "what's working, what's stalling, where to go next"

The baseline floor (Passes 0, 1, 2, 5, 8) applies to partial manuscripts as it does to complete drafts. Auto-escalation to full pass set (§2b) is suppressed for partial manuscripts — the triggers assume complete-manuscript data.

### §2a. Baseline floor rule

The "General diagnostic" row is the **floor**, not one option among equals. Apply it when:

- The user says "what's wrong" or any equivalent without specifying a concern.
- The router's fallback disambiguator fires.
- The user's answer is ambiguous and cannot be confidently mapped to a specific concern.

This replicates the current Core DE pass set (0, 1, 2, 5, 8) exactly. The baseline ensures that query-driven resolution never produces a thinner diagnostic than what users currently get from a standard run.

### §2b. Auto-escalation rule

After synthesis on any query-driven subset, check the Full DE trigger conditions:

- Synthesis identifies >5 root causes
- Reader Experience (Pass 1) logs >10 major issues
- Structural complexity flags fire (multiple timelines, unreliable narrators, non-linear structure)
- Author reports persistent unidentifiable problems or revision loops

If any trigger fires, recommend expanding to the full pass set. This is a recommendation, not automatic escalation. The system surfaces it explicitly:

> "Based on what I'm finding, the issues are interconnected enough that a full diagnostic would catch things this focused run can't. Want me to expand to the full pass set?"

The user can decline. If they accept, resolve the full pass set and continue.

---

## §3. Macro Block Definitions

User-facing groupings that organize output. Writers see 8 blocks, not 12 passes. The editorial letter groups findings by macro block within each severity tier (primary sort: severity; secondary grouping: macro block).

| Macro Block | Internal Passes | User Question |
|-------------|----------------|---------------|
| Structure Map | 0 + 2 | "Is the structure working?" |
| Reader Dynamics | 1 + 3 | "Does the pacing hold?" |
| Character Architecture | 5 + 7 | "Are my characters landing?" |
| Emotional Dynamics | 4 | "Are the emotional beats earning their weight?" |
| Scene Delivery | 6 | "Are the scenes doing their jobs?" |
| Reveal Economy | 8 | "Is the information flow right?" |
| Theme & Continuity | 9 + 10 | "Does it cohere?" |
| Submission Readiness | 11 | "Is this ready?" |

Pass 7 (POV & Voice) belongs to Character Architecture because voice is a character concern. Pass 4 (Emotional Value Tracking) has its own block — it was previously subordinated to Character Architecture, but emotional dynamics is a distinct diagnostic dimension.

When a query-driven run selects a subset of passes, only the relevant macro blocks appear in the editorial letter. Blocks with no selected passes are omitted entirely — not shown as empty.

---

## §4. Audit Resolver

The pass resolver (§2) determines which passes run. The audit resolver determines which specialized audits to surface. Both draw from the same concern signal (router output + pass findings).

### §4a. Router-triggered audits

Activated by intake answers before passes run.

| Router signal | Audit(s) | Policy | Reference file |
|---------------|----------|--------|----------------|
| Genre = Horror (Psychological) | Horror Craft Integration | Auto-recommend after Pass 1 | `genre/horror-craft.md` |
| Genre = Supernatural Horror | Supernatural Horror | Auto-recommend after Pass 1 | `genre/supernatural-horror.md` |
| Genre = Grimdark / Dark Fantasy | Grimdark / Dark Fantasy | Auto-recommend after Pass 1 | `genre/grimdark.md` |
| Genre = Mystery | Mystery/Thriller Architecture | Auto-recommend after Pass 8 | `genre/mystery-thriller-architecture.md` |
| Genre = Thriller | Mystery/Thriller Architecture | Auto-recommend after Pass 8 | `genre/mystery-thriller-architecture.md` |
| Genre = SF/Fantasy | SFF Worldbuilding Integration | Auto-recommend after Pass 10 | `genre/sff-worldbuilding.md` |
| Genre = Literary | Literary Craft Deep Dive | Auto-recommend after Pass 9 | `craft/literary-craft.md` |
| Constraint = ai | AI-Prose Calibration | Auto-run (bundled with workflow) | `craft/ai-prose-calibration.md` |
| Erotic content flagged at intake | Erotic Content | Auto-run (bundled with workflow) | `tag/erotic-content.md` |
| Genre = Romance + erotic content | Erotic Content + Consent Complexity | Auto-run / Auto-recommend | `tag/erotic-content.md`, `tag/consent-complexity.md` |
| Erotic or intimate content + power dynamics / conditioning / authority asymmetry / consent ambiguity disclosed | Consent Complexity | Auto-recommend before synthesis | `tag/consent-complexity.md` |
| Historical setting (>50 years) | Historical Fiction | Auto-recommend | `genre/historical-fiction.md` |
| Memoir or creative nonfiction | Memoir & Creative Nonfiction | Auto-run (bundled) | `genre/memoir-creative-nonfiction.md` |
| Narrative nonfiction | Narrative Nonfiction Craft | Auto-run (bundled) | `genre/narrative-nonfiction.md` |
| Short fiction (<20K words) | Short Fiction | Auto-recommend | `craft/short-fiction.md` |
| Series context flagged | Series & Composite Novel | Auto-recommend | `craft/series-composite-novel.md` |
| Series continuity concern | Series Continuity | Auto-run (requires Pass 10 + Pass 8) | `craft/series-continuity.md` |
| Representation or reception sensitivity disclosed at intake | Reception Risk | Auto-recommend before synthesis | `craft/reception-risk.md` |
| Queer romance / queer identity central | Queer Romance/Erotica | Auto-recommend | `tag/queer-romance-erotica.md` |
| Submission readiness goal | Shelf Positioning | Auto-recommend with Pass 11 | `craft/shelf-positioning.md` |
| Constraint = risk | (Risk Register — not yet built) | Note gap; proceed without | — |
| Constraint = nonfiction | (Nonfiction Pre-Draft Pathway — not yet built) | Note gap; offer closest | — |

### §4b. Finding-triggered audits

Activated by pass results during a diagnostic run. The system checks these after each pass completes.

| Pass | Finding pattern | Audit(s) | Policy |
|------|----------------|----------|--------|
| 1 (Reader Experience) | Emotional flatness, forced affect, unearned catharsis | Emotional Craft | Recommend |
| 1 (Reader Experience) | Dread/tension calibration problems | Horror Craft Integration | Recommend (if not already loaded) |
| 1 (Reader Experience) | Wrongness, supernatural pressure, belief threshold problems | Supernatural Horror | Recommend (if not already loaded) |
| 1 (Reader Experience) | Inert bleakness, violence without consequence, moral flatness, cynicism as posture | Grimdark / Dark Fantasy | Recommend (if not already loaded) |
| 1 (Reader Experience) | Comedy landing rate low, tonal inconsistency | Comedy & Satire | Recommend |
| 5 (Character Audit) | Character agency issues, puppet moments | Character Architecture | Recommend |
| 5 (Character Audit) | Female POV interiority thinning patterns | Female Interiority | Recommend |
| 5 (Character Audit) | Voice drift, dialogue undifferentiated | Scene Turn | Recommend |
| 7 (POV & Voice) | Interiority loss during peak-intensity scenes | Interiority Preservation | Recommend |
| 8 (Reveal Economy) | Information pressure problems in mystery/thriller | Mystery/Thriller Architecture | Recommend (if not already loaded) |
| 9 (Thematic Coherence) | Thematic argument under-structured, didacticism | Dialectical Clarity | Recommend |
| 9 (Thematic Coherence) | Straw opposition, authorial thumb on scale | Banister (Epistemic Humility) | Recommend |
| 6 (Scene Function) | Force delivery issues, inert action sequences | Force Architecture | Recommend |
| 1 (Reader Experience) | Uniform fluency, voice genericism (AI indicators) | AI-Prose Calibration | Auto-recommend before synthesis (if not already loaded) |
| 5 (Character Audit) | Puppet dialogue, cognitive sameness, generic fluency seams (AI indicators) | AI-Prose Calibration | Auto-recommend before synthesis (if not already loaded) |
| Any pass | Consent ambiguity, governance legibility failure, coercion aestheticization risk, or aftercare / repair incoherence in intimate or power-dynamic material | Consent Complexity | Auto-recommend before synthesis |
| Any pass | Representation contestation, screenshot risk, extractability, hostile-reader portability, or culturally volatile framing | Reception Risk | Auto-recommend before synthesis |
| 8 (Reveal Economy) | Cross-volume state drift, thread amnesia, or consequence reset in series context | Series Continuity | Auto-recommend before synthesis (if not already loaded) |
| 10 (Entity Tracking) | Cross-volume entity/state inconsistency or unresolved carry-forward consequences | Series Continuity | Auto-recommend before synthesis (if not already loaded) |
| Any pass | Fan fiction origin markers (IP scaffolding, assumed worldbuilding) | Fan Fiction Conversion | Recommend |

### §4c. Policy definitions

- **Auto-run:** Audit loads without user confirmation. Bundled with the workflow from intake. Used for audits that are definitional to the manuscript type (e.g., Memoir audit for a memoir, AI-Prose for an AI-assisted draft). **Auto-run audits are synthesis dependencies.** They must complete and append their findings to the Findings Ledger before synthesis begins. This ensures synthesis integrates auto-run audit findings into root cause analysis and triage rather than requiring post-hoc retrofitting.
- **Auto-recommend:** System recommends after the relevant pass completes. The user can decline. Used for genre-specific audits that would catch issues the passes surface but can't fully diagnose. Auto-recommend audits run after their triggering pass; if the user accepts and the audit completes before synthesis begins, its findings are integrated. If it completes after synthesis, its findings appear in the editorial letter appendix as "post-synthesis audit — not integrated into triage."
- **Auto-recommend before synthesis:** Same as Auto-recommend, but the recommendation must be resolved before synthesis begins. If the user declines or defers, the run records an explicit blind spot in the Audit Invocation Log and the synthesis/readiness layer must name the confidence limit.
- **Recommend:** System mentions availability when findings suggest relevance. The user opts in. Used for cross-cutting audits that *might* be relevant based on patterns. Same post-synthesis labeling applies if they complete late.

### §4d. Presentation format

When recommending an audit, use this format:

> **Audit available: [Audit Name]**
> Pass [N] found [brief finding summary]. The [Audit Name] audit would test [what it specifically diagnoses]. Want me to run it?

Do not list multiple recommendations simultaneously. Present them one at a time after the relevant pass, in the order they become relevant. If multiple recommendations emerge from the same pass, present the highest-severity one first.

---

## §5. Interaction with Genre Modules

Genre modules modify pass behavior (thresholds, tracking, flags). The audit resolver is separate from — and complementary to — genre module loading.

- **Genre modules** load at intake and stay active for all passes. They modify *how* passes run.
- **Genre audits** (from §4a/§4b) are deep-dive analyses that run *after* passes. They test whether the genre apparatus is doing narrative work.

A manuscript can have a genre module loaded (e.g., Horror) without running the corresponding audit (Horror Craft Integration). The module ensures passes track the right things; the audit provides the focused integration analysis. The audit resolver recommends the audit; it doesn't force it.

---

## §6. Interaction with `apodictic-audit` Command

The `apodictic-audit` command remains a direct-access shortcut. A user who types `apodictic-audit force-architecture` gets the Force Architecture audit regardless of what the resolver would recommend.

The resolver handles *automatic* surfacing during diagnostic runs. The `apodictic-audit` command handles *deliberate* requests. Both draw from the same audit catalog in `specialized-audits/SKILL.md`.

The resolver does not gate or limit `apodictic-audit`. If a user requests an audit that the resolver wouldn't have surfaced, run it without complaint.

---

*This file is a runtime reference. For design rationale, see the v0.5 UX Overhaul spec.*
