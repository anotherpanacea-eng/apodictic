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
- `argument_groundtruth.py --self-test`: PASS (40 arms, incl. retired-label + retired-token + all-three-retired-encodings rejection, present-but-unparseable-GT7 ERROR, `NONE_REGISTERED (provisional migration default)` acceptance, missing-GT8 rejection, malformed-flag rejection, truth-token-in-flag rejection, field↔row agreement both directions **as a multiset** — a doubled expected id or two conflicting detail rows for one premise id are rejected before the coverage compare (PR-review fold `fdb848f`), bolded-row acceptance, 5-cell strictness, token-boundary and heading-number-boundary arms, the moon-cheese `WARRANTED + P1` two-flag acceptance with a lowercase "true or false" Firewall-boundary that passes, and combined `GT4–GT8` heading coverage).
- `validate.sh --check-all`: PASS — all 16 argument-benchmark fixtures `ok`; `--self-test-all`, `check-mirror` (both `scripts/` and `plugins/apodictic/scripts/` mirror pairs byte-identical), `schema-coverage`, and `validator-conventions` all green.
- `build-codex.mjs --self-check` / `build-antigravity.mjs --self-check`: PASS. `release-generate --check`, `assemble-changelog --check`, `check-status-drift`, `check-inventory-parity`: PASS.
- Corpus GT8: 16/16 `NONE_REGISTERED` (10 as `provisional migration default`); the registered-flag path is exercised by the parser's moon-cheese self-test, not the corpus (the corpus is real published nonfiction — a logic-toy would never be scored/convergence-run).

**Behavioral acceptance — ✅ PASS-WITH-CAVEATS (convergence run 2026-07-09; independent Opus scorer).** Two independent blind engine runs over a decisive 4-fixture subset, cross-vendor.

- **Engines (model configs):** Engine 1 = **Fable** (Claude Code subagent, blind — given only the fixture text + `dialectical-clarity.md`, never the keys). Engine 2 = **Codex 5.6** (`gpt-5.6-sol`, high reasoning, Codex CLI 0.144.0, `codex exec` in an isolated read-only dir containing only the input + audit reference). Referenced fixture (andreessen) reconstituted from the out-of-tree source cache, SHA-verified against `SOURCES.md` (`1ba70593…`); the 3 synthetic fixtures are text-in-repo. Blind-run + separate-scorer discipline per `RUN-PROTOCOL.md` §Principles.
- **Fixture selection (each witnesses an M1 acceptance bullet):** `policy-brief-uncompared` (UNWARRANTED-via-FM-A10, the marquee), `op-ed-warrant-leap` (UNWARRANTED), `personal-essay-narrative-arg` (UBW positive control), `andreessen-techno-optimist-manifesto` (the FM-A10 strawman-guard non-regression witness — the exact fixture that over-fired in the 2026-06-11 round).

**Per-fixture warrant verdicts (Fable / Codex 5.6 · key target):**

| Fixture | Fable | Codex 5.6 | Key GT7 | FM-A (both) | Result |
|---|---|---|---|---|---|
| policy-brief-uncompared | UNWARRANTED | UNWARRANTED | UNWARRANTED | FM-A10, BP5+OB3, BURDEN | ✅ converged, on target |
| op-ed-warrant-leap | UNWARRANTED | UNWARRANTED | UNWARRANTED | FM-A10 (both) | ✅ verdict on target (locus caveat below) |
| personal-essay-narrative-arg | WARRANTED | UNCONVENTIONAL-BUT-WARRANTED | UBW | — | ✅ both non-UNWARRANTED (Q7-control latitude: WARRANTED/UBW both pass) |
| andreessen | UNCONVENTIONAL-BUT-WARRANTED | WARRANTED | WARRANTED (pinned) | FM-A20/OB5 | ✅ both non-UNWARRANTED; Codex hit the pin; rule-2a guard **held** on both |

**M1 acceptance — bullet by bullet:**
- **(a) GT7 old→new mapping preserved — PASS.** Verdict *sign* perfectly reliable: both failure-bearing fixtures → UNWARRANTED on both engines; both warranted-family fixtures → non-UNWARRANTED on both engines. All three tokens exercised and correctly produced. The two within-family token variances (Fable-B WARRANTED, Fable-D UBW) are inside documented Q7-form-control / recall latitude; neither is the UNWARRANTED trap direction.
- **(b) policy-brief UNWARRANTED via FM-A10 (BP5 primary + OB3 + comparative discriminator) — PASS (both engines)**, reached through the rule-2a evaluability defeat, not a forced Must-Fix or "premise false."
- **(c) FM-A10 guardrails do not regress — PASS.** Direct witness: on andreessen, Fable explicitly recorded "foils = partial-discharge → the zero-comparison defeat is NOT triggered," and both engines kept it warranted-family. The 2026-06-11 over-fire stays fixed under the new vocabulary, cross-vendor. (Corroborating: the op-ed genuinely names zero remedy-alternatives, so FM-A10 firing *there* is correct guard behavior, not an over-fire.)
- **(d) Positive controls do not regress — PASS-WITH-CAVEAT.** Neither engine returned UNWARRANTED on the control (hard regression avoided); Fable clean (traps → Could-Fix advisory). Caveat: Codex softened on B — fired FM-A17/WR0/BP2 on the narrative-argument control (the over-diagnosis this fixture guards against); noted-but-not-cleanly-downgraded, verdict still held warranted-family.
- **(e) Premise flags never become stealth verdict defeats — PASS (strongly witnessed).** Both engines registered P1–P5 on andreessen and still returned warranted-family verdicts; on A/C the flags coexist with a structurally-driven (FM-A10) UNWARRANTED. Firewall spot-check of the actual flag rows (orchestrator, 2026-07-09): every registered flag carries an explicit Firewall boundary ("the audit does not adjudicate the figures' truth"); a scan for a truth token (TRUE/FALSE/PROVEN/…) in any flag cell found **none**. No flag flipped or drove a verdict.

**Verdict (independent Opus scorer): PASS-WITH-CAVEATS — the SOUND→WARRANTED migration is behavior-preserving; safe to un-draft #192.** A FAIL would require a warranted↔unwarranted boundary flip, a flag-driven stealth defeat, or a positive control going UNWARRANTED — none occurred.

**Caveats / known-issues (orthogonal to the migrated axis — identical under the old vocab; not merge blockers):**
1. **op-ed-warrant-leap shared locus mis-rank** — both engines diagnosed it as FM-A10/BURDEN (uncompared AT3 ban) rather than the key's FM-A6/WARRANT (causal warrant leap). Both *did* fire WR0 but subordinated it. The op-ed genuinely has two defeaters (a bare uncompared ban + a causal leap), so this is part rule-2a FM-A10 over-capture, part key ambiguity. Follow-up: rule-2a-scope review / consider GT2-as-set for this fixture. The verdict (UNWARRANTED) is correct; only Q2-locus/Q3-zone diverge. **→ RESOLVED 2026-07-11 (convergence re-run PASSED, 4/4 cross-vendor) — see §M1-followup (warrant-leap primacy) below: fixed engine-side via rule 2a's primacy-override + a GT2 key sharpening; the GT2-as-set option was *rejected*.**
2. **andreessen** recognition = yes on both engines (recall-susceptible, GT4–GT8 provisional per CORPUS.md); Fable UBW is failure-mode-(a) under the strict key but within established recall latitude and strictly better than the ratified 2026-06-11 baseline (Opus=UNSOUND/Sonnet=UBE).
3. **GT8 over-flagging** — engines registered premise flags where the corpus default is `NONE_REGISTERED`; flags did not drive verdicts and the Firewall held (see (e)). GT8 remains a non-scored contract surface in M1.
4. **Scope:** decisive 4-fixture subset, not all 16. Judged sufficient for *this* gate by the scorer: the change is a token rename + FM-A10 rule-2a preserved exactly + additive GT8, altering no scoring/code logic; mechanical acceptance already showed 16/16 fixtures green; the subset spans all three verdict tokens and both verdict-family boundaries, produced by two independent engines. Full-16 exhaustive sweep remains an available extension.

Run outputs are in the session scratchpad (gitignored); this record is the durable, self-contained artifact.

## §Matched clean/broken pairs (2026-07-09)

**Increment:** the matched-pairs specificity retrofit (spec `apo-argument-benchmark-matched-pairs`, v0.2). The two synthetic planted-defect fixtures become matched clean/broken pairs: `op-ed-warrant-leap` and `policy-brief-uncompared` each move to `<pair>/broken/` (history-preserving) and gain a derived `clean` twin authored by an enumerated minimal repair. Adds parser **Check 7** (matched-pair provenance), the `--check-all` two-depth corpus glob + orphan-twin completeness pass, the scripted repair-diff acceptance gate, and the §Step 4 matched-pair convergence class. Scoring is unchanged (protocol-level only).

**Mechanical acceptance — ✅ PASS (2026-07-09; re-run green after the Codex #196 fold, 2026-07-11).**
- `argument_groundtruth.py --self-test`: PASS — the 11 base Check-7 arms (paired broken/clean accepted; `Paired-with: n/a` on a broken member rejected; `Paired-with` without `Matched-pair member` rejected; non-complement `clean↔.../clean` rejected; bad member token rejected; `cleanX` boundary near-miss rejected; legacy no-fields fixture accepted; clean member with missing/N/A repair record rejected; clean member with a substantive (non-positive-control) GT2 rejected; `Paired-with` slug contradicting the key's own `Fixture slug` pair rejected) **plus the 10 Codex #196 hardening arms** (5 Check-7 + 5 repair-diff, below), no existing arm removed or weakened.
- `validate.sh --check-all`: PASS — all **18** argument-benchmark GT files `ok` (14 flat + the 4 nested pair members printed by `<pair>/<member>` slug); the **repair-diff gate now runs in `--check-all`** (both pairs `ok`, was prose-only pre-fold); round-record conformance `ok`; the two-depth glob visits both depths and the orphan-twin + repair-diff gates fail loudly when a member's `fixture.md` is removed (verified in the worktree, restored).
- `check-mirror` (both `scripts/` ↔ `plugins/apodictic/scripts/` mirror pairs byte-identical), `assemble-changelog --check`, `schema-coverage`, `validator-conventions`: all green.
- Each clean twin passed the anti-gaming red-team (rule-2a general-evaluability standard) before registration — recorded in each clean key's Notes.

**Codex #196 diff-review fold — ✅ (2026-07-11).** The behavioral gate had already passed (below); the diff review was folded before merge, refreshed onto current `main` (adopting #197's structural GT-validator refactor):
- **[BLOCKING] clean-member GT2 marker** was a body substring (`"positive control" in gt2_body.lower()`) — a substantive GT2 that merely *mentioned* the phrase passed. Now a **structural leading-line match** on the GT2 section's first non-blank line against the canonical `N/A — positive control` marker (rule 6ii).
- **[P1] repair-diff gate wired.** The scripted `diff broken/fixture.md vs clean/fixture.md` (pure-additive, 0 deletions, hunks 1:1 with the enumerated loci) is now a real `--repair-diff` mode run in `--check-all`, not prose in this doc. Loci are parsed by a structural line-walk (no `\s*` block regex).
- **[P1] nested opt-out closed.** A file physically under `<pair>/{clean,broken}/` may no longer opt out of Check 7 by dropping its pairing fields; the directory (`member_hint`, from the file path) is the source of truth (rule 1).
- **[P2] regex/structural holes.** `_FIXTURE_SLUG_PAIR_RE` end-anchored (suffix garbage no longer truncate-parses); the orphan-twin check now requires **both** `fixture.md` and `groundtruth.md` per member and twin; repair-loci parsed structurally (empty/blank line cannot swallow the next locus).
- **Repair-diff (durable record):** each pair's `broken/fixture.md → clean/fixture.md` diff is **pure-additive** (0 deletions) with exactly **2 insertion hunks**, mapping 1:1 to the two enumerated `Base text + repair record` loci:
  - `op-ed-warrant-leap`: locus 1 (causal warrant: rate/denominator + confounders); locus 2 (remedy warrant: proportionality vs lighter remedies).
  - `policy-brief-uncompared`: locus 1 (comparative burden: service-investment comparison); locus 2 (feasibility burden: cost + funding mechanism).

**Behavioral acceptance — ✅ PASS (recorded 2026-07-11; blind, cross-vendor; raw outputs gitignored/prior-session, this table is the durable record).** The pair delta has no mechanical `--check-all` gate on *verdict behavior*; correctness is established by a recorded convergence run over both pairs — **4 members × 2 model configs (Fable + Codex 5.6) = 8 blind runs**, separate runner sessions per member, neutral labels, no twin disclosure (synthetic — no fetch needed):

| Pair | Member | Fable | Codex 5.6 | Target | Pair delta |
|---|---|---|---|---|---|
| op-ed-warrant-leap | broken | UNWARRANTED · WR0 / FM-A6 (warrant leap) | UNWARRANTED · WR0 / FM-A6 | UNWARRANTED | discriminator **fires** ✓ |
| op-ed-warrant-leap | clean | WARRANTED · only FM-A8 (advisory Should-Fix) | WARRANTED · only FM-A8 | WARRANTED | discriminator **withheld** ✓ |
| policy-brief-uncompared | broken | UNWARRANTED · BP5 / FM-A10 (uncompared burden) | UNWARRANTED · BP5 / FM-A10 | UNWARRANTED | discriminator **fires** ✓ |
| policy-brief-uncompared | clean | WARRANTED · only FM-A15 (advisory Should-Fix) | WARRANTED · only FM-A15 | WARRANTED | discriminator **withheld** ✓ |

**8/8 on target, cross-vendor.** Both broken members converge UNWARRANTED with the planted discriminator fired; both clean twins converge WARRANTED with **no registered trap** (WR0/FM-A6 for op-ed, BP5/FM-A10 for policy) firing — the only mentions are single **advisory Should-Fix** flags (op-ed clean = FM-A8; policy clean = FM-A15) that neither reach Must-Fix nor defeat the verdict, exactly the latitude the positive-control rule allows. The **pair delta holds per config** for both pairs (the discriminator is a structural failure in the broken run and absent in the clean run, on the same prose). The existing `ppi-one-size-fits-none` ↔ `op-ed` contrast is preserved (ppi stays WARRANTED; the retrofit adds the family gradient's third corner without perturbing the other two). No Q7 trap fired on either clean member.

---

## §M1-followup — warrant-leap primacy (2026-07-10)

**Status:** ✅ **VALIDATED — convergence re-run PASSED (2026-07-11); ready to merge.** Resolves M1
caveat #1 (the `op-ed-warrant-leap` shared locus mis-rank). Branch `feat/argument-warrant-leap-primacy`
(rebased onto `main` after #192 merged).

**Convergence re-run — ✅ PASS (2026-07-11; independent, blind, cross-vendor).** Two independent engines
(Fable + Codex 5.6 / `gpt-5.6-sol`, isolated read-only, given only the fixture text + this branch's
`dialectical-clarity.md`) over the discriminating pair — the override witness (`op-ed-warrant-leap`) and its
negative test (`policy-brief-uncompared`):

| Fixture | Fable | Codex 5.6 | Target | Override |
|---|---|---|---|---|
| op-ed-warrant-leap | UNWARRANTED · **WARRANT / FM-A6** primary (FM-A10 subordinate) | UNWARRANTED · **WARRANT / FM-A6** primary (FM-A10 subordinate) | FM-A6 primary | **fires** ✓ |
| policy-brief-uncompared | UNWARRANTED · **BURDEN / FM-A10** primary | UNWARRANTED · **BURDEN / FM-A10** primary | FM-A10 primary | correctly **withheld** ✓ |

4/4 on target, cross-vendor. The override promotes the causal warrant leap to primary on the op-ed (both engines
cited the L2-presupposes-L1 dependency) and the negative test holds on policy-brief (both engines: the localized
emissions warrant gap is a benefit-subclaim soft spot, not a MISSING causal leap on C0, so FM-A10 stays primary).
**Verdict unchanged (UNWARRANTED) everywhere** — only the primary locus/pattern moves, and only on the co-defeat
case. No regression: the ordinary uncompared-proposal stays FM-A10-primary. Run outputs in the session scratchpad
(gitignored); this table is the durable record.

**Finding restated.** On `op-ed-warrant-leap`, both blind engines (Fable + Codex 5.6) returned the correct
verdict (UNWARRANTED) but ranked **FM-A10 / BURDEN / the uncompared ban** as the *primary* locus, subordinating
the key's registered primary **FM-A6 / WARRANT / WR0** (the causal warrant leap). Both *fired* WR0; both
mis-ranked it. Only the Q2 failure-locus and Q3 objection-zone diverge — the verdict is right on both.

**Root cause (not "salience").** The engine already owns a primacy rule — "name the *first* defeated test"
(rule 2 / the Final Diagnostic Question), against the fixed decision-test order. Rule 2a plants the FM-A10
defeat at **decision test two (Evidence-evaluability)**; the causal warrant leap is a **test three
(Warrant-recoverability)** defeat. So "first defeated test" *currently resolves to FM-A10* — the generic table
order ranks the comparison break ahead of the deeper warrant break. There was no gap for salience to fill; the
tie-break existed and resolved *against* FM-A6.

**Decision.**
- **Sub-question 1 (rule-2a FM-A10 over-capture?) — YES, on *primacy* (not the verdict).** Fix the engine.
- **Sub-question 2 (key too strict → GT2-as-set?) — NO.** Freeze the registered primary (FM-A6); *sharpen* the
  key. A co-equal *FM-A6-OR-FM-A10* set is **rejected** under the GT-as-a-set discipline: guard #1 (a member
  must be structurally *prior*, not merely salient/reliably-found — FM-A10 is *downstream* of the causal
  warrant, since the remedy comparison L2 presupposes the causal warrant L1, per GT6) and guard #4 (no
  expansion that flips a fixture to "pass" by blessing a run's ranking error — a co-equal set would let a
  warrant-leap-*blind* run score Q2 = 3, dissolving the SUPPORT-vs-WARRANT discriminator this fixture isolates).
- **Sub-question 3 (ppi ↔ op-ed pairing holds?) — YES, and it is *sharpened*.** ppi is a *critique* (not AT3),
  so rule 2a never fires on it; `policy-brief-uncompared` is an AT3 rec whose problem-warrant is fine and whose
  *sole* defeat is the missing comparison (**no co-present WR0 leap**), so it keeps FM-A10 primary. The
  primacy-override fires **only** on a co-present test-three MISSING causal/diagnostic warrant leap — exactly
  the discriminator that separates op-ed (WARRANT-primary) from policy-brief (BURDEN-primary). No verdict moves
  (op-ed / policy-brief UNWARRANTED; ppi WARRANTED).

**Changes (this branch).**
- **Engine** — `dialectical-clarity.md` rule 2a gains a **primacy-override**: when the FM-A10 zero-comparison
  defeat co-occurs with a **MISSING** causal/diagnostic WR0 leap on C0, the warrant leap is the primary
  structural break (FM-A6) and FM-A10 is co-reported as subordinate (rationale: L2 presupposes L1). A negative
  test keeps the ordinary Uncompared-Proposal case FM-A10-primary. Cross-pointers added at the Step-9 Final
  Diagnostic Question ("name the first defeated test" / "name which step breaks first") / the operative-test
  FM-A10 note. *Verdict logic unchanged everywhere; only ranking, only
  for the co-defeat case.*
- **Key** — `op-ed-warrant-leap/groundtruth.md` GT2: `Primary failure layer: WARRANT` frozen; FM-A10 → BP5
  registered as a **subordinate** second defeater (its objection left *uncoded* so it cannot collide with GT3's
  confounding-zone central-objection code); a split **Q2 primacy boundary** — a run that *surfaces* WR0/the
  WARRANT locus but subordinates it caps at **Q2 = 2** (mis-ranked discriminator), while a run that *omits* the
  causal warrant leap is **Q2 = 0** (miss; Deficit-Lock — no laundering the locked locus miss into partial
  credit).
- **Changelog** — `changelog.d/argument-engine-warrant-leap-primacy.md`.
- Spec-reviewed (Opus swarm: 3 P1 + 3 P2, all folded — the false "salience vacuum" premise corrected to the
  decision-test-order override, the "omits → partial" Deficit-Lock breach split out, the OB3 referent collision
  removed).

**Validation.**
- **Mechanical (necessary, NOT sufficient).** `argument-groundtruth-check` green on op-ed + policy-brief + ppi;
  `--check-all` (mirrors regenerated + `check-mirror`, `assemble-changelog --check`,
  `argument-carve-behavior-preservation`) green. **No AGG_VALIDATOR covers the ranking flip** —
  `argument-groundtruth-check` is shape-only and there is **no run-vs-key scorer**. Green `--check-all` attests
  key well-formedness + mirror/changelog hygiene only; it is *not* non-regression evidence for the behavioral
  change.
- **Behavioral gate (HARD — the real merge blocker).** ≥2 cross-vendor blind runs (RUN-PROTOCOL disjoint
  roles), independently scored, must show **all three**:
  1. **op-ed-warrant-leap** now ranks **FM-A6 / WR0 / WARRANT primary** (FM-A10 co-reported subordinate);
     verdict UNWARRANTED; the mis-rank scores **Q2 = 2** only if WR0 was surfaced.
  2. **policy-brief-uncompared** keeps **FM-A10 / BP5 / BURDEN primary**; verdict UNWARRANTED (no regression).
  3. **ppi-one-size-fits-none** stays **WARRANTED**; GT3 = the fairness/discretion text-internal objection.
  Record per RUN-PROTOCOL Step 5. On pass, flip this Status to VALIDATED with the run date + model configs +
  per-fixture ranks. **Not runnable in the offline build sandbox** (this section was authored there).
- **Codex PR gate** before merge; no merge without operator sign-off.
