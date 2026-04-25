# Fixture Manifest: TAY White Paper ("The Transition Guarantee")

## Identity

- **Fixture slug:** tay-white-paper
- **Short name:** The Transition Guarantee — DC Owes Youth Leaving Juvenile Justice (Open City Advocates)
- **Bucket:** argument-nonfiction
- **Status:** active

## Source And Permission

- **Source class:** client-or-third-party (Open City Advocates organizational work; Joshua is author but the document is OCA's, not personal)
- **Permission status:** Joshua is OCA's Research & Advocacy Director and has organizational authority to use in-progress drafts for internal diagnostic purposes. External use of outputs or fixture content requires Penelope Spain (CEO) approval.
- **Permission record (if any):** implicit via Joshua's role; document for use of outputs externally if needed.

## Content Storage

- **In-repo text?:** no
- **Storage location:**
  - **Primary draft:** `../../../OCA/TAY White Paper/TAY White Paper - Full Report Draft.md` (32,607 words; marked [WORKING DRAFT])
  - **Outline:** `../../../OCA/TAY White Paper/TAY White Paper - Outline and Plan.md` (6,096 words)
  - **Evidence assessment:** `../../../OCA/TAY White Paper/TAY White Paper - Rigorous Evidence Assessment.md`
- **What, if any, text is stored:** none in manifest. All content is under `OCA/TAY White Paper/`, local-only.
- **Quotation policy:** outputs may quote policy claims and recommendations for diagnostic purposes. External sharing of fixture text requires OCA leadership approval. Outputs referencing specific youth, clients, or unpublished OCA positions must be redacted before any external use.

## Expected Diagnosis

- **Rubric file:** `evals/rubrics/core-de.md` with argument-shaped nonfiction extensions
- **Expected-diagnosis summary or known-comparison notes:** ground truth will come from one or more coalition partners (UDC, DC Justice Lab, Washington Lawyers' Committee, Council for Court Excellence, Georgetown Thrive Center) providing independent diagnosis. Joshua is author AND domain expert AND advocate, so Joshua's own assessment cannot be the sole ground truth without contamination. Target: at least one external diagnostic read before anchoring Argument Engine decisions.
- **Artifact scope for blind review:** full-letter (argument focus)
- **Target metrics (pre-registered):**
  - Root-cause accuracy
  - Evidence specificity
  - Counterevidence
  - Severity honesty
  - Absence detection
  - Argument-specific (from model-upgrade-backlog item 18 / ROADMAP Argument Engine Benchmark Suite):
    - Claim recovery
    - Warrant/support distinction
    - Objection strength
    - Audience calibration
    - Repair order

## Release And Publication

- **Can outputs be used in public release notes?:** **No, never.** Joshua-authored material (any category) is kept out of APODICTIC publications regardless of category per the unified rule in [../eval-harness-spec.md §Fixture Provenance Policy](../eval-harness-spec.md#fixture-provenance-policy).
- **Can the fixture itself be shared with external reviewers?:** blind-review-only for APODICTIC development purposes. Coalition-partner substantive review is a separate, parallel process outside the APODICTIC eval framework. Do not route OCA coalition-partner feedback through APODICTIC's blind-review protocol — different confidentiality norms.

## Maintenance

- **Date added:** 2026-04-24
- **Last refreshed:** 2026-04-24 (document marked [WORKING DRAFT])
- **Known staleness:** low. Actively drafted. Any APODICTIC findings age as the draft matures.
- **Retirement criteria:** retire when the white paper is published or when OCA wants the fixture deprecated. Retire immediately if OCA leadership indicates discomfort with the use.

## Audit-Routing Pre-Labels

| Audit | Expected | Reason |
|---|---|---|
| Argument Red Team / Stress Test | auto-run | Policy argument under stakes; need hostile reader |
| Warrant Gap | auto-run | Core argument analysis audit |
| Audience Calibration | auto-run | Audience includes DC Council, coalition partners, and general public; calibration matters |
| Evidence Provenance | auto-run | White paper leans on policy evidence; provenance check is central |
| Testimony Overburden | recommend | Risk where policy piece cites advocacy testimony as data |
| Emotional Inflation | recommend | Risk for advocacy writing |
| Scope Creep | recommend | White papers tend to overclaim scope |
| Concession Placement | recommend | Policy argument may need stronger concession-to-opposition |

## OCA / APODICTIC Firewall Note

Per CLAUDE.md: "Strictly delineate OCA work from personal projects." Using TAY White Paper as an APODICTIC eval fixture crosses that firewall by design, because:

1. APODICTIC's Nonfiction Argument Engine needs argument-shaped nonfiction fixtures, and Joshua's best-controlled example is OCA work.
2. OCA content is stored locally; no OCA material enters the apodictic repo.
3. Findings produced by APODICTIC on OCA content are Joshua's internal editorial diagnostic, not OCA organizational output.

If Joshua later wants a cleaner firewall, a published op-ed from anotherpanacea.com or a historical OCA public-record testimony would replace this fixture. For the current review, TAY is the strongest available argument fixture.

## Notes

This fixture feeds the ROADMAP's Argument Engine Benchmark Suite (see [../../docs/model-upgrade-backlog.md](../../docs/model-upgrade-backlog.md) item 18). Strongly recommend securing at least one coalition-partner independent read before this fixture anchors any argument-routing or warrant-analysis decision in the model-capability review.
