# Specialized Audit: Compression
## APODICTIC Development Editor
*Audit Classification: Cross-Genre Craft*

---

## §1. Purpose

This audit identifies expendable material in long-form manuscripts — novels, novellas, memoir, and narrative nonfiction — and produces a prioritized cut list with estimated word savings. It is a subtraction-first diagnostic: the operating instruction is *find material to remove, not material to add.*

### Core problem

The core failure is **retained scaffolding**.

A manuscript can preserve material the writer needed during drafting — establishment, orientation, exploration, redundant emotional beats — that the reader does not need during reading. The draft carries its construction equipment into the finished building.

**The fundamental question: What material can be removed or compressed without damaging causality, character, theme, or reader experience — and how many words would that save?**

### Activation

- Author reports "the book is too long" or specifies a word-count target
- Pass 2 identifies ≥3 orphan scenes or proportional imbalance >40% in any part
- Intake constraint includes a target word count below current manuscript length
- Revision-round re-entry with a "cut X words" goal
- Editor/agent feedback: "needs tightening"

### Required inputs

- Pass 0+1 reverse outline with word counts per chapter/scene
- Pass 2 structural map (orphan scenes, repeated beats, proportional analysis)
- Pass 1 reader experience log (disengagement points)
- Manuscript text (for in-scene compression diagnosis)

### Outputs

- Cut List artifact (primary)
- Compression Map artifact
- Compression audit report with flag inventory

### Non-duplication boundaries

1. **Scene Turn** checks whether scenes turn. This audit checks whether material is expendable — a non-turning scene may still be genre-functional (horror dwell, romance processing). Scene Turn tests the engine; this audit asks whether the car should be in the fleet.
2. **Pass 3 (Rhythm)** diagnoses pacing problems — slow spots, rhythmic monotony, modulation failure. Some pacing problems are solved by cutting; others by restructuring, rewriting, or reordering. This audit only addresses "solve by cutting" cases.
3. **Pass 2 (Structural Mapping)** identifies orphan scenes and repeated beats. This audit converts those findings into a prioritized removal plan with estimated word savings.
4. **Short Fiction** evaluates compression economy at short-form scale. This audit operates at long-form scale where the problem is "which of these 300 scenes aren't earning theirs?" rather than "every word must earn its place."
5. **Pass 1 (Reader Experience)** flags disengagement. This audit asks whether disengaging material is load-bearing or expendable.

### What this audit is not

- Not a line-editing pass (it identifies *what* to cut, not *how* to rewrite what remains)
- Not a pacing diagnostic (Pass 3's job — though pacing findings inform cut candidates)
- Not a scene-mechanics audit (Scene Turn's job — though non-turning scenes are cut candidates)
- Not a prose-level tightening exercise (sentence-level compression is outside scope)
- Not a word-count reduction service (it identifies what *can* be cut, not what *must* be cut — the author decides)

---

## §2. Compression Framework

Five channels for diagnosing expendable material. Each channel identifies a different *mechanism* by which material becomes expendable.

**Channel 1: Structural Expendability (SE)**
Material that has no causal connection to the spine. Orphan scenes, vestigial subplots, transitional scaffolding.

- *Integrated:* Every scene connects causally to spine events; removal of any scene breaks a downstream dependency.
- *Partial:* Some scenes are causally connected; others serve only orientation, atmosphere, or character color without advancing the story.
- *Detached:* Multiple scenes or sequences exist with no causal connection to spine events and no downstream dependency.

Detection: Cross-reference Pass 2 structural map. For each scene, trace forward: does any later scene *require* what this scene establishes? If not, it's a candidate.

**Channel 2: Informational Redundancy (IR)**
Material that delivers information the reader already has. Repeated setup, restated backstory, explained subtext.

- *Integrated:* Each piece of information appears once (or appears again only with new meaning — e.g., a detail recontextualized by a reveal).
- *Partial:* Some information is delivered more than once, but second delivery adds nuance, emotional weight, or new context.
- *Detached:* Information is delivered multiple times at the same register without escalation, recontextualization, or new meaning.

Detection: Track key information units (character backstory, world rules, relationship dynamics, plot setup) and count deliveries. Flag any information delivered ≥3 times at the same register.

**Channel 3: Scene Efficiency (ScE)**
Scenes that accomplish their function in more words than the reader needs. Slow turns, extended setups, over-described transitions.

- *Integrated:* Scene length is proportional to dramatic weight. High-stakes scenes get more space; transitional scenes are lean.
- *Partial:* Some scenes run long relative to their function but contain pockets of strong material worth preserving.
- *Detached:* Scenes routinely take 2-3x the words needed for their structural function. Dramatic entry points are buried under setup; scenes continue past their natural exit.

Detection: For each scene, identify the dramatic entry point (where the conflict or turn begins) and the dramatic exit point (where the outcome is clear). Measure words before entry and after exit. Flag scenes where pre-entry or post-exit material meets *both* thresholds: ≥300 words *and* ≥20% of scene length. The combined trigger prevents false positives: a 300-word opening in a 5,000-word scene is 6% and likely fine; a 300-word opening in a 900-word scene is 33% and likely a problem. Neither threshold alone is reliable.

**Channel 4: Emotional Redundancy (ER)**
Emotional beats that restate a previous position without escalation. Character processes the same feeling in the same register; interiority repeats rather than deepens.

- *Integrated:* Each emotional beat advances the character's internal arc. Processing scenes deepen, complicate, or redirect — they don't restate.
- *Partial:* Some processing scenes add new dimension; others circle back to established emotional positions.
- *Detached:* Character revisits the same emotional territory at the same depth ≥3 times without the feeling evolving, complicating, or producing a decision.

Detection: Track emotional positions per character per act. Flag sequences where the same emotion appears at the same register without intervening change.

**Channel 5: Structural Scaffolding (SS)**
Material the writer needed during drafting but the reader doesn't need during reading. Throat-clearing openings, explanatory transitions, setup for setup.

- *Integrated:* The manuscript begins each scene at or near its dramatic entry point. Transitions are minimal. The reader is trusted to bridge gaps.
- *Partial:* Some scenes enter cleanly; others begin with orientation or setup that the scene's action would have provided implicitly.
- *Detached:* Scenes routinely begin 1-2 pages before the drama starts. Transitions explain the gap between scenes rather than letting the cut do the work. Characters arrive at locations, settle in, and *then* the scene begins.

Detection: For a sample of 10-15 scenes, identify where the scene "actually starts" (the first moment of tension, conflict, or new information). Measure the material before that point. Flag scenes where the pre-drama material meets both thresholds (≥300 words *and* ≥20% of scene length) and doesn't contain information unavailable elsewhere.

### Channel overlap and deduplication rule

Channels can diagnose the same passage through different mechanisms — e.g., a transitional scene (SE-3) that also contains throat-clearing (SS-1). When this happens:

1. **Assign a primary flag** based on the dominant mechanism (the one that best explains *why* the material is expendable). The primary flag determines the Cut List entry.
2. **Note secondary flags** in the evidence column but do not create separate Cut List entries for the same passage.
3. **Count word savings once per passage.** If a scene is flagged SE-1 (orphan) and also contains IR-1 (triple delivery), the word savings appear under the SE-1 entry only. The IR-1 is noted as corroborating evidence, which increases confidence — it does not increase the word count.
4. **Cross-channel corroboration increases confidence** (see §4, Confidence Rubric). A passage flagged by two channels is more likely a genuine cut candidate than one flagged by one.

---

## §3. Named Diagnostic Flags

### Structural Expendability flags

| Code | Name | Definition | Default Severity |
|------|------|-----------|-----------------|
| SE-1 | **Orphan Scene** | Scene has no causal connection to any spine event; removal breaks nothing downstream | Should-Fix |
| SE-2 | **Vestigial Subplot** | Plot thread that once served a function (earlier draft, abandoned arc) but no longer connects to the controlling idea or main spine | Should-Fix |
| SE-3 | **Transitional Scaffolding** | Travel, arrival, settling-in, or getting-to-the-scene material with no independent dramatic function | Could-Fix |

### Informational Redundancy flags

| Code | Name | Definition | Default Severity |
|------|------|-----------|-----------------|
| IR-1 | **Triple Delivery** | Same information delivered ≥3 times at the same register without new meaning | Should-Fix |
| IR-2 | **Explained Subtext** | Character or narrator states explicitly what the scene has already shown through action, dialogue, or image | Could-Fix |
| IR-3 | **Re-Establishment** | Setup or backstory re-delivered to a reader who already has it (often at act or part breaks, as if the reader is rejoining) | Could-Fix |
| IR-4 | **Redundant Setup** | Scene exists primarily to establish something that a later scene could establish in its first paragraph | Should-Fix |

### Scene Efficiency flags

| Code | Name | Definition | Default Severity |
|------|------|-----------|-----------------|
| ScE-1 | **Buried Entry** | Scene's dramatic entry point is buried under pre-drama setup exceeding both ≥300 words and ≥20% of scene length | Could-Fix |
| ScE-2 | **Extended Exit** | Scene continues past its natural outcome by both ≥300 words and ≥20% of scene length; post-turn material doesn't establish anything new | Could-Fix |
| ScE-3 | **Slow Turn** | Scene takes ≥2x the words its dramatic function requires; the same turn could be accomplished in half the space | Should-Fix |

### Emotional Redundancy flags

| Code | Name | Definition | Default Severity |
|------|------|-----------|-----------------|
| ER-1 | **Emotional Restatement** | Character revisits the same emotional position at the same depth ≥3 times without escalation, complication, or decision | Should-Fix |
| ER-2 | **Processing Loop** | Character's interiority circles the same concern across multiple scenes without the feeling evolving or producing action | Should-Fix |

### Structural Scaffolding flags

| Code | Name | Definition | Default Severity |
|------|------|-----------|-----------------|
| SS-1 | **Throat-Clearing Opening** | Chapter or major section begins with material the writer needed to warm up but the reader doesn't need to read | Could-Fix |
| SS-2 | **Explained Transition** | Narrative bridges two scenes by explaining the gap rather than cutting cleanly between them | Could-Fix |
| SS-3 | **Setup for Setup** | A scene exists to establish a condition that a second scene uses as setup for the actual dramatic event. The chain has one link too many. | Should-Fix |
| SS-4 | **World-Building Tourism** | Extended description or explanation of setting/system/culture that serves atmosphere but not story — the plot and characters would function identically without it | Could-Fix |

### Severity ladder

| Level | Meaning | Action |
|-------|---------|--------|
| **Could-Fix** | Local issue. Removing this material would improve the manuscript but leaving it doesn't damage the reading experience. | Author's discretion; include in Cut List for awareness. |
| **Should-Fix** | Pattern-level issue. Multiple instances of the same compression failure, or a single instance with significant word-count cost. | Recommended cut; include in Cut List with priority. |
| **Must-Fix** | Systemic or contract-critical. Material actively damages pacing, reader trust, or structural coherence. Triggered by hard gates. | Required cut; prioritize in editorial letter. |

No other severity levels exist. Genre calibration (§6) adjusts the *default assignment* — e.g., SS-4 drops from Could-Fix to a "noted but not flagged" observation in literary fiction where world-building *is* the experience, and rises to Should-Fix in thriller where it's pace-killing. Calibration moves items within the ladder; it does not create levels outside it.

---

## §4. Tracking Artifacts

### Artifact 1: Cut List (primary deliverable)

The audit's main output. Organized from largest estimated cut to smallest.

```markdown
## Cut List — [Manuscript Title]

**Total manuscript word count:** [X]
**Total estimated savings:** [Y] words ([Z]% of manuscript)

### Tier 1: Scene-Level Cuts (Remove Entirely)
| # | Location | Type | Flag | Est. Words | Downstream Check | Confidence |
|---|----------|------|------|-----------|-----------------|------------|
| 1 | Ch.5-7 | Vestigial subplot (Maria's painting) | SE-2 | ~4,100 | Minor callback in Ch.22 — relocate to adjacent scene | Medium |
| 2 | Ch.12, Sc.3 | Orphan scene | SE-1 | ~2,400 | No downstream dependency identified | High |

### Tier 2: Scene-Level Compression (Tighten in Place)
| # | Location | Type | Flag | Current | Target | Savings | Method |
|---|----------|------|------|---------|--------|---------|--------|
| 1 | Ch.3, Sc.1 | Slow turn | ScE-3 | ~3,200 | ~1,500 | ~1,700 | Enter at confrontation; cut arrival/settling material |

### Tier 3: Paragraph-Level Cuts (Redundancy Removal)
| # | Location | Type | Flag | Est. Words | Note |
|---|----------|------|------|-----------|------|
| 1 | Ch.2, 8, 14 | Triple delivery (mother's death) | IR-1 | ~800 | Keep Ch.2 (first delivery + emotional context); cut Ch.8 and Ch.14 restatements |

### Running Total
| Tier | Items | Est. Savings |
|------|-------|-------------|
| Scene-Level Cuts | [n] | [x] words |
| Scene-Level Compression | [n] | [x] words |
| Paragraph-Level Cuts | [n] | [x] words |
| **Total** | **[n]** | **[x] words ([y]%)** |
```

### Confidence Rubric

Every Cut List entry requires a confidence classification. Confidence reflects how certain the audit is that the cut is safe — i.e., that removal or compression will not damage the manuscript downstream.

| Level | Criteria | When to assign |
|-------|----------|---------------|
| **High** | All five Distinguish tests passed (no downstream dependency, no first-and-only information, no emotional escalation, no orientation risk, no genre-contract requirement). Cross-channel corroboration (flagged by ≥2 channels). Downstream safety check completed. | Orphan scenes confirmed by Pass 2 causality trace; redundant material where all deliveries are accounted for. |
| **Medium** | Distinguish tests passed with one residual uncertainty — typically a possible but unconfirmed downstream dependency, or a genre-contract judgment call. Single-channel flag without corroboration. | Scenes that are *probably* expendable but where the causality trace has a gap; material that's redundant in one reading but might serve a subtextual function. |
| **Low** | Distinguish tests indicate expendability but with significant uncertainty — contested genre-contract applicability, ambiguous load-bearing status, or insufficient evidence to rule out downstream damage. | Material where the audit suspects expendability but cannot confirm it without author input; items that depend on authorial intent the text doesn't resolve. |

**Usage rule:** Hard-gate escalation (§7, gate 4) applies only to High-confidence items. Medium and Low items appear in the Cut List but are not escalated by systemic triggers. The author decides.

### Artifact 2: Compression Map

Visual overview showing which parts of the manuscript carry the most expendable material.

```markdown
## Compression Map — [Manuscript Title]

Part/Act distribution of cut candidates:

| Part | Word Count | Cut Candidates | Est. Savings | Density |
|------|-----------|---------------|-------------|---------|
| Part I | 28,000 | 7 | ~4,200 | 15% |
| Part II | 41,000 | 12 | ~8,600 | 21% |
| Part III | 19,000 | 3 | ~1,100 | 6% |
```

Density = estimated savings as % of part word count. Interpretation is mode-aware:

| Mode | "Already lean" | "Likely over-established" | Notes |
|------|---------------|-------------------------|-------|
| **Thriller / Suspense** | <3% | >12% | Lowest tolerance; even 12% suggests significant drag. |
| **Romance** | <5% | >18% | Processing scenes inflate density without being expendable. |
| **Literary Fiction** | <5% | >25% | Higher tolerance for dwell time; only flag density when material is genuinely inert. |
| **SFF** | <5% | >20% | World-building inflates density; verify SS-4 flags are genuine before flagging the part. |
| **Horror** | <5% | >22% | Dwell time may be functional dread-building. |
| **Mystery** | <4% | >15% | Informational precision expected; density usually means detours. |
| **Memoir / Literary Nonfiction** | <5% | >25% | Reflection and digression are structural; highest tolerance. |

Default (genre not listed or hybrid): <5% lean, >20% over-established.

---

## §5. Distinguish Framework

Three-outcome classification for every potential cut:

| Classification | Test | Action |
|---|---|---|
| **Cut** | Removal breaks no downstream dependency; no causality, character arc, emotional payoff, or reader orientation depends on this material | Add to Cut List Tier 1. Assign confidence per §4 Confidence Rubric (High if all five tests clear with corroboration; Medium or Low if residual uncertainty remains). |
| **Compress** | The function is needed but the execution is longer than required; same function can be served in fewer words | Add to Cut List Tier 2 with current/target word counts, compression method, and confidence level. |
| **Keep — Load-Bearing** | Removal would damage causality, character arc, emotional payoff, or reader orientation downstream, even though the material feels slow | Do not add to Cut List; note in audit report as "investigated and cleared" with the test(s) that triggered Keep. |

### Decision tests (apply in order)

1. **Causality test:** Does any later scene depend on information, setup, or emotional state established here? → If yes, investigate Compress before Cut.
2. **First-and-only test:** Is this the only place this information appears? → If yes and the information matters, Keep or Compress — do not Cut.
3. **Emotional-escalation test:** Does this beat advance the emotional arc beyond its previous position? → If no escalation, candidate for Cut (if redundant) or Compress (if first-and-only but overextended).
4. **Reader-orientation test:** Would a reader be confused or disoriented at a later point without this material? → If yes, Keep or Compress.
5. **Genre-contract test:** Does the genre promise require this type of material? → If yes and the material fulfills the promise, Keep even if it feels slow to a cross-genre reader.

### Conflict resolution rules

Tests are applied in order (1→5). When tests produce conflicting signals, use these rules:

- **Keep wins ties.** If any test returns a clear Keep signal (confirmed downstream dependency, confirmed first-and-only, confirmed genre requirement), the item is classified Keep unless the Keep-triggering evidence is itself weak (unconfirmed dependency, speculative genre claim). Weak Keep evidence downgrades to Compress, not Cut.
- **Compress is the default resolution for ambiguity.** When one test says Cut and another says Keep, and neither has decisive evidence, classify as Compress. The material's function is probably real but its current execution is probably longer than needed.
- **Genre-contract test (5) can override earlier Cut signals** but not earlier Keep signals. A passage that passes the causality and first-and-only tests (pointing toward Cut) but fails the genre-contract test (genre expects this material) is reclassified Keep or Compress, not Cut. However, a passage that already has a Keep from test 1 or 2 stays Keep regardless of test 5.
- **When tests 1 and 2 both return Cut, the item is a strong Cut candidate.** Both upstream dependency and information uniqueness are clear — this is the highest-confidence configuration. Apply remaining tests as safety checks, not as independent vetoes.

### Intentional-but-failing rule

Material can be intentional (the author meant to include it) and still expendable. Intentionality is not an exemption. The test is whether the material does work for the *reader*, not whether the *author* wanted it there.

---

## §6. Mode Calibration Matrix

| Mode | Compression Promise | Named Failure Mode | Tighten On | Loosen On |
|---|---|---|---|---|
| **Literary Fiction** | Density is earned through meaning; every passage does thematic or psychological work | **Decorative Density** — prose that performs literary weight without carrying narrative or thematic load; the writing is "good" but the story would lose nothing | IR flags, SS-4 (world-building tourism) | ER flags (interiority is genre-expected; raise threshold to ≥4 restatements) |
| **Thriller / Suspense** | Every scene advances threat or escape; pace never stalls without purpose | **Setup Bloat** — backstory, relationship establishment, and world-building front-loaded before the engine starts | SE-3 (transitional scaffolding), ScE-1 (buried entries) | ScE-2 (some extended exits serve as thriller processing beats) |
| **Romance** | Emotional beats are structural events, not padding; processing scenes advance the relationship | **Processing Spiral** — interiority that circles the same doubt without deepening the conflict or changing the relationship dynamic | ER-2 (processing loops — but raise threshold); IR-1 (relationship dynamics re-explained) | ER-1 (emotional restatement — romance allows more revisiting at lower severity if the register shifts) |
| **SFF** | World-building serves story; orientation is efficient | **Guided Tour** — extended world-building passages that showcase the setting without creating narrative pressure or character consequence | SS-4 (world-building tourism), IR-3 (re-establishment at part/section breaks) | SE-3 (transitional scenes may carry world-building that does double duty) |
| **Horror** | Dwell time builds dread; slowness is a tool | **Inert Dwell** — slow material that is merely slow, not dread-producing; the reader waits without growing uneasy | ScE-3 (slow turns — but verify the slowness isn't generating dread), SS-1 (throat-clearing in horror kills tension) | ScE-2 (extended exits can be horror processing — reader sitting with what just happened) |
| **Mystery** | Every scene delivers or conceals information with purpose | **Informational Detour** — scenes or passages that feel like investigation but deliver no clue, red herring, or character revelation | SE-1 (orphan scenes — but verify they aren't planted red herrings), IR flags | SS-4 (atmospheric setting can be mystery-functional for misdirection) |
| **Memoir / Literary Nonfiction** | Reflection and digression are structural features; the essay is the architecture | **Recursive Reflection** — the narrator returns to the same insight without deepening it; reflection becomes repetition | ER-1 and ER-2 (but only when reflection circles without deepening) | SS-4 (descriptive passages are often the *point*), ScE flags (memoir scenes follow different efficiency norms) |

---

## §7. Severity Hard Gates

Non-negotiable severity floors:

1. **Vestigial subplot consuming >3,000 words or >3% of manuscript word count (whichever is lower) with no spine connection** → Must-Fix. The space cost is too high for material that does no work. The relative guard ensures short manuscripts (e.g., a 50,000-word novella where 1,500 words is 3%) aren't held to an absolute threshold designed for 100k+ novels.
2. **Orphan scene cluster (≥3 adjacent scenes with no causal spine connection)** → Must-Fix. Indicates a section of the manuscript that has detached from the story.
3. **Triple delivery of backstory/setup at same register across ≥3 major structural divisions** (acts, parts, sections — whatever the manuscript uses) → Should-Fix minimum. Indicates a trust-the-reader failure that pervades the manuscript.
4. **Total estimated expendable material >25% of manuscript word count** (requires enumeration pass, not sample extrapolation) → escalate Should-Fix flags to Must-Fix *only for items classified High confidence with validated downstream safety checks* in the densest part. Medium- and Low-confidence items retain their original severity; the systemic finding is noted in the audit report but does not auto-escalate uncertain cuts.

Hard gates override mode calibration loosening.

### Evidence requirements by gate

- **Gates 1-3 can fire from the discovery pass** but require: (a) the flagged material has been directly examined (not inferred from adjacent scenes), (b) the Distinguish tests have been run on the specific item, and (c) the item is classified High or Medium confidence. A Low-confidence item cannot trigger a hard gate even if it meets the quantitative threshold — reclassify to Should-Fix and flag for author review.
- **Gate 4 requires the enumeration pass** (§9, step 5). Sample extrapolation cannot trigger gate 4.

---

## §8. Interaction Patterns

High-value channel interactions where multiple compression channels diagnose the same material:

1. **SE + ER (Orphan Scene × Emotional Restatement):** Scenes that exist to let the character process an emotion they've already processed — expendable on both structural and emotional grounds. Highest-confidence cuts. *Revision implication: cut first, then verify the emotional arc still progresses without the scene.*

2. **IR + SS (Informational Redundancy × Structural Scaffolding):** Setup material that re-delivers information the reader has, delivered through scaffolding the reader doesn't need. Common pattern: "as you know" exposition in transitional scenes. *Revision implication: cut the transition; if the information is needed, it's already delivered elsewhere.*

3. **ScE + SS (Scene Efficiency × Scaffolding):** Scenes that begin with scaffolding (throat-clearing, arrival) and run long (slow turn). Compound problem: late entry + early exit would compress the scene dramatically. *Revision implication: identify the dramatic entry and exit points; compress from both ends.*

4. **ER + IR (Emotional Redundancy × Informational Redundancy):** Character restates both the factual situation and their emotional response to it — "she remembered the accident, and the familiar dread settled in" for the fourth time. *Revision implication: keep the first delivery and the last (if the last adds new depth); cut intermediate restatements.*

5. **SE + ScE (Structural Expendability × Scene Efficiency):** A scene that's partially connected to the spine but accomplishes its function in the first third — the remaining two-thirds are expendable. *Revision implication: don't cut the scene entirely; compress it to its essential function.*

---

## §9. Audit Procedure

1. **Lock scope and mode.**
   - Confirm manuscript genre and set mode calibration.
   - If the author has a word-count target, note the gap between current and target as the minimum savings goal.

2. **Ingest pass findings.**
   - Read Pass 2 structural map: flag orphan scenes, repeated beats, proportional distribution.
   - Read Pass 1 reader experience log: flag disengagement clusters.
   - If Scene Turn audit was run: import non-turning scenes as candidates.
   - If Pass 3 was run: import pacing drag locations.

3. **Build Channel 1 (Structural Expendability) from Pass 2 data.**
   - For each orphan scene, confirm no downstream dependency. Classify: Cut / Compress / Keep.
   - Identify vestigial subplots (threads that don't connect to controlling idea). Estimate word count.

4. **Discovery pass: sample Channels 2-5 from manuscript reading.**
   - Sample ~15% of total scenes (minimum 10, maximum 30) distributed across the manuscript (weighted toward parts Pass 1 flagged as disengaging). For a 60-scene novel, that's ~9→10 scenes; for a 200-scene novel, ~30 scenes.
   - For each sampled scene: identify dramatic entry/exit, measure pre- and post-drama material, track information deliveries, track emotional positions.
   - Flag instances per channel definitions.
   - **Purpose:** The discovery pass identifies *which compression patterns exist* and *where they cluster*. It is sufficient for Could-Fix and Should-Fix severity calls on individual items.

5. **Enumeration pass: validate before escalation.**
   - If the discovery pass suggests systemic compression problems (flags in ≥3 channels, or estimated expendable material approaching 20%+ of manuscript), extend analysis to all remaining scenes in the densest parts before applying hard gates.
   - Hard gates (§7) require enumerated evidence, not extrapolation from a sample. A sample can identify the pattern; only a full count of the affected sections can justify escalation to Must-Fix.
   - If the discovery pass shows isolated rather than systemic problems, the enumeration pass is not required — proceed directly to step 6.

6. **Apply flags and severity.**
   - Assign flags with default severity.
   - Apply mode calibration (§6) — tighten and loosen per genre.
   - Check hard gates (§7) — apply only to items validated by enumeration (step 5), not extrapolated from sample.

7. **Run Distinguish tests on every flagged item.**
   - Apply the five decision tests in order (see §5 for conflict resolution rules).
   - Classify each item: Cut / Compress / Keep.
   - Assign confidence (High / Medium / Low) per the Confidence Rubric (§4).
   - For "Compress" items, estimate target word count and note compression method.

8. **Build Cut List artifact.**
   - Organize by tier (scene-level cuts, scene-level compression, paragraph-level cuts).
   - Sort within each tier by estimated word savings (largest first).
   - Calculate running total and percentage of manuscript.

9. **Build Compression Map artifact.**
   - Distribute cut candidates across parts/acts/sections.
   - Calculate density per part. Apply mode-aware density interpretation (see §4, Compression Map).

10. **Synthesize audit report.**
    - Pattern analysis: which channels dominate? Is this a structural problem (lots of SE flags), a trust-the-reader problem (lots of IR flags), or a drafting-residue problem (lots of SS flags)?
    - Distinguish classification summary: how many items in each category?
    - Readiness impact: what does the compression picture mean for the manuscript's publishability?

---

## §10. Output Template

```markdown
# Compression Audit Report — [Manuscript Title]

## Scope
- **Genre/Mode:** [genre] — calibration applied per §6
- **Current word count:** [X]
- **Target word count:** [Y, if specified] / [No target specified]
- **Gap:** [Z words to cut, if target specified]

## Channel Ratings

| Channel | Rating | Key Finding |
|---------|--------|------------|
| SE: Structural Expendability | [Integrated / Partial / Detached] | [one-line summary] |
| IR: Informational Redundancy | [Integrated / Partial / Detached] | [one-line summary] |
| ScE: Scene Efficiency | [Integrated / Partial / Detached] | [one-line summary] |
| ER: Emotional Redundancy | [Integrated / Partial / Detached] | [one-line summary] |
| SS: Structural Scaffolding | [Integrated / Partial / Detached] | [one-line summary] |

## Flag Inventory

| Flag | Instances | Severity | Blast Radius | Evidence |
|------|----------|---------|-------------|---------|
| [code] | [n] | [severity] | [local/pattern/systemic] | [scene references] |

## Pattern Analysis
[Which channels dominate? What does the compression profile reveal about the manuscript's drafting history?]

## Distinguish Classification Summary
- **Cut (remove entirely):** [n] items, ~[X] words
- **Compress (tighten in place):** [n] items, ~[X] words estimated savings
- **Keep — Load-Bearing (cleared):** [n] items investigated and retained

## Hard-Gate Triggers
[List any hard gates triggered, with evidence]

## Calibration Notes
[Mode-specific adjustments applied; false-positive risks flagged]

## Cut List
[Full Cut List artifact — see §4]

## Compression Map
[Full Compression Map artifact — see §4]

## Readiness Impact
[What does the compression picture mean for this manuscript? Is the expendable material a revision-stage issue or a structural issue? Does the cut list, if followed, bring the manuscript to target?]

## Top 3 Compression Failures Affecting Readiness
1. [Highest-impact compression failure with evidence and severity]
2. [Second]
3. [Third]
```

---

## §11. Integration and Handoff

### Recommended pairings

- **Scene Turn** — non-turning scenes are strong cut candidates. Run Scene Turn first if not already run; import findings into Channel 1.
- **Stakes System / Decision Pressure** — scenes flagged as low-pressure or low-stakes by these audits may correlate with expendable material. Cross-reference, but do not auto-cut based on pressure/stakes alone.
- **Short Fiction** — if the manuscript is under 20,000 words, use Short Fiction's compression economy instead. The Compression Audit is designed for long-form scale (novels, novellas, memoir, narrative nonfiction) where the problem is *which scenes* rather than *which sentences*.

### Sequence position

- Runs after Pass 2 (needs structural map) and Pass 1 (needs reader engagement data).
- Can run concurrently with Pass 3, Pass 5, and any specialized audits.
- Most useful as a late-stage audit — after core passes have identified the structural picture, before the editorial letter synthesis consolidates findings.
- In the editorial letter, Compression Audit findings feed primarily into §4 (What Needs Work) and §5 (Revision Checklist). The Cut List artifact appears in §9 (Appendices) as a reference document.

### Pass 11 handoff fields

- Top 3 compression failures affecting readiness
- Total estimated expendable material (words and percentage)
- Whether the cut list, if followed, brings the manuscript to target word count

---

## §12. What This Audit Is Not

1. **Not a line-editing pass.** It identifies what to cut, not how to rewrite what remains. Sentence-level tightening is prose-level work, outside scope.
2. **Not a replacement for Pass 3 (Rhythm).** Pass 3 diagnoses pacing problems — slow spots, rhythmic monotony, modulation failure. Some pacing problems are solved by cutting; others are solved by restructuring, rewriting, or reordering. This audit only addresses the "solve by cutting" cases.
3. **Not a replacement for Scene Turn.** Scene Turn diagnoses whether scenes *function*. A non-turning scene might still be worth keeping (if it's genre-functional — e.g., a horror dwell scene, a romance processing scene). This audit asks whether the material is expendable, not whether it turns.
4. **Not a judgment on prose quality.** Beautifully written material can be expendable. Rough material can be load-bearing. Word quality is irrelevant to the compression question.
5. **Not a word-count reduction service.** The audit identifies what *can* be cut, not what *must* be cut. The author decides which cuts to make. If the total estimated savings exceed the target, the author can prioritize.

---

## §13. Firewall Compliance

The audit is diagnostic.

**Allowed:**
1. Identify expendable material with evidence and severity.
2. Estimate word savings per item and total.
3. Specify compression scope (cut entirely vs. compress in place) and method (where to enter, where to exit).
4. Organize cuts by priority and confidence.

**Forbidden:**
1. Rewrite compressed scenes.
2. Generate replacement transitions after cuts.
3. Draft new versions of tightened passages.
4. Make the cuts — the audit recommends; the author executes (or the author requests handoff to execution mode per `references/handoff-protocol.md`).
