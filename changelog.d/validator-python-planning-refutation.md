### Native Python planning, revision-diff and refutation validators

Added native retcon plans, state-card diffs, revision arcs, regression diffs and
all three refutation routes. Existing helpers retain discovery, prior/current
ordering, strict behavior, distinct flag handling and snapshot/read checks.
Tests exercise canonical plans/rounds and hostile refutation inputs. Shared
refutation self-tests print a random diagnostic path, so their complete independent
PASS checks retain an explicit output-equivalence limitation pending a separate
self-test stabilizer. All 18 gate children are now native; gate launcher and
aggregate cutover remain separate queued work.
