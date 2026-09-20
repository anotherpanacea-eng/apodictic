# Approval-gated reconstruction fixtures

This directory is the Increment 1 executable home for synthetic histories H1–H18
from `docs/reviews/fr03-phase0-contract-ruling-2026-09-05.md`. The fixtures exercise
the public deterministic engine against disposable project directories. They do not
judge whether any proposition is true, calibrate a semantic model, or supply benchmark
ground truth.

Run the suite with the engine under test:

```text
# from the repository root
python3 evals/fixtures/argument-reconstruction/run_cases.py --engine plugins/apodictic/scripts/approval_graph.py
# Windows Python 3.12 alternative
py -3.12 evals/fixtures/argument-reconstruction/run_cases.py --engine plugins/apodictic/scripts/approval_graph.py
```

The `--engine` path is intentional: the root and plugin mirrors can each be exercised,
and the fixture never inventories or hashes source files. A successful run prints one
compact JSON result and exits zero. The runner uses only the standard library.

H1, H3–H4, H6, H8–H13, H17, and H18 cover the deterministic Increment 1 boundary.
H2, H5, H7, H15, and H16 deliberately stop at the deterministic first slice: packet
emission, semantic authorization, semantic freeze/recheck, and `/ready` integration are
later increments. No case claims those later layers are implemented.

The hostile controls include real source files and source snapshots, projection loss,
receipt prefix retention, newline and non-newline ledger corruption, canonical identity
reuse, endpoint eligibility, orphan/reappearance stickiness, existing-edge cascades,
and both separate-process and same-process OS lock contention checks, append fsync/short-write
outcomes, and atomic projection publication failure. Temporary project directories are removed
after each case.
