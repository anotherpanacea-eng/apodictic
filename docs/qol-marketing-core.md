# PR A — Marketing-parity core (spec)

**Status:** ✅ **Shipped — PR #80 (merged 2026-06-12).** Documentation/manifest only; **no diagnostic behavior, schema, or validator change.** The single root cause is that promotional prose is hand-maintained and 5 commands are unregistered, so the registry-generated command lists undersell.

## Goal
Bring the plugin's self-description in line with what it is at v2.3.1: register the 5 missing commands (so both READMEs' generated command lists fill in), refresh the hand-maintained framing/capability prose, back-port one already-fixed line, qualify the privacy claim, and reword one stale CONTRIBUTING reason. **Out of scope (PR B):** AUDIT_SELECTION_MATRIX, the dashboards, route-explorer, and their codex twins.

## Hard mechanics (verified, must be honored)
- **`release-registry.json` `commands[]`** entries have keys: `command`, `category` (`entry`/`diagnostic`/`focused`/`setup`), `status` (`primary`/`first_class_shortcut`/`compat_alias`), `routerEquivalent`, `writerQuestion`, `description`. `scripts/release-generate.mjs buildGroupedCommandList()` groups by `category` → headings (entry="Start here:", diagnostic="Diagnostic workflows:", focused="Focused tools:", setup="Setup:"), renders each non-alias as `` - `/cmd` — <writerQuestion> ``, and puts `compat_alias` on the trailing alias line.
- **Both READMEs' §Commands AND the count/"Framework Version" lines are GENERATED.** Do **not** hand-edit those lists. After editing the registry, run `node scripts/release-generate.mjs` (write mode) to regenerate, then `--check` must pass. (Hand-editing breaks `replaceOrThrow`'s anchor — this is what failed #77's CI.)
- **Every registered slug needs a base-skill in BOTH `codex.commandBaseSkills` and `antigravity.commandBaseSkills`** or `build-codex.mjs` / `build-antigravity.mjs` throw `Missing … commandBaseSkills mapping`.
- **`/apodictic` wrapper-name special-case:** `build-codex.mjs buildCommandMappings()` sets `wrapperName = \`${codex.wrapperPrefix}-${slug}\`` → `apodictic-apodictic`. Add a special-case so `/apodictic` → **`apodictic-index`**. Apply the SAME special-case in `build-antigravity.mjs`'s equivalent wrapper derivation (find it; mirror the logic). Keep it a tiny, localized map (e.g. `const WRAPPER_OVERRIDES = { apodictic: "apodictic-index" }` consulted in the wrapperName line).
- **`README.codex.md` is an authored override** (`codex.overrides`), NOT regenerated for its §Entrypoints/prose. Its prose edits are by hand; its `apodictic-*` Entrypoints list is hand-synced. Apply the same prose refresh there, with host-appropriate wording (no "Claude", `apodictic-*` command names, and `apodictic-index` for /apodictic).

## The 5 registry entries to add (to `commands[]`, preserving array style)
| command | category | status | writerQuestion | base skill (both generators) |
|---|---|---|---|---|
| `/apodictic` | `entry` | `first_class_shortcut` | "What can this plugin do? Where do I start?" | `core-editor` |
| `/projects` | `setup` | `first_class_shortcut` | "List, resume, and tidy my editing projects." | `core-editor` |
| `/legal-risk` | `focused` | `first_class_shortcut` | "Flag legal exposure (defamation, privacy, rights) for a lawyer's review." | `core-editor` |
| `/triage-feedback` | `focused` | `first_class_shortcut` | "Sort and prioritize beta-reader / editor feedback." | `revision-coach` |
| `/reader-questions` | `focused` | `first_class_shortcut` | "Turn my diagnosis into targeted beta-reader questions." | `revision-coach` |

`routerEquivalent`: `null` for all 5 (none is a router answer). `description`: one factual sentence each (builder may draft; keep ≤120 chars, host-neutral). Place each in a sensible spot in the array (group-order doesn't matter; the generator sorts by category). **`/apodictic` is `entry`** so it joins `/start` under "Start here:".

## Prose refreshes (hand-edit `README.md` AND `README.codex.md`; the root `README.md` §Commands regenerates, but its prose bullets at lines ~50–62 are hand-maintained — refresh those too)

### A. Framing — add persuasive/argument-shaped nonfiction
- `plugins/apodictic/README.md:5` "for fiction and narrative nonfiction" → "for fiction, narrative nonfiction, **and persuasive/argument-shaped nonfiction** (policy briefs, op-eds, testimony — via the Nonfiction Argument Engine)." Mirror at `README.codex.md:7` and the root `README.md` opening.
- `plugins/apodictic/README.md:37` Intended Audience — add a sentence naming persuasive-nonfiction writers (policy/op-ed/testimony) as a real audience, since `revision-coach` triggers on those forms.

### B. Capability list — add the shipped surfaces
In `README.md` "It does" (lines 17–24) and "Components → Workflows" (43–51), and the root README "Beyond Full Edits" bullets, add (factually, briefly): **Legal Risk Register** (flag defamation/privacy/rights for counsel — never legal advice), **Feedback Triage**, **Beta-Reader Instrument**, **Manuscript-Structure visualizations**, **Nonfiction Argument Engine** (argument spine/support/warrant + Red-Team/Persuasion/Evidence), **project addressability** (`/projects`, state-driven resume), **Retcon Planning / State Cards**, **Diagnostic-Vocabulary & Editor-Scaffolding operator modes**. Keep the firewall framing on Legal Risk ("flags, never adjudicates"). Mirror in `README.codex.md`.

### C. Back-port the already-fixed sentence (the contradiction)
- `plugins/apodictic/README.md:33` "After diagnosis, you work with Claude directly (outside the plugin) on execution." → replace with the **revision-coach-aware** wording (the override `README.codex.md:64` already has the right shape): something like *"After diagnosis you can stay inside APODICTIC's revision-coaching and editor workflows (session planning, stuck-point help, the revising-loop dispatcher), or step outside the diagnostic firewall to draft."* This also removes a string `build-codex.mjs` forbids — confirm the canonical README no longer contains the forbidden phrase. (`README.codex.md:64` already correct; leave it, just ensure parity of meaning.)

### D. Qualify the privacy claim
- `plugins/apodictic/README.md:31` "Access, store, or transmit manuscript text beyond the active session." Split the conflated claim honestly: (i) the plugin itself adds no telemetry/network calls of its own; (ii) **rolling diagnostic artifacts persist on the user's disk by design** (that's a feature, line 23) — so "session-only" is wrong as stated; (iii) **`/research` modes are internet-enabled** and send query-shaped text to search. Reword to something accurate, e.g. *"The plugin transmits nothing on its own and stores diagnostic state only on your local disk; the optional `/research` modes make web searches you invoke explicitly."* Mirror in `README.codex.md`.

### E. CONTRIBUTING reword (keep policy, fix the false reason)
- `CONTRIBUTING.md:15` "Pull requests (this is a plugin, not a repository with PR infrastructure)" — the **no-external-PR policy stays**; its reason is false (the repo runs CI + a PR/merge-commit policy per AGENTS.md). Reword to: external code PRs aren't accepted because the repo is solo-maintained and contributions are email-based (keep the existing `CONTRIBUTING.md` email channel), **not** because there's no PR infrastructure.

### F. SKILL.md description
- `plugins/apodictic/skills/core-editor/SKILL.md:4` frontmatter description "for fiction and narrative nonfiction" → include the argument engine ("…and argument-shaped nonfiction; owns the Nonfiction Argument Engine"). Update its `*Last Updated: February 2026*` (line ~14) to the current month, or drop the date line (recommend drop — it's drift-prone, same lesson as the status-drift lint).

## Out of scope for PR A (do NOT touch — PR B)
`AUDIT_SELECTION_MATRIX.md` + `.codex.md`, `overview-dashboard.html` + `.codex.html`, `route-explorer.html` + `.codex.html`. Also do **not** add markers/flip any status-drift docs here.

## Verification gates (run ALL locally before push — release-generate is the one that bit us)
1. `node scripts/release-generate.mjs` (write) then `node scripts/release-generate.mjs --check` → **passed**, and confirm both READMEs now list all 16 commands grouped correctly with `/apodictic` under "Start here:".
2. `node scripts/build-codex.mjs --self-check` and `node scripts/build-antigravity.mjs --self-check` → pass (proves the 5 `commandBaseSkills` entries exist in both, the `apodictic-index` wrapper special-case works, and no forbidden Claude-phrasing leaked into the refreshed README prose — the canonical README's old line-33 must be gone).
3. `node scripts/assemble-changelog.mjs --check` (add `changelog.d/qol-marketing-core.md`).
4. `bash scripts/validate.sh --check-all` → unaffected, exit 0.
5. Manual: `git grep -n "After diagnosis, you work with Claude directly"` → **only** zero hits in `plugins/apodictic/README.md` (gone); the forbidden-pattern back-port is complete.

## Non-goals
No diagnostic/schema/validator change. No count edits (counts are registry-generated and currently correct). No version bump (merge-time). No new commands — only registering existing ones.
