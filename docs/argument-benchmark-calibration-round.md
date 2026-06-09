# Argument Benchmark — calibration round (proposal, GATED on a real run)

**Status:** Proposal. The engine edits below are staged in this branch **but must not merge until a benchmark convergence run validates them** (see §Validation gate). This is calibration of the *live* argument engine's verdict logic; unlike the deterministic validators, its correctness is established only by running the benchmark and scoring — there is no mechanical `--check-all` gate for the behavioral change. Roadmap: `ROADMAP.md` → Nonfiction Argument Engine → Benchmark Suite, "Next round" items 1–2.

## The two roadmap items

1. **Strengthen Test A (the genre-genericity decoy filter)** — the filter "must recognize 'but public safety' as the genre-generic counter and downrank it."
2. **`policy-brief-uncompared` under-fire fix** — "an AT3 recommendation with no comparative defense and no funding mechanism should drive Must-Fix → UNSOUND, but it reads SOUND (the Step-9 default-to-SOUND overrides the Severity Floor)."

## Finding #1 — the decoy filter is already built; the residual is reliability, not mechanism

The genre-genericity filter the roadmap asks for **already exists in full** in `dialectical-clarity.md` §Step 6a:

- **Test A (genre-genericity / decoy filter)** literally names the target example — *"'but public safety' → any decarceration argument"* — and instructs: "it is a **canonical-imported / decoy** objection … **Downrank it** (keep it in the inventory, never as the strongest) — *unless Test B yielded nothing*."
- **Test B (self-undermining derivation, run FIRST)** generates the text-internal candidate before Test A runs.
- **OB5 (Decoy strongest objection)** fires when the piece engages a weaker/canonical objection in place of the text-internal one, with an explicit **engine self-guard**: "if the objection *you* named as strongest passes the genre-genericity test and you skipped Test B, you are about to hand back a decoy — re-run Test B first."
- **FM-A20 (Self-Undermining Remedy)** operationalizes the pattern.

`ppi-one-size-fits-none`'s ground truth already encodes the target: GT3 strongest = the **fairness/discretion** self-undermining objection (text-internal); the **public-safety** objection is the named **decoy**, and a run that calls it strongest scores **OB5**, not a GT3 hit.

So there is **no missing mechanism and no engine edit proposed for #1.** The roadmap's residual — "blind GPT-4 ran Test B but its self-undermining objection stayed on the public-safety decoy axis" — is an *empirical reliability* gap (a model under-applied existing guidance in one run), which only a benchmark run can re-measure. **Recommendation:** treat #1 as *mechanism-complete, pending run-confirmation*. If the gated run below still shows decoy-capture on `ppi`, the targeted follow-up is a small reinforcement (e.g. require the output to name the text-internal objection *before* any genre-generic one, and assert the Test-A downrank explicitly in the §6 objection inventory) — but do not pre-emptively bloat the guidance before a run shows it is needed.

## Finding #2 — the uncompared-recommendation verdict gap (the real edit)

`policy-brief-uncompared`'s own ground truth registers **GT7 = UNSOUND** (a planted AT3 fare-free recommendation: BP5 primary + OB3, no alternative engaged, no funding mechanism). The engine reads it **SOUND** because the classification decision rule (rule 2) explicitly says *"an alternative gestured at but not engaged [is a] soft spot in a sound argument, not [a] structural break,"* and Step 9 classifies any evaluable argument SOUND even when Must-Fix codes fired. That is a deliberate, valuable anti-over-firing stance for the general case — but it misfires on the *recommendation* class.

**The principled fix (staged in this branch):** add a **bounded carve-out, rule 2a**, in `dialectical-clarity.md`:

> For an argument whose C0 is a **recommendation to act (AT3)**, the comparative dimension is *constitutive of the claim, not peripheral to it* — a reader cannot evaluate "do Y" without "rather than the alternatives that target the same goal." So when an AT3 recommendation discharges *none* of its comparative burden (BP5 primary + OB3, no funding mechanism), the recommendation is **not evaluable as a recommendation** — a defeat under decision test one — and the verdict is **Structurally Unsound** (FM-A10).

Why this is a carve-out and not an override of the default-to-SOUND discipline:

- **It satisfies rule 2's own criterion** ("the reader cannot … test the argument"), rather than bypassing it. The comparison *is* the test for a recommendation.
- **It is scoped to AT3 recommendations only** — descriptive/explanatory/interpretive theses are untouched; rule 2 stands unmodified for them.
- **It preserves the anti-over-firing guard (rule 4)** via an explicit *wholly-absent vs. partially-discharged* line: a recommendation that engages even one alternative thinly stays a Should-Fix soft spot in a sound argument. Only the *zero-comparison* recommendation is a defeat.
- A matching one-line note is added at the Step 9 "Final Diagnostic Question" so the evaluability test returns "no" for this case.

This aligns the engine with the fixture's pre-registered key; it changes verdict behavior for **every** argument-shaped run, which is exactly why it is gated.

## Validation gate — DO NOT MERGE until this passes

The deterministic gates pass (`argument-groundtruth-check` on both fixtures, `--check-all`, `argument-spine --self-test`, `build-codex --self-check`), but they validate *contract hygiene*, not the behavioral change. Before merge, run the benchmark (`evals/fixtures/argument-benchmark/run.sh` + scoring per `RUN-PROTOCOL.md`), ideally multi-model per the convergence protocol, and confirm **all** of:

1. **`policy-brief-uncompared` flips SOUND → UNSOUND** (matches GT7), with BP5 primary + OB3 named and the comparative-burden discriminator.
2. **`ppi-one-size-fits-none` does NOT regress:** GT3 strongest = the fairness/discretion text-internal objection (public-safety scored as decoy / OB5 if mis-picked), and the verdict **stays SOUND** — the rule-2a carve-out must **not** fire here (ppi's C0 is a *critique*, not an AT3 recommendation; and it engages the standardization alternative, so even read charitably its comparative burden is *partially discharged*). A run that flips `ppi` to UNSOUND means the carve-out is over-scoped — fix before merge.
3. **No verdict regression across the other ~14 fixtures** — especially: competent recommendations that *do* weigh alternatives stay SOUND; sound non-recommendation arguments (`federalist-10`, `douglass-fourth-of-july`, `coates-case-for-reparations`, `modest-proposal-satire`, the unconventional-but-effective set) are unaffected; `op-ed-warrant-leap` keeps its Should-Fix/Must-Fix calibration (it is a causal-warrant case, not an uncompared recommendation).
4. **Severity-floor / Step-9 interaction is coherent** — the carve-out reaches UNSOUND *through* rule 2a's evaluability defeat, not by letting any Must-Fix force UNSOUND (which would re-introduce over-firing).

If 1 passes but 2 or 3 regress, narrow the carve-out's trigger (tighten "wholly undischarged") before merge. If the run shows #1's decoy still captured, apply the §Finding-1 reinforcement.

## Files

- `dialectical-clarity.md` — rule **2a** (the AT3 uncompared-recommendation carve-out) + the Step-9 evaluability-test note. (Engine edit; gated.)
- Ground truth unchanged — `policy-brief-uncompared` GT7 already says UNSOUND and `ppi` GT3 already names the decoy; the keys encode the targets, the engine is being brought into line with them.
- No validator/schema change; no count bump (this round touches engine guidance, not the validator set).
