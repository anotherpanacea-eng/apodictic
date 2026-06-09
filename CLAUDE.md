# CLAUDE.md

This repo's agent workflow, conventions, and hard-won lessons live in **[`AGENTS.md`](AGENTS.md)** — the canonical, tool-agnostic source (Claude Code, Codex, and others all read from it). This file exists only so Claude Code's auto-load points you there.

Read `AGENTS.md` first. In particular:

- **`AGENTS.md` § The flow → Review practices** — hostile fixtures, run the real CI command (`bash scripts/validate.sh --check-all`) first, and distrust count-shaped claims.
- **`AGENTS.md` § Platform parity → the dual script mirror** — `scripts/` (root, what CI runs) and `plugins/apodictic/scripts/` (canonical) are committed copies that must be kept byte-identical by hand.
- **`AGENTS.md` § CI / PRs and merges** — `validate.sh --check-all` is the gate; merge via merge commit (not squash).

Update `AGENTS.md`, not this file, when the workflow changes.
