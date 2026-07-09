# Ground Truth: ppi-one-size-fits-none

## Provenance

- **Fixture slug:** ppi-one-size-fits-none
- **Bucket:** 2 policy brief / report · **Cluster:** C (criminal justice / probation) · stance: reform advocacy
- **Source class:** third-party published — **referenced (text NOT stored; copyright)**
- **Work:** Prison Policy Initiative, "One Size Fits None: How 'standard conditions' of probation set people up to fail."
- **Pinned source:** https://www.prisonpolicy.org/reports/probation_conditions.html (record retrieval date + content hash on first authoritative run; analyzed-text extraction anchors (START / END / EXCLUDE) in [../SOURCES.md](../SOURCES.md)).
- **Quotation policy:** paraphrase only.
- **Ground-truth authority:** Joshua A. Miller (editor), diagnosis registered 2026-05-30, before any run.
- **Scope:** GT1–GT3 authoritative. **GT4–GT8 PROVISIONAL.**

## GT1 — Main claim *(Q1)*

- **Expected C0:** "Standardized, one-size-fits-all probation conditions manufacture technical violations and drive revocation risk."
- **Acceptable paraphrase band:** any recovery of *standardized/overbroad conditions cause technical violations & revocations* is a hit. "Probation is too harsh" is a partial.

## GT2 — Failure locus *(Q2)*

- **Main structural problem (authority):** proving that **overbreadth itself** — rather than supervision culture or individual client need — drives the outcomes. The causal attribution is the contested link.
- **Primary failure layer:** WARRANT — the causal bridge from "conditions are standardized/overbroad" to "this causes the violations," with live confounders (supervision culture, client circumstances).
- **Provisional codes:** WR0 / WR2 (causal warrant with unaddressed confounders) + BP (scope). FM-A6 (Warrant Leap)-family, at **Should-Fix**.

## GT3 — Strongest real objection *(Q3)*

- **Objection zone (authority):** some **standardization may protect fairness and notice** — uniform conditions have a legitimate due-process function the critique must answer.
- **Why this is the *strongest* (structurally prior):** it is **text-internal**, turning the report's own central warrant against it. The piece's case is that vague, individualized conditions transfer discretion to officers ("shadow policing") and produce arbitrary, disparate enforcement; standardization is the classic *cure* for exactly that arbitrariness (uniform conditions give notice and constrain officer discretion). So it attacks C0 on its own terms, where the public-safety objection only contests the proposal's costs from outside.
- **Accepted facets of this zone (either is a GT3 hit — both turn the report's own warrant against it):**
  1. **Fairness / notice:** uniform conditions give notice and predictability (the due-process cure).
  2. **Discretion-constraint contradiction:** the report condemns officer discretion ("shadow policing") yet its individualization remedy *requires* discretion; standardization is the classic constraint on it. The anti-discretion warrant vs. pro-individualization remedy is the same objection on the discretion axis.
- **Decoy (rank below):** the **public-safety / deterrence** objection (do standard conditions reduce reoffending?). Real and reasonable, and a hostile policymaker may raise it *first*, but it is the canonical, genre-generic counter to any decarceration proposal and is not text-internal. A run that names public-safety as *the* strongest objection has surfaced a plausible decoy and missed the structurally prior one: score **OB5**, not a GT3 hit.
- **Provisional codes:** OB3 (the fairness/notice–or–discretion counter unengaged); OB5 if the run substitutes the public-safety decoy.
- **Amended 2026-06-04 (ratified, post-run):** decoy and zone unchanged; the discretion facet (already implied by "constrain officer discretion") made explicit as in-zone per [../PROPOSAL-gt-sets-20260604.md](../PROPOSAL-gt-sets-20260604.md).

## GT4–GT8 — *(PROVISIONAL)*

- **GT4 audience:** MIXED (policy/reform) · SYMPATHETIC→MIXED · MEDIUM-HIGH.
- **GT5 red-team:** load-bearing = the confounders (supervision culture / client need) + the fairness/notice function. Decoy = disputing one jurisdiction's condition list.
- **GT6 repair order:** first target = **shore up the causal warrant** (isolate overbreadth from confounders) before expanding the catalog of bad conditions.
- **Expected warrant verdict:** WARRANTED — a careful report; the causal-attribution soft spot is Should-Fix. **Calibration trap (key for this fixture):** this is the *same family* of weakness as the synthetic `op-ed-warrant-leap` (a causal warrant), but here it must be called **Should-Fix in a competent report**, not Must-Fix. An engine that grades them identically has failed severity calibration.
- **Expected premise flags:** NONE_REGISTERED (provisional migration default)
- **GT8 Must not adjudicate:** whether standardized probation conditions, rather than supervision culture or individual client circumstances, are the actual cause of technical violations and revocation risk.

## Notes

The deliberate calibration pair: `op-ed-warrant-leap` (synthetic, catastrophic Must-Fix causal warrant) vs. this (real, Should-Fix causal soft spot). Same structural family, opposite severity — the cleanest test in the corpus of whether the engine calibrates severity rather than just pattern-matching the code.
