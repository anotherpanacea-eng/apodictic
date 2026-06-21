# Continuity Bible: A Quiet Year (literary fiction)

<!--
Worked example of a contract-conformant Auto-Derived Continuity Bible (see continuity-bible.md +
docs/continuity-bible.md). The Bible is the NARRATIVE half of a developmental-edit style sheet: a
single, locus-anchored reference of the canonical facts the manuscript commits to — identity /
physical facts (ages, spellings, aliases), named objects, place details — plus consolidated
chronology, and a Contradiction Ledger of the places the text commits to two facts at once.

The module firewall is *extract the stated, never author the unstated*: each fact records what the
text asserts, with its loci; a contradiction records BOTH conflicting values (here Mara's age) and
is SURFACED, never resolved — choosing canon is the author's call.

This file is exercised by `validate.sh --check-all` (paired with `example-timeline.md`) as a
canonical release-gate target for `continuity-bible`: C1 schema, C2 locus shape, C3 contradiction
integrity, a clean C4 chronology-consume check (CF-11 consolidates the real Timeline scene id
`Ch 1 §2`), and clean W1 coverage (every Timeline POV — Mara, Jon — has a Cast entry and every
Timeline setting — Kitchen, Office, Train station — has a Places entry). `value` is ALWAYS a string
(numerics quoted: "30"/"32"); `consolidates` is null unless the fact is consumed from the Timeline.
-->

## Cast

<!-- apodictic:canon_fact
{"schema":"apodictic.canon_fact.v1","id":"CF-01","entity":"Mara","category":"person","attribute":"role","value":"the narrator-protagonist","loci":["Ch 1 §1"],"consolidates":null}
-->

<!-- apodictic:canon_fact
{"schema":"apodictic.canon_fact.v1","id":"CF-02","entity":"Mara","category":"person","attribute":"surname spelling","value":"Vance","loci":["Ch 1","Ch 9"],"consolidates":null}
-->

<!-- apodictic:canon_fact
{"schema":"apodictic.canon_fact.v1","id":"CF-03","entity":"Mara","category":"person","attribute":"age","value":"30","loci":["Ch 2 ¶6"],"consolidates":null}
-->

<!-- apodictic:canon_fact
{"schema":"apodictic.canon_fact.v1","id":"CF-04","entity":"Mara","category":"person","attribute":"age","value":"32","loci":["Ch 9 ¶4"],"consolidates":null}
-->

<!-- apodictic:canon_fact
{"schema":"apodictic.canon_fact.v1","id":"CF-05","entity":"Jon","category":"person","attribute":"role","value":"Mara's estranged brother","loci":["Ch 2 §1"],"consolidates":null}
-->

<!-- apodictic:canon_fact
{"schema":"apodictic.canon_fact.v1","id":"CF-06","entity":"Jon","category":"person","attribute":"alias","value":"Jonny (only their mother uses it)","loci":["Ch 2 ¶11"],"consolidates":null}
-->

## Places

<!-- apodictic:canon_fact
{"schema":"apodictic.canon_fact.v1","id":"CF-07","entity":"Kitchen","category":"place","attribute":"description","value":"the family kitchen where the story opens","loci":["Ch 1 §1"],"consolidates":null}
-->

<!-- apodictic:canon_fact
{"schema":"apodictic.canon_fact.v1","id":"CF-08","entity":"Office","category":"place","attribute":"description","value":"Mara's downtown workplace","loci":["Ch 1 §2"],"consolidates":null}
-->

<!-- apodictic:canon_fact
{"schema":"apodictic.canon_fact.v1","id":"CF-09","entity":"Train station","category":"place","attribute":"description","value":"the regional station where Jon arrives","loci":["Ch 2 §1"],"consolidates":null}
-->

## Objects

<!-- apodictic:canon_fact
{"schema":"apodictic.canon_fact.v1","id":"CF-10","entity":"the mother's wedding ring","category":"object","attribute":"significance","value":"the inheritance token contested between Mara and Jon","loci":["Ch 3 ¶2","Ch 9 ¶18"],"consolidates":null}
-->

## Chronology

<!-- apodictic:canon_fact
{"schema":"apodictic.canon_fact.v1","id":"CF-11","entity":"Mara's office arrival","category":"chronology","attribute":"day","value":"Day 1, afternoon","loci":["Ch 1 §2"],"consolidates":"Ch 1 §2"}
-->

## Contradiction Ledger

The manuscript states two different ages for Mara. Both are recorded; the Bible does not pick a
winner — reconciling canon is the author's call.

| Entity | Attribute | Conflicting facts | Note |
|---|---|---|---|
| Mara | age | CF-03, CF-04 | "30" in Ch 2 ¶6 vs "32" in Ch 9 ¶4 — surfaced, not resolved |

## Notes

- **Facts are stated, never inferred.** Every entry cites the locus where the manuscript asserts it.
  Mara's age appears twice, in conflict, so both are catalogued and paired in the Contradiction
  Ledger — the Bible makes the conflict impossible to miss and stops there.
- **Chronology is consumed, not re-derived.** CF-11 consolidates the Pass-10 Timeline scene id
  `Ch 1 §2` rather than re-stating a temporal fact the Timeline already owns (validator C4).
- **Locus presence/shape is gated (C2), not resolved.** A locus is checked for a coarse
  chapter/§/¶ shape; resolving each citation into the manuscript waits on the shared snapshot layer,
  so the firewall is author/QA-enforced until then.
