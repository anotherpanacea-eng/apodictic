# Voice-Aware Copyedit: a copyeditor that knows what to leave alone

*Reference module for the APODICTIC Core Editor. Increment 1: a style sheet, a voice ledger, and a
pass that raises **queries only**. The tool never edits the manuscript and, in this increment, writes
no replacement text at all. Spec: `docs/voice-aware-copyediting.md`. Validator:
`python scripts/validate.py copyedit <run_folder>`. Harvest: `python scripts/copyedit.py harvest
<snapshot>`. Worked example: `example-copyedit/`.*

---

## The design center

Inconsistency is the signal; deviation is not. A form the book uses one way throughout may be voice.
A form the book uses two ways is worth a question. The pass asks; the author decides; the decision
goes on the style sheet or the voice ledger and is not asked again.

## The standing never-flag list

These are superstitions no competent copyeditor enforces on a voice. Raise none of them, in any
register, at any level:

1. A sentence that opens with a conjunction (*And*, *But*, *Or*, *So*).
2. A split infinitive.
3. A sentence that ends in a preposition.
4. Singular *they*.
5. A sentence fragment.
6. Contractions, including in serious prose.

The validator's W1 catches an item whose `reason` invokes one of these, best-effort. This list, in
the pass prompt, is the real guard.

## Register profile

The register sets which mechanical conventions apply. It comes from intake (form and genre) plus one
author setting:

- **Style authority.** Book-length work: Chicago-style conventions. Op-eds and journalism: AP-style
  conventions. Academic forms: the discipline's style when named. State each convention in your own
  words; quote no style manual.
- **Register tolerance.** Literary fiction, genre fiction, memoir, op-ed, academic argument and
  testimony each relax some conventions by default. For example, a comma splice in literary
  narration is a query only when the book handles splices inconsistently. Serial-comma consistency
  is checked everywhere.

## Phase 0: snapshot

Reuse the annotated-manuscript snapshot, `[Project]_Manuscript_Snapshot_[runlabel].md`. Paragraphs
are blank-line-separated blocks numbered from 1 (headings count); a `# ` heading starts a chapter.
Offsets are UTF-8 byte offsets over the raw snapshot, including any BOM and CRLF bytes.
Blank lines may contain spaces or tabs. Never change the snapshot.

## Phase 1: style sheet and ledger harvest (one review)

1. Run `python scripts/copyedit.py harvest [Project]_Manuscript_Snapshot_[runlabel].md`. It lists
   competing forms with counts and paragraphs: compounds (*email* / *e-mail*, *alright* / *all
   right*), mid-sentence capitalization (*god* / *God*), *-ise* / *-ize* and *-our* / *-or* pairs.
   It proposes nothing.
2. Read the manuscript for what the harvest cannot see: dialect spelling, unmarked dialogue,
   deliberate fragments, house spellings, names (from the Continuity Bible when one exists).
3. Give the author one **style-sheet review**: each competing-forms item with its counts and two or
   three examples in context, and each proposed ledger entry with its evidence. Ask; do not choose.
4. Write `[Project]_Style_Sheet.md` in the project root: the author's style decisions in prose, and
   one `<!-- apodictic:voice_ledger {...} -->` block per ledger entry
   (`apodictic.voice_ledger.v1`): `id` (`VL-01`…), `form` (a literal string), `scope`, `origin`,
   `evidence`, `run`, optional `note`.
   - `origin: author` for what the author confirmed or stetted; `inferred` for what you propose and
     the author has not confirmed.
   - `scope` is `book`, `chapter:<n>`, `paragraphs:<a>-<b>`, `instance:<item id>` (enforceable: the
     validator binds an author entry inside it), or `speaker:<name>` / `zone:<zone>` (declared: the
     validator can only require the label). When the author declares a speaker or zone scope, the
     first note it labels asks whether to narrow it to a chapter or paragraph range.

The ledger persists across runs, so a stet holds for the next draft.

## Phase 2: the pass (queries only)

One paragraph at a time, with the neighbouring paragraphs as read-only context. Read the style
sheet, the ledger, the register profile and the paragraph's zone (dialogue and quotation only where
quotation marks or block quotes mark them; verse inside a verse block; anything else only if the
author declared it).

Precedence is fixed:

1. **Settled is settled.** A form under an `author` entry in an enforceable scope that covers the
   paragraph is never raised. The author answered.
2. **Possible voice is labelled.** A note touching an `inferred` entry or a declared entry names it
   in `ledger_refs` (or, for a zone entry, carries that zone in `zone`), and the reason says it may
   be voice.
3. **Unknown departures are `voice_check` queries.** When something looks like an error but may be
   voice, ask.

Write each query as an `apodictic.copyedit_item.v1` block in
`[Project]_Copyedit_Queries_[runlabel].md`, with a heading per item and the question in prose below
the block:

- `id` `P<paragraph>.<n>`, where the paragraph is that of the first instance; numbering is fixed
  once.
- `instances`: every span the query covers, each `{start_byte, end_byte, original}` with `original`
  copied exactly from the snapshot and inside one paragraph. At least one, so the author sees a real
  example.
- `kind`: `spelling`, `consistency`, `punctuation_mechanics`, `word_confusion`, `style_sheet`,
  `clarity`, `stepped_on_move`, `agreement`, `usage`, `fact_consistency` or `voice_check`.
- `disposition: query`. No `replacement`, or `replacement: null`.
- `level`: 1 (name the class, one example) or 2 (ask how to handle it, with counts).
- `zone`: `narration`, `dialogue`, `quotation`, `verse` or `declared`.
- `ledger_refs`, `style_ref` (a style-sheet decision, or null) and `reason` (the question).

## Gate before finalizing

`python scripts/validate.py copyedit <run_folder>` (add `--strict` for CI). It resolves the queries
file, its snapshot by run label, and the style sheet in the folder or its parent.

- **E1** schema, unique ids, the id names its first instance's paragraph, no replacement text.
- **E2** every instance's `original` is the snapshot's bytes at its offsets, on code-point
  boundaries, inside one paragraph.
- **E3** no item re-raises a form the author settled in an enforceable scope; an item touching an
  inferred or declared entry carries the label. Markdown block quotes require `quotation`; paired
  double or curly double quotes within a line require `dialogue` or `quotation`. Other zones,
  including verse and unmarked dialogue, rely on the pass or declared ledger entries.
- **W1** best-effort never-flag reasons (ERROR under `--strict`).

## Phase 3: author review

The author answers each query. A stet becomes an `author` ledger entry with the scope the author
gives (this instance, this chapter, this speaker, the whole book). A chosen form becomes a style-sheet
decision. Suggestions, rewrites and export arrive in later increments (spec §Increment plan).

## State and output locations

Per `output-structure.md` §Folder Architecture: the snapshot, style sheet and queries file live in
the project root; archive the run's files into `runs/YYYY-MM-DD_{model}_{type}/` on completion.
Never write to the plugin repo.
