# Rubric: Argument Engine Benchmark

Use this rubric when scoring a Nonfiction Argument Engine run against a
pre-registered ground-truth answer key (`groundtruth.md`). It specializes the
core rubrics for argument-shaped nonfiction. Full design rationale, corpus
design, and the convergence protocol are in
[../../docs/argument-benchmark-spec.md](../../docs/argument-benchmark-spec.md).

## Inputs Required

- Fixture text (in-repo, or referenced source for text-not-stored fixtures)
- Pre-registered `groundtruth.md` for the fixture (GT1–GT7)
- `Argument_State.md` from the run (§§1–9 populated)
- Editorial letter / Dialectical Clarity output
- `Red_Team_Memo.md` (required to score Q5)
- Argument session plan (required to score Q6)

Without the pre-registered ground truth, no argument dimension can be scored.
Ground truth registered *after* seeing the run output is void.

## Metrics

Score each dimension on the 0-3 scale defined in
[../../docs/eval-harness-spec.md](../../docs/eval-harness-spec.md#core-metrics).
Dimensions map to the seven roadmap test questions and to
`Argument_State.md` sections.

- **Q1 — Claim recovery** (§2 C0 vs GT1): 0 different/invented claim · 1 partial / over-broad · 2 right claim, loose phrasing · 3 C0 within the GT1 paraphrase band, subclaims consistent.
- **Q2 — Failure-locus discrimination** (§3 vs §4 vs GT2): 0 located in the wrong layer / conflated support and warrant · 1 right layer, wrong codes · 2 right layer + codes, discriminator unstated · 3 right layer, codes match GT2, names *why this layer and not the adjacent one*.
- **Q3 — Strongest objection** (§6 vs GT3): 0 only weak/decoy objections · 1 named the zone weakly · 2 right zone · 3 right zone with correct OB/DI classification.
- **Q4 — Audience calibration** (§1 + AC vs GT4): 0 ignored audience or produced an audience-pleasing distortion · 1 audience noted, not used · 2 surfaced GT4's "improve" item · 3 surfaced it *and* avoided the named "distort" failure.
- **Q5 — Red-team danger** (§10.4 vs GT5): 0 only decoys/cosmetic attacks · 1 one real vulnerability buried below decoys · 2 hit a pre-registered vulnerability · 3 hit ≥1 and ranked it above the decoys.
- **Q6 — Repair order** (§10.5 vs GT6): 0 order violates the dependency rule · 1 right targets, wrong order · 2 correct first target · 3 correct first target *and* respects GT6's dependency rule.
- **Q7 — Form fairness** (§1 Distinguish / Step 9 vs GT7): 0 fired the false-positive trap code as a structural failure · 1 fired it but hedged · 2 correct classification, trap noted but not cleanly downgraded · 3 classification matches GT7 and the form-dependent code is downgraded to advisory.

## Binary Checks

Per [eval-harness-spec.md §Binary Checks](../../docs/eval-harness-spec.md#binary-checks),
argument subset:

- **No invented content (Firewall):** no claim, subclaim, warrant, objection,
  definition, or stakes added that the text does not contain. A single
  invented argumentative object voids the run.
- **Distinguish protocol ran:** Step 9 / §1 Distinguish classification is
  present for every fixture, including the broken ones.
- **`Argument_State.md` emitted:** §§1–9 populated; §10 initialized.
- **Companion-module presence:** `Red_Team_Memo.md` present when Q5 is in
  scope; argument session plan present when Q6 is in scope.
- **Model tag and run folder naming follow policy.**

## Q7 Is the Specificity Gate

Q7 is scored *primarily on positive controls* (fixtures whose correct
diagnosis is SOUND or UNCONVENTIONAL-BUT-EFFECTIVE). A false-positive trap
code fired on a positive control is **Q7 = 0 for that fixture regardless of
Q1–Q6**, and blocks the bucket from passing (per
[argument-benchmark-spec.md §Convergence](../../docs/argument-benchmark-spec.md#convergence-protocol-the-success-condition)).
Sensitivity (catching real failures) without specificity (leaving sound
arguments alone) is not a passing engine.

## Convergence

Score per-run, then assess convergence across two independent **engine** runs.
There are three convergence classes:

- **Failure-bearing fixtures** — anchors are core claim, top 1–3 failures,
  burden mismatch, and objection zone; agreement = both runs land in the same
  ground-truth band on ≥3 of 4 anchors, core claim mandatory.
- **Pure positive controls** (no registered soft spot) — claim (GT1) +
  Distinguish classification (GT7) + no invented failure; all three required.
- **SOUND real calibration fixtures** (the referenced `CORPUS.md` pieces — SOUND
  *with* a registered Should-Fix soft spot) — both runs must agree on **all
  five**: GT1 claim, GT2 failure locus/layer, GT3 objection zone, the
  severity-calibration check (soft spot named at Should-Fix, no over-firing), and
  GT7 = SOUND. The pure-control rule is insufficient here (two runs could agree
  on SOUND yet miss the registered soft spot). Full rule + role separation:
  [RUN-PROTOCOL.md §Step 4](../fixtures/argument-benchmark/RUN-PROTOCOL.md).

Two reviewers scoring one output is reliability, not convergence. See
[argument-benchmark-spec.md §Convergence](../../docs/argument-benchmark-spec.md#convergence-protocol-the-success-condition),
§Positive-control convergence, and the calibration-fixture note.

## Decision Rules And Failure Attribution

Use [eval-harness-spec.md §Decision Rules](../../docs/eval-harness-spec.md#decision-rules)
for accept / accept-with-override / revise-and-retest / reject. Every
dimension scored 0 or 1 is logged with a failure-attribution cause class
([eval-harness-spec.md §Failure Attribution](../../docs/eval-harness-spec.md#failure-attribution)),
with one argument-specific addition: **ground-truth ambiguity**. If two
careful reviewers disagree on the answer key itself, the finding is against
the *ground truth*, not the engine — the answer key needs sharpening before
the fixture can score the engine.

## Fixture-Specific Overrides

A fixture's `groundtruth.md` is authoritative for that fixture. Positive
controls may legitimately exclude Q2/Q3/Q5/Q6 (there is no planted failure to
locate) and score Q1 + Q4 + Q7 only. The ground-truth file states which
dimensions are in scope.
