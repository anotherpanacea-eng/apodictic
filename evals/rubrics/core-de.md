# Rubric: Core Developmental Edit

Use this rubric when scoring a full APODICTIC editorial letter or a complete multi-pass run.

## Metrics

Score on the 0-3 scale defined in [../../docs/eval-harness-spec.md](../../docs/eval-harness-spec.md#core-metrics):

- Contract recovery
- Root-cause accuracy
- Evidence specificity
- Counterevidence
- Severity honesty
- Absence detection
- Audit routing
- Firewall compliance
- Author usability

## Binary Checks

Per [../../docs/eval-harness-spec.md](../../docs/eval-harness-spec.md#binary-checks):

- No invented content
- Must-Fix evidence burden (≥2 references or stated confidence limit)
- Required sections present (per `plugins/apodictic/skills/core-editor/references/output-policy.md`)
- Checklist introduces no new findings
- High-risk declined/deferred audits disclosed as blind spots
- Model tag and run folder naming follow policy
- Generated host targets are not hand-edited

## Decision Rules

Use [eval-harness-spec.md §Decision Rules](../../docs/eval-harness-spec.md#decision-rules) for accept / accept-with-override / revise-and-retest / reject. Pre-register target metrics and fixture set before running A/B comparison.

## Failure Attribution

Every metric scored 0 or 1 should be logged with a likely cause class per [eval-harness-spec.md §Failure Attribution](../../docs/eval-harness-spec.md#failure-attribution).

## Fixture-Specific Overrides

Individual manifests may override this rubric's defaults (e.g., excluding audit routing for synthesis-only artifact scope). The manifest's target metrics are authoritative for its pre-registered decision rules.
