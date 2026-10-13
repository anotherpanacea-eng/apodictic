### Deterministic specificity and refutation self-tests

Specificity and shared refutation self-tests now capture their expected negative
CLI read diagnostics, assert exit status plus the complete artifact role/path
boundary and read/decode reason, and reject false PASS output.
Diagnostic payload checks follow the complete expected path delimiter, so valid
temporary-root names cannot supply a decode reason or trigger a false failure.
This removes random temporary filenames from successful self-test stdout while retaining
named fail-closed checks and unchanged ordinary command output. All 41 migrated
self-test surfaces again compare exact bytes without normalization. Gate launchers
and aggregate cutover remain separate held work.
