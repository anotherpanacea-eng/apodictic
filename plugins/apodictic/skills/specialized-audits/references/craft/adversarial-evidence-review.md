# Companion Module: Adversarial Evidence Review (v1.0)
## Nonfiction Argument Engine / APODICTIC
*Synthesized: March 24, 2026*
*Source: Adversarial collaboration between Claude Opus 4.6 (Anthropic) and Codex (OpenAI o3)*
*Architecture: Codex. Survivability layer, hostile-expert voice, grounding language: Claude.*
*Adjudicated by: Joshua Miller*
*Level-setting: `docs/adversarial-evidence-level-setting.md`*
*Consumes: `Argument_State.md` + `Evidence_Ledger.md` + `Citation_Ledger.md` + `Field_Reconnaissance_Report.md`*
*Produces: `Adversarial_Evidence_Preparation_Guide.md` + `Argument_State.md` § 10.8 annotations*

---

## §1. Purpose

Pressure-test whether a manuscript's evidence bears the weight its argument puts on it. Not whether the evidence exists (Citation Verifier), not whether the evidence portfolio is balanced (Argument Evidence), not whether the argument is structurally sound (Dialectical Clarity), and not what the strongest opposing case would be (Red Team). This module asks a narrower question:

**For each claim-evidence pairing that carries argumentative weight: would the inferential link survive a hostile expert who knows the source material?**

The module applies three formalized adversarial protocols — Analysis of Competing Hypotheses (ACH), legal cross-examination taxonomy, and severe testing (Mayo) — grounded in external data from upstream modules. It produces localized, grounded attacks with survivability judgments, organized as preparation for independent review.

### What this module is

An evidence stress-test. It takes the diagnostic outputs of the Nonfiction Argument Engine's other modules (codes, ledgers, reports) and asks what a hostile expert — a peer reviewer, a cross-examining attorney, a legislative staffer with domain knowledge — would do with each claim-evidence pairing. Every attack must cite its grounding source. Every attack must be localized to a specific passage. The output is a preparation guide, not a verdict.

### What this module is not

- **Not a second Red Team.** Red Team builds the strongest opposing *case* — opposition memos, adversary personas, full countercases. This module attacks individual *evidence nodes*. It does not construct countercases or audience-framed rhetorical attacks.
- **Not a replacement for independent review.** The level-setting research (Huang et al. ICLR 2024; Basil & Shapiro SSRN 2025) establishes that LLM self-critique without external grounding degrades performance, and persona prompting changes tone without changing the distribution of substantive findings. This module uses task structure and external grounding to partially compensate, but it cannot replicate genuine epistemic independence.
- **Not a diagnostic module.** Dialectical Clarity and Argument Evidence diagnose. This module attacks. The difference: a diagnostic code says "WR1 — missing backing for contested warrant." This module says "Here is the specific counter-evidence a hostile reviewer would cite, here is the specific inferential gap they would exploit, and here is whether the claim survives the attack."

### When to activate

- After Dialectical Clarity, Argument Evidence, Citation Verifier (Phase 2), and Field Reconnaissance have all run
- When the manuscript is heading toward publication, testimony, or legislative advocacy
- When Dialectical Clarity fires WR1, WR3, BP5, or OB3
- When Argument Evidence fires AE3, AE4, AE7, AE8, AE9, or AE10
- When Field Reconnaissance returns ADDRESS-level counterevidence
- When the author asks: "What would a hostile reviewer do with my evidence?"

---

## §2. Firewall and Scope

This module produces adversarial evidence analysis, not argument content.

### Allowed

- Reviewing claim-evidence pairings explicitly anchored in upstream artifacts
- Testing whether cited evidence discriminates between the manuscript's claim and live alternatives
- Applying ACH, legal cross-exam, and severe-testing protocols to the same evidence packet
- Using external artifact citations from Citation Verifier, Field Reconnaissance, and domain-standard frameworks
- Ranking vulnerabilities by convergence and damage potential
- Assigning survivability judgments and dispositions
- Annotating `Argument_State.md` with evidence-specific attack summaries

### Not allowed

- Constructing a rival case or countercase
- Writing an opposition memo
- Producing audience-framed rhetorical attacks
- Inventing evidence nodes or rival hypotheses not grounded in upstream artifacts
- Re-running citation resolution, literature search, or factual verification
- Re-diagnosing claim structure already owned by Dialectical Clarity
- Recommending replacement sources or rewriting evidence sections
- Suggesting what the argument *should* be
- Firing attacks based on intrinsic reasoning alone (every attack must cite an external grounding source)

### The Scope in Practice

- ❌ NOT ALLOWED: "A hostile committee member would say your whole policy is naive because the opposition has a stronger narrative."
- ✅ ALLOWED: "C1 relies on EL-04 plus CV Ref 7. The evidence packet is equally consistent with a narrower rival explanation identified in FR-C1-2. The hostile expert says: 'Your own source supports a weaker conclusion than you draw.' Code: HX1."
- ❌ NOT ALLOWED: "Write a stronger concession paragraph."
- ✅ ALLOWED: "The packet supporting C0 survives citation verification but fails severe-testing pressure on transportability. The hostile expert says: 'This is Cook County in the 1990s. You're proposing policy for DC in 2026.' Code: SX5. Disposition: ADDRESS."

---

## §3. Non-Duplication Boundary

### Existing modules own

| Module | Owned territory |
|--------|-----------------|
| **Dialectical Clarity** | Claim architecture, support mapping, warrant diagnosis, burden and scope, objection handling |
| **Argument Evidence** | Provenance chains, portfolio balance, testimony calibration, quantitative integrity, verification queue |
| **Citation Verifier** | Source existence, metadata sufficiency, quote/paraphrase fidelity, citation-to-claim fit |
| **Field Reconnaissance** | Counterevidence search, literature gaps, source ecosystem health |
| **Argument Red Team** | Countercase construction, broad vulnerability ranking, opposition memo, rhetorical and strategic attack surface |

### Adversarial Evidence Review owns

1. **Evidence-node adversarial pressure**: whether a mapped evidence packet survives structured attack once upstream diagnostics and research have already grounded the packet
2. **Protocol convergence**: where ACH, cross-exam, and severe-testing frameworks independently attack the same claim-evidence pairing
3. **Survivability judgments**: whether a claim-evidence pairing survives, is weakened, or does not survive structured adversarial pressure
4. **Preparation disposition**: whether the author should ADDRESS, ACKNOWLEDGE, or ACCEPT a localized evidence vulnerability before external review
5. **Domain-standard attack translation**: how GRADE, RoB 2, ROBINS-I, FRE 702, or humanities/theory standards change the severity of a localized evidence attack

### Sharp boundary with Red Team

This module may hand evidence-side pressure points to Red Team. It may not:

1. generalize those pressure points into a whole-argument opposition case
2. build alternative policy packages or rival narratives
3. simulate a hostile audience voice
4. turn evidentiary pressure into rhetorical advice

**Red Team asks:** "How does a prepared adversary attack the argument?"
**Adversarial Evidence Review asks:** "How does a prepared adversary attack this evidence packet?"

### Non-duplication enforcement

| If the analysis starts doing this... | Stop. It belongs to... |
|--------------------------------------|----------------------|
| Building a full opposing case | Red Team |
| Diagnosing warrant gaps without attacking them | Dialectical Clarity |
| Checking whether citations are accurate | Citation Verifier |
| Searching for new counterevidence | Field Reconnaissance |
| Assessing evidence portfolio balance | Argument Evidence |
| Suggesting what the author should argue | Firewall violation |

---

## §4. Preconditions and Run Modes

### Required inputs

All four artifacts are mandatory:

1. `Argument_State.md` — §§ 1–9 populated by Dialectical Clarity, § 10.1 by Argument Evidence
2. `Evidence_Ledger.md` — evidence analysis complete
3. `Citation_Ledger.md` — **Phase 2 complete** (the module requires source-reality data from Phase 2 fit assessments; Phase 1 alone is insufficient)
4. `Field_Reconnaissance_Report.md` — counterevidence search complete

If any are absent, stale, or materially incomplete, refuse to run. If `Citation_Ledger.md` has only Phase 1 data, refuse and direct the user to run Phase 2 on load-bearing citations before proceeding.

### What the module reads

From `Argument_State.md`:
1. § 1 — Context and Classification (audience, consequence context)
2. § 2 — Claim Architecture (C0–C7+)
3. § 3 — Support Map
4. § 4 — Warrant and Inference Map (WR codes)
5. § 5 — Burden, Scope, and Comparative Assessment (BP codes)
6. § 9 — Diagnostic Summary
7. § 10.1 — Evidence Analysis (AE codes)
8. § 10.6 — Citation Verification
9. § 10.7 — Field Reconnaissance

From `Evidence_Ledger.md`:
1. Evidence corridor selection
2. Provenance notes
3. Testimony and quantitative integrity findings
4. Node-level findings tied to AE codes

From `Citation_Ledger.md`:
1. Phase 2 content-fit results (MATCH / PARTIAL / MISMATCH)
2. Source-reality data (what the source actually says vs. manuscript characterization)
3. Flagged citation details and repair status

From `Field_Reconnaissance_Report.md`:
1. Counterevidence items per claim (with ADDRESS / ACKNOWLEDGE / SET ASIDE)
2. Temporal, methodological, and perspectival gap findings
3. Source ecosystem health flags

### Packet eligibility

The module reviews only evidence packets that meet all of the following:

1. The packet is attached to C0 or a named subclaim (C1+)
2. The packet has a corresponding entry in `Evidence_Ledger.md`
3. The packet has at least one mapped citation with Phase 2 data in `Citation_Ledger.md`
4. The packet has at least one external challenge input: counterevidence, gap signal, or domain-standard pressure

Additionally, all unflagged C0 and central-subclaim supports are eligible regardless of whether diagnostic codes fired, since the TAY White Paper test revealed that some vulnerabilities only emerge under adversarial pressure.

### Run modes

| Mode | When allowed | Requirements | Output consequence |
|------|-------------|-------------|--------------------|
| **Fresh-Session Review** | Default; required for all high-consequence reviews | Must run in a new session not used to draft or revise the argument | Full tiering available (Provisional and Elevated) |
| **Same-Session Convenience Review** | Low/medium-consequence exploratory review only | Same four artifacts still required | Downgrade language required; Elevated requires stronger corroboration (see §7) |

### High-consequence rule

Fresh-session review is **mandatory** when any of the following are true:

1. `Argument_State.md` § 1 marks consequence context as HIGH
2. The form is testimony, white paper, policy brief, or academic article intended for submission
3. The domain pack is clinical/public health or legal/policy analysis
4. The draft includes living-person, regulatory, or public-safety stakes

**If any of these apply and the run is same-session, refuse to run.** (Hard Gate HG-AER2.)

---

## §5. Code Namespace

Three code families, one per adversarial protocol. This preserves provenance of which protocol generated the finding — when two families converge on the same packet, the convergence is visible in the codes.

- `HX` — ACH / competing-hypothesis pressure
- `LX` — legal cross-examination pressure
- `SX` — severe-testing pressure

**No collisions with existing code systems:** AT, CL, SM, WR, BP, OB, NE, DI, AC, AE, CV, EV, RT.

### Severity tiers

| Tier | Meaning | Criteria |
|------|---------|----------|
| **Provisional** | One protocol family fires with valid grounding | May or may not appear in independent review |
| **Elevated** | Protocol convergence or protocol plus strong external corroboration | Likely to appear in independent review |

### Survivability judgments

| Judgment | Meaning |
|----------|---------|
| **Survives** | The attack is grounded but the evidence is strong enough to withstand it |
| **Weakened** | The attack lands but the claim can be defended with qualification, additional evidence, or honest acknowledgment |
| **Does not survive** | The inferential link breaks under adversarial pressure; the claim needs different evidence, narrower scope, or explicit concession |

### Disposition buckets

| Disposition | When to assign |
|-------------|---------------|
| **ADDRESS** | Repair before external review. Does-not-survive + Elevated; or any hard gate trigger. |
| **ACKNOWLEDGE** | Disclose, qualify, or bound if keeping the evidence. Weakened + Elevated; or Provisional but obviously exploitable. |
| **ACCEPT** | Intentional, bounded, low-blast-radius risk the author may knowingly carry. Survives; or weakened + Provisional with bounded scope. |

---

## §6. Domain Packs

Every evidence packet receives one primary domain pack. Domain packs modify how HX, LX, and SX codes are interpreted — they do not create separate code families.

| Domain pack | Primary standards | Tightens on | Typical attack pressure |
|------------|-------------------|-------------|-------------------------|
| **Clinical / public health** | GRADE, RoB 2, ROBINS-I | Indirectness, imprecision, publication bias, confounding, causal overreach | Weak causal claims from observational data; low-certainty evidence carrying decisive recommendations |
| **Social science / policy** | GRADE-adapted, ROBINS-I, measurement-validity norms, scite context where available | Representativeness, confounding, implementation transport, ecological inference | Narrow or context-bound findings generalized into policy certainty |
| **Legal / policy analysis** | FRE 702, sufficient-facts / reliable-method / fit standards, jurisdictional relevance | Qualification stretch, authority fit, methodological reliability, cross-jurisdiction transport | Expert or institutional authority used beyond domain or without method-fit |
| **Humanities / theory** | Severe-testing of interpretation, counterposition engagement, corpus sufficiency, historical-context fit | Selective quotation, corpus thinness, rival interpretation fit, conceptual overreach | Interpretation asked to bear more than the corpus or textual warrant can sustain |

### Pack-selection rules

1. Use the manuscript's dominant domain from `Argument_State.md` § 1 when clear.
2. If the argument mixes domains, choose the pack attached to the reviewed claim-evidence pairing, not the manuscript as a whole.
3. If a packet genuinely spans two domains, apply one primary pack and note one secondary overlay in the packet header. Do not blend standards silently.

### Pack-specific escalation examples

- Clinical/public health: GRADE downgrades on indirectness plus imprecision raise SX2 or SX3 from Provisional to Elevated.
- Social science/policy: strong confounding risk or weak external validity raises SX5.
- Legal/policy analysis: unreliable method fit or authority beyond domain raises LX4.
- Humanities/theory: rival interpretation strongly fits the same cited corpus raises HX1.

---

## §7. Named Codes

### ACH / competing-hypothesis pressure (`HX`)

| Code | Name | The hostile expert says: |
|------|------|--------------------------|
| **HX1** | Rival Fit | "Your own source supports a weaker conclusion than you draw. The same evidence is at least equally consistent with [rival explanation from upstream artifacts]." |
| **HX2** | Non-Discriminating Support | "This evidence supports the topic but doesn't distinguish your claim from nearby alternatives. It's consistent with everything, which means it proves nothing specific." |
| **HX3** | Missing Expected Disconfirmer | "If your claim were false, we'd expect to see [specific contrary signal]. Your evidence never tests for it." |
| **HX4** | Counterevidence Absorption Failure | "Field Recon surfaced [specific published challenge]. Your evidence packet doesn't discriminate against it, even though your citations are accurate." |

### Legal cross-examination pressure (`LX`)

| Code | Name | The hostile expert says: |
|------|------|--------------------------|
| **LX1** | Capacity Box-In | "Your source couldn't directly observe, measure, or know the point you're asking it to prove. Wrong population, wrong context, wrong measurement instrument." |
| **LX2** | Timeframe Trap | "This evidence is from [year/period]. You're proposing policy for [different year/context]. What happened in between?" |
| **LX3** | Stake Exposure | "The researchers who produced this finding have [funding/institutional/advocacy stake]. How does this differ from the developer-dependence you criticize in other programs?" |
| **LX4** | Qualification Stretch | "You're asking [source/authority] to speak beyond their domain competence or observational warrant." |
| **LX5** | Inconsistency Trap | "The source chain conflicts with itself. In [location A] you characterize the finding as X; in [location B] or in the source's own text, it says Y." |
| **LX6** | Authority Collision | "A stronger, more relevant, or more direct authority exists and points elsewhere. [Specific source from upstream record]." |

### Severe-testing pressure (`SX`)

| Code | Name | The hostile expert says: |
|------|------|--------------------------|
| **SX1** | Easy-Test Pass | "This evidence passed only a weak test. It would likely look the same even if your claim were wrong." |
| **SX2** | Proxy Escape | "A proxy or indirect measure is doing the work of direct evidence without enough bridge support." |
| **SX3** | Null-Compatible Support | "This evidence doesn't clearly discriminate between your claim and a null or weaker interpretation." |
| **SX4** | Selection Vulnerability | "Publication, survivorship, or source selection makes the evidence look stronger than it is." |
| **SX5** | Transport Stretch | "This is [jurisdiction/population/period]. You're claiming it applies to [different jurisdiction/population/period]. Where's the bridge?" |

---

## §8. Review Procedure

Eight steps. Steps 1-3 validate and build targets. Steps 4-6 run the three protocols in parallel. Step 7 converges findings. Step 8 produces outputs.

### Step 1: Validate artifacts and run mode

1. Confirm all four required artifacts exist and are aligned to the same manuscript state
2. Confirm `Citation_Ledger.md` includes Phase 2 data for load-bearing citations
3. Determine whether the run is Fresh-Session or Same-Session Convenience
4. If high-consequence rules apply and the run is same-session, **refuse to run** (HG-AER2)

### Step 2: Build evidence attack packets

For each eligible pairing, construct:

```markdown
Packet ID: AER-[N]
Claim target: [C0 / C1 / C2 / ...]
State references: [§ 2 claim, § 3 support node, § 4 warrant status]
Evidence ledger reference: [EL-ID]
Citation references: [CV Ref IDs]
Source reality: [what the source actually says — from Citation Ledger Phase 2]
Manuscript characterization: [how the manuscript describes the evidence]
Field Recon references: [FR item IDs, if any]
Upstream codes: [any WR, BP, AE codes already fired]
Domain pack: [clinical / social science / legal / humanities]
Load: [decisive / load-bearing / supporting]
Consequence context: [LOW / MEDIUM / HIGH]
```

### Step 3: Prioritize packets

Review in this order:
1. Packets attached to C0
2. Packets attached to highest-severity subclaims from `Argument_State.md` § 9
3. Packets flagged by AE3, AE4, AE7, AE8, AE9, AE10
4. Packets with CV non-pass verdicts or caveats
5. Packets tied to Field Recon items marked ADDRESS
6. Unflagged C0 and central-subclaim supports (catch vulnerabilities that diagnostic codes missed)

If the manuscript has many packets, review only the top corridor rather than skimming everything shallowly.

### Step 4: Run ACH pressure (`HX`)

For each packet:

1. State the manuscript's hypothesis
2. Identify one narrower or competing explanation from Field Recon or the manuscript's own support map
3. Identify one null or low-commitment alternative where applicable

Score the packet against each:
- CONSISTENT / MIXED / NON-DIAGNOSTIC / INCONSISTENT

Fire HX codes only when the packet fails to discriminate meaningfully.

**ACH rule:** A rival hypothesis must come from upstream artifacts or domain-standard alternatives. Do not invent speculative rivals.

```markdown
ACH — AER-[N]:
  Manuscript hypothesis: [...]
  Rival 1: [...] (source: FR-C1-2)
  Null alternative: [...]

  Packet consistency:
    With manuscript: [consistent / mixed / non-diagnostic / inconsistent]
    With rival: [...]
    With null: [...]

  Disconfirmation test: [what would falsify the manuscript's claim?]
  Status: [tested / untested / untestable]

  Code: [HX code or PASS]
  Grounding: [specific upstream artifact or domain standard]
```

### Step 5: Run legal cross-examination pressure (`LX`)

Apply the six attack vectors:

| Vector | Question | Maps to |
|--------|----------|---------|
| Perceptive capacity | Could this source observe what it claims? | LX1 |
| Temporal adequacy | Is this evidence current enough? | LX2 |
| Stake or bias exposure | Does the source have conflicts? | LX3 |
| Qualification fit | Is the source credible on this specific point? | LX4 |
| Internal consistency | Does the source chain conflict with itself? | LX5 |
| Authority collision | Do stronger sources disagree? | LX6 |

Use Citation Ledger and Evidence Ledger as the factual base. If the attack depends on source fidelity, cite the specific `Citation_Ledger.md` entry.

```markdown
CROSS-EXAM — AER-[N]:
  Vector: [which of the six]
  Attack: [the specific question a hostile expert would ask]
  Manuscript answer: [what the manuscript says or implies]
  Source answer: [what the evidence actually supports — from Citation Ledger Phase 2]
  Gap: [the specific inferential gap]

  Code: [LX code or PASS]
  Grounding: [Citation Ledger entry, Field Recon item, or published standard]
```

### Step 6: Run severe-testing pressure (`SX`)

For each packet:

1. What would this evidence probably look like if the manuscript's claim were false?
2. Would the current packet have detected that failure?
3. Is the packet direct enough, precise enough, and context-fit enough for the burden it carries?
4. Apply the appropriate domain pack.

```markdown
SEVERE TEST — AER-[N]:
  Claim: [...]
  Evidence: [...]
  Test severity: [HIGH / MODERATE / LOW / UNTESTED]

  If HIGH: [describe the test and why it was severe]
  If MODERATE: [what limits severity]
  If LOW: [what a more severe test would look like]
  If UNTESTED: [the claim has not been subjected to a test that could have found it false]

  Domain standard applied: [GRADE / RoB 2 / ROBINS-I / FRE 702 / conceptual severity]
  Code: [SX code or PASS]
  Grounding: [published standard or methodological source]
```

### Step 7: Converge findings, assign tier, survivability, disposition

For each packet:

**1. Collect** all fired HX, LX, and SX codes.

**2. Assign severity tier:**

| Tier | Criteria |
|------|----------|
| **Provisional** | One protocol family fires with both an internal anchor and an external artifact citation; no second protocol converges |
| **Elevated** | Two or more protocol families independently fire; OR one protocol fires plus Field Recon has a directly relevant ADDRESS item; OR one protocol fires plus domain pack indicates standards failure; OR one protocol fires on a decisive C0 packet in high-consequence fresh-session mode with no stronger adjacent support |

**Same-session downgrade rule:** In Same-Session Convenience mode, no finding may be marked Elevated unless (a) at least two external artifacts corroborate it AND (b) at least two protocol families converge. Otherwise it remains Provisional.

**3. Assign survivability:**

| Judgment | Criteria |
|----------|----------|
| **Survives** | Attack is grounded but evidence withstands it — the hostile expert's attack can be rebutted with existing evidence |
| **Weakened** | Attack lands but claim can be defended with qualification, additional evidence, or honest acknowledgment |
| **Does not survive** | Inferential link breaks — claim needs different evidence, narrower scope, or explicit concession |

**4. Assign disposition** (maps from survivability + tier):

| | Provisional | Elevated |
|---|------------|----------|
| **Survives** | ACCEPT | ACCEPT |
| **Weakened** | ACCEPT or ACKNOWLEDGE | ACKNOWLEDGE |
| **Does not survive** | ACKNOWLEDGE | ADDRESS |

Hard gate triggers override to ADDRESS regardless of tier (see §9).

### Step 8: Write outputs

Produce two artifacts:

1. `Adversarial_Evidence_Preparation_Guide.md` (primary deliverable)
2. `Argument_State.md` § 10.8 annotation (state update)

---

## §9. Hard Gates

| Gate | Condition | Result |
|------|-----------|--------|
| **HG-AER1** | Any required artifact is missing, stale, or not aligned to the same draft | Refuse to run |
| **HG-AER2** | High-consequence review attempted in same-session mode | Refuse to run; require fresh session |
| **HG-AER3** | A finding lacks both an internal anchor and at least one external-artifact citation | Drop the finding; it cannot appear in output |
| **HG-AER4** | A decisive C0 packet receives Elevated finding and no stronger adjacent packet offsets the same claim path | ADDRESS before persuasion, compression, or Red Team escalation |
| **HG-AER5** | Two or more Elevated findings from different protocol families converge on the same claim path | ADDRESS and recommend independent expert review |
| **HG-AER6** | Clinical/public-health or social-science/policy pack indicates low-certainty or method-compromised evidence carrying a decisive causal or policy claim | ADDRESS; route to expert review if publication stakes are high |
| **HG-AER7** | Testimony or legal/policy packet receives LX4 plus SX5 on a central claim | ADDRESS; witness or authority is being asked to speak beyond warranted scope |

---

## §10. Output Format

### `Adversarial_Evidence_Preparation_Guide.md`

```markdown
# Adversarial Evidence Preparation Guide
## [Manuscript title]
_Adversarial Evidence Review v1.0_
_Date: [date]_
_Run mode: [FRESH-SESSION REVIEW / SAME-SESSION CONVENIENCE REVIEW]_

---

## Independence Note
[Required disclosure language — see below]

---

## Review Scope
- Packets reviewed: [N]
- Domain packs used: [list]
- Highest-consequence corridor: [claim path]

---

## ADDRESS Before External Review
| # | Packet | Claim | Codes | Tier | Survivability | Why it lands | Grounding |
|---|--------|-------|-------|------|---------------|--------------|-----------|
| 1 | AER-03 | C0 | HX1, SX5 | Elevated | Does not survive | [1-2 sentences] | [EL-03; CV Ref 7; FR-C0-2; ROBINS-I] |

---

## ACKNOWLEDGE If You Keep This Evidence
| # | Packet | Claim | Codes | Tier | Survivability | What must be acknowledged | Grounding |
|---|--------|-------|-------|------|---------------|---------------------------|-----------|

---

## ACCEPT as Intentional or Bounded Risk
| # | Packet | Claim | Codes | Tier | Survivability | Why survivable | Grounding |
|---|--------|-------|-------|------|---------------|----------------|-----------|

---

## Packet Detail
### AER-03
Claim target: [C0]
State anchors: [§ references]
Evidence ledger: [EL-ID]
Citations: [CV refs]
Field Recon: [FR refs]
Domain pack: [domain]

Protocol findings:
- ACH: [code or PASS — with hostile-expert quote]
- Cross-exam: [code or PASS — with hostile-expert quote]
- Severe testing: [code or PASS — with hostile-expert quote]

Tier: [Provisional / Elevated]
Survivability: [Survives / Weakened / Does not survive]
Disposition: [ADDRESS / ACKNOWLEDGE / ACCEPT]
Grounding:
- Internal anchors: [...]
- External artifacts: [...]
- Standards: [...]
```

### `Argument_State.md` § 10.8 annotation

```markdown
### 10.8 Adversarial Evidence Review
_Module: Adversarial Evidence Review v1.0_
_Run date: [date]_
_Run mode: [FRESH-SESSION REVIEW / SAME-SESSION CONVENIENCE REVIEW]_

Packets reviewed: [N]
Tier summary:
- Elevated: [N]
- Provisional: [N]

Survivability summary:
- Survives: [N]
- Weakened: [N]
- Does not survive: [N]

Disposition summary:
- ADDRESS: [N]
- ACKNOWLEDGE: [N]
- ACCEPT: [N]

Top packets:
1. [Packet ID] — [Claim target] — [codes] — [tier] — [survivability] — [disposition]
   Grounding: [EL-ID; CV refs; FR refs; standard]
2. [...]

Hard gates triggered: [gate IDs, or NONE]

Independence note:
[Fresh-session or convenience-mode disclosure]

Full results: see Adversarial_Evidence_Preparation_Guide.md
```

### Required disclosure language

**Fresh-session review:**

> This review used structured adversarial protocols and external artifacts, but it is model-generated analysis rather than independent expert review. LLM-only adversarial review is incomplete and should not be treated as a substitute for independent expert scrutiny. Treat Elevated findings as preparation targets, not as final judgments.

**Same-session convenience review:**

> This review was produced in the same session used for drafting or revision. It is a convenience read, not independent adversarial review. Findings are downgraded: Elevated requires corroboration by multiple external artifacts and multiple protocol families. Independent review is strongly recommended for all ADDRESS items.

---

## §11. Calibration by Form

| Form | Tighten on | Loosen on | Typical ADDRESS triggers |
|------|------------|-----------|--------------------------|
| **White paper** | Transfer across jurisdictions, gray-literature overreach, expert authority fit, implementation assumptions | Exhaustive academic apparatus | Decisive recommendation resting on thin or non-transferable evidence |
| **Testimony** | Cross-exam survivability, witness scope, statistic defensibility, observational vs. representative burden | Full literature coverage | LX4 or SX5 on central witness-driven evidence |
| **Academic article** | Methodological severity, rival-fit pressure, counterevidence absorption, domain-standard failure | Public-facing compression concerns | Packet passes citation verification but fails severe-testing or rival-fit pressure on core claim |
| **Policy brief** | Implementation transfer, confounding, selective use of studies, narrower rival policies | Exhaustive philosophical qualification | Strong policy recommendation resting on indirect or context-bound evidence |
| **Op-ed** | Decisive statistic or anecdote carrying whole corridor, scope stretch from vivid case, compression overreach | Formal bibliographic completeness | A single packet is overburdened into general policy certainty |
| **Humanities / theory** | Rival interpretation fit, corpus sufficiency, selective quotation, historical-context transport | Empirical-method expectations not native to the form | Interpretation depends on thin or unrepresentative textual base while stronger rival reading is live |

---

## §12. Integration and Handoff

### Upstream (reads from)

| Module | What it provides | How this module uses it |
|--------|-----------------|----------------------|
| **Dialectical Clarity** | Claim ladder, support map, WR/BP/OB codes | Target selection, attack surface identification |
| **Argument Evidence** | AE codes, portfolio analysis, provenance chains | Identifies portfolio-level vulnerabilities to exploit |
| **Citation Verifier** | Phase 2 fit assessments, source-reality data | Grounds attacks in what sources actually say |
| **Field Reconnaissance** | Counterevidence items, literature gaps | Provides external counter-evidence for attack grounding |

### Downstream (hands off to)

| Module | What it receives | What it does with it |
|--------|-----------------|---------------------|
| **Revision Coach** | Ordered ADDRESS / ACKNOWLEDGE / ACCEPT guide with survivability judgments | Plans revision sessions around the most serious attacks |
| **Persuasion** | Which evidence nodes are weakest | Advises on which evidence to foreground vs. qualify |
| **Red Team** | Evidence-side pressure points (ADDRESS and ACKNOWLEDGE items) | May consume as vulnerabilities but may not ask this module to generate countercases |

### To Factual Verification

Escalate only when a packet's vulnerability cannot be resolved because a real-world claim remains externally unsettled rather than structurally overburdened.

---

## §13. Token Budget

| Component | Tokens | Notes |
|-----------|--------|-------|
| Artifact read-in and packet assembly | 4-8K | Scales with packet count and artifact richness |
| Domain-pack selection and standards overlay | 2-4K | Mostly deterministic |
| ACH pass (per packet) | 2-3K | Matrix + alternative generation |
| Cross-exam pass (per packet) | 2-3K | Six-vector check + grounding |
| Severe-testing pass (per packet) | 2-4K | Most variable — domain packs add questions |
| Convergence, tiering, survivability, disposition | 4-7K | Includes three-dimensional assessment |
| Preparation guide + state annotation | 4-7K | Guide is the main artifact |
| **Total** | **~30-60K** | For 5-10 targets at ~7-10K per target + synthesis |

Typical runs:
- White paper, 5 decisive packets: ~34-44K
- Testimony, 4 central packets: ~30-40K
- Academic article, 8 packets across 3 claims: ~42-56K

---

## §14. Guardrails

1. Never review evidence that is not explicitly mapped to a claim.
2. Never invent rival hypotheses, contradictory authorities, or methodological standards not grounded in upstream artifacts or the selected domain pack.
3. Never elevate a finding without explicit grounding citations.
4. Never confuse citation-fidelity problems with inferential problems. Citation Verifier owns fidelity. This module starts *after* fidelity is settled.
5. Never suppress inferential attacks merely because a citation passed MATCH in Citation Verifier. Accurate citation is not the same as adequate evidentiary burden. This is the module's core function.
6. Never convert evidence pressure into audience rhetoric. Red Team owns rhetorical hostility.
7. Never punish informal forms for lacking academic apparatus if their burden is honestly bounded.
8. If a packet is strong, say so. A guide with few ADDRESS items is a legitimate outcome.
9. If the author is knowingly carrying a bounded evidentiary risk, use ACCEPT rather than inflationary failure language.
10. If same-session convenience mode is used, keep the downgrade language visible at the top of the artifact.
11. Calibrate severity honestly. Uniform-density criticism — flagging everything at the same severity regardless of actual evidence quality — is a known LLM failure mode. Resist it.
12. Respect the honest ceiling. This module is structurally weaker than an independent expert review. It should say so every time.

---

*The strongest evidence is evidence that has survived the strongest available attack. This module generates the attacks. The author decides whether to strengthen, qualify, or stand.*
