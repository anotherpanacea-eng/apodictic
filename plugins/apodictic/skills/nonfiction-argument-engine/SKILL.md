---
name: nonfiction-argument-engine
description: >
  Argument-shaped nonfiction development engine for op-ed, policy brief, testimony,
  academic argument, open letter, white paper, advocacy argument, legal brief,
  regulatory comment, and expert affidavit. Provides Dialectical Clarity audit,
  Argument Red Team, Argument Persuasion, Argument Evidence Deep-Dive, Adversarial
  Evidence Review, Field Reconnaissance, and Citation Verifier as companion audits.
  Also covers nonfiction argument coaching and nonfiction pre-draft argument spine work.
  Invoked when intake resolves constraint=nonfiction + persuasive-argument form.
version: 2.6.2
---

# Nonfiction Argument Engine

*A named, first-class skill within the APODICTIC Development Editor. The argument path
has always existed — this skill makes it explicit, discoverable, and bounded.*

---

## Canonical Source

This skill is the named orchestrator for argument-shaped nonfiction. It does not duplicate
the core-editor's spine; it specializes it for argument runs. The core-editor owns the
editorial framework; this skill owns the argument-specific routing, audit activation, and
state management.

**Upstream:** Invoked by `core-editor/SKILL.md §Delegation Rules — Nonfiction Argument Engine`
when intake resolves `constraint=nonfiction + persuasive-argument form`.

---

## The Firewall

*The no-content-invention firewall applies in argument mode exactly as in fiction mode.
Argument editing = diagnosing inferential structure, not authoring claims.*

<!-- Load `../core-editor/references/firewall.md` for the canonical Firewall definition.
     This skill references the same file; there is exactly one canonical source. -->

See `core-editor/references/firewall.md` for the full definition. In argument context:
the Firewall means the engine diagnoses warrant gaps, objection architecture, and claim
integrity — it does NOT author new claims, invent evidence, or fill in the argument for
the writer.

---

## Delegation Contract (core-editor → engine)

**Trigger:** intake router resolves `constraint=nonfiction` AND form is in the persuasive-
argument family per `core-editor/references/intake-router-runtime.md §6 Table A`:
  - op-ed, policy brief, testimony (oral/written), academic article, open letter
  - white paper, advocacy argument, legal brief, regulatory comment, expert affidavit
  - grant proposal, book review, recommendation memo

**NOT argument-shaped:** memoir, narrative nonfiction, creative nonfiction, personal essay
without a discernible persuasive claim ladder. Those route via their own §4a rows.

**Run-shape fields passed from core-editor:**
  - `form` — the specific argument form (op-ed, policy brief, etc.)
  - `audience_burden` — HIGH / MEDIUM / LOW per §Step 1 of Dialectical Clarity
  - `stakes` — moral / epistemic / practical / mixed
  - `high_stakes_flag` — boolean (triggers Hard Prerequisite tier for Field Recon)
  - `constraint` — `nonfiction` (always set on this delegation path)

**Artifact set returned to core-editor:** unchanged from the fiction path:
  - Editorial letter (Argument-DE class)
  - Findings Ledger (`apodictic.finding.v1` blocks with argument-cluster severities)
  - `Argument_State.md` (Pass-10-Class rolling artifact; schema per argument-state-schema)
  - Marked-up manuscript (Annotation Manifest + Annotated copy)

The synthesis spine is UNCHANGED: root causes → triage → adversarial self-check →
editorial letter → mechanical validation. The argument-specific path only adds the
argument-cluster audit activation and the Argument_State artifact.

---

## Scope Boundary

**Owned (argument-shaped nonfiction):**
- Dialectical Clarity (primary diagnostic audit)
- Argument Red Team (adversarial pressure testing)
- Argument Persuasion (audience-fit testing)
- Argument Evidence Deep-Dive (evidence-chain integrity)
- Adversarial Evidence Review (hostile-expert survivability)
- Field Reconnaissance (literature-counterevidence surfacing)
- Citation Verifier (citation provenance)
- Argument_State.md (rolling argument spine state)
- Nonfiction argument coaching (post-diagnosis revision guidance)
- Nonfiction pre-draft argument spine (idea-stage claim ladder seeding)

**Adjacent but NOT owned (flag, do not own):**
- Narrative nonfiction / reported features → route via `genre/narrative-nonfiction.md`
- Memoir / creative nonfiction → route via `genre/memoir-creative-nonfiction.md`
- Fiction with argument themes (philosophical fiction, didactic fiction) → core-editor
  handles via Pass 9 + Dialectical Clarity; this engine does NOT activate on fiction

---

## Owned References

This skill loads the following reference files:

| Reference | Role |
|-----------|------|
| `core-editor/references/firewall.md` | Canonical Firewall definition (single source) |
| `core-editor/references/argument-audits-routing.md` | Argument-cluster audit routing rows (§4a/§4b fragment) |
| `core-editor/references/argument-audits-propagation.md` | Argument-cluster §4e signal-propagation rows (fragment) |
| `core-editor/references/nonfiction-intake-routing.md` | Nonfiction triage routing fragment (§6 Table A + triage logic) |
| `core-editor/references/synthesis-argument.md` | Argument-DE decision-layer schema (§8 Argument-DE class fragment) |
| `core-editor/references/intake-router-runtime.md` | Full intake routing (for §6 Table A / form identification) |
| `core-editor/references/pass-dependencies.md` | Pass resolver + audit tier definitions + §4e table |
| `core-editor/references/run-synthesis.md` | Synthesis spine (shared with fiction path) |

---

## Argument Engine Workflow

### 1. Argument Intake

Load `core-editor/references/intake-router-runtime.md §6`. Run nonfiction triage per
the fragment `core-editor/references/nonfiction-intake-routing.md`:

- Identify form, audience, stakes, constraint=high-stakes
- Seed `Argument_State.md` with the initial `apodictic:argument_spine` block
- Identify the Hard Prerequisite tier requirement (high-stakes signal → Field Recon first)

### 2. Audit Activation (Pre-Pass)

Load `core-editor/references/argument-audits-routing.md` to resolve which argument-cluster
audits activate at which tier per the run-shape:

- Hard Prerequisite tier (high-stakes): Field Reconnaissance MUST complete before passes
- Pre-DE Prerequisite tier (high-stakes): Citation Verifier runs before the DE begins
- Auto-recommend before synthesis: Dialectical Clarity (always for argument-shaped runs)
- Additional audits per §4a/§4b trigger logic in the routing fragment

### 3. Pass Execution (Shared Spine)

The argument engine uses the SAME pass set as the fiction path (Passes 0, 1, 2, 5, 8
for the baseline floor; full pass set for expanded runs). Argument-specific passes are
handled by the audit cluster, not by new passes. The Findings Ledger structure is unchanged.

### 4. Synthesis (Argument-DE Class)

Load `core-editor/references/synthesis-argument.md` for the Argument-DE decision-layer
schema. The synthesis spine is unchanged; only the decision-layer section names differ
(Protected Elements → Strengths / Protected Elements; Author Decisions → Editorial-Dispute
Territory). See `core-editor/references/run-synthesis.md §Step 8 Argument-DE class` for
the full schema.

Signal propagation for argument-cluster audits follows `core-editor/references/argument-audits-propagation.md`
(the §4e fragment for the argument cluster).

### 5. Argument_State.md Update

After synthesis, update `Argument_State.md` at the project root per the schema in
`core-editor/references/run-synthesis.md §Argument_State`. This is the argument path's
Pass-10-Class rolling artifact — it persists across runs and is diffed on re-runs.

---

## QA Guardrails

All core-editor QA guardrails apply (see `core-editor/SKILL.md §QA Guardrails`). Argument-specific additions:

1. **Warrant verification before severity assignment.** Every WR-class flag must name the specific
   inferential gap — "the audience must supply X" — not a generic "needs more evidence."
2. **Burden calibration.** Audience burden (HIGH/MEDIUM/LOW per §Step 1 of Dialectical Clarity)
   governs severity floors for WR0 and related flags. Verify burden level before assigning Must-Fix.
3. **Hard Prerequisite compliance.** On high-stakes runs, Field Reconnaissance MUST complete
   before any Tier 2 evaluative pass. A declined Hard Prerequisite cannot proceed silently.
4. **Firewall in argument context.** The engine diagnoses inferential structure; it does NOT author
   claims, invent evidence, or complete the argument. See `core-editor/references/firewall.md`.

---

*The nonfiction argument path has always been part of APODICTIC. This skill makes it named,
explicit, and bounded — so it can be selected, tested, and extended without touching the fiction path.*
