# Argument State — AGD worked fixture

*Schema: docs/argument-state-schema.md v0.2.0 — this fixture carries only the sections the argument-agd validator consumes (§2 ladder, §6 inventory, §10.9 block).*

## 1. Context and Classification

Form: op-ed · Argument type: AT3 · Burden: MEDIUM · Audience: GENERAL, MIXED

## 2. Claim Architecture

C0 (main claim): the city should convert the municipal building to closed offices
C1: open plans destroy productivity

## 6. Objection and Dialectical Integrity Map

Objection 1: conversion costs and the move-in schedule are unaddressed
  Target: C0
  Relation: EVIDENCE-CHALLENGE
  Basis: TEXT-INTERNAL
  Engaged: N
  Dialectical integrity: FAIR
  Codes: OB3

## 10. Companion Module Annotations

### 10.9 AGD Move Audit

Span: C0 — the closing recommendation
Span: C1.warrant — the studies sentence
Move count: 2
Completion: COMPLETE

M1: ASSURING at the studies sentence
  Source anchor: "Studies have shown that workers in open plans accomplish far less" @ the studies sentence
  Cue: studies have shown
  Challenge: STRIP
  Result: COLLAPSES
  Constructed challenge: Workers in open plans accomplish far less.
  Assessment basis: no study, figure, or citation remains once the assurance is stripped; the claim rests on the assurance alone
  Candidates: WR1 (PENDING); SM4 (PENDING)

M2: ASSURING at the closing recommendation
  Source anchor: "Every serious person now accepts" @ the closing recommendation
  Cue: every serious person
  Challenge: STRIP
  Result: COLLAPSES
  Constructed challenge: Open-plan offices destroy productivity.
  Assessment basis: the consensus claim is the only offered ground; stripping it leaves an unsupported universal
  Candidates: DI0 (PENDING)

_Signed: argument-agd-audit — fixture_
