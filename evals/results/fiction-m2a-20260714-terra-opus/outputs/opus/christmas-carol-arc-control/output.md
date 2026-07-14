# APODICTIC Structural Diagnostic

Manuscript treated as complete. Five staves, single protagonist arc (Scrooge), frame + three vision movements. Diagnosis below is drawn only from the submitted text.

---

## Pass 0 — Reverse Outline

- **Stave I:** Marley established dead (7 yrs). Scrooge characterized. Beats: Fred's invitation (rebuffed) → two charity gentlemen (rebuffed) → clerk dismissed for the day → walk home → Marley's face in the knocker → Marley's Ghost: warning + three-spirit prophecy → phantoms in the air.
- **Stave II (Past):** School/solitary boy → Ali Baba reverie → Fan fetches him home → Fezziwig's ball → Belle's release → Belle's later family (Scrooge seen "quite alone").
- **Stave III (Present):** City morning → Cratchit dinner + Tiny Tim → miners → lighthouse → ship → Fred's party → Ignorance & Want.
- **Stave IV (Yet To Come):** Businessmen dismiss a death → old Joe & the three plunderers → the unnamed corpse → Caroline (relieved debtor) → Cratchits mourn Tim → gravestone reveal: EBENEZER SCROOGE.
- **Stave V:** Reformation → turkey to the Cratchits → charity gentleman → Fred's dinner → Cratchit's raise → coda (Tim lives).

## Pass 1 — Premise/Spine

Spine is single and clean: a miser is given a supernatural audit of his own moral ledger across three tenses and reforms. Every stave advances one internal metric (recognition → grief → dread → resolve). No spine drift.

## Pass 2 — Beat Map / Causal Chain / Orphans

Causal chain is tight and mostly *thematic-causal* rather than plot-causal (the spirits, not Scrooge, drive locomotion; Scrooge supplies the internal turn). Two clusters do **not** attach to the causal spine or introduce recurring entities — see **F-STRUCT-02**. All Stave I/II/V beats are load-bearing and paid off.

## Pass 5 — Character Cards / Agency

- **Scrooge** — full agency in I and V; deliberately *passive observer* through II–IV (the design of a conversion narrative). Arc complete.
- **Ghost of Christmas Yet To Come** — zero dialogue, gesture only. Read as intentional (dread by silence), not an agency defect.
- **Fred, Bob, Belle, Fan, Fezziwig, Cratchit family** — each is a functional foil/mirror; none floats.

## Pass 7 — POV Distribution / Perspective

Single consistent *intrusive first-person narrator* over an omniscient field ("I am standing in the spirit at your elbow"; "What would I not have given to be one of them!"). The narrator alternately feigns limited knowledge ("partners for I don't know how many years") and reports private interiors (the clerk's failed imagination; Bob as "Tim's blood horse"). This is a stable rhetorical stance established in line 1, not a slip. **Pass clean.**

## Pass 8 — Reveal Timeline / Dropped Threads / Fairness

- **Central reveal** (the unnamed corpse = Scrooge) is **fairly clued**: his office occupied by a stranger, his corner taken, his own goods (bed-curtains, shirt) sold by the plunderers, Scrooge's dawning "the case of this unhappy man might be my own." Withholding is legitimate.
- **Threads all closed** except one intentional non-payoff (Marley remains damned — see SP table).

## Pass 10 — Entity + Timeline

- Wages consistent: "fifteen shillings a week" (I) = "fifteen 'Bob' a-week" (III).
- Kinship consistent: Fan → one child → Fred = Scrooge's nephew.
- Marley: "dead these seven years… this very night" ↔ "seven Christmas Eves ago." Consistent.
- **One hard contradiction in the visitation schedule — see F-TIMELINE-01 / CF-01.**

---

## Findings

```apodictic.finding.v1
id: F-TIMELINE-01
evidence_refs:
  - Stave I, Marley: "Expect the first to-morrow, when the bell tolls One."
  - Stave I, Marley: "Expect the second on the next night at the same hour. The third upon the next night when the last stroke of Twelve has ceased to vibrate."
  - Stave III: Ghost of Christmas Present: "My life upon this globe, is very brief… It ends to-night… To-night at midnight." (bell then strikes twelve; the third Phantom appears immediately)
  - Stave V: "I don't know how long I've been among the Spirits." / "The Spirits have done it all in one night." / boy: "Why, CHRISTMAS DAY."
mechanism: >
  Marley's instructions establish an explicit three-consecutive-nights cadence
  ("the next night… the next night"). The plot then executes all three visits
  inside a single compressed night and lands on Christmas morning, which Scrooge
  himself confirms ("all in one night"). A reader tracking the stated schedule
  hits a direct contradiction: the setup promises three nights, the payoff
  delivers one. The text gestures at supernatural time-compression ("the
  Christmas Holidays appeared to be condensed into the space of time they passed
  together") but never revises Marley's literal "next night… next night," so the
  hand-wave covers duration, not the day-count promise.
severity: Should-Fix
```

```apodictic.finding.v1
id: F-STRUCT-02
evidence_refs:
  - Stave III: "A place where Miners live, who labour in the bowels of the earth"
  - Stave III: "there stood a solitary lighthouse… two men who watched the light"
  - Stave III: "they lighted on a ship… every man among them hummed a Christmas tune"
  - Stave I (secondary): the phantoms in the air, incl. "one old ghost, in a white waistcoat, with a monstrous iron safe attached to its ankle"
mechanism: >
  The miners / lighthouse / ship triptych in Stave III is thematically on-message
  (Christmas reaches every remote place) but is structurally detachable: it has no
  causal link to Scrooge's reformation, introduces no entity that recurs, and can
  be excised without disturbing any downstream beat. It reads as a set-piece
  digression off the beat spine. The Stave I white-waistcoat/iron-safe ghost is a
  smaller instance of the same pattern — a vivid orphan that never returns.
  Flagged as spine-hygiene, not error; both are intentional atmosphere.
severity: Could-Fix
```

---

## Continuity Bible

| ID | Issue | Refs | Note |
|----|-------|------|------|
| CF-01 | Visitation cadence: three nights promised, one night delivered | Stave I (Marley) vs. Stave III (ends "to-night at midnight") vs. Stave V ("all in one night") | Cross-refs F-TIMELINE-01. Single most defensible continuity flag in the manuscript. |
| CF-02 | Bedtime hour asserted retroactively | Stave I (falls asleep "upon the instant," hour unstated) vs. Stave II ("It was past two when he went to bed") | Non-contradictory; retrospective specification. No action needed. |

## Setup → Payoff

| ID | Setup | Payoff | Status |
|----|-------|--------|--------|
| SP-01 | Marley's face in the knocker (I) | "I shall love it, as long as I live!" (V) | Paid |
| SP-02 | Clerk's starved fire / coal-box (I) | "buy another coal-scuttle" (V) | Paid |
| SP-03 | "decrease the surplus population" (I) | Ghost quotes it back over Tiny Tim (III) | Paid |
| SP-04 | "Are there no prisons?… workhouses?" (I) | Ghost turns Scrooge's words on him (III) | Paid |
| SP-05 | Fred's standing annual invitation (I/III) | Scrooge attends the dinner (V) | Paid |
| SP-06 | Charity gentlemen rebuffed (I) | Scrooge whispers a large subscription (V) | Paid |
| SP-07 | Tiny Tim's crutch / "vacant seat" (III) | "Tiny Tim, who did NOT die" (V) | Paid |
| SP-08 | Plunderers sell an unnamed man's goods (IV) | Gravestone: the man is Scrooge (IV) | Paid, fairly clued |
| SP-09 | Marley: "you have yet a chance… of escaping my fate" (I) | Scrooge escapes it (IV/V) | Paid **for Scrooge only**; Marley's own damnation is left unresolved by design — intentional non-payoff, no fix required. |

---

RECOGNITION: yes — Charles Dickens, *A Christmas Carol* (1843).
