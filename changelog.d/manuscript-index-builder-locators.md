### Workflows — Manuscript Index Builder (Increment 2: locators and output)

`/book-index locate` turns an accepted topic map into an index. `book_index.py locate` gives
every substantive anchor of every published heading a locator, or puts it on the unresolved list
with a reason. Two schemes:

- `paragraph`: chapter.paragraph, from the snapshot.
- `page`: printed folios from the proof PDF, with optional `pypdf`.

The page scheme takes folios from the PDF's page labels or from `--folio-start`; it never guesses.
It searches only the body, between the author's `--body-start` and `--body-end` PDF pages; page
labels are locator values, never page selectors.
It strips running heads and folios, matches quotes on a folded form (markdown, footnote markers,
dashes, quote styles, ligatures, line-break hyphenation and case), and keeps a match only if it lies
on every longest in-order sequence of matches.

`book_index.py format` writes the index as plain text or a byte-stable .docx, or the locator-free
topic map. Options set indented or run-in layout, word- or letter-by-letter sorting, Chicago or
full ranges, and See also placement. A report lists unresolved anchors, dropped cross-references
and left-out headings, and `--max-lines` adds cut candidates. `format` refuses when a heading
changed since `locate`. The .docx reuses `annotation_export.py`'s deterministic zip and OOXML
parts unchanged.
