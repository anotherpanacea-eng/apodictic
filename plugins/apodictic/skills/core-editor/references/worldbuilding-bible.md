# Standalone Worldbuilding Bible — check the author's own bible for self-contradiction

*Reference module for the APODICTIC Core Editor. A pre-draft consistency checker over the SFF
author's OWN hand-authored worldbuilding bible — the rules of the magic/tech, the cost of using it,
the geography, the order of events, the factions. It checks a **bible** (not a manuscript) for
self-contradiction and SURFACES the conflicts the bible has already committed to; it never invents
world content. Spec + validator: `docs/worldbuilding-bible.md`, `scripts/validate.sh world-bible`.
Worked example: `example-worldbuilding-bible.md`.*

---

## When to use

Before or alongside drafting — in the pre-writing pathway's spirit. A worldbuilding bible can
contradict itself before a single chapter exists: a rule stated two ways, a cost that is sometimes
paid and sometimes free, a city six days' ride from the capital in one note and two in another, an
event that happens "before" and "after" the same anchor. This tool reads that bible and flags the
class of contradiction the author has already locked in.

It is **distinct from the manuscript-facing SFF audits**, and consciously so:

- The **Genre Module: SF/F** (`genre-sff.md`) checks the *mechanical consistency of a manuscript* —
  the Rule Ledger and Cost Matrix ask "is the cost paid in *this scene*." This tool ports that
  consistency vocabulary (closed limits, cost types, scaling) to **bible scope, pre-draft**: "does
  the bible *state* the rule and its cost coherently, before any scene exists."
- The **SFF Worldbuilding Integration** audit (`specialized-audits/.../sff-worldbuilding.md`) checks
  whether the world does narrative *work* — its thesis is "the core problem is not inconsistency, it
  is inertness." That audit assumes the consistency baseline; this tool **checks that baseline**, and
  does it pre-draft where the integration audit has no prose to run on.
- The **Auto-Derived Continuity Bible** (`continuity-bible.md`) *extracts from a finished
  manuscript*. This tool ingests the author's *hand-authored, pre-draft* bible. Same block-and-
  validator machinery, different lifecycle stage and input.

## The firewall: extract the stated, never author the unstated

This module **invents no canon.** It is firewall-safe by construction:

- **Stated facts only.** A world_fact records what the bible *asserts* ("blood-magic cannot raise the
  dead — Bible §Magic ¶3"); it never infers an unstated rule, fills a gap, or invents a cost,
  distance, or date the bible has not written.
- **Contradictions are surfaced, never resolved.** When the bible states conflicting facts (a cost of
  "one year of life" in one note and "a drop of blood" in another), the tool records **both**, paired
  in a contradiction ledger citing both loci. It does **not** pick a winner — choosing canon is the
  author's call; choosing it for them would be invention by adjudication.
- **Recommendations stay abstract-structural.** If the tool says anything beyond the flag, it is
  structural, not content: "the bible prices blood-magic two ways — reconcile or stage the
  escalation," never "the cost should be one year of life." The author decides the world.
- **The honest limit.** The mechanical proxy for "no invention" is the locus citation, but this
  increment checks only that a locus is **present and well-shaped**, not that it is *truthful* — a
  fabricated `"Bible §Magic ¶3"` would pass. So the firewall here is **author/QA-enforced** at the
  extraction boundary, not yet mechanically proven; locus *resolution* into the source bible waits on
  the shared snapshot layer, exactly as the Continuity Bible defers its own. This module says so
  rather than claiming a gate it has not built.

## The artifact

A `[Project]_Worldbuilding_Bible_[runlabel].md` of `apodictic.world_fact.v1` blocks, grouped into
author-facing sections (Rules, Costs, Places & Distances, Chronology, Factions) plus a
`## Contradiction Ledger` markdown table. Each block:

```markdown
<!-- apodictic:world_fact
{
  "schema": "apodictic.world_fact.v1",
  "id": "WF-014",
  "category": "rule",
  "subject": "blood-magic",
  "attribute": "limit",
  "value": "raise the dead",
  "polarity": "cannot",
  "cost": null,
  "loci": ["Bible §Magic ¶3"]
}
-->
```

- `category` ∈ `rule` / `cost` / `place` / `distance` / `event` / `faction` / `entity` — it drives
  which contradiction arm applies.
- `subject` is the named element the fact is about (`"blood-magic"`, `"Karth"`, `"the Sundering"`) —
  the **grouping key** for cross-fact contradiction detection.
- `value` is **always a string** — numerics are quoted (`"6 days"`, `"120 miles"`, `"Day 100"`) so
  the validator can type-check and parse them.
- `polarity` (rule facts) ∈ `can` / `cannot` / `requires` / `n/a` — the closed-set assertion the rule
  arm pairs on.
- `cost` (cost/rule facts) — the stated price (`"one year of life"`, `"none"`, or `null` if unstated;
  omit the field entirely for a forbidden action that has no price to state).
- `pair_subject` (distance/event facts) — the other endpoint of the edge (`distance` A→B sets
  `subject=A`, `pair_subject=B`; `event` X-before-Y sets `subject=X`, `pair_subject=Y`).
- `loci` — the bible locations stating the fact (≥1), each a coarse `§section` / `¶` / page / map-note
  token.

A contradiction is recorded as one `world_fact` per conflicting value, plus a Contradiction-Ledger
row pairing their ids — and, when the contradiction is *intended* (a staged reveal, a documented cost
escalation), a per-pair override marker carrying the author's rationale.

The ledger table carries a **`State` column** — the contradiction axis, orthogonal to editorial
severity (the shared `contradiction_state` helper, also used by the [continuity
bible](continuity-bible.md)):

| State | Meaning | When |
|---|---|---|
| `conflicting` | a live, un-explained collision | the default for any written ledger row |
| `apparent` | a collision the author marks intentional | the pair carries a matching `world-rule` / `world-cost` / `world-geo` override marker (the same per-pair markers that silence the arm) |
| `consistent` | no collision | **never written as a row** |

The state is **mechanically derived, never judged**: the validator computes it from the literal
collision + the override presence and rejects a `State` value that disagrees (X1). A row whose pair is
overridden derives `apparent`; an un-overridden row derives `conflicting`. Every ledger row must pair
**at least two distinct `WF-NN` ids that each resolve to a real, well-formed `world_fact` block, whose
recorded `(subject, value, polarity, cost)` declarations are NOT all IDENTICAL** — a fabricated id, a
single id, or a row of identical declarations FAILs X1 referential integrity. A world's collision
universe is **arm-defined, not subject-defined**: cross-subject rows are legal, because geo's arms
already collide facts with different subjects (WB-G1's reversed-distance edge `A→B` vs `B→A`, and
WB-G2's chronology cycle `A→B→C→A`). Identity is the only relation that mechanically precludes a
collision; every non-identical pairing is the author's declared tension. The register **never**
carries an editorial-severity token or an `apodictic:finding` block — a contradiction is a fact-state,
not a defect (X1 firewall, the Content-Advisory A3 precedent). A ledger with data rows but no `State`
column is the pre-axis form: accepted (the column is additive) but WARNed loudly (ERROR under `--strict`).

### Feeding the letter (Stage A — prose citation)

When the bible runs inside a dev-edit, the editorial letter references each `conflicting` row **by
prose citation** (the Legal-Risk / Content-Advisory / Setup–Payoff precedent), so an unresolved
self-contradiction reaches the author's revision plan. The validator emits the conflicting rows (the
id-pair) for the letter to cite. An `apparent` (overridden) row is intentional and is **not** cited.

## How to extract (the model's job)

1. **Read the bible, not a manuscript.** The input is the author's hand-authored notes — prose and
   tables. Emit one `world_fact` per stated rule, cost, place, distance, event, faction, or entity.
   Quote every numeric value. Cite the bible locus for each.
2. **Type each fact for the right arm.** A closed-set rule → `category=rule` with a `polarity`. A
   stated price → `category=cost` (or a `cost` on a `rule`). A travel-distance or mileage →
   `category=distance` with `pair_subject`. An ordering or a dated event → `category=event`.
3. **Build the Contradiction Ledger.** Wherever the bible asserts two conflicting values, record both
   facts and pair them in a ledger row with a `State` of `conflicting`. Do not adjudicate. If the
   author *means* the contradiction (a rule that changes after an event, a cost that escalates), add
   the matching `world-rule` / `world-cost` / `world-geo` override marker and set that row's `State` to
   `apparent` — recording intent without softening the verdict. The validator rejects a `State` that
   disagrees with the override reality.

## What it is not

- **Not** the Genre Module SF/F manuscript consistency pass, the SFF Worldbuilding Integration audit,
  or the Continuity Bible — it checks the author's pre-draft *bible*, not the manuscript those run on.
- **Not** an adjudicator of *dramatic sufficiency* — whether a cost is dramatically heavy enough is
  the SFF Worldbuilding Integration audit's `TI-2 Passive Physics Engine`, out of scope here. This
  tool reads the *stated* cost and checks it is stated consistently.
- **Not** a semantic-contradiction detector. It fires only on **literal** collisions (same subject +
  normalized value + opposite polarity; one edge, two distances on one axis; a chronology cycle).
  Implied contradictions ("can fly" vs "earthbound" across different value strings) are the author's
  and the model's judgment, deliberately outside the mechanical gate to keep false positives near
  zero.

## Validation

`validate.sh world-bible <run_folder|files...> [--strict]` runs the integrity + contradiction checks:
**W1** schema + bespoke closed-key check, **WD** id-uniqueness, **WB-R1** closed-set rule consistency,
**WB-C1** cost contradiction (+ **WB-C2** free-then-costed, advisory; ERROR under `--strict`),
**WB-G1** distance contradiction (within a commensurable unit class — spatial vs travel-time are
separate axes), **WB-G2** chronology (a happens-before cycle, or the same event at two Day anchors),
and the **WF** firewall prose scan (a resolution/invention verb in the bible's prose; advisory, ERROR
under `--strict`). Each conflict is overridable per-pair:
`<!-- override: world-rule|world-cost|world-geo WF-NN/WF-MM — <rationale> -->`
(and `<!-- override: world-firewall — <rationale> -->` for WF). An empty/absent artifact is a clean
no-op. See `docs/worldbuilding-bible.md`.
