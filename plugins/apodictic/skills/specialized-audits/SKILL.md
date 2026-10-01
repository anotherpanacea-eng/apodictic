---
name: specialized-audits
description: >
  Discover APODICTIC's focused manuscript audits and research modes, list the
  available audits, or route an unclear audit request to its owning skill.
  Use for "list audits", "what audits are available", "help audits", or a
  focused-audit request whose family is not yet clear. Named tasks belong to
  narrative-craft-audits, genre-reader-audits, argument-audits,
  research-verification, or prose-measurements.
version: 2.13.3
---

# Focused Audit Catalog

This skill selects a focused workflow. Read the requested family's `SKILL.md`
and then only its selected protocol. For an unclear request, use the catalog
below to propose the relevant audit; ask only when manuscript context cannot
resolve the choice. Do not run unrelated audits because they appear here.

| Family | Entry point | Scope |
| --- | --- | --- |
| Narrative Craft | `../narrative-craft-audits/SKILL.md` | Focused manuscript audits of stakes, decisions, scene turns, character, emotion, interiority, literary craft, compression, and series structure. |
| Genre and Reader Expectations | `../genre-reader-audits/SKILL.md` | Genre and tag craft audits, shelf positioning, reception risk, reader-persona divergence, and descriptive content advisories. |
| Argument Analysis | `../argument-audits/SKILL.md` | Dialectical clarity, argument red team, persuasion, evidence provenance, adversarial evidence review, and assuring/guarding/discounting move analysis. |
| Research and Verification | `../research-verification/SKILL.md` | Requested internet research for citation verification, factual checking, field reconnaissance, comps, genre currency, and representation context. |
| Prose and Structural Measurements | `../prose-measurements/SKILL.md` | AI-prose calibration, narrative/argument decision signals, idiolect preservation, punctuation cadence, POV voice profiles, and experimental position-pair measurements. Optional SETEC execution is required for mechanical measurements. |

## Commands and shared contracts

`/audit <name>` keeps its existing aliases; `/research <mode>` routes directly
to research-verification. `/audit` without an argument lists the existing
catalog in `../../commands/audit.md`; `/research` lists its six modes in
`../../commands/research.md`. Plot spine work remains in
`../plot-architecture/SKILL.md`.

Load `../core-editor/references/focused-audit-contract.md` before execution.
The canonical activation rules and signal-emitting registry remain in
`../core-editor/references/audit-routing-table.md`; tier and severity rules
remain in `../core-editor/references/pass-dependencies.md`.

`catalog.json` is generated from the root release registry. It declares family
ownership and maps historical reference identifiers to their current files.
Applications use those aliases to preserve saved sessions and card identities;
they are path migrations, not duplicate protocols or permission boundaries.
