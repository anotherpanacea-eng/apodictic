# Manuscript Index Builder: a back-of-book index the author only has to approve

**Status:** **Proposed spec, 2026-10-29. Unbuilt.** Owner design calls resolved 2026-10-29 (§Resolved design calls). Codex review and the fleet `/spec-review` panel (verdict NEEDS-REWORK, 1 P1 and 9 P2) applied 2026-10-29. Awaits owner admission; no build until then. Roadmap: `ROADMAP.md` → [Horizon Capacities](../ROADMAP.md#horizon-capacities) Tier 2, item 20. Proposed implementation surface: `plugins/apodictic/scripts/book_index.py`, `validate.sh book-index`, a `core-editor/references/manuscript-indexing.md` module and a `/book-index` command.
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
| Entries for passing mentions | Every anchor carries a `substantive` / `passing` flag; passing anchors never become locators; the author promotes one by changing its role |
| Excessive, redundant subheadings | Subheading discipline checks: no subheading that repeats its parent's anchors, no lone subheading, a per-heading cap (W3) |
| Long strings of undifferentiated locators | A heading or subheading with more than six substantive anchors is flagged for breaking down (W2), following the usual Chicago guidance |
| Locators that fail a copyeditor's page test | Page numbers are never written by a model. They are looked up mechanically from the proof PDF by quoted anchor text (Phase B), and an anchor that cannot be found is reported, never guessed, and anchors that land out of manuscript order are held back (P1, P2) |
| Short snippets were not enough context for reviewers | The author's review list shows each heading with every anchor in context, grouped, with the chapter spread |
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
| Fitting the press's page allowance | Tool lists the lowest-weight headings as cut candidates; the author drops any they agree with |
| Redoing locators after late corrections | Tool reruns the locator step; no headings are touched |

The author's remaining work is one review session over the heading list, plus a final read of the finished index.

## Firewall fit

An index is paratext about what the manuscript discusses. The tool **never changes the manuscript** and never invents passages: every heading either has anchors the validator proves exist in the manuscript (I2) or only redirects to a heading that does (a See-only heading). Headings are proposals, and only headings the author accepted reach the output (I4).

**Scope.** Indexing is a production task, admitted by the owner on 2026-10-29. It lives as a core-editor reference module because it reuses core-editor's manuscript snapshot and its quote-anchor rules; it is not an audit and emits no findings. Copyediting is out of scope here (ROADMAP §Not Planned records the owner's reopening of it as a separate spec).

## How it works: topic map first, locators optional

### Phase A: the topic map (manuscript stage)

Input: the manuscript, ideally once the text is substantively final. The `/book-index map` command writes (or reuses) the run's `[Project]_Manuscript_Snapshot_[runlabel].md`, the same LF-normalized snapshot the [annotated-manuscript](annotated-manuscript.md) layer uses, and records its path and sha256 in the map header. Phase A works with nothing else. Two optional inputs, when present, only **seed** proposed headings and their loci never become anchors: Continuity Bible `canon_fact.v1` `entity` values (aliases come from facts whose `attribute` is `alias`), and the `argument_spine.v1` `key_terms`, `thesis` and `subclaims` that seed `Argument_State.md`.

Output: `[Project]_Index_Map_[runlabel].md` in the project root: a header block, then one `apodictic.index_heading.v1` block per heading.

```markdown
<!-- apodictic:index_map
{"schema": "apodictic.index_map.v1", "snapshot_path": "Book_Manuscript_Snapshot_r1.md", "snapshot_sha256": "<64 lowercase hex>"}
-->

<!-- apodictic:index_heading
{
  "schema": "apodictic.index_heading.v1",
  "id": "IX-042",
  "heading": "judgment, reflective",
  "kind": "concept",
  "variants": ["reflective judgment", "reflecting judgment"],
  "status": "accepted",
  "accepted_hash": "<64 lowercase hex>",
  "weight": 0.81,
  "anchors": [
    {"id": "IX-042.a1", "quote": "judgment that must find the universal for a given particular", "role": "substantive", "end_quote": null}
  ],
  "subheadings": [
    {"id": "IX-042.s1", "label": "and the spectator", "anchors": [
      {"id": "IX-042.s1.a1", "quote": "returns to reflective judgment as the faculty", "role": "substantive", "end_quote": "which is why the spectator, not the actor"}
    ]},
    {"id": "IX-042.s2", "label": "Kant on", "anchors": [
      {"id": "IX-042.s2.a1", "quote": "Kant never wrote the political philosophy", "role": "substantive", "end_quote": null},
      {"id": "IX-042.s2.a2", "quote": "as with reflective judgment, the", "role": "passing", "end_quote": null}
    ]}
  ],
  "see": [],
  "see_also": ["IX-017"]
}
-->
```

**`index_heading.v1` fields.** Required unless marked optional. I1 checks every row.

| Field | Type | Rule |
|---|---|---|
| `schema` | string | `apodictic.index_heading.v1` |
| `id` | string | `^IX-\d{3,}$`, unique in the map |
| `heading` | string | non-empty; the preferred form as printed |
| `kind` | enum | `name` / `place` / `work` / `concept` / `term` |
| `variants` | string[] | may be empty; alternate forms folded into this heading |
| `status` | enum | `proposed` / `accepted` / `merged` / `dropped` |
| `accepted_hash` | string | required when `status` is `accepted`, absent otherwise (see I4) |
| `merged_into` | string | required when `status` is `merged`, absent otherwise; an existing heading id |
| `weight` | number | in [0, 1]; orders the review list and cut candidates, never printed |
| `anchors` | anchor[] | the heading's own anchors, excluding any assigned to a subheading. Empty only for a See-only heading |
| `subheadings` | subheading[] | may be empty; one level deep |
| `see` | string[] | heading ids |
| `see_also` | string[] | heading ids |

An **anchor** is `{id, quote, role, end_quote}` with optional `context`. `id` is `<heading id>.a<N>` or `<subheading id>.a<N>`. `quote` is a single-line verbatim string; `role` ∈ `substantive` / `passing`; `end_quote` is a single-line verbatim string or null and closes an extended discussion that becomes a range. `context` (optional) is `{"before": str, "after": str}`, used only when `quote` cannot be made unique on its own; the matched text is `before + quote + after`.

A **subheading** is `{id, label, anchors}`. `id` is `<heading id>.s<N>`; `label` is non-empty; `anchors` follows the anchor rules and must hold at least one substantive anchor.

A **See-only heading** has `anchors: []`, no subheadings, a non-empty `see` and an empty `see_also`. Every other non-dropped heading has at least one substantive anchor of its own or in a subheading.

**Author decisions.** The Index_Map is the only state. The run renders a read-only **review list** from it: headings grouped by kind and sorted by weight, each with its variants, chapter spread and every anchor shown in context from the snapshot, and the headings with the lowest weight marked as cut candidates when a length allowance is given. The author accepts, renames (edits `heading`), merges or drops; the command writes those decisions into the map only from the author's explicit replies. Accepting a heading sets `accepted_hash`, a sha256 over its `heading`, `variants`, `see`, `see_also`, and its own and its subheadings' anchor quotes and end quotes. A heading that has never been decided stays `proposed` and is never published, so silence publishes nothing.

### Phase B: locators (optional, pluggable)

The core deliverable is the topic map: headings, subheadings and See/See also, each tied to real passages. It can be output with no locators at all, as a topic guide or as a head start for a professional indexer. When locators are wanted, the author picks a **locator scheme**, and Phase B resolves every anchor of every accepted heading under it. Every scheme meets one contract: each anchor resolves from its quote to a locator, or goes to the unresolved list with a reason. No scheme ever estimates.

| Scheme | Locator | Source |
|---|---|---|
| `paragraph` | chapter and paragraph | the snapshot itself: the chapter is the nearest preceding chapter heading (the same heading lookup `annotation_manifest.py` uses), and paragraphs are blank-line-separated blocks after it, headings excluded |
| `page` | printed page (folio) | the typeset proof PDF (procedure below) |
| `line` | line number | a line-numbered edition or text |
| `ebook` | ebook location | the EPUB, or a location table the author exports |
| `embedded` | none; tags are written instead | Word XE fields or LaTeX `\index` commands, and the typesetter generates the numbers |

Kindle locations are computed by Amazon from the published file, so the `ebook` scheme reads them from an author-supplied export rather than calculating them.

**The `page` scheme.** Input: the accepted map plus the typeset proof PDF.

1. Extract page text and build the page-label map: the PDF's own page labels when present, otherwise an author-supplied map (for example "PDF page 15 is folio 1; front matter is roman"). With neither, the scheme stops and asks; it never guesses folios. A proof with no extractable text (a scanned image) is refused with that reason.
2. Search only the body page range by default. Front matter, running heads and back-matter notes are excluded unless the author includes them, because an epigraph, a preface or a running head can repeat a body sentence.
3. For each anchor, find its `quote` (with `context` when present) in the proof text, searching across page breaks. Proof-side normalization is fixed: line-break hyphenation, ligatures, curly versus straight quotes, and whitespace. This normalization applies to the proof only; the manuscript side stays as-is (I2). The match must be unique. A quote that spans a page break takes the page where it starts.
4. Assign the folio. An `end_quote` found later yields a range; one found earlier than its start, or not found, sends the anchor to the unresolved list.
5. **Order check.** Sort the placed anchors by their offset in the manuscript snapshot; their positions in the proof must be non-decreasing. An anchor out of order matched the wrong place (a copyedited sentence whose original wording survives elsewhere), so it goes to the unresolved list.
6. Anything not found, not unique, reversed or out of order goes to the **unresolved list** for the author, with the reason. The author fixes it by updating the quote, which re-opens the heading for acceptance (I4).
7. Format the index under a style profile (indented or run-in, letter-by-letter or word-by-word, range style, See/See also placement) and write it out. Match positions are printed with the unresolved list and on request; they are not a stored artifact.

Because anchors are quotes, repagination or a new edition costs one rerun of Phase B under any scheme.

## The `book-index` validator

`validate.sh book-index <index_map.md> <snapshot>`; with `--output <formatted index>` it also checks the output. A missing or mismatched snapshot is an ERROR, never a skip. Checks are ERROR unless marked W.

- **I1 schema.** Every field rule in the table above, including the See-only and substantive-anchor rules, the id patterns and the `accepted_hash`/`merged_into` presence rules.
- **I2 provenance.** The snapshot's sha256 equals the map header's. Every `quote` and `end_quote` (with `context` when present) occurs in the snapshot as-is and exactly once, by the non-overlapping count `annotation_manifest.quote_anchor` and A6 already use. This proves the anchors are real passages of this exact draft.
- **I3 cross-references.** Every See and See also target exists and is not dropped. A reference to a merged heading is rewritten to its `merged_into` target before output, and `merged_into` chains end at a non-merged heading. No circular See.
- **I4 acceptance and publication** (with `--output`, from Increment 2). Every `accepted` heading's `accepted_hash` equals the hash of its current content; a heading changed after acceptance is an ERROR until it is re-accepted. The output contains only accepted headings, the anchors merged into them, and their See-only redirects. Passing anchors produce no locators.
- **P1 placement accounting** (with `--output` and a scheme). Every anchor of a published heading is either placed or on the unresolved list with a reason. Nothing is dropped silently.
- **P2 locator order** (with `--output` and a scheme). Re-derives step 5 in memory: placed anchors are non-decreasing in proof position when sorted by snapshot offset, every range starts no later than it ends, and duplicate locators under one heading are merged.
- **W1 coverage.** A chapter with no substantive anchors, located by each anchor's I2 match offset in the snapshot, is flagged as possible under-indexing.
- **W2 locator strings.** A heading or subheading with more than six substantive anchors and no subheadings.
- **W3 subheadings.** A lone subheading, a subheading whose anchors equal its parent's, or more than twelve subheadings under one heading.

**Honest limit.** I2 proves an anchor is a real passage, not that the passage is about its heading; a real passage filed under a mistaken topic is the residual firewall risk, and the review list shows every anchor in context so the author judges it. I4 proves the output matches the recorded decisions and that nothing changed after acceptance. It does not prove a human made those decisions: the command records them from the author's replies, and the validator cannot tell an author's reply from a model's write. Approval-gated reconstruction has the same limit (its `actor` field is also written by the tool). The substantive/passing call and the choice of heading words are judgment the validator does not check.

**Minimum negative self-tests:** a quote that occurs twice, a missing quote, a snapshot sha mismatch, an `end_quote` before its `quote`, circular See, See to a dropped heading, `merged` without `merged_into`, an accepted heading edited after acceptance, a lone subheading, a See-only heading with `see_also`, and a proof anchor out of manuscript order. The canonical worked example in `--check-all` includes accepted, merged, dropped and See-only headings and a populated subheading.

## Evaluation before release

Run on at least one public-domain or permissioned book that already has a professional index. Report one overall heading-recall figure against that index, and for the `page` scheme a spot-check of 50 randomly sampled locators against the printed pages. Report the numbers in the module doc and do not claim parity with professional indexes.

## Positioning

A human must review and endorse the index before it is used: nothing reaches the output without the author's acceptance (I4), and the docs say so. The ASI evaluations above are prior-art evidence that shaped the design. APODICTIC is not bound by ASI guidance, and the docs do not present it as a rule. They do say which of the documented failure modes this design checks mechanically and which still rest on the author's review. An author who wants a professional indexer can hand over the Cindex/SKY export.

## Where it lives

A core-editor reference module (`core-editor/references/manuscript-indexing.md`), invoked by a `/book-index` command with `map` and `locate` modes, routed like `/legal-risk` and `/world-bible`. The command is named `/book-index` because `/apodictic` is already the capability index. Nonfiction only: argument-shaped and narrative nonfiction are where indexes are expected. Fiction gets an index only in scholarly or annotated editions, which are handled as nonfiction apparatus.

## Dependencies

Phase A, the validator and the `paragraph` scheme are stdlib-only. DOCX output reuses `annotation_export.py`'s stdlib OOXML writer. The `page` scheme needs PDF text extraction: an optional `pypdf` import, loaded lazily, with the scheme refusing cleanly (and saying how to install it) when the package is missing, and tests that `skipif` without it. A model reading the PDF is rejected for locators because it is not deterministic.

## Increment plan

1. **Topic map.** `index_map.v1` header, `index_heading.v1`, the module, the review list, `book_index.py` with I1–I3 and W1–W3, the negative self-tests, the canonical worked example in `--check-all`, and the `/book-index map` command.
2. **Locators and output.** The scheme contract, the `paragraph` and `page` schemes, I4, P1, P2, style profiles and formatted output (plain text and DOCX), plus a locator-free topic-map output.
3. **More schemes and exports.** The `line`, `ebook` and `embedded` schemes, and a tab-delimited export for Cindex and SKY import.

## Resolved design calls (owner, 2026-10-29)

- **D1 Scope.** Indexing is admitted as a production module.
- **D2 Locators.** Optional and pluggable. Topics and references are the core; pages, ebook locations, line numbers and the rest are schemes (§Phase B).
- **D3 PDF dependency.** Optional `pypdf`, for the `page` scheme only.
- **D4 Positioning.** A human must review and endorse. ASI guidance informs the design but is not binding.
- **D5 Fiction.** Nonfiction only; fiction appears only as scholarly or annotated editions.

## Spec review record (2026-10-29)

Fleet `/spec-review`, seven lenses, verdict NEEDS-REWORK (1 P1, 9 P2). All fixes applied in this revision. The P1 (author acceptance could not be enforced, and the spec wrongly claimed reconstruction's gate) is resolved by keeping one state file, binding each acceptance to a content hash so any later change re-opens it, and stating the human-decision limit honestly. Recording decisions in the approval-gated reconstruction ledger was considered and not taken: its event vocabulary is built for claim graphs, and its `actor` field carries the same limit, so it would add machinery without adding proof. Cut as ceremony: trace records as stored output, the passing-mention override marker, the `renamed` status, configurable thresholds, the re-locate diff, and the extra evaluation metrics.
