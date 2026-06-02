# Validator Architecture Hardening (Tier 1 Harness bundle)

**Status:** Increment 1 built (severity-floor). Increments 2–6 planned.
**Theme:** move mechanical contract enforcement out of brittle shell regex and into
small Python validators with shared parsers and fixture-driven negative tests — *without*
turning `validate.sh` into anything other than the thin command surface, and without
adding an eval harness. This is the Backlog item **Validator Architecture Hardening**,
bundled with the two adjacent loose ends it naturally closes (release-gate canonical
runs; Harness Contracts v2 completion).

## Why

`validate.sh` has done heroic work, but every external review surfaced regex-shaped
edge cases: severity-label forms (`**Severity:** Must-Fix` vs `- Must-Fix:`), prefix
evidence-ref matches (`Chapter 3` matching `Chapter 34`), calibration-line downgrades,
body-vs-appendix marker placement. v2.0.0 began the migration — `structured_findings.py`,
`honesty_check.py`, `apodictic_artifacts.py`, `run_gate.py` are real parsers behind thin
`validate.sh` arms, each with a documented no-`python3` degrade path. This bundle extends
that precedent to the prose-validator arms that still parse markdown with shell regex.

## Architecture

Two shared parser modules back the bash-regex arms; `validate.sh` arms become thin
delegators that fall back to their existing bash implementation when `python3` is absent
(the established degrade discipline — the block stays human-readable and the gate degrades
to the prior behavior, never to nothing).

- **`scripts/letter_checks.py`** — editorial-letter / ledger prose validators. Shared
  primitives: body-vs-appendix split (synthesis body above the first `Appendix <X>`
  heading is canonical for findings; markers in appendices don't count), override-marker
  detection (body only), case-insensitive token counting, token-boundary evidence-ref
  matching. Backs: `severity-floor` (done), then `decision-layer-check`,
  `audit-signal-propagation`, `underdiagnosis-triggers`, `quality-risk-triggers`,
  `ledger-consolidation`, `audit-tier-criterion`, `argument-recon-prerequisite`.
- **`scripts/timeline_checks.py`** (Increment 4) — the timeline arithmetic arms
  (`timeline-diff`, `timeline-arithmetic`, `timeline-anchor-conflict`). These are genuine
  computation (date math, conflict detection), the strongest Python candidates of all.

**Output contract is preserved exactly.** Callers grep arm stdout — e.g.
`underdiagnosis-triggers` Trigger #5 greps `severity-floor` for lines beginning
`WARN`/`ERROR`/`FAILED` and relies on its exit code. Ported arms keep those prefixes and
exit semantics so no caller changes.

**Fixtures** follow the existing data-driven convention (`structured_findings.py`):
`test_fixtures/lc.<pass|fail>.<check>.<name>.md`; `.pass.` ⇒ clean (exit 0), `.fail.` ⇒
caught (exit 1). Fixtures are single-homed in `plugins/apodictic/scripts/test_fixtures/`;
the root `scripts/` copy resolves them via the same `_fixture_dir()` fallback the other
helpers use.

## Increment plan

| # | Track | Scope | Ships |
|---|-------|-------|-------|
| **1** | A — Validator Hardening | `letter_checks.py` shared module + port **severity-floor**; fixture suite; degrade path; build-archive registration. | **this PR** |
| 2 | A | Port **decision-layer-check** + **audit-signal-propagation** (incl. `--check-registry`) onto `letter_checks.py`. | next |
| 3 | A | Port **underdiagnosis-triggers**, **quality-risk-triggers**, **ledger-consolidation**, **audit-tier-criterion**, **argument-recon-prerequisite**. | next |
| 4 | A | `timeline_checks.py` + port the three **timeline-** arms (true arithmetic). | next |
| 5 | B — Release gate | Extend `validate.sh --check-all` to run validators against the *actual* canonical/shipped files: `audit-tier-criterion` vs `pass-dependencies.md` §4a/§4b; `decision-layer-check` + `audit-signal-propagation` vs the shipped sample letters; `timeline-*` vs a new shipped canonical Timeline fixture. Closes the deferred *Canonical-framework validator runs as release gate* item. | next |
| 6 | C — Contracts v2 completion | Schema the still-unschema'd artifacts so JSON Schema is source-of-truth for the whole set: Severity Calibration appendix entries (`apodictic.severity_calibration.v1`) and gate-event records. The calibration schema lets `softness-check` read structured data instead of parsing appendix prose — closing the loop with Track A. | next |

Each increment is a separately-verified PR (Cowork budgets; bounded blast radius), the
same stack discipline used for v2.0.0 #10–#14 and the harness work #18–#19.

## Verification (every increment)

1. `scripts/validate.sh --self-test-all` green (validator count unchanged — arm names are
   stable; this is a re-implementation, not a new validator).
2. `scripts/validate.sh --check-all` green (real-file invariants).
3. `node scripts/build-codex.mjs --check` / `build-antigravity.mjs --check` clean after
   regenerating the mirrors.
4. Canonical/root `scripts/` dual-copy parity (`diff` clean).
5. For each ported arm: the legacy `WARN`/`ERROR`/`FAILED`/`OK` output contract and exit
   codes are preserved (verified against the arms that grep them).

## Non-goals

- No eval harness, no scoring/judgment layer — this is mechanical contract enforcement.
- No new validators or changed validator semantics — ports reproduce existing behavior
  (the bash self-test cases become Python/fixture cases), then harden the edges.
- `validate.sh` stays the command surface; it does not gain logic beyond dispatch +
  degrade.
