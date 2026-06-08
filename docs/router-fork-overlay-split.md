# Router Fork/Overlay Split — separating workflow selectors from workflow modifiers

**Status:** **Built** — Increment 1 of [Project Addressability & State-Driven Routing](../ROADMAP.md#project-addressability--state-driven-routing). Implemented in `intake-router-runtime.md` (§3 fork/overlay tagging, new §3a routing algebra, §6 split into Table A base routes + Table B overlays) and `intake-router-design.md` (axis-model correction + revised router output contract). No pass-engine or synthesis change; `validate.sh --check-all` green. This doc remains the design rationale.

The intake router's design notes assert a clean principle: *"Constraints modify workflows; they don't select them. A deadline doesn't change whether you need Core DE — it changes how Core DE runs"* (`intake-router-design.md` §Why Constraint is post-routing). The runtime router does not honor it. `constraint:time` routes to a **different** workflow (Submission Triage — a compressed go/no-go with its own terminal artifact, not Core DE). `constraint:nonfiction` routes to a **different** engine (the Argument Engine, Narrative NF, or Memoir machinery — not the fiction passes). The model says "modifiers don't select"; the route map shows three of them doing nothing but selecting.

The cost of the divergence is visible in two places. First, the router output contract had to grow a bespoke `nonfiction_route: [argument_engine | narrative_nonfiction | memoir_cnf | none]` field — a special case bolted on precisely because one "constraint" was actually a workflow selector and the flat `constraints: [list]` couldn't carry that decision. Second, the §6 route map carries the cross-product of base routes against modifiers as *enumerated rows*, which is why it is 30-plus rows with recurring `Gap` / `Partially built` cells that are really one missing capability smeared across every base route it could combine with.

This proposal splits the undifferentiated modifier axis into two kinds with different routing algebra: **forks** (which select the workflow and therefore belong in the route map) and **overlays** (which modify a selected workflow and therefore compose orthogonally and must *not* appear as route-map rows).

## The two kinds

**Fork — selects or replaces the workflow.** A fork changes which engine runs or the terminal shape of the run. Forks of the same class are mutually exclusive (you run Submission Triage *or* full Core DE, never both). Forks belong in the route map, can be conditional, and can sub-resolve into a family.

**Overlay — modifies a selected workflow.** An overlay leaves the engine and workflow shape intact and changes only the output framing, adds a diagnostic lens, or changes execution depth. Overlays compose: any number can stack on a base route, and on each other. An overlay must never be a route-map row — its applicability is a property of the overlay, evaluated against whatever base route the forks selected.

**Classification test.** Does the modifier replace the primary diagnostic engine or change the workflow's terminal artifact? → **Fork.** Does it leave the pass/engine selection intact and only reskin output, add a lens, or change depth/cost? → **Overlay.**

## Every current modifier, classified

| Current option (§3) | Today's behavior | Kind | Sub-type | Status |
|---|---|---|---|---|
| `constraint:time` | Reroute to Submission Triage (full_draft); gap for partial | **Fork** | Workflow fork (conditional on artifact) | Built (full_draft) / Gap (partial) |
| `constraint:nonfiction` | Reroute to Argument Engine / Narrative NF / Memoir | **Fork** | Engine fork (sub-resolves by form) | Built (prose) / Gap (idea-stage pre-draft) |
| `operator:team` | Multi-party intake replacing single-author intake | **Fork** | Intake fork | Gap |
| (goal) `feedback` | Prepend Feedback Triage stage, then Core DE | **Fork** | Workflow fork (prepend) | Built (v2.2.0) |
| `constraint:ai` | Add AI-Prose Calibration audit + findings | **Overlay** | Lens overlay | Built |
| `operator:editor` | Re-aim the letter at a human editor (scaffolding) | **Overlay** | Output overlay | Built |
| `operator:facilitator` | Add a teaching Vocabulary Guide artifact | **Overlay** | Output overlay | Built |
| `constraint:risk` | Add a legal risk-register output | **Overlay** | Output overlay | Charted Gap¹ |
| `execution:hybrid` | Focus-map depth; ~2–3x cost; content-invariant | **Overlay** | Execution overlay | Built |
| `execution:swarm` | Independent-lens depth; ~5x cost; content-invariant | **Overlay** | Execution overlay | Built |

¹ The route map charts `risk` as a gap (§3 option D, §6 row), but `references/legal-risk-register.md` and `references/example-legal-risk-register.md` exist. This is exactly the failure mode the split removes: under the current model a status has to be re-asserted in every base-route cell it could appear in, so it drifts. Under the split, an overlay's status lives in exactly one place (the overlay table) and is authoritative.

## What the route map becomes

The route map splits into two tables with different algebra.

**Table A — Base routes (Artifact × Goal, forks resolved).** This is the actual workflow selection. ~20 rows collapse to the genuine routing decisions; the per-modifier cross-product rows are gone.

| Artifact | Goal | Fork (if any) | Workflow | Status |
|---|---|---|---|---|
| idea | draft | — | Pre-Writing Pathway | Built |
| idea | draft (fast-track) | — | Pre-Writing (Phase 4) | Built |
| idea | draft | engine=nonfiction | Nonfiction Pre-Writing | Gap |
| fragments | draft | — | Fragment Synthesis → Pre-Writing | Built |
| fragments | repair | — | Core DE (partial flag) | Built |
| partial | repair (diagnostic) | — | Core DE (partial flag) | Built |
| partial | repair (targeted) | — | Core DE (partial, targeted) | Built |
| partial | repair | engine=nonfiction (argument) | Argument Engine on available sections | Built |
| partial | draft (rethink) | — | Pre-Writing (re-entry) | Built |
| partial | repair | workflow=time | Submission Triage | Gap (needs complete ms) |
| full_draft | repair | — | Core DE | Built |
| full_draft | repair | engine=nonfiction | Argument Engine / Narrative NF / Memoir | Built |
| full_draft | repair | workflow=time | Submission Triage | Built |
| full_draft | repair | workflow=feedback | Feedback Triage → Core DE | Built |
| full_draft | submit | — | Submission Readiness | Built |
| full_draft | submit | workflow=time | Submission Triage | Built |
| full_draft | coach | — | Revision Coach | Built |
| series | repair (single vol) | — | Core DE (series context) | Partial |
| series | repair (continuity) | — | Series Continuity Audit | Built |
| series | draft (plan next) | — | Pre-Writing (series-aware) | Partial |

**Table B — Overlays (orthogonal; compose onto any compatible base).** Status lives here once.

| Overlay | Flag | Effect | Composes onto | Status |
|---|---|---|---|---|
| AI-Prose Calibration | `constraint:ai` | Adds AI-prose lens + findings | Any prose-bearing repair/submit | Built |
| Editor Scaffolding | `operator:editor` | Re-aims letter at a human editor | Any Core DE letter | Built |
| Diagnostic Vocabulary | `operator:facilitator` | Adds teaching Vocabulary Guide | Any Core DE letter | Built |
| Legal Risk Register | `constraint:risk` | Adds risk-register output | Any repair/submit | Charted Gap¹ |
| Hybrid execution | `execution:hybrid` | Focus-map depth, ~2–3x cost | Any pass-based run >40k | Built |
| Swarm execution | `execution:swarm` | Independent-lens depth, ~5x cost | Any pass-based run | Built |

Routing then reads: **resolve one base route (apply any forks) → apply N compatible overlays.** The eight current §6 rows that are nothing but `base × overlay` (`full_draft|repair|ai`, `…|hybrid`, `…|swarm`, `…|editor`, `…|facilitator`, `full_draft|submit|hybrid`, `…|swarm`, `fragments|draft|ai`) disappear as rows; they are computed, not enumerated.

## Router output contract change

Replace the flat-list-plus-special-case shape:

```
constraints: [list of active constraint flags]
operator: [author | editor | facilitator | team]
route: [workflow name]
nonfiction_route: [argument_engine | narrative_nonfiction | memoir_cnf | none]
```

with one that mirrors the algebra:

```
base_route:  [workflow name from Table A]
forks:       { engine?: nonfiction-argument | nonfiction-narrative | nonfiction-memoir,
               workflow?: time | feedback,
               intake?: team }
overlays:    [ai, editor, facilitator, risk, hybrid, swarm]   # composable, 0..n
gap_flags:   [any forks/overlays acknowledged as gaps]
```

`nonfiction_route` stops being a special case — it is just `forks.engine`. `operator` and `constraints` stop being undifferentiated lists whose elements have incompatible routing semantics.

## Downstream effects (small, mostly subtractive)

- **§3 (Q3) tagging.** Each Q3 option is internally tagged `fork` or `overlay` so the router knows whether an answer *re-routes* (must reconcile with the Q1/Q2 base — and with any other fork) or *stacks* (append to overlays). This also fixes a latent composition bug: today, "I'm on a deadline" (`time` → fork to Triage) + "I'm editing someone else's work" (`editor` → overlay) has no defined interaction. The split gives the only sensible one: fork to Submission Triage, then apply the editor overlay to the Triage output.
- **Conditional forks are first-class.** `time` forks for `full_draft` and is a gap for `partial` — expressed directly as a conditional fork rather than two unrelated route-map cells.
- **Gap accounting collapses.** A capability gap attaches to one fork or one overlay, not to every base cell it could combine with. `intake-router-design.md` §Current gap inventory shrinks accordingly and stops being a cross-product.
- **Optional validator.** A `validate.sh route-overlay-orthogonality` check (matching the repo's validator culture) can assert that no overlay flag appears as a base-route row and that every `base × overlay` status is derivable from the overlay's single status — making the drift that produced footnote 1 mechanically impossible.

## Why this is the enabling cleanup

The larger move discussed alongside this — making `/start` a **state-driven dispatcher** over a manuscript-lifecycle state machine, rather than a front-door questionnaire — is intractable while the modifier axis conflates selectors with modifiers. A state machine needs nodes (lifecycle positions) and edges (transitions), and it needs overlays to ride on edges without multiplying them. Forks are edges; overlays are edge decorations. Until they are separated, every node would carry the full modifier cross-product and the graph would be as combinatorial as the current table. This split is the prerequisite that makes the route map expressible as a transition graph instead of a lookup grid.

---

*This file is a design proposal. The runtime specification, if adopted, lands in `intake-router-runtime.md` (§3 tagging, §6 split into Tables A/B) with rationale folded into `intake-router-design.md`.*
