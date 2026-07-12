# Argument State — AGD worked fixture

*Schema: docs/argument-state-schema.md v0.2.0 — this fixture carries only the sections the argument-agd validator consumes (§2 ladder, §6 inventory, §10.9 block).*

## 1. Context and Classification

Form: op-ed · Argument type: AT3 · Burden: MEDIUM · Audience: GENERAL, MIXED

## 2. Claim Architecture

C0 (main claim): the city should expand the composting pilot
C1: diversion rose in the pilot districts
C2: staged expansion is affordable

## 6. Objection and Dialectical Integrity Map

Objection 1: a citywide rollout would strain the current fleet
  Target: C2
  Relation: EVIDENCE-CHALLENGE
  Basis: TEXT-INTERNAL
  Engaged: Y
  Quality: SUBSTANTIVE
  Dialectical integrity: FAIR
  Codes: PASS

## 10. Companion Module Annotations

### 10.9 AGD Move Audit

Span: C0 — the opening recommendation
Span: C1.support — the diversion-tonnage sentence
Span: C2.warrant — the staged-expansion sentence
Move count: 2
Completion: COMPLETE

M1: GUARDING at the diversion-tonnage sentence
  Source anchor: "Some households may lapse in winter" @ the diversion-tonnage sentence
  Cue: may
  Challenge: COMMITMENT
  Result: SURVIVES
  Constructed challenge: Households WILL lapse in winter.
  Assessment basis: the de-hedged claim stays falsifiable and the argument survives either way
  Trajectory: STABLE
  Candidates: NONE

M2: DISCOUNTING at the staged-expansion sentence
  Source anchor: "Although a citywide rollout would strain the current fleet" @ the staged-expansion sentence
  Cue: although
  Challenge: ENGAGEMENT
  Result: SURVIVES
  Assessment basis: the discounted objection is the strongest text-internal one and the pricing + surplus answer changes the plan
  Discounted: → Objection 1
  Candidates: NONE

_Signed: argument-agd-audit — fixture_
