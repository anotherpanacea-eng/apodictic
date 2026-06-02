# Timeline — Worked Example

<!--
Worked example of a Pass 10 `Timeline.md` artifact (see pass-10.md §Timeline.md Schema).
This file is contract-conformant and is exercised by `validate.sh --check-all` as a canonical
release-gate target for `timeline-arithmetic`, `timeline-anchor-conflict`, and `timeline-diff`
(self-diff). It is illustrative, not a run artifact; keep it passing when the Timeline schema
or the timeline validators change.
-->

## Section 1: Event Ledger

| Scene ID | Chapter / Section | Line range | Word count | POV | Setting | Anchor type | Anchor text | Calculated date | Calculated time-of-day | Span | Gap from previous scene | Confidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Ch 1 §1 | Ch 1 | 1-118 | 1480 | Mara | Kitchen | explicit-day | "Monday morning" | Day 1 | morning | 3 hours | n/a | HIGH |
| Ch 1 §2 | Ch 1 | 119-240 | 1390 | Mara | Office | relative-to-previous | "that same afternoon" | Day 1 | afternoon | 2 hours | 3 hours | HIGH |
| Ch 2 §1 | Ch 2 | 241-372 | 1610 | Jon | Train station | explicit-day | "the next morning" | Day 2 | morning | 1 hour | 16 hours | HIGH |

## Section 2: Master Calendar

- **Day 1** — Ch 1 §1 (morning), Ch 1 §2 (afternoon).
- **Day 2** — Ch 2 §1 (morning).

## Section 3: Temporal Marker Inventory

- Ch 1 §1: "Monday morning" → Day 1
- Ch 1 §2: "that same afternoon" → Day 1
- Ch 2 §1: "the next morning" → Day 2

## Section 4: Inconsistency Ledger

n/a — no temporal inconsistencies detected.

## Section 5: Ambiguity Ledger

n/a — no structural under-anchoring detected.

## Section 6: Revision-Drift Hot Spots

n/a — single-pass baseline; no drift indicators yet.

## Section 7: Recommended Anchor Set

- Fix the Day-1 start anchor ("Monday morning"); downstream scenes Ch 1 §2 and Ch 2 §1 derive from it.

## Section 8: Diff Notes

n/a — first Timeline run for this project.
