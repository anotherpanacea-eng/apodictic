# Voice-Aware Copyedit: a copyeditor that knows what to leave alone

**Status:** **Proposed spec, 2026-10-29. Unbuilt.** Design calls open for the owner (§Design calls). Awaits owner admission; no build until then. Roadmap: a Horizon Capacities Tier 2 entry is added once the manuscript-indexing spec PR (#406, which holds `ROADMAP.md` and reopens copyediting in §Not Planned) has landed. Proposed implementation surface: `plugins/apodictic/scripts/copyedit.py`, `validate.sh copyedit`, a `core-editor/references/voice-aware-copyediting.md` module and a `/copyedit` command.
<!-- built-when: plugins/apodictic/scripts/copyedit.py -->

## Why

The owner reopened copyediting on 2026-10-29 with one caution: copyediting is more than fixing spelling, and a good copyeditor leaves alone a great deal that looks like error when it is the voice and register of the book. Dialect spelling in a character's speech, fragments used for rhythm, a sentence that opens with "And", a narrator who never uses quotation marks, an essayist's run-on that is doing argumentative work: a rule-driven checker "fixes" all of these, and the book comes back flattened.

Copyeditors manage this with three tools, and this spec builds all three:

- **The style sheet.** A running record of every decision about spelling, hyphenation, capitalization, numbers and names, so the same choice is made the same way through the book. Its most important entries are often the departures: "Jim's dialect spellings are deliberate; do not regularize."
- **The query.** When a copyeditor cannot tell whether something is error or intention, they ask the author instead of changing it.
- **Stet.** The author's answer that the original stands. Once given, it holds for every later instance.

The design center is **inconsistency is the signal, deviation is not.** A nonstandard form used the same way forty times is probably a choice. A form that appears both ways is the classic copyedit target, and the useful question is which form the book uses.

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

APODICTIC's Firewall says diagnostics identify problems and never rewrite manuscripts, and the annotated-manuscript spec rules out tracked changes. Copyediting needs some replacement text: "recieve" has one right answer, and making the author type it is the kind of busywork the tool exists to remove. This spec draws the line narrowly (D2):

- **The snapshot is never changed.** All work is against the frozen snapshot, and the validator proves it (E8).
- **Replacement text exists only for mechanical kinds** (§Kinds), and only inside a size cap (E5). Anything about wording, clarity, usage or voice is a **query** with no replacement text at all.
- **Nothing is applied without the author's pick.** Picks can be made in bulk by kind ("accept every spelling suggestion"), but silence never applies anything.
- **Picks export to a copy** (CriticMarkup first, DOCX tracked changes later), the way Spec 113's export applies picks.

So the tool writes no prose. Its replacements are the size of a typo fix, the author chooses each one, and everything larger is a question.

## The voice ledger

The heart of the design. The ledger is the "leave alone" half of the style sheet: a list of forms, patterns and zones the copyedit must not regularize. Each entry carries its evidence and its source:

| Source | Example entry | Strength |
|---|---|---|
| **Author-declared** (the intake questions and the style-sheet review) | "No quotation marks anywhere; dialogue is unmarked." "Lowercase *god* throughout." "Jim's speech uses dialect spelling." | Binding |
| **Consistency harvest** (Phase 1) | `alright` occurs 37 times, `all right` never | Presumed deliberate; author confirms on the review sheet |
| **Idiolect preservation list** (SETEC, when a baseline exists) | the bigram `which is to say` | Presumed deliberate |
| **Baseline roughness** (SETEC, when a writer baseline exists) | fragment rate and sentence-initial And/But rate are inside the writer's normal band | Pattern rule: fragments and initial conjunctions are not flagged |
| **Zones** | dialogue; quoted and cited material (epigraphs, block quotes, sources); close-POV narration in multi-POV fiction; verse and lyrics | Query-only areas (E3) |

Entries are stored as `apodictic.voice_ledger.v1` blocks in `[Project]_Style_Sheet.md`, next to the ordinary style decisions. The ledger persists across runs and revisions, so an author's stet holds for the next draft.

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

The author gets a **style-sheet review**: each competing-forms item with its counts and a proposed choice, and each proposed ledger entry with two or three examples in context. The author picks forms and confirms or rejects ledger entries. Unconfirmed ledger entries still protect (a false stet costs nothing; a false correction costs voice), and they are shown again at the next run.

### Phase 2: the pass

One call per paragraph, with the neighbouring paragraphs as read-only context, as in Spec 113 §1. The call receives the style sheet, the ledger, the register profile and the paragraph's zones, and returns candidate items in the record below. Every candidate then goes through the deterministic checks (§Validator) before the author sees it. A candidate that touches a ledger entry or a zone is converted to a query or withheld; it never reaches the author as a replacement.

### Phase 3: author review and export

The author sees a numbered list (`P<paragraph>.<n>`, numbering fixed once as in Spec 113 §3), grouped by kind, with queries rendered as margin comments on the annotated-manuscript path. The author accepts, rejects, or answers each query. A query answer of "stet" adds a ledger entry, so the same question is not asked again. Accepted picks export to a copy of the snapshot.

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

- `kind` is closed: mechanical kinds `spelling`, `consistency`, `punctuation_mechanics`, `word_confusion`, `style_sheet`; query-only kinds `agreement`, `usage`, `clarity`, `fact_consistency`, `voice_check`.
- `disposition` is `suggest` (has a `replacement`) or `query` (`replacement` is null and `reason` is the question to the author). There is no `apply`.
- `consistency` and `style_sheet` items name the style-sheet decision in `style_ref`; their replacement must be the form that decision chose (E6).
- `voice_check` is how the pass says "this looks like an error, but it may be voice": it is always a query, and it is the kind a converted ledger or zone hit becomes.

## The `copyedit` validator

Mechanical checks, ERROR unless marked W. E1, E2, E4 and E7 follow Spec 113 §3 and §4.

- **E1 schema.** The closed record; unique ids; closed enums.
- **E2 provenance.** `original` equals the snapshot bytes at `span`; the span falls on code-point boundaries and inside one paragraph.
- **E3 ledger and zone guard.** No `suggest` item whose span touches a ledger entry or a zone. Such an item must be a `query`. This is the check that enforces the owner's caution mechanically for everything the ledger knows about.
- **E4 shape.** A replacement differs from its original, contains no line break, and does not leave its paragraph empty.
- **E5 size cap.** A `suggest` item's span covers at most a few words (default: three word tokens changed, one sentence touched); a larger change must be a query. This keeps replacement text at typo scale (D2).
- **E6 style-sheet agreement.** A `consistency` or `style_sheet` suggestion's replacement equals the chosen form in its `style_ref`; a choice the author has not made yet yields a query.
- **E7 combined selection.** The author's picks for a paragraph apply as a set only when no two overlap and the paragraph stays non-empty (Spec 113 §4).
- **E8 no mutation.** The snapshot's sha256 still matches its binding, and the export is the snapshot plus exactly the picked replacements.
- **W1 never-flag list.** An item whose reason or kind matches a never-flag rule is withheld and counted.
- **W2 flattening check** (when SETEC and a baseline are available). After picks are applied to the copy, punctuation cadence and productive roughness are rerun against the snapshot; a feature that moved beyond the writer's band is reported with the picks that moved it.
- **W3 query load.** Query density per chapter, so the author sees where the pass leaned hardest.

**Honest limit.** E3 protects only what the ledger and zones cover. A voice choice the ledger has never seen, used once, can still draw a suggestion. That gap is why unknown departures default to a `voice_check` query (D3) and why the evaluation measures it directly.

## Evaluation before release

- **Hostile fixtures.** Public-domain passages chosen for voice: dialect-heavy dialogue (Twain's *Adventures of Huckleberry Finn*, which opens with an explanatory note that its dialects are deliberate), unmarked or idiosyncratic punctuation, a period essay with long periodic sentences; plus synthetic passages with deliberate fragments and comma splices. Errors are planted into each fixture: typos, inconsistent hyphenation, wrong-word confusions, unbalanced quotation marks.
- **Measures.** (a) **Voice false-correction rate:** suggestions that would change a voice item, reported separately for ledgered items (must be zero, by E3) and unledgered items (the honest-limit number). (b) **Planted-error recall** by kind. (c) **Query precision:** share of queries a reader judges worth asking.
- **Baseline arm.** The same fixtures through a plain "copyedit this" prompt with no ledger or register profile, to show what the voice machinery buys. Report the numbers in the module doc and claim nothing beyond them.

## Where it lives

A core-editor workflow module (`core-editor/references/voice-aware-copyediting.md`) invoked by a `/copyedit` command with `style-sheet` and `pass` modes, routed like `/legal-risk` and `/world-bible`. The Idiolect Preservation audit's existing "before a heavy copyedit pass" trigger points here. Fiction and nonfiction both (D4). Stdlib-only for the core; the SETEC surfaces are optional and degrade cleanly, as they do in the prose-measurements audits.

## Increment plan

1. **Style sheet, ledger and queries only.** `voice_ledger.v1`, the Phase 1 harvest and review, the never-flag list, and a pass that emits only queries. No replacement text ships in this increment, so it stands inside today's Firewall on its own and is already useful: the consistency queries are most of a copyeditor's mechanical value.
2. **Suggestions.** `copyedit_item.v1` with `suggest`, E1–E8, W1, W3, bulk accept by kind, CriticMarkup export of picks, a canonical worked example in `--check-all`.
3. **Voice post-check and exports.** The productive-roughness shim, W2, DOCX tracked-changes export, and the fixture evaluation above.

## Design calls

Recommendations first; the owner decides.

- **D1 Consume or extend.** *Recommend:* port Spec 113's suggestion contract and checks into APODICTIC (spec dependency, no code import or new pin); consume the SETEC idiolect, roughness, cadence and POV surfaces through the existing SETEC contract. *Alternatives:* pin voicewright and call the 113 runner (heavy private harness, period brief); or generalize 113 inside voicewright and have APODICTIC call it.
- **D2 Replacement text and the Firewall.** *Recommend:* replacements only for mechanical kinds, at typo scale (E5), author-picked, exported to a copy; everything else a query. *Alternatives:* queries only (purest Firewall, more author typing); or full sentence-level suggestions like Spec 113 (a larger Firewall exception).
- **D3 Unknown departures.** A nonstandard form the ledger does not cover and that is used once. *Recommend:* a `voice_check` query. *Alternatives:* leave silently (misses real typos), or suggest a fix (the flattening the owner warned about).
- **D4 Scope.** *Recommend:* fiction and nonfiction both; unlike an index, every book is copyedited.
- **D5 Style authority.** *Recommend:* Chicago-style conventions for books and AP-style for short-form journalism by default, author-changeable, with the module stating every rule in its own words.
