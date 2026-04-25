# Fixture Manifest: Observer's Share 83k Hybrid Comparison

## Identity

- **Fixture slug:** observer-share-83k-hybrid
- **Short name:** The Observer's Share — 83k composite novel, single-context vs hybrid
- **Bucket:** 60k-100k
- **Status:** active

## Source And Permission

- **Source class:** joshuas-private-fiction
- **Permission status:** self-owned; author is framework owner
- **Permission record (if any):** implicit via authorship

## Content Storage

- **In-repo text?:** no
- **Storage location:** `Outputs/Hybrid_Test/` (gitignored; local-only on Joshua's machine)
- **What, if any, text is stored:** in the manifest itself, none — only structural summary. Raw outputs, reverse outline, and pass ledgers live under `Outputs/Hybrid_Test/83k_Run/` and `Outputs/Hybrid_Test/Single_Context_Run/`. `Outputs/Hybrid_Test/COMPARISON_Anonymized.md` is a publishable derived summary.
- **Quotation policy:** outputs may reference by line number without extended quotation; blind-review packets should use synthesis-only excerpts and anonymize character names before external review

## Expected Diagnosis

- **Rubric file:** `evals/rubrics/synthesis.md`
- **Expected-diagnosis summary or known-comparison notes:** `Outputs/Hybrid_Test/COMPARISON_Anonymized.md` (ground truth for single-context vs hybrid delta on this manuscript). A strong synthesis should name: (1) amnesia paradox as structural flaw, (2) awareness-without-change gap between confession and recurrence, (3) authority without enforcement, (4) prose conditioning the reader, (5) failed dissolution vs. successful integration as distinct Coda diagnoses.
- **Artifact scope for blind review:** synthesis-only (default) or full-letter when available
- **Target metrics (pre-registered):** root-cause accuracy, evidence specificity, counterevidence, severity honesty, absence detection, firewall compliance

## Release And Publication

- **Can outputs be used in public release notes?:** **No, never.** This is F.T. Caller fiction published under Quiet Harm Imprint. The existing `Outputs/Hybrid_Test/COMPARISON_Anonymized.md` was created before this policy was articulated and is not grandfathered into any new public use. No new APODICTIC outputs, raw or anonymized, may appear in public release notes, marketing material, sample letters, or any other APODICTIC-facing publication.
- **Can the fixture itself be shared with external reviewers?:** blind-review-only, with character names replaced and line-level quotes removed. External reviewers operate under the blind-review protocol and do not retain outputs after scoring.

## Maintenance

- **Date added:** 2026-04-24
- **Last refreshed:** 2026-02-24 (original test run, Opus 4.6, APODICTIC v4.15)
- **Known staleness:** original outputs are from Opus 4.6 and v4.15. Useful for packet-format calibration; not useful as current-model baseline. Needs rerun on current model before this fixture anchors any behavior-changing decision.
- **Retirement criteria:** retire when a more recent full-run on current model with current framework version is available as primary baseline; keep as historical regression reference.

## Notes

This fixture was used for the 2026-04-24 blind-review protocol dry run. See [../../Outputs/blind-review/2026-04-24_observers-share-83k_hybrid-vs-single-dryrun/](../../Outputs/blind-review/2026-04-24_observers-share-83k_hybrid-vs-single-dryrun/) and findings therein. Protocol packet-format issues were resolved into `docs/blind-review-protocol.md`.

Before this fixture can be used as a current-model baseline, run APODICTIC on the manuscript with Opus 4.7 in both single-agent and hybrid modes under the 1.7.1 framework.
