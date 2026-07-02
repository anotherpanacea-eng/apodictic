# Example Findings Ledger — dispositions fixture

*Canonical fixture for `validate.sh disposition-check` (docs/finding-dispositions.md). A
deliberately **non-governed** project (the sidecar carries no `gate_events` — the common case),
so the disposition records were written by the direct writer alongside the Coaching Log markers.
Two Must-Fix findings carry active dispositions (one declined, one deferred); one Should-Fix
stays open.*

## Pass 5 — Ledger Entry

### Notable Findings

1. **Interiority stays abstract at every decision point.** Severity: Must-Fix. The protagonist's
   choices are narrated as conclusions, never as pressure.
<!-- apodictic:finding
{"schema":"apodictic.finding.v1","id":"F-P5-01","mechanism":"decision points narrated as conclusions; no on-page pressure","severity":"Must-Fix","confidence":"HIGH","evidence_refs":["Ch. 4","Ch. 12"],"fix_class":"scene-level interiority","risk_if_fixed":"slows the middle if over-applied"}
-->

2. **The mentor's death lands before the reader can price it.** Severity: Must-Fix. The
   relationship gets one scene of setup for three chapters of consequence.
<!-- apodictic:finding
{"schema":"apodictic.finding.v1","id":"F-DP-02","mechanism":"consequence outweighs setup for the mentor bond","severity":"Must-Fix","confidence":"MEDIUM","evidence_refs":["Ch. 7","Ch. 8"],"fix_class":"setup redistribution","risk_if_fixed":"front-loads the early chapters"}
-->

3. **Chapter-opening weather beats repeat.** Severity: Should-Fix. Five chapters open on the
   same sky-report cadence.
<!-- apodictic:finding
{"schema":"apodictic.finding.v1","id":"F-P2-03","mechanism":"repeated chapter-opening cadence","severity":"Should-Fix","confidence":"HIGH","evidence_refs":["Ch. 2","Ch. 5","Ch. 9"],"fix_class":"opening variation","risk_if_fixed":"low"}
-->

### Data Artifacts for Letter Reference
- none

### Cross-Pass Connections
- none

### Unresolved Questions
- none

### Audit Triggers

| Trigger | Evidence | Recommendation |
|---|---|---|
