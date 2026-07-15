### Specs — Approval-Gated Reconstruction

New companion-module spec `docs/approval-gated-reconstruction.md` (v0.2.0, unbuilt):
approval-gated reconstruction over a provenance-linked claim graph — normalize
`Argument_State.md` + manuscript into a content-addressed approval graph, author
adjudicates every node and edge, a drafter authors a fresh document from the approved
subgraph only, and a two-layer conformance gate (mechanical `argument-reconstruction`
validator + semantic exclusion/coverage/novelty-quarantine checks) proves it, emitting a
reconstruction receipt that `/ready` validates. Five top-level invariants, including
rejection-stickiness (no reconciliation or revision path may shrink the exclusion set).
Spec folded three independent review passes before freeze; builds in five increments,
starting with `scripts/approval_graph.py`.
