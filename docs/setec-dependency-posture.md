# SETEC dependency posture (APODICTIC ↔ SETEC Voiceprint)

**Status:** accepted decision note
**Date:** 2026-05-30
**Owner:** anotherpanacea (maintains both APODICTIC and SETEC Voiceprint)
**Scope:** how APODICTIC's SETEC-backed audits declare their dependency on SETEC, and how the integration contract is versioned and normalized.

---

## Context

APODICTIC is a writer-facing developmental-editing plugin (skill/prompt-first; runs on frontier models; no heavy runtime dependencies). SETEC Voiceprint is a Python stylometry/forensics framework with a heavy dependency stack (spaCy, scikit-learn, sentence-transformers, transformers/torch). A subset of APODICTIC's audits delegate their *computation* to SETEC over a subprocess boundary, parsing a `schema_version` 1.0 JSON envelope (`setec_runner.run_supplement` / `setec_discovery`).

The PR #6 review cycle (Narrative-Decision / Surface 6 integration) surfaced a cluster of integration bugs — version-floor skew (1.86.0 vs 1.107.0), `--json` vs `--json-out`, argparse prefix-matching, the private-output policy, the `--json-out=` equals form. They were all **contract-shape** drift, not **SETEC-absent** failures. That distinction drives this note: "require SETEC" and "stop the contract drifting" are *independent* problems, and they get separate decisions below.

These two tools have deliberately different use cases. That difference is the reason the subprocess boundary is correct: a writer running a structural edit should not have to install torch. The voice-computational audits are a **narrow bridge** between two separate worlds, and the goal is to keep that bridge explicit and small — not to fuse the tools or make all of APODICTIC depend on the Python stack.

---

## Decision 1 — Dependency posture is decided **per audit**, not globally

There is no blanket "voice work requires SETEC" rule. Each SETEC-touching audit is classified by whether its value is **computational** (only SETEC can produce it; no honest LLM substitute) or **judgment** (LLM reasoning; SETEC adds nothing).

| Audit / layer | SETEC surface(s) | Class | Posture |
|---|---|---|---|
| **Narrative-Decision (StoryScope)** | `narrative_decision_audit` | Computational | **Required.** No audit without SETEC. Hard prerequisite with a version floor and a clean upgrade-path failure. |
| **POV Voice Profile** | `pov_voice_profile`, `voice_distance`, `voice_profile` | Computational | **Required.** Stylometric distance *is* the audit. |
| **Idiolect Preservation** | `idiolect_detector` | Computational | **Required** for the keyness/collocation extraction. |
| **Punctuation Cadence** | `punctuation_cadence_audit` | Computational | **Required** for the per-mark/bigram stylometry. |
| **AI-Prose Calibration — Layer A** (distributional) | `variance_audit`, `manuscript_audit`, `repetition_audit` | Computational | **Required for Layer A only.** An LLM approximating burstiness / MATTR / MTLD is theater; do not fake it. |
| **AI-Prose Calibration — Layer B** (AIC pattern scan) | — | Judgment | **SETEC-independent.** Runs on the model alone. |
| **AI-Prose Calibration — Layer C** (source triage) | — | Judgment | **SETEC-independent.** Runs on the model alone. |

Two consequences fall out of the table:

- **For computational audits/layers, hard-require SETEC and fail cleanly.** Do not degrade a computational audit to an LLM "estimate" of a statistic — that produces confident, unfalsifiable numbers the claim-license discipline forbids. The narrative-decision shim already models this: it discovers at its version floor and exits with an install/upgrade message rather than pretending.
- **Do not blanket-require SETEC for "AI-Prose Calibration."** Its Layer B/C are genuinely useful without SETEC; losing only Layer A (the distributional pre-scan) when SETEC is absent is a *feature*. The audit degrades by dropping the computational layer and saying so, while the judgment layers stand.

**Graceful degradation applies to the *judgment* tier, not the *computational* tier.** The three-tier warnings classification in `setec_runner` (blocking / reliability / cosmetic) and the LLM-only fallback remain correct for judgment-tier supplementation; they are not a license to substitute for a missing computation.

**A computed value earns trust only by passing a plausibility bound — "SETEC ran" is not "SETEC is right."** The present/absent framing has a third state: SETEC present, the computation completes, but the number is invalid. (Empirically: a Tier-4 surprisal run on a DirectML backend returned 14–22 nats/token against a theoretical maximum of log │vocab│ ≈ 11.76 — a confident, precise, unfalsifiable, *wrong* value.) That is the LLM-estimate ban's failure mode arriving from the compute backend instead of from substitution, and the claim-license discipline forbids it either way. Computational surfaces must **self-validate their raw outputs against cheap bounds** (surprisal ≤ log │vocab│; cosine ∈ [−1, 1]; finite, correctly-shaped vectors) and emit a clean failure on violation. This generalizes the framework's existing **polarity-inversion gate**, which already refuses to publish a below-chance calibration rather than ship one that ranks backwards: an out-of-bounds computation is a clean failure, not a result.

---

## Decision 2 — Version floors are a property of the **surface**, discovered, not hardcoded per shim

Today each shim hardcodes its floor (texture surfaces 1.86.0; `narrative_decision_audit` 1.107.0), and `run_supplement` accepts a `min_version`. This works but duplicates per-surface knowledge across shims, docs, and the runner — the exact thing that drifted on PR #6.

- **Target state:** APODICTIC reads each surface's `{ min SETEC version, schema_version, JSON delivery mode, calibration status, handoff posture }` from a **SETEC capabilities query** (SETEC already maintains a capabilities manifest), and asserts floors from that data. Adding a surface then costs zero hardcoded constants.
- **Interim state (current):** per-shim floor constants + `run_supplement(min_version=...)`. Acceptable until the capabilities query lands; new surfaces must still set their floor explicitly and surface a clean upgrade message (`setec_discovery._install_instructions` is floor-aware).

---

## Decision 3 — Normalize the contract surface (separate from Decision 1)

Requiring SETEC does **not** fix drift; narrowing the contract does. The roadmap (tracked separately; not committed here) is to collapse N drifting per-script CLIs into one stable surface:

1. **Phase 1 (highest leverage):** SETEC exposes a machine-readable capabilities query; APODICTIC data-drives floors/flags from it. Retires version-skew and flag-spelling drift at the source.
2. **Phase 2:** a single normalized entrypoint (`setec run <surface> --json`) that always emits the envelope to **stdout** under one flag; `run_supplement` collapses to one code path and the `--json-out`/private-dir/equals-form branches disappear.
3. **Cross-cutting:** a **shared contract-test fixture set** (golden envelopes + a reference fake SETEC) committed to *both* repos, so each side's CI verifies conformance without installing the other. Every PR #6 finding would have been caught here pre-review.

---

## Non-goals

- **Do not fuse the tools** or vendor SETEC into APODICTIC. The subprocess boundary keeps the heavy dependency stack out of the writer-facing plugin; that isolation is intended.
- **Do not require the Python stack for all of APODICTIC.** Only the computational audits declare the dependency, and only when invoked.
- **Do not LLM-fake a computation.** A missing computational surface is a clean failure, never an approximation.
- **Do not emit an out-of-bounds computation.** A computed value that fails a cheap plausibility bound (e.g. surprisal exceeding log │vocab│) is a clean failure, not a number — the same discipline as "never an approximation," applied to the compute backend rather than to LLM substitution.

---

## How a new SETEC-backed audit declares its posture (checklist)

1. Classify it: **computational** (required) or **judgment** (independent / optional supplement)?
2. If computational: set the surface's **version floor** in its shim, route through `run_supplement(min_version=...)`, ensure the failure path gives an install/upgrade message (not a silent skip, not an LLM estimate), and confirm the surface **self-validates its output against plausibility bounds** — failing cleanly rather than emitting an out-of-bounds number.
3. If judgment: keep it SETEC-independent; if it *optionally* consumes a SETEC signal, treat the signal as reliability-tier supplementation that degrades per `setec_runner`'s three-tier rule.
4. Record the audit's row in the Decision 1 table above.
5. When the capabilities query (Decision 2 target) lands, drop the hardcoded floor in favor of the manifest value.

---

## Status of related items

- **Resolved:** `idiolect_detector` uses a real stdout `--json` mode, so its documented `run_supplement("idiolect_detector.py", …)` wiring needs no `json_out=True`. (It is still *computational* / required per Decision 1 — required ≠ file-based output.)
- **Open (future):** the Decision 3 capabilities query + normalized entrypoint + shared contract fixtures. A SETEC-side spec is the next artifact when that work is scheduled.
