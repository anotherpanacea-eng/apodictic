# Rhetorical Purpose & Plural Standards — Roadmap Spec

**Status:** Proposed (unbuilt) — documentation only; increments require separate reviewed build briefs.
**Date:** 2026-10-01
**Origin:** Owner-requested response to an external critique of APODICTIC's claim-and-support model; developed with Astra.
**Depends on:** Dialectical Clarity v2.1; Argument Register & Rhetorical Stance Triage; Argument_State; output-policy severity honesty and Deficit Lock; ADR 0001's taxonomy ownership and loss-aware export boundaries.
<!-- built-when: plugins/apodictic/skills/argument-audits/references/craft/rhetorical-purpose.md -->

## Problem and intended result

APODICTIC usefully tests claims, warrants, evidence, scope, and objections. Its
current argument engine also accommodates testimony, implicit narrative claims,
recursive forms, and writer-confirmed generative lenses. Nevertheless, its shared
representation and final warrant question treat evaluable claim-and-support as
the organizing standard. The generative-register spec explicitly retains every
audit and calibrates severity. Some rhetorical work needs different questions,
not a discount on findings produced by an inapplicable question.

A solidarity address may constitute a collective subject rather than defend a
policy choice; witness may ask for recognition rather than generalize; genealogy
may unsettle the categories through which a dispute is adjudicated. Calling these
failures because they lack a thesis ladder or strongest-opponent rebuttal repeats
the category error APODICTIC already rejects when story diagnostics are imposed
on arguments.

The proposed result is a purpose-aware diagnostic layer. A writer sees which
standards the editor is applying and why. Different passages can perform different
rhetorical work. Concrete assertions and inferences retain their local evidential
and inferential obligations wherever they occur. The tool reports several
dimensions of achievement and weakness without declaring an entire address
universally warranted or unwarranted.

This spec does not establish that claim-and-support is intrinsically liberal,
that alternatives are politically superior, or that any tradition is fully
represented by a software profile. APODICTIC's existing Perelman/Olbrechts-Tyteca
and Fricker grounding must be acknowledged rather than rediscovered as absent.

## Scope and non-goals

Specify purpose intake, passage applicability, local commitment safeguards,
purpose-specific diagnostic profiles, shared-state compatibility, reporting,
evaluation, and a phased delivery order. This change writes the spec and roadmap;
it does not change runtime routing, findings, schemas, validators, registry,
benchmark keys, or published samples.

Do not add AT6–AT11, silently label writers by philosophical school, optimize
propaganda, infer political correctness, prescribe universal civility or inclusion,
predict actual audience uptake, or generate prose. Empirical truth adjudication
remains outside the diagnostic Firewall. Research verification remains a distinct
source-grounded capability. New profiles are hypotheses requiring level-setting
and editorial validation, not established assessments merely because they parse.

## Architecture decisions

1. **Purpose, operation, and commitment are distinct.** Purpose is what the writer
   intends the address to accomplish; operation is what a located passage appears
   to do; commitment is what it actually asserts, infers, attests, or demands.
   Intended purpose does not prove achieved operation or erase commitments.
2. **Several purposes may coexist.** One address can bear witness, form a public,
   and advocate a decision. A document-level label cannot exempt its passages.
3. **Selection is writer-confirmed.** Offer plain-language choices (help readers
   decide; make a conflict visible; build a shared identity; bear witness; question
   inherited categories; explore a lens; other), not an obligatory theory quiz.
   The editor may propose a profile with textual evidence but must not silently
   switch the run. Without confirmation, retain the existing default route and
   disclose its limitations; do not present it as a purpose-aware assessment.
   Mark alternative readings as provisional, without applying exemptions.
4. **Applicability precedes finding creation and severity assignment.** Determine
   whether a diagnostic question applies to a span before emitting a defect.
   `NOT_APPLICABLE` belongs to an applicability record, not the severity enum or
   a renamed Could-Fix. Applicable findings still use Must-Fix / Should-Fix /
   Could-Fix and the existing Deficit Lock. A change of purpose after locking
   requires a new run or the existing explicit override pathway; no silent erasure.
5. **Commitments are checked throughout.** Factual, historical, causal,
   representative, quantified, and prescriptive commitments activate appropriate
   existing checks even within witness, satire, genealogy, or identification.
   Purpose-specific interpretation must first distinguish literal assertion from
   quotation, metaphor, irony, and enacted speech. Record uncertain interpretations;
   do not invent an asserted proposition in order to find a defect.
6. **Dissent has several legitimate relations to an address.** Distinguish
   representing an opponent accurately, rebutting an objection, comparing feasible
   alternatives, refusing a frame, and sustaining disagreement. Absence of rebuttal
   is not misrepresentation. Steelmanning is conditional on the argumentative task;
   accuracy obligations attach when opponents are represented.
7. **Normative assumptions are visible.** Every profile declares its positive
   success criteria, obligations, exclusions, and contested assumptions. Writer
   commitments and documented rhetorical context ground the diagnosis; importing
   a reviewer's preference for consensus, moderation, universality, or inclusion
   is not an unannounced default. Every finding identifies its normative basis:
   writer-stated aim, text-grounded reader promise, or named external norm. An
   external-frame critique is optional/requested and reported separately from
   immanent defects; confirmation selects a task, not proof of its achievement.
   Do not infer culture, authenticity, politics, or bad faith from a profile name.
   Existing reporting and safety boundaries remain.
8. **Report purpose achievement and local integrity separately.** No scalar
   rhetorical score and no document-wide warranted verdict for multi-purpose work.
   Existing warrant vocabulary remains scoped to actual reconstructed reasoning.
   Unknown or unassessed is never rendered as pass.

## Proposed profiles and distinguish rules

Profiles are overlapping editorial lenses; the theory names below guide research,
not writer classification. Each build needs positive examples, counterexamples,
named flags, applicability conditions, and false-positive guards before runtime
activation. Do not present these candidate dimensions as canonical code families.

| Profile / lineage | Positive diagnostic questions | Candidate failure and false-positive guard |
|---|---|---|
| Deliberative / justificatory | Can readers inspect reasons for the conclusion, scope, and relevant alternatives? | Preserve existing DC checks on applicable reasoning; do not equate every call to action with a comparative policy proposal. |
| Agonistic | What conflict, adversaries, stakes, and boundaries become legible? Does the text sustain the contest it undertakes? | Flag concealed incompatibility or treatment that contradicts avowed terms of contest; no requirement of consensus, politeness, equal concessions, or treating every adversary as legitimate. |
| Constitutive | What public or "we" is addressed or brought into being? What roles and terms of belonging does the text enact? | Track shifts between avowed and operative membership; exclusion is an object of analysis, not automatically a defect under a universal inclusion rule. Actual formation of a public is unverified without reception evidence. |
| Identification / Burkean | How do identification and division, shared substance, metaphor, motive, and scapegoating organize the address? | Show where identification substitutes for an inference the text also claims to prove; neither emotional force nor identification alone is a fallacy. Describe mechanisms without assuming successful persuasion. |
| Genealogical / critical | How does the account expose the emergence, contingency, authority, and discontinuities of its categories? | Historical/causal assertions need support; deriving invalidity solely from an origin requires a local inferential check. An open problem or refusal of a replacement policy is not inherently a missing conclusion. |
| Witness / testimonial | What can the speaker attest to, from which position, with what limits and addressee? What recognition is sought? | Preserve local knowledge and uncertainty; test actual representative leaps, not an invented requirement to generalize, defend against denial, or speak for a population. |
| Exploratory / generative | What inquiry moves, distinctions, productive transformations, or new connections does the text make available? | Build on AT5 coherence/fertility checks; no compulsory final thesis or antithesis. Actual claims and prescriptions retain their burdens wherever they occur. |

The level-setting phase must consult traditions on their own terms. Initial
reading leads include Mouffe on agonism, Charland on constitutive rhetoric, Burke
on identification and division, Foucault on genealogy, and existing testimonial
and generative references. These are research leads, not a completed literature
review or authority for the exact software obligations proposed here. Seek
counterexamples and limitations as well as supporting passages; culturally
specific forms must not be flattened into a universal Western taxonomy.

## Intake and diagnostic procedure

1. Record intended work, audience/addressees, situation, institutional constraints,
   stakes, and confirmed purposes. Audience is potentially constituted or multiple,
   not always a pre-existing sympathetic/mixed/hostile recipient.
2. Map passage operations with manuscript anchors and uncertainty. Use overlapping
   spans where needed; a single passage may both enact solidarity and assert a fact.
3. Inventory actual commitments over the complete run scope. Cross-link assertions,
   prescriptions, and consequential reasoning to operations and existing claim,
   warrant, evidence, cash-out, and objection records where present. Do not require
   every operation to have a C0, a warrant, or an opponent to defeat.
4. Record applicability and rationale for each relevant diagnostic family and span.
   A pending/uncertain classification cannot silently remove an obligation. Present
   competing conditional diagnoses when clarification would change the finding.
   A disputed literal reading alone cannot license an unconditional locked defect.
5. Evaluate positive purpose-specific work and applicable local integrity checks.
   Classify findings and severity at Triage, preserving the Firewall and lock.
6. Synthesize a purpose-specific editorial letter: confirmed aims and frames;
   achieved work with anchored evidence; applicable failures; open interpretations;
   local commitment issues; and classes of repair. Never supply replacement prose,
   new identities, opponents, political positions, or evidence. For a proposed
   repair, name what valuable work it could destroy (situated voice, productive
   ambiguity, antagonism, identification) when that tradeoff is evidenced. A
   transition map may show where the address changes its undertaking.

**Example.** "We refuse to be treated as disposable" can enact solidarity and a
boundary; no comparative-policy defect follows from that sentence alone. If the
same address says "Program X will reduce deaths by 40%," that prediction receives
the usual support, inference, and precision scrutiny. If it prescribes adopting
X as a consequential institutional decision, assess the comparative and execution
burdens appropriate to that decision. A call to mourn, assemble, or recognize a
witness does not automatically become an uncompared policy brief.

## State, reporting, and compatibility contract

Keep `Argument_State.md` the single shared source of truth under ADR 0001. Propose
a versioned, optional purpose layer owned by APODICTIC; finalize field names and
placement in the first build brief. Do not fork an independently maintained
rhetorical state or rename existing codes.

| Record | Minimum information |
|---|---|
| Purpose context | Stable ID; declared purpose(s); confirmation/provenance; audience and situation; active profile version; normative assumptions. |
| Passage operation | Stable ID; source anchor(s); purpose references; operation description; alternative readings and uncertainty. |
| Commitment | Stable ID; source anchor(s); commitment kind and force; operation links; existing claim/cash-out links when applicable; uncertainty. |
| Applicability | Span/operation; diagnostic family; APPLICABLE / NOT_APPLICABLE / UNCERTAIN; rationale; triggered commitment references; responsible reviewer/run. |
| Purpose finding | Stable finding ID; anchors; operation/profile/criterion references; normative basis; mechanism, severity, counter-reading, and repair class under existing finding policy. |
| Assessment coverage | Examined spans and families; sampled or missing context; pending interpretations; local conclusions and their scope. |

These are proposed minimum records, not new shipped schemas. Mechanical checks
can prove references, enum membership, versions, and consistency of declared
applicability; they cannot prove a rhetorical reading or detect every omitted
commitment. Semantic coverage requires independent editorial review.

The current schema requires AT classification, a C0 with supporting subclaims,
and a warrant verdict. A text with no such reasoning cannot be made compatible
simply by appending an optional block. P0 must specify a new state version whose
purpose-native branch permits those fields to be absent or explicitly inapplicable
and scopes actual claim units and their warrant verdicts to their source spans;
the legacy argument branch preserves its existing requirements. Never use a fake
C0, empty-string warrant verdict, or unsupported broadening of WARRANTED.

Legacy artifacts remain valid without purpose records and take the existing route.
New artifacts must negotiate explicit capability/version support. Consumers that
require C0 or assume every finding is claim-linked must refuse unsupported purpose
operations explicitly, rather than invent a claim ladder or treat them as passing.
Preserve unaffected claim-support projections and their stable IDs. Reconstruction,
`/adjudicate`, readiness, coaching, red-team, evidence, and AIF export each need
reviewed adapters: some can consume the claim-support subset; loss-aware exports
must list unmapped rhetorical operations. No invented AIF inference edges.

**Required reviewed amendments before runtime release:** the register spec's AD2
(every audit runs/every finding retained) must distinguish applicability decisions
from severity calibration. Its AD4 document-wide high-stakes asserted gate must
be reconciled with situated witness/constitutive operations: high stakes must not
reduce evidence scrutiny, but neither establishes that every passage is a literal
assertion. Preserve current runtime rules until this amendment and its regression
evidence are reviewed. DC's all-argument kernel language, Step-9 whole-piece verdict,
and pre-draft's mandatory antithesis also need explicitly scoped replacements.
Existing Must-Fix criteria depend on defeat of C0. Purpose-native severity must
instead be defined against an evidenced failure of the confirmed undertaking or
reader promise, with profile-specific positive controls and counter-readings.
Normative disagreement or conjecture about audience reaction alone cannot license
Must-Fix. Define this extension before emitting purpose-native findings; retain
the three severity tokens and lock discipline, not a fictional C0.

## Evaluation and acceptance criteria

Do not score new profiles by agreement with the existing claim-ladder answer key.
Retain existing DC controls for local integrity; add purpose-specific controls.
Use synthetic, public-domain, or permissioned material with declared provenance.
Freeze prompts, source spans, expected distinctions, and scoring before runs.

Minimum first-increment behavioral battery:

- A competent solidarity address without a policy proposal: no automatic missing
  thesis, strongest-objection, or uncompared-policy defect; an anchored account of
  its enacted membership and boundary must still be provided.
- A clean witness account and its matched representative-overreach variant: protect
  situated testimony, detect the introduced generalization, and require no rebuttal
  of denial simply to recognize the witness's purpose.
- A mixed-purpose address with an unsupported quantified causal prediction inside
  a constitutive span: detect the same local failure as in an asserted control.
- An actual consequential policy proposal relabeled "manifesto": preserve its
  applicable evidence, comparison, and execution burdens.
- An opponent represented inaccurately, paired with mere refusal to rebut: distinguish
  misrepresentation from absence of engagement.
- A purpose switch after lock: preserve the locked record and require the existing
  override or a fresh run; never silently delete a finding.
- An unconfirmed profile proposal, ambiguous metaphor, legacy state, and unsupported
  consumer: respectively retain the default route, disclose uncertainty, preserve
  compatibility, and refuse unsupported projection without fabricating C0.
- A high-stakes witness address: preserve institutional evidential obligations on
  actual testimony while avoiding a requirement that solidarity or recognition
  passages adopt whole-document claim-support form. Unknown profiles must remain
  provisional and cannot activate unreviewed exclusions.

Later profiles add clean/broken pairs for historical fabrication, origin-to-invalidity
inference, identification presented as empirical proof, avowed/operative membership
shifts, and productive vs. inert exploration. Test ideological substitutions and
different addressees: changed purpose/context may change applicability, changed
political agreement alone must not. Preserve identical commitment scrutiny when
only a purpose label changes.

For each fixture preregister expected applicability, purpose-native defects,
retained commitment obligations, and prohibited outputs. Invented thesis/antithesis,
compulsory rebuttal of denial for balance, a commitment defect excused by purpose,
unconfirmed activation, and a legacy WARRANTED verdict for non-argumentative
achievement are release-blocking outcomes. Do not use raw flag counts as success.

Two independent blind readers assess source-grounding, purpose fit, local-integrity
coverage, false positives, repair usefulness, and declared assumptions. Model-only
agreement remains provisional; contested anchors use the existing reliability
ladder and a relevant human-editor panel before gating. Freeze operational rubric
and thresholds in the build brief before collecting results. Report mechanical
conformance, editorial judgments, audience-response evidence, and provenance
separately; none substitutes for the others.
Compare revision directions with the current engine on the same texts: purpose-
native guidance should improve usefulness without losing commitment scrutiny.
Disagreements are adjudicated and unresolved cases remain uncertain, not passes.

## Delivery increments and file map

**P0 — Level-setting and reviewed contract.** Research profiles and counterexamples;
write an ADR amending the existing runtime assumptions identified above; fix the
intake, applicability, record ownership, compatibility, and evaluation contract.
This roadmap spec is its starting brief, not a completed research deliverable.

**P1 — Bounded vertical slice.** Implement confirmed-purpose routing, passage
operations/commitments/applicability, and constitutive + witness profiles alongside
the existing deliberative baseline. Ship the first-increment behavioral battery,
independent reviews, and reporting. Do not claim support for all seven profiles.
Before any downstream mode touches new state, it must either have a safe reviewed
adapter or visibly decline the unsupported capability/version while preserving
the writer's artifacts. This negotiation/refusal gate ships in P1; completing
the adapters is P3 work. Retain ordinary legacy workflows on legacy artifacts.

**P2 — Profile expansion.** Add agonistic, identification, and genealogical profiles
only after their own research, distinguish rules, and clean/broken controls. Bring
existing exploratory AT5 into the shared purpose layer without weakening cash-out
checks. Each profile can remain research-only when agreement or usefulness fails.

**P3 — Workflow and evidence.** Complete coaching, pre-draft, red-team, evidence,
reconstruction/adjudication/readiness, and export adaptations; validate usefulness
with writers/editors and permissioned real work; revise public positioning and
samples to disclose supported profiles and the remaining evidence limits.

Likely build surfaces (not edited by this spec): `docs/argument-state-schema.md`;
the register/stance spec and a new ADR; nonfiction intake/router and engine;
`dialectical-clarity.md` and a new `rhetorical-purpose.md` reference; output policy
and synthesis; optional finding/state schemas and one owner-derived validator;
companion/coaching/pre-draft/export adapters; independent eval fixtures and rubric.
The planned new reference belongs under
`plugins/apodictic/skills/argument-audits/references/craft/`, following the audit
family split now on main; `specialized-audits` is the dispatcher, not its owner.
Registry/derived UI changes follow normal generation and consumer compatibility
review. SETEC remains an optional producer of declared observations, not the
authority for assigning rhetorical-purpose findings.

## Adjacent research candidates

Astra's suggestions are recorded as later research, not obligations of P1:

- **Stasis and frame audit:** distinguish disputes over facts, definitions, values,
  jurisdiction, and which questions may be asked; refusal of a frame can itself
  be substantive work.
- **Burden-allocation audit:** inspect who is asked to establish what, who can
  contest the premises, and whether institutional credibility standards distort
  the exchange. Do not assume the present tribunal is neutral.
- **Rhetorical ecology:** distinguish addressed, overhearing, institutional, future,
  and newly constituted publics; intended uptake, textual affordance, and observed
  response remain different evidence categories.
- **Multi-frame review:** provide alternative explicitly labeled diagnoses when
  traditions disagree about success, rather than average them into one verdict.

## Review record

Initial Astra consultation shaped the separation of purpose/operation/commitment,
local safeguards throughout the text, non-universal profile assumptions, and the
explicit compatibility amendments. Astra independently reviewed the spec, roadmap,
and changelog on 2026-10-01: initial NEEDS REWORK (five P2s, no P1), followed by
APPROVE after a focused reread of the repairs. Disposition:

| Finding | Resolution |
|---|---|
| Optional records cannot relax legacy C0/verdict requirements | Require a new state version with purpose-native applicability and span-local claim units; retain legacy invariants. |
| Existing Must-Fix depends on C0 defeat | Require reviewed purpose-specific severity tied to evidenced undertaking/reader-promise failure; exclude conjectural uptake and contested external norms from automatic Must-Fix. |
| Adapter completion deferred beyond new-state release | P1 requires safe adaptation or visible capability refusal before any downstream mode touches new state; preserve artifacts. |
| High-stakes witness missing from the initial battery | Add institutional witness with stringent local obligations and no compulsory whole-piece claim ladder or denial rebuttal. |
| Profile assumptions lack finding-level provenance | Record writer aim, text-grounded promise, or named external norm; separate optional external critique from immanent defects. |

The final editorial nit removed a count-shaped description of the required
amendments. Approval covers the planning document, not future builds, research
completion, or validated rhetorical judgments. Repository combined validation,
changelog-fragment validation, status-drift check, and diff whitespace check pass.
