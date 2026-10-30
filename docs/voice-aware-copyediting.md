# Voice-Aware Copyedit: a copyeditor that knows what to leave alone

**Status:** **Increment 1 built (fleet card AP-CE), 2026-10-30: style sheet, voice ledger, queries only.** Increments 2 and 3 unbuilt. Owner ruled on replacement text 2026-10-29 (D2) and accepted the D1 and D3–D5 recommendations on 2026-10-30 (§Design calls). Fleet spec review 2026-10-30 (apodictic #407) found one P1, fixed here (§The voice ledger, enforceable scopes). Roadmap: Horizon Capacities Tier 2. Proposed implementation surface: `plugins/apodictic/scripts/copyedit.py`, `validate.sh copyedit`, a `core-editor/references/voice-aware-copyediting.md` module and a `/copyedit` command.
<!-- built-when: plugins/apodictic/scripts/copyedit.py -->

## Why

The owner reopened copyediting on 2026-10-29 with one caution: copyediting is more than fixing spelling, and a good copyeditor leaves alone a great deal that looks like error when it is the voice and register of the book. Dialect spelling in a character's speech, fragments used for rhythm, a sentence that opens with "And", a narrator who never uses quotation marks, an essayist's run-on that is doing argumentative work: a rule-driven checker "fixes" all of these, and the book comes back flattened.

Copyeditors manage this with three tools, and this spec builds all three:

- **The style sheet.** A running record of every decision about spelling, hyphenation, capitalization, numbers and names, so the same choice is made the same way through the book. Its most important entries are often the departures: "Jim's dialect spellings are deliberate; do not regularize."
- **The query.** When a copyeditor cannot tell whether something is error or intention, they ask the author instead of changing it.
- **The suggested rewrite, used sparingly.** A good copyeditor will also offer a rewrite when a sentence is unclear, or when the author is stepping on their own move: explaining the joke, glossing an image the reader already has, hedging a claim the paragraph has earned, or adding a line after the one that should have ended the scene. The rewrite is offered, never imposed.
- **Stet.** The author's answer that the original stands. Once given, it holds for every later instance.

The design center is **inconsistency is the signal, deviation is not.** A nonstandard form used the same way forty times is probably a choice. A form that appears both ways is the classic copyedit target, and the useful question is which form the book uses.

## Terms

The tool never edits the manuscript. Everything it produces is one of two things, and the author acts on both:

- **Suggestion.** A proposed change with the replacement text written out (`suggest` for a mechanical fix, `rewrite` for a one-sentence rewrite). It changes nothing until the author accepts it. Accepting is the author's act; the tool only shows what accepting would do.
- **Query.** A question to the author with no replacement text, for cases where the right answer depends on the author's intent ("Deliberate? *alright* here, *all right* in chapter 2").
- **Stet.** The author's answer that the original stands. It goes on the voice ledger so the question is not asked again.

## Intervention levels

The author chooses how far the copyedit goes, for the whole run or per kind. Every level shows at least one real instance from the manuscript, because seeing an example is what makes a note usable. The levels, with one running example (a manuscript that writes *alright* 37 times and *all right* 4 times, all 4 in chapter 9):

1. **Name the class.** "Consider: *alright* and *all right* are both used. Example: ch. 9, ¶14, 'It was all right by him.' (4 instances, all in ch. 9.)" One note per class, no replacement text.
2. **Ask how to handle it.** "*all right* appears 4 times against 37 *alright*. Make them all *alright*, keep ch. 9 as is (a different narrator?), or something else? Example: ch. 9, ¶14." One query per class; the answer goes on the style sheet or the voice ledger.
3. **One suggested fix.** The level-2 question plus one worked suggestion on the first instance: ch. 9, ¶14 'all right' → 'alright', with the other three instances listed. Accepting it settles the style-sheet choice, and the remaining instances follow at level 4 if the author wants them.
4. **Suggest fixes for all.** One suggestion per instance (four here), each with its own span. This is the only level where opt-in bulk acceptance applies.

A rewrite kind uses the same ladder. For a stepped-on move: (1) "Consider: some scene endings explain the image they end on. Example: ch. 4, last paragraph." (2) "Ch. 4 ends on 'He shut the door,' then explains it. Keep the explanation, cut it, or move it?" (3) A suggested rewrite that ends the paragraph at "He shut the door." (4) The same for every such ending the pass found.

Defaults: level 3 for mechanical kinds, level 2 for rewrite kinds, and query-only kinds stop at level 2 whatever the setting. Levels 1 and 2 produce queries, so they are available in Increment 1. In the record, a level-1 or level-2 item carries `instances` (the spans it covers, with at least one) in place of a single `span`.

## Fleet prior art: consume or extend

The coordinator asked first whether to consume or extend two existing pieces. Both are close; neither is a drop-in.

| Existing surface | What it is | Relationship |
|---|---|---|
| **voicewright Spec 113, source-first period copyeditor** (`setec-voicewright/specs/113-source-first-period-copyeditor.md`, built 113.1) | One call per source paragraph returns numbered, span-anchored suggestions against the untouched source; the author picks; deterministic checks withhold malformed or out-of-bounds suggestions; a separate seat audits fidelity | **Port the contract and leave the code.** Its suggestion record (§3), deterministic checks (§4), alternatives-never-stack rule and combined-selection check are exactly right and are reused here with attribution. Its brief is periodization toward a Victorian register, its kinds are period kinds, and its runner is a private research harness (authorization records, reader panels, Tinker cost caps, run stores outside git). APODICTIC does not pin voicewright, and adding a pin for a record shape is not worth a new cross-repo contract. |
| **SETEC idiolect detector** (consumed today via `prose-measurements/scripts/ai_prose_idiolect_detector.py`, Idiolect Preservation audit) | Keyness against a reference corpus; writes a "do not normalize" preservation list; that audit already names "before a heavy copyedit pass" as a trigger | **Consume as is.** Its preservation list seeds the voice ledger (below). No SETEC change. |
| **SETEC productive roughness audit** (`productive_roughness_audit.py`) | Baseline-relative rates of fragments, sentence-initial conjunctions, contractions, asides, very short sentences; refuses without a writer baseline | **Consume, optional.** Seeds ledger rules ("fragments are this writer's normal") and drives the post-pick flattening check. It is not shimmed in APODICTIC yet; the build adds a shim like the idiolect one. |
| **SETEC punctuation cadence audit** (`ai_prose_punctuation_cadence.py`) | Dash, semicolon, parenthetical and sentence-final distributions; written to catch "smoothing that happened in the line edit" | **Consume, optional.** Post-pick flattening check. |
| **SETEC POV voice profile** | Per-POV voiceprints | **Consume, optional.** Marks close-POV narration as a voice zone in multi-POV fiction. |
| **APODICTIC Continuity Bible** | The narrative half of a style sheet: names, ages, timeline facts | **Consume.** Names and aliases enter the style sheet without re-extraction; contradictions become queries. |
| **APODICTIC Annotated Manuscript** | Immutable manuscript snapshot, quote anchors, CriticMarkup and Obsidian rendering, a no-mutation proof | **Reuse.** Same snapshot and the same rendering path for queries. |

**Recommendation (D1):** extend by porting. APODICTIC owns the author-facing copyedit; it reuses Spec 113's record contract and checks as a written spec dependency, and it consumes the SETEC voice surfaces through its existing pinned SETEC contract. If the two copyeditors later stabilize on one record, extracting a shared schema can come later as a follow-up for both repos.

## Firewall fit

APODICTIC's Firewall says diagnostics identify problems and never rewrite manuscripts, and the annotated-manuscript spec rules out tracked changes. Copyediting needs some replacement text: "recieve" has one right answer, and making the author type it is the kind of busywork the tool exists to remove. The owner ruled on 2026-10-29 (D2) that all three levels are acceptable: queries, small mechanical fixes, and sentence-level rewrites for clarity or where the author is stepping on a move. The line is drawn like this:

- **The snapshot is never changed.** All work is against the frozen snapshot, and the validator proves it (E8).
- **Two sizes of replacement.** Mechanical kinds get typo-scale fixes inside a size cap (E5). The two rewrite kinds, `clarity` and `stepped_on_move`, may offer a rewrite of up to one sentence, always paired with the question that explains it. Everything else (usage, agreement in voiced speech, fact consistency, possible voice) is a **query** with no replacement text.
- **Rewrites keep the voice.** A rewrite may not alter any author-declared ledger form, a rewrite touching inferred voice evidence or a zone is labelled as possible voice (E3), and the flattening check covers accepted rewrites (W2).
- **Nothing is applied without the author's pick.** Review is one suggestion at a time by default. Bulk acceptance ("accept every spelling suggestion", or everything in a chapter, rewrites included) is an option the author turns on, and an author who accepts wholesale does so on their own responsibility. Silence never applies anything.
- **Picks export to a copy** (CriticMarkup first, DOCX tracked changes later), the way Spec 113's export applies picks.

So the tool's own prose is bounded: typo-scale fixes, and at most one sentence where clarity or a stepped-on move calls for it, each chosen by the author. Those one-sentence rewrites are the owner's D2 exception; anything larger is line editing, which stays out of scope.

## The voice ledger

The heart of the design. The ledger is the "leave alone" half of the style sheet: a list of forms, patterns and zones the copyedit should treat as possible voice. Each entry carries its evidence, its source and an `origin` of `author` or `inferred`. Only `author` entries are binding; inferred entries and zones are editorial context that shapes how a note is framed (E3, D6):

| Source | Example entry | Strength |
|---|---|---|
| **Author-declared** (the intake questions, the style-sheet review, and every stet) | "No quotation marks anywhere; dialogue is unmarked." "Lowercase *god* throughout." "Jim's speech uses dialect spelling." | Binding within its stated scope (book, chapter, speaker or zone) |
| **Consistency harvest** (Phase 1) | `alright` occurs 37 times, `all right` never | Inferred; becomes binding when the author confirms it |
| **Idiolect preservation list** (SETEC, when a baseline exists) | the bigram `which is to say` | Inferred |
| **Baseline roughness** (SETEC, when a writer baseline exists) | fragment rate and sentence-initial And/But rate are inside the writer's normal band | Inferred pattern: fragments and initial conjunctions are framed as likely voice |
| **Zones** | dialogue; quoted and cited material (epigraphs, block quotes, sources); close-POV narration in multi-POV fiction; verse and lyrics | Inferred context: notes here carry a possible-voice label (E3). Found mechanically only where the text marks them: quotation-marked dialogue, Markdown block quotes, and lines inside a verse block. Unmarked dialogue and close-POV narration are zones only when the author declares them. |

Entries are stored as `apodictic.voice_ledger.v1` blocks in `[Project]_Style_Sheet.md`, next to the ordinary style decisions. The ledger persists across runs and revisions, so an author's stet holds for the next draft. Each entry has:

- `id`;
- `form`: a literal string, or a closed pattern name (for example `no_quotation_marks`, `lowercase:god`);
- `scope`: one of `book`, `chapter:<n>`, `paragraphs:<a>-<b>`, `instance:<item id>`, `speaker:<name>` or `zone:<zone>`;
- `origin`: `author` or `inferred`;
- `evidence`: the loci, and the counts for harvested entries;
- `run`: the run label that created it.

**Enforceable and declared scopes.** A validator can resolve `book`, chapter, paragraph-range and instance scopes from the snapshot alone, so an `author` entry with one of these scopes is **enforceable**, and E3 binds it. A validator cannot resolve `speaker` or `zone` scopes: it cannot attribute speech to a character, and it cannot find dialogue that has no quotation marks. An `author` entry with one of those scopes is **declared**. It is recorded, and E3 treats it the way it treats an inferred entry: it labels the notes it touches as possible voice and keeps them out of default bulk acceptance. The first note it labels asks the author whether to narrow it to a chapter or paragraph range, which makes it enforceable.

**Standing never-flag list.** Some "rules" are superstitions that no competent copyeditor enforces on a voice: a sentence opening with a conjunction, a split infinitive, a sentence ending in a preposition, singular *they*, a fragment, contractions in serious prose. The tool raises none of these in any register. They are in the module as a fixed list, so a model's training-data pedantry cannot reintroduce them.

## Register profile

The register sets which mechanical rules apply. It comes from APODICTIC's existing intake (form and genre) plus one setting the author can change:

- **Style authority.** Book-length work defaults to Chicago-style conventions; op-eds and journalism to AP-style conventions; academic forms to the discipline's style when named. The module states each rule it applies in its own words; no style manual's text is shipped.
- **Register tolerance.** Literary fiction, genre fiction, memoir, op-ed, academic argument and testimony each carry a short list of rules that are relaxed by default (for example, comma splices in literary narration become queries only when inconsistent; serial-comma consistency is enforced everywhere).

## How it works

### Phase 0: snapshot

Reuse the annotated-manuscript snapshot (`[Project]_Manuscript_Snapshot_[runlabel].md`, bound by sha256). Paragraphs split on blank lines; offsets are UTF-8 byte offsets over the snapshot, as in Spec 113 §1.

### Phase 1: style sheet and ledger harvest (one review)

The tool inventories the manuscript mechanically: spelling variants, hyphenation and compound forms, capitalization, number style, italics, abbreviations, names (from the Continuity Bible when present). For every item with competing forms it records each form's count and loci. It proposes ledger entries from consistent nonstandard forms and from the SETEC surfaces when a baseline is available.

The author gets a **style-sheet review**: each competing-forms item with its counts and a proposed choice, and each proposed ledger entry with two or three examples in context. The author picks forms and confirms or rejects ledger entries. A confirmed entry becomes `author` and binding. An unconfirmed entry stays `inferred`: it labels the notes it touches as possible voice and is shown again at the next run, but it does not stop the author from seeing a fix they asked for.

### Phase 2: the pass

One call per paragraph, with the neighbouring paragraphs as read-only context, as in Spec 113 §1. The call receives the style sheet, the ledger, the register profile and the paragraph's zones, and returns candidate items in the record below. Every candidate then goes through the deterministic checks (§Validator) before the author sees it. Precedence is fixed. First, a candidate covered by an author stet or author-declared entry within its scope is suppressed: the question was answered and is not asked again. Second, a candidate that touches an inferred entry or a zone keeps the author's chosen level but carries a possible-voice label naming the entry or zone, and it is left out of bulk acceptance unless the author opts in for labelled items too.

### Phase 3: author review and export

The author sees a numbered list (`P<paragraph>.<n>`, numbering fixed once as in Spec 113 §3), grouped by kind, with queries rendered as margin comments on the annotated-manuscript path. The author accepts, rejects, or answers each query. A query answer of "stet" adds an `author` ledger entry with the scope the author gives (this instance, this chapter, this speaker, the whole book), and Phase 2's first precedence rule keeps the question from coming back. Accepted picks export to a copy of the snapshot.

### The record: `apodictic.copyedit_item.v1`

```json
{"id": "P14.2",
 "span": {"start_byte": 212, "end_byte": 219},
 "original": "recieve",
 "replacement": "receive",
 "kind": "spelling",
 "disposition": "suggest",
 "zone": "narration",
 "ledger_refs": [],
 "style_ref": null,
 "reason": "misspelling; 'receive' appears 11 times elsewhere"}
```

- `kind` is closed: mechanical kinds `spelling`, `consistency`, `punctuation_mechanics`, `word_confusion`, `style_sheet`; rewrite kinds `clarity`, `stepped_on_move`; query-only kinds `agreement`, `usage`, `fact_consistency`, `voice_check`.
- `disposition` is `suggest` (a mechanical fix with a `replacement`), `rewrite` (a rewrite kind with a `replacement` of at most one sentence, and `reason` phrased as the question to the author) or `query` (`replacement` is null and `reason` is the question). There is no `apply`. A rewrite kind may also come as a plain `query` when the pass sees the problem but has no rewrite worth offering.
- `stepped_on_move` names the move in `reason` ("the scene's last line lands at 'shut the door'; the next sentence explains it"). Deleting the stepping sentence is a valid rewrite when the paragraph stays non-empty (E4).
- `consistency` and `style_sheet` items name the style-sheet decision in `style_ref`; their replacement must be the form that decision chose (E6).
- `voice_check` is how the pass says "this looks like an error, but it may be voice": it is always a query, and it is the kind a converted ledger or zone hit becomes.

## The `copyedit` validator

Mechanical checks, ERROR unless marked W. E1, E2, E4 and E7 follow Spec 113 §3 and §4.

- **E1 schema.** The closed record; unique ids; closed enums.
- **E2 provenance.** `original` equals the snapshot bytes at `span`; the span falls on code-point boundaries and inside one paragraph. A level-1 or level-2 item checks each entry of `instances` the same way, and each entry carries its own `original`.
- **E3 ledger and zone guard.** No item of any disposition may change a form covered by an enforceable `author` ledger entry within its scope, and no item may re-raise a question an author stet already answered in that scope. Any item touching an `inferred` entry, a declared `author` entry or a zone must carry the possible-voice label naming it. The label is the item's `ledger_refs` or `zone` field naming that entry or zone. A `rewrite` must keep every ledger form in its span unchanged unless the item is labelled. This is the check that enforces the author's own decisions mechanically; inferred voice evidence informs the author and never overrides the level they chose.
- **E4 shape.** A replacement differs from its original, contains no line break, and does not leave its paragraph empty.
- **E5 size cap.** A `suggest` item changes at most a few words (default: three word tokens, one sentence touched); a larger change must be a `rewrite` of a rewrite kind or a query. A `rewrite` touches at most one sentence, or two when it merges or splits them, and only the `clarity` and `stepped_on_move` kinds may use it (D2).
- **E6 style-sheet agreement.** A `consistency` or `style_sheet` suggestion's replacement equals the form in its `style_ref`. When the choice is confirmed, every suggestion must match it. When it is still proposed, only the single level-3 worked suggestion may use the proposed form; accepting it confirms the choice, and level-4 suggestions for the other instances appear only after that.
- **E7 combined selection.** The author's picks for a paragraph apply as a set only when no two overlap and the paragraph stays non-empty (Spec 113 §4). Bulk acceptance goes through the same check.
- **E8 no mutation.** The snapshot's sha256 still matches its binding, and the export is the snapshot plus exactly the picked replacements.
- **W1 never-flag list.** Best-effort: an item whose `reason` matches a keyword of a never-flag rule is withheld and counted. The real guard is the list in the pass prompt; W1 catches leaks without claiming completeness.
- **W2 flattening check** (when SETEC and a baseline are available). After picks are applied to the copy, punctuation cadence and productive roughness are rerun against the snapshot; a feature that moved beyond the writer's band is reported with the picks that moved it.

**Honest limit.** E3 binds only enforceable entries the author has declared. Inferred entries and zones label notes without blocking them, and a voice choice nothing has seen, used once, can still draw a plain suggestion. That gap is why unknown departures default to a `voice_check` query (D3), why labelled items stay out of default bulk acceptance, and why the evaluation measures voice false corrections directly.

## Evaluation before release

- **Hostile fixtures.** Public-domain passages chosen for voice: dialect-heavy dialogue (Twain's *Adventures of Huckleberry Finn*, which opens with an explanatory note that its dialects are deliberate), unmarked or idiosyncratic punctuation, a period essay with long periodic sentences; plus synthetic passages with deliberate fragments and comma splices. Errors are planted into each fixture: typos, inconsistent hyphenation, wrong-word confusions, unbalanced quotation marks.
- **Measures.** (a) **Voice false-correction rate:** suggestions that would change a voice item, reported separately for items under enforceable author entries (must be zero, by E3) and all others, including declared and inferred entries (the honest-limit number). (b) **Planted-error recall** by kind. (c) **Query precision:** share of queries a reader judges worth asking. (d) **Rewrite acceptance and voice cost:** share of rewrites a reader would take, and the W2 movement accepted rewrites cause. Fixtures include planted stepped-on moves (a gloss after a closing image, a hedge on an earned claim).
- **Baseline arm.** The same fixtures through a plain "copyedit this" prompt with no ledger or register profile, to show what the voice machinery buys. Report the numbers in the module doc and claim nothing beyond them.

## Where it lives

A core-editor workflow module (`core-editor/references/voice-aware-copyediting.md`) invoked by a `/copyedit` command with `style-sheet` and `pass` modes, routed like `/legal-risk` and `/world-bible`. The Idiolect Preservation audit's existing "before a heavy copyedit pass" trigger points here. Fiction and nonfiction both (D4). Stdlib-only for the core; the SETEC surfaces are optional and degrade cleanly, as they do in the prose-measurements audits.

## Increment plan

1. **Style sheet, ledger and queries only.** `voice_ledger.v1`, the Phase 1 harvest and review, the never-flag list, and a pass that emits only queries, recorded as `copyedit_item.v1` items with `disposition: query` and checked by E1–E3. No replacement text ships in this increment, so it stands inside today's Firewall on its own and is already useful: the consistency queries are most of a copyeditor's mechanical value.
2. **Suggestions and rewrites.** `suggest` and `rewrite` dispositions, E4–E8, W1, opt-in bulk acceptance, CriticMarkup export of picks, a canonical worked example in `--check-all`.
3. **Voice post-check and exports.** The productive-roughness shim, W2, DOCX tracked-changes export, and the fixture evaluation above.

## Design calls

D2 is answered. The rest are recommendations that stand unless the owner objects.

- **D1 Consume or extend.** *Recommend:* port Spec 113's suggestion contract and checks into APODICTIC (spec dependency, no code import or new pin); consume the SETEC idiolect, roughness, cadence and POV surfaces through the existing SETEC contract. *Alternatives:* pin voicewright and call the 113 runner (heavy private harness, period brief); or generalize 113 inside voicewright and have APODICTIC call it.
- **D2 Replacement text and the Firewall. Answered 2026-10-29.** The owner: all three levels are acceptable, and "a copy editor may suggest rewrites for clarity or when the author is stepping on a move." Follow-up the same day: "the fixes should be suggested, not made." So: queries; typo-scale mechanical fixes; and one-sentence rewrites for the `clarity` and `stepped_on_move` kinds. A third note: review is one at a time by default, and bulk acceptance is optional, at the author's own responsibility. A fourth: the author picks an intervention level, from naming a class of edits up to suggesting a fix for every instance, and every level shows an example (§Intervention levels). Every fix of any size is a suggestion the author accepts (§Terms); the tool applies nothing itself.
- **D3 Unknown departures.** A nonstandard form the ledger does not cover and that is used once. *Recommend:* a `voice_check` query. *Alternatives:* leave silently (misses real typos), or suggest a fix (the flattening the owner warned about).
- **D4 Scope.** *Recommend:* fiction and nonfiction both; unlike an index, every book is copyedited.
- **D5 Style authority.** *Recommend:* Chicago-style conventions for books and AP-style for short-form journalism by default, author-changeable, with the module stating every rule in its own words.
- **D6 Inferred voice evidence.** *Recommend:* only author-declared entries and stets are hard limits; inferred entries and zones (dialogue, quotations, close POV, verse) label notes as possible voice and keep them out of default bulk acceptance, but the author's chosen level still applies there. *Alternative:* treat zones as query-only regardless of level (safer for voice, but a plain typo in dialogue could then never get a suggested fix).
