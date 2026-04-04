---
description: Run a full development edit on a manuscript
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

Alias shortcut for `apodictic-start` with prefilled router values:

- `artifact=full_draft`
- `goal=repair`
- `concern=general` (unless the user provides a specific concern)

Load `../skills/core-editor/SKILL.md`, then execute the same runtime router behavior from `../skills/core-editor/references/intake-router-runtime.md` with Q1/Q2 prefilled by this command. Still ask Q3 constraints/operator modifiers unless already known.

After routing, run the selected workflow exactly as `apodictic-start` would:

- Development edit route -> `../skills/core-editor/references/run-core.md` + resolver from `../skills/core-editor/references/pass-dependencies.md`
- Apply auto-escalation recommendation for expansion to advanced passes
- Create run folder (`runs/YYYY-MM-DD_{model}_{type}/`) at the start of the run
- Write all run artifacts (pass reports, contract, findings ledger, results guide) into the run folder
- Update rolling state (`Diagnostic_State.md`, `SYNTHESIS.md`, `README.md`) at the project root
- Never write to the plugin repo

See `../skills/core-editor/references/output-policy.md` §Folder Architecture for the full folder convention.

If a manuscript file path is provided: @$1
