# Fiction Benchmark — Run Protocol

Three roles, kept separate to preserve blindness and to keep convergence
(agreement of independent *productions*) distinct from reliability (two scorers
on one output). Mirrors the argument benchmark's RUN-PROTOCOL.

## The three roles (blindness discipline)

1. **Preparer (fixture construction / repinning only).** Reads `SOURCES.md` and,
   for a broken member, only that member's mutation registry. Derives the stored
   short fixture or referenced-cache body, records its SHA-256, and hands only
   text to the runner. Routine runs use the committed short fixtures and fetch
   only the referenced Dickens control; they do not reconstruct mutations.
2. **Blind runner.** Receives only the fiction text + a **neutral label** (never
   the descriptive slug — `pov-break-broken` encodes the diagnosis). Runs the
   **pinned canonical pass-set** {0, 1, 2, 5, 7, 8, 10} + Synthesis, byte-identical
   across ALL fixtures (so the pass selection leaks zero information about which
   defect, if any, a fixture carries). `run.sh` automates this. Produces the
   Findings Ledger + pass artifacts + Synthesis, and answers the recognition
   probe (Step 2b).
3. **Scorer.** Opens `groundtruth.md` **afterward**, scores the run against the
   key per [../../rubrics/fiction-benchmark.md](../../rubrics/fiction-benchmark.md).
   A different session/person than the runner.

## Step 1–2 — Prepare and run (blind)

Use [run.sh](run.sh). Point `SRC` at your local cache; `./run.sh --fetch` can
reconstitute the Gutenberg controls and is required for the referenced Dickens
text. The ten short fixtures are committed and used as fallbacks when absent
from `SRC`. `./run.sh --verify` checks selected inputs against recorded hashes.
`./run.sh --prompt-only` materializes
the exact blind prompts without making model calls. The pinned M2a pair is
**Terra (`gpt-5.6-terra`, high reasoning) + Opus (`claude-opus-4-8`)**: two
independent, cross-vendor runs over byte-identical benchmark prompts.

### Step 2b — the recognition probe (anti-recall)

Every run ends with a `RECOGNITION:` line: did the model recognize the
author/title? A run that names the base is **flagged recall-susceptible** and
weighted lightly. The sharper fiction variant of the threat: a model that
recognizes the base may flag the mutation as a *deviation from the remembered
original* rather than detecting an *internal* contradiction. The controls are
maximally recognizable texts by design — for a *control*, recognition mostly
biases toward the correct answer ("this is a masterpiece"), so control passes are
**corroborating** specificity evidence, recall-flagged. The matched pairs use
original synthetic or low-recognition bases precisely to keep recall from
shortcutting the plant. Increment 1's matched pairs are original synthetic
works.

## Step 3 — Score each member (human, per the rubric)

Score the in-scope FQ dimensions 0–3. **Evidence-grounding is mandatory:** an FQ2
hit requires the finding's `evidence_refs` to cite the in-text loci AND the
`mechanism` to name the developmental mechanism. A finding justified by
out-of-text knowledge ("in the original, X…") is a **miss (recall)**; bare
seam-detection ("something is off at ¶40") with no mechanism is a **miss (seam)**.
Log each 0/1 with a failure-attribution cause class (incl. recall / seam /
ground-truth ambiguity).

## Step 4 — Matched-pair delta + convergence (the success condition)

**Compute the matched-pair delta BEFORE scoring FQ2/FQ4/FQ7.** A hit requires the
defect **flagged in the broken member AND NOT flagged (for that mechanism) in the
clean member** — score the *delta*, not the bare hit. Because the seam-adjacent
prose differs from the clean base only by the one mutation, a model firing on a
seam (not a mechanism) tends to fire on both members; the delta catches it.

The unit of pass/fail is the matched **pair** (D-1):

- **A pair CONVERGES** when, across both runs — **(broken, sensitivity)**
  agreement within bands on ≥3 of 4 anchors (locus FGT2, mechanism FGT3,
  severity/presence-delta FGT4, repair FGT6), **locus mandatory**; **and (clean,
  specificity)** neither run fires the defect's mechanism and neither exceeds the
  FGT4 over-fire ceiling. A pair fails if *either* member fails its side.
- **Standalone controls CONVERGE** when: (a) neither run fires the registered
  trap as Must/Should-Fix (FQ7), (b) structure recovery within band (FGT1), and
  (c) the control's registered positive anchor within band. **Lane-2/B anchors
  ((c) and FGT1 boundaries) REPORT but do not gate until a ≥3-editor panel
  α-licenses their bands (D-2)** — before licensing a control can only *fail* on
  (a), the Lane-1/A trap, or on a Lane-1 structure miss.
- **Suite-level:** a bucket passes when its matched pair converges (both members)
  AND any standalone control in that bucket converges, with no trap fired
  anywhere (any FQ7 = 0 blocks the bucket). The slice passes when all four buckets
  pass. Lane 3 / Class C is absent from the success condition by construction.

## Two-axis reporting (accuracy vs reliability)

Report the two axes separately: **accuracy** (did a run match the key's band?)
and **reliability** (did two scorers on one output agree?). Two reviewers scoring
one output is *reliability*, never convergence. Do not collapse them; a
same-vendor config pair especially can share a blind spot that looks like
agreement but is correlated error.

## The psychometric frame governs disagreements

If a ≥3-editor panel shows poor α on a Lane-2/B anchor, the ruling is
"reclassify to C or widen the band," **never** "the engine failed" (the engine's
accuracy against an un-licensed label is not computed). If two careful reviewers
disagree on a Lane-1/A key, the fixture was mis-classed (the anchor was really
Lane-2/B) — reclassify. Either way the finding is about the *architecture*, not
the engine.
