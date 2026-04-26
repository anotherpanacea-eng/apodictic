# Level-Setting Research: Adversarial Evidence Review Module
*Date: March 24, 2026*
*Status: Level-setting research — not yet a spec*
*Proposed location: Nonfiction Argument Engine, companion to Argument Evidence Deep-Dive*
*Trigger: F4 (argument-shaped nonfiction) test run revealed structural ceiling of persona-based adversarial critique*

---

## The Problem This Module Would Solve

APODICTIC's Nonfiction Argument Engine currently handles evidence through four complementary modules:

| Module | Question it asks | Method |
|--------|-----------------|--------|
| **Dialectical Clarity** | Is the argument structurally sound? | Diagnostic codes (AT, CL, SM, WR, BP, OB, NE, DI) |
| **Argument Evidence** | Is the evidence portfolio balanced, properly sourced, and quantitatively sound? | Provenance chains, portfolio balance, testimony calibration, verification queue |
| **Citation Verifier** | Do the citations exist and say what the manuscript claims? | API resolution (Phase 1) + editorial content comparison (Phase 2) |
| **Field Reconnaissance** | What counterevidence, gaps, and ecosystem problems exist? | Counterevidence search, literature gap detection, source health |

And one external skill:

| Skill | Question it asks | Method |
|-------|-----------------|--------|
| **Adversarial Critic** | Where would a hostile reader attack the argument? | Persona-based hostile reading |

**The gap:** None of these modules asks the adversarial evidentiary question: *"Even if every citation checks out, every number is correct, and every source is real — does the evidence actually bear the weight the argument puts on it, and how would a hostile expert dismantle the inferential chain?"*

- Dialectical Clarity diagnoses warrant gaps (WR0, WR1) but doesn't attack them
- Argument Evidence flags portfolio narrowness (AE3) but doesn't exploit it
- Citation Verifier catches mischaracterizations (CV4, CV5) but doesn't ask what a hostile reader would do with the accurate characterization
- Field Recon surfaces counterevidence but doesn't deploy it against the manuscript
- The adversarial critic produces hostile-sounding output but, per the research below, persona prompting changes tone without changing the distribution of substantive findings

The proposed module would consume outputs from all four existing modules and apply structured adversarial protocols to generate attacks that are specific, grounded, localized, and calibrated — not generic hostility.

---

## The Empirical Case Against Persona-Based Adversarial Review

### LLMs cannot self-correct reasoning without external feedback

**Huang et al., "Large Language Models Cannot Self-Correct Reasoning Yet" (ICLR 2024)**
[arXiv:2310.01798](https://arxiv.org/abs/2310.01798)

Intrinsic self-correction (no external tools or oracle) frequently *degrades* performance. The model changes correct answers to incorrect ones as often as it catches genuine errors. The core problem: LLMs lack a ground-truth signal for evaluating their own reasoning.

**Kamoi et al., "When Can LLMs Actually Correct Their Own Mistakes?" (TACL 2024)**
[MIT Press](https://direct.mit.edu/tacl/article/doi/10.1162/tacl_a_00713/125177/When-Can-LLMs-Actually-Correct-Their-Own-Mistakes)

Definitive survey. No prior work demonstrates successful self-correction with LLM-prompted feedback alone, except in tasks where verification is easier than generation (e.g., code with test suites). Written argument quality is *not* such a domain.

**Self-Correction Bench (2025)**
[arXiv:2507.02778](https://arxiv.org/html/2507.02778)

LLMs reliably correct errors in *external inputs* but fail to correct errors in *their own outputs*. Cause: training on error-free demonstrations means models never learn the error-and-correct process for their own generations.

**Design implication:** A module that reviews work in the same context that produced it will inherit the production's blind spots. The module needs external grounding — source documents, counterevidence, published standards — to compensate for lack of genuine epistemic independence.

### Persona prompting changes tone, not substance

**Basil & Shapiro et al., "Prompting Science Report 4: Playing Pretend: Expert Personas Don't Improve Factual Accuracy" (SSRN 2025)**
[SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5879722)

Expert personas have no significant impact on factual accuracy. They change style and tone but not the distribution of substantive findings. On MMLU, expert personas actually *damaged* accuracy (68.0% vs. 71.6% baseline).

**Design implication:** "You are a hostile peer reviewer" will produce hostile-*sounding* output without systematically surfacing different or better critiques. The module must change the *task structure* (what the model analyzes and against what evidence), not the persona.

### Localization outperforms holistic evaluation

**Tyen et al., "LLMs Cannot Find Reasoning Errors, but Can Correct Them Given the Error Location" (ACL Findings 2024)**
[ACL Anthology](https://aclanthology.org/2024.findings-acl.826/)

LLMs are bad at *locating* errors in reasoning chains, even in clear-cut cases. But when told *where* the error is, they can often correct it successfully.

**Design implication:** The module's job is localization — flag the specific passage, claim, and logical step — not holistic quality assessment. The author (human or model) does the correction.

### Multi-agent debate requires genuinely different frameworks

**Du et al., "Improving Factuality and Reasoning with Multiagent Debate" (ICLR 2024)**

Multi-agent debate only improves performance when agents use genuinely different analytical frameworks, not just different personas with the same reasoning method. Standard multi-agent debate with the same approach but different names creates a "fixed mental set."

**Diverse Multi-Agent Debate (DMAD) work (2024-2025)** confirms: assigning genuinely different reasoning approaches consistently outperforms standard MAD with fewer rounds.

**Design implication:** The adversarial evidence reviewer must apply a structurally different analytical framework from the diagnostic modules. Not "be meaner about what Argument Evidence found" but "apply ACH matrices, legal cross-examination taxonomy, and severe testing criteria that the diagnostic modules don't use."

### LLM review overlap with human experts is ~30-40%

**Liang et al., "Can Large Language Models Provide Useful Feedback on Research Papers?" (NEJM AI 2024)**
[NEJM AI](https://ai.nejm.org/doi/abs/10.1056/AIoa2400196)

GPT-4 feedback overlapped with human reviewer feedback 30.85% (Nature journals) and 39.23% (ICLR). Human-human overlap was 28.58% and 35.25% respectively. The LLM captures about a third of what any single expert would flag.

Critically: LLM reviews show *minimal structural variation across paper quality levels* — only 5.7% more weaknesses identified in weak vs. strong papers.

**Design implication:** The module should not promise to catch everything. It should promise to surface a *complementary* set of concerns. And it must calibrate critique density against actual evidence quality — uniform-density criticism is noise.

### Sycophancy is structural, not tonal

**Sharma et al., "Towards Understanding Sycophancy in Language Models" (ICLR 2024)**
[arXiv:2310.13548](https://arxiv.org/abs/2310.13548)

Sycophancy is driven by RLHF training: human preference data rewards agreeable responses. The problem is structural (baked into training), not a prompting issue that persona can fix.

**Design implication:** Mitigation requires structural changes to the task (forced consideration of alternatives, external grounding, rubric decomposition), not just instructions to "be critical."

### Persuasion can override truth in debate architectures

**Agarwal & Khanna, "When Persuasion Overrides Truth in Multi-Agent LLM Debates" (2025)**
[arXiv:2504.00374](https://arxiv.org/abs/2504.00374)

Even small models can craft persuasive arguments that override truthful answers with high confidence. Persuasion overrides truth even without malicious intent — just by varying verbosity.

**Design implication:** If the module generates attacks, the evaluation of those attacks must assess *evidence grounding*, not *rhetorical force*. An articulate but groundless attack is worse than useless — it could cause the author to weaken a sound argument.

---

## Existing Approaches: What the Field Offers

### Peer Review Simulation

**Stanford Agentic Reviewer** ([paperreview.ai](https://paperreview.ai/tech-overview)): Multi-agent system achieving Spearman correlation of 0.42 with human ICLR reviewers (vs. 0.41 between two human reviewers). Diagnostic, not adversarial — scores against criteria but doesn't inhabit a hostile reader.

**Katmer Peer Review Skill** ([GitHub](https://github.com/hkcanan/katmer-code/blob/main/src/skills/peer-review.md)): 8-criterion rubric (1-5 scores) with parallel subagents and API-grounded reference detection. Good structural decomposition but no adversarial reasoning, no inferential testing, no independence disclosure.

**ICLR 2025 Review Feedback Agent**: Tested on 20,000+ reviews; 27% of reviewers who received AI feedback made changes. Demonstrates that structured feedback from AI can influence expert judgment, but the feedback is quality-assessment, not adversarial.

**Assessment:** Peer review simulation tools are diagnostic. They assess quality against norms. None operationalizes "find the weakest link and attack it." The gap between "evaluate" and "attack" is where the proposed module would live.

### Forensic Statistics

**GRIM test**: Checks whether reported means are mathematically possible given sample sizes.
**SPRITE**: Extends GRIM to means + SDs, reconstructs plausible datasets.
**statcheck**: Extracts statistical results and recalculates p-values.
**rsprite2 / scrutiny R packages**: Modern implementations.

**AI-assisted statistical error detection (PMC 2025)**: Combines specific high-accuracy tools (statcheck, GRIM) with LLMs for qualitative design issues, confirmed by human reviewers.

**Assessment:** These tools operationalize "is this number even possible?" — a specific form of hostile reading. But none asks the deeper question: "even if this number is correct, does it support what you're claiming?" The inferential gap between statistical accuracy and argumentative warrant is the harder problem.

### Domain-Standard Evidence-Appraisal Frameworks

**[GRADE (Grading of Recommendations, Assessment, Development and Evaluations)](https://www.cdc.gov/acip-grade-handbook/hcp/chapter-7-grade-criteria-determining-certainty-of-evidence/index.html)**: The dominant framework for rating certainty of evidence in clinical and public health. Rates evidence as High / Moderate / Low / Very Low based on five downgrading criteria: risk of bias, inconsistency, indirectness, imprecision, and publication bias. Widely adopted by WHO, Cochrane, and CDC.

**[RoB 2 (Risk of Bias 2)](https://methods.cochrane.org/risk-bias-2)**: Cochrane's tool for assessing risk of bias in randomized trials. Structured around five domains: randomization, deviations from intended interventions, missing outcome data, measurement of outcome, and selection of reported result.

**[ROBINS-I](https://methods.cochrane.org/bias/risk-bias-non-randomized-studies-interventions)**: Cochrane's companion for non-randomized studies. Covers confounding, selection, intervention classification, deviations, missing data, outcome measurement, and reported result selection.

**[scite Smart Citations](https://direct.mit.edu/qss/article/2/3/882/102990/scite-A-smart-citation-index-that-displays-the)**: Citation index that classifies how citing papers use a source — supporting, mentioning, or contrasting. Directly relevant to adversarial evidence review: a paper heavily cited in "contrasting" mode is flagged as contested in its field.

**[Valsci](https://link.springer.com/article/10.1186/s12859-025-06159-4)**: Claim-verification system for scientific papers. Extracts claims, maps them to cited evidence, and assesses whether the evidence supports the claim. Closest existing system to the inferential testing this module proposes.

**Assessment:** These frameworks operationalize domain-specific standards for "how good is this evidence?" — not just "is it real?" GRADE's five downgrading criteria provide a ready-made adversarial rubric: for each piece of evidence, ask whether it suffers from bias, inconsistency, indirectness, imprecision, or publication bias. RoB 2 and ROBINS-I provide structured checklists for attacking specific study designs. Scite provides external signal on how the field actually treats a cited source. Valsci is the closest to our module's core function but operates at the individual-claim level within scientific papers, not at the argument level in policy writing.

**Design implication:** The spec should include domain packs that import the appropriate evidence-appraisal framework for the manuscript's field:

| Domain | Primary framework | Secondary |
|--------|------------------|-----------|
| Clinical / public health | GRADE + RoB 2 | ROBINS-I for non-randomized |
| Social science / policy | GRADE-adapted + ROBINS-I | scite for citation context |
| Legal / policy analysis | FRE 702 standards | Cross-exam taxonomy |
| Humanities / theory | Severe testing (Mayo) | Argument mining standards |

### Intelligence Community Red Team Frameworks

**Analysis of Competing Hypotheses (ACH)**: Developed by Richards Heuer at CIA. Core move: list all hypotheses, evaluate each piece of evidence for consistency/inconsistency with each. Privileges disconfirmation over confirmation. [CIA Tradecraft Primer (PDF)](https://www.cia.gov/resources/csi/static/Tradecraft-Primer-apr09.pdf).

**Structured Analytic Techniques (SATs)**: Broader framework including Devil's Advocacy, Team A/Team B, Red Team Analysis, Delphi Method.

**Pre-mortem analysis (Gary Klein)**: "Imagine this has already failed. Why?" Based on prospective hindsight research showing ~30% improvement in risk identification accuracy.

**Assessment:** ACH provides the strongest structural model for the module. Its matrix approach (evidence × hypotheses, scored for consistency/inconsistency) translates directly: for each piece of evidence in a manuscript, ask not just "is this true?" but "what competing claims does this also support?" and "what would we expect to see if this claim were false?"

The CIA Tradecraft Primer explicitly warns against analysts red-teaming their own work. The intelligence community solved the independence problem institutionally (separate red teams, different analysts). We can't replicate that, but we can import the analytical protocols.

### Legal Cross-Examination

Expert witness cross-examination uses six established attack vectors:

1. Lack of perceptive capacity (the source couldn't observe what it claims)
2. Inadequate recollection (the data is too old or incomplete)
3. Bias/prejudice (developer allegiance, funding conflicts)
4. Questionable qualifications (authority overreach across domains)
5. Prior inconsistent statements (the source contradicts itself elsewhere)
6. Inconsistency with published authorities (other credible sources disagree)

The "boxing in" technique: force the author to commit to exact opinions, bases, and assumptions, then test each one.

FRE Rule 702 (amended 2023): Expert testimony must reflect "reliable application of reliable methods to sufficient facts."

**Assessment:** These attack vectors translate directly to an evidence audit taxonomy. Each maps to a specific type of adversarial question about whether evidence bears the weight the argument puts on it.

### Philosophy of Science

**Severe testing (Deborah Mayo)**: A claim is severely tested only if it has been subjected to a test that probably would have found flaws, were they present. The question is not "did this evidence pass a test?" but "how hard was the test it passed?" [Error Statistics Philosophy blog](https://errorstatistics.com/).

**Adversarial collaborations**: Teams with opposing theoretical commitments jointly design experiments. Both sides agree in advance on what results would count for or against each position. APA 2024 paper argues this is the successor to pre-registration as a credibility mechanism.

**Registered Reports**: Separate hypothesis/method (Stage 1) from results (Stage 2). Forces separation of confirmatory and exploratory analyses.

**Assessment:** Mayo's severe testing framework provides the philosophical backbone. The module should operationalize "how severely has this claim been tested by this evidence?" — which requires imagining what the evidence would look like if the claim were wrong. This is the deepest form of adversarial evidence review and the hardest to implement in a self-reviewing system.

---

## Design Principles (Empirically Grounded)

Based on the research above, the module should be built around these principles:

### 1. External grounding, not self-critique

The module must consume external reference points:
- Citation Verifier data (what sources actually say)
- Field Recon counterevidence (what contradicts the claims)
- Published methodological standards (what counts as adequate evidence in this domain)
- Source text (the actual studies, not the manuscript's characterization of them)

Pure self-critique (same model, same context, no external data) will likely degrade quality. The CRITIC framework (arXiv 2305.11738) showed LLMs improve when they interact with external tools during critique.

### 2. Structured attack protocols, not open-ended hostility

Three formalized frameworks, each addressing a different adversarial question:

| Framework | Adversarial question | Source |
|-----------|---------------------|--------|
| **ACH matrix** | "What competing claims does this evidence also support?" | CIA/Heuer |
| **Legal cross-exam taxonomy** | "Which of these six attack vectors applies to this evidence?" | FRE/trial practice |
| **Severe testing** | "How hard was the test this claim passed? Would this evidence look different if the claim were false?" | Mayo |

These force consideration of paths the model wouldn't spontaneously take. They are task-structural, not persona-based.

### 3. Task structure over persona

The module should never rely on "you are a hostile reviewer." It should change:
- What the model analyzes (specific claim-evidence pairings, not the whole manuscript)
- Against what evidence (source text, counterevidence, methodological standards)
- Using what analytical framework (ACH, cross-exam, severe testing)

### 4. Localization over evaluation

Every attack must specify:
- The exact passage being challenged
- The exact claim being made
- The exact evidence being relied on
- The exact inferential gap or counter-evidence
- The exact source for the counter-claim

No generic severity labels. No "this section is weak." If the module can't localize the attack, the attack doesn't fire.

### 5. Calibration against quality

The module must produce proportionally more flags for weaker evidence and fewer for stronger evidence. The NEJM AI finding (5.7% variation across quality levels) means uncalibrated LLM review is noise. Possible calibration mechanisms:
- Weight attacks by the severity of the diagnostic codes already fired (WR1 gets heavier adversarial treatment than PASS)
- Weight attacks by load-bearing status (C0 supports get more adversarial attention than passing references)
- Skip citation-fidelity attack classes (CV4, CV5) when Citation Verifier Phase 2 already cleared the pairing with MATCH — but do NOT suppress inferential attacks on MATCHed citations. The whole point of this module is to ask what happens after citation accuracy is settled: evidence can be real, correctly cited, and still overburdened.

### 6. Honest limitation disclosure

The module should include, in every output:
- A statement that LLM-only adversarial review is incomplete and should not be treated as independent expert review
- A recommendation to seek independent expert review for the highest-stakes claims
- Disclosure of whether the same model/session produced the work being reviewed

Note: the ~30-40% overlap figure from the peer review literature (Liang et al. NEJM AI 2024) is a useful humility calibration for unstructured LLM review, but should not be cited as a hard numeric ceiling for a structured, externally grounded, evidence-specific module. The module may perform better or worse depending on domain, grounding quality, and task decomposition.

### 7. Independence controls

For high-consequence reviews (testimony, publication, legislative advocacy):
- **Require fresh-session execution.** The reviewing session must not be the drafting session. The self-correction research (Huang et al., Self-Correction Bench) shows same-session review is the worst case.
- **Require external-artifact citation for every attack.** No purely intrinsic critiques. Every adversarial finding must cite its grounding source: `source text`, `Citation Verifier finding`, `Field Recon item`, or `published methodological standard`.
- **Use a two-tier severity model:**
  - `Provisional attack`: one protocol flags a vulnerability
  - `Elevated attack`: two protocols converge on the same vulnerability, or one protocol plus external counterevidence or published standard failure
- If same-session review is used (convenience mode), the output must include explicit downgrade language: "This review was conducted in the same session that produced the work. Findings should be treated as preliminary and verified by independent review."

---

## Non-Duplication Boundary

### What existing modules own (and this module does NOT do):

| Already owned by | What |
|-----------------|------|
| **Dialectical Clarity** | Claim architecture, warrant diagnosis, scope assessment, objection handling |
| **Argument Evidence** | Provenance chains, portfolio balance, testimony calibration, verification queue |
| **Citation Verifier** | Source existence, metadata accuracy, quote/paraphrase fidelity |
| **Field Reconnaissance** | Counterevidence search, literature gaps, source ecosystem health |
| **Red Team** (when specced) | Argument vulnerability, rhetorical attack surface |

### What this module owns:

1. **Adversarial inferential testing**: Does this evidence *bear the weight* this claim puts on it? (Not whether the evidence exists or is accurately cited — that's the Verifier. Not whether the warrant is present — that's Dialectical Clarity. Whether the inferential chain would survive hostile expert scrutiny.)

2. **Evidence-node-bound attack generation**: Formalized attacks on specific claim-evidence pairings using ACH, cross-exam taxonomy, and severe testing — grounded in external data from the other modules' outputs. Every attack must have an explicit upstream anchor in `Argument_State.md`, `Citation_Ledger.md`, or `Field_Reconnaissance_Report.md`.

3. **Survivability judgments**: For each attacked claim-evidence pairing, a judgment on whether the inferential link survives the attack, with specific grounding cited.

**This module does NOT:**
- Construct full countercases or opposition memos (Red Team territory)
- Generate audience-framed rhetorical attacks (Red Team / adversarial critic territory)
- Propose what the argument *should* be (firewall violation)
- Attack claims without grounded evidence-node anchors (ungrounded attacks are suppressed)

### The handoff:

- **From** Citation Verifier: source data, phase 2 fit assessments, corrected characterizations
- **From** Field Recon: counterevidence items (ADDRESS/ACKNOWLEDGE/SET ASIDE), literature gaps
- **From** Argument Evidence: AE codes, portfolio analysis, verification queue
- **From** Dialectical Clarity: WR codes, BP codes, OB codes, claim ladder
- **To** Revision Coach: prioritized list of vulnerabilities with specific repair recommendations

---

## Design Decisions (Resolved)

Per Codex review and empirical test on F4 (argument-shaped nonfiction):

### 1. Scope: evidence-node-bound, not full-manuscript

The module fires only on claim-evidence pairings with explicit upstream anchors in `Argument_State.md`, `Citation_Ledger.md`, or `Field_Reconnaissance_Report.md`. It does not scan the full manuscript for unanchored problems — that's the diagnostic modules' job.

However, the F4 test revealed that some vulnerabilities (the CBT tier asymmetry) weren't flagged by any diagnostic code but emerged under adversarial pressure. **Resolution:** The module also tests all unflagged C0 and central-subclaim supports, regardless of whether diagnostic codes fired. The requirement is an upstream anchor (the claim-evidence pairing must be identifiable in the support map), not a prior flag.

### 2. Protocol execution: parallel

ACH, cross-exam taxonomy, and severe testing run in parallel on the same claim-evidence pairings. The DMAD research (Du et al. ICLR 2024) shows genuinely different analytical frameworks produce better results than sequential deepening of a single approach. The F4 test confirmed this — the attacks that landed hardest came from different analytical angles.

### 3. Output format: preparation guide with grounding

Format (d) from the options: a preparation guide organized by "what to address / what to acknowledge / what to accept." Each entry must include:
- The specific passage, claim, and evidence
- Which protocol(s) generated the attack
- The grounding source (source text, Citation Verifier finding, Field Recon item, or published standard)
- Severity tier (Provisional or Elevated)
- Survivability judgment (survives / weakened / does not survive)

### 4. Independence: resolved per §7 above

High-consequence reviews require fresh-session execution and external-artifact citation for every attack. Same-session review is permitted for convenience but requires explicit downgrade language in the output.

### 5. Relationship to adversarial critic skill: separate

The adversarial critic is a general-purpose persona skill for rhetorical/logical attack. This module is a structured, evidence-specific analytical tool. They coexist:
- Adversarial critic: "where would a hostile reader attack the *argument*?"
- Adversarial Evidence Review: "where would a hostile expert attack the *evidence*, and would the attack land?"

The research shows persona-based approaches have a ceiling for evidentiary reasoning but may be adequate for rhetorical attack. The modules serve different functions and should not be merged.

### 6. Open question remaining

**Domain packs.** The spec should include domain-specific evidence-appraisal standards (GRADE for clinical/public health, ROBINS-I for social science, FRE 702 for legal, severe testing for humanities). The level-setting research identifies the frameworks; the spec needs to operationalize which standards apply to which manuscript types and how they integrate with the attack protocols. This is the primary remaining design work.

---

## Sources

### LLM Self-Critique
- [Huang et al. (ICLR 2024) — Cannot Self-Correct Reasoning](https://arxiv.org/abs/2310.01798)
- [Kamoi et al. (TACL 2024) — When Can LLMs Correct Mistakes?](https://direct.mit.edu/tacl/article/doi/10.1162/tacl_a_00713/125177)
- [Self-Correction Bench (2025)](https://arxiv.org/html/2507.02778)
- [Tyen et al. (ACL 2024) — Cannot Find but Can Correct](https://aclanthology.org/2024.findings-acl.826/)
- [CRITIC Framework — Tool-Interactive Critiquing](https://arxiv.org/abs/2305.11738)
- [Madaan et al. (NeurIPS 2023) — Self-Refine](https://arxiv.org/abs/2303.17651)

### Persona and Sycophancy
- [Basil & Shapiro (SSRN 2025) — Expert Personas Don't Improve Accuracy](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5879722)
- [Sharma et al. (ICLR 2024) — Understanding Sycophancy](https://arxiv.org/abs/2310.13548)
- [Not Your Typical Sycophant (2025)](https://arxiv.org/html/2601.15436v1)

### LLM Review Quality
- [Liang et al. (NEJM AI 2024) — LLM Feedback on Research Papers](https://ai.nejm.org/doi/abs/10.1056/AIoa2400196)
- [Mind the Blind Spots (EMNLP 2025)](https://arxiv.org/html/2502.17086v4)
- [Monitoring AI-Modified Content (ICML 2024)](https://arxiv.org/abs/2403.07183)

### Multi-Agent Debate
- [Du et al. (ICLR 2024) — Multiagent Debate](https://proceedings.iclr.cc/paper_files/paper/2024/file/25cc3adf8c85f7c70989cb3a97a691a7-Paper-Conference.pdf)
- [Agarwal & Khanna (2025) — Persuasion Overrides Truth](https://arxiv.org/abs/2504.00374)
- Irving et al. (2018) — AI Safety via Debate (foundational)

### Intelligence Community
- [CIA Tradecraft Primer (PDF)](https://www.cia.gov/resources/csi/static/Tradecraft-Primer-apr09.pdf)
- [Analysis of Competing Hypotheses](https://en.wikipedia.org/wiki/Analysis_of_competing_hypotheses)
- [Gary Klein — Pre-mortem](https://www.gary-klein.com/premortem)

### Legal Cross-Examination
- [Expert Witness Cross-Examination Guide](https://www.expertinstitute.com/resources/insights/ultimate-guide-cross-examining-expert-witnesses/)
- [FRE Rule 702 (Cornell LII)](https://www.law.cornell.edu/rules/fre/rule_702)

### Philosophy of Science
- [Deborah Mayo — Error Statistics Philosophy](https://errorstatistics.com/)
- [Statistical Inference as Severe Testing (Cambridge)](https://www.cambridge.org/core/books/statistical-inference-as-severe-testing/D9DF409EF568090F3F60407FF2B973B2)
- [Adversarial Collaboration: Next Science Reform (APA 2024)](https://psycnet.apa.org/record/2024-24022-032)
- [Benefits of Registered Reports (2024)](https://www.tandfonline.com/doi/full/10.1080/2833373X.2024.2376046)

### Forensic Statistics
- [GRIM and SPRITE overview](https://www.enago.com/academy/grim-and-sprite-simple-tools-to-identify-errors-in-research/)
- [AI in Detecting Statistical Errors (PMC 2025)](https://pmc.ncbi.nlm.nih.gov/articles/PMC12722777/)

### Peer Review Simulation
- [Stanford Agentic Reviewer](https://paperreview.ai/tech-overview)
- [Katmer Peer Review Skill](https://github.com/hkcanan/katmer-code/blob/main/src/skills/peer-review.md)
- [Argument Mining Survey (2025)](https://arxiv.org/html/2506.16383v3)
- [Explaining Arguments' Strength (IJCAI 2024)](https://www.ijcai.org/proceedings/2024/0401.pdf)

### Evidence-Appraisal Frameworks
- [GRADE Handbook — Criteria for Determining Certainty of Evidence (CDC)](https://www.cdc.gov/acip-grade-handbook/hcp/chapter-7-grade-criteria-determining-certainty-of-evidence/index.html)
- [RoB 2 — Risk of Bias in Randomized Trials (Cochrane)](https://methods.cochrane.org/risk-bias-2)
- [ROBINS-I — Risk of Bias in Non-Randomized Studies (Cochrane)](https://methods.cochrane.org/bias/risk-bias-non-randomized-studies-interventions)
- [scite Smart Citations (MIT QSS 2021)](https://direct.mit.edu/qss/article/2/3/882/102990/scite-A-smart-citation-index-that-displays-the)
- [Valsci — Claim Verification for Scientific Papers (BMC Bioinformatics 2025)](https://link.springer.com/article/10.1186/s12859-025-06159-4)

### Curse of Knowledge
- [Curse of Knowledge in Predicting Others' Knowledge (PMC 2022)](https://pmc.ncbi.nlm.nih.gov/articles/PMC9794110/)

---

## Codex Review (March 24, 2026)

Codex reviewed this document and identified five findings. All have been incorporated:

1. **[P1] Red Team boundary sharpened.** Module is now evidence-node-bound by rule. No countercase construction, no opposition memos, no audience-framed rhetorical attacks. Only evidence attacks with upstream anchors.
2. **[P1] Independence controls promoted from open questions to design commitments.** Fresh-session required for high-consequence reviews. External-artifact citation required for every attack. Two-tier severity model (Provisional / Elevated). Downgrade language for same-session convenience mode.
3. **[P2] Evidence-appraisal frameworks added.** GRADE, RoB 2, ROBINS-I, scite Smart Citations, and Valsci now in the landscape survey. Domain packs proposed for the spec.
4. **[P2] Calibration fix.** "Suppress MATCHed citations" corrected to "skip citation-fidelity attack classes on MATCHed citations." Inferential attacks on accurately-cited evidence are the module's core function and must not be suppressed.
5. **[P3] Ceiling disclosure softened.** 30-40% figure retained as calibration, not as hard numeric ceiling. Disclosure language changed to "LLM-only adversarial review is incomplete and should not be treated as independent expert review."

---

*Level-setting complete. The research converges on a clear design direction: structured adversarial protocols with external grounding, not persona-based hostility. The module's value proposition is preparing the author for independent review by surfacing the attacks that grounded, structured adversarial reasoning can find — while honestly disclosing what it cannot find because it lacks genuine epistemic independence. Codex review incorporated.*
