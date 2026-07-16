# Rhetorical Stance Triage

Use this argument-domain triage only for overstatement-family findings: CL4, SM4,
WR-on-analogy, BP4, DI4/FM-A13, FM-A8, FM-A12, FM-A14, FM-A17, and FM-A19.
It runs while Triage assigns severity, before the Deficit Lock. It classifies the
rhetorical move; it never adjudicates whether the underlying claim is true.

## Boundary and posture

The writer declares or confirms the document register. `asserted` is the default;
`generative` is never silently inferred. An intake-declared high-stakes signal forces
`asserted` document-wide. A prescriptive/action-demanding cash-out is assessed at asserted
burden at that span regardless of the document register.

This is the argument-domain sibling of `ai-prose-calibration.md` Layer C source triage.
Source triage adjudicates voice/craft pattern families. This triage adjudicates
argumentative overstatement. They share writer-facing verdict words but do not share flag
families or verdict storage.

## Stance taxonomy

| Code | Stance | Working definition |
|------|--------|--------------------|
| **S1** | Sincere assertion | Default: offered as straight argument. |
| **S2** | Marked play | Irony, mock-heroic, bathos, a self-flagged pun, or another legibly playful move. |
| **S3** | Productive overstatement | A deliberate strong-form claim intended to be pushed against. |
| **S4** | Strategic misreading | Deliberate or indifferent misprision that generates a new position. |
| **S5** | Performative provocation | The reaction is the move's function rather than its propositional content. |

Pick the dominant stance and move on; the codes are ledger aids, not an ontology. S5 is
recognized but not served by a severity-demotion pathway in any real-consequence context.

## Verdict protocol

Run all three tests and report their outputs:

1. **Signaling:** does the text mark the move through register shift, bathos, self-flag,
   explicit hedge, or a demonstrably shared genre convention?
2. **Payoff:** does the move fund something downstream that the hedged version could not?
3. **Function under detection:** re-read the span as if its move were explicitly labeled.
   Does the argumentative work still happen? This is decisive when the first two disagree.

Convergence yields the candidate `earned`, `unearned`, or `earned-by-frame`. Divergence
yields `divergent`, with all test outputs returned to the writer. These are model/reader
judgments, never mechanically certified. The writer remains the authority.

An earned or earned-by-frame candidate calibrates an eligible finding to Could-Fix at
Triage. Unearned/divergent leaves severity unchanged. The committed severity is then
locked. For an earned would-be demotion under an active high-stakes gate, record
`calibration_effect: blocked-high-stakes`; for one joined to a prescriptive cash-out,
record `calibration_effect: blocked-cash-out`. Unearned/divergent records retain their
stance and full severity without a block effect because no demotion was attempted. The
validator proves only supplied `cash_out_ref` joins; join completeness remains an auditor
obligation. Premise-plausibility/GT8 flags are always excluded.

## Worked discriminators

- **S2 / earned-by-frame:** a mock-heroic "revolution for horsekind" is visibly playful;
  detection preserves its deflationary function.
- **S3/S4 / earned:** Nietzschean polemic or a disclosed redescription can remain
  productive when the reader identifies the move.
- **S4 / unearned:** a strategic reading presented unmarked as settled, load-bearing
  evidence does not survive detection. Evidentiary function, not fertility or intent,
  controls the boundary.
- **Motte-and-bailey / unearned:** if labeling the strong claim as exaggeration makes the
  conclusion evaporate, function-under-detection fails. DI4/FM-A13 retains full severity.

## Red-team and Firewall rules

Red Team attacks S3/S4 material as its strongest sincere reconstruction, not merely its
surface excess. An `earned` verdict is not evidence that the overstated claim is true; an
`unearned` verdict is not evidence that it is false. Any output that crosses that line
fails the Firewall.
