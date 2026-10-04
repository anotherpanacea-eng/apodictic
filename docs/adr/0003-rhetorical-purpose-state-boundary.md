# ADR 0003 — Rhetorical-purpose state boundary

**Status:** Accepted (built 2026-10-04, PR #306) · **Date:** 2026-10-04 (revised the same day after the level-setting synthesis) · **Related:** [lean build spec](../rhetorical-purpose-pluralism-spec.md), [level-setting research](../rhetorical-purpose-level-setting.md), [ADR 0001](0001-argument-layer-boundary.md), [ADR 0002](0002-approval-reconstruction-ledger-authority.md).

This records the state and applicability decisions the build spec implements. The first draft of this ADR proposed a branched `Argument_State` with persisted purpose, operation, commitment, applicability, finding, and coverage records. Both level-setting sources rejected that machinery as unnecessary; the decisions below replace it.

## Context: current obligations to amend deliberately

The [current Argument_State contract](../argument-state-schema.md) requires AT classification and a Step-9 warrant verdict in section 1, a text-extractable C0 and supporting subclaims in section 2, and claim-linked downstream work. An optional block appended to that contract cannot represent an address whose point is not a proposition.

The [register/stance spec, Architecture Decisions 2 and 4](../argument-register-stance-triage-spec.md#architecture-decisions-binding) presently requires every audit to run and every finding to be retained; register/stance changes severity at Triage, never post-lock. AD4 contains two distinct protections: intake-declared high stakes forces asserted register and blocks stance demotion document-wide; content-resolved consequential cash-outs retain asserted burden and block demotion at their own spans. Their precedence and uncertainty are not interchangeable.

[Dialectical Clarity](../../plugins/apodictic/skills/argument-audits/references/craft/dialectical-clarity.md) extracts the whole-piece C0, runs Step 9 once after the other steps and defines Must-Fix through defeat of C0's evaluability/warrant. [Nonfiction pre-draft](../../plugins/apodictic/skills/pre-writing-pathway/references/nonfiction-pre-draft.md) uses the argument-spine thesis and opposing-view/anti-thesis checks. Those obligations stay intact for the current legacy route. A solidarity operation cannot be assessed by inventing the claim needed to satisfy them.

## Decisions

### D1 — Purpose, operation, and commitment stay distinct, without new records

Writer-confirmed purpose states the undertaking; what a passage does is an operation; what it asserts, infers, attests, or demands is a commitment. Confirmation neither proves the operation succeeded nor removes a commitment. These distinctions live in the existing type (AT), span-function, and cash-out records, not in new persisted objects.

### D2 — Applicability before findings

A check that does not apply to a span produces no finding. `NOT_APPLICABLE` is never a severity and never a renamed Could-Fix. Register-spec AD2 is amended accordingly; applicable findings keep Triage and the Deficit Lock unchanged. Uncertain readings produce conditional findings or a question to the writer, never a locked defect built on an invented proposition.

### D3 — Both stakes protections stay

AD4 is unchanged. An intake-declared high-stakes gate makes every claim in the document a cash-out at asserted burden; it does not turn an address span that contains no claim into an assertion. Content-resolved consequential cash-outs keep full burden at their own spans.

### D4 — One `Argument_State`, typed C0

C0 stays mandatory and gains `C0 type: ASSERTION | ADDRESS`, default `ASSERTION`. An `ADDRESS` C0 ("the text asks [audience] to be / recognize / do [X]") requires writer-confirmed AT6 or a heard-witness AT4; CL0 still fires when neither form is statable. The warrant verdict gains one value for this case, with verdicts given per cash-out. Schema 0.4.0; existing artifacts remain valid. No branch, no fork, no fake C0, no empty verdict string, no broadened WARRANTED.

### D5 — Normative basis stays visible

Each AT6 or span-function finding names its basis: the writer's stated aim, a text-grounded promise to the reader, or a named external norm. Inferred culture, political agreement, or guessed audience reaction is never a criterion.

### D6 — Confirmation and lock continuity

Without writer confirmation the default route runs and says so. Changing purpose after the lock needs a fresh run or the existing ID-scoped override; nothing is silently erased.

### D7 — Downstream modules guard, not negotiate

A module that needs a claim ladder works on the cash-out claims of an `ADDRESS` C0 or says it does not apply. One guard paragraph per module reference; no capability-negotiation layer. ADR 0001 and ADR 0002 ownership is unchanged.

## Rejected alternatives

- Branched state with optional C0 and six linked record families (this ADR's first draft): a parallel system next to the AT mechanism that already does per-span burden.
- Optional C0 without a type (level-setting source 1): loosens a required field for every consumer and loses CL0's line between an address and a text that never commits.
- Keep every question and discount the findings: confuses applicability with severity.
- A purpose label or high stakes as a blanket switch: loses located commitments.
