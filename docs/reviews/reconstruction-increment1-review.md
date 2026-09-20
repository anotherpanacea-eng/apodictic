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
