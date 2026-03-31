# Specialized Audit: Character & Agency Architecture — Full Audit
## Version 0.4.4
*Last Updated: February 2026*

---

## Purpose

This audit calibrates Pass 5 (Character Audit) and Pass 7 (Voice/POV) by providing:

1. **Arc Type identification** — What kind of transformation (or stability) does each character embody?
2. **Psychology Engine** — Is internal logic driving external behavior?
3. **Agency Tracking** — Who causes things to happen?
4. **Voice Distinctiveness** — Can you tell who's speaking?
5. **Ensemble Balance** — Is the cast weighted appropriately?

**Core principle:** Characters are not decorations on plot; they are the engines that make plot meaningful. A structurally sound plot with psychologically incoherent characters is a failure.

**Genre-critical note:** In feminist erotic horror, psychological thrillers, and dark romance, *character is mechanism*. If agency isn't tracked, horror becomes exploitation. If wounds don't manifest in behavior, trauma becomes window dressing.

---

## Definitions (For Reproducible Analysis)

**Scene:** A unit with a change in value/state (emotional, relational, informational, physical, institutional) AND a clear entry/exit. If a chapter has multiple value shifts, treat it as multiple scenes.

**Major Character:** Any character who (a) has POV, OR (b) appears in >15% of scenes, OR (c) materially changes the protagonist's options.

**Decision:** A choice among alternatives with a cost. ("I feel X" is not a decision; "I lie, leave, comply, report, seduce, refuse" is.)

**Required Inputs:**
1. Scene list (numbered) with 1-2 sentence summaries
2. Cast list with role assignments
3. POV map (who holds interiority where)

---

## How to Use This Audit

**Step 1: Build Character Cards**
For each major character, complete the Psychology Engine schema.

**Step 2: Identify Arc Types**
Assign each major character to an arc type and apply the corresponding logic gate.

**Step 3: Calculate Agency**
Run the AQ (Agency Quotient) calculation for protagonist and antagonist.

**Step 4: Run Voice Tests**
Apply the Blind Swap test and Interiority Markers analysis.

**Step 5: Check Ensemble Balance**
For multi-POV or ensemble casts, verify distribution and function.

---

## Part 1: Character Arc Types

Every major character should map to one arc type. The arc type determines which logic gates apply.

### A. Positive Change Arc (Growth/Redemption)

**Movement:** Lie → Truth; Wound → Healing; Closed → Open
**Best for:** Romance, heroic fantasy, coming-of-age, redemption narratives
**On the page:** Character begins with a false belief or defensive posture; by the end, they've abandoned it for something truer and more vulnerable.

**Logic Gate: The Lie Collapse**
```
CHECK: Is there a specific scene where protagonist could solve the problem
       using their old Lie (defense mechanism) but CHOOSES the Truth instead?

IF decisive moment of choosing vulnerability/new way → PASS
IF protagonist succeeds using old methods → FLAG: "Arc Not Completed"
IF protagonist changes but change not tested → FLAG: "Untested Growth"
```

**Logic Gate: The Wound Touch**
```
CHECK: Does the climax require protagonist to confront the specific wound
       established in Act I?

IF climax directly engages the wound → PASS
IF climax unrelated to wound → FLAG: "Disconnected Arc"
IF wound mentioned but not tested → SOFT FLAG: "Wound Underutilized"
```

**Genre Cross-Reference:**
- Romance: Positive arc expected; FLAG becomes STRUCTURAL BREAK if missing
- Literary Fiction: Arc may be ambiguous; verify author intent before flagging
- Thriller: Positive arc optional; protagonist may remain unchanged

---

### B. Negative Change Arc (Corruption/Fall)

**Movement:** Truth → Lie; Integrity → Corruption; Open → Closed
**Best for:** Tragedy, villain origins, noir, some horror
**On the page:** Character begins with principles or openness; by the end, they've abandoned them, usually through a series of rationalizations.

**Logic Gate: The Moral Event Horizon**
```
CHECK: Is there a clear moment where character crosses a line they
       explicitly said they would never cross in Act I?

IF decisive crossing of stated line → PASS
IF corruption happens gradually without decision point → FLAG: "Drift Corruption"
IF line crossed but not previously established → FLAG: "Unearned Fall"
```

**Logic Gate: The Rationalization Index**
```
CHECK: Count the rationalizations/excuses across the arc.

IF excuses weaken as crimes enlarge → PASS (tragic irony)
IF excuses stay constant → FLAG: "Static Justification"
IF excuses strengthen (better reasons for worse acts) → Check if intentional
IF sudden jump from minor sin to atrocity → STRUCTURAL BREAK: "Missing Gradation"

Minimum steps for believable corruption:
- Novella: 3-4 distinct compromises
- Novel: 5-7 distinct compromises
- Series: Can be spread across volumes
```

**Genre Cross-Reference:**
- Literary Fiction: Negative arc should produce recognition, not just disgust
- Horror: Corruption may be external (possession) vs. internal (choice) — verify which
- Dark Romance: Negative arc may be reframed; check contract

---

### C. Flat Arc (The Steadfast)

**Movement:** Belief Challenged → Belief Reaffirmed; Character changes the world, not self
**Best for:** Mentors, iconic heroes (Sherlock, Bond), some thriller protagonists, moral exemplars
**On the page:** Character's core belief is tested by the world; they emerge unchanged but having changed others.

**Logic Gate: The Doubt Moment**
```
CHECK: Does the world punish the character for their belief, forcing them
       to genuinely consider abandoning it?

IF genuine temptation to change in Act II → PASS
IF character never wavered → FLAG: "Superman Problem — no genuine test"
IF character wavers but test is trivial → FLAG: "Weak Challenge"
```

**Logic Gate: The World Change**
```
CHECK: If character doesn't change, does the WORLD change because of them?

IF other characters or systems transform → PASS
IF everything stays the same → FLAG: "Static Story"
```

**Genre Cross-Reference:**
- Literary Fiction: Flat arc often flagged as shallow; verify it's intentional
- Thriller: Flat arc is common and acceptable for action protagonists
- Romance: Flat arc unusual for romantic lead; check if one lead carries the change

---

### D. Disillusionment Arc (Loss of Innocence)

**Movement:** False Belief → Tragic Truth; Innocence → Knowledge
**Best for:** Coming-of-age, literary fiction, cosmic horror, war narratives
**On the page:** Character learns something true but devastating; the knowledge costs them their previous happiness or worldview.

**Logic Gate: The Irreversible Knowledge**
```
CHECK: Does learning the Truth cost them something they cannot recover?

IF knowledge destroys innocence/happiness/relationship → PASS
IF character learns dark truth but remains happy → FLAG: "Costless Revelation"
IF truth is disturbing but character "gets over it" → FLAG: "Unprocessed Disillusionment"
```

**Logic Gate: The Nostalgia Test**
```
CHECK: Does the narrative mark what was lost?

IF text acknowledges the before/after contrast → PASS
IF loss is unmarked → SOFT FLAG: "Invisible Cost"
```

---

### E. Testing Arc (Trial by Fire)

**Movement:** Belief Tested → Belief Confirmed or Broken
**Best for:** Survival horror, faith narratives, endurance stories
**On the page:** Character's core identity or belief is put under extreme pressure; they emerge either confirmed or shattered.

**Logic Gate: The Genuine Trial**
```
CHECK: Does the test actually threaten the belief, or is it a foregone conclusion?

IF outcome uncertain until crisis → PASS
IF character's victory was never in doubt → FLAG: "Fake Test"
IF test is too easy → FLAG: "Insufficient Pressure"
```

---

### Arc Selection Shortcut

When uncertain which arc applies, check the ending:

| Ending Feels Like... | Arc Type |
|---------------------|----------|
| "I'm better now" | Positive Change |
| "I'm worse now (and it's my choice)" | Negative Change |
| "I was right, but it hurt" | Flat Arc |
| "I can't go back to who I was" | Disillusionment |
| "I survived, but barely" | Testing Arc |

---

## Part 2: The Psychology Engine

Build this schema for every major character during intake or early analysis.

### Character Psychology Card

```
CHARACTER: [Name]
ROLE: [Protagonist / Antagonist / Major Supporting / etc.]
ARC TYPE: [Positive / Negative / Flat / Disillusionment / Testing]

WOUND (Ghost): [Formative trauma or absence]
  └─ Manifestation Check: Does this cause a specific mistake in Act I? [Y/N]

LIE (Misbelief): [What they believe that isn't true]
  └─ Voice Check: Do they articulate this in dialogue or thought? [Y/N]

WANT (Conscious Goal): [What they're actively pursuing]
  └─ Activity Check: Do they take steps toward this in most chapters? [Y/N]

NEED (Unconscious Requirement): [What they actually require for fulfillment]
  └─ Conflict Check: Does pursuing WANT obstruct achieving NEED? [Y/N]

FEAR (Avoidance Pattern): [What they avoid at all costs]
  └─ Stakes Check: Does the antagonist/plot force them to face this? [Y/N]

DEFENSE MECHANISMS: [How the wound manifests in behavior]
  - [e.g., Deflection through humor]
  - [e.g., Preemptive rejection]
  - [e.g., Control/micromanagement]

CORE VALUE: [What they would sacrifice everything for]
  └─ Test Check: Is this value tested in the climax? [Y/N]

TELL (Optional): [Their self-justifying story about harm they cause]
  └─ Exposure Check: Is the TELL contradicted by visible consequences? [Y/N]
```

### Psychology Logic Gates

**The Want-Need Tension**
```
CHECK: Is there genuine conflict between Want and Need?

IF achieving Want prevents achieving Need → PASS (sets up sacrifice)
IF achieving Need requires abandoning Want → PASS (sets up growth)
IF character can easily have both → FLAG: "Low Internal Conflict"
IF Want and Need are identical → FLAG: "No Internal Journey"
```

**The Wound Manifestation Check**
```
CHECK: Does the wound cause visible behavior, not just backstory?

IF wound produces at least 2 bad decisions in the manuscript → PASS
IF wound is stated but produces 0 behavioral consequences → STRUCTURAL BREAK: "Trauma Window Dressing"
IF wound produces behavior but behavior is unexplained until late reveal → FLAG: "Retroactive Motivation"
```

**The Defense Mechanism Consistency**
```
CHECK: Does character use consistent defense patterns under stress?

IF same type of defense appears 3+ times → PASS (characterization)
IF defenses vary randomly → FLAG: "Inconsistent Psychology"
IF defenses are absent under stress → Check if intentional (breakthrough moment)
```

---

## Part 2B: Trauma Physics

**Trauma obeys conservation laws:** It doesn't disappear; it **converts** into symptoms, choices, distortions, and relational patterns.

### The Trauma Loop

For characters with significant wounds, map this cycle:

```
TRIGGER → APPRAISAL → SOMATIC RESPONSE → BEHAVIOR → COST → REINFORCEMENT

- Trigger: External cue or internal memory that activates the wound
- Appraisal: The Lie interprets the moment ("This means I'm unsafe/unlovable/trapped")
- Somatic Response: Freeze/flight/fawn, arousal mismatch, nausea, dissociation
- Behavior: Compliance, provocation, avoidance, confession, retaliation
- Cost: Lost time, lost trust, lost status, bodily harm, self-contempt
- Reinforcement: The world "rewards" the maladaptive pattern (dangerous!)
```

### Trauma Logic Gates

**The Manifestation Gate**
```
IF WOUND exists AND behavioral cost = 0
THEN → STRUCTURAL BREAK: "Trauma Window Dressing"

Trauma must cost something in the present story:
- A bad decision
- A misread situation
- A defensive reaction that damages a relationship
- A moment of paralysis at a critical juncture
```

**The Repair Gate (Optional but Powerful)**

If the story offers repair, define:
- **What is repaired?** (Body, trust, epistemic certainty, self-image)
- **What is NOT repairable?** (Irreversible cost—the scar that remains)
- **Who pays for repair?** (Protagonist, partner, third party, institution)

```
IF repair offered AND nothing remains unrepaired → SOFT FLAG: "Too-Clean Recovery"
IF repair offered AND cost is visible → PASS
IF no repair offered → Check if intentional (horror, tragedy)
```

---

## Part 3: Agency Tracking (The AQ Metric)

### Definitions

**Active Decision:** Character takes action that changes plot direction without being forced or ordered to. They had alternatives; they chose this.

**Reactive Action:** Character responds to immediate threat or stimulus. Necessary for survival but doesn't demonstrate agency over story direction.

**Puppet Action:** Character acts against their established psychology because the plot needs them somewhere or doing something. The hand of the author is visible.

### The Formula

```
AQ (Agency Quotient) = Active Decisions / Total Scenes Featuring Character
```

### The Thresholds

| Character Role | Minimum AQ | Below Threshold Flag |
|----------------|------------|---------------------|
| **Protagonist** | 0.40 (40%) | "Passive Protagonist" |
| **Antagonist** | 0.30 (30%) | "Reactive Antagonist" |
| **Major Supporting** | 0.20 (20%) | "Satellite Character" |
| **Love Interest** | 0.25 (25%) | "Trophy Character" |

### Agency Audit Table

```
| Scene | Character Present | Action Type | Decision Made | Plot Changed? |
|-------|-------------------|-------------|---------------|---------------|
| Ch 1  | Protagonist       | Active      | Leave home    | Yes           |
| Ch 2  | Protagonist       | Reactive    | Flee attacker | No            |
| Ch 3  | Protagonist       | Puppet      | Go to party   | Yes (but why?)|
```

### Puppet Detection

**Signs of puppet action:**
- Character does something they previously said they wouldn't, without justification
- Character goes somewhere for no reason except that's where the next scene happens
- Character trusts someone they have no reason to trust
- Character fails to take an obvious action that would solve the problem
- Character's intelligence or competence drops for one scene

```
IF Puppet Actions > 2 for any character → FLAG: "Plot-Serving Behavior"
IF Puppet Actions > 0 for Protagonist in climax → STRUCTURAL BREAK: "Protagonist Not Driving Climax"
```

### Genre Cross-Reference

- **Horror:** Lower protagonist AQ acceptable (0.30) if genre is survival horror
- **Romance:** Both romantic leads should have AQ > 0.30
- **Thriller:** Protagonist AQ should be high (0.50+); they should be driving the investigation
- **Literary Fiction:** AQ may be lower if passivity is thematic (explicitly examined)

---

## Part 3B: Constraint Quotient (CQ) — Agency Under Coercion

**For erotic horror, dark romance, captivity narratives, and institutional horror.**

Standard AQ doesn't capture choice-under-constraint. A coerced protagonist can still be dramatically *active* if they are choosing within a trap.

### The Formula

```
CQ (Constraint Quotient) = Constrained Choices / Total Scenes Appeared In
```

**Constrained Choice:** A decision made when options are narrowed by power, threat, dependency, conditioning, or social/institutional consequence. The character chooses, but the menu is limited.

### CQ Interpretation

| Pattern | Meaning | Genre Expectation |
|---------|---------|-------------------|
| Low AQ, Low CQ | Passive victim; no choices | Usually a problem |
| Low AQ, High CQ | Choosing within a trap | Expected in captivity/coercion narratives |
| High AQ, Low CQ | Free agent | Expected in thriller/adventure |
| High AQ, High CQ | Fighting back under pressure | Expected in resistance narratives |

### The Trajectory Check

```
CHECK: How does CQ change over the arc?

IF CQ rises over time (increasing constraint) → Common in horror; verify it's recognized
IF CQ falls over time (increasing freedom) → Escape/recovery arc
IF CQ stays constant → FLAG FOR REVIEW: "Static Constraint"
```

### The Stance Check (Anti-Exploitation Gate)

**Critical for erotic horror and dark romance.** For any scene with high CQ, answer:

1. Does the text **register** the constraint? (Even if character denies it)
2. Is there **aftereffect**? (Shame, confusion, rage, numbness, compulsive reenactment)
3. Does the narrative avoid framing arousal as **exculpation**?

```
IF "No" to 2+ of the above → FLAG: "Ethics Leak"
IF arousal is used to erase harm → FLAG: "Arousal as Alibi"
IF violation occurs then vanishes without trace → FLAG: "Aftereffect Vacuum"
```

---

## Part 4: Voice & Interiority Audit

### The Blind Swap Test

**Procedure:**
1. Extract 10 dialogue lines from Character A (without tags or context)
2. Extract 10 dialogue lines from Character B
3. Shuffle and attempt to attribute

**Logic Gate:**
```
IF correct attribution > 70% → PASS (voices distinct)
IF correct attribution 50-70% → SOFT FLAG: "Similar Voices"
IF correct attribution < 50% → FLAG: "Generic Voice — characters interchangeable"
```

### Interiority Markers

Track these distinctive fingerprints per character:

| Marker | What to Track | Example |
|--------|---------------|---------|
| **Sentence Length** | Fragments vs. compound | "Character A thinks in fragments. Sharp. Cutting." vs. "Character B thinks in long, flowing sentences that circle around the point." |
| **Filter Words** | How they process | "Noticed" vs. "Decided" vs. "Felt" vs. "Analyzed" |
| **Attention Focus** | What they observe | Character A notices exits; Character B notices faces |
| **Taboo Topics** | What they NEVER think about | The void is as distinctive as the content |
| **Metaphor Family** | Where their comparisons come from | Military metaphors vs. domestic vs. natural |
| **Self-Talk Register** | How they address themselves | Harsh critic vs. gentle coach vs. detached observer |

**Logic Gate:**
```
IF character has 3+ distinctive markers consistently applied → PASS
IF character has 1-2 markers → SOFT FLAG: "Thin Voice"
IF character has 0 markers OR markers inconsistent → FLAG: "No Distinctive Interiority"
```

### Interiority Function Check

For each significant interiority passage, tag its function:

- **Reveals character** (we learn something new about who they are)
- **Creates recognition** (reader sees themselves or human truth)
- **Builds pressure** (we understand what's at stake internally)
- **Earns emotion** (grounds feeling in specific thought)
- **Complicates** (adds nuance to simple interpretation)
- **Delays** (marks time without adding value)
- **Substitutes** (tells what could be shown)
- **Unclear** (no identifiable function)

```
IF > 75% of interiority is functional (first 5 categories) → PASS
IF 50-75% functional → SOFT FLAG: "Some Deadweight Interiority"
IF < 50% functional → FLAG: "Interiority Not Earning Space"
```

---

## Part 5: Character Function Audit

### Role Definitions

| Role | Function | Required? |
|------|----------|-----------|
| **Protagonist** | Engine — drives decisions that create plot | Yes |
| **Antagonist** | Brake — opposes Want, forces growth | Yes (can be internal/abstract) |
| **Foil/Mirror** | Warning — shows what protagonist could become or refuses to become | Recommended |
| **Catalyst** | Spark — forces change without having own arc | Optional |
| **Mentor** | Guide — provides tools/wisdom, often removed | Optional |
| **Shapeshifter** | Uncertainty — allegiance unclear, tests trust | Optional |
| **Threshold Guardian** | Test — blocks progress, must be overcome | Optional |
| **Witness/Chorus** | Names what others deny; provides external reality check | Optional |
| **Institutional Mouth** | Speaks the system's alibis (HR, clinician, committee) | Genre-specific |
| **Gatekeeper** | Controls access to resource/status/permission | Genre-specific |

### Redundancy Check

**The Merge Test:**
```
CHECK: Do Character A and Character B:
- Appear in the same scenes?
- Agree on the same positions?
- Offer the same skills/perspectives?
- Have similar relationships to protagonist?

IF 3+ of the above → FLAG: "Potential Merge — consider combining"
IF A can be removed without structural loss → FLAG: "Redundant Character"
IF both are necessary but similar → SOFT FLAG: "Differentiate Further"
```

### Missing Function Check

```
CHECK: Does the cast include:

☐ Someone who opposes protagonist's Want?
☐ Someone who embodies protagonist's Fear or possible future?
☐ Someone who knows protagonist's secret/wound?
☐ Someone who challenges protagonist's Lie?

IF any missing → FLAG FOR REVIEW: "Possible Missing Function"
```

---

## Part 6: Ensemble Balance

For multi-POV or ensemble casts.

### Distribution Table

```
| Character | Word Count | % Total | POV Scenes | Active Decisions | Arc Status |
|-----------|------------|---------|------------|------------------|------------|
| Char A    | 30,000     | 40%     | 12         | 8                | Complete   |
| Char B    | 22,500     | 30%     | 9          | 5                | Complete   |
| Char C    | 15,000     | 20%     | 6          | 4                | Incomplete |
| Char D    | 7,500      | 10%     | 3          | 1                | FLAG       |
```

### Balance Logic Gates

**The Ghost POV:**
```
IF POV character has < 15% of word count → FLAG FOR REVIEW: "Underweight POV"
   Ask: Is this a vital limited perspective or a head-hop?
```

**The Dropped Thread:**
```
IF character has > 20% presence in Act I and < 5% in Act III (without dying)
   → FLAG: "Dropped Character Thread"
```

**The Unearned POV:**
```
IF character has POV access but AQ < 0.15
   → FLAG: "POV Without Agency — why are we in this head?"
```

**The Arc Completion Check:**
```
IF character has > 20% word count but arc marked "Incomplete"
   → FLAG: "Major Character Without Resolution"
```

---

## Part 7: Diagnostic Flags

Named problems with detection logic.

### 1. "Sexy Lamp" / Satellite

**Definition:** A character who could be replaced by an object with a note attached without changing the plot. Often applied to love interests or female characters in male-POV stories, but can affect any character.

**Detection:**
```
CHECK: Does this character have a WANT independent of the protagonist?

IF independent want exists and is pursued → PASS
IF all wants relate to protagonist → FLAG: "Satellite Character"
IF character exists only to be rescued/desired/supportive → STRUCTURAL BREAK: "Sexy Lamp"
```

**Fix:** Give them a goal that conflicts with or complicates the protagonist's goal.

---

### 2. "Informed Attribute"

**Definition:** We're told they're brilliant/dangerous/charming but never shown evidence.

**Detection:**
```
CHECK: For any stated attribute (smart, funny, dangerous, kind):
       Count scenes where attribute is DEMONSTRATED.

IF demonstrations ≥ 3 → PASS
IF demonstrations = 1-2 → SOFT FLAG: "Underdeveloped Attribute"
IF demonstrations = 0 → FLAG: "Informed Attribute — show, don't tell"
```

---

### 3. "Personality Transplant"

**Definition:** Character behaves inconsistently without justification.

**Detection:**
```
CHECK: Does character exhibit opposite traits in different scenes
       without intervening cause?

Examples:
- Brave in Ch 3, cowardly in Ch 5 (no trauma between)
- Trusting in Ch 2, paranoid in Ch 7 (no betrayal between)
- Competent in Ch 1, bumbling in Ch 4 (no explanation)

IF opposite behaviors with cause → PASS
IF opposite behaviors without cause → FLAG: "Personality Transplant"
```

**Fix:** Either establish the trigger for the shift or choose a consistent characterization.

---

### 4. "Trauma Window Dressing"

**Definition:** Character has tragic backstory that never affects present behavior.

**Detection:**
```
IF [WOUND/TRAUMA] stated in text
AND [DECISIONS CAUSED BY WOUND] = 0
AND [MISINTERPRETATIONS CAUSED BY WOUND] = 0
THEN → STRUCTURAL BREAK: "Trauma Window Dressing"
```

**Fix:** The wound must cost them something in the present story — a bad decision, a misread situation, a defensive reaction that damages a relationship.

---

### 5. "Retroactive Motivation"

**Definition:** Motivation is revealed after the action it supposedly explains.

**Detection:**
```
CHECK: When is the motivation for a major action revealed?

IF motivation established before or during action → PASS
IF motivation revealed after action (flashback/confession) → FLAG FOR REVIEW
IF action seemed unmotivated until late reveal → FLAG: "Retroactive Motivation"
```

**Note:** This can work if the mystery of "why did they do that?" is intentionally cultivated. Check author intent.

---

### 6. "Maid and Butler"

**Definition:** Characters exist only to deliver exposition to each other.

**Detection:**
```
CHECK: Do two characters primarily exchange information the reader needs
       rather than pursuing their own goals?

IF characters have independent goals AND exchange information → PASS
IF characters exist mainly for exposition delivery → FLAG: "Maid and Butler Dialogue"
```

---

### 7. "Genius Without Feats"

**Definition:** Character described as highly competent but never demonstrates it.

**Detection:**
```
CHECK: For characters described as "genius/expert/master":
       Does the story show them solving a problem others couldn't?

IF unique contribution demonstrated → PASS
IF competence only claimed → FLAG: "Genius Without Feats"
```

---

### 8. "The Devouring Protagonist"

**Definition:** Supporting characters lose their distinctiveness in protagonist's presence.

**Detection:**
```
CHECK: Do supporting characters have different interiority/voice when POV
       vs. when observed by protagonist?

IF characters consistent across POV types → PASS
IF characters flatten when protagonist observes them → FLAG: "Protagonist Devours Supporting Cast"
```

---

### 9. "Therapeutic Alibi" *(Genre-Specific: Dark Romance, Erotic Horror)*

**Definition:** Harm is laundered through care-language. The manipulator's abuse is framed as therapy, guidance, or healing.

**Detection:**
```
CHECK: Does a character causing harm frame it as "for your own good"?

IF care-framing + visible harm + contradiction/consequence → PASS (critique is present)
IF care-framing + visible harm + no contradiction → FLAG: "Therapeutic Alibi"
IF care-framing + no visible harm → Check if harm is genuinely absent or unregistered
```

**Fix:** Insert contradiction: a consequence, a witness who names the harm, or a self-recognition beat where the protagonist glimpses the truth.

---

### 10. "Authorial Collusion" *(Genre-Specific: Dark Romance, Psychological Thriller)*

**Definition:** The narration grants the manipulator unchallenged rhetorical dominance. The prose itself sides with the abuser.

**Detection:**
```
CHECK: Does the manipulator always get the last word?
       Are their justifications presented without narrative pushback?
       Does the prose style become admiring/seductive during their scenes?

IF manipulator rhetoric is challenged by consequence, POV skepticism, or irony → PASS
IF manipulator's framing goes uncontested and prose validates it → FLAG: "Authorial Collusion"
```

**Fix:** Deny them the "last clean sentence." Force a cracked admission, observable harm, or shift POV to show their methods from outside.

---

## Part 8: Character-to-Theme Mapping

For literary fiction and thematically complex work.

### The Argument Distribution

**Check:** Does each major character embody a different position on the central question?

```
CENTRAL QUESTION: [e.g., "Is revenge ever justified?"]

| Character | Position | How Demonstrated |
|-----------|----------|------------------|
| Char A    | Yes, always | Pursues revenge, finds peace |
| Char B    | Yes, sometimes | Chooses revenge selectively |
| Char C    | Never | Refuses revenge, pays price |
| Char D    | [Same as A?] | → FLAG if duplicate |
```

### The Embodiment Check

```
CHECK: Does each thematic position have consequences in the story?

IF position is tested and costs/rewards are visible → PASS
IF position is stated but untested → FLAG: "Theme Without Stakes"
IF story only tests one position → SOFT FLAG: "Thesis, Not Exploration"
```

---

## Part 9: Moral Argument Architecture

**Based on:** John Truby's *The Anatomy of Story*. Extends Part 8 (Character-to-Theme Mapping) by requiring that character structure and thematic argument are mechanically coupled — the protagonist's defining weakness generates the story's moral question, and the story's events force a self-revelation that answers it.

**Core claim:** A story can have a sound spine and psychologically coherent characters and still feel hollow. When the protagonist's arc doesn't enact a moral argument — when weakness doesn't generate theme and the climax doesn't prove a value stance — the story resolves plot without resolving meaning.

### Activation

**Hard gates (both must be true):**

1. Protagonist hypothesis is stable (AQ computation possible even if weak)
2. A throughline conflict exists (Plot Architecture fit, or Franklin candidate spine)

If either fails: route to Franklin Pathway (pre-spine) or protagonist identification failure protocol.

**Soft triggers (activate when ≥2 are true):**

- Pass 1 reports "competent but hollow," "theme feels tacked on," or "I don't buy the arc"
- Plot Architecture fit passes, but synthesis flags "meaning thin" or "ending unearned"
- Pass 4 shows emotional turns but reader reports "no moral weight"
- Character Architecture finds AQ/CQ viable but arc feels decoupled from plot outcomes
- Emotional Craft audit shows repeated B2 (no judgment) or B3 (no impulse) breakpoints

### Scope

Analyze the protagonist line across three windows:

- Opening 10–15%: establish weakness strategy + desire line
- One mid-turn cluster (midpoint or equivalent): where plan is tested and value pressure applied
- Climax / resolution: moral choice proof

For long or braided manuscripts: scope to the dominant thread (one protagonist + one main opposition axis).

### Code Namespace Note

This section uses M-codes (moral argument), W-codes (weakness), N-codes (need), DN-codes (desire-need tension), OCA-codes (opponent counter-argument), PW-codes (plan-worldview), SR-codes (self-revelation), MC-codes (moral choice), and TP-codes (thematic pressure).

**PW** is used instead of P to avoid collision with Scene Turn Diagnostics P-codes (P1–P5, pattern flags). No other collisions with existing code systems: G/C/O/Sq/H/U/P (Scene Turn), S/B (Emotional Craft), F/QS/I/ST/SW/AS/A/LC/E (Narrative Nonfiction Craft).

### Step 1: Moral Argument Hypothesis (M-codes)

Produce a falsifiable moral argument statement extracted from the text:

**Format:** "This story argues that [value claim], because when [protagonist] faces [pressure], they must [new stance/choice] instead of [weakness strategy]."

Build the Moral Argument Card for the protagonist (and optionally the main opponent):

```
CHARACTER: [Name]

MORAL ARGUMENT HYPOTHESIS:
  "This story argues that __________, because when [protagonist]
  faces __________, they must __________ instead of __________."

PSYCHOLOGICAL WEAKNESS: [How the character is hurting themselves]
  └─ From Psychology Engine: Which WOUND / LIE / DEFENSE MECHANISM?
  └─ Behavioral evidence: [specific scenes where weakness costs them]

MORAL WEAKNESS: [How the character is hurting others]
  └─ Distinguished from psychological weakness: [how?]
  └─ May be unconscious: [does the character recognize the harm?]
  └─ Behavioral evidence: [specific scenes where others pay for this flaw]

DESIRE: [= WANT from Psychology Engine]

NEED:
  Psychological need: [what they need to overcome the psychological weakness]
  Moral need: [what they need to stop hurting others]
  └─ Are these the same or different?
  └─ If different, which does the story prioritize?

SELF-REVELATION: [The moment where the character sees their weakness clearly]
  └─ Psychological self-revelation: [sees how they've been hurting themselves]
  └─ Moral self-revelation: [sees how they've been hurting others]
  └─ Location in manuscript: [scene reference]
```

**Output:** Best hypothesis + one alternate (if text supports more than one).

**M-code failure taxonomy:**

| Code | Name | Description |
|------|------|-------------|
| **M0** | No arguable claim | Only topic/issue ("about grief," "about injustice"); no enacted value stance |
| **M1** | Slogan claim | Abstract moral without behavioral enactment; thesis without proof |
| **M2** | Claim contradicted by ending | Resolution rewards the opposite stance from what the arc argues |
| **M3** | Competing claims | Incompatible moral arguments without acknowledged tension; frame whiplash |

### Step 2: Weakness as Strategy (W-codes)

Test whether the protagonist's "weakness" is a recurring behavioral strategy that creates predictable costs — not a trait label.

**Evidence requirement:** 2–3 separate instances of the pattern under pressure.

Weakness must be:
- **Behavioral:** controls, avoids, performs, lies, pleases, punishes, withdraws — verbs, not adjectives
- **Recurrent:** appears across multiple pressure moments, not just stated once
- **Costly:** creates conflict, escalation, or loss — not just internal sadness

```
WEAKNESS STRATEGY: [verb-based description]
  Instance 1: [scene reference + cost]
  Instance 2: [scene reference + cost]
  Instance 3: [scene reference + cost]
  Code: [W-code or PASS]
```

**W-code failure taxonomy:**

| Code | Name | Description |
|------|------|-------------|
| **W0** | Trait-only | "She's insecure" — no repeated behavioral strategy; adjective, not verb |
| **W1** | Costless weakness | Pattern present but doesn't cause losses or escalation; decorative flaw |
| **W2** | Non-protagonist weakness | The real engine belongs to another character; protagonist is along for the ride |
| **W3** | Condition not strategy | "He is poor/sick/unlucky" — external condition, not behavioral choice |

**Cross-reference:** Psychology Engine (Part 2) maps wound, lie, defense mechanisms. W-codes test whether those mapped elements function as a *recurring strategy with costs* in the actual text. A character can have a fully populated Psychology Card and still fail W0 if the weakness never manifests as repeated behavior.

### Step 3: Need as Revaluation (N-codes)

Test whether the "need" is a genuine change in judgment or value that alters decisions — not a skill acquisition or stated lesson.

The Psychological/Moral Need Distinction remains key:

| Type | Question | Example |
|------|----------|---------|
| **Psychological need** | What must the character learn to stop self-destructing? | "I need to stop running from intimacy" |
| **Moral need** | What must the character learn to stop hurting others? | "I need to stop using people as shields against my own fear" |

**Logic Gate: Dual Need**
```
CHECK: Does the story distinguish psychological need from moral need?

IF both needs present and both tested → PASS (strongest moral argument)
IF only psychological need → SOFT FLAG: "Self-Focused Arc"
IF only moral need → SOFT FLAG: "Other-Focused Arc"
IF neither need identifiable → FLAG: "No Need Identified"
```

**N-code failure taxonomy (tests need quality, not presence):**

| Code | Name | Description |
|------|------|-------------|
| **N0** | Need is skill | "Needs to learn to fight/hack/negotiate" — competence, not moral revaluation |
| **N1** | Need asserted not enacted | Character states the lesson but later choices don't change |
| **N2** | Circumstantial change | Behavior changes only because situation changes; remove the new circumstances and the old pattern returns |
| **N3** | Offstage change | Change occurs without observable turning point or test; character is different but we don't see why |

**Evidence requirement:** One late-stage choice or behavior that differs meaningfully from early pattern under similar pressure.

**Important:** Not every story needs both psychological and moral need. Romance may emphasize psychological need; crime fiction may emphasize moral need; literary fiction often requires both. The Dual Need gate is informational; N-codes diagnose quality.

### Step 4: Desire vs Need Tension Map (DN-codes)

Test whether external desire pulls against internal need through the middle — and whether the tension forces sacrifice.

**Extract:**
- **Desire line:** concrete external objective (win case, get job, save person, be loved)
- **Need line:** revaluation that complicates the pursuit (honesty, mercy, autonomy, trust)

**Output: 3-point tension map:**
```
EARLY: Desire = [objective]; Need = [not yet visible / embryonic]
  Tension: [none / low / present]
MID: Desire = [still pursued]; Need = [emerging / conflicting]
  Tension: [present — describe tradeoff moment]
LATE: Desire vs Need = [sacrifice / compromise / integration / tragic refusal]
  Resolution: [which won? at what cost?]
```

**DN-code failure taxonomy:**

| Code | Name | Description |
|------|------|-------------|
| **DN0** | No tension | Desire and need align too early; moral conflict collapses before the middle |
| **DN1** | Desire absent | Protagonist drifts/reacts; no pursuit line to generate tension against need |
| **DN2** | Need absent | Plot-only story; desire is satisfied but no resonance because no revaluation was at stake |
| **DN3** | Tension untested | Desire-need conflict exists but never forces a sacrifice; talked about, not enacted |

**Cross-reference:** Psychology Engine's Want-Need Tension gate tests *presence*. DN-codes test *distribution and escalation* — whether the tension builds and forces a cost-bearing choice.

### Step 5: Opponent as Counter-Argument (OCA-codes)

Test whether the main opposition embodies a value system that challenges the protagonist's worldview — not just an obstacle that blocks the plot.

**Evidence requirement:** At least one confrontation where the opponent's logic is legible, plus one moment where the opponent wins or exposes the protagonist's weakness.

**Logic Gate: Opponent Alignment**
```
CHECK: Does the main opponent compete with the protagonist
       for the same goal, value, or moral territory?

IF opponent wants the same thing by different means → PASS (strongest opposition)
IF opponent wants something different that blocks protagonist → ADEQUATE
IF opponent is simply evil/obstructive without moral position → OCA0: "Flat Opposition"
IF opponent embodies what the protagonist could become → PASS (enhanced — mirror function)
```

**OCA-code failure taxonomy:**

| Code | Name | Description |
|------|------|-------------|
| **OCA0** | Obstacle-only | Opposition blocks but has no ideology or value stance; pure obstruction |
| **OCA1** | Strawman | Opponent's value stance is incoherent or purely evil; argument is rigged |
| **OCA2** | Mis-targeted | Opponent challenges plot desire but doesn't expose moral weakness |
| **OCA3** | Diffuse opposition | Many minor antagonists; no coherent counter-argument axis |

**Cross-reference:** Character Function Audit (Part 5) Foil/Mirror role. OCA-codes test whether the *main antagonist* functions as a moral mirror, not just supporting characters.

### Four-Corner Opposition

For complex narratives (literary fiction, ensemble, multi-protagonist), check whether the cast generates a multi-sided moral argument:

```
MORAL QUESTION: [The central question the story explores]

| Character | Position | How Demonstrated | Cost Shown |
|-----------|----------|------------------|------------|
| Protagonist | [their answer] | [scenes] | [what it costs them] |
| Main Opponent | [different answer] | [scenes] | [what it costs them] |
| Ally/Secondary | [third answer] | [scenes] | [what it costs them] |
| [Fourth character] | [fourth answer] | [scenes] | [what it costs them] |
```

**Logic Gate: Argument Coverage**
```
CHECK: Are there at least 3 distinct moral positions represented in the cast?

IF 3+ positions, each with consequences → PASS
IF 2 positions (protagonist vs. opponent only) → ADEQUATE for most genres
IF 1 position (everyone agrees) → FLAG: "No Moral Argument"
IF 4+ positions with consequences → PASS (enhanced complexity)
```

**Cross-reference:** Part 8 Argument Distribution. Four-Corner Opposition is the structural test; Part 8's Embodiment Check verifies consequences.

### Step 6: Plan as Worldview (PW-codes)

Test whether the protagonist's plan/approach is an expression of their weakness-based worldview — not generic logistics.

Plan is method choice, not task list: control vs. trust, force vs. persuasion, secrecy vs. openness, rule-following vs. transgression.

**Evidence requirement:** 1 early plan, 1 mid adaptation, and what caused the adaptation.

**PW-code failure taxonomy:**

| Code | Name | Description |
|------|------|-------------|
| **PW0** | No plan line | Pure reactivity; protagonist is pushed along by events with no strategy |
| **PW1** | Generic plan | Any character could use this strategy; doesn't express the specific worldview |
| **PW2** | External failure only | Plan fails due to luck or circumstance, not because of weakness pressure |
| **PW3** | Adaptation without learning | Shifts tactics under pressure but without value-level pressure or revaluation |

**Cross-reference:** When Plot Architecture flags a "spine that works but feels arbitrary," check PW-codes. Plans that emerge from the Lie feel inevitable; plans that emerge from the author's convenience feel imposed. If the plan fails *because* it expresses the weakness, plan and flaw are mechanically coupled (strongest integration).

### Step 7: Self-Revelation Evidence (SR-codes)

Test whether there is an identifiable point where the protagonist's interpretation or judgment changes — and whether that change matters.

A self-revelation is: an epistemic reframe ("I was wrong about X," "the cost is Y," "I can't keep doing Z"), tied to earlier evidence, that produces different subsequent choices.

**Logic Gate: Self-Revelation Quality**
```
CHECK: Does the self-revelation connect the character's weakness
       to the story's moral argument?

IF revelation addresses both psychological and moral weakness → PASS
IF revelation addresses only psychological weakness → ADEQUATE
IF no revelation occurs → Check arc type:
   - Negative arc: absence of revelation IS the tragedy → PASS
   - Flat arc: character already knows the truth → PASS (verify Part 1C)
   - Positive arc without revelation → SR0
```

**SR-code failure taxonomy:**

| Code | Name | Description |
|------|------|-------------|
| **SR0** | No revelation | Outcome happens, but protagonist's stance/understanding doesn't shift |
| **SR1** | Revelation as speech | Declared in dialogue or thought but not behaviorally tested afterward |
| **SR2** | Revelation unearned | Arrives without causal groundwork; insight from nowhere |
| **SR3** | Revelation irrelevant | Doesn't affect the climactic choice; epiphany goes unused |

### Step 8: Moral Choice Proof (MC-codes)

Test whether the climax forces a cost-bearing moral choice that proves the argument.

**Logic Gate: Moral Choice Proof**
```
CHECK: Does the climax require the protagonist to make a choice that demonstrates
       their new moral understanding?

IF climactic choice proves new moral stance (character acts against old pattern) → PASS
IF character fails to change (negative arc) and the failure IS the tragedy → PASS
IF climax resolves through fate, accident, or another character's action → MC0
IF choice has no cost → MC1
```

**MC-code failure taxonomy:**

| Code | Name | Description |
|------|------|-------------|
| **MC0** | No choice | Climax is fate, accident, deus ex machina, or someone else's action; protagonist doesn't decide |
| **MC1** | Choice without cost | Easy win; the "right" choice costs nothing, so the argument is unproven |
| **MC2** | Tactical-only choice | Plot victory without value stake; wins the battle but proves no moral stance |
| **MC3** | Ending contradicts choice | Narrative reward/punishment sends opposite moral message from what the choice enacts |

**Cross-reference:** Part 1A's Lie Collapse gate tests whether the protagonist chooses Truth over Lie. MC-codes test whether that choice specifically addresses the *moral* dimension and carries cost.

### Step 9: Thematic Pressure Distribution (TP-codes)

Test whether value tests are distributed across the middle — not concentrated at the ending.

**Identify 2–4 moments where:**
- Protagonist pays a cost because of weakness strategy
- Protagonist has a chance to choose differently and doesn't (or does)
- The moral argument is advanced, complicated, or tested by events

```
Value Test 1: [scene reference]
  What's tested: [which aspect of weakness/need/moral argument]
  Cost: [what it costs]
  Escalation from previous: [how stakes or stakes dimension changed]

Value Test 2: [scene reference]
  ...
```

**TP-code failure taxonomy:**

| Code | Name | Description |
|------|------|-------------|
| **TP0** | Theme only at end | Middle feels like plot errands; moral argument absent until climax |
| **TP1** | Repetitive tests | Same moral test repeated without escalation; argument stalls |
| **TP2** | Unlinked tests | Value tests occur but aren't connected to protagonist's weakness/need; random dilemmas |

### Common Patterns (Named Failure Modes)

**FM-T1: Theme-as-Slogan.** M1 (slogan claim) + TP0 (theme only at end). The story has a message — you can find it in the final chapter, maybe in dialogue. But nothing in the preceding 80% enacts, tests, or complicates it. The moral argument is an afterthought, not a structure.

**FM-T2: Plot Resolves / Stance Doesn't.** SR0 (no revelation) or MC0/MC2 (no moral choice). The story reaches an ending — the villain is defeated, the goal is achieved, the lovers unite. But the protagonist's moral stance is identical at the end to what it was at the beginning. The plot resolved; the character didn't.

**FM-T3: Costless Weakness.** W1 (weakness without cost) + DN3 (tension never forces sacrifice). The protagonist has a flaw — it's stated, maybe even dramatized — but it never costs them anything they can't recover. The weakness is decorative.

**FM-T4: Opponent Without Argument.** OCA0 (obstacle-only) or OCA2 (mis-targeted). The antagonist blocks the protagonist effectively, but embodies no value position. The conflict is tactical, not moral. The story has a villain but no counter-argument.

**FM-T5: Unproven Growth.** SR1 (revelation as speech) + MC1 (choice without cost). The character says they've changed. The narrative agrees. But the change was never tested by a cost-bearing choice. Growth by assertion.

### Genre Calibration

**Thriller / Action:** Moral argument can be lean, but MC-test must pass — climax should prove a value stance, not just win tactically. Allow compressed introspection; require choice + cost.

**Romance:** Opponent-as-counter-argument may be relational or internal. DN-test and MC-test are high-severity: love vs. self-protection, honesty vs. control, autonomy vs. belonging. Vulnerability IS the moral choice.

**Horror:** Opponent axis may be existential or systemic; PW-codes often reveal denial as worldview. SR-test can be tragic (refusal) and still pass if MC-test proves a stance through doom. Negative arcs are genre-normative.

**Literary / Upmarket:** Higher expectation for M-test clarity and TP distribution (value tests throughout), even if plot is quiet. Both psychological and moral need typically required.

**Erotic Horror / Dark Romance:** CQ-adjacent concerns (Part 3B Stance Check) interact with moral argument. If the protagonist's moral weakness is complicity or consent confusion, W-codes and MC-codes diagnose whether the text examines this or exploits it.

### Orchestration with Other Audits

**With Emotional Craft Diagnostics:** If Emotional Craft shows repeated B2 (no judgment) or B3 (no impulse) breakpoints, the Truby layer often explains why: the story lacks a coherent moral stance being tested. Conversely, Truby failures predict Emotional Craft "flatness" even when plot is functional.

**With Scene Turn Diagnostics:** If Scene Turn shows Sq2 (sequel drift — no decision), check whether sequels fail to terminate in decisions that express the evolving desire-need tension. DN-codes and Sq-codes may co-diagnose.

**With Narrative Nonfiction Craft Audit:** For nonfiction with character throughlines (profiles, memoir, narrative journalism), the moral argument layer applies. SW-codes (meaning line) from the Nonfiction Craft audit correspond to M-codes here — both test whether the piece earns its interpretive claim.

### Integration with Existing Character Architecture

This section extends, not replaces, existing infrastructure:

| Existing Tool | What It Does | What Moral Argument Adds |
|---------------|-------------|-------------------------|
| Psychology Engine (Part 2) | Maps wound, lie, want, need, fear | Splits NEED into psychological/moral; adds MORAL WEAKNESS; W-codes test behavioral strategy |
| Arc Types (Part 1) | Identifies transformation pattern | Tests whether transformation answers a moral question; MC-codes test the climactic choice |
| Character-to-Theme Mapping (Part 8) | Maps characters to thematic positions | M-codes test whether protagonist's weakness generates the theme; TP-codes test distribution |
| Character Function Audit (Part 5) | Identifies roles | OCA-codes test whether opponent functions as moral mirror with legible counter-argument |
| Plot Architecture | Diagnoses spine viability | PW-codes test whether the protagonist's strategy reveals character or feels arbitrary |
| Emotional Craft Diagnostics | Tests emotional transmission | B2/B3 breakpoints predict Truby-layer failures; orchestration guidance above |

**Output:** Moral Argument Card + 9-step diagnostic results (M/W/N/DN/OCA/PW/SR/MC/TP codes) + failure mode patterns + revision targets.

**When to run this section:**
- Literary fiction with thematic ambitions
- Any manuscript where Part 8 identifies a central question but the protagonist's arc doesn't engage it
- When Character Architecture shows solid AQ/CQ but the arc feels "arbitrary" or "tacked on"
- When the climax resolves plot but doesn't resolve theme
- When Emotional Craft shows persistent B2/B3 breakpoints that plot-level diagnosis can't explain

---

## Integration with Core Framework

This audit modifies:
- **Pass 5 (Character Audit):** Replaces general guidance with Psychology Engine + Arc Types + AQ calculation
- **Pass 7 (Voice/POV):** Adds Blind Swap test, Interiority Markers, ensemble balance thresholds
- **Synthesis:** Include arc completion status, AQ scores, voice distinctiveness, ensemble balance, moral argument analysis (M/W/N/DN/OCA/PW/SR/MC/TP codes when Part 9 is active), flag list

**Output:** Character cards, AQ calculations, arc diagnoses, voice analysis, ensemble balance table, moral argument card with 9-step diagnostic codes (when Part 9 is active), diagnostic flags.

---

*This audit provides character architecture diagnosis. It verifies that characters are psychologically coherent, appropriately agentic, distinctively voiced, functionally distributed, and — when Part 9 is active — mechanically coupled to the story's moral argument through falsifiable diagnostic codes. The system diagnoses character mechanics; the author creates the characters.*

---

## Appendix A: Genre Tuning Packs

The core Character Architecture module is a chassis. For different genres, swap the weightings, thresholds, and specialized tracking layers. Load the appropriate tuning pack after calibrating to genre.

---

### A1. Sci-Fi Adventure / Action Thriller

**Core Adjustment:** Competence-forward characterization. Characters are defined more by what they can *do* than what they *feel*.

**AQ Threshold:**
- Protagonist: **AQ > 0.50** (higher than baseline)
- If AQ < 0.45 → FLAG: "Passive Action Hero"

**Additional Metric — SQ (Solution Quotient):**
```
SQ = Problems Solved by Character's Unique Skills / Total Problems Encountered

Threshold: SQ > 0.30 for protagonist
IF SQ < 0.20 → FLAG: "Competence Not Demonstrated"
```

**Genre-Specific Gate: Competence Display**
```
CHECK: Does protagonist solve at least one problem using skills established
       in Act I (not deus ex machina)?

IF yes → PASS
IF competence appears only when needed → FLAG: "Informed Competence"
```

**Genre-Specific Bug: Skill Inflation**
```
IF new skill appears in Act III without setup → FLAG: "Skill Inflation"
IF protagonist is "the best" at too many things → FLAG: "Mary Sue Vector"
```

**Specialized Tracking:**
- Skill Inventory (what can they do? when established?)
- Problem/Solution Match (does the right skill meet the right problem?)

**CQ/Stance Check:** Usually irrelevant. May apply if capture/interrogation scenes exist.

---

### A2. Kick-Ass Girl Detective / Cozy Mystery

**Core Adjustment:** Inference-forward characterization. The protagonist's value is intellectual, not physical.

**AQ Threshold:**
- Protagonist: **AQ > 0.45**
- High AQ expected, but many decisions are *investigative* (questioning, observing, connecting) rather than physical

**Additional Metric — IQ (Inference Quotient):**
```
IQ = Correct Deductions / Total Deductions Attempted

Threshold: IQ > 0.60 (protagonist should be mostly right)
IF IQ < 0.40 → FLAG: "Too Many Wrong Guesses"
IF IQ = 1.0 → FLAG: "Implausibly Perfect"
```

**Genre-Specific Gate: The Inference Chain**
```
CHECK: Can reader trace how protagonist got from clue to conclusion?

IF reasoning visible and fair → PASS
IF solution appears without traceable logic → FLAG: "Intuition Leap"
IF protagonist knew something reader couldn't → FLAG: "Unfair Information"
```

**Specialized Tracking — Inference Chain Map:**
```
| Clue | Scene Introduced | Scene Connected | Deduction Made |
|------|------------------|-----------------|----------------|
| Mud on boots | Ch 2 | Ch 7 | Victim was at the lake |
```

**Genre-Specific Bug: Accidental Solution**
```
IF mystery solved by luck rather than deduction → STRUCTURAL BREAK
IF protagonist stumbles on killer by chance → FLAG: "Accidental Detective"
```

**CQ/Stance Check:** Usually irrelevant unless the mystery involves coercion/abuse as subject matter.

---

### A3. Romantic Comedy

**Core Adjustment:** Dual-engine story. Both leads drive; neither can be passive.

**AQ Threshold:**
- **Both** leads: **AQ > 0.35**
- If either lead AQ < 0.30 → FLAG: "Passive Partner"
- Aggregate romantic AQ should balance (neither more than 60% of total romantic decisions)

**Additional Metric — VQ (Vulnerability Quotient):**
```
VQ = Vulnerable Admissions / Opportunities for Vulnerability

Threshold: VQ > 0.20 for each lead by Act III
IF VQ = 0 at climax → FLAG: "Armor Never Drops"
```

**Genre-Specific Gate: The Bid/Repair Rhythm**
```
CHECK: Does each romantic "bid" (offer of connection) get a response?

IF bid → repair OR bid → escalation → PASS
IF bid → ignore (repeatedly) → FLAG: "Unresponsive Partner"
IF only one partner makes bids → FLAG: "One-Sided Pursuit"
```

**Specialized Tracking — Bid/Repair Rhythm:**
```
| Scene | Who Bids | Bid Type | Response | Outcome |
|-------|----------|----------|----------|---------|
| Ch 3 | Lead A | Compliment | Deflected (insecurity) | Tension |
| Ch 5 | Lead B | Invitation | Accepted | Warm moment |
```

**Genre-Specific Bug: Conflict Bypass**
```
IF leads resolve differences without cost → FLAG: "Too Easy Resolution"
IF neither lead sacrifices anything for relationship → FLAG: "Costless HEA"
```

**CQ/Stance Check:** Usually irrelevant. May apply if one lead has power over the other (boss/employee, etc.).

---

### A4. Epic Fantasy

**Core Adjustment:** Moral-scale characterization. Characters often embody political or ethical positions at civilizational scale.

**AQ Threshold:**
- Protagonist: **AQ > 0.45**
- Note: Many scenes may be reactive (responding to war, prophecy, political crisis), but protagonist must still *choose* within constraints

**Additional Metric — MQ (Moral Quotient):**
```
MQ = Decisions with Ethical Weight / Total Major Decisions

Threshold: MQ > 0.30 for protagonist in "chosen one" or political narratives
IF MQ < 0.20 → FLAG: "Moral Disengagement"
```

**Genre-Specific Gate: Power Cost**
```
CHECK: Does the protagonist's power (magic, political, chosen-one) cost something?

IF power requires sacrifice, limitation, or moral burden → PASS
IF power is free and unlimited → FLAG: "Costless Power"
IF power corrupts or tempts → PASS (enhanced)
```

**Specialized Tracking — Power Cost Ledger:**
```
| Power Used | Scene | Cost Paid | Who Paid It |
|------------|-------|-----------|-------------|
| Fire spell | Ch 12 | Physical exhaustion | Protagonist |
| Prophecy knowledge | Ch 8 | Isolation from friends | Protagonist |
```

**Genre-Specific Bug: Prophecy Puppet**
```
IF protagonist merely fulfills prophecy without choosing → FLAG: "Prophecy Puppet"
IF prophecy interpretation requires active decision → PASS
```

**CQ/Stance Check:** May apply in:
- Slavery/bondage narratives
- Court intrigue with constrained choice
- "Chosen one" who cannot refuse the call

---

### A5. Horror (General)

**Core Adjustment:** Constraint-forward characterization. The horror often comes from narrowing options.

**AQ Threshold:**
- Protagonist: **AQ 0.25–0.35** (lower is acceptable)
- IF AQ < 0.25 AND CQ not rising → FLAG: "Passive Victim"
- IF AQ drops over arc AND CQ rises → PASS (genre-appropriate constraint)

**CQ Interpretation:**
- Rising CQ is **expected** in horror
- The question is whether constraint is *registered* by the text

**Genre-Specific Gate: Fear Manifestation**
```
CHECK: Does protagonist's FEAR (from Psychology Engine) get activated?

IF story forces contact with stated fear → PASS
IF fear is stated but never confronted → FLAG: "Untested Fear"
IF fear changes without explanation → FLAG: "Fear Drift"
```

**Genre-Specific Gate: Survival Logic**
```
CHECK: Do protagonist's survival decisions make sense given available information?

IF decisions reasonable with what character knows → PASS
IF protagonist makes obviously stupid choices → FLAG: "Idiot Plot"
IF protagonist makes smart choices and still loses → PASS (genre-appropriate)
```

**Specialized Bug: Horror Immunity**
```
IF protagonist seems unaffected by witnessed horror → FLAG: "Horror Immunity"
IF trauma response (freeze, flight, fawn, hypervigilance) absent → FLAG: "Unrealistic Resilience"
```

**CQ/Stance Check:** Critical if horror involves:
- Captivity
- Psychological manipulation
- Gaslighting
- Coerced intimacy

Apply full Stance Check (anti-exploitation gate) for these elements.

---

### Using Tuning Packs

1. **Load base Character Architecture module**
2. **Identify primary genre** during intake
3. **Load corresponding tuning pack** (may load multiple for genre hybrids)
4. **Adjust thresholds** as specified
5. **Add specialized tracking** columns to relevant tables
6. **Run additional genre-specific gates** during analysis
7. **Flag genre-specific bugs** in diagnostic output

**For hybrid genres:** Load multiple packs. When thresholds conflict, use the higher threshold (more demanding). When tracking requirements overlap, combine columns. Note genre tensions in synthesis.

---

*Genre Tuning Packs v1.0 — Accompanies Character Architecture Audit v0.4.4*
