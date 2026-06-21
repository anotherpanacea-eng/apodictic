# Content-Advisory / Sensitivity-Surface Derivation — what's depicted, where, how intensely

**Status:** **Built (Increment 1), 2026-06-20.** Shipped: the `apodictic.content_note.v1` schema, the `specialized-audits/references/content-advisory.md` module, `scripts/content_advisory.py` + `validate.sh content-advisory` (A1–A3 + W1–W2), and the canonical `example-content-advisory.md` (an opt-in advisory with four notes across categories) wired into `--check-all` under `--strict`. Self-testable validators 52 → 53. **Build notes:** the validator count is **derived** from `validate.sh`'s `AGG_VALIDATORS` list (not a hand-maintained number); the module is homed in **specialized-audits** (sensitivity-surface work, not core analysis) but the worked example lives in `core-editor/references/` where the `--check-all` gate resolves its fixtures; **W1** prose-level prescription (not id-addressable) is silenced by any `advisory-eval` override while a label-level match is silenced per-id; the resolver classifies on parsed blocks (`_has_block`), not raw substrings. Roadmap: `ROADMAP.md` → [Horizon Capacities](../ROADMAP.md#horizon-capacities) Tier 1, item 8.
<!-- built-when: scripts/content_advisory.py -->

A writer preparing to publish often needs a **content advisory** — a map of where the manuscript depicts intense material (violence, sexual content, self-harm, abuse), at what intensity, on- or off-page — for front-matter notes, marketing metadata, sensitivity-reader handoff, or their own awareness. APODICTIC's existing audits *assess* such content for craft and harm risk, but none **derives a reader/marketing-facing advisory artifact**. This capability is pure extraction over depicted content, anchored to loci.

It is **opt-in by design.** Some authors decline content warnings on principle; the advisory is generated only when the author asks for it (an explicit `<!-- content-advisory: opted-in -->` marker inside the artifact), never imposed.

## What this is not

- **Not** the [Reception Risk audit](../plugins/apodictic/skills/specialized-audits/references/craft/reception-risk.md). Reception Risk *assesses harm/offense risk* across five channels and produces craft findings. This **derives a descriptive advisory** (what is depicted, for a reader's informed choice) — no harm judgment, no craft verdict.
- **Not** the Consent-Complexity or Erotic-Content tag audits (intimate-content *craft*). This catalogs depicted content as an advisory.
- **Not** a defect list. A content note is **not** an `apodictic.finding.v1` and carries **no** Must/Should/Could severity. Its intensity scale is orthogonal to the editorial severity scale, exactly as the Legal Risk Register keeps its legal-escalation severity orthogonal (`A3`).

**Consume-don't-duplicate — honestly scoped.** Where Reception Risk / Consent / Erotic have run, the advisory *should* draw on the content they already located. But those audits emit **prose and ad-hoc markdown tables with no addressable per-instance IDs** (`RR-1`/`EX-1` are taxonomy/flag codes reused across passages, not instance handles) — the same situation the [Continuity Bible](continuity-bible.md) faced with the Rule Ledger. So **Increment 1 consolidation is prose-citation only**: a note may reference a sibling audit in prose, but the `consolidates` field stays `null` and there is **no machine cross-check** that every sibling-audit instance has a note (that coverage diff is unbuildable against prose and is deferred until those audits emit ID-bearing blocks). The spec does not promise a structured consolidation the codebase can't support.

## Firewall compliance — describe the depicted, never judge or prescribe

- **Descriptive, not evaluative.** A note records *that* content is depicted and at what intensity ("on-page graphic violence — Ch 7"); it never calls it "gratuitous" or recommends cutting it. (`W1` heuristically flags *prescriptive constructions*, not bare adjectives — see the rule.)
- **Extract the depicted, never infer the unstated.** A note records content the text actually depicts or references; it does not infer content from vibes.
- **Honest enforcement limit (same as the Continuity Bible).** Increment 1 checks each note's locus is **present and well-shaped** (`A2`), not that it is *truthful* — a fabricated locus would pass. Locus *resolution* into the manuscript waits on the shared [manuscript snapshot](annotated-manuscript.md) layer. The firewall here is author/QA-enforced until then; this spec does not claim a gate it hasn't built.

## The artifact

A `[Project]_Content_Advisory_[runlabel].md` of `apodictic.content_note.v1` blocks, grouped by category, generated only under the opt-in marker:

```markdown
<!-- apodictic:content_note
{
  "schema": "apodictic.content_note.v1",
  "id": "CN-007",
  "category": "violence",
  "intensity": "high",
  "depiction": "on-page",
  "label": "",
  "loci": ["Ch 7 ¶12-18"]
}
-->
```

- All fields declared in both `properties` and `required` so the subset engine guards their presence/enum/type (unknown keys still pass silently — the shared engine limitation; no firewall guarantee rests on closed keys here).
- `category` — closed enum: `violence` / `sexual-content` / `self-harm-suicide` / `substance-use` / `abuse` / `hate-slurs` / `death-grief` / `medical` / `other`. The `other` category requires a non-empty `label` — a **conditional** requirement the subset engine *cannot* express (it has no `if`/`then`/`dependentRequired`), so it is hand-coded in `content_advisory.py` (like `legal_risk.py`'s checks beyond the schema).
- `intensity` ∈ `low` / `medium` / `high`; `depiction` ∈ `on-page` / `off-page` / `referenced` — closed enums, **orthogonal to editorial severity**.
- `loci` — manuscript locations (array `minItems:1` is schema-checkable; non-empty-string per element is a Python check). `consolidates` is omitted in Increment 1 (prose citation only — see above).

## The `content-advisory` validator

`validate.sh content-advisory <run_folder>` resolves the `*_Content_Advisory_*.md` artifact; if none exists it no-ops with exit 2 ("no advisory artifact"), like `legal_risk`. Delegates to `scripts/content_advisory.py`; degrades to advisory `WARN` without `python3`. Report lines namespaced `content-advisory:<ID>`. Structurally templated on `legal_risk.py`.

| ID | Severity | Rule | Engine vs. Python |
|---|---|---|---|
| **A1 — schema** | ERROR | Each `content_note.v1` parses; `category`/`intensity`/`depiction` ∈ enums; `loci` is a non-empty array. | enum/`minItems`: subset engine. **`other`→non-empty `label`** and **non-empty-string loci elements**: Python. |
| **A2 — locus presence & shape** | ERROR | Every note carries ≥1 `loci` entry matching a coarse locus shape (chapter / §section / ¶ / line token; empty/non-loci rejected). A precondition, **not** a firewall proof (resolution deferred to the snapshot increment). | Python (`re`). |
| **A3 — no editorial-severity leak** | ERROR | The artifact's reader-facing prose and any note `label` contain no Must/Should/Could token; no `apodictic:finding` block is present in the advisory artifact. Content notes are advisories, not findings (parallel to Legal Risk's orthogonal-severity discipline). | Python (prose + `label` scan; block-type check). |
| **W1 — prescriptive drift (firewall)** | WARN (ERROR under `--strict`) | A note or the advisory prose matches a **prescriptive construction** ("should/recommend/consider … cut/remove/soften/tone down/reduce") — not bare adjectives like "excessive" (which legitimately describe depicted content, e.g. "excessive blood loss"). The advisory describes; it does not prescribe. Heuristic, not a firewall proof; override `<!-- override: advisory-eval CN-NN — quoting the manuscript/author -->`. | Python (narrow regex, legal-risk `_ADVICE_RE` style). |
| **W2 — opt-in marker** | WARN (ERROR under `--strict`) | A resolved advisory artifact lacks the `<!-- content-advisory: opted-in -->` marker (it should be generated only on request). Marker is checked *inside* the resolved artifact, à la `legal_risk` L3's in-artifact disclaimer — not an editor-scaffolding-style mode gate. | Python. |

(The sibling-coverage check — "every sibling-audit instance has a note" — is **deferred**, not a `W3` in Increment 1: it cannot be mechanized against the prose-only sibling audits.)

**Ownership boundary.** `content-advisory` owns the **descriptive content-advisory contract**: taxonomy/intensity/depiction well-formedness, locus shape, the no-editorial-severity-leak rule, the descriptive-not-prescriptive guard, and the opt-in marker — classes no other validator raises. It does **not** assess harm (`reception-risk`), judge intimate-content craft (Consent/Erotic), or produce findings. It consumes those in prose; it does not re-detect, re-judge, or (in Increment 1) structurally cross-check them.

## Canonical `--check-all` gate

A worked example — an opted-in advisory with two notes (an on-page `high` `violence` note citing a chapter locus; an `off-page` `referenced` `death-grief` note) — is added, and `validate.sh --check-all` runs `content-advisory` against it: proving schema/enum validity (`A1`), locus shape (`A2`), no severity leak (`A3`), the opt-in marker (`W2`), and a clean descriptive scan (`W1`). It includes a **negative**: a note whose prose says "should cut this scene" (trips `W1` under `--strict`) and one carrying a "Must-Fix" token (trips `A3`). The example does **not** depend on a fictional addressable sibling-audit instance (consolidation is prose-only in Increment 1). (The "canonical-framework validator runs as release gate" discipline, `ROADMAP.md` §Deferred.)

## Increment plan

**Increment 1 (this spec):** the `apodictic.content_note.v1` schema (added to `schemas/`, auto-discovered by `known_schema_ids()`), the `content-advisory.md` module (extract depicted content under the opt-in marker; cite sibling audits in prose), `scripts/content_advisory.py` + `validate.sh content-advisory`, the worked example, and the `--check-all` gate. Locus presence/shape enforced; resolution and structured sibling-consolidation deferred. Adds one validator — the hand-maintained `--self-test-all`/`--check-all` count strings in `validate.sh` (base 35) must be bumped; note this count is **contended** with the sibling Continuity Bible spec (both target 36 — whichever lands second targets 37).

**Future increments (not built):**
- **Structured sibling consolidation** — once Reception Risk / Consent / Erotic emit ID-bearing instance blocks, add a `consolidates` ref + the deferred coverage check (every sibling instance has a note).
- **Snapshot-anchored locus resolution** — upgrade `A2` from presence/shape to resolution once the snapshot lands (shared resolver with Annotated-Manuscript / Continuity-Bible).
- **Metadata + front-matter export** — render the advisory to retailer/distributor content-warning metadata and an author-opt-in reader-facing note page, descriptive only.
- **Sensitivity-reader handoff** — pair with the Reception Risk Sensitivity Reader Handoff Memo.

## Self-review (Increment 1)

- *Why consolidation is prose-only in Increment 1* — the consumed audits emit prose with no addressable per-instance IDs, so a structured `consolidates`/coverage check would assert a reference they can't supply (the Rule Ledger problem the Continuity Bible spec handled the same way). Honesty over completeness: cite in prose now, structure later.
- *Why content notes are off the editorial severity scale* — depicted content is not a defect; the orthogonal intensity scale (and `A3` guarding the seam) follows the Legal Risk Register precedent.
- *Why opt-in* — content warnings are contested; generating one unbidden imposes a stance. The in-artifact marker keeps it author-requested.
- *Why W1 targets prescriptive constructions, not adjectives* — "excessive blood loss" can be an honest *description* of depicted content; only "should cut/soften" crosses into prescribing. Narrowing the heuristic (legal-risk `_ADVICE_RE` style) avoids false-firing on the advisory's own descriptive vocabulary.
