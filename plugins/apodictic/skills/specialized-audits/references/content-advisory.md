# Content-Advisory / Sensitivity-Surface Derivation — what's depicted, where, how intensely

*Reference module for the APODICTIC specialized audits. Derives a reader/marketing-facing **content
advisory** — a map of where the manuscript depicts intense material, at what intensity, on- or
off-page. Homed alongside the Reception-Risk / Consent / Erotic audits it draws on (sensitivity-
surface work, not core manuscript analysis). Spec + validator: `docs/content-advisory.md`,
`scripts/validate.sh content-advisory`. Worked example: `core-editor/references/example-content-advisory.md`.*

---

## When to use

When an author preparing to publish wants a content advisory — for front-matter notes, retailer
content-warning metadata, a sensitivity-reader handoff, or their own awareness. APODICTIC's existing
audits *assess* intense content for craft and harm risk; none derives the descriptive,
reader-facing artifact. This does — pure extraction over depicted content, anchored to loci.

It is **opt-in by design.** Some authors decline content warnings on principle, so the advisory is
generated **only** when the author asks for it — recorded as an explicit
`<!-- content-advisory: opted-in -->` marker in the artifact, never imposed.

## What this is not

- **Not** the [Reception Risk audit](craft/reception-risk.md). Reception Risk *assesses harm/offense
  risk* across five channels and produces craft findings. This **derives a descriptive advisory**
  (what is depicted, for a reader's informed choice) — no harm judgment, no craft verdict.
- **Not** the Consent-Complexity or Erotic-Content tag audits (intimate-content *craft*). This
  catalogs depicted content as an advisory.
- **Not** a defect list. A content note is **not** an `apodictic.finding.v1` and carries **no**
  Must/Should/Could severity. Its intensity scale is orthogonal to the editorial severity scale —
  the Legal Risk Register's orthogonal-severity discipline (validator `A3`).

**Consume-don't-duplicate — honestly scoped.** Where Reception Risk / Consent / Erotic have run, the
advisory *should* draw on the content they already located. But those audits emit prose with no
addressable per-instance IDs, so Increment 1 consolidation is **prose-citation only** — a note may
reference a sibling audit in prose, but there is no machine cross-check that every sibling instance
has a note (that coverage diff is deferred until those audits emit ID-bearing blocks).

## The firewall: describe the depicted, never judge or prescribe

- **Descriptive, not evaluative.** A note records *that* content is depicted and at what intensity
  ("on-page graphic violence — Ch 7"); it never calls it "gratuitous" or recommends cutting it
  (`W1` flags prescriptive constructions like "should cut/soften …", not bare descriptive adjectives
  like "excessive").
- **Extract the depicted, never infer the unstated.** A note records content the text actually
  depicts or references; it does not infer content from vibes.
- **Honest enforcement limit.** Locus *presence/shape* is gated (`A2`); locus *resolution* into the
  manuscript waits on the shared snapshot layer, so the firewall here is author/QA-enforced until then.

## The artifact

A `[Project]_Content_Advisory_[runlabel].md` of `apodictic.content_note.v1` blocks, grouped by
category, generated only under the opt-in marker:

```markdown
<!-- content-advisory: opted-in -->

<!-- apodictic:content_note
{
  "schema": "apodictic.content_note.v1",
  "id": "CN-07",
  "category": "violence",
  "intensity": "high",
  "depiction": "on-page",
  "label": "",
  "loci": ["Ch 7 ¶12-18"]
}
-->
```

- `category` — closed enum: `violence` / `sexual-content` / `self-harm-suicide` / `substance-use` /
  `abuse` / `hate-slurs` / `death-grief` / `medical` / `other`. The `other` category requires a
  non-empty `label`.
- `intensity` ∈ `low` / `medium` / `high`; `depiction` ∈ `on-page` / `off-page` / `referenced` —
  orthogonal to editorial severity.
- `loci` — manuscript locations (≥1), each a coarse chapter / §section / ¶ / line token.

## Validation

`validate.sh content-advisory <run_folder|files...> [--strict]` runs: **A1** schema (incl. the
`other`→non-empty-`label` conditional and non-empty loci elements), **A2** locus presence/shape,
**A3** no editorial-severity leak (no Must/Should/Could token in the prose or a label, no
`apodictic:finding` block), plus advisory **W1** prescriptive drift (a "should cut/soften …"
construction; ERROR under `--strict`; a note-`label` match is overridden per-id with
`<!-- override: advisory-eval CN-NN — <rationale> -->`, the reader-facing **prose** only with the
id-less `<!-- override: advisory-eval-prose — <rationale> -->`)
and **W2** opt-in marker. If no advisory artifact is resolved the command no-ops (exit 2). See
`docs/content-advisory.md`.
