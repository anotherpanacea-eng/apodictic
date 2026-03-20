# Companion Module: Argument Persuasion (v1.0)
## Nonfiction Argument Engine / APODICTIC
*Drafted: March 19, 2026*
*Status: Companion coaching module for Dialectical Clarity v2.0*
*Consumes: `Argument_State.md`*

---

## Purpose

The Persuasion module helps a writer understand how the *existing* argument is likely to land with a specified audience and what structural recalibrations would improve uptake.

**Core question:** Given this argument, this form, and this audience, what sequencing, framing, concession, and compression choices would make the case land better without changing its substance behind the writer's back?

This module is downstream of structural diagnosis. It assumes Dialectical Clarity has already identified the claim, support, warrants, burden, and current audience calibration.

### What this module is not

It is not:

1. direct copy generation
2. manipulative messaging optimization
3. a substitute for the core audit
4. a red-team module

It advises on *how the existing case should be presented*, not what the author should believe.

---

## Activation

Run when:

1. the user asks how to make the case land better
2. the core audit fires `AC` codes or identifies strong audience mismatch
3. the writer is preparing a specific form: testimony, op-ed, policy brief, academic article, open letter, advocacy piece
4. the user wants audience-specific calibration without ghostwriting

Run after Red Team when possible. Hostile-read findings make persuasion advice sharper.

---

## Required Inputs

Read from `Argument_State.md`:

1. § 1 Context and Classification
2. § 2 Claim Architecture
3. § 4 Warrant and Inference Map
4. § 5 Burden, Scope, and Comparative Assessment
5. § 6 Objection and Dialectical Integrity Map
6. § 8 Cross-Section Tracking
7. § 9 Diagnostic Summary
8. § 10.4 Red-Team Pressure when available

This module should not re-derive the argument graph. It should interpret how that graph should be surfaced for the intended audience.

---

## Firewall Compliance

### Allowed

- identify audience mismatch
- advise on what to foreground, delay, compress, or expand
- diagnose concession timing and sequencing issues
- coach on trust-building structure
- produce an audience calibration memo

### Not allowed

- rewrite paragraphs
- generate substitute language to paste in
- coach around structural weakness by hiding it
- override severity findings from the core audit

### Governing rule

Every persuasion recommendation must preserve or improve audibility *without making the argument less examinable*.

---

## Outputs

This module produces:

1. `Audience_Calibration_Memo.md`
2. annotations to `Argument_State.md` § 10.2
3. a ranked list of persuasion priorities
4. optional form-specific sequence guidance

---

## Persuasion Framework

Evaluate the manuscript across six observable dimensions.

### 1. Audience Model (`AU`)

Is the manuscript clear about who it is actually addressing?

### 2. Trust and Credibility Architecture (`TR`)

Does the sequence earn confidence before asking for high-cost agreement?

### 3. Framing and Value Alignment (`FR`)

Are the issue frame, stakes frame, and value language suited to the reader being addressed?

### 4. Arrangement and Sequence (`AR`)

Does the argument arrive in an order that reduces rather than amplifies resistance?

### 5. Concession Economy (`CN`)

Are concessions real, timely, and credibility-building rather than decorative or self-sabotaging?

### 6. Compression and Form Fit (`CF`)

Is the material calibrated to the constraints of its form without losing essential burden logic?

---

## Named Persuasion Signals

These are coaching signals, not core diagnostic codes.

| Code | Name | Description |
|---|---|---|
| `PS1` | Audience Blur | The piece tries to address multiple incompatible audiences with one undifferentiated strategy |
| `PS2` | Shared-Knowledge Mismatch | Required background or warrant is left implicit for the actual audience |
| `PS3` | Trust Lag | The manuscript asks for high-cost agreement before establishing why it should be trusted |
| `PS4` | Wrong Evidence Foreground | The support most legible to the audience is buried while less persuasive material leads |
| `PS5` | Value-Frame Mismatch | The argument is framed around values unlikely to move this audience |
| `PS6` | Thesis Timing Error | The main claim lands too early or too late for the uptake conditions |
| `PS7` | Concession Misplacement | A concession is real but structurally misplaced |
| `PS8` | Recommendation Before Burden | The ask arrives before sufficient problem, criteria, or comparison setup |
| `PS9` | Compression Rupture | The piece has cut beyond what the form can bear while remaining persuasive |
| `PS10` | Register Dissonance | Tone or register undermines trust with the target audience |
| `PS11` | Friendly-Audience Drift | The piece assumes agreement and stops doing persuasive work |
| `PS12` | Hostile-Audience Self-Sabotage | The draft hands skeptical readers easy attack surfaces through sequence or framing choices |

---

## Diagnostic Procedure

### Step 1: Specify the actual audience

Using § 1, define:

1. primary audience
2. secondary audience if relevant
3. expertise level
4. receptivity posture
5. decision context

If the audience is unclear, say so explicitly. `Audience blur` is often the first real problem.

### Step 2: Identify the argument's uptake bottleneck

Ask:

1. what does this audience need in order to hear the claim at all?
2. what will they resist first?
3. which subclaim is the most strategic entry point?

### Step 3: Evaluate sequence

Assess:

1. where the claim appears
2. where stakes appear
3. where concessions appear
4. when recommendation or call to action appears
5. whether the strongest support is foregrounded appropriately

### Step 4: Evaluate trust architecture

Identify:

1. what builds trust in this form and forum
2. what currently weakens trust
3. whether overstatement or register mismatch is raising friction

### Step 5: Produce recalibration priorities

Rank 3-5 changes in terms of persuasive leverage, such as:

1. front-load definition before controversy
2. move concession earlier for hostile audience
3. foreground empirical support before moral framing
4. narrow claim before recommendation

These remain structural instructions, not line rewrites.

### Step 6: Classify each recommendation

Before writing the memo, classify every persuasion recommendation using the Distinguish Framework:

| Classification | Definition | Action |
|---|---|---|
| **Healthy Recalibration** | Improves uptake while preserving structural integrity and auditability | Include in memo as primary recommendation |
| **Optional Stylistic Adjustment** | May help uptake but is not structurally necessary | Include in memo, mark as optional |
| **Manipulative Drift** | Improves persuasion by making the argument less examinable | Suppress — flag the temptation but do not recommend the move |

**Decision tests** (all must pass for Healthy Recalibration):

1. Does the adjustment clarify rather than merely intensify?
2. Does it preserve the actual burden of proof?
3. Does it reduce predictable misunderstanding without hiding information?
4. Does it respect the form's compression limits?
5. Would the argument remain structurally auditable after the change?

If a recommendation fails any test, downgrade it. If it fails tests 2 or 5, classify as Manipulative Drift.

### Step 7: Annotate state and write memo

Write:

1. `Audience_Calibration_Memo.md`
2. `Argument_State.md` § 10.2

---

## Annotation Format for `Argument_State.md` § 10.2

```markdown
### 10.2 Persuasion Assessment
_Status: run by Argument Persuasion (v1.0) on [date/time]_

Audience model:
- Primary audience: [...]
- Secondary audience: [...]
- Highest-friction zone: [...]

Top persuasion priorities:
1. `PS3` Trust Lag — establish competence before recommendation
2. `PS7` Concession Misplacement — move concession earlier relative to C0
3. `PS4` Wrong Evidence Foreground — foreground support now buried in body §2

Structural recalibration notes:
- [...]
```

---

## Calibration by Audience Posture

| Audience posture | Foreground | Delay or compress | Watch for |
|---|---|---|---|
| General | orientation, stakes, plain definitions | method detail | `PS2`, `PS9` |
| Expert | contribution, provenance, qualifier discipline | basic framing | `PS3`, `PS10` |
| Hostile | narrow defensible claim, early credibility, costly concession | broad moralizing | `PS7`, `PS12` |
| Sympathetic | specificity, burden honesty, informative structure | coalition-flattery repetition | `PS11` |
| Mixed | layered support, clean sequence, dual-legibility language | dense shorthand | `PS1`, `PS4` |

---

## Calibration by Form

| Form | Structural persuasion burden | Signature risk |
|---|---|---|
| Op-ed | immediate orientation plus compressed support | `PS6`, `PS9` |
| Policy brief | recommendation must follow criteria and comparison | `PS8` |
| Testimony | witness credibility plus disciplined interpretation boundary | `PS3`, `PS12` |
| Academic article | trust through precision and contribution clarity | `PS10` |
| Open letter | visible audience choice and stakes ownership | `PS1`, `PS5` |
| Advocacy journalism | conviction without sequencing collapse | `PS4`, `PS11` |

---

## Integration with Other Modules

### Dialectical Clarity

The core audit diagnoses `AC` failures. This module translates those into audience-specific coaching.

### Argument Red Team

Run Red Team first when possible. The best persuasion advice often begins with: "Here is what the hostile reader will attack first."

### Argument Evidence

When persuasion depends on foregrounding stronger or more trustworthy support, hand off to Evidence mode rather than guessing about provenance.

### Revision Coach

The Persuasion memo should feed the coach's audience recalibration pass, not operate as a standalone static note.

---

## Hard Rules

1. Never recommend a persuasive move that hides a real burden problem.
2. Never recommend emotional intensification as a substitute for structure.
3. Never flatten a mixed audience into a single ideal reader without saying so.
4. Never coach beyond the evidence and claim structure already mapped.
5. If `PS12` fires (Hostile-Audience Self-Sabotage), verify whether the self-sabotage is structural (a DC problem requiring claim or warrant repair) or presentational (a genuine sequencing/framing issue). Only coach the presentational layer.
6. If the Persuasion module's recommendation conflicts with a DC severity finding, DC wins on substance. Persuasion may advise on *sequence and emphasis* but may not coach around a structural weakness the core audit identified.
7. Every recommendation in the `Audience_Calibration_Memo` must carry its Distinguish Framework classification. Unclassified recommendations are not allowed in the final output.

---

## Bottom Line

The Persuasion module gives APODICTIC a way to help nonfiction arguments land more effectively while staying on the advisory side of the firewall. It does not write the case. It shows the writer how their current case is likely to be heard and where structural recalibration would make the biggest difference.
