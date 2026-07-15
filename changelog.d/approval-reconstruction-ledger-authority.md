### Approval-Gated Reconstruction — ledger-authority redesign (Rev 0.3.0)

Adopt ADR 0002: `Approval_Events.jsonl` becomes the sole authoritative state, one decision
bundle is one ledger record (carrying its `MINTED` content payload), and `Approval_Graph.md`
plus `Adjudication_Session.json` become deterministic projections rebuilt from the ledger.
Crash recovery collapses to truncate-and-replay that fails closed, and the three-artifact
cross-consistency checks reduce to a byte-identical regeneration compare. This supersedes the
multi-artifact recovery/reconciliation machinery of Rev 0.2.1–0.2.3, whose crash-prefix cases
move to an Increment-1 truncate-and-replay fixture family. Still an unbuilt spec; the
`built-when` marker does not fire.
