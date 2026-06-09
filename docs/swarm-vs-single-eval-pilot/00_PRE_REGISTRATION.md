# Pre-Registration — Swarm vs. Single-Agent, N=1 pilot (DCC Book 1)

**Locked before the single-agent review is run or scored.** Conforms (as far as an N=1 ad-hoc run can) to `docs/swarm-vs-single-eval.md`. This is a **directional pilot on one long-fiction fixture**, not the powered re-test the spec specifies. It inherits every threat the spec names; see §Threats.

## Fixture
*Dungeon Crawler Carl* Book 1 (130,173 words). One long, complex fiction manuscript — the *right domain* for swarm's claimed long-context-decay benefit (the spec's B3 notes the in-repo corpus is the wrong domain; this fixture is the right one, but N=1).

## The two arms
- **Swarm** — already run: `runs/2026-06-08_opus48_full-de/` (11 passes + 6 audits as architecturally isolated subagents + consolidation + synthesis). Claude Opus 4.8.
- **Single-agent (large-context)** — to be run: one subagent reads the manuscript once and runs the same pass+audit set sequentially in a single context, then synthesizes. Same model, same contract. `runs/2026-06-08_opus48_single-de/`.

Both arms share the same intake contract (intake is mode-independent in the framework). This is a **bundle comparison**: swarm = read-isolation + consolidation; single = neither. It cannot isolate "independent-lens reading" as the mechanism (spec §Honest scoping). Stated, not hidden.

## Ground truth (registered, blind to both letters)
A third isolated agent reads the manuscript + contract and registers an answer key BEFORE scoring, having seen **neither** editorial letter. Schema per issue:
- `id`, `locus` (line/chapter), `one-line issue`, `band` (0–3), `kind` (issue | strength | control-fact).
- **Bands:** 3 = Must-Fix (book-breaking) · 2 = Should-Fix (real, pattern-level) · 1 = Could-Fix (local polish) · 0 = not-an-issue / strength.
- A **Must-Fix-count judgment**: how many genuine band-3 issues exist (the spec's "is this text near-sound?" control fact). If ~0, DCC functions as a *weak* positive control for Must-Fix over-firing.

**Bias note (load-bearing):** the GT is produced by the same model family that wrote both reviews, and is informed by the shared contract. It is *blind to both editorial letters* but not model-independent. Recall against it is therefore "does this mode recover the issues an independent blind read of the same text registers," not an absolute truth. Honest limit.

## Metrics (only those that survive the spec's review)
1. **Real-issue recall** = (registered GT issues the review caught) / (registered GT issues). Computed per arm. **The sound core.**
2. **Over-firing on the (weak) control** = count of Must-Fix the review raises that GT does **not** register as band-3. Scope limit: only meaningful because DCC is near-sound; says nothing about FP on flawed texts. **Never reported as a global FP rate.**
3. **Severity-band match** = for GT issues both arms caught, did the review place them in GT's band (±0) / off by one / off by ≥2.
4. **Cost** = captured subagent token usage per arm (the Agent tool reports `subagent_tokens`; this is real capture, unlike the in-repo harness). Swarm cost excludes parent-orchestration overhead (under-counts swarm); single cost is the single subagent's usage. Report the ratio with that asymmetry stated.

**Not scored (diagnostics only, logged to interpret):** raw finding count, cross-cutting catches, consolidation/collapse ratio. These re-import count-shaped reasoning the spec rejects.

## Scoring procedure
A fourth isolated agent (the **scorer**) receives the GT and the two letters **labeled neutrally ("Review A" / "Review B")** and produces the recall / over-fire / band tables by mechanical matching. Structural tells (consolidation seam, length) mean blinding is only partial (spec); the scorer is told to match issues to GT mechanically and not to guess mode. Final adjudication by the orchestrator (me) is **non-blind and single-rater** — declared, not hidden. Where the spec wants ≥2 raters for judgment calls, the scorer + orchestrator are the two; agreement/disagreement is logged.

## Pre-registered decision rule (verbatim from the spec, thresholds locked)
Let **R** = mean per-fixture real-issue recall, **C** = over-firing-on-controls count, **T** = tokens/run.
- **Swarm justified as "deeper"** iff `R(swarm) − R(single) ≥ 0.15` **and** `C(swarm) ≤ C(single)` **and** the gain holds on the long-fiction arm. *(Here the long-fiction arm IS the only arm — so the third clause collapses to the first on this fixture; with N=1 this can only be suggestive.)*
- **Swarm justified only as verification insurance** iff recall gain `< 0.15` **or** `C(swarm) > C(single)`: keep swarm for the spot-check writer/verifier isolation + submission-prep; **drop the "deeper analysis" rationale from §2b.**
- **Single-agent default everywhere** iff single ties-or-wins cost-adjusted on the long-fiction arm.
Branches are exhaustive (spec). Outcome reported as **directional** given N=1.

## Threats to validity (named, per spec)
- **N=1, single fixture** → pilot, not verdict. Conclusions labeled directional; no powering.
- **GT not model-independent** → recall is "recovery of a blind same-model read," not ground truth.
- **Bundle confound** → swarm's consolidation step is scored as part of the bundle, not isolated.
- **Partial blinding** → letters have structural tells; only mechanical band-match is blindable; orchestrator adjudication is non-blind.
- **Cost asymmetry** → swarm token total under-counts (excludes parent orchestration); single is one subagent. Ratio is a floor on the gap, not exact.
- **Same-model GT + reviews** → shared blind spots inflate both recalls equally; the *difference* R(swarm)−R(single) is more trustworthy than either absolute.
- **Positive-control weakness** → DCC is strong, not canonical-sound; over-firing instrument is weak here.

## Measured swarm cost (recorded now, before single runs)
Sum of reported `subagent_tokens` across the 14 swarm subagents (13 analysis + 1 spot-check) = **≈ 3.14M tokens** (excludes parent-orchestration: ref-reading, ledger consolidation, synthesis authoring). Treat as a **floor** on swarm cost.
