### Nonfiction Argument Engine — Modularization (Workstream A)

Promoted the nonfiction argument path from implicit to named and bounded:

**Named skill.** `skills/nonfiction-argument-engine/SKILL.md` is now a first-class skill alongside `core-editor`, `specialized-audits`, `revision-coach`, and `plot-architecture`. The skill defines the delegation contract (triggered from `core-editor §Delegation Rules` when intake resolves `constraint=nonfiction` + persuasive-argument form), scope boundary, owned references, argument engine workflow, and QA guardrails. `core-editor/SKILL.md` gained an explicit `§ Nonfiction Argument Engine` delegation rule replacing the previous implicit routing through `specialized-audits`.

**Firewall single-sourced.** The canonical Firewall definition (`## The Firewall` + no-content-invention rule text) was extracted from the inline section in `core-editor/SKILL.md` to a new shared `references/firewall.md`. The engine skill and the core-editor pointer both reference this single file. `meta_lint.py` M7 (single-Firewall) enforces that exactly one plugin `.md` file carries the canonical definition — prose mentions and pointers are fine; a second definition is a lint error.

**Five interleaved tables split into dedicated fragments.** Argument-cluster rows extracted from `pass-dependencies.md` §4a, §4b, §4e and from `intake-router-runtime.md §4a` and `run-synthesis.md §Step 8` into four named reference files:

- `argument-audits-routing.md` — §4a Field Recon + Citation Verifier rows + §4b Dialectical Clarity / Consent / Reception rows
- `argument-audits-propagation.md` — §4e argument-cluster signal-propagation rows (Dialectical Clarity, Red Team, Persuasion, Evidence, Adversarial Evidence Review, Field Recon, Citation Verifier) — byte-identical to source; confirmed by `evals/fixtures/argument-carve/4e-before-after.diff`
- `nonfiction-intake-routing.md` — nonfiction triage branch (route conditions, hybrid rule, default-by-form table, post-diagnostic offer)
- `synthesis-argument.md` — Argument-DE parallel decision-layer schema (detection markers, skip contract, override path)

Source files retain `REPLACED-WITH-INCLUDE` pointer comments.

**Behavior-preservation guarantees.** The split is proven behavior-preserving on the mechanical resolver layer by two gates with teeth: `audit-signal-propagation --check-registry` asserts all 45 signal-emitting audits still have §4e propagation rows (it fails if the split fragment is dropped), and the byte-identical §4e extraction is confirmed by `evals/fixtures/argument-carve/4e-before-after.diff`. A supplementary `argument-carve-behavior-preservation` smoke gate (`validate.sh`, wired into `--check-all`) re-runs the mechanical resolvers on a fixed pre-carve fixture and confirms they still classify it as Argument-DE without regressing to error.
