# Ground Truth: orphan-scene-clean

## Provenance
- **Fixture slug:** orphan-scene/clean · **Bucket:** S · **Source class:** synthetic-or-derived
- **Matched-pair member:** clean
- **Paired-with:** orphan-scene/broken
- **Text stored in-repo?:** yes (pinned original synthetic fixture)
- **Base text + plant record:** no mutation — this IS the control. The original synthetic base verbatim: a clean
  causal chain, every scene load-bearing (its outcome enables the next), no inert scene.
- **Authored / adapted by:** APODICTIC fiction benchmark (original synthetic; pinned 2026-07-14) · **Registered (date):** 2026-07-06
- **Ground-truth authority:** author-registered; the positive control for the structure bucket
- **Scope:** FQ1 (inventory) + FQ7 (specificity) in scope; FQ2/FQ3/FQ6 `N/A — positive control`; FQ5 N/A
- **Run configuration:** complete-manuscript mode; canonical slice pass-set {0,1,2,5,7,8,10}

## FGT1 — Structure recovery *(FQ1; Pass 0 outline + Pass 2 beat map)*
   [gt_class: A][construct_lane: fault_injection][evidence_basis: planted_diff][decision_use: report][reliability_status: deterministic]
- **Expected scene inventory:** the base's scene count (one fewer than the broken member — no inserted scene); scene inventory only

## FGT2 — Planted defect locus *(FQ2)*
- **N/A — positive control.** No planted defect — every scene is causally load-bearing.

## FGT3 — Mechanism discrimination *(FQ3)*
- **N/A — positive control.**

## FGT4 — Severity band *(FQ4)*
- **N/A — positive control.** Over-fire ceiling: 0 Must-Fix orphan-scene finding (no scene is causally inert).

## FGT5 — Arc recovery *(FQ5; Pass 5)*
   [gt_class: B][construct_lane: consensus_alignment][evidence_basis: editor_panel][decision_use: report][reliability_status: provisional_author][alpha_metric: ordinal]
- **Gross arc shape band:** N/A — not scored

## FGT6 — Repair target *(FQ6)*
- **N/A — positive control.**

## FGT7 — Form fairness *(FQ7)*
   [gt_class: A][construct_lane: fault_injection][evidence_basis: planted_diff][decision_use: gate][reliability_status: deterministic]
- **Expected classification:** SOUND
- **False-positive trap:** a spurious "orphan scene / removable without causal break" flag on a scene that IS load-bearing (mistaking a quiet or reflective scene for an inert one). Fired here (the broken member minus the inserted inert scene) it scores FQ7 = 0 and blocks the S bucket.

## Notes
Recognition risk tier: LOW. The specificity control for structure: the same prose the broken member
carries, minus the one inserted inert scene. The delta discriminates a causal-inertness diagnosis from
seam-detection of the graft join. Compute the matched-pair delta before scoring FQ2/FQ4/FQ7.
