# Fixture Manifest: The Dinner Party — Standalone To Novel

## Identity

- **Fixture slug:** dinner-party-standalone-to-novel
- **Short name:** The Dinner Party — pre-APODICTIC standalone → post-APODICTIC novel chapter
- **Bucket:** short-fiction-known (short-form cross-version diagnostic)
- **Status:** active

## Source And Permission

- **Source class:** joshuas-private-fiction (F.T. Caller / Quiet Harm Imprint)
- **Permission status:** self-owned; author is framework owner
- **Permission record (if any):** implicit via authorship

## Content Storage

- **In-repo text?:** no
- **Storage location:**
  - **Pre-APODICTIC (earlier standalone):** `../../../Writing/The_Observers_Share/Archive/TSP_Archive/The_Dinner_Party_FINAL_REVISION.md` (14,571 words) as the primary "before" version. Alternative archive candidates: `The Dinner Party SECOND DRAFT.md` (14,454), `The_Dinner_Party_De-MUDDLED.md` (14,749), `The Dinner Party (not final).md` in Misc_Archive (14,579). Excluded: `The Dinner Party (Overactive AI Version).md` (20,540 words) — known-bad baseline, may be useful separately as an AI-prose calibration fixture.
  - **Post-APODICTIC (current novel chapter):** `../../../Writing/The_Observers_Share/Stories/The_Dinner_Party.md` (12,972 words)
- **What, if any, text is stored:** none in manifest. Both versions live under `Writing/The_Observers_Share/` and are local-only.
- **Quotation policy:** outputs may reference by line number. Blind-review packets must anonymize character names (Emma, Ryan, Claire, Maya). No extended prose quotes in publishable outputs.

## Expected Diagnosis

- **Rubric file:** `evals/rubrics/core-de.md`
- **Expected-diagnosis summary or known-comparison notes:** the delta between pre-APODICTIC and post-APODICTIC versions is itself the ground truth. A fresh APODICTIC run on `The_Dinner_Party_FINAL_REVISION.md` should identify diagnostic issues that correspond to the changes actually made in the current novel-chapter version. Diff the two versions and extract: what was cut, what was rewritten, what was added. APODICTIC findings that predict those changes score well; APODICTIC findings that name issues still present in the post-version are useful diagnostics of the current chapter; APODICTIC findings that recommend what revision actually avoided are regressions worth investigating.
- **Artifact scope for blind review:** full-letter on the pre-version; cross-version diff as secondary artifact
- **Target metrics (pre-registered):** root-cause accuracy (does APODICTIC name what got revised?), evidence specificity (are findings line-referenced?), absence detection (does APODICTIC identify absences the revision filled?), severity honesty (does APODICTIC give revision-warranting severity to issues that were actually revised?), firewall compliance (does APODICTIC stay abstract where the actual revision was creative?)

## Release And Publication

- **Can outputs be used in public release notes?:** **No, never.** F.T. Caller fiction. Same rule as [regrets-only-novella.md](./regrets-only-novella.md) and [observer-share-83k-hybrid.md](./observer-share-83k-hybrid.md).
- **Can the fixture itself be shared with external reviewers?:** blind-review-only, fully anonymized. The cross-version diff is the most shareable derivative but still requires character-name substitution.

## Maintenance

- **Date added:** 2026-04-24
- **Last refreshed:** 2026-04-24
- **Known staleness:** the current novel-chapter version is living text — if Joshua further revises it after this fixture anchors any decisions, note the rev in the review log.
- **Retirement criteria:** retire when the cross-version delta is exhausted as a ground-truth reference or when Joshua publishes The Observer's Share and wants the fixture reclassified as published-fiction.

## Audit-Routing Pre-Labels

| Audit | Expected | Reason |
|---|---|---|
| Consent Complexity | auto-run | Dinner Party is a load-bearing consent-dynamics scene in the novel |
| Reception Risk | auto-run | Erotic fiction with explicit power dynamics |
| AI-Prose Calibration | recommend | Archive includes a "(Overactive AI Version)" — suggests AI-prose is a known risk vector here |
| Scene Turn | auto-run | Universal audit; this is a single scene/story |
| Stakes System | auto-run | Universal audit |
| Decision Pressure | auto-run | Universal audit |

## Notes

This is the strongest ground-truth fixture in the current set because the "expected diagnosis" is a literal before/after delta with known Joshua-approved revisions. Use as a primary test for:

1. Does APODICTIC diagnose the pre-version issues that Joshua actually revised?
2. Does the current novel chapter still have diagnosable issues APODICTIC catches?
3. Does APODICTIC avoid flagging as problems things that were intentional creative choices in the revision?

The `(Overactive AI Version)` archive file is a separate candidate fixture for AI-prose calibration — worth its own manifest if that audit becomes a review focus.
