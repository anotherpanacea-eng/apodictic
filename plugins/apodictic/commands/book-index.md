---
description: Draft a back-of-book index the author only has to approve (nonfiction)
argument-hint: map (default), or point to the final manuscript text
---

Manuscript Index Builder. For a nonfiction author who has to produce an index: the tool drafts a topic map — headings, variants, subheadings, See and See also — with every heading tied to real passages by verbatim quotes, and the author accepts, renames, merges or drops headings on a short review list. It never changes the manuscript.

Load `../skills/core-editor/SKILL.md` and follow `../skills/core-editor/references/manuscript-indexing.md`.

**Mode.** `map` (the default) builds and reviews the topic map. `locate` resolves locators under the `paragraph` or `page` scheme and formats the index (procedure in the module's §Procedure: `/book-index locate`). The `line`, `ebook` and `embedded` schemes are not built yet; say so.

**Firewall.** `scripts/book_index.py` is the only writer of the snapshot and the Index_Map: never write or edit either by hand, and never write locators or a formatted index yourself. Record a decision only from the author's explicit reply, per heading id or per review group they were shown; bulk actions may only drop. A heading the author does not decide stays proposed and is never printed. Present the result as the author's draft index for review, never as publication-ready.

**Procedure** (per `../skills/core-editor/references/manuscript-indexing.md` §Procedure):

1. Ask for the final, copyedited text if it is not already given.
2. Propose headings as `apodictic.index_heading.v1` objects in a scratch JSON file, with verbatim quote anchors.
3. `python scripts/book_index.py init <text> <run_folder> <Project> <runlabel> <proposals.json> [--chapter-level N]`; fix and rerun on refusal.
4. `python scripts/book_index.py review <map>` and present the review list.
5. Record the author's decisions with `accept`, `drop`, `rename` and `merge`; apply any other change (a promoted anchor, a fixed quote) with `update`.
6. After late corrections: `python scripts/book_index.py resnapshot <map> <new_text> <new_runlabel>`.
7. For locators: `python scripts/book_index.py locate <map> --scheme paragraph`, or `--scheme page --pdf <proof.pdf> --body-end N [--folio-start N]`; then `python scripts/book_index.py format <map> --locators <[Project]_Index_Locators_[runlabel].json>` with the press's style flags. Show the index with its report; never write or edit locators or the index yourself.

**Gate before finalizing:** `python scripts/validate.py book-index <run_folder> --strict`. Resolve any ERROR (I1 schema, I2 a quote missing or not unique, I3 a broken See or See also, I4 a heading changed after acceptance) and review W1 (a chapter with no substantive anchor), W2 (more than six substantive anchors on one heading) and W3 (subheading problems). See `docs/manuscript-indexing.md`.

**State and output locations** (per `../skills/core-editor/references/output-structure.md` §Folder Architecture):
- Write the snapshot and `[Project]_Index_Map_[runlabel].md` to a run folder under `runs/YYYY-MM-DD_{model}_{type}/`; keep the proposals file outside it
- Never write to the plugin repo

If a manuscript path or mode is provided: $ARGUMENTS
