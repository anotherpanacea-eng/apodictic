# Ground Truth: modest-proposal-satire

## Provenance

- **Fixture slug:** modest-proposal-satire
- **Bucket:** 6 advocacy journalism / persuasive essay (satire); doubles as a bucket-4-adjacent Q7 hard case
- **Source class:** public-domain
- **Text stored in-repo?:** **no — referenced.** Jonathan Swift, *A Modest Proposal for Preventing the Children of Poor People from Being a Burthen to Their Parents or Country, and for Making Them Beneficial to the Publick* (1729). Public domain; widely available (e.g., Project Gutenberg). This fixture demonstrates the reference-by-source path for non-stored public-domain text.
- **Authored or adapted by:** Jonathan Swift (1729); ground truth registered by APODICTIC benchmark
- **Registered (date):** 2026-05-30
- **Ground-truth authority:** author-registered against the established scholarly reading of the text as Juvenalian satire; the ironic structure is not interpretively contested
- **Scope:** Q1, Q7 (primary). Q2/Q3/Q5/Q6 = N/A — the surface argument is intentionally monstrous; scoring its support/warrant on a literal reading is a category error the Distinguish protocol must prevent.

## GT1 — Main claim *(Q1; §2 C0)*

- **Expected C0 (real, recovered through irony):** "English policy and the indifference of the propertied class toward the Irish poor are so callous that a literal proposal to sell and eat poor children is barely more monstrous than the status quo." The **surface** claim ("the nation should raise poor children as food") is the satirical vehicle, not C0.
- **Acceptable paraphrase band:** a hit recovers the *target of the satire* — the indictment of policy / absentee landlords / the dehumanizing economic logic applied to the Irish poor. Reporting the surface claim ("the author argues we should eat children") as C0 is a **miss** and indicates the engine read the irony literally.

## GT2 — Failure locus *(Q2)*

- **N/A.** Auditing the literal proposal's support/warrant ("the cost accounting is sound," "the inference from population to commodity is valid") is the category error. The Distinguish protocol must intercept *before* the support/warrant steps are reported as findings.

## GT3 — Strongest real objection *(Q3)*

- **N/A** for scoring. (The text itself preempts genuine reform proposals — the famous "other expedients" passage — which is part of the satirical architecture, not an objection gap.)

## GT4 — Audience calibration *(Q4)*

- **Audience profile:** Expertise MIXED (educated 18th-c. readership) · Receptivity MIXED→HOSTILE (the propertied class being indicted) · Consequence HIGH
- **Note:** calibration here means recognizing the ironic register the audience was expected to decode. Not separately scored in the slice.

## GT5 / GT6 — *(Q5, Q6)*

- **N/A — the surface argument must not be red-teamed or repair-sequenced on a literal reading.**

## GT7 — Distinguish classification *(Q7; §1 Distinguish / Step 9)* — **PRIMARY METRIC**

- **Expected classification:** UNCONVENTIONAL-BUT-EFFECTIVE
- **Form name:** sustained irony / Juvenalian satire (the real argument is the inverse of the literal proposition; meaning is carried by the gap between surface and intent).
- **Form-dependent codes that MUST be downgraded / suspended:** every code that would fire on a literal reading — DI codes for "monstrous standpoint," BP/scope codes, SM/WR on the cost accounting. None describe a real defect; all are artifacts of reading irony literally.
- **False-positive trap (the hardest in the slice):** (a) reporting the literal proposal as the claim and failing it as monstrous/unsound; or worse, (b) *evaluating whether the literal argument is correct* — a Firewall and Distinguish double-failure. An engine that does either scores **Q7 = 0**. The catastrophic failure mode is treating the most famous satire in English as a sincere policy argument.

## Notes

This is the upper bound on the Q7 specificity test and the reason positive
controls are mandatory in the corpus. It pairs with
`personal-essay-narrative-arg` (narrative juxtaposition) as the slice's two
unconventional-form controls. Because the text is not stored, a run requires
fetching the source separately; the benchmark records the edition/source used
so the run is reproducible. Use this fixture to confirm the Distinguish
protocol fires *before* the literal-reading codes are surfaced, not after.
