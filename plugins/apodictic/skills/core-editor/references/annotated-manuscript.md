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
scripts/validate.sh annotated-manuscript <run_folder> # gates A1–A6 + W1
scripts/crosslink.py render <run_folder>              # back-links the letter to the margins
scripts/validate.sh crosslink <run_folder>            # gates X1–X4 (+ W1)
```

`build` reads the snapshot, the Findings Ledger, and (optionally) `Timeline.md`, resolves each finding's
anchor, projects its comment, and writes the manifest + annotated copy. It is the mechanical, firewall-safe
path: the model never authors a margin comment. `render <manifest> <snapshot>` re-renders the copy from a
manifest.

## When it is produced (the run-flow wiring)

The generators above are **wired into the run flow** so a real edit produces the deliverable — not just the
validators on a fixture (the producer, `docs/annotated-manuscript-producer.md`):

- **Intake** persists the snapshot for core-de / full-de runs (`run-core.md` §Intake Protocol → Step 1).
- **Run-end** offers the marked-up copy + crosslinked letter whenever the run wrote a full editorial letter
  (`*_…_DE_Synthesis_*`), **asks the author**, and on *yes* runs build → A1–A6 → render → X1–X4 **staged in a
  temp copy**, moving only verified artifacts into the run folder (`run-synthesis.md` §Annotated Manuscript +
  Crosslinked Letter).
- **Re-generation** for an existing un-annotated run folder is offered through `/start`'s `diagnosed`-node
  dispatch (`commands/start.md` §Step 0.5) — no separate command.

## The anchor ladder (per `evidence_refs` token; finest rung any *manuscript-scoped* token supports)

| Rung | When |
|---|---|
| `quote` | a finding's `evidence_quote` found **verbatim and uniquely** in the snapshot (Increment 2) — the finest rung, outranking line-range; gated by **A6** (verbatim + unique + offset) |
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
- **A4** the rendered comment-span multiset equals the manifest comment multiset (each manifest comment
  renders once; **no** un-manifested/authored span), then every body Must-Fix is present — a Must-Fix that
  never reaches the copy *and* an extra authored note both fail.
- **A5** each comment is a verbatim, inline-safe field projection.
- **A6** quote integrity: a `quote`-rung anchor's text occurs **verbatim, exactly once**, at the stated
  offsets in the snapshot (and matches the finding's `evidence_quote`) — a fabricated, non-unique, or
  mis-offset quote fails rather than smuggling authored text into the margin.
- **W1** (advisory) a locatable Should/Could parked at `document`, or a Timeline line-range that overruns
  the snapshot; override `<!-- override: annotation-coverage F-… -->`.

The **crosslink** validator (`scripts/validate.sh crosslink`) gates the back-linked letter: **X1** every
`<!-- finding: F-… -->` marker resolves to a manifest anchor, **X2** reverse consistency, **X3** every
CriticMarkup span in the letter is a back-link (no un-manifested spans), **X4** no letter mutation.

The editorial letter remains the artifact of record — the synthesis, the decision layer, and the
appendices live there; the annotated copy carries the per-locus findings, reached by ID.

## Increment status

- **Increment 1 (shipped):** comment-only CriticMarkup at line-range / section / chapter / document granularity.
- **Increment 2 (shipped):** character-precise quote anchoring (the `quote` rung), gated by A6.
- **Increment 3 (shipped):** letter↔margin cross-links (the `crosslink` validator, X1–X4).
- **Producer (this wiring):** intake snapshot + run-end offer + `diagnosed`-node re-gen, so a real run
  produces the deliverable (`docs/annotated-manuscript-producer.md`).
- **Export (shipped):** render-target export — Obsidian → read-only HTML → DOCX/Google-Docs comments →
  a self-contained byte-deterministic PDF proofing target (`docs/annotated-manuscript-export.md`).
- **Round-trip re-anchoring (shipped):** carry the margin notes onto a revised draft and re-emit the
  marked-up copy of the new draft, classifying held / moved / vanished / ambiguous / not-re-anchorable;
  cross-referenced against draft-over-draft regression at round-close. Wired into the Revision Round
  Protocol (`state-lifecycle.md` §Round-Trip Re-Anchoring; `docs/annotated-manuscript-reanchoring.md`).
