# Finding Disconfirmation — behavioral eval fixtures

Ground-truth fixtures for the Step 6b **Finding Disconfirmation Pass**
(`plugins/apodictic/skills/core-editor/references/run-synthesis.md §Step 6b`;
spec: `docs/finding-disconfirmation.md` §12 Behavioral evals). All fixture text is
synthetic (written for this eval; no permission constraints).

The mechanical validators (`validate.sh refutation-coverage / refutation-evidence /
refutation-write-scope`) prove record *shape* — quotes are real spans, transcription is
exact, severity is untouched. These fixtures test what validators cannot: whether the pass
actually **kills wrong findings and spares solid ones**. Run the pass (inline or as a
disconfirmation subagent, per the Step 6b execution-mode split) against each fixture's
snapshot + locked ledger, then score against `expected.md`. The subagent input must
exclude the ledger's confidence tokens and any letter draft (anti-anchoring, contract
item 5) — the ledger files here carry confidence only because the transcription and
budget checks need a locked baseline; strip the `confidence` field from the dispatch
packet.

| Fixture | Tests | Fails when |
|---|---|---|
| `rubber-stamp/` | failure mode (a), self-agreeing rubber stamp: a deliberately WRONG finding the pass must kill | the pass returns `survived` for F-P5-01, or its `counter_evidence_quotes` omit the disconfirming line |
| `demotion-abuse/` | failure mode (b), performative humility: a bulletproof finding the pass must NOT demote | the pass returns `weakened`/`refuted` for F-P0-01 |
| `budget/` | cap-bound disclosure: 17 eligible (10 Must-Fix + 7 HIGH Should-Fix) under the cap of 15 | fewer than 15 processed, any Must-Fix unprocessed, the 2 cap-bound HIGHs missing their `<!-- refutation: not-attempted-budget F-… -->` markers/Appendix B lines, or letter language that fails to distinguish stress-tested HIGH from convergence-only HIGH |

After each run, the produced Refutation Record must itself pass the three mechanical
validators against the fixture snapshot (the fixtures are validator-clean by
construction), so behavioral scoring never excuses a malformed record.
