# Manuscript Index Builder: a back-of-book index the author only has to approve

**Status:** **Proposed spec, 2026-10-29. Unbuilt.** Awaits owner admission and spec review; no build until both. Roadmap: `ROADMAP.md` → [Horizon Capacities](../ROADMAP.md#horizon-capacities) Tier 2, item 20. Proposed implementation surface: `plugins/apodictic/scripts/book_index.py`, `validate.sh book-index`, a `core-editor/references/manuscript-indexing.md` module and a `/book-index` command.
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
| Entries for passing mentions | Every anchor carries a `substantive` / `passing` flag; passing anchors never become locators unless the author overrides (I6) |
| Excessive, redundant subheadings | Subheading discipline checks: no subheading that repeats its parent's locators, no lone subheading, a per-heading cap (I5) |
| Long strings of undifferentiated locators | A heading or subheading with more than six locators must be broken down (I4), following the usual Chicago guidance |
| Locators that fail a copyeditor's page test | Page numbers are never written by a model. They are looked up mechanically from the proof PDF by quoted anchor text (Phase B), and an anchor that cannot be found is reported, never guessed (P1) |
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
| Page numbers | Tool, by mechanical lookup in the proofs |
| Page ranges (45–52) for extended discussions | Tool, from anchor spans |
| See and See also bookkeeping, blind and circular references | Tool generates; validator enforces |
| Alphabetizing and press-style formatting | Tool, deterministic, from a style profile |
| Fitting the press's page allowance | Tool trims lowest-weight entries and reports what it cut |
| Redoing page numbers after late corrections | Tool reruns placement against new proofs; no headings are touched |

The author's remaining work is one review session over the heading sheet, plus a final read of the typeset index.

## Firewall fit

An index is paratext about what the manuscript discusses. The tool **never changes the manuscript** and never invents content: every heading must point at real passages, and the validator proves the anchors exist (I2). Headings are proposals, and nothing becomes final without the author's decision, the same gate the [approval-gated reconstruction](approval-gated-reconstruction.md) workflow uses.

One scope question remains for the owner: `ROADMAP.md` §Not Planned excludes line editing and copyediting as a different discipline. Indexing is a production task like copyediting. This spec proposes admitting it as a separate production module that shares the engine's extraction and validation machinery, with copyediting still excluded (design call D1).

## How it works: two phases

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
    {"id": "IX-042.a1", "locus": "Ch 3 ¶12", "quote": "judgment that must find the universal for a given particular", "role": "substantive", "span_end": null},
    {"id": "IX-042.a2", "locus": "Ch 7 ¶4", "quote": "returns to reflective judgment as the faculty", "role": "substantive", "span_end": "Ch 7 ¶9"},
    {"id": "IX-042.a3", "locus": "Ch 9 ¶2", "quote": "as with reflective judgment, the", "role": "passing", "span_end": null}
  ],
  "subheadings": [],
  "see": [],
  "see_also": ["IX-017"]
}
-->
```

- `kind` ∈ `name` / `place` / `work` / `concept` / `term` (closed).
- `status` ∈ `proposed` / `accepted` / `renamed` / `merged` / `dropped` (closed). `merged` carries `merged_into`.
- `quote` is a short verbatim string from the passage, long enough to be unique in the manuscript (the validator checks both). It is the anchor Phase B uses to find the page.
- `span_end` marks an extended discussion that becomes a page range.
- `weight` orders the review sheet and drives length trimming. It is a ranking aid, never shown in the index.

Alongside the blocks, the run writes a **review sheet**: headings grouped by kind and sorted by weight, each with its preferred form, variants, chapter spread and two or three substantive passages in context. The author marks each one accept, rename, merge or drop. Unmarked headings stay `proposed` and are excluded from output, so silence never publishes anything.

### Phase B: placement (proofs stage)

Input: the accepted map plus the typeset proof PDF.

1. Extract page text and build the page-label map (printed folio versus PDF page index; roman front matter; unnumbered pages).
2. For each accepted anchor, find its `quote` in the proof text after normalizing line-break hyphenation, ligatures, curly quotes and whitespace. The match must be unique.
3. Assign the folio. A `span_end` that lands on a later page yields a range.
4. Anything not found or not unique goes to an **unresolved list** for the author. No locator is ever estimated.
5. Format the index under a style profile (indented or run-in, letter-by-letter or word-by-word, range style, See/See also placement) and write it out, plus the exports.

Because anchors are quotes, repagination costs one rerun of Phase B.

## The `book-index` validator

Mechanical checks, ERROR unless marked W:

- **I1 schema.** `index_heading.v1` contract, closed enums, unique ids.
- **I2 anchors exist.** Every `quote` occurs, after normalization, exactly once in the manuscript snapshot. This is a real firewall proof, stronger than the Continuity Bible's shape-only locus check, because the manuscript is an input here.
- **I3 cross-reference integrity.** No See or See also to a missing, dropped or merged heading; no circular See; See only from a heading with no locators; See also only from a heading that has locators.
- **I4 locator discipline.** No heading or subheading with more than six locators (configurable) without subheadings.
- **I5 subheading discipline.** No lone subheading; no subheading whose locators equal its parent's; no more than a configurable number of subheadings per heading (default 12).
- **I6 passing mentions.** Passing anchors never produce locators unless they carry an author override marker.
- **P1 placement completeness.** Every accepted anchor is either placed or on the unresolved list.
- **P2 folio sanity.** Folios are monotonic with PDF page order within each numbering sequence.
- **W1 coverage.** Chapters with no substantive anchors are flagged as possible under-indexing.
- **W2 length budget.** Estimated index length against the press allowance, when one is given.

**Honest limit.** The validator can prove anchors exist, references resolve, and locators came from the proofs. It cannot prove that a `substantive` flag is a good call or that a heading is the word a reader would look up. Those are the judgment calls left to the author, and the evaluation below measures them.

## Evaluation before release

Run on at least one public-domain or permissioned book that already has a professional index, at both phases:

- **Locator accuracy** on placed anchors: 100% required, checked by a copyeditor-style sample of 50 locators against the proofs.
- **Heading recall** against the professional index, reported per kind.
- **Passing-mention rate** and **subheading excess** against the same index.
- Report the numbers in the module doc. Do not claim parity with professional indexes.

## Positioning

The output is labeled the author's draft index, built for the author's review. The docs say plainly that ASI recommends against publishing AI-generated indexes, explain which of its failure modes this design addresses mechanically and which still rest on the author, and suggest professional review for trade titles. The Cindex/SKY export makes that handoff cheap.

## Where it lives

A core-editor workflow module (`core-editor/references/manuscript-indexing.md`), invoked by a `/book-index` command with `map` and `place` modes, routed like `/legal-risk` and `/world-bible`. The command is named `/book-index` because `/apodictic` is already the capability index. Nonfiction first: argument-shaped and narrative nonfiction are where indexes are expected.

## Dependencies

Phase A is stdlib-only. Phase B needs PDF text extraction. Proposed: an optional `pypdf` import, loaded lazily, with Phase B refusing cleanly (and saying how to install it) when the package is missing, and tests that `skipif` without it. A model reading the PDF is rejected for locators because it is not deterministic (design call D3).

## Increment plan

1. **Concept map.** `index_heading.v1`, the module, the review sheet, `book_index.py` with I1–I6 and W1, a canonical worked example in `--check-all`, and the `/book-index map` command.
2. **Placement.** Proof PDF extraction, page-label map, anchor matching, P1–P2, W2, style profiles and formatted output (plain text and DOCX).
3. **Exports and late changes.** Tab-delimited export for Cindex and SKY import, embedded-tag export (Word XE fields, LaTeX `\index`), and a repagination diff that lists every locator that moved.

## Open design calls (for the owner)

- **D1 Scope.** Admit indexing as a production module despite the copyediting exclusion in §Not Planned? *Recommended: yes, with copyediting still excluded.*
- **D2 Locator route.** Place locators from the proof PDF (works with any press), from embedded tags in the manuscript (survives repagination but needs the press to keep the tags), or both? *Recommended: PDF first; embedded-tag export in Increment 3.*
- **D3 PDF dependency.** Optional `pypdf`, the poppler `pdftotext` binary, or the host model reading the PDF? *Recommended: optional `pypdf`.*
- **D4 Positioning.** Label the output as a draft for author review and cite ASI's recommendation in the docs? *Recommended: yes.*
- **D5 Fiction.** Nonfiction only, or allow fiction on request? *Recommended: nonfiction first; fiction allowed on request with no fiction-specific features.*
