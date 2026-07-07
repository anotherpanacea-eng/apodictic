# Fiction Ground-Truth Template

Copy this file to `evals/fixtures/fiction-benchmark/<fixture-slug>/groundtruth.md`
and fill in every in-scope field. Ground truth must be registered **before**
any engine run is scored against it (`groundtruth.md` written after seeing the
run output is void). Fields map to the seven fiction test questions (FQ1–FQ7);
see [../docs/fiction-benchmark-spec.md](../docs/fiction-benchmark-spec.md) for
the schema rationale, the multi-lane validity architecture, and the convergence
protocol, and [rubrics/fiction-benchmark.md](rubrics/fiction-benchmark.md) for
scoring.

The mechanical validator `fiction-groundtruth-check`
(`scripts/fiction_groundtruth.py`) checks this key's **form only** — it is a
key-conformance gate, never a semantic judge and never a run scorer. Every FQ is
a human scorer judgment against the key per the rubric.

## The multi-lane tags (every scored anchor carries five)

Each in-scope FGT heading carries a tag run on the line **immediately under the
heading**:
`[gt_class: A|B|C][construct_lane: …][evidence_basis: …][decision_use: …][reliability_status: …]`
(+ `[alpha_metric: ordinal|nominal]` on Lane-2 / `consensus_alignment` anchors).

| Field | Values | Declares |
|---|---|---|
| `gt_class` | `A` \| `B` \| `C` (compound `B/A` allowed when a heading spans two ontologies — FGT1) | Ontology. A = mechanical/planted; B = structural-consensus (banded); C = interpretive. |
| `construct_lane` | `fault_injection` \| `consensus_alignment` \| `reader_effect` \| `editorial_preference` | Which validity lane. |
| `evidence_basis` | `planted_diff` \| `public_domain_control` \| `editor_panel` \| `reader_study` \| `preference_pair` | Where the ground truth comes from. |
| `decision_use` | `gate` \| `report` \| `exploratory` | What the benchmark does with the anchor. |
| `reliability_status` | `deterministic` \| `provisional_author` \| `panel_confirmed` \| `low_agreement` | How trustworthy the label is now. |

Mechanically enforced (validator Check 2): a `gt_class: C` anchor may **never**
carry `decision_use: gate`; a `decision_use: gate` anchor must be
`deterministic` or `panel_confirmed` (α licenses gating, not the author's
say-so); a `consensus_alignment` anchor must carry a **band** and an
`[alpha_metric]`. Class-B anchors start `report` / `provisional_author` and are
promoted to `gate` / `panel_confirmed` only when a ≥3-editor panel α-licenses
their band (D-2).

Controls and `clean` members may mark whole anchors `N/A — positive control`
(FQ2/FQ3/FQ6 have no planted defect to locate). State that in §Scope.

---

## Provenance

- **Fixture slug:** / **Bucket:** S | P | R | C / **Source class:** synthetic-or-derived | public-domain
- **Matched-pair member:** clean | broken | n/a (standalone control)   ← D-1
- **Paired-with:** <sibling slug> | n/a
- **Text stored in-repo?:** yes | no (referenced — SOURCES.md entry)
- **Base text + plant record:** (derived only; REQUIRED on the `broken` member) base
  citation; the exact edits planted (loci + before→after) — the mutation registry.
  THIS SECTION IS THE ANSWER KEY'S SPINE for Lane-1 anchors. The `clean` member
  records "no mutation" and IS the control.
- **Authored / adapted by:** · **Registered (date):**
- **Ground-truth authority:** who established it; per-anchor lane recap
- **Scope:** FQs in scope (controls / clean members may mark FQ2/FQ3/FQ6 `N/A — positive control`)
- **Run configuration:** complete-manuscript mode; canonical slice pass-set {0,1,2,5,7,8,10}

## FGT1 — Structure recovery *(FQ1; Pass 0 outline + Pass 2 beat map)*
   [gt_class: B/A][construct_lane: consensus_alignment][evidence_basis: editor_panel][decision_use: report][reliability_status: provisional_author][alpha_metric: ordinal]
- **Expected scene inventory:** N scenes (near-A; agreement band: ±1 segmentation split/merge)
- **Expected act/movement boundaries:** loci + band (± one scene) — Lane-2, gates only once α-licensed

## FGT2 — Planted defect locus *(FQ2)*
   [gt_class: A][construct_lane: fault_injection][evidence_basis: planted_diff][decision_use: gate][reliability_status: deterministic]
- **Defect family:** POV | CONTINUITY | REVEAL | STRUCTURE
- **Registered loci:** exact (chapter/scene/¶); BOTH loci for two-sided defects
- **Expected engine surface:** the pass/audit family AND its id shape — e.g.
  `F-P7-*`; continuity may land as `F-P10-*` OR a continuity-bible `CF-NN`
  contradiction row (both count); reveal as `F-P8-*` OR a setup-payoff `SP-NN`
  abandoned/open row (both count). See §Continuity/reveal scoreability for how a
  severity-free CF/SP row scores FQ4.
- **Evidence-grounding rule:** refs must cite the in-text loci AND name the
  mechanism; out-of-text justification = miss (recall); bare seam-detection = miss (seam)

## FGT3 — Mechanism discrimination *(FQ3)*
   [gt_class: A][construct_lane: fault_injection][evidence_basis: planted_diff][decision_use: gate][reliability_status: deterministic][alpha_metric: nominal]
- **Expected mechanism family:** + the discriminator (why THIS mechanism, not the
  adjacent one — e.g. "a continuity contradiction, not a reveal-economy error: no
  reader-knowledge management is implicated; two stated facts simply conflict")
- **Scoring note:** human judgment over the finding's free-text `mechanism`
  string (the schema does NOT enumerate mechanisms — no mechanical backstop)

## FGT4 — Severity band *(FQ4)*
   [gt_class: A][construct_lane: fault_injection][evidence_basis: planted_diff][decision_use: gate][reliability_status: deterministic]
- **Expected severity band:** e.g. Must-Fix..Should-Fix for the plant
- **Clean-member over-fire ceiling:** max Must-Fix count the clean member tolerates
  (the matched-pair specificity calibration)
- **Severity-free plant handling:** when the plant surfaces only as a CF/SP row
  (no severity token), FQ4 scores the DELTA — the row present in `broken`, absent
  in `clean` — not a severity band. Mark this FGT4 `presence-delta` (§Continuity/reveal scoreability).

## FGT5 — Arc recovery *(FQ5; Pass 5)*
   [gt_class: B][construct_lane: consensus_alignment][evidence_basis: editor_panel][decision_use: report][reliability_status: provisional_author][alpha_metric: ordinal]
- **Gross arc shape band:** agent + shape; what counts as a hit / a miss
- Non-arc-pilot fixtures may mark `N/A — not scored`. REPORTS until ≥3-editor α licenses it (D-2)

## FGT6 — Repair target *(FQ6)*
   [gt_class: A][construct_lane: fault_injection][evidence_basis: planted_diff][decision_use: gate][reliability_status: deterministic]
- **Correct first repair target:** the mechanism (e.g. "restore or consciously cut the
  planted setup" — either direction is a hit; a line-edit of the setup sentence is a miss)
- **Dependency rule (Lane-2 when present):** e.g. locate-the-contradiction before choosing-which-fact-wins

## FGT7 — Form fairness *(FQ7)*
   [gt_class: A][construct_lane: fault_injection][evidence_basis: public_domain_control][decision_use: gate][reliability_status: deterministic]
- **Expected classification:** SOUND | INTENTIONAL-AND-EFFECTIVE | DEFECT-AS-PLANTED
- **False-positive trap:** the naive finding that must NOT fire as Must-Fix here
  (scored on the clean member for matched pairs; on the whole text for standalone controls)
- **If intentional:** the device name + what an acceptable advisory mention looks like

## Notes
Free-form: known ambiguities, recognition risk tier, seam-risk tier, scoring caveats.
