# Project Addressability & State-Driven Routing — spec

**Status:** Increments 1–3 **built**. Increment 1 (router fork/overlay split — see [`router-fork-overlay-split.md`](router-fork-overlay-split.md)). Increment 2 (project registry + binding — schemas, `registry-check`, `/projects`, `/start` binding, `/new-project` registration, pre-writing minimal sidecar). Increment 3 (state-driven dispatch — `lifecycle-node` validator, `start.md` Step 0.5 `next_action`-as-primary + scoped contract-hash precondition, `§6` lifecycle transition table, `readiness[]` population). Increment 4 **built** — 4b (the "what now?" loop dispatcher) and 4a (the gated `revision_round` phase, `docs/revision-round-gate.md`) are both built. Roadmap: `ROADMAP.md` → [Project Addressability & State-Driven Routing](../ROADMAP.md#project-addressability--state-driven-routing). No pass-engine or synthesis change.

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

## Increment 3 — State-driven dispatch — **Built**

**Built:** `lifecycle-node` validator (`scripts/lifecycle_node.py` + `validate.sh lifecycle-node`, 36 → 37, mirrored to root `scripts/`, self-tests including the B1 fresh-project case); `start.md` Step 0.5 promoting `next_action` to primary dispatch with the scoped contract-hash precondition and the two-option Resume/Start-fresh prompt; `intake-router-runtime.md` §6 lifecycle transition table + Table A reframed as the cold-start entry map; `submission-readiness.md` `readiness[]` sidecar mirror for the `submission` node.

### Lifecycle node: a total derivation by precedence

The router's destination for a bound project is a **lifecycle node**, derived from sidecar fields by a single authoritative precedence (**first match wins**). The set is **total** — every bound project resolves to exactly one node — with `diagnosing` as the catch-all default.

**Precedence (first match wins):** `cold` → `blocked_gate` → `execution` → `pre_writing` → `submission` → `revising` → `diagnosed` → `diagnosing`.

| Node | Derived when (given the precedence above) | Source | Dispatch |
|---|---|---|---|
| `cold` | no bound project / no sidecar | trivial | cold-start intake (Table A) |
| `blocked_gate` | `execution.pending_gate` present | sidecar | resolve the pending gate first (`start.md:42`) |
| `execution` | `mode == "execution"` (with `active_scene_scope`) | sidecar | re-entry delta check / keep working (`handoff-protocol.md`) |
| `pre_writing` | `next_action.key == "pre_writing"` | sidecar | `pre-writing-pathway/SKILL.md` (Increment 2 dispatch row) |
| `submission` | `readiness[]` non-empty (a submission-readiness assessment has been recorded; entries are `apodictic.readiness.v1` = dimension/verdict/rationale — there is no status field, so presence is the signal) | sidecar | submission-readiness / triage |
| `revising` | `revision_progress.steps_complete > 0` | sidecar | the stored `next_action` (`revision_round`→`state-lifecycle.md` or `coaching`→`revision-coach`); Increment 4 enriches the *choice* among sub-steps |
| `diagnosed` | a synthesis/editorial letter exists for the project — `SYNTHESIS.md` at the project root OR `runs/*/*_Synthesis_*.md` | sidecar + **fs glob** | offer `/coach` |
| `diagnosing` | **default** — `mode == "diagnostic"`, nothing above matched (intake done, passes/synthesis in progress, no letter yet) | sidecar | the stored `next_action` (`run_passes`/`run_synthesis`/`run_audits`) |

Three corrections folded in from the Increment-3 spec review:

- **`diagnosing` is the total-making default (Blocker B1).** The single most common state — intake complete, passes underway, no editorial letter yet — matched *no* node in the first draft, leaving dispatch undefined. `diagnosing` catches it and dispatches via the stored `next_action`. It also restores the never-diagnosed (`diagnosing`, pre-letter) vs. diagnosed (`diagnosed`, letter exists) split.
- **Single authoritative precedence (S1).** The earlier draft's table order and build-plan order disagreed; the precedence line above is now the one source of truth. (`diagnosed` and `revising` are mutually exclusive on `steps_complete`, so their relative order is moot, but the list is stated once regardless.)
- **`revising` does not key on `finding_states: revised`** — that state is unreachable until a gated `revision_round` phase exists (`run_gate.py:48`; `runner-governed-execution.md:141`). `revising` derives from `steps_complete > 0` alone and dispatches to the revision workflow via the stored `next_action`; Increment 4's leverage ladder upgrades the choice among sub-steps.

`diagnosed` is the only node needing a filesystem check (the editorial-letter glob). When the glob can't run (no run folder available), derivation falls through to `diagnosing` — the safe pre-letter default.

### Promote `next_action` from exception to primary

Today `start.md` runs the questionnaire and treats the sidecar resume as a special pre-Q1 branch. Invert the priority for a **bound** project:

1. Bound + sidecar present → **run the contract-drift check first** → derive lifecycle node → dispatch via the existing `next_action` table (and `execution.phase`/`allowed_next` for runner-governed projects). **Artifact and Goal are read from the contract + sidecar, not re-asked.** The 2–3 questions collapse to zero; the router confirms ("Resuming *Wolves of November* — you're mid-revision with 2 Must-Fixes open. Pick up there?") rather than interrogates.
2. Cold-start (no bound project, or `cold` node) → the existing questionnaire runs unchanged.

**Contract-hash precondition (scoped — review fixes S2/S3).** Promoting `next_action` to primary must not short-circuit the contract-integrity gate (`contract_hash` vs. the live contract, `run-core.md:319-328`) — a stale sidecar from an out-of-band manuscript/contract edit is exactly what `run-core.md:326` catches. But the gate is **scoped to contract-bearing state**: it runs only when the sidecar carries a non-empty `contract_hash` (set at intake, `run-core.md:114`). Pre-contract states — `pre_writing`, and a freshly-intaken `diagnosing` before the contract is saved (`contract_hash: ""`, template :55) — carry no hash and **skip** the check; an absent/empty hash is a skip, never a failure. When a hash *is* present, `/start` locates the contract by globbing the newest `runs/*/[Project]_Contract_*.md` (the path is not a sidecar field — same glob as the letter) and runs `validate.sh contract-check <file> <hash>`; on mismatch it falls back to a confirming re-ground or cold intake, never silent resume.

**Honest scope (review fix S4).** This is additive in that the questionnaire stays the cold-start path and the existing `next_action` table is reused — but it is *not* free. New glue is required: the node→action mapping (the 8 `next_action` keys don't include `pre_writing` or a submission key), the minimal-sidecar write for pre-writing projects, and the registry schema + `registry-check` validator. "No schema change" holds only for the existing sidecar, not for the system.

### Route map as transition graph

With Increment 1's fork/overlay split in place, `intake-router-runtime.md` §6 is re-expressed as a transition graph keyed on lifecycle node: nodes are lifecycle positions, edges are forks (workflow selections), overlays decorate edges (and never appear as nodes or rows). The Artifact×Goal lookup table survives only as the **cold-start** entry map — the path for projects that have no node yet.

### Increment 3 — build plan

**New: `lifecycle-node` validator.** A Python validator `lifecycle-node <sidecar> [run_folder]` that computes the derived node by the authoritative precedence above (`cold → blocked_gate → execution → pre_writing → submission → revising → diagnosed → diagnosing`) and self-tests every row — including the fresh/mid-pass case (B1) that must resolve to `diagnosing`, not undefined. It is the *tested primitive* `/start`, `/projects` ("where it stands"), and Increment 4's dispatcher all read from, rather than re-deriving in prose. The `diagnosed` letter is detected relative to the sidecar's own project root (`SYNTHESIS.md`, or `runs/*/*_Synthesis_*.md`); an optional `run_folder` arg is an extra search location. When no synthesis is found anywhere, derivation falls through to `diagnosing` — the safe pre-letter default (S4). Wired into `validate.sh` (case + command list + AGG_VALIDATORS + count 36 → 37) **and the root `scripts/` mirror** (the Increment-2 lesson — CI runs the root copy). No new schema: it reads the existing sidecar.

**`start.md` (the core change).** Promote `next_action` from the resume *exception* to the *primary* dispatch for a bound project: Step 0 binds (Increment 2) → scoped contract-hash precondition (locate the contract via the newest `runs/*/[Project]_Contract_*.md` glob; skip when no hash) → derive lifecycle node → dispatch via the `next_action` table. Bound, in-progress projects collapse Q1/Q2 to a **two-option** prompt — **"Resume here / Start fresh (full intake)"** — reusing the existing resume-gate choices (`start.md:40-41,48`), never a bare yes/no that traps a writer whose intent changed (S5). Cold start runs the questionnaire unchanged; `blocked_gate` keeps precedence.

**`intake-router-runtime.md` §6.** Add a **lifecycle transition table** (node → primary next action → workflow loaded) above Table A, and reframe Table A explicitly as the *cold-start entry map* (the path for projects with no node yet). A bound project's **overlays still come from Table B** and are not re-derived per node (N1 — prevents reintroducing the cross-product drift Increment 1 removed). Table B is otherwise unchanged.

**`readiness[]` population (submission node).** `submission-readiness.md` / `pass-11.md` append a `readiness` entry to the sidecar when the readiness workflow runs, so the `submission` node derives from real state (OQ5(a)). Small and additive.

**Status/docs.** Spec Increment 3 → Built; ROADMAP; changelog fragment (37 validators).

**Not in scope:** the `revising` loop *ladder* and the `revised` finding-state — those are Increment 4 and its `revision_round` prerequisite.

---

## Increment 4 — Revision-loop-as-spine — **Built**

**Built (4b):** the "what now?" loop dispatcher — `revision-coach/SKILL.md` §Loop Dispatch (the leverage ladder reading `finding_states` + resolved markers + `revision_progress`/`control_questions`, with the stalled off-ramp and the source-of-truth rule) and `start.md`'s `revising` dispatch wired to it. **Built (4a):** the gated `revision_round` phase that folds `revised` into the sidecar for runner-governed projects, marking only the resolved subset, with the direct write retained for non-governed projects — `docs/revision-round-gate.md`.

**The `revised` finding-state and how Increment 4 handles it.** The ladder below references the `locked → delivered → revised` lifecycle. `revised` is **not written by the gate fold** — `_PHASE_FINDING_STATE` (`run_gate.py:49`) stops at `delivered`. But it is *not* unreachable: the revision-round protocol writes `execution.finding_states[<id>] = "revised"` **directly** into the sidecar today (`state-lifecycle.md:120`), and `finding-trace` E5 reads it (`finding_trace.py:245`). The **canonical source** of "which findings were revised" is the `<!-- resolved: F-… -->` markers in the revision report (what `finding-trace` parses, and what `state-lifecycle.md` uses to set the field). So the dispatcher reads `finding_states.revised` (present today) or those markers — no gate needed. A gated `revision_round` phase would make the gate *engine* the writer (folding the markers into the sidecar) — a *hardening*, not a precondition. This is the build split below.

For a project at the `revising` node, dispatch is not a single workflow load but a **"what now?" leverage decision**. Inputs, all already in the sidecar:

- `execution.finding_states` — per-finding lifecycle (`locked` → `delivered` → `revised`)
- the `<!-- resolved: F-… -->` markers in the latest revision report
- `execution.phase` / `allowed_next` — gate frontier; `revision_progress` (`steps_complete` / `current_step`); `triage_summary`; `control_questions.open`; the Coaching Log (for stall detection)

**Source of truth for "revised" (one rule).** Read `finding_states[<id>] == "revised"` when present — written by the `revision_round` gate for runner-governed projects (Increment 4a, `docs/revision-round-gate.md`) or directly by the revision round for non-governed projects (`state-lifecycle.md`); otherwise fall back to the report's resolved markers. The two should agree — `finding-trace` E5/W3 reconciles them — so prefer the sidecar field and treat a marker-without-field as "revised, sidecar not yet updated."

Selection (highest-leverage first):

1. `pending_gate` present → resolve it (blocking).
2. Any `locked`-but-not-`delivered` Must-Fix → that finding's diagnosis isn't in the letter yet → return to synthesis/diagnosis.
3. `delivered`-but-not-`revised` Must-Fix → the highest-leverage open fix → offer `/coach` session planning scoped to it, or an execution-mode handoff. *(Step 3 is the loop's core; the `revised` discriminator comes from the source-of-truth rule above — available today, not gated on 4a.)*
4. All Must-Fix `revised`, Should-Fix open → next-tier coaching.
5. All findings `revised`, `control_questions.open == 0` → offer submission-readiness (`submission` node).

**Stalled-revision off-ramp.** If a `delivered` Must-Fix has seen no progress across multiple sessions (Coaching Log) and still carries no resolved marker, step 3 must not re-offer the same `/coach` step indefinitely — surface "this finding has stalled: consider an execution-mode handoff, or set it aside, recording the decision in the Coaching Log" so the loop has a terminal move. (There is no engine-level "declined" finding state today — `finding_states` is `locked`/`delivered`/`revised` only — so the Coaching Log note is the durable record, not an auto-suppression of re-flagging.)

The dispatcher proposes; the writer disposes. It replaces "remember whether to type `/coach`, `/diagnose`, or `/ready`" with "the tool already knows where you are and what's worth doing next." This is the loop position and project identity that [Coaching Deepening](../ROADMAP.md#coaching-deepening) (Multi-Session Revision Arc Planning, Coaching History and Pattern Recognition) and [Collaborative Revision Coaching](../ROADMAP.md#collaborative-revision-coaching) build on but currently have no substrate for.

### Increment 4 — build plan (split by risk)

**Layer 4b — the "what now?" loop dispatcher (build now).** The increment's user-facing value. At the `revising` node, `/start` (Step 0.5) and `/coach` propose the next leverage action by the ladder above, reading: `finding_states` (`locked`/`delivered`, written today), the **`<!-- resolved: F-… -->` markers in the latest revision report** (the canonical "which findings were revised" — read directly), `revision_progress`, `triage_summary`, and `control_questions.open`. This is prose/logic in `start.md` (the `revising` dispatch) and `revision-coach/SKILL.md` (the ladder); no gate-engine change. The ladder's `delivered`-but-not-`revised` step (step 3) keys on the source-of-truth rule above, so it works without 4a. **Precedence with Increment 3:** at the `revising` node the ladder is the *decider*; the stored `next_action` is its default/output (used when the ladder is indeterminate), not a competing authority — Increment 3 shipped `next_action` as the dispatch, and 4b refines the choice among revision sub-steps.

**Layer 4a — gated `revision_round` phase (the canonical `revised` writer; follow-up).** Adds a third phase to `execution-gates.v1.json` (`revision_round`, `allowed_next: ["run_synthesis"]`, a revision-report artifact_key + attestations + a `finding-trace` check), maps `_PHASE_FINDING_STATE["revision_round"] = "revised"` in `run_gate.py`, and — the delicate part — marks **only the resolved subset** of findings `revised` (the report's `<!-- resolved: F-… -->` ids), unlike the existing phases that mark *all* ledger findings. That is real surgery on the runner-governed-execution fold (selective per-finding state, new manifest phase + artifact_key, `run_gate.py` self-tests, the `--check-all` gate-state canonical run-folder, the degradation path). **Critically, 4a must also *remove* the revision round's direct write of `finding_states[<id>] = "revised"` (`state-lifecycle.md:120`)** when it makes the gate the writer — otherwise `gate --check-state`'s `pointer == fold` invariant (`run_gate.py:662`) fails, because the fold recomputes `finding_states` only from gate-event deltas. Reconciling that direct-write-vs-fold contradiction under the pointer==fold invariant — not just "it balloons" — is the real reason 4a deserves an isolated review cycle. When it lands, 4b reads `revised` from the (now gate-folded) sidecar field exactly as today — a hardening, not a behavior change.

**Recommendation:** build **4b** in this branch; give **4a** its own spec→review→build→review cycle. 4a balloons into the most sophisticated machinery in the repo and deserves isolated review; 4b is the spine's actual value and fits cleanly here. (This is the "flag if it balloons" call.)

---

## Safety & write-location discipline

- The registry is the **only** new persistent artifact, and it lives in the workspace-relative `.apodictic/registry.json` (see §Where the registry lives) — never `~`/`$APODICTIC_HOME` (sandbox-unsafe), and never the plugin repo or plugin cache (same rule as all rolling state).
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
5. ~~Submission signal~~ **Decided (a):** populate the existing-but-unused `readiness[]` sidecar array when submission readiness enters scope (Pass 11 / `/ready` / submission-readiness workflow) — the smallest write, no schema change, no invented `submission` mode. The `submission` node derives when `readiness[]` is **non-empty** (entries are `apodictic.readiness.v1` = dimension/verdict/rationale, with no status field — presence is the signal, matching the lifecycle table and the submission-readiness mirror). Globbing for Pass-11 artifacts (b) and persisting `goal` (c) rejected as brittle / drift-prone respectively.

---

*This file is a design spec. If adopted, the runtime changes land in `commands/start.md` (binding + dispatch promotion), `commands/new-project.md` (registry write), a new `schemas/apodictic.project_registry.v1.schema.json` + `validate.sh registry-check`, and `intake-router-runtime.md` §6 (transition-graph re-expression).*
