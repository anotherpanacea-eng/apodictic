# Coach learning: implementation plan for AP-LRN-1, AP-LRN-2 and AP-LRN-3

**Status: plan, not built.** Written 2026-11-06 for the three fleet cards. The specs are `coach-lessons-as-map.md`
(AP-LRN-1, #418), `coach-lesson-see-also.md` (AP-LRN-2, #417) and `coach-brain-breaks.md` (AP-LRN-3, #419). The
owner made each spec's open calls on 2026-11-05. Their wording is recorded on the fleet cards, and each spec now
carries them. No execution or deployment approval is inferred: each build below is its own PR, in its own checkout.

## Owner rulings (2026-11-05)

| Card | Call | Ruling |
|---|---|---|
| AP-LRN-1 | Lesson door in the editorial letter? | No. The door appears in the coach's session plan only, not in core-editor's standalone letter. |
| AP-LRN-1 | Keep the status table, or show the trail only? | Keep both: the trail and the status table. |
| AP-LRN-2 | Keep the **proposed** links? | Keep them ("keep related-lesson links"). |
| AP-LRN-2 | "The writer may take any See also lesson next," ahead of AP-LRN-1? | Yes. Free choice of any linked lesson comes before the larger map. |
| AP-LRN-3 | Brain break with no state file? | Yes: stateless requests are allowed. |
| AP-LRN-3 | Learning Mode exercise when no passage is named? | Yes. Prefer the writer's own prose; a verified, attributed public-domain passage is an optional fallback. The Carroll, Doyle and Brontë examples in the thread were examples, not selections, and approve no rights. |
| AP-LRN-3 | Standing rule | The writer writes. No unsolicited exercise during depletion or feedback saturation. |

## Order

The three PRs touch overlapping prose: `syllabus.md` steps 1 to 3, and `revision-coach/SKILL.md` §1, §2 and §10. Build them in sequence, each from the previous one's merge, so no two edit the same lines at once.

1. **PR 1, AP-LRN-2 (see-also).** This touches only `syllabus.md` and depends on nothing.
2. **PR 2, AP-LRN-1 (doors, no default, trail).** Its step-1 rewrite offers "one See also of the last lesson taken", which needs PR 1.
3. **PR 3, AP-LRN-3 (brain breaks).** This touches the prompt library, the block taxonomy, `SKILL.md` §2, and syllabus step 3 for the passage-less exercise.

All paths below are under `plugins/apodictic/skills/revision-coach/`. Each PR is prose only: no validator, script or generated tree changes. Each ships one `changelog.d/<slug>.md` fragment and no version bump.

## PR 1: AP-LRN-2, see-also links

**`references/syllabus.md`:**
1. **A See also column.** Add it to both Sequence tables, between Assignment and Deeper reading, and fill it from the spec's map, all rows with the proposed links kept. Write each entry as `L3: whether the pressure shapes the choice`, taking the reason words from the map's source column. Rewrite proposed links' reasons from the map, never from a concept file past its Teach range.
2. **Deeper reading.** Where `docs/writer-guides/` has a guide, put it first and keep the research brief second. Guides exist for:
   - L2 `stakes-system.md`
   - L3 `decision-pressure.md`
   - L4 `force-architecture.md`
   - L11 `literary-craft.md`
   - L12 `compression-audit.md`
   - L13 `mystery-thriller-architecture.md` (mystery and thriller only)
   - L15 `writers-block-rut-breaking.md`
   - A1 `dialectical-clarity.md`
   - A2 `argument-red-team.md`
   - A3 `argument-persuasion.md`

   For L9, add `female-interiority.md` as optional reading for a female POV character, and keep `/audit interiority` as its assignment. Also update the Sequence intro sentence: it says deeper reading points to the level-setting briefs, and it should now name the writer guides too. Neither set is shipped or loaded.
3. **Step 2 (Teach).** Append: "Close by naming the lesson's See also entries with their reasons and offering its deeper reading. The writer may take any See also lesson next."

**Check:**
- `python plugins/apodictic/scripts/validate.py --check-all` passes.
- Every See also id exists in its own track: A-lessons link to A-lessons, except A3 → L14, which the spec allows.
- No reason quotes a concept file past its Teach range.

## PR 2: AP-LRN-1, lessons as a map

**`SKILL.md` §1 Session Planning.** Add one optional step:
- When a planned target's finding came from the audit or pass that a lesson's Assignment runs, add one line under that target: `Optional lesson: L2 Stakes (/coach learn L2)`. The finding's `F-<ORIGIN>-<NN>` id names its origin code (`findings-ledger-format.md`), but no table maps origin codes to Assignment commands, so the match is the same judgment syllabus step 1 already makes; do not build a code table for it.
- At most one door per plan, for the highest-leverage target that has one.
- Never for a lesson that is cleared or skipped, and never in a No-Prompt Zone for depletion.
- The door goes in the session plan only. Core-editor's editorial letter is not touched (owner ruling).

**`SKILL.md` §10, and the `syllabus.md` header line "Load this file only in Learning Mode…".** Both change to: "Learning Mode loads this file; Session Planning may read only its Sequence tables, to offer a lesson door."

**`syllabus.md` step 1 (Pick the lesson).** Replace the default with three doors and the writer's choice:
1. the lesson matching the highest-leverage open finding, when `Diagnostic_State.md` exists, as now;
2. one See also of the last lesson taken, or the first Sequence lesson if none has been taken;
3. the map: the Sequence tables as a list to browse.

The writer may name any lesson. "Next" or "just pick" takes the first lesson in Sequence order that isn't cleared or skipped, so the linear path stays. The clear-rule sentence at the start of step 1 is unchanged.

**`syllabus.md` §Progress and clearing.**
- Replace the header `Cleared 3 of 15 · Next: L5 Choosing a structure` with `Trail: L2 → L3 → L10`: the lessons in the order taken, repeats allowed, cleared or not.
- Keep the status table (owner ruling).
- Delete "The argument track counts 6 lessons (A1 to A4, L14, L15) instead of 15."
- Extend "keep the game light" to forbid counts as well as scores and streaks.

**Check:**
- The validator passes.
- A dry run, as in OCA-A6, covers four cases:
  - `/coach learn` with no state;
  - `/coach learn` with a `Diagnostic_State.md` whose top finding came from `/audit stakes` (ID `F-<ORIGIN>-<NN>`, per `findings-ledger-format.md`), which offers L2 first;
  - a session plan with a cleared L2, which gets no door;
  - "just pick", which takes the first uncleared lesson.

  Record the dry run in the PR, not in the repo.

## PR 3: AP-LRN-3, brain breaks

**`references/structural-prompt-library.md`.** Add a "Brain breaks" section after "Prompt Delivery Rules":
- The test-1 variant **concept-grounded**: one named syllabus concept, applied to material the writer invents now. It must not touch the manuscript, its characters or its argument. Tests 2 to 5 are unchanged.
- How to make one: a family plus a lesson concept, applied to invented material. Use the spec's Deletion-with-compression example.
- Two worked examples: one that passes, and one that fails on test 4 because it names the scenario.
- **Delivery:** one choice, never a list (one manuscript-connected prompt or one brain break). Framed as low-stakes and disposable, with the clinamen clause kept. Nothing is stored: the text never enters the manuscript, state files, findings or logs.
- **No-Prompt Zones:** add "except a brain break in the state-less run" to "state file missing". Depletion (Type 3) and feedback saturation (Type 7) stay absolute.

**`references/writers-block-taxonomy.md`.** One line each, offering a brain break beside the existing intervention:
- Type 2, Motivational / Avoidance: an off-project warm-up.
- Type 6, Aesthetic / Execution Gap: practise the skill without the book's stakes.
- The Perfectionism Modifier: disposable by design.

No line for Types 3 or 7.

**`SKILL.md` §2, "State-less run" paragraph.** Append: "After the conversation, the coach may offer one brain break in the conversation itself, under the Type 2, Type 6 or perfectionism conditions, and only when the writer asks for an exercise or accepts the offer. Nothing is written."

**`syllabus.md` step 3 (Exercise), for a writer who has named no passage.** In this order:
1. Ask for a paragraph of the writer's own prose. Any project counts, and this is preferred.
2. A public-domain passage, only when both of these hold:
   - **Its exact text is in the session.** The writer pasted it, or it is in a file the session has. The coach never quotes from memory.
   - **The session can show a public-domain basis for that source and edition.** Examples: a Project Gutenberg text carrying its public-domain notice, or an edition (and translation, if any) first published before the current US cutoff, which is before 1931 as of 2026.

   Name the author, the work and the edition. If either condition can't be established, skip this option.
3. Otherwise, a brain break on the lesson's concept.

Depletion and feedback saturation still mean "teach and stop."

*This plan's own choice:* "verified" requires both exact text and a shown public-domain basis, so nothing is invented and no copyrighted edition slips in. Bundling a public-domain sample set would be new scope and would need its own rights call. The owner can change this in review.

**Check:**
- The validator passes.
- A dry run covers four cases:
  - `/coach stuck` with no state, Type 2, where one brain break is offered and nothing is written;
  - Type 3, where no prompt is given;
  - `/coach learn L12` with no passage, where it asks for the writer's prose, then falls back to a brain break;
  - a public-domain passage pasted by the writer, which is attributed.
- Grep confirms that no brain-break text path writes a file.

## Review and landing

- Each PR is a draft, reviewed by Codex with `--base origin/main`, and waits for a train (fleet rule: drafts wait for trains).
- The cards stay `ready` until PR 1 opens, then move to `build`.
- The desktop app's clickable links and lesson-door rendering are out of scope: the specs' "Not in scope" lists, and AP-RUN.
