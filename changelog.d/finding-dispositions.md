### Finding Dispositions — engine-level `declined`/`deferred` set-asides

A deliberately set-aside finding is now a mechanical record, not a prose note a later session must
remember to read (`docs/finding-dispositions.md`). Dispositions are an **overlay**, never a fourth
lifecycle state: `execution.finding_dispositions` maps `F-id → apodictic.finding_disposition.v1`
(new closed-key schema, no severity field by construction) beside an untouched
`finding_states` — the fold stays rank-monotonic, finding-trace E3 unchanged. Pinned durable
markers (`<!-- declined: F-… — reason -->` / `<!-- deferred: F-… until: trigger — reason -->`) are
the canonical source, with ONE shared grammar helper (`apodictic_artifacts._DISPOSITION_RE` +
`parse_disposition_markers()`, code-span-stripped via the `override_marker` SSoT) imported by both
`run_gate.py` and the new validator. Dual writer mirrors `revised` exactly: governed projects
freeze full records into `gate_events[].disposition_deltas` at `revision_round` clear (fold-derived
map, `pointer == fold`, same-event revise+disclaim launder rejected by `gate-state`); non-governed
projects write the validated record directly. New `disposition-check` validator (self-testable
count is derived): DP0 record shape (trigger-iff-deferred), DP1 the `/ready` teeth — an active
declined/deferred Must-Fix must be named on the assessment's pinned `**Declined/Deferred
Must-Fixes:**` caveat lines, run BEFORE the verdict is delivered — and DP2 no-laundering
(same-run resolved+declined contradiction, phantom keys, ledger↔calibration severity mismatch,
triage-tally decrement via the shared `structured_findings.severity_tally`, bidirectional
marker/sidecar sync with governed-lag exemption). Canonical fixture
`references/example-run-folder-dispositions/` wired into `--check-all` with three hostile arms
(caveat stripped → DP1 fails; trigger stripped → DP0 fails; record dropped → DP2.5 warns, `--strict`
fails). Consumers: the revision-coach Loop Dispatch skips declined ids, trigger-reviews deferrals
(ISO dates fire mechanically), and records set-asides at the stalled off-ramp; `feedback-triage`
gains W3 (a declined item citing a ledger `F-…` id with no recorded disposition) plus the
decline-reconciliation offer; `/ready` gains the caveat block + a `CONDITIONALLY VIABLE` ceiling
for undisclosed declined Must-Fixes (fired deferrals count as open); the roundtrip resume displays
active dispositions and never machine-proposes `declined`/`deferred`. State gardening preserves
active disposition markers and compresses superseded ones to the archive line form. The honesty
gates (`softness-check`, `deficit-lock`, `severity-floor`, `structured-findings`, `finding-trace`,
`regression-diff`) read dispositions nowhere — a disposition grants no severity relief and never
decrements a count.
