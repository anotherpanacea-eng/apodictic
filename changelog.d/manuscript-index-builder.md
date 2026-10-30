### Workflows — Manuscript Index Builder (Increment 1)

New `/book-index` command for nonfiction authors who have to produce an index. The model proposes a
topic map (headings, variants, subheadings, See and See also), every heading tied to the text by
verbatim quote anchors, and the author accepts, renames, merges or drops headings on a review list.
`scripts/book_index.py` is the only writer of the snapshot and the `Index_Map`: `init`, `update`,
`review`, `accept`, `drop`, `rename`, `merge` and `resnapshot`. Two new closed-key schemas,
`apodictic.index_map.v1` and `apodictic.index_heading.v1`, and a new `book-index` validator: I1
schema, I2 provenance (each quote occurs exactly once in the snapshot), I3 cross-references, I4
acceptance (an accepted heading's content hash still matches), and advisory W1 chapter coverage, W2
long locator strings and W3 subheading checks. The canonical `example-book-index/` directory fixture
runs in `--check-all` under `--strict`. `reanchor.py`'s quote classification is now a shared
`classify_quote` helper. Locators and the formatted index are Increment 2.
