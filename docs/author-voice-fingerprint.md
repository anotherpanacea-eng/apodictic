# Cross-Manuscript Author Voice/Craft Fingerprint — the writer's signature, tracked over a career

**Status:** **Built (Increment 1), 2026-06-20.** Shipped: the `apodictic.voice_fingerprint.v1` schema, the `core-editor/references/author-voice-fingerprint.md` module, the operator-curated `Author_Voice_Profile.md` artifact, `scripts/author_fingerprint.py` + `validate.sh author-fingerprint` (F1–F4 + W1–W2), and the canonical `example-author-voice-profile.md` (two `literary-fiction` fingerprints, one within and one just outside the same-register band) wired into `--check-all` under `--strict`. Self-testable validators 51 → 52. **Build notes:** the validator count is **derived** from `validate.sh`'s `AGG_VALIDATORS` list (not a hand-maintained number); the module is homed in **core-editor** (not specialized-audits — it is a derived deliverable, not a craft audit); **F3** is mechanized as "a prose claim referencing ≥2 fingerprint ids must share a register" (the continuity-bible C3 shape); **F4** scans the visible reader-facing prose and a single `fingerprint-frame` override silences the family (prose is not id-addressable). Roadmap: `ROADMAP.md` → [Horizon Capacities](../ROADMAP.md#horizon-capacities) Tier 1, item 9.
<!-- built-when: scripts/author_fingerprint.py -->

A writer's voice changes over a career — sometimes by growth, sometimes by drift, sometimes by an unconscious settling into the same cadence book after book. APODICTIC can already measure voice *within* a manuscript, but it has no memory *across* a writer's body of work. This capability is that memory: a persistent fingerprint that accumulates across the works an author **collects into one profile** and surfaces movement.

It does **no new stylometry** — it consumes the existing single-voice stylometric machinery and adds the persistence-and-longitudinal-diagnosis layer on top.

## Consume, don't duplicate — the right source is the single-voice fit

The first draft of this spec named the wrong consume source. The corrected mapping:

| Existing surface | What it computes | This module's relationship |
|---|---|---|
| **AI-Prose distributional layer** — SETEC `voice_profile.py` ("private stylometric profile from a writer/register baseline") + `voice_distance.py` (Burrows Delta vs. a baseline) | a **single-voice author stylometric profile** treating the manuscript as one voice, and the distance between a work and a baseline | **primary consume** — the per-work *author* centroid is the single-voice `voice_profile` fit; cross-work distance is `voice_distance`'s Burrows Delta |
| **AI-Prose personal-baseline z-scores** (`results.baseline_comparison`: MATTR/MTLD/entropy/… z vs. the writer's own corpus) | how a work sits against the writer's own prior-work baseline | **primary consume** — these *are* cross-work author measurements |
| **POV Voice Profile** (`results.povs[*].centroid`, per **POV-character**) | per-POV-character voiceprints; refuses single-POV work | **secondary, optional** — used **only** for the cross-work *protagonist-collapse* sub-diagnostic (do successive protagonists share a voice?), **not** for the author centroid. It produces no author-level centroid and nothing at all on single-POV work, so it is the wrong source for the author signature. |
| Pass 11 Voice Distinctiveness; `Series_State` | single-work voice; same-series story facts | **distinct** — single-work / same-series |

So the author centroid and the personal-baseline signals come from the **single-voice AI-prose machinery**; POV Voice Profile is demoted to an optional input for one sub-diagnostic. This module **persists and diagnoses**; it computes no features.

## Persistence — an operator-curated author-root (not automatic, not global)

There is **no cross-project or machine-global state** in the framework: the hard rule is never to write state into the plugin/framework directories, and `Series_State.md` is **not** cross-project — it works only because the operator gathers one series' volumes under a single series-root. This module follows that exact convention: `Author_Voice_Profile.md` lives at an **author-root the operator designates** (`--author-profile <path>`), under which the author collects the works they want compared. It does **not** auto-discover unrelated projects, and it does **not** claim a global author registry. The honest phrasing is therefore "across works the author collects into one author-root," mirroring the series-root model — not "automatically accumulates across all your books."

## The persistent artifact

One `apodictic.voice_fingerprint.v1` block per work under the author-root, plus a recomputed aggregate (author centroid + per-register range):

```markdown
<!-- apodictic:voice_fingerprint
{
  "schema": "apodictic.voice_fingerprint.v1",
  "id": "VF-2026-thornfield",
  "work_label": "Thornfield (2026)",
  "register": "literary-fiction",
  "source": "ai-prose-baseline",
  "centroid_ref": "results.baseline_comparison (single-voice voice_profile fit)",
  "metrics": { "mattr_z": "-0.4", "mtld_z": "0.2", "burrows_to_author_centroid": "0.7" }
}
-->
```

- `register` — comparability class; drift compared **only within** a register (`F3`), per the AI-prose domain-shift caution.
- `source` ∈ `ai-prose-baseline` / `voice-distance` / `pov-voice-profile` (the last only for the protagonist-collapse sub-diagnostic).
- `centroid_ref` — points into the consumed audit's output (`results.baseline_comparison` for the single-voice fit). **The `metrics` keys shown are illustrative**; the authoritative key shapes live in SETEC's output schema, so `F2` checks provenance *presence*, not the exact value path.
- `metrics` — a flat map; subset engine types the container as `object`, per-key checks are Python (the `retcon_plan.scores` precedent).

## What it diagnoses (descriptive — the author judges)

All **observations, not verdicts** (observations-not-judgments coaching stance):
- **Drift** — `burrows_to_author_centroid` exceeds the same-register band → "intended departure, or drift?"
- **Range / growth** — spread of same-register centroids over time.
- **Unconscious self-imitation** — low cross-work variance where works are meant to be distinct, **framed as a feature-not-defect observation** the author opts into caring about (`F4`); grounded in the same discipline as `idiolect-preservation` ("does not adjudicate whether a recurrence is convergence or signature").
- **Signature tics** — features persistently extreme across works.

## Firewall, severity, privacy

- **Measure, never prescribe.** It reports movement; it never tells the author to change their voice. `F4` flags prescriptive phrasing — but, like its peers (`legal_risk`/`editor-scaffolding` W1), it is a **narrow lexical heuristic** that catches Must/Should/Could tokens and a small imperative set and **will miss soft prescription** ("you might open up your cadence"); the spec does not claim airtight enforcement.
- **Orthogonal severity.** A fingerprint is not a defect; no Must/Should/Could (the Legal Risk / Content Advisory orthogonality precedent).
- **Privacy — local-only (runtime mandate).** A career voice profile is the most privacy-sensitive artifact the framework could hold; the module's binding rule is **make no external call and never transmit the profile** (the no-telemetry / no-instrumentation-while-private commitment). `W2` is only a **partial, advisory** self-attestation check (a local-only marker + no-external-URL scan) — it cannot detect a runtime call, so it stays WARN-only and is **not** escalated to a strict gate; the real guarantee is the module's runtime rule, asserted in prose, not a pretended URL check.

## The `author-fingerprint` validator

`validate.sh author-fingerprint <author_root>` resolves `Author_Voice_Profile.md` under the designated author-root. Delegates to `scripts/author_fingerprint.py`; degrades to advisory `WARN` without `python3`. Report lines namespaced `author-fingerprint:<ID>`. Aggregation + drift band are Python; SETEC supplies the stylometry.

| ID | Severity | Rule |
|---|---|---|
| **F1 — schema** | ERROR | Each `voice_fingerprint.v1` parses; `work_label`/`register`/`source` present; `source` ∈ {ai-prose-baseline, voice-distance, pov-voice-profile}; `metrics` is an object. (Enum/container: subset engine; per-metric value shape: Python.) |
| **F2 — provenance** | ERROR | Every fingerprint carries `source` + `centroid_ref` naming a consumed audit output. Presence-checked (the external value can't be re-resolved here, like the deferred-locus pattern) — the module consumes; it does not compute its own stylometry. |
| **F3 — same-register comparison** | ERROR | Any drift/range diagnostic compares only fingerprints sharing a `register` — the AI-prose domain-shift guard. |
| **F4 — descriptive, not prescriptive/defect (firewall)** | WARN (ERROR under `--strict`) | A fingerprint/diagnostic carries a Must/Should/Could token or prescriptive phrasing ("you should vary/tighten/expand", "fix your voice"). Narrow lexical heuristic (catches lexicalized forms only); override `<!-- override: fingerprint-frame VF-… — <rationale> -->`. |
| **W1 — insufficient data** | WARN (ERROR under `--strict`) | Fewer than 2 same-register fingerprints; drift/growth/self-imitation suppressed (seed-only). A first work legitimately just seeds. |
| **W2 — local-only (advisory)** | WARN | The profile lacks the local-only marker or references an external URL. **WARN only** (a self-attestation hygiene check, not gate-blocking); the binding guarantee is the module's runtime no-external-call rule. |

**Ownership boundary.** `author-fingerprint` owns the **cross-work author-profile contract**: per-work fingerprint hygiene, provenance to a consumed stylometric source, the same-register guard, the descriptive-not-defect framing, and the local-only hygiene marker — classes no other validator raises. It does **not** compute stylometry (the SETEC single-voice tools do), diagnose within-manuscript voice (Pass 11), or track story facts (`Series_State`).

## Canonical `--check-all` gate

A worked example — an author-root `Author_Voice_Profile.md` with two `literary-fiction` fingerprints (each citing an `ai-prose-baseline` single-voice source), one within and one just outside the same-register band — is added, and `validate.sh --check-all` runs `author-fingerprint` against it: proving provenance (`F2`), same-register comparison (`F3`), a clean descriptive scan (`F4`), and that two same-register works satisfy `W1`. **Negatives**: a fingerprint with a "Must-Fix" token (fails `F4`) and a cross-register drift claim (fails `F3`). (The "canonical-framework validator runs as release gate" discipline, `ROADMAP.md` §Deferred.)

## Increment plan

**Increment 1 (this spec):** the `apodictic.voice_fingerprint.v1` schema (added to `schemas/`, auto-discovered by `known_schema_ids()`), the module (consume the single-voice `voice_profile`/`voice_distance` fit + personal-baseline z-scores; persist per-work fingerprints under the operator-designated author-root; diagnose drift/range/self-imitation/tics descriptively), `scripts/author_fingerprint.py` + `validate.sh author-fingerprint`, the worked example, and the `--check-all` gate. Adds one validator (hand-maintained count bumped).

**Future increments (not built):**
- **Fingerprint visualization** — the author's per-work centroid trajectory via [Manuscript-Structure Visualizations](manuscript-visualizations.md).
- **Coaching handoff** — feed a drift observation into the planned cross-session [Coaching History](../ROADMAP.md#coaching-deepening) (observations, not judgments).
- **Register-aware auto-baseline** — serve AI-prose calibration's requested "custom baseline (their own prior work in the same register)" from this profile, closing the loop with the personal-baseline machinery it consumes.

## Self-review (Increment 1)

- *Why the single-voice fit, not POV Voice Profile* — POV Voice Profile fits per-POV-*character* and refuses single-POV work, so it produces no author centroid for the central single-protagonist case; the author signature comes from the single-voice `voice_profile`/`voice_distance` fit + personal-baseline z-scores. POV Voice Profile is kept only for the optional protagonist-collapse sub-diagnostic.
- *Why an operator-curated author-root* — the framework has no global/cross-project state and forbids writing to framework dirs; the only honest persistence is the series-root convention applied to an author-root the operator designates. "Automatically accumulates across your books" overstated the filesystem model.
- *Why W2 stays advisory* — a self-attestation marker can't detect a runtime call; escalating it to a strict gate would fake enforcement. The real privacy guarantee is the runtime no-external-call rule.
- *Why self-imitation is an observation* — a consistent voice is a hallmark, not a flaw; `F4` and the `idiolect-preservation` precedent keep it descriptive, the author judging intent.
