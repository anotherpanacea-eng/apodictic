# Specialized Audit: SFF Worldbuilding Integration
## Version 0.4.8
*Last Updated: February 2026*
*Synthesis: Three-model collaboration (Opus, Codex, Gemini)*

---

## Purpose

This audit evaluates whether a manuscript's speculative worldbuilding does narrative work — integrating with character cognition, thematic architecture, prose texture, and social dynamics — or whether the world, however internally consistent, remains detached from the storytelling.

**The core problem is not inconsistency. It is inertness.** The genre module catches worlds that contradict themselves. This audit catches worlds that don't *matter* — worlds where the speculative element could be swapped for a different one without changing the characters, themes, or emotional experience. A magic system can be elegant and irrelevant. A society can be detailed and dramatically inert. A technology can be original and thematically transparent.

The audit's fundamental question: **Does this world generate story that couldn't exist without it, or is it set dressing for a plot that could happen anywhere?**

The structural insight that anchors this audit: **A world designed as a system but never connected to character cognition is structurally identical to a character designed as a backstory but never connected to scene behavior.** In both cases, the work was done — the system is elegant, the backstory is detailed — but it exists in the author's notes, not in the reader's experience. The mechanism works; it just doesn't matter.

This pattern has cross-genre isomorphisms that make the failure legible to authors who don't write SFF: a magic system treated purely as an engineering problem is to worldbuilding what a romance treated purely as a plot device is to characterization — the mechanism works, but it generates no meaning. A native character who notices their own world for the reader's benefit is the worldbuilding equivalent of the Maid and Butler dialogue flaw. A character with Earth-default psychology in an alien world is the worldbuilding equivalent of the Personality Transplant — their inner life serves the author's convenience rather than their lived reality.

This is a craft audit. It does not penalize simple or soft worldbuilding. It does not require hard magic systems, detailed histories, or encyclopedic scope. It measures whether worldbuilding at *whatever depth level* it operates is doing narrative work.

**Relationship to the Genre Module: SF/F**
The genre module handles consistency: Rule Ledger, Cost Matrix, Sanderson's Laws, Power Creep, Retro-Causality. Run the genre module first. This audit takes consistency as baseline and asks the next question: **now that the world holds together, does it matter?**

The genre module's existing integration tests (Cellphone Test, Salt vs. Meal, Social Impact Test) overlap with this audit's territory. This audit extends them from quick checks to systematic diagnostics.

**When to activate:**
- Any SF/F manuscript (run alongside the genre module)
- Work where beta readers say "cool world but I don't care about the characters"
- Work where the speculative element feels like an obligation rather than a source of energy
- Work where worldbuilding is well-designed but doesn't seem to change anything
- Any time an author asks "I've built this whole world — why doesn't my story feel like it's *in* it?"

**Stacking protocol:**
1. Run SF/F genre module first.
2. Import Rule Ledger, Salt vs Meal, Social Impact, and exposition tag outputs.
3. Run this audit.
4. Feed synthesis into Pass 11.

---

## The Integration Framework

Worldbuilding integration is not binary. A world doesn't simply "integrate" or "not integrate." Integration varies by *dimension* and by *location in the manuscript*. A world might integrate beautifully with plot mechanics while failing to integrate with character psychology. It might integrate in Act I (when the world is being established) and collapse in Act III (when plot mechanics take over and the world becomes backdrop).

### Five Integration Dimensions

Each dimension represents a way the speculative element can enter (or fail to enter) the narrative. A fully integrated world operates across all five. Most manuscripts are strong in one or two and weak in others.

**1. Cognitive Integration (WC)**
Characters think like people shaped by this world. Their assumptions, metaphors, risk models, and decision logic reflect the reality they inhabit — not the reality the author inhabits. A character raised in a world with casual telepathy doesn't just *use* telepathy; her conception of privacy, lying, intimacy, and selfhood is different from ours. A character in a post-scarcity economy doesn't just have access to resources; his anxiety architecture is different — scarcity of meaning, not scarcity of food.

*Integrated:* Character cognition is world-specific. Her metaphors come from her reality. His reflexive fears are shaped by what's actually dangerous here. Problem-solving approaches reflect this world's available tools and constraints.

*Detached:* Characters are Earth minds in alien bodies — 21st-century psychology with the nouns swapped out.

**2. Thematic Integration (TI)**
The speculative element generates dilemmas and meanings that couldn't exist without it. The theme is not generic (power corrupts, love redeems, war is hell) with SF/F wallpaper — it's a theme that *requires* this world's specific constraints.

*Integrated:* Remove the speculative element and the theme collapses. Le Guin's *Left Hand of Darkness* can't explore what it explores without ambisexuality. Chiang's "Story of Your Life" can't exist without the heptapods' simultaneity. The world doesn't illustrate the theme — it generates it.

*Detached:* The theme could exist in a contemporary literary novel. The speculative element adds spectacle but not meaning.

**3. Prose Integration (PL)**
The world enters the texture of the writing — sensory language, metaphor, cognitive framing, rhythm — not just the plot mechanics. The prose *thinks in* this world.

*Integrated:* Miéville's *The City & The City* enacts its dual-city premise in syntax. Okofor's *Binti* carries the Himba protagonist's cultural cognition in the prose's sensory focus. Delany's SF sentences are dense with speculative implication at the word level.

*Detached:* The prose could belong to a literary novel set on Earth with the SFF-specific nouns swapped out. Description passages paint the world; action and dialogue passages forget it.

**4. Social Integration (SI)**
The speculative element creates social structures that produce genuine dramatic friction — not just "there are guilds" but conflicts, costs, and impossible choices rooted in how this society works.

*Integrated:* Martine's *A Memory Called Empire* — the Teixcalaanli Empire's aesthetic colonialism generates the protagonist's central dilemma: she *loves* the empire that is destroying her people. The social structure doesn't just constrain her; it shapes her desires. Butler's *Parable of the Sower* — social collapse is the problem itself, not a backdrop to a different problem.

*Detached:* Political systems, hierarchies, religions, and economies are described but don't produce friction in scenes.

**5. Emotional Integration (EI)**
The world shapes what characters feel, fear, desire, and grieve. The emotional landscape is specific to this reality, not generic human affect in exotic circumstances.

*Integrated:* Jemisin's Essun grieves like someone who has learned that the world periodically ends — her grief carries the weight of cyclical catastrophe. Fear in a world with resurrection should feel different from fear in a world without it. The emotions are world-specific.

*Detached:* Characters feel standard-issue emotions without those emotions being *colored by* the specific reality they inhabit.

### Integration Levels

Rate each dimension using these operational definitions:

| Level | Meaning |
|---|---|
| **Integrated** | Dimension repeatedly alters choices, stakes, and interpretation in high-load scenes |
| **Partial** | Dimension appears intermittently, often front-loaded or context-limited |
| **Detached** | Dimension functions as surface description or mechanism only |

### The World Pressure Loop

Use this causal chain to locate where integration breaks:

1. Rule/novum state →
2. Social translation →
3. Cognitive uptake →
4. Decision under pressure →
5. Consequence and meaning →
6. Prose encoding

Repeated failure at any link is an integration failure candidate. The loop reveals *where* the chain breaks — a world can translate socially (guilds exist, factions matter) but fail at cognitive uptake (characters don't think like guild members), or succeed through decision but fail at prose encoding (the prose forgets the world during action).

---

## Named Diagnostic Flags

Each flag identifies a specific pattern of integration failure. Flags can co-occur. Severity depends on frequency, pattern, and the manuscript's implied contract.

### World-Character Integration Flags (WC)

**WC-1: "Earth Minds in Alien Bodies"**
Characters live in a world that should fundamentally shape their cognition but think like 21st-century Westerners. Their metaphors, oaths, casual references, risk models, and habitual thoughts all come from our world rather than theirs. This is the worldbuilding equivalent of the Personality Transplant — the character's inner life serves the author's convenience rather than their lived reality.
- *Detect:* Catalog the character's metaphors and habitual thought patterns. How many are world-specific vs. Earth-default? Does she use timekeeping, measurement, or emotional language specific to this reality?
- *Default severity:* Should-Fix. Must-Fix if protagonist in a world with major cognitive differences.

**WC-2: "The Tourist"**
Characters notice and describe their own world in ways that serve the reader but wouldn't occur to someone who grew up there. Internal monologue reads like a travel guide. Characters marvel at things that should be mundane to them.
- *Detect:* In character POV, flag every observation that a native wouldn't make. Compare with immersive-mode exemplars where the world is simply *there*.
- *Default severity:* Should-Fix. Must-Fix if the governing rhetoric is immersive (Mendlesohn).

**WC-3: "Wallpaper Competence"**
A character's professional or magical skills are load-bearing for the plot but don't shape how she *thinks*. She uses magic/technology as a tool without it entering her cognitive life — no world-specific problem-solving instincts, no habitual perception shifts, no professional deformation from years of practice.
- *Detect:* Does the character think *through* her abilities or just *with* them? If her abilities could be replaced with a different skill set without changing her psychology, the competence is wallpaper.
- *Default severity:* Should-Fix. Must-Fix if the ability is the character's defining trait.

**WC-4: "The Undeformed"**
Characters who have lived through world-specific experiences show no psychological marks. Their interiority doesn't carry the world's weight.
- *Detect:* Identify world-specific experiences in the character's backstory. Do these experiences surface in present-tense psychology — in flinches, avoidances, assumptions, or reflexes?
- *Default severity:* Should-Fix. Must-Fix for protagonist or when the world-specific experience is central to the plot.

### Exposition Craft Flags (EC)

**EC-1: "The Wiki World"**
The world has extraordinary depth — history, languages, political structures — but this depth enters the manuscript primarily through exposition rather than dramatic action. The worldbuilding was developed as a separate creative act and then *reported* rather than *integrated*.
- *Detect:* For each major worldbuilding element, find scenes where a character must *navigate* it under pressure. If most worldbuilding enters through explanation rather than navigation, the wiki hasn't become a world.
- *Default severity:* Should-Fix. Must-Fix if exposition-to-navigation ratio exceeds 3:1 for load-bearing elements.

**EC-2: "Exposition Rigor Mortis"**
Worldbuilding information is delivered without technical error — no infodumps, no As-You-Know-Bobs — but the exposition is *experientially dead*. It reads like well-written reference material. The reader learns facts without experiencing the world.
- *Detect:* Read exposition passages aloud. Do they carry emotional charge — fear, wonder, resentment, longing — or are they affectively neutral?
- *Default severity:* Should-Fix. Could-Fix if confined to early chapters where information density is necessary.

**EC-3: "The Mode Mismatch"**
The narrative's governing rhetoric (Mendlesohn) says one thing; the exposition strategy says another. Immersive fantasy with portal-quest exposition. Portal-quest without wonder. Intrusion domesticated by over-explanation.
- *Detect:* Identify the governing mode. Does immersive fantasy have characters explaining their world to each other? Does portal-quest skip the protagonist's discovery experience? Does intrusion fantasy explain the intrusion until it's no longer strange?
- *Default severity:* Must-Fix. Mode mismatch is structural.

**EC-4: "Late-Stage Explaining"**
Worldbuilding exposition density *increases* in the final act. New rules, history, or social structures are introduced to service the climax rather than being seeded earlier.
- *Detect:* Track exposition density by act. If Act III has more worldbuilding explanation than Act I, the world is being retrofitted to the plot rather than generating it.
- *Default severity:* Should-Fix. Must-Fix if new exposition is required to understand the climax.

### Thematic Integration Flags (TI)

**TI-1: "The Cellphone-Proof Theme"**
*(Extends genre module's Cellphone Test from system-level to theme-level.)* The speculative element is load-bearing for plot mechanics but not for thematic meaning. The theme could exist in a contemporary literary novel.
- *Detect:* State the manuscript's central theme in one sentence. Remove the speculative element. Does the theme survive intact? If yes, the world is thematically transparent.
- *Default severity:* Should-Fix if the contract promises thematic integration. Could-Fix if the contract is primarily adventure.

**TI-2: "The Passive Physics Engine"**
The world's rules accommodate the narrative rather than constraining it. The magic system has costs, but the costs never force a genuinely difficult choice between values. Game-design balance rather than dramatic friction.
- *Detect:* For each major system rule, find moments where it forces a character into a *worse* choice than they'd face without it. If the rules create tactical puzzles but not genuine dilemmas, the system is dramatic inert.
- *Default severity:* Should-Fix. Must-Fix if the system is positioned as central to the plot.

**TI-3: "Generic Dilemma in Exotic Dress"**
The protagonist faces a dilemma that the narrative frames as world-specific but that could exist without the speculative element. The power struggle could be a corporate drama. The forbidden love could be a class conflict.
- *Detect:* Translate the protagonist's central dilemma into a non-SFF equivalent. If the translation is easy and lossless, the dilemma is generic in exotic dress.
- *Default severity:* Could-Fix if execution is strong. Should-Fix if the manuscript markets its premise as original.

**TI-4: "Climax Decoupling"**
Final resolution does not materially depend on world architecture. The climax is portable to a non-speculative setting with minor edits.
- *Detect:* Strip the speculative element from the climax. Does the emotional and thematic resolution survive? If the novum functions as delivery mechanism rather than determinant, the climax is decoupled.
- *Default severity:* Must-Fix. A decoupled climax means the world was never load-bearing where it matters most.

### Scale and Depth Flags (SD)

**SD-1: "The Aesthetic Shell"**
The world is richly described — sensory detail, architectural specificity, environmental texture — but the descriptions are decorative rather than constitutive. The prose *paints* the world without the world entering the prose's *logic*.
- *Detect:* Compare description passages with action/dialogue passages. Does the world vanish when characters interact with each other? If the world is present only during scene-setting, it's a shell.
- *Default severity:* Should-Fix. Could-Fix if the contract is primarily action/adventure.

**SD-2: "Social Architecture Without Social Physics"**
Political systems, hierarchies, religions, and economies are detailed and consistent, but they don't produce friction in actual scenes. Characters describe the caste system; nobody faces a scene where caste loyalty conflicts with personal desire.
- *Detect:* For each major social structure, find scenes where a character must *choose* between what the structure demands and what they personally want.
- *Default severity:* Should-Fix. Must-Fix if the social structure is marketed as a defining element.

**SD-3: "The Load-Bearing Wall That Isn't"**
A worldbuilding element is given substantial page time and exposition but turns out not to be structurally necessary. Remove it and the plot, theme, and characterization survive intact. Decorative complexity — detail that is consistent, interesting, and irrelevant.
- *Detect:* For each worldbuilding element that receives significant exposition, apply the removal test: what breaks if this element disappears?
- *Default severity:* Could-Fix if decorative elements are brief. Should-Fix if they consume significant page time.

**SD-4: "Scope Inflation Drift"**
World scope expands faster than integration depth. New regions, factions, or systems introduced without corresponding character or thematic uptake.
- *Detect:* Track the ratio of world elements introduced vs. world elements that produce consequence. If expansion events outpace consequence tracking, scope is inflating without integration deepening.
- *Default severity:* Could-Fix isolated. Should-Fix patterned. Common in epic fantasy and space opera series.

### Prose-Level Flags (PL)

**PL-1: "The Noun-Swap World"**
The prose could belong to a literary novel set on Earth with the SFF-specific nouns swapped out. Sentence rhythm, metaphor structure, sensory focus, and cognitive framing are all genre-agnostic. The world exists in the vocabulary but not in the grammar.
- *Detect:* Replace all SFF-specific nouns with Earth equivalents. Does the prose read exactly the same? If the sentences don't change their *logic* — only their content — the world hasn't entered the prose.
- *Default severity:* Should-Fix. Could-Fix if the contract doesn't promise immersive worldbuilding.

**PL-2: "Description Island"**
Worldbuilding enters the prose only in dedicated description passages. Between descriptions, the narrative could be set anywhere. The world appears, is described, and then retreats.
- *Detect:* Highlight every sentence that carries world-specific information. Are they clustered in blocks or distributed throughout action, dialogue, and interiority? Clustering indicates the world is being *reported on* rather than *inhabited*.
- *Default severity:* Should-Fix. Could-Fix if confined to early chapters in portal-quest mode.

**PL-3: "Register Reversion"**
Narrative voice reverts to explanatory modern-default register under pressure. Established diction and cadence shift to tutorial voice in key scenes.
- *Detect:* Compare voice in world-establishment scenes vs. climactic or high-stress scenes. If the prose loses its world-situated register when the stakes rise, the voice is reverting.
- *Default severity:* Could-Fix isolated. Should-Fix patterned.

**PL-4: "Metaphor Import Leak"**
Figurative language repeatedly imports conceptual frames incompatible with world ontology. Metaphors rely on absent technologies, histories, or institutions.
- *Detect:* Catalog metaphors and similes. How many reference concepts that shouldn't exist in this world? A character in a pre-industrial setting who "feels like a machine" is importing a frame from elsewhere.
- *Default severity:* Could-Fix isolated. Should-Fix repeated.

---

## Tracking Artifacts

### Artifact A: Integration Map (required)

Track integration across five dimensions at the act level. This is the audit's primary evidence artifact. Do not issue final severity without it.

| Dimension | Act I | Act II-A | Act II-B | Act III | Notes |
|-----------|-------|----------|----------|---------|-------|
| Cognitive (WC) | I / P / D | I / P / D | I / P / D | I / P / D | |
| Thematic (TI) | I / P / D | I / P / D | I / P / D | I / P / D | |
| Prose (PL) | I / P / D | I / P / D | I / P / D | I / P / D | |
| Social (SI) | I / P / D | I / P / D | I / P / D | I / P / D | |
| Emotional (EI) | I / P / D | I / P / D | I / P / D | I / P / D | |

Key: I = Integrated, P = Partial, D = Detached

**Reading the Map:**
- **Consistent I across all dimensions and acts** → Fully integrated world. Rare and excellent.
- **Strong in Act I, weakening through Acts II–III** → The Establishment Fade. The most common pattern: world was built and then abandoned.
- **Strong on Cognitive and Social, weak on Prose and Emotional** → The Intelligent Shell. The world shapes what characters *do* but not what the *prose feels like* or what the *characters feel*.
- **Strong on Prose and Emotional, weak on Thematic and Social** → The Atmospheric World. The world *feels* present but doesn't *mean* anything. Beautiful but empty.
- **D across Act III** → The Climax Collapse. The ending disconnects from the world. Frequently a plot-priority problem.

### Artifact B: Load-Bearing Ledger (required)

| World Element | First Seen | Plot Load | Cognition Load | Theme Load | Prose Load | Social Load | Classification |
|---|---|---|---|---|---|---|---|
| Element ID | Ch/Scene | Y/N + where | Y/N + where | Y/N + where | Y/N + where | Y/N + where | Load-Bearing / Semi / Decorative |

Classification rule:
- **Load-Bearing** = influences at least 3 load columns, including one of Cognition, Theme, or Social.
- **Semi** = influences 2 columns.
- **Decorative** = influences 0–1 column.

### Artifact C: Pressure Event Log (optional)

Recommended for action-heavy or suspected late-collapse manuscripts.

| Pressure Event | Unit | World Constraint Active? | Value Conflict Triggered? | Emotional Cost Tracked? | Flags |
|---|---|---|---|---|---|
| Event ID | Ch/Scene | Y/N | Y/N | Y/N | Codes |

### Pattern Interpretation Protocol

After artifacts are complete, run:
1. **Act Drift Check:** Are Detached ratings rising in Act III?
2. **Channel Concentration Check:** Which dimensions fail most?
3. **Climax Integrity Check:** Are WC and TI Integrated at climax?
4. **Contract Fit Check:** Does observed depth match meal/salt promise?
5. **Distribution Check:** Isolated vs. clustered vs. systemic.

---

## The Distinguish Framework

Not all simple worldbuilding is a failure. *Star Wars* doesn't need a functioning economy. *Nineteen Eighty-Four* doesn't need plausible technology. Some of the best SFF keeps worldbuilding deliberately thin to serve other priorities. The audit must tell the difference.

### Intentional Simplicity (not a problem)

**Strategic minimalism.** The world is simple because depth would dilute the story's focus. *Star Wars* doesn't explain the Force's mechanics because mystery is the point. But if you remove the Force, Luke's arc collapses — the worldbuilding is simple but load-bearing.

**Allegory.** The world maps onto something outside itself. Simplicity serves the mapping. *Animal Farm* is thin as world but rich as argument.

**New Weird / Surrealist modes.** The world resists systematization by design. Contradiction and impossibility are the meaning.

**Formal constraint.** Short fiction, novellas, or compressed works that lack space for deep worldbuilding. Chiang's stories are world-minimal but integration-maximal.

**Discovery draft.** The author is finding the world as they write. Worldbuilding will deepen in revision.

### Integration Failure (problem)

- The author built a system but didn't connect it to character cognition
- The world was designed in a wiki and reported rather than integrated
- Characters inhabit the world physically but not psychologically
- The speculative element creates tactical problems but not human dilemmas
- Social structures are described but never produce friction
- **Silent Disengagement:** The world is present early and absent late, without narrative justification

### The Six Distinguish Tests

1. **Swap Test:** Replace the novum. Does arc, theme, and climax survive nearly intact? If yes → integration failure.
2. **Contract Depth Test:** Compare observed integration depth to promised subgenre burden. If under-integrated for contract → failure.
3. **Inhabitation Test:** Do characters think, speak, and prioritize as inhabitants, not tourists?
4. **Load-Bearing Test:** Remove key world elements. What collapses? If nothing → decorative.
5. **Pressure Test:** Does integration hold or disappear under high stress?
6. **Friction Test:** Do institutions force value tradeoffs, not just scenery?

### Decision Matrix

| Test profile | Classification | Action |
|---|---|---|
| Swap fails, load-bearing strong, pressure stable, contract met | Intentional Minimalism / Non-System Mode | Pass with calibration note |
| Mixed tests, partial load, localized drift | Discovery-State / Ambiguous | Targeted Could/Should flags, focused revision |
| Swap passes, load-bearing weak, inhabitation low, pressure collapse | Integration Failure | Should/Must by hard gates |

### False-Positive Guardrails

Before calling systemic failure, confirm:
1. You did not apply hard-SF standards to soft/literary contracts.
2. You assessed patterns across acts, not single weak sections.
3. You measured people-level consequence, not only lore elegance.
4. Ambiguity is evaluated for pattern and effect, not penalized by default.

### Special Caution Zones

Require stronger evidence before calling systemic failure:
- **Series Book 1** — worldbuilding may be deliberately withheld for later volumes. Check for seeds vs. gaps.
- **Discovery drafts** — flag for development, not as defect.
- **Cross-genre work** where SFF is subordinate — calibrate to the primary genre's contract.
- **Unreliable narrators** — the character's incomplete understanding of the world may be the point.

---

## Severity Hard Gates

These gates improve reproducibility. If triggered, minimum severity applies regardless of local strengths.

**Gate 1: Climax Load-Bearing Failure**
Trigger: TI-4 fires and climax-critical world element is Decorative or Semi in ledger.
Minimum severity: Must-Fix (Systemic).

**Gate 2: Protagonist Inhabitation Failure**
Trigger: WC-1/WC-3/WC-4 appear in more than 40% of protagonist high-pressure units.
Minimum severity: Must-Fix.

**Gate 3: Act-III Channel Collapse**
Trigger: 2+ dimensions move to Detached in Act III after being Integrated or Partial in Acts I–II.
Minimum severity: Should-Fix. Upgrade to Must-Fix if climax units are affected.

**Gate 4: Late Explain Patch Cluster**
Trigger: EC-4 appears 2+ times in final 20% and ties to payoff-critical logic.
Minimum severity: Must-Fix.

**Gate 5: Meal Contract Dilemma Failure**
Trigger: Salt vs Meal = Meal, and both TI-2 and TI-3 recur across all acts.
Minimum severity: Must-Fix.

**Gate 6: Social Zero-Friction**
Trigger: SI Detached in more than 60% of map units while institutions are contract-significant.
Minimum severity: Should-Fix.

**Gate 7: Decorative Majority**
Trigger: More than 50% of ledger elements are Decorative and SD-1/SD-3 fire.
Minimum severity: Should-Fix.

**Gate 8: Full Swap Persistence**
Trigger: Swap Test passes for protagonist arc, primary theme, and climax mechanics.
Minimum severity: Must-Fix for meal-level, Should-Fix for salt-level.

---

## Subgenre Calibration

Each subgenre promises a different depth and type of worldbuilding integration. What counts as integration failure in hard SF may be working-as-intended in space opera. Calibrate severity accordingly.

| Subgenre | Named Risk | Tighten On | Loosen On |
|----------|-----------|------------|-----------|
| Hard SF | The Elegant Irrelevance | WC, TI, SI, climax dependence | Sparse lyricism per se |
| Space Opera | The Grand Tour | SI, TI, faction consequence | Strict realism physics |
| Epic Fantasy | The Appendix Illusion | SI, WC, EI, ritual consequence | Slow setup density |
| Urban Fantasy | The Convenient Masquerade | SI, WC, constraint consequences | Voice-forward pacing |
| Cyberpunk | Neon Skin, No Bite | TI, SI, institutional bite | Endings that are not revolutionary |
| New Weird | Randomness Alibi | Pattern coherence, EI, TI | Full rule codification |
| Literary SFF | Metaphor Cage | TI, WC, climax meaning | Mechanics explicitation burden |
| Progression/LitRPG | The Stat Sheet Treadmill | WC, EI, cost conversion | Stat language density |

### Genre Notes

**Hard SF** — The science doesn't need to be the theme, but it does need to enter the *experience of being this character*. A protagonist solving orbital mechanics should feel the physics in her bones — the weight of limited delta-v, the terror of miscalculation. If the science is just a puzzle to solve, the world hasn't integrated with the character. Named risk: **The Elegant Irrelevance** — rigorous science that is technically fascinating and emotionally disconnected.

**Space Opera** — The galaxy is allowed to be a playground. But even playgrounds have rules, and the best space opera makes those rules matter. The Expanse works because the Belt's physics generate the Belt's politics generate the Belt's people. When worlds are big and empty, the Grand Tour has started. Named risk: **The Grand Tour** — impressive worlds that the protagonist moves through without being constrained by.

**Epic Fantasy** — A magic system that generates tactical problems but not human dilemmas is to epic fantasy what competence without cost is to characterization — the machinery is running, but nobody's home. The world's history should create moral weight that characters inherit, not just backstory to explain why the factions exist. Named risk: **The Appendix Illusion** — 300 pages of lore and detailed customs, zero moral friction; the history does not pressure the present plot.

**Urban Fantasy** — The masquerade is only interesting if it *costs* something. If the protagonist can use magic openly whenever convenient, the hidden-world premise is decorative. The best urban fantasy makes concealment a source of genuine dilemma — the things you can't tell the people you love. Named risk: **The Convenient Masquerade** — hidden-world rules that don't constrain the protagonist.

**Cyberpunk** — Technology should change what it's like to be *this person*, not just what this person can *do*. Chrome that's purely functional is SFF as gadget fiction. Chrome that changes the character's relationship to memory, embodiment, or identity is cyberpunk doing its job. Named risk: **Neon Skin, No Bite** — aesthetic cyber-surface without structural consequence.

**New Weird** — Ambiguity can pass when patterned and meaningful. Randomness as alibi fails. The world's incomprehensibility should generate cognitive work — wonder, dread, estrangement — not just confusion. Named risk: **Randomness Alibi** — strangeness used to mask absent architecture.

**Literary SFF** — The most common failure is a concept that's intellectually stimulating but emotionally inert. The speculative element needs to press on the character's consciousness, not just sit in the background being interesting. Ishiguro's *Never Let Me Go* works because the clones' situation isn't fascinating — it's devastating. Named risk: **Metaphor Cage** — the novum functions only as metaphor, never entering scene-level consequence.

**Progression/LitRPG** — Progression must alter human stakes, not just numerics. A stat increase that doesn't change what the character fears, wants, or is willing to sacrifice is growth that means nothing. Named risk: **The Stat Sheet Treadmill** — power growth quantified but not meaningful.

---

## Audit Output

### Summary Assessment

Provide:
1. **Integration assessment:** Does the manuscript achieve worldbuilding integration across the five dimensions, or are significant dimensions absent?
2. **Contract alignment:** Does the integration level match the manuscript's genre contract?
3. **Pattern diagnosis:** Where does integration drop? Is the pattern structural (Act III collapse), dimensional (strong cognitive, weak emotional), or localized (specific scenes)?

### Integration Map and Load-Bearing Ledger

Complete one Integration Map for the manuscript. Complete one Load-Bearing Ledger for each major speculative element. These are the audit's primary evidence artifacts. Do not issue final severity without them.

### Flag Inventory

For each triggered flag, provide:
- **Flag code and name** (e.g., WC-1: Earth Minds in Alien Bodies)
- **Location** (scene/chapter/act)
- **Evidence** (specific passage reference, ≤25 words, or structural paraphrase)
- **Severity** (Must-Fix / Should-Fix / Could-Fix)
- **Blast radius** (Local / Multi-scene / Systemic)
- **Pattern note** (isolated instance or systematic?)

### Pattern Analysis

From the Integration Map and flag inventory, identify:
- Does integration follow a temporal pattern (strong early, weak late)?
- Does integration cluster by dimension (cognitive yes, emotional no)?
- Is the speculative element load-bearing for plot only, or for character and theme?
- Is exposition integrated or isolated from dramatic action?

### Recommendations

Stated in abstract structural terms (per editorial firewall):
- "The magic system needs to enter the protagonist's cognitive life — currently it's used but not inhabited."
- "Social structures need scenes of navigation under pressure, not just exposition."
- "Act III worldbuilding integration collapses — the climax should be as world-specific as the opening."

**NOT:** Specific worldbuilding content, new systems, or world-design suggestions. Diagnose structure; don't invent content.

---

## Integration with Core Framework

This audit runs alongside or after:
- **Genre Module: SF/F** — Handles consistency. This audit handles integration. Run the genre module first.
- **Pass 5 (Character Audit):** Deepens character analysis by asking whether characters are *shaped by* the world, not just placed in it.
- **Pass 6 (Scene Function):** Flags scenes whose only function is exposition delivery without dramatic integration.
- **Pass 1 (Reader Experience):** Tracks orientation and immersion — this audit adds integration-specific immersion diagnostics.
- **Pass 10 (Entity & Continuity):** The genre module's Rule Ledger provides data; this audit interprets its narrative significance.

Can be combined with:
- **Female Interiority audit** (craft/) — when world displacement and gendered interior thinning overlap. "The Gender-Swapped Archetype" is an integration failure: the world creates a gendered society but the female character's cognition is gender-neutral.
- **Shelf Positioning audit** (craft/) — worldbuilding integration level affects genre positioning and comp selection.
- **Fantasy & Series Architecture** (plot-architecture/) — structural and integration diagnostics together provide full SFF coverage.
- **Philosophical Tag** (tag/) — for SFF works where the speculative element is primarily a vehicle for ideas.

### Synthesis Handoff

When handing into Pass 11 synthesis, provide:
1. Top 3 integration failures with blast radius.
2. Integration Map act-level summary.
3. Distinguish classification and rationale.
4. Contract-impact statement.

---

## What This Audit Is Not

1. **Not a consistency audit.** The genre module handles whether the rules work. This audit handles whether the rules *matter*.

2. **Not a demand for hard magic systems.** Soft worldbuilding can be fully integrated. The question is whether the world does narrative work at whatever depth it operates.

3. **Not a complexity requirement.** Simple worlds can be deeply integrated. Le Guin's Earthsea is spare. *Star Wars* is simple. The audit measures integration, not volume.

4. **Not a prohibition on worldbuilding-as-backdrop.** Space opera, fairytale fantasy, and other modes where the world is Salt rather than Meal can pass cleanly — if the Salt is doing its job.

5. **Not an originality test.** A familiar world type can be deeply integrated. Originality is a shelf-positioning concern, not an integration concern.

6. **Not a worldbuilding-maximalism checklist.** More worldbuilding is not better worldbuilding. A world with a wiki and no dramatic function for its depth is failing this audit. A world with three rules that generate the entire plot is passing it.

7. **Not a replacement for the genre module.** Consistency and integration are separate concerns. A world can be inconsistent but integrated (the contradictions *mean* something) or consistent but inert (the rules hold but don't generate story). Run both.

8. **Not a penalty for allegory, ambiguity, or weirdness.** The Distinguish protocol protects intentional modes.

9. **Not a prose ideology test.** Functional texture matters; style uniformity is not required.

---

*This audit is designed to bolt onto the APODICTIC development editor framework. Activate during intake when the manuscript is SF/F. Run alongside the Genre Module: SF/F (which handles consistency). File placement: `specialized-audits/references/genre/sff-worldbuilding.md`.*
