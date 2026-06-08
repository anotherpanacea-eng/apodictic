# Project Addressability & State-Driven Routing — spec

**Status:** Spec (not yet built). Roadmap: `ROADMAP.md` → [Project Addressability & State-Driven Routing](../ROADMAP.md#project-addressability--state-driven-routing). Covers Increments 2–4; Increment 1 (router fork/overlay split) is specced separately in [`router-fork-overlay-split.md`](router-fork-overlay-split.md). Touches `commands/start.md`, `commands/new-project.md`, a new registry artifact + schema, `references/output-structure.md`, and `references/intake-router-runtime.md`. No pass-engine or synthesis change.

## What exists, and the one thing that doesn't

The durable half is already built and mature. Every project carries, at its root (`references/output-structure.md` §Folder Architecture):

- `Diagnostic_State.md` + `Diagnostic_State.meta.json` (the machine-readable sidecar)
- `SYNTHESIS.md`, `README.md` run-archive manifest, and the Pass-10-class rolling artifacts (`Timeline.md`, `Argument_State.md`, `Series_State.md`, `State_Card`)

The sidecar already carries nearly everything routing needs: `project`, `mode`, `next_action.key` (an **enumerated dispatch key**), `execution.phase` (gate frontier) / `allowed_next` / `pending_gate` / `finding_states`, `revision_progress`, `triage_summary`, `control_questions`. And `commands/start.md` §Resume Target already maps `next_action` → workflow-to-load.

The missing thing is **addressability**. `output-structure.md:24` defines `{project-root}` as "the active project output context" — but *active* is **ambient**: it is whatever folder the host process is sitting in. There is no name, no index, no selector. A writer with three books cannot say "work on *Wolves of November*"; the resume gate only sees the state that happens to be underfoot. This spec adds the pointer, then promotes the sidecar from resume-fallback to primary routing input.

---

## Increment 2 — Project registry & session binding

### Registry as a recomputable cache over canonical sidecars

The design mirrors Runner-Governed Execution's discipline: **the per-project sidecars are canonical; the registry is a recomputable cache.** A project root's `Diagnostic_State.meta.json` already self-identifies (`project`, `mode`, `next_action`, `last_session.date`). The registry is a denormalized index built by folding those sidecars; if it is lost or stale, it is rebuilt by scanning. No fact lives only in the registry.

`apodictic.project_registry.v1`:

```json
{
  "schema": "apodictic.project_registry.v1",
  "updated": "2026-06-08",
  "projects": [
    {
      "id": "wolves-of-november",
      "title": "Wolves of November",
      "root": "/abs/path/to/Wolves_Of_November",
      "volume": 1,
      "lifecycle_node": "revising",
      "mode": "diagnostic",
      "next_action": "revision_round",
      "last_touched": "2026-06-07",
      "series_root": null
    }
  ]
}
```

Every field except `id`/`title`/`root` is a denormalized copy of the project's sidecar — present for fast listing, authoritative only in the sidecar. `root` is the only registry-native fact (the pointer the ambient model can't otherwise recover).

### Where the registry lives (decision needed — see Open Questions)

Project roots live outside the plugin repo, and the framework must **never** write to the plugin repo or installed plugin cache (`output-structure.md`, `SKILL.md §Project Integration`). The registry therefore needs a stable, user-owned home. Spec'd default: `$APODICTIC_HOME/registry.json`, `$APODICTIC_HOME` defaulting to `~/.apodictic/`. Rebuild path: scan a configured workspace root (or the parents of known roots) for `Diagnostic_State.meta.json` and fold each into the registry. The home-dir default is host-dependent; alternatives in Open Questions.

### Binding verbs

- **`/projects`** — list registered projects with title, lifecycle node, and last-touched; offer to bind one. Rebuilds the registry by scan if missing/stale.
- **`/start <project>`** — resolve `<project>` against the registry by `id` or title (fuzzy); if it resolves, **bind** the session (set the active project output context to its `root`, load its `Diagnostic_State.md` + sidecar) and proceed into the resume gate already in `start.md` §1. If `<project>` is an unregistered path, register-then-bind. If it resolves to nothing, fall through to cold-start intake.
- **`/new-project`** — unchanged in behavior, plus: append/update the registry entry on creation.

Binding is the explicit act that converts the *ambient* "active project output context" into a *chosen* one. Everything downstream (the resume gate, coach, gardening) already consumes that context; binding just makes it selectable.

### Validator

`validate.sh registry-check`: R1 schema valid; R2 every `root` exists and contains a `Diagnostic_State.meta.json`; R3 each denormalized field matches its sidecar (drift = WARN, sidecar wins — the cache is recomputable); R4 unique `id`s. Matches the repo's canonical-log/recomputable-pointer validator pattern (`gate-state`, `state-card-diff`).

---

## Increment 3 — State-driven dispatch

### Lifecycle node: a derived enum, not a new stored field

The router's destination for a bound project is a **lifecycle node** *derived* from existing sidecar fields — nothing new is persisted:

| Node | Derived when | Primary next action |
|---|---|---|
| `cold` | no bound project / fresh `/new-project` | run intake questionnaire |
| `pre_writing` | Structural_Plan exists, no editorial letter / Findings Ledger | continue pre-writing pathway |
| `diagnosed` | editorial letter exists, `revision_progress.steps_complete == 0` | offer `/coach` |
| `revising` | `revision_progress.steps_complete > 0` OR `finding_states` has `delivered`/`revised` | resume revision loop (Increment 4) |
| `execution` | `mode == "execution"` (active `active_scene_scope`) | re-entry delta check / keep working |
| `submission` | goal=submit in scope OR Pass 11 in resolved set | submission-readiness / triage |
| `blocked_gate` | `execution.pending_gate` present | resolve the pending gate first |

`blocked_gate` takes precedence over all others (it already does, per `start.md` §Resume Target "Resolve a pending gate first").

### Promote `next_action` from exception to primary

Today `start.md` runs the questionnaire and treats the sidecar resume as a special pre-Q1 branch. Invert the priority for a **bound** project:

1. Bound + sidecar present → derive lifecycle node → dispatch via the existing `next_action` table (and `execution.phase`/`allowed_next` for runner-governed projects). **Artifact and Goal are read from the contract + sidecar, not re-asked.** The 2–3 questions collapse to zero; the router confirms ("Resuming *Wolves of November* — you're mid-revision with 2 Must-Fixes open. Pick up there?") rather than interrogates.
2. Cold-start (no bound project, or `cold` node) → the existing questionnaire runs unchanged.

This is additive: the questionnaire stays the cold-start path; the sidecar dispatch table already exists; Increment 3 only changes which path is primary when a project is bound.

### Route map as transition graph

With Increment 1's fork/overlay split in place, `intake-router-runtime.md` §6 is re-expressed as a transition graph keyed on lifecycle node: nodes are lifecycle positions, edges are forks (workflow selections), overlays decorate edges (and never appear as nodes or rows). The Artifact×Goal lookup table survives only as the **cold-start** entry map — the path for projects that have no node yet.

---

## Increment 4 — Revision-loop-as-spine

For a project at the `revising` node, dispatch is not a single workflow load but a **"what now?" leverage decision**. Inputs, all already in the sidecar:

- `execution.finding_states` — per-finding lifecycle (`locked` → `delivered` → `revised`)
- `execution.phase` / `allowed_next` — gate frontier
- `revision_progress` — `steps_complete` / `current_step`
- `triage_summary` / `control_questions.open`

Selection (highest-leverage first):

1. `pending_gate` present → resolve it (blocking).
2. Any `locked`-but-not-`delivered` Must-Fix → that finding's diagnosis isn't in the letter yet → return to synthesis/diagnosis.
3. `delivered`-but-not-`revised` Must-Fix → the highest-leverage open fix → offer `/coach` session planning scoped to it, or an execution-mode handoff.
4. All Must-Fix `revised`, Should-Fix open → next-tier coaching.
5. All findings `revised`, `control_questions.open == 0` → offer submission-readiness (`submission` node).

The dispatcher proposes; the writer disposes. It replaces "remember whether to type `/coach`, `/diagnose`, or `/ready`" with "the tool already knows where you are and what's worth doing next." This is the loop position and project identity that [Coaching Deepening](../ROADMAP.md#coaching-deepening) (Multi-Session Revision Arc Planning, Coaching History and Pattern Recognition) and [Collaborative Revision Coaching](../ROADMAP.md#collaborative-revision-coaching) build on but currently have no substrate for.

---

## Safety & write-location discipline

- The registry is the **only** new persistent artifact, and it lives in `$APODICTIC_HOME` — never the plugin repo or plugin cache (same rule as all rolling state).
- Binding never mutates a project's state; it only sets the active context and reads.
- Drift between registry and sidecar always resolves to the sidecar (the cache is recomputable). A lost registry is a no-op recoverable by scan — no project is ever orphaned by registry loss.
- The Firewall is untouched: this is routing/setup infrastructure, not content generation.

## Open questions (for review)

1. **Registry home.** `~/.apodictic/registry.json` is host-dependent (the LLM may run where `~` is the plugin sandbox, not the user's home). Alternatives: (a) a workspace-relative `.apodictic/registry.json` discovered by walking up from cwd (portable, shareable, survives host changes); (b) pure scan-on-demand with no persisted registry (slower listing, zero new artifact, zero drift). Recommendation: **(a)** as canonical with scan as rebuild — but this is the maintainer's call.
2. **`/projects` vs. overloading `/start`.** Is a dedicated listing verb worth it, or should `/start` with no argument list-and-bind? Recommendation: keep both; `/start` no-arg lists when >1 project is registered.
3. **Series.** A `series_root` project groups volumes (`Series_State.md` already exists at the series root). Should `/projects` show series as a parent with volume children, or flat with a series tag? Deferred to Increment 2 detailed design.
4. **Lifecycle-node derivation ownership.** Derive on read (router computes from sidecar each session) vs. persist `lifecycle_node` in the sidecar (write-time). Spec assumes derive-on-read (no schema change); persisting would be faster listing but adds a write path and a drift surface.

---

*This file is a design spec. If adopted, the runtime changes land in `commands/start.md` (binding + dispatch promotion), `commands/new-project.md` (registry write), a new `schemas/apodictic.project_registry.v1.schema.json` + `validate.sh registry-check`, and `intake-router-runtime.md` §6 (transition-graph re-expression).*
