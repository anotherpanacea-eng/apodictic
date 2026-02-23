# APODICTIC Development Editor

Developmental editing that listens before diagnosing.

AI-powered developmental editing framework for fiction and narrative nonfiction. Diagnoses structural issues in manuscripts through systematic passes, genre-calibrated analysis, and specialized audits.

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

The system diagnoses structure. The author creates content. After diagnosis, you work with Claude directly (outside the plugin) on execution.

## Intended Audience

**Primary audience:** Fiction writers working on novels, novellas, and story collections. The plugin also supports narrative nonfiction, memoir, and creative nonfiction with genre-appropriate calibrations.

**Secondary audience:** Human developmental editors seeking analytical scaffolding, and writing groups using diagnostic vocabulary for structured feedback.

The plugin assumes its user is an adult working on a creative project. Its outputs are structural diagnoses, editorial letters, and revision recommendations — analytical documents, not fiction.

## Components

### Skills (4)

- **core-editor** — The main workflow: intake protocol, 11 analysis passes, synthesis, revision rounds, genre calibration
- **pre-writing-pathway** — Guides writers from idea to draftable structure (no manuscript required). Writer mode calibration, seed inventory, readiness gates, option architecture, complexity budget, prospective contract, re-entry diff protocol.
- **plot-architecture** — Plot structure diagnosis (48 spines across 12 families), selection coaching, fantasy & series architecture
- **specialized-audits** — 25 deep-dive audits (including 3 universal: stakes system, decision pressure, scene turn), 3 tag audits (cozy, philosophical, erotic content), and 4 internet-enabled research modes

### Commands (9)

| Command | Description |
|---------|-------------|
| `/start` | **Recommended entry point.** Routes to the right workflow in 2–3 questions. |
| `/develop-edit` | Run a full development edit on a manuscript |
| `/new-project` | Initialize a new project with contract and diagnostic state |
| `/pre-writing` | Guide a writer from idea to draftable structure (no manuscript needed) |
| `/revision-plan` | Generate revision priorities from diagnostic state |
| `/diagnose` | Quick targeted diagnostic on a specific concern |
| `/plot-coach` | Plot structure selection and coaching |
| `/audit [name]` | Run a specialized audit (no argument lists all available) |
| `/research [mode]` | Run a research mode (no argument lists all available) |

### Selection Guide

- See `AUDIT_SELECTION_MATRIX.md` for a practical routing chart of core passes, full passes, Pass 11 sub-passes, specialized audits, tag audits, and research modes.
- See `overview-dashboard.html` for a visual map of workflows, pass blocks, and audit families.

## Usage

### Getting Started
```
/start
```
The intake router asks what you have (idea, fragments, partial draft, complete draft, series), what you need (draft, diagnose/fix, submission readiness, AI cleanup), and any modifiers (deadline, AI-assisted text, nonfiction, editing for someone else, co-authoring). Routes you to the right workflow automatically. All other commands remain available as direct shortcuts.

### Full Development Edit
```
/develop-edit path/to/manuscript.md
```
Runs intake, core passes (reverse outline, reader experience, structural mapping, character audit, reveal economy), and synthesis. Outputs an editorial letter, revision checklist, and diagnostic state.

### Quick Diagnosis
```
/diagnose pacing in Act II
```
Focused check on a specific concern without the full pass sequence.

### Pre-Writing Pathway
```
/pre-writing
```
For writers with an idea but no manuscript. Calibrates writer mode (architecture-first vs. discovery-first), inventories seeds, builds a protagonist engine, offers 2–3 structural candidates, sets complexity caps, and produces a Structural Plan or Minimal Viable Plan. When the writer returns with a draft, the Re-Entry Diff Protocol compares intent against execution.

### Plot Coaching
```
/plot-coach
```
Helps choose or fix a plot structure. Works for pre-drafting planning, stuck drafts, and structural pivots.

### Specialized Audit
```
/audit character
/audit shelf
/audit
```
Run a named audit or list all 28 available audits.

### Research Mode
```
/research comp
/research fact-check
```
Internet-enabled research to validate comps, check facts, verify genre currency, or surface representation context.

## Model Requirements

APODICTIC is designed for and tested on **Claude Opus**. It will run on smaller models (Sonnet, Haiku), but with meaningfully degraded results — particularly in severity honesty, thematic interpretation, deliberate ambiguity handling, and fix quality. The framework includes anti-sycophancy protocols, adversarial self-checks, and severity floor rules that require strong instruction-following to work as intended. If you're evaluating the framework, use the best model available.

## Framework Version

Current version is in `.claude-plugin/plugin.json`. Capabilities: 48 plot spines across 12 families, 25 specialized audits (including 3 universal), 3 tag audits, 4 research modes, 11 core passes, the evaluative Pass 11 gate, the pre-writing pathway, and the intake router. Includes contract-driven and finding-driven audit integration pipeline.

## License

This work is licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).

You can use, adapt, and share this framework for non-commercial purposes, with attribution and under the same license. See [LICENSE](LICENSE) for details.

## Author

anotherpanacea
