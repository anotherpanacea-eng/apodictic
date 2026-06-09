# Swarm vs. Single-Agent — Comparison Report (N=1 pilot)

**Fixture:** *Dungeon Crawler Carl* Book 1 (130,173 words). **Model:** Claude Opus 4.8 (both arms, same snapshot).
**Design:** per `docs/swarm-vs-single-eval.md`, pre-registered in `00_PRE_REGISTRATION.md`. **Mode mapping (revealed post-scoring):** Review A = **swarm**, Review B = **single-agent**.
**Status: directional pilot on one fixture — NOT a verdict.** Every threat the spec names applies; see §Caveats.

---

## 1. Measured results

| Dimension (pre-registered metric) | Swarm (A) | Single (B) | Edge |
|---|---|---|---|
| **Real-issue recall** (TP / 8 registered GT issues) | **0.44** (3.5/8) | **0.50** (4.0/8) | Single, narrow (Δ = 0.06) |
| — clean full catches (YES) | 2 | 1 | Swarm |
| — partial catches | 3 | 6 | Single (breadth) |
| **Must-Fix over-firing** (on the near-sound control; GT = 0 Must-Fix) | **0** | **0** | Tie |
| **Severity-band calibration** (clean band on the caught-and-banded set; each review's lone valence-flip row excluded from both denominators) | 3/4 clean | 3/6 (3 off-by-one) | Swarm |
| **Contested-valence flips** (named a GT issue as a strength) | 2 | 3 | Swarm (fewer) |
| **Stat-math control** (GT = clean) | Should-Fix, hedged "verify" (borderline) | Could-Fix, "reads correct" | Single (cleaner) |
| **Strength recall** (of 4 GT strengths) | 4/4 | 4/4 | Tie |
| **Plausible extra findings** (GT-omitted but real) | ~5–6 (incl. 2 high-value) | ~6 (more local) | Tie |
| **Cost** (captured subagent tokens) | **≈3.14M** (14 subagents; floor — excludes parent orchestration) | **≈0.37M** (1 subagent) | **Single, ~8.5×** |

Recall scored label-blind by an independent scorer against an answer key built blind to both reviews. Numbers are from `02_SCORING.md`; key from `01_GROUND_TRUTH.md`.

## 2. Apply the pre-registered decision rule

Let **R** = real-issue recall, **C** = Must-Fix over-fire count, **T** = tokens.
- R(swarm) − R(single) = 0.44 − 0.50 = **−0.06** → **not ≥ 0.15**.
- C(swarm) = C(single) = 0 → C(swarm) ≤ C(single) holds, but the recall gate already fails.

→ **Branch 1 ("swarm justified as *deeper*") = FALSE** (requires a ≥0.15 recall gain that did not occur — single in fact edged swarm).
→ **Branch 2 ("swarm justified only as verification insurance") = TRUE** (recall gain < 0.15): keep swarm for the spot-check's writer/verifier isolation and final submission-prep; **on this fixture the "deeper analysis" rationale is not supported.**
→ **Branch 3 ("single-agent default, cost-adjusted") condition also met**: single tied-or-won on recall *and* cost ~8.5× less.

**Outcome on this fixture: single-agent ties-or-beats swarm on real-issue recall at ~12% of the cost; swarm shows no recall advantage. The pre-registered rule lands on "verification-insurance / single-default, cost-adjusted."**

## 3. What the recall number hides (read before concluding anything)

The headline (single 0.50 vs swarm 0.44) is real but **partial**, and it is *noise-level at N=1*. Three corrections keep it honest:

1. **Swarm's catches are *cleaner*, not just fewer.** Its catches are cleaner (2 full YES vs 1) and its severities land in the GT band on 3/4 of its caught-and-banded set vs single's 3/6 (single ran three off-by-one). Single's higher recall comes from a *wider, shallower net* — six partial touches, several mis-banded. So "single wins recall / swarm wins calibration" is the truthful shape — closer to a **tie with different failure modes** than a single-agent win.
2. **Swarm's distinctive depth includes its most contestable claim.** Swarm's #1 root cause — "the satire engine is back-loaded for the first half" — is treated by both the blind GT (GT-12) and the single-agent read as a *strength* ("the satire is stable and sharpens"). The scorer classed it a defensible-but-GT-unregistered onset/pacing read, not a hard error. Still: the place swarm went "deeper" than single is exactly the place an independent key disagrees with it. Depth bought contestability, not confirmed truth.
3. **Both modes correctly returned 0 Must-Fix on a near-sound text**, matching the GT control-fact — a win for *both*, and evidence neither over-fires on a strong manuscript. Notably, swarm's separately-run evidence spot-check had already self-corrected its one borderline over-call (the INT-stat finding, downgraded HIGH→"verify"); the GT confirms the math is clean. That is the verification-isolation value the spec endorses — operating as designed.

## 4. Did this reproduce the §2b claim ("~2× findings, deepest, least-biased")?

**No, not on this fixture.**
- **Not "2× findings":** single produced *more* raw findings (B1–B14 scored, vs the ~10 the swarm letter surfaced) — though raw count is a not-scored diagnostic per the spec, so this cuts against the folklore without being decisive.
- **Not "deeper" by recall:** single edged swarm against an independent key.
- **"Least-biased":** unmeasurable here (bundle confound; same-model GT). Swarm's architectural isolation is real, but on this text it did not convert to higher recovery of the independent issue set.

This is **consistent with what §2b already does** — it defaults to single-agent for ≥1M context when the manuscript fits, and only reaches for swarm on final-round / submission work. The pilot supports that default and supports the spec's **"cheap deliverable"**: keep the swarm claim (it rests on prior validation) but **add provenance + a `last re-validated:` date, and stop advertising "deeper analysis" as the everyday rationale** — its defensible everyday value is verification isolation, not higher yield.

## 5. Caveats (the result is only as strong as these are weak)

- **N=1.** One fixture, one model snapshot. Δrecall = 0.06 is within noise. **Directional, not a verdict.** A real conclusion needs the powered multi-fixture fiction corpus the spec specifies.
- **Same-model ground truth.** The key shares the reviews' model family (blind to the letters, but not model-independent). Shared blind spots inflate both recalls equally — so the *difference* (≈0) is more trustworthy than either absolute level, and "neither mode caught GT-02/06/07 well" may reflect a shared model tendency, not a mode effect.
- **Bundle confound.** Swarm = read-isolation **+** a consolidation step; single = neither. This cannot isolate "independent-lens reading" as the mechanism. A null result here is a null for the *bundle*.
- **Contested valence is unresolved, by construction.** Where the GT calls something an issue and a review calls it a strength (GT-02 formula repetition; GT-03 thin arc; GT-04 tonal seam), there is no blind way to adjudicate who is right. Two independent raters (GT-builder, scorer) registered the disagreement; neither resolves it. If the GT over-flagged those, both reviews' recall is understated.
- **Non-blind final synthesis.** The orchestrator (me) authored the swarm arm and wrote this report. Mitigation: the GT-builder, single-review, and scorer were isolated subagents; the recall scoring was label-blind; and the measured result is *mildly unfavorable to the swarm arm I produced* — i.e., not thumb-on-scale for swarm. But the framing judgments here are single-rater and should be read as such.
- **Cost is a floor, not exact.** Swarm's 3.14M excludes parent-orchestration (ref-reading, ledger consolidation, synthesis authoring — plausibly another 0.3–0.6M, pushing the true ratio toward ~10×). Single's 0.37M is one subagent. The gap is real and large; the exact multiple is approximate.

## 6. Bottom line

On one long-fiction fixture, **the swarm did not buy more real-issue recall than a single-agent read, at ~8.5× the token cost.** It bought *tighter severity calibration and more full-credit catches*; the single-agent read bought *breadth and a cleaner read of the near-sound stat-math control*, far cheaper. Both correctly returned zero book-breaking findings. Per the pre-registered rule this is a **"verification-insurance / single-default (cost-adjusted)"** outcome — which matches §2b's existing default and the spec's recommended cheap deliverable (provenance + drop the everyday "deeper" rationale), and does **not**, from N=1, justify retiring swarm for its separately-evidenced uses (writer/verifier isolation in the spot-check; final submission prep).

*Replicate on the powered multi-fiction corpus before treating any of this as more than a single honest data point.*
