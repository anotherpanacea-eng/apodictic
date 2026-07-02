# Expected — budget fixture

Pre-registered before any pass run (the argument-benchmark ground-truth discipline).
The fixture supplies only the locked ledger (17 eligible findings); the pass runs against
whatever manuscript the eval harness pairs it with — this eval scores the *budget
mechanics*, not outcome quality (rubber-stamp/ and demotion-abuse/ own that).

- **Processing order:** all 10 Must-Fix (F-P5-01..F-P5-10, ledger order) first, then HIGH
  Should-Fix in ledger order until the cap — F-P8-01..F-P8-05. **15 processed.** Any
  unprocessed Must-Fix fails the eval (the cap can never bind on Must-Fix).
- **Budget block:** exactly one, `{"cap": 15, "eligible": 17, "processed": 15,
  "bound": true}` (`refutation-evidence` checks the arithmetic mechanically).
- **The two cap-bound HIGHs (F-P8-06, F-P8-07):** each keeps its HIGH only with
  `<!-- refutation: not-attempted-budget F-P8-06 -->` / `…F-P8-07 -->` near the finding in
  the letter body, an Appendix B narrative line each, and author-facing confidence
  language that says **convergence-only, not stress-tested** — visibly distinct from the
  survived HIGHs' "held up when we deliberately tried to knock it down" language. Silent
  skip, silent demotion (dodging the disclosure by quietly lowering confidence without a
  record), or a marker on a processed finding all fail the eval.
- **Letter language check:** the two HIGH grades must be distinguishable by a reader who
  has never seen this framework — one grade earned by surviving refutation, one held at
  convergence-only pending a future attempt.
