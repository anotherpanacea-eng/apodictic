# Reference File Index

*Full load-on-demand index for the APODICTIC core editor. `SKILL.md` keeps a compact routing map; this file holds the complete tables (execution, genre modules, templates, other, deprecated).*

### Execution
| File | When to Load |
|------|-------------|
| `references/run-core.md` | Every Core DE and Full DE run (intake, pass execution, ledger protocol) |
| `references/audit-routing-table.md` | At the contract step — contract-driven audit-activation rules + signal-emitting-audit registry |
| `references/execution-modes-reference.md` | At dispatch (run start) — pre-flight and context-window detection detail |
| `references/findings-ledger-format.md` | When writing or validating per-pass ledger entries (entry template + Structured Findings Block) |
| `references/run-synthesis.md` | After passes complete (audit integration, synthesis, deliverables, evidence spot-check) |
| `references/state-lifecycle.md` | State gardening and revision rounds (loaded by `/start`, `/coach`, revision workflows) |
| `references/pass-dependencies.md` | When resolving concern to scoped pass set and dependency order |
| `references/run-full.md` | When selected pass set includes advanced passes (3, 4, 6, 7, 9, 10) |
| `references/output-policy.md` | Before writing any output (editorial letter, pass reports) |
| `references/output-structure.md` | At write/persist time — folder architecture, output naming, lifecycle, rolling-state and sidecar updates |
| `references/adversarial-stress-test.md` | During every editorial letter synthesis (§7 of letter) |
| `references/partial-manuscript.md` | When `artifact=partial` — modifies pass behavior for incomplete drafts |
| `references/editor-scaffolding.md` | When `operator:editor` — reframes the synthesis letter for a human developmental editor (editor-facing overlay) |
| `references/diagnostic-vocabulary.md` | When `operator:facilitator` — produces a Vocabulary Guide (glossary + discussion prompts) for a writing-group facilitator |
| `references/fragment-synthesis.md` | When `artifact=fragments` and goal=`draft` — pre-diagnostic clustering |
| `references/handoff-protocol.md` | When offering/entering/exiting scene-level execution mode |
| `references/character-architecture.md` | When detailed character analysis needed beyond Pass 5 basics |
| `references/pass-11.md` | When market viability / publication readiness is requested |

### Genre Modules
| File | When to Load |
|------|-------------|
| `references/genre-literary.md` | Literary fiction primary or secondary |
| `references/genre-horror.md` | Horror primary or secondary |
| `references/genre-sff.md` | SF/F primary or secondary |
| `references/genre-romance.md` | Romance primary or secondary |
| `references/genre-mystery.md` | Mystery primary or secondary |
| `references/genre-thriller.md` | Thriller primary or secondary |

### Templates
| File | Purpose |
|------|---------|
| `references/contract-template.md` | Contract schema template |
| `references/diagnostic-state-template.md` | Diagnostic state initialization |
| `references/diagnostic-state-meta-template.json` | Machine-readable sidecar template (written alongside Diagnostic_State.md) |
| `references/reverse-outline-template.md` | Reverse outline format |
| `references/intake-router-runtime.md` | Runtime routing spec for `/start` command |
| `references/intake-router-design.md` | Router rationale and implementation notes (non-runtime) |
| `references/series-state-template.md` | Series continuity state initialization |

### Other References
| File | Purpose |
|------|---------|
| `references/changelog.md` | Version history |

### Deprecated (do not load)
| File | Superseded by |
|------|--------------|
| `references/core-framework.md` | SKILL.md + run-core.md + run-full.md + all reference files |
| `references/module-index.md` | `AUDIT_SELECTION_MATRIX.md` + `specialized-audits/SKILL.md` |
| `references/intake-router.md` | `references/intake-router-runtime.md` + `references/intake-router-design.md` |
| `references/intake-questions.md` | `references/run-core.md` §Hypothesis-Driven Intake Questions |
| `references/certainty-axis.md` | `references/run-full.md` §Certainty Axis Cues |
| `references/structural-frameworks.md` | `references/run-full.md` §Structural Frameworks |

