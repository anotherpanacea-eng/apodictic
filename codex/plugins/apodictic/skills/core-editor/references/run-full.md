# Full DE Passes & Supplementary Audits

*Reference file for the APODICTIC Development Editor. Loaded when selected pass set includes advanced passes (3, 4, 6, 7, 9, 10), including full-pass expansion.*

**Expansion policy:**
Use this file when the user requests "full diagnostic" explicitly, or when auto-escalation recommendation criteria in `references/pass-dependencies.md` §2b are met and the user accepts expansion.

---

## Full DE Passes

### Pass 3: Rhythm and Modulation

Quantitative analysis to investigate Pass 1 flags only.

**Measure:**
- Sentence length variation
- Active verb density
- Dialogue-to-prose ratio
- Compression ratio (story time / word count)

**Constraint:** Metrics cannot flag scenes unless Pass 1 also logged an issue.

**Output:** `[Project]_Pass3_Rhythm_Modulation_[runlabel].md` — Intensity map (visual scene-by-scene trajectory using ASCII or table format), peak-valley pattern analysis, relief ratio assessment, sentence-level rhythm sampling at 3+ distributed points, pacing diagnosis with specific scenes flagged, title/framing architecture evaluation (when conceit detected). Genre modules may add genre-specific checks (e.g., dread fatigue threshold for horror, clock-pressure rhythm for thriller).

**Title/Framing Architecture (conditional — evaluate only when present):**

If the manuscript uses a deliberate titling conceit, epigraph sequence, section-header system, or other paratextual framing device, evaluate whether it functions as structural argument or decoration.

- **Detection:** Identify any consistent pattern in chapter titles, part titles, epigraphs, or section headers that suggests a governing conceit (e.g., a taxonomic system, a recurring source text, a progression that mirrors or counterpoints the narrative arc).
- **Deepening test:** Does the conceit develop across chapters — gaining complexity, irony, or weight — or does it repeat at a fixed register? A title sequence that deepens is load-bearing architecture; one that holds steady is wallpaper.
- **Counterpoint test:** Does the framing layer create meaning the prose alone doesn't deliver? If you stripped the titles/epigraphs, would the manuscript lose structural argument or only lose flavor?
- **Coherence test:** Does the conceit hold through the full manuscript, or does it lose discipline in later chapters (abandoned pattern, forced fit, tonal drift between framing and content)?
- **Flag if:** Framing conceit is present but ornamental (titles could be swapped without loss), OR conceit is load-bearing but loses coherence after midpoint, OR conceit creates ironic counterpoint the prose never earns or acknowledges.

**Finding-driven audit triggers:**
- Intensity plateau at 3+ consecutive high-intensity scenes → recommend **Stakes System** audit (pressure may be signaling without escalating)
- Pacing stalls specifically at scene boundaries → recommend **Scene Turn** audit (Bickham scene-sequel mechanics)
- Title/framing conceit detected but flagged as ornamental or losing coherence → recommend **Literary Craft** audit (the ornamental/load-bearing question at prose level may extend to other structural layers)

### Pass 4: Emotional Value Tracking

Track shifts on three axes:

**Valence:** Better ↔ Worse
**Intensity:** Calm ↔ Charged
**Certainty:** Confident ↔ Epistemically Destabilized

**Certainty decreases when:**
- Characters revise interpretation
- Competing explanations introduced without adjudication
- Sensory evidence conflicts with stated belief
- Causality becomes opaque
- Body contradicts mind

**Certainty increases when:**
- Hypothesis confirmed
- Boundary articulated and respected
- Hidden motive revealed and integrated
- Rules clarified

**Detect:** Static scenes (no movement on any axis), static sequences, redundant oscillation, intensity plateau.

**Output:** `[Project]_Pass4_Emotional_Value_Tracking_[runlabel].md` — Three-axis tracking table (certainty, intensity, valence per scene), certainty trajectory visualization for each POV character and reader, threshold checks (certainty stasis, premature collapse, intensity plateau, missing valleys), genre-specific axis emphasis where applicable (e.g., certainty axis as primary for horror, valence axis for romance). Note any emergent axes the manuscript introduces beyond the standard three.

**Finding-driven audit triggers:**
- Triple stasis (no movement on any axis) at 2+ scenes → recommend **Emotional Craft** audit (transmission may be failing even when events occur)
- Intensity plateau without certainty movement → recommend **Stakes System** audit (stakes may be signaling without converting)
- Certainty axis static in horror/thriller → recommend **Horror Craft** or **Mystery/Thriller Architecture** (dread/information architecture may be inert)

### Pass 6: Scene Function Audit

**Functions:**
- Advances plot
- Reveals character
- Builds tension
- Delivers theme
- Provides information
- Develops relationship
- **Promise/Setup**
- **Payoff**

**Detect:** Single-function, zero-function, redundant scenes, setup debt, orphan payoffs.

**Output:** `[Project]_Pass6_Scene_Function_[runlabel].md` — Scene function map (primary and secondary functions per scene, with "earns its space?" verdict for each), function distribution table, multi-function density analysis, reality test tracking where applicable. Genre modules may add genre-specific function tags (e.g., horror scene function tags, romance relationship-beat tags). Identify zero dead scenes or flag those that don't earn their place.

**Finding-driven audit triggers:**
- Single-function or zero-function scenes at >30% → recommend **Scene Turn** audit (Bickham scene mechanics may explain why scenes aren't earning their space)
- Setup debt or orphan payoffs concentrated in specific acts → recommend **Stakes System** audit (setup without payoff may indicate stakes signaling without conversion)

### Pass 7: POV and Voice

Track POV holder, narrative distance, information access, **tense**.

**Quantitative POV Distribution:**
```
| POV Character | Word Count | % of Total | Sections |
```

**Flag:** POV character <15% in multi-POV novel; POV characters who disappear in later acts; imbalance between equally weighted characters.

**Second Person Considerations:**
- Track total word count in second person
- Flag if >50,000 words without variation (reader fatigue risk)
- Consider: Does POV choice match power dynamic?

**Detect:** Perspective slips, head-hopping, voice intrusion, distance inconsistency, **POV-power mismatch**.

**Voice Distinctiveness Comparison (multi-POV manuscripts):**

For manuscripts with 2+ POV characters, compare the cognitive texture of each POV character's interiority. The goal is to test whether each POV genuinely thinks differently — not just about different topics, but with different cognitive machinery.

Compare across these dimensions:
- **Sentence architecture:** Length distribution, syntactic complexity, clause nesting. Does one POV think in fragments and another in subordinate clauses?
- **Attention pattern:** What does this character notice first in a scene? Sensory hierarchy, social vs. environmental focus, threat vs. beauty orientation.
- **Metaphor source domain:** Where does this character draw comparisons from? Professional vocabulary, body experience, childhood, nature, mechanical systems?
- **Temporal orientation:** Does this character dwell on the past, anticipate the future, or inhabit the present? How does memory intrude on narration?
- **Epistemic style:** How does this character process uncertainty? Anxious cataloguing, confident assertion, deliberate avoidance, pattern-seeking?
- **Emotional register:** How does this character experience and name (or fail to name) emotion? Somatic, analytical, deflective, performative?

```
| POV Character | Sentence Style | Attention Bias | Metaphor Domain | Temporal Lean | Epistemic Mode | Emotional Register |
```

**Flag: Under-individuation** — two or more POV characters share cognitive texture across 4+ dimensions. This typically indicates the author's own cognitive patterns overriding character differentiation. Most visible in high-stakes or emotionally charged scenes, where authorial voice tends to absorb character voice.

**Flag: Selective individuation** — POV characters are distinct in surface markers (vocabulary, topic) but converge in deep texture (sentence architecture, attention pattern, epistemic style). Surface-level differentiation without cognitive differentiation creates characters who *discuss* different things but *think* the same way.

**Output:** `[Project]_Pass7_POV_Voice_[runlabel].md` — POV distribution table (character, word count, % of total, sections), narrative distance tracking, tense consistency log, perspective slip inventory with specific line references, voice distinctiveness assessment per POV character, voice distinctiveness comparison table (multi-POV only).

### Pass 9: Thematic Coherence

Build a complete thematic architecture of the manuscript: what themes are present, how they are dramatized, whether they cohere with the controlling idea, and where thematic integration succeeds or fails.

**Reference project story guides for thematic intent. The contract's controlling idea and anti-idea are the primary calibration anchors.**

#### What to Build

**Thematic inventory.** Identify primary, secondary, and tertiary themes. For each theme, state:
- What the theme *is* (one sentence)
- How it is *dramatized* — through which characters, conflicts, images, or structural patterns (not through narrator declaration or character speechifying)
- Whether it supports, complicates, or contradicts the controlling idea

**Thematic architecture map.** Show hierarchy and relationships among themes. Themes may be:
- *Nested* (secondary theme is a specific case of primary)
- *Tensioned* (two themes create productive friction — this is usually a sign of strength)
- *Parallel* (themes coexist without interaction — may indicate thematic sprawl)
- *Contradictory* (themes undermine each other without the text acknowledging the contradiction)

**Controlling idea alignment check.** Test whether the manuscript's ending structurally supports the controlling idea declared at contract. The test is not whether the theme is "stated" but whether the narrative's causal architecture enacts it:
- Does the climax resolve the central tension in a direction consistent with the controlling idea?
- Does the protagonist's arc demonstrate the controlling idea through choice and consequence, not through realization monologue?
- If the ending is open, does the pressure applied to the central question align with the controlling idea's direction?

**Image system and motif tracking.** Map recurring images, objects, and sensory patterns across the manuscript:
- Where each motif first appears and how it evolves
- Whether motifs accrue meaning through variation or merely repeat
- Whether the motif system coheres with the thematic architecture or runs parallel to it
- Whether the final deployment of a recurring motif applies pressure (deepening, complicating, or inverting its earlier meaning)

**Keyword and semantic threading.** Track words and semantic clusters that carry thematic weight across the manuscript. This is not word-frequency analysis — it is attention to whether the text's own vocabulary builds a coherent associative network around its themes.

What to look for:
- *Deliberate synonym clusters* — a manuscript about confinement that threads "cramped," "bounded," "hemmed," and "cornered" through varied contexts is building thematic texture through language. Track whether the cluster is sustained across the full manuscript or drops out after act one.
- *Vocabulary colonization* — when a character, institution, or force in the narrative has a distinctive vocabulary (clinical language, legal jargon, religious register), track whether that vocabulary infiltrates other characters' internal speech or the narrator's diction. Colonization that deepens across the manuscript is a thematic technique. Colonization that appears and disappears without pattern is a threading gap.
- *Loaded terms* — words that the text invests with specific meaning beyond their dictionary definition. Once a term is loaded (through repetition in charged contexts, through a character defining it, through ironic deployment), the text has committed to that loading. Subsequent uses that ignore the established weight create a threading inconsistency.

What NOT to flag:
- Natural vocabulary variation that serves voice rather than theme
- Recurring words that are functional (character names, setting details) rather than thematically loaded
- Synonym variation that serves prose quality rather than thematic threading — not every word choice is a thematic signal

#### What to Detect

**Theme drift.** The manuscript establishes a thematic direction in early acts but migrates to different thematic territory without the controlling idea evolving to accommodate the shift. Distinguished from legitimate thematic development (where the question deepens or complicates) by whether the original thematic question is answered, transformed, or simply abandoned.

**Theme-as-thesis (didactic delivery).** The theme is delivered as argument rather than dramatized as experience. Symptoms: characters articulate the theme in dialogue or internal monologue; narrator commentary explains what scenes "mean"; the text tells the reader what to conclude rather than building the conclusion through story logic. Flag: *theme-as-explanation* — a character delivers the thesis statement. This is almost always a structural failure regardless of genre.

**Thematic intrusion.** A scene or passage exists primarily to broadcast a theme rather than to advance plot, character, or reader experience. Symptoms: characters engage in philosophical dialogue that doesn't arise from dramatic pressure; convenient artwork, books, or media within the story mirror the theme too perfectly; dream sequences serve as thematic allegory without narrative function. The test: if the thematic content were removed, would the scene still earn its space through causality, character, or tension? If not, the theme is intruding rather than integrating.

**Accidental motifs.** Patterns that emerge from repetition without apparent authorial intent — the text inadvertently builds a motif system the author isn't managing. This can be neutral (the accidental motif doesn't contradict the intended themes) or actively harmful (the accidental motif undermines or distracts from the intended thematic architecture). Flag only when the accidental pattern is strong enough that a reader would register it and when it conflicts with the intended themes.

**Unearned thematic resolution.** The manuscript's thematic question is "answered" by the ending without the narrative having built the causal architecture to support that answer. The ending asserts a thematic conclusion the story hasn't earned through character choice, consequence, and dramatic pressure. Related to but distinct from unearned plot resolution (which is a causality problem, not a thematic one) — thematic resolution can fail even when plot causality is sound, if the thematic pressure hasn't been applied to the right questions.

**Thematic contradiction.** Two themes in the manuscript undermine each other without the text acknowledging or productively using the tension. Distinguish from *productive thematic tension* (where contradiction is the point — the text deliberately holds two positions in friction) by whether the text demonstrates awareness of the contradiction. Productive tension is thematized; unproductive contradiction is invisible to the text.

**Thematic orphan.** An isolated thematic element — a scene, subplot, or motif — that doesn't connect to the manuscript's broader thematic architecture. The element may have internal coherence or aesthetic value, but it is structurally superfluous to the thematic argument. Flag only when the orphan is prominent enough to create reader expectation of thematic significance.

**Thematic overreach.** The manuscript attempts to address too many thematic concerns, diluting the primary controlling idea. Secondary and tertiary themes proliferate without hierarchy, and the reader cannot identify what the manuscript is primarily *about*. Distinguished from rich thematic texture (which deepens one central question through multiple angles) by whether the themes have a legible hierarchy or compete as equals.

#### Genre-Specific Thematic Assessment

When genre modules are active, adjust thematic expectations:

- **Literary fiction:** Theme is often the primary structural engine. Higher tolerance for thematic complexity, ambiguity, and open-ended thematic questions. Lower tolerance for didactic resolution. Motif systems and image architecture carry more structural weight.
- **Horror:** Assess whether the central metaphor (what the monster/threat represents) is consistent and whether the horror dramatizes the theme or merely illustrates it. Psychological horror relies on thematic coherence more heavily than supernatural horror.
- **Romance:** The thematic throughline typically concerns what must change internally before love becomes possible. Assess whether the romance's emotional arc enacts this theme or whether it resolves through external plot convenience.
- **SFF:** Worldbuilding details often carry thematic weight (a magic system's costs may dramatize themes of sacrifice or hubris). Assess whether speculative elements are thematically integrated or decorative.
- **Mystery/thriller:** The investigation structure often enacts a thematic question about truth, justice, or knowledge. Assess whether the resolution's thematic implications are consistent with what the investigation dramatized.
- **Satire/comedy:** Thematic targets must be consistently identified. Assess whether the satire's object is stable or whether it drifts between targets.

#### Cross-Volume Thematic Continuity

When running on a multi-volume work (series continuity audit active), extend thematic tracking to assess:
- Whether thematic threads carry across volumes with development (not just repetition)
- Whether thematic evolution is visible — the question deepens, complicates, or changes across volumes rather than restating
- Whether motif systems evolve (water imagery that shifts meaning across volumes) or simply recur
- Whether thematic continuity provides coherence when factual continuity is intentionally loose (common in literary series and linked collections)

**Output:** `[Project]_Pass9_Thematic_Coherence_[runlabel].md` — Thematic inventory (primary, secondary, tertiary with dramatization and controlling-idea relationship), thematic architecture map showing hierarchy and relationships, controlling idea alignment check with climax-test, image system and motif map with evolution tracking, keyword/semantic threading assessment, genre-specific thematic assessment where applicable, thematic failure flags with specific scene/page references. Flag theme-as-explanation if any character delivers the thesis statement.

### Pass 10: Entity Tracking

Build database of characters, locations, objects, facts. Track state changes.

**For consent-complexity works, also track:**
- Boundaries articulated vs. enacted
- Consent clarity level
- Aftercare/repair status

Detect: state errors, timeline impossibilities, spatial violations, world rule violations, knowledge errors.

**Output:** `[Project]_Pass10_Entity_Tracking_[runlabel].md` — Entity database (characters, locations, objects, facts with state changes tracked), timeline verification, spatial consistency log, world rule ledger, knowledge error inventory. For consent-complexity works: boundary tracking table (articulated vs. enacted, consent clarity level, aftercare/repair status).

---

## Supplementary Audits

Supplementary audits are specialized diagnostic modules that go deeper than any single pass. They are activated at contract (genre/mode-driven) or by finding-driven triggers during passes. See `run-core.md` §Audit Activation at Contract for the full activation table.

Each audit has its own reference file in `specialized-audits/references/`. Load the full module when running the audit. The summaries below describe what each audit does and how it connects to the pass sequence — they are not substitutes for the full audit modules.

### Universal Audits (recommend for every manuscript)

#### Stakes System Audit
**Module:** `specialized-audits/references/craft/stakes-system.md`
**Level-setting:** `specialized-audits/references/craft/stakes-system-level-setting.md`

Evaluates whether the manuscript's stakes system functions as a coherent escalation and consequence engine. Six channels: Stakes Texture (STX), Pressure Conversion (PC), Immediacy Management (IM), Escalation Geometry (EG), Multi-Axis Pressure (MP), Climax Load (CL). 22 named diagnostic flags.

**Pass connections:**
- Feeds from Pass 1 (reader disengagement), Pass 2 (structural mapping), Pass 5 (character wants/costs).
- Feeds into Dashboard Component 8 (Stakes Ladder).
- Pair with Decision Pressure: Stakes evaluates the pressure field; Decision Pressure evaluates choices made inside that field.

**Triggered by:** "Stakes feel low," "I don't care what happens," intensity plateau without escalation, stakes language high but consequence low.

#### Decision Pressure Audit
**Module:** `specialized-audits/references/craft/decision-pressure.md`
**Level-setting:** `specialized-audits/references/craft/decision-pressure-level-setting.md`

Evaluates whether major character decisions are believable under the manuscript's pressure environment. Seven channels: Alternative Visibility (AV), Constraint Specificity (CS), Information-State Integrity (IS), Emotion-Cognition Coherence (EC), Reasoning Fidelity (RF), Tradeoff Reality (TR), Pivot Integrity (PV). 23 named diagnostic flags.

**Pass connections:**
- Feeds from Pass 1 (belief failures), Pass 5 (motivation, agency), Pass 8 (knowledge state, reveal timing).
- Pair with Stakes System: strong stakes + weak decisions is a Decision Pressure problem; weak stakes + weak decisions is a Stakes problem first.
- Pair with Reveal Economy: apparent motivation failures may be information-timing failures.

**Triggered by:** "I don't buy why they did that," convenient pivots, character competence dropping at plot-critical moments, obvious alternatives unaddressed.

#### Scene Turn Diagnostics (Bickham)
**Module:** `specialized-audits/references/craft/scene-turn.md`

Evaluates scene-level mechanics: goal → conflict → outcome, sequel mechanics (reaction → dilemma → decision), scene-sequel chain causality. Named for Jack M. Bickham's *Scene & Structure*. G-, C-, O-, Sq-, H-, U-, P-code flag system.

**Pass connections:**
- Feeds from Pass 2 (scene-level causal gaps), Pass 6 (scene function — Scene Turn explains *why* a scene isn't earning its space).
- Pair with Emotional Craft: Scene Turn identifies missing mechanical turns; Emotional Craft tests whether turns transmit feeling.
- Pair with Decision Pressure: Scene Turn identifies missing decision beats within scenes; Decision Pressure evaluates whether those decisions are credible.

**Triggered by:** "Nothing happens" concerns, scenes that don't earn their space, pacing stalls at scene boundaries, missing transitional decision mechanics.

#### Emotional Craft Diagnostics
**Module:** `specialized-audits/references/craft/emotional-craft.md`

Evaluates emotional precision, earned moments, sentiment tracking, and felt transmission. Diagnoses whether emotional events on the page actually produce felt response in the reader.

**Pass connections:**
- Feeds from Pass 1 (emotional flatness, melodrama), Pass 4 (emotional value tracking — EV tracks axes; Emotional Craft diagnoses transmission failures).
- Pair with Decision Pressure: sound decision logic + weak emotional persuasiveness means architecture is right but transmission is failing.
- Pair with Stakes System: strong stakes + emotional flatness means consequences are present but unfelt.

**Triggered by:** Emotional flatness, melodrama, unearned catharsis, triple stasis in Pass 4, intensity plateau without felt movement.

### Genre and Mode Audits (contract-driven)

#### Force Architecture
**Module:** `specialized-audits/references/craft/force-architecture.md`
**Level-setting:** `specialized-audits/references/craft/force-architecture-level-setting.md`

Evaluates whether physical conflict events produce legible, causal, persistent, meaningful change — or are spectacle loops. 25 flags across 6 dimensions. 8 mode calibrations.

**Pass connections:**
- Feeds from Pass 1 (action scenes that break immersion), Pass 10 (state errors in physical scenes).
- Pair with Decision Pressure: Force Architecture evaluates choreography; Decision Pressure evaluates the decisions within it.

**Activated when:** Contract identifies significant physical conflict (military, progression fantasy, thriller, horror, crime, domestic violence, superhero).

#### Literary Craft Deep Dive
**Module:** `specialized-audits/references/craft/literary-craft.md`
**Level-setting:** `specialized-audits/references/craft/literary-craft-level-setting.md`

Evaluates whether literary-mode techniques (defamiliarization, image systems, subtext, recognition architecture) do narrative work or are cosmetic. 22 flags across 5+1 dimensions. 9 genre-hybrid calibrations.

**Activated when:** Contract identifies literary or upmarket mode.

#### Additional Genre/Mode Audits

These audits activate based on contract signals. Load the full module from `specialized-audits/references/` when activated.

| Audit | Module Location | Activates When |
|---|---|---|
| Mystery/Thriller Architecture | `references/genre/mystery-thriller-architecture.md` | Mystery or thriller in contract |
| Horror Craft Integration | `references/genre/horror-craft.md` | Horror or horror-hybrid in contract |
| SFF Worldbuilding Integration | `references/genre/sff-worldbuilding.md` | SF/F in contract |
| Memoir/Creative Nonfiction | `references/genre/memoir-creative-nonfiction.md` | Memoir or personal narrative in contract |
| Narrative Nonfiction Craft | `references/genre/narrative-nonfiction.md` | Nonfiction with narrative ambitions |
| Historical Fiction | `references/genre/historical-fiction.md` | Historical setting (>50 years before composition) |
| Comedy & Satire | `references/genre/comedy-satire.md` | Comedic voice or satirical intent |
| Character Architecture (full) | `references/craft/character-architecture.md` | Truby Part 9 (moral argument) activated by Pass 5 findings or author request |

### Tag Audits (cross-genre modifiers)

Tag audits evaluate experience-layer promises that sit on top of any genre's structural contract. Activate when contract or marketing signals the tag.

| Audit | Module Location | Activates When |
|---|---|---|
| Erotic Content | `references/tag/erotic-content.md` | Heat level > 0 or intimate scenes present |
| Consent Complexity | `references/tag/consent-complexity.md` | Consent narratively interrogated, power dynamics central |
| Cozy Tag | `references/tag/cozy-tag.md` | Cozy signaling in marketing or tone |
| Philosophical Tag | `references/tag/philosophical-tag.md` | Philosophical themes, novel of ideas |
| Queer Romance/Erotica | `references/tag/queer-romance-erotica.md` | Queer identity central to romance/erotica |

### Supplementary Audit Integration Protocol

1. **Timing:** Supplementary audits run after all activated passes are complete. They consume pass findings as input. They produce companion findings documents.
2. **Synthesis integration:** Audit findings fold into the editorial letter's "What Needs Work" sections — organized by problem, not by audit name. The reader shouldn't need to know which framework found the issue.
3. **Dashboard integration:** Stakes System feeds Component 8 (Stakes Ladder). Decision Pressure feeds a decision module (option-visibility trend, tradeoff payment trend, climax integrity status). Force Architecture feeds action-sequence tracking if physical conflict is present.
4. **Cross-audit coordination:** When multiple audits flag the same scene or decision, coordinate findings. The synthesis should present the unified diagnosis, not three separate audit outputs pointing at the same problem.
5. **Firewall compliance:** All supplementary audits maintain the firewall. They diagnose; they do not prescribe specific content, scenes, or dialogue.

---

## Full DE Deliverables

**Reminder:** All outputs must follow the Author-Facing Language requirement (see `references/output-policy.md`). Translate all framework shorthand on first use.

### Editorial Letter (Full DE)

The Core DE editorial letter format (§Core DE Synthesis in `references/run-synthesis.md`) is the base. The Full DE letter uses the same structure, tone, and principles. Differences at Full DE scale:

1. **Length:** 8-20 pages. The additional passes generate more findings.
2. **"What Needs Work" expands.** Character-level findings (Pass 5), reveal economy findings (Pass 8), and thematic coherence findings (Pass 9) integrate as additional headed subsections — same format (bolded thesis-statement heading, prose argument, embedded line references). They do not appear as numbered passes or as a pass-by-pass walkthrough. The organizing principle is *what the book needs*, not *which pass found it*.
3. **"What the Book Does Best" may draw on more evidence** from character, reveal, and thematic passes. The cap still applies.
4. **Revision Checklist may extend to 15 items** (vs. Core DE's 10). If more than 15 exist, the prose sections carry the rest.
5. **Contract confirmation** can appear as a brief paragraph in "The Short Version" or as a short section between "The Short Version" and "What the Book Does Best."

**Protected Elements at Full DE scale:** The additional passes (character, reveal, thematic) may surface protectable elements that Core DE wouldn't catch — a character voice that works despite structural problems, a reveal sequence that revision must not reorder, a thematic throughline that holds the book together. The Full DE Protected Elements section (§6) may therefore run slightly longer (up to 8 elements vs. Core DE's 3–6), but the same rule applies: every protected element must have been identified as a strength in §3 and must be genuinely threatened by a specific recommendation in §4 or §5.

**Pass 11 integration:** Hard Truths fold into "The Strongest Case Against" (§9). Revision Economics fold into the Revision Checklist. Three-Lens Verdict and Market Reality Check may appear as a brief section between "Revision Checklist" and "Protected Elements," or in an appendix, depending on manuscript context.

**Supplementary audit integration:** Audit findings fold into "What Needs Work" alongside pass findings — organized by problem, not by audit name. The reader never encounters a section titled "Stakes System Findings" or "Decision Pressure Results." Instead, audit evidence strengthens existing sections or creates new headed subsections when it surfaces problems no pass detected. Audit-specific artifacts (Decision Event Map, Stakes Ladder Map, Force Architecture tracking) are referenced in the letter body as needed and listed in Appendix A. The dashboard (see below) visualizes audit-sourced data in Components 8-9+; the letter *argues from* that data.

**Cross-audit overlap rule:** When multiple audits diagnose the same scene or decision point, the letter presents the unified diagnosis once and cites whichever audit's vocabulary is most clarifying. It does not repeat the same problem from three audit perspectives.

### Diagnostic Dashboard

**Purpose:** A single reference artifact that gives the author a visual, at-a-glance picture of the manuscript's structural health. The editorial letter argues in prose; the dashboard *shows* the data the arguments rest on. Authors who want to see the evidence behind a diagnosis look here.

**Output:** `[Project]_Diagnostic_Dashboard_[runlabel].md` — saved to the active project output context beside the manuscript, alongside pass reports and synthesis.

**Format:** Markdown file using ASCII tables and simple text-based visualizations. No external dependencies, no HTML, no images. Must be readable in any text editor or markdown viewer. Use monospace blocks (` ``` `) for visualizations that depend on alignment.

**When produced:** After all Full DE passes are complete but before the editorial letter is written. The dashboard informs the synthesis — findings visible in the dashboard should be referenced (not duplicated) in the letter.

**Author-facing language:** All component headings use plain English. Pass numbers may appear in parentheses for cross-referencing but never as primary labels. See `references/output-policy.md`.

---

#### Component 1: Pacing Heat Map

**Source:** Pass 1 (Reader Experience) + Pass 3 (Rhythm and Modulation)

**Format:** One row per scene/chapter. Columns: scene label, word count, compression ratio (story time / word count), intensity level (1-5 scale derived from Pass 1 emotional tracking), and a visual bar using block characters.

```
Scene/Ch  | Words | Compress | Intensity | ██████████
----------+-------+----------+-----------+----------
Ch 1      | 3,200 | 0.8      | ██░░░     | Slow open — establishing
Ch 2      | 2,100 | 2.1      | ████░     | First pressure
Ch 3      | 4,500 | 0.4      | ██░░░     | [FLAG: stalls after Ch 2 peak]
...
```

**Diagnostic value:** Shows pacing shape at a glance. Flags: flat stretches (3+ scenes at same intensity), missing valleys (4+ consecutive high-intensity scenes), premature peaks, post-climax drag.

---

#### Component 2: Emotional Value Chart (Three Axes)

**Source:** Pass 4 (Emotional Value Tracking)

**Format:** Table tracking all three axes per scene. Each axis uses a directional indicator (↑ rising, ↓ falling, → static, ↕ oscillating) plus a brief state note. One summary row per scene.

```
Scene  | Valence       | Intensity     | Certainty
-------+---------------+---------------+--------------
Ch 1   | → neutral     | → low         | → stable
Ch 2   | ↓ worsening   | ↑ rising      | ↓ destabilized
Ch 3   | → static      | → static      | → static       [FLAG: triple stasis]
Ch 4   | ↓ worsening   | ↑ rising      | ↓ collapsing
...
```

**Below the table:** Brief trajectory summary per axis (1-2 sentences). Note any emergent axes the manuscript introduces beyond the standard three (e.g., desire-certainty axis, trust axis).

**Diagnostic value:** Reveals emotional architecture. Flags: triple stasis (no movement on any axis), premature certainty collapse, intensity plateau, missing valence recovery.

---

#### Component 3: Structural Alignment

**Source:** Pass 2 (Structural Mapping) + Intake (Contract)

**Format:** Side-by-side comparison of the manuscript's actual beat map against the contract's implied structural promises.

```
Contract promises:         Manuscript delivers:
─────────────────         ────────────────────
Escalating dread     →    ✓ 10 escalation beats, no repeats
Reality destabilization → ✓ Certainty axis trends down throughout
Cost (psych/phys)    →    ⚠ Cost concentrated in final 20% — thin middle
Catharsis or denial  →    ✓ Denial — open ending, no resolution
```

**Below:** Proportional analysis — expected structural weight vs. actual (e.g., "Act I is 35% of the manuscript against a 25% target — the setup runs long").

**Diagnostic value:** Shows where the manuscript keeps its promises and where it drifts. Flags: contract violations, proportion imbalances >10 percentage points, promises made in Act I that have no payoff.

---

#### Component 4: Character Agency Timeline

**Source:** Pass 5 (Character Audit)

**Format:** One row per scene per tracked character (protagonist + up to 2 secondary characters). Columns: scene, character, action type (Active Decision / Reactive Response / Passive / Absent), and AQ running total.

```
Character: [Protagonist]    AQ target: >0.40
Scene  | Action                          | Type     | Running AQ
-------+---------------------------------+----------+-----------
Ch 1   | Accepts the appointment         | Active   | 1.00
Ch 2   | Follows instructions            | Reactive | 0.50
Ch 3   | Absent (other POV)              | —        | 0.50
Ch 4   | Discovers the manipulation      | Active   | 0.67
Ch 5   | Freezes                         | Passive  | 0.50  [FLAG: below target]
...
Final AQ: 0.43 [PASS — above 0.40 threshold]
```

**Diagnostic value:** Shows when characters are driving vs. being driven. Flags: AQ below target at manuscript end, 3+ consecutive passive/reactive scenes, agency collapse in Act III (character stops making decisions when it matters most).

---

#### Component 5: Scene Function Matrix

**Source:** Pass 6 (Scene Function Audit)

**Format:** Matrix with scenes as rows and functions as columns. Each cell marked with P (primary function), S (secondary), or blank. Function columns: Plot, Character, Tension, Theme, Information, Relationship, Setup, Payoff.

```
Scene  | Plot | Char | Tens | Theme | Info | Rel  | Setup | Payoff
-------+------+------+------+-------+------+------+-------+-------
Ch 1   | S    |  P   |      |   S   |  S   |      |   P   |
Ch 2   |  P   |  S   |  P   |       |      |  S   |       |
Ch 3   |      |      |      |       |  P   |      |       |        [FLAG: single-function]
...
```

**Below the matrix:** Function distribution summary (e.g., "Theme appears as primary function in 2/15 scenes — may be underserved"). Count of multi-function scenes (target: >60% should serve 2+ functions). Zero-function scenes listed explicitly.

**Diagnostic value:** Reveals scenes that don't earn their space and functions that are structurally underserved. Flags: zero-function scenes, single-function scenes at >30% of total, function deserts (3+ consecutive scenes without a given function that the contract requires).

---

#### Component 6: Promise/Payoff Ledger

**Source:** Pass 6 (Scene Function Audit) + Pass 8 (Reveal Economy)

**Format:** Ledger with one row per setup/promise. Columns: setup (scene + brief description), payoff (scene + description or "UNPAID"), distance (chapters between), and status.

```
Setup                          | Payoff                        | Distance | Status
-------------------------------+-------------------------------+----------+--------
Ch 1: Mysterious prescription  | Ch 8: Side effects revealed   | 7 ch     | ✓ Paid
Ch 2: Locked room mentioned    | —                             | —        | ✗ UNPAID
Ch 3: Character's tremor       | Ch 5: Tremor explained        | 2 ch     | ✓ Paid
Ch 4: "I used to be different" | Ch 11: Memory sequence        | 7 ch     | ✓ Paid
...
```

**Below:** Orphan payoff inventory (payoffs that don't correspond to any visible setup). Setup debt summary (number of unpaid setups, average payment distance).

**Diagnostic value:** Shows the manuscript's promise economy. Flags: unpaid setups at manuscript end, orphan payoffs, front-loaded setup debt (too many promises stacked without intermittent payment), suspiciously short distances (setup → payoff in same scene = no anticipation).

---

#### Component 7: Reveal Ledger

**Source:** Pass 8 (Reveal Economy)

**Format:** One row per significant information reveal. Columns: scene, what's revealed, who learns it (character, reader, or both), method (dialogue, discovery, narration, flashback), and fairness test result.

```
Scene  | Reveal                    | Who learns    | Method     | Fair?
-------+---------------------------+---------------+------------+------
Ch 3   | Medication has side effect| Reader only   | Narration  | ✓
Ch 5   | Doctor knows about it     | Both          | Discovery  | ✓
Ch 9   | Full scope of conspiracy  | Character     | Dialogue   | ⚠ Info-dump
Ch 11  | Protagonist's complicity  | Reader only   | Flashback  | ✗ Withheld
...
```

**Below:** Dramatic irony inventory (what the reader knows that characters don't, and vice versa). Information asymmetry summary.

**Diagnostic value:** Shows information flow and fairness. Flags: reveals that depend on withheld information (fairness violation), reveals delivered entirely through dialogue (info-dump risk), dramatic irony that isn't leveraged for tension, major reveals with no preparation.

---

#### Component 8: Stakes Ladder

**Source:** Stakes System Audit (Supplementary)

**Format:** One row per act or structural unit. Columns: unit, risk type (external / relational / identity / moral / bodily), immediacy (immediate / looming / abstract), and trajectory indicator.

```
Unit    | Risk Type      | Immediacy  | Trajectory
--------+----------------+------------+-----------
Act I   | Relational     | Abstract   | ↑ Establishing
Mid-I   | Identity       | Looming    | ↑ Escalating
Act II  | Identity+Moral | Immediate  | ↑ Escalating
Mid-II  | Bodily+Moral   | Immediate  | → Plateau    [FLAG: stakes stall]
Act III | All axes       | Immediate  | ↑ Peak
...
```

**Below:** Stakes diversity note (does the manuscript rely on a single risk type or layer multiple?). Escalation verdict: does the ladder always go up, or does it plateau or regress?

**Diagnostic value:** Shows whether the stakes earn the climax. Flags: stakes plateau (2+ structural units at same level), stakes regression (higher stakes in Act I than Act III), single-axis reliance (all stakes are the same type), abstract stakes at climax (should be immediate).

---

#### Component 9: Decision Pressure Map

**Source:** Decision Pressure Audit (Supplementary)

**Format:** One row per major decision point. Columns: scene, decision, option visibility (how many alternatives the character/reader can see), tradeoff cost (what the character pays), pivot integrity (does the decision change the trajectory?), and channel flags.

```
Decision Point          | Opt-Vis | Tradeoff  | Pivot? | Flags
------------------------+---------+-----------+--------+------
Ch 3: Accepts the deal  | 3 opts  | Career    | ✓ Yes  | —
Ch 7: Betrays ally      | 1 opt   | None seen | ✓ Yes  | AV-1, TR-1  [FLAG]
Ch 10: Final confession | 2 opts  | Identity  | ✓ Yes  | —
Ch 14: Climax choice    | 1 opt   | Unclear   | ✓ Yes  | AV-2, CS-2, TR-3  [FLAG]
...
```

**Below:** Option visibility trend (should widen then narrow toward climax — premature narrowing flags AV-2). Tradeoff payment trend (should escalate — cost-free decisions flag TR-1). Climax integrity verdict: does the final decision meet all seven channel thresholds?

**Diagnostic value:** Shows whether major decisions are plausible under pressure. Flags: option suppression (character has no visible alternatives), cost-free pivots (decisions without tradeoffs), information-state violations (character acts on knowledge they shouldn't have), deferred consequence erasure (decisions stop mattering).

**Pairing:** Read alongside Component 8 (Stakes Ladder). Strong stakes + weak decisions = Decision Pressure problem. Weak stakes + weak decisions = Stakes problem first.

---

#### Component 10: Force/Action Tracking (conditional)

**Source:** Force Architecture Audit (Supplementary) — include only when audit was activated.

**Format:** One row per physical conflict event. Columns: scene, combatants, force type (interpersonal / structural / environmental), consequence (what changed), persistence (does the change carry forward?), and flags.

```
Scene  | Combatants      | Force Type     | Consequence        | Persists? | Flags
-------+-----------------+----------------+--------------------+-----------+------
Ch 5   | Protag vs Guard | Interpersonal  | Injury (arm)       | ✓ 3 ch    | —
Ch 8   | Protag vs Storm | Environmental  | Route changed      | ✓ rest    | —
Ch 12  | Protag vs Antag | Interpersonal  | Protag wins        | ✗ reset   | FA-8  [FLAG]
...
```

**Diagnostic value:** Shows whether force events produce lasting change or are spectacle loops. Flags: consequence reset (injury/damage disappears), choreography fog (action becomes illegible), force without conversion (violence that changes nothing).

---

#### Dashboard Assembly Rules

1. **Order:** Components 1-8 appear in pass sequence order (pacing → emotional → structural → agency → scene function → promise/payoff → reveal → stakes). Components 9-10 appear after the core sequence; conditional components (Force/Action Tracking) appear only when their source audit was activated.

2. **Length target:** 3-7 pages total. Core components (1-8) should fit in roughly half a page each. Audit-sourced components (9-10) can be briefer if findings are sparse. The dashboard is a reference artifact, not a second editorial letter — keep it tight.

3. **Cross-referencing:** Where a dashboard component reveals a finding that appears in the editorial letter, add a brief pointer: "(See editorial letter: [section heading])." Don't duplicate the argument.

4. **Flags only for real findings.** If a component reveals no issues, include the visualization with a one-line note: "No flags. [Brief positive observation]." Don't manufacture problems to fill space.

5. **Genre module additions.** Genre modules may specify additional columns, rows, or components (e.g., Horror adds a "dread trajectory" row to the Pacing Heat Map; Mystery adds a "clue economy" component). These insert into the relevant component, not as separate sections.

6. **Conditional components.** Components sourced from supplementary audits only appear when those audits ran. Component 8 (Stakes Ladder) and Component 9 (Decision Pressure Map) appear for every Full DE (since those audits are universally recommended). Component 10 (Force/Action Tracking) appears only when Force Architecture audit was activated. Genre audits that produce dashboard-compatible data (Mystery/Thriller clue economy, Horror dread trajectory) integrate into existing components per Rule 5 rather than creating new components.

7. **Confidence markers.** Dashboard findings don't carry individual confidence tags (the visualizations speak for themselves), but the top of the file should note: "This dashboard reflects findings from Passes 1-10 and supplementary audits. Confidence levels for individual diagnoses appear in the editorial letter."

---

## Reference: Certainty Axis Cues

**Decreases when:**
- Characters revise interpretation
- Competing explanations without adjudication
- Sensory evidence conflicts with belief
- Causality becomes opaque
- Body contradicts mind
- Reliable narrator becomes unreliable
- Rules change without warning

**Increases when:**
- Hypothesis confirmed
- Boundary articulated and respected
- Hidden motive revealed and integrated
- Rules clarified
- Character gains self-knowledge
- Mystery resolved

---

## Reference: Structural Frameworks

Diagnostic lenses, not rules.

**Three-Act:** Setup (25%) → Confrontation (50%) → Resolution (25%)

**Save the Cat:** Opening Image → Theme Stated → Setup → Catalyst → Debate → Break into Two → Fun and Games → Midpoint → Bad Guys Close In → All Is Lost → Dark Night → Break into Three → Finale → Final Image

**Story Grid:** Inciting Incident → Progressive Complications → Crisis → Climax → Resolution (per scene)

**Kishotenketsu:** Introduction → Development → Twist → Conclusion (no conflict required)

Use as questions: "Does this have X? If not, is that intentional and working?"
