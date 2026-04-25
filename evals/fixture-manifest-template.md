# Fixture Manifest Template

Copy this file to `evals/manifests/<fixture-slug>.md` and fill in every field. Empty fields block fixture use.

## Identity

- **Fixture slug:**
- **Short name:**
- **Bucket:** short-fiction-known / 60k-100k / long-120k-plus / argument-nonfiction / high-risk-consent-reception / clean-control / ai-assisted / known-good-regression
- **Status:** active / draft / deprecated

## Source And Permission

- **Source class:** public-domain / permission-cleared / joshuas-private-fiction / client-or-third-party / synthetic-or-derived / high-risk-sample
- **Permission status:**
- **Permission record (if any):**

## Content Storage

- **In-repo text?:** yes / no
- **Storage location:** path or description of external storage
- **What, if any, text is stored:**
- **Quotation policy:** outputs may quote / outputs may reference without quoting / outputs must paraphrase only

## Expected Diagnosis

- **Rubric file:** `evals/rubrics/<rubric>.md`
- **Expected-diagnosis summary or known-comparison notes:**
- **Artifact scope for blind review:** full-letter / synthesis-only / pass-only / audit-routing / validator
- **Target metrics (pre-registered):**

## Release And Publication

- **Can outputs be used in public release notes?:** yes / no / with redaction. **Any Joshua-authored material (fiction, OCA work, blog, academic, testimony) is always no**, per [../docs/eval-harness-spec.md §Fixture Provenance Policy](../docs/eval-harness-spec.md#fixture-provenance-policy).
- **Can the fixture itself be shared with external reviewers?:** yes / no / blind-review-only. Blind-review-only is the safe default for any private-source fixture.

## Maintenance

- **Date added:**
- **Last refreshed:**
- **Known staleness:**
- **Retirement criteria:**

## Notes

Free-form. Flag dependencies on other fixtures, cross-references to review log entries, known false-positive risks, and anything else a future reviewer needs to interpret results.
