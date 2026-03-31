# Research Mode: Genre Contract Currency (v1.0)

## Purpose

Verify that genre contract expectations reflect *current* market norms before flagging violations. Genre lines shift faster than training data updates. What was transgressive becomes trope; what was required becomes optional.

**When to activate:**
- Subgenre is <5 years old or recently emerged (e.g., "romantasy," "cozy fantasy," "spicy fantasy")
- Contract element feels unfamiliar or unstable
- Author pushes back on a genre flag ("That's not how [subgenre] works anymore")
- Manuscript straddles categories that may have merged or split
- Genre terminology in the manuscript doesn't match system's lexicon

**Core principle:** Genre contracts are social agreements, not natural laws. They evolve. The system must know *when* it knows and *when* it needs to check.

---

## Part 1: Genre Confidence Assessment

Before flagging any contract violation, assess system confidence:

```
Genre/Subgenre: [X]
Last Verified: [training data cutoff / previous research]
Confidence: HIGH / MEDIUM / LOW

HIGH: Genre stable, well-documented (e.g., Cozy Mystery, Epic Fantasy)
MEDIUM: Genre active, some recent evolution (e.g., Dark Romance, LitRPG)
LOW: Genre new, hybrid, or rapidly evolving (e.g., Romantasy, Cozy Fantasy, Spicy Regency)
```

**Logic Gate:**
```
IF Confidence = LOW → Activate Research Mode before flagging violations
IF Confidence = MEDIUM AND flag is "Contract Violation" → Verify before reporting
IF Confidence = HIGH → Proceed with standard analysis
```

---

## Part 2: Research Protocol

**Search queries (in order):**

1. `"[subgenre]" + "definition" OR "expectations" + [current year]`
2. `"[subgenre]" + "tropes" OR "contract" + "readers expect"`
3. `"[subgenre]" + "controversy" OR "debate"` (to surface contested norms)
4. `"[subgenre]" + "bestseller" + [last 2 years]` (to identify exemplars)

**For hybrid/emerging genres, also search:**
- `"[subgenre]" + "vs" + "[parent genre]"` (to understand differentiation)
- `"[subgenre]" + "BookTok" OR "Bookstagram"` (to capture community usage)

---

## Part 3: Contract Element Verification

For each potentially flagged element, determine:

| Contract Element | System's Assumption | Current Evidence | Status |
|------------------|--------------------|--------------------|--------|
| [Element] | [What system believes] | [What research shows] | CONFIRMED / EVOLVED / CONTESTED |

**Status Definitions:**
- **CONFIRMED:** System's assumption matches current market
- **EVOLVED:** Norm has shifted; update assumption before flagging
- **CONTESTED:** Community actively debates this; flag as "contested norm," not violation

---

## Part 4: Subgenre Snapshot

When research is activated, generate a current snapshot:

```
SUBGENRE SNAPSHOT: [Name]

Parent Genre(s): [X, Y]
Emerged/Solidified: [approximate year]
Current Status: STABLE / EVOLVING / CONTESTED / FRAGMENTING

Core Contract (Non-Negotiable):
- [Element 1]
- [Element 2]
- [Element 3]

Variable Elements (Author Discretion):
- [Element]: Range from [X] to [Y]
- [Element]: Common but not required

Recent Evolution (last 2-3 years):
- [Change 1]: [Evidence]
- [Change 2]: [Evidence]

Active Debates:
- [Contested element]: [Both positions]

Exemplar Titles (last 24 months):
- [Title 1] — [What it demonstrates about current norms]
- [Title 2] — [What it demonstrates]
```

---

## Part 5: Flag Calibration

After research, recalibrate any genre flags:

**Before Research:**
```
FLAG: "Contract Violation — [Element]"
```

**After Research, choose:**

```
CONFIRMED VIOLATION:
Research confirms [element] remains non-negotiable.
FLAG: "Contract Violation — [Element]"
Evidence: [cite current sources]

EVOLVED NORM:
Research shows [element] is no longer required / now expected.
WITHDRAW FLAG or REVISE to: "[New assessment]"
Evidence: [cite current sources]

CONTESTED NORM:
Research shows community actively debates [element].
REVISE FLAG to: "Contested Genre Element — [Element]"
Note: "Some [subgenre] readers expect [X]; others accept [Y]. Author should make intentional choice."

INSUFFICIENT DATA:
Research inconclusive.
REVISE FLAG to: "Possible Contract Issue — [Element] (unverified)"
Recommend: Author consult beta readers in target community
```

---

## Part 6: Genre Lexicon Updates

When research reveals terminology shifts, note for future reference:

```
TERMINOLOGY UPDATE:
- Old term: [X] → Current term: [Y]
- New subgenre identified: [Name] — Definition: [X]
- Merged categories: [A] + [B] now commonly called [C]
- Split category: [X] has divided into [Y] and [Z]
```

---

## Guardrails

- Research verifies norms; it doesn't make aesthetic judgments
- If sources contradict, present the range—don't pick a winner
- Never claim authority over community-defined terms
- Cap research at 5 queries per genre question; more suggests the question is unanswerable
- When in doubt, flag as "contested" rather than "violation"
- Author's stated subgenre gets benefit of the doubt if research is ambiguous

---

## Integration

- **Trigger:** Automatically when Confidence = LOW; manually when author disputes a flag
- **Output location:** Append to Genre Calibration section of analysis
- **Cross-reference:** Shelf & Positioning audit (genre currency affects shelf prediction confidence)

---

## Quick Reference: High-Velocity Genres

These genres evolve quickly enough to warrant automatic LOW confidence and research activation:

| Genre | Why It Moves Fast |
|-------|-------------------|
| **Romantasy** | Category <5 years old; boundaries still forming |
| **Cozy Fantasy** | Emerged ~2022; norms actively debated |
| **Dark Romance** | Heat/consent norms shift with platform (TikTok vs. trad pub) |
| **Spicy [X]** | "Spicy" as modifier is new; thresholds vary by community |
| **Progression/LitRPG** | Rapidly iterating tropes; web serial vs. trad pub split |
| **Romantasy** | Definition contested (romance + fantasy? fantasy + romance subplot?) |
| **New Adult** | Age bracket fuzzy; content expectations vary by publisher |
| **BookTok genres** | Community-driven categories may not match BISAC |

For these genres, always research before flagging contract violations.

---

*Genre is a conversation, not a rulebook. This module ensures the system is listening to the current conversation.*
