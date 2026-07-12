# Argument State — AGD worked fixture

*Schema: docs/argument-state-schema.md v0.2.0 — this fixture carries only the sections the argument-agd validator consumes (§2 ladder, §6 inventory, §10.9 block).*

## 1. Context and Classification

Form: op-ed · Argument type: AT3 · Burden: MEDIUM · Audience: GENERAL, MIXED

## 2. Claim Architecture

C0 (main claim): the district should adopt the four-day school week
C1: the pilot evidence favors the change
C2: retention alone justifies it

## 6. Objection and Dialectical Integrity Map

OBJECTION 1: fifth-day childcare shifts real costs onto families least able to absorb them
  Target: C0
  Relation: VALUE-CONFLICT
  Basis: TEXT-INTERNAL
  Engaged: N
  Dialectical integrity: FAIR
  Codes: OB3

OBJECTION 2: bus-schedule disruption
  Target: C0
  Relation: EVIDENCE-CHALLENGE
  Basis: TEXT-INTERNAL
  Engaged: Y
  Quality: COSMETIC
  Dialectical integrity: FAIR
  Codes: PASS

## 10. Companion Module Annotations

### 10.9 AGD Move Audit

Span: C0 — the adoption recommendation
Span: C1.support — the pilot-districts sentence
Span: C2.warrant — the retention sentence
Move count: 1
Completion: COMPLETE

M1: DISCOUNTING at the adoption recommendation
  Source anchor: "several of whom asked how younger children would be supervised on the fifth day" @ the adoption recommendation
  Cue: NONE
  Challenge: ENGAGEMENT
  Result: COLLAPSES-DECOY
  Assessment basis: the childcare objection is surfaced inside a subordinate clause and walked past; the piece engages bus schedules instead — a weaker decoy — while the stronger childcare objection is the displaced one
  Discounted: → Objection 2
  Displaced strongest: → Objection 1
  Candidates: OB5 (PENDING)

_Signed: argument-agd-audit — fixture_
