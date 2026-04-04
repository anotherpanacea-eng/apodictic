# Argument Red Team — Level-Setting Research
## Nonfiction Argument Engine / APODICTIC
*Drafted: March 2026 (v1.0)*
*Status: Internal research brief for companion-module design*
*Depends on: Dialectical Clarity v2.0, Argument State Schema v0.1.1*

---

## What This Document Does

Provides the theoretical backbone for the Argument Red Team companion module. Identifies the frameworks that ground adversarial argument testing, catalogs the ways red-teaming itself fails, documents positive cases of excellent adversarial analysis across genres, calibrates the adversary model by form, and names the genuinely hard distinguish problems where adversarial analysis must remain disciplined.

This is reference material for the module, not a replacement for it. The module spec defines what to produce and how. This document explains *why* those diagnostic targets work and what intellectual traditions they draw from.

---

## Q1. Theoretical Grounding

Five frameworks ground the Red Team module. Each is marked as **DURABLE** (well-established in argumentation theory, unlikely to be overturned) or **INFERENCE** (the application to editorial adversarial testing is the module's own extension).

### 1. Walton's Critical Questions [DURABLE]

Douglas Walton's central insight is that defeasible arguments — arguments that are reasonable but not logically conclusive — each have characteristic vulnerabilities. His argumentation schemes (96 cataloged with Chris Reed and Fabrizio Macagno) each come with a set of "critical questions" that test whether the scheme's conditions are met.

**Why it matters for the Red Team:** The critical questions are the adversary's toolkit. An argument from expert opinion is defeated by asking whether the expert is credible *in the relevant domain*. An argument from consequence is defeated by asking whether the causal chain is plausible or whether the consequences have been overstated. An argument from analogy is defeated by identifying a relevant disanalogy.

The Dialectical Clarity audit uses scheme hints (Step 3) to classify support. The Red Team module reads those hints and deploys the corresponding critical questions as adversarial probes. This is why the Cross-Examination step (Step 4) can generate specific rather than generic questions: each scheme has its own attack surface.

**Key schemes and their critical questions for editorial red-teaming:**

| Scheme | Critical Question (adversary version) | Module application |
|--------|--------------------------------------|-------------------|
| Expert opinion | "Is the authority cited actually an expert on *this specific question*?" | RT9 (Evidence Chain Snap), RT11 (Standing/Scope Exposure) |
| Practical reasoning | "Are there side effects the author hasn't acknowledged?" | RT7 (Alternative Suppression), RT8 (Implementation Vacuum) |
| Consequence | "Is the causal chain from action to claimed outcome actually reliable?" | RT3 (Burden Inversion), RT11 (Standing/Scope Exposure) |
| Analogy | "What's the relevant difference between the case cited and the case being argued?" | RT4 (Exception Collapse), RT1 (Easy Steelman Against) |
| Sign | "Could this sign indicate something other than what the author claims?" | RT7 (Alternative Suppression) |
| Testimony | "Is the witness in a position to know what they claim to know?" | RT11 (Standing/Scope Exposure), RT3 (Burden Inversion) |

**Design constraint [INFERENCE]:** The module does not import Walton's full taxonomy as a checklist. The reviewer does not classify schemes. The module uses scheme hints from the Argument State to select relevant critical questions, then deploys them as adversarial probes. The theory is invisible in the output; only the resulting attacks are visible.

### 2. Pragma-Dialectics and Strategic Maneuvering [DURABLE]

Van Eemeren and Houtlosser's extension of pragma-dialectics adds the concept of "strategic maneuvering" — the ways arguers simultaneously pursue rhetorical effectiveness and dialectical reasonableness. An arguer maneuvers strategically by choosing which topics to discuss (topical selection), how to frame them (audience demand adaptation), and what language to use (presentational devices).

**Why it matters for the Red Team:** Strategic maneuvering is what a skilled adversary *does*. The adversary doesn't just raise objections; they choose which objections to raise (topical selection), frame them for the target audience (adaptation), and present them in the most damaging way (presentational devices). The Red Team module models this behavior.

More importantly, pragma-dialectics identifies when strategic maneuvering "derails" — when the pursuit of effectiveness overwhelms reasonableness, producing a fallacy. The module must distinguish between the adversary's legitimate strategic choices (highlighting the most damaging vulnerability) and illegitimate ones (misrepresenting the manuscript's position). This distinction is what separates red-teaming from bad-faith attack.

**Implementation:** The Countercase Construction step (Step 1) is the module's primary strategic-maneuvering output. The adversary's "best case" is the result of topical selection (choosing the most damaging angle), audience adaptation (framing it for the manuscript's target audience), and presentational optimization (stating it in the most persuasive way). The Distinguish Framework's "Intentional Risk" category catches cases where the module's own maneuvering has targeted a choice the author made knowingly.

**Key insight [INFERENCE]:** The manuscript itself is engaged in strategic maneuvering. The Red Team's job is to test whether the author's maneuvering is successful — whether their topical selections, audience adaptations, and presentational choices hold up under adversarial pressure. An author who strategically avoids a topic may be exercising good judgment (if the topic is irrelevant) or dodging a vulnerability (if it's the central objection). The module must distinguish these.

### 3. Mill's Argument from On Liberty Chapter 2 [DURABLE]

John Stuart Mill's defense of free expression in *On Liberty* (1859) provides the deepest philosophical argument for adversarial testing. Mill identifies four reasons why even true opinions must be challenged:

1. **The opinion may be wrong.** Suppressing challenge assumes infallibility.
2. **The opinion may be partially true.** Only through collision with opposing views does the whole truth emerge.
3. **Even if wholly true, an unchallenged opinion becomes "dead dogma."** It loses its meaning and force when it is never tested.
4. **The meaning of the doctrine itself degrades without challenge.** Terms lose their precision, arguments lose their structure, and the holder cannot explain why they believe what they believe.

**Why it matters for the Red Team:** Mill's fourth point is the most directly relevant. An argument that has never faced a prepared adversary suffers from meaning degradation — its terms become loose, its warrants become invisible (because they've never needed to be stated), and its scope becomes inflated (because no one has pushed back). The Red Team module is an operational implementation of Mill's thesis: it challenges the argument not because it might be wrong, but because unchallenged arguments become structurally lazy.

**Implementation:** The Burden and Definitional Pressure step (Step 3) is the most Millian component. RT5 (Definition Front Open) identifies where terms have degraded through lack of challenge — where "equity" means three things because no adversary has ever forced the author to choose one, where "reform" carries a concealed value judgment because it has never been questioned, where a key term is untethered because the author has never had to operationally define it.

**Key insight [INFERENCE]:** Mill's argument implies that the Red Team module should be most aggressive with arguments the reviewer *agrees with*. An argument the reviewer finds compelling is precisely the one most likely to contain unchallenged assumptions, inflated scope, and degraded definitions — because the reviewer's agreement has shielded it from the adversarial pressure it needs. The module's operational constraint ("does not judge correctness") is a Millian discipline: it applies adversarial pressure regardless of whether the argument is "right."

### 4. Adversarial Collaboration and Steelmanning [DURABLE framework, INFERENCE application]

Adversarial collaboration — formalized by Daniel Kahneman and first applied in his collaborations with Gary Klein — is a methodology for resolving disagreements by requiring each party to state the other's position in its strongest form before attacking it. The steelmanning requirement (as opposed to strawmanning) ensures that adversarial testing targets the argument's actual strengths, not a weakened caricature.

**Why it matters for the Red Team:** The module's adversary must be a steelmanner. The Countercase Construction step (Step 1) constructs the adversary's best case, but it must also accurately represent the manuscript's position. An adversary who misrepresents the manuscript is engaging in strawmanning, not red-teaming. The Distinguish Framework's "Genuinely Vulnerable" classification requires that the adversary has correctly identified the manuscript's actual claim before attacking it.

**Practical test:** For each vulnerability identified, the module should be able to state the manuscript's position accurately enough that the author would say "yes, that's what I'm arguing." If the adversary is attacking a position the author doesn't hold, the vulnerability is spurious.

**Key insight [INFERENCE]:** Adversarial collaboration research shows that the most productive disagreements occur when both parties agree on what they disagree about. The Red Team module's value depends on this: it must correctly identify the manuscript's commitments before testing whether those commitments are defensible. The Distinguish Framework's Structural Test exists specifically to catch cases where the module's own adversary model has the wrong target.

### 5. Institutional Adversarial Reading Traditions [DURABLE]

Several institutional traditions have formalized adversarial argument testing:

**Legal cross-examination.** The adversarial legal system is built on the premise that truth emerges from structured opposition. Cross-examination follows specific rules: questions must be specific and answerable, the examiner has a theory of the case, and the goal is to expose weakness in testimony, not to harass the witness. The "leading question" is the core tool: it forces a yes-or-no answer that the examiner already knows the implications of.

**Academic peer review.** Reviewer 2 is the academy's adversarial mechanism. The best peer reviews identify the strongest objection, test the evidence against the claims, check methodological warrant, and ask whether the contribution is novel given the existing literature. The worst peer reviews substitute personal taste for structural analysis.

**Intelligence red-teaming.** After the Iraq WMD failure, the intelligence community formalized "Red Team" and "Team B" exercises: groups explicitly tasked with arguing the opposing case to prevent groupthink and confirmation bias. The key lesson: red teams are most valuable when they have access to the same intelligence but are freed from the institutional incentive to reach the same conclusion.

**Devil's advocacy in deliberative bodies.** From the Catholic Church's *advocatus diaboli* (abolished in 1983 by John Paul II, leading to a dramatic increase in canonizations — a natural experiment in what happens when you remove the adversary) to parliamentary opposition, institutional adversarial roles serve a structural function that exceeds any individual's contribution.

**Why it matters for the Red Team:** These traditions demonstrate that adversarial testing is most effective when it is:
- Structured (not free-form hostility)
- Competent (the adversary understands the domain)
- Good-faith (the adversary is testing the argument, not the arguer)
- Answerable (the author can respond to what the adversary raises)
- Calibrated to the stakes (high-consequence arguments get more adversarial pressure)

The module inherits all five constraints.

---

## Q2. Failure Taxonomy — How Red-Teaming Itself Fails

The module must avoid its own characteristic failure modes. Seven named failure patterns:

### RT-F1: The Softball Red Team

The adversary raises objections the author can easily answer. The Red Team confirms the argument's strength by testing it against weak opposition. This typically happens when the module models an uninformed or lazy adversary instead of the best version of the real opposition.

**Detection:** Every vulnerability identified is Cosmetic or Manageable. No cross-exam question has expected difficulty "author would struggle." The countercase is weaker than the author's own framing.

**Root cause:** The adversary profile is miscalibrated — too sympathetic, too unfamiliar with the domain, or too generic.

### RT-F2: The Hostile Takedown

The adversary attacks everything with maximum severity. Every vulnerability is FATAL. The memo reads as an argument against the manuscript rather than a diagnostic of its weaknesses. The author receives no actionable information because everything is equally urgent.

**Detection:** More than 50% of vulnerabilities are FATAL. No vulnerability is classified as COSMETIC. The module spends more energy on the adversary's case than on the manuscript's structural profile.

**Root cause:** The module has abandoned the adversary model and become an advocate for the opposing position. The Distinguish Framework has been skipped or applied perfunctorily.

### RT-F3: The Generic Objection List

The Red Team produces objections that any argument on any topic would face. "Have you considered the counterarguments?" "What about unintended consequences?" "Is your evidence representative?" These are placeholders, not adversarial analysis.

**Detection:** The objections could be applied to a manuscript on a completely different topic without modification. No objection references a specific claim, warrant, or evidence unit from the Argument State. Cross-exam questions are interrogative rather than leading.

**Root cause:** The module is not reading the Argument State. It is generating adversarial content from generic templates rather than from the manuscript's actual structural profile.

### RT-F4: The Scope Mismatch

The Red Team tests the argument against a different audience or context than the one the manuscript targets. An academic article is red-teamed as if it were an op-ed. Testimony is red-teamed as if it were a policy brief. The vulnerabilities identified are real for the wrong audience.

**Detection:** The adversary profile doesn't match § 1 (Context) in the Argument State. Vulnerabilities are classified as Context-Dependent but treated as if they were universal.

**Root cause:** The adversary profile was constructed without reading § 1, or the module defaulted to a generic adversary instead of a form-calibrated one.

### RT-F5: The Strawman Attack

The adversary misrepresents the manuscript's position and attacks the misrepresentation. The vulnerabilities identified are real for an argument the author isn't making.

**Detection:** Objections target claims or warrants that don't appear in §§ 2–4 of the Argument State. The countercase doesn't accurately describe what the manuscript argues.

**Root cause:** The module has constructed its own version of the argument rather than reading the one in the State. This is the adversarial equivalent of the Dialectical Clarity audit inventing claims the text doesn't contain.

### RT-F6: The False-Balance Trap

The Red Team treats every argument as if it has an equally valid opposing case. A well-supported empirical claim gets the same adversarial pressure as a speculative assertion. The module refuses to say "this argument is strong" because that would feel un-adversarial.

**Detection:** Strong support chains (SM passes in Argument State) receive the same vulnerability coding as weak ones. The module assigns MAJOR or FATAL to subclaims that pass every Dialectical Clarity check.

**Root cause:** The module has confused adversarial testing with adversarial conviction. The Red Team's job is to test defensibility, not to prove the argument wrong. If the argument is strong, the Red Team should say so.

### RT-F7: The Cascading Inflation

A single minor vulnerability generates a chain of increasingly severe codes: the definitional ambiguity becomes a burden shift, the burden shift becomes an alternate framing, the alternate framing becomes a FATAL vulnerability. Each step is individually plausible, but the cascade inflates a COSMETIC issue into a FATAL one.

**Detection:** A FATAL vulnerability can be traced back through the code chain to a COSMETIC origin. Removing the first code in the chain eliminates every subsequent one.

**Root cause:** The module is ranking cascades rather than testing each step independently. Cascade effects are real, but each link must be independently validated.

### Structural Isomorphism Principle

The most dangerous red-team failures are usually not "new objections" but **pressure-activated versions of weaknesses already present in the argument graph**. A fragile shared premise (already visible in the Argument State) becomes RT2 under adversarial pressure. An unaddressed alternative (already visible in § 5) becomes RT7. The Red Team's value is not inventing new problems but showing how known structural features become exploitable under hostile conditions.

This means the failure taxonomy above (RT-F1 through RT-F7) and the vulnerability codes in the module are not independent systems. RT-F3 (Generic Objection List) is what happens when the module ignores structural isomorphism and invents attacks that don't map to the argument graph. RT-F5 (Strawman Attack) is what happens when the module attacks a structure the argument doesn't have.

---

## Q3. Positive Cases — What Excellent Adversarial Analysis Looks Like

### Legal cross-examination at its best

The most effective cross-examinations don't surprise the witness — they confront the witness with implications of their own testimony. The examiner uses the witness's own words from direct examination and earlier deposition to create contradictions or expose scope overreach. The questions are specific, answerable, and build toward a conclusion the witness can see coming but cannot avoid.

**What the module extracts:** Cross-exam questions (Step 4) should mirror this structure. They reference specific claims and evidence from the Argument State and build toward an adversarial conclusion using the manuscript's own commitments. "You stated in section 3 that X. You stated in section 7 that Y. How are these consistent?" is a cross-examination question. "Have you considered the other side?" is not.

### Academic peer review at its best

The best peer reviews identify the paper's strongest contribution and then test whether the evidence and methodology can support it. They distinguish between the paper's ambition (what it's trying to show) and its achievement (what it actually demonstrates). They identify the one or two genuinely damaging weaknesses — not a laundry list of minor complaints — and explain why those weaknesses matter for the specific contribution the paper claims to make.

**What the module extracts:** The Vulnerability Ranking should mirror this discipline. Identify the manuscript's strongest claim, test whether the support structure can bear it, and rank by exploitability rather than by number of codes fired. A memo with two FATAL vulnerabilities and an honest severity ranking is more useful than one with fifteen MAJOR flags.

### Policy devil's advocacy at its best

The best policy adversaries accept the problem and attack the solution. They don't argue that juvenile recidivism doesn't matter — they argue that this specific intervention won't reduce it, or that a different intervention would be more cost-effective, or that the implementation plan has a fatal gap. The adversary shares the author's values but disputes the means.

**What the module extracts:** The adversary profile for policy work should model a competent opponent who shares the problem definition but disputes the solution. RT7 (Alternative Suppression) and RT8 (Implementation Vacuum) are most valuable here: the adversary raises the competing proposal, the partial alternative, or the status-quo defense — not because they don't care about the problem, but because they think a different response is better.

### Hostile editorial reads at their best

The best hostile reads identify the piece's single most quotable vulnerability — the sentence an opponent will extract, the claim that doesn't survive its own evidence, the framing that backfires with the wrong audience. They ask: "If someone who disagrees with you reads this, what will they use against you?"

**What the module extracts:** The Countercase Construction step should identify what the adversary will *do* with the manuscript, not just what they'll say about it. Which sentences will be quoted? Which claims will be reframed? Which concessions will be weaponized? This is adversarial analysis at the level of practical consequence, not abstract logic.

### Cross-form success signals

What adversarial resilience looks like regardless of genre:

1. The strongest hostile question can be named without panic
2. The manuscript already knows where its narrowest defensible point sits
3. Definitions do not broaden opportunistically under pressure
4. Concession changes the shape of the case rather than decorating it
5. The author can lose a peripheral point without losing the whole argument

These signals are diagnostic: if the manuscript displays them, the Red Team memo should say the argument is strong. If it lacks them, the vulnerability ranking should reflect that.

---

## Q4. Mode Calibration — How the Adversary Changes by Form

### Testimony

The adversary is preparing for real-time questioning under formal rules. Testimony adversaries don't write response essays — they write questions designed to force concessions, expose scope overreach, and undermine witness credibility. The most dangerous questions are the ones that force the witness to choose between contradicting their written testimony and saying something that undermines their conclusion.

**What tightens:** Cross-exam questions (Step 4) must be realistic for cross-examination format — specific, answerable, building toward a point. RT3 (Burden Inversion) and RT11 (Standing/Scope Exposure) matter most here: witnesses who exceed their observational warrant (AT4 representative burden) are vulnerable to devastating cross-examination.

**What loosens:** Formal objection handling is less important. Testimony is not expected to address every counterargument — it's expected to survive cross-examination on the claims it does make.

### Policy brief

The adversary is a rival analyst who accepts the problem but disputes the proposed solution. Policy adversaries focus on alternatives (RT7), cost-benefit (RT3 on burden), and implementation gaps (RT8). They assume shared institutional language and don't attack definitions.

**What tightens:** Missing alternatives are critical. A policy brief that doesn't compare its proposal to the status quo and at least one competing proposal has a Fatal RT7.

**What loosens:** Definitional precision (RT5) is less important because policy briefs operate in shared terminology. Bold framing is expected.

### Op-ed

The adversary is an opposition columnist who will quote selectively and reframe uncharitably. Op-ed adversaries don't test logical rigor — they test whether the piece can survive being taken out of context.

**What tightens:** Countercase strength (RT1) and extractability (RT6). The adversary looks for the sentence that, quoted alone, makes the author sound unreasonable.

**What loosens:** Qualification discipline and evidence provenance. Op-eds are allowed rhetorical compression.

### Academic article

The adversary is a domain-competent peer reviewer. Academic adversaries test methodology, warrant integrity, evidence provenance, and whether the contribution is genuinely novel.

**What tightens:** Warrant integrity (RT10 targeting § 4) and evidence provenance (RT9). "Where does this number come from?" and "Why does this evidence support this conclusion and not that one?" are the standard attacks.

**What loosens:** Rhetorical force and emotional resonance. Academic prose is expected to be measured.

### Advocacy journalism

The adversary is a fact-checker, hostile editor, or opposing advocacy group. Advocacy adversaries challenge representativeness ("is this case typical?"), sourcing ("where does this come from?"), and framing fairness ("would the subjects describe themselves this way?").

**What tightens:** Evidence provenance and representativeness. Testimony overextension (AT4 representative burden) is common in advocacy journalism that generalizes from individual cases.

**What loosens:** Normative stance. The piece has a position and is expected to.

### Open letter

The adversary is the addressee and their allies. Open-letter adversaries look for misrepresentations of their position, unreasonable demands, and exploitable concessions.

**What tightens:** Accuracy of the addressee's position (RT2 — if you get the opponent's view wrong in an open letter, you've lost). Burden placement (RT3 — demanding impossible proof).

**What loosens:** Emotional register and scope. Open letters are urgent and focused.

### False-positive risks by form

The module must guard against form-inappropriate vulnerability flags:

| Form | False Positive Risk |
|------|-------------------|
| **Testimony** | Treating emotionally charged witness language as evasive when it is in fact observationally precise |
| **Policy brief** | Mistaking necessary brevity for irresponsibility when the brief actually links to fuller support elsewhere |
| **Op-ed** | Expecting full scholarly burden in 800–1,200 words |
| **Academic article** | Flagging genuinely field-shared warrants as under-explained |
| **Advocacy journalism** | Treating clear moral positioning itself as bias instead of testing whether the support chain remains auditable |
| **Open letter** | Mistaking strategic plainness for conceptual shallowness |

These false positives are the Red Team's own failure modes, not the manuscript's. The module should self-check against this table before finalizing severity ratings.

---

## Q5. The Distinguish Problem

The hardest problem in adversarial argument testing is distinguishing genuine vulnerability from three things that look like it:

### 1. Vulnerability vs. Unexploited Defense

Some manuscripts contain the resources to answer an objection but haven't deployed them. The evidence is in section 5; the claim it would support is in section 2; but the connection is never drawn. This is not a genuine vulnerability — it's an organizational failure. The adversary could raise the objection, but the author could answer it by repositioning existing material.

**Distinguish test [INFERENCE]:** For each vulnerability, check whether the Argument State contains support, warrant, or evidence that could address the objection if surfaced. If yes, classify as Unexploited Defense. The editorial implication is different: Genuinely Vulnerable means "you need new material or a narrower claim." Unexploited Defense means "the answer is already in your manuscript — you just haven't connected it."

### 2. Vulnerability vs. Context-Dependent Exposure

A vulnerability that's fatal for a hostile legislative committee may be cosmetic for an academic journal's readership. The same argument structure is defensible in one context and indefensible in another — not because the argument changes, but because the adversary's leverage changes.

**Distinguish test [DURABLE — follows from Perelman/Olbrechts-Tyteca's audience theory]:** For each vulnerability, test whether the attack is effective against the manuscript's target audience (from § 1), not just against any possible audience. If the attack works only for a different audience, classify as Context-Dependent and name both audiences.

**Practical implication:** An author who faces multiple audiences may need to address context-dependent vulnerabilities that a single-audience author can safely ignore. The module notes the dependency but doesn't prescribe the decision.

### 3. Vulnerability vs. Intentional Risk

Bold claims, normative commitments, and rhetorical choices that create exposure may be intentional. An author who opens with "the juvenile justice system is broken" knows they're taking on a burden. An author who refuses to qualify their central claim knows they're creating scope vulnerability. These are strategic choices, not failures.

**Distinguish test [INFERENCE]:** Check whether the manuscript signals awareness of the risk. Indicators: explicit scope limitations elsewhere, acknowledged tradeoffs, rhetorical framing that shows the author knows they're being bold. If the author appears aware of the risk, classify as Intentional Risk and note it. If the author appears unaware — if the boldness reads as carelessness rather than conviction — classify as Genuinely Vulnerable.

**The hardest case:** When the author intends the risk but underestimates its severity. The module should note this: "Classified as Intentional Risk (author signals awareness), but severity may be higher than author expects. This claim is defensible in a sympathetic context but creates a FATAL vulnerability in the hostile context the manuscript is targeting."

### 4. Genuine Vulnerability (the real thing)

After applying the three distinguish tests, what remains is genuine vulnerability: the manuscript's argument has a structural weakness that an informed adversary can exploit, that the manuscript cannot currently answer, that is relevant to the target audience, and that the author does not appear to have chosen deliberately.

This is the Red Team's core deliverable: vulnerability that the author needs to know about and can act on.

---

## Unsettled Questions

Three genuinely hard problems the module must acknowledge rather than solve:

### 1. How aggressive should the adversary be?

The module calibrates by consequence context (from § 1), but the threshold is inherently judgmental. A policy brief recommending a modest budget increase and a policy brief recommending systemic reform both have "high" consequence context, but they warrant very different adversarial intensity. The module should err toward the stronger adversary (per Mill: the argument benefits from the strongest challenge), but there's no formula for exactly how strong.

### 2. When does a cascade of minor vulnerabilities become a major one?

Three MANAGEABLE vulnerabilities in the same subclaim may collectively constitute a MAJOR vulnerability. Five COSMETIC definitional ambiguities may collectively enable a FATAL equivocation attack. The module must use judgment about when accumulation changes severity — and it should show its work when it makes this call.

### 3. Can an adversary legitimately use the manuscript's form against it?

If an op-ed uses rhetorical compression that's standard for the form, can the adversary legitimately attack the compression? The module's genre calibration says "loosen on qualification discipline for op-eds," but a skilled adversary will attack the compression anyway. The module should model what the adversary *will* do (attack the compression) while noting that the attack exploits a genre convention rather than a structural failure. This is the boundary between the Red Team and the Distinguish Framework: the Red Team identifies the attack; the Distinguish Framework classifies whether it represents genuine vulnerability.

---

*This research brief grounds the Argument Red Team module in five theoretical traditions (Walton, pragma-dialectics, Mill, adversarial collaboration, institutional adversarial reading), names seven failure modes of red-teaming itself, documents positive cases across four institutional traditions, calibrates the adversary by six forms, and identifies three genuinely unsettled questions. The module's value depends on discipline: adversarial pressure calibrated to the argument's actual structure, not generic hostility or false balance.*
