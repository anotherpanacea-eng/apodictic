# Author Voice Profile — J. Marsh

<!-- author-voice-profile: local-only -->

<!--
Worked example of a contract-conformant Author Voice Profile (see author-voice-fingerprint.md +
docs/author-voice-fingerprint.md). The persistent NARRATIVE memory of a writer's voice across the
works they collect under one author-root: one apodictic.voice_fingerprint.v1 block per work, plus a
recomputed aggregate (author centroid + per-register range) and DESCRIPTIVE observations — drift,
range/growth, unconscious self-imitation, signature tics. It does no new stylometry; each fingerprint
consumes the single-voice AI-prose machinery (here `results.baseline_comparison`).

This file is exercised by `validate.sh --check-all` as a canonical release-gate target for
`author-fingerprint`, under `--strict`: F1 schema, F2 provenance (each fingerprint cites a
`source` + `centroid_ref`), F3 same-register comparison (the drift claim compares only the two
`literary-fiction` works), F4 descriptive-not-prescriptive (it observes movement, never says "fix
your voice" or assigns a Must/Should/Could severity), clean W1 (two same-register fingerprints
satisfy the >= 2 threshold), and clean W2 (the local-only marker is present; no external URL).
Observations only — the author judges whether a departure is intended.
-->

## Fingerprints

<!-- apodictic:voice_fingerprint
{"schema":"apodictic.voice_fingerprint.v1","id":"VF-2024-marsh","work_label":"Marsh Light (2024)","register":"literary-fiction","source":"ai-prose-baseline","centroid_ref":"results.baseline_comparison (single-voice voice_profile fit)","metrics":{"mattr_z":"-0.2","mtld_z":"0.1","burrows_to_author_centroid":"0.2"}}
-->

<!-- apodictic:voice_fingerprint
{"schema":"apodictic.voice_fingerprint.v1","id":"VF-2026-thornfield","work_label":"Thornfield (2026)","register":"literary-fiction","source":"ai-prose-baseline","centroid_ref":"results.baseline_comparison (single-voice voice_profile fit)","metrics":{"mattr_z":"-0.4","mtld_z":"0.2","burrows_to_author_centroid":"0.7"}}
-->

## Aggregate

- **Author centroid (literary-fiction):** recomputed from the two same-register works above.
- **Per-register range:** `literary-fiction` only so far; other registers will seed their own band as works are added. Drift is read only within a register.

## Drift & Range (observations — the author judges)

- **Drift.** VF-2026-thornfield sits 0.5 further from the author centroid than VF-2024-marsh
  (`burrows_to_author_centroid` 0.7 vs 0.2), just outside the same-register band — an intended
  departure, or drift? The profile surfaces the movement; the author decides which.
- **Range / growth.** The two `literary-fiction` works span a modest same-register range; too few
  works yet to read a trajectory.
- **Self-imitation.** No low-variance recurrence flagged across the two works — and were one to
  appear, it would be recorded as a feature-not-defect observation the author opts into caring about.

## Notes

- **No new stylometry.** Every fingerprint consumes the single-voice AI-prose fit
  (`results.baseline_comparison`); the module persists and diagnoses, it does not recompute features.
- **Same-register only.** Drift is compared strictly within `literary-fiction`; a cross-register
  comparison would be a domain-shift error (validator F3).
- **Descriptive, local-only.** These are observations, never prescriptions — the profile never tells
  the author to change their voice — and it is local-only: no external call, never transmitted.
