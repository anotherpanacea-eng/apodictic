# Budget — Findings Ledger

<!--
CAP-BOUND fixture (the budget eval, docs/finding-disconfirmation.md §12): 17 eligible
findings — 10 Must-Fix (the output-policy ceiling) + 7 HIGH Should-Fix — against the
Step 6b cap of 15. A compliant pass processes all 10 Must-Fix plus the first 5 HIGH
Should-Fix in ledger order (F-P8-01..F-P8-05), writes a budget block
{cap:15, eligible:17, processed:15, bound:true}, and DISCLOSES the two unprocessed HIGHs
(F-P8-06, F-P8-07): a near-finding "refutation: not-attempted-budget" marker per id in the
letter body (pinned form in expected.md — not spelled out here because a literal marker
would nest a comment close inside this comment), Appendix B lines, and convergence-only
(not stress-tested) confidence language for both. Silent skips and
demotions-to-dodge-the-cap fail the eval.
-->

## Pass 5 — Ledger Entry

### Notable Findings
1. **The want never forces a sacrifice in act one, so the stakes stay abstract.** Locked Must-Fix.

<!-- apodictic:finding
{"schema":"apodictic.finding.v1","id":"F-P5-01","mechanism":"the want never forces a sacrifice in act one, so the stakes stay abstract","severity":"Must-Fix","confidence":"HIGH","evidence_refs":["Ch. 1"],"fix_class":"targeted revision","risk_if_fixed":"adjacent-scene ripple"}
-->

2. **The mentor's death carries no consequence for the protagonist's next choice.** Locked Must-Fix.

<!-- apodictic:finding
{"schema":"apodictic.finding.v1","id":"F-P5-02","mechanism":"the mentor's death carries no consequence for the protagonist's next choice","severity":"Must-Fix","confidence":"HIGH","evidence_refs":["Ch. 2"],"fix_class":"targeted revision","risk_if_fixed":"adjacent-scene ripple"}
-->

3. **The midpoint reversal is announced in narration instead of enacted in scene.** Locked Must-Fix.

<!-- apodictic:finding
{"schema":"apodictic.finding.v1","id":"F-P5-03","mechanism":"the midpoint reversal is announced in narration instead of enacted in scene","severity":"Must-Fix","confidence":"HIGH","evidence_refs":["Ch. 3"],"fix_class":"targeted revision","risk_if_fixed":"adjacent-scene ripple"}
-->

4. **The antagonist's leverage over the family is asserted but never demonstrated.** Locked Must-Fix.

<!-- apodictic:finding
{"schema":"apodictic.finding.v1","id":"F-P5-04","mechanism":"the antagonist's leverage over the family is asserted but never demonstrated","severity":"Must-Fix","confidence":"HIGH","evidence_refs":["Ch. 4"],"fix_class":"targeted revision","risk_if_fixed":"adjacent-scene ripple"}
-->

5. **The promise of the locked room is raised in chapter one and never paid.** Locked Must-Fix.

<!-- apodictic:finding
{"schema":"apodictic.finding.v1","id":"F-P5-05","mechanism":"the promise of the locked room is raised in chapter one and never paid","severity":"Must-Fix","confidence":"HIGH","evidence_refs":["Ch. 5"],"fix_class":"targeted revision","risk_if_fixed":"adjacent-scene ripple"}
-->

6. **The climax resolves through a coincidence the text has not seeded.** Locked Must-Fix.

<!-- apodictic:finding
{"schema":"apodictic.finding.v1","id":"F-P5-06","mechanism":"the climax resolves through a coincidence the text has not seeded","severity":"Must-Fix","confidence":"HIGH","evidence_refs":["Ch. 6"],"fix_class":"targeted revision","risk_if_fixed":"adjacent-scene ripple"}
-->

7. **The sister's betrayal has no on-page motivation chain.** Locked Must-Fix.

<!-- apodictic:finding
{"schema":"apodictic.finding.v1","id":"F-P5-07","mechanism":"the sister's betrayal has no on-page motivation chain","severity":"Must-Fix","confidence":"HIGH","evidence_refs":["Ch. 7"],"fix_class":"targeted revision","risk_if_fixed":"adjacent-scene ripple"}
-->

8. **The timeline of the flood contradicts the harvest chronology.** Locked Must-Fix.

<!-- apodictic:finding
{"schema":"apodictic.finding.v1","id":"F-P5-08","mechanism":"the timeline of the flood contradicts the harvest chronology","severity":"Must-Fix","confidence":"HIGH","evidence_refs":["Ch. 8"],"fix_class":"targeted revision","risk_if_fixed":"adjacent-scene ripple"}
-->

9. **The final choice costs the protagonist nothing she values on page.** Locked Must-Fix.

<!-- apodictic:finding
{"schema":"apodictic.finding.v1","id":"F-P5-09","mechanism":"the final choice costs the protagonist nothing she values on page","severity":"Must-Fix","confidence":"HIGH","evidence_refs":["Ch. 9"],"fix_class":"targeted revision","risk_if_fixed":"adjacent-scene ripple"}
-->

10. **The epilogue reverses the climax's consequence without dramatizing the reversal.** Locked Must-Fix.

<!-- apodictic:finding
{"schema":"apodictic.finding.v1","id":"F-P5-10","mechanism":"the epilogue reverses the climax's consequence without dramatizing the reversal","severity":"Must-Fix","confidence":"HIGH","evidence_refs":["Ch. 10"],"fix_class":"targeted revision","risk_if_fixed":"adjacent-scene ripple"}
-->

## Pass 8 — Ledger Entry

### Notable Findings
1. **The reveal economy front-loads answers, draining question density after the midpoint.** Locked Should-Fix at HIGH.

<!-- apodictic:finding
{"schema":"apodictic.finding.v1","id":"F-P8-01","mechanism":"the reveal economy front-loads answers, draining question density after the midpoint","severity":"Should-Fix","confidence":"HIGH","evidence_refs":["Ch. 11"],"fix_class":"targeted revision","risk_if_fixed":"adjacent-scene ripple"}
-->

2. **Secondary characters converge on one diction register, flattening scene texture.** Locked Should-Fix at HIGH.

<!-- apodictic:finding
{"schema":"apodictic.finding.v1","id":"F-P8-02","mechanism":"secondary characters converge on one diction register, flattening scene texture","severity":"Should-Fix","confidence":"HIGH","evidence_refs":["Ch. 12"],"fix_class":"targeted revision","risk_if_fixed":"adjacent-scene ripple"}
-->

3. **Interiority drops out of the confrontation scenes where it matters most.** Locked Should-Fix at HIGH.

<!-- apodictic:finding
{"schema":"apodictic.finding.v1","id":"F-P8-03","mechanism":"interiority drops out of the confrontation scenes where it matters most","severity":"Should-Fix","confidence":"HIGH","evidence_refs":["Ch. 13"],"fix_class":"targeted revision","risk_if_fixed":"adjacent-scene ripple"}
-->

4. **The subplot's clock is never synchronized with the main plot's deadline.** Locked Should-Fix at HIGH.

<!-- apodictic:finding
{"schema":"apodictic.finding.v1","id":"F-P8-04","mechanism":"the subplot's clock is never synchronized with the main plot's deadline","severity":"Should-Fix","confidence":"HIGH","evidence_refs":["Ch. 14"],"fix_class":"targeted revision","risk_if_fixed":"adjacent-scene ripple"}
-->

5. **Chapter openings repeat the same orientation move eleven times.** Locked Should-Fix at HIGH.

<!-- apodictic:finding
{"schema":"apodictic.finding.v1","id":"F-P8-05","mechanism":"chapter openings repeat the same orientation move eleven times","severity":"Should-Fix","confidence":"HIGH","evidence_refs":["Ch. 15"],"fix_class":"targeted revision","risk_if_fixed":"adjacent-scene ripple"}
-->

6. **The frame narration promises retrospection the body never uses.** Locked Should-Fix at HIGH.

<!-- apodictic:finding
{"schema":"apodictic.finding.v1","id":"F-P8-06","mechanism":"the frame narration promises retrospection the body never uses","severity":"Should-Fix","confidence":"HIGH","evidence_refs":["Ch. 16"],"fix_class":"targeted revision","risk_if_fixed":"adjacent-scene ripple"}
-->

7. **The setting's cost rules bend whenever the plot needs travel to be fast.** Locked Should-Fix at HIGH.

<!-- apodictic:finding
{"schema":"apodictic.finding.v1","id":"F-P8-07","mechanism":"the setting's cost rules bend whenever the plot needs travel to be fast","severity":"Should-Fix","confidence":"HIGH","evidence_refs":["Ch. 17"],"fix_class":"targeted revision","risk_if_fixed":"adjacent-scene ripple"}
-->

### Audit Triggers
| Trigger | Evidence | Recommendation |
|---------|----------|----------------|
