# FR-03: approval-reconstruction Phase-0 contract ruling

**Disposition: NEEDS-REWORK before Increment 1. Preserve ADR 0002's single ledger.**

The architecture is sound in its choice of authority, but the contract is not
closed over ordinary reconciliation histories. A required approved node can
become forbidden drafting input without any change to its requirement. The
reconciliation algorithm also demands provenance that the edge schema forbids.
These are contract contradictions, not demonstrated defects in deployed code.

**Source pin:** `anotherpanacea-eng/apodictic` commit
`20b8ca6219e649b2743866b9ffaba0e77ab208a5`, contract revision 0.3.2.
The source tree was fetched and inspected on 2026-09-05. It contains no
`approval_graph.py`; ROADMAP still calls implementation unbuilt.
All source links below are immutable commit links. Histories are newly invented
symbolic examples, not corpus material, serialized valid ledgers, or accepted
benchmark ground truth. A, B, and E are explanatory names, not record IDs.

## 1. Authority ruling

**Accept D1-D7.** Decisions belong in the ledger; graph and cursor are derived
views. Rebuilding an edited projection must not create a tamper incident or
import its edits into authority. The bundle boundary is the right *logical*
transaction boundary. A complete malformed line must error; only the final
non-LF suffix is eligible for recovery truncation. Retained receipt commitments
still constrain how far recovery may roll back. These are already specified
and should not be redesigned as three-way reconciliation.
([ADR D1-D7](https://github.com/anotherpanacea-eng/apodictic/blob/20b8ca6219e649b2743866b9ffaba0e77ab208a5/docs/adr/0002-approval-reconstruction-ledger-authority.md#L14-L21),
[recovery and retained receipts](https://github.com/anotherpanacea-eng/apodictic/blob/20b8ca6219e649b2743866b9ffaba0e77ab208a5/docs/approval-gated-reconstruction.md#L134-L175))

The three distinct claims must remain separate:

- A hash chain and replay establish internal history consistency.
- An author decision authorizes content; it does not establish its truth.
- A semantic judge supplies fallible conformance evidence. An offline grammar
  validator cannot independently prove that evidence true.

The contract already admits the limit when both a suffix and all receipts
committing to it disappear. Do not add signatures, remote witnesses, or a
second authoritative store to address a hostile operator outside the stated
scope. ([history limit](https://github.com/anotherpanacea-eng/apodictic/blob/20b8ca6219e649b2743866b9ffaba0e77ab208a5/docs/approval-gated-reconstruction.md#L166-L175),
[epistemic contract](https://github.com/anotherpanacea-eng/apodictic/blob/20b8ca6219e649b2743866b9ffaba0e77ab208a5/docs/approval-gated-reconstruction.md#L206-L221))

## 2. Findings that require contract changes

### R1: Define packet eligibility and required-content conflicts together

**Evidence.** I3 excludes orphaned records, and the Approval Protocol says
SUPERSEDED and ORPHANED records are withheld from the drafter. Reconciliation
preserves Approval and changes only Presence. The packet clause filters on
Approval alone, exporting approved nodes/edges with no Presence test; Stage B
asks only for no pending records and Inclusion on approved nodes. Stage C
requires every REQUIRED node to be realized.
([I3](https://github.com/anotherpanacea-eng/apodictic/blob/20b8ca6219e649b2743866b9ffaba0e77ab208a5/docs/approval-gated-reconstruction.md#L56-L58),
[reconcile](https://github.com/anotherpanacea-eng/apodictic/blob/20b8ca6219e649b2743866b9ffaba0e77ab208a5/docs/approval-gated-reconstruction.md#L719-L728),
[withholding and packet](https://github.com/anotherpanacea-eng/apodictic/blob/20b8ca6219e649b2743866b9ffaba0e77ab208a5/docs/approval-gated-reconstruction.md#L830-L852),
[Stages B-C](https://github.com/anotherpanacea-eng/apodictic/blob/20b8ca6219e649b2743866b9ffaba0e77ab208a5/docs/approval-gated-reconstruction.md#L917-L925))

**Minimal history H1.** Mint manuscript node A. The author approves A as
REQUIRED. A later normalization omits A. Replay now has
`A = (APPROVED, ORPHANED, REQUIRED)`, with no pending records. Reconciliation
has neither withdrawn approval nor relaxed Inclusion.

**Inference.** Exporting A follows the packet's approval filter but violates
I3. Withholding A follows I3 but leaves a coverage obligation whose only
authorized drafting input has been withheld. This does not logically prove
that no coincidental draft could realize A; it proves the drafting contract
does not supply a faithful path to satisfying that obligation. Silently
narrowing REQUIRED to current records would itself relax the author's decision.

**Recommended disposition: blocker, high confidence.** Define one packet
predicate and use it at export and map validation:

```
eligible_node = Approval == APPROVED and Presence == CURRENT
eligible_edge = Approval == APPROVED and Presence == CURRENT
                and both endpoints are eligible_node
```

Stage B must report any REQUIRED node outside that set and require an explicit
author resolution. Define which approved set the semantic authorization checks
consume as well; an approval-only lookup must not silently undo the packet/map
restriction. `CLOSED` can continue to mean no pending adjudications; it must not
be advertised as proof of draft-readiness. The recommendation is a proposed
contract repair, not an existing owner policy. Do not automatically change REQUIRED to OPTIONAL,
withdraw approval, or admit an orphan into the packet. Valid exits include
revision, legitimate reappearance/current reconciliation,
or withdrawal followed by a further legal author decision. Withdrawal alone
creates PENDING and therefore still fails Stage B; it is not a completed fix.
The exclusion set continues to include *all* REJECTED records, including orphans.

**Related history H2.** Approve A, B, and E=A SUPPORTS B; later orphan A while
preserving Approval. The approval-only coupling invariant remains true, so it
cannot substitute for packet endpoint closure. E must not export a dangling
reference to the withheld A. This is part of R1, not a separate counted finding.

### R2: Give edges a legal reconciliation lifecycle

**Evidence.** Edges must omit Provenance and Origin; their mint payload contains
only type, endpoints, and carried typing. Yet the UNCHANGED reconciliation
rule appends a provenance entry, and a zero-axis RECONCILE event is legal only
when its reason is compared to the record's Provenance list. DISAPPEARED is
defined by MANUSCRIPT origin. Mint bundle shape already distinguishes
manuscript edges from quarantined edges, but the reconciliation rule does not
explicitly consume that distinction.
([edge matrix](https://github.com/anotherpanacea-eng/apodictic/blob/20b8ca6219e649b2743866b9ffaba0e77ab208a5/docs/approval-gated-reconstruction.md#L385-L396),
[edge payload](https://github.com/anotherpanacea-eng/apodictic/blob/20b8ca6219e649b2743866b9ffaba0e77ab208a5/docs/approval-gated-reconstruction.md#L482-L493),
[mint origins and zero-axis events](https://github.com/anotherpanacea-eng/apodictic/blob/20b8ca6219e649b2743866b9ffaba0e77ab208a5/docs/approval-gated-reconstruction.md#L529-L545),
[reconciliation cases](https://github.com/anotherpanacea-eng/apodictic/blob/20b8ca6219e649b2743866b9ffaba0e77ab208a5/docs/approval-gated-reconstruction.md#L719-L743))

**Minimal history H3.** Mint A, B, and E from a manuscript. Re-normalize an
unchanged source, producing the identical E. The general UNCHANGED rule asks
for a provenance append that cannot appear in E's closed mint payload or
projection. Interpreting “atom” as node-only avoids that contradiction by
leaving the unchanged-edge behavior unspecified instead.

**Companion history H4.** In a later normalization A and B remain but E
disappears. E has no Origin field. A quarantined edge absent from normalization
must meanwhile retain its exemption from disappearance detection. Using node
origins, or the presence of endpoints, cannot distinguish these cases.

**Recommended disposition: blocker, high confidence.** Specify separate edge
rules. Derive edge origin from the bundle that first minted it: MINT/RECONCILE means
manuscript; QUARANTINE means novel. Do not add an independently editable Origin
field. An unchanged edge can keep its state without a per-edge event; define
presence flips for disappeared/reappeared manuscript edges. Reserve STATE
provenance appends and anchors/flags refreshes for nodes. Define a no-change
reconciliation as a no-op if no legal event is needed, rather than manufacturing
an empty bundle (the existing grammar requires a nonempty events array).

### R3: Recovery may classify a tail only after excluding a live writer

**Evidence.** Recovery runs on any resume or gate run and may truncate a
non-LF final suffix. An OS-held lock exists, and reconciliation is explicitly
blocked by the adjudication lock. The text does not expressly require a gate's
recovery, a QUARANTINE append, and every other ledger writer to participate in
the same exclusion protocol.
([recovery](https://github.com/anotherpanacea-eng/apodictic/blob/20b8ca6219e649b2743866b9ffaba0e77ab208a5/docs/approval-gated-reconstruction.md#L134-L164),
[reconciliation lock](https://github.com/anotherpanacea-eng/apodictic/blob/20b8ca6219e649b2743866b9ffaba0e77ab208a5/docs/approval-gated-reconstruction.md#L715-L749),
[S4 append](https://github.com/anotherpanacea-eng/apodictic/blob/20b8ca6219e649b2743866b9ffaba0e77ab208a5/docs/approval-gated-reconstruction.md#L975-L983))

**Minimal history H5.** An adjudicator has begun writing one new bundle and
has not yet written its LF. A gate starts, sees that suffix, and applies the
recovery rule while the writer is alive. Those bytes are indistinguishable
from a crashed append *to a reader that has not excluded the writer*. One
logical JSONL record alone does not settle this concurrency question.

**Inference and limit.** This is a missing synchronization contract, not a
claim that a production tool currently races. A careful implementer could
already apply the lock to all operations; the spec should require that choice.
No particular operating-system short-write behavior is asserted or measured.

**Recommended disposition: implementation prerequisite, high confidence.**
Require the same project lock around reading the authoritative head for a
mutation, tail classification/truncation, append, and projection publication.
A gate must refuse or wait when another session owns that lock; it may not
interpret an active append as a crash. A long semantic call need not hold the
lock: it can bind to a frozen ledger/draft identity and recheck both identities
under the lock before publishing results or appending quarantine. Changed
inputs invalidate that result. Pin an acknowledgement/durability policy before
claiming power-loss durability; do not infer it from JSONL framing.

### R4: Close existing-identity revision and quarantine paths without reminting

**Evidence.** Canonically identical text denotes the same node. REVISE always
mints a replacement starting PENDING, with a reciprocal AUTHOR-REVISION
successor. S4 mints content not entailed by approved records. The contract
enforces unique graph IDs, sticky rejection, and terminal SUPERSEDED state,
but does not explicitly define what these operations do when their computed
ID was already minted.
([identity](https://github.com/anotherpanacea-eng/apodictic/blob/20b8ca6219e649b2743866b9ffaba0e77ab208a5/docs/approval-gated-reconstruction.md#L674-L711),
[revision](https://github.com/anotherpanacea-eng/apodictic/blob/20b8ca6219e649b2743866b9ffaba0e77ab208a5/docs/approval-gated-reconstruction.md#L810-L829),
[S4](https://github.com/anotherpanacea-eng/apodictic/blob/20b8ca6219e649b2743866b9ffaba0e77ab208a5/docs/approval-gated-reconstruction.md#L975-L986))

**Minimal history H6.** A is APPROVED and B is REJECTED. The author revises
A to B's canonical text and type. The prescribed new mint has B's existing
ID. Overwriting B with PENDING violates I2; duplicating B violates uniqueness;
reusing B as a new AUTHOR-REVISION mint falsifies its origin. Revising A to
its own canonical text, or later back to a terminal superseded node, produces
related cases without any cryptographic collision.

**History H7.** A draft asserts the exact proposition of rejected B. S1 should
report the exclusion violation. Since B is not approved, the literal S4 test
also makes it a novelty candidate unless an existing-identity/check-order rule
takes precedence. Pin that precedence; reminting is still invalid.

**Recommended disposition: close before writer implementation, high confidence
on the identity conflict; no claim of a permitted rejection bypass.** The
top-level invariants already forbid the unsafe outcomes. Explicitly refuse
every second mint of an existing ID before any append. For revision, return an
itemized conflict and leave the ledger unchanged; use existing author actions
on existing records where legally possible. Do not add an undo transition for
SUPERSEDED. For S4, reference an existing record and retain the applicable
violation instead of minting it again. Existing PENDING quarantine is reused
on repeated runs. Define the no-new-novelty case without an empty bundle.

### R5: Empty is unstarted, yet the written readiness test passes vacuously

**Evidence.** An empty ledger is valid as unstarted/SUSPENDED and is expressly
not CLOSED. Stage B nevertheless adds only zero PENDING records and Inclusion
on every approved node. Both conditions are vacuously true for no records.
([session state](https://github.com/anotherpanacea-eng/apodictic/blob/20b8ca6219e649b2743866b9ffaba0e77ab208a5/docs/approval-gated-reconstruction.md#L146-L159),
[empty Stage A](https://github.com/anotherpanacea-eng/apodictic/blob/20b8ca6219e649b2743866b9ffaba0e77ab208a5/docs/approval-gated-reconstruction.md#L884-L893),
[Stage B](https://github.com/anotherpanacea-eng/apodictic/blob/20b8ca6219e649b2743866b9ffaba0e77ab208a5/docs/approval-gated-reconstruction.md#L917-L919))

**Minimal history H17.** The ledger exists but contains zero bundles; no
retained receipt requires a prior prefix. Stage A accepts the unstarted state.
No PENDING record exists, and no approved node lacks Inclusion. The written
Stage-B predicates all hold, despite no normalization or adjudication.

**Recommended disposition: deterministic gate blocker, high confidence.**
Require a nonempty MINT-derived graph for draft-readiness, in addition to the
existing predicates and R1. Requiring derived CLOSED is an equivalent start/
completion condition under the current cache definition, but is not sufficient
for R1's required-but-withheld conflicts. Do not add a minimum approved-node
count here: whether an author can reject everything is a separate policy choice.
This finding came from the independent review and was adopted after source check.

### R6: Bind retained anchors to retained source versions

Reconciliation replaces
the graph's source header, retains disappeared nodes, and cannot refresh their
absent anchors. Stage A nevertheless requires MANUSCRIPT anchors to resolve.
A removed quote cannot resolve against the latest source. Prior source hashes
exist in earlier contexts, but source archive custody and the choice of source
version for each retained anchor need to be explicit. **History H18:** source v1
contains A; source v2 removes its quote; reconciliation orphans A and publishes
the v2 source header. A must remain, but cannot resolve against v2.
**Recommended disposition: close before Increment 1, high confidence on the
missing resolution rule.** This is a historical evidence/liveness gap, not proof
that rejected content is leaked. Resolve anchors against their retained source version, or specify an honest
unavailable-evidence result; never delete the rejection to repair a missing
source. ([header](https://github.com/anotherpanacea-eng/apodictic/blob/20b8ca6219e649b2743866b9ffaba0e77ab208a5/docs/approval-gated-reconstruction.md#L315-L327),
[refresh](https://github.com/anotherpanacea-eng/apodictic/blob/20b8ca6219e649b2743866b9ffaba0e77ab208a5/docs/approval-gated-reconstruction.md#L488-L493),
[anchor check](https://github.com/anotherpanacea-eng/apodictic/blob/20b8ca6219e649b2743866b9ffaba0e77ab208a5/docs/approval-gated-reconstruction.md#L911-L915))

## 3. Important follow-ups, distinguished from the blockers

**F1: `/ready` opt-in detection must survive a missing receipt.** The
integration says a missing receipt runs ordinary `/ready`. A reconstruction
project with its ledger and draft still present but its receipt missing must
not be confused with a project that never opted in. Recommend recognizing
reconstruction artifacts as a reason to require acceptance; no artifacts
retains ordinary `/ready`. This is an Increment-5 integration requirement,
not a claim that Increment 1 can PASS acceptance today.
([ready](https://github.com/anotherpanacea-eng/apodictic/blob/20b8ca6219e649b2743866b9ffaba0e77ab208a5/docs/approval-gated-reconstruction.md#L1059-L1077))

**F2: Do not mistake canonically serialized ledger JSON for a fully specified
Markdown projection.** Anchors and other free strings can contain
line-significant characters unless forbidden. Their ledger representation is
JSON, while graph fields occupy grammar-controlled lines. Specify escaping/continuations for free strings and prove
parse(project(replay)) preserves them. The explicit canonical JSON rules for
Notes already provide a usable precedent. Do not invent a second broad parser
or reject ordinary source punctuation merely to simplify rendering.
([projection grammar](https://github.com/anotherpanacea-eng/apodictic/blob/20b8ca6219e649b2743866b9ffaba0e77ab208a5/docs/approval-gated-reconstruction.md#L300-L345),
[Notes](https://github.com/anotherpanacea-eng/apodictic/blob/20b8ca6219e649b2743866b9ffaba0e77ab208a5/docs/approval-gated-reconstruction.md#L414-L417),
[anchors](https://github.com/anotherpanacea-eng/apodictic/blob/20b8ca6219e649b2743866b9ffaba0e77ab208a5/docs/approval-gated-reconstruction.md#L761-L768))

## 4. Synthetic acceptance candidates

These expected dispositions are this ruling's proposals. They require
independent acceptance before becoming benchmark keys. They are symbolic
histories, not inputs claimed to pass an unbuilt parser.

| Case | Small history or condition | Proposed observable result |
|---|---|---|
| H1 | REQUIRED approved node becomes ORPHANED | Draft-readiness reports unresolved required-but-withheld content; no automatic relaxation |
| H2 | Approved edge retains approval after endpoint becomes ORPHANED | Packet excludes edge and endpoint; map cannot cite them as eligible |
| H3 | Manuscript edge unchanged across re-normalization | No illegal edge Provenance field or fabricated provenance event |
| H4 | Manuscript edge disappears; novel edge is absent from source | Orphan only the manuscript edge; preserve the novel edge's origin exemption |
| H5 | Writer active with incomplete final bytes; gate resumes | Gate waits/refuses without truncating active bytes |
| H6 | Revision hashes to self, REJECTED, APPROVED, or SUPERSEDED existing node | Explicit no-write conflict; existing approvals, rejection, origin and history remain unchanged |
| H7 | Draft repeats exact rejected node or already pending novelty | Report/reuse existing identity; no second mint or empty quarantine bundle |
| H8 | Missing graph and session, valid ledger | Rebuild deterministic projections; no authority-tamper error |
| H9 | Final non-LF suffix with no retained commitment beyond verified prefix | Discard suffix and replay; report recovery |
| H10 | Complete malformed line, bad stored hash, or broken chain | Error; never silently truncate a committed record |
| H11 | Recovery would cross a retained receipt commitment | Error even when suffix otherwise looks torn |
| H12 | Reject A; disappear A; reappear A | A remains REJECTED throughout; only explicit UNREJECT can exit |
| H13 | Withdraw approved endpoint of approved E | Same decision bundle includes E's cascade to PENDING |
| H14 | Request acceptance with otherwise complete pre-Increment-4 artifacts | ACTION-REQUIRED with I5-COMPARATOR-UNAVAILABLE and other provable defects |
| H15 | Ledger advances after a PASS receipt | Existing receipt is stale; `/ready` cannot accept it |
| H16 | Reconstruction ledger/draft remain but receipt missing | Integration refuses acceptance; ordinary non-reconstruction `/ready` remains available |
| H17 | Empty ledger, no retained receipt | Graph stage accepts unstarted state; draft-readiness refuses it |
| H18 | Reconciliation removes a quote and changes source hash | Retain the record and check its anchor against its retained source version, or report unavailable evidence |

H8-H15 are controls for the existing intended behavior. H11 needs an explicit
implementation rule: for each retained receipt with bundle count k and hash h,
require at least k bundles and bundle_hash[k] == h. Merely retaining all record
IDs is insufficient: a missing decision suffix can leave every minted ID intact.
A newer valid ledger head need not equal an older receipt head; compare the
committed prefix. Including these controls is deliberate: a useful review must preserve the good decisions, not count
their restatement as new defects.

## 5. Evidence limits and review

This is one FR-03 contract adjudication with eighteen synthetic acceptance
candidates. It is not a blinded model comparison, a licensed truth judgment,
or implementation of the reconstruction module. The input was the pinned
public contract and ADR, with newly invented symbolic histories. No manuscript,
benchmark answer key, or prior contract ruling was used.

Independent review confirmed R1 and R2, added the empty-ledger finding R5,
and prompted the withdrawal, historical-anchor, check-order, and receipt-prefix
clarifications. Re-review found no remaining material overclaims. This model
review does not promote the proposed cases to benchmark ground truth.

Local evidence checks resolved all 28 immutable source citations and evaluated
four narrow symbolic witnesses: H1's required-but-withheld state, H2's endpoint
eligibility distinction, H6's canonical identity equality, and H17's vacuous
readiness predicates. They did not exercise a production reconstruction parser
or run the eighteen proposed acceptance histories. The pinned source contains
no `approval_graph.py`; the contract and implementation status remain unchanged.
