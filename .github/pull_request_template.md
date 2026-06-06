## Summary

<!-- What changed. Cite the Issue (`Closes #N`) or ROADMAP item this implements. -->

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
- `node scripts/build-codex.mjs` re-run + parity committed (if `plugins/` changed)
- `git diff --check` clean
-->

<!-- See AGENTS.md for the full workflow and conventions. -->
