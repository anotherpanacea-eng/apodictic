# Cost-Floor Cap — run-metadata note (mid-draft round)

<!--
Canonical CLEAN cost-floor worked example for the `cost-floor` validator (run-core.md §Cost-floor
override (budget cap)). A cost-constrained user caps this run BELOW the token-fit floor at the
cheapest load-viable mode, with the tradeoff disclosed. The record carries BOTH halves — the
mode-suffixed override marker AND the matching `cost_floor_override` metadata token — and the
low-risk contract fires none of the five quality-risk triggers (Q1-Q5), so CF4 has nothing to
demote. Paired with example-cost-floor-preflight.md, whose standard-context token-fit floor sits
above this cap (so the below-floor tradeoff is real and disclosure-acknowledged).

This note deliberately paraphrases rather than quoting any Q1-Q5 trigger literal that would trip
the validator against its own documentation.

Exercised by `validate.sh --check-all`:
  * clean arm  — cost-floor over this note + the preflight packet is record-integrity clean (exit 0;
                 the below-floor and meta-withheld dimensions surface advisory WARNs);
  * hostile 1  — a throwaway copy with the cost_floor_override token line deleted FAILs CF2;
  * hostile 2  — a throwaway copy with a submit goal appended fires Q5 (target above the cap) with no
                 paired override and FAILs CF4;
  * hostile 3  — a throwaway copy with the marker line stripped (token kept) WARNs on the CF1 reverse
                 orphan-token check by default and FAILs under --strict.
-->

## Contract (low-risk — fires no quality-risk trigger)

GENRE/SUBGENRE: Literary fiction / family drama
DARKNESS LEVEL: Low
POV count: 1
STRUCTURE: linear / strictly chronological across one summer
GOAL: structural revision (mid-draft developmental pass; opening act and midpoint)
RECOMMENDED AUDITS: Scene Turn, Emotional Craft, Interiority Calibration

## Cost-Floor Cap

The parent orchestrator's standard-context token-fit floor for this manuscript sits above the mode
below (see the paired preflight packet), but the author is on a constrained usage budget and has
accepted the compaction / late-pass salience tradeoff for this exploratory mid-draft round. The cap
is recorded as BOTH an override marker and a run-metadata token — both required, and they must agree
on the mode:

<!-- override: cost-floor-sequential — $20-plan usage window; exploratory mid-draft round, accepted the compaction disclosure -->

cost_floor_override: sequential — $20-plan usage window; exploratory mid-draft round, accepted the compaction disclosure

Because the cap is sequential and no quality-risk trigger fires, CF4 has no fired Q-target above the
cap to demote — the cap only lowers the token-fit floor, exactly as designed.

---

*Framework: APODICTIC Development Editor (APDE)*
*Diagnostic posture: mid-draft round; user-declared cost-floor cap accepted with disclosure.*
