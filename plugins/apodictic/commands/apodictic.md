---
description: Capability index — every APODICTIC command grouped by workflow stage, the Firewall, and where your project stands
argument-hint: no argument
allowed-tools: Read, Glob, Bash
---

# /apodictic — capability index

Print the reference below, then stop. This command is a **flat index, not a router**: it never asks intake questions, never selects a workflow, and never writes any file or state. For guided routing, point the user to `/start`. Output goes to chat only.

**Before printing:** glob `../commands/*.md`. If any command file is **not** listed in the index below, append it under a final "Newer commands (not yet grouped)" line with its `description:`; if an indexed command's file is missing, omit that line. (This keeps the index self-healing for added/removed commands — only the *grouping* of a genuinely new command needs a human.)

<!-- keep in sync: one entry per file in commands/ — the glob check above catches presence, not grouping -->

---

## What APODICTIC is

A developmental editor that **listens before diagnosing**: it infers the manuscript's own contract (genre, promise, controlling idea) from the text, then diagnoses the draft against that contract — structure, pacing, character, argument, voice — and routes you to revision.

**The Firewall — diagnose, don't rewrite.** APODICTIC identifies problems and *classes* of solution — including which structural elements are missing or mis-weighted — but never drafts your prose or scripts the specific content that fills them (the events, characters, dialogue, or evidence). Naming a needed beat is diagnosis; writing it is yours. The author creates; the system analyzes. (Canonical: `../skills/core-editor/references/firewall.md`.) Per-module variants: the revision coach gives **guidance without specification** — it names the architectural weakness, you choose the words (`../skills/revision-coach/SKILL.md` §The Coaching Firewall); `/legal-risk` **flags, doesn't practice law** — it names exposure areas and routes serious items to counsel, never rendering a legal conclusion.

## Commands, by workflow stage

**Start here**
- `/start` — the recommended entry point; routes you in two or three questions (zero for a resumed project).
- `/apodictic` — this index.

**Before a draft exists**
- `/pre-writing` — turn an idea into a draftable structure; no manuscript required.
- `/plot-coach` — choose or repair a plot structure (pre-draft, or a stuck draft), drawing on the spine library.
- `/new-project` — set up project scaffolding, the contract, and diagnostic state.

**Diagnose a draft** — full or targeted diagnosis routes through `/start`.
- `/audit` — run a named specialized audit (no argument lists the full set).
- `/research` — internet-enabled verification modes (no argument lists them all).

**Revise after a diagnosis**
- `/coach` — session planning, stuck-point coaching, momentum tracking, deadline calendars.
- `/triage-feedback` — sort, validate, and prioritize external (beta-reader / critique / editor) feedback.
- `/reader-questions` — turn the diagnosis's open uncertainties into a targeted, non-leading beta-reader questionnaire.

**Risk & submission**
- `/legal-risk` — flag defamation / privacy / rights-clearance exposure for a lawyer's review (flags, never adjudicates).
- `/ready` — the full "is this ready to submit?" workflow, ending in a verdict.

**Projects**
- `/projects` — list and tidy your registered projects (the registry surface).

The commands sit on six capability areas: the diagnostic engine and its passes, the deep-dive audits and internet-research modes, the nonfiction argument engine, the spine library, the pre-writing pathway, and the revision coach.

## Where am I / what's next

- `/projects` — lists every registered project with its mode, next action, and last-touched time (from the workspace registry at `.apodictic/registry.json`).
- `/start <project>` — resumes a specific book, state-driven, with zero intake questions.
- Each project's place on the lifecycle rail (`cold → blocked_gate → execution → pre_writing → submission → revising → diagnosed → diagnosing`, first match wins) derives from its sidecar: `../scripts/validate.sh lifecycle-node <project-root>/Diagnostic_State.meta.json`. The model is documented in `docs/project-addressability.md`.

If a workspace registry is found, print a short **read-only** table — project title, lifecycle node, next action — plus the matching `/start <id>` resume line. Do **not** rebuild or rewrite the registry; that is `/projects`' job. If no `.apodictic/` workspace exists (or `python3`/`validate.sh` is unavailable), skip the table and say: *"No registered projects found — `/new-project` creates one, `/start` routes you."* Never fail or block on a tool.

## Visual maps & key docs (point, don't rebuild)

- `overview-dashboard.html` — a static visual map of the whole system: workflows, macro blocks, pass blocks, audit families, and the Firewall in plain language.
- `route-explorer.html` — an interactive walkthrough of the `/start` router: answer the three intake questions and see where every combination routes.
- `project-dashboard.html` — a render-only snapshot of your projects on the lifecycle rail (paste the registry payload `/projects` produces).
- `AUDIT_SELECTION_MATRIX.md` — the routing chart for passes, audits, tags, and research modes. `README.md` — the full plugin overview.

---

To actually *do* something: `/start`.
