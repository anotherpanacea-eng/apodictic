# Setup–Payoff Ledger: A Quiet Year (literary fiction)

<!--
Worked example of a contract-conformant Setup–Payoff Ledger (see docs/setup-payoff-ledger.md). The
Ledger is the REFERENTIAL-COMPLETENESS half of a developmental-edit style sheet: the mechanical home
for the one ConStory-Bench craft row APODICTIC otherwise has no surface for — "Abandoned Plot
Elements", committed narrative expectations never resolved (setup without payoff). It records the
author-marked Foreshadow → Trigger → Payoff triples (Codified Foreshadowing-Payoff Text Generation,
Yun et al., arXiv:2601.07033) and CHECKS every foreshadow resolves.

The module firewall is *extract the marked triple, never author the verdict*: the model marks the
F/T/P, the validator DERIVES the state (paid_off | open | abandoned) deterministically and checks
referential completeness — it never decides whether a passage "counts" as a payoff (the deferred
SETEC-consumer job) and carries NO editorial severity (X1). An `abandoned` row is a SURFACED fact,
not a defect verdict — the editorial letter cites it in prose (Stage A wiring); severity, if any, is
owned downstream by promise-contract.

This file is exercised by `validate.sh --check-all` as a canonical release-gate target for
`setup-payoff`: SP1 schema (both block kinds; SP-NN / PO-NN ids, required fields, state enum), SP2
referential integrity (SP-01's payoff_ref PO-03 resolves), SP3 open rationale (SP-02 carries one),
and SP4 derived-state agreement (each declared state matches the §D4 derivation over the resolved
refs). It carries the three valid states and NO firewall violation. The hostile negatives
(phantom-ref → SP2, open-no-rationale → SP3, a declared-paid_off-with-no-ref → SP4, and a planted
editorial-severity token → X1) live in the validator's `--self-test` as in-memory mutations, per the
repo's canonical fixture-passes-clean / hostile-arms-in-self-test convention (Continuity Bible,
Content Advisory). X1 scans the RAW artifact (mirroring world_bible's firewall), so this fixture is
deliberately free of any literal severity token — the register is a fact list, not a defect list.
-->

## Payoffs

<!-- apodictic:payoff
{"schema":"apodictic.payoff.v1","id":"PO-03","payoff":"The revolver Mara pockets in Ch 1 is the weapon Jon uses to force the inheritance confession in the climax.","anchor":["Ch 9 ¶4"]}
-->

## Setups

<!-- apodictic:setup_payoff
{"schema":"apodictic.setup_payoff.v1","id":"SP-01","foreshadow":"Mara pockets their mother's revolver from the kitchen drawer, telling herself it is only for safekeeping.","anchor":["Ch 1 §2"],"trigger":"when Jon arrives to contest the inheritance","payoff_ref":"PO-03","state":"paid_off"}
-->

<!-- apodictic:setup_payoff
{"schema":"apodictic.setup_payoff.v1","id":"SP-02","foreshadow":"The grandmother's half-finished letter names a beneficiary the family has never heard of.","anchor":["Ch 4 ¶11"],"payoff_ref":"","state":"open","open_rationale":"a deliberate series thread — the unnamed beneficiary is the hook that opens Book 2; flagged, not a defect in this volume"}
-->

<!-- apodictic:setup_payoff
{"schema":"apodictic.setup_payoff.v1","id":"SP-03","foreshadow":"Jon is described wearing a silver locket he never removes; the narrator lingers on it for half a page.","anchor":["Ch 2 ¶6"],"payoff_ref":"","state":"abandoned"}
-->

## Setup–Payoff Ledger

The reader-facing rollup. One row per triple; State is mechanically derived, never judged. SP-03 is
`abandoned` — a committed expectation (the lingered-on locket) with no resolving payoff and no
deferral rationale: a dropped promise the editorial letter cites in prose.

| ID | Foreshadow (short) | Trigger | payoff_ref | State |
|---|---|---|---|---|
| SP-01 | Mara pockets the revolver "for safekeeping" | Jon arrives to contest the inheritance | PO-03 | paid_off |
| SP-02 | the half-finished letter names an unknown beneficiary | — | — | open |
| SP-03 | Jon's silver locket he never removes | — | — | abandoned |

## Notes

- **The triple is extracted, the state is derived.** The model marks each Foreshadow → (Trigger) →
  Payoff; the validator resolves `payoff_ref` and derives the state from the refs (§D4). An author may
  write `state` into the block, but SP4 confirms it matches the derivation — the register never
  overrides the mechanics.
- **`open` is not `abandoned`.** SP-02 is deliberately unresolved and says why (a series thread), so
  it is flagged, not a defect. SP-03 has no payoff and no rationale, so it is the causal debt left
  unpaid — the "Abandoned Plot Elements" signal.
- **No severity in the register (X1).** The Ledger records the state and stops. Whether an abandoned
  setup rises to an editorial severity band is a downstream call (promise-contract, Stage B) — the
  Ledger never asserts it, and X1 fails the artifact if a severity token leaks in.
