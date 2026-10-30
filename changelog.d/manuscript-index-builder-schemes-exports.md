### Workflows — Manuscript Index Builder (Increment 3: more schemes and exports)

`book_index.py locate` gains two schemes. Both match on the same folded form as the page scheme and
run the same order check; a blank or repeated label leaves its locator unresolved.

- `line`: line numbers from a line-numbered edition supplied as text.
- `ebook`: locations from a `location<TAB>text` table the author exports. Kindle locations are
  read, never computed.

`format --cindex` writes tab-delimited records for Cindex or SKY Index import: UTF-8 with a
byte-order mark, always three fields, and ranges as full endpoints joined by an ASCII hyphen.

Not built: the `embedded` scheme (LaTeX `\index` and Word XE tags), which needs a real source
lexer and waits for its own design, and ebook locations read straight from an EPUB.
