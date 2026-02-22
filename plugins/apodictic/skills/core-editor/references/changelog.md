# APODICTIC Development Editor Changelog

All notable changes to the APODICTIC Development Editor (APDE) framework will be tracked in this file.

This changelog started at `v0.4.4.1` on **2026-02-13**.  
Historical backfill entries for `v0.4.4` and `v0.4.3` were added the same day from local file history and release notes.

## v1.0.0 - 2026-02-22

### 1.0 Release

v0.5 UX overhaul is complete: query-driven pass architecture, intake router, scene-level handoff, command alias model, overview dashboard, route explorer. The plugin is navigable by newcomers. Tagging 1.0.

### Changed — Version Hygiene
- Stripped decorative version numbers from ROADMAP.md, README.md, core-editor SKILL.md body header, AUDIT_SELECTION_MATRIX.md, route explorer HTML.
- Removed hardcoded version strings from output template footers (diagnostic-state-template.md, contract-template.md, reverse-outline-template.md, pass-11.md, pre-writing-pathway SKILL.md).
- Canonical version now lives exclusively in `plugin.json` + 4 SKILL.md frontmatter fields.
- Added `scripts/bump-version.sh` to update all 5 locations from a single command.

### Fixed — Audit Resolver Names
- Reconciled 3 string mismatches: "Erotic Content tag" → "Erotic Content", "Character Architecture (deep)" → "Character Architecture", "Banister" → "Banister (Epistemic Humility)".

## v0.4.19 - 2026-02-22

### Added — v0.5 Integration Files (Runtime)
- Added `references/pass-dependencies.md` to core-editor references and wired it into pass resolution flow.
- Added split router files: `references/intake-router-runtime.md` (runtime) and `references/intake-router-design.md` (design notes).
- Added `references/handoff-protocol.md` and integrated scene-level handoff mode transitions.
- Added `overview-dashboard.html` to plugin root.

### Changed — Core Runtime Wiring
- `/start` now runs a mode-aware resume gate before router Q1. If `Diagnostic_State.md` indicates execution mode, it presents: Check the fix / Keep working / Start fresh.
- `core-editor/SKILL.md` now uses concern-driven pass resolution (`pass-dependencies.md`) instead of fixed tier framing.
- `run-core.md` now explicitly resolves concern -> minimum pass set -> dependencies, with baseline floor fallback and optional scene-level handoff behavior.
- `run-full.md` reframed from trigger-gated language to expansion-policy language aligned with resolver auto-escalation.
- `diagnostic-state-template.md` now includes `Mode` and append-only `Handoff History` schema.

### Changed — Command Alias Model
- `/develop-edit` is now defined as a `/start` shortcut with prefilled `artifact=full_draft`, `goal=repair`.
- `/pre-writing` is now defined as a `/start` shortcut with prefilled `artifact=idea`, `goal=draft`.
- `/diagnose` is now defined as targeted resolver routing (`goal=repair`, concern-required).
- `pre-writing-pathway/SKILL.md` now accepts router output as prefilled intake context and skips redundant prompts.

### Changed — Handoff Semantics
- `handoff-protocol.md` language updated from "unload skill" to "suspend/re-enable core-editor constraints" to match actual behavior-contract capabilities.

### Version Reconciliation
- Updated plugin manifest version to `0.4.19` (`.claude-plugin/plugin.json`).
- Updated `core-editor/SKILL.md` version markers to `0.4.19`.
- Updated `README.md` framework version to `v0.4.19`.
- Updated roadmap header version to `v0.4.19`.

## v0.4.17 - 2026-02-21

### Fixed — Audit Discovery and Invocation (Codex review)
- **`/audit` command** expanded from 17 to 28 entries. Now lists all current audits organized by category: Universal (3), Craft (15), Genre (4), Tag (3), Plot (1 cross-reference). Previously missing: Stakes System, Decision Pressure, Force Architecture, Literary Craft, Horror Craft, Mystery/Thriller Architecture, SFF Worldbuilding, Cozy Tag, Philosophical Tag, Erotic Content.
- **`/develop-edit` workflow order** corrected: audit integration now happens after core passes and before synthesis (step 4), matching `run-core.md` §Audit Integration Point. Previously synthesis preceded audit evaluation.
- **`specialized-audits/SKILL.md` catalog** updated: Stakes System, Decision Pressure, and Scene Turn now listed as Universal Audits in both the Available Audits table and Reference Files section. Previously missing from both.
- **Intake router** (`intake-router.md`): added "Run a focused audit on a specific concern" option (E) for full_draft artifact, with corresponding route map entry. Previously no audit route was reachable for complete drafts via `/start`.
- **README.md** counts updated: "23 specialized audits, 5 tag audits" (was "18 deep-dive audits, 2 tag audits"); "28 available audits" (was "17"); version line updated.

### Added — Audit Invocation Log
- New artifact in `run-core.md` §Audit Integration Point: `[Project]_Audit_Invocation_Log_[runlabel].md`. Tracks every audit considered during a run with source (universal/contract/finding-driven), status (run/skipped/deferred), and reason. Referenced in `/develop-edit` step 4.

### Changed — Legacy Module Index
- **`module-index.md`** marked as legacy reference with deprecation header. File paths reference pre-plugin directory structure and do not match current package. Users directed to `AUDIT_SELECTION_MATRIX.md` and `specialized-audits/SKILL.md` for current routing and file paths.
- **`core-editor/SKILL.md`** reference to `module-index.md` annotated as legacy with redirect to current sources.

### Deferred
- **P2 #5 (Token overhead / router split):** Splitting `intake-router.md` into a short runtime decision table and a separate design document would reduce early-turn context consumption. Deferred to future version — requires updating all references and the `/start` command.

## v0.4.16 - 2026-02-21

### Added — Synthesized Audits and Integration Pipeline
- **Stakes System audit** (craft/stakes-system.md + craft/stakes-system-level-setting.md). Three-model synthesis (Opus46, Codex53, Gemini). 22 named diagnostic flags across 6 channels (STX, PC, IM, EG, MP, CL). 4 tracking artifacts. Four-tier distinguish framework. Production audit + level-setting companion.
- **Decision Pressure audit** (craft/decision-pressure.md + craft/decision-pressure-level-setting.md). Three-model synthesis (Opus46, Codex53, Gemini). 23 named diagnostic flags across 7 channels (AV, CS, IS, EC, RF, TR, PV). 6 tracking artifacts. Four-tier distinguish framework. Production audit + level-setting companion.
- **AUDIT_SELECTION_MATRIX.md** — comprehensive routing guide covering all 11 sections: fast entry router, core/full DE passes, Pass 11, craft audits, structural modules, genre audits, tag audits, research modes, recommended bundles, and minimal rule of thumb.

### Added — Audit Integration into Pass Sequence
- **Contract-driven audit activation** at intake (run-core.md): 17-row table mapping genre/mode signals to recommended audits.
- **Finding-driven audit triggers** across 7 passes: Pass 1 (belief failures → DP, emotional flatness → EC, low stakes → SS, action immersion → FA), Pass 2 (causal gaps → Scene Turn, nonfiction situation overwhelming → Franklin), Pass 3 (intensity plateau → SS, pacing stalls → Scene Turn), Pass 4 (triple stasis → EC, intensity plateau → SS, certainty static → Horror/Mystery-Thriller), Pass 5 (motivation discontinuity → DP, agency collapse → SS, under-specified wants → Character Architecture), Pass 6 (single/zero-function → Scene Turn, setup debt → SS), Pass 8 (knowledge errors → DP IS channel, information timing → DP + Reveal Economy).
- **Audit Integration Point** in run-core.md: 4-step protocol for compiling triggers, comparing against contract, running audits, feeding into synthesis.
- **Supplementary Audit Integration Protocol** in run-full.md: 5 rules covering timing, synthesis integration, dashboard feeds, cross-audit coordination, firewall compliance.

### Changed — Synthesis and Output Capacity
- **Processing Protocol** expanded from 5 to 6 steps. New Step 2: Audit Finding Consolidation with 5 rules (map to pass findings, cluster by problem not audit, preserve audit-unique findings, count consolidated problems not flags, carry artifacts to appendices).
- **Appendix A** spec expanded to include audit companion files and tracking artifacts.
- **Full DE letter spec** updated with supplementary audit integration guidance and cross-audit overlap rule.
- **Dashboard** expanded from 8 to 10 components: Component 9 (Decision Pressure Map — option visibility, tradeoff cost, pivot integrity), Component 10 (Force/Action Tracking — conditional on Force Architecture audit). Assembly rules updated for conditional components and expanded length target.

### Changed — Supplementary Audits Section
- **run-full.md** Supplementary Audits section replaced (~20-line stub → ~120-line comprehensive section): Universal Audits (Stakes System, Decision Pressure, Scene Turn, Emotional Craft) with pass connections and pairing logic; Genre/Mode Audits with activation table; Tag Audits table; Integration Protocol.

## v0.4.15 - 2026-02-21 (First Alpha Release)

### Changed — Full Rebrand
- **Package renamed** from `development-editor` to `apodictic`. Top-level directory, plugin.json name, and .plugin filename all updated.
- **Core skill renamed** from `core-development-editor` to `core-editor`. All command files, SKILL.md frontmatter, and internal references updated.
- **Version scheme changed** from 4.x to 0.4.x to reflect pre-1.0 status. All version references across all files updated.
- **Branding normalized** to "APODICTIC Development Editor" throughout. Legacy "APDE" shorthand retained in output template footers.

### Added — Full DE Output Specifications
- **Output specs added** for all Full DE passes (3, 4, 6, 7, 9, 10). Each pass now specifies its output filename and artifact contents, matching the Core DE pass format.
- **Output naming convention** in output-policy.md updated to include all Full DE filenames plus Pass 11 and Full DE Synthesis.

### Added — Inline Genre Calibration
- **Mystery / Investigation** inline calibration section added to core-framework.md — reader expectations, subgenre false-positive warnings, contract additions, priority pass (Pass 8), pass modifications, key diagnostic flags, false-positive warnings.
- **Thriller / Suspense** inline calibration section added to core-framework.md — same depth. All six genres now have inline calibration sections.

### Validated
- Dry run complete: full 11-pass DE executed on a novella-length manuscript. All passes produced output artifacts.
- Density re-audit passed all four §10 proportionality thresholds.
- Three §8 design decisions resolved (rejection memo scope, reference implementation, genre calibration coverage).

## v0.4.14.3 - 2026-02-20

### Added — Documentation and Policy
- **README.md:** Added "What This Plugin Does and Does Not Do" section — user-facing policy covering diagnostic scope, the Firewall, and explicit boundaries (no prose generation, no line editing, no content storage beyond session).
- **README.md:** Added "Intended Audience and Safety Boundaries" section — primary/secondary audience, content coverage statement (all published fiction genres analyzed on their own terms), and safety posture (analytical outputs only, no content generation).
- **CONTRIBUTING.md:** Added "Changelog Policy" section — entry format, framing rules, reframing table for public-facing language, and version bump guidance (patch/minor/major).
- **README.md version** updated to v0.4.14.3.
- Completes Publication Requirements §5 items: changelog policy, safety boundaries, and end-user policy text.

## v0.4.14.2 - 2026-02-20

### Added — SFF Subgenre Pass Recalibrations
- **genre-sff.md** expanded from 415 → 581 lines (+166 lines) with comprehensive subgenre pass recalibrations.
- **Master Calibration Matrix:** 10 subgenres × 8 modified passes showing ELEVATE/STANDARD/DEPRIORITIZE/RECALIBRATE for each combination. Tells the editor exactly how to adjust each pass for the manuscript's specific subgenre.
- **Per-Pass Recalibration Notes** for all 8 modified passes:
  - Pass 0: Hard SF `[SCIENCE CLAIM]` tagging, Epic Fantasy hard/soft/lore rule separation, New Weird rule-flag suppression, Portal Fantasy `[DISCOVERY]` tracking
  - Pass 1: Hard SF system-vs-vocabulary confusion distinction, Cyberpunk disorientation window (15%), Epic Fantasy stalling-vs-slowness, Grimdark interest-not-sympathy threshold (30%), Portal Fantasy synchronization tracking, Progression/LitRPG stat-block tolerance
  - Pass 4: Hard SF eureka tracking, Space Opera scale-wonder, Cyberpunk alienation axis, Epic Fantasy moral weight, New Weird estrangement, Solarpunk hope axis, Grimdark corruption axis, Portal Fantasy wonder resurfacing (2+ scenes after 50%), Progression/LitRPG flat progression affect
  - Pass 5: Hard SF frictionless expertise, Cyberpunk identity-cost augmentation, Urban Fantasy dual-identity strain, Grimdark costless edge, Portal Fantasy learning curve (2+ failures), Progression/LitRPG stat-growth-character-stasis
  - Pass 6: Hard SF lab bench scene, Epic Fantasy empty council, New Weird atmosphere tolerance
  - Pass 8: Hard SF textbook passage + stricter 50% threshold, Cyberpunk flat conspiracy, Epic Fantasy extended cadence (50%), Urban Fantasy spent masquerade, Portal Fantasy flat discovery, Progression/LitRPG incremental grind
  - Pass 9: Hard SF interchangeable tech, Cyberpunk aesthetic cyberpunk, New Weird pattern-not-statement, Solarpunk optimism without evidence, Grimdark decorative nihilism, Progression/LitRPG uncritical meritocracy
  - Pass 10: Hard SF zero-tolerance cost amnesia, Space Opera political-not-physics rules, Cyberpunk system rules, Epic Fantasy hard/soft/hybrid ledger, Urban Fantasy masquerade amnesia, New Weird dream-logic consistency, Progression/LitRPG zero-tolerance system inconsistency
- **Subgenre Deep-Dive Override Table:** 6 threshold overrides for SFF-DD1/DD2/DD3 across Progression/LitRPG, Hard SF, Epic Fantasy, New Weird, and Grimdark.
- **Cross-Reference section** linking to worldbuilding audit subgenre calibration for aligned expectations.

## v0.4.14.1 - 2026-02-20

### Changed — Genre Module Parity Hardening
- **All six genre modules updated to v0.4.14** with numeric thresholds, named deep-dive flags (Detection/Test/Threshold/Flag/Exception format), and mechanistic diagnostic checks. Changes target quantifiability and actionability, matching Romance's level of mechanical specificity.
- **genre-horror.md:**
  - Added Certainty-Intensity Sync Check (parallel to Romance's dual-track model) with alignment table and thresholds (certainty stasis >25%, premature collapse <40%, intensity plateau 3+ chapters)
  - Added Pass 3 thresholds: dread fatigue (3+ consecutive peak chapters), tension bleed (3+ consecutive low chapters), relief ratio (1 valley per 2-3 peaks)
  - Added 4 named deep-dive flags: HOR-DD1 Explanation Kills (>50% mystery resolved before final 20%), HOR-DD2 Numb Protagonist (3+ horror events without deterioration), HOR-DD3 Diminishing Returns (3+ same technique without variation), HOR-DD4 No Normalcy Baseline (horror in first 10% without baseline)
  - Added Dread Ladder diagnostic checks: stuck rung (3+ chapters), premature point-of-no-return (<40%), regression without purpose (2+ rung drop), repeated rungs (3+ without deepening)
  - Added Dread Indicators checklist (9 indicators, parallel to Romance's Chemistry Indicators) with told-not-shown threshold (3+ scenes relying on assertion)
- **genre-mystery.md:**
  - Added Pass 8 cadence and visibility thresholds: clue cadence (1 per 15%), information drought (20% stretch with zero clues), front-loading check (>60% clues in Act I), culprit visibility (minimum 3 scenes, at least 1 in first 40%), suspect pool size (3-6 optimal), red herring ratio (max 2:1), late clue deadline (no essential clues in final 10%), suspect suspicion shift (minimum 1 shift)
  - Added 4 named deep-dive flags: MYS-DD1 Parlor Scene Info Dump (>5% manuscript, <2 interruptions), MYS-DD2 Equal Opportunity Suspect (all suspects identical at 60%), MYS-DD3 Vanishing Investigation (3+ chapters without progress), MYS-DD4 Retroactive Incoherence (2+ scenes contradicting solution)
  - Added Fairness Score system (FAIR/BORDERLINE/UNFAIR granular assessment replacing binary pass/fail) with thresholds
- **genre-thriller.md:**
  - Added Pass 3 thresholds: flat middle (3+ chapters in Act II without escalation), premature climax (resolved before 75%), exhaustion pacing (4+ consecutive peak chapters), scene compression check, tension oscillation minimum (1 valley per 4 peaks)
  - Added Per-Act Resource Ledger (7 resource categories tracked across 5 story points) with depletion thresholds (minimum 2 categories degraded by Act II midpoint, 4+ depleted at dark moment)
  - Added formal Safety Island definition (4 criteria) with thresholds (>2 chapters, >15% manuscript, pre-climax lull)
  - Added 3 named deep-dive flags: THR-DD1 Teflon Protagonist (3+ confrontations without cost), THR-DD2 Convenience Engine (2+ unearned escapes), THR-DD3 Decaying Villain (peak threatening moment before 40%)
  - Added Escalation Ladder diagnostic checks: skipped rung, stuck rung (3+ chapters), missing first trap (by 25%), regression, escalation monotony (3+ same type)
- **genre-sff.md:**
  - Expanded from 5 to 10 pass modifications: added Pass 4 (wonder axis, power-cost emotional check with per-phase register table), Pass 5 (competence-cost inventory table, frictionless system threshold at 60%), Pass 8 (worldbuilding reveal cadence with late-rule threshold at 60%), Pass 9 (thematic integration check for speculative elements)
  - Added 3 named deep-dive flags: SFF-DD1 Magic Microwave (3+ identical-pattern uses), SFF-DD2 Worldbuilding Orphan (3+ weighted details without payoff), SFF-DD3 Escalation Treadmill (3+ threat-then-power-up cycles without lateral thinking)
  - Added Integration with Core Framework section listing all 10 modified passes and combination guidance
  - Added SF/F-specific reader experience flags (5 flags)
- **genre-literary.md:**
  - Added 4 named deep-dive flags: LIT-DD1 Theme-as-Lecture (Stated:Embodied ratio >2:1), LIT-DD2 Unearned Epiphany (<2 precursor scenes), LIT-DD3 Beautiful Emptiness (3+ high-craft passages without payoff), LIT-DD4 Quiet Evasion (2+ thematic questions unaddressed at ending)
  - Added Thematic Dual-Track Model (Theme-as-Content + Theme-as-Form) with alignment check table (parallel to Romance's emotional/physical dual-track)
  - Added Pass 9 thematic thresholds: theme drought (20% stretch with zero instances), front-loading (>60% heavy instances in first third), static theme (identical at 80% vs 20%), epiphany count (>2 investigate)
- **Author name updated** to "Joshua A. Miller, PhD" across README.md, plugin.json, CONTRIBUTING.md, and LICENSE.
- **README.md version** updated from v0.4.6.0 to v0.4.14.

## v0.4.14 - 2026-02-20

### Changed — Thin Orchestrator Refactor
- **Core SKILL.md reduced from 1,660 lines to 253 lines.** Rewritten as thin orchestrator containing only: firewall, operating tiers, workflow contract, pass architecture summary, output policy summary, delegation rules, genre module routing table, reference file routing table, QA guardrails.
- **Extracted four new reference files:**
  - `references/run-core.md` (~450 lines) — Intake protocol, Core DE passes (0/1/2/5/8), synthesis processing/presentation, deliverables, revision round protocol. Loaded every Core DE and Full DE run.
  - `references/run-full.md` (~170 lines) — Full DE passes (3/4/6/7/9/10), supplementary audits (Stakes System, Decision Pressure), Full DE deliverables, structural frameworks reference, certainty axis cues. Loaded only when Full DE tier triggers.
  - `references/output-policy.md` (~210 lines) — Author-facing language rules, output constraints, naming conventions, confidence calibration, epistemic humility, deep analysis triggers, severity honesty protocol, severity floor rules, editorial letter tone/voice, pass-level output protocol. Loaded before writing any output.
  - `references/character-architecture.md` (~110 lines) — Arc types, psychology engine, trauma physics, agency quotient, constraint quotient, voice distinctiveness, ensemble balance, genre tuning packs. Loaded when detailed character analysis needed.
- **Removed from core SKILL.md (delegated to existing reference files or companion skills):**
  - Genre calibration blocks (Literary Fiction, Horror, SF/F, Romance) — already exist as standalone reference files (`genre-literary.md`, `genre-horror.md`, `genre-sff.md`, `genre-romance.md`)
  - Specialized audit stubs (Interiority Preservation, Female Interiority, Series/Composite, Consent Complexity, Banister, Shelf & Positioning, Comedy & Satire, Historical Fiction, Queer Romance/Erotica, Fan Fiction Conversion, Tag Audits) — delegated to `specialized-audits` skill
  - Plot Architecture section (48 spines, logic gates, diagnostic quick reference) — delegated to `plot-architecture` skill
  - Plot Selection & Coaching, Fantasy & Series Architecture stubs — delegated to `plot-architecture` skill
  - Research Modes — delegated to `specialized-audits` skill
  - Pass 11 full internals — pointer to `references/pass-11.md`
  - Reference appendices (Structural Frameworks, Certainty Axis Cues) — moved to `references/run-full.md`
- **Patched `/start` command:** No longer preloads all three companion skills. Loads `core-editor` only; loads target skill after route decision.
- **Patched `/pre-writing` command:** No longer preloads `core-editor` and `plot-architecture` at session start. Loads `pre-writing-pathway` only; loads `plot-architecture` at Phase 4; loads core only on re-entry.
- **Patched `/develop-edit` command:** Added lazy loading instructions for `references/run-core.md`, genre modules, `references/output-policy.md`, and `references/run-full.md`. Fixed cap drift: "surgery list (max 25 items)" → "revision checklist (max 10 items)" to match current output policy.
- **Version bumped to 4.14.**

### Context Load Impact
- `/start` → loads ~253 lines (was ~1,660 + two companion skills)
- `/develop-edit` → loads ~253 + ~450 (run-core) = ~700 lines (was ~1,660)
- Full DE trigger → adds ~170 lines (run-full) on demand
- Genre modules load only when manuscript genre identified
- Specialized audits, plot architecture, pre-writing pathway load only when routed

## v0.4.13 - 2026-02-20

### Changed — Genre-to-Tag Restructure (Track 3)
- **Split Romance/Erotic genre module into Romance (genre) + Erotic Content (tag).** The combined `genre-romance-erotic.md` (423 lines) has been replaced by two purpose-built files:
  - `genre-romance.md` (new, ~320 lines) — Romance genre module. Keeps: relationship engine, structural obstacles, chemistry indicators, escalation stages, trust-rupture-repair cycle, pass modifications (Passes 1, 2, 4, 5, 6, 8), 15 genre-specific flags (including Magic Wand, Idiot Ball, Body Betrayal), subgenre calibration (Contemporary, Historical, Paranormal, Dark Romance, Slow Burn, Poly/WhyChoose, Romantasy, Romantic Suspense). Removed: heat level contract, consent calculus, kink integration, erotic-specific flags, escalation vs. repetition audit — all moved to Erotic Content tag.
  - `erotic-content.md` (new tag audit, ~400 lines) — Cross-genre Erotic Content tag. Applies to any manuscript with significant intimate content regardless of parent genre. Five diagnostic dimensions (Scene Function/Load-Bearing Test, Psychological Presence, Escalation Architecture, Consequence Persistence, Consent Architecture). Eight named flags (EC-1 Decorative Kink, EC-2 Mechanical Intimacy, EC-3 Skipped Aftermath, EC-4 Static Heat, EC-5 Intimacy as Pause, EC-6 Pattern Repetition, EC-7 Technique Saturation, EC-8 Vanishing Interiority). Consent Calculus with logic gates (migrated from old Pass 10 section). Escalation vs. Repetition Audit (migrated from old module). Seven mode calibrations with named failure modes (The Treadmill, The Manual, The Safety Net, The Detour, The Intermission, The Costume Party, The Catalog). Four severity hard gates. Four-class distinguish framework. Output template. Firewall compliance.
- **Updated companion audit integration references:**
  - `consent-complexity.md` → v0.4.13: Updated integration section to point to Erotic Content tag + Romance genre module (was: "Romance/Erotic Module")
  - `queer-romance-erotica.md` → v0.4.13: Updated integration section to point to Erotic Content tag + Romance genre module (was: "Romance/Erotic Module")
  - `interiority-preservation.md` → Expanded from intimate-scene-only stub to cross-genre high-intensity stub with genre-specific application pointers (Force Architecture, Erotic Content tag, Horror Craft, Romance genre module)
- **Updated core-editor SKILL.md:** "Genre Calibration: Romance / Erotic" → "Genre Calibration: Romance" with Erotic Content tag activation note. Updated reference path from `genre-romance-erotic.md` to `genre-romance.md`. Updated interiority preservation cross-reference. Renamed spine family "Relationship/Erotic" → "Relationship/Intimacy."
- **Updated specialized-audits SKILL.md → v0.4.13:** Added Erotic Content tag to Tag Audits table with trigger words. Added `references/tag/erotic-content.md` to reference paths. Updated Consent Complexity and Queer Romance/Erotica reference descriptions.
- **Removed:** `genre-romance-erotic.md` (old combined module), legacy flat-file duplicates of consent-complexity.md, queer-romance-erotica.md, interiority-preservation.md from references root.

### Edge Case Verification
- Pure erotica (no romance arc): Erotic Content tag standalone ✓
- Romantasy (romance + epic fantasy): Romance module + optional Erotic Content tag ✓
- Noir with sex scenes (thriller + erotic content): Erotic Content tag standalone ✓
- Literary fiction with explicit content: Erotic Content tag standalone ✓
- Sweet romance (heat level 1-2): Romance module standalone ✓

## v0.4.12 - 2026-02-20

### Added
- **Force Architecture audit** (craft/force-architecture.md, 622 lines, three-model synthesis). Cross-genre audit evaluating whether physical conflict functions as a coherent narrative engine or produces inert spectacle. Core concept: "inert force" — action choreography present, reader not changed by it. Anchor insight: force that escalates in intensity but not in consequence and meaning conversion is structurally parallel to ornamental prose, inert dread, and informational drift. Six integration dimensions (LG Legibility, TC Tactical Causality, CR Competence-Risk Tension, CP Cost Persistence, ES Escalation Kind-Shift, MC Meaning Conversion) with Integrated/Partial/Detached ratings. Force centrality profile (low/medium/high burden) as pre-assessment calibration. 25 named diagnostic flags: LG-1 White-Room Melee, LG-2 Teleport Bodies, LG-3 Actor Chain Blur, LG-4 Sensory Flatline, LG-5 Disembodied Combatant; TC-1 And-Then Chain, TC-2 Ruleless Advantage, TC-3 Frictionless Execution; CR-1 Godmode Drift, CR-2 Threat Collapse, CR-3 Plot Armor Leak, CR-4 Flawless Execution; CP-1 Rubber-Band Injury, CP-2 Resource Theater, CP-3 Trauma Erasure, CP-4 Collateral Erasure, CP-5 Relationship Reset; ES-1 Scale-Only Escalation, ES-2 Combat Monotone, ES-3 Escalation Cliff, ES-4 Pacing-Significance Inversion; MC-1 Violence Shortcut, MC-2 Cool-Kill Drift, MC-3 Aftermath Null, MC-4 Conversion Failure. Four tracking artifacts: Force Event Ledger with Abstraction Level column (required), Consequence Continuity Ledger with Behavioral Evidence column (required), Escalation Ladder Map (required), Legibility Snapshot Grid (recommended). Pattern interpretation protocol with 10 diagnostic combinations, Special Caution Zones (Horror Craft overlap, Mystery/Thriller overlap, Character Architecture downstream, Emotional Craft upstream, AI-Prose susceptibility). Nine severity hard gates. Seven distinguish tests (Reconstructability, Constraint Consistency, Risk Reality, Persistence, Kind-Shift, Conversion, Cognitive Anchor) with four-class decision matrix (Intentional and Successful, Intentional but Unstable, Ambiguous/Developmental, Accidental Failure). Eight mode calibrations with named failure modes: Map-Table Heroics (military/war), Stat-Sheet Spectacle (systems-driven progression), Perpetual Chase Blur (thriller), Shock Carousel (horror violence), Clean Hit Myth (crime/noir), Incident Theater (domestic violence drama), Aphoristic Carnage (literary violence), City-Scale Weightlessness (superhero/speculative). Explicit audit procedure (claim lock → build artifacts → rate channels → apply flags → synthesize). Output template. Firewall compliance. Stacks with Horror Craft, Mystery/Thriller Architecture, Emotional Craft, Character Architecture, AI-Prose Calibration, Literary Craft, Female Interiority; feeds Pass 11 synthesis.
- **Force Architecture level-setting brief** (craft/force-architecture-level-setting.md, 496 lines, three-model synthesis). Companion research brief grounding the audit in cognitive science, narrative theory, violence theory, and practitioner craft knowledge. Eight theoretical sections: SPECT (situation model construction under stress), event-indexing models (Zwaan/Langston/Graesser five-dimension tracking), event segmentation (Zacks boundary-marking), Sternberg's suspense architecture (suspense > surprise in force scenes), Clausewitz friction (plan-execution gap as cross-genre credibility bridge), the body problem (Disembodied Combatant, sensory hierarchy shifts, tachypsychia, auditory exclusion, experience-level differentiation, distance-difficulty scaling), Arendt/Scarry violence theory (violence/power distinction, bodily representation), Hayakawa abstraction ladder (compression vs. incoherence distinguish tool), consequence persistence (Stark coercive-control model, five-cost tracking). Full failure mode taxonomy (25 named patterns). Positive-case technique extraction across 8 modes: O'Brien truth-by-contradiction / Haldeman temporal estrangement / Cook chronicler distance (military), Dinniman environmental comedy-as-friction / Wight advancement-cost coupling (progression), Child preparation-as-suspense / Ludlum identity-through-combat (thriller), King domestic-space contamination / Jones cultural-weight violence (horror), Hammett consequence-networking / Ellroy institutional complicity (crime/noir), micro-escalation architecture / credibility asymmetry (domestic), McCarthy violence-as-epistemological-event / Morrison violence-as-historical-testimony / O'Connor revelatory violence (literary), power-scale clarity / collateral consequence architecture (superhero/speculative). Eight-mode calibration evidence with named failures and false positive risks. Distinguish problem analysis with seven operational tests, four outcome classes, and seven false-positive controls.

## v0.4.11 - 2026-02-20

### Added
- **Mystery/Thriller Architecture audit** (genre/mystery-thriller-architecture.md, 653 lines, three-model synthesis). Genre-specific audit evaluating whether mystery/thriller information architecture generates inference, urgency, and surprise-with-inevitability or merely assembles genre components. Core concept: "informational drift" — clues, suspects, reversals, and deadlines present but failing to generate hypothesis formation, prediction revision, felt urgency, or satisfying surprise. Anchor insight: information the reader possesses but isn't working with is structurally parallel to horror that doesn't produce dread and literary craft that doesn't do work. Six integration dimensions (IE Information Economy, RH Red Herring Integrity, IL Investigation Legibility, CM Clock Mechanics, RC Reveal Choreography, SF Solution Fairness) with Integrated/Partial/Detached ratings. 28 named diagnostic flags: IE-1 Fog of Facts, IE-2 Clue Starvation, IE-3 Asymmetry Collapse, IE-4 Evidence Island, IE-5 Signal Collapse; RH-1 Noise Cannon, RH-2 Decoy Without Spine, RH-3 Immortal Herring, RH-4 Orphaned Thread, RH-5 Herring Hierarchy; IL-1 Leap Detective, IL-2 Procedure Theatre, IL-3 Oracle Investigator, IL-4 Blind-Side Investigator, IL-5 Passive Catalyst; CM-1 Cosmetic Clock, CM-2 Clock Freeze, CM-3 Clock Without Cost, CM-4 Deadline Detour; RC-1 Reverse Gear Reveal, RC-2 Twist Before Foundation, RC-3 Premature Closure, RC-4 Reveal Pile-Up, RC-5 Explain Patch Ending; SF-1 Cheat Ending, SF-2 Invisible Culprit, SF-3 Obvious Culprit Drift, SF-4 Retroactive Collapse. Four required tracking artifacts: Clue Ledger (with Reader-Tractable? column), Red Herring Ledger (with Quality vs. True Solution column), Clock Pressure Map, Fairness Matrix. Pattern interpretation protocol with six checks, "Reading the Map" guide (8 dimension-combination patterns including Pressure-Puzzle Split), and blast radius classes. Ten severity hard gates (Architecture Void, Cheat Ending, Inferential Inaccessibility, Clock Disconnect, Investigation Opacity, Red Herring Dominance, Retroactive Incoherence, Culprit Underrepresentation, Reveal Timing Failure, Hybrid Contract Breach). Seven distinguish tests (Accessibility, Inference, Clock Conversion, Retroactive Coherence, Misdirection Foundation, Architecture-Ambiguity, POV Fairness) with four-class decision matrix and false-positive guardrails. Special Caution Zones (cozy, noir/hardboiled, literary mystery, inverted mystery, psychological thriller). Nine subgenre calibrations with named failure modes: The Locked Room Lecture (classic whodunit), Tea-Shop Stall Loop (cozy), Clipboard Carousel (procedural), Smoke Without Signal (hardboiled/noir), Unreliable Escape Hatch (psychological thriller), The Bulletin Board (conspiracy/political), Kitchen Twist Roulette (domestic), The Transparent Trap (inverted), The Beautiful Fog (literary hybrid). Dynamic literary mode trigger for hybrid recalibration. Explicit output format templates. Firewall compliance. Stacks with Genre Modules: Mystery and Thriller (contract), Emotional Craft (transmission), Horror Craft Integration (pressure-system parallel), Literary Craft (ambiguity), AI-Prose Calibration (generic fluency); feeds Pass 11 synthesis.
- **Mystery/Thriller Architecture level-setting brief** (genre/mystery-thriller-architecture-level-setting.md, 384 lines, three-model synthesis). Companion research brief grounding the audit in narrative theory, cognitive science, and practitioner craft knowledge. Eight theoretical sections: Sternberg's narrative interest triad with Brewer-Lichtenstein cognitive frame extensions (frame-matching/frame-completion/frame-shifting), Barthes' hermeneutic code (snares/equivocations/partial answers/suspended answers/disclosure mapped to audit dimensions), Eco's model reader (accessibility vs. tractability distinction), Todorov's typology with directional movement insight (mystery expands, thriller narrows), fair-play traditions and diagnostic limits (epistemic parity, prospective vs. retroactive fairness), cognitive psychology (hypothesis formation, model starvation/model lock, predictive processing, misdirection from magic performance studies via Kuhn/Rensink, the "click" of recognition, jigsaw vs. ball-of-twine architecture), craft practitioners (Christie assumption exploitation, Highsmith emotional suspense, Child present-moment urgency, French memory-as-investigation, Flynn epistemic warfare). Full failure mode taxonomy (28 named patterns including Pressure-Puzzle Split hybrid failure). Positive-case exemplar sets across 8 subtypes: Christie/Sayers (classic whodunit), Connelly/French (procedural), Chandler/Highsmith (noir), le Carré/Larsson (conspiracy), Flynn/Highsmith (psychological), French/Ware (domestic), Iles/Columbo (inverted), Eco/Auster/Bolaño (literary hybrid). Nine-subgenre calibration evidence with named failures and false positive risks. Distinguish problem analysis with seven operational tests, four outcome classes, and six false-positive controls.

## v0.4.10 - 2026-02-20

### Added
- **Horror Craft Integration audit** (genre/horror-craft.md, 593 lines, three-model synthesis). Genre-specific audit evaluating whether horror apparatus produces sustained dread, destabilization, and felt consequence or merely delivers horror-coded content. Core concept: "inert dread" — horror present in the plot summary but absent from the reading experience. Anchor insight: horror that escalates in facts but not in felt consequence is structurally parallel to literary craft that doesn't do work and worldbuilding that doesn't integrate. Six integration dimensions (DA Dread Architecture, UD Uncertainty Design, TC Threat Choreography, CE Consequence Embodiment, AP Atmosphere/Image Pressure, ER Ending Residue) with Producing/Partial/Inert ratings. 23 named diagnostic flags: DA-1 Static Dread Loop, DA-2 Kindless Escalation, DA-3 Escalation Cliff, DA-4 Dread Fatigue, DA-5 Anticipatory Deflation; UD-1 Confusion Smog, UD-2 Cheap Certainty, UD-3 Stated Instability, UD-4 Hypothesis Starvation; TC-1 Monster Before Mystery, TC-2 Mystery Without Teeth, TC-3 The Diminishing Reveal, TC-4 Visibility Drift; CE-1 Trauma Without Trace, CE-2 Immunity Bubble, CE-3 Damage as Decoration; AP-1 Gothic Wallpaper, AP-2 Symbolic Static, AP-3 Sensory Anesthesia, AP-4 Beautiful Distance; ER-1 Catharsis Betrayal, ER-2 Aftertaste Null, ER-3 Resolution Collapse. Three tracking artifacts: Horror Pressure Map (required), Consequence Ledger (recommended), Uncertainty Traction Log (optional). Pattern interpretation protocol with six named checks and "Reading the Map" guide. Nine severity hard gates (Pressure Void, Ending Contract Failure, Consequence Void, Dread Stasis, Epistemic Failure, Climax Underperformance, Reveal Timing Failure, Atmosphere Without Engine, Residue Null in Haunt Contract). Six distinguish tests (Interpretive Traction, Contract Coherence, Cost Continuity, Pressure Integrity, Transgression Purpose, Affect Calibration) with decision matrix and false-positive guardrails. Special Caution Zones (quiet horror, cosmic horror, horror-comedy, transgressive fiction). Nine subgenre calibrations with named failure modes: Mind Maze Without Thread (psychological), Abyss on a Leash (cosmic), Meat Without Meaning (body), Haunted Furniture Syndrome (domestic), Ritual Postcard (folk), Shock Treadmill (splatter/transgressive), Velvet Rot (Gothic/atmospheric), The Artful Flinch (literary horror), The Laser-Gun Safari (sci-fi horror). Explicit output format templates. Firewall compliance. Stacks with Genre Module: Horror (contract), Emotional Craft (transmission), Literary Craft (Beautiful Distance), Female Interiority (aestheticized suffering), Consent Complexity (violation/conditioning), AI-Prose Calibration (sensory flattening); feeds Pass 11 synthesis.
- **Horror Craft level-setting brief** (genre/horror-craft-level-setting.md, 328 lines, three-model synthesis). Companion research brief grounding the Horror Craft audit in horror theory, cognitive science, and practitioner craft knowledge. Nine theoretical sections: Carroll's art-horror (compound cognitive-affective mechanism, monster taxonomy — fusion/fission/magnification/massification), Freud's uncanny (familiar-made-strange, recognition before corruption), Kristeva's abjection (boundary collapse, corpse as ultimate manifestation, proximity requirement), Robin Wood's return of the repressed (monster as social/material pressure, structural isomorphism between external threat and internal state), Fisher's weird/eerie (absence-based and wrongness-based horror modes), Ligotti's philosophical horror (consciousness as horror, cosmic dread without monsters), King's terror hierarchy (terror > horror > revulsion), narrative psychology (anticipatory anxiety/predictive processing, habituation, cognitive appraisal, uncertainty tolerance). Full failure mode taxonomy (22 named patterns). Positive-case exemplar sets: Jackson/Harris/Tremblay (psychological), Lovecraft/VanderMeer/Langan/Ligotti (cosmic), Cronenberg/Machado/Barker/Koja (body), Enriquez/Oyeyemi/King/Due (domestic), Link/Jackson/Schweblin (literary), Barker/Ketchum/Palahniuk (transgressive). Folk Horror Chain structural pattern. Nine-subgenre calibration evidence with named failures and false positive risks. Distinguish problem analysis with six operational tests and five false-positive controls.

## v0.4.9 - 2026-02-20

### Added
- **Literary Craft Deep Dive audit** (craft/literary-craft.md, 575 lines, three-model synthesis). Cross-genre audit evaluating whether literary-mode ambitions do structural work or are cosmetic sophistication. Core concept: "ornamentation, not complexity." Anchor insight: literary mode that doesn't do work is structurally identical to worldbuilding that doesn't do work. Five primary integration dimensions (PA Prose Architecture, TF Thematic-Form Integration, IA Image Architecture, ST Subtext/Tonal Control, RA Recognition Architecture) plus one cross-cutting dimension (VA Voice Architecture). 22 named diagnostic flags: PA-1 Verbal Wallpaper, PA-2 Register Cosplay, PA-3 Purple Archipelago, PA-4 Difficulty Without Reward, PA-5 Workshop Finish; TF-1 Thesis Statement Novel, TF-2 Structural Stunt, TF-3 Thematic Furniture, TF-4 Interpretive Vacuum; IA-1 Dead Metaphor Garden, IA-2 Orphan Image, IA-3 Symbol Tyranny, IA-4 Sensory Wallpaper; ST-1 Transparent Character, ST-2 Explanatory Impulse, ST-3 Tonal Drift, ST-4 Ironic Collapse; RA-1 Near Miss, RA-2 Generic Recognition, RA-3 Insight Lecture, RA-4 Recognition Without Preparation; VA-1 Voice as Veneer, VA-2 Workshop Neutral, VA-3 Posture Mismatch. Three tracking artifacts: Literary Architecture Map (required), Scene Pressure Grid (required), Recognition Arc Log (optional). Central Defamiliarization Test (perception vs. appreciation). Eight severity hard gates. Six distinguish tests with decision matrix, false-positive guardrails, and Special Caution Zones (debut manuscripts, translated work, lyric novels). Nine genre-hybrid calibrations with named failure modes: Elegant Plateau (literary realist), Velvet Brake (literary thriller), Metaphor Shelter (literary SFF), Beautiful Rot (literary horror), Case and Chorus Split (literary crime), Competent Fog (upmarket), Structural Stunt elevated (experimental/lyric), Period Piece (literary historical), Beautiful Recollection (literary memoir/CNF). 2-of-5 activation rubric. Explicit output format templates. Firewall compliance section. Stacks with Emotional Craft, AI-Prose Calibration, Female Interiority, SFF Worldbuilding Integration; feeds Pass 11 synthesis.
- **Literary Craft level-setting brief** (craft/literary-craft-level-setting.md, 302 lines, three-model synthesis). Companion research brief grounding the Literary Craft audit in critical theory and practitioner craft knowledge. Nine theoretical sections: Shklovsky's defamiliarization (perception vs. automatization), New Criticism diagnostic method (Brooks on functional metaphor, Empson on productive ambiguity), Booth on rhetorical choice (voice as argument architecture), Phelan on rhetorical narratology (form as rhetorical action), Wood on free indirect style (consciousness management), contemporary craft perspectives (Saunders "bouncer at Club Story," Smith "Two Paths for the Novel," Baldwin, Robinson), Wallace on postmodern irony (foundation for Ironic Collapse), McGurl on Program Era (workshop-homogeneity problem). Full failure mode taxonomy across five categories (22 named flags with theoretical provenance). Positive-case exemplar sets: Morrison/Ferrante/Cusk (literary realism), Carver/Johnson/Berlin/Offill (minimalism), Pynchon/Wallace/Rushdie (maximalism), Sebald/Carson/Rankine (structural form), Ishiguro/Le Guin/McCarthy/Atwood/French (hybrid modes). Cross-genre calibration evidence. Distinguish problem analysis with operational tests and false-positive controls.

## v0.4.8.1 - 2026-02-20

### Added
- **Female Interiority level-setting brief** (craft/female-interiority-level-setting.md, 256 lines). Companion research brief grounding the Female Interiority audit in cognitive science and narratology. Three theoretical pillars: Dorrit Cohn's tripartite consciousness model (Psycho-Narration, Quoted Monologue, Narrated Monologue) providing syntactic markers for the four interiority tiers; Lisa Zunshine's Theory of Mind framework mapping recursive intentionality orders to interiority depth; Susan Lanser's Fictions of Authority connecting gendered voice modes to interiority vulnerability patterns. Includes: Cohn-to-tier mapping table, Voice-Context Vulnerability Matrix (3 voice modes × 7 pressure contexts), structural cascade analysis (Midpoint Pivot and Lie Collapse as interiority failure amplifiers), concrete detection mechanics (mode collapse, verb category shift, ToM order drop, emotional label substitution, reset signal), 11 positive-case exemplars with craft technique identification (Ferrante, Morrison, Milan, Jackson, Jemisin, Tolstoy, Woolf, Machado, Larsen, Anderson, Mantel), 5 cross-case success signals, intentionality problem reasoning with genre-specific challenges, full source set (theory, craft criticism, exemplar fiction). Follows the level-setting companion pattern established by cozy-tag-level-setting.md and sff-worldbuilding-level-setting.md.

## v0.4.8.0 - 2026-02-20

### Added
- **SFF Worldbuilding Integration audit** (specialized audit, genre/sff-worldbuilding.md, 501 lines, three-model synthesis). New audit evaluating whether speculative worldbuilding does narrative work — distinct from the Genre Module: SF/F which handles consistency. Core concept: "inertness, not inconsistency." Five integration dimensions (Cognitive, Thematic, Prose, Social, Emotional) with Integrated/Partial/Detached ratings. 20 named diagnostic flags across five families: World-Character (WC-1 Earth Minds in Alien Bodies, WC-2 The Tourist, WC-3 Wallpaper Competence, WC-4 The Undeformed), Exposition Craft (EC-1 The Wiki World, EC-2 Exposition Rigor Mortis, EC-3 The Mode Mismatch, EC-4 Late-Stage Explaining), Thematic Integration (TI-1 The Cellphone-Proof Theme, TI-2 The Passive Physics Engine, TI-3 Generic Dilemma in Exotic Dress, TI-4 Climax Decoupling), Scale/Depth (SD-1 The Aesthetic Shell, SD-2 Social Architecture Without Social Physics, SD-3 The Load-Bearing Wall That Isn't, SD-4 Scope Inflation Drift), Prose-Level (PL-1 The Noun-Swap World, PL-2 Description Island, PL-3 Register Reversion, PL-4 Metaphor Import Leak). Three tracking artifacts: Integration Map (required), Load-Bearing Ledger (required), Pressure Event Log (optional). World Pressure Loop diagnostic chain. Six Distinguish tests with decision matrix and false-positive guardrails. Eight severity hard gates with numerical thresholds. Eight subgenre calibrations with named failure modes (The Elegant Irrelevance, The Grand Tour, The Appendix Illusion, The Convenient Masquerade, Neon Skin No Bite, Randomness Alibi, Metaphor Cage, The Stat Sheet Treadmill). Cross-genre structural isomorphisms for author legibility. Stacks with Genre Module: SF/F; feeds Pass 11 synthesis.

## v0.4.6.0 - 2026-02-20

### Added
- **Intake Router v1** — single entry point (`/start`) that routes users to the right workflow in 2–3 questions
  - **Question 1 (Artifact):** "What do you have right now?" — idea, fragments, partial draft, complete draft, series. Deterministic thresholds for classification when material is provided rather than self-reported (based on narrative continuity, not word count).
  - **Question 2 (Goal, conditional on Artifact):** Options change per artifact state — prevents offering irrelevant goals. E.g., "Check submission readiness" only appears for complete drafts.
  - **Question 3 (Constraint/Operator modifiers):** Deadline, AI-assisted text, nonfiction, sensitive/legal risk, editing for someone else, facilitating a writing group, co-authoring. Multiple selections allowed.
  - **Fallback disambiguator:** When confidence is low, one tiebreaker question maps to three buckets (start drafting / improve existing / evaluate readiness).
  - **Complete route map** with status flags (built, gap, partially built) for all artifact × goal × constraint combinations.
  - **Gap protocol:** When route target isn't built, acknowledge honestly, offer closest available workflow, name what won't be covered.
- **Router integration in Core DE intake:** When user arrives via `/start`, router output (artifact, goal, constraint flags) skips redundant intake questions.
- New `/start` command (9 commands total, up from 8).

### Changed
- **Genre calibrations reordered:** Literary Fiction first (most common primary module), then Genre-Bending/Literary Mode, then alphabetical (Horror, SF, Romance/Erotic). Previously Romance/Erotic was first.
- **Genre calibrations generalized:** Genre-specific detail in core pass descriptions moved to on-demand genre modules. Core passes are now genre-neutral with summary + pointer to full module. All diagnostic machinery remains available when the genre module is activated.
- **Register Uncertainty diagnostic updated** with multi-genre example (Literary Thriller Horror interrogation scene). The diagnostic now demonstrates register conflict using three registers rather than four, making the core concept clearer.
- **Interiority Preservation audit expanded** from intimate scenes to all high-intensity scenes (combat, interrogation, crisis, intimate encounter). Genre-specific applications section covers Action/Thriller, Romance/Erotic, Horror, and Literary with cross-references to relevant modules.
- **AIC-7: Discourse Leak** integrated into AI-Prose Calibration (7 flag families total). Five evidence categories: Assistant Frame, Hedge Drift, Template Loop, Lexical Convergence, Commitment Evasion. Includes evidence burden requirements, false-positive guardrails, and three-step audit workflow.
- **Examples generalized** across reference files. Character-specific and manuscript-specific examples replaced with role-based descriptions (e.g., "Protagonist" instead of named characters, generic series descriptions instead of titled works). Teaching content preserved; specificity improved for broader applicability.
- **Reference implementation paths normalized.** Internal filesystem paths and project-specific directory names replaced with portable references.
- **Specialized-audits reference directory restructured** into three subdirectories: `craft/` (universal audits), `genre/` (form/genre-specific audits), `tag/` (cross-genre modifier audits). All reference paths updated. Prior changelog entries retain original paths as historical record.
- **Female Interiority audit expanded** from intimate-scene focus to universal craft audit (v0.4.8, three-model synthesis). New diagnostic framework: "interiority thinning" as core concept with four-level spectrum (Full / Thinned / Functional / Absent). 20 named diagnostic flags across four categories (Interiority Thinning IT-1–IT-12, Gaze & Observation GO-1–GO-4, Agency AG-1–AG-4, Relationship RF-1–RF-2). New flags from synthesis: Competence as Costume (IT-8), Caregiver Erasure (IT-9), Ensemble Fade (IT-10), Borrowed Stakes (IT-11), Refrigerated Consequence (IT-12), The Sexy Lamp (GO-4), The Smurfette (AG-4). Interiority Map with named reading patterns (Solitude Spike, Relational Dependency). Severity hard gates for reproducible calls. Five-test Distinguish framework with decision matrix. Genre calibration matrix with named failure modes (Desire Dependency, Generic Terror, The Case as Personality, The Gender-Swapped Archetype, The Aestheticized Woman, Minds in Corsets, Body-Without-Mind). Synthesis handoff spec for Pass 11.
- **APODICTIC branding** adopted in README. Full package rename deferred to publication.

### Notes
- Existing commands (`/develop-edit`, `/pre-writing`, `/diagnose`, etc.) remain functional as direct-access shortcuts. The router is the recommended entry point for new users.
- The router implements the four-axis classification model (Artifact × Goal × Operator × Constraint) from the Publication Requirements. Operator is inferred from context or self-reported in Q3, not asked as a separate question.
- Genre module activation is unchanged: modules load when genre is specified in contract or detected during intake. The core pass generalization means the core framework loads faster and doesn't assume any particular genre.

## v0.4.5.0 - 2026-02-20

### Added
- **Pre-Writing Pathway** — new skill and `/pre-writing` command guiding writers from idea to draftable structure without a manuscript
  - **Phase 0: Writer Mode Calibration** — detects architecture-first vs. discovery-first writers; adjusts pathway pressure, field tolerance, and re-entry interpretation accordingly
  - **Seed Inventory** (Phase 1) — maps writer's raw idea onto 8 seed types (premise, character, world, feeling, scene, theme, genre instinct, comp)
  - **Uncertainty/Assumption Ledger** — tracks confidence (Decided/Provisional/Unknown) and dependencies for every structural decision; persists into Structural Plan and feeds Re-Entry Diff
  - **Readiness Gates** — Storyable gate (after Phase 3: premise + engine + tension cohere) and Draftable gate (before Phase 5: spine candidate + ending instinct + arc states + known unknowns)
  - **Option Architecture** (Phase 4) — presents 2–3 viable spine candidates with tradeoffs instead of converging to one recommendation
  - **Complexity Budget** (Phase 4B) — explicit first-draft scope caps for POV count, subplots, timeline complexity, world-building scope
  - **Prospective Contract** — same schema as standard contract but built from intent; embedded in Structural Plan output
  - **Minimal Viable Plan** — prose-format fallback for discovery writers who pass the storyable gate but not the draftable gate
  - **Re-Entry Diff Protocol** (Phase 6) — classifies divergences between prospective contract and actual manuscript as: intentional evolution, signal loss, structural drift, or expected discovery
  - **Anti-sycophancy controls** — mandatory Hard Risks section, real readiness gates (not rubber stamps), option architecture prevents premature validation, ledger prevents false confidence
- **Output artifact conventions** aligned with Core DE naming: `[Project]_Structural_Plan_[runlabel].md`, `[Project]_MVP_[runlabel].md`, `[Project]_Reentry_Diff_[runlabel].md`
- **AI-Prose Calibration audit** (specialized audit #18) — diagnoses prose-level failure patterns in AI-generated or AI-assisted text
  - 6 flag families: AIC-1 Generic Hand (voice singularity), AIC-2 Velvet Fog (scene fog + lexical genericism), AIC-3 Echo Stack (structural repetition), AIC-4 Register Seams (multi-source splicing), AIC-5 Puppet Dialogue (mouth uniformity), AIC-6 Continuity Smear (world-model failures)
  - 3-tier severity: Spot / Pattern / Systemic
  - Required outputs: flag summary, top 3 systemic risks, contamination map, Keep/Recast/Replace salvage plan, Pass 11 readiness impact note
  - Contract intake integration: drafting-method question triggers automatic activation
  - Model-agnostic design: targets prose quality categories, not model-specific tells

### Notes
- The pre-writing pathway produces a prospective contract that becomes the baseline when the writer returns with a draft. Core DE intake uses it as a starting hypothesis; the Re-Entry Diff surfaces what the writer discovered, lost, or drifted from.
- Discovery-first writers may exit with an MVP instead of a full Structural Plan. MVPs do not feed the Re-Entry Diff — standard intake runs from scratch, with the MVP as context.
- AI-Prose Calibration frames AI-generated text as raw material to salvage, not contamination to detect. The audit is useful for any prose exhibiting the flagged patterns, regardless of origin.

## v0.4.4.8 - 2026-02-18

### Added
- **Severity Honesty Protocol** — 4 rules preventing LLM sycophancy in severity assignments (softening Must-Fix to Should-Fix, hedge language, finding one positive passage to downgrade systemic flags)
- **Severity Floor Rules** — 3 structural constraints ensuring diagnostic coherence (Weak core-promise axis requires Must-Fix flag; systemic blast radius caps verdict; high flag volume caps positive verdicts)
- **Pass-Level Output Protocol** — standardized output ordering for evaluative passes: Analysis → Rejection Memo → Priority Leaks → Strengths. Requires rejection memo in every evaluative pass (Pass 1, 2, 5, 8, and all Full DE passes). Strengths cap tied to leak count.
- **Rejection Memo** as a required component of both individual passes and synthesis ("The Strongest Case Against")
- **Revision Checklist** replaces Surgery List — author-facing table with What / Why / Effort columns (Low/Medium/High effort replaces Must-Fix/Should-Fix/Could-Fix severity labels)

### Changed
- **Core DE Synthesis completely rewritten** as editorial letter format:
  - Processing Protocol: 5-step internal process (Intent Check → Root Cause → Triage → Adversarial Self-Check → Write Letter)
  - Presentation Format: 7 required sections (Title Block, The Short Version, What the Book Does Best, What Needs Work, Revision Checklist, The Strongest Case Against, Appendices)
  - Tone and Voice guidance (avoid framework jargon, mechanistic transitions, strength-padding; use direct declarative assessment, embedded line references, bolded thesis-statement headings)
  - Key principle: processing order ≠ presentation order (self-check runs before writing but appears in appendix)
- **Core DE Deliverables simplified** to Editorial Letter + Diagnostic State (removed Surgery List, Revision Order, Top 10 Reader Questions)
- **Full DE Editorial Letter updated** with 5 scaling differences from Core DE + Pass 11 integration guidance
- **Output Constraints updated**: "Maximum 25 surgery list items" → "Maximum 10 revision checklist items (Core DE); 15 (Full DE)"
- Negative-first ordering: Priority Leaks appear before Strengths in all pass outputs
- Strengths must be specific and evidence-based with citation; capped relative to leak count

### Notes
- This version addresses the documented LLM tendency to soften editorial findings, producing editorial letters that read as one informed voice talking about a book rather than a framework generating output.

---

## v0.4.4.6 - 2026-02-17

### Added
- **Cozy level-setting brief** (`references/cozy-tag-level-setting.md`) — standalone research brief covering BISAC/Thema taxonomy, Circana/PW market data, recovery-psychology research (Rieger et al., Rieger & Bente), narrative-resistance findings (Moyer-Gusé et al.), social connectedness research (Wildschut et al., Juhl et al.), and cross-media cozy scholarship
  - Evidence labeling system: `SOURCE-VERIFIED` vs. `MARKET INFERENCE`
  - Lineage: Codex53 research brief
- **Inline Level-Setting Notes** added to Cozy Tag audit summarizing key external evidence

### Changed
- Tag audit family standard: every tag audit includes an inline Level-Setting Notes section grounding axes in external evidence. A standalone companion brief is the exception for tags with unusually deep evidence bases (cozy), not the standard.
- Philosophical Tag audit: family context updated to reflect inline-first standard
- Specialized-audits reference list: added `references/cozy-tag-level-setting.md`

### Notes
- The discipline of asking "what does the market say? what does the research say?" is institutionalized in the inline section. The cozy brief stays because the evidence genuinely warrants it — BISAC codes, peer-reviewed psych, game-studies scholarship. Most tags won't need a standalone file.

---

## v0.4.4.5 - 2026-02-16

### Added
- **New tag audit: Philosophical Tag** (`references/philosophical-tag.md`)
  - Second audit in the tag audit family (after Cozy)
  - Seven axes: Question Architecture, Dramatic Embodiment, Counterposition Strength, Conceptual Progression, Philosophical Feel, Legibility Under Complexity, Resolution Ethics
  - Philosophical Intensity Spectrum (High / Medium / Low) with severity calibration
  - 21 named diagnostic flags: Topic Fog, Question Collapse, Question Multiplication, Seminar Scene, Parallel Tracks, Illustration Mode, Straw Army, Mouthpiece Asymmetry, Vanishing Objection, Broken Record, Volume Escalation, Late Pivot Without Foundation, Closed Loop, Explanatory Reflex, Opacity Posture, Jargon Fog, Abstraction Drift, Decoration Philosophy, Resolution Collapse, Ambiguity Dodge, Thesis Snap
  - PH flag family (PH-1 through PH-9) with named pattern mappings
  - Cross-genre calibration matrix (Literary, SF, Horror, Fantasy, Thriller, Historical, Mystery, Romance)
  - Axis E (Philosophical Feel) addresses the experience-layer dimension: does the reader *think alongside* the text?
  - Routing distinction: Banister evaluates rhetorical fairness; Dialectical Clarity evaluates argument structure; this audit evaluates philosophical *delivery as experience*
  - Level-setting notes on Thema/BISAC metadata and narrative-transportation research
  - Lineage: Codex53 v0.1 draft → Opus revision

### Changed
- Specialized-audits skill description updated with philosophical/tag audit triggers
- Specialized-audits SKILL.md Tag Audits table: added Philosophical Tag row
- Core SKILL.md Tag Audits section: added Philosophical Tag entry
- Plugin structure note updated: "17 deep-dive audits, 2 tag audits, and 4 research modes"
- All skill versions bumped to 4.4.5

---

## v0.4.4.4 - 2026-02-16

### Added
- **New tag audit: Cozy Tag** (`references/cozy-tag.md`)
  - First audit in the new **tag audit family** — experience-layer diagnostics that sit on top of any parent genre's structural contract
  - Cozy Delivery Model with six axes: Safety Envelope, Softness Signals, Belonging Engine, Recovery Rhythm, Everyday Stakes Presence, Restoration Arc
  - Cozy Intensity Spectrum (High / Medium / Low) with severity calibration per intensity level
  - 18 named diagnostic flags: Trapdoor, Ratchet Without Release, Cruelty Leak, Cozy Skin, Comfort Prop, Warmth Collapse, Relational Vacuum, Protagonist Island, Unrepaired Breach, Summary Recovery, Adrenaline Stack, Fridge Recovery, Crisis Saturation, Inert Domesticity, Escalation Addiction, Pyrrhic Landing, Dangling Thread, Tonal Whiplash Landing
  - CZ flag family (CZ-1 through CZ-8) with named pattern mappings
  - Cross-genre calibration matrix (Mystery, Fantasy, Romance, Horror, Thriller, SF, Literary)
  - Anchor + Interacting Lenses analysis method (not sequential checklist)
  - High-Stakes Cozy misread section addressing the most common beta-reader misdiagnosis
  - "Return address" concept for Belonging Engine axis
  - Lineage: Codex53 v0.1 draft → Opus revision

### Changed
- Specialized-audits skill description updated with cozy/tag audit triggers
- Specialized-audits SKILL.md adds Tag Audits subsection in audit listing
- Core SKILL.md adds Tag Audits section between Specialized Audits and Research Modes
- Plugin structure note updated: "17 deep-dive audits, 1 tag audit, and 4 research modes"

### Notes
- The tag audit family establishes a new architectural category: experience-layer diagnostics distinct from genre audits (structural contracts). Future tag audits (Erotic, Dark/Grimdark, Literary, Hopepunk) will follow the same pattern: experience model with named axes, named diagnostic flags, intensity spectrum, cross-genre calibration, anchor + interacting lenses method.
- This revision also introduces the genre/tag distinction as a framework-level concept, which will inform the broader restructuring tracked in Publication Requirements.

---

## v0.4.4.3 - 2026-02-16

### Added
- **Plot Architecture audit expanded** from 39 spines / 9 families to 48 spines / 12 families:
  - Family 10 (Rhythm & Intensity Engines): Wave/Pulse Structure, Lullaby Structure, Pressure Cooker
  - Family 11 (Format & Frame Engines): Episodic/Modular, Clinical Case File, Nested Dolls, Talisman Structure
  - Family 12 (Transformation & Identity Journeys, Extended): Heroine's Journey (Murdock), Seven-Point Structure (Dan Wells)
  - Each new spine includes full logic gates, severity levels, and genre cross-references
  - Diagnostic Quick Reference expanded with 7 new symptom → diagnosis rows
  - Spine Compatibility Matrix expanded with 11 new combination entries
- **New specialized audit: Plot Selection & Coaching** (`Specialized_Audits/Specialized_Audit_Plot_Selection_Coaching.md`)
  - Upstream structural guidance: works before or alongside Plot Architecture
  - Phase 1: Story Concern Mapping (reader feeling, engine type, truth relationship)
  - Phase 2: Spine Selection Protocol with decision tree (single-spine and multi-spine)
  - Phase 3: Structural Technique Overlays (TV/Serial format, Game-Inspired format)
  - Phase 4: Hybrid Structure Design (layer model: micro/meso/macro/meta, conflict detection, handoff types)
  - Phase 5: Structural Triage for stuck drafts (symptom → diagnosis → prescribe)
  - Phase 6: Pre-Drafting Structural Plan template
- **New specialized audit: Fantasy & Series Architecture** (`Specialized_Audits/Specialized_Audit_Fantasy_Series_Architecture.md`)
  - Part I: 5 fantasy-specific spines with logic gates (Anti-Hero's Journey, Folkloric/Mythic Mosaic, Liminal Drift, Fractured Chronicle, Ritual Pattern)
  - Part II: 6 series-level architectural patterns (Expanding Quest, Character Web, Revolving Protagonist, Seasonal Arc, Mystery Box/Revelation Slow Burn, Empire Cycle/Generational Arc)
  - Part III: 3 series rhythm patterns (Convergent-Divergent Cycle, Event Spine, Mythic Undertow)
  - Part IV: Cross-reference tables linking fantasy spines to general spines and series architectures to per-volume spine choices

### Changed
- `Module_Index.md` updated to v3.5: new audits registered in table, file tree, statistics (now 32 total modules/audits/modes/passes/pathways), coverage notes, and "When to Use What" quick reference.
- Plot Architecture audit description in Module Index now reflects 48 spines / 12 families.

### Notes
- Source material: conversational exploration document ("Alternatives to 3 Act Plot Structures") de-duplicated against existing audit, reformatted into logic-gate structure, and split across three deliverables by function (diagnosis, coaching, architecture).
- Overlapping structures (Freytag, Spiral, Fugue, Braided, Rashomon, Hero's Journey, Quest, Siege) were already in the audit; only genuinely new spines were added.
- Structures better understood as presentation techniques (TV/Serial, Game-Inspired) were placed in the Selection & Coaching audit rather than as spines in the Plot Architecture audit.

## v0.4.4.2 - 2026-02-13

### Added
- New top-level `README.md` with public naming, shorthand, and canonical-doc pointers.

### Changed
- Public-facing product name normalized to `APODICTIC Development Editor` with shorthand `APDE`.
- `SKILL.md` and `Module_Index.md` now include explicit brand alias guidance while retaining legacy filenames for compatibility.
- Output templates now include framework footer branding:
  - `Templates/Contract_Template.md`
  - `Templates/Diagnostic_State_Template.md`
  - `Templates/Reverse_Outline_Template.md`
- Pass 11 module header and output template now use APDE branding for generated reports.

### Notes
- This is a naming and documentation normalization patch; no analysis logic changed.

## v0.4.4.1 - 2026-02-13

### Added
- Formal changelog introduced.
- Canonical-source declaration that `SKILL.md` is the operational source of truth.
- Explicit runlabel convention for core outputs (date-based `YYYY-MM-DD`, optional agent prefix such as `codex53_2026-02-13`).
- Optional Pass 11F (Adversarial Reader Stress Test) surfaced in module documentation where missing.

### Changed
- `SKILL.md` now defines runlabel-based output naming for core passes and clarifies `Diagnostic_State.md` as a rolling state file.
- `SKILL.md` project integration now accepts either `Contract_and_Controlling_Idea.md` or `[Project]_Contract*.md`.
- `SKILL.md` now requires initialization of `Diagnostic_State.md` from `Templates/Diagnostic_State_Template.md` when absent.
- `Module_Index.md` aligned with current pass architecture, including optional 11F and updated output conventions.
- `AI_Development_Editor_Complete_v0.4.4.md` Pass 11 section reframed as a condensed summary with explicit operational authority delegated to `SKILL.md` and `Pass_11_Critical_Quality_Market_Viability_v2.md`.

### Fixed
- Documentation drift between framework index/spec documents on Pass 11 coverage and output naming.
- Ambiguity around first-run bootstrap behavior for `Diagnostic_State.md`.

### Notes
- This release is a governance and consistency patch: no new core analysis passes were added.
- Suggested future process: append entries here whenever pass behavior, output contracts, or required artifacts change.

## v0.4.4 - 2026-02-02 to 2026-02-12 *(historical backfill; staged rollout)*

### Added
- Consolidated reference document: `AI_Development_Editor_Complete_v0.4.4.md`.
- Evaluative gate module: `Pass_11_Critical_Quality_Market_Viability_v2.md` with sub-passes `11A-11F`.
- QF flag family (`QF-1` through `QF-7`) and required Hard Truths/verification structures in Pass 11.
- Research modes under `Specialized_Audits/`:
  - `Research_Mode_Comp_Validation.md`
  - `Research_Mode_Factual_Verification.md`
  - `Research_Mode_Genre_Currency.md`
  - `Research_Mode_Representation_Context.md`
- Franklin redirect workflow: `Franklin_Pathway.md` (pre-spine viability gate).
- New specialized audits:
  - `Specialized_Audit_Emotional_Craft.md`
  - `Specialized_Audit_Scene_Turn.md`
  - `Specialized_Audit_Character_Architecture.md`
  - `Specialized_Audit_Dialectical_Clarity.md`
  - `Specialized_Audit_Memoir_Creative_Nonfiction.md`
  - `Specialized_Audit_Narrative_Nonfiction_Craft.md`

### Changed
- Operational quick-reference updated to `SKILL.md` version `4.4`.
- Workflow model expanded beyond Core/Full to include Franklin redirect criteria for absence-of-story material.
- Module index expanded to include evaluative pass routing and research-mode routing.

### Fixed
- Structural-only diagnostic gap addressed with explicit quality/market/readiness evaluation pass (Pass 11).
- Nonfiction/pre-spine handling gap addressed via dedicated Franklin pathway.

### Notes
- This backfill aggregates multiple file timestamps (not a single atomic commit).
- Earliest clear `v0.4.4` artifacts: research modes (`2026-02-02`) and Pass 11 module (`2026-02-05`).
- Latest core `v0.4.4` alignment in this phase: `SKILL.md`, `Module_Index.md`, and `AI_Development_Editor_Complete_v0.4.4.md` (`2026-02-12`).

## v0.4.3 - 2026-01-29 *(historical backfill)*

### Added
- Register Uncertainty diagnostic in the Literary Fiction module for multi-genre register conflict.
- Reframed interiority audit (`Male Gaze` -> `Interiority Preservation`) with symmetric POV logic.
- New `Series / Composite Novel` specialized audit for part-level and arc-level calibration.
- Subfolder project organization for genre modules, specialized audits, and templates.

### Changed
- Core framework promoted to `AI_Development_Editor_Framework_v0.4.md` version `4.3`.
- Supporting docs updated to reference folderized module paths.

### Notes
- Backfill from internal performance assessment (dated 2026-01-29).
- `v0.4.3` refinements were validated during live testing against a multi-POV literary fiction manuscript.
