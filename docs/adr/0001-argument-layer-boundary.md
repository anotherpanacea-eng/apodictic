# ADR 0001 — Argument-taxonomy layer boundary and the external-vocabulary crosswalk

**Status:** Accepted (R4A) · **Date:** 2026-07-11 · **Supersedes:** — · **Related:** the argument re-grounding roadmap R2–R5; GT benchmark schema v0.3.0.

## Context

APODICTIC's argument engine and the wider fleet incorporated *Understanding Arguments* (Sinnott-Armstrong & Fogelin, 9th ed.) **three times under three vocabularies** — the Dialectical Clarity code registry (46 codes + 20 FM-A patterns), the companion audits, and voiceprint's argument wing (the AGD apparatus + `argquality`) — and never cross-referenced them. A 2026-07-11 review established that before any of the roadmap's R2–R5 coherence moves can be built, the *layer boundaries* must be fixed, because the roadmap's own shorthand conflated distinct layers:

- it treated **AIF** (the Argument Interchange Format — an interchange *graph* ontology of information-nodes and inference/conflict/preference applications) as though it were a canonical *editorial* vocabulary;
- it asserted a **1:1** internal↔external mapping that is in fact **many-to-one** (the appeal-to-authority critical questions receive two codes at Q1, two at Q5, with Q3/Q4 unmapped — see `setec-scratch/apo-argument-taxonomy-coherence-audit/BOOK-FRAMEWORKS.md:55`);
- it left ownership of code-assignment ambiguous across the voiceprint→apodictic producer/consumer seam.

This ADR records the boundary decisions once, so R2/R3/R4B/R5 build on stable IDs instead of re-litigating the layering. **No taxonomy is renamed here.**

## Decisions

- **D1 — `Argument_State` is the internal Single Source of Truth.** The `Argument_State` schema (`docs/argument-state-schema.md`) and the Dialectical Clarity code registry remain the authoritative internal representation. They are not replaced, renamed, or re-based onto any external ontology.
- **D2 — AIF is an optional serialization / interchange adapter, not the vocabulary.** AIF (`I-node` / `RA-node` / `CA-node` / `PA-node`) is a downstream export target for interoperability and citeability. Mapping *to* AIF never constrains the internal codes. Building the AIF adapter itself is deferred to **R4B**.
- **D3 — External vocabularies are reference targets, crosswalked-*to*, never authorities that rename internal codes.** The reference set is: **AIF** (node ontology), **Walton** (argumentation schemes + critical questions), **S&F** (the four fallacy families + the validity/strength/soundness verdict axis + the p.333 four-way refutation taxonomy), and **Wachsmuth/GAQCorpus** (the logic/rhetoric/dialectic argument-quality dimensions voiceprint's `argquality` emits).
- **D4 — Mapping cardinality is first-class, explicit, and visible.** Every crosswalk row carries a cardinality tag from a closed enum (`exact` / `broader` / `narrower` / `related` / `unmapped`); "no mapping" is the explicit value `unmapped` with a required rationale, never a silent blank. This makes the historical "1:1" assertion *inspectable*: each mapping records an explicit cardinality (reviewable and refutable, not an unstated identity), and the validator's global **non-injectivity floor** mechanically forbids a silently all-`exact`/1:1 crosswalk. It does **not**, by itself, certify any *individual* cardinality correct (see "The firewall" below).
- **D5 — Ownership at the producer/consumer seam.** APODICTIC alone assigns internal DI/OB/WR/…/FM-A codes. voiceprint, as a producer, emits *located observations*; it does not assign APODICTIC codes. The crosswalk is APODICTIC-owned. This mirrors the existing SETEC contract seam (`sync_setec.py` / `check_setec_contract.py`) and pre-commits the ownership rule R3B will operationalize.
- **D6 — Completeness-contract scope.** The crosswalk covers the argumentation **code** layer: the **82** entries (46 Dialectical Clarity codes + 20 FM-A patterns + 8 scheme hints + 3 warrant-verdict values + 5 premise-plausibility flag types). Internal benchmark/structure scaffolding — the GT1–GT8 answer-key anchors, the `Argument_State` section numbers, the severity/blast-radius tiers — is **out of scope by design**, recorded here rather than silently omitted.
- **D7 — The verdict-axis → S&F mapping is R4A/R1-owned.** The warrant-verdict and premise-plausibility-flag rows map to the S&F premise-vs-inference refutation split established in R1 (GT7 = inference/relevance+sufficiency; GT8 = premise acceptability). That ownership is pinned so R2/R3 do not re-home it.

## The firewall — what green means, and what it does not

A passing `argument-crosswalk-check` certifies **shape**, not scholarly correctness. The `targets`, `cardinality`, `prov`, and `rationale` fields are authored assertions about external argumentation theory; no structural validator can know whether a given scheme, critical-question number, S&F family, or Wachsmuth dimension is the *right* one.

- **Mechanically enforced:** membership completeness (against the *derived* registry, not a re-typed copy), family well-typing, the cardinality enum, the `unmapped ⇔ no-targets` equivalence, a non-empty rationale on every `unmapped` row, a provenance locator on every populated target, a global non-injectivity floor (the crosswalk cannot be silently all-1:1), the closed external-ref value-spaces, and the drift-binding.
- **Not mechanically enforced — reviewed, not proven:** whether a target is the *correct* scheme/CQ/family, whether a cardinality is *accurate* rather than over-strong, whether a `prov` citation is *real*, whether an `unmapped` rationale is *sound*. These are adjudicated by the human author and the Codex PR review. **R2–R5 must treat crosswalk content as reviewed, not proven** — cite the PR's review, not "CI is green."

This boundary is deliberate: a shape-check that advertised itself as certifying content would be the rhetorical-firewall antipattern the fleet treats as a P1 defect. The provenance locator, the non-injectivity floor, and the drift-binding are what actually raise the floor, mirroring `argument_groundtruth.py`'s existing per-fault provenance requirement.

## Drift-binding — why the validator does not re-type the code list

The whole purpose of this ADR is to cure taxonomy drift, so the validator must not become a fourth silent copy of the code list. Its authoritative 82-ID set is **derived at check time**: the verdict / premise-flag / FM-A slices are imported from the live owners in `argument_groundtruth.py` (`_GT7_CLASSES`, `_GT8_ROW_FLAG_TYPES`, `_FM_A_MAX`); the 46 Dialectical Clarity codes and 8 scheme hints — which have no machine-readable owner — are parsed structurally out of `dialectical-clarity.md`. Crosswalk membership must equal that derived union, and count tripwires assert the *enumerated* 46 (naming OB5) and 20 (naming FM-A20), so the registry's own stale self-counts ("45", "nineteen") cannot be propagated.

## Rejected alternatives

- **AIF as the internal SSOT** — rejected: a graph-interchange ontology is not an editorial-diagnosis vocabulary; adopting it would flatten the apodictic-specific failure semantics.
- **Rename internal codes into Walton/S&F names** — rejected: churn plus loss of the diagnostic codes' specific meaning; this is exactly what D3 forbids.
- **A prose-only crosswalk** — rejected: not machine-checkable, so drift returns.

## Consequences

R2 (defeater/rebuttal records), R3 (the functional AGD move model + producer/consumer increment), R4B (legacy migration + the optional AIF adapter), and R5 (the ClaimLicense↔Toulmin crosswalk) build on the stable IDs and cardinality discipline established here. The crosswalk starts at v0.1.0 with the high-confidence mappings populated and the remainder explicitly `unmapped`; those `unmapped` rows are the visible R4B/R2/R3 work-list.
