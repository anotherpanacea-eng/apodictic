# Tag Audit: Erotic Content
## Version 0.4.13
*Last Updated: February 2026*

---

## Purpose

This tag audit evaluates the craft of erotic and intimate content in any manuscript — not limited to romance. It diagnoses whether intimate scenes do narrative work (advance character, shift power, reveal psychology, create vulnerability) or merely fulfill genre expectation without consequence.

**The fundamental question:** Does the erotic content in this manuscript produce narrative change, or is it inert?

**This is a cross-genre tag.** It applies to any manuscript with significant intimate content regardless of parent genre: literary fiction with explicit scenes, thriller with sexual dynamics, horror with erotic elements, romance at any heat level above "sweet," erotica as primary genre, dark romance, and any work where intimacy is load-bearing.

**When to activate:**
- Any manuscript with explicit sexual content (heat level 3+)
- Any manuscript where intimate scenes are intended to advance character arc or theme
- Dark romance, erotic romance, high erotica, erotic horror
- Work featuring power exchange, kink, or BDSM dynamics
- Work where the meaning or function of sex is thematically significant
- Author or intake flags concern about whether intimate scenes "earn their place"
- Pass 1 reader experience notes intimate scenes as flat, repetitive, or disconnected

**This audit does not police content, kink, or heat level.** It evaluates whether intimate content is integrated into the narrative architecture or decorative.

---

## Contract Additions

When erotic content is present, add to contract schema:

```
HEAT LEVEL: [1-5 scale or descriptive: sweet/warm/steamy/explicit/erotic]
CONSENT FRAMEWORK: [fully consensual / dubcon elements / CNC / dark]
KINK/CONTENT TAGS: [if applicable]
```

These supplement the Romance genre module's contract fields (relationship structure, power dynamic, expected ending) when both are active. For non-romance manuscripts with erotic content, these stand alone.

---

## Intake Questions: Intimacy Architecture

Add these when erotic content is present:

1. **What is the heat level expectation?** Does the manuscript deliver it consistently?

2. **Is erotic/intimate content load-bearing or decorative?**
   - Load-bearing: Scenes advance character development, reveal psychology, shift power dynamics, create vulnerability
   - Decorative: Scenes provide expected genre satisfaction without advancing narrative

3. **What is the emotional price of physical intimacy in this world?** What do characters risk by being vulnerable?

4. **What does sex/intimacy MEAN in this story?** (Connection, power, escape, self-discovery, surrender, claiming, healing, destruction, horror, conditioning, liberation)

---

## Core Diagnostic Dimensions

### Dimension 1: Scene Function (Load-Bearing Test)

For each intimate scene, assess:

**The Removal Test:** If this scene were removed, what narrative information would be lost?
- Character revelation lost → Load-bearing
- Power dynamic shift lost → Load-bearing
- Relationship state change lost → Load-bearing
- Nothing lost except explicit content → Decorative

**The Substitution Test:** If the explicit content were replaced with a fade-to-black, would the reader miss necessary information?
- Yes → Content is doing narrative work
- No → Content may be decorative (which is acceptable in erotica but should be flagged in literary/thriller/horror where every scene must earn its place)

### Dimension 2: Psychological Presence

Does the POV character maintain internal experience during intimate scenes?

**Track:**
- Sensation (physical experience rendered from inside)
- Thought (psychological processing continues during the scene)
- Emotion (felt states, not just described states)
- Observation-in-character (noticing the other person through this character's specific lens)

**Detect:**
- **Camera mode:** POV character becomes a lens describing the other person's body without their own experience
- **Choreography report:** Actions described mechanically without psychology
- **Vanishing interiority:** Character's inner life disappears during intimacy and returns after

**Cross-reference:** Interiority Preservation audit (craft/) for the cross-genre version of this diagnostic.

### Dimension 3: Escalation Architecture

Across the manuscript's full run of intimate scenes, does each scene do something the previous one didn't?

**Escalation doesn't require higher intensity.** Escalation can mean:
- Deeper vulnerability (not just more explicit)
- Higher emotional stakes
- Role reversal or power shift
- New location or context that changes meaning
- Integration of intimate dynamic into non-intimate life
- Testing limits that reveal character

**Stagnation = repetition without progression.**

### Dimension 4: Consequence Persistence

Do intimate encounters produce effects that persist outside the scene?

**Track:**
- Does the relationship state change after the scene?
- Do characters reference or process the encounter later?
- Does the power dynamic shift carry into non-intimate scenes?
- Is there psychological aftermath (positive or negative)?
- Does the scene create vulnerability that later becomes plot-relevant?

### Dimension 5: Consent Architecture

For every intimate scene, log the Consent Calculus:

| Scene | Stated Desire | Enacted Boundary | Aftermath State | Classification |
|-------|---------------|------------------|-----------------|----------------|

**Definitions:**
- **Stated Desire:** What did they explicitly say they wanted (or didn't want)?
- **Enacted Boundary:** What actually happened?
- **Aftermath State:** How do they feel about it afterward? (Positive / Negative / Ambivalent)

**Logic Gates:**

```
IF Enacted > Stated AND Aftermath = Positive
THEN Classification = "CNC / Awakening / Pushed Boundary (consensual)"

IF Enacted > Stated AND Aftermath = Negative
THEN Classification = "Violation / Trauma"

IF Enacted > Stated AND Aftermath = Ambivalent
THEN Classification = "Requires Processing" (flag for follow-up scene)

IF Enacted = Stated AND Aftermath = Positive
THEN Classification = "Negotiated Consent"

IF Enacted < Stated AND Aftermath = Negative
THEN Classification = "Unfulfilled / Frustration"
```

**Contract Check:**
- If Contract = "Sweet Romance" and any scene logs "Violation" → HARD FLAG
- If Contract = "Dark Romance" and scenes log "Violation" → Check: Is this the *point*? Is aftermath addressed?
- If Contract = "CNC" and scenes log "CNC/Awakening" → Expected; verify aftermath processing exists

**The Calculus prevents:**
- Flagging consensual kink as abuse
- Missing actual violations dressed as romance
- Ignoring aftermath when boundaries are tested

**For deeper consent analysis** (dubcon, conditioning, erotic horror, power-dynamic narratives), activate the **Consent Complexity audit**.

---

## Named Diagnostic Flags

### Erotic Craft Flags

**EC-1: Decorative Kink**
- *Detection:* A kink is introduced (bondage, praise kink, etc.) but reveals nothing about character psychology or power dynamic
- *Test:* Remove the kink element — does anything about the scene change?
- *Severity:* Could-Fix (isolated) / Should-Fix (pattern)

**EC-2: Mechanical Intimacy**
- *Detection:* Sex scene describes actions without psychology — a choreography report
- *Test:* Does the scene contain any sentence about what the experience *means* to the POV character?
- *Severity:* Should-Fix (pattern breaks immersion)

**EC-3: Skipped Aftermath**
- *Detection:* Intimate moment with no processing, consequence, or emotional residue in subsequent scenes
- *Test:* Does any later scene reference, process, or build on what happened?
- *Severity:* Could-Fix (single instance) / Should-Fix (pattern)

**EC-4: Static Heat**
- *Detection:* Every intimate scene at same intensity level — no escalation, variation, or modulation
- *Test:* Can intimate scenes be reordered without loss of narrative logic?
- *Severity:* Should-Fix (reader disengagement)

**EC-5: Intimacy as Pause**
- *Detection:* Sex scene stops the plot rather than advancing it — narrative pauses for the scene and resumes after
- *Test:* Does the story's situation change between the scene's beginning and end?
- *Severity:* Could-Fix (genre expectation may justify) / Should-Fix (in literary, thriller, horror)

**EC-6: Pattern Repetition**
- *Detection:* Multiple scenes using identical escalation mechanics (repeated denial cycles, same trigger sequence) without variation
- *Test:* Would a reader notice they've read this pattern before?
- *Severity:* Should-Fix

**EC-7: Technique Saturation**
- *Detection:* The same psychological/physical technique demonstrated more times than necessary for reader understanding
- *Test:* Does the Nth instance reveal something the (N-1)th didn't?
- *Severity:* Could-Fix (if characterization anchored) / Should-Fix (if repetitive)

**EC-8: Vanishing Interiority**
- *Detection:* POV character's inner life disappears during intimate scenes — becomes camera or action-delivery mechanism
- *Test:* Count sentences of internal experience vs. external description during scene
- *Severity:* Should-Fix (pattern) / Must-Fix (if it contradicts the manuscript's interiority standards elsewhere)

---

## Escalation vs. Repetition Audit

**For manuscripts with multiple intimate scenes, perform this audit:**

### Step 1: Catalog Scene Mechanics

For each intimate scene, document:
- Primary physical activity
- Primary psychological dynamic (power exchange, vulnerability, discovery, etc.)
- Escalation technique used (denial, edging, fractionation, command/obedience, etc.)
- New element introduced (if any)
- Character development accomplished

### Step 2: Build Escalation Map

| Scene | Mechanic | New Element? | Character Growth | Escalation from Previous |
|-------|----------|--------------|------------------|-------------------------|

### Step 3: Detect Repetition Patterns

Flag for review:
- **Same mechanic, same outcome:** Two or more scenes using identical technique without variation
- **Denial cycle redundancy:** More than 3 build/denial cycles within a single scene, or same cycle count across scenes
- **Missing escalation:** Scene that introduces nothing new (no new vulnerability, no new power shift, no new physical/emotional territory)
- **Technique demonstration vs. narrative use:** Scenes that re-explain a mechanism already understood by reader

**Repetition is not always a problem.** Ritual and pattern can create reader anticipation and character anchoring. Flag only when:
- Reader experience pass logs boredom or "skimming" sensation
- The repetition doesn't serve characterization or thematic purposes
- The pattern occupies disproportionate word count

**Output:** Escalation map, flagged redundant scenes, recommended consolidation targets

---

## Subgenre Calibration

| Mode | Integration Promise | Named Failure Mode | Tighten On | Loosen On |
|------|--------------------|--------------------|------------|-----------|
| **Erotic Romance** | Sex advances relationship arc | *The Treadmill* — scenes generate heat without changing relationship state | Scenes that could be reordered without loss | Explicit content that reveals psychology |
| **High Erotica** | Arousal is primary contract | *The Manual* — scenes read as instruction rather than experience | Clinical language, logistics over sensation | Flexible "reality" if sensation is vivid |
| **Dark Romance** | Intimacy = power = danger | *The Safety Net* — darkness declared but never felt | Power exchange without consequence | Consent complexity if intentionally interrogated |
| **Literary + Explicit** | Intimacy does thematic work | *The Detour* — explicit scene disconnected from literary concerns | Scenes that pause the novel's intellectual project | Explicitness in service of theme |
| **Thriller + Sexual** | Intimacy creates or reveals threat | *The Intermission* — sex as break from tension rather than source of it | Intimate scenes that lower stakes | Sex that raises danger or exposure |
| **Horror + Erotic** | Intimacy is site of horror | *The Costume Party* — horror aesthetics without actual dread in the intimate space | Erotic horror that is just edgy romance | Arousal-at-violation when interrogated as horror |
| **Erotica (non-romance)** | Arousal + craft; no romance arc required | *The Catalog* — scene after scene with no accumulation | Missing narrative throughline | Absence of romance beats (not the contract) |

---

## Severity Hard Gates

1. **Consent Calculus violation in non-dark contract** → Must-Fix
   - If contract = sweet/warm/steamy and consent calculus logs "Violation" → cannot be downgraded
2. **Systemic decorative pattern** → Must-Fix
   - If 50%+ of intimate scenes fail the Removal Test → erotic content is structurally inert
3. **Complete interiority loss across intimate scenes** → Must-Fix
   - If POV character has no internal experience in any intimate scene → the manuscript has a craft problem regardless of genre
4. **Zero escalation across 4+ intimate scenes** → Should-Fix minimum
   - Escalation map shows no new element, vulnerability, or power shift across consecutive scenes

---

## Distinguish Framework

### Intentional and Successful
- Erotic content is clearly doing narrative work
- Heat level matches contract
- Intimate scenes couldn't be removed without losing story information
- Escalation architecture is present and varied
- *Action:* Document and affirm; no revision needed

### Intentional but Unstable
- Author intends erotic content to do work, but execution is inconsistent
- Some scenes are load-bearing, others decorative within the same manuscript
- Consent architecture partially tracked
- *Action:* Flag inconsistencies; recommend which scenes need strengthening

### Decorative by Design
- Erotic content is genre-expected (erotica, erotic romance) and delivers reader satisfaction
- Scenes may not individually advance plot but collectively serve the reading experience
- *Action:* Distinguish from failure; note if any scenes underperform even by decorative standards

### Accidental Failure
- Intimate scenes appear without clear purpose
- Consent is unexamined
- Interiority disappears
- No escalation across the manuscript
- *Action:* Flag pattern; recommend structural revision of intimate content's role

---

## False Positive Warnings

1. **High heat is not gratuitous.** Explicit content in erotic romance is expected. Only flag if scenes don't perform narrative work.

2. **Taboo content is not automatically problematic.** Many subgenres explore forbidden or transgressive desire. Evaluate against stated contract, not generic "appropriateness."

3. **Repetition can be ritual.** In kink-focused narratives, repeated patterns can serve as anchoring ritual. Flag only when repetition produces reader disengagement, not when it produces reader anticipation.

4. **Decorative is not always a failure.** In erotica and erotic romance, some scenes exist primarily for reader pleasure. This is genre-appropriate. Flag only if the manuscript's *other* commitments (literary ambition, thriller tension, horror pressure) require every scene to earn its place.

5. **Body betrayal is not consent violation.** "My body wants what my mind resists" is a romance convention expressing internal conflict, not a consent failure. Flag only if overused (5+ instances without progression) — and that flag belongs to the Romance genre module, not here.

---

## Output Template

```markdown
## Erotic Content Tag — Audit Output

### Contract Lock
- Heat Level: [stated]
- Consent Framework: [stated]
- Kink/Content Tags: [stated]
- Parent Genre Module: [Romance / Thriller / Horror / Literary / Erotica / etc.]

### Scene-Level Assessment

| Scene | Location | Load-Bearing? | New Element | Interiority | Consent Classification | Severity Flags |
|-------|----------|---------------|-------------|-------------|----------------------|----------------|

### Escalation Map
[From Escalation vs. Repetition Audit]

### Consent Calculus Summary
[From Dimension 5 — timeline of consent states across manuscript]

### Flag Inventory
| Flag | Location | Frequency | Severity | Evidence |
|------|----------|-----------|----------|----------|

### Pattern Analysis
- Escalation trajectory: [ascending / flat / declining]
- Load-bearing ratio: [X of Y scenes pass Removal Test]
- Interiority consistency: [maintained / intermittent / absent]
- Consent architecture: [clear / partially tracked / unexamined]

### Distinguish Classification
[Intentional-Successful / Intentional-Unstable / Decorative-by-Design / Accidental Failure]

### Hard Gate Triggers
[List any triggered, with evidence]

### Top 3 Erotic Content Findings Affecting Readiness
1. [Finding + severity + blast radius]
2. [Finding + severity + blast radius]
3. [Finding + severity + blast radius]
```

---

## Integration and Handoff

### Companion Audits
- **Consent Complexity** — Deep-dive consent analysis. Activate alongside this tag for dark romance, erotic horror, conditioning narratives, dubcon. The Consent Complexity audit provides the full consent timeline, exploitation vs. exploration framework, and genre-specific consent tracking. This tag provides the scene-level Consent Calculus; Consent Complexity provides the manuscript-level consent architecture.
- **Queer Romance/Erotica** — Activate for queer pairings. Adds pronoun clarity, trope navigation, joy/struggle calibration, voyeurism check, audience orientation.
- **Interiority Preservation** — Cross-genre interiority diagnostic. This tag's EC-8 (Vanishing Interiority) is the erotic-content-specific version; Interiority Preservation covers all high-intensity scenes (combat, crisis, interrogation).
- **Female Interiority** — Activate when female characters are involved in intimate content. Tracks persistent interiority patterns beyond intimate scenes.

### Sequence Position
- Run **after** core passes (especially Pass 1, Pass 4, Pass 5, Pass 6)
- Run **alongside** Romance genre module (if active)
- Run **before** Consent Complexity (this tag identifies consent architecture; Consent Complexity evaluates it in depth)

### Pass 11 Handoff Fields
- Erotic content load-bearing ratio
- Escalation map summary
- Consent calculus summary
- Top erotic content flags affecting readiness

---

## What This Audit Is Not

1. **Not content policing.** This audit does not evaluate whether content is "appropriate." It evaluates whether content does narrative work.
2. **Not a replacement for the Romance genre module.** Romance handles relationship engine, chemistry, obstacles, trust-rupture-repair. This tag handles the intimate content layer that may or may not accompany romance.
3. **Not a consent evaluation.** For full consent analysis, use Consent Complexity. This tag tracks scene-level consent architecture; it does not provide the manuscript-level consent timeline.
4. **Not generic prose advice.** "Make the sex scenes better" is not a diagnostic. This audit identifies specific mechanisms (decorative kink, mechanical intimacy, vanishing interiority, static heat) with detection criteria.

---

## Firewall Compliance

This audit is diagnostic.

**Allowed:**
1. Identify structural failures in erotic content integration
2. Assign severity and blast radius
3. Specify revision scope (which scenes need what kind of work)

**Forbidden:**
1. Rewrite intimate scenes
2. Generate replacement erotic prose
3. Dictate kink content, heat level, or consent framework choices
4. Judge content on moral rather than craft grounds

---

*This tag audit is designed to bolt onto the APODICTIC development editor core framework. Activate during intake when manuscript includes significant erotic or intimate content, regardless of parent genre. Pairs with Romance genre module for romance manuscripts; stands alone for literary, thriller, horror, or erotica manuscripts with intimate content.*
