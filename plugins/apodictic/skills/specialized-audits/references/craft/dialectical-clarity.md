# Specialized Audit: Dialectical Clarity
## Version 2.1
*Previous version: 2.0 (March 2026)*
*Updated: July 2026*
*Enrichment inputs: Codex spec + level-setting, Claude research, Gemini research, v1.0 deployed audit*

---

## Purpose

Diagnose argumentative structure in non-narrative material: essays, op-eds, policy briefs, testimony, reports, scholarly articles, grant proposals, white papers, legal briefs, book reviews, advocacy journalism, open letters, crisis communications, and argument-with-embedded-narrative hybrids. This audit tests whether the argument is identifiable, supported, inferentially warranted, honestly scoped, fair to disagreement, and evaluable by its intended audience.

**Core claim:** Material whose dominant function is claim-and-support cannot be meaningfully audited by story-spine tools. Forcing narrative diagnostics on argument-shaped writing produces false failures ("no protagonist," "no inciting incident") that are technically true and practically useless. This audit provides what story-spine tools cannot: structural diagnosis of argumentative clarity, inferential integrity, and dialectical honesty.

**Deficit-First Diagnostic Rule:** Do not evaluate dialectical clarity by confirming that claims, evidence, and objections appear on the page. You must hunt for the *absence* of the inferential bridge — the *absence* of warrant linking evidence to claim, the *absence* of honest scope, and the *absence* of live disagreement the argument could lose to. A piece that cites evidence and gestures at objection but smuggles the warrant is a failure, even if it reads as rigorous. You are auditing for inferential gaps and foreclosed objections, not validating the vocabulary of rigor.

**What this audit is:** The diagnostic engine for all argument-shaped nonfiction entering the APODICTIC system. It asks whether the reader can identify the claim, evaluate the evidence, test the inferential bridge between them, judge whether the scope is honest, determine whether disagreement has been handled fairly, and assess whether narrative does argumentative work or replaces it. It calibrates all of these by audience and genre.

**What this audit is not:** Rhetoric coaching. It does not teach persuasion, suggest hooks, recommend "counterargument paragraphs," or optimize for audience manipulation. It does not catalog named fallacies as an end in themselves. It diagnoses whether the argument is structurally clear, inferentially warranted, and evidentially honest. The writer decides what to argue; this audit tests whether the argument holds together.

**Named for:** The dialectical tradition in philosophy, in which argument is tested through objection, scope, and evidence, not the rhetorical tradition (which optimizes for persuasion) and not the informal-logic tradition (which catalogs named fallacies).

**When to activate:**

- Franklin Pathway returns Classification 3 (Argument With Embedded Narrative)
- Franklin Pathway returns Classification 4 and redirects to "argument-driven piece" or "policy brief"
- Narrative Nonfiction Craft audit returns F5 (Argument with embedded narrative)
- Intake identifies material as essay, op-ed, testimony, policy brief, report, scholarly article, grant proposal, white paper, legal brief, book review, open letter, or advocacy journalism
- Author states the piece's purpose is to argue, persuade, propose, evaluate, or testify

---

## Firewall Compliance

This audit operates within the Editor's firewall by producing diagnostic classifications and structural requirements, not content.

### Allowed

- Extracting the main claim and subclaims from existing text
- Classifying argument type, audience posture, and promise
- Mapping what evidence supports which claims and through what inferential bridge
- Diagnosing scope mismatches between claims and evidence
- Testing warrant legibility, backing adequacy, and qualifier discipline
- Identifying objections the text engages (or conspicuously avoids) and classifying the quality of engagement
- Testing dialectical integrity: whether argumentative moves are fair or procedurally manipulative
- Classifying audience and calibrating structural requirements accordingly
- Tagging narrative vignettes by argumentative function and testimonial position
- Tracking cross-section drift in claims, definitions, qualifications, and scope
- Distinguishing unwarranted arguments from unconventional but warranted argument forms
- Flagging structural gaps in the support chain, inferential bridge, or dialectical procedure

### Not Allowed

- Inventing claims, subclaims, warrants, or stakes the text does not contain
- Suggesting what the argument "should" be
- Proposing objections the writer should address (diagnosis only: "central objection unaddressed")
- Writing or rewriting argument sections
- Supplying alternate definitions the manuscript never signals
- Converting the audit into persuasion coaching or audience manipulation advice
- Evaluating whether the argument is *correct* — only whether it is *structurally clear, inferentially warranted, and evidentially supported*
- Treating a structurally weak argument as strong because the reviewer agrees with it

### The Distinction in Practice

- ❌ NOT ALLOWED: "You should add a counterargument about cost-effectiveness in paragraph 7."
- ✅ ALLOWED: "Subclaim C2 has no support. The argument asks the reader to accept it on assertion alone. Code: SM0."
- ❌ NOT ALLOWED: "You should define freedom as collective self-rule in paragraph 4."
- ✅ ALLOWED: "The term 'freedom' carries one meaning in the setup and a broader one in the conclusion. The shift does argumentative work without disclosure. Code: CL4."
- ❌ NOT ALLOWED: "The opening would be stronger with a concrete example."
- ✅ ALLOWED: "Argument type is AT3 (propositional) but evidence is exclusively AT1-appropriate (explanatory). The burden of proof exceeds what the evidence structure delivers. Code: BP1."
- ❌ NOT ALLOWED: "You should answer the jobs objection by citing labor data."
- ✅ ALLOWED: "The central objection for an AT3 policy recommendation is missing. The proposal is not comparatively defended. Codes: OB3, BP5."

---

## Code Namespace

This audit uses nine code families across nine diagnostic steps.

**Original families (v1.0):**

- `AT` — argument type (Step 1)
- `CL` — claim ladder (Step 2)
- `SM` — support map (Step 3)
- `BP` — burden of proof and scope (Step 5)
- `OB` — objection handling (Step 6)
- `NE` — narrative-as-evidence (Step 7)

**Enrichment families (v2.0):**

- `AC` — audience calibration (Step 1)
- `WR` — warrant and inference bridge (Step 4)
- `DI` — dialectical integrity (Step 6)

**Total codes:** 45 across 9 families.

**No collisions with existing code systems:**

- Scene Turn Diagnostics: G-codes, C-codes, O-codes, Sq-codes, H-codes, U-codes, P-codes
- Emotional Craft Diagnostics: S-codes, B-codes
- Narrative Nonfiction Craft: F-codes, QS-codes, I-codes, ST-codes, SW-codes, AS-codes, A-codes, LC-codes, E-codes
- Character Architecture Part 9: M-codes, W-codes, N-codes, DN-codes, OCA-codes, PW-codes, SR-codes, MC-codes, TP-codes
- Horror Craft Integration: DR-codes, DP-codes, MN-codes, PS-codes, ED-codes, TP-codes, UN-codes
- Grimdark: MA-codes, VE-codes, PA-codes, CC-codes, IB-codes, CP-codes, HD-codes

All nine code families use two-letter prefixes. All may appear in the same editorial letter alongside codes from other audits.

---

## The Diagnostic Procedure

Nine steps. Steps 1 and 2 run on the full piece. Steps 3–7 sample strategically within the scope defined below. Step 8 compares across sections. Step 9 classifies the argument form and may retroactively adjust prior findings.

### Step 1: Argument Type, Promise & Audience Calibration (AT, AC)

Classify the argument by its dominant function, then identify what audience the argument structurally imagines. Audience calibration gates everything downstream: what counts as a warrant gap in a policy brief is standard operating procedure in a fundraising appeal. Every code in Steps 2–7 calibrates differently depending on what Step 1 returns.

**Run on:** opening + closing + 1–2 representative body sections.

```
Argument Type: [AT-code]
  Promise: [what the reader expects to receive]
  Burden level: [LOW / MEDIUM / HIGH]
  Audience:
    Expertise: [GENERAL / MIXED / EXPERT]
    Receptivity: [SYMPATHETIC / MIXED / HOSTILE]
    Consequence context: [LOW / MEDIUM / HIGH]
  Consistent throughout: [Y/N]
  Code: [AT-code, AC-code, or PASS]
```

**Argument type codes:**

| Code | Type | Promise to Reader | Burden Level |
|------|------|-------------------|-------------|
| **AT1** | Explanatory | "Here's how this works" | Low — must be clear and accurate |
| **AT2** | Evaluative | "Here's whether this is good/bad/working/broken" | Medium — must show criteria and apply them |
| **AT3** | Propositional | "Here's what we should do" (policy/normative) | High — must show problem, solution, tradeoffs, and why alternatives fail |
| **AT4** | Testimonial | "I witnessed this; here's what it means" | Split — observation is low-burden, interpretation is high-burden |
| **AT5** | Generative / Lens-Offering | "Here's a lens; look through it and see what it reveals" | Split — coherence + fertility on the journey; asserted burden at each cash-out |

**Argument type failure codes:**

| Code | Name | Description |
|------|------|-------------|
| **AT0** | Type undeclared | Argument shifts between explaining, evaluating, and proposing without signaling; reader can't calibrate their skepticism |

**AT4 burden split:** Do not split testimony into a new global argument type. Keep AT4, but diagnose within it:

1. **Observational burden** — what the witness directly saw, experienced, or can responsibly report
2. **Interpretive burden** — what the testimony means beyond the observed event
3. **Representative burden** — whether a personal or local account is being asked to stand for a wider population or system

**AT5 burden split:** A writer-confirmed generative register changes the aim of diagnosis, not its coverage. Keep every finding in the ledger and assess three burdens:

1. **Coherence burden** — the lens must survive its own development.
2. **Fertility burden** — the lens must reveal, reframe, or connect something unavailable without it. If deleting the lens vocabulary leaves every conclusion unchanged, consider GN1.
3. **Cash-out burden** — inventory every conversion of the lens into assertion or prescription. Each cash-out is assessed at asserted-register burden, scaled to how hard the landing is pressed. A prescriptive/action-demanding cash-out is never eligible for register or stance demotion.

AT5 is declared or writer-confirmed at intake; never infer it silently. An intake-declared high-stakes signal forces `register=asserted` for the whole document. A content-resolved high-consequence landing forces asserted burden only at that cash-out span.

**Why type classification matters:** All later steps calibrate by type. Flagging "no objections engaged" in an AT1 explanatory piece is a false positive: explanations don't require objection handling. Flagging "no objections engaged" in an AT3 propositional piece is a critical failure: proposals demand it.

**Generative-register failure codes:**

| Code | Name | Description | Severity |
|------|------|-------------|----------|
| **GN0** | Register instability | The piece oscillates between offering a lens and asserting without signaling which burden applies. | Should-Fix; Could-Fix only for a local wobble with a legible dominant register |
| **GN1** | Inert lens | The lens decorates or relabels but reveals nothing that was unavailable without it. | Should-Fix when fertility is the operative success criterion; otherwise Could-Fix |
| **GN2** | Concealed cash-out | An assertion or prescription is delivered at full force under exploratory cover. Cross-reference DI4/FM-A13. | Never demoted; floor at the equivalent asserted-register finding |
| **GN3** | Broken lens | The metaphor or frame contradicts its own terms when extended. | Should-Fix |
| **GN4** | Borrowed authority unreturned | Imported technical precision does warrant work at a cash-out rather than illustrative work in the lens. | Floor at the equivalent asserted-register finding |

Under `register=generative`, WR/SM/BP findings on non-cash-out spans may calibrate to Could-Fix at Triage, with the finding's register, stance, verdict, and calibration effect recorded before the Deficit Lock. Definitional migration is the method of many lens essays: CL4 fires only when the migration is concealed and spent at a cash-out. GN2/GN4 and prescriptive cash-outs retain asserted burden.

**Calibration with F5:** If the Narrative Nonfiction Craft audit has already classified the piece as F5 (Argument with embedded narrative), AT-codes add precision about *what kind* of argument. F5 says "argument dominates"; AT-codes say what the argument asks the reader to do.

**Audience calibration codes:**

| Code | Name | Description |
|------|------|-------------|
| **AC0** | Audience dependency undeclared | The manuscript's success clearly depends on a specific audience calibration, but that dependency is not signaled anywhere |
| **AC1** | Shared-knowledge overestimate | The argument assumes warrants, definitions, or background facts the intended audience cannot safely be expected to supply |
| **AC2** | Hostile-audience underdefense | The piece targets a skeptical or adversarial audience but defends itself as if the audience were already friendly |
| **AC3** | Sympathetic-audience flattery drift | The piece leans on pre-existing agreement rather than supplying the structural support needed to actually inform or persuade |
| **AC4** | Compression-context mismatch | The draft uses short-form compression where the context requires fuller support, qualifier discipline, or alternatives analysis |

**Working note:** This step is not asking the reviewer to guess marketing demographics. It is asking what kind of reader the argument structurally imagines and whether the draft is built for that reader honestly.

---

### Step 2: Claim Ladder & Definition Stability (CL)

Extract the main claim (C0) and the subclaims (C1–C3) that must be true for C0 to hold. Also extract the stakes claim and track any key terms whose meanings carry argumentative force.

**Run on:** full draft (claims may be distributed, not concentrated in one section).

```
C0 (main claim): [one sentence — what the piece argues]

C1: [subclaim that must be true for C0 to hold]
C2: [subclaim that must be true for C0 to hold]
C3: [subclaim that must be true for C0 to hold]

STAKES: [why C0 matters — what's at risk if the reader ignores this]
  Stakes type: CONSEQUENTIAL / MORAL / EPISTEMIC / PRACTICAL

KEY TERMS:
  T1: [term] = [operational meaning in the draft]
  T2: [term] = [operational meaning in the draft]
```

**Constraints:**

- C0 must be extractable from the text as written, not inferred from implication. If the reader can't state the main claim after reading, the ladder has failed.
- Subclaims must be necessary links, not illustrations. Test: if C2 is false, does C0 still hold? If yes, C2 isn't a subclaim; it's color.
- Stakes must be stated or strongly implied by the text. If the reader finishes and can't answer "why should I care?" the stakes claim is missing.
- Key terms only need to be tracked when definitional pressure matters to the argument. Track terms like *freedom, harm, violence, safety, expertise, democracy, justice, community, efficiency, equity, consent* when they carry argumentative force.

**Stakes types:**

| Type | What's at Risk |
|------|---------------|
| **Consequential** | Bad things will happen (or continue happening) if the claim is ignored |
| **Moral** | A moral wrong is occurring or will occur |
| **Epistemic** | We're misunderstanding something important |
| **Practical** | A better approach exists and is being missed |

**Claim Ladder failure codes:**

| Code | Name | Description |
|------|------|-------------|
| **CL0** | No identifiable main claim | The piece has a topic but never commits to a position; the reader finishes without knowing what was argued |
| **CL1** | Claim unstable | Main claim shifts between sections without acknowledgment; the reader tracks different arguments in different parts |
| **CL2** | Subclaim gap | A necessary link in the chain is missing; C0 doesn't follow from C1–C3 even if all subclaims are true |
| **CL3** | Circular subclaim | A subclaim restates C0 in different words; the argument turns in a circle |
| **CL4** | Definitional smuggling | A key term shifts meaning across the piece and the shift does unacknowledged argumentative work |

**Why CL4 matters:** CL1 catches claim drift. CL4 catches a narrower and more common failure: the apparent continuity of a term disguises a shift in what is being claimed. The argument *looks* stable because the same word appears throughout, but the word has changed meaning between premise and conclusion. This is especially common around high-stakes conceptual terms in policy, advocacy, and scholarly writing.

**Output:** Claim ladder (C0 + C1–C3 + stakes + key terms) + CL-codes for any failures.

---

### Step 3: Support Map & Scheme Analysis (SM)

For each subclaim, identify what supports it, classify the support type, identify the reasoning pattern (scheme) the support employs, and test whether the support actually bears on the claim it's attached to.

**Run on:** body of the argument — track evidence as it appears.

```
C1: [subclaim]
  Support: [what the text offers as evidence]
  Support type: [REASON / EXAMPLE / DATA / AUTHORITY / EXPERIENCE]
  Scheme hint: [AUTHORITY / CONSEQUENCE / CAUSAL / ANALOGY / EXAMPLE / TESTIMONY / PRACTICAL REASONING / SIGN]
  Code: [SM-code or PASS]

C2: [subclaim]
  Support: [...]
  ...
```

**Support types:**

| Type | What It Is | Strongest For |
|------|-----------|---------------|
| **Reason** | Logical argument (if X then Y) | Universal and evaluative claims |
| **Example** | Particular instance or case | Existence claims ("this happens"), illustration |
| **Data** | Aggregate evidence, statistics, trends | Probabilistic and scope claims |
| **Authority** | Appeal to credible source or expertise | Contested factual claims |
| **Experience** | First-person testimony or lived observation | Testimonial and particularist claims |

**Common scheme hints:**

These are not mandatory taxonomic labels. Use them only when they sharpen diagnosis.

| Scheme Hint | Practical First Question |
|-------------|------------------------|
| **Authority** | Is this source credible on this exact point, in this exact domain? |
| **Consequence** | Are the predicted outcomes supported or merely asserted? |
| **Causal** | Is correlation, sequence, or anecdote being mistaken for cause? |
| **Analogy** | Are the compared cases relevantly similar in the ways that matter? |
| **Example** | Is the example representative or merely vivid? |
| **Testimony** | What can the witness establish directly, and where does interpretation begin? |
| **Practical Reasoning** | Why this proposal rather than alternatives? What about unintended consequences? |
| **Sign** | Does the symptom reliably indicate the claimed condition? |

**Support Map failure codes:**

| Code | Name | Description |
|------|------|-------------|
| **SM0** | Missing support | Subclaim is asserted without evidence; reader must take it on faith |
| **SM1** | Irrelevant support | Evidence offered doesn't bear on the subclaim; connection is associative, not logical |
| **SM2** | Support proves different claim | Evidence is relevant and real but supports a claim the text isn't making |
| **SM3** | Single-type dependence | All support is the same type (e.g., all examples, no reasons); argument collapses if that type is challenged |
| **SM4** | Evidence laundering | Secondary interpretation, summary, or mediated authority is treated as equivalent to primary evidence without acknowledging the interpretive chain |

**Output:** Support map per subclaim + scheme hints + SM-codes for any failures.

---

### Step 4: Warrant & Inference Bridge (WR)

For each subclaim's support, test whether the inferential bridge between evidence and claim is present, recoverable, or missing. This is the step that answers: *why* does this evidence support *this* claim? The SM step tells you *what* evidence exists. This step tests whether the logical connection holds.

**Run on:** every subclaim-support pairing from Step 3 where the scheme hint is non-trivial.

```
C1: [subclaim]
  Warrant: [the principle connecting evidence to claim]
  Warrant status: [EXPLICIT / RECOVERABLE / MISSING / CONTESTED]
  Backing: [PRESENT / THIN / ABSENT]
  Qualifier: [MATCHED / OVERCONFIDENT / UNDERCLAIMED]
  Defeater refs: [POPULATED BY STEP 6 — leave absent here; see the Step 6 per-warrant sweep]
  If testimony: [OBSERVATIONAL / INTERPRETIVE / REPRESENTATIVE / INSTITUTIONAL]
  Code: [WR-code or PASS]
```

**Warrant status classifications:**

| Status | Meaning |
|--------|---------|
| **Explicit** | The text states the connecting principle; the reader can evaluate it directly |
| **Recoverable** | The warrant is unstated but a reasonable reader sharing the intended audience's background can supply it without controversy |
| **Missing** | The inferential bridge requires importing a premise the text never gives; the argument functions only for readers who already agree |
| **Contested** | The warrant is stated or recoverable but relies on a principle many reasonable readers would reject; the argument acknowledges this or it doesn't |

**Backing and qualifier:**

- **Backing** is support for the warrant itself. When the warrant is contested ("punishment deters crime," "markets self-correct," "lived experience constitutes evidence"), the text must provide backing or flag the contest. When backing is absent for a contested warrant, the argument has a structural hole.
- **Qualifier** tests whether the conclusion's confidence level matches what the support chain can bear. "Therefore we must" requires stronger support than "this suggests." Qualifier mismatch is the most common form of unearned confidence in argument-shaped writing.

**Warrant and inference bridge codes:**

| Code | Name | Description |
|------|------|-------------|
| **WR0** | Warrant gap | Evidence is relevant, but the principle connecting it to the claim is not made explicit enough for the intended audience; the reader must independently supply the major premise |
| **WR1** | Missing backing | The draft supplies a warrant, but the warrant itself is contestable and receives no support |
| **WR2** | Scheme fragility | The support form is misused relative to the type of reasoning it performs (e.g., a causal claim supported only by temporal sequence; an analogy where the cases differ on the relevant dimension) |
| **WR3** | Qualifier mismatch | The confidence level of the conclusion exceeds what the support chain can bear; the hedge that should be present is absent |

**Working rule:** If the reviewer asks, "Why does this evidence support this claim?" and the answer requires importing a norm, causal principle, or conceptual premise the text never earns, the failure is WR0. If the evidence simply doesn't bear on the claim at all, the failure is SM1. WR0 is the more common and more insidious failure because the argument *looks* supported.

**Calibration by audience:** WR0 calibrates heavily by audience. A recoverable warrant for an expert audience (who share a disciplinary framework) may be a genuine gap for a general audience. A warrant that is uncontroversial for a sympathetic audience may be contested for a hostile one. Always check WR findings against the AC classification from Step 1.

**Output:** Warrant analysis per subclaim + WR-codes for any failures.

---

### Step 5: Burden of Proof, Scope & Comparative Burden (BP)

Test whether the evidence is commensurate with what the claim asks the reader to believe. This is the scope discipline step, where arguments most commonly fail without the writer noticing. Expanded in v2.0 to include comparative burden (are alternatives addressed?) and precision discipline (is the certainty earned?).

**Run on:** compare C0's scope against the aggregate support from Steps 3–4.

```
CLAIM SCOPE:
  C0 claims: [UNIVERSAL / PROBABILISTIC / LOCAL / NORMATIVE / DEFINITIONAL]

EVIDENCE SCOPE:
  Evidence supports: [UNIVERSAL / PROBABILISTIC / LOCAL / NORMATIVE / DEFINITIONAL]

COMPARATIVE BURDEN:
  Alternatives considered: [Y/N]
  Precision justified: [Y/N]
  Testimony overextended: [Y/N]

MATCH: [Y/N]
  If N: [describe the gap]
```

**Claim scope types:**

| Scope | What It Asserts | Evidence Required |
|-------|----------------|-------------------|
| **Universal** | "X is always/never true" | Systematic evidence + engagement with exceptions |
| **Probabilistic** | "X tends to..." / "In most cases..." | Aggregate data or representative sample + acknowledgment of variance |
| **Local** | "In this case..." / "Here..." | Case evidence sufficient; lower burden |
| **Normative** | "We should..." / "X ought to..." | Reasons + values + engagement with competing norms |
| **Definitional** | "X is properly understood as Y" | Conceptual argument + engagement with alternative definitions |

**Burden of Proof failure codes:**

| Code | Name | Description |
|------|------|-------------|
| **BP0** | Scope undeclared | Claim's scope is ambiguous; reader can't tell if "always," "usually," or "in this case" is intended |
| **BP1** | Evidence type mismatch | Evidence doesn't match claim type (e.g., normative claim supported only by data; universal claim supported only by one example) |
| **BP2** | Scope creep | Claim begins local but conclusion asserts universal; evidence doesn't travel the distance |
| **BP3** | Burden shift | Argument asserts others must disprove the claim rather than making the positive case; "no one has shown otherwise" substitutes for evidence |
| **BP4** | False precision | The draft performs certainty, granularity, or numerical rigor beyond what the evidence base supports |
| **BP5** | Missing alternatives | An AT3 proposal is not comparatively defended against plausible alternatives; the recommendation is argued in a vacuum |
| **BP6** | Testimonial overburden | Personal or local evidence is asked to carry a system-level or representative claim without additional support |

**Practical notes:**

- BP4 is highest-risk in policy briefs, data journalism, and academic writing. Reporting survey data to decimal precision, citing a single study as if it were a meta-analysis, or using percentage changes on small absolute numbers all trigger BP4.
- BP5 is the structural signature of advocacy that looks rigorous but isn't: the proposal is argued against the status quo only, never against the second-best alternative.
- BP6 is not hostility to testimony. It is a structural honesty check. A witness may establish that something happened, that it mattered, and that it illuminates a pattern. A witness cannot automatically establish the full causal or representative explanation of a system without further support.

**Output:** Scope comparison + comparative burden assessment + BP-codes for any failures.

---

### Step 6: Objection Handling & Dialectical Integrity (OB, DI)

Identify 2–4 objections the piece implicitly anticipates or conspicuously ignores. Test whether the engagement is real and whether the argumentative procedure is fair. This step catches both overt failures (objections not addressed) and covert failures (objections addressed but handled through procedurally dishonest moves).

**Run on:** full draft — look for concessive moves ("to be sure," "one might argue," "critics say"), anticipated counterarguments, and structural gaps where an obvious objection goes unaddressed.

**6a. Find the single strongest objection — by procedure, not preference.** The strongest objection is almost always **text-internal** (it turns the argument's own warrant, evidence, cure, or target against it), not the **canonical imported** counter from the surrounding debate. Do not just *prefer* the text-internal one — *derive* it, with two tests run in order:

- **Test B — Self-undermining derivation (run FIRST, to generate the candidate).** Take the argument's own central diagnosis, value, or proposed cure and ask: (i) does the proposed *remedy recreate* the very problem the argument diagnoses? (ii) is the standard *cure* for the harm the argument decries exactly the mechanism the argument *opposes*? (iii) does the conclusion *depend on* the thing it condemns? If any holds, that self-undermining objection is the strongest text-internal one — name it. (See FM-A20.)
- **Test A — Genre-genericity (decoy) filter (run on whatever you are tempted to call strongest).** Ask: *would this same objection apply, almost verbatim, to most arguments in this genre or on this topic?* (e.g., "but public safety" → any decarceration argument; "but cost / inefficiency / delay" → any pro-regulation or pro-labor argument; "but government failure" → any pro-intervention argument.) If yes, it is a **canonical-imported / decoy** objection: a hostile reader may raise it first, but it is **not** the text-internal strongest one. **Downrank it** (keep it in the inventory below, never as the strongest) — *unless Test B yielded nothing*, i.e. only when no text-internal objection exists may a genre-generic objection hold the strongest slot.

Then check scope: an objection to the proposed *alternative*, or to a *secondary* claim, is not a substitute for an objection to **C0 as actually argued**. Record the result as `STRONGEST OBJECTION` even if the piece never raises it, and let it anchor the inventory below. If a genre-generic objection occupies the strongest slot while Test B yielded a sharper text-internal one, fire **OB5**.

**6a-type. Type every objection record (R2).** Each objection carries `Target` (what it aims at), `Relation`, and `Basis` — two DECOUPLED axes plus an address:

- **`Relation`** is *what the objection targets*. **`WARRANT-DEFEATER`** — Toulmin's rebuttal — is an "unless …" exception on a specific `Cn.warrant`'s connecting principle, **holding that warrant fixed**: if the concern can be phrased as an "unless" clause appended to the warrant, it is a warrant-defeater; if it targets the claim's truth (`CLAIM-CHALLENGE`), the support (`EVIDENCE-CHALLENGE`), imports a competing value (`VALUE-CONFLICT`), or proposes a rival (`ALTERNATIVE` — the FM-A10 axis), it is not.
- **`Basis`** is *derivation provenance*, and it is NOT the same axis: `TEXT-INTERNAL` = derived from the argument's own warrant/grounds (the Test B discipline); `IMPORTED` = genre-generic/canonical (Test A's class). **A Test-B-derived objection is not automatically a WARRANT-DEFEATER**: a self-undermining remedy (Test B's canonical output — see FM-A20) is `TEXT-INTERNAL` but its Relation is `CLAIM-CHALLENGE` or `ALTERNATIVE`, because it attacks the remedy, not the warrant's bridge. Conversely a generic warrant exception ("unless the sample is biased") is `WARRANT-DEFEATER` + `IMPORTED`.
- Every `WARRANT-DEFEATER` records its `Condition` (the "unless …" clause). When `Basis: TEXT-INTERNAL`, it must also cite `Derivation anchors` — the warrant/grounds locations the condition is derived from. **Firewall discipline:** the condition is engine-surfaced, author-adjudicated *diagnosis* derived from the text's own machinery — never an invented counter-condition imported from outside the text, and never asserted as a validity rule the argument must satisfy. An `IMPORTED` warrant-defeater carries no anchors and is flagged non-adjudicable-by-anchors.

**6a-sweep. The per-warrant defeater sweep (R2).** After the strongest objection is settled, run Test B once more, scoped per warrant: *for each `Cn` in the §4 warrant map, ask under what conditions that warrant's connecting principle fails to carry, holding it fixed.* Record any **material** result as a typed objection record (`Target: Cn.warrant`, `Relation: WARRANT-DEFEATER`) — the core inventory stays 2–4 strongest, and sweep-found records append after them. Then write the §4 projection: for each claim, set its `Defeater refs:` line to the within-run pointers of its warrant-defeater records (`O1, O3` — pointers into *this run's* §6 list; they renumber across reruns and are documentation, not a stable key), or to **`NO-MATERIAL-TEXT-INTERNAL-DEFEATER-IDENTIFIED — <review_basis>`** when the sweep found nothing material. The review_basis must state the materiality bar applied ("no exception a MIXED-expertise reader would treat as live"); this is an open-world *search result* — never a warrant-soundness assurance, never an input to Warrant status or the Step 9 verdict. A claim whose line is absent was not swept — absence is *unknown*, not clean. Do NOT promote a defeater to a failure code: an ignored material defeater reaches the author through the ordinary objection pathway (`Engaged: N` + the OB codes — OB3 when central).

```
OBJECTION 1: [what the strongest objection would be]
  Target: [C0 | Cn | Cn.warrant | Cn.support | argument-wide]
  Relation: [WARRANT-DEFEATER | CLAIM-CHALLENGE | EVIDENCE-CHALLENGE | VALUE-CONFLICT | ALTERNATIVE]
  Basis: [TEXT-INTERNAL | IMPORTED]
  Condition: [WARRANT-DEFEATER only — the "unless …" clause]
  Derivation anchors: [TEXT-INTERNAL only — the warrant/grounds locations the condition is derived from]
  Engaged: [Y/N]
  If Y — quality: [SUBSTANTIVE / STRAWMAN / EVASION / COSMETIC]
  If N — severity: [MINOR / SIGNIFICANT / CENTRAL]
  Dialectical integrity: [FAIR / STARTING-POINT SMUGGLING / PSEUDO-RESOLUTION / AMBIGUITY / MOTTE-AND-BAILEY]
  Code: [OB-code, DI-code, or PASS]

OBJECTION 2: [...]
...
```

**Calibration by argument type:**

| Type | Objection Handling Expectation |
|------|------------------------------|
| **AT1 (Explanatory)** | Objection handling optional; alternative explanations are the relevant "objections" |
| **AT2 (Evaluative)** | Must address alternative criteria or alternative applications of stated criteria |
| **AT3 (Propositional)** | Must address strongest available counter-proposal and implementation risks |
| **AT4 (Testimonial)** | Must acknowledge limitations of testimony as evidence; alternative interpretations of the same experience |

**Objection Handling failure codes:**

| Code | Name | Description |
|------|------|-------------|
| **OB0** | No objections engaged | Argument proceeds as if no reasonable person could disagree; closed to challenge |
| **OB1** | Strawman | Objection addressed is the weakest available version; reader recognizes the mismatch |
| **OB2** | Evasion | Objection named but not answered; text acknowledges disagreement then moves on without engaging |
| **OB3** | Central objection unaddressed | The hardest counterargument — the one a well-informed skeptic would raise first — is missing entirely |
| **OB4** | Concession without cost | The piece performs concession language but the concession changes nothing; the argument proceeds exactly as if the objection were never raised |
| **OB5** | Decoy strongest objection | The inventory engages a plausible objection, but the genuinely strongest, most load-bearing objection (the one that turns the argument's own central warrant, evidence, or target against it) is neither named nor engaged. Distinct from OB3: OB3 = the strongest objection is identified but unaddressed; OB5 = it is *misidentified*, a weaker or merely canonical objection having taken its place. OB5 is a finding about **the piece's** objection handling, not about your own analysis. **Engine self-guard (process, not a code about the piece):** if the objection *you* named as strongest passes the genre-genericity test (6a Test A) and you skipped the self-undermining derivation (6a Test B), you are about to hand back a decoy — re-run Test B first. Having correctly identified the strongest (text-internal) objection, code the *piece's* handling of it: **OB3** if the piece leaves that objection unaddressed, **OB5** only if the piece itself engages a weaker/canonical objection in its place |

**Note on AT1:** For explanatory arguments, OB0 is not automatically a failure. If the explanation is accurate and clear, absence of objection handling is acceptable. For all other argument types, OB0 is diagnostic.

**Dialectical Integrity codes:**

| Code | Name | Description |
|------|------|-------------|
| **DI0** | Starting-point smuggling | The argument treats a contested premise, value, or definition as if everyone already accepts it |
| **DI1** | Unexpressed-premise evasion | The draft relies on an unstated premise, then avoids responsibility for it when pressure arises |
| **DI2** | Pseudo-resolution | The piece talks as if a dispute has been settled when it has only been asserted over |
| **DI3** | Ambiguity doing argumentative work | Key language remains strategically vague so the conclusion can feel stronger than any single precise version would support |
| **DI4** | Motte-and-bailey drift | The draft alternates between a narrower defensible claim and a broader ambitious claim without acknowledging the shift |

**Working rule:** Mentioning disagreement is not the same thing as earning argumentative trust. OB4 and the DI family exist to catch drafts that *sound* fair without actually carrying the burden of fairness.

**Output:** The named STRONGEST OBJECTION (6a) + objection inventory (2–4, typed per 6a-type, plus any sweep-found WARRANT-DEFEATER records) + engagement quality + the §4 `Defeater refs:` projection (6a-sweep) + OB-codes + DI-codes for any failures.

---

### Step 7: Narrative-as-Evidence & Testimonial Position (NE)

For each narrative vignette, case study, or personal anecdote embedded in the argument, identify what claim it supports, whether it's doing argumentative work or serving as decoration, and what testimonial position the narrator occupies.

**Run on:** identify all narrative segments (scenes, anecdotes, case examples, personal testimony) within the argument. For each:

```
Vignette [X]: [description — location in draft]
  Attached to: [which subclaim does this support?]
  Function: [ILLUSTRATION / EVIDENCE / EMOTIONAL ANCHOR / UNATTACHED]
  Witness position: [OBSERVATIONAL / PARTICIPANT / INTERPRETIVE / REPRESENTATIVE / INSTITUTIONAL]
  Code: [NE-code or PASS]
```

**Vignette function types:**

| Function | What It Does | Argumentative Status |
|----------|-------------|---------------------|
| **Illustration** | Makes an abstract claim concrete; reader "sees" what the claim means | Useful but not probative — removing it weakens clarity, not validity |
| **Evidence** | Establishes that a claimed phenomenon exists or occurs | Probative — removing it weakens the support chain |
| **Emotional anchor** | Creates reader investment in the argument's stakes | Motivational — removing it reduces urgency but doesn't affect logic |
| **Unattached** | Powerful writing with no identifiable argumentative function | Decoration — may actively mislead by creating emotional conviction without logical connection |

**Witness position types:**

| Position | What the Narrator Can Establish | Structural Limit |
|----------|-------------------------------|-----------------|
| **Observational** | What was directly seen, heard, or experienced | Cannot establish cause, frequency, or system-level pattern |
| **Participant** | What it was like to be inside the experience | Cannot establish how representative the experience is |
| **Interpretive** | What the experience means in a broader context | Carries AT2/AT3 burden — requires support beyond the experience itself |
| **Representative** | What the experience tells us about a population or system | Carries high burden — cross-check BP6 |
| **Institutional** | What the institution's processes, incentives, or failures produce | Carries the authority of position but also the blindness of position — cross-check WR1 |

**Narrative-as-Evidence failure codes:**

| Code | Name | Description |
|------|------|-------------|
| **NE0** | Unattached vignette | Narrative is powerful but doesn't support any identifiable subclaim; it creates feeling without doing argumentative work |
| **NE1** | Vignette as substitute | Narrative replaces argument rather than supporting it; the vignette IS the entire case for a subclaim, with no reason or evidence alongside |
| **NE2** | Vignette-claim mismatch | Narrative supports a different claim than the one it's placed near; evidence is real but misrouted |
| **NE3** | Emotional override | Narrative's emotional power masks a logical weakness in the support chain; removing the vignette reveals the gap |

**Cross-reference rule:** When a vignette is doing interpretive or representative work, cross-check WR0, BP6, and AC1. Many testimonial failures are not failures of truthfulness. They are failures of argumentative travel distance: the witness told the truth, but the text asked that truth to carry more than it can structurally support.

**Cross-reference with Franklin Steps 1–4:** When this audit runs on Classification 3 material, Franklin Steps 1–4 run on each embedded narrative segment separately to verify internal spine. The NE-codes test the *argumentative function* of those segments — whether they're doing structural work in the argument, not just whether they have internal narrative coherence.

**Output:** Vignette inventory + function classification + witness position + NE-codes for any failures.

---

### Step 8: Cross-Section Integrity

Certain failures are invisible within any single section and only become visible when you compare across the full document. This step specifically targets dynamic failures that accumulate over distance.

**Run on:** full draft, comparing sections against each other.

**Track the following across all major sections:**

**8a. Claim drift:** State C0 as it appears in each major section. If the formulation changes, note where and how. A gradual broadening that the text never acknowledges is CL1. A stable-looking claim where a key term has silently shifted meaning is CL4.

**8b. Qualification erosion:** Track hedging and confidence language from introduction through conclusion. If qualifiers ("may," "suggests," "in some cases") appear in early sections but disappear by the conclusion, the final claims carry confidence the evidence chain never earned. This is WR3 operating dynamically.

**8c. Scope accumulation:** Track the scope of evidence in each section against the scope of the conclusion. If each section's evidence is local but the conclusion asserts something universal, the failure is BP2. The individual sections each look honest; the aggregate doesn't.

**8d. Definition stability:** Track the key terms identified in Step 2 across sections. If T1 means one thing in paragraph 3 and something broader in paragraph 18, flag CL4 with the specific locations.

**8e. Alternatives gap:** For AT3 arguments, check whether alternatives are addressed anywhere across the full piece. BP5 should fire from the whole-document perspective, not just within individual sections.

**This step does not introduce new codes.** It uses CL1, CL4, WR3, BP2, BP5, and AC1 in cross-section comparison. Its value is the *method* — requiring the reviewer to read across sections rather than diagnosing each section in isolation.

**Output:** Cross-section comparison findings + codes with specific locations.

---

### Step 9: Distinguish Protocol

After the full diagnostic runs, this terminal step asks: did this text fail because its reasoning does not **warrant** its conclusion, or because it's operating in an argument form that the previous steps aren't calibrated for? The verdict is about *warrant* — whether the inference holds on the text's own terms — not about whether the premises are true (that is the separate premise-plausibility axis; see below).

**Triage/lock boundary:** rhetorical stance triage runs earlier, when Triage assigns severity, before the Deficit Lock. Step 9 may surface new stance evidence but may not silently soften a locked finding. Any post-lock change uses only the existing ID-scoped `softness-downgrade` override plus its Severity Calibration entry. Rhetorical stance never applies to the GT8 premise-plausibility axis: it classifies an argumentative move, never whether a premise is true. See `rhetorical-stance-triage.md`.

**The cultural charity principle:** When a text fails Western structural expectations, presume unconventional form before diagnosing structural failure. Test whether the form is doing real argumentative work. Only return **UNWARRANTED** when the form itself blocks evaluability.

**Three-way warrant verdict:**

*(Migration note: earlier versions labeled these Structurally Sound / Unconventional-but-Effective / Unsound. The verdict axis is renamed to the warrant vocabulary — Argument Benchmark GT schema v0.2.0 — because the audit measures inferential **warrant** (whether the reasoning supports the conclusion on the text's own terms: Local Relevance + Local Sufficiency), not **soundness** (which additionally requires true premises — a judgment the Firewall forbids). Premise acceptability is surfaced separately as non-adjudicative flags. Historical scorecards may retain the old labels.)*

| Warrant verdict | Meaning | Action |
|----------------|---------|--------|
| **WARRANTED** | The claim, support, scope, and disagreement handling remain evaluable by whatever form the piece uses, even if codes (including Hard-Gate codes) fired. The reasoning warrants the conclusion; the codes are its repair agenda | Report all codes as issued, ranked by severity. The priority repair is the highest-severity soft spot, not an UNWARRANTED verdict |
| **UNCONVENTIONAL-BUT-WARRANTED** | The piece does not follow thesis-evidence-objection form, but a careful reader can recover and test the argument | Retroactively downgrade form-dependent failures (missing thesis sentence, absent formal concession paragraph, non-linear structure) to advisory notes rather than structural diagnoses |
| **UNWARRANTED** | The reader cannot reliably identify, evaluate, or pressure the argument regardless of form | Report all codes as issued; note that form does not explain the failures |

**Decision tests for classification:**

| Test | Diagnostic Question |
|------|-------------------|
| **Claim-accessibility** | Can a careful reader state the main claim or worldview after reading? |
| **Evidence-evaluability** | Can the reader identify what supports the claim and independently assess its adequacy? |
| **Bridge-recoverability** | Can the inferential bridge be recovered without importing a private argument the draft never gives? |
| **Scope-honesty** | Does the manuscript signal how far its evidence travels? |
| **Objection-awareness** | Does the manuscript show that alternative positions exist and matter? |
| **Form-fit** | Is the unconventional form doing real argumentative work, or shielding weakness? |

**Warrant-verdict decision rule (apply in order):**

1. **Default to WARRANTED.** Firing codes, including Hard-Gate codes, does not by itself make an argument UNWARRANTED. Codes are the repair agenda; the warrant verdict is a separate, higher-order judgment about evaluability. (Hard-Gate names a code *family*; Must-Fix is a severity *tier* a code reaches only through the Severity Floor — see §Severity definitions.)
2. **UNWARRANTED requires a defeat, not a weakness.** Return UNWARRANTED only when at least one decision test above fails as a *defeat*: the reader genuinely cannot identify the claim, find or assess the evidence, recover the inferential bridge, judge the scope, or see that objections exist. A recoverable-but-unstated warrant, a strong objection thinned rather than absent, scope tightened toward the conclusion, or an alternative gestured at but not engaged are soft spots in a warranted argument, not structural breaks.
   - **2a. The uncompared recommendation is a defeat, not a soft spot (AT3 only).** For an argument whose C0 is a *recommendation to act* (AT3 — "X should do Y"), the comparative dimension is **constitutive of the claim, not peripheral to it**: a reader cannot evaluate "do Y" without "rather than the alternatives that target the same goal." So when an AT3 recommendation discharges *none* of its comparative burden — **BP5** primary (no alternative engaged at all) **+ OB3** (the dominated-alternative / opportunity-cost objection wholly unaddressed), with no costing or funding mechanism — that is a **defeat** under decision test two (Evidence-evaluability) above: a recommendation's support *is* its comparative case, so with none discharged the reader cannot assess the adequacy of what supports "do Y" — it is *not evaluable as a recommendation* — and the verdict is **UNWARRANTED** (FM-A10, The Uncompared Proposal). (The claim itself stays statable, so decision test one / Claim-accessibility is *not* the failing test here.) This is the one place rule 2's "an alternative gestured at but not engaged is a soft spot" does **not** apply — and only here, because for a recommendation the comparison is the test, not an enrichment of it. **Scope guard — the defeat is for *zero comparison*, not *bad comparison*:** the line is *wholly absent* (defeat → UNWARRANTED) vs. *partially discharged* (an alternative named, costed, or weighed even thinly → soft spot → WARRANTED, per rule 2). **Naming *any* alternative at all counts as partially discharged — including a single one, and including a weak, strawmanned, or adversarially-framed alternative** (e.g., presenting only an extreme foil — "the only other option is X" where X is a caricatured or discredited position). That is a recommendation that engages one alternative badly → a Should-Fix in a *warranted* argument, not a defeat. The defeat (→ UNWARRANTED) requires the comparative dimension to be *wholly absent*: no alternative named, gestured at, costed, or even strawmanned anywhere in the text. **Do not read "the named alternative is a strawman / unfairly dismissed / not a serious option" as "no alternative engaged"** — the fairness and quality of the comparison is a separate Should-Fix (raise BP/OB severity), never the trigger for this defeat. A recommendation that engages one alternative badly is a Should-Fix in a warranted argument; a recommendation that engages *none at all* is UNWARRANTED *as a recommendation*. **Anti-gaming clause:** naming an alternative disables only the *automatic* FM-A10 defeat — it does not immunize the argument. A *merely decorative* foil (named, but with no comparative substance anywhere — no mechanism, criteria, costs, or tradeoff reasoning) can still be classified UNWARRANTED through the **general** evaluability test (rule 2 / decision test two) as an ordinary recommendation-evaluation failure — *not* via this AT3 automatic trigger. Bright line: any named/gestured alternative removes the automatic 2a defeat; egregious token-foil cases route through ordinary evaluability. This carve-out fires for AT3 recommendations only — never for descriptive/explanatory/interpretive theses, where rule 2 stands unmodified. **Primacy under co-present defeats — the warrant leap leads (which failure is the *primary locus*).** Rule 2a settles the *verdict* (UNWARRANTED); it does **not** settle the *primary structural break* through the "name the first defeated test" ordering (rule 2 / Step 9 / the Final Diagnostic Question). That ordering lists Evidence-evaluability (test two) before Bridge-recoverability (test three), so on its own it would rank the FM-A10 comparative defeat — which fires *at test two* — ahead of a co-present causal warrant leap. **Override that ordering here:** when the FM-A10 zero-comparison defeat co-occurs with a **WR0 warrant leap that is MISSING (not RECOVERABLE) on C0's *causal / diagnostic* bridge** — the recommendation's *problem* is not warranted ("the harm rose when X appeared" ⇒ "X *caused* the harm," confounders unaddressed), a decision-test-three defeat in its own right — then **the causal warrant leap is the primary structural break and FM-A6 (The Warrant Leap) is the primary pattern**, and **FM-A10 is co-reported as a subordinate defeat**, not the headline. The reason is a logical dependency, not the table order: a recommendation to "do Y about problem P" rests on **L1** (P is real and attributable to the thing Y targets) and **L2** (Y beats the alternatives that address P); **L2 presupposes L1** (you cannot weigh "ban X vs. lighter measures" until "X causes the harm" is warranted), so a defeat of L1 is *upstream* of a defeat of L2 — the same dependency the repair order encodes (warrant before remedy-defense). The verdict is UNWARRANTED under either failure; the *locus* is the upstream one. **Negative test (keeps the ordinary case FM-A10-primary):** this override fires **only** when a genuine test-three MISSING causal/diagnostic warrant leap co-defeats. An AT3 recommendation whose problem is adequately warranted (or whose only WR0 is incidental / RECOVERABLE) and whose *sole* defeat is the missing comparison keeps **FM-A10 as the primary pattern** (the ordinary Uncompared Proposal — e.g. a fare-free-transit brief whose benefits are evidenced but whose alternatives are never weighed): there is no upstream L1 defeat to take primacy.
3. **UNCONVENTIONAL-BUT-WARRANTED** applies when the *form* is non-standard but a careful reader can still recover and test the argument (downgrade form-dependent failures to advisory).
4. **When in doubt between a soft spot and a structural break, default to WARRANTED** and carry the issue as the priority Should-Fix repair. Over-firing an UNWARRANTED verdict on a competent argument is as serious an error as missing a real break.

**The Step-9 Final Diagnostic Question:**

> Can a careful reader who does not already agree with this argument identify what is being claimed, evaluate the evidence, test the inferential bridge, judge the scope, and determine whether disagreement has been handled honestly?

If yes: **WARRANTED**, regardless of whether the premises are ultimately true. If no: name the first defeated test and return **UNWARRANTED** — *but* when the FM-A10 comparative defeat (test two) co-occurs with a test-three MISSING causal/diagnostic warrant leap on C0, the *primary locus* is the upstream warrant leap (FM-A6), not FM-A10: see rule 2a's primacy-override. Then, separately, flag any contestable or unearned premises (see below).

**Premise-plausibility flags (the second axis — never a verdict).** The warrant verdict answers whether the reasoning warrants the conclusion on the text's own terms (the inference axis — Local Relevance + Local Sufficiency). It deliberately brackets whether the premises are *true* (Local Acceptability); the Firewall forbids the engine from adjudicating premise truth. A premise can be contestable, overloaded, or doing unearned work while the inference from it remains valid. When that is the case, register a **premise-plausibility flag** — never a second verdict. Each flag names the premise in the manuscript's own terms and its location, its load-bearing role, one or more flag types (`CONTESTABLE`, `UNEARNED`, `OVERLOADED`, `EXTERNAL-VERIFY`, `DEFINITIONAL` — joined by ` + ` when several apply, or the standalone `NONE_REGISTERED`), why a careful reviewer would not let it pass silently, the Firewall boundary (what is *not* being adjudicated), and the repair implication (support / qualify / disclose / compare / define / cite). A flag never changes the warrant verdict by itself; only a structural/warrant defeat produces `UNWARRANTED`. Two boundary rules: **(a)** the automatic FM-A10 defeat is never a premise flag — do not convert a BP5/OB3 comparative-burden defeat into a `CONTESTABLE` flag on the uncompared premise (the defeat is the warrant verdict's business, and the codes already carry it); **(b)** under `UNCONVENTIONAL-BUT-WARRANTED`, flags attach to the premises of the **recovered** argument, not the surface/ironic one — flagging a satire's deliberately monstrous literal premises is the same category error as evaluating the literal proposal.

**Boundary example (valid inference, contestable premise).** "The moon is made of cheese; cheese is edible; therefore the moon is edible" is **WARRANTED** — the inference holds on its own terms — while its load-bearing premise is flagged:

```
Warrant verdict: WARRANTED
Premise-plausibility flags:
  P1 | "the moon is made of cheese" | ground | CONTESTABLE + EXTERNAL-VERIFY
  Firewall boundary: The engine flags the premise as contestable and load-bearing; it does not adjudicate lunar composition.
```

That is the split: a warranted inference can coexist with a flagged premise. The engine reports both; it never collapses the flag into the verdict. If no premise is flagged, the flags line reads `NONE_REGISTERED` and states plainly that this is not a truth clearance.

**Recognized unconventional argument forms:**

- **Narrative argumentation:** Conclusion emerges through juxtaposition of events and thematic reflection rather than explicit thesis. Common in personal essays, literary journalism, Indigenous storytelling traditions.
- **Dialogical argumentation:** Meaning is co-constructed through exchange rather than delivered as monologue. Common in Socratic method, interview-structured arguments, co-authored position papers.
- **Circular or recursive argumentation:** The argument covers the same thematic ground repeatedly at increasing depth, operating as a spiral rather than a line. Common in Eastern philosophical traditions, meditative essays, some Indigenous knowledge systems.
- **Nyaya logic:** Five-member syllogism (thesis, reason, universal rule with example, application, conclusion) that insists on empirical grounding. Blends deduction and induction.
- **Prophetic address and call-and-response:** Draws the audience into participatory agreement, then reverses to expose complicity or demand moral awakening. Common in African-American rhetorical traditions, religious discourse, ancient Hebrew disputation.
- **Testimonial accumulation:** Multiple first-person accounts build a case through volume and pattern rather than through explicit claim-evidence structure. Common in advocacy, documentary, legislative testimony.

**Practical rule:** Do not fail a personal essay, testimony sequence, dialogic structure, or recursive essay merely because it does not announce a thesis sentence early. Fail it when the form blocks evaluability.

**Output:** Warrant verdict + decision test results + premise-plausibility flags + any retroactive adjustments to prior codes.

**Charity-gate (Deficit Lock).** Retroactively downgrading a prior code to an advisory note via the cultural-charity principle is a charity downgrade: legitimate, but it must be *legible*. Record the original code and the downgrade rationale so the deficit carries forward to synthesis as a marked adjustment rather than a silent disappearance — at synthesis it is locked at Triage and any further softening requires a body override marker (`core-editor/references/output-policy.md §Severity Honesty Protocol → Deficit Lock`). Never use the Distinguish Protocol to avoid recording the original finding.

---

## Common Patterns

Nineteen named diagnostic patterns. The first five are preserved from v1.0. Patterns 6–19 are new in v2.0. Organized by failure cluster (see Failure Cluster Taxonomy below).

### Architectural Failures

These indicate the basic argument structure is absent or disguised. Detectable early; often the audit can stop here.

**FM-A1: The Drive-By Thesis**
Signature: CL0 or CL1 + SM0 across multiple subclaims.
The writer has many interesting things to say. But there's no stable main claim. Each section makes a different point; the piece is a tour of the writer's thinking, not an argument. Common in smart writers who assume their conclusion is self-evident.

**FM-A3: The Persuasion Machine**
Signature: OB0 or OB4 + NE1 + NE3.
No objections addressed, and narrative does the heavy lifting where reasons should. Each vignette is devastating; together they create conviction without justification. Removing the vignettes reveals there's no argument underneath. Common in advocacy journalism, fundraising appeals, and op-eds written under deadline pressure.

**FM-A5: The Hidden Argument**
Signature: AT0 + piece classified as narrative (F1/F2/F3) by Nonfiction Craft audit but functioning as argument.
The piece presents itself as story, inquiry, or profile, but is actually arguing a position. The argument is embedded in selection, framing, and juxtaposition rather than stated as claim/evidence. Not inherently a flaw; narrative argument is a legitimate form. But the disguise prevents the reader from evaluating the claims on argumentative terms. Apply Step 9 (Distinguish) before escalating.

### Relational Failures

These emerge between codes, not within them. A text can pass every individual step and still harbor these failures because the problem lives in the relationship between evidence and claim, or between different sections' claims.

**FM-A6: The Warrant Leap**
Signature: WR0, sometimes with otherwise clean SM passes.
The argument looks supported until the reader asks *why* the evidence should carry this conclusion at all. The data is real, the claim is reasonable, but the connecting principle is absent. The argument functions only for readers who already agree. This is the single most common sophisticated failure in argument-shaped writing.

**FM-A7: Definitional Smuggling**
Signature: CL4, often with DI3.
A key term broadens, narrows, or shifts register across the piece while pretending to stay stable. The argument appears continuous because the same word appears throughout, but the word changed meaning between premise and conclusion. The shift does the argumentative work that evidence should.

**FM-A12: Emotional Inflation**
Signature: NE3 + BP2 + stakes disconnect (stakes claim at existential register, evidence at local scale).
The stakes claim is elevated to a register of existential or civilizational urgency that the localized evidence cannot support. This can happen without vignettes, through rhetorical escalation in the framing itself. Not the same as passionate writing, which may be fully earned. The test: remove the stakes language and read the evidence alone. If the evidence supports a local, moderate conclusion but the stakes claim asserts civilization-level consequences, the inflation is present.

**FM-A13: Structural Motte-and-Bailey**
Signature: DI4 + CL1, often with clean local SM/WR passes.
The argument oscillates between a highly defensible modest claim (the motte) and a controversial ambitious claim (the bailey). Evidence supports the motte; the conclusion asserts the bailey. Under pressure, the argument retreats to the motte. This is not drift (CL1); it's strategic oscillation. Distinguish by checking whether the text defends the ambitious version or only the modest one.

**FM-A15: Intermediate Outcome Fallacy**
Signature: WR2 + BP1.
The argument proves that intervention A affects mediator variable B, then assumes without proof that B guarantees outcome C. The causal chain has a missing link disguised by the apparent rigor of the A→B proof. Common in policy writing and social science. The editorial instruction: the text must prove B→C independently or acknowledge the gap.

**FM-A17: Anecdote-to-Principle Leap**
Signature: BP6 + WR0 or BP1.
The gap between "I saw this" and "this is how it works" is treated as self-evident. The anecdote is true, the principle may be true, but the text supplies no bridge between them. The experience is asked to carry representative or explanatory weight it cannot structurally support. Common in advocacy journalism and legislative testimony. Cross-reference: NE1 when the anecdote is the *only* support for a subclaim.

**FM-A20: Self-Undermining Remedy**
Signature: OB3/OB5 + DI (often DI2), in an otherwise competent argument.
The proposed remedy reintroduces, or structurally depends on, the very condition the argument diagnoses as the problem; or the standard cure for the harm the argument decries is exactly the mechanism it opposes. The strongest objection is therefore text-internal — the argument defeats itself on its own terms. Two templates: (a) *the remedy recreates the diagnosed problem* — participatory safeguards proposed against procedural veto points themselves reintroduce veto points; (b) *the cure is the condemned mechanism* — a brief that decries discretionary, arbitrary enforcement proposes individualized treatment that requires more of exactly that discretion, when standardization is the classic constraint on it. Distinct from FM-A10 (Uncompared Proposal — whether *alternatives* are weighed) and FM-A13 (Structural Motte-and-Bailey — *claim oscillation*). Surfacing it is the job of Step 6's 6a self-undermining derivation (Test B).

### Quality Failures

A code fires as present/pass, but the pass threshold is wrong. Evidence exists but is laundered. Concessions happen but are costless. Authority is cited but overreaches. These require the audit to test *quality* of passes, not just presence.

**FM-A8: False Precision Theater**
Signature: BP4, often with WR3.
The draft performs confidence, quantification, or causal precision it has not earned. Survey data reported to decimal precision on a 5-point Likert scale. A single study cited as if it were a meta-analysis. Percentage changes calculated on absolute numbers too small to be meaningful. The precision creates a veneer of rigor that masks empirical uncertainty.

**FM-A9: Concession Without Cost**
Signature: OB4, often with OB2.
The manuscript nods to disagreement but the concession changes nothing. The argument proceeds exactly as if the objection were never raised. The claim's scope is not narrowed. The qualifier is not adjusted. No subclaim is modified. The concession is rhetorical theater: it exists to make the writer *look* fair, not to actually integrate disagreement.

**FM-A11: Evidence Laundering**
Signature: SM4, often with AC1 for general audiences.
Interpretation, summary, or mediated authority is treated as if it were direct evidentiary ground. The text cites a secondary source's reading of a study as if it were the study itself. The inferential chain passes through an unexamined intermediary. For expert audiences this may be transparent; for general audiences it creates the impression of primary evidence where none exists.

**FM-A14: Epistemic Erasure**
Signature: SM3 (authority-only) + AC0 or AC1.
The argument relies exclusively on institutional, quantitative, or detached authority while structurally silencing the testimonial lived experience of populations directly impacted by the claim. The support map looks adequate until you ask *whose knowledge counts*. In mental health policy, this is psychiatric authority without patient voice. In criminal justice, this is recidivism data without reentry testimony. In education, this is test scores without student experience.

**FM-A19: Authority Overreach**
Signature: WR2 + SM1 (misrouted authority).
An expert whose credentials are in domain X makes claims in domain Y, leveraging credibility earned in one field to make claims in another. The text presents the authority as if domain expertise were fungible. An economist testifying about psychology. A clinician making policy recommendations. A legal scholar making empirical claims. The authority is real but structurally mismatched to the claim.

### Dynamic Failures

These accumulate across sections and are invisible in any single section. They require the cross-section tracking in Step 8.

**FM-A2: The Evidence Pile**
Signature: SM passes (evidence is present and relevant) + CL2 (subclaim gap) or BP2 (scope creep).
Lots of evidence, correctly matched to subclaims, but the subclaims don't add up to the main claim, or the evidence supports a narrower conclusion than the text asserts. The argument looks rigorous from inside any single section. The structural failure is in the connections between sections. Common in policy writing and data-driven journalism.

**FM-A4: Scope Inflation**
Signature: BP0 (scope undeclared) + BP2 (scope creep).
The evidence supports "in this case" or "sometimes." The conclusion asserts "always" or "we must." The gap is invisible to the writer because they've lived with the material long enough that the particular feels universal. Nearly universal in first drafts. Often the easiest pattern to fix.

**FM-A10: The Uncompared Proposal**
Signature: AT3 + BP5, frequently with OB3.
The proposal may be attractive in isolation, but the reader cannot judge it against plausible alternatives. The argument is defended against the status quo only. The second-best alternative is never named, let alone engaged. Common in policy briefs, op-eds advocating specific interventions, and grant proposals.

**FM-A16: Qualification Erosion**
Signature: WR3 operating dynamically across sections.
Hedging language appears in early sections ("may," "suggests," "in some cases") but progressively disappears. By the conclusion, the claims carry certainty the evidence chain never earned. The writer hasn't consciously strengthened the claims; the qualifiers simply evaporated across distance. Requires Step 8 tracking: compare the confidence language in the introduction against the confidence language in the conclusion.

**FM-A18: Implementation Blindspot**
Signature: AT3 + clean CL/SM/WR/BP on the problem and principle, but total absence of execution analysis.
The proposal proves the problem exists and argues the principle compellingly. But it never addresses how the proposed solution would actually work: cost, timeline, institutional capacity, political feasibility, unintended consequences. The argument is complete on paper and useless in practice. Common in advocacy, academic policy proposals, and open letters. The editorial instruction is not to write the implementation plan, but to diagnose that one is missing.

---

## Failure Cluster Taxonomy

The 20 patterns cluster into four diagnostic types that tell the reviewer *how* to find them:

| Cluster | What It Means | Detection Method | Patterns |
|---------|--------------|-----------------|----------|
| **Architectural** | The basic argument structure is absent or disguised | Detectable in Steps 1–2; often the audit can stop here | FM-A1, FM-A3, FM-A5 |
| **Relational** | The failure lives between codes, not within them | Compare findings across steps; look for disconnects between what individual steps return | FM-A6, FM-A7, FM-A12, FM-A13, FM-A15, FM-A17, FM-A20 |
| **Quality** | A code fires as pass but the pass quality is inadequate | Re-examine passes with higher resolution; test not just presence but adequacy | FM-A8, FM-A9, FM-A11, FM-A14, FM-A19 |
| **Dynamic** | The failure accumulates across sections and is invisible locally | Step 8 cross-section tracking; compare beginning against end | FM-A2, FM-A4, FM-A10, FM-A16, FM-A18 |

**Why this matters for the reviewer:** Different clusters require different reading strategies. Architectural failures are obvious on first pass. Relational failures require comparing outputs across steps. Quality failures require re-reading passages that initially looked adequate. Dynamic failures require reading the document beginning-to-end with tracking in mind. The cluster tells the reviewer where to look.

---

## Genre & Audience Calibration

### By Argument Form

**Lens Essay / Exploratory Essay:** AT5 is primary, often with an AT2/AT3 tail. Load-test the journey for coherence and fertility and every cash-out at asserted burden. GN2/GN4 are signature risks. Definitional migration is not automatically CL4; it becomes a defect when concealed at the landing. WR0 on analogy spans may calibrate to Could-Fix, with the ledger naming what a reader who rejects the analogy loses. Vignettes are lens material rather than evidence until a cash-out spends them. Apply Distinguish aggressively to objections aimed at the lens, never to evade objections aimed at a landing.

**Op-ed / Column (< 1,500 words):** Claim ladder must be tight: one C0, one or two subclaims. Support may be light but must be present. Compression is not an excuse for WR0, BP2, or OB4. AC4 is the high-risk code when short-form conventions are used to dodge necessary burden. NE-codes are high-value: at this length, a single vignette carries enormous weight.

**Policy Brief / Memo:** AT3 is the default expectation. Full support map required. BP5 is critical: alternatives must be addressed, even if briefly. BP-codes are critical because the audience will act on the argument. Objection handling must address the strongest counter-proposal. Vignettes function as illustration, not evidence (the data should do the evidential work). BP4 is high-risk when quantitative claims exceed the methodology's precision.

**Testimony (written or oral):** AT4 is primary. Claim ladder may be implicit (the claims emerge from the testimony). Observational authority is strong; interpretive and representative claims require WR and BP scrutiny. BP6 and AC2 are high-value checks in legislative, legal, and adversarial settings. The AT4 burden split (observational/interpretive/representative) is where most testimonial failures live.

**Academic / Scholarly Article:** Full diagnostic applies at highest standard. CL0 is disqualifying. SM3 (single-type dependence) is a common weakness. SM4 and WR1 are especially useful because scholarly prose often looks rigorous while quietly relying on definitional or literature-consensus shortcuts. OB-codes are critical: the audience expects adversarial engagement with the literature. BP-codes: scope discipline is the mark of mature scholarship; scope inflation is the mark of student work. NE-codes rarely apply, but when they do (case studies in applied fields), NE1 and NE3 matter. Genre-structure signal (see the genre layer + the Reviewer-Anticipation Lens below): the required skeleton is **contribution claim · related-work positioning · method/evidence · limitations/scope** — a contribution claim with no related-work positioning is the academic analogue of a bare assertion (novelty claimed without locating the gap).

**Personal Essay (argument-shaped):** AT4 or AT2 typically. The claim ladder may be implicit, emerging through reflection rather than stated as thesis. This is legitimate. Apply CL-codes loosely: flag CL0 only if the reader genuinely can't identify what the essay is about, not merely because the claim isn't stated as a sentence. OB-codes: personal essays may legitimately decline to engage objections from outside the essay's experiential frame. Use the Distinguish Protocol aggressively to avoid false positives. But if the essay asks the reader to generalize beyond the local experience, WR0 and BP6 still apply.

**Advocacy Journalism / Long-Form Argument:** Full diagnostic applies. FM-A3 (The Persuasion Machine) is the signature risk. FM-A9 (Concession Without Cost) and FM-A11 (Evidence Laundering) are high-frequency. The writer's conviction is genuine; the diagnostic question is whether the argument is structurally honest. NE-codes matter most here: does the narrative do argumentative work, or does it substitute for argument?

**Grant Proposal:** AT3 with unique burden structure. Must demonstrate problem (evidence), proposed solution (mechanism), feasibility (implementation), measurement (evaluation plan), and team capacity. BP5 is critical but calibrated differently: alternatives must be addressed to show the proposer has considered the landscape, not necessarily to demonstrate superiority. FM-A18 (Implementation Blindspot) is the signature risk. AC codes calibrate for the specific funder's priorities and expertise level. Genre-structure signal (see the genre layer + the Reviewer-Anticipation Lens below): the required skeleton is **Specific Aims · Significance · Innovation · Approach** — a proposal that omits the Approach (or leaves it unseeded) cannot survive a panel reviewer, who scores it directly.

**White Paper:** AT1/AT2 hybrid with AT3 tail. Technical audience. BP4 is highest-risk: the precision must match the methodology. SM4 matters because white papers frequently cite secondary analyses as if they were primary data. WR1 applies when industry-standard warrants are assumed but not shared by the intended audience.

**Legal Brief / Motion:** AT3 with strict procedural burden. Authority carries special weight (precedent-as-authority is the structural backbone). SM codes calibrate for legal citation standards. WR is less about unstated warrants and more about whether the precedent actually governs the case at hand. DI4 (Motte-and-Bailey) is high-risk in appellate briefing.

**Book Review:** AT2 primarily. Scope discipline is the central risk: the review must evaluate *this book*, not use this book as an excuse to evaluate *this field*. BP2 is the signature failure. CL4 may fire when the review's key terms (e.g., "accessible," "rigorous," "ambitious") shift meaning between praise sections and criticism sections.

**Open Letter / Manifesto:** AT3 with sympathetic audience. AC3 is the signature risk: the document preaches to the converted. FM-A12 (Emotional Inflation) and FM-A13 (Structural Motte-and-Bailey) are high-frequency. OB handling calibrates differently: manifestos may legitimately decline to engage moderate objections, but DI0 (starting-point smuggling) still applies.

**Crisis Communications:** Mixed audience. Compressed timeline. AC4 is high-risk. WR0 tolerance is higher because the audience needs direction, not philosophical completeness. But BP4 and DI2 (pseudo-resolution) are critical: the crisis communication must not perform certainty it doesn't have or claim resolution it hasn't achieved.

**Pitch Deck:** AT3 (back this / buy this), highly compressed, written for an **investor reading fast**. The genre-required structure is the **problem → solution → traction** narrative (see the genre layer, `docs/nonfiction-pre-draft.md`). Calibration: *loosen* on exhaustive support (compression is expected); *tighten* on the **problem→solution warrant** — the WR0 between "here is a pain" and "therefore our thing." FM-A8 (False Precision Theater) is the signature risk: vanity-metric traction dressed as evidence. The genre-structure signal: a solution that does not follow from the stated problem, or traction that is a metric without a baseline. **Firewall boundary (the line this entry must not cross):** diagnose whether the *argument* of the deck holds — the problem→solution inference and traction-as-evidence honesty. **Do not** coach slide design, deck length, or fundraising tactics — that is rhetoric coaching, which this audit does not do (see "What this audit is not," above). Diagnosis names the structural gap ("the solution does not follow from the problem as stated"); it never authors the problem, the solution, or the traction numbers.

### Reviewer-Anticipation Lens (grant / academic / pitch)

For the three **evaluator-scored** genres above, read the argument as the named evaluator will. The evaluator is the audience that *scores* the piece, not just receives it; the genre layer (`docs/nonfiction-pre-draft.md`) lets the writer pre-list the evaluator's objections (`reviewer_objections`), and the diagnostic surfaces a genre-required objection class that the draft leaves *unengaged* — it never authors the objection (the "Proposing objections the writer should address" line under Not Allowed still governs).

**Pre-draft vs. draft-time.** The two halves share the Firewall but run at different times. *Pre-draft*, the `argument-spine` validator's **W5** (reviewer-anticipation, Increment 2 of the genre layer) checks only that the writer's `reviewer_objections` list is **non-empty** — an empty or absent list is the empty required class W5 surfaces, nudging the writer to pre-list before drafting; W5 authors nothing. *Draft-time*, this audit reads that same pre-list as the reviewer lens and diagnoses whether each anticipated objection is actually **engaged** in the draft's §6 (The Strongest Case Against) — again authoring no objection, only surfacing an unengaged class. The per-genre calibration:

| Genre → evaluator | Evaluator's stance | Top objection classes the reviewer raises | W5 pre-list → §6 mapping |
|---|---|---|---|
| **Grant proposal → panel reviewer** | Scores Significance / Innovation / Approach against a rubric; feasibility-first, skeptical of measurement | "the design can't isolate the effect," "the timeline/feasibility is optimistic," "alternatives weren't surveyed" (FM-A18 Implementation Blindspot is where most score down) | Each `reviewer_objections` entry seeds one §6 objection the Approach + a feasibility/measurement subsection must engage; BP5 reads as "surveyed the landscape," **not** "proved superiority" |
| **Academic paper → peer reviewer** | Strictest calibration; CL0 disqualifying; adversarial with the literature | "this is already known," "the gap isn't real," "the method doesn't support the claim" | Each entry seeds a §6 objection engaged in Related-Work + the identification/method section; the signature gap — a **contribution claim with no related-work positioning** (W4 nudges it pre-draft) |
| **Pitch deck → investor** | Reading fast; compression expected; tests the load-bearing inference | "the problem isn't urgent enough to switch," "the solution doesn't follow from the problem," "the traction is a vanity metric" (FM-A8 False Precision Theater) | Each entry seeds a §6 objection engaged in the Solution (the problem→solution WR0) + a defensibility/traction-honesty subsection; never author the investor's objection for the writer |

- **Grant proposal → study-section / panel reviewer** (scores Significance / Innovation / Approach against a rubric). The objection class to check engaged: the reviewer's feasibility and measurement doubts. FM-A18 (Implementation Blindspot) is where most proposals score down. BP5 (alternatives) reads as "the proposer surveyed the landscape," **not** "proved superiority."
- **Academic paper → peer reviewer** (strictest calibration; CL0 is disqualifying). The objection class: "this is already known," "the gap isn't real," "the method doesn't support the claim." The net-new structural signal — a **contribution claim with no related-work positioning** is the academic analogue of a bare assertion: the paper claims novelty without locating the gap (the genre layer's W4 nudges the missing related-work section pre-draft).
- **Pitch deck → investor** (reading fast). The objection class: "the problem isn't urgent," "the solution doesn't follow," "the traction is vanity-metric'd." Surface the unengaged class; never write the investor's objection for the writer.

The three canonical worked examples (`core-editor/references/example-argument-state-genre-{grant,academic,pitch}.md`, gated by `validate.sh --check-all`) each carry a writer-authored `reviewer_objections` pre-list seeded into a §6 *Reviewer-anticipation* block — the worked demonstration of the mapping above (they pass W5 clean under `--strict` because the list is non-empty).

### By Audience Posture

| Audience Posture | Tighten On | Loosen On | Common False Positive |
|-----------------|-----------|----------|----------------------|
| **General audience** | AC1, WR0, BP0, definition clarity | Full scholarly literature review | Mistaking accessibility for oversimplification |
| **Expert audience** | SM4, WR1, BP4, DI0 | Explicit background explanation | Flagging compressed warrants that the field genuinely shares |
| **Hostile audience** | OB3, OB4, AC2, BP5 | Tonal warmth or narrative invitation | Treating any concession as weakness |
| **Sympathetic audience** | AC3, BP2, NE3 | Exhaustive defense of uncontested basics | Treating audience agreement as structural adequacy |
| **Mixed audience** | AC1, AC4, WR0, BP6 | Highly technical shorthand | Assuming one support form will satisfy everyone |

### Calibration for Length

- **Short form (< 1,500 words):** Expect 1–2 subclaims. Support map may be compressed. One vignette may carry the piece. Warrant analysis calibrates for compression: recoverable warrants are acceptable when the medium prohibits full explication.
- **Mid-length (1,500–5,000 words):** Full audit applies. 2–3 subclaims expected. Objection handling should be substantive, not gestural. Multiple vignettes require individual tagging. Cross-section tracking (Step 8) becomes relevant.
- **Long form (> 5,000 words):** Expect 3+ subclaims and possibly nested sub-arguments. Support map may require per-section tracking. BP-codes and WR-codes are highest-value at this length (scope creep and qualification erosion accumulate over distance). Full objection handling expected. Cross-section tracking is essential.

---

## Tracking Artifacts

### Artifact A: Argument Architecture Table

| Subclaim | Support Type | Scheme Hint | Warrant Status | Scope Match | Fired Codes |
|----------|-------------|-------------|---------------|-------------|-------------|
| C1 | [type] | [scheme] | [status] | [Y/N] | [codes] |
| C2 | [type] | [scheme] | [status] | [Y/N] | [codes] |
| C3 | [type] | [scheme] | [status] | [Y/N] | [codes] |

Purpose: Unified view of the argument's structural health. Each row shows one subclaim's support chain from evidence through warrant to scope. Replaces the need to cross-reference Steps 3, 4, and 5 manually.

### Artifact B: Audience Calibration Matrix

| Dimension | Classification | Structural Requirement | False-Positive Guard |
|-----------|---------------|----------------------|---------------------|
| Expertise | [general/mixed/expert] | [what this requires] | [what to tolerate] |
| Receptivity | [sympathetic/mixed/hostile] | [what this requires] | [what to tolerate] |
| Consequence | [low/medium/high] | [what this requires] | [what to tolerate] |

Purpose: Makes the audience gate explicit. Prevents the reviewer from applying expert-audience standards to a general-audience piece or sympathetic-audience tolerance to a hostile-audience piece.

### Artifact C: Failure Mode Inventory

| Code | Pattern Name | Severity | Cluster | Blast Radius | Location |
|------|-------------|----------|---------|-------------|----------|
| [code] | [pattern] | [Could-Fix / Should-Fix / Must-Fix] | [Arch / Rel / Qual / Dyn] | [Local / Multi-section / Systemic] | [where in draft] |

Purpose: Master inventory of all fired codes. Cluster column tells the reviewer how the failure was detected. Blast radius column indicates how much of the draft is affected.

### Artifact D: Cross-Section Tracking

| Section | Claim as Stated | Qualification Level | Key Term Definitions | Drift from C0 |
|---------|----------------|--------------------|--------------------|---------------|
| Opening | [claim] | [hedged/moderate/confident] | [T1 = X, T2 = Y] | [none / note] |
| Body §1 | [claim] | [hedged/moderate/confident] | [T1 = X, T2 = Y] | [none / note] |
| Body §2 | [claim] | [hedged/moderate/confident] | [T1 = X, T2 = Y] | [none / note] |
| Conclusion | [claim] | [hedged/moderate/confident] | [T1 = X, T2 = Y] | [none / note] |

Purpose: Makes dynamic failures visible. If the qualification level decreases from "hedged" to "confident" without new evidence, that's FM-A16. If key term definitions shift, that's CL4. If the claim broadens, that's BP2.

### Artifact E: Warrant Verdict + Premise-Plausibility Flags

| Decision Test | Result | Notes |
|--------------|--------|-------|
| Claim-accessibility | [pass/fail] | [detail] |
| Evidence-evaluability | [pass/fail] | [detail] |
| Bridge-recoverability | [pass/fail] | [detail] |
| Scope-honesty | [pass/fail] | [detail] |
| Objection-awareness | [pass/fail] | [detail] |
| Form-fit | [pass/fail] | [detail] |
| **Warrant verdict** | [WARRANTED / UNCONVENTIONAL-BUT-WARRANTED / UNWARRANTED] | |
| **Retroactive adjustments** | [codes downgraded/upgraded] | |

Premise-plausibility flags (the acceptability axis — surfaced, never adjudicated):

| Premise ID | Premise as used | Load-bearing role | Flag type(s) | Why flagged | Firewall boundary | Repair implication |
|-----------|-----------------|-------------------|--------------|-------------|-------------------|--------------------|
| [P1] | [premise in the text's own terms + location] | [C0 / ground / subclaim / warrant / scope limiter / comparison / objection / definition / stakes] | [CONTESTABLE / UNEARNED / OVERLOADED / EXTERNAL-VERIFY / DEFINITIONAL, joined by ` + ` — or NONE_REGISTERED] | [why a careful reviewer would not let it pass] | [what is *not* being adjudicated] | [support / qualify / disclose / compare / define / cite] |

If none are found or registered, the table collapses to a single `NONE_REGISTERED` row with a Firewall note that this is not a truth clearance.

Purpose: Documents the Distinguish Protocol's reasoning and separates the inferential warrant verdict from the (non-adjudicative) premise-acceptability flags. When prior codes are retroactively adjusted, the editorial letter can explain why. A premise flag never becomes a stealth warrant defeat.

---

## Hard Gates

These do not replace judgment. They identify failures that should default to top-tier concern because they break the audit's central promise of evaluability. Escalate to Must-Fix only through the Severity Floor below: a Hard-Gate pattern that fires but does not defeat C0's evaluability caps at Should-Fix.

### Severity definitions

These tiers are referenced throughout (artifacts, Hard Gates) and are defined here:

- **Must-Fix:** the failure *defeats* evaluability or warrant of **C0**. The main claim cannot be identified or is unstable; its central inferential bridge is *unrecoverable* (warrant MISSING, not merely RECOVERABLE-but-unstated); or the conclusion asserts something the evidence cannot reach at all. A code *correctly escalated* to Must-Fix has, by this definition, already registered a defeat of C0's evaluability — which is what forces an UNWARRANTED verdict in Step 9. (The Severity Floor, not the code family, is what escalates: a Hard-Gate code that fires without defeating evaluability caps at Should-Fix and does not touch the verdict.)
- **Should-Fix:** a real weakness a competent reader can route around: a recoverable-but-understated warrant, a strong objection thinned rather than absent, scope tightened toward the conclusion, an alternative gestured at but not engaged. This is the **default tier for soft spots in an otherwise-warranted argument** and is the priority repair agenda; it does not force UNWARRANTED.
- **Could-Fix:** improves rigor; does not affect whether C0 holds.

### Severity Floor

A Hard-Gate code escalates to Must-Fix **only when it meets the Must-Fix definition above** (it defeats C0's evaluability, not merely weakens it):

- **WR0** on C0 is Must-Fix only when the warrant is MISSING for the *actual, declared* audience, not merely under-stated for a hypothetical hostile one. Use Step 4's EXPLICIT / RECOVERABLE / MISSING / CONTESTED scale; RECOVERABLE caps at Should-Fix and must name the importable premise.
- **OB3** is Must-Fix only when the objection is central *and* its absence makes C0 unevaluable, not merely less persuasive.
- **BP5** is Must-Fix only when no comparative reasoning for the recommendation exists *anywhere* in the piece.
- **BP2 / DI4** are Must-Fix only when the scope creep or motte-and-bailey is load-bearing for C0 as actually concluded.

A Hard-Gate code that fires but does not meet the Must-Fix definition caps at **Should-Fix**.

### Specificity guard (anti-over-firing)

Deficit-hunting is calibrated against a *competent* baseline. A published, edited argument typically carries one or two genuine soft spots, not a flood of structural breaks. If the diagnosis returns **three or more Must-Fix codes** on a piece that passes Claim-accessibility, Evidence-evaluability, and Form-fit, treat that as a **re-examination trigger** (not an automatic downgrade): re-test each Must-Fix against the Severity Floor before returning UNWARRANTED. Firing an UNWARRANTED verdict on a competent argument is as serious a failure as missing a real break; leaving warranted arguments classified WARRANTED is a pass condition, not a courtesy.

### Default Must-Fix

1. **CL0** or **CL1** at the piece level — no identifiable or stable main claim
2. **WR0** on the support chain for C0 — the main claim's inferential bridge is absent
3. **BP2** in the final conclusion — scope creep in the conclusion
4. **BP5** in any consequential AT3 recommendation — proposal not comparatively defended
5. **OB3** where the objection is central to the manuscript's recommendation or evaluation
6. **DI2** or **DI4** when they affect C0 — pseudo-resolution or Motte-and-Bailey at the main-claim level
7. Repeated **NE3** across multiple key vignettes — systemic emotional override
8. **BP6** when testimony is being used to justify a general institutional conclusion without added support

### Context-Dependent Escalation

- **AC2** becomes Must-Fix for legal, legislative, adversarial, or expert-hostile contexts
- **BP4** becomes Must-Fix in technical, scientific, policy, or data-heavy work
- **SM4** becomes Must-Fix in academic and expert-facing prose
- **OB4** becomes Must-Fix when objection handling is central to the piece's claim of fairness or seriousness
- **CL4** becomes Must-Fix when the definitional shift affects C0's meaning
- **FM-A13** (Structural Motte-and-Bailey) is Must-Fix when the bailey is the argument's actual conclusion (C0); when the motte-and-bailey is local and not load-bearing for C0, it caps at Should-Fix per the Severity Floor
- **FM-A14** (Epistemic Erasure) becomes Must-Fix in advocacy, testimony, and policy writing about affected populations

---

## Scope Selection

### Default Scope

| Component | What to Sample | How Many |
|-----------|---------------|----------|
| Opening | First 3–5 paragraphs (where the claim should emerge) | 1 |
| Body sections | Representative sections containing subclaims + evidence | 2–3 |
| Definitions | All high-stakes terms that carry argumentative weight | As needed |
| Concessive moves | Passages where the text addresses objections, limits, or alternatives | All |
| Narrative segments | Vignettes, cases, anecdotes embedded in argument | All |
| Closing | Final section (where the claim should be cashed out) | 1 |

Steps 1 and 2 run on the whole piece. Steps 3–7 sample strategically within the scope above. Step 8 compares across sections. Step 9 runs once, after everything else.

### When to Expand

- If CL1 or CL4 fires → map the claim and key terms in every major section
- If WR0 fires on the main claim → inventory every inferential bridge touching C0
- If BP5 fires in an AT3 piece → expand to every mentioned or implied alternative
- If SM4 fires → trace the citation chain one level deeper where possible
- If AC1 or AC4 fires → compare one general-audience passage and one expert-facing passage if the manuscript mixes modes
- If NE-codes fire on sampled vignettes → expand to all narrative segments
- If DI4 fires → track the claim as stated in every section to map the oscillation

---

## Output Format

### 1. Primary Classification Block

```
Dialectical Clarity v2.0:
  Argument type: [AT-code]
  Audience calibration: [AC-code or PASS]
  Warrant verdict: [WARRANTED / UNCONVENTIONAL-BUT-WARRANTED / UNWARRANTED]
  Premise-plausibility flags: [NONE_REGISTERED / P1, P2, ...]
  Severity summary: [top 3 risks]
  Pattern matches: [FM-A codes]
```

### 2. Claim Ladder Block

```
Claim Ladder:
  C0: [...]
  C1: [...]
  C2: [...]
  C3: [...]
  Stakes: [...]
  Key terms: [T1 = ..., T2 = ...]
  Codes: [CL-codes]
```

### 3. Support & Warrant Block

```
Support / Warrant:
  C1 -> [support type] / [scheme hint] / [warrant status] / [qualifier]
  C2 -> [...]
  C3 -> [...]
  Codes: [SM-codes, WR-codes]
```

### 4. Burden & Objection Block

```
Burden / Objections:
  Scope match: [Y/N]
  Alternatives burden met: [Y/N]
  Strongest objection status: [engaged / evaded / missing]
  Dialectical integrity: [codes or PASS]
  Codes: [BP-codes, OB-codes, DI-codes]
```

### 5. Narrative-Evidence Block

```
Narrative as Evidence:
  V1 -> [function] / [witness position] / [attached claim]
  V2 -> [...]
  Codes: [NE-codes]
```

### 6. Cross-Section Block

```
Cross-Section Integrity:
  Claim drift: [stable / drift at §X]
  Qualification erosion: [stable / erosion from §X to §Y]
  Scope accumulation: [matched / escalation at conclusion]
  Definition stability: [stable / T1 shifts at §X]
  Codes: [cross-section codes with locations]
```

### 7. Priority Block

```
Priority diagnosis:
  Structural break: [...]
  Failure cluster: [Architectural / Relational / Quality / Dynamic]
  Why it matters: [...]
  First repair target: [diagnostic only; no rewrite]
```

### 8. Argument State Artifact

When this audit runs on argument-shaped nonfiction, emit `Argument_State.md` as a companion artifact alongside the editorial letter. Populate §§ 1–9 from the diagnostic steps above (§ 1 from Step 1, § 2 from Step 2, § 3 from Step 3, § 4 from Step 4, § 5 from Step 5, § 6 from Step 6, § 7 from Step 7, § 8 from Step 8, § 9 from the priority diagnosis). Initialize § 10 with empty subsections 10.1–10.9 for companion module annotations.

The `Argument_State.md` schema is defined in `docs/argument-state-schema.md`. This artifact is the shared state contract for the Nonfiction Argument Engine — Red Team, Persuasion, Evidence, and Coaching companions all read from it rather than re-deriving the argument graph.

If a companion module is requested and `Argument_State.md` does not yet exist, run this audit first to produce it.

---

## Integration with Core Framework

### Module Position

This is a specialized audit invoked by the Franklin Pathway (Classification 3 or 4 redirect) or loaded directly when intake identifies argument-shaped material. It stacks with other audits, particularly the Narrative Nonfiction Craft audit for hybrid material.

### Relationship to Franklin Pathway

**Franklin is the gate; this audit handles what Franklin's story-spine tools can't.**

Franklin's Classification 3 (Argument With Embedded Narrative) identifies material where argument dominates and narrative is used as evidence. This audit replaces the Classification 3 stub with a full diagnostic.

Franklin's Classification 4 (Not Storyable) identifies material that may be argument-shaped. When the redirect suggests "argument-driven piece" or "policy brief," this audit provides the appropriate structural diagnosis.

**Invocation logic:**

| Franklin Classification | This Audit's Role |
|------------------------|-------------------|
| Classification 1 (Story-Shaped) | Not invoked — material is narrative |
| Classification 2 (Storyable) | Not invoked — material has narrative potential |
| Classification 3 (Argument + Narrative) | **Primary invocation** — diagnose argument structure; Franklin Steps 1–4 handle embedded narrative segments |
| Classification 4 (Not Storyable) | **Conditional invocation** — run when redirect identifies argument-shaped material |

### Relationship to Narrative Nonfiction Craft Audit

For F5 (Argument with embedded narrative) material, both audits may run:

- **This audit** handles the argument structure: claim ladder, support map, warrant bridge, burden of proof, objection handling, dialectical integrity.
- **Narrative Nonfiction Craft** handles the reader experience: lead contract (LC-codes), question management (QS-codes for embedded questions), ending payoff (E-codes), and meaning line (SW-codes — though in argument, the meaning line IS the argument, so SW-codes recede).

They are complementary. This audit asks "is the argument warranted?" Nonfiction Craft asks "does the reader stay engaged?"

### Relationship to Character Architecture Part 9

Part 9 (Moral Argument Architecture) tests whether a **story** argues a moral position through character action — weakness, need, opponent-as-counter-argument, moral choice. This audit tests whether a **non-story** argues a position through claim-evidence structure.

For pieces that contain both (memoir with argument, narrative journalism with a thesis), both may apply. Part 9 diagnoses the story layer. This audit diagnoses the argument layer. The M-codes (moral argument hypothesis) and the CL-codes (claim ladder) may produce different formulations of "what this piece argues," and if they conflict, that's diagnostic: the story argues one thing and the explicit argument argues another.

### Relationship to Banister Audit

The Banister audit tests epistemic humility and moral complexity in fiction — whether the work honors genuine difficulty and avoids false resolution. This audit tests argumentative clarity, inferential integrity, and objection handling in non-fiction argument.

**Banister asks:** "Does the story honor complexity?"
**This audit asks:** "Does the argument handle objections and earn its confidence?"

For advocacy journalism, testimony, or policy arguments that touch contested moral terrain, both may be relevant. The Banister audit prevents the fiction layer from becoming propaganda; this audit prevents the argument layer from becoming dogma.

### Relationship to Emotional Craft Diagnostics

The v2.0 enrichment gives Emotional Craft cleaner handoff points:

- NE3 identifies when emotion is covering structural weakness
- AC3 identifies when emotional affinity substitutes for burden
- WR0 identifies when a passionate paragraph still lacks an inferential bridge

An argument can be fully warranted but emotionally dead, or emotionally powerful but logically empty. If Emotional Craft shows flat affect in argument-shaped sections (S-codes firing), the issue may be that the writer is suppressing voice to sound "objective." If Emotional Craft shows high emotional transmission alongside NE3 (emotional override), the issue is the opposite: feeling is substituting for reasoning.

### Relationship to Scene Turn Diagnostics

Scene Turn handles fiction scene mechanics. For Classification 3 material, embedded narrative segments may be checked by Scene Turn (if they contain goal-conflict-outcome scenes) while the argument frame is checked by this audit. The two operate on different layers of the same piece.

### Pass Modifications

**Pass 1 (Reader Experience):** When flagging "I don't know what the argument is" or "the piece shifts between claiming and narrating," add as Dialectical Clarity trigger. CL-codes and AT-codes diagnose the mechanism.

**Franklin Pipeline Integration (Classification 3):** Replace the stub argument output with: "Invoke the Dialectical Clarity Audit on the argument structure. Run Franklin Steps 1–4 on embedded narrative segments."

### Orchestration with Other Audits

**With Narrative Nonfiction Craft:** For F5 material, run both. This audit handles argumentative warrant; Nonfiction Craft handles reader contract and engagement.

**With Scene Turn Diagnostics:** For Classification 3 material with embedded scenes, Scene Turn handles goal-conflict-outcome mechanics; this audit handles the argument frame containing them.

**With Emotional Craft Diagnostics:** Complementary. NE3 is the handoff code: when narrative's emotional force masks structural weakness, both audits have something to say about it.

---

## Coaching in the Editorial Letter

The diagnostic procedure identifies structural failures with specific codes. When the editorial letter is written, it may include coaching guidance: explaining why scope discipline matters, how objection handling builds rather than undermines the argument's authority, what "narrative as substitute" looks like from the reader's perspective, how a warrant gap creates the feeling of "smart but unconvincing," or why definitional smuggling undermines trust even when the writer didn't intend deception. This coaching belongs in the deliverable, not in the diagnostic specification.

---

## Final Diagnostic Question

*Can a careful reader who does not already agree with this argument identify what is being claimed, evaluate the evidence, test the inferential bridge, judge the scope, and determine whether disagreement has been handled honestly?*

If yes: the argument is **WARRANTED**, regardless of whether its premises are ultimately true (premise acceptability is surfaced separately as non-adjudicative flags).
If no: name which step breaks first. That's the priority diagnosis. When two defeats co-fire, the *first-broken* (upstream) step leads; for a co-present FM-A10 comparative defeat plus a test-three MISSING causal warrant leap on C0, rule 2a's primacy-override names that upstream step as the warrant leap (FM-A6), with FM-A10 co-reported as subordinate.

This is the operative test for the Step 9 warrant verdict: if it returns "yes," return **WARRANTED** even when Hard-Gate codes fired. The codes become the Should-Fix repair agenda, not an UNWARRANTED verdict. **One bounded exception (see the warrant-verdict decision rule 2a):** for an AT3 *recommendation*, "evaluate the evidence … and determine whether disagreement has been handled honestly" includes the comparative test — so a recommendation that engages *no* alternative at all — naming even a single or strawmanned foil does **not** qualify (that is a soft spot, per rule 2a's scope guard) — and discharges *none* of its comparative burden (BP5 + OB3, no funding mechanism) returns **"no"** on this test *as a recommendation* and is **UNWARRANTED** (FM-A10), even though its benefit-claims are individually evaluable. **Primacy:** if this recommendation *also* suffers a MISSING causal/diagnostic warrant leap on C0 — its *problem* is unwarranted, not merely its remedy uncompared — that upstream warrant leap is the primary locus (FM-A6) and the FM-A10 defeat is co-reported as subordinate (rule 2a's primacy-override); the verdict is UNWARRANTED under either.

---

*This audit diagnoses argumentative structure in non-narrative material — whether the claim is identifiable, the evidence supports it, the inferential bridge holds, the scope is honest, the objections are engaged fairly, and narrative does argumentative work rather than substituting for it. It calibrates by audience and genre, tracks dynamic failures across sections, and distinguishes unwarranted arguments from unconventional but warranted argument forms. It extends the Editor's coverage from story-spine diagnosis to argument-spine diagnosis, providing the most comprehensive structural diagnostic in the APODICTIC system for any text whose dominant function is claim and support. The system diagnoses the argument's structure; the writer provides the claims, the evidence, and the intellectual honesty.*
