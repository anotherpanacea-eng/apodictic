# Ground Truth: yellow-wallpaper-voice-control

## Provenance
- **Fixture slug:** yellow-wallpaper-voice-control · **Bucket:** P (+S) · **Source class:** public-domain
- **Matched-pair member:** n/a (standalone control)
- **Paired-with:** n/a
- **Text stored in-repo?:** yes (short, PD — preparer-derived from the Gutenberg pin at first retrieval)
- **Base text + plant record:** no mutation — a standalone intentional-device control. Charlotte Perkins
  Gilman, *The Yellow Wallpaper* (1892, ~6k words), Gutenberg pin in SOURCES.md.
- **Authored / adapted by:** Charlotte Perkins Gilman (PD) · **Registered (date):** 2026-07-06
- **Ground-truth authority:** author-registered; the trap is a canonical, uncontested reading of the text
- **Scope:** FQ1 (inventory) + FQ7 (specificity, the trap) in scope; FQ2/FQ3/FQ6 `N/A — positive control`
- **Run configuration:** complete-manuscript mode; canonical slice pass-set {0,1,2,5,7,8,10}

## FGT1 — Structure recovery *(FQ1; Pass 0 outline + Pass 2 beat map)*
   [gt_class: A][construct_lane: fault_injection][evidence_basis: public_domain_control][decision_use: report][reliability_status: deterministic]
- **Expected scene inventory:** the journal entries as scene units (dated/undated diary sections); scene inventory only

## FGT2 — Planted defect locus *(FQ2)*
- **N/A — positive control.** No planted defect.

## FGT3 — Mechanism discrimination *(FQ3)*
- **N/A — positive control.**

## FGT4 — Severity band *(FQ4)*
- **N/A — positive control.**

## FGT5 — Arc recovery *(FQ5; Pass 5)*
   [gt_class: B][construct_lane: consensus_alignment][evidence_basis: editor_panel][decision_use: report][reliability_status: provisional_author][alpha_metric: ordinal]
- **Gross arc shape band:** N/A — not scored (not the arc pilot; this control's positive anchor is the voice-intentionality read, below)

## FGT6 — Repair target *(FQ6)*
- **N/A — positive control.**

## FGT7 — Form fairness *(FQ7)*
   [gt_class: A][construct_lane: fault_injection][evidence_basis: public_domain_control][decision_use: gate][reliability_status: deterministic]
- **Expected classification:** INTENTIONAL-AND-EFFECTIVE
- **If intentional:** the device is a deliberately deteriorating, unreliable first-person narrator — the narrative voice's progressive unreliability IS the story's method and meaning (the confinement's psychological toll rendered from inside). An acceptable engine response names the deterioration as intentional and effective, advisory at most (no Must/Should-Fix severity token attached).
- **False-positive trap:** a naive Pass 5 "voice drift / voice-consistency" Must-Fix or a Pass 7 "distance inconsistency / POV instability" Must-Fix fired on the intentional deterioration. Firing it as a structural failure scores FQ7 = 0 and blocks the bucket. Correct: recognized as intentional and effective.

## Notes
Recognition risk tier: HIGH (a canonical text) — per Step 2b, a control pass is CORROBORATING specificity
evidence, recall-flagged. For a control, recognition mostly biases toward the correct answer ("this is a
masterpiece"); the trap keeps teeth only if the engine diagnoses rather than recalls, which the
recognition probe + evidence-grounding rule test.
