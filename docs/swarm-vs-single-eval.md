# Execution-Mode Eval — swarm vs. single long-context (spec)

**Status:** Spec, **revised after an adversarial methodology review failed the first draft.** The first version claimed a clean, no-code measurement on the existing eval harness. The review showed that was false on three load-bearing points (below). This is a **re-test**: swarm-vs-single was validated in extensive earlier testing (the basis for the §2b guidance), but *not* on the current in-repo `evals/` harness — and the headline finding is that **the current harness can't re-run it without dedicated new build**.

> **An N=1 pilot has since run** this design ad-hoc on one long-fiction fixture (*Dungeon Crawler Carl* Book 1, 130K words) — see [`swarm-vs-single-eval-pilot/`](swarm-vs-single-eval-pilot/) (pre-registration, blind ground-truth key, label-blind scoring, comparison report). **Directional, not a verdict.** Outcome: on that fixture single-agent tied-or-edged swarm on real-issue recall (0.50 vs 0.44, noise-level at N=1) at ~8.5× less cost; swarm bought tighter severity calibration, not more recall. Per the pre-registered rule this lands on **"verification-insurance / single-default, cost-adjusted,"** which matches §2b's existing default. The pilot's cheap deliverable has been applied: §2b and `run-core.md` §Execution Mode keep swarm but reframe its everyday rationale to *verification isolation* (not "deeper analysis"); `run-core.md` §Execution Mode carries the `last re-validated: 2026-06` provenance note. A powered multi-fiction corpus is still needed before any firmer conclusion.

## The claim under test

`run-core.md` / §2b assert swarm yields *"~2× findings, deepest, least-biased analysis"* at *"~5× cost,"* reserved for "final submission prep." The claim is **not folklore — it rests on earlier testing** and the §2b default already hedges it (single-agent is the default for ≥1M context when the manuscript fits). What's open is whether that result still holds with **current models** and is reproducible on the **in-repo harness** — i.e., a periodic re-validation, not a first measurement.

## Why the obvious design fails (review findings, kept visible on purpose)

- **B1 — false-positive rate is uncomputable from existing ground truth.** Registered GT is a *deliberately thin* answer key (claim / failure-locus / objection; "well under a page," `argument-benchmark-spec.md §GT schema`), **not** an exhaustive issue list. So "reported-but-not-in-GT = false positive" miscounts a *real* secondary issue as noise — it penalizes the mode that finds more true issues, rigging the test against swarm. **Recall (TP / registered GT) is computable; a general false-positive rate is not.**
- **B2 — the harness can't run the variable or measure the cost.** Execution mode lives in the editor *orchestrator* (subagent fan-out + Findings Ledger + consolidation, `run-core.md §Execution Mode`). The benchmark `run.sh` inlines text into one `claude -p` call under two *model* configs — no orchestrator, no swarm path, no consolidation, and **zero token capture**. "No-code reuse" was false; running this is real engineering.
- **B3 — wrong-domain, underpowered corpus.** Swarm's claimed benefit is long-context decay on **long/complex fiction**; the corpus is **short nonfiction argument** (least likely to show the effect). The "fiction fixtures" the first draft leaned on **don't exist**, and the GT schema is argument-specific (GT1–GT7 → `Argument_State`), so fiction ground truth must be *built*, not reused.

## What a sound version actually requires (not "no code")

1. **A mode-comparable run path.** Orchestration that runs the *same* manuscript through single-agent and swarm reproducibly, captures each final consolidated output, and logs tokens. This does not exist for the eval corpus; it must be built or wired to the real editor orchestrator.
2. **Token/usage capture** for the cost axis (the "5×" is otherwise unmeasurable).
3. **Long-fiction fixtures with deeper-than-thin ground truth.** A new GT schema for developmental-edit findings (not the argument GT1–GT7), registered before scoring, on manuscripts long/complex enough that context decay could plausibly bite (the only place swarm's claimed edge can appear).
4. A **scorer-readable consolidated artifact** per mode.

## Metrics that survive review

| Metric | Computable? | Notes |
|---|---|---|
| **Real-issue recall** (TP / registered GT) | **Yes** | The sound core. Requires only that GT lists the issues a correct read must catch. |
| **Over-firing on positive controls** | **Yes (narrow)** | The *only* defensible false-positive instrument: on canonical-sound fixtures the correct Must-Fix count is ~0, so any Must-Fix is a false positive. **Scope limit (honest):** catches over-firing on *sound* texts only — says nothing about spurious findings on normal *flawed* texts. Do not generalize it to a global FP-rate. |
| **Severity calibration** (lands in correct GT band) | Yes | Reuse the 0–3 bands. |
| **Cost** (tokens/run) | Only after build #2 | Report results cost-adjusted; without token capture, omit — don't fabricate the 5×. |
| Cross-cutting catch, collapse ratio | Diagnostics only | **Not scored** (they re-import count-shaped reasoning, N1). Logged to interpret, not to grade. |

## Honest scoping of the comparison

- It tests **read-isolation + a consolidation step as a bundle** (swarm has a consolidator; single-agent doesn't). It cannot isolate "independent-lens reading" as the mechanism. Say so; don't claim more.
- **Blind scoring is only partially achievable** — swarm outputs have structural tells (consolidation seam, length). Reduce scoring to a **mechanical GT-band match** where possible (which is blindable) and accept that any "defensibility" judgment is not blind and must be pre-registered + adjudicated by ≥2 raters, not one.
- Pin the **model snapshot** (so it's a mode effect, not version drift) — but note this removes the harness's only built-in independence axis (opus-vs-sonnet), which is *why* build #1 is required.

## Pre-registered decision rule (concrete, falsifiable)

Assign the threshold a real, reachable number **before** running, and partition the outcome space with no gaps:

- Let **R** = mean per-fixture real-issue recall, **C** = over-firing-on-controls count, **T** = tokens/run.
- **Swarm justified as "deeper"** iff `R(swarm) − R(single) ≥ 0.15` (≥15 percentage-point recall gain, paired) **and** `C(swarm) ≤ C(single)` **and** the gain holds on the *long-fiction* arm specifically.
- **Swarm justified only as verification insurance** iff the recall gain is `< 0.15` **or** `C(swarm) > C(single)`: keep swarm for the spot-check's writer/verifier isolation (separately evidence-backed) and submission-prep, **drop the "deeper analysis" rationale from §2b.**
- **Single-agent default everywhere** iff single ties-or-wins on the long-fiction arm cost-adjusted.
  (These three branches are exhaustive: the first requires both conditions, the second is its negation, the third is the cost-adjusted tie/win — no result escapes.)

## The cheap deliverable (if the full re-test isn't worth it)

The §2b claim **stands on the earlier testing** — do not downgrade it. If the build cost of an in-repo re-test (orchestration + token capture + fiction GT) isn't justified now, the zero-cost improvement is provenance, not weakening: add a one-line pointer in §2b / `run-core.md` to *where* the swarm-vs-single result came from (the earlier validation), and a `last re-validated:` date, so the claim is locatable and its freshness is visible. Re-run this eval when models change enough to suspect the earlier result has drifted.

## Threats to validity (named)

- Strawman metric → recall + controls-over-firing, never raw count.
- Scorer bias / non-blindable tells → mechanical band-match + ≥2 raters for any judgment call.
- Underpower → this is a **pilot**, not a verdict, until the fiction corpus is powered; report per-fixture pairs, label conclusions directional.
- Fixture fetch / sandbox → referenced fixtures need outbound fetch; CI blocks it, so runs need a web-enabled session.
- Consolidation confound → scored as part of the bundle, logged, not isolated.

---

*Design spec, post-review. The first draft's "no-code reuse" framing was wrong; this version names the real build and narrows the claim. If the build isn't justified, ship "The cheap deliverable" into §2b instead.*
