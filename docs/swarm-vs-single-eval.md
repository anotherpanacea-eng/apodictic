# Execution-Mode Eval — swarm vs. single long-context (spec)

**Status:** Spec (not yet built). Converts a load-bearing *assertion* in the framework into a *measurement*. Builds on the existing eval harness (`docs/eval-harness-spec.md` shared metrics, `docs/argument-benchmark-spec.md`, `evals/fixtures/`, `evals/rubrics/`). No new validator — this is an eval protocol, not a mechanical check. Output: `evals/rubrics/execution-mode.md` + a results template + a small paired fixture set.

## The claim under test

`run-core.md` / `intake-router-runtime.md` §2b assert that **swarm** (every analytical lens reads the whole manuscript independently) yields *"~2× findings, deepest, least-biased analysis"* at *"~5× token cost,"* and reserve it for "final submission prep." None of this is measured anywhere in the repo. This eval asks: **does swarm produce a materially better diagnosis than a single long-context run, and is it worth the cost?**

The framework's own default already hedges the answer — §2b makes **single-agent the default** for ≥1M context when the manuscript fits — so the burden of proof is on swarm.

## Why "2× findings" is the wrong metric

Finding *count* is a bad proxy: N independent readers surface more candidates, but "more" includes false positives and near-duplicates that the consolidation step then re-merges. The eval must separate **real-issue recall** from **false-positive rate**, scored against registered ground truth — not count raw findings.

## Design

**Independent variable:** execution mode — `single-agent` (one long context, all passes) vs `swarm` (independent per-lens reads + consolidation). Hold everything else constant: same fixtures, same model snapshot, same resolved pass set, same registered ground truth.

**Reuse the harness's anti-overfit machinery (already in place):**
- **Ground truth registered before any scored run** (`argument-benchmark-spec.md §Ground-truth answer-key schema`) — no post-hoc moving the target.
- **Positive controls mandatory** (`§Anti-overfit guard`) — fixtures whose correct diagnosis is "do NOT over-fire." These are the **false-positive detector**: a mode that flags Must-Fix on a canonical sound argument (e.g. `federalist-10`) is penalized. This is where swarm's extra findings get tested for being noise.
- **Scope-anchored, SHA-pinned fixtures** — reproducible inputs, no leakage.
- **Shared 0–3 metric scale + GT severity bands** — reuse, don't reinvent.

**Metrics (per fixture, then aggregated, paired by fixture):**

| Metric | What it measures | Why |
|---|---|---|
| **Real-issue recall** | TP / (registered GT issues) | Does the mode find what's actually wrong? |
| **False-positive rate** | reported-but-not-GT-and-not-defensible / reported | The crux: are swarm's extra findings real? Driven by positive controls. |
| **Severity calibration** | fraction landing in the correct GT band (0–3) | Right problem, right severity. |
| **Cross-cutting catch** | recovery of linked / multi-pass GT issues | Tests the *single*-context hypothesis: does held state catch connections swarm's isolation loses (or vice-versa)? |
| **Cost** | tokens/run | The "5×" claim, so results are cost-adjusted (validated-recall-per-token), not raw count. |

**Controls against bias:**
- **Paired runs** — same fixtures through both modes; report per-fixture deltas, not just aggregates.
- **Blind scoring** — the scorer scores outputs against ground truth **without knowing which mode produced each** (strip mode labels; randomize order). Mode-bias is the most likely confound.
- **Convergence-protocol caveat (important).** The harness's success condition is "two independent *productions* agree" (`§Convergence protocol`). Swarm is *internally* multiple independent productions, so its internal agreement is **not** comparable to single-agent's. Score each mode's **final consolidated output against ground truth** — never its internal agreement — or the comparison is confounded in swarm's favor.
- **Model snapshot pinned** — both modes on the identical model build (mode effects, not version drift).

**Corpus:** reuse the registered `argument-benchmark` fixtures (incl. positive controls) for the nonfiction arm; add a small fiction arm (3–5 fixtures spanning a short, a mid-length, and a long/structurally-complex manuscript), since the long-context degradation swarm is meant to fix should show up most on long, multi-POV/non-linear drafts. Ground truth registered per the existing schema before any run.

## Pre-registered decision rule (the honest part)

Declare *before* running what result changes the default — so the eval can't be rationalized after the fact:

- **Swarm justified as "deeper"** only if it adds **≥ X real-issue recall** at a false-positive rate **≤** single-agent's, on a paired basis, at the §2b cost framing. (Pre-register X as the smallest difference that would matter editorially — e.g. ≥1 additional Must-Fix-class GT issue per fixture on average.)
- **If swarm's recall edge is small and its false-positive rate is ≥ single's:** downgrade §2b's guidance from *"swarm = deeper analysis"* to *"swarm = verification isolation only"* — keep it for the evidence spot-check (where independent verification is separately evidence-backed) and submission-prep insurance, drop the "deeper read" rationale.
- **If single-context wins or ties cost-adjusted on long fixtures:** make single-agent the default everywhere and document swarm as opt-in insurance, not a recommendation.

## What this is NOT

- Not a claim about all multi-agent setups — only swarm (independent whole-manuscript reads + consolidation) vs single long-context, for *this* holistic-diagnosis task.
- Not a verification eval — the spot-check's writer/verifier isolation is a *separate*, already-better-grounded use of independent agents and is out of scope here.

## Threats to validity (named)

- **Scorer bias** → blind, randomized scoring.
- **Fixture leakage / drift** → registered, scope-anchored, SHA-pinned fixtures (harness already enforces).
- **Strawman metric** → validated recall + false-positive rate, never raw finding count.
- **Underpowered** → pre-register the corpus size and the effect size that matters; report per-fixture pairs so small-n results are inspectable, not just averaged.
- **Consolidation as confound** → swarm's consolidation step is part of the mode under test; score its output, and log how many raw candidates collapsed (a high collapse ratio is itself evidence the "2× findings" are duplicates).

---

*Design spec. If adopted: `evals/rubrics/execution-mode.md`, a results template under `evals/results/`, and the paired fixture registrations. Reuses the shared eval-harness metrics; no code/validator change.*
