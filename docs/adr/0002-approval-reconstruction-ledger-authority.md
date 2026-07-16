# ADR 0002 — Approval-reconstruction authority model: the event ledger is the sole authoritative state

**Status:** Accepted · **Date:** 2026-07-15 · **Supersedes:** the recovery/reconciliation contract in `docs/approval-gated-reconstruction.md` §Phase 0 (Rev 0.2.3, PR #215) · **Related:** Spec 213 (approval-gated reconstruction); invariants I1–I5.

## Context

Three review rounds on PR #215 closed every static-invariant defect but never stopped finding contradictions in one subsystem: multi-event crash recovery and per-axis replay. The findings are not sloppiness — they are the shape of the problem leaking through the medium. The rest of Phase 0 specifies **static structural invariants** (state model, content-addressed identity, field-presence, event grammar, retention/I2), which prose can enumerate and a validator can check by membership. Crash recovery is a different kind of thing: the set of reachable intermediate states of a **multi-file write process**, a temporal/combinatorial space that prose specifies point-by-point and can never prove it has covered.

The root cause is an authority decision made implicitly rather than on purpose. The current design treats `Approval_Graph.md`, `Approval_Events.jsonl`, and `Adjudication_Session.json` as **three mutually cross-validated persistent artifacts**. That is a hand-rolled multi-file crash-consistency problem (the `prev_hash`-chained JSONL is a write-ahead log), and "the acknowledged prefix is authoritative" — the phrase we were about to enshrine — quietly picks a winner among the three without saying so. Deferring the *enumeration* of crash cases to Increment-1 fixtures (correct) without simplifying the *model* would leave that reconciliation state space intact for the implementer to reinvent.

## Decision

Adopt a single-authority model. Recovery stops being "reconcile three partially-written artifacts" and becomes "find the last complete ledger record and rebuild the projections."

- **D1 — `Approval_Events.jsonl` is the sole authoritative state.** Every approval fact lives in the ledger; nothing else is a source of truth.
- **D2 — One complete decision bundle occupies one JSONL record**, including its ordered cascade events. A decision is therefore atomic by construction: the record is appended in full or not at all. There is no "valid prefix of a bundle" to classify.
- **D3 — `Approval_Graph.md` is a deterministic, human-readable projection** rebuilt from the ledger. It is never authoritative and never hand-edited; author decisions enter only as ledger appends.
- **D4 — `Adjudication_Session.json` is a reconstructible cursor/cache, never an authority.** It may be regenerated from the ledger at any time; losing it loses nothing. Live `OPEN` state is an ephemeral exclusive process lock, not a persisted cache fact.
- **D5 — Recovery = verify, truncate only an uncommitted byte tail, and replay.** Every LF-terminated record carries a stored self-verifying bundle hash and is authoritative or an error. Only a final suffix lacking LF is torn and truncatable. Graph and session are regenerated from the verified replay. Recovery **fails closed**: if the last authoritative record cannot be identified, the tool errors — never a silent advance, never `CLOSED`.
- **D6 — Replay owns all projection inputs.** Bundle context carries source filename/hash and Argument State identity; event `note` fields carry the optional human-readable Notes projection. The graph header and notes never supply facts back to the ledger.
- **D7 — Novelty is a first-class ledger mutation.** S4 emits a `QUARANTINE` bundle of system `MINTED` events; it never appends directly to the graph projection. The bundle binds the current draft's logical version/hash, and each novel node carries the canonical empty-anchor, Origin, and S4-violation provenance payload needed to reproduce those bytes.

## What this supersedes in #215

Deleted or collapsed (all Phase 0 / Rev 0.2.3 additions):

- The multi-event **decision-bundle recovery** procedure (valid-prefix roll-forward, complete-vs-prefix classification) — D2 makes a bundle one atomic record, so the whole procedure reduces to D5.
- The `Adjudication_Session.json` **durable-state contract** (key set, `graph_sha256` parity conditions, staleness definition, reconcile-eligibility dance) — D4 makes the session a cache.
- The Stage A **cross-artifact consistency checks** ("graph Approval/Presence/Inclusion match the independently replayed ledger head"; "every ledger/prior-receipt ID remains in the current graph") — under D3 the graph matches the ledger *by construction*; the check becomes "regeneration is deterministic," not "two independent artifacts agree."
- The reconciliation **session-rewrite ordering** (events → graph → cursor atomicity) — folded into D5's regenerate-after-replay.

Survives, unchanged (this ADR is orthogonal to them):

- **I1–I5.** In fact I2 gets *stronger and simpler*: an append-only, hash-chained ledger makes a rejection permanent by construction, and truncation is detectable via the chain + the receipt's committed line-count — so the "deletion undetectable from a singleton graph" caveat narrows to "detectable unless the ledger itself is truncated below a committed receipt."
- Content-addressed **identity** (IDs from canonical node/edge content) — the ledger references these IDs; I1's "recompute ID from Text, fail on mismatch" moves into the ledger-write path (text only enters via a mint event), which is cleaner than guarding hand-edits to an authoritative graph.
- Field-presence **matrices**, the **event grammar**, and the **drafting-packet** contract (I3) — now describing the *projection* and the ledger record, not an independently-authored file.

## Consequences and resolved design points

1. **Bundle granularity vs. per-record History pointers — resolved.** Every event touched by a bundle projects one History line carrying the bundle's stored hash; the same hash may therefore appear on several records. The stored terminal hash makes even the final record independently verifiable.
2. **Adjudication-on-projection fits I3 better, not worse.** The named cost ("graph no longer authoritative") is smaller than it looks: I3 already forbids the drafter from seeing the graph, and adjudication was always session-driven decision capture, not graph editing. A rebuilt projection *removes* the current tension where the graph is simultaneously the authoritative store and the human-readable surface.
3. **Increment-1 scope shrinks.** `approval_graph.py` becomes: ledger validator + replay engine + deterministic projection generator + Stage A checks over the ledger. The three-artifact reconciliation logic leaves Increment 1 entirely. The Build-Increments list in the spec needs updating to match.
4. **Fixtures still own the crash-prefix cases**, now much smaller: missing-LF final suffixes are truncatable; newline-terminated malformed JSON, stored-hash failures, and `prev_hash` failures are committed-record errors.
5. **Projection drift is recoverable cache drift.** A missing or hand-edited graph is atomically replaced from replay and optionally reported; treating it as an authority-tamper error would recreate the multi-authority model this ADR rejects.
6. **Source identity, notes, and quarantine provenance are ledger-resident.** Bundle `context`, event `note`/`reason`, and bundle shape close the remaining cases where a projection otherwise held unreconstructible information.

## Recommended path

1. Land this ADR (accept the authority decision).
2. Revise `docs/approval-gated-reconstruction.md` through Rev 0.3.2: implement D1–D7, resolve bundle-record History grammar, pin canonical quarantine payload bytes, keep the invariant-level fail-closed rule, and update Build Increments.
3. Increment 1 builds against the revised spec, with the truncate-and-replay fixture family as an explicit deliverable.

This closes the recovery subsystem by deleting most of it, rather than hardening it for a fourth round.
