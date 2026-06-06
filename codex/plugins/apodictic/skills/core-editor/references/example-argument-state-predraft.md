# Argument State: Fund Curb-Cut Ramps Citywide (pre-draft)

<!--
Worked example of a contract-conformant PRE-DRAFT Argument_State, seeded by the Nonfiction
Pre-Draft Pathway (Increment 1 — argument spine; see pre-writing-pathway/references/nonfiction-pre-draft.md
+ docs/nonfiction-pre-draft.md). Before a draft exists, the writer plans the argument: the thesis
(C0), the claim ladder, and the opposing view it must defeat (the anti-thesis → §6 Objection 1).
The spine SEEDS this shared Argument_State.md so the Dialectical Clarity audit and the companion
modules consume one contract. The Firewall holds: the spine plans STRUCTURE, never prose or invented claims.

This file is exercised by `validate.sh --check-all` as a canonical release-gate target for
`argument-spine` (A1 schema, A2 seeds §1/§2, A3 the C0 main-claim carries the thesis; W1 the
anti-thesis names a genuine opposing view) AND Increment 2 (A4 support-plan schema, A5 each support
plan attaches to a declared subclaim, A6 the support map seeds §3; W2 no bare assertions). The
remaining draft-dependent sections (§§4–5, 7–9) are left PENDING on purpose — they are populated by
the Dialectical Clarity audit once a draft exists.
-->

<!-- apodictic:argument_spine
{"schema":"apodictic.argument_spine.v1","form":"op-ed","goal":"persuade the city council to fund curb-cut ramps citywide in the next budget","argument_type":"AT3","burden_level":"HIGH","audience_expertise":"MIXED","audience_receptivity":"HOSTILE","thesis":"the city should fund curb-cut ramps on every downtown corner within two budget cycles","subclaims":["C1: missing curb cuts are a documented, daily mobility barrier for wheelchair and stroller users","C2: the phased cost fits within the existing capital-improvement budget without new taxes","C3: piecemeal complaint-driven installation has failed to close the gap for a decade"],"anti_thesis":"limited capital dollars are better spent on road resurfacing that benefits far more residents","stakes":"residents with mobility needs are effectively excluded from downtown until the gaps close","stakes_type":"MORAL","consequence_context":"MEDIUM","key_terms":["curb cut = the ramped transition from sidewalk to street at a corner"]}
-->

## 1. Context and Classification

Form: op-ed
Goal: persuade the city council to fund curb-cut ramps citywide in the next budget
Argument type: AT3 — policy recommendation
  Burden level: HIGH
Audience:
  Expertise: MIXED
  Receptivity: HOSTILE
Distinguish classification: _pending — backfilled by Dialectical Clarity Step 9 once a draft exists_

## 2. Claim Architecture

C0 (main claim): the city should fund curb-cut ramps on every downtown corner within two budget cycles

Subclaims:
  C1: missing curb cuts are a documented, daily mobility barrier for wheelchair and stroller users
  C2: the phased cost fits within the existing capital-improvement budget without new taxes
  C3: piecemeal complaint-driven installation has failed to close the gap for a decade

Stakes: residents with mobility needs are effectively excluded from downtown until the gaps close
  Stakes type: MORAL

## 3. Support Map

The source/evidence map (Increment 2): per subclaim, the support the writer plans to bring. Each is a
`support_plan` block; a subclaim with none would be a bare assertion (validator W2). Here all three
are covered, so the spine carries no bare assertions into drafting.

- **C1** — DATA, to acquire: the city accessibility audit's count of non-compliant corners.
- **C2** — AUTHORITY, in hand: the published capital-improvement budget line items.
- **C3** — DATA, to acquire: a decade of complaint-log resolution times.

<!-- apodictic:support_plan
{"schema":"apodictic.support_plan.v1","subclaim_id":"C1","support_type":"DATA","planned_support":"the city accessibility audit's count of corners without compliant curb cuts","scheme_hint":"SIGN","status":"to-acquire"}
-->

<!-- apodictic:support_plan
{"schema":"apodictic.support_plan.v1","subclaim_id":"C2","support_type":"AUTHORITY","planned_support":"the published capital-improvement budget, showing the phased line items fit without new taxes","scheme_hint":"AUTHORITY","status":"in-hand"}
-->

<!-- apodictic:support_plan
{"schema":"apodictic.support_plan.v1","subclaim_id":"C3","support_type":"DATA","planned_support":"a decade of 311 complaint-log resolution times for curb-cut requests","scheme_hint":"CAUSAL","status":"to-acquire"}
-->

## 6. Objection and Dialectical Integrity Map

Objection 1 (the anti-thesis the argument must defeat): limited capital dollars are better spent on road resurfacing that benefits far more residents
  Engaged: _pending — to be argued in the draft_

## Pending (populated by the Dialectical Clarity audit once a draft exists)

§4 Warrant and Inference Map · §5 Burden, Scope, and Comparative Assessment ·
§7 Narrative-as-Evidence Inventory · §8 Cross-Section Tracking · §9 Diagnostic Summary.
This is a pre-draft spine + source/evidence map — these sections are intentionally not yet filled.
