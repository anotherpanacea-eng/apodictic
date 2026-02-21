# Specialized Audit: Dialectical Clarity
## Version 1.0
*Last Updated: February 2026*

---

## Purpose

Diagnose argumentative structure in non-narrative material — essays, op-eds, policy briefs, testimony, reports, and argument-with-embedded-narrative hybrids. This audit tests whether the argument is valid, scoped, supported, and honest about objections.

**Core claim:** Material whose dominant function is claim/support can't be meaningfully audited by story-spine tools. Forcing narrative diagnostics on argument-shaped writing produces false failures ("no protagonist," "no inciting incident") that are technically true and practically useless. This audit provides what story-spine tools can't: structural diagnosis of argumentative clarity.

**What this audit is:** Dialectical clarity + burden-of-proof discipline. It asks whether the reader can identify the claim, evaluate the evidence, and judge whether objections were handled — the structural hygiene of honest argument.

**What this audit is not:** Rhetoric coaching. It does not teach persuasion, suggest hooks, recommend "counterargument paragraphs," or optimize for audience manipulation. It diagnoses whether the argument is structurally clear and evidentially honest. The writer decides what to argue; this audit tests whether the argument holds together.

**Named for:** The dialectical tradition in philosophy — argument tested through objection, scope, and evidence. Not the rhetorical tradition (which optimizes for persuasion) and not the informal-logic tradition (which catalogs named fallacies).

**When to activate:**
- Franklin Pathway returns Classification 3 (Argument With Embedded Narrative)
- Franklin Pathway returns Classification 4 and redirects to "argument-driven piece" or "policy brief"
- Narrative Nonfiction Craft audit returns F5 (Argument with embedded narrative)
- Intake identifies material as essay, op-ed, testimony, policy brief, report, or scholarly article
- Author states the piece's purpose is to argue, persuade, propose, evaluate, or testify

---

## Firewall Compliance

This audit operates within the Editor's firewall by producing diagnostic classifications and structural requirements, not content.

### Allowed

- Extracting the main claim and subclaims from existing text
- Classifying argument type and promise
- Mapping what evidence supports which claims
- Diagnosing scope mismatches between claims and evidence
- Identifying objections the text engages (or conspicuously avoids)
- Tagging narrative vignettes by argumentative function
- Flagging structural gaps in the support chain

### Not Allowed

- Inventing claims, subclaims, or stakes the text doesn't contain
- Suggesting what the argument "should" be
- Proposing objections the writer should address (diagnosis only: "central objection unaddressed")
- Writing or rewriting argument sections
- Evaluating whether the argument is *correct* — only whether it is *structurally clear and evidentially supported*

### The Distinction in Practice

- ❌ NOT ALLOWED: "You should add a counterargument about cost-effectiveness in paragraph 7."
- ✅ ALLOWED: "Subclaim C2 has no support. The argument asks the reader to accept it on assertion alone. Code: SM0."
- ❌ NOT ALLOWED: "The opening would be stronger with a concrete example."
- ✅ ALLOWED: "Argument type is AT3 (propositional) but evidence is exclusively AT1-appropriate (explanatory). The burden of proof exceeds what the evidence structure delivers. Code: BP1."

---

## Code Namespace Note

This audit uses AT-codes (argument type), CL-codes (claim ladder), SM-codes (support map), BP-codes (burden of proof), OB-codes (objection handling), and NE-codes (narrative-as-evidence).

**No collisions with existing code systems:**
- Scene Turn Diagnostics: G-codes, C-codes, O-codes, Sq-codes, H-codes, U-codes, P-codes
- Emotional Craft Diagnostics: S-codes, B-codes
- Narrative Nonfiction Craft: F-codes, QS-codes, I-codes, ST-codes, SW-codes, AS-codes, A-codes, LC-codes, E-codes
- Character Architecture Part 9: M-codes, W-codes, N-codes, DN-codes, OCA-codes, PW-codes, SR-codes, MC-codes, TP-codes

All six code systems in this audit use two-letter prefixes to prevent collision. All may appear in the same editorial letter alongside codes from other audits.

---

## The Diagnostic Procedure

### Step 1: Argument Type & Promise (AT-codes)

Classify the argument by its dominant function — what the piece asks the reader to accept and what kind of acceptance that requires.

**Run on:** opening + closing + 1–2 representative body sections.

```
Argument Type: [AT-code]
  Promise: [what the reader expects to receive]
  Burden level: [LOW / MEDIUM / HIGH]
  Consistent throughout: [Y/N]
```

**Argument type codes:**

| Code | Type | Promise to Reader | Burden Level |
|------|------|-------------------|-------------|
| **AT1** | Explanatory | "Here's how this works" | Low — must be clear and accurate |
| **AT2** | Evaluative | "Here's whether this is good/bad/working/broken" | Medium — must show criteria and apply them |
| **AT3** | Propositional | "Here's what we should do" (policy/normative) | High — must show problem, solution, and why alternatives fail |
| **AT4** | Testimonial | "I witnessed this; here's what it means" | Mixed — observation is low-burden, interpretation is high-burden |

**Argument type failure codes:**

| Code | Name | Description |
|------|------|-------------|
| **AT0** | Type undeclared | Argument shifts between explaining, evaluating, and proposing without signaling; reader can't calibrate their skepticism |

**Why type classification matters:** All later steps calibrate by type. Flagging "no objections engaged" in an AT1 explanatory piece is a false positive — explanations don't require objection handling. Flagging "no objections engaged" in an AT3 propositional piece is a critical failure — proposals demand it.

**Calibration with F5:** If the Narrative Nonfiction Craft audit has already classified the piece as F5 (Argument with embedded narrative), AT-codes add precision about *what kind* of argument. F5 says "argument dominates"; AT-codes say what the argument asks the reader to do.

### Step 2: Claim Ladder (CL-codes)

Extract the main claim (C0) and the subclaims (C1–C3) that must be true for C0 to hold. Also extract the stakes claim — why the argument matters.

**Run on:** full draft (claims may be distributed, not concentrated in one section).

```
C0 (main claim): [one sentence — what the piece argues]

C1: [subclaim that must be true for C0 to hold]
C2: [subclaim that must be true for C0 to hold]
C3: [subclaim that must be true for C0 to hold]

STAKES: [why C0 matters — what's at risk if the reader ignores this]
  Stakes type: CONSEQUENTIAL / MORAL / EPISTEMIC / PRACTICAL
```

**Constraints:**
- C0 must be extractable from the text as written, not inferred from implication. If the reader can't state the main claim after reading, the ladder has failed.
- Subclaims must be necessary links, not illustrations. Test: if C2 is false, does C0 still hold? If yes, C2 isn't a subclaim — it's color.
- Stakes must be stated or strongly implied by the text. If the reader finishes and can't answer "why should I care?" the stakes claim is missing.

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

**Output:** Claim ladder (C0 + C1–C3 + stakes) + CL-codes for any failures.

### Step 3: Support Map (SM-codes)

For each subclaim, identify what supports it and classify the support type. Then test whether the support actually bears on the claim it's attached to.

**Run on:** body of the argument — track evidence as it appears.

```
C1: [subclaim]
  Support: [what the text offers as evidence]
  Support type: [REASON / EXAMPLE / DATA / AUTHORITY / EXPERIENCE]
  Link: [does the support actually bear on C1?]
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

**Support Map failure codes:**

| Code | Name | Description |
|------|------|-------------|
| **SM0** | Missing support | Subclaim is asserted without evidence; reader must take it on faith |
| **SM1** | Irrelevant support | Evidence offered doesn't bear on the subclaim; connection is associative, not logical |
| **SM2** | Support proves different claim | Evidence is relevant and real but supports a claim the text isn't making |
| **SM3** | Single-type dependence | All support is the same type (e.g., all examples, no reasons); argument collapses if that type is challenged |

**Output:** Support map per subclaim + SM-codes for any failures.

### Step 4: Burden of Proof & Scope (BP-codes)

Test whether the evidence is commensurate with what the claim asks the reader to believe. This is the scope discipline step — where arguments most commonly fail without the writer noticing.

**Run on:** compare C0's scope against the aggregate support from Step 3.

```
CLAIM SCOPE:
  C0 claims: [UNIVERSAL / PROBABILISTIC / LOCAL / NORMATIVE / DEFINITIONAL]

EVIDENCE SCOPE:
  Evidence supports: [UNIVERSAL / PROBABILISTIC / LOCAL / NORMATIVE / DEFINITIONAL]

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

**Output:** Scope comparison + BP-codes for any failures.

### Step 5: Objection Handling (OB-codes)

Identify 2–4 objections the piece implicitly anticipates or conspicuously ignores. Test whether the engagement is real.

**Run on:** full draft — look for concessive moves ("to be sure," "one might argue," "critics say"), anticipated counterarguments, and structural gaps where an obvious objection goes unaddressed.

```
OBJECTION 1: [what the strongest objection would be]
  Engaged: [Y/N]
  If Y — quality: [SUBSTANTIVE / STRAWMAN / EVASION]
  If N — severity: [MINOR / SIGNIFICANT / CENTRAL]

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

**Note on AT1:** For explanatory arguments, OB0 is not automatically a failure. If the explanation is accurate and clear, absence of objection handling is acceptable. For all other argument types, OB0 is diagnostic.

**Output:** Objection inventory (2–4) + OB-codes for any failures.

### Step 6: Narrative-as-Evidence Tagging (NE-codes)

For each narrative vignette, case study, or personal anecdote embedded in the argument, identify what claim it supports and whether it's doing argumentative work or serving as decoration.

**Run on:** identify all narrative segments (scenes, anecdotes, case examples, personal testimony) within the argument. For each:

```
Vignette [X]: [description — location in draft]
  Attached to: [which subclaim does this support?]
  Function: [ILLUSTRATION / EVIDENCE / EMOTIONAL ANCHOR / UNATTACHED]
  Code: [NE-code or PASS]
```

**Vignette function types:**

| Function | What It Does | Argumentative Status |
|----------|-------------|---------------------|
| **Illustration** | Makes an abstract claim concrete; reader "sees" what the claim means | Useful but not probative — removing it weakens clarity, not validity |
| **Evidence** | Establishes that a claimed phenomenon exists or occurs | Probative — removing it weakens the support chain |
| **Emotional anchor** | Creates reader investment in the argument's stakes | Motivational — removing it reduces urgency but doesn't affect logic |
| **Unattached** | Powerful writing with no identifiable argumentative function | Decoration — may actively mislead by creating emotional conviction without logical connection |

**Narrative-as-Evidence failure codes:**

| Code | Name | Description |
|------|------|-------------|
| **NE0** | Unattached vignette | Narrative is powerful but doesn't support any identifiable subclaim; it creates feeling without doing argumentative work |
| **NE1** | Vignette as substitute | Narrative replaces argument rather than supporting it; the vignette IS the entire case for a subclaim, with no reason or evidence alongside |
| **NE2** | Vignette-claim mismatch | Narrative supports a different claim than the one it's placed near; evidence is real but misrouted |
| **NE3** | Emotional override | Narrative's emotional power masks a logical weakness in the support chain; removing the vignette reveals the gap |

**Cross-reference with Franklin Steps 1–4:** When this audit runs on Classification 3 material, Franklin Steps 1–4 run on each embedded narrative segment separately to verify internal spine. The NE-codes test the *argumentative function* of those segments — whether they're doing structural work in the argument, not just whether they have internal narrative coherence.

**Output:** Vignette inventory + function classification + NE-codes for any failures.

---

## Common Patterns

Named diagnostic patterns this audit is designed to catch.

### Pattern FM-A1: The Drive-By Thesis

**Signature:** CL0 or CL1 + SM0 across multiple subclaims.

The writer has many interesting things to say and says them well. But there's no stable main claim. Each section makes a different point; the piece is a tour of the writer's thinking, not an argument. Common in smart writers who assume their conclusion is self-evident — they've internalized the argument so thoroughly that they skip the structure. The reader sees impressive observations that don't add up.

### Pattern FM-A2: The Evidence Pile

**Signature:** SM passes (evidence is present and relevant) + CL2 (subclaim gap) or BP2 (scope creep).

Lots of evidence, correctly matched to subclaims — but the subclaims don't add up to the main claim, or the evidence supports a narrower conclusion than the text asserts. The argument looks rigorous from inside any single section. The structural failure is in the connections between sections. Common in policy writing and data-driven journalism.

### Pattern FM-A3: The Persuasion Machine

**Signature:** OB0 (no objections engaged) + NE1 (vignettes substitute for argument) + NE3 (emotional override).

No objections addressed, and narrative does the heavy lifting where reasons should. Each vignette is devastating; together they create conviction without justification. Removing the vignettes reveals there's no argument underneath. Common in advocacy journalism, fundraising appeals, and op-eds written under deadline pressure. Not inherently dishonest — often the writer believes deeply and hasn't separated their conviction from their evidence.

### Pattern FM-A4: Scope Inflation

**Signature:** BP0 (scope undeclared) + BP2 (scope creep).

The evidence supports "in this case" or "sometimes." The conclusion asserts "always" or "we must." The gap is invisible to the writer because they've lived with the material long enough that the particular feels universal. Common in all argument-shaped writing, and nearly universal in first drafts. Often the easiest pattern to fix — the writer just needs to match their conclusion to their evidence.

### Pattern FM-A5: The Hidden Argument

**Signature:** AT0 (type undeclared) + piece classified as narrative (F1/F2/F3) by Nonfiction Craft audit but functioning as argument.

The piece presents itself as story, inquiry, or profile, but is actually arguing a position. The argument is embedded in selection, framing, and juxtaposition rather than stated as claim/evidence. Not inherently a flaw — narrative argument is a legitimate form. But the disguise prevents the reader from evaluating the claims on argumentative terms. The reader absorbs a conclusion without having been invited to weigh the evidence. If the argument is strong, making it legible strengthens it. If it's weak, the narrative disguise is hiding the weakness.

---

## Genre Calibration

### By Argument Form

**Op-ed / Column (short, < 1,500 words):** Claim ladder must be tight — one C0, one or two subclaims. Support may be light but must be present. Objection handling can be brief (a concessive clause) but OB0 is still a failure for AT2/AT3 pieces. NE-codes are high-value: at this length, a single vignette carries enormous weight.

**Policy Brief / Memo:** AT3 is expected. Full support map required. BP-codes are critical — scope discipline matters because the audience will act on the argument. Objection handling must address the strongest counter-proposal. Vignettes function as illustration, not evidence (the data should do the evidential work).

**Testimony (written or oral):** AT4 is primary. Claim ladder may be implicit (the claims emerge from the testimony). Support is first-person observation — BP1 mismatch is expected and acceptable for the observational layer. But interpretive claims ("this shows that the system is broken") carry AT2/AT3 burden and require support beyond personal experience. NE-codes: the testimony itself is a vignette, so tag interpretive moves vs. factual witness carefully.

**Academic / Scholarly Article:** Full diagnostic applies at highest standard. CL0 is disqualifying. SM3 (single-type dependence) is a common weakness. OB-codes are critical — the audience expects adversarial engagement with the literature. BP-codes: scope discipline is the mark of mature scholarship; scope inflation is the mark of student work. NE-codes rarely apply (academic arguments rarely embed narrative), but when they do (case studies in applied fields), NE1 and NE3 matter.

**Personal Essay (argument-shaped):** AT4 or AT2 typically. The claim ladder may be implicit, emerging through reflection rather than stated as thesis. This is legitimate — personal essays earn their claims through experience, not through explicit argument structure. Apply CL-codes loosely: flag CL0 only if the reader genuinely can't identify what the essay is about, not merely because the claim isn't stated as a sentence. OB-codes: personal essays may legitimately decline to engage objections from outside the essay's experiential frame.

**Advocacy Journalism / Long-Form Argument:** Full diagnostic applies. FM-A3 (The Persuasion Machine) is the signature risk. The writer's conviction is genuine; the diagnostic question is whether the argument is structurally honest. NE-codes matter most here: does the narrative do argumentative work, or does it substitute for argument?

### Calibration for Length

- **Short form (< 1,500 words):** Expect 1–2 subclaims. Support map may be compressed. One vignette may carry the piece. LC/E codes from Nonfiction Craft matter — the lead must establish the argument quickly.
- **Mid-length (1,500–5,000 words):** Full audit applies. 2–3 subclaims expected. Objection handling should be substantive, not gestural. Multiple vignettes require individual tagging.
- **Long form (> 5,000 words):** Expect 3+ subclaims and possibly nested sub-arguments. Support map may require per-section tracking. BP-codes are highest-value at this length (scope creep accumulates over distance). Full objection handling expected.

---

## Scope Selection

### Default Scope

| Component | What to Sample | How Many |
|-----------|---------------|----------|
| Opening | First 3–5 paragraphs (where the claim should emerge) | 1 |
| Body sections | Representative sections containing subclaims + evidence | 2–3 |
| Concessive moves | Passages where the text addresses objections or limits | All |
| Narrative segments | Vignettes, cases, anecdotes embedded in argument | All |
| Closing | Final section (where the claim should be cashed out) | 1 |

Steps 1 (Argument Type) and 2 (Claim Ladder) run on the whole piece. Steps 3–6 sample strategically within the scope above.

### When to Expand

- If CL1 (claim unstable) fires → track the claim as stated in every section to map the drift
- If SM0 (missing support) fires on multiple subclaims → expand to full evidence inventory
- If NE-codes fire on sampled vignettes → expand to all narrative segments

---

## Integration with Core Framework

### Module Position

This is a specialized audit invoked by the Franklin Pathway (Classification 3 or 4 redirect) or loaded directly when intake identifies argument-shaped material. It stacks with other audits — particularly the Narrative Nonfiction Craft audit for hybrid material.

### Relationship to Franklin Pathway

**Franklin is the gate; this audit handles what Franklin's story-spine tools can't.**

Franklin's Classification 3 (Argument With Embedded Narrative) identifies material where argument dominates and narrative is used as evidence. Previously, Classification 3 produced a stub output (claim/stakes/evidence ladder/narrative placement). This audit replaces that stub with a full diagnostic.

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

- **This audit** handles the argument structure: claim ladder, support map, burden of proof, objection handling.
- **Narrative Nonfiction Craft** handles the reader experience: lead contract (LC-codes), question management (QS-codes for embedded questions), ending payoff (E-codes), and meaning line (SW-codes — though in argument, the meaning line IS the argument, so SW-codes recede).

They are complementary. This audit asks "is the argument valid?" Nonfiction Craft asks "does the reader stay engaged?"

### Relationship to Character Architecture Part 9

Part 9 (Moral Argument Architecture) tests whether a **story** argues a moral position through character action — weakness, need, opponent-as-counter-argument, moral choice. This audit tests whether a **non-story** argues a position through claim-evidence structure.

For pieces that contain both (memoir with argument, narrative journalism with a thesis), both may apply. Part 9 diagnoses the story layer. This audit diagnoses the argument layer. The M-codes (moral argument hypothesis) and the CL-codes (claim ladder) may produce different formulations of "what this piece argues" — and if they conflict, that's diagnostic: the story argues one thing and the explicit argument argues another.

### Relationship to Banister Audit

The Banister audit tests epistemic humility and moral complexity in fiction — whether the work honors genuine difficulty and avoids false resolution. This audit tests argumentative clarity and objection handling in non-fiction argument.

**Banister asks:** "Does the story honor complexity?"
**This audit asks:** "Does the argument handle objections?"

For advocacy journalism, testimony, or policy arguments that touch contested moral terrain, both may be relevant. The Banister audit prevents the fiction layer from becoming propaganda; this audit prevents the argument layer from becoming dogma.

### Pass Modifications

**Pass 1 (Reader Experience):** When flagging "I don't know what the argument is" or "the piece shifts between claiming and narrating," add as Dialectical Clarity trigger. CL-codes and AT-codes diagnose the mechanism.

**Franklin Pipeline Integration (Classification 3):** Replace the stub argument output (claim/stakes/evidence ladder/narrative placement) with: "Invoke the Dialectical Clarity Audit on the argument structure. Run Franklin Steps 1–4 on embedded narrative segments."

### Orchestration with Other Audits

**With Narrative Nonfiction Craft:** For F5 material, run both. This audit handles argumentative validity; Nonfiction Craft handles reader contract and engagement. If the argument is valid but unreadable, Nonfiction Craft diagnoses why. If the argument reads well but is structurally unsound, this audit diagnoses why.

**With Scene Turn Diagnostics:** Scene Turn handles fiction scene mechanics. For Classification 3 material, embedded narrative segments may be checked by Scene Turn (if they contain goal-conflict-outcome scenes) while the argument frame is checked by this audit. The two operate on different layers of the same piece.

**With Emotional Craft Diagnostics:** An argument can be logically sound but emotionally dead — or emotionally powerful but logically empty. If Emotional Craft shows flat affect in argument-shaped sections (S-codes firing), the issue may be that the writer is suppressing voice to sound "objective." If Emotional Craft shows high emotional transmission alongside NE3 (emotional override), the issue is the opposite: feeling is substituting for reasoning.

### Output Delivered

The full audit produces:

1. **Argument Type & Promise** (Step 1: AT-code + burden level + promise)
2. **Claim Ladder** (Step 2: C0 + C1–C3 + stakes claim + CL-codes)
3. **Support Map** (Step 3: per-subclaim evidence inventory + support types + SM-codes)
4. **Burden of Proof & Scope** (Step 4: claim scope vs. evidence scope + BP-codes)
5. **Objection Handling** (Step 5: 2–4 objections inventoried + engagement quality + OB-codes)
6. **Narrative-as-Evidence Inventory** (Step 6: per-vignette function classification + NE-codes)

### Coaching in the Editorial Letter

The diagnostic procedure identifies structural failures with specific codes. When the editorial letter is written, it may include coaching guidance — explaining why scope discipline matters, how objection handling builds rather than undermines the argument's authority, what "narrative as substitute" looks like from the reader's perspective, or how an unstable claim ladder creates the feeling of "smart but inconclusive." This coaching belongs in the deliverable, not in the diagnostic specification.

---

*This audit diagnoses argumentative structure in non-narrative material — whether the claim is identifiable, the evidence supports it, the scope is honest, the objections are engaged, and narrative does argumentative work rather than substituting for it. It extends the Editor's coverage from story-spine diagnosis to argument-spine diagnosis, filling the gap that previously left Classification 3 and Classification 4 material without productive structural tools. The system diagnoses the argument's structure; the writer provides the claims, the evidence, and the intellectual honesty.*
