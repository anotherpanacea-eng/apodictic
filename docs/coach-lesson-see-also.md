# Learning Mode: see-also links between lessons (proposed)

**Status: proposed, not admitted.** Written 2026-10-30 for fleet card AP-LRN-2 ("Coach: see-also links
between lessons from each audit's neighbor boundaries"). Its dependency, OCA-A6, landed 2026-10-29.
Its done bar: each syllabus lesson ends with 2–3 see-also lessons and its deeper reading, derived from
existing non-duplication boundaries.

Owner direction (2026-10-29): discoverability and joy, like a good Wikipedia dive. This is mostly
linking existing content; the desktop app can make the links clickable.

## What changes

Only `plugins/apodictic/skills/revision-coach/references/syllabus.md`:

1. **A See also column** in both Sequence tables, holding 2–3 lesson ids each, from the map below.
2. **One closing line in step 2 (Teach).** After explaining the concept and its nearest neighbor, name
   the lesson's See also lessons, one line each on how it borders this one (from the boundary text
   just read), and offer its deeper reading. The writer may take any of them as the next lesson. That
   fits AP-LRN-1's map-not-course direction without building it.
3. **Deeper reading prefers the writer guides.** Point to the writer-facing guide in
   `docs/writer-guides/` (OCA-A7) where one exists, and keep the research brief as the second link.
   The guides exist for L2, L3, L4, L9 (`female-interiority.md`, whose subject is interiority across
   scene types), L11, L12, L13 (mystery and thriller only), L15, A1, A2 and A3.

There is no new validator. A wrong lesson id would show in the first session and costs one edit to fix.

## The map

Each link names its source: the boundary text in the lesson's concept file, or, where the file has no
boundary, the syllabus row itself. "Proposed" marks a link with no boundary source, for you to keep or
cut.

| Lesson | See also | Source |
|---|---|---|
| L1 Promise and reader contract | L13, L2 | **proposed**. L13 is the same shelf's promise delivered; `shelf-positioning.md` has no neighbor boundary |
| L2 Stakes | L3, L10, L4 | `stakes-system.md` overlap list: Emotional Craft (1), Decision Pressure (2); "Coordinate with Decision Pressure"; Force named once |
| L3 Decision pressure | L2, L8, L10 | `decision-pressure.md`: "Coordinate with Stakes"; Emotional Craft boundary (4); character interiority (12) |
| L4 Force and consequence | L10, L8, L9 | `force-architecture.md`: Emotional Craft boundary (2); "Pass 5 Character Architecture notes"; the vanishing-interiority flag |
| L5 Choosing a structure | L6, L15 | the L6 teach range (Plot Architecture); L5's assignment names the stuck-draft steps, which is L15's ground |
| L6 The spine | L5, L7, L12 | `scene-turn.md`: "not a substitute for Plot Architecture"; `compression-audit.md` cuts against the spine |
| L7 Scene turns | L6, L10, L8 | `scene-turn.md` "What this audit is not": Plot Architecture, Emotional Craft, Character Architecture |
| L8 Character architecture | L9, L10, L3 | `character-architecture.md` Interiority Function Check; `emotional-craft.md` fine-grain boundary; decision logic |
| L9 Interiority under pressure | L4, L8, L10 | `interiority-preservation.md`: "see Force Architecture (Disembodied Combatant)"; the Interiority Function Check |
| L10 Emotional craft | L8, L9, L6 | `emotional-craft.md` "What this audit is not": Plot Architecture, Character Architecture; the interiority fine-grain boundary |
| L11 Load-bearing prose | L10, L13 | `literary-craft.md`: the Emotional Craft boundary; Literary Fiction genre calibration |
| L12 Compression | L7, L6 | `compression-audit.md` (1): "Scene Turn checks whether scenes turn. This audit checks whether material is expendable" |
| L13 Delivering your genre's promise | L1, L2 | **proposed**. L1 is the same promise from the shelf side; `stakes-system.md`'s genre table |
| L14 Using feedback | L15, L1 | **proposed**. Process neighbors; L1 because feedback often disputes the book's promise |
| L15 Getting unstuck | L14, L5 | **proposed**. Process neighbors; L5's stuck-draft steps |
| A1 Claim, warrant, objection | A2, A4 | the syllabus order: A2 to A4 build on A1's `Argument_State.md` |
| A2 The hostile reader | A1, A4 | the same; the red team attacks warrants (A1) and evidence (A4) |
| A3 Persuading a real audience | A2, L14 | **proposed**. The hostile reader against the real one; audience feedback |
| A4 Evidence that holds | A1, A2 | the same as A1 and A2 |

## Owner calls

1. Keep or cut the six **proposed** links (L1, L13, L14, L15, A3, and the L5 → L15 link)?
2. Is "the writer may take any See also lesson next" in step 2 acceptable now, ahead of AP-LRN-1?

## Not in scope

- The lesson-door-from-findings design (AP-LRN-1).
- Brain-break exercises (AP-LRN-3).
- Clickable links in the desktop app.
- Any change to the concept files, `Syllabus_Progress.md` or the clear rule.
