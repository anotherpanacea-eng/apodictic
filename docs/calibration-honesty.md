# calibration-honesty — an uncalibrated SETEC band must never be rendered as a verdict

**Status:** **Built** (the `calibration-honesty` `AGG_VALIDATORS` arm + `calibration_honesty.py` +
the canonical decision-audit-letter fixture; spec `apo-narrative-decision-residue` increment (c),
Opus build-review READY-AFTER-P1s, both P2s folded — this doc + the CS2 case-sensitivity fixture).
<!-- built-when: scripts/calibration_honesty.py -->

Both consumer decision-audit surfaces — `narrative_decision_audit` (StoryScope) and
`argument_decision_audit` (ArgScope) — ship `handoff: experimental` with an envelope
`aggregate.verdict_band: "uncalibrated"` and `thresholds: {low: null, high: null}`. The consumer-side
discipline — surface the band as **provenance only**, never as a calibrated verdict — was enforced
**entirely in prose** (the two audit docs' anti-verdict sections + four `pass-dependencies.md` rows).
No mechanical check existed that a decision-audit's human-facing rendering doesn't present the
uncalibrated band as calibrated. This validator is that check: the house
`claim-surface-asserts-it → enforce-it` posture applied to a claim the audits already make.

---

## D1 — What it checks

The reader-facing editorial letter, scanned **whole** and **per paragraph** (blank-line-delimited).
A paragraph is flagged only when a **claim shape** matches **and no qualifier is co-present** in that
same paragraph. Bare token presence (`band`, `threshold`, `verdict`) never fires on its own — that is
what keeps the mandated clean-path boilerplate and the vendored SETEC bundle labels safe (each carries
a qualifier or lacks a claim shape).

## D2 — Whole-letter, not region-scoped

Region-scoping was a false foundation: the only per-audit sectioner (`_audit_subsection`) scopes
**appendix** bodies, but decision-audit findings land in the **unscoped synthesis body**, and the
canonical letter fixture carries no decision-audit region at all. So the scan is whole-letter,
per-paragraph — the paragraph is the co-presence unit.

## D3 — The claim shapes (CS1–CS4)

| Shape | Fires on |
|---|---|
| **CS1** band-placement | "the manuscript scores in the AI-elevated band" — subject + placement verb + `in/into/within/at` + `band`, no qualifier |
| **CS2** calibrated-verdict | "calibrated verdict/band/score", or a bare `verdict:` / `verdict =` field |
| **CS3** threshold claim | "sits above the threshold" / "threshold of 0.4" — a comparative + `the/a/its threshold\|cut-off`, or a numeric threshold, on a thresholds-null surface |
| **CS4** aggregate-verdict | "the aggregate score confirms/proves/establishes/demonstrates …" — the score promoted to a verdict |

**CS2 case-sensitivity (deliberate).** CS2's bare-`verdict:` arm is case-**sensitive** by design: a
capitalized `**Verdict:**` / `## Readiness Verdict:` is a submission-readiness / severity-floor heading
(severity-floor's turf, see D5) and legitimately out of scope for the calibration-band check; only a
lower-case decision-audit `verdict:` field is CS2's target. `IGNORECASE` would false-fire on every
readiness verdict heading. A `**Verdict:**`-shaped negative fixture (`fx7b`) records this and fails if
the case-sensitivity is ever "fixed" away.

## D4 — Severity (the honest class)

This is an **open natural-language co-presence check**, not a closed literal scan, so its house class
is `content_advisory` W1 (prescriptive drift) / stance-consistency F4: **WARN by default, ERROR only
under `--strict`.** Failure direction is toward **not** firing — a missed leak is recoverable by the
human reader who owns the reading; a false ERROR would block a run on prose the doc itself mandates.
The honest claim (stated here and in the validator's `--help`): the guard closes the **enumerated**
claim shapes when unqualified; it does **not** claim to close every way prose can imply calibration.
Residual semantic leakage no vocabulary list can close is presented to a human — layered mechanism +
human terminus, not a proof.

**Override:** a per-instance prose override `<!-- override: calibration-honesty — <why> -->`, detected
via the shared `override_marker` SSoT (code-span-stripped, boundary-matched — M5), never a bare
substring.

## D5 — Ownership (one new arm; the three-way boundary, disclaimed not latent)

- **`severity-floor`** (`letter_checks`) owns whole-letter verdict-band-vs-flags honesty for the
  **submission-readiness** vocabulary (`_HIGH_VERDICT_RE` = Strong Fit / publishable as-is / Highest
  Band / Excellent Fit), policed against flag volume. **Named overlap + disclaimer:** both validators
  scan letter-wide verdict-adjacent vocabulary; the two vocabularies are and must remain **disjoint** —
  no CS pattern matches the four readiness tokens (the readiness-disjointness self-test asserts a legal
  readiness sentence does not fire calibration-honesty), and calibration-honesty never reads flag counts.
- **`honesty_check`** (softness-check / deficit-lock) owns locked-severity delivery. It says nothing
  about calibration bands.
- **`calibration-honesty`** (this arm) owns per-audit calibration-**provenance** rendering — an
  uncalibrated SETEC band presented as calibrated. It never reads severities, never gates tiers, never
  touches the §4e propagation logic.

## D6 — Cross-surface

The guard covers **both** decision-audits and is surface-agnostic: nothing keys on the audit name, so
a future uncalibrated `handoff: experimental` consumer surface inherits it by construction.

---

## Vocabulary home

The severity-token SSoT (`severity_vocab.SEVERITY_TOKEN_RE`, meta-lint M8) is the Must/Should/Could-Fix
leak token — a **different** vocabulary that this guard does not use (it reads calibration-band prose,
not editorial-severity prose). The CS shapes, qualifier set, and allowlist are **this guard's own** new
vocabulary and live in `calibration_honesty.py`; M8 does not apply (no `(?:Must|Should|Could)`
alternation is re-compiled). This is a deliberate divergence from the spec's R-3 (which proposed homing
the constants in `severity_vocab.py`): M8's SSoT governs only the editorial-severity token this guard
never touches, so folding an unrelated vocabulary into that lean single-export module would blur the
SSoT boundary. Confirmed by the Opus build-review.

## Run

```
validate.sh calibration-honesty <run_folder|files...> [--strict]
calibration_honesty.py --self-test
```

Exit: 0 clean / WARN-only · 1 ERROR (WARN under `--strict`) · 2 usage / no artifact.
