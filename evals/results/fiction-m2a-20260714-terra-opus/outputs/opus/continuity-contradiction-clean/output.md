# APODICTIC Structural Diagnostic

## Pass 0 — Reverse Outline

- **Ch1** — Miriam returns to Bellweather (Oct); all house clocks stopped at 4:11; mother's will splits house between Miriam & Edmund with an orchard-retention condition; syndicate offers 2× value. *(Setup / hook)*
- **Ch2** — Breakfast: Edmund pushes sale-after-harvest; Miriam stalls. *(Positions established)*
- **Ch3** — Household accounts: marriage 1832 → "Spring, 1838" page paying surveyor Pell; a leaf cut out, dust line of a vanished enclosure; Miriam's memory of Edmund's 1838 broken wrist / left-hand writing / pear-stealing. *(First clue + planted memory)*
- **Ch4** — Mrs. Pell: railway would drain tenant wells; Pell proved it, was bought off, gave mother a copy; clocks encode the bearing 4°11′ W. *(Clue decoded)*
- **Ch5** — Sighting from west-parlor window points to the icehouse, not the orchard; door freshly scraped, pale square on floor, mortar dust on Edmund's boots. *(Clue leads to site + Edmund clue)*
- **Ch6** — Edmund confesses: syndicate paid his debts; he took Pell's copy but hasn't delivered it; produces the enclosure; states the will condition was mother's device to let Miriam catch him. *(Reveal / confession)*
- **Ch7** — Miriam writes tenants + county engineer, re-dates the proof (1838, six years after 1832 marriage); syndicate refused; wells preserved. *(Resolution)*

**Causal chain (Pass 2):** clocks → bearing → icehouse → survey → refusal → wells saved. The chain is unbroken; **no orphan scenes.** Every chapter delivers a distinct causal beat. Structurally this is a clean, tightly-wound eight-thousand-word detective mechanism.

## Pass 5 — Character / Agency
- **Miriam** — full active agent; drives every discovery. Strong.
- **Edmund** — antagonist by weakness; his agency is real (theft, concealment) but resolves through easy confession (he "had not yet delivered it").
- **Mother** — posthumous prime mover; her agency is the plot's engine (condition + clocks).
- **Mrs. Pell** — pure informant.
No agency vacuum. Antagonist resolution is low-friction but acceptable at this length.

## Pass 7 — POV
Consistent close third on Miriam throughout. Ch5's observation of Edmund's boot-dust and the scraped lock is available to Miriam. **No perspective slips detected.**

## Pass 8 / Pass 10 — Reveals, Threads, Timeline
Core fair-play chain (clock→bearing→site; cut leaf→produced enclosure; boot dust→prior entry) is planted and paid off cleanly. The material problems are all in the **date/age substructure** and two **unfired plants**, below.

---

## Findings

```yaml
apodictic.finding.v1:
  id: F-P10-01
  origin: Pass 10 (timeline)
  title: No single present-year reconciles Miriam's 1832 marriage, her age 36, and Edmund as a schoolboy in 1838
  evidence_refs:
    - "Ch2: 'At thirty-six, Miriam...' / 'her brother Edmund was two years younger'"
    - "Ch3: 'household accounts beginning with her marriage in 1832' / 'a page headed Spring, 1838'"
    - "Ch3: Edmund 'had come down from school with a broken wrist... learning to write with his left hand and stealing pears'"
    - "Ch7: 'Pell's survey in the spring of 1838, six years after her marriage in 1832'"
  mechanism: >
    Let P be the story's present year. Miriam is 36 (born P-36) and married in
    1832, so her age at marriage is 1868-P; a plausible marriage age (>=16)
    forces P <= 1852. Edmund is two years younger (born P-34) and is a schoolboy
    breaking his wrist in spring 1838 with distinctly boyish behavior; a
    schoolboy age (<=18) forces P >= 1854. The two constraints do not overlap.
    The only way to close the gap is to read "school" as university and Edmund
    as ~21 in 1838 (P ~1850-1852), which the childish detailing (left-hand
    penmanship practice, unripe-pear theft) actively resists. The story stakes
    its climax on Miriam "dating her account carefully," so an underlying
    date/age impossibility undercuts the very virtue the ending celebrates.
  severity: Should-Fix
```

```yaml
apodictic.finding.v1:
  id: F-P8-01
  origin: Pass 8 (setup/payoff)
  title: Edmund's left-handed penmanship is planted beside the "own hand" will condition but never fires
  evidence_refs:
    - "Ch1: mother 'had written the condition in her own hand beneath the will'"
    - "Ch3: Edmund 'spent April learning to write with his left hand'"
  mechanism: >
    The manuscript twice foregrounds handwriting: the will's authenticating
    "own hand" and Edmund's acquired left-handed script. Placed this close, the
    detail promises a payoff (a forged codicil, a handwriting-based catch, a
    signature tell). None arrives; Edmund is caught by boot-dust and confession
    instead. The planted skill is left inert, reading either as a misdirect the
    text forgot to resolve or as decoration masquerading as a clue.
  severity: Could-Fix
```

```yaml
apodictic.finding.v1:
  id: F-P10-02
  origin: Pass 10 (entity/object)
  title: The "something heavy" that left the pale floor-square is never matched to a recovered object
  evidence_refs:
    - "Ch3: 'a folded enclosure had rested for years' (dust line)"
    - "Ch5: 'the brick floor showed a pale square where something heavy had recently stood'"
    - "Ch6: Edmund 'drew the missing enclosure' (a folded paper) / 'sat on the empty ice chest'"
  mechanism: >
    The icehouse pale square denotes a recently-removed HEAVY object, but the
    only item recovered from Edmund is a folded paper enclosure, and the ice
    chest is still present (he sits on it). What heavy thing stood on that
    square, who moved it, and where it went are left unaccounted, so a
    deliberately weighted physical clue dangles without referent.
  severity: Could-Fix
```

```yaml
apodictic.finding.v1:
  id: F-P1-01
  origin: Pass 1 / Pass 0 (redundancy)
  title: Ch7 re-explains arithmetic and kinship the reader already holds
  evidence_refs:
    - "Ch2: 'her brother Edmund was two years younger'"
    - "Ch7: 'Edmund, her younger by two years'"
    - "Ch7: 'six years after her marriage in 1832' (restating Ch3's 1832->1838)"
  mechanism: >
    The closing chapter re-states the sibling age gap (third instance) and
    re-performs the 1832+6=1838 computation already made explicit in Ch3. In an
    otherwise economical text this hand-holding flattens the resolution beat
    into exposition and signals authorial anxiety that the puzzle won't land.
  severity: Could-Fix
```

---

## Continuity-Bible / Setup-Payoff Artifacts

| ID | Item | Set | Paid | Status |
|----|------|-----|------|--------|
| SP-01 | Clocks stopped at 4:11 → bearing 4°11′ W | Ch1 | Ch4/Ch5 | ✅ Fair, clean |
| SP-02 | Cut-out leaf / dust line of enclosure | Ch3 | Ch6 (produced) | ✅ Paid |
| SP-03 | Mortar dust on Edmund's boots | Ch5 | Ch6 (prior entry) | ✅ Paid |
| SP-04 | Edmund's left-handed writing / "own hand" will | Ch1, Ch3 | — | ❌ Unfired (F-P8-01) |
| SP-05 | "Something heavy" pale floor-square | Ch5 | — | ❌ Unmatched (F-P10-02) |
| CF-01 | Orchard fruit: "stealing pears" (Ch3) vs "last apples were stored... west orchard" (Ch7) | — | — | ⚠️ Ch3 never fixes the pears to the *west* orchard, so no hard contradiction, but the fruit-type drift invites a reader double-take. Could-Fix. |

---

## Synthesis

This is a compact, mechanically sound detective miniature: a single POV, a strictly causal beat-chain with no orphan scenes, and three properly planted-and-paid clues (clock-bearing, cut leaf, boot-dust). Its structural weakness is not architecture but **numerical/temporal underpinning**, which matters unusually much because the story's thematic payoff *is* the reliability of a preserved date and direction ("the clocks had preserved not an hour but a direction"). The one Should-Fix (**F-P10-01**) is a strained-to-broken date/age lattice: a 1832 adult marriage, a 36-year-old Miriam, and a schoolboy Edmund in 1838 cannot comfortably coexist. Secondary Could-Fixes are two clues that promise more than they pay (left-handed penmanship, the "heavy" floor-mark) and closing-chapter redundancy that re-teaches arithmetic already earned. Fix the date lattice first — anchor a present year and back-solve the two birth years — since the ending explicitly asks the reader to trust Miriam's careful dating.

RECOGNITION: No — I did not recognize this as a specific published author or title; it reads as an original period detective pastiche.
