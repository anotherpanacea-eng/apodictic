# Ground Truth: christmas-carol-arc-control

## Provenance
- **Fixture slug:** christmas-carol-arc-control · **Bucket:** S + arc pilot (Lane-2/B) · **Source class:** public-domain
- **Matched-pair member:** n/a (standalone control)
- **Paired-with:** n/a
- **Text stored in-repo?:** no — referenced (novella length, ~28.5k words); `SOURCES.md` + `run.sh --fetch`, SHA-pinned. No bytes in repo (keeps the repo lean and exercises the fetch path).
- **Base text + plant record:** no mutation — a standalone intentional-device control AND the Lane-2/B arc pilot. Charles Dickens, *A Christmas Carol* (1843), Gutenberg pin in SOURCES.md.
- **Authored / adapted by:** Charles Dickens (PD) · **Registered (date):** 2026-07-06
- **Ground-truth authority:** author-registered for the Lane-1 traps; the FGT5 arc band is provisional_author, REPORTS until a ≥3-editor panel α-licenses it (D-2)
- **Scope:** FQ1 (inventory + boundaries), FQ5 (the arc pilot), FQ7 (the two device traps) in scope; FQ2/FQ3/FQ6 `N/A — positive control`
- **Run configuration:** complete-manuscript mode; canonical slice pass-set {0,1,2,5,7,8,10}

## FGT1 — Structure recovery *(FQ1; Pass 0 outline + Pass 2 beat map)*
   [gt_class: B/A][construct_lane: consensus_alignment][evidence_basis: editor_panel][decision_use: report][reliability_status: provisional_author][alpha_metric: ordinal]
- **Expected scene inventory:** the five staves as movement units, sub-segmented by the three spirits' visitations (near-A inventory; band ±1 split/merge)
- **Expected act/movement boundaries:** the five-stave boundaries (band ± one scene) — Lane-2, REPORTS until α-licensed; the referenced novella is the fixture where FGT1 boundary bands actually mean something (short members scope FGT1 to inventory)

## FGT2 — Planted defect locus *(FQ2)*
- **N/A — positive control.** No planted defect.

## FGT3 — Mechanism discrimination *(FQ3)*
- **N/A — positive control.**

## FGT4 — Severity band *(FQ4)*
- **N/A — positive control.**

## FGT5 — Arc recovery *(FQ5; Pass 5)*
   [gt_class: B][construct_lane: consensus_alignment][evidence_basis: editor_panel][decision_use: report][reliability_status: provisional_author][alpha_metric: ordinal]
- **Gross arc shape band:** agent = Scrooge; shape = denial → confrontation-by-stages (past / present / future) → reversal (redemption). A hit recovers that gross agent+shape within band; a miss invents a different agent or denies the reversal. **REPORTS until ≥3-editor α licenses the band (D-2)** — it never blocks a bucket pre-license; it is the Lane-2 pilot exercising the report→license→gate flow.

## FGT6 — Repair target *(FQ6)*
- **N/A — positive control.**

## FGT7 — Form fairness *(FQ7)*
   [gt_class: A][construct_lane: fault_injection][evidence_basis: public_domain_control][decision_use: gate][reliability_status: deterministic]
- **Expected classification:** INTENTIONAL-AND-EFFECTIVE
- **If intentional:** the device is the five-stave episodic structure and the compressed one-night redemption arc — both are the form working as designed, not a defect. An acceptable engine response names them as intentional/effective, advisory at most (no severity token).
- **False-positive trap:** (1) a Pass 0/2 "missing conventional act structure / no clear three-act shape" Must-Fix fired on the five-stave episodic form; (2) a Pass 5 "rushed arc / redemption unearned by pacing" Must-Fix fired on the deliberately compressed one-night arc. Either fired as a structural failure scores FQ7 = 0 and blocks the S bucket.

## Notes
Recognition risk tier: HIGH (a canonical text) — control pass is CORROBORATING specificity evidence,
recall-flagged per Step 2b. This is the ONLY referenced (fetch-path) member in the slice and the ONLY
one carrying a live Lane-2/B arc band; it exercises both the shippable-kit fetch model and the
report→α-license→gate flow that D-2 defines.
