---
description: Initialize a new development editor project
allowed-tools: Read, Write, Edit, Bash, Glob
---

Initialize a new project for the APODICTIC Development Editor.

Load `../skills/core-editor/SKILL.md`. Create the project scaffolding per `../skills/core-editor/references/output-policy.md` §Folder Architecture:

1. **Create or confirm the project root** outside the plugin repo. Use Title_Case with underscores for the folder name (e.g., `My_Novel`). If the writer already has an existing output folder in use, reuse it as the project root — create `runs/` inside it if it doesn't exist yet.

2. **Create the `runs/` directory** inside the project root.

3. **Initialize rolling state at the project root:**
   - `Diagnostic_State.md` from `../skills/core-editor/references/diagnostic-state-template.md`
   - `Diagnostic_State.meta.json` from `../skills/core-editor/references/diagnostic-state-meta-template.json`
   - `README.md` with project manifest header and empty run archive table (see output-policy §Project Manifest)

4. **Run Intake Protocol:** If a manuscript is provided, read it and generate a DRAFT Contract Schema by inferring genre, reader promise, controlling idea, and structural features from the text. Present the draft to the author — misalignments between inferred contract and author intent are diagnostically valuable.

5. **Create first run folder** (`runs/YYYY-MM-DD_{model}_core-de/` or appropriate type) and **generate Contract Document** (`[Project]_Contract_[runlabel].md`) inside it, populated with intake findings and author corrections.

6. **Select genre modules and specialized audits** appropriate for the project. Record selections in the Contract.

7. **Report** what was created, where the project root lives, the folder structure, and what the next step is (typically: run `/develop-edit` or specific passes).

If a manuscript file path is provided: @$1
If a project name is provided as text, use it for the project directory and file naming.
