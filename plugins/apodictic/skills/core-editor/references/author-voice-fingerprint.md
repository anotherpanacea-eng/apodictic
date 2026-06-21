# Cross-Manuscript Author Voice/Craft Fingerprint — the writer's signature, tracked over a career

*Reference module for the APODICTIC Core Editor. A persistent profile that accumulates across the
works an author collects under one author-root and surfaces movement — drift, range/growth,
unconscious self-imitation, signature tics. It does **no new stylometry**: it consumes the existing
single-voice machinery and adds the persistence-and-longitudinal-diagnosis layer. Spec + validator:
`docs/author-voice-fingerprint.md`, `scripts/validate.sh author-fingerprint`. Worked example:
`example-author-voice-profile.md`.*

---

## When to use

When an author wants a memory of their voice *across* works — has it drifted, grown, or settled
unconsciously into the same cadence book after book? APODICTIC measures voice *within* a manuscript
(Pass 11 Voice Distinctiveness; the AI-prose personal-baseline z-scores); this is the cross-work
layer the framework otherwise lacks. It is privacy-sensitive — a career voice profile is the most
sensitive artifact the framework could hold — so it is **local-only** and **operator-curated**.

## Persistence — an operator-curated author-root (not automatic, not global)

There is **no cross-project or machine-global state** in the framework, and writing state into the
framework directories is forbidden. This module follows the `Series_State.md` convention exactly: the
`Author_Voice_Profile.md` lives at an **author-root the operator designates**, under which the author
collects the works they want compared. It does **not** auto-discover unrelated projects and claims no
global author registry — the honest phrasing is "across works the author collects into one
author-root," not "automatically accumulates across all your books."

## Consume, don't duplicate — the single-voice fit

The author centroid and the personal-baseline signals come from the **single-voice AI-prose
machinery** (SETEC `voice_profile` / `voice_distance` + the personal-baseline MATTR/MTLD/entropy
z-scores). The POV Voice Profile fits per-POV-*character* and refuses single-POV work, so it produces
no author centroid — it is kept only for the optional protagonist-collapse sub-diagnostic. This module
**persists and diagnoses**; it computes no features.

## The persistent artifact

An `Author_Voice_Profile.md` (under the author-root) of `apodictic.voice_fingerprint.v1` blocks — one
per work — plus a recomputed aggregate (author centroid + per-register range) and descriptive
observations:

```markdown
<!-- author-voice-profile: local-only -->

<!-- apodictic:voice_fingerprint
{
  "schema": "apodictic.voice_fingerprint.v1",
  "id": "VF-2026-thornfield",
  "work_label": "Thornfield (2026)",
  "register": "literary-fiction",
  "source": "ai-prose-baseline",
  "centroid_ref": "results.baseline_comparison (single-voice voice_profile fit)",
  "metrics": { "mattr_z": "-0.4", "burrows_to_author_centroid": "0.7" }
}
-->
```

- `register` — the comparability class; drift is compared **only within** a register (the AI-prose
  domain-shift caution).
- `source` ∈ `ai-prose-baseline` / `voice-distance` / `pov-voice-profile` (the last only for the
  protagonist-collapse sub-diagnostic).
- `centroid_ref` — names the consumed audit output (the metric *keys* are illustrative; the
  authoritative shapes live in SETEC's output, so provenance is presence-checked, not re-resolved).
- `metrics` — a flat map of scalar values.

## What it diagnoses (descriptive — the author judges)

All **observations, not verdicts**: **Drift** (a work's distance to the author centroid exceeds the
same-register band → "intended departure, or drift?"), **Range/growth** (the spread of same-register
centroids over time), **Unconscious self-imitation** (low cross-work variance where works are meant to
differ — framed as a feature-not-defect the author opts into caring about), **Signature tics**
(features persistently extreme across works). It reports movement; it never tells the author to change
their voice, and a fingerprint carries no Must/Should/Could severity (a fingerprint is not a defect).

## Validation

`validate.sh author-fingerprint <author_root|files...> [--strict]` runs: **F1** schema (incl. a
non-empty, scalar-valued `metrics`), **F2** provenance (each fingerprint cites a `source` +
`centroid_ref`), **F3** same-register comparison (a drift/range claim referencing ≥2 fingerprints
must share a register — the domain-shift guard), **F4** descriptive-not-prescriptive (no
Must/Should/Could token, no "fix your voice" directive; advisory, ERROR under `--strict`; override
`<!-- override: fingerprint-frame VF-… — <why> -->`), **W1** insufficient data (no register has ≥2
fingerprints → seed-only; advisory), and **W2** local-only hygiene (a missing `local-only` marker or
an external URL — **advisory WARN only**, never gate-blocking: the binding privacy guarantee is the
module's runtime no-external-call rule, which a marker scan cannot prove). See
`docs/author-voice-fingerprint.md`.
