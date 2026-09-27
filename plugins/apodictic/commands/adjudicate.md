---
description: Review and record author decisions on an existing reconstruction claim graph
argument-hint: project directory
allowed-tools: Read, Write, Bash, Glob
---

# /adjudicate — Author approval session

Load `../skills/core-editor/SKILL.md`, then follow
`../skills/core-editor/references/craft/approval-workflow.md` in full.
This is the dedicated approval workflow; do not launch diagnostic passes,
normalize a new graph, draft prose, or route through generic `/audit`.

Use the existing project directory supplied by the author: $ARGUMENTS.
If absent or ambiguous, identify that directory before any write. All state
belongs beside that project's manuscript, never in the plugin repository.

This increment provides mechanical decision capture and resume. Semantic
exclusion screening remains unavailable: a nonempty rejection set blocks new
approvals. Explain that limitation before beginning; never offer a blanket
override or suggest removing legitimate rejections merely to proceed.
