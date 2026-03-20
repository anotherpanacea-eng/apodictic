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
- **Revision Coach** (`/coach`) — post-diagnostic coaching that helps you plan revision sessions without doing the revision for you. Four modes: session planning (leverage-ranked priorities matched to your available time), stuck-point coaching (reframes the mechanism when a scene resists revision), momentum tracking (session-over-session progress), and deadline coaching (honest triage with revision calendar). Includes a stuck-point exercise library and three-way block diagnosis
- **Series Continuity** (`/audit series-continuity`) — cross-volume consequence tracking for multi-book series. Five diagnostic channels: character state, world rules, unresolved threads, hope calibration, and intentional discontinuities. Rolling `Series_State.md` persists across volumes
- **Pre-writing pathway** for writers who have an idea but no manuscript — takes you from seed to draftable structure
- **Plot coach** with 50 structural spines across 12 families (not just three-act)
- **33 available audits** (3 universal, 15 craft, 10 genre, 5 tag) including scene function, shelf positioning, emotional craft, AI-prose detection, worldbuilding integration, force architecture, reception risk, and intimacy/consent coverage
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
