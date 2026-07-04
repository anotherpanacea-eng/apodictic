# AI-Prose Calibration — unexercised flag-family fixtures

Ground-truth fixtures for the AI-Prose Calibration audit
(`plugins/apodictic/skills/specialized-audits/references/craft/ai-prose-calibration.md`).
All fixture text is **synthetic** — authored for this eval, no permission constraints
(provenance tier 1, per `evals/fixtures/argument-benchmark/CORPUS.md §Provenance tier`).

## Why this set exists

The audit defines seven numbered flag families, **AIC-1 through AIC-7**, plus **Unearned
Fluency** — the *meta-category* they all manifest (the audit's "Why Seven Flags" note; there is
no numbered AIC-8 in the reference — "AIC-8" is only a repo-wide shorthand for the umbrella
verdict, kept here for continuity with the ROADMAP/changelog). Prior canonical coverage
exercised **AIC-1** (Generic Hand / Voice Singularity), **AIC-3** (Echo Stack), **AIC-5** (Puppet
Dialogue), and **AIC-7** (Discourse Leak). The remaining families lacked any fixture that
genuinely exhibits them:

| Flag | Name | What the audit hunts for |
|------|------|--------------------------|
| **AIC-2** | Velvet Fog | Scene fog + lexical genericism — unspecified spaces, generic physical detail, indefinite-pronoun gesture ("something," "a kind of") |
| **AIC-4** | Register Seams | Multi-source splicing — bad drift: a vocabulary/confidence shift that serves nothing and breaks reader trust |
| **AIC-6** | Continuity Smear | World-model failures — objects teleport, spatial positions contradict, time smears, a character knows what hasn't been revealed |
| **AIC-8**\* | Unearned Fluency | The meta-category (\*not a numbered audit flag — the umbrella verdict AIC-1–7 manifest) — grammatically smooth prose where you can swap any sentence for a paraphrase and lose nothing; competence without consequence |

This set supplies a single AI-heavy prose sample deliberately drafted to fire exactly those
four families, with named-flag invocation targets, so a real audit run has ground truth to
score against and a no-AIC contrast is available in `clean-control.md`.

## What this tests (and what it does not)

This is a **behavioral** eval, not a mechanical check. There is no `validate.sh` arm that
parses this fixture — the AI-Prose Calibration audit is model-interpreted prose diagnosis.
These files test whether an audit run **names the four target families with the right
evidence and severity band**, and whether it **spares** the clean control. The
`argument-groundtruth-check` gate only walks `evals/fixtures/argument-benchmark/*/`; it does
not touch this directory, so these fixtures are **pure data**.

| File | Role |
|------|------|
| `ai-heavy-prose.md` | The AI-drafted sample. Exhibits AIC-2 / AIC-4 / AIC-6 / AIC-8 by construction. |
| `clean-control.md` | A voiced, grounded, continuity-clean human-style passage on the same subject. The audit must NOT fire AIC-2/4/6/8 here (a false-positive control). |
| `expected.md` | Pre-registered diagnosis (written before any run — the argument-benchmark ground-truth discipline). |

## Running it

Run the AI-Prose Calibration audit (Layer B flag scan, `ai-prose-calibration.md §Step 2`)
against `ai-heavy-prose.md`, then score the produced flag summary against `expected.md`.
Repeat against `clean-control.md` and confirm the four target families stay clean. The
model-run coverage-confirmation report (per the ROADMAP corpus-expansion survey) is a
separate, deferred deliverable — these files are the fixtures only.
