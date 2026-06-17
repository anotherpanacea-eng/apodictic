# Annotated-Manuscript Export — Obsidian (native footnotes, no plugin)

**Status:** Proposed (unbuilt). Spec for review. Obsidian-only this increment (maintainer 2026-06-17: "footnotes, no plugin"; "Obsidian only for now"). Depends on the gated **annotation manifest** + the crosslinked letter (deliverable Increments 1–3, in `main`) and the [producer](annotated-manuscript-producer.md) that generates them (#104/#105).

## The framing that unlocks it

The **canonical, gated artifact is the annotation manifest** (`finding_id → anchor → comment`, sha-bound to the snapshot). The CriticMarkup "annotated copy" is *one projection* of it. So is this Obsidian export — a sibling render `manifest + snapshot → Obsidian-native Markdown`. We do **not** change the base format; we add a projection.

**Why footnotes, not CriticMarkup, for Obsidian.** Obsidian does **not** render CriticMarkup `{>> … <<}` natively — vanilla Obsidian shows the literal braces as inline text clutter; the comment-bubble rendering exists only via a community plugin (Commentator / CodyBontecou). The requirement is **native, no plugin**. Obsidian's native primitive closest to an anchored margin comment is the **footnote**: `text[^id]` renders a clickable superscript whose definition shows on hover and collects in the core **Footnotes View** pane. Anchor links (`[[note#^block]]`, `[[note#Heading]]`) are *also* native — they were never the obstacle; the comment rendering was. So this export translates the manifest's comments into footnotes and its cross-references into wikilinks — all native.

## The transform (`manifest + snapshot → Obsidian Markdown`)

A new `scripts/annotation_export.py obsidian <run_folder>` (mirrored) reads the gated manifest + snapshot + crosslinked letter and writes Obsidian-flavored copies into an `obsidian/` subfolder (leaving the gated artifacts pristine):

1. **Annotated copy → footnoted Markdown.** For each manifest annotation, insert a footnote reference **`[^<finding_id>]`** at the anchor's locus in the snapshot (the same descending-offset splice the CriticMarkup renderer uses, so insertions never perturb each other), and append one footnote **definition** per annotation in a trailing block:

   ```
   [^F-RR-01]: **[Must-Fix]** three days collapse into one paragraph, a continuity seam — fix class: restore a transit beat. [[<Letter note>#^F-RR-01|→ letter §F-RR-01]]
   ```

   The definition body is the **verbatim finding-field projection** (the same fields the CriticMarkup comment carries, minus the `{>> <<}` sigils) plus a wikilink to the letter entry. The `[^id]` ref is placed: quote → at the quote's end offset; chapter/section → end of the heading line; line-range → end of the line; **document → a single file-level note** appended after the title (no inline ref, since there's no locus).

2. **Letter → block-id targets + back-links.** Each `<!-- finding: F-… -->` marker line in the crosslinked letter gets an Obsidian **block id** `^F-…` appended (so the footnote's `[[…#^F-…]]` resolves), and the existing back-link is rendered as a wikilink to the annotated copy (heading-anchored where the anchor is a chapter/section; file-level otherwise — reverse-nav to an exact inline locus isn't addressable in Obsidian, and we don't fake it).

Nothing else changes: prose, comment text, finding ids, anchor values — all carried verbatim. The export adds only footnote refs/definitions and `[[…]]`/`^id` tokens whose payloads are finding ids + field projections drawn from the gated manifest.

## Firewall

A pure projection of the gated manifest — invents nothing. Every footnote definition is the manifest's verbatim comment projection; every `[^id]`/`^id`/`[[…]]` token's payload is a finding id or anchor value copied from the manifest. The reverse transform (delete every `[^id]` reference + the trailing footnote-definition block) reproduces the snapshot **byte-for-byte** — the same no-mutation discipline as A2, on a different decoration. The model never authors or "updates" a note to fit the prose.

## The `obsidian-export` validator (proposed)

`validate.sh obsidian-export <run_folder>` → delegates to `scripts/annotation_export.py`; degrades to advisory `WARN` without `python3`. Gates by identity:

| ID | Severity | Rule |
|---|---|---|
| **O1 — round-trip to source** | ERROR | Deleting every `[^id]` reference + the footnote-definition block from the exported copy reproduces the gated snapshot **byte-for-byte** (no prose mutation — the A2 analog). Two-sided precondition: the snapshot contains no pre-existing `[^…]` footnote ref. |
| **O2 — footnote resolution** | ERROR | Every `[^id]` reference has **exactly one** matching definition and vice versa (no orphan ref, no orphan definition); the id set equals the manifest's annotation `finding_id` set (the A4/X3 multiset discipline, on footnotes). |
| **O3 — comment fidelity** | ERROR | Each footnote definition's projected body carries the **verbatim** manifest comment (relocate, never re-author). |
| **O4 — link resolution** | ERROR | Every footnote `[[<letter>#^id]]` wikilink targets a block id present in the exported letter; every exported-letter back-link `[[<copy>#Heading]]` targets a real ATX heading in the exported copy. No dangling wikilink. |
| **W1 — file-level back-link** | WARN | A finding whose manuscript anchor is `line-range`/`quote`/`document` (no addressable heading) gets a file-level letter→copy link — surfaced, not an error. |

The canonical `example-annotated-manuscript/` fixture gains its Obsidian pair under `obsidian/`, and `--check-all` runs `annotation_export.py obsidian` on a **temp copy** then gates it (temp-stage-then-move, the producer precedent), asserting the fresh export is byte-identical to the committed Obsidian fixture.

## Open questions for spec-review (verify against Obsidian's actual rules)

- **Q1 — footnote-label charset.** Does Obsidian accept a footnote label containing hyphens/uppercase, i.e. `[^F-RR-01]`? (Markdown footnote labels are typically `[^\w-]+`; confirm Obsidian's parser, and whether labels are case-sensitive. If not, define a normalized label keyed to the finding id.)
- **Q2 — inline ref placement.** Does a `[^id]` ref placed *mid-line* at a quote's end offset render cleanly, or should every ref go at end-of-line (simpler, but less precisely adjacent to the quoted span)? Weigh adjacency vs. the O1 round-trip simplicity.
- **Q3 — definition-block round-trip.** Is "delete the trailing footnote-definition block" an unambiguous reverse transform (the block is the contiguous run of `^\[\^…\]:` lines at the end)? Confirm no legitimate snapshot line can collide with a footnote-definition line.
- **Q4 — reverse nav.** Confirm there's no native way to link from the letter to an *exact inline locus* in the copy (footnote refs aren't link targets), so file/heading-level reverse-nav is the honest ceiling — and that forward nav (copy footnote → letter block id) is the primary, fully-native direction.
- **Q5 — fixture.** Confirm the Obsidian pair is constructible from the existing `example-annotated-manuscript/` manifest + snapshot + crosslinked letter, and gate-valid under O1–O4.

## Increment boundary

**In (Increment 1):** `scripts/annotation_export.py obsidian` (mirrored; `--self-test`) + `validate.sh obsidian-export` (O1–O4 + W1), reusing the manifest parser + the descending-offset splice; the Obsidian annotated copy + letter; the canonical Obsidian fixture + `--check-all` gate; validators +1 → 46 (lockstep bump of `AGG_VALIDATORS` + usage + `--check-all` description in both mirror copies, plus the dispatch arm). **Out:** read-only HTML / Google Docs / DOCX-comments / PDF export (later, demand-driven); the optional Tufte-**CSS-snippet** sidenote styling (documented, not shipped — it's a theme tweak, still no plugin); the Commentator-plugin path (documented as the alternative that also bridges to Word/GDocs, not built); any comment re-authoring.

## Why CriticMarkup stays canonical (the strategic note)

CriticMarkup is **not** the publishing-industry standard — Word Track Changes + Comments is (Google Docs suggesting mode; PDF for proofing). But CriticMarkup is the right *internal* representation: the firewall's no-mutation proof (A2) is trivial on plain text and painful on DOCX/PDF binaries, and CriticMarkup is the plain-text bridge the Commentator plugin round-trips to Word/Google-Docs comment mode. So the manifest stays canonical, CriticMarkup stays its first render, and the professional formats (DOCX-comments, GDocs, PDF) are future projections — not a new base.
