# Auto-Derived Continuity Bible — consolidate the canon, surface the contradictions

*Reference module for the APODICTIC Core Editor. The narrative half of a developmental-edit style
sheet: a single, locus-anchored reference of the facts the manuscript has committed to — and, as a
side effect, a ledger of the places it has committed to two facts at once. Spec + validator:
`docs/continuity-bible.md`, `scripts/validate.sh continuity-bible`. Worked example:
`example-continuity-bible.md` (paired with `example-timeline.md`).*

---

## When to use

After a development edit — typically once Pass 10 has produced a `Timeline.md` — when the author
wants the canonical record a human editor returns as the narrative side of a style sheet: who's who
and what's true. Names and spellings, ages, aliases, the significant objects, place details, and the
order of events, consolidated into one surface the writer can hold. It is a companion to the
editorial letter, not a replacement: the letter judges, the Bible catalogues.

The copyedit half of a style sheet (hyphenation, serial-comma policy, spelling conventions) stays
out of scope — this is the **narrative-continuity** half. Cross-volume continuity is the Series
Continuity audit's territory; the Bible is single-manuscript.

## The firewall: extract the stated, never author the unstated

This module **invents no canon.** It is firewall-safe by construction:

- **Stated facts only.** A Bible entry records what the text *asserts* ("Mara is 32 — Ch 9 ¶4"); it
  never infers an unstated fact, fills a gap, or resolves an ambiguity. Inferring "she's probably
  mid-thirties" from context would be inventing canon — forbidden.
- **Contradictions are surfaced, never resolved.** When the text states conflicting facts (age 30
  in Ch 2, 32 in Ch 9), the Bible records **both**, paired in the Contradiction Ledger citing both
  loci. It does **not** pick a winner — choosing canon is the author's call.
- **Consume, don't duplicate.** The Bible consolidates and *cites* the surfaces the framework
  already owns — the Timeline (by scene id), the Pass-5 character portraits, the SFF Rule Ledger —
  rather than re-deriving them. Its net-new territory is the grab-bag no single artifact owns:
  stated identity/physical facts, named objects, and place details below the Timeline's setting
  column.
- **The honest limit.** Locus *presence and shape* is gated (a citation must be present and
  well-shaped); locus *resolution* into the manuscript — proving the fact really came from the cited
  place — waits on the shared snapshot layer. Until then the firewall is author/QA-enforced, not
  mechanically proven, and this module says so rather than claiming a gate it has not built.

## The artifact

A `[Project]_Continuity_Bible_[runlabel].md` of `apodictic.canon_fact.v1` blocks, grouped into
author-facing sections (Cast, Places, World Rules, Objects, Chronology) plus a
`## Contradiction Ledger` markdown table. Each block:

```markdown
<!-- apodictic:canon_fact
{
  "schema": "apodictic.canon_fact.v1",
  "id": "CF-04",
  "entity": "Mara",
  "category": "person",
  "attribute": "age",
  "value": "32",
  "loci": ["Ch 9 ¶4"],
  "consolidates": null
}
-->
```

- `category` ∈ `person` / `place` / `object` / `world-rule` / `chronology`.
- `value` is **always a string** — numerics are quoted (`"32"`, not `32`) so the validator can
  type-check them.
- `loci` — the manuscript locations stating the fact (≥1), each a coarse chapter / §section / ¶ /
  line / page token.
- `consolidates` — set to a consumed artifact's addressable id (a **Timeline scene id**) when the
  fact is consumed rather than newly extracted; `null` otherwise. The Rule Ledger has no entry ids,
  so world-rule facts cite it in prose and leave `consolidates` null.

A contradiction is recorded as one `canon_fact` per conflicting value, plus a Contradiction-Ledger
row pairing their ids — the row names ≥2 ids that share entity+attribute but assert different values.

## How to extract (the model's job)

1. **Consume first.** Read the Timeline (scene ids, settings), the Pass-5 character portraits
   (names/aliases/role — the *fact* subset only, never arc/psychology), and any Rule Ledger. Record
   chronology facts with `consolidates` pointing at the Timeline scene id; cite the Rule Ledger /
   portraits in prose.
2. **Extract the net-new residue.** Catalogue the stated identity/physical facts (ages, spellings,
   aliases), named objects of significance, and place details no upstream artifact owns. Quote every
   numeric value. Cite the locus for each.
3. **Build the Contradiction Ledger.** Wherever the text asserts two different values for the same
   entity+attribute, record both facts and pair them in a ledger row. Do not adjudicate.

## What it is not

- **Not** the Timeline (`timeline-*`), the Rule Ledger, the character portraits, or the Series
  Continuity audit — it consumes those; it does not re-derive or re-check them.
- **Not** the character-architecture "Informed Attribute" flag (that tracks attributes-for-
  demonstration; the Bible catalogues spellings/ages/aliases as canon — overlapping raw material,
  different use).
- **Not** a copyedit style sheet (spelling/hyphenation policy) — that stays out of scope.

## Validation

`validate.sh continuity-bible <run_folder|files...> [--strict]` runs the integrity checks: **C1**
schema, **C2** locus presence/shape, **C3** contradiction integrity, **C4** chronology
consume-vs-rederive (advisory; ERROR under `--strict`; override
`<!-- override: bible-rederive CF-NN — <rationale> -->`), and **W1** coverage (a Timeline POV with
no Cast entry, or a Timeline setting with no Places entry; advisory). Pass the project-root
`Timeline.md` as a second file so C4 can resolve scene ids and W1 can check coverage; without it,
C4 cannot confirm scene ids and W1 is skipped. See `docs/continuity-bible.md`.
