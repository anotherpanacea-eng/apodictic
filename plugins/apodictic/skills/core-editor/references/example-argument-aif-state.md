# Argument State — AIF export final-audit fixture

## 2. Claim Architecture

C0 (main claim): The city should publish a heat-response plan at /Users/example/authored-path.

Subclaims:
  C1: Heat emergencies are recurring public-health events.
  C2: A published plan makes agency responsibilities inspectable.

## 3. Support Map

C1: Heat emergencies are recurring public-health events.
  Support: Five years of emergency-department records show recurring heat spikes.
  Support type: DATA
  Scheme hint: SIGN

C2: A published plan makes agency responsibilities inspectable.
  Support: The existing emergency plan already assigns named agency roles.
  Support type: AUTHORITY
  Scheme hint: AUTHORITY

## 4. Warrant and Inference Map

C1: Heat emergencies are recurring public-health events.
  Warrant: A repeated measured pattern across five years supports treating the event as recurring.
  Warrant status: EXPLICIT
  Backing: PRESENT
  Qualifier: MATCHED

C2: A published plan makes agency responsibilities inspectable.
  Warrant: Publishing named responsibilities lets residents compare promised duties with agency action.
  Warrant status: EXPLICIT
  Backing: PRESENT
  Qualifier: MATCHED

## 5. Burden, Scope, and Comparative Assessment

Claim scope: LOCAL
Evidence scope: LOCAL

## 6. Objection and Dialectical Integrity Map

Objection 1: A short record may reflect one anomalous weather cycle.
  Target: C1.warrant
  Relation: WARRANT-DEFEATER
  Basis: IMPORTED
  Engaged: Y
  Quality: SUBSTANTIVE

Objection 2: Publication alone cannot guarantee compliance.
  Target: C2
  Relation: CLAIM-CHALLENGE
  Basis: TEXT-INTERNAL
  Engaged: Y
  Quality: SUBSTANTIVE

Objection 3: A cooling-center-only strategy is cheaper.
  Target: C0
  Relation: ALTERNATIVE
  Basis: IMPORTED
  Engaged: N
