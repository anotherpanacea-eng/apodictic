# Multi-Session Revision Arc Planning (coaching track)

**Status:** v1 (Increment 1 — the full-Ledger arc above per-session Loop Dispatch)
**Trigger:** `/coach` → Arc Planning mode. Use when a returning author with a **completed diagnosis**
(a Findings Ledger + `Diagnostic_State.md`) wants a multi-week revision **strategy** — not "what do I
do in *this* session?" (that's Loop Dispatch / Session Planning) but "what's the *arc* across the next
several weeks, and in what order?"
**Inherits:** the Coaching Firewall (`revision-coach/SKILL.md §The Coaching Firewall`) + the core
Firewall (`core-editor/SKILL.md §The Firewall`).

---

## Purpose

Per-session planning answers *"what's the highest-leverage thing to do next?"* — the built **Loop
Dispatch** (`revision-coach/SKILL.md §Loop Dispatch`). **Arc Planning** answers the layer **above**:
*"what's the multi-week strategy?"* — a phased revision arc:

- **Phase 1 — structural root causes:** the Must-Fix findings the diagnosis identifies as the
  structural roots (the controlling idea, the spine, the load-bearing decision).
- **Phase 2 — downstream consequences:** the findings whose resolution depends on Phase 1 closing
  (consequences of the root cause; Should-Fix issues gated on the structural fix).
- **Phase 3 — polish:** Could-Fix / line-level work with no upstream dependency.

The arc is the **calendar** that sequences findings into per-session work. Each phase feeds the
per-session planner; **the arc does not re-run per-session Loop Dispatch.** It also **generalizes
Retcon Planning's** single-decision arc (one late decision → dependency-ordered setup debt) to the
**full Findings Ledger** across multiple sessions.

**The Firewall line (what makes this APODICTIC, not a writing assistant):** the arc says *which
findings, in which phase, in what order, and why* — it **SEQUENCES; it never prescribes execution**.
A phase rationale that drifts into "rewrite scene X so that …" or "add a scene where …" is a firewall
breach (the validator's advisory W1). *Sequence the findings; the author writes the tissue.*

---

## The honest posture (read this before building an arc)

This is the **Retcon pattern**: the coach infers, the validator gates the PLAN — and it is
load-bearing here because the dependency structure the arc reasons over is **not machine-readable**.

- `apodictic.finding.v1` carries structured **`severity`** (Must-Fix / Should-Fix / Could-Fix — the
  leverage axis) — and **nothing else structural**. There is no `depends_on` finding field.
- The diagnostic-state **Root-Cause map** (issue → root cause) is a **markdown table**, prose the
  coach reads — not data.

So the coach **reasons** the phasing from `severity` (structured) **+** the root-cause prose (read,
not gated), and the validator gates only **provenance + self-consistency + firewall**:

> **What the validator checks** — that every referenced finding is real (A2), that the arc is
> internally consistent (A3: each finding in exactly one phase; a Must-Fix finding the arc *itself*
> labels a structural root cause is not parked in the polish phase), that every phase has a
> sequencing rationale (A4), and that no phase prescribes execution (W1).
>
> **What the validator does NOT check** — whether the arc's phasing matches the Ledger's *true*
> causal structure. Whether Phase 2's findings *really* descend from Phase 1's root cause is the
> **coach's trusted judgment**, not a gated fact. A3 is a self-consistency check over the arc's own
> phase ordering, **never** a causal-graph verification. (The co-presence present-vs-mentioned
> precedent: the validator confirms the plan is well-formed and provenance-closed; it does not
> adjudicate the dependency reasoning.)

This boundary is stated identically in the schema `$comment` and the validator docstring. Don't
read the green gate as "the dependency reasoning is correct" — it means "the plan is well-formed,
every finding is real, and nothing prescribes prose."

---

## The artifact: `[Project]_Revision_Arc_[runlabel].md`

One **`apodictic.revision_arc.v1`** block per manuscript — the machine-checkable spine:

```markdown
<!-- apodictic:revision_arc
{"schema":"apodictic.revision_arc.v1",
 "phases":[
   {"phase_label":"Structural root causes",
    "findings":["F-CI-01"],
    "root_cause_findings":["F-CI-01"],
    "rationale":"Phase 1 must settle the Must-Fix controlling-idea root cause before Phase 2 begins."},
   {"phase_label":"Downstream consequences",
    "findings":["F-PT-02","F-CH-03"],
    "rationale":"Sequenced after Phase 1: both descend from the controlling-idea fix (the coach's read)."},
   {"phase_label":"Polish",
    "findings":["F-LN-04"],
    "rationale":"Could-Fix line-level work, no upstream dependency, sequenced last."}],
 "adaptation_note":"Stateless re-plan: regenerated each run from current finding_states."}
-->
```

- **`phases`** is an **ordered list (≥1)** — phase order *is* the dependency expression. It is **not
  a fixed 3-enum**: a 2-phase or 4-phase arc is fine (`phase_label` is free text). No empty phases —
  every phase has ≥1 `findings`.
- **`findings`** — the finding.v1 ids (`F-<ORIGIN>-<NN>`) the phase sequences. Every ref must resolve
  to a real Ledger finding (A2). There is **no declared cross-phase edge field**; a dependency the
  coach wants to name lives in the `rationale` prose (trusted, not data).
- **`root_cause_findings`** (optional) — the subset of *this phase's* `findings` the arc labels
  structural root causes. This is what the A3 leverage check reads: a Must-Fix root cause must not be
  parked in the last phase.
- **`rationale`** — the **sequencing** "why" (non-empty, A4). A SEQUENCING rationale ("Phase 1 must
  close X before Phase 2"), never an execution prescription.
- **`adaptation_note`** — how the arc adapts (see below).

Field set canonical in `schemas/apodictic.revision_arc.v1.schema.json`. Worked example:
`core-editor/references/example-revision-arc.md`.

---

## Adaptation — stateless re-plan (no new state to drift)

The arc is a **live plan tied to loop position**, **not** a frozen document and **not** a persisted,
versioned, diffed artifact. Like Loop Dispatch, **it is regenerated each run from the current
`execution.finding_states`** and **overwrites** the prior arc artifact at the project root. There is
**no round/version field** — re-running re-reads the state and re-phases:

- A finding in **`revised`** state has dropped out (it's resolved). `delivered`/`locked` findings
  continue to phase-order.
- New findings surfaced by re-diagnosis re-phase into the arc.

The `adaptation_note` tells the author *when* to re-run — typically: **after Phase 1 closes,
re-diagnose; Phase 2 may change** (settling a root cause can retire or reshape its consequences).

---

## Protocol

1. **Read the diagnostic state.** `finding_states` (which findings are `locked`/`delivered`/
   `revised`), `severity` per finding, the **Root-Cause map**, `triage_summary`, `revision_progress`
   — all already on disk (`Diagnostic_State.meta.json` + the Findings Ledger). Do **not** re-diagnose
   or invent findings; the arc consumes the diagnosis (the Delegation Principle).
2. **Assign phases** by leverage + root-cause position:
   - **Phase 1** = the Must-Fix findings the diagnosis identifies as structural *root causes* (record
     them in `root_cause_findings`).
   - **Phase 2** = their downstream consequences (findings whose root cause is a Phase-1 item, or
     Should-Fix issues gated on a Phase-1 fix — the coach's read of the root-cause prose).
   - **Phase 3** = polish (Could-Fix / line-level, no upstream dependency).
   - A finding with an unresolved upstream dependency cannot precede it — but that ordering is the
     coach's *reasoning*; the validator only checks the arc is internally consistent with its own
     phase order.
3. **Render the arc** — phases, the findings in each, a **sequencing** rationale per phase, and the
   `adaptation_note` (the re-diagnosis triggers).
4. **Firewall pass** — every rationale SEQUENCES; none prescribes the aesthetic material that
   resolves a finding. (Plan the phasing; the author writes the tissue.)
5. **Gate** with `scripts/validate.sh revision-arc <run_folder>` (`--strict` for CI), then hand each
   phase off to per-session **Loop Dispatch / Session Planning**.

---

## Session / Arc boundary (don't duplicate the per-session planner)

- **Arc Planning** (this mode) = the multi-week **calendar**: which findings, which phase, what order.
  It runs *once* over the full Ledger and is regenerated as phases close.
- **Loop Dispatch / Session Planning** (`revision-coach/SKILL.md §Loop Dispatch`, §Mode 1) = the
  per-session **decider**: given the current `finding_states`, what's the single highest-leverage
  action *next*. The arc **feeds** this; it does not re-run it.
- **Retcon Planning** (`retcon-planning.md`) = a *single* late-decision arc (dependency-ordered setup
  debt for one decision). Arc Planning **generalizes** that to the full Findings Ledger across
  sessions — same firewall, broader scope.

---

## Mechanical check

`scripts/validate.sh revision-arc <run_folder>` (globs `*_Revision_Arc_*.md` + the paired
`*_Findings_Ledger_*.md`): **A1** invalid arc (schema + nested phase shape — no empty phases, the
`finding_ref` pattern, `root_cause_findings` ⊆ the phase's `findings`); **A2** provenance closure
(every `finding_ref` resolves to a real Ledger finding); **A3 self-consistency ONLY** (each finding in
exactly one phase; a Must-Fix finding the arc labels a structural root cause is not parked in the last
phase — **not** a true-causal-graph check); **A4** non-empty phase rationale; advisory **W1** firewall
drift (a rationale that prescribes execution — reuses the retcon-plan directive heuristics, with a
tightened quoted-dialogue heuristic; best-effort, ERROR under `--strict`); advisory **W2** orphan (a
Must-Fix Ledger finding absent from the arc; ERROR under `--strict`). The validator **owns
sequencing-integrity + provenance closure + firewall-drift only** — it does not re-judge severity,
re-validate root causes, or rate leverage-optimality. Ownership boundary + lineage:
[`docs/multi-session-arc-planning.md`](../../../docs/multi-session-arc-planning.md).
