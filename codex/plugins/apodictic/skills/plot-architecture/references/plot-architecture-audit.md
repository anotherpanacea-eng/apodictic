# Specialized Audit: Plot Architecture & Spines
## Version 0.5.0
*Last Updated: March 2026*

---

## Purpose

This audit calibrates Pass 2 (Structural Mapping) and Pass 6 (Scene Function) by identifying the manuscript's **primary spine** and **secondary engines**, then applying spine-specific logic gates to detect structural failures.

**Core principle:** Plot structures are tools, not rules. The audit identifies which tool the manuscript is using and checks whether it's using that tool correctly.

---

## How to Use This Audit

**Step 1: Identify Primary Spine**
During intake, determine which macro-structure governs the manuscript. Most works have ONE primary spine.

**Step 2: Identify Secondary Engines (Optional)**
Some manuscripts layer multiple engines. A thriller might use Fichtean Curve (primary) with Conspiracy (secondary) and Countdown (tertiary).

**Step 3: Apply Logic Gates**
Run the specific detection protocols for the identified spine(s). Each gate produces one of three results:
- **PASS** — Structure functioning as intended
- **FLAG FOR REVIEW** — Potential issue; verify with author intent
- **STRUCTURAL BREAK** — Clear failure of the spine's core mechanism

**Step 4: Cross-Reference with Genre**
Some structural "failures" are features in certain genres. Check genre module before flagging.

---

## Severity Levels

| Level | Meaning | Action |
|-------|---------|--------|
| **STRUCTURAL BREAK** | The spine's core mechanism is non-functional | Must-fix; book doesn't work without addressing |
| **FLAG FOR REVIEW** | Potential issue or intentional subversion | Ask author; may be deliberate |
| **SOFT FLAG** | Minor deviation; may not matter | Note in synthesis; low priority |

---

## Family 1: Linear & Teleological Spines

Structures that move forward toward a definitive end.

### 1. Save the Cat / Beat Sheet

**Best for:** Commercial clarity, speed, readability, "I always know where I am."
**Breaks when:** Work wants ambiguity, recursion, or moral fog.
**On the page:** Clean inciting incident, midpoint flip, late "all is lost," decisive finale.

**Logic Gate: The Midpoint Pivot**
```
CHECK: Does protagonist's stance shift from REACTIVE to PROACTIVE
       between 45-55% of word count?

IF shift occurs at 45-55% → PASS
IF shift occurs at 35-45% or 55-65% → SOFT FLAG: "Early/Late Midpoint"
IF no shift occurs → FLAG FOR REVIEW: "Passive Midpoint"
IF protagonist proactive from start → N/A (different spine)
```

**Logic Gate: The "All Is Lost" Beat**
```
CHECK: Is there a distinct low point between 70-85% where victory
       seems impossible?

IF present at 70-85% → PASS
IF present but too early (<70%) → FLAG: "All Is Lost Too Early — no room to recover"
IF absent entirely → FLAG FOR REVIEW: "Missing Dark Night"
```

**Genre Cross-Reference:**
- Literary Fiction: Midpoint pivot optional; flag only if pacing drags
- Thriller: Midpoint pivot essential; STRUCTURAL BREAK if missing

---

### 2. Three-Act Structure

**Best for:** Everything; it's scaffolding, not a method.
**Breaks when:** You mistake it for guidance.
**On the page:** Act I = problem + lock-in (20-30%); Act II = escalation (40-60%); Act III = reckoning (20-30%).

**Logic Gate: Proportional Balance**
```
CHECK: Word count distribution across acts

Act I: 20-30% → PASS | <15% → "Rushed Setup" | >35% → "Delayed Lock-In"
Act II: 40-60% → PASS | <35% → "Thin Middle" | >65% → "Bloated Middle"
Act III: 15-30% → PASS | <10% → "Rushed Resolution" | >35% → "Extended Ending"
```

**Logic Gate: Lock-In Moment**
```
CHECK: Is there a point of no return at Act I/II boundary?

IF protagonist cannot return to status quo after this point → PASS
IF protagonist could walk away but chooses not to → SOFT FLAG (may be intentional)
IF no lock-in identifiable → FLAG FOR REVIEW: "Missing Commitment"
```

> **Cross-reference:** For a non-conflict-driven alternative to three-act structure, see **Kishōtenketsu** (Spine 6, below). If the manuscript resists conflict-based diagnostics but clearly "works," check for Kishōtenketsu before flagging structural failures.

---

### 3. Fichtean Curve (Crisis Staircase)

**Best for:** Thriller, horror, dread escalation, "no air" pacing.
**Breaks when:** Characters never metabolize events.
**On the page:** Short recovery beats between increasingly sharp turns.

**Logic Gate: The Recovery Ratio**
```
CHECK: Measure word count of "sequel" scenes (emotional processing)
       between crisis peaks. Ratio should DECREASE as book progresses.

Act I recovery scenes: X words average
Act II recovery scenes: Should be < X
Act III recovery scenes: Should be << X

IF ratio decreases → PASS
IF ratio stays constant → SOFT FLAG: "Pacing Plateau"
IF ratio INCREASES in Act III → FLAG: "Pacing Drag — recovery lengthening when tension should peak"
```

**Logic Gate: The Metabolization Check**
```
CHECK: After each crisis, does character's state change?

IF crisis produces visible psychological/strategic shift → PASS
IF crisis occurs but character unchanged → FLAG: "Unmetabolized Crisis"
IF 3+ unmetabolized crises → STRUCTURAL BREAK: "Crisis Fatigue"
```

---

### 4. Freytag Pyramid (Classical Tragedy)

**Best for:** Doom arcs, moral fall, "this was always coming."
**Breaks when:** Rising action peaks too early; falling action drags.
**On the page:** Rising pressure → peak → consequences cascade.

**Logic Gate: The Peak Placement**
```
CHECK: Where does the climactic moment occur?

IF peak at 65-80% with meaningful falling action → PASS
IF peak at 85-95% with minimal falling action → SOFT FLAG (may be intentional thriller pacing)
IF peak before 50% → FLAG: "Premature Climax — second half is aftermath without momentum"
```

**Logic Gate: The Inevitability Seed**
```
CHECK: In retrospect, was the tragic outcome foreseeable from Act I?

IF seeds planted that make ending feel "inevitable" → PASS
IF ending feels arbitrary/unlucky → FLAG: "Fate Without Foreshadowing"
```

---

### 5. Story Circle / Hero's Journey

**Best for:** Character-driven transformation, empowerment, corruption, or compromise.
**Breaks when:** External journey overshadows internal; protagonist lacks agency.
**On the page:** Need pulls them out; return costs them something.

**Logic Gate: The Transformation Evidence**
```
CHECK: Compare protagonist at 10% vs 90%. Is change visible in:
       - Decisions made?
       - Language/voice?
       - Relationships?
       - Values hierarchy?

IF 3+ categories show change → PASS
IF 1-2 categories show change → SOFT FLAG: "Shallow Transformation"
IF no visible change → STRUCTURAL BREAK: "Static Protagonist"
```

**Logic Gate: The Return Cost**
```
CHECK: Does returning to the "ordinary world" require sacrifice?

IF protagonist loses something to gain transformation → PASS
IF protagonist gains everything with no loss → FLAG: "Costless Victory"
IF protagonist cannot return (permanent exile) → Check if intentional
```

---

### 6. Kishōtenketsu (Four-Part Without Conflict)

**Origin:** Japanese (起承転結), with structural cognates in Chinese (Qǐ Chéng Zhuǎn Hé / 起承转合) and Korean (Gi Seung Jeon Gyeol / 기승전결). One template; three cultural lineages. The Japanese term is standard in English-language craft discourse; there is no established anglicization.

**Best for:** Juxtaposition as argument, slice-of-life, lyric fiction, stories where meaning emerges from contrast rather than collision.
**Breaks when:** The ten doesn't actually recontextualize; when it collapses into Western conflict by accident.
**On the page:** Introduction (Ki/起: bringing into being) → Development (Shō/承: continuing, receiving) → Turn (Ten/転: turning, changing) → Reconciliation (Ketsu/結: gathering, drawing together). No antagonist required. No crisis required. The third movement places two things side by side and the fourth movement lets the reader sit with what that juxtaposition means.

> ⚠ **TRANSLATION NOTE ON TEN:** The third movement is variously translated as "twist," "turn," or "change." These are not synonyms, and the translation chosen will affect how the logic gates below are applied. "Twist" suggests a Shyamalan-style plot reversal, which is misleading. "Turn" is more accurate: a shift in direction, perspective, or context that does not require surprise or deception. "Change" captures the broadest range but risks being too vague. For diagnostic purposes, APODICTIC treats *ten* as **juxtaposition**: the introduction of an element that does not follow causally from what precedes it and whose placement beside the earlier material generates new meaning. If the manuscript's third movement operates through surprise, check whether the spine has drifted toward Revelatory Plot. If it operates through conflict escalation, check whether the spine has drifted toward Three-Act Structure.

> ⚠ **CRITICAL CALIBRATION NOTE:** APODICTIC's conflict-driven diagnostics (particularly Save the Cat, Fichtean Curve, and Three-Act lock-in gates) will produce false positives on well-executed Kishōtenketsu manuscripts. If this spine is identified, **suppress the following default flags:**
> * "Passive Midpoint" (there is no reactive-to-proactive shift; that's not the engine)
> * "Missing Commitment" (there is no lock-in; the structure doesn't require one)
> * "Crisis Fatigue" or "Unmetabolized Crisis" (there may be no crisis to metabolize)
>
> Run Kishōtenketsu-specific gates instead.

**Logic Gate: The Juxtaposition Test**
```
CHECK: Does the third movement (Ten) introduce an element that is
       GENUINELY UNEXPECTED relative to movements one and two?

IF Ten introduces a new perspective, image, or situation that
   doesn't follow causally from Ki/Shō → PASS
IF Ten escalates the existing situation (conflict in disguise) →
   FLAG: "Kishōtenketsu Collapse — this is three-act structure
   with different labels"
IF Ten is merely a continuation of Shō → STRUCTURAL BREAK:
   "Missing Turn — no juxtaposition present"
IF Ten operates through surprise/deception rather than
   juxtaposition → FLAG FOR REVIEW: "Revelatory Ten — verify
   intended spine (may be Revelatory Plot)"
```

**Logic Gate: The Reconciliation Weight**
```
CHECK: Does the fourth movement (Ketsu) produce meaning FROM the
       juxtaposition, rather than resolving a problem?

IF Ketsu reframes Ki/Shō in light of Ten → PASS
IF Ketsu resolves a conflict introduced in Ten → FLAG:
   "Conflict Resolution Ending — structure has drifted to
   Western three-act"
IF Ketsu simply restates Ki → FLAG: "Empty Return — no
   semantic gain from the turn"
```

**Logic Gate: The Development Integrity**
```
CHECK: Does the second movement (Shō) deepen without disrupting?

IF Shō elaborates, enriches, or extends Ki without introducing
   antagonism → PASS
IF Shō introduces an obstacle or antagonist → SOFT FLAG:
   "Conflict Creep — verify intended spine"
   (If flagged, run Three-Act lock-in test. If lock-in present,
   reclassify. If absent, recommend revision to remove
   antagonism from Shō.)
IF Shō is static (pure repetition of Ki) → FLAG:
   "Stalled Development"
```

**Genre Cross-Reference:**
- Literary Fiction: Native habitat; juxtaposition can be subtle
- Manga/Comics: Often used at chapter level even within larger conflict arcs
- Slice-of-Life: Primary structural engine; troughs of "nothing happens" are features
- Horror: Ten as wrongness rather than conflict can produce distinctive unease (see Junji Ito). Distinct from Lullaby: Lullaby establishes comfort then ruptures it; Kishōtenketsu places wrongness *beside* normalcy without rupturing anything. Route accordingly.

---

## Family 2: Circular & Recursive Engines

Structures that repeat to deepen meaning or trap the character.

### 7. Spiral Plot (The Addiction)

**Best for:** Compulsion, coercive control, relapse, "tightening circle."
**Breaks when:** Readers feel stalled rather than trapped.
**On the page:** Same problem returns, but protagonist has fewer resources.

**Logic Gate: The Resource Drain**
```
CHECK: Compare Loop N to Loop N+1. Does protagonist have LESS of:
       - Dignity?
       - Privacy?
       - Agency?
       - Sanity?
       - External support?

IF at least one resource diminishes per loop → PASS
IF resources stay constant → FLAG: "Stalled Loop — repetition without cost"
IF resources INCREASE → Check if intentional (recovery arc)
```

**Logic Gate: The Variation Requirement**
```
CHECK: Does each return to the problem differ in approach or stakes?

IF same trigger + same response + same outcome → STRUCTURAL BREAK: "Identical Loop"
IF same trigger + different response → PASS
IF different trigger + escalated stakes → PASS
```

---

### 8. Fugue / Refrain Structure

**Best for:** Conditioning, ritual, obsession, "the body repeats a sentence."
**Breaks when:** Repetition doesn't accumulate meaning.
**On the page:** Same scene template with shifting interiority/context.

**Logic Gate: The Contextual Shift**
```
CHECK: When the refrain repeats, does reader understanding INVERT?

Example: What looked like Care in Ch. 1 looks like Capture in Ch. 10

IF meaning shifts/deepens with each repetition → PASS
IF meaning stays identical → FLAG: "Dead Repetition — no semantic payload"
IF meaning becomes LESS clear → Check if intentional (ambiguity as theme)
```

**Logic Gate: The Interiority Drift**
```
CHECK: Does POV character's internal experience of the refrain change?

IF interiority shows progression (comfort→unease→dread OR resistance→acceptance) → PASS
IF interiority static across repetitions → FLAG: "Frozen Interiority"
```

---

### 9. Loop / Groundhog Structure

**Best for:** Inevitability, learning protocols, time loops, behavioral repetition.
**Breaks when:** Loops don't produce learning or variation.
**On the page:** Same day/scene; new layer; tighter trap.

**Logic Gate: The Variance Threshold**
```
CHECK: Does protagonist attempt a DIFFERENT strategy in each loop?

IF new strategy each iteration → PASS
IF same strategy repeated 2x → SOFT FLAG
IF same strategy repeated 3+ times → STRUCTURAL BREAK: "Insanity Loop — same action expecting different results"
```

**Logic Gate: The Information Accumulation**
```
CHECK: Does protagonist carry knowledge across loops?

IF learning accumulates → PASS
IF each loop resets knowledge → Check if intentional (horror of forgetting)
IF knowledge accumulates but isn't applied → FLAG: "Unused Learning"
```

---

### 10. Braided Narrative

**Best for:** Past/present, dual POV, victim/perpetrator, double life.
**Breaks when:** One braid is obviously "less good" or strands never connect.
**On the page:** Alternating strands that collide into a reveal.

**Logic Gate: The Convergence Rate**
```
CHECK: Do the strands get CLOSER (in time, space, theme) as book progresses?

IF convergence visible by Act III → PASS
IF strands remain parallel throughout → FLAG: "Parallel Lines — strands don't affect each other"
IF strands converge too early (Act I) → FLAG: "Premature Collision"
```

**Logic Gate: The Balance Check**
```
CHECK: Word count distribution between strands

IF strands within 60/40 ratio → PASS
IF one strand <30% of total → FLAG FOR REVIEW: "Subordinate Strand — is this intentional?"
IF one strand shows lower craft quality → FLAG: "Uneven Braids"
```

**Logic Gate: The Resonance Test**
```
CHECK: Do strands illuminate each other thematically?

IF reading Strand A changes understanding of Strand B → PASS
IF strands could be separate novels → FLAG: "Unintegrated Braids"
```

---

## Family 3: Information & Knowledge Spines

Structures based on who knows what, and when.

### 11. Mystery / Investigation Spine

**Best for:** Whodunits, audits, institutional secrecy, clinical trials.
**Breaks when:** Explanation relieves dread instead of deepening it.
**On the page:** Question → clue → reversal → reveal → (new terror).

**Logic Gate: The Information Economy**
```
CHECK: Does every scene provide a clue that EXCLUDES a possibility?

IF each scene narrows solution space → PASS
IF scenes add information without narrowing → FLAG: "Data Noise"
IF solution space expands in Act III → Check if intentional (conspiracy revelation)
```

**Logic Gate: The Fair Play Test**
```
CHECK: Is the solution deducible from available evidence?

IF reader could solve before reveal (with effort) → PASS
IF solution requires information withheld from reader → FLAG: "Unfair Mystery"
IF solution requires information withheld from POV character → Check narration type
```

---

### 12. "Howcatchem" (Columbo Structure)

**Best for:** Moral disgust, watching denial operate, procedural.
**Breaks when:** No escalating leverage or pressure.
**On the page:** Reader knows who/what; tension is how and why.

**Logic Gate: The Pressure Escalation**
```
CHECK: Does investigator's leverage over perpetrator increase scene by scene?

IF leverage accumulates → PASS
IF leverage stays constant → FLAG: "Static Investigation"
IF perpetrator's position strengthens → Check if intentional (institutional protection)
```

---

### 13. Revelatory Plot (Recontextualization)

**Best for:** "I thought it was care; it was capture." Every scene becomes evidence.
**Breaks when:** Twist is merely clever, not ethically reorienting.
**On the page:** Post-reveal, earlier scenes mean something different.

**Logic Gate: The Reread Test**
```
CHECK: After the reveal, would rereading Act I produce different emotional experience?

IF meaning fundamentally shifts → PASS
IF meaning stays same (just adds information) → FLAG: "Twist Without Recontextualization"
IF earlier scenes become nonsensical post-reveal → STRUCTURAL BREAK: "Retcon Violation"
```

**Logic Gate: The Ethical Weight**
```
CHECK: Does the reveal change the MORAL landscape, not just facts?

IF "who was good/bad" shifts → PASS
IF only "what happened" shifts → SOFT FLAG: "Factual vs Ethical Twist"
```

---

### 14. Conspiracy Plot

**Best for:** Institutions, medicine, academia, compliance culture.
**Breaks when:** It becomes vague handwaving ("they" did it).
**On the page:** Escalating scope; every contact is compromised.

**Logic Gate: The Specificity Requirement**
```
CHECK: Is the conspiracy NAMED and MECHANIZED?

IF specific actors with specific motives identifiable → PASS
IF "the system" or "they" without specification → FLAG: "Vague Conspiracy"
IF mechanism of conspiracy explained → PASS
IF conspiracy operates by unexplained magic → FLAG: "Handwave Horror"
```

**Logic Gate: The Scope Escalation**
```
CHECK: Does conspiracy reveal expand from personal → institutional → systemic?

IF scope expands through acts → PASS
IF scope revealed all at once → SOFT FLAG: "Flat Revelation"
IF scope contracts (was bigger than thought) → Check if intentional (paranoia theme)
```

---

### 15. Puzzle Box

**Best for:** Mechanism horror, metaphysical systems, constraints as antagonist.
**Breaks when:** Rules inconsistent or introduced too late.
**On the page:** Each scene teaches rules by hurting someone.

**Logic Gate: The Consistency Check**
```
CHECK: Are rules established in Act I obeyed in Act III?

IF all rules consistent → PASS
IF rule broken without explanation → STRUCTURAL BREAK: "Rule Violation"
IF rule "reinterpreted" at climax → FLAG FOR REVIEW: "Possible Cheat"
```

**Logic Gate: The Late Introduction Flag**
```
CHECK: When is the last NEW rule introduced?

IF no new rules in final 15% → PASS
IF new rule introduced in final 15% that SOLVES problem → STRUCTURAL BREAK: "Deus Ex Machina"
IF new rule introduced in final 15% that CREATES problem → PASS (acceptable escalation)
```

---

## Family 4: Relationship & Erotic Engines

Structures driven by interpersonal dynamics.

### 16. Courtship Plot

**Best for:** Romance, dark romance, "consent as evolving contract."
**Breaks when:** Chemistry replaces agency.
**On the page:** Escalating intimacy beats; stakes become relational.

**Logic Gate: The Intimacy/Risk Correlation**
```
CHECK: For every increase in Intimacy, is there corresponding increase in Risk?

IF intimacy ↑ AND risk ↑ → PASS
IF intimacy ↑ AND risk static → FLAG: "Safe Sex — stakes not scaling"
IF intimacy ↑ AND risk ↓ → FLAG: "Tension Collapse"
```

*Cross-reference: See Romance/Erotic Module for detailed intimacy tracking.*

---

### 17. Seduction Plot

**Best for:** Erotic horror, manipulation, power exchange.
**Breaks when:** "Seduction" reads as endorsement rather than examination.
**On the page:** Attention narrows; choices become smaller and heavier.

**Logic Gate: The Narrowing Funnel**
```
CHECK: Does protagonist's decision space CONTRACT through the seduction?

IF options diminish scene by scene → PASS
IF options stay constant → FLAG: "Static Seduction"
IF protagonist retains full agency throughout → Check if intentional (subversion)
```

**Logic Gate: The Complicity Mechanism**
```
CHECK: Does seduction implicate protagonist in their own capture?

IF protagonist makes choices that enable seduction → PASS (darker, more effective)
IF seduction is purely external force → SOFT FLAG: "Passive Target"
```

---

### 18. Captivity Plot

**Best for:** Bodily autonomy horror, institutional containment.
**Breaks when:** Confinement removes all interesting choice.
**On the page:** Micro-choices; compliance as survival; small rebellions.

**Logic Gate: The Micro-Agency Check**
```
CHECK: As EXTERNAL freedom vanishes, does INTERNAL choice become more granular?

IF physical constraint ↑ AND psychological choice complexity ↑ → PASS
IF physical constraint ↑ AND all choice vanishes → STRUCTURAL BREAK: "Total Victimhood"
IF protagonist retains external options → Not a captivity plot
```

---

### 19. Taming/Training Plot

**Best for:** Conditioning themes, protocol, ritualized control.
**Breaks when:** It's only kink choreography without ethical inquiry.
**On the page:** Repeated exercises; body "learns" faster than mind.

**Logic Gate: The Rule Evolution**
```
CHECK: Does "protocol" shift from Constraint (forced) to Language (expression)?

IF protagonist begins resisting, ends using protocol for own purposes → PASS
IF protocol remains purely external imposition → FLAG: "Static Training"
IF protagonist's identity merges with protocol → Check if intentional (horror of conditioning)
```

**Logic Gate: The Body-Mind Lag**
```
CHECK: Does physical compliance precede psychological acceptance?

IF body responds before mind consents → PASS (the horror is working)
IF mind and body align immediately → SOFT FLAG: "Missing Conditioning Dread"
```

---

### 20. Betrayal of Self Plot

**Best for:** Arousal as alienation, desire as evidence against you.
**Breaks when:** Character reasoning and shame loops aren't anchored.
**On the page:** Response precedes intent; meaning lags; dread fills the gap.

**Logic Gate: The Interiority Anchor**
```
CHECK: Is the protagonist's reasoning about their own responses visible?

IF internal logic of shame/confusion/rationalization shown → PASS
IF only behavior shown without interiority → FLAG: "Missing Self-Observation"
IF protagonist has no reaction to self-betrayal → STRUCTURAL BREAK: "Absent Dread"
```

---

## Family 5: Moral & Social Engines

Structures driven by ethical stakes.

### 21. Corruption Arc

**Best for:** Villain origins, "I'm not harming anyone," self-justification.
**Breaks when:** Fall is too fast or too vague.
**On the page:** Small rationalizations that later read as monstrous.

**Logic Gate: The Rationalization Index**
```
CHECK: Compare excuses in Act I vs Act III.

IF excuses weaken while crimes enlarge → PASS
IF crimes enlarge suddenly without rationalization → FLAG: "Sudden Monster"
IF rationalizations stay constant → FLAG: "Static Justification"
```

**Logic Gate: The Step Count**
```
CHECK: How many distinct moral compromises between "good person" and "monster"?

IF 4+ identifiable steps → PASS
IF 2-3 steps → SOFT FLAG: "Compressed Corruption"
IF 1 step (good → evil) → STRUCTURAL BREAK: "Missing Gradation"
```

---

### 22. Redemption Arc

**Best for:** Chosen endings, repair that costs something.
**Breaks when:** Redemption is unearned or consequence-free.
**On the page:** Apology + restitution + loss; moral accounting.

**Logic Gate: The Cost Requirement**
```
CHECK: Does redemption cost the character something they value?

IF redemption requires sacrifice visible to reader → PASS
IF redemption is forgiveness without cost → FLAG: "Cheap Grace"
IF redemption restores status quo ante → FLAG: "Consequence-Free Repair"
```

**Logic Gate: The Restitution Test**
```
CHECK: Does character attempt to repair harm done, not just apologize?

IF action toward repair shown → PASS
IF only verbal apology → SOFT FLAG: "Words Without Action"
IF harm is to someone dead/gone (repair impossible) → Check for symbolic restitution
```

---

### 23. Justice/Revenge Plot

**Best for:** Catharsis, reader satisfaction, rage transmutation.
**Breaks when:** Revenge eclipses earlier ethical complexity.
**On the page:** Preparation → confrontation → payoff → aftermath cost.

**Logic Gate: The Aftermath Requirement**
```
CHECK: Does revenge have COST for the avenger?

IF revenge exacts psychological/moral/practical price → PASS
IF revenge is purely triumphant → FLAG FOR REVIEW: "Costless Revenge"
IF revenge makes avenger worse than target → Check if intentional
```

---

### 24. Scapegoat Plot

**Best for:** Social horror, witch trials, cancel culture, "The Lottery."
**Breaks when:** Mob portrayed as "evil" rather than fearful/rational-within-their-logic.
**On the page:** Community harmony → threat → suspicion → selection → expulsion.

**Logic Gate: The Complicity Check**
```
CHECK: Is protagonist initially PART of the mob/system before becoming target?

IF protagonist participates in earlier scapegoating → PASS (implicates reader)
IF protagonist is outsider from start → SOFT FLAG: "External Victim"
```

**Logic Gate: The Logic Visibility**
```
CHECK: Is the mob's reasoning visible (even if wrong)?

IF reader can understand why community is afraid → PASS
IF mob is simply "evil" → FLAG: "Cartoon Antagonist"
```

---

## Family 6: Constraint & Environment Engines

Structures defined by space, time, or rules.

### 25. Siege Plot

**Best for:** Party scenes, office, clinic, retreat, enclosed space.
**Breaks when:** Enclosure feels contrived; exits should have closed naturally.
**On the page:** Exits close; social rules become bars.

**Logic Gate: The Exit Closure Sequence**
```
CHECK: Do exits close for NARRATIVE reasons (not just because)?

IF each exit closes due to character action or revealed information → PASS
IF exits close arbitrarily → FLAG: "Contrived Containment"
```

---

### 26. Countdown Plot

**Best for:** Medical trials, expiring consent, tenure clocks, pregnancy.
**Breaks when:** Deadline is arbitrary or stakes unclear.
**On the page:** Time markers; narrowing options.

**Logic Gate: The Stakes Visibility**
```
CHECK: Is it clear what happens when countdown reaches zero?

IF consequences of failure are concrete → PASS
IF consequences are vague ("something bad") → FLAG: "Abstract Deadline"
```

**Logic Gate: The Pressure Curve**
```
CHECK: Does time pressure INCREASE as deadline approaches?

IF chapters shorten OR scene urgency increases near deadline → PASS
IF pacing stays constant → FLAG: "Deadline Without Tension"
```

---

### 27. Procedural Plot

**Best for:** Institutional horror, clinical settings, audits, compliance.
**Breaks when:** Procedure becomes exposition rather than trap.
**On the page:** Forms, checklists, meetings—each a mechanism of control.

**Logic Gate: The Procedure-As-Trap Test**
```
CHECK: Does following procedure make things WORSE for protagonist?

IF compliance leads to deeper entrapment → PASS
IF procedure is neutral backdrop → FLAG: "Decorative Procedure"
IF breaking procedure offers escape → Check if intentional
```

---

### 28. Quest Plot

**Best for:** "Get the data," "find the source," "secure the antidote."
**Breaks when:** Stations don't change the protagonist internally.
**On the page:** Each stop extracts a price; arrival is not the same person who departed.

**Logic Gate: The Station Cost**
```
CHECK: Does each quest station extract something from protagonist?

IF 75%+ of stations have visible cost → PASS
IF stations are just geography → FLAG: "Decorative Journey"
```

---

## Family 7: Time & Causality Engines

Structures that manipulate temporal or causal sequence.

### 29. Nonlinear Reveal

**Best for:** Trauma, memory, gaslighting structures.
**Breaks when:** It's just gimmickry without payoff.
**On the page:** Later scenes "explain" earlier ones; dread accrues retroactively.

**Logic Gate: The Retroactive Meaning**
```
CHECK: Does out-of-order presentation CREATE meaning it wouldn't have linearly?

IF nonlinearity produces dramatic irony or retroactive dread → PASS
IF story would work equally well told linearly → FLAG: "Decorative Nonlinearity"
```

---

### 30. Reverse Chronology

**Best for:** Tragedy where "how" matters more than "what," debunking fate.
**Breaks when:** Reveal doesn't recontextualize opening.
**On the page:** Effect (horror) → cause → deep cause → initial choice.

**Logic Gate: The Kuleshov Reversal**
```
CHECK: Does the final scene (chronologically first) invert meaning of opening scene (chronologically last)?

IF meaning fundamentally shifts → PASS
IF scenes are just "earlier versions" → FLAG: "Chronology Without Revelation"
```

---

### 31. Two-Handed Causality

**Best for:** Romantic collision, predator/prey ambiguity, mutual conditioning.
**Breaks when:** One hand is clearly the "real" story.
**On the page:** Alternating agency; mutual escalation.

**Logic Gate: The Agency Balance**
```
CHECK: Do both protagonists CAUSE events that affect the other?

IF causation flows both directions → PASS
IF one character is primarily acted-upon → FLAG: "Unbalanced Hands"
```

---

## Family 8: Existential & Identity Engines

### 32. Bildungsroman (Coming-of-Age)

**Best for:** Identity formation, awakening, threshold crossing.
**Breaks when:** External events substitute for internal development.
**On the page:** Protagonist's worldview visibly transforms; innocence lost cannot be recovered.

**Logic Gate: The Worldview Shift**
```
CHECK: Compare protagonist's stated beliefs/assumptions at 10% vs 90%.

IF core beliefs have changed → PASS
IF only circumstances have changed → FLAG: "External Coming-of-Age"
IF beliefs unchanged despite events → STRUCTURAL BREAK: "Static Identity"
```

---

### 33. Doppelgänger / Replacement Plot

**Best for:** Imposter syndrome, Stepford themes, obsolescence fear.
**Breaks when:** Double is just a "monster" rather than dark mirror.
**On the page:** Encounter → mimicry → displacement → reclaiming or acceptance.

**Logic Gate: The Envy Check**
```
CHECK: Does protagonist secretly admire or desire the double's life?

IF ambivalence toward double visible → PASS
IF double is purely threatening → SOFT FLAG: "External Monster Only"
```

---

### 34. Transformation / Metamorphosis

**Best for:** Body horror, identity dissolution, becoming-other.
**Breaks when:** Transformation is just special effect, not psychological.
**On the page:** The change IS the plot; identity questions are central.

**Logic Gate: The Identity Question**
```
CHECK: Does transformation raise "Am I still me?" explicitly or implicitly?

IF identity continuity is questioned → PASS
IF transformation is purely physical → FLAG: "Metamorphosis Without Philosophy"
```

---

### 35. Aftermath / Postmortem Plot

**Best for:** Trauma processing, investigation of self, "the horror already happened."
**Breaks when:** Present tense has no stakes of its own.
**On the page:** Story begins after the main event; present investigates past.

**Logic Gate: The Present Stakes**
```
CHECK: Does discovering/processing the past create NEW risk in present?

IF investigation has present-tense consequences → PASS
IF present is just framing device → FLAG: "Stakes-Free Frame"
```

---

### 36. Prophecy / Inevitability Engine

**Best for:** Greek tragedy, "I tried to prevent it and caused it."
**Breaks when:** Foreknowledge doesn't create irony.
**On the page:** The ending is known; the journey is how we get there.

**Logic Gate: The Irony Requirement**
```
CHECK: Does protagonist's attempt to avoid fate CAUSE fate?

IF prevention causes fulfillment → PASS (classic tragic irony)
IF fate simply happens despite prevention → SOFT FLAG: "Passive Fate"
IF foreknowledge has no effect on action → FLAG: "Decorative Prophecy"
```

---

## Family 9: Tonal & Hybrid Spines

### 37. Thriller Spine

**Best for:** Momentum, danger, narrow escapes.
**Breaks when:** Interiority is replaced by plot jogging.
**On the page:** Active danger + constant decisions.

**Logic Gate: The Decision Density**
```
CHECK: Does protagonist make consequential decisions at least every 2-3 scenes?

IF decisions frequent and consequential → PASS
IF protagonist is carried by events → FLAG: "Passive Thriller Protagonist"
```

---

### 38. Psychological Horror Spine

**Best for:** Gaslighting, self-betrayal, desire-as-alien.
**Breaks when:** Ambiguity becomes confusion.
**On the page:** Competing interpretations; reader can't settle.

**Logic Gate: The Competing Interpretations Test**
```
CHECK: Can reader construct at least TWO coherent explanations for events?

IF multiple interpretations viable → PASS
IF only one interpretation possible → Not psychological horror
IF no interpretation coherent → STRUCTURAL BREAK: "Confusion, Not Ambiguity"
```

---

### 39. Faustian Spine

**Best for:** "Be careful what you wish for," erotic horror.
**Breaks when:** Price is arbitrary rather than ironic.
**On the page:** Desire → offer → price → regret → doom (or loophole).

**Logic Gate: The Monkey's Paw**
```
CHECK: Does fulfillment of wish DIRECTLY cause protagonist's undoing?

IF wish-fulfillment creates the problem → PASS
IF wish-fulfillment and problem are unrelated → FLAG: "Arbitrary Price"
```

---

### 40. Rashomon Spine

**Best for:** Gaslighting, memory ambiguity, perspective as theme.
**Breaks when:** Contradictions are merely factual, not meaningful.
**On the page:** Same event, different truths.

**Logic Gate: The Truth Gap**
```
CHECK: Are contradictions between accounts MEANINGFUL (revealing bias) or just FACTUAL (errors)?

IF contradictions reveal character psychology → PASS
IF contradictions are just inconsistencies → FLAG: "Accidental Rashomon"
```

---

## Family 10: Rhythm & Intensity Engines

Structures governed by pacing pattern rather than plot logic.

### 41. Wave / Pulse Structure

**Best for:** Lyric fiction, psychological intensity, stories driven by emotional rhythm rather than plot.
**Breaks when:** Waves feel repetitive rather than escalating; reader can't distinguish one crest from the next.
**On the page:** Rising intensity → crest → retreat → higher intensity → crest → retreat → overwhelming final crest.

**Logic Gate: The Escalation Curve**
```
CHECK: Does each wave crest at HIGHER intensity than the previous?

IF intensity increases per wave → PASS
IF intensity stays constant → FLAG: "Flat Waves — repetition without escalation"
IF final wave is not the most intense → FLAG FOR REVIEW: "Anticlimax Wave"
```

**Logic Gate: The Trough Function**
```
CHECK: Do retreat/trough sections serve a purpose beyond rest?

IF troughs introduce new information or shift perspective → PASS
IF troughs are purely recovery → SOFT FLAG: "Decorative Troughs"
IF troughs are absent (nonstop intensity) → FLAG: "No Oscillation — this is Fichtean, not Wave"
```

**Genre Cross-Reference:**
- Literary Fiction: Wave structure is native; lower crests acceptable
- Horror: Final wave should dwarf earlier ones; troughs breed dread
- Erotica: Wave maps naturally to arousal cycle; each crest should change the relational equation

---

### 42. Lullaby Structure

**Best for:** Horror, kink, vulnerability narratives; stories where trust is weaponized.
**Breaks when:** Rhythm isn't established firmly enough for the rupture to land.
**On the page:** Soothing cadence → micro-dissonances → full rupture → attempt to re-establish comfort (succeeds or fails).

**Logic Gate: The Rhythm Establishment**
```
CHECK: Is a recognizable comfort pattern established before first disruption?

IF reader can identify the "lullaby" cadence by 25% → PASS
IF disruption occurs before rhythm is established → FLAG: "Premature Rupture"
IF no clear rhythmic pattern identifiable → N/A (different spine)
```

**Logic Gate: The Micro-Dissonance Sequence**
```
CHECK: Are there at least 2 small breaks in pattern before the major rupture?

IF micro-dissonances precede macro-rupture → PASS
IF major rupture comes without warning → SOFT FLAG: "Jump Scare vs. Dread"
IF micro-dissonances are too obvious → FLAG: "Telegraphed Rupture"
```

---

### 43. Pressure Cooker

**Best for:** Erotic horror, institutional containment, conditioning narratives, any story where constraint IS the engine.
**Breaks when:** Escalation plateaus; reader becomes numb to tightening.
**On the page:** Constraint introduced → tightened → tightened again → hope of escape removed → break or transcendence.

**Logic Gate: The Ratchet Test**
```
CHECK: Does each section introduce a NEW constraint or tighten an existing one?

IF constraint increases every 15-20% of word count → PASS
IF constraint holds steady for >25% of word count → FLAG: "Pressure Plateau"
IF constraint relaxes without narrative justification → FLAG: "Leaky Seal"
```

**Logic Gate: The Psychological Toll Visibility**
```
CHECK: Is the protagonist's internal response to constraint shown escalating?

IF psychological cost visible and increasing → PASS
IF protagonist adapts without visible cost → FLAG FOR REVIEW: "Invisible Erosion"
IF protagonist is unaffected → STRUCTURAL BREAK: "Constraint Without Consequence"
```

**Genre Cross-Reference:**
- Erotic Horror: Constraint should implicate desire; arousal as pressure gauge
- Thriller: External constraints dominate; internal toll can be subtler
- Literary: Constraint may be social/institutional rather than physical

---

### 44. Jo-ha-kyū (Rhythmic Acceleration)

**Origin:** Japanese aesthetic principle (序破急), originating in gagaku court music and codified for dramatic structure by the Noh playwright Zeami Motokiyo in the 14th/15th century. The Japanese term is standard in English-language discourse; there is no established anglicization. Literal character translations: Jo (序: preface, opening, opportunity), Ha (破: break, rip, tear), Kyū (急: urgent, sudden, rapid). The common gloss "beginning, middle, end" is actively misleading and should not be used. Applies at every scale: individual gesture, scene, act, whole work, and even the arrangement of works across a program.

**Best for:** Any manuscript where pacing feels flat or metronomic; works that need rhythmic shape independent of plot structure. Functions as a diagnostic overlay rather than a primary spine. Can be applied on top of any spine in this document.
**Breaks when:** Applied so rigidly that every scene follows the same acceleration pattern (monotony through predictability).
**On the page:** Deliberate, measured opening → increasing complexity and speed → rapid culmination that doesn't overstay.

> ⚠ **USAGE NOTE:** Jo-ha-kyū is not a plot structure. It does not replace spine identification. It is a pacing lens that can diagnose rhythmic problems within any identified spine. Apply it **after** primary spine identification, not instead of it.

> ⚠ **PROPORTION NOTE:** Traditional Jo-ha-kyū proportions are not equal thirds. In Noh, Jo is roughly one-fifth, Ha is three-fifths, and Kyū is one-fifth. The gates below use "phases" rather than "thirds" to avoid implying equal division. When diagnosing, identify where the rhythmic transitions occur rather than imposing a mechanical split.

**Logic Gate: The Macro Rhythm**
```
CHECK: Does the whole manuscript follow Jo-ha-kyū pacing?

IDENTIFY the three phases by rhythmic transition, not equal division.

Jo phase: Measured pacing? Scenes establish rhythm?
  IF deliberate, unhurried opening → PASS
  IF opening rushes → FLAG: "Missing Jo — no rhythmic grounding"

Ha phase: Does pace increase? Do complications multiply?
  IF pacing accelerates and texture thickens → PASS
  IF pacing stays constant from Jo phase → FLAG:
     "Missing Ha — no rhythmic breaking"
  IF pacing SLOWS from Jo phase → FLAG:
     "Inverted Rhythm — drag where acceleration expected"

Kyū phase: Does the work accelerate to conclusion
           without lingering?
  IF final movement is fastest → PASS
  IF final movement decelerates → FLAG FOR REVIEW:
     "Extended Kyū — check if intentional
     (denouement vs. drag)"
  IF final movement matches Ha pacing → SOFT FLAG:
     "Flat Finish — no final acceleration"
```

**Logic Gate: The Scene-Level Rhythm**
```
CHECK: Do individual scenes follow internal Jo-ha-kyū?

SAMPLE 5 scenes: 1 from Jo phase, 2 from Ha phase, 1 from
Kyū phase, 1 from a phase transition point.

IF 3+ scenes show internal acceleration pattern → PASS
IF scenes are uniformly paced internally → SOFT FLAG:
   "Flat Scene Rhythm — scenes lack internal shape"
IF every scene follows identical rhythm → FLAG:
   "Rhythmic Monotony — predictable acceleration"
```

**Logic Gate: The Scale Nesting**
```
CHECK: Does Jo-ha-kyū operate at multiple scales simultaneously?

IF whole-work rhythm AND act-level rhythm both present → PASS
IF only whole-work rhythm → SOFT FLAG:
   "Macro-Only — scenes lack shape"
IF rhythm present at scene level but not macro level → FLAG:
   "Micro-Only — individual scenes shaped but overall arc flat"
```

**Genre Cross-Reference:**
- Literary Fiction: Jo phase can be extended; Kyū may be a single devastating paragraph
- Thriller: Ha phase dominates; Jo is compressed; Kyū is the chase/confrontation
- Horror: Jo establishes normalcy (the lullaby); Ha introduces wrongness; Kyū is the break
- Erotica: Maps to arousal pacing; Jo is approach, Ha is escalation, Kyū is climax (note overlap with Wave/Pulse)

---

## Family 11: Format & Frame Engines

Structures defined by their formal presentation or framing device.

### 45. Episodic / Modular Structure

**Best for:** Story collections with arc, character studies, picaresque, "life in fragments."
**Breaks when:** Episodes don't accumulate; the whole isn't more than the sum.
**On the page:** Self-contained chapters with their own micro-arcs; unity through theme, character, or motif rather than plot.

**Logic Gate: The Accumulation Test**
```
CHECK: Does reading episodes in sequence produce meaning that individual
       episodes don't contain?

IF sequence creates emergent understanding → PASS
IF episodes are interchangeable in order → FLAG: "Unsequenced — collection, not novel"
IF episodes build but final episode doesn't apply pressure → FLAG: "Missing Capstone"
```

**Logic Gate: The Episode Completeness**
```
CHECK: Does each episode have its own internal arc (shift, turn, or button)?

IF 80%+ of episodes have internal arc → PASS
IF episodes are vignettes without turns → SOFT FLAG: "Sketches, Not Episodes"
IF some episodes exist only for series plot → FLAG: "Bridge Episode — serving the whole at expense of the part"
```

---

### 46. Clinical Case File

**Best for:** Psychological domination, institutional horror, unreliable interpretation, stories about diagnosis.
**Breaks when:** The "analyst" voice becomes authoritative rather than suspect.
**On the page:** Triangulation between observed behavior, private experience, and interpretation (real, false, or manipulative).

**Logic Gate: The Discrepancy Engine**
```
CHECK: Do observed, experienced, and interpreted realities DIVERGE?

IF all three layers produce different truths → PASS
IF observation and interpretation align (experience suppressed) → SOFT FLAG: "Gaslighting Structure — check if intentional"
IF all three align → N/A (not a Case File structure)
```

**Logic Gate: The Interpreter Reliability**
```
CHECK: Is the interpreting voice's authority destabilized?

IF reader has reason to doubt interpretation by Act III → PASS
IF interpreter is presented as neutral/reliable throughout → FLAG: "Unquestioned Authority"
IF interpreter's motives are revealed as corrupt → Check for Revelatory Plot overlay
```

---

### 47. Nested Dolls (Frame-within-Frame)

**Best for:** Hypnosis narratives, memory distortion, gaslighting, stories about layers of reality.
**Breaks when:** Layers don't interact; frame is ornamental.
**On the page:** Outer frame → inner story → deeper inner story → core revelation → return through layers, each recontextualized.

**Logic Gate: The Layer Interaction Test**
```
CHECK: Does the core revelation CHANGE the meaning of outer layers?

IF returning through frames produces retroactive recontextualization → PASS
IF layers are independent (nested but not interactive) → FLAG: "Stacked, Not Nested"
IF core layer contradicts outer layers → Check if intentional (reality destabilization)
```

**Logic Gate: The Descent Motivation**
```
CHECK: Is there a reason to go deeper at each level?

IF each descent is motivated by question or compulsion → PASS
IF descent is structural but unmotivated → FLAG: "Arbitrary Nesting"
```

---

### 48. Talisman Structure

**Best for:** Object-focused narratives, symbolic horror, stories where meaning accrues to a physical thing.
**Breaks when:** Object doesn't transform in meaning; it's just a recurring prop.
**On the page:** Object introduced → encountered in new contexts → meaning shifts with each appearance → final encounter seals or breaks something.

**Logic Gate: The Semantic Shift**
```
CHECK: Does the talisman's meaning CHANGE with each major appearance?

IF meaning shifts at least 3 times → PASS
IF meaning stays constant → FLAG: "Static Symbol — prop, not talisman"
IF meaning inverts (comfort → threat or innocence → corruption) → PASS (strongest form)
```

**Logic Gate: The Final Encounter**
```
CHECK: Does the talisman's last appearance carry the weight of all prior appearances?

IF final encounter is loaded with accumulated meaning → PASS
IF talisman simply reappears → FLAG: "Uncollected Investment"
IF talisman is absent from climax → FLAG FOR REVIEW: "Missing Payoff Object"
```

---

## Family 12: Transformation & Identity Journeys (Extended)

### 49. Heroine's Journey (Murdock)

**Best for:** Interior reconciliation arcs, recovery from over-identification, reclamation of suppressed self.
**Breaks when:** "Feminine/masculine" literalized as gender essentialism; descent has no psychological specificity.
**On the page:** Separation from one identity → over-identification with opposite → spiritual aridity → descent → reclamation → integration.

**Logic Gate: The False Empowerment Beat**
```
CHECK: Is there a moment where protagonist achieves success that feels hollow?

IF hollow victory present between 30-50% → PASS
IF protagonist's success feels genuine throughout → N/A (different spine)
IF hollow victory present but not recognized by protagonist → Check if intentional (delayed recognition)
```

**Logic Gate: The Integration Test**
```
CHECK: Does the ending integrate both halves rather than choosing one?

IF protagonist synthesizes previously opposed aspects of self → PASS
IF protagonist simply returns to starting identity → FLAG: "Regression, Not Integration"
IF protagonist replaces one over-identification with another → FLAG: "Swapped Cage"
```

**Genre Cross-Reference:**
- Literary Fiction: Integration can be partial or ambiguous
- Romance: Integration often coincides with relational resolution
- Horror: "Integration" may be the horror — the self was always both

---

### 50. Seven-Point Structure (Dan Wells)

**Best for:** Tight novellas, mystery/thriller arcs, psychological reveals where pressure points matter more than acts.
**Breaks when:** Midpoint lacks genuine internal shift; pinch points feel arbitrary.
**On the page:** Hook → Plot Turn 1 → Pinch 1 → Midpoint → Pinch 2 → Plot Turn 2 → Resolution.

**Logic Gate: The Pinch Escalation**
```
CHECK: Is Pinch 2 materially worse than Pinch 1?

IF Pinch 2 raises stakes beyond Pinch 1 → PASS
IF Pinch 2 is lateral (different but not worse) → SOFT FLAG: "Parallel Pinches"
IF Pinch 2 is less intense than Pinch 1 → FLAG: "Deflating Pressure"
```

**Logic Gate: The Midpoint Shift**
```
CHECK: Does protagonist gain genuine power or insight at midpoint
       (not just information)?

IF midpoint produces internal transformation → PASS
IF midpoint is purely informational → FLAG: "Data Midpoint — knowledge without shift"
IF no identifiable midpoint → N/A (different spine)
```

---

## Diagnostic Quick Reference

### When the Draft Feels...

| Symptom | Likely Diagnosis | Recommended Spine Injection |
|---------|------------------|----------------------------|
| Meandering / no drive | Lack of teleology | Add Save the Cat beats (Midpoint, All Is Lost) |
| Too simple / too neat | Lack of recursion | Add Spiral or Fugue elements |
| Just misery porn | Lack of agency | Add Captivity logic (micro-choices matter) |
| Flat ending | Lack of recontextualization | Add Revelatory Plot (reframe the past) |
| Boring relationship | Lack of risk | Add Courtship Plot (intimacy = stakes) |
| Repetitive but intentional | Missing variation cost | Apply Fugue rules (each return costs something) |
| Ethically thin | Missing accountability | Add Procedural or Corruption beats |
| Stakes feel abstract | Missing countdown | Add deadline with concrete consequences |
| Emotionally flat despite good structure | Missing rhythm | Add Wave/Pulse crests between structural beats |
| Creepy but not dreadful | Missing trust-rupture | Add Lullaby rhythm (establish comfort, then break it) |
| Claustrophobic but not escalating | Stalled constraint | Apply Pressure Cooker ratchet (each section tightens) |
| Episodic but not accumulating | Missing capstone | Apply Episodic logic gates (sequence = emergent meaning) |
| Character "empowered" but story feels hollow | False victory without descent | Add Heroine's Journey (Murdock) descent-and-integration |
| Symbolic object falls flat | Static symbol | Apply Talisman rules (meaning must shift per appearance) |
| Unreliable narrator without payoff | Missing discrepancy | Apply Clinical Case File (triangulate observation, experience, interpretation) |
| Conflict-driven diagnostics flagging a manuscript that clearly "works" | Wrong structural paradigm assumed | Check for Kishōtenketsu; suppress conflict-based gates |
| Pacing feels metronomic or flat despite good structure | Missing rhythmic shape | Apply Jo-ha-kyū overlay at macro and scene level |
| Juxtaposition present but ending falls flat | Weak reconciliation | Apply Kishōtenketsu Ketsu gate (meaning from contrast, not resolution) |

### Spine Compatibility Matrix

Some spines combine naturally; others fight.

| Combination | Compatibility | Notes |
|-------------|---------------|-------|
| Fichtean + Countdown | High | Natural thriller pairing |
| Spiral + Fugue | High | Recursion engines stack well |
| Mystery + Revelatory | High | Investigation leads to recontextualization |
| Braided + Two-Handed | High | Multiple perspectives enhance both |
| Corruption + Redemption | Sequential | One follows the other |
| Captivity + Training | High | Often co-occur |
| Psychological Horror + Mystery | Medium | Can fight (ambiguity vs. resolution) |
| Wave/Pulse + Spiral | High | Waves provide rhythm; spiral provides direction |
| Lullaby + Seduction | High | Trust-building/rupture maps onto seduction mechanics |
| Pressure Cooker + Captivity | High | Ratcheting constraint + micro-agency |
| Pressure Cooker + Fichtean | High | Both escalate; Pressure Cooker adds internal toll |
| Clinical Case File + Psychological Horror | High | Triangulated unreliability deepens ambiguity |
| Nested Dolls + Revelatory | High | Frame descent produces retroactive recontextualization |
| Talisman + Fugue | High | Both use repetition-with-variation; Talisman grounds it in object |
| Episodic + Wave/Pulse | Medium | Episodes can ride wave rhythm, but risk shapelessness |
| Heroine's Journey + Betrayal of Self | High | Integration arc powered by self-alienation |
| Seven-Point + Countdown | High | Pinch points align with deadline pressure |
| Lullaby + Pressure Cooker | Low | Lullaby needs comfort phases; Pressure Cooker eliminates them |
| Kishōtenketsu + Save the Cat | Low | Different theories of what drives narrative |
| Kishōtenketsu + Wave/Pulse | Medium-High | Wave provides intensity shape without requiring conflict |
| Kishōtenketsu + Talisman | High | Object meaning shifts via juxtaposition |
| Kishōtenketsu + Fugue | Medium | Repetition-with-variation works, but Fugue's dread accumulation may smuggle conflict back in |
| Kishōtenketsu + Lullaby | Medium | Lullaby's comfort-then-rupture can coexist with juxtaposition, but rupture risks smuggling conflict back in |
| Kishōtenketsu + Heroine's Journey | Low | Heroine's Journey requires descent/integration arc, which implies conflict with self |
| Jo-ha-kyū + any spine | High (overlay) | Pacing layer; compatible with all structural spines |
| Jo-ha-kyū + Pressure Cooker | Medium | Pressure Cooker resists Jo's measured opening |

---

## Integration with Core Framework

This audit modifies:
- **Pass 2 (Structural Mapping):** Apply spine-specific beat expectations
- **Pass 6 (Scene Function):** Evaluate scenes against spine requirements
- **Synthesis:** Include spine diagnosis and logic gate results

**Output:** Spine identification, logic gate results (PASS/FLAG/BREAK), recommended interventions.

---

*This audit provides plot architecture diagnosis. It identifies which structural tool the manuscript is using and checks whether that tool is functioning correctly. The system diagnoses structure; the author chooses and refines the spine.*
