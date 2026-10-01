# Specialized Audit: Shelf & Positioning
## Version 0.4.4
*Last Updated: February 2026*

---

## Purpose

To diagnose the gap between the book the author *thinks* they wrote (Intended Shelf) and the book the text *actually* projects (Evident Shelf). This audit treats "Shelf" as a testable hypothesis about reader expectations.

**When to activate:**
- **Early Drafting:** To verify concept viability
- **Intake/Calibration:** To ensure Contract matches Market
- **Pre-Submission:** To sharpen query/pitch
- **Symptoms (Reader-Side):** Beta readers say "I didn't know what to expect" or "It started slow"
- **Symptoms (Acquisition-Side):** Consistent rejections with similar feedback; editors say "loved it but couldn't place it"

**Core principle:** If you can't choose a primary shelf, you don't have positioning yet—you have ambiguity.

---

## Runtime Modes

| Mode | Time | When to Use | Sections |
|------|------|-------------|----------|
| **Fast Pass** | 20-30 min | Quick positioning check, early drafts, time-constrained | Parts 0, 1, 3.1–3.3, Shelf Memo fields only |
| **Full Pass** | 60-90 min | Comprehensive analysis, pre-submission, persistent issues | All Parts 0-6, full Shelf Memo |
| **Acquisition Pass** | 90-120 min | Pre-submission with rejection history, publisher targeting | Full Pass + Part 8 (Pre-Acquisition) |
| **Learning Pass** | Add 30 min | Post-rejection analysis, framework refinement | Add Part 9 (Rejection Forensics) |

**Fast Pass outputs:** Shelf decision, 2-3 comps, primary risk, one-paragraph recommendation.

**Full Pass outputs:** Complete Shelf Memo with all sections.

**Acquisition Pass outputs:** Full Shelf Memo + Acquisition Positioning Brief.

---

## Reference: Shelf Standards

**Trade (US/Canada):** BISAC subject headings, maintained by Book Industry Study Group (BISG). Best practice: ≤3 codes per title.

**Trade (Global/UK):** Thema subject categories, maintained by EDItEUR. Supports qualifiers for place, time, interest age, style. Replaces obsolete BIC codes.

**Library:** Dewey Decimal Classification for nonfiction; fiction usually shelved by author with local genre labels. Less relevant for trade positioning decisions.

---

## Part 0: Preflight — Lane Gates

*Lock these in before proceeding. Tentative answers are fine; inability to answer is a finding.*

| Gate | Decision |
|------|----------|
| **Mode** | Fiction / Nonfiction |
| **Audience lane** | Adult / YA / MG / Chapter / Picture |
| **Market posture** | Commercial / Upmarket / Literary (choose one primary) |
| **Format** | Standalone / Series / Collection |
| **Structure notes** | Dual timeline? Multiple POV? Nonlinear? Illustrated? |
| **Content boundaries** | Heat level / Violence level / Major triggers (if relevant) |
| **Value proposition** | Hook-driven (High Concept) / Voice-driven (Execution) |
| **Primary market locale** | US/Canada / UK/IE / ANZ / Global/Other |

**Logic Gate:**
```
IF any gate cannot be answered → FLAG: "Positioning Not Ready"
(The book's identity isn't clear enough to test shelf fit.)
```

**Market Locale Note:**

Locale determines which metadata standard applies and which retailer signals matter:

| Locale | Metadata Standard | Key Retailers |
|--------|------------------|---------------|
| **US/Canada** | BISAC (Book Industry Study Group) | Amazon US, B&N, indie bookstores |
| **UK/IE** | Thema (EDItEUR) — replaces obsolete BIC | Amazon UK, Waterstones, WHSmith |
| **ANZ** | Thema preferred, BISAC accepted | Booktopia, Dymocks |
| **Global/Other** | Thema (international standard) | Varies by territory |

Research Mode queries should be locale-aware. US "romantic suspense" may not map cleanly to UK "crime & romance."

**The Hook vs. Voice Switch:**

This gate determines *what the audit prioritizes*. Different books sell on different primary value propositions:

| Type | Sells On | Audit Prioritizes | Shelf Defined By |
|------|----------|-------------------|------------------|
| **High Concept** | The Hook (premise, "what if") | Pacing, plot clarity, concept freshness | The plot |
| **Execution** | The Voice (style, prose, narrator) | Interiority, prose quality, tonal control | The writing |

**Logic Gate: Value Proposition Alignment**
```
IF Value proposition = Hook-driven
  → WEIGHT HIGH: Pacing signals, premise clarity, genre token density
  → WEIGHT LOW: Prose/interiority critiques (unless Tone-Shelf Mismatch is also flagged)

IF Value proposition = Voice-driven
  → WEIGHT HIGH: Prose quality, tonal coherence, interiority density
  → WEIGHT LOW: Hook clarity complaints (unless Shelf Anchor Missing is also flagged)

IF Audit flags "hook isn't clear" on Voice-driven book
  → DE-WEIGHT (not suppress): Voice books still need a governing promise,
    but the promise may be tonal/thematic rather than premise-driven.
    Check for Shelf Anchor Missing before dismissing.

IF Audit flags "too quiet" on Voice-driven Literary/Upmarket book
  → DE-WEIGHT (not suppress): Pacing expectations are calibrated differently,
    but the book still needs momentum. Check for Slow Start / Buried Lead.
```

**Why this matters:** *A Gentleman in Moscow* doesn't have a "hook" in the thriller sense. It sells on voice. Evaluating it by hook clarity would be a category error—but it still needs to establish what it *is* early. DE-WEIGHT preserves the signal while adjusting calibration.

---

## Part 1: The Blind Prediction Protocol

*The system performs this analysis BEFORE reviewing author's intended shelf.*

**Procedure:**
1. Ingest Title, Opening Hooks, and First 10% of manuscript
2. Analyze against market signals (voice, pacing, content, tropes)
3. Predict: Where would a bookseller shelve this based *only* on text?

**Output:**
```
Predicted Trade Shelf: [plain language, e.g., "Romantic Suspense" or "Narrative Nonfiction"]
Predicted Audience: [e.g., Adult, skewing female, 25-45]
Confidence: HIGH / MEDIUM / LOW
Key Signals (phrases/tropes): [5-8 semantic signals found in text]
Metadata mapping (optional): BISAC code / Thema code
```

**Confidence calibration:**
- **HIGH:** Clear genre tokens, unambiguous pacing/voice
- **MEDIUM:** Mixed signals, commercial-literary blend
- **LOW:** Upmarket/book-club/literary positioning (market constructs, not textual features)

**Logic Gate: Alignment Check**
```
COMPARE: Predicted Shelf vs. Author's Intended Shelf
IF Match → PASS (Signal is clear)
IF Mismatch → FLAG: "Signal-Structure Mismatch"
  Evidence: [cite specific pages/scenes that created prediction]
```

When confidence is LOW, weight comp analysis more heavily than blind prediction.

---

## Part 1b: Research Mode (Optional)

*Triggered when the system needs current shelf-landscape data.*

**When to activate:**
- Blind Prediction confidence is LOW
- Author's intended shelf is niche, hybrid, or recently emerged (e.g., "cozy fantasy," "romantasy")
- Comps are >5 years old
- Query explicitly asks for current market positioning

**Procedure:**
1. Search for: `[predicted shelf] + "BISAC" OR "comparable titles" + [current year]`
2. Search for: `[author's comps] + reviews + "readers also bought"`
3. If hybrid: search each parent shelf separately

**Output (append to Blind Prediction):**
```
Research Supplement:
- Current shelf terminology: [what industry calls this now]
- Active comps (last 2 years): [3-5 titles with publication dates]
- Emerging sub-shelf: [if applicable, e.g., "cozy fantasy" within Fantasy]
- Confidence adjustment: [raise/lower/unchanged] — [reason]
```

**Guardrails:**
- Research supplements prediction; it doesn't replace structural analysis
- If search returns contradictory signals, note the ambiguity—don't force clarity
- Cap research at **3 tasks** (not 3 literal queries—a task may involve multiple sub-queries)
- More than 3 tasks suggests the positioning problem is structural, not informational

**Research Hygiene:**
```
For each research task, record:
- As-of date: [when research was conducted]
- Market locale: [US/UK/Global]
- Sources consulted: [Publisher Marketplace, Amazon, Goodreads, etc.]
- Confidence: [HIGH if multiple sources agree; LOW if contradictory or sparse]

Cache results by comp title to avoid redundant lookups within session.
Flag any comp data older than 2 years as potentially stale.
```

---

## Part 2: The Signal Density Audit

*Quantifying what the opening broadcasts.*

**Scan first 10% for Genre Tokens:**

| Genre | Tokens to count |
|-------|-----------------|
| **Romance** | Meet-cute, physical awareness, emotional yearning, relationship obstacle, banter |
| **Thriller** | Time pressure, physical danger, high-stakes decision, active antagonist, pursuit |
| **Mystery** | Crime/puzzle introduced, investigation begun, suspects, clues planted |
| **Fantasy** | Magic usage, secondary-world nouns, supernatural entities, quest elements |
| **Horror** | Dread/unease, physical wrongness, isolation, threat that can't be reasoned with |
| **SF** | Speculative technology, future/alternate setting markers, scientific problem |
| **Historical** | Period-specific details, historical figures, era-specific social constraints |
| **Literary** | Interiority density, thematic foregrounding, voice-forward prose, ambiguity |

**Nonfiction Tokens:**

| Category | Tokens to count |
|----------|-----------------|
| **Narrative NF** | Scene-based opening, named characters, sensory detail, dramatic question |
| **Memoir** | First-person intimacy, specific memory, emotional stakes, self-reflection |
| **Popular Science** | Scientific claim, expert citation, "counter to intuition" framing, explanation |
| **Popular History** | Period grounding, historical figure named, archival source, dramatic irony |
| **Prescriptive** | Problem stated, promise of solution, credibility marker, "you" address |

**Nonfiction Authority Audit:**

Nonfiction fails when the Authority Persona conflicts with the Category Promise. Content tokens tell you *what* the book is about; Authority tokens tell you *how* it's being delivered.

| Authority Persona | Voice Markers | Required For | Betrayal |
|-------------------|---------------|--------------|----------|
| **The Guru** (Prescriptive) | Imperatives ("Do this"), direct address ("You"), promise of result, bulleted steps, confident declarations | Self-Help, Business, How-To | Academic distance, excessive hedging |
| **The Witness** (Narrative) | Sensory detail, scene reconstruction, dialogue, emotional interiority, "I saw/felt/heard" | Memoir, True Crime, Narrative History | Preachiness, lessons before story |
| **The Scholar** (Academic) | Citations, qualifiers ("Evidence suggests"), passive voice, systemic analysis, "Studies show" | Big Idea, History, Sociology | Oversimplification, false certainty |
| **The Curator** (Pop-Ref) | Cultural references, synthesis of others' work, witty commentary, "I noticed" | Essay Collections, Cultural Crit | Pretending to original research |

**Logic Gate: Authority Alignment**
```
IDENTIFY: Primary Shelf (from content tokens)
IDENTIFY: Dominant Authority Persona (from voice markers)

IF Shelf = Memoir AND Persona = The Guru
  → FLAG: "Preachiness Risk"
  (Memoir readers want to witness your life, not be taught a lesson.)

IF Shelf = Prescriptive AND Persona = The Scholar
  → FLAG: "Academic Distance"
  (Self-help readers want a coach, not a professor.)

IF Shelf = Narrative NF AND Persona = The Curator
  → FLAG: "Commentary vs. Story"
  (Narrative requires scenes, not just analysis of scenes.)

IF Shelf = Big Idea AND Persona = The Guru
  → FLAG: "Authority Mismatch"
  (Big Idea readers expect evidence, not just confidence.)
```

**Logic Gate: The 10% Threshold**
```
CHECK: Does first 10% contain ≥3 distinct Primary Genre Tokens?
IF Yes → PASS (Promise established early)
IF No → FLAG: "Slow Start / Buried Lead"
  Evidence: [cite what IS present vs. what's missing]

EXCEPTION: If Market posture = Literary/Upmarket,
"Promise established" may be demonstrated by voice + thematic pressure + situation,
even with low genre-token density. One unmistakable shelf anchor also suffices
(e.g., corpse on page 1, meet-cute + mutual attraction + obstacle, magic on-page).
```

**Logic Gate: Upmarket Synthesis Detection**

Upmarket/Book Club is defined by the *collision* of Commercial Pacing + Literary Prose/Themes. Without this gate, the audit will flag upmarket books as "Signal Mismatch" when the blend is the entire point.

```
CHECK: Does first 10% contain BOTH:
  - Commercial pacing signals (plot propulsion, clear dramatic question, accessible entry)
  - Literary signals (high interiority, voice-forward prose, thematic foregrounding)

IF BOTH present at meaningful density (≥3 tokens each)
  → FLAG (positive): "Upmarket Synthesis Detected"
  → Market posture should be Upmarket/Book Club
  → Do NOT flag as "Signal Mismatch"—this is the target blend

IF Commercial tokens HIGH but Literary tokens LOW
  → Straight Commercial (genre)

IF Literary tokens HIGH but Commercial tokens LOW
  → Straight Literary

IF flagging "Signal Mismatch" on a book with Upmarket Synthesis
  → SUPPRESS: The blend is intentional; evaluate by Upmarket standards
```

**Why this matters:** *Lessons in Chemistry* has thriller-level pacing AND literary interiority. Flagging that as "mismatched signals" misses that this IS the upmarket lane.

---

## Part 3: The Five Core Tests

### Test 1: The Algorithm Cluster Test

*Replacing the "Browser Test" with a testable digital proxy.*

Instead of imagining a physical shelf, imagine the "Also Bought" cloud. Where does this book cluster algorithmically?

**1A. The Metadata Keyword Test:**

Generate 5-7 metadata keywords derived strictly from the text (not what the author *wants* the keywords to be):

```
Procedure:
1. Extract: Setting, period, protagonist type, central conflict, tonal markers
2. Generate: Keywords a reader might actually search
3. Test: "If a user searches these keywords on Amazon, what other books appear?"
4. Check: Do the Author's intended Comps appear in that search result?
```

**Logic Gate: Cluster Check**
```
IF Keywords generate Author's Comps → PASS (Positioning is tight)
IF Keywords generate books Author doesn't know → NOTE: "Discovery Opportunity"
  (These might be better comps)
IF Keywords generate books Author actively dislikes → FLAG: "Drift"
  (The book is signaling a different audience than intended)
```

**1B. The Viral Pitch Test:**

Social algorithms favor specific grammatical structures for specific genres. Can your book survive the syntax of its community?

Force the book's hook into the genre-specific format:

| Genre | The Algorithm Syntax | Example |
|-------|---------------------|---------|
| **Romance** | "She's a [X] and he's the [Y] who has to [Z]." | Micro-trope density |
| **Thriller** | "I thought [X] was safe, until I found [Y]." | The reversal |
| **Lit Fic** | "A novel about [Theme A] disguised as a story about [Plot B]." | The layers |
| **Nonfiction** | "Stop doing [X]. Here is the [Y] method instead." | The contrarian value |
| **Fantasy** | "Imagine a world where [System X] determines your [Value Y]." | The novum |
| **Historical** | "The true story of [forgotten figure] who [surprising action]." | The revelation |
| **Upmarket** | "A [warm/devastating/luminous] novel about [universal theme] set in [specific world]." | Accessible + specific |

**Logic Gate: Pitch Syntax**
```
IF book fits the syntax cleanly → PASS (Hook is algorithm-ready)
IF book requires caveats ("Well, it's complicated...") → FLAG: "Hook Drag"
  (The concept isn't sharp enough for algorithmic discovery)
IF book doesn't fit ANY syntax → Consider: Is this a Voice-driven book?
  (Voice books may not need a sharp hook—check Value Proposition gate)
```

**Hard Rule:** You must name ONE primary shelf. If you name more than two, force:
- Primary (must win)
- Secondary (will accept)
- Avoid (must not land here)

**Logic Gate: Shelf Decision**
```
IF cannot name a single primary shelf → FLAG: "Positioning Not Ready"
IF named shelves don't cluster algorithmically → FLAG: "Category Confusion"
  Evidence: [list the shelves named and why they don't cohere]
```

---

### Test 2: The Disappointment Test

If this book reaches the "wrong" reader, what specific element triggers a 1-star review?

| Shelf | The Deadly Sin | Manuscript Check |
|-------|----------------|------------------|
| **Romance** | No HEA/HFN; cheating without consequence; death of lead | [Check resolution] |
| **Mystery** | Unfair solution; coincidence solves it; detective fails | [Check reveal audit] |
| **Thriller** | Pacing collapse; threat fizzles; stakes feel abstract | [Check pacing audit] |
| **Horror** | Not actually scary; threat too explicable; safe ending | [Check dread maintenance] |
| **SFF** | Inconsistent rules; deus ex machina; magic solves everything | [Check rule ledger] |
| **Historical** | Obvious anachronism; modern psychology; setting as wallpaper | [Check voice audit] |
| **Literary** | Unearned sentiment; neat morals; thesis-statement theme | [Check thematic coherence] |
| **Narrative NF** | Dull prose; no narrative momentum; reads like textbook | [Check pacing/voice] |
| **Memoir** | No arc; score-settling tone; protagonist never changes | [Check character audit] |
| **YA** | Adult solves the problem; protagonist lacks agency; preachy | [Check agency quotient] |

**Logic Gate: Dealbreaker Check**
```
IF manuscript contains "Deadly Sin" for Primary Shelf
AND subversion is NOT explicitly in Contract
THEN → STRUCTURAL BREAK: "Contract Violation"
  Evidence: [cite the specific scene/choice that violates]
```

---

### Test 3: The Recommendation Test (Comps)

"If you liked ___ and ___, you'll love this."

**For each comp, identify the Structural Driver:**

| Comp Title | Its Structural Driver | Manuscript's Driver | Verdict |
|------------|----------------------|---------------------|---------|
| [title] | [what makes it work] | [your equivalent] | ✅ Valid / ❌ Vibe-Only |

**Examples of Structural Drivers:**
- *Gone Girl*: Dual unreliable POV + midpoint revelation
- *The Martian*: Competence porn + logistical problem-solving
- *Bridgerton*: Fake dating trope + social season structure
- *Project Hail Mary*: Science puzzle + friendship across difference

**Logic Gate: Comp Validity**
```
IF manuscript shares Structural Driver → PASS (Valid comp)
IF manuscript shares only vibes/setting → FLAG: "Vibe-Only Comp"
  Evidence: [what structural element is missing]
  Warning: Readers of [comp] may be disappointed by different mechanics.
```

**Anti-Comps (Required):**
- "This is NOT for readers of ___ because ___"
- "We should avoid comparison to ___ because it sets expectations we won't meet"

Anti-comps reveal what must be de-emphasized structurally or in opening signals.

**Anti-Comp Divergence Point Constraint:**

Anti-comps are dangerous without discipline—an LLM (or human) can hallucinate reasons to distance any book from any other ("It's not like *Gone Girl* because it's set in space").

**Rule:** A valid anti-comp must share the **Premise** but oppose the **Promise**.

| Anti-Comp | Shared Premise | Opposed Promise | Valid? |
|-----------|---------------|-----------------|--------|
| "Not *Gone Girl*" | Missing wife mystery | *Gone Girl* = dark twist; ours = sincere resolution | ✅ |
| "Not *Outlander*" | Historical + romance | *Outlander* = HEA; ours = protagonist dies | ✅ |
| "Not *The Martian*" | Survival story | *Martian* = competence porn; ours = psychological horror | ✅ |
| "Not *War and Peace*" | ... | "Because it's shorter" | ❌ (no structural opposition) |

**Logic Gate: Anti-Comp Validity**
```
FOR EACH anti-comp:
  IDENTIFY: Shared premise (what surface element creates the comparison)
  IDENTIFY: Opposed promise (what contract element diverges)

IF anti-comp lacks clear premise-sharing → REJECT: "Arbitrary anti-comp"
IF anti-comp lacks clear promise-opposition → REJECT: "Vague anti-comp"
IF anti-comp shares premise AND opposes promise → VALID
```

**Why this matters:** The purpose of an anti-comp is to *prevent wrong-reader acquisition*. "Not for readers of X because Y" must name the specific structural element that would disappoint X readers.

---

### Test 4: The Discovery Test

How does your ideal reader find this book?

| Channel | What matters most | Relevant for this book? |
|---------|-------------------|------------------------|
| **Shelf browsing** | Category codes, cover signals | |
| **Search/algorithm** | Keywords, metadata, also-boughts | |
| **Community (BookTok/Bookstagram/newsletters)** | Comps, tropes, "what to say when recommending" | |
| **Book clubs** | Discussion-worthiness, themes, accessibility | |
| **Awards/reviews** | Literary positioning, topicality, critical frames | |
| **Hand-selling** | Pitch language, staff-pick appeal | |

**Ask:** Which channel is primary? Does positioning support it?

**Logic Gate:**
```
IF primary channel = Shelf Browsing BUT genre tokens are sparse → FLAG: "Discoverability Gap"
IF book signals one discovery route BUT plan assumes another → FLAG: "Channel-Signal Tension"
  Evidence: [cite what signals point where vs. intended channel]
```

---

### Test 5: The Signal Alignment Audit

What is the book broadcasting at each layer?

| Signal Layer | What it's broadcasting | Aligned with Primary Shelf? | Evidence |
|--------------|----------------------|----------------------------|----------|
| **Title/Subtitle** | | Yes / No / Mixed | |
| **Opening scene** | | Yes / No / Mixed | |
| **First 10% pacing** | | Yes / No / Mixed | |
| **Voice/tone** | | Yes / No / Mixed | |
| **Structural payoff** | | Yes / No / Mixed | |
| **Ending mode** | | Yes / No / Mixed | |
| **Comp behavior** | | Yes / No / Mixed | |

**Logic Gate:**
```
IF ≥3 layers show "No" or "Mixed" → FLAG: "Signal-Structure Mismatch"
  (Opening promises one experience, structure delivers another.
   This is often misdiagnosed as "marketing problem" when it's structural.)
```

**Additional Flag: Shelf Anchor Missing**
```
IF book contains elements from multiple shelves
BUT never declares what it is fundamentally about/driving toward
THEN → FLAG: "Shelf Anchor Missing"
  (The book has ingredients but no governing promise.
   This is the most common dev-edit positioning problem—and it's structural.)
```

---

## Part 4: Straddle Strategy

*For books that intentionally cross shelves.*

**Bridge Types:**

1. **The Trojan Horse:** Looks like Genre A (cover/opening), delivers Genre B (theme/depth)
   - *Requirement:* Act I must hit Genre A beats perfectly to buy trust

2. **The Venn Diagram:** Satisfies core promises of both genres (e.g., Romantic Suspense = HEA + Solved Mystery)
   - *Requirement:* Must deliver non-negotiables of both

3. **The Dilution:** Has elements of both but satisfies neither
   - *Result:* "Too scary for Romance readers, too soft for Horror readers"

**Logic Gate: Bridge Integrity**
```
IF straddling two genres:
  CHECK: Does the book deliver non-negotiables of BOTH?
  IF Yes → PASS (Successful bridge)
  IF No → FLAG: "The Mushy Middle"
    Evidence: [which genre's contract is being violated]
```

**Integration with Module Hierarchy:**
```
IF Primary Shelf = [Genre A]
AND Primary Genre Module = [Genre B]
THEN → FLAG: "Category Error"
  (Shelf says Thriller but Module says Literary pacing.
   Shelf takes precedence for MARKETING decisions.
   Module takes precedence for STRUCTURAL revision.
   You must either change the shelf or change the book.)
```

---

## Part 5: Positioning Levers

*What knobs exist for adjusting shelf signal. Diagnosis, not prescription—author decides which to turn.*

| Lever | Range | Affects |
|-------|-------|---------|
| **Opening promise** | Scene choice, POV distance, voice register | What readers think they're getting |
| **Pacing density** | How quickly plot turns arrive | Commercial ↔ Literary feel |
| **Trope visibility** | Foreground vs background | Genre reader satisfaction |
| **Ending mode** | Closure level, ambiguity tolerance | Contract fulfillment |
| **Tone management** | Comic ↔ Earnest ↔ Dark | Audience emotional expectations |
| **Interiority level** | Action-forward vs reflection-heavy | Pacing feel, literary signals |
| **Romance subplot weight** | Central vs peripheral | Romance shelf viability |
| **Research visibility** | Shown vs absorbed | Historical/nonfiction authority signals |
| **Speculative element centrality** | Premise vs texture | SFF shelf viability |

---

## Part 6: Genre Contract Reference

### Fiction

| Shelf | Non-Negotiable | Can Vary | Betrayal |
|-------|----------------|----------|----------|
| **Romance** | HEA/HFN, central love story | Heat, subgenre, setting | Death of lead, no resolution, cheating wins |
| **Mystery** | Solution revealed, fair clues | Detective type, cozy vs noir | Unsolved, unfair withholding, coincidence |
| **Thriller** | Threat resolved, tension maintained | Protagonist type, stakes type | Pacing collapse, threat fizzles |
| **Horror** | Sustained dread, real threat | Supernatural vs psychological | Not scary, too explicable, safe ending |
| **Fantasy** | Consistent magic rules | Hard vs soft, scope | Rules broken for convenience |
| **SF** | Consistent speculation | Hard vs soft science | Hand-wave solutions, science as magic |
| **Historical** | Period authenticity | Research foregrounding | Anachronism, modern psychology |
| **Literary** | Insight, thematic resonance | Ambiguity, experimentation | Neat morals, unearned sentiment |
| **Upmarket/Book Club** | Emotional depth + accessibility | Genre elements, topicality | Inaccessible prose, no emotional landing |
| **Women's Fiction** | Female protagonist's internal journey | Relationship weight, tone | Journey externalized or unearned |

### Nonfiction

| Shelf | Non-Negotiable | Can Vary | Betrayal |
|-------|----------------|----------|----------|
| **Narrative NF** | Story momentum, scene-based | Research density, scope | Textbook feel, no narrative drive |
| **Memoir** | Personal arc, earned insight | Scope, humor level | No transformation, score-settling |
| **Popular Science** | Accuracy + accessibility | Narrative vs explanatory | Dumbed down or impenetrable |
| **Popular History** | Accuracy + narrative momentum | Scope, thesis strength | Dry, no characters, agenda-driven |
| **Prescriptive NF** | Actionable takeaways | Voice, structure | All theory, no application |
| **Essay Collection** | Voice consistency, thematic coherence | Formal vs personal | Random assembly, no through-line |

### YA-Specific

| Element | Expectation |
|---------|-------------|
| **Protagonist agency** | Teen solves the problem (not adults) |
| **Voice** | Authentically teen (not adult-looking-back) |
| **Pacing** | Generally faster than adult literary |
| **Stakes** | Feel enormous (first love, identity, survival) |
| **Ending** | Hope, even in dark stories |

---

## Part 7: Adaptation Potential Assessment

*Evaluating film/TV optionability as part of positioning.*

**⚠️ This section is optional and non-blocking.** Adaptation potential is a bonus consideration, not a core positioning requirement. Do not optimize for "optionability" at the expense of book clarity. A book that works perfectly on the page but is hard to adapt is still a good book. Run this section only when:
- Author explicitly asks about adaptation potential
- Agent/editor has raised film/TV interest
- The book has obvious visual/dramatic strengths worth documenting

**Why this matters for shelf positioning (when relevant):**
- Adaptation potential affects advance size and publisher interest
- "High-concept" and "visual" are selling points agents recognize
- Some books are harder to adapt; knowing this shapes expectations
- Identifying adaptation challenges early allows structural solutions

### Adaptation Strengths Checklist

| Factor | Question | Score |
|--------|----------|-------|
| **Visual potential** | Does setting/action translate to screen? | HIGH / MED / LOW |
| **Clear dramatic engine** | Is there a propulsive "what happens next"? | HIGH / MED / LOW |
| **Marketable hook** | Can you pitch it in one sentence? | HIGH / MED / LOW |
| **Character castability** | Are leads vivid, actable, star-worthy? | HIGH / MED / LOW |
| **Timely angle** | Does it connect to current cultural conversation? | HIGH / MED / LOW |
| **Emotional payoff** | Does ending deliver (even if bittersweet)? | HIGH / MED / LOW |
| **Scope manageability** | Can it be filmed on reasonable budget? | HIGH / MED / LOW |

**Logic Gate: Adaptation Viability**
```
COUNT factors rated HIGH
IF ≥5 HIGH → Strong adaptation potential
IF 3-4 HIGH → Moderate potential (depends on execution)
IF ≤2 HIGH → Book-native strengths; adaptation would require significant reimagining
```

### Adaptation Challenges & Solutions

**Common challenges that reduce optionability—and how to solve them:**

| Challenge | Why It's Hard | Solution for Screenwriter |
|-----------|---------------|---------------------------|
| **Metafictional narrator** | Film can't be "read"; meta-layer loses medium | Voice-over with visual presence (*Amélie*, *Grand Budapest*); narrator as character who appears on screen; frame story with narrator telling the tale |
| **Heavy interiority** | Can't film thoughts | Externalize through dialogue, behavior, visual metaphor; use confidant character; selective voice-over for key moments |
| **Epistolary structure** | Letters don't move | Show scenes the letters describe; intercut writing with events; use letters as voice-over bridge |
| **Ensemble without clear lead** | Studios want a star vehicle | Choose POV for film; composite characters; restructure around one arc |
| **Ambiguous ending** | Test audiences hate ambiguity | Preserve ambiguity through image, not dialogue; offer "emotional closure" even if plot stays open |
| **Long timeline** | Can't film 40 years | Time jumps with visual aging; focus on key moments; frame story from endpoint |
| **Abstract/philosophical content** | Ideas don't photograph | Embody ideas in conflict; make philosophy into dialogue between characters who disagree |
| **Non-visual premise** | Nothing to show | Find the visual correlative; what does this idea *look like* when it affects someone? |

### Adaptation-Specific Comps

When a book has strong adaptation potential, note film/TV comps that could guide a screenwriter:

```
Adaptation Comps:
- [Film/TV title]: [what structural element it solves similarly]
- [Film/TV title]: [what tonal register it matches]

Adaptation Challenge: [specific challenge from manuscript]
Solution Model: [film that solved similar challenge] — [how they did it]
```

### Output: Adaptation Brief

```
ADAPTATION POTENTIAL: HIGH / MODERATE / LOW

Strengths:
- [Visual element]
- [Dramatic engine]
- [Marketable angle]

Challenges:
- [Challenge 1]: [Suggested solution]
- [Challenge 2]: [Suggested solution]

Market Lane: Prestige drama / Commercial rom-com / Limited series / Animation / [other]

Adaptation Comps:
- [Film 1]: [why]
- [Film 2]: [why]

Notes for Screenwriter:
[1-3 sentences of specific guidance for the trickiest adaptation problem]
```

---

## Part 8: Pre-Acquisition Positioning (Gatekeeper Shelf)

*When the problem isn't finding readers—it's finding a publisher.*

**When to activate:**
- Book has received consistent rejections with similar feedback
- Feedback suggests positioning confusion ("didn't know where to place it," "loved it but couldn't figure out the list")
- Book straddles categories in ways that create acquisition anxiety
- Author is preparing submissions and wants to anticipate objections

**The core insight:** Trad publishing doesn't buy "a good book." It buys a positionable product that can survive internal handoffs:

```
Editor champions it → Acquisitions committee → Sales conference → Retailer pitch → Marketing copy → Consumer
```

Shelf confusion at the gatekeeper level often means:
- No clear internal story ("what is it?")
- No comp economics ("what sold like this, and why?")
- No imprint home ("who publishes this kind of thing?")

---

### Three Shelves, Not One

The audit so far focuses on **Reader Shelf** (where does the ideal reader look?). But acquisition requires two more:

| Shelf | Question | Who Cares |
|-------|----------|-----------|
| **Reader Shelf** | Where does the ideal reader browse? | Marketing, eventual consumer |
| **Retail Shelf** | Where can retailers/algorithms place it? | Sales team, bookstore buyers, Amazon categories |
| **Gatekeeper Shelf** | What category lets an editor sell it internally with comps? | Editor, acquisitions committee, P&L spreadsheet |

**Logic Gate: Shelf Alignment**
```
IF Reader Shelf is clear BUT Gatekeeper Shelf is unclear
  → FLAG: "Acquisition Gap"
  (Book may be loved; not obviously buyable.)

IF all three shelves align → PASS (clean positioning)
IF Retail ≠ Reader → FLAG: "Discovery Mismatch" (readers want it; can't find it)
IF Gatekeeper ≠ Reader → FLAG: "Acquisition Gap" (readers want it; editor can't buy it)
```

**"Too funny for literary historical"** is usually a Gatekeeper Shelf problem: the editor can't locate an internal story that sales/marketing will get behind.

---

### The Acquisitions Pitch Test

**You have 30 seconds in an acquisitions meeting. Can you finish this sentence?**

> "This is a **[shelf label]** novel for readers of **[comp1]** and **[comp2]**, and we can sell it because **[one concrete reason]**."

**Required outputs:**

1. **One internal label** (often broader than consumer shelf)
   - e.g., "upmarket historical with comic voice," "literary satire," "book club historical," "voice-driven commercial"

2. **Two comps with sales plausibility** (not just aesthetic kinship—see Comp Economics below)

3. **One merchandisable hook**
   - Time/place, scandal, concept gimmick, premise engine, "big question," debut angle, etc.

**Logic Gate: Pitch Coherence**
```
IF you cannot produce a clean 30-second acquisitions pitch
  → FLAG: "Internal Story Missing"
  (The book is good; the business case isn't obvious.)
```

---

### Comp Economics

**Why "vibe comps" kill deals.**

Structural driver matters (Test 3 in Part 3), but gatekeepers need one more column: *why did the comp sell?*

| Comp | Structural Driver | Shelf/Label | Why Publisher Believes It Sold |
|------|-------------------|-------------|-------------------------------|
| [title] | [what you share] | [its shelf] | [book club, awards, author brand, controversy, TikTok, hook, etc.] |

**Sales mechanisms to identify:**
- Book club adoption (Reese's, GMA, etc.)
- Award momentum (Booker longlist, etc.)
- Author platform/brand
- Controversy/news hook
- TikTok/BookTok virality
- Stunning reviews/blurbs
- Adaptation buzz
- Hand-selling/indie love
- Category dominance (owned the niche)

**Logic Gate: Comp Economics**
```
IF comps are structurally valid BUT do not explain a sales mechanism
  → FLAG: "Comp Economics Missing"
  (The comps feel right but don't answer "why will THIS sell?")

IF comps share a sales mechanism the manuscript can plausibly access
  → PASS (business case exists)
```

**The hard question:** Your comp sold because [X]. Can YOU access [X]?

- If *Lessons in Chemistry* sold partly on book club momentum, can you get book club attention?
- If *A Gentleman in Moscow* sold on author's prior success, what's your debut path?

---

### The Tone Register Test

**Every shelf has tonal expectations.** Mismatch between content-shelf and tone-shelf creates acquisition anxiety.

| Shelf | Expected Tone Register |
|-------|----------------------|
| **Literary Fiction** | Serious, restrained, interiority-dense, prestige-oriented, ambiguity-tolerant |
| **Upmarket / Book Club** | Warm, accessible, emotionally resonant, discussable, "smart but not difficult" |
| **Commercial Historical** | Propulsive, immersive, plot-forward, emotionally satisfying |
| **Literary Historical** | Serious + period authority, thematic weight, restrained prose, awards-track |
| **Rom-Com** | Witty, light, banter-forward, warm, satisfying |
| **Thriller** | Tense, propulsive, stakes-forward, minimal interiority |
| **Cozy** | Warm, safe, community-oriented, low-threat, comforting |

**Diagnostic: Tone Token Audit**

Scan first 10% for tone markers:

| Register | Tokens |
|----------|--------|
| **Serious/Prestige** | Complex sentences, restrained emotion, thematic foregrounding, ambiguity, moral weight |
| **Warm/Accessible** | Direct address, emotional transparency, humor that invites rather than distances |
| **Comic/Witty** | Banter, wordplay, irony, absurdist situations, narrator winking at reader |
| **Dark/Intense** | Dread, violence, transgression, moral complexity, unflinching content |
| **Light/Comforting** | Low stakes, found family, gentle conflict, reassuring resolution |

**Logic Gate: Tone-Shelf Alignment**
```
IDENTIFY: Primary shelf (from content/structure)
IDENTIFY: Dominant tone register (from prose/voice)
COMPARE: Does tone match shelf expectation?

IF Literary Historical shelf BUT Comic/Witty tone dominant
  → FLAG: "Tone-Shelf Mismatch"
  → Acquisition anxiety: "Too funny for literary" / "Not serious enough for prestige"

IF Commercial shelf BUT Literary/Serious tone dominant
  → FLAG: "Tone-Shelf Mismatch"
  → Acquisition anxiety: "Too slow/quiet for commercial list"
```

---

### The Acquisition Meeting Test

**Can you write one sentence that sounds like it belongs in an acquisitions meeting for a specific imprint?**

Test the pitch against real imprint profiles:

| Imprint Type | Acquisition Pitch Sounds Like |
|--------------|------------------------------|
| **Literary (FSG, Knopf, Graywolf)** | "A meditation on [theme] told through [structure], with prose that [quality]. For readers of [prestige comp]." |
| **Upmarket (Ballantine, Dutton, Atria)** | "A [warm/smart/compelling] novel about [character] navigating [situation], perfect for book clubs. [Commercial comp] meets [literary comp]." |
| **Commercial Historical (Berkley, MIRA, St. Martin's)** | "A sweeping/lush [saga/romance/adventure] set in [period], following [protagonist] as [plot]. For fans of [bestseller]." |
| **Book Club (Pamela Dorman, Viking)** | "An emotionally resonant novel about [universal theme] that will spark discussion. Comp to [book club hit]." |

**Logic Gate: Pitch Coherence**
```
ATTEMPT: Write acquisition pitch for intended shelf/imprint type
ASSESS: Does it sound natural, or does it require caveats?

IF pitch requires "but it's also..." or "despite the..."
  → FLAG: "Split Positioning"
  → The book is trying to serve two masters

IF pitch sounds coherent for Shelf A but book is being submitted to Shelf B editors
  → FLAG: "Submission Mismatch"
  → Reconsider target editors
```

---

### The List Fit Assessment

**Which imprints have actually acquired similar books?**

Research mode: Search for recent acquisitions that share key features.

```
SEARCH: "[feature 1]" + "[feature 2]" + "acquired by" OR "sold to" + [recent years]
SEARCH: "[comp title]" + "publisher" + "editor"
```

**⚠️ Reliability Warning:**

The "sold to / acquired by" web trail is noisy:
- Press releases are incomplete (not all deals are announced)
- Secondary sources may be rumor or outdated
- Paywalled databases (Publisher Marketplace) aren't always accessible
- Editor movement between imprints creates stale data

**Guardrails:**
- Treat editor/imprint targets as **hypotheses** unless confirmed by reliable sources
- Don't overfit to a single announcement—look for patterns across multiple data points
- Note confidence level: `HIGH` (multiple confirmations) / `LOW` (single source or >2 years old)
- When uncertain, frame output as "plausible homes" rather than "confirmed targets"

**Output:**
```
Books with similar positioning (last 3 years):
- [Title] — acquired by [Imprint] — [what it shares with manuscript] — [confidence]
- [Title] — acquired by [Imprint] — [what it shares] — [confidence]
- [Title] — acquired by [Imprint] — [what it shares] — [confidence]

Pattern: These books landed at [imprint type]. Editors who acquired them: [names if findable].
Implication: [What this suggests about where to submit]
Data confidence: [HIGH/MEDIUM/LOW]
```

---

### The Imprint Orphan Test

**Sometimes it's not shelf confusion—it's "I can't name the imprint this belongs to."**

**Test:** Name 2-3 imprints or "types of lists" this would plausibly fit.

Even without naming specific publishers, you can identify:
- "Upmarket commercial fiction lists" (Ballantine, Dutton)
- "Literary fiction with crossover potential" (Riverhead, Ecco)
- "Historical book club lists" (Pamela Dorman, William Morrow)
- "Voice-driven commercial" (Berkley, Atria)
- "Literary prestige" (FSG, Knopf, Graywolf)

**Logic Gate: Imprint Fit**
```
IF fewer than 2 plausible imprint homes emerge
  → FLAG: "Imprint Orphan"
  (The book's tone/structure is coherent, but it doesn't map onto how lists are organized.)
```

This is often what "too funny for literary historical" actually means: the editor can't locate a home list where sales/marketing will get behind it.

---

### Risk Profile

**Trad acquisition is risk-weighted. Debut math is different from established-author math.**

| Factor | Lower Risk | Higher Risk |
|--------|-----------|-------------|
| **Author status** | Established (track record) | Debut (unknown quantity) |
| **Length** | Standard (80-100K) | Long (higher production cost) |
| **Category clarity** | Clean fit | Hybrid/ambiguous |
| **Discovery path** | Clear (genre community, book club) | Dependent (needs hand-selling, tastemakers) |
| **Market timing** | Fresh or evergreen | Saturated or "over" |

**Logic Gate: Debut Penalty**
```
IF author is debut AND positioning is hybrid/ambiguous
  → FLAG: "Debut Penalty"
  (Hybrid positioning that might work for a known author is harder for a debut.)
```

**Why this matters:** An established author can say "trust me, it works." A debut author needs the category to do more of the selling.

---

### Acquisition Anxiety Identification

**Every book creates specific anxieties for acquiring editors. Name them before they become rejections.**

| Anxiety Type | Editor Thinking | How It Shows in Rejections |
|--------------|-----------------|---------------------------|
| **Category confusion** | "Which meeting do I bring this to?" | "Loved it but didn't know where to place it" |
| **Tone mismatch** | "My sales team won't know how to pitch this" | "Too X for Y readers, too Y for X readers" |
| **Comp difficulty** | "What do I put on the cover?" | "Couldn't find the right comp" |
| **Market timing** | "Did we miss this trend? Is it oversaturated?" | "The market for X has cooled" |
| **Voice risk** | "Will this narrator alienate readers?" | "Voice might be too strong/unusual" |
| **Structure risk** | "Is this too unconventional?" | "Structure might be challenging for readers" |
| **Ending risk** | "Will readers accept this?" | "Worried about reader satisfaction" |

**Diagnostic: Anxiety Audit**

For each potential anxiety, assess:
```
Anxiety: [type]
Present in manuscript: YES / NO / PARTIALLY
How it manifests: [specific element]
Counter-argument: [why this is actually a feature]
Preemptive pitch language: [how to address in query/pitch]
```

---

### The Reframe Protocol

**When consistent rejections cite the same issue, the problem isn't the book—it's the frame.**

**Step 1: Identify the rejection pattern**
```
Consistent feedback: [what editors keep saying]
What they're actually worried about: [underlying anxiety]
```

**Step 2: Test alternative frames**

| Current Frame | Alternative Frame | What Changes |
|---------------|-------------------|--------------|
| Literary Historical | Upmarket Book Club | Drops prestige expectation; gains "accessible + smart" positioning |
| Historical Romance | Historical Fiction with love story | Drops HEA expectation; gains permission for bittersweet |
| Literary Fiction | Speculative / Fabulist | Gains permission for unusual elements |
| [Genre] Fiction | Voice-driven [Genre] | Leads with distinctive voice as feature |
| Serious + Funny | Warmly intelligent / Wry | Names the tone blend instead of fighting it |

**Step 3: Rewrite the pitch in new frame**

Test: Does the pitch now sound coherent without caveats?

**Step 4: Identify editors who've bought the reframed version**

Research mode: Find acquisitions that fit the new frame.

---

### The "Unshelved" Diagnosis

**Some books genuinely don't fit existing categories. This is rare but real.**

**Symptoms:**
- Every frame requires significant caveats
- Comps are all "X meets Y" where X and Y don't naturally combine
- The book's best feature is exactly what makes it hard to place
- Multiple agents/editors have said "love it, can't sell it"

**If genuinely unshelved:**

1. **Acknowledge it.** The book may need a champion editor who acquires on passion rather than category.

2. **Find precedents.** Unusual books do get published. Research: How were they pitched? Which editors took the risk?

3. **Consider timing.** Sometimes markets shift. A book that's "unshelved" today might have clear positioning in two years.

4. **Evaluate structural compromise.** Are there changes that would clarify positioning without gutting what makes the book special? (Author decides—this is a menu, not a mandate.)

5. **Alternative paths.** Small press, indie, hybrid, serial—some books find their readers outside traditional acquisition.

---

### Rejection Data Capture

**When a book doesn't sell, capture the rejection data as structured evidence.**

```
Rejection Record:
  Stage: [agent / editor / acquisitions / other]
  Quoted language: "[exact phrase from rejection]"
  Reason tags: [shelf confusion / tone mismatch / platform / length / market timing / etc.]
  Implied failure mode: [imprint orphan / comp economics / signal mismatch / debut penalty / etc.]
```

**Over time, this builds a "rejection-to-diagnosis" map:**

| Rejection Language | Usually Means | Diagnostic Flag |
|-------------------|---------------|-----------------|
| "Loved it but couldn't place it" | Gatekeeper shelf unclear | Acquisition Gap |
| "Too X for Y readers, too Y for X" | Tone-shelf mismatch | Tone Mismatch |
| "Couldn't find the right comp" | Comp economics missing | Comp Economics Missing |
| "Voice might be too strong" | Risk aversion on unusual element | Voice Risk |
| "Not right for our list" | Imprint orphan | Imprint Orphan |
| "The market for X has cooled" | Timing/saturation | Market Timing |
| "For a debut, we'd need..." | Higher bar for new authors | Debut Penalty |

---

### Output: Acquisition Positioning Brief

```
ACQUISITION POSITIONING ASSESSMENT

Three-Shelf Analysis:
- Reader Shelf: [where ideal reader looks]
- Retail Shelf: [where retailers can place it]
- Gatekeeper Shelf: [what internal label works]
- Alignment: [all match / gaps identified]

30-Second Acquisitions Pitch:
"This is a [label] for readers of [comp1] and [comp2], and we can sell it because [reason]."

Comp Economics:
| Comp | Why It Sold | Can Manuscript Access This? |
|------|-------------|---------------------------|
| [title] | [mechanism] | [yes/no/partially] |

Imprint Fit:
- Plausible homes: [2-3 imprint types]
- Best targets: [specific imprints if known]

Risk Profile:
- Author status: [debut / established]
- Category clarity: [clean / hybrid]
- Discovery path: [clear / dependent]
- Debut Penalty applies: [yes / no]

Flags Raised:
- [ ] Acquisition Gap (readers want it; editor can't buy it)
- [ ] Internal Story Missing (no clean 30-second pitch)
- [ ] Comp Economics Missing (comps don't explain sales mechanism)
- [ ] Imprint Orphan (no obvious list home)
- [ ] Debut Penalty (hybrid + debut = harder sell)
- [ ] Tone-Shelf Mismatch (content says X, voice says Y)

Rejection Pattern (if applicable):
- Consistent feedback: [what editors keep saying]
- Underlying issue: [diagnosed cause]

Reframe Recommendation:
- From: [current frame]
- To: [proposed frame]
- Pitch in new frame: [one sentence]

Target Imprints/Editors:
- [Imprint]: [why / who's acquired similar]
- [Imprint]: [why / who's acquired similar]

Preemptive Pitch Language:
[How to address the main anxiety before it becomes an objection]
```

---

## Outputs: The Shelf Memo

### Style Guidance: Diagnostic vs. Deliverable

**The preceding sections (Parts 0-7) are diagnostic scaffolding**—logic gates, token counts, checklists. This machinery runs internally to generate findings. The author never sees it.

**The Shelf Memo is a professional deliverable.** Write it in fluent, confident prose addressed to the author. Hide the machinery; deliver the insight.

| Element | Diagnostic (Internal) | Deliverable (Author-Facing) |
|---------|----------------------|----------------------------|
| Logic gates | `IF X THEN FLAG` | "The opening currently signals literary fiction more than romance, which creates a mismatch with the intended shelf." |
| Token counts | "3 Romance tokens, 5 Historical tokens" | "The first chapters establish the historical world vividly but delay the romantic promise until Chapter 3." |
| Flags | `FLAG: "Signal-Structure Mismatch"` | "There's a tension between what the title promises and what the prologue delivers—this is worth addressing." |
| Tables | Checklist format | Prose with selective use of tables for comps or at-a-glance summaries |

**Tone:** Collegial, expert, direct. The editor is a trusted advisor, not an algorithm reporting results. Use "I" sparingly but naturally. Recommend, don't command.

**Structure for author-facing memo:**
1. **Executive Summary** (1 paragraph: the headline finding)
2. **Shelf Recommendation** (where this belongs and why)
3. **The Reader** (who finds this book and what they expect)
4. **Positioning Assets** (hook, comps, keywords)
5. **Risks & Considerations** (what could go wrong; what to watch)
6. **Acquisition Strategy** (if book is pre-publication: target editors, anticipated objections, reframe if needed)
7. **Adaptation Potential** (if relevant)
8. **Recommendations** (prioritized next steps)

The template fields below are for *content gathering*. The final memo synthesizes them into prose.

---

### Content Fields (for synthesis into prose)

#### 1. Shelf Decision

```
Primary Shelf: [BISAC code] — [plain language]
Secondary Shelf: [BISAC code] — [plain language]
Avoid Shelf: [what] — [why]
Confidence: HIGH / MEDIUM / LOW
Risk Profile: [Low/Med/High risk of category confusion]
```

### 2. Reader Definition

```
For readers who: [1-3 sentences]
Audience lane: [Adult/YA/MG] + sub-descriptor
Discovery channel: [primary channel]
Content flags: [if relevant]
```

### 3. Positioning Language

```
25-word hook: [elevator pitch]
"If you liked X and Y": [with structural reasons]
"NOT for readers of": [anti-comps with reasons]
Keywords: [8-20 search terms readers actually type]
```

### 4. Comp Set

| Comp | Author | Structural Driver Shared | Actual Shelf |
|------|--------|-------------------------|--------------|
| | | | |

### 5. Signal Alignment Summary

```
Blind Prediction: [matched/mismatched] — [confidence level]
Signal Density: [PASS / FLAG: Slow Start]
Comp Validity: [X of Y comps structurally valid]
Contract Check: [PASS / FLAG: specific violation]
```

### 6. Structural Implications

If flags present, what levers would address them? (Menu, not prescription)

```
Issue: [flag]
Relevant levers: [from Part 5]
Evidence: [specific scenes/chapters]
```

### 7. Adaptation Potential

```
Adaptation Potential: HIGH / MODERATE / LOW
Market Lane: [Prestige / Commercial / Limited Series / etc.]
Key Strengths: [2-3 bullet points]
Key Challenge: [the hardest thing to adapt]
Solution: [how a screenwriter could handle it]
Adaptation Comps: [1-2 films that solved similar problems]
```

---

## Integration with Core Framework

**Input Dependencies:**
- **Pass 1 (Reader Experience):** Provides "Promise Tracking" data
- **Pass 2 (Structural Mapping):** Provides pacing/proportion data
- **Pass 8 (Reveal Economy):** Provides information flow data
- **Genre Modules:** Provide contract specifics

**When to Run:**
- During Intake, after Contract Schema
- During Synthesis, as part of final recommendations
- On Revision, when author reports "it isn't working" without clear cause

**Add to Contract Document:**
```
## Shelf & Positioning

Primary shelf: [X]
Reader promise: [one sentence]
Non-negotiable payoff: [what this shelf demands]
Comps: [2-3 with structural reasons]
Anti-comps: [1-2 with reasons]
```

**Conflict Resolution:**
If Shelf Audit conflicts with Genre Module:
- **Shelf Audit** takes precedence for *marketing* decisions
- **Genre Module** takes precedence for *structural* revision
- Resolution: Change the shelf OR change the book

---

## Part 9: Rejection Forensics

*Turning vague rejection letters into structural data to refine future audits.*

**When to run:** After receiving rejections with substantive feedback. This section closes the learning loop.

---

### The Euphemism Translator

Rejection letters are diplomatic. Map the polite language to structural flags:

| Rejection Phrase | The "Polite" Meaning | Structural Reality (Flag) |
|------------------|---------------------|--------------------------|
| "I didn't fall in love with the voice." | Subjective taste | **Tone-Shelf Mismatch** (Voice didn't match category expectation) |
| "It felt a bit quiet for us." | Pacing issue | **Hook/Voice Switch Error** (Pitched as Hook book, wrote Voice book) |
| "I couldn't find the readership." | Marketing issue | **Imprint Orphan** or **Bridge Failure** (Mushy Middle) |
| "The market for this is tough." | Timing/saturation | **Comp Economics Missing** (No recent proof of sales for this structure) |
| "Loved the concept, execution fell short." | Drafting issue | **Signal-Structure Mismatch** (Opening promised X, delivered Y) |
| "Not right for our list." | Category fit | **Imprint Orphan** (Doesn't map to how lists are organized) |
| "For a debut, we'd need more..." | Risk calculation | **Debut Penalty** (Hybrid positioning harder for unknown author) |
| "The voice might be too strong/unusual." | Audience concern | **Voice Risk** (Distinctive narrator may polarize) |
| "Couldn't find the right comp." | Positioning gap | **Comp Economics Missing** or **Category Confusion** |
| "Loved it but couldn't place it." | Internal politics | **Acquisition Gap** (Gatekeeper shelf unclear) |

---

### The Feedback Protocol

**Step 1: Input**

Paste rejection text (or summarize if verbal):
```
Rejection Source: [Agent / Editor / Acquisitions Committee]
Exact Language: "[quote the key phrase]"
Context: [submission stage, comp titles used, pitch framing]
```

**Step 2: Translate**

Map to structural flags using the Euphemism Translator:
```
Primary Flag: [e.g., Tone-Shelf Mismatch]
Secondary Flag: [if applicable]
Implied Failure Mode: [what structural element caused this]
```

**Step 3: Compare**

Did the Shelf Audit predict this flag?

```
IF Audit predicted this flag:
  → The model works; the author needs to either:
    (a) Edit the manuscript to address the structural issue, OR
    (b) Reframe the pitch to target different gatekeepers
  → Note: Prediction validated

IF Audit did NOT predict this flag:
  → Framework gap identified
  → Update Logic Gates (see Step 4)
  → Note: Model needs refinement for this pattern
```

**Step 4: Refine (if needed)**

When the audit fails to predict a rejection pattern:

```
Pattern observed: [e.g., "quiet" rejections despite passing pacing checks]
Current threshold: [e.g., "≥3 genre tokens in first 10%"]
Proposed adjustment: [e.g., "Raise to ≥5 for Commercial shelf" OR "Add 'propulsive momentum' as separate check"]
Test: Run adjusted gate against known successful books in category
```

---

### Rejection Pattern Database

Over time, build a map from rejection language to diagnosis:

```
REJECTION PATTERN LOG

Entry 1:
  Date: [YYYY-MM-DD]
  Source: [Agent/Editor]
  Language: "[exact quote]"
  Translated Flag: [structural flag]
  Audit Predicted: [Yes/No]
  Resolution: [what changed—pitch, manuscript, or target]
  Outcome: [if resubmission, what happened]

Entry 2:
  ...
```

**Aggregation questions (after 5+ rejections):**

1. Do the flags cluster? (Same issue appearing repeatedly = structural problem)
2. Is there an imprint-type pattern? (Literary imprints say X, commercial say Y)
3. Did reframing help? (Same manuscript, different pitch = positioning was the issue)
4. Did revision help? (Different manuscript, same pitch = structure was the issue)

---

### Learning Loop Integration

The Rejection Forensics section feeds back into the audit framework:

```
IF a rejection pattern emerges that the audit doesn't catch:
  → Add new Logic Gate or adjust threshold
  → Document in "Framework Updates" log
  → Re-run audit on current manuscript with new gate

IF audit consistently predicts rejections correctly:
  → Framework is calibrated for this author/genre combination
  → Focus on addressing structural issues rather than refining detection
```

**The goal:** Transform "subjective" rejections into actionable structural feedback. Every rejection is data.

---

*This audit treats shelf as a testable hypothesis. The shelf you choose determines who finds your book and what they expect. Get it right, and readers arrive prepared to love what you've written. Get it wrong, and even a good book generates disappointed reviews.*
