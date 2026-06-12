# QOL Spec — Overview Dashboard Onboarding Callout

**Status:** Spec (ready for review → build). Small, additive. No redesign.

## Goal

`plugins/apodictic/overview-dashboard.html` (the static, single-file capability
dashboard — the ROADMAP's "Framework Overview Dashboard" backlog entry, ROADMAP.md
§Framework Overview Dashboard, already exists as this file) is linked from the root
README as the "whole system at a glance" page. Its gap as a **brand-new-user front
door**: the header gives a tagline and the Firewall note, but the first actionable
instruction ("Start with `/start`") is buried in the Router section intro. A new
user doesn't immediately see *what this page is* or *what to do first*.

Add **one small getting-started callout** to the header. Nothing else changes: all
six sections (Router, Macro Blocks, Genre Modules, Specialized Audits, Common
Workflows, Plot Architecture), the `.firewall-note`, the footer, and all JS stay
as-is.

## Current state (verified)

- File: `plugins/apodictic/overview-dashboard.html`, 659 lines. Fully self-contained:
  one inline `<style>` block (CSS custom properties in `:root`, accent `#b45309`),
  one inline `<script>`, **no** external fonts/scripts/stylesheets/CDN. The only
  `http` references are two plain `<a href="https://github.com/anotherpanacea-eng/apodictic">`
  anchor links (header h1 and footer) — links, not fetched resources. Keep it that way.
- Footer pins "Development Editor v2.3.1", which matches the current plugin version
  (`plugins/apodictic/.claude-plugin/plugin.json` = 2.3.1). This change does **not**
  bump any version; do not touch the footer.
- Current top-of-body markup (lines 330–336) — this is the insertion context:

```html
<header>
  <h1><a href="https://github.com/anotherpanacea-eng/apodictic" style="color:inherit; text-decoration:none;">APODICTIC</a></h1>
  <p>Development Editor — developmental editing that listens before diagnosing.</p>
  <div class="firewall-note">
    <strong>The Firewall:</strong> This tool diagnoses structure. It identifies problems, explains mechanisms, and proposes classes of solution. It never invents content — no plot ideas, no dialogue, no prose. Creative authority stays with the author.
  </div>
</header>
```

- `/start` first appears at line 341 (Router section intro: "Start with
  `<code>/start</code>`. Three questions route you to the right workflow.") — below
  the fold of the header, after a screen of CSS-rendered chrome.

## The enhancement

### 1. HTML — insert inside `<header>`, between the tagline `<p>` and the `.firewall-note`

Orientation first, Firewall second. One element does both jobs (plain-language
"what is this" + "what do I do first"):

```html
  <div class="getting-started">
    <strong>New here?</strong> This page is a map of everything the editor can do — you don't need to memorize it. Open your agent in your manuscript's folder and type <code>/start</code>; three questions route you to the right workflow.
  </div>
```

Host-neutral copy on purpose: no "Claude", no host names (the codex build's
generated-doc scan rejects Claude-specific runtime assumptions in markdown, and the
same discipline is house style for shared HTML).

### 2. CSS — add to the inline `<style>`, directly after the `.firewall-note` rule (after line 69)

Matches existing conventions (CSS variables, same paddings/radii/max-width as the
sibling `.firewall-note`, visually distinct from it: full accent border + surface
background vs. the note's left-border + amber wash):

```css
  .getting-started {
    background: var(--surface);
    border: 1px solid var(--accent);
    border-radius: 8px;
    padding: 0.75rem 1rem;
    margin: 1.5rem auto 0;
    max-width: 600px;
    font-size: 0.9rem;
    text-align: left;
  }

  .getting-started code {
    background: var(--accent-light);
    padding: 0.1rem 0.35rem;
    border-radius: 4px;
    font-weight: 600;
    color: var(--accent-hover);
  }
```

No JS changes. The element is static text — no `role`/`tabindex` needed.

## Variant parity (the load-bearing build-safety part)

### `overview-dashboard.codex.html` — hand-authored override; MUST receive the same edit

Verified, not assumed:

- `release-registry.json` → `codex.overrides` maps
  `"plugins/apodictic/overview-dashboard.codex.html": "plugins/apodictic/overview-dashboard.html"`.
- `scripts/build-codex.mjs` documents `plugins/apodictic/*.codex.*` as "**authored**
  Codex-only overrides" (workspace-README template, ~line 154) and its
  `applyOverrides()` (~line 287) does a plain `fs.copyFileSync` of the `.codex.html`
  **over** the base file in the generated workspace. It is **not generated** — it is
  hand-maintained, and it **wholesale replaces** the base file in the codex tree.
- **Therefore: editing only `overview-dashboard.html` silently drops the enhancement
  from the Codex distribution** — the stale override clobbers it. Both files must be
  edited.
- Diff of the two files today: they differ on exactly 9 lines, all the same kind of
  delta — slash-command tokens swapped for Codex wrapper names, surrounding words
  byte-identical: `/start` → `apodictic-start` (×7), `/audit [name]` →
  `apodictic-audit [name]`, `/plot-coach` → `apodictic-plot-coach`. No other
  differences (CSS, JS, structure all identical).

**Builder instructions:**

1. Apply the identical CSS + HTML edit to `overview-dashboard.codex.html`, with one
   token swap in the callout copy: `<code>/start</code>` → `<code>apodictic-start</code>`.
   Every other byte of the new content identical to the base file's version
   (this matches the established override convention above).
2. Verify with `diff plugins/apodictic/overview-dashboard.html plugins/apodictic/overview-dashboard.codex.html`
   — the result must still show **only** command-token deltas (now 10 changed lines,
   the 9 existing + the new callout line).
3. Note: `build-codex.mjs` `rewriteGeneratedDocs()` does rewrite slash commands in
   generated `.html` too, so a `/start` left in the override would get rewritten at
   build time — but do **not** rely on that; keep the override authored with
   `apodictic-start` per the existing convention, so the committed file is correct
   as-is.
4. Do **not** edit anything under `codex/` or `antigravity/` — both are gitignored
   generated workspaces (see `.gitignore`: "Generated host workspaces"), rebuilt by
   the release workflow. Nothing generated is committed for this change.

### Antigravity — no variant exists; no extra file

Verified: no `overview-dashboard.antigravity.html` (or any `*antigravity*` file)
exists under `plugins/apodictic/`; `release-registry.json` → `antigravity.overrides`
is `{}`; `scripts/build-antigravity.mjs` has no overview-dashboard handling. The
antigravity build consumes the base `overview-dashboard.html` directly (with its
own slash-command rewriting at build time). **No third file to edit.**

## Changelog fragment

Add `changelog.d/overview-dashboard-onboarding.md` per `changelog.d/README.md`
(first non-blank line a single freeform thematic `### ` header, non-empty body,
not `### Added/Changed/Fixed`):

```markdown
### Onboarding — overview dashboard front door

The overview dashboard header now opens with a "New here?" getting-started callout — a one-line plain-language orientation ("this page is a map; you don't need to memorize it") plus the first action (`/start`) — so a brand-new user landing on the page sees what to do before scrolling into the technical sections. Applied to both the canonical file and its authored `.codex.html` twin (which preserves `apodictic-start` naming).
```

## Gates — ALL of these run in CI (`.github/workflows/ci.yml`) and MUST be run locally before push

1. `bash scripts/validate.sh --check-all`
2. `node scripts/build-codex.mjs --self-check` — this is the one that catches a
   missing/broken `.codex.html` override (it `mustExist`s every `codex.overrides`
   source and builds + validates the workspace in temp).
3. `node scripts/build-antigravity.mjs --self-check`
4. `node scripts/release-generate.mjs --check` — **easy to forget; a recent CI
   failure came from hand-editing a paired/generated doc and skipping this gate.**
   For the record: `release-generate.mjs` references no `.html` files (its registry
   `paths` cover README, plugin manifests, skill files, and the audit command), so
   this dashboard does **not** appear to be registry-derived and this edit should
   not trip it — but that is an inference from reading the script, not a guarantee,
   so **the builder MUST run `release-generate --check` anyway**.
5. `node scripts/assemble-changelog.mjs --check` — validates the new fragment's
   format.

No script changes are involved, so the `scripts/` ↔ `plugins/apodictic/scripts/`
mirror (checked inside `--check-all` via check-mirror) is unaffected — but
`--check-all` runs it regardless.

Sanity check beyond the gates: open the edited file(s) in a browser once; the
callout must render between the tagline and the Firewall note, and clicking the
router/macro cards must still toggle (i.e., the `<style>`/`<script>` blocks were
not disturbed).

## Non-goals

- **No redesign.** No layout, palette, typography, or section changes. The existing
  header, all six sections, `.firewall-note`, footer, and JS stay byte-identical
  apart from the two insertions.
- **No new sections** and no new page; this is one `<div>` + two CSS rules per file.
- **No network/deps.** Still zero external fonts/scripts/styles; only the two
  existing plain GitHub anchor links.
- **No duplication of command/onboarding content.** The callout is one sentence of
  orientation + a pointer to `/start` — it must not replicate router question
  trees, install instructions, or any host-specific onboarding walkthrough. (The
  prompt for this spec referenced "the new `/apodictic` command"; no
  `commands/apodictic.md` exists in the repo today — `commands/` has `start.md`
  et al. — so the operative rule is simply: the callout points at `/start`, it
  doesn't explain it.)
- **No version bump**, no footer edit, no README edit (the README already links the
  dashboard), no ROADMAP edit.
