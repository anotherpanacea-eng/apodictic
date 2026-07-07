# Ground Truth: gift-of-magi-reveal-control

## Provenance
- **Fixture slug:** gift-of-magi-reveal-control · **Bucket:** R · **Source class:** public-domain
- **Matched-pair member:** n/a (standalone control)
- **Paired-with:** n/a
- **Text stored in-repo?:** yes (short, PD — preparer-derived from the Gutenberg pin at first retrieval)
- **Base text + plant record:** no mutation — a standalone intentional-device control. O. Henry,
  *The Gift of the Magi* (1905, ~2.1k words), from *The Four Million*; Gutenberg pin in SOURCES.md.
- **Authored / adapted by:** O. Henry (PD) · **Registered (date):** 2026-07-06
- **Ground-truth authority:** author-registered; the fairness reading is uncontested (both withholdings are diegetically fair)
- **Scope:** FQ1 (inventory) + FQ7 (specificity, the trap) in scope; FQ2/FQ3/FQ6 `N/A — positive control`
- **Run configuration:** complete-manuscript mode; canonical slice pass-set {0,1,2,5,7,8,10}

## FGT1 — Structure recovery *(FQ1; Pass 0 outline + Pass 2 beat map)*
   [gt_class: A][construct_lane: fault_injection][evidence_basis: public_domain_control][decision_use: report][reliability_status: deterministic]
- **Expected scene inventory:** the story's scene units (Della's sacrifice / Jim's return / the twin reveal); scene inventory only

## FGT2 — Planted defect locus *(FQ2)*
- **N/A — positive control.** No planted defect.

## FGT3 — Mechanism discrimination *(FQ3)*
- **N/A — positive control.**

## FGT4 — Severity band *(FQ4)*
- **N/A — positive control.**

## FGT5 — Arc recovery *(FQ5; Pass 5)*
   [gt_class: B][construct_lane: consensus_alignment][evidence_basis: editor_panel][decision_use: report][reliability_status: provisional_author][alpha_metric: ordinal]
- **Gross arc shape band:** N/A — not scored (not the arc pilot; this control's positive anchor is the reveal-fairness read, below)

## FGT6 — Repair target *(FQ6)*
- **N/A — positive control.**

## FGT7 — Form fairness *(FQ7)*
   [gt_class: A][construct_lane: fault_injection][evidence_basis: public_domain_control][decision_use: gate][reliability_status: deterministic]
- **Expected classification:** INTENTIONAL-AND-EFFECTIVE
- **If intentional:** the device is dual withheld knowledge (Della's sold hair; Jim's sold watch) resolving in the twin reveal — the Pass 8 fairness tests PASS: diegetic cues are available and the narration withholds nothing the POV would unfairly surface early. An acceptable engine response names the twin-reveal structure as intentional and fair, advisory at most (no severity token).
- **False-positive trap:** a Pass 8 "withheld information / unfair misdirection / reader cheated" Must-Fix fired on the fair twin reveal. Firing it scores FQ7 = 0 and blocks the R bucket. Correct: the withholding is fair by the fairness tests.

## Notes
Recognition risk tier: HIGH (a canonical text) — control pass is CORROBORATING specificity evidence,
recall-flagged per Step 2b. This control tests the SAME reveal-economy pass (Pass 8) the unpaid-setup
pair exercises for sensitivity — here the correct call is "fair, leave it alone."
