# Retcon Planning — a revision-coaching track

**Status:** Increment 1 **spec**. Roadmap: `ROADMAP.md` → Coaching Deepening (a concrete shape for Multi-Session Revision Arc Planning). Skill home: **revision-coach** (post-diagnostic, returning-author; inherits the Coaching Firewall). Reached via `/coach` (Retcon Planning mode).

**Lineage (recorded honestly).** Two sources, deliberately merged:
- **Door B — latent reinterpretation + commitment budget.** Gwern, *Better Fiction via Retcon Planning* (gwern.net/blog/2023/llm-retcon): treat hidden world-state as temporary; at checkpoints re-infer the latent story that best explains the canon, compress it to a small state card, and govern rewrites with a **commitment budget** (observed canon fixed > exposed consequences costly > unused latent cheap; **dramatic** retcon improves meaning, **evidential** retcon destroys fair play).
- **Door A — targeted decision → setup-debt.** A reframing that surfaced in this project's own design conversation before the essay was read: a writer who *discovers* a late structural decision (a new ending, a reframed controlling idea, a relocated reveal) incurs **setup debt** against the earlier draft; run reveal-economy *backward* (payoff → required setup) to account for it.

They are two entry doors into one machine. APODICTIC keeps only the **planning** half of Gwern's loop and refuses the generative half (see Firewall below).

---

## The Firewall line (what makes this APODICTIC and not AI Dungeon)

Gwern's loop is *generative*: it re-infers a latent world **and writes the next beats** from it. APODICTIC does the inference, scoring, compression, and commitment-budgeting as **diagnosis and revision planning**, and then stops. It hands the author a *retcon plan* — where setup must go, what it would cost, what it must not break — and the author writes the connective tissue. The model never inserts foreshadowing, plants a detail, or drafts a recontextualizing beat. Mapping:

| Gwern's retcon loop | APODICTIC keeps it as… |
|---|---|
| Canon (only what the reader has seen is fixed) | the manuscript-as-given + the Firewall (author's text is canon) |
| Hypotheses (latent motives/theme/promises/genre) | contract prediction (genre, reader promise, controlling idea) |
| Abductive reinterpretation | the core diagnostic move (the latent story the draft is half-telling) |
| Selection (coherence, agency, payoff density, *non-insane-coincidence rate*) | audits + reveal-economy fairness + the anti-over-diagnosis discipline |
| Compression → small state card | the **Manuscript State Card** (a new rolling artifact, Pass-10-class) |
| **Resample-into-prose + continue** | **refused** — this is the ghostwriting the Firewall forbids |

So: *plan the retcon and budget the commitments; the author writes the tissue.*

---

## Two entry doors

### Door A — Targeted retcon (you have committed to a late decision)
Trigger: the author names a **retcon target** they have decided on — "the ending is now X," "the controlling idea is really Y," "Z is the antagonist," "the reveal moves to chapter 4." The coach runs **reveal economy backward**: given the payoff, derive the **setup debt** — the setups the draft now owes, where they belong, and the contradictions the decision creates.

### Door B — Latent reinterpretation (you have a draft with weak / "glitch" / off-trajectory elements)
Trigger: the author points at elements that feel like bugs. The coach runs the **abductive "bug-or-feature" move**: is there a latent reading in which these become load-bearing — "the story was always about this"? It surfaces the candidate readings as **options** (never executed), each with the setup debt and commitment cost that *committing* to it would imply. Door B's output feeds Door A: a chosen reinterpretation becomes a retcon target.

Both doors converge on one **Retcon Plan** and are governed by one **commitment budget**.

---

## Artifacts

### The Manuscript State Card (compression)
A compression of what the draft has committed to: **active promises**, **unresolved tensions**, **forbidden contradictions**, **likely next pressures**, and the current **controlling-idea hypothesis**. It is the diagnostic form of Gwern's "world-state card," and it generalizes the partial-manuscript *setup inventory*. **In Increment 1 it is a `## State Card` section of the Retcon Plan**; promoting it to a standalone cross-revision rolling artifact (`[Project]_State_Card_[runlabel].md`, diff'd across rounds, Pass-10-class) is a future increment.

### The Retcon Plan
`[Project]_Retcon_Plan_[runlabel].md` — the coaching deliverable. Sections: a **State Card**; a `## Retcon Targets` list (each target declared with an id, `T1`, `T2`, …); the **setup-debt ledger** (Door A); the **commitment ledger** (the budget); the **blast radius** (Protected Elements + continuity collisions); and a **dependency-ordered sequence** (decision → backward seeding → forward consequence propagation). The machine-checkable spine is a set of structured items:

### `apodictic.retcon_item.v1` (one per setup-debt / commitment / contradiction)
```json
{
  "schema": "apodictic.retcon_item.v1",
  "id": "RX-01",
  "target_id": "T1",                   // resolves to a declared Retcon Target
  "kind": "setup-debt",                // setup-debt | contradiction | reinterpretation
  "mutability": "free",                // locked | costly | free   (the commitment budget)
  "retcon_type": "dramatic",           // dramatic | evidential    (the fair-play axis)
  "intervention_class": "plant a recontextualizable detail in the Ch.3 kitchen scene",
  "locations": ["Ch. 3", "Ch. 9 (line 220)"],
  "blast_radius": ["Protected: the sister-relationship arc (Ch.12 close)"],
  "disposition": "Author seeds one ambiguous gesture; do not state complicity."
}
```

**Two load-bearing axes, kept orthogonal** (mirroring the v2.0.0 severity/confidence discipline):
- **`mutability`** — Gwern's commitment budget. `locked` = the reader has already seen/used it (observed canon); `costly` = it has exposed downstream consequences; `free` = unused latent the author may still shape.
- **`retcon_type`** — the fair-play axis. `dramatic` = recontextualizes for *meaning* (allowed). `evidential` = changes the *evidence/clues the reader has reasoned from* (a mystery's culprit, a planted fact). **An `evidential` retcon of `locked` canon is the forbidden move** — it cheats the reader who already reasoned from it.

`intervention_class` is a *class*, never prose. The field set is canonical in `schemas/apodictic.retcon_item.v1.schema.json`.

---

## The `retcon-plan` validator

`validate.sh retcon-plan <run_folder|files>` (parses the `retcon_item` blocks via the shared `apodictic_artifacts` engine). Degrades to an advisory `WARN` without `python3`.

| ID | Severity | Rule |
|---|---|---|
| **R1 — invalid item** | ERROR | A `retcon_item` block fails its schema (bad `kind`/`mutability`/`retcon_type` enum, malformed `RX-NN` id, missing required field, broken JSON). |
| **R2 — duplicate id** | ERROR | Two items share an `RX-NN` id. |
| **R3 — evidential retcon of locked canon** | ERROR | An item with `retcon_type: evidential` **and** `mutability: locked` — changing a clue the reader has already reasoned from. Gwern's "evidential retconning destroys fair play," made mechanical. Override: `<!-- override: retcon-evidential — <rationale> -->` (e.g. the "clue" was never actually load-bearing). |
| **R4 — dangling target** | ERROR | An item's `target_id` does not resolve to a target declared in the plan's `## Retcon Targets` list (a `- T1: …` entry) — a typo or a deleted target leaves an orphan commitment. |
| **W1 — unaccounted blast radius** | WARN (ERROR `--strict`) | A `locked`/`costly` item with an empty `blast_radius` — a costly retcon planned without naming what it endangers (the Protected-Elements guard). |
| **W2 — firewall drift** | WARN (ERROR `--strict`) | `intervention_class`/`disposition` reads like *invented content* rather than a class — quoted invented dialogue, or "add a scene where <specific events>". A facilitator plans the class; the author writes the prose. Override: `<!-- override: retcon-firewall — <rationale> -->`. |

**The signature checks are R3 and W2** — they mechanize the two disciplines both sources insist on: *you may not retcon the evidence the reader has already used* (fair play) and *you may not cross into ghostwriting* (the Firewall). No other validator raises either.

**Ownership boundary.** `retcon-plan` owns the retcon-planning contract — commitment-budget coherence, the fair-play gate, target referential integrity, and firewall-drift surfacing. It does **not** judge severity (a retcon that maps to a real defect is governed by the finding/severity validators once it enters a ledger), re-diagnose (deriving the latent reading is coaching, not this validator's job), or check reveal-economy fairness in the *manuscript* (that stays with Pass 8).

---

## Workflow (revision-coach, Retcon Planning mode)

1. **Build / refresh the State Card** from the diagnosis (or the manuscript): active promises, unresolved tensions, forbidden contradictions, controlling-idea hypothesis.
2. **Choose the door.** Door A: capture the author's committed retcon target. Door B: run the bug-or-feature abduction and present latent readings as options; a chosen one becomes a target.
3. **Account the setup debt** (Door A, reveal-economy backward): per target, the required setups, locations, and contradictions to clear — as `retcon_item` blocks.
4. **Budget the commitments.** Tag each item's `mutability` and `retcon_type`; the fair-play gate (R3) blocks evidential retcon of locked canon; name the `blast_radius`.
5. **Sequence** the retcon as a dependency-ordered arc and hand off (no prose written by the coach). Validate with `validate.sh retcon-plan`.

A canonical worked example (`references/example-retcon-plan.md`) is gated by `validate.sh --check-all`.

---

## Increment boundaries

**Increment 1 (this):** the coaching-track contract, the State Card + Retcon Plan artifacts, the `apodictic.retcon_item.v1` block + schema, the `retcon-plan` validator (R1–R4 + W1–W2), the worked example, the `--check-all` gate, and revision-coach wiring.

**Future:** Door-B abduction depth (ranked latent readings with a "non-insane-coincidence" score, à la Gwern's selection); State Card as a true cross-revision rolling artifact diff'd across rounds; integration with Reveal Economy (Pass 8) so the setup-debt ledger is auto-seeded from payoff findings; and the more speculative interactive-fiction / game-narrative diagnostic the essay points at (an *unseeded* genre candidate on the roadmap).
