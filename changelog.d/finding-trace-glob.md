### Validators — finding-trace completion glob narrowed

`finding-trace`'s `_COMPLETION_GLOBS` narrowed from `*_Revision_*.md` to `*_Revision_Report_*.md`, so a deadline-coaching `*_Revision_Calendar_*.md` is no longer mis-classified as a completion artifact (which would let its mentions advance a finding toward `revised`). Aligns finding-trace with the Increment-4a `revision_round` gate, which already narrowed its `revision_report` key. Negative-test guarded (`calendar_not_completion`); the revision-*stage* glob (`_REVISION_GLOBS`, for plan-coverage) stays broad.
