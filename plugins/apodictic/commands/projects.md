---
description: List and manage your APODICTIC projects
allowed-tools: Read, Write, Edit, Bash, Glob
---

# /projects — list and manage registered projects

Management surface for the project registry. Routing lives on `/start`; this command is for *seeing and tidying* your projects, not for entering a workflow. (Project Addressability, Increment 2 — see `../skills/core-editor/references/output-structure.md` §Project Registry and `docs/project-addressability.md`.)

## Registry location

The registry lives at `.apodictic/registry.json` in the **workspace root** — the nearest ancestor of the current directory that contains a `.apodictic/` folder (discovered by walking up from cwd, the way tools locate `.git`). Never the plugin repo or plugin cache; `~` is not used (sandbox-unsafe). Schema: `apodictic.project_registry.v1`, one `apodictic.project_entry.v1` per project.

## Procedure

1. **Locate the workspace + registry.** Walk up from cwd for a `.apodictic/` dir. If none exists, report that no workspace is initialized yet and that `/new-project` (or `/start <path-to-project>`) will create one. Stop here.

2. **Rebuild-on-read (cache hygiene).** The registry is a *recomputable cache* over the per-project `Diagnostic_State.meta.json` sidecars — each sidecar is canonical, the registry is denormalized. Before listing, reconcile: scan the workspace root for `Diagnostic_State.meta.json` sidecars AND `*_Structural_Plan_*.md` artifacts (pre-writing projects carry a minimal sidecar). For each project found, refresh the denormalized `mode` / `next_action` / `last_touched` from its sidecar; add any unregistered project; flag any registered `root` that no longer resolves. Write the refreshed registry.

3. **Validate.** Run `../scripts/validate.sh registry-check <workspace_root>` (or the inline equivalent). R1 (schema) and R4 (duplicate id) are errors to fix; R2 (missing sidecar) and R3 (drift) are advisory — the rebuild in step 2 should already have resolved drift toward the sidecars.

4. **List.** Present a table: **title**, **where it stands** (the lifecycle node, derived per `docs/project-addressability.md` Increment 3; until that lands, show `mode` + `next_action.key`), and **last touched**. Offer to bind one — hand off to `/start <project>`.

5. **Manage (only when asked).** Rename a project's `title`, drop a stale entry whose `root` no longer resolves, or correct an `id`. `/projects` edits the registry **index** only.

6. **Visual snapshot (only when asked).** To populate `plugins/apodictic/project-dashboard.html`, emit an **extended registry payload**: the `apodictic.project_registry.v1` object with, per project, the **pre-computed** `node` (run `../scripts/lifecycle_node.py` per project — the dashboard does not re-derive it, since `diagnosed` needs a disk read the sandbox can't do) and `next_action` (the leverage-ladder string), plus a top-level `snapshot_ts`. The user pastes that payload into the dashboard's textarea; it renders the lifecycle rail + "what now?" + the `/start <id>` launch line. It is a **snapshot** — the dashboard cannot read the disk or run `/start` itself.

## Firewall & write discipline

`/projects` reads and tidies the registry index. It never mutates a project's `Diagnostic_State.md`, manuscript, or run artifacts, never deletes project files, and never writes outside the workspace `.apodictic/` directory or into the plugin repo / cache.
