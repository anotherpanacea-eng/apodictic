# Writer-Question Surface Hardening — Implementation Spec

**Status:** Planned
**Target:** v1.4.0
**Last updated:** 2026-03-20

---

## Goal

Make every user-facing surface writer-question shaped without restructuring internals. Writers should never see pass numbers, skill names, or framework jargon as their primary navigational layer.

---

## 1. Command Taxonomy in Release Registry

### What to build

Add a `commands` key to `release-registry.json` with structured metadata for every public command.

### Schema

```json
{
  "commands": [
    {
      "command": "/start",
      "category": "entry",
      "status": "primary",
      "routerEquivalent": null,
      "writerQuestion": "I have a manuscript — what should I do with it?",
      "description": "Recommended entry point. Routes to the right workflow in 2–3 questions."
    },
    {
      "command": "/develop-edit",
      "category": "diagnostic",
      "status": "first_class_shortcut",
      "routerEquivalent": "/start → full diagnostic",
      "writerQuestion": "What's wrong with my manuscript?",
      "description": "Run a full development edit."
    }
  ]
}
```

### Command inventory

| Command | Status | Writer Question |
|---------|--------|-----------------|
| `/start` | `primary` | "I have a manuscript — what should I do with it?" |
| `/develop-edit` | `first_class_shortcut` | "What's wrong with my manuscript?" |
| `/diagnose` | `first_class_shortcut` | "I have a specific concern — is it a real problem?" |
| `/ready` | `first_class_shortcut` | "Is this ready to submit?" |
| `/pre-writing` | `first_class_shortcut` | "I have an idea but no manuscript yet." |
| `/coach` | `first_class_shortcut` | "I have a diagnosis — how do I revise?" |
| `/plot-coach` | `first_class_shortcut` | "Is my plot structure working?" |
| `/audit` | `first_class_shortcut` | "Run a specific deep-dive analysis." |
| `/research` | `first_class_shortcut` | "I need internet-assisted verification." |
| `/new-project` | `first_class_shortcut` | "Set up a new editing project." |
| `/revision-plan` | `compat_alias` | (alias for `/coach`) |

### Implementation

1. Add the `commands` array to `release-registry.json`
2. Add a `buildCommandTaxonomy()` function to `release-generate.mjs` that writes the grouped command list to all public surfaces
3. Existing hand-maintained command lists in READMEs, help surfaces, and marketplace metadata are replaced by generated output

### Files to modify

- `release-registry.json` — add `commands` key
- `scripts/release-generate.mjs` — add generation function
- `README.md` — replace command list with generated version
- `plugins/apodictic/README.md` — replace command list with generated version
- Marketplace JSON files — description already handled by existing generator

---

## 2. Doc Sync

### What to build

Every public doc that lists commands uses the same grouped presentation generated from the registry. No more hand-maintained command lists that drift.

### Grouped presentation format

```markdown
**Start here:**
- `/start` — I have a manuscript — what should I do with it?

**Diagnostic workflows:**
- `/develop-edit` — What's wrong with my manuscript?
- `/diagnose` — I have a specific concern — is it a real problem?
- `/ready` — Is this ready to submit?

**Focused tools:**
- `/audit` — Run a specific deep-dive analysis
- `/research` — Internet-assisted verification
- `/plot-coach` — Is my plot structure working?
- `/coach` — I have a diagnosis — how do I revise?

**Setup:**
- `/pre-writing` — I have an idea but no manuscript yet
- `/new-project` — Set up a new editing project
```

### Files to sync

- `README.md`
- `plugins/apodictic/README.md`
- `overview-dashboard.html` (if it lists commands)
- `route-explorer.html` (if it lists commands)

### Implementation

Add a `buildGroupedCommandList()` function to `release-generate.mjs`. The function reads from `release-registry.json` `commands` and outputs the grouped markdown. Replace the command sections in each target file using the same `replaceOrThrow` pattern the generator already uses.

---

## 3. Canonical 8-Block Macro Map

### What to build

Resolve the Pass 4 ambiguity in `pass-dependencies.md` §3. Currently Pass 4 (Emotional Value Tracking) is parenthetically attached to Character Architecture. It should be its own block: **Emotional Dynamics**.

### The 8 blocks

| Macro Block | Internal Passes | Writer Question |
|-------------|----------------|-----------------|
| Structure Map | 0 + 2 | "Is the structure working?" |
| Reader Dynamics | 1 + 3 | "Does the pacing hold?" |
| Character Architecture | 5 + 7 | "Are my characters landing?" |
| Emotional Dynamics | 4 | "Are the emotional beats earning their weight?" |
| Scene Delivery | 6 | "Are the scenes doing their jobs?" |
| Reveal Economy | 8 | "Is the information flow right?" |
| Theme & Continuity | 9 + 10 | "Does it cohere?" |
| Submission Readiness | 11 | "Is this ready?" |

### Changes from current state

1. **Pass 4** moves from Character Architecture to its own block (Emotional Dynamics)
2. **Pass 7** (POV & Voice) moves from Scene Delivery to Character Architecture — voice is a character concern, not a scene concern
3. **Pass 6** (Scene Function) stands alone in Scene Delivery rather than sharing with Pass 7
4. Concern → Minimum pass set table in §2 updated to match

### Files to modify

- `plugins/apodictic/skills/core-editor/references/pass-dependencies.md` §3

### Design note

The concern → pass mapping in §2 already treats Emotional Dynamics as its own concern row (`0, 1, 4`). The macro block table in §3 is the only place where Pass 4 is subordinated. This change makes §3 consistent with §2.

---

## 4. Pass-Detail File Headers

### What to build

Add a standard header to each pass-detail output artifact that makes it legible without framework knowledge.

### Header format

```markdown
---
Macro block: Character Architecture
Writer question: Are my characters landing?
Pass: 5 (Character Audit)
---
```

### Implementation

Add the header template to the output section of `SKILL.md` (core-editor) or to a new output-format reference. The header is emitted by the LLM when producing pass artifacts — it's a prompt instruction, not a code change.

### Files to modify

- `plugins/apodictic/skills/core-editor/SKILL.md` — add header instruction to output format section
- Alternatively: `plugins/apodictic/skills/core-editor/references/output-policy.md` — add header spec

### Mapping table

| Pass | Macro Block | Writer Question |
|------|-------------|-----------------|
| 0 | Structure Map | Is the structure working? |
| 1 | Reader Dynamics | Does the pacing hold? |
| 2 | Structure Map | Is the structure working? |
| 3 | Reader Dynamics | Does the pacing hold? |
| 4 | Emotional Dynamics | Are the emotional beats earning their weight? |
| 5 | Character Architecture | Are my characters landing? |
| 6 | Scene Delivery | Are the scenes doing their jobs? |
| 7 | Character Architecture | Are my characters landing? |
| 8 | Reveal Economy | Is the information flow right? |
| 9 | Theme & Continuity | Does it cohere? |
| 10 | Theme & Continuity | Does it cohere? |
| 11 | Submission Readiness | Is this ready? |

---

## 5. Results Guide Artifact

### What to build

A new artifact produced after every diagnostic run: `[Project]_Results_Guide_[runlabel].md`. It maps each writer question to the relevant artifacts, audits, and state files from the run.

### Template

```markdown
# Results Guide — [Project Name]
_Run: [runlabel]_

## How to use this guide

Start with the **Editorial Letter** for the diagnosis and priority repairs.
Use this guide to find the detailed analysis behind each finding.

---

## Your results by question

### Is the structure working?
- Editorial Letter § Structure Map
- Detail: `[Project]_Pass0_Reverse_Outline_[runlabel].md`
- Detail: `[Project]_Pass2_Structural_Mapping_[runlabel].md`

### Does the pacing hold?
- Editorial Letter § Reader Dynamics
- Detail: `[Project]_Pass1_Reader_Experience_[runlabel].md`
- Detail: `[Project]_Pass3_Rhythm_[runlabel].md`

### Are my characters landing?
- Editorial Letter § Character Architecture
- Detail: `[Project]_Pass5_Character_Audit_[runlabel].md`
- Detail: `[Project]_Pass7_POV_Voice_[runlabel].md`

[... only blocks that ran appear ...]

## Specialized audits run
- [Audit Name]: `[artifact filename]`

## State files
- Diagnostic State: `Diagnostic_State.md`
- Argument State: `Argument_State.md` (if applicable)

## What to do next
- `/coach` — plan revision sessions from this diagnosis
- `/audit [name]` — run a focused deep-dive on a specific concern
```

### Implementation

The Results Guide is produced by the Synthesis step. After generating the editorial letter, the system produces the guide using the list of passes and audits that actually ran. Only blocks with completed passes appear.

### Files to modify

- `plugins/apodictic/skills/core-editor/SKILL.md` — add Results Guide to synthesis output instructions
- `plugins/apodictic/skills/core-editor/references/pass-dependencies.md` §1 Tier 3 — add Results Guide to synthesis outputs

---

## 6. Skill Names Scrubbed from User-Facing Copy

### What to do

Grep for skill names (`core-editor`, `specialized-audits`, `pre-writing-pathway`, `plot-architecture`, `revision-coach`) in all user-facing text. Replace with workflow descriptions.

### Replacement patterns

| Internal | User-facing |
|----------|-------------|
| "load the core-editor skill" | "start the diagnostic" |
| "load specialized-audits" | "run the audit" |
| "load pre-writing-pathway" | "start pre-writing" |
| "load plot-architecture" | "start plot coaching" |
| "load revision-coach" | "start revision coaching" |
| "enter the revision-coach skill" | "switch to revision coaching" |

### Scope

Only user-facing text — READMEs, command help, overview dashboard, marketplace copy. Internal references in SKILL.md files, router specs, and design docs keep skill names (they're the actual implementation identifiers).

### Files to check

- `README.md`
- `plugins/apodictic/README.md`
- `overview-dashboard.html`
- `route-explorer.html`
- Router output messages in `intake-router-runtime.md` (handoff language)

---

## 7. Handoff Language Standardized

### What to do

Cross-skill transitions in the router and post-diagnostic offers should use workflow language, not skill language.

### Current → Updated

| Current | Updated |
|---------|---------|
| "Loading specialized-audits skill..." | (silent — no announcement needed) |
| "Switching to revision-coach..." | "Ready to plan revision sessions." |
| "This will load the plot-architecture skill." | "Starting plot structure analysis." |
| "The pre-writing-pathway skill handles this." | "Let's start from your idea and build toward a draft." |

### Where handoffs happen

1. **Router → diagnostic:** `/start` routes to `/develop-edit` or `/diagnose` — already silent
2. **Diagnostic → audit:** Post-pass audit recommendation — already uses "Want me to run it?"
3. **Diagnostic → coaching:** Post-synthesis coaching offer — update language
4. **Router → pre-writing:** Direct routing — update language
5. **Router → plot coaching:** Direct routing — update language

### Files to modify

- `plugins/apodictic/skills/core-editor/references/intake-router-runtime.md` — handoff messages
- `plugins/apodictic/skills/core-editor/SKILL.md` — any transition language in output instructions

---

## What NOT to build in this phase

1. **Instrumentation / telemetry.** APODICTIC-Gemini has Cloud Run infrastructure that could support event logging, but there are no active external users generating usage data worth measuring. Revisit when external adoption justifies the build.

2. **Pass-detail filename renames.** Keep `Pass5_Character_Audit` etc. on disk. The Results Guide is the primary macro-block organizer. Bulk renames deferred unless usage shows writers navigate by detail files rather than the guide and letter.

3. **Skill merges or renames.** The five-skill architecture stays. Skill loading is invisible to users. Evaluate only if handoff pain surfaces.

4. **Editorial Letter renaming.** `Core_DE_Synthesis` and `Full_DE_Synthesis` work. The editorial letter *is* the synthesis. Don't alias.

5. **Command retirements.** All first-class shortcuts stay. `/revision-plan` stays as a compat alias. No commands are removed in this phase.

---

## Verification Checklist

- [ ] `release-registry.json` has `commands` key with all 11 commands
- [ ] All public docs show the same grouped command presentation
- [ ] `pass-dependencies.md` §3 shows 8 macro blocks with Pass 4 as Emotional Dynamics
- [ ] Pass-detail artifacts include macro-block headers
- [ ] Results Guide artifact produced after synthesis
- [ ] No skill names in user-facing text (READMEs, help, marketplace, dashboard)
- [ ] Cross-skill handoff messages use workflow language
- [ ] No behavior regression: all existing commands resolve to the same workflows
- [ ] Legacy artifact filenames unchanged on disk
