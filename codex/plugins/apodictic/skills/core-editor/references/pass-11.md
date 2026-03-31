# Pass 11: Critical Quality & Market Viability
## Version 2.3 (Merged: Opus46 + Codex53 + Calibration Patch + 11F Stress Test)
### APODICTIC Development Editor (APDE)

*Calibration additions: Adversarial-Critic Mode, Pre-READY Verification Checklist, Sub-Pass 11F (Adversarial Reader Stress Test)*

---

## Purpose

Pass 11 forces a candid acquisition-style judgment on the manuscript. Where earlier passes diagnose *what's happening* structurally, Pass 11 answers: **Is this good enough? Would it sell? What's actually stopping it?**

This pass exists because developmental editing without honest evaluation is incomplete. Authors need to know not just what to fix, but whether the manuscript is competitive—and if not, why not.

---

## Position in Framework

```
Intake → Core DE Passes (0, 1, 2, 5, 8) → Synthesis → PASS 11 → Deliverables
```

**Requires:** All Core DE passes complete; synthesis draft available; Shelf & Positioning audit complete (if marketability requested)

**Gate Function:** Pass 11 verdict determines deliverable framing

---

## Trigger Logic

**Pass 11 activates when any of the following conditions are met:**

1. Author states publication, submission, or market-readiness as a goal
2. Author requests "honest assessment" or "is this ready?"
3. Query materials or submission preparation is mentioned
4. Author asks for comp validation or market positioning

**Pass 11 does NOT activate for:**

- Pure craft diagnosis without market intent
- Experimental or personal projects where publication isn't the goal
- Early-draft feedback where market readiness is premature
- Author explicitly opts out ("just structural feedback, not market assessment")

**Override:** Author can request Pass 11 on any manuscript regardless of stated goals.

---

## Sub-Pass Architecture

Pass 11 comprises five sub-passes. Sub-passes 11A and 11B always run when Pass 11 is triggered. Sub-passes 11C, 11D, and 11E run based on author needs.

| Sub-Pass | Name | Runs When |
|----------|------|-----------|
| **11A** | Writing Quality Diagnostic | Always (when Pass 11 triggered) |
| **11B** | Critical Verdict Protocol | Always (when Pass 11 triggered) |
| **11C** | Market Reality Check | Marketability requested |
| **11D** | First-50 Conversion Gate | Submission readiness requested |
| **11E** | Revision Economics | Revision planning requested |
| **11F** | ~~Adversarial Reader Stress Test~~ | **Migrated to core synthesis §8 (v1.0.1)** — now runs for every editorial letter |

---

## Sub-Pass 11A: Writing Quality Diagnostic

**Purpose:** Evaluate prose quality at scene and sentence level without generating replacement prose.

### Scene-Level Voltage

**Measure per scene:**
- **Entry charge:** Does scene open with tension, question, or momentum?
- **Exit charge:** Does scene end with changed state or forward pull?
- **Voltage drop:** Where does energy dissipate within scene?
- **Dead zones:** Passages where nothing is at stake

**Flag:** >3 consecutive scenes with low entry/exit charge → `QF-7 Scene Voltage Failure`

### Sentence-Level Mechanics

**Track across manuscript sample (10% minimum, distributed):**

| Metric | Guideline Range | Flag Threshold | Genre Exceptions |
|--------|-----------------|----------------|------------------|
| Sentence length variance | 8-25 word range | <5 word variance | Literary: wider acceptable |
| Active verb ratio | >65% | <55% | Interiority-heavy: lower acceptable |
| "Was/were" density | <10% of sentences | >15% | Past-tense literary: higher acceptable |
| Adverb density | <3% of words | >5% | Voice-driven comedy: higher acceptable |
| Cliché frequency | <2 per 1000 words | >4 per 1000 | Genre romance: context-dependent |
| Abstraction clusters | <4 consecutive abstract sentences | >6 consecutive | Literary/philosophical: context-dependent |

**Genre Calibration Rule:** Before flagging any metric violation, check against active genre modules. If genre module permits the pattern, do not flag. If uncertain, flag as `[MEDIUM CONFIDENCE]` with genre note.

### Voice Distinctiveness

**Blind Swap Test:** Extract 10 random paragraphs from narrative (not dialogue). Could these have been written by any competent writer in this genre, or is there a recognizable voice?

**Markers to assess:**
- Signature syntax patterns
- Characteristic metaphor families
- Consistent sensory biases
- Distinctive interiority style
- Rhythm fingerprint

**Output:** `DISTINCTIVE` / `DEVELOPING` / `GENERIC`

If `GENERIC` → `QF-2 Voice Underdeveloped`

### Prose Tier Output

```
P0 Publication-Ready: No systemic prose blockers
P1 Needs Line-Level Tightening: Strong base, polish needed
P2 Needs Significant Craft Revision: Repeated craft failures affect readability
P3 Needs Reconception at Prose Level: Voice/clarity fundamentally unstable
```

---

## Sub-Pass 11B: Critical Verdict Protocol

**Purpose:** Force explicit, candid evaluation through multiple professional perspectives.

### The Three Lenses (Required)

Each lens asks different questions. Disagreement between lenses surfaces uncertainty.

### Adversarial-Critic Mode (Required)

**Before finalizing any lens assessment, apply adversarial-critic thinking:**

> "What would a hostile but intelligent reader find wrong with this manuscript? What would make an agent pass despite strong voice? What am I missing because I like the prose?"

This is not optional politeness—it's calibration against generosity bias. Strong voice can mask:
- Production-level continuity errors (chapter numbering, timeline math)
- Dangling setup threads (illnesses, pregnancies, fates never resolved)
- Secondary arc bridge gaps (transformations that feel abrupt)
- Consistency variance across long stretches

**The adversarial question:** "If I had to argue this manuscript should be rejected, what would I say?" Answer that question honestly before rendering verdicts.

#### Lens A: Acquiring Editor

*"Would I take this to editorial board?"*

**Evaluates:**
- Commercial viability in current market
- Comp positioning (is this in the same league?)
- Platform/hook clarity (one-sentence pitch)
- Category fit (clear shelf?)
- Risk factors (controversial content, niche appeal, timing)

**Key Questions:**
1. What's the one-sentence pitch? Is it compelling?
2. Who is the target reader, specifically?
3. What would make me reject this at query stage?
4. What would make me reject after reading full?

**Output:** `ACQUIRE` / `REVISE & RESUBMIT` / `PASS`

#### Lens B: Category Super-Reader

*"Would I recommend this to my book club?"*

**Evaluates:**
- Reader satisfaction (delivers on promise?)
- Emotional payoff (felt what I was supposed to feel?)
- Reread/recommend likelihood
- Comparison to favorites in category

**Key Questions:**
1. Did this deliver what the opening promised?
2. Where did I want to stop reading?
3. Would I recommend this? To whom? With caveats?
4. What's missing that I expected?

**Output:** `RECOMMEND` / `MIXED` / `WOULD NOT FINISH`

#### Lens C: Skeptical Critic

*"Is this actually good, or just competent?"*

**Evaluates:**
- Originality (derivative, thin, or overfamiliar?)
- Ambition (reaching for something difficult?)
- Voice distinctiveness (could anyone have written this?)
- Intellectual/emotional depth
- Craft at sentence level

**Key Questions:**
1. What is this manuscript trying to do that's difficult?
2. Where does it succeed at something hard?
3. Where does it settle for competence when it could reach?
4. Will this be remembered in five years?

**Output:** `NOTABLE` / `COMPETENT` / `DERIVATIVE`

### Lens Agreement Matrix

```
| Assessment    | Editor | Super-Reader | Critic | Consensus |
|---------------|--------|--------------|--------|-----------|
| Ready         |   ?    |      ?       |   ?    |     ?     |
| Prose         |   ?    |      ?       |   ?    |     ?     |
| Originality   |   ?    |      ?       |   ?    |     ?     |
| Satisfaction  |   ?    |      ?       |   ?    |     ?     |
```

**Interpretation:**
- 3/3 agreement → `[HIGH CONFIDENCE]` verdict
- 2/3 agreement → `[MEDIUM CONFIDENCE]`, note dissent
- Split → Present disagreement explicitly; author decides

### Path Parity Criteria

The three lenses default to traditional publishing frame. When author's path differs, apply these adjustments:

**Self-Pub Path:**
- Acquiring Editor → "Would I buy this as a reader scrolling Amazon?"
- Super-Reader → "Would I leave a 5-star review and buy the next one?"
- Critic → "Does this stand out in a crowded self-pub category?"

**Hybrid Path:**
- Evaluate against both frames
- Note where trad criteria and self-pub criteria diverge

### Verdict Tiers

**READY**
- Manuscript is competitive for stated path
- Prose is publication-quality (P0 or P1)
- Structure delivers on contract
- Clear path to target reader
- No non-negotiable issues remaining

**CONDITIONALLY VIABLE**
- Core is strong; specific issues must be addressed
- Prose needs work but foundation is solid (P1 or P2)
- Structure works with identified fixes
- Market positioning is achievable
- ≤5 non-negotiable issues, all fixable

**NOT READY**
- Fundamental issues prevent competitiveness
- Prose requires significant development (P2 or P3)
- Structure needs reconception, not revision
- Market positioning unclear or problematic
- Issues exceed reasonable revision scope

### Hard Truths Section (Required)

Every Pass 11 output must include 3-5 direct statements about what isn't working.

**Format:**
```
## Hard Truths

1. [HIGH CONFIDENCE] [Direct statement + consequence]

2. [HIGH CONFIDENCE] [Direct statement + consequence]

3. [MEDIUM CONFIDENCE] [Statement with noted uncertainty]
```

**Rules:**
- `[HIGH CONFIDENCE]` findings cannot be hedged ("might," "perhaps," "consider")
- `[HIGH CONFIDENCE]` requires evidence from 2+ passes or unambiguous textual proof
- `[MEDIUM CONFIDENCE]` must be framed as hypothesis
- `[LOW CONFIDENCE]` findings do not appear in Hard Truths (go in general notes)

**What Hard Truths Sound Like:**

✓ "The prose is not yet at publication quality. Sentence-level craft needs significant development before submission."

✓ "The opening 50 pages fail to establish stakes. Most agents would stop reading by page 20."

✓ "This manuscript is derivative of [COMP]. It doesn't yet offer enough differentiation to justify its place in a crowded market."

✗ "You might consider whether the prose could perhaps be strengthened."

✗ "Some readers might find the opening a bit slow."

---

## Sub-Pass 11C: Market Reality Check

**Prerequisite:** Shelf & Positioning audit must be complete.

**Purpose:** Move from category naming to commercial viability assessment.

### Market Evidence Rule

All market claims must be labeled:

- `[SOURCE-VERIFIED: date]` — Based on verifiable data (sales figures, Publisher's Marketplace, genre community consensus)
- `[MARKET INFERENCE]` — Based on system's genre knowledge, may not reflect current conditions

**Example:**
- "Romantasy is currently the fastest-growing fantasy subgenre `[SOURCE-VERIFIED: 2025 BookScan]`"
- "This heat level may limit traditional placement `[MARKET INFERENCE]`"

### Evaluate

- Shelf clarity and promise legibility
- Comp parity (does execution stand with stated comps?)
- Discovery route plausibility (query path, shelf path, direct-reader path)
- Opening conversion risk
- Category friction (straddling penalties, contract mismatch)

### Required Outputs

**Commercial Snapshot:** 1-paragraph candid assessment

**Submission Friction List:** Top 3 acquisition/agent objections likely

**Path Recommendation:** `Traditional-first` / `Hybrid` / `Self-pub-first` with rationale

### Shelf Positioning Gate

```
IF Shelf Positioning = UNCLEAR or STRADDLING
THEN Verdict cannot = READY
     Verdict maximum = CONDITIONALLY VIABLE
     Non-negotiable must include positioning fix
```

---

## Sub-Pass 11D: First-50 Conversion Gate

**Purpose:** Test whether the opening earns continuation from target readers.

### Page-by-Page Assessment

**Page 1:**
- Is there a question, tension, or promise in the first paragraph?
- Does the voice announce itself?
- Is there forward momentum by page end?

**Page 5:**
- Do we know whose story this is?
- Is there a reason to keep reading?
- Has a contract been implied?

**Page 20:**
- Is the inciting incident present or imminent?
- Do we understand the stakes?
- Are we invested in the protagonist?

**Page 50:**
- Has Act I completed its job?
- Do we know what the story is about?
- Would we keep reading?

### Promise Clarity Test

After 50 pages, can you complete these sentences?
- "This is a book about ___"
- "The main character wants ___"
- "The central tension is ___"
- "By the end, I expect ___"

**If any are unclear → Flag:** `QF-5 Opening Conversion Risk`

### Abandonment Risk Rating

Identify specific "put down" moments:
- Where would a casual reader stop?
- Where would an agent stop?
- Where would a harsh critic stop?

**Output:** `PASS` / `BORDERLINE` / `FAIL`

**Gate Rule:** If First-50 = `FAIL`, Overall Readiness cannot = `READY`

---

## Sub-Pass 11E: Revision Economics

**Purpose:** Convert critique into practical revision planning.

### Effort × Payoff × Blast Radius Matrix

For each must-fix and should-fix issue:

| Issue | Effort | Blast Radius | Payoff Type | Payoff Level | Priority |
|-------|--------|--------------|-------------|--------------|----------|
| [Issue] | Low/Med/High | Local/Multi-scene/Systemic | [Type] | High/Med/Low | [1-10] |

**Effort Levels:**
- **Low:** Line-edit level; doesn't change structure
- **Medium:** Scene/chapter revision; contained restructure
- **High:** Act-level or whole-manuscript revision

**Blast Radius:**
- **Local:** Fix is contained to specific scenes
- **Multi-scene:** Fix ripples to connected scenes
- **Systemic:** Fix requires changes throughout manuscript

**Payoff Types:**
- Reader Retention
- Contract Satisfaction
- Market Legibility
- Prose Quality
- Submission Readiness

**Priority Calculation:**
- High payoff + Low effort + Local = Priority 1-3
- High payoff + High effort = Priority 4-6
- Low payoff + Low effort = Priority 7-8
- Low payoff + High effort + Systemic = Priority 9-10 (consider deferring)

### Quick Wins

Identify 3-5 issues where small effort yields significant improvement.

### Defer List

Issues that are real but not worth addressing this cycle:
- Low impact relative to effort
- Dependent on other changes landing first
- Stylistic preference rather than craft problem

### Dependency Order

Note which fixes must happen before others:
- "Fix A before B (B depends on A's resolution)"
- "C and D can happen in parallel"

---

## Sub-Pass 11F: Adversarial Reader Stress Test

**⚠️ MIGRATED (v1.0.1):** The Adversarial Reader Stress Test has been extracted from Pass 11 and moved to the core editorial letter synthesis. It now runs as §8 of every editorial letter, regardless of whether Pass 11 is triggered. See `references/adversarial-stress-test.md` for the full specification.

**Rationale:** The stress test answers a craft question ("what would a hostile reader attack?"), not a market question. Gating it behind publication intent meant most manuscripts never received adversarial scrutiny. It is now a required element of every editorial letter.

When Pass 11 is active, the stress test still runs — but as part of the editorial letter synthesis, not as a Pass 11 sub-pass. Pass 11's other sub-passes (11A-11E) continue to function as before. If 11E (Revision Economics) is active, Fatal/Damaging + Some/Many findings from the stress test can reprioritize items per the existing escalation rules in `references/adversarial-stress-test.md`.

---

## Quality Flags (QF-* Family)

Pass 11 populates a new flag family that integrates with existing triage:

| Code | Flag | Severity Options |
|------|------|------------------|
| `QF-1` | Prose Not Ready | Must-Fix / Should-Fix |
| `QF-2` | Voice Underdeveloped | Must-Fix / Should-Fix |
| `QF-3` | Comp Mismatch | Must-Fix / Should-Fix |
| `QF-4` | Market Legibility Failure | Must-Fix / Should-Fix |
| `QF-5` | Opening Conversion Risk | Must-Fix / Should-Fix |
| `QF-6` | Submission Path Conflict | Should-Fix / Could-Fix |
| `QF-7` | Scene Voltage Failure | Should-Fix / Could-Fix |

**For each QF flag:**
- Severity: `Must-Fix` / `Should-Fix` / `Could-Fix`
- Confidence: `High` / `Medium` / `Low`
- Evidence: 2-4 references
- Impact statement: What happens if unfixed

**Integration:** QF flags carry into `Diagnostic_State.md` and persist across revision rounds.

---

## Pre-READY Verification Checklist

**Before any READY verdict, explicitly confirm each item. This is not optional.**

A verdict of READY means "this manuscript can be submitted without embarrassment." The checklist catches what strong voice can mask.

```
## Verification Checklist

### Production Continuity
- [ ] Chapter/section numbering verified (no duplicates, no gaps, consistent format)
- [ ] Part/act labels consistent in formatting
- [ ] Timeline math checked (ages, seasons, years between events)

### Thread Resolution
- [ ] All established illness/injury threads traced to resolution or explicit ambiguity
- [ ] All pregnancy/birth threads resolved
- [ ] All "will they survive?" setups paid off
- [ ] Secondary character fates closed (or explicitly left open)

### Arc Execution
- [ ] Each major character transformation has at least one bridge beat
- [ ] No arc shifts feel abrupt on re-read
- [ ] Secondary arcs don't just serve plot—they have interior logic

### Prose Consistency
- [ ] Sampled from beginning, middle, AND end (not just strong passages)
- [ ] Consistency variance assessed across long stretches
- [ ] Voice maintenance checked in exposition-heavy sections

### Adversarial Check
- [ ] Articulated what a hostile reader would criticize
- [ ] Identified what would make an agent pass
- [ ] Confirmed no generosity bias from strong voice
```

**Rule:** If any box cannot be checked, verdict cannot be READY. Downgrade to CONDITIONALLY VIABLE and add unchecked items to Non-Negotiables.

---

## Non-Negotiable Issues

For `CONDITIONALLY VIABLE` and `NOT READY` verdicts, identify issues that *must* be resolved. Maximum 5.

**Format:**
```
NON-NEGOTIABLE #1: [Issue]
- Evidence: [Specific locations]
- QF Code: [If applicable]
- Blast Radius: [Local / Multi-scene / Systemic]
- Consequence: [What happens if unfixed]
- Lens Agreement: [Which lenses flagged this]
```

**Consequence Types:**
- **Commercial** (when market mode active): "Agents will reject because...", "Readers will abandon at..."
- **Craft/Reader** (when market mode off): "Reader experience degrades because...", "Structural integrity fails because..."

**Rules:**
- Maximum 5 (if more exist, manuscript needs reconception)
- Each must have textual evidence
- Each must have stated consequence (commercial OR craft/reader, based on trigger mode)
- Cannot be hedged if `[HIGH CONFIDENCE]`

---

## Output Template

**Reminder:** All outputs must follow the Author-Facing Language requirement (SKILL.md, Output Constraints). Translate all framework codes (QF flags, P-tier labels, confidence tags, pass numbering, escalation thresholds) into plain language on first use. The author should never need to consult the framework to understand a finding.

```markdown
# Pass 11: Critical Quality & Market Viability Assessment

## Trigger Basis
[Why Pass 11 was activated]

---

## Overall Verdict: [READY / CONDITIONALLY VIABLE / NOT READY]

---

## Sub-Pass 11A: Writing Quality

**Prose Tier:** [P0 / P1 / P2 / P3]
**Voice:** [DISTINCTIVE / DEVELOPING / GENERIC]
**Scene Voltage:** [Consistent / Uneven / Low]

[3-5 sentence summary of prose strengths and weaknesses]

---

## Sub-Pass 11B: Critical Verdict

### Lens Assessments

| Lens | Verdict | Summary |
|------|---------|---------|
| Acquiring Editor | [ACQUIRE/R&R/PASS] | [1-2 sentences] |
| Category Super-Reader | [RECOMMEND/MIXED/WNF] | [1-2 sentences] |
| Skeptical Critic | [NOTABLE/COMPETENT/DERIVATIVE] | [1-2 sentences] |

**Lens Agreement:** [3/3 / 2/3 / Split]
[Note significant disagreements]

### Hard Truths

1. [CONFIDENCE] [Truth]
2. [CONFIDENCE] [Truth]
3. [CONFIDENCE] [Truth]
[4-5 if applicable]

---

## Sub-Pass 11C: Market Reality [If activated]

**Commercial Snapshot:**
[1 paragraph]

**Submission Frictions:**
1. [Friction + evidence tag]
2. [Friction + evidence tag]
3. [Friction + evidence tag]

**Path Recommendation:** [Traditional-first / Hybrid / Self-pub-first]
Rationale: [2-3 sentences]

**Shelf Gate:** [PASS / BLOCKED]

---

## Sub-Pass 11D: First-50 Assessment [If activated]

**Conversion Gate:** [PASS / BORDERLINE / FAIL]
**Abandonment Risk:** [LOW / MEDIUM / HIGH]

[Summary with specific page references]

---

## Sub-Pass 11E: Revision Economics [If activated]

| Issue | Effort | Blast Radius | Payoff | Priority |
|-------|--------|--------------|--------|----------|
| [...] | [...] | [...] | [...] | [...] |

**Quick Wins:**
1. [Win]
2. [Win]
3. [Win]

**Defer:**
- [Issue + rationale]

**Dependencies:**
- [Dependency chain]

---

## [11F: Migrated to editorial letter §8 — see references/adversarial-stress-test.md]

---

## Quality Flags

| Code | Flag | Severity | Confidence | Evidence | Impact |
|------|------|----------|------------|----------|--------|
| QF-x | [...] | [...] | [...] | [...] | [...] |

---

## Non-Negotiables [If CONDITIONALLY VIABLE or NOT READY]

**#1:** [Issue]
- Evidence:
- QF Code:
- Blast Radius:
- Consequence: [Commercial OR Craft/Reader based on trigger mode]
- Lens Agreement:

[Repeat for #2-5 as needed]

---

## Pre-READY Verification [Required for READY verdict]

| Check | Status | Notes |
|-------|--------|-------|
| Chapter/section numbering | ✓/✗ | |
| Timeline math | ✓/✗ | |
| Thread resolution (illness/fate) | ✓/✗ | |
| Arc bridge beats | ✓/✗ | |
| Prose consistency (distributed sample) | ✓/✗ | |
| Adversarial critique completed | ✓/✗ | |

[If any ✗, verdict cannot be READY]

---

## Verdict Summary

[One paragraph: honest assessment of where this manuscript stands, what it needs, and realistic path forward]

*Framework: APODICTIC Development Editor (APDE)*
```

---

## Firewall Compliance

Pass 11 maintains the Firewall:

**ALLOWED:**
- Quality assessment and verdicts
- Commercial viability analysis
- Comparison to market standards
- Identification of problems
- Prioritization guidance
- Path recommendations

**FORBIDDEN:**
- Generating replacement prose
- Inventing plot solutions
- Creating new content
- Specific line edits
- Rewriting passages

Pass 11 says "the prose isn't ready" and "here's what's wrong"—not "here's how to rewrite it."

---

## Integration Notes

### Relationship to Existing Passes

- Pass 11 **consumes** findings from all prior passes
- Pass 11 **does not repeat** structural diagnosis (references it)
- Pass 11 **adds** quality/viability layer
- Pass 11 **gates** deliverable framing

### Relationship to Diagnostic_State

- QF flags persist in `Diagnostic_State.md`
- Revision Round Protocol checks QF resolution
- Non-negotiables carry forward until addressed

### Deliverable Framing by Verdict

- **READY:** Editorial letter focuses on polish
- **CONDITIONALLY VIABLE:** Editorial letter focuses on must-fixes
- **NOT READY:** Editorial letter addresses revision vs. reconception decision

---

*Pass 11 is the honest friend. It tells authors what they need to hear, not what they want to hear. A developmental edit without this evaluation is incomplete—it identifies problems but won't say whether the problems are fatal. Pass 11 says the quiet part out loud.*
