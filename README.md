# APODICTIC: anotherpanacea's Development Editor

Developmental editing that listens before diagnosing.

```mermaid
flowchart TD
    S(["Type /start"]) --> Q1{"1 · What do you have?"}
    Q1 -->|An idea| Q2
    Q1 -->|Scattered fragments| Q2
    Q1 -->|A partial draft| Q2
    Q1 -->|A complete draft| Q2
    Q1 -->|A series| Q2
    Q2{"2 · What do you want?<br/>(your options depend on what you have)"} --> Q3{"3 · Anything that changes how we work?<br/>deadline · nonfiction · sensitive content · editing for someone else · writing group"}
    Q3 --> L["Your workflow<br/>→ editorial letter or structural plan"]
    L -. the Firewall:<br/>never .-> X["rewrite your prose"]
    style X stroke-dasharray: 5 5,color:#9ca3af
```

*Every edit starts at `/start`: three plain-language questions — the second's options depend on the first — route you to the right workflow. ([Walk the specific routes in the interactive route explorer](https://anotherpanacea-eng.github.io/apodictic/plugins/apodictic/route-explorer.html).)*

## Why This Exists

Every AI writing tool I tried wanted to rewrite my prose. I didn't need a co-writer. I needed what a good developmental editor does — read my manuscript, figure out what it's trying to be, and tell me where it's working and where it isn't. Structurally. Without touching my sentences.

So I built one.

## How It Works

APODICTIC reads a manuscript, predicts its "contract" (genre, reader promise, controlling idea) from the text alone, then measures the work against that contract. When the inferred contract doesn't match what you intended, that's the diagnostic signal — it means the text isn't communicating what you think it is.

It runs 11 analytical passes: reverse outline, reader experience mapping, structural diagnosis, character architecture, reveal economy, pacing analysis, and more — all calibrated to your genre. Genre modules adjust what counts as a problem. A slow opening is a feature in literary fiction, a defect in a thriller.

**The Firewall:** APODICTIC diagnoses problems and identifies classes of solution. It never invents content — no new plot events, characters, dialogue, or imagery. You're the writer. It's the analyst.

## See It in Action

You don't have to install anything to see what APODICTIC produces. These open as live, rendered pages:

- **[A sample editorial letter →](https://anotherpanacea-eng.github.io/apodictic/sample-editorial-letter.html)** — the main deliverable: a structural diagnosis with severity-ranked findings and classes of solution, prose left untouched. ([a second example](https://anotherpanacea-eng.github.io/apodictic/sample-editorial-letter-2.html))
- **[A targeted audit letter →](https://anotherpanacea-eng.github.io/apodictic/sample-targeted-audit-letter.html)** — a focused single-audit deep dive.
- **[Pre-writing output →](https://anotherpanacea-eng.github.io/apodictic/sample-pre-writing-output.html)** — what you get starting from an idea instead of a draft.

Two interactive maps of the tool itself:

- **[Overview dashboard →](https://anotherpanacea-eng.github.io/apodictic/plugins/apodictic/overview-dashboard.html)** — the whole system at a glance: the router, what each pass analyzes, genre modules, audits, and the 50 plot spines.
- **[Route explorer →](https://anotherpanacea-eng.github.io/apodictic/plugins/apodictic/route-explorer.html)** — answer the same three questions `/start` asks and watch where it routes you.

*(Tip: these are rendered links. Opening the raw `.html` files directly in the GitHub file browser shows source code, not the page.)*

## Beyond Full Edits

APODICTIC isn't just for finished drafts.

- **Partial manuscript diagnostic** — stuck mid-draft? APODICTIC runs on what exists without penalizing missing structure. Adds momentum tracking, stall detection, and a setup inventory showing what your draft has committed to. Synthesis focuses on what's working, what's stalling, and where to go next
- **Fragment synthesis** — scattered scenes and notes but no continuous narrative? Fragment Synthesis clusters your material, maps connections, and produces a candidate structure showing what your fragments add up to
- **Revision Coach** (`/coach`) — post-diagnostic coaching that helps you plan revision sessions without doing the revision for you. Four modes: session planning (leverage-ranked priorities matched to your available time), stuck-point coaching (8-type block diagnosis with structurally-informed writing experiments), momentum tracking (session-over-session progress), and deadline coaching (honest triage with revision calendar). Includes 7 structural prompt families, a stuck-point exercise library, nocebo inoculation, and no-prompt zones for states where more structure would make things worse
- **Series Continuity** (`/audit series-continuity`) — cross-volume consequence tracking for multi-book series. Five diagnostic channels: character state, world rules, unresolved threads, hope calibration, and intentional discontinuities. Rolling `Series_State.md` persists across volumes
- **Pre-writing pathway** for writers who have an idea but no manuscript — takes you from seed to draftable structure
- **Plot coach** with 50 structural spines across 12 families (not just three-act)
- **35 available audits** (3 universal, 17 craft, 10 genre, 5 tag) including scene function, shelf positioning, emotional craft, AI-prose detection, worldbuilding integration, force architecture, reception risk, and intimacy/consent coverage
- **6 internet-enabled research modes** for citation verification, comp validation, fact-checking, field reconnaissance (counterevidence + literature gaps), genre currency, and representation context
- **Nonfiction Argument Engine** for persuasive, argument-shaped nonfiction (policy briefs, op-eds, testimony) — argument spine, support, and warrant, with Red-Team, Persuasion, and Evidence companions
- **Legal Risk Register** (`/legal-risk`) — flags possible defamation, privacy, and rights exposure for a lawyer's review. It flags, never adjudicates — not legal advice
- **Feedback triage and beta-reader instrument** (`/triage-feedback`, `/reader-questions`) — sort and prioritize beta-reader/editor feedback, and turn a diagnosis into targeted reader questions
- **Project addressability** (`/projects`) — list, resume, and tidy editing projects from saved diagnostic state, with Retcon Planning and State Cards
- **Manuscript-structure visualizations** plus **Diagnostic-Vocabulary** and **Editor-Scaffolding** operator modes
- **Genre calibration** across literary fiction, horror, mystery, thriller, SF/F, romance, and hybrids

## Install

APODICTIC works best on strong frontier models with enough context for large-manuscript analysis. 

### Which install do I need?

Pick the row for the app you'll actually run APODICTIC in — that's the only thing that decides your path:

| You're using… | Go to | Fastest path |
|---|---|---|
| **Antigravity** | [Antigravity (Native)](#antigravity-native) | Workspace Isolation — download the zip, open the folder, `/start` |
| **Codex** | [Codex](#codex) | Download the zip, open the `codex/` folder, install from the local marketplace |
| **Claude Code (CLI / terminal)** | [Claude Code (CLI)](#claude-code-cli) | Two `/plugin` commands |
| **Cowork (desktop app)** | [Cowork (Desktop App)](#cowork-desktop-app) | Add the marketplace from GitHub, then install |

Whichever path you take, it ends the same way: start a fresh session and type `/start`.

### Antigravity (Native)

APODICTIC supports two modes of execution in Antigravity: Workspace Isolation (recommended) and Global Installation.

#### Method 1: Workspace Isolation (Recommended)
This method keeps APODICTIC isolated to its own project context, safely containing manuscript analysis.

1. Download **`apodictic-antigravity.zip`** from the [latest release](https://github.com/anotherpanacea-eng/apodictic/releases/latest) and unzip it. (No clone or build step — the workspace is prebuilt.)
2. Open the unzipped `antigravity/` folder as your **workspace root**.
3. Start a fresh thread and type `/start`.

Prefer to build from source? Clone the repo, run `node scripts/build-antigravity.mjs`, and open the generated `antigravity/` folder instead.

#### Method 2: Global Installation
If you want APODICTIC available globally across all of your Antigravity workspaces.

1. Download and unzip **`apodictic-antigravity.zip`** from the [latest release](https://github.com/anotherpanacea-eng/apodictic/releases/latest) (or clone the repo and run `node scripts/build-antigravity.mjs`).

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

### Codex

1. Download **`apodictic-codex-marketplace.zip`** from the [latest release](https://github.com/anotherpanacea-eng/apodictic/releases/latest) and unzip it. (No clone or build step — the workspace is prebuilt.)
2. Open the unzipped `codex/` folder as your Codex workspace root.
3. In Codex, open the Plugins view and install `APODICTIC` from the local marketplace.
4. Start a fresh thread and run `apodictic-start`.

If APODICTIC does not appear, the usual cause is opening the wrong folder. Codex must be opened on the generated `codex/` directory, not the repo root.

Prefer to build from source? Clone the repo, run `node scripts/build-codex.mjs`, and open the generated `codex/` folder instead.

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

## Your First Five Minutes

1. **Install** APODICTIC for your host (see above), then start a fresh session.
2. **Type `/start`.** It asks three plain-language questions — what you have (an idea, fragments, a partial draft, a complete draft, or a series), what you want, and anything that should change how it works.
3. **Give it your manuscript** when it asks — paste it, or point it at the file.
4. **Read the editorial letter.** You get a structural diagnosis like the [samples above](#see-it-in-action): what's working, what isn't, ranked by severity, each with a class of solution. It never rewrites your prose.
5. **Decide what's next.** The letter ends by pointing you onward — a focused `/audit`, revision planning with `/coach`, or a submission-readiness check with `/ready`.

Not sure where to begin? Just `/start`. When in doubt, that's the front door.

## Commands

**Start here:**
- `/start` — I have a manuscript — what should I do with it?
- `/apodictic` — What can this plugin do? Where do I start?

**Diagnostic workflows:**
- `/ready` — Is this ready to submit?

**Focused tools:**
- `/audit` — Run a specific deep-dive analysis.
- `/research` — I need internet-assisted verification.
- `/coach` — I have a diagnosis — how do I revise?
- `/plot-coach` — Is my plot structure working?
- `/legal-risk` — Flag legal exposure (defamation, privacy, rights) for a lawyer's review.
- `/triage-feedback` — Sort and prioritize beta-reader / editor feedback.
- `/reader-questions` — Turn my diagnosis into targeted beta-reader questions.

**Setup:**
- `/pre-writing` — I have an idea but no manuscript yet.
- `/new-project` — Set up a new editing project.
- `/projects` — List, resume, and tidy my editing projects.

## Key Terms

A few words you'll meet in the README and in your first editorial letter:

- **Contract** — what APODICTIC infers your manuscript is *trying to be*: its genre, the promise it makes to readers, and its controlling idea. It predicts this from the text alone, then measures the book against it. When the inferred contract doesn't match what you intended, that mismatch is the core diagnostic signal.
- **Controlling idea** — the central meaning or argument the story makes through its events. Part of the contract.
- **The Firewall** — the rule that APODICTIC diagnoses structure and names *classes* of solution but never writes content (no plot, characters, dialogue, or prose). You're the writer; it's the analyst.
- **Pass** — one analytical lens over the manuscript (reverse outline, reader experience, reveal economy, and so on). A development edit runs the passes your question requires.
- **Macro block** — a group of passes organized around a writer question (e.g. "Structure Map," "Reader Dynamics"). Eight blocks in all.
- **Audit** — a specialized deep-dive beyond the core passes (genre, craft, or tag), run via `/audit`.
- **Genre module** — recalibrates what counts as a problem for your genre. A slow opening is a feature in literary fiction, a defect in a thriller.
- **Editorial letter** — the main deliverable: a structural diagnosis with severity-ranked findings, each paired with a class of solution.
- **Severity tiers** — every finding is ranked **Must-Fix**, **Should-Fix**, or **Could-Fix**. Severity is locked before any charity reframing, so it can't be quietly softened (the "Deficit Lock").
- **Spine** — a plot-structure paradigm (Hero's Journey, Mystery, Spiral, …). APODICTIC works with 50 spines across 12 families, not just three-act.
- **Reverse outline** — reconstructing what each scene *actually* does, as opposed to what you intended — the starting point for structural diagnosis.

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
