# Craft Syllabus (Learning Mode)

**Status:** v0.1
**For:** APODICTIC Revision Coach, `/coach learn`
**Depends on:** `structural-prompt-library.md`, the craft audit files named below

---

## Purpose

The audit files already define one craft concept each: what it is, how it fails, and how it differs from its neighbours. Learning Mode teaches those concepts one lesson at a time, on the writer's own pages, so a writer can build the skill an audit checks for instead of only receiving its findings.

Learning Mode loads this file; Session Planning may read only its Sequence tables, to offer a lesson door. Normal runs and the other coach modes never open it.

---

## One lesson per session

1. **Pick the lesson.** If the last lesson is `practiced` and its assignment has since run, apply the clear rule to it first. The writer may name any lesson. When the writer names none, there is no default: offer up to three doors and let the writer choose.
   - **A live problem.** If `Diagnostic_State.md` exists and its highest-leverage open finding matches a lesson, offer that lesson first, since practice on a live problem sticks.
   - **A neighbour.** One See also of the last lesson on the Trail (below), or the first lesson in the writer's track if no lesson has been taken.
   - **The map.** The Sequence tables, as a list to browse.

   If the writer says "next" or "just pick", take the first lesson in the writer's track, in Sequence order, that `Syllabus_Progress.md` does not show as cleared or skipped.
2. **Teach (about 400 words).** Read only the concept file's opening section: §1 or Purpose, through its non-duplication boundaries where it has them, and stop there. Where the Sequence names a teach range for the lesson, read that range instead. Do not load the scoring procedure, logic gates, or output templates outside it. Explain the concept in plain language, name its main failure, and say how it differs from the nearest neighbouring concept. If the writer has named a passage, point to where the concept is visible in it, as an observation and never as a finding. Close by naming the lesson's See also entries with their reasons and offering its deeper reading. The writer may take any See also lesson next.
3. **Exercise.** Give one prompt from the lesson's prompt family in `structural-prompt-library.md`. It must pass the 5-part firewall, with one adaptation: in Learning Mode "state-grounded" means grounded in the lesson's concept applied to a passage the writer named. Include the clinamen clause and end with the structural self-check. Of the No-Prompt Zones, only depletion and feedback saturation apply here: if the writer is depleted or saturated with feedback, teach and stop. The missing-state-file zone does not apply in Learning Mode. Delivery rule 2 and the family selection rule do not apply either: asking for a lesson is asking for the experiment. Read "diagnosed" in a clinamen as the lesson's concept, and for Inversion name the passage's habitual move neutrally. If the family is `none` or `none (planning)`, give no prompt: the assignment is the practice.

   When the lesson has an exercise and the writer has named no passage, try these in order:
   1. Ask for a paragraph of the writer's own prose. Any project counts, and this is preferred.
   2. A public-domain passage, only when both of these hold. If either can't be established, skip this option.
      - **Its exact text is in the session.** The writer pasted it, or it is in a file the session has. Never quote from memory.
      - **The session can show a public-domain basis for that source and edition.** For example, a Project Gutenberg text carrying its public-domain notice, or an edition (and translation, if any) first published before the current US cutoff, which is before 1931 as of 2026.

      Name the author, the work and the edition.
   3. Otherwise, a brain break on the lesson's concept (`structural-prompt-library.md` §Brain Breaks).

   Depletion and feedback saturation still mean teach and stop.
4. **Assignment.** Name the command that tests the skill on the writer's own pages (the Assignment column). The writer runs it; the coach does not run audits or produce findings (Delegation principle). Lessons with no audit use the process named instead. Without a diagnosis, give the full invocation text, so the audit sees these terms in its arguments: run on the chosen pages at passage scale; missing pass inputs and run-sequence prerequisites are noted, not required; write only the run folder (A1's `/audit dialectical` also writes the `Argument_State.md` that A2 to A4 need).
5. **Record.** Update `Syllabus_Progress.md` (below): add the lesson to the Trail and update its row in the table.

The writer can stop after any step. A lesson that was taught but not tested is `practiced`, which is a fine place to leave it.

---

## Progress and clearing

Keep `Syllabus_Progress.md` at the project root (or the folder the writer names when there is no project). Never write it to the plugin.

```markdown
# Syllabus Progress
Trail: L2 → L3 → L10

| Lesson | Status | Date | Note |
|---|---|---|---|
| L2 Stakes | cleared | 2026-10-25 | Ch 3 re-run after revision: no Should-Fix stakes finding |
```

The Trail lists the lessons in the order the writer took them, cleared or not. A lesson taken twice appears twice.

Statuses: `open`, `practiced` (taught, and exercised where the lesson has an exercise), `cleared`, `skipped`.

A lesson is **cleared** when its assignment, run on the chosen or revised pages, raises no Should-Fix-or-higher finding for this concept on the channels those pages can show. Name any untested channels in the Note. Use the audit's final calibrated severity: a flag the audit itself classes as intentional and working does not count, but intentionality alone does not exempt a finding.

Where the assignment covers more than the lesson's concept, only these count: L6, a STRUCTURAL BREAK on the primary spine's gates; L8, the Part 3 agency flags; L11, the PA flags; A1, the CL, WR and OB codes. A2 clears when a re-run leaves no Fatal or Major vulnerability. In A3, a PS signal counts as a finding when the memo classifies its recommendation as a Healthy Recalibration.

Process lessons (L5, L14, L15) clear when the named process is completed once.

Keep the game light. Show the Trail and the table as a record of where the writer has been, never as a judgment of the writer (the same transference-health rule as Coaching History in `../SKILL.md`). Do not add counts, scores, streaks, or deadlines: pressure is itself a block type (`writers-block-taxonomy.md`), and the syllabus should never become one.

---

## Sequence

Concept paths are relative to `skills/`. See also names each lesson's neighbouring lessons, with the reason for the link. Deeper reading points to the writer guide in the repository's `docs/writer-guides/` folder where one exists, and then to the level-setting research brief in `docs/`. Neither set is shipped in the plugin or loaded; offer the links to a writer who wants more on a lesson.

### Fiction and narrative track

| # | Lesson | Concept file | Prompt family | Assignment | See also | Deeper reading |
|---|---|---|---|---|---|---|
| **Unit 1 · The promise** |
| L1 | Promise and reader contract | `genre-reader-audits/references/craft/shelf-positioning.md` | Perspective | `/audit shelf` (Fast Pass + Part 2) | L13: the same promise, delivered on the page; L2: the stakes that shelf expects | — |
| **Unit 2 · The engine** |
| L2 | Stakes | `narrative-craft-audits/references/craft/stakes-system.md` | Constraint | `/audit stakes` | L3: whether choices made under that pressure are believable; L10: whether a consequence is felt as well as shown; L4: when the risk is physical | `writer-guides/stakes-system.md`; `stakes-system-level-setting.md` |
| L3 | Decision pressure | `narrative-craft-audits/references/craft/decision-pressure.md` | Inversion | `/audit decision-pressure` | L2: the pressure field the choice sits in; L8: the wants and fears a decision should track; L10: how emotion bends the reasoning | `writer-guides/decision-pressure.md`; `decision-pressure-level-setting.md` |
| L4 | Force and consequence | `narrative-craft-audits/references/craft/force-architecture.md` | Temporal | `/audit force` | L10: whether the cost of force is felt; L8: whether force tests and changes the character; L9: whether the mind stays present in the fight | `writer-guides/force-architecture.md`; `force-architecture-level-setting.md` |
| **Unit 3 · Structure** |
| L5 | Choosing a structure | `plot-architecture/references/plot-selection-coaching.md` | Temporal | `/plot-coach` (pre-drafting steps 1–3 run against your draft, or the stuck-draft steps if you are stuck) | L6: diagnosing the spine of the structure you chose; L15: when a stuck draft is why you are choosing | — |
| L6 | The spine | `plot-architecture/references/plot-architecture-audit.md` | Scale-Shift | `/plot-coach` asking for spine diagnosis (`plot-architecture/SKILL.md` §Diagnostic Process) | L5: which structure the spine belongs to; L7: whether each scene carries the spine out; L12: what can be cut without breaking it | — |
| L7 | Scene turns | `narrative-craft-audits/references/craft/scene-turn.md` | Isolation | `/audit scene-turn` | L6: the spine the scenes serve; L10: whether a scene that turns also moves the reader; L8: the psychology and agency behind a scene's goal | — |
| **Unit 4 · People** |
| L8 | Character architecture | `narrative-craft-audits/references/craft/character-architecture.md` | Constraint | `/audit character` | L9: whether that inner life survives the intense scenes; L10: where inside a passage the feeling fails; L3: whether decisions follow from the character | — |
| L9 | Interiority under pressure | `narrative-craft-audits/references/craft/interiority-preservation.md` | Perspective | `/audit interiority` | L4: the same loss in fight scenes; L8: what a passage of interiority is for; L10: how thought and feeling reach the reader | optional, for a female POV character: `writer-guides/female-interiority.md` |
| L10 | Emotional craft | `narrative-craft-audits/references/craft/emotional-craft.md` | Isolation | `/audit emotional-craft` | L8: whether the character is psychologically coherent; L6: whether the story's structure works; L9: whether the inner life holds at peak intensity | — |
| **Unit 5 · Prose** |
| L11 | Load-bearing prose | `narrative-craft-audits/references/craft/literary-craft.md` | Isolation | `/audit literary-craft` | L10: whether the emotion transmits at all; L12: a device you could cut without changing the reading | `writer-guides/literary-craft.md`; `literary-craft-level-setting.md` |
| L12 | Compression | `narrative-craft-audits/references/craft/compression-audit.md` | Deletion | `/audit compression` | L7: scenes that do not turn are the first cut candidates; L6: the spine a cut must not break | `writer-guides/compression-audit.md`; `compression-audit-level-setting.md` |
| **Unit 6 · Genre elective** |
| L13 | Delivering your genre's promise | the file for the book's shelf under `genre-reader-audits/references/genre/` or `genre-reader-audits/references/tag/` (see `/audit` list) | Constraint | `/audit <genre or tag>` | L1: the same promise, seen from the shelf; L2: the stakes your genre expects | for mystery and thriller, `writer-guides/mystery-thriller-architecture.md` first; then the matching brief, if one exists (for example `grimdark-level-setting.md`, `mystery-thriller-architecture-level-setting.md`, `cozy-tag-level-setting.md`) |
| **Unit 7 · Revision practice** |
| L14 | Using feedback | `revision-coach/references/feedback-triage.md` | none | `/triage-feedback` on one round of notes | L15: when too much feedback becomes the block; L1: when the notes dispute the book's promise | — |
| L15 | Getting unstuck | `revision-coach/references/writers-block-taxonomy.md` | none | `/coach stuck` once | L14: sorting the notes that stalled you; L5: its steps for a stuck draft | `writer-guides/writers-block-rut-breaking.md`; `writers-block-rut-breaking-level-setting-codex54.md` |

Teach ranges, where the opening section is thin or the concept sits later in the file:
- L1: §Purpose, §Part 1, and the 10% Threshold gate in §Part 2.
- L5: §Purpose and the symptom table in §Phase 5, Step 1.
- L6: §Purpose and §Severity Levels, plus the Plot Architecture vs. Pass 2 boundary in `plot-architecture/SKILL.md`.
- L8: §Purpose, plus §Part 3's Definitions and Puppet Detection.
- L14: §When to use through §The structured record.
- L15: §Primary Block Types through §Perfectionism Modifier.

L13: skip it when the book's shelf has no genre or tag audit in the `/audit` list (for example, general romance or literary fiction).

L15's assignment needs a `Diagnostic_State.md` or `Argument_State.md`. Without one, the writer can opt into a state-less `/coach stuck` run (`../SKILL.md` §2). That run moves L15 to `practiced`; clearing still needs a run against a state file.

### Argument track

For op-eds, briefs, testimony, and other argument-shaped nonfiction. L14 and L15 apply here too.

| # | Lesson | Concept file | Prompt family | Assignment | See also | Deeper reading |
|---|---|---|---|---|---|---|
| A1 | Claim, warrant, objection | `argument-audits/references/craft/dialectical-clarity.md` | Isolation | `/audit dialectical` | A2: the attack on the warrants you mapped; A4: the evidence under those claims | `writer-guides/dialectical-clarity.md`; `dialectical-clarity-level-setting.md` |
| A2 | The hostile reader | `argument-audits/references/craft/argument-red-team.md` | Perspective | `/audit argument-red-team` | A1: the claims and warrants the red team attacks; A4: the evidence it attacks | `writer-guides/argument-red-team.md`; `argument-red-team-level-setting.md` |
| A3 | Persuading a real audience | `argument-audits/references/craft/argument-persuasion.md` | Scale-Shift | `/audit argument-persuasion` | A2: the hostile reader, set against the real one; L14: feedback from your real audience | `writer-guides/argument-persuasion.md`; `argument-persuasion-level-setting.md` |
| A4 | Evidence that holds | `argument-audits/references/craft/argument-evidence.md` | none (planning) | `/audit argument-evidence` | A1: the claims the evidence must carry; A2: the attack the evidence must survive | `adversarial-evidence-level-setting.md` |

A1's teach range: §Purpose, the opening paragraph of §Step 4 (what a warrant is), and §Common Patterns.

A2 to A4 need the `Argument_State.md` that A1's assignment produces, so keep that order. If you revised after A1, re-run `/audit dialectical` before the next lesson's audit.

Deeper reading links: `https://github.com/anotherpanacea-eng/apodictic/blob/main/docs/<file>`.
