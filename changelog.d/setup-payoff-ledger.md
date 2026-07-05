### Validators — Setup–Payoff Ledger (referential completeness for foreshadowing)

New `setup-payoff` validator arm + the `apodictic.setup_payoff.v1` (foreshadow) and
`apodictic.payoff.v1` (resolving payoff) schemas — the mechanical home for ConStory-Bench's
**"Abandoned Plot Elements"** row (introduced narrative expectations never resolved). The model
extracts the author-marked **Foreshadow → Trigger → Payoff** triples; the validator DERIVES each
foreshadow's `state` (`paid_off` / `open` / `abandoned`) deterministically and checks referential
completeness — **SP1** schema (SP-NN / PO-NN ids, required fields, state enum), **SP2** referential
integrity (a non-empty `payoff_ref` must resolve to a real payoff block; forward-only, N:1 allowed;
a phantom ref FAILs), **SP3** open rationale (an `open` state must carry a non-empty
`open_rationale`), **SP4** derived-state agreement (a declared state that disagrees with the refs
FAILs — no model in the gate), **X1** firewall (no `apodictic:finding` block, no editorial-severity
token — the register is a fact list, not a defect list). An `abandoned` row is a surfaced fact the
editorial letter cites in prose (Stage A wiring; the Legal-Risk / Content-Advisory precedent), never
a validation failure. Shipped with `scripts/setup_payoff_checks.py`,
`core-editor/references/setup-payoff-ledger.md`, and the canonical `example-setup-payoff-ledger.md`
wired into `--check-all` under `--strict`. The self-testable validator count is derived from
`AGG_VALIDATORS` (adding `setup-payoff` is the whole count change).

Anchors the concept on *Codified Foreshadowing-Payoff Text Generation* (Yun, Zhou, Hou, Peng, Shang),
**arXiv:2601.07033** (the F→T→P triple + the causal-debt / abandoned framing) — but takes the schema
only, **not** CFPG's LLM-judged detection method: the gate is mechanical referential-completeness, the
model marks the triple and never renders the verdict. Cross-repo sibling: voicewright
`specs/31-foreshadow-payoff-checker.md` is the generation-side counterpart (same CFPG root, different
consumer — declare-and-lint vs. extract-and-audit). Deferred (Stage B): promoting `abandoned` to a
structured promise-contract finding, and the semantic "does this passage actually pay off the setup?"
judgment (a future SETEC-consumer surface).
