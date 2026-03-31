---
description: Run a specialized audit or list available audits
argument-hint: [audit-name] or no argument to list all
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

Run a specialized audit from the APODICTIC Development Editor framework.

Load `../skills/specialized-audits/SKILL.md`.

**If no argument is provided** (or argument is "list" or "help"):
Display the complete list of available audits with brief descriptions:

### Universal Audits (recommended for every manuscript)
- **stakes** — Stakes System: pressure architecture, escalation geometry, consequence engine
- **decision-pressure** — Decision Pressure: choice plausibility, option visibility, tradeoff reality
- **scene-turn** — Scene Turn: scene-level mechanics, entry/exit charge, turns (Bickham)

### Craft Audits
- **character** — Character Architecture: psychology engine, arc types, agency, voice
- **emotional-craft** — Emotional Craft: emotional precision, earned moments
- **dialectical** — Dialectical Clarity: argument structure, rhetorical fairness
- **shelf** — Shelf Positioning: target reader, genre contract, comps, signals
- **series** — Series & Composite Novel: standalone function, hope calibration
- **interiority** — Interiority Preservation: POV interiority in high-intensity scenes
- **female-interiority** — Female Interiority: agency, desire, independence
- **literary-craft** — Literary Craft: load-bearing vs. ornamental prose, defamiliarization, hybrid calibrations
- **banister** — Banister (Epistemic Humility): rhetorical fairness, straw opposition
- **ai-prose** — AI-Prose Calibration: voice singularity, lexical genericism, echo stacks, register seams
- **force** — Force Architecture: force delivery, consequence/escalation tracking, inert force diagnosis
- **short** — Short Fiction: compression, single-effect, ending resonance
- **compression** — Compression: expendable material, cut list, word-savings map
- **reception-risk** — Reception Risk: reception exposure, extractability, sensitivity-review handoff
- **series-continuity** — Cross-Volume Series Continuity: consequence propagation, state tracking, thread inventory, hope calibration across volumes

### Genre Audits
- **comedy** — Comedy & Satire: timing, landing rate, tonal integration
- **historical** — Historical Fiction: period authenticity, research integration
- **memoir** — Memoir & Creative Nonfiction: truth-craft balance, narrator reliability
- **narrative-nonfiction** — Narrative Nonfiction Craft: scene construction in fact-based work
- **fanfic** — Fan Fiction Conversion: IP scaffolding, worldbuilding gaps
- **sff-worldbuilding** — SFF Worldbuilding Integration: five-dimension framework, load-bearing analysis
- **horror-craft** — Horror Craft Integration: dread architecture, consequence embodiment, subgenre calibrations
- **supernatural-horror** — Supernatural Horror: belief threshold, wrongness tracking, supernatural pressure architecture, 8 subgenre calibrations
- **grimdark** — Grimdark / Dark Fantasy: moral argument, violence economy, power anatomy, compromise pressure, consequence persistence, hope calibration
- **mystery-thriller** — Mystery/Thriller Architecture: information pressure, clue economy, fair play

### Tag Audits
- **cozy** — Cozy Tag: safety envelope, belonging engine, recovery rhythm
- **philosophical** — Philosophical Tag: question architecture, dramatic embodiment, conceptual progression
- **erotic** — Erotic Content: intimate scene integration, load-bearing analysis, consent calculus
- **consent** — Consent Complexity: consent timeline, boundary tracking
- **queer** — Queer Romance/Erotica: pronoun clarity, tropes, joy/struggle

### Plot Architecture
Plot structure analysis uses a separate skill. Run `apodictic-plot-coach` for spine diagnosis (50 spines across 12 families), selection coaching, and structural triage.

### Nonfiction Argument Engine
The **dialectical** audit is the entry point for all argument-shaped nonfiction. It produces `Argument_State.md`, which companion modules then consume:
- `apodictic-audit dialectical` — run first; produces the shared argument state
- `apodictic-audit argument-red-team` — hostile-reader pressure test (requires `Argument_State.md`)
- `apodictic-audit argument-persuasion` — audience calibration and framing guidance (requires `Argument_State.md`)
- `apodictic-audit argument-evidence` — provenance, testimony calibration, verification queue (requires `Argument_State.md`)
- `apodictic-coach` — argument revision coaching (reads `Argument_State.md` + companion annotations)

Companion modules will refuse to run without a populated `Argument_State.md`. Run `apodictic-audit dialectical` first.

**If an argument is provided:**
Load the named audit's reference file from `../skills/specialized-audits/references/` and run the full audit on the manuscript. Apply all logic gates, produce flagged findings with specific scene/page evidence, and output a focused audit report.

Manuscript context: $ARGUMENTS
