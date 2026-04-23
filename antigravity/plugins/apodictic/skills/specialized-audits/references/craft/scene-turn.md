# Specialized Audit: Scene Turn Diagnostics
## Version 1.1
*Last Updated: February 2026*

---

## Purpose

Diagnose whether individual scenes turn properly and whether scene-to-scene causality is maintained. Provide specific flags for scenes that lack goals, conflict, outcomes, or causal connections to adjacent scenes.

**Core claim:** A story can have a sound spine and psychologically coherent characters and still feel flat scene-by-scene. When a scene doesn't turn—when the situation at the end is the same as at the beginning—the reader's experience is "nothing happened," even if technically something did.

**Deficit-First Diagnostic Rule:** Your job is not to validate the presence of attractive prose, atmospheric detail, or conversational wit. You must hunt for the *absence* of scene turning mechanisms: missing goals, unaligned conflict, missing outcomes, and dead sequels. If a scene contains beautiful language but no consequence, it fails the turn diagnostic.

**What this audit is:** A scene-level mechanics diagnostic. It tests whether each scene has the internal engine (goal → conflict → outcome) and whether the processing between scenes (reaction → dilemma → decision) maintains causal momentum.

**What this audit is not:** A substitute for Plot Architecture (spine mechanics), Emotional Craft (emotional transmission), or Character Architecture (psychology/agency). Plot Architecture diagnoses whether the story's overall structure works. Emotional Craft diagnoses whether emotion transmits. Character Architecture diagnoses whether characters are psychologically coherent and appropriately agentic. This audit diagnoses whether individual scenes execute their structural function—whether each scene is a machine that produces change.

**Named for:** Jack M. Bickham's *Scene & Structure*, adapted as a scene-level diagnostic tool.

**When to activate:**
- Pass 1 flags "nothing happens" or reader disengagement at scene level
- Pass 2 identifies scenes but can't determine their function
- Pass 3 shows pacing problems in specific scene clusters
- Plot Architecture shows viable spine but scenes don't execute it
- Author reports "my scenes feel flat" or "I don't know what my characters want scene-by-scene"

---

## Vocabulary

### Scene (Action Unit)

A dramatic unit built on: **Goal → Conflict → Outcome.**

- **Goal:** What the POV character wants to achieve or learn in this specific scene. Must be concrete enough to succeed or fail at.
- **Conflict:** Active opposition to the goal. Not just difficulty—someone or something is working against the character's objective.
- **Outcome:** How the scene ends relative to the goal. The situation must change.

A scene is defined by its internal engine, not by setting or length. A chapter may contain multiple scenes. A scene may span chapters.

### Sequel (Processing Unit)

The bridge between scenes: **Reaction → Dilemma → Decision.**

- **Reaction:** Emotional and physical response to the previous scene's outcome. The character processes what happened.
- **Dilemma:** The choice forced by the new situation. What are the options, and what does each cost?
- **Decision:** The choice that sets up the next scene's goal.

Sequels can be a paragraph or a chapter. They can be implicit. But they must exist in some form, or the reader loses track of why the character does what they do next.

### Scene Turn

The change in situation between the beginning and end of a scene. If the situation hasn't changed, the scene hasn't turned.

### Outcome Types

How a scene resolves relative to the goal. Each outcome type is tagged for tracking across the audit:

| Code | Type | What Happens | Effect on Momentum |
|------|------|-------------|-------------------|
| **O1** | Success | Character achieves goal | Tension drops — weakest outcome for pacing |
| **O2** | Failure | Character fails, goal blocked | Dead end unless new information emerges |
| **O3** | Partial success / compromise | Goal partly achieved, partly blocked | Moderate momentum |
| **O4** | Success-with-cost | Goal achieved but situation worsens | Strong — complication maintains tension |
| **O5** | Reversal | Expected outcome flips | Strong — forces re-evaluation |
| **O6** | Revelation | New information changes stakes or plan | Strong — but overuse becomes informational |
| **O7** | Decision outcome | Unit ends with binding decision | Often hybrid scene/sequel |

**Diagnostic bias:** O4, O5, and O6 produce the strongest forward momentum — they tighten the knot. Unqualified O1 (success) risks dropping tension. Unqualified O2 (failure) risks dead-ending unless paired with new information. The key question is not "does the scene turn?" but "does the outcome create a new problem or sharper constraint?"

### Disaster Pressure

The concept behind the outcome taxonomy: a scene's ending should ideally increase urgency, risk, cost, or uncertainty. The outcome tightens the knot — it doesn't just change the situation, it makes the situation harder. This is what distinguishes narrative propulsion from mere event sequence.

### Scene Chain

The causal sequence: Scene outcome → Sequel processing → New goal → Next scene. When the chain is intact, each scene arises from the previous scene's consequences. When the chain breaks, scenes feel episodic — "and then" rather than "therefore."

---

## Relationship to Existing Passes

This audit does not duplicate existing infrastructure. It operates at a different resolution:

**Plot Architecture identifies spine; this audit tests execution at scene level.** Plot Architecture answers "does the story have a viable structural design?" This audit answers "does each scene do its job within that design?"

**Pass 2 (Structural Mapping) identifies scenes; this audit tests their internal mechanics.** Pass 2 documents scene boundaries, beat identification, and proportional analysis. This audit asks whether each identified scene turns — whether it has a goal, conflict, and outcome that produce change.

**Pass 3 (Pacing/Rhythm) measures pace; this audit explains why pace fails.** Pass 3 flags pacing problems. This audit diagnoses the mechanism: scenes without goals feel slow; scenes without outcomes feel purposeless; missing sequels make transitions feel abrupt.

**Franklin Pathway works at spine level; this audit works at scene level.** Franklin's function chain (complication → development turns → resolution) operates at the macro level. This audit tests whether individual scenes within each function chain slot actually execute their assigned structural work.

**Emotional Craft Diagnostics tests emotional transmission; this audit tests structural causality.** A scene can turn properly (goal met, situation changed) but transmit no emotion (S1: reportage, B1: no interpretation). Conversely, a scene can have rich emotional texture but fail to turn (no goal, no change). The two audits diagnose different dimensions of the same scene.

---

## Scope Selection

### Default Scope: 6–8 Scenes

Sample strategically:

| Scene Type | How Many | Why |
|-----------|----------|-----|
| Opening scene | 1 | Tests whether the narrative establishes forward drive |
| A scene that "feels slow" (Pass 1/3 flagged) | 1–2 | These are the diagnostic targets |
| A scene that works well | 1 | Calibrates what "working" looks like in this manuscript |
| A midpoint scene | 1 | Tests whether momentum carries through the middle |
| A climactic scene | 1 | Tests whether the biggest scene turns properly |
| A bridge/transition scene | 1–2 | Tests sequel mechanics between major scenes |

### When to Expand Scope

- If sample scenes show pervasive missing goals → expand to 12–15 scenes; likely manuscript-wide
- If sample shows inconsistent problems → targeted fixes may suffice
- If this audit is running alongside Franklin Pathway → focus on scenes within the candidate spine's function chain slots

### When NOT to Run This Audit

- Material has no scenes yet (notes, premise) → use Franklin Pathway
- The spine is absent or broken → fix spine first (Plot Architecture or Franklin); scene-level diagnosis on a structurally unmoored manuscript is premature
- Pacing problems stem from proportion, not scene mechanics → Pass 3 is sufficient

---

## Trigger Conditions

Activate when ≥2 of the following appear:

1. Pass 1 (Reader Experience) flags "nothing happens" or reader disengagement at scene level
2. Pass 2 (Structural Mapping) identifies scenes but can't determine their function
3. Pass 3 (Pacing/Rhythm) shows flat momentum in the middle third
4. Plot Architecture shows a viable spine but Pass 1 flags scene-level flatness
5. Author reports "my scenes feel purposeless" or "I don't know how to make scenes work"

---

## The Diagnostic Procedure

### Code Namespace Note

This audit uses G-codes (goal), C-codes (conflict), O-codes (outcome), Sq-codes (sequel), H-codes (handoff), U-codes (unit type), and P-codes (pattern). The **Sq** prefix distinguishes sequel codes from the Emotional Craft audit's **S**-codes (S1–S10, Microtension Slack). Both code systems may appear in the same editorial letter.

### Step 1: Unit Classification

For each selected unit, classify:

```
Unit [X]: [Title/location]
  Type: SCENE / SEQUEL / HYBRID / NON-UNIT
  POV: [character]
  Confidence + reason: [brief justification]
```

- **Scene:** Contains active pursuit of a concrete objective with obstruction and outcome.
- **Sequel:** Processes prior outcome and ends in a binding decision.
- **Hybrid:** Contains both but one is incomplete.
- **Non-unit:** Exposition, montage, vignette — doesn't function as scene or sequel.

**Unit classification codes (when classification fails):**

| Code | Name | Description |
|------|------|-------------|
| **U0** | Non-unit | Exposition or montage; no attempt, no processing, no decision |
| **U1** | Montage/listing | Time-skips and summaries; may need different handling |
| **U2** | POV drift | Multiple focal characters; can't assign goal/reaction cleanly |

**Non-unit routing:** Flag as form and route to voice/meaning diagnostics rather than forcing goal-conflict-outcome. Vignettes and interludes may be intentional craft — classify, don't condemn.

### Step 2: Scene Goal Audit

For each scene unit, extract the goal and code any failures:

```
Unit [X]: Goal Audit
  Goal: [what POV character wants to achieve/learn]
  Specificity: CONCRETE / VAGUE / ABSENT
  Stated or implied: STATED / IMPLIED / NEITHER
  Code: [G-code or PASS]
```

**Goal failure codes:**

| Code | Name | Description |
|------|------|-------------|
| **G0** | Missing goal | Action happens but no objective emerges; character is present without purpose |
| **G1** | Vague goal | "Figure things out," "try," "cope," "be okay" — can't fail concretely |
| **G2** | Diffuse goal | Multiple competing objectives with none dominant |
| **G3** | Proxy goal | Objective belongs to another character; protagonist is passenger |
| **G4** | Post-hoc goal | Goal only becomes legible after the unit ends; reader can't track in real time |

**False positive notes:**
- Mystery/investigation scenes often use "find out" goals — acceptable if the unit contains a specific question and a concrete investigative action (not just pondering).
- Literary scenes can have subtle goals (to avoid, to conceal, to test, to belong). If truly absent, that's likely intentional vignette form — classify as U0, don't force scene mechanics.

### Step 3: Conflict Collision Audit

For each scene unit, assess whether conflict *collides with the goal* — not just whether tension exists:

```
Unit [X]: Conflict Audit
  Opposition: [what or who opposes the goal]
  Collision: [does opposition directly obstruct the goal?]
  Code: [C-code or PASS]
```

**Conflict failure codes:**

| Code | Name | Description |
|------|------|-------------|
| **C0** | No conflict | Goal proceeds unopposed |
| **C1** | Soft conflict | Obstacle is mild, easily solved, or doesn't force adaptation |
| **C2** | Misaligned conflict | Conflict exists but doesn't obstruct the goal — adjacent drama, not collision |
| **C3** | Delayed conflict | Blocking force appears too late; unit reads as setup, not scene |
| **C4** | Internal-only without consequence | Rumination without external constraint and no decision; should be sequel |

**The collision heuristic:** If you can delete the "conflict" paragraph and the goal still succeeds or fails the same way, the conflict is misaligned (C2). This is the most common killer of scenes that look active but feel inert.

### Step 4: Outcome Audit

For each scene unit, identify the outcome type and code any failures:

```
Unit [X]: Outcome Audit
  Outcome type: [O1–O7]
  Situation change: [what's different at scene end vs. beginning]
  New constraint or problem: [what's harder now]
  Code: [O-code or PASS]
```

**Outcome type codes** (from Vocabulary): O1 Success, O2 Failure, O3 Partial, O4 Success-with-cost, O5 Reversal, O6 Revelation, O7 Decision.

**Outcome failure codes:**

| Code | Name | Description |
|------|------|-------------|
| **O8** | No outcome | No shift in constraints, knowledge, relationships, or plan; static |
| **O9** | Informational-only | Information delivered but doesn't change next action |
| **O10** | Soft closure | Pressure relieved without replacement; tension drops with nothing to take its place |
| **O11** | Uncaused outcome | Ending doesn't follow from the conflict chain; deus ex machina at scene level |

**The Turn Test:**
```
Can you state in one sentence how the situation changed
between the beginning and end of this unit?

IF yes → unit turns
IF no → O8
```

**Disaster Pressure Test (high-signal):** Does the outcome create a new problem or sharper constraint? If the ending increases urgency, risk, cost, or uncertainty, it's generating disaster pressure. If not, track: consecutive units without disaster pressure almost always produce momentum stalls.

### Step 5: Sequel Completion Audit

For each sequel unit (or the sequel portion of hybrid units), extract and code:

```
Unit [X]: Sequel Audit
  Reaction: [immediate felt response — Y/N]
  Dilemma: [at least two live options weighed — Y/N]
  Decision: [binding commitment that launches new goal — Y/N]
  Code: [Sq-code or PASS]
```

**Sequel failure codes:**

| Code | Name | Description |
|------|------|-------------|
| **Sq0** | No reaction | Jumps to analysis; emotional continuity breaks after prior scene's outcome |
| **Sq1** | No dilemma | Only one obvious path; choice feels preordained |
| **Sq2** | No decision | Sequel becomes drift, rumination, or exposition; no commitment |
| **Sq3** | Unbinding decision | A "decision" is stated but not acted on; no goal handoff to next unit |
| **Sq4** | Decision without cost | Choice is too easy; no constraint tradeoff, no sacrifice |

**The dead bridge diagnostic:** Most flat bridge scenes fail at Sq2. The character processes (reaction is present) but never commits to a next action. The sequel becomes meditation without momentum.

**Genre calibration for sequel length:**
- Literary fiction: Longer sequels expected; processing is where meaning lives
- Thriller/suspense: Compressed sequels; reaction → decision may be a paragraph
- Horror: Sequels produce dread; reaction may dominate
- Romance: Sequels carry emotional deepening; dilemma involves the relationship

### Step 6: Handoff Audit (Unit N → Unit N+1)

Compare end of unit N to start of unit N+1. Does the outcome/decision *cause* the next goal?

```
| Unit | Outcome/Decision | Next Goal | Handoff Code |
|------|-----------------|-----------|-------------|
| N    | [outcome]       | [next goal] | [H-code or PASS] |
```

**Handoff failure codes:**

| Code | Name | Description |
|------|------|-------------|
| **H0** | No handoff | Next unit feels unrelated; episodic jump |
| **H1** | Weak handoff | Causal link exists but isn't foregrounded; momentum leak |
| **H2** | Circular handoff | Next goal repeats previous goal with no escalation |
| **H3** | Offstage handoff | Key decision happens between units — the binding moment is missing |

**The "And Then" Test:** If the connection between Unit N and Unit N+1 can only be described as "and then" (not "therefore" or "but"), the handoff is broken. This is the scene-level version of Pass 0's causal chain assessment.

```
IF > 30% of transitions are H0 → FLAG: "Episodic Structure"
IF > 50% are H0 → STRUCTURAL FLAG: "No Scene-Level Causality"
```

### Step 7: Pattern Map (When Scope > 2 Units)

Across 5–10 consecutive units, summarize the aggregate picture:

**Compute:**
- Scene:Sequel ratio
- Outcome type distribution (how many O1 vs. O4/O5/O6)
- Frequency of Sq2 (sequel drift) and O8/O10 (pressure leak)

**Pattern flags:**

| Code | Name | Description |
|------|------|-------------|
| **P1** | Sequel swamp | Too many sequels or too many Sq2 failures; manuscript stagnates |
| **P2** | Scene pileup | Many scenes, few reflective decisions; turns feel unearned |
| **P3** | Pressure leak | Too many O1 outcomes without cost; tension drains |
| **P4** | Revelation crutch | Overuse of O6 outcomes; plot feels informational rather than dramatic |
| **P5** | Outcome monotony | Same outcome type repeatedly; turns lose force through repetition |

### Step 8: Revision Targets

Produce firewall-safe revision targets using the diagnostic codes.

#### Allowed Move Types

| Move | What It Does |
|------|-------------|
| **Establish goal** | Identify where the POV character's objective needs to be made clear or concrete (addresses G0–G4) |
| **Add opposition** | Identify where active resistance to the goal is missing (addresses C0–C1) |
| **Align conflict** | Identify where conflict exists but doesn't collide with the goal (addresses C2) |
| **Strengthen outcome** | Identify O1 outcomes that should add cost (→ O4) or O2 outcomes that should add revelation (→ O6) |
| **Add disaster pressure** | Identify outcomes that relieve tension without replacement (addresses O10) |
| **Complete sequel** | Identify sequel units missing reaction, dilemma, or decision (addresses Sq0–Sq2) |
| **Bind decision** | Identify sequels where decision is stated but not acted on (addresses Sq3) |
| **Connect chain** | Identify where the next unit's goal doesn't arise from the previous outcome (addresses H0–H1) |
| **Break circularity** | Identify where the same goal repeats without escalation (addresses H2) |
| **Convert to scene** | Identify summary passages that should be dramatized because they contain a structural turn |
| **Convert to summary** | Identify dramatized passages that should be summarized because they don't contain a turn |

**Output format:**
```
Target: [unit location]
  Codes: [G/C/O/Sq/H codes fired]
  Allowed move(s): [from the list above]
```

**Firewall compliance:** No invented scenes. No specific goals, conflicts, or outcomes suggested. The audit identifies where scene mechanics fail, codes the failure type, and specifies what structural function is missing. The writer provides the content.

---

## Common Patterns

Named diagnostic patterns this audit is designed to catch.

### Pattern 1: The Information Scene

**Signature:** G0 (missing goal) + C0 (no conflict) + O9 (informational-only outcome).

The scene exists to deliver information to the reader or to another character. It's structured around what needs to be communicated, not around what anyone wants. Often disguised as a conversation, meeting, or briefing.

**Diagnostic:** If you removed the information delivery and nothing else happened in the scene, the scene has no structural engine.

**Cross-reference:** Emotional Craft audit S8 (unarmed dialogue) often co-occurs.

### Pattern 2: The Observation Scene

**Signature:** G0 (missing goal) + U0 (non-unit) + O8 (no outcome).

The POV character watches events, describes settings, or reflects on the past. No objective is pursued; no opposition is met; nothing changes. Common in literary fiction (where it may be intentional) and in early drafts of everything else.

**Diagnostic:** If the character could be absent and nothing would change, the scene is an observation, not a scene.

**Cross-reference:** Emotional Craft audit S1 (reportage) and S9 (filterless POV) often co-occur.

### Pattern 3: The Sequel Without a Scene

**Signature:** Sq0/Sq2 in a unit where the triggering event happened offstage.

A character reacts, reflects, and decides — but the event they're processing was summarized or occurred between scenes. The emotional weight of the processing exceeds the dramatized weight of the trigger.

**Diagnostic:** If the sequel is longer than the scene it follows, the proportions may be inverted. The dramatic event should usually be dramatized.

### Pattern 4: The Momentum Killer

**Signature:** O1 (unqualified success) + O10 (soft closure) + no disaster pressure.

The character achieves their goal without complication. The scene ends on a positive note. Tension drops. The next scene has to rebuild momentum from zero.

**Diagnostic:** Count consecutive O1 outcomes. Two or more in a row almost always produces P3 (pressure leak).

### Pattern 5: The Episodic Middle

**Signature:** H0 (no handoff) across 3+ consecutive units + P5 (outcome monotony).

Scenes in the middle third don't arise from each other. The character moves from situation to situation without causal connection. Often occurs when the writer knows the beginning and ending but not the middle.

**Cross-reference:** Franklin Pathway Failure Mode D (Plateau in the Middle) and the Escalation Requirement. Episodic middles often co-occur with plateau risk.

### Pattern 6: The Misaligned Middle

**Signature:** C2 (misaligned conflict) across multiple units.

Tension exists in every scene but nothing is blocking the goal. Characters argue, worry, face difficulties — but the obstacles don't collide with what they're trying to achieve. The manuscript feels active but purposeless.

**Diagnostic:** The collision heuristic catches this: if you can delete the conflict and the outcome doesn't change, the conflict is decorative.

---

## Genre Calibration

### By Genre Module

**Romance / Erotic:** Scene goals in romance are often relational — the goal is to test, deepen, or protect the relationship. Conflict is often internal (desire vs. fear) combined with external obstacles. The sequel is where emotional deepening happens; don't flag long romance sequels as pacing problems. The Bid/Repair Rhythm from Character Architecture's Romance tuning pack maps directly to scene goals (bid = scene goal; repair/escalation = outcome).

**Thriller / Suspense:** Goals should be concrete and urgent. Outcomes should predominantly be "No, and furthermore" to maintain pace. Sequels should be compressed — long processing kills thriller momentum. Decision density (from the Thriller genre module) correlates with scene turn frequency.

**Literary Fiction:** Scene goals may be subtle — the goal might be understanding rather than action. Internal conflict may be the primary opposition. "Observation scenes" may be intentional craft, not missing structure. But even literary scenes should produce change — a shift in understanding, a revision of belief, a new recognition. If nothing shifts, it's not a scene even in literary fiction.

**Mystery / Investigation:** Scene goals are often informational — learn X, question Y, find Z. This is legitimate; investigation scenes have discovery goals. But the outcome should change the investigator's understanding or options, not just deliver facts. If every investigation scene ends in "Yes" (character learns what they wanted), the mystery lacks resistance.

**Horror:** Scene outcomes should increasingly be "No, and furthermore" — the situation should worsen. Sequels produce dread through extended reaction. The horror genre uniquely benefits from sequels where the dilemma has no good option.

**Science Fiction / Fantasy:** Long worldbuilding passages may masquerade as scenes but lack the goal-conflict-outcome engine. If a scene exists primarily to establish setting or rules, it's exposition, not a scene. The Context Smother Diagnostic from the Franklin Pathway is relevant here.

---

## Integration with Core Framework

### Module Position

This is a specialized audit that runs after or alongside relevant passes, producing its own output section. It stacks with genre modules and other specialized audits.

### Loading Trigger

Activate when ≥2 of the following appear:

1. Pass 1 flags "nothing happens" or reader disengagement at scene level
2. Pass 2 identifies scenes but can't determine their function
3. Pass 3 shows pacing problems in specific scene clusters
4. Plot Architecture shows viable spine but scenes don't execute it
5. Author reports scene-level problems

### Pass Modifications

**Pass 2 (Structural Mapping):** When documenting scene boundaries, note whether each scene has an identifiable goal. If more than 30% of scenes lack identifiable goals, flag as Scene Turn Diagnostics trigger.

**Pass 3 (Pacing/Rhythm):** When flagging pacing problems, distinguish between proportion problems (too much time on a structural function — stays in Pass 3) and scene mechanics problems (scenes don't turn — routes to this audit).

### Output Delivered

The full audit produces:

1. **Unit Classification** (Step 1: scene vs. sequel vs. hybrid vs. non-unit for each selected unit, with U-codes)
2. **Goal Audit** (Step 2: per scene unit — goal clarity, specificity, connection to spine, with G-codes)
3. **Conflict Collision Audit** (Step 3: per scene unit — opposition type, collision quality, with C-codes)
4. **Outcome Audit** (Step 4: per scene unit — outcome type O1–O7, situation change, disaster pressure, with O-codes)
5. **Sequel Diagnostics** (Step 5: per sequel/hybrid unit — reaction, dilemma, decision, with Sq-codes)
6. **Handoff Audit** (Step 6: causal connections between units — linked, weak, or broken, with H-codes)
7. **Pattern Map** (Step 7: aggregate picture across sampled units — scene:sequel ratio, outcome distribution, P-codes)
8. **Revision Targets** (Step 8: firewall-safe — location + codes fired + allowed move type)

All outputs anchored to specific units in the manuscript.

### Orchestration with Emotional Craft Diagnostics

When both this audit and the Emotional Craft Diagnostics audit are active on the same manuscript, run Scene Turn first. Scene Turn identifies which units have mechanical failures (G/C/O/Sq/H codes). Then run Emotional Craft on the same units to diagnose whether emotional transmission is also failing.

**The diagnostic logic:** A unit can fail mechanically but transmit emotionally (rich interior processing in a scene that doesn't turn), or turn properly but transmit nothing (goal-conflict-outcome present but S1 reportage). The two audits diagnose different dimensions of the same unit. Running Scene Turn first provides the structural map; Emotional Craft then diagnoses transmission within that map.

**In the editorial letter:** Combine findings per unit. A unit flagged with both G0 (missing goal) and S1 (reportage) needs different guidance than one flagged with G0 alone (the goal is absent but the writing is emotionally alive — structural fix only) or S1 alone (the mechanics work but the prose is flat — transmission fix only).

### Coaching in the Editorial Letter

The diagnostic procedure identifies *what* is broken at the scene level. When the editorial letter is written, it may include coaching guidance — explaining why goals matter, how "Yes, but" outcomes differ from "Yes" outcomes, or how sequel compression works in different genres. This coaching belongs in the deliverable, not in the diagnostic specification.

---

*This audit diagnoses scene-level mechanics — whether individual scenes turn and whether scene-to-scene causality is maintained. It identifies where goals are missing, where outcomes fail to change the situation, and where the causal chain between scenes breaks. The system diagnoses scene mechanics; the writer provides the scenes.*
