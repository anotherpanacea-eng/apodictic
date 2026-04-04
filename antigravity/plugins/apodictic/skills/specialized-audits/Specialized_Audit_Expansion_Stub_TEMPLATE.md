# Specialized Audit Expansion Stub Template
## APDE / APODICTIC
*Use this template when creating any new specialized audit.*

---

## What This Template Is

This is a reusable scaffold for designing a new specialized audit that can be integrated into APDE.

It is built for:

1. rigorous level-setting research,
2. diagnostically useful audit design,
3. reproducible severity calibration,
4. plugin-ready packaging.

It is not the audit itself.
It is the design and drafting protocol.

---

## How To Use This Template

### Workflow

1. Copy this file and rename it:
   - `[audit-slug]-expansion-stub.md`
2. Fill metadata and scope fields first.
3. Complete **Phase 1 (Level-Setting Research)**.
4. Complete **Phase 2 (Structural Spec)**.
5. Produce two deliverables:
   - `[audit-slug]-level-setting.md`
   - `[audit-slug].md`

### Annotation tags

Use these tags exactly:

1. `[FILL]` = write from scratch
2. `[REVISE]` = starter text exists; revise it
3. `[KEEP]` = required structural element

### Collaboration mode compatibility

Works for:

1. single-model drafting,
2. multi-model head-to-head drafting,
3. synthesis merge drafting.

If running multi-model:

1. require same stub input for all models,
2. compare against identical deliverable requirements,
3. synthesize only after all outputs exist.

---

## Metadata (Fill First)

`[FILL]`

```markdown
AUDIT NAME: [e.g., Force Architecture]
AUDIT SLUG: [kebab-case]
AUDIT TYPE: [craft | genre | tag | workflow]
PRIMARY DOMAIN: [what this audit uniquely diagnoses]
SCOPE CLASS: [cross-genre | genre-specific | cross-genre modifier]
RELATED MODULES: [genre modules and existing audits this interacts with]
ACTIVATION TRIGGERS: [user-request / symptom patterns]
TARGET DEPTH: [line range for v1; e.g., 400-650]
STATUS: [draft]
AUTHORING MODE: [single-model / multi-model / synthesis]
```

---

## Scope and Positioning

### What already exists

`[FILL]`

List current framework coverage that touches this area.
Do not understate overlap.

### What is missing

`[FILL]`

State the unique gap this audit fills in one sentence.

Pattern:

> "Existing systems diagnose X and Y. This audit diagnoses Z."

### Core failure claim

`[REVISE]` Starter:

> The key failure is not absence of content.  
> The key failure is **detached delivery**: the manuscript signals the right domain elements without converting them into narrative consequence.

### Non-duplication boundary

`[KEEP]`

Must explicitly define:

1. what this audit does that core passes do not,
2. what this audit does that related specialized audits do not,
3. where it should be run in sequence.

### Depth target

`[REVISE]` Starter:

1. enough detail for inter-editor agreement,
2. not so broad it duplicates half the framework,
3. include named flags,
artifacts,
distinguish protocol,
mode calibration,
hard gates.

---

## Phase 1: Level-Setting Research

Complete all five research questions before writing the audit.

Output file:
`[audit-slug]-level-setting.md`

The audit draft should not read like scholarship,
but the research should be visible in flag specificity and thresholds.

### Research Question 1: Theoretical Grounding

`[FILL]`

What models explain why this domain works when it works?

Deliverable:

1. 3-6 conceptual frames,
2. operationalized into testable diagnostics.

### Research Question 2: Failure Taxonomy

`[FILL]`

What repeat failure patterns appear in this domain?

Deliverable:

1. failure inventory with mechanisms,
2. one structural-isomorphism anchor line.

### Research Question 3: Positive Integration Cases

`[FILL]`

What good execution looks like across modes/subtypes.

Deliverable:

1. exemplar list,
2. extracted techniques,
3. cross-case success signals.

### Research Question 4: Calibration by Mode

`[FILL]`

How do burdens shift by mode/subgenre/context?

Deliverable per mode:

1. promise,
2. common blind spot,
3. false-positive risk.

### Research Question 5: Distinguish Problem

`[FILL]`

How to distinguish intentional style choice from execution failure.

Deliverable:

1. decision tests,
2. 3-way classification outcomes.

### Research source discipline

`[KEEP]`

1. Prefer primary and durable sources.
2. Use contemporary craft references where needed.
3. Separate stable principles from trend-specific observations.
4. Mark uncertain claims explicitly.

---

## Phase 2: Structural Spec

Use the sections below as the skeleton for `[audit-slug].md`.

### §1. Purpose

`[REVISE]` Starter:

Define this audit as a mechanism-level diagnostic.
State core problem, fundamental question, activation, required inputs, outputs.

`[KEEP]`

Must include explicit non-duplication with core passes and related audits.

---

### §2. Delivery Framework

`[FILL]`

Build the conceptual engine.

Requirements:

1. 5-7 channels/dimensions,
2. channel definitions with detection criteria,
3. channel ratings:
   - Integrated
   - Partial
   - Detached

`[KEEP]`

Each channel must be observable in manuscript evidence,
not theoretical mood.

---

### §3. Named Diagnostic Flags

`[FILL]`

Target 12-22 flags.

Each flag must include:

1. code,
2. memorable name,
3. one-line definition,
4. detection criteria,
5. default severity.

`[REVISE]` Starter severity model:

1. `Could-Fix` (local),
2. `Should-Fix` (pattern),
3. `Must-Fix` (systemic/contract-critical).

`[KEEP]`

Flag language must be portable to editorial reports.

---

### §4. Tracking Artifacts

`[FILL]`

Design 2-4 artifacts that make patterns visible.

Artifact requirements:

1. fillable by an editor while reading,
2. pattern-revealing,
not checklist-only,
3. supports severity calls.

`[KEEP]`

At least one artifact must track persistence over time.

---

### §5. Distinguish Framework

`[FILL]`

Separate:

1. intentional and successful,
2. intentional but unstable,
3. accidental failure.

Include:

1. named decision tests,
2. matrix mapping outcomes to actions.

`[KEEP]`

No "intentionality as exemption" rule.
Intentional can still fail.

---

### §6. Mode Calibration Matrix

`[REVISE]` Starter structure:

| Mode | Integration Promise | Named Failure Mode | Tighten On | Loosen On |
|---|---|---|---|---|
| [Mode A] | [FILL] | [FILL] | [FILL] | [FILL] |
| [Mode B] | [FILL] | [FILL] | [FILL] | [FILL] |
| [Mode C] | [FILL] | [FILL] | [FILL] | [FILL] |

`[KEEP]`

1. Each mode needs a vivid named failure mode.
2. Tighten/Loosen columns are mandatory to control false positives.

---

### §7. Severity Hard Gates

`[FILL]`

Define minimum severity floors for non-negotiable failures.

Starter pattern:

1. climax-critical legibility/coherence failure -> `Must-Fix`,
2. systemic persistence failure -> `Must-Fix`,
3. repeated conversion failure -> minimum `Should-Fix`.

`[KEEP]`

Hard gates override soft tone or preference-based hedging.

---

### §8. Interaction Patterns

`[FILL]`

List high-value channel interactions where diagnosis becomes more accurate.

Minimum:

1. 5 interaction patterns,
2. each tied to likely revision order implications.

---

### §9. Audit Procedure

`[REVISE]` Starter:

1. lock claim/scope/mode,
2. build artifacts,
3. rate channels,
4. apply flags and hard gates,
5. run distinguish matrix,
6. synthesize priorities.

`[KEEP]`

Procedure must be executable by another editor without hidden assumptions.

---

### §10. Output Template

`[KEEP]`

Audit output must include:

1. contract/mode lock,
2. channel ratings,
3. artifact summaries,
4. flag inventory (severity,
frequency,
blast radius,
evidence),
5. pattern analysis,
6. distinguish classification,
7. calibration notes,
8. hard-gate triggers,
9. readiness impact note.

`[FILL]`

Provide a copy-paste markdown output template.

---

### §11. Integration and Handoff

`[REVISE]` Starter:

Define:

1. recommended pairings with existing audits/modules,
2. where this audit sits in sequence,
3. required Pass 11 handoff fields.

`[KEEP]`

Must include "top 3 failures affecting readiness" format.

---

### §12. What This Audit Is Not

`[FILL]`

List explicit non-goals and anti-misread boundaries.

Minimum:

1. not content policing,
2. not replacement for adjacent audits,
3. not generic prose advice disguised as domain diagnostics.

---

### §13. Firewall Compliance

`[KEEP]`

The audit is diagnostic.

Allowed:

1. identify structural failures,
2. assign severity and blast radius,
3. specify revision scope.

Forbidden:

1. rewrite scenes,
2. generate replacement prose,
3. invent plot events as "fixes."

---

## Generic Flag Coding Pattern (Optional)

`[REVISE]`

Pick a short code family aligned to channels.

Example:

1. channel prefixes (`LG`,
`CP`,
etc.),
2. numbered flags (`LG-1`,
`LG-2`...).

Rules:

1. avoid overlapping meanings across codes,
2. one code = one failure mechanism.

---

## Anti-Sycophancy Controls (Recommended)

`[KEEP]`

Apply these in audit drafting and execution:

1. Negative-case-first ordering:
   - summarize strongest failure case before strengths.
2. Evidence burden:
   - no major claim without textual anchors.
3. Hard-gate dominance:
   - triggered hard gates limit verdict ceilings.
4. Candor requirement:
   - avoid euphemistic softening when severity is systemic.

---

## Deliverables Checklist

`[KEEP]`

Required:

1. `[audit-slug]-expansion-stub.md`
2. `[audit-slug]-level-setting.md`
3. `[audit-slug].md`

Recommended:

1. `[audit-slug]-synthesized.md` (if multi-model process used)
2. short changelog note entry

---

## Plugin Packaging Checklist

Use this to make the audit shippable in plugin builds.

### A) File placement

`[FILL]`

Choose destination family:

1. `specialized-audits/references/craft/`
2. `specialized-audits/references/genre/`
3. `specialized-audits/references/tag/`
4. `specialized-audits/references/workflow/` (if created)

Include:

1. audit file (`[audit-slug].md`)
2. optional level-setting file (`[audit-slug]-level-setting.md`)

### B) Registry/index updates

`[FILL]`

Update project index surfaces that list audits.

Minimum:

1. module index table entry,
2. any command help/intake router references,
3. publication requirements inventory (if maintained).

### C) Invocation guidance

`[FILL]`

Add activation triggers and pairings so users know when to run it.

### D) Validation pass

`[KEEP]`

Before shipping:

1. run one manuscript through the new audit,
2. check flag reproducibility on second read/sample,
3. verify no contradiction with existing audits,
4. verify output template is complete and concise.

---

## Quality Gate Rubric (Score Before Finalizing)

Rate each 0-2.
Target: 10+ / 12 minimum.

1. **Distinctiveness**
   - Clearly non-duplicative value.
2. **Diagnosability**
   - Flags are testable and reproducible.
3. **Actionability**
   - Findings imply revision scope without ghostwriting.
4. **Calibration**
   - Mode-aware thresholds and false-positive controls.
5. **Severity Discipline**
   - Hard gates and escalation logic are explicit.
6. **Integration Fit**
   - Cleanly composes with APDE workflow.

If score <10:

1. revise failure taxonomy,
2. tighten artifacts,
3. sharpen non-duplication boundary.

---

## Quick-Start Copy Block

Use this to begin a new stub quickly.

```markdown
# [AUDIT NAME] — Expansion Stub
## Collaboration Protocol
*Created: [Month Year]*

This is a two-phase build:
1) Level-setting research
2) Structural audit spec

Deliverables:
1) [audit-slug]-level-setting.md
2) [audit-slug].md

Tags used:
- [FILL]
- [REVISE]
- [KEEP]
```

---

## Notes

This template is intentionally strict.

The goal is to prevent:

1. vague audits that collapse into generic craft advice,
2. overlap-heavy audits that duplicate existing passes,
3. soft audits that avoid hard severity calls.
