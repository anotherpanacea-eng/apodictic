# Execution-Mode A/B fixture pair — single-agent vs. multi-agent (swarm)

Ground-truth fixture pair for the **single-agent vs. multi-agent staging** eval
(`docs/swarm-vs-single-eval.md`). Pre-Pass Re-Grounding and Staged Visibility are mode-
conditional; their less-observable **single-agent** mode had no paired fixture for direct A/B
observation. This pair supplies one shared scene run under both modes so the mode-conditional
instructions can be observed side by side.

All fixture text is **synthetic** (no permission constraints; provenance tier 1).

| File | Role |
|------|------|
| `manuscript.md` | The shared input. Both arms read this exact text. Carries 6 registered ground-truth developmental findings + 2 decoys. |
| `single-agent-config.md` | Mode A: one long-context agent, no fan-out/consolidation. The less-observable mode. |
| `multi-agent-config.md` | Mode B: swarm fan-out + Findings Ledger + consolidation. |
| `expected.md` | Registered GT recall set, decoys, and the pre-registered decision rule (from `docs/swarm-vs-single-eval.md`). |

## What this tests (and what it does not)

This is a **behavioral** eval scaffold. Scoring is **real-issue recall** (TP / registered GT)
per arm — the one metric that survives the adversarial methodology review in
`docs/swarm-vs-single-eval.md` (a general false-positive rate is *not* computable from a thin
GT key). There is no `validate.sh` arm that parses this pair, and the `argument-groundtruth-
check` gate walks only `evals/fixtures/argument-benchmark/*/`, so these fixtures are **pure
data**.

**The run itself is deferred and cannot execute on the current in-repo harness.** Per review
finding B2, running mode as a variable needs a dedicated build (mode-comparable orchestration
+ token capture + a scorer-readable consolidated artifact per mode) that does not yet exist.
This pair is the **shared inputs + registered GT + decision rule** — the scaffold a future
build scores against — not the run outputs. It is also a single short scene (a schema/GT
scaffold), not the powered long-fiction arm the decision rule's "long-fiction" clause
requires; the N=1 pilot in `docs/swarm-vs-single-eval-pilot/` is directional only.

The model-run coverage-confirmation report (per the corpus-expansion survey) is **deferred** —
these files are the fixtures only.
