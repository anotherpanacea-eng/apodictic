---
name: narrative-craft-audits
description: >
  Focused manuscript audits of stakes, decisions, scene turns, character, emotion, interiority, literary craft, compression, and series structure.
  Use when the user requests one of these focused audits. For the complete
  audit catalog or an unclear request, use specialized-audits.
version: 2.13.3
---

# Narrative Craft

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
| `stakes` | **Stakes System** — pressure architecture, escalation geometry, consequence engine | `references/craft/stakes-system.md` |
| `decision-pressure` | **Decision Pressure** — choice plausibility, option visibility, tradeoff reality | `references/craft/decision-pressure.md` |
| `scene-turn` | **Scene Turn** — scene-level mechanics, entry/exit charge, turns (Bickham) | `references/craft/scene-turn.md` |
| `character` | **Character Architecture** — psychology engine, arc types, agency, voice | `references/craft/character-architecture.md` |
| `emotional-craft` | **Emotional Craft** — emotional precision, earned moments | `references/craft/emotional-craft.md` |
| `series` | **Series & Composite Novel** — standalone function, hope calibration | `references/craft/series-composite-novel.md` |
| `interiority` | **Interiority Preservation** — POV interiority in high-intensity scenes | `references/craft/interiority-preservation.md` |
| `female-interiority` | **Female Interiority** — agency, desire, independence | `references/craft/female-interiority.md` |
| `literary-craft` | **Literary Craft** — load-bearing vs. ornamental prose, defamiliarization, hybrid calibrations | `references/craft/literary-craft.md` |
| `banister` | **Banister (Epistemic Humility)** — rhetorical fairness, straw opposition | `references/craft/banister.md` |
| `force` | **Force Architecture** — force delivery, consequence/escalation tracking, inert force diagnosis | `references/craft/force-architecture.md` |
| `short` | **Short Fiction** — compression, single-effect, ending resonance | `references/craft/short-fiction.md` |
| `compression` | **Compression** — expendable material, cut list, word-savings map | `references/craft/compression-audit.md` |
| `series-continuity` | **Cross-Volume Series Continuity** — consequence propagation, state tracking, thread inventory, hope calibration across volumes | `references/craft/series-continuity.md` |

## Universal-status rationale


**Universal-status criterion (Phase 6 Wave 3 / Priority 5).** An audit earns universal status when **all three** hold: (1) the audit catches a class of failure that any narrative manuscript can exhibit regardless of genre, length, or form; (2) the audit produces material findings on cross-genre fixture coverage at a rate sufficient to justify default-on routing; (3) the audit is computationally cheap relative to its information yield (deferring it to opt-in would lose more diagnostic signal than the routing cost saves). Audits not meeting all three drop to Auto-recommend or Recommend tier per `core-editor/references/pass-dependencies.md §4c` Audit Tier Promotion Criteria.

**Universal status verification (2026-04-25, Phase 6 Wave 3).** Stakes System / Decision Pressure / Scene Turn re-audited against fixture coverage per Phase 6 plan §Priority 5. Outcome: **Outcome A — keep universal**. Verification basis:

- **Cross-model parity (Phase 3 §17):** Both Opus and Codex correctly fire all three audits on parity sets. The cross-model evidence shows the universal-status routing produces consistent material findings regardless of model capability variance.
- **Cross-fixture material findings:** All three audits produced material findings on the cross-genre fixture set (F1/F2 Stage 2 — fiction, novella-length; F3 — short fiction; F4 Stage 2 — argument-shaped nonfiction; the cross-model comparison's "3 universal skipped for fixture parity" was a procedural choice for the cross-model comparison protocol, not a finding-of-no-material-output). Stakes and Decision Pressure apply across all three forms (fiction and argument-shaped nonfiction both need pressure architecture and choice plausibility); Scene Turn applies fully to fiction fixtures and at reduced scope to argument-shaped runs (it surfaces narrative-section turns inside argument-shaped pieces with embedded scene work — case studies, vignettes, narrative ledes — without over-firing on purely propositional sections).
- **Computational cost:** The three universal audits run inside the same context as the passes that surface their finding-triggers (Pass 1 / Pass 5 / Pass 7); marginal cost is low relative to their convergence-trigger contribution to the underdiagnosis-retry loop.
- **Demotion candidates considered and rejected:** Scene Turn for argument-shaped runs was the closest demotion candidate (purely propositional argument-shaped pieces produce limited Scene Turn output). Rejected because the audit self-attenuates on propositional material without producing false positives, and because argument-shaped runs with embedded narrative sections (case studies, anecdotal evidence, opening vignettes) need it to fire there. The audit's self-attenuation is a feature, not an over-firing risk.

The universal status holds; future audit additions follow the criterion above with explicit rationale logged in the changelog.
