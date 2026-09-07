# Continuity corrective experiment

A frozen, exploratory comparison of the existing fiction benchmark projection
with a small generic continuity-grounding instruction. See [PROTOCOL.md](PROTOCOL.md)
for the decision rule and [SCORING.md](SCORING.md) for anonymous advisory grading.
No production prompt, registered source, key, or existing candidate is modified.

## Saved stopping point

The 2026-09-07 production phase is complete: **64/64 sealed outputs**, with
zero failed or contaminated receipts. The owner requested a stop here. **0/128
advisory scoring calls have run**, so no corrective-effect result or model-quality
comparison is claimed. The production controller has exited; raw diagnosis and
key bodies have not been inspected by the orchestrator.

[PRODUCTION-RECEIPT.json](PRODUCTION-RECEIPT.json) records requested model counts,
reported usage, elapsed time, and whole-artifact hashes for the frozen manifest,
completion index and accounting adapter. Raw outputs and per-cell mappings remain
local in ignored results. Subscription invocation cost is unknown per call.

On continuation, preserve these production bytes and the existing scoring anchors.
The dated scorer launch deadline is 2026-09-08 01:45 UTC. A later continuation
needs a reviewed new scoring freeze identity/window; never edit a frozen manifest
or rerun completed productions to extend a deadline. Keep the independent scoring
and final interpretation separate from this completed production phase.

## Run locally

Use Python 3.12+ and an authenticated Codex subscription CLI that supports both
requested models. Version 0.153.4 passed readiness checks; 0.147.0 refused Astra.
The user/project configuration is excluded from runner input, tool features are
disabled, the sandbox remains read-only, and exec-policy rules remain enabled.
The exact command is saved for every invocation. [Codex non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode)
describes the underlying structured event and final-output interfaces.

From the repository root, choose a fresh ignored result directory:

```text
python evals/experiments/fr02-corrective-retest-20260907/experiment.py freeze --repo . --root evals/results/FR02-RUN --codex /path/to/codex
python evals/results/FR02-RUN/frozen/experiment.py run --root evals/results/FR02-RUN
python evals/results/FR02-RUN/frozen/experiment.py status --root evals/results/FR02-RUN
```

This dated experiment stops new productions at 2026-09-08 01:00 UTC. A later
campaign requires a new reviewed protocol and run identity; do not edit this
run's frozen manifest to extend it. Readiness probes are separate from the
64-production denominator. Status checks hashes but does not infer that a process
is terminal from a stale-looking file. Poll the real process handle first.

For an interrupted unsealed row, `recover --root ... --row rNNN` refuses while
its recorded controller or child is live, preserves partial bytes and seals an
interrupted disposition. For a failed transport or interrupted base attempt,
`run --root ... --row rNNN` permits one retry under a separate `retry-1/` directory.
Completed answers and contaminated runs are never retried to improve results.
The default run resumes verified completions and stops new dispatch after the
first noncompletion; each already-live invocation finishes into its own directory.

After all productions are sealed, assemble anonymous scorer packets:

```text
python evals/experiments/fr02-corrective-retest-20260907/score.py assemble --primary evals/results/FR02-RUN --root evals/results/FR02-SCORES --repo .
python evals/results/FR02-SCORES/frozen/score.py run --root evals/results/FR02-SCORES
python evals/results/FR02-SCORES/frozen/score.py status --root evals/results/FR02-SCORES
```

Scorer identity and quote verification are mechanical checks, not correctness
or human truth licenses. Keep raw outputs and private mappings in ignored
results. Publish only the reviewed aggregate interpretation and whole-artifact
hashes. The full review and results will be linked here when complete.

## Verification

```text
python evals/experiments/fr02-corrective-retest-20260907/test_experiment.py
python evals/experiments/fr02-corrective-retest-20260907/test_score.py
python evals/experiments/fr02-corrective-retest-20260907/test_summarize.py
bash scripts/validate.sh --check-all
```

On Windows, Git Bash's standard `usr/bin/core_perl` directory must be on PATH
for the existing contract-hash/check validators to find `shasum`. No shim or
validator change is needed. Tests exercise custody, interruption, full matrix
coverage, treatment-only prompt differences and scorer identity/evidence checks.
