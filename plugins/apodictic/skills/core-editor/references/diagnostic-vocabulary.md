# Diagnostic Vocabulary Mode (operator mode)

**Status:** v1 (Increment 1)
**Trigger:** `operator:facilitator` from the intake router (Question 3 option F — "I'm facilitating a writing group"), or any Core DE command carrying `operator:facilitator`.
**Adds:** a `[Project]_Vocabulary_Guide_[runlabel].md` deliverable.
**Does not change:** which passes run, what is diagnosed, or how severe a finding is. The author-facing editorial letter is still produced, unchanged.

---

## Purpose

The reader is a **writing-group facilitator** helping a peer group — often writers still learning to name structure — see and discuss the manuscript's architecture for themselves. They want a **teaching aid**, not an edit letter: the structural vocabulary the diagnosis used, defined plainly and grounded in *this* manuscript, plus questions to seed discussion.

**What this is:** a Vocabulary Guide — a glossary + discussion prompts the facilitator hands the group.

**What this is not:** a replacement for the editorial letter, and not a softer diagnosis. The honest severity record lives in the letter; the Guide teaches the group to *see* the structure behind it.

---

## The Vocabulary Guide

Produce `[Project]_Vocabulary_Guide_[runlabel].md` alongside the normal editorial letter. Two required sections:

1. **Glossary.** For each structural concept the diagnosis leaned on (controlling idea, reverse outline, reveal economy, causal gap, character agency, pacing, POV discipline, dramatic irony, …), one entry:
   - format `- **Term** — plain-language definition …`,
   - **grounded**: name one concrete place in *this* manuscript where the concept is visible (working or not), with a reference (`Ch. 9`, `lines 142-160`, `§Reader Knowledge`). Grounding is the teaching value — "here is what *reveal economy* means, and here is where your book spends it." Aim to ground every entry; the gate requires at least three.

2. **Discussion Prompts.** Open questions tied to the glossary concepts, for the group to discuss. Phrase them as **questions** ("Where does the controlling idea first come into focus, and where does it blur?"), never as directives. The facilitator runs a discussion, not a verdict.

Worked example: `references/example-vocabulary-guide.md`.

---

## What is preserved (non-negotiable)

- **The Firewall** (`core-editor/SKILL.md §The Firewall`) — the Guide teaches concepts and asks questions; it never invents plot, characters, imagery, or prose.
- **Severity honesty is not laundered.** The Guide is a teaching companion, not a replacement for the editorial letter. The author-facing letter keeps the full Canonical Severity Scale and the Deficit Lock. The "frame issues as questions" rule applies to the *group-discussion surface* (the Guide), so it can't soften a Must-Fix into a gentle "something to think about."
- **No author-directed prescription.** A facilitator teaches vocabulary and poses questions; the group and author draw their own conclusions. No "rewrite the climax" / "add a scene where…" in the Guide.

---

## Mechanical check

`scripts/validate.sh diagnostic-vocabulary <vocab_guide>` enforces the contract when the artifact declares `<!-- mode: diagnostic-vocabulary -->`. Because the Vocabulary Guide is a distinct named artifact, a file identifiable as one (by `*_Vocabulary_Guide_*.md` name or a `# … Vocabulary Guide` title) that is **missing** the marker is a **V0 ERROR** — only genuinely unrelated files stay a no-op pass. All checks are body-scoped (before any Appendix A heading):

- **V1** non-empty Glossary, ≥3 entries; **V2** every entry is `term — definition` shaped; **V3** ≥3 entries grounded in the manuscript (override `<!-- override: vocabulary-grounding — … -->`); **V4** a Discussion Prompts section, ≥3 prompts, all phrased as questions.
- **W1** (advisory; ERROR under `--strict`) author-directed prescription in the body — modal ("you should rewrite") or a bare line-start imperative ("Add a scene…", "Cut the prologue"); override `<!-- override: vocabulary-prescription — … -->`.

Sibling operator mode: [Editor Scaffolding](editor-scaffolding.md) (`operator:editor`). Design + ownership boundary + the rule-of-three extraction note: [`docs/diagnostic-vocabulary.md`](../../../docs/diagnostic-vocabulary.md).
