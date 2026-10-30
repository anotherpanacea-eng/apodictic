# Manuscript Index Builder — a back-of-book index the author only has to approve

*Reference module for the APODICTIC Core Editor. A production task, not an audit: it emits no
findings and never changes the manuscript. The tool drafts a topic map (headings, variants,
subheadings, See and See also), each heading tied to real passages by verbatim quotes, and the author
accepts, renames, merges or drops headings on a short review list. Spec: `docs/manuscript-indexing.md`.
Script and validator: `python scripts/book_index.py`, `python scripts/validate.py book-index`. Worked
example: `example-book-index/`.*

---

## When to use

Nonfiction only, argument-shaped or narrative, when the author needs an index: the press has handed
them the job, or they want a head start to give a professional indexer. Fiction gets an index only in
scholarly or annotated editions, which are handled as nonfiction apparatus. Ask for the final,
copyedited text; an index built on an earlier draft will need a re-snapshot.

**Positioning.** This is the author's draft index for review, never a publication-ready index. A human
must review and endorse it before use. The American Society for Indexing has documented how
AI-drafted indexes fail (under-indexing, entries for passing mentions, redundant subheadings, long
strings of undifferentiated locators, wrong page numbers). The validator checks some of these
mechanically (anchors exist, passing mentions never become locators, W1 to W3); whether a passage is
really about its heading, and which words a reader will look up, rest on the author's review. Say so
plainly. APODICTIC is not bound by ASI guidance, and the docs do not present it as a rule.

## What is built

- **Increment 1, the topic map:** snapshot, proposals, the review list, author decisions, re-snapshot
  and the `book-index` gate.
- **Increment 2, locators and output:** `locate` under the `paragraph` and `page` schemes, then
  `format` to a plain-text or .docx index, or to the locator-free topic map.
- **Not built:** the `line`, `ebook` and `embedded` schemes and the Cindex/SKY export (Increment 3).

## The firewall for this module

- **The scripts are the only writers.** `book_index.py` writes the snapshot and the Index_Map. Never
  edit the map by hand: hand edits bypass the carrier escaping and break acceptance hashes.
- **The manuscript is never changed** and no passage is invented. Every anchor is a verbatim quote
  the validator proves occurs exactly once in the snapshot (I2).
- **Decisions come only from the author's explicit replies.** Accept a heading only when the author
  names its id, or names a review group (`--kind`) they were shown. Bulk actions may only drop. A
  heading the author never decides stays `proposed` and is never printed. The validator cannot prove
  a human decided; this rule is the process guarantee.

## Procedure — `/book-index map`

1. **Read the text** the author supplies, and the project's `Argument_State.md` if it has an
   `argument_spine.v1` block. Its `key_terms` (text before ` = `, or the whole term) and `subclaims`
   (with the `Cn:` prefix stripped) are discovery candidates only: their wording and loci never become
   anchors. A missing block or field changes nothing.
2. **Propose headings** as a JSON array of `apodictic.index_heading.v1` objects in a scratch file
   (outside the run folder). For each heading:
   - `heading`: the preferred form as it will print ("Carnegie, Andrew"; "reading rooms").
     `kind`: `name` / `place` / `work` / `concept` / `term`. `variants`: other forms the text uses.
   - `anchors`: verbatim single-line quotes, copied exactly from the text, long enough to occur only
     once. Add `context` (`{"before": ..., "after": ...}`) only when a quote cannot be made unique on
     its own. `end_quote` closes an extended discussion that will become a range.
   - `role`: `substantive` when the passage discusses the topic; `passing` for a mention. Passing
     anchors never become locators. When in doubt, mark it passing; the author can promote it.
   - `subheadings` (one level deep) break down a big topic. Avoid a lone subheading, a subheading
     that repeats its parent's passages, and more than twelve under one heading. A heading or
     subheading with more than six substantive anchors should be broken down.
   - `see` makes a See-only heading ("quiet, *see* silence"): no anchors, no subheadings, no See also.
     `see_also` links related headings; reciprocal links are normal.
   - `weight` in [0, 1]: how likely a reader is to look this up. It orders the review list and, later,
     the cut candidates. It is never printed.
   - Ids: `IX-001`, `IX-001.a1`, `IX-001.s1`, `IX-001.s1.a1`. Status is set by the tool.
3. **Write the snapshot and map:**
   `python scripts/book_index.py init <text.md> <run_folder> <Project> <runlabel> <proposals.json> [--chapter-level N]`.
   `chapter_level` is the heading level that starts a chapter (1 for `#`, 2 for `##` under a `#` book
   title). The command forces every heading to `proposed`, refuses to overwrite an existing snapshot
   or map, and refuses proposals that fail I1 to I3, printing why. Fix the proposals and rerun.
4. **Show the review list:** `python scripts/book_index.py review <map>`. It groups headings by kind,
   sorts them by weight, and shows each heading's variants, chapter spread, See links and every anchor
   in context. Present it to the author as written, a group at a time for a long list.
5. **Record the author's decisions**, only as they state them:
   - accept: `book_index.py accept <map> IX-004 IX-009` or `accept <map> --kind name`
   - drop: `book_index.py drop <map> IX-012 IX-013`
   - rename: `book_index.py rename <map> IX-004 "Arendt, Hannah"` (back to proposed; re-accept)
   - merge: `book_index.py merge <map> <source> <target>`: the source's anchors, subheadings, heading
     text and variants move to the target; references to the source repoint to the target; the
     target and every heading it rewrote return to proposed for the author to look at again.
   - anything else (promote a passing anchor, fix a quote, add a heading): write the changed headings
     to a proposals file and run `book_index.py update <map> <proposals.json>`. A heading whose
     content changed returns to proposed; an unchanged one keeps its acceptance.
   An accept refuses a heading with validator errors. There is no hand-edit path.
6. **Gate:** `python scripts/validate.py book-index <run_folder> --strict`.

## Procedure: `/book-index locate`

Only published headings take part: accepted, with no validator error. Passing anchors never get a
locator. The model never writes or edits a locator or the formatted index; `locate` and `format` are
their only writers.

1. **Choose a scheme with the author.**
   - `paragraph` gives chapter.paragraph locators (`3.12`, `3.12–14`). It numbers chapters in book
     order and body paragraphs within each; front matter and headings are excluded. It needs chapter
     headings at the map's `chapter_level`.
   - `page` gives printed folios from the typeset proof PDF. It needs `pypdf`
     (`pip install pypdf`); without it the scheme refuses and says so.
2. **Run it:** `python scripts/book_index.py locate <map> --scheme paragraph`, or
   `--scheme page --pdf <proof.pdf> --body-end N`.
   - **Folios** come from the PDF's own page labels. Without labels, ask the author which PDF page is
     folio 1 and pass `--folio-start N`. The command never guesses folios, so front matter can be
     searched (`--include-front`) only when the PDF carries its own labels.
   - **Body pages** are the only pages searched by default, because notes and other back matter can
     repeat body sentences. Ask the author for the last PDF page of the body and pass `--body-end N`
     (required); `--include-back` adds the pages after it.
   - **Running heads and folio lines** are dropped when, digits masked, they repeat on five or more
     pages.
   - **Matching** folds both sides first: inline markdown, footnote markers, dashes, quote styles,
     ligatures, line-break hyphenation, whitespace and case. A quote must match exactly once.
   - **The order check** then keeps a matched passage only if it lies on every longest in-order
     sequence of matches. Others are unresolved as `out_of_order` or `ambiguous_order`; usually a
     copyedited sentence whose old wording survives elsewhere.
   - **Output:** `[Project]_Index_Locators_[runlabel].json`.
3. **Format:** `python scripts/book_index.py format <map> --locators <that json>`, with the press's
   style:
   - `--layout indented|run-in`
   - `--sort word|letter` (word-by-word or letter-by-letter)
   - `--ranges chicago|full` (`101–8` or `101–108`)
   - `--see-also end|after-heading`
   - `--docx` for Word
   - `--max-lines N` to list the lowest-weight headings as cut candidates for the press's length
     allowance. None is cut; the author drops any they agree with.

   Without `--locators`, it writes the locator-free topic map. A report beside the index lists every
   unresolved anchor with its reason and position, every See or See also dropped because its target
   isn't published, and every heading left out. If a heading changed since `locate`, `format`
   refuses: run `locate` again.
4. **Show the author** the index and the report. Resolve unresolved anchors by updating their
   quotes (`update`), then run `locate` again. Repagination or a new edition costs one rerun of
   `locate`.

## Re-snapshot after late corrections

When the text changes, run
`python scripts/book_index.py resnapshot <map> <new_text.md> <new_runlabel>`. It writes a new snapshot
beside the old one (which stays), points the map at it, and re-checks every anchor. An accepted
heading stays accepted when its anchors only moved and their paragraphs (across the whole range, for
a range anchor) and chapter are unchanged. It returns to `proposed` when a quote vanished or became
ambiguous, or when the passage around a quote changed: the author judged the old passage, not the new
one. The command lists broken quotes separately from changed passages. Fix broken quotes with
`update`; show changed passages to the author for re-acceptance.

## The `book-index` gate

`validate.py book-index <run_folder|index_map.md> [--strict]`. Exit 0 clean or WARN-only, 1 ERROR
(or WARN under `--strict`), 2 usage. I1 covers every heading; I2, I3 and W1 to W3 skip dropped ones.

| Check | What it catches |
|---|---|
| I1 schema | field rules, closed keys, nested anchor and subheading rules, the See-only shape, a heading with no substantive anchor |
| I2 provenance | a quote or end quote that is missing or occurs more than once, an end quote before its quote, a missing snapshot |
| I3 cross-references | a See or See also to a missing, dropped or See-only heading; a See cycle |
| I4 acceptance | an accepted heading changed after acceptance |
| W1 coverage | a chapter with no substantive anchor (possible under-indexing) |
| W2 locator strings | more than six substantive anchors on one heading or subheading |
| W3 subheadings | a lone subheading, a subheading repeating its parent's or a sibling's passages, more than twelve subheadings |

**Honest limit.** I2 proves a passage is real, not that it is about its heading. I4 proves an accepted
heading is unchanged since acceptance was recorded, not that a human made the decision.
