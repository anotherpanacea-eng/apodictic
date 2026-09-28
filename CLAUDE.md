# CLAUDE.md

This repo's agent workflow, conventions, and hard-won lessons live in **[`AGENTS.md`](AGENTS.md)** — the canonical, tool-agnostic source (Claude Code, Codex, and others all read from it). This file exists only so Claude Code's auto-load points you there.

Read `AGENTS.md` first. In particular:

- **`AGENTS.md` § Test value convention** — tests must protect behavior,
  contracts, reproduced bugs, or stable safety boundaries; do not preserve
  implementation-mirroring tests or production seams built only for tests.
- **`AGENTS.md` § The flow → Review practices** — hostile fixtures, run the real CI command (`bash scripts/validate.sh --check-all`) first, and distrust count-shaped claims.
- **`AGENTS.md` § Platform parity** — validators live only in `plugins/apodictic/scripts/`; root `scripts/validate.sh` is a shim.
- **`AGENTS.md` § CI / PRs and merges** — `validate.sh --check-all` is the gate; merge via merge commit (not squash).

Update `AGENTS.md`, not this file, when the workflow changes.
