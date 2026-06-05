# Handoff — Argument Engine Benchmark

*Last updated: 2026-06-02. Pick up here later.*

This is a resume point for the Nonfiction Argument Engine **benchmark suite**:
what's done, what's on which branch, and the exact next action. Read this first,
then [`RUN-PROTOCOL.md`](RUN-PROTOCOL.md) for the run mechanics.

---

## TL;DR — the one next action

The benchmark is **built, provenance-complete, and has been run and scored once**
(that first cycle surfaced and fixed a Dialectical Clarity over-firing bug, now
in **PR #22**). To re-run it you need a machine with the Claude CLI + the local
source-text cache + web access (your Mac, not the cloud sandbox):

```bash
# 1. find your apodictic clone (you are NOT in it by default)
find ~ -type d -name apodictic 2>/dev/null

# 2. cd into it, get the runner branch
cd /path/to/apodictic            # <- result of step 1
git fetch origin
git checkout claude/benchmark-runner-script

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

## Where everything lives (branches)

| Branch | State | Contents |
|--------|-------|----------|
| `main` | merged | The whole benchmark: spec, rubric, schema, synthetic fixtures, the 10-piece referenced corpus + answer keys, SOURCES.md with all 10 hashes (incl. corrected Coates). |
| `claude/benchmark-runner-script` | **open as PR #22**, rebased onto current `main` | `run.sh` (blind-runner automation), this handoff, the SOURCES `BODY_START`/`BODY_END` anchors, and the Dialectical Clarity calibration + Step-6 (`6a`/`OB5`) edits with their codex/antigravity mirrors. |
| `claude/stoic-gates-ooP11` | merged (was #7 + #8) | historical; nothing left to do here. |

PRs **#7** (spec + synthetic slice) and **#8** (referenced corpus + protocol)
are both merged. The runner branch is now **PR #22** (owner review addressed;
based on current `main`); land it after its dependencies #20 and #21.

---

## What's done

- **Engine itself:** Dialectical Clarity v2.0 + `Argument_State.md` + 8 companion
  modules. The benchmark *tests* it; the first run surfaced a severity over-firing
  bug now fixed in PR #22 (a Step-9 default-to-SOUND rule + a Hard-Gate Severity
  Floor, plus the Step-6 `6a`/`OB5` objection-discrimination round).
- **Benchmark scaffolding** (`docs/argument-benchmark-spec.md`,
  `evals/rubrics/argument-benchmark.md`, `evals/argument-groundtruth-template.md`):
  7 test questions → 0–3 scoring, three convergence classes (failure-bearing /
  pure positive control / SOUND-real-calibration), recognition-contamination
  handling.
- **Synthetic fixtures** (text in-repo): `op-ed-warrant-leap`,
  `policy-brief-uncompared` (sensitivity); `personal-essay-narrative-arg`,
  `modest-proposal-satire` (specificity / Q7 controls).
- **Referenced real corpus** (10 pieces, text NOT stored — see `CORPUS.md`),
  each with a `groundtruth.md` whose GT1–GT3 are an editor's pre-registered
  diagnosis; GT4–GT7 provisional. All 10 fetched, hashed, and anchored in
  `SOURCES.md`.
- **`run.sh`** verified statically: `bash -n` clean; the SOURCES.md hash parser
  extracts all 10 slug→hash pairs and resolves Coates to the **corrected** hash
  (`d4407650…`), not the superseded one.
- **One real run already done:** the synthetic `op-ed-warrant-leap`, Opus +
  Sonnet — both converged on all four anchors, scored 3 across in-scope
  dimensions, and surfaced two ground-truth refinements (see RUN-PROTOCOL
  "Worked example"). That proves the loop end-to-end.

## What's NOT done (the actual remaining work)

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
4. **GT4–GT7 second-editor confirmation (the one human-gated item).** GT1–GT3 are
   editor-pre-registered (temporally independent); GT4–GT7 are provisional and want
   a *second* human editor diagnosing blind for personal independence. A ready-to-hand
   **blind packet is built** at Dropbox `…/Development Editor/argument-benchmark-second-editor-packet/`
   (5 load-bearing pieces, stripped + neutral-labeled, README + registration form;
   the de-anon map + scoring steps in its `TODO.md`). Gitignored — the packet holds
   third-party text, so it lives in Dropbox, never the repo. Recruit one editor and
   hand them `packet/`.
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
