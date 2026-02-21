# Genre Module: Science Fiction / Fantasy
## Version 0.4.14.2
*Last Updated: February 2026*

---

## Core Contract

SF/F readers buy a specific promise: **"A world that works differently, but works."**

The primary failure mode is not "unrealistic" but **inconsistent**. Every SF/F manuscript establishes its own physics engine. The editor's job is to verify that engine runs without crashes.

---

## Subgenre Logic Table

Calibrate false positives based on subgenre. What's a bug in one subgenre is a feature in another.

| Subgenre | Primary Expectation | Distinctive Structural Constraint | Common False Positive to Ignore |
|----------|---------------------|-----------------------------------|--------------------------------|
| **Hard SF** | Competence porn, scientific accuracy | Plot must turn on a scientific reality/problem | "Dry" or technical dialogue |
| **Space Opera** | Scale, melodrama, adventure | Stakes must be political/civilizational | "Unrealistic" physics (FTL, sound in space) |
| **Cyberpunk** | High tech, low life, systemic decay | Protagonist usually cannot "save the world," only survive it | Depressing endings; anti-heroism |
| **Epic Fantasy** | Total immersion, clear moral vectors | The "Quest" structure; detailed magic systems | Slow pacing in Act I (world establishment) |
| **Urban Fantasy** | Hidden world within our world | Masquerade maintenance; noir/detective beats | Mixing modern slang with archaic concepts |
| **New Weird** | The uncanny, body horror, indefinable | Deliberate lack of explanation for the strange | "Unexplained" phenomena (ambiguity is the point) |
| **Progression/LitRPG** | Quantifiable growth, hard rules | Power levels must rise visibly and numerically | "Video game" logic or stat sheets |
| **Solarpunk/Hopepunk** | Radical optimism, solutions | Conflict often man vs. nature or man vs. self, not man vs. villain | Lack of violent conflict |
| **Grimdark** | Nihilism, subversion of heroism | No "good" outcome; survival is the only victory | Unlikable protagonists; pyrrhic victories |
| **Portal Fantasy** | Fish-out-of-water discovery | Protagonist learns rules alongside reader | Convenient inciting incident (falling into portal is allowed) |

---

## Subgenre Pass Recalibrations

The Subgenre Logic Table above tells you what false positives to suppress. This section tells you how to *run each pass differently* depending on the subgenre. SFF subgenres don't share a common engine the way Romance subgenres do — Hard SF and Portal Fantasy have genuinely different diagnostic needs.

**How to use:** After identifying the subgenre during intake, consult the Master Calibration Matrix to see which passes need adjustment. Then read the per-pass recalibration notes for specifics. Passes marked STANDARD run as written above with no changes.

### Master Calibration Matrix

| Pass | Hard SF | Space Opera | Cyberpunk | Epic Fantasy | Urban Fantasy | New Weird | Progression/LitRPG | Solarpunk | Grimdark | Portal Fantasy |
|------|---------|-------------|-----------|--------------|---------------|-----------|-------------|-----------|----------|----------------|
| **0 (Reverse Outline)** | ▲ | — | — | ▲ | — | ▼ | — | — | — | ▲ |
| **1 (Reader Experience)** | ↻ | — | ↻ | ↻ | ↻ | ↻ | ↻ | — | ↻ | ▲ |
| **4 (Emotional Value)** | ↻ | ▲ | ↻ | ▲ | — | ↻ | ↻ | ↻ | ↻ | ▲ |
| **5 (Character Audit)** | ↻ | — | ▲ | — | ↻ | ↻ | ▲ | — | ↻ | ↻ |
| **6 (Scene Function)** | ▲ | — | — | ↻ | — | ▼ | — | — | — | — |
| **8 (Reveal Economy)** | ▲ | — | ↻ | ↻ | ↻ | ▼ | ↻ | — | — | ▲ |
| **9 (Thematic Coherence)** | ↻ | — | ▲ | — | — | ↻ | ↻ | ▲ | ↻ | — |
| **10 (Entity/Continuity)** | ▲ | ↻ | ↻ | ▲ | ↻ | ▼ | ▲ | — | — | ↻ |

**Key:** ▲ = Elevate (tighter thresholds, higher priority) · ▼ = Deprioritize (looser thresholds, lower priority) · ↻ = Recalibrate (different focus, not tighter/looser) · — = Standard (run as written)

### Per-Pass Recalibration Notes

#### Pass 0: Reverse Outline

**Hard SF** ▲ — Tag `[SCIENCE CLAIM]` alongside `[NEW RULE]`. Track whether plot-critical science is established or handwaved. If a science claim drives the climax but was never seeded, flag "Unseeded Science" (stricter than the standard Deus Ex Machina risk).

**Epic Fantasy** ▲ — `[NEW RULE]` tracking is critical because magic systems accumulate across 100k+ words. Track separately: hard rules (explicit limits), soft rules (implied limits), and lore (background history). Only hard rules trigger Deus Ex Machina risk; soft rules get "Possible Soft-System Stretch" (lower severity); lore gets no mechanical flag.

**New Weird** ▼ — `[NEW RULE]` tags may not apply. The world may resist codification by design. If the manuscript's contract specifies soft/mysterious worldbuilding, suppress `[RULE VIOLATION]` flags unless the violation is *narratively* incoherent (not just mechanically unexplained). Flag only when the violation breaks the story's own dream-logic.

**Portal Fantasy** ▲ — Track the protagonist's learning curve. Tag `[DISCOVERY]` for moments when the protagonist (and reader) learn a rule. Discovery pacing should parallel reader orientation. If the protagonist understands a rule before it's been demonstrated to the reader, flag "Reader Left Behind." If rules are demonstrated but the protagonist doesn't react, flag "Passive Learner."

#### Pass 1: Reader Experience

**Hard SF** ↻ — "I don't understand the rules" is a serious flag here. Hard SF promises comprehensibility. But "I don't understand the jargon" is a false positive if context clues exist. Distinguish: *system confusion* (flag) vs. *vocabulary density* (tolerate if decodable).

**Cyberpunk** ↻ — Disorientation in the first 10% is a feature (the reader should feel the world's information overload). "I'm lost" becomes a flag only after the 15% mark. "I don't care about anyone" has a higher threshold — anti-heroes and damaged protagonists are genre-conventional. Flag only if no character generates investment by the 25% mark.

**Epic Fantasy** ↻ — "Slow start" is not a flag for the first 12-15% (conventional establishment window for 100k+ word count). However, track whether the slow start is *orienting* or *stalling*. Orienting: each chapter adds world-knowledge the reader needs. Stalling: chapters add atmosphere without mechanical or emotional information. Flag stalling, not slowness.

**Urban Fantasy** ↻ — Track the dual-world experience. Reader should feel grounded in the "normal" world before the hidden world intrudes. If the speculative element appears before page 1 orientation in the mundane world, flag "Missing Baseline" (reader needs the ordinary to feel the extraordinary).

**New Weird** ↻ — "I don't understand what's happening" is the *expected* reader experience in early chapters. Flag only "I don't care what's happening" — engagement without comprehension is the target. The wonder axis (Pass 4) should register as estrangement, not confusion.

**Grimdark** ↻ — "I don't like anyone" has a much higher tolerance. Flag only if no character generates *interest* (not sympathy) by the 30% mark. Sympathy is optional; fascination is not. "This is too dark" is a false positive if the contract promises grimdark.

**Portal Fantasy** ▲ — The reader experience IS the protagonist's experience. Track synchronization: moments where the protagonist's wonder/confusion/discovery maps onto the reader's. Desynchronization (protagonist knows more or less than reader without narrative justification) is a serious flag here because it breaks the genre's core promise.

**Progression/LitRPG** ↻ — Stat-block exposition (character sheets, level-up screens, skill descriptions) is not an infodump in this subgenre. Flag only if stat blocks occur without narrative context (no stakes, no choice, no consequence) for 3+ consecutive instances.

#### Pass 4: Emotional Value Tracking

**Hard SF** ↻ — The wonder axis peaks at *understanding*, not spectacle. Track "eureka" moments alongside standard wonder. If the protagonist solves a science problem and the emotional register is purely intellectual (no fear, relief, or triumph), flag "Cerebral Vacuum — the science works but the scientist doesn't feel it."

**Space Opera** ▲ — Wonder should be BIG. Scale, spectacle, and sweep are the emotional contract. If the wonder axis flatlines after Act I worldbuilding, flag "Domesticated Galaxy — the universe has become furniture." The power-cost emotional check applies to civilizational stakes, not just personal ones: empires falling should *feel* like something.

**Cyberpunk** ↻ — The dominant emotional axis is *alienation*, not wonder. Track alienation (from self, from society, from embodiment) alongside standard emotional tracking. Wonder in cyberpunk is often tinged with horror or vertigo. If the tech augmentation generates only enthusiasm and never disquiet, flag "Chrome Without Cost."

**Epic Fantasy** ▲ — Track *moral weight* as a distinct emotional register. Characters inherit the weight of history (ancient evils, prophecies, ancestral obligations). If the quest generates only adventure-excitement without moral gravity by the midpoint, flag "Weightless Quest."

**New Weird** ↻ — The emotional target is *estrangement* — wonder's uncanny cousin. Track moments where the world resists comprehension and the character's emotional response registers that resistance. If characters accept impossibility without affect, flag "Domesticated Weird — the uncanny has become mundane."

**Solarpunk** ↻ — Track the *hope axis* — distinct from wonder. Hope in solarpunk should feel earned through difficulty, not given as a starting condition. If optimism is the default emotional state rather than an achievement, flag "Pre-Earned Hope — the world is already saved before the story starts."

**Grimdark** ↻ — The power-cost emotional check inverts: power should feel *compromising*, not empowering. Track the corruption/degradation axis. If violence and power acquisition generate no psychological mark, flag "Clean Hands in a Dirty World" (not the same as Teflon Protagonist from Thriller — here the issue is moral, not physical).

**Portal Fantasy** ▲ — The wonder axis should track the protagonist's arc from *outsider awe* through *acclimatization* to *earned understanding*. If wonder disappears after Act I and doesn't return as deeper appreciation, the portal experience has stalled. Threshold: wonder should resurface in at least 2 scenes after the 50% mark.

**Progression/LitRPG** ↻ — The emotional register of power-up should evolve. Early: excitement, validation. Middle: ambition, temptation, cost-awareness. Late: responsibility, sacrifice, or mastery-as-burden. If every level-up generates the same emotional beat (triumph → move on), flag "Flat Progression Affect." Threshold: emotional register unchanged across 3+ power-ups.

#### Pass 5: Character Audit

**Hard SF** ↻ — Competence is the genre contract. Don't flag high-competence protagonists as "Mary Sue/Gary Stu." Flag only if competence comes without cost, failure, or domain limitation. The test: does the protagonist fail at something *within* their expertise at least once? Zero in-domain failures → "Frictionless Expertise."

**Cyberpunk** ▲ — The competence-cost inventory must include *identity cost*. Chrome, augmentation, neural modification — these don't just cost resources. They cost selfhood. Track: what has the character given up of their original self? If augmentation has only tactical consequences (better aim, faster reflexes) without identity consequences (what am I now?), flag "Unexamined Augmentation."

**Urban Fantasy** ↻ — Track dual-identity strain. The protagonist maintains a normal life and a supernatural one. The character audit should verify both identities are developed — not just the supernatural side. If the mundane identity is cardboard (exists only to be disrupted), flag "Paper Normal — the character only matters when the magic is on."

**New Weird** ↻ — Character coherence operates differently. Characters may be *changed* by the world in ways that resist psychological realism. Don't flag psychological inconsistency if the inconsistency is *caused by* the world's weirdness and the text acknowledges it. Flag only when characters are inconsistent for no world-related reason.

**Grimdark** ↻ — The competence-cost inventory inverts: track what competence has *taken from* the character. In grimdark, mastery should leave marks — moral compromise, isolation, loss of innocence. If the protagonist is a skilled fighter/mage/operative and that skill hasn't cost them something human, flag "Costless Edge."

**Portal Fantasy** ↻ — Track the learning curve. The protagonist should develop competence *within the story*. If they arrive with skills that conveniently match the new world's needs without explanation, flag "Suspiciously Prepared." Competence growth should be visible and struggled-for. Threshold: at least 2 demonstrated failures before the protagonist achieves basic competence.

**Progression/LitRPG** ▲ — The competence-cost inventory is the CENTRAL diagnostic for this subgenre. Track every power acquisition: what was the quantifiable cost? What was the narrative cost? What was the psychological cost? If quantifiable cost exists but narrative and psychological costs are absent for 3+ level-ups, flag "Stat Growth, Character Stasis." The defining test: is the character at Level 20 a *different person* than at Level 1, or just a bigger number?

#### Pass 6: Scene Function

**Hard SF** ▲ — The "Double Duty" check is critical. Pure problem-solving scenes (protagonist works through a scientific challenge) are allowed even without character development if they generate tension. But track: does the science create *dramatic* tension (time pressure, stakes, uncertainty) or only *intellectual* puzzle satisfaction? Pure puzzles without stakes → "Lab Bench Scene — interesting problem, no dramatic function."

**Epic Fantasy** ↻ — Council/war-room scenes are conventional but must do double duty. If a council scene delivers only strategic information without character dynamics (who wants what, who's lying, who's afraid), flag "Empty Council — this is a briefing, not a scene."

**New Weird** ▼ — Scenes may exist primarily for atmosphere, estrangement, or phenomenological experience. Standard "every scene needs a function" logic loosens. Flag only scenes that are atmospheric AND boring (no sensory charge, no cognitive work for the reader).

#### Pass 8: Reveal Economy

**Hard SF** ▲ — Rule reveals must be both *accurate* and *dramatic*. Scientific exposition that is correct but undramatized → "Textbook Passage." Tighter threshold on late-stage worldbuilding: no new fundamental science after 50% (stricter than the standard 60% threshold). Exception: if the late science is a *consequence* of earlier established rules, not a new rule.

**Cyberpunk** ↻ — Track *system reveals* alongside standard reveals. The revelation of how the system works (corporate structure, surveillance apparatus, social control) follows its own economy. System reveals should escalate in scope: personal → institutional → structural. If the protagonist learns the system is corrupt at the beginning and nothing deeper is revealed, flag "Flat Conspiracy."

**Epic Fantasy** ↻ — The reveal economy spans much longer timescales. Adjust cadence expectations: rule reveals can continue through 50% (not the standard 40%) for 100k+ manuscripts. But the *type* shifts: early reveals should be operational (how magic works), middle reveals should be exceptional (what the rules hide), late reveals should be consequential (what the rules cost at civilizational scale).

**Urban Fantasy** ↻ — Track masquerade reveals alongside standard reveals. The "hidden world" should deepen in layers: surface (magic exists) → structural (here's how it's organized) → consequential (here's what it costs to maintain). If the masquerade is fully revealed early and then becomes irrelevant, flag "Spent Masquerade."

**New Weird** ▼ — The reveal economy may deliberately *withhold* reveals. Not all mysteries require resolution. Flag only when withholding is *unsatisfying* (reader feels cheated) rather than *productive* (reader feels haunted). This is a reader-experience judgment, not a structural one.

**Portal Fantasy** ▲ — Reveal cadence should track the protagonist's discovery curve. Front-loading is expected and welcome — the reader is learning the world alongside the character. But each reveal should deepen, not just add. If reveals at 40% are the same *type* as reveals at 10% (just more facts about the world), flag "Flat Discovery — learning more without understanding deeper."

**Progression/LitRPG** ↻ — The system itself is a reveal economy. New abilities, new tiers, new mechanics are reveals. Track: does each system reveal *change the strategic landscape* or just add another option? If the Level 10 unlock doesn't change how the protagonist approaches problems, it's a stat bump, not a reveal. Threshold: 3+ system reveals without strategic consequence → "Incremental Grind."

#### Pass 9: Thematic Coherence

**Hard SF** ↻ — The science itself should embody the theme. If the story is about hubris, the technology should be a *lens* on hubris that couldn't exist without the specific science. Flag if theme could be served by any technology (interchangeable tech = wallpaper theme).

**Cyberpunk** ▲ — Systemic critique is the genre contract. The thematic integration check must verify that technology is not just setting but *argument*. If the tech creates cool scenes without interrogating power, identity, or embodiment, flag "Aesthetic Cyberpunk — the neon is on but nobody's asking questions."

**New Weird** ↻ — Theme may operate through accumulation and resonance rather than statement. Don't require a statable one-sentence theme. Instead, track thematic *patterns* — recurring images, situations, transformations that accrue meaning. Flag only if no pattern emerges across the full manuscript.

**Solarpunk** ▲ — The speculative element should embody the *solution*, not just the problem. If the story's optimism comes entirely from character attitude rather than from the world's technology/social structure demonstrating that another way is possible, flag "Optimism Without Evidence — the hope isn't built into the world."

**Grimdark** ↻ — Nihilism is not the absence of theme. Track what the story's darkness *argues* — about power, survival, moral compromise, the cost of violence. If the darkness is purely atmospheric (bad things happen, no accumulating meaning), flag "Decorative Nihilism — the suffering doesn't mean anything."

**Progression/LitRPG** ↻ — The system itself is a thematic statement about growth, power, and merit. What does it mean that power is quantifiable? That growth follows rules? That hard work is rewarded with measurable advancement? If the system is presented uncritically (grind = good, power = reward, no examination of what the system costs or excludes), flag "Uncritical Meritocracy."

#### Pass 10: Entity & Continuity (Rule Ledger)

**Hard SF** ▲ — The Rule Ledger is the PRIORITY diagnostic. Every scientific claim is a rule. Cost Amnesia threshold: zero tolerance. If a scientific constraint is established and then violated without explanation, flag as Must-Fix regardless of context.

**Space Opera** ↻ — The Rule Ledger applies to *political* and *technological* rules, not physics. FTL exists; don't track its consistency unless the story specifically constrains it. Track instead: faction capabilities, political commitments, resource limitations. Cost Amnesia applies to strategic resources, not to handwaved physics.

**Cyberpunk** ↻ — Track *system rules* alongside magic/tech rules. How does the corporation work? What are the surveillance capabilities? What are the economic constraints? These are the "physics" of cyberpunk. If a corporate antagonist's capabilities fluctuate for plot convenience, flag "Convenient Oppression."

**Epic Fantasy** ▲ — The Rule Ledger must handle magic system complexity. For hard magic: full ledger, zero-tolerance Cost Amnesia. For soft magic: track only *established* limits and *demonstrated* costs. For hybrid: separate ledger columns for hard elements (strict) and soft elements (pattern-tracked).

**Urban Fantasy** ↻ — Track masquerade rules as physics. If magic is hidden from mundanes, every public use needs consequence tracking. "Masquerade Amnesia" — public magic use without fallout — is the urban fantasy equivalent of Cost Amnesia.

**New Weird** ▼ — The Rule Ledger may be partially inapplicable. If the world resists systematization, track only *narrative* consistency (does the world behave consistently within its own dream-logic?) rather than *mechanical* consistency (do the rules add up?). Flag only contradictions that break the story's internal coherence, not contradictions that serve its weirdness.

**Progression/LitRPG** ▲ — The Rule Ledger is CRITICAL. The system's rules are the reader's contract. Any mechanical inconsistency (a skill does X in one scene and Y in another, a level requirement is bypassed without explanation) is a Must-Fix. Cost Amnesia in progression systems (a costly ability becomes free when plot requires it) breaks reader trust in the entire system. Zero tolerance.

### Subgenre Deep-Dive Override Table

Some named deep-dive flags from the main module need subgenre-specific threshold adjustments:

| Flag | Subgenre | Override |
|------|----------|----------|
| **SFF-DD1 (Magic Microwave)** | Progression/LitRPG | Raise threshold to 5+ identical uses (mechanical consistency is expected). Flag only if *emotional* register is also identical. |
| **SFF-DD1 (Magic Microwave)** | Hard SF | Lower threshold to 2+ identical uses. If science is a puzzle, each use should reveal new facets. |
| **SFF-DD2 (Worldbuilding Orphan)** | Epic Fantasy | Raise threshold to 5+ orphaned details (epic fantasy conventionally builds world depth that pays off across long arcs or series). Add: "Possible Long-Arc Seed" for Series Book 1. |
| **SFF-DD2 (Worldbuilding Orphan)** | New Weird | Suppress unless orphaned details are *emphasized* (given narrative weight). Ambient strangeness that doesn't pay off is the mode, not a failure. |
| **SFF-DD3 (Escalation Treadmill)** | Progression/LitRPG | Raise threshold to 4+ cycles (escalation IS the contract). Flag only if no cycle includes lateral thinking, sacrifice, or strategic innovation. |
| **SFF-DD3 (Escalation Treadmill)** | Grimdark | Invert the flag: if escalation leads to clear *victories*, suspect the contract. In grimdark, escalation should lead to pyrrhic outcomes. Flag "Clean Escalation — the power curve doesn't cost anything." |

### Cross-Reference: Worldbuilding Audit Subgenre Calibration

The SFF Worldbuilding Integration Audit (`sff-worldbuilding.md`) provides its own subgenre calibration focused on integration dimensions (cognitive, thematic, prose, social, emotional). When running both the genre module and the worldbuilding audit:

- **This module** handles mechanical consistency, pass-level diagnostics, and structural flags.
- **The worldbuilding audit** handles whether the world does narrative *work* across five integration dimensions.
- Subgenre calibrations in both modules should agree: if this module deprioritizes Rule Ledger strictness for New Weird, the worldbuilding audit should correspondingly loosen its mechanical integration expectations.

Consult both calibration tables during intake to ensure aligned expectations.

---

## Contract Schema Additions

Add these fields to the Manuscript Contract for SF/F works:

```
NOVUM (The Speculative Element): [The specific change: e.g., FTL travel, Elemental Magic]
MAGIC/TECH SYSTEM HARDNESS: [Hard / Soft / Hybrid]
COST OF POWER: [What is paid? Life, Sanity, Energy, Social Standing?]
EXPOSITION TOLERANCE: [High (Infodumps allowed) / Medium / Low (Show-don't-tell)]
SCOPE: [Personal / City / Continent / Galactic / Multiversal]
TECH LEVEL: [Stone Age / Medieval / Industrial / Information / Post-Scarcity]
```

### Sanderson's Laws (Quick Reference)

**First Law:** The ability to solve problems with magic is proportional to how well the reader understands it.
- **Hard magic:** Reader knows the rules → magic can solve climactic problems
- **Soft magic:** Rules mysterious → magic creates problems but shouldn't solve them

**Second Law:** Limitations are more interesting than powers.

**Third Law:** Expand what you have before adding something new.

---

## Intake Calibration Questions

### A. The Novum (The One Big Lie)

1. **What is the central speculative element?** (The thing that makes this world different from ours.)

2. **What are the Hard Limits?** Complete: "Magic/Tech can do X, but it absolutely cannot do Y."

3. **What is the Cost Mechanism?** Is the cost paid before, during, or after usage? What form does it take?

4. **What is the Tech Level?** Stone Age → Medieval → Industrial → Information → Post-Scarcity

5. **How Hard is the System?**
   - **Hard:** Rules explicit, reader could predict outcomes
   - **Soft:** Mysterious, reader cannot predict, creates wonder/dread
   - **Hybrid:** Some aspects hard (combat magic), others soft (prophecy)

### B. The Integration Tests

1. **The "Replace with Cellphone" Test:** If you replaced the magic spell with a smartphone/gun, does the scene play out exactly the same?
   - **If yes:** The speculative element is wallpaper, not load-bearing.
   - **Action:** Flag for author consideration. Is this intentional (background texture) or a missed opportunity?

2. **The "Salt vs. Meal" Test:** Is the speculative element the Meal or the Salt?
   - **Meal:** The story is *about* the magic/tech (e.g., *Jurassic Park*, *The Martian*)
   - **Salt:** Human drama flavor-enhanced by magic (e.g., *Star Wars*)
   - **Action:** If Contract says "Meal" but draft reads like "Salt," flag as "Speculative Element Under-utilized."

3. **The Social Impact Test:** Name one social custom, law, or religious belief that exists solely because of the Novum.
   - **If author cannot answer:** Worldbuilding may be superficial.

---

## Pass Modifications

### Priority Pass: Pass 10 (Entity & Continuity) — The Physics Engine

In SF/F, entity tracking isn't just checking for typos. It's verifying the world's physics engine runs without crashes.

**The Rule Ledger Protocol:**

Build a dynamic table tracking every magic/tech usage:

| Scene | The Action | Established Cost | Payment Shown | Notes |
|-------|------------|------------------|---------------|-------|
| Ch. 3 | Cast Fireball | Burns calories | Hero eats energy bar | ✓ Consistent |
| Ch. 12 | Cast Fireball (larger) | Burns calories | No payment shown | ⚠️ Cost Amnesia? |
| Ch. 15 | Teleport squad | Unstated | None | ⚠️ New ability, no cost |

**Flag Triggers:**
- Column "Payment Shown" empty in High-Stakes scene → "Cost Amnesia"
- Action exceeds previously established limits without explanation → "Power Creep"
- New ability introduced without cost mechanism → "Scope Creep"

### Pass 0: Reverse Outline (Additions)

Add these tags:

- `[EXPOSITION BLOCK]` — Any paragraph >100 words explaining history/mechanics
- `[NEW RULE]` — Whenever a mechanic is explained for the first time
- `[RULE VIOLATION]` — When established rule appears to be broken

**Flag Triggers:**
- `[NEW RULE]` in final 15% of manuscript → "Deus Ex Machina Risk" (flag for review, not automatic violation—some reveals are seeded)
- `[EXPOSITION BLOCK]` density >3 per chapter early, <1 late → Normal (front-loaded)
- `[EXPOSITION BLOCK]` density increases in Act III → "Late-stage Explaining" (usually a problem)

### Pass 6: Scene Function (Additions)

**The "Double Duty" Check:**

In SF/F, scenes rarely just "inform." Pure exposition without conflict is a flag.

- **Weak:** Scene exists to explain how the magic works (character lectures)
- **Strong:** Scene teaches rule through consequence (character breaks rule, pays price)
- **Ideal:** "Exposition via Conflict" — learning the rule because breaking it hurt

**Flag:** Scenes tagged `[EXPOSITION BLOCK]` that have no other function (no conflict, no character development, no tension).

### Pass 1: Reader Experience (Additions)

Track specifically:
- **Orientation in space:** Where are we? (Especially in non-Earth settings)
- **Orientation in rules:** What can/can't happen here?
- **"Floating Head" moments:** Scene occurs with generic descriptors that could exist in 2024 Earth

**SF/F-specific reader experience flags:**
- "I'm lost" — worldbuilding insufficient or unclear; reader can't picture where they are
- "This is just Earth with swords" — speculative element is wallpaper
- "I don't understand the rules" — magic/tech system unclear when it needs to be clear (hard system)
- "Why is this a big deal?" — power/event has no established context for its significance
- "Wait, they could do that the whole time?" — ability introduced mid-crisis without setup

### Pass 4: Emotional Value Tracking (Additions)

**SF/F-specific emotional tracking:**

The **wonder axis** is unique to SF/F. Track moments of awe, discovery, and conceptual surprise alongside standard emotional tracking.

- Wonder should peak at key world reveals and diminish as the world becomes familiar — then resurface when deeper layers are exposed
- In Hard SF, wonder often comes from problem-solving with established rules
- In Epic Fantasy, wonder comes from scale and discovery
- In New Weird, wonder comes from the uncanny and inexplicable

**The Power-Cost Emotional Check:**

Track the emotional weight of power use. As characters gain capability, the *feeling* of power should evolve:

| Story Phase | Expected Emotional Register |
|-------------|---------------------------|
| Early | Wonder, fear, or awe at new ability |
| Middle | Confidence, temptation, cost awareness |
| Late | Burden, sacrifice, moral weight, or mastery earned through suffering |

**Threshold:** If protagonist's emotional response to using power is unchanged from Act I to Act III, flag "Flat Power Affect — magic/tech isn't changing the person."

### Pass 5: Character Audit (Additions)

**The Competence-Cost Inventory:**

For each character who wields the speculative element (magic user, tech specialist, powered individual):

| Character | Power/Skill | Cost Paid | Psychological Toll | Growth Required |
|-----------|-------------|-----------|-------------------|-----------------|
| [name] | [what they can do] | [what it costs them] | [how it changes them] | [what they must learn/accept] |

**Detect:**
- **Power without psychology:** Character wields magic/tech but it doesn't shape their identity, choices, or relationships → Flag "Disconnected Power — the ability is a tool, not part of the person"
- **Competence plateau:** Character is equally skilled at Act I and Act III, just with bigger problems → Flag if no learning, failure, or adaptation shown
- **Cost-free mastery:** Character achieves full control without sacrifice, training montage, or failure → Flag "Unearned Mastery" (threshold: 0 failures or setbacks before climactic power use)
- **Supporting characters as exposition vehicles:** Non-POV characters who exist only to explain rules → Flag "Walking Encyclopedia — this character is a textbook"

**Threshold:** By the 60% mark, at least 1 major character should have experienced a meaningful failure or unexpected cost from the speculative element. Zero failures → flag "Frictionless System — if magic never goes wrong, the stakes are theoretical."

### Pass 8: Reveal Economy (Additions)

**SF/F-specific information management:**

Worldbuilding reveals follow their own economy. Track:

- **Rule reveals:** When the reader learns how something works
- **Exception reveals:** When an established rule turns out to have a wrinkle
- **Scope reveals:** When the world turns out to be bigger/stranger/more connected than expected
- **Cost reveals:** When the true price of power becomes clear

**The Reveal Cadence:**
- Rule reveals should front-load (heaviest in first 40%). New rules in final 15% = Deus Ex Machina risk.
- Exception reveals work best in Act II (complicating established expectations).
- Scope reveals can work throughout but peak in Act II midpoint.
- Cost reveals are most powerful in Act III (when the bill comes due).

**Threshold:** If >2 fundamental rules (not minor details) are first introduced after the 60% mark, flag "Late-Stage Worldbuilding — the physics engine is being patched during the final boss fight."

### Pass 9: Thematic Coherence (Additions)

**SF/F-specific thematic tracking:**

The speculative element should embody or interrogate the theme. If the story is about power, the magic system should be a *lens* on power. If about identity, the Novum should pressure identity.

**The Thematic Integration Check:**
- Can you state the theme in one sentence?
- Does the speculative element make this theme *visible* in a way realistic fiction couldn't?
- Does the climax resolve the thematic question *through* the speculative element?

**Detect:**
- **Theme disconnected from Novum:** Story has a theme, but the speculative element doesn't interact with it → Flag "Parallel Tracks — the SF/F world and the story's meaning aren't talking to each other"
- **Novum as decoration:** The Novum exists for flavor but doesn't shape any character's choice or the plot's resolution → Flag "Wallpaper Novum — the speculative element could be removed without changing the story"
- **Theme stated through worldbuilding lecture:** Characters explain what the magic/tech "really means" rather than demonstrating it → Flag "Theme-as-Exposition"

---

## Genre-Specific Diagnostic Flags

### 1. "Wikipedia Dialogues" (As You Know, Bob)

**Detection:** Two characters tell each other facts they both already know.

**Example:** "As you know, Captain, the Warp Drive requires Dilithium."

**The Test:** Would this character actually say this to this listener? Do they both already know it?

**Fix Options:**
- Cut dialogue; move fact to narrative summary
- Have a novice character ask
- Reveal through conflict/consequence rather than explanation

### 2. Sanderson's First Law Violation

**Detection Logic:**
```
IF Magic System = "Soft/Mysterious"
AND Climax Solution = "Magic Usage" (protagonist uses magic to win)
THEN Flag: "Potential Unearned Resolution"
```

**Nuance:** Soft magic can appear in climaxes if:
- The magic creates the final problem, not the solution
- The solution is character choice/sacrifice, magic is backdrop
- The magic was seeded earlier (reader knew this was possible)

### 3. "Floating Head" Syndrome (White Room)

**Detection:** Scene occurs with generic physical descriptors that could exist anywhere.

**Test:** Remove all dialogue. Is the remaining description specific to this world?

**Fix:** Ground the scene in the secondary world:
- What does the air smell like?
- How many moons/suns are visible?
- What tech/magic is humming in the background?
- What's the architecture made of?

### 4. Power Creep (The Anime Problem)

**Detection:** Compare Act I threats to Act III threats.

**Test:** If the Act I "Big Bad" would be instantly defeated by the Act III protagonist, has the psychological/moral toll escalated to match?

**Flag Conditions:**
- Physical power up without corresponding psychological cost → Stakes have vanished
- Each new threat is "even more powerful" without deepening complexity → Escalation treadmill

**Exception:** Progression/LitRPG explicitly promises power creep. Flag only if the *challenge* doesn't scale with power.

### 5. "Retro-Causality" Error

**Detection:** A world-altering technology exists, but society is structured as if it doesn't.

**Examples:**
- Teleportation exists, but cities have walls and roads
- Instant communication exists, but messages take days to arrive (for plot convenience)
- Healing magic exists, but hospitals and disease are treated like our world

**Flag:** "Worldbuilding Inconsistency — [Tech/Magic] would reshape [Social Structure]."

**Exception:** If the inconsistency is explained (teleportation is illegal/expensive/rare), not a flag.

### 6. Cost Amnesia

**Detection:** Established costs are ignored when dramatically inconvenient.

**The Cost Matrix:**

| Cost Type | Narrative Function | Common Failure Mode |
|-----------|-------------------|---------------------|
| **Physiological** | Limits immediate action (Stamina/Health) | Hero ignores exhaustion in climax |
| **Material** | Limits frequency (Reagents/Ammo) | "Infinite ammo" cheat code |
| **Psychological** | Limits willingness (Sanity/Corruption) | Hero angst is stated but not shown in behavior |
| **Social** | Limits access (Illegal/Taboo) | Hero uses magic in public without consequence |
| **Temporal** | Limits speed (Casting time/Cooldowns) | Instant casting when earlier it took minutes |

**Flag:** Cost established in Act I, violated in Act III without justification.

---

## False Positive Warnings

**Do not flag these as problems:**

1. **"Unexplained Phenomena" in Soft SF/Horror/New Weird:** If Contract specifies mystery or Lovecraftian mode, lack of explanation is the feature.

2. **"Jargon Density" in Hard SF:** Technical terms ("Heisenberg Compensator") are expected if context clues exist. Flag only if jargon blocks comprehension.

3. **"Slow Start" in Epic Fantasy:** If word count >120k, extended Act I world establishment is conventional. Flag only if reader experience log shows actual boredom/confusion.

4. **"Convenient Inciting Incident" in Portal Fantasy:** Protagonist falling into the portal is allowed to be coincidence. Getting out cannot be.

5. **"Info-Dumping" in High Exposition Tolerance works:** If Contract specifies High Exposition Tolerance (e.g., Hard SF, Epic Fantasy), don't flag exposition blocks as failures. Flag only if reader experience log shows confusion or boredom.

6. **"Unrealistic Physics" in Space Opera:** FTL, artificial gravity, sound in space—these are genre conventions, not errors.

---

## Literary Mode Integration

**When Literary Fiction is primary and SF/F is subordinate or interrogated:**

SF/F conventions become thematic material rather than requirements:

- **The Novum as Metaphor:** Speculative element exists to embody theme (Octavia Butler's vampirism as addiction/dependency)
- **Convention Subversion as Commentary:** Breaking genre rules to make a point (Ishiguro's *The Buried Giant* refuses fantasy catharsis)
- **Worldbuilding Gaps as Feature:** Literary SF/F may leave mechanics unexplained to maintain ambiguity

**Recalibrations:**
- Rule Ledger still runs → data informs literary analysis
- Cost Amnesia still tracked → but ask "Is inconsistency serving theme?" before flagging
- Integration Tests still apply → but "wallpaper" may be intentional if theme is character-focused

**The Key Question:** Is the speculative element doing *literary* work (embodying theme, creating recognition, enabling psychological exploration) even if it's not doing *genre* work (driving plot, creating wonder)?

---

## Named Deep-Dive Flags (with detection logic)

**SFF-DD1: The "Magic Microwave" Problem**
- *Detection:* Magic/tech is used identically every time — same input, same output, no variation, no discovery, no risk. Characters treat it like an appliance.
- *Test:* List every use of the primary speculative element. If 3+ uses follow identical mechanics (cast spell → get result → move on) without variation in cost, risk, context, or emotional register, flag.
- *Threshold:* 3+ identical-pattern uses → flag. 5+ → "Magic Microwave — the speculative element has no texture, just function."
- *Flag:* "Routine Magic — the wonder has been domesticated"
- *Exception:* Progression/LitRPG where mechanical consistency IS the point. Even there, the *emotional* register should evolve.

**SFF-DD2: The "Worldbuilding Orphan" Problem**
- *Detection:* Worldbuilding details introduced with narrative emphasis (long description, character reaction, thematic weight) that never connect to plot, character arc, or theme.
- *Test:* List every worldbuilding detail that receives >50 words of description or explicit character attention. Does each one pay off in plot, character, or theme? If 3+ details are orphaned (introduced with weight, never referenced again), flag.
- *Threshold:* 3+ weighted worldbuilding details with no payoff → flag. 5+ → "Worldbuilding Tourism — the tour guide is showing rooms that don't connect to the story."
- *Flag:* "Orphaned Worldbuilding — this detail was set up but never used"
- *Exception:* Series where details seed future books. If this is Book 1+, note as "Possible Series Seed" rather than flag.

**SFF-DD3: The "Escalation Treadmill" Problem**
- *Detection:* Each new threat is solved by the protagonist gaining a proportionally larger power, creating an arms race with no ceiling.
- *Test:* Plot threat level and protagonist power level across the manuscript. If both escalate in parallel with no point where the protagonist must solve a problem *without* gaining new power, flag.
- *Threshold:* 3+ threat-then-power-up cycles without a scene where the protagonist must use existing resources creatively or accept limitation → flag.
- *Flag:* "Escalation Treadmill — bigger threats met with bigger powers means the relative stakes never change"
- *Exception:* Progression/LitRPG where the treadmill is the genre contract. Even there, at least one crisis should require lateral thinking, not vertical power gain.

---

## Quick Diagnostics Checklist

For rapid assessment, check:

1. **Rule Ledger:** Any "Cost Amnesia" flags?
2. **Integration Test:** Does the Novum pass the "Cellphone Test"?
3. **Sanderson Check:** If soft magic, does it avoid solving the climax?
4. **Social Impact:** Can author name one social structure shaped by the Novum?
5. **Floating Head:** Are scenes grounded in the secondary world?
6. **Power Creep:** Do stakes scale with power?
7. **Retro-Causality:** Does society reflect the Novum's existence?

---

## Integration with Core Framework

This module modifies the following core framework elements:

- **Contract Schema:** Add novum, magic/tech system hardness, cost of power, exposition tolerance, scope, tech level
- **Intake Questions:** Add novum, integration tests, and calibration questions
- **Pass 0:** Add `[EXPOSITION BLOCK]`, `[NEW RULE]`, `[RULE VIOLATION]` tags
- **Pass 1:** Add orientation, floating head, and rule clarity tracking
- **Pass 4:** Add wonder axis; power-cost emotional check
- **Pass 5:** Add competence-cost inventory; detect power without psychology
- **Pass 6:** Add double-duty check for exposition scenes
- **Pass 8:** Add worldbuilding reveal cadence tracking
- **Pass 9:** Add thematic integration check for speculative elements
- **Pass 10:** ELEVATED TO PRIORITY—Rule Ledger Protocol for physics engine verification

All other passes run as specified in core framework.

Can be combined with:
- **Literary Fiction:** For literary SF/F (speculative element as thematic lens)
- **Horror:** For SF/F horror (cosmic horror, body horror, techno-horror)
- **Romance:** For romantasy (romance + epic fantasy)
- **Thriller:** For techno-thriller or SF-thriller hybrids

---

*This module provides diagnostic tools for Science Fiction and Fantasy manuscripts. It calibrates the core framework for genre-specific expectations while maintaining the firewall: the system diagnoses structure; the author invents content.*
