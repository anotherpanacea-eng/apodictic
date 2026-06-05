# Retcon Planning (coaching track)

**Status:** v1 (Increment 1)
**Trigger:** `apodictic-coach` → Retcon Planning mode. Use when a returning author has either (a) **committed to a late structural decision** — a new ending, a reframed controlling idea, a relocated reveal, a different antagonist (Door A); or (b) a draft with **weak / "glitch" / off-trajectory elements** they suspect could be meaningful (Door B).
**Inherits:** the Coaching Firewall (`revision-coach/SKILL.md §The Coaching Firewall`) + the core Firewall (`core-editor/SKILL.md §The Firewall`).

---

## Purpose

A large share of revision is **retroactive**: once a writer discovers what the book is *really* about — or commits to a late decision — they owe the earlier draft a pile of setup, recontextualization, and continuity repair. Retcon Planning helps the author **plan** that retroactive-continuity work and **budget its commitments** — it does not do the rewriting.

**The Firewall line (what makes this APODICTIC, not AI Dungeon):** the coach infers the latent story, accounts the setup debt, budgets the commitments, and sequences the arc — then **stops**. It never writes the foreshadowing, plants the detail, or drafts the recontextualizing beat. *Plan the retcon and budget the commitments; the author writes the tissue.* Design + lineage (Gwern's *Better Fiction via Retcon Planning* + this project's setup-debt framing): [`docs/retcon-planning.md`](../../../docs/retcon-planning.md).

---

## Two doors

- **Door A — targeted retcon.** The author names a **retcon target** they've decided on. Run **reveal economy backward**: given the payoff, derive the **setup debt** — the setups the draft now owes, where they belong, and the contradictions the decision creates.
- **Door B — latent reinterpretation.** The author points at elements that feel like bugs. Run the abductive **"bug-or-feature"** move — "is there a reading in which the story was always about this?" — and present the candidate readings as **options** (never executed). A chosen reading becomes a Door-A target.

---

## The artifact: `[Project]_Retcon_Plan_[runlabel].md`

Sections: a **State Card** (active promises, unresolved tensions, forbidden contradictions, likely next pressures, controlling-idea hypothesis); a `## Retcon Targets` list (each declared with an id — `T1`, `T2`, …); the **Setup-Debt Ledger**; a **Commitment Ledger**; the **Blast Radius**; and a **dependency-ordered Sequence**. The machine-checkable spine is a set of `apodictic.retcon_item.v1` blocks — one per setup-debt / contradiction / reinterpretation:

```markdown
<!-- apodictic:retcon_item
{"schema":"apodictic.retcon_item.v1","id":"RX-01","target_id":"T1","kind":"setup-debt",
 "mutability":"free","retcon_type":"dramatic",
 "intervention_class":"plant a recontextualizable detail in the Ch.3 kitchen scene",
 "locations":["Ch. 3"],"disposition":"author seeds one gesture; do not state complicity"}
-->
```

**Two orthogonal axes** (the heart of the method):
- **`mutability`** — the commitment budget. `locked` (the reader has seen/used it — observed canon) → `costly` (exposed downstream consequences) → `free` (unused latent). What you're still free to change.
- **`retcon_type`** — the fair-play axis. `dramatic` (recontextualize for *meaning* — allowed) vs. `evidential` (change the *evidence/clues the reader reasoned from* — forbidden on locked canon).

`intervention_class` is a **class** ("plant a detail", "recontextualize the beat", "remove the contradiction"), never invented prose. Field set canonical in `schemas/apodictic.retcon_item.v1.schema.json`. Worked example: `core-editor/references/example-retcon-plan.md`.

---

## The fair-play rule (non-negotiable)

You may retcon for **meaning** freely (recontextualize what the reader has seen). You may **never** retcon the **evidence** the reader has already reasoned from — a mystery's culprit, an inspected clue, a planted fact. *Dramatic retcon improves meaning; evidential retcon destroys fair play.* If the new direction requires altering an inspected clue, that is not a retcon to plan — it is a reveal-economy problem to solve (Pass 8). And beware **rubber reality**: if a "retcon" is patching over a real structural hole rather than adding connective tissue, name the hole instead.

---

## Protocol

1. **Build / refresh the State Card** from the diagnosis (or the manuscript).
2. **Choose the door** (capture the committed target, or run the bug-or-feature abduction and let a chosen reading become a target).
3. **Account the setup debt** as `retcon_item` blocks (Door A: reveal economy run backward).
4. **Budget the commitments:** tag each item's `mutability` and `retcon_type`; the fair-play gate blocks evidential retcon of locked canon; name each costly/locked item's `blast_radius` (the Protected Elements it endangers).
5. **Sequence** the arc (decision → backward seeding → forward consequence propagation) and hand off — no prose written by the coach.

## Mechanical check

`scripts/validate.sh retcon-plan <run_folder>`: R1 schema, R2 unique ids, **R3 no evidential retcon of locked canon** (the signature gate; override `<!-- override: retcon-evidential RX-NN — … -->`), R4 target referential integrity; W1 blast-radius accounting on locked/costly items, W2 firewall drift (invented prose where a class belongs; override `retcon-firewall RX-NN`). W1/W2 advisory, ERROR under `--strict`. Ownership boundary + lineage: [`docs/retcon-planning.md`](../../../docs/retcon-planning.md).
