### Reference hygiene

Shipped references no longer cite `docs/` files that do not exist (the F4
Stage 2 review, the Pass 10 timeline spec, the eval-harness spec); the
reference index now says that `docs/`, `evals/`, and `ROADMAP.md` paths are
repo-only provenance, never load targets. The model-tag table gains current
Claude rows (`opus55`, `sonnet55`, `opus5`, `fable51`), so runs on those models
pass `dispatch-record`'s tag check, and the plugin README's context example
names Claude Opus 5.5. The compression-audit expansion stub and the audit
expansion template move out of the plugin to `docs/audit-expansion/`.
ROADMAP validator counts are updated.
