# Antigravity Parity Notes

This file tracks the architectural alignment between the original APODICTIC framework and the native Antigravity packaging.

## Current Alignments
1. **Slash Command Routing**: Native Antigravity `.agents/workflows/` intercept commands (e.g. `/start`, `/develop-edit`) directly from the user chat.
2. **Execute Delegation**: Antigravity's `core-orchestrator` Subagent autonomously reads state triggers and executes the canonical `run-core.md` execution logic without requiring proxy wrappers.
3. **Canonical Truth**: All files strictly reference the single authoritative APODICTIC runtime.
4. **Folder Architecture**: Output follows the v0.5.0 folder architecture — rolling state at the project root, run artifacts in `runs/YYYY-MM-DD_{model}_{type}/`. See `output-policy.md` §Folder Architecture.
