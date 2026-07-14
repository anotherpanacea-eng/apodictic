# APODICTIC Structural Diagnostic

Manuscript treated as COMPLETE. ~700 words, 6 scenes (section-break delimited). Diagnosis confined to text inside `<submission>`.

---

## Pass 0 — Reverse Outline

| # | Scene | Function on spine |
|---|---|---|
| S1 | Workshop | Inciting break; stakes (inspector in 4 days, ferry contract, Bridge St. trade); discovery of hidden initials **A.R.** = Abel Rusk |
| S2 | Rusk's cottage | Backstory reveal (father filed wheel thin to steal credit); pattern obtained; new requirement — **bell bronze** |
| S3 | Chapel / churchwarden | Obstacle → reversal via council minutes; conditional grant of bronze (Rusk's name restored); bell fragment cut at low tide |
| S4 | Puppet theatre / market square | Nessa repairs a music box; receives a **blue ribbon** |
| S5 | Foundry | Pour, cast, file, install escapement; clock runs true |
| S6 | Inspector / tower | Contract renewed; nameplate replaced (RUSK MAKER / ROOK RESTORER); thematic close |

## Pass 1 — Premise / Promise

Promise made in S1–S2: a technical rescue that is secretly an act of *restorative justice* (undoing the father's theft). The title-mechanism (clock) and the moral mechanism (credit) are the same object — an elegant structural coupling. The promise is fully paid: the nameplate and the "measured stroke" carry both meanings. Spine is coherent and closed.

## Pass 2 — Beat Map / Causal Chain / Orphan Scenes

Causal chain (each link forced by the prior):
`broken tooth → need new wheel → need pattern (Rusk) → need bell bronze → need churchwarden's consent → cut fragment → cast wheel → install → pass inspection → restore name`

Every scene sits on this chain **except S4 (puppet theatre)**. Removing S4 breaks nothing in the plot: the bronze is already "under her arm" when she enters and still under her arm when she leaves; no obstacle, resource, information, or relationship changes state relative to the clock spine.

```
apodictic.finding.v1
id: F-P2-01
title: Orphan scene — puppet theatre / music-box repair sits off the causal chain
evidence_refs:
  - "Nessa found a traveling puppet theatre performing beneath the market awning"
  - "Nessa bent the catch with her pocket pliers, and the little cylinder completed its song"
  - "watched the company pack its painted moon, and continued to the foundry"
mechanism: S4 is thematically load-bearing (a second broken mechanism restored to true, mirroring the clock and foreshadowing the "completed song" of the final chime) but causally inert. It gates nothing and is gated by nothing; the wrapped bronze enters and exits unchanged. In a manuscript this tight, the single off-spine scene reads as a resonance interlude rather than a beat, and its only tangible output (the ribbon) is not reclaimed elsewhere. Either braid an outcome from S4 back into the spine (e.g., the repair earns something later needed) or accept it explicitly as a thematic coda and cut the vestigial props.
severity: Should-Fix
```

## Pass 5 — Character Cards / Agency

- **Nessa Rook** — protagonist; agency HIGH. Drives every beat (removes wheel, seeks Rusk, converts churchwarden, cuts metal, casts, files, installs, re-plates). Arc: inheritor of a stolen name → restorer of a true one. Fully realized for the length.
- **Abel Rusk** — agency MODERATE→LOW by design. Hands "too unsteady," so he supplies knowledge/pattern and is *acted for* rather than acting; the final "took Nessa's arm" completes his return. Passivity is intentional, not a defect.
- **Churchwarden** — functional obstacle; the one *reversal* engine (changes answer via minutes). Adequate.
- **Foundry master** — pure function (the pour). Fine.
- **Puppeteer** — exists only to service the orphan scene (see F-P2-01).
- **Father (dead)** — off-page antagonist; establishes the moral debt.

No agency defects rising to a finding.

## Pass 7 — POV Distribution / Perspective Slips

Uniform close-third limited on Nessa across all 6 scenes. No head-hops. Only stylistic risk is the final free-indirect flourish ("its missing metal sounded in every measured stroke") — this stays inside Nessa's perception and reads as intended lyricism, not a slip. **No findings.**

## Pass 8 — Reveal Timeline / Dropped Threads / Fairness

Reveals, in order — all planted before payoff:
- **R1** initials A.R. → identified next scene as Rusk. Fair.
- **R2** father sabotaged the wheel / stole credit → delivered in S2.
- **R3** the clock was Rusk's work → weaponized in S3 and corroborated by council minutes. Fair.

```
apodictic.finding.v1
id: F-P8-01
title: Dropped thread — blue ribbon planted, never reclaimed
evidence_refs:
  - "The puppeteer offered her a blue ribbon in payment. She tied it around her wrist"
severity: Could-Fix
mechanism: The ribbon is foregrounded (accepted, tied on, worn onward) with the ceremony of a Chekhov object, then never referenced through S5–S6. It creates a small unpaid setup — the reader who logs it waits for it at the tower and gets nothing. Either let it recur at the naming/close (a visible token of the one favor Nessa did for herself) or demote it so it stops signaling a payoff. Tightly coupled to F-P2-01.
```

```
apodictic.finding.v1
id: F-P8-02
title: Reveal fairness — the "filed thin" accusation is single-sourced
evidence_refs:
  - "\"Your father filed that wheel thin,\" he said... \"He wanted the council to replace my mechanism with his.\""
  - "By evening the churchwarden had read the old council minutes and changed his answer."
severity: Could-Fix
mechanism: The moral pivot — that the father actively SABOTAGED, not merely renamed — rests solely on the testimony of the wronged party, Rusk. The council minutes independently corroborate only AUTHORSHIP ("the machine was built by Rusk"), not the filing. Nessa handles the physical wheel twice and could confirm or deny the thinned tooth from the object itself; the text never lets the evidence speak. As written the reader must take the antagonist's crime on the beneficiary's word. A one-clause physical confirmation (Nessa reading the file-marks) would move this from asserted to demonstrated and close the fairness gap.
```

No other dropped threads: bell bronze (set S2 / paid S3–S5), churchwarden's naming condition (set S3 / paid S6), cracked bell's silence (set S2 / paid S6) all resolve.

## Pass 10 — Entity + Timeline

Entities consistent: Rook/Rusk (A.R.), bell = three parishes, one handspan cut from "split lip," 20 years since Rusk driven out, 40 years bell silent. No contradictions.

```
apodictic.finding.v1
id: F-P10-01
title: Deadline arithmetic — "in four days" vs. "the fourth morning"
evidence_refs:
  - "The council inspector was due in four days."
  - "The inspector arrived on the fourth morning."
severity: Could-Fix
mechanism: Day-1 is "the morning the bridge clock stopped." An inspector "due in four days" from Day-1 lands on Day-5; "arrived on the fourth morning" lands on Day-4. The gap is reconcilable under inclusive counting, but the two phrasings invite the reader to check and find a one-day wobble. The intervening durations ("spent a day finding the... churchwarden," foundry "before dawn") leave ample slack, so this is cosmetic — normalize one phrase to the other.
```

### Continuity-bible / Setup-Payoff artifact rows

| ID | Item | Set | Paid | State |
|---|---|---|---|---|
| SP-01 | Bell bronze required | S2 | S3–S5 | ✅ paid |
| SP-02 | Churchwarden's condition: restore Rusk's name | S3 | S6 nameplate | ✅ paid |
| SP-03 | Cracked bell silent 40 yrs; "rang once when it fell" | S2/S3 | S6 "sounded in every measured stroke" | ✅ paid (thematic apex) |
| SP-04 | Blue ribbon | S4 | — | ⚠️ unpaid → F-P8-01 |
| SP-05 | Father's sabotage of the wheel | S2 | asserted only | ⚠️ single-sourced → F-P8-02 |
| CF-01 | Deadline count | S1 | S6 | ⚠️ 4-days/4th-morning → F-P10-01 |

---

## Synthesis

Structurally this is a near-clean, fully-closed short: one causal spine, one POV, a title-object that doubles as the moral object, and three planted reveals that all pay off — the cracked-bell metal "sounding in every measured stroke" is a genuine convergence of plot and theme. It needs no rebuild.

The material work is one decision: **S4 (the puppet theatre) is the only scene off the causal chain, and it drags an unpaid prop (the ribbon) behind it** (F-P2-01 + F-P8-01). Resolve these together — either braid S4's outcome into the spine or commit to it as an explicit thematic mirror and retire the ribbon. Secondary, low-cost polish: let the wheel's file-marks physically corroborate the father's sabotage instead of leaving it on Rusk's word (F-P8-02), and reconcile the deadline phrasing (F-P10-01). Nothing rises to Must-Fix.

RECOGNITION: no — I did not recognize this as a specific published work or known author; it reads as an original submission.
