---
name: argument-audits
description: >
  Dialectical clarity, argument red team, persuasion, evidence provenance, adversarial evidence review, and assuring/guarding/discounting move analysis.
  Use when the user requests one of these focused audits. For the complete
  audit catalog or an unclear request, use specialized-audits.
version: 2.13.3
---

# Argument Analysis

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
| `dialectical` | **Dialectical Clarity** — argument structure, rhetorical fairness | `references/craft/dialectical-clarity.md` |
| `argument-red-team` | **Argument Red Team** — Hostile-reader simulation | `references/craft/argument-red-team.md` |
| `argument-persuasion` | **Argument Persuasion** — Audience matrix & framing | `references/craft/argument-persuasion.md` |
| `argument-evidence` | **Argument Evidence Deep-Dive** — Provenance & testimony calibration | `references/craft/argument-evidence.md` |
| `adversarial-evidence-review` | **Adversarial Evidence Review** — Evidence survivability under structured adversarial protocols | `references/craft/adversarial-evidence-review.md` |
| `argument-agd` | **AGD Move Audit** — Functional assuring, guarding, and discounting move audit | `references/craft/argument-agd-audit.md` |

## Prerequisites and handoffs

Dialectical Clarity produces `Argument_State.md`; companion analyses consume
that populated state for the same draft. This family implements focused argument
audits; `../nonfiction-argument-engine/SKILL.md` owns full-run intake and orchestration.
Adversarial Evidence Review also requires the evidence ledger, citation ledger,
and field-reconnaissance report specified by its protocol. Research requests
route to `../research-verification/SKILL.md`. The optional AGD mechanical scan
is `../prose-measurements/scripts/ai_prose_agd_move_scan.py`; only this family's
AGD protocol adjudicates the scan's candidate pointers.
