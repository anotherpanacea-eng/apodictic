# Argument State — AGD worked fixture

*Schema: docs/argument-state-schema.md v0.2.0 — this fixture carries only the sections the argument-agd validator consumes (§2 ladder, §6 inventory, §10.9 block).*

## 1. Context and Classification

Form: op-ed · Argument type: AT3 · Burden: MEDIUM · Audience: GENERAL, MIXED

## 2. Claim Architecture

C0 (main claim): lawn-watering restrictions should continue through September
C1: storage is at a twenty-year low
C2: lifting restrictions raises usage

## 6. Objection and Dialectical Integrity Map

Objection 1: restrictions burden landscaping businesses
  Target: C0
  Relation: VALUE-CONFLICT
  Basis: IMPORTED
  Engaged: N
  Dialectical integrity: FAIR
  Codes: PASS

## 10. Companion Module Annotations

### 10.9 AGD Move Audit

Span: C0 — the restrictions sentence
Span: C1.support — the gauge-report clause
Span: C2.support — the neighboring-towns clause
Move count: 2
Completion: COMPLETE

M1: ASSURING at the gauge-report clause
  Source anchor: "Of course, the reservoir is at a twenty-year low" @ the gauge-report clause
  Cue: of course
  Challenge: STRIP
  Result: SURVIVES
  Constructed challenge: The reservoir is at a twenty-year low.
  Assessment basis: the April gauge report independently carries the claim after the strip
  Candidates: NONE

M2: ASSURING at the restrictions sentence
  Source anchor: "Clearly the lawn-watering restrictions should continue" @ the restrictions sentence
  Cue: clearly
  Challenge: STRIP
  Result: SURVIVES
  Constructed challenge: The lawn-watering restrictions should continue through September.
  Assessment basis: the model projection and the neighboring-town comparison carry the recommendation without the intensifier
  Candidates: NONE

_Signed: argument-agd-audit — fixture_
