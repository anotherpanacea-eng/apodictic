### Validators — Finding Disconfirmation

`refutation-coverage` no longer blocks the `run_spot_check` gate on an honest run where Step 6b
weakens or refutes a HIGH Should-Fix. The §6.9 transcription lowers that finding's ledger
confidence after lock, so the budget's `eligible` now reconciles against a count that includes
Should-Fix findings with a `weakened` or `refuted` record. The cap-bound exemption is stricter:
a record cannot prove a finding was HIGH at lock, so a marker is honored only when the strict set
(Must-Fix plus HIGH now) exceeds the cap and every processed record names a finding in that set.
Fabricated demotions can make the arithmetic add up but can never spend the budget or exempt an
untested HIGH. One edge stays strict: an honest run with more than 15 eligible findings and any
6b demotion cannot use the exemption marker. Three new self-test arms cover the honest demotion
and the two fabricated-record attacks.
