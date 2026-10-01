# Research Mode: Comp Validation (v1.0)

## Purpose

Verify that author-provided comparable titles are current, correctly positioned, and useful for querying. Stale or mispositioned comps undermine query letters and create false expectations.

**When to activate:**
- Any comp is >3 years old (publication date)
- Comp is unfamiliar to the system (low confidence on positioning)
- Author's comps span multiple shelves without clear rationale
- Comp author has since become problematic (cancellation, genre pivot)
- Preparing query letter or pitch materials

**Core principle:** Comps are arguments, not descriptions. They must be *currently working* in the market.

---

## Part 1: Comp Triage

For each author-provided comp, assess:

| Comp Title | Pub Date | Shelf | Still in Print? | Known Issues? |
|------------|----------|-------|-----------------|---------------|

**Logic Gate: Age Check**
```
IF Pub Date > 3 years ago → FLAG: "Stale Comp"
IF Pub Date > 5 years ago → FLAG: "Expired Comp" (likely unusable for query)
```

**Logic Gate: Availability Check**
```
IF Out of Print AND not a classic → FLAG: "Unavailable Comp"
(Agent/editor may not recognize it)
```

---

## Part 2: Research Protocol

**For each flagged comp, search:**

1. `"[comp title]" + "comparable titles" OR "readers also bought"`
2. `[comp author] + "recent" + [current year]`
3. `[comp's shelf] + "bestseller" OR "debut" + [last 2 years]`

**Output per comp:**
```
Original Comp: [title]
Status: VALID / STALE / EXPIRED / MISPOSITIONED
If Invalid, Replacement Candidates:
  - [Title 1] (Pub: [year]) — [why it works]
  - [Title 2] (Pub: [year]) — [why it works]
Comp Function: Tone / Structure / Audience / Heat Level / [other]
```

---

## Part 3: Comp Function Mapping

Comps serve different purposes. Clarify what each is meant to signal:

| Function | What It Signals | Example |
|----------|-----------------|---------|
| **Tone Comp** | Voice, mood, register | "The humor of [X]" |
| **Structure Comp** | Architecture, pacing | "The dual timeline of [X]" |
| **Audience Comp** | Who will buy this | "Readers of [X]" |
| **Heat/Darkness Comp** | Content calibration | "The intensity of [X]" |
| **Prestige Comp** | Literary positioning | "In the tradition of [X]" |
| **Commercial Comp** | Market viability | "For fans of [X]" |

### Developmental vs. Query-Ready Comps

**Critical distinction:** Not all comps belong in a query letter.

| Comp Type | Medium Allowed | Purpose | Where It Belongs |
|-----------|----------------|---------|------------------|
| **Developmental** | Books, films, TV, games, any | Internal understanding of tone, structure, vibe | Contract document, author notes |
| **Query-Ready** | Books only (rare film exception) | Convince agent you know the book market | Query letter, pitch materials |

**Why this matters:**
- Film comps in queries signal "I don't read in my genre"
- Agents want to see you understand the *book* market specifically
- Film/TV comps are useful shorthand for tone—just keep them internal

**Logic Gate: Medium Check**
```
IF comp is film/TV/game AND context = query letter → FLAG: "Wrong Medium for Context"
  Action: Find book equivalent or move to developmental comps
IF comp is film/TV AND context = developmental/internal → PASS (useful for tone/structure)
```

**Translating Film Comps to Book Equivalents:**

When a film comp captures something essential, find the book that does the same work:

| Film Comp | What It Captures | Book Equivalent(s) |
|-----------|------------------|-------------------|
| *Stranger Than Fiction* | Metafictional narrator | *The French Lieutenant's Woman*, *If on a winter's night a traveler* |
| *Marie Antoinette* (Coppola) | Anachronistic wit in period setting | *Slammerkin*, *Hag-Seed*, *Circe* |
| *The Grand Budapest Hotel* | Nested narration, whimsy + melancholy | *The Shadow of the Wind*, *Cloud Atlas* |
| *Amélie* | Whimsical narrator, magical realism lite | *The Storied Life of A.J. Fikry*, *A Man Called Ove* |
| *Atonement* | Literary structure, earned tragedy | *The Remains of the Day*, *On Earth We're Briefly Gorgeous* |

**Output format for comps with film originals:**
```
Developmental Comp (internal): [Film title] — captures [X]
Query-Ready Equivalent: [Book title] — same structural driver in book form
```

**Logic Gate: Function Coverage**
```
CHECK: Do comps cover at least 2 distinct functions?
IF Yes → PASS
IF All comps serve same function → FLAG: "One-Dimensional Comp Set"
  Recommendation: Add comp serving [missing function]
```

---

## Part 4: The Three-Comp Test

Industry standard: Query letters use 2-3 comps. Test the set:

**Test 1: Recognition**
```
Would a mid-level agent recognize all comps without Googling?
IF No → Replace obscure comp with more recognizable alternative
```

**Test 2: Shelf Alignment**
```
Do all comps live on the same primary shelf?
IF No → Either justify the crossover or tighten the set
```

**Test 3: Recency Spread**
```
Is at least one comp from the last 18 months?
IF No → FLAG: "Comp Set Dated"
```

**Test 4: Comp Collision**
```
Do any two comps contradict each other's signals?
(e.g., one signals "cozy," another signals "dark")
IF Yes → FLAG: "Contradictory Comps" — clarify which signal governs
```

---

## Part 5: Output — Comp Memo

```
COMP VALIDATION REPORT

Original Comps Provided:
1. [Title] — [Status: VALID/STALE/etc.] — Function: [X]
2. [Title] — [Status] — Function: [X]
3. [Title] — [Status] — Function: [X]

Flags:
- [List any flags triggered]

Recommended Comp Set:
1. [Title] (Pub: [year]) — [Function] — [Why]
2. [Title] (Pub: [year]) — [Function] — [Why]
3. [Title] (Pub: [year]) — [Function] — [Why]

Coverage Check:
- Tone: ✓/✗
- Structure: ✓/✗
- Audience: ✓/✗
- Heat/Content: ✓/✗ (if applicable)

Notes for Query:
[Any positioning advice for how to frame the comps]
```

---

## Guardrails

- Research supplements author knowledge; doesn't override author's vision of their book
- If research returns contradictory positioning, note ambiguity—don't force false clarity
- Cap research at 3-5 queries per comp; more suggests the comp itself is wrong, not the search
- Never recommend comps the system hasn't verified are correctly positioned
- Flag but don't auto-replace comps with personal significance to author (mentor's book, etc.)

---

## Integration

- **Trigger:** During Intake (after Contract) or during Synthesis (before query prep)
- **Add to Contract Document:** Validated comp set with functions noted
- **Cross-reference:** Shelf & Positioning audit (comps should align with Predicted Trade Shelf)

---

*Comps are promises. Stale comps are broken promises. This module ensures the promises are current and keepable.*
