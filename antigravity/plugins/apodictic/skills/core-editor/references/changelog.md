# APODICTIC Development Editor Changelog

All notable changes to the APODICTIC Development Editor (APDE) framework will be tracked in this file.

This changelog started at `v0.4.4.1` on **2026-02-13**.  
Historical backfill entries for `v0.4.4` and `v0.4.3` were added the same day from local file history and release notes.

## v1.8.3 - 2026-04-25

### Fixed — Phase 7 Wave 4: antigravity plugin.json JSON-corruption bug; defensive JSON-parse check added

Closes Phase 7 Wave 4 of the model-capability review per `docs/review-log/2026-04-25_phase-7-implementation-plan.md` §Wave 4. Wave 4 is closing-gate work: D2 host parity sweep + D3 Phase 7 done-gate verification. The parity sweep surfaced one critical drift item beyond what the mechanical `--check` calls catch — fixed in this release.

#### D2 host parity sweep — finding

`antigravity/plugins/apodictic/plugin.json` was being generated with a literal two-character string `\n` (backslash followed by lowercase n) instead of a real newline at end-of-file, because `scripts/build-antigravity.mjs` line 250 wrote `+ "\\n"` (escaped backslash) rather than `+ "\n"` (newline). The mechanical `node scripts/build-antigravity.mjs --check` did not catch this because it compared the freshly-generated workspace to the persisted workspace; both copies were corrupted identically. Result: the antigravity host's `plugin.json` was unparseable JSON (`SyntaxError: Unexpected non-whitespace character after JSON at position 1227`) for the entirety of v1.7.7 (when antigravity build was added) through v1.8.2.

Severity assessment: **build-script bug** per Phase 7 plan §D2.4 classification — fix immediately. The bug never surfaced in mechanical release checks because no consumer verifies JSON validity of the generated plugin.json — the file is consumed by the Antigravity host runtime, which would presumably reject it on installation. No user reports to date, so blast radius is limited to whoever attempted an Antigravity install of APODICTIC during the v1.7.7-v1.8.2 window.

#### Fix

- **`scripts/build-antigravity.mjs` line 250** — changed `+ "\\n"` (literal backslash-n) to `+ "\n"` (newline). One-character change.
- **`scripts/build-antigravity.mjs`** — added defensive `readJson(...)` re-parse of the generated `plugin.json` after write, so any future JSON-corruption regression fails the build immediately rather than silently passing through `--check` (which compares against itself). ~10 lines of validation logic + comment.
- **`antigravity/plugins/apodictic/plugin.json`** — regenerated with valid trailing newline; now parses as valid JSON.

#### D2 sweep — full results (parity holds elsewhere)

Spot-checked semantic parity across canonical → codex and canonical → antigravity:

- **Validate.sh + preflight.sh** — byte-identical across plugin source, codex, antigravity (`diff -q` confirms).
- **Skills tree (canonical → antigravity)** — byte-identical except .DS_Store cruft. All `references/` content preserved.
- **Skills tree (canonical → codex)** — diffs are all mechanical slash-to-wrapper rewrites (`/start` → `apodictic-start`, etc.) per the documented Codex transform. Spot-checked SKILL.md, run-core.md, changelog.md, series-continuity.md, plot-architecture/SKILL.md, pre-writing-pathway/SKILL.md, command files: every diff line is the slash-rewrite transformation, no semantic drift.
- **Frontmatter versions** — all SKILL.md frontmatter matches canonical (1.8.2 pre-bump, 1.8.3 post-bump) across all three trees.
- **Codex wrapper skills** — 11/11 commands have matching `apodictic-*` wrapper SKILL.md; all reference correct base skill and command path.
- **Antigravity workflow files** — 11/11 commands have matching `.agents/workflows/*.md`; orchestrator `instructions.md` reads correct canonical paths.
- **Cross-host contamination** — Codex `NON_PARITY_NOTES.md` does not mention Antigravity; Antigravity `NON_PARITY_NOTES.md` does not mention Codex. Host isolation preserved.
- **Codex JSONs (`.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`)** — both parse as valid JSON.
- **Antigravity `agents/core-orchestrator/agent.json`** — parses as valid JSON.

#### D3 Phase 7 done-gate verification

All 10 Phase 7 done-gate criteria verified CLOSED. All 6 spec §First Ship Gate criteria verified CLOSED. Verdict: **Phase 7 complete.** See `docs/review-log/2026-04-25_phase-7-wave-4-done-gate-verification.md` for per-criterion evidence.

#### Files

- `scripts/build-antigravity.mjs` — fix `"\\n"` → `"\n"` literal; add defensive JSON re-parse of generated plugin.json (~10 lines).
- `antigravity/plugins/apodictic/plugin.json` — regenerated valid (trailing newline correct; parses as JSON).
- `plugins/apodictic/skills/core-editor/references/changelog.md` — v1.8.3 entry.
- Version bumped via `scripts/bump-version.sh 1.8.3`.
- Generated host workspaces (codex, antigravity) regenerated via release pipeline (validate.sh / preflight.sh remain byte-identical to plugin source).

Total framework prose change: ~10 lines net (build-script fix + JSON parse guard). No skill content edits. No validator changes; all 11 validator self-tests PASS.

#### Self-test verification (v1.8.3)

| Validator | Cases | Status |
|---|---|---|
| `severity-floor` | 7 | PASS |
| `audit-signal-propagation` | 9 | PASS |
| `underdiagnosis-triggers` | 5 | PASS |
| `ledger-consolidation` | 5 | PASS |
| `decision-layer-check` | 12 | PASS |
| `quality-risk-triggers` | 12 | PASS |
| `timeline-diff` | 8 | PASS |
| `timeline-arithmetic` | 6 | PASS |
| `timeline-anchor-conflict` | 6 | PASS |
| `audit-tier-criterion` | 4 | PASS |
| `argument-recon-prerequisite` | 5 | PASS |

#### Out of scope

- Wave 5 closeout (Codex final review + E1 final report + E2 ROADMAP update) is the next and final wave; not in v1.8.3 scope.

---

## v1.8.2 - 2026-04-25

### Added — Phase 7 Wave 3: cross-cutting rule dedup + Plot Architecture vs Pass 2 boundary + Focus Map empirical test ROADMAP deferral

Closes Phase 7 Wave 3 of the model-capability review per `docs/review-log/2026-04-25_phase-7-implementation-plan.md` §Wave 3. Three jobs ship as a coordinated wave: C1 — cross-cutting rule dedup with canonical-home annotations (firewall, anti-sycophancy / no-self-revise, absence-first / blind-spot disclosure, Pass-10-Class artifact pattern); C2 — Plot Architecture vs. Pass 2 (Structural Mapping) boundary clarification; B2 — Focus Map empirical test formalized as ROADMAP entry (test runs not executed in this cycle; deferred per Phase 5 resource-cost rationale, formalized in Wave 3 with named re-evaluation triggers). Net framework prose change: small positive (canonical-home annotations and boundary block exceed the few collapsed restatements). No validator changes; all 11 validator self-tests pass.

#### C1 — Cross-cutting rule dedup

Phase 3 inventory identified five cross-cutting rules added during Phase 4-6 to a shared dedup table; per Phase 3 spec ("compression deferred to Phase 7 only after eval coverage exists"), Wave 2's B1 eval coverage of UNPROVEN instructions unblocked compression work in Wave 3. Each rule receives a canonical-home annotation marking the authoritative statement; non-canonical surfaces collapse generic restatements to pointers while preserving any context-specific elaboration.

- **Firewall — canonical home: `core-editor/SKILL.md §The Firewall`.** Annotation added naming downstream surfaces (`revision-coach/SKILL.md §The Coaching Firewall`, `adversarial-stress-test.md §Firewall Compliance`, `run-full.md §QA gate`, `pass-11.md §Forbidden`) and noting that those surfaces preserve only context-specific elaborations (coaching-mode drift, stress-test scope, market-viability scope). No generic restatements collapsed in this Wave — all downstream firewall mentions are already context-specific (coaching-firewall, stress-test firewall, pass-11 firewall, supplementary-audit firewall). The annotation prevents future drift by marking the canonical home explicitly.

- **Anti-sycophancy / no-self-revise — canonical home: `core-editor/references/output-policy.md §Severity Honesty Protocol`.** Annotation added naming downstream surfaces (`adversarial-stress-test.md §Lock-then-test protocol` / §Anti-softening rule, `specialized-audits/references/craft/reception-risk.md §Lock-then-classify` / §Forbidden #6, `run-synthesis.md §Step 5 Adversarial Self-Check`). Two reception-risk parentheticals collapsed to canonical pointer ("Anti-sycophancy / no-self-revise rule canonical in `core-editor/references/output-policy.md §Severity Honesty Protocol`."); preserves the audit-specific operational instructions (lock-then-classify discipline; "Reduce severity ratings through self-generated counter-arguments after locking" forbidden). Adversarial-stress-test §Lock-then-test sentence rewritten to point at the canonical rule while preserving the stress-test-specific elaboration (lock-before-steelman ordering). Per-audit Deficit-First Diagnostic Rule blocks (each audit-tailored) explicitly preserved in their audit reference files — they are operational expressions of the principle, not generic restatements.

- **Absence-first / deficit-first framing AND blind-spot disclosure as confidence limiter — canonical home: `core-editor/references/run-synthesis.md §Step 3 Blind Spot / Absence Inventory`.** (Two cross-cutting rules consolidated under one canonical home because Step 3 already integrates both: the Absence Inventory is the absence-first operational step; the Mandatory blind-spot disclosure paragraph is the confidence-limiter rule.) Annotation added naming downstream surfaces (`output-policy.md §Severity Honesty Protocol` rule #5 evidence-first checks, `submission-readiness.md §Blind-spot rule`, `pass-dependencies.md §4c` Auto-recommend before synthesis decline policy, `specialized-audits/SKILL.md §How to Use` Field Reconnaissance prerequisite paragraph). Submission-readiness §Blind-spot rule extended with canonical-home pointer while preserving the submission-readiness-specific elaboration (which audits, how the readiness verdict carries the limiter forward). Per-audit Deficit-First Diagnostic Rule opening blocks in `specialized-audits/references/craft/*.md` (11 audits — stakes-system, dialectical-clarity, ai-prose-calibration, interiority-preservation, emotional-craft, banister, decision-pressure, scene-turn, female-interiority, character-architecture, compression-audit) explicitly preserved — they are audit-tailored operational expressions, not generic restatements.

- **Pass-10-Class rolling artifact pattern — canonical home: `core-editor/SKILL.md §Project Integration §Pass-10-Class Rolling Structured Artifacts`** (already established in Phase 4). Annotation added naming downstream surfaces (`pass-dependencies.md §1 Tier 1 Pass 10 row`, `run-synthesis.md §Step 2 Pass-10-Class artifact integration`, `references/pass-10.md`) and noting that those surfaces add only artifact-instance specifics (Timeline schema, Argument_State schema, etc.). No generic restatements collapsed — downstream surfaces already cite back to the canonical home; the annotation prevents future drift.

**Risk-controlled dedup decisions (no rule deferred for risk).** Each cross-cutting rule had its canonical home statement spot-checked for sufficiency in isolation: the firewall block in `core-editor/SKILL.md` is complete (FORBIDDEN list + ALLOWED list + example); the anti-sycophancy block in `output-policy.md §Severity Honesty Protocol` is complete (5 manifestations + 5 rules); the absence-first + blind-spot disclosure block in `run-synthesis.md §Step 3` is complete (Absence Inventory protocol + Mandatory blind-spot disclosure paragraph for argument-shaped runs). Pointers preserve the contextual hint ("the audit-specific lock-then-classify discipline implements the canonical rule") so downstream readers reach the canonical statement without losing the local operational instruction. **No load-bearing redundancy was deferred** — all collapsed locations were generic parentheticals or one-line restatements, never the load-bearing operational instruction itself.

#### C2 — Plot Architecture vs. Pass 2 (Structural Mapping) boundary clarification

Phase 3 inventory flagged the boundary between Plot Architecture (a separate skill orchestrator covering 50 spines, 12 families, fantasy/series architecture) and Pass 2 (Structural Mapping in core editor) as ambiguous. Authors and models could confuse which to invoke when. Wave 3 ships explicit boundary documentation in three locations:

- **`plot-architecture/SKILL.md` — new §Plot Architecture vs. Pass 2 (Structural Mapping) — Boundary section** (~25 lines). Comparison table covering writer question, layer-of-operation, output, when-to-invoke, and routing for each. Cross-references in practice: Plot Architecture → Pass 2 (when a STRUCTURAL BREAK at the spine level wants on-page mapping); Pass 2 → Plot Architecture (when on-page structural symptoms cannot be diagnosed at the spine level). Rule-of-thumb: "what kind of book is this structurally" → Plot Architecture; "is the structure I have on the page working" → Pass 2; both → Pass 2 first, then Plot Architecture against the honest map.
- **`pass-dependencies.md §1 Tier 1 Pass 2 row** — extended Pass 2 output-artifact cell (~1 line) with the boundary callout pointing at `plot-architecture/SKILL.md` for spine-paradigm questions.
- **`core-editor/SKILL.md §Delegation Rules §Plot Structure** — extended (~3 lines) with the boundary distinction (Plot Architecture handles whole-work spine paradigm; Pass 2 handles on-page structural execution) and a cross-reference to the plot-architecture boundary section.

Total ~30 lines added across three files. The boundary clarification is small-scope and additive — no existing prose was rewritten or removed, no existing routing changed.

#### B2 — Focus Map empirical test formalized as ROADMAP deferral

Phase 5 deferred the Focus Map empirical test (6-fixture comparison: 3 fixtures × 2 arms — control vs. treatment) for resource reasons. The test framework was documented in `hybrid-mode.md §Focus Map Architectural Decision Framework`. Wave 3 formalizes the deferral as a named ROADMAP item rather than running the test in this cycle.

- **`ROADMAP.md` — new §Deferred (Empirically-Gated Decisions) section** added between §Not Planned and §Done, with one entry: "Focus Map Architectural Decision — Empirical Test." Entry covers source (Phase 5 deferred; Phase 7 Wave 3 formalized), current default (Focus Map remains hybrid-only — conservative per spec §Phase 5), hypothesis + acceptance criteria reference (pointer to `hybrid-mode.md §Focus Map Architectural Decision Framework`), test scope (6 runs total: 3 fixtures × 2 arms), and re-evaluation triggers (fixture corpus expansion making the 6-run cost worthwhile, OR Pass 10 Timeline integration forcing the cross-mode question). Decision until re-evaluated: default holds.
- **`hybrid-mode.md §Focus Map Architectural Decision Framework §Test deferred`** — extended (~3 lines) with explicit pointer to the new ROADMAP entry, naming the re-evaluation triggers and confirming the framework default holds until trigger + acceptance-bar clearance.

#### Files

- `plugins/apodictic/skills/core-editor/SKILL.md` — firewall canonical-home annotation (~2 lines); Pass-10-Class artifact pattern canonical-home annotation (~2 lines); §Delegation Rules §Plot Structure boundary clarification (~3 lines).
- `plugins/apodictic/skills/core-editor/references/output-policy.md` — anti-sycophancy / no-self-revise canonical-home annotation in §Severity Honesty Protocol (~2 lines).
- `plugins/apodictic/skills/core-editor/references/run-synthesis.md` — absence-first + blind-spot disclosure canonical-home annotation in §Step 3 Blind Spot / Absence Inventory (~2 lines).
- `plugins/apodictic/skills/core-editor/references/adversarial-stress-test.md` — §Lock-then-test protocol rewritten to point at canonical rule (~1 line net change, no collapse).
- `plugins/apodictic/skills/specialized-audits/references/craft/reception-risk.md` — two parenthetical anti-sycophancy restatements collapsed to canonical pointers (~0 lines net; same word count).
- `plugins/apodictic/skills/core-editor/references/submission-readiness.md` — §Blind-spot rule extended with canonical-home pointer (~1 line).
- `plugins/apodictic/skills/plot-architecture/SKILL.md` — new §Plot Architecture vs. Pass 2 (Structural Mapping) — Boundary section (~25 lines).
- `plugins/apodictic/skills/core-editor/references/pass-dependencies.md` — Pass 2 row extended with boundary callout (~1 line).
- `ROADMAP.md` — new §Deferred (Empirically-Gated Decisions) section + Focus Map entry (~20 lines).
- `plugins/apodictic/skills/core-editor/references/hybrid-mode.md` — §Test deferred extended with ROADMAP pointer (~3 lines).
- `plugins/apodictic/skills/core-editor/references/changelog.md` — v1.8.2 entry.
- Version bumped via `scripts/bump-version.sh 1.8.2`.
- Generated host workspaces (codex, antigravity, APODICTIC-Gemini) regenerated via release pipeline.

Total framework prose change: net positive ~50 lines (canonical-home annotations + C2 boundary block + B2 ROADMAP/hybrid-mode pointers exceed the few collapsed parentheticals). No validator changes; no `validate.sh` change; root `scripts/validate.sh` remains byte-identical to plugin source. All 11 validator self-tests PASS. All 4 release checks PASS.

#### Self-test verification (v1.8.2)

| Validator | Cases | Status |
|---|---|---|
| `severity-floor` | 7 | PASS |
| `audit-signal-propagation` | 9 | PASS |
| `underdiagnosis-triggers` | 5 | PASS |
| `ledger-consolidation` | 5 | PASS |
| `decision-layer-check` | 12 | PASS |
| `quality-risk-triggers` | 12 | PASS |
| `timeline-diff` | 8 | PASS |
| `timeline-arithmetic` | 6 | PASS |
| `timeline-anchor-conflict` | 6 | PASS |
| `audit-tier-criterion` | 4 | PASS |
| `argument-recon-prerequisite` | 5 | PASS |

#### Out of scope (deferred Phase 7 work)

- **D2 — Generated host parity sweep + D3 — Phase 7 done-gate verification.** Wave 4 work.
- **E1 — Model-capability review final report + E2 — ROADMAP.md update.** Wave 5 work (the v1.8.2 ROADMAP edit is scoped to the B2 deferral entry only; the broader Wave 5 ROADMAP closeout updates ship in Wave 5).

---

## v1.8.1 - 2026-04-25

### Added — Phase 7 Wave 2: 11 UNPROVEN instructions eval coverage + decision-layer-check re-eval against canonical fixtures

Closes Phase 7 Wave 2 of the model-capability review per `docs/review-log/2026-04-25_phase-7-implementation-plan.md` §Wave 2. Two jobs ship as a coordinated wave: B1 — static-analysis eval coverage of the 11 UNPROVEN instructions identified by Phase 3 inventory + archaeology log against the four canonical fixtures (Regrets Only Opus + Codex, Dinner Party, TAY argument-DE); B3 — re-run of `decision-layer-check` against the four canonical fixtures after Wave 1 A1 calibration, with B3-extension calibration to close two remaining gaps (bold-paragraph subhead detection; Must-Fix entry-form filter). Validator suite total stays at 11; self-test extended from 11 cases to 12 (`decision-layer-check` adds `c1b_bold_subhead_clusters`). Phase 7 Wave 3 (Group C compression work) unblocked.

#### B1 — 11 UNPROVEN instructions eval coverage (static analysis)

Per Phase 3 inventory + archaeology, 11 instructions were classified Keep-UNPROVEN — meaning provenance evidence is missing OR the instruction's load-bearing effect was unverified at Phase 3 close. v1.8.1 documents static-analysis eval coverage of each instruction against the four canonical fixtures, classifying per fixture and producing per-instruction verdicts.

- **Verdict distribution:** 7 Confirmed load-bearing / 0 No detectable effect / 4 Ambiguous-or-Partial (3 due to fixture scope outside instruction's natural exercise class; 1 split confirmed/needs-corpus-expansion).
- **Zero v1.9.x deletion candidates surfaced.** All 11 instructions either show direct fixture evidence of load-bearing behavior or are scoped outside the current fixture set in ways the report documents — per spec discipline ("guesswork includes guessing the rule still matters when no test catches it failing"; unexercised ≠ not load-bearing), unexercised instructions are flagged for v1.8.x or v1.9.x corpus expansion, not deletion.
- **Highest-confidence findings:** (1) Universal-audit status criterion (B1-2): confirmed load-bearing in all four fixtures including in negative-disclosure form. (2) consent-complexity.md full file (B1-4): confirmed load-bearing across three of four in-scope fixtures with named-flag invocation (CC-6 Perpetrator Erasure observed in Dinner Party). (3) Auto-escalation + root-cause + findings-table caps (B1-3 / B1-8 / B1-9): three overlapping evals all converge on cap-honoring behavior across all four fixtures.
- **Corpus-expansion candidates for v1.9.x (per fixture-scope limitation, not deletion):** state-lifecycle gardening thresholds (synthetic state-file fixtures); ai-prose-calibration AIC-2 / AIC-4 / AIC-6 / AIC-8 flag families (synthetic AI-heavy fixture); queer-romance-erotica / cozy-tag / philosophical-tag tag audits (genre-specific short fixtures).
- **Output:** `docs/review-log/2026-04-25_phase-7-wave-2-eval-coverage.md` documents per-instruction location, stated effect, eval method, per-fixture findings, verdict, and recommendation. Summary table at top.

#### B3 — `decision-layer-check` re-eval against canonical fixtures + Wave 2 calibration extensions

Wave 1 (v1.8.0) shipped A1 calibration for the four C1-C4 patterns identified by Phase 4 Wave 3. B3 re-runs the calibrated validator against F1-F4 to confirm the four FAILs from Phase 4 Wave 3 are resolved.

- **Pre-Wave-1 baseline:** F1 FAIL (2 checks); F2 FAIL (3 checks); F3 FAIL (2 checks); F4 FAIL (1 check + 1 WARN).
- **Post-Wave-1 (A1) result:** Approximately half of the original failures closed. Two patterns remained as A1 calibration scope-misses: (1) F1's Author Decisions section uses bold-paragraph subheads (`**Keep**`, `**Cut / Release**`, `**Unsure — decide before revision**`) rather than level-3 markdown subheads (`### Keep`); A1's C1 calibration only detected `### Keep`. (2) All four fixtures discuss "Must-Fix" extensively in body prose (severity-test commentary, Findings Ledger discussions) without those mentions being labeled finding entries; A1's C5 paragraph-block widening helped but didn't address the prose-vs-label distinction.
- **Wave 2 B3a — Bold-paragraph subhead detection.** C1 subhead-cluster count extended to detect both level-3 markdown subheads AND bold-paragraph subheads (`**Keep**`, `**Cut / Release**`, etc.) as cluster delimiters. Both forms are equivalent semantically; the validator now treats them as equivalent. Self-test adds `c1b_bold_subhead_clusters` (mirrors canonical Regrets Only Opus 4.7 fixture pattern: 13 sub-bullets across 3 bold-paragraph subheads → 3 cluster count → PASS).
- **Wave 2 B3b — Must-Fix entry-form filter.** Check 5 evidence-density previously counted every line containing the literal "Must-Fix" string as a labeled finding. Editorial letters discuss Must-Fix extensively in body prose (verdict commentary, severity-test discussion, ledger summaries) without those mentions being labeled entries. v1.8.1 extends the filter to count Must-Fix mentions only when in label form: heading line; list-item leader within first 80 chars; numbered list-item leader within first 80 chars; `**Severity:**` label co-located with Must-Fix; bare `Severity:` label at line start; MF-N anchor co-located with Must-Fix; pipe-table cell. Plus appendix-exclusion (appendix-only mentions are severity-calibration discussion, not labeled findings). The filter uses POSIX-portable `tolower()` + `index()` for case-insensitive matching (awk's `/i` regex flag is not POSIX-portable; initial implementation discovered this and corrected to portable form). Existing `neg4` self-test fixture restructured from bare prose `Must-Fix:` line to `### Must-Fix:` heading form to preserve the original test intent (label form with <2 references should still FAIL Check 5).
- **Post-Wave-2 (A1 + B3) result:** All four canonical fixtures (F1, F2, F3, F4) now produce **OK** on `decision-layer-check`. All 12 self-test cases PASS (added `c1b_bold_subhead_clusters`). No regression on the 6 prior validator self-tests.
- **Calibration effectiveness:** A1 (Wave 1) was partially effective; B3 extension (Wave 2) closes the remaining gaps. Across the two waves, all four Phase 4 Wave 3 calibration findings (C1-C4) plus the two Wave 2-surfaced patterns (bold-paragraph subhead form; prose-vs-label Must-Fix distinction) are resolved.

#### Files

- `plugins/apodictic/scripts/validate.sh` — `decision-layer-check`: B3a bold-paragraph subhead detection (~+15 lines); B3b Must-Fix entry-form filter with body-only scope (~+30 lines); self-test extended from 11 to 12 cases (added `c1b_bold_subhead_clusters`); `neg4` fixture restructured to use `### Must-Fix:` heading + bare-bullet Author Decisions to preserve original Check 5 negative-test intent. Net ~+95 lines.
- `scripts/validate.sh` — synced with plugin copy (canonical lives at `plugins/apodictic/scripts/validate.sh`; root copy is the user-facing alias).
- `plugins/apodictic/skills/core-editor/references/changelog.md` — v1.8.1 entry.
- Version bumped via `scripts/bump-version.sh 1.8.1`.
- Generated host workspaces (codex, antigravity) regenerated via release pipeline.

Total prose change: 0 lines in framework prose (all edits in `validate.sh` validator + self-test + new review-log entry). Total validator change: ~+95 lines in `validate.sh`. All 11 validator self-tests PASS. All 4 release checks PASS.

#### Self-test verification (v1.8.1)

| Validator | Cases (was → now) | New coverage |
|---|---|---|
| `severity-floor` | 7 | Unaffected |
| `audit-signal-propagation` | 9 | Unaffected |
| `underdiagnosis-triggers` | 5 | Unaffected |
| `ledger-consolidation` | 5 | Unaffected |
| `decision-layer-check` | 11 → 12 | B3a `c1b_bold_subhead_clusters` (bold-paragraph subhead form); B3b Must-Fix entry-form filter (existing `neg4` restructured) |
| `quality-risk-triggers` | 12 | Unaffected |
| `timeline-diff` | 8 | Unaffected |
| `timeline-arithmetic` | 6 | Unaffected |
| `timeline-anchor-conflict` | 6 | Unaffected |
| `audit-tier-criterion` | 4 | Unaffected |
| `argument-recon-prerequisite` | 5 | Unaffected |

#### Out of scope (deferred Phase 7 work)

- **B2 — Focus Map empirical test.** Wave 3+ work per Phase 7 plan §Wave 3 sequencing.
- **C1 — Cross-cutting prose compression.** Wave 3 work; unblocked by B1 closure.
- **C2 — Plot Architecture vs Pass 2 boundary clarification.** Wave 3 work.
- **D2 — Generated host parity sweep + D3 — Phase 7 done-gate verification.** Wave 4 work.

---

## v1.8.0 - 2026-04-25

### Added — Phase 7 Wave 1: decision-layer-check calibration + optional validators batch + v1.7.1 changelog backfill

Closes Phase 7 Wave 1 of the model-capability review per `docs/review-log/2026-04-25_phase-7-implementation-plan.md` §Wave 1. Three jobs ship as a coordinated wave: decision-layer-check calibration against the four C1-C4 Phase 4 Wave 3 eval-coverage findings (A1); two new validators from the Phase 6 + v1.7.9 §Out-of-scope queue (A2); v1.7.1 changelog backfill closing the documented release-hygiene gap (D1). Validator suite total: 9 → 11. v1.8.0 ships as the first release of the Phase 7 cycle (rc1 in plan terms; final 1.8.0 number reserved for end of Phase 7 closure once Waves 2-5 land).

#### A1 — `decision-layer-check` calibration (Phase 4 Wave 3 C1-C4 closure)

The Phase 4 Wave 3 eval-coverage report (`docs/review-log/2026-04-25_phase-4-eval-coverage.md`) documented four calibration findings against the four canonical fixtures (Regrets Only Opus + Codex, Dinner Party, TAY argument-DE). All four FAILs were calibration artifacts, not contract violations. v1.8.0 calibrates the validator's parsing logic to close them.

- **C1 — Author Decisions count over-fires on Keep/Cut/Unsure subhead clusters.** Phase 4-6 validator counted each sub-bullet across subheads (13 sub-bullets in Regrets Opus → out-of-3-7 ERROR). v1.8.0 detects `### Keep` / `### Cut` / `### Unsure` (also `### Defer` / `### Decide`) subheads within the Author Decisions section and counts subhead clusters (typical 1-3) when present. Implements the contract intent: "3-7 distinct decision categories, with sub-items permitted." Falls back to list-item counting when no subheads.

- **C2 — Codex paragraph-form decision entries undetected.** Phase 4-6 validator's heuristic order (list items → bolded paragraphs) returned zero on Codex 5.5 letters that use blank-line-separated paragraphs leading with verb-prefixed sentences ("Protect..." / "Keep..." / "Cut..."). v1.8.0 adds a third-fallback heuristic: count blank-line-separated paragraphs whose first sentence begins with a canonical decision verb (Protect / Keep / Cut / Defer / Decide / Unsure) or contains an opening bolded keyword (`**Decision:**`, `**Question:**`, `**Element:**`). Risk-controlled — only fires when list-item and bolded-paragraph heuristics return zero.

- **C3 — Argument-DE letters use different headings + lack canonical Appendix A/B/C.** TAY argument-shaped letters use "Coalition-Partner Ground-Truth Recommendations" and "Editorial-Dispute Territory" instead of "Protected Elements" / "Author Decisions"; they don't include Control Questions or Appendix A/B/C blocks. v1.8.0 detects argument-DE class via marker presence ("Coalition-Partner Ground-Truth Recommendations", "Editorial-Dispute Territory", "Argument_State", "Claim Ladder", "Argument Engine"). When detected: Check 1 accepts the variant heading names; Check 2 accepts "Editorial-Dispute Territory" as the equivalent decision section; Checks 3-4 (Control Questions, Appendix A/B/C) are skipped — argument-DE class is not held to fiction-DE structural contract.

- **C4 — Evidence-density 6-line window misses inline-prose evidence.** Phase 4-6 validator scanned exactly 6 lines after each Must-Fix mention; Codex letters with paragraph-form evidence (references in surrounding prose, not in an immediate trailing list) FAILed despite documenting evidence within the Must-Fix's section block. v1.8.0 widens the window to a paragraph-block scan: from each Must-Fix line until the next Must-Fix occurrence OR the next section header (^## at column 0), whichever comes first. Trade-off documented: wider window reduces false-positive density flags but is slightly less strict on truly under-evidenced Must-Fixes.

- **Self-test extended from 7 cases to 11.** Original cases preserved (pos, neg1-4, over1, over_appx); new cases added — `c1_subhead_clusters` (Keep/Cut/Unsure with 13 sub-bullets → 3 cluster count → PASS), `c2_paragraph_form` (Codex-style verb-leading paragraphs → paragraph-form fallback → PASS), `c3_argument_de` (argument-DE letter with Coalition-Partner / Editorial-Dispute headings → Checks 3-4 skipped → PASS), `c4_paragraph_evidence` (Must-Fix with inline-prose evidence in the surrounding paragraph block → paragraph-block window → PASS). Negative cases (neg3 specifically) restructured from subheaded form to bare list form so list-item count = 8 still triggers the out-of-range error; over1 / over_appx restructured to bare list form so subhead-cluster mode does not mask the original Control Questions test.

- **B3 deferral.** Re-running the calibrated validator against the four canonical fixtures (B3 in the Phase 7 plan) is deferred to Wave 2 — Wave 1 lands the calibration; Wave 2 confirms F1-F4 produce expected results post-calibration. The Phase 7 plan §Wave 2 sequencing (B3 depends on A1) is honored.

#### A2 — Optional validators batch (`audit-tier-criterion` + `argument-recon-prerequisite`)

Two of the three optional validators identified in v1.7.9 §Out of scope and the Phase 7 plan §A2 ship in Wave 1. The third (`audit-signal-propagation §4e context-modifier extension`) is deferred to a later Phase 7 wave per scope-control. Validator total: 9 → 11.

- **`audit-tier-criterion` (new validator, ~250 lines).** Verifies audit tier assignments in `pass-dependencies.md §4a/§4b` against the §4c Audit Tier Promotion Criteria (Phase 6 Wave 2). Mechanically verifies criterion 1 (named hard gates / Must-Fix floor) by scanning each high-tier audit's reference file for `hard[ -]?gate` or `must-?fix[ -]?floor` patterns. Audits at Hard Prerequisite / Pre-DE Prerequisite / Auto-run / Auto-recommend before synthesis tiers without criterion-1 language are surfaced as candidates for tier review. Recommend / Auto-recommend tiers are exempt. **Capability ceiling documented:** criteria 2 (undetectable-by-passes) and 3 (disclosure-non-equivalence) require model judgment about the manuscript / fixture corpus and remain in the §4a/§4b verification subsection prose. Per-audit override marker: `<!-- override: audit-tier-criterion-<audit-slug> --> `. Self-test: 4 cases (pos, neg, over, edge — Recommend tier exempt).

- **`argument-recon-prerequisite` (new validator, ~190 lines).** Verifies argument-shaped runs satisfy the Field Reconnaissance prerequisite per `pass-dependencies.md §4a` (Hard Prerequisite or Auto-recommend before synthesis tier) and v1.7.9's wired execution-flow Pre-Pass Prerequisite Resolution step. Detects argument-engine artifacts (Argument_State.md, Red_Team_Memo.md, Argument_Evidence.md, Argument_Persuasion.md, Adversarial_Evidence.md) by filename pattern in the run folder, plus editorial-letter mentions of Dialectical Clarity / Argument Red Team / Argument Evidence Deep-Dive / argument-engine pass output. When argument-engine present, requires either (a) `Field_Reconnaissance_Report.md` in the run folder, OR (b) the canonical blind-spot disclosure ("literature-counterevidence not surveyed") in the editorial letter per `run-synthesis.md §Step 3` (Phase 6 Wave 3 / CR-4). Silent omission is forbidden at the Hard Prerequisite tier per the canonical decline policy. Body-only override marker: `<!-- override: argument-recon-prerequisite -->`. Self-test: 5 cases (pos1 — argument-engine + Field Recon; pos2 — argument-engine + canonical disclosure; pos3 — fiction run exempt; neg — silent omission caught; over — override marker downgrades).

- **Deferred from A2 batch:** `audit-signal-propagation §4e context-modifier extension` (per-audit table-driven dispatch reading §4e programmatically). Listed in Phase 7 plan as one of three A2 items; deferred to a later wave to keep Wave 1 scope bounded. v1.7.9's audit-signal-propagation default mapping continues to handle the verification.

#### D1 — v1.7.1 changelog backfill

The v1.7.1 release ("underdiagnosis hardening") shipped 2026-04-23 without a changelog entry — flagged in Phase 4 Wave 1 as a deferred hygiene item. Wave 1 of Phase 7 backfills the entry between v1.7.0 and v1.7.2 with explicit non-contemporaneous note. Cites originating commits `cfaadef` (underdiagnosis hardening), `7bb9c34` (Deficit-First extension to 5 craft audits), `9cd8948` (release.sh build-antigravity step), and version-bump commit `6b477d5`. See v1.7.1 entry below for full content.

#### Files

- `plugins/apodictic/scripts/validate.sh` — `decision-layer-check` calibrated for C1-C4 with extended self-test (~+330 lines net: doc-comment expansion, three-tier counting helper with subhead-cluster + paragraph-form fallbacks, argument-DE class detection, paragraph-block evidence-density window, four new self-test fixtures); two new validators added (`audit-tier-criterion` ~250 lines including self-test; `argument-recon-prerequisite` ~190 lines including self-test); top-of-file usage doc-comments extended for both new validators; usage help text updated. Net ~+750 lines.
- `scripts/validate.sh` — synced with plugin copy (canonical lives at `plugins/apodictic/scripts/validate.sh`; root copy is the user-facing alias).
- `plugins/apodictic/skills/specialized-audits/SKILL.md` — added Field Reconnaissance prerequisite paragraph in How to Use section pointing to `argument-recon-prerequisite` validator (~+3 lines).
- `plugins/apodictic/skills/core-editor/references/changelog.md` — v1.8.0 entry; v1.7.1 backfill entry between v1.7.0 and v1.7.2.
- Version bumped via `scripts/bump-version.sh 1.8.0`.
- Generated host workspaces (codex, antigravity) regenerated via release pipeline.

Total prose change: ~3 lines added (SKILL.md). Total validator change: ~+750 lines in `validate.sh`. All 11 validator self-tests PASS. All 4 release checks PASS.

#### Self-test verification (v1.8.0)

| Validator | Cases (was → now) | New coverage |
|---|---|---|
| `severity-floor` | 7 | Unaffected |
| `audit-signal-propagation` | 9 | Unaffected |
| `underdiagnosis-triggers` | 5 | Unaffected |
| `ledger-consolidation` | 5 | Unaffected |
| `decision-layer-check` | 7 → 11 | C1 (subhead clusters), C2 (paragraph form), C3 (argument-DE class), C4 (paragraph-block evidence window) |
| `quality-risk-triggers` | 12 | Unaffected |
| `timeline-diff` | 8 | Unaffected |
| `timeline-arithmetic` | 6 | Unaffected |
| `timeline-anchor-conflict` | 6 | Unaffected |
| `audit-tier-criterion` | 0 → 4 | NEW — pos / neg / over / edge (Recommend-tier exempt) |
| `argument-recon-prerequisite` | 0 → 5 | NEW — pos1 (Field Recon present) / pos2 (canonical disclosure) / pos3 (fiction exempt) / neg (silent omission) / over |

#### Out of scope (deferred Phase 7 work)

- **B3 — decision-layer-check re-eval against canonical fixtures (F1-F4).** Wave 2 work per Phase 7 plan §Wave 2 sequencing.
- **`audit-signal-propagation §4e context-modifier extension`.** Third A2 validator deferred to a later Phase 7 wave; v1.7.9 default mapping continues to handle propagation verification.
- **A3 Python-helper-based true Timeline parsing.** Recommended out of scope for the model-capability review cycle per Phase 7 plan §A3; added to ROADMAP.md as future Python tooling cycle candidate.

---

## v1.7.9 - 2026-04-25

### Fixed — Honest Validator Capability Correction + Execution-Flow Prerequisite Wiring

Closes five review findings on the v1.7.8 framework state (Joshua's substantive code review). Four validators overclaimed what they actually verified; the new Hard Prerequisite tier policy from Phase 6 Wave 3 wasn't wired into the `run-core.md` execution flow. v1.7.9 ships the coordinated correction: one validator tightened to actually do per-audit, per-signal propagation verification; one validator extended to cover Section 3 marker inventory and to count-match Section 8 documentation; two validators reframed honestly as marker-hygiene / pre-labeled-conflict-surfacing checks with Phase 7 deferral noted for true verification; one execution-protocol step added to wire Hard Prerequisite resolution before pass dispatch. No commits, no behavior regression for Phase 4-6 work that was already correct.

#### Finding 1 — `audit-signal-propagation` overclaim (P1, tightened)

The Phase 4-6 validator only checked the whole letter for severity-vocabulary presence (any "Must-Fix" anywhere in body satisfied any audit's hard-gate signal in any appendix). A letter with an unrelated Decision Pressure Must-Fix in the body and a Reception Risk hard gate buried in Appendix A passed. The `run-synthesis.md §Step 2` prose promised per-signal §4e-table-driven verification; the implementation didn't do this.

- **`plugins/apodictic/scripts/validate.sh` `audit-signal-propagation`** — substantial rewrite (~+200 lines net). The validator now: (a) detects each audit appendix subsection by name (`<Audit Name> Audit` heading or in-appendix prose mention); (b) for each detected audit, identifies its severity signals (hard-gate, Must-Fix floor, HIGH/Alert) within that audit's subsection; (c) for each signal, verifies the synthesis body's Must-Fix or Should-Fix list contains either an explicit audit-name reference (e.g., "Reception Risk Alert at L2956") OR a finding tied to evidence-line numbers shared with the audit's appendix subsection. Per-class override markers (`audit-propagation-hard-gate`, etc.) preserved; new per-audit override marker form added (`audit-propagation-<audit-slug>`) for principled single-audit deviations. Body-only marker invariant preserved. Self-test extended from 6 cases to 9 cases including Joshua's canonical false-pass case (`neg1b`) — letter with unrelated Decision Pressure Must-Fix in body and Reception Risk hard gate in Appendix A — which now correctly FAILS where Phase 4-6 PASSED. Falls back to legacy whole-letter taxonomy check when no audit appendix subsections are detected (preserves Phase 4 behavior for letters that mention severity vocabulary without dedicated audit appendices).

- **`plugins/apodictic/skills/core-editor/references/run-synthesis.md` §Step 2** — Canonical Audit-Signal Propagation Rule prose tightened to honestly describe what the validator verifies (per-audit, per-signal; audit-name reference OR shared evidence-line; not generic Must-Fix presence). New per-audit override marker form documented.

#### Finding 2 — `timeline-diff` Section 3 + Section 8 count-match (P1, extended)

The Phase 4-6 validator only extracted Section 1 Event Ledger pipe-table rows. Section 3 (Temporal Marker Inventory) bullet items, Section 2 calendar shifts, Section 4 paradoxes, and Section 8 prose-only documentation all went uncovered. Section 8 documentation was accepted on keyword presence alone (any "Added" / "Removed" / "Changed" satisfied any structural delta).

- **`plugins/apodictic/scripts/validate.sh` `timeline-diff`** — extended (~+50 lines net). The validator now: (a) continues extracting Section 1 pipe-table rows (preserved Phase 4-6 behavior); (b) ALSO extracts Section 3 bullet items (`- ...` lines under the Section 3 heading) and diffs them; (c) when Section 8 contains bullet-form documentation (`- Added: ...`, `- Removed: ...`), counts those bullets and requires them to cover the structural totals across Section 1 + Section 3 (count-match, not just keyword-presence). Sections 2 (Master Calendar) and 4 (Inconsistency Ledger) are documented as freeform prose deferred to Phase 7 item-level diffing — diffed at section-presence level only by the bash validator. Self-test extended to 8 cases including a Section-3-only change (Phase 4-6 missed; v1.7.9 catches) and a count-mismatch case (Section 8 documents 1 added when structural diff shows 3 added).

- **`plugins/apodictic/skills/core-editor/references/pass-10.md` §Validator Integration** — `timeline-diff` description updated to reflect the actual Section 1 + Section 3 + Section 8 count-match behavior.

#### Finding 3 — `timeline-arithmetic` honest reframing (P1, reframed)

Real arithmetic checks need date-format parsing across heterogeneous anchor formats (`Day 1 morning`, `the following Friday`, `January 14`) plus span normalization plus pairwise compatibility reasoning — not feasible in bash. The Phase 4-6 validator only grepped for negative-gap text or pre-written conflict markers, but the `--help` text and the `pass-10.md` description claimed it verified span calculations. Real arithmetic violations passed.

- **`plugins/apodictic/scripts/validate.sh` `timeline-arithmetic`** — reframed (~+25 lines net, no semantic change to detection). Doc-comment, OK/WARN/ERROR messages, and self-test descriptions updated to honestly describe the validator as "marker hygiene only" with "true arithmetic verification deferred to a Phase 7 Python helper." Self-test extended with a `silent_arithmetic` case that documents the Phase 7 limitation (the case passes with an explicit comment that bash cannot detect it). Validator command name preserved (no integration breakage).

- **`plugins/apodictic/skills/core-editor/references/pass-10.md` §Validator Integration** — `timeline-arithmetic` description updated to match validator's honest semantics.

#### Finding 4 — `timeline-anchor-conflict` honest reframing (P1, reframed)

Same pattern as Finding 3. The Phase 4-6 validator only counted parenthetical `(contradicts ...)` annotations — i.e., only caught conflicts the Pass 10 model had already pre-labeled. The `--help` text and `pass-10.md` claimed it identified pairs of explicit temporal markers that cannot both be true. Same Ch 1 §1 with both "Monday morning" and "Tuesday morning" passed unless the model pre-labeled it.

- **`plugins/apodictic/scripts/validate.sh` `timeline-anchor-conflict`** — reframed (~+25 lines net, no semantic change to detection). Doc-comment, OK/WARN/ERROR messages, and self-test descriptions updated to "pre-labeled-conflict surfacing only" with "true anchor parsing deferred to a Phase 7 Python helper." Self-test extended with a `silent_anchor` case (same scene with two different anchors, no parenthetical pre-labeling) that documents the Phase 7 limitation. Validator command name preserved.

- **`plugins/apodictic/skills/core-editor/references/pass-10.md` §Validator Integration** — `timeline-anchor-conflict` description updated to match validator's honest semantics.

#### Finding 5 — Hard Prerequisite tier wired into `run-core.md` execution flow (P2, wired)

Phase 6 Wave 3 added `Hard Prerequisite` and `Pre-DE Prerequisite` tiers in `pass-dependencies.md §4a/§4c/§4f` (Field Reconnaissance and Citation Verifier for high-stakes argument-shaped runs). The tier definitions named the obligation ("Field Recon MUST complete before any Tier 2 evaluative pass") but `run-core.md`'s execution protocol jumped from pass resolution directly to pass dispatch with no prerequisite resolution step. The policy was documented but not executable.

- **`plugins/apodictic/skills/core-editor/references/run-core.md` §Audit Activation at Contract** — paragraph extended (~3 lines) to call out Hard Prerequisite and Pre-DE Prerequisite tiers as exceptions to the "audits run after core passes" baseline, with cross-reference to `pass-dependencies.md §4a/§4c/§4f`.

- **`plugins/apodictic/skills/core-editor/references/run-core.md` §Execution Protocol** — new step 6 (`Pre-Pass Prerequisite Resolution`) added before pass dispatch (~12 lines). The step walks `pass-dependencies.md §4a` for Hard Prerequisite and Pre-DE Prerequisite audits given the resolved contract, dispatches them in the correct order (Pre-DE first, Hard before Tier 2), handles the decline path per `pass-dependencies.md §4c` + §4f edge cases 8-9 (terminate or downgrade-with-disclosure; silent omission forbidden), records resolution in the Audit Invocation Log, and honors the §4f tier precedence invariant. Subsequent dispatch steps renumbered (single-agent: step 7-8; multi-agent: steps 7-10) to inherit Pre-Pass Prerequisite outputs as analytical context alongside the contract.

#### Files

- `plugins/apodictic/scripts/validate.sh` — `audit-signal-propagation` rewritten for per-audit per-signal verification (~+200 lines); `timeline-diff` extended to Section 3 + Section 8 count-match (~+50 lines); `timeline-arithmetic` reframed as marker hygiene with Phase 7 deferral (~+25 lines); `timeline-anchor-conflict` reframed as pre-labeled surfacing with Phase 7 deferral (~+25 lines); top-of-file usage doc-comments updated. Net ~+300 lines.
- `scripts/validate.sh` — synced with plugin copy (canonical lives at `plugins/apodictic/scripts/validate.sh`; root copy is the user-facing alias).
- `plugins/apodictic/skills/core-editor/references/run-core.md` — Audit Activation at Contract paragraph extended (~3 lines); new §Execution Protocol step 6 (Pre-Pass Prerequisite Resolution) with subsequent steps renumbered (~+12 lines). Net ~+15 lines.
- `plugins/apodictic/skills/core-editor/references/run-synthesis.md` — §Step 2 Canonical Audit-Signal Propagation Rule prose tightened to honestly describe per-audit per-signal verification (~+5 lines); per-audit override marker form documented (~+8 lines). Net ~+13 lines.
- `plugins/apodictic/skills/core-editor/references/pass-10.md` — §Validator Integration descriptions rewritten to honestly state validator capabilities (Section 1 + Section 3 + count-match for `timeline-diff`; marker hygiene only for `timeline-arithmetic`; pre-labeled surfacing only for `timeline-anchor-conflict`); new §Phase 7 Work Items section (~+30 lines) listing the Python helper work items with a framework-design lesson on bash validator ceiling. Net ~+50 lines.
- Version bumped via `scripts/bump-version.sh 1.7.9`.
- Generated host workspaces (codex, antigravity) regenerated via release pipeline; APODICTIC-Gemini public mirror synced.

Total prose change: ~78 lines added across framework files. Total validator change: ~+300 lines in `validate.sh`. All 9 validator self-tests PASS. All 4 release checks PASS.

#### Self-test verification (v1.7.9)

| Validator | Cases (was → now) | Joshua's false-pass case |
|---|---|---|
| `severity-floor` | 7 | Unaffected |
| `audit-signal-propagation` | 6 → 9 | `neg1b` (unrelated Must-Fix in body + Reception Risk hard gate in appendix) — was PASS, now FAIL |
| `underdiagnosis-triggers` | 5 | Unaffected (delegates to audit-signal-propagation; tighter delegate behavior preserved) |
| `ledger-consolidation` | 5 | Unaffected |
| `decision-layer-check` | 8 | Unaffected |
| `quality-risk-triggers` | 12 | Unaffected |
| `timeline-diff` | 5 → 8 | `s3_neg` (Section 3 marker change undocumented), `count_mismatch` (Section 8 documents 1 of 3 added) — was PASS, now FAIL |
| `timeline-arithmetic` | 5 → 6 | `silent_arithmetic` documents Phase 7 limitation (still passes; honest about ceiling) |
| `timeline-anchor-conflict` | 5 → 6 | `silent_anchor` documents Phase 7 limitation (still passes; honest about ceiling) |

#### Framework-design lesson (logged in `pass-10.md §Phase 7 Work Items`)

Bash validators have a real ceiling. Bash is excellent for structural and pattern-presence checks (heading inventory, table-row diff, marker keyword surfacing, count matching) but cannot do parsing, normalization, or reasoning over heterogeneous formats (date math across `Day N` / `Monday morning` / `January 14`; cross-format span normalization; pairwise compatibility reasoning). Phase 4-6 validator work mixed the two by *claiming* parsing capability in bash validators that only did keyword grepping — producing validators that overclaimed and false-passed on the cases that most matter. v1.7.9's correction: each validator's `--help` text, doc-comment, OK/ERROR messages, and the framework prose that describes them now match what the validator actually does. Future validator work should choose the implementation tool to match the verification kind needed, and document the ceiling explicitly when bash is the right tool for part of the job.

#### Out of scope (Phase 7 candidates, documented in `pass-10.md §Phase 7 Work Items`)

- Python-based Timeline parser (Section 1 + Section 3 normalized scene records; anchor-format normalization; span normalization).
- True arithmetic verification (replaces `timeline-arithmetic` marker-hygiene).
- True anchor conflict detection (replaces `timeline-anchor-conflict` pre-labeled surfacing).
- Item-level diff for Sections 2 (Master Calendar) and 4 (Inconsistency Ledger).
- Per-audit table-driven dispatch in `audit-signal-propagation` (currently the validator detects audit names by appendix-heading pattern; a Phase 7 enhancement would read `pass-dependencies.md §4e` programmatically and apply per-audit context modifiers).

---

## v1.7.8 - 2026-04-25

### Added — Phase 6 Wave 3: Field Reconnaissance Prerequisite for Argument-Shaped Runs (CR-4) + Universal Audit Re-Audit

Closes Phase 6 Wave 3 of the model-capability review (see `docs/review-log/2026-04-25_phase-6-implementation-plan.md` Wave 3 = Priorities 2 + 5). With Wave 3, all six Phase 6 priorities are closed and Phase 6 is complete.

#### Priority 2 — Field Reconnaissance Prerequisite (CR-4 closed)

Closes the literature-counterevidence blind spot identified in TAY Stage 2 (`docs/review-log/2026-04-24_tay-stage-2-comparative.md`). Stage 2 documented seven literature-counterevidence misses where competing studies, replication failures, meta-analytic disagreement, and opposing scholarly positions never entered the Findings Ledger because Field Reconnaissance was not prerequisited for argument-shaped runs. Wave 3 establishes Field Recon as a prerequisite (Hard or Auto-recommend before synthesis depending on stakes signal) and Citation Verifier as a Pre-DE Prerequisite for high-stakes argument-shaped runs.

- **`core-editor/references/pass-dependencies.md` §4a** — added two new router-triggered audit rows (Field Reconnaissance and Citation Verifier) with explicit argument-shaped routing definition, high-stakes signal definition, and a why-prerequisite-tier-exists prose block citing TAY Stage 2 evidence (~25 lines).

- **`core-editor/references/pass-dependencies.md` §4c** — added two new tier definitions above the existing four: **Hard Prerequisite** (stronger than Auto-run; gates Tier 2 passes rather than synthesis; used for Field Recon on high-stakes argument-shaped runs) and **Pre-DE Prerequisite** (audit runs before the DE begins; not a DE-internal audit; used for Citation Verifier on high-stakes argument-shaped runs). Both definitions include explicit decline-path semantics (terminate or downgrade-with-disclosure; silent omission forbidden). The header sentence updated to reflect the six-tier ordering. ~10 lines added.

- **`core-editor/references/pass-dependencies.md` §4f** — tier-ordering block extended from four tiers to six (Hard Prerequisite > Pre-DE Prerequisite > Auto-run > Auto-recommend before synthesis > Auto-recommend > Recommend). Added a Hard Prerequisite ordering note explaining why these tiers sit above Auto-run (pass dependencies vs. synthesis dependencies). Added two new edge cases (8 + 9) covering Hard Prerequisite and Pre-DE Prerequisite decline forks. ~12 lines added.

- **`specialized-audits/references/craft/research-field-recon.md`** — added Prerequisite Mode for Argument-Shaped Runs section after Core principle paragraph (~50 lines). Documents two prerequisite tiers (Hard Prerequisite when high-stakes signal present; Auto-recommend before synthesis otherwise), the four-class literature-counterevidence focus (competing studies / counter-citations / replication failures / opposing scholarly positions), the canonical artifact (`Field_Reconnaissance_Report.md`) and how the argument-engine passes (Dialectical Clarity / Argument Red Team / Argument Evidence Deep-Dive / Synthesis) consume it, the decline path (terminate or downgrade-with-disclosure), and when Wave-2-sibling mode still applies (fiction, narrative nonfiction, memoir, re-invocations).

- **`specialized-audits/references/craft/research-citation-verifier.md`** — added Pre-DE Prerequisite Mode subsection inside §Activation (~25 lines). Documents the Pre-DE Prerequisite tier semantics (runs before any Tier 1 pass; produces `Citation_Ledger.md` consumed by argument-engine passes; not a DE-internal audit), the rationale (citation integrity is an evidentiary precondition for argument analysis, not a finding within it), the decline path (terminate or downgrade-with-disclosure naming "citation provenance not verified"), and the lower-stakes case (Citation Verifier remains available via existing activation paths and direct `/research citation-verifier`).

- **`core-editor/references/run-synthesis.md`** — added a mandatory blind-spot disclosure paragraph inside Step 3 (Blind Spot / Absence Inventory) covering declined Field Reconnaissance on argument-shaped runs (~6 lines). The disclosure must name what is unsurveyed (competing studies, counter-citations, replication failures, opposing scholarly positions) and what the absence implies for synthesis confidence (the argument engine operated against a manuscript-internal claim graph rather than a literature-aware one). Parallel disclosure rule for declined Pre-DE Citation Verifier on high-stakes runs. Appendix A description extended to require the disclosure in editorial-letter Diagnostic Detail (~3 lines).

#### Priority 5 — Universal Audit Re-Audit (Outcome A: keep universal)

Phase 3 inventory classified Stakes / Decision Pressure / Scene Turn as UNPROVEN-keep universal, with Phase 6 instructed to re-audit against fixture data. Wave 3 verifies and ratifies universal status.

- **`specialized-audits/SKILL.md` §Universal Audits** — added Universal-status criterion (~2 lines: three-criterion definition matching the §4c Audit Tier Promotion Criteria pattern from Wave 2) and Universal status verification block dated 2026-04-25 (~8 lines: cross-model parity from Phase 3 §17; cross-fixture material findings on Regrets Only / Dinner Party / TAY; computational-cost reasoning; demotion candidates considered and rejected — Scene Turn for argument-shaped runs was the closest demotion candidate, rejected because the audit self-attenuates on propositional material without producing false positives). Each of the three universal-audit table rows updated to reference verification status with date and fixture set. ~15 lines net.

- **`specialized-audits/references/craft/stakes-system.md`** — added Universal status verification line in frontmatter under audit classification (~2 lines).

- **`specialized-audits/references/craft/decision-pressure.md`** — added Universal status verification line in frontmatter under audit classification, with explicit note that the audit applies fully to argument-shaped runs (~2 lines).

- **`specialized-audits/references/craft/scene-turn.md`** — added Universal status verification line in frontmatter under audit classification, with explicit note about self-attenuation on purely propositional argument-shaped sections (~2 lines).

Outcome A (keep universal) chosen over Outcome B (demote to baseline-recommend with explicit opt-out). Verification basis: cross-model parity (Phase 3 §17 — both Opus and Codex correctly fire all three on parity sets); cross-fixture material findings on Regrets Only / Dinner Party / TAY; computational cost is low because the audits run inside the same context as their finding-trigger passes (Pass 1 / Pass 5 / Pass 7); the convergence-trigger contribution to the underdiagnosis-retry loop is material. No demotions or tier changes; universal status holds.

#### Files

- `plugins/apodictic/skills/core-editor/references/pass-dependencies.md` — §4a Field Recon + Citation Verifier router rows with argument-shaped routing definition, high-stakes signal definition, and CR-4 closure rationale (~25 lines); §4c Hard Prerequisite + Pre-DE Prerequisite tier definitions with header sentence updated to six-tier ordering (~10 lines); §4f tier-ordering block extended to six tiers, Hard Prerequisite ordering note, edge cases 8 and 9 (~12 lines). Net ~+47 lines.
- `plugins/apodictic/skills/core-editor/references/run-synthesis.md` — Step 3 Blind Spot / Absence Inventory mandatory disclosure paragraph for declined Field Recon on argument-shaped runs and parallel rule for Pre-DE Citation Verifier (~6 lines); Appendix A description extension naming literature-counterevidence and citation-provenance blind spots (~3 lines). Net ~+9 lines.
- `plugins/apodictic/skills/specialized-audits/SKILL.md` — Universal-status criterion + verification block + updated table rows for the three universal audits (~15 lines net).
- `plugins/apodictic/skills/specialized-audits/references/craft/research-field-recon.md` — new Prerequisite Mode for Argument-Shaped Runs section between Core principle and Part 1 (~50 lines).
- `plugins/apodictic/skills/specialized-audits/references/craft/research-citation-verifier.md` — new Pre-DE Prerequisite Mode subsection inside §Activation (~25 lines).
- `plugins/apodictic/skills/specialized-audits/references/craft/stakes-system.md` — Universal status verification line in frontmatter (~2 lines).
- `plugins/apodictic/skills/specialized-audits/references/craft/decision-pressure.md` — Universal status verification line in frontmatter (~2 lines).
- `plugins/apodictic/skills/specialized-audits/references/craft/scene-turn.md` — Universal status verification line in frontmatter (~2 lines).
- Version bumped via `scripts/bump-version.sh 1.7.8` (Wave 2 may bump to 1.7.7 in coordination; Wave 3 ships as 1.7.8).

Total prose change: ~152 lines added across framework files. No validators added (existing `audit-signal-propagation` validator covers post-Field-Recon propagation; activation policy is documented contract). No fixture changes (Field Recon prerequisite would have surfaced TAY Stage 2 blind spots had it been in place; verification by trace analysis per Phase 6 plan §Priority 2 acceptance criterion 6).

#### Out of scope (Phase 7 candidates)

- Optional `validate.sh argument-recon-prerequisite <intake_file> <audit_invocation_log>` validator that would verify, for argument-shaped intake, either Field Recon ran or a blind-spot disclosure exists in the synthesis. Deferred to Phase 7.
- Pass 10 Timeline cross-fixture eval coverage (still deferred from Wave 1).
- Cross-model fixture re-evaluation against the §4e propagation table (Wave 2 territory; Wave 3 does not affect this).

#### Phase 6 closure

Wave 3 closes the final two priorities. All six Phase 6 priorities are now complete:

- **Wave 1 (v1.7.6):** Priority 1 (CR-5 Pass 10 Timeline) + Priority 6 (CR-7 Audit Tier Precedence Rule).
- **Wave 2 (v1.7.7):** Priority 3 (CR-8 Audit-Signal Propagation Table) + Priority 4 (CR-3 Auto-recommend tier re-audit + Priority Queue).
- **Wave 3 (v1.7.8):** Priority 2 (CR-4 Field Reconnaissance Prerequisite) + Priority 5 (Universal Audit Re-Audit).

Phase 6 is closed. All four Codex critique items (CR-3, CR-4, CR-5, CR-7, CR-8) plus the Phase 3 Universal Audit re-audit are resolved.

---

## v1.7.7 - 2026-04-25

### Added — Phase 6 Wave 2: Audit-Signal Propagation Table (CR-8 operationalized) + Auto-Recommend Tier Re-Audit + Priority Queue (CR-3 closed)

Closes Phase 6 Wave 2 of the model-capability review (see `docs/review-log/2026-04-25_phase-6-implementation-plan.md` Wave 2 = Priorities 3 + 4, `docs/review-log/2026-04-24_phase-2-archaeology.md` for CR-3 promotion-drift evidence, `docs/review-log/2026-04-25_phase-3-codex-critique-adjudication.md` §3 + §6 for CR-8 evidence, and Phase 4's canonical Audit-Signal Propagation Rule in `core-editor/references/run-synthesis.md §Step 2` which Wave 2 operationalizes per-audit). Wave 2 ships alongside Wave 3 (v1.7.8); both edit `pass-dependencies.md §4` and were coordinated in parallel. Version files were already bumped to 1.7.8 by Wave 3; the v1.7.7 entry here documents the Wave 2 changes for changelog continuity.

#### Priority 3 — Audit-Signal Propagation Table (CR-8 operationalized)

Phase 4 established the canonical Audit-Signal Propagation Rule (`run-synthesis.md §Step 2`) that defines the propagation taxonomy (Must-Fix floor → synthesis Must-Fix; hard gate → synthesis Must-Fix; HIGH → synthesis Must-Fix or Should-Fix per audit context; MEDIUM → Should-Fix; LOW → Could-Fix). Wave 2 builds the per-audit table the rule defers to.

- **`core-editor/references/pass-dependencies.md` §4e — Audit-Signal Propagation Table** — new section between §4d and §4f (~140 lines). Six subsections covering Universal audits (Stakes / Decision Pressure / Scene Turn), High-priority craft audits (Compression / Reception Risk / Banister / AI-Prose / Female Interiority / Interiority Preservation), Argument cluster (Dialectical Clarity / Red Team / Persuasion / Evidence / Adversarial Evidence Review / Field Recon / Citation Verifier), Specialized craft audits (Character Architecture / Emotional Craft / Literary Craft / Force Architecture / Series Continuity / Series Composite Novel / Shelf Positioning / Short Fiction), Genre audits (Comedy/Satire / Historical / Memoir/CNF / Narrative NF / Fan Fiction / SFF Worldbuilding / Horror / Supernatural Horror / Grimdark / Mystery-Thriller), and Tag audits (Consent Complexity / Erotic Content / Queer Romance / Cozy / Philosophical). Approximately 95 rows total; each row maps one audit-internal signal class to one synthesis severity, with explicit context modifier and source-file reference. Includes prologue explaining how to read each row, validator integration with Phase 4's `audit-signal-propagation`, override-path reminder, and footer with default mapping (canonical rule's column-2 fallback) for un-enumerated audits.

- **CR-8 closure cases enumerated explicitly** in §4e: Compression Must-Fix floor → synthesis Must-Fix (always; primary CR-8 case); Reception Risk Alert post-calibration → synthesis Must-Fix (when not artifact-of-method); Reception Risk coercion-marked Alert → synthesis Must-Fix + retry-loop trigger #2 (refines default per cross-step trigger); Banister HIGH-confidence rhetorical-fairness failure → synthesis Must-Fix when thematic-coherence-load is high (refines default per Codex §9.4 closure). Each closure case carries explicit context modifiers and Override column annotations.

- **`core-editor/references/run-synthesis.md` §Step 2** — "Per-audit specifics live elsewhere" sentence updated. Old text pointed to "Phase 6 work" with "until that table exists, treat the column-2 mapping above as the default." New text points to `pass-dependencies.md §4e`, names the validator, and clarifies that un-enumerated audits fall back to the column-2 default (so the canonical rule still governs un-enumerated audits via the default). +1 line net.

- **`core-editor/references/pass-dependencies.md` §4 header** — "Audit-signal propagation" paragraph updated to point to §4e instead of "Phase 6 work." +0 lines net (sentence rewrite).

- **`specialized-audits/SKILL.md` §How to Use** — existing "Severity signals from audits propagate" paragraph extended with a one-sentence pointer to `pass-dependencies.md §4e` and audit-author guidance ("add a §4e row at registration time; un-enumerated audits fall back to the canonical default mapping"). +1 sentence.

No new validator. The existing Phase 4 `audit-signal-propagation` validator covers the new table without modification; it reads §4e's per-audit context modifiers as refinements to the canonical default. Validator extension to read context modifiers programmatically is deferred to Phase 7.

#### Priority 4 — Auto-Recommend Tier Re-Audit + Priority Queue (CR-3 closed)

Phase 2 archaeology surfaced cfaadef's batch promotion of five audits (Compression / Female Interiority / Scene Turn / Interiority Preservation / Decision Pressure) from Recommend to Auto-recommend before synthesis without an explicit promotion criterion. Wave 2 closes the criterion gap and verifies all existing tier assignments.

- **`core-editor/references/pass-dependencies.md` §4a Router-triggered audits** — added Tier verification subsection at the top of §4a (~3 lines). Result: existing tiers hold. Auto-recommend before synthesis tier on Reception Risk and Consent Complexity confirmed against Phase 2 archaeology (the obligation tier's defining condition — absent these audits, the run records explicit blind spots — is met). Auto-run audits (Constraint=ai → AI-Prose; Erotic Content; Memoir; Narrative NF) confirmed against §4c Auto-run definition. No router-tier promotions or demotions.

- **`core-editor/references/pass-dependencies.md` §4b Finding-triggered audits** — added Tier verification subsection at the top of §4b (~5 lines). Result: existing tiers hold. The five cfaadef-promoted audits (Compression / Female Interiority / Scene Turn / Interiority Preservation / Decision Pressure) verified against the new §4c Audit Tier Promotion Criteria — promotions justified. Demotion candidates considered and rejected: each catches undetectable-by-passes-alone omissions; blind-spot disclosure is non-equivalent to running them. Recommend tier on Character Architecture / Emotional Craft / Banister and others remains: each catches a class of issue that *could* be inferred from passes, so opt-in is the right tier. Banister-for-thematic-runs candidate flagged in Phase 3 documented in §4e propagation entry but tier stays at Recommend pending stronger Phase 7 evidence.

- **`core-editor/references/pass-dependencies.md` §4c — new Audit Tier Promotion Criteria subsection** (~16 lines). Documents the three-criterion test for Auto-recommend before synthesis status: (1) audit has named hard gates or audit-internal Must-Fix floors; (2) audit catches a class of issue undetectable by passes alone; (3) blind-spot disclosure is non-equivalent to running the audit. Documents the Auto-run derivation (all three above + definitional-or-prerequisite-signal); Auto-recommend derivation (criterion 1 + partial criterion 2, criterion 3 fails). Establishes the logging requirement: each promotion (or principled non-promotion) recorded in the changelog entry that introduces it. The §4a/§4b verification subsections at the start of each table document the criterion's application to existing audits.

- **`core-editor/references/pass-dependencies.md` §4d — Presentation format & Priority Queue** — section title updated; section restructured to add explicit Priority Queue specification (~30 lines). Four ordering rules in sequence: (1) higher tier fires first; (2) within tier, higher audit-internal severity fires first (hard gate beats Must-Fix floor beats HIGH/Alert beats MEDIUM/Flag beats LOW/Note); (3) within severity, higher signal count fires first; (4) tie-breaking alphabetical by audit name. Re-prompt suppression rule cross-references §4f (CR-7); tier resolution precedes queue ordering. Three worked examples illustrating: same-tier different-internal-severity (Female Interiority vs Scene Turn after Pass 5); two Auto-recommend-before-synthesis audits at different signal classes (Reception Risk Alert vs Compression Must-Fix floor after Pass 1); two Recommend audits with different signal counts (Dialectical Clarity vs Banister after Pass 9).

#### Files

- `plugins/apodictic/skills/core-editor/references/pass-dependencies.md` — §4 header propagation paragraph rewrite (0 net); §4a verification subsection (~3 lines); §4b verification subsection (~5 lines); §4c Audit Tier Promotion Criteria subsection (~16 lines); §4d Priority Queue + worked examples (~30 lines); §4e Audit-Signal Propagation Table (~140 lines, ~95 audit rows). Net ~+194 lines.
- `plugins/apodictic/skills/core-editor/references/run-synthesis.md` — §Step 2 "Per-audit specifics live elsewhere" sentence rewrite (+1 line net).
- `plugins/apodictic/skills/specialized-audits/SKILL.md` — §How to Use propagation paragraph extended with §4e pointer + audit-author guidance (+1 sentence).
- Version files — already bumped 1.7.6 → 1.7.8 by Wave 3 in parallel; Wave 2's nominal v1.7.7 slot is documented here without re-bumping (Wave 2 + Wave 3 share a same-day release window).

Total prose change: ~196 lines added across framework files. No validators added (existing `audit-signal-propagation` from Phase 4 covers the table without modification). No fixture changes (CR-3 closure is documentation; CR-8 operationalization is documentation; the validator behavior on Regrets Only Opus / Codex / TAY / Dinner Party fixtures from Phase 4 Wave 3 is unchanged — §4e refines per-audit defaults but the canonical rule still applies for un-enumerated audits).

#### Out of scope (Phase 7 candidates)

- Optional `audit-signal-propagation` validator extension to read per-audit context modifiers from §4e and check audit-context propagation programmatically. Defer to Phase 7.
- Optional `validate.sh audit-tier-criterion <audit_invocation_log>` validator to verify every audit's promotion-criterion satisfaction is logged. Defer to Phase 7.
- Cross-model fixture re-evaluation against §4e: Codex's documented under-propagation of Compression / Reception / Banister signals (per Codex critique adjudication §3) would now be surfaced as validator failures under §4e. Re-running the cross-model fixtures to confirm is downstream eval work, not Wave 2 scope.

---

## v1.7.6 - 2026-04-25

### Added — Phase 6 Wave 1: Pass 10 Timeline Enhancement (CR-5) + Audit Tier Precedence Rule (CR-7)

Closes Phase 6 Wave 1 of the model-capability review (see `docs/review-log/2026-04-25_phase-6-implementation-plan.md` Wave 1 = Priorities 1 + 6, `docs/review-log/2026-04-25_pass-10-timeline-enhancement-spec.md` for the lifted Pass 10 schema, and `docs/review-log/2026-04-25_phase-3-codex-critique-adjudication.md` §5 for CR-7 origin). Implements the first live instance of the Pass-10-Class Rolling Structured Artifacts pattern named in Phase 4 (`Timeline.md`), and resolves the §4 audit-tier ambiguity surfaced in the Codex critique adjudication.

#### Pass 10 Timeline Artifact (CR-5 closed; Pass-10-Class first live instance)

- **`core-editor/references/pass-10.md`** — new reference file (~150 lines). Documents the eight-section Timeline artifact schema lifted from `docs/review-log/2026-04-25_pass-10-timeline-enhancement-spec.md`:
  1. Event Ledger (tabular, one row per scene)
  2. Master Calendar (day/week reconstruction)
  3. Temporal Marker Inventory (every explicit temporal marker)
  4. Inconsistency Ledger (paradox / drift / ambiguity classification)
  5. Ambiguity Ledger (structural vs. accidental ambiguity)
  6. Revision-Drift Hot Spots (repair recommendation classes)
  7. Recommended Anchor Set (3-7 author decisions)
  8. Diff Notes (input to the timeline-diff validator)

  Also documents naming convention (`Timeline.md` at project root), migration / backward compatibility (existing projects get first Timeline.md on next Pass 10 run with empty Section 8), validator integration (three new validators below), and synthesis integration (Section 4 counts feed severity propagation).

- **`core-editor/references/pass-dependencies.md` §1 Tier 1** — Pass 10 row updated. Pass 10 now produces both a run-folder artifact (existing Entity Tracking output: Rule Ledger + Entity Table + legacy chronology) and a project-level rolling artifact (`Timeline.md`). Added an explanatory paragraph naming Timeline as the first live instance of the Pass-10-Class Rolling Structured Artifacts pattern, listing the three paired validators, and pointing to the canonical schema in `references/pass-10.md`. ~5 lines added.

- **`core-editor/references/run-synthesis.md` §Step 2 Canonical Audit-Signal Propagation Rule** — extended with a new Pass-10-Class artifact integration subsection (~14 lines). Timeline Inconsistency Ledger counts feed synthesis severity via the same canonical rule that governs audit signals: ≥1 paradox → Must-Fix candidate (timeline coherence); ≥3 drifts → Should-Fix candidate (revision-drift hygiene); load-bearing ambiguity → Author Decision. Names the artifact-class-agnostic principle: severity propagation is the same whether the signal originates in an audit findings file or a rolling structured artifact (`Argument_State.md`, `Series_State.md`, `Timeline.md`, future `Plot_Spine.md`).

- **`core-editor/SKILL.md` §Project Integration / Pass-10-Class Rolling Structured Artifacts** — Timeline.md instance status updated from "(Phase 6 implementation per spec)" to "(live; schema in `references/pass-10.md`; three mechanical validators in `scripts/validate.sh`: `timeline-diff`, `timeline-arithmetic`, `timeline-anchor-conflict`)". Closing paragraph updated to mark Timeline as the first live Pass-10-Class instance landed under the named pattern.

#### Three Mechanical Validators for Timeline (Pass-10-Class instance)

Three new validators added to `scripts/validate.sh`. All three honor body-only override markers and Section-8-vs-body discipline (Section 8 is the appendix-equivalent for the Timeline artifact; markers placed there are non-canonical) parallel to the Phase 4 pattern.

- **`scripts/validate.sh timeline-diff <prior_timeline> <current_timeline>`** — surfaces every changed / removed / added Event Ledger row between two Timeline artifacts. Verifies Section 8 (Diff Notes) annotates each diff. Exit 0 if no diff exists, diff is documented in Section 8, or body override marker present; exit 1 if undocumented diff. ~110 lines including self-test (5 cases: positive identical, negative undocumented diff, documented diff, body override, Section-8-only override).

- **`scripts/validate.sh timeline-arithmetic <timeline_file>`** — verifies span calculations sum correctly. Detects negative gaps (revision broke ordering) and explicit conflict markers in Event Ledger rows. Exit 0 if clean; exit 1 if conflicts detected and no body override. ~90 lines including self-test (5 cases: positive clean, negative gap, anchor conflict marker, body override, Section-8-only override).

- **`scripts/validate.sh timeline-anchor-conflict <timeline_file>`** — identifies pre-flagged anchor contradictions / paradoxes in Section 3 (Temporal Marker Inventory). Surfaces candidates (per Pass 10 spec §Risks: validators surface candidates; Pass 10 model judgment classifies). Exit 0 if no candidates; exit 1 if candidates surfaced and no body override. ~95 lines including self-test (5 cases: positive distinct anchors, negative contradiction marker, paradox marker, body override, Section-8-only override).

Override marker syntax (one per validator, body-only honored):

```
<!-- override: timeline-diff-undocumented — <one-sentence rationale> -->
<!-- override: timeline-arithmetic-conflict — <one-sentence rationale> -->
<!-- override: timeline-anchor-conflict — <one-sentence rationale> -->
```

All three validator self-tests pass on the canonical 5-case fixture set per validator. Five Phase 4 validator self-tests (severity-floor, audit-signal-propagation, underdiagnosis-triggers, ledger-consolidation, decision-layer-check) remain green — no regressions.

#### Audit Tier Precedence Rule (CR-7 closed)

- **`core-editor/references/pass-dependencies.md` §4f** — new Audit Tier Precedence Rule subsection (~32 lines). Documents the highest-obligation-wins rule: Auto-run > Auto-recommend before synthesis > Auto-recommend > Recommend. Enumerates seven edge cases (router Auto-run + finding Recommend → Auto-run; router Auto-recommend + finding Auto-recommend before synthesis → promoted; two finding-triggers at Auto-recommend before synthesis → deduplicated; multi-pass Recommend triggers → no promotion; user-declined-at-Recommend later promoted by finding-trigger → re-prompt with new rationale; user-declined-at-Auto-recommend-before-synthesis later trigger → no re-prompt, blind-spot disclosure persists; tier-precedence vs. priority-queue interaction).

- **Cross-references added in §4a, §4b, §4c, §4d** (one-line pointers each, ~4 lines total). §4a: router-triggered audits use §4f when also finding-triggered. §4b: finding-triggered audits use §4f when also router-triggered or fired by multiple passes. §4c: tier definitions establish the §4f ordering. §4d: priority queue applies *after* tier resolution per §4f.

Closes Codex critique §5 (CR-7) — the §4 ambiguity that the same audit could surface through router-triggered (§4a) and finding-triggered (§4b) paths at different obligation levels with no canonical resolution rule.

#### Files

- `plugins/apodictic/skills/core-editor/references/pass-10.md` — new reference file (~150 lines).
- `plugins/apodictic/skills/core-editor/references/pass-dependencies.md` — §1 Tier 1 Pass 10 row + Pass-10-Class explanatory paragraph (~5 lines); §4a/§4b/§4c/§4d cross-reference pointers (~4 lines); §4f new Audit Tier Precedence Rule (~32 lines). Net ~+41 lines.
- `plugins/apodictic/skills/core-editor/references/run-synthesis.md` — §Step 2 Pass-10-Class artifact integration subsection (~14 lines added).
- `plugins/apodictic/skills/core-editor/SKILL.md` — Pass-10-Class subsection Timeline-instance status updated (~3 lines net).
- `plugins/apodictic/scripts/validate.sh` and `scripts/validate.sh` — three new validator commands (`timeline-diff`, `timeline-arithmetic`, `timeline-anchor-conflict`) added before the final `*)` case (~295 lines total including self-tests); usage block extended; doc-comment block extended (~30 lines).
- Version files bumped 1.7.4 → 1.7.6 via `scripts/bump-version.sh 1.7.6` (Phase 5 had not bumped to 1.7.5 yet at Wave 1 execution time; the direct bump to 1.7.6 is documented as a coordination note here for the eventual Phase 5 Wave 1.7.5 retrofit).

#### Out of scope (Phase 6 Wave 2+)

- Priority 3 — Audit-Signal Propagation Table (CR-8 operationalization): per-audit propagation entries deferred to Wave 2.
- Priority 4 — Auto-recommend tier re-audit (CR-3): tier reassignment deferred to Wave 2.
- Priority 2 — Field Reconnaissance prerequisite for argument-shaped runs (CR-4): deferred to Wave 3.
- Priority 5 — Universal audit re-audit: deferred to Wave 3.
- Pass 10 Timeline cross-fixture eval coverage (Regrets Only / Dinner Party / TAY): the Wave 1 release ships the schema + validators + synthesis integration; live-fixture re-runs are downstream eval work.

---

## v1.7.5 - 2026-04-25

### Added — Phase 5: Quality-Risk Mode Triggers + Mode-Conditional Re-Grounding + Focus Map Decision Framework

Closes Phase 5 of the model-capability review (see `docs/review-log/2026-04-25_phase-5-implementation-plan.md`). Three priorities: (1) Quality-Risk Mode Selection layered atop token-fit floor (CR-2 closed); (2) Pre-Pass Re-Grounding restructured into three named blocks (universal contract-hash + standard-context full re-read + single-agent anchor confirmation); (3) Focus Map cross-mode decision framework documented; empirical test deferred to a follow-on workstream.

#### Priority 1 — Quality-Risk Mode Selection (CR-2 closed)

- **`core-editor/references/run-core.md` — new §Quality-Risk Mode Selection subsection** (placed between §Context Window Detection and §Single-Agent Mode). Specifies five enumerated triggers (Q1 consent/governance; Q2 argument-shaped nonfiction with high stakes; Q3 many POVs / non-linear; Q4 prior thin synthesis; Q5 submission readiness), each with a detectable predicate, escalation target, and named rationale. Stacking ceiling = swarm. Override path documented (explicit user acknowledgment recorded as `quality_risk_override` in run metadata).
- **`core-editor/references/run-core.md` §Pre-flight Diagnostics** — appended a one-sentence pointer noting the token-fit recommendations are the floor, with quality-risk overlay above.
- **`core-editor/references/run-core.md` §Single-Agent / §Sequential / §Hybrid / §Swarm Mode "When to use" subsections** — appended one-line pointers to §Quality-Risk Mode Selection.
- **`core-editor/references/run-core.md` §Execution Protocol step 3** — replaced single-line selection rule with three-clause layered rule (token-fit floor → quality-risk overlay → final mode = max(floor, recommendation), user override takes precedence).
- **`core-editor/references/intake-router-runtime.md` §2b** — added a Quality-risk overlay paragraph documenting router-side detection of Q1-Q5 triggers from intake fields and contract draft, with cross-reference to `run-core.md` §Quality-Risk Mode Selection.
- **`scripts/validate.sh quality-risk-triggers <contract_file> [<diagnostic_state_meta_file>]`** — new mechanical check (~280 lines including self-test). Detects Q1-Q5 triggers from contract artifact and (for Q4) optional `Diagnostic_State.meta.json`. Emits per-trigger fired set + escalation target (none / hybrid / swarm). Per-trigger override marker support: `<!-- override: quality-risk-Q[1-5] — <rationale> -->` in contract body. Self-test mode covers one positive (clean fiction), five negative (one per Q1-Q5), one override case. All self-tests PASS.

Closes CR-2 (HIGH confidence — execution mode auto-selection was token-fit only; now layered with quality-risk overlay). The token-fit floor is preserved (mode definitions unchanged); quality-risk only escalates upward. Coordinates with Phase 6 CR-4 (Q2's rationale anticipates Field Reconnaissance prerequisite for argument-shaped runs).

#### Priority 2 — Pre-Pass Re-Grounding mode-conditional restructure

- **`core-editor/references/run-core.md` §Pre-Pass Re-Grounding** — restructured single-protocol re-grounding into three named blocks:
  - **Block A — Contract Integrity Check (Universal, all modes).** Mechanical SHA-256 hash compare against `contract_hash` in `Diagnostic_State.meta.json`. Mode-independent Tool-invocable check; fires in single-agent, sequential, hybrid, and swarm. Reuses existing `validate.sh contract-check`.
  - **Block B — Full Re-Grounding (sequential / hybrid / swarm).** Re-read of contract's controlling idea + anti-idea + non-negotiables and accumulated Findings Ledger before each evaluative pass. Compensation for context salience decay on standard-context per-pass subagent dispatch. Existing behavior preserved verbatim.
  - **Block C — Anchor Confirmation (single-agent large-context).** Lighter protocol: contract integrity check (Block A) + one-line restatement of controlling idea + anti-idea + non-negotiables from active context + review of most recent ledger entry. No fresh text re-load (decorative on a 1M-context single-agent run where anchors remain in attention).
- **Block-selection table** documented; Block A is universal regardless of mode. Mode escalation (per Priority 1) at run start re-runs the selection. Future mid-run escalation handler (ROADMAP) is responsible for re-running this selection table.
- No new validator — Block A reuses existing `validate.sh contract-hash` / `validate.sh contract-check` per §Mechanical Validation Protocol.

Salience-decay rationale named explicitly: it is the original failure mode the protocol was designed to counteract; it is real on standard-context per-pass dispatch (Block B) and negligible in single-agent large-context (Block C). The contract-drift check (Block A) is mode-independent because it catches out-of-band file modification, which can happen in any architecture.

#### Priority 3 — Focus Map Architectural Decision Framework

- **`core-editor/references/hybrid-mode.md` — new §Focus Map Architectural Decision Framework (Phase 5)** appended after §Open Questions. Documents the test hypothesis, test design (3 fixtures × 2 arms), target metrics M1-M4 (Severity Honesty, Audit Routing Coverage, Cross-Pass Connection Density, Author Usability), pass-independence guards G1-G2 (Cross-Pass Connection independence; Findings outside Focus Map ≥40%), and acceptance criteria per spec §Phase 5 ("adopt only if M1-M4 improves on ≥2 metrics for ≥2 fixtures, AND G1-G2 satisfied for all fixtures").
- **Default: Focus Map remains hybrid-only** unless future test produces data supporting cross-mode adoption.
- **Test deferred** note: 6 fixture comparisons (3 × 2) is non-trivial scope expansion beyond Phase 5's prose-and-validator priorities. Decision-recording protocol specifies that when the test runs, the data + decision get logged in a date-stamped review-log entry under `docs/review-log/<YYYY-MM-DD>_focus-map-cross-mode-test.md`, and this section gets a "Resolved" annotation.

#### Files

- `plugins/apodictic/skills/core-editor/references/run-core.md` — §Pre-flight Diagnostics token-fit-floor pointer (~1 line); §Quality-Risk Mode Selection new subsection (~30 lines: 5 triggers + stacking + override path + validator pointer); 4 mode "When to use" pointers (~4 lines); §Execution Protocol step 3 layered-rule rewrite (~6 lines); §Pre-Pass Re-Grounding restructured into Blocks A/B/C with selection table (~70 lines, replacing ~12 lines of single-protocol prose). Net ~+100 lines.
- `plugins/apodictic/skills/core-editor/references/intake-router-runtime.md` — §2b Quality-risk overlay paragraph (~10 lines added).
- `plugins/apodictic/skills/core-editor/references/hybrid-mode.md` — §Focus Map Architectural Decision Framework (Phase 5) (~70 lines added after §Open Questions).
- `plugins/apodictic/scripts/validate.sh` and `scripts/validate.sh` — `quality-risk-triggers` command added (~280 lines including self-test).

#### Out of scope (deferred)

- Adaptive Mid-Run Mode Escalation (spec §Phase 5 Task 4) — ROADMAP execution work, not Phase 5 scope.
- Focus Map empirical test runs — deferred to follow-on workstream when bandwidth permits. Decision framework is documented; default (hybrid-only) maintained.
- Phase 6 priorities (Pass 10 Timeline implementation, Field Reconnaissance prerequisite, Auto-recommend tier re-audit) — Phase 6 (parallel implementation in progress, ships as v1.7.6).
- Phase 4 calibration follow-ups C1-C4 (`decision-layer-check` semantics) — Phase 7 or post-review calibration phase.

---

## v1.7.4 - 2026-04-25

### Added — Phase 4 Wave 3: Decision-Layer Validator + Pass-10-Class Pattern + Initial Eval Coverage

Closes Phase 4 of the model-capability review (see `docs/review-log/2026-04-25_phase-4-implementation-plan.md` and `docs/review-log/2026-04-25_phase-4-eval-coverage.md`). Mechanizes Decision-Layer Consolidation counts (Priority 5), names the Pass-10-class artifact pattern as the Phase 6 unblocker (Priority 6), and runs the initial eval coverage check across all 5 Phase 4 validators against canonical Stage 1 fixtures.

#### Decision-Layer Consolidation Validator (Priority 5)

- **`scripts/validate.sh decision-layer-check`** — new mechanical check (~250 lines including self-test). Verifies five contract checks per `core-editor/references/run-synthesis.md §Step 7` (counts) and `core-editor/references/output-policy.md §Mandatory Appendices / §Evidence Density Self-Check` (presence + density):
  1. Protected Elements — 3-6 entries (counts list items, falls back to bolded paragraphs when no list items present).
  2. Author Decisions — 3-7 entries.
  3. Control Questions — exactly 7 entries.
  4. Mandatory Appendices A, B, C — each present as a heading.
  5. Per-Must-Fix evidence density — every Must-Fix mention has ≥2 references (chapter/scene/line/page/audit-code) in the 6-line window.
  Per-check override markers (body-only honored, appendix-only ignored): `<!-- override: decision-layer-protected-elements -->`, `<!-- override: decision-layer-author-decisions -->`, `<!-- override: decision-layer-control-questions -->`, `<!-- override: decision-layer-appendices -->`, `<!-- override: decision-layer-evidence-density -->`. Self-test mode covers one positive case, four negative cases (5 Control Questions; missing Appendix B; 8 Author Decisions; Must-Fix with <2 refs), and two override cases (body marker downgrades; appendix marker does not).
- **`core-editor/references/run-synthesis.md §Step 7`** — added a Mechanical check paragraph naming the validator and the override-marker syntax. Editorial judgment about WHICH elements/decisions/questions appear is preserved at Step 7; counts and structural compliance become mechanical at Step 10. ~6 lines added.
- **`core-editor/references/run-synthesis.md §Step 10`** — collapsed three formerly-redundant bullets (decision-layer completeness, appendix completeness, evidence density) into a single combined bullet that points to `validate.sh decision-layer-check` and the canonical homes in output-policy. Removes inline rule restatement; runtime gate semantics preserved. Net: -3 lines.
- **`core-editor/references/output-policy.md §Mandatory Appendices`** — added a one-line validator-authoritative annotation (parallel to severity-floor's canonical-home annotation). ~2 lines added.
- **`core-editor/references/output-policy.md §Evidence Density Self-Check`** — appended a sentence pointing to `validate.sh decision-layer-check` Check 5 + override marker syntax; preserves the editorial nuance ("downgrade confidence, not severity"). ~1 line appended.

Closes Codex critique §9.4 ("final author-facing consolidation" model-compensation finding) by making counts mechanical. Phase 2 §2.4 numerical invariants (3-6 / 3-7 / exactly 7) preserved as the validator's rule basis.

#### Pass-10-Class Artifact Pattern Naming (Priority 6 — Phase 6 unblocker)

- **`core-editor/SKILL.md §Project Integration`** — added a Pass-10-Class Rolling Structured Artifacts subsection (~22 lines). Names the pattern: project-level rolling artifacts that share five properties (project-level, structured, diffable, validator-paired, synthesis-layer integrated). Lists existing instances (Diagnostic_State, SYNTHESIS, Argument_State, Series_State) and proposed instances (Timeline per Phase 6, Plot_Spine future). Provides Phase 6 Timeline implementation a clear class to instantiate against per `docs/review-log/2026-04-25_pass-10-timeline-enhancement-spec.md` §Cross-application to non-fiction.

Per Phase 3 §Sequencing interlock (b), this completes in Phase 4 to unblock Phase 6.

#### Initial Eval Coverage Check

- **`docs/review-log/2026-04-25_phase-4-eval-coverage.md`** — new review-log entry documenting validator runs against the four canonical Stage 1 fixtures (Regrets Only Opus, Regrets Only Codex, Dinner Party, TAY).
- **Headline result:** Wave 1 + Wave 2 validators (severity-floor, audit-signal-propagation, underdiagnosis-triggers, ledger-consolidation) produce expected results — OK on positive cases; FAIL on the negative case (Codex Stage 1's underdiagnosis convergence) the loop was designed to catch. No false-positive cascade.
- **Wave 3 decision-layer-check surfaces three calibration follow-ups** documented in the eval-coverage entry as C1-C4 (Author Decisions count semantics; Protected Elements paragraph form; tier-awareness for argument-DE; evidence-density window width). Per Wave 2 guidance, Phase 4 documents calibration findings without re-tuning; these become Phase 5+ work.
- **Pre-existing Wave 2 bash-arithmetic noise fixed.** `ledger-consolidation` was emitting `[: 0\n0: integer expression expected` warnings when grep -c returned nonzero under `set -euo pipefail`. Same bug pattern was present in three locations of the Wave 2 validator and would have appeared in Wave 3 decision-layer-check. Fixed by routing through `{ grep ... || true; } | head -1 | tr -d ' \n'`. All 5 validator self-tests remain green.

Closes Phase 4 Done Gate criterion 7 (eval coverage). No regression on firewall compliance, evidence specificity, severity honesty, or audit-routing blind-spot disclosure (binary checks per `docs/eval-harness-spec.md §Binary Checks`).

#### Files

- `plugins/apodictic/skills/core-editor/SKILL.md` — Pass-10-Class Rolling Structured Artifacts subsection in §Project Integration (~22 lines added).
- `plugins/apodictic/skills/core-editor/references/run-synthesis.md` — Step 7 Mechanical check pointer (~6 lines); Step 10 three-bullet collapse to single combined bullet (net -3 lines).
- `plugins/apodictic/skills/core-editor/references/output-policy.md` — §Mandatory Appendices validator-authoritative annotation (~2 lines); §Evidence Density Self-Check validator pointer (~1 line appended).
- `plugins/apodictic/scripts/validate.sh` and `scripts/validate.sh` — `decision-layer-check` command added (~270 lines including self-test); arithmetic-noise fix for `ledger-consolidation` (~4 hunks); arithmetic-noise fix for new `decision-layer-check` helper. Net ~+422 lines (validator host previously had 11 commands, now 12).
- `docs/review-log/2026-04-25_phase-4-eval-coverage.md` — new eval-coverage report.

#### Out of scope (future phases)

- Decision-layer-check calibration follow-ups C1-C4 (Phase 5 or post-review calibration phase).
- Phase 6: Pass 10 Timeline implementation as the next Pass-10-class instance; per-audit propagation table.
- Phase 7: prose compression / dedup of cross-cutting rules (firewall, anti-sycophancy, absence-first canonical statements where deferred).

---

## v1.7.3 - 2026-04-24

### Added — Phase 4 Wave 2: Override Markers, Underdiagnosis Triggers, Findings Ledger Consolidation

Implements the second wave of Phase 4 of the model-capability review (see `docs/review-log/2026-04-25_phase-4-implementation-plan.md` and `docs/review-log/2026-04-25_phase-3-codex-critique-adjudication.md`). Refactors Wave 1's override detection per Joshua's correction (regex ≠ loose detection), closes CR-6 (Underdiagnosis Retry Loop model-judgment language), and closes the Codex-critique-identified gap on Findings Ledger consolidation.

#### Refactor — Wave 1 override detection migrates from regex to structured markers

- **`scripts/validate.sh severity-floor`** — replaced regex-based override detection ("severity floor", "floor override") with HTML-comment marker detection in the letter body. Per-rule markers: `<!-- override: severity-floor-weak-axis -->`, `<!-- override: severity-floor-systemic -->`, `<!-- override: severity-floor-band-cap -->`. Markers in appendix bodies are non-canonical and ignored. Self-test extended with `over1` (body marker downgrades) and `over_appx` (appendix-only marker does not downgrade) cases.
- **`scripts/validate.sh audit-signal-propagation`** — replaced regex-based override detection ("propagation override", "audit-signal rationale") with HTML-comment marker detection in the synthesis body. Per-class markers: `<!-- override: audit-propagation-must-fix -->`, `<!-- override: audit-propagation-hard-gate -->`, `<!-- override: audit-propagation-high -->`. Same body-vs-appendix discipline. Self-test extended with marker cases.
- **`core-editor/references/output-policy.md §Severity Floor Rules`** — extended the override-path paragraph (Wave 1) with marker syntax + body-vs-appendix rule (~9 lines added).
- **`core-editor/references/run-synthesis.md §Step 2 Canonical Audit-Signal Propagation Rule`** — extended the override-path paragraph (Wave 1) with marker syntax + body-vs-appendix rule (~10 lines added).

Rationale: regex on prose gives narrow precision (false negatives when the magic phrase isn't used), not loose detection. Structured markers give the model a low-friction signal to opt into; looseness comes from the model choosing to insert the marker, not from fuzzy prose matching.

#### Underdiagnosis Retry Loop — condition-triggered logic (CR-6)

- **`core-editor/references/run-synthesis.md §Step 9 Conditional Underdiagnosis Retry Loop`** — replaced model-judgment trigger language with six enumerated detectable triggers:
  1. Convergence trigger (3+ artifacts share a mechanism with no synthesis Must-Fix)
  2. Hard-gate trigger (high-risk audit Alert / hard gate without synthesis Must-Fix)
  3. Cross-pass complication trigger (final-third concern in both character + structure passes)
  4. Multi-axis severity trigger (concern spans 2+ severity classes)
  5. Severity-floor trigger (severity-floor validator returns WARN/FAIL)
  6. Propagation trigger (audit-signal-propagation validator returns ERROR/WARN)
  
  Each trigger is detectable from named artifacts (Findings Ledger, Audit Invocation Log, audit findings files, in-progress letter); none rely on model self-judgment. Override marker syntax documented for each trigger; markers must be in letter body, not appendix. Loop semantics specified: fires once per synthesis pass; addressing all triggers (upgrade or override) advances to Step 10. Net change: ~+30 lines (was 5 lines of model-judgment prose, now ~35 lines of enumerated triggers + override syntax).
- **`scripts/validate.sh underdiagnosis-triggers`** — new mechanical check (~210 lines including self-test). Detects all six triggers; per-trigger override marker downgrades ERROR → WARN. Triggers 5 and 6 invoke `severity-floor` and `audit-signal-propagation` for composability. Self-test mode covers one positive case, three negative cases (convergence, hard-gate, final-third), and one override case.
- **`specialized-audits/references/craft/reception-risk.md §7 Severity Hard Gates`** — added one-line pointer noting that Reception Risk Alerts and §7 hard-gate signals propagate to Underdiagnosis Retry Loop trigger #2 in `run-synthesis.md §Step 9`.

Closes CR-6 (HIGH confidence — cross-bias load-bearing convergence #7 in Phase 3 inventory): converts Step 9 from model-emergent trigger detection to artifact-detectable trigger conditions.

#### Findings Ledger Consolidation Contract + Validator (Codex-critique gap)

- **`core-editor/references/run-synthesis.md §Step 2`** — added a new Findings Ledger Consolidation Contract subsection (sister to the Wave 1 Canonical Audit-Signal Propagation Rule). Specifies inputs (raw Ledger Snippets), outputs (consolidated by-mechanism ledger), required transformations (deduplication, cross-reference annotation, severity collation, source-pointer preservation), reduction expectation (≤70% of raw item count), validator invocation, override marker syntax, and single-agent vs. swarm mode application. ~30 lines added.
- **`core-editor/references/run-core.md §Findings Ledger Protocol`** — added one-line consolidation requirement pointing to the canonical contract. Mandatory after pass dispatch, before synthesis begins.
- **`scripts/validate.sh ledger-consolidation`** — new mechanical check (~150 lines including self-test). Verifies four contract checks: (1) consolidation actually happened (raw "Pass N Findings" headers don't appear ≥3 times in concatenation); (2) cross-pass convergence preserved as annotation; (3) severity collation visible when multiple tiers present; (4) reduction ratio ≤70% if raw ledger provided. Override markers downgrade per-check failures to WARN. Self-test mode covers one positive case (consolidated by mechanism), two negative cases (raw concatenation, no convergence annotation), and one override case.

Closes the Codex-critique-identified gap: turning raw pass/audit Ledger Snippets into a consolidated by-mechanism ledger was model-dependent (Opus produced 337-line consolidated ledger; Codex produced 2,558-line raw-aggregate). The contract specifies the consolidation behavior; the validator verifies compliance.

#### Files
- `plugins/apodictic/skills/core-editor/references/output-policy.md` — marker syntax in §Severity Floor Rules override path (~9 lines added).
- `plugins/apodictic/skills/core-editor/references/run-synthesis.md` — marker syntax in §Step 2 Audit-Signal Propagation Rule (~10 lines); Findings Ledger Consolidation Contract subsection in §Step 2 (~30 lines); §Step 9 rewrite from model-judgment to enumerated triggers (net ~+30 lines).
- `plugins/apodictic/skills/core-editor/references/run-core.md` — consolidation requirement pointer in §Findings Ledger Protocol (~3 lines added).
- `plugins/apodictic/skills/specialized-audits/references/craft/reception-risk.md` — Step 9 trigger pointer on §7 (~3 lines added).
- `plugins/apodictic/scripts/validate.sh` and `scripts/validate.sh` — `severity-floor` and `audit-signal-propagation` refactored to marker-based override detection; two new commands added (`underdiagnosis-triggers`, `ledger-consolidation`) with self-test modes. Net ~+360 lines (validator host previously had 9 commands, now 11).

#### Out of scope (Phase 4 later waves)
- Decision-Layer Consolidation validator (Priority 5 in revised plan).
- Pass-10-class artifact pattern naming (Priority 6 in revised plan; Phase 6 unblocker, may be deferred to Phase 7).
- Per-audit propagation table (Phase 6 work; Wave 1 propagation rule + Wave 2 marker discipline together establish the specification basis).

---

## v1.7.2 - 2026-04-24

### Added — Phase 4 Wave 1: Severity-Floor Consolidation + Audit-Signal Propagation

Implements the first wave of Phase 4 of the model-capability review (see `docs/review-log/2026-04-25_phase-4-implementation-plan.md` and `docs/review-log/2026-04-25_phase-3-codex-critique-adjudication.md`). Closes CR-1 (severity-floor triplication) and CR-8 (audit-internal severity signals had no canonical synthesis propagation rule).

#### Severity-Floor Canonical Home + Validator (CR-1)

- `core-editor/references/output-policy.md §Severity Floor Rules` — designated as the canonical home with a one-line annotation. Added an explicit override-with-rationale path (Appendix B documents any deviation; absence of rationale blocks synthesis). Three numerical rules unchanged (Phase 2 archaeology preserved).
- `core-editor/references/run-synthesis.md §Step 10 Pre-Output Verification` — replaced the duplicate severity-floor restatement bullet with a pointer to the canonical home and a validator-call instruction. Runtime protocol (when the check fires, what blocks delivery) preserved.
- `specialized-audits/references/craft/reception-risk.md §7 Severity Hard Gates` — added an explicit relation-to-canonical statement clarifying that the five reception-specific hard gates are additive (audit-internal severity-event triggers) and never substitute for the framework-level floors. Hard-gate table unchanged.
- `scripts/validate.sh severity-floor` — new mechanical check (~110 lines, including self-test). Verifies the three rules; advisory output (WARN/ERROR/OK); supports an override-rationale path that downgrades ERROR to WARN when Appendix B documents the deviation. Self-test mode (`--self-test`) covers one positive case and three negative cases (one per rule).

#### Audit-Signal Propagation Rule + Validator (CR-8)

- `core-editor/references/run-synthesis.md §Step 2 Audit Finding Consolidation` — added a Canonical Audit-Signal Propagation Rule subsection. Establishes the propagation taxonomy (audit-internal Must-Fix floor → synthesis Must-Fix; hard gate → Must-Fix; HIGH/Alert → MF or SF; MEDIUM/Flag → SF; LOW/Note → CF). Names the validator and the override-with-rationale path. Distinguishes the canonical taxonomy from per-audit specifics (Phase 6 propagation table).
- `core-editor/references/pass-dependencies.md §4 Audit Resolver` — added a one-line pointer to the canonical propagation rule and noted that the per-audit propagation table is Phase 6 work.
- `specialized-audits/SKILL.md` — added a one-line pointer in the How to Use section directing readers to the canonical rule for severity-signal propagation.
- `scripts/validate.sh audit-signal-propagation` — new mechanical check (~125 lines, including self-test). Splits the editorial letter into synthesis body and audit appendix to detect when audit-internal hard gates / Must-Fix floors / HIGH-Alert signals fail to propagate to synthesis-layer Must-Fix or Should-Fix. Override-rationale path supported. Self-test mode (`--self-test`) covers one positive case and three negative cases.

#### Files
- `plugins/apodictic/skills/core-editor/references/output-policy.md` — canonical-home annotation + override path (~5 lines added).
- `plugins/apodictic/skills/core-editor/references/run-synthesis.md` — Step 2 propagation rule (~25 lines added); Step 10 severity-floor bullet collapsed to pointer (-2 / +1 lines net).
- `plugins/apodictic/skills/core-editor/references/pass-dependencies.md` — propagation pointer (~2 lines added).
- `plugins/apodictic/skills/specialized-audits/references/craft/reception-risk.md` — relation-to-canonical statement on §7 (~3 lines added; hard-gate table unchanged).
- `plugins/apodictic/skills/specialized-audits/SKILL.md` — propagation pointer in How to Use (~3 lines added).
- `plugins/apodictic/scripts/validate.sh` and `scripts/validate.sh` — two new commands (`severity-floor`, `audit-signal-propagation`) with self-test modes (~235 lines added; validator host previously had 7 commands, now 9).

#### Out of scope (Phase 4 later waves)
- Underdiagnosis Retry Loop conversion to condition-triggered logic (Priority 3 in revised plan; CR-6).
- Findings Ledger consolidation contract / subagent (Priority 4 in revised plan).
- Decision-Layer Consolidation validator (Priority 5 in revised plan).
- Pass-10-class artifact pattern naming (Priority 6 in revised plan; Phase 6 unblocker, may be deferred to Phase 7).
- Per-audit propagation table (Phase 6 work; the canonical rule added here establishes the specification basis).

---

## v1.7.1 - 2026-04-23

> **Backfilled 2026-04-25 during Phase 7 Wave 1 of the model-capability review.** The original release shipped 2026-04-23 without a changelog entry; the gap was flagged in Phase 4 Wave 1 as a deferred hygiene item and closed here per `docs/review-log/2026-04-25_phase-7-implementation-plan.md` §D1. Entry reconstructed from commits `cfaadef`, `7bb9c34`, `9cd8948`, and version-bump commit `6b477d5`.

### Added — Underdiagnosis Hardening + Deficit-First Diagnostic Rule + release.sh build-antigravity step

Tightens synthesis against soft-pedaled diagnosis. The framework now hunts for absence instead of validating presence, installs tripwires when severity-floor logic is incoherent, and blocks delivery on tone-compliance violations. Eleven craft audits gain a Deficit-First Diagnostic Rule opening block; five audits promoted from Recommend → Auto-recommend before synthesis. Closes the v1.7.0 underdiagnosis vector documented in archaeology and motivates the Phase 4 audit-signal propagation + condition-triggered retry-loop work.

#### Synthesis flow tightening (cfaadef)

- **`core-editor/references/run-synthesis.md` Step 3 (new) — Blind Spot / Absence Inventory.** Before root-cause analysis, scan the Findings Ledger to identify what is missing from the text rather than just evaluating what is present on the page. Missing elements (rushed sequence compression, lacking interiority, unsupported choice architecture) leave no explicit textual footprint and are harder to detect; the Absence Inventory makes the omission scan a required gate before triage.
- **`core-editor/references/run-synthesis.md` Step 9 (new) — Conditional Underdiagnosis Retry Loop.** Abort synthesis if severity-floor logic is incoherent, the Reader Stress Test surfaces uncaptured attacks, or live audit blind spots remain unrouted. (v1.7.2 + v1.7.4 + v1.7.9 later refined this loop into the canonical condition-triggered enumerated-trigger form with `validate.sh underdiagnosis-triggers`.)
- **`core-editor/references/run-synthesis.md` Step 13 (new) — Tone Compliance Check.** Wired to `validate.sh tone-check`; blocks letters containing sycophantic superlatives ("masterpiece," "stunning," "flawless," "clean bill," "tour de force," "triumph," "perfection") before delivery.
- **Steps 10, 11, 12 renumbered** to accommodate Step 3 + Step 9 + Step 13 additions.

#### Output policy (cfaadef)

- **`core-editor/references/output-policy.md` rule #5 (new).** A text is only "structurally clean" if Reader Stress Test, Rejection Memo, and Absence Inventory all explicitly fail to surface deep flaws. Codifies the prohibition against asserting structural soundness from absence-of-flag-firing.

#### Pass dependencies — five audits promoted (cfaadef)

Five audits promoted from Recommend → Auto-recommend before synthesis because they catch omission patterns that undermine the whole letter if skipped:
- Compression
- Female Interiority
- Scene Turn
- Interiority Preservation
- Decision Pressure

(Phase 6 Wave 2 §4a/§4b verification confirmed the promotions hold under the formal Audit Tier Promotion Criteria added in §4c.)

#### Craft audits — Deficit-First Diagnostic Rule (cfaadef + 7bb9c34)

Each audit gets a tailored "Deficit-First Diagnostic Rule" opening block directing the auditor to hunt for absence of structural necessity, interiority, or consequence rather than validate presence of fluent prose. Initial six audits in cfaadef; commit 7bb9c34 extended the rule to five additional craft audits with audit-specific tailoring (no cargo-culting):

**Initial six (cfaadef):**
- `craft/ai-prose-calibration.md` — hunt for absence of voice signature.
- `craft/compression-audit.md` — hunt for absence of scene-level granularity.
- `craft/decision-pressure.md` — hunt for absence of choice architecture.
- `craft/female-interiority.md` — hunt for absence of perception → interpretation → judgment in interiority-load scenes.
- `craft/interiority-preservation.md` — hunt for absence of POV interiority during peak-intensity scenes.
- `craft/scene-turn.md` — hunt for absence of goal + change + consequence (Bickham Turn Test).

**Extension five (7bb9c34):**
- `craft/character-architecture.md` — hunt for absence of genuine agency, psychological cost, and internal contradiction under pressure. Distinctive voice does not prove coherent agency.
- `craft/emotional-craft.md` — hunt for absence of the meaning pipeline (perception → interpretation → judgment → impulse). Feeling-words do not prove transmission.
- `craft/stakes-system.md` — hunt for absence of conversion (visible consequence, narrowing options, persistent cost). Signaled peril does not prove stakes architecture.
- `craft/banister.md` — hunt for absence of steelmanned opposition, author self-implication, and conclusions the text could lose to. Voicing multiple positions does not prove epistemic humility.
- `craft/dialectical-clarity.md` — hunt for absence of the inferential bridge (warrant, honest scope, live disagreement). Citing evidence and gesturing at objection does not prove the argument holds.

#### Tooling (cfaadef + 9cd8948)

- **`scripts/validate.sh tone-check` (new subcommand)** — blocks sycophantic superlatives (masterpiece, stunning, flawless, clean bill, tour de force, triumph, perfection). Wired into `run-synthesis.md` Step 13 as a delivery gate.
- **`scripts/release.sh` extended with build-antigravity step (commit 9cd8948).** Adds a `[4/8] Build generated Antigravity workspace` step invoking `scripts/build-antigravity.mjs`, mirroring how `build-codex.mjs` is run. Without this step, bumping the version left the `antigravity/` workspace mirror stale, and the next `release-verify` run failed with "Antigravity workspace is stale." Renumbers subsequent steps and updates the banner total from 7 to 8.

#### Files

- `plugins/apodictic/skills/core-editor/references/run-synthesis.md` — Step 3 (Absence Inventory), Step 9 (Underdiagnosis Retry Loop initial form), Step 13 (Tone Compliance Check) added; subsequent steps renumbered.
- `plugins/apodictic/skills/core-editor/references/output-policy.md` — rule #5 added (structural-clean condition).
- `plugins/apodictic/skills/core-editor/references/pass-dependencies.md` — five-audit promotion (Compression / Female Interiority / Scene Turn / Interiority Preservation / Decision Pressure).
- `plugins/apodictic/skills/specialized-audits/references/craft/{ai-prose-calibration,compression-audit,decision-pressure,female-interiority,interiority-preservation,scene-turn,character-architecture,emotional-craft,stakes-system,banister,dialectical-clarity}.md` — Deficit-First Diagnostic Rule opening block (11 audits total across cfaadef + 7bb9c34).
- `plugins/apodictic/scripts/validate.sh` — `tone-check` subcommand added.
- `scripts/release.sh` — `[4/8] Build generated Antigravity workspace` step added (commit 9cd8948); banner total 7 → 8.
- Mirrors (antigravity/, codex/, APODICTIC-Gemini/public/apodictic-plugin/) regenerated via `build-codex.mjs`, `build-antigravity.mjs`, and rsync.
- Version bumped via `scripts/bump-version.sh 1.7.1` (commit 6b477d5).

#### Originating commits

- `cfaadef` — Underdiagnosis hardening: absence inventory, retry loop, deficit-first audits.
- `7bb9c34` — Extend Deficit-First rule to 5 additional craft audits.
- `9cd8948` — Extend release.sh with build-antigravity step.
- `6b477d5` — Bump version to 1.7.1 for underdiagnosis hardening release.

---

## v1.7.0 - 2026-04-01

### Added — Harness Engineering Improvements

Applies design principles from Anthropic and OpenAI harness engineering research to the APODICTIC development editor. Motivated by three articles: "Harness Design for Long-Running Apps" (Anthropic), "Effective Harnesses for Long-Running Agents" (Anthropic), and "Harness Engineering: Leveraging Codex in an Agent-First World" (OpenAI).

#### Machine-Readable Sidecar State
- `Diagnostic_State.meta.json` — machine-readable sidecar alongside the human-facing `Diagnostic_State.md`
- Enumerated `next_action.key` for reliable resume dispatch (8 valid values: `run_passes`, `run_synthesis`, `run_spot_check`, `deliver`, `revision_round`, `run_audits`, `coaching`, `handoff_reentry`)
- Resume gate reads sidecar for fast structured routing; falls back to parsing markdown for pre-v1.7 projects
- Template: `references/diagnostic-state-meta-template.json`

#### Mechanical Validation
- `scripts/validate.sh` — 6 zero-token invariant checks: contract hash, contract drift, ledger structure, artifact naming, synthesis sections (14 headings as markdown headings), state line count
- Integrated at checkpoints: contract hash at intake, contract drift at pre-pass re-grounding, ledger check after each pass, artifact naming and ledger check at pre-synthesis gate, 14-heading section validation after editorial letter
- Bundled inside the plugin tree (`plugins/apodictic/scripts/`) for Codex compatibility
- Inline fallbacks for hosts that cannot run shell scripts (e.g., ChatGPT)

#### Post-Synthesis Evidence Spot-Check
- Independent verification layer after synthesis: samples 5 claims from the editorial letter and checks them against the manuscript
- Verifies: evidence exists at cited location, diagnosis matches text, fix class matches root cause
- In multi-agent modes, dispatched as a separate subagent for architectural isolation between letter writer and verifier
- Reports findings as a verification block appended to the editorial letter

#### State Gardening Protocol
- Threshold-triggered archival when `Diagnostic_State.md` exceeds 500 lines (advisory at 300)
- Archives to `Diagnostic_State_Archive_[datetime].md` (ISO 8601, minute-resolution, filesystem-safe)
- Compresses completed sessions, resolved handoffs, answered control questions
- Preserves all unresolved material, root causes, triage, author decisions, coaching log

#### Enhanced Resume Gate
- `/start` presents context-aware summary from sidecar: session count, root cause count, revision progress, next action
- "Continue" option resumes from `next_action.key` dispatch table
- State gardening triggered automatically when state exceeds threshold

### Changed — run-core.md Refactored into Three Files

Split `run-core.md` (1,091 → 653 lines) into three files along phase boundaries:

| File | Lines | Content |
|---|---|---|
| `run-core.md` | ~650 | Intake, pass resolution, execution modes, pass specs, Findings Ledger protocol |
| `run-synthesis.md` | ~330 | Audit integration, synthesis processing, editorial letter format, deliverables, evidence spot-check |
| `state-lifecycle.md` | ~130 | State gardening, revision round protocol |

Cross-references updated in: `SKILL.md`, `start.md`, `ready.md`, `submission-readiness.md`, `run-full.md`.

#### Files
- `references/run-synthesis.md` — new
- `references/state-lifecycle.md` — new
- `references/run-core.md` — refactored (synthesis and state sections removed, handoff pointers added)
- `references/diagnostic-state-meta-template.json` — new
- `scripts/validate.sh` — new (repo root + plugin bundle)
- `scripts/preflight.sh` — copied into plugin bundle for Codex compatibility
- `scripts/build-codex.mjs` — updated to require new files and bundled scripts in archive
- `commands/start.md` — updated resume gate with sidecar routing, enumerated dispatch, state gardening
- `SKILL.md` — updated reference table, workflow contract, QA guardrails

---

## v1.1.0 - 2026-03-17

### Added — Submission Readiness Workflow

New unified workflow for "is this ready to submit?" Runs Core DE → Synthesis → Pass 11 → Compression Test and produces a single readiness assessment document.

#### What it adds over standalone Core DE + Pass 11
- **Compression Test** — tests whether the manuscript's identity survives query/synopsis compression. Populates SR-8 (Better Than It Sounds), SR-10 (Spine Amnesia), SR-13 (Arc Substitution), SR-14 (Comp Fragility), SR-15 (Evidence Thinness) from compression evidence.
- **Unified Readiness Assessment** — single document synthesizing diagnostic findings, verdict (READY / CONDITIONALLY VIABLE / NOT READY), market reality, opening conversion gate, and prioritized next steps. Writers no longer need to cross-reference the editorial letter and Pass 11 output.
- **Full SR code vocabulary** — all 15 submission readiness codes populated across Core DE passes and compression test (vs. 7 in Submission Triage).
- **`/ready` command** — direct entry point bypassing the `/start` router's Q1-Q3 sequence.
- **Abbreviated intake** — pre-fills artifact and goal, asks only publication path, query materials, and execution mode.

#### Router integration
- `full_draft + submit + —` route now resolves to Submission Readiness Workflow (was previously a gap).
- `/start` routes here when artifact = `full_draft` and goal = `submit` without time constraint.
- Submission Triage remains the fast path for `constraint:time`.

#### Files
- `commands/ready.md` — new command
- `references/submission-readiness.md` — workflow specification
- `references/intake-router-runtime.md` — gap closed in route map §6

### Added — Context-Aware Execution Mode Selection

APODICTIC now detects the available context window and selects execution mode accordingly.

#### Large-context models (≥1M tokens)
- **Single-agent mode** is the new default: one subagent runs all passes sequentially in a single context. Manuscript loads once; Findings Ledger still written to disk after each pass.
- Viable for manuscripts up to ~200,000 words (estimated load < 600K tokens).
- Token cost: ~240-300K for a 118K-word novel (roughly half of sequential mode).
- Swarm mode remains available for architectural isolation when the user wants maximum analytical depth.

#### Standard-context models (<1M tokens)
- Existing three-mode behavior preserved: sequential / hybrid / swarm.
- No changes to thresholds or routing.

#### Files
- `scripts/preflight.sh` — computes estimated token load, outputs two recommendation tiers
- `references/run-core.md` — new §Context Window Detection, §Single-Agent Mode, updated execution protocol and token cost table
- `references/intake-router-runtime.md` — §2b now has large-context and standard-context versions
- `docs/subagent-architecture-design.md` — status line updated

---

## v1.0.9 - 2026-03-04

### Added — Reception Risk Audit

New specialized craft audit: **Reception Risk** — "How will this land?" Identifies passages, patterns, and structural choices that create cultural, political, or ideological reception risk. Over-inclusive flagging diagnostic for human sensitivity review. Does not tell the author what to write or what to believe; surfaces risk so the author can make informed decisions.

#### Design rationale
Core passes and the Adversarial Stress Test evaluate craft; they do not evaluate how the text will function as a cultural object. A manuscript can be beautifully written and structurally sound while containing unexamined reception risk — content that hostile readers will weaponize or that well-meaning readers will find hurtful. This audit fills the gap between "does the text work?" and "how will the text land?"

Core failure claim: **unexamined exposure** — culturally charged content present on the page, narrative apparatus not accounting for how it will land.

#### Audit specifications
- 17 diagnostic flags across 5 channels: Representational Risk (RR×4), Extractability (EX×3), Power Framing (PF×4), Cultural Register (CR×3), Harm Weight (HW×3)
- 3-tier severity: Note / Flag / Alert (review urgency, not rewrite urgency)
- 3-way classification: Unexamined / Examined / False Positive
- Three primary artifacts: Risk Map (passage-level with context portability and reviewer questions), Pattern Summary (with P-## IDs), Sensitivity Reader Handoff Memo (conditional)
- Two-pass procedure: over-inclusive marking → coding, Distinguish tests, mode calibration, hard-gate check
- Distinguish framework with 5 decision tests (apparatus, load-bearing, extraction, subject-position, genre-contract), tie-breaking rules, lock-then-classify anti-sycophancy control
- 8-mode calibration matrix with named failure modes (Aestheticized Harm, Collateral Caricature, Archive Shield, Transgression Without Containment, Normalization Drift, Target Blur Satire, Self-Exonerating Frame, Allegory Evasion)
- 5 hard gates including alert concentration rule (≥2 Alerts → automatic handoff) and PF+EX-1 escalation pathway
- 6 interaction patterns with prescribed review orders
- Directional Check: net word-count implication of findings, flag if >10% addition skew
- Cross-genre scope: literary fiction, commercial, historical, dark romance, YA/NA, humor/satire, memoir/autofiction, SFF
- Firewall: diagnostic only — identifies risk, assigns severity, recommends review scope. Forbidden: rewriting, adjudicating, gatekeeping, reducing severity after lock.

#### Level-setting brief
- Theoretical grounding: Jauss (horizon of expectations), Iser (implied reader), Fish (interpretive communities), Hall (encoding/decoding), Booth (rhetorical distance), Genette (focalization), Phelan (ethical positioning)
- 14-pattern failure taxonomy with mechanisms, surface signals, structural isomorphisms
- 6 exemplar techniques for well-managed reception risk with 6 cross-case success signals
- 8-mode calibration evidence (promise, blind spot, false-positive risk per mode)
- Distinguish problem with conflict resolution protocol
- Three-model workflow guidance (discovery, apparatus challenge, extraction stress test)
- Source bibliography: 12 references (7 primary theory, 5 contemporary process)

#### Authoring process
Multi-model synthesis: independent research outputs from Opus 4.6 and Codex 5.3, systematically compared and synthesized across all sections. Stuart Hall reference added from Gemini 2.5 Pro research output.

#### Files added
- `specialized-audits/references/craft/reception-risk.md` — The audit (17 flags, 5 channels, 5 hard gates, 8 mode calibrations, §1–§13)
- `specialized-audits/references/craft/reception-risk-level-setting.md` — Level-setting brief (reception theory, failure taxonomy, positive cases, mode calibration, distinguish problem, three-model workflow, bibliography)

#### Changed: Plugin integration
- `specialized-audits/SKILL.md` — Added Reception Risk row to Craft Audits table, reference file entries, trigger phrases in description
- `core-editor/references/run-core.md` — Added finding-driven audit trigger at Pass 1 (cultural register mismatch on identity/power content at 2+ scenes) and cross-audit trigger (Representation Context surfaces active contestation)
- Audit count updated from 26 → 27 across `plugin.json`, `marketplace.json`, `README.md`

### Added — Title/Framing Architecture (Pass 3)

New conditional diagnostic section in **Pass 3: Rhythm & Modulation** for manuscripts with deliberate titling conceits, epigraph sequences, or section-header systems. Evaluates whether framing devices function as structural argument or decoration.

- Detection criteria for governing conceits in chapter titles, part titles, epigraphs, or section headers
- Deepening test (does conceit develop or repeat at fixed register?)
- Counterpoint test (does framing layer create meaning prose alone doesn't?)
- Coherence test (does conceit hold through full manuscript or lose discipline?)
- New finding-driven trigger: ornamental or incoherent framing conceit → **Literary Craft** audit

#### Changed
- `core-editor/references/run-full.md` — Added Title/Framing Architecture conditional section to Pass 3, updated output specification, added finding-driven audit trigger

### Added — Voice Distinctiveness Comparison (Pass 7)

New diagnostic section in **Pass 7: POV and Voice** for multi-POV manuscripts. Compares cognitive texture of each POV character's interiority across 6 dimensions: sentence architecture, attention pattern, metaphor source domain, temporal orientation, epistemic style, emotional register. Produces a comparison table.

Two new flags:
- **Under-individuation** — 2+ POV characters share cognitive texture across 4+ dimensions (authorial voice absorbing character voice)
- **Selective individuation** — POV characters distinct in surface markers but convergent in deep texture (different topics, same thinking)

#### Changed
- `core-editor/references/run-full.md` — Added Voice Distinctiveness Comparison section to Pass 7, comparison table template, two new flags, updated output specification

---

## v1.0.8 - 2026-03-04

### Added — Compression Audit

New specialized craft audit: **Compression** — "What should be cut?" Identifies expendable material in long-form manuscripts and produces a prioritized cut list with estimated word savings. Subtraction-first diagnostic: finds material to remove, not material to add.

#### Design rationale
The framework's existing passes diagnose structural problems that *imply* cutting but frame their findings as "what's wrong." This audit reframes existing and new findings as "what should go" and quantifies the cost of keeping it. Addresses the framework's structural bias toward addition.

Core failure claim: **retained scaffolding** — the draft carries its construction equipment into the finished building.

#### Audit specifications
- 16 diagnostic flags across 5 channels: Structural Expendability (SE), Informational Redundancy (IR), Scene Efficiency (ScE), Emotional Redundancy (ER), Structural Scaffolding (SS)
- Two primary artifacts: Cut List (3 tiers, sorted by word savings, with confidence ratings) and Compression Map (density per part, mode-aware thresholds)
- Two-pass procedure: discovery sample (~15% of scenes) → enumeration pass before hard-gate escalation
- Distinguish framework with 5 decision tests, explicit conflict resolution rules, and 3-way classification (Cut / Compress / Keep — Load-Bearing)
- Confidence Rubric (High / Medium / Low) gating hard-gate escalation
- 7-mode calibration matrix with named failure modes (Decorative Density, Setup Bloat, Processing Spiral, Guided Tour, Inert Dwell, Informational Detour, Recursive Reflection)
- 4 hard gates with evidence requirements
- Cross-genre scope: literary fiction, thriller, romance, SFF, horror, mystery, memoir/nonfiction

#### Files added
- `specialized-audits/references/craft/compression-audit.md` — The audit (16 flags, 5 channels, 4 hard gates, 7 mode calibrations, §1–§13)
- `specialized-audits/references/craft/compression-audit-level-setting.md` — Level-setting brief (scaffolding theory, over-establishment, diminishing-returns, genre norms, distinguish problem)
- `specialized-audits/references/craft/compression-audit-expansion-stub.md` — Design document (expansion stub)

#### Changed: Plugin integration
- `specialized-audits/SKILL.md` — Added Compression row to Craft Audits table, reference file entries, trigger phrases in description
- `core-editor/references/run-core.md` — Added finding-driven audit trigger at Pass 2 (orphan scenes ≥3 or proportional imbalance >40%)
- Audit count updated from 25 → 26 across `plugin.json`, `marketplace.json`, `.claude-plugin/plugin.json`, `README.md`

---

## v1.0.7 - 2026-03-04

### Added — Protected Elements Section

New required section in the editorial letter synthesis: **§6 Protected Elements — What Not to Touch.** Names 3–6 specific elements the revision must not damage, with reasons. These are the manuscript's load-bearing strengths — scenes, techniques, voice qualities, structural choices, or relationships that are working and that revision could accidentally break.

#### Design rationale
Revision fixes problems but can also destroy what works. §3 identifies strengths; §5 identifies what to change; §6 explicitly marks the no-go zones. Authors revising under pressure tend to over-correct — this section gives them specific guardrails. Zero-cost addition: no new pass, just a new output requirement drawn from existing pass findings.

#### Relationship to §3 (What the Book Does Best)
§3 argues *why* the strengths matter. §6 translates that into *operational protection* — it tells the author which strengths are at risk from the specific revisions recommended in §4 and §5. An element in §3 that isn't threatened by the revision plan doesn't need to appear here.

#### Changed: Editorial Letter Format
- Sections renumbered: old §6 (Strongest Case Against) → §7, old §7 (Stress Test) → §8, old §8 (Appendices) → §9.
- Verification gate updated to check §1–§9.
- All §-cross-references updated across `run-core.md`, `pass-11.md`, `adversarial-stress-test.md`, and `run-full.md`.

#### Changed: Full DE Differences (`run-full.md`)
- Protected Elements at Full DE scale may run up to 8 elements (vs. Core DE's 3–6).
- Pass 11 integration note updated for new section numbering.

---

## v1.0.6 - 2026-03-04

### Added — Kishōtenketsu & Jo-ha-kyū Plot Spines

Two new spines added to the Plot Architecture system, bringing the total from 48 to 50. Contributed by **Appropriate-Record68**.

#### New: Kishōtenketsu (Four-Part Without Conflict) — Spine 6, Family 1

Japanese four-part structure (起承転結) with Chinese and Korean cognates. The major non-conflict-driven structural paradigm in English-language craft discourse. Generates meaning through juxtaposition rather than collision: Introduction (Ki) → Development (Shō) → Turn (Ten) → Reconciliation (Ketsu). No antagonist or crisis required.

- Three logic gates: Juxtaposition Test (does Ten introduce a genuinely non-causal element?), Reconciliation Weight (does Ketsu produce meaning from the juxtaposition?), Development Integrity (does Shō deepen without smuggling in conflict?).
- Critical calibration note: suppresses conflict-driven false positives (Passive Midpoint, Missing Commitment, Crisis Fatigue) when Kishōtenketsu is the identified spine.
- Translation note on *ten*: APODICTIC treats it as juxtaposition, not twist or surprise.
- Cross-reference note added at Three-Act Structure entry for discoverability.
- Genre cross-references: literary fiction (native habitat), manga/comics, slice-of-life, horror (ten-as-wrongness, distinct from Lullaby).

#### New: Jo-ha-kyū (Rhythmic Acceleration) — Spine 44, Family 10

Japanese aesthetic principle (序破急) from Noh drama. A pacing overlay, not a primary spine — diagnoses rhythmic problems within any identified spine. Jo (measured opening) → Ha (accelerating complexity) → Kyū (rapid culmination).

- Three logic gates: Macro Rhythm (whole-work pacing acceleration), Scene-Level Rhythm (internal scene pacing with specified sampling protocol), Scale Nesting (rhythm at multiple scales simultaneously).
- Proportion note: traditional Jo-ha-kyū is not equal thirds (~1/5, 3/5, 1/5); gates use "phases" rather than "thirds."
- Usage note: apply after primary spine identification, not instead of it.
- Genre cross-references: literary fiction, thriller, horror, erotica.

#### Changed: Plot Architecture Audit (`references/plot-architecture-audit.md`)
- Version bumped to 0.5.0.
- All spines renumbered: Family 1 now 1-6 (was 1-5), Family 10 now 41-44 (was 40-42), Families 11-12 now 45-50 (was 43-48).
- Three new rows in Diagnostic Quick Reference ("When the Draft Feels..." table).
- Eight new entries in Spine Compatibility Matrix.
- Removed duplicate Save the Cat + Kishōtenketsu entry (consolidated into new Kishōtenketsu entries).

#### Changed: Plot Selection & Coaching (`references/plot-selection-coaching.md`)
- Version bumped to 1.1.
- Phase 1: Added "contemplative recognition" to reader-feeling map; added "juxtaposition" as engine type.
- Phase 2: Added juxtaposition branch to single-spine decision tree.
- Phase 3: Added Jo-ha-kyū as a structural technique overlay alongside TV/Serial and Game-Inspired formats.
- Phase 5: Added "every diagnostic flags problems but draft works" to stuck-draft symptom table.

#### Changed: SKILL.md (plot-architecture)
- Version bumped to 1.0.4.
- Spine count updated from 48 to 50 across all references.
- Family table updated: Family 1 includes Kishōtenketsu, Family 10 includes Jo-ha-kyū.
- Quick reference logic gates and diagnostic table updated.

#### Changed: Genre Module — Literary Fiction (`genre-literary.md`)
- Pass 2 (Structural Mapping): Added Kishōtenketsu as native structural option; added juxtaposition to organizational principles; added Jo-ha-kyū pacing note.

#### Changed: Genre Module — Horror (`genre-horror.md`)
- Pass 2 (Structural Mapping): Added non-conflict horror note (Kishōtenketsu ten-as-wrongness, distinct from Lullaby rupture).
- Pass 3 (Rhythm): Added Jo-ha-kyū horror pacing mapping.

#### Changed: README.md
- Spine count updated from 48 to 50.

#### Changed: plugin.json
- Version bumped to 1.0.6.

---

## v1.0.5 - 2026-02-24

### Added — Hybrid Mode (Optional Execution Mode)

Hybrid mode is a middle ground between single-context and full swarm. Pass 0+1 reads the entire manuscript and produces a **focus map** — a targeting document that directs each subsequent pass to specific scenes for deep reading. Later passes run as independent subagents with the reverse outline (compressed manuscript) plus only the focus map's targeted excerpts, not the full text.

**Tested** on an 83k-word novel where per-pass targeting was 22–33%, producing categorically richer findings than single-context at ~2.8x the token cost. Single-context vs. hybrid comparison showed: 12 findings (mostly approving) vs. 25 findings (genuinely diagnostic, 92% with counterevidence); opposite diagnoses on the ending; zero cross-pass complication in single-context vs. four genuine complications in hybrid.

**Cost profile:** ~1.5–2x for 60–100k manuscripts; ~2–3x for 100k+ manuscripts. Tested at ~1.4x on 83k (2 analytical passes) and projected ~1.7–1.9x (3 analytical passes).

**Quality profile:** Architectural isolation for later passes (same as swarm), but with targeted rather than full manuscript access. The focus map errs on inclusion (no enforced targeting range; advisory ceiling at 60%), and every pass still receives the complete reverse outline.

#### New: Focus Map specification (`references/hybrid-mode.md`)
- Complete specification for the focus map output type: format, targeting grammar, confidence tiers (high-confidence and broad-net), excerpt extraction protocol, risk analysis, and token cost model.
- Targeting rationale categories drawn from both Pass 0 (outliner lens: arbitrary breaks, unusual ratios, word count anomalies, information density, POV shifts) and Pass 1 (reader lens: belief failures, orientation failures, boredom signals, emotional spikes, promise drift, immersion breaks).
- Cross-pass targets section for scenes flagged by multiple passes.
- Coverage interpretation note in focus map output — explains what the numbers mean for this specific manuscript and offers swarm as alternative if coverage is high.
- No enforced targeting range; inclusion bias + advisory ceiling (60%) only. Triage subagent targets what it finds.
- Ledger persistence requirement: each subagent's findings must be written to file immediately upon return, making the parent orchestrator stateless between dispatches and resilient to context compaction.
- Open questions partially resolved by testing; remaining open questions documented.

#### Changed: Execution Mode section (`run-core.md`)
- Added hybrid mode between single-context and swarm.
- Updated token cost table to three modes.
- Added hybrid mode additional output note to Pass 0 specification (focus map production).

#### Changed: Intake router (`references/intake-router-runtime.md`)
- New §2b: Execution Mode question fires for manuscripts over 40k words. Three plain-language options (standard read / targeted deep read / full independent read) with context-sensitive recommendations. Surfaces the execution mode choice as a first-class intake question rather than burying it in the constraint list.
- §3 options H and I retained as safety net for users who arrive via direct commands or shorter manuscripts.
- §2 `full_draft` submission recommendation now defers to §2b instead of handling execution mode inline.
- Added route map entries for `full_draft + repair + hybrid` and `full_draft + submit + hybrid` (both **Built**).

#### Changed: SKILL.md
- Execution mode description updated to cover all three modes.

#### Changed: README.md
- Execution Modes section expanded to describe single-context, hybrid, and swarm with guidance on when to use each.

---

## v1.0.4 - 2026-02-24

### Added — Swarm Mode (Optional Execution Mode)

A/B testing demonstrated that dispatching each pass as an independent subagent produces roughly twice as many findings with more specific cross-pass connections and more consistent counterevidence, at approximately 5x the token cost. The quality improvement comes from architectural isolation: each pass genuinely cannot see prior analysis until reconciliation, which eliminates anchoring bias and produces multi-perspectival convergence rather than echo.

#### New: Execution Mode section (`run-core.md`)
- **Single-context mode** (default): all passes run sequentially in the current conversation context. No change from prior behavior.
- **Swarm mode** (optional, user-invoked): each evaluative pass runs as an independent subagent with its own context window. Parent orchestrator manages the sequence and accumulates the Findings Ledger between dispatches.
- Swarm Execution Protocol: specifies parent orchestrator responsibilities, what each subagent receives and returns, pass grouping (Pass 0+1 combined), and token cost estimates.
- User invokes swarm mode at intake (e.g., "run this in swarm mode").

#### Changed: Staged Visibility (`run-core.md`)
- Added note clarifying that staged visibility is architecturally enforced in swarm mode (subagent has no prior pass artifacts in context) vs. procedurally enforced in single-context mode (reduces but does not eliminate anchoring).

#### Changed: Design document (`docs/subagent-architecture-design.md`)
- Status updated from "Future (v2.0+)" to "Available as optional execution mode (v1.0.4+)."
- Decision record updated with A/B test results and rationale for shipping as optional mode.

#### Changed: Roadmap (`ROADMAP.md`)
- Subagent Pass Orchestration marked as shipped (optional mode, v1.0.4).

---

## v1.0.3 - 2026-02-23

### Added — Findings Ledger & Editorial Letter Integration

Comparative testing (plugin vs. blind editorial letter on *A Game of Universe*) revealed that pass artifacts contain rich analytical data that the synthesis step compresses away. Context window decay compounds the problem — by synthesis time, earlier pass details have faded. This release adds a running ledger and companion editorial letter changes to preserve pass findings through to the author.

#### New: Findings Ledger Protocol (`run-core.md`)
- **Findings Ledger** — a running document (`[Project]_Findings_Ledger_[runlabel].md`) appended to by each evaluative pass immediately after completion, while pass content is still in active context.
- Each ledger entry contains: Notable Findings, Data Artifacts for Letter Reference, Cross-Pass Connections, Unresolved Questions, and Audit Triggers.
- **"When in doubt, include" rule** — lowers the bar for initial ledger entries since synthesis can ignore noise but can't recover omissions.
- **Retroactive promotion** — later passes can append `[Retroactive — added by Pass N]` notes to earlier ledger sections when a finding proves more important than initially assessed.
- Pass 0 and Pass 10 exempt unless they surface observations warranting a ledger entry (e.g., SFF Rule Ledger inconsistencies).

#### Changed: Synthesis Processing Protocol (`run-core.md`)
- **Step 3 (Root Cause Analysis):** Synthesis now reads the Findings Ledger as primary input. Ledger cross-pass connections are treated as pre-built root cause hypotheses. Unclustered findings carry forward to §4b.
- **Step 6 (Adversarial Stress Test):** Added independence instruction — stress test begins by setting aside pass findings and generating attacks from holistic manuscript reading. Draws also from ledger's Unresolved Questions. Reconciles with pass findings afterward; new attacks enter §7, convergent attacks noted but not duplicated.

#### Added: §4b "Additional Observations from the Diagnostic Passes" (`run-core.md`)
- New editorial letter section between §4 (What Needs Work) and §5 (Revision Checklist).
- Draws from the Findings Ledger — notable findings and cross-pass connections not covered in the main editorial argument.
- Serves two purposes: prevents synthesis compression of useful pass findings, and teaches the author how to use pass artifacts as revision tools.
- Every item includes a cross-reference to the relevant pass artifact.

#### Added: Cross-Reference Convention (`output-policy.md`)
- New section specifying inline cross-reference format: `*(see [Pass Name], §[Section or Table Name])*`.
- Transforms the editorial letter from a standalone argument into a navigation layer over the pass artifacts.
- Findings Ledger added to Output Naming Convention.

#### Changed: Pass Dependencies (`pass-dependencies.md`)
- Added "Running Artifacts" table documenting the Findings Ledger as a non-pass artifact.
- Version bumped to v0.6 (internal architecture version for the pass dependency map).

#### Added: SFF Rule Ledger Cross-Check (`genre-sff.md`)
- **Pass 1 addition:** When Pass 10 is not in the run, Pass 1 cross-references belief failures against Pass 0's Rule Ledger for scaling inconsistencies, cost amnesia, and unexplored implications.
- **Pass 8 addition:** Same condition; Pass 8 checks construct scaling consistency, cost payment consistency across uses, and introduced-but-unexplored rules.
- Both log matches to the Findings Ledger as cross-pass connections between their pass and Pass 0.

### Provenance
- Root cause: Comparative A/B testing (APODICTIC vs. blind editorial letter on *A Game of Universe* by Eric Nylund, 118K words) revealed the plugin's pass artifacts contained richer analysis than the blind letter in several categories, but the synthesis compressed away the advantage. The blind letter independently caught findings (Manifoldification scaling, Erybus backstory-collapse risk, Campbell scaffolding, child abuse access barrier) that the plugin's passes had data for but never surfaced.
- Design document: `Outputs/APODICTIC_Findings_Ledger_Proposal.md`

## v1.0.0 - 2026-02-22

### 1.0 Release

v0.5 UX overhaul is complete: query-driven pass architecture, intake router, scene-level handoff, command alias model, overview dashboard, route explorer. The plugin is navigable by newcomers. Tagging 1.0.

### Changed — Version Hygiene
- Stripped decorative version numbers from ROADMAP.md, README.md, core-editor SKILL.md body header, AUDIT_SELECTION_MATRIX.md, route explorer HTML.
- Removed hardcoded version strings from output template footers (diagnostic-state-template.md, contract-template.md, reverse-outline-template.md, pass-11.md, pre-writing-pathway SKILL.md).
- Canonical version now lives exclusively in `plugin.json` + 4 SKILL.md frontmatter fields.
- Added `scripts/bump-version.sh` to update all 5 locations from a single command.

### Fixed — Audit Resolver Names
- Reconciled 3 string mismatches: "Erotic Content tag" → "Erotic Content", "Character Architecture (deep)" → "Character Architecture", "Banister" → "Banister (Epistemic Humility)".

## v0.4.19 - 2026-02-22

### Added — v0.5 Integration Files (Runtime)
- Added `references/pass-dependencies.md` to core-editor references and wired it into pass resolution flow.
- Added split router files: `references/intake-router-runtime.md` (runtime) and `references/intake-router-design.md` (design notes).
- Added `references/handoff-protocol.md` and integrated scene-level handoff mode transitions.
- Added `overview-dashboard.html` to plugin root.

### Changed — Core Runtime Wiring
- `/start` now runs a mode-aware resume gate before router Q1. If `Diagnostic_State.md` indicates execution mode, it presents: Check the fix / Keep working / Start fresh.
- `core-editor/SKILL.md` now uses concern-driven pass resolution (`pass-dependencies.md`) instead of fixed tier framing.
- `run-core.md` now explicitly resolves concern -> minimum pass set -> dependencies, with baseline floor fallback and optional scene-level handoff behavior.
- `run-full.md` reframed from trigger-gated language to expansion-policy language aligned with resolver auto-escalation.
- `diagnostic-state-template.md` now includes `Mode` and append-only `Handoff History` schema.

### Changed — Command Alias Model
- `/develop-edit` is now defined as a `/start` shortcut with prefilled `artifact=full_draft`, `goal=repair`.
- `/pre-writing` is now defined as a `/start` shortcut with prefilled `artifact=idea`, `goal=draft`.
- `/diagnose` is now defined as targeted resolver routing (`goal=repair`, concern-required).
- `pre-writing-pathway/SKILL.md` now accepts router output as prefilled intake context and skips redundant prompts.

### Changed — Handoff Semantics
- `handoff-protocol.md` language updated from "unload skill" to "suspend/re-enable core-editor constraints" to match actual behavior-contract capabilities.

### Version Reconciliation
- Updated plugin manifest version to `0.4.19` (`.claude-plugin/plugin.json`).
- Updated `core-editor/SKILL.md` version markers to `0.4.19`.
- Updated `README.md` framework version to `v0.4.19`.
- Updated roadmap header version to `v0.4.19`.

## v0.4.17 - 2026-02-21

### Fixed — Audit Discovery and Invocation (Codex review)
- **`/audit` command** expanded from 17 to 28 entries. Now lists all current audits organized by category: Universal (3), Craft (15), Genre (4), Tag (3), Plot (1 cross-reference). Previously missing: Stakes System, Decision Pressure, Force Architecture, Literary Craft, Horror Craft, Mystery/Thriller Architecture, SFF Worldbuilding, Cozy Tag, Philosophical Tag, Erotic Content.
- **`/develop-edit` workflow order** corrected: audit integration now happens after core passes and before synthesis (step 4), matching `run-core.md` §Audit Integration Point. Previously synthesis preceded audit evaluation.
- **`specialized-audits/SKILL.md` catalog** updated: Stakes System, Decision Pressure, and Scene Turn now listed as Universal Audits in both the Available Audits table and Reference Files section. Previously missing from both.
- **Intake router** (`intake-router.md`): added "Run a focused audit on a specific concern" option (E) for full_draft artifact, with corresponding route map entry. Previously no audit route was reachable for complete drafts via `/start`.
- **README.md** counts updated: "23 specialized audits, 5 tag audits" (was "18 deep-dive audits, 2 tag audits"); "28 available audits" (was "17"); version line updated.

### Added — Audit Invocation Log
- New artifact in `run-core.md` §Audit Integration Point: `[Project]_Audit_Invocation_Log_[runlabel].md`. Tracks every audit considered during a run with source (universal/contract/finding-driven), status (run/skipped/deferred), and reason. Referenced in `/develop-edit` step 4.

### Changed — Legacy Module Index
- **`module-index.md`** marked as legacy reference with deprecation header. File paths reference pre-plugin directory structure and do not match current package. Users directed to `AUDIT_SELECTION_MATRIX.md` and `specialized-audits/SKILL.md` for current routing and file paths.
- **`core-editor/SKILL.md`** reference to `module-index.md` annotated as legacy with redirect to current sources.

### Deferred
- **P2 #5 (Token overhead / router split):** Splitting `intake-router.md` into a short runtime decision table and a separate design document would reduce early-turn context consumption. Deferred to future version — requires updating all references and the `/start` command.

## v0.4.16 - 2026-02-21

### Added — Synthesized Audits and Integration Pipeline
- **Stakes System audit** (craft/stakes-system.md + craft/stakes-system-level-setting.md). Three-model synthesis (Opus46, Codex53, Gemini). 22 named diagnostic flags across 6 channels (STX, PC, IM, EG, MP, CL). 4 tracking artifacts. Four-tier distinguish framework. Production audit + level-setting companion.
- **Decision Pressure audit** (craft/decision-pressure.md + craft/decision-pressure-level-setting.md). Three-model synthesis (Opus46, Codex53, Gemini). 23 named diagnostic flags across 7 channels (AV, CS, IS, EC, RF, TR, PV). 6 tracking artifacts. Four-tier distinguish framework. Production audit + level-setting companion.
- **AUDIT_SELECTION_MATRIX.md** — comprehensive routing guide covering all 11 sections: fast entry router, core/full DE passes, Pass 11, craft audits, structural modules, genre audits, tag audits, research modes, recommended bundles, and minimal rule of thumb.

### Added — Audit Integration into Pass Sequence
- **Contract-driven audit activation** at intake (run-core.md): 17-row table mapping genre/mode signals to recommended audits.
- **Finding-driven audit triggers** across 7 passes: Pass 1 (belief failures → DP, emotional flatness → EC, low stakes → SS, action immersion → FA), Pass 2 (causal gaps → Scene Turn, nonfiction situation overwhelming → Franklin), Pass 3 (intensity plateau → SS, pacing stalls → Scene Turn), Pass 4 (triple stasis → EC, intensity plateau → SS, certainty static → Horror/Mystery-Thriller), Pass 5 (motivation discontinuity → DP, agency collapse → SS, under-specified wants → Character Architecture), Pass 6 (single/zero-function → Scene Turn, setup debt → SS), Pass 8 (knowledge errors → DP IS channel, information timing → DP + Reveal Economy).
- **Audit Integration Point** in run-core.md: 4-step protocol for compiling triggers, comparing against contract, running audits, feeding into synthesis.
- **Supplementary Audit Integration Protocol** in run-full.md: 5 rules covering timing, synthesis integration, dashboard feeds, cross-audit coordination, firewall compliance.

### Changed — Synthesis and Output Capacity
- **Processing Protocol** expanded from 5 to 6 steps. New Step 2: Audit Finding Consolidation with 5 rules (map to pass findings, cluster by problem not audit, preserve audit-unique findings, count consolidated problems not flags, carry artifacts to appendices).
- **Appendix A** spec expanded to include audit companion files and tracking artifacts.
- **Full DE letter spec** updated with supplementary audit integration guidance and cross-audit overlap rule.
- **Dashboard** expanded from 8 to 10 components: Component 9 (Decision Pressure Map — option visibility, tradeoff cost, pivot integrity), Component 10 (Force/Action Tracking — conditional on Force Architecture audit). Assembly rules updated for conditional components and expanded length target.

### Changed — Supplementary Audits Section
- **run-full.md** Supplementary Audits section replaced (~20-line stub → ~120-line comprehensive section): Universal Audits (Stakes System, Decision Pressure, Scene Turn, Emotional Craft) with pass connections and pairing logic; Genre/Mode Audits with activation table; Tag Audits table; Integration Protocol.

## v0.4.15 - 2026-02-21 (First Alpha Release)

### Changed — Full Rebrand
- **Package renamed** from `development-editor` to `apodictic`. Top-level directory, plugin.json name, and .plugin filename all updated.
- **Core skill renamed** from `core-development-editor` to `core-editor`. All command files, SKILL.md frontmatter, and internal references updated.
- **Version scheme changed** from 4.x to 0.4.x to reflect pre-1.0 status. All version references across all files updated.
- **Branding normalized** to "APODICTIC Development Editor" throughout. Legacy "APDE" shorthand retained in output template footers.

### Added — Full DE Output Specifications
- **Output specs added** for all Full DE passes (3, 4, 6, 7, 9, 10). Each pass now specifies its output filename and artifact contents, matching the Core DE pass format.
- **Output naming convention** in output-policy.md updated to include all Full DE filenames plus Pass 11 and Full DE Synthesis.

### Added — Inline Genre Calibration
- **Mystery / Investigation** inline calibration section added to core-framework.md — reader expectations, subgenre false-positive warnings, contract additions, priority pass (Pass 8), pass modifications, key diagnostic flags, false-positive warnings.
- **Thriller / Suspense** inline calibration section added to core-framework.md — same depth. All six genres now have inline calibration sections.

### Validated
- Dry run complete: full 11-pass DE executed on a novella-length manuscript. All passes produced output artifacts.
- Density re-audit passed all four §10 proportionality thresholds.
- Three §8 design decisions resolved (rejection memo scope, reference implementation, genre calibration coverage).

## v0.4.14.3 - 2026-02-20

### Added — Documentation and Policy
- **README.md:** Added "What This Plugin Does and Does Not Do" section — user-facing policy covering diagnostic scope, the Firewall, and explicit boundaries (no prose generation, no line editing, no content storage beyond session).
- **README.md:** Added "Intended Audience and Safety Boundaries" section — primary/secondary audience, content coverage statement (all published fiction genres analyzed on their own terms), and safety posture (analytical outputs only, no content generation).
- **CONTRIBUTING.md:** Added "Changelog Policy" section — entry format, framing rules, reframing table for public-facing language, and version bump guidance (patch/minor/major).
- **README.md version** updated to v0.4.14.3.
- Completes Publication Requirements §5 items: changelog policy, safety boundaries, and end-user policy text.

## v0.4.14.2 - 2026-02-20

### Added — SFF Subgenre Pass Recalibrations
- **genre-sff.md** expanded from 415 → 581 lines (+166 lines) with comprehensive subgenre pass recalibrations.
- **Master Calibration Matrix:** 10 subgenres × 8 modified passes showing ELEVATE/STANDARD/DEPRIORITIZE/RECALIBRATE for each combination. Tells the editor exactly how to adjust each pass for the manuscript's specific subgenre.
- **Per-Pass Recalibration Notes** for all 8 modified passes:
  - Pass 0: Hard SF `[SCIENCE CLAIM]` tagging, Epic Fantasy hard/soft/lore rule separation, New Weird rule-flag suppression, Portal Fantasy `[DISCOVERY]` tracking
  - Pass 1: Hard SF system-vs-vocabulary confusion distinction, Cyberpunk disorientation window (15%), Epic Fantasy stalling-vs-slowness, Grimdark interest-not-sympathy threshold (30%), Portal Fantasy synchronization tracking, Progression/LitRPG stat-block tolerance
  - Pass 4: Hard SF eureka tracking, Space Opera scale-wonder, Cyberpunk alienation axis, Epic Fantasy moral weight, New Weird estrangement, Solarpunk hope axis, Grimdark corruption axis, Portal Fantasy wonder resurfacing (2+ scenes after 50%), Progression/LitRPG flat progression affect
  - Pass 5: Hard SF frictionless expertise, Cyberpunk identity-cost augmentation, Urban Fantasy dual-identity strain, Grimdark costless edge, Portal Fantasy learning curve (2+ failures), Progression/LitRPG stat-growth-character-stasis
  - Pass 6: Hard SF lab bench scene, Epic Fantasy empty council, New Weird atmosphere tolerance
  - Pass 8: Hard SF textbook passage + stricter 50% threshold, Cyberpunk flat conspiracy, Epic Fantasy extended cadence (50%), Urban Fantasy spent masquerade, Portal Fantasy flat discovery, Progression/LitRPG incremental grind
  - Pass 9: Hard SF interchangeable tech, Cyberpunk aesthetic cyberpunk, New Weird pattern-not-statement, Solarpunk optimism without evidence, Grimdark decorative nihilism, Progression/LitRPG uncritical meritocracy
  - Pass 10: Hard SF zero-tolerance cost amnesia, Space Opera political-not-physics rules, Cyberpunk system rules, Epic Fantasy hard/soft/hybrid ledger, Urban Fantasy masquerade amnesia, New Weird dream-logic consistency, Progression/LitRPG zero-tolerance system inconsistency
- **Subgenre Deep-Dive Override Table:** 6 threshold overrides for SFF-DD1/DD2/DD3 across Progression/LitRPG, Hard SF, Epic Fantasy, New Weird, and Grimdark.
- **Cross-Reference section** linking to worldbuilding audit subgenre calibration for aligned expectations.

## v0.4.14.1 - 2026-02-20

### Changed — Genre Module Parity Hardening
- **All six genre modules updated to v0.4.14** with numeric thresholds, named deep-dive flags (Detection/Test/Threshold/Flag/Exception format), and mechanistic diagnostic checks. Changes target quantifiability and actionability, matching Romance's level of mechanical specificity.
- **genre-horror.md:**
  - Added Certainty-Intensity Sync Check (parallel to Romance's dual-track model) with alignment table and thresholds (certainty stasis >25%, premature collapse <40%, intensity plateau 3+ chapters)
  - Added Pass 3 thresholds: dread fatigue (3+ consecutive peak chapters), tension bleed (3+ consecutive low chapters), relief ratio (1 valley per 2-3 peaks)
  - Added 4 named deep-dive flags: HOR-DD1 Explanation Kills (>50% mystery resolved before final 20%), HOR-DD2 Numb Protagonist (3+ horror events without deterioration), HOR-DD3 Diminishing Returns (3+ same technique without variation), HOR-DD4 No Normalcy Baseline (horror in first 10% without baseline)
  - Added Dread Ladder diagnostic checks: stuck rung (3+ chapters), premature point-of-no-return (<40%), regression without purpose (2+ rung drop), repeated rungs (3+ without deepening)
  - Added Dread Indicators checklist (9 indicators, parallel to Romance's Chemistry Indicators) with told-not-shown threshold (3+ scenes relying on assertion)
- **genre-mystery.md:**
  - Added Pass 8 cadence and visibility thresholds: clue cadence (1 per 15%), information drought (20% stretch with zero clues), front-loading check (>60% clues in Act I), culprit visibility (minimum 3 scenes, at least 1 in first 40%), suspect pool size (3-6 optimal), red herring ratio (max 2:1), late clue deadline (no essential clues in final 10%), suspect suspicion shift (minimum 1 shift)
  - Added 4 named deep-dive flags: MYS-DD1 Parlor Scene Info Dump (>5% manuscript, <2 interruptions), MYS-DD2 Equal Opportunity Suspect (all suspects identical at 60%), MYS-DD3 Vanishing Investigation (3+ chapters without progress), MYS-DD4 Retroactive Incoherence (2+ scenes contradicting solution)
  - Added Fairness Score system (FAIR/BORDERLINE/UNFAIR granular assessment replacing binary pass/fail) with thresholds
- **genre-thriller.md:**
  - Added Pass 3 thresholds: flat middle (3+ chapters in Act II without escalation), premature climax (resolved before 75%), exhaustion pacing (4+ consecutive peak chapters), scene compression check, tension oscillation minimum (1 valley per 4 peaks)
  - Added Per-Act Resource Ledger (7 resource categories tracked across 5 story points) with depletion thresholds (minimum 2 categories degraded by Act II midpoint, 4+ depleted at dark moment)
  - Added formal Safety Island definition (4 criteria) with thresholds (>2 chapters, >15% manuscript, pre-climax lull)
  - Added 3 named deep-dive flags: THR-DD1 Teflon Protagonist (3+ confrontations without cost), THR-DD2 Convenience Engine (2+ unearned escapes), THR-DD3 Decaying Villain (peak threatening moment before 40%)
  - Added Escalation Ladder diagnostic checks: skipped rung, stuck rung (3+ chapters), missing first trap (by 25%), regression, escalation monotony (3+ same type)
- **genre-sff.md:**
  - Expanded from 5 to 10 pass modifications: added Pass 4 (wonder axis, power-cost emotional check with per-phase register table), Pass 5 (competence-cost inventory table, frictionless system threshold at 60%), Pass 8 (worldbuilding reveal cadence with late-rule threshold at 60%), Pass 9 (thematic integration check for speculative elements)
  - Added 3 named deep-dive flags: SFF-DD1 Magic Microwave (3+ identical-pattern uses), SFF-DD2 Worldbuilding Orphan (3+ weighted details without payoff), SFF-DD3 Escalation Treadmill (3+ threat-then-power-up cycles without lateral thinking)
  - Added Integration with Core Framework section listing all 10 modified passes and combination guidance
  - Added SF/F-specific reader experience flags (5 flags)
- **genre-literary.md:**
  - Added 4 named deep-dive flags: LIT-DD1 Theme-as-Lecture (Stated:Embodied ratio >2:1), LIT-DD2 Unearned Epiphany (<2 precursor scenes), LIT-DD3 Beautiful Emptiness (3+ high-craft passages without payoff), LIT-DD4 Quiet Evasion (2+ thematic questions unaddressed at ending)
  - Added Thematic Dual-Track Model (Theme-as-Content + Theme-as-Form) with alignment check table (parallel to Romance's emotional/physical dual-track)
  - Added Pass 9 thematic thresholds: theme drought (20% stretch with zero instances), front-loading (>60% heavy instances in first third), static theme (identical at 80% vs 20%), epiphany count (>2 investigate)
- **Author name updated** to "Joshua A. Miller, PhD" across README.md, plugin.json, CONTRIBUTING.md, and LICENSE.
- **README.md version** updated from v0.4.6.0 to v0.4.14.

## v0.4.14 - 2026-02-20

### Changed — Thin Orchestrator Refactor
- **Core SKILL.md reduced from 1,660 lines to 253 lines.** Rewritten as thin orchestrator containing only: firewall, operating tiers, workflow contract, pass architecture summary, output policy summary, delegation rules, genre module routing table, reference file routing table, QA guardrails.
- **Extracted four new reference files:**
  - `references/run-core.md` (~450 lines) — Intake protocol, Core DE passes (0/1/2/5/8), synthesis processing/presentation, deliverables, revision round protocol. Loaded every Core DE and Full DE run.
  - `references/run-full.md` (~170 lines) — Full DE passes (3/4/6/7/9/10), supplementary audits (Stakes System, Decision Pressure), Full DE deliverables, structural frameworks reference, certainty axis cues. Loaded only when Full DE tier triggers.
  - `references/output-policy.md` (~210 lines) — Author-facing language rules, output constraints, naming conventions, confidence calibration, epistemic humility, deep analysis triggers, severity honesty protocol, severity floor rules, editorial letter tone/voice, pass-level output protocol. Loaded before writing any output.
  - `references/character-architecture.md` (~110 lines) — Arc types, psychology engine, trauma physics, agency quotient, constraint quotient, voice distinctiveness, ensemble balance, genre tuning packs. Loaded when detailed character analysis needed.
- **Removed from core SKILL.md (delegated to existing reference files or companion skills):**
  - Genre calibration blocks (Literary Fiction, Horror, SF/F, Romance) — already exist as standalone reference files (`genre-literary.md`, `genre-horror.md`, `genre-sff.md`, `genre-romance.md`)
  - Specialized audit stubs (Interiority Preservation, Female Interiority, Series/Composite, Consent Complexity, Banister, Shelf & Positioning, Comedy & Satire, Historical Fiction, Queer Romance/Erotica, Fan Fiction Conversion, Tag Audits) — delegated to `specialized-audits` skill
  - Plot Architecture section (48 spines, logic gates, diagnostic quick reference) — delegated to `plot-architecture` skill
  - Plot Selection & Coaching, Fantasy & Series Architecture stubs — delegated to `plot-architecture` skill
  - Research Modes — delegated to `specialized-audits` skill
  - Pass 11 full internals — pointer to `references/pass-11.md`
  - Reference appendices (Structural Frameworks, Certainty Axis Cues) — moved to `references/run-full.md`
- **Patched `/start` command:** No longer preloads all three companion skills. Loads `core-editor` only; loads target skill after route decision.
- **Patched `/pre-writing` command:** No longer preloads `core-editor` and `plot-architecture` at session start. Loads `pre-writing-pathway` only; loads `plot-architecture` at Phase 4; loads core only on re-entry.
- **Patched `/develop-edit` command:** Added lazy loading instructions for `references/run-core.md`, genre modules, `references/output-policy.md`, and `references/run-full.md`. Fixed cap drift: "surgery list (max 25 items)" → "revision checklist (max 10 items)" to match current output policy.
- **Version bumped to 4.14.**

### Context Load Impact
- `/start` → loads ~253 lines (was ~1,660 + two companion skills)
- `/develop-edit` → loads ~253 + ~450 (run-core) = ~700 lines (was ~1,660)
- Full DE trigger → adds ~170 lines (run-full) on demand
- Genre modules load only when manuscript genre identified
- Specialized audits, plot architecture, pre-writing pathway load only when routed

## v0.4.13 - 2026-02-20

### Changed — Genre-to-Tag Restructure (Track 3)
- **Split Romance/Erotic genre module into Romance (genre) + Erotic Content (tag).** The combined `genre-romance-erotic.md` (423 lines) has been replaced by two purpose-built files:
  - `genre-romance.md` (new, ~320 lines) — Romance genre module. Keeps: relationship engine, structural obstacles, chemistry indicators, escalation stages, trust-rupture-repair cycle, pass modifications (Passes 1, 2, 4, 5, 6, 8), 15 genre-specific flags (including Magic Wand, Idiot Ball, Body Betrayal), subgenre calibration (Contemporary, Historical, Paranormal, Dark Romance, Slow Burn, Poly/WhyChoose, Romantasy, Romantic Suspense). Removed: heat level contract, consent calculus, kink integration, erotic-specific flags, escalation vs. repetition audit — all moved to Erotic Content tag.
  - `erotic-content.md` (new tag audit, ~400 lines) — Cross-genre Erotic Content tag. Applies to any manuscript with significant intimate content regardless of parent genre. Five diagnostic dimensions (Scene Function/Load-Bearing Test, Psychological Presence, Escalation Architecture, Consequence Persistence, Consent Architecture). Eight named flags (EC-1 Decorative Kink, EC-2 Mechanical Intimacy, EC-3 Skipped Aftermath, EC-4 Static Heat, EC-5 Intimacy as Pause, EC-6 Pattern Repetition, EC-7 Technique Saturation, EC-8 Vanishing Interiority). Consent Calculus with logic gates (migrated from old Pass 10 section). Escalation vs. Repetition Audit (migrated from old module). Seven mode calibrations with named failure modes (The Treadmill, The Manual, The Safety Net, The Detour, The Intermission, The Costume Party, The Catalog). Four severity hard gates. Four-class distinguish framework. Output template. Firewall compliance.
- **Updated companion audit integration references:**
  - `consent-complexity.md` → v0.4.13: Updated integration section to point to Erotic Content tag + Romance genre module (was: "Romance/Erotic Module")
  - `queer-romance-erotica.md` → v0.4.13: Updated integration section to point to Erotic Content tag + Romance genre module (was: "Romance/Erotic Module")
  - `interiority-preservation.md` → Expanded from intimate-scene-only stub to cross-genre high-intensity stub with genre-specific application pointers (Force Architecture, Erotic Content tag, Horror Craft, Romance genre module)
- **Updated core-editor SKILL.md:** "Genre Calibration: Romance / Erotic" → "Genre Calibration: Romance" with Erotic Content tag activation note. Updated reference path from `genre-romance-erotic.md` to `genre-romance.md`. Updated interiority preservation cross-reference. Renamed spine family "Relationship/Erotic" → "Relationship/Intimacy."
- **Updated specialized-audits SKILL.md → v0.4.13:** Added Erotic Content tag to Tag Audits table with trigger words. Added `references/tag/erotic-content.md` to reference paths. Updated Consent Complexity and Queer Romance/Erotica reference descriptions.
- **Removed:** `genre-romance-erotic.md` (old combined module), legacy flat-file duplicates of consent-complexity.md, queer-romance-erotica.md, interiority-preservation.md from references root.

### Edge Case Verification
- Pure erotica (no romance arc): Erotic Content tag standalone ✓
- Romantasy (romance + epic fantasy): Romance module + optional Erotic Content tag ✓
- Noir with sex scenes (thriller + erotic content): Erotic Content tag standalone ✓
- Literary fiction with explicit content: Erotic Content tag standalone ✓
- Sweet romance (heat level 1-2): Romance module standalone ✓

## v0.4.12 - 2026-02-20

### Added
- **Force Architecture audit** (craft/force-architecture.md, 622 lines, three-model synthesis). Cross-genre audit evaluating whether physical conflict functions as a coherent narrative engine or produces inert spectacle. Core concept: "inert force" — action choreography present, reader not changed by it. Anchor insight: force that escalates in intensity but not in consequence and meaning conversion is structurally parallel to ornamental prose, inert dread, and informational drift. Six integration dimensions (LG Legibility, TC Tactical Causality, CR Competence-Risk Tension, CP Cost Persistence, ES Escalation Kind-Shift, MC Meaning Conversion) with Integrated/Partial/Detached ratings. Force centrality profile (low/medium/high burden) as pre-assessment calibration. 25 named diagnostic flags: LG-1 White-Room Melee, LG-2 Teleport Bodies, LG-3 Actor Chain Blur, LG-4 Sensory Flatline, LG-5 Disembodied Combatant; TC-1 And-Then Chain, TC-2 Ruleless Advantage, TC-3 Frictionless Execution; CR-1 Godmode Drift, CR-2 Threat Collapse, CR-3 Plot Armor Leak, CR-4 Flawless Execution; CP-1 Rubber-Band Injury, CP-2 Resource Theater, CP-3 Trauma Erasure, CP-4 Collateral Erasure, CP-5 Relationship Reset; ES-1 Scale-Only Escalation, ES-2 Combat Monotone, ES-3 Escalation Cliff, ES-4 Pacing-Significance Inversion; MC-1 Violence Shortcut, MC-2 Cool-Kill Drift, MC-3 Aftermath Null, MC-4 Conversion Failure. Four tracking artifacts: Force Event Ledger with Abstraction Level column (required), Consequence Continuity Ledger with Behavioral Evidence column (required), Escalation Ladder Map (required), Legibility Snapshot Grid (recommended). Pattern interpretation protocol with 10 diagnostic combinations, Special Caution Zones (Horror Craft overlap, Mystery/Thriller overlap, Character Architecture downstream, Emotional Craft upstream, AI-Prose susceptibility). Nine severity hard gates. Seven distinguish tests (Reconstructability, Constraint Consistency, Risk Reality, Persistence, Kind-Shift, Conversion, Cognitive Anchor) with four-class decision matrix (Intentional and Successful, Intentional but Unstable, Ambiguous/Developmental, Accidental Failure). Eight mode calibrations with named failure modes: Map-Table Heroics (military/war), Stat-Sheet Spectacle (systems-driven progression), Perpetual Chase Blur (thriller), Shock Carousel (horror violence), Clean Hit Myth (crime/noir), Incident Theater (domestic violence drama), Aphoristic Carnage (literary violence), City-Scale Weightlessness (superhero/speculative). Explicit audit procedure (claim lock → build artifacts → rate channels → apply flags → synthesize). Output template. Firewall compliance. Stacks with Horror Craft, Mystery/Thriller Architecture, Emotional Craft, Character Architecture, AI-Prose Calibration, Literary Craft, Female Interiority; feeds Pass 11 synthesis.
- **Force Architecture level-setting brief** (craft/force-architecture-level-setting.md, 496 lines, three-model synthesis). Companion research brief grounding the audit in cognitive science, narrative theory, violence theory, and practitioner craft knowledge. Eight theoretical sections: SPECT (situation model construction under stress), event-indexing models (Zwaan/Langston/Graesser five-dimension tracking), event segmentation (Zacks boundary-marking), Sternberg's suspense architecture (suspense > surprise in force scenes), Clausewitz friction (plan-execution gap as cross-genre credibility bridge), the body problem (Disembodied Combatant, sensory hierarchy shifts, tachypsychia, auditory exclusion, experience-level differentiation, distance-difficulty scaling), Arendt/Scarry violence theory (violence/power distinction, bodily representation), Hayakawa abstraction ladder (compression vs. incoherence distinguish tool), consequence persistence (Stark coercive-control model, five-cost tracking). Full failure mode taxonomy (25 named patterns). Positive-case technique extraction across 8 modes: O'Brien truth-by-contradiction / Haldeman temporal estrangement / Cook chronicler distance (military), Dinniman environmental comedy-as-friction / Wight advancement-cost coupling (progression), Child preparation-as-suspense / Ludlum identity-through-combat (thriller), King domestic-space contamination / Jones cultural-weight violence (horror), Hammett consequence-networking / Ellroy institutional complicity (crime/noir), micro-escalation architecture / credibility asymmetry (domestic), McCarthy violence-as-epistemological-event / Morrison violence-as-historical-testimony / O'Connor revelatory violence (literary), power-scale clarity / collateral consequence architecture (superhero/speculative). Eight-mode calibration evidence with named failures and false positive risks. Distinguish problem analysis with seven operational tests, four outcome classes, and seven false-positive controls.

## v0.4.11 - 2026-02-20

### Added
- **Mystery/Thriller Architecture audit** (genre/mystery-thriller-architecture.md, 653 lines, three-model synthesis). Genre-specific audit evaluating whether mystery/thriller information architecture generates inference, urgency, and surprise-with-inevitability or merely assembles genre components. Core concept: "informational drift" — clues, suspects, reversals, and deadlines present but failing to generate hypothesis formation, prediction revision, felt urgency, or satisfying surprise. Anchor insight: information the reader possesses but isn't working with is structurally parallel to horror that doesn't produce dread and literary craft that doesn't do work. Six integration dimensions (IE Information Economy, RH Red Herring Integrity, IL Investigation Legibility, CM Clock Mechanics, RC Reveal Choreography, SF Solution Fairness) with Integrated/Partial/Detached ratings. 28 named diagnostic flags: IE-1 Fog of Facts, IE-2 Clue Starvation, IE-3 Asymmetry Collapse, IE-4 Evidence Island, IE-5 Signal Collapse; RH-1 Noise Cannon, RH-2 Decoy Without Spine, RH-3 Immortal Herring, RH-4 Orphaned Thread, RH-5 Herring Hierarchy; IL-1 Leap Detective, IL-2 Procedure Theatre, IL-3 Oracle Investigator, IL-4 Blind-Side Investigator, IL-5 Passive Catalyst; CM-1 Cosmetic Clock, CM-2 Clock Freeze, CM-3 Clock Without Cost, CM-4 Deadline Detour; RC-1 Reverse Gear Reveal, RC-2 Twist Before Foundation, RC-3 Premature Closure, RC-4 Reveal Pile-Up, RC-5 Explain Patch Ending; SF-1 Cheat Ending, SF-2 Invisible Culprit, SF-3 Obvious Culprit Drift, SF-4 Retroactive Collapse. Four required tracking artifacts: Clue Ledger (with Reader-Tractable? column), Red Herring Ledger (with Quality vs. True Solution column), Clock Pressure Map, Fairness Matrix. Pattern interpretation protocol with six checks, "Reading the Map" guide (8 dimension-combination patterns including Pressure-Puzzle Split), and blast radius classes. Ten severity hard gates (Architecture Void, Cheat Ending, Inferential Inaccessibility, Clock Disconnect, Investigation Opacity, Red Herring Dominance, Retroactive Incoherence, Culprit Underrepresentation, Reveal Timing Failure, Hybrid Contract Breach). Seven distinguish tests (Accessibility, Inference, Clock Conversion, Retroactive Coherence, Misdirection Foundation, Architecture-Ambiguity, POV Fairness) with four-class decision matrix and false-positive guardrails. Special Caution Zones (cozy, noir/hardboiled, literary mystery, inverted mystery, psychological thriller). Nine subgenre calibrations with named failure modes: The Locked Room Lecture (classic whodunit), Tea-Shop Stall Loop (cozy), Clipboard Carousel (procedural), Smoke Without Signal (hardboiled/noir), Unreliable Escape Hatch (psychological thriller), The Bulletin Board (conspiracy/political), Kitchen Twist Roulette (domestic), The Transparent Trap (inverted), The Beautiful Fog (literary hybrid). Dynamic literary mode trigger for hybrid recalibration. Explicit output format templates. Firewall compliance. Stacks with Genre Modules: Mystery and Thriller (contract), Emotional Craft (transmission), Horror Craft Integration (pressure-system parallel), Literary Craft (ambiguity), AI-Prose Calibration (generic fluency); feeds Pass 11 synthesis.
- **Mystery/Thriller Architecture level-setting brief** (genre/mystery-thriller-architecture-level-setting.md, 384 lines, three-model synthesis). Companion research brief grounding the audit in narrative theory, cognitive science, and practitioner craft knowledge. Eight theoretical sections: Sternberg's narrative interest triad with Brewer-Lichtenstein cognitive frame extensions (frame-matching/frame-completion/frame-shifting), Barthes' hermeneutic code (snares/equivocations/partial answers/suspended answers/disclosure mapped to audit dimensions), Eco's model reader (accessibility vs. tractability distinction), Todorov's typology with directional movement insight (mystery expands, thriller narrows), fair-play traditions and diagnostic limits (epistemic parity, prospective vs. retroactive fairness), cognitive psychology (hypothesis formation, model starvation/model lock, predictive processing, misdirection from magic performance studies via Kuhn/Rensink, the "click" of recognition, jigsaw vs. ball-of-twine architecture), craft practitioners (Christie assumption exploitation, Highsmith emotional suspense, Child present-moment urgency, French memory-as-investigation, Flynn epistemic warfare). Full failure mode taxonomy (28 named patterns including Pressure-Puzzle Split hybrid failure). Positive-case exemplar sets across 8 subtypes: Christie/Sayers (classic whodunit), Connelly/French (procedural), Chandler/Highsmith (noir), le Carré/Larsson (conspiracy), Flynn/Highsmith (psychological), French/Ware (domestic), Iles/Columbo (inverted), Eco/Auster/Bolaño (literary hybrid). Nine-subgenre calibration evidence with named failures and false positive risks. Distinguish problem analysis with seven operational tests, four outcome classes, and six false-positive controls.

## v0.4.10 - 2026-02-20

### Added
- **Horror Craft Integration audit** (genre/horror-craft.md, 593 lines, three-model synthesis). Genre-specific audit evaluating whether horror apparatus produces sustained dread, destabilization, and felt consequence or merely delivers horror-coded content. Core concept: "inert dread" — horror present in the plot summary but absent from the reading experience. Anchor insight: horror that escalates in facts but not in felt consequence is structurally parallel to literary craft that doesn't do work and worldbuilding that doesn't integrate. Six integration dimensions (DA Dread Architecture, UD Uncertainty Design, TC Threat Choreography, CE Consequence Embodiment, AP Atmosphere/Image Pressure, ER Ending Residue) with Producing/Partial/Inert ratings. 23 named diagnostic flags: DA-1 Static Dread Loop, DA-2 Kindless Escalation, DA-3 Escalation Cliff, DA-4 Dread Fatigue, DA-5 Anticipatory Deflation; UD-1 Confusion Smog, UD-2 Cheap Certainty, UD-3 Stated Instability, UD-4 Hypothesis Starvation; TC-1 Monster Before Mystery, TC-2 Mystery Without Teeth, TC-3 The Diminishing Reveal, TC-4 Visibility Drift; CE-1 Trauma Without Trace, CE-2 Immunity Bubble, CE-3 Damage as Decoration; AP-1 Gothic Wallpaper, AP-2 Symbolic Static, AP-3 Sensory Anesthesia, AP-4 Beautiful Distance; ER-1 Catharsis Betrayal, ER-2 Aftertaste Null, ER-3 Resolution Collapse. Three tracking artifacts: Horror Pressure Map (required), Consequence Ledger (recommended), Uncertainty Traction Log (optional). Pattern interpretation protocol with six named checks and "Reading the Map" guide. Nine severity hard gates (Pressure Void, Ending Contract Failure, Consequence Void, Dread Stasis, Epistemic Failure, Climax Underperformance, Reveal Timing Failure, Atmosphere Without Engine, Residue Null in Haunt Contract). Six distinguish tests (Interpretive Traction, Contract Coherence, Cost Continuity, Pressure Integrity, Transgression Purpose, Affect Calibration) with decision matrix and false-positive guardrails. Special Caution Zones (quiet horror, cosmic horror, horror-comedy, transgressive fiction). Nine subgenre calibrations with named failure modes: Mind Maze Without Thread (psychological), Abyss on a Leash (cosmic), Meat Without Meaning (body), Haunted Furniture Syndrome (domestic), Ritual Postcard (folk), Shock Treadmill (splatter/transgressive), Velvet Rot (Gothic/atmospheric), The Artful Flinch (literary horror), The Laser-Gun Safari (sci-fi horror). Explicit output format templates. Firewall compliance. Stacks with Genre Module: Horror (contract), Emotional Craft (transmission), Literary Craft (Beautiful Distance), Female Interiority (aestheticized suffering), Consent Complexity (violation/conditioning), AI-Prose Calibration (sensory flattening); feeds Pass 11 synthesis.
- **Horror Craft level-setting brief** (genre/horror-craft-level-setting.md, 328 lines, three-model synthesis). Companion research brief grounding the Horror Craft audit in horror theory, cognitive science, and practitioner craft knowledge. Nine theoretical sections: Carroll's art-horror (compound cognitive-affective mechanism, monster taxonomy — fusion/fission/magnification/massification), Freud's uncanny (familiar-made-strange, recognition before corruption), Kristeva's abjection (boundary collapse, corpse as ultimate manifestation, proximity requirement), Robin Wood's return of the repressed (monster as social/material pressure, structural isomorphism between external threat and internal state), Fisher's weird/eerie (absence-based and wrongness-based horror modes), Ligotti's philosophical horror (consciousness as horror, cosmic dread without monsters), King's terror hierarchy (terror > horror > revulsion), narrative psychology (anticipatory anxiety/predictive processing, habituation, cognitive appraisal, uncertainty tolerance). Full failure mode taxonomy (22 named patterns). Positive-case exemplar sets: Jackson/Harris/Tremblay (psychological), Lovecraft/VanderMeer/Langan/Ligotti (cosmic), Cronenberg/Machado/Barker/Koja (body), Enriquez/Oyeyemi/King/Due (domestic), Link/Jackson/Schweblin (literary), Barker/Ketchum/Palahniuk (transgressive). Folk Horror Chain structural pattern. Nine-subgenre calibration evidence with named failures and false positive risks. Distinguish problem analysis with six operational tests and five false-positive controls.

## v0.4.9 - 2026-02-20

### Added
- **Literary Craft Deep Dive audit** (craft/literary-craft.md, 575 lines, three-model synthesis). Cross-genre audit evaluating whether literary-mode ambitions do structural work or are cosmetic sophistication. Core concept: "ornamentation, not complexity." Anchor insight: literary mode that doesn't do work is structurally identical to worldbuilding that doesn't do work. Five primary integration dimensions (PA Prose Architecture, TF Thematic-Form Integration, IA Image Architecture, ST Subtext/Tonal Control, RA Recognition Architecture) plus one cross-cutting dimension (VA Voice Architecture). 22 named diagnostic flags: PA-1 Verbal Wallpaper, PA-2 Register Cosplay, PA-3 Purple Archipelago, PA-4 Difficulty Without Reward, PA-5 Workshop Finish; TF-1 Thesis Statement Novel, TF-2 Structural Stunt, TF-3 Thematic Furniture, TF-4 Interpretive Vacuum; IA-1 Dead Metaphor Garden, IA-2 Orphan Image, IA-3 Symbol Tyranny, IA-4 Sensory Wallpaper; ST-1 Transparent Character, ST-2 Explanatory Impulse, ST-3 Tonal Drift, ST-4 Ironic Collapse; RA-1 Near Miss, RA-2 Generic Recognition, RA-3 Insight Lecture, RA-4 Recognition Without Preparation; VA-1 Voice as Veneer, VA-2 Workshop Neutral, VA-3 Posture Mismatch. Three tracking artifacts: Literary Architecture Map (required), Scene Pressure Grid (required), Recognition Arc Log (optional). Central Defamiliarization Test (perception vs. appreciation). Eight severity hard gates. Six distinguish tests with decision matrix, false-positive guardrails, and Special Caution Zones (debut manuscripts, translated work, lyric novels). Nine genre-hybrid calibrations with named failure modes: Elegant Plateau (literary realist), Velvet Brake (literary thriller), Metaphor Shelter (literary SFF), Beautiful Rot (literary horror), Case and Chorus Split (literary crime), Competent Fog (upmarket), Structural Stunt elevated (experimental/lyric), Period Piece (literary historical), Beautiful Recollection (literary memoir/CNF). 2-of-5 activation rubric. Explicit output format templates. Firewall compliance section. Stacks with Emotional Craft, AI-Prose Calibration, Female Interiority, SFF Worldbuilding Integration; feeds Pass 11 synthesis.
- **Literary Craft level-setting brief** (craft/literary-craft-level-setting.md, 302 lines, three-model synthesis). Companion research brief grounding the Literary Craft audit in critical theory and practitioner craft knowledge. Nine theoretical sections: Shklovsky's defamiliarization (perception vs. automatization), New Criticism diagnostic method (Brooks on functional metaphor, Empson on productive ambiguity), Booth on rhetorical choice (voice as argument architecture), Phelan on rhetorical narratology (form as rhetorical action), Wood on free indirect style (consciousness management), contemporary craft perspectives (Saunders "bouncer at Club Story," Smith "Two Paths for the Novel," Baldwin, Robinson), Wallace on postmodern irony (foundation for Ironic Collapse), McGurl on Program Era (workshop-homogeneity problem). Full failure mode taxonomy across five categories (22 named flags with theoretical provenance). Positive-case exemplar sets: Morrison/Ferrante/Cusk (literary realism), Carver/Johnson/Berlin/Offill (minimalism), Pynchon/Wallace/Rushdie (maximalism), Sebald/Carson/Rankine (structural form), Ishiguro/Le Guin/McCarthy/Atwood/French (hybrid modes). Cross-genre calibration evidence. Distinguish problem analysis with operational tests and false-positive controls.

## v0.4.8.1 - 2026-02-20

### Added
- **Female Interiority level-setting brief** (craft/female-interiority-level-setting.md, 256 lines). Companion research brief grounding the Female Interiority audit in cognitive science and narratology. Three theoretical pillars: Dorrit Cohn's tripartite consciousness model (Psycho-Narration, Quoted Monologue, Narrated Monologue) providing syntactic markers for the four interiority tiers; Lisa Zunshine's Theory of Mind framework mapping recursive intentionality orders to interiority depth; Susan Lanser's Fictions of Authority connecting gendered voice modes to interiority vulnerability patterns. Includes: Cohn-to-tier mapping table, Voice-Context Vulnerability Matrix (3 voice modes × 7 pressure contexts), structural cascade analysis (Midpoint Pivot and Lie Collapse as interiority failure amplifiers), concrete detection mechanics (mode collapse, verb category shift, ToM order drop, emotional label substitution, reset signal), 11 positive-case exemplars with craft technique identification (Ferrante, Morrison, Milan, Jackson, Jemisin, Tolstoy, Woolf, Machado, Larsen, Anderson, Mantel), 5 cross-case success signals, intentionality problem reasoning with genre-specific challenges, full source set (theory, craft criticism, exemplar fiction). Follows the level-setting companion pattern established by cozy-tag-level-setting.md and sff-worldbuilding-level-setting.md.

## v0.4.8.0 - 2026-02-20

### Added
- **SFF Worldbuilding Integration audit** (specialized audit, genre/sff-worldbuilding.md, 501 lines, three-model synthesis). New audit evaluating whether speculative worldbuilding does narrative work — distinct from the Genre Module: SF/F which handles consistency. Core concept: "inertness, not inconsistency." Five integration dimensions (Cognitive, Thematic, Prose, Social, Emotional) with Integrated/Partial/Detached ratings. 20 named diagnostic flags across five families: World-Character (WC-1 Earth Minds in Alien Bodies, WC-2 The Tourist, WC-3 Wallpaper Competence, WC-4 The Undeformed), Exposition Craft (EC-1 The Wiki World, EC-2 Exposition Rigor Mortis, EC-3 The Mode Mismatch, EC-4 Late-Stage Explaining), Thematic Integration (TI-1 The Cellphone-Proof Theme, TI-2 The Passive Physics Engine, TI-3 Generic Dilemma in Exotic Dress, TI-4 Climax Decoupling), Scale/Depth (SD-1 The Aesthetic Shell, SD-2 Social Architecture Without Social Physics, SD-3 The Load-Bearing Wall That Isn't, SD-4 Scope Inflation Drift), Prose-Level (PL-1 The Noun-Swap World, PL-2 Description Island, PL-3 Register Reversion, PL-4 Metaphor Import Leak). Three tracking artifacts: Integration Map (required), Load-Bearing Ledger (required), Pressure Event Log (optional). World Pressure Loop diagnostic chain. Six Distinguish tests with decision matrix and false-positive guardrails. Eight severity hard gates with numerical thresholds. Eight subgenre calibrations with named failure modes (The Elegant Irrelevance, The Grand Tour, The Appendix Illusion, The Convenient Masquerade, Neon Skin No Bite, Randomness Alibi, Metaphor Cage, The Stat Sheet Treadmill). Cross-genre structural isomorphisms for author legibility. Stacks with Genre Module: SF/F; feeds Pass 11 synthesis.

## v0.4.6.0 - 2026-02-20

### Added
- **Intake Router v1** — single entry point (`/start`) that routes users to the right workflow in 2–3 questions
  - **Question 1 (Artifact):** "What do you have right now?" — idea, fragments, partial draft, complete draft, series. Deterministic thresholds for classification when material is provided rather than self-reported (based on narrative continuity, not word count).
  - **Question 2 (Goal, conditional on Artifact):** Options change per artifact state — prevents offering irrelevant goals. E.g., "Check submission readiness" only appears for complete drafts.
  - **Question 3 (Constraint/Operator modifiers):** Deadline, AI-assisted text, nonfiction, sensitive/legal risk, editing for someone else, facilitating a writing group, co-authoring. Multiple selections allowed.
  - **Fallback disambiguator:** When confidence is low, one tiebreaker question maps to three buckets (start drafting / improve existing / evaluate readiness).
  - **Complete route map** with status flags (built, gap, partially built) for all artifact × goal × constraint combinations.
  - **Gap protocol:** When route target isn't built, acknowledge honestly, offer closest available workflow, name what won't be covered.
- **Router integration in Core DE intake:** When user arrives via `/start`, router output (artifact, goal, constraint flags) skips redundant intake questions.
- New `/start` command (9 commands total, up from 8).

### Changed
- **Genre calibrations reordered:** Literary Fiction first (most common primary module), then Genre-Bending/Literary Mode, then alphabetical (Horror, SF, Romance/Erotic). Previously Romance/Erotic was first.
- **Genre calibrations generalized:** Genre-specific detail in core pass descriptions moved to on-demand genre modules. Core passes are now genre-neutral with summary + pointer to full module. All diagnostic machinery remains available when the genre module is activated.
- **Register Uncertainty diagnostic updated** with multi-genre example (Literary Thriller Horror interrogation scene). The diagnostic now demonstrates register conflict using three registers rather than four, making the core concept clearer.
- **Interiority Preservation audit expanded** from intimate scenes to all high-intensity scenes (combat, interrogation, crisis, intimate encounter). Genre-specific applications section covers Action/Thriller, Romance/Erotic, Horror, and Literary with cross-references to relevant modules.
- **AIC-7: Discourse Leak** integrated into AI-Prose Calibration (7 flag families total). Five evidence categories: Assistant Frame, Hedge Drift, Template Loop, Lexical Convergence, Commitment Evasion. Includes evidence burden requirements, false-positive guardrails, and three-step audit workflow.
- **Examples generalized** across reference files. Character-specific and manuscript-specific examples replaced with role-based descriptions (e.g., "Protagonist" instead of named characters, generic series descriptions instead of titled works). Teaching content preserved; specificity improved for broader applicability.
- **Reference implementation paths normalized.** Internal filesystem paths and project-specific directory names replaced with portable references.
- **Specialized-audits reference directory restructured** into three subdirectories: `craft/` (universal audits), `genre/` (form/genre-specific audits), `tag/` (cross-genre modifier audits). All reference paths updated. Prior changelog entries retain original paths as historical record.
- **Female Interiority audit expanded** from intimate-scene focus to universal craft audit (v0.4.8, three-model synthesis). New diagnostic framework: "interiority thinning" as core concept with four-level spectrum (Full / Thinned / Functional / Absent). 20 named diagnostic flags across four categories (Interiority Thinning IT-1–IT-12, Gaze & Observation GO-1–GO-4, Agency AG-1–AG-4, Relationship RF-1–RF-2). New flags from synthesis: Competence as Costume (IT-8), Caregiver Erasure (IT-9), Ensemble Fade (IT-10), Borrowed Stakes (IT-11), Refrigerated Consequence (IT-12), The Sexy Lamp (GO-4), The Smurfette (AG-4). Interiority Map with named reading patterns (Solitude Spike, Relational Dependency). Severity hard gates for reproducible calls. Five-test Distinguish framework with decision matrix. Genre calibration matrix with named failure modes (Desire Dependency, Generic Terror, The Case as Personality, The Gender-Swapped Archetype, The Aestheticized Woman, Minds in Corsets, Body-Without-Mind). Synthesis handoff spec for Pass 11.
- **APODICTIC branding** adopted in README. Full package rename deferred to publication.

### Notes
- Existing commands (`/develop-edit`, `/pre-writing`, `/diagnose`, etc.) remain functional as direct-access shortcuts. The router is the recommended entry point for new users.
- The router implements the four-axis classification model (Artifact × Goal × Operator × Constraint) from the Publication Requirements. Operator is inferred from context or self-reported in Q3, not asked as a separate question.
- Genre module activation is unchanged: modules load when genre is specified in contract or detected during intake. The core pass generalization means the core framework loads faster and doesn't assume any particular genre.

## v0.4.5.0 - 2026-02-20

### Added
- **Pre-Writing Pathway** — new skill and `/pre-writing` command guiding writers from idea to draftable structure without a manuscript
  - **Phase 0: Writer Mode Calibration** — detects architecture-first vs. discovery-first writers; adjusts pathway pressure, field tolerance, and re-entry interpretation accordingly
  - **Seed Inventory** (Phase 1) — maps writer's raw idea onto 8 seed types (premise, character, world, feeling, scene, theme, genre instinct, comp)
  - **Uncertainty/Assumption Ledger** — tracks confidence (Decided/Provisional/Unknown) and dependencies for every structural decision; persists into Structural Plan and feeds Re-Entry Diff
  - **Readiness Gates** — Storyable gate (after Phase 3: premise + engine + tension cohere) and Draftable gate (before Phase 5: spine candidate + ending instinct + arc states + known unknowns)
  - **Option Architecture** (Phase 4) — presents 2–3 viable spine candidates with tradeoffs instead of converging to one recommendation
  - **Complexity Budget** (Phase 4B) — explicit first-draft scope caps for POV count, subplots, timeline complexity, world-building scope
  - **Prospective Contract** — same schema as standard contract but built from intent; embedded in Structural Plan output
  - **Minimal Viable Plan** — prose-format fallback for discovery writers who pass the storyable gate but not the draftable gate
  - **Re-Entry Diff Protocol** (Phase 6) — classifies divergences between prospective contract and actual manuscript as: intentional evolution, signal loss, structural drift, or expected discovery
  - **Anti-sycophancy controls** — mandatory Hard Risks section, real readiness gates (not rubber stamps), option architecture prevents premature validation, ledger prevents false confidence
- **Output artifact conventions** aligned with Core DE naming: `[Project]_Structural_Plan_[runlabel].md`, `[Project]_MVP_[runlabel].md`, `[Project]_Reentry_Diff_[runlabel].md`
- **AI-Prose Calibration audit** (specialized audit #18) — diagnoses prose-level failure patterns in AI-generated or AI-assisted text
  - 6 flag families: AIC-1 Generic Hand (voice singularity), AIC-2 Velvet Fog (scene fog + lexical genericism), AIC-3 Echo Stack (structural repetition), AIC-4 Register Seams (multi-source splicing), AIC-5 Puppet Dialogue (mouth uniformity), AIC-6 Continuity Smear (world-model failures)
  - 3-tier severity: Spot / Pattern / Systemic
  - Required outputs: flag summary, top 3 systemic risks, contamination map, Keep/Recast/Replace salvage plan, Pass 11 readiness impact note
  - Contract intake integration: drafting-method question triggers automatic activation
  - Model-agnostic design: targets prose quality categories, not model-specific tells

### Notes
- The pre-writing pathway produces a prospective contract that becomes the baseline when the writer returns with a draft. Core DE intake uses it as a starting hypothesis; the Re-Entry Diff surfaces what the writer discovered, lost, or drifted from.
- Discovery-first writers may exit with an MVP instead of a full Structural Plan. MVPs do not feed the Re-Entry Diff — standard intake runs from scratch, with the MVP as context.
- AI-Prose Calibration frames AI-generated text as raw material to salvage, not contamination to detect. The audit is useful for any prose exhibiting the flagged patterns, regardless of origin.

## v0.4.4.8 - 2026-02-18

### Added
- **Severity Honesty Protocol** — 4 rules preventing LLM sycophancy in severity assignments (softening Must-Fix to Should-Fix, hedge language, finding one positive passage to downgrade systemic flags)
- **Severity Floor Rules** — 3 structural constraints ensuring diagnostic coherence (Weak core-promise axis requires Must-Fix flag; systemic blast radius caps verdict; high flag volume caps positive verdicts)
- **Pass-Level Output Protocol** — standardized output ordering for evaluative passes: Analysis → Rejection Memo → Priority Leaks → Strengths. Requires rejection memo in every evaluative pass (Pass 1, 2, 5, 8, and all Full DE passes). Strengths cap tied to leak count.
- **Rejection Memo** as a required component of both individual passes and synthesis ("The Strongest Case Against")
- **Revision Checklist** replaces Surgery List — author-facing table with What / Why / Effort columns (Low/Medium/High effort replaces Must-Fix/Should-Fix/Could-Fix severity labels)

### Changed
- **Core DE Synthesis completely rewritten** as editorial letter format:
  - Processing Protocol: 5-step internal process (Intent Check → Root Cause → Triage → Adversarial Self-Check → Write Letter)
  - Presentation Format: 7 required sections (Title Block, The Short Version, What the Book Does Best, What Needs Work, Revision Checklist, The Strongest Case Against, Appendices)
  - Tone and Voice guidance (avoid framework jargon, mechanistic transitions, strength-padding; use direct declarative assessment, embedded line references, bolded thesis-statement headings)
  - Key principle: processing order ≠ presentation order (self-check runs before writing but appears in appendix)
- **Core DE Deliverables simplified** to Editorial Letter + Diagnostic State (removed Surgery List, Revision Order, Top 10 Reader Questions)
- **Full DE Editorial Letter updated** with 5 scaling differences from Core DE + Pass 11 integration guidance
- **Output Constraints updated**: "Maximum 25 surgery list items" → "Maximum 10 revision checklist items (Core DE); 15 (Full DE)"
- Negative-first ordering: Priority Leaks appear before Strengths in all pass outputs
- Strengths must be specific and evidence-based with citation; capped relative to leak count

### Notes
- This version addresses the documented LLM tendency to soften editorial findings, producing editorial letters that read as one informed voice talking about a book rather than a framework generating output.

---

## v0.4.4.6 - 2026-02-17

### Added
- **Cozy level-setting brief** (`references/cozy-tag-level-setting.md`) — standalone research brief covering BISAC/Thema taxonomy, Circana/PW market data, recovery-psychology research (Rieger et al., Rieger & Bente), narrative-resistance findings (Moyer-Gusé et al.), social connectedness research (Wildschut et al., Juhl et al.), and cross-media cozy scholarship
  - Evidence labeling system: `SOURCE-VERIFIED` vs. `MARKET INFERENCE`
  - Lineage: Codex53 research brief
- **Inline Level-Setting Notes** added to Cozy Tag audit summarizing key external evidence

### Changed
- Tag audit family standard: every tag audit includes an inline Level-Setting Notes section grounding axes in external evidence. A standalone companion brief is the exception for tags with unusually deep evidence bases (cozy), not the standard.
- Philosophical Tag audit: family context updated to reflect inline-first standard
- Specialized-audits reference list: added `references/cozy-tag-level-setting.md`

### Notes
- The discipline of asking "what does the market say? what does the research say?" is institutionalized in the inline section. The cozy brief stays because the evidence genuinely warrants it — BISAC codes, peer-reviewed psych, game-studies scholarship. Most tags won't need a standalone file.

---

## v0.4.4.5 - 2026-02-16

### Added
- **New tag audit: Philosophical Tag** (`references/philosophical-tag.md`)
  - Second audit in the tag audit family (after Cozy)
  - Seven axes: Question Architecture, Dramatic Embodiment, Counterposition Strength, Conceptual Progression, Philosophical Feel, Legibility Under Complexity, Resolution Ethics
  - Philosophical Intensity Spectrum (High / Medium / Low) with severity calibration
  - 21 named diagnostic flags: Topic Fog, Question Collapse, Question Multiplication, Seminar Scene, Parallel Tracks, Illustration Mode, Straw Army, Mouthpiece Asymmetry, Vanishing Objection, Broken Record, Volume Escalation, Late Pivot Without Foundation, Closed Loop, Explanatory Reflex, Opacity Posture, Jargon Fog, Abstraction Drift, Decoration Philosophy, Resolution Collapse, Ambiguity Dodge, Thesis Snap
  - PH flag family (PH-1 through PH-9) with named pattern mappings
  - Cross-genre calibration matrix (Literary, SF, Horror, Fantasy, Thriller, Historical, Mystery, Romance)
  - Axis E (Philosophical Feel) addresses the experience-layer dimension: does the reader *think alongside* the text?
  - Routing distinction: Banister evaluates rhetorical fairness; Dialectical Clarity evaluates argument structure; this audit evaluates philosophical *delivery as experience*
  - Level-setting notes on Thema/BISAC metadata and narrative-transportation research
  - Lineage: Codex53 v0.1 draft → Opus revision

### Changed
- Specialized-audits skill description updated with philosophical/tag audit triggers
- Specialized-audits SKILL.md Tag Audits table: added Philosophical Tag row
- Core SKILL.md Tag Audits section: added Philosophical Tag entry
- Plugin structure note updated: "17 deep-dive audits, 2 tag audits, and 4 research modes"
- All skill versions bumped to 4.4.5

---

## v0.4.4.4 - 2026-02-16

### Added
- **New tag audit: Cozy Tag** (`references/cozy-tag.md`)
  - First audit in the new **tag audit family** — experience-layer diagnostics that sit on top of any parent genre's structural contract
  - Cozy Delivery Model with six axes: Safety Envelope, Softness Signals, Belonging Engine, Recovery Rhythm, Everyday Stakes Presence, Restoration Arc
  - Cozy Intensity Spectrum (High / Medium / Low) with severity calibration per intensity level
  - 18 named diagnostic flags: Trapdoor, Ratchet Without Release, Cruelty Leak, Cozy Skin, Comfort Prop, Warmth Collapse, Relational Vacuum, Protagonist Island, Unrepaired Breach, Summary Recovery, Adrenaline Stack, Fridge Recovery, Crisis Saturation, Inert Domesticity, Escalation Addiction, Pyrrhic Landing, Dangling Thread, Tonal Whiplash Landing
  - CZ flag family (CZ-1 through CZ-8) with named pattern mappings
  - Cross-genre calibration matrix (Mystery, Fantasy, Romance, Horror, Thriller, SF, Literary)
  - Anchor + Interacting Lenses analysis method (not sequential checklist)
  - High-Stakes Cozy misread section addressing the most common beta-reader misdiagnosis
  - "Return address" concept for Belonging Engine axis
  - Lineage: Codex53 v0.1 draft → Opus revision

### Changed
- Specialized-audits skill description updated with cozy/tag audit triggers
- Specialized-audits SKILL.md adds Tag Audits subsection in audit listing
- Core SKILL.md adds Tag Audits section between Specialized Audits and Research Modes
- Plugin structure note updated: "17 deep-dive audits, 1 tag audit, and 4 research modes"

### Notes
- The tag audit family establishes a new architectural category: experience-layer diagnostics distinct from genre audits (structural contracts). Future tag audits (Erotic, Dark/Grimdark, Literary, Hopepunk) will follow the same pattern: experience model with named axes, named diagnostic flags, intensity spectrum, cross-genre calibration, anchor + interacting lenses method.
- This revision also introduces the genre/tag distinction as a framework-level concept, which will inform the broader restructuring tracked in Publication Requirements.

---

## v0.4.4.3 - 2026-02-16

### Added
- **Plot Architecture audit expanded** from 39 spines / 9 families to 48 spines / 12 families:
  - Family 10 (Rhythm & Intensity Engines): Wave/Pulse Structure, Lullaby Structure, Pressure Cooker
  - Family 11 (Format & Frame Engines): Episodic/Modular, Clinical Case File, Nested Dolls, Talisman Structure
  - Family 12 (Transformation & Identity Journeys, Extended): Heroine's Journey (Murdock), Seven-Point Structure (Dan Wells)
  - Each new spine includes full logic gates, severity levels, and genre cross-references
  - Diagnostic Quick Reference expanded with 7 new symptom → diagnosis rows
  - Spine Compatibility Matrix expanded with 11 new combination entries
- **New specialized audit: Plot Selection & Coaching** (`Specialized_Audits/Specialized_Audit_Plot_Selection_Coaching.md`)
  - Upstream structural guidance: works before or alongside Plot Architecture
  - Phase 1: Story Concern Mapping (reader feeling, engine type, truth relationship)
  - Phase 2: Spine Selection Protocol with decision tree (single-spine and multi-spine)
  - Phase 3: Structural Technique Overlays (TV/Serial format, Game-Inspired format)
  - Phase 4: Hybrid Structure Design (layer model: micro/meso/macro/meta, conflict detection, handoff types)
  - Phase 5: Structural Triage for stuck drafts (symptom → diagnosis → prescribe)
  - Phase 6: Pre-Drafting Structural Plan template
- **New specialized audit: Fantasy & Series Architecture** (`Specialized_Audits/Specialized_Audit_Fantasy_Series_Architecture.md`)
  - Part I: 5 fantasy-specific spines with logic gates (Anti-Hero's Journey, Folkloric/Mythic Mosaic, Liminal Drift, Fractured Chronicle, Ritual Pattern)
  - Part II: 6 series-level architectural patterns (Expanding Quest, Character Web, Revolving Protagonist, Seasonal Arc, Mystery Box/Revelation Slow Burn, Empire Cycle/Generational Arc)
  - Part III: 3 series rhythm patterns (Convergent-Divergent Cycle, Event Spine, Mythic Undertow)
  - Part IV: Cross-reference tables linking fantasy spines to general spines and series architectures to per-volume spine choices

### Changed
- `Module_Index.md` updated to v3.5: new audits registered in table, file tree, statistics (now 32 total modules/audits/modes/passes/pathways), coverage notes, and "When to Use What" quick reference.
- Plot Architecture audit description in Module Index now reflects 48 spines / 12 families.

### Notes
- Source material: conversational exploration document ("Alternatives to 3 Act Plot Structures") de-duplicated against existing audit, reformatted into logic-gate structure, and split across three deliverables by function (diagnosis, coaching, architecture).
- Overlapping structures (Freytag, Spiral, Fugue, Braided, Rashomon, Hero's Journey, Quest, Siege) were already in the audit; only genuinely new spines were added.
- Structures better understood as presentation techniques (TV/Serial, Game-Inspired) were placed in the Selection & Coaching audit rather than as spines in the Plot Architecture audit.

## v0.4.4.2 - 2026-02-13

### Added
- New top-level `README.md` with public naming, shorthand, and canonical-doc pointers.

### Changed
- Public-facing product name normalized to `APODICTIC Development Editor` with shorthand `APDE`.
- `SKILL.md` and `Module_Index.md` now include explicit brand alias guidance while retaining legacy filenames for compatibility.
- Output templates now include framework footer branding:
  - `Templates/Contract_Template.md`
  - `Templates/Diagnostic_State_Template.md`
  - `Templates/Reverse_Outline_Template.md`
- Pass 11 module header and output template now use APDE branding for generated reports.

### Notes
- This is a naming and documentation normalization patch; no analysis logic changed.

## v0.4.4.1 - 2026-02-13

### Added
- Formal changelog introduced.
- Canonical-source declaration that `SKILL.md` is the operational source of truth.
- Explicit runlabel convention for core outputs (date-based `YYYY-MM-DD`, optional agent prefix such as `codex53_2026-02-13`).
- Optional Pass 11F (Adversarial Reader Stress Test) surfaced in module documentation where missing.

### Changed
- `SKILL.md` now defines runlabel-based output naming for core passes and clarifies `Diagnostic_State.md` as a rolling state file.
- `SKILL.md` project integration now accepts either `Contract_and_Controlling_Idea.md` or `[Project]_Contract*.md`.
- `SKILL.md` now requires initialization of `Diagnostic_State.md` from `Templates/Diagnostic_State_Template.md` when absent.
- `Module_Index.md` aligned with current pass architecture, including optional 11F and updated output conventions.
- `AI_Development_Editor_Complete_v0.4.4.md` Pass 11 section reframed as a condensed summary with explicit operational authority delegated to `SKILL.md` and `Pass_11_Critical_Quality_Market_Viability_v2.md`.

### Fixed
- Documentation drift between framework index/spec documents on Pass 11 coverage and output naming.
- Ambiguity around first-run bootstrap behavior for `Diagnostic_State.md`.

### Notes
- This release is a governance and consistency patch: no new core analysis passes were added.
- Suggested future process: append entries here whenever pass behavior, output contracts, or required artifacts change.

## v0.4.4 - 2026-02-02 to 2026-02-12 *(historical backfill; staged rollout)*

### Added
- Consolidated reference document: `AI_Development_Editor_Complete_v0.4.4.md`.
- Evaluative gate module: `Pass_11_Critical_Quality_Market_Viability_v2.md` with sub-passes `11A-11F`.
- QF flag family (`QF-1` through `QF-7`) and required Hard Truths/verification structures in Pass 11.
- Research modes under `Specialized_Audits/`:
  - `Research_Mode_Comp_Validation.md`
  - `Research_Mode_Factual_Verification.md`
  - `Research_Mode_Genre_Currency.md`
  - `Research_Mode_Representation_Context.md`
- Franklin redirect workflow: `Franklin_Pathway.md` (pre-spine viability gate).
- New specialized audits:
  - `Specialized_Audit_Emotional_Craft.md`
  - `Specialized_Audit_Scene_Turn.md`
  - `Specialized_Audit_Character_Architecture.md`
  - `Specialized_Audit_Dialectical_Clarity.md`
  - `Specialized_Audit_Memoir_Creative_Nonfiction.md`
  - `Specialized_Audit_Narrative_Nonfiction_Craft.md`

### Changed
- Operational quick-reference updated to `SKILL.md` version `4.4`.
- Workflow model expanded beyond Core/Full to include Franklin redirect criteria for absence-of-story material.
- Module index expanded to include evaluative pass routing and research-mode routing.

### Fixed
- Structural-only diagnostic gap addressed with explicit quality/market/readiness evaluation pass (Pass 11).
- Nonfiction/pre-spine handling gap addressed via dedicated Franklin pathway.

### Notes
- This backfill aggregates multiple file timestamps (not a single atomic commit).
- Earliest clear `v0.4.4` artifacts: research modes (`2026-02-02`) and Pass 11 module (`2026-02-05`).
- Latest core `v0.4.4` alignment in this phase: `SKILL.md`, `Module_Index.md`, and `AI_Development_Editor_Complete_v0.4.4.md` (`2026-02-12`).

## v0.4.3 - 2026-01-29 *(historical backfill)*

### Added
- Register Uncertainty diagnostic in the Literary Fiction module for multi-genre register conflict.
- Reframed interiority audit (`Male Gaze` -> `Interiority Preservation`) with symmetric POV logic.
- New `Series / Composite Novel` specialized audit for part-level and arc-level calibration.
- Subfolder project organization for genre modules, specialized audits, and templates.

### Changed
- Core framework promoted to `AI_Development_Editor_Framework_v0.4.md` version `4.3`.
- Supporting docs updated to reference folderized module paths.

### Notes
- Backfill from internal performance assessment (dated 2026-01-29).
- `v0.4.3` refinements were validated during live testing against a multi-POV literary fiction manuscript.
