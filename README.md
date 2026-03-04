# APODICTIC: anotherpanacea's Development Editor

AI Developmental Editing. *Necessarily, Everything Follows.*

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

Requires **Claude Opus** for intended results. Runs on smaller models with degraded severity honesty and thematic interpretation.

### Claude Code (CLI)

```
/plugin marketplace add anotherpanacea-eng/apodictic
/plugin install apodictic@anotherpanacea-eng-apodictic
```

### Cowork (Desktop App)

Go to **Customize > Browse > Personal > +** and select **Add marketplace from GitHub**. Enter `anotherpanacea-eng/apodictic`, then install the plugin.

Or download `apodictic.plugin` from the [latest release](https://github.com/anotherpanacea-eng/apodictic/releases/latest) and upload it through Cowork. (Mac users: if your browser auto-unzips the download, re-zip the folder and rename it to `apodictic.plugin`.)

---

Then type `/start` — it asks you three questions to figure out what you need.

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

## Troubleshooting

### Windows / Cowork Desktop: Plugin Installs Then Reverts

Some users on Windows PCs have reported issues installing the plugin through Cowork's desktop app. The symptoms include:

- The plugin appears to install but then reverts to "not installed"
- Pointing Cowork to a local folder produces sandbox/virtiofs errors like:
  ```
  sandbox-helper: failed to unmount host share (virtiofs at /mnt/.virtiofs-root: invalid argument)
  ```

These are **Cowork platform issues**, not plugin bugs. Cowork's desktop app runs a sandboxed Linux VM, and on some Windows machines the virtualization layer (virtiofs/Hyper-V) doesn't initialize correctly. The plugin has no control over this layer.

**Workarounds:**

1. **Use Claude Code (CLI) instead** — it doesn't rely on sandboxing or virtualization. See the install instructions above, then run `/start`.
2. **Report the sandbox error to Cowork** — the virtiofs mount failure is a platform bug that their team would need to address.
3. **Check your Windows virtualization settings** — ensure Hyper-V and/or WSL2 are enabled and up to date (`wsl --update` from PowerShell).

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
