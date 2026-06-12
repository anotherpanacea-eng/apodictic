# QoL: `/apodictic` — Capability Index Command (spec)

**Status:** spec for review → build. Do not implement until reviewed.
**Problem:** APODICTIC ships 15 slash commands and 5 skills but no non-interactive "what can I do / where do I start / what's my current state" reference. `/start` is an interactive *router* (it asks 2–3 questions and sends you somewhere); the README command list covers only the 11 registry-listed commands (it omits `/projects`, `/legal-risk`, `/triage-feedback`, `/reader-questions`). There is no single surface a user can glance at.
**Goal:** one new command that *prints* a concise, grouped capability index — every command with a one-line "when to use," the Firewall in plain language, how to find your current project state, and pointers to the existing HTML maps. Reference, not router.

---

## 1. Command name: `/apodictic`

Decision: the command file is `plugins/apodictic/commands/apodictic.md`, invoked as `/apodictic`.

Rationale:

- **`/help` is off the table.** Claude Code has a built-in `/help`. Plugin commands are namespaced (`/apodictic:help` style), and a plugin command colliding with a built-in is at best confusing, at worst shadowed — bare `/help` would not reliably reach this command. *Honesty note:* exact built-in-vs-plugin precedence was not verified at runtime in this repo; the collision risk alone is disqualifying since collision-free names cost nothing.
- **`/overview` collides conceptually** with `overview-dashboard.html` (README §Selection Guide already says "See `overview-dashboard.html` for a visual map") — users would expect it to open the dashboard.
- **`/commands` undersells** — the index also covers skills, the Firewall, project state, and the HTML maps. **`/guide` is generic** and likely to collide with other installed plugins.
- **`/apodictic` is collision-proof** (it's the plugin's unique name), and maximally discoverable: a user who remembers nothing except "I installed APODICTIC" finds it by typing `/apod`. Nothing in the repo (README, ROADMAP, release-registry) reserves another name; ROADMAP's "Doc sync" item speaks only of a generic "help surface."
- **Known wart, accepted:** if this command were ever added to `release-registry.json` (it should not be — §3), `build-codex.mjs` would generate a wrapper skill named `apodictic-apodictic` (wrapper name = `${wrapperPrefix}-${slug}`). Staying unregistered avoids this; if it is ever registered, rename or special-case then.

## 2. The command file

`plugins/apodictic/commands/apodictic.md`. This is a prose command in the house pattern (cf. `commands/triage-feedback.md`, `commands/projects.md`: YAML frontmatter + a markdown body of instructions the agent follows).

### Frontmatter

```yaml
---
description: Capability index — every APODICTIC command grouped by workflow stage, the Firewall, and where your project stands
argument-hint: no argument
allowed-tools: Read, Glob, Bash
---
```

`allowed-tools` decision: **`Read, Glob, Bash`** (the minimal set in this codebase — every existing command grants at least Read/Bash/Glob; this one deliberately omits Write/Edit because it must never produce artifacts or touch state).

- `Glob` + `Read` — locate the workspace `.apodictic/registry.json` (walk up from cwd, same discovery rule as `/projects`) and read it for the optional "your projects" section; also the §5 drift check over `../commands/*.md`.
- `Bash` — optionally run `../scripts/validate.sh lifecycle-node <project-root>/Diagnostic_State.meta.json` to report each project's node (same call `/start` Step 0.5 makes).
- **Degrade rule (must be stated in the body):** if no `.apodictic/` workspace is found, or python3/validate.sh is unavailable, print the static index unchanged and say "No registered projects found — `/new-project` creates one, `/start` routes you." Never fail, never block on tools.

### Body — section-by-section (draft text; builder may tighten prose but must keep section order, the never-routes rule, and all 15 commands)

**Header + contract (top of body):**

> `# /apodictic — capability index`
>
> Print the reference below, then stop. This command is a *flat index*, not a router: it never asks intake questions, never selects a workflow, never writes any file or state. For guided routing, point the user to `/start`. Output goes to chat only.

**(a) What APODICTIC is + the Firewall.** One paragraph adapted from `README.md` ("Developmental editing that listens before diagnosing" — infers the manuscript's contract from the text, then diagnoses against it), then the Firewall in plain language with its per-module variants:

> **The Firewall — diagnose, don't rewrite.** APODICTIC identifies problems and classes of solution; it never invents content — no new plot events, characters, dialogue, or imagery. The author creates; the system analyzes. (Canonical: `../skills/core-editor/SKILL.md` §The Firewall.) Variants: the revision coach gives **guidance without specification** — it names the architectural weakness, you choose the words (`../skills/revision-coach/SKILL.md` §The Coaching Firewall); `/legal-risk` **flags, doesn't practice law** — it names exposure areas and routes serious items to counsel, never renders legal conclusions.

**(b) Commands grouped by workflow stage** — all 15 + this one, each with a one-liner reusing the file's `description:`/the registry `writerQuestion`. Proposed grouping (every command appears exactly once):

| Group | Commands |
|---|---|
| **Start here** | `/start` — recommended entry point; routes you in 2–3 questions (zero for a resumed project). `/apodictic` — this index. |
| **Before a draft exists** | `/pre-writing` — idea → draftable structure, no manuscript required. `/plot-coach` — choose or fix a plot structure (pre-draft or stuck draft). `/new-project` — set up project scaffolding + contract + diagnostic state. |
| **Diagnose a draft** | `/develop-edit` — full development edit. `/diagnose` — quick targeted diagnostic on one concern. `/audit` — run a named specialized audit (no argument lists all 34). `/research` — internet-enabled verification modes (no argument lists all 6). |
| **Revise after diagnosis** | `/coach` — session planning, stuck points, momentum, deadlines. `/revision-plan` — compatibility alias for `/coach`. `/triage-feedback` — sort/validate/prioritize external feedback. `/reader-questions` — turn the diagnosis's open uncertainties into a beta-reader questionnaire. |
| **Risk & submission** | `/legal-risk` — flag defamation/privacy/rights-clearance exposure for legal review. `/ready` — full "is this ready to submit?" workflow with verdict. |
| **Projects** | `/projects` — list and tidy registered projects (the registry surface). |

Plus one orienting line on the 5 skills behind the commands: core-editor (diagnostic engine, 11 passes), specialized-audits (34 audits + 6 research modes), plot-architecture (50 spines), pre-writing-pathway, revision-coach. *(Write skill names in plain text or as full `../skills/<name>/SKILL.md` paths — see §3 build-safety.)*

**(c) Where am I / what's next.**

> - `/projects` — lists every registered project with mode, next action, last touched (registry: `.apodictic/registry.json` at the workspace root).
> - `/start <project>` — resumes a specific book state-driven, zero intake questions.
> - Each project's position on the lifecycle rail (`cold → blocked_gate → execution → pre_writing → submission → revising → diagnosed → diagnosing`, first match wins) derives from its sidecar: `../scripts/validate.sh lifecycle-node <project-root>/Diagnostic_State.meta.json`. See `docs/project-addressability.md` (repo) for the model.
>
> Then, *if* a workspace registry was found (degrade rule above): print a short live table — project title, lifecycle node, `next_action` — and the matching `/start <id>` resume command. Read-only; do not rebuild or rewrite the registry (that's `/projects`' job).

**(d) Visual maps & key docs** (point, don't rebuild — mirror README §Selection Guide):

> - `overview-dashboard.html` — static visual map of the whole system: workflows, macro blocks, pass blocks, audit families, the Firewall in user-facing language.
> - `route-explorer.html` — interactive walkthrough of the `/start` router: answer the three intake questions, see where every combination routes.
> - `project-dashboard.html` — render-only snapshot of your projects on the lifecycle rail (paste the registry payload `/projects` produces).
> - `AUDIT_SELECTION_MATRIX.md` — routing chart for passes, audits, tags, research modes. `README.md` — full plugin overview.

Closing line: "To actually do something: `/start`."

## 3. Registration / build-safety

**Least-surface path (recommended): ship the `.md` only.** Precedent: `/projects`, `/legal-risk`, `/triage-feedback`, `/reader-questions` exist solely as `commands/*.md` — they are *not* in `release-registry.json`'s `commands` array (it lists 11), and both builds pass. The builds copy `plugins/apodictic/` wholesale, so the new file ships to the codex/antigravity trees automatically.

- **Do not add** a `release-registry.json` `commands[]` entry. If anyone does, `build-codex.mjs` (`buildCommandMappings`, scripts/build-codex.mjs:103-106) throws `Missing codex.commandBaseSkills mapping` unless **both** `codex.commandBaseSkills` and `antigravity.commandBaseSkills` get an entry. If registered later anyway, the base skill is **core-editor** (it's the orientation/state surface, like `/start`/`/projects`) — and see the `apodictic-apodictic` wrapper-name wart in §1.
- **Codex self-check content rules** (the generated-tree scan in `build-codex.mjs` runs over *all* command docs, including unregistered ones — these will fail the build if violated):
  - No backticked shorthand paths: never `` `references/...` ``; never bare backticked `specialized-audits` / `plot-architecture` / `pre-writing-pathway`. Use full `../skills/<skill>/...` paths or plain text.
  - No `Outputs/[Project]` legacy wording.
  - No Claude-specific runtime phrasing anywhere in the body (the scan rejects e.g. "Claude loads the full audit", "After diagnosis, you work with Claude directly", "Claude Opus"). Write host-neutrally ("the system", "the editor").
- **Known parity quirk (accepted, matches precedent):** `rewriteGeneratedDocs` rewrites only the 11 registered slash names to `apodictic-*` wrapper names in the generated codex tree; mentions of the 4 unregistered commands (and `/apodictic` itself) keep slash form — same posture as today's `/projects` mentions, covered by `NON_PARITY_NOTES.codex.md` note 1 ("no native slash-command runtime").
- **No mirror concern:** `commands/` is not in the `scripts/` ↔ `plugins/apodictic/scripts/` mirrored set; `check-mirror` is unaffected.
- **Changelog:** add `changelog.d/qol-capability-index.md`, one `### ` thematic section per house style (e.g. `### Commands — Capability Index`), first non-blank line is the header.
- **Recommended (small, optional):** one line in `plugins/apodictic/README.md` §Commands "Start here" block: `` `/apodictic` — What can this plugin do? `` Defer if the reviewer wants zero README churn.

## 4. Staleness (single source of truth)

A hand-maintained command list *will* drift — the README's already has (4 of 15 commands missing), and the validator-count drift was the same failure class. Honest assessment of the options:

- **Derive from `release-registry.json` `commands[]`?** No — it covers 11/15; the index would be stale on day one. (ROADMAP's "Doc sync across all public surfaces… generated from the registry" is the right long-term fix, but it requires backfilling the registry + commandBaseSkills for 4 commands first; out of scope here.)
- **Derive fully at runtime from frontmatter?** The agent *could* Glob+Read all of `../commands/*.md` and print live `description:` lines, but grouping and "when to use" curation can't be derived from one-line descriptions, and 16 file reads per invocation is wasteful for a glance-reference.
- **Recommended: curated list + runtime drift check.** The body keeps the hand-written grouped index, and instructs: *"Before printing, Glob `../commands/*.md`. If any command file is not in the index below, append it under a 'Newer commands (not yet grouped)' line with its `description:`; if an indexed command's file is missing, omit it."* One Glob (plus Reads only for deltas) makes the index self-healing for additions/removals; only the *grouping* of a new command needs a human. Reinforce with an HTML comment at the top of the index section: `<!-- keep in sync: one entry per file in commands/ — the Glob drift check above only catches presence, not grouping -->`.

## 5. Verification

1. `bash scripts/validate.sh --check-all` — the CI gate (run first, per AGENTS.md review practice).
2. `node scripts/build-codex.mjs --self-check` — proves the unregistered-command path holds and the body passes the shorthand-path / legacy-wording / host-neutrality scans.
3. `node scripts/build-antigravity.mjs --self-check`.
4. `node scripts/assemble-changelog.mjs --check` — fragment format.
5. Manual review: all 15 existing commands (+ `/apodictic` itself) appear exactly once; one-liners match each file's `description:` in substance; firewall statements match the canonical sources (core-editor SKILL.md §The Firewall, revision-coach SKILL.md §The Coaching Firewall, commands/legal-risk.md); the index is scannable in one screenful-ish; invoking it with no workspace prints the static index without errors or questions.
6. Manual behavior check: the command never asks a question, never writes a file, and the "your projects" table appears only when a registry exists.

## 6. Non-goals

- **Not a router.** No intake questions, no workflow selection, no two-option prompts — `/start` owns routing.
- **Not a dashboard rebuild.** Points to `overview-dashboard.html` / `route-explorer.html` / `project-dashboard.html`; duplicates none of their content.
- **Not a registry manager.** Reads the registry at most; rebuild-on-read and tidying stay in `/projects`.
- **No state writes** of any kind (no Diagnostic_State, no run folders, no registry writes).
- **No registry/doc-sync backfill** for the 4 unregistered commands (worthwhile, separate change per ROADMAP "Doc sync").
