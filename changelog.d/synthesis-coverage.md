### Synthesis Coverage Disclosure (M1)

Whole-novel editorial letters now disclose what the synthesis step could actually see when it
wrote the letter — the silent degrade (chapters and pass artifacts outside active context at
letter time) becomes a mechanical, author-visible record (spec: `docs/synthesis-regrounding.md`;
M2, pre-letter re-grounding, ships separately).

- **Artifact-read manifest** `[Project]_Synthesis_Read_Manifest_[runlabel].md`, written **before**
  the letter exists — by the parent orchestrator at synthesis dispatch (sequential/hybrid/swarm,
  provenance `dispatch-derived`) or by the agent immediately before letter-writing (single-agent,
  provenance `declared`, labeled in pinned language). Closed row grammar
  (`| kind | id | status | annotations |`; `verbatim | summary | absent`,
  `in-context | outside-active-context`; the `regrounded: true` annotation is encoded now and
  reserved for M2). The denominator is enumerated **from disk** (run-folder globs + preflight
  section boundaries), never from the letter's prose — new Processing Protocol step 9b in
  `run-synthesis.md` + the dispatch-side write in `run-core.md` §Execution Protocol step 10.
- **Coverage note in the letter:** a required `### Synthesis Coverage` subsection of Appendix C
  (no 15th top-level section; `synthesis-sections` untouched), a
  `<!-- coverage: ok|degraded -->` machine marker on the first non-blank line after the title
  block, and a pinned Short Version sentence when degraded. "Degraded" is recomputed from the
  manifest per an exhaustive D1-D4 truth table, relative to the mode's own baseline — normal
  multi-agent outline-mediated coverage is *not* degraded.
- **Additive sidecar object** `synthesis_coverage` in `Diagnostic_State.meta.json`
  (`complexity_signals` additive pattern — property + `$comment` in
  `apodictic.diagnostic-state.v1`, template field, `output-structure.md` docs; no new schema
  file, no version bump).
- **New validator `validate.sh synthesis-coverage <run_folder> [--strict]`**
  (`scripts/synthesis_coverage.py`, mirrored ×2): V1 presence, V2 disk↔manifest row bijection
  (the manifest can neither shrink nor pad the denominator), V3 note/sidecar/marker as exact
  projections of the manifest, V4 provenance/mode agreement (`declared` in a multi-agent run
  fails — the cheap lie is blocked), V5 degrade recompute (masking fails louder than degrading).
  No override markers — disclosure is not overridable. Wired into the `run_spot_check` gate;
  canonical green + degraded-and-disclosed fixtures plus hostile arms run at `--check-all`.
  Launch posture (operator call folded 2026-07-01): the V2/V3/V4 fiction-checks are blocking day
  one; V1/V5 — and so the overall gate — are advisory-first for one release (WARN at exit 0,
  `--strict` promotes), flipping to blocking once real runs confirm the degrade thresholds don't
  over-fire.
