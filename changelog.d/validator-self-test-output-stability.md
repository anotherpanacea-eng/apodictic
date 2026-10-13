### Deterministic specificity and refutation self-tests

Specificity and shared refutation self-tests now capture their expected negative
CLI read diagnostics and assert exit status 2 plus the named artifact role and
path. This removes random temporary filenames from successful self-test stdout
while retaining the named fail-closed checks and unchanged ordinary command
output. All migrated self-test surfaces again compare exact bytes without
normalization.
