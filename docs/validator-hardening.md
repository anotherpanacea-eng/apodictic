# Validator Architecture Hardening (Tier 1 Harness bundle)

**Status:** Increments 1–6 built. The **editorial-letter / ledger family** is on
`letter_checks.py`; the **timeline family** is on `timeline_checks.py`; the
**contract/config/run-folder family** (quality-risk-triggers, audit-tier-criterion,
argument-recon-prerequisite) is on `config_checks.py`. All `validate.sh` prose/config arms now
delegate to a real parser with a bash degrade path. **Inc 6** extends `--check-all` to run the
ported validators against the real `pass-dependencies.md` and two canonical worked examples
(`example-editorial-letter.md`, `example-timeline.md`), so framework drift is caught at release
time. Increment 7 (Contracts v2 completion) remains.

<!-- Pre-Inc-5 status retained below for context. -->
Increments 1–4 built — the whole **editorial-letter / ledger validator family**
is on the shared `letter_checks.py` parser (severity-floor, decision-layer-check,
audit-signal-propagation, underdiagnosis-triggers, ledger-consolidation), and the **timeline
family** is on the new `timeline_checks.py` parser (timeline-diff, timeline-arithmetic with true
span arithmetic, timeline-anchor-conflict with true anchor-drift detection). Increments 5–7 +
the contract/config/run-folder validators are planned.
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

| # | Track | Scope | Status |
|---|-------|-------|--------|
| **1** | A — Validator Hardening | `letter_checks.py` shared module + port **severity-floor**; fixture suite; degrade path; build-archive registration. | ✅ done |
| **2** | A | Port **decision-layer-check** (2a) + **audit-signal-propagation** incl. `--check-registry` (2b) onto `letter_checks.py`. | ✅ done |
| **3** | A | Port **underdiagnosis-triggers** (3a) + **ledger-consolidation** (3b) — completing the **editorial-letter / ledger** family (the five arms that take a letter or ledger; the regex-edge-case sources the reviews flagged). | ✅ done |
| **4** | A | `timeline_checks.py` + the three **timeline-** arms. `timeline-diff` faithfully ported; `timeline-arithmetic` / `timeline-anchor-conflict` gain **true** verification (span-overrun arithmetic; same-scene anchor drift) — the capability pass-10.md §Phase 7 deferred. The two `silent_*` cases that bash false-passed now fail. | ✅ done |
| **5** | A — other artifact families | `config_checks.py` + port the non-letter validators that operate on *different artifact types*: **quality-risk-triggers** (contract + sidecar), **audit-tier-criterion** (pass-dependencies + audits dir tree), **argument-recon-prerequisite** (run-folder scan). Their own module (not `letter_checks.py`) since they take paths/dirs and do filesystem I/O. Faithful ports (oracle-diff identical, incl. byte-identical output on the real `pass-dependencies.md`). | ✅ done |
| **6** | B — Release gate | Extend `validate.sh --check-all` to run validators against the *actual* canonical files: `audit-tier-criterion` vs the real `pass-dependencies.md`; `decision-layer-check` + `audit-signal-propagation` + `severity-floor` vs a new canonical worked-example letter; `timeline-arithmetic`/`-anchor-conflict`/`-diff` vs a new canonical worked-example Timeline. Both examples ship under `core-editor/references/` (`example-editorial-letter.md`, `example-timeline.md`) and double as docs. (The shipped sample letters are HTML renders and fail the markdown parsers, so canonical worked examples are gated instead.) Closes the deferred *Canonical-framework validator runs as release gate* item. | ✅ done |
| 7 | C — Contracts v2 completion | Schema the still-unschema'd artifacts so JSON Schema is source-of-truth for the whole set: Severity Calibration appendix entries (`apodictic.severity_calibration.v1`) and gate-event records. The calibration schema lets `softness-check` read structured data instead of parsing appendix prose — closing the loop with Track A. | next |

Increments 1–3 ship together as one PR (the coherent letter/ledger family); 4–7 follow as
separate stacked PRs (Cowork budgets; bounded blast radius), the same stack discipline used
for v2.0.0 #10–#14 and the harness work #18–#19.

**Scope note (boundary).** The "letter-validator family" is precisely the arms that take an
editorial letter or ledger. `quality-risk-triggers` (validates a *contract*),
`audit-tier-criterion` (validates *pass-dependencies* + walks an *audits directory*), and
`argument-recon-prerequisite` (scans a *run folder*) validate different artifact types and
were not the regex-edge-case sources, so they are deliberately a later, separate increment
rather than being forced into the letter-prose module.

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
