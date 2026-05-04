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

- **Partial manuscript diagnostic** — stuck mid-draft? APODICTIC runs on what exists without penalizing missing structure. Adds momentum tracking, stall detection, and a setup inventory showing what your draft has committed to. Synthesis focuses on what's working, what's stalling, and where to go next
- **Fragment synthesis** — scattered scenes and notes but no continuous narrative? Fragment Synthesis clusters your material, maps connections, and produces a candidate structure showing what your fragments add up to
- **Revision Coach** (`/coach`) — post-diagnostic coaching that helps you plan revision sessions without doing the revision for you. Four modes: session planning (leverage-ranked priorities matched to your available time), stuck-point coaching (8-type block diagnosis with structurally-informed writing experiments), momentum tracking (session-over-session progress), and deadline coaching (honest triage with revision calendar). Includes 7 structural prompt families, a stuck-point exercise library, nocebo inoculation, and no-prompt zones for states where more structure would make things worse
- **Series Continuity** (`/audit series-continuity`) — cross-volume consequence tracking for multi-book series. Five diagnostic channels: character state, world rules, unresolved threads, hope calibration, and intentional discontinuities. Rolling `Series_State.md` persists across volumes
- **Pre-writing pathway** for writers who have an idea but no manuscript — takes you from seed to draftable structure
- **Plot coach** with 50 structural spines across 12 families (not just three-act)
- **33 available audits** (3 universal, 15 craft, 10 genre, 5 tag) including scene function, shelf positioning, emotional craft, AI-prose detection, worldbuilding integration, force architecture, reception risk, and intimacy/consent coverage
- **6 internet-enabled research modes** for citation verification, comp validation, fact-checking, field reconnaissance (counterevidence + literature gaps), genre currency, and representation context
- **Genre calibration** across literary fiction, horror, mystery, thriller, SF/F, romance, and hybrids

## Install

APODICTIC works best on strong frontier models with enough context for large-manuscript analysis. 

### Antigravity (Native)

APODICTIC supports two modes of execution in Antigravity: Workspace Isolation (recommended) and Global Installation.

#### Method 1: Workspace Isolation (Recommended)
This method keeps APODICTIC isolated to its own project context, safely containing manuscript analysis.

1. Clone this repo.
2. From the repo root, run the native builder:

```bash
node scripts/build-antigravity.mjs
```

3. Open the newly generated `antigravity/` folder as your **workspace root**.
4. Start a fresh thread and type `/start`.

#### Method 2: Global Installation
If you want APODICTIC available globally across all of your Antigravity workspaces.

1. Clone this repo and build the native target:

```bash
node scripts/build-antigravity.mjs
```

2. Symlink the generated plugin into your global Antigravity data directory:

```bash
mkdir -p ~/.gemini/antigravity/plugins
ln -s "$(pwd)/antigravity/plugins/apodictic" ~/.gemini/antigravity/plugins/apodictic
```

3. Copy the workflow definitions into the `.agents/workflows` directory of whatever active workspace you want to run APODICTIC from:

```bash
cp -r antigravity/.agents/workflows/* /path/to/your/workspace/.agents/workflows/
```
4. Start a fresh thread and type `/start`.

### Codex (legacy build path)

1. Clone this repo.
2. From the repo root, run:

```bash
node scripts/build-codex.mjs
```

3. Open the generated `codex/` folder as your Codex workspace root.
4. In Codex, open the Plugins view and install `APODICTIC` from the local marketplace.
5. Start a fresh thread and run `apodictic-start`.

If APODICTIC does not appear, the usual cause is opening the wrong folder. Codex must be opened on the generated `codex/` directory, not the repo root.

### Claude Code / Cowork (legacy host flow)

The instructions below are the older Claude-oriented install path.

### Claude Code (CLI)

```
/plugin marketplace add anotherpanacea-eng/apodictic
/plugin install apodictic@anotherpanacea-eng-apodictic
```

### Cowork (Desktop App)

Go to **Customize > Browse > Personal > +** and select **Add marketplace from GitHub**. Enter `anotherpanacea-eng/apodictic`, then install the plugin.

Or download `apodictic.plugin` from the [latest release](https://github.com/anotherpanacea-eng/apodictic/releases/latest) and upload it through Cowork. (Mac users: if your browser auto-unzips the download, re-zip the folder and rename it to `apodictic.plugin`.)

### Updating to a new version

```bash
claude plugin marketplace update apodictic
```

Or `/plugin marketplace update apodictic` from inside Claude Code (CLI). For Cowork Desktop, use the marketplace's update control in the Customize panel.

**Then fully quit and relaunch Claude Code / Cowork** — a restart is required to apply the new version. The marketplace cache will refresh on update, but the running process keeps the previous version loaded until relaunched.

---

Then type `/start` — it asks you three questions to figure out what you need.

## Commands

**Start here:**
- `/start` — I have a manuscript — what should I do with it?

**Diagnostic workflows:**
- `/develop-edit` — What's wrong with my manuscript?
- `/diagnose` — I have a specific concern — is it a real problem?
- `/ready` — Is this ready to submit?

**Focused tools:**
- `/audit` — Run a specific deep-dive analysis.
- `/research` — I need internet-assisted verification.
- `/coach` — I have a diagnosis — how do I revise?
- `/plot-coach` — Is my plot structure working?

**Setup:**
- `/pre-writing` — I have an idea but no manuscript yet.
- `/new-project` — Set up a new editing project.

`/revision-plan` is a compatibility alias for `/coach`.

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
