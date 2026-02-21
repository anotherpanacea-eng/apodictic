# Specialized Audit: Narrative Nonfiction Craft
## Version 1.0
*Last Updated: February 2026*

---

## Purpose

Diagnose craft-level execution in narrative nonfiction — reported features, profiles, narrative journalism, systems journalism, explanatory features, and memoir-adjacent reported work. This audit tests whether the nonfiction draft manages its reader contract, controls its information flow, pressurizes its scenes, and earns its interpretive claims.

**Core claim:** Nonfiction can have a viable spine (Franklin passes) and still fail as a reading experience. The failures are specific: the reader doesn't know what question they're tracking, context arrives before curiosity exists, scenes describe rather than pressurize, and meaning is asserted rather than earned. These are craft failures, not structural ones.

**What this audit is:** A nonfiction craft layer. It tests reader contract, question management, information timing, scene pressure, interpretive framing, and reporting discipline.

**What this audit is not:** A substitute for the Franklin Pathway (which diagnoses spine viability), Plot Architecture (which diagnoses structural design), or Scene Turn Diagnostics (which diagnoses fiction scene mechanics). Franklin asks "is this a story?" This audit asks "is the nonfiction executing well?"

**Named for:** Jack Hart's *Storycraft*, adapted as a nonfiction craft diagnostic. Additional mechanisms drawn from the reporting and narrative journalism tradition.

**When to activate:**
- Input is nonfiction (any form) and the Franklin Pathway has classified it
- Story-shaped nonfiction (Franklin Classification 1) that needs craft diagnosis, not spine repair
- Storyable material (Classification 2) after Franklin Steps 1–4, to improve delivery against the candidate spine
- Argument with Embedded Narrative (Classification 3) for reader contract and argument/narrative integration
- Not Storyable (Classification 4) for form recommendation and contract diagnosis
- Author reports "the piece is well-structured but doesn't hold readers" or "I can't figure out what kind of piece this is"

---

## Firewall Compliance

This audit operates within the Editor's firewall by producing diagnostic classifications and structural requirements, not content.

### Allowed

- Classifying nonfiction form and diagnosing form-engine mismatches
- Extracting the central question and promise from existing text
- Tracking question states (raised, held, answered, abandoned) across sections
- Classifying information slabs by type and timing
- Diagnosing scene pressure through status baseline and shift analysis
- Identifying the meaning line (or its absence) from existing interpretive moves
- Flagging attribution and certainty risks in reported reconstruction
- Testing whether lead and ending fulfill the reader contract

### Not Allowed

- Inventing central questions, meaning lines, or interpretive frames
- Writing leads, endings, or transitions
- Suggesting specific reporting actions or interview questions
- Creating scenes, dialogue, or reconstructed events

---

## Code Namespace Note

This audit uses F-codes (form), QS-codes (question state), I-codes (information timing), ST-codes (status pressure), SW-codes (meaning line), AS-codes (anchor/system), A-codes (attribution), LC-codes (lead contract), and E-codes (ending payoff).

**No collisions with existing code systems:**
- Scene Turn Diagnostics: G-codes, C-codes, O-codes, Sq-codes, H-codes, U-codes, P-codes
- Emotional Craft Diagnostics: S-codes, B-codes
- Memoir Gornick Layer: GS-codes, NI-codes, SC-codes, TD-codes, BR-codes, SEL-codes, EP-codes
- Character Architecture Part 9: M-codes, W-codes, N-codes, DN-codes, OCA-codes, PW-codes, SR-codes, MC-codes, TP-codes
- Dialectical Clarity: AT-codes, CL-codes, SM-codes, BP-codes, OB-codes, NE-codes

All code systems may appear in the same editorial letter.

---

## The Diagnostic Procedure

### Step 1: Form Engine Classification (F-codes)

Classify the draft by its dominant propulsion — what keeps the reader reading.

**Run on:** lead + one representative midsection + ending.

```
Draft: [Title/description]
  Form engine: [F-code]
  Confidence: [HIGH / MEDIUM / LOW]
  Contract note: [does the lead promise this form, or a different one?]
```

**Form engine codes:**

| Code | Form | Propulsion | Common In |
|------|------|-----------|-----------|
| **F1** | Event narrative | "What happened?" drives forward | Reported features, true crime, disaster journalism |
| **F2** | Inquiry narrative | "What's true / what's going on?" drives forward | Investigative journalism, explanatory features |
| **F3** | Profile under pressure | Character revealed through constrained decisions | Profiles, personality journalism |
| **F4** | Systems + anchor case | Human case explains/illustrates a system | Policy journalism, institutional reporting |
| **F5** | Argument with embedded narrative | Claim-evidence logic dominates; vignettes illustrate | Op-eds, policy briefs, advocacy journalism |
| **F6** | Mosaic / braided | Multiple threads; meaning emerges by juxtaposition | Multi-source features, oral histories, braided essays |

**Form failure codes:**

| Code | Name | Description |
|------|------|-------------|
| **F0** | Mixed engine without control | Switches engines midstream without signaling; reader feels lost |
| **F7** | Engine mismatch | Opening promises one form, body delivers another |

**Calibration:** F5 (Argument with embedded narrative) overlaps with Franklin Classification 3. When Franklin returns Classification 3, confirm with F-code. If the form is truly F5, argument structure is primary — invoke the Dialectical Clarity Audit (AT/CL/SM/BP/OB/NE codes) on the argument structure, and run this audit's remaining steps only on the embedded narrative segments.

**Why form classification matters:** All later steps calibrate by form. Flagging "no scene-level goal" in an F5 argument piece is a false positive. Flagging "no central question" in an F1 event narrative is a real problem.

### Step 2: Central Question & Promise Map

Extract the central question (CQ) the reader is tracking and the promise type — what kind of answer the piece offers.

**Run on:** lead + section transitions + ending.

```
Central Question: [what the reader wants answered]
  Specificity: CONCRETE / VAGUE / ABSENT
  Established by: [paragraph/scene reference]

Promise Type: [REVEAL / EXPLAIN / VERDICT / PORTRAIT / LESSON]
  Reinforced at section turns: [Y/N — does the text remind the reader what they're reading for?]
```

**Promise types:**

| Type | What the Reader Expects |
|------|------------------------|
| **Reveal** | "I'll show you what really happened" |
| **Explain** | "I'll help you understand how this works" |
| **Verdict** | "I'll tell you whether this is good/bad/true/false" |
| **Portrait** | "I'll show you who this person really is" |
| **Lesson** | "I'll show you what this means / what it teaches" |

**CQ failure codes:**

| Code | Name | Description |
|------|------|-------------|
| **Q0** | No central question | Lead is atmospheric or informational but non-committal; reader has no question to track |
| **Q1** | Question drift | CQ changes midstream without transition; reader loses the thread |
| **Q2** | Answer dump too early | CQ answered before curiosity builds; often paired with Context Smother CLI > 0.70 |
| **Q3** | No payoff | Ending doesn't answer the CQ, or answers a different question |

**Cross-reference:** Franklin's Question Management Diagnostic provides the logic gates (Opening Question, Question Continuity, Question Escalation). This step provides the formal CQ extraction and failure codes. The Question Management gates test whether questions *function*; CQ codes test whether the *central* question functions.

### Step 3: Question State Tracking (QS-codes)

Track how reader questions are raised, held, and resolved across the draft. This is the operational mechanism behind the Franklin Question Management gates.

**Run on:** section headings or paragraph transitions — doesn't require full close reading.

**For 5–10 question states across the draft, track:**

```
Q[n]: [question text]
  Raised: [section/paragraph reference]
  State sequence: RAISED → HELD → [COMPLICATED →] ANSWERED / ABANDONED / REPLACED
  Currently: [ACTIVE / RESOLVED / ABANDONED]
```

**Question state definitions:**

| State | Meaning |
|-------|---------|
| **Raised** | Question introduced (explicit or implied) |
| **Held** | Tension maintained; partial information provided but question unanswered |
| **Complicated** | New constraint or information deepens the question |
| **Answered** | Payoff — the question is resolved |
| **Replaced** | A new question supersedes this one as the reader's primary curiosity |
| **Abandoned** | Question dropped without resolution or replacement |

**QS failure codes:**

| Code | Name | Description |
|------|------|-------------|
| **QS0** | No questions raised | Informational opening; no curiosity engine engaged |
| **QS1** | Unheld questions | Questions raised then abandoned; reader feels threads are dropped |
| **QS2** | Premature answering | Information arrives before the reader wants it; exposition precedes curiosity |
| **QS3** | Stacking without payoff | Questions multiply without resolution; "mystery pileup" |
| **QS4** | Payoff without setup | Reveals feel arbitrary because the question they answer wasn't established |

**Output:** Compact question state timeline:
```
Q1: "Will she win the case?" — RAISED (lead) → HELD (§2–4) → COMPLICATED (§5: new evidence) → ANSWERED (§8)
Q2: "Why did the agency hide the records?" — RAISED (§3) → ABANDONED (never resolved)
Q3: "What happens to the kids?" — RAISED (§6) → HELD → REPLACED by Q4
```

### Step 4: Information Timing & Slab Diagnostics (I-codes)

Classify information slabs by type and diagnose their placement. Extends the Franklin Context Smother Diagnostic with formal codes.

**Run on:** identify 3–5 information slabs (runs of explanatory prose). For each:

```
Slab [X]: [location]
  Type: [I-code]
  Question served: [which reader question does this answer, or "none"]
  Placement: [WELL-TIMED / PREMATURE / DISRUPTIVE / ACCEPTABLE]
```

**Information slab type codes:**

| Code | Type | Description |
|------|------|-------------|
| **I1** | Hook-fueling | Answers a question the narrative just created; reader wants this |
| **I2** | Necessary orientation | Prevents confusion (who/where/when); reader would be lost without it |
| **I3** | Argumentation | Claims and reasons; often belongs in an F5 argument track, not the narrative |
| **I4** | Credentialing | Establishes writer's authority or topic importance; defensive, not reader-serving |
| **I5** | Background | Interesting context but not doing structural work; enrichment |

**Placement failure codes:**

| Code | Name | Description |
|------|------|-------------|
| **I0** | Front-loaded slab | Context before any curiosity or stakes; pre-complication exposition |
| **I6** | Scene interruption | Breaks immersion at peak narrative pressure |
| **I7** | Redundancy | Repeats information already conveyed |
| **I8** | Wrong-question mismatch | Information answers a question the reader isn't asking; misaligned context |

**Integration with Franklin Context Smother:**

Franklin's Context Smother Diagnostic measures the Context Load Index (CLI) and classifies slabs by function. This step adds two dimensions:

1. **"Question served" field** — converts Context Smother from "too much context" to "context mistimed." A slab that answers the reader's active question is well-timed regardless of length; a slab that precedes curiosity is premature regardless of quality.

2. **I-codes for slab typing** — more granular than Franklin's four-category classification (necessary/enrichment/credentialing/argumentation). I1 and I2 are structural; I3–I5 are candidates for moving, condensing, or cutting.

**The Demand Principle** (from Franklin's Information Timing Principle): Information delivered before the reader wants it is exposition. Information delivered after the reader wants it is revelation. The I-codes diagnose where the gap between delivery and demand has collapsed.

### Step 5: Scene Status Pressure (ST-codes)

For reported scenes and dramatized moments, diagnose whether status pressure is legible and whether status shifts drive the narrative forward. Extends Franklin's Scene Selection SCR (Status-Complication-Resolution) with the specific status dimension.

**Run on:** 1–3 dramatized scenes, especially institutional interactions, interviews, meetings, courtroom moments, or profile-revealing encounters.

```
Scene [X]: [description]
  Status baseline: [who has authority / credibility / control / face / belonging at scene opening]
  Threat: [what puts status at risk within the scene]
  Status shift: [who gains/loses face, leverage, access, trust at scene end]
  CQ relevance: [does the status shift advance the central question? Y/N]
```

**Status Pressure failure codes:**

| Code | Name | Description |
|------|------|-------------|
| **ST0** | No status baseline | Reader can't feel the stakes of the interaction; hierarchy invisible |
| **ST1** | No threat | Scene is descriptive but unpressurized; nothing is at risk |
| **ST2** | No shift | Scene ends as it began; status unchanged |
| **ST3** | Status asserted not dramatized | Told "he felt humiliated" without observable social consequence |
| **ST4** | Status shift without relevance | Shift doesn't tie to the central question; scenic but purposeless |

**Relationship to existing SCR:** Franklin's Scene Selection Diagnostic uses SCR (Status-Complication-Resolution) as the nonfiction parallel to Bickham's Goal-Conflict-Outcome. The ST-codes add precision about *what kind of status* is at play and whether the shift matters to the piece's central question. SCR tests whether the scene turns; ST-codes test whether the turn matters.

**Genre calibration:** High diagnostic value in profiles (where character is revealed by status under pressure), institutional reporting (where power dynamics are the story), courtroom/legal narratives, and family/relational memoir. Lower value in F2 inquiry narratives where the propulsion is informational rather than interpersonal.

### Step 6: Meaning Line Diagnostic (SW-codes)

Diagnose whether the draft earns an interpretive claim — the "so what?" that ties scenes and facts to significance.

**Run on:** look for interpretive moves (framing sentences, juxtaposition, selected detail that implies a stance) in lead, midsection, and ending.

```
Meaning Line: [the implied interpretive claim — what this means, not just what happened]
  Established by: [section reference]
  Consistent with CQ: [Y/N]
  Deepens over draft: [Y/N — does understanding deepen, or is meaning repeated as slogan?]
```

**Meaning Line failure codes:**

| Code | Name | Description |
|------|------|-------------|
| **SW0** | No meaning line | Sequence of facts with no interpretive progression; "and then" without "because" or "therefore" |
| **SW1** | Meaning asserted, not earned | Thesis dropped without narrative support; the text tells the reader what to think rather than showing why |
| **SW2** | Meaning line appears only at end | Too late; midsection feels purposeless because the reader doesn't know why events matter |
| **SW3** | Competing meanings | Frame whiplash — the draft offers incompatible interpretive claims without acknowledging the tension |

**Cross-reference with Franklin Narrative Stance:** The stance diagnostic identifies the narrator's *relationship* to events (witness/investigator/advocate/participant/invisible). The meaning line diagnostic identifies the narrator's *interpretive claim* about events. Stance is how you're telling; meaning line is what you're arguing the events mean. Both must be present for nonfiction to land.

**Genre calibration by form:**

| Form | Meaning Line Expectation |
|------|------------------------|
| F1 Event narrative | Meaning line emerges from event sequence; should feel earned, not imposed |
| F2 Inquiry | Meaning line is the answer to the inquiry; explicit is acceptable |
| F3 Profile | Meaning line is the character assessment; often implied through selected detail |
| F4 Systems + case | Meaning line is the systemic diagnosis; case provides the evidence |
| F5 Argument | Meaning line IS the argument; SW-codes less relevant (use argument quality tests) |
| F6 Mosaic | Meaning line emerges by juxtaposition; may be implicit until ending |

### Step 7: Anchor/System Balance (AS-codes)

**Conditional — run only for F4 (Systems + Anchor Case) form.**

When a piece uses a human case to explain a system, diagnose the integration between case material and system material.

**Run on:** track case segments (human throughline, scenes, personal stakes) and system segments (policy, data, history, institutions) across the full draft.

```
Case/System Ratio:
  Case segments: [word count or section count]
  System segments: [word count or section count]
  Integration quality: [do system sections answer questions created by the case?]
  Case arc: [does the anchor case evolve, or remain a static illustration?]
```

**AS failure codes:**

| Code | Name | Description |
|------|------|-------------|
| **AS0** | Case tokenism | Case appears only as anecdote; no arc, no development, no return |
| **AS1** | System swamp | Case disappears; narrative drops; piece becomes policy paper |
| **AS2** | Case swamp | System claim under-supported; piece feels narrow, anecdotal rather than diagnostic |
| **AS3** | Poor integration | System material doesn't resolve questions raised by the case; parallel tracks that don't meet |
| **AS4** | Multiple cases without control | Mosaic of cases without an organizing question or hierarchy; reader loses throughline |

**The integration test:** For each system segment, ask: "Does this answer a question the case just raised?" If yes, the integration is functional. If the system material precedes the case-raised question, it's I0 (front-loaded) or QS2 (premature answering). If the system material answers a question the case never raised, it's AS3 (poor integration).

### Step 8: Attribution & Certainty Discipline (A-codes)

Diagnose whether the draft's narrative moves are consistent with what can be responsibly known or reconstructed. This is a reporting constraint audit, not a moral judgment.

**Run on:** scan for reconstructed interiority, precise dialogue, omniscient sequencing, and causal claims. Focus on scenes where the writer was not present.

```
Scene [X]: Attribution Audit
  Risk flags: [A-codes]
  Evidence basis: [observation / multi-source interview / single-source / documents / memory]
  Recommendation: [attribution phrasing / hedging / structural relocation / sourcing note]
```

**Attribution risk codes:**

| Code | Name | Description |
|------|------|-------------|
| **A0** | Systemic certainty mismatch | Tone of certainty exceeds evidence across the draft; not scene-specific but pervasive |
| **A1** | Unattributed interiority | "She thought..." without sourcing; reconstructed mental state presented as fact |
| **A2** | Unattributed dialogue | Precise quoted dialogue without explanation of reporting basis |
| **A3** | Overconfident causality | Claims of cause beyond what evidence supports; "because" without warrant |
| **A4** | Timeline omniscience | Events sequenced with precision beyond what reporting allows |
| **A5** | Composite/identity risk | Implicit compression of sources or events without acknowledgment |

**Relationship to Franklin Reconstruction Standards:** Franklin's Scene Selection Diagnostic includes a Reconstruction Confidence table (firsthand observation → single-source interview → memory reconstruction). The A-codes extend this from scene-level confidence to manuscript-wide certainty discipline. Reconstruction Standards ask "can this scene be built?" A-codes ask "is the draft claiming more certainty than the reporting supports?"

**Firewall compliance:** This step flags risks and recommends mitigation types (attribution phrasing, hedging, sourcing note, structural relocation). It does not evaluate journalistic ethics, adjudicate truth claims, or prescribe reporting methods.

### Step 9: Lead Contract (LC-codes)

Diagnose whether the lead establishes a contract the body fulfills. This is often where popular-audience nonfiction fails: the lead promises one kind of reading experience, the body delivers another.

**Run on:** lead (first 3–5 paragraphs) + body form.

```
Lead Type: [L-code]
Body Form: [F-code from Step 1]
Contract: [MATCH / MISMATCH]
```

**Lead type codes:**

| Code | Lead Type | What It Promises |
|------|-----------|-----------------|
| **L1** | Scene lead | "This is a story — you'll experience it moment by moment" |
| **L2** | Anecdotal vignette | "Here's a compelling moment — the piece will explain why it matters" |
| **L3** | Question lead | "Here's a mystery — the piece will answer it" |
| **L4** | Statement/thesis lead | "Here's a claim — the piece will support it" |
| **L5** | Character portrait lead | "Here's a person — the piece will reveal who they are" |
| **L6** | Data/contrast lead | "Here's a surprising fact — the piece will explain it" |

**Lead contract failure codes:**

| Code | Name | Description |
|------|------|-------------|
| **LC0** | Contract breach | Lead promises narrative (L1/L2), body delivers exposition; reader feels bait-and-switch |
| **LC1** | Wrong lead for form | Lead type doesn't match the body's form engine; e.g., F5 argument uses L1 scene lead that misleads |
| **LC2** | Stakes mismatch | Lead implies high stakes; body can't sustain the implied urgency |

### Step 10: Ending Payoff (E-codes)

Diagnose whether the ending delivers the promised answer and leaves the reader with appropriate residue (implication, cost, or next question).

**Run on:** final section + cross-reference with CQ from Step 2.

```
Ending Assessment:
  CQ answered: [Y/N/PARTIALLY]
  Meaning line cashed out: [Y/N]
  Opening recontextualized: [Y/N — does the ending change how the reader understands the opening?]
  Residue: [what the reader is left with — implication / cost / next question / closure]
```

**Ending failure codes:**

| Code | Name | Description |
|------|------|-------------|
| **E0** | No answer | Piece drifts out; CQ unresolved without intentional open ending |
| **E1** | Summary ending | Repeats facts from the body; no meaning culmination; feels like a book report |
| **E2** | New thesis at end | Introduces an interpretive claim not earned by the preceding material |
| **E3** | Sentimental wrap | Pressure released without insight; emotional resolution substitutes for intellectual payoff |

---

## Common Patterns

Named diagnostic patterns this audit is designed to catch.

### Pattern 1: The Bait-and-Switch Feature

**Signature:** LC0 (contract breach) + F7 (engine mismatch) + Q1 (question drift).

Scene lead promises narrative; body delivers policy exposition. Common in advocacy journalism and reported features by writers who know their subject better than their craft. The reader signed up for a story and got a briefing.

### Pattern 2: The Context Wall

**Signature:** I0 (front-loaded slab) + QS0 (no questions raised) + QS2 (premature answering).

The first 30% of the piece is background: history, definitions, statistics, policy context. No question has been raised. No character has appeared. The writer is building the foundation before laying the first brick of story. The reader has stopped reading.

**Cross-reference:** Franklin Context Smother CLI > 0.70. This is the same problem diagnosed from two angles — Franklin measures proportion, this audit diagnoses the question-management failure underneath.

### Pattern 3: The Token Case

**Signature:** AS0 (case tokenism) + SW1 (meaning asserted not earned) + ST2 (no status shift in case scenes).

A human case opens the piece, appears in an anecdote, then vanishes. The system material does the real work. The case never develops, never faces pressure, never changes. It's illustration, not throughline. The meaning line claims the system matters to real people, but the real person in the piece never demonstrates it through action.

### Pattern 4: The Purposeless Middle

**Signature:** QS1 (unheld questions) + SW0 (no meaning line) + multiple ST2 (no status shifts).

The opening establishes a question. The ending delivers a payoff. The middle is a sequence of facts, scenes, and interviews that don't build toward either. Each section is interesting in isolation; together they don't accumulate. The question state timeline shows gaps where no question is active.

**Cross-reference:** Franklin Failure Mode D (Plateau in the Middle). Same phenomenon, different resolution: Franklin diagnoses escalation failure in the function chain; this audit diagnoses question management and meaning line failure.

### Pattern 5: The Certainty Mirage

**Signature:** A0 (systemic certainty mismatch) + A1 (unattributed interiority) + A2 (unattributed dialogue).

The prose reads like a novel: characters think, speak precise dialogue, and move through precisely sequenced events. But the sourcing doesn't support this level of certainty. The draft reads beautifully and is built on sand. Common in narrative journalism that prioritizes readability over reporting transparency.

---

## Genre Calibration

### By Form Engine

**F1 Event Narrative:** CQ and QS tests are primary — the story must raise and manage questions about what happened. ST-codes are high-value (events involve status). A-codes matter if reconstruction is involved.

**F2 Inquiry Narrative:** CQ and QS tests are primary — the inquiry must have a question and manage information toward an answer. SW-codes are high-value (the inquiry must earn its conclusion). ST-codes are lower-value unless the inquiry involves confrontation.

**F3 Profile Under Pressure:** ST-codes are primary — the profile must show character through status under pressure. SW-codes matter (what does this person mean?). A-codes matter for reconstructed scenes. QS-codes track the portrait question ("who is this person?").

**F4 Systems + Anchor Case:** AS-codes are primary — integration between case and system must work. I-codes are high-value (system material must be timed to case-raised questions). SW-codes matter (what does this system mean for people?).

**F5 Argument with Embedded Narrative:** LC-codes are primary (lead must match argument form). SW-codes recede (the argument IS the meaning line). QS-codes apply per-segment. Run the Dialectical Clarity Audit (AT/CL/SM/BP/OB/NE codes) for the overall argument structure; run this audit on embedded narrative segments only.

**F6 Mosaic / Braided:** QS-codes apply per-thread, not globally. SW-codes are high-value (meaning must emerge from juxtaposition). AS-codes may apply if threads have different weights. Lead contract matters: the lead must signal braided form.

### Calibration for Length

- **Short form (op-ed length, < 2,000 words):** Allow tighter answer-dumps (QS2 less flaggable). Enforce LC (lead contract) and E (ending payoff) strictly. SW meaning line must be present early.
- **Mid-length (2,000–8,000 words):** Full audit applies. QS timeline is most diagnostic in this range.
- **Long form (> 8,000 words):** Expand scope to 10+ question states. AS-codes and I-codes become critical for managing the reader through complex material.

---

## Scope Selection

### Default Scope

| Component | What to Sample | How Many |
|-----------|---------------|----------|
| Lead | Full lead (first 3–5 paragraphs) | 1 |
| Section transitions | Where the piece shifts between threads, topics, or modes | 3–5 |
| Dramatized scenes | Scenes with characters, action, real-time pacing | 1–3 |
| Information slabs | Runs of explanatory prose | 3–5 |
| Ending | Final section | 1 |

Steps 1 (Form), 2 (CQ), 9 (Lead Contract), and 10 (Ending Payoff) run on the whole piece. Steps 3–8 sample strategically within the scope above.

### When to Expand

- If QS timeline shows pervasive QS1 (unheld questions) → expand to full question state tracking
- If I-codes show systematic I0 (front-loading) → cross-reference all slabs with CLI from Franklin Context Smother
- If A-codes fire on sampled scenes → expand to all dramatized scenes

---

## Integration with Core Framework

### Module Position

This is a specialized audit invoked by the Franklin Pathway or loaded directly for nonfiction inputs. It stacks with genre modules and other specialized audits.

### Relationship to Franklin Pathway

**Franklin is the gate; this audit is the craft layer.**

Franklin diagnoses whether the material has a viable spine (Steps 0–4) and provides nonfiction-specific structural tools (Context Smother, Scene Selection, Narrative Stance, Question Management). This audit diagnoses whether the nonfiction executes its craft well — reader contract, question management, information timing, scene pressure, interpretive framing, reporting discipline.

**Invocation logic:**

| Franklin Classification | This Audit's Role |
|------------------------|-------------------|
| Classification 1 (Story-Shaped) | Optional — run on nonfiction to improve delivery |
| Classification 2 (Storyable) | Run after Franklin Steps 1–4 to diagnose craft against candidate spine |
| Classification 3 (Argument + Narrative) | Run on the whole piece for reader contract; Franklin runs on embedded narrative segments |
| Classification 4 (Not Storyable) | Run Steps 1 (Form), 2 (CQ), 9 (Lead Contract) for form recommendation |

### Pass Modifications

**Pass 1 (Reader Experience):** When flagging "I don't know what I'm reading for" or "this feels like an essay," add as Hart Audit trigger. CQ and LC codes diagnose the mechanism.

**Pass 3 (Pacing/Rhythm):** When flagging nonfiction pacing problems, distinguish between proportion problems (Franklin Context Smother) and question management problems (QS-codes from this audit).

### Orchestration with Other Audits

**With Scene Turn Diagnostics:** Scene Turn uses goal-conflict-outcome for fiction scenes. This audit uses status-complication-resolution + status pressure for nonfiction scenes. For nonfiction with strong narrative scenes, both may apply. Run SCR/ST from this audit first (nonfiction framing), then Scene Turn's G-C-O if scenes have clear character goals.

**With Emotional Craft Diagnostics:** A nonfiction scene can have proper status pressure (ST passes) but flat emotional transmission (S-codes fire). The two audits diagnose different dimensions: this audit tests whether the scene is structurally pressurized; Emotional Craft tests whether emotion transmits through the prose.

**With Memoir/Creative Nonfiction Audit (including Gornick Layer):** Memoir audit handles truth/memory ethics and scene reconstruction. Its Gornick Layer (GS/NI/SC/TD/BR/SEL/EP codes) handles the meaning engine — narrating intelligence, stance, situation-story braid. This audit handles craft execution — question management, information timing, meaning line. For memoir, all three layers may be active. SW-codes (meaning line) from this audit correspond to GS-codes (situation/story) from the Gornick Layer: SW diagnoses whether a meaning line exists in nonfiction generally; GS diagnoses whether a story-beneath-the-situation exists in memoir specifically. A-codes from this audit complement the Memoir audit's reconstruction standards.

### Output Delivered

The full audit produces:

1. **Form Engine Classification** (Step 1: F-code + contract note)
2. **Central Question & Promise Map** (Step 2: CQ extraction + promise type + Q-codes)
3. **Question State Timeline** (Step 3: 5–10 question states tracked across draft + QS-codes)
4. **Information Timing Diagnostics** (Step 4: slab typing with I-codes + placement assessment)
5. **Scene Status Pressure** (Step 5: 1–3 scene audits with ST-codes)
6. **Meaning Line Diagnosis** (Step 6: interpretive claim identification + SW-codes)
7. **Anchor/System Balance** (Step 7: AS-codes — conditional, F4 only)
8. **Attribution & Certainty Risk** (Step 8: A-codes for reconstruction discipline)
9. **Lead Contract** (Step 9: LC-codes — lead type vs. body form)
10. **Ending Payoff** (Step 10: E-codes — CQ resolution + meaning line culmination)

### Coaching in the Editorial Letter

The diagnostic procedure identifies craft failures with specific codes. When the editorial letter is written, it may include coaching guidance — explaining why question management matters, how information timing affects the reader's experience, what status pressure looks like in nonfiction scenes, or how a meaning line differs from a thesis statement. This coaching belongs in the deliverable, not in the diagnostic specification.

---

*This audit diagnoses craft execution in narrative nonfiction — whether the draft manages its reader contract, controls its question flow, times its information delivery, pressurizes its scenes, and earns its interpretive claims. It extends the Franklin Pathway's structural diagnosis with a craft layer specific to nonfiction forms. The system diagnoses nonfiction craft mechanics; the writer provides the reporting, the scenes, and the meaning.*
