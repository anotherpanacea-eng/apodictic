# Manuscript Index Builder amendment: the `embedded` scheme

**Status:** **Parked design note (owner, 2026-10-30), not build-ready.** Recheck it against the author's real LaTeX setup when a build is wanted, and close §Open for a future build first. Spec only; not built. It concerns [`manuscript-indexing.md`](manuscript-indexing.md) §Phase B (the `embedded` row of the scheme table) and §Increment plan item 3. Increment 3 (PR #415, draft) leaves this scheme out on purpose: a first LaTeX tagger was built, then cut after a Codex adversarial review found it unsafe. This note is the lexer-level design that review asked for, plus a decision on Word XE fields. **Until a build is wanted, point LaTeX and Word authors to the `page` scheme on the proof (§Is it worth building).**

## What the scheme does

The `embedded` scheme does not compute locators. It writes LaTeX `\index{...}` tags into a **copy** of the author's source at each placed anchor. The author's typesetting run (LaTeX, then makeindex, then LaTeX again) then generates the page numbers. The tags travel with the source, so repagination needs no rerun of the tool.

It reuses the Phase B machinery unchanged. `_published` gives the accepted, I1–I4-clean headings; `_placements` lists their substantive anchors; `fold` and `_quote_key` give the match keys; and `_find_and_order` runs the unique-match search and the order check. The only new parts are the LaTeX lexer that supplies the text to search (§Lexer contract), the rules for where a tag may go (§Insertion rules), the entry text (§Escaping) and the writer (§Output).

CLI: `book_index.py locate <index_map.md> --scheme embedded --source <main.tex> [--source <chapter.tex> ...]`, with the files listed in reading order. Output is a folder of tagged copies plus a report (§Output). There is no locators file and no `format` step: makeindex and the press's `.ist` style format the index.

**Firewall fit.** This is the first scheme that writes a file the author sends to press. It never edits the author's source. It writes a **copy** that differs from the input only by inserted `\index` tags, and every run checks that before anything is written (§Output, the strip-and-compare gate). The parent spec's §Firewall fit, the module's firewall bullets and the `/book-index` command text, which now say the tool "never changes the manuscript", must say this when the scheme is built (§Build surface).

**Snapshot fit.** Quotes are matched against the reader-visible text of the `.tex` (§Lexer contract), not its markup. The map should be anchored on a prose rendering of the same source, for example `pandoc -t markdown` output. A map anchored on raw LaTeX has `\emph{` and similar markup in its quotes, and most of its anchors will go to the unresolved list.

## Scope

**Supported.** LaTeX sources in UTF-8 (pdfLaTeX, XeLaTeX or LuaLaTeX) and makeindex's default input syntax: `!` for levels, `@` for sort keys, `|` for encapsulators and `"` as the quote character. Headings and subheadings (one level, as in the map), page ranges, See and See also. Several files in reading order. Exactly one of them holds `\begin{document}` and `\end{document}`; the others are included chapter files.

**Refused (whole run; nothing written).** The run stops with a reason when the tool cannot trust its reading of the source:

| Condition | Why |
|---|---|
| A `.docx` source, or any non-`.tex` source | Word XE fields are not supported (§Word XE fields) |
| A file that is not valid UTF-8 | Byte-faithful copying and matching need one known encoding |
| `\catcode`, `\ExplSyntaxOn` or `\scantokens` anywhere; `\makeatletter` in the body | These change how later text is tokenized, which the lexer cannot follow. `\makeatletter`…`\makeatother` in the preamble is allowed and makes `@` a letter until `\makeatother` |
| An inline-verbatim maker in **any file**, preamble, body or chapter file: `\DefineShortVerb`, `\MakeShortVerb`, `\lstMakeShortInline`, `\newmintinline`, `\CustomVerbatimCommand`, `\RecustomVerbatimCommand`, or an xparse command definition (`\NewDocumentCommand` and its variants) whose argument spec has `v` | These make inline verbatim out of a character or a command name the lexer cannot know. A tag inside one prints as literal text in the book. Verbatim *environments* defined in the preamble need no row: they are off the prose allowlist, so they are opaque, and the end-of-file balance refusal catches one whose raw content upsets the lexer |
| In the body, any `\if…` conditional other than `\iffalse` | Both branches look like prose to the lexer, so a tag could land in the branch that is never typeset, and its index entry would vanish silently. `\iffalse`…`\fi` is read as dead text (§Lexer contract) |
| `\begin{document}` or `\end{document}` missing, repeated, out of order, or in more than one file; or found in a chapter file | The body cannot be bounded (finding 4) |
| An unbalanced brace or environment at the end of any file, or at the real `\end{document}` | The lexer has lost track, so none of its regions can be trusted |
| An existing `\index` in any body | The source is already tagged, by the author or by an earlier run. Tagging again would double every entry and unbalance every range |
| The output folder already exists | The output must never overwrite the input (finding 6) or an earlier tagged copy the typesetter may have edited (§Output) |
| A tagged copy that, with its recorded tags stripped, does not equal the input bytes | A lexer or writer bug changed the author's text. Nothing is written (§Output) |

**Unresolved (per anchor, listed in the report).** These are the existing Phase B reasons (`not_found`, `ambiguous_match`, `out_of_order`, `ambiguous_order`, `conflicting_matches`, the end-quote reasons, `quote_folds_away`) plus one new one:

- `no_safe_insertion_point`: the quote (or the end quote of a range) matched, but has no qualifying boundary (§Insertion rules).

`not_found` will be common in this scheme. It covers every quote that lies inside, or runs across, a region the lexer does not show as prose: footnotes, math, floats, captions, section titles, citations and cross-references, and environments outside the prose list. That is by design (§Lexer contract), and the report says so in one line.

**Left out (listed beside the unresolved anchors), as in `format`:**

- A See or See also whose target is not printed. This is the existing rule: a target prints only when it has at least one placed tag of its own or in a subheading.
- A See or See also whose target text contains `!`, `@` or `"`, reason `see_target_unquotable`. Whether makeindex honors `"` quoting inside a `|see{…}` argument has not been checked on a real TeX installation (none was available when this was drafted), so the target is left out rather than risk an entry that prints a stray quote character. If the build session confirms the quoting with the TeX test (§Tests, T-TeX), this rule is dropped.
- A heading or subheading whose sort text (§Escaping) is empty, reason `no_sortable_text`.

## Lexer contract

The lexer turns each file into a sequence of tokens. Each token records its byte span in the source, its kind, and its **region**. The visible text and its index map are built from the tokens, never from raw characters. Every boundary the tool can insert at is a boundary between two tokens. This is what makes token-splitting impossible (finding 1).

### Tokens (TeX's default catcodes)

| Token | Form |
|---|---|
| control word | `\` plus letters (plus `@` while `\makeatletter` is in force in the preamble), **including the spaces and at most one line end that TeX skips after it** |
| control symbol | `\` plus one non-letter: `\&`, `\%`, `\'`, `\\`, `\ `, and so on |
| comment | `%` to the end of the line, plus the line end and the next line's leading spaces |
| group open / close | `{` / `}` |
| math shift | `$`, `$$`, `\(`, `\)`, `\[`, `\]` |
| ligature | ``` `` ```, `''`, `--`, `---`, `` ?` ``, `` !` ``, `,,`, `<<`, `>>` (always one token, even in encodings where some of them are not ligatures) |
| character | any other single character; `~`, `&`, `#`, `^` and `_` are their own kinds |
| whitespace | a run of spaces and tabs with at most one line end; two or more line ends form a **paragraph break** token |

**Verbatim forms are read raw.** Their whole extent is one opaque token, so nothing inside them can open a group, start a comment or end the document. The forms are:

- `\verb<d>…<d>` and `\verb*<d>…<d>` (the delimiter is the next character and the form ends on the same line), and likewise fancyvrb's `\Verb` and `\Verb*`, `\spverb` and `\tcboxverb`;
- `\lstinline` with a delimiter or a brace argument;
- `\mintinline{<lang>}` with a delimiter or a brace argument;
- `\url{…}`, `\path{…}`, `\nolinkurl{…}` and the first argument of `\href{…}`;
- the environments `verbatim`, `verbatim*`, `Verbatim`, `Verbatim*`, `BVerbatim`, `LVerbatim`, `lstlisting`, `minted`, `comment`, `filecontents` and `filecontents*`, from `\begin{name}` to the first literal `\end{name}`.

Any other raw environment, such as one the preamble defines with fancyvrb or listings, is opaque because it is off the prose allowlist. If its raw content (a `%` or an unbalanced `}`) throws off the lexer, the end-of-file balance refusal stops the run. That refusal is the backstop for every raw form not listed here.

**Dead text.** `\iffalse` up to its matching `\fi` is one opaque token. Nested `\if…` control words are counted to find the match.

### Regions

Every token is in exactly one region:

- **preamble**: before the real `\begin{document}` in the main file. Never searched, never tagged.
- **after-document**: after the real `\end{document}`. Never searched, never tagged. TeX ignores it.
- **prose**: body text that a reader sees in the main text flow.
- **prose-argument**: the argument of an allowlisted prose command. Searched, but never tagged.
- **opaque**: everything else in the body.

The real `\begin{document}` is the first control word `\begin` in the main file at group depth 0, not inside a comment, verbatim form or dead text, followed by the group `{document}`. The real `\end{document}` is the same with `\end`, at depth 0 with no open environment. Both are found from the token stream, never by a string search, so a commented `% \end{document}`, one inside `verbatim`, and one inside `\iffalse` are all ignored (finding 4). A chapter file has no preamble and no after-document region: the whole file is body.

**Prose** is the allowlist; anything not on it is opaque.

- Environments: `document`, `quote`, `quotation`, `verse`, `itemize`, `enumerate`, `description`, `center`, `flushleft`, `flushright`. Text directly inside them is prose, and so is text in plain brace groups nested inside them, such as `{\itshape …}`.
- Prose commands, whose argument is **prose-argument**: `\emph`, `\textit`, `\textbf`, `\textsc`, `\textsl`, `\textup`, `\textrm`, `\textsf`, `\textnormal`, `\enquote`. `\enquote{x}` is visible as `"x"`.
- Known zero-argument commands, which add no text: font and size declarations (`\itshape`, `\bfseries`, `\em`, `\small`, …), `\noindent`, `\indent`, `\par` (which counts as a paragraph break), `\centering`, the `\…skip` and page-break commands, `\hfill`, `\relax`, `\xspace`, `\@` and `\/`. A brace group right after one of these is a plain group. `\item` is known too: its optional `[…]` argument is opaque and the text after it is prose.
- Commands that produce text: `\ldots`, `\dots` and `\textellipsis` (as `…`), `\textendash`, `\textemdash`, `\TeX`, `\LaTeX`; the control symbols `\& \% \$ \# \_ \{ \}` (as the character); `\ `, `\,`, `\;`, `\:` and `~` (as a space); `\\` (as a space, with its `*` and `[…]` opaque); `\-` (as nothing, inside a word). The standard text accents `\' \` \^ \" \~ \= \.` and `\c \v \u \H \k \r`, in the forms `\'e`, `\'{e}` and `{\'e}`, compose to the NFC character. So do the named letters `\i \j \ss \ae \AE \oe \OE \o \O \aa \AA \l \L`.
- Any other control word or symbol is **opaque**. So is every `[…]` and `{…}` group that directly follows it, in any number, with whitespace between them allowed. The lexer does not know such a command's arity, so it treats every group after it as an argument. `\ref{…}`, `\cite[…]{…}`, `\label{…}`, `\footnote{…}`, `\section{…}`, `\caption{…}` and `\includegraphics[…]{…}` are all opaque this way (finding 2). A group that was really a plain group is lost with them, which is a safe failure: the quote goes unresolved.
- Math, every environment not listed above (including `figure`, `table`, `tabular`, `minipage`, `equation` and theorem-like environments) and every verbatim form are opaque.

**Opacity is inherited.** Every token inside an opaque environment, an opaque argument or math is opaque. That includes prose environments, prose commands and plain groups nested inside it. A prose environment is prose only when every environment enclosing it is prose or `document` and it sits inside no opaque argument. So the body text of `\begin{figure}\begin{center}…`, of `\begin{minipage}…\begin{quote}…` and of `\footnote{\begin{itemize}…}` is all opaque. Floats and footnotes move away from their source position when typeset, so a tag there would break the source-order pairing that range merging relies on.

### Visible text

The visible text of a run is the visible text of each file's prose and prose-argument tokens, in reading order. Each opaque token, and each boundary between files, contributes one **barrier** character, U+FFFC. No folded quote contains it, so no match can cross an opaque region or a file boundary. Every visible character maps back to the token it came from. `fold` then runs on the visible text exactly as on a proof page, and `_find_and_order` runs on the result.

The amendment does not touch `_read`: the tagger reads each file as bytes, decodes it as UTF-8 with no newline translation (`newline=""`), and writes the same way. CRLF files stay CRLF, and a byte-order mark is kept.

## Insertion rules

A **qualifying boundary** is a gap between two adjacent tokens A and B where all of the following hold.

1. A is in a **prose** region, at the top level of the body, inside no macro argument (finding 2). Plain groups are allowed; prose-argument is not, so a tag never goes inside `\emph{…}`. Inside an argument, `\index` gets text that was tokenized before `\index` could switch catcodes, and specials in the entry would then break.
2. A is a word-ending token: a letter or digit character, an accent construct or named letter ending in a letter or `}`, or the `}` that closes a visible group or prose argument.
3. B is whitespace, a paragraph break, a comment, `~`, one of `. , ; : ! ? ) ]`, the ligatures `''`, `--` or `---`, or a single `'` that is not followed by a letter. A hyphen inside a compound and an apostrophe inside a word (`self-governing`, `Kant's`) are therefore never boundaries.
4. At least one visible character comes before the gap in the same paragraph. So TeX is in horizontal mode there: an `\index` in vertical mode, for example straight after a section heading, adds a node that lets a page break fall between the heading and its text.

Where tags go:

- **A point anchor** gets `\index{<entry>}` at the first qualifying boundary whose A lies inside the quote. That is normally the end of the quote's first word. The page is the one where that word ends. In the `page` scheme it is the page where the quote starts, and the two differ only when the first word is broken across a page.
- **A range anchor** gets `\index{<entry>|(}` at the first qualifying boundary inside the quote, and `\index{<entry>|)}` at the last qualifying boundary whose A lies inside the end quote.
- **No qualifying boundary**: the anchor goes to the unresolved list as `no_safe_insertion_point`.
- **Several tags at one boundary** are written together with nothing between them. After range merging, no two tags of one entry share a boundary, so their order cannot change the index.

### Merging ranges for one entry (finding 5)

Work per **entry**, meaning one owner (a heading's own anchors, or one subheading's anchors), after placement:

1. Take its ranges as boundary-offset intervals and sort them by start.
2. Merge two ranges when the second starts at or before the first one's end, so overlapping, nested and touching ranges all merge. The merged range runs from the earliest `|(` boundary to the latest `|)` boundary.
3. Drop any point tag whose boundary lies inside a merged range, since the range already covers it, and drop point tags that repeat a boundary.
4. Write one `|(` and one `|)` per merged range.

So for each entry the `|(` and `|)` tags alternate in source order, starting with `|(`, with no nesting. That is the balanced form makeindex needs. A heading and its subheading are separate entries, and their ranges are never merged with each other.

All tags lie in main-text prose (not floats, footnotes or marginal notes), so TeX writes them to the `.idx` file in source order, and the pairing in the source is the pairing makeindex sees.

### See and See also

See and See also tags go in one block placed straight after the real `\begin{document}`, one per line, with no blank line. The rule for which targets print is `format`'s rule (§Scope, Left out). There is one tag per heading per field, with the targets sorted by the formatter's `_sort_key` and joined with `; `:

```latex
\begin{document}
\index{reflecting judgment|see{judgment, reflective}}
\index{Kant, Immanuel|seealso{judgment, reflective; spectator}}
```

A `|see` entry prints no page number, so it does not matter which page it is written on. Its position only has to be in the body and safe. The first tagger appended its block before `\end{document}`, which has two faults. A string search found a commented `\end{document}` (finding 4). And a write node left after the last page can make TeX ship out an extra blank page (T-TeX checks the page count). Directly after `\begin{document}`, the node rides on the first page that ships. `\seealso` comes from `makeidx` or `imakeidx`; a document using an index package without it fails to compile, which is loud, not silent.

## Escaping (finding 3)

Each level of an entry (the heading, then the subheading label after `!`) is written as `sort@display`, or as `display` alone when the sort text equals the display text.

**Display text**, in this order:

1. **TeX escaping**, one character at a time:

   | Char | Written as | | Char | Written as |
   |---|---|---|---|---|
   | `\` | `\textbackslash{}` | | `#` | `\#` |
   | `{` | `\textbraceleft{}` | | `^` | `\textasciicircum{}` |
   | `}` | `\textbraceright{}` | | `~` | `\textasciitilde{}` |
   | `%` | `\%` | | `\|` | `\textbar{}` |
   | `&` | `\&` | | `_` | `\_` |
   | `$` | `\$` | | | |

   The `\text…{}` forms keep braces balanced, which both `\index` and makeindex need, and work in the default OT1 and T1 encodings. `|` is TeX-escaped rather than makeindex-quoted because a bare `|` prints as a dash in OT1.

2. **makeindex quoting** of what remains: `!` becomes `"!`, `@` becomes `"@`, and `"` becomes `""`. No TeX escape ends in a backslash. That matters because makeindex does not treat `"` as a quote when a `\` comes right before it.

**Sort text** is the original text in NFKD form, with combining marks removed and every character in ``\ { } % & _ $ # ^ ~ | ! @ "`` deleted, and whitespace runs collapsed to one space. It therefore needs no escaping. If it comes out empty, the heading is left out as `no_sortable_text`.

**See targets** use the display text of the target heading, TeX-escaped only. Targets containing `!`, `@` or `"` are left out for now (§Scope).

Examples:

| Map text | Entry written |
|---|---|
| `judgment, reflective` | `\index{judgment, reflective}` |
| heading `Kant, Immanuel`, subheading `on judgment` | `\index{Kant, Immanuel!on judgment}` |
| `AT&T` | `\index{ATT@AT\&T}` |
| `50% rule` | `\index{50 rule@50\% rule}` |
| `C#` | `\index{C@C\#}` |
| `x_1` | `\index{x1@x\_1}` |
| `e^x` | `\index{ex@e\textasciicircum{}x}` |
| `Yahoo!` | `\index{Yahoo@Yahoo"!}` |
| `user@host` | `\index{userhost@user"@host}` |
| `pipe \| operator` | `\index{pipe operator@pipe \textbar{} operator}` |
| `"scare" quotes` | `\index{scare quotes@""scare"" quotes}` |
| `\LaTeX` (literal backslash) | `\index{LaTeX@\textbackslash{}LaTeX}` |
| `{braces}` | `\index{braces@\textbraceleft{}braces\textbraceright{}}` |
| `Émile` | `\index{Emile@Émile}` |
| range on `judgment, reflective` | `\index{judgment, reflective\|(}` … `\index{judgment, reflective\|)}` |

The two halves of a range are built by the same function from the same owner, so their key text is byte-identical. makeindex needs that to pair them.

**Known limit.** With `babel` or `polyglossia` loaded for a language that makes `"` active (German, Dutch and others), `"!` inside `\index` may be read as a shorthand. `\index` neutralizes only TeX's own special characters, not babel's. Entries that need makeindex quoting are rare, and the author reviews the typeset index anyway, so this stays a documented limit rather than a check. A press using a custom `.ist` that changes the quote, level or actual characters is out of scope.

## Output (finding 6)

- **Tagged copies.** One file per input, under its original basename, in a new folder `[Project]_Index_Tagged_[runlabel]/` beside the map. Keeping the basenames lets the files drop into a copy of the author's project tree, so `\include{ch1}` still resolves.
- **Report.** `[Project]_Index_Tagged_Report_[runlabel].md` lists the files written with their tag counts, the unresolved anchors with reasons, and the left-out cross-references. It also carries the one-line `not_found` note (§Scope).
- **Strip-and-compare gate.** Tags are inserted only at byte offsets in the original bytes, and the writer records each inserted span. Before anything is written, it strips the recorded spans from every tagged copy and requires the result to equal that input's bytes exactly. Any mismatch refuses the whole run, and nothing is written. This turns "the copy differs from the input only by `\index` tags" from a fixture claim into a check on every run.
- **Never overwrite.** The tool creates `[Project]_Index_Tagged_[runlabel]/` with `os.makedirs(exist_ok=False)`, refuses the run if it already exists, and writes only inside it. Each file is written to a temporary name there and renamed into place. Inputs are opened read-only.

The output folder name comes from the map's runlabel. A rerun after the author fixes something therefore needs the old folder moved or deleted first. That is deliberate: the typesetter may have edited the old copies.

## Tests

The tests go in `book_index.py`'s Phase B self-test, like the other schemes. **R1–R6 are the regressions for the six review findings.**

**R1. Tokens never split.** For each of these, a quote that ends or begins at the construct places its tag at a token boundary. Removing the tag from the output gives the input byte for byte, and re-lexing the output gives the input's tokens plus the tag's own:

- `Smith \& Jones`, with the quote `Smith & Jones`;
- ``` ``word'' ```, with the quote `word`, where the tag goes before `''` and never between the two apostrophes;
- `pages 10--20` and `thus---and`;
- `Andr\'e said` and `Andr\'{e} said`;
- `` ?`Qué `` and `` !`Ay ``;
- `\LaTeX is` (the skipped space after a control word is never treated as a boundary);
- `hy\-phen`.

**R2. No tags in verbatim, math or non-prose arguments.** A quote whose text occurs only inside each of these goes to the unresolved list as `not_found`, and the output contains no tag inside that construct:

- `\verb|…|` and `\verb*+…+`;
- the `verbatim`, `lstlisting` and `minted` environments;
- `\Verb|a, b|` in prose;
- `\url{}`, `\href{}{}`'s first argument, `\ref{}`, `\cite[…]{}`, `\label{}`, `\footnote{}` and `\section{}`;
- `$…$` and `equation`;
- a `figure` caption;
- prose environments nested in opaque ones: body text of `figure > center`, `minipage > quote` and `\footnote{\begin{itemize}…}`;
- `\iffalse…\fi`.

A quote that occurs once in a verbatim block and once in prose is placed in the prose occurrence: opaque text does not count toward the uniqueness check. `\verb|a}b%c|` followed by ordinary prose does not derail the lexer, and a quote in that prose is still tagged. A quote whose first word is inside `\emph{…}` gets its tag after the closing `}`, never inside it.

**R3. Escaping.** Every row of the examples table is a test. One heading carries all of `\ { } % & _ $ # ^ ~ | ! @ "` together. A See target with `!` is left out as `see_target_unquotable`. A heading made only of specials is left out as `no_sortable_text`.

**R4. The real `\begin{document}` and `\end{document}`.** A commented `% \end{document}` before the real one, an `\end{document}` inside `verbatim`, and one inside `\iffalse` are all ignored. A quote in text after the real `\end{document}` is `not_found`. The See block lands after the real `\begin{document}`, not a commented one. Two real `\end{document}`s, none, or a `\begin{document}` in a chapter file each refuse the run.

**R5. Overlapping ranges.** Two overlapping ranges, a nested range and two touching ranges on one entry each produce exactly one `|(`…`|)` pair. A point inside a range is dropped. A heading's range and its subheading's range overlapping produce two independent pairs. A property check over all range fixtures: for every entry, the tags in source order alternate `|(`, `|)`, starting with `|(`.

**R6. Output never overwrites input.**

- An existing output folder is refused.
- An input whose body already contains `\index` (for example the tool's own earlier output) is refused.
- A writer fault that changes one byte of prose is caught by the strip-and-compare gate: the run is refused and nothing is written.

**Other tests.**

- **Refusals:** one fixture for each other refusal row in §Scope (catcode, body conditional, unbalanced group, non-UTF-8, `.docx`). The inline-verbatim row gets a chapter file containing `\MakeShortVerb`. The balance backstop gets an unlisted raw environment containing `%` or `}`.
- **Multi-file:** a main file and two chapter files. A quote in chapter 2 is tagged in chapter 2's copy. Listing the chapters out of order sends the affected anchors to `out_of_order`. A quote that would cross the file boundary is `not_found`.
- **Insertion edges:** a quote at a paragraph's start whose first token is `{` gets no tag before any visible character (rule 4). A quote that crosses a footnote is `not_found`.
- **Bytes:** CRLF and BOM input keeps both.
- **T-TeX (`skipif` without `pdflatex` and `makeindex`):** compile a tagged fixture, run makeindex, and check the `.ind`. Every entry from the escaping table must appear as expected, the ranges must print as ranges, the See lines must be present, and the page count must be the same as the untagged compile (no blank page added). Run it once on a machine with TeX during the build, and record the result in the PR. This test also settles the `see_target_unquotable` question.

## Word XE fields: not supported

**Decision: refuse `.docx` sources and recommend the `page` scheme on the proof.** Reasons:

- **It is a second lexer of the same size, in XML.** A word's text in OOXML can be split across many `w:r` runs: by spell-check and revision-session ids, by formatting changes, by `w:hyperlink`, `w:smartTag`, `w:sdt`, simple and complex fields, `w:footnoteReference`, `w:sym`, `w:tab`, and soft and no-break hyphens. Tracked changes (`w:ins`, `w:del`) mean the visible text depends on whether revisions are accepted. Inserting an XE field means splitting a run and cloning its `w:rPr`, then adding the `begin`, `instrText` and `end` field runs. A range needs a uniquely named bookmark around the span plus the field's `\r` switch, so three edits per range. Every hazard the LaTeX review found has a Word twin, with fewer readable failure signals.
- **The payoff is smaller.** Word-based production usually ends in a PDF proof, and the `page` scheme already reads that proof. InDesign's Word import has an option to bring Word index entries in as index markers, but whether a press's workflow keeps them is outside the tool's control and cannot be checked from here.
- **Nothing is lost by waiting.** The anchors are quotes, so a `page` rerun after repagination costs one command (parent spec §Phase B).

Revisit only if a press requires XE fields in the author's Word file. The command text already says to offer the `page` scheme instead, so no change is needed there.

## Is it worth building?

**What `embedded` adds over `page`.** Tags generate their numbers at every typesetting run, so late repagination after the author's last look needs no rerun and no proof PDF. Some LaTeX-based production workflows accept, or ask for, author-supplied `\index` tags.

**What it costs.**

- The lexer, regions, insertion rules, escaping, range merging and writer come to roughly 500 lines of code and 300 of tests.
- It adds a failure class the other schemes do not have: a tagged copy that fails to compile, or compiles with a quietly wrong entry.
- It resolves fewer anchors than `page` does. Anything in a footnote, a caption, a section title, a theorem environment or next to a citation goes to the unresolved list, while the proof PDF shows all of that text plainly.
- It serves only LaTeX authors. There is no evidence yet of how many APODICTIC nonfiction authors typeset in LaTeX themselves.

**The `page` scheme already covers the core need.** The parent spec's design center is that page numbers are looked up mechanically and never typed, and that repagination costs one rerun. `page` meets both for every author who gets a proof PDF, which is every author whose press typesets the book.

**Recommendation.** Do not build this now; the owner parked it as a design note on 2026-10-30. Point LaTeX and Word authors to `page` on the proof, which is what the `/book-index` command already says. The durable parts are the answers to the six Codex findings, the Word XE decision and the three P1 fixes folded in here. If a real author or press needs `\index` tags in the source, first recheck the package and command lists against that author's LaTeX setup, then close §Open for a future build. A cheaper alternative was considered and rejected: a list of ready-made `\index{…}` strings for the author to paste in by hand. It hands the most tedious part of the job back to the author, against the parent spec's design center.

## Build surface (when built)

- `book_index.py`: the lexer, `--scheme embedded` with a repeatable `--source`, and the tests above.
- The parent spec: the status line, plus the `embedded` row of the scheme table pointing here.
- The module reference and the `/book-index` command text: the scheme's procedure and its LaTeX-only scope.
- The firewall wording in the parent spec's §Firewall fit, the module's firewall bullets and the command text: this scheme writes a copy that differs from the input only by inserted `\index` tags, checked on every run. The command text also gets one line: the model never creates, edits or deletes a tagged copy or the `[Project]_Index_Tagged_*` folder, and never hand-writes an `\index` tag. On a compile failure or a refused rerun, it reports and lets the author act.
- A changelog fragment, and the ROADMAP item 20 status.

No new validator, schema or canonical fixture is needed. The scheme reads the same accepted map, and its output is a copy for the typesetter, not an APODICTIC artifact.

## Open for a future build

The review's P2s, one line each, are not folded in. Close them before any build. The panel's summary counts nine P2s but itemizes seven; the three P3s are listed with them so nothing is lost.

1. **Reading order:** take it from `main.tex`'s live `\include`/`\input` sites, not the `--source` order. Refuse on `\includeonly` or an unlisted or unspliced file, and write outputs under paths relative to main's folder, which also ends basename collisions.
2. **Visible text of ligatures, comments and breaks:** map each ligature to its Unicode glyph, since `fold` drops backticks. A comment gives nothing, and a paragraph break is a space or a barrier. A comment counts as B only when the next visible token qualifies, so `word%⏎next` gets no tag. Name a fitting pandoc invocation.
3. **`\if…` handling:** define a conditional (excluding `\iff` and `\ifthenelse`), and treat body conditionals as opaque through their matching `\fi` instead of refusing them. Refuse a stray `\fi`, `\else` or `\or` that comes from an aliased conditional.
4. **Token extents:** a prose argument's braces belong to the enclosing region; `\begin`/`\end` and their arguments are opaque; define a quote's token extent; add `proof_estart` to `_find_and_order` for the range-close rule.
5. **See/See also:** emit them through a printable-set helper shared with `format`, with its "left out: no placed tags" lines and word-by-word target sort. State that sort, range style and length cuts belong to the press's `.ist`.
6. **Base:** Increments 1–3 are draft PRs #412, #414 and #415, and the parent spec on main still lists `embedded` (Word XE included) in Increment 3. Land the parent-spec pointer edits and list the helper symbols this scheme depends on.
7. **T-TeX:** give it fixed expected `.ind` lines and commit the recorded run as a golden fixture. Keep `see_target_unquotable` until a later amendment changes it.
8. **P3s:** escape `<` and `>` (or narrow the OT1 rationale to T1); make `--source` an append option that `line` and `ebook` refuse to repeat; refuse a redefinition of an allowlisted prose environment or `\item`.

## Review record

2026-10-30, fleet `/spec-review` (seven lenses): NEEDS-REWORK (3 P1, 9 P2). The owner parked it as a design note; the P1s are folded in and the accepted cuts applied (layered overwrite checks, the verbatim-environment list, the rerun test and the tag-order rule, "design of record"). Razor-declined: report provenance hashes, run-time range and re-lex gates, a missing-`\makeindex` warning, and babel shorthand detection. Summary on PR #413.
