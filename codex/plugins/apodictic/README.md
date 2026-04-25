# APODICTIC Development Editor

Developmental editing that listens before diagnosing.

AI-powered developmental editing framework for fiction and narrative nonfiction. Diagnoses structural issues in manuscripts through systematic passes, genre-calibrated analysis, and specialized audits.

## Installation

The current tested Codex install path is workspace-based:

1. From the repo root, run:
   ```bash
   node scripts/build-codex.mjs
   ```
2. Open the generated `codex/` folder as your Codex workspace root.
3. In Codex, open the Plugins view and install `APODICTIC` from the local marketplace.
4. Start a fresh thread and run `apodictic-start`.

If the plugin does not appear, make sure Codex is opened on the generated `codex/` directory, not the repo root.

## Quick Start In Codex

If you're new to the plugin, start with a plain-language request:

- "Use APODICTIC to tell me what kind of manuscript help I need."
- "Use APODICTIC to diagnose the structural problems in this draft."
- "Use APODICTIC to help me plan revisions without rewriting prose."

If you already know the entrypoint you want, invoke the namespaced workflow directly:

- `apodictic-start`
- `apodictic-develop-edit`
- `apodictic-audit shelf`
- `apodictic-coach`

The plugin is designed to feel natural in chat, so plain-language requests and named `apodictic-*` entrypoints should both work.

## What It Does

The Development Editor works like a human developmental editor: it reads a manuscript, infers what it's trying to do, and diagnoses where it succeeds or struggles. The system listens first — inferring authorial intent from the text — before measuring the work against that intent.

**Key design principle:** The editor predicts the manuscript's contract (genre, reader promise, controlling idea) from the text alone. Misalignments between the inferred contract and the author's stated intent are diagnostically valuable — they reveal where the text doesn't communicate what the author intended.

**The Firewall:** The system diagnoses problems and identifies classes of solution. It never invents content (new plot events, characters, dialogue, imagery). The author creates; the system analyzes.

## What This Plugin Does and Does Not Do

**It does:**
- Diagnose structural problems in fiction and narrative nonfiction manuscripts
- Identify where a manuscript succeeds or struggles relative to its own implied contract (genre, reader promise, controlling idea)
- Provide genre-calibrated analysis across literary fiction, horror, mystery, thriller, science fiction, fantasy, romance, and cross-genre hybrids
- Track continuity, pacing, character arcs, reveal economy, emotional dynamics, and thematic coherence across 11 systematic passes
- Run specialized audits for specific craft concerns (scene function, shelf positioning, AI-prose detection, worldbuilding integration, force delivery, and more)
- Generate editorial letters, revision checklists, and diagnostic state that persists across revision rounds
- Guide pre-draft writers from idea to draftable structure

**It does not:**
- Rewrite prose, generate new scenes, invent characters, or produce creative content (the Firewall)
- Line edit, copyedit, or proofread
- Replace a human developmental editor's judgment — it provides analytical scaffolding, not verdicts
- Guarantee commercial viability, publication readiness, or literary merit
- Access, store, or transmit manuscript text beyond the active session

The system diagnoses structure. The author creates content. After diagnosis, you can either stay inside APODICTIC's coaching/editor workflows or switch to a general writing session outside the diagnostic firewall.

## Intended Audience

**Primary audience:** Fiction writers working on novels, novellas, and story collections. The plugin also supports narrative nonfiction, memoir, and creative nonfiction with genre-appropriate calibrations.

**Secondary audience:** Human developmental editors seeking analytical scaffolding, and writing groups using diagnostic vocabulary for structured feedback.

The plugin assumes its user is an adult working on a creative project. Its outputs are structural diagnoses, editorial letters, and revision recommendations — analytical documents, not fiction.

## Components

### Workflows

- **Development Edit** — The main workflow: intake protocol, 11 analysis passes, synthesis, revision rounds, genre calibration
- **Pre-Writing Pathway** — Guides writers from idea to draftable structure (no manuscript required). Writer mode calibration, seed inventory, readiness gates, option architecture, complexity budget, prospective contract, re-entry diff protocol.
- **Plot Coaching** — Plot structure diagnosis (50 spines across 12 families), selection coaching, fantasy & series architecture
- **Specialized Audits** — 33 available audits (3 universal, 15 craft, 10 genre, 5 tag), including 3 primary tags (cozy, philosophical, erotic content) and 2 companion intimacy audits; plus 6 internet-enabled research modes
- **Revision Coaching** — Post-diagnostic coaching: session planning, stuck-point help, momentum tracking, deadline management

### Entrypoints

In this Codex build, the legacy workflows are exposed as namespaced compatibility skills. Invoke them by name or by plain-language request.

**Start here:**
- `apodictic-start` — I have a manuscript — what should I do with it?

**Diagnostic workflows:**
- `apodictic-develop-edit` — What's wrong with my manuscript?
- `apodictic-diagnose` — I have a specific concern — is it a real problem?
- `apodictic-ready` — Is this ready to submit?

**Focused tools:**
- `apodictic-audit` — Run a specific deep-dive analysis.
- `apodictic-research` — I need internet-assisted verification.
- `apodictic-coach` — I have a diagnosis — how do I revise?
- `apodictic-plot-coach` — Is my plot structure working?

**Setup:**
- `apodictic-pre-writing` — I have an idea but no manuscript yet.
- `apodictic-new-project` — Set up a new editing project.

`apodictic-revision-plan` is a compatibility alias for `apodictic-coach`.

### Selection Guide

- See `AUDIT_SELECTION_MATRIX.md` for a practical routing chart of core passes, full passes, Pass 11 sub-passes, specialized audits, tag audits, and research modes.
- See `overview-dashboard.html` for a visual map of workflows, pass blocks, and audit families.

## Usage

### Getting Started
```
apodictic-start
```
The intake router asks what you have (idea, fragments, partial draft, complete draft, series), what you need (draft, diagnose/fix, submission readiness, AI cleanup), and any modifiers (deadline, AI-assisted text, nonfiction, editing for someone else, co-authoring). Routes you to the right workflow automatically. All other namespaced entrypoints remain available as direct shortcuts.

### Full Development Edit
```
apodictic-develop-edit path/to/manuscript.md
```
Runs intake, core passes (reverse outline, reader experience, structural mapping, character audit, reveal economy), and synthesis. Outputs an editorial letter, revision checklist, and diagnostic state.

### Submission Readiness
```
apodictic-ready
```
The full "is this ready?" workflow. Runs Core DE → Synthesis → Pass 11 → Compression Test and produces a unified readiness assessment with verdict, market reality check, opening conversion gate, SR code inventory, and query/synopsis diagnostic. For deadline-constrained writers, say "I'm on a deadline" during intake to get Submission Triage (single-pass go/no-go) instead.

### Quick Diagnosis
```
apodictic-diagnose pacing in Act II
```
Focused check on a specific concern without the full pass sequence.

### Pre-Writing Pathway
```
apodictic-pre-writing
```
For writers with an idea but no manuscript. Calibrates writer mode (architecture-first vs. discovery-first), inventories seeds, builds a protagonist engine, offers 2–3 structural candidates, sets complexity caps, and produces a Structural Plan or Minimal Viable Plan. When the writer returns with a draft, the Re-Entry Diff Protocol compares intent against execution.

### Plot Coaching
```
apodictic-plot-coach
```
Helps choose or fix a plot structure. Works for pre-drafting planning, stuck drafts, and structural pivots.

### Specialized Audit
```
apodictic-audit character
apodictic-audit shelf
apodictic-audit
```
Run a named audit or list all 33 available audits.

### Research Mode
```
apodictic-research comp
apodictic-research fact-check
```
Internet-enabled research to validate comps, check facts, verify genre currency, or surface representation context.

## Execution Modes

APODICTIC selects its execution mode based on the available context window. On large-context frontier models, the default is **single-agent mode**: one subagent runs all passes sequentially in a single context, with the full manuscript in view throughout. This is the fastest and most token-efficient option, viable for manuscripts up to roughly 200,000 words.

For maximum analytical depth, request **swarm mode**: each pass runs as an independent subagent loading the full manuscript. Swarm produces roughly **twice as many findings** with more specific cross-pass connections and more consistent counterevidence — at approximately **5x the token cost**. The quality gain comes from architectural isolation: each pass genuinely cannot see prior analysis until reconciliation, which eliminates anchoring bias.

On standard-context models, APODICTIC falls back to per-pass subagent dispatch with three tiers: **sequential** (each pass gets the full manuscript), **hybrid** (later passes get targeted excerpts via a focus map, ~2–3x cost), and **swarm** (parallel independent subagents, ~5x cost).

**When to consider each mode:**

- **Single-agent** (default on large-context models): Most manuscripts, quick diagnostics, budget-constrained runs.
- **Swarm**: Final-round diagnostics before submission, or when prior runs produced findings that echo rather than complicate each other.
- **Sequential / Hybrid**: Automatic on standard-context models; not typically needed on large-context models unless you prefer per-pass isolation.

To invoke swarm: tell the editor "run this in swarm mode" at intake.

## Model Requirements

APODICTIC works best on high-capability models with strong instruction-following and enough context to hold large manuscript sections in memory. On weaker or smaller-context models, expect degraded severity honesty, thematic interpretation, deliberate ambiguity handling, and fix quality. If you're evaluating the framework, use the best model available in your Codex environment.

## Framework Version

Current Codex manifest version is `1.8.3`. Capabilities: 50 plot spines across 12 families, 33 available audits (3 universal, 15 craft, 10 genre, 5 tag), 6 research modes, 11 core passes, the evaluative Pass 11 gate, the pre-writing pathway, and the intake router. Includes contract-driven and finding-driven audit integration pipeline.

## License

This work is licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).

You can use, adapt, and share this framework for non-commercial purposes, with attribution and under the same license. See [LICENSE](LICENSE) for details.

## Author

anotherpanacea
