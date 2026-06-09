---
description: Initialize a new development editor project
allowed-tools: Read, Write, Edit, Bash, Glob
---

Initialize a new project for the APODICTIC Development Editor.

Load `../skills/core-editor/SKILL.md`. Create the project scaffolding per `../skills/core-editor/references/output-structure.md` §Folder Architecture:

1. **Create or confirm the project root** outside the plugin repo. Use Title_Case with underscores for the folder name (e.g., `My_Novel`). If the writer already has an existing output folder in use, reuse it as the project root — create `runs/` inside it if it doesn't exist yet.

2. **Create the `runs/` directory** inside the project root.

3. **Initialize rolling state at the project root:**
   - `Diagnostic_State.md` from `../skills/core-editor/references/diagnostic-state-template.md`
   - `Diagnostic_State.meta.json` from `../skills/core-editor/references/diagnostic-state-meta-template.json`
   - `README.md` with project manifest header and empty run archive table (see `../skills/core-editor/references/output-structure.md` §Project Manifest)

4. **Run Intake Protocol:** If a manuscript is provided, read it and generate a DRAFT Contract Schema by inferring genre, reader promise, controlling idea, and structural features from the text. Present the draft to the author — misalignments between inferred contract and author intent are diagnostically valuable.

5. **Create first run folder** (`runs/YYYY-MM-DD_{model}_core-de/` or appropriate type) and **generate Contract Document** (`[Project]_Contract_[runlabel].md`) inside it, populated with intake findings and author corrections.

6. **Select genre modules and specialized audits** appropriate for the project. Record selections in the Contract.

7. **Register the project** so it is addressable by `/start <project>` and `/projects`:
   - Locate the **workspace root** — the nearest ancestor of the project root containing a `.apodictic/` directory (walk up, like locating `.git`). If none exists, create `.apodictic/registry.json` at a sensible workspace root (typically the project root's parent), initialized as `{"schema": "apodictic.project_registry.v1", "updated": "<date>", "projects": []}`. Never create it inside the plugin repo or plugin cache.
   - Append an `apodictic.project_entry.v1`. Derive the `id` from the title by **slugifying**: lowercase, replace every run of non-`[a-z0-9]` characters with a single hyphen, then trim leading/trailing hyphens — so `id` always matches `^[a-z0-9][a-z0-9-]*$` (e.g. "My Novel!" → `my-novel`, "The Wolves (Vol. 2)" → `the-wolves-vol-2`). If the slug collides with an existing `id`, append `-2`, `-3`, … Then add the `title`, the `root` (relative to the workspace root), `volume` (1 unless part of a series), and the denormalized `mode` / `next_action` copied from the new sidecar.
   - Validate with `../scripts/validate.sh registry-check <workspace_root>`.

8. **Report** what was created, where the project root lives, the folder structure, and what the next step is (typically: run `/develop-edit` or specific passes).

If a manuscript file path is provided: @$1
If a project name is provided as text, use it for the project directory and file naming.
