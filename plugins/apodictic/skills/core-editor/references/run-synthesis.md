# Core DE Synthesis & Deliverables

*Reference file for the APODICTIC Development Editor. Loaded after all passes complete.*
*Prerequisite: `run-core.md` (pass execution and Findings Ledger must be complete).*

---

### Audit Integration Point

After all core passes are complete and before writing the synthesis:

1. **Run auto-run audits first.** All audits with **auto-run** policy (see `pass-dependencies.md` §4c) are synthesis dependencies. They must complete and append their findings to the Findings Ledger before synthesis begins. Execute them immediately after their prerequisite passes are complete. Auto-run audits include: AI-Prose Calibration (when `constraint:ai`), Erotic Content (when erotic content flagged at intake), Memoir & CNF (when memoir/CNF), Narrative Nonfiction Craft (when narrative nonfiction), Series Continuity (when series continuity concern flagged).
2. **Review accumulated audit triggers.** Compile all finding-driven recommendations from Passes 1, 2, 5, and 8.
3. **Compare against contract-activated audits.** If a finding-driven trigger recommends an audit already activated at contract, confirm it should run. If it recommends an audit not activated at contract, present the recommendation to the author with evidence.
4. **Apply the high-risk blind-spot gate.** Before synthesis, explicitly check whether any of these risk classes are live:
   - **AI-origin fluency risk** — AI-assisted draft disclosed, or Pass 1 / Pass 5 flags uniform fluency, lexical genericism, puppet dialogue, or register seams
   - **Consent / governance risk** — intimate or power-dynamic material where consent architecture, conditioning, coercion, aftercare, or governance legibility is a live interpretive problem
   - **Reception / extractability risk** — contested representation, likely screenshot/excerpt vulnerability, hostile-reader portability, or representation context active contestation
   - **Series consequence risk** — cross-volume state drift, consequence reset, thread amnesia, or continuity pressure across volumes

   For each live risk class:
   - run the relevant audit before synthesis when policy or user acceptance allows;
   - if the audit is declined or deferred, record the blind spot in the Audit Invocation Log and carry it into synthesis as a confidence limiter.

   Relevant audits:
   - AI-origin fluency risk -> **AI-Prose Calibration**
   - Consent / governance risk -> **Consent Complexity**
   - Reception / extractability risk -> **Reception Risk**
   - Series consequence risk -> **Series Continuity**

5. **Run auto-recommend and user-accepted audits.** Load the full specialized audit module from `specialized-audits/references/` and apply to the manuscript. Each audit produces its own findings document. If an auto-recommend or user-accepted audit completes before synthesis begins, its findings are integrated. If it completes after, label it as a post-synthesis audit in the appendix and name the resulting blind spot in the editorial letter or readiness assessment when material.
6. **Write the Audit Invocation Log.** Before synthesis, produce a log artifact tracking every audit considered during this run. Format:

```
## Audit Invocation Log

| Audit | Source | Status | Reason |
|-------|--------|--------|--------|
| Stakes System | universal | run | Recommended at intake |
| Decision Pressure | universal | run | Recommended at intake |
| Scene Turn | universal | run | Recommended at intake |
| [audit name] | contract | run/skipped | [why] |
| [audit name] | finding-driven | run/skipped | [trigger evidence or skip reason] |
```

**Source** = `universal` (always recommended), `contract` (genre/mode-driven at intake), or `finding-driven` (triggered by pass findings).
**Status** = `run`, `skipped` (author declined), or `deferred` (postponed to Full DE).
Save as `[Project]_Audit_Invocation_Log_[runlabel].md`.

7. **Feed audit findings into synthesis.** Specialized audit findings integrate into the editorial letter's "What Needs Work" sections — organized by problem, not by audit name. The author reads about the book's needs, not about which framework found the issue.

**Cross-audit finding-driven triggers:**
- **Representation Context** research mode surfaces active community contestation relevant to the manuscript's content → recommend **Reception Risk** audit if not already activated

**Minimum audit recommendations for every manuscript:**
- **Stakes System** — universal pressure architecture diagnostic
- **Decision Pressure** — universal choice plausibility diagnostic
- **Scene Turn** (Bickham) — universal scene-level mechanics diagnostic

These three audits address craft concerns that apply regardless of genre. They should be recommended at intake and confirmed by the author.

---

## Core DE Synthesis

The synthesis is the author-facing editorial letter. It must read as one informed voice talking about a book — not as a framework generating output.

### Pre-Synthesis Gate (Required)

**Run `scripts/validate.sh gate run_synthesis <run_folder>`, confirm each `ATTEST` item it prints, then run `scripts/validate.sh gate --attest run_synthesis <run_folder>` to clear the gate; do not begin synthesis until that clears (exit 0).** The first call runs the *mechanical* checks below (ledger structure + consolidation, structured-findings, deficit-lock, artifact naming) from `schemas/execution-gates.v1.json` and records a `mechanical-passed` event (checks green, attestation owed). The items it lists as `ATTEST` (selected-pass + auto-run-audit completeness, blind-spot recording) are contract/judgment-based and remain yours to confirm; `--attest` re-runs the mechanical checks (so a clean pass can't ride stale evidence) and, only if still clean, records the **clearing** `passed` event. The checklist below is the human-readable expansion of that gate.

> **Degradation (no shell).** Perform the mechanical checks inline, confirm the `ATTEST` items, then append one combined clearing event to `execution.gate_events[]` in the sidecar: `{"gate":"run_synthesis","result":"passed","provenance":"attested","ts":"<date>","attested_items":["syn-a1","syn-a2","syn-a3"],"attested_contract":["syn-a1","syn-a2","syn-a3"],"note":"no shell; inline checks"}` (the attested IDs are `entry_requires.attested[*].id` in the manifest). Append-position is the order; do not write a `gates` map.

Before beginning synthesis, verify:

1. All selected Tier 2 passes are complete
2. All **auto-run audits** (per contract and constraint flags) are complete
3. The Findings Ledger includes entries from both passes and auto-run audits
4. The Audit Invocation Log is written
5. Any deferred or declined high-risk audit is recorded as an explicit blind spot
6. **Mechanical checks (run before synthesis begins):**
   - Final ledger structure validation — verify all pass entries have required subsection headings (script or inline per `run-core.md` §Mechanical Validation Protocol)
   - Pass artifact naming — verify all output files match `[Project]_Pass[N]_[Name]_[runlabel].md` convention

If any auto-run audit has not completed, do not begin synthesis. Complete the audit first. Synthesis written without auto-run audit findings must be rewritten — this wastes tokens and produces incomplete editorial letters.

### Processing Protocol

**Processing order (what the LLM does internally):**

1. **Intent Check Loop.** Before finalizing any flag, verify against stated intent: "I detect [observation] in [location]. Is this the [stated intentional element], or unintentional?" Do not flag elements that align with contract, controlling idea, or stated non-negotiables.

2. **Audit Finding Consolidation.** Before root cause analysis, integrate supplementary audit findings with pass findings. Consolidation rules:
   - **Map audit flags to pass findings.** Each audit flag should connect to the pass finding(s) that triggered or support it. Audit flags that duplicate a pass finding are evidence for that finding, not separate items.
   - **Cluster by problem, not by audit.** If Stakes System flags STX-2 (Abstract Risk Persistence) and Decision Pressure flags AV-1 (Option Suppression) at the same decision point, they describe one problem (the decision fails because stakes are too abstract to generate real options), not two.
   - **Preserve audit-specific diagnosis when distinct.** If an audit surfaces a problem that no pass detected (e.g., Decision Pressure identifies a pattern of deferred consequence erasure that passes didn't flag), it enters root cause analysis as a distinct finding.
   - **Count consolidated problems, not individual flags.** A single root cause may have 8 audit flags supporting it. The flags are evidence; the root cause is what enters triage.
   - **Carry audit artifacts forward.** Audit-specific tracking artifacts (Decision Event Map, Stakes Ladder Map, Scene Turn code inventory, etc.) become appendix material. They support the editorial letter's arguments but don't appear in the letter body.

   **Canonical Audit-Signal Propagation Rule.** The three synthesis-layer tiers (Must-Fix / Should-Fix / Could-Fix) are defined canonically in `output-policy.md §Canonical Severity Scale`, which also names the orthogonal axes (confidence, prose tier, readiness) that are *not* severity. Audit-internal severity signals do not become synthesis-layer Must-Fix / Should-Fix decisions automatically — the model must propagate them. Without an explicit rule, audit-internal signals (Compression Must-Fix floors, Reception Risk hard gates, Banister HIGH ratings) reliably die inside the audit findings file even when the model integrates the audit's narrative content into the editorial letter. The rule:

   | Audit-internal signal | Propagates to synthesis as |
   |---|---|
   | Audit-internal Must-Fix floor | Synthesis Must-Fix |
   | Audit-internal hard gate | Synthesis Must-Fix |
   | Audit-internal HIGH / Alert | Synthesis Must-Fix or Should-Fix (per audit context) |
   | Audit-internal MEDIUM / Flag | Synthesis Should-Fix |
   | Audit-internal LOW / Note | Synthesis Could-Fix |

   For each audit that ran, scan its findings file for these signal classes and confirm each one appears at the rule-mandated severity in the synthesis layer (root causes, Must-Fix flags, Should-Fix flags, or revision-checklist items). **Per-signal verification (v1.7.9).** Propagation is verified per-audit, per-signal — not by the mere presence of *some* Must-Fix or Should-Fix item in the synthesis body. A Reception Risk hard gate in Appendix A is propagated only when the synthesis-body Must-Fix list contains either (a) a finding that names the audit by name (e.g., "Reception Risk Alert at L2956") or (b) a finding that cites at least one evidence line number that also appears in the audit's appendix subsection. An unrelated Must-Fix in the body — e.g., a Decision Pressure flag at a different scene — does not satisfy the Reception Risk propagation requirement. The validator (`scripts/validate.sh audit-signal-propagation`) implements this per-audit, per-signal check as of v1.7.9; prior versions accepted any body Must-Fix as evidence and produced false passes.

   **Override path.** The model may decline to propagate at the rule-mandated severity when the audit signal is genuinely an artifact-of-method (e.g., a hard gate fired on a passage the manuscript itself has already retracted, or an Alert that survives only by ignoring stated authorial intent). Deviation requires a structured marker placed **in the letter body** (not in an appendix) near the affected finding, plus a parallel narrative entry in Appendix B (Severity Calibration). Marker syntax (one per propagation class):

   ```
   <!-- override: audit-propagation-must-fix — <one-sentence rationale> -->
   <!-- override: audit-propagation-hard-gate — <one-sentence rationale> -->
   <!-- override: audit-propagation-high — <one-sentence rationale> -->
   ```

   A per-audit override marker form is also honored (v1.7.9), allowing a single override scoped to one audit rather than the whole class:

   ```
   <!-- override: audit-propagation-<audit-slug> — <one-sentence rationale> -->
   ```

   where `<audit-slug>` is the lowercase-hyphenated audit name (e.g. `reception-risk`, `compression`, `banister`). Use the per-audit form when one audit's signal is genuinely artifact-of-method but other audits at the same class still warrant propagation.

   Markers in appendix bodies are non-canonical (synthesis body is canonical for findings; appendices hold evidence) and do not satisfy the override path. **Absence of marker and rationale = blocked synthesis** — propagate at the rule-mandated severity or override-with-reason in the body; do not silently drop the signal.

   **Mechanical check.** Run `scripts/validate.sh audit-signal-propagation <editorial_letter_file>` (or perform the equivalent inline check on hosts without shell execution) before delivery. The validator surfaces un-propagated signals; the model still owns the final severity decision but must justify any deviation.

   **Per-audit specifics live elsewhere.** This rule is the *propagation taxonomy*. Per-audit applicability — e.g., which Reception Risk hard gate maps to synthesis Must-Fix vs. Should-Fix in which manuscript class, or how Banister HIGH-confidence findings calibrate against thematic-coherence verdicts — lives in `pass-dependencies.md §4e — Audit-Signal Propagation Table`. The validator `scripts/validate.sh audit-signal-propagation` reads §4e to verify compliance. Audits not enumerated in §4e fall back to the column-2 default mapping above; the override path applies to principled per-finding exceptions in either case.

   **Pass-10-Class artifact integration (Timeline).** When Pass 10 ran and produced a `Timeline.md` artifact at the project root, its Section 4 (Inconsistency Ledger) counts feed synthesis severity per the same propagation taxonomy. Pass-10-Class artifacts are not audits; they are rolling structured state. But the Inconsistency Ledger entries function as audit-equivalent signals and propagate per these thresholds:

   | Timeline signal class | Trigger | Synthesis-layer effect |
   |---|---|---|
   | `paradox` rows in Inconsistency Ledger | ≥1 | Must-Fix candidate (timeline coherence) |
   | `drift` rows in Inconsistency Ledger | ≥3 | Should-Fix candidate (revision-drift hygiene pass) |
   | `ambiguity` rows tied to load-bearing structural elements | Any (climax positioning, intervention windows, character-development arc spans) | Author Decision |

   The same override-path discipline applies: a timeline paradox that is artifact-of-method (e.g., the manuscript itself flags the paradox as character-perception) can be downgraded with a structured marker in the synthesis body. Markers in Timeline appendix or in the Diff Notes section are non-canonical for synthesis-severity purposes. See `references/pass-10.md §Synthesis Integration` for the full Timeline artifact contract; see `references/pass-10.md §Validator Integration` for the three mechanical validators (`timeline-diff`, `timeline-arithmetic`, `timeline-anchor-conflict`) that surface candidates for the Inconsistency Ledger.

   Other Pass-10-Class artifacts (`Argument_State.md`, `Series_State.md`, future `Plot_Spine.md`) propagate signals through the same canonical rule. The taxonomy is artifact-class-agnostic; severity propagation is the same whether the signal originates in an audit findings file or a rolling structured artifact.

   **Findings Ledger Consolidation Contract.** Audit Finding Consolidation operates on a *consolidated* Findings Ledger, not the raw per-pass Ledger Snippets. Turning raw snippets into a consolidated by-mechanism ledger is the consolidation step. It is mandatory and must run after pass dispatch completes, before this audit-integration step begins. The contract:

   - **Inputs.** Raw Ledger Snippet sections from each pass artifact and each completed audit findings file (the "Notable Findings", "Cross-Pass Connections", "Unresolved Questions", and "Audit Triggers" subsections per `run-core.md §Findings Ledger Protocol`).
   - **Outputs.** A consolidated by-mechanism ledger where related findings from multiple sources cluster under a single mechanism heading (e.g., `## Mechanism: Aftermath Compression`) rather than appearing as parallel raw entries.
   - **Required transformations.**
     - **Deduplication.** Multiple raw entries describing the same underlying mechanism collapse to one consolidated entry; the source artifacts become an annotation, not separate entries.
     - **Cross-reference annotation.** Each consolidated entry that came from multiple sources includes an explicit annotation: `(confirmed by Pass 1, Pass 5, Reception Risk audit)` or equivalent. Single-source entries do not require this annotation.
     - **Severity collation.** When the same mechanism was rated at different severities by different sources, the consolidated entry shows the resolution. By default, highest severity wins per the severity-floor rules; documented downgrades (with a one-sentence rationale) are permitted but must be visible (keyword: `collated`, `downgrade`, `upgrade`, `highest severity wins`, `resolved`).
     - **Cross-reference to source artifacts.** Each consolidated entry preserves a pointer back to the raw pass/audit artifacts where the underlying evidence lives (so synthesis can trace any finding back to its source for spot-checking).
   - **Reduction expectation.** A compliant consolidation produces fewer entries than the raw aggregate. Heuristic threshold: consolidated item count ≤ 70% of raw item count (i.e., ≥30% reduction). Single-pass runs and naturally low-friction manuscripts may legitimately fall below this threshold; in those cases use the override path.
   - **Validator.** Run `scripts/validate.sh ledger-consolidation <consolidated_ledger_file> [<raw_ledger_file>]` (or perform the equivalent inline check). The validator surfaces non-compliance; the model owns the final ledger structure.
   - **Override path.** Documented deviations use a structured marker in the consolidated ledger:

     ```
     <!-- override: ledger-consolidation-raw-aggregate — <rationale> -->
     <!-- override: ledger-consolidation-no-convergence — <rationale> -->
     <!-- override: ledger-consolidation-no-collation — <rationale> -->
     <!-- override: ledger-consolidation-no-reduction — <rationale> -->
     ```

   - **Single-agent vs. swarm.** The contract applies in both execution modes. In single-agent mode, consolidation is an inline sub-step the synthesis agent performs. In swarm/multi-agent mode, consolidation may be delegated to a dedicated subagent that reads all raw Ledger Snippets and writes the consolidated ledger; the synthesis subagent then operates on the consolidated output. Either way, the contract is the same.

3. **Blind Spot / Absence Inventory (required).** Before root cause analysis, explicitly scan the Findings Ledger to identify what is *missing* from the text rather than just evaluating what is present on the page. Missing elements (e.g., rushed sequence compression, lacking interiority, unsupported choice architecture) are often harder to detect because they leave no explicit textual footprint. Document an internal "Absence Inventory": what structural, emotional, or pacing elements *should* be here but aren't? This ensures the root cause analysis includes omission gaps.

   *Canonical home for the absence-first / deficit-first framing rule and for blind-spot disclosure as a confidence limiter. Other surfaces (`output-policy.md §Severity Honesty Protocol` rule #5, `submission-readiness.md §Blind-spot rule`, `pass-dependencies.md §4c` Auto-recommend before synthesis decline policy, `specialized-audits/SKILL.md §How to Use` Field Reconnaissance prerequisite paragraph) reference here. Per-audit Deficit-First Diagnostic Rule opening blocks in `specialized-audits/references/craft/*.md` are the operational, audit-tailored expression of this canonical rule and stay in their audit reference files; they are not generic restatements.*

   **Mandatory blind-spot disclosure: declined Field Reconnaissance on argument-shaped runs (Phase 6 Wave 3 / CR-4).** When a run is argument-shaped (constraint=nonfiction + persuasive-argument form per `pass-dependencies.md §4a`) AND Field Reconnaissance was not run — whether because the user declined the Hard Prerequisite or Auto-recommend before synthesis invocation, the user opted out at intake, or the run pre-dates the prerequisite policy — the synthesis layer MUST record "literature-counterevidence not surveyed" as a confidence-limiting blind spot in this Absence Inventory and carry it forward to Appendix A (Diagnostic Detail). The disclosure must name what is unsurveyed (competing studies, counter-citations, replication failures, opposing scholarly positions) and what the absence implies for synthesis confidence (Dialectical Clarity, Argument Red Team, and Argument Evidence Deep-Dive operated against a manuscript-internal claim graph rather than a literature-aware one). This disclosure is not optional for argument-shaped runs without Field Recon coverage; the §4c Auto-recommend before synthesis decline policy treats it as the canonical confidence limiter for this audit-class. For Pre-DE Prerequisite Citation Verifier declines on high-stakes argument-shaped runs, additionally name "citation provenance not verified" as the parallel confidence limit. Fiction runs and non-argument nonfiction runs do not require this disclosure (Field Recon is not prerequisited for those forms; absence is not a blind spot).

4. **Root Cause Analysis.** Read the Findings Ledger as the primary input for root cause analysis. The ledger's cross-pass connections are pre-built hypotheses about shared root causes — evaluate each. Identify 3-5 root causes (maximum 5) from the ledger's notable findings, cross-pass connections, and consolidated audit findings. If more than 5 seem present, flag that manuscript may need reconception. Audit findings that cluster under the same root cause strengthen the diagnosis; they don't multiply the root cause count. For any ledger finding that doesn't cluster under a root cause, carry it forward to the "Additional Observations" section (§4b) of the editorial letter.

5. **Triage.** Assign severity to each finding:
   - **Must-Fix:** Book-breaking (max 10)
   - **Should-Fix:** Significant diminishment (max 15)
   - **Could-Fix:** Polish (no cap, deprioritized)

   **Deficit Lock (required, generation-order).** The moment a finding is triaged Must-Fix or Should-Fix, commit it as a structured Finding (`apodictic.finding.v1`, see `findings-ledger-format.md`) at that severity in the Findings Ledger — **before** Step 6 (Adversarial Self-Check) or any later charity reframing runs. From here later steps may raise severity freely, but may only lower a locked severity (or drop a locked finding) by recording an **ID-scoped** body override marker `<!-- override: softness-downgrade F-… — <rationale> -->` — naming the finding's Lifecycle ID, so it acknowledges only that finding (a bare marker acknowledges nothing) — plus an Appendix B entry. Each locked finding keeps its **Finding Lifecycle ID** (`id`); when you deliver it in the letter, cite that ID in an HTML comment near the finding — in the **pinned canonical form `<!-- finding: F-… -->`** (see `output-policy.md §Deficit Lock`; this exact form is what the Annotated-Manuscript crosslink producer back-links against) — and in the Severity Calibration appendix so the gates can match locked→delivered by ID. Canonical rule: `output-policy.md §Severity Honesty Protocol → Deficit Lock`; enforced at Step 10 by `scripts/validate.sh softness-check <letter> <ledger>` and `deficit-lock <ledger>`.

6. **Adversarial Self-Check (required before writing the letter).** Re-evaluate findings in both directions — test whether each severity is too soft (under-diagnosed) or too harsh (over-escalated). Adjust if the adversarial case is stronger than the original assignment. Record the results.

   **Upward pressure (testing for softening):** For each Should-Fix flag, state in one sentence why it should be Must-Fix. If the Must-Fix case is stronger, upgrade. For each Mixed axis, state in one sentence why it should be Weak. If the Weak case is stronger, downgrade.

   **Downward pressure (testing for over-escalation):** For each Must-Fix flag, state in one sentence the best case for Should-Fix. If the Should-Fix case is stronger, downgrade. For each Weak axis, state in one sentence the best case for Mixed. If the Mixed case is stronger, upgrade.

   **Evidence check (both directions):** For each Must-Fix flag, confirm you have 2+ specific scene/line references. If not, either find them or downgrade your confidence (not the severity).

6b. **Finding Disconfirmation Pass (required — after the Step 5 Deficit Lock and the Step 6 Adversarial Self-Check, before Step 7).** An adversarial attempt to *refute* each high-stakes finding against the manuscript text. Every other adversarial surface points elsewhere: the Step 6 self-check tests severity *calibration* without re-contacting the manuscript, the Step 7 stress test attacks the *manuscript*, and the Evidence Spot-Check confirms the letter's *own* citations. This pass hunts **counter**-evidence — and it is what HIGH confidence now means for synthesis-bound findings: *survived a recorded disconfirmation attempt*, not merely converged-upon (`output-policy.md §Confidence Calibration`). Running after the Deficit Lock means severities are already structurally locked, so the pass physically cannot be a softening vector; Steps 8–10 then consume the re-mapped confidences and the letter (Step 11) is written with refutation outcomes already known.

   **Eligible set (bounded by construction):** locked, synthesis-bound findings where `severity == Must-Fix` (any confidence) **or** (`severity == Should-Fix` **and** `confidence == HIGH` at lock). Could-Fix and MEDIUM/LOW Should-Fix are out of scope. Findings carrying a `declined`/`deferred` disposition (`docs/finding-dispositions.md`) are skipped — the author already ruled; don't spend budget re-litigating — noted in the record's prose, not counted against the cap.

   **Cap: 15 findings per run**, processed Must-Fix first (ledger order), then HIGH Should-Fix (ledger order). The Must-Fix ceiling is 10 (`output-policy.md §Output Constraints`), so every Must-Fix is always processed — the cap can only ever bind on HIGH Should-Fix. **When the cap binds — disclose, never silently skip or demote:** the budget block records `bound: true` with `eligible`/`processed`; each unprocessed HIGH Should-Fix keeps its HIGH **only** with a near-finding marker `<!-- refutation: not-attempted-budget F-<ORIGIN>-<NN> -->` in the letter body plus an Appendix B narrative line, and its author-facing confidence language must say *convergence-only, not stress-tested* (two grades of HIGH, visibly distinct). The marker is honored by the validators only when the budget block says `bound: true` and the marked id has no record — a marker on a processed finding, or under an unbound budget, is an ERROR (the marker is a disclosure, not an exemption you can reach for).

   **Artifact — the Refutation Record.** The pass's entire write surface is one new artifact, `[Project]_Refutation_Record_[runlabel].md` in the run folder: prose-first (author-auditable rationale per attempt), with one machine-parseable `apodictic.refutation.v1` block per processed finding and exactly one `apodictic.refutation_budget.v1` block (fields `cap`/`eligible`/`processed`/`bound`, all required — the mechanical basis for cap-bound disclosure), in the established `<!-- apodictic:<type> { … } -->` envelope family (`findings-ledger-format.md §Companion structured blocks`). Field set is canonical in `plugins/apodictic/schemas/apodictic.refutation.v1.schema.json`; each block records `id`, `attempted`, `outcome` (`survived | weakened | refuted`), `counter_evidence_quotes` (verbatim, single-line snapshot substrings — min 1), `alternative_explanations` (min 1), `rationale`, `confidence_after`, and the `snapshot_path`/`snapshot_sha256` binding pair (the quotes were verified against *these* bytes). **There is no severity field, by design** — write-scope isolation is what makes the no-severity-write guarantee mechanical (deliberately a separate artifact, never new fields on the locked ledger blocks). A zero-eligible run still writes the record with an `eligible: 0` budget block — absence-vs-skip stays distinguishable.

   **Execution modes** (per `references/execution-modes-reference.md`; the §Step 2 single-vs-swarm and §Evidence Spot-Check precedents):
   - **Single-agent / sequential:** the pass runs inline here, in the same context. The manuscript is already loaded; cost is snippet-scoped re-reads (~2–5K tokens per finding — the finding's `evidence_refs` neighborhoods plus targeted counter-evidence hunts, *never* full-manuscript re-reads per finding) → ~30–75K worst case at the cap.
   - **Hybrid / swarm:** dispatch a dedicated **disconfirmation subagent** that receives the locked Findings Ledger (`mechanism` + `severity` + `evidence_refs`/`evidence_quote` per finding), the manuscript snapshot path, and the contract below — and writes the Refutation Record. This is the stronger form (architectural isolation: the refuter is not the author of the findings — the spot-check's "the writer cannot verify its own claims" principle). Recommended whenever the run is already hybrid/swarm. The subagent's input deliberately **excludes** the letter draft and each finding's confidence token (anti-anchoring, contract item 5).

   **The pass contract (per eligible finding):**
   1. **Adversarial stance, stated as the goal.** The job is to *refute* the finding: argue that this diagnosis is wrong, overstated, or better explained by something else — against the text. Success is a kill or a weakening; a survival must be *earned*, not defaulted. "Kill" means **demote, never delete**: a refuted finding ships at its locked severity with LOW/UNCERTAIN confidence — it is never removed from the letter.
   2. **Quote-first ordering (hunt-then-judge).** Gather candidate counter-evidence spans from the manuscript **before** writing the outcome — the disconfirmation mirror of the stress test's lock-then-test discipline. An outcome written before the quotes exist is malformed.
   3. **Counter-evidence, not the finding's evidence.** Hunt spans that *contradict* the mechanism (the pressure-tested beat the pass missed, the scene where the arc does move, the qualifier the argument does state). Re-quoting the finding's own evidence is not an attempt.
   4. **Alternative explanations are mandatory** (min 1): intentional craft choice, genre convention (`genre-*.md` calibration), POV/register design, evidence elsewhere in the text. A bare "could be intentional" without a quote or a named textual basis does not count — each alternative must point at text (quote mark or `Ch.`/`p.` locator) or at a contract/intent statement; the validator surfaces ungrounded entries as WARN. Deeper grounding — does the alternative actually engage the mechanism, or just gesture? — is judged here, not by a validator.
   5. **Anchoring blinds.** The pass is **not shown** the finding's confidence token, the lens-verdict convergence count, or the letter draft. It judges the mechanism against the text, not against how sure the system already was.
   6. **Strict outcome semantics (anti-performative-humility):** `refuted` requires counter-evidence that the **mechanism does not operate** — the finding's `mechanism` field, the one-sentence causal claim (`findings-ledger-format.md §Fields`) — not that the book has compensating strengths, and not that the author probably meant it. "Author intent" alone never refutes: intent questions route to the Intent Check Loop (Step 1) and author verification; the record may say *survived* with an intent note. `weakened` = the mechanism operates but the counter-evidence materially narrows its scope or force. The `rationale` must name **what evidence would have refuted the finding and whether it was found** — a rubber stamp cannot answer that question honestly.
   7. **Firewall** (`references/firewall.md`): the record contains quotes (manuscript bytes) and diagnosis-of-why — never fixes, never rewritten prose, never invented content. Naming a rival *reading* is diagnosis (allowed); scripting what the author should write instead is invention (forbidden).
   8. **Author-facing language** (`output-policy.md §Author-Facing Language`): outcome tokens never appear raw in the letter body — "this diagnosis held up when we deliberately tried to knock it down" / "a deliberate counter-check found evidence that cuts against this — quoted below."
   9. **Confidence transcription (synthesis agent, not the pass).** After the record is written and **before Step 7**, the synthesis agent transcribes each processed finding's `confidence_after` into that finding's locked ledger block (`apodictic.finding.v1` `confidence`), per the outcome caps table below. This is the flow's only ledger write and it belongs to the transcriber — the pass never touches the ledger. `refutation-write-scope` fails the run on any ledger-vs-record mismatch. Enforcement posture: a **pre-delivery fail-the-run gate, not a write-prevention mechanism** — nothing physically stops a bad transcription from being written; the run just cannot ship with one. Exception: when the intake snapshot is missing off the core-de/full-de path, `weakened`/`refuted` demotions are **void** (unverifiable without quotes) — confidence stays unchanged and the letter carries the disclosure line "counter-evidence quotes unverified — no intake snapshot; demotions withheld".

   **Confidence re-map (what the transcription writes; severity is never remapped — a refuted Must-Fix is still a locked Must-Fix):**

   | Outcome | Confidence consequence |
   |---|---|
   | `survived` | Unchanged (survival is **necessary for HIGH, never sufficient** — the pass may never *raise* confidence; `confidence_after` must equal the ledger's current value) |
   | `weakened` | Capped at MEDIUM |
   | `refuted` | LOW; or UNCERTAIN when the counter-evidence supports a rival interpretation rather than negating the mechanism (conflicting signals, per the existing UNCERTAIN semantics) |

   **How outcomes appear in the letter:** *survived* — no body change beyond the honest HIGH language (the finding now carries earned confidence). *Weakened* — delivered at locked severity, MEDIUM confidence, with the strongest counter-evidence quoted inline near the finding (≤25 words per excerpt, the standing quote budget) so the author sees *why*. *Refuted* — **not silently dropped** (the Deficit Lock forbids that, and rightly): delivered at locked severity with LOW/UNCERTAIN confidence, framed per "never present LOW or UNCERTAIN findings as definitive diagnoses" — the diagnosis, the counter-evidence quote, and an explicit author-verification ask. If the synthesis judges a refuted finding shouldn't ship at its locked tier at all, that is exactly the existing ID-scoped `<!-- override: softness-downgrade F-… -->` + Appendix B path — a legible human-auditable act, never this pass's write. **Appendix B (Severity Calibration)** gains a compact **Refutation Summary** — one line per processed finding: `- F-<ORIGIN>-<NN> — <survived|weakened|refuted> — <one-clause reason> (record: [Project]_Refutation_Record_[runlabel].md)`. Cap-bound HIGHs: marker + Appendix B disclosure per the cap rule above; body language says convergence-only.

   **Mechanical gates (run at Step 10, wired into the `run_spot_check` gate):** `refutation-coverage` (no HIGH without survived refutation), `refutation-evidence` (verbatim snapshot-anchored counter-evidence; fabricated quotes void the attempt), `refutation-write-scope` (no severity channel; exact transcription). See the Step 10 check bullet for invocations. This pass is invisible to `structured-findings`, `deficit-lock`, and `softness-check` — it adds no ledger fields and never touches severity.

7. **Adversarial Reader Stress Test (required).** Before writing the letter, run the stress test per `references/adversarial-stress-test.md`. **Begin the stress test by setting aside the pass findings and the Findings Ledger.** Inhabit the low-charity reader profiles and generate 3-5 adversarial claims from a holistic reading of the manuscript — what would a hostile reader attack regardless of what the passes found? Draw also from the Findings Ledger's "Unresolved Questions" entries, which may contain vulnerabilities the passes noticed but couldn't fully analyze. After generating the independent claims, reconcile them with the pass findings: which attacks are already covered by editorial letter findings? Which are new? New attacks enter the stress test section of the letter. Attacks already covered by the editorial argument are noted as convergent evidence but not duplicated. This is a separate exercise from the adversarial self-check (step 6) — the self-check tests severity calibration of existing findings; the stress test surfaces what hostile readers would attack, which may include issues not flagged by the passes.

8. **Decision-Layer Consolidation (required).** Before writing the letter, convert the diagnosis into explicit revision-control artifacts:

   - **Protected Elements candidate list:** 3-6 load-bearing elements from §3 strength findings that revision could easily damage
   - **Author Decisions:** 3-7 manuscript-specific decisions or commitments, organized as `Keep`, `Cut`, or `Unsure`. These are not generic preferences; they are the live choices that control revision order, book identity, interpretive stance, or risk posture.
   - **Control Questions:** Exactly 7 manuscript-specific questions that should govern revision. These are not "reader questions" and not workshop prompts. They are the high-leverage unresolved questions whose answers determine whether the major fixes actually land.

   Build these from root causes, audit findings, the stress test, and the strongest-case-against logic. If a decision or control question cannot be tied to a root cause, live blind spot, or structural pressure point, it probably does not belong here.

   **Mechanical check.** Decision-layer counts (3-6 / 3-7 / exactly 7) are mechanically validated by `scripts/validate.sh decision-layer-check <editorial_letter_file>` (or the equivalent inline check on hosts without shell execution) at Step 10's pre-output gate. Editorial judgment about *which* elements, decisions, and questions appear is preserved here at Step 8; counts and structural compliance are mechanical at Step 10. Override markers (one per check ID, body-only): `<!-- override: decision-layer-protected-elements -->`, `<!-- override: decision-layer-author-decisions -->`, `<!-- override: decision-layer-control-questions -->`. Markers in appendix bodies are non-canonical (synthesis body is canonical for findings; appendices hold evidence). Use the override path for principled deviations (e.g., short-fiction tier reduces Control Questions to 5; the model must say so in the body and explain in Appendix B).

   **Author Decisions counting (v1.8.0 calibration).** When the Author Decisions section uses Keep / Cut / Unsure (or Defer / Decide) level-3 subheads, the validator counts subhead clusters (typical 1-3) rather than the sub-bullets within them — the contract intent is "3-7 distinct decision categories," and Keep / Cut / Unsure naturally clusters multiple sub-decisions under each category. Letters without subheads are still counted by list-item or paragraph-form rules (verb-leading paragraphs starting with Protect / Keep / Cut / Defer / Decide / Unsure also count when neither list items nor bolded paragraphs are present). This calibration closes Phase 4 Wave 3 eval-coverage findings C1 + C2.

   <!-- REPLACED-WITH-INCLUDE: Argument-DE class schema extracted to `references/synthesis-argument.md`.
        The `decision-layer-check` validator already accepts argument-DE markers; this pointer replaces the
        inline schema paragraph. Load that fragment on argument-shaped runs. -->
   <!-- INCLUDE: `references/synthesis-argument.md` — Argument-DE class decision-layer schema lives there. -->

   **Argument-DE class.** Argument-shaped letters use a parallel decision-layer schema (validator accepts
   "Strengths / Protected Elements" and "Editorial-Dispute Territory" heading variants; skips Checks 3/4).
   See `references/synthesis-argument.md` for the full schema, detection markers, and override path.

   **Evidence-density window (v1.8.0 calibration).** Per-Must-Fix evidence density (≥2 references) is checked over a paragraph-block window — from each Must-Fix line until the next Must-Fix occurrence OR the next section header (`^##` at column 0), whichever comes first. The wider window detects paragraph-form evidence that the prior fixed 6-line window missed. Closes Phase 4 Wave 3 eval-coverage finding C4.

9. **Conditional Underdiagnosis Retry Loop (required gate).** This step uses **enumerated detectable triggers**, not model self-judgment. Run `scripts/validate.sh underdiagnosis-triggers <editorial_letter_file>` (or perform the equivalent inline check on hosts without shell execution). The validator surfaces triggers; the model still owns the decision. For each fired trigger, you MUST either (a) upgrade the affected finding's severity in the synthesis layer, OR (b) document an override marker in the letter body (not in an appendix).

   **Enumerated triggers (detectable from artifacts; no model-judgment language):**

   1. **Convergence trigger:** the same concern (shared mechanism keyword) is flagged in 3+ pass artifacts, audit findings, or ledger entries with no synthesis-layer Must-Fix on it.
   2. **Hard-gate trigger:** any high-risk audit produces an Alert or hard gate (e.g., Reception Risk §7 hard gates, Compression Must-Fix floor) without a synthesis-layer Must-Fix.
   3. **Cross-pass complication trigger:** a final-third concern appears in both a character-pass and a structure-pass artifact.
   4. **Multi-axis severity trigger:** a single concern is rated across 2+ severity classes (series-impact, representation, reader-trust, or equivalent multi-axis hit) with no synthesis-layer Must-Fix.
   5. **Severity-floor trigger:** `validate.sh severity-floor` returns WARN or FAIL on the in-progress letter.
   6. **Propagation trigger:** `validate.sh audit-signal-propagation` returns ERROR or WARN — i.e., audit-internal signals failed to propagate to synthesis.
   7. **Softness trigger:** `validate.sh softness-check <editorial_letter> <findings_ledger>` reports a problem — the delivered letter softens a Triage-locked finding below its locked severity (Deficit Lock, `output-policy.md §Severity Honesty Protocol`) without a body override marker. An unmarked downgrade is an ERROR (exit 1); a hedged-but-delivered finding is a WARN printed to stdout at exit 0 — parse stdout and treat a WARN as a softness trigger too.

   **Override marker syntax** (one per trigger ID, placed in the letter body near the affected finding — NOT in an appendix):

   ```
   <!-- override: underdiagnosis-trigger-convergence — <one-sentence rationale> -->
   <!-- override: underdiagnosis-trigger-hard-gate — <one-sentence rationale> -->
   <!-- override: underdiagnosis-trigger-final-third — <one-sentence rationale> -->
   <!-- override: underdiagnosis-trigger-multi-axis — <one-sentence rationale> -->
   <!-- override: underdiagnosis-trigger-severity-floor — <one-sentence rationale> -->
   <!-- override: underdiagnosis-trigger-propagation — <one-sentence rationale> -->
   <!-- override: underdiagnosis-trigger-softness — <one-sentence rationale> -->
   ```

   Markers in appendix bodies are non-canonical (synthesis body is canonical for findings; appendices hold evidence) and do not satisfy the override path. **Absence of override marker AND absence of severity upgrade = blocked synthesis.**

   **Loop semantics:** Step 9 fires once per synthesis pass. If any trigger remains unaddressed (neither upgraded nor overridden) when validate.sh runs, retry synthesis at higher severity for the affected findings. Once all fired triggers are addressed (upgrade-in-place or override-marker-in-body), Step 9 passes and synthesis proceeds to Step 10.

   Do not proceed to letter generation until the structural deficit analysis correctly reflects the manuscript's severity. Trigger conditions are detectable from named artifacts (Findings Ledger, Audit Invocation Log, audit findings files, in-progress letter); they are not "if the synthesis feels too soft" judgments.

9b. **Synthesis Coverage Manifest (required — before any letter prose).** Produce the artifact-read manifest `[Project]_Synthesis_Read_Manifest_[runlabel].md` in the run folder — the mechanical record of what this synthesis step can actually see, written **before the letter exists** so the letter's coverage note (Appendix C, below) can only ever be a projection of it, never a self-report. The design rule that keeps the disclosure honest: the note is computed from the manifest, and the manifest's denominator is enumerated from disk — never from the letter's own prose, never from a model's memory of what it read.

   - **Who writes it.** Sequential / hybrid / swarm: the **parent orchestrator** writes it at synthesis dispatch (`run-core.md` §Execution Protocol step 10) — one row per dispatch input; provenance is **`dispatch-derived`** (the orchestrator lists exactly the files it handed the synthesis subagent — the strongest coverage evidence available without platform introspection). Single-agent: the agent writes it **now**, immediately before letter-writing — one row per artifact with the status it declares; provenance is **`declared`** (there is no read-event log; nothing platform-side records what stayed salient, and the note says so in pinned language rather than laundering the gap).
   - **Row grammar (closed).** The manifest body is a single pipe table, four cells per row — `| kind | id | status | annotations |` — and `synthesis_coverage.py` is its only parser. `kind ∈ {artifact, span}`. Artifact rows: `id` = the artifact file's basename; `status ∈ {verbatim, summary, absent}` (`verbatim` = full file provided/re-read at synthesis time; `summary` = represented only via its ledger entry / the reverse outline; `absent` = on disk but not represented in any synthesis input). Span rows: `id` = a chapter/scene span label from the preflight section boundaries + reverse-outline scene list (`Ch 12 (sc. 30-31)`, `Ch 1-2`; single-agent runs may use the single universal label `full manuscript`); `status ∈ {in-context, outside-active-context}` (`in-context` = single-agent nominal / a verification excerpt in multi-agent). The `annotations` cell is empty or exactly `regrounded: true` — an encoding reserved for the pre-letter re-grounding step (`docs/synthesis-regrounding.md` M2), which flips re-read rows and appends it; **nothing writes it today** — the field is encoded now so the manifest format never changes. Any other annotation content is a validation FAIL, never silently ignored.
   - **The denominator is enumerated from disk, never model-supplied.** Artifact rows must cover exactly the run folder's pass artifacts (`[Project]_Pass[N]_[Name]_[runlabel].md`), the Findings Ledger, the Contract, and the audit files (Audit Invocation Log + audit findings files): every enumerated file gets exactly one row, and no row may name a file outside that set — the manifest can neither shrink nor pad the denominator. At least one span row is required (the manuscript dimension cannot be omitted).
   - **Degrade truth table (what `degraded` means, mechanically).** Coverage is `degraded` iff any applicable condition fires; otherwise `ok`: **D1** any artifact row `absent` (all modes); **D2** a synthesis-bound (Must-Fix/Should-Fix) ledger finding whose evidence is covered by no `verbatim` origin-pass row and no chapter-matching `in-context` span (all modes); **D3** estimated context utilization > 60% of the detected window (single-agent only — preflight's viability threshold family); **D4** zero `in-context` verification-excerpt spans while the letter carries ≥ 1 Must-Fix (multi-agent only). Degrade is **relative to the mode's own baseline**: normal multi-agent outline-mediated coverage (all spans `outside-active-context` with ledger/outline at `summary` and excerpts present) is **not** degraded — that is the architecture working as designed, and the note says so rather than crying wolf.
   - **What follows from the manifest** (all validated by `scripts/validate.sh synthesis-coverage <run_folder>` at Step 12, and wired into the Step 10 `run_spot_check` gate): the `<!-- coverage: ok|degraded -->` title-block marker (§1 Title Block), the conditional Short Version sentence (§2), the Appendix C `### Synthesis Coverage` note (§11), and the sidecar `synthesis_coverage` object (`output-structure.md` §Machine-Readable Sidecar). Fill the sidecar object now, while the manifest is fresh. There are **no override markers** for any of these checks — disclosure is not overridable; the only legitimate escape is fixing the manifest.

9c. **Pre-Letter Re-Grounding (required — after the step-9b manifest, before any letter prose).** Before writing the letter, re-read the locked findings from disk and restore into the draft claims the exact **counts, names, and quote anchors** that context-salience decay smears into vague prose (`docs/subagent-architecture-design.md:15`: Pass 1's "nine belief failures" must not become "several belief failures" in the letter). This step runs after the Synthesis Coverage Manifest exists (step 9b) — it re-reads the consolidated ledger *and* updates that manifest — and before the Step 10 pre-output gate and Step 11 letter-writing. It is named **Pre-Letter Re-Grounding** to avoid collision with the built `run-core.md §Pre-Pass Re-Grounding` (a different seam — pre-*pass*, not pre-*letter*); **this step does not touch that section.**

   1. **Re-read the consolidated Findings Ledger verbatim from disk** (all modes — even single-agent, where the disk copy is the canonical record and the re-read is cheap). This restores the ledger's locked counts / names / evidence anchors as the ground truth the letter must project, not a decayed memory of them.
   2. **For each synthesis-bound (Must-Fix/Should-Fix) locked finding, re-read the manuscript text its `evidence_refs` anchor.** Single-agent: direct targeted re-reads (the manuscript is a file). Multi-agent: from the verification excerpts where covered, else **bounded synthesis pulls** — ≤ 2 spans per finding, ≤ 5k tokens per span, keyed on the `finding_id` + that finding's locked `evidence_refs` anchors (the evidence-pull constraints, `subagent-architecture-design.md:107–111`, applied at the synthesis seam). This is the ROADMAP §Model-Capacity "long-context re-grounding before synthesis" item, sized ~10–30k tokens per run.

      **Increment-1 scope-down (pinned).** The orchestrator-governed pull *API* is unbuilt — Runner-Governed Execution Increment 4 (external host orchestrator) remains future (`ROADMAP.md` §Runner-Governed Execution). So this ships **prompt-level**: the pulls are step-text instructions executed by the orchestrating model, backstopped by the mechanical floors below (the specificity-floor gate + M1's V1–V5 verify the *results* on disk — restored counts, updated manifest rows — not the pull transcript).

      <!-- deferred: orchestrator-pull-interface (Runner-Governed Execution Increment 4) -->

   3. **Restore specificity into the draft claims** — exact counts, names, quote anchors, from the re-read ledger + text. **Re-grounding may only ADD specificity.** It may **not** add a finding (anything genuinely new noticed here goes to §4b Additional Observations, without a finding ID and without a Must-Fix/Should-Fix label, flagged "surfaced post-ledger; awaits pass-level confirmation" — the Step 10 findings-integration demotion path), **not** change any severity (Deficit Lock is untouched; severity writes from this step are forbidden — Deficit Lock + softness-check downstream remain the enforcement), and **not** remove counterevidence or soften wording (softness-check still applies at Step 10). The smuggled-finding gate is **`scripts/validate.sh finding-trace <run_folder>`** (its E1 check: a letter citation to an F-… ID not in the ledger fails, exit 1) — the sole owner of the letter-ID-must-exist-in-ledger direction; this step names it, and does not re-implement it. When you write the letter (Step 11), place a `<!-- regrounding: done -->` marker on its own line **directly after the coverage marker** (which sits immediately after the title block — §1 / the step-9b V5 placement).
   4. **Update the M1 manifest (never suppress the coverage note).** Artifacts / spans re-read here flip their manifest row `status` to `verbatim` / `in-context` **and** append `regrounded: true` in the annotations cell (e.g. `| artifact | MyBook_Pass5_Character_Audit_r3.md | verbatim | regrounded: true |`). The `regrounded: true` annotation is the encoding M1 already parse-accepts (step 9b row grammar). The coverage note then reflects post-re-grounding reality — disclosure improves because contact with the text actually happened, never because the note was edited. **M1's disclosure stays mandatory:** re-grounding never lets a `degraded` coverage state read `ok`; `synthesis-coverage` runs unchanged on the updated manifest and its V5 masking check still fires (the note is computed from the manifest, not from the letter). M1 is a hard dependency of this step and is never replaced by it.

   **Mechanical gate (run at Step 10, wired into the `run_spot_check` gate):** `scripts/validate.sh specificity-floor <editorial_letter> <findings_ledger>` — the **count floor** (a finding whose ledger entry locks a count may not deliver a vague quantifier with none of that count in its letter window; case-insensitive number-word matching, so a sentence-initial "Nine" satisfies a ledger "nine") and the **anchor floor** (each delivered Must-Fix window carries an evidence reference matching the finding's locked `evidence_refs`, so a restored number rides a ledger-matching anchor). Legitimately non-countable findings use an ID-scoped `<!-- override: specificity-floor F-… — <rationale> -->` marker (body) + an Appendix B entry. Name restoration, quote selection, and the add-only discipline itself are prompt-level, backstopped by that gate and by the Evidence Spot-Check (§Evidence Spot-Check, which now samples post-re-grounding claims).

10. **Pre-Output Synthesis Verification (required gate).** Before delivering the letter, **run `scripts/validate.sh gate run_spot_check <run_folder>`, resolve any `GATE-WARN`, confirm each `ATTEST` item, then run `scripts/validate.sh gate --attest run_spot_check <run_folder>` to clear; do not deliver until that clears (exit 0).** The first call runs the mechanical letter checks below (sections, severity-floor, decision-layer, audit-signal-propagation, underdiagnosis, softness-check, tone, synthesis-coverage, specificity-floor, refutation-coverage/-evidence/-write-scope) from `schemas/execution-gates.v1.json` and records `mechanical-passed` (or `pass-with-warn` / `blocked`); the `ATTEST` items it prints (findings integration, cap compliance, blind-spot disclosure) remain your confirmation, and `--attest` re-runs the checks and records the **clearing** `passed` event only if still clean. On hosts without shell execution, perform the checks inline and append one combined clearing event to `execution.gate_events[]` (`gate: "run_spot_check"`, `attested_items`/`attested_contract` = `spot-a1..spot-a3`), as in the Pre-Synthesis Gate degradation note. The per-check detail below is the expansion of that gate. Verify the synthesis is actually drawing from pass findings — not generating an editorial letter from general impressions of the manuscript. Run these checks:

   - **Findings integration check:** For each root cause identified in step 3, confirm it cites at least one specific ledger finding by pass and finding name. If a root cause exists only as a general impression without ledger grounding, either locate the supporting ledger entry or demote it to §4b (Additional Observations) with a note that it awaits pass-level confirmation.
   - **Section ordering check:** Confirm the letter will follow the required §1-§11 order. Protected Elements, Author Decisions, Control Questions, Strongest Case Against, and Stress Test are separate sections with distinct jobs — they must not be merged or omitted.
   - **Cap compliance check:** Root causes ≤ 5. Revision checklist items ≤ 10 (Core DE) or ≤ 15 (Full DE). Must-Fix flags ≤ 10.
   - **Severity floor check:** Severity-floor rules are canonical in `references/output-policy.md §Severity Floor Rules`. Run `scripts/validate.sh severity-floor <editorial_letter_file>` (or perform the equivalent inline check on hosts without shell execution) before delivering the letter. Failures block delivery until the model either re-tiers the offending finding or documents an override rationale in Appendix B (Severity Calibration). Do not restate the rules here — point to the canonical home.
   - **Decision-layer + appendix + evidence-density check:** Run `scripts/validate.sh decision-layer-check <editorial_letter_file>` (or perform the equivalent inline check on hosts without shell execution). The validator mechanically verifies Protected Elements count (3-6), Author Decisions count (3-7), Control Questions count (exactly 7), Appendices A/B/C presence, and per-Must-Fix evidence density (≥2 references). Editorial judgment about *which* elements/decisions/questions/appendix content appear is preserved at Step 8 and the editorial layer; counts and structural compliance are the validator's job. Do not restate the count contract here — point to the canonical homes (`references/output-policy.md §Mandatory Appendices` and `references/output-policy.md §Evidence Density Self-Check`). This validator runs alongside `severity-floor` and `audit-signal-propagation` as part of pre-output verification.
   - **Deficit Lock / softness check:** Run `scripts/validate.sh deficit-lock <findings_ledger_file>` (verifies every synthesis-bound finding was locked structurally) and `scripts/validate.sh softness-check <editorial_letter_file> <findings_ledger_file>` (compares the delivered letter against the Triage-time locks — Deficit Lock, canonical in `references/output-policy.md §Severity Honesty Protocol`), or the equivalent inline check on hosts without shell execution. An unmarked downgrade of a locked Must-Fix/Should-Fix blocks delivery (ERROR, exit 1); hedged delivery of a locked finding is surfaced as WARN (exit 0) — treat it as a softness trigger and re-examine the wording. Resolve by re-tiering, delivering at the locked severity, or recording an ID-scoped `<!-- override: softness-downgrade F-… — <rationale> -->` marker (naming that finding's Lifecycle ID) in the body plus an Appendix B entry. Weak-axis-vs-Must-Fix coherence is owned separately by `severity-floor` and is not duplicated here.
   - **Finding disconfirmation check:** Run `scripts/validate.sh refutation-coverage <editorial_letter> <findings_ledger> <refutation_record>` (no HIGH without a survived refutation attempt; every Must-Fix processed; cap-bound disclosure markers honored only under a `bound: true` budget), `scripts/validate.sh refutation-evidence <refutation_record> <manuscript_snapshot> --require-snapshot` (every counter-evidence quote verbatim and single-line in the intake snapshot; `snapshot_sha256` binding; budget arithmetic — pass `--require-snapshot` whenever this run wrote a `*_Core_DE_Synthesis_*`/`*_Full_DE_Synthesis_*` letter, where a missing snapshot is a broken intake; elsewhere a missing snapshot is a WARN and every demotion in the record is **void** — `weakened`/`refuted` may not be transcribed without verified quotes), and `scripts/validate.sh refutation-write-scope <findings_ledger> <refutation_record>` (no severity channel in the record; ledger confidence equals `confidence_after` per the Step 6b outcome caps) — or the equivalent inline checks on hosts without shell execution. Like deficit-lock/softness-check, these are pre-delivery fail-the-run gates, not write prevention. Resolve by re-running the Step 6b pass, fixing the transcription, or adding the disclosure the validator names — never by editing outcomes to fit.
   - **Pre-letter re-grounding fidelity check:** Run `scripts/validate.sh specificity-floor <editorial_letter> <findings_ledger>` (or perform the equivalent inline check on hosts without shell execution). It holds the delivered letter to the specificity the ledger locked: the **count floor** (a locked count may not decay to a vague quantifier — "nine belief failures" → "several belief failures" fails unless the count is restored, case-insensitively) and the **anchor floor** (each delivered Must-Fix window carries an evidence reference matching the finding's locked `evidence_refs`). Resolve by restoring the exact count / anchor from the re-read ledger (step 9c), or — for a legitimately non-countable finding — by recording an ID-scoped `<!-- override: specificity-floor F-… — <rationale> -->` marker in the body plus an Appendix B entry. The letter-ID-must-exist-in-ledger (smuggled-finding) direction is **not** this check's — it is `finding-trace`'s E1; run `scripts/validate.sh finding-trace <run_folder>` for that. Like deficit-lock/softness-check, these are pre-delivery fail-the-run gates.
   - **Blind-spot disclosure check:** Any deferred or declined high-risk audit appears in Appendix A and is named in the letter where it materially limits confidence or readiness.

   If any check fails, fix it before proceeding. This gate exists because the most common synthesis failure mode is generating an editorially plausible letter that doesn't actually integrate the analytical work — the letter sounds right but isn't grounded in what the passes found.

11. **Write the editorial letter** using the presentation format below. The self-check informs the letter's severities; the stress test becomes §10 of the letter.

**Key principle:** Processing order ≠ presentation order. The self-check must happen before writing, but in the output document it belongs in an appendix. The author reads findings; the framework owner reads methodology.

12. **Post-Write Section Validation (required).** After saving the editorial letter to disk, verify that all 14 required sections appear as markdown headings in the correct order. The required headings (in order):

    1. Title block (level-1 heading with project name)
    2. "The Short Version"
    3. "What the Book Does Best"
    4. "What Needs Work" (with subsection headings per root cause)
    5. "Additional Observations" (§4b)
    6. "Revision Checklist"
    7. "Protected Elements"
    8. "Author Decisions"
    9. "Control Questions"
    10. "The Strongest Case Against"
    11. "Stress Test" (or "Adversarial Reader Stress Test")
    12. "Appendix A" (Diagnostic Detail)
    13. "Appendix B" (Severity Calibration)
    14. "Appendix C" (Framework Notes)

    Check that each appears as a heading (`#`, `##`, or `###`), not just as a phrase in prose. If using `scripts/validate.sh synthesis-sections`, note that the script performs substring matching — the inline check is more precise and should be preferred when the script's loose matching could give false confidence. If any section is missing or out of order, fix before delivering.

    **Coverage reconciliation (required).** After section validation, run `scripts/validate.sh synthesis-coverage <run_folder>` (or perform the equivalent inline check on hosts without shell execution). It verifies the step 9b surfaces against each other and against the filesystem: the manifest exists and covers the on-disk denominator (V1/V2), the Appendix C note and sidecar object are exact projections of the manifest (V3), provenance matches the execution mode (V4), and the `<!-- coverage: ok|degraded -->` marker matches the mechanically recomputed degrade state (V5). Launch posture (operator call, spec `docs/synthesis-regrounding.md`): the V2/V3/V4 fiction-checks are blocking day one; V1/V5 are advisory for one release (`--strict` promotes). The check also runs inside the Step 10 `run_spot_check` gate.

13. **Tone Compliance Check (required).** After section validation, run `scripts/validate.sh tone-check <letter_file>` on the saved editorial letter. The script blocks sycophantic superlatives (masterpiece, stunning, flawless, clean bill, tour de force, triumph, perfection) that indicate praise has displaced rigorous diagnosis. If the check fails, rewrite the offending passages with severity-calibrated language and re-run until it passes. This gate exists because the framework's job is accurate diagnosis; a letter that earns its praise through superlatives rather than evidence undermines every other structural check in this file.

### Presentation Format (Editorial Letter)

The synthesis is structured as a letter with scannable reference material. Prose carries the argument; headings, bold thesis statements, and a revision table provide scannability. Framework shorthand (severity labels, pass numbers, protocol stamps) stays out of the main text — it belongs in the appendices only.

**Operator mode — Editor Scaffolding (`operator:editor`).** If the router set `operator:editor` ("I'm editing someone else's work"), build the letter in **Editor Scaffolding** mode per `references/editor-scaffolding.md`: a superset overlay that re-aims the same diagnosis at a human developmental editor. Add the `<!-- mode: editor-scaffolding -->` marker near the title block; replace "The Short Version" with an **Editor Brief** (addressee = the editor; name where their read and yours most likely diverge); add a **What You Might Have Missed** blind-spot section; reframe the Revision Checklist as an **Intervention Menu (editor's discretion)**. Keep every mandatory section below (Protected Elements, Author Decisions, Control Questions, Appendices A/B/C) and all severity honesty intact — scaffolding changes the addressee, never the severity. At Step 10, run `scripts/validate.sh editor-scaffolding <editorial_letter>` alongside `decision-layer-check` / `severity-floor` / `softness-check`. Absent the flag, build the standard author-facing letter below. **Dual output.** If the editor wants *both* artifacts — the scaffolded letter to work from and the author-facing letter to hand the author — emit both from the one diagnosis (the scaffolded letter here, plus the ordinary author-facing letter with no editor marker and no editor-only sections) and validate the pair with `scripts/validate.sh editor-scaffolding --dual <editor_letter> <author_letter>` (D1 editor side E1–E4, D2 author register, D3 matching top severity band). See `references/editor-scaffolding.md` §Dual-output.

**Operator mode — Diagnostic Vocabulary (`operator:facilitator`).** If the router set `operator:facilitator` ("I'm facilitating a writing group"), additionally produce a **Vocabulary Guide** (`[Project]_Vocabulary_Guide_[runlabel].md`) per `references/diagnostic-vocabulary.md`: a teaching aid for the group with a `<!-- mode: diagnostic-vocabulary -->` marker, a **Glossary** of the structural concepts the diagnosis used (each `**Term** — definition` grounded in a specific manuscript spot with a reference), and a **Discussion Prompts** section of open questions. The author-facing editorial letter is still produced **with its severity record intact** — the Guide is a teaching companion, not a softer letter, so it carries no severity and frames issues as questions, never author-directed prescriptions. Validate with `scripts/validate.sh diagnostic-vocabulary <vocab_guide>`.

**Constraint mode — Legal Risk Register (`constraint:risk`).** If the contract carries `constraint:risk` ("sensitive or legally risky content"), **offer** the author a Legal Risk Register; on the author's accept, run its protocol (`references/legal-risk-register.md` §Protocol) and write `[Project]_Legal_Risk_Register_[runlabel].md` — an additive companion artifact (the editorial letter is unchanged). It flags legal-exposure areas (defamation / privacy / rights-clearance) with an escalation tier and routes serious items to counsel; the firewall is **flag, don't practice law** — never adjudicate ("not defamatory", "fair use"). Unlike the operator overlays above, this one is **offered, not auto-produced** — the not-a-lawyer framing warrants an explicit confirm. Validate with `scripts/validate.sh legal-risk <run_folder>`. Direct entry point: `/legal-risk`.

**Content-detection auto-recommend — Legal Risk Register (no explicit `constraint:risk` flag).** Parallel to the `constraint:risk` path above, the synthesis layer **auto-recommends** (offers) the Legal Risk Register when the manuscript's *content* exhibits the memoir / real-people signals **even though `constraint:risk` was not set** — the author never flagged the exposure, so the model reads for it. This is **model-side detection in the synthesis prose**, not a mechanical validator arm: around the Audit Integration Point, before synthesis — as an additive scan, *not* a member of the high-risk blind-spot gate's own closed risk-class list — scan the manuscript and contract for the content signals below — grounded in `references/legal-risk-register.md` §Detection guidance / §Auto-recommend — and, when they fire, **offer** the register. The trigger is also declared where routing lives: `intake-router-runtime.md` §3 (Q3 option D) / §6 Table B and `pass-dependencies.md` §4a (Router-triggered audits), consistent with the Field Reconnaissance / Reception Risk "auto-recommend before synthesis" precedent.

**Trigger — the manuscript is memoir / autofiction / nonfiction portraying identifiable real people.** Detect via a **mode signal** *plus* at least one **real-people content signal**:

- **Mode signals:** first-person retrospective narration presented as the author's own lived experience (memoir); an autofictional author-surrogate, or an author's-note / framing that maps characters onto real people (autofiction); nonfiction that names or depicts identifiable living people — biography, reportage, personal essay, or the `constraint:nonfiction` memoir / witness-led route (`nonfiction-intake-routing.md`).
- **Real-people content signals** (any one — drawn from §Detection guidance): a reputational **statement of fact** about a named or role-identifiable **living** person (crime, fraud, sexual / professional misconduct, addiction, financial wrongdoing — the `defamation` pattern); **intimate private facts** about an identifiable living **private** person (medical / psychiatric, sexual, abuse, family secrets — the `privacy` pattern); **changed-name fiction that stays recognizable** (the autofiction defamation pattern); quoted **song lyrics / poetry / epigraphs / unpublished letters or diaries**, or other substantial third-party copyrighted material (the `rights-clearance` pattern); an admitted **NDA / settlement / confidentiality** covering disclosed material.

**It is an OFFER, not an auto-produce** — identical discipline to the explicit-flag path: the not-a-lawyer framing warrants an explicit confirm, so on detection the synthesis layer *offers* the Legal Risk Register and runs its protocol (`references/legal-risk-register.md` §Protocol) only on the author's accept; the editorial letter is unchanged either way. On decline, note that the offer was made and declined (no blind-spot escalation is owed — the register is advisory, not a synthesis dependency). **The firewall is intact end to end:** detection flags a content signal that *may* warrant legal review; it never adjudicates ("not defamatory", "fair use", "no liability") and never produces the register without confirm. **False-positive guard:** purely invented fiction with no identifiable real-person mapping does not trigger, and the §Detection guidance lower-exposure carve-outs (the dead, public figures acting in their public role, facts already lawfully in the public record, a real person merely written *about* in expressive content) are not signals. When the signals are genuinely ambiguous, a light offer ("this reads like memoir portraying real people — want a Legal Risk Register pass?") costs the author one decision and keeps the not-a-lawyer boundary explicit.

**Required sections, in order:**

**1. Title Block**
```
# Development Edit: [Title]
### [Author] | [Word count] words | [Draft stage]
*APODICTIC Development Editor v[X] — [Date]*
```

**Coverage marker (required).** The first non-blank line immediately after the title block, on its own line — nothing else on the line — is the machine marker `<!-- coverage: ok -->` or `<!-- coverage: degraded -->`. One declaration, one place: a second coverage marker anywhere in the letter is a validation FAIL. The value is not self-assessed — it must equal the sidecar's `synthesis_coverage.coverage`, and `degraded` is recomputed mechanically from the Synthesis Coverage Manifest per the step 9b truth table (`validate.sh synthesis-coverage`).

**2. The Short Version.** One paragraph. Names both the primary asset and the primary liability. States the verdict class (reconception vs. targeted revision vs. polish). Names the revision's core ask. The author should be able to read this paragraph alone and know where they stand.

When the coverage marker is `degraded`, end the paragraph with this pinned sentence (body is canonical; appendices hold the evidence): *"Coverage note: synthesis-time contact with the manuscript was degraded; see the Synthesis Coverage note in Appendix C."*

**3. What the Book Does Best.** Prose. Specific scenes and line references embedded naturally. Explain *why* each strength matters — not just that it exists, but what it does for the reader. If one scene exemplifies the book's highest capacity, name it and explain why. This section establishes what the revision must protect.

Discipline: Maximum 3 major strengths for manuscripts needing significant revision. Maximum max(leaks, 3) for manuscripts needing only polish. Every strength must cite specific evidence.

**4. What Needs Work.** Headed subsections. Each heading is a **bolded thesis statement** that names the problem in plain language (e.g., "**Pacing: Part I has room Part III needs.**" — not "Priority Leak #1: Dramatic Density Imbalance"). Prose argument underneath with line references embedded naturally. The argument should make the reader understand *why* the issue matters for their book specifically, not just that a structural rule has been violated.

Group related issues under a single heading when they share a root cause (e.g., four underdeveloped secondary characters become one section about the pattern, not four separate flags).

**4b. Additional Observations from the Diagnostic Passes.** This section draws from the Findings Ledger — specifically from notable findings and cross-pass connections that didn't make it into §3 or §4 but that the author should know about. Brief prose paragraphs with cross-references to the pass artifacts.

**Inclusion criteria:**
- Any ledger finding rated "notable" that isn't already discussed in §3 or §4
- Any cross-pass connection that reveals a pattern not covered by the root causes
- Any data artifact that would be useful for revision even though it doesn't correspond to a "problem" (e.g., a competence-cost inventory that confirms the author's consistency, a suspense architecture table that shows strong question density)
- Structural characteristics of the manuscript worth noting even when they aren't flaws (e.g., "the novel runs on almost zero dramatic irony — this is a structural characteristic, not necessarily a problem, but it has these specific implications for revision")

**Exclusion criteria:**
- Findings already covered in §3 or §4 (no duplication)
- Raw data without interpretive value
- Audit triggers (these stay in Appendix A)

This section serves two purposes: it prevents the synthesis from compressing away pass findings that the author needs, and it teaches the author how to use the pass artifacts as revision tools. Every item should include a cross-reference pointing the author to the relevant pass artifact.

**5. Revision Checklist.** A table the author can tape to the wall. Priority ordered. Columns:

| # | What | Why it matters | Effort |
|---|------|---------------|--------|

"Effort" replaces severity labels — Low / Medium / High communicates what the author needs to know (how much work) without framework jargon. Map roughly: continuity fixes → Low; single-scene additions → Low–Medium; multi-scene redistribution → Medium; structural reconception → High.

Maximum 10 items in the table. If more than 10 issues exist, the prose sections carry the rest; the table holds only the actionable priorities.

**Traceability rule:** Every item in the revision checklist must correspond to a finding already discussed with rationale in the prose sections above (§3 or §4). The checklist is a summary tool, not a place to introduce new findings. If an issue isn't important enough to discuss in the letter body, it isn't important enough for the checklist.

**6. Protected Elements — What Not to Touch.** Name 3–6 specific elements the revision must not damage, with reasons. These are the manuscript's load-bearing strengths — scenes, techniques, voice qualities, structural choices, or relationships that are working and that revision could accidentally break.

Each element should be:
- **Named specifically** (a scene, a character dynamic, a structural choice, a voice quality — not "the good parts")
- **Grounded in pass evidence** (drawn from §3 findings and pass artifacts)
- **Given a reason** (why this element matters, and what would be lost if revision eroded it)

Format: Brief prose list (not a table). Each element gets 1–3 sentences: what it is, why it works, and what revision pressure it's most vulnerable to.

**Why this section exists:** Revision fixes problems but can also destroy what works. §3 identifies strengths; §5 identifies what to change; §6 explicitly marks the no-go zones. Authors revising under pressure tend to over-correct — this section gives them specific guardrails.

**Relationship to §3:** §3 argues *why* the strengths matter. §6 translates that into *operational protection* — it tells the author which strengths are at risk from the specific revisions recommended in §4 and §5. An element in §3 that isn't threatened by the revision plan doesn't need to appear here. An element that isn't in §3 shouldn't appear here either — if it's worth protecting, it should have been identified as a strength first.

**7. Author Decisions.** A compact decision layer that translates diagnosis into concrete authorial commitments.

Organize under these subheads as needed:
- **Keep** — elements or interpretive stances the revision should preserve on purpose
- **Cut** — moves, explanations, scene functions, or repeated beats the revision should remove or stop relying on
- **Unsure** — unresolved decisions the author must make before revision can proceed cleanly

Each item should be 1-2 sentences and materially affect revision order, book identity, stance, or risk calibration. If the author has not made the decision yet, phrase it as the decision they now need to make.

**8. Control Questions.** Exactly 7 manuscript-specific questions that should sit beside the draft during revision. These are not curiosity questions for the reader. They are control questions for the author and editor: if the answer changes, the revision plan changes.

Each question should:
- be anchored in a root cause, high-risk ambiguity, or unresolved decision
- be specific enough to answer through revision choices
- avoid generic workshop phrasing

Add a brief note after each question: why the answer matters for the book's revision path.

**9. The Strongest Case Against.** The rejection memo, reframed for the author. Write it as: "If I were arguing for passing on this manuscript..." State the case in 1-2 paragraphs. Reference findings from the letter — no new uncited claims.

**Do not render a verdict on whether the case wins or loses.** The author assesses that. The framework's job is to make the strongest honest case for rejection and let it stand on its own evidence. If the case is weak, its weakness will be self-evident; if the case is strong, dismissing it is a disservice. End with the case, not with reassurance.

**10. Adversarial Reader Stress Test.** Required for every editorial letter. Format and methodology per `references/adversarial-stress-test.md`. This section presents 3-5 adversarial claims from low-charity reader perspectives, each with evidence, severity, steelman defense, and net risk assessment. The stress test complements §9 — where §9 states the structural case against the manuscript in 1-2 paragraphs, §10 inhabits specific hostile reader types and surfaces what each would attack.

**11. Appendices.**
- **Appendix A: Diagnostic Detail.** Pointers to companion pass files and supplementary audit findings with brief descriptions of what each contains. For each supplementary audit that ran, list its companion findings file and any tracking artifacts produced (e.g., Decision Event Map, Stakes Ladder Map, Scene Turn code inventory). Group pass files first, then audit findings. If any high-risk audit was deferred or declined, name the blind spot here and state how it limits confidence or readiness claims. **For argument-shaped runs without Field Reconnaissance coverage (Phase 6 Wave 3 / CR-4):** name "literature-counterevidence not surveyed" as a blind spot and state the implication (the argument engine operated against a manuscript-internal claim graph; competing studies / counter-citations / replication failures / opposing scholarly positions in the literature were not surfaced; synthesis confidence on counterevidence completeness is bounded). For high-stakes argument-shaped runs without Pre-DE Citation Verifier coverage, additionally name "citation provenance not verified" with the same disclosure pattern.
- **Appendix B: Severity Calibration.** Compressed summary of the adversarial self-check — which findings were tested, in which direction, whether any severities were adjusted.
- **Appendix C: Framework Notes.** Analysis version, model, run date, passes completed, protocol flags, prior analyses on file, cross-version stability notes (if applicable).

  **Required subsection — `### Synthesis Coverage`.** A mandatory subsection of Appendix C (inside the existing 14th required heading — no 15th top-level section; the `synthesis-sections` contract is untouched, and the subsection's checks live in `validate.sh synthesis-coverage`, not there). The note is a **projection** of the step 9b manifest — it may never claim broader coverage than the manifest records. Content, in order:

  1. **Mode + provenance sentence**, pinned verbatim: *"This letter was synthesized in [mode] mode."* followed by — multi-agent: *"The coverage below is dispatch-derived: it lists exactly the artifacts and excerpts the synthesis step received."* — or single-agent: *"The coverage below is declared by the model, not platform-verified: with a single long context, what remained in active attention at letter time cannot be mechanically observed."* (Write `[mode]` as the plain mode word — `hybrid`, `single-agent` — no backticks; the validator matches the sentence verbatim.)
  2. **The manifest table, reproduced row-for-row** — the same four-cell grammar as the manifest file; the validator diffs the two as sets, so statuses, span lists, and annotations must agree exactly.
  3. **Manuscript span coverage in prose:** single-agent — *"full manuscript nominally in context (estimated context utilization NN% per preflight)"* (NN = preflight's estimated token load ÷ detected window, both already computed); multi-agent — the explicit lists, e.g. *"In active context at letter time: Ch 3 (sc. 7-8), Ch 12 (sc. 30-31) — the verification excerpts. Outside active context: Ch 1-2, 4-11 (represented via the reverse outline and Findings Ledger only)."*
  4. **Interpretation line** (per mode, in the spirit of the hybrid focus map's coverage-interpretation note): what this coverage means for trust in this letter, ending with the remedy — *"If you want broader synthesis-time contact with the text, request more verification excerpts or swarm mode."*

---

## Core DE Deliverables

**Reminder:** All outputs must follow the Author-Facing Language requirement (see `references/output-policy.md`). Translate all framework shorthand on first use.

### Editorial Letter (Core Synthesis)

The primary deliverable. Format specified in §Core DE Synthesis above.

### Run Folder, Rolling State & Machine-Readable Sidecar

Where run artifacts and rolling state are written (run folder vs. project root), the post-synthesis update steps for `Diagnostic_State.md` / `SYNTHESIS.md` / `README.md`, and the `Diagnostic_State.meta.json` sidecar update schedule live in `references/output-structure.md` (loaded at write/persist time). The sidecar `contract_hash` is set at intake and checked at pre-pass re-grounding (see `run-core.md` §Mechanical Validation).

### Evidence Spot-Check (Required — Post-Synthesis)

After the editorial letter is written, saved, and mechanically validated, run an independent evidence spot-check. This is the "verify from the outside" layer — it tests whether the editorial letter's claims actually match the manuscript, not just whether the analysis is internally consistent.

**What it is:** A lightweight verification pass that samples specific claims from the editorial letter and checks them against the primary source (the manuscript). This is analogous to end-to-end testing in software: the editorial letter is the "application output"; the manuscript is the "running application."

**Why it exists:** The most insidious synthesis failure mode is an editorially plausible letter that sounds right but doesn't accurately represent what's in the text. The Pre-Output Synthesis Verification (step 8) checks structural completeness; the spot-check tests factual accuracy. These are different failure modes.

**How it runs:**

1. **Select 5 claims to verify.** Choose the highest-stakes claims — prioritize:
   - The 2 highest-severity Must-Fix flags (if any)
   - 1 claim from "What the Book Does Best" (confirming a cited strength)
   - 1 claim from "The Strongest Case Against"
   - 1 claim from the stress test
   If fewer than 5 claims meet these criteria, fill from the revision checklist.

2. **For each claim, verify three things:**
   - **Evidence exists:** The cited scene/page/line reference actually exists in the manuscript at approximately the stated location.
   - **Diagnosis matches text:** The editorial letter's characterization of what happens in the cited passage is accurate — not hallucinated, conflated with a different scene, or significantly misrepresented.
   - **Fix class matches root cause:** The recommended intervention class is logically connected to the diagnosed mechanism. (E.g., if the diagnosis is "motivation gap," the fix class should address motivation, not pacing.)

3. **Report findings.** Append a brief verification block to the end of the editorial letter (before appendices), or as a note in Appendix C:

   ```markdown
   ### Evidence Spot-Check
   Verified 5 claims against manuscript. Results:
   - [Claim 1]: CONFIRMED — [scene ref] matches diagnosis.
   - [Claim 2]: CONFIRMED — [scene ref] matches diagnosis.
   - [Claim 3]: ADJUSTED — [scene ref] exists but characterization overstates X. [Correction applied to §4.]
   - [Claim 4]: CONFIRMED — [scene ref] matches diagnosis.
   - [Claim 5]: CONFIRMED — [scene ref] matches diagnosis.
   ```

4. **On failure:** If a claim fails verification:
   - **Evidence doesn't exist:** Correct the scene reference in the editorial letter. If no supporting evidence can be found, downgrade the finding's confidence and note the gap.
   - **Diagnosis doesn't match:** Revise the characterization in the editorial letter. If the revision changes the severity, re-run the adversarial self-check for that finding.
   - **Fix class doesn't match:** Revise the intervention class. This usually means the root cause analysis was surface-level — the mechanism in the letter doesn't match the mechanism in the text.

**Execution mode considerations:**
- **Single-agent mode:** The spot-check runs in the same context after synthesis. The manuscript is already loaded; this adds ~5 targeted re-reads.
- **Multi-agent modes:** Dispatch the spot-check as a separate subagent that receives the editorial letter and the manuscript file path. This provides architectural isolation between the writer of the letter and its verifier — the strongest form of this check.

**Cost:** Minimal. 5 targeted scene lookups + comparison against 5 claims. Approximately 10-20K additional tokens in single-agent mode.

**Design principle:** This check exists because self-evaluation is unreliable. The same process that wrote the editorial letter cannot reliably verify its own claims — even with an adversarial self-check, the failure mode is confirming what you already believe. The spot-check forces re-contact with the primary source after the analytical work is complete.

### Annotated Manuscript + Crosslinked Letter (offered at run-end)

The marked-up manuscript copy — each finding placed **in the margin next to the prose that triggered it** — plus the editorial letter **crosslinked** to those margins is the #1 thing a human developmental editor hands back. APODICTIC generates it as a **pure projection** of artifacts that already exist (the snapshot, the Findings Ledger, the letter): comments only, every margin note a verbatim finding-field projection, the model **never** authors prose. See `references/annotated-manuscript.md`.

**Offer it — don't assume it, don't bury it behind a command.** A marked-up copy isn't always wanted (a quick triage doesn't need one), so **ask**. The offer fires **only when this run wrote a full editorial letter** — concretely, a `*_Core_DE_Synthesis_*.md` (or `*_Full_DE_Synthesis_*.md`) exists in the run folder. (A partial-de run writes `*_Partial_Diagnostic_*.md`, a fragment-de run writes `*_Fragment_Map_*.md`, a triage run writes a go/no-go memo — none match, so none are offered; `/ready` writes a full Synthesis letter, so it **does** offer.)

After the letter is written, validated, spot-checked, and the rolling state is updated, ask: *"Want your manuscript marked up — each finding in the margin — plus the letter crosslinked to it?"* On **yes**, run the generation chain — **staged in a temp copy so the run folder only ever receives verified artifacts**:

1. Copy the run-folder **inputs** (the `*_Manuscript_Snapshot_*` written at intake, the Findings Ledger, this editorial letter, and `Timeline.md` if present) into a scratch staging directory. Build/render run there, never in place.
2. `scripts/annotation_manifest.py build <staging>` — writes the annotation manifest + the annotated copy (anchors resolved from the ledger; comments are verbatim projections).
3. `scripts/validate.sh annotated-manuscript <staging>` — the **A1–A6** gate (the firewall, mechanical).
4. `scripts/crosslink.py render <staging>` — writes the crosslinked letter (back-links from the letter's `<!-- finding: F-… -->` markers to the manifest anchors; the marker form is pinned in `output-policy.md §Deficit Lock`).
5. `scripts/validate.sh crosslink <staging>` — the **X1–X4** gate.
6. **Only if A1–A6 *and* X1–X4 both pass**, move the three generated artifacts (`*_Annotation_Manifest_*`, `*_Annotated_Manuscript_*`, `*_Crosslinked_Letter_*`) from staging into the run folder, then point the writer to the marked-up copy as the revision surface. On any gate failure, report **which** gate failed and that **nothing was written** to the run folder (discard staging); the build is deterministic, so re-running after a fix is clean. On hosts without shell execution, perform the build/gate/render/gate inline with the same verified-or-absent discipline.

**No snapshot?** If this run skipped the intake snapshot (it shouldn't, for core/full-de) or the manuscript was revised mid-run, re-snapshot the assembled manuscript first (LF-normalized, trailing newline, no other change) before step 2. **Legacy / no-marker letter:** a letter with no `<!-- finding: F-… -->` markers still produces the annotated copy plus a no-op crosslinked letter (zero back-links, X-gate passes) — gracefully, not as a failure. **Re-generating later:** an author who declines here (or a run made before this was wired) can regenerate from the existing run folder via `/start`'s `diagnosed`-node dispatch (see `commands/start.md` §Step 0.5) — no separate command. Generation writes **no** diagnostic state beyond the human-readable pointer and changes **no** core-flow gate; do not invent a `next_action` value for it.
