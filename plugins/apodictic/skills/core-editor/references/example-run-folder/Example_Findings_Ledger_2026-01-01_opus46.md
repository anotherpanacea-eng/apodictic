# Example — Findings Ledger

<!--
Canonical run-folder fixture (Nonfiction/fiction-agnostic) exercised by `validate.sh --check-all`
as the release-gate target for the RUN-FOLDER validators: gate-state, escalation-check,
argument-recon-prerequisite (read-only), and the gate engine itself (gate run_synthesis, run on a
temp copy so this committed fixture is not mutated). It is a minimal but gate-VALID run folder: the
ledger passes ledger-check / ledger-consolidation / structured-findings / deficit-lock, and the
sidecar carries an attested run_synthesis gate event. Keep it gate-valid when the manifest or the
validators change.
-->

## Pass 5 — Character — Ledger Entry

### Notable Findings
- The protagonist's want is stated but never costs her anything, so the stakes stay abstract.

<!-- apodictic:finding
{"schema":"apodictic.finding.v1","id":"F-P5-01","mechanism":"the want never forces a sacrifice, so stakes stay abstract","severity":"Must-Fix","confidence":"HIGH","evidence_refs":["Ch.3 p.40"],"fix_class":"raise the cost of the want","risk_if_fixed":"may slow the midpoint"}
-->

### Data Artifacts for Letter Reference
- Want-vs-cost table: 0 of 12 scenes impose a cost on the want.

### Cross-Pass Connections
- Feeds Pass 8 (Reveal Economy): the unpaid want weakens the climax payoff.

### Unresolved Questions
- Is the want meant to read as ironic? Confirm with the author.

### Audit Triggers
- None.
