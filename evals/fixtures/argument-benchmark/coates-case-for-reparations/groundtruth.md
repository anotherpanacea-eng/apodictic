# Ground Truth: coates-case-for-reparations

## Provenance

- **Fixture slug:** coates-case-for-reparations
- **Bucket:** 7 argument-with-embedded-narrative hybrid · **Cluster:** D (standalone long-form) · also advocacy journalism (6)
- **Source class:** third-party published — **referenced (text NOT stored; copyright)**
- **Work:** Ta-Nehisi Coates, "The Case for Reparations," *The Atlantic*, June 2014.
- **Pinned source:** https://www.theatlantic.com/magazine/archive/2014/06/the-case-for-reparations/361631/ (record retrieval date + content hash on first authoritative run; analyzed-text extraction anchors (START / END / EXCLUDE) in [../SOURCES.md](../SOURCES.md); note possible paywall — use an accessible copy or library access).
- **Quotation policy:** paraphrase only — do not reproduce the source text.
- **Ground-truth authority:** Joshua A. Miller (editor), independent diagnosis registered 2026-05-30, before any engine run.
- **Scope:** GT1–GT3 authoritative. **GT4–GT8 PROVISIONAL.**
- **Reliability:** GT1–GT3: authoritative, gate; GT4–GT6: provisional, confirm; GT7: provisional, confirm; GT8: provisional, report

## GT1 — Main claim *(Q1)*

- **Expected C0:** "Reparations are owed as a national moral reckoning for legally structured theft (redlining, housing predation, discriminatory policy), not merely as compensation for slavery."
- **Acceptable paraphrase band:** any recovery centered on *reckoning for ongoing, legally-structured theft / 20th-c. policy* (not slavery-only, not narrow cash compensation) is a hit. "Black Americans deserve money for slavery" is a **miss** — it recovers the popular caricature, not Coates's actual claim.

## GT2 — Failure locus *(Q2)*

- **Main structural problem (authority):** the **leap from concrete housing predation (richly documented) to national remedy**.
- **Primary failure layer:** WARRANT / SCOPE — the inferential bridge from documented, specific predation to the national-obligation claim.
- **Provisional codes:** WR0 (the predation→national-remedy warrant) + BP2 (scope: specific theft → national obligation). FM-A6 (Warrant Leap) / FM-A4 (Scope), at **Should-Fix**, not collapse.
- **NE note (bucket 7):** the Clyde Ross narrative does real **argumentative work** (NE function = EVIDENCE/ILLUSTRATION, not decoration). Firing NE/FM-A3 on the narrative would be a calibration error — Step 9 must credit narrative-as-evidence.

## GT3 — Strongest real objection *(Q3)*

- **Objection zone (authority):** the essay proves the **debt** more clearly than it specifies **institutional design** — the "what, exactly, and how" gap. (Partly by design: Coates argues for an HR-40-style *study*, not a specific scheme — a run should weigh whether the design gap is a bounded scope choice or a real hole.)
- **Provisional codes:** OB3 / FM-A18 (Implementation Blindspot)-adjacent.

## GT4–GT8 — *(PROVISIONAL)*

- **GT4 audience:** GENERAL-MIXED · MIXED→HOSTILE (contested topic) · HIGH. Hostile-audience defense is the calibration burden.
- **GT5 red-team:** load-bearing = the national-remedy warrant + design gap. Decoy = disputing individual historical examples (the documentation is the strong part).
- **GT6 repair order:** first target = the **warrant/scope bridge** from predation to national obligation, before more historical evidence.
- **Expected warrant verdict:** WARRANTED — a landmark argument whose narrative method is legitimate; design gap is Should-Fix. **Calibration trap:** over-pathologizing the embedded-narrative method, or treating the (partly intentional) design gap as UNWARRANTED. Bucket-7 dual-audit: also exercises the Narrative Nonfiction Craft ↔ Dialectical Clarity handoff.
- **Expected premise flags:** NONE_REGISTERED (provisional migration default)
- **GT8 Must not adjudicate:** whether reparations are in fact owed as a national moral reckoning for legally structured 20th-century theft.

## Notes

The corpus's hybrid (bucket 7) anchor — tests the NE inventory and the two-audit handoff, not just the argument layer.

**Input integrity:** the 2026-05-30 cached extraction (`coates-case-for-reparations-corrected.md`; provenance in [../SOURCES.md](../SOURCES.md)) is clean — the predatory-lending block is in sequence and no captions/sidebar are interleaved. An earlier extraction with ordering artifacts on the GT2 / conclusion anchors was superseded; Coates is a load-bearing fixture (no longer provisional).
