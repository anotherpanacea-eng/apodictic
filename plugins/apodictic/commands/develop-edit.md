---
description: Run a full development edit on a manuscript
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

Run a full development edit using the APODICTIC Development Editor framework.

Load the `core-editor` skill, then load `references/run-core.md` for execution details. Follow the complete workflow:

1. **Intake:** Read the manuscript. Generate a DRAFT Contract Schema by inferring genre, reader promise, controlling idea, and structural features from the text alone. Present the draft to the author and ask hypothesis-driven questions to validate or correct inferences. Misalignments between the inferred contract and author intent are diagnostically valuable — they reveal where the text doesn't communicate what the author intended.

2. **Contract:** Finalize `Contract_and_Controlling_Idea.md` with schema, controlling idea, anti-idea, selected genre modules, and non-negotiables. Load the appropriate genre module(s) from `references/genre-*.md`.

3. **Core Passes:** Run Pass 0 (Reverse Outline), Pass 1 (Reader Experience), Pass 2 (Structural Mapping), Pass 5 (Character Audit), and Pass 8 (Reveal Economy). Use measured word counts (`wc -w`), not estimates. Load `references/output-policy.md` for pass-level output protocol.

4. **Audit Integration:** After core passes, review accumulated finding-driven audit triggers. Recommend universal audits (Stakes System, Decision Pressure, Scene Turn) and any contract- or finding-driven audits. Run activated audits before synthesis. See `run-core.md` §Audit Integration Point. Log all recommended, accepted, run, and skipped audits with reasons in an Audit Invocation Log artifact.

5. **Synthesis:** Integrate audit findings with pass findings. Identify 3-5 root causes, triage into Must-Fix / Should-Fix / Could-Fix, generate revision checklist (max 10 items), revision order, and top 10 reader questions. Verify every flag against stated intent before finalizing.

6. **Evaluate Full DE trigger:** If >5 root causes, >10 major reader experience issues, or structural complexity is high, offer to run Full DE passes (3, 4, 6, 7, 9, 10) and additional supplementary audits. Load `references/run-full.md` only when this trigger is met.

7. **Output:** Write all artifacts to the project's `Outputs/` folder using the naming convention `[Project]_[PassName]_[runlabel].md`.

If a manuscript file path is provided: @$1
