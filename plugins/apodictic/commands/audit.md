---
description: Run a specialized audit or list available audits
argument-hint: [audit-name] or no argument to list all
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

Run a specialized audit from the APODICTIC Development Editor framework.

Load the `specialized-audits` skill.

**If no argument is provided** (or argument is "list" or "help"):
Display the complete list of available audits with brief descriptions:

- **character** — Character Architecture: psychology engine, arc types, agency, voice
- **scene-turn** — Scene Turn: scene-level mechanics, entry/exit charge, turns
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
- **plot** — Plot Architecture: spine diagnosis (use `/plot-coach` for selection)

**If an argument is provided:**
Load the named audit's reference file and run the full audit on the manuscript. Apply all logic gates, produce flagged findings with specific scene/page evidence, and output a focused audit report.

Manuscript context: $ARGUMENTS
