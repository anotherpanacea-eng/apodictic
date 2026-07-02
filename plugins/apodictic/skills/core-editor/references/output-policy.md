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
- ✅ "All three evaluative lenses agree on this point, and the diagnosis survived a deliberate attempt to refute it against the text"

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

## Output Structure & Filesystem Conventions

Folder architecture, run-folder layout, output and file naming, the model-tag table, and lifecycle conventions have moved to `references/output-structure.md` — loaded on demand at write/persist time, not during diagnostic reasoning. Load it when creating run folders, naming artifacts, or writing rolling state.

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

**HIGH means "survived" (synthesis-bound findings).** For synthesis-bound Must-Fix and HIGH-candidate findings, HIGH requires the existing bar (2+ passes or unambiguous textual proof) **and** a recorded refutation attempt with `outcome == survived` — the Finding Disconfirmation Pass, `run-synthesis.md §Step 6b`. Survival is a **necessary condition for HIGH, never a confidence-raising event**: a `survived` outcome leaves confidence exactly where the ledger already had it — the pass can only lower or hold, never lift (`weakened` caps at MEDIUM; `refuted` transcribes LOW/UNCERTAIN; severity is never touched). Convergence still *feeds* confidence (§Canonical Severity Scale, lens verdicts) — it is no longer *sufficient* for HIGH. The only legible exception is a cap-bound, disclosed HIGH (`bound: true` budget + the not-attempted-budget marker + Appendix B line), whose author-facing language must say *convergence-only, not stress-tested*. Enforced by `scripts/validate.sh refutation-coverage` / `refutation-evidence` / `refutation-write-scope`.

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

## Canonical Severity Scale (v2.0.0)

*Canonical home for the framework's single severity vocabulary. Every audit-internal severity signal — Must-Fix floors, hard gates, HIGH/Alert ratings, named flags, Pass-10 inconsistency counts — maps onto this one scale via the Canonical Audit-Signal Propagation Rule (`run-synthesis.md §Step 2`) and its per-audit table (`pass-dependencies.md §4e`). Do not introduce a parallel severity vocabulary; relabel local audit scales onto these three tokens.*

APODICTIC has exactly three severity tiers:

- **Must-Fix** — the manuscript fails a core promise here; shipping without addressing it risks the book. Audit hard gates and Must-Fix floors land here.
- **Should-Fix** — a real, pattern-level weakness the author should address; not contract-breaking on its own. Most pattern-level flags and MEDIUM signals land here.
- **Could-Fix** — a local, low-blast-radius issue; optional polish. Isolated flags and LOW/Note signals land here.

**These are the only severity tokens.** Use them verbatim — the mechanical validators `severity-floor` and `audit-signal-propagation` grep these exact strings.

**Not severity — orthogonal axes (do not collapse into the scale):**
- **Confidence** (`HIGH` / `MEDIUM` / `LOW` / `UNCERTAIN`, see §Confidence Calibration) — how sure the diagnosis is, not how bad the problem is. A real problem with thin evidence keeps its severity and loses confidence, never the reverse.
- **Prose tier** (`P0`–`P3`) — line-level prose-quality band; independent of structural severity.
- **Readiness / verdict bands** (submission-readiness tiers, tag-audit Fit verdicts) — whole-manuscript dispositions that *consume* severity counts; they are not themselves severity.
- **Lens verdicts** (per-lens agreement signals) — convergence indicators that feed confidence, not severity. (Convergence alone no longer suffices for HIGH on synthesis-bound findings — HIGH additionally requires a survived refutation attempt; see §Confidence Calibration and `run-synthesis.md §Step 6b`.)

Audit-internal scales (AIC Spot/Pattern/Systemic, Reception Note/Flag/Alert, Red Team Fatal/Major/Manageable, Timeline paradox/drift/ambiguity, etc.) are *local vocabularies* that propagate **onto** this canonical scale per §4e; they are not additional severity tiers.

---

## Severity Honesty Protocol (v0.4.14.3)

*Canonical home for anti-sycophancy / no-self-revise rule. Other surfaces (`adversarial-stress-test.md §Lock-then-test protocol` / §Anti-softening rule, `specialized-audits/references/craft/reception-risk.md §Lock-then-classify` / §Forbidden #6, `run-synthesis.md §Step 6 Adversarial Self-Check`) reference here and add only context-specific elaborations (stress-test ordering, audit lock-then-classify discipline, self-check up/down pressure). The general principle — LLMs reliably talk themselves out of hard findings; severity locks before steelmanning — lives here. Per-audit Deficit-First Diagnostic Rule blocks (each tailored to the audit's failure modes) are the operational expression of this principle and stay in their audit reference files.*

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
5. **Evidence-first, verifier-backed underdiagnosis checks:** Do not assume a text is structurally sound simply because the prose flows well. Absence of structural friction must be proven, not assumed. A text is only "structurally clean" if the Reader Stress Test, the Rejection Memo, and the Absence/Blind-Spot Inventory explicitly fail to surface deep flaws. **The Deficit Lock (below) is the operational enforcement of this rule.**

### Deficit Lock (generation-order rule, v2.0.0)

*The highest-leverage anti-softening mechanism: lock severity before any charity reframing can soften it. This is the synthesis-layer sequencing of the lock-then-test discipline canonical in `adversarial-stress-test.md §Lock-then-test protocol` — it does not restate that protocol, it orders it against the synthesis steps. It closes the one honesty leak the existing coherence gates miss: a letter that quietly under-delivers a finding it already diagnosed, while still passing severity-floor and audit-signal-propagation.*

At Triage (`run-synthesis.md §Step 5`), the moment a finding is assigned **Must-Fix** or **Should-Fix**, commit it as a structured Finding (`apodictic.finding.v1`, see `findings-ledger-format.md`) at that severity in the Findings Ledger — **before** any later step that could lower it runs: the Adversarial Self-Check's downward pressure, the Distinguish Protocol's cultural-charity downgrade, or any genre-specific exception. Once a severity is locked:

- Later steps may **raise** severity freely (under-diagnosis is the failure mode being guarded against — there is no friction on getting harder).
- Later steps may **lower** a locked severity, or decline to deliver a locked finding at its locked tier, **only** by recording an **ID-scoped** body override marker — `<!-- override: softness-downgrade F-<ORIGIN>-<NN> — <one-sentence rationale> -->`, naming the exact Finding Lifecycle ID it downgrades — plus a parallel Appendix B (Severity Calibration) entry. The override acknowledges **only the named finding**; a bare marker with no resolvable ID acknowledges nothing (one marker can never blanket-mask every locked finding — the Deficit Lock is per-finding). Silent softening is forbidden.
- Each locked finding carries its **Finding Lifecycle ID** (`id`, e.g. `F-P5-01`; see `findings-ledger-format.md`). The gates match a locked finding to its delivery **by ID (exact)** when present — the editorial letter cites the ID in an HTML comment near the delivered finding and in the Severity Calibration appendix — falling back to evidence/mechanism heuristics only for id-less legacy findings.
- **Canonical near-finding marker form (pinned).** Write the near-finding citation as **exactly** `<!-- finding: F-… -->` (the literal token `finding:`, one space, the id). This strict form is a **subset** of the loose "any `F-…` token inside any `<!-- … -->`" that `finding-trace` / `softness-check` already accept, so pinning it changes nothing for the honesty gates — but it is **required** by the Annotated-Manuscript crosslink producer, whose parser recognizes *only* this form when back-linking the letter to the marked-up copy (`references/annotated-manuscript.md`; `docs/annotated-manuscript-producer.md` §1d). A near-finding citation written any other way (`<!-- F-P5-01 -->`, `<!-- id: F-P5-01 -->`) still satisfies the honesty gates but yields **zero** crosslink back-links. **Duplicate-back-link guard:** the Severity Calibration appendix cites the same ids, but inside `apodictic:severity_calibration` blocks (a *different* comment form), **not** `<!-- finding: … -->` markers — keep it that way, so each finding gets exactly one back-link (from its near-finding marker), never a second from the appendix.
- Mechanical gates: `scripts/validate.sh softness-check <editorial_letter> <findings_ledger>` compares the delivered letter against the locked ledger and blocks delivery on any unmarked downgrade; `scripts/validate.sh deficit-lock <findings_ledger>` verifies every synthesis-bound finding was locked structurally (not merely that one lock exists). (Weak-axis-vs-Must-Fix coherence remains owned by `severity-floor`; the softness gate does not duplicate it.)

The Deficit Lock does not forbid charity — it makes charity *legible*. A genuine over-diagnosis can still be corrected; it just leaves a recorded trace instead of disappearing silently.

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
