# Fixture Manifest: Regrets Only (The Let Down, Novella 2)

## Identity

- **Fixture slug:** regrets-only-novella
- **Short name:** Regrets Only — The Let Down, Book 2
- **Bucket:** novella (30-50k). Does not map cleanly to the existing eval-harness bucket taxonomy; flag for a later amendment to add a "novella" row. Closest existing fit is between "short-fiction-known" and "60k-100k."
- **Status:** active (primary mid-length fixture)

## Source And Permission

- **Source class:** joshuas-private-fiction
- **Permission status:** self-owned; author is framework owner
- **Permission record (if any):** implicit via authorship

## Content Storage

- **In-repo text?:** no
- **Storage location:** `../../../Writing/The_Let_Down/Novellas/Novella_02_COMPLETE.md` (outside apodictic repo, under Cowork Working Folder)
- **What, if any, text is stored:** none in manifest. Manuscript is local-only under `Writing/The_Let_Down/`.
- **Quotation policy:** outputs may reference by line number. Blind-review packets must anonymize character names (Ada, Jordan, Daphne, Makayla, and any Let Down terminology) before external review. No extended prose quotes in publishable outputs.

## Expected Diagnosis

- **Rubric file:** `evals/rubrics/core-de.md` (full-letter run) or `evals/rubrics/synthesis.md` (synthesis-only)
- **Expected-diagnosis summary or known-comparison notes:** active multi-round APODICTIC project under `Writing/The_Let_Down/Apodictic/Novella_02/`. Prior runs: 2026-02-28 (early-framework, `N2_` prefix) and 2026-03-19 (labeled `DE-2026-03-19`). Accumulated state files exist: `Diagnostic_State.md` (70K, last updated 2026-04-20), `SYNTHESIS.md` (35K), handoff docs, and execution-mode drafts (Coffee Shop Movement 1, Ch03 POV alternates). An `APODICTIC_vs_Opus_4_7_Evaluation.md` note exists from 2026-04-17. Ground truth includes: what the 03-19 synthesis prioritized, what subsequent scene-level handoff work Joshua chose to execute, and whether a current-model run adds new useful findings or repeats prior ones. This makes the fixture a revision-round test, not a greenfield baseline.
- **Artifact scope for blind review:** full-letter (preferred) or synthesis-only
- **Target metrics (pre-registered):** root-cause accuracy, evidence specificity, counterevidence, severity honesty, absence detection, firewall compliance, author usability

## Release And Publication

- **Can outputs be used in public release notes?:** **No, never.** This is F.T. Caller erotica published under Quiet Harm Imprint. Neither raw outputs nor anonymized derivations of APODICTIC outputs on this manuscript may appear in public release notes, marketing material, sample letters, or any other APODICTIC-facing publication.
- **Can the fixture itself be shared with external reviewers?:** blind-review-only, fully anonymized (character names, Let Down terminology, distinguishing plot elements replaced). External reviewers operate under the blind-review protocol and do not retain outputs after scoring.

## Maintenance

- **Date added:** 2026-04-24
- **Last refreshed:** 2026-04-24 (manuscript status: actively in revision; word count 39,838)
- **Known staleness:** low. Manuscript is current and being worked on. Run results may age quickly as Joshua revises.
- **Retirement criteria:** retire when Regrets Only is published under Quiet Harm Imprint or Joshua designates a different Let Down novella as the active fixture.

## Audit-Routing Pre-Labels

The Let Down series is philosophical erotic horror exploring consent, conditioning, and identity. Expected audit behavior:

| Audit | Expected | Reason |
|---|---|---|
| Consent Complexity | auto-run | Series explores conditioning and consent as unstable system |
| Reception Risk | auto-run | Erotic horror with high-stakes subject matter; reception miscalibration is a real risk |
| AI-Prose Calibration | recommend | Joshua drafts with AI assistance; worth checking voice |
| Stakes System | recommend | Universal audit; calibrate whether universal treatment holds here |
| Decision Pressure | recommend | Universal audit |
| Scene Turn | recommend | Universal audit |
| Character Architecture | recommend | Ada/Jordan/Daphne/Makayla character architecture is central |

## Run Methodology — 2026-04-24 Opus 4.7 Blind Run

Per Joshua's decision, the 2026-04-24 run is a **two-stage methodology**:

**Stage 1 (this run):** Blind Opus 4.7 extra-high-effort run. No accumulated state (`Diagnostic_State.md`, `SYNTHESIS.md`, handoff docs, prior run artifacts) is loaded. Each swarm subagent operates as if no prior APODICTIC work exists. Purpose: produce a clean current-model baseline without prior-round contamination. Output isolated to `runs/2026-04-24_opus47_de/`; no updates to cumulative project state during stage 1.

**Stage 2 (later, separate session):** Comparative evaluation. Stage 1 findings read against accumulated wisdom from prior runs (2026-02-28 N2, 2026-03-19 DE) and current Diagnostic_State. Questions: does Opus 4.7 rediscover the 03-19 findings? What new findings does it surface? What does it miss that older runs caught? Did scene-level handoff execution address findings Stage 1 now raises? Stage 2 produces a comparative report, not new passes.

The isolation is deliberate. Stage 1's value as a fixture signal depends on its independence from prior state.

## Notes

Primary fixture for mid-length fiction work in the 2026-04-24 review. Replaces Observer's Share 83k as the active novel-length fixture because:

1. Observer's Share outputs are stale (Opus 4.6, v4.15).
2. Regrets Only is actively under revision — findings have immediate editorial value in addition to diagnostic value.
3. Shorter manuscript makes single-agent mode feasible for comparison runs; Observer's Share requires hybrid.

Observer's Share 83k remains in [observer-share-83k-hybrid.md](./observer-share-83k-hybrid.md) as the historical packet-format calibration reference.

Before first eval run: select execution mode (single-agent preferred for 40k length), pass set, and audit roster.
