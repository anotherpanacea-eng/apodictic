# Annotated-Manuscript Deliverable — reference

The third leg of the trade developmental-edit deliverable set: the manuscript itself, marked up.
Where the editorial letter *references* loci ("Chapter 9 collapses three days…"), the annotated copy
puts each finding **next to the prose that triggered it**, so the writer revises at the line. This is
an **export/anchor** capability — it invents nothing; every margin note is a verbatim projection of a
finding the passes already produced. Comments only — never tracked changes, never suggested prose
(that is content invention, the Firewall's red line).

Spec + rule detail: [`docs/annotated-manuscript.md`](../../../../docs/annotated-manuscript.md).

## The three artifacts (the manuscript is never mutated in place)

1. **Snapshot** — `[Project]_Manuscript_Snapshot_[runlabel].md`: a frozen copy of the manuscript, line
   endings forced to LF and a trailing newline ensured, **nothing else**. The snapshot *is* the line
   index; all anchoring and the no-mutation proof are against it, never the author's live file.
2. **Annotation manifest** — `[Project]_Annotation_Manifest_[runlabel].md`: a single
   `apodictic.annotation.v1` block binding the snapshot (`snapshot_path` / `snapshot_sha256` /
   `snapshot_line_count`) and listing one `annotations[]` entry per finding `{finding_id, anchor, comment}`.
3. **Annotated copy** — `[Project]_Annotated_Manuscript_[runlabel].md`: the snapshot with CriticMarkup
   `{>> … <<}` comment spans injected. Deleting every span reproduces the snapshot **byte-for-byte**.

## How to produce it

```
scripts/annotation_manifest.py build <run_folder>     # resolves anchors + projects comments + renders
scripts/validate.sh annotated-manuscript <run_folder> # gates A1–A5 + W1
```

`build` reads the snapshot, the Findings Ledger, and (optionally) `Timeline.md`, resolves each finding's
anchor, projects its comment, and writes the manifest + annotated copy. It is the mechanical, firewall-safe
path: the model never authors a margin comment. `render <manifest> <snapshot>` re-renders the copy from a
manifest.

## The anchor ladder (per `evidence_refs` token; finest rung any *manuscript-scoped* token supports)

| Rung | When |
|---|---|
| `line-range` | a token that **exactly equals** a `Timeline` Section-1 scene-id with an in-bounds line range |
| `section` | a non-chapter manuscript heading name matched **uniquely** in the snapshot |
| `chapter` | a chapter token (`Chapter N` / `Ch. N` / `Ch.N` / `Ch N`, via the shared `chapter_token`) with a **unique** matching heading; a page suffix (`p.40`) is ignored |
| `document` | nothing manuscript-scoped resolved — surfaced as a general note at the head, honestly *not* in the margin |

A `Pass N §…` / leading-`§` token is **artifact-scoped** (it points at a pass artifact, not the prose):
it is excluded from the finer rungs and contributes only `document`. A manuscript scene-id is `Ch N §M`
— it contains `§` but starts with a chapter token, so it is *not* artifact-scoped. The resolver **never
fabricates precision**: a chapter-only ref that merely shares a chapter with a scene gets a `chapter`
anchor, not the scene's line-range; an ambiguous (duplicated) heading degrades to `document`.

## The comment template (fixed — no free-text slot)

```
[<severity> · <finding_id>] <mechanism> — fix class: <fix_class>. (See letter §<finding_id>.)
```

Every field is the finding's **verbatim** value; the rest is fixed boilerplate. A field carrying a
newline, a `{>>`/`<<}` sigil, or a `|` is **not** inline-CriticMarkup-safe — `build` refuses to emit it
(and `A5` flags it) rather than escaping or guessing. Fix the finding text.

## What the validator guarantees (`annotated-manuscript`)

- **A1** manifest schema + per-entry shape + `finding_id` uniqueness.
- **A2** no prose mutation: reverse transform == the bound snapshot; a CriticMarkup sigil on *either* side
  (snapshot or a projected field) is a loud failure before render.
- **A3** anchor integrity: line-range in bounds; chapter/section a unique ATX heading; honest `document` ok.
- **A4** every body Must-Fix → a manifest entry → a **rendered** span (one-to-one); a Must-Fix that never
  reaches the copy fails.
- **A5** each comment is a verbatim, inline-safe field projection.
- **W1** (advisory) a locatable Should/Could parked at `document`, or a Timeline line-range that overruns
  the snapshot; override `<!-- override: annotation-coverage F-… -->`.

The editorial letter remains the artifact of record — the synthesis, the decision layer, and the
appendices live there; the annotated copy carries the per-locus findings, reached by ID.

## Increment boundary

Increment 1 ships comment-only CriticMarkup at line-range / section / chapter / document granularity.
**Not** in Increment 1: character-precise (sentence/quote) anchoring (a future increment with its own
integrity gate), DOCX / Google Docs / Obsidian export, letter↔margin cross-links, and round-trip
re-anchoring across revisions.
