# Manuscript Index Builder: a back-of-book index the author only has to approve

**Status:** **Proposed spec, 2026-10-29. Unbuilt.** Owner design calls resolved 2026-10-29 (§Resolved design calls). Codex review and three rounds of the fleet `/spec-review` panel applied 2026-10-29; round 3 verdict BUILD-READY-WITH-FIXES, with its fixes folded in (§Spec review record). Awaits owner admission; no build until then. Roadmap: `ROADMAP.md` → [Horizon Capacities](../ROADMAP.md#horizon-capacities) Tier 2, item 20. Proposed implementation surface: `plugins/apodictic/scripts/book_index.py`, `validate.sh book-index`, a `core-editor/references/manuscript-indexing.md` module and a `/book-index` command.
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
| Locators that fail a copyeditor's page test | Page numbers are never written by a model. They are looked up mechanically from the proof PDF by quoted anchor text (Phase B), and an anchor that cannot be found is reported, never guessed, and anchors that land out of manuscript order are held back (the Phase B order check) |
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
| Redoing locators after late corrections | Tool re-snapshots the corrected text, lists the anchors whose quotes broke, and reruns the locator step; only headings whose quotes the author updates need re-accepting |

The author's remaining work is one review session over the heading list, plus a final read of the finished index.

## Firewall fit

An index is paratext about what the manuscript discusses. The tool **never changes the manuscript** and never invents passages: every heading either has anchors the validator proves exist in the manuscript (I2) or only redirects to a heading that does (a See-only heading). Headings are proposals, and only headings with a recorded author acceptance that still matches their content reach the output (I4).

**Scope.** Indexing is a production task, admitted by the owner on 2026-10-29. It lives as a core-editor reference module because it reuses core-editor's manuscript-snapshot convention and quote-anchor rule; it is not an audit and emits no findings. Copyediting is out of scope here (ROADMAP §Not Planned records the owner's reopening of it as a separate spec).

## How it works: topic map first, locators optional

### Phase A: the topic map (manuscript stage)

**Snapshot.** The author supplies the text to index, ideally the final post-copyedit text. `/book-index map` writes a fresh `[Project]_Manuscript_Snapshot_[runlabel].md` from it (LF-normalized, trailing newline, the annotated-manuscript convention) in its own run folder under its own runlabel. It never reuses or overwrites a developmental-edit snapshot, so the map is never anchored to stale pre-copyedit text. The Index_Map sits in the same run folder and its header records `snapshot_path`, relative to the map.

**Seeds.** Phase A works with no inputs beyond the snapshot. When the project's `Argument_State.md` carries an `argument_spine.v1` block, its `key_terms` (the text before ` = `, or the whole term when there is none) and its `subclaims` (with the `Cn:` prefix stripped) are offered as discovery candidates only; their wording and loci never become anchors. A missing block or field is a no-op.

Output: `[Project]_Index_Map_[runlabel].md`: a header block, then one `apodictic.index_heading.v1` block per heading.

```markdown
<!-- apodictic:index_map
{"schema": "apodictic.index_map.v1", "snapshot_path": "Book_Manuscript_Snapshot_ix1.md", "chapter_level": 1}
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

**`index_map.v1` header.** Exactly one per map: `schema`, `snapshot_path` (relative to the map), and `chapter_level` (integer 1 to 6, default 1; read by W1 and the `paragraph` scheme).

**`index_heading.v1` fields.** Required unless marked optional. I1 checks every row.

| Field | Type | Rule |
|---|---|---|
| `schema` | string | `apodictic.index_heading.v1` |
| `id` | string | `^IX-\d{3,}$`, unique in the map |
| `heading` | string | non-empty; the preferred form as printed |
| `kind` | enum | `name` / `place` / `work` / `concept` / `term` |
| `variants` | string[] | may be empty; alternate forms folded into this heading |
| `status` | enum | `proposed` / `accepted` / `dropped` |
| `accepted_hash` | string | required when `status` is `accepted`, absent otherwise (see I4) |
| `weight` | number | in [0, 1]; orders the review list, never printed |
| `anchors` | anchor[] | the heading's own anchors, excluding any assigned to a subheading. Empty only for a See-only heading |
| `subheadings` | subheading[] | may be empty; one level deep |
| `see` | string[] | heading ids |
| `see_also` | string[] | heading ids |

An **anchor** is `{id, quote, role, end_quote}` with optional `context`. `id` is `<heading id>.a<N>` or `<subheading id>.a<N>`. `quote` is a single-line verbatim string; `role` ∈ `substantive` / `passing`; `end_quote` is a single-line verbatim string or null and closes an extended discussion that becomes a range. `context` (optional) is `{"before": str, "after": str}`, used only when `quote` cannot be made unique on its own; the matched text is `before + quote + after`.

A **subheading** is `{id, label, anchors}`. `id` is `<heading id>.s<N>`; `label` is non-empty; `anchors` follows the anchor rules and must hold at least one substantive anchor.

A **See-only heading** has `anchors: []`, no subheadings, a non-empty `see` and an empty `see_also`. A non-empty `see` is allowed only on a See-only heading. Every other non-dropped heading has at least one substantive anchor of its own or in a subheading.

Both schemas are registered with `closed_keys: true`, so an unknown key fails I1 before it can enter the hash. The shared schema engine checks top-level fields only; `book_index.py` checks the nested rules by hand: anchor and subheading id patterns and their agreement with the parent id, the `role` enum, single-line strings (including `context.before` and `context.after`), nullable `end_quote`, the `context` shape, `accepted_hash` presence, the See-only shape and the substantive-anchor minimums.

**Carrier safety.** The writer JSON-escapes `<` and `>` (as `\u003c` and `\u003e`) in `quote`, `end_quote` and `context`, so a quote containing `-->` cannot break the HTML-comment block. I2 compares the decoded strings.

**Author decisions.** The Index_Map is the only state. The run renders a read-only **review list** from it: headings grouped by kind and sorted by weight, each with its variants, chapter spread and every anchor shown in context from the snapshot. The author accepts, renames (edits `heading`), merges or drops; the command writes those decisions into the map only from the author's explicit replies. Acceptance is recorded per heading id the author names, or per review group the author was shown; bulk actions may only drop.

- **Accepting** sets `accepted_hash` = sha256 of `json.dumps(projection, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")`, where `projection` is the whole heading object minus `status`, `accepted_hash` and `weight`. It therefore covers the heading text, kind, variants, See/See also, every anchor's id, quote, end quote, role and context in array order, and every subheading's id, label and anchors in array order. Any later change to printed text, roles, anchors or their grouping breaks the hash.
- **Merging** is an action, not a stored state, and its result must pass I1 to I3. The source's anchors and subheadings move under the target and are renumbered from the target's highest index plus one; the source's heading text joins the target's variants, skipping duplicates; the two `see` and `see_also` lists are unioned with self-references and duplicates removed; references to the source anywhere in the map are repointed to the target; the source is set to `dropped`. The target and every heading whose references were rewritten return to `proposed` and are listed for review, so none drops out of the output silently.
- A heading never decided stays `proposed` and is never published, so silence publishes nothing.

**Re-snapshotting.** When the text changes (copyedits, late corrections), the author supplies the new text and `/book-index map --resnapshot` writes a new snapshot under a new runlabel in the same folder and points `snapshot_path` at it. The old snapshot stays on disk. Each anchor is classified against the old and new snapshots with the quote branch of `reanchor.py` (held, moved, vanished, ambiguous), factored into a shared helper. Any heading with an anchor that is not held, or whose enclosing paragraph text differs between the two snapshots, returns to `proposed` and is listed for review, separately from the broken quotes. This closes the case where a copyedit rewrites or cuts the passage around a quote that survives verbatim: the author judged the old passage, not the new one. Updating a broken quote also changes the heading's hash. Unaffected headings keep their acceptance.

### Phase B: locators (optional, pluggable)

The core deliverable is the topic map: headings, subheadings and See/See also, each tied to real passages. It can be output with no locators at all, as a topic guide or as a head start for a professional indexer. When locators are wanted, `/book-index locate` takes the accepted headings (only those passing I4), the author picks a **locator scheme**, and every anchor resolves from its quote to a locator or goes to the unresolved list with a reason. No scheme ever estimates, and passing anchors produce no locators. A See or See also whose target is not in the published set is dropped from the output and listed beside the unresolved anchors.

`book_index.py locate` and `book_index.py format` are the only writers of the finished index. The command text forbids the model from writing or editing locator text or the formatted index.

| Scheme | Locator | Source |
|---|---|---|
| `paragraph` | chapter and paragraph | the snapshot (see §Chapters) |
| `page` | printed page (folio) | the typeset proof PDF (procedure below) |
| `line` | line number | a line-numbered edition or text |
| `ebook` | ebook location | the EPUB, or a location table the author exports |
| `embedded` | none; tags are written instead | Word XE fields or LaTeX `\index` commands, and the typesetter generates the numbers |

Kindle locations are computed by Amazon from the published file, so the `ebook` scheme reads them from an author-supplied export rather than calculating them.

**Chapters.** A private helper in `book_index.py` defines them for this module, using `annotation_manifest.atx_headings` for the heading scan and deliberately not `apodictic_artifacts.chapter_token`: every ATX heading at the header's `chapter_level` starts a chapter, labeled by its heading text. Text before the first such heading is front matter and is excluded. A paragraph is a blank-line-separated block after a chapter heading, headings excluded. With no chapter headings, the `paragraph` scheme refuses with that reason and W1 is skipped with a note.

**Match normalization (Phase B only).** Locating compares a folded form of both sides: inline markdown and footnote markers stripped, and dashes, quote styles, ligatures, line-break hyphenation and whitespace folded, so a quote containing `*Title*` or `[^12]` still finds its printed text. I2 is unaffected; it always checks the raw quote against the raw snapshot.

**The `page` scheme.** Input: the accepted map plus the typeset proof PDF.

1. Extract page text and build the page-label map: the PDF's own page labels when present, otherwise an author-supplied map (for example "PDF page 15 is folio 1; front matter is roman"). With neither, the scheme stops and asks; it never guesses folios. A proof with no extractable text (a scanned image) is refused with that reason.
2. Search only the body page range by default. Front matter and back-matter notes are excluded unless the author includes them, because an epigraph or a preface can repeat a body sentence. Running heads and folios are stripped deterministically: the first and last line of each body page are dropped when, with digits masked, they repeat on at least five pages. A quote that still fails to match across a page break goes to the unresolved list.
3. For each anchor, find its `quote` (with `context` when present) in the folded proof text, searching across page breaks. The match must be unique. A quote that spans a page break takes the page where it starts.
4. Assign the folio. An `end_quote` is searched only after its quote; found, it yields a range; one found earlier than its start, or not found, sends the anchor to the unresolved list.
5. **Order check.** Sort every placed anchor in the book by its snapshot offset and take the longest subsequence whose proof positions are non-decreasing. Among equally long subsequences, keep the one that is lexicographically smallest by anchor id, comparing ids numerically by component (`IX-9.a2` before `IX-10.a1`). Anchors outside that subsequence matched the wrong place, typically a copyedited sentence whose old wording survives elsewhere, and go to the unresolved list with reason `out_of_order`.
6. Format the index under a style profile (indented or run-in, letter-by-letter or word-by-word, range style, See/See also placement) and write it out, with the unresolved list and its match positions alongside.

Because anchors are quotes, repagination or a new edition costs one rerun of Phase B under any scheme.

Locate behavior (only I4-passing headings formatted, every anchor placed or unresolved, the order check, range direction, duplicate locators merged under one heading) is covered by ordinary unit tests, including one early wrong match that step 5 must reject, a swapped pair of equal-length candidates, and a quote that crosses a page break with a running head between its halves.

## The `book-index` validator

`validate.py book-index <run_folder|index_map.md> [--strict]`, following the `world-bible` convention: it finds the snapshot through `snapshot_path`; a missing snapshot is an ERROR. W checks are advisory and ERROR under `--strict`; there are no override markers. Exit 0 clean or WARN-only, 1 ERROR, 2 usage.

Status scope: I1 covers every heading; I2, I3 and W1 to W3 skip `dropped` headings. A freshly proposed map, with See links between proposed headings, validates clean.

- **I1 schema.** Every field rule above, including the header, the See-only and substantive-anchor rules, the nested rules and the id patterns.
- **I2 provenance.** Every `quote` and `end_quote` (with `context` when present) occurs in the raw snapshot exactly once, by the non-overlapping count `annotation_manifest.quote_anchor` and A6 already use, and a non-null `end_quote` occurs exactly once after the end of its `quote`.
- **I3 cross-references.** Every See and See also target exists and is not dropped. No See or See also targets a See-only heading, and the See graph has no cycle. Reciprocal See also links are normal index practice and are allowed.
- **I4 acceptance.** Every `accepted` heading's `accepted_hash` equals the hash of its current projection. A heading changed after acceptance is an ERROR until re-accepted.
- **W1 coverage.** A chapter (§Chapters) with no substantive anchors, located by each anchor's I2 offset, is flagged as possible under-indexing.
- **W2 locator strings.** A heading or subheading with more than six substantive anchors of its own.
- **W3 subheadings.** A lone subheading, a subheading whose anchors match the same snapshot spans as its parent's or a sibling's, or more than twelve subheadings under one heading.

**Honest limit.** I2 proves an anchor is a real passage of this snapshot, not that the passage is about its heading; a real passage filed under a mistaken topic is the residual firewall risk, and the review list shows every anchor in context so the author judges it. I4 proves every accepted heading is unchanged since its acceptance was recorded. It does not prove a human made the decision: recording happens only from the author's explicit replies, a process rule the validator cannot verify. Approval-gated reconstruction has the same limit (its `actor` field is also written by the tool). The substantive/passing call, the choice of heading words, and the `weight` ranking behind the cut candidates are judgment the validator does not check. The finished index is protected by process: the scripts are its only writers, and the command forbids model edits to it.

**Self-tests.** Increment 1 negatives: a quote that occurs twice, a missing quote, a missing snapshot, an `end_quote` before its `quote`, a circular See, a See to a dropped heading, a See also to a See-only heading, a role flip inside a subheading after acceptance, a malformed nested anchor id, a lone subheading (W3), a See-only heading with `see_also`, and a quote containing `-->` that must round-trip. Positives: a fresh proposed map with See links between proposed headings validates clean, and a merge result passes I1 to I3. The canonical worked example is a directory fixture under `core-editor/references/` (map plus snapshot) that must pass `validate.py book-index <dir> --strict` with exit 0. It includes accepted, dropped and See-only headings, a heading with two subheadings, a substantive anchor in every chapter, and a titled (word-numbered) chapter. Increment 2's locate unit tests are listed above.

## Evaluation before release

Run on at least one public-domain or permissioned book that already has a professional index. Report one overall heading-recall figure, adjudicated by hand against that index, and for the `page` scheme a spot-check of 50 randomly sampled locators against the printed pages. These are reported in the module doc, not used as gates, and the docs do not claim parity with professional indexes.

## Positioning

A human must review and endorse the index before it is used. Nothing reaches the output without a recorded acceptance that still matches the heading's content (I4); recording happens only from the author's explicit replies, a process rule the validator cannot verify. The module doc and `/book-index` command text say exactly this. The ASI evaluations above are prior-art evidence that shaped the design. APODICTIC is not bound by ASI guidance, and the docs do not present it as a rule. They do say which of the documented failure modes this design checks mechanically and which still rest on the author's review. An author who wants a professional indexer can hand over the Cindex/SKY export.

## Where it lives

A core-editor reference module (`core-editor/references/manuscript-indexing.md`), invoked by a `/book-index` command with `map` and `locate` modes, routed like `/legal-risk` and `/world-bible`. The command is named `/book-index` because `/apodictic` is already the capability index. Nonfiction only: argument-shaped and narrative nonfiction are where indexes are expected. Fiction gets an index only in scholarly or annotated editions, which are handled as nonfiction apparatus.

## Dependencies

Phase A, the validator and the `paragraph` scheme are stdlib-only. The `page` scheme needs PDF text extraction: an optional `pypdf` import, loaded lazily, with the scheme refusing cleanly (and saying how to install it) when the package is missing, and tests that `skipif` without it. A model reading the PDF is rejected for locators because it is not deterministic.

## Increment plan

1. **Topic map.** `index_map.v1` and `index_heading.v1`; the module and the review list; snapshot writing and `--resnapshot`; `book_index.py` with I1–I4 and W1–W3; the Increment 1 negative self-tests; the canonical worked example and its snapshot in `--check-all`; the `/book-index map` command. Registration points: the two schema files and their schema id strings in `book_index.py`; two `schemas/_coverage.json` rows (one per schema, `validators: ["book-index"]`, `closed_keys: true`, the canonical gate); the `validate.py` ROUTES entry; the `validate.sh` `AGG_VALIDATORS` entry; a `validate_canonical.py` run_validator call on the directory fixture; the `schemas/validator-runtime-inventory.json` entry; and the fixture paths.
2. **Locators and output.** `/book-index locate` with the scheme contract, the `paragraph` and `page` schemes, match normalization, the order check, style profiles, the locate unit tests, length-allowance cut candidates (lowest-weight headings listed for the author to drop), a locator-free topic-map output, and plain-text and DOCX output. For DOCX, extract `annotation_export.py`'s deterministic-zip and OOXML helpers into a shared function first, as a preparatory change that leaves annotation_export's self-tests and canonical gates byte-identical.
3. **More schemes and exports.** The `line`, `ebook` and `embedded` schemes, and a tab-delimited export for Cindex and SKY import.

## Resolved design calls (owner, 2026-10-29)

- **D1 Scope.** Indexing is admitted as a production module.
- **D2 Locators.** Optional and pluggable. Topics and references are the core; pages, ebook locations, line numbers and the rest are schemes (§Phase B).
- **D3 PDF dependency.** Optional `pypdf`, for the `page` scheme only.
- **D4 Positioning.** A human must review and endorse. ASI guidance informs the design but is not binding.
- **D5 Fiction.** Nonfiction only; fiction appears only as scholarly or annotated editions.

## Spec review record (2026-10-29)

Fleet `/spec-review`, seven lenses, two rounds, all fixes applied.

- **Round 1: NEEDS-REWORK (1 P1, 9 P2).** The P1 was that author acceptance could not be enforced and the spec wrongly claimed reconstruction's gate. Fixed with one state file, a content-hash binding that re-opens any changed heading, and an honest statement of the human-decision limit. Recording decisions in the reconstruction ledger was considered and not taken: its event vocabulary is built for claim graphs and its `actor` field carries the same limit. Cut as ceremony: stored trace records, the passing-mention override marker, the `renamed` status, configurable thresholds, the re-locate diff and extra evaluation metrics.
- **Round 2: NEEDS-REWORK (3 P1, 10 P2).** P1s: the acceptance hash left out printed and locator-changing fields and had no canonical serialization (now the whole heading minus status, hash and weight, with a fixed JSON serialization); the validator's output gates had no way to receive their inputs (cut; locate behavior is unit-tested instead); the copyedit path had no re-snapshot step (added). Also fixed: snapshot ownership, merge as an action instead of a stored state, accepted-only cross-reference targets, a defined chapter helper, a longest-subsequence order check, match normalization on both sides in Phase B, the CLI and registration contract, the Continuity Bible seed dropped (fiction-shaped), and the snapshot hash cut (the exactly-once check is the provenance rule).
- **Round 3: BUILD-READY-WITH-FIXES (0 P1, 10 P2).** Folded in: per-gate status scope so a fresh proposed map validates; the See-cycle rule narrowed to See (reciprocal See also allowed); merge written as a complete transform; re-snapshot reopens headings whose surrounding passage changed, reusing `reanchor.py`'s quote classification; closed-key schema registration with the nested rules named; the scripts as sole writers of the finished index; a strict directory canonical gate and the missing registration points; HTML-comment carrier escaping; a deterministic running-head strip; W2/W3 aligned with the prior-art table; deterministic tie-breaks; per-heading acceptance, with bulk actions limited to drops.
