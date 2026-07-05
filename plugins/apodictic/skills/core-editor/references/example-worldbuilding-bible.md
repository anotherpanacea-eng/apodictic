# Worldbuilding Bible: The Sundering Cycle (epic fantasy)

<!--
Worked example of a contract-conformant standalone Worldbuilding Bible (see worldbuilding-bible.md +
docs/worldbuilding-bible.md). This is the SFF author's OWN pre-draft reference — the rules of the
magic, its cost, the geography, the order of events, the factions — checked for self-contradiction
BEFORE any manuscript exists. The tool checks a BIBLE (not a manuscript) for closed-set rule
consistency, magic-system cost accounting, and geography/timeline contradiction, and SURFACES the
contradictions the bible has already committed to; it never invents world content or resolves a
conflict (the Firewall: extract the stated, never author the unstated).

This file is exercised by `validate.sh --check-all` (under `--strict`) as a canonical release-gate
target for `world-bible`: W1 schema + closed-key, WD unique ids, WB-R1 closed-set rule consistency,
WB-C1/WB-C2 cost accounting, WB-G1 distance (within a unit class), WB-G2 chronology (cycle +
anchor-drift), and the WF firewall prose scan. Two contradictions are present and DELIBERATELY STAGED
by the author (a rule that changes after the Sundering, WF-02/WF-03; a cost that escalates for
novices, WF-11/WF-12) — each carries a per-pair override that records the author's intent without
softening the verdict, so the file is clean under `--strict`. `value` is ALWAYS a string (numerics
quoted: "6 days", "120 miles", "Day 100"); a travel-TIME and a spatial DISTANCE are separate axes
that never collide-check against each other.
-->

This bible is the author's pre-draft reference. Where the world's rules intentionally change — a
limit that lifts after the Sundering, a cost that escalates for the untrained — both stated values
are recorded and the staged contradiction is marked with an override. The bible surfaces conflicts;
reconciling canon is the author's call.

<!-- override: world-rule WF-02/WF-03 — staged reveal: blood-magic gains the power to raise the dead only after the Sundering breaks the old binding -->
<!-- override: world-cost WF-11/WF-12 — documented escalation: untrained casters pay a year of life; trained adepts pay only a day -->

## Rules

<!-- apodictic:world_fact
{"schema":"apodictic.world_fact.v1","id":"WF-01","category":"rule","subject":"blood-magic","attribute":"limit","value":"cross running water","polarity":"cannot","loci":["Bible §Magic ¶3"]}
-->

<!-- apodictic:world_fact
{"schema":"apodictic.world_fact.v1","id":"WF-02","category":"rule","subject":"blood-magic","attribute":"limit","value":"raise the dead","polarity":"cannot","loci":["Bible §Magic ¶4 (before the Sundering)"]}
-->

<!-- apodictic:world_fact
{"schema":"apodictic.world_fact.v1","id":"WF-03","category":"rule","subject":"blood-magic","attribute":"limit","value":"raise the dead","polarity":"can","cost":"the caster's own name","loci":["Bible §Magic ¶9 (after the Sundering)"]}
-->

<!-- apodictic:world_fact
{"schema":"apodictic.world_fact.v1","id":"WF-04","category":"rule","subject":"the Wardens","attribute":"capability","value":"a binding requires the warden's true name","polarity":"requires","cost":null,"loci":["Bible §The Wardens ¶2"]}
-->

## Costs

<!-- apodictic:world_fact
{"schema":"apodictic.world_fact.v1","id":"WF-10","category":"cost","subject":"a scrying","attribute":"cost","value":"the price of a far-sight casting","polarity":"n/a","cost":"a day of blindness","loci":["Bible §Costs ¶1"]}
-->

<!-- apodictic:world_fact
{"schema":"apodictic.world_fact.v1","id":"WF-11","category":"cost","subject":"a resurrection","attribute":"cost","value":"the price for an untrained caster","polarity":"n/a","cost":"one year of life","loci":["Bible §Costs ¶4"]}
-->

<!-- apodictic:world_fact
{"schema":"apodictic.world_fact.v1","id":"WF-12","category":"cost","subject":"a resurrection","attribute":"cost","value":"the price for a trained adept","polarity":"n/a","cost":"a day of life","loci":["Bible §Costs ¶5"]}
-->

## Places & Distances

<!-- apodictic:world_fact
{"schema":"apodictic.world_fact.v1","id":"WF-20","category":"place","subject":"Karth","attribute":"description","value":"the northern fortress-city on the river Sere","polarity":"n/a","cost":null,"loci":["Bible §Geography ¶2"]}
-->

<!-- apodictic:world_fact
{"schema":"apodictic.world_fact.v1","id":"WF-21","category":"distance","subject":"Karth","attribute":"distance-to","value":"120 miles","polarity":"n/a","cost":null,"pair_subject":"the capital","loci":["Bible §Geography ¶3","Map note 2"]}
-->

<!-- apodictic:world_fact
{"schema":"apodictic.world_fact.v1","id":"WF-22","category":"distance","subject":"Karth","attribute":"travel-time-to","value":"6 days by horse","polarity":"n/a","cost":null,"pair_subject":"the capital","loci":["Bible §Geography ¶3"]}
-->

## Chronology

<!-- apodictic:world_fact
{"schema":"apodictic.world_fact.v1","id":"WF-30","category":"event","subject":"the Founding","attribute":"happens-before","value":"before","polarity":"n/a","cost":null,"pair_subject":"the Sundering","loci":["Bible §History ¶1"]}
-->

<!-- apodictic:world_fact
{"schema":"apodictic.world_fact.v1","id":"WF-31","category":"event","subject":"the Sundering","attribute":"happens-before","value":"before","polarity":"n/a","cost":null,"pair_subject":"the Long Winter","loci":["Bible §History ¶6"]}
-->

<!-- apodictic:world_fact
{"schema":"apodictic.world_fact.v1","id":"WF-32","category":"event","subject":"the Sundering","attribute":"day-anchor","value":"Day 100 of the new reckoning","polarity":"n/a","cost":null,"loci":["Bible §History ¶6"]}
-->

## Factions

<!-- apodictic:world_fact
{"schema":"apodictic.world_fact.v1","id":"WF-40","category":"faction","subject":"the Wardens","attribute":"commitment","value":"sworn to keep the old bindings intact","polarity":"n/a","cost":null,"loci":["Bible §The Wardens ¶1"]}
-->

<!-- apodictic:world_fact
{"schema":"apodictic.world_fact.v1","id":"WF-41","category":"entity","subject":"the Sere","attribute":"nature","value":"the running river that bounds blood-magic","polarity":"n/a","cost":null,"loci":["Bible §Geography ¶2"]}
-->

## Contradiction Ledger

The bible states two intentional, staged contradictions. Both pairs are recorded with an override
that names the author's intent; the bible records both stated values and does not pick a winner.

| Subject | Arm | Conflicting facts | State | Author's note |
|---|---|---|---|---|
| blood-magic | rule (WB-R1) | WF-02, WF-03 | apparent | "cannot raise the dead" before the Sundering vs "can" after — staged reveal, override world-rule |
| a resurrection | cost (WB-C1) | WF-11, WF-12 | apparent | "one year of life" (untrained) vs "a day of life" (adept) — documented escalation, override world-cost |

The `State` column is the mechanically-derived contradiction axis (orthogonal to editorial severity):
`conflicting` (a live, un-overridden collision), `apparent` (a collision an override marks intentional
— as both rows here are), or `consistent` (no collision — never written as a row). Both rows above
derive `apparent` because each pair carries a matching `world-rule` / `world-cost` override.

## Notes

- **Facts are stated, never invented.** Every fact cites the bible locus where it is asserted. Where
  the world's rules change (WF-02 → WF-03) or its costs escalate (WF-11 → WF-12), both stated values
  are recorded and the staged contradiction is overridden — the bible surfaces the conflict and
  leaves canon to the author.
- **Distance and travel-time are separate axes.** WF-21 ("120 miles") and WF-22 ("6 days by horse")
  describe the same Karth↔capital edge on different axes (spatial vs travel-time); the tool never
  treats them as the same quantity, so they do not collide.
- **Chronology is an ordering, not a re-derivation.** The happens-before edges (Founding → Sundering
  → Long Winter) form an acyclic order; WF-32 anchors the Sundering to a single day.
