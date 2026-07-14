# APODICTIC Structural Diagnostic — "The Schoolhouse on Saint Brannoc" (working title from content)

## Pass 0 — Reverse Outline

| # | Scene (break-delimited) | Function | Turn |
|---|---|---|---|
| S1 | Ferry arrival; Pell tags furniture; Elin signs inventory, not sale order | Establish stakes (auction in 12h), protagonist hesitation | Withholds signature |
| S2 | Mara hands over iron ring + special brass key from mother | Plants the key + a sworn obligation | Key becomes a charged object |
| S3 | Cleaning; Tomas Bell arrives; talk of teaching/certification | Human stake (pupils); plants Tomas's name in cupboard | Tomas assumes agreement |
| S4 | Rain seals them in; key catches in desk drawer; mantel cabinet spotted; flue cleared; walks Tomas home | Delay/tension; misdirect (drawer) → redirect (cabinet) | Discovery deferred |
| S5 | Returns after dark; cabinet opens; tuning fork, photos, note; list ending in Elin's own name | Reveal / thematic core | Obligation becomes choice |
| S6 | Auction morning; tears sale order; reopens school; rings handbell | Resolution / decision enacted | Turn completed |

**Spine:** Return-to-sell → key-borne inheritance → discovery reframes duty as desire → refusal of sale. Clean, closed, single-protagonist arc.

## Pass 1 / Pass 2 — Causal Chain & Orphan Scenes

Causal linkage is tight; every scene feeds the decision engine (each hesitation/discovery raises the cost of signing). **No orphan scenes.** The flue-clearing in S4 (`"The gale pressed smoke down the chimney"`) is a deliberate delay device, not an orphan — it defers the cabinet reveal to S5 and is diegetically motivated by the gale.

## Pass 5 — Character Cards / Agency

- **Elin** — active protagonist; want (resolve estate cleanly / leave) vs. need (belong / continue mother's work). Genuine agency.
- **Mara** — catalyst; withholds (`"would say nothing more"`).
- **Pell** — soft antagonist / opposing value (`"You can't run a school on memories"`).
- **Tomas** — minor agency (advocates for the school).

## Pass 7 — POV

Third-person limited, anchored to Elin throughout. **No slips.** `"Elin heard herself explain"` and `"Tomas was smiling as if she had already agreed"` both stay inside her observational frame.

## Pass 8 / Pass 10 — Reveals, Dropped Threads, Timeline, Entities

Entity set consistent (Elin, Mara, mother [dec.], Pell, Tomas [14], sisters, brass key, iron ring, mantel cabinet, desk, tuning fork, note, handbell). No name/attribute contradictions.

---

## Findings

```yaml
apodictic.finding.v1:
  id: F-P8-01
  title: Locked desk drawer is a planted Chekhov object with no payoff
  evidence_refs:
    - "Every drawer opened except a narrow one above the kneehole."
    - "the brass key entered halfway before catching"
    - "Elin nearly forced it. Instead she withdrew it and noticed a tiny cabinet..."
  mechanism: >
    The narrow desk drawer is explicitly locked and the special key is tested
    against it and fails, which foregrounds the drawer as a question the reader
    files for later. The narrative then satisfies the key on the mantel cabinet
    instead and never returns to the drawer. The result is an open loop: a
    deliberately sealed container, emphasized, left unopened and unremarked. A
    reader tracking the key's purpose expects the drawer resolved or dismissed.
  severity: Should-Fix
```

```yaml
apodictic.finding.v1:
  id: F-P10-01
  title: "Twelve hours before the auction" contradicts the depicted elapsed time
  evidence_refs:
    - "with one suitcase and twelve hours before the auction"
    - "appeared at noon carrying a basket of oatcakes"
    - "Rain arrived before evening"
    - "She returned alone after dark."
    - "At nine the next morning, Mr. Pell arranged his catalogues"
  mechanism: >
    The auction lands "at nine the next morning." The action spans a full
    working day (room-to-room clearing), a noon visit, an evening of rain, a
    return "after dark," and an overnight — comfortably 18-24 hours from any
    plausible arrival. The stated "twelve hours" understates this and cannot be
    reconciled with the timeline unless the ferry lands near 9 p.m., which the
    daytime labor and the noon visit rule out.
  severity: Should-Fix
```

```yaml
apodictic.finding.v1:
  id: F-P8-02
  title: Tuning fork is an orphan object inside the reveal cache
  evidence_refs:
    - "Inside lay her mother's tuning fork, a packet of school photographs, and a note addressed to Elin."
  mechanism: >
    The tuning fork is named with specificity alongside two objects that do
    work (photographs = the pencilled-cupboard/pupil motif; note = the thematic
    payload). It carries no plot, callback, or explicit thematic use and is
    never touched again. It reads as texture but its specificity invites a
    payoff the text does not supply. Lower stakes than F-P8-01 because it is not
    pre-emphasized as a locked question.
  severity: Could-Fix
```

```yaml
apodictic.finding.v1:
  id: F-P8-03
  title: Climactic recontextualization rests on withheld protagonist backstory
  evidence_refs:
    - "a list of mainland teachers who had offered to share winter terms"
    - "The last name was Elin's, copied from a letter she had sent years ago and forgotten."
  mechanism: >
    The emotional hinge — that Elin herself once volunteered — is delivered as
    new information at the reveal; nothing earlier in Elin's close-POV
    interiority hints she had made such an offer, despite the narration having
    access to her memory (e.g. the certification rules, the forgotten letter).
    For a non-mystery this is permissible, but because the whole turn pivots on
    it, the late disclosure feels slightly engineered rather than earned. A
    faint earlier trace inside her POV would convert coincidence into
    inevitability.
  severity: Could-Fix
```

```yaml
apodictic.finding.v1:
  id: F-P5-01
  title: Low counter-pressure makes the protagonist's turn feel foreordained
  evidence_refs:
    - "She told herself the delay was practical."
    - "the small key no longer felt like an obligation carried for someone else"
    - "\"You can't run a school on memories.\""
  mechanism: >
    Every beat bends one direction (unsigned order, sworn key, arriving pupils,
    the affirming note). The only opposing force, Pell, is a single line and
    concedes immediately. Elin never seriously entertains signing, so the
    resolution confirms rather than tests her. The piece works as mood but the
    dramatic question ("will she sell?") lacks real jeopardy.
  severity: Could-Fix
```

## Artifact Rows

**Continuity Bible**

| ID | Item | Note |
|---|---|---|
| CF-01 | Auction clock | "twelve hours" vs. overnight span — see F-P10-01 |
| CF-02 | Brass key fit | Fails desk drawer, opens mantel cabinet — internally consistent, but drawer left open (F-P8-01) |

**Setup–Payoff**

| ID | Setup | Payoff | Status |
|---|---|---|---|
| SP-01 | Brass key from Mara (S2) | Opens mantel cabinet (S5) | Paid |
| SP-02 | Names pencilled in cupboard incl. Tomas Bell (S3) | Tomas arrives / pupils climb hill (S3/S6) | Paid |
| SP-03 | Locked narrow desk drawer (S4) | — | **Unpaid (F-P8-01)** |
| SP-04 | Tuning fork (S5) | — | **Unpaid (F-P8-02)** |
| SP-05 | Boarded eastern windows (S1) | Boards off, "faced the harbor awake" (S6) | Paid |

## Synthesis

A structurally sound, closed short piece: single POV, clean causal spine, well-planted central key, and a satisfying frame (boarded windows → windows awake). The material issues are two: one genuine **Chekhov violation** (the emphasized locked desk drawer, SP-03) that a reader is primed to see resolved, and one **timeline arithmetic** slip (the "twelve hours," F-P10-01). Both are Should-Fix and independently correctable — resolve or drop the drawer; adjust the clock or the arrival hour. The remaining notes (orphan tuning fork, late backstory pivot, thin counter-pressure) are craft-level Could-Fixes that affect resonance, not integrity.

RECOGNITION: No — I do not recognize this as a specific published author or title; it presents as an original submission.
