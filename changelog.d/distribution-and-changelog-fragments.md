### Distribution & changelog tooling

The generated `codex/` and `antigravity/` workspaces are **no longer committed** to
the repo. They are built from the canonical `plugins/` source and published as
**release assets** by a new `.github/workflows/release.yml` (triggered on `v*`
tags): `apodictic-codex-marketplace.zip`, the new `apodictic-antigravity.zip`, and
`apodictic.plugin`. Install is now download-and-open — no clone, no Node — with
build-from-source still available. This removes the ×3 parity-churn multiplier
that every release-touching change otherwise paid. (Decision: GitHub #52, Option B.)

`release-verify.mjs` and CI now `--self-check` the host builds (regenerate in a temp
dir and validate internal consistency) instead of diffing against committed trees,
and CI gained generator/parity gates (`release-generate --check`, both build
`--self-check`s, `assemble-changelog --check`).

The changelog moves to a **`changelog.d/` fragment directory** at the repo root:
each change drops one `### `-headed fragment instead of editing the shared
changelog, and `scripts/assemble-changelog.mjs` cuts them into a dated section at
release time (wired into `release.sh` after the version bump). (GitHub #51.)
