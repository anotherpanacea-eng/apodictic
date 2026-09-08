# Continuity corrective retest results

The completed run does not establish that the corrective improves diagnosis.
All 64 productions and 128 scorer calls finished, but the frozen conservative
primary outcome is unresolved for both production models. Twenty-three grades
failed exact-quote validation, and the scorers also disagreed on substantive
metrics. No production prompt change is justified.

## Frozen primary outcome

Each model/arm has two continuity-pair repetitions. A success requires a grounded
broken-member mechanism hit and no unsupported clean Must/Should continuity
finding, agreed by both scorers. Unresolved cells remain in the denominator.

| Production model | Arm | Resolved successes | Resolved failures | Unresolved | Planned pairs |
|---|---|---:|---:|---:|---:|
| Astra high | Baseline | 1 | 0 | 1 | 2 |
| Astra high | Corrective | 0 | 0 | 2 | 2 |
| Terra high | Baseline | 0 | 0 | 2 | 2 |
| Terra high | Corrective | 1 | 0 | 1 | 2 |

Neither model has a computable primary delta. These are counts of resolved
successes, not evidence that either arm failed its unresolved pairs. The transfer
guard is also unresolved: 23 unresolved guard entries for Astra production and
25 for Terra. Zero agreed hard-failure flags does not clear those unknowns.

## Per-scorer results and reliability

| Scorer | Valid grades | Invalid grades | Planned |
|---|---:|---:|---:|
| Codex 5.5 high | 42 | 22 | 64 |
| Astra high | 63 | 1 | 64 |

All invalid grades failed diagnosis or submission quote matching after whitespace
normalization. The original answers and inspection receipts were retained; no
quality retry, punctuation relaxation or silent regrade was used. There were zero
transport failures, contaminated calls or missing receipts. Forty-two of 64 outputs
had differing metric vectors between scorers, including differences caused by
invalid grades. This measures scoring reliability, not production-model quality.

The Astra scorer alone gives Astra production 2/2 primary successes in both arms:
a baseline ceiling, with no demonstrated improvement. For Terra production it
gives baseline 1 success plus 1 unresolved and corrective 2 successes, leaving the
delta uncomputable. Its transfer/invention assessment flags a hard failure for
each production model. The 5.5 scorer also flags one hard failure for Astra
production and leaves Terra unresolved. These individual flags and the lack of
consensus must both remain visible; selecting the more favorable scorer would
change the experiment's decision rule.

The secondary 100-point rubric is descriptive. Valid-grade means and their
unequal denominators are in SCORING-RECEIPT.json; invalid grades remain missing
from those means and remain unresolved in the fixed primary matrix. The numeric
means cannot override primary uncertainty or invention flags.

## Advisory adjudication

Two independent Codex 5.5-high reviews challenged the evidence after all scoring
was sealed. The primary reviewer inspected all 16 continuity outputs and their
32 grades. The transfer reviewer inspected all transfer grader summaries and
targeted packets for the priority flags and representative invalid grades; this
was not a semantic re-review of all 48 transfer outputs. Both preserved the frozen
conservative result. Their separate local artifacts are bound in the receipt.

| Production model | Advisory baseline primary | Advisory corrective primary | Interpretation |
|---|---:|---:|---|
| Terra high | 1/2 | 2/2 | Plausible primary improvement; full adoption conditions still unmet |
| Astra high | 2/2 | 2/2 | Baseline ceiling; no demonstrated improvement |

This advisory reading does not replace the table above or convert invalid grades
into valid ones. The Terra baseline false positive imposes an unstated mechanical
objection on the clean clock clue. The corrective avoids that overfire while still
identifying the broken member's age/date contradictions. Astra handles the primary
pair in both arms. Thus there is a useful development signal for Terra, alongside
an unresolved official result.

The primary reviewer also confirmed minor local attribution/sequence errors in a
Terra corrective broken diagnosis. The 5.5 hardflag against an Astra corrective
clean diagnosis was narrower quote hygiene around supported passages, rather than
a new semantic continuity error. Its frozen scorer-specific flag remains intact.
The transfer reviewer confirmed two Astra-scorer concerns: an unsupported causal
attribution for unsteady hands in an Astra diagnosis, and a Terra diagnosis that
incorrectly describes an auction proceeding after its cancellation. The first is
minor; neither should disappear from the record just because consensus is absent.

Invalid grades are not all harmless typography. The review found outer-quotation
wrapper mismatches, but also diagnosis material mislabeled as submission evidence
and a source quotation absent from the submission. Repairing punctuation alone
would not resolve this scoring population. Neither review licenses a disputed key
or makes these cases human ground truth.

## Implementation and limits

The experiment tooling and execution are complete. No runtime corrective is
implemented: the required improvement and transfer conditions were not established.
Scoring reliability and the specific disputed evidence need resolution before a
new experiment could justify adoption. Any later evaluation needs its own reviewed
protocol; it must preserve this run and must not relabel these exposed cases as a
fresh holdout.

There are only two repetitions of four existing public synthetic pairs, one
provider and requested configurations rather than verified served-model identities.
The continuity pair already informed the correction. Neither the two scorer votes
nor final model review provides human ground-truth authority, a whole-suite M2
pass, a powered superiority claim or a frontier ranking.

## Custody and validation

SCORING-RECEIPT.json binds the original scorer manifest, frozen aggregate and
reviewed accounting adapter. All scorer calls launched by 01:38:24 UTC and the
last completed at 01:39:03 UTC on 2026-09-08, before the original 01:45 launch
cutoff. The reviewed continuation contingency was unused. Production and scoring
used the authenticated Codex subscription, with tool-disabled fresh contexts and
CLI 0.153.4. Per-call cost and served-model identity were unavailable.

The experiment's 29 custody/behavior tests passed during tooling build review.
Final repository validation reproduced a pre-existing timestamp-sensitive
calibration-honesty self-test: equal file modification times can select the clean
fixture instead of the intended newer violating fixture. Canonical checks pass,
but the full gate is not yet cleared. A reviewed fixture-only timestamp correction
is prepared separately; it does not affect frozen experiment inputs or results.
Independent review cleared the completed interpretation; delivery still needs
final validation and review of the exact committed head.
