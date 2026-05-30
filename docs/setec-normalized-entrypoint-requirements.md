# SETEC normalized-entrypoint — consumer requirements (APODICTIC → SETEC)

**Status:** consumer requirements / request. Input to a SETEC-side implementation spec; not a commitment from SETEC's side.
**Date:** 2026-05-30
**Direction:** APODICTIC (consumer) → SETEC Voiceprint (producer).
**Owner:** anotherpanacea (maintains both).
**Companion:** `docs/setec-dependency-posture.md` (per-audit required/optional classification). This doc is the contract-shape half; that doc is the dependency-posture half.

---

## Why this exists

APODICTIC consumes SETEC stylometry surfaces over a subprocess boundary, parsing a `schema_version` 1.0 JSON envelope (`setec_runner.run_supplement` / `setec_discovery`). The PR #6 integration cycle surfaced a cluster of bugs that were all **contract-shape drift**, not absent-SETEC failures:

- version-floor skew (1.86.0 framework floor vs 1.107.0 for `narrative_decision_audit`), hardcoded per shim;
- `--json` (stdout) vs `--json-out <path>` (file) inconsistency across surfaces;
- argparse prefix-matching (`--json` silently binding to `--json-out`);
- the default-private output policy refusing `--json-out` paths outside `ai-prose-baselines-private/`;
- the `--json-out=PATH` equals form not being recognized by the consumer.

Each was a separate copy of "this surface behaves differently, and the consumer has to know it." This request asks SETEC to expose **one normalized surface** so APODICTIC discovers per-surface facts instead of hardcoding them, and integrates against a single invocation + output shape.

This is the reverse of the StoryScope handoff: there, SETEC told APODICTIC what it ships; here, APODICTIC states the interface it needs SETEC to expose.

---

## Surfaces in scope

The surfaces APODICTIC consumes today (via shims that forward to SETEC scripts):

| APODICTIC shim | SETEC script / surface | Current floor | Current JSON delivery |
|---|---|---|---|
| `ai_prose_variance_audit.py` | `variance_audit.py` | 1.86.0 | stdout `--json` |
| `ai_prose_manuscript_audit.py` | `manuscript_audit.py` | 1.86.0 | stdout `--json` |
| `ai_prose_repetition_audit.py` | `repetition_audit.py` | 1.86.0 | stdout `--json` |
| `ai_prose_voice_distance.py` | `voice_distance.py` | 1.86.0 | stdout `--json` |
| `ai_prose_voice_profile.py` | `voice_profile.py` | 1.86.0 | stdout `--json` |
| `ai_prose_pov_voice_profile.py` | `pov_voice_profile.py` | 1.86.0 | **file `--json-out`** |
| `ai_prose_punctuation_cadence.py` | `punctuation_cadence.py` | 1.86.0 | stdout `--json` |
| `ai_prose_idiolect_detector.py` | `idiolect_detector.py` | 1.86.0 | stdout `--json` |
| `ai_prose_narrative_decision_audit.py` | `narrative_decision_audit.py` | **1.107.0** | stdout `--json` |

The inconsistencies above (one surface on `--json-out`, one floor at 1.107.0) are exactly the per-surface knowledge that should move into a discoverable manifest + a uniform invocation.

---

## What APODICTIC needs

### R1 — A machine-readable capabilities query

A stable command emitting, per surface, the facts the consumer needs to decide whether/how to call it and how to validate the result:

`setec capabilities --json` (all surfaces) and/or `setec describe <surface> --json` (one surface), returning at minimum:

```jsonc
{
  "setec_version": "1.110.0",
  "surfaces": {
    "narrative_decision_audit": {
      "surface": "narrative_decision_audit",
      "min_setec_version": "1.107.0",   // the floor — consumer asserts against this, never hardcodes
      "schema_version": "1.0",          // envelope contract version
      "handoff": "experimental",        // stable | experimental
      "calibration_status": "literature_anchored",
      "json_delivery": "stdout",        // see R2 — target is uniformly "stdout"
      "inputs": [                        // enough to build the arg list without guessing
        {"flag": "--manifest", "type": "path", "required": false},
        {"flag": "--judge", "type": "enum", "values": ["manifest","mock","anthropic","openai","gemini"]}
      ],
      "consumers": ["apodictic"]
    }
    // ... one entry per surface ...
  }
}
```

This single command retires version-skew and flag-spelling drift: APODICTIC reads `min_setec_version` and `inputs` instead of hardcoding `(1, 107, 0)` and flag strings in a shim.

### R2 — One normalized invocation, stdout-only envelope

A single dispatch form that wraps per-script quirks:

`setec run <surface> [surface args] --json`  → writes the `schema_version` envelope to **stdout**, for **every** surface.

- The consumer envelope always goes to stdout under one flag (`--json`). No `--json-out` file dance on the integration path; no argparse prefix-matching ambiguity; no equals/split-form variance for the consumer to handle.
- **Artifact / private outputs stay separate from the consumer envelope.** Voice-cloning artifacts (POV voiceprints, idiolect baselines) remain governed by SETEC's default-private policy and `--json-out`/`ai-prose-baselines-private/` as an *internal* concern; they must not be the only way to retrieve the consumer envelope. (This is the specific thing that broke `pov_voice_profile` for us — the envelope and the private artifact were conflated.)

### R3 — Structured error model

Failures should be parseable, not argparse text on stderr + ad-hoc exit codes:

- A failed run returns an envelope with `available: false` and a machine-readable `reason` + `reason_category` (e.g. `version_floor`, `missing_dependency`, `bad_input`, `text_too_short`, `policy_refused`), plus human text.
- A documented, stable exit-code scheme (e.g. 0 success, 2 discovery/version, 3 contract/usage), so the consumer can branch without scraping stderr.
- Version-floor failures report the **requested** floor (not a default), so the message is never self-contradictory (the bug we fixed in `setec_discovery._install_instructions`).

### R4 — Version & compatibility semantics

- `schema_version` is **the** contract; additive-only within a major; any breaking change bumps it and is announced via the capabilities manifest (R1), not discovered by a consumer crashing.
- Per-surface `min_setec_version` lives in the manifest; the entrypoint refuses an out-of-floor surface with an R3 structured error.

### R5 — Shared contract-test fixtures

A fixture set (golden envelopes per surface + a reference "fake SETEC" harness) committed to **both** repos, so each side's CI verifies conformance **without installing the other**. APODICTIC has hand-rolled the same fake `pov_voice_profile.py` three times during review; that harness should be a shared, versioned fixture. This is what would have caught every PR #6 finding before review.

---

## Acceptance criteria (consumer view)

When R1–R5 land, APODICTIC should be able to:

- **Delete per-shim version-floor constants.** `setec_discovery` reads `min_setec_version` from the capabilities query (R1) instead of `MIN_SETEC_VERSION = (1, 107, 0)` per shim.
- **Collapse `run_supplement` to one code path.** The `json_out` parameter, the `--json-out` injection, the `ai-prose-baselines-private/` temp-dir handling, and the `--json-out=`/split-form recovery all disappear — there is one stdout path (R2).
- **Reduce shims to a thin `setec run <surface>` call** (or remove them).
- **Branch on errors structurally** (R3) rather than matching warning strings / exit codes.
- **Add a new SETEC-backed audit with zero hardcoded per-surface knowledge** — floor, inputs, posture all come from R1.

---

## Phasing (consumer adoption order)

1. **Phase 1 — capabilities query (R1).** Highest leverage, lowest cost: APODICTIC data-drives floors/flags from the manifest while still calling existing scripts. Retires version-skew and flag drift even before the dispatcher exists.
2. **Phase 2 — normalized entrypoint (R2) + structured errors (R3).** `run_supplement` collapses to the single stdout path; the `--json-out` family of branches is removed.
3. **Cross-cutting — shared fixtures (R5).** Land alongside Phase 1 so conformance is CI-verified from the start.

R4 semantics apply throughout.

---

## Non-goals

- Not asking SETEC to drop `--json-out` / the private-output policy for **artifacts** — only to stop making the consumer envelope reachable *solely* through it.
- Not asking to merge the tools or change the subprocess boundary; the boundary is intentional (keeps SETEC's heavy deps out of the writer-facing plugin).
- Not asking SETEC to take on APODICTIC's claim-license / verdict semantics; those stay consumer-side.

---

## Open questions for SETEC

1. **Capabilities source.** SETEC already maintains a capabilities manifest (`capabilities.yaml` / `capabilities.py`). Can `setec capabilities --json` emit it directly, or is a normalization layer needed?
2. **Dispatcher vs. per-script.** Is a single `setec run <surface>` dispatcher preferred, or would normalizing each existing script's flags (uniform stdout `--json`, no prefix-match ambiguity) be a smaller change with the same consumer benefit?
3. **Envelope-vs-artifact split for private surfaces.** For `pov_voice_profile` / `idiolect_detector`, what's the cleanest way to return the consumer envelope on stdout while keeping the voice-cloning artifact under the private-output policy?
4. **Error model surface.** Is `available: false` + `reason_category` in the envelope sufficient, or should there also be a distinct typed-error envelope for pre-run failures (bad surface name, version floor)?
5. **Fixture ownership.** Where do the shared golden envelopes live so both repos' CI can consume them without a circular dependency?

---

## Status

- **Filed:** 2026-05-30 (APODICTIC consumer side).
- **Next artifact:** a SETEC-side implementation spec (authored in the `setec-voiceprint` repo, where the CLI surface, capabilities manifest, and producer-side fixtures live) that answers the open questions and maps R1–R5 onto SETEC's internals.
- **No SETEC-side commitment implied.** APODICTIC continues to function against the current per-surface contract (with the per-shim floors and the `json_out` handling shipped in v1.11.0) until/unless this lands.
