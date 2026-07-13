### Argument engine — R4B AIF export + ADR review folds (non-blocking)

Folds five non-blocking review findings from the R4B pass. **ADR hygiene:** restores the
accepted `docs/adr/0001-argument-layer-boundary.md` Consequences sentence ("those `unmapped`
rows are the visible R4B/R2/R3 work-list") that the R4B PR had silently rewritten, and moves
the reinterpretation ("R4B reviewed those rationales into present-tense conclusions rather than
treating them as a quota for speculative mappings") into the dated **R4B implementation note**,
so the amendment history is explicit rather than overwriting the accepted decision.

**Exporter (`scripts/argument_aif.py`).** The `_populated` placeholder heuristic no longer
treats *any* underscore-led line as an empty stub: only the reserved machine-seeded shapes
(`_seeded…_`, `_pending…_`, or a bracketed `[…]` stub) count as unpopulated, so authored italic
content smuggled into an out-of-profile section (e.g. a §7 body of `_smuggled real out-of-profile
content_`) now discloses its `OUT-OF-PROFILE-SECTION` loss instead of being dropped silently,
while genuinely-seeded stubs still disclose nothing. Under `--source`, `check` now binds the
export's recorded `source.artifact` basename to the supplied source filename, so a tampered
basename can no longer ride through a source-closure check. Sourceless `check` now enforces the
canonical **key order** (it re-emits the parsed object in the exporter's emission order and
compares bytes), so a key-reordered-but-otherwise-canonical artifact fails without a source;
`docs/argument-aif-export.md` states that loss-set completeness still genuinely requires
`--source`. The self-test banner now derives its arm count from a counter (17 arms) instead of a
stale literal, adds a dedicated `final-support-enum-invalid` build-failure arm, and asserts both
the out-of-profile disclosure and the reserved-placeholder non-disclosure. The committed goldens
(`evals/fixtures/argument-aif/final-audit/export.json` and the reference example) are unchanged
and regenerate byte-identically; the `scripts/` ↔ `plugins/apodictic/scripts/` mirror stays
byte-identical.
