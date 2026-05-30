# Ground Truth: ppi-one-size-fits-none

## Provenance

- **Fixture slug:** ppi-one-size-fits-none
- **Bucket:** 2 policy brief / report · **Cluster:** C (criminal justice / probation) · stance: reform advocacy
- **Source class:** third-party published — **referenced (text NOT stored; copyright)**
- **Work:** Prison Policy Initiative, "One Size Fits None: How 'standard conditions' of probation set people up to fail."
- **Pinned source:** https://www.prisonpolicy.org/reports/probation_conditions.html (record retrieval date + content hash on first authoritative run).
- **Quotation policy:** paraphrase only.
- **Ground-truth authority:** Joshua A. Miller (editor), diagnosis registered 2026-05-30, before any run.
- **Scope:** GT1–GT3 authoritative. **GT4–GT7 PROVISIONAL.**

## GT1 — Main claim *(Q1)*

- **Expected C0:** "Standardized, one-size-fits-all probation conditions manufacture technical violations and drive revocation risk."
- **Acceptable paraphrase band:** any recovery of *standardized/overbroad conditions cause technical violations & revocations* is a hit. "Probation is too harsh" is a partial.

## GT2 — Failure locus *(Q2)*

- **Main structural problem (authority):** proving that **overbreadth itself** — rather than supervision culture or individual client need — drives the outcomes. The causal attribution is the contested link.
- **Primary failure layer:** WARRANT — the causal bridge from "conditions are standardized/overbroad" to "this causes the violations," with live confounders (supervision culture, client circumstances).
- **Provisional codes:** WR0 / WR2 (causal warrant with unaddressed confounders) + BP (scope). FM-A6 (Warrant Leap)-family, at **Should-Fix**.

## GT3 — Strongest real objection *(Q3)*

- **Objection zone (authority):** some **standardization may protect fairness and notice** — uniform conditions have a legitimate due-process function the critique must answer.
- **Provisional codes:** OB3 (the legitimate-function counter unengaged).

## GT4–GT7 — *(PROVISIONAL)*

- **GT4 audience:** MIXED (policy/reform) · SYMPATHETIC→MIXED · MEDIUM-HIGH.
- **GT5 red-team:** load-bearing = the confounders (supervision culture / client need) + the fairness/notice function. Decoy = disputing one jurisdiction's condition list.
- **GT6 repair order:** first target = **shore up the causal warrant** (isolate overbreadth from confounders) before expanding the catalog of bad conditions.
- **GT7 Distinguish:** SOUND — a careful report; the causal-attribution soft spot is Should-Fix. **Calibration trap (key for this fixture):** this is the *same family* of weakness as the synthetic `op-ed-warrant-leap` (a causal warrant), but here it must be called **Should-Fix in a competent report**, not Must-Fix. An engine that grades them identically has failed severity calibration.

## Notes

The deliberate calibration pair: `op-ed-warrant-leap` (synthetic, catastrophic Must-Fix causal warrant) vs. this (real, Should-Fix causal soft spot). Same structural family, opposite severity — the cleanest test in the corpus of whether the engine calibrates severity rather than just pattern-matching the code.
