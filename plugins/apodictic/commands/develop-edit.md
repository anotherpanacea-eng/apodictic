---
description: Run a full development edit on a manuscript
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

Alias shortcut for `/start` with prefilled router values:

- `artifact=full_draft`
- `goal=repair`
- `concern=general` (unless the user provides a specific concern)

Load `../skills/core-editor/SKILL.md`, then execute the same runtime router behavior from `../skills/core-editor/references/intake-router-runtime.md` with Q1/Q2 prefilled by this command. Still ask Q3 constraints/operator modifiers unless already known.

After routing, run the selected workflow exactly as `/start` would:

- Development edit route -> `../skills/core-editor/references/run-core.md` + resolver from `../skills/core-editor/references/pass-dependencies.md`
- Apply auto-escalation recommendation for expansion to advanced passes
- Write artifacts and rolling state files to the active project output context beside the manuscript, never to the plugin repo

If a manuscript file path is provided: @$1
