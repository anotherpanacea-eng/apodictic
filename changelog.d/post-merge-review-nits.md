### Validators — post-merge review nits

Three small fixes from a review of the merged batch (no new validators; count unchanged at 38→40 baseline):

- **`reader-instrument` B3 (fabrication smell-test).** The "unsourced question" advisory was gated on the Ledger *having* `### Unresolved Questions` bullets, so an `unresolved-question` reader-question with an invented `source_note` passed unflagged when the Ledger had **none** (the more suspicious case — citing a UQ that can't exist). The advisory now also fires when the Ledger has zero UQ bullets. Stays a WARN: UQ provenance is non-referential by design, so this is a fabrication smell-test, not a hard gate.
- **`manuscript-viz` render gate (false pacing curve).** `W2 scene order` is advisory, but a reordered manifest draws a *false* pacing curve — the one warning that corrupts the render's core output. The `render` subcommand now refuses on a scene-order divergence too (not just ERROR-level gate failures), overridable with `--force`; `W1 coverage` stays advisory so a legitimate partial map still renders.
- **Swarm cost copy.** The intake-router execution-mode menu rows (B/C/I) said a bare "roughly 5x" while `run-core.md` notes the 2026-06 re-test measured ~8.5×+ on long fiction — understating cost at the decision point. The menu rows now carry the measured figure.
