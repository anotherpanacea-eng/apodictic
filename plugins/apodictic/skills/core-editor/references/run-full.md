# Full DE Passes & Supplementary Audits

*Reference file for the APODICTIC Development Editor. Loaded only when Full DE tier is triggered.*

**Full DE Trigger Conditions:**
- Core DE identifies >5 root causes
- Reader experience pass logs >10 major issues
- Author reports persistent unidentifiable problems
- Structural complexity (multiple timelines, unreliable narrators, non-linear)
- Author revision loops ("I've rewritten this section multiple times and it still doesn't work")

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

**Output:** `[Project]_Pass3_Rhythm_Modulation_[runlabel].md` — Intensity map (visual scene-by-scene trajectory using ASCII or table format), peak-valley pattern analysis, relief ratio assessment, sentence-level rhythm sampling at 3+ distributed points, pacing diagnosis with specific scenes flagged. Genre modules may add genre-specific checks (e.g., dread fatigue threshold for horror, clock-pressure rhythm for thriller).

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

**Output:** `[Project]_Pass7_POV_Voice_[runlabel].md` — POV distribution table (character, word count, % of total, sections), narrative distance tracking, tense consistency log, perspective slip inventory with specific line references, voice distinctiveness assessment per POV character.

### Pass 9: Thematic Coherence

Track motifs, thematic development, controlling idea alignment.

**Reference project story guides for thematic intent.**

Detect: theme drift, theme-as-thesis, accidental motifs, unearned resolution, thematic contradiction.

**Output:** `[Project]_Pass9_Thematic_Coherence_[runlabel].md` — Thematic inventory (primary, secondary, tertiary themes with statements of what each means and how dramatized), thematic architecture map showing hierarchy and relationships, controlling idea alignment check, genre-specific thematic assessment where applicable (e.g., horror metaphor assessment, romance thematic throughline). Flag theme-as-explanation if any character delivers the thesis statement.

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

### Stakes System Audit

**Track per scene/act:**
- Risk type: external / relational / identity / bodily autonomy / moral self-concept
- Immediacy: immediate vs. abstract
- Trajectory: escalating / cycling / static

**Detect:** Stakes plateau, regression, abstraction without manifestation.

### Decision Pressure Audit

**For each major decision:**
- Alternatives plausibly considered
- Why each fails (pressure, fear, limited info, cost)
- Cognitive distortion or value tradeoff in play
- Whether reader has access to reasoning

**Detect:** Unmotivated decisions, invisible alternatives, convenient stupidity, missing interiority.

---

## Full DE Deliverables

**Reminder:** All outputs must follow the Author-Facing Language requirement (see `references/output-policy.md`). Translate all framework shorthand on first use.

### Editorial Letter (Full DE)

The Core DE editorial letter format (§Core DE Synthesis in `references/run-core.md`) is the base. The Full DE letter uses the same structure, tone, and principles. Differences at Full DE scale:

1. **Length:** 8-20 pages. The additional passes generate more findings.
2. **"What Needs Work" expands.** Character-level findings (Pass 5), reveal economy findings (Pass 8), and thematic coherence findings (Pass 9) integrate as additional headed subsections — same format (bolded thesis-statement heading, prose argument, embedded line references). They do not appear as numbered passes or as a pass-by-pass walkthrough. The organizing principle is *what the book needs*, not *which pass found it*.
3. **"What the Book Does Best" may draw on more evidence** from character, reveal, and thematic passes. The cap still applies.
4. **Revision Checklist may extend to 15 items** (vs. Core DE's 10). If more than 15 exist, the prose sections carry the rest.
5. **Contract confirmation** can appear as a brief paragraph in "The Short Version" or as a short section between "The Short Version" and "What the Book Does Best."

**Pass 11 integration:** Hard Truths fold into "The Strongest Case Against." Revision Economics fold into the Revision Checklist. Three-Lens Verdict and Market Reality Check may appear as a brief section between "Revision Checklist" and "The Strongest Case Against," or in an appendix, depending on manuscript context.

### Diagnostic Dashboard

**Purpose:** A single reference artifact that gives the author a visual, at-a-glance picture of the manuscript's structural health. The editorial letter argues in prose; the dashboard *shows* the data the arguments rest on. Authors who want to see the evidence behind a diagnosis look here.

**Output:** `[Project]_Diagnostic_Dashboard_[runlabel].md` — saved to `Outputs/[Project]/` alongside pass reports and synthesis.

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

#### Dashboard Assembly Rules

1. **Order:** Components appear in the order listed above (pacing → emotional → structural → agency → scene function → promise/payoff → reveal → stakes). This follows the logic of the Full DE pass sequence.

2. **Length target:** 3-6 pages total. Each component should fit in roughly half a page. The dashboard is a reference artifact, not a second editorial letter — keep it tight.

3. **Cross-referencing:** Where a dashboard component reveals a finding that appears in the editorial letter, add a brief pointer: "(See editorial letter: [section heading])." Don't duplicate the argument.

4. **Flags only for real findings.** If a component reveals no issues, include the visualization with a one-line note: "No flags. [Brief positive observation]." Don't manufacture problems to fill space.

5. **Genre module additions.** Genre modules may specify additional columns, rows, or components (e.g., Horror adds a "dread trajectory" row to the Pacing Heat Map; Mystery adds a "clue economy" component). These insert into the relevant component, not as separate sections.

6. **Confidence markers.** Dashboard findings don't carry individual confidence tags (the visualizations speak for themselves), but the top of the file should note: "This dashboard reflects findings from Passes 1-10. Confidence levels for individual diagnoses appear in the editorial letter."

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
