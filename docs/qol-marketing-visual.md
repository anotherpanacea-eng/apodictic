# PR B — Marketing-parity: visual + matrix surfaces (spec)

**Status:** spec → build (Opus) → review (Fable). Docs/HTML/matrix only; **no diagnostic behavior, schema, or validator change.** Second of two marketing-parity PRs (PR A = #80, the README/registry core). Depends on nothing in PR A (different files); can merge in any order.

## Goal
Refresh the visual + matrix surfaces to v2.3.1 reality, AND remove two redundant codex overrides so future edits stop being double-edits. Three surfaces + their codex twins are in scope: `AUDIT_SELECTION_MATRIX.md`(+`.codex.md`), `overview-dashboard.html`(+`.codex.html`), `route-explorer.html`(+`.codex.html`).

## Part 1 — Codex-twin de-duplication (verified; do the empirical proof anyway)
`build-codex.mjs` runs `applyOverrides()` **then** `rewriteGeneratedDocs()`, and the latter walks `.md`+`.html` (line 303) swapping `/cmd`→`apodictic-cmd`. So a `.codex.*` override whose ONLY difference from its base is those command-token swaps is **redundant** — delete it and the base flows through the rewrite to the same codex output. Verified via diff (command-token grep, 0 non-swap lines):
- **DELETE `plugins/apodictic/overview-dashboard.codex.html`** and **`plugins/apodictic/AUDIT_SELECTION_MATRIX.codex.md`**, and remove both keys from `release-registry.json` `codex.overrides`.
- **KEEP `route-explorer.codex.html`** — it has genuine non-command deltas (a host-specific `<h2>` "Skill Entrypoints" vs "Command Shortcuts"; and a `full_draft|repair|risk` route the base lacks — see Part 2). It stays a hand-authored override.

**Mandatory empirical proof before committing the two deletions** (don't trust the grep alone): build the codex workspace **with** the overrides (`node scripts/build-codex.mjs`), copy the generated `codex/plugins/apodictic/overview-dashboard.html` and `…/AUDIT_SELECTION_MATRIX.md` aside; then remove the two overrides + their registry keys and rebuild; **`diff` the regenerated files against the saved copies — they must be byte-identical.** If any differ, do NOT delete that override (restore it); report the delta. (`codex/` is gitignored; clean it up after. `mustExist` only checks override SOURCES listed in the registry, so removing the keys removes the check — confirm `build-codex --self-check` passes after deletion.)

## Part 2 — Content refresh (canonical BASE files; then mirror only into the surviving route-explorer.codex.html)
Re-derive the inventory from the **canonical source**, not from memory: the audit roster is `core-editor/references/audit-routing-table.md` §Signal-Emitting Audit Registry (the `<!-- registry:signal-emitting-audits:begin -->` list) PLUS the two intentionally-excluded advisory audits named there (Idiolect Preservation, Punctuation Cadence) PLUS the research modes in `commands/research.md` (6: citation-verifier, comp, fact-check, field-recon, genre, representation). Cross-check audit files under `skills/specialized-audits/references/{craft,genre,tag}/`. Do **not** hand-invent counts; where a surface states a count, make it match the registry (which PR A's manifests already use: 34 audits / 6 modes / 50 spines).

**A. `AUDIT_SELECTION_MATRIX.md`** (hand-maintained; release-generate does NOT touch it):
- Update `*Last Updated: February 2026*` → current month (or drop the date line — recommend drop, drift-prone).
- §7 genre table: add the missing genre audits (verify against `genre/` dir — at least **Grimdark**, **Supernatural Horror**).
- Add rows/sections for **Narrative-Decision (StoryScope)**, **Idiolect Preservation**, **Punctuation Cadence** (craft), and the **Legal Risk Register**, **Feedback Triage**, **Beta-Reader Instrument** workflows + `constraint:risk`.
- §9 Research Modes: add the 2 missing (**Citation Verifier**, **Field Reconnaissance**) so the table lists all 6.
- After editing, the `.codex.md` twin is being DELETED (Part 1), so no twin to sync.

**B. `overview-dashboard.html`** (base; `.codex.html` being deleted):
- Audit chips: add the missing audits so the chip inventory matches the registry (the diff vs registry is the checklist — Grimdark, Supernatural Horror, Narrative-Decision/StoryScope, Idiolect, Punctuation Cadence, Compression, Stakes System, Decision Pressure, the Argument companions, Adversarial Evidence Review, etc.); research chips: add Citation Verifier + Field Recon (4→6).
- §Common Workflows: add the shipped workflows currently absent — Feedback Triage, Legal Risk, Beta-Reader loop (`/reader-questions`), project resume (`/start <id>`), the Nonfiction Argument path.
- Q3 router detail: name the **Legal Risk Register** on the sensitive/risky-content branch.
- Keep it a static, no-network/no-deps single file (only the existing GitHub anchor links). After deleting the codex twin, `rewriteGeneratedDocs` will produce the codex version — so use bare `/cmd` slash commands in the base (they auto-swap).

**C. `route-explorer.html`** (base) + **`route-explorer.codex.html`** (surviving twin — mirror edits with command-token swaps, preserving its host-specific "Skill Entrypoints" heading):
- Add a **version/date stamp** to the header (it has none; overview-dashboard has one).
- **Parity-up the base with the legal-risk route the codex twin already has** (`full_draft|repair|risk` → "Core DE + Legal Risk Register"), so the two agree apart from command tokens + the heading.
- Add the **projects/resume path** (`/projects`, `/start <id>`, lifecycle/resume) — absent from both today.
- Add an **execution-mode** note consistent with the swarm reframe ("verification insurance for final submission prep; ~5x, measured up to ~8.5x on long fiction"), matching `run-core.md §Execution Mode`. (Light — a note, not a full §2b menu rebuild.)
- Every edit applied to BOTH route-explorer files; in the `.codex.html`, command tokens become `apodictic-*`, and keep its "Skill Entrypoints" heading. Verify `diff route-explorer.html route-explorer.codex.html` afterward shows only command-token swaps + the heading line.

## Out of scope
README/registry/CONTRIBUTING/SKILL (that's PR A, #80). No status-drift markers. No new audits/commands. No version bump.

## Verification gates (run ALL locally before push)
1. The two-deletion empirical proof (Part 1) — byte-identical codex output with/without the deleted overrides.
2. `node scripts/build-codex.mjs --self-check` (passes after deletion — proves the removed `codex.overrides` keys aren't required and the base+rewrite produces valid codex docs).
3. `node scripts/build-antigravity.mjs --self-check`.
4. `node scripts/release-generate.mjs --check` (unaffected — these surfaces aren't registry-derived; confirm anyway, per the lesson that bit #77).
5. `node scripts/assemble-changelog.mjs --check` (+ `changelog.d/qol-marketing-visual.md`).
6. `bash scripts/validate.sh --check-all` (unaffected, exit 0).
7. `diff plugins/apodictic/route-explorer.html plugins/apodictic/route-explorer.codex.html` → only command-token swaps + the "Skill Entrypoints"/"Command Shortcuts" heading line.
8. Static HTML sanity: both edited HTML files are well-formed (tag-balanced), still self-contained (no new external fetched resources), and the `<script>` toggles are intact.

## Non-goals / honesty notes
- Re-derive inventory from the canonical registry; if a surface's count and the registry disagree, fix the surface, don't invent a number.
- If the empirical proof shows EITHER candidate override is not truly redundant, keep it and report — don't force the deletion.
