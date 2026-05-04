# Specialized Audit: AI-Prose Calibration
## Version 2.0
*Last Updated: May 2026*

---

## Purpose

Diagnose prose-level failure patterns characteristic of AI-generated or AI-assisted text. Provide a salvage plan — priority zones and triage categories — so the author can turn structurally competent but editorially hollow prose into writing that sounds like a person wrote it on purpose.

**Core claim:** AI-generated prose fails in categories, not just surface tells. The categories are more durable than any model's particular tics because they reflect what language models structurally cannot do: inhabit a specific consciousness, make surprising word choices under genuine constraint, or sustain voice across register shifts. Surface tells (em-dash density, hedge phrases, "I couldn't help but") shift every six months. The categories persist.

**The mathematical foundation.** Every working AI-prose detector (Burrows Delta, GLTR, GPTZero, DetectGPT, Binoculars, EditLens, Pangram) measures one underlying asymmetry: human writing occupies a high-variance, long-tailed, multi-modal region of stylometric distributions. RLHF-aligned LLM output occupies a narrower sub-region that overlaps the human mode but conspicuously lacks the tails. Sentence lengths cluster in a band. Readability scores cluster in a band. Function-word ratios converge. Connectives appear at metronome density. The diagnostic question is not "did a machine write this" but "where does this prose lack the irregularity that human consciousness produces by accident."

**Deficit-First Diagnostic Rule:** Do not evaluate AI prose by confirming its grammatical fluency or logical coherence. You must hunt for the *absence* of friction, the *absence* of specificity, and the *absence* of unpredictable consciousness. AI prose fails because it is a velvet fog of competence without consequence. You are auditing for the omission of human interiority.

**What this audit is:** A prose-level diagnostic overlay. It identifies where AI-generated text fails as *writing* — not where it fails as *imitation*. The question is never "did a machine write this?" The question is: "Where does this prose lack the specificity, friction, and voice that make a reader trust the narrator?"

**What this audit is not:** A provenance detector. It does not guess which model produced which passage. It does not flag text as "AI" or "human." It diagnoses symptoms on the page. A human writer who produces voice-flattened, generically fluent prose will trigger the same flags — and benefit from the same salvage plan.

**When to activate:**
- Writer identifies the draft (or portions) as AI-generated or AI-assisted
- Contract intake records mixed drafting methods (human + one or more LLMs)
- Pass 1 (Reader Experience) flags uniform fluency without friction, "competent but soulless"
- Pass 5 (Character Audit) flags psychological coherence without psychological specificity
- Pass 7 (Voice/POV) Blind Swap test shows voices are interchangeable across characters *and* across chapters
- Emotional Craft audit finds meaning pipeline consistently intact but producing generic output — correct structure, wrong texture
- Author or beta readers report "it reads like AI" or "it feels samey"

**When NOT to activate:**
- The manuscript has severe structural problems (no spine, incoherent plot). Fix structure first; prose calibration on a structurally broken manuscript wastes effort.
- The prose problems are isolated craft weaknesses (weak verbs, passive voice, show-don't-tell) without the *pattern* of unearned fluency. Standard passes and Emotional Craft audit cover single-axis craft problems. This audit adds value when multiple AIC categories co-occur — the signature is systemic uniformity, not individual weakness.
- The writer is using AI for brainstorming/outlining only, not prose generation. The pre-writing pathway handles this.

**Provenance-agnostic activation:** This audit triggers on symptoms, not on drafting method. If a human-written manuscript exhibits voice singularity, echo stacks, and velvet fog simultaneously, the audit is useful regardless of origin. The "When to activate" triggers above are symptom-based for this reason. The contract intake question about drafting method is a *convenience trigger* (it predicts which manuscripts are likely to exhibit the patterns), not a gate.

---

## Vocabulary

### Unearned Fluency

Prose that reads smoothly without having earned that smoothness through specificity, voice, or structural pressure. The sentences are grammatically competent, the paragraphs transition logically, the rhythm is consistent — and none of it required a human consciousness to select these particular words in this particular order. The hallmark: you can swap any sentence with a paraphrase and lose nothing.

Unearned fluency is the meta-category. The seven flag families below are its specific manifestations.

### Voice Singularity

A manuscript that reads as though one consciousness wrote every character, every scene, every register. No variation in sentence rhythm across POV characters. No shift in diction between intimate scenes and action scenes. No idiosyncrasy. The narrator has no personality — only competence.

Distinguished from **consistent voice** (a deliberate authorial choice, where the narrator's personality is the consistency) and from **close third** (where voice should shift with POV character). Voice singularity is the absence of choice, not a style.

### Lexical Genericism

Word choices that are accurate but never specific. "She felt a wave of sadness" instead of anything a particular person in a particular moment would think or feel. The prose selects from the center of each word's semantic field — never the edge, never the wrong word used right, never the word that makes the reader pause and recalibrate.

### Register Seam

A detectable shift in prose quality, vocabulary level, or stylistic confidence that correlates with a change in drafting method or model. Common in manuscripts assembled across multiple LLM sessions or mixed human/AI drafting. The seam may be between chapters, within a chapter, or between dialogue and narration.

Not all register shifts are seams. Intentional register shifts (formal narration dropping into colloquial interiority, for example) serve the prose. Register seams serve nothing — they're artifacts of production, not choices of craft.

### Echo Stack

Repetitive structural patterns at the sentence, paragraph, or scene level that the writer didn't choose. Sentence echo: three consecutive sentences with identical syntax (Subject → Verb → Object → Prepositional phrase). Paragraph echo: every paragraph opens with a topic sentence and closes with a transition. Scene echo: every scene opens with setting, moves to dialogue, ends with internal reflection. The pattern is correct but mechanical — a template applied, not a rhythm felt.

### Puppet Dialogue

Dialogue where every character speaks in the same register, at the same intelligence level, with the same sentence complexity. Characters take turns delivering information or advancing plot. No one interrupts, misunderstands strategically, uses language as a weapon, or reveals themselves through what they *won't* say. The characters are mouths for the narrative, not people in a room.

Distinguished from **functional dialogue** (where the writing is sparse by design, as in Hemingway or Carver). Puppet dialogue isn't spare — it's uniform. Functional dialogue is a specific voice; puppet dialogue is the absence of one.

### Continuity Smear

Failures of physical, temporal, or causal continuity that result from generating text without maintaining a persistent world model. A character holds a glass that was set down two paragraphs ago. The sun sets twice. A conversation references information that hasn't been revealed yet. A character reacts to an event that happened in a different draft version.

Distinguished from **ordinary continuity errors** (which human writers make too) by density and type. AI continuity smear tends to cluster around entity states (what characters are holding, wearing, positioned relative to each other) and temporal sequence (how much time has passed, what happened in what order). Human continuity errors tend to be about factual consistency across long stretches.

### Discourse Leak

Prose in which characters, narrators, or the text itself organizes thought the way a language model does rather than the way a person in that situation would. The tell is not bad prose — it's the wrong *kind* of fluency. A character who hedges like a chatbot. A narrator who throat-clears before a revelation. Interiority that proceeds through rhetorical correction ("Not grief, exactly — something closer to recognition") at a frequency no actual mind sustains. Descriptive passages that group attributes in threes because the generating model defaults to triples, not because the rhythm earns it.

Discourse leak differs from the other flag families in what it targets. AIC-1 through AIC-6 diagnose failures of craft — the prose lacks voice, specificity, embodiment, variation, or continuity. Discourse leak diagnoses a failure of *register*: the prose has imported the organizational habits of an assistant into the voice of a narrator or character. The words may be fine. The way they're arranged reveals the wrong speaker.

Distinguished from **rhetorical sophistication** (an educated narrator who genuinely thinks in correctio/epanorthosis or epistemic qualification) by frequency and context. A philosophy professor character who hedges is in character. The same hedging in a twelve-year-old's interiority is discourse leak. A narrator who uses correctio once for emphasis is making a choice. The same figure appearing every third paragraph is a generating habit.

### Scene Fog

Scenes that proceed through dialogue and interiority without grounding the reader in physical reality. Characters talk in unspecified spaces. Actions happen without bodies. The world exists as concept, not as sensory experience. The prose can describe a room if prompted but doesn't *notice* the room the way a character with a body and a history would.

Distinguished from **minimalist staging** (deliberate sparseness, as in Beckett or certain literary fiction) by the absence of selectivity. Minimalist staging chooses what to omit; scene fog simply doesn't generate the physical world unless forced.

---

## Relationship to Existing Passes

This audit does not duplicate existing infrastructure. It adds a diagnostic lens that connects findings other passes produce in isolation.

**Pass 1 (Reader Experience) flags the symptom; this audit names the mechanism.** Pass 1 catches "competent but flat," "nothing distinctive," "I kept reading but didn't care." This audit explains why: the prose has unearned fluency, and here are the specific failure categories present.

**Pass 5 (Character Audit) catches the psychology problem; this audit catches the prose problem.** Pass 5's psychology engine and agency tracking identify whether characters have coherent internal logic. AI-generated characters often pass the psychology check — their motivations are consistent, their arcs are complete — but their interiority reads as a case study rather than a lived experience. This audit flags the prose-level manifestation: psychological coherence without psychological *specificity*.

**Pass 7 (Voice/POV) detects interchangeable voices; this audit diagnoses why.** The Blind Swap test from Character Architecture identifies when characters sound alike. This audit provides the mechanism: voice singularity (one generating consciousness) and puppet dialogue (characters as information conduits rather than people with speech patterns).

**Emotional Craft audit diagnoses emotional transmission; this audit diagnoses the texture.** The meaning pipeline can be structurally intact — perception → interpretation → judgment → impulse → choice — while every element in the chain is generic. This audit catches that gap: correct pipeline, wrong words.

**Scene Turn audit checks mechanics; this audit checks embodiment.** Scene Turn verifies that scenes have goals, conflicts, and outcomes. This audit checks whether those scenes happen in a physical world with sensory specificity, or whether they float in scene fog.

---

## Scope Selection

### Default Scope: 3 Passages

Select three passages that represent different conditions:

| Passage | What to pick | Why |
|---------|-------------|-----|
| **A: Dialogue-heavy** | A conversation scene with 2+ characters | Tests puppet dialogue, voice singularity, register consistency |
| **B: Interiority-heavy** | A passage of internal reflection, aftermath, or bridge scene | Tests lexical genericism, emotional specificity, unearned fluency |
| **C: Action or transition** | A scene with physical movement, setting, or time passage | Tests scene fog, continuity smear, echo stack |

If the writer identifies specific passages as AI-generated or as problematic, substitute those for one or more of the defaults.

### When to Expand Scope

- If all three passages show the same flag families → the problem is manuscript-wide; expand to a contamination map (see Output)
- If passages show different flags → the issue may correlate with drafting method; check whether flag clusters align with production history
- If the writer reports mixed human/AI drafting → select one passage from each drafting method for comparison

### Contamination Map

When the audit expands beyond sample passages, produce a chapter-by-chapter (or section-by-section) map:

```
Chapter/Section | Dominant Flags | Severity | Notes
[1]             | AIC-1, AIC-5  | High     | Dialogue scenes uniformly puppet
[2]             | AIC-2         | Medium   | Bridge scene fog, action grounded
[3]             | (clean)       | Low      | Human-drafted section per author
...
```

The map is a *diagnostic tool*, not a score sheet. Its purpose is to show the writer where to focus salvage effort.

---

## Layer A Pre-Scan (Optional Computational Support)

A computational pre-scan can sharpen scope selection and surface manuscript-wide patterns the manual flag scan would catch only by accident. Run when the manuscript is large enough that sample-passage selection might miss systemic compression, or when the writer reports lexical compression that's hard to localize.

The pre-scan is *additive*. It does not replace the manual flag scan, the source triage step, or the salvage plan. It supplies stylometric magnitudes that predict which AIC flags will fire and which chapters deviate most from the writer's own baseline.

**See `ai-prose-calibration-distributional.md` for the full Layer A reference.**

### What Layer A measures

Eleven variance signals against a personal baseline (the writer's own prior unedited work) or against a genre baseline:

- Sentence-length variance and burstiness B = (σ − μ)/(σ + μ)
- Lexical diversity: MATTR (moving-average TTR), MTLD, Yule's K
- Shannon entropy of token distribution
- Per-sentence Flesch-Kincaid Grade Level standard deviation
- Adjacent-sentence cosine similarity (mean and SD)
- Function-word distribution (Burrows' Delta against baseline)
- POS-bigram KL divergence against baseline
- Mean Dependency Distance variance
- Connective density (explicit discourse markers per 1000 tokens)
- Function-word ratio against baseline

### What Layer A produces

For a single document, a band classification (Lightly / Moderately / Heavily smoothed) plus per-signal z-scores against baseline. For a manuscript, a chapters × signals dashboard plus identification of which signals are manuscript-wide patterns vs. chapter-specific.

### Three scripts

- `scripts/ai_prose_variance_audit.py` — single document, eleven signals, optional baseline z-scoring.
- `scripts/ai_prose_manuscript_audit.py` — cross-chapter dashboard, surfaces manuscript-wide compression patterns and outlier chapters.
- `scripts/ai_prose_repetition_audit.py` — vocabulary-level diagnostic. Surfaces words a writer is using more than expected against their own baseline, plus within-document clustering. Run when Layer A flags lexical compression and you want specific candidates for restoration.

### How Layer A signals predict Layer B flags

| Compressed Layer A signal | Likely Layer B flag |
|---|---|
| Sentence-length variance | AIC-3 (Echo Stack), AIC-1 (Generic Hand) |
| MATTR / MTLD / Yule's K | AIC-1, AIC-7 (Lexical Convergence) |
| FKGL std | AIC-1, AIC-3 |
| Adjacent-sentence cosine high, std low | AIC-7 (cohesion-too-tidy), AIC-2 (Velvet Fog) |
| Function-word distribution near LLM default | AIC-7 (Discourse Leak), AIC-1 |
| POS-bigram KL high | AIC-7, AIC-3 |
| MDD-SD compressed | AIC-3 |
| Connective density high | AIC-7 |

If Layer A flags compression and the predicted Layer B flags don't fire, the writer probably has unusual register conventions. Note this and lean harder on the Source Triage step (see below). If Layer A is clean and Layer B flags fire, the smoothing is below the variance signals' detection threshold; this happens with sophisticated paraphrase or careful AI editing that preserves variance while imposing pattern.

### Calibration warnings for Layer A

- **Personal baseline is operative.** Heuristic absolute thresholds catch unsubtle cases. Writers with focused vocabulary, fragment-heavy fiction styles, or essayistic long-sentence registers can produce pre-AI prose that triggers the heuristics. The personal-baseline z-score is the reliable diagnostic; absolute thresholds are fallback.
- **Length sensitivity.** Several signals are unreliable below 200-2000 words depending on the metric. The variance audit reports skipped signals when the document is too short.
- **ESL writing.** Lower lexical diversity and lower text perplexity are typical of fluent non-native English, placing it in the same low-variance region as LLM output. Do not run this audit on writing in a writer's second language as if its variance signals carried the same meaning.
- **Heavy paraphrase ceiling.** As paraphraser quality approaches the human distribution, all stylometric signals converge toward 0.5 AUROC (Sadasivan et al. 2023). Layer A operates well below that asymptote with current LLMs but cannot exceed it. When Layer A is clean and the writer suspects AI involvement anyway, source triage at Layer C is the remaining tool.

---

## The Diagnostic Procedure

### Step 1: Pass-Linked Symptom Summary

Before running any new analysis, compile what earlier passes found. Each passage audit begins by quoting upstream signals.

```
Passage [X]: [Location/description]
  Pass 1 (Reader Experience): [relevant flags or "no flags"]
  Pass 5 (Character Audit): [psychology/agency findings or "not yet run"]
  Pass 7 (Voice/POV): [Blind Swap results, interiority markers, or "not yet run"]
  Emotional Craft: [meaning pipeline findings or "not yet run"]
  Scene Turn: [scene mechanics findings or "not yet run"]
  Layer A (if run): [band classification, top compressed signals]
  Production note: [AI-generated / human-drafted / mixed / unknown]
```

### Step 2: Flag Scan

For each passage, test against each of the seven flag families. A flag fires when the pattern is *present and unintentional* — not when the writer chose it.

#### AIC-1: Generic Hand (Voice Singularity)

**Test:** Read the passage aloud in a neutral voice. Then read it as if a different character wrote it. Does anything resist the swap?

**Indicators:**
- Sentence rhythm does not vary across characters or emotional states
- Diction level is uniform (no character uses simpler or more complex language than another)
- Narrator personality is absent — the prose reports but doesn't select
- Interiority sounds the same in every POV character

**Severity:**
- **Spot** — isolated to one passage or scene; the surrounding text has voice
- **Pattern** — recurring across multiple scenes; the manuscript has a default register it falls into
- **Systemic** — manuscript-wide; the text reads as though one entity generated all of it

#### AIC-2: Velvet Fog (Scene Fog + Lexical Genericism)

**Test:** After reading the passage, can you draw the room? Can you point to three sensory details that only this character in this moment would notice?

**Indicators:**
- Characters talk in unspecified spaces
- Physical descriptions are accurate but generic (a "cozy apartment," a "bustling street")
- Sensory detail is visual-only or absent
- The character's body doesn't exist between dialogue lines
- Word choices are accurate but never surprising — center of the semantic field, never the edge

**Named subtype: Indefinite-Pronoun Gesture**

A specific instance of lexical genericism worth flagging by name. The pattern: "something" + abstract qualifier; "some X part" + adjective; "a kind of Y" without specifying Y. The prose outsources specificity to the reader's imagination.

The subtype is *earned* (rare) when the character cannot name what they are feeling and the prose registers that incapacity as part of the experience. It is *unearned* (common) when the prose, not the character, is failing to commit. The diagnostic question: would naming the failure to name ("she had no word for it") be sharper than the indefinite gesture?

See `ai-prose-calibration-level-setting.md` for earned and unearned examples.

**Severity:**
- **Spot** — one scene lacks grounding; adjacent scenes are specific
- **Pattern** — bridge scenes and dialogue scenes consistently foggy; action scenes grounded
- **Systemic** — the manuscript lacks a physical world

#### AIC-3: Echo Stack (Structural Repetition)

**Test:** Mark sentence openings and syntactic patterns across 10+ consecutive sentences. Mark paragraph openings across 5+ paragraphs. Mark scene openings across 3+ scenes.

**Indicators:**
- Sentence-level: repeated Subject-Verb-Object pattern, identical sentence lengths, parallel constructions that aren't rhetorical
- Paragraph-level: every paragraph opens with a topic sentence, closes with a transition, has the same number of sentences
- Scene-level: every scene opens with setting → moves to dialogue → ends with reflection
- The pattern is consistent but not chosen — it's a default, not a style

**Severity:**
- **Spot** — one passage falls into repetitive rhythm; surrounding text varies
- **Pattern** — the echo recurs in predictable contexts (all dialogue scenes, all openings)
- **Systemic** — the manuscript has a template it applies everywhere

#### AIC-4: Register Seams (Multi-Source Splicing)

**Test:** Read the passage looking for shifts in vocabulary level, sentence complexity, or stylistic confidence that don't correspond to POV shifts, emotional shifts, or deliberate register changes.

**Indicators:**
- Abrupt vocabulary level changes mid-paragraph or mid-scene
- One chapter reads at a notably different prose level than its neighbors
- Dialogue and narration feel written by different people (not character voice — authorial voice)
- Transitions between sections feel like cuts, not flows
- Confidence level shifts: some passages are assertive, others hedge

**Cross-detector caveat (Pangram signal-9 tension).** Some commercial detectors (notably Pangram and EditLens) treat *uniform style across segments* as the AI tell, on the theory that humans naturally drift more in voice and register across a draft. AIC-4 flags *visible drift* as a problem. The framework distinguishes:

- **Bad drift (AIC-4 fires):** jarring tonal shift mid-scene that breaks reader trust. The seam serves nothing; it's an artifact of production.
- **Natural drift (AIC-4 does not fire):** a writer who switches register between a technical paragraph and an anecdote, or whose voice wobbles across a long draft because attention and energy varied. This is human and protective against detector signals.

The diagnostic is whether the shift serves the prose. Authorial-controlled register variation is good; production-artifact register seams are bad. A writer who smooths every seam at the prose level may walk into higher third-party detector confidence; a writer who introduces tonal shifts to "humanize" the prose may break reader trust. Source triage adjudicates.

**Severity:**
- **Spot** — one detectable seam; might be a single paste-in
- **Pattern** — multiple seams correlating with chapter or scene boundaries
- **Systemic** — the manuscript is a patchwork; no consistent authorial voice holds it together

#### AIC-5: Puppet Dialogue (Mouth Uniformity)

**Test:** Cover character names. Can you tell who is speaking from diction, rhythm, sentence length, what they refuse to say, or how they deflect?

**Indicators:**
- All characters speak in complete sentences at the same complexity level
- Characters take turns delivering information without interrupting, mishearing, or talking past each other
- No character has a verbal tic, habitual deflection, or characteristic rhythm
- Subtext is absent — characters say what they mean and mean what they say
- Dialogue tags are the only differentiation

**Severity:**
- **Spot** — one conversation is uniform; others have distinct voices
- **Pattern** — dialogue scenes consistently puppet; non-dialogue prose has more voice
- **Systemic** — no character has a distinct speech pattern

#### AIC-6: Continuity Smear (World-Model Failures)

**Test:** Track three things through the passage: (1) what characters are physically holding or wearing, (2) spatial positions relative to each other, (3) what information each character has at each point.

**Indicators:**
- Objects appear, disappear, or teleport between characters' hands
- Spatial positions are inconsistent within a scene
- Characters reference information they shouldn't have yet
- Time passes unevenly (a conversation that should take 5 minutes spans what feels like an hour, or vice versa)
- Emotional states reset between paragraphs without transition

**Severity:**
- **Spot** — one or two continuity breaks; the physical world is otherwise maintained
- **Pattern** — continuity breaks cluster around specific scene types (action, group dialogue)
- **Systemic** — the manuscript doesn't maintain a physical world model

#### AIC-7: Discourse Leak (Assistant-Register Intrusion)

**Test:** Read the passage looking for moments where the text sounds like it's explaining, presenting, or organizing for a reader rather than inhabiting a character or telling a story. Ask: "Is this how a person in this situation would think — or is this how an AI would present this person's thoughts?"

**Evidence categories:**

**Assistant Frame** — Direct assistant-register intrusions in narrative prose. Throat-clearing before points ("Here's the thing about grief—"). Resumptive parroting in interiority (a character restating what just happened before reacting to it). Sycophantic or evaluative framing ("The remarkable thing was..."). Metacommentary on the difficulty or complexity of what's being described ("It was a complicated feeling, one that resisted easy categorization").

*Named pattern within Assistant Frame: Pseudo-Aphorism.* "X is the Y of Z" or "X as Y" formulations that aspire to maxim register without earning the standing of a maxim. Often followed by a real image or specification that does the work the aphorism gestured at. Cut the aphorism, keep the image. See `ai-prose-calibration-level-setting.md` for earned and unearned examples.

*In fiction, this should be near-zero.* A narrator can be self-aware, but self-awareness and assistant framing are different registers. The test: would an essayist write this sentence, or would a chatbot?

**Hedge Drift** — Epistemic hedging at densities that suggest LLM caution rather than narrative uncertainty. "In some ways," "to a certain extent," "it could be said that," "arguably," "there was a sense in which." Individual uses are often legitimate — characters doubt, narrators qualify. The flag fires on accumulation: when a passage hedges more than the character's psychology or the narrative situation warrants.

*Named pattern within Hedge Drift: Negation Hedge.* "Not X." / "Not X, exactly." / "Not X. Not Y." Narrator pretends to make a careful discrimination. The pattern is *earned* when the character is actively sorting, cataloguing, or refusing the wrong word — the negation IS the cognitive act. *Unearned* when the next sentence does the work the negation pretended to. See level-setting reference.

*Flagged by density and spread, not single use.* Three hedges in a paragraph of genuine uncertainty is voice. Three hedges per page across a chapter is drift.

**Template Loop** — Rhetorical figures deployed as structural tics rather than choices. Correctio/epanorthosis ("Not X, but Y" / "Not X exactly — more like Y") is the most common. Also: cataphoric teasing ("Here's where it gets complicated"), synonym stacking in descriptive passages ("robust, thorough, and comprehensive" or the literary equivalent: "vast, sprawling, and untamed"), and the magic triple — grouping attributes, actions, or sensory details in threes with mechanical regularity.

*Named pattern within Template Loop: Disguised Correctio.* "Not X, but Y" embedded in narration; "did not X but Y." Same as Negation Hedge but harder to spot because it's mid-sentence. Almost always cuts cleanly when the affirmative carries the meaning alone.

*Named pattern within Template Loop: Manifesto Cadence.* Three or four parallel sentences building to conclusion. *Earned* when each sentence escalates, restricts, or reveals — the parallelism IS the development. *Unearned* when parallel structure substitutes for actual development; each sentence is a register variant of the same content.

*The test is whether the pattern does new work each time.* Correctio used once to mark a character revising their own understanding in real time is good prose. Correctio appearing every time a character processes an emotion is a template. The magic triple describing three genuinely distinct things is a list. The magic triple padding a description to feel complete is a habit.

**Lexical Convergence** — The generating model reaches for the same high-register word across semantically different contexts where a human voice would normally differentiate. Where a human writer might choose "structure," "layout," "pattern," "shape," or "logic" depending on what they're actually describing, an LLM has a favorite and uses it for all of them. The diagnostic question is not "does this word appear on a list of AI words?" but "does this manuscript reuse the same prestige term across unrelated contexts where more specific or more ordinary words would serve?"

The convergence habit is more durable than any particular word list. Early ChatGPT-4o overindexed on "delve," "tapestry," "navigate," "landscape," "nuanced," "multifaceted." Sonnet 3.5 favored "architecture," "choreography," and a general drift toward lyrical register. The specific words shift every model generation. The habit of convergence — defaulting to the same prestige vocabulary regardless of context — persists.

*Maintain a per-project watchlist, but use it as an evidence tool, not a rule engine.* The watchlist identifies candidates; the convergence test determines whether they're flags. A word earns its watchlist spot when it (a) appears in multiple unrelated contexts (different subject matter, different characters, different emotional registers) and (b) could be replaced with a more specific or more ordinary word each time.

*Layer A integration.* `scripts/ai_prose_repetition_audit.py` surfaces convergence candidates automatically against a personal or genre baseline. The script identifies words a writer is using more than expected; the auditor's judgment determines whether the recurrence is convergence (flag) or thematic anchor (keep).

*Genre calibration rider:* Tolerance for lexical convergence varies by genre and narrative mode. Essayistic, literary, and philosophical narration naturally reuses conceptual vocabulary — a narrator thinking about "architecture" as a sustained metaphor across a novel may be doing deliberate thematic work. Commercial thriller, romance, and horror prioritize diction clarity and immediacy; convergence on prestige vocabulary reads as artificial faster in these registers. The auditor should calibrate the flag threshold to the manuscript's genre and narrative mode before firing.

**Commitment Evasion** — Both-sidesing, positivity pivots, and unearned resolution in narrative prose. A narrator who refuses to commit when the story's stakes demand commitment. An ending that softens into hope when the scene earned something harder. Interiority that compulsively balances every negative thought with a qualifying positive ("It was devastating, but also, in a strange way, freeing"). A character whose anger always resolves into understanding within the same paragraph.

*If stakes are concrete, language must commit.* A character can genuinely see both sides of a conflict — that's psychology. But when *every* character sees both sides of *every* conflict, the manuscript is performing epistemic caution rather than rendering human thought. The positivity pivot is especially diagnostic: real people sometimes end on unresolved negative feeling. LLM-generated interiority almost never does.

**Evidence burden:** Each fired evidence category requires a minimum of two quoted instances from the passage, with a brief note explaining why each instance is unearned in context (i.e., not explained by the character's psychology, the narrator's established voice, or the scene's rhetorical demands). A single instance of correctio or a lone hedge is not evidence — it's a sentence. The flag fires on accumulation, and the audit must show the accumulation, not assert it.

For Lexical Convergence specifically, the evidence thresholds scale with severity:

- **Spot** — Same term in at least 3 unrelated contexts (different subject matter, different characters, or different emotional registers). All instances may appear within a single chapter or section.
- **Pattern** — Same term in unrelated contexts across at least 2 chapters. Multiple terms on the watchlist showing the same convergence habit.
- **Systemic** — Convergence appears across most POVs or sections. The manuscript has a default prestige register it applies regardless of context.

A word used three times in one scene about actual architecture is not a flag. "Architecture" used to describe a building, a relationship, and a character's emotional defenses across three chapters is Spot at minimum.

*Readiness guardrail:* Lexical Convergence alone should rarely gate submission readiness. Convergence is a surface property — a copyeditor can catch it in a line pass. It gates readiness primarily when co-occurring with AIC-1 (Generic Hand) or with other AIC-7 evidence categories (particularly Assistant Frame or Template Loop), where the convergence is one symptom of a deeper register problem.

**Severity:**

- **Spot** — One or two evidence categories appear in isolated passages; the surrounding text is free of assistant-register habits. Likely a single generation session that wasn't revised.
- **Pattern** — Multiple evidence categories recur across scenes or chapters. Discourse leak correlates with specific content types (interiority passages, emotional processing, thematic reflection) while action and dialogue stay cleaner. The manuscript has a "thinking voice" problem.
- **Systemic** — The narrator's voice is itself contaminated with assistant-register habits throughout. The reader feels they're being presented to rather than told a story. Even dialogue and action scenes carry traces of hedging, template loops, or commitment evasion.

**False-positive guardrails:**

Some literary modes produce patterns that resemble discourse leak but are deliberate craft choices. Before flagging, test whether the pattern is explained by any of these:

- **Essayistic fiction.** Narrators in the tradition of Sebald, Bernhard, or Knausgaard think in qualification, correction, and digression as a formal strategy. Hedge Drift, Template Loop (correctio), and Commitment Evasion may all be structural features of the voice. The test: does the pattern persist with consistent texture across the full manuscript, or does it appear only in passages that feel generated? Essayistic narrators hedge *distinctively* — their qualifications carry personality. LLM hedging is generic.
- **Philosophical narrators.** A character or narrator with a philosophical orientation may genuinely think in both-sidesing, epistemic caution, and rhetorical self-correction. The test: does the hedging track the character's specific intellectual commitments, or is it generalized caution about everything? A philosopher character who qualifies claims about justice but speaks with certainty about lunch is in character. A character who hedges about everything is leaking.
- **Trauma-loop cognition.** Characters processing trauma often circle, restate, qualify, and revise — patterns that overlap with Hedge Drift and Template Loop. The test: does the repetition escalate, deepen, or shift with each iteration (the character is working through something), or does it cycle at the same level (the prose is stalling)? Trauma loops have psychological pressure behind them. Discourse leak is frictionless.
- **Adolescent or uncertain narrators.** Young narrators and narrators in states of genuine confusion may over-qualify, hedge, and correct themselves. The test: does the uncertainty match the character's developmental stage and situation, and does it contrast with passages where the character is more sure? A teenager who hedges about feelings but is definitive about music is characterized. Uniform hedging is leak.
- **Ironic or unreliable narration.** A narrator who performs epistemic authority they don't deserve, or who qualifies everything to avoid commitment, may be deliberately constructed as unreliable. The test: does the text frame the hedging as characterization (other characters react to it, the plot exposes it, the reader is positioned to see through it), or does it pass without comment?
- **Writers whose natural register sits in the variance-compressed region.** Some writers — those with focused vocabularies, fragment-heavy fiction styles, or essayistic long-sentence registers — produce pre-AI prose that triggers Layer A heuristics by absolute thresholds. For these writers, the personal-baseline z-score is the operative diagnostic; absolute heuristics are misleading. Layer B flags should be evaluated against the writer's own corpus distribution rather than a literature-derived baseline.

When a guardrail applies, note it in the audit: "AIC-7 evidence present but consistent with [essayistic voice / philosophical narrator / etc.]. Not flagged." This documents the auditor's reasoning and prevents a future auditor from re-flagging the same passages.

**Output ordering for AIC-7:** Present raw evidence (quoted instances, counts, cross-context mapping for Lexical Convergence) before any severity assignment. The author should see the data before the judgment. This supports a three-step workflow: (1) the audit finds candidates with quotes and counts, (2) the rubric enforces thresholds and false-positive guardrails, (3) the author/editor confirms severity and readiness impact.

### Step 3: Pattern Synthesis

After flagging individual passages, look for connections:

1. **Which flags co-occur?** AIC-1 (Generic Hand) + AIC-5 (Puppet Dialogue) together suggest the entire voice layer was generated rather than written. AIC-2 (Velvet Fog) + AIC-6 (Continuity Smear) together suggest the text was generated without a persistent world model.

2. **Do flags cluster by production method?** If the writer mixed human and AI drafting, do the flag clusters align? This is diagnostically useful — it tells the writer which aspects of the AI output need the most attention.

3. **What's the interaction with genre?** Some genres tolerate more of certain flags. Thriller pacing can carry AIC-2 (Velvet Fog) if the momentum is strong. Literary fiction cannot. Romance requires AIC-5 (Puppet Dialogue) to be zero — if the lovers sound alike, the relationship doesn't breathe.

4. **Does AIC-7 (Discourse Leak) correlate with interiority?** Discourse leak often spares dialogue and action but saturates interiority and reflection passages — the moments where the AI is "thinking through" a character's response rather than rendering events. If the flag fires only in interiority, the salvage target is narrow: rewrite the thinking, keep the doing.

5. **AIC-7 + AIC-1 compound.** When Generic Hand and Discourse Leak co-occur, the manuscript has both a voice problem and a register problem. The prose lacks a specific narrator *and* the organizational habits are wrong. This is the most damaging combination for reader trust — the text feels generated at every level, not just at the word level.

6. **Layer A signal alignment.** If Layer A was run, check whether the compression signature aligns with the Layer B flag pattern. Lexical compression (low MATTR/MTLD) predicts AIC-1 and AIC-7 Lexical Convergence. Compressed sentence-length variance predicts AIC-3. Manuscript-wide patterns (>50% chapters compressed on a signal) suggest revision drift toward density rather than chapter-specific issues.

### Step 4: Salvage Triage

Classify every flagged passage into one of three triage categories:

| Category | Meaning | Author action |
|----------|---------|--------------|
| **Keep** | The prose works despite AI origin. It has enough specificity, voice, or structural function to stand. | Light revision at most. Don't fix what isn't broken. |
| **Recast** | The structural intent is sound — the scene does what the story needs — but the prose needs to be rewritten in the author's voice. | Rewrite from scratch using the existing text as a structural outline. Don't edit the sentences; replace them. |
| **Replace** | The passage doesn't serve the story structurally *and* the prose is generic. It's weight without function. | Cut or reconceive. The problem isn't how it's written; it's whether it should exist. |

**Triage discipline:** In lightly AI-assisted manuscripts, Keep will typically be the largest category — most AI prose is structurally functional. But in heavily AI-drafted manuscripts (80%+ generated), Recast may dominate, and that's correct. The distribution should reflect the manuscript, not a predetermined ratio. Two failure modes to guard against: (1) over-triaging toward Recast/Replace in a manuscript that's mostly functional, producing a revision plan the author won't execute; (2) under-triaging toward Keep in a manuscript with pervasive voice singularity, because the uniform competence makes each individual passage seem "fine" in isolation while the cumulative effect is deadening.

### Step 5: Source Triage Pass

The voice-attribution layer. Answers the question that distributional analysis and pattern matching cannot: whose voice is this, and is it doing real work?

**Run only when voice-bearing material is identifiable.** For fiction, this means each character's voice register and the narrator's. For argument-shaped nonfiction, this means the writer's persona, the audience's expectations, the argument's stakes. Without that input, source triage is unreliable; report Layer C as unavailable and stop after Step 4.

**Why this layer matters.** Almost all the AI-prose work depends on being able to ask "whose voice is this, and is that voice doing real work or pretending to?" Pattern-matching surface tells without that triage produces the failure mode common in external critiques: generic recommendations that flatten character voice in the name of cleaning up prose. Source triage prevents that failure by making voice attribution the precondition for every cut.

**See `ai-prose-calibration-level-setting.md` for the full source-triage examples library.**

#### The Payoff Test

The most actionable diagnostic in the framework. AI-fluent prose often takes the shape:

```
AI-fluent setup → character-voice payoff
```

The setup hedges, qualifies, or aphorizes. The payoff commits, specifies, lands. The setup is doing nothing the payoff isn't doing better. Cut the setup, promote the payoff.

**Diagnostic question.** Does the next sentence do the work the prior sentence pretended to? If yes, cut the prior. The payoff sentence usually has the specific image, the committed verb, the registered emotion. The setup sentence usually has a hedge, a negation, an indefinite, or an aphorism.

**When the payoff test fails.** Sometimes the setup is doing real work: building rhythm, establishing register, doing the cognitive labor of a character actively sorting. Then both stay. The diagnostic is contextual; pattern alone does not entitle the cut.

#### The Voice Test

For each flagged sentence, ask: is this something this specific character (or this story's narrator) would actually say? Or is this generic literary-fluent interior monologue?

**Generic monologue wearing a character's name is the failure mode.** Real character voice has specific registers. Take a flagged sentence. Could the same sentence appear in another character's POV without changing? If yes, voice is not doing the work. The sentence is generic.

#### Voice Slip vs. Lost Callback

When the voice test flags a line as off, the failure mode matters because the fix is different.

**Voice slip.** The line is in nobody's voice. It's authorial generic register imported into a character's mouth. The character wouldn't say this; the line could appear in another character's POV without changing. Fix: rewrite in the character's voice, or cut.

**Lost callback.** The line is in voice (the character would say this) but reaches for material the reader hasn't seen. The setup was cut in earlier revision and the callback now lands on no anchor. The reader registers the line as discordant because it's gesturing at a shared frame the prose hasn't established. Fix: restore the setup somewhere earlier, or cut the callback, or replace it with a callback to material the current text supports.

The diagnostic question that distinguishes them: when you ask the writer "does the character actually use this phrase elsewhere, or refer to this idea elsewhere?", the answer for voice slip is "no, this is just authorial register." The answer for lost callback is "yes, but you cannot see it because it has been cut." Lost callback is recoverable through restoration. Voice slip requires rewriting.

When running source triage and a flagged line resists the voice-slip rewrite (the writer says "no, the character would say this; something else is wrong"), check for lost callback before continuing. Search the rest of the manuscript for the term, the analogy, or the conceptual setup the line is reaching for. Absence is a strong signal that the setup got cut.

#### Triage Rules by Passage Type (Fiction)

| Passage type | Pattern usually earned | Pattern usually unearned |
|---|---|---|
| Dialogue | Yes; character voice tolerates more pattern | Only when the pattern is uniform across all characters |
| Character interior, actively sorting | Yes; the negation IS the cognitive act | When the sorting goes nowhere |
| Character interior, generic introspection | Rarely | Almost always; "Not X. Not Y." setup is AI-fluent monologue |
| Narrator-pose commentary | Rarely | Almost always; the "There was X in his Y" structures are pose |
| Genre-required language | Yes (hypnotic induction, prayer, ritual) | When the writer is signaling the register without earning it |

The hardest rule to teach is that "earned" depends on context, and only knowing what the character's voice actually is reveals which instances qualify. Without voice attribution, the pattern alone does not justify the cut.

#### "Earned by Frame" — A Third Verdict

Beyond *earned* and *unearned*, some passages are *earned by frame*: the prose itself diagnoses the problematic pattern through proximate commentary, characters calling each other out, or narrator awareness. When a chapter's diagnostic register names the AI-fluent move and uses it deliberately as evidence of altered cognition or pose, the move is doing structural work that cutting would erase.

Diagnostic test for earned-by-frame: does the surrounding prose make the reader see the move as a move, rather than reading past it? If yes, the move is load-bearing through the frame. Don't soften.

---

## Argument-Shaped Nonfiction Parallel Pattern Set

For testimony, briefs, op-eds, scholarly articles, and policy memos, the AI-prose patterns differ from literary fiction. Five argument-shaped poses common in AI-assisted nonfiction. These map onto AIC categories (mostly AIC-7) but warrant their own names because their specific contexts and revision moves differ.

### Abstraction Shielding (AIC-2 analog for argument)

**Forms.** "Stakeholders," "impacted communities," "decision-makers," "those affected," "service providers," "youth-serving institutions."

**What it does (unearned).** Lets the writer avoid naming specific actors, specific institutions, specific people. The abstraction protects the writer from commitment and from the reader's ability to verify.

**What it does (earned).** Names a class because the class itself is the analytical unit. The abstraction is doing analytical work, not avoidance work.

**Cut rule.** Replace with specific actors when the analysis depends on knowing who. Keep when the abstraction is the point of the analysis. The diagnostic question: would naming three specific actors make the sentence sharper, or would it obscure a structural critique?

### False-Balance Construction (AIC-7 Commitment Evasion analog)

**Forms.** "While reasonable people may disagree." "There are valid concerns on both sides." "Some have argued [reasonable position]; others have argued [unreasonable position]."

**What it does (unearned).** Smuggles in the appearance of judiciousness while granting standing to positions that don't merit it. Flattens moral or evidentiary asymmetry.

**What it does (earned).** Genuinely contested empirical or normative question; both positions are entitled to the standing. The writer commits to a position despite the contestability.

**Cut rule.** Replace with specific named disagreement when the disagreement is real. Cut when the construction is fabricating balance. Procatalepsis (anticipation of objection in its strongest form) is the rhetorical countermove: state the opposing view at full strength, then commit to your own.

### Hedge-and-Affirm (AIC-7 Hedge Drift analog)

**Forms.** "While X is generally true, in some cases Y." "Although X, it is also true that Y." "X, though of course Y."

**What it does (unearned).** Performs caution while saying nothing definite. The hedge protects the writer from commitment; the affirm performs commitment without earning it.

**What it does (earned).** Genuine epistemic care. Acknowledges a real qualification before committing. Both halves carry specific content.

**Cut rule.** Earned when both halves do specific work. Unearned when both halves gesture. Replace with concession-with-cost: concede only what costs the writer something the reader can verify and negotiate.

### Recommendation Template (AIC-7 Template Loop analog for argument)

**Forms.** "The Council should commit to..." "We urge stakeholders to..." "It is essential that..." "Going forward, [actor] should prioritize..."

**What it does (unearned).** Provides the appearance of advocacy without specifying the action. The verb is committed but the object is generic.

**What it does (earned).** Names a specific action by a specific actor by a specific date.

**Cut rule.** Recommendations earn their place when actor, action, scope, and verifiability are present. Generic recommendations are template-driven and almost always unearned. Imperative-with-object is the rhetorical countermove: replace abstract verbs with imperatives that name what is to be done by whom.

### Authority Laundering (AIC-7 Assistant Frame analog for argument)

**Forms.** "Scholars have argued..." "Research suggests..." "Studies have shown..." "Experts agree..."

**What it does (unearned).** Borrows authority without taking on responsibility. The writer reports what authority claims without committing to it or accountably citing it.

**What it does (earned).** Names the scholar, the study, the finding, with citation. Commits to the authority's claim, contests it, or specifies its scope.

**Cut rule.** Authority claims earn their place when they name the authority and its specific claim. Generic appeals to research or expertise are usually authority laundering. The countermove is specific-citation-with-stake: name the author, year, finding, and the stake the citation carries for your argument.

### Triage Rules by Passage Type (Nonfiction)

| Passage type | Pattern usually earned | Pattern usually unearned |
|---|---|---|
| Argument under construction | Yes; thinking is the point | When the working-through goes nowhere |
| Recommendation paragraphs | Rarely | Almost always; template "must commit to" formulations are pose |
| Concession passages | When the concession is real | When false-balance constructions manufacture concession |
| Evidence deployment | When evidence is named and committed to | When authority laundering substitutes for citation |
| Framing / context-setting | When the frame does specific analytical work | When abstractions replace named actors that the writer should commit to |

---

## Required Outputs

### 1. Flag Key and Summary

**Before the flag table, produce a brief key explaining each flag that fired.** The key uses the flag name and a one-sentence plain-language description of what it means for the reader. Only include flags that actually fired (Clean flags can be omitted from the key). This ensures the author can read the audit without memorizing codes.

Example key format:

```
| Flag | Name | What it means |
|------|------|---------------|
| AIC-1 | Generic Hand | The prose loses the character's specific voice — it could belong to anyone. |
| AIC-3 | Echo Stack | The same sentence shapes or structural patterns repeat without earning the repetition. |
```

Then the flag summary table:

```
Flag    | Name             | Severity | Passages affected | Co-occurring flags
AIC-1   | Generic Hand     | [S/P/Sy] | [list]           | [list]
AIC-2   | Velvet Fog       | [S/P/Sy] | [list]           | [list]
AIC-3   | Echo Stack       | [S/P/Sy] | [list]           | [list]
AIC-4   | Register Seams   | [S/P/Sy] | [list]           | [list]
AIC-5   | Puppet Dialogue  | [S/P/Sy] | [list]           | [list]
AIC-6   | Continuity Smear | [S/P/Sy] | [list]           | [list]
AIC-7   | Discourse Leak   | [S/P/Sy] | [list]           | [list]
```

For nonfiction work, add a parallel pattern table for the five argument-shaped patterns.

**Author-facing requirement:** Throughout the findings, use the flag *name* (Generic Hand, Velvet Fog, etc.) rather than just the code. Codes are for cross-referencing; names are for reading. When a flag first appears in the findings narrative, include a brief parenthetical description if the key hasn't been presented yet. The author should never have to look up what a code means.

### 2. Top 3 Systemic Risks

The three most damaging patterns in the manuscript, stated as **reader-impact claims** — what the reader experiences, not what the code is. Include the flag name and severity parenthetically for cross-referencing, but lead with the human-readable diagnosis:

- "The dialogue cannot carry the romance because no two characters sound different enough for the reader to feel the relationship as between two people." (AIC-5, Systemic)
- "The manuscript's uniform competence works against it — the reader never encounters a sentence that could only appear in this book." (AIC-1, Systemic)
- "Chapters 4–7 read at a different prose level than 1–3, creating a patchwork effect that undermines the narrator's authority." (AIC-4, Pattern)

### 3. Layer A Findings (if Pre-Scan Run)

If Layer A pre-scan was run, include the band classification (Lightly / Moderately / Heavily smoothed) for the manuscript and the top compressed signals against baseline. Note manuscript-wide patterns (signals compressed on >50% of chapters) and outlier chapters (those with the most |z| > 1.5 signals).

### 4. Contamination Map (if expanded scope)

Chapter-by-chapter flag density map as described in Scope Selection. Include a one-line note per chapter identifying the dominant issue.

### 5. Salvage Plan: Keep / Recast / Replace

For each flagged passage or region, the triage classification with a one-sentence rationale:

```
Location          | Triage  | What's wrong
Ch 3, pp 2–4      | Recast  | Scene function is critical (midpoint turn) but the dialogue is puppet — both characters sound the same
Ch 5, pp 1–3      | Keep    | Action sequence; momentum carries the generic prose
Ch 7, full chapter | Replace | Bridge chapter with no structural function and velvet fog throughout — you can't see the room
Ch 9, pp 4–5      | Recast  | Interiority passage; the emotional pipeline is correct but the words are generic — nothing specific to this character
```

### 6. Source Triage Verdicts (if Step 5 Run)

For each flagged passage where source triage was performed, the verdict with brief reasoning:

```
Location          | Verdict          | Reasoning
Ch 3, p 2         | Earned           | Character actively sorting — negation IS the cognitive act
Ch 5, p 1         | Unearned         | Narrator-pose negation; next sentence carries the meaning alone
Ch 7, p 4         | Earned by frame  | Surrounding prose names the move; pose is diagnostic
Ch 9, p 5         | Lost callback    | Line is in voice but reaches for material cut from earlier draft; restore Ch 1
Ch 12, p 3        | Voice slip       | Line in nobody's voice; rewrite or cut
```

### 7. Readiness Impact Note (Hard Gates / Must-Fix Floor)

A short assessment of how the audit's findings affect submission readiness (Pass 11). The conditions below are **audit-internal hard gates**: when they fire, the AIC finding carries an audit-internal **Must-Fix floor** that propagates to synthesis severity per the canonical Audit-Signal Propagation Rule in `core-editor/references/run-synthesis.md §Step 2`. Synthesis cannot downgrade a hard-gate flag below Must-Fix without an explicit override marker recording rationale.

- If **any AIC flag is Systemic and confirmed by expanded scope (contamination map)** → **Hard Gate.** Submission readiness cannot pass until the systemic flag is resolved; produces a Must-Fix floor for the named flag. State which flag and why.
- If **any AIC flag is Systemic from sample scope only (3 passages)** → not yet a hard gate. Instead, flag as: "Systemic finding from limited sample — expand to contamination map before gating submission readiness." The audit must run expanded scope to justify a readiness block.
- If **AIC-4 (Register Seams) is Pattern or higher** → **Hard Gate.** Flag as readiness-gating: agents and editors will detect the patchwork, and it signals unfinished revision; produces a Must-Fix floor.
- If **AIC-7 (Discourse Leak) is Pattern or higher in interiority passages** → flag for revision but do not gate submission readiness independently. Discourse leak in interiority is revisable without structural changes. However, if AIC-7 co-occurs with AIC-1 (Generic Hand) at Pattern or higher, the combination is a **Hard Gate** — the manuscript's voice layer needs rebuilding, not patching; produces a compound Must-Fix floor.
- If **all flags are Spot** → no hard gate. Manuscript can proceed through Pass 11 with the salvage plan as a revision checklist item.

---

## Integration Points

### Contract Intake

Add to the intake protocol:

**"How was this draft produced?"**
- Primarily human-written
- Primarily AI-generated (single model)
- Primarily AI-generated (multiple models)
- Mixed human and AI drafting
- Prefer not to say

If the answer is anything other than "primarily human-written," flag the AI-Prose Calibration audit for automatic activation after core passes complete. If "prefer not to say," do not flag — but if Pass 1 or Pass 5 findings suggest AI-generated prose, note the recommendation without assuming.

### Interaction with Other Audits

- **Emotional Craft:** If both audits run, the Emotional Craft audit identifies where the meaning pipeline breaks. This audit identifies whether the breakage has the signature of AI generation (correct structure, generic texture) versus human craft weakness (missing pipeline stages).
- **Character Architecture:** If AIC-5 (Puppet Dialogue) fires, cross-reference with the Blind Swap test results. If characters also fail the Blind Swap in narration, the voice singularity is deeper than dialogue — it's authorial.
- **Scene Turn:** If AIC-6 (Continuity Smear) fires, cross-reference with Scene Turn's causal chain analysis. Continuity smear and broken scene chains compound — the reader loses both physical and narrative orientation simultaneously.
- **Compression Audit:** If AIC-3 (Echo Stack) at paragraph or scene level co-occurs with retained-scaffolding findings from Compression, the structural over-extension and the prose-level template are reinforcing each other. Run compression first; the compression cuts may resolve some echo-stack patterns without prose-level work.

### Model-Agnostic Design

This audit deliberately avoids:
- Lists of model-specific tells (these decay within months)
- "AI detection" scoring or probability estimates
- Assumptions about which models produce which patterns
- Any framing that treats AI-generated text as inherently inferior

The audit targets *prose quality categories* that happen to be common in AI-generated text. A human writer who produces the same patterns gets the same flags and the same salvage plan. The categories are durable because they describe what the prose *lacks* (specificity, embodiment, voice, surprise) rather than what it *contains* (particular phrases, punctuation patterns, syntactic habits).

As models improve, some flag families may fire less often on AI-generated text. That's fine — the audit remains useful for any text that exhibits the patterns, regardless of origin.

---

## Firewall Compliance

This audit diagnoses prose-level patterns. It does not:
- Rewrite flagged passages (the author executes all prose changes)
- Generate replacement prose, even as examples
- Invent character voices to demonstrate what "distinct dialogue" would sound like
- Suggest specific word substitutions for generic phrasing

The salvage plan (Keep/Recast/Replace) tells the author *what to do*. It does not do it for them. "Recast this passage with sensory specificity" is a diagnostic instruction. "The room smelled of burnt coffee and old paper" is content invention. The audit produces the former, never the latter.

The level-setting reference (`ai-prose-calibration-level-setting.md`) contains generic illustrative examples of earned vs. unearned patterns. These are calibration aids, not generated prose for the manuscript under audit. Do not adapt them as substitutions; deploy the writer's voice in revision.

---

## Output Ordering Convention

When producing the full audit output, follow this sequence:

```
1. Layer A Pre-Scan Findings (if run; band, top compressed signals, manuscript-wide patterns)
2. Pass-Linked Symptom Summary (per-passage upstream findings)
3. Flag Summary Table (all AIC flags, severities, co-occurrences; nonfiction parallel set if applicable)
4. Top 3 Systemic Risks (reader-impact statements)
5. Contamination Map (if expanded scope; omit if sample-only)
6. Salvage Plan: Keep / Recast / Replace (per-passage triage)
7. Source Triage Verdicts (per-passage earned/unearned/earned-by-frame/voice-slip/lost-callback if Step 5 run)
8. Readiness Impact Note (Pass 11 interaction)
9. Synthesis Translation (severity mapping for revision checklist integration)
```

If the audit runs at sample scope (3 passages) and finds potential systemic flags, append a recommendation to expand scope before the Readiness Impact Note.

---

## Design Notes

### Why "Salvage" and Not "Detection"

The metaphor matters. Detection frames AI prose as contamination to be identified and removed. Salvage frames it as raw material to be refined. The writer who drafted with AI made a production choice — the audit's job is to help them finish the work, not to judge the method.

### Why Three Layers

The audit operates at three resolutions, each with its own blind spot:

- **Layer A (distributional)** measures variance compression against a baseline. Catches the magnitude of smoothing. Cannot see whose voice the prose is reaching for or what the prose is doing.
- **Layer B (pattern, the seven AIC flags)** catches recurring AI-prose habits. Cannot adjudicate whether a specific instance is earned or unearned in context.
- **Layer C (source triage)** answers voice attribution and the earned/unearned question. Doesn't scale; requires character/narrator/persona knowledge.

Each layer's blind spot is the next layer's expertise. The audit never collapses these into a single AI-or-not score. The math doesn't entitle that conclusion. Layer A produces a magnitude. Layer B produces a flag inventory. Layer C produces a per-passage verdict.

### Why Seven Flags

The seven flag families cover two diagnostic layers within Layer B. AIC-1 through AIC-6 diagnose craft failures — what the prose lacks (voice, specificity, embodiment, variation, continuity). AIC-7 diagnoses a register failure — what the prose imported (the organizational and rhetorical habits of an assistant). These are independent failure modes. A passage can be clean on AIC-1 through AIC-6 (it has voice, specificity, grounded scenes, varied structure, distinct dialogue, solid continuity) and still trigger AIC-7 because the narrator hedges like a chatbot or organizes every reflection through correctio.

AIC-7's five evidence categories (Assistant Frame, Hedge Drift, Template Loop, Lexical Convergence, Commitment Evasion) are grouped under one flag rather than split into five because the diagnostic question is the same for all of them: "Is this passage organizing thought like an assistant or like a narrator?" The categories help the author locate the specific habit; the flag tells them the underlying problem. The named patterns within categories (Negation Hedge, Disguised Correctio, Pseudo-Aphorism, Manifesto Cadence) are sharper instances writers can search for.

Within each layer, the flag families are deliberately coarse-grained. Finer distinctions (e.g., separating "generic metaphor" from "generic description" within AIC-2) would increase diagnostic precision but decrease author actionability. The author needs to know: "This passage is velvet fog — rewrite it with sensory specificity." They don't need a taxonomy of fog subtypes.

### Why Severity Uses Spot/Pattern/Systemic Instead of Must-Fix/Should-Fix/Could-Fix

The standard severity labels (Must-Fix, etc.) imply editorial priority. But AI-prose calibration flags interact with the author's production method in ways that standard editorial flags don't. A systemic AIC-1 (Generic Hand) in a manuscript the author plans to rewrite from scratch is less urgent than a pattern-level AIC-4 (Register Seams) in a manuscript the author considers near-final. Spot/Pattern/Systemic describes *extent*, and the Salvage Plan describes *action*. The author and the Readiness Impact Note together determine priority.

**Synthesis translation:** When AIC flags feed into Core DE synthesis or revision economics, translate to the standard framework severity using this mapping:

| AIC Severity | + Salvage Triage | → Framework Severity |
|-------------|-----------------|---------------------|
| Systemic | Recast or Replace | Must-Fix |
| Systemic | Keep | Should-Fix (the pattern is pervasive but the prose is functional) |
| Pattern | Recast | Should-Fix |
| Pattern | Keep or Replace | Could-Fix |
| Spot | Any | Could-Fix |

**AIC-7 (Discourse Leak) specific translations:**

| AIC Severity | + Salvage Triage | → Framework Severity |
|-------------|-----------------|---------------------|
| (AIC-7 only) Systemic | Recast | Should-Fix (register is pervasive but revisable without structural changes) |
| (AIC-7 only) Pattern | Keep | Could-Fix (localized habits in otherwise strong voice) |
| (AIC-7 + AIC-1) Pattern+ | Recast | Must-Fix (compound voice + register failure) |

**Source triage modifiers (Step 5):** Source triage verdicts modify severity:

| Source Verdict | Severity Adjustment |
|---|---|
| Earned | Reduce severity by one level (Pattern → Spot, Systemic → Pattern) |
| Earned by frame | Hold severity; flag as not-actionable in revision (the frame is the work) |
| Unearned | Hold or raise severity per Layer B finding |
| Lost callback | Hold severity; salvage plan becomes Restore-Setup-Elsewhere rather than Recast |
| Voice slip | Hold severity; salvage plan is Recast in voice |

Note: Systemic + Keep is not a valid combination for AIC-7. If discourse leak is systemic, the narrator's register is contaminated throughout — that cannot be "kept." Systemic findings should triage as Recast (the voice is functional but the register needs rebuilding) or, rarely, Replace (the voice is also broken). If an auditor is tempted to mark Systemic + Keep, they should re-examine whether the finding is genuinely systemic or whether a false-positive guardrail applies.

This translation is for interoperability with severity floors and revision checklist integration only. The audit's own outputs use Spot/Pattern/Systemic + Keep/Recast/Replace + source-triage verdicts because those three axes are more informative for the author's revision work.

### The Surface-Tell Question

Writers and editors often maintain lists of "AI words" and surface tells — em-dash frequency, "delve," "tapestry," the magic triple. These lists are useful but unstable: they decay as models change and as writers learn to avoid them. AIC-7 is designed to be more durable than a word list because it targets *discourse habits* rather than *vocabulary*. "Delve" will stop being a tell when models stop overusing it. But the tendency to hedge, to organize in threes, to throat-clear before revelations, to qualify every commitment — these reflect how language models process and present information, not which words they favor. The habits will evolve more slowly than the vocabulary.

The named patterns within AIC-7 (Negation Hedge, Disguised Correctio, Pseudo-Aphorism, Manifesto Cadence) and within AIC-2 (Indefinite-Pronoun Gesture) are syntactic rather than lexical. They survive vocabulary changes across model generations because they are structural moves, not word choices.

That said, AIC-7's Lexical Convergence category does maintain a per-project watchlist of recurring prestige vocabulary. This is the one evidence category most sensitive to model generation. The watchlist is project-specific (flagging words that converge in *this* manuscript) rather than universal (flagging words from a master list of "AI words"), which gives it some durability. But auditors should expect the typical convergence candidates to shift over time. The repetition audit script handles automatic candidate surfacing against a writer's personal baseline.

### Lexical Convergence: A Historical Note

The convergence problem is easier to understand historically. ChatGPT-4o's signature was a set of prestige nouns and verbs — "delve," "tapestry," "navigate," "landscape," "nuanced," "multifaceted," "underscores," "fostering" — used at rates wildly elevated over normal human frequency. "Delve" became a meme because it went from a word most writers use once a year to one appearing in every third response. The tell was rate, not meaning.

Sonnet 3.5's signature was different: more em-dashes, more "I couldn't help but," more reaching for lyrical register in contexts that didn't warrant it. "Architecture" and "choreography" as metaphors for non-physical processes belong to this lineage. The lexical convergence was less about individual prestige nouns and more about tonal defaulting — a tendency to make everything sound slightly literary.

These specific signatures decay within a model generation or two. Early GPT-3.5 had different tics than GPT-4, which had different tics than 4o. Sonnet 3.5 reads differently from 3.7. The particular words are snapshots. But the *habit of convergence* — reaching for the same word across contexts where a human writer would differentiate — persists across all of them. That habit, not any token list, is what Lexical Convergence diagnoses.

This historical framing is a design note, not an operational criterion. The audit should never flag a word because it appears on a list of "ChatGPT words" or "Claude words." It flags convergence: the same term doing duty across contexts where the manuscript should have reached for something more specific.

### The Em-Dash Question

The em-dash reduction skill handles a specific surface tell. This audit handles the categories underneath. They are complementary: a writer whose AI-generated prose has both AIC-1 (Generic Hand) and excessive em-dashes should run both. The em-dash skill is a scalpel; this audit is a diagnostic.

### What v2.0 Adds Over v1.0

Version 2.0 (May 2026) extends v1.0 in five ways:

1. **Layer A pre-scan.** Optional computational step that produces a band classification and per-signal compression magnitudes against a personal or genre baseline. Surfaces manuscript-wide patterns single-passage scans miss. Three Python scripts implement variance, manuscript-aggregate, and vocabulary-repetition diagnostics.
2. **Named subtypes.** Indefinite-Pronoun Gesture (within AIC-2), Negation Hedge, Disguised Correctio, Pseudo-Aphorism, Manifesto Cadence (within AIC-7). Sharper instances writers can search for.
3. **Argument-shaped nonfiction parallel pattern set.** Five patterns (Abstraction Shielding, False-Balance Construction, Hedge-and-Affirm, Recommendation Template, Authority Laundering) for testimony, briefs, op-eds, scholarly articles, and policy memos.
4. **Source triage step (Step 5).** Voice attribution layer with the payoff test, voice slip vs. lost callback distinction, earned-by-frame verdict.
5. **Cross-detector caveat (AIC-4 Pangram signal-9 tension).** Distinguishes bad drift from natural drift; addresses the failure mode where smoothing register seams trips third-party detector confidence.

The v1.0 spec is preserved in full. All v2.0 additions are integrative rather than restructuring.
