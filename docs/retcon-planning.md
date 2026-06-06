# Retcon Planning — a revision-coaching track

**Status:** Increment 1 + **F1 (Ranked Door-B abduction)** + **F2 (State Card rolling artifact)** built. Roadmap: `ROADMAP.md` → Coaching Deepening (a concrete shape for Multi-Session Revision Arc Planning). Skill home: **revision-coach** (post-diagnostic, returning-author; inherits the Coaching Firewall). Reached via `/coach` (Retcon Planning mode).

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

**The Selection step (F1).** Candidate readings are not a flat menu — they are **ranked** (Gwern's selection step) by a small rubric and pruned to the top 1–3, the costed shortlist. Each candidate is an `apodictic.retcon_reading.v1` block scored 1–5 (higher is better) on five dimensions: **canon coherence**, **payoff density**, **agency preservation**, **genre fit**, and **coincidence resistance** — the last is the structural guard against *rubber reality* (a reading that only "works" by treating every incidental detail as load-bearing scores low). A `coincidence_note` shows the rate's work (which details the reading makes load-bearing). The chosen reading's `implied_targets` then names the declared Retcon Target it becomes — the Door-B → Door-A handoff, made referentially checkable.

Both doors converge on one **Retcon Plan** and are governed by one **commitment budget**.

---

## Artifacts

### The Manuscript State Card (compression)
A compression of what the draft has committed to: **active promises**, **unresolved tensions**, **forbidden contradictions**, **likely next pressures**, and the current **controlling-idea hypothesis**. It is the diagnostic form of Gwern's "world-state card," and it generalizes the partial-manuscript *setup inventory*. It appears two ways: as a human-readable `## State Card` section inside the Retcon Plan (Increment 1), and — **as of F2** — as a standalone, structured, **rolling** artifact `[Project]_State_Card_[runlabel].md` at the project root, carrying one `apodictic.state_card.v1` block per round and **diff'd across revision rounds** (the Pass-10-class rolling-structured-artifact pattern). See §The `state-card-diff` validator.

```json
{
  "schema": "apodictic.state_card.v1",
  "round": 2,
  "controlling_idea": "the cost of the silences we keep to protect those we love",
  "active_promises": ["SE-01: the dual-POV converges", "SE-02: the sister-arc pays off"],
  "unresolved_tensions": ["SE-04: the locket's significance (Ch. 2)"],
  "forbidden_contradictions": ["SE-05: keep the sisters' warmth earned"],
  "likely_next_pressures": ["the new ending re-weights every sister scene"]
}
```

The three tracked lists (promises / tensions / contradictions) hold `"SE-NN: <text>"` strings sharing **one kind-agnostic `SE-NN` id namespace**, so the *same* element keeps its id when it changes kind across rounds — the cross-revision-traceability lesson (don't depend on prose matching). The `SE-NN:` prefix and within-card uniqueness are enforced in code (S1/S2), since the subset schema checker can't express them. Field set canonical in `schemas/apodictic.state_card.v1.schema.json`.

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

### `apodictic.retcon_reading.v1` (one per ranked Door-B candidate reading) — F1

```json
{
  "schema": "apodictic.retcon_reading.v1",
  "id": "CR-01",
  "reading": "the sister was complicit all along",   // a CLASS/label of the latent reading, never prose
  "scores": {                                          // the Selection rubric — integers 1-5, higher is better
    "canon_coherence": 5,
    "payoff_density": 4,
    "agency_preservation": 5,
    "genre_fit": 4,
    "coincidence_resistance": 4                         // 5 = no forced coincidences; 1 = rubber-reality over-fit
  },
  "coincidence_note": "needs only the locket and the Ch.7 silence load-bearing; the rest stands",
  "implied_targets": ["T1"]                             // declared Retcon Target(s) this reading becomes if committed
}
```

The five `scores` dimensions and the 1–5 range are required, but the subset schema checker can't express nested required keys or numeric bounds, so they are enforced in `scripts/retcon_plan.py` (R5) — the same place the R3 fair-play gate lives. `coincidence_note` is optional in the schema; a surfaced reading lacking it raises the **W3** over-fitting-guard advisory. `implied_targets` is optional, but every id present must resolve to a declared target (**R7**). Field set canonical in `schemas/apodictic.retcon_reading.v1.schema.json`.

---

## The `retcon-plan` validator

`validate.sh retcon-plan <run_folder|files>` (parses the `retcon_item` blocks via the shared `apodictic_artifacts` engine). Degrades to an advisory `WARN` without `python3`.

| ID | Severity | Rule |
|---|---|---|
| **R1 — invalid item** | ERROR | A `retcon_item` block fails its schema (bad `kind`/`mutability`/`retcon_type` enum, malformed `RX-NN` id, missing required field, broken JSON). |
| **R2 — duplicate id** | ERROR | Two items share an `RX-NN` id. |
| **R3 — evidential retcon of locked canon** | ERROR | An item with `retcon_type: evidential` **and** `mutability: locked` — changing a clue the reader has already reasoned from. Gwern's "evidential retconning destroys fair play," made mechanical. Override (per item): `<!-- override: retcon-evidential RX-NN — <rationale> -->` (e.g. the "clue" was never actually load-bearing). |
| **R4 — dangling target** | ERROR | An item's `target_id` does not resolve to a target declared in the plan's `## Retcon Targets` list (a `- T1: …` entry) — a typo or a deleted target leaves an orphan commitment. |
| **W1 — unaccounted blast radius** | WARN (ERROR `--strict`) | A `locked`/`costly` item with an empty `blast_radius` — a costly retcon planned without naming what it endangers (the Protected-Elements guard). |
| **W2 — firewall drift** | WARN (ERROR `--strict`) | `intervention_class`/`disposition` reads like *invented content* rather than a class — quoted invented dialogue, or "add a scene where <specific events>". A facilitator plans the class; the author writes the prose. Override (per item): `<!-- override: retcon-firewall RX-NN — <rationale> -->`. |

**Door-B Selection step (F1)** — checks over the `apodictic.retcon_reading.v1` blocks:

| ID | Severity | Rule |
|---|---|---|
| **R5 — invalid reading** | ERROR | A `retcon_reading` block fails its schema (malformed `CR-NN` id, missing required field, broken JSON), or its `scores` object is missing one of the five named dimensions / carries a value outside 1–5. |
| **R6 — duplicate reading id** | ERROR | Two readings share a `CR-NN` id. |
| **R7 — dangling reading target** | ERROR | A reading's `implied_targets` entry does not resolve to a declared target in `## Retcon Targets` (the Door-B → Door-A handoff broke — a typo or deleted target). Mirrors R4. |
| **W3 — uncosted reading** | WARN (ERROR `--strict`) | A surfaced candidate reading carries no `coincidence_note` — the non-insane-coincidence-rate over-fitting guard isn't shown its work. **The signature F1 check.** |
| **W4 — unpruned shortlist** | WARN (ERROR `--strict`) | More than 3 candidate readings are surfaced — the Selection step returns the top 1–3, not a flat menu. |

The validator prints the readings sorted by score total (max 25), so the ranking is mechanically visible.

**The signature checks are R3 and W2** — they mechanize the two disciplines both sources insist on: *you may not retcon the evidence the reader has already used* (fair play) and *you may not cross into ghostwriting* (the Firewall). No other validator raises either. F1 adds the **Selection** discipline: rank the readings, and **W3** keeps the coincidence rate honest (the guard against rubber reality).

**Ownership boundary.** `retcon-plan` owns the retcon-planning contract — commitment-budget coherence, the fair-play gate, target referential integrity, and firewall-drift surfacing. It does **not** judge severity (a retcon that maps to a real defect is governed by the finding/severity validators once it enters a ledger), re-diagnose (deriving the latent reading is coaching, not this validator's job), or check reveal-economy fairness in the *manuscript* (that stays with Pass 8).

---

## The `state-card-diff` validator (F2)

`validate.sh state-card-diff <current>` validates one card; `validate.sh state-card-diff <prior> <current>` diffs two rounds (modeled on `timeline-diff`). Degrades to an advisory `WARN` without `python3`.

| ID | Severity | Rule |
|---|---|---|
| **S1 — invalid card** | ERROR | A `state_card` block fails its schema, or a tracked-list element lacks a well-formed `SE-NN: <text>` id prefix (format enforced in code). |
| **S2 — duplicate id** | ERROR | Two tracked elements in one card share an `SE-NN` id (one namespace across promises / tensions / contradictions). |
| **S3 — round backwards** | ERROR | `current.round < prior.round` — a stale or misordered diff. |
| **S4 — promise→contradiction** | ERROR | An `SE-NN` that was an `active_promise` in prior is a `forbidden_contradiction` in current — the draft has reasoned past a coherence break. **The signature F2 check.** Override: `<!-- override: state-card-transition SE-NN — <reason> -->`. |
| **W1 — dropped promise** | WARN (ERROR `--strict`) | An `SE-NN` `active_promise` in prior is gone from current entirely (silently dropped, not resolved). Override: `<!-- override: state-card-drop SE-NN — <reason> -->`. |
| **W2 — idea shift** | WARN (ERROR `--strict`) | `controlling_idea` changed between rounds (reframing is legitimate but worth surfacing). Override: `<!-- override: state-card-idea-shift — <reason> -->`. |
| **W3 — same-round edit** | WARN (ERROR `--strict`) | `current.round == prior.round` but the content differs — bump the round when the card changes. |

The diff prints a one-line summary (kept / added / resolved-tension). **S4 is the signature check** — it mechanizes the coherence break F2 exists to catch ("a Round-1 active promise is now a forbidden contradiction"). Because elements are matched by `SE-NN` id, S4 survives rewording. **Ownership boundary.** `state-card-diff` owns cross-round State Card coherence; it does not re-diagnose, judge severity, or duplicate the `retcon-plan` contract.

---

## Workflow (revision-coach, Retcon Planning mode)

1. **Build / refresh the State Card** from the diagnosis (or the manuscript): active promises, unresolved tensions, forbidden contradictions, controlling-idea hypothesis.
2. **Choose the door.** Door A: capture the author's committed retcon target. Door B: run the bug-or-feature abduction, **score and rank** the latent readings (the `## Candidate Readings` table — top 1–3, each with a coincidence-rate note), present them as options; a chosen one's `implied_targets` becomes a declared target.
3. **Account the setup debt** (Door A, reveal-economy backward): per target, the required setups, locations, and contradictions to clear — as `retcon_item` blocks.
4. **Budget the commitments.** Tag each item's `mutability` and `retcon_type`; the fair-play gate (R3) blocks evidential retcon of locked canon; name the `blast_radius`.
5. **Sequence** the retcon as a dependency-ordered arc and hand off (no prose written by the coach). Validate with `validate.sh retcon-plan`.

A canonical worked example (`references/example-retcon-plan.md`) is gated by `validate.sh --check-all`.

---

## Increment boundaries

**Increment 1:** the coaching-track contract, the State Card + Retcon Plan artifacts, the `apodictic.retcon_item.v1` block + schema, the `retcon-plan` validator (R1–R4 + W1–W2), the worked example, the `--check-all` gate, and revision-coach wiring.

**F1 (built):** the Door-B Selection step — the `apodictic.retcon_reading.v1` block + schema, the ranked `## Candidate Readings` section, the `retcon-plan` validator's reading checks (R5–R7 + W3–W4) with the over-fitting guard, the ranked display, the worked-example readings under the `--check-all` gate, and the revision-coach Door-B protocol update. Same validator (no new validator entry; count stays 24).

**F2 (built):** the State Card promoted to a standalone rolling artifact — the `apodictic.state_card.v1` block + schema, the new `state-card-diff` validator (S1–S4 + W1–W3, modeled on `timeline-diff`), the canonical Round-1 / Round-2 worked examples under the `--check-all` gate, and registration of `[Project]_State_Card_[runlabel].md` as a project-root rolling-state file. New validator (24 → 25).

**Future:** the increments below (F1, F2 now built; F3–F4 remain).

## Future increments

Each is additive on Increment 1 and keeps the Firewall (plan the class, never write the prose). Listed roughly by leverage.

### F1 — Ranked Door-B abduction (the Selection step) — **Built**

**What.** Door B used to surface latent "bug-or-feature" readings as a flat, unranked list. F1 adds the scoring step from Gwern's loop: candidate readings are ranked by a small rubric — coherence with the canon, payoff density, character-agency preservation, genre fit, and a **non-insane-coincidence rate** (penalize a reading that only "works" by treating every incidental detail as load-bearing) — and pruned to the top 1–3, each with its score profile and the target it becomes if committed.
**Why.** This is the structural guard against "rubber reality" / paranoid over-fitting — the failure mode the essay names — and it gives the author a principled, costed shortlist instead of a flat menu.
**Built as.** A `## Candidate Readings` section with an `apodictic.retcon_reading.v1` block per candidate (`id`, the five `scores` dimensions, optional `coincidence_note`, optional declared `implied_targets`). The `retcon-plan` validator gained R5 (schema + 1–5 score rubric), R6 (unique reading ids), R7 (reading-target referential integrity), **W3** (the coincidence-note over-fitting guard — the signature F1 check), and W4 (top-1–3 shortlist), plus a ranked-by-total display. Firewall unchanged — still options, never prose. See §The `retcon-plan` validator and `schemas/apodictic.retcon_reading.v1.schema.json`.

### F2 — State Card as a standalone cross-revision rolling artifact — **Built**

**What.** The `## State Card` section is now also a first-class rolling artifact — `[Project]_State_Card_[runlabel].md` at the project root, diff'd across revision rounds (the Pass-10-class rolling-structured-artifact pattern).
**Why.** A retcon's whole value is *cross-round* coherence, and a per-run section can't show drift. A rolling, diff'd card surfaces movement like "the controlling-idea hypothesis shifted between round 2 and round 3," or "a Round-1 active promise is now a forbidden contradiction" — exactly the cross-revision coherence the Pass-10 pattern exists for.
**Built as.** The `apodictic.state_card.v1` schema (one block per round; tracked elements carry a kind-agnostic `SE-NN` id); the `state-card-diff` validator (modeled on `timeline-diff`) — single-card S1/S2 and cross-round S3/S4 + W1–W3, with **S4 (promise→contradiction)** the signature coherence-break check; canonical Round-1 / Round-2 worked examples gated by `--check-all`; and registration in `output-structure.md` as a project-root rolling-state file. See §The `state-card-diff` validator and `schemas/apodictic.state_card.v1.schema.json`.

### F3 — Reveal-Economy (Pass 8) auto-seeding of the setup-debt ledger

**What.** Door A enumerates setup debt by hand. Pass 8 (Reveal Economy) already maps setup→payoff and runs a fairness test; given a retcon target (a new or relocated payoff), derive the required setups from the Pass-8 map and propose `retcon_item` candidates the author curates — each carrying a Pass-8 cross-reference.
**Why.** Closes the loop between the diagnostic (Pass 8) and the coaching (Retcon Planning), cuts manual enumeration, and grounds each setup-debt item in reveal-economy evidence — including the fairness check that keeps a seeded clue honest (so an auto-seeded item can't quietly become an evidential retcon).
**Shape.** A Pass-8 → Retcon-Plan handoff; setup-debt items gain a `source` cross-reference to the originating Pass-8 finding. Firewall: still classes, derived from existing findings.
**Dependency.** A completed Pass 8 / reveal-economy run.

### F4 — Interactive-fiction / game-narrative diagnostic (speculative, demand-gated)

**What.** Extend the retcon frame to *interactive* fiction / game narrative — the essay's native habitat. Diagnose branching and agency: does the hidden world-state harden too early? are player-observed canon and the commitment budget respected across branches? Kept **diagnostic** (evaluate a branching narrative's retcon-safety), never generative (the engine does not write the branches).
**Why.** Interactive fiction / game narrative is an *unseeded* genre candidate on the roadmap (§Genre & Audit Expansion), and the retcon frame is its native analytical lens.
**Shape.** A genre-module-style diagnostic built per the genre-expansion protocol (level-setting research → structural spec → multi-model QA). Larger and demand-gated — build only if IF / game manuscripts actually materialize.
**Dependency.** The genre-expansion protocol; real demand.
