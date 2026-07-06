# Ground Truth: continuity-contradiction-clean

## Provenance
- **Fixture slug:** continuity-contradiction/clean · **Bucket:** C · **Source class:** synthetic-or-derived
- **Matched-pair member:** clean
- **Paired-with:** continuity-contradiction/broken
- **Text stored in-repo?:** yes (preparer-derived at pin time — no base bytes in repo)
- **Base text + plant record:** no mutation — this IS the control. The same two entity-fact statements
  are made **mutually consistent** (Edmund is the younger brother in both chapter 2 and chapter 7) and
  the date arithmetic reconciles (marriage 1832, the event six years later = 1838, referred to as 1838).
- **Authored / adapted by:** APODICTIC fiction benchmark (derived) · **Registered (date):** 2026-07-06
- **Ground-truth authority:** author-registered; the positive control for the continuity bucket
- **Scope:** FQ1 (inventory) + FQ7 (specificity) in scope; FQ2/FQ3/FQ6 `N/A — positive control`; FQ5 N/A
- **Run configuration:** complete-manuscript mode; canonical slice pass-set {0,1,2,5,7,8,10}

## FGT1 — Structure recovery *(FQ1; Pass 0 outline + Pass 2 beat map)*
   [gt_class: A][construct_lane: fault_injection][evidence_basis: public_domain_control][decision_use: report][reliability_status: deterministic]
- **Expected scene inventory:** identical to the broken member's inventory (same base; scene inventory only)

## FGT2 — Planted defect locus *(FQ2)*
- **N/A — positive control.** No planted defect — the two facts are mutually consistent.

## FGT3 — Mechanism discrimination *(FQ3)*
- **N/A — positive control.**

## FGT4 — Severity band *(FQ4)*
- **N/A — positive control.** Over-fire ceiling: no CF-NN contradiction row and 0 Must-Fix continuity finding.

## FGT5 — Arc recovery *(FQ5; Pass 5)*
   [gt_class: B][construct_lane: consensus_alignment][evidence_basis: editor_panel][decision_use: report][reliability_status: provisional_author][alpha_metric: ordinal]
- **Gross arc shape band:** N/A — not scored

## FGT6 — Repair target *(FQ6)*
- **N/A — positive control.**

## FGT7 — Form fairness *(FQ7)*
   [gt_class: A][construct_lane: fault_injection][evidence_basis: public_domain_control][decision_use: gate][reliability_status: deterministic]
- **Expected classification:** SOUND
- **False-positive trap:** a spurious continuity contradiction "found" between the two now-consistent facts, or a timeline-arithmetic error asserted on the reconciled dates. Either fired here (the broken member minus the two value swaps + date fix) scores FQ7 = 0 and blocks the C bucket.

## Notes
Recognition risk tier: LOW. The specificity control for continuity: byte-for-byte the broken member
with the two conflicting values made consistent and the dates reconciled. Compute the presence-delta
(a CF-NN row present in broken, absent here) before scoring FQ2/FQ4/FQ7.
