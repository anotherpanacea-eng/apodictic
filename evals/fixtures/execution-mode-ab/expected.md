# Expected — Single-Agent vs. Multi-Agent A/B pair

Pre-registered **before any run** (the argument-benchmark ground-truth discipline). Both mode
arms (`single-agent-config.md`, `multi-agent-config.md`) run the same `manuscript.md`; each
arm's consolidated findings list is scored for **real-issue recall** against the registered
ground-truth set below. Per `docs/swarm-vs-single-eval.md`, **recall (TP / registered GT) is
the computable, defensible metric**; a general false-positive rate is **not** computable from
a thin GT key, so it is not scored here. This manuscript is a **flawed** text, not a positive
control, so it also does not support the over-firing-on-controls instrument.

## Registered ground-truth findings (the recall set)

A finding is a **true positive** when a run names the issue at the stated locus with a
rationale that matches the discriminator. Severity band uses the canonical 0-3 / Must-Fix …
Could-Fix scale.

| ID | Severity | Locus | The real issue (discriminator) |
|----|----------|-------|--------------------------------|
| **GT-1** | Must-Fix | Ch2 ending / Ch1 lantern room | **Uncanny beat lands flat.** The final line treats the lens "turning all night on its own" as supernatural, but Elias himself "set the great lens turning" in Ch1 and a lighthouse lens turns all night **by design** — the eerie detail describes normal operation, so the intended chill reads as a logic error. |
| **GT-2** | Must-Fix | Ch2 ("a thing he had never told anyone about"; "watched a thing … long ago") | **Un-paid-off setup / dangling hook.** A buried backstory is raised twice as if load-bearing but is never anchored or paid off in the excerpt. Either plant/pay it off or cut it. |
| **GT-3** | Should-Fix | Ch2 final log line ("You watched. You always watched.") | **On-the-nose reveal.** The closing line states outright the theme the scene built by implication; it tells what the ambiguity already showed. |
| **GT-4** | Must-Fix | Ch2 (the memory gap) | **Unmotivated unreliable-narrator mechanism.** The pivot depends on Elias not remembering writing the 6:30 line, but the source of the gap (drink / fugue / supernatural) is never established, so the reader can't calibrate the doubt — the ambiguity reads as arbitrary rather than designed. |
| **GT-5** | Should-Fix | Ch2 ("the man from the Board") | **Flat antagonist.** The inquiry's opposition is a cardboard bureaucrat ("Men from Boards always decided first and inquired after"); the scene's tension is thin because the counter-pressure has no specificity. |
| **GT-6** | Should-Fix | Ch1 (pattern) | **Stock diction cluster.** "the sea was honest," "the old familiar calm," "threw itself against the rocks the way it always did," "he lit the warning flare and he prayed" — a pattern of cliché phrasing that flattens the voice. |

Recall for an arm = (TP among GT-1…GT-6) / 6. Report per-arm recall and the paired
difference. Severity-band calibration (does each caught finding land in its GT band) is scored
secondarily, reusing the 0-3 bands.

## Decoys (flagging these is a false read, not a true positive)

- **The 5:30-vs-6:30 discrepancy is the intended mystery, not a plot hole.** The gap between
  Ch1 (flare implied immediate) and the Ch2 log (flare at 6:30) is the deliberate engine of
  doubt. A run that reports it as a **continuity error to fix** has misread design as defect.
- **The second, un-written log entry in an unknown hand** is an intended supernatural beat,
  not a POV/continuity break to "correct."

## Pre-registered decision rule (from `docs/swarm-vs-single-eval.md §Decision rule`)

Let **R** = mean per-fixture real-issue recall, **C** = over-firing-on-controls count (not
computable on this flawed fixture — needs a positive control), **T** = tokens/run.

- **Swarm justified as "deeper"** iff `R(swarm) − R(single) ≥ 0.15` **and** `C(swarm) ≤
  C(single)` **and** the gain holds on the long-fiction arm.
- **Swarm justified only as verification insurance** iff the recall gain is `< 0.15` **or**
  `C(swarm) > C(single)`.
- **Single-agent default everywhere** iff single ties-or-wins cost-adjusted.

## Scope and honest limits (why the run itself is deferred)

This fixture supplies the **shared inputs + registered GT + decision rule** — everything a run
is scored against. It does **not** supply run outputs, and it cannot be executed on the
current in-repo harness without the dedicated build named in `docs/swarm-vs-single-eval.md
§What a sound version actually requires` (a mode-comparable run path with orchestrator +
swarm consolidation, token capture, and a scorer-readable consolidated artifact per mode). The
benchmark `run.sh` inlines text into one `claude -p` call under two *model* configs and has no
orchestrator, no swarm path, and zero token capture (review finding B2).

The N=1 pilot on a long-fiction fixture (`docs/swarm-vs-single-eval-pilot/`) is directional,
not a verdict; a powered multi-fiction corpus is still required. This excerpt is short (single
short scene), so it is a **schema/GT scaffold** for the mode-comparison, not the powered long-
fiction arm the decision rule's "long-fiction" clause needs. The model-run coverage-
confirmation report is therefore **deferred** — these files are the fixture pair only.
