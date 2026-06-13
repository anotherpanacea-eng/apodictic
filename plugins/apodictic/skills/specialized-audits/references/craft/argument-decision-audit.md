# Specialized Audit: Argument-Decision (ArgScope)
## Version 0.1 (consumer of SETEC's `argument_decision_audit` surface)
*Created: June 2026*
*Status: consumer-pinning contract for SETEC's `argument_decision_audit` task surface (`handoff: experimental`).*

---

## Purpose

Score a public-debate / op-ed-register essay's **argumentative structure** against the human / LLM group means Kim, Chang, Pham & Iyyer 2026 ("Argument Collapse: LLMs Flatten Long-Form Public Debate", arXiv:2606.01736) report over public-debate-forum essays (NYT *Room for Debate* ~352w; *Boston Review* ~1,150w), surfaced through SETEC Voiceprint's `argument_decision_audit` task surface. The audit answers a structure-level question that the soundness/warrant audits cannot: not *is this argument valid?* but *how is this argument built* — its **B1 structural arc** (paragraph-role transition rates) and its **B2 discourse-mode mix** — and where do those construction choices cluster toward the patterns the paper reports for LLM-generated argument?

This is the **argument-domain sibling** of the Narrative-Decision (StoryScope) audit. Where the texture-level shims (variance/repetition/voice) measure how *sentences are phrased*, and narrative-decision measures how a *story is built*, this surface measures how an *argument is built*.

Like every audit in this framework, this is **not a provenance detector**. The question is never "did a machine write this." The paper measures argumentative **diversity**, not quality or accuracy, and explicitly does **not** claim human arguments are better. A human who argues thesis-first in an abstract register, leans heavily on the argumentation mode, and rarely moves from support to a fresh proposal will score the same way — and the finding is structural attention, never a verdict.

**Why APODICTIC carries this surface.** It supplies a *structural* reading of an argument that survives sentence-level rewriting, and a descriptive **pre-flag** for whether a dialectical-clarity run is informative. It is complementary to — never a substitute for — the soundness/warrant audits (dialectical clarity, warrant gap, banister): those adjudicate whether the argument *holds*; this one only describes how it is *shaped*. This surface may PRE-FLAG that a dialectical-clarity pass is worth running; it never adjudicates soundness, fairness, or warrant.

---

## Relationship to the argument-shaped-nonfiction family

This audit is a **sibling** to the soundness/warrant audits and a **cousin** to the AI-prose family, each answering a distinct question and licensing distinct claims:

| Audit | SETEC surface(s) | Measures | Question |
|---|---|---|---|
| **Dialectical Clarity / Warrant Gap / Banister** | (APODICTIC-native) | *Soundness* — warrants, burden of proof, concession cost | Does the argument **hold**? |
| **Argument-Decision (this audit)** | `argument_decision_audit` (ArgScope) | *Structure* — B1 arc + B2 discourse-mode scores vs. paper-anchored human/LLM means | How is the argument **built**, and do its construction choices cluster toward the paper's LLM-elevated patterns? |
| **Narrative-Decision (StoryScope)** | `narrative_decision_audit` | *Structure* — narrative-decision feature scores vs. paper-anchored means | How is the **story** built? |
| **AI-Prose Calibration** | `smoothing_diagnosis` + AIC set | *Texture* — distance from a typical human-prose region | Where does the prose lack human irregularity? |

The structure-level and soundness-level audits are **complementary, not substitutes**. Do not collapse argument-decision findings into a soundness verdict — they answer a different question and carry a different (uncalibrated, register-bound) claim license. The framework-side `claim_license.does_not_license` text encodes this; the operator-facing rephrasing lives in §The framing note below.

---

## When to activate

- A public-debate / op-ed-register argumentative essay (≥ ~300 words, multi-paragraph) where the writer wants structural collapse-tells that survive sentence-level rewriting.
- A draft is identified as AI-generated/assisted and the writer wants a structure-level (not texture-level) reading of how the *argument* is built.
- As a **pre-flag** before a dialectical-clarity run: the surface's `pre_flag.dialectical_clarity_informative` reports (descriptively) whether the anchored arc/mode signals converge on the paper's collapse-leaning pattern, i.e. whether a soundness pass is likely to find purchase.

## When NOT to activate

- **You need a soundness / warrant / fairness verdict.** That is dialectical clarity / banister. This surface refuses it.
- **You need an AI-vs-human provenance verdict or a quality judgment.** The surface refuses both — diversity ≠ quality, and there is no "human = better" (and no "concrete = better").
- **Register mismatch (the `distant` tier).** The paper's anchors are **register-bound to public-debate forums**; its Limitations warn they may not transfer to **research / legal / policy** writing. For those registers the band stays unconditionally `uncalibrated` and the audit downgrades to **structural-signals-only** — surface the arc/mode observations without anchored contributions or direction claims (see §Register discipline).
- **No LLM judge or pre-computed label manifest is available.** The per-paragraph role/mode labels come from a pluggable judge; without one (or a `--judge manifest`), there is nothing to score.

---

## SETEC delegation

This audit owns no computation. It consumes SETEC Voiceprint's `argument_decision_audit` task surface through a thin shim and interprets the JSON envelope against this contract.

- **Shim:** `scripts/ai_prose_argument_decision_audit.py` → SETEC `argument_decision_audit.py`. All CLI arguments forward unchanged; pass `--help` for SETEC's full surface (judge backend — `manifest` / `mock` / `anthropic` / `openai` / `gemini` — plus `--judge-manifest` / `--judge-model`).
- **Version floor:** SETEC plugin-version **≥ 1.116.0** — read from the surface's `min_setec_version` in SETEC's capabilities manifest, not hardcoded. 1.116.0 is the plugin-version at which ArgScope Increment A1 shipped, and the first release tag carrying this surface is `v1.116.0`. The floor is **enforced by SETEC's normalized dispatcher at runtime (R2)**: an out-of-floor SETEC comes back as an R3 `version_floor` error envelope (`available: false`, naming the required minimum), not a missing-script error. The consumer does **not** run a redundant `resolve_floor` pre-check; `resolve_floor` + the vendored manifest are retained for the offline drift gate and capability introspection only.
- **Invocation (pass-side):** `setec_runner.run_supplement("argument_decision_audit", args)`, which routes through `setec_run.py argument_decision_audit --json` and parses the `schema_version` 1.0 envelope from **stdout**; read from `result.results`. The direct shim does exactly this for CLI use.
- **Calibration status:** `literature_anchored` for the B1/B2 anchored signals (the human/LLM means are transcribed from Kim et al. 2026 §4.1-4.2 / Tables 26-27). The B3/B4 `reused_signals` carry `calibration_status: heuristic` (no numeric anchor — see below).
- **Ships uncalibrated.** The verdict band is unconditionally `uncalibrated`; there are no `--threshold-low` / `--threshold-high` for this surface. The anchors are a **directional reference, not thresholds**, and a register mismatch downgrades to structural-signals-only.

### The envelope (schema_version 1.0)

The surface emits the same top-level envelope APODICTIC already parses for `variance_audit`, `narrative_decision_audit`, etc. (`available`, `claim_license`, `claim_license_rendered`, `results`, `schema_version`, `target`, `task_surface`, …). The load-bearing keys inside `results`:

```jsonc
"results": {
  "target": { "words": 620, "paragraphs": 6,
              "register_match": ["op-ed"], "register_warnings": [] },
  "judge": {                              // provenance only — see §Judge provenance
    "judge_identity": { "kind": "...", "model": "...", "role_index": ..., "mode_index": ... },
    "per_paragraph_confidence": [...],
    "raw_response_truncated": "...",
    "values": { "paragraphs": [ { "index": 0, "role": "...", "mode": "..." }, ... ] }
  },
  "prompt_fingerprint_sha256": "...",     // parity-check across runs
  "paragraph_labels": [...],
  "observed_signals": { "support_to_proposal_rate": ..., ... },
  "contributions": [                      // 4 entries — THE load-bearing payload
    { "signal_key": "support_to_proposal_rate", "label": "support→proposal transition rate",
      "bundle": "B1_structural_arc", "anchored": true, "calibration_status": "literature_anchored",
      "observed_value": 0.0, "paper_human_mean": 0.123, "paper_ai_mean": 0.294,
      "contribution": 1.719, "direction": "human", "leaning": "ai" },
    { "signal_key": "support_to_support_rate", ... "paper_human_mean": 0.525, "paper_ai_mean": 0.329 },
    { "signal_key": "thesis_opening_tendency", "anchored": false,   // DIRECTIONAL — no anchor
      "contribution": null, "direction": "directional", "paper_human_mean": null, "paper_ai_mean": null },
    { "signal_key": "argumentation_share", "bundle": "B2_discourse_mode",
      "paper_human_mean": 0.715, "paper_ai_mean": 0.897, "direction": "ai", ... }
  ],
  "bundles": [                            // 2 entries — convenience rollup
    { "bundle": "B1_structural_arc", "label": "B1 — Structural arc (paragraph-role transitions)",
      "n_signals": 3, "n_evaluated": 2, "mean_contribution": ...,
      "human_leaning_signals": 2, "ai_leaning_signals": 0 },
    { "bundle": "B2_discourse_mode", "label": "B2 — Discourse-mode mix", "n_signals": 1, ... }
  ],
  "reused_signals": {                     // B3/B4 — DESCRIPTIVE, heuristic, NOT in the aggregate
    "available": true, "calibration_status": "heuristic", "reason": null,
    "signals": { "stance.hedge": ..., "agency.nominalization_per_1k": ...,
                 "agd.discounting_per_1k": ..., "abstraction.mean_concreteness": ... } },
  "pre_flag": {                           // descriptive hook for dialectical-clarity
    "dialectical_clarity_informative": false,
    "basis": "The anchored arc/mode signals do not converge on the paper's collapse-leaning pattern (...)." },
  "aggregate": {                          // surfaced for provenance only — NOT pinned
    "score": ..., "n_signals_evaluated": 3, "n_signals_total": 4,
    "verdict_band": "uncalibrated", "thresholds": { "low": null, "high": null } },
  "validation_warnings": [...],
  "run_timestamp_utc": "2026-..."
}
```

The four derived signals: **B1** — `support_to_proposal_rate` (anchored; human 0.123 / LLM 0.294), `support_to_support_rate` (anchored; human 0.525 / LLM 0.329), `thesis_opening_tendency` (**directional/unanchored** — a tendency reported with no human/LLM anchor); **B2** — `argumentation_share` (anchored; human 0.715 / LLM 0.897).

### `claim_license` fields to surface

Bound every claim by the envelope's `claim_license` block. Surface, at minimum:

- `licenses` — what the score *is* (B1 transition rates + B2 argumentation share vs. the paper's means).
- `does_not_license` — the anti-verdict discipline. **Load-bearing; quote or paraphrase it in every finding.** It denies: an AI/human authorship verdict; a quality judgment (diversity ≠ quality; no "human = better", no "concrete = better"); transfer beyond public-debate forums (the `distant` tier); a soundness/warrant/fairness verdict (that's dialectical-clarity, which this may PRE-FLAG but never adjudicates). It also states the **temporal confound** (the human/LLM means are a dated snapshot of the models the paper studied; the gap shifts as models change) and that B3/B4 abstraction & stance ship as descriptive `reused_signals` (heuristic, **no numeric anchor by design** — marker density is a different construct from the paper's judge-rated stance strength).
- `comparison_set.literature_anchor` — the Kim et al. 2026 citation string.
- `comparison_set.judge_kind` / `judge_model` and `comparison_set.prompt_fingerprint_sha256` — provenance + cross-run parity value. **Judge fidelity varies by backend**: `mock` is a deterministic test stub (infer nothing from it); `manifest` is only as good as whatever produced the labels (unverifiable by this surface — read `judge.provenance.model`); the API backends are a faithful per-paragraph labeler.
- `length_range_words = [300, 8000]` and `register_match = ["op-ed"]` — surface as the register caveat when the target falls outside them.
- `additional_caveats` — the mock-judge warning + the uncalibrated/register-bound caveat, surfaced into the finding.

---

## APODICTIC integration decisions

These follow the framework's standing posture: structural diagnosis over verdicts, claims bounded by the license the measurement carries.

### Which surfaces APODICTIC pins

- **`argument_decision_audit` — pinned (with experimental awareness).** APODICTIC consumes the schema_version 1.0 envelope through the shim. The per-signal `contributions` block is the load-bearing payload; the 2 `bundles` are a convenience layer. Because the surface is `handoff: experimental`, a future SETEC v0.2 may bump the aggregate math, the judge-prompt pipeline, or add the deferred dynamic signals; APODICTIC pins only the parts SETEC has committed (envelope shape, `contributions`, `claim_license`) and treats the rest as provisional.
- **B3/B4 `reused_signals` — NOT pinned as anchored evidence.** They ship `calibration_status: heuristic` with **no numeric anchor by design** (marker density is a different construct from the paper's judge-rated per-essay stance strength). Surface them as descriptive context only — never as anchored contributions, never in the aggregate, never as a direction claim.
- **Deferred dynamic signals — not present.** The two dynamic collapse signals (disappearing-guard, discounting-straw-men) are a deferred SETEC follow-up; they are not a pin target until SETEC ships them with explicit framing.

### Aggregate posture

**APODICTIC surfaces per-signal `contributions`; it does NOT pin verdicts to SETEC's aggregate `score`.** The aggregate is the mean per-signal contribution (1.0 = paper's human mean, 0.0 = paper's LLM mean). It is exposed for single-document inspection but is the wrong thing to gate on:

- **Per-signal influence is unequal.** Contributions are `(observed − ai_mean) / (human_mean − ai_mean)`; the denominator varies across signals, so a small-gap signal can produce a contribution far outside [0, 1] that swamps the others (e.g. the fixture's `support_to_support_rate` contribution ≈ 3.4).
- **Unbounded.** An observed value outside both means produces a contribution outside [0, 1] with no natural ceiling.
- **Only 3 of 4 signals are anchored.** `thesis_opening_tendency` is directional with no anchor and contributes nothing to the aggregate; the aggregate is a mean over the evaluated anchored signals only.

**If a single number is genuinely needed**, compute it from the `contributions` array with a saner pooling rule — **clip each contribution to [−1, 1], then take the mean over evaluated anchored signals** — and label it explicitly as an APODICTIC-computed pool, distinct from SETEC's `aggregate.score`. Never present either number as a verdict; the band ships `uncalibrated` with no thresholds.

### Judge provenance

Consume `judge_identity` and `prompt_fingerprint_sha256` as **provenance metadata**, informational only. Do **not** gate findings on a specific judge model — operators choose models, and pinning to one re-introduces the coupling SETEC's pluggable-judge design avoids. Treat `mock` runs as non-informative test stubs. The `prompt_fingerprint_sha256` is a version-detection / cross-run parity key: a v0.2 that changes the prompt changes the fingerprint — the signal to re-read the contract, not a value to assert about the essay.

### Register discipline

The paper's home register is **public-debate / op-ed**, and the signal directions are validated there. For targets in that register and length band (`[300, 8000]` words), surface the per-signal evidence with its claim license. **Outside that register** — research, legal, policy writing (the `distant` tier) — and outside the length band:

- Surface `target.register_warnings` and the `length_range_words` / `register_match` caveat **before** any per-signal reading, and downgrade to **structural-signals-only**.
- Do **not** infer signal directions; the paper's human/LLM means may invert or wash out on an unvalidated register, and the Limitations explicitly warn against transfer.
- High-stakes genres (research/legal/policy) default to `distant` / no-verdict. APODICTIC does not ship a default polarity-check report; per-signal polarity validation on an out-of-register corpus is operator-supplied work.

---

## Interpreting the output

Read in this order. Each step is bounded by the claim license; none produces a verdict.

1. **Register gate.** If `target.register_warnings` is non-empty or word count is outside `[300, 8000]`, surface the caveat first and mark the finding register-uncertain / structural-signals-only (see §Register discipline). For the `distant` tier, stop after the structural observations unless the operator has supplied a polarity check.
2. **Judge-fidelity gate.** Read `judge.judge_identity.kind`. If `mock`, state that the run is a non-informative test stub and stop. If `manifest`, note the labels are unverified (read the provenance model). Only API-backed (or trusted-manifest) runs license per-signal reading.
3. **Per-signal contributions (load-bearing).** Walk the 4 `contributions`. For each anchored signal report `label`, `bundle`, `direction` (human/ai), `observed_value` vs. `paper_human_mean` / `paper_ai_mean`, and the contribution. Mark `thesis_opening_tendency` as directional (no anchor). Mark `unavailable` signals explicitly. Present the data before any synthesis.
4. **Bundle rollup (convenience).** Use the 2 `bundles` (B1 structural arc, B2 discourse mode) for an operator-readable grouping. A one-sentence summary is fair; a verdict is not.
5. **`reused_signals` (descriptive only).** Optionally surface B3/B4 stance/agency/abstraction markers as heuristic context, explicitly flagged as not-anchored and not-in-aggregate.
6. **Pre-flag.** Report `pre_flag.dialectical_clarity_informative` + its `basis` as a descriptive hook — "the anchored signals (do/do not) converge on the paper's collapse-leaning pattern, so a dialectical-clarity run is (likely/unlikely) to find purchase." Never as a soundness claim.
7. **Claim-license surfacing.** Close with the `does_not_license` text and the register/uncalibrated/temporal caveats. Every number stated must be bounded by the license it carries.

---

## Required outputs

1. **Register & provenance header.** Word count vs. `[300, 8000]`; register match or warning (and the `distant`-tier downgrade if applicable); judge `kind`/`model` and `prompt_fingerprint_sha256`; calibration status; verdict band `uncalibrated`.
2. **Per-signal contributions table.** One row per signal: label, bundle, anchored/directional, direction, observed value vs. paper human/LLM means, contribution. Raw data before synthesis. Mark `unavailable` explicitly.
3. **Bundle rollup.** B1 / B2 with mean contribution and human/ai/neutral signal counts; a one-sentence operator-readable summary.
4. **Optional `reused_signals` context.** B3/B4 markers, flagged heuristic / not-anchored / not-in-aggregate.
5. **Pre-flag note.** `dialectical_clarity_informative` + basis, framed as descriptive (not a soundness verdict).
6. **The framing note** (below), when argument-decision evidence is presented alongside soundness or AI-prose signals.
7. **Claim-license close.** The `does_not_license` text + register/uncalibrated/temporal caveats.

---

## The framing note

When argument-decision evidence is presented to operators alongside dialectical-clarity, warrant, or AI-prose signals, surface this interpretive note (it is *not* a threshold, *not* a verdict):

> Argument-decision signals score how an argument is *built* — its paragraph-role arc and discourse-mode mix — against the human / LLM group means Kim et al. 2026 report for public-debate-forum essays. They measure argumentative *diversity*, not quality, accuracy, or soundness, and license no authorship verdict: a human arguing thesis-first in an abstract register scores the same. The anchors are register-bound to public-debate forums and are a dated snapshot of the models the paper studied. This surface may flag whether a dialectical-clarity (soundness) run is likely to be informative; it never adjudicates soundness itself.

---

## Anti-verdict discipline (firewall alignment)

This audit sits behind the same firewall as the rest of APODICTIC: it diagnoses classes of structural attention; it never invents content and never issues provenance, quality, or soundness verdicts. The surface **ships uncalibrated**, with no thresholds and an `uncalibrated` band, because the anchors are register-bound and a dated snapshot. Honor that: surface per-signal evidence and the bundle rollup, bound every claim by the license, and route any "is this AI" or "is this argument sound" question back to the standing answers — no signal in this surface licenses either claim (soundness is dialectical clarity's question, and this surface only PRE-FLAGS it).

---

## References

- Kim, Chang, Pham & Iyyer (2026). *Argument Collapse: LLMs Flatten Long-Form Public Debate.* arXiv:2606.01736v3. (Surface source; B1 paragraph-role transition rates + B2 discourse-mode share; §4.1-4.2 / Tables 26-27 human/LLM group means over NYT *Room for Debate* + *Boston Review* essays.)
- SETEC Voiceprint capabilities manifest: `argument_decision_audit` task surface, `literature_anchored` calibration status, `handoff: experimental`, `min_setec_version: 1.116.0`.
- `narrative-decision-audit.md` — the narrative-domain sibling (StoryScope; the "structure, not texture; complementary, not substitute" framing precedent).
- `dialectical-clarity.md` and the warrant/banister audits — the soundness-level siblings this surface pre-flags but never replaces.
- `plugins/setec-voiceprint/references/signals-glossary.md` (SETEC) — glossary cross-reference for the anchored-signal vocabulary.
