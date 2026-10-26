# Craft Syllabus (Learning Mode)

**Status:** v0.1
**For:** APODICTIC Revision Coach, `/coach learn`
**Depends on:** `structural-prompt-library.md`, the craft audit files named below

---

## Purpose

The audit files already define one craft concept each: what it is, how it fails, and how it differs from its neighbours. Learning Mode teaches those concepts one lesson at a time, on the writer's own pages, so a writer can build the skill an audit checks for instead of only receiving its findings.

Load this file only in Learning Mode. Normal runs and the other coach modes never open it.

---

## One lesson per session

1. **Pick the lesson.** Default to the first lesson in the sequence that `Syllabus_Progress.md` does not show as cleared or skipped. The writer may pick any lesson instead. If `Diagnostic_State.md` exists and its highest-leverage open finding matches a lesson, offer that lesson first, since practice on a live problem sticks.
2. **Teach (about 400 words).** Read only the concept file's opening section (its Purpose or core-problem section, through the named failure modes and the non-duplication boundaries). Do not load the scoring procedure, logic gates, or output templates. Explain the concept in plain language, name its main failure, and say how it differs from the nearest neighbouring concept. If the writer has named a passage, point to where the concept is visible in it, as an observation and never as a finding.
3. **Exercise.** Give one prompt from the lesson's prompt family in `structural-prompt-library.md`. It must pass the 5-part firewall, with one adaptation: in Learning Mode "state-grounded" means grounded in the lesson's concept applied to a passage the writer named. Include the clinamen clause and end with the structural self-check. Of the No-Prompt Zones, only depletion and feedback saturation apply here: if the writer is depleted or saturated with feedback, teach and stop. The missing-state-file zone does not apply in Learning Mode.
4. **Assignment.** Name the command that tests the skill on the writer's own pages (the Assignment column). The writer runs it; the coach does not run audits or produce findings (Delegation principle). Lessons with no audit use the process named instead.
5. **Record.** Update `Syllabus_Progress.md` (below).

The writer can stop after any step. A lesson that was taught but not tested is `practiced`, which is a fine place to leave it.

---

## Progress and clearing

Keep `Syllabus_Progress.md` at the project root (or the folder the writer names when there is no project). Never write it to the plugin.

```markdown
# Syllabus Progress
Cleared 3 of 15 · Next: L5 Choosing a structure

| Lesson | Status | Date | Note |
|---|---|---|---|
| L2 Stakes | cleared | 2026-10-25 | F-07 revised |
```

Statuses: `open`, `practiced` (taught and exercised), `cleared`, `skipped`.

A lesson is **cleared** when its assignment shows the skill on the page:
- the assignment audit's finding for this concept reaches `revised` in `execution.finding_states` (or carries a resolved marker in the latest revision report), or
- the assignment audit, run on the chosen pages, raises no finding for this concept. The writer tested out.

Process lessons (L5, L14, L15) clear when the named process is completed once.

Keep the game light. Show the cleared count and the next lesson as the writer's place in the course, never as a judgment of the writer (the same transference-health rule as Coaching History in `../SKILL.md`). Do not add scores, streaks, or deadlines: pressure is itself a block type (`writers-block-taxonomy.md`), and the syllabus should never become one.

---

## Sequence

Concept paths are relative to `skills/`. Deeper reading points to the level-setting research briefs in the repository's `docs/` folder. They are not shipped in the plugin and are not loaded; offer the link to a writer who wants the theory behind a lesson.

### Fiction and narrative track

| # | Lesson | Concept file | Prompt family | Assignment | Deeper reading |
|---|---|---|---|---|---|
| **Unit 1 · The promise** |
| L1 | Promise and reader contract | `core-editor/references/promise-contract.md` | Perspective | `/audit shelf` | — |
| **Unit 2 · The engine** |
| L2 | Stakes | `narrative-craft-audits/references/craft/stakes-system.md` | Constraint | `/audit stakes` | `stakes-system-level-setting.md` |
| L3 | Decision pressure | `narrative-craft-audits/references/craft/decision-pressure.md` | Inversion | `/audit decision-pressure` | `decision-pressure-level-setting.md` |
| L4 | Force and consequence | `narrative-craft-audits/references/craft/force-architecture.md` | Temporal | `/audit force` | `force-architecture-level-setting.md` |
| **Unit 3 · Structure** |
| L5 | Choosing a structure | `plot-architecture/references/plot-selection-coaching.md` | Temporal | `/plot-coach` (selection) | — |
| L6 | The spine | `plot-architecture/references/plot-architecture-audit.md` | Scale-Shift | `/plot-coach` (diagnosis) | — |
| L7 | Scene turns | `narrative-craft-audits/references/craft/scene-turn.md` | Isolation | `/audit scene-turn` | — |
| **Unit 4 · People** |
| L8 | Character architecture | `narrative-craft-audits/references/craft/character-architecture.md` | Constraint | `/audit character` | — |
| L9 | Interiority under pressure | `narrative-craft-audits/references/craft/interiority-preservation.md` | Perspective | `/audit interiority` | — |
| L10 | Emotional craft | `narrative-craft-audits/references/craft/emotional-craft.md` | Isolation | `/audit emotional-craft` | — |
| **Unit 5 · Prose** |
| L11 | Load-bearing prose | `narrative-craft-audits/references/craft/literary-craft.md` | Isolation | `/audit literary-craft` | `literary-craft-level-setting.md` |
| L12 | Compression | `narrative-craft-audits/references/craft/compression-audit.md` | Deletion | `/audit compression` | `compression-audit-level-setting.md` |
| **Unit 6 · Genre elective** |
| L13 | Your genre's contract | the genre or tag file for the book's shelf (see `/audit` list) | Constraint | `/audit <genre or tag>` | the matching brief, if one exists (for example `grimdark-level-setting.md`, `mystery-thriller-architecture-level-setting.md`, `cozy-tag-level-setting.md`) |
| **Unit 7 · Revision practice** |
| L14 | Using feedback | `revision-coach/references/feedback-triage.md` | none | `/triage-feedback` on one round of notes | — |
| L15 | Getting unstuck | `revision-coach/references/writers-block-taxonomy.md` | per block type | `/coach stuck` once | `writers-block-rut-breaking-level-setting-codex54.md` |

### Argument track

For op-eds, briefs, testimony, and other argument-shaped nonfiction. L14 and L15 apply here too.

| # | Lesson | Concept file | Prompt family | Assignment | Deeper reading |
|---|---|---|---|---|---|
| A1 | Claim, warrant, objection | `argument-audits/references/craft/dialectical-clarity.md` | Isolation | `/audit dialectical` | `dialectical-clarity-level-setting.md` |
| A2 | The hostile reader | `argument-audits/references/craft/argument-red-team.md` | Perspective | `/audit argument-red-team` | `argument-red-team-level-setting.md` |
| A3 | Persuading a real audience | `argument-audits/references/craft/argument-persuasion.md` | Scale-Shift | `/audit argument-persuasion` | `argument-persuasion-level-setting.md` |
| A4 | Evidence that holds | `argument-audits/references/craft/argument-evidence.md` | none (planning) | `/audit argument-evidence` | `adversarial-evidence-level-setting.md` |

A2 to A4 need the `Argument_State.md` that A1's assignment produces, so keep that order.

Deeper reading links: `https://github.com/anotherpanacea-eng/apodictic/blob/main/docs/<file>`.
