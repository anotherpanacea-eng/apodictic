# Example — Findings Ledger (round 1)

<!--
Canonical ROUND-1 fixture for the `regression-diff` validator (docs/draft-regression-testing.md),
paired with ../example-run-folder-r2/. `validate.sh --check-all` runs `regression-diff` across the
two folders to prove cross-round round-linkage (R1) and that the deterministic heuristic matcher
raises the recurrence (W1) and quiet-chapter (W2) candidates under --strict. Round 1 carries two
synthesis-bound findings (Ch 7, Ch 9); its Revision Report marks BOTH resolved, so round 2's
re-diagnosis tests those resolutions. Keep both folders gate-valid (ledger-check / structured-findings)
when the matcher or validators change. The matcher keys on origin code + chapter token + shared
mechanism tokens, never on ID equality (which the framework does not guarantee across rounds).
-->

## Pass 5 — Character — Ledger Entry

### Notable Findings
- The protagonist's want is stated but never costs her anything, so the stakes stay abstract.

<!-- apodictic:finding
{"schema":"apodictic.finding.v1","id":"F-P5-01","mechanism":"the want never forces a sacrifice, so stakes stay abstract","severity":"Must-Fix","confidence":"HIGH","evidence_refs":["Ch 7"],"fix_class":"raise the cost of the want","risk_if_fixed":"may slow the midpoint"}
-->

### Data Artifacts for Letter Reference
- Want-vs-cost table: 0 of 12 scenes impose a cost on the want.

### Cross-Pass Connections
- Feeds Pass 8 (Reveal Economy): the unpaid want weakens the climax payoff.

### Unresolved Questions
- Is the want meant to read as ironic? Confirm with the author.

### Audit Triggers
- None.

## Pass 1 — Reader Experience — Ledger Entry

### Notable Findings
- The middle third's pacing collapses: three days pass in two sentences, reading as a continuity seam.

<!-- apodictic:finding
{"schema":"apodictic.finding.v1","id":"F-RR-01","mechanism":"three days collapse into one paragraph, a continuity seam","severity":"Should-Fix","confidence":"HIGH","evidence_refs":["Ch 9"],"fix_class":"restore a transit beat","risk_if_fixed":"may add length"}
-->

### Data Artifacts for Letter Reference
- Elapsed-time map: Ch 9 compresses 3 days into 2 sentences.

### Cross-Pass Connections
- Connects to Pass 5: the compression also flattens the protagonist's reaction beat.

### Unresolved Questions
- None.

### Audit Triggers
- None.
