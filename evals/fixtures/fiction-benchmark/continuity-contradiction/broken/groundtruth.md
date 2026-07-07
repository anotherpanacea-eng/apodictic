# Ground Truth: continuity-contradiction-broken

## Provenance
- **Fixture slug:** continuity-contradiction/broken · **Bucket:** C · **Source class:** synthetic-or-derived
- **Matched-pair member:** broken
- **Paired-with:** continuity-contradiction/clean
- **Text stored in-repo?:** yes (preparer-derived at pin time — no base bytes in repo)
- **Base text + plant record:** base = a low-recognition public-domain short work that states an entity
  fact in two places and dates one event. Planted mutations (before→after recorded): (1) chapter 2 —
  set an entity attribute to a NOVEL value ("her brother Edmund was three years younger"); (2) chapter 7
  — set the SAME attribute to an incompatible NOVEL value ("Edmund, her elder by five years"). Both
  values are novel (neither matches any famous original) — **dual mutation** — so recall of the base
  provides no shortcut; the contradiction is internal-only. (3) a timeline-arithmetic error: an event
  dated "the spring of 1841" is later referred to as "six years after her marriage in 1832" (would be
  1838, not 1841).
- **Authored / adapted by:** APODICTIC fiction benchmark (derived) · **Registered (date):** 2026-07-06
- **Ground-truth authority:** author-registered; deterministic by construction (both loci mutated to conflicting novel values)
- **Scope:** FQ1 (inventory), FQ2, FQ3, FQ4 (presence-delta), FQ6, FQ7 in scope; FQ5 N/A
- **Run configuration:** complete-manuscript mode; canonical slice pass-set {0,1,2,5,7,8,10}

## FGT1 — Structure recovery *(FQ1; Pass 0 outline + Pass 2 beat map)*
   [gt_class: A][construct_lane: fault_injection][evidence_basis: planted_diff][decision_use: report][reliability_status: deterministic]
- **Expected scene inventory:** the base's scene count (recorded at pin; near-A; scene inventory only for a short work)

## FGT2 — Planted defect locus *(FQ2)*
   [gt_class: A][construct_lane: fault_injection][evidence_basis: planted_diff][decision_use: gate][reliability_status: deterministic]
- **Defect family:** CONTINUITY
- **Registered loci:** chapter 2 and chapter 7 (the two conflicting attribute statements); plus the timeline-arithmetic locus (the 1832/1841 conflict)
- **Expected engine surface:** a Pass 10 finding (`F-P10-*`) OR a continuity-bible `CF-NN` contradiction row pairing the two conflicting facts — **either counts**; a well-formed `CF-NN` with no `F-<ORIGIN>` finding is conformant. The timeline error may additionally surface via the timeline validators.
- **Evidence-grounding rule:** refs must cite BOTH in-text loci AND name the conflict as the mechanism; "the original says younger" = miss (recall)

## FGT3 — Mechanism discrimination *(FQ3)*
   [gt_class: A][construct_lane: fault_injection][evidence_basis: planted_diff][decision_use: gate][reliability_status: deterministic][alpha_metric: nominal]
- **Expected mechanism family:** a continuity contradiction (two stated facts about the same entity+attribute simply conflict), NOT a reveal-economy error — no reader-knowledge management is implicated. The CF row's paired-fact conflict IS the mechanism statement.
- **Scoring note:** human judgment over the finding's free-text `mechanism` string / the CF row's conflict pairing

## FGT4 — Severity band *(FQ4)*
   [gt_class: A][construct_lane: fault_injection][evidence_basis: planted_diff][decision_use: gate][reliability_status: deterministic]
- **Severity-free plant handling:** `presence-delta` — the plant legitimately surfaces as a severity-free `CF-NN` row (the continuity-bible firewall carries no severity token). FQ4 scores the DELTA: the CF-NN contradiction row present in `broken`, absent in `clean`. If the plant ALSO surfaces as an `F-P10-*` finding, that finding's severity is scored Must-Fix..Should-Fix.

## FGT5 — Arc recovery *(FQ5; Pass 5)*
   [gt_class: B][construct_lane: consensus_alignment][evidence_basis: editor_panel][decision_use: report][reliability_status: provisional_author][alpha_metric: ordinal]
- **Gross arc shape band:** N/A — not scored (not the arc pilot)

## FGT6 — Repair target *(FQ6)*
   [gt_class: A][construct_lane: fault_injection][evidence_basis: planted_diff][decision_use: gate][reliability_status: deterministic]
- **Correct first repair target:** locate the contradiction (surface both conflicting facts) before choosing which fact wins — the editor's job is to flag, not to pick canon
- **Dependency rule (Lane-2 when present):** locate-the-contradiction MUST precede choosing-which-fact-wins (the continuity-bible firewall: surface, do not resolve)

## FGT7 — Form fairness *(FQ7)*
   [gt_class: A][construct_lane: fault_injection][evidence_basis: public_domain_control][decision_use: gate][reliability_status: deterministic]
- **Expected classification:** DEFECT-AS-PLANTED
- **False-positive trap:** N/A — the FQ7 specificity read is scored on the clean member of this pair

## Notes
Recognition risk tier: LOW (dual mutation to novel values defeats recall). Seam-risk tier: LOW (value
swaps, no structural graft). The matched clean member (same two facts made mutually consistent) is the
specificity control.
