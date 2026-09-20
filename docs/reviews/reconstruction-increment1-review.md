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
