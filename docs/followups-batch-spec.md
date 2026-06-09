# Three follow-ups — spec (finding-trace glob · legal-risk wiring · project dashboard)

**Status:** Spec, **revised after an Opus spec review.** Three independent roadmap follow-ups through one spec→review→build→review loop; split into **A+B** (validator/router/command) and **C** (artifact) at merge. Conventions per `AGENTS.md` (dual-script mirror; merge commit; full-relative reference paths in command docs). Review verdicts: A buildable + safe; B buildable as doc/command (no executable plumbing) but novel framing + a stale-doc trap; C buildable, generator confirmed **safe**, but must be render-only.

---

## A. `finding-trace` `_COMPLETION_GLOBS` narrowing — *buildable + safe*

**Problem.** `finding_trace.py:70` `_COMPLETION_GLOBS = ("*_Revision_*.md",)` is over-broad — a `*_Revision_Calendar_*.md` matches it and is wrongly classified a *completion*. Increment 4a already defined `[Project]_Revision_Report_[runlabel].md` and narrowed the gate's `revision_report` key; align finding-trace.

**Confirmed safe (review):** `_REVISION_GLOBS` and `_COMPLETION_GLOBS` are globbed independently in `resolve_run_folder` (`:329-333`); narrowing only completion preserves the `completion ⊆ revision-stage` invariant. `run_gate` does **not** import these globs (it resolves its own narrowed `revision_report` key + uses only `resolved_cited_ids`), so the gate is unaffected. The `--check-all` finding-trace invariant runs ledger+letter only (`validate.sh:285`) — no completion dependency. Nothing breaks.

**Change (in `finding_trace.py`, then mirror byte-identically to root `scripts/finding_trace.py`):**
1. `_COMPLETION_GLOBS = ("*_Revision_Report_*.md",)`; update the comment at `:67-70` and the `trace()` docstring at `:160-166` (both hardcode the old glob in prose).
2. `classify_files` has the `_Revision_` substring at **two** lines: `:351` (`_Session_Plan_`/`_Revision_` → `revisions`) **stays broad**; **only** `:353` (`if "_Revision_" in base` → `completions`) narrows to `"_Revision_Report_" in base`. Name both lines so the builder edits only `:353`.
3. Self-test: the fixture written at `:566` (`Proj_Revision_run.md`) → `Proj_Revision_Report_run.md`, **and its consumer** at `:580-581` (`explicit_files_completion`, the `run([...])` path string) must be renamed in lockstep or it reads a now-missing file. **Add a negative test:** a `Proj_Revision_Calendar_run.md` carrying a `<!-- resolved: F-… -->` marker is **not** classified a completion (genuine regression guard — it *does* match pre-fix).

**Validate:** `validate.sh finding-trace --self-test` + `--check-all`. No schema/count change.

---

## B. Legal Risk Register router wiring — *doc/command change; novel framing + stale-doc trap*

**Problem.** The module is built (`references/legal-risk-register.md` + `legal-risk` validator + `--check-all` example), classified an output overlay (§6 Table B), but `constraint:risk` doesn't attach it and there's no command.

**Family is right, but it is NOT a "mirror" (review).** Legal Risk Register produces a **separate companion artifact** (like the Vocabulary Guide), not ledger findings — so it belongs to the synthesis-*presentation* overlay family, not the §4c auto-run-audit family (that's how `constraint:ai` is wired). **But** the two existing presentation hooks (`run-synthesis.md:280-282`) key on `operator:` only; nothing carries a `constraint:` flag into that section today. So this is the **first `constraint:`-keyed presentation hook** and the **first offer-then-attach overlay** (every existing overlay auto-runs). Both are net-new shapes, not mirrors. (Still a prose-procedure edit — run-synthesis is followed by the model, not executed — so no code plumbing.)

**Change:**
1. **`run-synthesis.md` — new constraint hook** beside the operator hooks: "**Constraint mode — Legal Risk Register (`constraint:risk`).** When the contract carries `constraint:risk`, **offer** the register; on the author's accept, run the Legal Risk Register **Protocol** (`references/legal-risk-register.md §Protocol`, the §38-43 procedure) and write `[Project]_Legal_Risk_Register_[runlabel].md`, validated with `scripts/validate.sh legal-risk`. Additive companion artifact — the editorial letter is unchanged." Point explicitly at the module's Protocol (today the module is invocation-agnostic). State the offer/confirm step explicitly (no existing overlay models it).
2. **Flag propagation.** Confirm intake records `constraint:risk` where synthesis reads it — the same persistence the `operator:` flags use between intake and synthesis. If there's no such channel, add the one line that carries it (this is the only "is it really wired" risk; verify during build).
3. **`/legal-risk` command** (`commands/legal-risk.md`, new) mirroring `commands/triage-feedback.md` **including frontmatter**: `description`, `argument-hint`, `allowed-tools: Read, Write, Edit, Bash, Glob, Grep` (needs `Bash` for `validate.sh legal-risk`). Use **full relative reference paths** (`../skills/core-editor/references/legal-risk-register.md`), never bare `` `references/...` `` — the codex build throws on ambiguous shorthand (`build-codex.mjs:420-424`).
4. **Status surfaces — flip exactly these, no more (review found 6):**
   - `intake-router-runtime.md:190` (§3 option D) → Built.
   - `intake-router-runtime.md:357` (§6 Table B) → Built.
   - `pass-dependencies.md:179` (§4a) → auto-attach (offer-then-attach) on `constraint:risk`, wired.
   - `docs/legal-risk-register.md:66` (future-increment `/legal-risk` + intake branch) → built.
   - `ROADMAP.md:253` (follow-up backlog item) → done.
   - **`ROADMAP.md:223` — PARTIAL flip only (Blocker).** That "Future increments" sentence bundles *`/legal-risk` + intake routing* **with** *per-class detection guidance* **and** *a standard escalation-trigger taxonomy*. Flip **only** the command/routing clause; leave the detection + taxonomy clauses as still-future. Do not mark the whole sentence built.

**Validate:** `validate.sh legal-risk --self-test` + `--check-all` (unchanged). Command auto-discovers (no manifest entry).

---

## C. Project-dashboard artifact — *buildable; generator safe; must be render-only*

**What it is.** A self-contained `plugins/apodictic/project-dashboard.html` (pattern of `overview-dashboard.html` / `route-explorer.html`) rendering project state — "select the project, see where each stands."

**Generator confirmed safe (review).** Both host builds `fs.cpSync` the **whole** `plugins/apodictic/` dir (`build-codex.mjs:582`, `build-antigravity.mjs:248`); required-assets list no dashboard HTML; `.codex.html` overrides are iterated, not required-per-file; `--self-check` builds in a temp dir and returns early (no committed-tree diff). A new `.html` is copied and auto-doc-rewritten; **`--self-check` cannot fail from it.**

**Render-only — the load-bearing correction (Blocker).** The sandbox has no filesystem, and `lifecycle_node.py` derives `diagnosed` by a **disk check** (SYNTHESIS.md / `runs/*/*_Synthesis_*.md`) the artifact can't do. So the HTML must **not re-derive** the lifecycle node. Instead:
- **Claude pre-computes** each project's `node` + `next_action` (via `lifecycle_node.py` + the leverage ladder) and **embeds them in the payload**; the HTML **renders only**. This eliminates the drift surface entirely (no node logic in JS — just labels) and resolves the rail/precedence mismatch the first draft had.
- The lifecycle rail is a **display grouping** of the 8 node names *for labeling*, not a re-derivation. Use the exact node set/order from `lifecycle_node.py:9` (`cold → blocked_gate → execution → pre_writing → submission → revising → diagnosed → diagnosing`, `diagnosing` = catch-all default) so labels match the source of truth.

**Payload + behavior:**
- **Input:** a `<textarea>` for an `apodictic.project_registry.v1` payload extended with the pre-computed `node` + `next_action` + `last_touched` per project (and a `snapshot_ts`); a small embedded **sample** so it renders out-of-the-box. No `fetch` (sandbox-safe).
- **Per-project card:** title, the lifecycle rail with "you are here" (from the payload's `node`), last-touched, and the **"what now?"** next action — **labeled "as of <snapshot_ts>"** (the leverage ladder reads live `finding_states`, `revision-coach/SKILL.md:89-100`, so it can go stale the instant a finding is revised). Click → expand (mode, the `/start <id>` launch line).
- **Interactions:** filter by node, sort by last-touched, `localStorage` for last filter.
- **Honest scope (in the HTML + README):** "**snapshot** dashboard + launcher — not live; shows `/start <id>` but cannot bind/run." Note in a comment that the codex build auto-rewrites `/start` → `apodictic-start` in the generated copy (expected; don't "fix" it).

**No validator** (consistent with existing dashboards).

---

## PR split (decide after build review)

- **PR 1 (A+B):** finding-trace narrowing + legal-risk wiring/command/status flips. Same reviewer mindset.
- **PR 2 (C):** the dashboard artifact.

No hidden coupling between A/B/C (only shared surfaces — the dual mirror (A) and the generators (C) — are confirmed safe).
