### Disposition supersedence is recomputed, never trusted (disposition-check DP2.6)

Sibling-sweep fix from the PR #161 Codex P1 class (an exemption gate trusting a recorded field):
`disposition-check`'s `active()` exempted a declined/deferred Must-Fix from the DP1 readiness
caveat on the sidecar's self-reported `finding_states[id] == "revised"` alone — one JSON field
edit on a non-governed sidecar waived the caveat, silenced the DP2.5 sync audit for the id, and
no validator on the enforcement path corroborated (finding-trace E5 is deliberately scoped to
report-mentioned ids; `/ready` runs only `disposition-check` at verdict time). Supersedence now
requires a corroborating `<!-- resolved: F-id -->` marker in a reachable completion artifact
(run folder, project root, or `runs/*` archives — evidence-only, so DP2.1's same-run scoping is
untouched); an uncorroborated `revised` leaves the disposition ACTIVE (DP1 caveat still owed)
and is surfaced as the new **DP2.6** WARN (ERROR under `--strict`). Adds 10 self-tests (the
`disposition-check` suite → 46): the keystone exploit repro, archived-evidence exemption,
evidence-not-leaked negative, DP2.5-no-longer-suppressed, non-UTF8 evidence fails closed, and a
run-folder + `runs/*` end-to-end both directions; `--check-all` gains hostile arm 4 (fabricated
supersedence must fail closed). Build-review folds: `_read` gains the `UnicodeDecodeError` guard
(the adjacent-exception class this PR later seeded a repo-wide sweep for), and the trusting-rule
sentences in `state-lifecycle.md` / `submission-readiness.md` are amended to the corroborated
form. Spec: `docs/disposition-supersedence-recompute.md`.
