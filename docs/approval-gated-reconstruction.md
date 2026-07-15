# Approval-Gated Reconstruction over a Provenance-Linked Claim Graph (spec)
## Nonfiction Argument Engine — Companion Module Specification

*Version: 0.2.1*

**Status:** Phase 0 contract hardening in progress (implementation unbuilt)
<!-- built-when: scripts/approval_graph.py -->

*Depends on: Argument State Schema 0.2.0; Dialectical Clarity v2.0*
*Revision 0.2.0 (2026-07-15) folds three independent spec-review passes — schema-compatibility, adversarial red-team, implementability. Reports: `docs/.local/review-log/2026-07-15_approval-gated-reconstruction-spec-review.md`.*
*Revision 0.2.1 (2026-07-15) fixes the deterministic boundary needed before Increment 1: explicit stage selection, separate node/edge field matrices, a parseable event grammar, durable session state, the enforceable limit of rejection-history checks, and an Increment-4 dependency for I5 comparison.*

---

## Purpose

A controlled-authoring workflow: decompose a source document into an approval graph of
atomic claims, support units, warrants, qualifiers, definitions, and typed relationships;
have the author adjudicate every node and every edge; author a **fresh** document from the
approved subgraph only; verify conformance mechanically and semantically; emit a
reconstruction receipt tracing every passage back to approved material; and finish with the
existing holistic review (`/ready`).

The workflow exists for situations where a document must be rebuilt under explicit human
control of its propositional content — e.g., rewriting a piece whose drafting history is
untrusted, converting one form to another (testimony → op-ed) without importing unvetted
claims, or producing a document where every assertion must be traceable to author sign-off.

**One sentence:** approval-gated reconstruction over a provenance-linked claim graph, with
semantic exclusion, novelty quarantine, reconstruction receipts, and final holistic review.

**Scope:** one reconstruction per project. The schema is one-`Argument_State.md`-per-project
and this module's artifacts are singletons; several reconstruction targets from one source
are several projects.

---

## Top-Level Invariants

Everything else in this spec serves these five. A build that violates one of them is wrong
even if it matches every other sentence here.

- **I1 — Changed text is never silently re-approved.** A node whose text changes gets a new
  identity and starts unadjudicated. Approval never transfers across a text change.
- **I2 — Rejection is sticky and text-independent.** No reconciliation event, revision, or
  re-run may remove a REJECTED record from the exclusion set. The only exit from REJECTED
  is an explicit, logged author *un-reject*. (I1 makes stale *approvals* fail-safe; I2 is
  its mirror, making stale *rejections* fail-safe. The first draft of this spec had I1
  only; the red-team review demonstrated that reconciliation and revision each functioned
  as unguarded deletions from the exclusion set.)
- **I3 — The drafter sees only the drafting packet.** Not the source manuscript, not
  anchors, not notes, not flags, not any rejected/superseded/orphaned/pending record.
  Exclusion is defense-in-depth: leak-prevention by construction first, the semantic gate
  as backstop.
- **I4 — The gate never silently passes and never silently drops.** Every verdict is PASS
  or ACTION-REQUIRED with itemized records; there is no warn-and-proceed.
- **I5 — Gate strictness is monotone per reconstruction.** No gate iteration may run with
  a configuration weaker (lower recall, older judge, smaller fixture set) than any earlier
  iteration in the same reconstruction; any relaxation requires an explicit, logged author
  decision recorded in the receipt.

---

## Phase 0 — Deterministic Boundary (normative for Increment 1)

Increment 1 may not infer lifecycle intent or invent an ordering over semantic-gate
configurations. Its command is explicit:

```text
validate.sh argument-reconstruction <PROJECT> --stage graph|draft-ready|acceptance
```

`--stage` is required. `graph` runs Stage A, `draft-ready` runs A–B, and `acceptance`
runs A–C. Artifact presence is validated *after* stage selection; it never selects a
stage. This prevents an incomplete draft or receipt from silently downgrading itself to a
weaker check.

Increment 1 owns graph parsing, identity, state-transition, reconciliation, and Stage A/B
shape checks. It may parse the Stage C envelope, but `acceptance` must return
`ACTION-REQUIRED (I5-COMPARATOR-UNAVAILABLE)` until Increment 4 lands both a structured
gate-config schema and a product partial order with an explicit comparator for every
field. A current config must be greater than or equal to every prior config; an
incomparable field fails closed unless the receipt contains the author-relaxation record
I5 requires. String summaries, judge-name recency, and fixture-set labels are not
mechanically comparable.

Adjudication state is durable in `Adjudication_Session.json`, with exactly these keys:
`schema` (`approval-session/1`), `status` (`OPEN`, `SUSPENDED`, or `CLOSED`),
`graph_sha256`, `opened_at`, `updated_at`, `next_record` (record ID or `null`), and
`decision_count` (non-negative integer). Each decision is flushed to the graph and event
ledger before `decision_count` and `next_record` advance. On resume, the tool validates
the ledger chain and graph first. If a valid contiguous ledger suffix proves that one or
more decisions were flushed after the session file's `graph_sha256`, those decisions are
completed and the tool advances the pointers before presenting another record. A session
is **stale** only when the current graph cannot be derived from that recorded hash by the
valid ledger suffix; stale or malformed is an error, never equivalent to `CLOSED`.
Reconciliation refuses `status: OPEN`; a `SUSPENDED` session may reconcile only after this
recovery step leaves its `graph_sha256` equal to the pre-reconcile graph.

I2 is enforced operationally and comparatively, not claimed as cryptographic persistence.
All tool-owned mutations write an append-only `Approval_Events.jsonl`; each line is one
canonical compact-JSON event under the grammar below. The validator rejects deletion of a
REJECTED record when that record exists in the event ledger, any archived graph, or any
prior receipt available in the project. With no retained prior artifact, deletion of both
a record and all evidence of it is not detectable from a singleton current graph; the
module must state that limit and may not advertise tamper-proof rejection history.

---

## Design Origin and the Excluded Objective

The design borrows one idea from Assembly Theory: **provenance through explicit
construction** — the output is assembled from identified components, and the assembly
record *is* the audit trail. Every unit of the final document traces to components a human
approved.

The design **explicitly excludes** Assembly Theory's quantitative apparatus. Assembly
index rewards substructure reuse; optimizing prose toward reuse compresses it toward
exactly the low-variance, formulaic texture that reads as machine smoothing. Therefore:

- No component of this workflow may compute an assembly index as a target, reward, or
  ranking signal.
- The drafter contract (below) contains an explicit anti-objective clause: reuse,
  repetition, and compression are never goals.

Provenance stays; the optimization objective goes.

---

## Epistemic Contract (Firewall Alignment)

The Nonfiction Argument Engine never adjudicates truth: premise-plausibility flags are
"never a truth verdict" (Argument State Schema § 1), and companion modules "may not convert
[flags] to truth verdicts." This module is where adjudication finally happens — and it is
**author** adjudication, which is where the Firewall says it belongs.

- **APPROVED records author sign-off, not engine-asserted truth.** The graph never
  claims a proposition is true; it claims the author authorized its use.
- **REJECTED records author refusal, not engine-asserted falsity.**
- **The conformance gate enforces author decisions, not validity.** A gate PASS means
  "the draft uses only what the author authorized," never "the argument is sound."
- Engine-surfaced diagnostics (premise flags, warrant status, objection typing) are
  presented to the author *during* adjudication as decision support. They inform the
  human's decision; they never make it.

---

## Non-Goals

- **No truth adjudication** (above).
- **No assembly-index optimization** (above).
- **Not a plagiarism or similarity detector.** The semantic exclusion gate checks the
  draft against *this project's rejected set*, not against external corpora.
- **Not a replacement for `/ready`.** The gate is mechanical conformance; `/ready` remains
  the holistic evaluation. Locally approved pieces can still compose a misleading whole —
  that is `/ready`'s jurisdiction, deliberately kept separate.
- **Not an editing workflow for the source document.** The output is a fresh document.
  Revision of the source belongs to the revision coach.

---

## Pipeline Overview

```
source manuscript ─┐
                   ├─(1) normalize──▶ Approval_Graph.md
Argument_State.md ─┘                       │
                           (2) author adjudicates every node + edge
                               (approval-time exclusion screen runs here)
                                           │
                                  drafting packet (approved
                                  subgraph only — see I3)
                                           │
                                    (3) drafter ──▶ Reconstruction_Draft.md
                                           │         + passage map
                                 (4) conformance gate
                              mechanical + semantic layers
                               │ violations / quarantine │
                               ▼                         │
                     author adjudicates ──▶ re-draft ────┘   (loop until PASS)
                                           │
                             (5) gate emits Reconstruction_Receipt.md
                                           │
                                   (6) /ready (holistic)
```

The normalizer requires **both** inputs: `Argument_State.md` supplies the structure;
the source manuscript supplies the verbatim text for atoms and anchors (the state is
deliberately structure-not-content with coarse locations — approval-grade text cannot come
from it). This mirrors the § 10.9 precedent, whose validator takes `--source` for anchor
resolution.

Loop-backs: gate violations route to a re-draft; quarantined novelty routes to author
adjudication (approve → the content is retroactively authorized and the gate re-runs;
reject → re-draft without it). Quarantine approval inverts the approve-then-draft ordering
by design — that is legitimate *because the author is the authority*, and it is guarded by
the history-surfacing rule in the Approval Protocol (the author decides with any prior
refusal of near-identical content in front of them).

---

## Artifacts

All artifacts live in the project directory alongside `Argument_State.md` and the
editorial letter.

| Artifact | Role | Lifecycle |
|---|---|---|
| `Approval_Graph.md` | canonical persistent graph + adjudication state | persists across re-runs; reconciled, never re-minted |
| `Approval_Events.jsonl` | canonical append-only transition/reconciliation ledger | persists for the project; never truncated or rewritten by module tooling |
| `Adjudication_Session.json` | crash-recovery cursor bound to a graph hash | created on session open; retained as `SUSPENDED`; rewritten atomically per recovered/completed decision; retained as `CLOSED` until the next session replaces it |
| drafting packet | the drafter's entire input (generated export, not hand-assembled) | regenerated from the graph per drafting run; not persisted |
| `Reconstruction_Draft.md` | the fresh document | current unversioned; prior iterations archived as `Reconstruction_Draft_v[N].md` |
| `Reconstruction_Receipt.md` | passage map + gate results + config | paired 1:1 with the draft; archived as `Reconstruction_Receipt_v[N].md` in lockstep |
| `Style_Brief.md` (optional) | author-authored style guidance for the drafter | approved by construction (author-authored); must carry no propositional content about the subject — any substantive proposition traceable only to it is S4 novelty |

**Lifecycle exception, stated for future schema readers:** the schema's archive-and-remint
versioning governs `Argument_State.md` only. `Approval_Graph.md` is deliberately the
opposite — a persistent artifact that reconciliation updates in place — because approval
state must survive re-runs (see Identity and Reconciliation). This satisfies the schema's
single-source-of-truth principle for adjudication state precisely by *not* re-minting.

### `Approval_Graph.md`

Machine-parseable under a strict grammar, validated by `scripts/approval_graph.py`.
**Fixed field order; unknown lines are grammar errors.** File structure: one header block,
then a `## Nodes` section, then a `## Edges` section.

Header block:

```markdown
# Approval Graph
Schema: approval-graph/1
Source manuscript: [filename] — sha256 [64-hex]
Reconciled against: Argument_State_v3
ID length: 12
```

Node record:

```markdown
### Node n-3f8a2c91b04d
Type: CLAIM
Text: [the atomic proposition, self-contained — referents resolved]
Anchors: "[verbatim contiguous quote from the source]" — [location]
         "[second occurrence, if the same proposition recurs]" — [location]
Provenance: C2 (Argument_State_v3) [SPLIT 2/3]
Origin: MANUSCRIPT
Approval: PENDING
Presence: CURRENT
Inclusion: —
Flags: [premise-plausibility / warrant-status annotations carried from the state, or NONE]
Notes: [optional; rejection reasons recommended — they sharpen gate adjudication]
History:
  event:<64 lowercase hex>
```

Node types: `CLAIM` (C0/Cn, post-split), `SUPPORT` (§ 3 support units), `WARRANT` (§ 4),
`QUALIFIER` (§ 4 — the extracted qualifier *proposition*, see Normalization), `DEFINITION`
(§ 2 key terms), `STAKES` (§ 2), `OBJECTION` (§ 6 records), `VIGNETTE` (§ 7).

Edge record:

```markdown
### Edge e-7b01d4e2a9c3
Type: SUPPORTS
Source: n-xxxxxxxxxxxx
Target: n-xxxxxxxxxxxx
Carried typing: [TARGETS edges only — Relation/Basis (+ Condition) from § 6, or —]
Approval: PENDING
Presence: CURRENT
Notes: [optional]
History:
  event:<64 lowercase hex>
```

Edge types: `SUPPORTS`, `WARRANTS`, `QUALIFIES`, `DEPENDS-ON`, `DEFINES`, `TARGETS`,
`ATTACHED-TO`.

Edges are first-class approvable objects. Approving "costs fell" and "the lease ended"
does not approve "costs fell *because* the lease ended" — that causal edge is adjudicated
separately, and a drafter-asserted edge that was never approved is a gate violation.

**Node field-presence matrix** (R = required, O = optional, — = must be absent):

| Field | PENDING | APPROVED | REJECTED | SUPERSEDED |
|---|---|---|---|---|
| Type / Text / Provenance / Origin / Approval / Presence / History | R | R | R | R |
| Anchors | R for Origin: MANUSCRIPT; `NONE (novel)` for Origin: QUARANTINE or AUTHOR-REVISION | same | same | same |
| Inclusion (nodes) | `—` | R (`REQUIRED` or `OPTIONAL`) | `—` | `—` |
| Flags (nodes) | R (may be NONE) | R | R | R |
| Notes | O | O | O (reasons recommended) | O |

**Edge field-presence matrix** (R = required, O = optional, — = must be absent):

| Field | PENDING | APPROVED | REJECTED | SUPERSEDED |
|---|---|---|---|---|
| Type / Source / Target / Approval / Presence / History | R | R | R | R |
| Carried typing | R; `—` unless Type is `TARGETS` | same | same | same |
| Notes | O | O | O (reasons recommended) | O |
| Text / Provenance / Origin / Anchors / Inclusion / Flags | — | — | — | — |

`History:` contains event hashes, one per indented line, in append order:

```text
  event:<64 lowercase hex>
```

Each hash resolves to exactly one line in `Approval_Events.jsonl`. That line is canonical
compact JSON (UTF-8, LF, keys in the order shown, no extra keys):

```json
{"timestamp":"2026-07-15T14:03:00Z","event":"DECISION","actor":"author","record_id":"n-3f8a2c91b04d","approval_from":"PENDING","approval_to":"APPROVED","presence_from":null,"presence_to":null,"reason":null,"prev_hash":"<64 lowercase hex or GENESIS>"}
```

The event hash is SHA-256 over that exact JSON line including neither LF nor a hash field.
Allowed `event` values are `MINTED`, `DECISION`, `UNREJECT`, `WITHDRAWAL`, `REVISE`,
`CASCADE`, and `RECONCILE`. `actor` is `normalizer`, `author`, `system`, or
`reconciliation`. Approval and presence values are the enums in the State Model or
`null`; exactly one axis changes except `MINTED`, which records `null → PENDING` and
`null → CURRENT`, and `RECONCILE`, which changes only Presence or changes neither axis.
A zero-axis `RECONCILE` event is legal only when the same atomic write appends a new local
reference to `Provenance:` for an UNCHANGED record; its non-empty `reason` is that exact
appended reference. `reason` is also required and non-empty for `UNREJECT`, otherwise
string or `null`. `prev_hash` chains the whole project ledger. Unknown keys, missing keys, broken
hashes, broken chain order, an event referenced by zero or multiple records, or a History
sequence inconsistent with the ledger are Stage A errors.

### `Reconstruction_Receipt.md`

Emitted by the **gate runner** (pipeline step 5) per gate run. Contents:

- Draft identity (filename + sha256 over raw UTF-8 bytes) and graph identity (filename +
  sha256 over raw UTF-8 bytes at gate time).
- Event-ledger identity (line count + terminal event hash) and the sorted IDs of all
  REJECTED records at gate time, so a retained prior receipt can prove exclusion-set
  shrinkage even when an old graph snapshot is unavailable.
- The **passage map** (drafter-produced, gate-verified — grammar below).
- Coverage table: every `REQUIRED` node, with the passage(s) realizing it.
- Semantic gate results in the recorded-output grammar (below): per-check verdicts,
  itemized violation and quarantine records (empty on PASS), and the gate configuration
  (judge identity/version, retrieval settings, thresholds, calibration-fixture-set
  version) **plus the config of every prior iteration in this reconstruction** (the I5
  monotonicity record).
- `Argument_State` version(s) consumed; timestamps.

**Passage map grammar.** The draft is segmented exhaustively: every paragraph belongs to
exactly one passage record.

```markdown
### Passage p-14
Span: paragraphs 7–8
Kind: MAPPED
Realizes: n-3f8a2c91b04d, n-90ce44a1f7b2, e-7b01d4e2a9c3
```

`Kind:` is `MAPPED` (with `Realizes:` listing approved IDs) or `DE-MINIMIS` (purely
transitional/metadiscursive; no `Realizes:`). A `DE-MINIMIS` declaration is a claim the
semantic layer verifies (S4), not a free pass.

---

## State Model

Two orthogonal axes plus an origin tag. The first draft of this spec used a single
six-value enum; review showed it conflated author decisions with reconciliation status,
which is exactly what let reconciliation overwrite a rejection.

**Approval axis** — author decisions only:

| State | Meaning |
|---|---|
| `PENDING` | not yet adjudicated (initial state; also entered by un-reject, withdrawal, and system cascades) |
| `APPROVED` | author authorized use (nodes additionally carry `Inclusion: REQUIRED / OPTIONAL`) |
| `REJECTED` | author refused. In the exclusion set (see below) |
| `SUPERSEDED` | replaced via the revise action. Terminal |

**Presence axis** — reconciliation status only, never touches Approval:

| State | Meaning |
|---|---|
| `CURRENT` | derivable from the latest normalization (or non-manuscript origin) |
| `ORPHANED` | Origin: MANUSCRIPT record no longer derivable from the latest normalization |

**Origin tag** — `MANUSCRIPT` (via normalizer), `AUTHOR-REVISION (of n-x)` (via revise),
`QUARANTINE (draft v[N])` (via S4). Only `MANUSCRIPT` records participate in
DISAPPEARED detection; the other origins are never orphaned by reconciliation.

**Legal transitions** (anything not listed is illegal; the mechanical gate validates every
`History:` line against this table):

| From → To | Actor | Notes |
|---|---|---|
| PENDING → APPROVED | author | triggers the approval-time exclusion screen |
| PENDING → REJECTED | author | |
| APPROVED → PENDING | author | withdrawal, logged |
| APPROVED → REJECTED | author | logged |
| REJECTED → PENDING | author | **un-reject: the only exit from REJECTED.** Requires a logged reason. No direct REJECTED → APPROVED — un-reject then approve, two deliberate steps |
| PENDING / APPROVED → SUPERSEDED | author (revise) | **revise is forbidden on REJECTED records** — replacing a rejection is laundering; un-reject first |
| APPROVED edge → PENDING | system cascade | automatic when either endpoint node leaves APPROVED; logged as a system event |
| CURRENT ↔ ORPHANED | reconciliation | Presence axis only; Approval untouched |

**Exclusion set** = every record with `Approval: REJECTED`, regardless of Presence axis
(an ORPHANED rejection still excludes — I2). Un-reject is the only operation that shrinks
the exclusion set, and it is logged.

**Edge–endpoint coupling:** an edge may be APPROVED only while both endpoints are
APPROVED. The cascade row above maintains this; the mechanical gate enforces it as an
integrity check. (Without this, an approved QUALIFIES/TARGETS edge into a rejected node
both leaks the rejected proposition's existence into the drafting packet and evades the
rejected-edge check.)

**Rejected records are never deleted.** They are load-bearing: the exclusion gate reads
them. Deletion, revision, and orphaning are all just spellings of "remove from the
exclusion set," and I2 forbids all of them.

---

## Identity and Reconciliation

### Why local IDs cannot be the key

The schema's local IDs do not survive re-runs: each audit re-run archives the old state and
mints a fresh `Argument_State.md` with fresh numbering, and § 4's `Defeater refs` field is
explicitly "PROJECTION ONLY — … non-stable across reruns; resolved by no validator."
Approval state keyed to `Cn`/`On`/`Pn` would dangle on the first re-audit. In this
workflow, re-audits are routine.

### Content-addressed IDs

- **Node ID:** `n-` + first 12 hex chars of SHA-256 over the canonical string
  `<node-type> "\n" <canonicalized text>`. Canonicalization: Unicode NFC, collapse internal
  whitespace runs to single spaces, strip leading/trailing whitespace. Case is preserved
  (it can carry meaning). Anchors are deliberately **not** hashed: an identical proposition
  that moved in a revised draft keeps its identity and its approval.
- **Edge ID:** `e-` + first 12 hex chars of SHA-256 over
  `<edge-type> "\n" <source-node-id> "\n" <target-node-id>`.
- **ID length is fixed at 12 hex (48 bits), declared in the graph header, and an ID is
  never mutated after minting.** At claim grain (tens of nodes) a 48-bit collision between
  *distinct* canonical strings is astronomically unlikely; if one ever occurs at mint time
  it is a hard validator error, not an auto-remediation (auto-lengthening would mutate
  approval keys).
- **Identical canonical strings are the same node by design** — not a collision. A
  proposition that recurs in the source dedupes to one node with multiple `Anchors:`
  entries and is adjudicated once. (Consequence, stated deliberately: you cannot approve a
  proposition in one location and reject the same proposition in another. At claim grain
  that is the correct semantics — adjudication is about *what may be said*, not where it
  was said.)
- **The validator recomputes every ID from its record's canonical content and fails on
  mismatch.** I1 is enforced by this check, not by convention — without it, hand-editing
  `Text:` under an existing ID silently carries approval onto altered content.

The key property: **changed text ⇒ changed ID ⇒ no inherited approval** (I1).

### Reconciliation procedure (per diagnostic re-run)

Reconciliation is **blocked while an adjudication session is open** — finish or suspend
the session first. When a new `Argument_State_v[N]` exists, the normalizer re-runs against
it plus the manuscript, and the tool reconciles:

| Case | Detection | Result |
|---|---|---|
| UNCHANGED | new atom's ID already in graph | Approval state carries; new local ref appended to `Provenance:` with a zero-axis `RECONCILE` event |
| NEW | ID not in graph | node added as `PENDING` / `CURRENT` |
| DISAPPEARED | a `MANUSCRIPT`-origin record's ID absent from the new normalization | `Presence: ORPHANED` (Approval untouched — a REJECTED record stays REJECTED and stays in the exclusion set, per I2) |
| REAPPEARED | an ORPHANED record's ID present again | `Presence: CURRENT` (Approval untouched) |

`AUTHOR-REVISION` and `QUARANTINE` origin records are exempt from DISAPPEARED detection —
they never derived from the manuscript, so their absence from a normalization is not
evidence of anything.

"Changed" is not directly detectable by hash (it presents as NEW + DISAPPEARED). The tool
MAY suggest lineage between a NEW and a DISAPPEARED record (e.g., by embedding similarity)
to save the author re-reading, but a suggestion **never transfers approval** — the new
record is `PENDING` regardless. Lineage suggestions involving a REJECTED disappeared
record are surfaced with that rejection prominently displayed (see Approval Protocol —
history surfacing).

`Provenance:` is append-only across reconciliations (a list, newest last); `SPLIT k/n`,
`author revision of n-x`, and per-run local refs coexist as separate entries.

---

## Normalization Rules (`Argument_State.md` + manuscript → graph)

Normalization is a **prompt-contract task, not a script task**: atomization, referent
resolution, qualifier extraction, and edge re-homing are model-judgment work. The
deterministic `scripts/approval_graph.py` mints/verifies IDs, parses and validates the
grammar, and runs reconciliation by hash — it never makes judgment calls. (Increment 1
builds both halves; see Build Increments.)

1. **Atomization.** One proposition per node. Each atom must be self-contained: pronouns
   and elided referents resolved (bracketed insertions preferred, preserving the author's
   wording otherwise). A compound `Cn` splits into sub-atoms with `SPLIT k/n` provenance.
2. **Anchors.** An anchor is a contiguous verbatim quote from the source manuscript,
   resolvable by normalized substring match, plus a location. Anchor spans are kept
   minimal — the span that grounds *this* atom, not the whole containing sentence.
   (Anchors are audit data. They never enter the drafting packet — I3 — because a source
   sentence routinely contains an approved atom's text adjacent to a rejected clause.)
3. **Edge re-homing on splits.** § 4 warrants and § 6 objection targets are keyed per-`Cn`.
   When a `Cn` splits, every attached edge is re-homed to the correct sub-atom(s) — and
   every re-homed `WARRANTS` edge is forced to `PENDING` with a review note, never
   inherited: a warrant for the compound claim may not survive the split.
4. **Qualifier extraction.** § 4's `Qualifier` field is an assessment enum
   (MATCHED / OVERCONFIDENT / UNDERCLAIMED), not content. The normalizer extracts the
   actual qualifier proposition from the manuscript (via the state's location) as a
   `QUALIFIER` node with a `QUALIFIES` edge. Where § 4 flagged OVERCONFIDENT/UNDERCLAIMED,
   that flag is carried onto the node as decision support.
5. **Support and warrant minting.** § 3 support units and § 4 warrants have no IDs in the
   schema at all (§ 6 says `Target: Cn.support` as a path expression precisely because
   there is nothing to point at). The normalizer mints them as first-class nodes.
6. **Objections carry their typing.** § 6 `Target`/`Relation`/`Basis` (and `Condition` for
   warrant-defeaters) transfer onto `TARGETS` edges as `Carried typing`. Legacy untyped
   records normalize with typing absent (valid, per schema R2).
7. **Diagnostic sections are not content.** § 5 (burden/scope), § 8 (cross-section
   tracking), § 9 (summary) are assessments of the argument, not parts of it. They are not
   normalized into nodes; they surface to the author as adjudication-time context.
8. **Premise flags annotate, never gate.** § 1 premise-plausibility flags attach to the
   matching nodes' `Flags` line. Consistent with the Firewall, a flag never auto-rejects.

**Grain expectation:** claim-level, not fragment-level. A typical op-ed/brief should
normalize to roughly 20–80 nodes. If normalization produces hundreds of nodes for a short
document, the atomization criteria are being applied below claim grain — that is a
normalizer bug, not an approval burden the author should absorb.

---

## Approval Protocol

- **Completeness before drafting:** every node and every edge must leave `PENDING`
  (mechanically enforced). There is no "approve the rest silently."
- **Ordering:** nodes are adjudicated before their incident edges (an edge decision is
  meaningless while its endpoints are undecided; the session presents edges only once both
  endpoints are adjudicated, and the edge–endpoint coupling rule constrains the outcome).
- **Presentation:** each record is shown with its `Text`, its `Flags` (the engine's
  non-adjudicative decision support), and relevant § 5/§ 8/§ 9 context. The author's
  decision and optional note are captured into the record and its `History:` line.
- **Decisions:** `APPROVED` (with `Inclusion: REQUIRED | OPTIONAL`), `REJECTED`, or
  **revise** — the author supplies replacement text, which mints a *new* node
  (`Origin: AUTHOR-REVISION (of n-x)`) starting `PENDING`, while the original becomes
  `SUPERSEDED`. Revise is **forbidden on REJECTED records** (see State Model).
- **Approval-time exclusion screen.** When a record is approved, the semantic tooling
  screens the newly approved text against the exclusion set (same retrieval + entailment
  machinery as the gate, single record). A hit blocks the approval pending author
  resolution: un-reject the conflicting rejection (logged), or decline the approval.
  Without this screen, an approved record that entails a rejected one makes the gate
  either unsatisfiable (every faithful realization flags) or a coin-flip on judge recall.
- **History surfacing.** Whenever the author adjudicates a quarantine record, a revise
  replacement, or a NEW record with a suggested lineage to a REJECTED/ORPHANED record, the
  session retrieves and displays any entailment-near REJECTED records first. The author
  may still approve — but with their own prior refusal in front of them, not behind them.
- **Exclusion set = REJECTED only** (on the Approval axis; Presence is irrelevant — I2).
  `SUPERSEDED` and `ORPHANED` records are withheld from the drafter but are *not* in the
  exclusion set — the author replaced or lost them; they did not refuse them. Only refusal
  creates an exclusion obligation, and only un-reject removes one.
- **Sessions are resumable and crash-safe.** The tool persists each decision as it is made
  (append-safe write per adjudication, not a save-at-end). An interrupted session loses at
  most the in-flight decision. Progress (`k of n adjudicated`) is always reportable.
  Reconciliation is blocked while a session is open.

---

## Drafter Contract

- **Input: the drafting packet and nothing else** (I3). The packet is a generated export
  containing: per approved node — ID, Type, Text, Inclusion; per approved edge — ID, Type,
  endpoints, Carried typing; the § 1 context fields (form, goal, audience); the approved
  `Style_Brief.md` if present. It contains **no** anchors, notes, flags, history,
  provenance, and no record in any state other than APPROVED. The drafter never sees the
  source manuscript.
- **Output:** `Reconstruction_Draft.md` plus the passage map (grammar above): an
  exhaustive segmentation of the draft into MAPPED passages (with realized IDs) and
  DE-MINIMIS passages. The map is the drafter's self-report; the gate verifies it rather
  than trusting it (see Conformance Gate).
- **Free:** ordering, emphasis, transitions, paragraphing, sentence-level style — the
  authorial whole. These are exactly what a bag of atoms does not determine, and the
  drafter is expected to supply them. (Freedom of arrangement is not freedom of assertion:
  structure that *asserts* an unapproved or rejected relationship — a cause→effect
  section sequence, a framing heading — is checked by S2's structural pass.)
- **Not free:** asserting any substantive proposition or relationship not entailed by the
  approved subgraph. Such content is not an error to hide but a **quarantine record to
  declare** (the gate will find it regardless; a drafter that self-declares novelty
  produces faster loops).
- **Anti-objective clause:** the drafter is never instructed to maximize reuse of approved
  phrasing, minimize construction steps, or compress. Approved *propositions* constrain
  content; they do not prescribe wording.

---

## Conformance Gate

Two layers, split on what can run offline. This follows the § 10.9 precedent (a
prompt-driven audit with a mechanical `validate.sh` gate over its artifacts).

### Mechanical layer — `validate.sh argument-reconstruction` (deterministic, CI-runnable)

Named `argument-reconstruction` (not `reconstruction`) to avoid colliding with the
existing "recon = reconnaissance" namespace (`argument-recon-prerequisite`, Field Recon).
Checks are staged by the required `--stage graph|draft-ready|acceptance` option defined in
Phase 0. Artifact presence never selects or weakens the requested stage:

**Stage A — graph integrity** (whenever `Approval_Graph.md` exists):
- Grammar parses (fixed field order; unknown lines are errors); header block complete.
- **Every node/edge ID recomputes from its canonical content** (I1's enforcement).
- ID uniqueness; referential integrity (edge endpoints exist).
- Field-presence matrix satisfied per record state.
- Every `History:` transition is legal per the State Model table.
- Every History hash resolves against the complete, hash-chained `Approval_Events.jsonl`;
  available archived graphs and prior receipts contain no REJECTED record missing from the
  current graph unless its ledger shows an author `UNREJECT` transition.
- Edge–endpoint approval coupling holds.
- Origin/Anchors consistency (MANUSCRIPT records have resolvable anchors; QUARANTINE /
  AUTHOR-REVISION records carry `NONE (novel)`).

**Stage B — draft-readiness** (before a drafting packet is generated):
- Stage A, plus: zero `PENDING` records; every APPROVED node carries `Inclusion:`.

**Stage C — draft acceptance** (when a draft + receipt exist):
- Stages A–B, plus:
- Passage map parses; it covers **every paragraph of the draft exhaustively** (an
  unmapped paragraph is a hard failure — an incomplete self-report must not shrink the
  gate's coverage); every `Realizes:` ID exists and is APPROVED.
- Every `REQUIRED` node appears in some passage's `Realizes:`.
- Receipt completeness: semantic-layer results present in the recorded-output grammar
  with verdicts; config block present **and not weaker than any prior iteration's** (I5).
  Until Increment 4 defines the structured config and comparison order, this check fails
  closed with `I5-COMPARATOR-UNAVAILABLE` as specified in Phase 0;
  draft and graph hashes in the receipt match the files on disk.
- Zero open quarantine records; zero unresolved violations.

### Semantic layer — model-driven, results recorded in the receipt

Architecture per check: **candidate generation for recall, entailment judgment for the
decision.** Similarity alone cannot make the call — "the lease ending caused the savings"
and "the lease ending did *not* cause the savings" are near-neighbors in embedding space
and logical opposites. Candidate generation (an embedding index or judge-directed scan —
functional requirement is recall on the calibration fixtures, not a specific mechanism;
it runs at author-time, never in CI) proposes candidate (draft-span, graph-record) pairs;
an entailment/contradiction judge decides each pair. **Draft spans are segmented from the
full raw draft text, never from the passage map** — the map is itself under audit.

- **S1 — Node exclusion.** No part of the draft may *assert* a `REJECTED` proposition.
  Two passes:
  - *Span pass:* single spans and contiguous multi-sentence windows, judged pairwise
    against each rejected record.
  - *Composition pass:* for each rejected record, retrieve all draft spans sharing its
    entities/predicates — wherever they sit in the document — and judge the
    **conjunction** of that span set against the rejected proposition. (Two truthful
    spans, one in the intro and one in the conclusion, can jointly entail a rejected
    claim that neither entails alone; pairwise judging never sees it.)
  Assertion, not mention: a rejected claim appearing under negation, or under *genuine*
  attribution in order to be rebutted, is a mention and is permitted. Endorsed attribution
  ("as X rightly argues…", attribute-then-concede) is a use. **Projective content counts
  as assertion:** presuppositions and factives smuggle rejected content past at-issue
  entailment ("costs *returned* to normal" asserts the rejected prior abnormality;
  "when did costs fall after the lease ended?" presupposes the rejected ordering).
  The judge is prompted and fixtured on all three distinctions.
- **S2 — Edge exclusion.** No rejected relationship may be asserted, at any granularity:
  - *Sentence pass:* explicit statement and juxtaposition-implicature ("Costs fell. The
    lease had just ended.").
  - *Structural pass:* section ordering, adjacency, and heading framing that assert a
    rejected relation (a "What changed" heading over lease-then-costs sequence asserts
    the rejected causal edge without a single flaggable sentence).
  This is the hardest check; it errs toward flagging, and flags route to the author,
  never to silent failure.
- **S3 — Coverage and qualifier fidelity.** Every `REQUIRED` node must be entailed by some
  draft span (direction: draft ⊨ atom). Additionally, the draft must not *strengthen* an
  approved qualified claim past its approved qualifier — realizing approved
  "X, in most observed cases" as "X, always" is an overclaim flag. Scalar drift toward a
  rejected stronger neighbor ("many were denied" realized as "the border was effectively
  sealed" when "all were denied" is REJECTED) is fixtured under this check jointly with S1.
- **S4 — Novelty quarantine.** Substantive draft propositions/relations not entailed by
  any approved record become quarantine records: appended to the graph as `PENDING` with
  `Origin: QUARANTINE (draft v[N])`, `Anchors: NONE (novel)`, and routed to adjudication
  (with history surfacing — see Approval Protocol). If approved, the author assigns
  `Inclusion:` like any node and the content is retroactively authorized; the gate then
  re-runs. **De minimis is a property of propositional content, not surface form:**
  a passage is DE-MINIMIS only if it asserts nothing beyond metadiscourse. "Consider
  first the budget" is de minimis; "Consider first the budget crisis everyone now
  acknowledges" embeds two substantive claims and is not. S4 verifies every DE-MINIMIS
  declaration in the passage map against this standard.

**Directionality is part of the spec:** exclusion tests *draft ⇒ rejected*; coverage tests
*draft ⇒ required-approved*. These are different tests with different failure costs and are
calibrated separately.

### Recorded-output grammar (what the judge writes into the receipt)

```markdown
### Gate Run 3
Timestamp: [ISO]
Judge: [identity/version]
Config: candidates=[settings] thresholds=[per-check] fixtures=[set version]
Prior configs: [run 1 → summary; run 2 → summary]        (I5 record)
Verdict: PASS | ACTION-REQUIRED

#### Violations
### Violation x-01
Check: S1-span | S1-composition | S2-sentence | S2-structural | S3-coverage |
       S3-overclaim | S4-novelty | S4-de-minimis
Draft span(s): "[quote]" — [location] (composition records list every span)
Graph record: n-xxxxxxxxxxxx | e-xxxxxxxxxxxx | NONE (novelty)
Judgment: [one-sentence basis]
Disposition: OPEN | RESOLVED ([how])
```

The mechanical layer shape-checks these records (Stage C) exactly as the § 10.9 AGD gate
shape-checks its move records; it never re-runs the judgments.

### Calibration

Fixture families (living in `evals/`, the repo's behavioral ground-truth track, one
manifest + expected-verdict rubric per fixture per the house template):

1. paraphrase (single-span)
2. distributed paraphrase (contiguous multi-sentence)
3. dispersed composition (spans far apart whose conjunction entails a rejected record)
4. negation (rejected content asserted-false is permitted — the judge must not fire on
   similarity)
5. quotation/attribution — mention (genuine rebuttal context, permitted)
6. endorsed attribution — use ("as X rightly argues", attribute-then-concede; flagged)
7. presupposition/factive/projective content (flagged as assertion)
8. qualification shifts, both directions (overclaim past approved qualifier; underclaim)
9. scalar approach toward a rejected stronger neighbor
10. compositional laundering (sentence juxtaposition asserting a rejected edge)
11. structural implicature (ordering/heading/section-sequence asserting a rejected edge)
12. metadiscourse-carrying-substance (S4 must flag) and true de minimis transitions
    (S4 must pass)

Exclusion and coverage thresholds are calibrated independently — preservation of approved
meaning and exclusion of rejected meaning are asymmetric tasks, and neither inherits
thresholds from any prior semantic-fidelity work. Per family, the calibrated metric is
recall for the exclusion families (1–3, 6–7, 9–11) and judgment accuracy for the
permitted-content families (4–5, 12): a false exclusion flag costs the author minutes of
adjudication; a missed exclusion defeats the workflow's purpose — so exclusion is tuned
for recall, with the author as the precision filter.

**Verdicts:** `PASS` or `ACTION-REQUIRED` (itemized violations and/or quarantine records).
There is no warn-and-proceed (I4).

---

## `/ready` Integration

The gate runs **before** `/ready`, and the separation is deliberate: the gate is
mechanical conformance to author decisions; `/ready` is holistic quality. When a
`Reconstruction_Receipt.md` is present in the project, `/ready` validates it before the
holistic pass:

- the receipt's draft hash matches `Reconstruction_Draft.md` on disk;
- the receipt's **graph hash matches `Approval_Graph.md` on disk** (re-adjudicating the
  graph after a PASS invalidates the receipt — without this check, a stale-but-passing
  receipt survives its own graph);
- the verdict is `PASS`.

Otherwise `/ready` reports the stale/failing receipt and stops. `/ready` binds to the
current (unversioned) draft/receipt pair; archived `_v[N]` pairs are history, not inputs.
A project with no receipt runs `/ready` unchanged (the module is opt-in).

---

## Argument State § 10 Registration

The module registers as companion subsection **§ 10.10 Approval-Gated Reconstruction**.
Registration is an additive edit to `argument-state-schema.md` (a `### 10.10` stub in the
§ 10 list plus a "Subsection responsibilities" entry); per the schema's versioning rules
this does not bump the schema version. Annotations are signed and timestamped per the
annotation protocol:

```markdown
### 10.10 Approval-Gated Reconstruction
_Annotated by: approval-gated-reconstruction — [ISO timestamp]_
- Normalization summary (node/edge counts by type, splits, re-homed edges)
- Adjudication progress and outcome summary
- Gate verdicts per draft iteration
- Working artifacts reference: Approval_Graph.md, Reconstruction_Receipt.md
- Full contract reference: [the module's craft contract — path fixed at Increment 2/3]
```

(§ 10.6–10.8 use a "Full results reference" file pattern and § 10.9 a "Full contract
reference"; this subsection uses both, and the distinction is kept — the graph and receipt
are working artifacts, the craft contract is the module's behavioral spec.) The module
obeys the annotation protocol: it reads §§ 1–9, writes only its own subsection, and never
modifies §§ 1–9.

---

## Build Increments

1. **Deterministic validator + normalizer prompt contract + graph artifact.**
   - `scripts/approval_graph.py`: grammar parser, ID minting/recomputation, field-presence
     and transition-legality checks, event-ledger/session validation, reconciliation by
     hash, complete Stage A–B checks, and the fail-closed Stage C envelope described in
     Phase 0 — the deterministic half only; it makes no judgment calls. *This is the
     built-when target.*
   - The normalization **prompt contract** (atomization, referent resolution, qualifier
     extraction, edge re-homing — the model-judgment half), emitting `Approval_Graph.md`
     for the script to validate.
   - `validate.sh argument-reconstruction <PROJECT> --stage graph|draft-ready|acceptance`
     wiring, following the § 10.9 dispatch pattern:
     thin `validate.sh` case → `approval_graph.py`; joins the single-sourced
     `AGG_VALIDATORS` list and the usage Commands string; ships a `--self-test` dispatcher
     case (CI's `validator-conventions` meta-linter and `--self-test-all` both require it).
   - **Mirror obligation:** `approval_graph.py` and the `validate.sh` dispatch exist
     byte-identical in root `scripts/` (what CI runs) and `plugins/apodictic/scripts/`
     (canonical); sync by hand as the last step before `--check-all` and verify with
     `validate.sh check-mirror`.
2. **Approval workflow.** The adjudication session contract (presentation order,
   decision capture, approval-time exclusion screen, history surfacing, resumable,
   crash-safe, progress-reporting), as a command/skill following house patterns. The
   craft contract file lands under the owning skill's `references/craft/` directory
   (the § 10.9 precedent's real location — `plugins/apodictic/skills/<skill>/references/
   craft/`); its exact path is fixed here and in § 10.10 when the owning skill is chosen.
3. **Drafter contract + packet generator + receipt emission.** The drafting-packet export,
   the drafting prompt contract, the passage-map grammar, receipt emission by the gate
   runner, and draft/receipt versioning.
4. **Semantic gate + calibration fixtures.** The candidate-generation + entailment-judge
   contract, the recorded-output grammar, and the twelve `evals/` fixture families with
   per-family metrics; thresholds set from fixtures, not defaults.
5. **`/ready` receipt validation.** The stage-6 integration (draft hash + graph hash +
   verdict).

Each increment lands via the standard flow (spec review → build → review → Codex PR) with
a `changelog.d/<slug>.md` fragment. The status-drift lint arms as soon as the Increment-1
deliverable exists (any-true marker semantics); from that point the Status line above must
read as partially built (e.g., "Increment 1 built; 2–5 unbuilt") until the module is
complete.

---

## Open Questions

1. **Judge implementation.** The repo is prompt/skill-based with no model runtime in CI —
   the entailment judge is a prompt contract (like § 10.9's AGD audit), with `validate.sh`
   shape-checking its recorded outputs rather than re-running it. Is that sufficient, or
   does the semantic gate warrant an offline NLI model for reproducibility?
2. **Threshold defaults.** None are specified here on purpose; they come from the
   Increment-4 fixture calibration.
3. **Approval-time exclusion screen cadence.** Per-decision (immediate feedback, more
   judge calls) vs. batched at session end (cheaper, but conflicts surface after the
   author has moved on). Leaning per-decision; Increment 2 decides with usage data.
4. **Assisted lineage suggestions** (reconciliation): worth the complexity, or does
   NEW+ORPHANED with author re-read suffice at claim grain? (If built, the
   rejected-lineage surfacing rule in the Approval Protocol is mandatory, not optional.)
5. **Owning skill** for the craft contract and command surface (fixes the § 10.10
   contract-reference path and the Increment-2 marker target).

---

*This module is where the engine's non-adjudicative diagnosis meets author adjudication:
the audit surfaces the argument's structure, the author decides what may be said, and the
reconstruction proves it said only that. The engine cannot make the approval decisions;
that is the point.*
