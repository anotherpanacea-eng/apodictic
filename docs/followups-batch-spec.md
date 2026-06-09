# Three follow-ups — spec (finding-trace glob · legal-risk wiring · project dashboard)

**Status:** Spec (not yet built). Three independent roadmap follow-ups, run through one spec→review→build→review loop. Likely split into 2–3 PRs at merge. Conventions per `AGENTS.md` (dual-script mirror; merge commit; validator culture).

---

## A. `finding-trace` `_COMPLETION_GLOBS` narrowing

**Problem.** `finding_trace.py:70` `_COMPLETION_GLOBS = ("*_Revision_*.md",)` is over-broad — a deadline-coaching `*_Revision_Calendar_*.md` matches it. Benign today (a calendar carries no `<!-- resolved: F-… -->` markers, so it contributes no completion), but Increment 4a already defined the report filename `[Project]_Revision_Report_[runlabel].md` and narrowed the gate's `revision_report` key to `*_Revision_Report_*.md`. Align `finding-trace` for consistency, so the *completion* surface (E5/W3, the `revised` lifecycle) keys on the Report, not any revision-stage artifact.

**Change (touch points — all in `finding_trace.py`, then mirror to root `scripts/`):**
1. `_COMPLETION_GLOBS = ("*_Revision_Report_*.md",)` + update the comment.
2. `classify_files` completion sub-classification (`:353` `if "_Revision_" in base:`) → `"_Revision_Report_" in base`. The *revision-stage* classification (`:351`, `_Revision_` / `_Session_Plan_`) stays broad — a calendar is still a revision-stage artifact (can express intent / W2 plan coverage), just not a **completion**.
3. Self-test fixture (`:566,:581`) `Proj_Revision_run.md` → `Proj_Revision_Report_run.md` (so the completion test still exercises a completion). **Add a negative case:** a `Proj_Revision_Calendar_run.md` with a `<!-- resolved: F-… -->` marker is **not** treated as a completion (mirrors the gate's `rev_calendar_not_report_blocks`).

**Note `_REVISION_GLOBS` stays broad** (`*_Revision_*.md`) — it's the revision-*stage* surface (intent/plan coverage), correctly inclusive of calendars. Only the completion subset narrows. This keeps the SUBSET relationship the comment describes (completion ⊂ revision-stage).

**Risk/validation:** confirm the finding-trace `--check-all` canonical ledger↔letter pair has no revision-report dependency (it tests E1–E6 on a ledger/letter, not a completion). Run `validate.sh finding-trace --self-test` + `--check-all`. No schema/count change.

---

## B. Legal Risk Register router wiring

**Problem.** The Legal Risk Register module is built (`references/legal-risk-register.md` + `legal-risk` validator), and the fork/overlay split classifies it as an output **overlay** (`intake-router-runtime.md` §6 Table B) — but `constraint:risk` doesn't yet auto-attach it, and there's no direct command. The route map says "module built; router auto-wiring pending."

**Change (mirror the editor-scaffolding / diagnostic-vocabulary overlay pattern):**
1. **`run-synthesis.md` constraint hook.** Add a "Constraint mode — Legal Risk Register (`constraint:risk`)" paragraph next to the existing Operator-mode hooks (`run-synthesis.md:280-282`): when `constraint:risk` is set, **offer** the register and, on accept, additionally produce `[Project]_Legal_Risk_Register_[runlabel].md` per `references/legal-risk-register.md`, validated with `scripts/validate.sh legal-risk`. It's an additive overlay (like the Vocabulary Guide) — the editorial letter is unchanged; the register is a companion artifact. *Offer-then-attach* (not silent auto-run) because the not-a-lawyer framing warrants an explicit confirm.
2. **`/legal-risk` command** (`commands/legal-risk.md`, new) — direct entry point, mirroring `commands/triage-feedback.md`: load core-editor, run the Legal Risk Register workflow on the manuscript, write the artifact, validate. The router path (constraint:risk) and the command are the two doors, same as `/triage-feedback` vs the feedback route.
3. **Status flips:** `intake-router-runtime.md` §3 option D and §6 Table B → "**Built**" (drop "router auto-wiring pending"). `pass-dependencies.md:179` §4a risk line → auto-attach on `constraint:risk` (offer-then-attach), wired. `docs/legal-risk-register.md` "Future increments" note (`/legal-risk` command + intake routing) → mark built. ROADMAP follow-up item → done.

**Validation:** `validate.sh legal-risk --self-test` (unchanged) + `--check-all` (the canonical register example still gates). No new validator. Confirm the new command file doesn't need manifest registration (commands are auto-discovered — confirmed for `/projects`).

---

## C. Project-dashboard artifact

**What it is.** A self-contained HTML dashboard (the pattern of `plugins/apodictic/overview-dashboard.html` / `route-explorer.html`) that renders project state from an `apodictic.project_registry.v1` payload — "select the project, see where each stands." File: `plugins/apodictic/project-dashboard.html`.

**Honest scope (from the earlier discussion).** A Claude **Artifact** / standalone HTML is sandboxed: **no filesystem, no Python, no live re-read**. So it is a **generated snapshot + launcher**, not a live monitor and not a controller:
- Claude (in a session) reads the registry + sidecars, derives each lifecycle node + leverage action, and the dashboard renders that. To refresh, regenerate.
- It **shows** the launch command (`/start <id>`) per project; it cannot itself bind/run (no bridge from the sandbox to the CLI).

**Content / behavior:**
- **Input:** a `<textarea>` to paste a registry JSON (+ optional per-project sidecar fields), with a small embedded **sample** payload so it renders out-of-the-box. (No `fetch` — sandbox-safe.)
- **Per-project card:** title, a **lifecycle rail** (`cold → diagnosing → diagnosed → revising → submission`, with `blocked_gate`/`execution`/`pre_writing` as states) showing "you are here," last-touched, and the **"what now?"** next action (from the leverage ladder / `next_action`). A card click expands detail (mode, open Must-Fix count if present, the `/start <id>` launch line).
- **Interactions:** filter by lifecycle node, sort by last-touched; `localStorage` to remember last filter. All over the embedded/pasted data — no network.
- **Derivation parity:** the lifecycle-node precedence and leverage ladder rendered must match `scripts/lifecycle_node.py` and `revision-coach/SKILL.md` §Loop Dispatch (single source of truth is the Python; the HTML mirrors it for display). Note this in a comment so they don't drift.

**Scope guard:** display-only; no claim of live state or actuation; the docs/README should call it a "snapshot dashboard." 

**Parity/build:** edit only the canonical `plugins/apodictic/project-dashboard.html` (the `codex`/`antigravity` variants are generated, not committed — confirm `build-codex.mjs --self-check` / `build-antigravity.mjs --self-check` pass with the new file; if the generator enumerates dashboards explicitly, it may need the new filename added). No validator (consistent with the existing dashboards).

---

## Open questions

1. **PR granularity:** one PR (all three) vs. split (A+B code/docs; C artifact). Recommend **split** — C is a different kind of artifact and reviewer; A+B are small router/validator touches. Decide after build review.
2. **Legal-risk auto-attach tier:** offer-then-attach (recommended, given the legal framing) vs. silent auto-run on `constraint:risk`. Spec assumes offer-then-attach.
3. **Dashboard input ergonomics:** paste-registry textarea (spec'd, sandbox-safe) vs. a future generator step where Claude writes a data-embedded copy on request. Start with paste + sample.
