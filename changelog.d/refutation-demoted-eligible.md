### Validators — Finding Disconfirmation

`refutation-coverage` no longer blocks the `run_spot_check` gate on an honest run where Step 6b
weakens or refutes a HIGH Should-Fix. The §6.9 transcription lowers that finding's ledger
confidence after lock, so the budget's `eligible` now reconciles against a count that includes
Should-Fix findings with a `weakened` or `refuted` record. The cap-bound exemption still uses the
strict count (Must-Fix plus HIGH now): a record cannot prove the finding was HIGH at lock, so
fabricated demotions can never exempt an untested HIGH. One edge stays strict: an honest run with
more than 15 eligible findings whose demotions bring the strict count to 15 or fewer cannot use
the exemption marker. Two new self-test arms cover the honest demotion and the fabricated-bound case.
