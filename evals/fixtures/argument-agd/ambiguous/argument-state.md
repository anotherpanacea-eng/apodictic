# Argument State — AGD worked fixture

*Schema: docs/argument-state-schema.md v0.2.0 — this fixture carries only the sections the argument-agd validator consumes (§2 ladder, §6 inventory, §10.9 block).*

## 1. Context and Classification

Form: op-ed · Argument type: AT3 · Burden: MEDIUM · Audience: GENERAL, MIXED

## 2. Claim Architecture

C0 (main claim): the amnesty increased returns
C1: returns doubled during the amnesty month

## 6. Objection and Dialectical Integrity Map

Objection 1: the reopened entrance, not the amnesty, may explain the jump
  Target: C1
  Relation: EVIDENCE-CHALLENGE
  Basis: TEXT-INTERNAL
  Engaged: Y
  Quality: SUBSTANTIVE
  Dialectical integrity: FAIR
  Codes: PASS

## 10. Companion Module Annotations

### 10.9 AGD Move Audit

Span: C0 — the amnesty claim
Span: C1.support — the returns sentence
Move count: 1
Completion: COMPLETE

M1: GUARDING at the amnesty claim
  Source anchor: "arguably increased returns" @ the amnesty claim
  Cue: arguably
  Challenge: COMMITMENT
  Result: INDETERMINATE
  Constructed challenge: The amnesty increased returns.
  Assessment basis: the de-hedged claim is confounded by the entrance reopening the text itself surfaces; adjudicators disagree whether the guard is load-bearing or honest calibration
  Trajectory: STABLE
  Candidates: NONE

_Signed: argument-agd-audit — fixture_
