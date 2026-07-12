### Argument engine — R4B vocabulary migration + optional AIF-Core export

Renames Step 9's third decision test from **Warrant-recoverability** to
**Bridge-recoverability** without changing its question, ordering, verdicts,
codes, or scoring; Dialectical Clarity advances to v2.1 while `Argument_State`
stays v0.2.0. The taxonomy crosswalk advances to v0.2.0 with a separately
drift-bound eight-row concept layer for R2 relations and R3 AGD moves; the closed
82-code layer remains unchanged and all 48 unmapped rationales are now stable
present-tense conclusions.

Adds the optional `apodictic.aif-core-export.v1` one-way adapter: deterministic,
atomic JSON with source-owned claim/support IDs, verbatim warrant `scheme_text`,
typed I/RA/CA incidence, explicit loss accounting, final-vs-pre-draft precedence,
and byte-level `--source` closure. It never invents claim-ladder, PA, alternative-
conflict, or AGD topology and never feeds external graphs back into diagnosis.
Mechanical gates certify shape and closure only; mappings remain reviewed
scholarly assertions. Source: ARG-tech, *The AIF Specification*, Definition 1.1
(AIF graph); Toulmin, *The Uses of Argument* (1958); Sinnott-Armstrong & Fogelin,
*Understanding Arguments*, 9th ed.
