# Annotated-Manuscript Export — Obsidian (native footnotes, no plugin)

**Status:** **Increment 1 Built (2026-06-17)** — the annotated copy → native-footnote Obsidian projection; Increment 2 (the letter cross-links) deferred. Shipped surface: `scripts/annotation_export.py` (`obsidian` generate + `obsidian-export` validate, `--self-test`), the `validate.sh obsidian-export <run_folder>` validator (O1–O3; +1 → 46 validators, mirrored), and the canonical `example-annotated-manuscript/obsidian/` fixture wired into `--check-all` (byte-identical to a fresh export). Web-verified spec-review 2026-06-17. Obsidian-only ("footnotes, no plugin"; "Obsidian only for now"). Depends on the gated **annotation manifest** + snapshot (deliverable Increments 1–3, in `main`) and the [producer](annotated-manuscript-producer.md) that generates them (#104/#105).
<!-- built-when: scripts/annotation_export.py -->

## The framing that unlocks it

The **canonical, gated artifact is the annotation manifest** (`finding_id → anchor → comment`, sha-bound to the snapshot). The CriticMarkup "annotated copy" is *one projection* of it. So is this Obsidian export — a sibling render `manifest + snapshot → Obsidian-native Markdown`. We do **not** change the base format; we add a projection.

**Why footnotes, not CriticMarkup, for Obsidian.** Obsidian does **not** render CriticMarkup `{>> … <<}` natively — vanilla Obsidian shows the literal braces as inline text clutter; the comment-bubble rendering exists only via a community plugin (Commentator / CodyBontecou). The requirement is **native, no plugin**. Obsidian's native primitive closest to an anchored margin comment is the **footnote**: `text[^id]` renders a clickable superscript whose definition shows on hover and collects in the core **Footnotes View** pane. Anchor links (`[[note#^block]]`, `[[note#Heading]]`) are *also* native — they were never the obstacle; the comment rendering was. So this export translates the manifest's comments into footnotes and its cross-references into wikilinks — all native. **Canonical view is Reading view** (Obsidian's Live Preview renders footnote superscripts only partially — a cosmetic Live-Preview limitation, not a Reading-view one).

## Obsidian facts this design relies on (web-verified by spec-review, 2026-06-17)

- **Footnote labels accept `[^F-RR-01]`** (hyphens + uppercase): Obsidian's `markdown-it-footnote` parser scans to the closing `]` via `parseLinkLabel`, with no `[\w-]`-only restriction. Labels are matched **case-insensitively** — harmless here because both the ref and definition are keyed off the *same verbatim* `finding_id`, and A1 already guarantees `finding_id` uniqueness. The label **is** the verbatim `finding_id`.
- **A mid-line `[^id]` ref renders** as a clickable superscript in Reading view regardless of position; **co-located refs must be space-separated** (`[^a] [^b]`) to avoid a Live-Preview editor display quirk.
- **Footnote definitions may sit anywhere; a contiguous trailing block is valid** — Reading view always collects them at the foot.
- **A wikilink inside a footnote *definition* renders clickable** (`[^id]: … [[Note#^id]]`). This is the decisive contrast with the prior CriticMarkup design (wikilinks inside `{>> <<}` don't render). *Inline* footnotes (`^[…]`) break wikilinks — so we use **reference-style** footnotes only.

## The transform (`manifest + snapshot → Obsidian Markdown`)

A new `scripts/annotation_export.py obsidian <run_folder>` (mirrored) reads the gated manifest + snapshot and writes an Obsidian-flavored annotated copy into an `obsidian/` subfolder (leaving the gated artifacts pristine).

**Annotated copy → footnoted Markdown.** For each manifest annotation, insert a footnote reference **`[^<finding_id>]`** at the anchor's locus in the snapshot (the same descending-offset splice the CriticMarkup renderer uses, so insertions never perturb each other; co-located refs get a separating space), and append one footnote **definition** per annotation in a contiguous trailing block. **The definition body is the manifest comment VERBATIM** (the exact `comment_for(finding)` string — `[<severity> · <id>] <mechanism> — fix class: <fix_class>. (See letter §<id>.)`) — **no bold-wrapping, no paraphrase, no re-projection**:

```
[^F-RR-01]: [Must-Fix · F-RR-01] the middle third's pacing collapses — three days pass in two sentences at Chapter 9, reading as a continuity break — fix class: restore a transit beat or an explicit time marker. (See letter §F-RR-01.)
```

The comment **already carries the textual pointer `(See letter §F-RR-01.)`** — so the reader has the cross-reference even before the *clickable* letter wikilink lands (Export Increment 2). Ref placement by anchor kind: **quote** → at the quote's end offset (mid-line, fine in Reading view); **chapter/section** → end of the heading line, space-separated (the heading text stays a valid ATX heading); **line-range** → end of the line; **document** → end of the first line (file-level; no offset-0 prepend, which would break a leading `#` heading).

Nothing else changes: prose, comment text, finding ids — all carried verbatim. The export adds only footnote refs/definitions whose payloads are finding ids + the verbatim manifest comment.

## Firewall

A pure projection of the gated manifest — invents nothing. Every footnote definition carries the manifest's **verbatim** comment; every `[^id]`/`^id`/`[[…]]` token's payload is a finding id or anchor value copied from the manifest. The reverse transform reproduces the snapshot **byte-for-byte** — the A2 discipline, two-sided and manifest-keyed (see O1). The model never authors or "updates" a note to fit the prose; it relocates the unchanged comment into a footnote or reports it can't.

## The `obsidian-export` validator (proposed)

`validate.sh obsidian-export <run_folder>` → delegates to `scripts/annotation_export.py`; degrades to advisory `WARN` without `python3`. Gates by identity (the A/X discipline):

| ID | Severity | Rule |
|---|---|---|
| **O1 — round-trip to source** | ERROR | **Manifest-keyed, two-sided.** *Precondition (hard-fail before export, mirroring `render`/A2):* neither the snapshot **nor** any projected definition body (the verbatim comment) contains `[^`, and no snapshot line matches a footnote-definition shape `^\[\^…\]:`. *Round-trip:* deleting exactly the literal `[^<finding_id>]` refs (one per manifest annotation — the `_CM_SPAN_RE` analog keyed to the **manifest id set**, never a `\[\^…\]` wildcard) and the contiguous trailing block of `[^<finding_id>]:` definition lines reproduces the gated snapshot **byte-for-byte**. |
| **O2 — footnote resolution** | ERROR | Every `[^id]` reference has **exactly one** matching definition and vice versa (no orphan ref, no orphan/authored definition); the ref/definition id set **equals** the manifest's annotation `finding_id` set (the A4 forward+inverse multiset discipline, on footnotes — an un-manifested footnote is the A4-inverse violation). |
| **O3 — comment fidelity** | ERROR | Each footnote definition body **equals** its manifest `comment` (`comment_for`) byte-for-byte (relocate, never re-author — the A5 analog). |

The canonical `example-annotated-manuscript/` fixture gains its Obsidian copy under `obsidian/`, and `--check-all` runs `annotation_export.py obsidian` on a **temp copy** then gates it (temp-stage-then-move, the producer precedent), asserting the fresh export is byte-identical to the committed Obsidian fixture. **The Obsidian copy is built from the *snapshot*** (clean ATX headings: `# Chapter 9`), **not** the CriticMarkup annotated copy (whose headings sit mid-line after `{>> <<}` spans).

## Increment boundary

**In (Increment 1 — the annotated copy):** `scripts/annotation_export.py obsidian` (mirrored; `--self-test`) + `validate.sh obsidian-export` (O1–O3), reusing the manifest parser + the descending-offset splice; the Obsidian annotated copy (footnotes whose definitions carry the verbatim comment); the canonical Obsidian fixture + `--check-all` gate. **Validators +1 → 46** — lockstep bump in **both** `scripts/validate.sh` and `plugins/apodictic/scripts/validate.sh` (check-mirror byte-identity) of the **four** sites: (1) `AGG_VALIDATORS`, (2) the `Commands:` usage string, (3) the `--check-all` description, plus (4) the new `obsidian-export)` dispatch arm.

**Out — Export Increment 2 (the letter cross-links, deferred):** the Obsidian *letter* (each `<!-- finding: F-… -->` marker gets a `^F-…` block id; the crosslinked letter's CriticMarkup back-link spans convert to `[[<copy>#<heading>]]` wikilinks using the **resolved snapshot heading text**, never the manifest `Ch 9` token; the copy's footnote definitions gain a `[[<letter>#^id]]` forward wikilink) + the O4 link-resolution / W1 file-level-back-link gate. Deferred because the spec-review's two trickiest findings (heading-text back-links, CriticMarkup-span conversion) live entirely on the letter side; the copy alone delivers the native marked-up manuscript the maintainer asked for. **Out — later still:** read-only HTML / Google Docs / DOCX-comments / PDF (demand-driven); the optional Tufte-**CSS-snippet** sidenote styling (a theme tweak, no plugin); the Commentator-plugin path (the alternative that bridges to Word/GDocs); any comment re-authoring.

## Why CriticMarkup stays canonical (the strategic note)

CriticMarkup is **not** the publishing-industry standard — Word Track Changes + Comments is (Google Docs suggesting mode; PDF for proofing). But CriticMarkup is the right *internal* representation: the firewall's no-mutation proof (A2) is trivial on plain text and painful on DOCX/PDF binaries, and CriticMarkup is the plain-text bridge the Commentator plugin round-trips to Word/Google-Docs comment mode. So the manifest stays canonical, CriticMarkup stays its first render, and the professional formats (DOCX-comments, GDocs, PDF) are future projections — not a new base.
