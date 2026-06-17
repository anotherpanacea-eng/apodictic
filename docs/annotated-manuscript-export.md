# Annotated-Manuscript Export — render targets for the deliverable

**Status:** Proposed (unbuilt). Increment 1 = **Obsidian**.

The [Annotated-Manuscript deliverable](annotated-manuscript.md) + its [producer](annotated-manuscript-producer.md) now generate, in a real run, two gated artifacts: the **annotated copy** (the snapshot with inline CriticMarkup `{>> … <<}` margin comments) and the **crosslinked letter** (the editorial letter with `<!-- finding: F-… -->` markers + `{>>→ marked-up copy: F-… @ kind:value<<}` back-link spans). Both are plain Markdown. This spec adds **export targets** that render the deliverable where writers actually work — **render-only, model-never-authors**: an export is a *pure projection* of the already-gated artifacts; it adds navigation/markup syntax derived from finding IDs + anchors that are already in the gated manifest, and **invents no content**.

**Export sub-stack (ordered — maintainer 2026-06-17):** **(1) Obsidian** (this increment — CriticMarkup + wikilinks render natively, so it's the lightest lift), then **(2) read-only HTML**, then **(3) Google Docs**. **DOCX is deferred to the horizon** (built on demand). Each target is an independent increment over the same gated source; none changes the deliverable's own gates.

## Why Obsidian is first / what it actually adds

Obsidian already renders the deliverable's two mechanics natively: the **CriticMarkup** `{>> … <<}` margin comments (via Obsidian's CriticMarkup support), and **wikilinks** `[[…]]` / **block references** `[[note#^id]]` / **heading links** `[[note#Heading]]`. The annotated copy is therefore *already* Obsidian-renderable as comments. What's missing is **navigation**: today the cross-references are **textual** — a margin note ends `(See letter §F-RR-01.)` and a letter entry carries `{>>→ marked-up copy: F-RR-01 @ chapter:Ch 9<<}` — neither is clickable. The Obsidian export turns those textual references into **clickable wikilinks**, so a writer clicks from a margin note to its letter entry and from a letter entry back to the marked-up passage. That is the whole increment: **navigation, not content.**

## Increment 1 — Obsidian export

### 1a. The generator

A new `scripts/annotation_export.py obsidian <run_folder>` (mirrored to root `scripts/`, like the other generators) reads the **gated** manifest + annotated copy + crosslinked letter and writes Obsidian-flavored copies into an `obsidian/` subfolder of the run folder (leaving the canonical gated artifacts **pristine** — the export is a derived view, not a mutation):

- `obsidian/<Project>_Annotated_Manuscript_<run>.md`
- `obsidian/<Project>_Crosslinked_Letter_<run>.md`

Writing to a subfolder (a) keeps the gated source immutable for re-gates/re-exports, and (b) gives Obsidian a self-contained pair to open as a mini-vault.

### 1b. The navigation transform (the only change the export makes)

Two link directions, both keyed on the finding ID, both derived from tokens already in the gated artifacts:

1. **Letter findings become link targets.** In the Obsidian letter, each `<!-- finding: F-id -->` marker gets an Obsidian **block identifier** appended to its line — `^F-id` (e.g. `^F-RR-01`). This makes every finding addressable as `[[<letter-note>#^F-id]]`. *(Open question Q1 — block-ID charset/case; see §1d.)*
2. **Margin note → letter (forward nav).** In the Obsidian annotated copy, the margin comment's textual `(See letter §F-id.)` becomes a wikilink: `(See [[<Letter note>#^F-id|letter §F-id]].)` — clickable to the letter entry. *(Open question Q2 — does Obsidian render a wikilink **inside** a `{>> … <<}` CriticMarkup comment as clickable? If not, §1d gives the fallback.)*
3. **Letter back-link → marked-up copy (reverse nav).** In the Obsidian letter, the back-link span `{>>→ marked-up copy: F-id @ kind:value<<}` becomes a wikilink into the annotated copy. For a `chapter`/`section` anchor this is a **heading link** `[[<Annotated note>#Ch 9]]` (the annotated copy already carries the chapter/section as an ATX heading); for `line-range`/`quote`/`document` anchors — which have no stable heading target — it links to the **note top** `[[<Annotated note>]]` with the kind:value retained as visible text (honest: navigates to the file, not a phantom block). *(Open question Q3 — best addressable target for inline anchors.)*

Nothing else changes: the prose, the CriticMarkup comment text, the severities, the finding IDs, the anchors — all carried through **verbatim**. The export adds only `[[…]]` / `^id` tokens whose contents are finding IDs and anchor values copied from the gated manifest.

### 1c. Firewall + the gate (`obsidian-export`, mirrored)

The export is firewall-safe because it is a **mechanical projection**: every added token is a wikilink/block-ID whose payload is a finding ID or anchor value drawn verbatim from the gated manifest — never authored prose. A new `obsidian-export` validator gates this **by identity**, the same discipline as A1–A6 / X1–X4:

- **E1 — round-trip to source.** Stripping the export's *additions* (the appended ` ^F-id` block IDs; the wikilink wrappers, reduced to their visible text) reproduces the gated annotated copy / crosslinked letter **byte-for-byte**. This proves the export mutated no prose and no CriticMarkup — it only decorated.
- **E2 — link resolution (no dangling links).** Every `[[note#^F-id]]` target resolves: the block ID `^F-id` exists in the named Obsidian letter; every heading link `[[note#Heading]]` resolves to an ATX heading in the named annotated copy. No wikilink points at a missing target.
- **E3 — projection completeness + no extras.** The set of forward links equals the set of manifest findings with a `(See letter §…)` reference; the set of letter block IDs equals the set of `<!-- finding: F-… -->` markers; no link/block-ID exists that isn't backed by a manifest finding (the A4/X3 "no un-manifested span" discipline, applied to links).
- **E4 — anchor fidelity.** Each reverse-nav heading link names the **same** chapter/section the manifest anchor records (no drift, mirroring X2).
- **W1 (advisory)** — an inline-anchored finding (`line-range`/`quote`/`document`) that necessarily degrades to a file-top link, surfaced as a coverage note, not an error.

The canonical `example-annotated-manuscript/` fixture gains its Obsidian pair under `obsidian/`, and `--check-all` runs `annotation_export.py obsidian` on a **temp copy** then gates it (the temp-stage-then-move discipline from the producer), asserting the fresh export is byte-identical to the committed Obsidian fixture.

### 1d. Open questions for spec-review (resolve via Obsidian's actual rendering rules)

- **Q1 — block-ID validity.** Are `^F-RR-01`-style block IDs valid in Obsidian (hyphens; uppercase)? Obsidian's documented rule is "letters, numbers, dashes." Confirm; if case/charset is a problem, define a normalized block ID (e.g. lowercased `^f-rr-01`) and key the wikilinks to it.
- **Q2 — wikilinks inside CriticMarkup.** Does Obsidian render a `[[…]]` wikilink that sits **inside** a `{>> … <<}` CriticMarkup comment as a clickable link? If the CriticMarkup renderer swallows it, the fallback is to place the forward wikilink **immediately after** the comment span (still on the same line, outside the sigils) rather than inside it — decide which, and reflect it in E1's strip transform.
- **Q3 — inline-anchor targets.** Is there a better Obsidian-addressable target for `line-range`/`quote` anchors than the file top (e.g. injecting a block ID at the anchored line in the annotated copy)? Weigh the navigation gain against the added round-trip-strip complexity and the risk of mutating the annotated prose.

## Increment boundary

**In (Increment 1):** the `annotation_export.py obsidian` generator (mirrored) + the `obsidian-export` validator (E1–E4 + W1) + the canonical Obsidian fixture + the `--check-all` temp-copy export-and-gate chain. **Out:** read-only HTML export (Increment 2); Google Docs export (Increment 3); DOCX (horizon); any change to the deliverable's own A/X gates; any content the model authors (the export only decorates with links derived from the manifest).

**Dependencies.** Consumes the gated annotated copy + crosslinked letter + manifest (deliverable Increments 1–3, in `main`) and the producer that generates them (Producer Increment 1, PR #104). Stacks on the producer branches.
