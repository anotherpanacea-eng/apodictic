---
description: Generate revision priorities from diagnostic state
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

Generate a revision plan from the current diagnostic state.

Load the `core-editor` skill. Follow the Revision Round Protocol:

1. **Locate Diagnostic State:** Find `Diagnostic_State.md` in the project's output context.

2. **Gather revision context:** Ask the author: What changed since last analysis? Which flags were addressed? Which were deliberately declined? Any new concerns?

3. **If this is a revision round** (previous analysis exists):
   - Run Delta Scan on changed sections
   - Check ripple effects of changes
   - Verify whether addressed flags are resolved
   - Detect new issues in changed material
   - Check integration with unchanged material

4. **If this is initial prioritization** (after a first development edit):
   - Read synthesis findings and surgery list
   - Organize into revision phases following the standard order: contract drift → causal chain → protagonist agency → relationship dynamics → reveal timing → scene turns → continuity → line polish

5. **Output:** Revision Report with resolved flags, remaining flags, new issues, ripple effects, and prioritized next steps. Update `Diagnostic_State.md`.

If a project path is provided: @$1
