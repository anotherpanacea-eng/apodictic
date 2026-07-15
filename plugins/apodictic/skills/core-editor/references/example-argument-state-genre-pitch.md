# Argument State: Seed Pitch — AccessMap Routing (pre-draft, genre profile)

<!--
Worked example of a GENRE-PROFILED pre-draft Argument_State for a PITCH DECK (Nonfiction Pre-Draft
Pathway, argument-spine Increment 5 — the genre layer; see docs/nonfiction-pre-draft.md). A pitch deck
must run the problem → solution → traction narrative or the investor bounces. The genre profile declares
the genre-required roles (problem / solution / traction); each seeds a ### sub-heading under the
canonical §1–§6. The evaluator is an investor reading fast: compression is expected (the audit loosens on
exhaustive support, tightens on the problem→solution warrant — the WR0 between "here is a pain" and
"therefore our thing"); FM-A8 (False Precision Theater) is the signature risk (vanity-metric traction).

FIREWALL BOUNDARY (the riskiest genre): the genre layer diagnoses whether the ARGUMENT of the deck holds.
It NEVER coaches slide design, slide count, or fundraising tactics — that is the rhetoric-coaching line
the Dialectical Clarity audit already forbids. It invents no problem, no solution, no traction numbers.

Exercised by `validate.sh --check-all`: B1 schema, B2 each declared section seeded, B3 genre agrees with
the spine's form, B4 one profile, W4 all three canonical roles declared, W5 the writer's
reviewer_objections pre-list is non-empty (seeds §6; the genre layer never authors the objections).
-->

<!-- apodictic:argument_spine
{"schema":"apodictic.argument_spine.v1","form":"pitch-deck","goal":"win a seed investment for an accessibility-routing product","argument_type":"AT3","burden_level":"MEDIUM","audience_expertise":"MIXED","audience_receptivity":"MIXED","thesis":"AccessMap should be backed because accessible-routing demand is unmet and our wedge converts","subclaims":["C1: wheelchair and stroller users have no reliable accessible-routing option (the problem)","C2: our curb-level routing graph is the wedge that solves it (the solution)","C3: early pilot usage shows the wedge converts (the traction)"],"anti_thesis":"the problem is real but niche, and incumbents will fold accessible routing in before a wedge can compound","stakes":"the market window for an accessibility-native router closes if a generalist ships first","stakes_type":"PRACTICAL","key_terms":["wedge = the narrow entry that compounds into a defensible position"]}
-->

<!-- apodictic:genre_profile
{"schema":"apodictic.genre_profile.v1","genre":"pitch-deck","required_sections":[{"role":"problem","heading":"Problem","seeded_by":"stakes"},{"role":"solution","heading":"Solution","seeded_by":"C0+ladder"},{"role":"traction","heading":"Traction","seeded_by":"support_plan"}],"evaluator":"investor","reviewer_objections":[{"objection":"the problem isn't urgent enough to switch","target":"C1","relation":"CLAIM-CHALLENGE"},{"objection":"the solution doesn't follow from the problem","target":"C2.warrant","relation":"WARRANT-DEFEATER"},{"objection":"the traction is a vanity metric","target":"C3.support","relation":"EVIDENCE-CHALLENGE"}]}
-->

## 1. Context and Classification

Form: pitch-deck
Goal: win a seed investment for an accessibility-routing product
Argument type: AT3 — propositional (back this), highly compressed
  Burden level: MEDIUM
Register: asserted
Register confirmation: DEFAULT-ASSERTED
High-stakes gate: INACTIVE — NONE
Audience:
  Expertise: MIXED (investor reading fast)
  Receptivity: MIXED
Cash-out inventory:
  - NONE
Evaluator: investor (loosen on exhaustive support; tighten on the problem→solution warrant; FM-A8 is the signature risk)

### Problem

_seeded by stakes — wheelchair and stroller users have no reliable accessible-routing option; the market window closes if a generalist ships first._

## 2. Claim Architecture

C0 (main claim): AccessMap should be backed because accessible-routing demand is unmet and our wedge converts

Subclaims:
  C1: wheelchair and stroller users have no reliable accessible-routing option (the problem)
  C2: our curb-level routing graph is the wedge that solves it (the solution)
  C3: early pilot usage shows the wedge converts (the traction)

Stakes: the market window for an accessibility-native router closes if a generalist ships first
  Stakes type: PRACTICAL

### Solution

_seeded by C0 + the claim ladder — the curb-level routing graph is the wedge. The problem→solution warrant (WR0) is the load-bearing inference an investor will test: does "here is a pain" actually entail "therefore this product"?_

### Traction

_seeded by the support plan (§3, pending) — early pilot usage. FM-A8 (False Precision Theater) is the signature risk: the traction must be honest evidence, not a vanity metric dressed as a curve._

## 6. Objection and Dialectical Integrity Map

Objection 1 (the anti-thesis the argument must defeat): the problem is real but niche, and incumbents will fold accessible routing in before a wedge can compound
  Engaged: _pending — to be argued in the Solution + a defensibility subsection once a draft exists_

Reviewer-anticipation (the writer's pre-list; the genre layer never authors these):
  - the problem isn't urgent enough to switch
  - the solution doesn't follow from the problem
  - the traction is a vanity metric

## Pending (populated by the Dialectical Clarity audit once a draft exists)

§3 Support Map · §4 Warrant and Inference Map · §5 Burden, Scope, and Comparative Assessment ·
§7 Narrative-as-Evidence Inventory · §8 Cross-Section Tracking · §9 Diagnostic Summary.
This is a genre-profiled pre-draft spine — these sections are not yet filled.
