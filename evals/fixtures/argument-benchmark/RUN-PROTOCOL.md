# Run Protocol — Argument Engine Benchmark

How to actually run the engine on a fixture and score it. Self-contained and
copy-pasteable. Use this in a **web-enabled** Claude Code session — referenced
fixtures (Swift, the CORPUS.md pieces) require fetching their source, which the
build/CI sandbox blocks.

See also: [the benchmark spec](../../../docs/argument-benchmark-spec.md)
(design + convergence), [the rubric](../../rubrics/argument-benchmark.md)
(scoring), and [CORPUS.md](CORPUS.md) (referenced real fixtures + recognition risk).

## Principles

1. **Three disjoint roles — never the same session for 1 and 3.**
   - **Preparer:** fetches/extracts the input. Reads **only** [SOURCES.md](SOURCES.md)
     (metadata: URL, anchors, hash — *no* answer key). Never opens `groundtruth.md`.
   - **Runner (blind):** sees **only** the extracted argument text + the audit
     procedure. Never sees `groundtruth.md`, `SOURCES.md`, `CORPUS.md`, the
     rubric, or the spec.
   - **Scorer:** reads `groundtruth.md` + the rubric, *after* the runs.
   The preparer and runner must be **separate sessions/contexts** so fetch
   metadata (or the act of reading a GT-bearing file) cannot enter the runner's
   context. A single session that both reads `groundtruth.md` and then diagnoses
   is **not a blind run.**
2. **Two independent runs per fixture** for convergence — use two model configs
   (e.g., Opus + Sonnet) or two editors. Two reviewers scoring *one* output is
   reliability, not convergence.
3. **Score after**, against `groundtruth.md`, using the rubric. GT1–GT3 are
   authoritative; for referenced real pieces GT4–GT8 are provisional.
4. **Record provenance.** For referenced sources, the *preparer* records the
   retrieval date + SHA-256 of the extracted text into [SOURCES.md](SOURCES.md)
   (not `groundtruth.md`, which the preparer never opens).

## Step 1 — Get the input (preparer role; metadata-free hand-off)

Done by the **preparer**, in a session separate from the runner.

- **Stored fixture** (`fixture.md` present): use its contents verbatim.
- **Referenced fixture** (text not stored): read the fixture's entry in
  [SOURCES.md](SOURCES.md) — **not** `groundtruth.md` — for the URL and
  analyzed-text START/END anchors. Fetch, keep only the text between the anchors,
  drop the EXCLUDE boilerplate, and (on first authoritative retrieval) record the
  exact anchor strings + retrieval date + SHA-256 into that SOURCES.md entry's
  `RECORDED` block.
- **Hand-off:** give the runner the extracted text under a **neutral label**
  (e.g., "Submission X") — never the slug, the URL, the author/title, or any
  SOURCES.md / `groundtruth.md` content.

## Step 2 — Blind-run prompt (paste per run, per fixture)

> You are running the APODICTIC "Dialectical Clarity" audit on a piece of
> argument-shaped nonfiction. Produce a structural diagnosis only — never
> rewrite or invent content (the Editor's Firewall).
>
> **Procedure:** read and faithfully apply
> `plugins/apodictic/skills/specialized-audits/references/craft/dialectical-clarity.md`.
> Run all 9 steps; use its code families (AT, AC, CL, SM, WR, BP, OB, DI, NE)
> and named patterns (FM-A1..FM-A20); end with Step 9 (Distinguish) and the
> audit's Output Format. You may also read `docs/argument-state-schema.md`.
>
> **Blindness constraint:** diagnose ONLY from the submission text below. Do NOT
> open any `groundtruth.md`, `CORPUS.md`, `evals/rubrics/*`,
> `docs/argument-benchmark-spec.md`, or anything else under
> `evals/fixtures/argument-benchmark/`. They contain the answer key.
>
> **Submission (neutral label "Submission X"):**
> [PASTE THE ARGUMENT TEXT HERE]
>
> **Return:** the 9 steps with concrete codes, a Step-9 warrant verdict
> (WARRANTED / UNCONVENTIONAL-BUT-WARRANTED / UNWARRANTED) with any
> premise-plausibility flags (or NONE_REGISTERED), and a priority diagnosis
> (primary structural break, FM-A pattern(s), severity ranking, first repair
> target). For GT5 run Argument Red Team; for GT6 run the Revision Coach argument mode.

Run this twice with two different model configs (the two runs are independent
productions). Keep each run's full output.

## Step 2b — Recognition probe (referenced real fixtures)

The main validity threat for famous pieces is **recognition, not leakage**: the
engine may recognize the text and recite its *canonical* critique from training
rather than diagnose it. After the diagnosis (as a separate question, so it
doesn't prime the run), ask the runner:

> Did you recognize this piece — author, title, or its standard published
> critiques? Answer yes/no; if yes, name them.

If the runner names the author/title or a canonical critique, **flag the score
as recall-susceptible** and weight it lightly. Per CORPUS.md, the
MODERATE→LOW-recognition fixtures (abundance cluster, AECF, PPI) carry the
construct validity; HIGH-recognition fixtures (Coates, Andreessen, Amodei,
Bender) corroborate at best.

## Step 3 — Score against the key

For each run, open `groundtruth.md` and score the seven dimensions on the
rubric's 0–3 bands:

| Dim | Check |
|-----|-------|
| Q1 | C0 within GT1 paraphrase band |
| Q2 | failure located in GT2's layer; primary code matches (accepted equivalents allowed); discriminator named. **Referenced real fixtures:** score on the failure *locus/layer*, not the exact code — GT2 codes there are provisional (CORPUS.md §Scope convention). |
| Q3 | GT3 objection zone named with correct OB/DI code |
| Q4 | GT4 "improve" surfaced; "distort" avoided |
| Q5 | hit ≥1 pre-registered vulnerability above the decoys (if Red Team run) |
| Q6 | correct first repair target + dependency respected (if coaching run) |
| Q7 | Warrant verdict matches GT7 |
| GT8 | premise-plausibility flags present (`NONE_REGISTERED` or `P<n>`); no premise adjudicated true/false (M1 contract check, not scored) |

**Calibration emphasis for referenced real pieces (CORPUS.md).** These are
competent arguments with one Should-Fix soft spot. The scored event is whether
the engine names that one soft spot at **Should-Fix** severity and **resists
over-firing** (a flood of Must-Fix codes on a WARRANTED argument is the failure to
catch). The `ppi-one-size-fits-none` ↔ `op-ed-warrant-leap` pair is the sharpest
test: same causal-warrant family, opposite correct severity.

## Step 4 — Convergence

- **Failure-bearing fixtures:** the two runs converge if they agree on ≥3 of 4
  anchors (claim, top failures, burden mismatch, objection zone), claim
  mandatory.
- **Pure positive controls** (no registered soft spot — `personal-essay-narrative-arg`,
  `modest-proposal-satire`): converge if both agree on claim (GT1) + warrant
  verdict (GT7) + no invented failure.
- **WARRANTED real calibration fixtures** (the CORPUS.md pieces — WARRANTED *with* a
  registered Should-Fix soft spot): the positive-control rule is **not enough**,
  because two runs could both say `WARRANTED`, miss the registered failure locus and
  objection, and still "converge" — passing a calibration fixture without testing
  the calibration. These converge only when **both runs agree on all five**:
  1. **GT1** claim,
  2. **GT2** failure *locus/layer* (the registered soft spot — not the exact code),
  3. **GT3** objection zone (authoritative for these fixtures),
  4. **severity calibration:** the soft spot is named at **Should-Fix** (not
     Must-Fix) **and** the run does not over-fire (no flood of Must-Fix codes on a
     WARRANTED argument), and
  5. **GT7 = WARRANTED.**
  All five are required (no either/or). A run that says WARRANTED but misses the
  locus or the objection zone, or fires the soft spot as Must-Fix, **fails** the
  fixture even if the two runs agree with each other —
  agreement on a wrong diagnosis is not convergence.

### Reporting the verdict: two axes, not one binary

"Converged?" collapses two orthogonal questions. Report them separately — the
binary hides *which* failure you have:

- **Accuracy (per run, vs the key):** how many of the fixture's required anchors
  does *that one run* hit? A run is *accurate* when it hits all of them.
  Accuracy is run-vs-key.
- **Reliability (run vs run):** on how many anchors do the two runs make the
  *same* call — both hit, or both miss — regardless of whether they match the
  key? Reliability is run-vs-run.

The old "converged" = **reliable AND accurate** (both runs hit every anchor, so
they necessarily agree with the key *and* each other). Decomposed, the quadrants
are diagnostic:

| | Accurate (both runs hit the key) | Inaccurate (a run misses the key) |
|---|---|---|
| **Reliable** (runs agree) | **Converged** — trustworthy. | **Shared blind spot** — both runs make the *same wrong* call (e.g. both take a registered decoy). High agreement, both wrong → **engine fault; freeze the key.** |
| **Unreliable** (runs differ) | *(impossible — two all-anchor hits agree)* | **Variance / key-ambiguity** — runs disagree. If they disagree with the key but the *interesting* agreement is on a locus the key never registered, suspect the **key**, not the engine. |

Two cautions on the axes:

- **Reliability via two same-vendor configs is a weak signal.** Models from one
  lab share training data, so they share recognition (apparent agreement that is
  really shared *recall*) and share blind spots (a *shared-blind-spot* cell that
  reads as reliability). Treat config-pair reliability as a floor; genuine
  independence needs a different vendor or a second human editor.
- **"Accurate" can be recall, not diagnosis.** A run that recognized the piece
  and recited the canonical critique can hit the anchors without diagnosing.
  Flag recall-susceptible runs (Step 2b) and read their accuracy as provisional.

## Step 5 — Record

- Save both run outputs + the scorecard under `evals/results/` (gitignored;
  `git add -f` only outputs the provenance policy permits).
- For referenced sources, the preparer writes retrieval date + SHA-256 into the
   source's `RECORDED` block in [SOURCES.md](SOURCES.md) (kept out of `groundtruth.md`).
- Log convergence/score disagreements with a cause class (engine fault /
  ground-truth ambiguity / reviewer error). Ground-truth ambiguity → sharpen the
  key; that is a valid and expected outcome.

## Worked example (already run)

`op-ed-warrant-leap` was run with Opus + Sonnet (synthetic fixture, no fetch
needed). Both converged on all four anchors and scored 3 across in-scope
dimensions; the run also caught two ground-truth refinements (consequence level;
support-map subclaim routing). That is the loop this protocol formalizes.
