# Revision Arc: The Tide Between Us

<!--
Worked example of a contract-conformant Revision Arc (Multi-Session Revision Arc Planning coaching
track — operator: revision-coach; see multi-session-arc-planning.md + docs/multi-session-arc-planning.md).
A returning author with a completed diagnosis is planning a multi-week revision STRATEGY: which
findings, in which phase, in what order, and why. APODICTIC SEQUENCES the Findings Ledger into a
phased arc (Phase 1 structural root causes -> Phase 2 downstream consequences -> Phase 3 polish);
the AUTHOR writes the tissue (the Firewall). The arc is the layer ABOVE the per-session Loop
Dispatch — it is the calendar that feeds the per-session planner; it does not re-run dispatch.

This file is exercised by `validate.sh --check-all` as a canonical release-gate target for
`revision-arc` (--strict): A1 schema + nested phase shape, A2 provenance closure (every finding_ref
resolves to a real finding in the embedded Findings Ledger below), A3 self-consistency (each
finding in exactly one phase; no Must-Fix structural root cause parked in the polish phase), A4
non-empty sequencing rationale; W1 firewall-drift (none — every rationale SEQUENCES, never
prescribes execution) and W2 orphan (none — every Must-Fix ledger finding is placed in the arc).

HONEST POSTURE (the load-bearing disclaimer): the validator gates this plan's self-consistency +
provenance + firewall, NOT a true causal graph. The Root-Cause mapping below is the COACH'S
reasoning (read from the diagnosis, trusted), not a machine-readable dependency structure the
validator verifies. Whether Phase 2's consequences truly descend from Phase 1's root cause is the
coach's judgment; A3 only checks that the arc is internally consistent with its own phase ordering.

It is illustrative, not a run artifact; keep it passing when the contract or the validator changes.
Keep every phase `rationale` a SEQUENCING rationale ("Phase 1 must close X before Phase 2"), never
an execution prescription ("rewrite the climax so that …").
-->

## The diagnosis this arc reads (Root-Cause map — the coach's reasoning, not gated)

The development edit found a controlling-idea problem at the root: the manuscript never commits to
whether the sisters' estrangement is the *subject* or the *backdrop*. The coach reads this Root-Cause
table from `Diagnostic_State.md` — it is prose, not machine-readable, so the **coach** reasons the
dependency and the **validator** trusts it:

| Finding | Severity | Root cause (coach's read) |
|---|---|---|
| F-CI-01 controlling-idea drift | Must-Fix | the structural root — the book's subject is unsettled |
| F-PT-02 midpoint reversal lands flat | Should-Fix | downstream of F-CI-01: the reversal can't pay off an unsettled subject |
| F-CH-03 sister B reads as a device | Should-Fix | downstream of F-CI-01: her arc only coheres once the subject is fixed |
| F-LN-04 chapter-7 prose over-hedged | Could-Fix | line-level; no upstream dependency |

## The Arc

The arc places the Must-Fix root cause first, its two Should-Fix consequences second (they cannot be
judged resolved until the subject is settled), and the Could-Fix line-level work last. Phase order
*is* the dependency expression — there is no declared-edge field; the cross-phase dependency the
coach names lives in the rationale prose, trusted but not blessed as data.

<!-- apodictic:revision_arc
{"schema":"apodictic.revision_arc.v1","phases":[{"phase_label":"Structural root causes","findings":["F-CI-01"],"root_cause_findings":["F-CI-01"],"rationale":"Phase 1 must settle the Must-Fix controlling-idea root cause before any downstream work; until the book's subject is fixed, the consequence findings can't be judged resolved. Sequence this finding alone so re-diagnosis after Phase 1 can re-phase the rest."},{"phase_label":"Downstream consequences","findings":["F-PT-02","F-CH-03"],"rationale":"Sequenced after Phase 1: both Should-Fix findings descend from the controlling-idea fix (the coach's read) — the midpoint reversal and sister B's arc only cohere once the subject is settled, so they wait on Phase 1 closing rather than being worked in parallel."},{"phase_label":"Polish","findings":["F-LN-04"],"rationale":"Could-Fix line-level work with no upstream dependency, sequenced last so polish isn't spent on prose a structural phase may rewrite."}],"adaptation_note":"Stateless re-plan: regenerated each run from the current finding_states, overwriting the prior arc. After Phase 1 closes (F-CI-01 -> revised), re-run — re-diagnosis may re-phase or retire the Phase-2 consequences."}
-->

## Findings Ledger (the example manuscript's findings — A2 resolves against these)

<!-- apodictic:finding
{"schema":"apodictic.finding.v1","id":"F-CI-01","mechanism":"the manuscript never commits to whether the sisters' estrangement is the subject or the backdrop, so the controlling idea drifts across the three acts","severity":"Must-Fix","confidence":"HIGH","evidence_refs":["Act I","Act III"],"fix_class":"settle the controlling idea, then re-weight the sister scenes to it","risk_if_fixed":"over-committing could flatten the ambient-grief texture the opening earns"}
-->

<!-- apodictic:finding
{"schema":"apodictic.finding.v1","id":"F-PT-02","mechanism":"the midpoint reversal lands flat because it pays off a subject the draft hasn't committed to","severity":"Should-Fix","confidence":"MEDIUM","evidence_refs":["Chapter 11"],"fix_class":"re-aim the reversal at the settled controlling idea","risk_if_fixed":"a sharper reversal could over-determine the close"}
-->

<!-- apodictic:finding
{"schema":"apodictic.finding.v1","id":"F-CH-03","mechanism":"sister B reads as a plot device rather than a person; her arc only coheres once the book's subject is fixed","severity":"Should-Fix","confidence":"MEDIUM","evidence_refs":["Chapter 4","Chapter 12"],"fix_class":"give sister B an interiority beat anchored to the controlling idea","risk_if_fixed":"too much interiority could slow the Chapter-4 momentum"}
-->

<!-- apodictic:finding
{"schema":"apodictic.finding.v1","id":"F-LN-04","mechanism":"the Chapter-7 prose hedges every emotional claim with a qualifier, reading as evasive rather than restrained","severity":"Could-Fix","confidence":"HIGH","evidence_refs":["Chapter 7"],"fix_class":"thin the qualifiers in the chapter's key beats","risk_if_fixed":"removing all hedges could overstate a deliberately ambivalent narrator"}
-->

## Session/Arc boundary

This arc is the **calendar** that sequences findings into per-session work; it does not re-run the
per-session **Loop Dispatch** (which answers "what's the single highest-leverage thing to do *next*?"
from `finding_states`). Each phase feeds that per-session planner. The arc generalizes Retcon
Planning's single-decision arc (one late decision -> dependency-ordered setup debt) to the full
Findings Ledger across multiple weeks.
