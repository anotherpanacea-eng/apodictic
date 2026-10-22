# Offline citation extraction: local producer contract

**Status:** Built — a finite, standalone citation-surface producer. It is not a complete citation checker or a promise that every citation in a document was found.
<!-- built-when: plugins/apodictic/skills/research-verification/scripts/citation_extract.py -->

`citation_extract.py` recognizes selected citation syntax and immediately associated
quote spans in text supplied by its caller. It uses only the Python 3.10+ standard
library and works from a bare plugin-directory copy under `python -S`. It has no
CLI, file acquisition, network/provider/model call, source resolution, source-text
verification, rendering, or persistent state. Its output does not establish that
a URL is reachable, a source exists, or a quotation matches a source.

## API and coordinates

```python
from citation_extract import CitationExtractionError, extract_citations

result = extract_citations(text, media_type="text/markdown")
```

`text` must be the caller's already LF-normalized Unicode string. The function
does not trim, re-encode, case-fold the document, or repair it. `media_type` is
exactly `text/plain` or `text/markdown`; both use the same grammar. Any other
string media type returns `unsupported_format` with no records.

Validation occurs before media-type selection, in this order: a non-string
`text` raises `TypeError("text must be str")`; a non-string `media_type`
raises `TypeError("media_type must be str")`; more than 1,000,000 Unicode
codepoints raises `CitationExtractionError("text exceeds extraction limit")`;
CR or a lone surrogate raises `CitationExtractionError("text must be LF-normalized Unicode scalar content")`.
Errors do not include the supplied text.

All spans are half-open `start,end` Python character indices in the exact
supplied string. They are not byte or UTF-16 offsets. `raw_citation_text`
equals `text[start:end]`. An adapter that needs original-byte coordinates must
compose these positions with its own normalization boundary map. For example,
UTF-8 bytes `c3a90d0a31302e313233342f61` normalize to
`"é\n10.1234/a"`; character span `[2,11)` maps through
`[0,2,4,5,6,7,8,9,10,11,12,13]` to original bytes `[4,13)`.
The producer does not emit byte offsets, files, hashes, IDs, or timestamps.

## Closed result

The top-level keys are exactly `schema_version` (integer `1`),
`grammar` (`m1-local-v1`), `status`, `coverage` (`admitted_syntax_only`),
and `citations` (list). `status` is `recognized_surfaces` if records
exist, `no_matches` for supported text with none, and `unsupported_format`
for another string media type. `no_matches` means no surface matched this
limited grammar; it is not a zero-citation or full-coverage assertion.

Each record has exactly `kind`, `status`, `reason`, `span`,
`raw_citation_text`, `normalized_citation`, `definition_span`,
`quote_span`, `claim_corridor_span`, and `attachment_method`.
`kind` is `footnote | author_year | markdown_link | url | doi`.
Record `status` is `extracted | ambiguous`; an ambiguous `reason` is
`missing_definition | multiple_definitions | unsupported_definition`,
and an extracted record has null reason. `normalized_citation` always has
`doi,url,title,author,year`, each string or null. Unknown values remain null:
a Markdown label is not a title. Non-null spans have only integer `start,end`
with `0 <= start < end <= len(text)`. `definition_span` is the whole
single-line definition excluding LF; it is auxiliary syntax provenance, not
proof of a source. Records are sorted by occurrence span, repeated occurrences
are retained, and a consumed surface never yields nested locator records.
Calls return fresh JSON-compatible containers.

## Admitted syntax and exclusions

This is a deliberately finite grammar, not a Markdown, APA, BibTeX, HTML, or
general prose parser. All literal spaces in the formats below mean one ASCII
space. Exact reference keys are case-sensitive; no Unicode normalization is
performed.

- A surname is 1–64 codepoints, alphabetic at both ends, with only alphabetic
  characters, ASCII hyphen/apostrophe, or U+2019 inside. An initial is one
  capital ASCII letter. A year is `1000`–`2999` as four ASCII digits with an
  optional lowercase ASCII suffix letter.
- A DOI is optional ASCII case-insensitive `doi:`, then `10.`, 4–9 ASCII
  digits, `/`, and a 1–256-character suffix. The suffix starts with an ASCII
  alphanumeric and thereafter uses ASCII alphanumerics or `._;/:+-()`.
  Parentheses balance left-to-right at depth at most two. The returned DOI
  drops `doi:` and lowercases ASCII letters. Thus
  `10.1016/s0140-6736(97)11096-0` is admitted.
- An HTTP(S) URL has at most 2,048 ASCII characters, a nonempty hostname,
  no userinfo, and any explicit port in `0..65535` and nonempty. Whitespace,
  controls, backslash, quotes, backticks, angle/square/curly brackets are
  unsupported. The URL is returned byte-for-character as supplied without
  canonicalizing case, escapes, or paths. Literal parentheses are admitted
  only in a `doi.org` or `dx.doi.org` DOI URL whose complete path is a
  valid DOI, without explicit port, query, or fragment. Such a URL also
  returns its normalized DOI. Other valid DOI-host URLs may return a URL
  with a null DOI. These syntax rules do not authorize any request to a host.

Bare DOI/URL candidates start outside consumed regions and cannot immediately
follow a Unicode alphanumeric, underscore, slash, or escaping backslash.
Their maximal token stops at whitespace or an angle bracket, quote, backtick,
or backslash. Terminal `.,;:!?` and unmatched terminal `)]}` are removed
iteratively; balanced DOI parentheses remain. The entire remaining token
must validate. A failed larger candidate is consumed opaquely; no valid
prefix or interior URL is recovered. Whole locators in links or definitions
receive no terminal-punctuation removal.

Fenced code starts on a line with 0–3 spaces and at least three backticks or
tildes. It closes only on a line with 0–3 spaces, the same marker repeated at
least as many times, and then only spaces/tabs. An unclosed fence excludes
the rest of the text. Outside fences, an unescaped inline backtick run closes
at the next same-length run on that line; an unclosed run excludes the line
remainder. Code, definitions, the reference section, quoted content, and
atomic bracket ranges do not yield nested citation tokens. An odd run of
backslashes escapes a citation/quote/link opener; an even run does not.

A column-zero footnote definition has `[^LABEL]:` with an ASCII
`[A-Za-z0-9_-]{1,32}` label. It needs exactly one space after the colon
and a whole DOI/URL or the complete bibliography entry below. A continuation
line beginning with a tab or at least four spaces makes that definition
unsupported. Duplicate definitions remain ambiguous, including identical
copies. Broader definition-like lines, including ordinary `[LABEL]:`
references, malformed labels and their continuations, are consumed without
emitting interior locators. An occurrence `[^LABEL]` has
`missing_definition`, `multiple_definitions`, or
`unsupported_definition` when appropriate. Only a unique supported
definition supplies normalized fields and a definition span.

The first non-code line exactly `References` or `## References` begins
a reference section through EOF. Candidate entries start at column zero
with `SURNAME, INITIAL. (YEAR).`; even an unsupported body registers the
exact surname/year key. A supported whole entry is
`SURNAME, INITIAL. (YEAR). TITLE. LOCATOR`, with a 1–512-character
non-control title and no leading/trailing whitespace. The final `. `
before the whole locator separates the title; interior title periods remain.
An unescaped `(SURNAME, YEAR)` before that section emits only when the
exact key has at least one candidate. One supported candidate is extracted;
duplicates or one unsupported candidate are ambiguous. Ambiguous author-year
records keep only literal surname/year, with null DOI/URL/title and spans
other than the occurrence. Unmatched parenthetical prose remains outside
the grammar, although it can block unique quote association.

A one-line `[LABEL](URL)` admits a nonempty, at most 200-character label
without square/round brackets, backslash, backtick, LF, or leading/trailing
spaces/tabs. Its destination is one whole admitted URL, with no title or
padding. A DOI URL with balanced suffix parentheses is allowed. A bracket
range consumes atomically from its first `[`. Code-masked delimiters do
not close its bracket bodies or destination. A nested, escaped, or unclosed
first/second bracket body consumes the rest of that line opaquely. In a
destination, a backslash, square bracket, parenthesis nesting beyond three
including the outer pair, or no matching outer `)` also consumes the line
tail. A balanced, structurally closed destination within that depth is
consumed only through its outer `)` even when its whole URL is invalid
(for example `[x](bad)` or `[x](bad(inner))`), so a later bare locator
on the line can still be recognized. A closed but unsupported link,
an image `![...](...)`, an escaped link, or a reference-style
`[LABEL][ID]` likewise yields no citation or interior fallback. Two adjacent
exact footnotes `[^a][^b]` remain two occurrences. The scanner advances
past each entire consumed range.

## Location and small quote association

A non-ambiguous author-year, link, URL, or DOI record attaches to its
containing paragraph, a maximal run of nonblank lines. A blank line has
only spaces/tabs. The corridor includes the first line's leading whitespace
and interior LF, ending before its last terminating LF. This is a location,
not a proposition; `attachment_method` is `paragraph`. Footnotes and
ambiguous records have null corridor and `none` attachment.

Simple nonempty same-line ASCII `"…"` and curly `“…”` pairs provide
quote-content spans without delimiters. Delimiters inside atomic brackets
or code do not open/close a quote. Escaped, unclosed, or mixed-style
quote-like remainders are excluded conservatively; empty pairs produce
no quote span. Citation-looking content inside a valid quote is excluded
from citation recognition. A non-ambiguous citation receives a preceding
valid quote span only if the quote closes on the same line, the gap is
spaces/tabs only, and it is the sole citation-like surface in its
comma/semicolon/space/tab cluster. Unsupported brackets, failed locator
tokens, and unmatched exact author-year markers also block uniqueness,
without appearing as records. No source-text authentication or semantic
quote attribution is implied.

## Synthetic examples and limits

```python
extract_citations("A result.[^n]\n\n[^n]: doi:10.1234/alpha\n")
# one footnote: occurrence [9,13), definition [15,38), DOI 10.1234/alpha

extract_citations("A result (Smith, 2020).\n\nReferences\n"
                  "Smith, A. (2020). Alpha. doi:10.1234/alpha\n")
# one author_year: occurrence [9,22), definition [36,78),
# title Alpha, paragraph [0,23)

extract_citations("“A result” [study](https://example.org/a).\n")
# one markdown_link: occurrence [11,41), quote content [1,9),
# paragraph [0,42); label "study" is not a title
```

No multi-author or `et al.` group, narrative `Smith (2020)`, page
locator, numeric endnote, HTML anchor, reference-style Markdown link,
multiline entry, arbitrary DOI suffix, or general direct-quote detection is
supported. A no-match result never proves absence, and this API emits no
recall estimate, confidence, eligible-document denominator, claim judgment,
source-health/access result, or citation-integrity rating.
