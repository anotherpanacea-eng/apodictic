# Example — Findings Ledger (round 2, re-diagnosis of the revised draft)

<!--
Canonical ROUND-2 fixture for the `regression-diff` validator, paired with ../example-run-folder-r1/.
Re-diagnosis of the revised draft. Two synthesis-bound findings: F-P5-01 (Ch 7) re-flags the want/cost
problem round 1 marked RESOLVED — same origin (P5) + same chapter (Ch 7) + overlapping mechanism tokens,
so the matcher raises it as a RECURRENCE-CANDIDATE (the resolution may not have held). F-P5-02 (Ch 3) is
a new voice-drift finding in a chapter round 1 left QUIET (round 1 had findings only in Ch 7 and Ch 9),
so the matcher raises it as a NEW-IN-QUIET-CHAPTER breakage candidate. Round 1's F-RR-01 (Ch 9) has no
round-2 match and was marked resolved, so it classifies as RESOLVED-AND-HELD (the win). IDs are renumbered
per run; the match is heuristic, never by ID equality. Keep gate-valid.
-->

## Pass 5 — Character — Ledger Entry

### Notable Findings
- The protagonist's want still never forces a sacrifice; the stakes remain abstract after the revision.

<!-- apodictic:finding
{"schema":"apodictic.finding.v1","id":"F-P5-01","mechanism":"the want still never forces a sacrifice; stakes remain abstract","severity":"Must-Fix","confidence":"HIGH","evidence_refs":["Ch 7"],"fix_class":"raise the cost of the want","risk_if_fixed":"may slow the midpoint"}
-->

- A new voice-drift sentence breaks POV discipline in the opening chapter.

<!-- apodictic:finding
{"schema":"apodictic.finding.v1","id":"F-P5-02","mechanism":"a new voice-drift sentence breaks POV discipline","severity":"Should-Fix","confidence":"MEDIUM","evidence_refs":["Ch 3"],"fix_class":"hold the POV or mark the break","risk_if_fixed":"may flatten the voice"}
-->

### Data Artifacts for Letter Reference
- POV-consistency scan: 1 paragraph in Ch 3 slips out of the established POV.

### Cross-Pass Connections
- Connects to Pass 5: the voice slip coincides with the unresolved want from round 1.

### Unresolved Questions
- None.

### Audit Triggers
- None.
