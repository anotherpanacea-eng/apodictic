# Example — Refutation Record

<!--
Canonical Refutation Record for the example-run-folder fixture (docs/finding-disconfirmation.md
§4), exercised by `validate.sh --check-all` as the release-gate target for the three refutation
validators: refutation-coverage (V1 no HIGH without survived refutation), refutation-evidence
(V2 verbatim snapshot-anchored counter-evidence + snapshot_sha256 binding + budget arithmetic),
and refutation-write-scope (V3 no severity channel + exact confidence transcription). The block
below is recompute-consistent with the fixture's Findings Ledger (F-P5-01, Must-Fix, HIGH) and
Manuscript Snapshot (the quote occurs verbatim; the sha256 hashes the snapshot's as-is bytes) —
keep all three in sync when editing. The severity-injection, fabricated-quote, and
stripped-record hostile arms mutate temp copies of this file, never this file.
-->

## F-P5-01 — the want never forces a sacrifice

Disconfirmation attempt: hunted the manuscript for a scene where the want costs the
protagonist something real — the evidence that would refute the mechanism. What would have
refuted this finding: a paid cost anywhere in the want's arc. The closest candidate is the
orchard hesitation (quoted in the block below), which is a cost *declined*, not paid — it
sharpens the diagnosis rather than cutting against it. Rival reading considered: the
restraint could be the design, but the mechanism claims the want never *costs*, and the
restraint scene shows no paid cost either. Outcome: survived; confidence transcribed
unchanged (survival never raises confidence).

<!-- apodictic:refutation
{"schema":"apodictic.refutation.v1","id":"F-P5-01","attempted":true,"outcome":"survived","counter_evidence_quotes":["For a moment she almost chooses the orchard over the debt."],"alternative_explanations":["Restraint could be the design — Ch. 3 frames her caution as inheritance, not avoidance — but the mechanism claims the want never costs, and Ch. 3 shows no paid cost either."],"rationale":"A scene where the want forces a paid sacrifice would have refuted this; the closest candidate is the orchard hesitation (quoted), a cost declined rather than paid — the mechanism stands.","confidence_after":"HIGH","snapshot_path":"Example_Manuscript_Snapshot_2026-01-01_opus46.md","snapshot_sha256":"113098dc16884863256d1f09c56550cda0b7cf023c687936a1682df4301f3a51"}
-->

## Budget

Eligible set at lock: 1 (one Must-Fix; no HIGH Should-Fix). Processed 1 of 1 under the
cap of 15 — the budget did not bind.

<!-- apodictic:refutation_budget
{"schema":"apodictic.refutation_budget.v1","cap":15,"eligible":1,"processed":1,"bound":false}
-->
