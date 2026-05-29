# Specialized Audit: Narrative-Decision (StoryScope)
## Version 0.1 (consumer of SETEC Surface 6)
*Created: May 2026*
*Status: consumer-pinning contract for SETEC's `narrative_decision_audit` task surface (`handoff: experimental`).*

---

## Purpose

Score a manuscript against the **30 core narrative-decision features (33 signals)** from Russell et al. 2026's *StoryScope* paper, surfaced through SETEC Voiceprint's `narrative_decision_audit` task surface. The audit answers a structure-level question that the texture-level AI-prose work cannot: not *how are these sentences phrased?* but *how is this story built* — its themes, plot structure, sensory register, reader stance, and temporal arrangement.

Like every audit in this framework, this is **not a provenance detector**. The question is never "did a machine write this." The question is: *where do this manuscript's narrative decisions cluster toward the patterns StoryScope reports for AI-generated narrative, and what kind of revision does that clustering invite?* A human writer who builds stories with over-determined themes, streamlined structure, and performative sensory detail will score the same way — and benefit from the same structural attention.

**Why APODICTIC carries this surface.** Russell et al. 2026 report that detection accuracy drops only ~1.6 macro-F1 points (95.5 → 93.9) after LAMP-style span-level rewriting that scrubs surface artifacts, because removing narrative-decision tells requires *structural* rewrites, not phrase-level substitution. Narrative-decision evidence is therefore the most **rewrite-resistant** signal in the AI-prose family. When it disagrees with texture-level evidence, it is the more durable of the two. That durability is the reason this audit is worth surfacing alongside Tier-1 variance, AIC pattern, and voice-distance evidence — not because it licenses a verdict.

---

## Relationship to the AI-Prose family

This audit is a **sibling** to AI-Prose Calibration and POV Voice Profile, all three backed by SETEC, each answering a distinct question and licensing distinct claims:

| Audit | SETEC surface(s) | Measures | Question |
|---|---|---|---|
| **AI-Prose Calibration** | `smoothing_diagnosis` (variance/repetition) + AIC pattern set | *Texture* — distance from a typical human-prose region | Where does the prose lack the irregularity human consciousness produces by accident? |
| **POV Voice Profile** | `voice_distance` / `voice_profile` | *Voice* — distance from a specific writer/register | Do these POV characters sound different from each other? |
| **Narrative-Decision (this audit)** | `narrative_decision_audit` (Surface 6) | *Structure* — narrative-decision feature scores vs. paper-anchored human/AI means | How is the story built, and do its construction choices cluster toward StoryScope's AI-elevated bundles? |

The three are **complementary, not substitutes**. The framework-side `claim_license` block already encodes this in its `does_not_license` text; the operator-facing rephrasing lives in §The framing note below. Do not collapse narrative-decision findings into the AI-Prose Calibration contamination map — they answer a different question and carry a different (uncalibrated) claim license.

---

## When to activate

- A draft is identified as AI-generated/assisted and the writer wants structure-level evidence beyond texture (the most rewrite-resistant axis).
- AI-Prose Calibration fired (texture-level smoothing) and the writer wants to know whether the *story construction* corroborates or contradicts the texture signal.
- A manuscript reads as competently built but generic at the level of theme, plot shape, and reader stance ("the scaffolding feels off-the-shelf") and the writer wants the per-signal breakdown.
- Cross-checking a mixed-evidence report: narrative-decision evidence adjudicates when texture-level and voice-level signals disagree.

## When NOT to activate

- **Register mismatch.** StoryScope's home register is **long-form fiction**; the surface's `claim_license.length_range_words` is `[2000, 25000]` and `register_match` is `["long_form_fiction"]`. Do not run it as if its signal directions held for essays, op-eds, novels in translation, or short fiction without an operator-supplied polarity check (see §Register discipline). Below 2000 words the per-signal judge values are unreliable; surface the register warnings rather than the scores.
- **The manuscript has severe structural problems.** Fix the spine first; narrative-decision scoring on an incoherent plot wastes effort.
- **The writer wants a verdict.** This audit cannot supply one. If the question is "was this written by AI," the honest answer is that no signal in this framework licenses that claim. Decline and explain.

---

## SETEC delegation

This audit owns no computation. It consumes SETEC Voiceprint's `narrative_decision_audit` task surface through a thin shim and interprets the JSON envelope against this contract.

- **Shim:** `scripts/ai_prose_narrative_decision_audit.py` → SETEC `narrative_decision_audit.py`. All CLI arguments forward unchanged; pass `--help` for SETEC's full surface (judge-backend selection, prompt-version pinning, baseline manifest).
- **Version floor:** SETEC **≥ 1.107.0**. Surface 6 shipped in v1.107.0 (StoryScope integration, PRs #128/#129/#130). This floor is higher than the framework-wide 1.86.0 floor the texture-level shims use; the shim enforces it and fails with an upgrade message rather than a missing-script error. Diagnose location/version problems with `python3 setec_discovery.py` from the audit scripts directory.
- **Discovery order:** `SETEC_VOICEPRINT_DIR` env var → `~/.claude/plugins/marketplaces/*/plugins/setec-voiceprint`. Hard error with install instructions if neither resolves.
- **Calibration status:** `literature_anchored` — the per-signal human/AI means are transcribed from Russell et al. 2026 Table 12. SETEC's capabilities manifest (PR #129) added `literature_anchored` as the canonical status for these signals; APODICTIC's verdict-licensing layer reuses the same vocabulary unchanged.
- **Ships uncalibrated.** The verdict band defaults to `uncalibrated`; SETEC does not ship `--threshold-low` / `--threshold-high` for this surface. Treat any band label other than a per-signal direction as advisory.

### The envelope (schema_version 1.0)

The surface emits the same top-level envelope APODICTIC already parses for `variance_audit`, `voice_distance`, etc. The pass-side helper `setec_runner.run_supplement("narrative_decision_audit.py", args)` parses it; read from `result.results`. The load-bearing keys:

```jsonc
"results": {
  "judge": {                            // provenance only — see §Judge provenance
    "values": {...},
    "per_feature_confidence": {...},
    "judge_identity": { "kind": "...", "model": "...", "model_revision": "...", "prompt_version": "..." },
    "raw_response_truncated": "..."
  },
  "prompt_fingerprint_sha256": "...",   // SHA-256 of system preamble + user prompt; parity-check across runs
  "target": {
    "words": 5023,
    "register_warnings": ["Target is 1450 words; paper's home register is long-form fiction..."]
  },
  "values": { "<feature_key>": "<value or [values]>" },
  "validation_warnings": [...],
  "contributions": [                    // 33 entries — THE load-bearing payload
    {
      "feature_key": "agency_in_resolution",
      "feature_label": "Agency in Resolution",
      "dimension": "PLT", "bundle": "structural_streamlining",
      "option": "protagonist_choice", "leaning": "ai",
      "paper_human_mean": 0.46, "paper_ai_mean": 0.69,
      "target_value": 1.0, "contribution": -1.348,
      "direction": "ai"                 // ai | human | neutral | unavailable
    }, ...
  ],
  "bundles": [                          // 7 entries — convenience rollup
    { "bundle": "structural_streamlining", "label": "AI-elevated: Structural streamlining",
      "n_signals": 8, "n_evaluated": 8, "mean_contribution": -0.842,
      "human_leaning_signals": 1, "ai_leaning_signals": 7, "neutral_signals": 0 }, ...
  ],
  "aggregate": {                        // surfaced for provenance only — NOT pinned
    "score": -1.234, "n_signals_evaluated": 33, "n_signals_total": 33,
    "verdict_band": "uncalibrated", "thresholds": {"low": null, "high": null}
  },
  "run_timestamp_utc": "2026-05-28T14:33:21+00:00"
}
```

### `claim_license` fields to surface

Bound every claim the audit makes by the envelope's `claim_license` block. Surface, at minimum:

- `licenses` — the default block describing what the score *is*.
- `does_not_license` — the anti-verdict discipline: narrative-decision evidence does not entitle binary AI/human verdicts. **This is load-bearing; quote or paraphrase it in every finding.**
- `comparison_set.literature_anchor` — the paper citation string.
- `comparison_set.judge_kind` / `judge_model` and `comparison_set.prompt_fingerprint_sha256` — provenance + cross-run parity value.
- `length_range_words = [2000, 25000]` and `register_match = ["long_form_fiction"]` — surface as the register caveat when the target falls outside them.
- `additional_caveats` — register warnings + the uncalibrated-band caveat, surfaced into the finding.

---

## APODICTIC integration decisions

This section records the consumer-side decisions on the SETEC handoff's open questions. They follow the framework's standing posture: structural diagnosis over verdicts, claims bounded by the license the measurement carries.

### Which surfaces APODICTIC pins

- **Tier A.1 `narrative_decision_audit` — pinned (with experimental awareness).** APODICTIC consumes the schema_version 1.0 envelope through the shim above. The per-signal `contributions` block is the load-bearing payload; per-bundle aggregates are a convenience layer. Because the surface is `handoff: experimental`, a future SETEC v0.2 may bump the aggregate math or swap in a 10-aspect-prompt judge pipeline; APODICTIC pins only the parts SETEC has committed (envelope shape, `contributions`, `claim_license`) and treats the rest as provisional.
- **Tier B vocabulary — adopted as shared vocabulary.** APODICTIC reuses SETEC's `narrative_feature_schema` keys, the 7 `BUNDLE_LABELS`, and the 10 NarraBench `DIMENSION_LABELS` so the audit's output and any APODICTIC-internal narrative representation speak the same language (e.g., a finding can name `feature_key="dominant_emotional_expression"` and surface paper-anchored prevalence without recomputing it). This is a vocabulary alignment, not a runtime dependency on SETEC's data layer.
- **Tier A.2 `narrative_polarity_audit` — NOT pinned.** The calibration-side polarity audit is a non-envelope sidecar (no `TASK_SURFACE`, no `schema_version`, not in the capabilities manifest). It is **not a pin target** in v1. If APODICTIC later wants direction-aware per-signal AUC against an operator-labeled corpus as a contract-stable input, that requires a separate request to SETEC for either (a) envelope wrapping or (b) a manifest entry with explicit `handoff: experimental` framing. Until then it is, at most, an internal SETEC output an operator could read with awareness that its shape may change — never a runtime input to APODICTIC's verdict layer.

### Aggregate posture

**APODICTIC surfaces per-signal `contributions`; it does NOT pin verdicts to SETEC's aggregate `score`.** The aggregate is the mean per-signal contribution in human-z-units (1.0 = paper's human mean, 0.0 = paper's AI mean). It is exposed for single-document inspection, but it is the wrong thing to gate on:

- **Per-signal influence is unequal.** Contributions are `(target_value − ai_mean) / (human_mean − ai_mean)`; the denominator varies ~6.3× across signals, so a small-gap scale feature can produce a single-signal contribution of ±11 that swamps the other 32.
- **Unbounded.** A target value outside both means produces a contribution outside [0, 1] with no natural ceiling.
- **Not what the paper reports.** Russell et al. use XGBoost+SHAP, not a mean-of-ratios. SETEC's aggregate is a single-doc convenience, not a published statistic.

**If a single number is genuinely needed** (e.g., a one-line summary in a mixed-evidence report), compute it from the `contributions` array with a saner pooling rule — **clip each contribution to [−1, 1], then take the mean** — and label it explicitly as an APODICTIC-computed pool, distinct from SETEC's aggregate. Never present either number as a verdict; the verdict band ships `uncalibrated` and there are no thresholds. SETEC's `aggregate.score` and `verdict_band` are surfaced, if at all, as provenance metadata, with the caveats above stated inline.

### Judge provenance

Consume `judge_identity` and `prompt_fingerprint_sha256` as **provenance metadata** for the finding, and treat them as informational. Do **not** gate findings on a specific judge model (Claude Sonnet 4.6, GPT-5.4, etc.) — operators choose models, and pinning to one would re-introduce the model coupling SETEC's pluggable-judge design avoids. The `prompt_fingerprint_sha256` is a version-detection and cross-run parity key: verify identity across runs, not content. A v0.2 that swaps in the 10-aspect-prompt pipeline will change the fingerprint; that is the signal to re-read the contract, not a value to assert about the manuscript.

### Register discipline

StoryScope's home register is **long-form fiction**, and the signal directions are validated there. For manuscripts in that register and length band ([2000, 25000] words), surface the per-signal evidence with its claim license. **Outside that register** (essays, op-eds, novels in translation, short fiction):

- Surface `target.register_warnings` and the `length_range_words` / `register_match` caveat **before** any per-signal reading, and downgrade the finding to "register-uncertain."
- Do **not** infer signal directions; the paper's human/AI means may invert or wash out on an unvalidated register.
- APODICTIC does **not** ship a default polarity-check report alongside the verdict UI. Per-signal polarity validation on an out-of-register corpus is operator-supplied work (it requires a labeled corpus and the non-pinned `narrative_polarity_audit` workflow). When the operator has not supplied that validation, the audit states the register limit and stops short of direction claims.

### Replication scaffold

SETEC's L1/L2/L3 replication tooling (`scripts/replication/`, XGBoost/SHAP/LDA stages, $4k+ operator API budget) is research methodology, **out of scope** for APODICTIC integration. APODICTIC pins against the runtime surface and the vocabulary layer only — never against `replication/manifest_format.py` or the `stages/*.py` files.

---

## Interpreting the output

Read the output in this order. Each step is bounded by the claim license; none of them produces a verdict.

1. **Register gate.** If `target.register_warnings` is non-empty or the word count is outside `[2000, 25000]`, surface the caveat first and mark the finding register-uncertain (see §Register discipline). For out-of-register targets, stop after reporting the limit unless the operator has supplied a polarity check.
2. **Per-signal contributions (load-bearing).** Walk the 33 `contributions`. For each evaluated signal report `feature_label`, `dimension`, `bundle`, `direction` (ai/human/neutral), and the `target_value` vs. `paper_human_mean` / `paper_ai_mean`. Flag signals whose `direction` is `ai` and whose `contribution` is strongly negative; these are the structural decisions clustering toward StoryScope's AI-elevated patterns. Present the data before any synthesis.
3. **Bundle rollup (convenience).** Use the 7 `bundles` for operator-readable groupings: the four AI-elevated bundles (`thematic_over_determination`, `sensory_embodied_performativity`, `structural_streamlining`) and the human-elevated bundles (`intertextual_richness`, `reader_engagement`, `temporal_complexity`, `narrative_diversity`). A one-sentence summary ("this story scores high on sensory_embodied_performativity and structural_streamlining") is fair; a verdict is not.
4. **Convergence with texture-level evidence.** Cross-reference against AI-Prose Calibration findings if available. Agreement strengthens the structural reading; disagreement is informative because narrative-decision evidence is the more rewrite-resistant axis (state which way the evidence points and why, without resolving it into a provenance claim).
5. **Claim-license surfacing.** Close with the `does_not_license` text and the register/uncalibrated caveats. Every number stated must be bounded by the license it carries.

---

## Required outputs

1. **Register & provenance header.** Word count vs. `[2000, 25000]`; register match or warning; judge `kind`/`model` and `prompt_fingerprint_sha256`; calibration status `literature_anchored`; verdict band `uncalibrated`.
2. **Per-signal contributions table.** One row per evaluated signal: feature label, dimension, bundle, direction, target value vs. paper human/AI means, contribution. Present raw data before any synthesis. Mark `unavailable` signals explicitly.
3. **Bundle rollup.** The 7 bundles with mean contribution and ai/human/neutral signal counts; a one-sentence operator-readable summary of which bundles dominate.
4. **Optional APODICTIC-computed pool.** If a single number is requested: clip-to-[−1,1]-then-mean over evaluated contributions, labeled as an APODICTIC pool and explicitly distinguished from SETEC's `aggregate.score`. Never as a verdict.
5. **Convergence note** (if AI-Prose Calibration or voice evidence is present): does the structural evidence corroborate or contradict the texture/voice evidence, and which is more rewrite-resistant.
6. **The framing note** (below), when narrative-decision evidence is presented alongside other AI-prose signals.
7. **Claim-license close.** The `does_not_license` text + register/uncalibrated caveats.

---

## The framing note

When narrative-decision evidence is presented to operators alongside Tier-1 variance / AIC / voice signals, surface this interpretive note (it is *not* a threshold, *not* a verdict, *not* shipped per-signal):

> Narrative-decision signals score how a story is *built* — its themes, plot structure, sensory register, reader stance, temporal arrangement — rather than how its sentences are *phrased*. Russell et al. 2026 reports that detection accuracy drops only ~1.6 macro-F1 points after span-level rewriting that scrubs surface artifacts (95.5 → 93.9), because removing narrative-decision tells requires structural rewrites, not phrase-level substitution. When narrative-decision evidence and texture-level evidence disagree, narrative-decision evidence is the more rewrite-resistant of the two.

---

## Anti-verdict discipline (firewall alignment)

This audit sits behind the same firewall as the rest of APODICTIC: it diagnoses and identifies classes of structural attention; it never invents content and never issues provenance verdicts. The surface **ships uncalibrated**, with no thresholds and an `uncalibrated` verdict band, precisely because the aggregate math is experimental and the signal directions are register-bound. Honor that: surface per-signal evidence and bundle rollups, bound every claim by the license, and route any "is this AI" question back to the standing answer — no signal in this framework licenses that claim.

### §4e propagation

Per `core-editor/references/pass-dependencies.md §4e`, this audit produces **no audit-internal Must-Fix floor and no hard gates**. Its signals propagate at Could-Fix (per-signal, informational) and, at most, Should-Fix when bundle-level AI-leaning concentration *converges* with corroborating texture-level AI-Prose Calibration evidence — never as a standalone gate. The §4e rows are provisional (the surface is `handoff: experimental` and ships uncalibrated) and carry an Override note recording the no-Must-Fix-floor posture.

---

## References

- Russell et al. (2026). *StoryScope: narrative-decision features for human/AI narrative analysis.* arXiv:2604.03136v4. (Surface 6 source; 30 core features / 33 signals / 7 bundles / 10 NarraBench dimensions; Table 12 human/AI group means.)
- SETEC Voiceprint capabilities manifest (PRs #128/#129/#130): `narrative_decision_audit` task surface, `literature_anchored` calibration status, `handoff: experimental`.
- `ai-prose-calibration.md` — texture-level sibling audit (the "complementary, not substitute" framing).
- `pov-voice-profile.md` — voice-level sibling audit (SETEC-backed, opt-in precedent).
- `plugins/setec-voiceprint/references/signals-glossary.md` (SETEC) — glossary cross-reference for the `literature_anchored` vocabulary.
