---
description: Run a specialized audit or list available audits
argument-hint: [audit-name] or no argument to list all
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

Run a specialized audit from the APODICTIC Development Editor framework.

Load the `specialized-audits` skill.

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
- **shelf** — Shelf & Positioning: target reader, genre contract, comps, signals
- **series** — Series & Composite Novel: standalone function, hope calibration
- **memoir** — Memoir & Creative Nonfiction: truth-craft balance, narrator reliability
- **narrative-nonfiction** — Narrative Nonfiction Craft: scene construction in fact-based work
- **consent** — Consent Complexity: consent timeline, boundary tracking
- **interiority** — Interiority Preservation: POV interiority in high-intensity scenes
- **female-interiority** — Female Interiority: agency, desire, independence
- **banister** — Banister (Epistemic Humility): rhetorical fairness, straw opposition
- **comedy** — Comedy & Satire: timing, landing rate, tonal integration
- **historical** — Historical Fiction: period authenticity, research integration
- **queer** — Queer Romance/Erotica: pronoun clarity, tropes, joy/struggle
- **fanfic** — Fan Fiction Conversion: IP scaffolding, worldbuilding gaps
- **short** — Short Fiction: compression, single-effect, ending resonance
- **literary-craft** — Literary Craft Deep Dive: load-bearing vs. ornamental prose, defamiliarization, 9 hybrid calibrations
- **ai-prose** — AI-Prose Calibration: voice singularity, lexical genericism, echo stacks, register seams

### Genre Audits
- **sff-worldbuilding** — SFF Worldbuilding Integration: five-dimension framework, load-bearing analysis
- **horror-craft** — Horror Craft Integration: dread architecture, consequence embodiment, 9 subgenre calibrations
- **mystery-thriller** — Mystery/Thriller Architecture: information pressure, clue economy, fair play
- **force** — Force Architecture: force delivery, consequence/escalation tracking, inert force diagnosis

### Tag Audits
- **cozy** — Cozy Tag: safety envelope, belonging engine, recovery rhythm
- **philosophical** — Philosophical Tag: question architecture, dramatic embodiment, conceptual progression
- **erotic** — Erotic Content: intimate scene integration, load-bearing analysis, consent calculus

### Plot Audits (use `/plot-coach` for selection and coaching)
- **plot** — Plot Architecture: spine diagnosis (48 spines across 12 families)

**If an argument is provided:**
Load the named audit's reference file and run the full audit on the manuscript. Apply all logic gates, produce flagged findings with specific scene/page evidence, and output a focused audit report.

Manuscript context: $ARGUMENTS
