### Plugin headroom

The shipped plugin drops from 509 to 426 files. Validator fixtures move from
`plugins/apodictic/scripts/test_fixtures/` to `tests/fixtures/validators/`
(the self-tests now fail, rather than skip, when a repo checkout lacks them).
The Codex-only sources (`README.codex.md`, `NON_PARITY_NOTES.codex.md`,
`route-explorer.codex.html`, and `.codex-plugin/plugin.json`) move to
`packaging/codex/` and are copied in by `build-codex.mjs` through the registry
overrides. The six deprecated core-editor references (`core-framework`,
`module-index`, `intake-router`, `intake-questions`, `certainty-axis`,
`structural-frameworks`) are deleted, and the registry and reference pointers
to them now name their canonical homes in `run-core.md` and `run-full.md`.
