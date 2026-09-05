# Frozen construction-screen criteria (v1)

Status: author-intent candidates; no ground-truth or engine-performance license.

One fresh, independent model screen is required per input, for eight screens.
Each receives the exact common prompt, a neutral label, and only that story's
text. It receives no pair, mutation, role, descriptive path, key, or previous
review. Context is not inherited. These are instructionally separated
same-host agents, not an access-controlled or cryptographically sealed enclave.

The prompt deliberately teaches evidence scoping. This is an assisted candidate
construction screen, not a blind test of whether the production engine already
knows that method. No conclusion about frontier advantage, production accuracy,
or FR-02 corrective improvement may be drawn from the results.

## Freeze and no post-hoc repair

Before dispatch, freeze common prompt bytes, this file, intent.json, all input
bytes, and each exact dispatch prompt. Author intent is frozen before screens,
but remains a hypothesis. Save the raw screen response before folding it.
Dispatcher-owned receipts bind response hashes to the submitted input/prompt
hashes; never ask a model to certify the hashes of its own invocation.

## Fold rule (applied per pair)

| Condition | Disposition |
|---|---|
| Either input lacks a complete preserved screen | INCOMPLETE; no pair conclusion |
| Reviewer identifies an unintended continuity defect or a conspicuous mutation seam that the root confirms from the text | REWORK-CANDIDATE; preserve v1 |
| Intended control is CONSISTENT and intended mutation is INCONSISTENT; both cite the relevant loci and identify the intended distinction; no confirmed second defect or seam | RETAIN-CANDIDATE |
| Either reading is AMBIGUOUS, differs from intent, or depends on an unsupported premise, without a confirmed defective construction | AMBIGUOUS-CANDIDATE; preserve the disagreement |

Apply these in the displayed order. Root must cite the raw review and source
when confirming or declining a collateral defect; disagreement is not erased
because author intent would prefer a pass. RETAIN means eligible for further
fixture review, never accepted benchmark ground truth. One reading per input
is construction feedback and supplies no estimate of reliability or variance.

Do not rewrite v1 after seeing reviews. A repair becomes a separate v2 with
new hashes, frozen intent, and fresh screens of both affected pair members.
Neither model agreement nor an enumerated edit automatically licenses a key.
Human/independently licensed fixture adjudication remains necessary before
registration; use the existing fiction benchmark conventions at that stage.

## Construction checks

- Original synthetic prose only; no adaptation of existing fixture prose.
- Each input reads as a complete short work, with no key or role metadata.
- Each twin is exactly one contiguous before/after replacement. Everything
  outside the mutation must be byte-identical, including paragraph order.
- Author rationale names both sides of the conflict, a strongest alternative,
  and the smallest repair without flattening an intentional device.
- Hash checks validate custody and mutation conservation only. They cannot
  decide whether the prose is good or the intended diagnosis correct.
- Publication makes these public development candidates, unsuitable as a
  sealed holdout or an unseen-manuscript claim for future models.

## Versioned identity repair

For this v2, require exactly two fresh screens, one per revised input. Apply
the original ordered per-pair disposition table unchanged. The eight v1 screens
and their dispositions remain recorded; v2 does not replace their history.
