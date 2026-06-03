# Diagnostic Vocabulary Mode — a teaching aid for writing-group facilitators

**Status:** Increment 1 **built**. Roadmap: `ROADMAP.md` → Operators → Diagnostic Vocabulary Mode. Implementation: `plugins/apodictic/skills/core-editor/references/diagnostic-vocabulary.md` (mode contract), `run-synthesis.md §Operator Mode: Diagnostic Vocabulary` (synthesis hook), the intake-router `operator:facilitator` flip (gap → built), `scripts/diagnostic_vocabulary.py`, `validate.sh diagnostic-vocabulary` (+ canonical `--check-all` gate), and the worked example `references/example-vocabulary-guide.md`.

A **writing-group facilitator** is running APODICTIC not to hand the author a fix but to help a *peer group* — often writers still learning to name structure — see and discuss the manuscript's architecture for themselves. What they want is a **teaching aid**: the structural vocabulary the diagnosis used, defined in plain language and grounded in *this* manuscript, plus discussion prompts that turn findings into questions the group can work through together.

This is an **operator mode**, the sibling of [Editor Scaffolding](editor-scaffolding.md) (`operator:editor`). It is reached by the `/start` router (`operator:facilitator`, Question 3 option F) or by any Core DE command carrying the flag. It adds a **Vocabulary Guide** deliverable; it does **not** change which passes run or how severe a finding is.

## The deliverable — a Vocabulary Guide

In facilitator mode the run produces `[Project]_Vocabulary_Guide_[runlabel].md` (alongside the normal editorial letter), a cheat sheet the facilitator hands the group. Two required sections:

1. **Glossary.** Each structural concept the diagnosis leaned on (controlling idea, reverse outline, reveal economy, causal gap, character agency, pacing, POV discipline, …) gets a plain-language definition **and a "where it shows up here" anchor** — one concrete place in *this* manuscript where the concept is visible (working or not), with a reference. The grounding is the teaching value: not an abstract dictionary, but "here is what *reveal economy* means, and here is where your book spends it."

2. **Discussion Prompts.** Open questions tied to the glossary concepts, for the group to discuss ("Where does the controlling idea first come into focus, and where does it blur?"). Framed as **questions, not directives** — the facilitator runs a discussion, not a verdict.

## What is preserved (non-negotiable)

- **The Firewall** (`core-editor/SKILL.md §The Firewall`). The Guide teaches concepts and asks questions; it never invents plot, characters, imagery, or prose.
- **Severity honesty is not laundered.** The Vocabulary Guide is a teaching companion, *not* a replacement for the editorial letter. The author-facing letter — with the full Canonical Severity Scale and the Deficit Lock — is still produced and unchanged. The "frame issues as questions" rule applies to the *group-discussion surface* (the Guide), so it cannot become a way to soften a Must-Fix into a gentle "something to think about." The honest record lives in the letter; the Guide teaches the group to see the structure behind it.
- **Prescription stays out.** Like Editor Scaffolding's prescription deferral, the Guide does not issue author-directed imperatives ("rewrite the climax", "add a scene") — a facilitator teaches vocabulary and poses questions; the group and author draw their own conclusions.

## The `diagnostic-vocabulary` validator (Increment 1)

`validate.sh diagnostic-vocabulary <vocab_guide|run_folder> [--strict]` (resolves the newest `*_Vocabulary_Guide_*.md` in a run folder). Delegates to `scripts/diagnostic_vocabulary.py`; degrades to an advisory `WARN` without `python3`.

**Conditional enforcement** (the editor-scaffolding pattern): the contract is enforced only when the artifact declares `<!-- mode: diagnostic-vocabulary -->`; without it the validator reports "not in diagnostic-vocabulary mode" and exits `0`, so it is safe to run over any file. All section checks are **body-scoped** (everything before a first `Appendix A` heading, if any), so an appendix can't satisfy a required section.

| ID | Severity | Rule |
|---|---|---|
| **V1 — mode + Glossary** | ERROR | The mode marker is present **and** a non-empty **Glossary** section exists in the body with **≥3 entries** (a real glossary, not a token). |
| **V2 — entries are defined** | ERROR | Every Glossary entry is `term — definition` shaped (a bolded/headed term followed by explanatory text), not a bare term with no definition. |
| **V3 — glossary is grounded** | ERROR | **≥3** Glossary entries carry a manuscript anchor (a chapter/scene/line/§ reference) — the teaching value is grounding the term in *this* text. Override: `<!-- override: vocabulary-grounding — <rationale> -->` for a deliberately conceptual glossary. |
| **V4 — prompts are questions** | ERROR | A non-empty **Discussion Prompts** section with **≥3** prompts, **all** phrased as questions (end with `?`). The "frame issues as questions" contract, made mechanical. |
| **W1 — prescription leak** | WARN (ERROR under `--strict`) | An author-directed prescriptive imperative in the body — modal ("you should rewrite") or a bare line-start imperative ("Add a scene…", "Cut the prologue"). Facilitators teach and prompt; they don't prescribe. Override: `<!-- override: vocabulary-prescription — <rationale> -->`. |

**Report.** A mode banner + one line per check. Exit `0` clean / WARN-only / not-in-mode, `1` on any ERROR (or WARN under `--strict`), `2` usage.

**Ownership boundary.** `diagnostic-vocabulary` owns the **facilitator teaching-aid contract** — glossary presence/definition/grounding, question-framing, and prescription suppression — classes no other validator raises. It does **not** carry or check severity (the editorial letter and its gates own that), and it is a standalone artifact, not a letter overlay, so it does not compose with or duplicate the letter-family gates.

## Canonical `--check-all` gate

`references/example-vocabulary-guide.md` is a contract-conformant worked example. `validate.sh --check-all` runs `diagnostic-vocabulary` against it — proving the canonical framework's own example satisfies the validator (the "canonical-framework validator runs as release gate" discipline).

## Relationship to Editor Scaffolding (and a rule-of-three note)

Diagnostic Vocabulary and [Editor Scaffolding](editor-scaffolding.md) are the two `operator:*` presentation modes, and they share a validator *shape*: a mode marker, conditional enforcement, body-scoped section checks, the shared `<!-- override: … -->` convention, and the same modal-plus-bare prescription detection. They are kept as **two self-contained validators** (matching the codebase's standalone-validator convention — `escalation_check`, `feedback_triage`, `editor_scaffolding` are each self-contained). They differ where it matters: Editor Scaffolding reframes the *editorial letter* for one professional editor (blind-spot surfacing); Diagnostic Vocabulary produces a *separate teaching artifact* for a peer group (glossary + question prompts). If a **third** operator mode lands (Multi-Party Intake, `operator:team`), the shared prose helpers (`_body`, `has_override`, prescription detection, `_section_nonempty`) should be extracted into one `operator_modes.py` module then — the rule-of-three threshold — and the existing two refactored onto it.

## Increment boundaries

**Increment 1 (this):** the Vocabulary Guide contract, the synthesis hook, the router flip, the validator (V1–V4 + W1), the worked example, and the `--check-all` gate.

**Future increments (not built):**
- **Concept selection from the ledger** — auto-derive the glossary's concept set from the Findings Ledger's actually-used mechanisms, rather than the model choosing them.
- **Difficulty tiering** — beginner / intermediate glossary depth for groups at different experience levels.
- **Prompt ↔ finding traceability** — link each discussion prompt to the finding ID it exercises, so a facilitator can see which structural issue each question opens onto.
- The sibling operator **Multi-Party Intake** (`operator:team`) remains a separate ROADMAP gap.
