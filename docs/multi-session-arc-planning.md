# Multi-Session Revision Arc Planning — design, lineage, and the validator's ownership boundary

**Track:** revision-coaching (Coaching Deepening). **Operator:** `revision-coach`.
**Skill:** `plugins/apodictic/skills/revision-coach/references/multi-session-arc-planning.md`.
**Schema:** `apodictic.revision_arc.v1`. **Validator:** `revision-arc` (`scripts/revision_arc.py`).
**Canonical example:** `plugins/apodictic/skills/core-editor/references/example-revision-arc.md`.

## The idea

Per-session planning answers *"what's the highest-leverage thing to do next?"* — the built **Loop
Dispatch** (`revision-coach/SKILL.md §Loop Dispatch`). **Arc Planning** answers the layer **above**:
*"what's the multi-week strategy?"* — a phased revision arc that sequences the full Findings Ledger:

- **Phase 1 — structural root causes** (the Must-Fix structural roots),
- **Phase 2 — downstream consequences** (findings gated on Phase 1 closing),
- **Phase 3 — polish** (Could-Fix / line-level, no upstream dependency).

The arc is the **calendar** that sequences findings into per-session work; each phase feeds the
per-session planner. It is the **generalization** of **Retcon Planning** — which plans a *single*
late-decision arc (dependency-ordered setup debt for one decision) — to the **full Findings Ledger**
across multiple sessions. Same Coaching Firewall; broader scope.

## The honest posture (load-bearing) — the Retcon pattern

The dependency structure an arc reasons over is **not machine-readable**:

- `apodictic.finding.v1` carries structured **`severity`** (Must-Fix / Should-Fix / Could-Fix) and
  **no** `depends_on` finding field.
- The diagnostic-state **Root-Cause map** (issue → root cause) is **markdown prose**, not data.

So this capability adopts the **Retcon pattern**: *the coach infers, the validator gates the PLAN.*
The coach **reasons** the phasing from `severity` (structured) **+** the root-cause prose (read, not
gated). The validator gates **provenance + self-consistency + firewall**, and **nothing else**.

### What `revision-arc` checks — and, precisely, what it does NOT

| Check | What it verifies | What it does NOT verify |
|---|---|---|
| **A1** invalid arc | the block + each phase object is well-formed (schema, no empty phases, the `finding_ref` pattern, `root_cause_findings` ⊆ the phase's `findings`) | — |
| **A2** provenance | every `finding_ref` resolves to a real finding in the Findings Ledger | that the finding is correctly diagnosed (the ledger owns that) |
| **A3** self-consistency | each finding sits in **exactly one** phase; a Must-Fix finding the arc **itself** labels a structural root cause is **not** parked in the last/polish phase | **that the arc's phasing matches the Ledger's TRUE causal structure.** Whether Phase 2's findings really descend from Phase 1's root cause is the **coach's trusted judgment**, never gated. A3 is internal-consistency over the arc's **own** phase order — not a causal-graph check. |
| **A4** rationale | every phase has a non-empty sequencing rationale | that the rationale's *reasoning* is correct |
| **W1** firewall drift (advisory) | a rationale that prescribes **execution** (pattern-based; reuses the retcon-plan directive heuristics + a tightened quoted-dialogue heuristic) | it's best-effort — **known false-negatives**: a rationale can prescribe execution in language the heuristics don't catch |
| **W2** orphan (advisory) | a Must-Fix Ledger finding absent from the arc | leverage-optimality of the phasing |

**The boundary, stated plainly:** the green gate means *"the plan is well-formed, every finding is
real, the arc is internally consistent, and nothing prescribes prose."* It does **not** mean *"the
dependency reasoning is correct."* That reasoning is the coach's, and it is **trusted, not gated** —
the same posture the schema `$comment` and the validator docstring state verbatim. This is the
co-presence present-vs-mentioned precedent applied to a phased arc: the validator confirms structural
integrity and provenance closure; it does not adjudicate the causal claim the phase order expresses.

This is deliberate. There is **no** structured `depends_on` field to verify against, so a validator
that *claimed* to check causal correctness would be checking a graph the author never declared —
false rigor. The increment that would change this (adding a structured finding→finding dependency
edge + a real DAG check) is a larger one, explicitly out of scope here.

## Adaptation — stateless re-plan

Like Loop Dispatch, the arc is **regenerated each run** from the current `execution.finding_states`
and **overwrites** the prior arc artifact at the project root. There is **no round/version field** —
no new state to drift. A finding in **`revised`** state has dropped out; `delivered`/`locked` findings
continue to phase-order; new findings from re-diagnosis re-phase in. The `adaptation_note` records
*when* to re-run (typically: after Phase 1 closes, re-diagnose — Phase 2 may change).

## Boundaries (don't duplicate the neighbors)

- **vs. Loop Dispatch / Session Planning** — the arc is the multi-week **calendar** (which findings,
  which phase, what order); Loop Dispatch is the per-session **decider** (the single next action). The
  arc **feeds** Loop Dispatch; it does not re-run it.
- **vs. Retcon Planning** — Retcon plans one late-decision arc; this generalizes that single arc to
  the full Ledger across sessions.
- **The `revision-arc` validator owns** sequencing-integrity + provenance closure + firewall-drift
  **only.** It does not re-judge severity, re-validate root causes, or rate leverage-optimality.
