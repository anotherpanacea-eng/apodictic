# Manuscript Index Builder: a back-of-book index the author only has to approve

**Status:** **Proposed spec, 2026-10-29. Unbuilt.** Owner design calls resolved 2026-10-29 (§Resolved design calls); Codex spec review applied. Awaits owner admission; no build until then. Roadmap: `ROADMAP.md` → [Horizon Capacities](../ROADMAP.md#horizon-capacities) Tier 2, item 20. Proposed implementation surface: `plugins/apodictic/scripts/book_index.py`, `validate.sh book-index`, a `core-editor/references/manuscript-indexing.md` module and a `/book-index` command.
<!-- built-when: plugins/apodictic/scripts/book_index.py -->

## Why

Authors hate making their own indexes. Many presses hand the index to the author, either to write or to pay for, at the worst possible moment: the proofs have just arrived, the schedule is tight, and the job is days of tedious marking, page-hunting, alphabetizing and checking. Most of that labor is mechanical. A small part of it is judgment: which concepts a reader will look up, under what words, and how a big topic should be broken down.

The design center of this spec is to **take every painful part away from the author and leave only the judgment calls, packaged as a short review.** The tool does the harvesting, the finding, the page numbers, the ranges, the sorting, the cross-reference bookkeeping and the formatting. The author accepts, renames, merges or drops proposed headings, then looks over the typeset result.

## Prior art and what this spec takes from it

**Dedicated indexing software (Cindex, SKY Index, Macrex).** Professional indexers work in record-based programs: one record per entry (heading, subheadings, locators), with configurable sort rules (letter-by-letter or word-by-word, symbol and numeral handling), locator formatting and truncation, and error scans that flag circular or nonexistent cross-references ([NISO, "Standards for Indexing"](https://www.niso.org/niso-io/2015/12/standards-indexing)). These tools do none of the choosing; they make a human's choices fast and consistent. **We take:** the record model, deterministic sorting and formatting as press-style settings, mechanical cross-reference checks, and an export the indexer's own tools can import, so an author who hires a professional hands over a head start.

**Embedded indexing (Word XE fields, InDesign index markers, LaTeX `\index` with makeindex or xindy).** Index terms are tagged in the manuscript and the page numbers are generated at typesetting, so the index survives repagination. It only works when the press's production workflow preserves the tags. **We take:** an optional embedded-tag export (Increment 3), and the core lesson that locators should be generated from anchors, never typed.

**Concordance generators (PDF Index Generator and similar).** They list words and the pages they occur on. The hard part of indexing is choosing what to include, and a concordance does not choose ([Virginia DH abstract on machine-aided index generation](https://dh-abstracts.library.virginia.edu/works/698)). **We take:** nothing beyond the mechanical page lookup, which a concordance does well.

**AI indexing products and the indexers' evaluation of them.** Several products now draft indexes with LLMs (Indexia, AI-Indexing, IndexerLabs, IndexStudio among those the American Society for Indexing lists). Indexia, for example, takes an uploaded manuscript, extracts names, places, concepts and themes, and offers an editor before export, including a Cindex-compatible format ([interview with Indexia's creators](https://armedwithabook.com/a-conversation-with-the-creators-of-indexia/)). ASI's AI Committee has published three white papers (August 2025, November 2025, March 2026) and a statement, updated March 2026, recommending that AI-generated indexes not be used in books at this time ([ASI statement via ANZSI](https://www.anzsi.org/asi-statement-on-ai-and-book-indexing/); [ASI white paper](https://asindexing.org/ai-news/white-paper-ai-index/); [supplement](https://asindexing.org/ai-news/supplement-to-white-paper-ai-and-indexing/)). The failure modes they document are specific, and this spec is built against each one:

| ASI-documented failure | This spec's answer |
|---|---|
| Under-indexing (earlier models) | Coverage check per chapter (W1) and a recall measurement against a professional index before release (§Evaluation) |
| Entries for passing mentions | Every anchor carries a `substantive` / `passing` flag; passing anchors never become locators unless the author overrides (I5) |
| Excessive, redundant subheadings | Subheading discipline checks: no subheading that repeats its parent's locators, no lone subheading, a per-heading cap (W3) |
| Long strings of undifferentiated locators | A heading or subheading with more than six locators is flagged for breaking down (W2), following the usual Chicago guidance |
| Locators that fail a copyeditor's page test | Page numbers are never written by a model. They are looked up mechanically from the proof PDF by quoted anchor text (Phase B), and an anchor that cannot be found is reported, never guessed (P1, P2) |
| Short snippets were not enough context for reviewers | The author's review sheet shows each heading with its substantive passages in context, grouped, with the chapter spread |
| Roughly 70% of entries needing human remediation | The product is framed as the author's draft index for review, never as publication-ready (§Positioning) |

**Standards.** ISO 999:1996, NISO TR02-1997 and *The Chicago Manual of Style*'s indexes chapter define the conventions the formatter and validator encode (sort order, See versus See also, run-in versus indented style, inclusive page ranges).

**Fleet prior art.** No earlier indexing work exists in the fleet repos or the project files (searched 2026-10-29). The closest APODICTIC surfaces are the [Continuity Bible](continuity-bible.md) (locus-anchored extraction of names and aliases) and the [PDF navigation](annotated-manuscript-pdf-navigation.md) work (offline PDF handling).

## The pain map

| Painful part | Who does it |
|---|---|
| Deciding what is worth indexing | Tool proposes headings, ranked; author accepts or drops in bulk |
| Finding every substantive discussion of each topic | Tool, with the passing-mention filter |
| Gathering variant names, spellings and synonyms | Tool consolidates under one preferred form; author confirms the form |
| Breaking big topics into subheadings | Tool proposes; validator caps and dedupes; author renames |
| Locators, when wanted (pages, ebook locations, line or paragraph numbers) | Tool, by mechanical lookup under the chosen scheme |
| Ranges (45–52) for extended discussions | Tool, from anchor spans |
| See and See also bookkeeping, blind and circular references | Tool generates; validator enforces |
| Alphabetizing and press-style formatting | Tool, deterministic, from a style profile |
| Fitting the press's page allowance | Tool proposes the lowest-weight cuts; author approves them |
| Redoing locators after late corrections | Tool reruns the locator step; no headings are touched |

The author's remaining work is one review session over the heading sheet, plus a final read of the finished index.

## Firewall fit

An index is paratext about what the manuscript discusses. The tool **never changes the manuscript** and never invents content: every heading must point at real passages, and the validator proves the anchors exist (I2), and nothing the author has not accepted reaches the output (I4). Headings are proposals, and nothing becomes final without the author's decision, the same gate the [approval-gated reconstruction](approval-gated-reconstruction.md) workflow uses.

**Scope.** Indexing is a production task. The owner admitted it on 2026-10-29 as a separate production module that shares the engine's extraction and validation machinery. The same ruling reopened copyediting, with the caution that good copyediting leaves alone much that looks like error when it is the book's voice and register. Copyediting gets its own spec; it is not part of this one.

## How it works: topic map first, locators optional

### Phase A: the concept map (manuscript stage)

Input: the manuscript in any format APODICTIC already reads, ideally once the text is substantively final. Optional inputs it consumes when present: the Continuity Bible's entities and aliases, and `Argument_State.md`'s named claims and concepts for argument-shaped nonfiction.

Output: `[Project]_Index_Map_[runlabel].md` in the project root, one `apodictic.index_heading.v1` block per proposed heading:

```markdown
<!-- apodictic:index_heading
{
  "schema": "apodictic.index_heading.v1",
  "id": "IX-042",
  "heading": "judgment, reflective",
  "kind": "concept",
  "variants": ["reflective judgment", "reflecting judgment"],
  "status": "proposed",
  "weight": 0.81,
  "anchors": [
    {"id": "IX-042.a1", "locus": "Ch 3 ¶12", "quote": "judgment that must find the universal for a given particular", "role": "substantive", "end_quote": null},
    {"id": "IX-042.a2", "locus": "Ch 7 ¶4", "quote": "returns to reflective judgment as the faculty", "role": "substantive", "end_quote": "which is why the spectator, not the actor"},
    {"id": "IX-042.a3", "locus": "Ch 9 ¶2", "quote": "as with reflective judgment, the", "role": "passing", "end_quote": null}
  ],
  "subheadings": [],
  "see": [],
  "see_also": ["IX-017"]
}
-->
```

- `kind` ∈ `name` / `place` / `work` / `concept` / `term` (closed).
- `status` ∈ `proposed` / `accepted` / `renamed` / `merged` / `dropped` (closed). `merged` carries `merged_into`.
- `quote` is a short verbatim string from the passage, long enough to be unique in the manuscript (the validator checks both). It is the anchor Phase B uses to find the page. `locus` is for the author's review sheet only; placement never uses it.
- `end_quote` closes an extended discussion that becomes a range. It is a second verbatim quote, so Phase B can find where the discussion ends the same way it finds the start. A `context` field (a few words before and after) is added only when a quote cannot be made unique on its own.
- `weight` orders the review sheet and drives length trimming. It is a ranking aid, never shown in the index.

Alongside the blocks, the run writes a **review sheet**: headings grouped by kind and sorted by weight, each with its preferred form, variants, chapter spread and two or three substantive passages in context. The author marks each one accept, rename, merge or drop. Unmarked headings stay `proposed` and are excluded from output, so silence never publishes anything.

### Phase B: locators (optional, pluggable)

The core deliverable is the topic map: headings, subheadings and See/See also, each tied to real passages. It can be output with no locators at all, as a topic guide or as a head start for a professional indexer. When locators are wanted, the author picks a **locator scheme**, and Phase B resolves every anchor under it. Every scheme meets one contract: each anchor resolves from its quote to a locator with a trace record, or goes to the unresolved list with a reason. No scheme ever estimates.

| Scheme | Locator | Source |
|---|---|---|
| `paragraph` | chapter and paragraph, or the manuscript's own section numbers | the manuscript itself; needs no second file |
| `page` | printed page (folio) | the typeset proof PDF (procedure below) |
| `line` | line number | a line-numbered edition or text |
| `ebook` | ebook location | the EPUB, or a location table the author exports |
| `embedded` | none; tags are written instead | Word XE fields or LaTeX `\index` commands, and the typesetter generates the numbers |

Kindle locations are computed by Amazon from the published file, so the `ebook` scheme reads them from an author-supplied export rather than calculating them.

**The `page` scheme.** Input: the accepted map plus the typeset proof PDF.

1. Extract page text and build the page-label map: the PDF's own page labels when present, otherwise an author-supplied map (for example "PDF page 15 is folio 1; front matter is roman"). With neither, Phase B stops and asks; it never guesses folios. A proof with no extractable text (a scanned image) is refused with that reason.
2. For each accepted anchor, find its `quote` in the proof text, searching across page breaks. Normalization is conservative and fixed: line-break hyphenation, ligatures, curly versus straight quotes, and whitespace. Nothing fuzzier, so a quote changed by copyediting fails to match instead of matching the wrong place.
3. The match must be unique; `context` breaks a tie when present. A quote that spans a page break takes the page where it starts.
4. Assign the folio. An `end_quote` found on a later page yields a range; one found earlier than its start, or not found, sends the anchor to the unresolved list.
5. Anything not found, not unique, or reversed goes to an **unresolved list** for the author, with the reason. No locator is ever estimated.
6. Format the index under a style profile (indented or run-in, letter-by-letter or word-by-word, range style, See/See also placement) and write it out, plus the exports. Each output locator keeps a trace record: anchor id, PDF page index, folio and match offset. Other schemes keep the equivalent (source position and locator).

Because anchors are quotes, repagination or a new edition costs one rerun of Phase B under any scheme. Copyedits made after Phase A show up as unresolved anchors, which the author fixes by updating the quote.

## The `book-index` validator

Mechanical checks, ERROR unless marked W:

- **I1 schema.** `index_heading.v1` contract, closed enums, unique ids.
- **I2 provenance.** Every `quote` and `end_quote` occurs, after the fixed normalization, exactly once in the manuscript snapshot (or once with its `context`). This proves the anchors are real, a stronger firewall check than the Continuity Bible's shape-only locus check, because the manuscript is an input here. Locator placement is a separate check (P1).
- **I3 cross-reference integrity.** No See or See also to a missing or dropped heading; a reference to a merged heading is rewritten to its `merged_into` target before output; no circular See; See only from a heading with no anchors of its own; See also only from a heading that has anchors.
- **I4 publication gate.** Only `accepted` and `renamed` headings, and the merged anchors they absorb, reach the output. A `proposed` heading in the formatted index is an error.
- **I5 passing mentions.** Passing anchors never produce locators unless they carry an author override marker.
- **P1 placement accounting.** When a scheme is chosen, every anchor of a published heading is either placed, with a trace record, or on the unresolved list with a reason. Nothing is dropped silently.
- **P2 locator integrity.** Every output locator matches its trace record; locators are monotonic with source order within each numbering sequence (for `page`, PDF page order); every range starts no later than it ends; duplicate locators under one heading are merged.
- **W1 coverage.** Chapters with no substantive anchors are flagged as possible under-indexing.
- **W2 locator strings.** A heading or subheading with more than six substantive anchors (configurable) and no subheadings.
- **W3 subheadings.** A lone subheading, a subheading whose anchors equal its parent's, or more than a configurable number of subheadings per heading (default 12).
- **W4 length budget.** Estimated index length against the press allowance, when one is given, with the proposed lowest-weight cuts for the author to approve.

W2 and W3 are style warnings, not correctness errors, because presses and subjects differ; `--strict` promotes them for the canonical example only.

**Honest limit.** The validator can prove anchors exist, references resolve, and locators came from the chosen source. It cannot prove that a `substantive` flag is a good call or that a heading is the word a reader would look up. Those are the judgment calls left to the author, and the evaluation below measures them.

## Evaluation before release

Run on at least one public-domain or permissioned book that already has a professional index, for the topic map and for each locator scheme built:

- **Locator accuracy.** Correctness of every placed locator rests on the trace records and P2, which are mechanical. A copyeditor-style audit of a random sample of 50 locators against the printed pages checks that the trace matches what a reader sees (for `page`: page labels and cross-page quotes). Report the sample result and its confidence interval; zero errors in 50 is evidence, not proof of corpus-wide accuracy.
- **Heading recall** against the professional index, reported per kind.
- **Passing-mention rate** and **subheading excess** against the same index.
- Report the numbers in the module doc. Do not claim parity with professional indexes.

## Positioning

A human must review and endorse the index before it is used: nothing reaches the output without the author's acceptance (I4), and the docs say so. The ASI evaluations above are prior-art evidence that shaped the design. APODICTIC is not bound by ASI guidance, and the docs do not present it as a rule. They do say which of the documented failure modes this design checks mechanically and which still rest on the author's review. An author who wants a professional indexer can hand over the Cindex/SKY export.

## Where it lives

A core-editor workflow module (`core-editor/references/manuscript-indexing.md`), invoked by a `/book-index` command with `map` and `locate` modes, routed like `/legal-risk` and `/world-bible`. The command is named `/book-index` because `/apodictic` is already the capability index. Nonfiction only: argument-shaped and narrative nonfiction are where indexes are expected. Fiction gets an index only in scholarly or annotated editions, which are handled as nonfiction apparatus.

## Dependencies

Phase A and the `paragraph` scheme are stdlib-only. The `page` scheme needs PDF text extraction: an optional `pypdf` import, loaded lazily, with the `page` scheme refusing cleanly (and saying how to install it) when the package is missing, and tests that `skipif` without it. A model reading the PDF is rejected for locators because it is not deterministic (design call D3).

## Increment plan

1. **Concept map.** `index_heading.v1`, the module, the review sheet, `book_index.py` with I1–I5 and W1–W3, a canonical worked example in `--check-all`, and the `/book-index map` command.
2. **Locators.** The scheme contract, the `paragraph` and `page` schemes (PDF extraction, page-label map, anchor matching), P1–P2, W4, style profiles and formatted output (plain text and DOCX). A locator-free topic-map output ships here too.
3. **More schemes and exports.** The `line`, `ebook` and `embedded` schemes, tab-delimited export for Cindex and SKY import, and a re-locate diff that lists every locator that moved.

## Resolved design calls (owner, 2026-10-29)

- **D1 Scope.** Indexing is admitted as a production module. Copyediting is reopened too, as its own voice- and register-aware spec, separate from this one.
- **D2 Locators.** Optional and pluggable. Topics and references are the core; pages, ebook locations, line numbers and the rest are schemes (§Phase B).
- **D3 PDF dependency.** Optional `pypdf`, for the `page` scheme only.
- **D4 Positioning.** A human must review and endorse. ASI guidance informs the design but is not binding.
- **D5 Fiction.** Nonfiction only; fiction appears only as scholarly or annotated editions.
