# Ground Truth: unpaid-setup-broken

## Provenance
- **Fixture slug:** unpaid-setup/broken · **Bucket:** R · **Source class:** synthetic-or-derived
- **Matched-pair member:** broken
- **Paired-with:** unpaid-setup/clean
- **Text stored in-repo?:** yes (pinned original synthetic fixture)
- **Base text + plant record:** base = an original synthetic short work with an emphatic early
  object-plant and a later scene that pays it off. Planted mutation (before→after recorded): the payoff
  **scene is excised** — the base's early emphatic setup (an object introduced with weight: "the small
  brass key she never let out of her sight") is retained at its original locus (~scene 2), but the later
  scene where the key is used is deleted, and the two adjoining scenes are re-stitched so the work still
  **reads complete** (beginning and ending on the page). One deletion + a re-stitch; the setup emphasis
  is untouched so the dropped thread, not a truncated draft, is what a hit must catch.
- **Authored / adapted by:** APODICTIC fiction benchmark (original synthetic; pinned 2026-07-14) · **Registered (date):** 2026-07-06
- **Ground-truth authority:** author-registered; deterministic by construction (the payoff scene was excised)
- **Scope:** FQ1 (inventory), FQ2, FQ3, FQ4 (presence-delta), FQ6, FQ7 in scope; FQ5 N/A
- **Run configuration:** complete-manuscript mode; canonical slice pass-set {0,1,2,5,7,8,10}

## FGT1 — Structure recovery *(FQ1; Pass 0 outline + Pass 2 beat map)*
   [gt_class: A][construct_lane: fault_injection][evidence_basis: planted_diff][decision_use: report][reliability_status: deterministic]
- **Expected scene inventory:** the base's scene count minus one (the excised payoff scene); recorded at pin (scene inventory only)

## FGT2 — Planted defect locus *(FQ2)*
   [gt_class: A][construct_lane: fault_injection][evidence_basis: planted_diff][decision_use: gate][reliability_status: deterministic]
- **Defect family:** REVEAL
- **Registered loci:** the setup locus (~scene 2, the emphatic brass-key plant) — the dropped thread's origin; the payoff is absent by construction
- **Expected engine surface:** a Pass 8 finding (`F-P8-*` dropped thread / unresolved setup) OR a setup-payoff `SP-NN` abandoned/open row — **either counts**; a well-formed `SP-NN` with no `F-<ORIGIN>` finding is conformant (the plant may surface only as the artifact row).
- **Evidence-grounding rule:** refs must cite the setup locus AND name the unpaid/abandoned setup as the mechanism; "the original pays this off later" = miss (recall); "the ending feels thin" with no plant named = miss (seam)

## FGT3 — Mechanism discrimination *(FQ3)*
   [gt_class: A][construct_lane: fault_injection][evidence_basis: planted_diff][decision_use: gate][reliability_status: deterministic][alpha_metric: nominal]
- **Expected mechanism family:** a reveal-economy dropped thread (an emphatic setup with no payoff), NOT a continuity contradiction (no two facts conflict) and NOT an orphan scene (nothing inert was inserted — a load-bearing scene was removed). The SP row's abandoned/open state IS the mechanism statement.
- **Scoring note:** human judgment over the finding's free-text `mechanism` string / the SP row's abandoned state

## FGT4 — Severity band *(FQ4)*
   [gt_class: A][construct_lane: fault_injection][evidence_basis: planted_diff][decision_use: gate][reliability_status: deterministic]
- **Severity-free plant handling:** `presence-delta` — the plant legitimately surfaces as a severity-free `SP-NN` abandoned/open row (the setup-payoff firewall carries no severity token). FQ4 scores the DELTA: the SP-NN row abandoned/open in `broken`, resolved/paid in `clean`. If the plant ALSO surfaces as an `F-P8-*` finding, that finding's severity is scored Must-Fix..Should-Fix.

## FGT5 — Arc recovery *(FQ5; Pass 5)*
   [gt_class: B][construct_lane: consensus_alignment][evidence_basis: editor_panel][decision_use: report][reliability_status: provisional_author][alpha_metric: ordinal]
- **Gross arc shape band:** N/A — not scored (not the arc pilot)

## FGT6 — Repair target *(FQ6)*
   [gt_class: A][construct_lane: fault_injection][evidence_basis: planted_diff][decision_use: gate][reliability_status: deterministic]
- **Correct first repair target:** restore the payoff OR consciously cut the setup — **either direction is a hit** (the mechanism is the unpaid plant, not the specific resolution). A line-edit of the setup sentence that leaves the thread unpaid is a miss.
- **Dependency rule (Lane-2 when present):** N/A

## FGT7 — Form fairness *(FQ7)*
   [gt_class: A][construct_lane: fault_injection][evidence_basis: planted_diff][decision_use: gate][reliability_status: deterministic]
- **Expected classification:** DEFECT-AS-PLANTED
- **False-positive trap:** N/A — the FQ7 specificity read is scored on the clean member of this pair

## Notes
Recognition risk tier: LOW. Seam-risk tier: HIGH (a deletion + re-stitch is the seam-prone surgery — the
craft-clean-splice review criterion is load-bearing here; the matched-pair delta is the runtime backstop).
The matched clean member (setup AND payoff both present) is the specificity control.
