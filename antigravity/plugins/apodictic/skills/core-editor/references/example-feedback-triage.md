# Feedback Triage — Worked Example

<!--
Worked example of a contract-conformant Feedback Triage artifact (see
revision-coach/references/feedback-triage.md + docs/feedback-triage.md). A writer returns with
beta-reader / critique-group / editor feedback; each item is recorded as an
apodictic.feedback_item.v1 block carrying APODICTIC's own assessment of the external claim, the
triage disposition, and any items it conflicts with. This file is exercised by
`validate.sh --check-all` as a canonical release-gate target for `feedback-triage` (contract
hygiene + conflict referential integrity + the "contradiction kept live on both sides" check). It
is illustrative, not a run artifact; keep it passing when the contract or the validator changes.

Note the resolved contradiction: FB-03 ("add a prologue explaining the magic system") conflicts
with FB-02 ("cut the prologue"); the conflict is resolved by declining FB-03, so neither
contradiction is left actionable on both sides (no W1). FB-04 is unverified, so it is parked at
`monitor` rather than acted on (no W2).
-->

## Author-facing summary

Returning with notes from two beta readers, the critique group, and the agent. Sorted, checked
against the diagnosis, and prioritized below. One contradiction (prologue in vs. out) is resolved.

## Triaged feedback

- **FB-01 — midpoint sags (beta reader A).** Confirmed: the Pass 5 pacing-collapse finding is the
  same problem the reader felt. Acting now.
  <!-- apodictic:feedback_item
  {"schema":"apodictic.feedback_item.v1","id":"FB-01","source":"Beta reader A","claim":"The middle third drags and the midpoint doesn't land.","assessment":"validated","triage":"act-now","evidence_refs":["Pass 5 §Pacing","Ch. 9"],"disposition":"Matches the Pass 5 pacing-collapse finding; revise the middle third first."}
  -->
- **FB-02 — cut the prologue (critique group).** Confirmed against the Pass 1 orientation finding.
  Acting now.
  <!-- apodictic:feedback_item
  {"schema":"apodictic.feedback_item.v1","id":"FB-02","source":"Critique group","claim":"The prologue competes with Chapter 1 and should be cut.","assessment":"validated","triage":"act-now","evidence_refs":["Pass 1 §Orientation"],"disposition":"Aligns with the Should-Fix orientation finding; cut the prologue."}
  -->
- **FB-03 — add an explanatory prologue (beta reader B).** Contradicts FB-02 and the diagnosis;
  the frame works without front-loaded exposition. Declined — this resolves the prologue conflict.
  <!-- apodictic:feedback_item
  {"schema":"apodictic.feedback_item.v1","id":"FB-03","source":"Beta reader B","claim":"Add a prologue that explains the magic system up front.","assessment":"refuted","triage":"decline","conflicts_with":["FB-02"],"evidence_refs":["Pass 1 §Orientation"],"disposition":"Contradicts FB-02 and the orientation finding; the system reveals well in-scene. Declined."}
  -->
- **FB-04 — voice wobbles in Part II (agent).** Not yet confirmed by analysis; parked for a
  targeted Pass 3 re-run before any revision.
  <!-- apodictic:feedback_item
  {"schema":"apodictic.feedback_item.v1","id":"FB-04","source":"Agent","claim":"The narrator's voice slips in Part II.","assessment":"pending","triage":"monitor","disposition":"Run a targeted Pass 3 (voice) on Part II to confirm before scheduling work."}
  -->
