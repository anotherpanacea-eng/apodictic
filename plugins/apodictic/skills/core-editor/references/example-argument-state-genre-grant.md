# Argument State: NIH R01 — Curb-Cut Mobility Intervention (pre-draft, genre profile)

<!--
Worked example of a GENRE-PROFILED pre-draft Argument_State (Nonfiction Pre-Draft Pathway,
argument-spine Increment 5 — the genre layer; see docs/nonfiction-pre-draft.md). A grant proposal is
not just "AT3 with a unique burden": it is a near-contract with named, reviewer-scored sections
(Specific Aims / Significance / Innovation / Approach). The apodictic.genre_profile.v1 block names the
genre and declares which genre-required section ROLES the pre-draft must seed; each is seeded here as a
### sub-heading under the canonical §1–§6, so NO new top-level numbered section is added (the schema doc
stays v0.1.1). The Firewall holds: the genre layer validates the writer's DECLARED structure and
surfaces which genre-required section is missing or unseeded; it invents no aims, no significance, no
approach. The draft-time diagnosis (does the Approach actually support the Aims?) is the LLM-driven
Dialectical Clarity audit, unchanged.

Exercised by `validate.sh --check-all` as a canonical genre-layer target: B1 schema (genre / evaluator /
seeded_by enums + per-section shape), B2 every declared section is seeded (a ### heading present), B3
the genre agrees with the spine's form, B4 exactly one genre profile, W4 the genre's canonical sections
(specific-aims / significance / innovation / approach) are all declared. The §3/§4 support and warrant
maps and the remaining draft-dependent sections (§§5, 7–9) are left PENDING — they are the audit's job.
-->

<!-- apodictic:argument_spine
{"schema":"apodictic.argument_spine.v1","form":"grant-proposal","goal":"win R01 funding for a curb-cut mobility intervention and its evaluation","argument_type":"AT3","burden_level":"HIGH","audience_expertise":"EXPERT","audience_receptivity":"MIXED","thesis":"a phased curb-cut intervention with an embedded outcome study should be funded","subclaims":["C1: the mobility-access gap is documented and consequential","C2: the phased install + measurement design is feasible at the proposed scale","C3: the team has the capacity to deliver and evaluate it"],"anti_thesis":"the intervention is worthwhile but the evaluation design cannot isolate its effect, so the science is weak","stakes":"residents with mobility needs remain excluded and the field gains no transferable evidence","stakes_type":"CONSEQUENTIAL","key_terms":["specific aims = the measurable objectives the project commits to"]}
-->

<!-- apodictic:genre_profile
{"schema":"apodictic.genre_profile.v1","genre":"grant-proposal","required_sections":[{"role":"specific-aims","heading":"Specific Aims","seeded_by":"C0+ladder"},{"role":"significance","heading":"Significance","seeded_by":"stakes"},{"role":"innovation","heading":"Innovation","seeded_by":"subclaim"},{"role":"approach","heading":"Approach","seeded_by":"support_plan"}],"evaluator":"panel-reviewer","reviewer_objections":["the evaluation design cannot isolate the intervention's effect","the install timeline is optimistic given permitting"]}
-->

## 1. Context and Classification

Form: grant-proposal
Goal: win R01 funding for a curb-cut mobility intervention and its evaluation
Argument type: AT3 — propositional (fund this)
  Burden level: HIGH
Audience:
  Expertise: EXPERT (study-section reviewers)
  Receptivity: MIXED
Evaluator: panel-reviewer (scores Significance / Innovation / Approach against the rubric)

### Significance

_seeded by stakes — the mobility-access gap is documented and consequential, and closing it yields transferable evidence the field lacks._

## 2. Claim Architecture

C0 (main claim): a phased curb-cut intervention with an embedded outcome study should be funded

Subclaims:
  C1: the mobility-access gap is documented and consequential
  C2: the phased install + measurement design is feasible at the proposed scale
  C3: the team has the capacity to deliver and evaluate it

Stakes: residents with mobility needs remain excluded and the field gains no transferable evidence
  Stakes type: CONSEQUENTIAL

### Specific Aims

_seeded by C0 + the claim ladder — Aim 1 (gap), Aim 2 (phased install + measurement), Aim 3 (delivery + evaluation capacity)._

### Innovation

_seeded by subclaim — the embedded outcome study turns a routine accessibility build into a measurement design the field can reuse._

### Approach

_seeded by the support plan (§3, pending) — the phased install schedule and the outcome-measurement plan. FM-A18 (Implementation Blindspot) is the signature risk; BP5 alternatives are read as "surveyed the landscape," not "proved superiority."_

## 6. Objection and Dialectical Integrity Map

Objection 1 (the anti-thesis the argument must defeat): the intervention is worthwhile but the evaluation design cannot isolate its effect, so the science is weak
  Engaged: _pending — to be argued in the Approach + a power/identification subsection once a draft exists_

Reviewer-anticipation (the writer's pre-list; the genre layer never authors these):
  - the evaluation design cannot isolate the intervention's effect
  - the install timeline is optimistic given permitting

## Pending (populated by the Dialectical Clarity audit once a draft exists)

§3 Support Map · §4 Warrant and Inference Map · §5 Burden, Scope, and Comparative Assessment ·
§7 Narrative-as-Evidence Inventory · §8 Cross-Section Tracking · §9 Diagnostic Summary.
This is a genre-profiled pre-draft spine — these sections are not yet filled.
