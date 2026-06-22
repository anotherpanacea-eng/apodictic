# Intake Interview — *The Tidewater Braid*

<!--
Worked example of a contract-conformant Uncertainty-Resolution Intake Interview (see
intake-interview.md + docs/uncertainty-intake-interview.md). Generated at the after-Pass-0/1
checkpoint, it asks the author to resolve a SPECIFIC structural ambiguity the framework detected but
cannot settle from the text — never the contract (genre / controlling idea / reader promise / who
it's for), which the draft-then-validate intake and Shelf & Positioning already own.

This file is exercised by `validate.sh --check-all` (paired with
`example-intake-interview-ledger.md`) as a canonical release-gate target for `intake-interview`,
under `--strict`: I1 schema, I2 no-contract-duplication, I3 grounded ambiguity via BOTH paths
(IQ-01 resolves `ambiguity_ref` F-P2-04 against the Ledger; IQ-02 grounds in a `source_note` on the
Unresolved-Questions bullet), and I4 calibrate-not-suppress (`treat_as_intended` directs HOW the
feature is assessed and never says "suppress the flag"). Every `kind` is a flavor of
intentional-vs-accidental — the closed enum has no contract value.
-->

## Detected ambiguities

<!-- apodictic:intake_query
{"schema":"apodictic.intake_query.v1","id":"IQ-01","kind":"timeline-order","ambiguity_ref":"F-P2-04","source_note":"","current_inference":"The non-linear ordering across Chapters 4-6 reads as possibly unintentional drift.","confidence":"LOW","question":"Is the non-linear ordering in Chapters 4-6 a deliberate braided timeline, or unintended drift?","answer":"Deliberate — the three threads are meant to braid and converge in Chapter 6.","treat_as_intended":"Pass 2 assesses the braided ordering as intended structure, on its own terms; the finding remains available to Triage and is not pre-empted."}
-->

<!-- apodictic:intake_query
{"schema":"apodictic.intake_query.v1","id":"IQ-02","kind":"register-straddle","ambiguity_ref":"","source_note":"the `### Unresolved Questions` bullet on the second-person interludes","current_inference":"The second-person address in the interludes may be an unintentional artifact of an earlier draft.","confidence":"UNCERTAIN","question":"Are the second-person interludes a deliberate device, or an artifact of an earlier draft to revise out?","answer":"Deliberate — the second-person interludes are the drowned narrator speaking to the reader.","treat_as_intended":"Pass 5 evaluates the second-person interludes as a chosen register, on their own terms; no verdict is pre-empted."}
-->

## Notes

- **Every query disambiguates a detected ambiguity** — IQ-01 the timeline ordering (`F-P2-04`), IQ-02
  the second-person interludes (an Unresolved-Questions bullet with no id). Neither re-asks the
  contract; that stays with the draft-then-validate intake and Shelf & Positioning.
- **Grounded in the framework's own uncertainty.** Each query states the framework's `current_inference`
  + `confidence` first, so the author's `answer` corrects a stated prior — a reader can audit that the
  question was genuinely uncertain, not a fishing expedition.
- **Answers calibrate the lens, never the verdict.** `treat_as_intended` tells analysis to *assess the
  feature on its own terms*; it never says "suppress the flag." The framework still reaches and locks
  the verdict at Triage — the author supplies intent, not a downgrade (the Deficit-Lock guard).
