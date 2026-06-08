# Project Addressability & State-Driven Routing — spec

**Status:** Increment 1 **built** (router fork/overlay split — see [`router-fork-overlay-split.md`](router-fork-overlay-split.md)). Increment 2 **built** (project registry + binding — schemas, `registry-check` validator, `/projects`, `/start` binding, `/new-project` registration, pre-writing minimal sidecar). Increments 3–4 remain specced below. Roadmap: `ROADMAP.md` → [Project Addressability & State-Driven Routing](../ROADMAP.md#project-addressability--state-driven-routing). No pass-engine or synthesis change.

## What exists, and the one thing that doesn't

The durable half is already built and mature. A **Core-DE project** carries, at its root (`references/output-structure.md` §Folder Architecture):

- `Diagnostic_State.md` + `Diagnostic_State.meta.json` (the machine-readable sidecar)
- `SYNTHESIS.md`, `README.md` run-archive manifest, and the Pass-10-class rolling artifacts (`Timeline.md`, `Argument_State.md`, `Series_State.md`, `State_Card`)

The sidecar *schema* carries most of what routing needs: `project`, `mode`, `next_action.key` (an **enumerated dispatch key**), `execution.phase` (gate frontier) / `allowed_next` / `pending_gate` / `finding_states`, `revision_progress`, `triage_summary`, `control_questions`. And `commands/start.md` §Resume Target (`start.md:50-60`) already maps `next_action` → workflow-to-load.

Two grounding caveats this spec must respect (both surfaced in review against the codebase):

1. **Schema ≠ populated state.** `execution.phase`/`allowed_next`/`finding_states` are empty (`""`/`{}`) until a gate runs, and `execution.pending_gate` is omitted from the template entirely (it appears only in the schema, written once a gate is pending). So routing signal from the `execution` block is *absent* for any project that hasn't reached `run_synthesis` — the router must treat empty execution state as "pre-diagnosis," not as a bug.
2. **Not every project has a sidecar.** `/new-project` and the sidecar machinery are Core-DE-centric. A **pre-writing-only project** (the pre-writing pathway writes `[Project]_Structural_Plan_[runlabel].md` and an MVP but does *not* initialize `Diagnostic_State.meta.json`) has no sidecar to derive a node from. Increment 2 must extend `/new-project` (or the pre-writing pathway) to drop a **minimal sidecar** (`project`, `mode`, `next_action: pre_writing`) at the project root so pre-writing projects are registrable and addressable. This is a named prerequisite, not a free derivation.

The missing thing is **addressability**. `output-structure.md:24` defines `{project-root}` as "the active project output context" — but *active* is **ambient**: it is whatever folder the host process is sitting in. There is no name, no index, no selector. A writer with three books cannot say "work on *Wolves of November*"; the resume gate only sees the state that happens to be underfoot. This spec adds the pointer, then promotes the sidecar from resume-fallback to primary routing input.

---

## Increment 2 — Project registry & session binding — **Built**

**Built:** schemas `apodictic.project_registry.v1` + `apodictic.project_entry.v1`; validator `scripts/registry_check.py` wired as `validate.sh registry-check` (R1 schema / R2 root+sidecar / R3 drift / R4 dup; 36/36 self-tests); commands `/projects` (new), `/start` Step 0 binding, `/new-project` registration; pre-writing minimal sidecar (`next_action: pre_writing`); `output-structure.md` §Project Registry. The decided registry home (workspace-relative `.apodictic/`) and the `readiness[]` submission signal (OQ5) are reflected below.

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
      "root": "Wolves_Of_November",
      "volume": 1,
      "mode": "diagnostic",
      "next_action": { "key": "revision_round", "description": "" },
      "last_touched": "2026-06-07",
      "series_root": null
    }
  ]
}
```

`id`/`title`/`root`/`series_root` are registry-native (the pointer + identity the ambient model can't otherwise recover). `mode`/`next_action`/`last_touched` are denormalized copies of the sidecar — present for fast listing, authoritative only in the sidecar, and copied in the sidecar's *shape* (`next_action` is the `{key, description}` object, not a bare string). The derived `lifecycle_node` (Increment 3) is **not** stored here — it is computed on read, so the validator has no stored copy to drift-check it against.

### Where the registry lives (decided)

Project roots live outside the plugin repo, and the framework must **never** write to the plugin repo or installed plugin cache (`output-structure.md:28`, `SKILL.md §Project Integration`). A `~/.apodictic/` home is rejected: in a sandboxed host `~` can resolve *into* the plugin sandbox the framework forbids writing to, so it is not a safe default. **Canonical home: a workspace-relative `.apodictic/registry.json`, discovered by walking up from the cwd** (the same way tools locate `.git`), with the workspace root — the nearest ancestor containing `.apodictic/` — as the well-defined **scan domain**. This is portable, shareable, survives host changes, and gives the rebuild a concrete place to look.

Rebuild path (well-defined): scan the workspace root recursively for `Diagnostic_State.meta.json` **and** for `[Project]_Structural_Plan_*.md` (so pre-writing-only projects, which per the caveat above carry a minimal sidecar, are found), fold each into the registry. If no `.apodictic/` ancestor exists, the session is unbound and only cold-start intake is available until `/new-project` or an explicit `/start <path>` establishes a workspace.

### Binding verbs

- **`/projects`** — list registered projects with title, lifecycle node, and last-touched; offer to bind one. Rebuilds the registry by scan if missing/stale.
- **`/start <project>`** — resolve `<project>` against the registry by `id` or title (fuzzy); if it resolves, **bind** the session (set the active project output context to its `root`, load its `Diagnostic_State.md` + sidecar) and proceed into the resume gate already in `start.md` §1. If `<project>` is an unregistered path, register-then-bind. If it resolves to nothing, fall through to cold-start intake.
- **`/new-project`** — unchanged in behavior, plus: append/update the registry entry on creation.

Binding is the explicit act that converts the *ambient* "active project output context" into a *chosen* one. Everything downstream (the resume gate, coach, gardening) already consumes that context; binding just makes it selectable.

### Validator

`validate.sh registry-check`: R1 schema valid; R2 every `root` exists and contains a `Diagnostic_State.meta.json`; R3 each denormalized field matches its sidecar (drift = WARN, sidecar wins — the cache is recomputable); R4 unique `id`s. Matches the repo's canonical-log/recomputable-pointer validator pattern (`gate-state`, `state-card-diff`).

---

## Increment 3 — State-driven dispatch

### Lifecycle node: derived, but not all from the sidecar alone

The router's destination for a bound project is a **lifecycle node**. The honest accounting (corrected in review): three nodes derive cleanly from sidecar fields, two lean on a filesystem check, and two need signal the sidecar does not store today and so carry a **named prerequisite**. The `Source` column makes this explicit.

| Node | Derived when | Source | Prerequisite |
|---|---|---|---|
| `cold` | no bound project / no sidecar | trivial | — |
| `blocked_gate` | `execution.pending_gate` present | sidecar | — (precedence over all others, per `start.md:42`) |
| `execution` | `mode == "execution"`, `active_scene_scope` set | sidecar | — |
| `diagnosed` | `revision_progress.steps_complete == 0` AND an editorial letter exists in `runs/` | sidecar + **fs glob** | letter-existence is a glob, not a field |
| `revising` | `revision_progress.steps_complete > 0` | sidecar | the `finding_states` half is **dropped** — see below |
| `pre_writing` | minimal sidecar `next_action == "pre_writing"` | sidecar | **requires the minimal-sidecar prerequisite** (Increment 2 caveat); without it, pre-writing projects can't reach this node |
| `submission` | a submission signal is live | **new signal** | `goal` is router input, never persisted, and there is no `submission` mode (`handoff-protocol.md:23`). Needs either a persisted `readiness[]` signal (the array exists in the template but is unused) or a Pass-11-artifact glob. **Open decision (OQ5).** |

Two corrections folded in from review:

- **`revising` no longer keys on `finding_states: revised`.** That state is currently **unreachable** — `revised` "is reached at a revision round (no gated phase yet)" (`run_gate.py:48`; `runner-governed-execution.md:141`). So the loop ladder cannot rely on it until a gated `revision_round` phase exists; see Increment 4's prerequisite. `revising` derives from `revision_progress.steps_complete > 0` alone.
- **`blocked_gate` takes precedence** over all others (it already does, per `start.md:42` "Resolve a pending gate first").

The headline is therefore weaker than the first draft claimed: the enum is *mostly* derived, but `pre_writing` and `submission` each carry a real prerequisite, and `diagnosed`/`revising` touch the filesystem. This is glue work, not free derivation.

### Promote `next_action` from exception to primary

Today `start.md` runs the questionnaire and treats the sidecar resume as a special pre-Q1 branch. Invert the priority for a **bound** project:

1. Bound + sidecar present → **run the contract-drift check first** → derive lifecycle node → dispatch via the existing `next_action` table (and `execution.phase`/`allowed_next` for runner-governed projects). **Artifact and Goal are read from the contract + sidecar, not re-asked.** The 2–3 questions collapse to zero; the router confirms ("Resuming *Wolves of November* — you're mid-revision with 2 Must-Fixes open. Pick up there?") rather than interrogates.
2. Cold-start (no bound project, or `cold` node) → the existing questionnaire runs unchanged.

**Contract-hash is a precondition of bind→dispatch (review fix S3).** Today the resume path reaches the contract-integrity check (`contract_hash` compared against the live contract, `run-core.md:319-328`) at pre-pass re-grounding. Promoting `next_action` to primary must *not* short-circuit that gate: a stale sidecar (e.g., the manuscript or contract was edited out-of-band) is exactly the case `run-core.md:326` exists to catch. So bind→dispatch runs the `contract_hash` check before any zero-question dispatch; on mismatch it falls back to a confirming re-ground (or cold intake), never silent resume.

**Honest scope (review fix S4).** This is additive in that the questionnaire stays the cold-start path and the existing `next_action` table is reused — but it is *not* free. New glue is required: the node→action mapping (the 8 `next_action` keys don't include `pre_writing` or a submission key), the minimal-sidecar write for pre-writing projects, and the registry schema + `registry-check` validator. "No schema change" holds only for the existing sidecar, not for the system.

### Route map as transition graph

With Increment 1's fork/overlay split in place, `intake-router-runtime.md` §6 is re-expressed as a transition graph keyed on lifecycle node: nodes are lifecycle positions, edges are forks (workflow selections), overlays decorate edges (and never appear as nodes or rows). The Artifact×Goal lookup table survives only as the **cold-start** entry map — the path for projects that have no node yet.

---

## Increment 4 — Revision-loop-as-spine

**Hard prerequisite (review fix B1): a gated `revision_round` phase must exist first.** Increment 4's ladder keys on the `locked → delivered → revised` finding lifecycle, but `revised` is currently **unreachable** — it "is reached at a revision round (no gated phase yet)" (`run_gate.py:48`; `runner-governed-execution.md:141`). Until a `revision_round` gate writes the `revised` state, the dispatcher can only see `locked`/`delivered`. So Increment 4 is blocked on defining and gating `revision_round` — an unacknowledged prerequisite in the first draft, now named and scheduled ahead of the loop work. (This dovetails with the existing Runner-Governed Execution "increment 4 future" item.)

For a project at the `revising` node, dispatch is not a single workflow load but a **"what now?" leverage decision**. Inputs, all already in the sidecar:

- `execution.finding_states` — per-finding lifecycle (`locked` → `delivered` → `revised`; the `revised` writer is the prerequisite above)
- `execution.phase` / `allowed_next` — gate frontier
- `revision_progress` — `steps_complete` / `current_step`
- `triage_summary` / `control_questions.open`

Selection (highest-leverage first):

1. `pending_gate` present → resolve it (blocking).
2. Any `locked`-but-not-`delivered` Must-Fix → that finding's diagnosis isn't in the letter yet → return to synthesis/diagnosis.
3. `delivered`-but-not-`revised` Must-Fix → the highest-leverage open fix → offer `/coach` session planning scoped to it, or an execution-mode handoff. *(Step 3 is the loop's core, and it is exactly the step the `revised` prerequisite gates.)*
4. All Must-Fix `revised`, Should-Fix open → next-tier coaching.
5. All findings `revised`, `control_questions.open == 0` → offer submission-readiness (`submission` node).

The dispatcher proposes; the writer disposes. It replaces "remember whether to type `/coach`, `/diagnose`, or `/ready`" with "the tool already knows where you are and what's worth doing next." This is the loop position and project identity that [Coaching Deepening](../ROADMAP.md#coaching-deepening) (Multi-Session Revision Arc Planning, Coaching History and Pattern Recognition) and [Collaborative Revision Coaching](../ROADMAP.md#collaborative-revision-coaching) build on but currently have no substrate for.

---

## Safety & write-location discipline

- The registry is the **only** new persistent artifact, and it lives in `$APODICTIC_HOME` — never the plugin repo or plugin cache (same rule as all rolling state).
- Binding never mutates a project's state; it only sets the active context and reads.
- Drift between registry and sidecar always resolves to the sidecar (the cache is recomputable). A lost registry is recoverable by scanning the workspace root for sidecars **and** Structural-Plan artifacts; a project is orphaned only if it lives outside any `.apodictic/` workspace — in which case `/start <path>` re-establishes it.
- The Firewall is untouched: this is routing/setup infrastructure, not content generation.

## Dependency chain — corrected (review fix N1)

The first draft framed Increments 1→2→3→4 as a single forced line. It isn't. The real graph:

- **Increment 1 (fork/overlay split) → Increment 3** only — the split is what lets §6 become a transition graph. It does **not** gate Increment 2.
- **Increment 2 (registry & binding) → Increment 3** — dispatch needs a bound project.
- **Increment 3 → Increment 4.**
- **Increments 1 and 2 are independent** and can be built in parallel or either order.
- **Increment 4 additionally requires a gated `revision_round` phase** (the `revised`-state writer, B1) — a prerequisite outside this chain entirely.

So: `{1, 2} → 3 → 4`, with 4 also waiting on `revision_round`. The ROADMAP entry's "forced dependency chain" wording is corrected to match.

## Open questions (for review)

1. ~~Registry home~~ **Decided:** workspace-relative `.apodictic/registry.json` (see §Where the registry lives). `~/.apodictic` rejected (sandbox-unsafe).
2. ~~`/projects` vs. overloading `/start`~~ **Decided:** keep both, split by role. `/start` is the router and branches on registry size (0 → cold intake; 1 → bind+resume; >1 → list-and-pick); `/projects` is a *management-only* surface (list with lifecycle nodes, rename, drop stale entries) and is never required for the core flow. No mandatory second verb; routing on `/start`, housekeeping on `/projects`.
3. **Series.** A `series_root` project groups volumes (`Series_State.md` already exists at the series root). Should `/projects` show series as a parent with volume children, or flat with a series tag? Deferred to Increment 2 detailed design.
4. **Lifecycle-node derivation ownership.** Derive on read (router computes each session) vs. persist `lifecycle_node` at write time. Spec assumes derive-on-read (no schema change); persisting would speed listing but adds a write path and a drift surface. The registry deliberately does **not** store `lifecycle_node` (so `registry-check` R3 has nothing spurious to drift-check).
5. ~~Submission signal~~ **Decided (a):** populate the existing-but-unused `readiness[]` sidecar array when submission readiness enters scope (Pass 11 / `/ready` / submission-readiness workflow) — the smallest write, no schema change, no invented `submission` mode. The `submission` node derives when `readiness[]` is non-empty and its latest entry is not "delivered." Globbing for Pass-11 artifacts (b) and persisting `goal` (c) rejected as brittle / drift-prone respectively.

---

*This file is a design spec. If adopted, the runtime changes land in `commands/start.md` (binding + dispatch promotion), `commands/new-project.md` (registry write), a new `schemas/apodictic.project_registry.v1.schema.json` + `validate.sh registry-check`, and `intake-router-runtime.md` §6 (transition-graph re-expression).*
