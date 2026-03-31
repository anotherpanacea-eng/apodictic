---
description: Quick structural diagnostic on a specific concern
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

Alias shortcut for `/start` with targeted routing:

- `goal=repair`
- `targeted=true`
- `concern=<required>` (ask if missing)

Load `../skills/core-editor/SKILL.md`, resolve the concern through `../skills/core-editor/references/pass-dependencies.md`, and run only the minimum pass set plus dependencies. This is a focused diagnostic, not a full-run default unless concern ambiguity triggers the general floor rule.

Output should remain scoped:

- Specific findings with scene/page references
- Confidence markers
- Short action list tied to the diagnosed concern
- Any state updates go to the active project output context beside the manuscript, not the plugin repo

If a manuscript file path is provided: @$1
