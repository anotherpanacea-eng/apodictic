### Validators — Finding Disconfirmation

`refutation-coverage` no longer blocks the `run_spot_check` gate on an honest run where Step 6b
weakens or refutes a HIGH Should-Fix. The budget's `eligible` count is recomputed from the
ledger, and the §6.9 transcription had already lowered that finding's confidence, so the
recount came up short and no truthful record could pass. A Should-Fix with a `weakened` or
`refuted` record now counts as eligible, since only lock-time eligible findings are processed.
A new self-test arm covers the case.
