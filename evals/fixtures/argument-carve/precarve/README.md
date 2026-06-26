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

## What this baseline proves (and what it does not)

Post-carve, the `argument-carve-behavior-preservation` smoke gate re-runs
`audit-signal-propagation` and `decision-layer-check` on these fixed inputs and
diffs their summary line against the captured goldens — asserting the mechanical
resolvers still classify the argument fixture as Argument-DE and do not regress to
error after the table split.

It is deliberately NOT the full §2.4 field-level equivalence (no row-by-row
Findings-Ledger id/severity diff, no annotation anchor-map diff): the propagation
summary line is invariant on this fixture, so this is a smoke check, not the proof.
The authoritative behavior-preservation guarantees — the ones with teeth — are
`audit-signal-propagation --check-registry` (all 45 signal-emitting audits still
have §4e rows; it FAILS if the split fragment is dropped) and the byte-identical
§4e extraction proof in `../4e-before-after.diff`.
