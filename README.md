# APODICTIC: anotherpanacea's Development Editor

Developmental editing that listens before diagnosing.

## Why This Exists

Every AI writing tool I tried wanted to rewrite my prose. I didn't need a co-writer. I needed what a good developmental editor does — read my manuscript, figure out what it's trying to be, and tell me where it's working and where it isn't. Structurally. Without touching my sentences.

So I built one.

## How It Works

APODICTIC reads a manuscript, predicts its "contract" (genre, reader promise, controlling idea) from the text alone, then measures the work against that contract. When the inferred contract doesn't match what you intended, that's the diagnostic signal — it means the text isn't communicating what you think it is.

It runs 11 analytical passes: reverse outline, reader experience mapping, structural diagnosis, character architecture, reveal economy, pacing analysis, and more — all calibrated to your genre. Genre modules adjust what counts as a problem. A slow opening is a feature in literary fiction, a defect in a thriller.

**The Firewall:** APODICTIC diagnoses problems and identifies classes of solution. It never invents content — no new plot events, characters, dialogue, or imagery. You're the writer. It's the analyst.

## Beyond Full Edits

APODICTIC isn't just for finished drafts.

- **Pre-writing pathway** for writers who have an idea but no manuscript — takes you from seed to draftable structure
- **Plot coach** with 48 structural spines across 12 families (not just three-act)
- **28 specialized audits** including 3 universal (stakes system, decision pressure, scene turn), plus scene function, shelf positioning, emotional craft, AI-prose detection, worldbuilding integration, force architecture, and more
- **4 internet-enabled research modes** for comp validation, fact-checking, genre currency, and representation context
- **Genre calibration** across literary fiction, horror, mystery, thriller, SF/F, romance, and hybrids

## Install

```
/plugin marketplace add anotherpanacea-eng/apodictic
/plugin install apodictic@apodictic
```

Then type `/start` — it asks you three questions to figure out what you need.

Requires Claude Code 1.0.33+ or Cowork mode.

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

## Project Docs

- [ROADMAP.md](ROADMAP.md) — what's planned after publication
- [BIBLIOGRAPHY.md](BIBLIOGRAPHY.md) — sources and influences (~155 works cited)
- [CONTRIBUTING.md](CONTRIBUTING.md) — how to contribute, changelog policy
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)

## License

This work is licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).

You can use, adapt, and share this framework for non-commercial purposes, with attribution and under the same license.

## Author

Joshua A. Miller, PhD
