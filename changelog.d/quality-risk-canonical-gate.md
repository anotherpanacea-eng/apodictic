### Validators — Canonical Release Gate

`quality-risk-triggers` now runs as a canonical release gate. Added
`core-editor/references/example-quality-risk-contract.md` — a clean, well-formed,
low-risk Contract worked example (single-POV literary family drama, moderate
darkness, mid-draft developmental goal) that raises none of the five pre-pass
quality-risk triggers (Q1-Q5) — and wired it into `validate.sh --check-all`: a
clean arm asserts the canonical contract exits 0, plus a hostile arm that flips
its darkness rating to the top setting on a throwaway copy and asserts the Q1
consent/governance trigger fires and exits non-zero (gate proven to have teeth).
This closes the last gap in the "canonical-framework validator runs as release
gate" track — every validator with a single-artifact canonical target is now
gated against the shipped framework, not only its own synthetic fixtures.
Validator count unchanged (67); no new validator.
