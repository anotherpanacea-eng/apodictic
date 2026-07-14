# Ground Truth: unpaid-setup-clean

## Provenance
- **Fixture slug:** unpaid-setup/clean · **Bucket:** R · **Source class:** synthetic-or-derived
- **Matched-pair member:** clean
- **Paired-with:** unpaid-setup/broken
- **Text stored in-repo?:** yes (pinned original synthetic fixture)
- **Base text + plant record:** no mutation — this IS the control. The original synthetic base verbatim: the emphatic
  brass-key setup at ~scene 2 AND its payoff scene both present, the thread paid off.
- **Authored / adapted by:** APODICTIC fiction benchmark (original synthetic; pinned 2026-07-14) · **Registered (date):** 2026-07-06
- **Ground-truth authority:** author-registered; the positive control for the reveal bucket
- **Scope:** FQ1 (inventory) + FQ7 (specificity) in scope; FQ2/FQ3/FQ6 `N/A — positive control`; FQ5 N/A
- **Run configuration:** complete-manuscript mode; canonical slice pass-set {0,1,2,5,7,8,10}

## FGT1 — Structure recovery *(FQ1; Pass 0 outline + Pass 2 beat map)*
   [gt_class: A][construct_lane: fault_injection][evidence_basis: planted_diff][decision_use: report][reliability_status: deterministic]
- **Expected scene inventory:** the base's full scene count (one more than the broken member — the payoff scene is present); scene inventory only

## FGT2 — Planted defect locus *(FQ2)*
- **N/A — positive control.** No planted defect — the setup is paid off.

## FGT3 — Mechanism discrimination *(FQ3)*
- **N/A — positive control.**

## FGT4 — Severity band *(FQ4)*
- **N/A — positive control.** Over-fire ceiling: no SP-NN abandoned/open row and 0 Must-Fix dropped-thread finding on the paid-off setup.

## FGT5 — Arc recovery *(FQ5; Pass 5)*
   [gt_class: B][construct_lane: consensus_alignment][evidence_basis: editor_panel][decision_use: report][reliability_status: provisional_author][alpha_metric: ordinal]
- **Gross arc shape band:** N/A — not scored

## FGT6 — Repair target *(FQ6)*
- **N/A — positive control.**

## FGT7 — Form fairness *(FQ7)*
   [gt_class: A][construct_lane: fault_injection][evidence_basis: planted_diff][decision_use: gate][reliability_status: deterministic]
- **Expected classification:** SOUND
- **False-positive trap:** a spurious "dropped thread / unpaid setup" flag on the brass-key plant that IS paid off (an `SP-NN` marked abandoned when the payoff is on the page). Fired here (the broken member plus the restored payoff scene) it scores FQ7 = 0 and blocks the R bucket.

## Notes
Recognition risk tier: LOW. The specificity control for reveal economy: the same prose the broken member
carries, with the excised payoff scene restored. Because the broken surgery is a deletion (seam-risk
HIGH), the delta here is the key discriminator — a model firing "dropped thread" on BOTH members is
detecting the seam, not the mechanism. Compute the presence-delta before scoring FQ2/FQ4/FQ7.
