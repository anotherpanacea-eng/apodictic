# Rubric: Synthesis Layer

Use this rubric when scoring a synthesis artifact only (not a full letter). The synthesis layer is APODICTIC's highest-risk quality layer and gets additional checks.

## Metrics

Score from the [core metrics](../../docs/eval-harness-spec.md#core-metrics) subset that applies to synthesis:

- Root-cause accuracy
- Evidence specificity
- Counterevidence
- Severity honesty
- Absence detection
- Firewall compliance
- Author usability

Exclude:

- Audit routing (unless the Audit Invocation Log is included in the packet)
- Contract recovery (unless the contract is included in the packet)

## Per-Root-Cause Checks

Per [eval-harness-spec.md §Synthesis-Specific Eval](../../docs/eval-harness-spec.md#synthesis-specific-eval), each root cause should satisfy:

1. Traces to named pass or audit findings.
2. Identifies the mechanism, not just the symptom.
3. Names the best case against itself.
4. Produces a revision-control decision (not a workshop prompt).
5. Produces a checklist item that follows from the diagnosis.

## Named Failure Patterns To Watch

From [eval-harness-spec.md §Failure Pattern Definitions](../../docs/eval-harness-spec.md#failure-pattern-definitions):

- **Beautiful but broken:** praise displaces mechanism.
- **Framework dump:** pass codes or resolver logic leak into main letter.
- **Checklist drift:** action list solves problems not argued in the body.
- **Smoothing:** contradictions become balanced prose instead of decision-relevant diagnosis.

## Binary Checks

Synthesis-scope subset:

- No invented content
- Must-Fix evidence burden
- Required sections for synthesis scope (per manifest)
- Checklist introduces no new findings (where applicable)
- High-risk blind spots disclosed

## Decision Rules And Failure Attribution

Same as [core-de.md](./core-de.md).
