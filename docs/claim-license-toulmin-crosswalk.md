# ClaimLicense ↔ Toulmin crosswalk

**Status:** Built (R5 docs-only crosswalk) · **Snapshot:** setec-voiceprint v1.124.0

## Purpose and boundary

This document corrects the source-audit's shorthand recommendation
`warrant ≡ claim_license` (`setec-scratch/apo-argument-taxonomy-coherence-audit/FINDINGS.md`
§D, “The warrant ≡ license insight,” and §R5). The useful insight is a
**cross-level analogy**, not identity:

- Toulmin's claim, grounds/data, warrant, backing, qualifier, and rebuttal describe
  roles inside an object-level argument.
- SETEC Voiceprint's `ClaimLicense` is a meta-level epistemic-governance object. It
  says what an audit result may and may not be reported as saying, under named
  comparison, register, language, length, calibration, and provenance constraints.

ClaimLicense is not a Toulmin warrant. It does not populate or replace APODICTIC's
`Argument_State`, create a soundness judgment, or turn a measurement into a conclusion.

### Sources and snapshot posture

- **Toulmin model:** Stephen Toulmin, *The Uses of Argument* (1958). APODICTIC's
  six-role account is documented in
  [`dialectical-clarity-level-setting.md`](../plugins/apodictic/skills/specialized-audits/references/craft/dialectical-clarity-level-setting.md),
  and R2 records Toulmin as its typed warrant/rebuttal design source.
- **APODICTIC model:** [`argument-state-schema.md`](argument-state-schema.md) §§2–6.
  Claims live in §2, support/grounds in §3, warrant/backing/qualifier in §4, and
  warrant-specific exception conditions in typed §6 `WARRANT-DEFEATER` records.
- **SETEC model:** setec-voiceprint v1.124.0, commit
  `43138034e1017961758b90187b9fe0bed10fae54`: live
  `plugins/setec-voiceprint/scripts/claim_license.py` and `output_schema.py`, plus
  producer-owned `schema_version: 1.0` contract fixtures for
  `argument_decision_audit`, `agd_move_scan`, and `variance_audit`.

This is a documentation snapshot, not an APODICTIC dependency floor. APODICTIC does
not import or vend ClaimLicense through this crosswalk. A future SETEC change can make
the prose stale without breaking APODICTIC CI; updating it requires re-reading the
producer implementation and serialized fixtures, recording the new producer version
and commit, and reviewing any changed cardinalities.

## Compared layers and ownership

| Side | Level | Compared object | Object whose claim is governed |
|---|---|---|---|
| Toulmin / APODICTIC | Object-level | One reconstructed argument in the manuscript | A `C0`/`Cn` proposition supported through grounds and an inferential bridge |
| SETEC ClaimLicense | Meta-level | One audit result's interpretation policy | A reader-facing statement about what the audit's `results` may support |

At object level, APODICTIC records the manuscript's argument in `Argument_State`
§§2–6. At meta level, SETEC's measurement and comparison data live primarily in the
surrounding envelope's `results`, `baseline`, and `target`; ClaimLicense governs how
those outputs may be interpreted.

The envelope's top-level `task_surface` is the routing owner.
`output_schema.build_output` enforces equality between it and nested
`claim_license.task_surface`. The nested value is a deliberately duplicated carrier
that keeps the license self-describing. Equality between routing fields is not identity
with a Toulmin component, and neither value is an instance-level conclusion.

## Cardinality discipline

Rows run from a SETEC field/object to a Toulmin role and use R4A's closed vocabulary:
`exact`, `broader`, `narrower`, `related`, or `unmapped`. This crosswalk has no
`exact` row. `Related` means analogous limiting, supporting, or claim-scoping work at
the meta level; it does not mean semantic identity. `Unmapped` means the current
serialized object supplies no field with that role.

| SETEC field/object | Toulmin target | Cardinality | Decision |
|---|---|---|---|
| Envelope `results` | Grounds/data | `related` | Measured observations are the closest meta-level grounds, but `results` is surface-specific and outside ClaimLicense. A result value is not automatically evidence for every licensed reading. |
| Envelope `baseline` / `target` | Grounds context | `related` | These identify the compared material and input, not an argument component or inference rule. |
| Envelope `task_surface` | Any Toulmin role | `unmapped` | Authoritative output-routing field. `build_output` requires equality with nested `claim_license.task_surface`; routing identity is not argument-component identity. |
| `claim_license.task_surface` | Claim domain/scope | `related` | Duplicate self-describing carrier of the governed task surface. It scopes the class of report but is not the report's instance-level conclusion. |
| `claim_license.licenses` | Claim / qualified conclusion | `related` | States the class of report the output entitles. It does not state the complete actual claim, bind named grounds to that claim, or prove it. |
| `claim_license.does_not_license` | Rebuttal and qualifier boundaries | `related` | Excludes readings and records anti-verdict discipline. It is not necessarily an “unless” condition on one inference and is not identical to Toulmin rebuttal. |
| `claim_license.comparison_set` | Grounds context / backing | `related` | Records corpus, baseline, judge, literature anchor, or other comparison provenance. Contents vary by surface and do not express why the result entails the licensed report. |
| `claim_license.length_range_words` | Qualifier / field-of-application limit | `related` | Bounds applicability by length; it is not modal force such as “probably.” |
| `claim_license.register_match` | Qualifier / rebuttal boundary | `related` | Names intended registers. Mismatch may limit application but is not a warrant-specific exception record. |
| `claim_license.language_match` | Qualifier / rebuttal boundary | `related` | Same posture as register: an applicability constraint, not an inference rule. |
| `claim_license.fpr_target` | Qualifier / operating point | `related` | When populated, constrains a statistical decision posture. It is often `null` and does not qualify every prose claim by itself. |
| `claim_license.confidence_interval_95` | Qualifier / uncertainty | `related` | When populated, expresses uncertainty about a named metric or operating point. It is often `null`; it is not a general warrant. |
| `claim_license.additional_caveats` | Qualifier and rebuttal boundaries | `related` | Carries heterogeneous limitations, abstentions, provenance warnings, and interpretive caveats; that heterogeneity prevents a one-component identity. |
| `claim_license.references` | Backing | `related` | Sources may back method or interpretation policy, but a citation list neither guarantees backing nor identifies which inference it supports. |
| Current ClaimLicense as a whole | Warrant | `unmapped` | It has no `entitlement_basis`, `inference_rule`, or equivalent field explicitly connecting named result grounds to a named licensed conclusion. |
| `claim_license_rendered` | Any Toulmin role | `unmapped` | Markdown projection of ClaimLicense, not a second semantic object. |
| Envelope `schema_version`, `tool`, `version`, `available`, `warnings`, `ai_status` | Any single Toulmin role | `unmapped` | Serialization, producer, availability, warning, and routing metadata may affect reliance, but none is a Toulmin component by identity. |

The reverse non-mappings matter just as much:

- Toulmin **claim** is normally the actual interpretation sentence a consumer writes;
  ClaimLicense only bounds its permissible class.
- Toulmin **grounds** are the concrete measured observations in `results`;
  `comparison_set` describes context but does not duplicate those observations.
- Toulmin **warrant** has no current serialized counterpart inside ClaimLicense.
  Surface-specific `results` may report warrant, backing, or rebuttal **coverage** (for
  example, SETEC's `warrant_probe`), but coverage status is observation about whether an
  argument component was found or assessed. It is not the component's inference-rule
  content, does not supply ClaimLicense's missing grounds→conclusion bridge, and does not
  make ClaimLicense the warrant.
- Toulmin **backing**, **qualifier**, and **rebuttal** have several related
  ClaimLicense fields but no one-to-one home.

## The permitted meta-argument analogy

A SETEC result can be reconstructed as a meta-argument in which measured results are
candidate grounds, a consumer states a bounded interpretation claim, and ClaimLicense
supplies governance constraints and contextual support around that inference. The current
object can help a reader test whether a proposed interpretation exceeds its license, but
it does not serialize the bridge “because result R under comparison C, infer claim P.”

Therefore:

- `licenses` is not itself a warrant;
- `does_not_license` is not automatically Toulmin rebuttal;
- `comparison_set` is not identical to grounds;
- `references` is not automatically backing;
- `confidence_interval_95` and `fpr_target` are not universal qualifiers; and
- a populated ClaimLicense does not license a soundness, validity, quality, fairness,
  authorship, calibration, or generalizability verdict beyond its own text.

Absence is not transitive. A null CI/FPR does not prove the inference invalid, and an
empty register/language list does not mean universal applicability. Read the specific
surface's `licenses`, `does_not_license`, caveats, results, and warnings together.

### Three meanings of “rebuttal”

1. **Toulmin / APODICTIC R2:** an exception condition on a particular warrant — an
   “unless …” clause represented by `WARRANT-DEFEATER` targeting `Cn.warrant`.
2. **Voiceprint B1 paragraph role:** a paragraph answering a counterclaim. It describes
   discourse function, not necessarily a warrant exception.
3. **General objection/response:** any challenge or answer. APODICTIC distinguishes claim,
   evidence, value, alternative, and warrant-directed relations; only the last is the
   Toulmin-aligned rebuttal object.

## Worked examples

### Argument-decision audit

`results.contributions` and the literature-anchored comparison are candidate meta-grounds
for a consumer's licensed structural-comparison sentence. The license's register limits,
dated-anchor caveat, judge provenance, and `does_not_license` text constrain that report.
They do not create an object-level warrant for the manuscript and do not authorize a
soundness verdict.

### AGD move scan

Located observations are candidate meta-grounds for the narrow statement “the scan
located these candidate moves.” The live license refuses APODICTIC codes, aggregates, and
soundness/quality readings. That governance does not make the manuscript's warrant, and
an observed move is a location rather than a finding or flaw.

## Hostile anti-equivalence cases

| Hostile statement | Required disposition |
|---|---|
| “`ClaimLicense == Toulmin warrant`.” | Reject: the current warrant mapping is `unmapped`; only a cross-level analogy exists. |
| “`licenses` is the claim and `results` are its grounds, therefore the envelope is a complete Toulmin argument.” | Reject: there is no explicit inference rule, results are heterogeneous, and no instance-level conclusion is required. |
| “`does_not_license` is Toulmin rebuttal.” | Reject as identity: refusals are often excluded conclusions or governance policy, not warrant-specific exception conditions. |
| “A reference entry proves the license's warrant is backed.” | Reject: provenance is not proof, and references are not linked to a serialized inference rule. |
| “A null CI/FPR means no claim is licensed.” | Reject: many descriptive surfaces intentionally have no operating point; the license text controls. |
| “An empty register/language list means the result generalizes to every register/language.” | Reject: empty is not universal; consult surface caveats and comparison context. |
| “Voiceprint B1 `rebuttal` is Toulmin rebuttal.” | Reject: B1 is a paragraph role; APODICTIC R2's warrant-specific `WARRANT-DEFEATER` is the Toulmin-aligned object. |
| “ClaimLicense is a legal/software license.” | Reject: here it is an epistemic reporting-governance object. |

## Version and provenance

ClaimLicense has no independent schema-version field. It is serialized inside SETEC's
canonical output envelope, whose observed `schema_version` is `1.0`; envelope `tool` and
`version` name the producer, while producer-owned contract fixtures preserve representative
shapes. The authoritative producer implementation remains SETEC's `claim_license.py` and
`output_schema.py`. Green APODICTIC documentation gates establish file hygiene and existing
framework invariants, not the scholarly correctness of these mappings.

## Future `entitlement_basis` / `inference_rule`

R5 does not pre-approve either possible producer field. Promoting a future field's mapping
to `exact` with Toulmin warrant requires all of the following:

1. SETEC owns, serializes, and versions the field through its envelope and producer-owned
   contract fixtures.
2. It identifies the named result/grounds it consumes and the named licensed conclusion
   it supports.
3. It expresses the defeasible inference rule connecting them, rather than only a method
   citation, policy rationale, or restatement of `licenses`.
4. Its scope and exception behavior are documented.
5. APODICTIC re-reads the released producer contract and re-reviews the cardinality.

If `entitlement_basis` contains only calibration provenance, citations, or policy reasons,
it is `related` to backing/context rather than warrant identity. If `inference_rule` merely
names a rule family without binding concrete grounds and conclusion, it is also only
`related`. Even a qualifying field would make that field warrant-like; it would not make
the whole ClaimLicense identical to a Toulmin argument. Adding either field or vending its
schema is a separate cross-repo increment.
