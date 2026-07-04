# Mode A — Single-Agent Long-Context config

The **single-agent** arm of the A/B pair. One agent reads the whole of `manuscript.md` in a
single long context and produces one consolidated developmental-findings output. No subagent
fan-out, no per-lens isolation, no consolidation step.

- **Input:** `manuscript.md` (verbatim, whole).
- **Execution mode:** single-agent (`run-core.md §Execution Mode`, the ≥1M-context default
  when the manuscript fits).
- **Pre-Pass Re-Grounding / Staged Visibility:** run in their **single-agent** form — this is
  precisely the less-observable mode the ROADMAP A/B item exists to exercise (the mode-
  conditional instructions have no paired fixture for direct observation otherwise).
- **Output artifact:** one scorer-readable consolidated findings list (finding id, severity
  band, failure locus, one-line rationale) — the shape `expected.md` scores recall against.
- **Cost capture:** log tokens in/out for this run (the cost axis; see `expected.md` and
  `docs/swarm-vs-single-eval.md §Metrics`). Omit the cost comparison if token capture is
  unavailable rather than fabricating it.

Pin the **same model snapshot** used for the multi-agent arm, so any delta is a mode effect,
not version drift (`docs/swarm-vs-single-eval.md §Honest scoping`).
