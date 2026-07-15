### Approval-Gated Reconstruction — ledger-authority redesign (Rev 0.3.1)

Adopt ADR 0002: `Approval_Events.jsonl` becomes the sole authoritative state, one decision
bundle is one ledger record (carrying its `MINTED` content payload), and `Approval_Graph.md`
plus `Adjudication_Session.json` become deterministic projections rebuilt from the ledger.
Crash recovery collapses to verify/truncate-uncommitted-tail/replay that fails closed, and the
three-artifact cross-consistency checks reduce to deterministic projection rebuild. This supersedes the
multi-artifact recovery/reconciliation machinery of Rev 0.2.1–0.2.3, whose crash-prefix cases
move to an Increment-1 truncate-and-replay fixture family. Still an unbuilt spec; the
`built-when` marker does not fire.
- Close the authority gaps found after the redesign: stored terminal-verifiable bundle hashes,
  ledger-resident source context, a legal QUARANTINE bundle, carried-typing edge identity,
  newline-delimited torn-tail recovery, ledger-derived notes, cache rebuild semantics, and an
  ephemeral process lock for live-session state.
