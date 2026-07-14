# Handoff — Argument Engine Benchmark

*Last updated: 2026-07-14. Pick up here later.*

This is a resume point for the Nonfiction Argument Engine **benchmark suite**:
what's done, what's on which branch, and the exact next action. Read this first,
then [`RUN-PROTOCOL.md`](RUN-PROTOCOL.md) for the run mechanics.

---

## TL;DR — the one next action

The benchmark is built and its shared panel packet is current. The next action
is human: recruit at least three qualified independent editors, give each an
identical sealed copy of Dropbox
`argument-benchmark-second-editor-packet/current/packet/`, and keep
`current/operator-only/` private. After returns, compile ratings and run the
frozen alpha/key-compatibility adjudicator before changing any Reliability
ledger. The argument engine's model-run path remains available for a separate
rerun on a machine with the source cache:

```bash
# 1. find your apodictic clone (you are NOT in it by default)
find ~ -type d -name apodictic 2>/dev/null

# 2. cd into the current clone
cd /path/to/apodictic            # <- result of step 1
git fetch origin

# 3. point at the local source cache and DRY-CHECK first (no model calls)
cd evals/fixtures/argument-benchmark
export SRC="/Users/anotherpanacea/Library/CloudStorage/Dropbox/Cowork/Development Editor/argument-benchmark-sources"
./run.sh --verify
```

`--verify` reports, per fixture, whether the cached text matches the recorded
SHA-256 (`whole` / `body` / neither). Once it looks right, run a subset:

```bash
./run.sh roosevelt-democratic-abundance current-affairs-abandon-abundance \
         reason-problem-with-abundance-agenda cato-industrial-policy-bad-idea \
         ppi-one-size-fits-none
```

Then hand the outputs in `evals/results/run-<timestamp>/` to a scorer (a fresh
session *with* repo access, or paste them back to Claude) — scoring is a
**separate** step and never happens in the blind-run session.

---

## Where everything lives

The benchmark, runner, decoy-resistance work, and matched-pair convergence work
are on `main`; PR #37 is the latest merged calibration baseline. PRs #7, #8, and
#22 are historical and require no action. The access-controlled human packet
lives only in Dropbox; its copyright-safe builder/compiler/adjudicator contract
lives under `evals/panels/shared-blind-editor/` in this repo.

---

## What's done

- **Engine itself:** Dialectical Clarity v2.0 + `Argument_State.md` + 8 companion
  modules. The benchmark *tests* it; the first run surfaced a severity over-firing
  bug now fixed in PR #22 (a Step-9 default-to-WARRANTED rule + a Hard-Gate Severity
  Floor, plus the Step-6 `6a`/`OB5` objection-discrimination round).
- **Benchmark scaffolding** (`docs/argument-benchmark-spec.md`,
  `evals/rubrics/argument-benchmark.md`, `evals/argument-groundtruth-template.md`):
  7 test questions → 0–3 scoring, three convergence classes (failure-bearing /
  pure positive control / WARRANTED-real-calibration), recognition-contamination
  handling.
- **Synthetic fixtures** (text in-repo): the two planted-defect fixtures are now **matched
  clean/broken pairs** — `op-ed-warrant-leap/{broken,clean}` and
  `policy-brief-uncompared/{broken,clean}` (broken = sensitivity; the derived `clean` twin =
  within-work specificity, **author-deterministic** by the enumerated minimal repair, so it adds
  **no new second-editor ask**); plus `personal-essay-narrative-arg`, `modest-proposal-satire`
  (cross-work specificity / Q7 controls).
- **Referenced real corpus** (10 pieces, text NOT stored — see `CORPUS.md`),
  each with a `groundtruth.md` whose GT1–GT3 are an editor's pre-registered
  diagnosis; GT4–GT8 provisional (GT8 premise-plausibility flags are
  `NONE_REGISTERED` across the whole corpus — a flag-only M1 contract check, a
  scored M2 candidate). All 10 fetched, hashed, and anchored in `SOURCES.md`.
- **`run.sh`** verified statically: `bash -n` clean; the SOURCES.md hash parser
  extracts all 10 slug→hash pairs and resolves Coates to the **corrected** hash
  (`d4407650…`), not the superseded one.
- **One real run already done:** the synthetic `op-ed-warrant-leap`, Opus +
  Sonnet — both converged on all four anchors, scored 3 across in-scope
  dimensions, and surfaced two ground-truth refinements (see RUN-PROTOCOL
  "Worked example"). That proves the loop end-to-end.

## Next round (current — after PR #37 merge)

The full convergence runs + the decoy-resistance engine fix landed in **PR #37** (merged to
`main`). The current next-round list (with rationale) is tracked in `ROADMAP.md` → §Benchmark
Suite → **Next round**:

- **Substantive (engine/key — next calibration round):** (1) strengthen **Test A** (genre-genericity decoy filter) — `ppi` partial cross-vendor, GPT's objection stayed on the public-safety decoy; (2) **`policy-brief-uncompared` under-fire** — AT3 + no comparative defense should drive Must-Fix → UNWARRANTED (Step-9 default overrides the floor). #1 + #2 pair.
- **Human-gated (needs people; packet ready 2026-07-14):** packet regeneration
  is complete at Dropbox `argument-benchmark-second-editor-packet/current/`.
  The sendable form uses the warrant vocabulary + GT8, closed codable fields,
  exact ordinal transforms, a panel Reliability ledger, and the same ≥3-editor
  roster as fiction M2b. The older one-editor packet is preserved only under
  `archive/`. Remaining M2 promotion sequence: **recruit the shared ≥3-editor
  panel → compute Krippendorff's α per provisional dimension
  (`agreement-alpha`; α ≥ .800 CI lower bound → `panel-licensed`, < .667 →
  `low-agreement`) → reconcile clearing panel values to the frozen key
  projection → independently review → edit each promoted/demoted fixture's
  Reliability ledger (cleaning stale `(PROVISIONAL)` heading markers in the same
  commit) and record the round in
  `docs/argument-benchmark-calibration-round.md`.** The five argument units can
  promote only their own GT4–GT8 anchors; `current-affairs` GT2 is the separately
  registered recall-suspect check. Unpanelled fixtures remain provisional.
- **Minor / optional:** (5) PDF `--fetch` (AECF) → add a `pdftotext` branch if PDFs multiply; (6) a second cross-vendor GPT pass on `roosevelt` (kills the n=1 "variance" objection); (7) housekeeping — the merged `claude/benchmark-corpus-round2` branch can be deleted.

The list below predates the PR #37 merge and is kept for historical context.

## Historical pre-PR-37 backlog (superseded; retained for context)

The first full cycle is **done**: the blind runs executed (abundance cluster +
ppi), were scored, and both the convergence findings and the Dialectical Clarity
calibration fix landed in **PR #22**. See `evals/results/*/SCORECARD.md` plus the
`regression-*` and `experiment-*` records. What remains:

1. **Land PR #22** after its dependencies (#20, #21).
2. **GT3 as a set (next engine round).** The Step-6 `6a`/`OB5` edit shifted runs
   off canonical decoys onto text-internal objections, but "the strongest
   objection" proved plural. Register each fixture's GT3 as a *set* of acceptable
   strong objections, and fold in the two the experiment surfaced (the ppi
   discretion-contradiction and the current-affairs motte-bailey symmetry).
3. **Recognition re-test.** With the masthead + trailing-bio leaks closed,
   re-confirm the recognition picture (ppi already flipped to "not recognized");
   the lower-recognition fixtures now carry the construct validity.
4. **GT4–GT8 panel confirmation (the one human-gated item).** GT1–GT3 are
   editor-pre-registered (temporally independent); the covered GT4–GT8 anchors
   remain provisional until a ≥3-editor panel clears the pre-registered α and
   key-compatibility gates. The current shared packet is at Dropbox
   `…/Development Editor/argument-benchmark-second-editor-packet/current/` (5
   load-bearing argument pieces + 7 independent fiction units, neutral-labeled,
   with sealed response and operator-only scoring surfaces). The packet holds
   third-party text, so it lives in access-controlled Dropbox, never the repo.
   Recruit at least three qualified editors and hand each an identical copy of
   `current/packet/` only.
   *(The `validate.sh argument-groundtruth-check` validator is DONE — shipped in main
   v2.1/2.2 as `scripts/argument_groundtruth.py`, extended to FM-A20 here.)*

---

## Gotchas / things that bit us

- **You must be *inside* the clone.** `~` is not a git repo; the first failed
  attempt was just running from `$HOME`. `find ~ -type d -name apodictic` finds it.
- **The cloud sandbox can't run this.** No Claude CLI, no web fetch (Gutenberg /
  a16z / Atlantic / Reason all 403 there), and the source cache is local-only.
  Runs and re-fetches happen on your Mac. The cloud session is fine for
  *scoring* (it has repo + key access) and for editing fixtures/docs.
- **Source texts are never committed** (copyright). They live in `$SRC` outside
  the git tree; `evals/results/` is gitignored. Re-fetch must reproduce the
  recorded SHA-256.
- **`--verify` saying "neither"** for a fixture is not a blocker — blindness is
  structural, not hash-dependent. It only means the strip heuristic didn't match
  how the text was hashed; tell Claude what it reports and the strip logic
  (`STRIP_CMD`) gets aligned.
- **`run.sh` tunables** (header comment has detail): `SRC` (required),
  `CLAUDE_TOOL_FLAGS` (empty default; set to your CLI's tool-disable flag if you
  want belt-and-suspenders — `claude --help` to confirm `--allowedTools` vs
  `--allowed-tools`), `STRIP_CMD`, `MODELS`, `REQUIRE_HASH`.
- **Coates** was re-extracted to fix ordering artifacts; the corrected file is
  `coates-case-for-reparations-corrected.md` and `run.sh` prefers the
  `-corrected` copy automatically.
- **Recognition contamination:** for the famous four (Coates, Andreessen,
  Amodei, Bender) a model may recite the *canonical* critique from memory rather
  than diagnose. `run.sh` appends a `RECOGNITION:` self-report line; weight those
  hits lightly. The abundance cluster + AECF + PPI carry the real validity.

---

## Key files (all under `evals/fixtures/argument-benchmark/` unless noted)

- `CORPUS.md` — the 10 referenced pieces, clusters, editor diagnoses, recognition tags.
- `SOURCES.md` — metadata-only manifest: URL + extraction anchors + recorded SHA-256. **Preparer reads this, never `groundtruth.md`.**
- `RUN-PROTOCOL.md` — the 3-role (preparer / blind runner / scorer) procedure + convergence rules.
- `run.sh` — automates preparer + blind-runner.
- `<slug>/groundtruth.md` — per-fixture answer keys (scorer-only).
- `../../rubrics/argument-benchmark.md` — scoring rubric.
- `../../../docs/argument-benchmark-spec.md` — design, convergence, deferred validator.

---

## How to resume with Claude

Paste this:

> Resuming the argument-engine benchmark. Read
> `evals/fixtures/argument-benchmark/HANDOFF.md`. I've run `run.sh` on
> [which fixtures] — here are the outputs [paste or attach]. Score them against
> the keys and report convergence.

or, if you haven't run yet and want help getting `./run.sh --verify` green:

> Read `evals/fixtures/argument-benchmark/HANDOFF.md`. `./run.sh --verify`
> reported [paste output] — help me get the cache/paths right.
