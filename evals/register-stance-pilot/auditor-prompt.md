# Blind Auditor Prompt - Register / Stance E7

Read `fixture-hybrid.txt` and `machinery-addendum.md`. Do not read the build spec,
`expected-profiles.md`, prior run records, or another auditor's output.

Run the Nonfiction Argument Engine as a writer-confirmed generative-register audit. Use only
`Must-Fix`, `Should-Fix`, and `Could-Fix`. Inventory every cash-out and apply the machinery's
high-stakes/cash-out/register/stance precedence before the Deficit Lock. Classify moves, never
the truth of claims. Ambiguity returns to the writer.

Return exactly two complete Markdown artifacts, labeled `Argument_State.md` and
`Findings_Ledger.md`. They must be ready to save and pass `stance-calibration` without
substantive normalization.

## `Argument_State.md` contract

Include this exact section and field grammar, filling in the values:

```text
## 1. Context and Classification

Form: [form]
Goal: [goal]
Argument type: AT5 - generative / lens-offering
  Burden level: MEDIUM
Register: generative
Register confirmation: WRITER-CONFIRMED
High-stakes gate: INACTIVE - NONE
Audience:
  Expertise: GENERAL
  Receptivity: MIXED
  Consequence context: HIGH
Cash-out inventory:
  - CO1 | Location: [location] | Kind: [ASSERTION or PRESCRIPTION] | Press: [LIGHT, MEDIUM, or HARD] | Consequence: [LOW, MEDIUM, or HIGH]
```

Use canonical cash-out identifiers `CO1`, `CO2`, and so on, consecutively. Do not use `CO-1`,
`CO01`, or a decorated `NONE`. Add two separate lines: a `Warrant verdict:` field whose complete
value is exactly one of `WARRANTED`, `UNCONVENTIONAL-BUT-WARRANTED`, or `UNWARRANTED`, then a
`First defeated test:` field whose value is the test or `NONE`.

## `Findings_Ledger.md` contract

For every finding, include a visible mechanism heading and exactly one embedded block in this
shape:

```html
<!-- apodictic:finding
{"schema":"apodictic.finding.v1","id":"F-E7-01","mechanism":"...","severity":"Should-Fix","confidence":"HIGH","evidence_refs":["paragraph 1"],"fix_class":"...","risk_if_fixed":"...","register":"generative","stance":"S1","stance_verdict":"unearned","calibration_effect":"blocked-cash-out","cash_out_ref":"CO1"}
-->
```

Rules:

- IDs are `F-E7-01`, `F-E7-02`, and so on.
- Use only schema fields shown above or defined by the finding schema; omit a field rather than
  inventing prose-valued extensions.
- Every finding located at a cash-out span has its exact `cash_out_ref`. A prescriptive cash-out
  cannot be demoted and records `calibration_effect: blocked-cash-out` when calibration was
  attempted.
- A non-cash-out generative-register floor may use `calibration_effect: register-floor` only for
  a `WR#`, `SM#`, or `BP#` mechanism and must be `Could-Fix`.
- An actual stance demotion may use `calibration_effect: stance-demotion` only for the
  overstatement families enumerated in the addendum and must be `Could-Fix`.
- `stance` and `stance_verdict` appear together. An earned or earned-by-frame verdict must be
  `Could-Fix` and carry the applicable calibration effect. An unearned verdict leaves severity
  unchanged and does not itself require a calibration effect.
- Use `calibration_effect: blocked-cash-out` only when an earned or register-floor demotion was
  actually attempted at a prescriptive cash-out. Full asserted severity with an unearned verdict
  carries no `calibration_effect`; the canonical join records the cash-out burden.
- The `mechanism` value begins with its canonical code. State whether calibration applied or was
  blocked through the structured fields, not an invented annotation field.

After the two artifacts, give a short prose note explaining whether the journey and landing were
calibrated separately. The note is not part of either file.
