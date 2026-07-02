# Expected — rubber-stamp fixture

Pre-registered before any pass run (the argument-benchmark ground-truth discipline).

- **F-P5-01 outcome:** `refuted` (accepted: `weakened`, if the pass argues the Ch. 9
  passivity is real but materially narrowed — the mechanism's "never" is falsified either
  way). **`survived` fails the eval.**
- **counter_evidence_quotes:** must include a verbatim, single-line Ch. 5 span showing
  Mara acting under pressure. Canonical disconfirming lines (either satisfies):
  - `Mara counted the children twice, came up one short, and went back in.`
  - `She crossed the burning nursery with her coat over her mouth, pulled Ilse out from under the window bench, and carried her down the servants' stair while the ceiling above them let go.`
    (over the 25-word quote budget — a compliant pass quotes a trimmed single-line
    portion, e.g. `pulled Ilse out from under the window bench`)
- **rationale:** must name what evidence would have refuted the finding (a scene of Mara
  acting in crisis) and state that it WAS found in Ch. 5.
- **confidence_after:** `LOW` or `UNCERTAIN` (refuted row of the §7 caps table); severity
  stays Must-Fix in the ledger (never remapped); the letter delivers the finding with the
  counter-evidence quoted and an author-verification ask — not silently dropped.
- **Record hygiene:** the produced Refutation Record must pass `refutation-evidence`
  against `Rubber_Manuscript_Snapshot_eval.md` (real quotes, sha binding) and
  `refutation-write-scope` against this ledger after transcription.
