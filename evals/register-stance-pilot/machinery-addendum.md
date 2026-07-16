# Dialectical Clarity — Register & Stance Addendum (Candidate Machinery)

*Apply this addendum ON TOP of the standard Dialectical Clarity audit reference. Where this addendum
extends the base audit, follow the addendum. All base-audit steps still run; all findings are still
recorded. This addendum changes calibration and adds codes; it never removes coverage.*

---

## Part 1 — Argument Register (document level)

A run now carries a `register` field set at intake: `asserted` (default) or `generative`. The
generative register applies only when the writer has declared/confirmed it at intake AND no
high-stakes signal is present (testimony, expert affidavit, regulatory comment, legal brief,
peer-reviewed publication force `asserted`).

### New argument type: AT5 (Generative / Lens-Offering)

| Code | Type | Promise to Reader | Burden Level |
|------|------|-------------------|--------------|
| **AT5** | Generative | "Here's a lens; look through it and see what it reveals" | Split — see below |

**AT5 burden split** (diagnose within the type, as with AT4):

1. **Coherence burden** — the lens must survive its own development (internal consistency of the
   metaphor/frame as it extends). LOW-MEDIUM.
2. **Fertility burden** — the lens must do generative work: reveal, reframe, or connect something
   not visible without it. This replaces soundness as the success criterion. It is a real burden.
3. **Cash-out burden** — every point where the lens is converted into an assertion or prescription
   carries burden at the ASSERTED level, scaled to how hard the conversion is pressed. A lightly
   hedged, self-applied suggestion carries light burden. A concrete policy prescription, a demand
   for real-world action, or a factual claim offered as established carries FULL asserted-register
   burden regardless of the declared register. The register covers the journey, never the landing.

### New failure codes: GN namespace

| Code | Name | Description |
|------|------|-------------|
| **GN0** | Register instability | The piece oscillates between lens-offering and asserting without signaling; the reader can't calibrate whether they are being invited to play or asked to believe. |
| **GN1** | Inert lens | The lens is introduced and developed but never does work; nothing is revealed that was not visible without it. |
| **GN2** | Concealed cash-out | An assertion or prescription is delivered at full force under exploratory cover — the register functioning as a motte (cross-reference DI4). **GN2 findings are never demoted by the register.** |
| **GN3** | Broken lens | The metaphor contradicts its own terms when extended; coherence burden fails. |
| **GN4** | Borrowed authority unreturned | Technical precision (neuroscience, statistics, control theory, etc.) is imported and ends up doing WARRANT work at a cash-out point rather than illustrative work inside the lens. Texture is fine; load-bearing borrowed authority at a landing is not. |

### Severity mapping under `register=generative`

- GN2 and GN4 floor at the severity the equivalent asserted-register finding would carry.
- GN0, GN1, GN3 calibrate by how much the piece asks of the lens.
- WR / SM / BP findings on non-cash-out spans floor at **Could-Fix**, recorded with
  `register: generative` in the finding block, with a note naming what a reader who rejects the
  lens loses.
- CL4 / definitional-drift findings: a term migrating from technical to metaphorical sense is
  the METHOD of a lens essay, not automatically smuggling. Flag only when the migration is
  concealed at a cash-out point (the borrowed precision is still being spent as if technical).
- All cash-out points must be individually located, listed, and assessed at asserted burden.

### Register-claim integrity

A declared generative register does NOT rescue a piece whose structure is asserted. If the piece
demands real-world action, treats contested claims as established, or leans on evidence-shaped
support for its landing, assess those spans at full asserted burden and check GN2. The register is
earned by the piece's structure, not by its framing sentences.

---

## Part 2 — Rhetorical Stance Triage (instance level)

Before assigning final severity to any overstatement-family finding (CL4, SM4, WR-on-analogy, BP4,
DI4, FM-A8 False Precision, FM-A12 Emotional Inflation, anecdote-to-principle, authority overreach,
epistemic erasure / straw man), classify the instance's stance:

| Code | Stance | Description |
|------|--------|-------------|
| **S1** | Sincere assertion | Default. The move is offered as straight argument. |
| **S2** | Marked play | Irony, mock-heroic, bathos, self-flagged pun or wink; the text marks the move as play. |
| **S3** | Productive overstatement | Deliberate strong-form claim intended to be pushed against; the exaggeration is the engine of the piece. |
| **S4** | Strategic misreading | Deliberate or indifferent misprision of a source that generates a new position. |
| **S5** | Performative provocation | The move's function is the reaction it provokes, not its content. No earned-verdict pathway demotes severity for S5 in any form with real consequence context. |

### Verdicts: earned / unearned / earned-by-frame

Core principle — **function under detection**: a move is earned if and only if it retains its
function when the reader sees it for what it is. Productive overstatement survives detection
(a polemic still works on a reader who knows it is polemic). Deception requires non-detection
(a motte-and-bailey collapses the moment the reader sees both positions; laundered evidence stops
working when its provenance is visible).

Supporting tests (run all three; convergence → assign the verdict; divergence → report the tests'
outputs and return the verdict to the writer):

1. **Signaling test** — does the text mark the move (register shift, bathos, self-flag, explicit
   hedge, genre convention the audience demonstrably shares)? Marked → earned-by-frame candidate.
2. **Payoff test** — does the overstatement pay off in the piece's economy? Is something built on
   the provocation that could not be built on the hedged version? A provocation that funds nothing
   downstream is unearned regardless of intent.
3. **Function-under-detection test** — re-read the span AS IF the move were explicitly labeled
   ("the author is deliberately overstating here"); does the argumentative work still happen?
   This is the decisive test when the first two disagree.

### Severity interaction

- Run stance triage during severity assignment, before the Deficit Lock commits the finding.
- Earned or earned-by-frame → finding demotes to Could-Fix, with `stance:` and
  `stance_verdict:` recorded in the finding block.
- Unearned → severity unchanged.
- **Stakes gate:** in high-stakes forms the triage still runs and records, but NO verdict demotes
  severity.
- **Cash-out gate:** a finding joined to a prescriptive cash-out remains at full asserted burden;
  no register floor or stance verdict demotes it.
- Precedence, highest first: high-stakes gate → prescriptive cash-out → register floor → instance
  stance.

### Firewall lines

- Stance verdicts classify the MOVE, never the claim. An "earned" verdict is not evidence the
  overstated claim is true; "unearned" is not evidence it is false.
- The triage never authors the sober version of the claim for the writer; it names the gap between
  the move and its discharge.
