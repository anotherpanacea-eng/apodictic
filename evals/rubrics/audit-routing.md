# Rubric: Audit Routing

Use this rubric when testing whether APODICTIC recommends, runs, or skips the right audits for a given fixture.

## Inputs Required

- Fixture intake and contract
- Pass artifacts that trigger audit routing
- Audit Invocation Log (required — without this, audit-routing cannot be scored)
- Synthesis blind-spot section or equivalent

## Metrics

Score the 0-3 audit-routing dimension from [eval-harness-spec.md](../../docs/eval-harness-spec.md#core-metrics):

- Audit routing: misses key audits / over-recommends / mostly appropriate / sparse, prioritized, blind spots named

Secondary:

- Severity honesty (for blind-spot disclosure)
- Firewall compliance (for decline/defer language)

## Pre-Labeled Audit Expectations

Each fixture manifest should include an audit-routing table listing expected behavior per audit. See [eval-harness-spec.md §Audit-Routing Eval](../../docs/eval-harness-spec.md#audit-routing-eval).

Score routing separately from audit quality:

- A correct recommendation can still produce a weak audit.
- A strong audit can still have been over-triggered.

## Binary Checks

- Declined/deferred high-risk audits disclosed as blind spots in final output
- Audit Invocation Log is complete (every triggered audit has a decision recorded)
- No synthesis began while a required auto-run audit was missing

## Decision Rules

Same as [core-de.md](./core-de.md). Note that over-routing is a specific failure mode worth distinguishing from missed routing — the decision rules should reflect which direction the change under review tends to push.
