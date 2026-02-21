---
description: Quick structural diagnostic on a specific concern
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

Run a targeted structural diagnostic on a specific concern without a full development edit.

Load the `core-editor` skill. This is a focused check, not a comprehensive analysis.

1. **Identify the concern.** If the author specifies one (e.g., "pacing in Act II," "character agency," "ending doesn't land"), focus there. If not specified, ask.

2. **Run only the relevant pass(es):** Map the concern to the appropriate pass or audit:
   - Pacing → Pass 1 (Reader Experience) + Pass 3 (Rhythm)
   - Structure → Pass 2 (Structural Mapping)
   - Character → Pass 5 (Character Audit) or Character Architecture audit
   - Reveals/twists → Pass 8 (Reveal Economy)
   - Emotional impact → Pass 4 (Emotional Value Tracking) or Emotional Craft audit
   - Plot structure → Plot Architecture audit (use plot-architecture skill)
   - Scenes → Scene Turn audit (use specialized-audits skill)
   - Market readiness → Pass 11 (use references/pass-11.md)

3. **Report findings** with specific scene/page references, confidence levels, and 1-3 actionable suggestions. Keep the output focused — this is a spot check, not an editorial letter.

If a manuscript file path is provided: @$1
