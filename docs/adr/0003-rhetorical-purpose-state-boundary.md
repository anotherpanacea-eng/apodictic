# ADR 0003 — Proposed rhetorical-purpose state boundary

**Status:** Proposed · **Date:** 2026-10-04 · **Supersedes:** nothing until separately reviewed implementation · **Related:** [rhetorical-purpose roadmap](../rhetorical-purpose-pluralism-spec.md), [ADR 0001](0001-argument-layer-boundary.md), [ADR 0002](0002-approval-reconstruction-ledger-authority.md).

This is a documentation-only architecture proposal. It changes no current route, state/schema, code, validator, severity rule or acceptance status. It is not completed P0 research, a complete build brief, or authority to activate profiles. Decisions below describe the proposed boundary; unresolved choices remain explicit.

## Context: current obligations to amend deliberately

The [current Argument_State contract](../argument-state-schema.md) requires AT classification and a Step-9 warrant verdict in section 1, a text-extractable C0 and supporting subclaims in section 2, and claim-linked downstream work. An optional purpose block cannot make a C0-free address valid under that legacy contract.

The [register/stance spec, Architecture Decisions 2 and 4](../argument-register-stance-triage-spec.md#architecture-decisions-binding) presently requires every audit to run and every finding to be retained; register/stance changes severity at Triage, never post-lock. AD4 contains two distinct protections: intake-declared high stakes forces asserted register and blocks stance demotion document-wide; content-resolved consequential cash-outs retain asserted burden and block demotion at their own spans. Their precedence and uncertainty are not interchangeable.

[Dialectical Clarity](../../plugins/apodictic/skills/argument-audits/references/craft/dialectical-clarity.md) extracts the whole-piece C0, runs Step 9 once after the other steps and defines Must-Fix through defeat of C0's evaluability/warrant. [Nonfiction pre-draft](../../plugins/apodictic/skills/pre-writing-pathway/references/nonfiction-pre-draft.md) uses the argument-spine thesis and opposing-view/anti-thesis checks. Those obligations stay intact for the current legacy route. A solidarity operation cannot be assessed by inventing the claim needed to satisfy them.

## Proposed decisions

### D1 — Separate purpose, operation and commitment

Writer-confirmed purpose states the undertaking; a located operation records what the passage appears to do; commitments record actual assertions, inferences, attestations or demands. Confirmation neither proves successful operation nor removes obligations. Several purposes/operations can overlap a span. Purpose intake retains confirmation provenance, declared audience/addressees (including multiple or newly constituted publics), situation, institutional constraints, stakes, active profile version and declared normative assumptions.

Maintain an anchored inventory across the complete run scope. Factual, historical, causal, quantified, representative and consequential prescriptive commitments retain applicable evidence, inference, scope, comparison and execution scrutiny. Distinguish literal assertion from quotation, metaphor, irony and enacted speech before assigning those commitments; do not invent a proposition to criticize it.

### D2 — Applicability before findings and severity

For each relevant span/family, record applicability, rationale, responsible reviewer/run, provenance and uncertainty before creating a finding or assigning severity. `NOT_APPLICABLE` is an applicability decision, never a fourth severity or renamed Could-Fix. An uncertain reading cannot erase a commitment or license an unconditional locked defect; retain alternatives and conditional diagnoses until clarified.

Propose amending AD2 to require complete, disclosed applicability coverage rather than manufactured findings from inapplicable questions. Applicable findings still enter the existing ledger and Triage/lock discipline. Missing examination or uncertain classification is unknown, never a clean pass. Final coverage rules and omission detection belong to the build brief and independent semantic evaluation.

### D3 — Keep both stakes protections, scope the proposed amendment

For future purpose-native work, intake-declared stakes must remain recorded and must retain institutional/evidential requirements on actual testimony and other commitments. High stakes alone must not turn solidarity, recognition or ambiguous metaphor into a literal whole-document claim-support undertaking. This requires an explicitly reviewed amendment to AD4's document-wide forced-asserted rule; this ADR does not switch it off.

Separately preserve the local cash-out protection: consequential assertions and prescriptions retain full applicable burden at their located spans, including applicable demotion safeguards. A purpose label cannot hide a policy decision. The build brief must define how the two mechanisms compose, which records carry the joins and what uncertainty/coverage means, with controls for both document-wide intake and local content. Do not weaken current AD4 while that remains unresolved.

### D4 — One APODICTIC-owned, versioned Argument_State

Propose a new version of the same shared state with distinct legacy-argument and purpose-native branches. Preserve the existing AT/C0/subclaim/warrant requirements and stable claim-support IDs for the legacy branch. The purpose-native branch permits absent or explicitly inapplicable whole-piece claim fields; actual reconstructed reasoning retains anchored claim units, support, objections and scoped warrant verdicts where applicable.

No fake C0, empty warrant string, invented inference edge, automatic PASS or broadened WARRANTED can bridge incompatibility. Concrete version identifier, discriminant, field names, validation rules and migration are intentionally not chosen here; they require the separately reviewed build brief. Do not fork a second rhetorical state or present proposed records as valid current artifacts.

Minimum information categories must remain linked and inspectable; this is not a field/schema declaration:

| Category | Information to retain |
|---|---|
| Purpose context | Stable identity, confirmed purposes/provenance, addressees/situation/constraints/stakes, profile version and normative assumptions |
| Passage operation | Stable identity, source anchors, purpose links, description, alternative readings and uncertainty |
| Actual commitment | Stable identity, source anchors, kind/force, operation links, existing claim/cash-out links where present and uncertainty |
| Applicability | Span/operation and family, decision/rationale, triggering commitments, responsible reviewer/run and provenance |
| Purpose finding | Stable identity, anchors, operation/profile/criterion links, normative basis, mechanism, severity, counter-reading and repair class under reviewed policy |
| Assessment coverage | Examined spans/families, sampled or missing context, pending interpretations, local conclusions and their scope |

ADR 0001 remains controlling: APODICTIC owns internal taxonomy and assignments; external vocabularies and AIF are loss-aware downstream crosswalk/export targets, not diagnostic authorities. ADR 0002's approval ledger remains sole approval authority; purpose records do not create a parallel approval source or authorize hand-edited projections.

### D5 — Visible normative basis and separate achievements

Every proposed purpose finding names its basis: writer-stated aim, text-grounded reader promise or named external norm. Naming a norm does not establish its legitimacy or applicability. Optional/requested external-frame criticism is reported separately from immanent defects; political agreement, inferred culture/authenticity or conjectured uptake is not an unstated criterion.

Report purpose achievement, local commitment integrity, coverage and uncertainty separately. Existing warrant vocabulary applies only to actual reconstructed reasoning in its source scope, not a global rhetorical score or whole-address achievement verdict. Empirical truth adjudication and actual reception remain outside this proposal's evidence.

Purpose-native severity needs a reviewed extension tied to evidenced failure of a confirmed undertaking or reader promise, with positive controls, counter-readings and explicit normative bases. Norm disagreement or guessed audience reaction alone cannot license Must-Fix. Retain the three severity tokens and lock; do not borrow a fictional C0 to justify escalation.

### D6 — Confirmation, refusal and lock continuity

Without writer confirmation, retain the current default route and disclose its limitations; alternative readings remain provisional. A confirmed but unknown/unreviewed profile is still unsupported and cannot activate exclusions. Preserve writer artifacts and ordinary legacy workflows; disclose when a requested purpose-aware assessment is unavailable.

Changing purpose after lock requires a fresh run or the existing explicit ID-scoped override pathway. Preserve the original run/finding IDs, reasons and required history; no silent erasure, severity reduction or new override authority. A new run does not rewrite the old run.

### D7 — Negotiate consumers before touching new state

Reconstruction, `/adjudicate`, readiness, coaching, pre-draft, red-team, evidence and AIF export must each negotiate supported capability/version before consuming or projecting purpose-native state. Each needs either a safe reviewed adapter or visible refusal of unsupported operations while preserving the source artifact. Completing all adapters is later work; implementing refusal before any unsupported downstream use is a prerequisite to the bounded release.

Adapters may consume an evidenced, unaffected claim-support subset only under a reviewed contract with stable IDs and declared losses. No claim ladder or AIF edge by guess, silent operation loss or unknown-as-pass. Pre-draft cannot require a thesis/antithesis for a C0-free purpose undertaking merely to satisfy the old spine; its scoped replacement/refusal remains a reviewed adapter task. Existing legacy consumers remain unchanged.

## Rejected alternatives

- Append purpose metadata while retaining mandatory C0 everywhere: cannot represent the intended work without fabrication.
- Keep every question and discount every resulting finding: confuses applicability with severity and permits category errors.
- Treat declared purpose or high stakes as a universal assertion/exemption switch: loses located commitments or misclassifies operations.
- Fork rhetorical state, approval authority or taxonomy: violates ADR 0001/0002 ownership and multiplies inconsistent representations.
- Silently project unsupported operations or issue a global rhetorical pass: hides loss, uncertainty and unsupported capability.

## Dependencies and disposition

| Surface | Proposed boundary here | Current disposition / remaining work |
|---|---|---|
| Purpose/operation/commitment and applicability | Located, confirmed, explicit, uncertainty retained | Architecture proposed; research, normative assumptions and coverage/build contracts unresolved |
| Register AD2 and both AD4 mechanisms | Applicability distinct from severity; no blanket commitment exemption | Current runtime preserved; amendments and document/span regression evidence required |
| Argument_State | One versioned owner with distinct branches | Current schema unchanged; concrete fields/version/migration/validation build brief required |
| DC verdict and severity | Scoped reasoning verdict; evidenced undertaking failure without invented C0 | Current rules preserved; kernel/Step-9 and purpose-native severity contracts/review required |
| All downstream consumers | Reviewed support or explicit refusal before use | Current legacy behavior preserved; negotiation/refusal release prerequisite, adapters separately reviewed |
| Research/evaluation | Independent source-grounded readings and contested-case review | [Draft #300](https://github.com/anotherpanacea-eng/apodictic/pull/300) is candidate construction; [draft #301](https://github.com/anotherpanacea-eng/apodictic/pull/301) is selected-source research; neither licenses profiles or completes P0 |
| Approval/taxonomy ownership | ADR 0001 and ADR 0002 unchanged | No new approval facts, ledger mutation, external code assignment or inferred export edges |

A future build brief must freeze operational rubric and decision thresholds before runs, define coverage and purpose-native severity, and retain independent editorial/human adjudication for contested anchors. Mechanical conformance cannot certify rhetorical readings or audience response. No adoption, schema migration, profile activation or runtime status promotion follows from this proposed ADR.
