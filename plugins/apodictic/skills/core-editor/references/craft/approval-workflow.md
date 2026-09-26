# Author approval workflow

This is the mechanical portion of Approval-Gated Reconstruction Increment 2.
The author decides what may be said. Diagnostics, confidence, flags and model
preferences never count as author approval. This workflow does not draft or
certify a reconstruction. The compatible semantic exclusion screen and
entailment-near history retrieval remain pending Increment 4.

## Open or resume

Use the plugin's `scripts/approval_session.py` (relative to the plugin root)
with the available Python 3 interpreter:

```text
python3 scripts/approval_session.py PROJECT --show
```

Use a shell argument array or proper quoting for the exact project path. Do
not concatenate manuscript or author text into a shell command. `PROJECT`
must already contain `Approval_Events.jsonl` from the normalizer contract.
Missing, unreadable or corrupt committed history is an error: stop and show the
error rather than inventing a graph. A zero-byte existing ledger is unstarted;
route back to normalization without making author decisions.

The adapter verifies source custody and ledger history under the project lock,
recovers only the existing engine's permitted torn suffix, and rebuilds
`Approval_Graph.md` and `Adjudication_Session.json`. These are caches: never
edit them or hand-append to the ledger. Do not run reconciliation concurrently
with a decision. The lock covers each snapshot/commit operation, not the human
conversation; every decision uses the shown count/hash to detect intervening
work. If the head changes, re-present and obtain a fresh author decision.

Report the replayed progress: adjudicated of total, plus APPROVED, REJECTED,
SUPERSEDED and PENDING counts. These count records (including edges and
superseded history), not approved propositions or editorial quality.

## Present before asking

1. Start with the snapshot's `session.next_record`: pending nodes in lexical
   ID order, then pending edges whose endpoint nodes are adjudicated. Do not
   skip an undecided endpoint to approve or reject its edge. The author can
   explicitly revisit a prior record; never infer that request.
2. Show node ID, type, exact text, presence, origin, flags, anchors, Inclusion,
   history and notes. Show an edge's ID, type, both endpoint IDs and their
   exact texts/approval states, and its carried typing. Never paraphrase away
   a qualifier or hide a prior decision.
3. Read relevant Argument State sections 5, 8 and 9 as decision support, using
   the state version named in the snapshot context. Label a missing or
   mismatched state unavailable; never present a different version as current
   evidence. Flags inform the author and never auto-reject a record.
4. Show the complete REJECTED set, including ORPHANED rejections, with text or
   edge relation/endpoints, prior refusal history, reasons and notes. For a
   quarantine, revision successor, or suggested lineage, surface that history
   before the proposed record. Listing all rejections is conservative interim
   presentation, not a claim of semantic retrieval. If it cannot fit, suspend
   and review in explicit pages; never silently truncate it.
5. Ask for one explicit decision: approve (nodes require REQUIRED or OPTIONAL),
   reject, or revise a node using author-supplied type/text. Do not recommend
   approval merely because a claim seems plausible. No approve-the-rest,
   timeout approval, or model-authored replacement prose.

## Record one decision

Write one UTF-8 JSON request file in the project, separately from the ledger.
The request is a transient input, not state authority. Example (replace the
ID, timestamp and head with the actual presented values):

```json
{
  "action": "approve",
  "record_id": "n-0123456789ab",
  "expected_head": {"bundle_count": 1, "terminal_hash": "<actual 64-character hash>"},
  "timestamp": "2026-09-25T12:00:00Z",
  "inclusion": "REQUIRED",
  "note": "Author's optional note, verbatim"
}
```

```text
python3 scripts/approval_session.py PROJECT --decision REQUEST.json
```

Use the actual UTC time, and preserve the author's note separately from the
reason. Never reuse an old request as a new decision. Actions:

| Action | Author input and mechanical effect |
|---|---|
| `approve` | PENDING only. Node needs `inclusion`; edge forbids it and needs APPROVED endpoints. Nonempty exclusions block this operation. |
| `reject` | PENDING or APPROVED -> REJECTED; withdrawing an approved node's authority cascades its approved incident edges to PENDING in the same bundle. |
| `withdraw` | APPROVED -> PENDING, with the same atomic edge cascades. |
| `unreject` | REJECTED -> PENDING, with an explicit nonempty `reason`. This is not approval; a separate author decision follows. |
| `inclusion` | APPROVED node only; change REQUIRED/OPTIONAL with explicit `inclusion` and nonempty `reason`. |
| `revise` | PENDING/APPROVED node only; `replacement` is exactly `{"type":"CLAIM","text":"author-supplied text"}` (use the actual valid type). New identity starts PENDING, old identity becomes SUPERSEDED, and edge cascades commit atomically. Existing identities and rejected-node revision are refused. |

`note` is optional for every action. Unknown or inapplicable fields fail closed.
No action deletes records or changes presence. A legitimate un-rejection is
the author's explicit change of mind, never a workaround proposed to evade
the screen. If exclusions remain, retain the blocked approval and suspend or
continue other author decisions. No human "accept risk" or model agreement
substitutes for the unavailable semantic screen.

After success, run `--show` again, display the new head/progress and summarize
any cascades. Only `status: COMMITTED` acknowledges a completed operation.
On an error with `committed: true`, the decision is already durable; recover
with `--show` and verify its history instead of retrying. With `committed: null`
or a missing acknowledgement, inspect recovered history before any further
action. A false result is not permission to retry with a refreshed head:
`STALE-HEAD` requires fresh presentation and renewed author intent.

## Stop or finish

The author may stop at any decision boundary. Report the current head,
progress and next record; disk state is sufficient to resume. Never mark
cache status OPEN or CLOSED yourself. `CLOSED` means every record has left
PENDING, not that the project is ready to draft or accepted. Run the existing
`validate.sh argument-reconstruction PROJECT --stage draft-ready` to report
mechanical readiness separately (for example, REQUIRED-BUT-WITHHELD can still
block it). Packet generation, drafting, semantic acceptance and `/ready`
receipt integration remain later increments. Do not claim an acceptance PASS.
