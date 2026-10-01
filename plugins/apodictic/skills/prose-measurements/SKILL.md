---
name: prose-measurements
description: >
  AI-prose calibration, narrative/argument decision signals, idiolect preservation, punctuation cadence, POV voice profiles, and experimental position-pair measurements. Optional SETEC execution is required for mechanical measurements.
  Use when the user requests one of these focused audits. For the complete
  audit catalog or an unclear request, use specialized-audits.
version: 2.13.3
---

# Prose and Structural Measurements

Load `../core-editor/references/focused-audit-contract.md` for the shared execution, output, and severity contract.
Select the requested protocol below and read it in full. Load its named
companions and level-setting references when called for; do not load every
protocol in this family. Preserve all flags, gates, register/genre calibrations,
prerequisites and claim limits in the selected protocol. This skill diagnoses;
it does not rewrite manuscript prose.

Paths beginning `references/` or `scripts/` in these protocols resolve from
this skill directory. Paths naming another skill resolve from the shared
`skills/` directory; `../` links resolve from this skill directory.

| Request / command alias | Task | Protocol |
| --- | --- | --- |
| `ai-prose` | **AI-Prose Calibration** — voice singularity, lexical genericism, echo stacks, register seams | `references/craft/ai-prose-calibration.md` |
| `narrative-decision` | **Narrative-Decision (StoryScope)** — structure-level AI tells, 33 narrative-decision signals, per-signal contributions | `references/craft/narrative-decision-audit.md` |
| `argument-decision` | **Argument-Decision (ArgScope)** — structure-level argument AI tells, B1 paragraph-role arc + B2 discourse-mode mix, per-signal contributions | `references/craft/argument-decision-audit.md` |
| `pov-voice-profile` | **POV Voice Profile** — per-POV voice signatures and distance discipline (opt-in) | `references/craft/pov-voice-profile.md` |
| `idiolect` | **Idiolect Preservation** — Opt-in; retain the protocol's calibration and claim limits. | `references/craft/idiolect-preservation.md` |
| `punctuation-cadence` | **Punctuation Cadence** — Opt-in; retain the protocol's calibration and claim limits. | `references/craft/punctuation-cadence.md` |
| `position-pair-register` | **Position-Pair Register** — Opt-in; retain the protocol's calibration and claim limits. | `references/craft/position-pair-register.md` |

## Optional measurement execution

Keep editorial calibration separate from automated measurement. Run bundled
helpers only with the user's selected inputs and workspace output paths.
Use a trusted SETEC installation the user has selected; discovery candidates
do not authorize arbitrary execution. Do not install software or run downloaded
commands automatically. If execution, dependencies, baselines, an LLM judge,
or a compatible SETEC installation are missing, disclose N/A rather than
inventing scores. Retain uncalibrated/register-distance and anti-verdict
warnings: no measurement establishes authorship, argument soundness or prose
quality by itself. The SETEC script group and vendored client stay colocated
under `scripts/`; research lookups belong to `../research-verification/SKILL.md`.
