# APODICTIC Development Editor: Module Index

## Core Framework

| File | Description |
|------|-------------|
| `AI_Development_Editor_Framework_v0.4.md` | Core framework (genre-agnostic) |

The core framework handles passes, synthesis, deliverables, and philosophy. Genre modules and specialized audits bolt on without modifying the core.

**Source-of-truth note:** `SKILL.md` is the canonical operational spec.  
`Module_Index.md` and `AI_Development_Editor_Complete_v0.4.4.md` are reference mirrors and may lag.

If instructions conflict:
1. `SKILL.md` wins for workflow behavior.
2. Dedicated module files win for module-specific rules.
3. Consolidated/reference docs defer.

**Branding note:** Public-facing name is `APODICTIC Development Editor (APDE)`.  
Legacy filenames containing `AI_Development_Editor_*` remain for backward compatibility.

---

## Genre Modules

Load after intake determines genre classification. Multiple modules can be active using the **Primary/Secondary System** (see below).

| Module | File | Priority Pass | Use When |
|--------|------|---------------|----------|
| Romance / Erotic | `Genre_Modules/Genre_Module_Romance_Erotic.md` | Pass 4 + Pass 5 | Central relationship is primary engine; erotic content significant |
| Horror (Psychological) | `Genre_Modules/Genre_Module_Horror_Psychological.md` | Pass 4 (certainty) + Pass 1 (dread) | Dread, reality destabilization, epistemic uncertainty central |
| Thriller / Suspense | `Genre_Modules/Genre_Module_Thriller_Suspense.md` | Pass 3 + Stakes Audit | Time pressure, escalating danger, constrained options |
| Mystery / Investigation | `Genre_Modules/Genre_Module_Mystery_Investigation.md` | Pass 8 | Puzzle, whodunit, investigation, fair-play information |
| Science Fiction / Fantasy | `Genre_Modules/Genre_Module_Science_Fiction_Fantasy.md` | Pass 10 (Rule Ledger) | Speculative elements, magic systems, future tech, secondary worlds |
| Literary Fiction | `Genre_Modules/Genre_Module_Literary_Fiction.md` | Pass 9 | Thematic depth, psychological complexity, ambiguity valued |

**Template for new modules:** `Templates/Genre_Module_TEMPLATE.md`

---

## Specialized Audits

Load after intake determines content concerns. Audits can stack with each other and with genre modules.

| Audit | File | Use When |
|-------|------|----------|
| Banister (Epistemic Humility) | `Specialized_Audits/Specialized_Audit_Banister.md` | Contested moral/political questions; work aspires to genuine complexity |
| Character Architecture | `Specialized_Audits/Specialized_Audit_Character_Architecture.md` | Arc types; agency tracking; psychology engine; voice distinctiveness; ensemble balance |
| Comedy and Satire | `Specialized_Audits/Specialized_Audit_Comedy_Satire.md` | Comedic voice; witty narrator; banter-heavy dialogue; satire; tonal balance |
| Consent Complexity | `Specialized_Audits/Specialized_Audit_Consent_Complexity.md` | Power imbalance; dubcon/noncon; consent as theme; conditioning narratives |
| Dialectical Clarity | `Specialized_Audits/Specialized_Audit_Dialectical_Clarity.md` | Argument structure; claim/evidence/scope discipline; objection handling; narrative-as-evidence |
| Emotional Craft | `Specialized_Audits/Specialized_Audit_Emotional_Craft.md` | Structurally competent but emotionally flat; emotion labeled not transmitted; flat dialogue; generic voice |
| Fan Fiction Conversion | `Specialized_Audits/Specialized_Audit_Fan_Fiction_Conversion.md` | Fanfic origins; worldbuilding gaps; character independence; IP scaffolding |
| Historical Fiction | `Specialized_Audits/Specialized_Audit_Historical_Fiction.md` | Period setting; real historical figures; research integration; historical attitudes |
| Interiority Preservation | `Specialized_Audits/Specialized_Audit_Female_Interiority.md` | Intimate scenes; POV interiority during sex; significant female characters |
| Memoir / Creative Nonfiction | `Specialized_Audits/Specialized_Audit_Memoir_Creative_Nonfiction.md` | Truth/memory tension; living person ethics; scene reconstruction; personal essay; Gornick Layer for meaning engine (GS/NI/SC/TD/BR/SEL/EP codes) |
| Narrative Nonfiction Craft | `Specialized_Audits/Specialized_Audit_Narrative_Nonfiction_Craft.md` | Nonfiction craft execution; reader contract; question management; information timing; scene pressure; meaning line; attribution discipline |
| Fantasy & Series Architecture | `Specialized_Audits/Specialized_Audit_Fantasy_Series_Architecture.md` | Fantasy-specific spines (Anti-Hero's Journey, Folkloric Mosaic, Liminal Drift, Fractured Chronicle, Ritual Pattern); series-level architecture (Expanding Quest, Character Web, Revolving Protagonist, Seasonal Arc, Mystery Box, Empire Cycle); series rhythm patterns (Convergent-Divergent, Event Spine, Mythic Undertow) |
| Plot Architecture | `Specialized_Audits/Specialized_Audit_Plot_Architecture.md` | Structural diagnosis; spine identification; pacing problems; stuck drafts. 48 spines across 12 families including rhythm/intensity engines (Wave/Pulse, Lullaby, Pressure Cooker), format/frame engines (Episodic, Clinical Case File, Nested Dolls, Talisman), and extended identity journeys (Heroine's Journey, Seven-Point) |
| Plot Selection & Coaching | `Specialized_Audits/Specialized_Audit_Plot_Selection_Coaching.md` | Upstream structure selection; pre-drafting guidance; stuck-draft triage; hybrid structure design; structural technique overlays (TV/Serial, Game-Inspired) |
| Queer Romance/Erotica | `Specialized_Audits/Specialized_Audit_Queer_Romance_Erotica.md` | Same-gender romance; bi/pan protagonists; trans characters; queer identity themes |
| Scene Turn Diagnostics | `Specialized_Audits/Specialized_Audit_Scene_Turn.md` | Scene-level mechanics; goal-conflict-outcome; scene-sequel chain; episodic structure; scene-level pacing |
| Series / Composite Novel | `Specialized_Audits/Specialized_Audit_Series_and_Composite_Novel.md` | Multi-part works; linked novellas; series with shared arc |
| Shelf Positioning | `Specialized_Audits/Specialized_Audit_Shelf_Positioning.md` | Category targeting; comp validation; discoverability; contract-to-market alignment |
| Short Fiction | `Specialized_Audits/Specialized_Audit_Short_Fiction.md` | Stories <20K words; flash fiction; compression economy; single-effect focus |

---

## Research Modes

Activate when current information beyond training data is needed. Research supplements analysis; it doesn't replace structural judgment.

| Mode | File | Use When |
|------|------|----------|
| Comp Validation | `Specialized_Audits/Research_Mode_Comp_Validation.md` | Verifying author comps are current, positioned correctly, query-ready |
| Factual Verification | `Specialized_Audits/Research_Mode_Factual_Verification.md` | Historical fiction, memoir, technical works; spot-checking real-world claims |
| Genre Currency | `Specialized_Audits/Research_Mode_Genre_Currency.md` | Rapidly evolving subgenres; verifying current market expectations |
| Representation Context | `Specialized_Audits/Research_Mode_Representation_Context.md` | Writing outside lived experience; sensitivity guidance; community discourse |

**Research Mode Principles:**
- Supplements structural judgment, doesn't replace it
- Cap at 3-5 queries per question
- Present uncertainty honestly when sources conflict
- Recommend sensitivity readers/experts when scope is exceeded

---

## Workflow Pathways

Pathways redirect the Editor's workflow when standard passes can't proceed.

| Pathway | File | Use When |
|---------|------|----------|
| Franklin Pathway | `Franklin_Pathway.md` | Editor's early passes detect absence of functional story spine; pre-narrative material (reporting pile, notes, premise); nonfiction that hasn't found narrative shape |

**Franklin Pathway** is the pre-spine viability gate. It activates when ≥2 trigger signals fire (Plot Architecture fit failure, causality failure, structural mapping failure, protagonist identification failure, or reader experience signals indicating no forward momentum). Produces a four-way classification: Story-Shaped (resume normal passes), Storyable Material (construct candidate spine, then resume), Argument With Embedded Narrative (reroute to argument architecture), or Not Storyable (redirect to non-narrative form).

---

## Evaluative Pass

| Pass | File | Use When |
|------|------|----------|
| Pass 11: Critical Quality & Market Viability | `Pass_11_Critical_Quality_Market_Viability_v2.md` | Author states publication/submission goal; requests honest assessment; preparing query materials |

**Pass 11** is the evaluative gate that runs after synthesis, before deliverables. It forces candid judgment on prose quality, market viability, and submission readiness.

**Sub-passes:**
- **11A** Writing Quality Diagnostic (always runs)
- **11B** Critical Verdict Protocol with Three Lenses (always runs)
- **11C** Market Reality Check (when marketability requested)
- **11D** First-50 Conversion Gate (when submission readiness requested)
- **11E** Revision Economics (when revision planning requested)
- **11F** Adversarial Reader Stress Test (optional, explicit author opt-in only)

**Outputs:** Verdict (READY / CONDITIONALLY VIABLE / NOT READY), Hard Truths, QF-* Quality Flags, Non-Negotiables, optional 11F Stress Test Summary + claim matrix

---

## The Primary/Secondary System

When a manuscript combines genres, establish clear precedence:

### Primary Module
The genre whose promise **must be satisfied** for the book to work. If this promise is broken, the book fails its contract.

- Primary module's expectations take precedence in conflicts
- Primary module's priority pass is the critical path
- Primary module's flags are evaluated strictly

### Secondary Module(s)
Genres whose conventions **must not be violated** but don't define the core promise.

- Secondary module expectations are "shoulds" not "musts"
- Secondary module flags are evaluated with more latitude
- Secondary module adds tracking and calibration but doesn't override primary

### Setting Precedence During Intake

Add to calibration:
```
PRIMARY GENRE: [the promise that must be satisfied]
SECONDARY GENRE(S): [constraints that must not be violated]
PRECEDENCE NOTES: [any specific priority decisions]
```

### The Conflict Resolver Rule

**When module expectations conflict, report as a contract tension and ask the author to prioritize.**

The AI does not resolve genre conflicts—it surfaces them. Example:

> "The literary module suggests that ambiguous ending is appropriate here, but the romance module flags that the HEA promise may be broken. Which takes precedence: literary ambiguity or romance resolution?"

**Never silently choose one module over another.** The author decides their priorities.

---

## Common Module Combinations

| Project Type | Primary | Secondary | Audits |
|--------------|---------|-----------|--------|
| Cozy mystery | Mystery | — | Comedy/Satire |
| Converted fanfic (fantasy) | SF/Fantasy | — | Fan Fiction Conversion |
| Converted fanfic (M/M romance) | Romance/Erotic | — | Fan Fiction Conversion, Queer Romance/Erotica |
| Converted fanfic (romance) | Romance/Erotic | — | Fan Fiction Conversion, Interiority Preservation |
| Dark comedy literary | Literary | — | Comedy/Satire, Banister |
| Dark romance | Romance/Erotic | — | Interiority Preservation, Consent Complexity |
| Epic fantasy | SF/Fantasy | — | — |
| Erotic horror | Horror (Psych) | Romance/Erotic | Consent Complexity |
| Erotic romance | Romance/Erotic | — | Interiority Preservation |
| F/F romance | Romance/Erotic | — | Queer Romance/Erotica, Interiority Preservation |
| Fantasy romance | Romance/Erotic | SF/Fantasy | Interiority Preservation |
| Historical mystery | Mystery | — | Historical Fiction |
| Historical romance | Romance/Erotic | — | Historical Fiction, Interiority Preservation |
| Literary erotic horror | Literary | Horror (Psych), Romance/Erotic | Interiority Preservation, Consent Complexity, Banister |
| Literary fiction (moral complexity) | Literary | — | Banister |
| Literary historical | Literary | — | Historical Fiction, Banister |
| Literary SF | Literary | SF/Fantasy | Banister |
| Literary thriller | Literary | Thriller | — |
| M/M romance | Romance/Erotic | — | Queer Romance/Erotica |
| M/M historical romance | Romance/Erotic | — | Queer Romance/Erotica, Historical Fiction |
| Mystery thriller | Thriller | Mystery | — |
| Political thriller | Thriller | — | Banister |
| Psychological horror | Horror (Psych) | — | — |
| Queer dark romance | Romance/Erotic | — | Queer Romance/Erotica, Consent Complexity |
| Queer fantasy romance | Romance/Erotic | SF/Fantasy | Queer Romance/Erotica |
| Queer romantic comedy | Romance/Erotic | — | Queer Romance/Erotica, Comedy/Satire |
| Regency romance | Romance/Erotic | — | Historical Fiction, Interiority Preservation |
| Romantic comedy | Romance/Erotic | — | Interiority Preservation, Comedy/Satire |
| Romantic mystery | Romance/Erotic | Mystery | Interiority Preservation |
| Romantic suspense | Romance/Erotic | Thriller | Interiority Preservation |
| Satirical SF | SF/Fantasy | Literary | Comedy/Satire, Banister |
| Science fiction thriller | Thriller | SF/Fantasy | — |
| Trans romance | Romance/Erotic | — | Queer Romance/Erotica, Interiority Preservation |
| Upmarket book club (voice-driven) | Literary | — | Comedy/Satire |
| Upmarket historical (voice-driven) | Literary | — | Historical Fiction, Comedy/Satire |
| Whodunit | Mystery | — | — |
| Witty historical (anachronistic) | Literary | — | Historical Fiction, Comedy/Satire |

---

## Priority Passes by Genre

Each genre has a "boss pass"—the analytical pass that matters most:

| Genre | Priority Pass | Why |
|-------|---------------|-----|
| Mystery | Pass 8 (Reveal Economy) | Information management IS the story |
| Thriller | Pass 3 (Rhythm) + Stakes Audit | Pacing IS the story |
| Romance | Pass 4 (Emotional) + Pass 5 (Character) | Emotional trajectory IS the story |
| Horror (Psych) | Pass 4 (Certainty axis) + Pass 1 (Dread) | Epistemic/emotional destabilization IS the story |
| SF/Fantasy | Pass 10 (Continuity) | World rule consistency IS the foundation |
| Literary | Pass 9 (Thematic) | Meaning IS the story |

When genres combine, the primary genre's priority pass takes precedence, but secondary genre passes are still run.

---

## Module Architecture

### How Modules Work

1. **Core framework runs always.** It contains philosophy, passes, synthesis, and deliverables.

2. **Genre modules modify passes.** They add:
   - Contract schema fields
   - Intake questions
   - Pass tracking requirements (additions, not replacements)
   - Genre-specific flags (problems unique to genre)
   - False positive warnings (what looks wrong but isn't)
   - Priority pass designation

3. **Specialized audits add targeted analysis.** They:
   - Run alongside or after relevant passes
   - Produce their own output sections
   - Stack with each other and with genre modules

### Loading Order

1. Read core framework
2. Complete standard intake questions
3. Based on intake, identify:
   - Primary genre module
   - Secondary genre module(s)
   - Relevant specialized audits
4. Load genre modules
5. Complete additional intake questions from modules
6. Load specialized audits
7. Run passes with module modifications active
8. Run specialized audits
9. Synthesize findings from all sources (surfacing any conflicts)
10. Deliver outputs

### Module Maintenance

- **Core framework** should remain stable; major changes are versioned
- **Genre modules** can be updated independently
- **Specialized audits** can be updated independently
- **New modules/audits** can be added without modifying core

---

## Quick Reference: When to Use What

### "I want to write a..."

| If you say... | Load... |
|---------------|---------|
| "psychological horror" | Horror (Psych) |
| "erotic thriller" | Thriller (primary) + Romance/Erotic (secondary) + Consent Complexity |
| "literary novel about grief" | Literary + (consider Banister if moral complexity) |
| "romance with mystery subplot" | Romance (primary) + Mystery (secondary) |
| "fantasy epic" | SF/Fantasy |
| "feminist erotic horror" | Horror (Psych) + Romance/Erotic + Interiority Preservation + Consent Complexity |
| "whodunit" | Mystery |
| "action thriller" | Thriller |
| "slow-burn romance" | Romance/Erotic + (consider Literary if prioritizing character depth) |
| "literary science fiction" | Literary (primary) + SF/Fantasy (secondary) |
| "dark romance with dubcon" | Romance/Erotic + Consent Complexity |
| "political novel" | Literary + Banister |
| "fantasy series" | SF/Fantasy + Fantasy & Series Architecture + Series/Composite Novel |
| "urban fantasy with case-of-the-week" | SF/Fantasy + Fantasy & Series Architecture (Seasonal Arc) |
| "new weird / literary fantasy" | Literary (primary) + SF/Fantasy (secondary) + Fantasy & Series Architecture (Liminal Drift) |
| "multi-POV epic fantasy" | SF/Fantasy + Fantasy & Series Architecture (Character Web) |
| "I'm stuck / my draft isn't working" | Plot Selection & Coaching (structural triage) + Plot Architecture (diagnosis) |
| "I haven't started yet but I'm planning" | Plot Selection & Coaching (pre-drafting plan) |
| "I want to combine multiple structures" | Plot Selection & Coaching (hybrid design) |

---

## File Organization

```
Development Editor/
├── AI_Development_Editor_Framework_v0.4.md   (core framework)
├── SKILL.md                                 (canonical operational spec)
├── Module_Index.md                          (this file)
├── Franklin_Pathway.md                      (pre-spine viability gate)
├── Pass_11_Critical_Quality_Market_Viability_v2.md  (evaluative pass)
│
├── Genre_Modules/
│   ├── Genre_Module_Romance_Erotic.md
│   ├── Genre_Module_Horror_Psychological.md
│   ├── Genre_Module_Thriller_Suspense.md
│   ├── Genre_Module_Mystery_Investigation.md
│   ├── Genre_Module_Science_Fiction_Fantasy.md
│   └── Genre_Module_Literary_Fiction.md
│
├── Specialized_Audits/
│   ├── Specialized_Audit_Banister.md
│   ├── Specialized_Audit_Character_Architecture.md
│   ├── Specialized_Audit_Comedy_Satire.md
│   ├── Specialized_Audit_Consent_Complexity.md
│   ├── Specialized_Audit_Dialectical_Clarity.md
│   ├── Specialized_Audit_Emotional_Craft.md
│   ├── Specialized_Audit_Fan_Fiction_Conversion.md
│   ├── Specialized_Audit_Fantasy_Series_Architecture.md
│   ├── Specialized_Audit_Female_Interiority.md
│   ├── Specialized_Audit_Historical_Fiction.md
│   ├── Specialized_Audit_Memoir_Creative_Nonfiction.md
│   ├── Specialized_Audit_Narrative_Nonfiction_Craft.md
│   ├── Specialized_Audit_Plot_Architecture.md
│   ├── Specialized_Audit_Plot_Selection_Coaching.md
│   ├── Specialized_Audit_Queer_Romance_Erotica.md
│   ├── Specialized_Audit_Scene_Turn.md
│   ├── Specialized_Audit_Series_and_Composite_Novel.md
│   ├── Specialized_Audit_Shelf_Positioning.md
│   ├── Specialized_Audit_Short_Fiction.md
│   ├── Research_Mode_Comp_Validation.md
│   ├── Research_Mode_Factual_Verification.md
│   ├── Research_Mode_Genre_Currency.md
│   └── Research_Mode_Representation_Context.md
│
├── Templates/
│   ├── Contract_Template.md
│   ├── Diagnostic_State_Template.md
│   ├── Reverse_Outline_Template.md
│   └── Genre_Module_TEMPLATE.md
│
└── Outputs/                                 (project-specific deliverables)
    ├── [Project]_Contract_[runlabel].md
    ├── [Project]_Pass0_Reverse_Outline_[runlabel].md
    ├── [Project]_Pass1_Reader_Experience_[runlabel].md
    ├── [Project]_Pass2_Structural_Mapping_[runlabel].md
    ├── [Project]_Pass5_Character_Audit_[runlabel].md
    ├── [Project]_Pass8_Reveal_Economy_[runlabel].md
    ├── [Project]_Core_DE_Synthesis_[runlabel].md
    └── Diagnostic_State.md                  (rolling state file)
```

`runlabel` should be date-based (`YYYY-MM-DD`) and may include agent tag (example: `codex53_2026-02-13`).

---

## Summary Statistics

**Total modules/audits/modes/passes/pathways:** 32
- 1 core framework
- 6 genre modules (Romance/Erotic, Horror, Thriller, Mystery, SF/Fantasy, Literary)
- 19 specialized audits (Banister, Character Architecture, Comedy/Satire, Consent Complexity, Dialectical Clarity, Emotional Craft, Fan Fiction Conversion, Fantasy & Series Architecture, Historical Fiction, Interiority Preservation, Memoir/Creative Nonfiction, Narrative Nonfiction Craft, Plot Architecture, Plot Selection & Coaching, Queer Romance/Erotica, Scene Turn Diagnostics, Series/Composite Novel, Shelf Positioning, Short Fiction)
- 4 research modes (Comp Validation, Factual Verification, Genre Currency, Representation Context)
- 1 evaluative pass (Pass 11: Critical Quality & Market Viability)
- 1 workflow pathway (Franklin Pathway: Pre-Spine Viability Gate)

**Coverage:**
- Most commercial fiction categories represented
- Literary fiction integration allows "literary + genre" combinations
- Specialized audits address cross-genre concerns
- Series/Composite Novel audit handles multi-part works
- Comedy/Satire audit enables voice-driven and witty fiction
- Historical Fiction audit covers period accuracy, research integration, anachronism handling
- Queer Romance/Erotica audit covers pronoun clarity, trope navigation, authenticity markers
- Fan Fiction Conversion audit handles worldbuilding gaps, character independence, echo management
- Shelf Positioning audit handles category targeting, comp validation, market alignment
- Memoir/Creative Nonfiction audit handles truth/memory tension, living person ethics, scene reconstruction; Gornick Layer handles situation-story separation, narrating intelligence, stance coherence, temporal distance, braid integrity, selection, and ending stance proof
- Short Fiction audit handles compression economy, single-effect focus, flash fiction constraints
- Research modes enable real-time verification and market currency checks
- Character Architecture includes Moral Argument Architecture (Part 9) for coupling character weakness to thematic argument
- Dialectical Clarity audit handles argument structure for Classification 3/4 material (claim ladder, support map, burden of proof, objection handling, narrative-as-evidence)
- Franklin Pathway includes Scene Selection Diagnostic and Narrative Stance Diagnostic for nonfiction
- Plot Architecture now covers 48 spines across 12 families (expanded from 39/9 in v0.4.4), including rhythm/intensity engines, format/frame engines, and extended identity journeys
- Plot Selection & Coaching provides upstream structural guidance: spine selection, hybrid design, stuck-draft triage, and structural technique overlays
- Fantasy & Series Architecture covers fantasy-specific structural forms (5 spines) and series-level architectural patterns (6 architectures + 3 rhythm patterns)

**Not yet developed:**
- Grimdark Fantasy — nihilism calibration, violence economy, hope management (note: Anti-Hero's Journey spine now available in Fantasy & Series Architecture audit)
- Horror (Supernatural) — distinct from psychological horror
- Military/War Fiction — tactical plausibility, combat pacing, trauma handling
- Young Adult — age-appropriate calibration, teen voice authenticity

These can be developed using the template as needed.

---

*Module Index v0.4.14.3 — Accompanies APODICTIC Development Editor (APDE) Framework v0.4.14.3*
*Last Updated: February 2026*
