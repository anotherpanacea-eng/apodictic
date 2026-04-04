---
description: Initialize a new development editor project
allowed-tools: Read, Write, Edit, Bash, Glob
---

Initialize a new project for the APODICTIC Development Editor.

Load `../skills/core-editor/SKILL.md`. Create the project scaffolding:

1. **Create or confirm the project output context** outside the plugin repo. If the writer already has a manuscript folder, create or reuse an `Outputs/` sibling there. If they already have an output folder in use, reuse it instead of creating a second one.

2. **Initialize Diagnostic State** in that output context from `../skills/core-editor/references/diagnostic-state-template.md`.

3. **Run Intake Protocol:** If a manuscript is provided, read it and generate a DRAFT Contract Schema by inferring genre, reader promise, controlling idea, and structural features from the text. Present the draft to the author — misalignments between inferred contract and author intent are diagnostically valuable.

4. **Generate Contract Document** (`[Project]_Contract_[runlabel].md`) from the contract template, populated with intake findings and author corrections.

5. **Select genre modules and specialized audits** appropriate for the project. Record selections in the Contract.

6. **Report** what was created, where the output context lives, and what the next step is (typically: run `/develop-edit` or specific passes).

If a manuscript file path is provided: @$1
If a project name is provided as text, use it for the project directory and file naming.
