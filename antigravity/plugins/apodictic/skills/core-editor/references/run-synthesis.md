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

   **Canonical Audit-Signal Propagation Rule.** Audit-internal severity signals do not become synthesis-layer Must-Fix / Should-Fix decisions automatically — the model must propagate them. Without an explicit rule, audit-internal signals (Compression Must-Fix floors, Reception Risk hard gates, Banister HIGH ratings) reliably die inside the audit findings file even when the model integrates the audit's narrative content into the editorial letter. The rule:

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

5. **Adversarial Self-Check (required before writing the letter).** Re-evaluate findings in both directions — test whether each severity is too soft (under-diagnosed) or too harsh (over-escalated). Adjust if the adversarial case is stronger than the original assignment. Record the results.

   **Upward pressure (testing for softening):** For each Should-Fix flag, state in one sentence why it should be Must-Fix. If the Must-Fix case is stronger, upgrade. For each Mixed axis, state in one sentence why it should be Weak. If the Weak case is stronger, downgrade.

   **Downward pressure (testing for over-escalation):** For each Must-Fix flag, state in one sentence the best case for Should-Fix. If the Should-Fix case is stronger, downgrade. For each Weak axis, state in one sentence the best case for Mixed. If the Mixed case is stronger, upgrade.

   **Evidence check (both directions):** For each Must-Fix flag, confirm you have 2+ specific scene/line references. If not, either find them or downgrade your confidence (not the severity).

6. **Adversarial Reader Stress Test (required).** Before writing the letter, run the stress test per `references/adversarial-stress-test.md`. **Begin the stress test by setting aside the pass findings and the Findings Ledger.** Inhabit the low-charity reader profiles and generate 3-5 adversarial claims from a holistic reading of the manuscript — what would a hostile reader attack regardless of what the passes found? Draw also from the Findings Ledger's "Unresolved Questions" entries, which may contain vulnerabilities the passes noticed but couldn't fully analyze. After generating the independent claims, reconcile them with the pass findings: which attacks are already covered by editorial letter findings? Which are new? New attacks enter the stress test section of the letter. Attacks already covered by the editorial argument are noted as convergent evidence but not duplicated. This is a separate exercise from the adversarial self-check (step 5) — the self-check tests severity calibration of existing findings; the stress test surfaces what hostile readers would attack, which may include issues not flagged by the passes.

7. **Decision-Layer Consolidation (required).** Before writing the letter, convert the diagnosis into explicit revision-control artifacts:

   - **Protected Elements candidate list:** 3-6 load-bearing elements from §3 strength findings that revision could easily damage
   - **Author Decisions:** 3-7 manuscript-specific decisions or commitments, organized as `Keep`, `Cut`, or `Unsure`. These are not generic preferences; they are the live choices that control revision order, book identity, interpretive stance, or risk posture.
   - **Control Questions:** Exactly 7 manuscript-specific questions that should govern revision. These are not "reader questions" and not workshop prompts. They are the high-leverage unresolved questions whose answers determine whether the major fixes actually land.

   Build these from root causes, audit findings, the stress test, and the strongest-case-against logic. If a decision or control question cannot be tied to a root cause, live blind spot, or structural pressure point, it probably does not belong here.

   **Mechanical check.** Decision-layer counts (3-6 / 3-7 / exactly 7) are mechanically validated by `scripts/validate.sh decision-layer-check <editorial_letter_file>` (or the equivalent inline check on hosts without shell execution) at Step 10's pre-output gate. Editorial judgment about *which* elements, decisions, and questions appear is preserved here at Step 7; counts and structural compliance are mechanical at Step 10. Override markers (one per check ID, body-only): `<!-- override: decision-layer-protected-elements -->`, `<!-- override: decision-layer-author-decisions -->`, `<!-- override: decision-layer-control-questions -->`. Markers in appendix bodies are non-canonical (synthesis body is canonical for findings; appendices hold evidence). Use the override path for principled deviations (e.g., short-fiction tier reduces Control Questions to 5; the model must say so in the body and explain in Appendix B).

   **Author Decisions counting (v1.8.0 calibration).** When the Author Decisions section uses Keep / Cut / Unsure (or Defer / Decide) level-3 subheads, the validator counts subhead clusters (typical 1-3) rather than the sub-bullets within them — the contract intent is "3-7 distinct decision categories," and Keep / Cut / Unsure naturally clusters multiple sub-decisions under each category. Letters without subheads are still counted by list-item or paragraph-form rules (verb-leading paragraphs starting with Protect / Keep / Cut / Defer / Decide / Unsure also count when neither list items nor bolded paragraphs are present). This calibration closes Phase 4 Wave 3 eval-coverage findings C1 + C2.

   **Argument-DE class (v1.8.0 calibration).** Argument-shaped letters (detected by markers: "Coalition-Partner Ground-Truth Recommendations", "Editorial-Dispute Territory", "Argument_State", "Claim Ladder", "Argument Engine") use a parallel decision-layer schema. The validator accepts variant heading names ("Coalition-Partner Ground-Truth Recommendations" or "Strengths / Protected Elements" for Protected Elements; "Editorial-Dispute Territory" for Author Decisions) and skips Check 3 (Control Questions) and Check 4 (Mandatory Appendices A/B/C) — argument-DE class is not held to the fiction-DE structural contract. Closes Phase 4 Wave 3 eval-coverage finding C3.

   **Evidence-density window (v1.8.0 calibration).** Per-Must-Fix evidence density (≥2 references) is checked over a paragraph-block window — from each Must-Fix line until the next Must-Fix occurrence OR the next section header (`^##` at column 0), whichever comes first. The wider window detects paragraph-form evidence that the prior fixed 6-line window missed. Closes Phase 4 Wave 3 eval-coverage finding C4.

9. **Conditional Underdiagnosis Retry Loop (required gate).** This step uses **enumerated detectable triggers**, not model self-judgment. Run `scripts/validate.sh underdiagnosis-triggers <editorial_letter_file>` (or perform the equivalent inline check on hosts without shell execution). The validator surfaces triggers; the model still owns the decision. For each fired trigger, you MUST either (a) upgrade the affected finding's severity in the synthesis layer, OR (b) document an override marker in the letter body (not in an appendix).

   **Enumerated triggers (detectable from artifacts; no model-judgment language):**

   1. **Convergence trigger:** the same concern (shared mechanism keyword) is flagged in 3+ pass artifacts, audit findings, or ledger entries with no synthesis-layer Must-Fix on it.
   2. **Hard-gate trigger:** any high-risk audit produces an Alert or hard gate (e.g., Reception Risk §7 hard gates, Compression Must-Fix floor) without a synthesis-layer Must-Fix.
   3. **Cross-pass complication trigger:** a final-third concern appears in both a character-pass and a structure-pass artifact.
   4. **Multi-axis severity trigger:** a single concern is rated across 2+ severity classes (series-impact, representation, reader-trust, or equivalent multi-axis hit) with no synthesis-layer Must-Fix.
   5. **Severity-floor trigger:** `validate.sh severity-floor` returns WARN or FAIL on the in-progress letter.
   6. **Propagation trigger:** `validate.sh audit-signal-propagation` returns ERROR or WARN — i.e., audit-internal signals failed to propagate to synthesis.

   **Override marker syntax** (one per trigger ID, placed in the letter body near the affected finding — NOT in an appendix):

   ```
   <!-- override: underdiagnosis-trigger-convergence — <one-sentence rationale> -->
   <!-- override: underdiagnosis-trigger-hard-gate — <one-sentence rationale> -->
   <!-- override: underdiagnosis-trigger-final-third — <one-sentence rationale> -->
   <!-- override: underdiagnosis-trigger-multi-axis — <one-sentence rationale> -->
   <!-- override: underdiagnosis-trigger-severity-floor — <one-sentence rationale> -->
   <!-- override: underdiagnosis-trigger-propagation — <one-sentence rationale> -->
   ```

   Markers in appendix bodies are non-canonical (synthesis body is canonical for findings; appendices hold evidence) and do not satisfy the override path. **Absence of override marker AND absence of severity upgrade = blocked synthesis.**

   **Loop semantics:** Step 9 fires once per synthesis pass. If any trigger remains unaddressed (neither upgraded nor overridden) when validate.sh runs, retry synthesis at higher severity for the affected findings. Once all fired triggers are addressed (upgrade-in-place or override-marker-in-body), Step 9 passes and synthesis proceeds to Step 10.

   Do not proceed to letter generation until the structural deficit analysis correctly reflects the manuscript's severity. Trigger conditions are detectable from named artifacts (Findings Ledger, Audit Invocation Log, audit findings files, in-progress letter); they are not "if the synthesis feels too soft" judgments.

10. **Pre-Output Synthesis Verification (required gate).** Before writing the letter, verify the synthesis is actually drawing from pass findings — not generating an editorial letter from general impressions of the manuscript. Run these checks:

   - **Findings integration check:** For each root cause identified in step 3, confirm it cites at least one specific ledger finding by pass and finding name. If a root cause exists only as a general impression without ledger grounding, either locate the supporting ledger entry or demote it to §4b (Additional Observations) with a note that it awaits pass-level confirmation.
   - **Section ordering check:** Confirm the letter will follow the required §1-§11 order. Protected Elements, Author Decisions, Control Questions, Strongest Case Against, and Stress Test are separate sections with distinct jobs — they must not be merged or omitted.
   - **Cap compliance check:** Root causes ≤ 5. Revision checklist items ≤ 10 (Core DE) or ≤ 15 (Full DE). Must-Fix flags ≤ 10.
   - **Severity floor check:** Severity-floor rules are canonical in `references/output-policy.md §Severity Floor Rules`. Run `scripts/validate.sh severity-floor <editorial_letter_file>` (or perform the equivalent inline check on hosts without shell execution) before delivering the letter. Failures block delivery until the model either re-tiers the offending finding or documents an override rationale in Appendix B (Severity Calibration). Do not restate the rules here — point to the canonical home.
   - **Decision-layer + appendix + evidence-density check:** Run `scripts/validate.sh decision-layer-check <editorial_letter_file>` (or perform the equivalent inline check on hosts without shell execution). The validator mechanically verifies Protected Elements count (3-6), Author Decisions count (3-7), Control Questions count (exactly 7), Appendices A/B/C presence, and per-Must-Fix evidence density (≥2 references). Editorial judgment about *which* elements/decisions/questions/appendix content appear is preserved at Step 7 and the editorial layer; counts and structural compliance are the validator's job. Do not restate the count contract here — point to the canonical homes (`references/output-policy.md §Mandatory Appendices` and `references/output-policy.md §Evidence Density Self-Check`). This validator runs alongside `severity-floor` and `audit-signal-propagation` as part of pre-output verification.
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

13. **Tone Compliance Check (required).** After section validation, run `scripts/validate.sh tone-check <letter_file>` on the saved editorial letter. The script blocks sycophantic superlatives (masterpiece, stunning, flawless, clean bill, tour de force, triumph, perfection) that indicate praise has displaced rigorous diagnosis. If the check fails, rewrite the offending passages with severity-calibrated language and re-run until it passes. This gate exists because the framework's job is accurate diagnosis; a letter that earns its praise through superlatives rather than evidence undermines every other structural check in this file.

### Presentation Format (Editorial Letter)

The synthesis is structured as a letter with scannable reference material. Prose carries the argument; headings, bold thesis statements, and a revision table provide scannability. Framework shorthand (severity labels, pass numbers, protocol stamps) stays out of the main text — it belongs in the appendices only.

**Required sections, in order:**

**1. Title Block**
```
# Development Edit: [Title]
### [Author] | [Word count] words | [Draft stage]
*APODICTIC Development Editor v[X] — [Date]*
```

**2. The Short Version.** One paragraph. Names both the primary asset and the primary liability. States the verdict class (reconception vs. targeted revision vs. polish). Names the revision's core ask. The author should be able to read this paragraph alone and know where they stand.

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

---

## Core DE Deliverables

**Reminder:** All outputs must follow the Author-Facing Language requirement (see `references/output-policy.md`). Translate all framework shorthand on first use.

### Editorial Letter (Core Synthesis)

The primary deliverable. Format specified in §Core DE Synthesis above.

### Run Folder and Rolling State

All run artifacts (editorial letter, pass reports, contract, findings ledger, audit invocation log, results guide) are written to the **run folder** (`runs/YYYY-MM-DD_{model}_{type}/`) inside the project root. See `references/output-policy.md` §Folder Architecture.

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
- `triage_summary` — after synthesis (counts of must-fix, should-fix, could-fix)
- `control_questions` — after synthesis and after each revision round (open/answered/deferred counts)
- `revision_progress` — after each revision round (steps_complete, current_step)
- `session_count` and `handoff_count` — increment on each new session or handoff
- `state_lines` — line count of `Diagnostic_State.md` (used by state gardening to trigger archival)
- `contract_hash` — SHA-256 of the contract file, set at intake, checked at pre-pass re-grounding (see `run-core.md` §Mechanical Validation)
- `next_action.key` — enumerated dispatch key for resume routing. Valid values: `run_passes`, `run_synthesis`, `run_spot_check`, `deliver`, `revision_round`, `run_audits`, `coaching`, `handoff_reentry`. See `commands/start.md` §Resume Target for the full dispatch table.
- `next_action.description` — human-readable context for display (e.g., "resume Tier 2 passes — Pass 5 next"). Not used for routing.

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
