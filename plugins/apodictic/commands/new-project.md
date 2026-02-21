---
description: Initialize a new development editor project
allowed-tools: Read, Write, Edit, Bash, Glob
---

Initialize a new project for the APODICTIC Development Editor.

Load the `core-editor` skill. Create the project scaffolding:

1. **Create project directory** in the current working folder with an `Outputs/` subfolder.

2. **Initialize Diagnostic State** from the diagnostic state template (`references/diagnostic-state-template.md`).

3. **Run Intake Protocol:** If a manuscript is provided, read it and generate a DRAFT Contract Schema by inferring genre, reader promise, controlling idea, and structural features from the text. Present the draft to the author — misalignments between inferred contract and author intent are diagnostically valuable.

4. **Generate Contract Document** (`Contract_and_Controlling_Idea.md`) from the contract template, populated with intake findings and author corrections.

5. **Select genre modules and specialized audits** appropriate for the project. Record selections in the Contract.

6. **Report** what was created and what the next step is (typically: run `/develop-edit` or specific passes).

If a manuscript file path is provided: @$1
If a project name is provided as text, use it for the project directory and file naming.
