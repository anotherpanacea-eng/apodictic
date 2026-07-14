# APODICTIC Structural Diagnostic

Complete short work, ~620 words, single POV, five scene-breaks. Treated as a finished manuscript.

---

## Pass 0 — Reverse Outline

1. Clock stops; Nessa finds a broken brass tooth; the bridge can't be timed. (setup + inciting)
2. Stakes fixed: inspector in four days, else the ferry contract and Bridge Street's winter trade are lost.
3. Hidden initials **A.R.** on the wheel → not her father's mark but Abel Rusk's, whom her father drove out.
4. Rusk visit: father sabotaged the wheel to seize the contract; Rusk has the pattern but shaky hands; needs *bell bronze*.
5. Only source is the cracked chapel bell; senior churchwarden refuses metal "for a machine built by a Rook."
6. Nessa reframes authorship (Rusk built it, father only "put his name on the case"); warden reads old minutes, relents on condition Rusk's name is restored.
7. Low tide: she cuts metal from the bell's split lip.
8. Casting before dawn; new wheel filed true; escapement installed; clock runs, bridge rises.
9. Inspector renews the contract.
10. New plate — MAKER Rusk / RESTORER Rook; bell metal now "sounds in every measured stroke."

## Pass 1 — Premise / Container

A tight restitution parable: a mechanical problem (broken escape wheel) is solved only by solving a *moral* problem (restoring a wronged maker's name). Container is well-sealed — the object that fails (clock), the object that repairs it (bell), and the injustice being corrected all converge on the same closing image. No structural sag.

## Pass 2 — Beat Map / Causal Chain / Orphan Scenes

Causal spine is clean — every beat is joined by **therefore / but**, not **and then**:

> tooth breaks → *therefore* wheel removed → *but* initials expose history → *therefore* seek Rusk → *but* needs rare bronze → *therefore* seek bell → *but* warden refuses → *therefore* reframe authorship → *therefore* cast → *therefore* clock runs → *therefore* contract saved → *therefore* name restored.

**No orphan scenes.** Each of the five sections both consumes the prior deliverable and produces the next obstacle. The physical quest and the reputational quest are braided rather than sequential — structurally efficient.

## Pass 5 — Character Cards / Agency

- **Nessa Rook** — protagonist, high agency throughout; every plot advance is her decision (goes to Rusk, argues the warden, cuts the bell, files the teeth, changes the plate). Notably she also authors her own moral turn: siding against her dead father.
- **Abel Rusk** — wronged maker; agency deliberately limited ("hands too unsteady now"), which correctly routes action through Nessa while keeping him causally necessary (pattern, alloy knowledge, directs the pour).
- **Father Rook** (deceased) — antagonist-by-backstory; never on-page, functions as the injustice to be corrected.
- **Senior churchwarden** — gatekeeper; single reversal, adequately motivated by the minutes (see F-P8-01).
- **Foundry master / inspector** — functional agents, appropriately flat.

No agency vacuum. Protagonist earns the resolution.

## Pass 7 — POV Distribution / Perspective Slips

Third-person limited, anchored to Nessa, 100% of scenes. No head-hops. The closing sentence — *"Rusk listened from the square until the last chime faded, then took Nessa's arm"* — stays external/observable from Nessa's vantage; not a slip. The single lyric flourish (*"its missing metal sounded in every measured stroke"*) is narratorial coloring, not an interiority breach. **Clean pass.**

## Pass 8 — Reveal Timeline / Dropped Threads / Fairness

Reveals are ordered and fair-ish: the initials (physical, verifiable) precede and license the accusation; the chronic *"shuddering"* clock is a genuine plant that retroactively corroborates a thin-filed wheel. No dropped threads — the rivalry backstory, the alloy requirement, and the contract stake all pay off. See findings below for the two soft spots (unverified sabotage claim; warden authority).

## Pass 10 — Entity + Timeline

**Entities:** Nessa Rook, Abel Rusk, Father Rook (dec.), council inspector, senior churchwarden, foundry master, chapel (tri-parish). All internally consistent; no naming drift.

**Timeline:** Day 1 morning clock stops → Rusk → "a day finding the senior churchwarden," reversal "by evening" → low tide → foundry "before dawn" → install → "the fourth morning" inspector. Compresses plausibly, but see F-P10-01 for a count mismatch.

---

## Findings

```apodictic.finding.v1
id: F-P8-01
origin: Pass 8 (fairness)
title: Load-bearing accusation rests on an interested party's uncorroborated word
severity: Could-Fix
evidence_refs:
  - "Your father filed that wheel thin ... He wanted the council to replace my mechanism with his."
  - "not her father's mark but those of Abel Rusk"
  - "the churchwarden had read the old council minutes and changed his answer"
  - "For the first time in years, the minute hand crossed twelve without shuddering"
mechanism: >
  The story establishes two distinct claims. AUTHORSHIP (Rusk built the
  mechanism; the father only put his name on the case) is proven independently
  by the hidden A.R. initials — solid, and it alone justifies the restored
  plate. SABOTAGE (the father deliberately filed the wheel thin) is asserted
  only by Rusk, the aggrieved party, and is never physically checked on-page
  even though the damaged wheel is in hand and repeatedly examined. The
  "shuddering" plant and the council minutes gesture at corroboration but
  actually confirm authorship/expulsion, not intentional filing. The ending
  reads as full moral vindication of the sabotage charge, so the weakest
  evidentiary link carries the heaviest thematic freight. A single verifying
  beat (e.g., the warden or foundry master remarking the wheel's teeth are
  visibly thinned below gauge) would close the gap without new plot.
```

```apodictic.finding.v1
id: F-P5-02
origin: Pass 5 / Pass 2 (agency-of-gatekeeper)
title: Churchwarden's authority to alienate tri-parish property is under-established
severity: Could-Fix
evidence_refs:
  - "The chapel belonged to three parishes and to none of them."
  - "the senior churchwarden, who refused to surrender even a broken bell"
  - "He gave her a written order for one handspan of bronze"
mechanism: >
  The text foregrounds that the chapel — and thus the bell — is jointly owned
  by three parishes and effectively orphaned. A lone "senior churchwarden"
  then unilaterally issues a binding written order to remove bell metal. The
  reversal is emotionally motivated (the minutes), but the *jurisdictional*
  motivation is left implicit: one warden overriding a tri-parish claim reads
  as slightly frictionless given the story itself raised the ownership
  complication. Either the tri-parish detail is doing less work than it seems
  and could be trimmed, or the warden needs one clause locating his authority.
```

```apodictic.finding.v1
id: F-P10-01
origin: Pass 10 (timeline)
title: Deadline count mismatch — "four days" vs "the fourth morning"
severity: Could-Fix
evidence_refs:
  - "The council inspector was due in four days."
  - "The inspector arrived on the fourth morning."
mechanism: >
  Beat 1 fixes the deadline on the stopping morning ("due in four days"). If
  that morning is counted as day one, the fourth morning is only three days
  later; if the deadline means four days *after* day one, the inspector should
  arrive on the fifth morning. The elapsed action (Rusk day, a full day
  finding the warden, an overnight cast) fits either reading, so the story
  survives, but the two phrasings are not strictly reconcilable. Pick one
  convention.
```

---

## Continuity Bible / Setup–Payoff Artifacts

| ID | Setup (ref) | Payoff (ref) | Status |
|----|-------------|--------------|--------|
| SP-01 | "a tooth of brass ... broken from the escapement" | "carried the finished escapement to the bridge tower ... The old clock accepted it" | Paid |
| SP-02 | "the ferry contract would go upriver ... lose their winter trade" | "renewed the ferry contract before lunch" | Paid |
| SP-03 | initials "A.R. ... those of Abel Rusk" | "ABEL RUSK, MAKER; NESSA ROOK, RESTORER" | Paid |
| SP-04 | "The alloy required bell bronze ... The foundry had no bell bronze" → chapel bell | "cut the metal from the bell's split lip" → cast wheel "rough but true" | Paid |
| SP-05 | "provided Rusk's name was restored to the clock" | new plate restoring Rusk's name | Paid |
| SP-06 | "The fragment rang once when it fell, a small clear note" | "its missing metal sounded in every measured stroke above Bridge Street" | Paid (thematic capstone) |
| CF-01 | "filed that wheel thin" (Rusk, uncorroborated) | never physically verified on-page | Open — see F-P8-01 |
| CF-02 | "belonged to three parishes and to none of them" | single warden authorizes removal | Open — see F-P5-02 |
| CF-03 | "due in four days" | "the fourth morning" | Open — see F-P10-01 |

---

## Synthesis

This is a structurally sound, unusually well-sealed short work. The causal chain has no gaps or orphan scenes, POV is disciplined, protagonist agency is high and morally active, and the setup/payoff ledger is nearly complete — including a genuinely earned thematic capstone (SP-06) where the sacrificed bell "sounds" through the clock it repaired. There are **no Must-Fix or Should-Fix findings.**

The three Could-Fix items are all small and non-blocking, and two of them (F-P8-01, F-P5-02) share a single root: the story *raises* two complications — the sabotage charge's proof and the bell's contested ownership — more prominently than it *resolves* them, leaning on the reader's goodwill and one convenient off-page document (the council minutes) to close both. Tightening those two seams, plus reconciling the day-count, would leave the piece airtight. None of this requires added scenes or characters — each fix is a clause, not a beat.

RECOGNITION: No — I did not recognize this as a specific published author or title.
