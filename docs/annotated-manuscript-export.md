# Annotated-Manuscript Export — Obsidian (native footnotes, no plugin)

**Status:** Proposed (unbuilt). Spec-reviewed 2026-06-17 (web-verified; build-ready after the fixes below were folded in). Obsidian-only this increment ("footnotes, no plugin"; "Obsidian only for now"). Depends on the gated **annotation manifest** + the crosslinked letter (deliverable Increments 1–3, in `main`) and the [producer](annotated-manuscript-producer.md) that generates them (#104/#105).

## The framing that unlocks it

The **canonical, gated artifact is the annotation manifest** (`finding_id → anchor → comment`, sha-bound to the snapshot). The CriticMarkup "annotated copy" is *one projection* of it. So is this Obsidian export — a sibling render `manifest + snapshot → Obsidian-native Markdown`. We do **not** change the base format; we add a projection.

**Why footnotes, not CriticMarkup, for Obsidian.** Obsidian does **not** render CriticMarkup `{>> … <<}` natively — vanilla Obsidian shows the literal braces as inline text clutter; the comment-bubble rendering exists only via a community plugin (Commentator / CodyBontecou). The requirement is **native, no plugin**. Obsidian's native primitive closest to an anchored margin comment is the **footnote**: `text[^id]` renders a clickable superscript whose definition shows on hover and collects in the core **Footnotes View** pane. Anchor links (`[[note#^block]]`, `[[note#Heading]]`) are *also* native — they were never the obstacle; the comment rendering was. So this export translates the manifest's comments into footnotes and its cross-references into wikilinks — all native. **Canonical view is Reading view** (Obsidian's Live Preview renders footnote superscripts only partially — a cosmetic Live-Preview limitation, not a Reading-view one).

## Obsidian facts this design relies on (web-verified by spec-review, 2026-06-17)

- **Footnote labels accept `[^F-RR-01]`** (hyphens + uppercase): Obsidian's `markdown-it-footnote` parser scans to the closing `]` via `parseLinkLabel`, with no `[\w-]`-only restriction. Labels are matched **case-insensitively** — harmless here because both the ref and definition are keyed off the *same verbatim* `finding_id`, and A1 already guarantees `finding_id` uniqueness. The label **is** the verbatim `finding_id`.
- **A mid-line `[^id]` ref renders** as a clickable superscript in Reading view regardless of position; **co-located refs must be space-separated** (`[^a] [^b]`) to avoid a Live-Preview editor display quirk.
- **Footnote definitions may sit anywhere; a contiguous trailing block is valid** — Reading view always collects them at the foot.
- **A wikilink inside a footnote *definition* renders clickable** (`[^id]: … [[Note#^id]]`). This is the decisive contrast with the prior CriticMarkup design (wikilinks inside `{>> <<}` don't render). *Inline* footnotes (`^[…]`) break wikilinks — so we use **reference-style** footnotes only.

## The transform (`manifest + snapshot → Obsidian Markdown`)

A new `scripts/annotation_export.py obsidian <run_folder>` (mirrored) reads the gated manifest + snapshot + crosslinked letter and writes Obsidian-flavored copies into an `obsidian/` subfolder (leaving the gated artifacts pristine).

**1. Annotated copy → footnoted Markdown.** For each manifest annotation, insert a footnote reference **`[^<finding_id>]`** at the anchor's locus in the snapshot (the same descending-offset splice the CriticMarkup renderer uses, so insertions never perturb each other; co-located refs get a separating space), and append one footnote **definition** per annotation in a contiguous trailing block. **The definition body carries the manifest comment VERBATIM** (the exact `comment_for(finding)` string — `[<severity> · <id>] <mechanism> — fix class: <fix_class>. (See letter §<id>.)`), followed by a single space and a wikilink to the letter entry — **no bold-wrapping, no paraphrase, no re-projection**:

```
[^F-RR-01]: [Must-Fix · F-RR-01] the middle third's pacing collapses — three days pass in two sentences at Chapter 9, reading as a continuity break — fix class: restore a transit beat or an explicit time marker. (See letter §F-RR-01.) [[Example_Crosslinked_Letter_2026-01-01#^F-RR-01|→ letter §F-RR-01]]
```

Ref placement by anchor kind: **quote** → at the quote's end offset (mid-line, fine in Reading view); **chapter/section** → end of the heading line, space-separated (the heading text stays a valid ATX heading); **line-range** → end of the line; **document** → no inline ref, a single file-level footnote referenced from a marker appended after the note title.

**2. Letter → block-id targets + back-links.** Each `<!-- finding: F-… -->` marker line in the crosslinked letter gets an Obsidian **block id** `^F-…` appended (so the footnote's `[[…#^F-…]]` resolves). The crosslinked letter's existing CriticMarkup back-link spans (`{>>→ marked-up copy: F-… @ kind:value<<}`, which Obsidian would show as literal clutter) are **converted** to a wikilink to the annotated copy: a **chapter/section** anchor → `[[<copy>#<heading text>]]` where the `#fragment` is the **resolved snapshot heading text** (e.g. `Chapter 9`) — **never** the manifest's `Ch 9` token; a **line-range/quote/document** anchor → a file-level `[[<copy>]]` link (W1). The letter is itself treated as a "second snapshot": its own reverse transform (strip the appended ` ^F-…` block ids + the converted wikilinks) reproduces the editorial-letter prose.

Nothing else changes: prose, comment text, finding ids, anchor values — all carried verbatim. The export adds only footnote refs/definitions and `[[…]]`/`^id` tokens whose payloads are finding ids + the verbatim manifest comment.

## Firewall

A pure projection of the gated manifest — invents nothing. Every footnote definition carries the manifest's **verbatim** comment; every `[^id]`/`^id`/`[[…]]` token's payload is a finding id or anchor value copied from the manifest. The reverse transform reproduces the snapshot **byte-for-byte** — the A2 discipline, two-sided and manifest-keyed (see O1). The model never authors or "updates" a note to fit the prose; it relocates the unchanged comment into a footnote or reports it can't.

## The `obsidian-export` validator (proposed)

`validate.sh obsidian-export <run_folder>` → delegates to `scripts/annotation_export.py`; degrades to advisory `WARN` without `python3`. Gates by identity (the A/X discipline):

| ID | Severity | Rule |
|---|---|---|
| **O1 — round-trip to source** | ERROR | **Manifest-keyed, two-sided.** *Precondition (hard-fail before export, mirroring `render`/A2):* neither the snapshot **nor** any projected definition body (the verbatim comment + the wikilink display text) contains `[^`, and no snapshot line matches a footnote-definition shape `^\[\^…\]:`. *Round-trip:* deleting exactly the literal `[^<finding_id>]` refs (one per manifest annotation — the `_CM_SPAN_RE` analog keyed to the **manifest id set**, never a `\[\^…\]` wildcard) and the contiguous trailing block of `[^<finding_id>]:` definition lines reproduces the gated snapshot **byte-for-byte**. |
| **O2 — footnote resolution** | ERROR | Every `[^id]` reference has **exactly one** matching definition and vice versa (no orphan ref, no orphan/authored definition); the ref/definition id set **equals** the manifest's annotation `finding_id` set (the A4 forward+inverse multiset discipline, on footnotes — an un-manifested footnote is the A4-inverse violation). |
| **O3 — comment fidelity** | ERROR | Each footnote definition contains its manifest `comment` (`comment_for`) **verbatim, as a contiguous substring** (relocate, never re-author — the A5 analog). The only non-manifest text in a definition is the trailing letter wikilink, whose payload is the finding id + a fixed display string. |
| **O4 — link resolution** | ERROR | Every footnote `[[<letter>#^id]]` wikilink targets a `^id` block id present in the exported letter (forward nav — the X3 analog); every converted letter→copy `[[<copy>#<heading>]]` back-link targets a **real ATX heading in the exported copy** (matched by the heading's actual text, accounting for any appended footnote ref). A back-link whose `#fragment` doesn't resolve fails — this is the gate that catches a manifest-token-vs-heading-text mismatch at build time. |
| **W1 — file-level back-link** | WARN | A finding whose manuscript anchor is `line-range`/`quote`/`document` (no addressable heading) gets a file-level letter→copy link — surfaced, not an error. Forward nav (copy footnote → letter `^id` block) is the only fully-bidirectional rung; footnote refs are not link targets, so reverse nav to an exact inline locus is honestly file/heading-level. |

The canonical `example-annotated-manuscript/` fixture gains its Obsidian pair under `obsidian/`, and `--check-all` runs `annotation_export.py obsidian` on a **temp copy** then gates it (temp-stage-then-move, the producer precedent), asserting the fresh export is byte-identical to the committed Obsidian fixture. **The Obsidian copy is built from the *snapshot*** (clean ATX headings: `# Chapter 9`), **not** the CriticMarkup annotated copy (whose headings sit mid-line after `{>> <<}` spans) — so O4's heading back-links resolve.

## Increment boundary

**In (Increment 1):** `scripts/annotation_export.py obsidian` (mirrored; `--self-test`) + `validate.sh obsidian-export` (O1–O4 + W1), reusing the manifest parser + `comment_for` + the descending-offset splice; the Obsidian annotated copy + converted letter; the canonical Obsidian fixture + `--check-all` gate. **Validators +1 → 46** — lockstep bump in **both** `scripts/validate.sh` and `plugins/apodictic/scripts/validate.sh` (check-mirror byte-identity) of the **four** sites: (1) `AGG_VALIDATORS`, (2) the `Commands:` usage string, (3) the `--check-all` description, plus (4) the new `obsidian-export)` dispatch arm. **Out:** read-only HTML / Google Docs / DOCX-comments / PDF export (later, demand-driven); the optional Tufte-**CSS-snippet** sidenote styling (documented, not shipped — a theme tweak, still no plugin); the Commentator-plugin path (documented as the alternative that also bridges to Word/GDocs, not built); any comment re-authoring.

## Why CriticMarkup stays canonical (the strategic note)

CriticMarkup is **not** the publishing-industry standard — Word Track Changes + Comments is (Google Docs suggesting mode; PDF for proofing). But CriticMarkup is the right *internal* representation: the firewall's no-mutation proof (A2) is trivial on plain text and painful on DOCX/PDF binaries, and CriticMarkup is the plain-text bridge the Commentator plugin round-trips to Word/Google-Docs comment mode. So the manifest stays canonical, CriticMarkup stays its first render, and the professional formats (DOCX-comments, GDocs, PDF) are future projections — not a new base.
