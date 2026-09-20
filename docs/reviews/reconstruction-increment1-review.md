# Approval reconstruction Increment 1 review record

Base: `09583d2f9a5e0365fd4209cf4fa861d5a0f0419b`.
Scope: apply the PR #235 ruling and implement the deterministic first increment.
The historical ruling remains unchanged. Synthetic histories test software contracts;
they do not establish semantic calibration or benchmark ground truth.

## Contract review — 2026-09-20

Authority author and independent reviewer were dispatched separately with
`gpt-6-astra`. The reviewer read the revised specification, ADR 0002, PR #235
ruling, repository workflow and fleet BUILD-PREFLIGHT before clearing the contract.

Resolved before engine implementation:

- R1: one approved/current eligibility predicate with endpoint closure, and
  an author-owned REQUIRED-but-withheld readiness failure.
- R2: edge origin derives from mint shape; provenance/anchor refresh is node-only;
  reconciliation without legal events leaves the ledger/context unchanged.
- R3: one OS-held project lock covers recovery, reads, append and publication;
  expected-head checking and fsync acknowledgement distinguish rejected, committed
  and uncertain outcomes. No unconditional hardware power-loss guarantee.
- R4: no second mint of an existing identity; revision/novelty preserve prior decisions.
- R5: empty is unstarted and cannot pass draft readiness.
- R6: anchors retain their source-version binding and resolve against hash-verified
  evidence snapshots without making those snapshots approval authority.
- F2: free projection values use canonical JSON escaping.
- Review clarifications: retained-receipt envelope and prefix grammar, header-only
  Verdict uniqueness, engine-path containment/non-link checks, complete normalizer
  instructions, deterministic paragraph/map and recorded-gate shape grammar.

Disposition: **SPEC-CLEAR for Increment 1**. Independent review found no remaining
contract blocker after those changes. Implementation validation remains separate.

## Delivery boundary

Increment 1 supplies graph/draft-ready validation and a fail-closed acceptance
envelope. Approval-session UX, packet/drafter production, semantic judging/comparison
and `/ready` integration remain Increments 2–5. H2/H5/H7/H15/H16 core checks cannot
certify those later integrations. Keep the constituent PR draft and unarmed; reserve
hosted clearance and merge for the normal integration train.

## Build checkpoint — 2026-09-20

The implementation and synthetic fixtures are complete at the deterministic
Increment 1 boundary. Luna prepared the engine and histories; Terra completed
transition, recovery and receipt validation after adversarial probes exposed
incomplete guards. The mirrors are byte-identical.

Local checks passed before independent build review:

- `bash scripts/validate.sh --check-all` (validator self-tests, canonical
  framework checks, reconstruction histories and mirror gate).
- H1–H18 on native Windows Python 3.12 and WSL Python 3.10.
- Standalone helper self-test from a directory without repository fixtures.
- Generator self-checks for Codex and Antigravity; release-generation,
  changelog, status-drift, inventory-parity and whitespace checks.
- Independent real-file probes: corrupt committed prefix plus torn tail is
  preserved; absent anchors refuse append; short writes retry; fsync uncertainty
  reports `committed: null`; projection failure after append reports
  `committed: true` and the next validation repairs projections; concurrent
  threads and processes receive `PROJECT-BUSY` without consuming active bytes.

The fixtures include independent known-answer identity/hash values. Their
negative cases require domain errors rather than treating unexpected Python
exceptions as successful refusals. Receipt shape validation can report only the
expected I5 unavailability for an otherwise valid synthetic envelope; it cannot
certify semantic judgments.

Independent build-review disposition is recorded below after review. Hosted
validation remains deferred to the integration train.

## Independent build review and repairs

The generic review was dispatched with `gpt-5.5`; the separate fleet/authority
review with `gpt-6-astra`. Both reviewed candidate
`1092a926facd398e40cb1077c8149f517c5df81f` against the recorded base. The literal
`/code-review` skill was unavailable; these were independent Codex agent reviews.
The fleet reviewer read the complete BUILD-PREFLIGHT and sanitized checklist.
Neither review claimed hosted clearance or permission to merge.

Findings repaired in the follow-up:

- Preserve supplied Argument State provenance when refreshing evidence; never
  invent a `REFRESH` local reference.
- Compare full canonical identity material at every existing-ID join. Distinct
  controlled collisions now refuse with `ID-COLLISION` across replay, append,
  revision, novelty and reconciliation, including novel-origin records.
- Complete H2's known-ineligible map checks and H7's repeated-disposition,
  duplicate-quarantine and empty-append refusals. Strengthen source-binding proof.
- Validate retained source/draft custody before mutations, including no-op
  reconciliation; missing or corrupt historical evidence cannot advance state.
- Keep public errors within their documented envelopes. Native pre-append errors
  refuse safely; validation errors retain I5. Preserve the append outcome through
  lock cleanup and CLI output failures, including an uncertain fsync followed by
  an unlock failure.

The expanded histories pass on Windows Python 3.12 and WSL Python 3.10. Follow-up
checks target the reproduced failures and their adjacent paths. Controlled hash
collisions are injected for branch coverage; no natural SHA-256 collision is
claimed. Re-review of the repaired head is recorded separately below.

## Re-review disposition

Both reviewers cleared repaired implementation head
`354429e5532ae3990523537aaabaf7110b1e822d` with no remaining material P1/P2
findings. Each independently reran H1–H18 and reproduced the relevant original
failures against the repairs. The generic reviewer additionally checked syntax,
self-test, mirror parity and true/null outcomes after cleanup failures. The fleet
reviewer confirmed supplied provenance, collision refusals without ledger mutation,
and the repaired H2/H7 coverage claims.

Disposition: **reviewed for an unarmed draft constituent**. The full local combined
gate passed on the initial review candidate; the repair received focused behavioral
checks on Windows and WSL and both independent re-reviews. Generator/status checks
passed for this change. No hosted CI receipt, semantic calibration, end-to-end
acceptance PASS or merge clearance is claimed. This final section is a review
receipt only; it changes no implementation, fixtures or contract.

## Train-admission review (2026-09-20)

An independent read of the exact head
`3428e24b2df172bd58d4e8ac98db84d9fc52d0b1`, taken before admitting this
constituent to the v2.12.0 integration train, found three defects the earlier
re-review did not. Each was reproduced against that head before it was repaired,
and the two behavioral ones now carry executable cases that fail on the
unrepaired engine.

- **Session presentation order violated the contract.** `project_session` sorted
  the merged node and edge lists, so `"e-…" < "n-…"` put every eligible edge
  ahead of every still-pending node. The contract requires pending nodes in
  lexical ID order, *then* eligible edges. Because `Adjudication_Session.json` is
  the resume cursor, the session steered the author to an edge while claims were
  still unadjudicated. Covered by **H19**.
- **`_ProjectLock.__enter__` leaked the lock on the `LOCK-UNSUPPORTED` path.**
  That error is raised inside a `try` whose only handler catches `OSError`, so
  the per-project `RLock` was never released and the descriptor never closed. The
  raising thread could not observe it (an `RLock` is reentrant); every other
  thread then received `PROJECT-BUSY` permanently, masking the real cause on
  exactly the platform the branch exists to serve. Covered by **H20**.
- **Dead duplicated `raise` in `_receipt_identity`.** The identical
  `RECEIPT-GRAMMAR` raise appeared on two consecutive lines; the second was
  unreachable. Removed. Note that counting `Verdict: ` lines is *not* the missing
  check it might look like: a conforming receipt carries a second `Verdict: ` line
  inside each gate-run block, so such a guard would reject valid receipts.

Two further findings were recorded and deliberately not repaired here, because
neither is a correctness defect in the ledger and both are larger than a
train-admission fix should be:

- **Replay cost is quadratic.** Every append re-replays the whole ledger two or
  three times and deep-copies the record map per bundle, so cost grows as
  O(bundles² × records). Measured on a 250-node graph with one decision per node:
  426.9s of CPU across the appends, against 1.79s for a single full
  `validate_project` replay of the same finished ledger, on a 240 KB file. It is
  algorithmic, not data volume.
- **Torn-tail recovery discards an unbounded suffix and still reports `PASS`.**
  This is contract-conformant and the receipt-prefix check correctly runs before
  truncation, but a 5 015-byte LF-less ledger truncates to zero bytes with
  `verdict: PASS` and exit 0, and the engine verdict enum has no
  `PASS-WITH-RECOVERY` value for a shell caller to see.

Disposition: **admitted to the v2.12.0 train with the three repairs above.** The
combined gate `bash scripts/validate.sh --check-all` passes on the repaired head,
including H1–H20 and `check-mirror`.
