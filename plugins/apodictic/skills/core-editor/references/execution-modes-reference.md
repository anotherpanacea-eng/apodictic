# Execution Modes — Reference

*Reference file for the APODICTIC Development Editor. Loaded at dispatch time (run start), not during pass diagnosis. Holds pre-flight and context-window detection detail extracted from `run-core.md` §Execution Mode. The mode-selection algorithm, quality-risk triggers, dispatch protocol, pre-pass re-grounding, and mechanical validation remain in `run-core.md`.*

---

### Pre-flight Diagnostics (Required)

Before selecting an execution mode, the parent orchestrator runs a pre-flight metadata scan. Pre-flight is a bash script — not a model call — that gathers manuscript measurements needed for informed dispatch decisions.

**What it does:** Runs `scripts/preflight.sh` on the manuscript file. Produces a metadata packet containing: total lines, estimated word count, section/chapter boundaries, POV and tense detection (pronoun-frequency heuristic on three 200-line samples), dialogue ratio, mean paragraph length, estimated token load, and dispatch recommendations.

**What it computes:**
- **Estimated token load:** Approximate manuscript tokens (word count × 4/3) plus analytical overhead (~75K for pass specs, contract, ledger growth, and synthesis). Used by the parent orchestrator to determine whether single-agent mode is viable.
- **Per-mode token cost estimate:** A `## Per-Mode Token Cost Estimate` section with a figure per mode (single-agent overhead-loaded · sequential ×3 · hybrid ×4 · swarm ×7 of the bare manuscript-token estimate), calibrated to `run-core.md` §Token Cost. These are order-of-magnitude budget signals, **not ratio-comparable** (the single-agent figure carries the +75K overhead while the ×3/×4/×7 figures are overhead-stripped), and preflight prints no "cheapest viable mode" verdict — the orchestrator picks that at dispatch. The `run-core.md` §Cost-Floor Override (Budget Cap) path reads these numbers to let a budget-constrained user cap below the token-fit floor.
- **Execution mode recommendations:** Two tiers based on context window size. For large-context models (≥1M tokens): single-agent if estimated load < 600K tokens, sequential otherwise. For standard-context models (<1M tokens): <60K words → sequential; 60–100K → hybrid; >100K → swarm. The parent orchestrator selects the appropriate tier based on its own context window. **These are token-fit recommendations only — they establish the floor. Manuscript and contract characteristics may upgrade the recommendation per §Quality-Risk Mode Selection below.**
- **Triage subagent `max_turns`:** `ceil(total_lines / 500) + 20`. This ensures enough turns for full-manuscript I/O (at 500 lines per read chunk) plus output file generation, with a 20-turn buffer for reasoning, complex structural decisions, and focus map targeting.
- **Conversion artifacts flag:** If the section boundary count is low relative to word count (e.g., 4 breaks in 84K words), the metadata packet notes that chapter structure may have been lost in file conversion. The triage subagent should identify scene boundaries from narrative content rather than relying on headers.

**What it does NOT do:** No scene identification, no structural function tagging, no reader experience tracking, no focus map targeting, no diagnostic flags of any kind, no genre identification. Pre-flight is a tape measure, not a stethoscope.

**Cost:** Zero model tokens. Sub-second execution time. The bash script runs locally.

**How it integrates:** The parent orchestrator runs pre-flight immediately after loading the manuscript path. It reads the metadata packet, determines its own context window size, selects the execution mode from the appropriate recommendation tier, sets `max_turns` for the triage subagent, and passes relevant metadata (total lines, section boundaries, POV pattern) to subagents so they don't have to rediscover it.

**Script location:** `scripts/preflight.sh`. Usage: `./scripts/preflight.sh <manuscript_path> [output_path]`. If output path is omitted, writes to stdout.

### Context Window Detection

The parent orchestrator determines its available context window before selecting an execution mode. This is a model-level property, not something the preflight script can measure.

**How to detect:** The parent orchestrator checks the model identifier or host metadata from the current session. Any model documented as supporting ≥1M token context qualifies for the large-context execution tier. When uncertain, assume standard-context and use the conservative recommendation tier.

**Why this matters:** The original motivation for per-pass subagent dispatch was twofold: (1) compaction resilience — platform context compaction could lose analytical work mid-run, and (2) salience decay — in a 200K window, earlier pass artifacts lose salience by synthesis time. With a 1M context window, a typical novel (~180K tokens) plus all analytical overhead fits comfortably without compaction risk or salience decay. This makes single-agent mode viable as a default for most manuscripts, while preserving multi-agent modes for manuscripts that exceed the window or for users who want architectural isolation.
