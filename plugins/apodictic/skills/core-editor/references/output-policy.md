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
- **Evidence Density Self-Check (required):** Before finalizing each flag, count its specific scene/page references. If a flag cites fewer than 2 references, either locate additional textual evidence to support it or downgrade confidence (not severity — a real problem with thin evidence is still a real problem, but the author needs to know the evidence base is narrow). This check runs at the flag level during triage, not as a separate pass.

---

## Output Naming Convention (v0.4.15)

Write project artifacts to the project's `Outputs/` folder using:

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

`runlabel` should be date-based (`YYYY-MM-DD`) and may include agent tag (e.g., `codex53_2026-02-13`).

`Diagnostic_State.md` is a rolling state file (not run-specific). If missing, initialize from `references/diagnostic-state-template.md`.

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

---

## Severity Floor Rules (v0.4.14.3)

These rules prevent diagnostic softening from producing incoherent verdicts:

1. If any core-promise axis is rated Weak at High or Medium intensity, at least one flag must be Must-Fix. (A Weak core-promise axis with no Must-Fix flags means either the axis rating is wrong or the flag severity is wrong. Reconcile before proceeding.) At Low intensity or for peripheral axes, a Weak rating may stand with Should-Fix flags only, but must be explicitly justified.

2. If any Must-Fix flag has Systemic blast radius, the verdict cannot exceed Partial Fit (for tag audits) or equivalent ceiling for passes.

3. If three or more flags are Should-Fix or above, the verdict cannot be the highest positive band without explicit justification of why the flag volume doesn't impair the core contract.

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

1. **Appendix A: Diagnostic Detail.** Pointers to companion pass files and supplementary audit findings, with brief descriptions of what each contains. This tells the author where to find the evidence and revision tools behind the letter's arguments.

2. **Appendix B: Severity Calibration.** Compressed summary of the adversarial self-check — which findings were tested for softening or over-escalation, in which direction, and whether any severities were adjusted. This is the author's assurance that severity assignments were stress-tested, not just assigned.

3. **Appendix C: Framework Notes.** Analysis version, model, run date, passes completed, protocol flags, prior analyses on file, cross-version stability notes (if applicable). This is the run's metadata — it makes results reproducible and lets the framework owner track behavior across versions.

If a letter omits any of these appendices, the omission is a framework compliance failure regardless of the letter's analytical quality.
