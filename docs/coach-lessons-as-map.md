# Learning Mode: lessons raised by findings, not a linear course (proposed)

**Status: proposed, not admitted.** Written 2026-10-30 for fleet card AP-LRN-1. Its dependency, OCA-A6
(the syllabus dry run), landed 2026-10-29.

**Owner direction (2026-10-29):** "never force a lesson the writer does not need right now; the 15
lessons become a browsable map."

**Done bar:**
- findings offer an optional lesson door;
- `/coach learn` no longer defaults to the next uncleared lesson;
- progress is a trail, not a cleared count.

Companion: AP-LRN-2's see-also links (apodictic#417). This spec works with or without them.

## Today

`revision-coach/references/syllabus.md` step 1 defaults to "the first lesson in the sequence that
`Syllabus_Progress.md` does not show as cleared or skipped", and it already offers the lesson matching
the highest-leverage open finding first. The progress file opens with `Cleared 3 of 15 · Next: L5 …`.
Session Planning (`revision-coach/SKILL.md` §1) never mentions lessons.

## Changes

All the changes are prose, in two files. No validator reads `Syllabus_Progress.md`.

1. **The lesson door, in Session Planning.**
   - **The door:** add one optional step to §1. When a finding the plan targets came from an audit
     that is a lesson's Assignment (for example `/audit stakes` → L2, Pass 5 Character Audit → L8,
     whose concept file says it calibrates Pass 5), the plan may add one line under that target:
     "Optional lesson: L2 Stakes (`/coach learn L2`)".
   - **Limits:** at most one door per plan, for the highest-leverage target that has one. Never one
     for a cleared lesson, and never when the writer is depleted (the existing No-Prompt Zone).
   - **Matching:** the coach judges the match from the finding's source audit, the same judgment as
     syllabus step 1. Finding ids carry no audit code that could be looked up (their `ORIGIN` is chosen
     per run, `findings-ledger-format.md`), so this adds no table.
2. **No default lesson.** Rewrite syllabus step 1 so `/coach learn` with no lesson named offers up to
   three doors and lets the writer choose:
   - the lesson matching the highest-leverage open finding (as now);
   - one See also of the last lesson taken (once AP-LRN-2 lands), otherwise the next lesson in the
     Sequence, offered as one choice and not as the default;
   - the map: the Sequence table, as a list to browse.

   "Next", or "just pick", takes the Sequence order, so the linear path stays available.
3. **A trail instead of a count.** In the progress file, replace the header line
   `Cleared 3 of 15 · Next: L5 Choosing a structure` with the lessons in the order the writer took
   them, for example `Trail: L2 → L3 → L10`.
   - Drop the "Cleared n of 15" and "Next" phrasing, and the argument track's "counts 6 lessons" line.
   - The status table and the clear rule stay as they are, so a writer can still see what's cleared.
   - The "keep the game light" paragraph already forbids scores and streaks; it now also covers counts.

## Owner calls

1. Should the lesson door also appear in the editorial letter? This spec keeps it to the coach's
   session plan: the letter is core-editor's deliverable, with its own format rules.
2. Keep the status table in the progress file (proposed), or show the trail only?

## Not in scope

- See-also links (AP-LRN-2) and brain breaks (AP-LRN-3).
- Any change to the clear rule, the Teach ranges or the audits.
- Desktop rendering.
