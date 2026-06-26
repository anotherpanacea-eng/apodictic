# argument-carve/precarve — Pre-carve equivalence baseline

Captured from the MONOLITHIC `pass-dependencies.md` + `run-synthesis.md` +
`intake-router-runtime.md` tables **before** the Workstream-A table splits.

Files:

- `argument-editorial-letter.md` — Minimal argument-DE letter exercising `audit-signal-propagation`
  (argument-cluster hard gates) and `decision-layer-check` (Argument-DE class).
- `argument-findings-ledger.md` — Paired Findings Ledger with `apodictic.finding.v1` blocks;
  argument-shaped findings (Dialectical Clarity WR1, Argument Red Team Fatal).
- `argument-state.md` — Minimal `Argument_State.md` with `apodictic:argument_spine` block.
- `propagation-output.txt` — `audit-signal-propagation` output captured on this fixture pre-carve.
- `decision-layer-output.txt` — `decision-layer-check` output captured on this fixture pre-carve.

## Equivalence contract

Post-carve, the `argument-carve-behavior-preservation` validator re-runs
`audit-signal-propagation` and `decision-layer-check` on these fixed inputs and
asserts output is byte-identical to the captured golden files. Any drift means
a resolver no longer reads the argument rows it needs.
