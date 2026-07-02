### Adversarial finding disconfirmation: HIGH means "survived"

New synthesis-time **Finding Disconfirmation Pass** — Step 6b in `run-synthesis.md`
§Processing Protocol (lettered, no renumbering; after the Deficit Lock and the Adversarial
Self-Check, before the stress test). Per eligible finding (Must-Fix ∪ HIGH Should-Fix, cap
15 — Must-Fix always processed), the pass hunts counter-evidence spans, generates rival
readings, judges `survived | weakened | refuted`, and records the attempt in a new
`[Project]_Refutation_Record_[runlabel].md` artifact (`apodictic.refutation.v1` +
`apodictic.refutation_budget.v1` blocks; hybrid/swarm runs dispatch a dedicated
disconfirmation subagent whose input excludes the letter draft and confidence tokens —
anti-anchoring). The synthesis agent then transcribes only the confidence consequences into
the locked ledger blocks: survived = unchanged (never confidence-raising — HIGH now
*requires* a survived attempt, `output-policy.md §Confidence Calibration`), weakened capped
at MEDIUM, refuted = LOW/UNCERTAIN, severity never remapped. Cap-bound HIGHs are disclosed
(`<!-- refutation: not-attempted-budget F-… -->` + Appendix B), never silently skipped; a
refuted finding ships labeled with its counter-evidence quoted, never dropped.

Three new validators in one `scripts/refutation_check.py` module (registered in
`AGG_VALIDATORS`, the `run_spot_check` gate, and `--check-all` against an extended
`example-run-folder` fixture with hostile arms): `refutation-coverage` (no HIGH without
survived refutation; dangling ids; marker abuse), `refutation-evidence` (verbatim
single-line snapshot quotes — fabricated quotes void the attempt; `snapshot_sha256` binding;
missing-snapshot split — ERROR on core-de/full-de runs under `--require-snapshot`/run-shape
detection, WARN-with-demotions-void elsewhere; budget arithmetic), and
`refutation-write-scope` (no severity channel in the record; exact confidence transcription
per the outcome caps). Behavioral eval fixtures land under
`evals/fixtures/finding-disconfirmation/` (rubber-stamp, demotion-abuse, budget).
