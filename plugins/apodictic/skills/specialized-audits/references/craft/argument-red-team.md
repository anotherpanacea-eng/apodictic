# Companion Module: Argument Red Team
## Nonfiction Argument Engine / APODICTIC
*Version: 1.0 (reconstructed March 2026)*
*Status: Companion module for Dialectical Clarity v2.0*
*Consumes: `Argument_State.md` §§ 1–9*
*Produces: `Red_Team_Memo.md` + `Argument_State.md` § 10.4 annotations*

---

## §1. Purpose

This module produces the strongest possible case against the manuscript's argument — the specific, informed hostile read that a prepared adversary would deliver. Not generic negativity. Not a list of things the reviewer disagrees with. The objections a congressional staffer would write on a sticky note during testimony, the questions a peer reviewer would circle in red, the reframing a political opponent would use in a response op-ed.

**Core problem:** An argument can be structurally sound by every Dialectical Clarity metric and still be practically indefensible. The core audit diagnoses whether the argument holds together. This module diagnoses whether it survives contact with someone smart trying to break it.

### Structural isomorphism principle

The most dangerous red-team findings are usually not "new objections" but **pressure-activated versions of weaknesses already present in the argument graph**. A fragile shared premise (already visible in § 5) becomes RT2 under adversarial pressure. An unaddressed alternative (already visible in § 5) becomes RT7. The module's value is showing how known structural features become exploitable under hostile conditions, not inventing problems the argument doesn't have.

### Relationship to adjacent modules

| Module | What it asks | Red Team's relationship |
|--------|-------------|------------------------|
| **Dialectical Clarity v2.0** | Is the argument structurally sound? | Red Team takes DC's diagnosis as input and asks what a skilled adversary would do with the structural profile |
| **§ 6 (Objection Handling)** | Does the manuscript engage its strongest 2–4 objections? | Red Team generates the full objection set, produces the adversary's best framing, and ranks vulnerabilities |
| **Banister** | Does the manuscript give disagreement fair hearing? | Red Team is the source of what that disagreement actually looks like. Run Banister after Red Team. |
| **Reception Risk** | How will the argument land in contested cultural/political territory? | Red Team models an informed good-faith adversary. When a vulnerability is both argumentatively weak and culturally exposed, flag for both. |

---

## §2. Firewall

This module produces adversarial analysis, not argument content.

**Allowed:** Build the strongest opposing case. Surface missing alternatives, fragile premises, cross-exam traps. Rank vulnerabilities. Produce hostile-reader questions and an opposition memo. Annotate `Argument_State.md`.

**Not allowed:** Suggest what the author should argue instead. Write or rewrite argument sections. Supply counterarguments the manuscript "should" include. Recommend concession strategies (Persuasion module's territory). Generate the author's defense. Evaluate whether the argument is *correct* — only whether it is *defensible*. Fabricate adversarial positions no informed reader would hold.

**In practice:**

- ❌ "You should add a paragraph addressing the cost objection."
- ✅ "An informed adversary's first move is the cost objection. The manuscript does not engage it. RT7 — Fatal for AT3 with hostile audience."
- ❌ "Define 'equity' more precisely in paragraph 4."
- ✅ "'Equity' carries three distinct meanings across the draft. An adversary would exploit this: 'Which equity does the author mean?' RT5 — Major."

---

## §3. Named Vulnerability Flags (RT1–RT12)

Twelve named flags. These are the module's primary output vocabulary — what the Red Team finds when it pressure-tests the argument.

**Severity scale:**

| Tier | Meaning | Editorial implication |
|------|---------|----------------------|
| **Fatal** | A prepared adversary can use this to defeat the argument entirely | Must-Fix before further work |
| **Major** | Seriously weakens credibility, scope, or decision-usefulness, but core claim may survive | Should-Fix |
| **Manageable** | Real vulnerability, limited blast radius; author could concede without losing the case | Could-Fix in high-consequence contexts |
| **Cosmetic** | Detectable but not worth an adversary's time | Note only. Do not inflate. |

**Flag table:**

| Code | Name | What the adversary does | Default Severity |
|------|------|------------------------|-----------------|
| **RT1** | Easy Steelman Against | Builds a stronger rival case from the manuscript's own omissions | Major |
| **RT2** | Shared Premise Fragility | Rejects one starting-point premise and disables a large section of the argument | Major |
| **RT3** | Burden Inversion | Forces the manuscript to defend a premise it quietly shifted onto others | Major |
| **RT4** | Exception Collapse | Names one serious exception or edge case that destabilizes the advertised scope | Major |
| **RT5** | Definition Front Open | Attacks a key term's ambiguity — the manuscript needs the ambiguity to sound stronger than any precise version | Major |
| **RT6** | Quote-Mine Exposure | Extracts a sentence whose compression or ambiguity makes it unusually easy to weaponize or misread | Manageable |
| **RT7** | Alternative Suppression | Points out the preferred course looks strong only because rivals are absent | Fatal for AT3; Major otherwise |
| **RT8** | Implementation Vacuum | Asks "how would this actually work?" and the manuscript has no answer | Fatal for consequential AT3 |
| **RT9** | Evidence Chain Snap | Presses one level deeper on provenance or interpretation and a critical support node weakens sharply | Major |
| **RT10** | Cross-Exam Trapdoor | Asks a short sequence of questions that forces retreat, contradiction, or overclaim | Major |
| **RT11** | Standing and Scope Exposure | Shows the manuscript speaks beyond the authority or reach of its evidence position | Major |
| **RT12** | Clustered Weakness Corridor | Exploits multiple medium weaknesses converging on the same claim path — jointly dangerous | Fatal or Major depending on clustering |

---

## §4. Prerequisites and Adversary Construction

### Required input

Read `Argument_State.md` §§ 1–9, populated by Dialectical Clarity v2.0. Do not re-derive claim structure. If the state is empty or incomplete, refuse to run.

### What the module reads

| State Section | What Red Team uses it for |
|---------------|--------------------------|
| § 1 (Context) | Argument type, audience posture, consequence context → determines adversary profile |
| § 2 (Claims) | C0 and subclaim ladder → attack targets |
| § 3 (Support) | Support types and scheme hints → identifies attackable evidence |
| § 4 (Warrants) | Warrant status and backing → identifies inferential gaps to exploit |
| § 5 (Burden/Scope) | Scope match, alternatives considered, precision → identifies overreach |
| § 6 (Objections) | Existing objection inventory → starting point, not ceiling |
| § 7 (Narrative) | Vignette functions and witness positions → identifies testimony overextension |
| § 8 (Cross-Section) | Dynamic failures, qualification drift → identifies inconsistency attacks |
| § 9 (Summary) | Pattern matches and severity → identifies highest-leverage attack points |

### Adversary profile construction

Build a single adversary calibrated to the argument's context:

- **Audience from § 1** determines who the adversary is. A policy brief aimed at a hostile committee gets a staffer-adversary. An academic article gets a peer-reviewer-adversary. An op-ed gets an opposition-columnist-adversary.
- **Consequence context from § 1** determines intensity. High-consequence arguments get more aggressive pressure.
- **Argument type from § 1** determines attack surface. AT3 arguments are vulnerable to alternatives and burden attacks. AT4 arguments are vulnerable to representative-burden attacks. AT1 arguments have a narrow surface (accuracy and completeness).

Do not invent a cartoon villain. The adversary is informed, competent, and argues in good faith. Bad-faith attacks belong in Reception Risk.

---

## §5. Diagnostic Procedure

Six steps. The module reads the Argument State once, constructs the adversary profile, then runs each step against the manuscript using the state as its structural map.

### Step 1: Countercase Construction

Build the adversary's best case — the strongest version of the opposing position, stated as a skilled adversary would state it.

Using §§ 2–5, construct the best alternative case from:
1. rival premises
2. rival explanations
3. rival policies or proposals
4. a narrower reading of the same evidence

This is the center of the memo. If the countercase is weak, say so — that's a finding too.

**Fires:** RT1 (Easy Steelman Against), RT7 (Alternative Suppression)

### Step 2: Objection Extraction

Expand § 6 of the Argument State. The core audit identifies 2–4 strongest objections. Red Team produces the comprehensive set — everything a prepared adversary would bring.

For each objection, identify:
- target (which claim, warrant, or evidence unit)
- adversary basis (what a hostile reader would cite)
- manuscript engagement (ADDRESSED / PARTIALLY / ABSENT)
- if addressed: quality from § 6 (SUBSTANTIVE / STRAWMAN / EVASION / COSMETIC)

**Fires:** RT2 (Shared Premise Fragility), RT4 (Exception Collapse), RT9 (Evidence Chain Snap)

### Step 3: Burden and Definitional Pressure

Test where the argument misplaces the burden of proof and where key terms do hidden argumentative work.

**Burden pressure** — read from § 5:
- Where does the manuscript assume a burden it hasn't earned?
- Where does it dodge a burden it should carry?
- Where does it demand opponents disprove the claim rather than proving it?

**Definitional pressure** — read from § 2 (Key Terms) and § 8 (Cross-Section):
- Where do key terms carry incompatible meanings across the manuscript?
- Where does a term's ambiguity do argumentative work the author hasn't acknowledged?
- Where would hostile paraphrase expose that ambiguity?

**Fires:** RT3 (Burden Inversion), RT5 (Definition Front Open), RT11 (Standing and Scope Exposure)

### Step 4: Cross-Examination Questions

Generate 5–10 questions a hostile but competent interlocutor would ask. Not generic prompts — specific to this manuscript's claims, evidence, and structural profile.

Each question must:
- target a specific claim, warrant, or evidence unit (cite the State reference)
- be answerable (not rhetorical aggression)
- exploit a real structural gap identified in the State
- be calibrated to the adversary profile

Questions should escalate logically: start with the adversary's strongest opening, build toward the point where the manuscript would struggle most.

Rate expected difficulty: *author would struggle* / *could answer but hasn't* / *should answer easily*

**Fires:** RT10 (Cross-Exam Trapdoor), RT6 (Quote-Mine Exposure)

### Step 5: Vulnerability Ranking

Rank all identified vulnerabilities by severity. This is the module's primary deliverable.

For each vulnerability, record:
1. RT code and name
2. severity tier (Fatal / Major / Manageable / Cosmetic)
3. blast radius (which claim paths are affected)
4. Distinguish classification (see §6)
5. forum relevance (is this audience-relative?)

**Ranking principles:**

1. **Rank by exploitability, not logical severity.** A technically significant gap that no real adversary would notice is less dangerous than a minor inconsistency a skilled opponent can make devastating.
2. **Audience-relative ranking.** A vulnerability that's fatal for a hostile audience may be cosmetic for a sympathetic one. Note the dependency.
3. **Cascade effects.** RT5 (definition front) enabling RT3 (burden inversion) enabling RT1 (easy steelman against) is more dangerous than any component alone. Rank the cascade.
4. **Don't inflate.** If the argument is strong, say so. A memo that flags everything as Fatal is as useless as one that flags nothing.

**Fires:** RT12 (Clustered Weakness Corridor) — when multiple medium vulnerabilities converge on the same claim path

### Step 6: Annotate State and Write Memo

Write findings to:
1. `Argument_State.md` § 10.4
2. `Red_Team_Memo.md` (standalone artifact)

See §9 for output formats.

---

## §6. Distinguish Framework

Every vulnerability must be classified, not just identified. The Red Team's value depends on this: an unclassified vulnerability list is noise; a classified one is actionable.

### Four classes

| Class | What it means | Editorial implication |
|-------|-------------|---------------------|
| **Genuinely Vulnerable** | The adversary exploits a real structural weakness. The manuscript is weaker than it appears on this point. | Author must address — strengthen support, narrow scope, add engagement, or concede. |
| **Unexploited Defense** | The manuscript has resources to answer this objection but hasn't deployed them. The defense exists in the evidence or logic but isn't surfaced. | Often the cheapest fix — the answer is already in the manuscript, just not in the right place. |
| **Context-Dependent** | The vulnerability is real for one audience but not another. A hostile committee would exploit this; an academic reviewer wouldn't (or vice versa). | Author decides based on primary audience. Note the dependency. |
| **Intentional Risk** | The author is knowingly making a choice that creates vulnerability — a bold claim, an omitted qualification, a normative stake. The "weakness" is the argument's bet. | Note the risk; do not treat as failure. Flag if the author appears *unaware* of the risk. |

### Five distinguish tests

Apply before assigning a classification:

1. **Structural test:** Does the vulnerability correspond to a real gap in the Argument State (missing warrant, unsupported subclaim, scope mismatch)? If not, it may be adversarial noise.
2. **Adversary competence test:** Would a prepared, informed adversary actually make this attack? Generic objections no real opponent would bother with are Cosmetic at most.
3. **Defense availability test:** Does the manuscript contain material that could answer this objection if repositioned? If yes → Unexploited Defense.
4. **Audience relativity test:** Is this exploitable by the manuscript's actual target audience, or only by a different audience? If audience-relative → Context-Dependent, and specify both audiences.
5. **Authorial intent test:** Does the manuscript signal awareness of the risk? Bold claims, explicit scope limitations, acknowledged tradeoffs suggest intentional risk-taking.

---

## §7. Genre Calibration

### Adversary profiles by form

| Form | Adversary | What they want | Fatal threshold |
|------|-----------|---------------|----------------|
| **Testimony** | Hostile committee staffer or opposing counsel. Has read the full record. | Undermine credibility, limit impact, expose scope overreach | RT10 unanswerable on central claim; RT11 testimony beyond observational warrant |
| **Policy brief** | Rival analyst who accepts the problem but disputes the solution | Show the alternative is better, the cost is higher, the implementation is implausible | RT7 missing competing proposal; RT8 no implementation answer |
| **Op-ed** | Opposition columnist who will quote selectively and reframe uncharitably | Extract the most attackable sentence, reframe the whole piece | RT1 opposing frame stronger; RT6 extractable sentence |
| **Academic article** | Reviewer 2. Domain-competent, skeptical by training | Find methodological, evidential, or inferential gaps | RT9 evidence chain snap on primary data; RT10 warrant gap on central claim |
| **Advocacy journalism** | Fact-checker, hostile editor, or opposing advocacy group | Challenge representativeness, sourcing, framing fairness | RT9 evidence laundering; RT11 testimony overextension |
| **Open letter** | The addressee and their allies | Find misrepresentation, overreach, exploitable concessions | RT2 misrepresentation of addressee's position (fatal); RT3 demanding impossible proof |

### Calibration adjustments

| Form | Tighten on | Loosen on | Signature flags |
|------|-----------|----------|-----------------|
| Testimony | standing, scope, cross-exam readiness, witness-vs-interpretation boundary | formal objection handling, full literature review | RT10, RT11 |
| Policy brief | alternatives, implementation, decision burden | exhaustive moral framing, definitional precision | RT7, RT8 |
| Op-ed | compression, quote-mine exposure, easy steelman against | full scholarly apparatus, qualification discipline | RT1, RT6 |
| Academic article | definitional precision, evidence-chain snap, exception handling | public-facing compression, rhetorical force | RT4, RT9 |
| Advocacy journalism | narrative-derived overclaim, alternative suppression | total neutrality performance, explicit normative stance | RT1, RT7 |
| Open letter | shared-premise fragility, audience heterogeneity, definitional pressure | exhaustive method display, emotional register | RT2, RT5 |

### Calibration principles

1. The adversary is competent and informed. Not lazy critics, not trolls, not uninformed opponents.
2. Fatal means the argument cannot survive this attack *for the target audience*. Not that the author is wrong.
3. Genre tolerance is not weakness tolerance. An op-ed is allowed compression; it's not allowed to ignore the central objection.

---

## §8. Hard Gates

Conditions that escalate to Must-Fix regardless of other findings.

| Gate | Condition | Rationale |
|------|-----------|-----------|
| **HG-RT1** | C0 has a Fatal vulnerability and no Unexploited Defense is available | The central claim cannot survive the adversary's attack with current resources |
| **HG-RT2** | ≥3 Fatal vulnerabilities across different RT codes | Systemic exposure from multiple independent angles |
| **HG-RT3** | RT10 (Cross-Exam Trapdoor) targets C0 directly with "author would struggle" | The manuscript cannot answer the adversary's central question |
| **HG-RT4** | RT1 (Easy Steelman Against) + RT7 (Alternative Suppression) co-occur | The adversary has a better story and the manuscript doesn't engage it |
| **HG-RT5** | RT5 (Definition Front) enables RT3 (Burden Inversion) | A definitional instability allows the adversary to reverse who must prove what |
| **HG-RT6** | All CX questions rated "author would struggle" | Comprehensively unprepared for cross-examination |
| **HG-RT7** | Testimony: RT11 (Standing/Scope Exposure) with no qualification | Witness exceeding observational warrant without acknowledgment — credibility-destroying under cross |

---

## §9. Output Format

### Argument_State.md § 10.4 Annotations

```markdown
### 10.4 Red-Team Pressure
_Module: Argument Red Team v1.0_
_Run date: [date]_
_Adversary profile: [form-calibrated description]_

**Vulnerability count:** [N] total — [n] Fatal, [n] Major, [n] Manageable, [n] Cosmetic

**Top vulnerabilities:**

| # | Flag | Name | Tier | Attack Vector | Distinguish Class | State Reference |
|---|------|------|------|---------------|------------------|-----------------|
| 1 | RT7 | Alternative Suppression | Fatal | [how adversary exploits] | Genuinely Vulnerable | § 5, alternatives |
| 2 | RT5 | Definition Front Open | Major | [how adversary exploits] | Context-Dependent | § 2, T1 |
| ... | | | | | | |

**Hard gates triggered:** [gate IDs, or NONE]

**Distinguish summary:**
- Genuinely Vulnerable: [count]
- Unexploited Defense: [count]
- Context-Dependent: [count]
- Intentional Risk: [count]

**Cross-examination readiness:** [PREPARED / PARTIALLY PREPARED / UNPREPARED]

**Bridge recommendations:**
- Banister: [Y/N and why]
- Reception Risk: [Y/N and why]
- Argument Evidence: [Y/N and why]
```

### Red_Team_Memo.md (Standalone Artifact)

```markdown
# Red Team Memo
## [Manuscript title or identifier]
_Argument Red Team v1.0_
_Date: [date]_
_Adversary profile: [description]_
_Argument type: [AT-code from § 1]_
_Audience: [from § 1]_

---

## Executive Summary
[2–3 sentences: Is this argument defensible? What is the adversary's
strongest line of attack? What is the overall vulnerability profile?]

---

## The Adversary's Best Case
[The strongest version of the opposing position, stated as a skilled
adversary would state it. 1–3 paragraphs.]

---

## Vulnerability Ranking
[Full ranking table — all vulnerabilities with RT codes, severity,
attack vector, distinguish class, and state reference]

---

## Objection Inventory
[Full objection set — every objection with target, adversary basis,
engagement status, and RT flags]

---

## Cross-Examination Questions
[5–10 questions with targets, exploits, expected difficulty, and RT flags]

---

## Burden and Definitional Pressure
[Burden attacks and definitional attacks with RT flags]

---

## Missing Alternatives
[Alternatives the manuscript fails to address with RT flags]

---

## Distinguish Classifications
[Each vulnerability with its classification and the test results
that support it]

---

## Hard Gate Report
[Gates triggered with explanation, or "No hard gates triggered."]

---

## Bridge Recommendations
- **Banister:** [recommendation and rationale]
- **Reception Risk:** [recommendation and rationale]
- **Argument Evidence:** [recommendation and rationale]
- **Revision Coach:** [if vulnerabilities suggest a specific repair
  sequence, note it — but do not prescribe the repairs]
```

---

## §10. Integration

### With Dialectical Clarity v2.0

Red Team is a downstream consumer. It reads the Argument State and produces adversarial analysis the core audit cannot — because structural diagnosis and adversarial testing are different activities. An argument can pass Dialectical Clarity and fail Red Team (structurally sound but defenseless against the strongest objection). An argument can fail Dialectical Clarity and pass Red Team (structurally messy but practically robust because the adversary's attacks all target strengths). Both outcomes are informative.

### With Revision Coach (Argument Mode)

The coach reads the Red Team Memo to sequence repair. Typical order: fix Fatal vulnerabilities first, surface Unexploited Defenses (cheapest fixes), narrow scope where burden is misplaced, stabilize definitions, strengthen engagement with the central objection. The Red Team does not prescribe this sequence — it provides the data.

---

## §11. Hard Rules

1. Never attack an argument the manuscript is not actually making.
2. Never confuse ideological disagreement with structural vulnerability.
3. Never recommend rewriting language inside this module; diagnose pressure only.
4. Always rank vulnerabilities rather than listing them flatly.
5. Always classify vulnerabilities through the Distinguish Framework before finalizing severity.
6. If the argument is strong, say so. A memo that finds nothing Fatal is a legitimate finding.

---

*The core audit asks whether the argument holds together. Red Team asks whether it holds up when someone smart tries to break it. Those are adjacent but not identical questions, and argument-shaped nonfiction needs both.*
