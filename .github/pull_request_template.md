## Summary

<!-- What changed. Cite the Issue (`Closes #N`) or ROADMAP item this implements. -->

<!-- Ordinary changes stay draft and unarmed until admitted to a periodic train. -->

## Why

<!--
The problem solved, failure mode prevented, or roadmap item advanced.
For Issue-driven work, the Issue's acceptance criteria are the contract
the reviewer checks this diff against.
-->

## Validation

<!--
Proof of correctness a reviewer can read against the diff:
- `python -m compileall plugins scripts` → clean
- manifests parse (CI does this)
- changelog entry added as a `changelog.d/<slug>.md` fragment (not a changelog edit)
- `node scripts/build-codex.mjs --self-check` + `build-antigravity.mjs --self-check`
  pass if `plugins/` changed (the generated trees are not committed — GitHub #52)
- `git diff --check` clean
-->

<!-- See AGENTS.md for the full workflow and conventions. -->

## Train clearance (train PRs only)

<!--
Exact base:
Exact head:

Included (PR, title, exact 40-hex head, dependency order):

Explicitly excluded:

Conflict resolutions or separately reviewed train-only adjustments:

Local validation and exact generic/fleet-posture review receipts:

Promotion and landing protocol:
- re-read unchanged main/base, train head, and constituent heads
- promote this frozen train once
- require the exact live `validate` receipt
- land with the expected-head/CAS guard, then verify containment
-->
