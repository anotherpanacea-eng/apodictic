# Scene-Ethics Plan: A Quiet Year (memoir, pre-draft)

<!--
Worked example of a contract-conformant Scene-Ethics Plan (Nonfiction Pre-Draft Pathway, Increment 4;
see pre-writing-pathway/references/nonfiction-pre-draft.md + docs/nonfiction-pre-draft.md). Before
drafting narrative nonfiction / memoir that depicts identifiable real people, the writer plans how
each depiction will be handled ETHICALLY — consent, fairness, anonymization/composite/omission. This
is the writer's ethical plan; it is NOT ethical adjudication and NOT legal advice. Legal exposure
(defamation / privacy / rights) lives in the Legal Risk Register; the two coexist and cross-reference
via `legal_ref`.

This file is exercised by `validate.sh --check-all` as a canonical release-gate target for
`scene-ethics` (E1 schema, E2 unique EP-NN ids; W1 no unresolved depiction — an identifiable person
depicted as-is with neither consent nor a fairness rationale; W2 each as-is identifiable depiction
cross-checks the Legal Risk Register). Every depiction below is resolved, so it passes clean.
-->

**This is an ethical plan, not legal advice.** Legal exposure for these depictions is tracked
separately in the Legal Risk Register (defamation / privacy / rights); `legal_ref` cross-links the two.

## Depictions

<!-- apodictic:scene_ethics
{"schema":"apodictic.scene_ethics.v1","id":"EP-01","subject":"the narrator's former manager (named, identifiable)","depiction":"portrayed making a dismissive remark in a team meeting","consent_status":"not-sought","handling":"anonymize","fairness_check":"role and remark kept; name, employer, and identifying details changed so the person is not identifiable"}
-->

<!-- apodictic:scene_ethics
{"schema":"apodictic.scene_ethics.v1","id":"EP-02","subject":"the city council member, quoted from a public hearing","depiction":"quoted voting against the accessibility measure on the record","consent_status":"not-applicable","handling":"as-is","fairness_check":"public official acting in a public capacity; quote is from the published hearing transcript, in context"}
-->

<!-- apodictic:scene_ethics
{"schema":"apodictic.scene_ethics.v1","id":"EP-03","subject":"the narrator's sister (identifiable)","depiction":"portrayed during a private family conflict, as-is","consent_status":"obtained","handling":"as-is","fairness_check":"sister read the chapter and approved the portrayal; her objection to one detail was cut","legal_ref":"LR-02"}
-->

## Notes

- **Handling** options: `as-is` (identifiable, unmodified) · `anonymize` · `composite` · `seek-consent` · `omit`.
- An **as-is** depiction needs a resolution: consent `obtained` / `not-applicable`, or a fairness rationale — otherwise it's an unresolved exposure to address before drafting (W1).
- Each as-is identifiable depiction should be cross-checked against the **Legal Risk Register** (`legal_ref`), where its legal exposure is tracked (W2).
