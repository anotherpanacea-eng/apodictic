# Ground Truth: pov-break-broken

## Provenance
- **Fixture slug:** pov-break/broken · **Bucket:** P · **Source class:** synthetic-or-derived
- **Matched-pair member:** broken
- **Paired-with:** pov-break/clean
- **Text stored in-repo?:** yes (preparer-derived at pin time — no base bytes in repo)
- **Base text + plant record:** base = a low-recognition public-domain short story written in
  consistent third-limited (single focal character), pinned in SOURCES.md at build. Planted mutations
  (before→after recorded per locus): (1) ¶18 — insert one sentence rendering a NON-focal character's
  interiority ("She wondered whether he had ever loved her at all") = head-hop #1; (2) ¶24 — insert a
  second non-focal interiority beat = head-hop #2; (3) ¶31 — the focal narration states a fact the
  focal character could not know ("Across town, the letter still lay unopened on the hall table") =
  POV-knowledge leak. Three surgical inserts; no deletion; the surround is unchanged so the mutation,
  not bad prose, is what a hit must catch.
- **Authored / adapted by:** APODICTIC fiction benchmark (derived) · **Registered (date):** 2026-07-06
- **Ground-truth authority:** author-registered; deterministic by construction (the POV breaks are planted)
- **Scope:** FQ1 (inventory), FQ2, FQ3, FQ4, FQ6, FQ7 in scope; FQ5 N/A (not the arc pilot)
- **Run configuration:** complete-manuscript mode; canonical slice pass-set {0,1,2,5,7,8,10}

## FGT1 — Structure recovery *(FQ1; Pass 0 outline + Pass 2 beat map)*
   [gt_class: B/A][construct_lane: consensus_alignment][evidence_basis: editor_panel][decision_use: report][reliability_status: provisional_author][alpha_metric: ordinal]
- **Expected scene inventory:** the base's scene count (recorded at pin; near-A; agreement band: ±1 split/merge)
- **Expected act/movement boundaries:** loci + band (± one scene) — Lane-2, gates only once α-licensed; short-fixture FGT1 is scoped to inventory (boundary bands ride the Carol)

## FGT2 — Planted defect locus *(FQ2)*
   [gt_class: A][construct_lane: fault_injection][evidence_basis: planted_diff][decision_use: gate][reliability_status: deterministic]
- **Defect family:** POV
- **Registered loci:** ¶18, ¶24, ¶31 (the two head-hops + the knowledge leak)
- **Expected engine surface:** `F-P7-*` perspective-slip / head-hop finding at those ¶ loci (a P5
  voice-mechanism `F-P5-*` naming the same break also counts). Not F-P10 — this is not a continuity fact conflict.
- **Evidence-grounding rule:** refs must cite the in-text ¶ loci AND name POV/perspective as the mechanism; "the original keeps one POV" = miss (recall); "something feels off around here" with no mechanism = miss (seam)

## FGT3 — Mechanism discrimination *(FQ3)*
   [gt_class: A][construct_lane: fault_injection][evidence_basis: planted_diff][decision_use: gate][reliability_status: deterministic][alpha_metric: nominal]
- **Expected mechanism family:** a POV/perspective-discipline break (head-hopping + a knowledge leak in an established third-limited), NOT a "voice drift" style issue and NOT a continuity error — the discriminator is that the *narrative access* changes, not that two stated facts conflict.
- **Scoring note:** human judgment over the finding's free-text `mechanism` string (schema does NOT enumerate mechanisms — no mechanical backstop)

## FGT4 — Severity band *(FQ4)*
   [gt_class: A][construct_lane: fault_injection][evidence_basis: planted_diff][decision_use: gate][reliability_status: deterministic]
- **Expected severity band:** Must-Fix..Should-Fix (a three-point POV break in an established limited POV is a load-bearing craft defect)
- **Clean-member over-fire ceiling:** 0 Must-Fix attributed to a POV/perspective break on the clean member

## FGT5 — Arc recovery *(FQ5; Pass 5)*
   [gt_class: B][construct_lane: consensus_alignment][evidence_basis: editor_panel][decision_use: report][reliability_status: provisional_author][alpha_metric: ordinal]
- **Gross arc shape band:** N/A — not scored (not the arc pilot; the arc pilot is the Carol control)

## FGT6 — Repair target *(FQ6)*
   [gt_class: A][construct_lane: fault_injection][evidence_basis: planted_diff][decision_use: gate][reliability_status: deterministic]
- **Correct first repair target:** restore single-focal-character POV discipline at the three loci (cut the non-focal interiority; remove the unknowable fact) — the mechanism, not a line-edit of the sentences
- **Dependency rule (Lane-2 when present):** N/A — a local discipline fix, no upstream dependency

## FGT7 — Form fairness *(FQ7)*
   [gt_class: A][construct_lane: fault_injection][evidence_basis: public_domain_control][decision_use: gate][reliability_status: deterministic]
- **Expected classification:** DEFECT-AS-PLANTED
- **False-positive trap:** N/A — the FQ7 specificity read is scored on the clean member of this pair

## Notes
Recognition risk tier: LOW (low-recognition base). Seam-risk tier: MODERATE (three inserts; the
craft-clean-splice review criterion applies). The matched clean member is the specificity control.
