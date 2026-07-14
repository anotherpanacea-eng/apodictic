# APODICTIC Structural Diagnostic — Submission (untitled, ~850 words)

## Pass 0 — Reverse Outline (as-written beat list)

1. Dusk. Jonah sees signal lamp wink twice above flooded quarry; decides it's for him.
2. Exposition: he's come to sell the lock house; agent holds the key; sale completes "by noon tomorrow."
3. Office shuttered since pumps failed; no boat, no figure.
4. Climbs cinder road.
5. Door ajar; calls Clara's name (she vowed never to return).
6. Interior: warm signal lamp, oil can, shift ledgers, survey map with eastern shaft circled in blue.
7. Backstory: father died in that shaft per the company.
8. Clara appears; "You saw it too" / "The lamp was already dark."
9. Lamp now smoking/extinguished; ambiguity established.
10. Three knocks from beneath the floor (twice).
11. Pry open swollen trapdoor; ladder; drainage gallery.
12. Fresh boot marks; Jonah measures heel; Clara descends.
13. Timber door, company seal **cut**, new chain looped but unlocked.
14. Chamber: camp stool, tin dispatch box (from father's desk).
15. Contents: pay sheets, then letters reporting cracks in eastern retaining wall weeks before collapse.
16. Reveal: father reported danger; company continued the shift and scapegoated him.
17. A scrape beyond the chamber; the boot-mark maker does not approach.
18. Aside: Jonah's mailed letter hasn't reached the buyer / "the letter still lay unopened on the hall table."
19. Return to office at dawn.
20. Clara sets lamp in window; Jonah realizes **she** lit it.
21. Reconciliation beats; key laid beside lamp; they descend to telephone the inspector; house left unsold, lamp burning.

The spine is clean and legible: a competent one-night investigation with a document reveal and a sibling reconciliation. The load-bearing defects are all in the **causal attribution of the "presence"** and in **POV discipline**.

---

## Pass 2 / Pass 8 — Causal Chain & Fairness (primary defects)

```yaml
apodictic.finding.v1:
  id: F-P8-01
  title: The underground "presence" is planted three times and never attributed
  severity: Must-Fix
  evidence_refs:
    - "three measured knocks from somewhere under the floor"
    - "the knocks came again"
    - "Fresh boot marks stippled the mud. Jonah crouched over them, measuring the heel against his palm"
    - "A scrape sounded beyond the chamber... whoever had made the boot marks did not approach"
  mechanism: >
    Four independent cues assert a living agent underground during the scene:
    the knocks that summon the siblings down, the fresh boot marks, the measured
    heel (implying a person of specific size), and the retreating scrape. The
    story's only agency-reveal (Pass 5) assigns the lamp to Clara, who was above
    ground on the towpath. Nothing is offered for the subterranean cues. A
    complete manuscript owes the reader either an answer (father alive? the
    boot-mark maker who cut the seal?) or a deliberate, marked refusal. As
    written it reads as an unclosed thread rather than chosen ambiguity, and it
    is the engine that drives the descent — so its non-payoff is structural, not
    cosmetic.
```

```yaml
apodictic.finding.v1:
  id: F-P8-02
  title: Reveal ("Clara lit the lamp") does not reconcile with the on-page lamp state
  severity: Should-Fix
  evidence_refs:
    - "The signal lamp sat warm beside an oil can... Someone had lit it within the hour."
    - "'The lamp was already dark.'"
    - "the wick smoked under the chimney, and the office held the sharp smell of extinguished oil"
    - "she had lit it, not to summon him into danger, but to make certain he could not leave"
  mechanism: >
    Jonah enters to a lamp that is warm and recently lit, then — after Clara
    speaks — sees it smoking and extinguished. Jonah is alone in the room the
    whole interval, so no one extinguishes it on-page. Clara both denies lighting
    it ("already dark") and is later confirmed to have lit it. The denial can be
    read as self-protection, but the physical extinguishing event has no cause in
    the text. The reveal therefore lands as assertion, not as a click the reader
    can re-check against the earlier lamp beats. Either the extinguishing needs a
    seen cause or the "warm/lit within the hour" beat needs to be Clara's doing
    she can own.
```

```yaml
setup_payoff_ledger:
  - id: SP-01
    setup: "the old shift ledgers leaned together on a shelf"
    later: "Clara... [glanced] at the shelf where their father's ledgers should have been"
    payoff: NONE
    note: >
      Ledgers are shown present at beat 6, then registered as missing/expected-
      missing at beat 6-adjacent, then never referenced again; the dispatch box
      contains pay sheets and letters, not ledgers. Dropped object-thread.
    severity: Could-Fix
  - id: SP-02
    setup: "the company's seal... cut and looped a new chain through the handles without locking it"
    later: "boot marks / scrape"
    payoff: NONE
    note: >
      Someone forced entry and staged the chamber (camp stool, dispatch box).
      Feeds directly into F-P8-01; the stager is never identified.
    severity: Should-Fix
```

---

## Pass 7 — POV Distribution & Perspective Slips

Governing POV is **close third on Jonah** (his sensations, memory, inference). Three passages violate it:

```yaml
apodictic.finding.v1:
  id: F-P7-01
  title: Two head-hops into Clara's interiority inside a Jonah-anchored narration
  severity: Must-Fix
  evidence_refs:
    - "She wondered whether he had ever loved her at all."
    - "She wished he would ask her to come instead of ordering her to remain behind."
  mechanism: >
    Both sentences report Clara's private mental state, unavailable to the Jonah
    filter that governs every other interior beat. They are also thematically
    load-bearing (they carry the sibling-grievance subplot), so the slips are not
    incidental — the story tries to run its emotional B-plot through a POV it has
    otherwise closed off. Convert to observable behavior filtered through Jonah,
    or commit to a declared alternating/omniscient frame from beat 1.
```

```yaml
apodictic.finding.v1:
  id: F-P7-02
  title: Omniscient camera-cut breaks the fixed locale and the character filter
  severity: Should-Fix
  evidence_refs:
    - "Across town, the letter still lay unopened on the hall table."
  mechanism: >
    The narration leaves the quarry to report a fact no present character can
    perceive. Coming one clause after "he could only hope the sale could still be
    stopped," it also deflates that hope for the reader before the characters —
    puncturing the tension the surrounding paragraph is building.
```

---

## Pass 5 — Character Cards / Agency

- **Jonah Vale** — POV, reactive throughout: reads signals, climbs, pries, descends, reads documents. Wants: to sell and leave / (revised) to stop the sale. Agency is investigative but consistently *responding* to Clara's staging.
- **Clara** — the true prime mover (lit lamp; per SP-02 likely staged the chamber), but her agency is withheld until beat 20 and never reconciled with her vow "never to set foot there again" (she must have gone underground to stage the box, contradicting the vow and feeding F-P8-01/SP-02).

```yaml
apodictic.finding.v1:
  id: F-P5-01
  title: Clara's established constraint contradicts the agency the reveal assigns her
  severity: Should-Fix
  evidence_refs:
    - "Clara had promised never to set foot there again"
    - "a dry chamber, a camp stool, and a tin dispatch box"
    - "she had lit it... to make certain he could not leave without seeing"
  mechanism: >
    The staged chamber implies Clara descended and arranged it (or an unnamed
    third party did — see F-P8-01). Either reading strains: the first breaks her
    stated vow without acknowledgment; the second leaves the stager unaccounted.
    Her characterization ("older than at the funeral, less willing to forgive")
    is otherwise consistent and earned.
```

---

## Pass 10 — Entity & Timeline

Entities consistent: Jonah, Clara, father (foreman, dead ~ the collapse), the company, estate agent, buyer, inspector. Chronology (dusk → office → descent → "pale strip of morning") is a single continuous night and holds.

```yaml
continuity_bible:
  - id: CF-01
    entity: "the sale / the letter"
    conflict: >
      "come home to sell the lock house," agent holds the key, sale completes
      "by noon tomorrow" — yet "The letter Jonah had mailed before leaving the
      city had not yet reached the buyer; he could only hope the sale could still
      be stopped." A posted letter cannot plausibly reach a buyer and reverse a
      conveyance inside the sub-24-hour window, and it presupposes Jonah already
      wanted to stop the sale before any of tonight's revelations.
    severity: Should-Fix
  - id: CF-02
    entity: "signal lamp"
    conflict: >
      Warm/recently-lit on entry → "already dark" (Clara) → smoking/extinguished
      (Jonah looks back) → burning again at the close ("the old signal burning
      behind them"). The relighting at the end is unshown. See F-P8-02.
    severity: Could-Fix
```

---

## Synthesis

The manuscript is structurally sound at the spine level — a single-night descent, a document reveal that recontextualizes the father's death, and a reconciliation payoff (key laid beside lamp) all land in order. Two defect clusters are load-bearing:

1. **The unattributed presence (F-P8-01, SP-02, F-P5-01).** The knocks, boot marks, measured heel, and scrape are the causal trigger for the entire descent, yet the story's only reveal explains the *lamp*, not the *person underground*. This is the single Must-Fix that most affects reader trust: the mechanism that opens the trapdoor is the one thing left dark.

2. **POV leakage (F-P7-01 Must-Fix, F-P7-02).** A Jonah-anchored narration twice reports Clara's inner life and once cuts across town. Because the sibling grievance is routed through exactly those slips, tightening POV will force a decision about how the B-plot is carried.

Secondary: the lamp-state chain (F-P8-02/CF-02), the dropped ledgers (SP-01), and the sale/letter logistics (CF-01).

Nothing here required inventing content; every finding is anchored to quoted text, and no resolution is proposed for the open threads — only their openness is diagnosed.

RECOGNITION: No — I did not recognize this as a known published author or title; it presents as an original untitled submission.
