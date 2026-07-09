# APODICTIC Roadmap

**Current version:** See `plugins/apodictic/.claude-plugin/plugin.json`

---

## Board

*Reconciled 2026-07-02 against git tags + `fleet_inventory.py`: shipped capability lanes moved to their release versions in Done; In Progress / Planned now list only genuinely-open work.*

| In Progress | Planned | Done | Backlog |
|-------------|---------|------|---------|
| [Argument Benchmark Suite](#benchmark-suite) | [Multi-Party Intake](#multi-party-intake) | **v2.7.0** · **v2.6.2** · **v2.6.1** · **v2.6.0** *(sections below stop at v2.4.0; see git tags / CHANGELOG)* | [Model-Capacity Exploitation](#model-capacity-exploitation) |
| [Validation & External Evidence](#validation--external-evidence) | [Coaching Deepening](#coaching-deepening) | [**v2.4.0**](#v240--argument-engine-calibration-command-trim--legal-risk-wiring) | [Research / API Reliability Layer](#research--api-reliability-layer) *(M1 built; follow-ons deferred)* |
| | [Genre Audit Expansion](#genre--audit-expansion) | [**v2.3.1**](#v231--decoupled-ui-generation--host-bundle-distribution) | [Episode Cadence](#episode-cadence) |
| | | [**v2.3.0**](#v230--retcon-planning-legal-risk-register--nonfiction-pre-draft) | [Collaborative Revision Coaching](#collaborative-revision-coaching) |
| | | [**v2.2.0**](#v220--operator-modes-feedback-triage--revision-follow-through) | [Corpus-Expansion Fixtures](#deferred-corpus-expansion-candidates) |
| | | [**v2.1.0**](#v210--runner-governed-execution--finding-lifecycle-ids) | [Horizon Capacities](#horizon-capacities) *(Tier-1 fully shipped; Tier-2 mostly deferred)* |
| | | [**v2.0.0**](#v200--editorial-honesty--structural-integrity) | |
| | | [v1.9.0](#v190--ai-prose-calibration-v20) | |
| | | [v1.7.0](#v170--harness-engineering) | |
| | | [v1.4.0](#v140--surface-hardening--writers-block) | |
| | | [v1.3.0](#v130--nonfiction-argument-engine--genre-audits) | |
| | | [v1.2.1](#v121--audit-sequencing--model-tags) | |
| | | [v1.2.0](#v120--artifact-coverage) | |
| | | [v1.1.3](#v113--coaching-deepening) · [v1.1.2](#v112--revision-coach) · [v1.1.1](#v111--series-continuity--pass-9) · [v1.1.0](#v110--token-aware-agent-usage) | |
| | | [v1.0.9](#v109) · [v1.0.8](#v108) · [v1.0.4](#v104) · [v1.0](#v10--public-release) | |

**Now backfilled below (v2.6.0–v2.7.0):** **v2.6.0** — the Horizon Tier-1 wave (the Annotated-Manuscript deliverable + all its exports, plus the Tier-1 extraction audits); **v2.6.1** — audit carding + persona-divergence severity hardening; **v2.6.2** — override-marker SSoT hardening; **v2.7.0** — the state-seams wave (round-trip resume, finding dispositions, finding disconfirmation, synthesis re-grounding) + Multi-Session Arc Planning + the co-presence-network chart. See the [Done](#done) sections; git tags remain authoritative. *(There is no v2.5.0.)*

**Recently shipped (through v2.4.0):** **v2.3.0** — Retcon Planning (revision-coaching track), the Nonfiction Pre-Draft Pathway, the Legal Risk Register, Adaptive Mode de-escalation, and the Horizon Capacities scan. **v2.3.1** — decoupled web-app UI generation and research modes 4 → 6. **v2.4.0** — Manuscript-Structure Visualizations, Beta-Reader Instrument generation, the Legal Risk Register detection layer + router wiring, the routing fork/overlay split + project addressability, the Capability Index command (command surface trimmed to 13), and the Argument-Decision (ArgScope) audit with the SETEC normalized-dispatcher integration (vendor/pin/drift-gate); the release pipeline was also decoupled from the APODICTIC-Gemini sibling. *(Earlier — v2.2.0: Editor Scaffolding + Diagnostic Vocabulary operators, Feedback Triage, Adaptive Mid-Run Mode Escalation, Finding Lifecycle IDs incr 2–3.)* **Done and folded into shipped releases:** Runner-Governed Execution (incr 1–3 + 5; incr 4 future), Finding Lifecycle IDs (incr 1–3; incr 4 future), Validator Architecture Hardening, Adaptive Mode Escalation, Editor Scaffolding, Diagnostic Vocabulary, Feedback Triage. Pre-Skill Context Compaction is resolved by platform (see below).

---

## Validation & External Evidence

*Surfaced sharply by an external blind review (GPT, 2026-06-26): the framework's strongest objection is that its **validators verify process, not editorial truth** — they prove a letter is well-formed, severities are locked, and the ledger is consistent, but not that "this protagonist lacks an arc" is **correct**. The honest interim posture is the one the tool already takes — a structured second opinion; findings are hypotheses, not verdicts — and the contamination disclosures, the Distinguish Protocol, and the positive/specificity controls are real mitigations. The three evidence gaps below are named as standing work, not papered over. (Same review credited the project's unusual methodological self-criticism; this section is meant to keep earning that.)*

### V1 — Finding correctness, not just structural conformance

The mechanical layer (~59 validators) gates artifact structure, severity propagation, ledger integrity, and export correctness. None of it can tell whether a finding is *right, relevant, or helpful* — that is editorial judgment, and a system asked to hunt structural defects can always name one. The argument engine is furthest along on closing this (the [Benchmark Suite](#benchmark-suite): ground-truth diagnoses, sensitivity fixtures, specificity positive controls, the two-run convergence protocol). Gaps:
- **Second-editor confirmation** of the provisional ground-truth (GT4–GT8; GT1–GT3 authoritative) — the blind packet is built and waiting (`evals/fixtures/argument-benchmark/HANDOFF.md`).
- **The fiction passes/audits have no equivalent ground-truth benchmark.** Breadth (11 passes, dozens of audits) is the least-validated surface; the positive-control / specificity-guard design has not yet earned confidence across it. The bar is inter-rater agreement against human developmental editors on a labeled corpus.

### V2 — Auditable scorecard

Eval scorecards exist (`evals/results/*/SCORECARD.md`), but the corpus *bytes* are largely gitignored — a deliberate provenance choice (copyrighted op-eds/manuscripts can't ship in-repo), not concealment. The cost is that the claimed performance is not straightforwardly externally auditable. Open work: publish a **committed, reconstructable scorecard** on the [shippable-kit model](#benchmark-suite) — keys + harness + protocol + SHA-pinned fetch instructions ship; the bytes reconstitute locally — so a third party can re-run and check the numbers without the repo hosting copyrighted text.

### V3 — Blind demonstration

Every public sample (DCC, *Theo of Golden*, ACOTAR, Kleiman's *When Brute Force Fails*) is a known, published work with a disclosed contamination risk — they demonstrate *presentation quality and reasoning transparency*, not *blind editorial discovery on an unseen manuscript*. Open work: at least one **blind sample** — a permissioned unpublished manuscript, or a sufficiently obscure / post-training-cutoff text — run cold and published, so the examples can show independent discovery rather than recall.

### Positioning until these close

The tool is correctly positioned as a disciplined **structured second opinion**, not an authority. The recent Firewall-honesty pass and the "findings are hypotheses" framing are the right interim stance. These three workstreams are what would move it from *well-engineered and self-audited* toward *externally validated*.

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
10. Position-Pair Register (v0.1) — consumer of SETEC's `position_pair_register` surface: a relation-free register of passage PAIRS in a nonfiction work that address the same question Q, in document order; the human reads both and owns the entire conflict call (the fleet's deliberate NON-step across the content-verdict wall — the consumer derives nothing, runs gates only). Vendor/pin/drift-gate + the Q1 banned-key walk / Q2 verbatim-with-F1-fold / A3 firewall / F5 framing-prose / document-order validator. Anchored to ContraDoc (arXiv:2311.09182) + BeliefShift (arXiv:2603.23848). Consumer gated on SETEC v1.121.0.

**In progress**

1. Argument Engine Benchmark Suite — spec + vertical slice landed (see below)

### Benchmark Suite

Validate that the engine works on real argument-shaped nonfiction, not just in theory. Corpus-based testing against manuscripts where the correct structural diagnosis is already known.

**Status:** Spec landed at [`docs/argument-benchmark-spec.md`](docs/argument-benchmark-spec.md). Vertical slice (Increment 1) built: rubric ([`evals/rubrics/argument-benchmark.md`](evals/rubrics/argument-benchmark.md)), ground-truth answer-key template ([`evals/argument-groundtruth-template.md`](evals/argument-groundtruth-template.md)), and four pre-registered fixtures under [`evals/fixtures/argument-benchmark/`](evals/fixtures/argument-benchmark/) — two broken (op-ed warrant leap; uncompared policy brief) for sensitivity, two positive controls (narrative-argumentation personal essay; Swift's *A Modest Proposal*, referenced) for specificity. Corpus is synthetic + public-domain (provenance policy blocks shipping copyrighted op-eds/testimony in-repo); real modern fixtures are added by gitignored manifest.

**Status (Increment 2–3):** The **two-independent-runs convergence protocol has been run across the full corpus** (Opus + Sonnet on all referenced + synthetic + public-domain fixtures, plus a cross-vendor GPT-4 pass), scored, and recorded in `evals/results/*/SCORECARD.md`; buckets 1, 2, 5, 6, 7 are covered by the referenced corpus (`CORPUS.md`). The runs drove a Dialectical Clarity calibration fix (the severity floor) and a **Step-6 decoy-resistance fix** (6a two-test procedure + FM-A20).

**Direction — shippable kit (the distribution model).** The copyrighted source *bytes* are the only thing that can't ship; the keys, harness, protocol, and method all can. So the benchmark ships as a kit and reconstitutes copyrighted texts locally (URL + extraction anchor + SHA-256; never the bytes).
- ✓ **Public-domain core** (fetchable, not stored): *Federalist* No. 10 (bucket 5 positive control, Gutenberg) and Douglass, *What to the Slave Is the Fourth of July?* (bucket 3 / testimony + Q7 unconventional-form control, archive.org pinned). Both verified via `run.sh --fetch`.
- ✓ **`run.sh --fetch`** reconstitution mode — pulls each referenced source from its pinned URL and verifies the recorded hash.
- ✓ **`validate.sh argument-groundtruth-check`** key-conformance validator (`scripts/argument_groundtruth.py`, shipped v2.1/2.2): GT1–GT8 coverage (GT schema v0.2.0), DC code-namespace resolution, GT2 locus↔code consistency, GT7 warrant verdict + GT8 premise-plausibility flags — **extended to FM-A20** for the decoy-resistance pattern.
- **Remaining:** second-editor confirmation of GT4–GT8 (GT1–GT3 authoritative; GT4–GT8 provisional) — see **Next round** below.

**Next round (after the convergence runs, PR #37).** Grouped by what each needs:

*Substantive (engine / key — the next calibration round):*
1. ~~**Strengthen Test A** (the genre-genericity decoy filter).~~ **Run-confirmed 2026-06-11 (PR #72):** mechanism was already complete; the benchmark run had both models downrank "but public safety" as the decoy (**OB5**) on `ppi`. No edit needed.
2. ~~**`policy-brief-uncompared` under-fire fix.**~~ **DONE / benchmark-validated 2026-06-11 (PR #72):** added classification **rule 2a** (an AT3 recommendation with wholly-undischarged comparative burden → Structurally Unsound, FM-A10), then narrowed it post-benchmark so a strawman foil counts as partial discharge (soft spot), not a defeat. See `docs/argument-benchmark-calibration-round.md` → Status.

*Human-gated (ready — just needs people):*
3. **Recruit one second editor** — the GT4–GT7 / personal-independence upgrade. The blind packet is built and waiting in Dropbox (`argument-benchmark-second-editor-packet/`, with its own `TODO.md`); pointer in `evals/fixtures/argument-benchmark/HANDOFF.md`.
4. **`current-affairs` GT2** (flagged recall-suspect on a cross-vendor split) — resolves via #3, or via a second vendor.

*Minor / optional:*
5. **PDF `--fetch` (AECF)** — currently fails loudly with a manual path; add a `pdftotext` branch if PDF fixtures multiply (flagged in PR #37, non-blocking).
6. **Cross-vendor n=1** — `roosevelt`'s clean GPT flip is strong but single-run; a second GPT pass would kill any "it was variance" objection. Optional hardening.
7. **Housekeeping** — the merged `claude/benchmark-corpus-round2` branch can be deleted (nothing depends on it; the Dropbox artifacts are independent).

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

### Retcon Planning — **Built (Increment 1 + F1 + F2 + F3)**

A revision-coaching track for the retroactive-continuity work a late structural decision owes the earlier draft. Two entry doors — a committed late decision → **setup-debt ledger** (run reveal economy backward), and a latent **"bug-or-feature" reinterpretation** — unified by a **commitment budget** (locked/costly/free) and a **fair-play rule** (dramatic retcon for meaning allowed; evidential retcon of canon the reader has reasoned from forbidden). Firewall-bound: the coach plans the retcon and budgets the commitments; the author writes the tissue. Lineage: Gwern's *Better Fiction via Retcon Planning* (latent-world + commitment budget) merged with this project's setup-debt framing. Enforced by the `retcon-plan` validator (R1–R4 + advisory W1/W2; the signature checks are R3 no-evidential-retcon-of-locked-canon and W2 firewall-drift) over `apodictic.retcon_item.v1` blocks, with a canonical `--check-all` gate. Validators 23 → 24. Spec: [`docs/retcon-planning.md`](docs/retcon-planning.md).

**F1 — Ranked Door-B abduction (built).** The Door-B bug-or-feature move no longer hands the author a flat menu: candidate latent readings are **scored and ranked** to a costed top-1–3 shortlist as `apodictic.retcon_reading.v1` blocks in a `## Candidate Readings` section. The rubric is five 1–5 dimensions — canon coherence, payoff density, agency preservation, genre fit, and **coincidence resistance** (the structural guard against "rubber reality" / paranoid over-fitting — the failure mode the essay names). The `retcon-plan` validator gained R5 (reading schema + score rubric), R6 (unique reading ids), R7 (reading-target referential integrity), **W3** (the coincidence-note over-fitting guard — the signature F1 check) and W4 (top-1–3 shortlist), plus a ranked-by-total display; same validator (count stays 24). Firewall unchanged — readings are options, never prose.

**F2 — State Card rolling artifact (built).** The State Card is promoted from a `## State Card` section to a standalone, structured, **rolling** project-root artifact `[Project]_State_Card_[runlabel].md` (`apodictic.state_card.v1`, one block per round), **diff'd across revision rounds** (the Pass-10-class rolling-structured-artifact pattern). Tracked elements (promises/tensions/contradictions) share one kind-agnostic `SE-NN` id, so the same element is followed across rounds even when it changes kind. New `state-card-diff` validator (modeled on `timeline-diff`): single-card S1/S2 and cross-round S3/S4 + W1–W3, with **S4 promise→contradiction** the signature coherence-break check (matched by id, so it survives rewording). Validators 24 → 25.

**F3 — Pass-8 source provenance (built).** Closes the Pass-8 (Reveal Economy) → Retcon-Plan loop: `apodictic.retcon_item.v1` gains an optional `source` finding-ref (primarily a Pass-8 finding, e.g. `F-P8-03`) so a seeded setup-debt item's provenance is auditable. Format is validated by the schema and shown in the `retcon-plan` item line; **`finding-trace` E6** resolves the `source` against the Findings Ledger (a dangling source is an error). The check lands in `finding-trace` (the cross-artifact `F-…` owner) rather than rebuilding ledger access in `retcon-plan`; no new validator (count stays 25). **Remaining future increment** ([`docs/retcon-planning.md`](docs/retcon-planning.md) §Future increments): F4 an interactive-fiction / game-narrative diagnostic (speculative, demand-gated — build only if IF/game manuscripts materialize).

### Multi-Session Revision Arc Planning — **Built**

Session Planning operates one session at a time; Loop Dispatch picks the single next action. **Arc Planning** is the layer above: a phased multi-week strategy — **Phase 1** structural root causes → **Phase 2** downstream consequences → **Phase 3** polish — that sequences the full Findings Ledger and feeds the per-session planner (it does not re-run Loop Dispatch). It **generalizes** Retcon Planning's single-decision arc (above — a dependency-ordered arc rooted in one late decision) to the whole Ledger. Firewall-bound: the coach **SEQUENCES findings; it never prescribes execution**. New `apodictic.revision_arc.v1` schema (one block per manuscript; `phases` an **ordered list ≥1**, no fixed 3-enum, so 2- and 4-phase arcs are absorbed; **stateless re-plan** — regenerated each run from the current `finding_states`, overwriting the prior arc, no round/version field, like Loop Dispatch) + the `multi-session-arc-planning.md` skill (revision-coach mode 8) + `docs/multi-session-arc-planning.md` + the canonical `example-revision-arc.md` `--check-all` gate.

**Honest posture (the Retcon pattern).** The Root-Cause mapping is **not machine-readable** (`finding.v1` carries only structured `severity`; the diagnostic-state root-cause map is prose), so the coach's dependency reasoning is **trusted, not gated**. The new `revision-arc` validator gates the PLAN's **provenance + self-consistency + firewall only**: **A1** schema + nested phase shape, **A2** provenance closure (every `finding_ref` resolves to a real Ledger finding), **A3 self-consistency ONLY** (each finding in exactly one phase; a Must-Fix finding the arc *itself* labels a structural root cause is not parked in the polish phase — explicitly **not** a true-causal-graph check), **A4** non-empty sequencing rationale; advisory **W1** firewall-drift and **W2** orphan (a Must-Fix Ledger finding absent from the arc). Validator count stays **derived** from `AGG_VALIDATORS`.

### Genre-Specific Coaching Calibration

Adjust coaching behavior by genre: romance coaching emphasizes emotional-arc leverage; thriller coaching emphasizes pacing-first sequencing; literary coaching allows longer stuck-point exploration. Builds on the existing genre module system.

### Writer's Block & Rut-Breaking — **Built (v1.4.0)**

8-type expanded block taxonomy (replaces 3-way split), 7 structural prompt families (Constraint, Inversion, Isolation, Scale-shift, Perspective, Deletion, Temporal), 5-part firewall test, perfectionism modifier, nocebo inoculation, no-prompt zones, Structural Experiment session plan section. Integrated into both fiction and argument coaching protocols.

### Coaching History and Pattern Recognition — **Built (Increment 1, v1 scope)**

Over multiple revision cycles, surface patterns: "You tend to defer character-agency work — three consecutive session plans without completion." Privacy-sensitive — observations, not judgments.

**Built.** APODICTIC's ONE ethically-sensitive surface, shipped with the two Fable conditions (2026-07-05) mechanized as the load-bearing gates. A rolling, **opt-in**, local-only `[Project]_Coaching_History_[runlabel].md` of `apodictic.coaching_observation.v1` blocks, each **mechanically derived from recorded session history** (a count over `execution.finding_dispositions` / the revision-arc phases, never a vibe) and carrying **no editorial severity** (no Must/Should/Could token, no `apodictic:finding` block). v1 ships the two patterns derivable from data that exists today — `deferral-recurrence` (the same finding `deferred` across an unbroken run of `finding_disposition.session` ordinals, floor ≥3) and `phase-incompletion` (a revision-arc phase open across ≥2 consecutive sessions); `stuck-point-cluster` / `completion-drift` are deferred to v2 (they need a session-plan / stuck-family taxonomy that does not exist yet). Enforced by the `coaching-history` validator (H1 schema+floor, H2 provenance/anti-fabrication with a consecutive-session proof, H3 descriptive-not-judgmental, H4 no-severity-leak, H7 tentative-framing/transference-health floor, W1 local-only) plus the two ethics gates: **H5** single-home / no coach-only shadow (project root + `runs/*` + the machine-facing sidecar; a projection outside the one artifact, a second artifact, or sidecar coaching material beyond `coaching_history_seq` = non-overridable ERROR) and **H6 + the `delete <project_root>` subcommand** (deletion honored, RECOMPUTED not trusted — the PR #161 recorded-field rule; residue = ERROR, no override). Canonical `example-coaching-history/` project wired into `--check-all` under `--strict` (positive + five hostile ethics-gate arms + a delete round-trip); the `revision-coach` skill contract §9 carries the human-terminus obligations (opt-in gate, single-home / no-projection, tentative-noticing presentation, surface-the-delete). Spec: [`docs/coaching-history.md`](docs/coaching-history.md). This completes the **[Coaching Deepening](#coaching-deepening)** pair with Multi-Session Revision Arc Planning.

---

## Operators

### Editor Scaffolding — **Built (Increment 1 + Dual-output)**

For human developmental editors using the framework as analytical assist. Output framing shifts to "here's what I found that you might have missed." Suppress prescriptive language, add blind-spot emphasis.

**Built.** The `operator:editor` routing gap is closed (intake router → `references/editor-scaffolding.md`). The mode is a superset overlay on the Core DE editorial letter: an **Editor Brief** addressee reorientation, a required **What You Might Have Missed** blind-spot section, and an **Intervention Menu (editor's discretion)** that defers the author-facing prescription to the human editor — while severity honesty, the Firewall, and the decision layer are preserved unchanged. Enforced by the `editor-scaffolding` validator (E1–E4 + advisory W1), conditional on a `<!-- mode: editor-scaffolding -->` marker, with a canonical `--check-all` gate proving it composes with `decision-layer-check` / `severity-floor`. **Editor ↔ author dual-output built:** the same validator's `editor-scaffolding --dual <editor_letter> <author_letter>` arm validates one diagnosis emitted as *both* letters — D1 editor side (E1–E4), D2 author register (no editor marker / no editor-only sections + a Revision Checklist anchor; the framework still never authors the prescription — Firewall preserved), D3 top-severity-band consistency across the pair — gated in `--check-all` over a canonical editor+author example pair (validator count unchanged, no new validator). Spec + ownership boundary: [`docs/editor-scaffolding.md`](docs/editor-scaffolding.md). Validators 21 → 22 (dual-output adds no validator). **Future increments:** per-pass scaffolding, blind-spot ranking by severity-vs-salience gap. The sibling operators (Diagnostic Vocabulary Mode, Multi-Party Intake) remain separate gaps.

### Diagnostic Vocabulary Mode — **Built (Increment 1)**

For writing group facilitators who want to teach structural feedback vocabulary. Glossary/cheat sheet output, discussion prompts tied to structural concepts.

**Built.** The `operator:facilitator` routing gap is closed (intake router → `references/diagnostic-vocabulary.md`). Facilitator mode produces a `[Project]_Vocabulary_Guide_[runlabel].md` teaching aid alongside the editorial letter: a **Glossary** of the structural concepts the diagnosis used (each grounded in a specific manuscript spot) and a **Discussion Prompts** section that frames issues as questions for the group. The author-facing letter keeps its severity record — the Guide is a teaching companion, not a softer letter. Enforced by the `diagnostic-vocabulary` validator (V1 glossary present, V2 entries defined, V3 ≥3 grounded, V4 ≥3 prompts all questions; W1 prescription-leak advisory), conditional on a `<!-- mode: diagnostic-vocabulary -->` marker, with a canonical `--check-all` gate. Spec: [`docs/diagnostic-vocabulary.md`](docs/diagnostic-vocabulary.md). Validators 22 → 23. This completes the **operator pair** with [Editor Scaffolding](#editor-scaffolding); the remaining operator, **Multi-Party Intake** (`operator:team`), stays a gap. (Rule-of-three: if it lands, extract the shared operator-mode prose helpers into one module then.)

### Multi-Party Intake

For co-authoring teams. Priority conflict resolution, sign-off workflow, change ledger. Build only if user feedback indicates need.

---

## Workflows

### Feedback Triage — **Built (Increment 1, v2.2.0)**

Writers returning with beta reader or critique group feedback. Sort, validate, and prioritize external feedback. Targeted pass execution to test specific claims, conflict resolution when feedback contradicts itself.

**Built.** Lives in the revision-coach skill (`/triage-feedback`, `revision-coach/references/feedback-triage.md`). Each note is a real-JSON `apodictic.feedback_item.v1` block (orthogonal `assessment` truth axis × `triage` disposition axis) in a `[Project]_Feedback_Triage_[runlabel].md` artifact, checked by the `feedback-triage` validator (contract hygiene + conflict referential integrity + the contradiction-coherence gap). Design: [`docs/feedback-triage.md`](docs/feedback-triage.md). Future increments: targeted-validation automation; deeper coaching handoff.

### Nonfiction Pre-Draft Pathway — **Built (Increment 1: argument spine; 2: source/evidence map; 3: warrant pre-check; 4: scene-ethics plan)**

Argument spine + source/evidence map + scene ethics plan. Separate from fiction pre-writing because nonfiction structure is thesis-driven, not character-driven.

**Built (Increment 1 — argument spine).** A thesis-driven pre-writing mode (homed in `pre-writing-pathway`) that captures the **argument spine** before a draft exists — thesis, claim ladder, and the **anti-thesis** (the opposing view the argument must defeat) — as an `apodictic.argument_spine.v1` block, and **seeds the shared `Argument_State.md`** (§1/§2 + §6 Objection 1) so the Dialectical Clarity audit and companion modules consume one contract (no parallel schema, no conversion step). Enforced by the `argument-spine` validator: A1 schema (AT0–AT4 / burden / audience enums, ≥1 subclaim), **A2 unseeded** + **A3 thesis/C0 drift** (the signature seed-`Argument_State` integration checks), W1 anti-thesis echo (name a genuine opposing view, not a restatement; overridable). Canonical `--check-all` gate over a worked pre-draft `Argument_State.md`. Validators 33 → 34. Spec: [`docs/nonfiction-pre-draft.md`](docs/nonfiction-pre-draft.md).

**Increment 2 — source/evidence map (built).** Per subclaim, the writer plans the **intended support** as `apodictic.support_plan.v1` blocks that seed §3 Support Map; a subclaim with no planned support is a **bare assertion** the validator surfaces *before* drafting. Extends the `argument-spine` validator: A4 support-plan schema, A5 each plan attaches to a declared `Cn` subclaim, A6 the support map seeds §3 (parallel to A2), and **W2 bare assertion** (staged — fires only once support planning has started, so a spine-only artifact is never nagged). Same validator (no count change). Firewall unchanged (plan which evidence to bring; never invent it).

**Increment 3 — warrant pre-check (built).** Per subclaim, the writer plans the **warrant** (the principle connecting support to claim) as `apodictic.warrant_plan.v1` blocks that seed §4 Warrant and Inference Map. Extends `argument-spine`: A7 warrant-plan schema, A8 dangling subclaim_id, A9 the warrant map seeds §4, and **W3** — **audience-calibrated**: for a HOSTILE audience (per the spine's `audience_receptivity`), a non-`EXPLICIT` or `ABSENT`-backed warrant is flagged to make explicit and back before drafting (a no-op for non-hostile audiences). Same validator (no count change). With Increments 1–3 the pre-draft seeds the **Toulmin core** — claims (§2), grounds (§3), warrants (§4).

**Increment 4 — scene-ethics plan (built).** For narrative nonfiction / memoir depicting identifiable real people, the writer's pre-draft **ethical** plan — consent status, handling (as-is / anonymize / composite / seek-consent / omit), fairness reasoning — as `apodictic.scene_ethics.v1` blocks in a *distinct* artifact `[Project]_Scene_Ethics_Plan_[runlabel].md`. Per the maintainer's design decision, it is a distinct artifact that **coexists with and cross-references the Legal Risk Register** (ethics here; legal exposure there, via `legal_ref`), not folded into it. New `scene-ethics` validator: E1 invalid item, E2 duplicate id, **W1 unresolved depiction** (as-is + consent not-sought + no fairness rationale — the signature), W2 no legal cross-check (an as-is depiction with no `legal_ref`). Validators 34 → 35. Firewall: the writer makes the ethical calls; the plan surfaces unresolved depictions — not ethical adjudication, not legal advice.

### Legal Risk Register — **Built (Increment 1)**

Defamation concerns in memoir/autofiction, privacy issues for identifiable individuals, rights clearance flags. Produces a legal risk register with severity levels and escalation triggers. "I'm flagging areas that may need legal review. I am not a lawyer."

**Built (Increment 1).** A workflow that **flags** a manuscript's legal-exposure areas — `defamation` / `privacy` / `rights-clearance` / `other` — each as an `apodictic.legal_risk.v1` block with a **legal-escalation severity** (`monitor` / `review-recommended` / `review-now`, kept orthogonal to the editorial Must/Should/Could scale) and an escalation trigger, in a `[Project]_Legal_Risk_Register_[runlabel].md` artifact. The module firewall is **flag, don't practice law**: it never adjudicates. Enforced by the `legal-risk` validator (L1 schema, L2 unique ids, **L3 not-a-lawyer disclaimer present**; **W1 legal-advice drift** — a legal conclusion where a flag belongs, overridable — and W2 a `review-now` item not routed to counsel), with a canonical `--check-all` gate. Validators 24 → 25. Homed in core-editor; spec: [`docs/legal-risk-register.md`](docs/legal-risk-register.md). **Built since:** the `/legal-risk` command + `constraint:risk` intake routing (offer-then-attach); the **detection layer** — per-class detection guidance + a standard escalation-trigger taxonomy (`references/legal-risk-register.md` §Detection guidance / §Escalation-trigger taxonomy), synthesized from cross-model research ([`docs/legal-risk-detection-level-setting.md`](docs/legal-risk-detection-level-setting.md)); the **content-detection auto-recommend** — the register is auto-offered for memoir / autofiction / real-people *without* an explicit `constraint:risk`. Per the maintainer's decision this last one is **prompt/router-only** (model-side detection in the synthesis/routing prose; **no new validator**, no validator-count change): `run-synthesis.md §Content-detection auto-recommend`, `references/legal-risk-register.md` §Auto-recommend, `intake-router-runtime.md` §3/§6, `pass-dependencies.md §4a`. **Future increments:** none currently planned.

### Episode Cadence

For web serial and newsletter fiction writers. Hook debt tracking, recap burden analysis, season pivots, retention checkpoints. Each installment must work standalone AND advance the series.

### Collaborative Revision Coaching

For co-authoring teams or author-editor pairs working through a diagnostic together. Priority conflict resolution, sign-off workflow, change ledger. Build only if demand materializes.

---

## Project Addressability & State-Driven Routing

APODICTIC already persists durable per-project state — `Diagnostic_State.md` + the `Diagnostic_State.meta.json` sidecar, `SYNTHESIS.md`, and the README run-archive manifest, all at a project root initialized by `/new-project` (`references/output-structure.md` §Folder Architecture). What it lacks is **addressability**: the "active project output context" is *ambient* (whatever folder the host happens to be in), so a writer carrying several books cannot point the tool at one by name and resume where they left off. This capability makes a project a named, selectable entity and promotes the sidecar from a resume-time fallback to the *primary* routing input — `/start` reads *where you are* instead of re-interviewing you, and the intake router's route map becomes a lifecycle transition graph rather than an Artifact×Goal lookup grid.

The increments form a dependency graph (not a single line): **{1, 2} → 3 → 4**. Increments 1 and 2 are independent and can be built in either order or in parallel; both feed Increment 3; Increment 4 follows 3 and *also* requires a gated `revision_round` phase (see spec, B1). Detail and rationale in [`docs/project-addressability.md`](docs/project-addressability.md) §Dependency chain.

**Increment 1 — Router fork/overlay split. — Built.** Separate workflow-*selecting* modifiers (forks: `time`, `nonfiction`, `feedback`, `team`) from workflow-*modifying* ones (overlays: `ai`, `editor`, `facilitator`, `risk`, `hybrid`, `swarm`), so overlays compose orthogonally instead of multiplying route-map rows. Gates Increment 3 specifically: a transition graph cannot carry the full modifier cross-product at every node. **Built:** `intake-router-runtime.md` §3/§3a/§6 (route map split into Table A base routes + Table B overlays; nine `base × overlay` rows removed) + `intake-router-design.md` axis-model/output-contract correction; `validate.sh --check-all` green. Design rationale: [`docs/router-fork-overlay-split.md`](docs/router-fork-overlay-split.md).

**Increment 2 — Project registry & session binding. — Built.** A canonical project registry homed outside the plugin repo (workspace-relative `.apodictic/registry.json`), with each project root's sidecar as the canonical self-description and the registry as a recomputable cache (the same canonical-log / recomputable-pointer discipline as [Runner-Governed Execution](#runner-governed-execution)). `/start <project>` and `/projects` bind/list. **Built:** schemas `apodictic.project_registry.v1` + `apodictic.project_entry.v1`; `validate.sh registry-check` (R1–R4; validators 35 → 36, `--self-test-all` 36/36); `/projects` command + `/start` Step 0 binding + `/new-project` registration; pre-writing minimal sidecar. Spec: [`docs/project-addressability.md`](docs/project-addressability.md).

**Increment 3 — State-driven dispatch. — Built.** Promote the sidecar `next_action` dispatch table (formerly the `/start` resume *exception*) to the *primary* routing path. For a bound, in-progress project the artifact and goal axes are known from the contract and sidecar, so the intake questions collapse to a two-option Resume/Start-fresh prompt; cold-start still runs the questionnaire. **Built:** `lifecycle-node` validator (total node derivation by precedence, 36 → 37, root-mirrored); `start.md` Step 0.5 (`next_action`-as-primary + scoped contract-hash precondition); `intake-router-runtime.md` §6 lifecycle transition table (Table A reframed as the cold-start entry map); `readiness[]` sidecar mirror for the `submission` node. Spec: [`docs/project-addressability.md`](docs/project-addressability.md).

**Increment 4 — Revision-loop-as-spine. — Built.** With a bound project and state-driven dispatch, the diagnose⇄coach⇄execute⇄verify loop becomes the resumable spine: a "what now?" dispatcher that reads `execution.finding_states` (locked→delivered→revised), resolved markers, and `revision_progress`, then proposes the next leverage action instead of waiting for the writer to recall the right command. **Built (4b):** the leverage ladder in `revision-coach/SKILL.md` §Loop Dispatch + `start.md`'s `revising` dispatch. **Built (4a):** a gated `revision_round` phase that folds `revised` into the sidecar `finding_states` for runner-governed projects (marking only the resolved subset), with the revision round's direct write *scoped* to non-governed projects so the `pointer == fold` invariant holds. Spec: [`docs/revision-round-gate.md`](docs/revision-round-gate.md), [`docs/project-addressability.md`](docs/project-addressability.md). This is the substrate the [Coaching Deepening](#coaching-deepening) items (Multi-Session Revision Arc Planning, Coaching History and Pattern Recognition) and [Collaborative Revision Coaching](#collaborative-revision-coaching) currently lack — none has a home for project identity or loop position.

### Follow-ups (post-Increment-4)

Small, independent items surfaced during the Increment 1–4 build + reviews. Neither blocks anything; each is a clean standalone change.

- **Legal Risk Register router wiring — Built.** `constraint:risk` now offers + attaches the Legal Risk Register overlay (synthesis constraint hook, `run-synthesis.md §Constraint mode`), plus a `/legal-risk` direct command. Route-map status flipped to Built (§3 D / §6 Table B / §4a).
- **Legal Risk Register content-detection auto-recommend — Built (prompt/router-only).** The register is now auto-offered for memoir / autofiction / nonfiction portraying identifiable real people *without* the explicit `constraint:risk` flag — model-side detection in the synthesis/routing prose (`run-synthesis.md §Content-detection auto-recommend`, `references/legal-risk-register.md` §Auto-recommend, `intake-router-runtime.md` §3/§6 Table B, `pass-dependencies.md §4a`), the maintainer's chosen design over a mechanical validator (no new validator, no validator-count change). Offer-then-attach, explicit confirm; flag-don't-practice-law firewall intact.
- **`finding-trace` completion-glob narrowing — Built.** `_COMPLETION_GLOBS` narrowed to `*_Revision_Report_*.md` (was `*_Revision_*.md`), so a deadline-coaching `*_Revision_Calendar_*.md` is no longer mis-classified a completion — aligned with the Increment-4a gate. Negative-test guarded.

**Status:** Increments 1–4 **built** (router fork/overlay split; project registry + binding; state-driven dispatch; revision-loop spine incl. the gated `revision_round` phase). All three post-Increment-4 follow-ups above built (router wiring; the content-detection auto-recommend, prompt/router-only; `finding-trace` glob narrowing), plus the **project-dashboard artifact** (`plugins/apodictic/project-dashboard.html` — snapshot viewer + launcher). The Legal Risk Register is now built through content-detection auto-recommend (both the flag-driven attach and the no-flag content offer); see `intake-router-design.md` § remaining gaps.

---

## Harness Engineering

The trajectory from "a brilliant prompt stack" toward an editorial operating system. These build directly on the v2.0.0 structural-integrity work (#10–#14) and extend the forward design patterns surfaced by the model-capability review (see §Future Work → Forward design patterns). The first three are the priority set; together they move enforcement out of the prompt and into the harness.

### Harness Contracts v2

Make JSON Schema the source of truth for every structured artifact — findings (`apodictic.finding.v1`), audit triggers, readiness verdicts, deficit locks, severity-calibration entries, sidecar state (`Diagnostic_State.meta.json`), and runner events. Markdown stays the author-facing surface, but is generated from — or validated against — those contracts rather than hand-authored in parallel. Generalizes the v2.0.0 Phase-3 move (real-JSON `apodictic.finding.v1` + `structured_findings.py`) from one block type to the whole artifact set, and gives Validator Architecture Hardening a single shared schema to enforce.

**Built (the completion increment), 2026-06-21.** Spec + build doc: [`docs/harness-contracts-v2.md`](docs/harness-contracts-v2.md). The per-artifact generalization had already shipped incrementally (all 22 `apodictic.*` artifact schemas exist and each is bound to a Python validator through the shared `apodictic_artifacts.py` subset engine); what was missing was the *enforcement that this stays true*. This increment ships that keystone: the `schema-coverage` validator (`scripts/schema_coverage.py`) proves disk reality matches a declarative `schemas/_coverage.json` binding table at `--check-all` (no orphan/phantom schema; every binding grep-proven against its bound script; every canonical-gate file actually exercised; closed-key table↔file agreement), opt-in **closed-key (`additionalProperties:false`)** enforcement in the engine — the misspelled-field kill — with the six flat const-tagged blocks closed (`finding.v1`/sidecar/`gate_event` stay open by design), and an advisory docs-no-re-list prose lint. A YAML→schema *generator* was considered and rejected (it would add a second source and create the drift this removes). Self-testable validators 50 → 51. No model seam — pure stdlib harness mechanics.

### Runner-Governed Execution

A lightweight runner that owns execution state — current phase, required artifacts, sidecar state, pending gates, fired retry triggers, allowed next actions — and enforces the ordering the model currently self-polices (*"you cannot synthesize until the Findings Ledger exists and the Deficit Lock / underdiagnosis gates pass"*). The model still does all the reasoning; the runner makes the gates non-optional. This is the most ambitious remaining step of the original prompt-governed → runner-governed direction, and the successor to the *condition-triggered vs. model-emergent gates* discipline (§Future Work): condition-triggering made the *triggers* detectable; the runner makes the *enforcement* external.

**Built (increments 1–3 + 5; shipped v2.1.0). Increment 4 SPLIT: cooperative slice built / external host orchestrator deferred with triggers.** Spec + increment plan at [`docs/runner-governed-execution.md`](docs/runner-governed-execution.md). Increments 1–3 (cooperative gate manifest + engine + sidecar state + finding-ID lifecycle) **and increment 5 — structured gate-event records** are **built, shipped in v2.1.0**: history-only append-only `execution.gate_events[]` as the canonical record (the v1 per-phase `gates` map dropped as derivable), a stored-event-vs-derived-label lifecycle vocabulary, a recomputable resume pointer (`== fold(gate_events)`), the `mechanical-passed`→`--attest` attestation handshake with durable per-event contracts, safe grandfathered migration, and the `gate-state` validator that enforces it. Increment 4's **cooperative M1 is built** (finding-ID end-to-end: `finding-trace` as a `run_spot_check` gate row = referential integrity at delivery, NOT ordering; the clearing-event trace; event-scoped E5; the `T4-watch` + `open exceptions` count lines); the **external host orchestrator (M2) is deferred with four detectable triggers** — the revisit clause has not fired (no recorded post-v2.1.0 skipped-gate incident). Spec: `setec-scratch/apo-runner-fid-increment-4/SPEC.md`.

### Finding Lifecycle IDs

Give every material finding a durable ID that follows it across the whole pipeline: pass output → Findings Ledger → Deficit Lock → editorial letter → revision plan / coaching. With stable IDs, softness, downgrade, omission, and revision follow-through become directly auditable — the Deficit Lock and `softness-check` could match by ID instead of today's token/mechanism/evidence-ref heuristics — and cross-artifact traceability stops depending on prose matching. Pairs with Harness Contracts v2 (the ID is a contract field) and Runner-Governed Execution (the runner tracks findings by ID).

**Built (increments 1–4).** The ID itself already ships (`apodictic.finding.v1.id`, `F-<ORIGIN>-<NN>`); `structured-findings` owns intra-ledger hygiene and `softness-check` owns severity fidelity (locked→delivered) by ID. **Increment 1** (spec + `finding-trace` validator, [`docs/finding-lifecycle-ids.md`](docs/finding-lifecycle-ids.md), shipped v2.1.0) traces the ID *across* artifacts — cross-artifact **referential integrity + sidecar lifecycle coherence** (E1 dangling letter reference, E2 phantom `finding_states` key, E3 invalid state, W1 coverage). **Increments 2–3** (shipped v2.2.0) extend `finding-trace` into the revision loop: E4 dangling revision-plan reference, W2 revision coverage, E5 phantom completion (a `revised` finding lacking an explicit `<!-- resolved: F-… -->` marker), W3 completion coverage — plus canonical `--check-all` gating of the example ledger↔letter pair in both directions. **Increment 4** (runner tracks findings by ID end-to-end, paired with Runner-Governed Execution increment 4's M1) is **built**: `finding-trace` becomes a `run_spot_check` gate row (M1a — referential integrity at delivery, NOT ordering; W1 self-skips out-of-order); the clearing event reports the per-ID trace (M1b); event-scoped E5 on governed sidecars (M1c); the `T4-watch` marker-count line (M1d). Spec: `setec-scratch/apo-runner-fid-increment-4/SPEC.md`.

### Validator Architecture Hardening

`validate.sh` has done heroic work, but the external reviews kept surfacing regex-shaped edge cases (severity-label forms, prefix evidence-ref matches, calibration-line downgrades). Roadmap a gradual migration toward small Python validators with shared parsers, fixture-driven negative tests, and one thin shell dispatcher — extending the v2.0.0 precedent (`structured_findings.py`, `honesty_check.py`) to the rest of the suite. This is mechanical contract enforcement, not an eval harness. Subsumes the deferred *Canonical-framework validator runs as release gate* (§Deferred), which v2.0.0 began closing by wiring `validate.sh --check-all` into `release-verify`.

**Built (shipped across v2.0.0–v2.1.0; the bundle is complete).** Spec + increment plan at [`docs/validator-hardening.md`](docs/validator-hardening.md), bundled with the two adjacent loose ends it closes (release-gate canonical runs; Harness Contracts v2 completion). Increments 1–4 landed: shared `scripts/letter_checks.py` prose-parser module with the **whole editorial-letter / ledger validator family** ported off shell regex — `severity-floor`, `decision-layer-check`, `audit-signal-propagation` (incl. `--check-registry`), `underdiagnosis-triggers`, `ledger-consolidation` — using token-boundary matching, body/appendix split, and fixture-driven negatives. Increment 4 adds `scripts/timeline_checks.py`, a structured Timeline parser backing the three `timeline-*` arms: `timeline-diff` (faithful port) plus `timeline-arithmetic` and `timeline-anchor-conflict` upgraded from marker-hygiene to **true** span-overrun arithmetic and same-scene anchor-drift detection (the capability `pass-10.md` §Phase 7 explicitly deferred). Increment 5 adds `scripts/config_checks.py`, backing the three non-letter arms that validate different artifact types — `quality-risk-triggers` (a contract + optional `Diagnostic_State.meta.json` sidecar), `audit-tier-criterion` (`pass-dependencies.md` §4a/§4b + an audits directory tree), and `argument-recon-prerequisite` (a run-folder scan). Each letter-family port is verified by oracle-diff against the pre-port bash arm (identical exit codes on fixtures + the shipped sample letters); the timeline ports are oracle-identical except the two `silent_*` cases bash false-passed, which now fail; the config ports are oracle-identical including byte-identical output on the real `pass-dependencies.md`. The bash implementations are retained as the no-`python3` degrade path. Increment 6 (Track B — release gate) extends `validate.sh --check-all` to run the ported validators against the *actual* canonical files: `audit-tier-criterion` vs the real `pass-dependencies.md`, plus `decision-layer-check`/`audit-signal-propagation`/`severity-floor` and the `timeline-*` arms against two new canonical worked examples shipped under `core-editor/references/` (`example-editorial-letter.md`, `example-timeline.md`) — so a drift in pass-dependencies tiers, the letter contracts, or the Timeline schema is caught at release time (gate verified to have teeth). Increment 7 (Track C — Contracts v2) ships `apodictic.severity_calibration.v1`, a structured Appendix-B Severity Calibration entry, and makes `softness-check` read `delivered` keyed by finding ID from embedded blocks instead of parsing prose (prose fallback retained) — closing the loop with the Track A honesty gates; the canonical example letter carries a worked-example block gated by `--check-all`. The other half of the original Track C line — structured **gate-event records** — is deliberately deferred to the still-evolving **Runner-Governed Execution** track (which owns that contract) rather than enum-tightened or bolted on here; it is re-homed as a future "option 2, after design" increment in [`docs/runner-governed-execution.md`](docs/runner-governed-execution.md) §Later increments. Increment 8 ports the last four early bash-regex arms that predated the hardening — `ledger-check`, `synthesis-sections`, `tone-check` (onto `letter_checks.py`) and `artifact-names` (onto `config_checks.py`) — so no `validate.sh` markdown/filename validator parses with shell regex anymore; faithful (oracle-diff byte-identical on non-hostile inputs) plus edge-hardening (heading-anchored section matching, body-only/code-stripped/blockquote-skipped tone scan, literal project/runlabel matching). With that, the validator-hardening bundle is complete.

**Follow-on (pure-utility self-test coverage).** The seven count/format utilities that `--self-test-all` previously skipped as "pure utilities that do not carry self-tests" — `contract-hash`, `contract-check`, `ledger-check`, `artifact-names`, `synthesis-sections`, `tone-check`, `state-lines` — now carry fixture-driven self-tests (hash round-trip; required-section/heading presence; naming convention; blocked-superlative detection; line-count incl. the 300/500 state-lifecycle thresholds) and join `--self-test-all` (**24 → 31**). Every command in the suite is now exercised by the aggregate self-test; the bash implementations stay the no-`python3` degrade path.

### Model-Capacity Exploitation

The more ambitious sibling of [Adaptive Mid-Run Mode Escalation](#adaptive-mid-run-mode-escalation): workflows that lean on high-context / leading-model capacity — pass-driven retargeting, per-pass model-tier assignment, critic passes invoked only where uncertainty is high, and long-context re-grounding before synthesis. Where Adaptive Escalation *reacts* to mid-run signal, this would *plan* model and compute allocation up front from the contract and uncertainty profile.

### Research / API Reliability Layer

**Status: M1 built** (`docs/research-reliability-layer.md`). v2.0.0 Phase 5 handled the first real plumbing (exponential backoff with `Retry-After`, no-sticky-error caching, single-call retraction). The reliability layer hardens the external-research path at the run/provider level: cache TTLs with freshness stamps (`response_cache.py`), per-provider budgets + a run-scoped circuit breaker + a per-run reliability ledger (`api_reliability.py`), and a per-result `resolution_status` (resolved / not-found / not-checked) wired into `academic_apis.py` — so for Citation Verifier and Field Reconnaissance a silently-degraded API can no longer masquerade as a clean (or missing) result; a degraded provider's `unretrievable` is reported as NOT-CHECKED, not NOT-FOUND. The editor's *use* of the block (writing the honest distinction into the ledger prose) is the model seam, verified through `evals/`. Follow-ons (deferred): telemetry-tuned budgets, a `--strict` halt on degraded high-stakes runs, a `Citation_Reliability.json` sidecar.

---

## Infrastructure

### Adaptive Mid-Run Mode Escalation — **Built (v2.2.0)**

**Built.** Shipped as the `escalation-check` validator + `run-core.md` integration: a condition-triggered checkpoint after Tier 1 that reads the Tier-1 finding count from the ledger and the complexity signals from the sidecar, and recommends escalating the execution mode before Tier 2. Advisory by default; `--strict` halts on a recommendation. Design: [`docs/adaptive-mode-escalation.md`](docs/adaptive-mode-escalation.md). **De-escalation (swarm/hybrid → sequential) is now also built** — the symmetric case: when no trigger fires and *every* complexity signal sits in a clearly-simple band (set below the escalation thresholds, with a neutral zone between), an over-provisioned mode is recommended down to `sequential`. It is strictly conservative (a missing/malformed signal blocks it; never de-escalates below `sequential`), because wrongly stripping isolation off a complex manuscript risks wrong analysis, worse than the wasted tokens of over-provisioning. The original proposal follows.

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
- ~~Should the system also support *de-escalation* (swarm → sequential) if Tier 1 reveals the manuscript is simpler than expected?~~ **Built** (conservatively: only on affirmatively-confirmed simplicity, never below `sequential`). The reasoning that made it lower-priority — a more expensive mode wastes tokens, not correctness — is exactly why the de-escalation guard is asymmetric: it blocks on any unconfirmed signal so it can never trade correctness for tokens.
- What's the UX for presenting the escalation recommendation? Probably a brief summary: "Tier 1 found [X complexity signals]. I'd recommend switching from [current] to [recommended] mode for the remaining passes. Cost difference: ~[N]K tokens. Proceed?"

### Framework Overview Dashboard

**Status:** ✅ **Built / shipped.** `plugins/apodictic/overview-dashboard.html` and `route-explorer.html` ship the static single-file overview; content refreshed to v2.3.1 reality in #81, and the inventory-parity check (#82) guards them against re-drift.

Static, single-file HTML overview of the plugin's capabilities. System-at-a-glance visual layout, highlighted workflow paths, the Firewall in user-facing language. ~~Build after command restructuring is settled.~~

### Pre-Skill Context Compaction

**Status:** Largely resolved by platform. 1M context on Opus 4.6 + Claude Code's built-in auto-compression. A dedicated pre-skill compaction hook remains a nice-to-have if Claude Code adds skill-lifecycle events.

---

## Writer-Question Surface Hardening

Continuing the v0.5 vision: the plugin should be organized around writer questions, not framework internals. The query-driven pass architecture and intake router shipped in v1.0, but the command surface, output naming, and skill boundaries still reflect build history. Evaluated in v1.3.0 — no user-facing pain found, but the surface can be cleaner.

### What to build

1. **Command taxonomy in release-registry.** ✅ **Shipped + acted on.** Each command carries `category`, `status` (`primary` / `first_class_shortcut` / `compat_alias`), `routerEquivalent`, and a plain-language `writerQuestion`; the grouped README lists generate from it. The taxonomy then drove a surface trim: `/revision-plan` (the lone compat alias) and the two shortcuts that were just the default `/start` path — `/develop-edit` (full_draft + repair) and `/diagnose` (targeted repair) — were **retired into `/start`**, since a writer with a draft hits the router first anyway. The distinct doors stay first-class: `/ready`, `/pre-writing`, `/coach`, `/audit`, `/research`, `/plot-coach`, `/legal-risk`, `/triage-feedback`, `/reader-questions`, `/new-project`, `/projects` (13 commands total, down from 16). NB: "revision-plan follow-through" in `finding-trace` (E4/W2) is the revision-plan *artifact* `/coach` emits — unrelated to the retired command.

2. **Doc sync across all public surfaces.** ✅ **Shipped (#80).** Every public doc, README, help surface, and marketplace entry uses the same grouped command presentation generated from the registry — the 5 previously-unregistered commands are registered and both READMEs' command lists are registry-generated. No more hand-maintained command lists; the inventory-parity check (#82) keeps the dashboard/matrix inventories from drifting again.

3. **Canonical 8-block macro map.** ✅ **Shipped.** Emotional Dynamics has its own block permanently. The 8 blocks: Structure Map, Reader Dynamics, Character Architecture, Emotional Dynamics, Scene Delivery, Reveal Economy, Theme & Continuity, Submission Readiness. `pass-dependencies.md §3` is locked as the single source of truth for the blocks, the pass→block map, and the per-block `User Question` — §2's concern map and `core-editor/SKILL.md` derive from it; `audit-signal-propagation` / `audit-tier-criterion` (which read §4) ripple-verified unchanged.

4. **Pass-detail file headers.** ✅ **Shipped.** Each Core DE pass artifact begins with a §3-sourced blockquote header (`Macro block` · `Writer question` · `Legacy pass id`), values read from §3, never authored. New `pass-header` validator (H1 header present — legacy header-less = WARN; H2 block ∈ 8 + block↔pass + question all agree with §3; H3 non-empty) checked in `--check-all` against the real §3 via `example-pass-artifact-header.md`. Emission wired into `run-core.md`. Makes a direct-opened file legible without framework knowledge.

5. **Results Guide artifact.** ✅ **Shipped.** `[Project]_Results_Guide_[runlabel].md` — a plain-language navigation index mapping each writer question the run produced (the §3 `User Question` for each macro block that ran) to the relevant artifacts, audits, and state files. First file after the editorial letter, a standard deliverable (not an offer). The template already lived in `core-editor/SKILL.md §Results Guide Artifact`; this wired its emission into `run-synthesis.md §Core DE Deliverables` and added the `results-guide` validator (`results_guide.py`, dual-mirrored) — one arm, three checks: **R1** every `### <question>` heading is a canonical §3 User Question (an invented block ERRORs; a run that produced only some blocks is legal — absence is fine, invention is the defect); **R2** (load-bearing) every backtick `.md`/`.json` citation resolves to a run-folder file and no un-substituted `[…]` placeholder survives, while `/coach` / `/audit [name]` command tokens are exempt via the extension guard; **R3** no `Must/Should/Could-Fix` severity leak and no `apodictic:finding` block (it indexes, never diagnoses). R1 reuses `config_checks._parse_section3` against the real `pass-dependencies.md §3`; degrades to a skip when §3 is unavailable, fails closed on an unreadable run folder. Checked in `--check-all` against the canonical `example-results-guide` run folder.

6. **Skill names scrubbed from user-facing copy.** ✅ **Shipped (2026-07-06).** Public copy describes workflows and next steps, not which skill is being loaded. A completed inventory across the committed tree found the writer-facing surfaces near-clean already; the one residual writer-rendered leak — the `/apodictic` capability-index body — was rewritten from "the commands sit on five skills: **core-editor** (…)" to workflow language naming six capability areas (also fixing a stale five-vs-six count that omitted the nonfiction argument engine). The classification rule is the firewall: scrub **writer-rendered prose only**; agent-routing/delegation prose the model reads to dispatch (the Delegation Rules zone, Genre Module Routing activation notes, `commands/*.md` load-directives, inter-skill reference lists, run-flow load instructions) legitimately names skills and is exempt — rewording it risks breaking routing for zero writer-visible gain. The durable guarantee lives in the convention, not the one edit (see #7).

7. **Handoff language standardized.** ✅ **Shipped (2026-07-06).** Cross-skill transitions phrased as workflow moves: "run an audit next," "plan revision next," not "load specialized-audits." The writer-rendered handoffs were already command-phrased (offers route by `/coach`, `/audit`, `/ready`, `/start`); this codified the convention so future prose stays clean — a new **§Author-Facing Language** subsection in `core-editor/references/output-policy.md` requires writer-rendered and generated author-facing prose to name the command or the workflow move, never the skill slug (a backticked slug inside a workflow noun is still a slug), with a boundary note distinguishing it from the framework-code glossing that `author-facing-lint` enforces on the generated letter body. No standalone validator: the committed scrub set is one line wide and the ROADMAP records "no user-facing pain found" / "skill loading is invisible to users" — a `skill-name-lint` arm is deferred until a demonstrated regression need. **Downstream:** the vendored siblings (APODICTIC-Gemini, apodictic-tauri) carry the old prose byte-for-byte and pick up the fix via the next `sync:plugin` machine re-vendor after an apodictic release, not in this change.

### What not to build (yet)

- **Instrumentation.** APODICTIC-Gemini has a Cloud Run backend that could support event logging, but there's no current need for telemetry. Revisit when external users are active.
- **Filename renames.** Keep pass-numbered filenames on disk. The Results Guide is the primary macro-block organizer. Bulk renames deferred unless usage shows writers navigate by detail files.
- **Skill merges or renames.** The current six-skill architecture stays. Skill loading is invisible to users. Evaluate only if handoff pain surfaces.
- **Editorial Letter renaming.** `Core_DE_Synthesis` and `Full_DE_Synthesis` work. Don't alias.

---

## Annotated-Manuscript Deliverable

**Status: Built (Increments 1–3)** — Increment 1 shipped 2026-06-16 (margin comments at line-range / section / chapter / document granularity, promoted the same day from [Horizon Capacities](#horizon-capacities) Tier 1, item 2 — number retained there for stable cross-reference). **Increment 2 (2026-06-17):** character-precise *quote-locator* anchoring — the finest `quote` rung, the **A6** quote-integrity gate, a unified character-offset renderer (byte-identical to Increment 1 for non-quote anchors), and the optional `evidence_quote` finding field. **Increment 3 (2026-06-17):** **letter ↔ margin cross-links** — the `crosslink` render + validator (`scripts/crosslink.py`), back-link spans injected into the letter (a "second snapshot"), gated X1–X4 + W1. Spec: [`docs/annotated-manuscript.md`](docs/annotated-manuscript.md). The **[Producer](#producer--generation-wiring-increment-1)** wires the deliverable into the run flow. **Producer Increment 1 (generation wiring, 2026-06-17):** a real run persists the snapshot at intake, then — when it wrote a full editorial letter — offers and (on accept) generates the marked-up copy + crosslinked letter, with the `<!-- finding: F-… -->` marker pinned so Increment 3's letter→margin back-links resolve live. This **clears Increment 3's inertness** (the synthesis now emits matching letter markers). **Increment 2's `quote` rung stays consumer-only** until the producer's `evidence_quote` pass-attachment lands ([§Producer — `evidence_quote` population](#producer--evidence_quote-population-increment-2)). Downstream stack (maintainer 2026-06-17): **draft-over-draft structural regression** (`regression-diff`, [`docs/draft-regression-testing.md`](docs/draft-regression-testing.md)) and **round-trip re-anchoring** (`reanchor` — carry the margin notes onto a revised draft, classifying held / moved / vanished / ambiguous / not-re-anchorable, [`docs/annotated-manuscript-reanchoring.md`](docs/annotated-manuscript-reanchoring.md)) are both **Built (2026-06-17)**. **Render-target export** ([`docs/annotated-manuscript-export.md`](docs/annotated-manuscript-export.md)): **Obsidian Increments 1–2 Built (2026-06-17)** — the gated manifest projected to **native Obsidian** (no plugin) via `scripts/annotation_export.py` + the `obsidian-export` validator. **Inc 1:** each finding renders as a `[^finding-id]` footnote whose definition is the verbatim comment (O1 round-trip + O2 footnote resolution + O3 comment fidelity). **Inc 2:** bidirectional clickable cross-links — the footnote definition gains a `[[letter#^id]]` forward wikilink, the Obsidian letter gets `^id` block ids + reverse `[[copy#heading]]` wikilinks (resolved heading text, not the manifest token — Obsidian strips the heading's footnote ref from the slug), gated O4 (link resolution) + O5 (letter prose fidelity). **Inc 3 (HTML) Built (2026-06-17):** a self-contained, read-only `.html` openable in any browser (no tool) — the manuscript in a faithful escaped `<pre>` with `<sup>` footnote markers + a findings section + native bidirectional anchor links + embedded CSS, gated by `html-export` (H1 round-trip + H2 anchor resolution + H3 comment fidelity). **Inc 4 (DOCX → Google Docs) Built (2026-06-17):** a `.docx` (hand-written OOXML, stdlib-only, byte-deterministic ZIP) where each finding's manuscript span is wrapped as an anchored Word comment — so **Google Docs imports it as a native anchored comment** (the professional standard), and it doubles as the DOCX target. Gated by `docx-export` (D1 artifact integrity = on-disk == fresh build byte-for-byte, D2 text round-trip, D3 comment resolution + fidelity). **PDF** remains on the horizon. CriticMarkup stays the canonical render — it's not the industry standard (Word Track Changes is) but it's the plain-text base whose no-mutation proof is cheap and which bridges to Word/GDocs comment mode.

The standard trade developmental-edit deliverable set is **editorial letter + in-manuscript margin comments + book map**. APODICTIC ships two of the three: the letter (the synthesis — judgment and priority) and the book map in both prose (the reverse outline, Pass 0) and partial visual form (the [Manuscript-Structure Visualizations](#horizon-capacities) Tier-1 item). The margin-comment leg — the manuscript itself, marked up, with each finding anchored where the problem lives — is the one the framework does not produce: it emits a letter that only *references* loci ("Chapter 9 collapses three days…"). Judgment without location is unactionable at the desk; the marked-up copy is the working surface that makes the letter revisable at the line. This is what promotes it out of the Horizon scan: it completes the deliverable set, and it is the **highest externally-validated gap** (the #1 human-DE deliverable, the one a writer expects back first). Firewall-bound — comments only, never tracked prose changes.

### Producer — generation wiring (Increment 1)

**Built (2026-06-17).** Wires the validator-only deliverable into the run flow so a real `/start` diagnosis ends with a marked-up manuscript + a crosslinked letter — render-only, model-never-authors. Spec: [`docs/annotated-manuscript-producer.md`](docs/annotated-manuscript-producer.md). What shipped:

- **Snapshot at intake.** The intake step persists `[Project]_Manuscript_Snapshot_[runlabel].md` (LF-normalized, trailing newline, no other change) for core-de / full-de runs — the deliverable's immutable reference, captured while the manuscript is reliably in context (before a long run's context compacts).
- **Run-end offer, conditioned on a detectable artifact.** Whenever a run wrote a full editorial letter (`*_Core_DE_Synthesis_*` / `*_Full_DE_Synthesis_*` — a file predicate, self-excluding for partial / fragment / triage / audit; `/ready` offers because it writes one), the orchestrator **asks the author** and, on *yes*, runs build → A1–A6 → render → X1–X4 **staged in a temp copy**, moving only gate-verified artifacts into the run folder (verified-or-absent). No headline command — the offer is the surface.
- **Marker pin.** The letter's near-finding citation is pinned to the canonical `<!-- finding: F-… -->` (a subset of what the honesty gates already accept, so they're unaffected) so the crosslink back-links resolve; the Severity-Calibration appendix keeps a distinct comment form to avoid a second back-link.
- **Re-generation, no new command.** An existing un-annotated run folder is re-annotated through `/start`'s `diagnosed`-node dispatch, conditioned on a no-annotated-copy glob — not a new `next_action` enum.
- **Gate.** A new `--check-all` chain runs build→gate→render→gate on a temp copy of the canonical inputs and asserts the fresh build is **byte-identical** to the committed fixture. No new validator (count stays 43); no command registration.

### Producer — `evidence_quote` population (Increment 2)

**Pilot built (Pass 5, 2026-06-17); demand-gated for further passes.** Deliverable Increment 2 built the **consumer** of `evidence_quote` (the quote-locator + the [A6](docs/annotated-manuscript.md) gate); Producer Increment 2 makes a pass *populate* it. The pilot adopts **Pass 5 (Character Audit)** — its findings are the most sentence-precise of the Core baseline: when a Pass-5 finding is about a specific line, it attaches that line **verbatim** as `evidence_quote`, lighting the character-precise `quote` rung on the marked-up copy. The discipline (sentence-precision criterion, the copy-not-author firewall, location-by-bytes, single-line) is written in `findings-ledger-format.md` §"When to populate `evidence_quote`". Prose-only — no schema change, no new gate (A6 is the existing safety gate). Further passes adopt **per demand** (below).

- **Scope.** A pass populates `evidence_quote` only when its finding genuinely points at a specific line (a flat-dialogue beat, a telling-not-showing sentence, a continuity seam at a named line, a quote-bearing nonfiction claim). A structural finding about a whole chapter or arc correctly **omits** it — the rung then degrades to chapter/line, exactly as today. No finding is forced to carry one.
- **Firewall (why this is safe to roadmap).** `evidence_quote` is **manuscript bytes, never authored** — the pass copies a span it is *already citing*, never composes one. The downstream **A6** gate enforces this *by identity*: the quote must occur in the snapshot verbatim and uniquely, so a pass physically cannot smuggle authored text (a non-verbatim or non-unique quote fails A6 and the locator degrades). The pass-side discipline is just "copy the span you cited"; A6 is the mechanical proof. This keeps the producer inside the existing Firewall rather than widening it.
- **Demand-gated + incremental, not a retrofit.** A pass adopts `evidence_quote` when its findings are *already* sentence-precise. **Pass 5 (character beats) is the shipped pilot.** The natural next adopters — Pass 8 (reveal lines), the AI-prose line-level flags, and citation/quote-bearing nonfiction findings — are **not** in this increment; each adoption immediately lights up the quote rung for that pass's output while the rest keep degrading harmlessly. Build per-pass when that pass's output is demonstrably sentence-precise and a writer would benefit from the exact-sentence anchor — never speculatively across all 11 passes at once.

### How it was built (the record)

Increment 1 shipped exactly the way the promotion analysis called for: **spec-review, then build with a hostile fixture set** — an export/anchor build, not a research one. One adversarial Codex spec-review ran first (P0–P3 incorporated before any code); the build then mechanized the contract and gated a canonical fixture. The original reasoning:

- **Not a research build.** It renders findings the engine *already produces* — a margin note is a verbatim projection of an existing finding, so the editorial reasoning is upstream and settled. This is an anchor-and-export problem, not a reasoning one. No level-setting research and no three-model synthesis: those de-risk diagnostic *content* (what a new audit should flag); this is mechanical contract enforcement, where the content is already decided.
- **One adversarial spec review first** (the normal spec→review gate; Codex 5.5 is the standing reviewer — *not* a three-model pass). The spec is dense and makes subtle load-bearing claims worth pressure-testing before a line of code: the no-mutation reverse-transform (`A2`) and its sigil-collision precondition; whether `A5`'s verbatim-projection template truly closes the Firewall for *every* finding-field shape (a CriticMarkup sigil or newline inside `mechanism`); and whether the four-rung anchor ladder covers the real `evidence_refs` corpus. The **manuscript-snapshot prerequisite** — which makes the author's manuscript a tracked, line-stable run artifact for the first time — is the most architecturally novel piece and the right focus for that review.
- **A hostile fixture set**, beyond the two `--check-all` fixtures the spec already commits to. The anchor resolver is the single highest-risk surface, and the *shipped* corpus already spans every rung and the messy cases: `["Chapter 9"]`, `["Ch. 12"]`, `["Ch.3 p.40"]` (page-bearing), the mixed `["Pass 4 §Scene Turns", "Ch. 12"]` (finest rung wins), and the pass-artifact-only `["Pass 1 §Orientation"]` (honest `document` degradation). Fixtures should exercise each rung plus the `W1` Timeline-boundary drift and the `A2` sigil-collision hard-fail — the "hostile fixtures" review discipline applied at build time, where correctness is actually retired.
- **Reuse, don't reinvent.** `scripts/viz_manifest.py` (the already-built visualizations sibling) carries a conservative chapter parser (the "conservative `evidence_refs` parse" → `Ch N` / `unplaced`). The anchor ladder's chapter rung should share it, not author a second chapter-normalizer that can silently drift from it — a reuse trap the spec review should catch.
- **Build Increment 1 only:** CriticMarkup render, line-range / section / chapter / document anchoring, no character-precise anchoring. DOCX / Google Docs export and the quote-locator each ship their *own* integrity gate as later increments.

The "big lift" is real but it is breadth, not depth: the lift is the *number* of new surfaces (snapshot step + `apodictic.annotation.v1` schema + validator + CriticMarkup renderer + run-flow integration), not any single hard problem. The reasoning is done; what remains is plumbing plus the no-mutation proof.

---

## Horizon Capacities

*Surfaced by a 2026-06 design scan; unplanned.*

A deliberate sweep for capacities a developmental-editing tool of this shape **could** have that are absent from both the codebase and the plan above. Each is judged against the five load-bearing commitments — the **Firewall** (diagnose structure and *classes* of fix, never invent content), **severity honesty** (the Deficit Lock; severity cannot be softened), **listens-before-diagnosing** (the contract is inferred from the text), **non-commercial / local / no-telemetry**, and **mechanical validators over eval harnesses**. Sorted by how cleanly each fits. These are candidates, not commitments — the framework default is to build none until a forcing function appears. Numbering is stable for cross-reference; speccing order follows fit (Tier 1 first).

Cross-field calibration: the visualization and annotated-manuscript gaps are validated against the structural-editing field (Fictionary ships 15+ automated story visualizations; the standard human-DE deliverable set is editorial letter **+ in-manuscript margin comments + book map + style sheet**), and the deliberate exclusions (marketability guarantees, copyediting) are confirmed against [§Not Planned](#not-planned).

### Tier 1 — Clean whitespace (fits the philosophy)

These invent nothing — they render, export, or extract what the engine already produces — and sit in gaps the plan does not touch.

1. **Manuscript-Structure Visualizations — Increment 1 built (charts 1–3) + chart 7-nonfiction claim ladder built (render-only M1).** A *manuscript-specific* visual report. **Built:** the pacing/word-count curve, POV-time distribution, and finding-severity-by-chapter charts, plus the **nonfiction claim ladder** (C0 + subclaims + per-rung support coverage over `argument_spine.v1` + `support_plan.v1` — gates X1/X5/X6/X7/X8 + W3, no scene axis, no new schema or validator), as a render-only single-file SVG companion (`viz_manifest.py render`) over a provenance-closed `apodictic.viz_manifest.v1` manifest. **Producer-gated (future):** the character co-presence network, scene-function heatmap, reveal-economy timeline, and beat-map against the chosen spine (each gated on a producer increment that makes its upstream artifact machine-readable); a claim-to-scene overlay is a further producer increment, out of scope. **Distinct from** the planned [Framework Overview Dashboard](#framework-overview-dashboard), which visualizes the *plugin's* capabilities, not a book. Highest externally-validated gap (Fictionary's signature). Builds a new single-file SVG renderer in the static-HTML house pattern (no editorial-letter render pipeline exists to reuse); the data already lives, machine-readable, in the Findings Ledger (`apodictic.finding.v1` blocks) and `Timeline.md` (the Event Ledger's per-scene word-count/POV). Firewall-safe (it renders diagnosis, invents nothing). Spec: [`docs/manuscript-visualizations.md`](docs/manuscript-visualizations.md).

2. **Annotated-Manuscript Deliverable. — Built (Increment 1), 2026-06-16.** Promoted out of the Horizon scan and shipped the same day; see [§Annotated-Manuscript Deliverable](#annotated-manuscript-deliverable) for status + lineage, and [`docs/annotated-manuscript.md`](docs/annotated-manuscript.md) for the spec. (Number retained for stable cross-reference: locus-anchored margin notes — the #1 human-DE deliverable — exported as an annotated copy; an export/anchor problem over findings that already carry stable loci **and** durable IDs ([Finding Lifecycle IDs](#finding-lifecycle-ids)), comments only, firewall-clean. *Effort: low–medium.*)

3. **Beta-Reader Instrument Generation — built.** The upstream complement to [Feedback Triage](#feedback-triage--built-increment-1-v220) (which *ingests* reader feedback): turns the diagnosis's open, low-confidence questions into a targeted reader questionnaire. Exploits the confidence axis the engine already tracks. Firewall-safe. Built as the `/reader-questions` command + revision-coach mode + the `reader-instrument` validator. Spec/docs: [`docs/beta-reader-instrument.md`](docs/beta-reader-instrument.md).

4. **Promise-Contract Fidelity (author's own marketing copy). — Built (Increment 1), 2026-06-19.** Diagnoses a query / synopsis / blurb / logline against the *inferred manuscript Contract* — does the pitch keep the promise the book makes? APODICTIC's core contract-mismatch move pointed at the pitch instead of the prose, narrowed to the **document-fidelity** residue (emphasis PCF1, reveal leak PCF2, over-promise PCF3, under-sell PCF4, cross-document inconsistency PCF5): it **consumes** Shelf & Positioning (genre/comp/tone) rather than re-deriving it, and submission-readiness (is it ready) stays separate. Firewall-bound — diagnose the author's copy, never *write* the query (Shelf & Positioning's Reframe Protocol owns rewriting). Built as a **core-editor workflow module**: the `apodictic.pitch_copy.v1` persisted input, `apodictic.finding.v1` findings with origin `PCF` + the `PCF`-scoped namespaced evidence-ref convention (`copy:`/`contract:`/`ms:`), and the `promise-contract` validator (P1 two-sided gap, P2 copy persisted & typed, P3 reveal-leak form gate; W1 drafted-copy firewall leak + W2 market-prediction drift, ERROR under `--strict`), with a canonical `--check-all` gate over `example-promise-contract.md`. Promoted OD1: `CONTROLLING IDEA` is now a first-class Contract schema field. Validators 48 → 49. (See also #14.) Spec: [`docs/promise-contract-audit.md`](docs/promise-contract-audit.md).

5. **Reader-Persona / Audience-Segmented Experience Simulation. — Built (Increment 1), 2026-06-20.** Run the reader-experience map through distinct persona lenses and surface *divergence*. Reception Risk covers harm/offense; the experience pass runs one composite reader. Neither models how the same beats land across audience segments. Firewall-safe (it predicts structurally and never fabricates reader testimony — the line against item 17). **Built:** the `apodictic.persona.v1` + `apodictic.divergence.v1` schemas, the `craft/persona-divergence.md` Pass-1 overlay, `scripts/persona_divergence.py` + `validate.sh persona-divergence` (D1 schema, D2 grounded-prediction, D3 target-severity anchoring, D4 anti-fabrication, D5 closed-key persona, W1 coverage), and the canonical worked example wired into `--check-all`. The three mechanical #17 guards (closed-key D5, grounded D2, anti-fabrication D4) keep it a lens, not a focus group. Validators 53 → 54. Spec: [`docs/reader-persona-simulation.md`](docs/reader-persona-simulation.md).

6. **Draft-over-Draft Structural Regression Testing. — Built (Increment 1), 2026-06-17.** `finding-trace` tracks revision *follow-through* (was `F-…` addressed?); it does not detect *regressions* — structure the fix broke ("tightening Act 2 severed the Act 1 setup that paid off in Act 3"). The shipped `regression-diff` validator (`scripts/regression_diff.py`) diffs the **whole Findings Ledger across revision rounds** on a **deterministic heuristic match** (per-run ids mean cross-round identity is a *candidate*, never an assertion): **W1 recurrence-candidate** (a resolved finding that re-appears) and **W2 new-in-quiet-chapter** (candidate fix-induced breakage), advisory / ERROR under `--strict`, with round-close integration in `state-lifecycle.md`. It is the dependency for **round-trip re-anchoring** (next in the stack). *Effort: medium.* Spec + status: [`docs/draft-regression-testing.md`](docs/draft-regression-testing.md).

7. **Auto-Derived Continuity Bible. — Built (Increment 1), 2026-06-20.** The narrative half of a DE "style sheet": canonical names, ages, timeline facts, world rules, extracted into a reference artifact. `Series_State.md` does this cross-volume; there is no *single-manuscript* equivalent. The copyedit half (spelling/hyphenation) stays out of scope ([§Not Planned](#not-planned)). Pure extraction → firewall-clean. **Built:** the `apodictic.canon_fact.v1` schema, the `continuity-bible.md` module, `scripts/continuity_bible.py` + `validate.sh continuity-bible` (C1 schema, C2 locus shape, C3 contradiction integrity, C4 chronology consume-vs-rederive, W1 coverage), and the canonical `example-continuity-bible.md` (consolidating `example-timeline.md`) wired into `--check-all`. Contradictions are surfaced (both values, paired in a Contradiction Ledger), never resolved. Validators 49 → 50. Spec: [`docs/continuity-bible.md`](docs/continuity-bible.md).

8. **Content-Advisory / Sensitivity-Surface Derivation. — Built (Increment 1), 2026-06-20.** A structured map of where intense content occurs, at what intensity, on- vs off-page. Reception-Risk / Consent-Complexity / Erotic-Content audits assess *craft/risk*; none emit a reader- or marketing-facing advisory artifact. Extraction → firewall-safe. Optional by design (some authors decline content warnings on principle). **Built:** the `apodictic.content_note.v1` schema, the `specialized-audits/references/content-advisory.md` module, `scripts/content_advisory.py` + `validate.sh content-advisory` (A1 schema, A2 locus shape, A3 no-severity-leak, W1 prescriptive-drift, W2 opt-in), and the canonical `example-content-advisory.md` wired into `--check-all`. Descriptive, never prescriptive; off the editorial severity scale. Validators 52 → 53. Spec: [`docs/content-advisory.md`](docs/content-advisory.md).

9. **Cross-Manuscript Author Voice/Craft Fingerprint. — Built (Increment 1), 2026-06-20.** A persistent author profile across *unrelated* works — voice drift, growth, unconscious self-imitation. Today's voice-distinctiveness is *within-manuscript*; Series Continuity tracks *story facts*. **Distinct from** the planned cross-session pattern recognition under [Coaching Deepening](#coaching-deepening). Privacy-sensitive (observations, not judgments) and local-only. Consumes the existing stylometry — the **single-voice** AI-prose fit (`voice_profile`/`voice_distance`) + personal-baseline z-scores as the primary source (POV Voice Profile centroids only for the optional protagonist-collapse sub-diagnostic, since they produce no author centroid on single-POV work) — it persists/diagnoses across works under an operator-curated author-root, it does not recompute. **Built:** the `apodictic.voice_fingerprint.v1` schema, the `author-voice-fingerprint.md` module, `scripts/author_fingerprint.py` + `validate.sh author-fingerprint` (F1 schema, F2 provenance, F3 same-register, F4 descriptive-not-prescriptive, W1 seed-only, W2 local-only), and the canonical `example-author-voice-profile.md` wired into `--check-all`. Validators 51 → 52. Spec: [`docs/author-voice-fingerprint.md`](docs/author-voice-fingerprint.md).

### Tier 2 — Adjacent disciplines / input modalities

Bigger lifts, still philosophy-compatible.

10. **Dramatic-Writing Structural Module (screenplay / stage play / audio drama).** The genre-expansion list names interactive fiction, game narrative, and comics but **not** screen or stage — which have their own structure (sequence/act architecture, shown-vs-told, subtext-on-the-page, white-space pacing) and formats (Fountain, Final Draft). The contract-inference engine ports. *Effort: large.*

11. **Argument-Engine Extension to Grant Proposals / Academic Papers / Pitch Decks.** ✅ **M1 built** (genre layer — Nonfiction Pre-Draft Increment 5). The Dialectical Clarity kernel already handles argument-shaped nonfiction; this adds the genre-specific *structure contract* (Specific Aims / Significance / Innovation / Approach; contribution + related-work positioning; problem / solution / traction) as an optional `apodictic.genre_profile.v1` block that seeds `Argument_State` and is validated by the existing `argument-spine` validator (B1–B4 + W4 — no new validator; the genre layer rides `argument-spine`, validator count unchanged), plus genre-calibration + reviewer-anticipation prose in Dialectical Clarity. Calibration on an existing engine, not new architecture. See `docs/nonfiction-pre-draft.md` § The genre layer. **Increment 2 built:** reviewer-anticipation **W5** ships in `argument-spine` (`plugins/apodictic/scripts/argument_spine.py`, PR #168), and the per-genre diagnostic-calibration table lands in Dialectical Clarity's *Reviewer-Anticipation Lens* (`plugins/apodictic/skills/specialized-audits/references/craft/dialectical-clarity.md`). *Effort: medium–large.*

12. **Songwriting / Lyrics / Spoken-Word Lens.** Poetry is already a genre candidate; lyrics are a different problem (hook economy, refrain function, prosody-against-meter, the verse/chorus contract). Demand-gated. *Effort: small–medium.*

13. **Standalone Worldbuilding-Bible Coherence Tool. — Built (M1), 2026-06-21.** SFF-Worldbuilding audits a *manuscript*; a standalone bible-coherence checker (rules consistency, magic-system cost accounting, geography/timeline contradiction) is usable before or alongside drafting, in the pre-writing pathway's spirit. **Built:** the `apodictic.world_fact.v1` schema, the `worldbuilding-bible.md` extraction module, `scripts/world_bible.py` + `validate.sh world-bible` (W1 schema + bespoke closed-key check, WD unique ids, WB-R1 closed-set rule consistency, WB-C1/WB-C2 cost accounting, WB-G1 distance within a commensurable unit class — spatial vs travel-time axes kept separate — WB-G2 chronology cycle + Day-anchor drift, and the WF surface-don't-resolve firewall scan), the `/world-bible` command (routed like `/legal-risk`, not a manuscript-pass audit), and the canonical `example-worldbuilding-bible.md` (an epic-fantasy bible with two staged + overridden contradictions) wired into `--check-all` under `--strict`. It checks a *bible* (not a manuscript) and ports the genre module's consistency kernel to bible scope, pre-draft — distinct from the manuscript-facing SFF Worldbuilding Integration audit and a sibling to the post-draft Continuity Bible. Contradictions are surfaced (both values, paired in a ledger), never resolved. Validators 50 → 51. *Effort: medium.* Spec: [`docs/worldbuilding-bible.md`](docs/worldbuilding-bible.md).

### Reconsidered from the boundary

Two capacities first scanned as boundary-pushing are, on reflection, **closer to buildable** than the non-viable set below — each has prior art in the framework and a firewall-safe diagnostic form.

14. **Positioning-Risk Lens (the diagnostic sibling of marketability).** **Resolved: will not build — covered by existing surfaces.** Pass 11C (Market Reality Check + Shelf Positioning Gate), Pass 11D (Abandonment Risk Rating), and the Shelf & Positioning audit already surface positioning risk in three deliverable sections, so a consolidation register would be redundant. The one net-new idea — a "risk-not-forecast" boundary guard — is non-viable: [§Not Planned](#not-planned) excludes commercial-viability *guarantees*, **not predictions**, yet the guard would police predictions and so would flag the framework's *own* canonical Pass-11 output (which deliberately produces acquisition-style predictions like "agents will reject because…"). The only real boundary (outright guarantees) folds, if wanted, into [Promise-Contract Fidelity](#horizon-capacities)'s W2 phrase set rather than a standalone capability. Reopen only if a cross-manuscript *portfolio* view is demanded (a different artifact). Decision record: [`docs/positioning-risk-lens.md`](docs/positioning-risk-lens.md).

18. **Uncertainty-Resolution Intake Interview. — Built (Increment 1), 2026-06-20.** A narrow loop, *on top of* the existing draft-then-validate intake, that asks the author to **disambiguate a specific structural ambiguity the framework detected but cannot settle from the text** ("is the non-linear ordering in Ch 4–6 a deliberate braid, or drift?"). **Prior art:** the `/start` router already runs a two-to-three-question intake, and `run-core.md`'s intake already shows the inferred contract and asks the author to correct it — so contract/audience/scope capture is *already owned*; this adds the one thing nothing covers. The apparent tension with *listens-before-diagnosing* dissolves because the loop is confined to detected-ambiguity disambiguation (every question a flavor of *intentional-vs-accidental*), never re-asking the genre/reader-promise/controlling-idea the intake already captures, and answers may direct *how* a feature is assessed but never *suppress* a finding (the Deficit-Lock guard). *Effort: medium.* Spec: [`docs/uncertainty-intake-interview.md`](docs/uncertainty-intake-interview.md).

19. **Interpretable Stylometric Explanation (descriptive style-feature labels over the Author Voice Fingerprint). — Built (M1), 2026-06-21.** The DESCRIPTIVE labelling layer **on top of** the Author Voice Fingerprint (#9): #9 measures *how distinctive* a voice is and persists it as scalar z-scores; this overlay attaches a **natural-language gloss** to a handful of the *salient measured* features ("the prose leans hard on the definite article", "function-word profile concentrated in *the/and/but*"), each bound by provenance (`feature_ref`) to the exact SETEC `voice_profile` feature it describes. It does **no new stylometry** (it consumes #9's already-consumed per-family feature inventory) and offers **no advice** — it *names* a measured feature, it never prescribes a voice change and never fabricates a style claim. This is the **riskiest of its wave**: one preposition from a Firewall breach, so the result schema is built so a "write more like X" directive is **unrepresentable** (no target/goal/recommendation/rewrite/compare_to_author field; `frame`/`direction` are closed descriptive enums) and the one residual free-text surface (`label`) is scanned by the validator. **Built (M1):** the `apodictic.style_label.v1` schema, the `interpretable-stylometric-explanation.md` overlay module, `scripts/style_explanation.py` + `validate.sh style-explanation` (X1 schema, X2 provenance/anti-fabrication, X3 no-severity-leak, X4 descriptive-not-prescriptive — incl. a first-class comparison-to-emulate match — X5 same-register cluster, X6 local-only hygiene, W1 seed/coverage), and the canonical `example-author-style-explanation.md` (a local-only profile with three same-register `function-words` labels in one coordinating cluster plus one out-of-cluster punctuation label) wired into `--check-all` under `--strict`. The validator count is **derived** from `validate.sh`'s `AGG_VALIDATORS` list (no hand-maintained number). The label-*generating* embedding/scoring model is a **deferred M2** lazy-import + `skipif` seam — the M1 validator never calls a model and enforces the firewall regardless of who authored the labels. Descriptive, local-only, off the editorial severity scale. *Effort: medium.* Spec: [`docs/interpretable-stylometric-explanation.md`](docs/interpretable-stylometric-explanation.md).

### Surfaced but not viable (and why)

These three were surfaced by the same scan but **collide with a load-bearing commitment**, and are recorded here so the boundary is explicit and durable. They are not [§Not Planned](#not-planned) scope-exclusions; they are capacities a similar tool *could* have that *this* tool's principles forbid.

15. **Cross-User Telemetry / Aggregate Severity Calibration.** Learning severity calibration from many real runs would be powerful, but it collides with the **no-instrumentation-while-private** stance ([§Writer-Question Surface Hardening](#writer-question-surface-hardening) → "What not to build (yet)") and the local-tool ethos. The only principle-preserving form is opt-in, privacy-preserving aggregation — out of scope until external users exist and ask for it.

16. **Author-Editor Negotiation / Concession Loop.** A workflow where the author contests a finding and the editor **downgrades** it. This directly contradicts the **Deficit Lock**: severity is locked at Triage *before* charity reframing, precisely so it cannot be softened. The disciplined form already exists — the structured override-marker pattern records dissent *without changing the verdict*. Building a concession loop would dismantle severity honesty, the framework's central value.

17. **Simulated Reader Focus Group (generated reactions).** Fabricated reader reactions are invented data — the **Firewall's** spirit applied to evidence. Reception Risk and persona simulation (#5) are the disciplined alternatives: reason about reader experience without manufacturing testimony.

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

### State-lifecycle gardening thresholds (300/500 lines) — **partially addressed**

Framework instruction in `state-lifecycle.md` triggers gardening protocol when `state.md` exceeds 300 lines (warning) or 500 lines (forced gardening). Canonical fixtures don't reach the thresholds, so threshold-crossing behavior is not directly observed. **The mechanical half is now covered:** the `state-lines` self-test includes 300-line and 500-line fixtures and asserts the validator reports those counts exactly (the count the gardening triggers read). The *gardening behavior* itself — what the model does once `state-lines` reports a threshold crossing — is prose in `state-lifecycle.md` and remains model-interpreted (a fixture for it would be an eval, not a mechanical check).

### AI-Prose Calibration unexercised flag families (AIC-2 / AIC-4 / AIC-6 / AIC-8)

The AI-Prose Calibration audit defines flag families AIC-1 through AIC-8. F1-F4 exercise AIC-1 (Voice Singularity), AIC-3 (Echo Stack), AIC-5 (Puppet Dialogue), and AIC-7 (Discourse Leak). The remaining four families (AIC-2 Velvet Fog, AIC-4 Register Seams, AIC-6 Continuity Smear, AIC-8 Unearned Fluency) lacked fixture coverage. **Fixtures authored:** `evals/fixtures/ai-prose-calibration/` supplies a synthetic AI-heavy prose sample (`ai-heavy-prose.md`) drafted to fire exactly those four families with named-flag invocation targets, a voiced `clean-control.md` false-positive control, and a pre-registered `expected.md`. These are pure data (behavioral eval; no mechanical `validate.sh` arm parses them). The **eval-coverage confirmation report is a model run and remains deferred** (per the corpus-expansion survey) — the fixtures are authored; the sign-off run is not done.

### Genre-specific tag audits (queer-romance, cozy, philosophical)

Tag audits for queer-romance-erotica, cozy-tag, and philosophical-tag are defined in `specialized-audits/references/tag/` but no canonical fixture invoked them. **Fixtures authored:** `evals/fixtures/tag-audits/` supplies one ~500-word synthetic scene per genre territory (`queer-romance-scene.md`, `cozy-scene.md`, `philosophical-scene.md`), each drafted to exercise that audit's activation path and planted signals, plus a `no-tag-baseline.md` negative control and a pre-registered `expected.md`. These are pure data (behavioral eval; no mechanical `validate.sh` arm parses them). The **eval-coverage confirmation report is a model run and remains deferred** (per the corpus-expansion survey) — the fixtures are authored; the sign-off run is not done.

### Single-agent vs. multi-agent staging A/B fixture pair

Pre-Pass Re-Grounding and Staged Visibility instructions are mode-conditional. Their less-observable single-agent mode lacked a paired fixture for direct A/B observation. **Fixtures authored:** `evals/fixtures/execution-mode-ab/` supplies a synthetic A/B pair — one shared `manuscript.md` with a registered ground-truth recall set, and `single-agent-config.md` / `multi-agent-config.md` mode wrappers, scored by a pre-registered `expected.md` (recall + the `docs/swarm-vs-single-eval.md` decision rule). These are pure data. **The run itself remains deferred:** per `docs/swarm-vs-single-eval.md` review finding B2, mode-as-a-variable cannot execute on the current in-repo harness without a dedicated build (mode-comparable orchestration + token capture), and this excerpt is a short schema/GT scaffold, not the powered long-fiction arm. The **eval-coverage confirmation report is a model run and remains deferred** — the fixture pair is authored; the sign-off run is not done.

---

## Deferred (Out of Scope for This Cycle)

Items deferred from the Phase 7 closeout per scope-control. Each has a documented rationale; each is a candidate for a future cycle if a forcing function justifies the investment.

### Python helpers for true Timeline parsing (A3) — **Delivered (v2.0.0–v2.1.0)**

Originally deferred from the Phase 7 closeout: Phase 7 plan §A3 specified four Python modules (`timeline_parser.py`, `timeline_arithmetic.py`, `timeline_anchor.py`, `timeline_diff.py`) to lift the bash-validator capability ceiling for Pass 10 Timeline verification. **Subsequently delivered** under §Validator Architecture Hardening (Increment 4): a single `scripts/timeline_checks.py` structured Timeline parser backs the three `timeline-*` arms, upgrading `timeline-arithmetic` and `timeline-anchor-conflict` from marker-hygiene to **true** span-overrun arithmetic and same-scene anchor-drift detection (the capability `pass-10.md` §Phase 7 explicitly deferred). The four originally-specified modules were collapsed into the one parser module; the bash implementations are retained as the no-`python3` degrade path.

### audit-signal-propagation §4e context-modifier extension — **Built**

Phase 7 plan §A2 specified three optional validators; the third (`audit-signal-propagation §4e context-modifier extension`) was deferred per scope-control. **Now built** (changelog fragment `section-4e-table-driven.md`): the `audit-signal-propagation` validator (`letter_checks.py`) no longer hardcodes the signal-class → synthesis-severity mapping — it **parses it from `pass-dependencies.md §4e`** (the `#### Default mapping` block) and honors a per-audit `propagate-override: <signal-class> → <synthesis-severity>` directive in a §4e row's Override column, making the propagation table fully driven by the `§4e` source of truth. A malformed §4e mapping is surfaced as an ERROR (hostile fixture); a per-audit modifier that reassigns the required severity is honored (hostile fixture). The port is oracle-identical on the real committed §4e — `--check-registry`, the byte-identical §4e diff, and `argument-carve-behavior-preservation` pass unchanged; no new validator (count stays 67).

### Codex `validateGeneratedWorkspace` allowlist maintainability

Wave 4 D2 host parity sweep finding 3: the codex build's `validateGeneratedWorkspace` function maintains a hard-coded allowlist of files where historical "Claude Opus" / `.claude-plugin/` references are intentional. Future framework additions with intentional historical references must update the allowlist by hand. Cosmetic / future-cleanup observation; defer until it bites.

### Canonical-framework validator runs as release gate

**Status: partially shipped (v2.0.0).** v2.0.0 added `validate.sh --check-all` and wired it into `release-verify.mjs`, putting *real-file* canonical invariants into the release gate for the first time: `audit-signal-propagation --check-registry` (the 42-audit Signal-Emitting Registry checked against `pass-dependencies.md §4e`) and `structured-findings` against the shipped templates (`findings-ledger-format.md`, `diagnostic-state-meta-template.json`). For those checks the class is closed — the gate now proves the *canonical framework* satisfies the validator, not just that the validator passes its own fixtures.

Original finding (Codex final critique, P1, v1.8.4): the `audit-tier-criterion` validator passed its synthetic self-test but failed against the actual canonical `pass-dependencies.md` it was built to police. The *class* of failure motivated the item: validator self-tests prove the validator works on its own fixtures, not that the canonical framework satisfies the validator.

**Progress.** Validator Architecture Hardening Inc 6 gated `audit-tier-criterion` (vs the real `pass-dependencies.md`), `decision-layer-check` / `audit-signal-propagation` / `severity-floor`, and the `timeline-*` arms (vs canonical worked examples). A follow-on then gated the rest of the **editorial-letter / ledger validator family** against the canonical worked examples: `underdiagnosis-triggers` + `ledger-consolidation` vs `example-editorial-letter.md`, and `deficit-lock` vs `example-findings-ledger.md` — so the *whole* letter/ledger family now proves the canonical framework satisfies it, not just that each validator passes its own fixtures.

**Run-folder validators now gated too.** A canonical *run folder* fixture (`core-editor/references/example-run-folder/`: a gate-valid Findings Ledger + an Audit Invocation Log + a `Diagnostic_State.meta.json` sidecar carrying an attested `run_synthesis` gate event) was added, and `--check-all` now gates the run-folder–shaped validators against it: `gate-state`, `escalation-check`, and `argument-recon-prerequisite` run read-only against the committed fixture, and the **gate engine** (`gate run_synthesis`) runs against a throwaway temp copy (it appends an event to the sidecar, so the committed fixture stays immutable). With that, every validator that has a single-artifact or run-folder canonical target is gated.

**Contract validator now gated too.** A canonical clean *Contract* worked example (`core-editor/references/example-quality-risk-contract.md`: a single-POV literary family drama at moderate darkness with a mid-draft developmental goal) was added, and `--check-all` now gates `quality-risk-triggers` against it — a clean arm asserting the contract raises none of the five pre-pass triggers (Q1-Q5) and exits 0, plus a hostile arm that flips the darkness rating to the top setting on a throwaway copy and asserts the Q1 consent/governance trigger fires (gate proven to have teeth). That closes the `quality-risk-triggers` hole below.

**Remaining:** only the self-test-only `artifacts-schema` (validates arbitrary embedded blocks; covered indirectly by `structured-findings` on the shipped templates) has no clean canonical target. Defer until a forcing function surfaces.

### Clearer §4e table-driven propagation framing — **Built**

Surfaced by Codex final critique (P3, v1.8.4): the `pass-dependencies.md §4e` framing could be sharpened with explicit table-driven language — naming each row's columns, formalizing the override-modifier column, and pulling the modifier semantics into the §4e header rather than the per-row prose. **Now built** (paired, as planned, with the `audit-signal-propagation §4e context-modifier extension` above): §4e carries a formalized **six-column contract** (*Audit · Audit-internal signal · Synthesis severity (required-severity) · Context modifier · Source · Override (override-modifier)*), each column's semantics named in the §4e header prose; the **override-modifier column** is formalized with a machine directive (`propagate-override: <signal-class> → <synthesis-severity>`); and the `#### Default mapping` block is declared the machine-parseable source of truth the validator parses. The framing was sharpened first, then the validator was wired to source-of-truth parsing, exactly as this item prescribed.

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

## Release-Readiness Review (2026-06-19)

A pre-v2.5.0 review. v2.5.0 is **staged but untagged**: `plugin.json` / `marketplace.json` already
read `2.5.0`, 11 `changelog.d/` fragments are accumulated, and the 81 unreleased commits are one
coherent theme — the **Annotated-Manuscript deliverable + export targets** (Obsidian, HTML,
DOCX→Google Docs). **GitHub CI for `main` is green on `ubuntu-latest` — the release is shippable.**
The items below are hardening / showcase work the review surfaced; none blocks the tag. **Several were
resolved in the same wave** (marked *Fixed*); the strategic items remain roadmap work.

### Cross-platform gate parity (Windows dev environment) — **Fixed (this wave)**

The three named CI gates all fail *locally on Windows* for environment reasons, not content — so a
maintainer following `AGENTS.md`'s "run the real CI command first" discipline on the Windows rig gets
spurious red, which trains reviewers to ignore the gate (the dangerous failure mode). All three are
checkout/locale artifacts; CI is green on Linux.
- **`validate.sh --check-all`** — 9/48 validator self-tests crash with `UnicodeDecodeError` on byte
  `0x97` (the cp1252 em-dash): the self-test fixture writers use bare `open(..., "w")`, so on a
  cp1252 default-locale box the fixture is written non-UTF-8 and the UTF-8 reader chokes. Confirmed:
  `PYTHONUTF8=1 bash scripts/validate.sh --check-all` → **all 48 pass**.
- **`release-generate.mjs --check`** — "Pattern not found for root README grouped command list": the
  README is checked out CRLF (`core.autocrlf=true`, no `eol=lf` in `.gitattributes`) and the script's
  `\n`-anchored regexes don't match. The raw blob is LF, so Linux CI passes.
- **`build-codex.mjs --self-check`** — a Claude-specific-reference false positive because the
  generated path uses Windows backslashes and the allowlist matches forward slashes.

**What landed:** `* text=auto eol=lf` in `.gitattributes` (zero-renormalization — all blobs were already
LF — and it future-proofs the byte-identical dual-script mirror against EOL drift); `encoding="utf-8"`
pinned on all **70** text-mode fixture/output writers across the validator suite (root-cause fix, so
`bash scripts/validate.sh --self-test-all` is **48/48 without `PYTHONUTF8`** on a cp1252 box); and a
`path.sep`→`/` normalize before build-codex's allowlist match. After a `.gitattributes` refresh
(`git add --renormalize .` once, post-merge), `--check-all` is green on the Windows rig. A follow-on
(#118) then pinned `newline=""` on the **93** text-mode output writers (+ the one `os.fdopen` sidecar in
`run_gate.py`) so a fresh build is LF on every platform — otherwise, once the fixtures are LF, a
CRLF-on-Windows build wouldn't byte-match them.

**Tracked residual (demand-gated):** `scripts/sync_setec.py`'s `Path.write_text` calls still lack
`newline=`. It's **root-only** (not part of the byte-identical mirrored validator set) and its outputs
are regenerated via `sync_setec.py` rather than byte-compared, so it doesn't affect any gate — fix only
if full-tree Windows EOL determinism is ever wanted.

### Input-encoding robustness — **Mostly fine; small follow-up**

*Correction to the initial review, which overstated this.* The **manuscript-reading** family
(`annotation_export.py`, `reanchor.py`, `regression_diff.py`) already catches `(OSError,
UnicodeDecodeError)` and degrades — the user-facing path does **not** crash on a non-UTF-8 manuscript.
The other ~18 `_read` helpers raw-crash on non-UTF-8, but they only ever read **tool-written** artifacts
(ledgers, sidecars, letters) that are UTF-8 by construction (now doubly so, with the writers pinned). So
the residual is a small consistency follow-up, not a confirmed user crash. The right shape is **fail-loud**
(a clear "must be UTF-8" message naming the file), **not** the `regression_diff`-style swallow-to-`None`,
which produces a *silent* wrong answer — the worse hazard. Demand-gated; no fixture exercises it today.

### Showcase the v2.5.0 marquee deliverable — **Built (this wave)**

v2.5.0's theme is the Annotated-Manuscript deliverable — "the #1 human-DE deliverable"
(§Annotated-Manuscript Deliverable). Added [`sample-annotated-manuscript.html`](sample-annotated-manuscript.html)
(rendered from the canonical `example-annotated-manuscript/` fixture via `annotation_export.py html` — a
self-contained, browser-openable file with severity-tagged, bidirectionally-linked margin findings) and a
"See It in Action" entry linking it on GitHub Pages, beside the letter / audit / pre-writing samples.

### Repo-browsable version history — **Partly fixed (this wave)**

The "Done" section is **backfilled** with v2.3.0 / v2.3.1 / v2.4.0 (shipped tags that had no entry), so the
in-repo history is complete through the current release. Still open as a deliberate choice: whether to
**commit the assembled `CHANGELOG.md`** at release (history in-repo) rather than only in `changelog.d/`
fragments + GitHub Releases. (For reference, the current suite is **48 validators**; `registry-check`'s
"43" is the separate signal-emitting-audit count.)

### README host-positioning — **Fixed (this wave)**

The install routing table listed Claude Code (CLI) and Cowork as first-class rows while the section header
called them "legacy host flow." Dropped the contradictory "legacy" framing (header + body) so the headers
agree with the table; ordering unchanged (Antigravity / Codex still lead). *If the intent was to actively
de-emphasize Claude Code / Cowork, re-add an explicit note — this fix only removed the contradiction.*

### Toward "truly great" (strategic) — **Planned**

Beyond hardening: the framework is a deep *diagnostic* instrument, and the highest-value next moves are
**not more capabilities** (the roadmap's restraint is correct). Three investments move it from
remarkable to indispensable:
1. **Published, reproducible validation.** The success condition is already written down (§Benchmark
   Suite: "two serious editors usually converge on the core claim, top failures, burden mismatch,
   strongest objection"). Measure and publish it — even at small N — for **fiction** (F1–F4) as well as
   argument (gated today only on recruiting a second editor). A trust story of "here's the measured
   inter-rater agreement" beats "trust the discipline." The #1 strategic item; it also matches the
   maintainer's settle-confusions-with-small-experiments workstyle.
2. **Close the revision loop into the writer's editor. — Workflow glue Built, 2026-06-20.** v2.5.0 ships
   the annotated copy *out* (DOCX→GDocs comments). The sticky move is the **round-trip**: ingest the
   writer's revised draft and re-anchor the notes. The `reanchor` validator already classifies held /
   moved / vanished / ambiguous — the glue that was missing (a real round-trip workflow, not just a gate)
   is now built: a `reanchor.py emit` subcommand that **writes** the re-anchored manifest + the rendered
   annotated copy of the *revised* draft (held/moved only, re-gated RA1–RA3 before any write), a
   `reanchor.py crossref` subcommand that **joins** the anchor-level classes against `regression-diff`'s
   finding-level classes by `finding_id` (the §Q2 orchestrator join), and the Revision Round Protocol
   wiring (`state-lifecycle.md` §Round-Trip Re-Anchoring: snapshot → emit → crossref), proven end-to-end by
   a `--check-all` `round-trip glue chain` gate. Spec: `docs/annotated-manuscript-reanchoring.md`
   (Increment 2). A one-shot letter is a product; a revision loop in the writer's tool is a habit.
   *The remaining last mile is closed: surfaced as the `/start` round-trip resume offer at the
   bound-project `revising` and `diagnosed` nodes, with the operator-confirmed disposition round-close
   (`roundtrip-disposition`, RT1–RT4 + `rev-a4` — Increment 3), 2026-07-01.*
3. **Finish the visualization leg.** Charts 1–3 ship (pacing, POV, severity-by-chapter), **and chart
   7-nonfiction — the claim ladder — now ships render-only** (Manuscript-Visualization Completion M1:
   C0 + subclaims + per-rung support coverage over `argument_spine.v1` + `support_plan.v1`, no scene
   axis, no new schema/validator). The character co-presence network, scene-function heatmap,
   reveal-economy timeline, and beat-map-against-spine (§Horizon Tier 1, item 1) remain producer-gated
   — each is gated on a producer increment that makes its upstream artifact machine-readable. Highest-ROI
   "render what you already produce" work after validation.

---

## Done

### v2.7.0 — State-Seams Wave, Multi-Session Arc Planning & Co-Presence Network
Additive; no command/API break. The **state-seams wave** hardens the diagnose⇄revise loop's seams. **One-click round-trip resume** surfaces at `/start`'s `revising` + `diagnosed` nodes (Increment 1) with a `reanchor.py` disposition gate (RT1–RT4 + W1, Increment 2). **Finding dispositions** — a declined/deferred overlay that is explicitly *not* a lifecycle state (anti-laundering by construction: no disposition can improve on a declined Must-Fix), with a marker-grammar SSoT and the `disposition-check` validator. **Finding disconfirmation** — HIGH now means *survived a recorded refutation attempt* (the Step-6b Finding Disconfirmation Pass; `refutation_check.py` + three `validate.sh` arms; the refuter never sees severity or confidence — anti-anchoring). **Synthesis coverage disclosure** (M1 — the read manifest + letter coverage note + `synthesis_coverage` sidecar/validator) plus **pre-letter re-grounding** (M2 — re-read spans flip their manifest rows, so disclosure gets *better* on contact with the text). Also: **Multi-Session Revision Arc Planning** (the `revision-arc` validator + `apodictic.revision_arc.v1`, one arc per manuscript), **Manuscript-Structure Visualization chart 5** (character co-presence network — the first producer-gated chart to land), the **Validation & External Evidence** lane added to the roadmap, and the **SETEC contract re-sync** to v1.118.0. Hardening: a UnicodeDecodeError class-sweep across every OSError-only artifact reader, `specificity_floor` fail-*closed* on an unreadable required artifact, and disposition-supersedence recompute-don't-trust. Released `#166`, 2026-07-02.

### v2.6.2 — Override-Marker SSoT Hardening
Additive; no behavior change to green runs. Routes **18 validators through a single `override_marker` source-of-truth** so structured-dissent detection (the `<!-- override: … -->` path) is parsed identically everywhere instead of by per-validator regex, closing a fleet-wide substring-match class. Folds #148 review P2s: CRLF fence closing and drafted-copy backtick payloads. Released 2026-06-26.

### v2.6.1 — Audit Carding & Persona-Divergence Severity Hardening
**Registers the two genuine new specialized audits — Content Advisory + Reader-Persona Simulation — on the marketing/inventory surfaces** (`release-registry.json`) and adds the `check-inventory-parity` gate so a shipped specialized-audit reference that isn't carded (or explicitly `NOT_CARDED`) fails CI. Two Codex #146 P1 follow-ups: the `files[0]`-primary binding gate (a ref misattached as a non-primary file no longer passes coverage) and persona-divergence **D3 severity equality**, including the Timeline-anchor path where an asserted Must-Fix over a no-locked-severity anchor was a silent severity sink. Released 2026-06-22.

### v2.6.0 — Horizon Tier-1 Wave: Annotated-Manuscript Deliverable + Extraction Audits
The largest capability release since v2.0.0 — it completes **Horizon Capacities Tier-1**. **Annotated-Manuscript Deliverable** (the #1 human-DE deliverable): locus-anchored margin comments (Increment 1), character-precise quote anchoring + the A6 quote-integrity gate (Increment 2), letter↔margin cross-links (Increment 3), the producer that wires it into the run flow, plus **round-trip re-anchoring** and **draft-over-draft `regression-diff`**, and four render targets — Obsidian (footnotes + bidirectional wikilinks), self-contained HTML, and **DOCX with anchored Word comments that Google Docs imports natively**. **Horizon Tier-1 extraction audits:** Promise-Contract Fidelity (#4), Reader-Persona Simulation (#5), Auto-Derived Continuity Bible (#7), Content-Advisory / Sensitivity-Surface Derivation (#8), Cross-Manuscript Author Voice/Craft Fingerprint (#9), Uncertainty-Resolution Intake Interview (#18), Interpretable Stylometric Explanation (#19, M1). **Tier-2:** the standalone Worldbuilding-Bible coherence tool (#13) and the Nonfiction Argument Engine **genre layer** for grants / academic papers / pitch decks (#11, M1). **Visualizations:** the render-only nonfiction claim ladder (chart 7). **Harness:** the Harness Contracts v2 keystone — the `schema-coverage` gate + opt-in closed-key (`additionalProperties:false`) enforcement — and the run-level **Research / API reliability layer** (M1). CI gained a version-parity gate + a weekly release-readiness nudge, and a long Codex-hardening tail across the new validators (override-marker fleet-wide, content-advisory negation scope, persona-divergence D4, intake I4). Released `#145`, 2026-06-22. *(No v2.5.0 — the wave shipped as v2.6.0.)*

### v2.4.0 — Argument-Engine Calibration, Command Trim & Legal-Risk Wiring
Additive on top of v2.3.1; no API break. **Nonfiction Argument Engine:** Dialectical Clarity classification **rule 2a** — an AT3 *recommendation* that discharges none of its comparative burden (BP5 + OB3, no funding mechanism) is not evaluable as a recommendation → **Structurally Unsound** (FM-A10, "The Uncompared Proposal"). Post-benchmark it was narrowed so that naming *any* alternative — even a strawman foil — counts as partial discharge (a Should-Fix soft spot), with an anti-gaming clause so a merely decorative foil can still be Unsound via the general evaluability test. Aligns the engine with the `policy-brief-uncompared` ground-truth key (GT7 = UNSOUND); verdict-behavior change, gated on a benchmark convergence run. **Command surface trimmed to 13** — retired `/revision-plan`, `/develop-edit`, `/diagnose`, all reachable through `/start`. **Validators:** `finding-trace` completion glob narrowed to `*_Revision_Report_*.md` so a deadline `*_Revision_Calendar_*.md` isn't mis-counted as a completion. **Legal Risk Register:** a detection layer (per-class signals + severity modifiers + ~20-code escalation-trigger taxonomy) and router wiring — `constraint:risk` offer-then-attach + a `/legal-risk` command. **Onboarding:** README install decision-aid table + a Key Terms glossary.

### v2.3.1 — Decoupled UI Generation & Host-Bundle Distribution
`release-generate.mjs` no longer reaches into the private APODICTIC-Gemini sibling to write its `App.tsx` / `LandingPage.tsx`; the app now **pulls** this repo's vendored `release-registry.json` and runs its own generator (−175 lines of dead TS-emit), fixing the silent drift when the sibling wasn't checked out at release. The generated `codex/` + `antigravity/` workspaces are **no longer committed** — a new `.github/workflows/release.yml` builds them from the canonical `plugins/` source and publishes them as release assets on `v*` tags (`apodictic-codex-marketplace.zip`, `apodictic-antigravity.zip`, `apodictic.plugin`), so install is download-and-open and the ×3 parity-churn multiplier is gone (GitHub #52, Option B). `release-verify.mjs` + CI now `--self-check` the host builds, and CI gained generator/parity gates (`release-generate --check`, both build `--self-check`s, `assemble-changelog --check`).

### v2.3.0 — Retcon Planning, Legal Risk Register & Nonfiction Pre-Draft
Captures capability that merged to `main` after the v2.2.0 release commit without a bump; additive, no command/API break. **Retcon Planning** (a `/coach` revision-coaching track) accounts for the *setup debt* a late structural decision incurs, governed by a commitment budget; planning-only (Firewall). **Legal Risk Register** flags defamation / privacy / rights-clearance exposure for work portraying identifiable real people — *flag, don't practice law*. **Nonfiction Pre-Draft Pathway** — thesis-driven pre-writing that plans the argument spine and seeds `Argument_State.md`. **Adaptive Mode Escalation: de-escalation** — steps *down* an over-provisioned mode when Tier 1 reveals a simpler manuscript (strictly conservative, never below `sequential`). Validators **23 → 35** (5 new — `retcon-plan`, `state-card-diff`, `legal-risk`, `scene-ethics`, `argument-spine` — plus self-test coverage for 7 pre-existing pure-utility validators).

### v2.2.0 — Operator Modes, Feedback Triage & Revision Follow-Through
Additive on top of v2.1.0; no command/API break. **Operators:** two output-presentation modes close the intake-router operator gaps — **Editor Scaffolding** (`operator:editor`, a superset overlay re-aiming the editorial letter at a human developmental editor: Editor Brief, What-You-Might-Have-Missed, Intervention Menu) and **Diagnostic Vocabulary** (`operator:facilitator`, a Vocabulary Guide teaching aid: grounded glossary + question-framed discussion prompts). **Workflows:** **Feedback Triage** increment 1 (sort/validate/prioritize external feedback; `apodictic.feedback_item.v1`, `/triage-feedback`). **Infrastructure:** **Adaptive Mid-Run Mode Escalation** (condition-triggered post-Tier-1 checkpoint that recommends escalating execution mode). **Harness:** **Finding Lifecycle IDs** increments 2–3 extend `finding-trace` into the revision loop (revision-plan follow-through E4/W2; revision-completion E5/W3 on an explicit `<!-- resolved: F-… -->` marker). Validators **19 → 23** (`escalation-check`, `feedback-triage`, `editor-scaffolding`, `diagnostic-vocabulary`); `--self-test-all` 23/23, `--check-all` + `release-verify` green.

### v2.1.0 — Runner-Governed Execution & Finding Lifecycle IDs
Harness Engineering: the prompt-governed → runner-governed step. **Runner-Governed Execution** lands the cooperative gate engine (increments 1–3: declarative manifest `execution-gates.v1.json` + `scripts/run_gate.py` behind `validate.sh gate <phase> <run_folder>`; sidecar `execution` state; finding-ID lifecycle) and **structured gate-event records** (increment 5): the per-phase `gates` map is replaced by an append-only `execution.gate_events[]` log (`apodictic.gate_event.v1`) with `phase`/`allowed_next`/`pending_gate`/`finding_states` as a recomputable resume pointer, a `mechanical-passed`→`--attest` attestation handshake (a `passed` clears only with `attested_items` covering its own snapshotted `attested_contract`), durable history, and safe grandfathered migration — all enforced by a new `gate-state` validator. **Finding Lifecycle IDs** increment 1 adds `finding-trace` (cross-artifact referential integrity + sidecar lifecycle coherence by `apodictic.finding.v1.id`). The **Argument Benchmark** ground-truth validator `argument-groundtruth-check` (GT1–GT7) also landed. Validators **14 → 19** (`gate`, `gate-state`, `finding-trace`, `argument-groundtruth-check`, `artifacts-schema`); `--self-test-all` 19/19. Still cooperative — external host orchestration (RGE increment 4) and revision-plan follow-through (FLI increment 2) remain future.

### v2.0.0 — Editorial Honesty & Structural Integrity
Five-phase subtraction-and-hardening pass. **Subtract:** bookkeeping moved out of the always-loaded judgment files into on-demand references (instruction floor −9.5%); `.gitattributes` collapses the generated mirrors in review. **Normalize severity:** one canonical Must-Fix/Should-Fix/Could-Fix scale with the orthogonal axes (confidence, prose tier, readiness, lens verdicts) named as not-severity, plus a 42-audit Signal-Emitting Registry enforced by `audit-signal-propagation --check-registry`. **Structured state:** real-JSON `apodictic.finding.v1` blocks + Python validator (`structured_findings.py`), required for synthesis-bound findings and mirrored into the sidecar under a triage-tally invariant. **Harden honesty (behavior change):** the Deficit Lock generation-order rule locks severities at Triage before any charity reframing, with the Distinguish / literary-exception / Stillness hatches gated so charity is legible; `honesty_check.py` drives `softness-check` (delivered-vs-locked, read from the Severity Calibration appendix) and `deficit-lock`. **Plumbing:** API exponential backoff honoring Retry-After, no-sticky-error caching, response-cache disk persistence, and full decoupling of the public release path from the private Gemini sibling; `release-verify` runs `validate.sh --check-all`. Validators 11 → 14.

### v1.9.0 — AI-Prose Calibration v2.0
Three-layer architecture extending the v1.0 audit. Layer A distributional pre-scan: variance_audit (single document), manuscript_audit (cross-chapter), repetition_audit (vocabulary diagnostic), eleven signals against personal/genre baseline with z-score band classification. Layer B named subtypes: AIC-2 Indefinite-Pronoun Gesture; AIC-7 Negation Hedge, Disguised Correctio, Pseudo-Aphorism, Manifesto Cadence. Argument-shaped nonfiction parallel set: Abstraction Shielding, False-Balance Construction, Hedge-and-Affirm, Recommendation Template, Authority Laundering. Layer C Source Triage Pass: payoff test, voice slip vs. lost callback distinction, earned-by-frame verdict. Cross-detector caveat for AIC-4 / Pangram signal-9 tension. Source-triage modifier table layered onto existing severity translation. v1.0 spec preserved verbatim — additions are integrative.

### v1.7.0 — Harness Engineering
Machine-readable sidecar state (`Diagnostic_State.meta.json`) with enumerated resume dispatch. Mechanical validation script (`validate.sh`) for contract integrity, ledger structure, artifact naming, and 14-heading synthesis section verification — bundled in plugin tree for Codex. Post-synthesis evidence spot-check (5 claims verified against manuscript). State gardening protocol (threshold-triggered archival). Enhanced `/start` resume gate with context-aware summary and state gardening trigger. Refactored `run-core.md` into three files: `run-core.md` (orchestration + pass specs), `run-synthesis.md` (audit integration, synthesis, deliverables), `state-lifecycle.md` (gardening, revision rounds). Cross-references updated across all callers.

### v1.4.0 — Surface Hardening & Writer's Block
Writer-Question Surface Hardening: command taxonomy in release-registry (11 commands with category/status/writer question), doc sync via release-generate, canonical 8-block macro map (Pass 4 → Emotional Dynamics), pass-detail artifact headers, Results Guide artifact, skill names scrubbed from user-facing copy, handoff language standardized. *(The last two — items #6/#7 in §Writer-Question Surface Hardening — were listed here at v1.4.0 but not fully closed until the 2026-07-06 scrub + convention pass; the residue is now cleared and the build-list is reconciled.)* Writer's Block & Rut-Breaking module: 8-type expanded block taxonomy (replaces 3-way split), 7 structural prompt families, 5-part firewall test, clinamen clause, perfectionism modifier, nocebo inoculation, no-prompt zones, Structural Experiment session plan section, integrated into both fiction and argument coaching.

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
