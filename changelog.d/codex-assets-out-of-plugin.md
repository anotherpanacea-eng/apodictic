### Codex images move out of the plugin folder

The five Codex listing images (icon and screenshots) move from `plugins/apodictic/assets/` to
`packaging/codex/assets/` and are copied into the Codex build via `release-registry.json`
overrides. Two screenshots exceeded the Claude plugin directory's 256 KiB per-file limit, which
failed directory validation; the Claude plugin never referenced them.
