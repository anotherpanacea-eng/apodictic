# Argument State Schema
## Nonfiction Argument Engine — Shared Artifact Specification
*Version: 0.1.1*
*Status: Active*
*Last updated: March 19, 2026*
*Depends on: Dialectical Clarity v2.0*

---

## Purpose

Define the canonical shared representation of an argument so that every downstream mode (diagnosis, evidence analysis, persuasion coaching, red-team pressure, revision planning) reads and writes the same internal objects. Without this, each module rebuilds the argument from scratch on every handoff. With it, the engine becomes composable: the Dialectical Clarity audit populates the state, companion modules consume and annotate it, and the revision coach reads the annotated state to plan repair sequences.

**This document defines the schema. It does not define the modules that consume it.**

The artifact is emitted as `Argument_State.md` during a diagnostic run and persists in the project directory alongside the editorial letter and other APODICTIC outputs.

---

## Design Principles

1. **Single source of truth.** Every module that touches the argument reads from and writes to this artifact. No module maintains a private representation that diverges from the state.

2. **Populated incrementally.** The Dialectical Clarity audit fills Sections 1–8 during its 9-step diagnostic. Companion modules (evidence, persuasion, red-team) add annotations to the state rather than replacing sections. The revision coach reads the fully annotated state.

3. **Readable by humans.** The artifact is Markdown. A writer or editor who opens it can understand the argument's structural map without knowing APODICTIC internals. Code references (AT3, WR0, FM-A6) appear alongside plain-language explanations.

4. **Stable across modules.** Section numbering, field names, and object types are fixed by this schema. Modules may add annotation blocks (clearly marked) but may not redefine the core fields.

5. **Lightweight.** The state captures the argument's *structure*, not its content. It references the manuscript by location (section, paragraph, page) rather than quoting it at length. A typical Argument_State.md should be 150–400 lines depending on the argument's complexity.

---

## When the Artifact Is Created

The Dialectical Clarity audit creates `Argument_State.md` at the start of its run and populates it as each step completes. The file lives in the project directory alongside the editorial letter.

If companion modules run after the audit, they annotate the existing state file rather than creating a new one. Each annotation block is signed with the module name and timestamp.

If the audit runs again (e.g., on a revised draft), a new state file is created. The previous state is archived with a version suffix.

---

## Schema

### § 1. Context and Classification

Populated by: Dialectical Clarity Step 1.

```markdown
## 1. Context and Classification

Form: [op-ed / policy brief / testimony / academic article / personal essay /
       advocacy journalism / grant proposal / white paper / legal brief /
       book review / open letter / crisis communication / other: ___]

Goal: [what the piece is trying to accomplish — one sentence]

Argument type: [AT-code] — [type name]
  Promise: [what the reader expects to receive]
  Burden level: [LOW / MEDIUM / HIGH]

Audience:
  Expertise: [GENERAL / MIXED / EXPERT]
  Receptivity: [SYMPATHETIC / MIXED / HOSTILE]
  Consequence context: [LOW / MEDIUM / HIGH]

Distinguish classification: [SOUND / UNCONVENTIONAL-BUT-EFFECTIVE / UNSOUND]
  Form notes: [if unconventional, name the form and the basis for classification]

Fired codes: [AT-codes, AC-codes, or PASS]
```

**Field definitions:**

| Field | Source Step | Required | Notes |
|-------|-----------|----------|-------|
| Form | Intake / Step 1 | Yes | From the genre calibration list; "other" allowed with explanation |
| Goal | Step 1 | Yes | One sentence; extracted from the text, not invented |
| Argument type | Step 1 | Yes | AT0–AT4 |
| Audience | Step 1 | Yes | Three dimensions; drives calibration in all later sections |
| Distinguish classification | Step 9 | Yes | Backfilled after terminal step; may retroactively adjust codes |

---

### § 2. Claim Architecture

Populated by: Dialectical Clarity Step 2.

```markdown
## 2. Claim Architecture

C0 (main claim): [one sentence]

Subclaims:
  C1: [necessary subclaim]
  C2: [necessary subclaim]
  C3: [necessary subclaim]

Stakes: [why C0 matters]
  Stakes type: [CONSEQUENTIAL / MORAL / EPISTEMIC / PRACTICAL]

Key terms:
  T1: [term] = [operational meaning in the draft]
  T2: [term] = [operational meaning in the draft]

Fired codes: [CL-codes or PASS]
```

**Field definitions:**

| Field | Source Step | Required | Notes |
|-------|-----------|----------|-------|
| C0 | Step 2 | Yes | Must be extractable from text, not reviewer-supplied |
| C1–C3 | Step 2 | Yes (at least one) | Necessary links only; may be fewer than 3 |
| Stakes | Step 2 | Yes | Stated or strongly implied by the text |
| Key terms | Step 2 | When definitional pressure matters | Track terms whose meaning carries argumentative force |

**Downstream consumers:** Every module reads C0 and the claim ladder. The red-team module attacks C0 and its weakest subclaim. The persuasion module assesses which subclaim to foreground for the identified audience. The revision coach sequences repair by subclaim dependency.

---

### § 3. Support Map

Populated by: Dialectical Clarity Step 3.

```markdown
## 3. Support Map

C1: [subclaim]
  Support: [what the text offers]
  Support type: [REASON / EXAMPLE / DATA / AUTHORITY / EXPERIENCE]
  Scheme hint: [AUTHORITY / CONSEQUENCE / CAUSAL / ANALOGY / EXAMPLE /
                TESTIMONY / PRACTICAL REASONING / SIGN]
  Codes: [SM-codes or PASS]

C2: [subclaim]
  Support: [...]
  Support type: [...]
  Scheme hint: [...]
  Codes: [...]

C3: [subclaim]
  ...
```

**Field definitions:**

| Field | Source Step | Required | Notes |
|-------|-----------|----------|-------|
| Support | Step 3 | Yes, per subclaim | What the text actually offers as evidence |
| Support type | Step 3 | Yes | One of 5 types |
| Scheme hint | Step 3 | When diagnostically useful | One of 8 schemes; not required for every support unit |

**Downstream consumers:** The evidence module deepens the provenance analysis per support node. The red-team module identifies which support units are most attackable. The persuasion module assesses which evidence type to foreground for the audience.

---

### § 4. Warrant and Inference Map

Populated by: Dialectical Clarity Step 4.

```markdown
## 4. Warrant and Inference Map

C1: [subclaim]
  Warrant: [the principle connecting evidence to claim]
  Warrant status: [EXPLICIT / RECOVERABLE / MISSING / CONTESTED]
  Backing: [PRESENT / THIN / ABSENT]
  Qualifier: [MATCHED / OVERCONFIDENT / UNDERCLAIMED]
  Codes: [WR-codes or PASS]

C2: [subclaim]
  ...
```

**Field definitions:**

| Field | Source Step | Required | Notes |
|-------|-----------|----------|-------|
| Warrant | Step 4 | Yes, per subclaim | The connecting principle; stated or reconstructed |
| Warrant status | Step 4 | Yes | Calibrates against audience from § 1 |
| Backing | Step 4 | Yes | Whether the warrant itself is supported |
| Qualifier | Step 4 | Yes | Whether the conclusion's confidence matches the support chain |

**Downstream consumers:** The red-team module attacks the weakest warrants. The persuasion module identifies which warrants need to be made explicit for the target audience. The revision coach sequences warrant repair before support repair (fixing the bridge before adding more evidence).

---

### § 5. Burden, Scope, and Comparative Assessment

Populated by: Dialectical Clarity Step 5.

```markdown
## 5. Burden, Scope, and Comparative Assessment

Claim scope: [UNIVERSAL / PROBABILISTIC / LOCAL / NORMATIVE / DEFINITIONAL]
Evidence scope: [UNIVERSAL / PROBABILISTIC / LOCAL / NORMATIVE / DEFINITIONAL]
Match: [Y/N]
  If N: [describe the gap]

Comparative burden:
  Alternatives considered: [Y/N — list if Y]
  Precision justified: [Y/N]
  Testimony overextended: [Y/N]

Codes: [BP-codes or PASS]
```

**Field definitions:**

| Field | Source Step | Required | Notes |
|-------|-----------|----------|-------|
| Claim scope | Step 5 | Yes | One of 5 scope types |
| Evidence scope | Step 5 | Yes | What the evidence actually supports |
| Alternatives | Step 5 | For AT3 | List of alternatives mentioned or conspicuously absent |
| Precision justified | Step 5 | For data-heavy work | Whether quantitative claims match methodological precision |
| Testimony overextended | Step 5 | For AT4 / testimony | Whether personal evidence carries system-level claims |

---

### § 6. Objection and Dialectical Integrity Map

Populated by: Dialectical Clarity Step 6.

```markdown
## 6. Objection and Dialectical Integrity Map

Objection 1: [what the strongest objection would be]
  Engaged: [Y/N]
  Quality: [SUBSTANTIVE / STRAWMAN / EVASION / COSMETIC]
  Dialectical integrity: [FAIR / code]
  Codes: [OB-codes, DI-codes, or PASS]

Objection 2: [...]
  ...

Objection 3: [...]
  ...
```

**Field definitions:**

| Field | Source Step | Required | Notes |
|-------|-----------|----------|-------|
| Objection | Step 6 | 2–4 required | The strongest objections a careful skeptic would raise |
| Quality | Step 6 | Yes, if engaged | Four-level classification |
| Dialectical integrity | Step 6 | Yes | DI0–DI4 or FAIR |

**Downstream consumers:** The red-team module expands this section substantially: it generates the full objection set, produces cross-examination questions, and writes the opposition memo. The persuasion module identifies where concessions should be placed and what costly concession looks like for this argument.

---

### § 7. Narrative-as-Evidence Inventory

Populated by: Dialectical Clarity Step 7.

```markdown
## 7. Narrative-as-Evidence Inventory

V1: [description — location in draft]
  Attached to: [subclaim]
  Function: [ILLUSTRATION / EVIDENCE / EMOTIONAL ANCHOR / UNATTACHED]
  Witness position: [OBSERVATIONAL / PARTICIPANT / INTERPRETIVE /
                     REPRESENTATIVE / INSTITUTIONAL]
  Codes: [NE-codes or PASS]

V2: [...]
  ...
```

**Field definitions:**

| Field | Source Step | Required | Notes |
|-------|-----------|----------|-------|
| Vignette | Step 7 | All narrative segments | Description + location |
| Function | Step 7 | Yes | Four-level classification |
| Witness position | Step 7 | When testimony involved | Five-level classification; drives BP6 cross-check |

---

### § 8. Cross-Section Tracking

Populated by: Dialectical Clarity Step 8.

```markdown
## 8. Cross-Section Tracking

| Section | Claim as Stated | Qualification Level | Key Term Definitions | Drift from C0 |
|---------|----------------|--------------------|--------------------|---------------|
| Opening | [...] | [hedged/moderate/confident] | [T1=X, T2=Y] | [none / note] |
| Body §1 | [...] | [...] | [...] | [...] |
| Body §2 | [...] | [...] | [...] | [...] |
| Conclusion | [...] | [...] | [...] | [...] |

Dynamic failures detected: [codes with locations, or NONE]
```

**Field definitions:**

| Field | Source Step | Required | Notes |
|-------|-----------|----------|-------|
| Section rows | Step 8 | All major sections | Minimum: opening, 2 body sections, conclusion |
| Qualification level | Step 8 | Yes | Three-level scale; tracks erosion |
| Key term definitions | Step 8 | When tracked in § 2 | Per-section meaning; tracks smuggling |
| Dynamic failures | Step 8 | Yes | Codes with locations, or explicit NONE |

---

### § 9. Diagnostic Summary

Populated by: Dialectical Clarity after all steps complete.

```markdown
## 9. Diagnostic Summary

### Pattern matches
[FM-A codes with names — e.g., FM-A6: The Warrant Leap]

### Failure cluster
[Architectural / Relational / Quality / Dynamic — primary cluster]

### Severity ranking
| Code | Pattern | Severity | Blast Radius | Location |
|------|---------|----------|-------------|----------|
| [...] | [...] | [Must-Fix / Should-Fix / Could-Fix] | [Local / Multi-section / Systemic] | [...] |

### Hard gate violations
[List any Must-Fix hard gates triggered, or NONE]

### Priority diagnosis
Structural break: [...]
Why it matters: [...]
First repair target: [diagnostic only; no rewrite]
```

**This section is the bridge between diagnosis and downstream modules.** The red-team module reads the severity ranking to identify the most attackable points. The persuasion module reads the pattern matches to identify what audience-facing adjustments would address the structural weaknesses. The revision coach reads the priority diagnosis and hard gate violations to sequence repair.

---

### § 10. Companion Module Annotations

Populated by: Companion modules, when they run. Empty if only the core audit runs.

```markdown
## 10. Companion Module Annotations

### 10.1 Evidence Analysis
[Populated by argument-evidence module when it runs]
_Status: not yet run_

### 10.2 Persuasion Assessment
[Populated by argument-persuasion module when it runs]
_Status: not yet run_

### 10.3 Verification and Research Handoff
[Populated by evidence mode or research handoff when needed]
_Status: not yet run_

### 10.4 Red-Team Pressure
[Populated by argument-red-team module when it runs]
_Status: not yet run_

### 10.5 Revision Plan
[Populated by revision coach argument mode when it runs]
_Status: not yet run_

### 10.6 Citation Verification
[Populated by citation-verifier research mode when it runs]
_Status: not yet run_

### 10.7 Field Reconnaissance
[Populated by field-recon research mode when it runs]
_Status: not yet run_

### 10.8 Adversarial Evidence Review
[Populated by adversarial-evidence-review module when it runs]
_Status: not yet run_
```

**Annotation protocol:** Each companion module writes into its designated subsection. Annotations are signed with the module name and timestamp. Annotations may reference any field in §§ 1–9 by section and field name. Annotations may not modify §§ 1–9 directly; they add interpretive layers, not corrections. If a companion module disagrees with a diagnostic finding, it notes the disagreement in its annotation block.

**Subsection responsibilities:**

```markdown
### 10.1 Evidence Analysis
- Source provenance ledger
- Primary/secondary distinction per support node
- Confidence and precision notes
- Verification recommendations

### 10.2 Persuasion Assessment
- Audience-specific framing options
- Concession placement recommendations
- Sequencing and compression guidance
- Foreground/background recommendations per subclaim

### 10.3 Verification and Research Handoff
- Claim-specific verification queue
- Research mode referrals
- Time-sensitive factual check notes
- Publication-risk checkpoints

### 10.4 Red-Team Pressure
- Strongest objection set (expanded from § 6)
- Opposition memo
- Cross-examination questions
- Burden-of-proof attacks
- Definitional attacks
- Vulnerability ranking

### 10.5 Revision Plan
- Claim-first repair sequence
- Warrant repair plan
- Evidence acquisition queue
- Definition stabilization targets
- Objection-handling pass plan
- Audience recalibration plan

### 10.6 Citation Verification
- Citation resolution results and confidence levels
- Fit verdicts per citation (supported / partial / misrepresented / etc.)
- Named flags (CV1-CV12) with severity and location
- Repair queue ordered by argumentative centrality
- Full results reference: Citation_Ledger.md

### 10.7 Field Reconnaissance
- Counterevidence summary with action recommendations
- Literature gap findings (temporal, methodological, perspectival, concentration)
- Source ecosystem health (dead links, retractions, preprints)
- Full results reference: Field_Reconnaissance_Report.md

### 10.8 Adversarial Evidence Review
- Evidence survivability verdicts per claim-evidence pairing (survives / weakened / does not survive)
- Localized attack findings from three protocols (HX: ACH, LX: cross-exam, SX: severe testing)
- Severity tiers (Provisional / Elevated) with convergence criteria
- Disposition assignments (ADDRESS / ACKNOWLEDGE / ACCEPT)
- Domain-standard attack translations (GRADE, RoB 2, ROBINS-I, FRE 702, conceptual severity)
- Hard gate triggers
- Full results reference: Adversarial_Evidence_Preparation_Guide.md
```

---

## Artifact Lifecycle

### Creation

The Dialectical Clarity audit creates `Argument_State.md` at the start of its run. Sections 1–8 are populated as each step completes. Section 9 is populated after all steps finish. Section 10 is initialized with empty subsections 10.1 through 10.8.

### Persistence

The file lives in the project directory alongside:
- the editorial letter
- any tracking artifacts generated during the audit
- the manuscript file(s)

Naming convention: `Argument_State.md` (no version suffix for the current state).

### Versioning

If the audit runs again on a revised draft, the current state is archived as `Argument_State_v[N].md` and a fresh state is created. This allows comparison between diagnostic runs.

### Multi-module runs

When companion modules run after the core audit:
1. They read the existing `Argument_State.md`
2. They populate their annotation subsection in § 10
3. They do not modify §§ 1–9
4. Each annotation is timestamped

When the revision coach runs:
1. It reads the full state including all annotations
2. It produces a session plan referencing specific sections and fields
3. It notes which diagnostic findings and companion annotations drive each repair recommendation

---

## Relationship to Existing APODICTIC Artifacts

### Versus the editorial letter

The editorial letter is a *deliverable* written for the writer. It uses natural language, includes coaching, and reads as a document. The Argument_State.md is *infrastructure* written for the engine. It uses structured fields, codes, and references. They coexist; they serve different audiences.

### Versus tracking artifacts (A–E in the v2.0 audit)

The five tracking artifacts defined in the Dialectical Clarity v2.0 spec (Argument Architecture Table, Audience Calibration Matrix, Failure Mode Inventory, Cross-Section Tracking, Distinguish Classification) are *subsets* of the Argument State. They can be generated from the state; they do not replace it. The tracking artifacts are formatted for inclusion in the editorial letter. The state is formatted for module consumption.

### Versus the diagnostic-state.md (fiction DE)

The fiction development edit uses a diagnostic state file to track pass results across the 12-pass pipeline. The Argument_State.md is the nonfiction analogue: it tracks the 9-step diagnostic and its downstream modules. The two state files have different schemas because fiction and nonfiction arguments have fundamentally different structural objects (scenes vs. claims, arcs vs. support chains, beats vs. warrants).

---

## Integration Points

### Intake router

When the intake router classifies material as nonfiction / argument-shaped (Franklin Classification 3 or 4, or direct identification), it should:
1. Create the project directory if it doesn't exist
2. Note that the Dialectical Clarity audit will populate `Argument_State.md`
3. After the audit completes, offer companion modules based on form and need

### Dialectical Clarity audit

The audit is the primary producer. It populates §§ 1–9 during its run. It should:
1. Create `Argument_State.md` at the start of Step 1
2. Populate each section as the corresponding step completes
3. Backfill the Distinguish classification in § 1 after Step 9
4. Populate § 9 (Diagnostic Summary) after all steps
5. Initialize § 10 with empty subsections

### Companion modules

Each companion module is a consumer-and-annotator. It should:
1. Read the full state
2. Validate that §§ 1–9 are populated (refuse to run on an empty state)
3. Populate its designated subsection in § 10
4. Reference specific state fields by section number and field name
5. Timestamp its annotations

### Revision coach

The revision coach is a pure consumer. It should:
1. Read the full state including all annotations
2. Produce a session plan or repair queue
3. Sequence repairs by dependency (claim architecture before warrant repair; warrant repair before evidence acquisition)
4. Reference specific state fields in each recommendation

---

## Schema Versioning

This schema is versioned independently of the audit spec. Schema version changes when:
- A section is added, removed, or restructured
- A required field is added or removed
- The annotation protocol changes

Schema version does not change when:
- The audit adds or removes failure codes (the state references codes; it doesn't define them)
- Companion modules are added (they get new subsections in § 10)
- Field descriptions are clarified without changing the field's meaning

Current schema version: **0.1.1**
Depends on: Dialectical Clarity v2.0

---

*This schema defines the shared representation of an argument across the Nonfiction Argument Engine. The Dialectical Clarity audit populates it; companion modules annotate it; the revision coach consumes it. It is infrastructure, not a deliverable. The writer never sees it unless they want to. The engine cannot function as a composable system without it.*
