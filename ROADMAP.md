# APODICTIC Roadmap

**Current version:** See `plugins/apodictic/.claude-plugin/plugin.json`

---

## Board

| In Progress | Planned | Done | Backlog |
|-------------|---------|------|---------|
| [Genre Audit Expansion](#genre--audit-expansion) | [Adaptive Mode Escalation](#adaptive-mid-run-mode-escalation) | [v1.9.0](#v190--ai-prose-calibration-v20) | [Feedback Triage](#feedback-triage) |
| | | [v1.7.0](#v170--harness-engineering) | |
| [Coaching Deepening](#coaching-deepening) | [Editor Scaffolding](#editor-scaffolding) | [v1.4.0](#v140--surface-hardening--writers-block) | [Nonfiction Pre-Draft](#nonfiction-pre-draft-pathway) |
| | [Diagnostic Vocabulary](#diagnostic-vocabulary-mode) | [v1.3.0](#v130--nonfiction-argument-engine--genre-audits) | [Legal Risk Register](#legal-risk-register) |
| | | [v1.2.1](#v121--audit-sequencing--model-tags) | [Multi-Party Intake](#multi-party-intake) |
| | | [v1.2.0](#v120--artifact-coverage) | [Episode Cadence](#episode-cadence) |
| | | [v1.1.3](#v113--coaching-deepening) | [Collaborative Revision Coaching](#collaborative-revision-coaching) |
| | | [v1.1.2](#v112--revision-coach) | [Framework Overview Dashboard](#framework-overview-dashboard) |
| | | [v1.1.1](#v111--series-continuity--pass-9) | [Pre-Skill Context Compaction](#pre-skill-context-compaction) |
| | | [v1.1.0](#v110--token-aware-agent-usage) | |
| | | [v1.0.9](#v109) | |
| | | [v1.0.8](#v108) | |
| | | [v1.0.4](#v104) | |
| | | [v1.0](#v10--public-release) | |

---

## Genre & Audit Expansion

New specialized audits built from real editorial engagements, not hypothetical coverage. Each manuscript-in-genre that runs through the plugin surfaces what a genre's audit actually needs.

**Expansion protocol** (codified in `Specialized_Audit_Expansion_Stub_TEMPLATE.md`):
1. Level-setting research phase (cognitive narratology, genre theory, reader-experience evidence, positive cases)
2. Structural spec phase (named flags, dimensions, hard gates, subgenre calibrations, distinguish framework)
3. Three-model synthesis for quality assurance — validated with Reception Risk (v1.0.9)

**Built** (shipped in v1.3.0):
- **Supernatural Horror** (genre module, 25 flags, 7 dimensions, 8 subgenre calibrations, 10 hard gates)
- **Grimdark / Dark Fantasy** (genre module, 22 flags, 7 dimensions, 6 subgenre calibrations, 9 hard gates)
- **Nonfiction Argument Engine** — see [dedicated section](#nonfiction-argument-engine) below

**Seeded candidates** — reference texts identified, ready for level-setting:

**YA / Kidlit (genre module).** Protagonist age-authority dynamics, voice register calibration (too-adult vs. condescending), first-experience plot drivers, pacing expectations distinct from adult fiction. One module with MG/YA subgenre variation.
- Mary Kole — *Writing Irresistible Kidlit*
- Deborah Halverson — *Writing Young Adult Fiction For Dummies*

**Military / War Fiction Plausibility (scope TBD).** Tactical plausibility, violence-meaning relationship, institutional voice. May be a subgenre variation within Historical Fiction or a specialized research mode. Build only if demand materializes.
- Benjamin Sobieck — *The Writer's Guide to Weapons*

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
2. `docs/argument-state-schema.md` (v0.1.1, §§ 10.1–10.7)
3. Argument Red Team (v1.0) + level-setting research
4. Argument Persuasion + level-setting research
5. Argument Evidence Deep-Dive
6. Citation Verifier (v1.0) + level-setting research — CV1-CV12 flags, two-phase verification, 5 citation relation types, domain-adaptive source hierarchy, Python API scripts, Citation_Ledger.md artifact
7. Field Reconnaissance (v1.0) + level-setting research — counterevidence search with adaptive self-feedback loop, literature gap detection, source ecosystem health, domain-adaptive priority, Field_Reconnaissance_Report.md artifact
8. Adversarial Evidence Review (v1.0) + level-setting research — three-protocol adversarial pressure test (ACH, legal cross-exam, severe testing), HX/LX/SX code families, domain packs (GRADE, RoB 2, ROBINS-I, FRE 702), two-tier severity with convergence, survivability judgments, Adversarial_Evidence_Preparation_Guide.md artifact. Adversarial collaboration: Claude Opus 4.6 + Codex o3.
9. Nonfiction routing in intake (runtime + design docs)
9. Revision Coach argument mode (8 coaching tracks + argument session plan template)

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

### Writer's Block & Rut-Breaking — **Built (v1.4.0)**

8-type expanded block taxonomy (replaces 3-way split), 7 structural prompt families (Constraint, Inversion, Isolation, Scale-shift, Perspective, Deletion, Temporal), 5-part firewall test, perfectionism modifier, nocebo inoculation, no-prompt zones, Structural Experiment session plan section. Integrated into both fiction and argument coaching protocols.

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

### Adaptive Mid-Run Mode Escalation

After Tier 1 passes complete, the system has significantly more information about the manuscript than it had at preflight — multiple POV characters discovered, timeline complexity detected, genre hybridization identified. The execution mode selected at intake may no longer be optimal.

**What it does:** A checkpoint after Tier 1 passes that compares the actual manuscript complexity (as revealed by Pass 0 and Pass 1 findings) against the preflight estimate. If complexity is materially higher than predicted, recommend escalating the execution mode before committing Tier 2 tokens.

**Escalation paths:**
- Single-agent → sequential (when salience decay risk rises due to unexpected complexity)
- Sequential → hybrid (when the focus map would meaningfully reduce noise for later passes)
- Sequential → swarm (when architectural isolation would catch cross-pass anchoring on a complex manuscript)

**Constraints:**
- Escalation is safe only between Tier 1 and Tier 2 — never retroactively re-run completed passes
- Escalation is a recommendation to the author, not automatic — the user confirms before mode switch
- The existing Findings Ledger entries from Tier 1 carry forward unchanged; only the dispatch method for Tier 2 passes changes

**Triggers (checked after Tier 1 completes):**
- Pass 0 discovers > 3 POV characters (preflight's pronoun heuristic underestimated)
- Pass 0 discovers non-linear timeline or nested frame structure
- Pass 1 flags > 5 belief failures or > 3 orientation failures (higher-than-expected analytical density)
- Pass 0+1 combined findings exceed 20 notable items (suggesting the manuscript will generate a complex synthesis)

**Dependencies:** Requires the sidecar state (`Diagnostic_State.meta.json`) and mechanical validation infrastructure from v1.7.0. The escalation check reads the Tier 1 findings from the Findings Ledger, compares against preflight metadata, and writes the mode change to the sidecar if accepted.

**Where to implement:** Add a §Mid-Run Escalation Check section to `run-core.md` between the Execution Protocol and Pre-Pass Re-Grounding sections. The check runs once, after Tier 1, before the first Tier 2 pass is dispatched.

**Open questions:**
- Should the system also support *de-escalation* (swarm → sequential) if Tier 1 reveals the manuscript is simpler than expected? Lower priority — the cost of running a more expensive mode is wasted tokens, not wrong analysis.
- What's the UX for presenting the escalation recommendation? Probably a brief summary: "Tier 1 found [X complexity signals]. I'd recommend switching from [current] to [recommended] mode for the remaining passes. Cost difference: ~[N]K tokens. Proceed?"

### Framework Overview Dashboard

Static, single-file HTML overview of the plugin's capabilities. System-at-a-glance visual layout, highlighted workflow paths, the Firewall in user-facing language. Build after command restructuring is settled.

### Pre-Skill Context Compaction

**Status:** Largely resolved by platform. 1M context on Opus 4.6 + Claude Code's built-in auto-compression. A dedicated pre-skill compaction hook remains a nice-to-have if Claude Code adds skill-lifecycle events.

---

## Writer-Question Surface Hardening

Continuing the v0.5 vision: the plugin should be organized around writer questions, not framework internals. The query-driven pass architecture and intake router shipped in v1.0, but the command surface, output naming, and skill boundaries still reflect build history. Evaluated in v1.3.0 — no user-facing pain found, but the surface can be cleaner.

### What to build

1. **Command taxonomy in release-registry.** Each command gets `category`, `status` (`primary` / `first_class_shortcut` / `compat_alias`), `router_equivalent`, and a plain-language writer question it answers. `/revision-plan` is the only true compat alias (→ `/coach`). All others stay first-class.

2. **Doc sync across all public surfaces.** Every public doc, README, help surface, and marketplace entry uses the same grouped command presentation generated from the registry. No more hand-maintained command lists.

3. **Canonical 8-block macro map.** Resolve Pass 4 ambiguity by giving Emotional Dynamics its own block permanently. The 8 blocks: Structure Map, Reader Dynamics, Character Architecture, Emotional Dynamics, Scene Delivery, Reveal Economy, Theme & Continuity, Submission Readiness. Source of truth in pass-dependencies.md.

4. **Pass-detail file headers.** Add a standard header to each pass artifact with `Macro block`, `Writer question`, and `Legacy pass id`. Makes a direct-opened file legible without framework knowledge.

5. **Results Guide artifact.** `[Project]_Results_Guide_[runlabel].md` — maps each writer question to the relevant artifacts, audits, and state files. First file after the editorial letter.

6. **Skill names scrubbed from user-facing copy.** Public copy describes workflows and next steps, not which skill is being loaded.

7. **Handoff language standardized.** Cross-skill transitions phrased as workflow moves: "run an audit next," "plan revision next," not "load specialized-audits."

### What not to build (yet)

- **Instrumentation.** APODICTIC-Gemini has a Cloud Run backend that could support event logging, but there's no current need for telemetry. Revisit when external users are active.
- **Filename renames.** Keep pass-numbered filenames on disk. The Results Guide is the primary macro-block organizer. Bulk renames deferred unless usage shows writers navigate by detail files.
- **Skill merges or renames.** Five-skill architecture stays. Skill loading is invisible to users. Evaluate only if handoff pain surfaces.
- **Editorial Letter renaming.** `Core_DE_Synthesis` and `Full_DE_Synthesis` work. Don't alias.

---

## Not Planned

- **Live project dashboard** — separate product, not a plugin feature
- **Prose execution mode** — violates the Firewall; explicitly out of scope
- **Line editing / copyediting** — different discipline, different tooling
- **Commercial viability guarantees** — the plugin diagnoses structure, not market outcomes

---

## Deferred (Empirically-Gated Decisions)

Decisions whose framework default is documented and conservative, but whose empirical re-evaluation requires fixture/token resources beyond a single release cycle. Re-evaluation triggers are named per item; the framework default holds until the trigger fires.

### Focus Map Architectural Decision — Empirical Test

**Source:** Phase 5 (test framework documented; runs deferred for resource reasons). Phase 7 Wave 3 (formalized as ROADMAP entry rather than running the test in this cycle).

**Current default:** Focus Map remains **hybrid-only**. Single-agent, sequential, and swarm modes do not produce a Focus Map. This is the conservative default per the model-capability review spec §Phase 5.

**Hypothesis + acceptance criteria:** Specified in `plugins/apodictic/skills/core-editor/references/hybrid-mode.md §Focus Map Architectural Decision Framework`. The acceptance bar requires improvement on ≥2 of {Severity Honesty, Audit Routing Coverage, Cross-Pass Connection Density, Author Usability} for ≥2 of 3 fixtures, with G1 (Cross-Pass Connection independence) and G2 (≥40% findings outside Focus Map) satisfied for all fixtures.

**Test scope:** 6 runs total. 3 fixtures (one literary fiction, one argument-shaped nonfiction, one short-fiction control) × 2 arms (control: current behavior; treatment: Focus Map produced in all four modes). Per Phase 5 design, the treatment arm preserves anti-overfit guards: in non-hybrid modes the Focus Map is analytical framing only, never gates manuscript access.

**Re-evaluation trigger:** Either (a) the canonical fixture corpus expands enough that the 6-run cost becomes worthwhile alongside other planned eval work, OR (b) Pass 10 Timeline integration with Focus Map raises the issue urgency (Pass 10's Timeline artifact may interact with Focus Map's pass-targeting in ways that force the cross-mode question). When triggered, run per the recording protocol in `hybrid-mode.md §Decision-recording protocol` and record the result + decision in a date-stamped review-log entry.

**Decision until re-evaluated:** Default holds. Focus Map stays hybrid-only.

---

## Deferred (Corpus Expansion Candidates)

Instructions whose framework status is "load-bearing under current evidence" but whose decision surfaces are not exercised by the canonical fixture corpus (F1 fiction-novella baseline-model run, F2 fiction-novella comparator-model run, F3 short-fiction control, F4 argument-shaped nonfiction). Per the model-capability review spec's UNPROVEN provenance rule, these are corpus-expansion candidates rather than deletion candidates: the instruction's effect is ambiguous due to fixture scope, not absent.

Surfaced by Phase 7 Wave 2 B1 eval coverage (`docs/.local/review-log/2026-04-25_phase-7-wave-2-eval-coverage.md`).

### State-lifecycle gardening thresholds (300/500 lines)

Framework instruction in `state-lifecycle.md` triggers gardening protocol when `state.md` exceeds 300 lines (warning) or 500 lines (forced gardening). Canonical fixtures don't reach the thresholds, so threshold-crossing behavior is not directly observed. Synthetic state-lifecycle fixtures at the 300/500 boundaries would exercise `validate.sh state-lines` threshold-crossing behavior and confirm gardening-trigger load-bearing.

### AI-Prose Calibration unexercised flag families (AIC-2 / AIC-4 / AIC-6 / AIC-8)

The AI-Prose Calibration audit defines flag families AIC-1 through AIC-8. F1-F4 exercise AIC-1 (Voice Singularity), AIC-3 (Echo Stack), AIC-5 (Puppet Dialogue), and AIC-7 (Discourse Leak). The remaining four families (AIC-2 Velvet Fog, AIC-4 Register Seams, AIC-6 Continuity Smear, AIC-8 Unearned Fluency) lack fixture coverage. A synthetic AI-heavy fixture (e.g., a deliberately AI-drafted prose sample with named-flag invocation targets) would exercise the unexercised families.

### Genre-specific tag audits (queer-romance, cozy, philosophical)

Tag audits for queer-romance-erotica, cozy-tag, and philosophical-tag are defined in `specialized-audits/references/tag/` but no canonical fixture invokes them. One ~500-word synthetic scene per genre territory would exercise tag-audit activation paths and confirm their findings vs. a no-tag baseline.

### Single-agent vs. multi-agent staging A/B fixture pair

Pre-Pass Re-Grounding and Staged Visibility instructions are mode-conditional. Their less-observable single-agent mode lacks a paired fixture for direct A/B observation. A synthetic A/B fixture pair (same scene, run in both modes) would exercise the mode-conditional instructions in their less-observable single-agent mode.

---

## Deferred (Out of Scope for This Cycle)

Items deferred from the Phase 7 closeout per scope-control. Each has a documented rationale; each is a candidate for a future cycle if a forcing function justifies the investment.

### Python helpers for true Timeline parsing (A3)

Phase 7 plan §A3 specified four Python modules (`timeline_parser.py`, `timeline_arithmetic.py`, `timeline_anchor.py`, `timeline_diff.py`) that would lift the documented bash-validator capability ceiling for Pass 10 Timeline verification. Recommended out of scope for this cycle because:

1. Substantial new tooling (4 modules + new test harness, ~870 lines)
2. No Phase 4-6 finding requires it as blocking; v1.7.9 honestly reframed bash validators as marker-hygiene / pre-labeled-surfacing checks
3. Pass 10 model judgment still does the primary verification; bash validators surface candidates for model judgment

Best-fit follow-on: a "Python tooling" minor cycle, contingent on a forcing function (e.g., recurring real-world false-pass case on novella-length manuscripts with complex chronologies).

### audit-signal-propagation §4e context-modifier extension

Phase 7 plan §A2 specified three optional validators; the third (`audit-signal-propagation §4e context-modifier extension`) was deferred per scope-control. The v1.7.9 validator uses a default mapping; this extension would make the propagation table fully driven by the `§4e` source of truth. Refinement, not missing capability. Defer to v1.9.x or until `§4e` table changes force a re-derivation.

### Codex `validateGeneratedWorkspace` allowlist maintainability

Wave 4 D2 host parity sweep finding 3: the codex build's `validateGeneratedWorkspace` function maintains a hard-coded allowlist of files where historical "Claude Opus" / `.claude-plugin/` references are intentional. Future framework additions with intentional historical references must update the allowlist by hand. Cosmetic / future-cleanup observation; defer until it bites.

### Canonical-framework validator runs as release gate

Surfaced by Codex final critique (P1, v1.8.4): the `audit-tier-criterion` validator passed its synthetic self-test but failed against the actual canonical `pass-dependencies.md` it was built to police. v1.8.4 closed the specific instance, but the *class* of failure remains: validator self-tests prove the validator works on its own fixtures, not that the canonical framework satisfies the validator. Currently the four release checks (`release-generate.mjs --check`, `build-codex.mjs --check`, `build-antigravity.mjs --check`, `release-verify.mjs`) plus per-validator `--self-test` invocations gate releases; canonical-framework runs (e.g., `validate.sh audit-tier-criterion plugins/apodictic/skills/core-editor/references/pass-dependencies.md`, plus analogous canonical runs for `decision-layer-check` against canonical fixtures, `audit-signal-propagation` against sample editorial letters, and `timeline-*` against canonical Timeline.md fixtures) are not part of the release-gate set. Adding a `release-canonical-checks.sh` orchestrator (or extending `release-verify.mjs`) to run validators against their canonical targets would catch the audit-tier-criterion class of overclaim earlier — before the next external review surfaces it. Estimated cost: ~50 lines of shell + ~5 canonical-fixture invocations. Defer until a forcing function (next minor cycle's release prep, or a second canonical-validator-mismatch finding).

### Clearer §4e table-driven propagation framing

Surfaced by Codex final critique (P3, v1.8.4): the current `pass-dependencies.md §4e` framing is sufficient for the present validator suite (per-audit propagation rules with default mapping for un-tabled cases), but could be sharpened with explicit table-driven language — naming each row's columns, formalizing the override-modifier column, and pulling the modifier semantics into the §4e header rather than the per-row prose. Pairs with the deferred `audit-signal-propagation §4e context-modifier extension` above: if/when the propagation table is fully driven by §4e source-of-truth parsing, the table framing should be sharpened first. Defer to whichever cycle picks up the §4e extension; not a release-blocker.

---

## Future Work

Forward-looking design patterns and trajectories surfaced during the 2026-04-24 model-capability review. These are not feature commitments; they are design lessons carried forward as discipline for future cycles.

### v1.9.x cycle considerations

Likely shape of the next minor cycle:
- **Corpus expansion** — synthetic fixtures for the four candidates listed in §Deferred (Corpus Expansion Candidates) above. Cost: synthetic-fixture authorship + per-fixture eval-coverage report.
- **Python tooling** — only if a real-world forcing function (e.g., recurring Pass 10 false-pass) justifies the toolchain investment. Otherwise skip.
- **Codex final-review adjudication outcomes** — if the Phase 7 Wave 5 Codex final review (drafted at `docs/.local/2026-04-25_codex-final-review-prompt.md`) surfaces P1 findings, v1.8.4 / v1.9.0 patches them. P0 findings would block before v1.9.x scope opens.

### Forward design patterns (from the review)

The review surfaced four reusable framework-design patterns. Each generalizes beyond its first application; future audits, validators, and pass artifacts can adopt them.

#### Structured-marker pattern for validator overrides

Where a mechanical validator would otherwise be tyrannical (correctly-failing on cases that author judgment should override), the override is a structured comment marker in the canonical artifact. The validator records the override but does not block. Used in `decision-layer-check`, `audit-signal-propagation`, and the timeline validators. Pattern generalizes to any future validator where author judgment must be allowed to override mechanical signal.

#### Condition-triggered vs. model-emergent gates

When the framework needs a behavior, the trigger conditions must be detectable — not "the model should notice." CR-6 (Underdiagnosis Retry Loop) was the canonical example: a model-emergent retry loop that fired for Opus and didn't fire for Codex on the same evidence. Phase 4 conversion to condition-triggered logic + `underdiagnosis-triggers` validator made the gate framework-honest. Discipline carries forward: any future gate of this class must be condition-triggered before it ships.

#### Pass-10-class rolling structured artifact pattern

Pass 10's Timeline.md is the first instance of a generalizable family: rolling project-root artifacts with structured schemas, diff'd across revisions by mechanical validators. Future passes facing cross-revision coherence challenges (cross-revision character voice consistency; cross-revision argument-state evolution beyond the existing `Argument_State.md`) can adopt the same pattern. Named in `core-editor/SKILL.md §Project Integration §Pass-10-Class Rolling Structured Artifacts`.

#### Propagation-table pattern as audit-coverage extension mechanism

`pass-dependencies.md §4e` propagation table maps audit-internal severity signals to synthesis-layer obligations. One row per audit; columns for signal type, signal level, synthesis-layer obligation, override condition. Future audits can be added by appending rows rather than rewriting framework rules. Pattern generalizes — analogous tables could cover audit precedence (CR-7 closure already uses a related rule), audit-tier promotion criteria (`§4c`), and audit-routing rules (`§4`).

### Methodology carry-forward

The bias-equalized parallel adjudication methodology developed during the review (cross-model fixture runs + per-side comparators + meta-comparison + manual ground-truth verification + per-phase done-gates) is now part of APODICTIC's development discipline. Documented in `docs/.local/blind-review-protocol.md` + `docs/.local/eval-harness-spec.md`. Any future model upgrade (Opus 5, Codex 6, Gemini 3, etc.) can be evaluated against the framework using the same pattern.

The fixtures in place (F1-F4) are reusable for future model-capability reviews. Corpus expansion (per §Deferred above) increases the methodology's reach without changing its shape.

---

## Done

### v1.9.0 — AI-Prose Calibration v2.0
Three-layer architecture extending the v1.0 audit. Layer A distributional pre-scan: variance_audit (single document), manuscript_audit (cross-chapter), repetition_audit (vocabulary diagnostic), eleven signals against personal/genre baseline with z-score band classification. Layer B named subtypes: AIC-2 Indefinite-Pronoun Gesture; AIC-7 Negation Hedge, Disguised Correctio, Pseudo-Aphorism, Manifesto Cadence. Argument-shaped nonfiction parallel set: Abstraction Shielding, False-Balance Construction, Hedge-and-Affirm, Recommendation Template, Authority Laundering. Layer C Source Triage Pass: payoff test, voice slip vs. lost callback distinction, earned-by-frame verdict. Cross-detector caveat for AIC-4 / Pangram signal-9 tension. Source-triage modifier table layered onto existing severity translation. v1.0 spec preserved verbatim — additions are integrative.

### v1.7.0 — Harness Engineering
Machine-readable sidecar state (`Diagnostic_State.meta.json`) with enumerated resume dispatch. Mechanical validation script (`validate.sh`) for contract integrity, ledger structure, artifact naming, and 14-heading synthesis section verification — bundled in plugin tree for Codex. Post-synthesis evidence spot-check (5 claims verified against manuscript). State gardening protocol (threshold-triggered archival). Enhanced `/start` resume gate with context-aware summary and state gardening trigger. Refactored `run-core.md` into three files: `run-core.md` (orchestration + pass specs), `run-synthesis.md` (audit integration, synthesis, deliverables), `state-lifecycle.md` (gardening, revision rounds). Cross-references updated across all callers.

### v1.4.0 — Surface Hardening & Writer's Block
Writer-Question Surface Hardening: command taxonomy in release-registry (11 commands with category/status/writer question), doc sync via release-generate, canonical 8-block macro map (Pass 4 → Emotional Dynamics), pass-detail artifact headers, Results Guide artifact, skill names scrubbed from user-facing copy, handoff language standardized. Writer's Block & Rut-Breaking module: 8-type expanded block taxonomy (replaces 3-way split), 7 structural prompt families, 5-part firewall test, clinamen clause, perfectionism modifier, nocebo inoculation, no-prompt zones, Structural Experiment session plan section, integrated into both fiction and argument coaching.

### v1.3.0 — Nonfiction Argument Engine & Genre Audits
Nonfiction Argument Engine: Dialectical Clarity v2.0 as kernel, Argument State Schema (v0.1.1), Red Team (12 flags, Distinguish Framework), Persuasion (12 signals, audience × form calibration), Evidence Deep-Dive (10 flags, form calibration, testimony handoff), Coaching Protocol (8 tracks, stuck-point diagnosis), nonfiction routing in intake. Supernatural Horror genre audit (25 flags, 7 dimensions, 8 subgenres). Grimdark / Dark Fantasy genre audit (22 flags, 7 dimensions, 6 subgenres).

### v1.2.1 — Audit Sequencing & Model Tags
Auto-run audits as synthesis dependencies (fixes multi-story collection sequencing bug). Model-tag required in output filenames.

### v1.2.0 — Artifact Coverage
Partial Manuscript Diagnostic (six stall causes, momentum report, setup inventory). Fragment Synthesis Mode (clustering, connection mapping, candidate structure). Router gaps filled for fragments and partial drafts.

### v1.1.3 — Coaching Deepening
Guidance Without Specification stance. Stuck-point block diagnosis (expanded to 8-type taxonomy in v1.4.0). Exercise library (6 exercises). Anti-chronological revision. Pause/Paraphrase/Probe.

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
