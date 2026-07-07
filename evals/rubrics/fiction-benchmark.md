# Rubric: Fiction Structural Fault-Injection Benchmark

Use this rubric when scoring a Core Development Editor run against a
pre-registered fiction ground-truth answer key (`groundtruth.md`). It
specializes the core rubrics for the fiction structural-defect slice. Full
design rationale, corpus design, the multi-lane validity architecture, and the
convergence protocol are in
[../../docs/fiction-benchmark-spec.md](../../docs/fiction-benchmark-spec.md).

**This rubric scores the engine; the mechanical validator does not.** Every
check below is a human scorer judgment applied to the run output. The
`fiction-groundtruth-check` validator touches the answer **key** only — it never
sees a run, never scores the engine, and has zero view of whether a finding
landed. FQ2/FQ3/FQ6 run-fidelity, FQ7's "no severity token attached," the
anti-recall / anti-seam evidence reads, and the matched-pair delta are declared
human work with **no mechanical backstop** (the finding `mechanism` field is
free text; the schema enumerates no mechanisms).

## Inputs Required

- Fixture text (in-repo, or the referenced source for text-not-stored fixtures)
- Pre-registered `groundtruth.md` for the fixture (FGT1–FGT7)
- The run's Findings Ledger + Pass 0 outline + Pass 2 beat map + Pass 5/7/10
  artifacts + companion `CF-NN`/`SP-NN` rows where the plant surfaces there
- The Synthesis / editorial letter from the run
- The recognition-probe answer (RUN-PROTOCOL Step 2b), recorded with the score
- **For matched pairs: BOTH members' runs** (the delta is scored, not the bare hit)

Without the pre-registered ground truth, no fiction dimension can be scored.
Ground truth registered *after* seeing the run output is void.

## Metrics

Score each in-scope dimension on the 0–3 scale defined in
[../../docs/eval-harness-spec.md](../../docs/eval-harness-spec.md#core-metrics).

- **FQ1 — Structure recovery** (Pass 0 outline + Pass 2 beat map vs FGT1): 0 structure invented or unrecognizable vs the page · 1 inventory off by >1 or boundaries wild · 2 inventory within band, boundaries loose · 3 inventory within band **and** boundaries within band. *(FGT1 boundaries are Lane-2/B — they REPORT until α-licensed; short-fixture FGT1 is scoped to scene inventory, boundary bands ride the novella-length referenced control.)*
- **FQ2 — Defect locus** (Findings Ledger `evidence_refs`/`evidence_quote` **or** a companion CF/SP row vs FGT2): 0 plant missed entirely, or "found" via out-of-text recall · 1 gestured at the area, no locus · 2 right locus, thin evidence · 3 plant found at the registered locus, in-text evidence cited. An FQ2 hit **requires** the evidence to cite the in-text loci; out-of-text justification ("in the original, X…") is a **miss (recall)**; bare seam-detection with no mechanism is a **miss (seam)**.
- **FQ3 — Mechanism discrimination** (the finding's free-text `mechanism` string + origin family vs FGT3): 0 wrong family (a POV break called a voice-drift style issue; a contradiction called a reveal problem) · 1 right family, no discriminator · 2 right family + discriminator implied · 3 mechanism family matches and the discriminator is named. Human judgment over free text — no mechanical backstop.
- **FQ4 — Severity band** (finding `severity` vs FGT4 band, or the presence-delta): 0 plant at Could-Fix/absent, or a Must-Fix flood on sound surround · 1 wrong band · 2 in band, over-fire near the ceiling · 3 severity in band and no over-fire beyond the clean-member ceiling. **Severity-free CF/SP plants** score the DELTA (row present in `broken`, absent in `clean`), not a band.
- **FQ5 — Arc recovery** (character card / arc statement vs FGT5 band): 0 arc invented or denied against the band · 3 gross arc within band. *(Lane-2/B — REPORTS until α-licensed; only the arc-pilot control scores FQ5.)*
- **FQ6 — Repair target** (`fix_class` + letter repair framing vs FGT6): 0 repair targets a symptom or violates the dependency · 3 first repair targets the mechanism and respects the dependency rule.
- **FQ7 — Form fairness** (finding behavior on the clean member + the registered trap vs FGT7): 0 the trap fired as Must-Fix on a control (or the clean member) · 3 the trap is unfired and the device is read as intentional/effective (advisory at most). **See §FQ7 Is the Specificity Gate.**

## Binary Checks (human SCORER checks per this rubric — not wired gates)

Every check is applied by the human scorer to the run output. None is a
mechanical gate; the anti-recall / anti-seam / firewall reads have **zero**
mechanical enforcement — they are defensible precisely because scoring is a
declared human activity.

- **No invented content (Firewall):** the run added no scene, character, fact, or
  quote the text does not contain; `evidence_quote`, when present, is a verbatim
  substring (the scorer verifies by string search — the scoring-time analog of
  the annotated-manuscript A6 gate, not that wired gate).
- **Findings are structured:** material findings carry `apodictic.finding.v1`
  blocks with valid `F-<ORIGIN>-<NN>` ids; continuity/reveal plants may instead
  (or also) surface as `CF-NN`/`SP-NN` companion-artifact rows.
- **Ledger emitted and consolidated;** Synthesis ran after all passes.
- **Complete-manuscript mode confirmed** (no `artifact=partial` in the run header).
- **Recognition probe answered** (Step 2b) and recorded with the score; the
  **matched-pair delta** (broken-vs-clean) computed before scoring FQ2/FQ4/FQ7.
- Model tag + run-folder naming follow policy.

## FQ7 Is the Specificity Gate

FQ7 is scored *primarily on positive controls* — the standalone
intentional-device controls **and** the clean member of every matched pair. A
registered false-positive trap fired as a **Must-Fix** on a positive control (or
on the clean member) is **FQ7 = 0 for that fixture regardless of FQ1–FQ6**, and
blocks the bucket. Matched pairs make this airtight: the clean member is the same
prose minus one mutation, so a Must-Fix on it cannot be excused as "the base was
just bad prose." Sensitivity without specificity is not a passing engine — a
fiction editor who "finds" defects in *The Yellow Wallpaper*'s narration is worse
than one who finds nothing.

Because the fiction engine emits **findings, not a classification token**, FGT7
scoring is operationalized over finding behavior: DEFECT-AS-PLANTED = the plant
is found (FQ2); SOUND = no Must-Fix fired against registered-sound material;
INTENTIONAL-AND-EFFECTIVE = the registered device is unflagged or explicitly
framed as intentional/effective (advisory register, no Must/Should-Fix token
attached). All three are human scorer judgments — no mechanical backstop.

## Convergence — the Matched Pair Is the Unit

Score per-run, then assess convergence across two independent **engine** runs.
The unit of pass/fail is the matched **pair**, not the lone fixture (D-1).

- **A matched pair CONVERGES** when, across both runs: **(broken member —
  sensitivity, Lane-1/A)** agreement within bands on ≥3 of 4 anchors — locus
  (FGT2), mechanism (FGT3), severity/presence-delta (FGT4), repair target (FGT6)
  — **locus mandatory**; **and (clean member — specificity, Lane-1/A)** neither
  run fires the defect's mechanism and neither exceeds the FGT4 over-fire ceiling.
  A pair fails if *either* member fails its side.
- **Standalone intentional-device controls** converge when: (a) neither run fires
  the registered trap as Must/Should-Fix (FQ7), (b) structure recovery within
  band (FGT1), and (c) the control's registered positive anchor within band.
  **Lane-2/B anchors ((c) and FGT1 boundaries) REPORT but do not gate until a
  ≥3-editor panel α-LICENSES their bands (D-2).**
- **Suite-level:** a bucket passes when its matched pair converges (both members)
  **and** any standalone control in that bucket converges, with no trap fired
  anywhere. The slice passes when all four buckets pass. Lane 3 / Class C is
  absent from the success condition by construction; Lane 2 / Class B anchors
  report-only until α-licensed.

Two reviewers scoring one output is *reliability*, not convergence. Same-vendor
config pairs carry a shared-blind-spot caveat; report the two axes (accuracy and
reliability) separately. Full rule + role separation:
[RUN-PROTOCOL.md §Step 4](../fixtures/fiction-benchmark/RUN-PROTOCOL.md).

## Decision Rules And Failure Attribution

Use [eval-harness-spec.md §Decision Rules](../../docs/eval-harness-spec.md#decision-rules)
for accept / accept-with-override / revise-and-retest / reject. Every dimension
scored 0 or 1 is logged with a failure-attribution cause class, with the
fiction-specific additions: **recall contamination**, **seam detection**, and
**ground-truth ambiguity**. Per the psychometric frame: if a ≥3-editor panel
shows poor α on a Lane-2/B anchor, the ruling is "reclassify to C or widen the
band," **never** "the engine failed" (the engine's accuracy against an
un-licensed label is not computed). If two careful reviewers disagree on a
Lane-1/A key, the fixture was mis-classed (the anchor was really Lane-2/B) —
reclassify.

## Fixture-Specific Overrides

A fixture's `groundtruth.md` is authoritative for that fixture. Controls and
`clean` members may legitimately exclude FQ2/FQ3/FQ6 (there is no planted defect
to locate) and score FQ1 + FQ5 + FQ7 only. The ground-truth file states which
dimensions are in scope.
