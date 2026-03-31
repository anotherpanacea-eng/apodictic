# Dialectical Clarity — Enrichment Level-Setting Research
## Version 2.0
*Compiled: March 2026*
*Sources: Codex level-setting, Claude research, Gemini research, v1.0 deployed audit, argumentation theory literature*

---

## What This Document Does

Provides the theoretical backbone for the Dialectical Clarity v2.0 enrichment. Identifies the frameworks that ground the new diagnostic capabilities (warrant analysis, audience calibration, dialectical integrity, cross-section tracking, distinguish protocol), catalogs the failure modes the enrichment targets, documents positive cases of structural excellence across genres, and names the genuinely unsettled questions where the audit must remain humble.

This is reference material for the audit, not a replacement for it. The audit spec defines what to diagnose and how. This document explains *why* those diagnostics work and what theoretical traditions they draw from.

---

## Theoretical Frames

Seven frameworks ground the v2.0 enrichment. Each is marked as **durable** (well-established, unlikely to be overturned) or **inference** (the application to editorial diagnosis is the enrichment's own extension, not directly stated in the source tradition).

### 1. Toulmin's Warrant Model [DURABLE]

Stephen Toulmin's *The Uses of Argument* (1958) separates argument into six components: claim, grounds (data), warrant (the principle connecting grounds to claim), backing (support for the warrant), qualifier (degree of confidence), and rebuttal (conditions under which the warrant doesn't hold).

**What it solves for the audit:** The v1.0 audit extracted claims (CL codes) and mapped support (SM codes) but had no mechanism for testing the inferential bridge between them. The warrant is that bridge. A text can have accurate data and a reasonable claim, and still fail structurally because the principle connecting them is absent, contested, or relies on an audience assumption the text never earns.

**Implementation:** Step 4 (Warrant & Inference Bridge) operationalizes Toulmin directly. WR0 (warrant gap), WR1 (missing backing), WR2 (scheme fragility), and WR3 (qualifier mismatch) map onto Toulmin's components. The qualifier dimension is especially important: Toulmin emphasizes that most real arguments are not deductively certain but carry qualifiers ("probably," "presumably," "in most cases"). When a text drops its qualifiers, the confidence exceeds what the argument structure can bear.

**Key insight [INFERENCE]:** Warrant visibility is audience-relative. A warrant that is recoverable for an expert audience (who share the disciplinary framework providing the warrant) may be genuinely missing for a general audience. This is why WR0 calibrates against the AC classification from Step 1: the same evidence-to-claim connection can be a pass for one audience and a failure for another.

### 2. Walton's Argumentation Schemes [DURABLE]

Douglas Walton, Chris Reed, and Fabrizio Macagno cataloged 96 distinct argumentation schemes, each a stereotypical pattern of defeasible reasoning with associated "critical questions" that test the scheme's binding force. Key schemes for the audit's genres: argument from expert opinion, practical reasoning (goal-to-action), argument from consequence, argument from analogy, argument from sign, argument from waste (sunk costs), and argument from position to know.

**What it solves for the audit:** The v1.0 support map classified evidence by type (reason, example, data, authority, experience) but not by the reasoning pattern it employed. Two arguments can both use "authority" evidence but fail for completely different reasons: one because the authority isn't credible in the relevant domain, the other because the authority's finding has been misapplied to a case it doesn't cover. Scheme awareness sharpens the diagnosis.

**Implementation:** Step 3 adds "scheme hints" as a diagnostic aid, not a mandatory taxonomy. The audit doesn't require the reviewer to classify every evidence unit into one of 96 schemes. It provides 8 common scheme hints (authority, consequence, causal, analogy, example, testimony, practical reasoning, sign) with one practical first question per scheme. The critical question is what matters: "Is this source credible on this exact point?" is more diagnostically useful than "this is an argument from expert opinion."

**Design choice [INFERENCE]:** The full Walton compendium was deliberately not integrated. Ninety-six schemes would overwhelm usability and violate the audit's operational constraints. The enrichment uses Walton's *principle* (different reasoning patterns have different vulnerabilities) without importing his *catalog* as a checklist. FM-A19 (Authority Overreach) and FM-A15 (Intermediate Outcome Fallacy) are both scheme-specific failures that the v1.0 audit could not name.

### 3. Pragma-Dialectics [DURABLE]

The Amsterdam School (Frans van Eemeren and Rob Grootendorst) defines argumentation as a procedure for resolving differences of opinion through critical discussion, governed by rules. Their "Ten Commandments" specify procedural obligations: parties must not prevent each other from advancing positions, burden of proof falls on the party advancing a standpoint, attacks must relate to the standpoint actually advanced, failed defenses must result in retraction, and so on. Fallacies are redefined as violations of these procedural rules, not as formal logic errors.

**What it solves for the audit:** The v1.0 OB codes tested whether objections were addressed and classified the quality of engagement (substantive, strawman, evasion). But they didn't test whether the argumentative procedure itself was fair. A text can address every objection and still be procedurally dishonest if it smuggles in contested starting points, evades responsibility for unstated premises, performs pseudo-resolution, or maintains strategic ambiguity. The DI (Dialectical Integrity) codes operationalize pragma-dialectical fairness.

**Implementation:** DI0 (starting-point smuggling) captures violations of the Freedom Rule and the Starting Point Rule. DI1 (unexpressed-premise evasion) captures violations of the Unexpressed Premise Rule. DI2 (pseudo-resolution) captures violations of the Closure Rule. DI3 (ambiguity doing argumentative work) captures violations of the Usage Rule. DI4 (Motte-and-Bailey drift) captures violations of the Standpoint Rule. These are not abstract logical classifications; they're editorial diagnoses of specific manuscript behaviors.

**Key insight [INFERENCE]:** Pragma-dialectics was designed for interactive debate. Its application to monological texts (essays, briefs, testimony) requires adaptation. In dialogue, violations are visible because the interlocutor can challenge them. In monologue, violations are harder to detect because the text controls the conversational frame. The DI codes compensate by asking the reviewer to reconstruct what a skilled interlocutor would challenge.

### 4. Perelman/Olbrechts-Tyteca and Bitzer: Audience and Rhetorical Situation [DURABLE]

Chaim Perelman and Lucie Olbrechts-Tyteca (*The New Rhetoric*, 1958) argue that all argumentation is fundamentally audience-directed. What counts as "reasonable" shifts depending on whether the arguer addresses a particular audience or a universal audience. Lloyd Bitzer (*The Rhetorical Situation*, 1968) defines the conditions for effective discourse through three components: exigence (an imperfection marked by urgency), audience (those capable of being influenced), and constraints (the factors limiting available strategies).

**What it solves for the audit:** The v1.0 audit analyzed argument structure in a vacuum. An argument lacking explicit objection-handling might be structurally sound for a sympathetic audience (where shared values provide implicit warrants) but structurally disastrous for a hostile audience (where every assumption needs backing). The AC (Audience Calibration) codes make this calibration explicit, preventing false positives (flagging audience-appropriate shortcuts as failures) and false negatives (allowing weak arguments to pass because they use correct formatting).

**Implementation:** Step 1 adds audience classification along three dimensions: expertise (general/mixed/expert), receptivity (sympathetic/mixed/hostile), and consequence context (low/medium/high). Every subsequent step calibrates against this classification. The genre calibration section specifies per-form and per-audience tightening/loosening rules with false-positive guards.

**Key insight [INFERENCE]:** Audience calibration is not audience pandering. The audit diagnoses whether the text is built for its audience honestly, not whether it's optimized for persuasion. AC3 (sympathetic-audience flattery drift) specifically catches texts that lean on agreement rather than supplying structure. The distinction between "calibrated for audience" and "manipulating audience" is the firewall's central challenge in this area.

### 5. Fricker: Epistemic Injustice and Testimonial Authority [DURABLE]

Miranda Fricker (*Epistemic Injustice*, 2007) identifies two forms of structural wrong: testimonial injustice (prejudice causes a hearer to assign deflated credibility to a speaker) and hermeneutical injustice (gaps in collective interpretive resources disadvantage marginalized groups in making sense of their experience).

**What it solves for the audit:** The v1.0 audit mapped "authority" and "experience" as evidence types but didn't interrogate the power dynamics determining whose authority is recognized and whose experience is validated. FM-A14 (Epistemic Erasure) names the specific failure where an argument relies exclusively on institutional authority while structurally silencing the lived experience of affected populations. This is not a political diagnosis; it's a structural one. An argument about criminal justice that relies only on recidivism data without reentry testimony has a structural gap in its evidence base, regardless of the writer's politics.

**Implementation:** Step 7 adds witness position classification (observational, participant, interpretive, representative, institutional). BP6 (testimonial overburden) and FM-A14 (epistemic erasure) are the primary diagnostic codes. The audit does not require every argument to include lived experience. It flags when an argument *about affected populations* relies exclusively on detached authority while the affected populations' knowledge is absent.

**Key insight [INFERENCE]:** Fricker's framework applies bidirectionally. Epistemic erasure (FM-A14) catches arguments that silence lived experience. But BP6 (testimonial overburden) catches arguments that ask lived experience to carry more than it structurally can. The audit does not privilege either direction; it tests whether the evidence base is structurally adequate for the claim being made.

### 6. Fallacy Theory (Selective Integration) [DURABLE framework, INFERENCE in selection]

The v1.0 audit deliberately avoided the informal-logic tradition of cataloging named fallacies. This decision was correct: fallacy-naming frequently produces false precision, and many "fallacies" (ad hominem, appeal to authority, appeal to emotion) are context-dependent rather than inherently invalid.

**What the enrichment changes:** The v2.0 selectively incorporates failures that have specific structural mechanisms, not just Latin names. CL4 (definitional smuggling) captures equivocation without requiring the reviewer to cite "the fallacy of equivocation." BP4 (false precision) captures false exactness without requiring "the fallacy of misplaced concreteness." FM-A13 (structural Motte-and-Bailey) names a specific oscillation pattern. FM-A15 (intermediate outcome fallacy) names a specific causal-chain break.

**Design principle [INFERENCE]:** The audit uses fallacy theory's diagnostic insight (arguments fail in recurring structural patterns) without importing its taxonomic apparatus (named Latin fallacies with definitional boundary disputes). The focus is on the mechanism of failure, not the nomenclature.

### 7. Alternative Argument Traditions and Form Pluralism [INFERENCE]

Western analytic argument follows a broadly linear structure: thesis, evidence, objection handling, conclusion. Many effective arguments operate on different structural paradigms that the v1.0 audit was not calibrated to recognize. The Distinguish Protocol (Step 9) prevents the audit from committing a form of hermeneutical injustice by classifying unconventional structures as failures.

**Recognized traditions:**

- **Narrative argumentation:** Conclusions emerge through juxtaposition and thematic reflection. The "evidence" is lived experience; the "warrant" is the universal empathy the narrative elicits. Well-documented in Indigenous storytelling traditions and literary personal essays. The argument is implicit but recoverable.

- **Dialogical argumentation:** Meaning is co-constructed through exchange. Positions develop, shift, and synthesize through dialogue rather than being defended monolithically. Rooted in Socratic method, formalized in Barth and Krabbe's dialogical logic, and common in interview-structured longform journalism.

- **Circular/recursive argumentation:** The argument covers the same ground repeatedly at increasing depth, operating as a spiral. Recognized in Eastern philosophical traditions, meditative and contemplative essays, and some Indigenous knowledge systems. Linear analysis misdiagnoses the recursion as repetition.

- **Nyaya logic (classical Indian philosophy):** Five-member syllogism insisting on empirical grounding. Blends deduction and induction in ways that Western formal logic separates. The structure looks foreign to thesis-evidence analyzers but is rigorously evaluable on its own terms.

- **Prophetic address and call-and-response:** Draws the audience into participatory agreement, then reverses to expose complicity. The "objection handling" is embedded in the reversal. Common in African-American rhetorical traditions, religious discourse, and ancient Hebrew disputation.

- **Testimonial accumulation:** Multiple first-person accounts build a case through volume and pattern rather than through explicit claim-evidence structure. The claim emerges from the pattern across accounts, not from any single account's argument.

**Implementation:** Step 9 applies the cultural charity principle: when a text fails Western structural expectations, presume unconventional form before diagnosing structural failure. The six decision tests (claim-accessibility, evidence-evaluability, warrant-recoverability, scope-honesty, objection-awareness, form-fit) are deliberately form-independent. They test whether the argument is evaluable, not whether it follows a specific template.

**Genuinely unsettled [INFERENCE]:** The boundary between "unconventional form" and "structural weakness disguised as unconventional form" is not fully resolved. A poorly argued personal essay can hide behind "narrative argumentation." A vague manifesto can claim "prophetic address." The Form-fit test is the audit's best defense: is the form doing real argumentative work, or shielding weakness? But this test requires judgment that cannot be fully algorithmic.

---

## Failure Mode Catalog

Nineteen named patterns. Each entry provides the theoretical grounding, the mechanism of failure, detection heuristics, and the editorial question that distinguishes it from adjacent failures.

### Architectural Failures (detectable at entry)

**FM-A1: The Drive-By Thesis**
Grounding: Basic claim-evidence logic. No specific theoretical tradition required.
Mechanism: The text has observations, insights, even evidence, but no stable claim organizing them. Each section gestures at a different thesis.
Detection: CL0 or CL1 fires in Step 2. SM0 fires on multiple subclaims because there's no stable claim to support.
Distinguish from: FM-A5 (Hidden Argument), where a claim exists but is disguised. In FM-A1, no claim exists.

**FM-A3: The Persuasion Machine**
Grounding: Perelman's distinction between persuasion and conviction. A text can move the audience without providing evaluable reasons.
Mechanism: Narrative emotional force replaces argument. Each vignette is devastating; together they produce conviction without justification.
Detection: OB0 or OB4 + NE1 + NE3. The structural test: remove all vignettes and read what remains. If the argument collapses, it was the vignettes doing the work.
Distinguish from: Legitimate testimony (AT4) where narrative IS the evidence. The difference: in FM-A3, the narrative is the *only* support for claims that require more than testimony. In AT4, the testimony carries claims it's structurally able to carry.

**FM-A5: The Hidden Argument**
Grounding: Perelman's concept of dissociation; Bitzer's exigence theory (the text responds to an urgency it doesn't name).
Mechanism: The piece presents as story or inquiry but is arguing a position through selection, framing, and juxtaposition.
Detection: AT0 + classification as narrative by another audit. Apply Distinguish Protocol: if the argument is recoverable, it's unconventional form, not failure.
Distinguish from: FM-A1 (where no argument exists) and legitimate narrative argumentation (where the implicit argument is a chosen form, not an accident).

### Relational Failures (between-code gaps)

**FM-A6: The Warrant Leap**
Grounding: Toulmin's warrant concept. The gap is not in the evidence (SM) or the claim (CL) but in the connection between them.
Mechanism: Evidence is real and relevant. Claim is reasonable. The principle connecting them is unstated. The argument functions only for readers who already supply the warrant from their own beliefs.
Detection: WR0 fires; SM passes. The reviewer's question: "Why does this evidence prove this claim?" If the answer requires a norm, causal principle, or ideological commitment the text never states, WR0 is the diagnosis.
Distinguish from: SM1 (irrelevant support), where the evidence doesn't bear on the claim at all. In FM-A6, the evidence is relevant; the bridge is missing.
Anchor line: The most common sophisticated failure in argument-shaped writing. Detected in every genre, at every skill level.

**FM-A7: Definitional Smuggling**
Grounding: Walton's fallacy of equivocation; pragma-dialectics Usage Rule.
Mechanism: A key term silently changes meaning across the piece. The argument appears continuous because the same word persists, but the meaning has shifted between premise and conclusion.
Detection: CL4 fires in Step 2; often co-occurs with DI3. Cross-section tracking (Step 8) catches it when the shift is gradual.
Distinguish from: CL1 (claim unstable), which is overt drift. CL4 is covert: the claim *looks* stable because the words are the same.
Common terms vulnerable to smuggling: freedom, harm, violence, safety, expertise, democracy, justice, community, efficiency, equity, consent, rights, accountability.

**FM-A12: Emotional Inflation (Stakes Disconnect)**
Grounding: Bitzer's concept of exigence; Perelman's distinction between particular and universal audience.
Mechanism: The stakes claim operates at civilizational or existential register while the evidence is local and specific. The gap between the evidence's actual reach and the stakes language's urgency is bridged by metaphor, not by argument.
Detection: NE3 + BP2 + stakes claim analysis. Remove the stakes language and read the evidence alone: if the evidence supports a moderate, local conclusion, the inflation is present.
Distinguish from: Legitimate urgency, where the stakes genuinely are existential and the evidence supports that scale. Also from passionate writing, which may use intense language for claims the evidence fully supports.

**FM-A13: Structural Motte-and-Bailey**
Grounding: Nicholas Shackel's original formulation; pragma-dialectics Standpoint Rule.
Mechanism: The text maintains two claims simultaneously: a modest defensible claim (the motte) and an ambitious controversial claim (the bailey). Evidence supports the motte; the conclusion asserts the bailey. Under pressure, the text retreats.
Detection: DI4 + CL1. Distinguished from ordinary claim drift by intentionality: check whether the text defends the ambitious version or only the modest one.
Distinguish from: CL1 (unintentional drift) and scope creep (BP2, which is gradual broadening). Motte-and-Bailey is oscillation between two distinct claims.

**FM-A15: Intermediate Outcome Fallacy**
Grounding: Blackwell (2013) on assumption smuggling in intermediate outcome tests of causal mechanisms.
Mechanism: The argument proves A causes B (the mediator), then assumes B causes C (the outcome) without proof. The causal chain has a missing link that the rigor of the A→B proof disguises.
Detection: WR2 + BP1. Trace the full causal chain: if there's a gap between the proven mediator and the claimed outcome, the failure is present.
Distinguish from: WR0 (warrant gap), which is broader. FM-A15 is specifically about causal chains where an intermediate variable is proven but the final link is assumed.
High-frequency in: Social science policy arguments, public health interventions, education reform proposals.

**FM-A17: Anecdote-to-Principle Leap**
Grounding: Fricker's testimonial framework; Toulmin's warrant requirement.
Mechanism: A true, vivid anecdote is treated as sufficient evidence for a general principle. The gap between "I saw this happen" and "this is how the system works" is bridged by implicit warrant that the text never states.
Detection: BP6 + WR0 or BP1. The structural test: does the text supply any evidence beyond the anecdote for the general principle?
Distinguish from: Legitimate testimonial evidence (where the anecdote supports a local claim it can structurally carry) and from FM-A14 (epistemic erasure, which is about whose evidence is absent, not about how far evidence travels).
High-frequency in: Legislative testimony, advocacy journalism, personal essay with policy implications.

### Quality Failures (inadequate passes)

**FM-A8: False Precision Theater**
Grounding: The fallacy of misplaced concreteness (Whitehead); statistical literacy literature on precision vs. accuracy.
Mechanism: The text performs certainty that the evidence base cannot support. Decimal precision on ordinal data. Single-study conclusions stated as established findings. Percentage changes on small absolute numbers.
Detection: BP4, often with WR3. Compare the precision of the language against the nature of the evidence.
Distinguish from: Legitimate precision, where the data and methodology support the level of exactness claimed.
High-frequency in: White papers, policy briefs, data journalism, academic manuscripts with small-n studies.

**FM-A9: Concession Without Cost**
Grounding: Pragma-dialectics Closure Rule (failed defenses must result in retraction or qualification).
Mechanism: The text performs the *form* of concession but the concession changes nothing. The claim is not narrowed. The qualifier is not adjusted. No subclaim is modified. The concession exists to make the writer look fair.
Detection: OB4. The structural test: read the argument with the concessive passage removed. If the argument is identical, the concession was costless.
Distinguish from: Legitimate concession (which modifies the claim or its scope) and from OB2 (evasion, which doesn't even perform the form of engagement).
High-frequency in: Academic writing (especially literature review sections), advocacy journalism, policy briefs.

**FM-A11: Evidence Laundering**
Grounding: Scholarly citation standards; Walton's chain of reasoning.
Mechanism: The text cites a secondary source's interpretation as if it were primary evidence. A newspaper's summary of a study is treated as the study. A think tank's analysis is cited as if it were the underlying data.
Detection: SM4. Trace the citation chain one level deeper. If the cited source is interpreting rather than reporting primary evidence, the interpretive step is invisible to the reader.
Distinguish from: Legitimate secondary citation (where the secondary source is identified as interpretive and the reader can assess the mediation). Also from SM1 (irrelevant support), where the evidence doesn't bear on the claim at all.
High-frequency in: Op-eds, advocacy writing, general-audience policy arguments.

**FM-A14: Epistemic Erasure**
Grounding: Fricker's testimonial and hermeneutical injustice.
Mechanism: The argument relies exclusively on institutional, quantitative, or detached authority while structurally silencing the lived experience of affected populations. The evidence base *looks* adequate by conventional standards; the structural question is whose knowledge was deemed admissible.
Detection: SM3 (authority-only) + AC0 or AC1. Check whether the argument concerns a population whose experience is available but unconsulted.
Distinguish from: Arguments where lived experience is genuinely irrelevant to the claim (e.g., a mathematical proof, a technical engineering assessment). FM-A14 fires only when the claim is *about* affected populations and their experience is structurally excluded.
High-frequency in: Mental health policy (clinical authority without patient voice), criminal justice (recidivism data without reentry testimony), education (test scores without student experience).

**FM-A19: Authority Overreach**
Grounding: Walton's argument from expert opinion and its critical questions (especially: "Is the source an expert in the domain of the claim?").
Mechanism: An expert whose credentials are in domain X makes claims in domain Y. The text presents the authority as if expertise were fungible across domains.
Detection: WR2 + SM1. Check whether the cited authority's domain matches the claim's domain.
Distinguish from: Interdisciplinary expertise (where the authority genuinely has relevant knowledge across domains) and from SM1 (where the authority isn't cited for expertise at all).
High-frequency in: Public testimony, expert commentary in journalism, policy briefs citing academic sources outside their discipline.

### Dynamic Failures (accumulate over distance)

**FM-A2: The Evidence Pile**
Grounding: Basic logical structure. Individually valid premises do not automatically compose into a valid argument.
Mechanism: Each section's evidence is real, relevant, and matched to its subclaim. But the subclaims don't add up to the main claim, or the aggregate evidence supports a narrower conclusion than the text asserts. The failure is invisible from inside any single section.
Detection: SM passes + CL2 or BP2. Step 8 cross-section tracking catches it by comparing section-level conclusions against the piece-level conclusion.
Distinguish from: FM-A4 (scope inflation), which is specifically about scope creep. FM-A2 is about logical composition: the parts don't add up to the whole.

**FM-A4: Scope Inflation**
Grounding: Basic scope logic; Toulmin's qualifier.
Mechanism: Evidence supports "sometimes" or "in this case." Conclusion asserts "always" or "we must." The writer has lived with the material long enough that the particular feels universal.
Detection: BP0 + BP2. Step 8 tracking shows the scope widening across sections.
Distinguish from: FM-A2 (evidence pile), where the subclaims don't add up. In FM-A4, the subclaims add up to a local conclusion, but the text asserts a universal one.

**FM-A10: The Uncompared Proposal**
Grounding: Walton's practical reasoning scheme (which requires evaluation of alternatives).
Mechanism: The proposal is defended against the status quo only. The second-best alternative is never named. The reader cannot judge whether this proposal is better than other available interventions.
Detection: AT3 + BP5. Step 8 checks whether alternatives appear anywhere in the full piece.
Distinguish from: FM-A18 (implementation blindspot), which is about execution, not alternatives. A proposal can address alternatives but ignore implementation, or address implementation but ignore alternatives.

**FM-A16: Qualification Erosion**
Grounding: Toulmin's qualifier; cognitive psychology on confidence drift in extended writing.
Mechanism: Hedging language appears in early sections but progressively disappears. The conclusion carries certainty the evidence chain never earned. The writer didn't consciously strengthen the claims; the qualifiers evaporated over distance.
Detection: WR3 operating across sections. Step 8 tracks qualification level from introduction through conclusion.
Distinguish from: WR3 firing within a single section (which is local qualifier mismatch, not dynamic erosion). FM-A16 requires the cross-section comparison.

**FM-A18: Implementation Blindspot**
Grounding: Policy implementation literature; the distinction between policy argument and policy design.
Mechanism: The proposal proves the problem and argues the principle. But cost, timeline, institutional capacity, political feasibility, and unintended consequences are entirely absent. The argument is structurally complete as *advocacy* but structurally incomplete as *proposal*.
Detection: AT3 + clean CL/SM/WR/BP on problem and principle + absence of implementation analysis.
Distinguish from: FM-A10 (uncompared proposal), which is about alternatives. FM-A18 is about execution. Also: AT3 calibration matters. An op-ed may legitimately omit implementation details that a policy brief cannot.

---

## Positive Cases: Structural Excellence by Technique

Organized by technique rather than by genre or author, to show how the same structural strategies produce different forms of excellence across different contexts.

### Warrant Legibility

The strongest arguments make their inferential bridges visible without becoming pedantic. In policy briefs, this looks like explicit causal reasoning ("X causes Y because Z mechanism, as demonstrated by Q study"). In personal essays, it looks like reflective commentary that articulates the connection the narrative implies ("The ice on the windshield that morning wasn't metaphor. It was the thing itself: the system working as designed, and designed to freeze"). In academic writing, it's the literature review that doesn't just cite supporting studies but articulates the principle those studies establish.

**Diagnostic marker:** WR codes return "explicit" or "recoverable" across all key subclaims.

### Scope Discipline

Mature writers signal the limits of their evidence as clearly as they signal its force. Academic writing does this through methodology sections and limitations paragraphs. Testimony does it through the distinction between observation and interpretation ("I saw X; I believe it means Y, but I acknowledge Z"). Policy briefs do it through confidence intervals and comparative qualification ("This approach shows promise in urban contexts; its applicability to rural settings requires further study").

**Diagnostic marker:** BP codes pass; qualifier status is "matched" throughout.

### Costly Concession

The strongest objection handling doesn't just acknowledge disagreement; it allows the disagreement to modify the argument. The claim is narrowed. The qualifier is adjusted. A subclaim is revised. The reader sees that the writer has genuinely engaged the pressure and emerged with a more precise, more honest argument. This is structurally different from costless concession, where the acknowledgment is performed but nothing changes.

**Diagnostic marker:** OB codes pass; DI codes pass; the claim ladder shows evidence of narrowing or qualifying after the concessive passage.

### Evidence-Type Diversity

Arguments that depend on a single evidence type are structurally fragile. The strongest policy briefs combine data (aggregate patterns), examples (specific cases that illustrate the mechanism), authority (expert confirmation), and experience (testimony from affected populations). When one type is challenged, the others hold the structure.

**Diagnostic marker:** SM3 does not fire; SM passes show multiple support types across subclaims.

### Audience Calibration

Effective writers build their argument for their actual audience. Hostile-audience writing features preemptive concession, narrow scope, unimpeachable evidence, and explicit warrants. Sympathetic-audience writing features identity affirmation balanced with structural rigor (not just assumed agreement). Mixed-audience writing uses layered structure: narrative for general engagement, data for expert satisfaction, political viability analysis for decision-makers.

**Diagnostic marker:** AC codes pass; false-positive guards appropriate for the identified audience.

### Testimonial Precision

The most effective testimony precisely delineates what the witness can and cannot establish. An advocate testifying about youth incarceration distinguishes between "I observed that the facility lacked mental health staff" (observational, low burden), "I believe this reflects a systemic pattern" (interpretive, needs additional support), and "This affects an estimated X youth annually" (representative, requires data beyond personal observation). The testimony is strongest when it stays within its structural authority and calls for additional evidence where its own authority ends.

**Diagnostic marker:** AT4 burden split is clean; NE codes pass; BP6 does not fire because the testimony does not overextend.

### Definitional Honesty

Strong arguments that depend on contested terms acknowledge the contest. They either define their terms explicitly at the outset, or they earn their definitions through argument. When a term's meaning shifts legitimately across the piece (because the argument has demonstrated why the shift is warranted), the text signals the shift rather than performing it silently.

**Diagnostic marker:** CL4 does not fire; key terms in Step 2 are either stable or explicitly redefined.

### Cross-Section Coherence

In long-form argument, the strongest writers maintain qualification discipline across distance. The conclusion restates the claim at the same level of confidence the evidence earned, not at a higher level that has drifted upward through 5,000 words of sustained advocacy. Key terms carry the same meaning in the conclusion as in the introduction. The scope stays constant or is explicitly expanded with additional evidence.

**Diagnostic marker:** Step 8 returns no drift, no erosion, no scope accumulation, no definition instability.

---

## Audience Calibration Framework

Five audience contexts with specific structural requirements, common calibration errors, and false-positive risks. This framework grounds the AC codes and the per-audience calibration in the audit spec.

| Context | Structural Requirement | Common Calibration Error | False-Positive Risk |
|---------|----------------------|------------------------|-------------------|
| **General audience** | Warrants must be explicit or recoverable from common knowledge. Definitions must be accessible. Scope claims must be clear. | Applying academic standards of exhaustive citation or statistical precision to a space-constrained text. | Flagging warrant gaps where the warrant is genuinely shared by the general public. |
| **Expert audience** | Maximum burden. Explicit warrants required. Primary evidence expected. Methodological transparency. Scope signaling must be precise. | Allowing emotional inflation, narrative appeals, or rhetorical shortcuts to substitute for empirical rigor. | Flagging compressed warrants that the disciplinary field genuinely shares and does not need stated. |
| **Hostile audience** | Maximum warrant explicitness. Claims must be narrowly scoped. Concessions must be costly and preemptive. Strongest objection must be addressed first. | Relying on shared values or aggressive claims that invite easy refutation. | Interpreting narrowly scoped, defensive argument as lacking ambition or stakes. |
| **Sympathetic audience** | Structure shifts from persuasion to mobilization and shared-identity affirmation. Warrants heavily implicit. Objection handling often omitted or minimal. | Assuming logical persuasion is occurring when the text is performing emotional reinforcement. | Flagging absent objection handling when the genre does not require it (fundraising appeal, internal organizing document). |
| **Mixed audience** | Requires layered, modular structure: narrative for public engagement, hard data for experts, political viability for decision-makers. | Speaking exclusively to one faction while alienating others. | Flagging structural shifts between register (narrative to data to policy) as "inconsistent tone" when it's strategic multi-audience targeting. |

---

## The Distinguish Problem

The core epistemological challenge for the Dialectical Clarity audit: how to avoid committing the very hermeneutical injustice it's designed to detect.

The v1.0 audit was calibrated toward Western analytic argumentation: thesis → evidence → objection → conclusion. Many effective arguments operate on different structural paradigms. If the audit can't distinguish between a text that fails at conventional structure and one that succeeds at unconventional structure, it risks invalidating diverse intellectual traditions.

**The solution:** The cultural charity principle + six decision tests. These test evaluability, not form. A personal essay that argues through juxtaposition and reflection passes if the claim is accessible, the evidence is evaluable, the scope is honest, and the form is doing real argumentative work. A poorly argued manifesto that hides behind "prophetic address" fails if the form blocks evaluability.

**What remains unsettled:**

1. **Strategic ambiguity vs. structural dishonesty.** When does deliberate vagueness become DI3 (ambiguity doing argumentative work)? Some political writing intentionally maintains ambiguity to build coalitions. The audit flags this as a structural failure. Is it always one?

2. **Audience adaptation vs. audience manipulation.** At what point does calibrating for audience (AC codes) become optimizing for persuasion (which the audit explicitly disclaims)? The firewall distinguishes between "built for this audience honestly" and "designed to manipulate this audience." The boundary is clear in principle and blurry in practice.

3. **Testimonial authority in contested domains.** When the experience of affected populations conflicts with institutional data, which carries more structural weight? The audit doesn't answer this; it diagnoses whether both types of evidence are present (FM-A14 catches when one is absent). But the *weighting* question remains open.

4. **Recursive and circular forms.** The Distinguish Protocol recognizes recursive argumentation, but the audit's cross-section tracking is designed for linear texts. Can Step 8 meaningfully track "drift" in a text that intentionally revisits the same ground at increasing depth? The Form-fit test is the current safeguard, but it may underserve these forms.

5. **Prophetic address and burden of proof.** Prophetic argument intentionally reverses the usual burden: it doesn't defend a position so much as demand the audience confront one. The audit's BP codes assume the arguer bears the burden. In prophetic address, the argument shifts burden to the audience. Should the audit flag this as BP3 (burden shift) or recognize it as a distinct form with its own structural logic?

These five questions are genuinely open. The audit should be transparent about them when they arise in specific manuscripts, rather than forcing a resolution the theory doesn't support.

---

*This document provides the theoretical foundation for the Dialectical Clarity v2.0 enrichment. It grounds the audit's new capabilities in established argumentation theory (Toulmin, Walton, pragma-dialectics, Perelman, Fricker) while marking where the application to editorial diagnosis is the enrichment's own extension. It catalogs 19 failure modes with theoretical grounding and detection heuristics, documents positive cases organized by structural technique rather than by genre, provides an audience calibration framework, and names the five genuinely unsettled questions where the audit must exercise judgment rather than algorithmic certainty. The audit diagnoses structure; this document explains why the structure matters.*
