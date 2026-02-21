# APODICTIC: anotherpanacea's Development Editor

Developmental editing that listens before diagnosing.

AI-powered developmental editing framework for fiction and narrative nonfiction. Diagnoses structural issues in manuscripts through systematic passes, genre-calibrated analysis, and specialized audits.

## Install

```
/plugin marketplace add anotherpanacea/apodictic
/plugin install apodictic@apodictic
```

Then run `/start` to begin.

## What It Does

The Development Editor works like a human developmental editor: it reads a manuscript, infers what it's trying to do, and diagnoses where it succeeds or struggles. The system listens first — inferring authorial intent from the text — before measuring the work against that intent.

**Key design principle:** The editor predicts the manuscript's contract (genre, reader promise, controlling idea) from the text alone. Misalignments between the inferred contract and the author's stated intent are diagnostically valuable — they reveal where the text doesn't communicate what the author intended.

**The Firewall:** The system diagnoses problems and identifies classes of solution. It never invents content (new plot events, characters, dialogue, imagery). The author creates; the system analyzes.

## Components

- **core-editor** — The main workflow: intake protocol, 11 analysis passes, synthesis, revision rounds, genre calibration
- **pre-writing-pathway** — Guides writers from idea to draftable structure (no manuscript required)
- **plot-architecture** — Plot structure diagnosis (48 spines across 12 families), selection coaching, fantasy and series architecture
- **specialized-audits** — 18 deep-dive audits, 3 tag audits, and 4 internet-enabled research modes

## Commands

| Command | Description |
|---------|-------------|
| `/start` | **Recommended entry point.** Routes to the right workflow in 2-3 questions. |
| `/develop-edit` | Run a full development edit on a manuscript |
| `/new-project` | Initialize a new project with contract and diagnostic state |
| `/pre-writing` | Guide a writer from idea to draftable structure (no manuscript needed) |
| `/revision-plan` | Generate revision priorities from diagnostic state |
| `/diagnose` | Quick targeted diagnostic on a specific concern |
| `/plot-coach` | Plot structure selection and coaching |
| `/audit [name]` | Run a specialized audit (no argument lists all available) |
| `/research [mode]` | Run a research mode (no argument lists all available) |

## Requirements

Claude Code 1.0.33+ or Cowork mode.

## License

This work is licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).

You can use, adapt, and share this framework for non-commercial purposes, with attribution and under the same license.

## Author

Joshua A. Miller, PhD
