# APODICTIC Development Editor Changelog

All notable changes to the APODICTIC Development Editor (APDE) framework will be tracked in this file.

This changelog started at `v0.4.4.1` on **2026-02-13**.  
Historical backfill entries for `v0.4.4` and `v0.4.3` were added the same day from local file history and release notes.

## v2.9.0 - 2026-07-12

### Validators — Krippendorff's α (`agreement-alpha`)

A new pure-stdlib validator, `scripts/agreement_alpha.py`, computes **Krippendorff's α** inter-rater reliability over a tidy `rater,unit,value` CSV — the mechanical half of the benchmarks' *agreement-as-license* promotion workflow, shipped **before** any human panel data exists so the M2 round is analysis-ready and α is computed by audited, self-tested code rather than an ad-hoc notebook (and shared with the fiction benchmark's M2b, which specifies no calculator of its own). Run via `validate.sh agreement-alpha <ratings.csv> [--metric nominal|ordinal]`. It builds the coincidence matrix (each within-unit ordered value pair contributing `1/(m_u−1)`; units with `<2` values contribute nothing), then `α = 1 − D_o/D_e` under the **nominal** (`δ²=0/1`) or **ordinal** (Krippendorff's cumulative-marginal metric) difference function. Contract, pinned: a **required `rater,unit,value` header** (missing/wrong → ERROR), stdlib-`csv` quoting, blank `value` = missing, a **malformed row** (wrong column count or empty `rater`/`unit`) → ERROR naming the line number (never silently skipped); `D_e=0` (a constant column) → `alpha=UNDEFINED (D_e=0)` + WARN, treated as **not clearing** any threshold. The **bootstrap 95% CI** resamples **UNITS** with replacement — `≥1000` resamples (default 1000; `--resamples` may only raise the floor), the **Hayes & Krippendorff (2007)** unit-level scheme — from a **fixed default seed** (`--seed` override) so two auditors reproduce the same interval byte-for-byte; licensing is on the **CI lower bound**, not the point estimate (the small-n false-promotion guard). The **panel floor** is enforced mechanically: `panel-licensed` requires a **≥3-editor panel** (docs/argument-benchmark-spec.md §GT schema), so a run with fewer than three **participating** editors (those carrying `≥1` non-missing rating — an all-blank column is a listed-but-absent editor, not a rating one) still computes and prints α for information but returns an explicit **non-clearing FAILED (exit 2)** with no `OK:` line, which the promotion path rejects; a two-rater high-agreement dataset can no longer back into a license. Its hermetic `--self-test` locks the arithmetic to hand-derived values — Krippendorff's published worked example (nominal **α = 0.691**, n = 26), a fully worked tiny nominal case (**8/15**), an ordinal-beats-nominal ordered example (**0.700** vs **0.4545**), perfect agreement (**1.0**), systematic disagreement (**−0.5**), the `D_e=0` UNDEFINED path, a deterministic seeded-CI regression lock, the missing-header / malformed-row / single-rater / single-unit ERROR arms, and the panel-floor arms (a two-rater run prints α but is non-clearing; a ≥3-editor panel licenses; the reviewer's 100-unit two-disagreement high-α repro is rejected; an all-blank third editor does not count toward the floor). Registered on all five surfaces (AGG token, dispatcher case with `--self-test` + python3-degrade path, help line, byte-identical `scripts/` ↔ `plugins/apodictic/scripts/` mirror, this fragment); no `--check-all` corpus block — panel ratings live outside git. No hard-coded validator count is introduced (`AGG_COUNT` stays derived). Method sources: Krippendorff, K. (2011/2013), *Computing Krippendorff's Alpha-Reliability*; Hayes, A. F., & Krippendorff, K. (2007), *Answering the Call for a Standard Reliability Measure for Coding Data*, Communication Methods and Measures 1(1), 77–89.

### Nonfiction Argument Engine — Reliability Ledger (Agreement-as-License, GT schema v0.3.0)

The Argument Benchmark's ground truth now carries its trust distinction as machine-checked data rather than prose. Each fixture's Provenance block gains a required **Reliability ledger** line assigning every GT anchor a **status** (`authoritative` / `provisional` / `panel-licensed` / `low-agreement`) and a **decision-use** (`gate` / `confirm` / `report`), and the GT schema bumps to **v0.3.0**. `scripts/argument_groundtruth.py` gains **Check 6**: the ledger group grammar (`GT<a>(–GT<b>)?: <status>, <use>`, `(?![0-9])` boundary-guarded so `GT10` cannot truncate-parse, `|`/`/`-in-value rejected as copied guidance), exact GT1–GT8 coverage (no gaps/overlaps), the enforcement matrix (`gate` requires a licensed status — `authoritative`/`panel-licensed`; `provisional` may only confirm/report; `low-agreement` may only report), and a **stale-heading cross-check** that finally *consumes* the formerly-dead `(PROVISIONAL)` heading bool — a licensed status under a PROVISIONAL-marked heading is an error (the M2-promotion tripwire). A sibling **round-record conformance mode** (`--round-record <record.md> --fixtures-dir <dir>`, wired into `--check-all` over `docs/argument-benchmark-calibration-round.md`) is the one mechanical guard at the run-side attribution seam: every booked `- BOOKED: ENGINE-FAULT <fixture-slug> GT<n>[ OVER-FIRE]` must cite an anchor whose ledger licenses it (`gate`: any booking; `confirm`: only with an explicit `OVER-FIRE` tag — the asymmetric ruling; `report`: none). All 16 registered `groundtruth.md` fixtures migrate (one added ledger line each; the GT8 `(provisional migration default)` parentheticals preserved byte-for-byte; two PD-control Scope sentences corrected to `GT4–GT6 and GT8 are provisional / advisory`), and Checks 1–5 plus the strict GT8 contract are byte-stable. The **convergence criteria are unchanged**; only *attribution* becomes reliability-aware and **asymmetric** — a `confirm`-anchor over-fire stays ENGINE-FAULT (the specificity gate does not soften), while a `confirm`-anchor false-negative downgrades to `key-suspect (ground-truth ambiguity)` and routes to run-blind re-registration or the blind M2 panel, never an engine regression. Promotion α thresholds are **pre-registered** in the spec (Krippendorff's canonical cutoffs: α ≥ .800 → `panel-licensed`, .667 ≤ α < .800 → `provisional`, α < .667 → `low-agreement`; ordinal-weighted for the GT4 sub-scales, nominal for GT2/GT6/GT7; licensed on the bootstrap-CI lower bound), computed by the audited `agreement-alpha` CLI shipped separately. This is the argument-benchmark instantiation of the psychometric frame the fiction benchmark already ships (`scripts/fiction_groundtruth.py`) — inter-rater agreement **licenses** whether a label may gate; it never scores the engine — with a deliberately domain-honest token set (a documentation-only fiction↔argument cross-map, no drift guard). 76 parser self-test arms total (40 inherited from the warrant-split base), 36 new — Check-6, round-record, plus a Codex-#193-review hardening pass: the ledger field is anchored to the exact `- **Reliability:**` label **within the `## Provenance` block** (a near-label like `- **Not Reliability:**` or a misplaced ledger under `## Notes` is rejected, not silently accepted); the `provisional` heading bool is sticky-true across every heading covering a GT anchor (a later duplicate heading cannot clear a `(PROVISIONAL)` marker and evade the stale-heading tripwire); and the round-record BOOKED matcher is claim-broad/validate-strict — house-bold `- **BOOKED:**` is legal, while near-miss dialects (`- **BOOKED** — …`, `- BOOKED:: …`, `- BOOKED* …`, `* BOOKED: …`) are loud errors, never silent skips.

### Argument engine — AGD Move Audit companion (`argument-agd`; Argument_State §10.9)

R3A of the argument re-grounding roadmap — the frontier build: a companion audit that inventories the text's **performative argument moves** — **ASSURING** (authority/certainty in place of support), **GUARDING** (a claim weakened to shrink its commitment), **DISCOUNTING** (an objection anticipated and set aside) — identified **functionally at a transition, not by cue words** (cue lexicons under-determine function: most hedge-cue lemmas also occur as non-cues — Velldal et al. 2012, *Comp. Ling.* 38(2), BioScope, domain-specific; the identification-by-transition posture is analogically scaffolded on Inference Anchoring Theory, Budzynska et al. 2016, a dialogue result whose monological transfer is this audit's own claim, validated by its fixtures). All three moves are **legitimate**; the audit never codes a move for being a move. Each inventoried move is **challenged** with its family's protocol — ASSURING × **STRIP** (purely subtractive: delete the assurance span; does independent support remain? — S&F 9e ch. 5), GUARDING × **COMMITMENT** (**de-hedge-only**: force the text's own claim to its unguarded form, adding no specificity the text lacks; ch. 16's self-sealer test), DISCOUNTING × **ENGAGEMENT** (constructs no text: decoy-vs-strongest reuses Step 6a Test A/B + the R2 `Basis` field by cross-reference, plus a downstream-consequence prong) — under a **total family × challenge × result matrix** (`SURVIVES` / `COLLAPSES` [/`-DECOY`/`-COSTLESS`] / `SELF-SEALS` (GUARDING-only) / `INDETERMINATE` (run-but-unresolved, documented) / `NOT-CHALLENGED` (inventory-only)). GUARDING records carry a `Trajectory` (S&F's disappearing guard). **Candidate diagnoses are flag-only and licensed exclusively by failed function**: `Candidates: NONE` is required on `SURVIVES`/`NOT-CHALLENGED`/`INDETERMINATE` (sole exception: the `Trajectory: DISAPPEARING` whitelist {FM-A16, WR3, BP4}); candidates come from a **derived 62-code namespace** (the Dialectical Clarity codes minus the AT1–AT4 type labels, via `argument_crosswalk`'s scoped registry parse — no fourth hardcoded copy — plus FM-A1–20 from `argument_groundtruth._FM_A_MAX`), carry a **PENDING → CONFIRMED/DECLINED reconciliation contract** (the human editor or a full engine re-run adjudicates; the companion never writes codes outside its §10.9 annotation block, honoring the annotation protocol), and **never enter severity propagation directly**. The audit writes `Argument_State.md` **§10.9** behind a machine-readable **coverage manifest** (declared spans cross-checked against the §2 claim ladder; exclusions with reasons; `Completion: PARTIAL` = WARN, ERROR under `--strict`).

The mechanical gate, `scripts/argument_agd.py` (stdlib, + byte-identical mirror; `validate.sh argument-agd`), enforces: matrix totality; the neutrality firewall both directions (incl. `NOT-CHALLENGED`-carries-no-construction and ENGAGEMENT-constructs-no-text); candidate namespace + reconciliation grammar (`CONFIRMED` requires adjudicator + target ref); the DISCOUNTING cross-ref contract (`COLLAPSES-DECOY` ⇒ a resolving `Displaced strongest:` pointer to §6's STRONGEST OBJECTION; `COLLAPSES-COSTLESS` ⇒ a resolving `Discounted:` grading target; `NOT-INVENTORIED` legal only on `SURVIVES`/`INDETERMINATE`); coverage (records' loci ∈ declared spans; `COMPLETE` ⇒ spans ⊇ C0 + the §2 ladder, degrade-not-fail when §2 is absent); and — with `--source` — **Source-anchor resolution by normalized substring** (whitespace folded, quotes/dashes normalized; paraphrase and elision near-misses FAIL; greenfield — R2's anchors are convention-only and the GT lineage deliberately retired naive substring matching). Registered on all five surfaces (AGG token, dispatcher with `--self-test` + python3-degrade, help line, mirror, this fragment) plus a `--check-all` resolve-and-skip arm over **five worked fixtures** (`evals/fixtures/argument-agd/`: legitimate / abusive-cued / cue-only / **cue-free structural discounting** (the decisive functional-not-lexical case) / ambiguous-INDETERMINATE — original authored prose with stored source, anchors resolved under `--strict`). `Argument_State` schema **stays v0.2.0** (companion subsections do not bump, per the schema's own rule); the §10 initializer enumerations (schema doc + the Dialectical Clarity §8 artifact text, which was already stale at "10.1–10.5") now read 10.1–10.9. No new failure code; no crosswalk change (AGD↔S&F crosswalk entries are R4B's). Sources: Sinnott-Armstrong & Fogelin, *Understanding Arguments* 9e, ch. 3/5/16; Budzynska, Janier, Reed & Saint-Dizier (2016), *Arg. & Computation* 7(1); Velldal, Øvrelid, Read & Oepen (2012), *Comp. Ling.* 38(2) — ACL J12-2005.

### Argument engine — AGD Move Scan consumer (R3B seam; `agd_move_scan` → AGD Move Audit §10.9)

R3B A-1 of the argument re-grounding roadmap — the consumer half of the AGD producer/consumer seam. SETEC's **`agd_move_scan`** surface (shipped in the tagged **v1.124.0** release, `handoff: experimental`, `calibration_status: heuristic`) reports **LOCATED, verbatim-anchored candidate AGD move observations** (family + verbatim span + `paragraph_index` + cue; `cue: null` = cue-free) for an argument-shaped nonfiction passage. APODICTIC now consumes them under the load-bearing ownership rule (**R4A ADR D5: the producer observes, the consumer alone assigns codes**): the scan is a **POINTER, never a finding** — every challenge, result, and diagnosis stays the AGD Move Audit's.

**Consumer surface.** A canonical stdout-forwarding shim `scripts/ai_prose_agd_move_scan.py` (`SURFACE = "agd_move_scan"`, so `discover_shim_surfaces` counts it) routes through SETEC's normalized dispatcher (R2), with the per-surface floor (1.124.0) enforced runtime-side. `sync_setec` re-vendored the projected capabilities manifest (now carrying `agd_move_scan` with its 1.124.0 floor), re-vendored the contract fixtures (adds the `agd_move_scan.json` golden), and repinned `setec-plugin.lock` to the **v1.124.0** release tag. The offline drift gate's CHECK-1 self-consistency now covers the surface, and `tests/setec-contract/test_setec_contract.py` bumps the shim-count floor (11 → 12), maps the surface to its 1.124.0 floor, and adds a **positive runner-path assertion** (routes the vendored golden through `run_supplement`, asserting `results.observations` survives — not mere fixture presence).

**Consumption contract (Layer-1 scan pre-pass).** The AGD Move Audit's Layer 1 gains a bounded pre-pass: if `agd_move_scan.json` is present in the run folder, read `results.observations` **before** building the move inventory; absent or malformed ⇒ proceed and record `Scan: not consulted (<absent|error>)` — loud, never silent (the artifact write is an **orchestration** stdout-redirect, not shim code). The §10.9 coverage manifest gains an optional mechanical `Scan:` line — `Scan: consulted (<n> observations; <k> inventoried, <m> declined)` + one indented `Declined: "<span fragment>" — <one-clause reason>` per declined observation, OR `Scan: not consulted (absent|error)` (that two-value reason enum only; an absent line is the valid pre-R3B case). Each scan observation is either **inventoried** (an M-record at that locus — identification authority stays with the audit) or **declined** with a one-clause reason; the comparison coordinate is the M-record's resolved `Source anchor` → derived paragraph index → normalized span overlap **within that paragraph** (the prose locus label is never a comparison operand). `scripts/argument_agd.py` (+ byte-identical mirror) learns and shape-checks the line — integers; `k + m = n`; `m` = the count of `Declined:` lines; and, with `--scan agd_move_scan.json` (as `--check-all` supplies), `n = len(results.observations)` — with hostile self-test arms (bad counts, k+m≠n, m≠declined-lines, bad reason value, malformed `Declined:` line). Structural line parse throughout; bounded leaf regexes on the count/reason tokens only.

**Worked fixture + source realism.** The five R3A fixture sources are split into their natural 2–3 blank-line paragraphs (a whitespace-only edit; every §10.9 `Source anchor` is intra-sentence and keeps resolving — the `--check-all` arm re-verified). The **cue-free structural-discounting** fixture ships a committed `agd_move_scan.json` (generated by the producer's manifest judge against the split source) plus a §10.9 `Scan:` block that exercises the cross-check with **one inventoried** observation (the cue-free DISCOUNTING move whose anchor resolves in a *different* paragraph than its prose locus label — matching on the label would flip the verdict) and **one declined** (an ASSURING data-report observation with no strippable assurance span), validated by the extended `argument-agd` under `--check-all`. The stale B5 "deferred dynamic signals — not present" note in `argument-decision-audit.md` is refreshed: the disappearing-guard and discounting/straw-man signals now ship via `agd_move_scan` as observed-not-pinned, unanchored, aggregate-excluded located observations (the §131 B3/B4 posture).

No new apodictic diagnostic code, no GT anchor, no crosswalk change (the AGD↔S&F crosswalk is R4B's); the Phase-1/2 behavioral benchmark is a separate later track. Sources: Sinnott-Armstrong & Fogelin, *Understanding Arguments* 9e, ch. 3 (assuring / guarding / discounting); R3A AGD Move Audit lineage (`argument-agd-audit.md`); R4A ADR D5 (producer observes, consumer adjudicates).

### Nonfiction Argument Engine — Matched Clean/Broken Pairs (Argument Benchmark specificity retrofit)

The Argument Benchmark's two synthetic planted-defect fixtures (`op-ed-warrant-leap`, `policy-brief-uncompared`) are retrofitted into **matched clean/broken pairs** so specificity is measured **within-work**, not across works: today the broken fixtures and the positive controls are *different prose*, so "the engine flagged the broken fixture" is confounded with "found the fixture's own authored roughness" and "correctly specific" is confounded with "the control is just different prose." Each broken member moves (history-preserving `git mv`) to `<pair>/broken/`, and a **derived clean twin** is authored at `<pair>/clean/` by an **enumerated, minimal repair-edit set** that discharges exactly the broken key's registered GT2 defect and nothing else (every other byte identical) — for `op-ed-warrant-leap` the *double* warrant leap (a causal-warrant insertion supplying a per-ride rate + confounder disposal, and a remedy-warrant insertion showing the lighter remedies were tried and failed); for `policy-brief-uncompared` the AT3 comparative + feasibility burden (a genuine same-goal service-investment comparison with criteria and a conceded tradeoff, plus a cost figure and funding mechanism discharging the planted FM-A18). Both twins are born on GT schema v0.3.0 with the Reliability ledger at the authoritative tier and are author-deterministic (the mutation diff *is* the answer key), so they add **no new second-editor ask**. `scripts/argument_groundtruth.py` gains **Check 7** — matched-pair provenance (`Matched-pair member` / `Paired-with`, fiction's field names and `<pair>/<member>` value shape) implemented as a deliberate **stricter superset** of fiction's pairing grammar: a **new lowercase leading-token member regex** `_PAIR_MEMBER_RE` (hostile boundary lookahead so `cleanX` cannot truncate-parse — NOT fiction's substring parse, and the uppercase `_GT7_VERDICT_RE`/`_GT8_FLAGS_RE` are neither touched nor reused), both-fields-together enforcement, complement pairing (a `clean` names its `broken` twin and vice versa), **slug self-consistency** (the wrong-twin gate — the key's own `Fixture slug` pair must equal the `Paired-with` pair), and **clean-side derivation gates** (a `clean` member requires a non-N/A `Base text + repair record` and a GT2 marked `N/A — positive control` — the argument-side inversion of fiction's broken-plant-record gate). Absence of both pairing fields is a zero-behavior no-op, so all 14 unpaired legacy keys pass byte-unmodified. `validate.sh --check-all`'s argument corpus loop gains the **two-depth glob** (`<pair>/{clean,broken}/groundtruth.md`) so nested members are validated at all, plus an **orphan-twin completeness pass** (a member with no sibling is a loud FAIL) that closes the missing-twin hole mechanically alongside Check 7 rule 5's wrong-twin hole. Two mechanical guards make the "deterministic twin" claim real: Check 7 rule 6 and a scripted **repair-diff acceptance gate** (each pair's `diff broken/fixture.md clean/fixture.md` is pure-additive with hunks mapping **1:1** to the enumerated repair-record loci — 2 each, zero unrecorded drift). Protocol side: `RUN-PROTOCOL.md` §Step 4 gains a fourth convergence class (broken converges failure-bearing, clean converges Must-Fix-qualified-positive-control, and the pair **delta** — the planted discriminator fires as a structural failure in the broken run and NOT in the clean run, on the same prose, per config), with a §Step 1/2 **pair-blindness** rule (members are separate blind submissions in separate runner sessions; a runner is never told a submission has a twin). Scoring is unchanged (protocol-level only — no new metric, no rubric dimension). Eleven new Check-7 self-test arms (none weakened to fiction's looser behavior); byte-identical `scripts/` ↔ `plugins/apodictic/scripts/` mirror; no hard-coded fixture/validator counts introduced. Out of scope (M2): a PD broken twin of `federalist-10` (broken *derived from* the real clean base, carrying `Base text + plant record` — the fiction direction); `douglass-fourth-of-july` is excluded (a planted defect in an unconventional-but-warranted form-control would score sensitivity by pathologizing the form). Pattern: `BUILD-PREFLIGHT.md` §"CONSTRUCTIVE PATTERN — ground truth for a partly-subjective domain" (matched counterfactual pairs — score the delta), adapted from the fiction benchmark (fiction-GT #187).

Codex #196 diff-review fold (refreshed onto `main` after #197's structural GT-validator refactor, whose `_provenance_block`/`_parse_booked` helpers this branch adopts): the clean-member GT2 positive-control gate is now a **structural leading-line marker match** rather than a body substring (a substantive GT2 that merely mentioned "positive control" no longer passes); the scripted **repair-diff acceptance gate is wired into `--check-all`** as a real `--repair-diff` mode (pure-additive, hunks 1:1 with the enumerated repair loci parsed by a structural line walk — not prose-only); the **nested opt-out is closed** (a file under `<pair>/{clean,broken}/` may not drop its pairing fields — the directory is the source of truth via a path-derived member hint); and the residual regex holes are closed structurally (`_FIXTURE_SLUG_PAIR_RE` end-anchored so suffix garbage cannot truncate-parse; the orphan-twin pass now requires **both** `fixture.md` and `groundtruth.md` per member and twin). Ten new self-test arms (5 Check-7 hardening + 5 repair-diff) join the original eleven; the byte-identical `scripts/` ↔ `plugins/apodictic/scripts/` mirror holds; no hard-coded counts introduced. The behavioral pair-delta convergence (8/8 cross-vendor, Fable + Codex 5.6) is recorded in `docs/argument-benchmark-calibration-round.md` §Matched clean/broken pairs.

Second Codex #196 fold (fresh-head review): the orphan-twin completeness pass is now driven off the member **directories** (`<pair>/{clean,broken}`), not a `groundtruth.md` glob — a **fixture-only member directory** (a `fixture.md` with no `groundtruth.md`) was invisible to every corpus loop, all of which key on `groundtruth.md`, and so evaded completeness validation entirely (P1); it is now a loud FAIL. And the repair-diff gate now rejects **duplicate repair-locus identifiers** (a repeated `Locus <n>` inflated the loci count and could spuriously match the hunk total, purporting a 1:1 map that isn't one — P2); each enumerated locus must carry a distinct id. Two more self-test arms; mirror parity and full `--check-all` (all 18 GT files `ok`) hold.

Third Codex #196 fold (fresh-head re-review): Check 7 rule 1 is now **bidirectional** — a file that *declares* a `Matched-pair member` but lives at a flat path (its parent directory is a slug, not `clean`/`broken`) is rejected, closing the inverse of the nested opt-out (a flat member declaration escaped the directory-enumerated completeness pass, so its missing twin was never caught); the CLI passes the raw parent-dir basename as `member_hint` so this is distinguishable (`None` is reserved for the in-memory self-test). And the repair-loci parser adopts the claim-broad / validate-strict pattern: a locus-shaped bullet that is not a well-formed `- **Locus <n> — …` (a case variant `LOCUS 1`, a number-less `Locus`, `Locus1`) is now a loud **malformed-locus** error instead of being silently dropped, and a **second `Base text + repair record` field** (whose loci would be invisible to the map) is rejected. Five more self-test arms; mirror parity and full `--check-all` hold.

Fourth Codex #196 fold (fresh-head residuals): Check 7 now binds the in-file pair slug to the actual parent pair directory (two internally consistent `wrong-pair/*` declarations can no longer pass at another pair's path), parses pairing declarations only from the exact `## Provenance` block, rejects pair-shaped fields misplaced under Notes (including on flat fixtures), and rejects contradictory duplicate fields instead of trusting the first match. The repair-locus strict leaf now enforces the documented bold-title + dash form rather than accepting any line that merely begins `Locus <n>`. Five hostile self-test arms pin the three bypass classes; mirror parity and the full corpus gate hold.

### Nonfiction Argument Engine — GT-validator Check 3 exemption hardened to a structural marker

`scripts/argument_groundtruth.py` (and its byte-identical `plugins/apodictic/scripts/` mirror) closes the last instance of the substring-exemption class that Codex #196 fixed for Check 7 rule 6ii. The Check 3 GT2 locus↔code-family consistency check previously exempted "N/A" GT2s via a body substring test (`re.search("N/A", gt2)` OR `"positive control" in gt2.lower()`), so a real WARRANT-locus GT2 that carried only SUPPORT codes — the spec's "WARRANT diagnosed as SUPPORT" error — was wrongly **exempted** whenever it merely *mentioned* the words "N/A" or "positive control" anywhere in its prose, and the locus↔code mismatch slipped through. The exemption is now **structural**: it fires only when the GT2 section's first non-blank line (extracted by `_parse_gt_sections`) OPENS with an `N/A` marker (new `_GT2_NA_MARKER_RE`, the same leading-anchored posture as `_GT2_POSCTRL_MARKER_RE`). The marker is deliberately the **broader N/A family** — a bare `- **N/A.**` (the `modest-proposal-satire` fixture, whose literal-support/warrant locus is legitimately N/A, not a positive control) as well as the `N/A — positive control` controls (a subset) — so every currently-exempt fixture stays exempt; a real `Primary failure layer` GT2 is checked regardless of any downstream N/A / positive-control mention. Verified non-regressive: the exempt/run classification is byte-for-byte identical to the prior behavior across all 18 registered GT files (0 flips), all stay `ok` under `validate.sh --check-all`, and two new self-test arms pin it — a WARRANT-locus/SUPPORT-codes GT2 that mentions both phrases in prose now FAILs, and a bare-`N/A` satire GT2 stays exempt. Byte-identical `scripts/` ↔ `plugins/apodictic/scripts/` mirror; no schema, spec, or contract change. Stacked on #196 (which introduced `_GT2_POSCTRL_MARKER_RE`).

### Argument engine — warrant-defeaters as typed §6 objections (R2; Argument_State v0.2.0)

R2 of the argument re-grounding roadmap: complete the Toulmin model's **rebuttal node** — the "this holds *unless* …" exception conditions on a warrant — as a **typed kind of §6 objection**, not a parallel field. The §6 objection record (`docs/argument-state-schema.md` §6; Dialectical Clarity Step 6 template) gains a typing vocabulary: `Target` (`C0`/`Cn`/`Cn.warrant`/`Cn.support`/`argument-wide`), `Relation` (`WARRANT-DEFEATER` / `CLAIM-CHALLENGE` / `EVIDENCE-CHALLENGE` / `VALUE-CONFLICT` / `ALTERNATIVE`), and `Basis` (`TEXT-INTERNAL` / `IMPORTED`) — two **decoupled** axes: Relation is what the objection targets (a `WARRANT-DEFEATER` is an "unless…" exception on a specific `Cn.warrant`'s connecting principle, holding that warrant fixed — Toulmin's rebuttal), Basis is derivation provenance (the existing Step 6a Test-B/Test-A distinction, mechanized). A Test-B-derived self-undermining remedy is `TEXT-INTERNAL` + `CLAIM-CHALLENGE`/`ALTERNATIVE`, **not** a warrant-defeater; a generic warrant exception is `WARRANT-DEFEATER` + `IMPORTED`. Every warrant-defeater records its `Condition`; a `TEXT-INTERNAL` one must cite `Derivation anchors` (the warrant/grounds locations it is derived from — engine-surfaced, author-adjudicated diagnosis, never an asserted validity constraint; the Firewall's no-invented-warrants discipline). A new bounded **per-warrant sweep** (Step 6, "6a-sweep") runs the Test-B question scoped to each §4 warrant and records material results as typed records; the existing `Engaged`×`Quality` axes grade them **once** (no new engagement vocabulary), and an ignored material defeater reaches the author through the ordinary objection pathway (`Engaged: N` + OB codes — OB3 when central), so severity propagation rides the existing table unchanged. §4 gains a **projection line only** — `Defeater refs:` (within-run pointers, populated by Step 6, never authored at Step 4) or `NO-MATERIAL-TEXT-INTERNAL-DEFEATER-IDENTIFIED — <review_basis stating the materiality bar>` (an open-world search result, never a warrant-soundness assurance; an absent line = not swept, i.e. *unknown*, never clean — the silent-skip guard). **No new failure code** (WR stays 4, OB stays 6 — the R4A crosswalk's exact-82-set pin is untouched; Relation/Basis are field enums, and their crosswalk mapping to Toulmin/AIF-CA is deferred to R4B with the AIF adapter).

Pre-draft, the opposition surfaces stay **writer-owned**: `reviewer_objections` items may now be a legacy bare string (unchanged; blank-ness remains W5's *advisory* concern — behavior-preserved against the documented whitespace-only arm) or an object `{objection: required non-whitespace, target?, relation?}`; `anti_thesis` stays a required string with optional flat scalar siblings `anti_thesis_target`/`anti_thesis_relation` (schema `pattern`/`enum`-checked; W1's echo consumer untouched). The genre-profile schema's `reviewer_objections.items` is deliberately **untyped** — the stdlib subset validator has no union support and a typed `items` would reject the object form before hand-rolled code ran — so ALL per-item validation lives in `argument_spine.py`'s new `_reviewer_objection_errs` (the `_genre_section_errs` pattern): object shape (required `objection`, `target`/`relation` value-spaces, **post-draft audit keys rejected** as wrong-surface, closed key set), plus a new **B5 dangling-objection-target** arm (a typed `target`'s `Cn` must resolve against the spine ladder via the A5/A8 machinery; skip-not-fail when no valid spine — the B3 precedent; `C0`/`argument-wide` need no resolution) and a **W5 widening** so an all-object-form list counts as real content (previously it would false-fire "declares no reviewer_objections" — ERROR under `--strict`). The review fold also rejects explicit JSON `null` for either optional typed object field: omission remains legal, but a present `target` or `relation` must satisfy its declared value space. 19 new self-test arms (101 total) cover the full truth table (valid variants, missing/blank `objection`, numeric item, bad or null target/relation, stray post-draft key, unknown key, B5 dangling + skip-without-spine + C0/argument-wide, all-object W5-green under `--strict`, sibling-field pattern/enum rejects, blank-bare-string-stays-advisory). The canonical genre fixtures now exercise all three item forms under `--check-all --strict` (grant = mixed, pitch = all-object, academic = legacy bare). Both docs (`docs/nonfiction-pre-draft.md`, the pre-writing-pathway reference) updated; `check-mirror` byte-identity held; no new `AGG_VALIDATORS` entry (the derived count is unchanged). Post-draft §6 typed fields and the §4 projection are convention-governed (parity with every §6/§4 field today). Design source: Toulmin, S. (1958), *The Uses of Argument*, Cambridge University Press (the warrant/rebuttal model); the typed-objection single-home frame follows a cross-vendor design review that rejected a parallel-field design as duplicating the semantic object and adding a third engagement vocabulary.

### Nonfiction Argument Engine — Warrant-Leap Primacy Over the Uncompared-Proposal Defeat (rule 2a)

Dialectical Clarity's Step-9 **rule 2a** (the AT3 uncompared-recommendation FM-A10 defeat) gains a **primacy-override** for the case where an AT3 recommendation is defeated *both* by the zero-comparison FM-A10 rule *and* by a causal/diagnostic **warrant leap** (WR0 **MISSING** on C0's causal bridge — the recommendation's *problem* is not warranted, e.g. "the harm rose when X appeared" ⇒ "X *caused* the harm" with confounders unaddressed). Previously the engine's "name the *first* defeated test" ordering ranked the FM-A10 comparative defeat — which fires at decision **test two** (Evidence-evaluability) — ahead of the warrant leap at **test three** (Warrant-recoverability), so a piece with both defeaters was reported as an Uncompared-Proposal (FM-A10 / BURDEN) primary even though the causal warrant leap is the deeper break. The override makes the **causal warrant leap the primary structural break (FM-A6, The Warrant Leap)** and **co-reports FM-A10 as a subordinate defeat**, on a logical-dependency rationale rather than the table order: a recommendation to "do Y about problem P" rests on **L1** (P is real and attributable to Y's target) and **L2** (Y beats the alternatives), and **L2 presupposes L1** — the same dependency the repair order already encodes (warrant before remedy-defense). The **verdict is unchanged** (UNWARRANTED under either failure); only the *primary locus / pattern* changes, and only for this co-defeat case. A **negative test** preserves the ordinary case: an AT3 recommendation whose problem is adequately warranted (or whose only WR0 is incidental / RECOVERABLE) and whose *sole* defeat is the missing comparison keeps **FM-A10 primary** (e.g. a fare-free-transit brief whose benefits are evidenced but whose alternatives are never weighed). Cross-pointers were added at the Step-9 Final Diagnostic Question ("name the first defeated test" / "name which step breaks first") and the operative-test FM-A10 note so the override is discoverable from every place the ordering rule is stated. Resolves the M1 convergence-run caveat #1 (`docs/argument-benchmark-calibration-round.md`), where two independent blind engines (Fable + Codex 5.6) both returned the correct UNWARRANTED verdict on `op-ed-warrant-leap` but ranked FM-A10 / BURDEN over the registered FM-A6 / WARRANT primary. The fixture's `groundtruth.md` GT2 is sharpened to match: FM-A10 → BP5 is registered as a **subordinate** second defeater (uncoded objection to avoid colliding with GT3's confounding-zone central-objection code), with a split Q2 scoring boundary (surfaced-but-subordinated → cap Q2 = 2; warrant-leap-omitted → Q2 = 0 miss) and an explicit rejection of a co-equal GT-as-a-set reading under GT-set guards #1 and #4. Behavioral change → gated on a cross-vendor blind convergence re-run before merge.

### Argument taxonomy — layer-boundary ADR + machine-readable crosswalk (`argument-crosswalk-check`)

R4A of the argument re-grounding roadmap: fix the layer boundaries *once* so the R2–R5 coherence work builds on stable IDs. Ships an Architecture Decision Record (`docs/adr/0001-argument-layer-boundary.md`) and a machine-readable crosswalk (`evals/argument-crosswalk/crosswalk.json`, v0.1.0) mapping the **82** internal argumentation code-layer entries (46 Dialectical Clarity codes + 20 FM-A patterns + 8 scheme hints + 3 warrant-verdict values + 5 premise-plausibility flag **types**) to four external reference vocabularies — **AIF** (node ontology; an *optional serialization adapter*, ADR D2), **Walton** schemes + critical questions, **S&F** fallacy families + the p.333 refutation split, and **Wachsmuth/GAQCorpus** logic/rhetoric/dialectic dimensions — each row carrying an explicit **cardinality** tag (`exact`/`broader`/`narrower`/`related`/`unmapped`). The ADR records: `Argument_State` stays the internal SSOT (D1); AIF is an adapter, not the vocabulary (D2); external vocabularies are reference targets crosswalked-*to*, never authorities that rename internal codes (D3); mapping cardinality is first-class and visible, and a mechanical global non-injectivity floor forbids a silently all-1:1 crosswalk, so the historical "1:1" overclaim cannot silently recur (D4); apodictic alone assigns codes, voiceprint emits located observations (D5, mirroring the SETEC seam); the verdict-axis→S&F mapping is R4A/R1-owned (D7). No taxonomy is renamed; R4A is purely additive.

The gate, `scripts/argument_crosswalk.py` (stdlib-only, `validate.sh argument-crosswalk-check`), certifies **shape, not scholarly correctness** — the crosswalk's targets/cardinality/provenance/rationale are authored assertions about external theory that no structural check can verify, so the ADR draws that boundary explicitly and the mechanical additions raise the floor without overclaiming: (1) **drift-binding** — the authoritative 82-ID set is *derived at check time*, not a fourth hardcoded copy (the verdict/flag/FM-A slices import the live owners `_GT7_CLASSES` / `_GT8_ROW_FLAG_TYPES` / `_FM_A_MAX` from `argument_groundtruth.py`; the 46 DC codes + 8 scheme hints, which have no machine-readable owner, are parsed structurally from `dialectical-clarity.md` by heading/table walk — the structural discipline, not a doc-wide regex), so a 47th code, a renamed flag type, or a stale registry self-count desyncs loudly; (2) **count tripwires** freeze the enumerated 46 (naming OB5) and 20 (naming FM-A20) against the registry's own stale "45"/"nineteen"; (3) a **provenance locator** (`{work, loc, id}`) is required on every populated target, mirroring the existing `argument_groundtruth.py` per-fault provenance precedent; (4) a **global non-injectivity floor** makes a silently all-1:1 crosswalk impossible; (5) closed external-ref value-spaces (an unregistered Walton scheme / Wachsmuth sub-criterion → ERROR); (6) `unmapped ⇔ no-targets`, with a **required non-empty rationale** on every `unmapped` row (the visible R2/R3/R4B work-list — 48 of the 82 at v0.1.0). Registered on all five surfaces (AGG token, dispatcher case with `--self-test` + python3-degrade path, help line, byte-identical `scripts/` ↔ `plugins/apodictic/scripts/` mirror, this fragment) plus a `--check-all` real-file arm over the shipped `crosswalk.json` (resolve-and-skip when `evals/` is absent from host workspaces). Behaviorally inert: no engine reading or scoring changes, no `Argument_State`/`dialectical-clarity.md` step-logic edits. Reference sources: the AIF specification (arg-tech.org); Walton, D., Reed, C., & Macagno, F. (2008), *Argumentation Schemes*, Cambridge University Press; Sinnott-Armstrong, W., & Fogelin, R. (2015), *Understanding Arguments*, 9th ed., Cengage; Wachsmuth, H., et al. (2017), *Argumentation Quality Assessment: Theory vs. Practice*, ACL — ACL Anthology P17-2039 (the citation the repo's `argquality_judge.py` already uses; the fuller 15-dimension taxonomy is Wachsmuth et al. 2017 EACL E17-1017), as the taxonomy behind GAQCorpus (Lauscher et al. 2020, arXiv:2006.00843).

### Nonfiction Argument Engine — Warrant Verdict / Premise-Plausibility Split (GT schema v0.2.0)

Dialectical Clarity's Step-9 verdict enum is re-grounded from `SOUND / UNCONVENTIONAL-BUT-EFFECTIVE / UNSOUND` to **`WARRANTED / UNCONVENTIONAL-BUT-WARRANTED / UNWARRANTED`**, splitting the conflated "soundness" judgment into two axes: a **warrant verdict** (whether the reasoning warrants the conclusion on the text's own terms — the inference axis, Wachsmuth cogency's Local Relevance + Local Sufficiency) and separate, non-adjudicative **premise-plausibility flags** (whether a load-bearing premise is contestable — the acceptability axis, Local Acceptability). The token stays `WARRANTED` rather than `COGENT` precisely because full cogency folds in premise acceptability, which the Firewall forbids the engine from adjudicating in a verdict; premise flags surface a premise for the writer to earn but never rule it true or false and never change the warrant verdict by themselves. The FM-A10 (Uncompared Proposal) rule-2a evaluability defeat is preserved exactly — only the token changed (`UNSOUND → UNWARRANTED`). The Argument Benchmark GT schema bumps to **v0.2.0**: GT7 is renamed `Warrant verdict`, a required flag-only **GT8 — Premise-plausibility flags** section is added, and all 16 registered `groundtruth.md` fixtures migrate (10 take `NONE_REGISTERED (provisional migration default)`). `scripts/argument_groundtruth.py` gains GT1–GT8 coverage, warrant-verdict enum validation with active rejection of the retired label/tokens (present-but-unparseable GT7 is now an ERROR, not a silent skip), and GT8 leading-token parsing with a field-scoped case-sensitive truth-token Firewall check (flag-type cell only; the `Why flagged` / `Firewall boundary` prose is exempt). GT8 is an M1 contract/firewall check, not a scored dimension — a scored premise-flag dimension is deferred to M2. A Fable-5 three-lens review (anchor/parity, conceptual/firewall, adversarial/edge-case) was folded pre-merge: the GT8 registered path is **strict** (field↔row id agreement both directions as a **multiset** — a doubled `P1, P1` field id or two conflicting `P1` detail rows are rejected before the coverage compare rather than collapsed away by set equality, bolded-id rows matched, exactly-5-cell rows, full-match flag enum, token/heading-number boundaries, all three retired GT7 encodings rejected as residue — 40 self-test arms), the Hard-Gate-vs-Must-Fix conflation in the Step-9 decision rule was fixed behavior-preservingly, `ground` joined the load-bearing-role enum, and the GT8 ownership boundary (a flag must not duplicate a phenomenon a code already carries) landed in the ground-truth template. Move 1 of a multi-increment re-grounding of the argument taxonomy in *Understanding Arguments* (Sinnott-Armstrong & Fogelin, 9th ed.) and the argument-mining literature; grounded in Wachsmuth et al., "Computational Argumentation Quality Assessment in Natural Language" (EACL 2017) and Inference Anchoring Theory (Budzynska & Reed).

### Execution Modes — Cost-Floor Dispatch Override

New `cost-floor` validator + run-core path: a cost-constrained user can now cap a run **below** the token-fit floor at the cheapest load-viable mode, with honest tradeoff disclosure — the missing counterpart to `quality_risk_override` (which only declines an *upward* escalation). A cap is recorded as BOTH a `<!-- override: cost-floor-{single-agent,sequential,hybrid} — … -->` marker and a `cost_floor_override: <mode>[; context_tier: standard|large] — …` metadata token (via the `override_marker` SSoT). Execution Protocol step 3 gains **(d)** `final = min( max(token-fit-floor, RAW-quality-risk-target), cost_cap )`. `scripts/validate.sh cost-floor` gates record integrity — CF1 marker integrity incl. the bidirectional orphan-token check, CF2 marker↔token sync, CF3 single-agent `context_tier: large` + mandatory-packet load-under-600K bound (with a below-floor WARN for a sequential/hybrid cap under the token-fit floor), CF4 no silent quality-risk demotion (a fired Q-trigger above the cap needs its own `quality-risk-Q[n]` marker) — without selecting the mode; the orchestrator owns selection. `preflight.sh` now prints a `## Per-Mode Token Cost Estimate` section (single-agent · sequential ×3 · hybrid ×4 · swarm ×7, **not ratio-comparable**), the intake-router §2b below-floor pick is routed through the same gated front door, and `dispatch_record.py --report` counts `cost_floor_override` records (CR-6 detectability). The shared Q1–Q5 detection was extracted into a behavior-preserving `_fired_triggers` enumerator that both `quality-risk-triggers` and `cost-floor` call.

### Nonfiction Argument Engine — GT-validator markdown matchers refactored to structural parsing

`scripts/argument_groundtruth.py` (and its byte-identical `plugins/apodictic/scripts/` mirror) replaces the two markdown-**structure** matchers behind the recurring Codex-review edge bugs on the reliability-ledger PR (#193) — three of the four edge bugs there were in these two (two in the Provenance scope, one in the BOOKED matcher) — with structural line/heading parsing (pure stdlib; the fleet no-deps rule holds). The `## Provenance`-block scope, formerly a multi-line `^##[ \t]+Provenance…(.*?)(?=^##\s)` block regex that took three review rounds to stop matching `## Provenance Notes` (suffix lookalike) and `##\nProvenance` (newline split), is now **`_provenance_block`** — a heading walk mirroring `_parse_gt_sections` that matches the heading by exact title equality and closes the block at the next `##`-level heading, with no `\b`/`\s`-across-newline boundary games. The round-record `BOOKED` matcher, formerly a claim-broad / validate-strict / body regex trio that reached correctness only after review rounds hand-tuned it to reject the near-miss dialects (`- **BOOKED** — ENGINE-FAULT`, `- BOOKED::`, `- BOOKED*`, `* BOOKED:`), is now **`_parse_booked`**: a deliberately broad structural CLAIM (any bullet, optional bold, the word `BOOKED`) so no near-miss dialect silently escapes, a strict canonical form (`- BOOKED:` / house-bold `- **BOOKED:**`) by string slicing, and a token-split body (`ENGINE-FAULT <slug> GT<n>[ OVER-FIRE]`, zero-padding rejected). The fourth #193 edge bug's guard — the `- **Reliability:**` field-label leaf regex — is deliberately **kept** as a bounded single-line token match (regex is the right tool for a leaf token; the trap was multi-line/heading scope). The change is **behavior-preserving**: all 76 parser self-test arms pass unchanged (including the `reliability_provenance_lookalike` / `_newline_split` / `_near_label_rejected` / `_misplaced_ledger` and every `roundrec_dialect_*` regression arm), and a differential sweep of the retired regexes vs the new helpers over a hostile input battery confirms they agree — the sole delta is a functionally-inert error-message category (a whitespace-only-body `- BOOKED:  ` now reads "unrecognized dialect" rather than "malformed body ''"; both reject the line, so the round-record accept/reject verdict is identical). No schema, spec, or contract change.

## v2.8.0 - 2026-07-07

### Nonfiction Argument Engine — Reviewer-Anticipation (genre layer, Increment 2)

The genre layer's reviewer-anticipation surface (**W5**) now rides the `argument-spine` validator. When a `genre_profile` block is present and its `reviewer_objections` array is empty or absent, W5 surfaces the empty required class as a WARN (ERROR under `--strict`), directing the writer to pre-list the evaluator's likely objections — which seed §6, The Strongest Case Against — before drafting. The Firewall holds: W5 checks only that the writer's list is **non-empty**; it never authors, suggests, or validates the *content* of an objection. Overridable via `<!-- override: argument-spine-reviewer <genre> — <rationale> -->` (a W5-specific slug, decoupled from W4's `argument-spine-genre`). W5 adds **no** validator — the derived self-testable count is unchanged. The three canonical genre worked examples (grant / academic / pitch) each carry a `reviewer_objections` pre-list seeded into a §6 *Reviewer-anticipation* block, so they pass `--check-all` under `--strict`; a per-genre reviewer-anticipation calibration table (evaluator stance · top objection classes · W5 pre-list → §6 mapping) lands in Dialectical Clarity's *Genre & Audience Calibration*.

### Validators — cross-surface uncalibrated-band `calibration-honesty` guard + decision-audit doc fixes

Both consumer decision-audit surfaces — `narrative_decision_audit` (StoryScope) and `argument_decision_audit` (ArgScope) — ship an `uncalibrated` verdict band with null thresholds; the discipline that the band is surfaced as **provenance only, never as a calibrated verdict** was enforced entirely in prose (the audit docs' anti-verdict sections + four `pass-dependencies.md` rows), with no mechanical check that a reader-facing rendering doesn't present the uncalibrated band as calibrated. New `AGG_VALIDATORS` arm **`calibration-honesty`** closes that gap: a **whole-letter, per-paragraph** scan (region-scoping was a false foundation — the only per-audit sectioner scopes appendix bodies only, decision-audit findings land in the unscoped synthesis body, and the canonical scaffolded letter carries no decision-audit region) that flags a paragraph only when a **claim shape** matches **and** no **qualifier** is co-present — CS1 band-placement (`… scores in the … band`), CS2 calibrated-verdict, CS3 threshold-claim on a thresholds-null surface, CS4 aggregate-as-verdict; a co-present `uncalibrated` / `provenance-only` / `advisory` / `not a verdict` qualifier quenches the flag, so the mandated clean-path boilerplate, the seven vendored StoryScope bundle labels (`"AI-elevated: Structural streamlining"` …), ArgScope's two bundle labels, and the doc's own "fair" summary sentence all PASS. **WARN by default, ERROR under `--strict`** (the honest class — an open natural-language co-presence check, `content_advisory` W1 / stance-consistency F4, failure direction toward NOT firing): the guard closes the enumerated claim shapes; residual semantic leakage no vocabulary can close is presented to a human who owns the reading. **Disjoint from `severity-floor`** (D5): the submission-readiness band vocabulary (`Strong Fit` / `Highest Band` / …) is excised from CS1, so a legal readiness verdict does not fire here, and calibration-honesty never reads flag counts. Per-paragraph override via the shared `override_marker` SSoT (`<!-- override: calibration-honesty — <why> -->`, code-span-stripped, boundary-matched). Cross-surface + surface-agnostic — a future uncalibrated `handoff: experimental` consumer inherits it by construction. A dedicated canonical `example-decision-audit-letter.md` (a clean narrative-decision finding + a violating argument-decision finding coexisting) exercises the arm non-vacuously in `--check-all`. The CS shapes / qualifier set / allowlist are this guard's own new vocabulary (not the Must/Should/Could-Fix severity token, so `severity_vocab`/M8 does not apply). Firewall-hardening chore; no paper cite.

Also two docs-only decision-audit fixes: `narrative-decision-audit.md`'s Version-floor line still described a consumer-side `resolve_floor` pre-check (pre-R2 language, contradicting the same file's corrected line and the shim it documents) — rewritten to the post-R2 runtime-dispatcher enforcement matching the ArgScope sibling; and `AUDIT_SELECTION_MATRIX.md`'s Narrative-Decision cell described a non-existent choice-and-consequence propagation lens — rewritten to describe StoryScope feature scoring.

### Coaching Deepening — Coaching History & Pattern Recognition (the ethics-sensitive surface)

Over multiple revision cycles the coach can now surface a **cross-session process pattern** — the same finding deferred across an unbroken run of sessions (`deferral-recurrence`, floor ≥3), or a revision-arc phase left open across consecutive sessions (`phase-incompletion`, floor ≥2) — as a **rolling, opt-in, local-only** `[Project]_Coaching_History_[runlabel].md` of `apodictic.coaching_observation.v1` blocks, each **mechanically derived from the recorded finding-disposition / revision-arc records** (a count, never a vibe) and carrying **no editorial severity** (no Must/Should/Could token, no `apodictic:finding` block). This is APODICTIC's ONE ethically-sensitive surface; the two Fable conditions (2026-07-05) are mechanized as the load-bearing gates.

New `coaching-history` validator (`scripts/coaching_history.py`, dual-mirror) + the `apodictic.coaching_observation.v1` schema: **H1** schema + unique `CH-NN` + per-pattern count floor, **H2** provenance/anti-fabrication (every `<F-id> deferred @ session <n>` resolves to a recorded deferred disposition; `len(evidence) ≥ count`; the cited sessions are **actually consecutive** — a gap fails), **H3** descriptive-not-judgmental (reuses `author_fingerprint._PRESCRIPTIVE_RE` + a trait-blame lexicon), **H4** no-severity-leak (`severity_vocab.SEVERITY_TOKEN_RE`), **H7** tentative-framing (no trait verdict / no bare-scoreboard rendering / an invitation present — the transference-health floor), **W1** local-only. The two ethics gates: **H5** single-home / no coach-only shadow and **H6 + the `delete <project_root>` subcommand** deletion-honored (RECOMPUTE-not-trust per the PR #161 recorded-field rule / `disposition_check` DP2.6 — under the `<!-- coaching-history: deleted -->` tombstone the full H5 scan must be empty + no surviving artifact + no seq; residue = ERROR with **no** override; `opted-in`+`deleted` = ERROR). `delete` removes every artifact (root + `runs/*`), drops the sidecar seq, and flips consent to the tombstone. Opt-in gate (home: `Diagnostic_State.md`; no marker → no-op exit 2). `revision-coach/SKILL.md` §9 carries the human-terminus contract (opt-in gate, single-home / no-projection, read-by-id, tentative-noticing presentation, surface-the-delete). Spec: [`docs/coaching-history.md`](docs/coaching-history.md).

**H5 scan coverage (Opus review F1, P1).** The projection-ban is only as good as its coverage: an early draft scanned a 6-glob authored-artifact allowlist, so a coaching observation projected into an **unlisted** type (the editorial letter, `*_Core_DE_Synthesis_*`) escaped H5 **and** survived `delete` — a false "deletion honored" that broke *both* Fable gates (H6 rests on H5's projection ban). Fixed: the self-identifying (i) parsed `coaching_observation` block + (ii) schema-id signatures are now scanned over **every `*.md` in scope** (minus the one Coaching_History artifact — zero false-positive risk, no legitimate file carries either); the (iii) evidence-grammar + bare-`CH-NN` scans (which *do* carry manuscript false-positive risk) stay manuscript-excluded, but the manuscript is now identified **positively** via the persisted `*_Manuscript_Snapshot_*.md` (`annotation_manifest._SNAPSHOT_GLOB`), not an allowlist. Regression fixtures (self-test + `--check-all`): an editorial-letter projection FAILs H5 and, after `delete`, is CAUGHT by the H6 recompute; a manuscript snapshot carrying "CH-12" / prose "@ session" does not false-trip.

**H2 anti-fabrication honestly scoped (Opus review F2).** The guarantee is fabrication-resistant ONLY on **governed** projects (the independent per-session `gate_events[].disposition_deltas` records). On **non-governed** projects the multi-session history is self-reported by `/coach` (the folded record's `sessions` list), so H2 now requires a non-governed `deferral-recurrence` observation to carry a **visible honesty caveat** that its streak is from the coach's own notes, not an independently verified record (WARN, ERROR `--strict`, per-id override — the writer is never shown an unverified pattern as if it were checked; the H7 principle). SKILL §9 now instructs `/coach` to persist the `sessions` list at disposition time and to state the caveat; the canonical fixture teaches both.

**Completeness sweep — the incomplete-verification class, closed across ALL patterns and ALL depths (Codex round-1 P1 + P2 + the class sweep).** The same "checked the known locations, not all of them" class that produced F1/F2 recurred twice more; swept whole:
- **P1 (phase-incompletion verification, BLOCKING).** `phase-incompletion` evidence was shape-checked only — a fabricated streak at non-existent sessions (101/102) passed `--strict`. Grepped exhaustively: **no per-session revision-arc-phase completion is recorded anywhere** (`finding_states` is a rolling last-write map; `finding_deltas` carry no session ordinal; the arc is a stateless overwriting re-plan). So phase-incompletion has **no governed verification path on any project** — it is inherently self-reported. H2 now (a) does not claim a verification it cannot perform, (b) requires the honesty caveat on **every** phase-incompletion observation, governed or not. Pattern-by-pattern status is documented: `deferral-recurrence` = verified-on-governed / caveated-on-non-governed; `phase-incompletion` = caveated-always. No pattern is shape-checked-only.
- **P2 (recursive seq residue).** A `coaching_history_seq` nested under a non-home key survived `delete` (two-home strip) while H6 reported "deletion honored." Now `delete` strips the seq **recursively at any depth**, and the H6 recompute + H5.v search for it **recursively** (residue anywhere = ERROR); a seq at any non-home depth is itself flagged.
- **Depth-complete `.md` scan (class sweep item 3).** The H5 signature scan + Coaching_History enumeration now walk the project root **recursively** (`os.walk`), not `glob(root/*.md)+glob(runs/*/*.md)` — a projection or shadow Coaching_History file nested in a subdir (`drafts/ch3/`, `runs/r2/artifacts/`) no longer escapes, and `delete`/H6 reach the same depths.

Regression fixtures (self-test + `--check-all`): fabricated phase-incompletion (101/102, no caveat) FAILs `--strict`; a nested-depth `coaching_history_seq` survives the naive strip and is CAUGHT by the H6 recompute (not "deletion honored"); a projection at `drafts/ch3/`, `runs/r2/artifacts/`, `a/b/c/d/` is caught; a deep shadow Coaching_History file is counted by H5.iv and removed by `delete`. The canonical `example-coaching-history/` project is wired into `--check-all` under `--strict` with a positive run + the full hostile ethics-gate arm set + a delete round-trip.

### Intake — contract artifact name reconciled

`run-core.md` §Output: Contract Document instructed the bare `Contract_and_Controlling_Idea.md` filename while `output-structure.md` declares `[Project]_Contract_[runlabel].md` — and the qualified name is load-bearing: `/start`'s Step 0.5 contract-hash precondition locates the contract via the `runs/*/[Project]_Contract_*.md` glob, and the shipped coverage fixtures already use `Example_Contract_…`. A run following the old instruction silently broke zero-question dispatch. The qualified name is now emitted at intake. Sibling of the Pass 0 reverse-outline name reconciliation (same drifted-emitter class, same file).

### Contract Schema — narrative-nonfiction block

The Contract schema (`contract-template.md`) gains an **optional narrative-nonfiction block** — `CENTRAL QUESTION:` + `PROMISE TYPE: [Reveal / Explain / Verdict / Portrait / Lesson]` — appended when intake resolves the constraint to narrative nonfiction (`nonfiction-intake-routing.md` §Route to Narrative Nonfiction Craft). Until now `narrative-nonfiction.md`'s Central Question & Promise Map existed only as a diagnostic *procedure*; a narrative-nonfiction run had no stored contract form for its promise fields. The intake draft-then-validate step (`run-core.md` §Contract Schema) now drafts and author-confirms both fields alongside the fiction schema. LC/E lead-contract codes remain audit-time diagnostics (Findings-Ledger entries), never contract fields. This is upstream prerequisite B of the reader-contract-outline deliverable (the outline's §2 header projects these fields verbatim for narrative-nonfiction runs).

### Validators — the contradiction State axis (world-bible + continuity-bible)

Both bible Contradiction Ledgers now carry a **`State` column** — the contradiction *fact-state*
axis, orthogonal to the editorial Must/Should/Could severity scale: a self-contradiction is a
fact-state, not a defect, so it is never forced onto the severity scale (the same discipline Legal
Risk's escalation tier and Content Advisory's intensity follow). Values: `conflicting` (a live,
un-explained collision), `apparent` (a collision an override marks intentional), `consistent` (no
collision — never written as a row). **No new schema** — the column rides the existing plain-markdown
`## Contradiction Ledger`, parsed like continuity-bible's bespoke `C3` table parse.

The state is **mechanically derived, never model-judged**: a new shared helper
`scripts/contradiction_state.py` (`derive_state` — no collision → `consistent`; collision + matching
override → `apparent`; else → `conflicting`), imported by both `world_bible.py` and
`continuity_bible.py`. World-bible reuses its live `world-rule` / `world-cost` / `world-geo` per-pair
override markers; continuity-bible gains a new `bible-contradiction CF-NN/CF-MM` pair override (order-
insensitive, code-span-hardened via the `override_marker` SSoT; distinct from the `bible-rederive` C4
escape hatch). A new **`X1` firewall arm on the existing `world-bible` / `continuity-bible` validators**
(no new `AGG_VALIDATORS` entry) proves the register carries no `apodictic:finding` block and no
editorial-severity token, and that each `State` value is a valid enum token that **matches** the
mechanical derivation — an author-asserted state disagreeing with the fire/override reality FAILs
(ERROR). `conflicting` rows are surfaced for the editorial letter to cite **in prose** (Stage A wiring
— the Legal-Risk / Content-Advisory / Setup–Payoff precedent), so an unresolved self-contradiction
reaches the author's revision plan; an `apparent` (overridden) row is intentional and is not cited.

Both canonical `--check-all` fixtures now exercise the axis: `example-continuity-bible.md` carries a
`conflicting` Mara-age row and an `apparent` overridden kitchen-repaint row;
`example-worldbuilding-bible.md`'s two staged rows both derive `apparent`. Hostile self-test negatives
on both validators: a planted severity token (X1 FAIL), a planted `apodictic:finding` block (X1 FAIL),
an author-asserted State contradicting the derivation (FAIL), a `consistent` row written at all (FAIL),
a bad enum token (FAIL), and a code-span-quoted override that must not silence (FAIL). Dual-script
mirror byte-identical; the self-testable validator count is unchanged (arms-on-existing, not a new
validator).

**Fold hardening (review + code-scan follow-up).** The `X1` arm now also enforces **ledger-row
referential integrity**: over every ledger data row (all rows, pre-axis included), each row must pair
at least two *distinct* `WF-NN` / `CF-NN` ids that each resolve to a real, well-formed `world_fact` /
`canon_fact` block — a fabricated id or a single-id row FAILs (`X1 ledger integrity`) and, crucially,
never reaches the `conflicting`-row prose rollup, so a phantom contradiction can no longer be cited
into the editorial letter. **Codex-P1 hardening (world-bible), R1(b″):** the `X1` ledger-integrity
check now runs a single **identity** leg as a pure field recompute over the parsed `world_fact` blocks —
a row FAILs only when its cited facts all record the SAME normalized `(subject, value, polarity, cost)`
tuple (Codex's exact repro: two identical `place` facts labeled `conflicting`, which previously passed
clean and rolled up a phantom contradiction into the letter; it now FAILs `X1 ledger integrity` and
never reaches the rollup). **A world's collision universe is arm-defined, not subject-defined**, so
**cross-subject rows are LEGAL** — the geo arm already collides facts about different subjects (WB-G1's
reversed-distance edge `A→B` vs `B→A`, WB-G2's chronology cycle `A→B→C→A`). Round-1 (R1(b′)) added a
same-subject leg that wrongly imported continuity C3's schema and rejected both of those legitimate geo
shapes; R1(b″) **drops the same-subject leg entirely** (a round-2 Codex P1 — the round-1 fix's own
tests had encoded the overcorrection by pinning cross-subject-FAILs). Identity is the only relation
that mechanically precludes a collision; every non-identical pairing is the author's declared tension.
No arm restructuring and no semantic judgment — the register-neutral leg does not adjudicate whether
the facts truly collide (that stays the author's call). A ledger with data rows
but **no `State` column** is now a **loud pre-axis WARN** (ERROR under `--strict`) rather than silent —
the additive column is nudged, not forced. And the shared `contradiction_state.py --self-test` (the
truth-table / State-column-parse / `Statement`-decoy / X1-regex cases), previously invoked by nothing
in CI, is now wired into `continuity-bible --self-test`, so it runs under `--self-test-all`.

Anchors the axis on *Lost in Stories: Consistency Bugs in Long Story Generation by LLMs*
(Li, Guo, Wu, Lee, Li, Xie), **arXiv:2603.05890** (ConStory-Bench / ConStory-Checker — the
factual/temporal, mid-narrative contradiction taxonomy that confirms a contradiction is a locatable
fact-state) and *DOME* (**arXiv:2412.13575**) — taxonomy and benchmark only: APODICTIC's detection
stays mechanical (literal collision + override), never LLM-as-judge, the same "cite the benchmark,
don't glassbox the method" line drawn for StoryScope and Setup–Payoff. Stage B (single-substrate
merge, one fact schema, a structured `contradiction_ref` on `finding.v1`) and Stage C (the Timeline
fold) are explicitly deferred — the pre-draft *intent* vs post-draft *reality* split is load-bearing,
and Timeline's model-authored LOW/UNCERTAIN confidence rows do not fit a mechanical register.

### Evals — Corpus-expansion synthetic fixtures

Three behavioral-eval fixture sets author-added under `evals/fixtures/`, each carrying a
pre-registered `expected.md` ground-truth key (the argument-benchmark registration
discipline): **`ai-prose-calibration/`** — a synthetic AI-heavy prose sample that fires the
four previously-unexercised AI-Prose Calibration families (AIC-2 Velvet Fog, AIC-4 Register
Seams, AIC-6 Continuity Smear, AIC-8 Unearned Fluency) with named-flag invocation targets,
plus a voiced clean-control for false-positive scoring; **`tag-audits/`** — one ~500-word
scene each exercising the queer-romance-erotica, cozy, and philosophical tag audits, plus a
no-tag negative baseline; and **`execution-mode-ab/`** — a single-agent vs. multi-agent
(swarm) A/B pair sharing one manuscript with a registered real-issue-recall set and the
`docs/swarm-vs-single-eval.md` decision rule. All three are **pure data** — no mechanical
`validate.sh` arm parses them (the `argument-groundtruth-check` gate walks only
`argument-benchmark/`), and they live under repo-root `evals/` so the `codex/` + `antigravity/`
host builds are unaffected. The downstream model-run eval-coverage confirmation report is
**deferred** (per the corpus-expansion survey): these are the fixtures only, not the sign-off run.

### Editor Scaffolding — Blind-Spot Ordering

The Editor Scaffolding "What You Might Have Missed" section can now be **ordered**, closing the deferred blind-spot-ranking increment (`docs/editor-scaffolding.md` §Future increments). Opt in with a `<!-- blindspot-ranked -->` marker in the letter's E2 section: its items become an ordered, `F-…`-anchored list, verified against the run folder's Findings Ledger by four checks on the existing `editor-scaffolding` validator — **B1** every item anchors a resolvable ledger finding (a marked section with no resolvable Ledger is a hard ERROR, never a silent pass), **B2** the order is the declared key — severity band descending, then the model's **`salience`** (a new optional `apodictic.finding.v1` enum — `prominent`/`moderate`/`subtle`, read from the *ledger* finding — where `subtle` = most easily missed and leads its band), then `evidence_refs` footprint, then finding-id, **B3** severity fidelity (a restated severity token must match the anchored finding's locked ledger band **exactly** — a lower token softens/launders, a higher one inflates; both fail — the Deficit Lock holds), **B4** no duplicate anchor (WARN / ERROR under `--strict`). Salience and footprint order **only within a severity band** — the band stays dominant, so a Must-Fix can never fall below a Should-Fix whatever its salience, and salience (a descriptive judgment, never a severity input) cannot touch the Deficit Lock. Findings without `salience` order by footprint exactly as before (additive, backward-compatible). The Firewall holds: the validator invents nothing, authors no content, and changes no severity — it checks author-listed, id-anchored items against a transparent key. Ranked mode is letter/run_folder-path only (the `--per-pass` and `--dual` arms have no Ledger channel); the marker is absent by default, so every existing scaffolded letter stays green. **No** new validator (the derived self-testable count is unchanged); a canonical `example-blindspot-ranked/` run folder (letter + Findings Ledger) is exercised by `--check-all` under `--strict`.

### Operators — Editor Scaffolding dual-output

Editor Scaffolding now supports **editor ↔ author dual-output**: one diagnosis emitted as *both* the editor-scaffolded letter and its author-facing companion, for an editor who wants both. A new two-file arm on the same validator — `validate.sh editor-scaffolding --dual <editor_letter> <author_letter>` — enforces D1 (the editor letter declares the mode and passes E1–E4), D2 (the author letter is in author register: no editor marker, no Editor Brief / What You Might Have Missed / Intervention Menu, and it carries a Revision Checklist anchor — the framework never authors the prescription content, so the Firewall holds), and D3 (the top severity band matches across both letters, so the verdict class can't soften on either side). A canonical editor+author worked-example pair (`example-editorial-letter-scaffolded.md` + `example-editorial-letter-dual-author.md`) is gated under `--check-all`. No new validator — the self-testable validator count is unchanged.

### Operators — Editor Scaffolding per-pass

Editor Scaffolding now reframes **individual pass artifacts** for the editor audience, not just the synthesis letter. A new single-file arm on the same validator — `validate.sh editor-scaffolding --per-pass <pass_artifact>` — applies the operator-mode reframe to a Core DE pass artifact (`[Project]_Pass<N>_<Name>_<runlabel>.md`). A pass is a single diagnostic lens, so the contract is a right-sized subset of the letter's E1–E4: P1 (the mode marker plus a non-empty **Editor Note** addressee section — a distinct heading from the letter's Editor Brief), P2 (a non-empty **What You Might Have Missed** blind-spot section — not ranked; ranking stays deferred), and the reused W1 author-directed prescription firewall (advisory; ERROR under `--strict`). A pass has no Revision Checklist to reframe into an Intervention Menu, so there is no positive per-pass E3, and a pass may legitimately be severity-free (a Pass 0 reverse outline), so there is no mandatory per-pass severity token — severity honesty stays owned downstream by `softness-check` / `deficit-lock`. Marker-conditional exactly like the letter path (a pass artifact without the marker is a no-op), and body-scoped (before Appendix A). A canonical scaffolded Pass 2 worked example (`example-pass-scaffolded.md`) is gated under `--check-all --strict`. No new validator — the self-testable validator count is unchanged.

### Workflows — Feedback Triage structured `maps_to` (Increment 2)

A feedback item can now carry an optional **`maps_to`** field — a Finding-Lifecycle id (`F-<ORIGIN>-<NN>`) linking a triaged claim to its finding in the Findings Ledger, the structured successor to Increment 1's prose "maps to F-…" note. The field is additive: every pre-existing feedback item without it stays valid.

`feedback-triage` grows a paired-artifact cross-check (an **optional second file — the Findings Ledger**, resolved from a run folder's `*_Findings_Ledger_*.md` or an explicit file, exactly like `finding-trace` / `ledger-consolidation`). When the ledger is present it enforces two new invariants: **E5 (dangling `maps_to`)** — a hard ERROR when an item's `maps_to` names a finding that is not in the ledger (assessment-independent referential integrity, mirroring `finding-trace` E1) — and **W4 (unmapped validated)** — an advisory WARN (ERROR under `--strict`) when a `validated` item carries no `maps_to`, the checkable form of the spec's "a validated feedback item must point at a real F-…". W4 is advisory by default so a claim marked `validated` ahead of its ledger entry stays valid; `--strict` is the finalize/CI gate. Without a ledger the cross-check is skipped and single-file behavior is unchanged.

The canonical worked example is now paired with the example Findings Ledger under `--check-all --strict` (FB-01 `maps_to: F-RR-01` resolves E5-clean; no fully-validated item is left unmapped). No new validator — the self-testable validator count is unchanged (67).

### Validators — Fiction Structural Fault-Injection Benchmark (M1)

The fiction sibling of the argument-engine benchmark now ships its M1 scaffolding: a corpus-based validation harness for the Core Development Editor's structural fiction passes, scoped to a defensible construct — does the engine recover pre-registered **local** structural defects (POV break, continuity contradiction, dropped setup, orphan scene), name the mechanism, calibrate severity/repair, and leave registered intentional devices alone — explicitly NOT whole-manuscript, theme, or reader-help diagnosis. New validator `fiction-groundtruth-check` (`scripts/fiction_groundtruth.py`, dual-script mirror) is a **key-conformance gate, never a semantic judge and never a run scorer**: it checks the pre-registered answer keys for FGT1–FGT7 coverage, the multi-lane tag discipline (the architecture guardrail — `gt_class: C` may never `gate`; `gate` requires `deterministic`/`panel_confirmed` reliability, so α licenses gating rather than the author; a Lane-2 anchor must be banded with an `alpha_metric`), broken-member completeness (plant record + well-shaped locus + defect family + `Paired-with` sibling, per the mandatory matched-pair rule), the OPEN-namespace expected-surface shape + family consistency (F-P&lt;n&gt; findings validate by shape/family; `CF-NN`/`SP-NN` are disjoint cross-artifact ids recognized only for continuity/reveal, and a CF/SP-only surface is conformant — with the negated/PASS decoy masks re-grammared to the fiction surface tokens, not ported from the argument regex), FGT4 severity tokens (via the `severity_vocab` SSoT, with a severity-free `presence-delta` regime for firewalled artifact rows), and FGT7 classification (`SOUND`/`INTENTIONAL-AND-EFFECTIVE`/`DEFECT-AS-PLANTED`). The M1 kit ships `docs/fiction-benchmark-spec.md`, the FGT template, the `fiction-benchmark` rubric, and an 11-member fixture set — 4 matched clean/broken PD-derived pairs (each clean member is its bucket's airtight specificity control) + 3 standalone intentional-device controls (*The Yellow Wallpaper*, *The Gift of the Magi* stored; *A Christmas Carol* referenced via `SOURCES.md` + `run.sh --fetch`, SHA-pinned, no bytes in-repo) — all pre-registered and `--check-all`-gated. Model-convergence runs (M2a) and the ≥3-editor α-licensing panel (M2b) are doc-only, not built.

### Workflows — Legal Risk Register content-detection auto-recommend

The Legal Risk Register is now **auto-offered** for memoir / autofiction / nonfiction
portraying identifiable real people **without** an explicit `constraint:risk` flag. The
model reads the manuscript for the memoir / real-people signals (a mode signal — first-person
lived-experience retrospective, autofictional author-surrogate, or nonfiction naming/depicting
identifiable living people — plus at least one real-people content signal drawn from the module's
§Detection guidance: a reputational statement of fact about a living person; intimate private facts
about an identifiable private person; recognizable changed-name portrayal; quoted
lyrics/poetry/unpublished third-party writing; NDA/settlement-covered disclosure) and **offers**
the register. Per the maintainer's decision this is **prompt/router-only** — model-side detection
in the synthesis/routing prose, deliberately **not** a mechanical validator arm (no new validator,
no validator-count change). Offer-then-attach with an explicit confirm, and the
**flag-don't-practice-law** firewall is intact end to end: it flags/offers, never adjudicates, and
never auto-produces the register without confirm. Prose homes: `run-synthesis.md`
§Content-detection auto-recommend, `references/legal-risk-register.md` §Auto-recommend,
`intake-router-runtime.md` §3 D / §6 Table B, `pass-dependencies.md` §4a.

### Harness — Model-Capacity Exploitation M1 (dispatch observability)

The first increment of Model-Capacity Exploitation ships **observability-first, no allocator** (the repo's build-nothing-without-a-forcing-function default; the repo's own eval scorecards show no measured model-tier differential, so an allocator now would be speculation). The single missing join key — *which model each dispatched step was issued to* — is now recorded in an additive `dispatch_log` array on `apodictic.diagnostic-state.v1` (the `complexity_signals` / `synthesis_coverage` precedent: property + `$comment`, no version bump, no new schema file). Each entry is `{seq, step, model_tag, execution_mode, max_turns, provenance}`; the `step` grammar is `pass<N>` / `pass0+1` (combined triage subagent) / `synthesis` / `all-passes` (single-agent's one subagent), with `audit:*` / `prerequisite:*` / `refutation` a stated deferred extension (accepted-if-recorded, not reconciled). **Provenance honesty is pinned in the schema `$comment` and binding on every consumer:** a `dispatch-derived` entry attests the dispatch *instruction* — the model parameter the parent requested — it is **parent-requested, not platform-verified** (no host API attests which model actually served the subagent), deliberately weaker than `synthesis_coverage`'s manifest-reconciled coverage; `declared` marks an inline step with no dispatch event, and provenance tracks the host's per-entry dispatch capability, **not** the run's mode (a no-shell host legitimately records all-`declared` entries under `execution_mode: sequential`). New validator `dispatch-record` (`scripts/dispatch_record.py`, dual-script mirror, bash-degrades-to-advisory) runs R1–R5: R1 presence (advisory-first; key-absent = pre-adoption grandfather / silent PASS, present-but-`[]` = a post-adoption recording failure that fires); R2 pass-artifact + synthesis-letter coverage per the satisfaction map (`pass0+1` satisfies both Tier-1 artifacts, `all-passes` is exclusive; artifact-with-no-entry FAILs only under `--strict`, entry-with-no-artifact WARNs never FAILs); R3 tag vocabulary parsed from the `output-structure.md` model-tag table (SSoT-by-reference; the literal `unknown` is a sanctioned PASS; a zero-row table parse exits 2 `model-tag-table-unparseable`, never accept-everything); R4 per-entry shape (no mode-based provenance FAIL); and R5 escalation cross-check (at most one mode transition; final entry mode == `last_session.execution_mode`), WARN-first with `--strict` promotion. `dispatch-record --report <project_dir>` is a read-only cross-run scan that gates nothing and surfaces the **M2 demand signal** — the count of `quality_risk_override` records (matched via the shared `override_marker` SSoT, meta-lint M5) and how many carry a budget-flavored rationale — so the M2 tier-experiment trigger is mechanically visible rather than recorded-but-invisible (the CR-6 detectability discipline). Two false claims in `output-structure.md` are **corrected** (not merely clarified): the per-file / per-output model-tag claims are structurally false under the single-`runlabel` filename grammar — every pass file in a run shares one runlabel, so per-file tags cannot exist in filenames; `dispatch_log` is now named the per-dispatch SSoT. `run-core.md` gains recording sentences at Execution Protocol steps 7 (both branches, plus the single-agent declared variant) and 10 — zero behavioral change. The two canonical coverage run folders (`references/example-run-folder-coverage` / `-degraded`) gain populated `dispatch_log` arrays so R1–R4 run against real data in `--check-all`, alongside a parser-has-teeth proof (the R3 table parse extracts the six known tags from the shipped `output-structure.md`) and an R5 stale-mode hostile arm (WARN by default, FAIL under `--strict`). M2 (the pre-registered tier experiment) and M3 (contract-time advisory allocation) remain evidence-gated with named triggers.

### Writer-Question Surface Hardening — macro-map SSoT + pass headers

Locked `pass-dependencies.md §3` (Macro Block Definitions) as the **single source of truth** for the 8 macro blocks, the pass→block map, and each block's writer-facing `User Question`. The §2 concern resolver, the `core-editor/SKILL.md` pass-header mapping, and the per-pass artifact header all now read from §3, never re-author it (Writer-Question Surface Hardening #3). `audit-signal-propagation` / `audit-tier-criterion` read §4 and are unaffected — ripple-verified unchanged.

Each Core DE pass artifact now begins with a §3-sourced blockquote header — `> **Macro block:** … · **Writer question:** … · **Legacy pass id:** Pass N` — so a directly-opened detail file is legible without framework knowledge (#4). The values are read from §3, and a concern-driven run that pulls a dependency pass outside its usual block still declares the pass's **own** canonical §3 block (the map is by pass, not by run). New `pass-header` validator (`config_checks.py`, dual-mirrored): **H1** header present (a header-less legacy artifact WARNs, not ERRORs); **H2** the Macro block is one of the 8 and matches §3's pass→block map for the Legacy pass id, and the Writer question matches §3's User Question; **H3** all three fields non-empty. A Legacy pass id that §3 does not map is a present-but-wrong value and **ERRORs** (either the header is wrong or §3 must be updated in the same change) — WARN marks absence only, never a wrong value. Absent python3 the arm degrades to the fleet advisory-WARN convention (skip + inline-check guidance), not a bash reimplementation of the §3 parse. Wired into `--check-all` against the real `pass-dependencies.md §3` via the canonical `example-pass-artifact-header.md`, and header emission added to `run-core.md`'s pass-emission instructions.

### Pass 0 — reverse-outline artifact name reconciled

`run-core.md` §Pass 0 was the last emitter of the bare `Reverse_Outline.md` filename while `output-structure.md`, `pass-dependencies.md`, and `partial-manuscript.md` all declare `[Project]_Pass0_Reverse_Outline_[runlabel].md`. The project-qualified name is now canonical everywhere (it matches the runlabel convention every other run artifact uses); no script read either name. This is upstream prerequisite A of the reader-contract-outline deliverable, whose scene spine is located by the `*_Pass0_Reverse_Outline_*` glob.

### Annotated-Manuscript Export — PDF Proofing Target (`pdf-export`, P1–P3)

Added a **4th projection** of the gated annotation manifest beside the shipped Obsidian / HTML / DOCX
targets: a self-contained, **byte-deterministic `.pdf`** (`scripts/annotation_export.py pdf`) the writer
opens in any PDF reader — the proofing/annotation deliverable. Written **by hand from raw PDF objects,
stdlib only** (no reportlab/fpdf): a `%PDF-1.4` header, numbered `/Catalog` → `/Pages` → per-page
`/Page` + uncompressed `/Contents` objects, a base-14 `/Helvetica` `/WinAnsiEncoding` font, an `xref`
table, and a trailer. The snapshot prose renders as text with a `[<finding_id>]` marker spliced at each
anchor locus (the HTML `<sup>` precedent, via the same `_insertion_offset` splice) and each verbatim
comment lands in a trailing **Findings** section, char-wrapped so the chunks concatenate back exactly.

**Byte-determinism** (the DOCX discipline, for a different binary): **no `/Info` dict** (so no
`/CreationDate`/`/ModDate`), **no `/ID`** array, **no stream compression** (no zlib drift), all shown
text emitted as **octal-escaped ASCII** (`\247` → §, interpreted by `/WinAnsiEncoding`), fixed object
order, xref offsets from byte lengths — no wall clock, no random. Two renders are byte-identical.

New **`pdf-export`** validator gating the on-disk artifact: **P1** artifact integrity (on-disk == fresh
build byte-for-byte — the authoritative lock), **P2** text round-trip (manuscript runs, markers stripped,
reproduce the snapshot), **P3** marker resolution + comment fidelity (markers ↔ manifest set bijection;
each Findings chunk group concatenates to the verbatim comment). Ships the canonical
`example-annotated-manuscript/pdf/` fixture wired into `--check-all` (byte-identical to a fresh render;
`*.pdf binary` added to `.gitattributes`), a `--self-test` with a hostile `( ) \ §` escape/offset case,
and the degrade-to-`WARN`-without-python3 arm. **Validators +1 → 68** (the count stays DERIVED from
`AGG_VALIDATORS`). Docs: `docs/annotated-manuscript-export.md` §Increment 5.

### Specialized Audits — Position-Pair Register consumer wired

Wired the **Position-Pair Register** consumer of SETEC's `position_pair_register` surface (stance-consistency PR 2). The surface reads one long nonfiction argument-shaped work and emits a register of passage PAIRS that address the SAME question Q — each pair a neutral interrogative question + both passages' verbatim loci, in DOCUMENT ORDER. It asserts NO relation between the passages (not agreement, conflict, contradiction, or tension) and does not rank by disagreement; the HUMAN reads both and owns 100% of the conflict call. This is the fleet's deliberate NON-step across the content-verdict wall: the model points at two passages sharing a question; the writer decides whether they conflict, evolved, or were mischaracterized. It sits further from the Firewall than any other consumer — where ArgScope's consumer derives an editorial signal mechanically, this one derives nothing and runs gates only.

New shim `scripts/ai_prose_position_pair_register.py` (`SURFACE = "position_pair_register"`), mirroring the argument-decision consumer: floor-from-manifest (`min_setec_version: 1.121.0`, the first release tag carrying the surface — the first-tag convention), the R2 dispatcher enforcing the floor at runtime (no redundant consumer-side pre-check), `handoff: experimental`, `calibration_status: uncalibrated` (an LLM extraction surface is not bit-deterministic — human re-review absorbs the drift). It pins the `results.pairs` payload + the refusal/cap disclosures and the `claim_license`, never a verdict, relation, or aggregate (there is none).

New `position-pair-register` validator (`position_pair_gates.py`, dual-mirrored) — the "claim-surface-asserts-it" firewall for the register artifact, over three inputs (the rendered artifact, the JSON envelope, the manuscript the consumer holds): **Q1** a two-layer recursive banned-KEY walk over the envelope (relation keys never legitimate anywhere; generic verdict keys scoped to `results.pairs` — KEYS only, since `claim_license` VALUES legitimately carry relation words; the walk shape from setec-voiceprint PR #298's `test_envelope_carries_no_verdict_keys_recursive`, not its key list); **Q2** a verbatim re-check of every quote against the manuscript with the F1 punctuation-fold (NFC → typographic quotes to straight → all Unicode dashes to `-` → `…` to `...` → Zs spaces to U+0020 → newline to space → whitespace-run collapse) — a fabricated or paraphrased quote DROPS the pair with an inspectable log line + a counted `pairs_dropped_quote_mismatch` disclosure + WARN (a drop is a disclosure, not an error; `--strict` FAILs); **A3** no `Must/Should/Could-Fix` severity leak and no `apodictic:finding` block (the content_advisory A3 firewall); **F5** the framing-prose relation-vocabulary scan over the consumer's OWN text, exempting a `>`-blockquote line ONLY when its text (after an optional `A:`/`B:` side label) fold-matches the manuscript verbatim — the author's quotes may carry such words, but a non-verbatim blockquote is framing dressed as evidence and is scanned (the exemption is verbatim-bound, never merely structural or a per-token allowlist); and a document-order check (the artifact must present pairs in envelope order — re-ranking is a judgment channel the posture forbids; an artifact with no parseable `### <n>. Q:` headings makes the order UNVERIFIABLE → WARN, never a silent skip). Unreadable inputs fail closed. Canonical `example-position-pair-register` fixture (manuscript + envelope + rendered register) wired into `--check-all` under `--strict`; hostile self-test matrix covers the paraphrased-quote drop, the F1 smart-quote/em-dash/ellipsis/NBSP fold, a planted Must-Fix / finding block, an injected relation key (whole-envelope) and verdict key (pairs-scoped), a relation-vocabulary framing line, re-ranked pairs, and each fail-closed path.

Rooted in **ContraDoc: Understanding Self-Contradictions in Documents with Large Language Models** (Li, Raheja & Kumar; arXiv:2311.09182 — the contradiction-type taxonomy informs what "same question" pairing must catch) and **BeliefShift** (Myakala, Agrawal & Manche; arXiv:2603.23848 — the position-drift framing).

### Validators — Canonical Release Gate

`quality-risk-triggers` now runs as a canonical release gate. Added
`core-editor/references/example-quality-risk-contract.md` — a clean, well-formed,
low-risk Contract worked example (single-POV literary family drama, moderate
darkness, mid-draft developmental goal) that raises none of the five pre-pass
quality-risk triggers (Q1-Q5) — and wired it into `validate.sh --check-all`: a
clean arm asserts the canonical contract exits 0, plus a hostile arm that flips
its darkness rating to the top setting on a throwaway copy and asserts the Q1
consent/governance trigger fires and exits non-zero (gate proven to have teeth).
This closes the last gap in the "canonical-framework validator runs as release
gate" track — every validator with a single-artifact canonical target is now
gated against the shipped framework, not only its own synthetic fixtures.
Validator count unchanged (67); no new validator.

### Deliverables — Reader-Contract Reverse Outline

The third finalized third-party developmental-edit deliverable now ships (alongside the editorial letter and the Annotated Manuscript): a reverse outline that lays the book out **scene by scene** and maps it against the **reader contract** it implicitly makes — where each promise is established, where it's paid off, and where it breaks. Like the Annotated Manuscript, it is a **byte-deterministic projection** of artifacts that already exist (the Pass 0 reverse outline, the Contract, the Findings Ledger); the model's only authored contribution anywhere in the deliverable is a gated, ids-only **Contract Map** (`apodictic.contract_map.v1`, closed-key), which localizes each contract clause to the scenes that establish and pay it off. New validator `reader-contract-outline` (`scripts/reader_contract_outline.py`, dual-script mirror) runs the R1–R7 gate: R1 scene-spine round-trips to Pass 0 verbatim; R2 two-sided contract-field fidelity (empty fields render their literal state, none dropped/invented); R3 the rendered Contract Map ↔ Map-block bijection with every evidence line byte-matching the cited scene's Pass 0 "what the reader now knows" line; R4 no fabricated gap (each gap cell is `none logged` or the verbatim Ledger projection); R5 no untranslated framework shorthand in the deliverable; R6 the READER-PROMISE split-completeness coverage (advisory WARN, ERROR under `--strict`, override via the `override_marker` SSoT slug `reader-contract-coverage`); and R7 map integrity (Mode-11 untrusted input — closed-key schema, `inputs.*_sha256` bound to the staged artifacts so a stale Map fails loudly, every `clause_text` a verbatim substring of its named Contract field, the clause denominator recomputed from the Contract, never trusted from the Map). Offered at run-end (sibling to the Annotated Manuscript, gated on a `*_DE_Synthesis_*` letter + `*_Pass0_Reverse_Outline_*` + `*_Contract_*`) and regenerable from `/start`'s `diagnosed` node. Scope: fiction (the full 10-field contract schema) and narrative nonfiction (the optional `CENTRAL QUESTION` / `PROMISE TYPE` block drives the idea clause); argument-shaped nonfiction is deferred. Canonical fiction + narrative-nonfiction fixtures ship under `references/example-reader-contract-outline/` (the repo's first artifacts using the reconciled Pass 0 name), exercised with hostile arms in `--check-all`.

### Research — Reliability Layer strict halt + sidecar (OQ-1, OQ-3)

Two additive, stdlib-only follow-ons to the Research / API Reliability Layer, both
off by default so existing (non-strict) behavior and the AC-1..AC-13 contract are
unchanged. **OQ-1 (`--strict` halt):** `academic_apis.py batch --strict` (and
`resolve_batch(..., strict=True)`) now HALTS a high-stakes run — non-zero exit
(`STRICT_HALT_EXIT_CODE` = 3) plus a `reliability.strict` sub-block
(`{enabled, halt, reason, degraded_providers, not_checked}`) — iff coverage ended
DEGRADED (≥1 degraded provider) **and** ≥1 citation was NOT-CHECKED, so a degraded
verdict can no longer be emitted as a clean not-found. The halt is one-directional:
a clean run, a non-strict run, or a genuine all-healthy NOT-FOUND (NOT-FOUND ≠
NOT-CHECKED) never fires it, and with `APODICTIC_RELIABILITY=off` there is no
degradation signal to trip it. **OQ-3 (`Citation_Reliability.json` sidecar):** a
pure serializer `build_reliability_sidecar` + writer `write_reliability_sidecar`
(schema `apodictic.citation_reliability.v1`, deterministic `sort_keys` order)
persist budget-spent, circuit states, coverage/degraded_providers, per-provider
snapshot, events, and the resolved/not_found/not_checked summary; opt-in via
`batch --sidecar-dir DIR`, and it never mutates the in-`output` `reliability` block.
Both modules' `--self-test` gained coverage (halt fires only on genuine degradation;
sidecar shape, determinism, and disk round-trip); OQ-2 (telemetry-tuned budgets)
stays open.

### Writer-Question Surface Hardening — Results Guide wired + validated

Wired the **Results Guide** deliverable (`[Project]_Results_Guide_[runlabel].md`, Writer-Question Surface Hardening #5) into the run flow and added a validator for it. The Guide is a plain-language **navigation index** — the first file after the editorial letter — mapping each writer question the run produced (the §3 `User Question` for each macro block that ran) to the run-folder artifacts, specialized audits, and state files behind it, so a writer can navigate their results without framework knowledge. Its template already lived in `core-editor/SKILL.md §Results Guide Artifact`; this change wires its emission (a standard deliverable, not an offer) into `run-synthesis.md §Core DE Deliverables` — the template is emitted as-is, never re-authored.

New `results-guide` validator (`results_guide.py`, dual-mirrored) — **one arm, three checks, R2 load-bearing**: **R1** membership (every `### <question>` heading matches a canonical §3 User Question, reusing `config_checks._parse_section3` against the real `pass-dependencies.md §3` — an invented block ERRORs; a run that produced only some blocks is legal, so listing fewer questions is fine, inventing one is the defect); **R2** referential integrity (every backtick `.md`/`.json` citation resolves to a run-folder file; citations must not escape the run folder — an absolute or traversal/subdir path (`../outside.md`, `/etc/x`) FAILS; an un-substituted `[…]` placeholder or a dangling citation ERRORs; the "What to do next" `/coach` / `/audit [name]` command tokens are exempt via the `.md`/`.json` extension guard so they never false-fail); **R3** hygiene (no `Must/Should/Could-Fix` severity leak — the same posture `content_advisory` A3 enforces — and no `apodictic:finding` block, so the index never masquerades as a second letter). R1/R3 ride along inside the single arm as cheap checks; there are no standalone arms. R1 degrades to a skip when §3 is unavailable, and an unreadable run folder fails closed with a named error. Absent python3 the arm degrades to the fleet advisory-WARN convention (skip + inline-check guidance), not a bash reimplementation. Wired into `--check-all` against the canonical `example-results-guide` run folder.

### Harness — Runner-Governed Execution + Finding Lifecycle IDs increment 4 (cooperative slice)

`finding-trace` is now a **mechanical row in the `run_spot_check` gate** (`schemas/execution-gates.v1.json`), closing the live gap where the letter-ID-must-exist-in-ledger (smuggled-finding) gate was prose-invoked while the manifest pointed at `finding-trace` as its owner without running it. E0 (unparseable sidecar) / E1 (dangling letter ref) / E2 (phantom `finding_states` key) / E3 (invalid state) now **block the clear** (exit 1). The row asserts **referential integrity at delivery time, NOT ordering**: W1 is gated on the folded pointer having reached a synth-cleared phase, so on an out-of-order spot-check it self-skips and the row produces no order signal — external ordering enforcement stays the deferred host layer's job.

**In-flight-run note:** a governed run with a `run_spot_check` `mechanical-passed` pending from before this release will now re-check `finding-trace` at `--attest` time; a letter that cites a phantom `F-…` id blocks cleanly (never a crash or a false clear).

The clearing event (`gate --attest` / a no-attest clearing `passed`) now prints the **per-ID finding trace** (`severity · state · cited? · rev=`) and a **`T4-watch: N deferred orchestrator-pull-interface marker(s)`** line — the mechanical, per-clear surface for a Runner-Governed Execution defer-trigger (CR-6 detectability). `gate --check-state` prints an **`open exceptions: N (skipped · deferred · pass-with-warn · mechanical-passed · blocked)`** count line.

On **governed** sidecars, `finding-trace`'s E5 (phantom completion) widens its in-scope set to the ids a clearing event of *this run* advanced to `revised` — so a resolved marker removed *after* the gate cleared (post-clear tampering) is now caught. The E5 predicate and the resolved-marker union across all completion artifacts are unchanged; ungoverned sidecars keep today's mention-scope behaviour byte-identically.

The **external host orchestrator (M2)** — a Claude Code plugin-hook set that would refuse an out-of-order write — is **deferred with four detectable triggers**: no post-v2.1.0 skipped-gate incident is recorded, so the revisit clause has not fired. The chosen shape, the rejected shapes, and the parked cooperative alternative are recorded in the spec. No new validator, no validator-count change.

### Audit-Signal Propagation — §4e is now the source of truth

`pass-dependencies.md §4e` (Audit-Signal Propagation Table) now formalizes an explicit **six-column contract** — *Audit · Audit-internal signal · Synthesis severity (required-severity) · Context modifier · Source · Override (override-modifier)* — with each column's semantics named in prose so the table is machine-parseable. The Override column gains a formalized per-audit **override-modifier directive** (`propagate-override: <signal-class> → <synthesis-severity>`) that reassigns the required synthesis severity for an audit's strong signal class without editing Python. The `audit-signal-propagation` validator (`letter_checks.py`) is now **driven by §4e**: it parses the signal-class → synthesis-severity mapping from the `#### Default mapping` block instead of a hardcoded in-Python default map, applies per-audit `propagate-override:` directives, and reports a **malformed §4e mapping** (unrecognized severity, missing strong-signal class, or malformed directive) as an ERROR rather than silently defaulting. On the real committed §4e the parsed mapping reproduces the historical hardcode exactly, so the port is **oracle-identical** — `audit-signal-propagation --check-registry`, the byte-identical §4e diff, and `argument-carve-behavior-preservation` all pass unchanged. Two hostile self-test fixtures were added (a per-audit modifier that reassigns the required severity is honored; a malformed §4e row/directive is caught). No new validator — the derived self-testable count is unchanged (67).

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

### Validators — severity-token vocabulary SSoT (`severity_vocab`) + meta-lint M8

The editorial-severity leak token `\b(?:Must|Should|Could)-Fix\b` — the A3 Content-Advisory firewall vocabulary reused by the X-gate Author-Style / Author-Voice firewalls, the Results-Guide navigation-index guard, and the Setup-Payoff / Contradiction-State fact-register guards — had accumulated **six byte-identical hand-synced copies** (`_SEVERITY_RE = re.compile(...)` in `content_advisory`, `results_guide`, `contradiction_state`, `setup_payoff_checks`, `style_explanation`, `author_fingerprint`), kept in sync only by "copied from `content_advisory._SEVERITY_RE`" comments, with a seventh forming on an open PR. The pattern now lives once, in `severity_vocab.SEVERITY_TOKEN_RE`; every leak-guard imports it (the local `_SEVERITY_RE` is an alias binding, so all `.search()` call sites are byte-identical and every validator's self-test passes unchanged — the adoption is provably faithful: `content_advisory._SEVERITY_RE is severity_vocab.SEVERITY_TOKEN_RE`). New meta-lint rule **M8** bans a local re-definition — it flags a `re.compile` whose literal carries the grouped three-modal `(?:Must|Should|Could)` alternation (and its re-spellings: a capturing group, a reordered alternation), directing the author to `from severity_vocab import SEVERITY_TOKEN_RE`. M8 is deliberately narrow to the modal-alternation shape, so the fleet's other legitimately-different severity patterns — `editor_scaffolding`'s `(Must-Fix|Should-Fix|Could-Fix)` token alternation, `disposition_check`'s `(Declined|Deferred) Must-Fixes` caveat line, `letter_checks`' single literals — are not flagged, and a `Must-Fix` named in prose / a docstring is not flagged (comments + docstrings stripped first). `severity_vocab.py` (the SSoT) is exempt; the meta-lint self-test proves M8's teeth with a doctored source. `docs/validator-conventions.md` is brought current to **M1–M8** (it had drifted, documenting only M1–M5 while M6 code-span hygiene and M7 single-Firewall were already live). No behavior change to any validator; no new `AGG_VALIDATORS` entry.

### Validators — Architecture Hardening (Increment 8)

Ported the last four bash-regex prose/filename validators onto the shared
parsers, completing the editorial-letter / ledger family. `ledger-check`,
`synthesis-sections`, and `tone-check` now run through `letter_checks.py`
(heading-anchored section matching that kills the mid-heading substring
false-positive; body-only, code-span-stripped, blockquote-skipped superlative
scanning so a superlative quoted in an appendix, a code fence, or an author
blurb no longer false-fails); `artifact-names` runs through `config_checks.py`
with the project/runlabel matched as literals. Each keeps its exact legacy
output contract (verified byte-identical against the pre-port arm) and its bash
implementation as the no-`python3` degrade path, and gains fixture-driven
negative tests.

### Manuscript Visualizations — Beat-Map Against Spine (chart 7-fiction)

Built the beat-map-against-spine (chart 7-fiction) over a new `apodictic.story_spine.v1` **producer**:
the chosen fiction spine and its ordered beats (`beats: [{beat, scene_id, anchor}]` + a top-level
`spine_framework`). The `spine_framework` is a token in the **closed 50-spine plot-coach taxonomy** —
`plot-architecture/SKILL.md` §Spine Families (50 Spines, 12 Families) — and each spine's own named,
ordered beats live in its "On the page" line in `plot-architecture-audit.md` (e.g. Seven-Point (Dan
Wells): Hook → Plot Turn 1 → Pinch 1 → Midpoint → Pinch 2 → Plot Turn 2 → Resolution). The `beat` name
stays a **free non-empty string** because beats are open per framework and are not exhaustively
enumerated (the `scene_roster.v1` character-name precedent). The `manuscript-viz` gate gains **X9**
(beats byte-checked against the producer + Timeline: beat → producer beat; manifest scene_id == producer
scene_id and resolves to a Timeline row; producer spine_framework ∈ closed 50-spine enum; producer beat
+ anchor non-empty and, when line-range-shaped, overlapping the scene's Timeline line-range), and the
**X8** producer-present rule so a present `beats[]` is legitimate iff it byte-checks against the
producer — **retiring the last producer-gated chart** (no producer-gated chart remains). The renderer
draws a deterministic beat-map along a single spine rail (one node per beat, in spine order, at its
mapped scene, with the framework as caption — no style in the manifest, no time/random). Beats are keyed
directly on `scene_id` (per-scene, like scene_roster/scene_function/tension_point) — no `evidence_ref →
scene_id` resolution. Adds the `apodictic.story_spine.v1` schema + its `_coverage.json` binding
(`closed_keys:true`), the new `beats[]` manifest array on `apodictic.viz_manifest.v1`, and the worked
`example-story-spine.md` fixture (paired to `example-timeline.md`), gated by `--check-all`. No new
validator — the count stays DERIVED.

### Manuscript Visualizations — Reveal-Economy / Tension Timeline (chart 4)

Built the reveal-economy / tension timeline (chart 4) over a new `apodictic.tension_point.v1`
**producer**: a per-scene reader-tension pass (`points: [{scene_id, tension, anchor}]`) whose `tension`
is a token on the closed reader-dynamics **Pass 1 (Reader Experience) 1–5 intensity scale** — the Pacing
Heat Map's "intensity level (1-5 scale derived from Pass 1 emotional tracking)" (1 = flat, 5 = peak). The
`manuscript-viz` gate gains **X4** (reveal_points byte-checked against the producer + Timeline: scene_id
→ producer + Timeline row; manifest tension == producer level; producer tension ∈ closed 1–5 enum;
producer anchor non-empty and, when line-range-shaped, overlapping the scene's Timeline line-range), and
the **X8 flip** so a present `reveal_points[]` is legitimate iff it byte-checks against the producer —
retiring the last producer-gated hard-fail array (only chart 7-fiction's beat-map remains gated, and it
has no manifest array). The renderer draws a deterministic tension-over-scene-order timeline (tension
level on the y-axis, scene order on the x-axis, a polyline through one point per scene at its declared
level, from a hardcoded level → y-position map — no style in the manifest, no time/random). Tension
points are keyed directly on `scene_id` (per-scene, like scene_roster/scene_function) — no
`evidence_ref → scene_id` resolution, so that overlay stays explicitly out of scope. Adds the
`apodictic.tension_point.v1` schema + its `_coverage.json` binding (`closed_keys:true`) and the worked
`example-tension-points.md` fixture (paired to `example-timeline.md`), gated by `--check-all`. No new
validator — the count stays DERIVED.

### Manuscript Visualizations — Scene-Function Heatmap (chart 6)

Built the scene-function heatmap (chart 6) over a new `apodictic.scene_function.v1` **producer**: a
per-scene structural-function pass (`functions: [{scene_id, function, anchor}]`) whose `function` is the
scene-turn audit's Step-1 Unit Classification — the closed set `scene | sequel | hybrid | non-unit`. The
`manuscript-viz` gate gains **X3** (scene_functions byte-checked against the producer + Timeline:
scene_id → producer + Timeline row; manifest function == producer classification; producer function ∈
closed enum; producer anchor non-empty and, when line-range-shaped, overlapping the scene's Timeline
line-range), and the **X8 flip** so a present `scene_functions[]` is legitimate iff it byte-checks
against the producer (`reveal_points` stays producer-gated). The renderer draws a deterministic
scenes × functions grid (one shaded cell per scene at its declared function column, from a hardcoded
function → colour band — no style in the manifest). Adds the `apodictic.scene_function.v1` schema + its
`_coverage.json` binding (`closed_keys:true`) and the worked `example-scene-function.md` fixture (paired
to `example-timeline.md`), gated by `--check-all`. No new validator — the count stays DERIVED.

### Writer-Question Surface Hardening — skill names scrubbed, handoff convention codified

Closed the last two Writer-Question Surface Hardening items (#6 skill-name scrub, #7 handoff-language standardization). A completed inventory across the committed tree found the writer-facing surfaces near-clean already: the one residual writer-rendered leak — the `/apodictic` capability-index body — was rewritten from "the commands sit on five skills: **core-editor** (…)" to workflow language naming **six capability areas**, which also fixed a stale five-vs-six count that had omitted the nonfiction argument engine. The classification rule is the firewall: scrub **writer-rendered prose only**; agent-routing/delegation prose the model reads to dispatch (the Delegation Rules zone, Genre Module Routing activation notes, `commands/*.md` load-directives, inter-skill reference lists, run-flow load instructions) legitimately names skills and stays untouched — rewording it would risk breaking routing for zero writer-visible gain.

The durable #7 guarantee is a convention, not the single edit: a new **§Author-Facing Language** subsection in `core-editor/references/output-policy.md` now requires writer-rendered and all generated author-facing prose to name the **command** (`/coach`, `/audit`, `/plot-coach`) or the **workflow move** ("run an audit next," "plan revision next"), never the skill slug — a backticked slug wrapped inside a workflow noun ("the `specialized-audits` workflow") is still a slug — with a boundary note distinguishing it from the framework-*code* glossing that `author-facing-lint` enforces on the generated letter body. No new validator: the committed scrub set is one line wide and the ROADMAP itself records "no user-facing pain found" and "skill loading is invisible to users," so a `skill-name-lint` arm is deferred until a demonstrated regression need. The vendored siblings (APODICTIC-Gemini, apodictic-tauri) carry the old prose byte-for-byte and pick up the fix via the next `sync:plugin` machine re-vendor after a release.

## v2.7.0 - 2026-07-02

### Disposition supersedence is recomputed, never trusted (disposition-check DP2.6)

Sibling-sweep fix from the PR #161 Codex P1 class (an exemption gate trusting a recorded field):
`disposition-check`'s `active()` exempted a declined/deferred Must-Fix from the DP1 readiness
caveat on the sidecar's self-reported `finding_states[id] == "revised"` alone — one JSON field
edit on a non-governed sidecar waived the caveat, silenced the DP2.5 sync audit for the id, and
no validator on the enforcement path corroborated (finding-trace E5 is deliberately scoped to
report-mentioned ids; `/ready` runs only `disposition-check` at verdict time). Supersedence now
requires a corroborating `<!-- resolved: F-id -->` marker in a reachable completion artifact
(run folder, project root, or `runs/*` archives — evidence-only, so DP2.1's same-run scoping is
untouched); an uncorroborated `revised` leaves the disposition ACTIVE (DP1 caveat still owed)
and is surfaced as the new **DP2.6** WARN (ERROR under `--strict`). Adds 10 self-tests (the
`disposition-check` suite → 46): the keystone exploit repro, archived-evidence exemption,
evidence-not-leaked negative, DP2.5-no-longer-suppressed, non-UTF8 evidence fails closed, and a
run-folder + `runs/*` end-to-end both directions; `--check-all` gains hostile arm 4 (fabricated
supersedence must fail closed). Build-review folds: `_read` gains the `UnicodeDecodeError` guard
(the adjacent-exception class this PR later seeded a repo-wide sweep for), and the trusting-rule
sentences in `state-lifecycle.md` / `submission-readiness.md` are amended to the corroborated
form. Spec: `docs/disposition-supersedence-recompute.md`.

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

### Finding Dispositions — engine-level `declined`/`deferred` set-asides

A deliberately set-aside finding is now a mechanical record, not a prose note a later session must
remember to read (`docs/finding-dispositions.md`). Dispositions are an **overlay**, never a fourth
lifecycle state: `execution.finding_dispositions` maps `F-id → apodictic.finding_disposition.v1`
(new closed-key schema, no severity field by construction) beside an untouched
`finding_states` — the fold stays rank-monotonic, finding-trace E3 unchanged. Pinned durable
markers (`<!-- declined: F-… — reason -->` / `<!-- deferred: F-… until: trigger — reason -->`) are
the canonical source, with ONE shared grammar helper (`apodictic_artifacts._DISPOSITION_RE` +
`parse_disposition_markers()`, code-span-stripped via the `override_marker` SSoT) imported by both
`run_gate.py` and the new validator. Dual writer mirrors `revised` exactly: governed projects
freeze full records into `gate_events[].disposition_deltas` at `revision_round` clear (fold-derived
map, `pointer == fold`, same-event revise+disclaim launder rejected by `gate-state`); non-governed
projects write the validated record directly. New `disposition-check` validator (self-testable
count is derived): DP0 record shape (trigger-iff-deferred), DP1 the `/ready` teeth — an active
declined/deferred Must-Fix must be named on the assessment's pinned `**Declined/Deferred
Must-Fixes:**` caveat lines, run BEFORE the verdict is delivered — and DP2 no-laundering
(same-run resolved+declined contradiction, phantom keys, ledger↔calibration severity mismatch,
triage-tally decrement via the shared `structured_findings.severity_tally`, bidirectional
marker/sidecar sync with governed-lag exemption). Canonical fixture
`references/example-run-folder-dispositions/` wired into `--check-all` with three hostile arms
(caveat stripped → DP1 fails; trigger stripped → DP0 fails; record dropped → DP2.5 warns, `--strict`
fails). Consumers: the revision-coach Loop Dispatch skips declined ids, trigger-reviews deferrals
(ISO dates fire mechanically), and records set-asides at the stalled off-ramp; `feedback-triage`
gains W3 (a declined item citing a ledger `F-…` id with no recorded disposition) plus the
decline-reconciliation offer; `/ready` gains the caveat block + a `CONDITIONALLY VIABLE` ceiling
for undisclosed declined Must-Fixes (fired deferrals count as open); the roundtrip resume displays
active dispositions and never machine-proposes `declined`/`deferred`. State gardening preserves
active disposition markers and compresses superseded ones to the archive line form. The honesty
gates (`softness-check`, `deficit-lock`, `severity-floor`, `structured-findings`, `finding-trace`,
`regression-diff`) read dispositions nowhere — a disposition grants no severity relief and never
decrements a count.

### The Firewall — claim honesty

Reframed the Firewall's user-facing claim to match what the audit actually does. The absolute "it never invents content — no new plot events, characters, dialogue, or imagery" overstated the boundary: the audit routinely (and usefully) names that a structural element is missing or mis-weighted — "the climax needs a cost paid on-page," "this character carries no climactic agency," "this argument never re-qualifies its scope" — which is a *class of solution*, not content invention. The honest line is **never drafts your prose and never scripts the specific content (events, characters, dialogue, evidence)** — not *never names a needed element*. Updated the canonical `references/firewall.md` (with an explicit naming-a-need-vs-inventing-content distinction), the README ("How It Works" + Key Terms), and the `/apodictic` command (whose canonical pointer now targets `references/firewall.md`).

### Workflows — Multi-Session Revision Arc Planning

New revision-coaching capability: a **phased multi-week revision arc** (Phase 1 structural root causes → Phase 2 downstream consequences → Phase 3 polish) that sequences the full Findings Ledger — the layer **above** the per-session Loop Dispatch, and the generalization of Retcon Planning's single-decision arc to the whole Ledger. The coach SEQUENCES findings; it never prescribes execution (the Coaching Firewall). Adds the `apodictic.revision_arc.v1` schema (one block per manuscript; `phases` an ordered list, ≥1, no fixed 3-enum; stateless re-plan with no round/version field), the `revision-arc` validator, the `multi-session-arc-planning.md` skill (revision-coach mode 8), `docs/multi-session-arc-planning.md`, and the canonical `example-revision-arc.md` gate.

**Honest posture (the Retcon pattern — load-bearing).** The Root-Cause mapping is not machine-readable (`finding.v1` carries only structured `severity`; the diagnostic-state root-cause map is prose), so the coach's dependency reasoning is **trusted, not gated**. The `revision-arc` validator gates the PLAN's **provenance + self-consistency + firewall only** — **A1** schema + nested phase shape, **A2** provenance closure (every `finding_ref` resolves to a real Ledger finding), **A3 self-consistency ONLY** (each finding in exactly one phase; a Must-Fix finding the arc *itself* labels a structural root cause is not parked in the polish phase — **not** a true-causal-graph check), **A4** non-empty sequencing rationale; advisory **W1** firewall-drift (a rationale that prescribes execution) and **W2** orphan (a Must-Fix Ledger finding absent from the arc).

### Nonfiction Argument Engine — Modularization (Workstream A)

Promoted the nonfiction argument path from implicit to named and bounded:

**Named skill.** `skills/nonfiction-argument-engine/SKILL.md` is now a first-class skill alongside `core-editor`, `specialized-audits`, `revision-coach`, and `plot-architecture`. The skill defines the delegation contract (triggered from `core-editor §Delegation Rules` when intake resolves `constraint=nonfiction` + persuasive-argument form), scope boundary, owned references, argument engine workflow, and QA guardrails. `core-editor/SKILL.md` gained an explicit `§ Nonfiction Argument Engine` delegation rule replacing the previous implicit routing through `specialized-audits`.

**Firewall single-sourced.** The canonical Firewall definition (`## The Firewall` + no-content-invention rule text) was extracted from the inline section in `core-editor/SKILL.md` to a new shared `references/firewall.md`. The engine skill and the core-editor pointer both reference this single file. `meta_lint.py` M7 (single-Firewall) enforces that exactly one plugin `.md` file carries the canonical definition — prose mentions and pointers are fine; a second definition is a lint error.

**Five interleaved tables split into dedicated fragments.** Argument-cluster rows extracted from `pass-dependencies.md` §4a, §4b, §4e and from `intake-router-runtime.md §4a` and `run-synthesis.md §Step 8` into four named reference files:

- `argument-audits-routing.md` — §4a Field Recon + Citation Verifier rows + §4b Dialectical Clarity / Consent / Reception rows
- `argument-audits-propagation.md` — §4e argument-cluster signal-propagation rows (Dialectical Clarity, Red Team, Persuasion, Evidence, Adversarial Evidence Review, Field Recon, Citation Verifier) — byte-identical to source; confirmed by `evals/fixtures/argument-carve/4e-before-after.diff`
- `nonfiction-intake-routing.md` — nonfiction triage branch (route conditions, hybrid rule, default-by-form table, post-diagnostic offer)
- `synthesis-argument.md` — Argument-DE parallel decision-layer schema (detection markers, skip contract, override path)

Source files retain `REPLACED-WITH-INCLUDE` pointer comments.

**Behavior-preservation guarantees.** The split is proven behavior-preserving on the mechanical resolver layer by two gates with teeth: `audit-signal-propagation --check-registry` asserts all 45 signal-emitting audits still have §4e propagation rows (it fails if the split fragment is dropped), and the byte-identical §4e extraction is confirmed by `evals/fixtures/argument-carve/4e-before-after.diff`. A supplementary `argument-carve-behavior-preservation` smoke gate (`validate.sh`, wired into `--check-all`) re-runs the mechanical resolvers on a fixed pre-carve fixture and confirms they still classify it as Argument-DE without regressing to error.

### Nonfiction & Argument — First-Class Front Door

Restructured README, plugin description, and browser-facing materials to surface fiction and argument-shaped nonfiction as co-equal pillars.

**README.md (root):** Tagline updated to "a development editor for fiction and argument-shaped nonfiction." The `/start` mermaid promotes nonfiction from a Q3 constraint modifier to a Q1 fork (argument-shaped piece alongside manuscript). "How It Works" adds the argument contract framing (claim / audience / burden / stakes) and the Nonfiction Argument Engine's diagnostic role. "See It in Action" adds a nonfiction samples section (marked-up op-ed + Dialectical Clarity letter, marked available at first release — no sample files exist yet). "Beyond Full Edits" restructured into two co-equal headed blocks: Fiction and Nonfiction & Argument. "Key Terms" expanded with argument terms: argument contract, claim ladder, warrant, burden, Dialectical Clarity, scope drift.

**Plugin description (registry-derived):** Updated tagline across `plugin.json`, `marketplace.json`, and `.claude-plugin/marketplace.json` to lead with "fiction and argument-shaped nonfiction."

**Registry commands:** `/start` writerQuestion updated to "manuscript or argument"; `/audit` writerQuestion surfaces argument-specific audits (dialectical, argument-decision).

**`plugins/apodictic/README.md`:** Tagline, "What It Does," "Intended Audience," and "Components > Workflows" restructured into Fiction and Nonfiction & Argument pillars, with the Nonfiction Argument Engine and its Dialectical Clarity / Red-Team / Persuasion / Evidence companions called out as a top-level workflow group.

**`overview-dashboard.html`:** Header tagline updated. New "Nonfiction Argument Engine" section added as a top-level subsystem (before Specialized Audits) listing the engine, Dialectical Clarity, Red-Team, Persuasion, Evidence, and ArgScope. Argument workflow promoted to first position in Common Workflows.

**`route-explorer.html` + `route-explorer.codex.html`:** Added `argument` as a Q1 artifact option ("An argument-shaped piece — op-ed, brief, testimony, essay") with four goals (diagnose, dialectical, red_team, pre_draft) and corresponding ROUTES entries routing to the Nonfiction Argument Engine, Dialectical Clarity Audit, Argument Red Team, and argument pre-draft pathway.

### Nonfiction Sample — Dialectical Clarity Letter (When Brute Force Fails)

Shipped the first nonfiction "See It in Action" deliverable: a hand-authored Dialectical Clarity letter on the spine argument of Mark A. R. Kleiman's *When Brute Force Fails: How to Have Less Crime and Less Punishment* (Princeton University Press, 2009), retiring the "available at first release" placeholders in the README's nonfiction samples section.

**`sample-dialectical-clarity-letter.html` (root):** A whole-book development edit of the central argument (not a chapter-by-chapter pass), produced by running APODICTIC's Nonfiction Argument Engine / Dialectical Clarity audit. Mirrors the existing fiction letter samples' structure, styling, and Dead Sea Scroll / Scriptorium Noir theme. Opens with a contamination disclosure (WBFF is a known, influential book; the model's knowledge contaminates independent discovery). Hindsight is handled as disclosed-not-scored: the argument is graded on its 2009 evidence, and the later contested HOPE replication record (the ~2016 Demonstration Field Experiment) is not used to grade it but is surfaced as an objection on the model→world bridge, where it confirms an existing structural soft spot rather than creating a new one. Diagnoses the argument with real Dialectical Clarity codes — claim ladder (C0–C3), the derived certainty-over-severity warrant as the headline strength, and four findings clustered on scope propagation (WR3/BP2-adjacent banner-vs-mechanism gap as the highest-leverage note; BP6 small-*n* program evidence; CL4 "cost of crime" definitional slide; BP5-partial comparative ledger). Names the strongest objection by procedure (text-internal scope-conditioning, not the genre-generic "public safety" decoy), credits Chapter 10 as a model of dialectical integrity, and returns a **Structurally Sound** Distinguish verdict (0 Must-Fix / 1 Should-Fix / 3 Could-Fix). Quotation kept within fair use (minimal quotes + loci, no substantial reproduction); the Firewall holds throughout (classes of solution only; the argument is never rewritten and no evidence is supplied).

This is a hand-authored static page like the fiction letter samples — not an `html-export` pipeline output — so no byte-determinism gate applies and it is not regenerated in CI. The contamination disclosure and Firewall are review obligations (Codex + human), not mechanical validators.

**`README.md` (root):** Retired the "(available at first release)" framing on the "See It in Action → Nonfiction & argument samples" section. The Dialectical Clarity letter bullet is now a live link to the published Pages URL (and ordered first, as the shipped deliverable); the Marked-up op-ed bullet remains a non-linked placeholder-stub marked *(forthcoming)* pending a follow-up.

### Pre-Letter Re-Grounding (M2)

Whole-novel editorial letters now **restore the specificity the ledger locked** before they are
written — the context-salience decay that smears "nine belief failures" into "several belief
failures" (`docs/subagent-architecture-design.md:15`) becomes a mechanically checkable fidelity
gate (spec: `docs/synthesis-regrounding.md`, M2; builds on M1's coverage disclosure, which stays
mandatory).

- **New Processing Protocol step 9c — Pre-Letter Re-Grounding** in `run-synthesis.md` (lettered,
  no renumbering; after the step-9b Synthesis Coverage Manifest, before the Step 10 pre-output
  gate and Step 11 letter-writing). Named to avoid collision with the built `run-core.md
  §Pre-Pass Re-Grounding` — a different seam, untouched. The step re-reads the consolidated
  Findings Ledger **verbatim from disk** and re-reads bounded manuscript spans for each
  synthesis-bound finding, then restores exact counts / names / quote anchors into the draft
  claims. **Add-only:** re-grounding may not add a finding (new observations go to §4b without an
  ID), change any severity (Deficit Lock untouched), or soften wording (softness-check still
  applies). It writes a `<!-- regrounding: done -->` marker directly after the coverage marker and
  **updates the M1 manifest** — re-read rows flip to `verbatim` / `in-context` with the
  `regrounded: true` annotation M1 already parse-accepts, so the coverage note improves because
  contact with the text actually happened; it never lets a `degraded` coverage read `ok` (M1's V5
  masking check still fires).

- **Bounded-pull seam (Increment-1 scope-down).** In sequential/hybrid/swarm, the synthesis step
  may request per-finding retrievals (≤ 2 spans × 5k tokens, keyed on `finding_id` +
  `evidence_refs`) serviced by the parent orchestrator (`run-core.md` §Execution Protocol step 10).
  The orchestrator-governed pull *API* is unbuilt (Runner-Governed Execution Increment 4 remains
  future), so this ships **prompt-level** — step-text instructions backstopped by the mechanical
  floors, with a `<!-- deferred: orchestrator-pull-interface (Runner-Governed Execution
  Increment 4) -->` marker recording where a mechanically enforced pull lands if ever.

- **New validator `validate.sh specificity-floor <editorial_letter> <findings_ledger> [--strict]`**
  (`scripts/specificity_floor.py`, mirrored ×2): the **count floor** (a finding whose ledger
  entry locks a count may not deliver a vague quantifier — `VAGUE_QUANTIFIERS`, pinned in one
  module-level constant — with none of that count restored in its letter window; number-words
  normalize to digit strings, case-insensitively, so a ledger "nine" and a letter "9" satisfy
  each other in both directions and a sentence-initial "Nine" satisfies a ledger "nine";
  evidence-locator numbers — "sc. 30-31", plural "scenes 30-31", a spelled-out "Chapter Nine" —
  are stripped so a scene number can't masquerade as a restored count, with a ledger↔window
  count-phrase rescue so a real count heading a count-noun phrase after a locator keyword
  ("…scene 9 belief failures…") is never falsely eaten — the rescue head must be the ledger's
  own count-noun (the ledger side of the match is locator-stripped), so a locator+verb bigram
  ("Chapter 9 opens") never rescues a decayed window even when the chapter number equals the
  locked count; an all-malformed ledger — finding blocks
  present, zero parse — refuses with a named error instead of a vacuous pass) and the **anchor floor** (each delivered Must-Fix window carries an evidence
  reference matching the finding's locked `evidence_refs`, so a restored number rides a
  ledger-matching anchor). Both are blocking; the `<!-- regrounding: done -->` presence check is
  an advisory WARN (`--strict` promotes). Legitimately non-countable findings use an ID-scoped
  `<!-- override: specificity-floor F-… — <rationale> -->` marker (via the shared
  `override_marker` SSoT — code-span-stripped, boundary-matched) + an Appendix B entry. Wired into
  the `run_spot_check` gate and the Step 10 checklist; a canonical re-grounded letter↔ledger pair
  plus hostile arms (decay → count-floor FAIL, anchor-drift → anchor-floor FAIL, missing marker →
  WARN/strict-FAIL) run at `--check-all`.

- **Single ownership of the smuggled-finding direction.** The reverse-direction
  letter-ID-must-exist-in-ledger check is **`finding-trace` E1's** — its sole owner
  (`docs/finding-lifecycle-ids.md`). `specificity-floor` implements no reverse ID check (two
  enforcers with subtly different ID grammars is the drift risk single ownership prevents); the
  step text names `validate.sh finding-trace` as the smuggled-finding gate, and E1's own
  `e1_dangling_ref` self-test pins that shape.

### Non-UTF8 artifacts degrade instead of crashing (repo-wide reader class sweep)

PR #162's build review found `disposition_check.py`'s `_read()` crashed with a raw
UnicodeDecodeError traceback on a non-UTF8 artifact — and the idiom is a class, not an instance.
Swept every OSError-only artifact reader in `scripts/`: the shared `_read()` helper in 25
validators (annotation-manifest through world-bible/viz-manifest, incl. the `Path.read_text`
variant in `schema_coverage.py`), both CLI read sites in `honesty_check.py`,
`structured_findings.validate_file`, two `run_gate.py` sites (`_ledger_finding_ids` and the
disposition-marker sources loop), `lifecycle_node._read_json` (whose
`(OSError, JSONDecodeError)` did NOT cover UnicodeDecodeError — it subclasses ValueError, not
JSONDecodeError), `refutation_check._read_file` (the shared letter/ledger/record CLI reader — the
Codex #164 P2 miss; its `_read_bytes` sibling is binary and cannot decode-fault), and
`disposition_check._read` itself (the module that ORIGINATED the class in PR #162 was left
OSError-only — the earlier note that it was "already guarded on PR #162" was incorrect and is
corrected here), and `specificity_floor._read` (added by PR #163 after this sweep's branch was cut,
so the class sweep couldn't see it; its letter/ledger CLI reader was OSError-only — a non-UTF8
letter/ledger via `validate.sh specificity-floor` raw-tracebacked — and is folded in on the
main-merge here). Each now catches `(OSError, UnicodeDecodeError)`. The advisory readers degrade to
their existing unreadable-artifact path (skip / `None` / `[]` / error-line) instead of a traceback.
**`specificity_floor` is the exception: it is a BLOCKING gate, so it FAILS CLOSED.** Its `_read`
still returns `None` on a read/decode failure, but `main()` no longer collapses that `None` to `""`
— an unreadable letter or ledger now prints a named `Error:` and exits 2 (mirroring
`refutation_check._read_file`'s `(None, msg) -> Error -> exit-2` shape), rather than degrading an
unreadable letter to a vacuous "0 delivered / PASS" and an unreadable ledger to "no findings —
nothing to hold" — either of which silently bypassed the count/anchor floor with a real ledger
(Codex #164 P2, a fail-OPEN on a blocking gate). A legitimately-empty-but-readable artifact still
reads as `""` (not `None`) and runs unchanged. One non-UTF8 self-test case added per touched
validator, plus — for specificity_floor — fail-CLOSED pins on both the letter-read and ledger-read
failure paths and a readable-empty-stays-green regression pin. Already safe and untouched: the
previously guarded readers (`annotation_export`, `editor_scaffolding`, `reanchor`,
`regression_diff`), the `errors="replace"` family
(`config_checks`, `timeline_checks`, `letter_checks`, `meta_lint`, `argument_groundtruth`), the
`except (OSError, ValueError)` sites in `run_gate.py` (ValueError covers UnicodeDecodeError), and
the repo-internal fail-loud readers (`run_gate._load_manifest`, `apodictic_artifacts` schema
loads, `sync_setec`), which never see user-supplied artifact paths.

### Workflows — One-Click Round-Trip Resume at `/start`

The built round-trip revision loop (reanchor → emit → crossref) is now **surfaced**, not just
reachable: at the bound-project `revising` **and** `diagnosed` nodes, `/start` checks round-trip
eligibility (a prior run folder holding a `*_Annotation_Manifest_*.md` + `python3` — a file glob,
no new command, no new `next_action`) and, when eligible, offers **"Returning with a revised
draft?"** alongside the existing dispatch. On accept it sequences the existing gated surfaces —
reset check, snapshot, `reanchor` classify, `emit -o <new_run_folder>` (exit (a): carry-only),
optional targeted re-diagnosis, `regression-diff` + `crossref` — and closes the round with a new
step 4: a per-finding **disposition table** the operator confirms row by row (the model proposes;
the operator disposes). The record (`[Project]_Roundtrip_Disposition_[runlabel].md`, marker-based)
carries a **hard-sequenced** confirmation token written only after every row is confirmed, and
resolved markers are written for `confirm-resolved` rows only.

New `roundtrip-disposition` validator (`reanchor.py disposition`, joined into `--self-test-all` /
`--check-all` with a canonical fixture pair + hostile arms): **RT1** recompute alignment (row
classes and the derived `compares:` header must equal a live reanchor/crossref recompute — no
stale or fabricated evidence), **RT2** confirmation record present (no decided row without the
token; the validator proves the record, never the human — that layer is the new **rev-a4**
attested item on the `revision_round` gate), **RT3** confirmed-writes-only (a resolved marker
without a confirmed disposition — the vanished-anchor auto-close — is an ERROR), **RT4**
partition coverage (every finding id in the recomputed RA3 partition must have a disposition
row, missing ids named — a partial record never reads round-close clean; WARN, ERROR
`--strict`), **W1**
unadjudicated/staged (advisory; ERROR `--strict`). Existing gates (RA1–RA3, R1, W1–W3, X1,
rev-a1–a3) and both lifecycle writers are unchanged — the disposition record is a confirmation
precondition upstream, never a third writer. Closes ROADMAP "Toward truly great" #2's last mile.

### Synthesis Coverage Disclosure (M1)

Whole-novel editorial letters now disclose what the synthesis step could actually see when it
wrote the letter — the silent degrade (chapters and pass artifacts outside active context at
letter time) becomes a mechanical, author-visible record (spec: `docs/synthesis-regrounding.md`;
M2, pre-letter re-grounding, ships separately).

- **Artifact-read manifest** `[Project]_Synthesis_Read_Manifest_[runlabel].md`, written **before**
  the letter exists — by the parent orchestrator at synthesis dispatch (sequential/hybrid/swarm,
  provenance `dispatch-derived`) or by the agent immediately before letter-writing (single-agent,
  provenance `declared`, labeled in pinned language). Closed row grammar
  (`| kind | id | status | annotations |`; `verbatim | summary | absent`,
  `in-context | outside-active-context`; the `regrounded: true` annotation is encoded now and
  reserved for M2). The denominator is enumerated **from disk** (run-folder globs + preflight
  section boundaries), never from the letter's prose — new Processing Protocol step 9b in
  `run-synthesis.md` + the dispatch-side write in `run-core.md` §Execution Protocol step 10.
- **Coverage note in the letter:** a required `### Synthesis Coverage` subsection of Appendix C
  (no 15th top-level section; `synthesis-sections` untouched), a
  `<!-- coverage: ok|degraded -->` machine marker on the first non-blank line after the title
  block, and a pinned degrade sentence in the reader-facing summary section when degraded (The
  Short Version — or the Editor Brief that replaces it in editor-scaffolding letters, which swap
  that section out). "Degraded" is recomputed from the
  manifest per an exhaustive D1-D4 truth table, relative to the mode's own baseline — normal
  multi-agent outline-mediated coverage is *not* degraded.
- **Additive sidecar object** `synthesis_coverage` in `Diagnostic_State.meta.json`
  (`complexity_signals` additive pattern — property + `$comment` in
  `apodictic.diagnostic-state.v1`, template field, `output-structure.md` docs; no new schema
  file, no version bump).
- **New validator `validate.sh synthesis-coverage <run_folder> [--strict]`**
  (`scripts/synthesis_coverage.py`, mirrored ×2): V1 presence, V2 disk↔manifest row bijection
  (the manifest can neither shrink nor pad the denominator), V3 note/sidecar/marker as exact
  projections of the manifest, V4 provenance/mode agreement (`declared` in a multi-agent run
  fails — the cheap lie is blocked), V5 degrade recompute (masking fails louder than degrading).
  No override markers — disclosure is not overridable. Wired into the `run_spot_check` gate;
  canonical green + degraded-and-disclosed fixtures plus hostile arms run at `--check-all`.
  Launch posture (operator call folded 2026-07-01): the V2/V3/V4 fiction-checks are blocking day
  one; V1/V5 — and so the overall gate — are advisory-first for one release (WARN at exit 0,
  `--strict` promotes), flipping to blocking once real runs confirm the degrade thresholds don't
  over-fire.

### Manuscript visualizations — character co-presence network (chart 5)

Built Viz Chart 5, the character co-presence network: nodes are characters, an edge means they share a scene, and chord thickness is the count of shared scenes. It is the firewall-safe, producer-gated chart — co-presence is a *fact* (two characters both on-page in a scene), so the chart renders structure and invents no relationship.

**New producer schema `apodictic.scene_roster.v1`** — one block per manuscript: `rosters: [{scene_id, characters: [{name, anchor}]}]` plus an inline `character_aliases` table (surface-form → canonical-name). Each roster character carries a **required, non-empty `anchor`** (a Timeline-relative line-range or short on-page quote). The Timeline carries POV only, not a full cast roster, so this dedicated roster pass is what makes the per-scene cast machine-readable — without mutating the Timeline columns (charts 1–3 are untouched).

**Present-vs-mentioned rule (the firewall crux).** A character is *present* in a scene iff they take on-page action, speak, or are a POV/thought subject within the scene's line-range; a character named only in another's speech, in summary, or by reference is *mentioned* → no roster entry, no edge. The reading is **producer/author-enforced** (a validator cannot read prose) and made auditable by the required `anchor` — the Continuity Bible C2 author-enforced precedent. The gate enforces anchor-non-empty + provenance closure, not the semantic reading.

**`manuscript-viz` gate X2** byte-checks the manifest's `co_presence[]` against the producer: every `scene_id` matches a roster entry and resolves to a Timeline row; every `co_presence` name is in that scene's (canonical) roster names; the scene's Timeline POV character is present in its roster (cross-check); and every producer anchor is non-empty. X8 flips for `co_presence` (a present array is now legitimate iff it byte-checks against `scene_roster.v1`); it still fails for the producer-less `scene_functions`/`reveal_points`.

**Deterministic render** — a circular node layout with chords for shared scenes; chord thickness comes from a hardcoded weight band (never read from the manifest). Edges and weights are computed mechanically from the rosters (an edge iff two characters co-occur in ≥1 scene; weight = the count). A solo character renders as an isolated node, never dropped. Single-file inline SVG, no network.

**Worked fixture** `example-scene-roster.md` (paired to `example-timeline.md`): Mara + Adrian share two scenes (one edge, weight 2); Eleanor is mentioned-not-present (no node, no edge); Jon is a solo isolated node; and the "Mara Voss" surface form collapses to "Mara" via the alias table. The `_coverage.json` binding row (`manuscript-viz`, `closed_keys:true`) is added and exercised by `--check-all`.

## v2.6.2 - 2026-06-26

### Validators — override-marker hardening

Closed the code-span-decoy override bypass fleet-wide. Eighteen validators
(`content-advisory`, `persona-divergence`, `intake-interview`, `author-fingerprint`,
`world-bible`, `continuity-bible`, `legal-risk`, `scene-ethics`, `retcon-plan`,
`state-card-diff`, `annotation-manifest`, `crosslink`, `argument-spine`,
`reader-instrument`, `promise-contract`, `regression-diff`, `style-explanation`,
`honesty-check`) carried their own `re.compile(r"<!--\s*override: …")` — seventeen
of them matching on **raw text**, so an override marker quoted inside a ``` fence or
an inline `code span` (a documentation example) was honored as a live directive.
They now route through the shared `override_marker` SSoT: new `override_targets`
(id- / pair- / presence-scoped) and `override_payloads` (free-text) helpers strip
code spans first and boundary-match the slug, so one module owns both stripping and
marker-matching. The meta-linter gains two gates so the class cannot re-enter: **M5**
now flags the compiled / inline override-marker regex form (not just the bare
substring), and **M6** flags a local code-span / fence stripper (delegate to
`override_marker.strip_code_spans`). The shared helpers match `override:` case-
sensitively (the old per-validator regexes were `re.IGNORECASE`); every shipped and
documented marker is lowercase, so this is a deliberate, inert tightening in the
fail-closed direction — an off-spec mixed-case marker no longer silences a finding.

## v2.6.1 - 2026-06-23

### Audit Inventory — Content Advisory + Reader-Persona Simulation now registered

Two specialized audits that shipped in v2.6.0 — **Content Advisory** (`content-advisory`, a sensitivity-surface audit sibling to Reception Risk) and **Reader-Persona Simulation** (`persona-divergence`, a Pass-1 reader-dynamics overlay) — were never carded in the user-facing audit surfaces, so they were absent from the downstream Gemini website (generated from `release-registry.json`). Both are now registered across every audit-inventory surface: `release-registry.json` (two new **Craft** items; `availableAudits` 35 → 37, `specializedAudits` 32 → 34), the canonical `audit-routing-table.md` signal-emitting-audits inventory, `AUDIT_SELECTION_MATRIX.md`, and `overview-dashboard.html` (inventory-synced markers re-synced to `audits=45`). The inventory-parity gate (`scripts/check-inventory-parity.mjs`) now **also guards `release-registry.json`**: every shipped reference under `specialized-audits/references/` must be carded in the registry's `categories[].items[].files` or explicitly listed in a new `NOT_CARDED` allowlist — so a future specialized audit can no longer ship uncarded the way these two did. A hermetic `--self-test` case proves the new check is non-vacuous.

## v2.6.0 - 2026-06-23

### Annotated-Manuscript Deliverable — letter ↔ margin cross-links (Increment 3)

Navigation between the editorial letter and the marked-up copy is now **bidirectional**. The margin→letter direction already existed (every comment ends "(See letter §F-…)"); this adds **letter→margin**. A `crosslink` render treats the letter as a "second snapshot" and injects a CriticMarkup back-link span — `{>>→ marked-up copy: <id> @ <kind>:<value><<}` — immediately after each letter `<!-- finding: F-… -->` marker whose finding has a manifest annotation, copying the anchor **verbatim from the gated manifest**. The same reverse transform (delete every `{>> … <<}` span) proves the letter is untouched, behind the **same two-sided sigil precondition** (the letter, being authored prose, must not already contain a CriticMarkup sigil — without this the transform would silently delete an author's own span). A new `crosslink` validator gates bidirectional integrity: **X1** the margin comment carries the forward link, **X2** each back-link's anchor equals the manifest's (no drift), **X3** no dangling either way (no phantom back-link; no missing reverse link), **X4** no letter mutation; **W1** annotated-but-uncited is advisory. Firewall-clean: the back-links carry only finding IDs + anchor tokens drawn verbatim from the manifest, never authored prose. Validators 42 → 43. Consumer-only — the shipped synthesis does not yet emit letter markers matching the annotation manifest, so the feature is inert on the real corpus until that producer lands; the canonical `--check-all` fixture's worked letter + crosslinked letter are hand-constructed.

### Annotated-Manuscript export — DOCX with anchored comments → Google Docs (Increment 4)

The marked-up manuscript can now be exported as a **`.docx` that imports into Google Docs with each finding as a native anchored comment** — the professional editorial deliverable (Word/Google-Docs comments are the industry standard), and the DOCX target in one. `annotation_export.py docx <run_folder>` projects the gated manifest + snapshot into a `.docx` (Office Open XML — a ZIP of XML parts, **stdlib-only**: `zipfile` + hand-written XML, no `python-docx`): the manuscript text fills `word/document.xml` as one `<w:p>` per snapshot line, each finding's anchored span is wrapped `<w:commentRangeStart/End w:id="N"/>` + `<w:commentReference w:id="N"/>`, and `word/comments.xml` carries the **verbatim** comment — so Word and Google Docs render an anchored comment on the exact span. **Firewall-clean by construction:** a pure projection — the document text is the verbatim snapshot (XML-escaped via the same exact `&`/`<`/`>` 3-entity pair as the HTML path, runs split only at comment boundaries), comments are verbatim, and the model assembles fixed OOXML boilerplate (7 parts incl. minimal `styles.xml`/`settings.xml` to avoid Word's repair-prompt) around copied bytes. The ZIP is **byte-deterministic** (`ZIP_STORED`; explicit `ZipInfo` per part with pinned `date_time`/`create_system=3`/`external_attr`; fixed order; seekable buffer; a `w:date` derived from the **run date** (the manifest `runlabel` at noon UTC — deterministic, not wall-clock, and no prior-day rollback in western timezones)) so a committed `.docx` fixture is byte-stable across machines. The new `docx-export` validator gates the on-disk artifact: **D1** artifact integrity (the `.docx` equals a fresh deterministic build byte-for-byte — the authoritative lock for a binary, the HTML-H1 discipline), **D2** text round-trip (the `document.xml` `<w:t>` text, exact-unescaped, one `<w:p>`/line + one trailing newline, reproduces the snapshot — the comment markup carries no body text), **D3** comment resolution + fidelity (the `commentRangeStart`/`End`/`Reference` ids ↔ `comments.xml` ids form a bijection equal to the manifest finding set, and each comment is verbatim, keyed via the deterministic `sorted(finding_id)→N` map). Ships with the canonical `example-annotated-manuscript/docx/` fixture wired into `--check-all` (byte-identical to a fresh export) and `*.docx binary` in `.gitattributes`. Validators 47 → 48. One-time maintainer acceptance: open the fixture in Word (no repair prompt) and import into Google Docs (comments land anchored) — OOXML on-paper validity doesn't guarantee either. PDF remains on the horizon; the manifest stays the one canonical artifact, every format (CriticMarkup, Obsidian, HTML, DOCX/GDocs) a projection.

### Annotated-Manuscript export — self-contained read-only HTML (Increment 3)

The marked-up manuscript can now be exported as a **self-contained `.html` openable in any browser** — no Obsidian, no plugin, no Markdown tool. `annotation_export.py html <run_folder>` projects the gated manifest + snapshot into one HTML file: the manuscript in a faithful `<pre class="manuscript">` (CSS `white-space: pre-wrap` + a serif face reads as prose while preserving the snapshot's exact bytes), with a footnote-style `<sup id="ref-F-…"><a href="#fn-F-…">[F-…]</a></sup>` marker at each anchor, and a `<section class="findings">` listing each finding (`<li id="fn-F-…">{verbatim comment} <a href="#ref-F-…">↩</a></li>`) — so the browser gives native bidirectional anchor navigation, with embedded CSS and zero network refs. **Firewall-clean by construction:** a pure projection — the snapshot is HTML-escaped (`&`→`&amp;` first, then `<`/`>`), footnote markers are spliced **between escaped prose segments** at raw-snapshot offsets (escaping never touches a marker, so offsets never drift), and the new `html-export` validator gates it by identity: **H1** round-trip (delete the manifest-keyed `<sup id="ref-…">` markers + the **exact 3-entity inverse** unescape — not a general decoder — reproduces the snapshot byte-for-byte), **H2** anchor resolution (`<sup>`↔`<li>` bijection equal to the manifest finding-id set, catching an un-manifested marker/finding), **H3** comment fidelity (each `<li>` equals the HTML-escaped verbatim comment + the exact back-ref). The validator reads and gates the **on-disk** `html/` artifact. A `<pre>`-faithful view (not reflowed `<p>`/`<h>`, which would defeat the byte-exact round-trip) keeps the firewall proof exact; reflowed-prose HTML is a future increment. Ships with the canonical `example-annotated-manuscript/html/` fixture wired into `--check-all` (byte-identical to a fresh export) and a **hostile self-test** (HTML metachars upstream of an anchor + literal `&`/`<` in a comment) that the metachar-free canonical fixture can't exercise. Validators 46 → 47. Google Docs is the next render target (DOCX/PDF on the horizon); the manifest stays the one canonical artifact, every format a projection.

### Annotated-Manuscript Obsidian export — bidirectional letter cross-links (Increment 2)

The native-Obsidian export is now **clickable both ways**, with no plugin. Building on Increment 1's footnoted copy, `annotation_export.py` now also projects the **Obsidian letter** and wires the navigation: (a) each copy footnote definition gains a forward `[[<letter>#^<finding-id>|→ letter]]` wikilink (web-verified that wikilinks render clickable inside footnote *definitions* — the key contrast with CriticMarkup); (b) the Obsidian letter appends an Obsidian `^<finding-id>` block id to each finding's line so those forward links resolve; (c) the gated crosslinked letter's CriticMarkup back-link spans convert in place to reverse `[[<copy>#<heading>]]` wikilinks, using the **resolved snapshot heading text** (`Chapter 9`) — never the manifest's normalized `Ch 9` token — with a file-level `[[<copy>]]` link for line-range/quote/document anchors that have no addressable heading (W1). Heading-level reverse-nav is reliable because Obsidian's heading-anchor slug **strips** the footnote ref Increment 1 appended to the heading line (`# Chapter 9[^F-RR-01]` → resolves as `Chapter 9`, web-verified). **Firewall-preserved:** still a pure projection — the comment is carried verbatim (O3 now checks comment + the *exact* forward wikilink, no authored-text gap), and the letter's editorial prose is untouched: **O5** proves stripping the Obsidian letter's additions (wikilinks + block ids) reproduces the same bytes as stripping the crosslinked letter's CriticMarkup spans (the X4 analog, two-sided precondition). **O4** gates link resolution (every forward link → a real letter block id; every reverse link → a real copy heading, footnote refs stripped) — so a manifest-token-vs-heading-text mismatch fails at build. Extends `obsidian-export` (no new validator — still 46); the validator reads and gates the **on-disk** copy *and* letter. The canonical `obsidian/` fixtures (copy + new letter) are wired into `--check-all` (both byte-identical to a fresh export). Scope stays Obsidian-only; read-only HTML → Google Docs are the next render targets, DOCX/PDF on the horizon. The manifest remains the one canonical artifact; every format (CriticMarkup, Obsidian, future HTML/GDocs/DOCX/PDF) is a projection.

### Annotated-Manuscript Export — Obsidian native footnotes (no plugin)

The marked-up manuscript can now be opened in **vanilla Obsidian, no plugin**, with every finding as a clickable footnote. The new `annotation_export.py` projects the gated annotation manifest + snapshot into Obsidian-native Markdown: each finding becomes a footnote reference `[^<finding_id>]` at its anchor locus (quote → after the sentence; chapter/section → on the heading line; line-range → end of line; document → file-level), and its definition carries the **verbatim** manifest comment (which already includes the `(See letter §id.)` pointer). Obsidian renders footnotes natively — clickable superscript, hover preview, the core Footnotes View pane — whereas CriticMarkup `{>> <<}` shows as literal brace clutter without a community plugin; *that* (not anchor links, which are native) was the real obstacle. **Firewall-clean by construction:** a pure projection of the gated manifest — the reverse transform (strip the manifest-keyed `[^id]` refs + the trailing `[^id]:` definition block) reproduces the snapshot byte-for-byte (the A2 discipline, two-sided and manifest-keyed), and the comment is relocated verbatim, never re-authored. The new `obsidian-export` validator gates it: **O1** round-trip to source (with a two-sided `[^` precondition mirroring `render`/A2), **O2** footnote resolution (ref↔definition bijection equal to the manifest finding_id set — the A4 forward+inverse multiset on footnotes, catching an un-manifested/authored footnote), **O3** comment fidelity (each definition equals its manifest comment byte-for-byte). Ships with the canonical `example-annotated-manuscript/obsidian/` fixture wired into `--check-all` (generate on a temp copy, gate, and assert byte-identical to the committed fixture — the producer-chain discipline). Validators 45 → 46. Scope: the annotated **copy** (Obsidian Increment 1); the Obsidian **letter** cross-links (block ids + back-link wikilinks using the resolved heading text) are Export Increment 2. The canonical render stays CriticMarkup — not the publishing-industry standard (Word Track Changes is), but the plain-text base whose no-mutation proof is cheap and which bridges to Word/Google-Docs comment mode via the Commentator plugin; Obsidian/HTML/GDocs/DOCX/PDF are all sibling projections of the one gated manifest.

### Annotated-Manuscript Producer — `evidence_quote` Pass-5 pilot (Increment 2)

The character-precise `quote` rung is now **live for Pass 5 (Character Audit)** findings. Deliverable Increment 2 had shipped the *consumer* (the quote-locator + the **A6** quote-integrity gate) but nothing populated `evidence_quote`; this increment makes Pass 5 attach it. When a Pass-5 finding is about a specific line (a flat-affect beat, a puppet-moment decision, a voice-drift sentence) the pass copies that line **verbatim** into the finding's `evidence_quote`, and the marked-up copy anchors the margin note at that exact sentence instead of the chapter. The discipline is written once in `findings-ledger-format.md` §"When to populate `evidence_quote`" (sentence-precision criterion; the copy-never-author firewall; location is by the quote's own bytes, not `evidence_refs`; single line only) and pointed to from the Pass-5 spec. **Firewall-clean by construction:** the build-time locator emits a quote anchor only when the span occurs in the snapshot verbatim and exactly once, so a non-verbatim, non-unique, multi-line, or fabricated quote simply degrades to the chapter/line rung and never reaches the margin; A6 is the validate-time backstop that rejects any forged quote anchor — a pass physically cannot smuggle authored prose. Demand-gated and per-pass: Pass 5 is the only adopter in this increment (Pass 8 reveal lines, the AI-prose flags, and citation-bearing nonfiction findings are deliberately deferred). Prose-only — no schema change (`evidence_quote` was already an optional `apodictic.finding.v1` field), no new validator (count stays 43); the canonical `--check-all` fixture already proves the consumer end-to-end (F-QT-01 lights the rung; F-QAMB-01 degrades).

### Annotated-Manuscript Deliverable — wired into the run flow (the producer, Increment 1)

A real Core/Full DE run now **produces** the marked-up manuscript + crosslinked letter, not just the validators on a hand-built fixture. At **intake** the manuscript is persisted as a frozen, LF-normalized snapshot — the deliverable's immutable left-hand side — for core-de / full-de runs (skipped for partial / fragment; an aborted run just leaves a benign provenance copy). At **run-end**, whenever the run wrote a full editorial letter (a `*_Core_DE_Synthesis_*` / `*_Full_DE_Synthesis_*` exists — a detectable artifact, not an abstract "workflow"; `/ready` writes one so it offers, partial / fragment / triage / audit do not), the orchestrator **offers** the deliverable and **asks the author** (a marked-up copy isn't always wanted). On *yes* it runs build → A1–A6 → render → X1–X4 **staged in a temp copy**, moving only gate-verified artifacts into the run folder — so the run folder is never left holding an unverified copy (verified-or-absent), the same temp-stage discipline the CI gate uses. The letter's finding-marker form is **pinned** to the canonical `<!-- finding: F-… -->` (a subset of what the honesty gates already accept, so nothing there changes) so the crosslink back-links resolve; the Severity-Calibration appendix keeps its distinct `apodictic:severity_calibration` form to avoid a second back-link. An existing un-annotated run folder is re-annotated through `/start`'s `diagnosed`-node dispatch — conditioned on a no-annotated-copy glob, **not** a new `next_action` value — with **no new command** (so no registration burden). A new `--check-all` chain gate runs build→gate→render→gate on a temp copy of the canonical inputs and asserts the fresh build is **byte-identical** to the committed fixture (the fixtures are provably "what a fresh build emits"). No new validator; the count stays 43. Render-only, model-never-authors — every margin note remains a verbatim projection of a finding the passes already produced.

### Annotated-Manuscript Deliverable — character-precise anchoring (Increment 2)

Margin comments can now anchor to the **exact sentence**, not just the chapter or scene. A finding carrying an optional verbatim `evidence_quote` (a manuscript substring) is matched against the snapshot; when it occurs verbatim and **exactly once** it anchors to that character span — a new `quote` rung, finest in the ladder — otherwise it degrades to the line/chapter ladder, never fabricating precision. The new **A6** gate proves every quote anchor is a verbatim, unique manuscript span that the recorded offsets pin and that matches the finding's `evidence_quote`, closing the one new failure mode (a fabricated or mis-placed quote) the existing gates do not cover; the rendered margin is still only the comment (A5), so the firewall reduces to provenance-by-identity. The renderer is generalized to a unified character-offset splice (descending-offset insertion, **byte-identical to Increment 1** for line/chapter anchors, so A2 still holds). `evidence_quote` is an optional `apodictic.finding.v1` field — Increment-1 findings are unaffected, and no shipped pass emits it yet (the consumer + A6 ship now; populating it upstream is deferred). Single-line quotes only.

### Annotated-Manuscript Round-Trip Re-Anchoring — `reanchor`

The marked-up copy is now **revision-aware**: when the writer revises, `reanchor` (`scripts/reanchor.py`; `validate.sh reanchor <prior_run_folder> <new_snapshot>`) carries draft N's margin annotations onto draft N+1 by re-resolving each anchor against the new snapshot, and classifies what happened — **held** (same locus), **moved** (a quote whose verbatim+unique text is now at a new offset), **vanished** (anchored prose gone — a candidate the finding was addressed), **ambiguous** (the span now occurs more than once — re-anchor refused), or **not-re-anchorable** (a bare `line-range` carries no text to search). This is the **anchor/text-level** complement to `regression-diff`'s finding-level cross-round diff: a vanished anchor is hard evidence a finding was addressed; a quote that persists verbatim is hard evidence it wasn't. **Firewall-clean by construction:** re-anchoring is pure text search over the new snapshot — a re-anchored quote's offset is **recomputed** against N+1 by the same A6 identity that built it (verbatim + exactly once, else it degrades; the offset is never carried forward), and the margin comment is **carried over byte-identical** (RA2), never re-authored. The re-anchored manifest (held/moved only, bound to N+1) is gated by the existing A-machinery: a new `ledger_optional` mode on `annotation_manifest.check` runs **A1 + A2 + A3 + A4-multiset + A6** against N+1 without requiring a re-diagnosed Findings Ledger (its A4/A5 ledger arms are legitimately absent — vanished Must-Fixes go to the re-anchoring report, and RA3 partition-completeness guarantees none is silently lost). The `reanchor` validator raises **RA1** re-anchor integrity, **RA2** comment fidelity, **RA3** partition completeness (hard errors — the mechanical contract) and **W1** candidate-resolved / **W2** re-anchor refused (advisory, ERROR under `--strict` — the `regression-diff` posture). It prints to stdout (the diff-validator precedent); a human-readable re-anchoring report is orchestrator-written. Ships with a revised-draft fixture (`example-reanchor-revised.md`) wired into `--check-all` that exercises all five classes against the canonical manifest. Validators 44 → 45. This completes the deliverable's revision-awareness, building on draft-over-draft regression.

### Annotated-Manuscript Deliverable (Increment 1)

The editorial letter's findings, now anchored in the margin of the manuscript itself — the third leg of the standard developmental-edit deliverable set (letter + book map + marked-up copy), and the one the framework did not previously produce. A new `annotated-manuscript` validator + `apodictic.annotation.v1` manifest schema + CriticMarkup renderer (`scripts/annotation_manifest.py`, with `build` / `render` / validate modes) produce a **comments-only** marked-up copy over an immutable, LF-normalized manuscript snapshot: each margin note is a *verbatim projection* of an `apodictic.finding.v1` field set, anchored by a four-rung ladder (line-range / section / chapter / document) that never fabricates precision. The no-mutation guarantee is mechanical — deleting every `{>> … <<}` span reproduces the snapshot byte-for-byte — and every body Must-Fix must reach the copy as a rendered span (A4). Firewall-bound: comments only, never tracked changes or suggested prose. Chapter-reference normalization is now shared (`apodictic_artifacts.chapter_token`) so the annotation and visualization surfaces bin chapters identically. Self-testable validators 41 → 42; `--check-all` gates a canonical snapshot + manifest + annotated-copy fixture. Promoted from Horizon Capacities Tier 1 and shipped the same day. See `docs/annotated-manuscript.md`.

### Nonfiction Pre-Draft

Added the **genre layer** (Increment 5) to the Nonfiction Pre-Draft Pathway — a pre-draft scaffold that holds a genre to its genre-required argument structure. A new single-sourced `apodictic.genre_profile.v1` schema names the genre (grant-proposal / academic-article / pitch-deck), the genre-required section roles it must seed, and the evaluator it is written for. The existing `argument-spine` validator gains **B1–B4 + W4** (B1 invalid genre profile, B2 a declared section unseeded — the signature, B3 genre/form mismatch with normalized comparison, B4 duplicate profile, W4 thin canonical skeleton, overridable via `argument-spine-genre`) over the new block — **no new validator; the validator count is unchanged** (the genre layer rides `argument-spine`, like Increments 1–3). B2 matches the declared heading against a markdown heading's *full* text (modulo a trailing colon / whitespace), so a declared section is not seeded by an unrelated heading that merely contains its text as a substring. Three canonical worked examples (grant / academic / pitch) are gated by `validate.sh --check-all` under `--strict`. Dialectical Clarity's *Genre & Audience Calibration* gains a Pitch Deck entry and a Reviewer-Anticipation Lens (panel / peer / investor), and the form enum gains "pitch deck". The Firewall holds: the engine validates the writer's declared structure and surfaces which genre-required section is missing or unseeded; it authors no aims, contribution claim, objection text, or traction numbers, and the pitch-deck entry coaches no design or fundraising tactics.

### Workflows — Cross-Manuscript Author Voice/Craft Fingerprint (the writer's signature over a career)

A persistent profile that accumulates across the works an author collects under one **author-root** and surfaces movement — drift, range/growth, unconscious self-imitation, signature tics. APODICTIC measures voice *within* a manuscript (Pass 11; the AI-prose personal-baseline z-scores) but had no memory *across* works; this is that memory. It does **no new stylometry** — each `apodictic.voice_fingerprint.v1` block **consumes** the single-voice AI-prose machinery (SETEC `voice_profile`/`voice_distance` + the personal-baseline z-scores via `centroid_ref`) and the module adds only the persistence-and-longitudinal-diagnosis layer. Persistence follows the `Series_State.md` convention exactly: the `Author_Voice_Profile.md` lives at an **operator-designated author-root** (no cross-project or machine-global state, no auto-discovery — "across works the author collects into one author-root," not "automatically across all your books"). It is **descriptive** (observations, not verdicts — "intended departure, or drift?", never "fix your voice"), carries no Must/Should/Could severity (a fingerprint is not a defect), and is **local-only** (no external call, never transmitted). The new `author-fingerprint` validator (`scripts/author_fingerprint.py`) enforces **F1** schema (incl. a non-empty, scalar-valued `metrics` — the `retcon_plan.scores` nested-object precedent), **F2** provenance (each fingerprint cites a `source` + `centroid_ref` naming a consumed audit output — presence-checked, since the external value can't be re-resolved), **F3** same-register comparison (a drift/range claim referencing ≥2 fingerprints must share a `register` — the AI-prose domain-shift guard), plus advisory **F4** descriptive-not-prescriptive (no editorial severity token, no "fix/vary your voice" directive; ERROR under `--strict`; per-id override `fingerprint-frame`), **W1** insufficient data (no register has ≥2 fingerprints → seed-only), and **W2** local-only hygiene (a missing `local-only` marker or an external URL — **advisory WARN only, never gate-blocking**: a marker scan can't prove a runtime call, so the binding guarantee stays the module's no-external-call rule). The POV Voice Profile (which fits per-POV-*character* and refuses single-POV work) is **not** the author centroid source — the single-voice fit is; POV is kept only for the optional protagonist-collapse sub-diagnostic. Ships the canonical `example-author-voice-profile.md` (two `literary-fiction` fingerprints, one within and one just outside the same-register band, with a same-register drift observation) wired into `--check-all` under `--strict`. Self-testable validators **51 → 52**. Spec: [`docs/author-voice-fingerprint.md`](../../../../docs/author-voice-fingerprint.md).

### Tooling / DX — Codex README brought into the registry-generated path

`README.codex.md`'s capability counts were the one inventory surface still hand-maintained: `release-generate.mjs` regenerated the **Claude** `README.md` count lines from `release-registry.json`, but the Codex README sat outside that path and had drifted to **34 available audits (16 craft)** while the registry, plugin description, and Claude README all read **35 / 17 craft** (`bump-version.sh` only ever updated its version callout). `release-generate.mjs` now also generates + `--check`-gates the three `README.codex.md` count lines — the Specialized-Audits line, the "list all N available audits" line, and the Framework-Version capabilities sentence — reusing the existing Claude-README builders, with a Codex-specific capabilities builder that regenerates only the `Capabilities: … pipeline.` span and leaves the `bump-version.sh`-owned "Current Codex manifest version is \`X\`." callout untouched (new `paths.pluginReadmeCodex`). This corrects the stale 34/16 counts to 35/17 and folds the Codex README into the CI drift gate (`release-generate.mjs --check`), closing the drift class rather than hand-patching one number. Resolves the capability-inventory finding from the 2026-06-19 capability audit.

### Workflows — Content-Advisory / Sensitivity-Surface Derivation (what's depicted, where, how intensely)

A new specialized-audit deliverable that derives a reader/marketing-facing **content advisory** — a map of where the manuscript depicts intense material (violence, sexual content, self-harm, abuse, …), at what intensity, on- or off-page — for front-matter notes, retailer content-warning metadata, sensitivity-reader handoff, or the author's own awareness. APODICTIC's existing audits *assess* such content for craft and harm risk; none derived the descriptive, reader-facing artifact. This does: pure extraction over depicted content, anchored to loci, as `apodictic.content_note.v1` blocks (`category` ∈ a closed nine-value taxonomy; `intensity` low/medium/high; `depiction` on-page/off-page/referenced; `loci` ≥1). It is **opt-in by design** — generated only under a `<!-- content-advisory: opted-in -->` marker (content warnings are contested; an unbidden one imposes a stance) — and **descriptive, never evaluative**: a note records *that* content is depicted and how, never that it is "gratuitous" and never that it should be cut. A content note is **not a defect** — it carries no Must/Should/Could severity; its intensity scale is orthogonal to the editorial scale, the Legal Risk Register precedent. The new `content-advisory` validator (`scripts/content_advisory.py`) enforces **A1** schema (incl. the `other`→non-empty-`label` conditional the subset engine can't express, and non-empty loci elements), **A2** locus presence/shape (the continuity-bible C2 shape), **A3** no editorial-severity leak (no Must/Should/Could token in the prose or a label, and no `apodictic:finding` block in the advisory — the orthogonal-severity firewall), plus advisory **W1** prescriptive drift (a "should cut/soften/tone-down …" **construction** — a modal/recommend verb governing a revision action, deliberately *not* bare descriptive adjectives like "excessive blood loss"; ERROR under `--strict`; per-id override `advisory-eval`) and **W2** opt-in marker. If no advisory artifact is resolved it no-ops (exit 2), like legal-risk. The Increment-1 consume-don't-duplicate against Reception Risk / Consent / Erotic is **prose-citation only** (those audits emit no addressable per-instance IDs — the structured coverage diff is deferred until they do). Module homed in **specialized-audits** (alongside Reception Risk); the canonical `example-content-advisory.md` (an opt-in advisory with four notes across categories) lives in core-editor/references and is wired into `--check-all` under `--strict`. Self-testable validators **52 → 53**. Spec: [`docs/content-advisory.md`](../../../../docs/content-advisory.md).

### Workflows — Auto-Derived Continuity Bible (the narrative half of a style sheet)

A new core-editor deliverable that consolidates the canonical facts a manuscript has committed to — the narrative side of the editorial **style sheet** a human developmental editor returns. APODICTIC already scatters continuity across the Timeline, the SFF Rule Ledger, and the Pass-5 portraits; the Bible gathers the *narrative* half into one locus-anchored reference (Cast, Places, Objects, World Rules, Chronology) and, as a side effect, a **Contradiction Ledger** of the places the text commits to two facts at once. Each fact is a first-class `apodictic.canon_fact.v1` block (`category` ∈ person/place/object/world-rule/chronology; `value` always a quoted string so numerics type-check; `loci` ≥1; `consolidates` pointing at a Timeline scene id when the fact is consumed rather than newly extracted). It is firewall-bound: it records **stated facts only** (never inferring an unstated one, never filling a gap), and **surfaces contradictions, never resolves them** — both conflicting values are catalogued and paired, choosing canon stays the author's call. The net-new territory is the grab-bag no single artifact owns — stated identity/physical facts (ages, spellings, aliases), named objects, and place details below the Timeline's setting column — so the Bible **consumes and cites** the surfaces the framework already produces rather than re-deriving them. The new `continuity-bible` validator (`scripts/continuity_bible.py`) enforces **C1** schema (bad category enum, malformed `CF-NN` id, missing field, unquoted-numeric value, empty loci, duplicate id), **C2** locus presence & shape (a coarse chapter/§/¶/line/page token — a well-formedness precondition, **not** a firewall proof; locus *resolution* into the manuscript is deferred to the shared snapshot layer), **C3** contradiction integrity (a `## Contradiction Ledger` row must pair ≥2 real `canon_fact`s sharing entity+attribute but asserting **different** values — a bespoke markdown-table parse), plus advisory **C4** chronology consume-vs-rederive (a `chronology` fact that doesn't consolidate to a real Timeline scene id; override `<!-- override: bible-rederive CF-NN — … -->`) and **W1** coverage (a Timeline POV with no Cast entry, or a Timeline setting with no Places entry), both ERROR under `--strict`. C4 and W1 resolve against the project-root `Timeline.md` passed as a second input; Increment 1 sources character coverage from the Timeline **POV column** (the machine-readable name source) rather than the prose Pass-5 portraits, which have no machine-readable artifact yet. Ships with the canonical `example-continuity-bible.md` fixture (a Cast/Places/Objects/Chronology Bible consolidating `example-timeline.md`, with a real Mara-age contradiction) wired into `validate.sh --check-all` under `--strict`. Self-testable validators **49 → 50**. Homed in core-editor; spec: [`docs/continuity-bible.md`](../../../../docs/continuity-bible.md).

### Infrastructure — Crash-resistance for malformed block payloads (the non-P1 sweep batch)

Follow-up to the validator-fleet hardening: the 2026-06-20 sweep's recurring **crash-on-malformed** class — a `parse_*`/check path reaching `obj.get()` (or `.lower()`, or char-iterating a string) on a *valid-but-non-dict* JSON block payload (`[1,2,3]`, `"str"`, `42`, `null`-comment) and raising an **uncaught traceback** — is closed across the eight remaining (non-P1) sites the sweep confirmed (the four P1 sites were fixed earlier):

- **viz_manifest** (`manuscript-viz`) — a non-object manifest block now reports a controlled **E1** failure instead of crashing in `check()` (and never passes vacuously).
- **annotation_manifest** (`annotated-manuscript`) — same, a non-object manifest block → controlled **A1** failure.
- **crosslink** — `_anchor_str` tolerates a non-dict `anchor` (covers the X2 back-link path).
- **reanchor** — `reclassify` guards a non-dict annotation / non-dict anchor.
- **registry_check** — a non-object project sidecar is treated as unparseable drift (R3), not a crash.
- **annotation_export** (`obsidian-export`) — the footnote-definition sort filters non-dict entries **before** sorting, and the O3 comparison tolerates a `null` comment.
- **editor_scaffolding** — `_read` tolerates non-UTF-8 bytes (clean "cannot read" / exit 2, not a `UnicodeDecodeError` traceback).
- **regression_diff** — `_mech_tokens` coerces a non-string mechanism before `.lower()`, and `_chapter_of` guards a non-list `evidence_refs` (which was silently char-iterated, demoting a `new-in-quiet-chapter` W2 candidate to a plain `new` with no warning — a silent-loss bug, not just a crash).

Each fix mirrors `apodictic_artifacts.validate_obj`'s own `isinstance(obj, dict)` guard, applied identically to both byte-identical script copies. Locked with direct-unit regression self-tests for `reanchor`, `regression-diff`, `crosslink`, `manuscript-viz`, `editor_scaffolding` (non-UTF-8 read), and `registry_check` (non-object sidecar). Crash-resistance is not statically gateable by the `validator-conventions` M1–M4 checks, so each site carries its own self-test lock.

A **second, distinct crash class** in the same sweep: a malformed **finding_id** (or ledger id) used as a dict KEY or a SORT key — a non-hashable id (a JSON list/object kept as-is by `parse_*`) raises `unhashable type`, and a mixed `int`/`str` id set raises `sorted()`'s `'<' not supported between instances`. The four P1-era sites (the annotation A1 uniqueness map) were fixed earlier; this batch closes the remaining sibling sites and **centralizes one normalizer — `apodictic_artifacts.fid_key`** (the lowest shared lib, so `finding_trace`/`annotation_*`/`reanchor` all route through it without a circular import; a valid string id is unchanged, a malformed id is `str()`-coerced — matching the `"[^%s]"`-rendered footnote ref so the multiset/provenance join still ties):

- **reanchor** — `_fid` normalizes the `finding_id` at `build_reanchored` (re-anchor map + re-annotation), the orig-comment lookup, and the comment-fidelity check.
- **annotation_manifest** — the A1 uniqueness `seen` map, the comment-provenance `led_obj` lookups, the `manifest_ids` set, and the **ledger-side** index `led_obj[o["id"]]` (a malformed *ledger* finding id) all coerce through `fid_key` (an `art`-None-safe local mirror, since its `apodictic_artifacts` import is best-effort).
- **annotation_export** — both `build_obsidian` sorts (the offset/fid ref sort + the definition-block sort) and the `check_obsidian` O2 `manifest_set` + O3 `comment_of` dict keys.
- **finding_trace / intake_interview / reader_instrument / viz_manifest** — the four `ledger_*`-index functions (`ledger_inventory`, `ledger_index`, `ledger_index`, `ledger_findings`) all key the authoritative-ID set by a raw `obj["id"]` (the byte-identical pattern); each now routes that key through `fid_key`, so a malformed *ledger* finding id no longer crashes the index (reachable via each validator's public entrypoint — e.g. `viz_manifest.check` / `reader_instrument.check` / `intake_interview.interview`).

`regression_diff` already self-handled non-string ids (it skips them). Locked with non-hashable + mixed-type id regression self-tests (a list/mixed manifest `finding_id`, a non-hashable ledger id, and a non-hashable-id no-crash test on each of the four `ledger_*`-index functions), each raising against the pre-fix code.

### Tooling — cross-platform (Windows) gate parity

The validator self-tests and host generators now pass on a non-UTF-8 / CRLF (Windows) checkout, not just on Linux CI — so a maintainer can run the real gate (`bash scripts/validate.sh --check-all`) locally and trust the result. Three checkout/locale artifacts were closed: (1) `encoding="utf-8"` is pinned on all 70 text-mode fixture/output writers across the validator suite, so a cp1252-default box no longer writes an em-dash as byte `0x97` that the UTF-8 reader then chokes on (`bash scripts/validate.sh --self-test-all` is **48/48 without `PYTHONUTF8`**); (2) `.gitattributes` gains `* text=auto eol=lf` so every checkout stores and emits LF — fixing `release-generate.mjs --check`'s `\n`-anchored README match and future-proofing the byte-identical dual script mirror against EOL drift (zero renormalization: all tracked blobs were already LF); and (3) `build-codex.mjs` normalizes `path.sep`→`/` before its allowlist check, so the parity scan no longer false-positives on Windows backslash paths. No change to any diagnostic output.

### Draft-over-Draft Structural Regression Testing — `regression-diff`

A revision can no longer *quietly* lose ground. The new `regression-diff` validator (`scripts/regression_diff.py`; `validate.sh regression-diff <prior_run_folder> <this_run_folder>`) diffs the **whole Findings Ledger across two revision rounds** — did this revision resolve what it claimed, and did it break anything that was working? — a signal no single-round diagnosis can produce. Because finding IDs are **unique per run** (renumbered each round, no stable cross-round identity), cross-round matching is a **deterministic heuristic**: a current finding matches a prior one iff same origin code **and** equal chapter token (`apodictic_artifacts.chapter_token`) **and** ≥1 shared mechanism token (greedy, stable, one-to-one) — so every regression signal is a **candidate for editor judgment, never a mechanical verdict**. Classification: `persisted` / `resolved-and-held` / `recurrence-candidate` / `new` / `new-in-quiet-chapter`. The validator raises **R1** round-linkage (ERROR — both ledgers parse, non-empty, distinct rounds: the one mechanical invariant), **W1** recurrence-candidate (a finding the prior round marked `<!-- resolved: F-… -->` that re-appears — the fix may not have held; reverts to the prior round's severity on confirmation), **W2** new-in-quiet-chapter (a finding in a chapter the prior round left quiet — candidate fix-induced breakage; override `<!-- override: regression-cleared <runlabel>:<chapter> — investigated, not fix-induced -->`), and **W3** unexplained-drop. W1–W3 are advisory (re-diagnosing a *changed* manuscript legitimately shifts findings), ERROR under `--strict` — the `finding-trace` / `state-card-diff` posture; only R1 is a hard error. It reuses the shared primitives (`apodictic_artifacts.parse_blocks` + `chapter_token`, `finding_trace.resolved_cited_ids`, the `state_card_diff.resolve` two-snapshot scaffolding), prints to stdout like the sibling diff validators (the human-readable Regression Report is orchestrator-written at round-close, integrated in `state-lifecycle.md` §Cross-Round Regression Check), and ships with a paired two-round fixture (`example-run-folder-r1/`, `-r2/`) wired into `--check-all` (asserting round linkage plus the recurrence + quiet-chapter candidates under `--strict`). Validators 43 → 44. This is the dependency for round-trip re-anchoring of the annotated manuscript.

### Harness Engineering — Harness Contracts v2 (schema-coverage gate + closed-key enforcement)

The completion increment of the Harness Contracts v2 roadmap line: the schemas already *are* the single source of truth for every structured artifact and each is bound to a validator, but nothing forced them to *stay* the only source. This ships the drift-kill keystone. A new `schema-coverage` validator (`scripts/schema_coverage.py`) proves disk reality matches a declarative `schemas/_coverage.json` binding table at `--check-all`: **C2** no orphan schema (every `apodictic.*.schema.json` on disk is bound), **C3** no phantom binding (every row's schema exists), **C4** binding *proven* not asserted (the schema id literal is grep-reachable in a `.py` the **bound** dispatch arm delegates to — the "distrust count-shaped claims" discipline mechanized), **C5** canonical-gate reachability (the exact canonical filename token appears in `--check-all` and the file exists, or an auditable `self-test-only` escape for the two registry schemas), plus **C1** manifest validity, **C1'** closed-key table↔file agreement, and advisory **W1** dead-exclusion (ERROR under `--strict`). The shared engine (`apodictic_artifacts.py`) now honors **`additionalProperties:false`** (opt-in per schema) — the misspelled-field kill — and the six flat const-tagged blocks (`audit_trigger`, `readiness`, `severity_calibration`, `feedback_item`, `reader_question`, `scene_ethics`, all of whose optional fields are declared) are closed; `finding.v1` (forward-extended per pass), the sidecar, and `gate_event` stay open by design. A new `schema_field_names()` helper backs an advisory `--check-docs` prose lint that flags a field-set re-listing (a `Fields:`-labelled line) on a defer-marker doc that names a field the schema does not declare — catching divergence, not list-existence, and only on opt-in docs. The manifest dogfoods the discipline: it validates against two new schemas (`apodictic.schema_coverage.v1`, `apodictic.schema_binding.v1`), both themselves `additionalProperties:false`. `execution-gates.v1.json` is correctly *not* treated as an artifact (its name isn't `*.schema.json`, so the orphan glob already skips it — and listing it in `non_artifact[]` would trip W1). Wired into `validate.sh --check-all` against the **real** `schemas/` dir (C2/C5/C1' only have teeth against disk reality), with hermetic hostile-fixture self-tests for every check. Self-testable validators **50 → 51** (derived from `AGG_VALIDATORS`, re-enumerated not asserted). No model seam — pure stdlib harness mechanics; the Firewall is untouched. Spec: [`docs/harness-contracts-v2.md`](../../../../docs/harness-contracts-v2.md).

### Workflows — Interpretable Stylometric Explanation (descriptive style-feature labels over the voice fingerprint)

A **descriptive labelling layer ON TOP of** the Author Voice Fingerprint (#9). #9 measures *how distinctive* an author's voice is and persists it as scalar z-scores; a writer reading that profile learns *that* their voice sits 0.7 from their author centroid but not **which measured features** carry that distance, in plain language. This overlay attaches a **natural-language gloss** to a handful of the *salient measured* features — "the prose leans hard on the definite article", "function-word profile concentrated in *the / and / but*" — each bound by provenance (`feature_ref`) to the exact SETEC `voice_profile` feature it describes (`families.<family>.top_features[].{feature, mean, sd, cv}`). It does **no new stylometry** (it consumes the same per-family inventory #9 consumes) and offers **no advice**: it *names* a measured feature, it never prescribes a voice change and never fabricates a style claim. Rooted in *Latent Space Interpretation for Stylistic Analysis and Explainable Authorship Attribution* ([arXiv:2409.07072](https://arxiv.org/abs/2409.07072)), whose method attaches LLM-generated natural-language style descriptions to anchor points in a style-embedding space — this build ships the **firewall-safe descriptive slice** (the labels + their binding to a measured feature; the embedding/LLM that *generates* them is a deferred M2 seam).

This is the **riskiest of its wave** — one preposition from a Firewall breach — so the result schema is built so a *"write more like X"* directive is **unrepresentable**: there is no `recommendation`/`target`/`goal`/`rewrite`/`compare_to_author` field, `frame` and `direction` are closed *descriptive* enums (the indicative "elevated use of the definite article", never the imperative "elevate your diction"), and `register` is a comparability class, never a target author to emulate. The one residual free-text surface (`label`) is scanned by the validator's signature **X4** gate.

The new `style-explanation` validator (`scripts/style_explanation.py` + `validate.sh style-explanation`) enforces **X1** schema (`apodictic.style_label.v1`: closed `feature_family`/`frame`/`direction`/`magnitude` enums, `SL-NN` id, unique ids), **X2** provenance / anti-fabrication (every label cites a non-empty `feature_ref` into a consumed measurement — an un-sourced label is fabricated; the #9 `centroid_ref` discipline per-feature), **X3** no-severity-leak (no Must/Should/Could token in the prose or a label, no embedded `apodictic:finding` block — a style label is not a defect), the signature **X4** descriptive-not-prescriptive (a prescriptive voice-directive OR a first-class **comparison-to-emulate** match — `write/sound more like …`, `emulate …`, `model your prose on …`; advisory, ERROR under `--strict`; per-id override `style-frame SL-NN`, prose-level override the bare `style-frame`), **X5** same-register cluster (a `describes-cluster` label referencing ≥2 labels must share a `register` — the AI-prose domain-shift guard), advisory **X6** local-only hygiene (a missing `local-only` marker or an external URL — **WARN only, never gate-blocking**), and **W1** seed/coverage (a single glossed feature is a thin overlay; no blocks no-op). The adjective-ambiguous `direction` words (`reduced`/`lower`/`elevated`) read as indicative unless they govern a possessive object ("reduce **your** reliance …"), so a bare descriptive label never trips X4.

It does **not duplicate #9**: #9's unit is *one work's position* in stylometric space (a scalar `metrics` map, validator `author_fingerprint.py`); this unit is *one feature's natural-language gloss* (a `label` string + closed enums, validator `style_explanation.py`). They compose — both block types can coexist in one `Author_Voice_Profile.md`, or the labels can live in a sibling `Author_Style_Explanation*.md` — but neither subsumes the other. The module is **descriptive, local-only, off the editorial severity scale**, and ships **no model dependency**: the label-*generating* embedding/scoring model is a deferred **M2** lazy-import + `skipif` seam, and the M1 validator never calls a model. Ships the canonical `example-author-style-explanation.md` (a local-only profile with three same-register `function-words` labels forming one coordinating cluster plus one out-of-cluster punctuation label) wired into `--check-all` under `--strict`. The self-testable validator count is **derived** from `validate.sh`'s `AGG_VALIDATORS` list (no hand-maintained number). Spec: [`docs/interpretable-stylometric-explanation.md`](../../../../docs/interpretable-stylometric-explanation.md).

### Workflows — Manuscript-Structure Visualizations

Chart 7-nonfiction — the **claim ladder** — now ships render-only (Manuscript-Visualization
Completion, M1). The `apodictic.viz_manifest.v1` manifest gains four OPTIONAL, additive arrays
(`co_presence` / `scene_functions` / `reveal_points` / `claim_ladder`); the M1 render-only chart is
the claim ladder over `apodictic.argument_spine.v1` (C0 thesis + C1…Cn subclaims) annotated with
support coverage from `apodictic.support_plan.v1` (support type + in-hand/to-acquire, or a
bare-assertion marker). The `manuscript-viz` validator gains gates **X1** (new-array schema + the
no-scene-axis firewall — a `scene_ids`/`scene_id`/`section` key on a `claim_ladder[]` object is a
hard failure), **X5/X6** (claim-ladder provenance — `claim_id` resolves via the reused
`argument_spine.spine_subclaim_ids()` leading-`Cn`-token parser, `label` byte-equals the subclaim
string minus its `Cn:` token, each `support[]` item byte-copies a real `support_plan.v1` block),
**X7** (no duplicate rung), **X8** (producer-present — no producer, no chart), and **W3** (chart
coverage). No new schema and no new validator — the validator count stays DERIVED. Charts
4/5/6/7-fiction remain producer-gated; a claim-to-scene overlay is out of scope (no subclaim→location
producer exists). The canonical `--check-all` Structure Map gate now exercises the claim ladder
against the pre-draft Argument_State spine. Render-only and firewall-clean: no renderer or validator
in this layer calls a model.

### Validators — POV Voice Profile §4e Must-Fix propagation validated

The **Must-Fix row** of the five **POV Voice Profile** rows in `pass-dependencies.md` §4e (Audit-Signal Propagation Table) is promoted from provisional to **"Validated 2026-06-19 (audit-signal-propagation self-test + multi-POV fixture)."** The `audit-signal-propagation` self-test now exercises it directly: four in-code cases in `letter_checks.py` `run_self_test` (`pov_propagated_clean`, `pov_unpropagated_errors`, `pov_override_body_no_error`, `pov_override_body_warns`) drive `audit_signal_propagation(text)` with a believable multi-POV editorial-letter snippet (Mara/Jon + Mara/Elen pairs) whose voice-collapse-on-2+-pairs + Blind-Swap-fail signal is expressed as a **Must-Fix floor** — the §4e Must-Fix row's signal class — under a `### POV Voice Profile Audit` appendix subsection the validator parses as audit `POV Voice Profile` (slug `pov-voice-profile`). The cases assert: (positive) the Must-Fix floor propagating to a body Must-Fix via audit-name reference + shared evidence line `L1840` is clean; (negative) the same signal unpropagated ERRORs; (override) the negative case plus a body `<!-- override: audit-propagation-must-fix … -->` marker yields no ERROR and one WARN. The validator's logic is unchanged — coverage only. Scope is honest: the propagation validator enforces *canonical propagation* of a **strong** audit-internal signal (hard gate / Must-Fix floor / HIGH) to the mandated synthesis tier, and has no mechanism to derive or assert a Should-Fix / Could-Fix tier or a downshift. The other four rows — the single-pair **Should-Fix**, the Blind-Swap-pass **Could-Fix**, and the two downshift modifiers (threshold-confidence and POV-mapping-provenance) — therefore **remain provisional documented editorial conventions** (not fixture-validated, the same posture as the Narrative-/Argument-Decision rows), tunable on a live multi-POV manuscript run.

### Workflows — Promise-Contract Fidelity (does the pitch keep the promise the book makes?)

A new core-editor workflow module that points APODICTIC's contract-inference move at the author's own **marketing copy** — query, synopsis, blurb, logline — diagnosing the document-level fidelity gap between the persisted pitch and the inferred Contract: emphasis distortion (PCF1), reveal leak (PCF2), over-promise (PCF3), under-sell (PCF4), and cross-document inconsistency (PCF5). It **consumes** Shelf & Positioning (genre/comp/tone) rather than re-deriving it, and is firewall-bound: it flags the gap and a *class* of repair, and never drafts the replacement copy (Shelf & Positioning's Reframe Protocol owns rewriting — this is its diagnostic-only sibling). The pitch copy becomes a **first-class persisted input**, `apodictic.pitch_copy.v1` (a `[Project]_Pitch_Copy_[runlabel].md` block per document, declared `copy_type` + verbatim `text`); persisting it is what turns the firewall guard into a substring check and the disclosure gate into a mechanical one. Findings are `apodictic.finding.v1` blocks with origin `PCF` (`F-PCF-NN`), and adopt a `PCF`-scoped **namespaced evidence-ref convention** — `copy:<copy_type>¶<n>` / `contract:<FIELD>` / `ms:<locus>` — so the two-sided gap is machine-checkable (the shared schema is unchanged for every other origin). The new `promise-contract` validator (`scripts/promise_contract.py`) enforces **P1** two-sided gap (every `F-PCF` finding cites ≥1 well-formed `copy:` ref — the full `copy:<copy_type>¶<n>` grammar whose `copy_type` is actually *persisted* — AND ≥1 `contract:`/`ms:` ref; a locus-less, malformed, or dangling copy ref is no evidence and cannot satisfy the gate — the signature integrity check), **P2** pitch copy persisted & typed, **P3** reveal-leak form gate (a PCF2 against a `synopsis` is a calibration error — a synopsis discloses by design), plus advisory **W1** drafted-copy leak (a multi-sentence quoted block in the report that isn't verbatim persisted copy — the Firewall; overridable per id) and **W2** market-prediction drift (the prohibited sales-prediction phrase set — the #14 boundary; overridable), both ERROR under `--strict`. Resolved decision OD1: `CONTROLLING IDEA` is promoted to a first-class colon-delimited Contract schema field (alongside `READER PROMISE` / `ENDING TYPE` / `NON-NEGOTIABLES`) so PCF1/PCF4 resolve it directly. Ships with the canonical `example-promise-contract.md` fixture (a query committing PCF1+PCF4 with valid two-sided refs, and a disclosing synopsis that proves the P3 negative) wired into `validate.sh --check-all`. Homed in core-editor; spec: [`docs/promise-contract-audit.md`](../../../../docs/promise-contract-audit.md).

### Validators

48 → 49 self-testable validators. Added `promise-contract` (Promise-Contract Fidelity: P1 two-sided gap, P2 pitch copy persisted & typed, P3 reveal-leak form gate, W1 drafted-copy firewall leak, W2 market-prediction drift), with its own `--self-test` and a canonical `--check-all` gate over `example-promise-contract.md`.

### Workflows — Reader-Persona Simulation (where the book lands differently by audience)

A new specialized-audit overlay on Pass 1 (Reader Dynamics): Pass 1 maps the experience of one composite reader, but a manuscript meets an audience with different tolerances. Persona simulation runs the *same* reader-experience lens through several declared reading **dispositions** and surfaces where the predicted experience **diverges** — and divergence is the diagnostic signal, exactly as contract-mismatch is. It sits on the sharpest firewall edge in the Horizon scan (the non-viable **Simulated Reader Focus Group**, item 17, which fabricates reader reactions as data), so the boundary is enforced by **three mechanical guards**, not rhetoric: a persona is a **closed-key disposition vector**, never an invented character (`D5`, a non-overridable ERROR — the real guarantee, since the subset engine silently allows unknown keys); every divergence is **grounded** in a real finding or Timeline locus (`D2`, the signature gate — an ungrounded prediction is a fabricated one); and a first-person reader-reaction **quote presented as data is scanned** (`D4`). A persona is an `apodictic.persona.v1` block of disposition axes only — `pace_tolerance` / `genre_familiarity` / `content_sensitivity` / `thematic_receptivity` (the **verbatim** Argument-Engine `Audience.Receptivity` enum) / `continuity_attention` — plus `id` and a boolean `target`. Divergence is an `apodictic.divergence.v1` block: an `anchor`, a nested per-persona `experiences` map (engaged/neutral/friction/disengage), a `magnitude`, and an optional `asserted_severity`. **Severity honesty** is preserved against *persona-shopping* (softening a real defect by finding some disposition for which it "works"): severity is locked against the **target** persona, so a divergence whose `asserted_severity` is *lower* than the anchored finding's locked Ledger severity fails `D3` — "works for the expert, fails for the newcomer" is recorded as divergence, but if the newcomer is the target it stays a defect at full severity. The new `persona-divergence` validator (`scripts/persona_divergence.py`) enforces **D1** schema (incl. the nested `experiences` enum and that each key is a declared persona — the `retcon_plan.scores` nested-object precedent), **D2** grounded prediction, **D3** target-severity anchoring (exactly one `target:true`; no downgrade), plus advisory **D4** anti-fabrication (ERROR under `--strict`; override `persona-quote D-NN`) and **W1** coverage (≥2 personas with a varying disposition axis); **D5** is a non-overridable ERROR. Homed as a Pass-1 overlay in `specialized-audits/references/craft/`; ships the canonical `example-persona-divergence-map.md` + `example-persona-divergence-ledger.md` (a target newcomer and a genre-expert diverging on a locked Must-Fix Ch-3 lull) wired into `--check-all` under `--strict`. Self-testable validators **53 → 54**. Spec: [`docs/reader-persona-simulation.md`](../../../../docs/reader-persona-simulation.md).

### Round-Trip Re-Anchoring — the workflow glue (Increment 2)

The `reanchor` validator (Increment 1) classified held / moved / vanished / ambiguous / not-re-anchorable but only **validated in memory** — it never produced the revision-aware marked-up copy a revision loop needs on disk, and it left the anchor-level × finding-level join unwired. This increment closes the round-trip into a real workflow (the ROADMAP "Toward truly great" item #2):

- **`reanchor.py emit <prior_run_folder> <new_snapshot> [-o <out_dir>]`** — re-anchors draft N's margin notes onto the revised draft N+1 and **writes** `[Project]_Reanchored_Manifest_[runlabel].md` + `[Project]_Reanchored_Annotated_Manuscript_[runlabel].md` (held/moved only, each comment carried byte-identical — relocate, never re-author). It re-gates RA1–RA3 before any write (refuses to emit an unverified re-anchor); the `Reanchored_` infix keeps a carried-over copy distinct from a re-diagnosed one and out of the `*_Annotation_Manifest_*` glob.
- **`reanchor.py crossref <prior_run_folder> <new_snapshot> <this_run_folder>`** — joins the round-trip's per-annotation classes against `regression-diff`'s per-finding classes **by `finding_id`** (the §Q2 orchestrator join; `regression_diff.crossref_classes` returns the prior-keyed class map the re-anchored manifest shares). It corroborates the heuristic regression signal with anchor ground truth: `vanished` × `resolved-and-held` (the fix landed) and `held`/`moved` × `recurrence-candidate` (the fix did not hold — `X1`, advisory / ERROR under `--strict`).
- **Revision Round Protocol wiring** — `state-lifecycle.md` gains a §Round-Trip Re-Anchoring step (snapshot the revised draft → classify + emit the revision-aware copy → cross-reference at round-close), the anchor-level sibling of the existing Cross-Round Regression Check.
- **`--check-all` `round-trip glue chain` gate** — exercises emit → A-gate the emitted copy (ledger-optional) → crossref end-to-end on a temp copy of the canonical fixture, so the flow is proven to compose, not just the individual validators.

No new validator and no new command — this increment adds **zero** entries to `AGG_VALIDATORS`, so it leaves the validator count exactly where `main` already has it (the count is **derived** from `AGG_VALIDATORS` by `validate.sh`, never a hard-coded literal). On the current `main` that count is 50 (`continuity-bible`, PR #123, landed after this branch was cut), so the post-merge count stays 50 — this PR does not change it. The glue is two subcommands on the existing `reanchor.py` + one on `regression_diff.py`, both mirrored. Spec: `docs/annotated-manuscript-reanchoring.md` (Increment 2).

### Onboarding — annotated-manuscript sample + host-positioning

"See It in Action" now includes a live **annotated-manuscript** sample ([`sample-annotated-manuscript.html`](sample-annotated-manuscript.html)) — the marked-up copy with severity-tagged, bidirectionally-linked margin findings, rendered from the canonical `example-annotated-manuscript/` fixture via `annotation_export.py html` — so the annotated-manuscript deliverable (the standard "#1 human-DE deliverable") has a no-install showcase beside the editorial-letter, targeted-audit, and pre-writing samples. The install section's "Claude Code / Cowork (legacy host flow)" header, which contradicted the first-class routing table at the top of the install section, is reworded to plain "Claude Code & Cowork" (ordering unchanged).

### Research — API Reliability Layer

The `/research` Citation Verifier and Field Reconnaissance modes now distinguish a
source that is genuinely *not found* from one that was *not checked* because the
index it needed was degraded or exhausted — closing the failure where a silently
degraded API masqueraded as a clean (or missing) result.

A new stdlib-only `api_reliability.py` (in the research scripts dir) adds, per
batch run: per-provider call **budgets**, a per-provider **circuit breaker**
(run-scoped — it never persists open across runs), and a **reliability ledger**.
`response_cache.py` gains **TTL freshness** (bibliographic metadata 30 days,
Wayback 7 days; env-overridable) wrapped in a backward-compatible envelope; the
no-sticky-error rule is preserved — transient `_error` payloads are still never
written to disk, even with a TTL.

`academic_apis.py`'s batch `output` now carries a `reliability` block (per-provider
calls/ok/errors, budget, circuit state, and a `coverage` summary naming any
degraded provider), and each result gains `resolution_status ∈ {resolved,
not-found, not-checked}`. Citation Verifier and Field Reconnaissance report a
**Source coverage** line: when coverage is DEGRADED, any `unretrievable` verdict on
a citation whose only candidate index was a degraded provider is reported as
NOT-CHECKED, not NOT-FOUND, and a DEGRADED state on a high-stakes / Pre-DE run is
disclosed as a blind spot in the synthesis Absence Inventory.

Reliability bookkeeping is default-on; `APODICTIC_RELIABILITY=off` omits the
top-level `reliability` block. The additive per-result
(`resolution_status`/`degraded_providers`) and summary (`not_checked`/`not_found`)
keys remain, additive and never altering an existing value, so the legacy
result/summary keys are unchanged. Per-provider budgets and TTLs are
env-overridable (`APODICTIC_BUDGET_<PROVIDER>`,
`APODICTIC_CACHE_TTL_METADATA_DAYS`, `APODICTIC_CACHE_TTL_WAYBACK_DAYS`).

### Infrastructure — ID-scope the softness-downgrade override (closes the Deficit-Lock gate-bypass)

The 2026-06-20 validator sweep found a **P1 override-parse / gate-bypass** in `softness-check`: it tested `SOFT_MARKER in body` as a single global boolean, so **one** unscoped `<!-- override: softness-downgrade -->` marker anywhere in the letter blanket-acknowledged **every** locked finding's softness downgrade — dismantling the Deficit Lock (per-finding severity honesty), the framework's central value. The softness override is now **ID-scoped**: `<!-- override: softness-downgrade F-<ORIGIN>-<NN> — <rationale> -->` downgrades ERROR→WARN **only** for the named Finding Lifecycle ID (exact, boundary-matched so `F-P5-021` / `F-P5-02-extra` cannot mask `F-P5-02`); a **bare marker with no resolvable ID acknowledges nothing**, and markers inside backtick code spans (documentation examples) are ignored. There is intentionally no blanket/all-findings form. Behavioral change: an **id-less** (legacy heuristic-path) locked finding can no longer be bare-acknowledged — it must carry a Lifecycle ID (which the Deficit Lock already requires for synthesis-bound findings). Locked with regression self-tests including the signature case — an override for one finding must **not** mask another finding's downgrade (`override_masks_only_named_id`). The canonical rule docs (`output-policy.md §Severity Honesty Protocol`, `run-synthesis.md`) are updated to the ID-scoped form.

The same loose-substring override idiom in `timeline_checks` (`timeline-arithmetic-conflict`, `timeline-anchor-conflict`, `timeline-diff-undocumented`) is hardened the same way — a shared `_has_override(body, slug)` requires the **exact slug followed by a delimiter** (so a suffixed slug like `…-conflict-later` is rejected) and strips code spans before scanning — across both the Python implementations and the three bash degrade arms in `validate.sh` (parity). New hostile self-tests cover the suffixed-slug and backtick-span cases.

(softness-check has no bash degrade arm — it delegates to python3 — so only its Python path needed the fix.)

### Workflows — Uncertainty-Resolution Intake Interview (disambiguate what the text leaves open)

A narrow, optional loop on top of the existing intake: at the after-Pass-0/1 checkpoint (the Mid-Run Escalation Check seam), it asks the author to resolve a **specific structural ambiguity the framework detected but cannot settle from the text** — "is the non-linear ordering in Ch 4-6 a deliberate braid, or drift?" — and only that. APODICTIC's draft-then-validate intake and Shelf & Positioning already own genre/controlling-idea/reader-promise/audience capture, so this **defers** all of it and confines itself to the one thing nothing covers: *was this detected feature intentional?* That niche is a real structural guarantee, not a slogan — each query is an `apodictic.intake_query.v1` block whose `kind` is a **closed enum** (`timeline-order` / `pov-choice` / `tonal-shift` / `structural-device` / `register-straddle` / `other-detected-ambiguity`), every value a flavor of intentional-vs-accidental, so the enum cannot express a contract ask. It is the author-facing sibling of the Beta-Reader Instrument (that turns uncertainties into *reader* questions; this turns them into *author* questions), and both are barred from softening a verdict. The firewall is **calibrate the lens, never suppress a finding**: `treat_as_intended` may direct *how* analysis treats the feature (assess the braid on its own terms) but may never pre-empt whether a finding is raised — that would be the author-editor concession loop through the front door, dismantling the Deficit Lock. The new `intake-interview` validator (`scripts/intake_interview.py`) enforces **I1** schema, **I2** no-contract-duplication (a question re-asking a contract element — advisory; ERROR under `--strict`; per-id override), **I3** grounded ambiguity (a resolving `ambiguity_ref` against the Findings Ledger **or** a non-empty `source_note` for ID-less Pass-0 / Unresolved-Questions ambiguities — a query grounded in neither is manufactured, and a stated-but-dangling ref is an error), **I4** calibrate-not-suppress (suppression phrasing in `treat_as_intended` — ERROR by default, with a negation guard so the spec's own recommended "it does not pre-suppress any finding" phrasing stays clean), plus advisory **W1** coverage (a Pass-0/1 LOW/UNCERTAIN finding or an Unresolved-Questions bullet with no query). It runs only on interactive-input-capable hosts and never blocks a non-interactive run (it falls back to the framework's own intentionality inference). Wired into `run-core.md` at the after-Tier-1 checkpoint, with `references/intake-interview.md` as the protocol. Ships the canonical `example-intake-interview.md` + `example-intake-interview-ledger.md` (one ref-grounded query, one source_note-grounded query) wired into `--check-all` under `--strict`. Self-testable validators **50 → 51**. Spec: [`docs/uncertainty-intake-interview.md`](../../../../docs/uncertainty-intake-interview.md).

### Infrastructure — Validator-fleet hardening + the `validator-conventions` meta-linter

A fleet-wide adversarial sweep (2026-06-20, ~40 agents over 22 validators × 8 bug classes, each finding verified) surfaced a set of recurring latent bug classes that manual review had let drift. This change closes the two **structural** ones and gates them so they cannot recur, and fixes the highest-severity crashes.

- **New meta-linter `validator-conventions`** (`scripts/meta_lint.py`) — *a validator that validates the validators*. **M1**: every `AGG_VALIDATORS` entry has a dispatcher case that handles `--self-test`. **M2**: no validator classifies inputs by a raw `apodictic:<type>` marker scan (membership `in`/`not in` OR a str/re scan op `.find`/`.count`/`re.search`/…); resolvers must classify on parsed blocks (the `_has_block` / `art.parse_blocks` idiom) — the substring anti-pattern misroutes a file that merely *names* a marker, silently false-passing. **M3**: the advertised count is derived from `AGG_VALIDATORS` (`AGG_COUNT` via `$#`), never hand-typed. **M4**: no orphan schema (every `*.schema.json` filename stem in the resolved schema dir is referenced; degrades to a WARN, not a clean PASS, if the resolver is unavailable). **M5**: no validator detects an override marker by a bare `<!-- override: <slug>` substring scan (Python `"<!-- override: %s" % slug in body` / bash `grep -F "<!-- override:`) — the override-marker sibling of M2; use the hardened `override_marker.has_override` / `_has_override` helpers. Wired into `--self-test-all` and the `--check-all` release gate (it is itself in `AGG_VALIDATORS`, so **M1 checks the meta-linter against its own rule**). Validators **55 → 56**. Spec: [`docs/validator-conventions.md`](../../../../docs/validator-conventions.md).
- **Resolver-substring class closed (13 validators)** — `legal_risk`, `scene_ethics`, `feedback_triage`, `argument_spine`, `retcon_plan`, `continuity_bible`, `world_bible`, `finding_trace`, `reader_instrument`, `viz_manifest`, `crosslink`, `annotation_manifest`, and `promise_contract` now classify input files on parsed blocks via a shared `_has_block` helper instead of a raw marker substring. Before: a decoy file naming a marker in prose, passed before the real artifact, won resolution and the validator reported "nothing to check" (exit 0) — silently masking a real failure. M2 now gates the whole class.
- **Crash-on-malformed P1s fixed (3)** — `promise_contract.parse_findings`, `retcon_plan._score_errors`, and `state_card_diff.check_one` guarded `obj is not None` only, so a non-dict JSON block payload (`[1,2,3]`, `"str"`, `42`) reached `obj.get()` and raised an uncaught traceback. Each now guards `isinstance(obj, dict)` and surfaces the existing clean "expected a JSON object" error (controlled exit 1). Locked with per-validator non-dict-payload regression self-tests.
- **Crash-on-malformed P1 fixed — `honesty_check` (softness-check), distinct class** — softness-check already filtered non-dict block payloads upstream (`parse_locked_findings` skips `not isinstance(obj, dict)`), so the non-dict-payload class never applied to it. Its real latent crash was a locked dict finding with a **non-string `id`** (e.g. `{"id": 42, …}`): the int/list id reached `re.escape(fid)` in `_id_delivered_in_body` and raised an uncaught `TypeError`. It now guards `isinstance(fid, str)`, routing a non-string id to the id-less heuristic path (controlled ERROR, no crash). Locked with a load-bearing regression self-test (`crash_nonstring_id_finding` / `crash_nonstring_id_with_override`) that raises against the pre-fix code.

This PR also hardens the **override-substring gate-bypass** class (the override-marker sibling of the resolver-substring class above) across the **bash arms + the recently-built Python gates**, and introduces the shared helper + a gate so it cannot re-enter. The bare `<!-- override: <slug>` prefix test — exploitable via a suffix-collision slug (`<slug>-but-not-really`) or a code-span decoy (a marker quoted inside a backtick span / fenced block) — is replaced by a single shared hardened helper. The Python sites converted here (`letter_checks`, `config_checks`, `editor_scaffolding`, `diagnostic_vocabulary`, and — closing this PR's *own* timeline/softness hardening — `timeline_checks` and `honesty_check`, which had each carried a *local* `re.compile(r"```...```|`...`")` stripper that a multi-backtick / `~~~`-fenced / multiline example could bypass) now route through **`override_marker`**: `has_override` (a state-machine code-span stripper + slug boundary-match) for the slug gates, or `strip_code_spans` for `honesty_check`'s ID-scoped softness markers. All bash sites (`severity-floor`, `audit-signal-propagation`, `underdiagnosis-triggers`, `ledger-consolidation`, `decision-layer-check`, `quality-risk-triggers`, `audit-tier-criterion`, `argument-recon-prerequisite`, and the three `timeline-*` arms) delegate to that same helper via a stdin CLI (with a documented best-effort `_has_override` shell fallback for no-python3). A **bash↔Python divergence** (the legacy bash arm stripped only *inline* code spans, so a marker inside a *fenced* block was wrongly honored by bash though the Python path rejected it; and the bash literal rejected `<!--  override:` / `<slug>—reason` whitespace/dash forms Python accepts) is closed — both paths now share one implementation. `strip_code_spans` is a CommonMark-faithful state machine: a closing fence must be the fence run **plus trailing whitespace only** (a `~~~not-a-close` / ` ```lang` line is content, not a premature closer), an opener is capped at **3 leading spaces** (a 4-space/tab-indented fence is indented code), and a **backtick** opener whose info string contains a backtick (`` ```info` ``) is not a fence at all (CommonMark — a tilde info string is unrestricted) — so a malformed-fence example can neither expose nor suppress a live marker. Each site carries a code-span-decoy + suffix-collision regression. **M5 gates the bare-substring form going forward** — its Python string-body matcher is delimiter-aware, so an *opposite*-quote character inside the literal (`"…author's…"` / `'…"quoted"…'`) cannot end the body early and evade the scan, and the body spans newlines so a **multiline triple-quoted** scan is caught too; zero violations across the converted fleet.

> **Scope — NOT yet fleet-complete (tracked follow-up).** Five EARLIER validators still detect overrides with their own *compiled-regex* logic that is slug-boundary-matched but does **not** strip code spans, so a code-span-decoy override remains a latent bypass there: `content_advisory` (`advisory-eval` / `advisory-eval-prose`), `persona_divergence` (`persona-quote` — silences the D4 anti-fabrication boundary), `intake_interview` (`intake-dup`), `author_fingerprint` (`fingerprint-frame`), and `world_bible` (`world-rule`/`-cost`/`-geo`/`-firewall`). M5 does not flag them (it detects the bare-substring form, not a compiled regex). Migrating these to `override_marker` and extending M5 to gate the compiled-regex form is a **round-2 PR** (it builds on the `override_marker` + M5 this PR lands on `main`). The sweep's other remaining classes (non-P1 crash sites; lexical-regex over/under-fire heuristics the specs concede are fuzzy) are likewise deferred — not statically gateable by M1–M5.

### Tooling — Windows EOL determinism in validator output writers

Completes the cross-platform gate parity from the previous wave. Once `.gitattributes` made every checkout LF, the canonical **byte-identical** export checks (`html-export`, `obsidian-export`, and the producer chain) failed on a Windows checkout because the export/validator scripts wrote their output with the platform-default newline (CRLF on Windows) — so a fresh build no longer matched the now-LF committed fixtures (Linux/CI was never affected: it wrote LF either way). Pinned `newline=""` on every text-mode write `open()` (93 call sites) plus the one `os.fdopen` sidecar writer in `run_gate.py`, across the validator suite, in both mirror dirs byte-identically, so every artifact is written LF on every platform. `bash scripts/validate.sh --check-all` is now green on a Windows (cp1252 + LF) checkout end-to-end. No byte change on Linux (text-mode `\n` was already written verbatim) and no change to any artifact content.

### Workflows — Standalone Worldbuilding-Bible Coherence Tool (`/world-bible`)

A new optional-artifact tool that checks the SFF author's **own pre-draft worldbuilding bible** — the rules of the magic/tech and its cost, the geography, the order of events, the factions — for self-contradiction, **before any manuscript exists**. It is distinct from the framework's manuscript-facing SFF surfaces: the Genre Module SF/F checks a *manuscript's* Rule Ledger and Cost Matrix in-scene, and the SFF Worldbuilding Integration audit checks whether the world does narrative *work* (its thesis: "the core problem is not inconsistency, it is inertness"). This tool ports the genre module's **consistency** vocabulary (closed limits, cost types, scaling) to **bible scope, pre-draft** — checking the baseline the integration audit assumes — and is a sibling to the post-draft Auto-Derived Continuity Bible (same block-and-validator machinery, different lifecycle stage and input). Each stated world fact is a first-class `apodictic.world_fact.v1` block (`category` ∈ rule/cost/place/distance/event/faction/entity, the discriminator that selects the contradiction arm; `subject` the grouping key; `value` always a quoted string so numerics type-check and parse; optional `polarity` for rules, `cost` for cost/rule facts, `pair_subject` for distance/event edges; `loci` ≥1). It is firewall-bound: it records **stated facts only** (never inventing an unstated rule, cost, distance, or date) and **surfaces contradictions, never resolves them** — both conflicting values are recorded and paired, and any recommendation stays abstract-structural ("the bible prices blood-magic two ways — reconcile or stage the escalation", never "the cost is one year of life"). The new `world-bible` validator (`scripts/world_bible.py`) enforces **W1** schema **plus a bespoke closed-key check** (the subset schema engine silently admits unknown keys, so a misspelled field is caught here or the closed-set guarantee is hollow) **and a bespoke `cost` value-type check** (the schema leaves `cost` un-typed because the subset engine cannot express a `string|null` union, so a non-string/non-null `cost` — an unquoted `5`, a list, a bool — fails `W1` here instead of reaching the cost arm and crashing `_norm_value`), **WD** id-uniqueness, and the deterministic, stdlib-only, conservative contradiction arms: **WB-R1** closed-set rule consistency (same subject + normalized value, `can` vs `cannot` / `requires` vs `cannot`), **WB-C1** cost contradiction (two different stated costs for one subject) + advisory **WB-C2** free-then-costed (the pre-draft form of Cost Amnesia; ERROR under `--strict`), **WB-G1** distance contradiction (one edge, two parsed distances **within a commensurable unit class** — a spatial mile/league/km axis and a temporal travel-time day/hour axis are kept separate and never collide-check against each other, so a 6-day ride and 120 miles can both be true), **WB-G2** chronology (a **cycle** in the happens-before graph via a stdlib DFS, or the same event at two `Day N` anchors), and a **WF** firewall prose scan (a resolution/invention verb leaking into the bible's prose; advisory, ERROR under `--strict`). Each conflict is overridable per-pair (`<!-- override: world-rule|world-cost|world-geo WF-NN/WF-MM — <rationale> -->`, order-insensitive; `<!-- override: world-firewall — … -->` for WF), recording an intended contradiction (a staged reveal, a documented cost escalation) without softening the verdict. Routed as the `/world-bible` **command** (tool-like `/legal-risk`, not a manuscript-pass audit), usable before or alongside drafting in the pre-writing pathway's spirit. Ships with the canonical `example-worldbuilding-bible.md` fixture (an epic-fantasy bible with two deliberately staged + overridden contradictions) wired into `validate.sh --check-all` under `--strict`. Self-testable validators **50 → 51**. Homed in core-editor; spec: [`docs/worldbuilding-bible.md`](../docs/worldbuilding-bible.md).

## v2.4.0 - 2026-06-14

### Nonfiction Argument Engine — uncompared-recommendation carve-out

`dialectical-clarity.md` gains **classification rule 2a**: for an argument whose controlling claim is a *recommendation to act* (AT3 — "X should do Y"), the comparative dimension is constitutive of the claim, so an AT3 recommendation that discharges **none** of its comparative burden (BP5 primary + OB3, no funding mechanism) is **not evaluable as a recommendation** — a defeat under decision test two (Evidence-evaluability) — and the verdict is **Structurally Unsound** (FM-A10, The Uncompared Proposal), with a matching note at the Step-9 Final Diagnostic Question. This is a bounded exception to rule 2's default-to-SOUND discipline, scoped to AT3 recommendations only (descriptive/explanatory/interpretive theses are untouched) and guarded by a *wholly-absent vs. partially-discharged* line — a recommendation that engages even one alternative thinly stays a Should-Fix soft spot in a sound argument. **Calibration update (post-benchmark):** the guard is tightened so that naming *any* alternative — even a weak or strawmanned foil — counts as partially-discharged (soft spot); only the total absence of any comparison triggers Unsound. (A benchmark run had `andreessen-techno-optimist-manifesto` regress SOUND→UNSOUND because a strawman "the only alternative is Communism" framing was misread as zero comparison.) Two independent cross-vendor reviewers (Gemini + GPT-5.5) ratified the narrowing and both flagged a token-foil gaming risk, so an **anti-gaming clause** was added: a named foil disables only the *automatic* FM-A10 defeat; a merely decorative foil (no mechanism/criteria/costs/tradeoff) can still be Unsound via the general evaluability test (rule 2), not the AT3 auto-trigger. It brings the engine into line with the `policy-brief-uncompared` ground-truth key (GT7 = UNSOUND), which the engine previously read SOUND. Verdict-behavior change for argument-shaped runs; **gated on a benchmark convergence run** (no `--check-all` gate covers behavioral calibration). No validator/schema change. See `docs/argument-benchmark-calibration-round.md`.

### Command Surface — trimmed to 13

Retired three redundant command entry points, all reachable through `/start`: `/revision-plan` (a compatibility alias for `/coach`), `/develop-edit` (the default `full_draft` + `repair` router path), and `/diagnose` (a targeted `repair`). A writer with a draft lands on the `/start` router first anyway, so these added surface without adding capability. The distinct doors stay first-class (`/ready`, `/pre-writing`, `/coach`, `/audit`, `/research`, `/plot-coach`, `/legal-risk`, `/triage-feedback`, `/reader-questions`, `/new-project`, `/projects`). The registry command taxonomy (`category` / `status` / `routerEquivalent` / `writerQuestion`) is the single source the grouped README lists generate from. Routing references that pointed at the retired commands now point at `/start`.

### Validators — finding-trace completion glob narrowed

`finding-trace`'s `_COMPLETION_GLOBS` narrowed from `*_Revision_*.md` to `*_Revision_Report_*.md`, so a deadline-coaching `*_Revision_Calendar_*.md` is no longer mis-classified as a completion artifact (which would let its mentions advance a finding toward `revised`). Aligns finding-trace with the Increment-4a `revision_round` gate, which already narrowed its `revision_report` key. Negative-test guarded (`calendar_not_completion`); the revision-*stage* glob (`_REVISION_GLOBS`, for plan-coverage) stays broad.

### Workflows — Legal Risk Register detection layer

The Legal Risk Register gains a **detection layer** (`core-editor/references/legal-risk-register.md` §Detection guidance / §Escalation-trigger taxonomy): per-class textual signals for what to flag under each `risk_class` (defamation / privacy / rights-clearance / other, with the finer categories — intrusion, false light, trade secrets, incitement, … — as sub-signals), a **severity model** (base tier raised by documented modifiers: `+identifiable-living-private-person`, `+serious-allegation`, `+weak-or-no-documentation`, `+international-distribution`, `+author-signed-agreement`, `+marketing/cover/merchandise-use`, `+minor-or-vulnerable-subject`), route-to-counsel bright lines, a *flag-don't-resolve* posture for jurisdiction divergence, and a compact controlled-vocabulary **escalation-trigger taxonomy** (~20 codes → default tiers) for the `escalation_trigger` field. Lean by design — the runtime module carries the heuristics; the cross-model research + citations live in `docs/legal-risk-detection-level-setting.md`. Firewall unchanged: detection only; a qualified lawyer is the final gate. No schema or validator change.

### Workflows — Legal Risk Register router wiring

The built Legal Risk Register module is now reachable from the router and a command, not just internally. `constraint:risk` ("sensitive or legally risky content") **offers** the register and, on accept, attaches `[Project]_Legal_Risk_Register_[runlabel].md` as a companion artifact (synthesis constraint hook in `run-synthesis.md` — the first `constraint:`-keyed presentation overlay, and the first offer-then-attach one, since the not-a-lawyer framing warrants a confirm). New `/legal-risk` command as a direct entry point. The route map flips to **Built** (§3 option D, §6 Table B, §4a). The firewall is unchanged — flag, don't practice law. (Still future: auto-recommending the register for memoir/autofiction with identifiable real people *without* the explicit flag.)

### Onboarding — install decision-aid and glossary

The README install section now opens with a **Which install do I need?** table that maps each host (Antigravity, Codex, Claude Code CLI, Cowork) to its path and fastest route, so a newcomer doesn't have to read all five install flows to find theirs. A new **Key Terms** section defines the load-bearing vocabulary a first-timer meets cold — contract, controlling idea, the Firewall, pass, macro block, audit, genre module, editorial letter, the Must/Should/Could severity tiers (and the Deficit Lock), spine, and reverse outline.

### Onboarding — visual surfaces brought current

The README now opens with a **See It in Action** section linking the rendered sample editorial letters, the targeted-audit and pre-writing samples, and the two interactive maps (overview dashboard, route explorer) so newcomers can see real output before installing, plus a **Your First Five Minutes** walkthrough.

The `overview-dashboard.html` and `route-explorer.html` visuals (and their `.codex.html` twins) were stale at a v1.0.2 snapshot and have been brought current: the route explorer no longer reports shipped workflows (Fragment Synthesis, partial-manuscript mode, Submission Readiness, Submission Triage, Feedback Triage, the Nonfiction Argument Engine, editor scaffolding, diagnostic vocabulary, Series Continuity) as "not yet built"; the Legal Risk Register is shown as built-but-not-yet-routed; only multi-party/team intake remains a true gap. The overview dashboard now shows the canonical 8-block macro map (Emotional Dynamics restored as its own block), the full 50 spines / 12 families (adding Kishōtenketsu and Jo-ha-kyū), and the current version. The dashboard's click-to-expand cards are now keyboard-operable (`role="button"`, `tabindex`, Enter/Space handlers).

### Onboarding — overview dashboard front door

The overview dashboard header now opens with a "New here?" getting-started callout — a one-line plain-language orientation ("this page is a map; you don't need to memorize it") plus the first action (`/start`) — so a brand-new user landing on the page sees what to do before scrolling into the technical sections. Additive only (one `<div>` + two CSS rules; no redesign, no new sections, no network/deps). Applied to both the canonical `overview-dashboard.html` and its authored `.codex.html` twin (which keeps the `apodictic-start` wrapper naming per the codex override convention).

### Validators — post-merge review nits

Three small fixes from a review of the merged batch (no new validators; count unchanged at 38→40 baseline):

- **`reader-instrument` B3 (fabrication smell-test).** The "unsourced question" advisory was gated on the Ledger *having* `### Unresolved Questions` bullets, so an `unresolved-question` reader-question with an invented `source_note` passed unflagged when the Ledger had **none** (the more suspicious case — citing a UQ that can't exist). The advisory now also fires when the Ledger has zero UQ bullets. Stays a WARN: UQ provenance is non-referential by design, so this is a fabrication smell-test, not a hard gate.
- **`manuscript-viz` render gate (false pacing curve).** `W2 scene order` is advisory, but a reordered manifest draws a *false* pacing curve — the one warning that corrupts the render's core output. The `render` subcommand now refuses on a scene-order divergence too (not just ERROR-level gate failures), overridable with `--force`; `W1 coverage` stays advisory so a legitimate partial map still renders.
- **Swarm cost copy.** The intake-router execution-mode menu rows (B/C/I) said a bare "roughly 5x" while `run-core.md` notes the 2026-06 re-test measured ~8.5×+ on long fiction — understating cost at the decision point. The menu rows now carry the measured figure.

### Validators — manuscript-viz E5 + check-mirror hardening

Follow-ups from an independent post-merge review of the Horizon-Tier-1 validator train. **manuscript-viz** gains **E5 (no duplicate entry)**: a `scenes[].scene_id` or `findings[].id` repeated in the manifest is now an ERROR — a duplicate double-draws a pacing bar / double-counts a chapter's severity bar (a chart element showing a value the sources did not contain), which the per-id E2/E4 checks pass on. **check-mirror** now flags a `CM_ROOT_ONLY` utility (e.g. `sync_setec.py`) that has **strayed to the plugin side** or diverged across both copies, instead of skipping it by name in every mode (it was only ever meant to excuse a *root-only* file). `viz_manifest.py render`'s usage + refusal now state that the Timeline and Ledger are required for a gated render (with `--force` as the manifest-only escape) and name any missing source. Docs trued up: the manuscript-visualizations and mirror-parity specs + ROADMAP Horizon item 1 flipped from "Proposed/Spec" to built (manuscript-viz Increment 1 = charts 1–3; the network/heatmap/timeline/beat-map charts remain future); the `reader-instrument` module docstring now lists its two B3 advisories and the advisory summary reads B3/B4/B5/W1. No validator-count change; no schema change.

### Routing — fork/overlay split + project addressability (Increments 1–4)

The intake router now distinguishes **forks** (modifiers that *select* a workflow — `time` → Submission Triage, `nonfiction` → the argument / narrative / memoir engines, `feedback`, `team`) from **overlays** (modifiers that only *modify* a selected run — `ai`, `editor`, `facilitator`, `risk`, `hybrid`, `swarm`). The §6 route map splits into a base-route table (Table A) plus an orthogonal overlay table (Table B), removing nine `base × overlay` rows and giving each overlay a single authoritative status; the router output contract becomes `base_route` + typed `forks{}` + composable `overlays[]` (the bespoke `nonfiction_route` folds into `forks.engine`). Projects are now **addressable**: a workspace-relative `.apodictic/registry.json` (`apodictic.project_registry.v1`) makes each book selectable by name, with `/start <project>` binding a session to its state and a new `/projects` command listing/rebuilding/tidying the registry — each project's `Diagnostic_State.meta.json` sidecar stays canonical, the registry is a rebuildable cache. `/new-project` registers on creation; pre-writing projects drop a minimal sidecar (`next_action: pre_writing`) so they register before any diagnostic run. **State-driven dispatch (Increment 3):** for a bound project, `/start` derives a **lifecycle node** from the sidecar by a single total precedence (`cold → blocked_gate → execution → pre_writing → submission → revising → diagnosed → diagnosing`) and dispatches via `next_action` — collapsing the intake questions to a two-option Resume/Start-fresh prompt (cold start runs the full questionnaire unchanged), behind a scoped contract-hash precondition. The §6 route map gains a lifecycle transition table, with the Artifact×Goal table reframed as the cold-start entry map. **Revision-loop spine (Increment 4b):** at the `revising` node the coach answers "what now?" with a leverage ladder (`revision-coach/SKILL.md` §Loop Dispatch) — reading the finding lifecycle (`locked`/`delivered`/`revised`) and the revision report's resolved markers to propose the next highest-leverage action, with a stalled-revision off-ramp. **Increment 4a** then makes the runner-governed gate engine the fold-consistent writer of `revised`: a gated `revision_round` phase advances **only the resolved subset** of findings (the report's `<!-- resolved: F-… -->` ids) to `revised`, with the revision round's pre-existing direct sidecar write *scoped* to non-governed projects so `gate --check-state`'s `pointer == fold` invariant holds. Design: `docs/router-fork-overlay-split.md`, `docs/project-addressability.md`, `docs/revision-round-gate.md`.

### Onboarding — project dashboard (snapshot viewer)

A new `plugins/apodictic/project-dashboard.html` — a self-contained, sandbox-safe **snapshot** view of your projects: select/filter by lifecycle node, see where each stands ("what now?"), and get the `/start <project>` launch command per project. It renders an `apodictic.project_registry.v1` payload (with the node + next action pre-computed by the tool and embedded), so it is render-only — a viewer and launch-pad, not a live monitor or controller. Complements `/projects` (text) with an at-a-glance visual, in the style of the existing route-explorer / overview dashboards.

### Commands — Capability Index

New **`/apodictic`** command: a non-interactive capability index for discoverability. APODICTIC had 15 slash commands and 5 skills but no flat "what can I do / where do I start / what's my current state" reference — `/start` is an interactive *router*, not an index, and the README's command list had drifted (missing 4 of 15). `/apodictic` prints a curated, scannable index: the Firewall in plain language, every command grouped by workflow stage (Start → Pre-writing → Diagnose → Revise → Risk/Submit → Projects) with a one-line "when to use," how to find your current project state (the registry + lifecycle rail), and pointers to the existing HTML maps. It never routes (that's `/start`) and never writes state. Named `/apodictic` to avoid colliding with Claude Code's built-in `/help`. Drift-resistant by design: before printing it globs `commands/*.md` and appends any command not yet in the index, so additions self-heal (only grouping needs a human). Ships as a command file only (no registry entry, per the existing `/projects`/`/legal-risk` precedent); host-neutral wording so the codex/antigravity generators pass.

### Tooling / DX

Single-sourced the self-testable validator **count**. It was hard-coded as the literal "40" in five places (`validate.sh` ×4 + a `ci.yml` comment); every validator-adding PR had to hand-edit all five, which repeatedly produced merge conflicts when concurrent PRs each bumped the number independently (and a stale denominator would fail `--self-test-all`). Now `AGG_VALIDATORS` is hoisted to a single top-level constant with a derived `AGG_COUNT=$(set -- $AGG_VALIDATORS; echo $#)`, and every displayed count (`--self-test-all` header + `PASS/FAIL (N/N)` tally + the usage banner) reads from it; the `ci.yml` comment is de-numbered. A PR adding a validator now edits only the `AGG_VALIDATORS` line — the count can no longer go stale or collide. No behavior change; mirrored byte-identical across both `validate.sh` copies (`check-mirror` green).

### QoL — inventory-parity sync-marker check

New meta-check `scripts/check-inventory-parity.mjs` (stdlib Node only) guards that the display surfaces (`overview-dashboard.html`, `AUDIT_SELECTION_MATRIX.md`) stay synced with the canonical audit/research inventory — the rot PR #81 hand-fixed. It computes a `<count>:<short-hash>` signature for the signal-emitting audit registry (between the `registry:signal-emitting-audits` markers in `audit-routing-table.md`) and the research modes (`commands/research.md`), and flags any opted-in surface whose embedded `<!-- inventory-synced: audits=… research=… -->` marker drifts from current (exit 1). This is the #79 status-drift pattern applied to inventory: a sync-marker + changed-since signal — robust, near-zero false positives, and no brittle name-by-name matching. **Honest limitation:** like #79's status flip, it verifies the *signal is consistent*, not that the surface content is actually correct — a maintainer who bumps the marker without re-syncing defeats it; that's a transparent trade vs. brittle name-matching, and strictly better than nothing. Vacuity-guarded (zero markers → error), fence-aware (markers inside ``` / ~~~ are ignored), malformed-marker-loud, and `--self-test` covers the 7 hermetic cases plus an integrity check proving the negatives fail only because the compare is real. Both surfaces seeded with the current signature; wired into CI. No validator-count bump.

### Docs — Marketing-parity refresh

Brought the plugin's self-description in line with what it ships at v2.3.1. Registered the 5 previously-unlisted commands (`/apodictic`, `/projects`, `/legal-risk`, `/triage-feedback`, `/reader-questions`) in `release-registry.json`, so both READMEs' registry-generated command lists now fill in all 16 commands grouped correctly (`/apodictic` joins `/start` under "Start here:"). Added an `apodictic-index` wrapper-name special-case to the Codex and Antigravity generators so `/apodictic` no longer derives an awkward `apodictic-apodictic`. Refreshed the hand-maintained framing and capability prose in both READMEs (and the Codex twin): added persuasive/argument-shaped nonfiction (policy briefs, op-eds, testimony) to the tagline and Intended Audience, and surfaced the shipped capabilities — Legal Risk Register (flags, never adjudicates), Feedback Triage, Beta-Reader Instrument, manuscript-structure visualizations, the Nonfiction Argument Engine, project addressability/resume, Retcon Planning / State Cards, and the Diagnostic-Vocabulary & Editor-Scaffolding operator modes. Back-ported the revision-coach-aware post-diagnosis wording (removing the contradictory "work with Claude directly" line), qualified the privacy claim honestly (no telemetry of its own; diagnostic state persists on local disk by design; `/research` makes explicit web searches), and fixed the false CONTRIBUTING reason for the no-external-PR policy (solo-maintained + email-based, not "no PR infrastructure"). No diagnostic-behavior, schema, or validator change.

### Marketing-parity — visual + matrix surfaces refreshed; two codex twins de-duplicated

Brought the three onboarding surfaces up to v2.3.1 reality and removed two redundant Codex overrides so future edits stop being double-edits. `overview-dashboard.html` and `AUDIT_SELECTION_MATRIX.md` gained the audit/research inventory that had drifted out of date — the missing genre audits (**Supernatural Horror**, **Grimdark / Dark Fantasy**), **Narrative-Decision (StoryScope)**, **POV Voice Profile**, the advisory **Idiolect Preservation** / **Punctuation Cadence**, the **Compression** / **Stakes System** / **Decision Pressure** / **Reception Risk** craft chips, the **Adversarial Evidence Review** + **Argument Evidence / Persuasion / Red Team** companions, and the two missing research modes (**Citation Verifier**, **Field Reconnaissance** → all 6) — all re-derived from `core-editor/references/audit-routing-table.md` §Signal-Emitting Audit Registry and `commands/research.md`. The dashboard and matrix also document the shipped **Legal Risk Register** (`/legal-risk`, named on the Q3 sensitive-content branch), **Feedback Triage** (`/triage-feedback`), **Beta-Reader Instrument** (`/reader-questions`), project **resume** (`/start <id>`, `/projects`), and the **Nonfiction Argument** path. `route-explorer.html` (and its surviving Codex twin) picked up a version stamp, the projects/resume path, an execution-mode note (swarm = verification insurance for final submission prep; ~5x, measured up to ~8.5x on long fiction), and base/twin parity on the legal-risk route. Because `rewriteGeneratedDocs` already swaps `/cmd` → `apodictic-cmd` across `.md`/`.html`, the `overview-dashboard.codex.html` and `AUDIT_SELECTION_MATRIX.codex.md` overrides were byte-for-byte reproducible from the base + rewrite (proven empirically), so both were deleted along with their `release-registry.json` `codex.overrides` keys. Docs/HTML/matrix only — no diagnostic-behavior, schema, or validator change.

### Tooling / DX

New **status-drift lint** (`scripts/check-status-drift.mjs`, wired into CI): catches spec docs whose `**Status:**` line still says "unbuilt" after the deliverable shipped — drift that recurred across the #66/#70/#74 trains and invites duplicate builds (agents implement *from* specs). Opt-in by design to avoid crying wolf: a spec declares its deliverable in a `<!-- built-when: <path> -->` (or `… contains "<literal>"`) HTML-comment marker, and the lint flags a doc **only** when its marker's deliverable now exists *and* the Status line still reads unbuilt — un-marked docs are never flagged (zero false positives by construction; most "Proposed (unbuilt)" specs are *correctly* unbuilt). Standalone Node, stdlib-only (no validator-count bump, no dual-script-mirror burden — same class as `assemble-changelog`); fenced-code-immune; a conservative built-guard skips multi-increment statuses; 10-case hermetic `--self-test`. Seeded with markers on 11 specs (3 built → green, 8 future → the tripwires for the next build train) plus its own. Companion discipline in `AGENTS.md` § Review practices ("flip the status when you build"). Surfaced and fixed two live drifts while building — `docs/followups-batch-spec.md` and `docs/runner-governed-execution.md` increment 5 (structured gate-event records, shipped v2.1.0) both flipped to Built. (A third candidate — the ROADMAP "Framework Overview Dashboard" Backlog entry — is left for maintainer adjudication, since `overview-dashboard.html` exists but the entry may intend a redesign.) Detection only — the status flip stays a deliberate edit.

### Onboarding — router diagram in the README

The README now opens with a GitHub-rendered Mermaid flowchart of the `/start` router: the three intake questions (what you have → what you want → anything that changes how we work) routing every starting point to its workflow, with the Firewall shown as the one thing the tool never does — rewrite your prose. It renders inline on github.com and links out to the interactive route explorer, whose full-draft goal list now includes the Revision Coach path, for parity with `intake-router-runtime.md`.

### Audits — Argument-Decision (ArgScope) registered in the canonical inventory

Registered the `argument_decision_audit` SETEC consumer surface (adopted in #87) in the audit registry so it's discoverable like its `narrative_decision_audit` sibling — previously it lived only in the skill/reference/contract layer and was absent from the listing surfaces. Adds a Craft entry to `release-registry.json` (available audits 34 → 35; craft 16 → 17), which regenerates the `/audit` list, the README audit counts, and the plugin description; adds it to the signal-emitting audit registry (`audit-routing-table.md`); and re-syncs the inventory-parity surfaces (`AUDIT_SELECTION_MATRIX.md`, `overview-dashboard.html`) to the new signature `audits=43:1202e80a`.

### Release — self-contained, decoupled from the APODICTIC-Gemini sibling

apodictic's release flow no longer reaches into an APODICTIC-Gemini sibling checkout. The legacy **push** reach-ins are removed: `release.sh` no longer rsyncs `plugins/apodictic/` into the sibling's public mirror or runs `release-verify.mjs --check-sync` (steps 7–8 dropped; banners renumbered to 7 steps), `release-verify.mjs` drops the App.tsx "Based on APODICTIC plugin vX.Y.Z" version-parity arm, the `--check-sync` mirror-parity arm, and the `checkRsyncParity` helper, and `release-registry.json` drops the three Gemini-pointing path keys (`appTsx`, `landingPageTsx`, `geminiPublicPlugin`). The canonical, drift-gated **pull** chain is unchanged and remains the sole coupling: APODICTIC-Gemini's `sync-plugin.mjs` vendors apodictic's released tag + registry, `generate-ui.mjs` regenerates `App.tsx`/`LandingPage` from the vendored registry, and Gemini CI's weekly + dispatch drift gate (`generate:ui:check`) owns mirror/version parity. apodictic's release is now self-contained and builds entirely from its own `plugins/` tree with no sibling dependency.

### Docs / Samples

Refreshed the *Dungeon Crawler Carl* sample editorial letter (`sample-editorial-letter.html`) to the current framework version (v1.0.1 → v2.3.1, June 2026 run). Content revisions only — same template and styling: re-proportions the structural read (Floor 1 measured at ~52% of word count, not estimated ~60%; the genuine idle stretch relocated to the top of Floor 2), adds the Carl/Donut two-hander and the individuation-gate framing to "What the Book Does Best," reframes the callout around the satire going load-bearing twice (Death Watch + fighting-pit mercy), and reworks the "What Needs Work" items (Floor-2 re-tutorialization, the under-felt mass-death beat, Donut-as-prop at the climaxes, competence-outruns-change) with a matching revision checklist. No plugin behavior change.

### SETEC integration — adopt the ArgScope `argument_decision_audit` surface

APODICTIC now consumes SETEC Voiceprint's `argument_decision_audit` task surface
(ArgScope) — the argument-domain sibling of the narrative-decision (StoryScope)
audit. A new thin shim `ai_prose_argument_decision_audit.py` routes the surface
through SETEC's normalized dispatcher (R2) via `run_surface_cli`, like the other
`ai_prose_*` shims; the dispatcher enforces the per-surface version floor at
runtime (R3 `version_floor` on an out-of-floor SETEC), so the shim hardcodes no
version. The surface scores a public-debate / op-ed essay's argumentative
STRUCTURE — the B1 paragraph-role transition arc (support→proposal,
support→support, thesis-opening) + the B2 discourse-mode share — against Kim et
al. 2026's ("Argument Collapse", arXiv:2606.01736) human/LLM group means. It
measures argumentative *diversity*, not quality, soundness, or provenance, ships
`uncalibrated`, and is register-bound to public-debate forums (research / legal /
policy = the consumer's `distant` tier, structural-signals-only).

- **Bumped the vendored SETEC contract pin v1.114.0 → v1.116.0** (`setec-plugin.lock`,
  release pin to the tag carrying the surface). Re-synced the consumer-projected
  manifest (`tests/setec-contract/setec-capabilities.json`, now 13 apodictic
  surfaces incl. `argument_decision_audit` at floor 1.116.0) and the R5 contract
  fixtures via `scripts/sync_setec.py`. Per the script's documented design the
  manifest is consumer-projected while the golden fixtures are copied whole, so
  the bump also vendors the 1.115.0 voicewright-bundle goldens (binoculars /
  general_imposters / mimicry_cosplay / voice_fingerprint) as parser-test data.
- **New audit-level contract** `references/craft/argument-decision-audit.md` (v0.1):
  the envelope shape (4 contributions, B1/B2 bundles, heuristic `reused_signals`,
  the `pre_flag`), the 3-tier register map, the claim-license fields to surface,
  the aggregate posture (pin per-signal `contributions`, NOT the aggregate score),
  judge provenance, and the anti-verdict / framing note. It may PRE-FLAG whether a
  dialectical-clarity (soundness) run is informative; it never adjudicates
  soundness, warrant, or fairness.
- **Registered in the specialized-audits SKILL.md** (triggers, the surfaces table
  row, and the references list).
- **Offline contract test** (`tests/setec-contract/test_setec_contract.py`) now
  expects 10 shim surfaces and pins `argument_decision_audit`'s floor at 1.116.0;
  the drift gate re-derives the shim set, so the new shim joins automatically.
- Pins only the parts SETEC has committed (envelope shape, per-signal
  `contributions`, `claim_license`); the aggregate math, B3/B4 `reused_signals`
  (heuristic, no numeric anchor by design), and the deferred dynamic signals
  remain provisional under the surface's `handoff: experimental` posture.

### SETEC integration — R1 capabilities query + vendor/pin/drift-gate

APODICTIC now data-drives each SETEC surface's version floor from SETEC's
capabilities manifest (`capabilities.py emit --json`) instead of hardcoding it.
New `setec_capabilities.resolve_floor()` discovers SETEC at a single bootstrap
floor, queries the manifest, and asserts the discovered `setec_version` against
each surface's `min_setec_version`. The retired `MIN_SETEC_VERSION = (1, 86, 0)`
per-surface authority and the narrative-decision shim's `(1, 107, 0)` constant
are deleted; all nine `ai_prose_*` shims resolve their floor through the manifest.

Added a vendor/pin/drift-gate apparatus (ported from APODICTIC-Gemini's pull
pattern, in Python): a pinned copy of SETEC's consumer-projected manifest +
R5 contract fixtures under `tests/setec-contract/`, a `setec-plugin.lock` pin,
`scripts/sync_setec.py` (`--check`-able re-derivation), and a drift gate
(`tools/check_setec_contract.py`) whose self-consistency guard fails if any
shim surface is missing from the vendored manifest or lacks a floor. Wired into
CI plus a weekly `sync-setec` workflow. (Provisional pin against the unreleased
SETEC R1+R5 branch; finalization re-pins to the release tag.)

### SETEC integration — adopt the R2 normalized dispatcher + R3 structured errors

`setec_runner.run_supplement` now routes EVERY SETEC surface through SETEC's
normalized dispatcher (`setec_run.py <surface> [args] --json`, R2) and parses
the `schema_version` 1.0 envelope from **stdout** — including
`pov_voice_profile`, whose private file artifact the dispatcher projects to
stdout. One delivery path. The signature changed from a script filename to a
surface NAME: `run_supplement("variance_audit", args)`, not
`run_supplement("variance_audit.py", args)`.

- **Deleted from `run_supplement`:** the `json_out` parameter, the
  `_caller_json_out_path` helper, the `--json-out` injection + `--json-out=`
  /split-form recovery, the ephemeral `ai-prose-baselines-private/` tempdir +
  `rmtree`, and the `min_version` escape hatch. The dispatcher owns delivery
  and floor/dependency enforcement now.
- **R3 structured errors.** On `available: false`, `run_supplement` branches on
  the envelope's `reason_category` (not stderr scraping): `version_floor` /
  `missing_dependency` → blocking (surface the upgrade/install message);
  `text_too_short` → reliability (preserving the §6.4 reliability-vs-blocking
  semantics); `policy_refused` / `bad_input` / `internal_error` (and any
  unknown category) → blocking with the reason text. New `SupplementResult`
  fields `reason` / `reason_category` carry the structured error.
- **The 9 `ai_prose_*.py` shims are thinned** to a single
  `run_surface_cli(SURFACE, argv)` call (via the shared helper in
  `setec_runner`): they drop the per-shim `resolve_floor` runtime pre-check and
  the `pov` `json_out=True` special-case, route through the dispatcher, emit the
  envelope to stdout, and exit with the dispatcher's exit-code contract.
- **Floor reconciliation.** The dispatcher is the single RUNTIME authority for
  per-surface floor/dependency failures (it returns R3 `version_floor` /
  `missing_dependency`). `setec_capabilities.resolve_floor` + the vendored
  manifest are retained ONLY for the offline drift gate and capability
  introspection (Increment 2's contract role), not a redundant runtime
  pre-check that could drift from the dispatcher.
- **Bootstrap/dispatcher floor.** `run_supplement` fails cleanly with an
  upgrade message if the discovered SETEC predates the R2 dispatcher
  (`setec_run.py` absent) rather than crashing. A `# FINALIZATION:` marker in
  `setec_runner.py` flags raising `BOOTSTRAP_SETEC_VERSION` to the real R2
  release (target ~1.114) once SETEC cuts it.
- **Docs updated:** `run-full.md` Pass 3 + Pass 7 wiring (surface-name calls;
  Pass 7 multi-POV drops `json_out`; POV read keys corrected to the dispatcher's
  projected names `cross_pov_distances_weighted` / `pov_vs_corpus_mean` /
  `voice_collapse_verdict`); `narrative-decision-audit.md`; the contract test
  gains the dispatcher path (T2) + R3 tiering (T2b).

### Docs / Calibration

Ran the swarm-vs-single execution-mode eval as an **N=1 pilot** on one long-fiction fixture (*Dungeon Crawler Carl* Book 1, 130K words) and recorded it under `docs/swarm-vs-single-eval-pilot/` (pre-registration, blind ground-truth key, label-blind scoring, comparison report). Directional, not a verdict. On that fixture single-agent tied-or-edged swarm on real-issue recall (0.50 vs 0.44, noise-level) at ~8.5× less token cost; swarm bought tighter severity calibration (3/4 vs 3/6 band-clean on the caught-and-banded set) and more full-credit catches, not more recall, and both correctly returned zero Must-Fix on the near-sound control. Per the pre-registered rule this is a "verification-insurance / single-default (cost-adjusted)" outcome — matching the existing §2b default. Applied the pilot's recommended cheap deliverable: `run-core.md` §Execution Mode (which carries the `last re-validated: 2026-06` provenance note), the intake-router swarm menu rows, `core-editor/SKILL.md`, and both READMEs now keep swarm but reframe its everyday rationale from "deeper analysis / ~2× findings" to **verification isolation for final submission prep**. The historical changelog entry for the original swarm A/B claim is left intact as a record. No validator or routing-logic change (the user-facing §2b execution-mode menu copy is reworded).

### Validators

37 → 38 self-testable validators. Added `check-mirror`, a QoL gate that mechanizes the dual-script-mirror invariant (`AGENTS.md` § Platform parity): `validate.sh`, `preflight.sh`, and every `*.py` exist in two committed copies — root `scripts/` (what CI runs) and `plugins/apodictic/scripts/` (canonical) — that must be byte-identical by hand, or a validator change passes against one copy while CI runs the stale other blind. `check-mirror` asserts the shared mirrored set matches (root-only build/release scripts, plus root-only `*.py` infra utilities listed in `CM_ROOT_ONLY` — e.g. `sync_setec.py` — and the plugin-only `test_fixtures/` correctly excluded; schemas are single-sourced) and is wired into `--check-all`, so drift is now CI-blocking instead of a silent footgun. Detection only — it never auto-syncs; the by-hand `cp` stays deliberate. Pure shell (no `python3` dependency).

### Workflows — Manuscript-Structure Visualizations

New **Manuscript-Structure Visualizations** capability (Horizon Tier 1): a presentation layer that adds *no analysis* — a deterministic render of data the passes already produced. An `apodictic.viz_manifest.v1` block copies, **verbatim**, the Timeline Event-Ledger rows (scenes) and `apodictic.finding.v1` blocks (findings); the new render-only SVG layer (`scripts/viz_manifest.py render`) draws charts 1–3 — pacing/word-count curve, POV time-share, finding-severity-by-chapter (chapters sorted numerically, Ch 2 before Ch 10) — into a single self-contained offline HTML (no network, no deps, no telemetry). The `manuscript-viz` validator owns manifest↔source provenance: **E1** schema + a *no-visual-style* field allowlist (style is the renderer's, not the run's; a present-but-unparseable block is an E1 failure, not a silent no-op, and `--require-block` fails an absent one — the `--check-all` gate uses it so it can't pass vacuously), **E2** provenance closure (scene_id → Timeline row; finding id → ledger; finding `chapter` == the conservative `Chapter N`/`Ch N` `evidence_refs` parse, else the literal `unplaced` — no guessed placement), **E3** every body Must-Fix appears, **E4** byte-equal copy fidelity (the manifest copied, it did not compute), **W1** coverage, and **W2** scene order (scenes[] must follow the Timeline's document order, since the pacing curve's x-axis is scene order). `render` runs the gate first and refuses on an ERROR (`--force` to override). Firewall-safe by construction: render-only, provenance-closed, severity encoding hardcoded so a Must-Fix can't be recolored and a LOW-confidence Must-Fix is never shrunk. Reuses `timeline_checks._parse_event_ledger` (the Timeline column parser) and the shared block/schema engine; the subset engine can't validate arrays-of-objects or reject extra fields, so the nested-object validation + no-style allowlist live in Python. Backed by a worked-example manifest paired with the existing `example-timeline.md` + `example-findings-ledger.md`, gated by `validate.sh --check-all`. Mirrored into the root `scripts/` harness CI runs. Spec: `docs/manuscript-visualizations.md`.

### Workflows — Beta-Reader Instrument Generation

New **Beta-Reader Instrument** mode in the revision-coach skill (`/reader-questions`), the **upstream complement to Feedback Triage**: it turns the diagnosis's *own* open uncertainties — `LOW`/`UNCERTAIN` findings, the Findings Ledger's `### Unresolved Questions`, and `risk_if_fixed` tradeoffs — into a targeted, non-leading reader questionnaire, so the feedback that comes back is worth triaging. Closes the reader loop end to end: diagnose → ask the right questions → collect → triage → revise. Each question is an `apodictic.reader_question.v1` block; the new `reader-instrument` validator (`scripts/reader_instrument.py`) owns the question-contract — B1 schema, B2 unique ids, **B3 provenance integrity** (a finding-sourced question's `targets` resolves to a real ledger finding, with an advisory flag when a `low-confidence-finding` probe points at a non-LOW finding; an unresolved-question carries a `source_note` matching a real Unresolved-Questions bullet, and no targets), **B4 leading/invented-content firewall** (a sound finite blocklist of leading constructions + a coarse content-neutrality heuristic; advisory, ERROR under `--strict`, overridable), **B5 anti-relitigation** (never poll readers on a *locked* verdict — severity ∈ {Must-Fix, Should-Fix} and confidence ∈ {HIGH, MEDIUM} — overridable for "how to fix"), and W1 coverage. The severity-honesty boundary is the point: it tests uncertainty, never certainty. Backed by a new worked example + paired uncertainty-fixture ledger, gated by `validate.sh --check-all`. Mirrored into the root `scripts/` harness CI runs. Spec: `docs/beta-reader-instrument.md`.

### Validators

35 → 37 self-testable validators. Added `registry-check` (project-registry integrity over a workspace-relative `.apodictic/registry.json`: R1 envelope + per-entry schema, R2 root + sidecar resolution, R3 cache-vs-sidecar drift with the sidecar canonical, R4 duplicate id), backed by the new `apodictic.project_registry.v1` + `apodictic.project_entry.v1` schemas; and `lifecycle-node` (derives a bound project's lifecycle node from its sidecar by a single total first-match precedence — the tested primitive state-driven dispatch reads from). Both mirrored into the root `scripts/` harness that CI runs.

## v2.3.1 - 2026-06-07

### Tooling — decoupled web-app UI generation

`release-generate.mjs` no longer reaches into the private APODICTIC-Gemini sibling
to write its `App.tsx` / `LandingPage.tsx`. That generation now lives in the app,
which **pulls** this repo's `release-registry.json` (vendored alongside the plugin)
and runs its own generator. apodictic's generator produces only its own docs;
removed the now-dead TS-emit helpers (−175 lines). Fixes the silent drift that
occurred whenever the sibling wasn't checked out during a release.

### Distribution & changelog tooling

The generated `codex/` and `antigravity/` workspaces are **no longer committed** to
the repo. They are built from the canonical `plugins/` source and published as
**release assets** by a new `.github/workflows/release.yml` (triggered on `v*`
tags): `apodictic-codex-marketplace.zip`, the new `apodictic-antigravity.zip`, and
`apodictic.plugin`. Install is now download-and-open — no clone, no Node — with
build-from-source still available. This removes the ×3 parity-churn multiplier
that every release-touching change otherwise paid. (Decision: GitHub #52, Option B.)

`release-verify.mjs` and CI now `--self-check` the host builds (regenerate in a temp
dir and validate internal consistency) instead of diffing against committed trees,
and CI gained generator/parity gates (`release-generate --check`, both build
`--self-check`s, `assemble-changelog --check`).

The changelog moves to a **`changelog.d/` fragment directory** at the repo root:
each change drops one `### `-headed fragment instead of editing the shared
changelog, and `scripts/assemble-changelog.mjs` cuts them into a dated section at
release time (wired into `release.sh` after the version bump). (GitHub #51.)

### Registry — research modes 4 → 6

`release-registry.json`'s `researchModes` array was missing two of the six modes it
claims in `counts.researchModes` and lists in `commands/research.md`: **Citation
Verification** (`citation-verifier`) and **Field Reconnaissance** (`field-recon`).
Added both (their backing reference docs already shipped), so the array matches the
count and the registry-derived web-app UI surfaces all six research modes.

## v2.3.0 - 2026-06-07

A revision-planning track, two new workflows, a thesis-driven pre-draft pathway, and mid-run de-escalation — all additive on top of v2.2.0, no command/API break. **23 → 35 self-testable validators** (5 new + self-test coverage for 7 pre-existing pure-utility validators).

### Workflows — Retcon Planning (revision-coaching track)

A post-diagnostic, returning-author track in the revision-coach skill (reached via `/coach`, Retcon Planning mode) for writers who *discover* a late structural decision — a new ending, a reframed controlling idea, a relocated reveal — and must account for the **setup debt** it incurs against the earlier draft. Two doors into one machine: Door B (latent reinterpretation governed by a **commitment budget** — observed canon fixed > exposed consequences costly > unused latent cheap; **dramatic** retcon improves meaning, **evidential** retcon destroys fair play) and Door A (run reveal-economy *backward*, payoff → required setup). Strictly the **planning** half (the Firewall): the model produces a retcon plan — where setup must go, what it would cost, what it must not break — and the author writes the connective tissue; it never inserts foreshadowing or drafts a recontextualizing beat. Increment 1 + **F1** ranked Door-B abduction (the Selection step), **F2** the State Card as a standalone cross-revision rolling artifact, **F3** Reveal-Economy (Pass 8) source provenance. New `retcon-plan` and `state-card-diff` validators. Design: [`docs/retcon-planning.md`](../../../docs/retcon-planning.md).

### Workflows — Legal Risk Register

A core-editor content-analysis register for memoir, autofiction, and nonfiction that portrays **identifiable real people**: flags **defamation**, **privacy / disclosure**, and **rights-clearance** exposure with a severity and an escalation trigger, in a `[Project]_Legal_Risk_Register_[runlabel].md` artifact of `apodictic.legal_risk.v1` blocks. Firewall — **flag, don't practice law**: it names the *exposure* and the *trigger* and routes high-severity items to counsel; it never adjudicates ("not defamatory," "fair use," "no liability"). Two checks mechanize it — a required not-a-lawyer disclaimer (`legal-risk` L3) and **legal-advice drift** detection when a concern/disposition reads like a legal conclusion (W1); a companion `scene-ethics` validator covers consent/depiction handling (pending consent treated as unresolved for as-is depictions). New `legal-risk` and `scene-ethics` validators. Design: [`docs/legal-risk-register.md`](../../../docs/legal-risk-register.md).

### Workflows — Nonfiction Pre-Draft Pathway

A thesis-driven pre-writing track (pre-writing-pathway skill) for argument-shaped writers: plan the **spine** of the argument before a draft exists and **seed the shared `Argument_State.md`** so the Nonfiction Argument Engine (Dialectical Clarity + companions) consumes one contract instead of rebuilding the argument once a draft arrives. Increment 1 (argument spine — thesis, claim ladder, strongest opposing view), 2 (source/evidence map, seeds §3), 3 (warrant pre-check, seeds §4), 4 (scene-ethics plan). Inherits the pre-writing Firewall: structures the writer's argument through questions; never invents claims, fabricates evidence, or writes prose. New `argument-spine` validator. Design: [`docs/nonfiction-pre-draft.md`](../../../docs/nonfiction-pre-draft.md).

### Infrastructure — Adaptive Mid-Run Mode Escalation: de-escalation

Closes the roadmap open question left by the v2.2.0 escalation check: `escalation-check` now also **de-escalates** (expensive → cheap mode) when Tier 1 reveals the manuscript is simpler than the preflight estimate, saving Tier-2 tokens on an over-provisioned mode. Strictly conservative — the "clearly simple" band (POV ≤ 2, linear, belief ≤ 2, orientation ≤ 1, Tier-1 findings ≤ 8) sits below the escalation thresholds with a neutral no-thrash zone, a single absent/malformed signal blocks de-escalation, and it never drops below `sequential` (the salience floor). The asymmetry is deliberate: wrongly de-escalating a complex manuscript risks cross-pass anchoring, worse than wasted tokens. Advisory by default; `--strict` exits non-zero (symmetric with escalation). Extends `escalation-check` (no new validator). Design: [`docs/adaptive-mode-escalation.md`](../../../docs/adaptive-mode-escalation.md).

### Validators

23 → **35** self-testable validators. Five new — `retcon-plan`, `state-card-diff`, `legal-risk`, `scene-ethics`, `argument-spine` — plus self-test coverage closing the long-standing gap for seven pre-existing pure-utility validators (`contract-hash`, `contract-check`, `ledger-check`, `artifact-names`, `synthesis-sections`, `tone-check`, `state-lines`). `--check-all` extended to gate the run-folder and letter/ledger validator families against canonical fixtures. `validate.sh --self-test-all`: **35/35**; `--check-all` and `release-verify` green; `codex/` + `antigravity/` mirrors regenerated.

### Planning — Horizon Capacities scan

A roadmap scan of unplanned capabilities with reviewed design specs for the viable candidates (Manuscript-Structure Visualizations, Annotated-Manuscript Deliverable, Beta-Reader Instrument Generation, Promise-Contract Fidelity, Reader-Persona Simulation, Draft-over-Draft Structural Regression, Auto-Derived Continuity Bible, Content-Advisory Derivation, Cross-Manuscript Author Voice Fingerprint, Uncertainty-Resolution Intake Interview) plus one reviewed-and-declined (Positioning-Risk Lens). **Design specs only — none built this release**; see `ROADMAP.md` → Horizon Capacities and `docs/`.

### Repository

Workflow standardization kit (AGENTS.md, CI workflow running `validate.sh --check-all`, issue + PR templates) and an Argument Benchmark ground-truth corpus expansion (round 2).

## v2.2.0 - 2026-06-03

Operator modes, a returning-author workflow, mid-run infrastructure, and finding-lifecycle revision follow-through — all additive on top of v2.1.0, no command/API break. **19 → 23 self-testable validators.**

### Operators — Editor Scaffolding (`operator:editor`) + Diagnostic Vocabulary (`operator:facilitator`)

Two output-presentation operator modes close the two long-standing intake-router operator gaps.

**Editor Scaffolding** re-aims the Core DE editorial letter at a human developmental editor using APODICTIC as analytical assist. A superset overlay on the standard letter — every mandatory section is preserved, so `decision-layer-check` / `severity-floor` / `softness-check` / `finding-trace` still apply — adding an **Editor Brief** addressee reorientation, a required **What You Might Have Missed** blind-spot section, and an **Intervention Menu (editor's discretion)** that defers the author-facing prescription to the human editor. Severity honesty and the Firewall are untouched. New `editor-scaffolding` validator (E1–E4 + advisory W1), conditional on a `<!-- mode: editor-scaffolding -->` marker, body-scoped, with modal + bare-imperative prescription detection; a canonical `--check-all` gate proves the overlay composes with the standard letter gates. Design: [`docs/editor-scaffolding.md`](../../../docs/editor-scaffolding.md).

**Diagnostic Vocabulary Mode** produces a `[Project]_Vocabulary_Guide_[runlabel].md` teaching aid for a writing-group facilitator — a Glossary of the structural concepts the diagnosis used (each grounded in a specific manuscript spot) plus Discussion Prompts framed as questions for the group. The author-facing letter keeps its full severity record; the Guide is a teaching companion, not a softer letter. New `diagnostic-vocabulary` validator (V0 marker-required-on-a-named-guide, V1–V4 + advisory W1), body-scoped and wrapped-markdown-aware; canonical `--check-all` gate. Design: [`docs/diagnostic-vocabulary.md`](../../../docs/diagnostic-vocabulary.md).

### Workflows — Feedback Triage (increment 1)

A returning-author workflow in the revision-coach skill: sort, validate, and prioritize external (beta-reader / critique-group) feedback before any revision time is spent. Each note is a real-JSON `apodictic.feedback_item.v1` block — an `assessment` truth axis (did our own analysis confirm it?) kept orthogonal to a `triage` disposition axis — in a `[Project]_Feedback_Triage_[runlabel].md` artifact. New `/triage-feedback` command and `feedback-triage` validator: E1 invalid item, E2 duplicate id, E3 dangling conflict, E4 self conflict, W1 unresolved contradiction (both sides still actionable), W2 act-on-unvalidated; `--strict` gates the warnings. Makes "conflict resolution when feedback contradicts itself" mechanically checkable. Design: [`docs/feedback-triage.md`](../../../docs/feedback-triage.md).

### Infrastructure — Adaptive Mid-Run Mode Escalation

A condition-triggered checkpoint after Tier 1 passes that compares revealed manuscript complexity against the preflight estimate and recommends escalating the execution mode before Tier 2 commits tokens. New `escalation-check` validator reads the Tier-1 finding count from the ledger and the complexity signals from the sidecar (POV count > 3; non-linear timeline; belief > 5 / orientation > 3; Tier-1 findings > 20); advisory by default, `--strict` halts on a recommendation. Integrated into `run-core.md` between Tier 1 and Tier 2. Every trigger is a count or boolean read from a named field, so it fires identically across models (the condition-triggered, not model-emergent, discipline). Type-hardened against model-authored sidecar shapes. Design: [`docs/adaptive-mode-escalation.md`](../../../docs/adaptive-mode-escalation.md).

### Finding Lifecycle IDs — revision follow-through & completion (increments 2–3)

`finding-trace` extends from cross-artifact referential integrity (increment 1, v2.1.0) into the revision loop: **E4** a revision-plan / coaching artifact cites an `F-…` ID not in the ledger; **W2** a Must-Fix ledger ID not referenced in any revision plan; **E5** a completed-revision artifact mentions a `revised` finding without an explicit `<!-- resolved: F-… -->` marker; **W3** completion coverage. Completion keys on the explicit `resolved` marker (not on any `F-…` token in prose) and is scoped to the current revision report, so earlier-round resolutions are left alone. Closes FLI increment 2 (revision-plan follow-through) + increment 3 (revision-completion lifecycle) and the canonical `--check-all` gating of the example ledger↔letter pair in both directions; increment 4 (external host orchestrator) remains future. Design: [`docs/finding-lifecycle-ids.md`](../../../docs/finding-lifecycle-ids.md).

### Validators

19 → **23** self-testable validators. Added since v2.1.0: `escalation-check`, `feedback-triage`, `editor-scaffolding`, `diagnostic-vocabulary` (the Finding-Lifecycle work extends the existing `finding-trace` rather than adding a validator). `validate.sh --self-test-all`: **23/23**; `--check-all` (real-file invariants, including the new canonical scaffolded-letter and Vocabulary-Guide gates) and `release-verify` green; `codex/` + `antigravity/` mirrors regenerated.

## v2.1.0 - 2026-06-03

Harness Engineering: the prompt-governed → runner-governed step lands, plus cross-artifact finding-lifecycle auditing and the Argument Benchmark ground-truth gate. Additive throughout — no command/API change. **14 → 19 self-testable validators.**

### Runner-Governed Execution — cooperative gate engine (increments 1–3)

Execution gates move out of scattered prose into one declarative manifest, `schemas/execution-gates.v1.json`, consolidated behind a single command the model must pass: **`validate.sh gate <phase> <run_folder>`** (`scripts/run_gate.py`). The manifest names each phase's required artifacts, mechanical checks (validator + target artifacts), and the contract/judgment **attested** preconditions the gate prints as a required checklist — so the gate can't silently narrow the pre-synthesis / pre-delivery gates to their mechanical subset. The two load-bearing gates are `run_synthesis` (pre-synthesis lock) and `run_spot_check` (consolidated letter-delivery, subsuming the scattered Step 10/12/13 checks). Results record into the `Diagnostic_State.meta.json` `execution` block; `/start` resumes from it. A passing gate advances each ledger finding's **lifecycle state** (`locked` → `delivered`), keyed by `apodictic.finding.v1.id`. Adds the `gate` validator; the shared schema engine `scripts/apodictic_artifacts.py` is exposed as the `artifacts-schema` self-test. Still cooperative (the model invokes the gate) — external host enforcement is a future increment. Design: [`docs/runner-governed-execution.md`](../../../docs/runner-governed-execution.md).

### Runner-Governed Execution — structured gate-event records (increment 5)

Replaces the lossy per-phase `execution.gates` map with an **append-only `execution.gate_events[]` log** (`apodictic.gate_event.v1`) as the canonical record of gate decisions; `phase` / `allowed_next` / `pending_gate` / `finding_states` become a recomputable **resume pointer (`== fold(gate_events)`)**, asserted by a new **`gate-state`** validator (`validate.sh gate-state` / `run_gate.py --check-state`). Properties hardened across review:

- **Attestation is part of a clean pass** — a `passed` clears a gate only if its `attested_items` cover its own `attested_contract` (snapshotted manifest IDs); the engine never auto-emits a clearing pass on mechanical success — `gate --attest` re-runs the checks (freshness) and records the clearing pass only if still clean. Manifest `attested` entries gain stable `{id, text}` IDs.
- **Durable history** — coverage is validated against each event's *recorded* contract, never the live manifest, so a later rename/retire can't retroactively un-clear history.
- **Safe migration** — upgrading a legacy sidecar seeds a grandfathered baseline in manifest phase order so the prior frontier survives; `migrated` is legal only as a contiguous prefix followed by real work (so it can't be reused as a clearing bypass), and `gate-state` tolerates malformed entries with a clean validation failure rather than a traceback.

Adds the `gate-state` validator. The lifecycle vocabulary, degrade-path event authoring, and `--strict` CI mode are in [`docs/runner-governed-execution.md`](../../../docs/runner-governed-execution.md) §Increment 5.

### Finding Lifecycle IDs — cross-artifact trace (increment 1)

New **`finding-trace`** validator (`validate.sh finding-trace <run_folder>`, `scripts/finding_trace.py`) audits the un-owned dimension of the Finding Lifecycle ID: cross-artifact **referential integrity + sidecar lifecycle coherence** — complementary to `structured-findings` (intra-ledger ID hygiene) and `softness-check` (severity fidelity, locked→delivered). E1 dangling letter/calibration reference (a cited `F-…` ID not in the ledger), E2 phantom `execution.finding_states` key, E3 invalid lifecycle state, W1 lifecycle coverage (advisory; ERROR under `--strict`). Graceful — each artifact optional, but a present-but-malformed sidecar is an error, not a silent skip. Design + ownership-boundary table: [`docs/finding-lifecycle-ids.md`](../../../docs/finding-lifecycle-ids.md).

### Argument Benchmark — ground-truth answer-key validator

New **`argument-groundtruth-check`** validator (`scripts/argument_groundtruth.py`): GT1–GT7 coverage, Dialectical-Clarity code-namespace resolution, GT2 locus↔code consistency, and GT7 Distinguish classification for the Argument Engine Benchmark answer keys; tuned against the registered corpus and run over it by `--check-all`. See [`docs/argument-benchmark-spec.md`](../../../docs/argument-benchmark-spec.md).

### Validators

14 → **19** self-testable validators. Added since v2.0.0: `gate`, `gate-state`, `finding-trace`, `argument-groundtruth-check`, `artifacts-schema`. `validate.sh --self-test-all`: **19/19**; `--check-all` (real-file invariants) and `release-verify` green; `codex/` + `antigravity/` mirrors regenerated.

## v2.0.0 - 2026-06-01

A milestone release that hardens APODICTIC's editorial honesty and structural integrity, delivered as five sequenced phases. The strategy was **subtraction + honesty hardening, not added plumbing**: shrink the always-loaded instruction floor, normalize the severity vocabulary, make findings machine-checkable, and close the silent-softening leak — then fix the surrounding ops. The plugin's command/API surface is unchanged; the major bump headlines the behavior-changing honesty work (the Deficit Lock) and the severity-model normalization.

### Phase 1 — Subtract bookkeeping from the instruction floor

Moved filesystem/format/mode-mechanics bookkeeping out of the always-loaded judgment files into on-demand references (`output-structure.md`, `reference-index.md`, `audit-routing-table.md`, `execution-modes-reference.md`, `findings-ledger-format.md`), leaving one-line pointers. **Always-on instruction floor −9.5%** (32,132 → 29,078 words; `output-policy.md` alone −31%). A root `.gitattributes` marks `codex/**` and `antigravity/**` `linguist-generated` so the mechanical mirrors collapse in review.

### Phase 2 — Normalize severity (Canonical Severity Scale)

One canonical **Must-Fix / Should-Fix / Could-Fix** scale (`output-policy.md §Canonical Severity Scale`), with the orthogonal axes (confidence, prose tier, readiness bands, lens verdicts) named explicitly as *not* severity. Local audit scales propagate onto it via the `pass-dependencies.md §4e` table; a machine-readable **Signal-Emitting Audit Registry** (42 audits) in `audit-routing-table.md` is enforced by `validate.sh audit-signal-propagation --check-registry` (42/42).

### Phase 3 — Minimal structured state (real-JSON findings)

Replaced the YAML-ish structured-finding block with **real JSON** (`apodictic.finding.v1`) validated by a real parser, `scripts/structured_findings.py`. Synthesis-bound (Must-Fix/Should-Fix) Notable Findings must carry a block (enforced for ledgers). The `Diagnostic_State.meta.json` sidecar gains optional `findings[]` / `audit_triggers[]` / `readiness[]` arrays whose severities must tally to `triage_summary` (schema/array mismatch and missing-tally now fail). New `validate.sh structured-findings`, plus a `validate.sh --check-all` aggregate (self-tests + real-file invariants).

### Phase 4 — Harden honesty (Deficit Lock + Softness Gate) — behavior change

New **Deficit Lock** generation-order rule (`output-policy.md §Severity Honesty Protocol`): at Triage, severities lock as structured findings *before* any charity reframing; later steps may raise freely but may only lower with a body override marker (`<!-- override: softness-downgrade -->`) plus an Appendix B (Severity Calibration) entry. The charity hatches (Distinguish Protocol retroactive downgrade; the literary Beautiful-Emptiness / Quiet-Evasion exceptions; the Stillness classification) are gated so charity is legible, not silent. New `scripts/honesty_check.py` drives `validate.sh softness-check` (delivered-vs-locked severity, read from the Severity Calibration appendix with token-boundary evidence matching) and `deficit-lock` (every synthesis-bound finding is structurally locked). Validated by a mandatory before/after read on the frozen sample letters.

### Phase 5 — Plumbing

`academic_apis.py` HTTP backoff with exponential retry honoring `Retry-After` for 429/5xx + transient errors (a rate-limit no longer masquerades as a ghost citation); transient `_error` payloads stay memory-only (never disk-persisted, so an outage isn't sticky across runs); retraction is derived from the single cached DOI lookup. Response-cache disk persistence engaged (`$APODICTIC_CACHE_DIR` or `.apodictic_run/cache`). The release pipeline (`release.sh`, `release-verify.mjs`, `release-generate.mjs`) skips-with-WARN the private `APODICTIC-Gemini` sibling steps when absent, decoupling the public release path; `release-verify` now runs `validate.sh --check-all` as part of the gate.

### Validators

11 → **14** self-testable validators (`structured-findings`, `softness-check`, `deficit-lock` added). `validate.sh --self-test-all`: 14/14. New `validate.sh --check-all` real-file gate (self-tests + registry-vs-§4e + structured-findings on the shipped templates).

## v1.11.0 - 2026-05-29

### Added — Narrative-Decision (StoryScope) audit: APODICTIC consumer integration of SETEC Surface 6

Integrates SETEC Voiceprint's sixth task surface — `narrative_decision_audit` — into APODICTIC as a new opt-in craft audit, **Narrative-Decision (StoryScope)**. Closes the consumer-side decisions in SETEC's 2026-05-28 handoff (StoryScope / narrative-decision integration; Russell et al. 2026 arXiv:2604.03136v4, SETEC PRs #128/#129/#130). The surface scores prose against the 30 core narrative-decision features (33 signals) across 10 NarraBench dimensions and 7 bundles — measuring how a story is *built* (themes, plot, sensory register, reader stance, time) rather than how its sentences are *phrased*. It is a structure-level complement to AI-Prose Calibration (texture) and a sibling to POV Voice Profile (voice); all three are SETEC-backed and answer distinct questions under distinct claim licenses.

**Audit count: 33 → 34 (craft 15 → 16).** Specialized audits 30 → 31. Source of truth is `release-registry.json` (Craft category + `counts.availableAudits` / `counts.specializedAudits`); derived count strings regenerate to 34/16 across the READMEs, plugin/marketplace manifests, and the `/audit` command list.

#### New files

- `plugins/apodictic/skills/specialized-audits/scripts/ai_prose_narrative_decision_audit.py` — SETEC subprocess shim → `narrative_decision_audit.py`. Forwards CLI args unchanged; enforces its own version floor **SETEC ≥ 1.107.0** (Surface 6's ship release, higher than the framework-wide 1.86.0 floor) by discovering with that floor and passing the validated location through, so an older SETEC fails with an upgrade message rather than a missing-script error.
- `plugins/apodictic/skills/specialized-audits/references/craft/narrative-decision-audit.md` — audit reference v0.1 (consumer-pinning contract): envelope/`results` shape, `claim_license` fields to surface, the interpretive procedure, required outputs, the rewrite-resistance framing note, and the anti-verdict discipline.

#### Consumer decisions (SETEC handoff open questions)

- **Which surfaces pinned.** Tier A.1 `narrative_decision_audit` pinned (with experimental-handoff awareness — only the committed envelope shape, `contributions`, and `claim_license` are pinned). Tier B vocabulary (`narrative_feature_schema` keys, 7 `BUNDLE_LABELS`, 10 `DIMENSION_LABELS`, `literature_anchored` status) adopted as shared cross-tool vocabulary. **Tier A.2 `narrative_polarity_audit` NOT pinned** — it is a non-envelope sidecar (no `schema_version`, not in the capabilities manifest); contract-stable consumption would require a separate SETEC request (envelope wrapping or manifest entry).
- **Aggregate posture.** Per-signal `contributions` is the load-bearing payload; APODICTIC does **not** pin verdicts to SETEC's aggregate `score` (unequal/unbounded per-signal influence; not the paper's XGBoost+SHAP statistic). If a single number is needed, APODICTIC computes a clip-to-[−1,1]-then-mean pool, labeled distinctly; SETEC's `aggregate.score` / `verdict_band` are surfaced as provenance only.
- **Judge provenance.** `judge_identity` and `prompt_fingerprint_sha256` consumed as informational provenance / cross-run parity; verdicts are not gated on a specific judge model.
- **Register discipline.** Long-form-fiction home register; `claim_license.length_range_words = [2000, 25000]`. Out-of-register targets surface `register_warnings` and the register caveat first and stop short of direction claims. No default polarity-check report ships (operator-supplied).
- **Replication scaffold.** Out of scope; APODICTIC pins the runtime surface + vocabulary only.

#### Registration & tier rationale (§4c Audit Tier Promotion Criteria)

Registered at **Recommend (opt-in)** in `pass-dependencies.md §4b`, not a higher tier. Principled non-promotion per §4c: criterion 1 fails by design — the surface ships `uncalibrated` and the claim_license forbids provenance verdicts, so the audit produces **no audit-internal Must-Fix floor and no hard gates**. §4e gains three provisional Narrative-Decision rows (Could-Fix per-signal; Should-Fix only on convergence with texture-level AI-Prose Calibration evidence; SETEC aggregate surfaced as provenance only). The `audit-tier-criterion` validator's Recommend-tier exemption applies; the `audit-signal-propagation` validator operates on editorial letters (runtime), not on this table.

#### Files

- `release-registry.json` — Craft category item `narrative-decision`; `counts.availableAudits` 33→34, `counts.specializedAudits` 30→31.
- `plugins/apodictic/skills/specialized-audits/SKILL.md` — description triggers (storyscope / narrative-decision / rewrite-resistant / structure-level ai); Craft Audits table row; Reference Files entry.
- `plugins/apodictic/skills/core-editor/references/pass-dependencies.md` — §4b Recommend-tier finding-trigger row; three §4e propagation rows + a Narrative-Decision §4e note.
- `plugins/apodictic/commands/audit.md` — `/audit` Craft list entry.
- READMEs (root + plugin + codex), `plugin.json` (root + canonical), `marketplace.json` (root + `.claude-plugin/`) — count strings 34/16.
- Generated Codex + Antigravity host workspaces regenerated from canonical.

#### Review-round hardening (PR #6)

SETEC-runner plumbing fixes surfaced during PR review, all in the same unreleased version:

- `setec_runner.run_supplement` gained a `min_version` parameter so the documented narrative-decision path enforces the 1.107.0 Surface 6 floor (discovery otherwise ran at the framework-wide 1.86.0 floor and failed "script not found" instead of giving the upgrade path). Backward-compatible (default `None`).
- `setec_discovery`'s install/upgrade message is now floor-aware (`_install_instructions(min_version)`); the narrative-decision shim's "requires 1.107.0" error no longer appends a stale "Minimum required version: 1.86.0" line. Module-level `INSTALL_INSTRUCTIONS` retained at the default floor for compatibility.
- `setec_runner.run_supplement` gained `json_out=True`, a file-based JSON strategy for SETEC surfaces (e.g. `pov_voice_profile.py`) that write the envelope via `--json-out <path>` rather than stdout `--json`. The runner writes into an ephemeral `ai-prose-baselines-private/` directory (SETEC's default-private output policy refuses voice-cloning outputs elsewhere short of the unsafe `--allow-public-output`), reads the envelope back, and removes the tree; caller-supplied `--json-out` paths are honored. `run-full.md` Pass 7 multi-POV wiring now calls `pov_voice_profile.py` with `json_out=True`. Scoped to `pov_voice_profile`; other surfaces keep stdout `--json` unchanged.

Release note: the Gemini-mirror steps of `release.sh` (App.tsx / LandingPage.tsx generation, public-plugin rsync) are maintainer-local and were not run in this environment; `release-generate.mjs` count regeneration for those external targets is pending a maintainer run.

## v1.8.5 - 2026-04-26

### Hygiene — disclosure-discipline fixes; re-release of v1.8.4 with sanitized fixture references

No behavior changes. v1.8.5 ships v1.8.4 with two post-release hygiene commits folded in:

- **Fixture references in framework files replaced with abstract IDs (F1/F2/F3/F4)** — specific fixture identifiers had leaked into ~96 lines across 21 framework file copies (changelog entries, audit reference frontmatter, validator inline comments, ROADMAP). Sanitized to abstract IDs with generic genre tags (fiction-novella / short-fiction / argument-shaped nonfiction). Substitution applied across canonical + codex + antigravity trees.
- **Per-fixture manifest files gitignored via wildcard + allowlist pattern** — `evals/manifests/*.md` with `!evals/manifests/README.md` and `!evals/manifests/fixture-manifest-template.md`. Working copies preserved locally; index entries removed via `git rm --cached`. The .gitignore pattern itself does not enumerate the manifest filenames.
- **`.gitignore` reverted to explicit-filename pattern** for working notes (the `docs/.local/` hidden-directory pattern was reverted in favor of explicit gitignore entries with manuscript-discipline applied to filenames).

Validator suite unchanged at 11 (all self-test PASS via `validate.sh --self-test-all`). All 4 release checks PASS at parity with v1.8.4. Generated host workspaces sanitized in-place to match canonical (no behavior regen).

False-positive disambiguations preserved (left intact during sanitization):
- "Faustian Spine" plot type from Goethe (one of 39 plot types in framework taxonomy)
- Bibliographic citations to published authors with surname-only matches (left as-is)
- "Codex" as model identifier (vs. fixture binding)

#### Files

- `scripts/validate.sh` (canonical + repo-root + codex + antigravity copies): inline self-test fixture comments
- `plugins/apodictic/skills/core-editor/references/changelog.md` (3 trees): historical entries
- `plugins/apodictic/skills/specialized-audits/SKILL.md` (3 trees): Universal Audits verification block
- `plugins/apodictic/skills/specialized-audits/references/craft/{stakes-system,decision-pressure,scene-turn,research-citation-verifier,research-field-recon,adversarial-evidence-review}.md` (3 trees each)
- `plugins/apodictic/skills/core-editor/references/{pass-dependencies,output-policy}.md` (3 trees)
- `plugins/apodictic/skills/{pre-writing-pathway,core-editor}/SKILL.md` (3 trees)
- `plugins/apodictic/commands/new-project.md` (3 trees)
- `ROADMAP.md` (root)
- `docs/adversarial-evidence-level-setting.md` (root)
- `evals/manifests/*.md` (4 manifest files removed from index; working copies preserved)

## v1.8.4 - 2026-04-25

### Fixed — Phase 7 Codex final critique adjudication: audit-tier-criterion canonical-input closure + governance sharpening

Closes the Codex 5.5 final external review of Phase 7 work per `docs/.local/review-log/2026-04-25_phase-7-codex-final-critique.md`. One P1 + three P2s + three P3s adjudicated; full adjudication at `docs/.local/review-log/2026-04-25_codex-final-critique-adjudication.md`. Same failure-mode class as Joshua's earlier substantive code review caught for `audit-signal-propagation` (closed in v1.7.9): a validator passes its synthetic self-test but fails against the canonical framework file it was built to police. v1.8.4 closes the specific instance + adds ROADMAP item naming the class.

#### P1 — `audit-tier-criterion` canonical-input failure (5 audit-side fixes)

The v1.8.0 validator passed its 4-case synthetic self-test (PASS) but failed against canonical `pass-dependencies.md` (5 ERRORs: AI-Prose Calibration, Consent Complexity, Memoir & Creative Nonfiction, Narrative Nonfiction Craft, Series Continuity). Each audit was assigned to Auto-run or Auto-recommend before synthesis tier per §4a; each audit's reference file genuinely lacked the criterion-1 hard-gate / Must-Fix-floor language the §4c Audit Tier Promotion Criteria require for that tier. The validator's pattern matching was correct; the audit references needed updating.

Per-failure resolution — all five are audit-side fixes (no override markers; no validator pattern extension; no audit demotions):

| # | Audit | Tier | Fix |
|---|---|---|---|
| 1 | AI-Prose Calibration | Auto-run / Auto-rec-before-syn | §Readiness Impact Note retitled "Hard Gates / Must-Fix Floor"; per-condition (Hard Gate) labels added; explicit "Must-Fix floor" propagation language tied to the canonical Audit-Signal Propagation Rule. |
| 2 | Consent Complexity | Auto-rec-before-syn | New §Hard Gates — Must-Fix Floor block at top of §Detection Targets with four named gates (CC-Gate-1 Anti-Exploitation Floor, CC-Gate-2 Capacity-Bypass Floor, CC-Gate-3 Retcon Floor, CC-Gate-4 Perpetrator-Erasure Floor / CC-6). |
| 3 | Memoir & Creative Nonfiction | Auto-run | §Diagnostic Flags §Must-Fix Flags renamed §Must-Fix Floor — Hard Gates; per-flag (Hard Gate) labels added to Memory Fraud, Living Person Harm, No Transformation, False Precision; preamble names the audit-internal Must-Fix floor and propagation. |
| 4 | Narrative Nonfiction Craft | Auto-run | New §Hard Gates — Must-Fix Floor section after Step 8 with four named gates (NN-Gate-1 Source-Integration / Fact-Anchor — closing the previously-broken cross-reference from `pass-dependencies.md §4e`; NN-Gate-2 Attribution-Risk Convergence; NN-Gate-3 Composite/Identity Disclosure; NN-Gate-4 Lead-Contract Breach). Notes that Franklin remains the spine gate; the Hard Gates above are craft-layer gates that operate within a viable spine. |
| 5 | Series Continuity | Auto-run (when series flagged) | New §Hard Gates — Must-Fix Floor subsection in CS/RL channel block with four named gates (SC-Gate-1 Consequence-Erasure; SC-Gate-2 Silent-Retcon at explicit-canon layer; SC-Gate-3 Reader-Promise Failure; SC-Gate-4 High-Signal Thread Drop). |

Post-fix: `validate.sh audit-tier-criterion plugins/apodictic/skills/core-editor/references/pass-dependencies.md` PASSES with 0 errors / 0 warnings.

Validator self-test extended from 4 cases to 6 (analogous to Wave 2 B3 extension after canonical-fixture findings): added `autorun` (Auto-run definitional audit with §Hard Gates section header + per-flag (Hard Gate) markers — mirrors the canonical Memoir / Narrative-NF / Series Continuity pattern this v1.8.4 work surfaces) and `findingtrig` (§4b finding-triggered row without ref-path cell — confirms validator does not error on §4b's column form, since canonical §4b reference paths live in §4a). All 6 cases PASS. Validator total stays at 11.

#### P2 — `argument-recon-prerequisite` framing sharpening

Codex's correct read: the validator backstops argument-engine artifact runs against silent omission of Field Recon / disclosure; it does not detect argument-shaped runs from contract or intake. The execution-flow Pre-Pass Prerequisite Resolution step in `run-core.md` is the real router/intake verifier; the validator is the post-run backstop. v1.8.0 changelog framing ("Verifies argument-shaped runs satisfy the Field Reconnaissance prerequisite") was directionally true but technically over-broad. Honest framing: "verifies argument-engine runs did not silently omit Field Recon or disclosure." No code change required; validator behavior was correct.

#### P2 — B1 verdict-language sharpening (`docs/.local/review-log/2026-04-25_phase-7-wave-2-eval-coverage.md`)

Codex's correct read: "Confirmed load-bearing" is ablation-strength language; static analysis on existing canonical fixtures supports "evidence consistent with load-bearing" but not the stronger claim. v1.8.4 sharpens 18 occurrences of "Confirmed load-bearing" to "Static-analysis evidence consistent with load-bearing" throughout the eval-coverage doc; updates summary table verdict distribution; adds a v1.8.4 sharpening note at top of summary table; reworks highest-confidence-findings section to use ablation-honest language. The no-deletion outcome is unchanged: unexercised ≠ no effect, and observed in-output compliance is enough to keep instructions until ablation evidence proves removability.

#### P2 — Aggregate self-test dispatcher implemented

The E1 final report referred to an aggregate self-test command that did not exist (`validate.sh --self-test` exited "Unknown command"). v1.8.4 adds `validate.sh --self-test-all` (~30 lines): dispatcher iterates over the 11 self-testable validators, runs `--self-test` on each, reports per-validator PASS/FAIL, exits 0 only if every per-validator self-test exits 0. Closes the documentation-vs-implementation mismatch and simplifies CI / release workflows. Tested: 11/11 PASS.

#### P3 — ROADMAP additions

Three new entries under §Deferred (Out of Scope for This Cycle):

- **Canonical-framework validator runs as release gate.** Names the class of failure mode that produced both the v1.7.9 audit-signal-propagation case and the v1.8.4 audit-tier-criterion case. Currently release-check set covers self-tests + four mechanical generation/check pipelines; canonical-target validator runs are not gated. Adding a `release-canonical-checks.sh` orchestrator (or extending `release-verify.mjs`) would catch this class earlier. Estimated cost: ~50 lines + ~5 canonical invocations.
- **Clearer §4e table-driven propagation framing.** Pairs with the existing §4e context-modifier extension entry; if/when the §4e table is taken up for full source-of-truth parsing, the framing should be sharpened first.

The third recommendation (aggregate self-test dispatcher) was implementable inline and is shipped in v1.8.4 (see P2 above) rather than deferred.

#### v1.8.0 + v1.8.2 entries sharpened

- **v1.8.0:** `audit-tier-criterion` description extended with explicit honest correction noting the v1.8.0 self-test was insufficient against canonical input; closure cross-reference to v1.8.4 added. The capability-ceiling framing remains accurate; what was missing was the canonical-input check, now added in v1.8.4.
- **v1.8.2:** C1 framing sharpened from "cross-cutting rule dedup" to "cross-cutting rule canonical-home governance." Per Wave 3 report's own acknowledgment ("Net positive prose change for C1 rather than the typical compression negative: the canonical-home annotations themselves are the durable compression value"), the durable value is forward-looking drift prevention, not present-cycle compression. Title and opening sentence updated to match.

#### Files

- `plugins/apodictic/skills/specialized-audits/references/craft/ai-prose-calibration.md` — §Readiness Impact Note retitled + Hard Gate / Must-Fix floor labels (~+3 lines).
- `plugins/apodictic/skills/specialized-audits/references/tag/consent-complexity.md` — new §Hard Gates — Must-Fix Floor block in §Detection Targets (~+15 lines).
- `plugins/apodictic/skills/specialized-audits/references/genre/memoir-creative-nonfiction.md` — §Diagnostic Flags §Must-Fix Flags renamed + Hard Gate labels (~+4 lines).
- `plugins/apodictic/skills/specialized-audits/references/genre/narrative-nonfiction.md` — new §Hard Gates — Must-Fix Floor section (~+12 lines).
- `plugins/apodictic/skills/specialized-audits/references/craft/series-continuity.md` — new §Hard Gates — Must-Fix Floor subsection in CS/RL channel block (~+12 lines).
- `plugins/apodictic/scripts/validate.sh` — `audit-tier-criterion` self-test extended 4 → 6 cases (~+40 lines); new top-level `--self-test-all` aggregate dispatcher (~+30 lines). Net ~+70 lines.
- `scripts/validate.sh` — synced with plugin copy.
- `plugins/apodictic/skills/core-editor/references/changelog.md` — v1.8.4 entry; v1.8.0 + v1.8.2 sharpening notes.
- `ROADMAP.md` — two new entries under §Deferred (Out of Scope for This Cycle): canonical-framework validator runs as release gate; clearer §4e table-driven propagation framing.
- `docs/.local/review-log/2026-04-25_phase-7-wave-2-eval-coverage.md` — verdict-language sharpening (gitignored; sharpening matters for honest internal documentation).
- `docs/.local/review-log/2026-04-25_codex-final-critique-adjudication.md` — new adjudication entry (gitignored).
- `docs/.local/review-log/2026-04-25_phase-7-implementation-plan.md` — appended v1.8.4 Codex-critique adjudication subsection.
- Version bumped via `scripts/bump-version.sh 1.8.4`.
- Generated host workspaces (codex, antigravity) regenerated via release pipeline.

Total framework prose change: ~+46 lines across five audit reference files (Hard Gate / Must-Fix Floor language). Total validator change: ~+70 lines in `validate.sh` (extended self-test + aggregate dispatcher). All 11 validator self-tests PASS. `--self-test-all` aggregate dispatcher returns 11/11 PASS. Canonical-input check: `audit-tier-criterion` PASSES against `pass-dependencies.md` (0 errors / 0 warnings). All 4 release checks PASS.

#### Self-test verification (v1.8.4)

| Validator | Cases (was → now) | Status |
|---|---|---|
| `severity-floor` | 7 | PASS |
| `audit-signal-propagation` | 9 | PASS |
| `underdiagnosis-triggers` | 5 | PASS |
| `ledger-consolidation` | 5 | PASS |
| `decision-layer-check` | 12 | PASS |
| `quality-risk-triggers` | 12 | PASS |
| `timeline-diff` | 8 | PASS |
| `timeline-arithmetic` | 6 | PASS |
| `timeline-anchor-conflict` | 6 | PASS |
| `audit-tier-criterion` | 4 → 6 | PASS (+ NEW: canonical pass-dependencies.md PASS, 0/0) |
| `argument-recon-prerequisite` | 5 | PASS |
| `--self-test-all` aggregate | NEW | PASS (11/11) |

#### Methodology validation

This is the second instance in the model-capability review where bias-equalized parallel adjudication caught a Joshua-flagged failure mode (validator overclaiming). v1.7.9 closed the audit-signal-propagation case after Joshua's substantive code review; v1.8.4 closes the audit-tier-criterion case after Codex's final critique. The pattern is durable: validators that pass synthetic self-tests can fail canonical inputs, and the only reliable detector is running the validator against its real target. The new ROADMAP item (Canonical-framework validator runs as release gate) names the class explicitly.

#### Out of scope

- The class-level fix (canonical-framework validator runs as a release-check gate) is documented in ROADMAP but not implemented in v1.8.4; defer to a forcing-function-justified later cycle.
- §4e table-driven propagation framing sharpening is documented in ROADMAP and pairs with the existing §4e context-modifier extension entry.

---

## v1.8.3 - 2026-04-25

### Fixed — Phase 7 Wave 4: antigravity plugin.json JSON-corruption bug; defensive JSON-parse check added

Closes Phase 7 Wave 4 of the model-capability review per `docs/review-log/2026-04-25_phase-7-implementation-plan.md` §Wave 4. Wave 4 is closing-gate work: D2 host parity sweep + D3 Phase 7 done-gate verification. The parity sweep surfaced one critical drift item beyond what the mechanical `--check` calls catch — fixed in this release.

#### D2 host parity sweep — finding

`antigravity/plugins/apodictic/plugin.json` was being generated with a literal two-character string `\n` (backslash followed by lowercase n) instead of a real newline at end-of-file, because `scripts/build-antigravity.mjs` line 250 wrote `+ "\\n"` (escaped backslash) rather than `+ "\n"` (newline). The mechanical `node scripts/build-antigravity.mjs --check` did not catch this because it compared the freshly-generated workspace to the persisted workspace; both copies were corrupted identically. Result: the antigravity host's `plugin.json` was unparseable JSON (`SyntaxError: Unexpected non-whitespace character after JSON at position 1227`) for the entirety of v1.7.7 (when antigravity build was added) through v1.8.2.

Severity assessment: **build-script bug** per Phase 7 plan §D2.4 classification — fix immediately. The bug never surfaced in mechanical release checks because no consumer verifies JSON validity of the generated plugin.json — the file is consumed by the Antigravity host runtime, which would presumably reject it on installation. No user reports to date, so blast radius is limited to whoever attempted an Antigravity install of APODICTIC during the v1.7.7-v1.8.2 window.

#### Fix

- **`scripts/build-antigravity.mjs` line 250** — changed `+ "\\n"` (literal backslash-n) to `+ "\n"` (newline). One-character change.
- **`scripts/build-antigravity.mjs`** — added defensive `readJson(...)` re-parse of the generated `plugin.json` after write, so any future JSON-corruption regression fails the build immediately rather than silently passing through `--check` (which compares against itself). ~10 lines of validation logic + comment.
- **`antigravity/plugins/apodictic/plugin.json`** — regenerated with valid trailing newline; now parses as valid JSON.

#### D2 sweep — full results (parity holds elsewhere)

Spot-checked semantic parity across canonical → codex and canonical → antigravity:

- **Validate.sh + preflight.sh** — byte-identical across plugin source, codex, antigravity (`diff -q` confirms).
- **Skills tree (canonical → antigravity)** — byte-identical except .DS_Store cruft. All `references/` content preserved.
- **Skills tree (canonical → codex)** — diffs are all mechanical slash-to-wrapper rewrites (`/start` → `apodictic-start`, etc.) per the documented Codex transform. Spot-checked SKILL.md, run-core.md, changelog.md, series-continuity.md, plot-architecture/SKILL.md, pre-writing-pathway/SKILL.md, command files: every diff line is the slash-rewrite transformation, no semantic drift.
- **Frontmatter versions** — all SKILL.md frontmatter matches canonical (1.8.2 pre-bump, 1.8.3 post-bump) across all three trees.
- **Codex wrapper skills** — 11/11 commands have matching `apodictic-*` wrapper SKILL.md; all reference correct base skill and command path.
- **Antigravity workflow files** — 11/11 commands have matching `.agents/workflows/*.md`; orchestrator `instructions.md` reads correct canonical paths.
- **Cross-host contamination** — Codex `NON_PARITY_NOTES.md` does not mention Antigravity; Antigravity `NON_PARITY_NOTES.md` does not mention Codex. Host isolation preserved.
- **Codex JSONs (`.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`)** — both parse as valid JSON.
- **Antigravity `agents/core-orchestrator/agent.json`** — parses as valid JSON.

#### D3 Phase 7 done-gate verification

All 10 Phase 7 done-gate criteria verified CLOSED. All 6 spec §First Ship Gate criteria verified CLOSED. Verdict: **Phase 7 complete.** See `docs/review-log/2026-04-25_phase-7-wave-4-done-gate-verification.md` for per-criterion evidence.

#### Files

- `scripts/build-antigravity.mjs` — fix `"\\n"` → `"\n"` literal; add defensive JSON re-parse of generated plugin.json (~10 lines).
- `antigravity/plugins/apodictic/plugin.json` — regenerated valid (trailing newline correct; parses as JSON).
- `plugins/apodictic/skills/core-editor/references/changelog.md` — v1.8.3 entry.
- Version bumped via `scripts/bump-version.sh 1.8.3`.
- Generated host workspaces (codex, antigravity) regenerated via release pipeline (validate.sh / preflight.sh remain byte-identical to plugin source).

Total framework prose change: ~10 lines net (build-script fix + JSON parse guard). No skill content edits. No validator changes; all 11 validator self-tests PASS.

#### Self-test verification (v1.8.3)

| Validator | Cases | Status |
|---|---|---|
| `severity-floor` | 7 | PASS |
| `audit-signal-propagation` | 9 | PASS |
| `underdiagnosis-triggers` | 5 | PASS |
| `ledger-consolidation` | 5 | PASS |
| `decision-layer-check` | 12 | PASS |
| `quality-risk-triggers` | 12 | PASS |
| `timeline-diff` | 8 | PASS |
| `timeline-arithmetic` | 6 | PASS |
| `timeline-anchor-conflict` | 6 | PASS |
| `audit-tier-criterion` | 4 | PASS |
| `argument-recon-prerequisite` | 5 | PASS |

#### Out of scope

- Wave 5 closeout (Codex final review + E1 final report + E2 ROADMAP update) is the next and final wave; not in v1.8.3 scope.

---

## v1.8.2 - 2026-04-25

### Added — Phase 7 Wave 3: cross-cutting rule canonical-home governance + Plot Architecture vs Pass 2 boundary + Focus Map empirical test ROADMAP deferral

Closes Phase 7 Wave 3 of the model-capability review per `docs/review-log/2026-04-25_phase-7-implementation-plan.md` §Wave 3. Three jobs ship as a coordinated wave: C1 — cross-cutting rule **canonical-home governance / annotation work** (firewall, anti-sycophancy / no-self-revise, absence-first / blind-spot disclosure, Pass-10-Class artifact pattern); C2 — Plot Architecture vs. Pass 2 (Structural Mapping) boundary clarification; B2 — Focus Map empirical test formalized as ROADMAP entry (test runs not executed in this cycle; deferred per Phase 5 resource-cost rationale, formalized in Wave 3 with named re-evaluation triggers). Net framework prose change: small positive (canonical-home annotations and boundary block exceed the few collapsed restatements). No validator changes; all 11 validator self-tests pass.

**v1.8.4 framing correction (Codex final critique):** the v1.8.2 changelog originally described C1 as "cross-cutting rule dedup," which overclaimed compression value. The honest framing is **canonical-home governance**: the durable value is the canonical-home annotations themselves (forward-looking drift prevention naming the authoritative location for each cross-cutting rule), not present-cycle prose compression. Past Phase 4-6 work had already largely deduped the rules in their operational locations; the few remaining collapses (two reception-risk parentheticals, one adversarial-stress-test sentence) are small. The Wave 3 report itself acknowledged this ("Net positive prose change for C1 rather than the typical compression negative: the canonical-home annotations themselves are the durable compression value"); the title and opening sentence of this entry are now updated to match. "Dedup" should be read as governance against future drift, not substantial present compression.

#### C1 — Cross-cutting rule canonical-home governance

Phase 3 inventory identified five cross-cutting rules added during Phase 4-6 to a shared dedup table; per Phase 3 spec ("compression deferred to Phase 7 only after eval coverage exists"), Wave 2's B1 eval coverage of UNPROVEN instructions unblocked compression work in Wave 3. Each rule receives a canonical-home annotation marking the authoritative statement; non-canonical surfaces collapse generic restatements to pointers while preserving any context-specific elaboration.

- **Firewall — canonical home: `core-editor/SKILL.md §The Firewall`.** Annotation added naming downstream surfaces (`revision-coach/SKILL.md §The Coaching Firewall`, `adversarial-stress-test.md §Firewall Compliance`, `run-full.md §QA gate`, `pass-11.md §Forbidden`) and noting that those surfaces preserve only context-specific elaborations (coaching-mode drift, stress-test scope, market-viability scope). No generic restatements collapsed in this Wave — all downstream firewall mentions are already context-specific (coaching-firewall, stress-test firewall, pass-11 firewall, supplementary-audit firewall). The annotation prevents future drift by marking the canonical home explicitly.

- **Anti-sycophancy / no-self-revise — canonical home: `core-editor/references/output-policy.md §Severity Honesty Protocol`.** Annotation added naming downstream surfaces (`adversarial-stress-test.md §Lock-then-test protocol` / §Anti-softening rule, `specialized-audits/references/craft/reception-risk.md §Lock-then-classify` / §Forbidden #6, `run-synthesis.md §Step 5 Adversarial Self-Check`). Two reception-risk parentheticals collapsed to canonical pointer ("Anti-sycophancy / no-self-revise rule canonical in `core-editor/references/output-policy.md §Severity Honesty Protocol`."); preserves the audit-specific operational instructions (lock-then-classify discipline; "Reduce severity ratings through self-generated counter-arguments after locking" forbidden). Adversarial-stress-test §Lock-then-test sentence rewritten to point at the canonical rule while preserving the stress-test-specific elaboration (lock-before-steelman ordering). Per-audit Deficit-First Diagnostic Rule blocks (each audit-tailored) explicitly preserved in their audit reference files — they are operational expressions of the principle, not generic restatements.

- **Absence-first / deficit-first framing AND blind-spot disclosure as confidence limiter — canonical home: `core-editor/references/run-synthesis.md §Step 3 Blind Spot / Absence Inventory`.** (Two cross-cutting rules consolidated under one canonical home because Step 3 already integrates both: the Absence Inventory is the absence-first operational step; the Mandatory blind-spot disclosure paragraph is the confidence-limiter rule.) Annotation added naming downstream surfaces (`output-policy.md §Severity Honesty Protocol` rule #5 evidence-first checks, `submission-readiness.md §Blind-spot rule`, `pass-dependencies.md §4c` Auto-recommend before synthesis decline policy, `specialized-audits/SKILL.md §How to Use` Field Reconnaissance prerequisite paragraph). Submission-readiness §Blind-spot rule extended with canonical-home pointer while preserving the submission-readiness-specific elaboration (which audits, how the readiness verdict carries the limiter forward). Per-audit Deficit-First Diagnostic Rule opening blocks in `specialized-audits/references/craft/*.md` (11 audits — stakes-system, dialectical-clarity, ai-prose-calibration, interiority-preservation, emotional-craft, banister, decision-pressure, scene-turn, female-interiority, character-architecture, compression-audit) explicitly preserved — they are audit-tailored operational expressions, not generic restatements.

- **Pass-10-Class rolling artifact pattern — canonical home: `core-editor/SKILL.md §Project Integration §Pass-10-Class Rolling Structured Artifacts`** (already established in Phase 4). Annotation added naming downstream surfaces (`pass-dependencies.md §1 Tier 1 Pass 10 row`, `run-synthesis.md §Step 2 Pass-10-Class artifact integration`, `references/pass-10.md`) and noting that those surfaces add only artifact-instance specifics (Timeline schema, Argument_State schema, etc.). No generic restatements collapsed — downstream surfaces already cite back to the canonical home; the annotation prevents future drift.

**Risk-controlled dedup decisions (no rule deferred for risk).** Each cross-cutting rule had its canonical home statement spot-checked for sufficiency in isolation: the firewall block in `core-editor/SKILL.md` is complete (FORBIDDEN list + ALLOWED list + example); the anti-sycophancy block in `output-policy.md §Severity Honesty Protocol` is complete (5 manifestations + 5 rules); the absence-first + blind-spot disclosure block in `run-synthesis.md §Step 3` is complete (Absence Inventory protocol + Mandatory blind-spot disclosure paragraph for argument-shaped runs). Pointers preserve the contextual hint ("the audit-specific lock-then-classify discipline implements the canonical rule") so downstream readers reach the canonical statement without losing the local operational instruction. **No load-bearing redundancy was deferred** — all collapsed locations were generic parentheticals or one-line restatements, never the load-bearing operational instruction itself.

#### C2 — Plot Architecture vs. Pass 2 (Structural Mapping) boundary clarification

Phase 3 inventory flagged the boundary between Plot Architecture (a separate skill orchestrator covering 50 spines, 12 families, fantasy/series architecture) and Pass 2 (Structural Mapping in core editor) as ambiguous. Authors and models could confuse which to invoke when. Wave 3 ships explicit boundary documentation in three locations:

- **`plot-architecture/SKILL.md` — new §Plot Architecture vs. Pass 2 (Structural Mapping) — Boundary section** (~25 lines). Comparison table covering writer question, layer-of-operation, output, when-to-invoke, and routing for each. Cross-references in practice: Plot Architecture → Pass 2 (when a STRUCTURAL BREAK at the spine level wants on-page mapping); Pass 2 → Plot Architecture (when on-page structural symptoms cannot be diagnosed at the spine level). Rule-of-thumb: "what kind of book is this structurally" → Plot Architecture; "is the structure I have on the page working" → Pass 2; both → Pass 2 first, then Plot Architecture against the honest map.
- **`pass-dependencies.md §1 Tier 1 Pass 2 row** — extended Pass 2 output-artifact cell (~1 line) with the boundary callout pointing at `plot-architecture/SKILL.md` for spine-paradigm questions.
- **`core-editor/SKILL.md §Delegation Rules §Plot Structure** — extended (~3 lines) with the boundary distinction (Plot Architecture handles whole-work spine paradigm; Pass 2 handles on-page structural execution) and a cross-reference to the plot-architecture boundary section.

Total ~30 lines added across three files. The boundary clarification is small-scope and additive — no existing prose was rewritten or removed, no existing routing changed.

#### B2 — Focus Map empirical test formalized as ROADMAP deferral

Phase 5 deferred the Focus Map empirical test (6-fixture comparison: 3 fixtures × 2 arms — control vs. treatment) for resource reasons. The test framework was documented in `hybrid-mode.md §Focus Map Architectural Decision Framework`. Wave 3 formalizes the deferral as a named ROADMAP item rather than running the test in this cycle.

- **`ROADMAP.md` — new §Deferred (Empirically-Gated Decisions) section** added between §Not Planned and §Done, with one entry: "Focus Map Architectural Decision — Empirical Test." Entry covers source (Phase 5 deferred; Phase 7 Wave 3 formalized), current default (Focus Map remains hybrid-only — conservative per spec §Phase 5), hypothesis + acceptance criteria reference (pointer to `hybrid-mode.md §Focus Map Architectural Decision Framework`), test scope (6 runs total: 3 fixtures × 2 arms), and re-evaluation triggers (fixture corpus expansion making the 6-run cost worthwhile, OR Pass 10 Timeline integration forcing the cross-mode question). Decision until re-evaluated: default holds.
- **`hybrid-mode.md §Focus Map Architectural Decision Framework §Test deferred`** — extended (~3 lines) with explicit pointer to the new ROADMAP entry, naming the re-evaluation triggers and confirming the framework default holds until trigger + acceptance-bar clearance.

#### Files

- `plugins/apodictic/skills/core-editor/SKILL.md` — firewall canonical-home annotation (~2 lines); Pass-10-Class artifact pattern canonical-home annotation (~2 lines); §Delegation Rules §Plot Structure boundary clarification (~3 lines).
- `plugins/apodictic/skills/core-editor/references/output-policy.md` — anti-sycophancy / no-self-revise canonical-home annotation in §Severity Honesty Protocol (~2 lines).
- `plugins/apodictic/skills/core-editor/references/run-synthesis.md` — absence-first + blind-spot disclosure canonical-home annotation in §Step 3 Blind Spot / Absence Inventory (~2 lines).
- `plugins/apodictic/skills/core-editor/references/adversarial-stress-test.md` — §Lock-then-test protocol rewritten to point at canonical rule (~1 line net change, no collapse).
- `plugins/apodictic/skills/specialized-audits/references/craft/reception-risk.md` — two parenthetical anti-sycophancy restatements collapsed to canonical pointers (~0 lines net; same word count).
- `plugins/apodictic/skills/core-editor/references/submission-readiness.md` — §Blind-spot rule extended with canonical-home pointer (~1 line).
- `plugins/apodictic/skills/plot-architecture/SKILL.md` — new §Plot Architecture vs. Pass 2 (Structural Mapping) — Boundary section (~25 lines).
- `plugins/apodictic/skills/core-editor/references/pass-dependencies.md` — Pass 2 row extended with boundary callout (~1 line).
- `ROADMAP.md` — new §Deferred (Empirically-Gated Decisions) section + Focus Map entry (~20 lines).
- `plugins/apodictic/skills/core-editor/references/hybrid-mode.md` — §Test deferred extended with ROADMAP pointer (~3 lines).
- `plugins/apodictic/skills/core-editor/references/changelog.md` — v1.8.2 entry.
- Version bumped via `scripts/bump-version.sh 1.8.2`.
- Generated host workspaces (codex, antigravity, APODICTIC-Gemini) regenerated via release pipeline.

Total framework prose change: net positive ~50 lines (canonical-home annotations + C2 boundary block + B2 ROADMAP/hybrid-mode pointers exceed the few collapsed parentheticals). No validator changes; no `validate.sh` change; root `scripts/validate.sh` remains byte-identical to plugin source. All 11 validator self-tests PASS. All 4 release checks PASS.

#### Self-test verification (v1.8.2)

| Validator | Cases | Status |
|---|---|---|
| `severity-floor` | 7 | PASS |
| `audit-signal-propagation` | 9 | PASS |
| `underdiagnosis-triggers` | 5 | PASS |
| `ledger-consolidation` | 5 | PASS |
| `decision-layer-check` | 12 | PASS |
| `quality-risk-triggers` | 12 | PASS |
| `timeline-diff` | 8 | PASS |
| `timeline-arithmetic` | 6 | PASS |
| `timeline-anchor-conflict` | 6 | PASS |
| `audit-tier-criterion` | 4 | PASS |
| `argument-recon-prerequisite` | 5 | PASS |

#### Out of scope (deferred Phase 7 work)

- **D2 — Generated host parity sweep + D3 — Phase 7 done-gate verification.** Wave 4 work.
- **E1 — Model-capability review final report + E2 — ROADMAP.md update.** Wave 5 work (the v1.8.2 ROADMAP edit is scoped to the B2 deferral entry only; the broader Wave 5 ROADMAP closeout updates ship in Wave 5).

---

## v1.8.1 - 2026-04-25

### Added — Phase 7 Wave 2: 11 UNPROVEN instructions eval coverage + decision-layer-check re-eval against canonical fixtures

Closes Phase 7 Wave 2 of the model-capability review per `docs/review-log/2026-04-25_phase-7-implementation-plan.md` §Wave 2. Two jobs ship as a coordinated wave: B1 — static-analysis eval coverage of the 11 UNPROVEN instructions identified by Phase 3 inventory + archaeology log against the four canonical fixtures (F1/F2 fiction-novella baseline + comparator runs, F3 short-fiction control, F4 argument-shaped nonfiction); B3 — re-run of `decision-layer-check` against the four canonical fixtures after Wave 1 A1 calibration, with B3-extension calibration to close two remaining gaps (bold-paragraph subhead detection; Must-Fix entry-form filter). Validator suite total stays at 11; self-test extended from 11 cases to 12 (`decision-layer-check` adds `c1b_bold_subhead_clusters`). Phase 7 Wave 3 (Group C compression work) unblocked.

#### B1 — 11 UNPROVEN instructions eval coverage (static analysis)

Per Phase 3 inventory + archaeology, 11 instructions were classified Keep-UNPROVEN — meaning provenance evidence is missing OR the instruction's load-bearing effect was unverified at Phase 3 close. v1.8.1 documents static-analysis eval coverage of each instruction against the four canonical fixtures, classifying per fixture and producing per-instruction verdicts.

- **Verdict distribution:** 7 Confirmed load-bearing / 0 No detectable effect / 4 Ambiguous-or-Partial (3 due to fixture scope outside instruction's natural exercise class; 1 split confirmed/needs-corpus-expansion).
- **Zero v1.9.x deletion candidates surfaced.** All 11 instructions either show direct fixture evidence of load-bearing behavior or are scoped outside the current fixture set in ways the report documents — per spec discipline ("guesswork includes guessing the rule still matters when no test catches it failing"; unexercised ≠ not load-bearing), unexercised instructions are flagged for v1.8.x or v1.9.x corpus expansion, not deletion.
- **Highest-confidence findings:** (1) Universal-audit status criterion (B1-2): confirmed load-bearing in all four fixtures including in negative-disclosure form. (2) consent-complexity.md full file (B1-4): confirmed load-bearing across three of four in-scope fixtures with named-flag invocation (CC-6 Perpetrator Erasure observed in F3). (3) Auto-escalation + root-cause + findings-table caps (B1-3 / B1-8 / B1-9): three overlapping evals all converge on cap-honoring behavior across all four fixtures.
- **Corpus-expansion candidates for v1.9.x (per fixture-scope limitation, not deletion):** state-lifecycle gardening thresholds (synthetic state-file fixtures); ai-prose-calibration AIC-2 / AIC-4 / AIC-6 / AIC-8 flag families (synthetic AI-heavy fixture); queer-romance-erotica / cozy-tag / philosophical-tag tag audits (genre-specific short fixtures).
- **Output:** `docs/review-log/2026-04-25_phase-7-wave-2-eval-coverage.md` documents per-instruction location, stated effect, eval method, per-fixture findings, verdict, and recommendation. Summary table at top.

#### B3 — `decision-layer-check` re-eval against canonical fixtures + Wave 2 calibration extensions

Wave 1 (v1.8.0) shipped A1 calibration for the four C1-C4 patterns identified by Phase 4 Wave 3. B3 re-runs the calibrated validator against F1-F4 to confirm the four FAILs from Phase 4 Wave 3 are resolved.

- **Pre-Wave-1 baseline:** F1 FAIL (2 checks); F2 FAIL (3 checks); F3 FAIL (2 checks); F4 FAIL (1 check + 1 WARN).
- **Post-Wave-1 (A1) result:** Approximately half of the original failures closed. Two patterns remained as A1 calibration scope-misses: (1) F1's Author Decisions section uses bold-paragraph subheads (`**Keep**`, `**Cut / Release**`, `**Unsure — decide before revision**`) rather than level-3 markdown subheads (`### Keep`); A1's C1 calibration only detected `### Keep`. (2) All four fixtures discuss "Must-Fix" extensively in body prose (severity-test commentary, Findings Ledger discussions) without those mentions being labeled finding entries; A1's C5 paragraph-block widening helped but didn't address the prose-vs-label distinction.
- **Wave 2 B3a — Bold-paragraph subhead detection.** C1 subhead-cluster count extended to detect both level-3 markdown subheads AND bold-paragraph subheads (`**Keep**`, `**Cut / Release**`, etc.) as cluster delimiters. Both forms are equivalent semantically; the validator now treats them as equivalent. Self-test adds `c1b_bold_subhead_clusters` (mirrors canonical fixture F1 pattern: 13 sub-bullets across 3 bold-paragraph subheads → 3 cluster count → PASS).
- **Wave 2 B3b — Must-Fix entry-form filter.** Check 5 evidence-density previously counted every line containing the literal "Must-Fix" string as a labeled finding. Editorial letters discuss Must-Fix extensively in body prose (verdict commentary, severity-test discussion, ledger summaries) without those mentions being labeled entries. v1.8.1 extends the filter to count Must-Fix mentions only when in label form: heading line; list-item leader within first 80 chars; numbered list-item leader within first 80 chars; `**Severity:**` label co-located with Must-Fix; bare `Severity:` label at line start; MF-N anchor co-located with Must-Fix; pipe-table cell. Plus appendix-exclusion (appendix-only mentions are severity-calibration discussion, not labeled findings). The filter uses POSIX-portable `tolower()` + `index()` for case-insensitive matching (awk's `/i` regex flag is not POSIX-portable; initial implementation discovered this and corrected to portable form). Existing `neg4` self-test fixture restructured from bare prose `Must-Fix:` line to `### Must-Fix:` heading form to preserve the original test intent (label form with <2 references should still FAIL Check 5).
- **Post-Wave-2 (A1 + B3) result:** All four canonical fixtures (F1, F2, F3, F4) now produce **OK** on `decision-layer-check`. All 12 self-test cases PASS (added `c1b_bold_subhead_clusters`). No regression on the 6 prior validator self-tests.
- **Calibration effectiveness:** A1 (Wave 1) was partially effective; B3 extension (Wave 2) closes the remaining gaps. Across the two waves, all four Phase 4 Wave 3 calibration findings (C1-C4) plus the two Wave 2-surfaced patterns (bold-paragraph subhead form; prose-vs-label Must-Fix distinction) are resolved.

#### Files

- `plugins/apodictic/scripts/validate.sh` — `decision-layer-check`: B3a bold-paragraph subhead detection (~+15 lines); B3b Must-Fix entry-form filter with body-only scope (~+30 lines); self-test extended from 11 to 12 cases (added `c1b_bold_subhead_clusters`); `neg4` fixture restructured to use `### Must-Fix:` heading + bare-bullet Author Decisions to preserve original Check 5 negative-test intent. Net ~+95 lines.
- `scripts/validate.sh` — synced with plugin copy (canonical lives at `plugins/apodictic/scripts/validate.sh`; root copy is the user-facing alias).
- `plugins/apodictic/skills/core-editor/references/changelog.md` — v1.8.1 entry.
- Version bumped via `scripts/bump-version.sh 1.8.1`.
- Generated host workspaces (codex, antigravity) regenerated via release pipeline.

Total prose change: 0 lines in framework prose (all edits in `validate.sh` validator + self-test + new review-log entry). Total validator change: ~+95 lines in `validate.sh`. All 11 validator self-tests PASS. All 4 release checks PASS.

#### Self-test verification (v1.8.1)

| Validator | Cases (was → now) | New coverage |
|---|---|---|
| `severity-floor` | 7 | Unaffected |
| `audit-signal-propagation` | 9 | Unaffected |
| `underdiagnosis-triggers` | 5 | Unaffected |
| `ledger-consolidation` | 5 | Unaffected |
| `decision-layer-check` | 11 → 12 | B3a `c1b_bold_subhead_clusters` (bold-paragraph subhead form); B3b Must-Fix entry-form filter (existing `neg4` restructured) |
| `quality-risk-triggers` | 12 | Unaffected |
| `timeline-diff` | 8 | Unaffected |
| `timeline-arithmetic` | 6 | Unaffected |
| `timeline-anchor-conflict` | 6 | Unaffected |
| `audit-tier-criterion` | 4 | Unaffected |
| `argument-recon-prerequisite` | 5 | Unaffected |

#### Out of scope (deferred Phase 7 work)

- **B2 — Focus Map empirical test.** Wave 3+ work per Phase 7 plan §Wave 3 sequencing.
- **C1 — Cross-cutting prose compression.** Wave 3 work; unblocked by B1 closure.
- **C2 — Plot Architecture vs Pass 2 boundary clarification.** Wave 3 work.
- **D2 — Generated host parity sweep + D3 — Phase 7 done-gate verification.** Wave 4 work.

---

## v1.8.0 - 2026-04-25

### Added — Phase 7 Wave 1: decision-layer-check calibration + optional validators batch + v1.7.1 changelog backfill

Closes Phase 7 Wave 1 of the model-capability review per `docs/review-log/2026-04-25_phase-7-implementation-plan.md` §Wave 1. Three jobs ship as a coordinated wave: decision-layer-check calibration against the four C1-C4 Phase 4 Wave 3 eval-coverage findings (A1); two new validators from the Phase 6 + v1.7.9 §Out-of-scope queue (A2); v1.7.1 changelog backfill closing the documented release-hygiene gap (D1). Validator suite total: 9 → 11. v1.8.0 ships as the first release of the Phase 7 cycle (rc1 in plan terms; final 1.8.0 number reserved for end of Phase 7 closure once Waves 2-5 land).

#### A1 — `decision-layer-check` calibration (Phase 4 Wave 3 C1-C4 closure)

The Phase 4 Wave 3 eval-coverage report (`docs/review-log/2026-04-25_phase-4-eval-coverage.md`) documented four calibration findings against the four canonical fixtures (F1/F2 fiction-novella baseline + comparator runs, F3 short-fiction control, F4 argument-shaped nonfiction). All four FAILs were calibration artifacts, not contract violations. v1.8.0 calibrates the validator's parsing logic to close them.

- **C1 — Author Decisions count over-fires on Keep/Cut/Unsure subhead clusters.** Phase 4-6 validator counted each sub-bullet across subheads (13 sub-bullets in F1 → out-of-3-7 ERROR). v1.8.0 detects `### Keep` / `### Cut` / `### Unsure` (also `### Defer` / `### Decide`) subheads within the Author Decisions section and counts subhead clusters (typical 1-3) when present. Implements the contract intent: "3-7 distinct decision categories, with sub-items permitted." Falls back to list-item counting when no subheads.

- **C2 — Codex paragraph-form decision entries undetected.** Phase 4-6 validator's heuristic order (list items → bolded paragraphs) returned zero on Codex 5.5 letters that use blank-line-separated paragraphs leading with verb-prefixed sentences ("Protect..." / "Keep..." / "Cut..."). v1.8.0 adds a third-fallback heuristic: count blank-line-separated paragraphs whose first sentence begins with a canonical decision verb (Protect / Keep / Cut / Defer / Decide / Unsure) or contains an opening bolded keyword (`**Decision:**`, `**Question:**`, `**Element:**`). Risk-controlled — only fires when list-item and bolded-paragraph heuristics return zero.

- **C3 — Argument-DE letters use different headings + lack canonical Appendix A/B/C.** F4 argument-shaped letters use "Coalition-Partner Ground-Truth Recommendations" and "Editorial-Dispute Territory" instead of "Protected Elements" / "Author Decisions"; they don't include Control Questions or Appendix A/B/C blocks. v1.8.0 detects argument-DE class via marker presence ("Coalition-Partner Ground-Truth Recommendations", "Editorial-Dispute Territory", "Argument_State", "Claim Ladder", "Argument Engine"). When detected: Check 1 accepts the variant heading names; Check 2 accepts "Editorial-Dispute Territory" as the equivalent decision section; Checks 3-4 (Control Questions, Appendix A/B/C) are skipped — argument-DE class is not held to fiction-DE structural contract.

- **C4 — Evidence-density 6-line window misses inline-prose evidence.** Phase 4-6 validator scanned exactly 6 lines after each Must-Fix mention; Codex letters with paragraph-form evidence (references in surrounding prose, not in an immediate trailing list) FAILed despite documenting evidence within the Must-Fix's section block. v1.8.0 widens the window to a paragraph-block scan: from each Must-Fix line until the next Must-Fix occurrence OR the next section header (^## at column 0), whichever comes first. Trade-off documented: wider window reduces false-positive density flags but is slightly less strict on truly under-evidenced Must-Fixes.

- **Self-test extended from 7 cases to 11.** Original cases preserved (pos, neg1-4, over1, over_appx); new cases added — `c1_subhead_clusters` (Keep/Cut/Unsure with 13 sub-bullets → 3 cluster count → PASS), `c2_paragraph_form` (Codex-style verb-leading paragraphs → paragraph-form fallback → PASS), `c3_argument_de` (argument-DE letter with Coalition-Partner / Editorial-Dispute headings → Checks 3-4 skipped → PASS), `c4_paragraph_evidence` (Must-Fix with inline-prose evidence in the surrounding paragraph block → paragraph-block window → PASS). Negative cases (neg3 specifically) restructured from subheaded form to bare list form so list-item count = 8 still triggers the out-of-range error; over1 / over_appx restructured to bare list form so subhead-cluster mode does not mask the original Control Questions test.

- **B3 deferral.** Re-running the calibrated validator against the four canonical fixtures (B3 in the Phase 7 plan) is deferred to Wave 2 — Wave 1 lands the calibration; Wave 2 confirms F1-F4 produce expected results post-calibration. The Phase 7 plan §Wave 2 sequencing (B3 depends on A1) is honored.

#### A2 — Optional validators batch (`audit-tier-criterion` + `argument-recon-prerequisite`)

Two of the three optional validators identified in v1.7.9 §Out of scope and the Phase 7 plan §A2 ship in Wave 1. The third (`audit-signal-propagation §4e context-modifier extension`) is deferred to a later Phase 7 wave per scope-control. Validator total: 9 → 11.

- **`audit-tier-criterion` (new validator, ~250 lines).** Verifies audit tier assignments in `pass-dependencies.md §4a/§4b` against the §4c Audit Tier Promotion Criteria (Phase 6 Wave 2). Mechanically verifies criterion 1 (named hard gates / Must-Fix floor) by scanning each high-tier audit's reference file for `hard[ -]?gate` or `must-?fix[ -]?floor` patterns. Audits at Hard Prerequisite / Pre-DE Prerequisite / Auto-run / Auto-recommend before synthesis tiers without criterion-1 language are surfaced as candidates for tier review. Recommend / Auto-recommend tiers are exempt. **Capability ceiling documented:** criteria 2 (undetectable-by-passes) and 3 (disclosure-non-equivalence) require model judgment about the manuscript / fixture corpus and remain in the §4a/§4b verification subsection prose. Per-audit override marker: `<!-- override: audit-tier-criterion-<audit-slug> --> `. Self-test: 4 cases (pos, neg, over, edge — Recommend tier exempt). **v1.8.4 honest correction:** the v1.8.0 self-test (PASS) was insufficient — Codex final critique surfaced 5 canonical-input failures against `pass-dependencies.md` (AI-Prose Calibration / Consent Complexity / Memoir & Creative Nonfiction / Narrative Nonfiction Craft / Series Continuity), all closed in v1.8.4 via audit-side hard-gate / Must-Fix-floor language additions. The validator's logic was correct; the audit references genuinely lacked the language their tier required. Self-test passing on synthetic fixtures did not prove canonical-framework conformance; v1.8.4 closes both. See v1.8.4 entry below.

- **`argument-recon-prerequisite` (new validator, ~190 lines).** Verifies argument-shaped runs satisfy the Field Reconnaissance prerequisite per `pass-dependencies.md §4a` (Hard Prerequisite or Auto-recommend before synthesis tier) and v1.7.9's wired execution-flow Pre-Pass Prerequisite Resolution step. Detects argument-engine artifacts (Argument_State.md, Red_Team_Memo.md, Argument_Evidence.md, Argument_Persuasion.md, Adversarial_Evidence.md) by filename pattern in the run folder, plus editorial-letter mentions of Dialectical Clarity / Argument Red Team / Argument Evidence Deep-Dive / argument-engine pass output. When argument-engine present, requires either (a) `Field_Reconnaissance_Report.md` in the run folder, OR (b) the canonical blind-spot disclosure ("literature-counterevidence not surveyed") in the editorial letter per `run-synthesis.md §Step 3` (Phase 6 Wave 3 / CR-4). Silent omission is forbidden at the Hard Prerequisite tier per the canonical decline policy. Body-only override marker: `<!-- override: argument-recon-prerequisite -->`. Self-test: 5 cases (pos1 — argument-engine + Field Recon; pos2 — argument-engine + canonical disclosure; pos3 — fiction run exempt; neg — silent omission caught; over — override marker downgrades).

- **Deferred from A2 batch:** `audit-signal-propagation §4e context-modifier extension` (per-audit table-driven dispatch reading §4e programmatically). Listed in Phase 7 plan as one of three A2 items; deferred to a later wave to keep Wave 1 scope bounded. v1.7.9's audit-signal-propagation default mapping continues to handle the verification.

#### D1 — v1.7.1 changelog backfill

The v1.7.1 release ("underdiagnosis hardening") shipped 2026-04-23 without a changelog entry — flagged in Phase 4 Wave 1 as a deferred hygiene item. Wave 1 of Phase 7 backfills the entry between v1.7.0 and v1.7.2 with explicit non-contemporaneous note. Cites originating commits `cfaadef` (underdiagnosis hardening), `7bb9c34` (Deficit-First extension to 5 craft audits), `9cd8948` (release.sh build-antigravity step), and version-bump commit `6b477d5`. See v1.7.1 entry below for full content.

#### Files

- `plugins/apodictic/scripts/validate.sh` — `decision-layer-check` calibrated for C1-C4 with extended self-test (~+330 lines net: doc-comment expansion, three-tier counting helper with subhead-cluster + paragraph-form fallbacks, argument-DE class detection, paragraph-block evidence-density window, four new self-test fixtures); two new validators added (`audit-tier-criterion` ~250 lines including self-test; `argument-recon-prerequisite` ~190 lines including self-test); top-of-file usage doc-comments extended for both new validators; usage help text updated. Net ~+750 lines.
- `scripts/validate.sh` — synced with plugin copy (canonical lives at `plugins/apodictic/scripts/validate.sh`; root copy is the user-facing alias).
- `plugins/apodictic/skills/specialized-audits/SKILL.md` — added Field Reconnaissance prerequisite paragraph in How to Use section pointing to `argument-recon-prerequisite` validator (~+3 lines).
- `plugins/apodictic/skills/core-editor/references/changelog.md` — v1.8.0 entry; v1.7.1 backfill entry between v1.7.0 and v1.7.2.
- Version bumped via `scripts/bump-version.sh 1.8.0`.
- Generated host workspaces (codex, antigravity) regenerated via release pipeline.

Total prose change: ~3 lines added (SKILL.md). Total validator change: ~+750 lines in `validate.sh`. All 11 validator self-tests PASS. All 4 release checks PASS.

#### Self-test verification (v1.8.0)

| Validator | Cases (was → now) | New coverage |
|---|---|---|
| `severity-floor` | 7 | Unaffected |
| `audit-signal-propagation` | 9 | Unaffected |
| `underdiagnosis-triggers` | 5 | Unaffected |
| `ledger-consolidation` | 5 | Unaffected |
| `decision-layer-check` | 7 → 11 | C1 (subhead clusters), C2 (paragraph form), C3 (argument-DE class), C4 (paragraph-block evidence window) |
| `quality-risk-triggers` | 12 | Unaffected |
| `timeline-diff` | 8 | Unaffected |
| `timeline-arithmetic` | 6 | Unaffected |
| `timeline-anchor-conflict` | 6 | Unaffected |
| `audit-tier-criterion` | 0 → 4 | NEW — pos / neg / over / edge (Recommend-tier exempt) |
| `argument-recon-prerequisite` | 0 → 5 | NEW — pos1 (Field Recon present) / pos2 (canonical disclosure) / pos3 (fiction exempt) / neg (silent omission) / over |

#### Out of scope (deferred Phase 7 work)

- **B3 — decision-layer-check re-eval against canonical fixtures (F1-F4).** Wave 2 work per Phase 7 plan §Wave 2 sequencing.
- **`audit-signal-propagation §4e context-modifier extension`.** Third A2 validator deferred to a later Phase 7 wave; v1.7.9 default mapping continues to handle propagation verification.
- **A3 Python-helper-based true Timeline parsing.** Recommended out of scope for the model-capability review cycle per Phase 7 plan §A3; added to ROADMAP.md as future Python tooling cycle candidate.

---

## v1.7.9 - 2026-04-25

### Fixed — Honest Validator Capability Correction + Execution-Flow Prerequisite Wiring

Closes five review findings on the v1.7.8 framework state (Joshua's substantive code review). Four validators overclaimed what they actually verified; the new Hard Prerequisite tier policy from Phase 6 Wave 3 wasn't wired into the `run-core.md` execution flow. v1.7.9 ships the coordinated correction: one validator tightened to actually do per-audit, per-signal propagation verification; one validator extended to cover Section 3 marker inventory and to count-match Section 8 documentation; two validators reframed honestly as marker-hygiene / pre-labeled-conflict-surfacing checks with Phase 7 deferral noted for true verification; one execution-protocol step added to wire Hard Prerequisite resolution before pass dispatch. No commits, no behavior regression for Phase 4-6 work that was already correct.

#### Finding 1 — `audit-signal-propagation` overclaim (P1, tightened)

The Phase 4-6 validator only checked the whole letter for severity-vocabulary presence (any "Must-Fix" anywhere in body satisfied any audit's hard-gate signal in any appendix). A letter with an unrelated Decision Pressure Must-Fix in the body and a Reception Risk hard gate buried in Appendix A passed. The `run-synthesis.md §Step 2` prose promised per-signal §4e-table-driven verification; the implementation didn't do this.

- **`plugins/apodictic/scripts/validate.sh` `audit-signal-propagation`** — substantial rewrite (~+200 lines net). The validator now: (a) detects each audit appendix subsection by name (`<Audit Name> Audit` heading or in-appendix prose mention); (b) for each detected audit, identifies its severity signals (hard-gate, Must-Fix floor, HIGH/Alert) within that audit's subsection; (c) for each signal, verifies the synthesis body's Must-Fix or Should-Fix list contains either an explicit audit-name reference (e.g., "Reception Risk Alert at L2956") OR a finding tied to evidence-line numbers shared with the audit's appendix subsection. Per-class override markers (`audit-propagation-hard-gate`, etc.) preserved; new per-audit override marker form added (`audit-propagation-<audit-slug>`) for principled single-audit deviations. Body-only marker invariant preserved. Self-test extended from 6 cases to 9 cases including Joshua's canonical false-pass case (`neg1b`) — letter with unrelated Decision Pressure Must-Fix in body and Reception Risk hard gate in Appendix A — which now correctly FAILS where Phase 4-6 PASSED. Falls back to legacy whole-letter taxonomy check when no audit appendix subsections are detected (preserves Phase 4 behavior for letters that mention severity vocabulary without dedicated audit appendices).

- **`plugins/apodictic/skills/core-editor/references/run-synthesis.md` §Step 2** — Canonical Audit-Signal Propagation Rule prose tightened to honestly describe what the validator verifies (per-audit, per-signal; audit-name reference OR shared evidence-line; not generic Must-Fix presence). New per-audit override marker form documented.

#### Finding 2 — `timeline-diff` Section 3 + Section 8 count-match (P1, extended)

The Phase 4-6 validator only extracted Section 1 Event Ledger pipe-table rows. Section 3 (Temporal Marker Inventory) bullet items, Section 2 calendar shifts, Section 4 paradoxes, and Section 8 prose-only documentation all went uncovered. Section 8 documentation was accepted on keyword presence alone (any "Added" / "Removed" / "Changed" satisfied any structural delta).

- **`plugins/apodictic/scripts/validate.sh` `timeline-diff`** — extended (~+50 lines net). The validator now: (a) continues extracting Section 1 pipe-table rows (preserved Phase 4-6 behavior); (b) ALSO extracts Section 3 bullet items (`- ...` lines under the Section 3 heading) and diffs them; (c) when Section 8 contains bullet-form documentation (`- Added: ...`, `- Removed: ...`), counts those bullets and requires them to cover the structural totals across Section 1 + Section 3 (count-match, not just keyword-presence). Sections 2 (Master Calendar) and 4 (Inconsistency Ledger) are documented as freeform prose deferred to Phase 7 item-level diffing — diffed at section-presence level only by the bash validator. Self-test extended to 8 cases including a Section-3-only change (Phase 4-6 missed; v1.7.9 catches) and a count-mismatch case (Section 8 documents 1 added when structural diff shows 3 added).

- **`plugins/apodictic/skills/core-editor/references/pass-10.md` §Validator Integration** — `timeline-diff` description updated to reflect the actual Section 1 + Section 3 + Section 8 count-match behavior.

#### Finding 3 — `timeline-arithmetic` honest reframing (P1, reframed)

Real arithmetic checks need date-format parsing across heterogeneous anchor formats (`Day 1 morning`, `the following Friday`, `January 14`) plus span normalization plus pairwise compatibility reasoning — not feasible in bash. The Phase 4-6 validator only grepped for negative-gap text or pre-written conflict markers, but the `--help` text and the `pass-10.md` description claimed it verified span calculations. Real arithmetic violations passed.

- **`plugins/apodictic/scripts/validate.sh` `timeline-arithmetic`** — reframed (~+25 lines net, no semantic change to detection). Doc-comment, OK/WARN/ERROR messages, and self-test descriptions updated to honestly describe the validator as "marker hygiene only" with "true arithmetic verification deferred to a Phase 7 Python helper." Self-test extended with a `silent_arithmetic` case that documents the Phase 7 limitation (the case passes with an explicit comment that bash cannot detect it). Validator command name preserved (no integration breakage).

- **`plugins/apodictic/skills/core-editor/references/pass-10.md` §Validator Integration** — `timeline-arithmetic` description updated to match validator's honest semantics.

#### Finding 4 — `timeline-anchor-conflict` honest reframing (P1, reframed)

Same pattern as Finding 3. The Phase 4-6 validator only counted parenthetical `(contradicts ...)` annotations — i.e., only caught conflicts the Pass 10 model had already pre-labeled. The `--help` text and `pass-10.md` claimed it identified pairs of explicit temporal markers that cannot both be true. Same Ch 1 §1 with both "Monday morning" and "Tuesday morning" passed unless the model pre-labeled it.

- **`plugins/apodictic/scripts/validate.sh` `timeline-anchor-conflict`** — reframed (~+25 lines net, no semantic change to detection). Doc-comment, OK/WARN/ERROR messages, and self-test descriptions updated to "pre-labeled-conflict surfacing only" with "true anchor parsing deferred to a Phase 7 Python helper." Self-test extended with a `silent_anchor` case (same scene with two different anchors, no parenthetical pre-labeling) that documents the Phase 7 limitation. Validator command name preserved.

- **`plugins/apodictic/skills/core-editor/references/pass-10.md` §Validator Integration** — `timeline-anchor-conflict` description updated to match validator's honest semantics.

#### Finding 5 — Hard Prerequisite tier wired into `run-core.md` execution flow (P2, wired)

Phase 6 Wave 3 added `Hard Prerequisite` and `Pre-DE Prerequisite` tiers in `pass-dependencies.md §4a/§4c/§4f` (Field Reconnaissance and Citation Verifier for high-stakes argument-shaped runs). The tier definitions named the obligation ("Field Recon MUST complete before any Tier 2 evaluative pass") but `run-core.md`'s execution protocol jumped from pass resolution directly to pass dispatch with no prerequisite resolution step. The policy was documented but not executable.

- **`plugins/apodictic/skills/core-editor/references/run-core.md` §Audit Activation at Contract** — paragraph extended (~3 lines) to call out Hard Prerequisite and Pre-DE Prerequisite tiers as exceptions to the "audits run after core passes" baseline, with cross-reference to `pass-dependencies.md §4a/§4c/§4f`.

- **`plugins/apodictic/skills/core-editor/references/run-core.md` §Execution Protocol** — new step 6 (`Pre-Pass Prerequisite Resolution`) added before pass dispatch (~12 lines). The step walks `pass-dependencies.md §4a` for Hard Prerequisite and Pre-DE Prerequisite audits given the resolved contract, dispatches them in the correct order (Pre-DE first, Hard before Tier 2), handles the decline path per `pass-dependencies.md §4c` + §4f edge cases 8-9 (terminate or downgrade-with-disclosure; silent omission forbidden), records resolution in the Audit Invocation Log, and honors the §4f tier precedence invariant. Subsequent dispatch steps renumbered (single-agent: step 7-8; multi-agent: steps 7-10) to inherit Pre-Pass Prerequisite outputs as analytical context alongside the contract.

#### Files

- `plugins/apodictic/scripts/validate.sh` — `audit-signal-propagation` rewritten for per-audit per-signal verification (~+200 lines); `timeline-diff` extended to Section 3 + Section 8 count-match (~+50 lines); `timeline-arithmetic` reframed as marker hygiene with Phase 7 deferral (~+25 lines); `timeline-anchor-conflict` reframed as pre-labeled surfacing with Phase 7 deferral (~+25 lines); top-of-file usage doc-comments updated. Net ~+300 lines.
- `scripts/validate.sh` — synced with plugin copy (canonical lives at `plugins/apodictic/scripts/validate.sh`; root copy is the user-facing alias).
- `plugins/apodictic/skills/core-editor/references/run-core.md` — Audit Activation at Contract paragraph extended (~3 lines); new §Execution Protocol step 6 (Pre-Pass Prerequisite Resolution) with subsequent steps renumbered (~+12 lines). Net ~+15 lines.
- `plugins/apodictic/skills/core-editor/references/run-synthesis.md` — §Step 2 Canonical Audit-Signal Propagation Rule prose tightened to honestly describe per-audit per-signal verification (~+5 lines); per-audit override marker form documented (~+8 lines). Net ~+13 lines.
- `plugins/apodictic/skills/core-editor/references/pass-10.md` — §Validator Integration descriptions rewritten to honestly state validator capabilities (Section 1 + Section 3 + count-match for `timeline-diff`; marker hygiene only for `timeline-arithmetic`; pre-labeled surfacing only for `timeline-anchor-conflict`); new §Phase 7 Work Items section (~+30 lines) listing the Python helper work items with a framework-design lesson on bash validator ceiling. Net ~+50 lines.
- Version bumped via `scripts/bump-version.sh 1.7.9`.
- Generated host workspaces (codex, antigravity) regenerated via release pipeline; APODICTIC-Gemini public mirror synced.

Total prose change: ~78 lines added across framework files. Total validator change: ~+300 lines in `validate.sh`. All 9 validator self-tests PASS. All 4 release checks PASS.

#### Self-test verification (v1.7.9)

| Validator | Cases (was → now) | Joshua's false-pass case |
|---|---|---|
| `severity-floor` | 7 | Unaffected |
| `audit-signal-propagation` | 6 → 9 | `neg1b` (unrelated Must-Fix in body + Reception Risk hard gate in appendix) — was PASS, now FAIL |
| `underdiagnosis-triggers` | 5 | Unaffected (delegates to audit-signal-propagation; tighter delegate behavior preserved) |
| `ledger-consolidation` | 5 | Unaffected |
| `decision-layer-check` | 8 | Unaffected |
| `quality-risk-triggers` | 12 | Unaffected |
| `timeline-diff` | 5 → 8 | `s3_neg` (Section 3 marker change undocumented), `count_mismatch` (Section 8 documents 1 of 3 added) — was PASS, now FAIL |
| `timeline-arithmetic` | 5 → 6 | `silent_arithmetic` documents Phase 7 limitation (still passes; honest about ceiling) |
| `timeline-anchor-conflict` | 5 → 6 | `silent_anchor` documents Phase 7 limitation (still passes; honest about ceiling) |

#### Framework-design lesson (logged in `pass-10.md §Phase 7 Work Items`)

Bash validators have a real ceiling. Bash is excellent for structural and pattern-presence checks (heading inventory, table-row diff, marker keyword surfacing, count matching) but cannot do parsing, normalization, or reasoning over heterogeneous formats (date math across `Day N` / `Monday morning` / `January 14`; cross-format span normalization; pairwise compatibility reasoning). Phase 4-6 validator work mixed the two by *claiming* parsing capability in bash validators that only did keyword grepping — producing validators that overclaimed and false-passed on the cases that most matter. v1.7.9's correction: each validator's `--help` text, doc-comment, OK/ERROR messages, and the framework prose that describes them now match what the validator actually does. Future validator work should choose the implementation tool to match the verification kind needed, and document the ceiling explicitly when bash is the right tool for part of the job.

#### Out of scope (Phase 7 candidates, documented in `pass-10.md §Phase 7 Work Items`)

- Python-based Timeline parser (Section 1 + Section 3 normalized scene records; anchor-format normalization; span normalization).
- True arithmetic verification (replaces `timeline-arithmetic` marker-hygiene).
- True anchor conflict detection (replaces `timeline-anchor-conflict` pre-labeled surfacing).
- Item-level diff for Sections 2 (Master Calendar) and 4 (Inconsistency Ledger).
- Per-audit table-driven dispatch in `audit-signal-propagation` (currently the validator detects audit names by appendix-heading pattern; a Phase 7 enhancement would read `pass-dependencies.md §4e` programmatically and apply per-audit context modifiers).

---

## v1.7.8 - 2026-04-25

### Added — Phase 6 Wave 3: Field Reconnaissance Prerequisite for Argument-Shaped Runs (CR-4) + Universal Audit Re-Audit

Closes Phase 6 Wave 3 of the model-capability review (see `docs/review-log/2026-04-25_phase-6-implementation-plan.md` Wave 3 = Priorities 2 + 5). With Wave 3, all six Phase 6 priorities are closed and Phase 6 is complete.

#### Priority 2 — Field Reconnaissance Prerequisite (CR-4 closed)

Closes the literature-counterevidence blind spot identified in F4 Stage 2 (`docs/review-log/2026-04-24_tay-stage-2-comparative.md`). Stage 2 documented seven literature-counterevidence misses where competing studies, replication failures, meta-analytic disagreement, and opposing scholarly positions never entered the Findings Ledger because Field Reconnaissance was not prerequisited for argument-shaped runs. Wave 3 establishes Field Recon as a prerequisite (Hard or Auto-recommend before synthesis depending on stakes signal) and Citation Verifier as a Pre-DE Prerequisite for high-stakes argument-shaped runs.

- **`core-editor/references/pass-dependencies.md` §4a** — added two new router-triggered audit rows (Field Reconnaissance and Citation Verifier) with explicit argument-shaped routing definition, high-stakes signal definition, and a why-prerequisite-tier-exists prose block citing F4 Stage 2 evidence (~25 lines).

- **`core-editor/references/pass-dependencies.md` §4c** — added two new tier definitions above the existing four: **Hard Prerequisite** (stronger than Auto-run; gates Tier 2 passes rather than synthesis; used for Field Recon on high-stakes argument-shaped runs) and **Pre-DE Prerequisite** (audit runs before the DE begins; not a DE-internal audit; used for Citation Verifier on high-stakes argument-shaped runs). Both definitions include explicit decline-path semantics (terminate or downgrade-with-disclosure; silent omission forbidden). The header sentence updated to reflect the six-tier ordering. ~10 lines added.

- **`core-editor/references/pass-dependencies.md` §4f** — tier-ordering block extended from four tiers to six (Hard Prerequisite > Pre-DE Prerequisite > Auto-run > Auto-recommend before synthesis > Auto-recommend > Recommend). Added a Hard Prerequisite ordering note explaining why these tiers sit above Auto-run (pass dependencies vs. synthesis dependencies). Added two new edge cases (8 + 9) covering Hard Prerequisite and Pre-DE Prerequisite decline forks. ~12 lines added.

- **`specialized-audits/references/craft/research-field-recon.md`** — added Prerequisite Mode for Argument-Shaped Runs section after Core principle paragraph (~50 lines). Documents two prerequisite tiers (Hard Prerequisite when high-stakes signal present; Auto-recommend before synthesis otherwise), the four-class literature-counterevidence focus (competing studies / counter-citations / replication failures / opposing scholarly positions), the canonical artifact (`Field_Reconnaissance_Report.md`) and how the argument-engine passes (Dialectical Clarity / Argument Red Team / Argument Evidence Deep-Dive / Synthesis) consume it, the decline path (terminate or downgrade-with-disclosure), and when Wave-2-sibling mode still applies (fiction, narrative nonfiction, memoir, re-invocations).

- **`specialized-audits/references/craft/research-citation-verifier.md`** — added Pre-DE Prerequisite Mode subsection inside §Activation (~25 lines). Documents the Pre-DE Prerequisite tier semantics (runs before any Tier 1 pass; produces `Citation_Ledger.md` consumed by argument-engine passes; not a DE-internal audit), the rationale (citation integrity is an evidentiary precondition for argument analysis, not a finding within it), the decline path (terminate or downgrade-with-disclosure naming "citation provenance not verified"), and the lower-stakes case (Citation Verifier remains available via existing activation paths and direct `/research citation-verifier`).

- **`core-editor/references/run-synthesis.md`** — added a mandatory blind-spot disclosure paragraph inside Step 3 (Blind Spot / Absence Inventory) covering declined Field Reconnaissance on argument-shaped runs (~6 lines). The disclosure must name what is unsurveyed (competing studies, counter-citations, replication failures, opposing scholarly positions) and what the absence implies for synthesis confidence (the argument engine operated against a manuscript-internal claim graph rather than a literature-aware one). Parallel disclosure rule for declined Pre-DE Citation Verifier on high-stakes runs. Appendix A description extended to require the disclosure in editorial-letter Diagnostic Detail (~3 lines).

#### Priority 5 — Universal Audit Re-Audit (Outcome A: keep universal)

Phase 3 inventory classified Stakes / Decision Pressure / Scene Turn as UNPROVEN-keep universal, with Phase 6 instructed to re-audit against fixture data. Wave 3 verifies and ratifies universal status.

- **`specialized-audits/SKILL.md` §Universal Audits** — added Universal-status criterion (~2 lines: three-criterion definition matching the §4c Audit Tier Promotion Criteria pattern from Wave 2) and Universal status verification block dated 2026-04-25 (~8 lines: cross-model parity from Phase 3 §17; cross-fixture material findings on canonical fixtures F1/F2/F3/F4; computational-cost reasoning; demotion candidates considered and rejected — Scene Turn for argument-shaped runs was the closest demotion candidate, rejected because the audit self-attenuates on propositional material without producing false positives). Each of the three universal-audit table rows updated to reference verification status with date and fixture set. ~15 lines net.

- **`specialized-audits/references/craft/stakes-system.md`** — added Universal status verification line in frontmatter under audit classification (~2 lines).

- **`specialized-audits/references/craft/decision-pressure.md`** — added Universal status verification line in frontmatter under audit classification, with explicit note that the audit applies fully to argument-shaped runs (~2 lines).

- **`specialized-audits/references/craft/scene-turn.md`** — added Universal status verification line in frontmatter under audit classification, with explicit note about self-attenuation on purely propositional argument-shaped sections (~2 lines).

Outcome A (keep universal) chosen over Outcome B (demote to baseline-recommend with explicit opt-out). Verification basis: cross-model parity (Phase 3 §17 — both baseline and comparator models correctly fire all three on parity sets); cross-fixture material findings on canonical fixtures F1/F2/F3/F4; computational cost is low because the audits run inside the same context as their finding-trigger passes (Pass 1 / Pass 5 / Pass 7); the convergence-trigger contribution to the underdiagnosis-retry loop is material. No demotions or tier changes; universal status holds.

#### Files

- `plugins/apodictic/skills/core-editor/references/pass-dependencies.md` — §4a Field Recon + Citation Verifier router rows with argument-shaped routing definition, high-stakes signal definition, and CR-4 closure rationale (~25 lines); §4c Hard Prerequisite + Pre-DE Prerequisite tier definitions with header sentence updated to six-tier ordering (~10 lines); §4f tier-ordering block extended to six tiers, Hard Prerequisite ordering note, edge cases 8 and 9 (~12 lines). Net ~+47 lines.
- `plugins/apodictic/skills/core-editor/references/run-synthesis.md` — Step 3 Blind Spot / Absence Inventory mandatory disclosure paragraph for declined Field Recon on argument-shaped runs and parallel rule for Pre-DE Citation Verifier (~6 lines); Appendix A description extension naming literature-counterevidence and citation-provenance blind spots (~3 lines). Net ~+9 lines.
- `plugins/apodictic/skills/specialized-audits/SKILL.md` — Universal-status criterion + verification block + updated table rows for the three universal audits (~15 lines net).
- `plugins/apodictic/skills/specialized-audits/references/craft/research-field-recon.md` — new Prerequisite Mode for Argument-Shaped Runs section between Core principle and Part 1 (~50 lines).
- `plugins/apodictic/skills/specialized-audits/references/craft/research-citation-verifier.md` — new Pre-DE Prerequisite Mode subsection inside §Activation (~25 lines).
- `plugins/apodictic/skills/specialized-audits/references/craft/stakes-system.md` — Universal status verification line in frontmatter (~2 lines).
- `plugins/apodictic/skills/specialized-audits/references/craft/decision-pressure.md` — Universal status verification line in frontmatter (~2 lines).
- `plugins/apodictic/skills/specialized-audits/references/craft/scene-turn.md` — Universal status verification line in frontmatter (~2 lines).
- Version bumped via `scripts/bump-version.sh 1.7.8` (Wave 2 may bump to 1.7.7 in coordination; Wave 3 ships as 1.7.8).

Total prose change: ~152 lines added across framework files. No validators added (existing `audit-signal-propagation` validator covers post-Field-Recon propagation; activation policy is documented contract). No fixture changes (Field Recon prerequisite would have surfaced F4 Stage 2 blind spots had it been in place; verification by trace analysis per Phase 6 plan §Priority 2 acceptance criterion 6).

#### Out of scope (Phase 7 candidates)

- Optional `validate.sh argument-recon-prerequisite <intake_file> <audit_invocation_log>` validator that would verify, for argument-shaped intake, either Field Recon ran or a blind-spot disclosure exists in the synthesis. Deferred to Phase 7.
- Pass 10 Timeline cross-fixture eval coverage (still deferred from Wave 1).
- Cross-model fixture re-evaluation against the §4e propagation table (Wave 2 territory; Wave 3 does not affect this).

#### Phase 6 closure

Wave 3 closes the final two priorities. All six Phase 6 priorities are now complete:

- **Wave 1 (v1.7.6):** Priority 1 (CR-5 Pass 10 Timeline) + Priority 6 (CR-7 Audit Tier Precedence Rule).
- **Wave 2 (v1.7.7):** Priority 3 (CR-8 Audit-Signal Propagation Table) + Priority 4 (CR-3 Auto-recommend tier re-audit + Priority Queue).
- **Wave 3 (v1.7.8):** Priority 2 (CR-4 Field Reconnaissance Prerequisite) + Priority 5 (Universal Audit Re-Audit).

Phase 6 is closed. All four Codex critique items (CR-3, CR-4, CR-5, CR-7, CR-8) plus the Phase 3 Universal Audit re-audit are resolved.

---

## v1.7.7 - 2026-04-25

### Added — Phase 6 Wave 2: Audit-Signal Propagation Table (CR-8 operationalized) + Auto-Recommend Tier Re-Audit + Priority Queue (CR-3 closed)

Closes Phase 6 Wave 2 of the model-capability review (see `docs/review-log/2026-04-25_phase-6-implementation-plan.md` Wave 2 = Priorities 3 + 4, `docs/review-log/2026-04-24_phase-2-archaeology.md` for CR-3 promotion-drift evidence, `docs/review-log/2026-04-25_phase-3-codex-critique-adjudication.md` §3 + §6 for CR-8 evidence, and Phase 4's canonical Audit-Signal Propagation Rule in `core-editor/references/run-synthesis.md §Step 2` which Wave 2 operationalizes per-audit). Wave 2 ships alongside Wave 3 (v1.7.8); both edit `pass-dependencies.md §4` and were coordinated in parallel. Version files were already bumped to 1.7.8 by Wave 3; the v1.7.7 entry here documents the Wave 2 changes for changelog continuity.

#### Priority 3 — Audit-Signal Propagation Table (CR-8 operationalized)

Phase 4 established the canonical Audit-Signal Propagation Rule (`run-synthesis.md §Step 2`) that defines the propagation taxonomy (Must-Fix floor → synthesis Must-Fix; hard gate → synthesis Must-Fix; HIGH → synthesis Must-Fix or Should-Fix per audit context; MEDIUM → Should-Fix; LOW → Could-Fix). Wave 2 builds the per-audit table the rule defers to.

- **`core-editor/references/pass-dependencies.md` §4e — Audit-Signal Propagation Table** — new section between §4d and §4f (~140 lines). Six subsections covering Universal audits (Stakes / Decision Pressure / Scene Turn), High-priority craft audits (Compression / Reception Risk / Banister / AI-Prose / Female Interiority / Interiority Preservation), Argument cluster (Dialectical Clarity / Red Team / Persuasion / Evidence / Adversarial Evidence Review / Field Recon / Citation Verifier), Specialized craft audits (Character Architecture / Emotional Craft / Literary Craft / Force Architecture / Series Continuity / Series Composite Novel / Shelf Positioning / Short Fiction), Genre audits (Comedy/Satire / Historical / Memoir/CNF / Narrative NF / Fan Fiction / SFF Worldbuilding / Horror / Supernatural Horror / Grimdark / Mystery-Thriller), and Tag audits (Consent Complexity / Erotic Content / Queer Romance / Cozy / Philosophical). Approximately 95 rows total; each row maps one audit-internal signal class to one synthesis severity, with explicit context modifier and source-file reference. Includes prologue explaining how to read each row, validator integration with Phase 4's `audit-signal-propagation`, override-path reminder, and footer with default mapping (canonical rule's column-2 fallback) for un-enumerated audits.

- **CR-8 closure cases enumerated explicitly** in §4e: Compression Must-Fix floor → synthesis Must-Fix (always; primary CR-8 case); Reception Risk Alert post-calibration → synthesis Must-Fix (when not artifact-of-method); Reception Risk coercion-marked Alert → synthesis Must-Fix + retry-loop trigger #2 (refines default per cross-step trigger); Banister HIGH-confidence rhetorical-fairness failure → synthesis Must-Fix when thematic-coherence-load is high (refines default per Codex §9.4 closure). Each closure case carries explicit context modifiers and Override column annotations.

- **`core-editor/references/run-synthesis.md` §Step 2** — "Per-audit specifics live elsewhere" sentence updated. Old text pointed to "Phase 6 work" with "until that table exists, treat the column-2 mapping above as the default." New text points to `pass-dependencies.md §4e`, names the validator, and clarifies that un-enumerated audits fall back to the column-2 default (so the canonical rule still governs un-enumerated audits via the default). +1 line net.

- **`core-editor/references/pass-dependencies.md` §4 header** — "Audit-signal propagation" paragraph updated to point to §4e instead of "Phase 6 work." +0 lines net (sentence rewrite).

- **`specialized-audits/SKILL.md` §How to Use** — existing "Severity signals from audits propagate" paragraph extended with a one-sentence pointer to `pass-dependencies.md §4e` and audit-author guidance ("add a §4e row at registration time; un-enumerated audits fall back to the canonical default mapping"). +1 sentence.

No new validator. The existing Phase 4 `audit-signal-propagation` validator covers the new table without modification; it reads §4e's per-audit context modifiers as refinements to the canonical default. Validator extension to read context modifiers programmatically is deferred to Phase 7.

#### Priority 4 — Auto-Recommend Tier Re-Audit + Priority Queue (CR-3 closed)

Phase 2 archaeology surfaced cfaadef's batch promotion of five audits (Compression / Female Interiority / Scene Turn / Interiority Preservation / Decision Pressure) from Recommend to Auto-recommend before synthesis without an explicit promotion criterion. Wave 2 closes the criterion gap and verifies all existing tier assignments.

- **`core-editor/references/pass-dependencies.md` §4a Router-triggered audits** — added Tier verification subsection at the top of §4a (~3 lines). Result: existing tiers hold. Auto-recommend before synthesis tier on Reception Risk and Consent Complexity confirmed against Phase 2 archaeology (the obligation tier's defining condition — absent these audits, the run records explicit blind spots — is met). Auto-run audits (Constraint=ai → AI-Prose; Erotic Content; Memoir; Narrative NF) confirmed against §4c Auto-run definition. No router-tier promotions or demotions.

- **`core-editor/references/pass-dependencies.md` §4b Finding-triggered audits** — added Tier verification subsection at the top of §4b (~5 lines). Result: existing tiers hold. The five cfaadef-promoted audits (Compression / Female Interiority / Scene Turn / Interiority Preservation / Decision Pressure) verified against the new §4c Audit Tier Promotion Criteria — promotions justified. Demotion candidates considered and rejected: each catches undetectable-by-passes-alone omissions; blind-spot disclosure is non-equivalent to running them. Recommend tier on Character Architecture / Emotional Craft / Banister and others remains: each catches a class of issue that *could* be inferred from passes, so opt-in is the right tier. Banister-for-thematic-runs candidate flagged in Phase 3 documented in §4e propagation entry but tier stays at Recommend pending stronger Phase 7 evidence.

- **`core-editor/references/pass-dependencies.md` §4c — new Audit Tier Promotion Criteria subsection** (~16 lines). Documents the three-criterion test for Auto-recommend before synthesis status: (1) audit has named hard gates or audit-internal Must-Fix floors; (2) audit catches a class of issue undetectable by passes alone; (3) blind-spot disclosure is non-equivalent to running the audit. Documents the Auto-run derivation (all three above + definitional-or-prerequisite-signal); Auto-recommend derivation (criterion 1 + partial criterion 2, criterion 3 fails). Establishes the logging requirement: each promotion (or principled non-promotion) recorded in the changelog entry that introduces it. The §4a/§4b verification subsections at the start of each table document the criterion's application to existing audits.

- **`core-editor/references/pass-dependencies.md` §4d — Presentation format & Priority Queue** — section title updated; section restructured to add explicit Priority Queue specification (~30 lines). Four ordering rules in sequence: (1) higher tier fires first; (2) within tier, higher audit-internal severity fires first (hard gate beats Must-Fix floor beats HIGH/Alert beats MEDIUM/Flag beats LOW/Note); (3) within severity, higher signal count fires first; (4) tie-breaking alphabetical by audit name. Re-prompt suppression rule cross-references §4f (CR-7); tier resolution precedes queue ordering. Three worked examples illustrating: same-tier different-internal-severity (Female Interiority vs Scene Turn after Pass 5); two Auto-recommend-before-synthesis audits at different signal classes (Reception Risk Alert vs Compression Must-Fix floor after Pass 1); two Recommend audits with different signal counts (Dialectical Clarity vs Banister after Pass 9).

#### Files

- `plugins/apodictic/skills/core-editor/references/pass-dependencies.md` — §4 header propagation paragraph rewrite (0 net); §4a verification subsection (~3 lines); §4b verification subsection (~5 lines); §4c Audit Tier Promotion Criteria subsection (~16 lines); §4d Priority Queue + worked examples (~30 lines); §4e Audit-Signal Propagation Table (~140 lines, ~95 audit rows). Net ~+194 lines.
- `plugins/apodictic/skills/core-editor/references/run-synthesis.md` — §Step 2 "Per-audit specifics live elsewhere" sentence rewrite (+1 line net).
- `plugins/apodictic/skills/specialized-audits/SKILL.md` — §How to Use propagation paragraph extended with §4e pointer + audit-author guidance (+1 sentence).
- Version files — already bumped 1.7.6 → 1.7.8 by Wave 3 in parallel; Wave 2's nominal v1.7.7 slot is documented here without re-bumping (Wave 2 + Wave 3 share a same-day release window).

Total prose change: ~196 lines added across framework files. No validators added (existing `audit-signal-propagation` from Phase 4 covers the table without modification). No fixture changes (CR-3 closure is documentation; CR-8 operationalization is documentation; the validator behavior on canonical fixtures F1/F2/F3/F4 from Phase 4 Wave 3 is unchanged — §4e refines per-audit defaults but the canonical rule still applies for un-enumerated audits).

#### Out of scope (Phase 7 candidates)

- Optional `audit-signal-propagation` validator extension to read per-audit context modifiers from §4e and check audit-context propagation programmatically. Defer to Phase 7.
- Optional `validate.sh audit-tier-criterion <audit_invocation_log>` validator to verify every audit's promotion-criterion satisfaction is logged. Defer to Phase 7.
- Cross-model fixture re-evaluation against §4e: Codex's documented under-propagation of Compression / Reception / Banister signals (per Codex critique adjudication §3) would now be surfaced as validator failures under §4e. Re-running the cross-model fixtures to confirm is downstream eval work, not Wave 2 scope.

---

## v1.7.6 - 2026-04-25

### Added — Phase 6 Wave 1: Pass 10 Timeline Enhancement (CR-5) + Audit Tier Precedence Rule (CR-7)

Closes Phase 6 Wave 1 of the model-capability review (see `docs/review-log/2026-04-25_phase-6-implementation-plan.md` Wave 1 = Priorities 1 + 6, `docs/review-log/2026-04-25_pass-10-timeline-enhancement-spec.md` for the lifted Pass 10 schema, and `docs/review-log/2026-04-25_phase-3-codex-critique-adjudication.md` §5 for CR-7 origin). Implements the first live instance of the Pass-10-Class Rolling Structured Artifacts pattern named in Phase 4 (`Timeline.md`), and resolves the §4 audit-tier ambiguity surfaced in the Codex critique adjudication.

#### Pass 10 Timeline Artifact (CR-5 closed; Pass-10-Class first live instance)

- **`core-editor/references/pass-10.md`** — new reference file (~150 lines). Documents the eight-section Timeline artifact schema lifted from `docs/review-log/2026-04-25_pass-10-timeline-enhancement-spec.md`:
  1. Event Ledger (tabular, one row per scene)
  2. Master Calendar (day/week reconstruction)
  3. Temporal Marker Inventory (every explicit temporal marker)
  4. Inconsistency Ledger (paradox / drift / ambiguity classification)
  5. Ambiguity Ledger (structural vs. accidental ambiguity)
  6. Revision-Drift Hot Spots (repair recommendation classes)
  7. Recommended Anchor Set (3-7 author decisions)
  8. Diff Notes (input to the timeline-diff validator)

  Also documents naming convention (`Timeline.md` at project root), migration / backward compatibility (existing projects get first Timeline.md on next Pass 10 run with empty Section 8), validator integration (three new validators below), and synthesis integration (Section 4 counts feed severity propagation).

- **`core-editor/references/pass-dependencies.md` §1 Tier 1** — Pass 10 row updated. Pass 10 now produces both a run-folder artifact (existing Entity Tracking output: Rule Ledger + Entity Table + legacy chronology) and a project-level rolling artifact (`Timeline.md`). Added an explanatory paragraph naming Timeline as the first live instance of the Pass-10-Class Rolling Structured Artifacts pattern, listing the three paired validators, and pointing to the canonical schema in `references/pass-10.md`. ~5 lines added.

- **`core-editor/references/run-synthesis.md` §Step 2 Canonical Audit-Signal Propagation Rule** — extended with a new Pass-10-Class artifact integration subsection (~14 lines). Timeline Inconsistency Ledger counts feed synthesis severity via the same canonical rule that governs audit signals: ≥1 paradox → Must-Fix candidate (timeline coherence); ≥3 drifts → Should-Fix candidate (revision-drift hygiene); load-bearing ambiguity → Author Decision. Names the artifact-class-agnostic principle: severity propagation is the same whether the signal originates in an audit findings file or a rolling structured artifact (`Argument_State.md`, `Series_State.md`, `Timeline.md`, future `Plot_Spine.md`).

- **`core-editor/SKILL.md` §Project Integration / Pass-10-Class Rolling Structured Artifacts** — Timeline.md instance status updated from "(Phase 6 implementation per spec)" to "(live; schema in `references/pass-10.md`; three mechanical validators in `scripts/validate.sh`: `timeline-diff`, `timeline-arithmetic`, `timeline-anchor-conflict`)". Closing paragraph updated to mark Timeline as the first live Pass-10-Class instance landed under the named pattern.

#### Three Mechanical Validators for Timeline (Pass-10-Class instance)

Three new validators added to `scripts/validate.sh`. All three honor body-only override markers and Section-8-vs-body discipline (Section 8 is the appendix-equivalent for the Timeline artifact; markers placed there are non-canonical) parallel to the Phase 4 pattern.

- **`scripts/validate.sh timeline-diff <prior_timeline> <current_timeline>`** — surfaces every changed / removed / added Event Ledger row between two Timeline artifacts. Verifies Section 8 (Diff Notes) annotates each diff. Exit 0 if no diff exists, diff is documented in Section 8, or body override marker present; exit 1 if undocumented diff. ~110 lines including self-test (5 cases: positive identical, negative undocumented diff, documented diff, body override, Section-8-only override).

- **`scripts/validate.sh timeline-arithmetic <timeline_file>`** — verifies span calculations sum correctly. Detects negative gaps (revision broke ordering) and explicit conflict markers in Event Ledger rows. Exit 0 if clean; exit 1 if conflicts detected and no body override. ~90 lines including self-test (5 cases: positive clean, negative gap, anchor conflict marker, body override, Section-8-only override).

- **`scripts/validate.sh timeline-anchor-conflict <timeline_file>`** — identifies pre-flagged anchor contradictions / paradoxes in Section 3 (Temporal Marker Inventory). Surfaces candidates (per Pass 10 spec §Risks: validators surface candidates; Pass 10 model judgment classifies). Exit 0 if no candidates; exit 1 if candidates surfaced and no body override. ~95 lines including self-test (5 cases: positive distinct anchors, negative contradiction marker, paradox marker, body override, Section-8-only override).

Override marker syntax (one per validator, body-only honored):

```
<!-- override: timeline-diff-undocumented — <one-sentence rationale> -->
<!-- override: timeline-arithmetic-conflict — <one-sentence rationale> -->
<!-- override: timeline-anchor-conflict — <one-sentence rationale> -->
```

All three validator self-tests pass on the canonical 5-case fixture set per validator. Five Phase 4 validator self-tests (severity-floor, audit-signal-propagation, underdiagnosis-triggers, ledger-consolidation, decision-layer-check) remain green — no regressions.

#### Audit Tier Precedence Rule (CR-7 closed)

- **`core-editor/references/pass-dependencies.md` §4f** — new Audit Tier Precedence Rule subsection (~32 lines). Documents the highest-obligation-wins rule: Auto-run > Auto-recommend before synthesis > Auto-recommend > Recommend. Enumerates seven edge cases (router Auto-run + finding Recommend → Auto-run; router Auto-recommend + finding Auto-recommend before synthesis → promoted; two finding-triggers at Auto-recommend before synthesis → deduplicated; multi-pass Recommend triggers → no promotion; user-declined-at-Recommend later promoted by finding-trigger → re-prompt with new rationale; user-declined-at-Auto-recommend-before-synthesis later trigger → no re-prompt, blind-spot disclosure persists; tier-precedence vs. priority-queue interaction).

- **Cross-references added in §4a, §4b, §4c, §4d** (one-line pointers each, ~4 lines total). §4a: router-triggered audits use §4f when also finding-triggered. §4b: finding-triggered audits use §4f when also router-triggered or fired by multiple passes. §4c: tier definitions establish the §4f ordering. §4d: priority queue applies *after* tier resolution per §4f.

Closes Codex critique §5 (CR-7) — the §4 ambiguity that the same audit could surface through router-triggered (§4a) and finding-triggered (§4b) paths at different obligation levels with no canonical resolution rule.

#### Files

- `plugins/apodictic/skills/core-editor/references/pass-10.md` — new reference file (~150 lines).
- `plugins/apodictic/skills/core-editor/references/pass-dependencies.md` — §1 Tier 1 Pass 10 row + Pass-10-Class explanatory paragraph (~5 lines); §4a/§4b/§4c/§4d cross-reference pointers (~4 lines); §4f new Audit Tier Precedence Rule (~32 lines). Net ~+41 lines.
- `plugins/apodictic/skills/core-editor/references/run-synthesis.md` — §Step 2 Pass-10-Class artifact integration subsection (~14 lines added).
- `plugins/apodictic/skills/core-editor/SKILL.md` — Pass-10-Class subsection Timeline-instance status updated (~3 lines net).
- `plugins/apodictic/scripts/validate.sh` and `scripts/validate.sh` — three new validator commands (`timeline-diff`, `timeline-arithmetic`, `timeline-anchor-conflict`) added before the final `*)` case (~295 lines total including self-tests); usage block extended; doc-comment block extended (~30 lines).
- Version files bumped 1.7.4 → 1.7.6 via `scripts/bump-version.sh 1.7.6` (Phase 5 had not bumped to 1.7.5 yet at Wave 1 execution time; the direct bump to 1.7.6 is documented as a coordination note here for the eventual Phase 5 Wave 1.7.5 retrofit).

#### Out of scope (Phase 6 Wave 2+)

- Priority 3 — Audit-Signal Propagation Table (CR-8 operationalization): per-audit propagation entries deferred to Wave 2.
- Priority 4 — Auto-recommend tier re-audit (CR-3): tier reassignment deferred to Wave 2.
- Priority 2 — Field Reconnaissance prerequisite for argument-shaped runs (CR-4): deferred to Wave 3.
- Priority 5 — Universal audit re-audit: deferred to Wave 3.
- Pass 10 Timeline cross-fixture eval coverage (canonical fixtures F1/F2/F3/F4): the Wave 1 release ships the schema + validators + synthesis integration; live-fixture re-runs are downstream eval work.

---

## v1.7.5 - 2026-04-25

### Added — Phase 5: Quality-Risk Mode Triggers + Mode-Conditional Re-Grounding + Focus Map Decision Framework

Closes Phase 5 of the model-capability review (see `docs/review-log/2026-04-25_phase-5-implementation-plan.md`). Three priorities: (1) Quality-Risk Mode Selection layered atop token-fit floor (CR-2 closed); (2) Pre-Pass Re-Grounding restructured into three named blocks (universal contract-hash + standard-context full re-read + single-agent anchor confirmation); (3) Focus Map cross-mode decision framework documented; empirical test deferred to a follow-on workstream.

#### Priority 1 — Quality-Risk Mode Selection (CR-2 closed)

- **`core-editor/references/run-core.md` — new §Quality-Risk Mode Selection subsection** (placed between §Context Window Detection and §Single-Agent Mode). Specifies five enumerated triggers (Q1 consent/governance; Q2 argument-shaped nonfiction with high stakes; Q3 many POVs / non-linear; Q4 prior thin synthesis; Q5 submission readiness), each with a detectable predicate, escalation target, and named rationale. Stacking ceiling = swarm. Override path documented (explicit user acknowledgment recorded as `quality_risk_override` in run metadata).
- **`core-editor/references/run-core.md` §Pre-flight Diagnostics** — appended a one-sentence pointer noting the token-fit recommendations are the floor, with quality-risk overlay above.
- **`core-editor/references/run-core.md` §Single-Agent / §Sequential / §Hybrid / §Swarm Mode "When to use" subsections** — appended one-line pointers to §Quality-Risk Mode Selection.
- **`core-editor/references/run-core.md` §Execution Protocol step 3** — replaced single-line selection rule with three-clause layered rule (token-fit floor → quality-risk overlay → final mode = max(floor, recommendation), user override takes precedence).
- **`core-editor/references/intake-router-runtime.md` §2b** — added a Quality-risk overlay paragraph documenting router-side detection of Q1-Q5 triggers from intake fields and contract draft, with cross-reference to `run-core.md` §Quality-Risk Mode Selection.
- **`scripts/validate.sh quality-risk-triggers <contract_file> [<diagnostic_state_meta_file>]`** — new mechanical check (~280 lines including self-test). Detects Q1-Q5 triggers from contract artifact and (for Q4) optional `Diagnostic_State.meta.json`. Emits per-trigger fired set + escalation target (none / hybrid / swarm). Per-trigger override marker support: `<!-- override: quality-risk-Q[1-5] — <rationale> -->` in contract body. Self-test mode covers one positive (clean fiction), five negative (one per Q1-Q5), one override case. All self-tests PASS.

Closes CR-2 (HIGH confidence — execution mode auto-selection was token-fit only; now layered with quality-risk overlay). The token-fit floor is preserved (mode definitions unchanged); quality-risk only escalates upward. Coordinates with Phase 6 CR-4 (Q2's rationale anticipates Field Reconnaissance prerequisite for argument-shaped runs).

#### Priority 2 — Pre-Pass Re-Grounding mode-conditional restructure

- **`core-editor/references/run-core.md` §Pre-Pass Re-Grounding** — restructured single-protocol re-grounding into three named blocks:
  - **Block A — Contract Integrity Check (Universal, all modes).** Mechanical SHA-256 hash compare against `contract_hash` in `Diagnostic_State.meta.json`. Mode-independent Tool-invocable check; fires in single-agent, sequential, hybrid, and swarm. Reuses existing `validate.sh contract-check`.
  - **Block B — Full Re-Grounding (sequential / hybrid / swarm).** Re-read of contract's controlling idea + anti-idea + non-negotiables and accumulated Findings Ledger before each evaluative pass. Compensation for context salience decay on standard-context per-pass subagent dispatch. Existing behavior preserved verbatim.
  - **Block C — Anchor Confirmation (single-agent large-context).** Lighter protocol: contract integrity check (Block A) + one-line restatement of controlling idea + anti-idea + non-negotiables from active context + review of most recent ledger entry. No fresh text re-load (decorative on a 1M-context single-agent run where anchors remain in attention).
- **Block-selection table** documented; Block A is universal regardless of mode. Mode escalation (per Priority 1) at run start re-runs the selection. Future mid-run escalation handler (ROADMAP) is responsible for re-running this selection table.
- No new validator — Block A reuses existing `validate.sh contract-hash` / `validate.sh contract-check` per §Mechanical Validation Protocol.

Salience-decay rationale named explicitly: it is the original failure mode the protocol was designed to counteract; it is real on standard-context per-pass dispatch (Block B) and negligible in single-agent large-context (Block C). The contract-drift check (Block A) is mode-independent because it catches out-of-band file modification, which can happen in any architecture.

#### Priority 3 — Focus Map Architectural Decision Framework

- **`core-editor/references/hybrid-mode.md` — new §Focus Map Architectural Decision Framework (Phase 5)** appended after §Open Questions. Documents the test hypothesis, test design (3 fixtures × 2 arms), target metrics M1-M4 (Severity Honesty, Audit Routing Coverage, Cross-Pass Connection Density, Author Usability), pass-independence guards G1-G2 (Cross-Pass Connection independence; Findings outside Focus Map ≥40%), and acceptance criteria per spec §Phase 5 ("adopt only if M1-M4 improves on ≥2 metrics for ≥2 fixtures, AND G1-G2 satisfied for all fixtures").
- **Default: Focus Map remains hybrid-only** unless future test produces data supporting cross-mode adoption.
- **Test deferred** note: 6 fixture comparisons (3 × 2) is non-trivial scope expansion beyond Phase 5's prose-and-validator priorities. Decision-recording protocol specifies that when the test runs, the data + decision get logged in a date-stamped review-log entry under `docs/review-log/<YYYY-MM-DD>_focus-map-cross-mode-test.md`, and this section gets a "Resolved" annotation.

#### Files

- `plugins/apodictic/skills/core-editor/references/run-core.md` — §Pre-flight Diagnostics token-fit-floor pointer (~1 line); §Quality-Risk Mode Selection new subsection (~30 lines: 5 triggers + stacking + override path + validator pointer); 4 mode "When to use" pointers (~4 lines); §Execution Protocol step 3 layered-rule rewrite (~6 lines); §Pre-Pass Re-Grounding restructured into Blocks A/B/C with selection table (~70 lines, replacing ~12 lines of single-protocol prose). Net ~+100 lines.
- `plugins/apodictic/skills/core-editor/references/intake-router-runtime.md` — §2b Quality-risk overlay paragraph (~10 lines added).
- `plugins/apodictic/skills/core-editor/references/hybrid-mode.md` — §Focus Map Architectural Decision Framework (Phase 5) (~70 lines added after §Open Questions).
- `plugins/apodictic/scripts/validate.sh` and `scripts/validate.sh` — `quality-risk-triggers` command added (~280 lines including self-test).

#### Out of scope (deferred)

- Adaptive Mid-Run Mode Escalation (spec §Phase 5 Task 4) — ROADMAP execution work, not Phase 5 scope.
- Focus Map empirical test runs — deferred to follow-on workstream when bandwidth permits. Decision framework is documented; default (hybrid-only) maintained.
- Phase 6 priorities (Pass 10 Timeline implementation, Field Reconnaissance prerequisite, Auto-recommend tier re-audit) — Phase 6 (parallel implementation in progress, ships as v1.7.6).
- Phase 4 calibration follow-ups C1-C4 (`decision-layer-check` semantics) — Phase 7 or post-review calibration phase.

---

## v1.7.4 - 2026-04-25

### Added — Phase 4 Wave 3: Decision-Layer Validator + Pass-10-Class Pattern + Initial Eval Coverage

Closes Phase 4 of the model-capability review (see `docs/review-log/2026-04-25_phase-4-implementation-plan.md` and `docs/review-log/2026-04-25_phase-4-eval-coverage.md`). Mechanizes Decision-Layer Consolidation counts (Priority 5), names the Pass-10-class artifact pattern as the Phase 6 unblocker (Priority 6), and runs the initial eval coverage check across all 5 Phase 4 validators against canonical Stage 1 fixtures.

#### Decision-Layer Consolidation Validator (Priority 5)

- **`scripts/validate.sh decision-layer-check`** — new mechanical check (~250 lines including self-test). Verifies five contract checks per `core-editor/references/run-synthesis.md §Step 7` (counts) and `core-editor/references/output-policy.md §Mandatory Appendices / §Evidence Density Self-Check` (presence + density):
  1. Protected Elements — 3-6 entries (counts list items, falls back to bolded paragraphs when no list items present).
  2. Author Decisions — 3-7 entries.
  3. Control Questions — exactly 7 entries.
  4. Mandatory Appendices A, B, C — each present as a heading.
  5. Per-Must-Fix evidence density — every Must-Fix mention has ≥2 references (chapter/scene/line/page/audit-code) in the 6-line window.
  Per-check override markers (body-only honored, appendix-only ignored): `<!-- override: decision-layer-protected-elements -->`, `<!-- override: decision-layer-author-decisions -->`, `<!-- override: decision-layer-control-questions -->`, `<!-- override: decision-layer-appendices -->`, `<!-- override: decision-layer-evidence-density -->`. Self-test mode covers one positive case, four negative cases (5 Control Questions; missing Appendix B; 8 Author Decisions; Must-Fix with <2 refs), and two override cases (body marker downgrades; appendix marker does not).
- **`core-editor/references/run-synthesis.md §Step 7`** — added a Mechanical check paragraph naming the validator and the override-marker syntax. Editorial judgment about WHICH elements/decisions/questions appear is preserved at Step 7; counts and structural compliance become mechanical at Step 10. ~6 lines added.
- **`core-editor/references/run-synthesis.md §Step 10`** — collapsed three formerly-redundant bullets (decision-layer completeness, appendix completeness, evidence density) into a single combined bullet that points to `validate.sh decision-layer-check` and the canonical homes in output-policy. Removes inline rule restatement; runtime gate semantics preserved. Net: -3 lines.
- **`core-editor/references/output-policy.md §Mandatory Appendices`** — added a one-line validator-authoritative annotation (parallel to severity-floor's canonical-home annotation). ~2 lines added.
- **`core-editor/references/output-policy.md §Evidence Density Self-Check`** — appended a sentence pointing to `validate.sh decision-layer-check` Check 5 + override marker syntax; preserves the editorial nuance ("downgrade confidence, not severity"). ~1 line appended.

Closes Codex critique §9.4 ("final author-facing consolidation" model-compensation finding) by making counts mechanical. Phase 2 §2.4 numerical invariants (3-6 / 3-7 / exactly 7) preserved as the validator's rule basis.

#### Pass-10-Class Artifact Pattern Naming (Priority 6 — Phase 6 unblocker)

- **`core-editor/SKILL.md §Project Integration`** — added a Pass-10-Class Rolling Structured Artifacts subsection (~22 lines). Names the pattern: project-level rolling artifacts that share five properties (project-level, structured, diffable, validator-paired, synthesis-layer integrated). Lists existing instances (Diagnostic_State, SYNTHESIS, Argument_State, Series_State) and proposed instances (Timeline per Phase 6, Plot_Spine future). Provides Phase 6 Timeline implementation a clear class to instantiate against per `docs/review-log/2026-04-25_pass-10-timeline-enhancement-spec.md` §Cross-application to non-fiction.

Per Phase 3 §Sequencing interlock (b), this completes in Phase 4 to unblock Phase 6.

#### Initial Eval Coverage Check

- **`docs/review-log/2026-04-25_phase-4-eval-coverage.md`** — new review-log entry documenting validator runs against the four canonical Stage 1 fixtures (F1, F2, F3, F4).
- **Headline result:** Wave 1 + Wave 2 validators (severity-floor, audit-signal-propagation, underdiagnosis-triggers, ledger-consolidation) produce expected results — OK on positive cases; FAIL on the negative case (Codex Stage 1's underdiagnosis convergence) the loop was designed to catch. No false-positive cascade.
- **Wave 3 decision-layer-check surfaces three calibration follow-ups** documented in the eval-coverage entry as C1-C4 (Author Decisions count semantics; Protected Elements paragraph form; tier-awareness for argument-DE; evidence-density window width). Per Wave 2 guidance, Phase 4 documents calibration findings without re-tuning; these become Phase 5+ work.
- **Pre-existing Wave 2 bash-arithmetic noise fixed.** `ledger-consolidation` was emitting `[: 0\n0: integer expression expected` warnings when grep -c returned nonzero under `set -euo pipefail`. Same bug pattern was present in three locations of the Wave 2 validator and would have appeared in Wave 3 decision-layer-check. Fixed by routing through `{ grep ... || true; } | head -1 | tr -d ' \n'`. All 5 validator self-tests remain green.

Closes Phase 4 Done Gate criterion 7 (eval coverage). No regression on firewall compliance, evidence specificity, severity honesty, or audit-routing blind-spot disclosure (binary checks per `docs/eval-harness-spec.md §Binary Checks`).

#### Files

- `plugins/apodictic/skills/core-editor/SKILL.md` — Pass-10-Class Rolling Structured Artifacts subsection in §Project Integration (~22 lines added).
- `plugins/apodictic/skills/core-editor/references/run-synthesis.md` — Step 7 Mechanical check pointer (~6 lines); Step 10 three-bullet collapse to single combined bullet (net -3 lines).
- `plugins/apodictic/skills/core-editor/references/output-policy.md` — §Mandatory Appendices validator-authoritative annotation (~2 lines); §Evidence Density Self-Check validator pointer (~1 line appended).
- `plugins/apodictic/scripts/validate.sh` and `scripts/validate.sh` — `decision-layer-check` command added (~270 lines including self-test); arithmetic-noise fix for `ledger-consolidation` (~4 hunks); arithmetic-noise fix for new `decision-layer-check` helper. Net ~+422 lines (validator host previously had 11 commands, now 12).
- `docs/review-log/2026-04-25_phase-4-eval-coverage.md` — new eval-coverage report.

#### Out of scope (future phases)

- Decision-layer-check calibration follow-ups C1-C4 (Phase 5 or post-review calibration phase).
- Phase 6: Pass 10 Timeline implementation as the next Pass-10-class instance; per-audit propagation table.
- Phase 7: prose compression / dedup of cross-cutting rules (firewall, anti-sycophancy, absence-first canonical statements where deferred).

---

## v1.7.3 - 2026-04-24

### Added — Phase 4 Wave 2: Override Markers, Underdiagnosis Triggers, Findings Ledger Consolidation

Implements the second wave of Phase 4 of the model-capability review (see `docs/review-log/2026-04-25_phase-4-implementation-plan.md` and `docs/review-log/2026-04-25_phase-3-codex-critique-adjudication.md`). Refactors Wave 1's override detection per Joshua's correction (regex ≠ loose detection), closes CR-6 (Underdiagnosis Retry Loop model-judgment language), and closes the Codex-critique-identified gap on Findings Ledger consolidation.

#### Refactor — Wave 1 override detection migrates from regex to structured markers

- **`scripts/validate.sh severity-floor`** — replaced regex-based override detection ("severity floor", "floor override") with HTML-comment marker detection in the letter body. Per-rule markers: `<!-- override: severity-floor-weak-axis -->`, `<!-- override: severity-floor-systemic -->`, `<!-- override: severity-floor-band-cap -->`. Markers in appendix bodies are non-canonical and ignored. Self-test extended with `over1` (body marker downgrades) and `over_appx` (appendix-only marker does not downgrade) cases.
- **`scripts/validate.sh audit-signal-propagation`** — replaced regex-based override detection ("propagation override", "audit-signal rationale") with HTML-comment marker detection in the synthesis body. Per-class markers: `<!-- override: audit-propagation-must-fix -->`, `<!-- override: audit-propagation-hard-gate -->`, `<!-- override: audit-propagation-high -->`. Same body-vs-appendix discipline. Self-test extended with marker cases.
- **`core-editor/references/output-policy.md §Severity Floor Rules`** — extended the override-path paragraph (Wave 1) with marker syntax + body-vs-appendix rule (~9 lines added).
- **`core-editor/references/run-synthesis.md §Step 2 Canonical Audit-Signal Propagation Rule`** — extended the override-path paragraph (Wave 1) with marker syntax + body-vs-appendix rule (~10 lines added).

Rationale: regex on prose gives narrow precision (false negatives when the magic phrase isn't used), not loose detection. Structured markers give the model a low-friction signal to opt into; looseness comes from the model choosing to insert the marker, not from fuzzy prose matching.

#### Underdiagnosis Retry Loop — condition-triggered logic (CR-6)

- **`core-editor/references/run-synthesis.md §Step 9 Conditional Underdiagnosis Retry Loop`** — replaced model-judgment trigger language with six enumerated detectable triggers:
  1. Convergence trigger (3+ artifacts share a mechanism with no synthesis Must-Fix)
  2. Hard-gate trigger (high-risk audit Alert / hard gate without synthesis Must-Fix)
  3. Cross-pass complication trigger (final-third concern in both character + structure passes)
  4. Multi-axis severity trigger (concern spans 2+ severity classes)
  5. Severity-floor trigger (severity-floor validator returns WARN/FAIL)
  6. Propagation trigger (audit-signal-propagation validator returns ERROR/WARN)
  
  Each trigger is detectable from named artifacts (Findings Ledger, Audit Invocation Log, audit findings files, in-progress letter); none rely on model self-judgment. Override marker syntax documented for each trigger; markers must be in letter body, not appendix. Loop semantics specified: fires once per synthesis pass; addressing all triggers (upgrade or override) advances to Step 10. Net change: ~+30 lines (was 5 lines of model-judgment prose, now ~35 lines of enumerated triggers + override syntax).
- **`scripts/validate.sh underdiagnosis-triggers`** — new mechanical check (~210 lines including self-test). Detects all six triggers; per-trigger override marker downgrades ERROR → WARN. Triggers 5 and 6 invoke `severity-floor` and `audit-signal-propagation` for composability. Self-test mode covers one positive case, three negative cases (convergence, hard-gate, final-third), and one override case.
- **`specialized-audits/references/craft/reception-risk.md §7 Severity Hard Gates`** — added one-line pointer noting that Reception Risk Alerts and §7 hard-gate signals propagate to Underdiagnosis Retry Loop trigger #2 in `run-synthesis.md §Step 9`.

Closes CR-6 (HIGH confidence — cross-bias load-bearing convergence #7 in Phase 3 inventory): converts Step 9 from model-emergent trigger detection to artifact-detectable trigger conditions.

#### Findings Ledger Consolidation Contract + Validator (Codex-critique gap)

- **`core-editor/references/run-synthesis.md §Step 2`** — added a new Findings Ledger Consolidation Contract subsection (sister to the Wave 1 Canonical Audit-Signal Propagation Rule). Specifies inputs (raw Ledger Snippets), outputs (consolidated by-mechanism ledger), required transformations (deduplication, cross-reference annotation, severity collation, source-pointer preservation), reduction expectation (≤70% of raw item count), validator invocation, override marker syntax, and single-agent vs. swarm mode application. ~30 lines added.
- **`core-editor/references/run-core.md §Findings Ledger Protocol`** — added one-line consolidation requirement pointing to the canonical contract. Mandatory after pass dispatch, before synthesis begins.
- **`scripts/validate.sh ledger-consolidation`** — new mechanical check (~150 lines including self-test). Verifies four contract checks: (1) consolidation actually happened (raw "Pass N Findings" headers don't appear ≥3 times in concatenation); (2) cross-pass convergence preserved as annotation; (3) severity collation visible when multiple tiers present; (4) reduction ratio ≤70% if raw ledger provided. Override markers downgrade per-check failures to WARN. Self-test mode covers one positive case (consolidated by mechanism), two negative cases (raw concatenation, no convergence annotation), and one override case.

Closes the Codex-critique-identified gap: turning raw pass/audit Ledger Snippets into a consolidated by-mechanism ledger was model-dependent (Opus produced 337-line consolidated ledger; Codex produced 2,558-line raw-aggregate). The contract specifies the consolidation behavior; the validator verifies compliance.

#### Files
- `plugins/apodictic/skills/core-editor/references/output-policy.md` — marker syntax in §Severity Floor Rules override path (~9 lines added).
- `plugins/apodictic/skills/core-editor/references/run-synthesis.md` — marker syntax in §Step 2 Audit-Signal Propagation Rule (~10 lines); Findings Ledger Consolidation Contract subsection in §Step 2 (~30 lines); §Step 9 rewrite from model-judgment to enumerated triggers (net ~+30 lines).
- `plugins/apodictic/skills/core-editor/references/run-core.md` — consolidation requirement pointer in §Findings Ledger Protocol (~3 lines added).
- `plugins/apodictic/skills/specialized-audits/references/craft/reception-risk.md` — Step 9 trigger pointer on §7 (~3 lines added).
- `plugins/apodictic/scripts/validate.sh` and `scripts/validate.sh` — `severity-floor` and `audit-signal-propagation` refactored to marker-based override detection; two new commands added (`underdiagnosis-triggers`, `ledger-consolidation`) with self-test modes. Net ~+360 lines (validator host previously had 9 commands, now 11).

#### Out of scope (Phase 4 later waves)
- Decision-Layer Consolidation validator (Priority 5 in revised plan).
- Pass-10-class artifact pattern naming (Priority 6 in revised plan; Phase 6 unblocker, may be deferred to Phase 7).
- Per-audit propagation table (Phase 6 work; Wave 1 propagation rule + Wave 2 marker discipline together establish the specification basis).

---

## v1.7.2 - 2026-04-24

### Added — Phase 4 Wave 1: Severity-Floor Consolidation + Audit-Signal Propagation

Implements the first wave of Phase 4 of the model-capability review (see `docs/review-log/2026-04-25_phase-4-implementation-plan.md` and `docs/review-log/2026-04-25_phase-3-codex-critique-adjudication.md`). Closes CR-1 (severity-floor triplication) and CR-8 (audit-internal severity signals had no canonical synthesis propagation rule).

#### Severity-Floor Canonical Home + Validator (CR-1)

- `core-editor/references/output-policy.md §Severity Floor Rules` — designated as the canonical home with a one-line annotation. Added an explicit override-with-rationale path (Appendix B documents any deviation; absence of rationale blocks synthesis). Three numerical rules unchanged (Phase 2 archaeology preserved).
- `core-editor/references/run-synthesis.md §Step 10 Pre-Output Verification` — replaced the duplicate severity-floor restatement bullet with a pointer to the canonical home and a validator-call instruction. Runtime protocol (when the check fires, what blocks delivery) preserved.
- `specialized-audits/references/craft/reception-risk.md §7 Severity Hard Gates` — added an explicit relation-to-canonical statement clarifying that the five reception-specific hard gates are additive (audit-internal severity-event triggers) and never substitute for the framework-level floors. Hard-gate table unchanged.
- `scripts/validate.sh severity-floor` — new mechanical check (~110 lines, including self-test). Verifies the three rules; advisory output (WARN/ERROR/OK); supports an override-rationale path that downgrades ERROR to WARN when Appendix B documents the deviation. Self-test mode (`--self-test`) covers one positive case and three negative cases (one per rule).

#### Audit-Signal Propagation Rule + Validator (CR-8)

- `core-editor/references/run-synthesis.md §Step 2 Audit Finding Consolidation` — added a Canonical Audit-Signal Propagation Rule subsection. Establishes the propagation taxonomy (audit-internal Must-Fix floor → synthesis Must-Fix; hard gate → Must-Fix; HIGH/Alert → MF or SF; MEDIUM/Flag → SF; LOW/Note → CF). Names the validator and the override-with-rationale path. Distinguishes the canonical taxonomy from per-audit specifics (Phase 6 propagation table).
- `core-editor/references/pass-dependencies.md §4 Audit Resolver` — added a one-line pointer to the canonical propagation rule and noted that the per-audit propagation table is Phase 6 work.
- `specialized-audits/SKILL.md` — added a one-line pointer in the How to Use section directing readers to the canonical rule for severity-signal propagation.
- `scripts/validate.sh audit-signal-propagation` — new mechanical check (~125 lines, including self-test). Splits the editorial letter into synthesis body and audit appendix to detect when audit-internal hard gates / Must-Fix floors / HIGH-Alert signals fail to propagate to synthesis-layer Must-Fix or Should-Fix. Override-rationale path supported. Self-test mode (`--self-test`) covers one positive case and three negative cases.

#### Files
- `plugins/apodictic/skills/core-editor/references/output-policy.md` — canonical-home annotation + override path (~5 lines added).
- `plugins/apodictic/skills/core-editor/references/run-synthesis.md` — Step 2 propagation rule (~25 lines added); Step 10 severity-floor bullet collapsed to pointer (-2 / +1 lines net).
- `plugins/apodictic/skills/core-editor/references/pass-dependencies.md` — propagation pointer (~2 lines added).
- `plugins/apodictic/skills/specialized-audits/references/craft/reception-risk.md` — relation-to-canonical statement on §7 (~3 lines added; hard-gate table unchanged).
- `plugins/apodictic/skills/specialized-audits/SKILL.md` — propagation pointer in How to Use (~3 lines added).
- `plugins/apodictic/scripts/validate.sh` and `scripts/validate.sh` — two new commands (`severity-floor`, `audit-signal-propagation`) with self-test modes (~235 lines added; validator host previously had 7 commands, now 9).

#### Out of scope (Phase 4 later waves)
- Underdiagnosis Retry Loop conversion to condition-triggered logic (Priority 3 in revised plan; CR-6).
- Findings Ledger consolidation contract / subagent (Priority 4 in revised plan).
- Decision-Layer Consolidation validator (Priority 5 in revised plan).
- Pass-10-class artifact pattern naming (Priority 6 in revised plan; Phase 6 unblocker, may be deferred to Phase 7).
- Per-audit propagation table (Phase 6 work; the canonical rule added here establishes the specification basis).

---

## v1.7.1 - 2026-04-23

> **Backfilled 2026-04-25 during Phase 7 Wave 1 of the model-capability review.** The original release shipped 2026-04-23 without a changelog entry; the gap was flagged in Phase 4 Wave 1 as a deferred hygiene item and closed here per `docs/review-log/2026-04-25_phase-7-implementation-plan.md` §D1. Entry reconstructed from commits `cfaadef`, `7bb9c34`, `9cd8948`, and version-bump commit `6b477d5`.

### Added — Underdiagnosis Hardening + Deficit-First Diagnostic Rule + release.sh build-antigravity step

Tightens synthesis against soft-pedaled diagnosis. The framework now hunts for absence instead of validating presence, installs tripwires when severity-floor logic is incoherent, and blocks delivery on tone-compliance violations. Eleven craft audits gain a Deficit-First Diagnostic Rule opening block; five audits promoted from Recommend → Auto-recommend before synthesis. Closes the v1.7.0 underdiagnosis vector documented in archaeology and motivates the Phase 4 audit-signal propagation + condition-triggered retry-loop work.

#### Synthesis flow tightening (cfaadef)

- **`core-editor/references/run-synthesis.md` Step 3 (new) — Blind Spot / Absence Inventory.** Before root-cause analysis, scan the Findings Ledger to identify what is missing from the text rather than just evaluating what is present on the page. Missing elements (rushed sequence compression, lacking interiority, unsupported choice architecture) leave no explicit textual footprint and are harder to detect; the Absence Inventory makes the omission scan a required gate before triage.
- **`core-editor/references/run-synthesis.md` Step 9 (new) — Conditional Underdiagnosis Retry Loop.** Abort synthesis if severity-floor logic is incoherent, the Reader Stress Test surfaces uncaptured attacks, or live audit blind spots remain unrouted. (v1.7.2 + v1.7.4 + v1.7.9 later refined this loop into the canonical condition-triggered enumerated-trigger form with `validate.sh underdiagnosis-triggers`.)
- **`core-editor/references/run-synthesis.md` Step 13 (new) — Tone Compliance Check.** Wired to `validate.sh tone-check`; blocks letters containing sycophantic superlatives ("masterpiece," "stunning," "flawless," "clean bill," "tour de force," "triumph," "perfection") before delivery.
- **Steps 10, 11, 12 renumbered** to accommodate Step 3 + Step 9 + Step 13 additions.

#### Output policy (cfaadef)

- **`core-editor/references/output-policy.md` rule #5 (new).** A text is only "structurally clean" if Reader Stress Test, Rejection Memo, and Absence Inventory all explicitly fail to surface deep flaws. Codifies the prohibition against asserting structural soundness from absence-of-flag-firing.

#### Pass dependencies — five audits promoted (cfaadef)

Five audits promoted from Recommend → Auto-recommend before synthesis because they catch omission patterns that undermine the whole letter if skipped:
- Compression
- Female Interiority
- Scene Turn
- Interiority Preservation
- Decision Pressure

(Phase 6 Wave 2 §4a/§4b verification confirmed the promotions hold under the formal Audit Tier Promotion Criteria added in §4c.)

#### Craft audits — Deficit-First Diagnostic Rule (cfaadef + 7bb9c34)

Each audit gets a tailored "Deficit-First Diagnostic Rule" opening block directing the auditor to hunt for absence of structural necessity, interiority, or consequence rather than validate presence of fluent prose. Initial six audits in cfaadef; commit 7bb9c34 extended the rule to five additional craft audits with audit-specific tailoring (no cargo-culting):

**Initial six (cfaadef):**
- `craft/ai-prose-calibration.md` — hunt for absence of voice signature.
- `craft/compression-audit.md` — hunt for absence of scene-level granularity.
- `craft/decision-pressure.md` — hunt for absence of choice architecture.
- `craft/female-interiority.md` — hunt for absence of perception → interpretation → judgment in interiority-load scenes.
- `craft/interiority-preservation.md` — hunt for absence of POV interiority during peak-intensity scenes.
- `craft/scene-turn.md` — hunt for absence of goal + change + consequence (Bickham Turn Test).

**Extension five (7bb9c34):**
- `craft/character-architecture.md` — hunt for absence of genuine agency, psychological cost, and internal contradiction under pressure. Distinctive voice does not prove coherent agency.
- `craft/emotional-craft.md` — hunt for absence of the meaning pipeline (perception → interpretation → judgment → impulse). Feeling-words do not prove transmission.
- `craft/stakes-system.md` — hunt for absence of conversion (visible consequence, narrowing options, persistent cost). Signaled peril does not prove stakes architecture.
- `craft/banister.md` — hunt for absence of steelmanned opposition, author self-implication, and conclusions the text could lose to. Voicing multiple positions does not prove epistemic humility.
- `craft/dialectical-clarity.md` — hunt for absence of the inferential bridge (warrant, honest scope, live disagreement). Citing evidence and gesturing at objection does not prove the argument holds.

#### Tooling (cfaadef + 9cd8948)

- **`scripts/validate.sh tone-check` (new subcommand)** — blocks sycophantic superlatives (masterpiece, stunning, flawless, clean bill, tour de force, triumph, perfection). Wired into `run-synthesis.md` Step 13 as a delivery gate.
- **`scripts/release.sh` extended with build-antigravity step (commit 9cd8948).** Adds a `[4/8] Build generated Antigravity workspace` step invoking `scripts/build-antigravity.mjs`, mirroring how `build-codex.mjs` is run. Without this step, bumping the version left the `antigravity/` workspace mirror stale, and the next `release-verify` run failed with "Antigravity workspace is stale." Renumbers subsequent steps and updates the banner total from 7 to 8.

#### Files

- `plugins/apodictic/skills/core-editor/references/run-synthesis.md` — Step 3 (Absence Inventory), Step 9 (Underdiagnosis Retry Loop initial form), Step 13 (Tone Compliance Check) added; subsequent steps renumbered.
- `plugins/apodictic/skills/core-editor/references/output-policy.md` — rule #5 added (structural-clean condition).
- `plugins/apodictic/skills/core-editor/references/pass-dependencies.md` — five-audit promotion (Compression / Female Interiority / Scene Turn / Interiority Preservation / Decision Pressure).
- `plugins/apodictic/skills/specialized-audits/references/craft/{ai-prose-calibration,compression-audit,decision-pressure,female-interiority,interiority-preservation,scene-turn,character-architecture,emotional-craft,stakes-system,banister,dialectical-clarity}.md` — Deficit-First Diagnostic Rule opening block (11 audits total across cfaadef + 7bb9c34).
- `plugins/apodictic/scripts/validate.sh` — `tone-check` subcommand added.
- `scripts/release.sh` — `[4/8] Build generated Antigravity workspace` step added (commit 9cd8948); banner total 7 → 8.
- Mirrors (antigravity/, codex/, APODICTIC-Gemini/public/apodictic-plugin/) regenerated via `build-codex.mjs`, `build-antigravity.mjs`, and rsync.
- Version bumped via `scripts/bump-version.sh 1.7.1` (commit 6b477d5).

#### Originating commits

- `cfaadef` — Underdiagnosis hardening: absence inventory, retry loop, deficit-first audits.
- `7bb9c34` — Extend Deficit-First rule to 5 additional craft audits.
- `9cd8948` — Extend release.sh with build-antigravity step.
- `6b477d5` — Bump version to 1.7.1 for underdiagnosis hardening release.

---

## v1.7.0 - 2026-04-01

### Added — Harness Engineering Improvements

Applies design principles from Anthropic and OpenAI harness engineering research to the APODICTIC development editor. Motivated by three articles: "Harness Design for Long-Running Apps" (Anthropic), "Effective Harnesses for Long-Running Agents" (Anthropic), and "Harness Engineering: Leveraging Codex in an Agent-First World" (OpenAI).

#### Machine-Readable Sidecar State
- `Diagnostic_State.meta.json` — machine-readable sidecar alongside the human-facing `Diagnostic_State.md`
- Enumerated `next_action.key` for reliable resume dispatch (8 valid values: `run_passes`, `run_synthesis`, `run_spot_check`, `deliver`, `revision_round`, `run_audits`, `coaching`, `handoff_reentry`)
- Resume gate reads sidecar for fast structured routing; falls back to parsing markdown for pre-v1.7 projects
- Template: `references/diagnostic-state-meta-template.json`

#### Mechanical Validation
- `scripts/validate.sh` — 6 zero-token invariant checks: contract hash, contract drift, ledger structure, artifact naming, synthesis sections (14 headings as markdown headings), state line count
- Integrated at checkpoints: contract hash at intake, contract drift at pre-pass re-grounding, ledger check after each pass, artifact naming and ledger check at pre-synthesis gate, 14-heading section validation after editorial letter
- Bundled inside the plugin tree (`plugins/apodictic/scripts/`) for Codex compatibility
- Inline fallbacks for hosts that cannot run shell scripts (e.g., ChatGPT)

#### Post-Synthesis Evidence Spot-Check
- Independent verification layer after synthesis: samples 5 claims from the editorial letter and checks them against the manuscript
- Verifies: evidence exists at cited location, diagnosis matches text, fix class matches root cause
- In multi-agent modes, dispatched as a separate subagent for architectural isolation between letter writer and verifier
- Reports findings as a verification block appended to the editorial letter

#### State Gardening Protocol
- Threshold-triggered archival when `Diagnostic_State.md` exceeds 500 lines (advisory at 300)
- Archives to `Diagnostic_State_Archive_[datetime].md` (ISO 8601, minute-resolution, filesystem-safe)
- Compresses completed sessions, resolved handoffs, answered control questions
- Preserves all unresolved material, root causes, triage, author decisions, coaching log

#### Enhanced Resume Gate
- `/start` presents context-aware summary from sidecar: session count, root cause count, revision progress, next action
- "Continue" option resumes from `next_action.key` dispatch table
- State gardening triggered automatically when state exceeds threshold

### Changed — run-core.md Refactored into Three Files

Split `run-core.md` (1,091 → 653 lines) into three files along phase boundaries:

| File | Lines | Content |
|---|---|---|
| `run-core.md` | ~650 | Intake, pass resolution, execution modes, pass specs, Findings Ledger protocol |
| `run-synthesis.md` | ~330 | Audit integration, synthesis processing, editorial letter format, deliverables, evidence spot-check |
| `state-lifecycle.md` | ~130 | State gardening, revision round protocol |

Cross-references updated in: `SKILL.md`, `start.md`, `ready.md`, `submission-readiness.md`, `run-full.md`.

#### Files
- `references/run-synthesis.md` — new
- `references/state-lifecycle.md` — new
- `references/run-core.md` — refactored (synthesis and state sections removed, handoff pointers added)
- `references/diagnostic-state-meta-template.json` — new
- `scripts/validate.sh` — new (repo root + plugin bundle)
- `scripts/preflight.sh` — copied into plugin bundle for Codex compatibility
- `scripts/build-codex.mjs` — updated to require new files and bundled scripts in archive
- `commands/start.md` — updated resume gate with sidecar routing, enumerated dispatch, state gardening
- `SKILL.md` — updated reference table, workflow contract, QA guardrails

---

## v1.1.0 - 2026-03-17

### Added — Submission Readiness Workflow

New unified workflow for "is this ready to submit?" Runs Core DE → Synthesis → Pass 11 → Compression Test and produces a single readiness assessment document.

#### What it adds over standalone Core DE + Pass 11
- **Compression Test** — tests whether the manuscript's identity survives query/synopsis compression. Populates SR-8 (Better Than It Sounds), SR-10 (Spine Amnesia), SR-13 (Arc Substitution), SR-14 (Comp Fragility), SR-15 (Evidence Thinness) from compression evidence.
- **Unified Readiness Assessment** — single document synthesizing diagnostic findings, verdict (READY / CONDITIONALLY VIABLE / NOT READY), market reality, opening conversion gate, and prioritized next steps. Writers no longer need to cross-reference the editorial letter and Pass 11 output.
- **Full SR code vocabulary** — all 15 submission readiness codes populated across Core DE passes and compression test (vs. 7 in Submission Triage).
- **`/ready` command** — direct entry point bypassing the `/start` router's Q1-Q3 sequence.
- **Abbreviated intake** — pre-fills artifact and goal, asks only publication path, query materials, and execution mode.

#### Router integration
- `full_draft + submit + —` route now resolves to Submission Readiness Workflow (was previously a gap).
- `/start` routes here when artifact = `full_draft` and goal = `submit` without time constraint.
- Submission Triage remains the fast path for `constraint:time`.

#### Files
- `commands/ready.md` — new command
- `references/submission-readiness.md` — workflow specification
- `references/intake-router-runtime.md` — gap closed in route map §6

### Added — Context-Aware Execution Mode Selection

APODICTIC now detects the available context window and selects execution mode accordingly.

#### Large-context models (≥1M tokens)
- **Single-agent mode** is the new default: one subagent runs all passes sequentially in a single context. Manuscript loads once; Findings Ledger still written to disk after each pass.
- Viable for manuscripts up to ~200,000 words (estimated load < 600K tokens).
- Token cost: ~240-300K for a 118K-word novel (roughly half of sequential mode).
- Swarm mode remains available for architectural isolation when the user wants maximum analytical depth.

#### Standard-context models (<1M tokens)
- Existing three-mode behavior preserved: sequential / hybrid / swarm.
- No changes to thresholds or routing.

#### Files
- `scripts/preflight.sh` — computes estimated token load, outputs two recommendation tiers
- `references/run-core.md` — new §Context Window Detection, §Single-Agent Mode, updated execution protocol and token cost table
- `references/intake-router-runtime.md` — §2b now has large-context and standard-context versions
- `docs/subagent-architecture-design.md` — status line updated

---

## v1.0.9 - 2026-03-04

### Added — Reception Risk Audit

New specialized craft audit: **Reception Risk** — "How will this land?" Identifies passages, patterns, and structural choices that create cultural, political, or ideological reception risk. Over-inclusive flagging diagnostic for human sensitivity review. Does not tell the author what to write or what to believe; surfaces risk so the author can make informed decisions.

#### Design rationale
Core passes and the Adversarial Stress Test evaluate craft; they do not evaluate how the text will function as a cultural object. A manuscript can be beautifully written and structurally sound while containing unexamined reception risk — content that hostile readers will weaponize or that well-meaning readers will find hurtful. This audit fills the gap between "does the text work?" and "how will the text land?"

Core failure claim: **unexamined exposure** — culturally charged content present on the page, narrative apparatus not accounting for how it will land.

#### Audit specifications
- 17 diagnostic flags across 5 channels: Representational Risk (RR×4), Extractability (EX×3), Power Framing (PF×4), Cultural Register (CR×3), Harm Weight (HW×3)
- 3-tier severity: Note / Flag / Alert (review urgency, not rewrite urgency)
- 3-way classification: Unexamined / Examined / False Positive
- Three primary artifacts: Risk Map (passage-level with context portability and reviewer questions), Pattern Summary (with P-## IDs), Sensitivity Reader Handoff Memo (conditional)
- Two-pass procedure: over-inclusive marking → coding, Distinguish tests, mode calibration, hard-gate check
- Distinguish framework with 5 decision tests (apparatus, load-bearing, extraction, subject-position, genre-contract), tie-breaking rules, lock-then-classify anti-sycophancy control
- 8-mode calibration matrix with named failure modes (Aestheticized Harm, Collateral Caricature, Archive Shield, Transgression Without Containment, Normalization Drift, Target Blur Satire, Self-Exonerating Frame, Allegory Evasion)
- 5 hard gates including alert concentration rule (≥2 Alerts → automatic handoff) and PF+EX-1 escalation pathway
- 6 interaction patterns with prescribed review orders
- Directional Check: net word-count implication of findings, flag if >10% addition skew
- Cross-genre scope: literary fiction, commercial, historical, dark romance, YA/NA, humor/satire, memoir/autofiction, SFF
- Firewall: diagnostic only — identifies risk, assigns severity, recommends review scope. Forbidden: rewriting, adjudicating, gatekeeping, reducing severity after lock.

#### Level-setting brief
- Theoretical grounding: Jauss (horizon of expectations), Iser (implied reader), Fish (interpretive communities), Hall (encoding/decoding), Booth (rhetorical distance), Genette (focalization), Phelan (ethical positioning)
- 14-pattern failure taxonomy with mechanisms, surface signals, structural isomorphisms
- 6 exemplar techniques for well-managed reception risk with 6 cross-case success signals
- 8-mode calibration evidence (promise, blind spot, false-positive risk per mode)
- Distinguish problem with conflict resolution protocol
- Three-model workflow guidance (discovery, apparatus challenge, extraction stress test)
- Source bibliography: 12 references (7 primary theory, 5 contemporary process)

#### Authoring process
Multi-model synthesis: independent research outputs from Opus 4.6 and Codex 5.3, systematically compared and synthesized across all sections. Stuart Hall reference added from Gemini 2.5 Pro research output.

#### Files added
- `specialized-audits/references/craft/reception-risk.md` — The audit (17 flags, 5 channels, 5 hard gates, 8 mode calibrations, §1–§13)
- `specialized-audits/references/craft/reception-risk-level-setting.md` — Level-setting brief (reception theory, failure taxonomy, positive cases, mode calibration, distinguish problem, three-model workflow, bibliography)

#### Changed: Plugin integration
- `specialized-audits/SKILL.md` — Added Reception Risk row to Craft Audits table, reference file entries, trigger phrases in description
- `core-editor/references/run-core.md` — Added finding-driven audit trigger at Pass 1 (cultural register mismatch on identity/power content at 2+ scenes) and cross-audit trigger (Representation Context surfaces active contestation)
- Audit count updated from 26 → 27 across `plugin.json`, `marketplace.json`, `README.md`

### Added — Title/Framing Architecture (Pass 3)

New conditional diagnostic section in **Pass 3: Rhythm & Modulation** for manuscripts with deliberate titling conceits, epigraph sequences, or section-header systems. Evaluates whether framing devices function as structural argument or decoration.

- Detection criteria for governing conceits in chapter titles, part titles, epigraphs, or section headers
- Deepening test (does conceit develop or repeat at fixed register?)
- Counterpoint test (does framing layer create meaning prose alone doesn't?)
- Coherence test (does conceit hold through full manuscript or lose discipline?)
- New finding-driven trigger: ornamental or incoherent framing conceit → **Literary Craft** audit

#### Changed
- `core-editor/references/run-full.md` — Added Title/Framing Architecture conditional section to Pass 3, updated output specification, added finding-driven audit trigger

### Added — Voice Distinctiveness Comparison (Pass 7)

New diagnostic section in **Pass 7: POV and Voice** for multi-POV manuscripts. Compares cognitive texture of each POV character's interiority across 6 dimensions: sentence architecture, attention pattern, metaphor source domain, temporal orientation, epistemic style, emotional register. Produces a comparison table.

Two new flags:
- **Under-individuation** — 2+ POV characters share cognitive texture across 4+ dimensions (authorial voice absorbing character voice)
- **Selective individuation** — POV characters distinct in surface markers but convergent in deep texture (different topics, same thinking)

#### Changed
- `core-editor/references/run-full.md` — Added Voice Distinctiveness Comparison section to Pass 7, comparison table template, two new flags, updated output specification

---

## v1.0.8 - 2026-03-04

### Added — Compression Audit

New specialized craft audit: **Compression** — "What should be cut?" Identifies expendable material in long-form manuscripts and produces a prioritized cut list with estimated word savings. Subtraction-first diagnostic: finds material to remove, not material to add.

#### Design rationale
The framework's existing passes diagnose structural problems that *imply* cutting but frame their findings as "what's wrong." This audit reframes existing and new findings as "what should go" and quantifies the cost of keeping it. Addresses the framework's structural bias toward addition.

Core failure claim: **retained scaffolding** — the draft carries its construction equipment into the finished building.

#### Audit specifications
- 16 diagnostic flags across 5 channels: Structural Expendability (SE), Informational Redundancy (IR), Scene Efficiency (ScE), Emotional Redundancy (ER), Structural Scaffolding (SS)
- Two primary artifacts: Cut List (3 tiers, sorted by word savings, with confidence ratings) and Compression Map (density per part, mode-aware thresholds)
- Two-pass procedure: discovery sample (~15% of scenes) → enumeration pass before hard-gate escalation
- Distinguish framework with 5 decision tests, explicit conflict resolution rules, and 3-way classification (Cut / Compress / Keep — Load-Bearing)
- Confidence Rubric (High / Medium / Low) gating hard-gate escalation
- 7-mode calibration matrix with named failure modes (Decorative Density, Setup Bloat, Processing Spiral, Guided Tour, Inert Dwell, Informational Detour, Recursive Reflection)
- 4 hard gates with evidence requirements
- Cross-genre scope: literary fiction, thriller, romance, SFF, horror, mystery, memoir/nonfiction

#### Files added
- `specialized-audits/references/craft/compression-audit.md` — The audit (16 flags, 5 channels, 4 hard gates, 7 mode calibrations, §1–§13)
- `specialized-audits/references/craft/compression-audit-level-setting.md` — Level-setting brief (scaffolding theory, over-establishment, diminishing-returns, genre norms, distinguish problem)
- `specialized-audits/references/craft/compression-audit-expansion-stub.md` — Design document (expansion stub)

#### Changed: Plugin integration
- `specialized-audits/SKILL.md` — Added Compression row to Craft Audits table, reference file entries, trigger phrases in description
- `core-editor/references/run-core.md` — Added finding-driven audit trigger at Pass 2 (orphan scenes ≥3 or proportional imbalance >40%)
- Audit count updated from 25 → 26 across `plugin.json`, `marketplace.json`, `.claude-plugin/plugin.json`, `README.md`

---

## v1.0.7 - 2026-03-04

### Added — Protected Elements Section

New required section in the editorial letter synthesis: **§6 Protected Elements — What Not to Touch.** Names 3–6 specific elements the revision must not damage, with reasons. These are the manuscript's load-bearing strengths — scenes, techniques, voice qualities, structural choices, or relationships that are working and that revision could accidentally break.

#### Design rationale
Revision fixes problems but can also destroy what works. §3 identifies strengths; §5 identifies what to change; §6 explicitly marks the no-go zones. Authors revising under pressure tend to over-correct — this section gives them specific guardrails. Zero-cost addition: no new pass, just a new output requirement drawn from existing pass findings.

#### Relationship to §3 (What the Book Does Best)
§3 argues *why* the strengths matter. §6 translates that into *operational protection* — it tells the author which strengths are at risk from the specific revisions recommended in §4 and §5. An element in §3 that isn't threatened by the revision plan doesn't need to appear here.

#### Changed: Editorial Letter Format
- Sections renumbered: old §6 (Strongest Case Against) → §7, old §7 (Stress Test) → §8, old §8 (Appendices) → §9.
- Verification gate updated to check §1–§9.
- All §-cross-references updated across `run-core.md`, `pass-11.md`, `adversarial-stress-test.md`, and `run-full.md`.

#### Changed: Full DE Differences (`run-full.md`)
- Protected Elements at Full DE scale may run up to 8 elements (vs. Core DE's 3–6).
- Pass 11 integration note updated for new section numbering.

---

## v1.0.6 - 2026-03-04

### Added — Kishōtenketsu & Jo-ha-kyū Plot Spines

Two new spines added to the Plot Architecture system, bringing the total from 48 to 50. Contributed by **Appropriate-Record68**.

#### New: Kishōtenketsu (Four-Part Without Conflict) — Spine 6, Family 1

Japanese four-part structure (起承転結) with Chinese and Korean cognates. The major non-conflict-driven structural paradigm in English-language craft discourse. Generates meaning through juxtaposition rather than collision: Introduction (Ki) → Development (Shō) → Turn (Ten) → Reconciliation (Ketsu). No antagonist or crisis required.

- Three logic gates: Juxtaposition Test (does Ten introduce a genuinely non-causal element?), Reconciliation Weight (does Ketsu produce meaning from the juxtaposition?), Development Integrity (does Shō deepen without smuggling in conflict?).
- Critical calibration note: suppresses conflict-driven false positives (Passive Midpoint, Missing Commitment, Crisis Fatigue) when Kishōtenketsu is the identified spine.
- Translation note on *ten*: APODICTIC treats it as juxtaposition, not twist or surprise.
- Cross-reference note added at Three-Act Structure entry for discoverability.
- Genre cross-references: literary fiction (native habitat), manga/comics, slice-of-life, horror (ten-as-wrongness, distinct from Lullaby).

#### New: Jo-ha-kyū (Rhythmic Acceleration) — Spine 44, Family 10

Japanese aesthetic principle (序破急) from Noh drama. A pacing overlay, not a primary spine — diagnoses rhythmic problems within any identified spine. Jo (measured opening) → Ha (accelerating complexity) → Kyū (rapid culmination).

- Three logic gates: Macro Rhythm (whole-work pacing acceleration), Scene-Level Rhythm (internal scene pacing with specified sampling protocol), Scale Nesting (rhythm at multiple scales simultaneously).
- Proportion note: traditional Jo-ha-kyū is not equal thirds (~1/5, 3/5, 1/5); gates use "phases" rather than "thirds."
- Usage note: apply after primary spine identification, not instead of it.
- Genre cross-references: literary fiction, thriller, horror, erotica.

#### Changed: Plot Architecture Audit (`references/plot-architecture-audit.md`)
- Version bumped to 0.5.0.
- All spines renumbered: Family 1 now 1-6 (was 1-5), Family 10 now 41-44 (was 40-42), Families 11-12 now 45-50 (was 43-48).
- Three new rows in Diagnostic Quick Reference ("When the Draft Feels..." table).
- Eight new entries in Spine Compatibility Matrix.
- Removed duplicate Save the Cat + Kishōtenketsu entry (consolidated into new Kishōtenketsu entries).

#### Changed: Plot Selection & Coaching (`references/plot-selection-coaching.md`)
- Version bumped to 1.1.
- Phase 1: Added "contemplative recognition" to reader-feeling map; added "juxtaposition" as engine type.
- Phase 2: Added juxtaposition branch to single-spine decision tree.
- Phase 3: Added Jo-ha-kyū as a structural technique overlay alongside TV/Serial and Game-Inspired formats.
- Phase 5: Added "every diagnostic flags problems but draft works" to stuck-draft symptom table.

#### Changed: SKILL.md (plot-architecture)
- Version bumped to 1.0.4.
- Spine count updated from 48 to 50 across all references.
- Family table updated: Family 1 includes Kishōtenketsu, Family 10 includes Jo-ha-kyū.
- Quick reference logic gates and diagnostic table updated.

#### Changed: Genre Module — Literary Fiction (`genre-literary.md`)
- Pass 2 (Structural Mapping): Added Kishōtenketsu as native structural option; added juxtaposition to organizational principles; added Jo-ha-kyū pacing note.

#### Changed: Genre Module — Horror (`genre-horror.md`)
- Pass 2 (Structural Mapping): Added non-conflict horror note (Kishōtenketsu ten-as-wrongness, distinct from Lullaby rupture).
- Pass 3 (Rhythm): Added Jo-ha-kyū horror pacing mapping.

#### Changed: README.md
- Spine count updated from 48 to 50.

#### Changed: plugin.json
- Version bumped to 1.0.6.

---

## v1.0.5 - 2026-02-24

### Added — Hybrid Mode (Optional Execution Mode)

Hybrid mode is a middle ground between single-context and full swarm. Pass 0+1 reads the entire manuscript and produces a **focus map** — a targeting document that directs each subsequent pass to specific scenes for deep reading. Later passes run as independent subagents with the reverse outline (compressed manuscript) plus only the focus map's targeted excerpts, not the full text.

**Tested** on an 83k-word novel where per-pass targeting was 22–33%, producing categorically richer findings than single-context at ~2.8x the token cost. Single-context vs. hybrid comparison showed: 12 findings (mostly approving) vs. 25 findings (genuinely diagnostic, 92% with counterevidence); opposite diagnoses on the ending; zero cross-pass complication in single-context vs. four genuine complications in hybrid.

**Cost profile:** ~1.5–2x for 60–100k manuscripts; ~2–3x for 100k+ manuscripts. Tested at ~1.4x on 83k (2 analytical passes) and projected ~1.7–1.9x (3 analytical passes).

**Quality profile:** Architectural isolation for later passes (same as swarm), but with targeted rather than full manuscript access. The focus map errs on inclusion (no enforced targeting range; advisory ceiling at 60%), and every pass still receives the complete reverse outline.

#### New: Focus Map specification (`references/hybrid-mode.md`)
- Complete specification for the focus map output type: format, targeting grammar, confidence tiers (high-confidence and broad-net), excerpt extraction protocol, risk analysis, and token cost model.
- Targeting rationale categories drawn from both Pass 0 (outliner lens: arbitrary breaks, unusual ratios, word count anomalies, information density, POV shifts) and Pass 1 (reader lens: belief failures, orientation failures, boredom signals, emotional spikes, promise drift, immersion breaks).
- Cross-pass targets section for scenes flagged by multiple passes.
- Coverage interpretation note in focus map output — explains what the numbers mean for this specific manuscript and offers swarm as alternative if coverage is high.
- No enforced targeting range; inclusion bias + advisory ceiling (60%) only. Triage subagent targets what it finds.
- Ledger persistence requirement: each subagent's findings must be written to file immediately upon return, making the parent orchestrator stateless between dispatches and resilient to context compaction.
- Open questions partially resolved by testing; remaining open questions documented.

#### Changed: Execution Mode section (`run-core.md`)
- Added hybrid mode between single-context and swarm.
- Updated token cost table to three modes.
- Added hybrid mode additional output note to Pass 0 specification (focus map production).

#### Changed: Intake router (`references/intake-router-runtime.md`)
- New §2b: Execution Mode question fires for manuscripts over 40k words. Three plain-language options (standard read / targeted deep read / full independent read) with context-sensitive recommendations. Surfaces the execution mode choice as a first-class intake question rather than burying it in the constraint list.
- §3 options H and I retained as safety net for users who arrive via direct commands or shorter manuscripts.
- §2 `full_draft` submission recommendation now defers to §2b instead of handling execution mode inline.
- Added route map entries for `full_draft + repair + hybrid` and `full_draft + submit + hybrid` (both **Built**).

#### Changed: SKILL.md
- Execution mode description updated to cover all three modes.

#### Changed: README.md
- Execution Modes section expanded to describe single-context, hybrid, and swarm with guidance on when to use each.

---

## v1.0.4 - 2026-02-24

### Added — Swarm Mode (Optional Execution Mode)

A/B testing demonstrated that dispatching each pass as an independent subagent produces roughly twice as many findings with more specific cross-pass connections and more consistent counterevidence, at approximately 5x the token cost. The quality improvement comes from architectural isolation: each pass genuinely cannot see prior analysis until reconciliation, which eliminates anchoring bias and produces multi-perspectival convergence rather than echo.

#### New: Execution Mode section (`run-core.md`)
- **Single-context mode** (default): all passes run sequentially in the current conversation context. No change from prior behavior.
- **Swarm mode** (optional, user-invoked): each evaluative pass runs as an independent subagent with its own context window. Parent orchestrator manages the sequence and accumulates the Findings Ledger between dispatches.
- Swarm Execution Protocol: specifies parent orchestrator responsibilities, what each subagent receives and returns, pass grouping (Pass 0+1 combined), and token cost estimates.
- User invokes swarm mode at intake (e.g., "run this in swarm mode").

#### Changed: Staged Visibility (`run-core.md`)
- Added note clarifying that staged visibility is architecturally enforced in swarm mode (subagent has no prior pass artifacts in context) vs. procedurally enforced in single-context mode (reduces but does not eliminate anchoring).

#### Changed: Design document (`docs/subagent-architecture-design.md`)
- Status updated from "Future (v2.0+)" to "Available as optional execution mode (v1.0.4+)."
- Decision record updated with A/B test results and rationale for shipping as optional mode.

#### Changed: Roadmap (`ROADMAP.md`)
- Subagent Pass Orchestration marked as shipped (optional mode, v1.0.4).

---

## v1.0.3 - 2026-02-23

### Added — Findings Ledger & Editorial Letter Integration

Comparative testing (plugin vs. blind editorial letter on *A Game of Universe*) revealed that pass artifacts contain rich analytical data that the synthesis step compresses away. Context window decay compounds the problem — by synthesis time, earlier pass details have faded. This release adds a running ledger and companion editorial letter changes to preserve pass findings through to the author.

#### New: Findings Ledger Protocol (`run-core.md`)
- **Findings Ledger** — a running document (`[Project]_Findings_Ledger_[runlabel].md`) appended to by each evaluative pass immediately after completion, while pass content is still in active context.
- Each ledger entry contains: Notable Findings, Data Artifacts for Letter Reference, Cross-Pass Connections, Unresolved Questions, and Audit Triggers.
- **"When in doubt, include" rule** — lowers the bar for initial ledger entries since synthesis can ignore noise but can't recover omissions.
- **Retroactive promotion** — later passes can append `[Retroactive — added by Pass N]` notes to earlier ledger sections when a finding proves more important than initially assessed.
- Pass 0 and Pass 10 exempt unless they surface observations warranting a ledger entry (e.g., SFF Rule Ledger inconsistencies).

#### Changed: Synthesis Processing Protocol (`run-core.md`)
- **Step 3 (Root Cause Analysis):** Synthesis now reads the Findings Ledger as primary input. Ledger cross-pass connections are treated as pre-built root cause hypotheses. Unclustered findings carry forward to §4b.
- **Step 6 (Adversarial Stress Test):** Added independence instruction — stress test begins by setting aside pass findings and generating attacks from holistic manuscript reading. Draws also from ledger's Unresolved Questions. Reconciles with pass findings afterward; new attacks enter §7, convergent attacks noted but not duplicated.

#### Added: §4b "Additional Observations from the Diagnostic Passes" (`run-core.md`)
- New editorial letter section between §4 (What Needs Work) and §5 (Revision Checklist).
- Draws from the Findings Ledger — notable findings and cross-pass connections not covered in the main editorial argument.
- Serves two purposes: prevents synthesis compression of useful pass findings, and teaches the author how to use pass artifacts as revision tools.
- Every item includes a cross-reference to the relevant pass artifact.

#### Added: Cross-Reference Convention (`output-policy.md`)
- New section specifying inline cross-reference format: `*(see [Pass Name], §[Section or Table Name])*`.
- Transforms the editorial letter from a standalone argument into a navigation layer over the pass artifacts.
- Findings Ledger added to Output Naming Convention.

#### Changed: Pass Dependencies (`pass-dependencies.md`)
- Added "Running Artifacts" table documenting the Findings Ledger as a non-pass artifact.
- Version bumped to v0.6 (internal architecture version for the pass dependency map).

#### Added: SFF Rule Ledger Cross-Check (`genre-sff.md`)
- **Pass 1 addition:** When Pass 10 is not in the run, Pass 1 cross-references belief failures against Pass 0's Rule Ledger for scaling inconsistencies, cost amnesia, and unexplored implications.
- **Pass 8 addition:** Same condition; Pass 8 checks construct scaling consistency, cost payment consistency across uses, and introduced-but-unexplored rules.
- Both log matches to the Findings Ledger as cross-pass connections between their pass and Pass 0.

### Provenance
- Root cause: Comparative A/B testing (APODICTIC vs. blind editorial letter on *A Game of Universe* by Eric Nylund, 118K words) revealed the plugin's pass artifacts contained richer analysis than the blind letter in several categories, but the synthesis compressed away the advantage. The blind letter independently caught findings (Manifoldification scaling, Erybus backstory-collapse risk, Campbell scaffolding, child abuse access barrier) that the plugin's passes had data for but never surfaced.
- Design document: `Outputs/APODICTIC_Findings_Ledger_Proposal.md`

## v1.0.0 - 2026-02-22

### 1.0 Release

v0.5 UX overhaul is complete: query-driven pass architecture, intake router, scene-level handoff, command alias model, overview dashboard, route explorer. The plugin is navigable by newcomers. Tagging 1.0.

### Changed — Version Hygiene
- Stripped decorative version numbers from ROADMAP.md, README.md, core-editor SKILL.md body header, AUDIT_SELECTION_MATRIX.md, route explorer HTML.
- Removed hardcoded version strings from output template footers (diagnostic-state-template.md, contract-template.md, reverse-outline-template.md, pass-11.md, pre-writing-pathway SKILL.md).
- Canonical version now lives exclusively in `plugin.json` + 4 SKILL.md frontmatter fields.
- Added `scripts/bump-version.sh` to update all 5 locations from a single command.

### Fixed — Audit Resolver Names
- Reconciled 3 string mismatches: "Erotic Content tag" → "Erotic Content", "Character Architecture (deep)" → "Character Architecture", "Banister" → "Banister (Epistemic Humility)".

## v0.4.19 - 2026-02-22

### Added — v0.5 Integration Files (Runtime)
- Added `references/pass-dependencies.md` to core-editor references and wired it into pass resolution flow.
- Added split router files: `references/intake-router-runtime.md` (runtime) and `references/intake-router-design.md` (design notes).
- Added `references/handoff-protocol.md` and integrated scene-level handoff mode transitions.
- Added `overview-dashboard.html` to plugin root.

### Changed — Core Runtime Wiring
- `/start` now runs a mode-aware resume gate before router Q1. If `Diagnostic_State.md` indicates execution mode, it presents: Check the fix / Keep working / Start fresh.
- `core-editor/SKILL.md` now uses concern-driven pass resolution (`pass-dependencies.md`) instead of fixed tier framing.
- `run-core.md` now explicitly resolves concern -> minimum pass set -> dependencies, with baseline floor fallback and optional scene-level handoff behavior.
- `run-full.md` reframed from trigger-gated language to expansion-policy language aligned with resolver auto-escalation.
- `diagnostic-state-template.md` now includes `Mode` and append-only `Handoff History` schema.

### Changed — Command Alias Model
- `/develop-edit` is now defined as a `/start` shortcut with prefilled `artifact=full_draft`, `goal=repair`.
- `/pre-writing` is now defined as a `/start` shortcut with prefilled `artifact=idea`, `goal=draft`.
- `/diagnose` is now defined as targeted resolver routing (`goal=repair`, concern-required).
- `pre-writing-pathway/SKILL.md` now accepts router output as prefilled intake context and skips redundant prompts.

### Changed — Handoff Semantics
- `handoff-protocol.md` language updated from "unload skill" to "suspend/re-enable core-editor constraints" to match actual behavior-contract capabilities.

### Version Reconciliation
- Updated plugin manifest version to `0.4.19` (`.claude-plugin/plugin.json`).
- Updated `core-editor/SKILL.md` version markers to `0.4.19`.
- Updated `README.md` framework version to `v0.4.19`.
- Updated roadmap header version to `v0.4.19`.

## v0.4.17 - 2026-02-21

### Fixed — Audit Discovery and Invocation (Codex review)
- **`/audit` command** expanded from 17 to 28 entries. Now lists all current audits organized by category: Universal (3), Craft (15), Genre (4), Tag (3), Plot (1 cross-reference). Previously missing: Stakes System, Decision Pressure, Force Architecture, Literary Craft, Horror Craft, Mystery/Thriller Architecture, SFF Worldbuilding, Cozy Tag, Philosophical Tag, Erotic Content.
- **`/develop-edit` workflow order** corrected: audit integration now happens after core passes and before synthesis (step 4), matching `run-core.md` §Audit Integration Point. Previously synthesis preceded audit evaluation.
- **`specialized-audits/SKILL.md` catalog** updated: Stakes System, Decision Pressure, and Scene Turn now listed as Universal Audits in both the Available Audits table and Reference Files section. Previously missing from both.
- **Intake router** (`intake-router.md`): added "Run a focused audit on a specific concern" option (E) for full_draft artifact, with corresponding route map entry. Previously no audit route was reachable for complete drafts via `/start`.
- **README.md** counts updated: "23 specialized audits, 5 tag audits" (was "18 deep-dive audits, 2 tag audits"); "28 available audits" (was "17"); version line updated.

### Added — Audit Invocation Log
- New artifact in `run-core.md` §Audit Integration Point: `[Project]_Audit_Invocation_Log_[runlabel].md`. Tracks every audit considered during a run with source (universal/contract/finding-driven), status (run/skipped/deferred), and reason. Referenced in `/develop-edit` step 4.

### Changed — Legacy Module Index
- **`module-index.md`** marked as legacy reference with deprecation header. File paths reference pre-plugin directory structure and do not match current package. Users directed to `AUDIT_SELECTION_MATRIX.md` and `specialized-audits/SKILL.md` for current routing and file paths.
- **`core-editor/SKILL.md`** reference to `module-index.md` annotated as legacy with redirect to current sources.

### Deferred
- **P2 #5 (Token overhead / router split):** Splitting `intake-router.md` into a short runtime decision table and a separate design document would reduce early-turn context consumption. Deferred to future version — requires updating all references and the `/start` command.

## v0.4.16 - 2026-02-21

### Added — Synthesized Audits and Integration Pipeline
- **Stakes System audit** (craft/stakes-system.md + craft/stakes-system-level-setting.md). Three-model synthesis (Opus46, Codex53, Gemini). 22 named diagnostic flags across 6 channels (STX, PC, IM, EG, MP, CL). 4 tracking artifacts. Four-tier distinguish framework. Production audit + level-setting companion.
- **Decision Pressure audit** (craft/decision-pressure.md + craft/decision-pressure-level-setting.md). Three-model synthesis (Opus46, Codex53, Gemini). 23 named diagnostic flags across 7 channels (AV, CS, IS, EC, RF, TR, PV). 6 tracking artifacts. Four-tier distinguish framework. Production audit + level-setting companion.
- **AUDIT_SELECTION_MATRIX.md** — comprehensive routing guide covering all 11 sections: fast entry router, core/full DE passes, Pass 11, craft audits, structural modules, genre audits, tag audits, research modes, recommended bundles, and minimal rule of thumb.

### Added — Audit Integration into Pass Sequence
- **Contract-driven audit activation** at intake (run-core.md): 17-row table mapping genre/mode signals to recommended audits.
- **Finding-driven audit triggers** across 7 passes: Pass 1 (belief failures → DP, emotional flatness → EC, low stakes → SS, action immersion → FA), Pass 2 (causal gaps → Scene Turn, nonfiction situation overwhelming → Franklin), Pass 3 (intensity plateau → SS, pacing stalls → Scene Turn), Pass 4 (triple stasis → EC, intensity plateau → SS, certainty static → Horror/Mystery-Thriller), Pass 5 (motivation discontinuity → DP, agency collapse → SS, under-specified wants → Character Architecture), Pass 6 (single/zero-function → Scene Turn, setup debt → SS), Pass 8 (knowledge errors → DP IS channel, information timing → DP + Reveal Economy).
- **Audit Integration Point** in run-core.md: 4-step protocol for compiling triggers, comparing against contract, running audits, feeding into synthesis.
- **Supplementary Audit Integration Protocol** in run-full.md: 5 rules covering timing, synthesis integration, dashboard feeds, cross-audit coordination, firewall compliance.

### Changed — Synthesis and Output Capacity
- **Processing Protocol** expanded from 5 to 6 steps. New Step 2: Audit Finding Consolidation with 5 rules (map to pass findings, cluster by problem not audit, preserve audit-unique findings, count consolidated problems not flags, carry artifacts to appendices).
- **Appendix A** spec expanded to include audit companion files and tracking artifacts.
- **Full DE letter spec** updated with supplementary audit integration guidance and cross-audit overlap rule.
- **Dashboard** expanded from 8 to 10 components: Component 9 (Decision Pressure Map — option visibility, tradeoff cost, pivot integrity), Component 10 (Force/Action Tracking — conditional on Force Architecture audit). Assembly rules updated for conditional components and expanded length target.

### Changed — Supplementary Audits Section
- **run-full.md** Supplementary Audits section replaced (~20-line stub → ~120-line comprehensive section): Universal Audits (Stakes System, Decision Pressure, Scene Turn, Emotional Craft) with pass connections and pairing logic; Genre/Mode Audits with activation table; Tag Audits table; Integration Protocol.

## v0.4.15 - 2026-02-21 (First Alpha Release)

### Changed — Full Rebrand
- **Package renamed** from `development-editor` to `apodictic`. Top-level directory, plugin.json name, and .plugin filename all updated.
- **Core skill renamed** from `core-development-editor` to `core-editor`. All command files, SKILL.md frontmatter, and internal references updated.
- **Version scheme changed** from 4.x to 0.4.x to reflect pre-1.0 status. All version references across all files updated.
- **Branding normalized** to "APODICTIC Development Editor" throughout. Legacy "APDE" shorthand retained in output template footers.

### Added — Full DE Output Specifications
- **Output specs added** for all Full DE passes (3, 4, 6, 7, 9, 10). Each pass now specifies its output filename and artifact contents, matching the Core DE pass format.
- **Output naming convention** in output-policy.md updated to include all Full DE filenames plus Pass 11 and Full DE Synthesis.

### Added — Inline Genre Calibration
- **Mystery / Investigation** inline calibration section added to core-framework.md — reader expectations, subgenre false-positive warnings, contract additions, priority pass (Pass 8), pass modifications, key diagnostic flags, false-positive warnings.
- **Thriller / Suspense** inline calibration section added to core-framework.md — same depth. All six genres now have inline calibration sections.

### Validated
- Dry run complete: full 11-pass DE executed on a novella-length manuscript. All passes produced output artifacts.
- Density re-audit passed all four §10 proportionality thresholds.
- Three §8 design decisions resolved (rejection memo scope, reference implementation, genre calibration coverage).

## v0.4.14.3 - 2026-02-20

### Added — Documentation and Policy
- **README.md:** Added "What This Plugin Does and Does Not Do" section — user-facing policy covering diagnostic scope, the Firewall, and explicit boundaries (no prose generation, no line editing, no content storage beyond session).
- **README.md:** Added "Intended Audience and Safety Boundaries" section — primary/secondary audience, content coverage statement (all published fiction genres analyzed on their own terms), and safety posture (analytical outputs only, no content generation).
- **CONTRIBUTING.md:** Added "Changelog Policy" section — entry format, framing rules, reframing table for public-facing language, and version bump guidance (patch/minor/major).
- **README.md version** updated to v0.4.14.3.
- Completes Publication Requirements §5 items: changelog policy, safety boundaries, and end-user policy text.

## v0.4.14.2 - 2026-02-20

### Added — SFF Subgenre Pass Recalibrations
- **genre-sff.md** expanded from 415 → 581 lines (+166 lines) with comprehensive subgenre pass recalibrations.
- **Master Calibration Matrix:** 10 subgenres × 8 modified passes showing ELEVATE/STANDARD/DEPRIORITIZE/RECALIBRATE for each combination. Tells the editor exactly how to adjust each pass for the manuscript's specific subgenre.
- **Per-Pass Recalibration Notes** for all 8 modified passes:
  - Pass 0: Hard SF `[SCIENCE CLAIM]` tagging, Epic Fantasy hard/soft/lore rule separation, New Weird rule-flag suppression, Portal Fantasy `[DISCOVERY]` tracking
  - Pass 1: Hard SF system-vs-vocabulary confusion distinction, Cyberpunk disorientation window (15%), Epic Fantasy stalling-vs-slowness, Grimdark interest-not-sympathy threshold (30%), Portal Fantasy synchronization tracking, Progression/LitRPG stat-block tolerance
  - Pass 4: Hard SF eureka tracking, Space Opera scale-wonder, Cyberpunk alienation axis, Epic Fantasy moral weight, New Weird estrangement, Solarpunk hope axis, Grimdark corruption axis, Portal Fantasy wonder resurfacing (2+ scenes after 50%), Progression/LitRPG flat progression affect
  - Pass 5: Hard SF frictionless expertise, Cyberpunk identity-cost augmentation, Urban Fantasy dual-identity strain, Grimdark costless edge, Portal Fantasy learning curve (2+ failures), Progression/LitRPG stat-growth-character-stasis
  - Pass 6: Hard SF lab bench scene, Epic Fantasy empty council, New Weird atmosphere tolerance
  - Pass 8: Hard SF textbook passage + stricter 50% threshold, Cyberpunk flat conspiracy, Epic Fantasy extended cadence (50%), Urban Fantasy spent masquerade, Portal Fantasy flat discovery, Progression/LitRPG incremental grind
  - Pass 9: Hard SF interchangeable tech, Cyberpunk aesthetic cyberpunk, New Weird pattern-not-statement, Solarpunk optimism without evidence, Grimdark decorative nihilism, Progression/LitRPG uncritical meritocracy
  - Pass 10: Hard SF zero-tolerance cost amnesia, Space Opera political-not-physics rules, Cyberpunk system rules, Epic Fantasy hard/soft/hybrid ledger, Urban Fantasy masquerade amnesia, New Weird dream-logic consistency, Progression/LitRPG zero-tolerance system inconsistency
- **Subgenre Deep-Dive Override Table:** 6 threshold overrides for SFF-DD1/DD2/DD3 across Progression/LitRPG, Hard SF, Epic Fantasy, New Weird, and Grimdark.
- **Cross-Reference section** linking to worldbuilding audit subgenre calibration for aligned expectations.

## v0.4.14.1 - 2026-02-20

### Changed — Genre Module Parity Hardening
- **All six genre modules updated to v0.4.14** with numeric thresholds, named deep-dive flags (Detection/Test/Threshold/Flag/Exception format), and mechanistic diagnostic checks. Changes target quantifiability and actionability, matching Romance's level of mechanical specificity.
- **genre-horror.md:**
  - Added Certainty-Intensity Sync Check (parallel to Romance's dual-track model) with alignment table and thresholds (certainty stasis >25%, premature collapse <40%, intensity plateau 3+ chapters)
  - Added Pass 3 thresholds: dread fatigue (3+ consecutive peak chapters), tension bleed (3+ consecutive low chapters), relief ratio (1 valley per 2-3 peaks)
  - Added 4 named deep-dive flags: HOR-DD1 Explanation Kills (>50% mystery resolved before final 20%), HOR-DD2 Numb Protagonist (3+ horror events without deterioration), HOR-DD3 Diminishing Returns (3+ same technique without variation), HOR-DD4 No Normalcy Baseline (horror in first 10% without baseline)
  - Added Dread Ladder diagnostic checks: stuck rung (3+ chapters), premature point-of-no-return (<40%), regression without purpose (2+ rung drop), repeated rungs (3+ without deepening)
  - Added Dread Indicators checklist (9 indicators, parallel to Romance's Chemistry Indicators) with told-not-shown threshold (3+ scenes relying on assertion)
- **genre-mystery.md:**
  - Added Pass 8 cadence and visibility thresholds: clue cadence (1 per 15%), information drought (20% stretch with zero clues), front-loading check (>60% clues in Act I), culprit visibility (minimum 3 scenes, at least 1 in first 40%), suspect pool size (3-6 optimal), red herring ratio (max 2:1), late clue deadline (no essential clues in final 10%), suspect suspicion shift (minimum 1 shift)
  - Added 4 named deep-dive flags: MYS-DD1 Parlor Scene Info Dump (>5% manuscript, <2 interruptions), MYS-DD2 Equal Opportunity Suspect (all suspects identical at 60%), MYS-DD3 Vanishing Investigation (3+ chapters without progress), MYS-DD4 Retroactive Incoherence (2+ scenes contradicting solution)
  - Added Fairness Score system (FAIR/BORDERLINE/UNFAIR granular assessment replacing binary pass/fail) with thresholds
- **genre-thriller.md:**
  - Added Pass 3 thresholds: flat middle (3+ chapters in Act II without escalation), premature climax (resolved before 75%), exhaustion pacing (4+ consecutive peak chapters), scene compression check, tension oscillation minimum (1 valley per 4 peaks)
  - Added Per-Act Resource Ledger (7 resource categories tracked across 5 story points) with depletion thresholds (minimum 2 categories degraded by Act II midpoint, 4+ depleted at dark moment)
  - Added formal Safety Island definition (4 criteria) with thresholds (>2 chapters, >15% manuscript, pre-climax lull)
  - Added 3 named deep-dive flags: THR-DD1 Teflon Protagonist (3+ confrontations without cost), THR-DD2 Convenience Engine (2+ unearned escapes), THR-DD3 Decaying Villain (peak threatening moment before 40%)
  - Added Escalation Ladder diagnostic checks: skipped rung, stuck rung (3+ chapters), missing first trap (by 25%), regression, escalation monotony (3+ same type)
- **genre-sff.md:**
  - Expanded from 5 to 10 pass modifications: added Pass 4 (wonder axis, power-cost emotional check with per-phase register table), Pass 5 (competence-cost inventory table, frictionless system threshold at 60%), Pass 8 (worldbuilding reveal cadence with late-rule threshold at 60%), Pass 9 (thematic integration check for speculative elements)
  - Added 3 named deep-dive flags: SFF-DD1 Magic Microwave (3+ identical-pattern uses), SFF-DD2 Worldbuilding Orphan (3+ weighted details without payoff), SFF-DD3 Escalation Treadmill (3+ threat-then-power-up cycles without lateral thinking)
  - Added Integration with Core Framework section listing all 10 modified passes and combination guidance
  - Added SF/F-specific reader experience flags (5 flags)
- **genre-literary.md:**
  - Added 4 named deep-dive flags: LIT-DD1 Theme-as-Lecture (Stated:Embodied ratio >2:1), LIT-DD2 Unearned Epiphany (<2 precursor scenes), LIT-DD3 Beautiful Emptiness (3+ high-craft passages without payoff), LIT-DD4 Quiet Evasion (2+ thematic questions unaddressed at ending)
  - Added Thematic Dual-Track Model (Theme-as-Content + Theme-as-Form) with alignment check table (parallel to Romance's emotional/physical dual-track)
  - Added Pass 9 thematic thresholds: theme drought (20% stretch with zero instances), front-loading (>60% heavy instances in first third), static theme (identical at 80% vs 20%), epiphany count (>2 investigate)
- **Author name updated** to "Joshua A. Miller, PhD" across README.md, plugin.json, CONTRIBUTING.md, and LICENSE.
- **README.md version** updated from v0.4.6.0 to v0.4.14.

## v0.4.14 - 2026-02-20

### Changed — Thin Orchestrator Refactor
- **Core SKILL.md reduced from 1,660 lines to 253 lines.** Rewritten as thin orchestrator containing only: firewall, operating tiers, workflow contract, pass architecture summary, output policy summary, delegation rules, genre module routing table, reference file routing table, QA guardrails.
- **Extracted four new reference files:**
  - `references/run-core.md` (~450 lines) — Intake protocol, Core DE passes (0/1/2/5/8), synthesis processing/presentation, deliverables, revision round protocol. Loaded every Core DE and Full DE run.
  - `references/run-full.md` (~170 lines) — Full DE passes (3/4/6/7/9/10), supplementary audits (Stakes System, Decision Pressure), Full DE deliverables, structural frameworks reference, certainty axis cues. Loaded only when Full DE tier triggers.
  - `references/output-policy.md` (~210 lines) — Author-facing language rules, output constraints, naming conventions, confidence calibration, epistemic humility, deep analysis triggers, severity honesty protocol, severity floor rules, editorial letter tone/voice, pass-level output protocol. Loaded before writing any output.
  - `references/character-architecture.md` (~110 lines) — Arc types, psychology engine, trauma physics, agency quotient, constraint quotient, voice distinctiveness, ensemble balance, genre tuning packs. Loaded when detailed character analysis needed.
- **Removed from core SKILL.md (delegated to existing reference files or companion skills):**
  - Genre calibration blocks (Literary Fiction, Horror, SF/F, Romance) — already exist as standalone reference files (`genre-literary.md`, `genre-horror.md`, `genre-sff.md`, `genre-romance.md`)
  - Specialized audit stubs (Interiority Preservation, Female Interiority, Series/Composite, Consent Complexity, Banister, Shelf & Positioning, Comedy & Satire, Historical Fiction, Queer Romance/Erotica, Fan Fiction Conversion, Tag Audits) — delegated to `specialized-audits` skill
  - Plot Architecture section (48 spines, logic gates, diagnostic quick reference) — delegated to `plot-architecture` skill
  - Plot Selection & Coaching, Fantasy & Series Architecture stubs — delegated to `plot-architecture` skill
  - Research Modes — delegated to `specialized-audits` skill
  - Pass 11 full internals — pointer to `references/pass-11.md`
  - Reference appendices (Structural Frameworks, Certainty Axis Cues) — moved to `references/run-full.md`
- **Patched `/start` command:** No longer preloads all three companion skills. Loads `core-editor` only; loads target skill after route decision.
- **Patched `/pre-writing` command:** No longer preloads `core-editor` and `plot-architecture` at session start. Loads `pre-writing-pathway` only; loads `plot-architecture` at Phase 4; loads core only on re-entry.
- **Patched `/develop-edit` command:** Added lazy loading instructions for `references/run-core.md`, genre modules, `references/output-policy.md`, and `references/run-full.md`. Fixed cap drift: "surgery list (max 25 items)" → "revision checklist (max 10 items)" to match current output policy.
- **Version bumped to 4.14.**

### Context Load Impact
- `/start` → loads ~253 lines (was ~1,660 + two companion skills)
- `/develop-edit` → loads ~253 + ~450 (run-core) = ~700 lines (was ~1,660)
- Full DE trigger → adds ~170 lines (run-full) on demand
- Genre modules load only when manuscript genre identified
- Specialized audits, plot architecture, pre-writing pathway load only when routed

## v0.4.13 - 2026-02-20

### Changed — Genre-to-Tag Restructure (Track 3)
- **Split Romance/Erotic genre module into Romance (genre) + Erotic Content (tag).** The combined `genre-romance-erotic.md` (423 lines) has been replaced by two purpose-built files:
  - `genre-romance.md` (new, ~320 lines) — Romance genre module. Keeps: relationship engine, structural obstacles, chemistry indicators, escalation stages, trust-rupture-repair cycle, pass modifications (Passes 1, 2, 4, 5, 6, 8), 15 genre-specific flags (including Magic Wand, Idiot Ball, Body Betrayal), subgenre calibration (Contemporary, Historical, Paranormal, Dark Romance, Slow Burn, Poly/WhyChoose, Romantasy, Romantic Suspense). Removed: heat level contract, consent calculus, kink integration, erotic-specific flags, escalation vs. repetition audit — all moved to Erotic Content tag.
  - `erotic-content.md` (new tag audit, ~400 lines) — Cross-genre Erotic Content tag. Applies to any manuscript with significant intimate content regardless of parent genre. Five diagnostic dimensions (Scene Function/Load-Bearing Test, Psychological Presence, Escalation Architecture, Consequence Persistence, Consent Architecture). Eight named flags (EC-1 Decorative Kink, EC-2 Mechanical Intimacy, EC-3 Skipped Aftermath, EC-4 Static Heat, EC-5 Intimacy as Pause, EC-6 Pattern Repetition, EC-7 Technique Saturation, EC-8 Vanishing Interiority). Consent Calculus with logic gates (migrated from old Pass 10 section). Escalation vs. Repetition Audit (migrated from old module). Seven mode calibrations with named failure modes (The Treadmill, The Manual, The Safety Net, The Detour, The Intermission, The Costume Party, The Catalog). Four severity hard gates. Four-class distinguish framework. Output template. Firewall compliance.
- **Updated companion audit integration references:**
  - `consent-complexity.md` → v0.4.13: Updated integration section to point to Erotic Content tag + Romance genre module (was: "Romance/Erotic Module")
  - `queer-romance-erotica.md` → v0.4.13: Updated integration section to point to Erotic Content tag + Romance genre module (was: "Romance/Erotic Module")
  - `interiority-preservation.md` → Expanded from intimate-scene-only stub to cross-genre high-intensity stub with genre-specific application pointers (Force Architecture, Erotic Content tag, Horror Craft, Romance genre module)
- **Updated core-editor SKILL.md:** "Genre Calibration: Romance / Erotic" → "Genre Calibration: Romance" with Erotic Content tag activation note. Updated reference path from `genre-romance-erotic.md` to `genre-romance.md`. Updated interiority preservation cross-reference. Renamed spine family "Relationship/Erotic" → "Relationship/Intimacy."
- **Updated specialized-audits SKILL.md → v0.4.13:** Added Erotic Content tag to Tag Audits table with trigger words. Added `references/tag/erotic-content.md` to reference paths. Updated Consent Complexity and Queer Romance/Erotica reference descriptions.
- **Removed:** `genre-romance-erotic.md` (old combined module), legacy flat-file duplicates of consent-complexity.md, queer-romance-erotica.md, interiority-preservation.md from references root.

### Edge Case Verification
- Pure erotica (no romance arc): Erotic Content tag standalone ✓
- Romantasy (romance + epic fantasy): Romance module + optional Erotic Content tag ✓
- Noir with sex scenes (thriller + erotic content): Erotic Content tag standalone ✓
- Literary fiction with explicit content: Erotic Content tag standalone ✓
- Sweet romance (heat level 1-2): Romance module standalone ✓

## v0.4.12 - 2026-02-20

### Added
- **Force Architecture audit** (craft/force-architecture.md, 622 lines, three-model synthesis). Cross-genre audit evaluating whether physical conflict functions as a coherent narrative engine or produces inert spectacle. Core concept: "inert force" — action choreography present, reader not changed by it. Anchor insight: force that escalates in intensity but not in consequence and meaning conversion is structurally parallel to ornamental prose, inert dread, and informational drift. Six integration dimensions (LG Legibility, TC Tactical Causality, CR Competence-Risk Tension, CP Cost Persistence, ES Escalation Kind-Shift, MC Meaning Conversion) with Integrated/Partial/Detached ratings. Force centrality profile (low/medium/high burden) as pre-assessment calibration. 25 named diagnostic flags: LG-1 White-Room Melee, LG-2 Teleport Bodies, LG-3 Actor Chain Blur, LG-4 Sensory Flatline, LG-5 Disembodied Combatant; TC-1 And-Then Chain, TC-2 Ruleless Advantage, TC-3 Frictionless Execution; CR-1 Godmode Drift, CR-2 Threat Collapse, CR-3 Plot Armor Leak, CR-4 Flawless Execution; CP-1 Rubber-Band Injury, CP-2 Resource Theater, CP-3 Trauma Erasure, CP-4 Collateral Erasure, CP-5 Relationship Reset; ES-1 Scale-Only Escalation, ES-2 Combat Monotone, ES-3 Escalation Cliff, ES-4 Pacing-Significance Inversion; MC-1 Violence Shortcut, MC-2 Cool-Kill Drift, MC-3 Aftermath Null, MC-4 Conversion Failure. Four tracking artifacts: Force Event Ledger with Abstraction Level column (required), Consequence Continuity Ledger with Behavioral Evidence column (required), Escalation Ladder Map (required), Legibility Snapshot Grid (recommended). Pattern interpretation protocol with 10 diagnostic combinations, Special Caution Zones (Horror Craft overlap, Mystery/Thriller overlap, Character Architecture downstream, Emotional Craft upstream, AI-Prose susceptibility). Nine severity hard gates. Seven distinguish tests (Reconstructability, Constraint Consistency, Risk Reality, Persistence, Kind-Shift, Conversion, Cognitive Anchor) with four-class decision matrix (Intentional and Successful, Intentional but Unstable, Ambiguous/Developmental, Accidental Failure). Eight mode calibrations with named failure modes: Map-Table Heroics (military/war), Stat-Sheet Spectacle (systems-driven progression), Perpetual Chase Blur (thriller), Shock Carousel (horror violence), Clean Hit Myth (crime/noir), Incident Theater (domestic violence drama), Aphoristic Carnage (literary violence), City-Scale Weightlessness (superhero/speculative). Explicit audit procedure (claim lock → build artifacts → rate channels → apply flags → synthesize). Output template. Firewall compliance. Stacks with Horror Craft, Mystery/Thriller Architecture, Emotional Craft, Character Architecture, AI-Prose Calibration, Literary Craft, Female Interiority; feeds Pass 11 synthesis.
- **Force Architecture level-setting brief** (craft/force-architecture-level-setting.md, 496 lines, three-model synthesis). Companion research brief grounding the audit in cognitive science, narrative theory, violence theory, and practitioner craft knowledge. Eight theoretical sections: SPECT (situation model construction under stress), event-indexing models (Zwaan/Langston/Graesser five-dimension tracking), event segmentation (Zacks boundary-marking), Sternberg's suspense architecture (suspense > surprise in force scenes), Clausewitz friction (plan-execution gap as cross-genre credibility bridge), the body problem (Disembodied Combatant, sensory hierarchy shifts, tachypsychia, auditory exclusion, experience-level differentiation, distance-difficulty scaling), Arendt/Scarry violence theory (violence/power distinction, bodily representation), Hayakawa abstraction ladder (compression vs. incoherence distinguish tool), consequence persistence (Stark coercive-control model, five-cost tracking). Full failure mode taxonomy (25 named patterns). Positive-case technique extraction across 8 modes: O'Brien truth-by-contradiction / Haldeman temporal estrangement / Cook chronicler distance (military), Dinniman environmental comedy-as-friction / Wight advancement-cost coupling (progression), Child preparation-as-suspense / Ludlum identity-through-combat (thriller), King domestic-space contamination / Jones cultural-weight violence (horror), Hammett consequence-networking / Ellroy institutional complicity (crime/noir), micro-escalation architecture / credibility asymmetry (domestic), McCarthy violence-as-epistemological-event / Morrison violence-as-historical-testimony / O'Connor revelatory violence (literary), power-scale clarity / collateral consequence architecture (superhero/speculative). Eight-mode calibration evidence with named failures and false positive risks. Distinguish problem analysis with seven operational tests, four outcome classes, and seven false-positive controls.

## v0.4.11 - 2026-02-20

### Added
- **Mystery/Thriller Architecture audit** (genre/mystery-thriller-architecture.md, 653 lines, three-model synthesis). Genre-specific audit evaluating whether mystery/thriller information architecture generates inference, urgency, and surprise-with-inevitability or merely assembles genre components. Core concept: "informational drift" — clues, suspects, reversals, and deadlines present but failing to generate hypothesis formation, prediction revision, felt urgency, or satisfying surprise. Anchor insight: information the reader possesses but isn't working with is structurally parallel to horror that doesn't produce dread and literary craft that doesn't do work. Six integration dimensions (IE Information Economy, RH Red Herring Integrity, IL Investigation Legibility, CM Clock Mechanics, RC Reveal Choreography, SF Solution Fairness) with Integrated/Partial/Detached ratings. 28 named diagnostic flags: IE-1 Fog of Facts, IE-2 Clue Starvation, IE-3 Asymmetry Collapse, IE-4 Evidence Island, IE-5 Signal Collapse; RH-1 Noise Cannon, RH-2 Decoy Without Spine, RH-3 Immortal Herring, RH-4 Orphaned Thread, RH-5 Herring Hierarchy; IL-1 Leap Detective, IL-2 Procedure Theatre, IL-3 Oracle Investigator, IL-4 Blind-Side Investigator, IL-5 Passive Catalyst; CM-1 Cosmetic Clock, CM-2 Clock Freeze, CM-3 Clock Without Cost, CM-4 Deadline Detour; RC-1 Reverse Gear Reveal, RC-2 Twist Before Foundation, RC-3 Premature Closure, RC-4 Reveal Pile-Up, RC-5 Explain Patch Ending; SF-1 Cheat Ending, SF-2 Invisible Culprit, SF-3 Obvious Culprit Drift, SF-4 Retroactive Collapse. Four required tracking artifacts: Clue Ledger (with Reader-Tractable? column), Red Herring Ledger (with Quality vs. True Solution column), Clock Pressure Map, Fairness Matrix. Pattern interpretation protocol with six checks, "Reading the Map" guide (8 dimension-combination patterns including Pressure-Puzzle Split), and blast radius classes. Ten severity hard gates (Architecture Void, Cheat Ending, Inferential Inaccessibility, Clock Disconnect, Investigation Opacity, Red Herring Dominance, Retroactive Incoherence, Culprit Underrepresentation, Reveal Timing Failure, Hybrid Contract Breach). Seven distinguish tests (Accessibility, Inference, Clock Conversion, Retroactive Coherence, Misdirection Foundation, Architecture-Ambiguity, POV Fairness) with four-class decision matrix and false-positive guardrails. Special Caution Zones (cozy, noir/hardboiled, literary mystery, inverted mystery, psychological thriller). Nine subgenre calibrations with named failure modes: The Locked Room Lecture (classic whodunit), Tea-Shop Stall Loop (cozy), Clipboard Carousel (procedural), Smoke Without Signal (hardboiled/noir), Unreliable Escape Hatch (psychological thriller), The Bulletin Board (conspiracy/political), Kitchen Twist Roulette (domestic), The Transparent Trap (inverted), The Beautiful Fog (literary hybrid). Dynamic literary mode trigger for hybrid recalibration. Explicit output format templates. Firewall compliance. Stacks with Genre Modules: Mystery and Thriller (contract), Emotional Craft (transmission), Horror Craft Integration (pressure-system parallel), Literary Craft (ambiguity), AI-Prose Calibration (generic fluency); feeds Pass 11 synthesis.
- **Mystery/Thriller Architecture level-setting brief** (genre/mystery-thriller-architecture-level-setting.md, 384 lines, three-model synthesis). Companion research brief grounding the audit in narrative theory, cognitive science, and practitioner craft knowledge. Eight theoretical sections: Sternberg's narrative interest triad with Brewer-Lichtenstein cognitive frame extensions (frame-matching/frame-completion/frame-shifting), Barthes' hermeneutic code (snares/equivocations/partial answers/suspended answers/disclosure mapped to audit dimensions), Eco's model reader (accessibility vs. tractability distinction), Todorov's typology with directional movement insight (mystery expands, thriller narrows), fair-play traditions and diagnostic limits (epistemic parity, prospective vs. retroactive fairness), cognitive psychology (hypothesis formation, model starvation/model lock, predictive processing, misdirection from magic performance studies via Kuhn/Rensink, the "click" of recognition, jigsaw vs. ball-of-twine architecture), craft practitioners (Christie assumption exploitation, Highsmith emotional suspense, Child present-moment urgency, French memory-as-investigation, Flynn epistemic warfare). Full failure mode taxonomy (28 named patterns including Pressure-Puzzle Split hybrid failure). Positive-case exemplar sets across 8 subtypes: Christie/Sayers (classic whodunit), Connelly/French (procedural), Chandler/Highsmith (noir), le Carré/Larsson (conspiracy), Flynn/Highsmith (psychological), French/Ware (domestic), Iles/Columbo (inverted), Eco/Auster/Bolaño (literary hybrid). Nine-subgenre calibration evidence with named failures and false positive risks. Distinguish problem analysis with seven operational tests, four outcome classes, and six false-positive controls.

## v0.4.10 - 2026-02-20

### Added
- **Horror Craft Integration audit** (genre/horror-craft.md, 593 lines, three-model synthesis). Genre-specific audit evaluating whether horror apparatus produces sustained dread, destabilization, and felt consequence or merely delivers horror-coded content. Core concept: "inert dread" — horror present in the plot summary but absent from the reading experience. Anchor insight: horror that escalates in facts but not in felt consequence is structurally parallel to literary craft that doesn't do work and worldbuilding that doesn't integrate. Six integration dimensions (DA Dread Architecture, UD Uncertainty Design, TC Threat Choreography, CE Consequence Embodiment, AP Atmosphere/Image Pressure, ER Ending Residue) with Producing/Partial/Inert ratings. 23 named diagnostic flags: DA-1 Static Dread Loop, DA-2 Kindless Escalation, DA-3 Escalation Cliff, DA-4 Dread Fatigue, DA-5 Anticipatory Deflation; UD-1 Confusion Smog, UD-2 Cheap Certainty, UD-3 Stated Instability, UD-4 Hypothesis Starvation; TC-1 Monster Before Mystery, TC-2 Mystery Without Teeth, TC-3 The Diminishing Reveal, TC-4 Visibility Drift; CE-1 Trauma Without Trace, CE-2 Immunity Bubble, CE-3 Damage as Decoration; AP-1 Gothic Wallpaper, AP-2 Symbolic Static, AP-3 Sensory Anesthesia, AP-4 Beautiful Distance; ER-1 Catharsis Betrayal, ER-2 Aftertaste Null, ER-3 Resolution Collapse. Three tracking artifacts: Horror Pressure Map (required), Consequence Ledger (recommended), Uncertainty Traction Log (optional). Pattern interpretation protocol with six named checks and "Reading the Map" guide. Nine severity hard gates (Pressure Void, Ending Contract Failure, Consequence Void, Dread Stasis, Epistemic Failure, Climax Underperformance, Reveal Timing Failure, Atmosphere Without Engine, Residue Null in Haunt Contract). Six distinguish tests (Interpretive Traction, Contract Coherence, Cost Continuity, Pressure Integrity, Transgression Purpose, Affect Calibration) with decision matrix and false-positive guardrails. Special Caution Zones (quiet horror, cosmic horror, horror-comedy, transgressive fiction). Nine subgenre calibrations with named failure modes: Mind Maze Without Thread (psychological), Abyss on a Leash (cosmic), Meat Without Meaning (body), Haunted Furniture Syndrome (domestic), Ritual Postcard (folk), Shock Treadmill (splatter/transgressive), Velvet Rot (Gothic/atmospheric), The Artful Flinch (literary horror), The Laser-Gun Safari (sci-fi horror). Explicit output format templates. Firewall compliance. Stacks with Genre Module: Horror (contract), Emotional Craft (transmission), Literary Craft (Beautiful Distance), Female Interiority (aestheticized suffering), Consent Complexity (violation/conditioning), AI-Prose Calibration (sensory flattening); feeds Pass 11 synthesis.
- **Horror Craft level-setting brief** (genre/horror-craft-level-setting.md, 328 lines, three-model synthesis). Companion research brief grounding the Horror Craft audit in horror theory, cognitive science, and practitioner craft knowledge. Nine theoretical sections: Carroll's art-horror (compound cognitive-affective mechanism, monster taxonomy — fusion/fission/magnification/massification), Freud's uncanny (familiar-made-strange, recognition before corruption), Kristeva's abjection (boundary collapse, corpse as ultimate manifestation, proximity requirement), Robin Wood's return of the repressed (monster as social/material pressure, structural isomorphism between external threat and internal state), Fisher's weird/eerie (absence-based and wrongness-based horror modes), Ligotti's philosophical horror (consciousness as horror, cosmic dread without monsters), King's terror hierarchy (terror > horror > revulsion), narrative psychology (anticipatory anxiety/predictive processing, habituation, cognitive appraisal, uncertainty tolerance). Full failure mode taxonomy (22 named patterns). Positive-case exemplar sets: Jackson/Harris/Tremblay (psychological), Lovecraft/VanderMeer/Langan/Ligotti (cosmic), Cronenberg/Machado/Barker/Koja (body), Enriquez/Oyeyemi/King/Due (domestic), Link/Jackson/Schweblin (literary), Barker/Ketchum/Palahniuk (transgressive). Folk Horror Chain structural pattern. Nine-subgenre calibration evidence with named failures and false positive risks. Distinguish problem analysis with six operational tests and five false-positive controls.

## v0.4.9 - 2026-02-20

### Added
- **Literary Craft Deep Dive audit** (craft/literary-craft.md, 575 lines, three-model synthesis). Cross-genre audit evaluating whether literary-mode ambitions do structural work or are cosmetic sophistication. Core concept: "ornamentation, not complexity." Anchor insight: literary mode that doesn't do work is structurally identical to worldbuilding that doesn't do work. Five primary integration dimensions (PA Prose Architecture, TF Thematic-Form Integration, IA Image Architecture, ST Subtext/Tonal Control, RA Recognition Architecture) plus one cross-cutting dimension (VA Voice Architecture). 22 named diagnostic flags: PA-1 Verbal Wallpaper, PA-2 Register Cosplay, PA-3 Purple Archipelago, PA-4 Difficulty Without Reward, PA-5 Workshop Finish; TF-1 Thesis Statement Novel, TF-2 Structural Stunt, TF-3 Thematic Furniture, TF-4 Interpretive Vacuum; IA-1 Dead Metaphor Garden, IA-2 Orphan Image, IA-3 Symbol Tyranny, IA-4 Sensory Wallpaper; ST-1 Transparent Character, ST-2 Explanatory Impulse, ST-3 Tonal Drift, ST-4 Ironic Collapse; RA-1 Near Miss, RA-2 Generic Recognition, RA-3 Insight Lecture, RA-4 Recognition Without Preparation; VA-1 Voice as Veneer, VA-2 Workshop Neutral, VA-3 Posture Mismatch. Three tracking artifacts: Literary Architecture Map (required), Scene Pressure Grid (required), Recognition Arc Log (optional). Central Defamiliarization Test (perception vs. appreciation). Eight severity hard gates. Six distinguish tests with decision matrix, false-positive guardrails, and Special Caution Zones (debut manuscripts, translated work, lyric novels). Nine genre-hybrid calibrations with named failure modes: Elegant Plateau (literary realist), Velvet Brake (literary thriller), Metaphor Shelter (literary SFF), Beautiful Rot (literary horror), Case and Chorus Split (literary crime), Competent Fog (upmarket), Structural Stunt elevated (experimental/lyric), Period Piece (literary historical), Beautiful Recollection (literary memoir/CNF). 2-of-5 activation rubric. Explicit output format templates. Firewall compliance section. Stacks with Emotional Craft, AI-Prose Calibration, Female Interiority, SFF Worldbuilding Integration; feeds Pass 11 synthesis.
- **Literary Craft level-setting brief** (craft/literary-craft-level-setting.md, 302 lines, three-model synthesis). Companion research brief grounding the Literary Craft audit in critical theory and practitioner craft knowledge. Nine theoretical sections: Shklovsky's defamiliarization (perception vs. automatization), New Criticism diagnostic method (Brooks on functional metaphor, Empson on productive ambiguity), Booth on rhetorical choice (voice as argument architecture), Phelan on rhetorical narratology (form as rhetorical action), Wood on free indirect style (consciousness management), contemporary craft perspectives (Saunders "bouncer at Club Story," Smith "Two Paths for the Novel," Baldwin, Robinson), Wallace on postmodern irony (foundation for Ironic Collapse), McGurl on Program Era (workshop-homogeneity problem). Full failure mode taxonomy across five categories (22 named flags with theoretical provenance). Positive-case exemplar sets: Morrison/Ferrante/Cusk (literary realism), Carver/Johnson/Berlin/Offill (minimalism), Pynchon/Wallace/Rushdie (maximalism), Sebald/Carson/Rankine (structural form), Ishiguro/Le Guin/McCarthy/Atwood/French (hybrid modes). Cross-genre calibration evidence. Distinguish problem analysis with operational tests and false-positive controls.

## v0.4.8.1 - 2026-02-20

### Added
- **Female Interiority level-setting brief** (craft/female-interiority-level-setting.md, 256 lines). Companion research brief grounding the Female Interiority audit in cognitive science and narratology. Three theoretical pillars: Dorrit Cohn's tripartite consciousness model (Psycho-Narration, Quoted Monologue, Narrated Monologue) providing syntactic markers for the four interiority tiers; Lisa Zunshine's Theory of Mind framework mapping recursive intentionality orders to interiority depth; Susan Lanser's Fictions of Authority connecting gendered voice modes to interiority vulnerability patterns. Includes: Cohn-to-tier mapping table, Voice-Context Vulnerability Matrix (3 voice modes × 7 pressure contexts), structural cascade analysis (Midpoint Pivot and Lie Collapse as interiority failure amplifiers), concrete detection mechanics (mode collapse, verb category shift, ToM order drop, emotional label substitution, reset signal), 11 positive-case exemplars with craft technique identification (Ferrante, Morrison, Milan, Jackson, Jemisin, Tolstoy, Woolf, Machado, Larsen, Anderson, Mantel), 5 cross-case success signals, intentionality problem reasoning with genre-specific challenges, full source set (theory, craft criticism, exemplar fiction). Follows the level-setting companion pattern established by cozy-tag-level-setting.md and sff-worldbuilding-level-setting.md.

## v0.4.8.0 - 2026-02-20

### Added
- **SFF Worldbuilding Integration audit** (specialized audit, genre/sff-worldbuilding.md, 501 lines, three-model synthesis). New audit evaluating whether speculative worldbuilding does narrative work — distinct from the Genre Module: SF/F which handles consistency. Core concept: "inertness, not inconsistency." Five integration dimensions (Cognitive, Thematic, Prose, Social, Emotional) with Integrated/Partial/Detached ratings. 20 named diagnostic flags across five families: World-Character (WC-1 Earth Minds in Alien Bodies, WC-2 The Tourist, WC-3 Wallpaper Competence, WC-4 The Undeformed), Exposition Craft (EC-1 The Wiki World, EC-2 Exposition Rigor Mortis, EC-3 The Mode Mismatch, EC-4 Late-Stage Explaining), Thematic Integration (TI-1 The Cellphone-Proof Theme, TI-2 The Passive Physics Engine, TI-3 Generic Dilemma in Exotic Dress, TI-4 Climax Decoupling), Scale/Depth (SD-1 The Aesthetic Shell, SD-2 Social Architecture Without Social Physics, SD-3 The Load-Bearing Wall That Isn't, SD-4 Scope Inflation Drift), Prose-Level (PL-1 The Noun-Swap World, PL-2 Description Island, PL-3 Register Reversion, PL-4 Metaphor Import Leak). Three tracking artifacts: Integration Map (required), Load-Bearing Ledger (required), Pressure Event Log (optional). World Pressure Loop diagnostic chain. Six Distinguish tests with decision matrix and false-positive guardrails. Eight severity hard gates with numerical thresholds. Eight subgenre calibrations with named failure modes (The Elegant Irrelevance, The Grand Tour, The Appendix Illusion, The Convenient Masquerade, Neon Skin No Bite, Randomness Alibi, Metaphor Cage, The Stat Sheet Treadmill). Cross-genre structural isomorphisms for author legibility. Stacks with Genre Module: SF/F; feeds Pass 11 synthesis.

## v0.4.6.0 - 2026-02-20

### Added
- **Intake Router v1** — single entry point (`/start`) that routes users to the right workflow in 2–3 questions
  - **Question 1 (Artifact):** "What do you have right now?" — idea, fragments, partial draft, complete draft, series. Deterministic thresholds for classification when material is provided rather than self-reported (based on narrative continuity, not word count).
  - **Question 2 (Goal, conditional on Artifact):** Options change per artifact state — prevents offering irrelevant goals. E.g., "Check submission readiness" only appears for complete drafts.
  - **Question 3 (Constraint/Operator modifiers):** Deadline, AI-assisted text, nonfiction, sensitive/legal risk, editing for someone else, facilitating a writing group, co-authoring. Multiple selections allowed.
  - **Fallback disambiguator:** When confidence is low, one tiebreaker question maps to three buckets (start drafting / improve existing / evaluate readiness).
  - **Complete route map** with status flags (built, gap, partially built) for all artifact × goal × constraint combinations.
  - **Gap protocol:** When route target isn't built, acknowledge honestly, offer closest available workflow, name what won't be covered.
- **Router integration in Core DE intake:** When user arrives via `/start`, router output (artifact, goal, constraint flags) skips redundant intake questions.
- New `/start` command (9 commands total, up from 8).

### Changed
- **Genre calibrations reordered:** Literary Fiction first (most common primary module), then Genre-Bending/Literary Mode, then alphabetical (Horror, SF, Romance/Erotic). Previously Romance/Erotic was first.
- **Genre calibrations generalized:** Genre-specific detail in core pass descriptions moved to on-demand genre modules. Core passes are now genre-neutral with summary + pointer to full module. All diagnostic machinery remains available when the genre module is activated.
- **Register Uncertainty diagnostic updated** with multi-genre example (Literary Thriller Horror interrogation scene). The diagnostic now demonstrates register conflict using three registers rather than four, making the core concept clearer.
- **Interiority Preservation audit expanded** from intimate scenes to all high-intensity scenes (combat, interrogation, crisis, intimate encounter). Genre-specific applications section covers Action/Thriller, Romance/Erotic, Horror, and Literary with cross-references to relevant modules.
- **AIC-7: Discourse Leak** integrated into AI-Prose Calibration (7 flag families total). Five evidence categories: Assistant Frame, Hedge Drift, Template Loop, Lexical Convergence, Commitment Evasion. Includes evidence burden requirements, false-positive guardrails, and three-step audit workflow.
- **Examples generalized** across reference files. Character-specific and manuscript-specific examples replaced with role-based descriptions (e.g., "Protagonist" instead of named characters, generic series descriptions instead of titled works). Teaching content preserved; specificity improved for broader applicability.
- **Reference implementation paths normalized.** Internal filesystem paths and project-specific directory names replaced with portable references.
- **Specialized-audits reference directory restructured** into three subdirectories: `craft/` (universal audits), `genre/` (form/genre-specific audits), `tag/` (cross-genre modifier audits). All reference paths updated. Prior changelog entries retain original paths as historical record.
- **Female Interiority audit expanded** from intimate-scene focus to universal craft audit (v0.4.8, three-model synthesis). New diagnostic framework: "interiority thinning" as core concept with four-level spectrum (Full / Thinned / Functional / Absent). 20 named diagnostic flags across four categories (Interiority Thinning IT-1–IT-12, Gaze & Observation GO-1–GO-4, Agency AG-1–AG-4, Relationship RF-1–RF-2). New flags from synthesis: Competence as Costume (IT-8), Caregiver Erasure (IT-9), Ensemble Fade (IT-10), Borrowed Stakes (IT-11), Refrigerated Consequence (IT-12), The Sexy Lamp (GO-4), The Smurfette (AG-4). Interiority Map with named reading patterns (Solitude Spike, Relational Dependency). Severity hard gates for reproducible calls. Five-test Distinguish framework with decision matrix. Genre calibration matrix with named failure modes (Desire Dependency, Generic Terror, The Case as Personality, The Gender-Swapped Archetype, The Aestheticized Woman, Minds in Corsets, Body-Without-Mind). Synthesis handoff spec for Pass 11.
- **APODICTIC branding** adopted in README. Full package rename deferred to publication.

### Notes
- Existing commands (`/develop-edit`, `/pre-writing`, `/diagnose`, etc.) remain functional as direct-access shortcuts. The router is the recommended entry point for new users.
- The router implements the four-axis classification model (Artifact × Goal × Operator × Constraint) from the Publication Requirements. Operator is inferred from context or self-reported in Q3, not asked as a separate question.
- Genre module activation is unchanged: modules load when genre is specified in contract or detected during intake. The core pass generalization means the core framework loads faster and doesn't assume any particular genre.

## v0.4.5.0 - 2026-02-20

### Added
- **Pre-Writing Pathway** — new skill and `/pre-writing` command guiding writers from idea to draftable structure without a manuscript
  - **Phase 0: Writer Mode Calibration** — detects architecture-first vs. discovery-first writers; adjusts pathway pressure, field tolerance, and re-entry interpretation accordingly
  - **Seed Inventory** (Phase 1) — maps writer's raw idea onto 8 seed types (premise, character, world, feeling, scene, theme, genre instinct, comp)
  - **Uncertainty/Assumption Ledger** — tracks confidence (Decided/Provisional/Unknown) and dependencies for every structural decision; persists into Structural Plan and feeds Re-Entry Diff
  - **Readiness Gates** — Storyable gate (after Phase 3: premise + engine + tension cohere) and Draftable gate (before Phase 5: spine candidate + ending instinct + arc states + known unknowns)
  - **Option Architecture** (Phase 4) — presents 2–3 viable spine candidates with tradeoffs instead of converging to one recommendation
  - **Complexity Budget** (Phase 4B) — explicit first-draft scope caps for POV count, subplots, timeline complexity, world-building scope
  - **Prospective Contract** — same schema as standard contract but built from intent; embedded in Structural Plan output
  - **Minimal Viable Plan** — prose-format fallback for discovery writers who pass the storyable gate but not the draftable gate
  - **Re-Entry Diff Protocol** (Phase 6) — classifies divergences between prospective contract and actual manuscript as: intentional evolution, signal loss, structural drift, or expected discovery
  - **Anti-sycophancy controls** — mandatory Hard Risks section, real readiness gates (not rubber stamps), option architecture prevents premature validation, ledger prevents false confidence
- **Output artifact conventions** aligned with Core DE naming: `[Project]_Structural_Plan_[runlabel].md`, `[Project]_MVP_[runlabel].md`, `[Project]_Reentry_Diff_[runlabel].md`
- **AI-Prose Calibration audit** (specialized audit #18) — diagnoses prose-level failure patterns in AI-generated or AI-assisted text
  - 6 flag families: AIC-1 Generic Hand (voice singularity), AIC-2 Velvet Fog (scene fog + lexical genericism), AIC-3 Echo Stack (structural repetition), AIC-4 Register Seams (multi-source splicing), AIC-5 Puppet Dialogue (mouth uniformity), AIC-6 Continuity Smear (world-model failures)
  - 3-tier severity: Spot / Pattern / Systemic
  - Required outputs: flag summary, top 3 systemic risks, contamination map, Keep/Recast/Replace salvage plan, Pass 11 readiness impact note
  - Contract intake integration: drafting-method question triggers automatic activation
  - Model-agnostic design: targets prose quality categories, not model-specific tells

### Notes
- The pre-writing pathway produces a prospective contract that becomes the baseline when the writer returns with a draft. Core DE intake uses it as a starting hypothesis; the Re-Entry Diff surfaces what the writer discovered, lost, or drifted from.
- Discovery-first writers may exit with an MVP instead of a full Structural Plan. MVPs do not feed the Re-Entry Diff — standard intake runs from scratch, with the MVP as context.
- AI-Prose Calibration frames AI-generated text as raw material to salvage, not contamination to detect. The audit is useful for any prose exhibiting the flagged patterns, regardless of origin.

## v0.4.4.8 - 2026-02-18

### Added
- **Severity Honesty Protocol** — 4 rules preventing LLM sycophancy in severity assignments (softening Must-Fix to Should-Fix, hedge language, finding one positive passage to downgrade systemic flags)
- **Severity Floor Rules** — 3 structural constraints ensuring diagnostic coherence (Weak core-promise axis requires Must-Fix flag; systemic blast radius caps verdict; high flag volume caps positive verdicts)
- **Pass-Level Output Protocol** — standardized output ordering for evaluative passes: Analysis → Rejection Memo → Priority Leaks → Strengths. Requires rejection memo in every evaluative pass (Pass 1, 2, 5, 8, and all Full DE passes). Strengths cap tied to leak count.
- **Rejection Memo** as a required component of both individual passes and synthesis ("The Strongest Case Against")
- **Revision Checklist** replaces Surgery List — author-facing table with What / Why / Effort columns (Low/Medium/High effort replaces Must-Fix/Should-Fix/Could-Fix severity labels)

### Changed
- **Core DE Synthesis completely rewritten** as editorial letter format:
  - Processing Protocol: 5-step internal process (Intent Check → Root Cause → Triage → Adversarial Self-Check → Write Letter)
  - Presentation Format: 7 required sections (Title Block, The Short Version, What the Book Does Best, What Needs Work, Revision Checklist, The Strongest Case Against, Appendices)
  - Tone and Voice guidance (avoid framework jargon, mechanistic transitions, strength-padding; use direct declarative assessment, embedded line references, bolded thesis-statement headings)
  - Key principle: processing order ≠ presentation order (self-check runs before writing but appears in appendix)
- **Core DE Deliverables simplified** to Editorial Letter + Diagnostic State (removed Surgery List, Revision Order, Top 10 Reader Questions)
- **Full DE Editorial Letter updated** with 5 scaling differences from Core DE + Pass 11 integration guidance
- **Output Constraints updated**: "Maximum 25 surgery list items" → "Maximum 10 revision checklist items (Core DE); 15 (Full DE)"
- Negative-first ordering: Priority Leaks appear before Strengths in all pass outputs
- Strengths must be specific and evidence-based with citation; capped relative to leak count

### Notes
- This version addresses the documented LLM tendency to soften editorial findings, producing editorial letters that read as one informed voice talking about a book rather than a framework generating output.

---

## v0.4.4.6 - 2026-02-17

### Added
- **Cozy level-setting brief** (`references/cozy-tag-level-setting.md`) — standalone research brief covering BISAC/Thema taxonomy, Circana/PW market data, recovery-psychology research (Rieger et al., Rieger & Bente), narrative-resistance findings (Moyer-Gusé et al.), social connectedness research (Wildschut et al., Juhl et al.), and cross-media cozy scholarship
  - Evidence labeling system: `SOURCE-VERIFIED` vs. `MARKET INFERENCE`
  - Lineage: Codex53 research brief
- **Inline Level-Setting Notes** added to Cozy Tag audit summarizing key external evidence

### Changed
- Tag audit family standard: every tag audit includes an inline Level-Setting Notes section grounding axes in external evidence. A standalone companion brief is the exception for tags with unusually deep evidence bases (cozy), not the standard.
- Philosophical Tag audit: family context updated to reflect inline-first standard
- Specialized-audits reference list: added `references/cozy-tag-level-setting.md`

### Notes
- The discipline of asking "what does the market say? what does the research say?" is institutionalized in the inline section. The cozy brief stays because the evidence genuinely warrants it — BISAC codes, peer-reviewed psych, game-studies scholarship. Most tags won't need a standalone file.

---

## v0.4.4.5 - 2026-02-16

### Added
- **New tag audit: Philosophical Tag** (`references/philosophical-tag.md`)
  - Second audit in the tag audit family (after Cozy)
  - Seven axes: Question Architecture, Dramatic Embodiment, Counterposition Strength, Conceptual Progression, Philosophical Feel, Legibility Under Complexity, Resolution Ethics
  - Philosophical Intensity Spectrum (High / Medium / Low) with severity calibration
  - 21 named diagnostic flags: Topic Fog, Question Collapse, Question Multiplication, Seminar Scene, Parallel Tracks, Illustration Mode, Straw Army, Mouthpiece Asymmetry, Vanishing Objection, Broken Record, Volume Escalation, Late Pivot Without Foundation, Closed Loop, Explanatory Reflex, Opacity Posture, Jargon Fog, Abstraction Drift, Decoration Philosophy, Resolution Collapse, Ambiguity Dodge, Thesis Snap
  - PH flag family (PH-1 through PH-9) with named pattern mappings
  - Cross-genre calibration matrix (Literary, SF, Horror, Fantasy, Thriller, Historical, Mystery, Romance)
  - Axis E (Philosophical Feel) addresses the experience-layer dimension: does the reader *think alongside* the text?
  - Routing distinction: Banister evaluates rhetorical fairness; Dialectical Clarity evaluates argument structure; this audit evaluates philosophical *delivery as experience*
  - Level-setting notes on Thema/BISAC metadata and narrative-transportation research
  - Lineage: Codex53 v0.1 draft → Opus revision

### Changed
- Specialized-audits skill description updated with philosophical/tag audit triggers
- Specialized-audits SKILL.md Tag Audits table: added Philosophical Tag row
- Core SKILL.md Tag Audits section: added Philosophical Tag entry
- Plugin structure note updated: "17 deep-dive audits, 2 tag audits, and 4 research modes"
- All skill versions bumped to 4.4.5

---

## v0.4.4.4 - 2026-02-16

### Added
- **New tag audit: Cozy Tag** (`references/cozy-tag.md`)
  - First audit in the new **tag audit family** — experience-layer diagnostics that sit on top of any parent genre's structural contract
  - Cozy Delivery Model with six axes: Safety Envelope, Softness Signals, Belonging Engine, Recovery Rhythm, Everyday Stakes Presence, Restoration Arc
  - Cozy Intensity Spectrum (High / Medium / Low) with severity calibration per intensity level
  - 18 named diagnostic flags: Trapdoor, Ratchet Without Release, Cruelty Leak, Cozy Skin, Comfort Prop, Warmth Collapse, Relational Vacuum, Protagonist Island, Unrepaired Breach, Summary Recovery, Adrenaline Stack, Fridge Recovery, Crisis Saturation, Inert Domesticity, Escalation Addiction, Pyrrhic Landing, Dangling Thread, Tonal Whiplash Landing
  - CZ flag family (CZ-1 through CZ-8) with named pattern mappings
  - Cross-genre calibration matrix (Mystery, Fantasy, Romance, Horror, Thriller, SF, Literary)
  - Anchor + Interacting Lenses analysis method (not sequential checklist)
  - High-Stakes Cozy misread section addressing the most common beta-reader misdiagnosis
  - "Return address" concept for Belonging Engine axis
  - Lineage: Codex53 v0.1 draft → Opus revision

### Changed
- Specialized-audits skill description updated with cozy/tag audit triggers
- Specialized-audits SKILL.md adds Tag Audits subsection in audit listing
- Core SKILL.md adds Tag Audits section between Specialized Audits and Research Modes
- Plugin structure note updated: "17 deep-dive audits, 1 tag audit, and 4 research modes"

### Notes
- The tag audit family establishes a new architectural category: experience-layer diagnostics distinct from genre audits (structural contracts). Future tag audits (Erotic, Dark/Grimdark, Literary, Hopepunk) will follow the same pattern: experience model with named axes, named diagnostic flags, intensity spectrum, cross-genre calibration, anchor + interacting lenses method.
- This revision also introduces the genre/tag distinction as a framework-level concept, which will inform the broader restructuring tracked in Publication Requirements.

---

## v0.4.4.3 - 2026-02-16

### Added
- **Plot Architecture audit expanded** from 39 spines / 9 families to 48 spines / 12 families:
  - Family 10 (Rhythm & Intensity Engines): Wave/Pulse Structure, Lullaby Structure, Pressure Cooker
  - Family 11 (Format & Frame Engines): Episodic/Modular, Clinical Case File, Nested Dolls, Talisman Structure
  - Family 12 (Transformation & Identity Journeys, Extended): Heroine's Journey (Murdock), Seven-Point Structure (Dan Wells)
  - Each new spine includes full logic gates, severity levels, and genre cross-references
  - Diagnostic Quick Reference expanded with 7 new symptom → diagnosis rows
  - Spine Compatibility Matrix expanded with 11 new combination entries
- **New specialized audit: Plot Selection & Coaching** (`Specialized_Audits/Specialized_Audit_Plot_Selection_Coaching.md`)
  - Upstream structural guidance: works before or alongside Plot Architecture
  - Phase 1: Story Concern Mapping (reader feeling, engine type, truth relationship)
  - Phase 2: Spine Selection Protocol with decision tree (single-spine and multi-spine)
  - Phase 3: Structural Technique Overlays (TV/Serial format, Game-Inspired format)
  - Phase 4: Hybrid Structure Design (layer model: micro/meso/macro/meta, conflict detection, handoff types)
  - Phase 5: Structural Triage for stuck drafts (symptom → diagnosis → prescribe)
  - Phase 6: Pre-Drafting Structural Plan template
- **New specialized audit: Fantasy & Series Architecture** (`Specialized_Audits/Specialized_Audit_Fantasy_Series_Architecture.md`)
  - Part I: 5 fantasy-specific spines with logic gates (Anti-Hero's Journey, Folkloric/Mythic Mosaic, Liminal Drift, Fractured Chronicle, Ritual Pattern)
  - Part II: 6 series-level architectural patterns (Expanding Quest, Character Web, Revolving Protagonist, Seasonal Arc, Mystery Box/Revelation Slow Burn, Empire Cycle/Generational Arc)
  - Part III: 3 series rhythm patterns (Convergent-Divergent Cycle, Event Spine, Mythic Undertow)
  - Part IV: Cross-reference tables linking fantasy spines to general spines and series architectures to per-volume spine choices

### Changed
- `Module_Index.md` updated to v3.5: new audits registered in table, file tree, statistics (now 32 total modules/audits/modes/passes/pathways), coverage notes, and "When to Use What" quick reference.
- Plot Architecture audit description in Module Index now reflects 48 spines / 12 families.

### Notes
- Source material: conversational exploration document ("Alternatives to 3 Act Plot Structures") de-duplicated against existing audit, reformatted into logic-gate structure, and split across three deliverables by function (diagnosis, coaching, architecture).
- Overlapping structures (Freytag, Spiral, Fugue, Braided, Rashomon, Hero's Journey, Quest, Siege) were already in the audit; only genuinely new spines were added.
- Structures better understood as presentation techniques (TV/Serial, Game-Inspired) were placed in the Selection & Coaching audit rather than as spines in the Plot Architecture audit.

## v0.4.4.2 - 2026-02-13

### Added
- New top-level `README.md` with public naming, shorthand, and canonical-doc pointers.

### Changed
- Public-facing product name normalized to `APODICTIC Development Editor` with shorthand `APDE`.
- `SKILL.md` and `Module_Index.md` now include explicit brand alias guidance while retaining legacy filenames for compatibility.
- Output templates now include framework footer branding:
  - `Templates/Contract_Template.md`
  - `Templates/Diagnostic_State_Template.md`
  - `Templates/Reverse_Outline_Template.md`
- Pass 11 module header and output template now use APDE branding for generated reports.

### Notes
- This is a naming and documentation normalization patch; no analysis logic changed.

## v0.4.4.1 - 2026-02-13

### Added
- Formal changelog introduced.
- Canonical-source declaration that `SKILL.md` is the operational source of truth.
- Explicit runlabel convention for core outputs (date-based `YYYY-MM-DD`, optional agent prefix such as `codex53_2026-02-13`).
- Optional Pass 11F (Adversarial Reader Stress Test) surfaced in module documentation where missing.

### Changed
- `SKILL.md` now defines runlabel-based output naming for core passes and clarifies `Diagnostic_State.md` as a rolling state file.
- `SKILL.md` project integration now accepts either `Contract_and_Controlling_Idea.md` or `[Project]_Contract*.md`.
- `SKILL.md` now requires initialization of `Diagnostic_State.md` from `Templates/Diagnostic_State_Template.md` when absent.
- `Module_Index.md` aligned with current pass architecture, including optional 11F and updated output conventions.
- `AI_Development_Editor_Complete_v0.4.4.md` Pass 11 section reframed as a condensed summary with explicit operational authority delegated to `SKILL.md` and `Pass_11_Critical_Quality_Market_Viability_v2.md`.

### Fixed
- Documentation drift between framework index/spec documents on Pass 11 coverage and output naming.
- Ambiguity around first-run bootstrap behavior for `Diagnostic_State.md`.

### Notes
- This release is a governance and consistency patch: no new core analysis passes were added.
- Suggested future process: append entries here whenever pass behavior, output contracts, or required artifacts change.

## v0.4.4 - 2026-02-02 to 2026-02-12 *(historical backfill; staged rollout)*

### Added
- Consolidated reference document: `AI_Development_Editor_Complete_v0.4.4.md`.
- Evaluative gate module: `Pass_11_Critical_Quality_Market_Viability_v2.md` with sub-passes `11A-11F`.
- QF flag family (`QF-1` through `QF-7`) and required Hard Truths/verification structures in Pass 11.
- Research modes under `Specialized_Audits/`:
  - `Research_Mode_Comp_Validation.md`
  - `Research_Mode_Factual_Verification.md`
  - `Research_Mode_Genre_Currency.md`
  - `Research_Mode_Representation_Context.md`
- Franklin redirect workflow: `Franklin_Pathway.md` (pre-spine viability gate).
- New specialized audits:
  - `Specialized_Audit_Emotional_Craft.md`
  - `Specialized_Audit_Scene_Turn.md`
  - `Specialized_Audit_Character_Architecture.md`
  - `Specialized_Audit_Dialectical_Clarity.md`
  - `Specialized_Audit_Memoir_Creative_Nonfiction.md`
  - `Specialized_Audit_Narrative_Nonfiction_Craft.md`

### Changed
- Operational quick-reference updated to `SKILL.md` version `4.4`.
- Workflow model expanded beyond Core/Full to include Franklin redirect criteria for absence-of-story material.
- Module index expanded to include evaluative pass routing and research-mode routing.

### Fixed
- Structural-only diagnostic gap addressed with explicit quality/market/readiness evaluation pass (Pass 11).
- Nonfiction/pre-spine handling gap addressed via dedicated Franklin pathway.

### Notes
- This backfill aggregates multiple file timestamps (not a single atomic commit).
- Earliest clear `v0.4.4` artifacts: research modes (`2026-02-02`) and Pass 11 module (`2026-02-05`).
- Latest core `v0.4.4` alignment in this phase: `SKILL.md`, `Module_Index.md`, and `AI_Development_Editor_Complete_v0.4.4.md` (`2026-02-12`).

## v0.4.3 - 2026-01-29 *(historical backfill)*

### Added
- Register Uncertainty diagnostic in the Literary Fiction module for multi-genre register conflict.
- Reframed interiority audit (`Male Gaze` -> `Interiority Preservation`) with symmetric POV logic.
- New `Series / Composite Novel` specialized audit for part-level and arc-level calibration.
- Subfolder project organization for genre modules, specialized audits, and templates.

### Changed
- Core framework promoted to `AI_Development_Editor_Framework_v0.4.md` version `4.3`.
- Supporting docs updated to reference folderized module paths.

### Notes
- Backfill from internal performance assessment (dated 2026-01-29).
- `v0.4.3` refinements were validated during live testing against a multi-POV literary fiction manuscript.
