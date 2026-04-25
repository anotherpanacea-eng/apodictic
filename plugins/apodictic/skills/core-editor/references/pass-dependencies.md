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
| 10 | Entity Tracking + Timeline Architecture | manuscript only | Run-folder: `[Project]_Pass10_Entity_Tracking_[runlabel].md` (Rule Ledger + Entity Table + legacy chronology). Project-level rolling: `Timeline.md` at project root (8-section schema per `references/pass-10.md`). |

Tier 1 passes read the manuscript directly. They have no upstream dependencies and can execute in parallel.

**Pass 10 — Pass-10-Class artifact.** Pass 10 produces both a run-folder-scoped artifact (existing Entity Tracking output) and a project-level rolling artifact (`Timeline.md`). The Timeline artifact is the first live instance of the Pass-10-Class Rolling Structured Artifacts pattern named in `core-editor/SKILL.md §Project Integration` (alongside `Diagnostic_State.md`, `SYNTHESIS.md`, `Argument_State.md`, `Series_State.md`). Schema lives in `references/pass-10.md`. Three mechanical validators pair with the Timeline artifact: `validate.sh timeline-diff`, `validate.sh timeline-arithmetic`, `validate.sh timeline-anchor-conflict`. Inconsistency Ledger counts feed synthesis-layer severity per the Canonical Audit-Signal Propagation Rule (`run-synthesis.md §Step 2`).

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

**Audit-signal propagation:** Audit-internal severity signals (Must-Fix floors, hard gates, HIGH/Alert ratings) propagate to synthesis-layer Must-Fix / Should-Fix / Could-Fix per the canonical rule in `run-synthesis.md §Step 2 — Canonical Audit-Signal Propagation Rule`. Per-audit propagation specifics — which audit-internal signal classes map to which synthesis severities for which audits — live in §4e (Audit-Signal Propagation Table). Audits not enumerated in §4e fall back to the canonical rule's default mapping.

### §4a. Router-triggered audits

Activated by intake answers before passes run. When a router-triggered audit is also surfaced via a finding-trigger in §4b, the highest-obligation tier wins per §4f.

**Tier verification (Phase 6 Wave 2 / CR-3 closure).** All router-triggered audit tier assignments below were re-audited per the Phase 6 plan against Phase 2 archaeology, Phase 3 inventory classifications, and Codex critique CR-3 evidence. Result: existing tiers hold. The Auto-recommend before synthesis tier for Reception Risk and Consent Complexity (the two router-triggered audits at that obligation tier) was confirmed against Phase 2 finding that absent these audits, the run records an explicit blind spot — the obligation tier's defining condition. Auto-run audits (Constraint=ai → AI-Prose; Erotic Content; Memoir; Narrative NF) were confirmed against the §4c Auto-run definition: bundled at intake because the audit is definitional to the manuscript type. No router-tier promotions or demotions in this wave; future audit additions follow the §4c Audit Tier Promotion Criteria.

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
| Argument-shaped run (constraint=nonfiction + intake hint at white paper / policy brief / testimony / op-ed / academic article / regulatory comment / expert affidavit) | Field Reconnaissance | **Hard Prerequisite** when high-stakes signal present (testimony, expert affidavit, regulatory comment, peer-reviewed publication, or `constraint=high-stakes` flag); otherwise **Auto-recommend before synthesis** | `craft/research-field-recon.md` |
| Argument-shaped run (constraint=nonfiction + high-stakes intake hint: testimony / expert affidavit / regulatory comment / peer-reviewed publication) | Citation Verifier | **Pre-DE Prerequisite** (runs before passes; not a DE-internal audit — see audit reference) | `craft/research-citation-verifier.md` |

**Argument-shaped routing definition (Phase 6 Wave 3 / CR-4 closure).** A run is "argument-shaped" when intake produces `constraint=nonfiction` AND the intake hint, declared form, or contract draft places it in the persuasive-argument family: white paper, policy brief, testimony (oral or written), op-ed, academic article, grant proposal, legal brief, book review, advocacy journalism, open letter, regulatory comment, expert affidavit, or peer-reviewed publication. Memoir, narrative nonfiction, and creative-nonfiction forms are nonfiction but *not* argument-shaped; they route via their own §4a rows above.

**High-stakes signal definition.** "High-stakes" applies when the manuscript's literature provenance is dispositive — i.e., a counterevidence miss could carry legal, regulatory, professional, or publication consequences the author cannot absorb post-hoc. The signal fires when any of the following hold: (a) intake declares the form as testimony, expert affidavit, regulatory comment, or peer-reviewed publication; (b) the contract carries an explicit `constraint=high-stakes` flag; (c) the intake hint identifies the audience as a court, legislative body, regulatory agency, or peer-review panel. Op-eds, academic articles, and policy briefs that lack these hooks default to the Auto-recommend before synthesis tier; the user can request Hard Prerequisite escalation at intake.

**Why argument-shaped runs get a prerequisite tier.** TAY Stage 2 (`docs/review-log/2026-04-24_tay-stage-2-comparative.md`) documented seven literature-counterevidence blind spots that the Stage 1 development edit missed because Field Reconnaissance was not prerequisited — Wave 2 audits operate on manuscript-as-written, so competing studies, replication failures, and meta-analytic counterevidence the author had documented privately (or that exist in the literature but were not surfaced) never entered the Findings Ledger. The Hard Prerequisite tier closes this gap by routing literature-counterevidence surfacing **before** the argument engine fires, so downstream passes (Dialectical Clarity, Argument Red Team, Argument Evidence Deep-Dive) operate against a literature-aware claim graph rather than a manuscript-internal one. The Auto-recommend before synthesis tier provides the same routing for lower-stakes argument runs with an opt-out (and mandatory blind-spot disclosure if declined — see `run-synthesis.md` Step 3 Blind Spot / Absence Inventory and Step 11 Appendix A).

### §4b. Finding-triggered audits

Activated by pass results during a diagnostic run. The system checks these after each pass completes. When a finding-triggered audit is also surfaced via §4a or via another §4b finding-trigger, the highest-obligation tier wins per §4f.

**Tier verification (Phase 6 Wave 2 / CR-3 closure).** All finding-triggered audit tier assignments below were re-audited per the Phase 6 plan. Confirmed against Phase 2 archaeology (commit history showing five audits — Compression, Female Interiority, Scene Turn, Interiority Preservation, Decision Pressure — promoted from Recommend to Auto-recommend before synthesis to catch omission patterns that undermine the whole letter if skipped) and against Phase 4's audit-signal propagation work. The promotions hold. Demotion candidates considered and rejected: Compression / Female Interiority / Interiority Preservation / Scene Turn / Decision Pressure (catch undetectable-by-passes-alone omissions; blind-spot disclosure is non-equivalent to running them); AI-Prose / Reception Risk (hard gate semantics make synthesis-without-them confidence-limiting). Recommend tier on Character Architecture, Emotional Craft, Banister, and others remains: each catches a class of issue that *could* be inferred from passes, so opt-in is the right tier. The Banister-for-thematic-runs candidate flagged in Phase 3 is documented in §4e (its propagation entry) but the tier stays at Recommend pending stronger Phase 7 evidence.

| Pass | Finding pattern | Audit(s) | Policy |
|------|----------------|----------|--------|
| 1 (Reader Experience) | Pacing stalls, rushed sequence compression, narrative summary overuse | Compression | Auto-recommend before synthesis |
| 1 (Reader Experience) | Emotional flatness, forced affect, unearned catharsis | Emotional Craft | Recommend |
| 1 (Reader Experience) | Dread/tension calibration problems | Horror Craft Integration | Recommend (if not already loaded) |
| 1 (Reader Experience) | Wrongness, supernatural pressure, belief threshold problems | Supernatural Horror | Recommend (if not already loaded) |
| 1 (Reader Experience) | Inert bleakness, violence without consequence, moral flatness, cynicism as posture | Grimdark / Dark Fantasy | Recommend (if not already loaded) |
| 1 (Reader Experience) | Comedy landing rate low, tonal inconsistency | Comedy & Satire | Recommend |
| 5 (Character Audit) | Character agency issues, puppet moments | Character Architecture | Recommend |
| 5 (Character Audit) | Female POV interiority thinning patterns | Female Interiority | Auto-recommend before synthesis |
| 5 (Character Audit) | Voice drift, dialogue undifferentiated | Scene Turn | Auto-recommend before synthesis |
| 7 (POV & Voice) | Interiority loss during peak-intensity scenes | Interiority Preservation | Auto-recommend before synthesis |
| 8 (Reveal Economy) | Information pressure problems in mystery/thriller | Mystery/Thriller Architecture | Recommend (if not already loaded) |
| 9 (Thematic Coherence) | Thematic argument under-structured, didacticism | Dialectical Clarity | Recommend |
| 9 (Thematic Coherence) | Straw opposition, authorial thumb on scale | Banister (Epistemic Humility) | Recommend |
| 6 (Scene Function) | Force delivery issues, inert action sequences | Force Architecture | Recommend |
| 1 (Reader Experience) | Uniform fluency, voice genericism (AI indicators) | AI-Prose Calibration | Auto-recommend before synthesis (if not already loaded) |
| 5 (Character Audit) | Puppet dialogue, cognitive sameness, generic fluency seams (AI indicators) | AI-Prose Calibration | Auto-recommend before synthesis (if not already loaded) |
| Any pass | Unsupported choice architecture, false dilemmas, or abstract risk persistence | Decision Pressure | Auto-recommend before synthesis |
| Any pass | Consent ambiguity, governance legibility failure, coercion aestheticization risk, or aftercare / repair incoherence in intimate or power-dynamic material | Consent Complexity | Auto-recommend before synthesis |
| Any pass | Representation contestation, screenshot risk, extractability, hostile-reader portability, or culturally volatile framing | Reception Risk | Auto-recommend before synthesis |
| 8 (Reveal Economy) | Cross-volume state drift, thread amnesia, or consequence reset in series context | Series Continuity | Auto-recommend before synthesis (if not already loaded) |
| 10 (Entity Tracking) | Cross-volume entity/state inconsistency or unresolved carry-forward consequences | Series Continuity | Auto-recommend before synthesis (if not already loaded) |
| Any pass | Fan fiction origin markers (IP scaffolding, assumed worldbuilding) | Fan Fiction Conversion | Recommend |

### §4c. Policy definitions

The tier definitions below establish the obligation ordering used by the §4f Audit Tier Precedence Rule: **Hard Prerequisite > Pre-DE Prerequisite > Auto-run > Auto-recommend before synthesis > Auto-recommend > Recommend**.

- **Hard Prerequisite (Phase 6 Wave 3):** Audit MUST complete before any Tier 2 evaluative pass can begin. This is stronger than Auto-run: Auto-run audits are *synthesis* dependencies (they must complete before synthesis), but Hard Prerequisite audits are *pass* dependencies (they must complete before the passes themselves run). Used when the audit's output materially changes what the passes are evaluating against — e.g., Field Reconnaissance for high-stakes argument-shaped runs, where surfacing literature-counterevidence before the argument engine fires changes the claim graph that Dialectical Clarity / Argument Red Team / Argument Evidence operate on. **A user-declined Hard Prerequisite cannot proceed silently.** If the user declines, the run either (a) terminates with an explicit "Hard Prerequisite declined; argument-engine passes cannot run as configured — re-route as Auto-recommend before synthesis with blind-spot disclosure?" prompt, or (b) downgrades to Auto-recommend before synthesis with a body-of-letter disclosure recorded at synthesis. There is no third path; silent omission is forbidden at this tier.
- **Pre-DE Prerequisite (Phase 6 Wave 3):** Audit runs *before* the Development Edit begins; it is **not** a DE-internal audit. Used for source-integrity work that establishes evidentiary preconditions (Citation Verifier for high-stakes argument-shaped runs, where ghost citations / quote drift / paraphrase inflation would invalidate downstream argument analysis). The audit's output (e.g., `Citation_Ledger.md`) is consumed by argument-cluster passes but the audit itself is not part of the pass dependency graph — it is a precondition for the run, not a member of it. See the audit's reference file for the full pre-DE handoff protocol.
- **Auto-run:** Audit loads without user confirmation. Bundled with the workflow from intake. Used for audits that are definitional to the manuscript type (e.g., Memoir audit for a memoir, AI-Prose for an AI-assisted draft). **Auto-run audits are synthesis dependencies.** They must complete and append their findings to the Findings Ledger before synthesis begins. This ensures synthesis integrates auto-run audit findings into root cause analysis and triage rather than requiring post-hoc retrofitting.
- **Auto-recommend:** System recommends after the relevant pass completes. The user can decline. Used for genre-specific audits that would catch issues the passes surface but can't fully diagnose. Auto-recommend audits run after their triggering pass; if the user accepts and the audit completes before synthesis begins, its findings are integrated. If it completes after synthesis, its findings appear in the editorial letter appendix as "post-synthesis audit — not integrated into triage."
- **Auto-recommend before synthesis:** Same as Auto-recommend, but the recommendation must be resolved before synthesis begins. If the user declines or defers, the run records an explicit blind spot in the Audit Invocation Log and the synthesis/readiness layer must name the confidence limit. This policy applies to critical structural and consent issues that undermine the core framework (e.g., Compression, Interiority, AI-Prose).
- **Recommend:** System mentions availability when findings suggest relevance. The user opts in. Used for cross-cutting audits that *might* be relevant based on patterns. Same post-synthesis labeling applies if they complete late.

#### Audit Tier Promotion Criteria

A new audit (or a re-audited existing audit) earns Auto-recommend before synthesis status when **all three** of the following hold:

1. **The audit has named hard gates or audit-internal Must-Fix floors.** Audits with only Note/Flag/Recommend-style outputs do not warrant the Auto-recommend before synthesis tier — the obligation is reserved for audits that produce signals strong enough to gate synthesis severity.
2. **The audit catches a class of issue undetectable by passes alone.** If the passes' Findings Ledger reliably surfaces the issue without the audit, the audit is supplementary (Recommend tier). The Auto-recommend before synthesis tier is for audits whose absence creates a *blind spot* — an issue the synthesis cannot otherwise see.
3. **Blind-spot disclosure is non-equivalent to running the audit.** That is, naming "we did not run X" in Appendix A is materially weaker than running X and integrating its findings. Audits where the disclosure adequately substitutes for the audit do not warrant the higher tier.

A new audit earns Auto-run status when **all three** above hold AND **either**: (a) the audit is definitional to the manuscript type (Memoir audit for memoir; AI-Prose for AI-assisted draft); or (b) the audit's prerequisite signals are present at intake without ambiguity (Erotic Content disclosed; Series context disclosed with Pass 10+8 prerequisites).

A new audit earns Auto-recommend status when criterion 1 holds (named hard gates or Must-Fix floors exist) AND criterion 2 *partially* holds (passes detect the issue at lower severity than the audit; the audit refines), but criterion 3 fails (blind-spot disclosure is reasonably substitutable for the audit).

**Decisions get logged.** Each promotion (or principled non-promotion) is recorded in the changelog entry that introduces it. Phase 2 archaeology surfaced cfaadef's batch promotion of five audits; future audit additions follow the criterion above with explicit rationale. The §4a/§4b verification subsections at the start of each table document the criterion's application to existing audits.

### §4d. Presentation format & Priority Queue

When recommending an audit, use this format:

> **Audit available: [Audit Name]**
> Pass [N] found [brief finding summary]. The [Audit Name] audit would test [what it specifically diagnoses]. Want me to run it?

Do not list multiple recommendations simultaneously. Present them one at a time after the relevant pass, in the order specified by the priority queue below.

**Priority queue (when multiple audits trigger from the same pass).** Apply ordering rules in sequence; the first rule that distinguishes the audits is dispositive:

1. **Higher tier fires first.** Auto-run > Auto-recommend before synthesis > Auto-recommend > Recommend. (Auto-run audits should already be loaded; this rule mainly orders the remaining recommendations.)
2. **Within the same tier, higher audit-internal severity fires first.** Hard gate beats Must-Fix floor beats HIGH/Alert beats MEDIUM/Flag beats LOW/Note. The audit-internal severity comes from the audit reference file's named-flag table.
3. **Within the same internal severity, higher signal count fires first.** An audit whose finding-trigger fired three times beats an audit whose finding-trigger fired once. Signal count comes from the Audit Invocation Log rationale column (per §4f).
4. **Tie-breaking: alphabetical by audit name** for deterministic queue ordering.

**Re-prompt suppression.** A user-recommended user-declined audit does not re-prompt within the same run unless the §4f tier-precedence rule fires (declined-at-Recommend, later-promoted-by-finding-trigger to Auto-recommend before synthesis re-prompts with the new tier rationale; declined-at-Auto-recommend-before-synthesis does not re-prompt — the blind-spot disclosure persists).

**Tier resolution precedes queue ordering.** Per §4f cross-reference: when an audit is surfaced through multiple paths, resolve its tier first (highest obligation wins). Then apply the priority queue to order surface presentation.

**Worked examples.**

*Example 1 — Pass 5 finding triggers two audits at different tiers.*
Pass 5 (Character Audit) surfaces female POV interiority thinning AND voice drift. From §4b: Female Interiority is Auto-recommend before synthesis; Scene Turn (voice drift trigger) is also Auto-recommend before synthesis. Both at the same tier. Apply rule 2: assume Female Interiority's audit-internal Must-Fix floor fires (≥3 thinning instances in interiority-load scenes); Scene Turn's audit-internal Should-Fix-default flag fires for the voice drift signal. Female Interiority's hard signal beats Scene Turn's softer one — Female Interiority presents first; Scene Turn presents second.

*Example 2 — Pass 1 finding triggers Compression (Auto-recommend before synthesis) AND Reception Risk (Auto-recommend before synthesis from §4a router-trigger).*
Both at Auto-recommend before synthesis tier. Apply rule 2: Reception Risk Alert (hard-gate-class signal from §7) beats Compression Must-Fix floor (Must-Fix-floor-class signal). Reception Risk presents first; Compression presents second.

*Example 3 — Pass 9 finding triggers Dialectical Clarity (Recommend) AND Banister (Recommend).*
Both at Recommend tier. Apply rule 2: assume both produce Flag-class signals at MEDIUM. Apply rule 3: if Dialectical Clarity's finding-trigger fired three times across passes (warrant-gap convergence in 1, 5, 9) and Banister fired once (only Pass 9), Dialectical Clarity presents first. Apply rule 4 only if rules 2-3 don't distinguish: alphabetical (Banister < Dialectical Clarity).

### §4e. Audit-Signal Propagation Table (per-audit operationalization of the Canonical Rule)

This is the per-audit operationalization of the Canonical Audit-Signal Propagation Rule. Canonical home: `run-synthesis.md §Step 2 — Canonical Audit-Signal Propagation Rule`. The canonical rule defines the *propagation taxonomy* (Must-Fix floor → synthesis Must-Fix; hard gate → synthesis Must-Fix; HIGH → synthesis Must-Fix or Should-Fix per audit context; MEDIUM → synthesis Should-Fix; LOW → synthesis Could-Fix). This table specifies *per-audit applicability*: for each audit, which audit-internal signal classes propagate to which synthesis severity, and what context modifiers apply.

**How to read each row.** Each row maps one audit-internal signal class to one synthesis severity. An audit may produce multiple signal classes; each gets its own row. Where audit-internal signals are context-modified (e.g., Compression's Must-Fix floor only applies in specific channels; Reception Risk Alerts vary by genre context), the Context column documents the modifier. The Source column points to the audit reference file specifying the signal class. The Override column flags any deviation from the canonical default mapping.

**Validator integration.** The `scripts/validate.sh audit-signal-propagation` validator (Phase 4) reads this table to verify that audit-internal signals reach the editorial letter at the rule-mandated synthesis severity. The Phase 4 default mapping (canonical rule's column 2) is the fallback for any audit not enumerated here; the per-audit entries below refine the default for audit-specific context.

**Override path.** Per-audit refinements that diverge from the canonical default mapping are documented in the Override column with a brief rationale. Synthesis-time overrides for individual findings still follow the canonical rule's body-only marker pattern (`<!-- override: audit-propagation-must-fix — <rationale> -->`, etc.).

#### Universal audits

| Audit | Audit-internal signal | Synthesis severity | Context modifier | Source | Override |
|---|---|---|---|---|---|
| Stakes System | STX/PC/IM/EG/MP/CL flag at default Must-Fix | Must-Fix | Climax-critical or contract-breaking; STX-1/STX-3 by default | `craft/stakes-system.md` §STX-/PC-/IM- | — |
| Stakes System | STX/PC/IM/EG/MP/CL flag at default Should-Fix | Should-Fix | Repeated, multi-scene; default for most flags | `craft/stakes-system.md` §STX-/PC-/IM- | — |
| Stakes System | STX/PC/IM/EG/MP/CL flag at default Could-Fix | Could-Fix | Local, low blast radius; STX-2 / EG-3 / MP-3 default | `craft/stakes-system.md` §STX-/PC-/IM- | — |
| Stakes System | Convergence: ≥2 universal audits flag the same scene at MEDIUM | Should-Fix | Cross-universal-audit convergence elevates by one tier | `craft/stakes-system.md` + canonical rule | Refines default (cross-audit elevation) |
| Decision Pressure | AV/CS/IS/EC/RF/TR/PV flag at default Must-Fix | Must-Fix | Climax-critical or systemic; AV-2 climax-critical, EC-2 systemic, RF-1 default | `craft/decision-pressure.md` §AV-/CS-/IS- | — |
| Decision Pressure | AV/CS/IS/EC/RF/TR/PV flag at default Should-Fix | Should-Fix | Repeated, multi-scene; default for most flags | `craft/decision-pressure.md` §AV-/CS-/IS- | — |
| Decision Pressure | AV/CS/IS/EC/RF/TR/PV flag at default Could-Fix | Could-Fix | Local; AV-3 / IS-3 / RF-3 / PV-3 default | `craft/decision-pressure.md` §AV-/CS-/IS- | — |
| Scene Turn | G-/C-/O-/Sq-/H-/U-/P-code at hard-gate severity | Must-Fix | Scene fails Turn Test (no goal + no change + no consequence) | `craft/scene-turn.md` §Hard Gates / Turn Test | — |
| Scene Turn | G-/C-/O-/Sq-/H-/U-/P-code at default flag | Should-Fix | Pattern across ≥3 scenes (e.g., O5 outcome monotony) | `craft/scene-turn.md` §Named Flags | — |
| Scene Turn | Single-scene flag (isolated) | Could-Fix | Isolated scene-mechanics flag | `craft/scene-turn.md` §Named Flags | — |

#### High-priority craft audits

| Audit | Audit-internal signal | Synthesis severity | Context modifier | Source | Override |
|---|---|---|---|---|---|
| Compression | Must-Fix floor (any §7 hard gate fires) | Must-Fix | Always; primary CR-8 case | `craft/compression-audit.md` §7 Hard Gates + §Severity table | — |
| Compression | Should-Fix flag (no hard gate, pattern-level) | Should-Fix | Pattern across ≥3 scenes / one channel saturated | `craft/compression-audit.md` §Severity table | — |
| Compression | Could-Fix flag (single-scene) | Could-Fix | Isolated low-confidence reclassification per §316 rule | `craft/compression-audit.md` §Severity table | — |
| Reception Risk | Alert (post-calibration, Gates 1-5 fire) | Must-Fix | Always when not artifact-of-method (e.g., Gate 2 extractable hate, Gate 3 minor exploitation) | `craft/reception-risk.md` §7 Hard Gates | — |
| Reception Risk | Alert + coercion-marked context (PF-4/PF-2 patterns) | Must-Fix + retry-loop trigger #2 | Coercion-marked findings additionally fire underdiagnosis-trigger-hard-gate | `craft/reception-risk.md` §7 + `run-synthesis.md §Step 9` | Refines default (cross-step trigger) |
| Reception Risk | Flag (post-calibration) | Should-Fix | Pattern-level concern, not Alert | `craft/reception-risk.md` §6 Severity Levels | — |
| Reception Risk | Note (post-calibration) | Could-Fix | Isolated finding, surrounding framing intact | `craft/reception-risk.md` §6 Severity Levels | — |
| Banister (Epistemic Humility) | HIGH-confidence rhetorical-fairness failure (e.g., systemic straw opposition, narrative-mechanics deck-stacking, certainty-without-warrant) | Must-Fix | Thematic-coherence-load is high (Pass 9 selected); failure is systemic not local | `craft/banister.md` §Flag families | Refines default per Codex §9.4 (Banister HIGH gap closure) |
| Banister (Epistemic Humility) | MEDIUM (single-flag, recurring across 2-3 scenes) | Should-Fix | Pattern-level | `craft/banister.md` §Flag families | — |
| Banister (Epistemic Humility) | LOW (single-flag, isolated) | Could-Fix | Local fairness lapse | `craft/banister.md` §Flag families | — |
| AI-Prose Calibration | Systemic severity (manuscript-wide pattern across ≥3 AIC families) | Must-Fix | Always; primary contamination-map case | `craft/ai-prose-calibration.md` §Severity (Spot/Pattern/Systemic) | — |
| AI-Prose Calibration | Pattern severity (recurring across multiple scenes; ≥2 AIC families) | Should-Fix | Pattern-level signal | `craft/ai-prose-calibration.md` §Severity | — |
| AI-Prose Calibration | Spot severity (isolated to one passage; surrounding text has voice) | Could-Fix | Local seam | `craft/ai-prose-calibration.md` §Severity | — |
| Female Interiority | Hard gate (≥3 thinning instances in interiority-load scenes) | Must-Fix | Interiority-load scenes (combat, intimate, crisis) | `craft/female-interiority.md` §Hard Gates | — |
| Female Interiority | Pattern flag (gendered thinning across 2-3 scenes) | Should-Fix | Pattern-level | `craft/female-interiority.md` §Named flags | — |
| Female Interiority | Spot flag (single-scene thinning) | Could-Fix | Isolated | `craft/female-interiority.md` §Named flags | — |
| Interiority Preservation | Hard gate (interiority loss in named peak-intensity scene) | Must-Fix | Combat / interrogation / intimate / crisis POV scene | `craft/interiority-preservation.md` §Hard Gates | — |
| Interiority Preservation | Pattern flag | Should-Fix | Pattern across ≥2 peak-intensity scenes | `craft/interiority-preservation.md` §Named flags | — |
| Interiority Preservation | Spot flag | Could-Fix | Isolated | `craft/interiority-preservation.md` §Named flags | — |

#### Argument cluster (Dialectical Clarity, Argument Red Team, Argument Persuasion, Argument Evidence, Adversarial Evidence Review, Field Recon, Citation Verifier)

| Audit | Audit-internal signal | Synthesis severity | Context modifier | Source | Override |
|---|---|---|---|---|---|
| Dialectical Clarity | WR0 (warrant gap) at HIGH burden audience | Must-Fix | Burden level HIGH from §Step 1 (policy brief, expert testimony) | `craft/dialectical-clarity.md` §Step 4 WR codes + §Step 1 burden | Refines default (audience-calibrated) |
| Dialectical Clarity | WR0 (warrant gap) at MEDIUM burden audience | Should-Fix | Burden level MEDIUM | `craft/dialectical-clarity.md` §Step 4 WR codes | — |
| Dialectical Clarity | WR1 (missing backing for contested warrant) | Must-Fix | Always | `craft/dialectical-clarity.md` §Step 4 WR codes | — |
| Dialectical Clarity | CL2 (subclaim gap) | Must-Fix | Always | `craft/dialectical-clarity.md` §CL codes | — |
| Dialectical Clarity | OB4 (concession without cost) | Should-Fix | Pattern-level concession theater | `craft/dialectical-clarity.md` §OB codes | — |
| Dialectical Clarity | BP2 (scope creep) | Should-Fix | Always; upgrade to Must-Fix if BP2 in conclusion | `craft/dialectical-clarity.md` §BP codes | Refines default (location-sensitive) |
| Argument Red Team | RT-flag at Fatal severity | Must-Fix | Adversary can defeat the argument entirely | `craft/argument-red-team.md` §Severity Scale | — |
| Argument Red Team | RT-flag at Major severity | Should-Fix | Real vulnerability; argument needs reinforcement | `craft/argument-red-team.md` §Severity Scale | — |
| Argument Red Team | RT-flag at Manageable severity | Could-Fix | Limited blast radius | `craft/argument-red-team.md` §Severity Scale | — |
| Argument Persuasion | PS-flag fortification failure (audience-posture mismatch) | Should-Fix | Pattern across ≥2 audience postures | `craft/argument-persuasion.md` §PS signals | — |
| Argument Persuasion | PS-flag at hard-rule violation | Must-Fix | Hard rule fires (e.g., concession-without-cost convergence) | `craft/argument-persuasion.md` §7 Hard Rules | — |
| Argument Evidence | AE10 (Verification Hotspot Cluster) | Must-Fix | Always; per Hard Gate #1 (Evidence Ledger escalates) | `craft/argument-evidence.md` §Hard Gates | — |
| Argument Evidence | AE1 on C0 support (provenance opaque on central claim) | Must-Fix | Always; per Hard Gate #2 | `craft/argument-evidence.md` §Hard Gates | — |
| Argument Evidence | AE2 (Secondary Flattening) | Should-Fix | Pattern across ≥2 supports; Must-Fix if confirmed via Citation Verifier | `craft/argument-evidence.md` §Named flags | Refines default (verification-conditional) |
| Argument Evidence | AE5 + AE6 co-occurrence (testimony boundary) | Must-Fix | Per Hard Gate #3 (handoff to Coaching Track 8) | `craft/argument-evidence.md` §Hard Gates | — |
| Argument Evidence | AE3 / AE4 / AE7 / AE8 / AE9 isolated | Should-Fix | Pattern-level; upgrade to Must-Fix on convergence | `craft/argument-evidence.md` §Named flags | — |
| Adversarial Evidence Review | HX-class survivability failure (claim cannot survive hostile expert scrutiny) | Must-Fix | Survivability judgment = Vulnerable across multiple protocols | `craft/adversarial-evidence-review.md` §HX/LX/SX | — |
| Adversarial Evidence Review | LX-class limited-survival failure | Should-Fix | Survives some protocols; not all | `craft/adversarial-evidence-review.md` §HX/LX/SX | — |
| Adversarial Evidence Review | SX-class stable-claim flag | Could-Fix | Survives all protocols; flag for documentation | `craft/adversarial-evidence-review.md` §HX/LX/SX | — |
| Field Reconnaissance | Counterevidence surfaced post-Field-Recon contradicting C0 | Must-Fix | Direct contradiction of central claim | `craft/research-field-recon.md` §Output | — |
| Field Reconnaissance | Counterevidence surfaced post-Field-Recon weakening subclaim | Should-Fix | Subclaim weakened, central claim stands | `craft/research-field-recon.md` §Output | — |
| Field Reconnaissance | Literature-gap flag (no counterevidence found despite expected adversarial pressure) | Could-Fix | Documents the search; no actionable finding | `craft/research-field-recon.md` §Output | — |
| Citation Verifier | Ghost citation (CV-class verdict: source does not exist) | Must-Fix | Always | `craft/research-citation-verifier.md` §Verdict tiers | — |
| Citation Verifier | Misquoted / misattributed citation | Should-Fix | Source exists but quote/attribution inaccurate | `craft/research-citation-verifier.md` §Verdict tiers | — |
| Citation Verifier | Stale or unverifiable citation | Could-Fix | Source unreachable but no evidence of fabrication | `craft/research-citation-verifier.md` §Verdict tiers | — |

#### Specialized craft audits

| Audit | Audit-internal signal | Synthesis severity | Context modifier | Source | Override |
|---|---|---|---|---|---|
| Character Architecture | Hard gate (e.g., Sexy Lamp test fails for major character) | Must-Fix | Character central to plot | `craft/character-architecture.md` §Hard Gates | — |
| Character Architecture | Pattern flag (puppet moments across ≥2 scenes) | Should-Fix | Pattern-level | `craft/character-architecture.md` §Named flags | — |
| Character Architecture | Spot flag (isolated puppet moment) | Could-Fix | Isolated | `craft/character-architecture.md` §Named flags | — |
| Emotional Craft | Unearned-catharsis hard gate (climax-load scene) | Must-Fix | Climax-load scene (third act emotional crest) | `craft/emotional-craft.md` §Hard Gates | — |
| Emotional Craft | Forced-affect / sentiment-tracking flag | Should-Fix | Pattern across ≥2 scenes | `craft/emotional-craft.md` §Named flags | — |
| Emotional Craft | Local emotional-precision flag | Could-Fix | Isolated | `craft/emotional-craft.md` §Named flags | — |
| Literary Craft Deep Dive | Must-Fix flag (ending-level dimension failure or contract-damaging sustained pattern) | Must-Fix | Ending-level OR sustained-and-contract-damaging | `craft/literary-craft.md` §Named flags severity | — |
| Literary Craft Deep Dive | Should-Fix flag (recurring across multiple scenes; non-ending) | Should-Fix | Pattern-level | `craft/literary-craft.md` §Named flags severity | — |
| Literary Craft Deep Dive | Could-Fix flag (isolated; over-recommend-expansion guard applies) | Could-Fix | Isolated; check protected-elements list before recommending expansion | `craft/literary-craft.md` §Named flags severity | Refines default (protected-elements guard) |
| Force Architecture | Hard gate (inert-force or consequence-collapse in named action sequence) | Must-Fix | Named action sequence | `craft/force-architecture.md` §Hard Gates | — |
| Force Architecture | Pattern flag (inert force across ≥2 sequences) | Should-Fix | Pattern-level | `craft/force-architecture.md` §Named flags | — |
| Force Architecture | Spot flag | Could-Fix | Isolated | `craft/force-architecture.md` §Named flags | — |
| Series Continuity | Orphan-reference / consequence-reset hard gate (cross-volume thread amnesia or silent retcon) | Must-Fix | Silent retcon at explicit-canon layer; consequence-level violation | `craft/series-continuity.md` §Severity guides | — |
| Series Continuity | Forward-load drift (mid-series hope failure or unresolved carry-forward) | Should-Fix | Pattern-level cross-volume drift | `craft/series-continuity.md` §Severity guides | — |
| Series Continuity | Detail-level state inconsistency (minor facts) | Could-Fix | Isolated; non-load-bearing | `craft/series-continuity.md` §Severity guides | — |
| Series & Composite Novel | Standalone-function failure (volume cannot be read solo per stated contract) | Must-Fix | Series-with-standalone-promise contract | `craft/series-composite-novel.md` §Hard Gates | — |
| Series & Composite Novel | Hope-calibration / distance-management flag | Should-Fix | Pattern-level | `craft/series-composite-novel.md` §Named flags | — |
| Shelf Positioning | Contract Violation flag | Must-Fix | Stated genre / shelf contract violated | `craft/shelf-positioning.md` §Five Tests | — |
| Shelf Positioning | Straddling Penalty / Discoverability Gap | Should-Fix | Affects market positioning, not contract | `craft/shelf-positioning.md` §Five Tests | — |
| Shelf Positioning | Signal-Structure Mismatch (minor) | Could-Fix | Isolated signal | `craft/shelf-positioning.md` §Five Tests | — |
| Short Fiction | Single-effect design hard gate | Must-Fix | Compression / ending-resonance failure in flash or short story | `craft/short-fiction.md` §Hard Gates | — |
| Short Fiction | Pattern flag (compression failure) | Should-Fix | Pattern-level | `craft/short-fiction.md` §Named flags | — |

#### Genre audits

| Audit | Audit-internal signal | Synthesis severity | Context modifier | Source | Override |
|---|---|---|---|---|---|
| Comedy & Satire | Landing-rate hard gate (<30% jokes land per audit count) | Must-Fix | Comedy contract genre | `genre/comedy-satire.md` §Hard Gates | — |
| Comedy & Satire | Tonal-inconsistency flag | Should-Fix | Pattern across ≥2 scenes | `genre/comedy-satire.md` §Named flags | — |
| Historical Fiction | Period-authenticity hard gate (anachronism load-bearing on plot) | Must-Fix | Anachronism affects plot logic | `genre/historical-fiction.md` §Hard Gates | — |
| Historical Fiction | Research-integration flag | Should-Fix | Pattern-level | `genre/historical-fiction.md` §Named flags | — |
| Memoir / Creative NF | Truth-craft hard gate (composite character or reconstructed dialogue undisclosed) | Must-Fix | Disclosure failure | `genre/memoir-creative-nonfiction.md` §Hard Gates | — |
| Memoir / Creative NF | Narrator-reliability / ethical-obligation flag | Should-Fix | Pattern-level | `genre/memoir-creative-nonfiction.md` §Named flags | — |
| Narrative Nonfiction | Source-integration / fact-anchor hard gate | Must-Fix | Load-bearing claim unsourced | `genre/narrative-nonfiction.md` §Hard Gates | — |
| Narrative Nonfiction | Pacing / scene-construction flag | Should-Fix | Pattern-level | `genre/narrative-nonfiction.md` §Named flags | — |
| Fan Fiction Conversion | IP-scaffolding hard gate (worldbuilding gap blocks reader independence) | Must-Fix | Manuscript depends on assumed worldbuilding | `genre/fan-fiction-conversion.md` §Hard Gates | — |
| Fan Fiction Conversion | Character-independence flag | Should-Fix | Pattern-level | `genre/fan-fiction-conversion.md` §Named flags | — |
| SFF Worldbuilding Integration | Hard gate (worldbuilding non-load-bearing across ≥3 dimensions) | Must-Fix | Worldbuilding cosmetic, not narrative | `genre/sff-worldbuilding.md` §Hard Gates | — |
| SFF Worldbuilding Integration | Pattern flag | Should-Fix | Pattern across multiple dimensions | `genre/sff-worldbuilding.md` §Named flags | — |
| Horror Craft Integration | Hard gate (inert-dread across ≥3 dimensions OR ending-load horror collapse) | Must-Fix | Horror apparatus delivers content but not pressure | `genre/horror-craft.md` §Hard Gates | — |
| Horror Craft Integration | Pattern flag (dread-accumulation / legibility failure) | Should-Fix | Pattern across 2 dimensions | `genre/horror-craft.md` §Named flags | — |
| Horror Craft Integration | Spot flag | Could-Fix | Isolated | `genre/horror-craft.md` §Named flags | — |
| Supernatural Horror | Any of 10 hard gates fires | Must-Fix | Belief-threshold / wrongness / aftermath chain failure | `genre/supernatural-horror.md` §10 Hard Gates | — |
| Supernatural Horror | Pattern flag (BT/WO/HP/RL/MS/IE/RR family) | Should-Fix | Pattern-level | `genre/supernatural-horror.md` §Named flags | — |
| Grimdark / Dark Fantasy | Any of 9 hard gates fires (e.g., empathy bankruptcy, beautiful rot) | Must-Fix | Distinguish Framework = Inert | `genre/grimdark.md` §9 Hard Gates | — |
| Grimdark / Dark Fantasy | Pattern flag (MA/VE/PA/CC/IB/CP/HD family) | Should-Fix | Pattern-level | `genre/grimdark.md` §Named flags | — |
| Mystery / Thriller Architecture | Any of 10 hard gates fires (fair-play violation, clue-economy collapse) | Must-Fix | Mystery / thriller contract | `genre/mystery-thriller-architecture.md` §10 Hard Gates | — |
| Mystery / Thriller Architecture | Pattern flag (informational drift) | Should-Fix | Pattern-level | `genre/mystery-thriller-architecture.md` §Named flags | — |

#### Tag audits

| Audit | Audit-internal signal | Synthesis severity | Context modifier | Source | Override |
|---|---|---|---|---|---|
| Consent Complexity | Exploitation-vs-Exploration verdict = Exploitation (unmarked altered-state, scope-creep without interrogation, violation reframed without handling) | Must-Fix | Always | `tag/consent-complexity.md` §Exploitation vs Exploration | — |
| Consent Complexity | Authentic-vs-installed-desire HIGH (consent-as-conditioning unmarked) | Must-Fix | Power-dynamic / conditioning context | `tag/consent-complexity.md` §Flag families | Refines default per Phase 3 evidence |
| Consent Complexity | Pattern flag (boundary-tracking gap; not Exploitation) | Should-Fix | Pattern-level | `tag/consent-complexity.md` §Named flags | — |
| Consent Complexity | Spot flag (isolated boundary blur) | Could-Fix | Isolated | `tag/consent-complexity.md` §Named flags | — |
| Erotic Content | Any of 4 hard gates fires (e.g., consent calculus failure in load-bearing scene) | Must-Fix | Always | `tag/erotic-content.md` §4 Hard Gates | — |
| Erotic Content | Pattern flag (escalation-vs-repetition / static heat / decorative kink) | Should-Fix | Pattern across ≥2 intimate scenes | `tag/erotic-content.md` §8 Flags | — |
| Erotic Content | Spot flag | Could-Fix | Isolated | `tag/erotic-content.md` §8 Flags | — |
| Queer Romance / Erotica | Pronoun-clarity hard gate (clarity failure in load-bearing intimate scene) | Must-Fix | Same-gender intimate scene | `tag/queer-romance-erotica.md` §Hard Gates | — |
| Queer Romance / Erotica | Trope-navigation flag (joy / struggle calibration off) | Should-Fix | Pattern-level | `tag/queer-romance-erotica.md` §Named flags | — |
| Cozy Tag | Safety-envelope hard gate (cozy contract violated by retained menace at climax) | Must-Fix | Cozy contract | `tag/cozy-tag.md` §Hard Gates | — |
| Cozy Tag | Belonging-engine / recovery-rhythm flag | Should-Fix | Pattern-level | `tag/cozy-tag.md` §Named flags | — |
| Philosophical Tag | Counterposition-strength hard gate (no live counterposition for central question) | Must-Fix | Philosophical contract | `tag/philosophical-tag.md` §Hard Gates | — |
| Philosophical Tag | Question-architecture / dramatic-embodiment flag | Should-Fix | Pattern-level | `tag/philosophical-tag.md` §Named flags | — |

#### Default mapping (fallback for un-enumerated audits)

Audits not enumerated above default to the canonical rule's column-2 mapping (`run-synthesis.md §Step 2`):

- Audit-internal Must-Fix floor → Synthesis Must-Fix
- Audit-internal hard gate → Synthesis Must-Fix
- Audit-internal HIGH / Alert → Synthesis Must-Fix or Should-Fix per audit context (model judgment)
- Audit-internal MEDIUM / Flag → Synthesis Should-Fix
- Audit-internal LOW / Note → Synthesis Could-Fix

Future audit additions should add a §4e row at registration time. Audits with UNPROVEN-status hard gates (per Phase 3 Tag-audit inventory) fall under the default mapping until per-audit refinement lands.

#### Notes on table maintenance

- **Per-audit narrative explanations live in the audit reference files**, not in §4e. Each row references the source file's relevant subsection so the model can load context as needed.
- **The table refines, it does not contradict.** Per-audit entries that diverge from the canonical default carry an Override column note. If the table is silent on a signal class for an enumerated audit, fall back to the canonical default for that class.
- **CR-8 closure cases.** The named CR-8 closure cases — Compression Must-Fix floor, Reception Risk Alert (and coercion-marked Alert), Banister HIGH — appear explicitly above with their context modifiers and synthesis-severity mappings.

### §4f. Audit Tier Precedence Rule (highest obligation wins)

When the same audit is surfaced through multiple paths — most often router-triggered (§4a) **and** finding-triggered (§4b), but also via two distinct finding-triggers in §4b — the **highest obligation tier wins**. The audit runs at the higher tier; lower-tier triggers do not produce additional invocations.

**Tier ordering** (per §4c definitions):

```
Hard Prerequisite  >  Pre-DE Prerequisite  >  Auto-run  >  Auto-recommend before synthesis  >  Auto-recommend  >  Recommend
```

If two paths produce the same audit at different tiers, the audit runs at the highest tier among those paths. The Audit Invocation Log records the resolved tier and notes both source paths in the rationale column (e.g., `Reception Risk | router=Auto-recommend before synthesis + finding=Recommend → resolved Auto-recommend before synthesis`).

**Hard Prerequisite ordering note (Phase 6 Wave 3 / CR-4).** Hard Prerequisite and Pre-DE Prerequisite tiers added in Phase 6 Wave 3 to support Field Reconnaissance and Citation Verifier prerequisite policy on argument-shaped runs. They sit above Auto-run in the ordering because they are *pass* dependencies (must complete before Tier 2 evaluative passes can begin) rather than *synthesis* dependencies. A finding-trigger at Auto-recommend before synthesis cannot promote an audit to Hard Prerequisite — that tier is reserved for router-triggered prerequisite policy on argument-shaped runs with high-stakes signal. The priority queue (§4d) does not reorder Hard Prerequisite / Pre-DE Prerequisite audits within a pass surface — those audits run before passes, so they have no in-pass surface position to order.

**Edge cases:**

1. **Router Auto-run + finding-trigger Recommend.** Audit runs as Auto-run. The router obligation is dispositive; the finding-trigger does not create a duplicate invocation or weaken the tier. (Cross-reference §4a Auto-run policy.)
2. **Router Auto-recommend + finding-trigger Auto-recommend before synthesis.** Audit runs at Auto-recommend before synthesis. The finding-trigger promoted the tier. (Cross-reference §4b finding-trigger policy.)
3. **Two finding-triggers, both Auto-recommend before synthesis.** Audit runs once at Auto-recommend before synthesis (deduplication). Both triggers are recorded in the Audit Invocation Log rationale column; the audit is not invoked twice.
4. **Two finding-triggers, both Recommend, multiple passes fire it.** Audit runs once at Recommend tier (count of triggers does not promote tier; only the highest tier among triggers does). Multiple-pass evidence enters the recommendation framing presented to the user, not the tier.
5. **Audit declined by user at Recommend tier; later finding-trigger fires at Auto-recommend before synthesis.** The new tier rationale changes the obligation. **Re-prompt the user** with the new tier rationale (the prior decline was based on a weaker obligation; the user has not yet had the chance to consider the higher-tier framing). If the user declines again, the run records an explicit blind-spot disclosure per §4c Auto-recommend before synthesis policy.
6. **Audit declined under Auto-recommend before synthesis tier; later finding-trigger fires.** Blind-spot disclosure already logged; the new finding-trigger does not re-prompt. The blind-spot disclosure carries forward to synthesis as the canonical confidence limiter for this audit-class.
7. **Audit-tier precedence interacts with the priority queue (§4d).** Precedence determines tier; the priority queue determines surface order within a pass. Tier resolution happens before queue ordering.
8. **Hard Prerequisite declined by user (Phase 6 Wave 3).** When a Hard Prerequisite audit (router-triggered for an argument-shaped run with high-stakes signal) is declined, the resolver MUST present a fork: (a) terminate the run with a "cannot proceed without literature-counterevidence surfacing for high-stakes argument-shaped runs" advisory, or (b) downgrade to Auto-recommend before synthesis with a body-of-letter blind-spot disclosure that names "literature-counterevidence not surveyed" as a confidence limit at synthesis. The user chooses (a) or (b); the resolver does not silently downgrade. If the user re-affirms (b), the §4c Auto-recommend before synthesis decline path applies thereafter.
9. **Pre-DE Prerequisite declined by user (Phase 6 Wave 3).** When the Pre-DE Prerequisite Citation Verifier is declined for a high-stakes argument-shaped run, the same fork applies: terminate or downgrade-with-disclosure. Citation Verifier declines must additionally name "citation provenance not verified — Ghost Citation / Quote Drift / Paraphrase Inflation risks not surveyed" as the confidence limit at synthesis.

**Cross-references:** §4a (router-triggered audits use this rule when also finding-triggered); §4b (finding-triggered audits use this rule when also router-triggered or fired by multiple passes); §4c (tier definitions provide the ordering); §4d (priority queue applies to surface order *after* tier resolution).

**Validator follow-up (Phase 7):** A `validate.sh audit-tier-precedence <audit_invocation_log>` script could verify that every audit appears at its highest-tier-applied. Deferred to Phase 7; the rule itself is enforceable via documented contract today.

---

## §5. Interaction with Genre Modules

Genre modules modify pass behavior (thresholds, tracking, flags). The audit resolver is separate from — and complementary to — genre module loading.

- **Genre modules** load at intake and stay active for all passes. They modify *how* passes run.
- **Genre audits** (from §4a/§4b) are deep-dive analyses that run *after* passes. They test whether the genre apparatus is doing narrative work.

A manuscript can have a genre module loaded (e.g., Horror) without running the corresponding audit (Horror Craft Integration). The module ensures passes track the right things; the audit provides the focused integration analysis. The audit resolver recommends the audit; it doesn't force it.

---

## §6. Interaction with `/audit` Command

The `/audit` command remains a direct-access shortcut. A user who types `/audit force-architecture` gets the Force Architecture audit regardless of what the resolver would recommend.

The resolver handles *automatic* surfacing during diagnostic runs. The `/audit` command handles *deliberate* requests. Both draw from the same audit catalog in `specialized-audits/SKILL.md`.

The resolver does not gate or limit `/audit`. If a user requests an audit that the resolver wouldn't have surfaced, run it without complaint.

---

*This file is a runtime reference. For design rationale, see the v0.5 UX Overhaul spec.*
