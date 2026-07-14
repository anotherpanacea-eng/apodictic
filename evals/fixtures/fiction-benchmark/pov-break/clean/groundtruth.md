# Ground Truth: pov-break-clean

## Provenance
- **Fixture slug:** pov-break/clean · **Bucket:** P · **Source class:** synthetic-or-derived
- **Matched-pair member:** clean
- **Paired-with:** pov-break/broken
- **Text stored in-repo?:** yes (pinned original synthetic fixture)
- **Base text + plant record:** no mutation — this IS the control (the original synthetic base verbatim, consistent third-limited throughout).
- **Authored / adapted by:** APODICTIC fiction benchmark (original synthetic; pinned 2026-07-14) · **Registered (date):** 2026-07-06
- **Ground-truth authority:** author-registered; the positive control for the pov-break bucket
- **Scope:** FQ1 (inventory) + FQ7 (specificity) in scope; FQ2/FQ3/FQ6 `N/A — positive control`; FQ5 N/A
- **Run configuration:** complete-manuscript mode; canonical slice pass-set {0,1,2,5,7,8,10}

## FGT1 — Structure recovery *(FQ1; Pass 0 outline + Pass 2 beat map)*
   [gt_class: B/A][construct_lane: consensus_alignment][evidence_basis: editor_panel][decision_use: report][reliability_status: provisional_author][alpha_metric: ordinal]
- **Expected scene inventory:** identical to the broken member's inventory band (same base; near-A; band ±1 split/merge)

## FGT2 — Planted defect locus *(FQ2)*
- **N/A — positive control.** No planted defect to locate (this is the clean base).

## FGT3 — Mechanism discrimination *(FQ3)*
- **N/A — positive control.**

## FGT4 — Severity band *(FQ4)*
- **N/A — positive control.** Over-fire ceiling: 0 Must-Fix attributed to a POV/perspective break.

## FGT5 — Arc recovery *(FQ5; Pass 5)*
   [gt_class: B][construct_lane: consensus_alignment][evidence_basis: editor_panel][decision_use: report][reliability_status: provisional_author][alpha_metric: ordinal]
- **Gross arc shape band:** N/A — not scored (not the arc pilot)

## FGT6 — Repair target *(FQ6)*
- **N/A — positive control.**

## FGT7 — Form fairness *(FQ7)*
   [gt_class: A][construct_lane: fault_injection][evidence_basis: planted_diff][decision_use: gate][reliability_status: deterministic]
- **Expected classification:** SOUND
- **False-positive trap:** a naive Pass 7 "distance inconsistency" or Pass 5 "voice drift" Must-Fix fired on intact third-limited discipline. Firing it here (the same prose the broken member carries, minus the three POV inserts) scores FQ7 = 0 and blocks the P bucket.

## Notes
Recognition risk tier: LOW. This clean member is the airtight specificity control: it is the broken
member minus exactly the three planted POV inserts, so a false fire cannot be excused as "the base was
just bad prose." Compute the matched-pair delta (broken-vs-clean) before scoring FQ2/FQ4/FQ7.
