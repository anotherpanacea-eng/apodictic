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

1. **Pick the lesson.** If the last lesson is `practiced` and its assignment has since run, apply the clear rule to it first. Then default to the first lesson in the sequence that `Syllabus_Progress.md` does not show as cleared or skipped. The writer may pick any lesson instead. If `Diagnostic_State.md` exists and its highest-leverage open finding matches a lesson, offer that lesson first, since practice on a live problem sticks.
2. **Teach (about 400 words).** Read only the concept file's opening section: §1 or Purpose, through its non-duplication boundaries where it has them, and stop there. Where the Sequence names a teach range for the lesson, read that range instead. Do not load the scoring procedure, logic gates, or output templates outside it. Explain the concept in plain language, name its main failure, and say how it differs from the nearest neighbouring concept. If the writer has named a passage, point to where the concept is visible in it, as an observation and never as a finding.
3. **Exercise.** Give one prompt from the lesson's prompt family in `structural-prompt-library.md`. It must pass the 5-part firewall, with one adaptation: in Learning Mode "state-grounded" means grounded in the lesson's concept applied to a passage the writer named. Include the clinamen clause and end with the structural self-check. Of the No-Prompt Zones, only depletion and feedback saturation apply here: if the writer is depleted or saturated with feedback, teach and stop. The missing-state-file zone does not apply in Learning Mode. Delivery rule 2 and the family selection rule do not apply either: asking for a lesson is asking for the experiment. Read "diagnosed" in a clinamen as the lesson's concept, and for Inversion name the passage's habitual move neutrally. If the family is `none` or `none (planning)`, give no prompt: the assignment is the practice.
4. **Assignment.** Name the command that tests the skill on the writer's own pages (the Assignment column). The writer runs it; the coach does not run audits or produce findings (Delegation principle). Lessons with no audit use the process named instead. Without a diagnosis, give the full invocation text, so the audit sees these terms in its arguments: run on the chosen pages at passage scale; missing pass inputs and run-sequence prerequisites are noted, not required; write only the run folder (A1's `/audit dialectical` also writes the `Argument_State.md` that A2 to A4 need).
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
| L2 Stakes | cleared | 2026-10-25 | Ch 3 re-run after revision: no Should-Fix stakes finding |
```

The argument track counts 6 lessons (A1 to A4, L14, L15) instead of 15.

Statuses: `open`, `practiced` (taught, and exercised where the lesson has an exercise), `cleared`, `skipped`.

A lesson is **cleared** when its assignment, run on the chosen or revised pages, raises no Should-Fix-or-higher finding for this concept on the channels those pages can show. Name any untested channels in the Note. A flag the audit classes as intentional does not count.

Where the assignment covers more than the lesson's concept, only these count: L6, a STRUCTURAL BREAK on the primary spine's gates; L8, the Part 3 agency flags; L11, the PA flags; A1, the CL, WR and OB codes. A2 clears when a re-run leaves no Fatal or Major vulnerability. In A3, a PS signal counts as a finding when the memo classifies its recommendation as a Healthy Recalibration.

Process lessons (L5, L14, L15) clear when the named process is completed once.

Keep the game light. Show the cleared count and the next lesson as the writer's place in the course, never as a judgment of the writer (the same transference-health rule as Coaching History in `../SKILL.md`). Do not add scores, streaks, or deadlines: pressure is itself a block type (`writers-block-taxonomy.md`), and the syllabus should never become one.

---

## Sequence

Concept paths are relative to `skills/`. Deeper reading points to the level-setting research briefs in the repository's `docs/` folder. They are not shipped in the plugin and are not loaded; offer the link to a writer who wants the theory behind a lesson.

### Fiction and narrative track

| # | Lesson | Concept file | Prompt family | Assignment | Deeper reading |
|---|---|---|---|---|---|
| **Unit 1 · The promise** |
| L1 | Promise and reader contract | `genre-reader-audits/references/craft/shelf-positioning.md` | Perspective | `/audit shelf` (Fast Pass + Part 2) | — |
| **Unit 2 · The engine** |
| L2 | Stakes | `narrative-craft-audits/references/craft/stakes-system.md` | Constraint | `/audit stakes` | `stakes-system-level-setting.md` |
| L3 | Decision pressure | `narrative-craft-audits/references/craft/decision-pressure.md` | Inversion | `/audit decision-pressure` | `decision-pressure-level-setting.md` |
| L4 | Force and consequence | `narrative-craft-audits/references/craft/force-architecture.md` | Temporal | `/audit force` | `force-architecture-level-setting.md` |
| **Unit 3 · Structure** |
| L5 | Choosing a structure | `plot-architecture/references/plot-selection-coaching.md` | Temporal | `/plot-coach` (pre-drafting steps 1–3 run against your draft, or the stuck-draft steps if you are stuck) | — |
| L6 | The spine | `plot-architecture/references/plot-architecture-audit.md` | Scale-Shift | `/plot-coach` asking for spine diagnosis (`plot-architecture/SKILL.md` §Diagnostic Process) | — |
| L7 | Scene turns | `narrative-craft-audits/references/craft/scene-turn.md` | Isolation | `/audit scene-turn` | — |
| **Unit 4 · People** |
| L8 | Character architecture | `narrative-craft-audits/references/craft/character-architecture.md` | Constraint | `/audit character` | — |
| L9 | Interiority under pressure | `narrative-craft-audits/references/craft/interiority-preservation.md` | Perspective | `/audit interiority` | — |
| L10 | Emotional craft | `narrative-craft-audits/references/craft/emotional-craft.md` | Isolation | `/audit emotional-craft` | — |
| **Unit 5 · Prose** |
| L11 | Load-bearing prose | `narrative-craft-audits/references/craft/literary-craft.md` | Isolation | `/audit literary-craft` | `literary-craft-level-setting.md` |
| L12 | Compression | `narrative-craft-audits/references/craft/compression-audit.md` | Deletion | `/audit compression` | `compression-audit-level-setting.md` |
| **Unit 6 · Genre elective** |
| L13 | Delivering your genre's promise | the file for the book's shelf under `genre-reader-audits/references/genre/` or `genre-reader-audits/references/tag/` (see `/audit` list) | Constraint | `/audit <genre or tag>` | the matching brief, if one exists (for example `grimdark-level-setting.md`, `mystery-thriller-architecture-level-setting.md`, `cozy-tag-level-setting.md`) |
| **Unit 7 · Revision practice** |
| L14 | Using feedback | `revision-coach/references/feedback-triage.md` | none | `/triage-feedback` on one round of notes | — |
| L15 | Getting unstuck | `revision-coach/references/writers-block-taxonomy.md` | none | `/coach stuck` once | `writers-block-rut-breaking-level-setting-codex54.md` |

Teach ranges, where the opening section is thin or the concept sits later in the file:
- L1: §Purpose, §Part 1, and the 10% Threshold gate in §Part 2.
- L5: §Purpose and the symptom table in §Phase 5, Step 1.
- L6: §Purpose and §Severity Levels, plus the Plot Architecture vs. Pass 2 boundary in `plot-architecture/SKILL.md`.
- L8: §Purpose, plus §Part 3's Definitions and Puppet Detection.
- L14: §When to use through §The structured record.
- L15: §Primary Block Types through §Perfectionism Modifier.

L13: skip it when the book's shelf has no genre or tag audit in the `/audit` list (for example, general romance or literary fiction).

L15's assignment needs a `Diagnostic_State.md` (`/coach` routes to `/start` without one); without it the lesson stops at `practiced`.

### Argument track

For op-eds, briefs, testimony, and other argument-shaped nonfiction. L14 and L15 apply here too.

| # | Lesson | Concept file | Prompt family | Assignment | Deeper reading |
|---|---|---|---|---|---|
| A1 | Claim, warrant, objection | `argument-audits/references/craft/dialectical-clarity.md` | Isolation | `/audit dialectical` | `dialectical-clarity-level-setting.md` |
| A2 | The hostile reader | `argument-audits/references/craft/argument-red-team.md` | Perspective | `/audit argument-red-team` | `argument-red-team-level-setting.md` |
| A3 | Persuading a real audience | `argument-audits/references/craft/argument-persuasion.md` | Scale-Shift | `/audit argument-persuasion` | `argument-persuasion-level-setting.md` |
| A4 | Evidence that holds | `argument-audits/references/craft/argument-evidence.md` | none (planning) | `/audit argument-evidence` | `adversarial-evidence-level-setting.md` |

A1's teach range: §Purpose, the opening paragraph of §Step 4 (what a warrant is), and §Common Patterns.

A2 to A4 need the `Argument_State.md` that A1's assignment produces, so keep that order. If you revised after A1, re-run `/audit dialectical` before the next lesson's audit.

Deeper reading links: `https://github.com/anotherpanacea-eng/apodictic/blob/main/docs/<file>`.
