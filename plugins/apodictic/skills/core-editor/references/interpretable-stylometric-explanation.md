# Interpretable Stylometric Explanation — descriptive style-feature labels over the voice fingerprint

*Reference module for the APODICTIC Core Editor. The DESCRIPTIVE labelling layer **on top of** the
Author Voice Fingerprint (#9): it attaches a natural-language gloss to a handful of the salient
**measured** features, each bound by provenance to the exact SETEC `voice_profile` feature it describes.
It does **no new stylometry** and offers **no advice** — it names a measured feature, it never
prescribes a voice change and never fabricates a style claim. Spec + validator:
`docs/interpretable-stylometric-explanation.md`, `scripts/validate.sh style-explanation`. Worked
example: `example-author-style-explanation.md`.*

---

## When to use

When an author has a voice fingerprint (#9) and wants to know, in plain language, **which measured
features characterize the voice** — not just *that* it sits 0.7 from the author centroid. #9 measures
*how distinctive* a voice is and stores it as scalar z-scores; this overlay narrates the handful of
salient features behind those numbers ("the prose leans hard on the definite article", "function-word
profile concentrated in *the / and / but*"). It is a **reading aid**, not a new measurement and not
advice.

## The load-bearing firewall (the riskiest of its wave)

This module is **one preposition** from a Firewall breach. "Your prose leans on the definite article" is
a measured description (in-bounds). "Write more like Author X" / "vary your function-word profile" is a
prescriptive directive (out of bounds — the Firewall's no-prose-execution rule, and #9's
descriptive-not-prescriptive posture). The design makes the prescriptive sentence **unrepresentable in
the data shape**: there is no `recommendation`/`target`/`goal`/`rewrite`/`compare_to_author` field;
`frame` and `direction` are closed descriptive enums; `register` is a comparability class, never a
target author to emulate. The one residual free-text surface (`label`) is scanned by the validator's X4
gate — for a prescriptive voice-directive AND for a comparison-to-emulate construction.

## Consume, don't duplicate — the measured features

Every label glosses a feature SETEC already measured: the `voice_profile` per-family feature inventory
(`families.<family>.top_features[].{feature, mean, sd, cv}`), the same inventory #9 consumes. The
overlay adds only the **label text** plus its `feature_ref` binding back to the measured feature. It
introduces **no new stylometry** — an un-sourced label (empty/absent `feature_ref`) is a **fabricated**
style claim and is rejected (X2).

## Distinct from the voice fingerprint (#9)

#9's unit is *one work's position* in stylometric space (a scalar `metrics` map); this unit is *one
feature's natural-language gloss* (a `label` string + closed descriptive enums). They **compose** — a
profile can carry both block types, and a `style_label` may gloss a feature a `voice_fingerprint`
aggregates into a z-score — but neither subsumes the other. #9 has no natural-language feature labels;
this has no cross-work scalar memory.

## The artifact

The labels live in #9's existing `Author_Voice_Profile.md` (composing with `voice_fingerprint` blocks)
OR a sibling `Author_Style_Explanation*.md` when the operator keeps them separate, under the same
operator-designated author-root. Each label is an `apodictic.style_label.v1` block; the visible markdown
summarizes the labels for the author. The artifact carries a `<!-- author-style-explanation: local-only -->`
marker — a labelled voice profile is voice-cloning-adjacent and never transmitted.

## Descriptive, no severity, local-only

These are descriptions of measured features, never prescriptions and never findings. The overlay carries
**no editorial severity** (no Must/Should/Could; X3 rejects any leak and any embedded
`apodictic:finding` block), and it is **local-only** (no external call, never transmitted; X6). It
reports where the measured features sit; the author alone reads what, if anything, that means.

## Model seam (M1 vs M2)

This is a **model-CPU** capability — the natural-language labels are *produced* by an embedding/scoring
LLM. M1 (built) is the descriptive scaffolding over **injected** labels; the label-generating model is a
deferred **M2** lazy-import + `skipif` seam. The firewall is enforced by the M1 validator regardless of
who authored the labels — the model can only emit labels that pass X1–X6.

Source paper: *Latent Space Interpretation for Stylistic Analysis and Explainable Authorship
Attribution* (arXiv:2409.07072).
