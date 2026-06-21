# Auto-Derived Continuity Bible — the manuscript's canonical facts, consolidated

**Status:** **Built (Increment 1), 2026-06-20.** Shipped: the `apodictic.canon_fact.v1` schema, the `core-editor/references/continuity-bible.md` extraction module, `scripts/continuity_bible.py` + `validate.sh continuity-bible` (C1–C4 + W1), and the canonical `example-continuity-bible.md` (consolidating `example-timeline.md`, with a real Mara-age contradiction) wired into `--check-all` under `--strict`. Self-testable validators 49 → 50. **Two build-time deltas from this spec** (both honest-scoping, see §Self-review): (1) the validator count is **derived** from `validate.sh`'s `AGG_VALIDATORS` list, not a hand-maintained "35→36" string — adding `continuity-bible` to that list is the whole count change; (2) W1 character coverage is sourced from the Timeline **POV column** (the only machine-readable name source — there is no `pass-5.md` artifact and no portrait fixture), with portrait-sourced coverage deferred. Roadmap: `ROADMAP.md` → [Horizon Capacities](../ROADMAP.md#horizon-capacities) Tier 1, item 7. Homed in core-editor as a derived deliverable (like [Manuscript-Structure Visualizations](manuscript-visualizations.md)), not a routed audit.
<!-- built-when: scripts/continuity_bible.py -->

A human developmental (and copy) editor often returns a **style sheet**: the canonical record of who's who and what's true — character names and spellings, ages, eye colors, the geography, the rules of the world, the order of events. APODICTIC scatters these facts across several artifacts (the Timeline, the SFF Rule Ledger, the Pass-5 character portraits) and never consolidates the *narrative* half into one place a writer can hold. The Continuity Bible is that consolidation: a single, locus-anchored reference of the facts the manuscript has committed to — and, as a side effect, a detector of the places it has committed to two facts at once.

The copyedit half of a style sheet (hyphenation, serial-comma policy, spelling conventions) stays out of scope (`ROADMAP.md` §Not Planned — line/copyediting). This is the **narrative-continuity** half. (Naming note: the Series Continuity audit already uses "series bible" for the *author's* cross-volume artifact; "Continuity Bible" is the single-manuscript, framework-derived sibling — adjacent concept, distinct artifact.)

## Consume, don't duplicate

The framework already owns several continuity surfaces. The Bible **consolidates and cites** them; it does not recompute them — the companion-module-reads-the-shared-artifact pattern (the Argument Engine's design principle), the same discipline [Promise-Contract Fidelity](promise-contract-audit.md) uses with Shelf & Positioning.

| Existing surface | What it owns | Bible's relationship |
|---|---|---|
| `Timeline.md` (Pass 10, **project root**) | temporal architecture (scene order, dates, spans); scenes have real ids (`Ch N §M`) | **consume** — the Chronology section references Timeline scene ids, never re-derives them |
| SFF **Rule Ledger** (Pass 10) | magic/world rules + cost accounting | **consume by reference only** — the Rule Ledger is an *in-letter / in-ledger table*, **not a standalone artifact and has no entry-id scheme**, so the Bible's World Rules section points at it in prose; structured `consolidates` against it is **deferred** (see C4) |
| Pass-5 **character portraits** | character psychology + arc (Wound→Lie→Want→Need) | **consume the *fact* subset** — names/aliases/role; never arc/psychology |
| character-architecture **"Informed Attribute"** flag | inventories *stated attributes* ("smart, dangerous") to test demonstration | **distinct** — that flag tracks attributes-for-demonstration; the Bible catalogues spellings/ages/aliases as *canon*, a different use of overlapping raw material |
| `Series_State.md` / **Series Continuity audit** | **cross-volume** consequence tracking (incl. some identity facts) | **out of scope** — the Bible is single-manuscript; Series_State is the cross-book layer |

The genuinely **net-new** territory — the grab-bag no single artifact owns — is **stated identity/physical facts** (ages, appearance, spellings, aliases), **named objects** of significance, and **place details** below the Timeline's setting column. That residue, plus the consolidation and the contradiction ledger, is the Bible's whole job. (Verified: the Pass-5 portraits hold psychology/arc, not identity facts; the residue is genuinely unclaimed.)

## Firewall compliance — extract the stated, never fill the unstated

- **Stated facts only.** A Bible entry records what the text *asserts* ("Mara is 32 — Ch 9 ¶4"); it never infers an unstated fact, fills a gap, or resolves an ambiguity. Inferring "she's probably mid-thirties" from context would be inventing canon — forbidden.
- **Contradictions are surfaced, never resolved.** When the text states conflicting facts (age 30 in Ch 2, 32 in Ch 9), the Bible records **both**, flagged as a contradiction citing both loci (`C3`). It does **not** pick a winner — choosing canon is the author's call; choosing it for them would be invention by adjudication (the same surface-don't-author posture as the [Annotated-Manuscript](annotated-manuscript.md) deliverable, consistent with `SKILL.md §The Firewall`).
- **The honest limit of Increment 1's enforcement.** The mechanical proxy for "no invention" is locus citation, but Increment 1 can only check that a locus is **present and well-shaped** (`C2`), not that it is *truthful* — a fabricated `"Ch 9 ¶4"` would pass. So the firewall here is **not yet mechanically proven**; it is author/QA-enforced, with `C2` catching only missing or malformed citations. The real proof — resolving each locus into the manuscript — waits on the shared [manuscript snapshot](annotated-manuscript.md) layer (a future increment), exactly as the Annotated-Manuscript spec defers its own locus *resolution*. This spec does not claim a firewall gate it has not yet built.

## The artifact

A `[Project]_Continuity_Bible_[runlabel].md` of `apodictic.canon_fact.v1` blocks, grouped into author-facing sections (Cast, Places, World Rules, Objects, Chronology) plus a `## Contradiction Ledger` markdown table. Each block:

```markdown
<!-- apodictic:canon_fact
{
  "schema": "apodictic.canon_fact.v1",
  "id": "CF-014",
  "entity": "Mara",
  "category": "person",
  "attribute": "age",
  "value": "32",
  "loci": ["Ch 9 ¶4"],
  "consolidates": null
}
-->
```

- All seven fields (`schema`, `id`, `entity`, `category`, `attribute`, `value`, `loci`) are declared **both** in the schema's `properties` and `required`, so the subset engine guards them. (Note: the subset engine silently allows *unknown* keys, so a misspelled field passes — a known limitation shared with `legal_risk` et al.; the Python validator does not add closed-key checking here because, unlike the persona spec, no firewall guarantee rests on it.)
- `value` is **always a string** (the extractor quotes numerics: `"32"`, not `32`), so `C1` can type-check it; an unquoted numeric fails.
- `category` ∈ `person` / `place` / `object` / `world-rule` / `chronology` (closed enum).
- `loci` — manuscript locations stating the fact (≥1; `C2`).
- `consolidates` — optional ref into an owned artifact **with an addressable id** (a Timeline scene id) when the fact is *consumed* rather than newly extracted; `null` otherwise. (The Rule Ledger has no ids, so world-rule facts cannot set a structured `consolidates` in Increment 1 — they cite it in prose.)

A contradiction is recorded as a `canon_fact.v1` for **each** conflicting value plus a `## Contradiction Ledger` table row pairing their ids. That table is plain markdown, **not** an `apodictic:*` block, so `C3` is **bespoke table parsing in `continuity_bible.py`** (the same group-by primitive as `legal_risk.py`'s duplicate-id logic), not a schema-engine check.

## The `continuity-bible` validator

`validate.sh continuity-bible <run_folder>` resolves the Bible in the run folder and the **`Timeline.md` at the project root** (mirroring `pass-10.md`'s placement) plus the Pass-5 portraits if present. Delegates to `scripts/continuity_bible.py`; degrades to advisory `WARN` without `python3`. Report lines namespaced `continuity-bible:<ID>`. Structurally templated on `legal_risk.py` (flat-field schema + `parse_blocks` + group-by).

| ID | Severity | Rule |
|---|---|---|
| **C1 — schema** | ERROR | Each `canon_fact.v1` parses; `category` ∈ enum; `entity`/`attribute` present; `value` is a (string) scalar; `loci` is a non-empty array. Subset-engine-validatable for the flat fields. |
| **C2 — locus presence & shape** | ERROR | Every `canon_fact` carries ≥1 `loci` entry, and each matches a coarse locus shape (a chapter / §section / ¶ / line token — rejecting empty strings and obvious non-loci). **A well-formedness precondition, not a firewall proof** — it cannot detect a fabricated-but-well-shaped locus; locus *resolution* into the manuscript is the deferred snapshot increment. |
| **C3 — contradiction integrity** | ERROR | Every Contradiction-Ledger row references ≥2 real `canon_fact` ids that share `entity`+`attribute` but assert **different** `value`s, each with its own loci. Parsed by `continuity_bible.py` (bespoke markdown-table parse), not the schema engine. |
| **C4 — consume-don't-duplicate (chronology only, Inc 1)** | WARN (ERROR under `--strict`) | A `chronology` `canon_fact` that does not set `consolidates` to a real Timeline scene id — i.e., re-derives a temporal fact the Timeline already owns. Scoped to chronology↔Timeline because only the Timeline has addressable ids; world-rule↔Rule-Ledger is deferred until the Rule Ledger is addressable. Override `<!-- override: bible-rederive CF-NN — <rationale, e.g. no Timeline run> -->`. |
| **W1 — coverage** | WARN (ERROR under `--strict`) | A named character (the Timeline **POV column** — the machine-readable name source, since there is no Pass-5 portrait artifact) or a setting (the Timeline **Setting column**) in the project-root Timeline has no Cast/Places entry — a continuity gap. Advisory. Portrait-sourced character coverage deferred until portraits emit a machine-readable artifact. |

**Ownership boundary.** `continuity-bible` owns the **consolidated canonical-fact reference**: schema/locus well-formedness, contradiction integrity, and the chronology consume-vs-rederive boundary — classes no other validator raises. It does **not** validate the Timeline (`timeline-*`), the Rule Ledger, character arcs, or cross-volume continuity (`Series_State` / the Series Continuity audit). It consumes those; it does not re-derive or re-check them.

## Canonical `--check-all` gate

A worked example — a small fixture Bible consolidating the existing project-root-style `example-timeline.md` (a `chronology` fact with `consolidates` set to a real Timeline scene id, e.g. `Ch 1 §2`) plus two net-new `person` facts that contradict on `age` (with a Contradiction-Ledger row pairing them) — is added, and `validate.sh --check-all` runs `continuity-bible` against it: proving locus well-formedness (`C2`), contradiction integrity (`C3`), and a clean chronology consume check (`C4`, the chronology fact correctly cites the Timeline scene id) on canonical artifacts (the "canonical-framework validator runs as release gate" discipline, `ROADMAP.md` §Deferred).

## Increment plan

**Increment 1 (this spec):** the `apodictic.canon_fact.v1` schema (added to `schemas/`, auto-discovered by `known_schema_ids()` — which globs the directory, no manual registry edit), the `continuity-bible.md` extraction module (extract net-new identity/object/place facts; consume Timeline by scene id + Rule Ledger / portraits by prose; build the Contradiction Ledger), `scripts/continuity_bible.py` + `validate.sh continuity-bible`, the worked example, and the `--check-all` gate (run under `--strict`). Locus *presence/shape* enforced; locus *resolution* deferred. Adds one validator — registered by appending `continuity-bible` to `validate.sh`'s `AGG_VALIDATORS` list (the count is **derived** from that list via `AGG_COUNT`, not a hand-maintained number; 49 → 50) and to the `Commands:` line.

**Future increments (not built):**
- **Snapshot-anchored locus resolution** — once the [manuscript snapshot](annotated-manuscript.md) lands, upgrade `C2` from presence/shape to *resolution* (each `loci` entry must resolve into the snapshot), turning the firewall from author-enforced into mechanically proven, shared with the Annotated-Manuscript anchor resolver.
- **Addressable Rule Ledger + world-rule consolidation** — if the Rule Ledger gains entry ids, extend `C4` to world-rule↔Rule-Ledger.
- **Contradiction → finding promotion** — promote a Contradiction-Ledger row into an `apodictic.finding.v1` (a continuity Must/Should-Fix) so it enters the editorial letter and the revision loop.
- **Style-sheet export** — render the Bible to the alphabetized cast+spellings format a copyeditor expects (still narrative facts only; not copyedit policy).

## Self-review (Increment 1)

- *Why C2 is honestly a precondition, not a firewall proof* — "did this fact come from the text" is not detectable from a citation's *presence*; only resolving the citation into the manuscript proves it. Increment 1 ships the presence/shape check and says plainly the firewall is author-enforced until the snapshot layer lands, rather than borrowing the rhetoric of a checkable gate it hasn't built.
- *Why consolidate rather than extract everything* — re-deriving the Timeline, Rule Ledger, and character facts would duplicate three artifacts and invite drift. The Bible's value is the *single locus-anchored surface* plus the net-new identity/object/place residue.
- *Why contradictions aren't resolved* — picking the "true" age is choosing canon, the author's job; the Bible's job is to make the conflict impossible to miss, with both loci, and stop there.
- *Why C4 is chronology-only in Increment 1* — `consolidates` needs an addressable id on the consumed side; only the Timeline has one. Claiming symmetric Rule-Ledger coverage would be asserting a reference the artifact can't supply.
- *Why W1 character coverage reads the Timeline POV column, not the Pass-5 portraits (build-time delta)* — the spec named the Pass-5 portraits as the character source, but the build surfaced that there is **no `pass-5.md` and no portrait fixture**: the portraits are prose with no machine-readable name field, so depending on them would make W1 a fragile, false-positive-prone parse. The Timeline Event-Ledger **POV column** *is* a machine-readable named-character source (and is already the second input C4 needs), so Increment 1 sources both halves of W1 — characters (POV) and settings (Setting) — from the Timeline, and defers portrait-sourced coverage to the increment that gives portraits a structured artifact. Same honesty-over-completeness posture this spec already takes for the Rule Ledger (`C4`) and locus resolution (`C2`).
