# Ground Truth: orphan-scene-broken

## Provenance
- **Fixture slug:** orphan-scene/broken · **Bucket:** S · **Source class:** synthetic-or-derived
- **Matched-pair member:** broken
- **Paired-with:** orphan-scene/clean
- **Text stored in-repo?:** yes (pinned original synthetic fixture)
- **Base text + plant record:** base = an original synthetic short work with a clean causal
  chain (each scene's outcome enables the next). Planted mutation (before→after recorded): **one
  causally-inert scene inserted** between the base's scene 3 and scene 4 — written in-register (the same
  voice, period, and diction), plausible on its surface, but **removable without breaking causality**
  (nothing in it is referenced or required downstream; the story's cause-and-effect is identical with it
  cut). One insertion; the surrounding scenes are unchanged.
- **Authored / adapted by:** APODICTIC fiction benchmark (original synthetic; pinned 2026-07-14) · **Registered (date):** 2026-07-06
- **Ground-truth authority:** author-registered; deterministic by construction (the inserted scene is causally inert by design)
- **Scope:** FQ1 (inventory), FQ2, FQ3, FQ4, FQ6, FQ7 in scope; FQ5 N/A
- **Run configuration:** complete-manuscript mode; canonical slice pass-set {0,1,2,5,7,8,10}

## FGT1 — Structure recovery *(FQ1; Pass 0 outline + Pass 2 beat map)*
   [gt_class: A][construct_lane: fault_injection][evidence_basis: planted_diff][decision_use: report][reliability_status: deterministic]
- **Expected scene inventory:** the base's scene count plus one (the inserted scene); recorded at pin (scene inventory only)

## FGT2 — Planted defect locus *(FQ2)*
   [gt_class: A][construct_lane: fault_injection][evidence_basis: planted_diff][decision_use: gate][reliability_status: deterministic]
- **Defect family:** STRUCTURE
- **Registered loci:** the inserted scene between base-scene 3 and base-scene 4 (the orphan)
- **Expected engine surface:** a Pass 2 finding (`F-P2-*` orphan scene / removable-without-breaking-causality). Not F-P8 (nothing was set up or dropped) and not F-P10 (no fact conflict).
- **Evidence-grounding rule:** refs must cite the inserted scene's locus AND name causal inertness (removable without breaking the chain) as the mechanism; "this scene isn't in the original" = miss (recall); "this part drags" with no causal argument = miss (seam/pacing, not the orphan mechanism)

## FGT3 — Mechanism discrimination *(FQ3)*
   [gt_class: A][construct_lane: fault_injection][evidence_basis: planted_diff][decision_use: gate][reliability_status: deterministic][alpha_metric: nominal]
- **Expected mechanism family:** an orphan scene / causal-inertness defect (removable without breaking the causal chain), NOT a pacing complaint and NOT a POV or continuity issue. The discriminator: the diagnosis rests on a **causal** argument (cut it and the chain is intact), not a felt sense that the scene is slow.
- **Scoring note:** human judgment over the finding's free-text `mechanism` string

## FGT4 — Severity band *(FQ4)*
   [gt_class: A][construct_lane: fault_injection][evidence_basis: planted_diff][decision_use: gate][reliability_status: deterministic]
- **Expected severity band:** Should-Fix..Could-Fix (an inert scene is a real structural defect but rarely a hard blocker; the band is intentionally below the POV break's)
- **Clean-member over-fire ceiling:** 0 Must-Fix orphan-scene finding on the clean member (no scene there is causally inert)

## FGT5 — Arc recovery *(FQ5; Pass 5)*
   [gt_class: B][construct_lane: consensus_alignment][evidence_basis: editor_panel][decision_use: report][reliability_status: provisional_author][alpha_metric: ordinal]
- **Gross arc shape band:** N/A — not scored (the S-bucket arc pilot is the referenced Carol control)

## FGT6 — Repair target *(FQ6)*
   [gt_class: A][construct_lane: fault_injection][evidence_basis: planted_diff][decision_use: gate][reliability_status: deterministic]
- **Correct first repair target:** cut the inert scene, OR give it a causal function that the chain requires — the mechanism (causal load-bearing), not a line-edit for pace
- **Dependency rule (Lane-2 when present):** N/A

## FGT7 — Form fairness *(FQ7)*
   [gt_class: A][construct_lane: fault_injection][evidence_basis: planted_diff][decision_use: gate][reliability_status: deterministic]
- **Expected classification:** DEFECT-AS-PLANTED
- **False-positive trap:** N/A — the FQ7 specificity read is scored on the clean member of this pair

## Notes
Recognition risk tier: LOW. Seam-risk tier: MODERATE-HIGH (an inserted scene has a graft join on both
sides — the craft-clean-splice review criterion applies; the matched-pair delta is the runtime backstop
against seam-detection scoring as a hit). The matched clean member (no inserted scene) is the specificity control.
