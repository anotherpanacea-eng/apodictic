### Pre-Letter Re-Grounding (M2)

Whole-novel editorial letters now **restore the specificity the ledger locked** before they are
written — the context-salience decay that smears "nine belief failures" into "several belief
failures" (`docs/subagent-architecture-design.md:15`) becomes a mechanically checkable fidelity
gate (spec: `docs/synthesis-regrounding.md`, M2; builds on M1's coverage disclosure, which stays
mandatory).

- **New Processing Protocol step 9c — Pre-Letter Re-Grounding** in `run-synthesis.md` (lettered,
  no renumbering; after the step-9b Synthesis Coverage Manifest, before the Step 10 pre-output
  gate and Step 11 letter-writing). Named to avoid collision with the built `run-core.md
  §Pre-Pass Re-Grounding` — a different seam, untouched. The step re-reads the consolidated
  Findings Ledger **verbatim from disk** and re-reads bounded manuscript spans for each
  synthesis-bound finding, then restores exact counts / names / quote anchors into the draft
  claims. **Add-only:** re-grounding may not add a finding (new observations go to §4b without an
  ID), change any severity (Deficit Lock untouched), or soften wording (softness-check still
  applies). It writes a `<!-- regrounding: done -->` marker directly after the coverage marker and
  **updates the M1 manifest** — re-read rows flip to `verbatim` / `in-context` with the
  `regrounded: true` annotation M1 already parse-accepts, so the coverage note improves because
  contact with the text actually happened; it never lets a `degraded` coverage read `ok` (M1's V5
  masking check still fires).

- **Bounded-pull seam (Increment-1 scope-down).** In sequential/hybrid/swarm, the synthesis step
  may request per-finding retrievals (≤ 2 spans × 5k tokens, keyed on `finding_id` +
  `evidence_refs`) serviced by the parent orchestrator (`run-core.md` §Execution Protocol step 10).
  The orchestrator-governed pull *API* is unbuilt (Runner-Governed Execution Increment 4 remains
  future), so this ships **prompt-level** — step-text instructions backstopped by the mechanical
  floors, with a `<!-- deferred: orchestrator-pull-interface (Runner-Governed Execution
  Increment 4) -->` marker recording where a mechanically enforced pull lands if ever.

- **New validator `validate.sh specificity-floor <editorial_letter> <findings_ledger> [--strict]`**
  (`scripts/specificity_floor.py`, mirrored ×2): the **count floor** (a finding whose ledger
  entry locks a count may not deliver a vague quantifier — `VAGUE_QUANTIFIERS`, pinned in one
  module-level constant — with none of that count restored in its letter window; number-word
  matching is case-insensitive, so a sentence-initial "Nine" satisfies a ledger "nine";
  evidence-locator numbers like "sc. 30-31" are stripped so a scene number can't masquerade as a
  restored count) and the **anchor floor** (each delivered Must-Fix window carries an evidence
  reference matching the finding's locked `evidence_refs`, so a restored number rides a
  ledger-matching anchor). Both are blocking; the `<!-- regrounding: done -->` presence check is
  an advisory WARN (`--strict` promotes). Legitimately non-countable findings use an ID-scoped
  `<!-- override: specificity-floor F-… — <rationale> -->` marker (via the shared
  `override_marker` SSoT — code-span-stripped, boundary-matched) + an Appendix B entry. Wired into
  the `run_spot_check` gate and the Step 10 checklist; a canonical re-grounded letter↔ledger pair
  plus hostile arms (decay → count-floor FAIL, anchor-drift → anchor-floor FAIL, missing marker →
  WARN/strict-FAIL) run at `--check-all`.

- **Single ownership of the smuggled-finding direction.** The reverse-direction
  letter-ID-must-exist-in-ledger check is **`finding-trace` E1's** — its sole owner
  (`docs/finding-lifecycle-ids.md`). `specificity-floor` implements no reverse ID check (two
  enforcers with subtly different ID grammars is the drift risk single ownership prevents); the
  step text names `validate.sh finding-trace` as the smuggled-finding gate, and E1's own
  `e1_dangling_ref` self-test pins that shape.
