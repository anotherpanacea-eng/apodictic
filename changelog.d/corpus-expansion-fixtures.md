### Evals — Corpus-expansion synthetic fixtures

Three behavioral-eval fixture sets author-added under `evals/fixtures/`, each carrying a
pre-registered `expected.md` ground-truth key (the argument-benchmark registration
discipline): **`ai-prose-calibration/`** — a synthetic AI-heavy prose sample that fires the
four previously-unexercised AI-Prose Calibration families (AIC-2 Velvet Fog, AIC-4 Register
Seams, AIC-6 Continuity Smear, AIC-8 Unearned Fluency) with named-flag invocation targets,
plus a voiced clean-control for false-positive scoring; **`tag-audits/`** — one ~500-word
scene each exercising the queer-romance-erotica, cozy, and philosophical tag audits, plus a
no-tag negative baseline; and **`execution-mode-ab/`** — a single-agent vs. multi-agent
(swarm) A/B pair sharing one manuscript with a registered real-issue-recall set and the
`docs/swarm-vs-single-eval.md` decision rule. All three are **pure data** — no mechanical
`validate.sh` arm parses them (the `argument-groundtruth-check` gate walks only
`argument-benchmark/`), and they live under repo-root `evals/` so the `codex/` + `antigravity/`
host builds are unaffected. The downstream model-run eval-coverage confirmation report is
**deferred** (per the corpus-expansion survey): these are the fixtures only, not the sign-off run.
