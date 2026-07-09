# Argument Benchmark — calibration round (proposal, GATED on a real run)

**Status:** ✅ **VALIDATED 2026-06-11 — gate satisfied; ready to merge.** *(Was: Proposal, gated on a benchmark convergence run — the behavioral change has no mechanical `--check-all` gate, so correctness is established by running the benchmark and scoring.)*

> **Vocabulary migration note (2026-07-09, GT schema v0.2.0).** This record documents the
> 2026-06-11 rule-2a calibration round in the **pre-split vocabulary**, when the Step-9 verdict
> enum was `SOUND / UNCONVENTIONAL-BUT-EFFECTIVE / UNSOUND`. Under the warrant/premise split
> (spec `apo-argument-validity-premise-split`), read every historical verdict token below by the
> mapping `SOUND → WARRANTED`, `UNCONVENTIONAL-BUT-EFFECTIVE → UNCONVENTIONAL-BUT-WARRANTED`,
> `UNSOUND → UNWARRANTED`. The rule-2a FM-A10 evaluability defeat is **unchanged** — only the token
> name changed (the defeat now yields `UNWARRANTED`). This historical record is **not re-scored**.
> The M1 vocabulary migration itself is gated on a fresh convergence run before merge — see
> **§M1 warrant/premise split (2026-07-09)** at the end of this doc.

Run complete: Opus + Sonnet blind runs, scored in a separate pass (outputs in gitignored `evals/results/run-20260611-*`).
- **Criteria 1 / 2 / 4 — PASS (converged).** `policy-brief-uncompared` flips SOUND→UNSOUND via the rule-2a evaluability defeat (BP5+OB3, FM-A10). `ppi-one-size-fits-none` stays SOUND with public-safety scored **OB5** and the carve-out correctly **not** firing. UNSOUND is reached *through* rule 2a, not a forced Must-Fix — proven by `ppi` staying SOUND despite a Must-Fix code firing.
- **Criterion 3 — 12/13 sweep fixtures clean.** The sweep surfaced rule 2a **over-firing** on `andreessen-techno-optimist-manifesto` (a strawman "the only alternative is Communism" foil misread as *zero* comparison). **Fixed in this branch** by tightening the scope guard — naming *any* alternative, even a strawman/weak foil, = partial discharge → soft spot; only *wholly-absent* comparison defeats — plus an anti-gaming clause (a merely decorative foil can still be Unsound via the general evaluability test, not the AT3 auto-trigger). Re-validated under the narrowed engine: andreessen's rule-2a auto-defeat is now blocked, while `policy-brief-uncompared` and `op-ed-warrant-leap` stay UNSOUND.
- **andreessen caveat:** its residual UNSOUND(opus)/UBE(sonnet) is recall on a **high-recognition, corroborate-only** fixture (per CORPUS.md); its GT4–GT7 stay **provisional**. Not a gate blocker.
- The narrowing was **cross-vendor adjudicated** (Gemini + GPT-5.5 both ratified the diagnosis and the fix).

Roadmap: `ROADMAP.md` → Nonfiction Argument Engine → Benchmark Suite, "Next round" item 2 (done; item 1 run-confirmed).

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

> For an argument whose C0 is a **recommendation to act (AT3)**, the comparative dimension is *constitutive of the claim, not peripheral to it* — a reader cannot evaluate "do Y" without "rather than the alternatives that target the same goal." So when an AT3 recommendation discharges *none* of its comparative burden (BP5 primary + OB3, no funding mechanism), the recommendation is **not evaluable as a recommendation** — a defeat under **decision test two (Evidence-evaluability)**, since the comparative case *is* the support a reader must assess (the claim stays statable, so it is *not* a Claim-accessibility / test-one failure) — and the verdict is **Structurally Unsound** (FM-A10).

Why this is a carve-out and not an override of the default-to-SOUND discipline:

- **It satisfies rule 2's own criterion** ("the reader cannot … test the argument"), rather than bypassing it. The comparison *is* the test for a recommendation.
- **It is scoped to AT3 recommendations only** — descriptive/explanatory/interpretive theses are untouched; rule 2 stands unmodified for them.
- **It preserves the anti-over-firing guard (rule 4)** via an explicit *wholly-absent vs. partially-discharged* line: a recommendation that engages even one alternative thinly stays a Should-Fix soft spot in a sound argument. Only the *zero-comparison* recommendation is a defeat.
- A matching one-line note is added at the Step 9 "Final Diagnostic Question" so the evaluability test returns "no" for this case.

This aligns the engine with the fixture's pre-registered key; it changes verdict behavior for **every** argument-shaped run, which is exactly why it is gated.

## Validation gate — DO NOT MERGE until this passes

The deterministic gates pass (`argument-groundtruth-check` on both fixtures, `--check-all`, `argument-spine --self-test`, `build-codex --self-check`), but they validate *contract hygiene*, not the behavioral change. Before merge, run the benchmark and score per `RUN-PROTOCOL.md`, ideally multi-model per the convergence protocol, and confirm **all** of the criteria below.

> **Harness note (do not skip).** `policy-brief-uncompared` (criterion 1) and `op-ed-warrant-leap` / `personal-essay-narrative-arg` (criterion 3) are **stored synthetic fixtures** with no `SOURCES.md` recorded hash, so `evals/fixtures/argument-benchmark/run.sh` **SKIPs** them (`SKIP … no recorded hash in SOURCES.md`). Run those through **RUN-PROTOCOL Step 1's stored-fixture path** — feed each fixture's `fixture.md` verbatim to the blind runner — rather than expecting `run.sh` to cover them. `run.sh` covers only the cached-corpus fixtures. A runner who only invokes `run.sh` will get green output while never exercising the fixture this round exists to fix.
>
> **On pass, record provenance.** `run.sh` writes model outputs to the gitignored `evals/results/`, so a pass leaves no durable artifact. On a passing run, amend this doc's **Status** (and ROADMAP "Next round") with the run date, the model configs used, and the per-fixture verdicts/scores — the house never-fabricate-calibration-status discipline cuts both ways: a "validated" claim at merge time must be auditable later.

1. **`policy-brief-uncompared` flips SOUND → UNSOUND** (matches GT7), with BP5 primary + OB3 named and the comparative-burden discriminator.
2. **`ppi-one-size-fits-none` does NOT regress:** GT3 strongest = the fairness/discretion text-internal objection (public-safety scored as decoy / OB5 if mis-picked), and the verdict **stays SOUND** — the rule-2a carve-out must **not** fire here (ppi's C0 is a *critique*, not an AT3 recommendation; and it engages the standardization alternative, so even read charitably its comparative burden is *partially discharged*). A run that flips `ppi` to UNSOUND means the carve-out is over-scoped — fix before merge. *(Note: the GT3 decoy/OB5 half is authoritative; the "stays SOUND" half rests on GT7, which `ppi`'s `groundtruth.md` still marks **PROVISIONAL** pending second-editor confirmation — treat it as the expected direction, not a hard oracle, and confirm the key is ratified at scoring time.)*
3. **No verdict regression across the other ~14 fixtures** — especially: competent recommendations that *do* weigh alternatives stay SOUND; sound non-recommendation arguments (`federalist-10`, `douglass-fourth-of-july`, `coates-case-for-reparations`, `modest-proposal-satire`, the unconventional-but-effective set) are unaffected; `op-ed-warrant-leap` keeps its Should-Fix/Must-Fix calibration (it is a causal-warrant case, not an uncompared recommendation).
4. **Severity-floor / Step-9 interaction is coherent** — the carve-out reaches UNSOUND *through* rule 2a's evaluability defeat, not by letting any Must-Fix force UNSOUND (which would re-introduce over-firing).

If 1 passes but 2 or 3 regress, narrow the carve-out's trigger (tighten "wholly undischarged") before merge. If the run shows #1's decoy still captured, apply the §Finding-1 reinforcement.

## Files

- `dialectical-clarity.md` — rule **2a** (the AT3 uncompared-recommendation carve-out) + the Step-9 evaluability-test note. (Engine edit; gated.)
- `changelog.d/argument-engine-uncompared-recommendation.md` — the fragment for the rule-2a behavior change (in the PR, not deferred to the merge commit).
- Ground truth unchanged — `policy-brief-uncompared` GT7 already says UNSOUND and `ppi` GT3 already names the decoy; the keys encode the targets, the engine is being brought into line with them.
- No validator/schema change; no count bump (this round touches engine guidance, not the validator set).

---

## §M1 warrant/premise split (2026-07-09)

**Increment:** move 1 of the argument-taxonomy re-grounding (spec `apo-argument-validity-premise-split`, v0.4). Renames the Step-9 verdict axis to the warrant vocabulary and adds the flag-only GT8 premise-plausibility surface (Argument Benchmark GT schema v0.2.0). Verdict remap: `SOUND → WARRANTED`, `UNCONVENTIONAL-BUT-EFFECTIVE → UNCONVENTIONAL-BUT-WARRANTED`, `UNSOUND → UNWARRANTED`. The FM-A10 rule-2a calibration (documented above) is preserved exactly — only the token name changed.

**Mechanical acceptance — ✅ PASS (2026-07-09; re-verified after the Fable-5 three-lens review fold, same day).**
- A Fable-5 review panel (anchor/parity, conceptual/firewall, adversarial/edge-case) over spec v0.4 + the built branch found 2 P1 + 8 P2 (+P3s), all folded: legacy verdict tokens swept from the fixture scoring prose / README / run.sh prompt / CORPUS.md; the GT8 registered path hardened from leading-token-only to a strict contract (field↔row id agreement both directions, bolded-id rows matched, exactly-5-cell rows, full-match flag enum, token boundaries, all three retired GT7 encodings rejected as residue); rule-1/Severity-definition Hard-Gate-vs-Must-Fix conflation fixed behavior-preservingly; `ground` added to the role enum; ownership boundary added to the template; second-editor packet flagged stale pending regeneration. Spec bumped to v0.5.
- `argument_groundtruth.py --self-test`: PASS (37 arms, incl. retired-label + retired-token + all-three-retired-encodings rejection, present-but-unparseable-GT7 ERROR, `NONE_REGISTERED (provisional migration default)` acceptance, missing-GT8 rejection, malformed-flag rejection, truth-token-in-flag rejection, field↔row agreement both directions, bolded-row acceptance, 5-cell strictness, token-boundary and heading-number-boundary arms, the moon-cheese `WARRANTED + P1` two-flag acceptance with a lowercase "true or false" Firewall-boundary that passes, and combined `GT4–GT8` heading coverage).
- `validate.sh --check-all`: PASS — all 16 argument-benchmark fixtures `ok`; `--self-test-all`, `check-mirror` (both `scripts/` and `plugins/apodictic/scripts/` mirror pairs byte-identical), `schema-coverage`, and `validator-conventions` all green.
- `build-codex.mjs --self-check` / `build-antigravity.mjs --self-check`: PASS. `release-generate --check`, `assemble-changelog --check`, `check-status-drift`, `check-inventory-parity`: PASS.
- Corpus GT8: 16/16 `NONE_REGISTERED` (10 as `provisional migration default`); the registered-flag path is exercised by the parser's moon-cheese self-test, not the corpus (the corpus is real published nonfiction — a logic-toy would never be scored/convergence-run).

**Behavioral acceptance — ⏳ PENDING (pre-merge gate; operator/engine-gated).** The vocabulary migration has no mechanical `--check-all` gate on *verdict behavior*; correctness of the remap is established by a fresh two-independent-engine-run convergence pass over the migrated corpus (per `RUN-PROTOCOL.md`), confirming:
- every fixture's GT7 behavior matches the old→new mapping;
- `policy-brief-uncompared` remains `UNWARRANTED` **via FM-A10 rule 2a** (BP5 primary + OB3, comparative-burden discriminator named) — not via a generic "premise false" or forced Must-Fix;
- FM-A10 guardrails do not regress (partial-discharge stays `WARRANTED` + Should-Fix; strawman alternatives not misread as zero comparison; decorative foils route through the general evaluability test);
- positive controls do not regress (form-dependent traps stay advisory under `UNCONVENTIONAL-BUT-WARRANTED`);
- premise flags never become stealth verdict defeats (a flagged premise can coexist with `WARRANTED`).

Record the run (model configs, per-fixture warrant verdicts, GT8 observations, pass/fail) here before merge. Do not claim validation from gitignored outputs alone.
