# Feedback Triage — sort, validate, prioritize external feedback

<!-- built-when: scripts/feedback_triage.py contains "maps_to" -->

**Status:** Increments 1–2 **built**. Roadmap: `ROADMAP.md` → Workflows → Feedback Triage. Implementation: `scripts/feedback_triage.py`, `validate.sh feedback-triage` (+ canonical `--check-all` gate), `commands/triage-feedback.md`, `revision-coach/references/feedback-triage.md`, schema `apodictic.feedback_item.v1`.

A writer returns after circulating a draft — beta readers, a critique group, an agent or editor — carrying a pile of external feedback that is often **contradictory, uneven in quality, and unvalidated**. "Cut the prologue" from one reader; "add a prologue" from another. A claim that the midpoint sags (which the diagnosis already caught) sitting next to a claim about voice that no pass has confirmed. The job is not to obey the feedback — it is to **sort it, check each claim against the manuscript, prioritize, and resolve the contradictions** before any revision time is spent.

This is a returning-author workflow, so it lives in the **revision-coach** skill and inherits the coaching firewall: the coach **structures and prioritizes** feedback and **routes targeted validation back to the Core Editor** (it never runs passes or re-diagnoses itself). What this track adds is the machine-checkable spine under that conversation.

## The structured artifact

Each feedback item is recorded as a real-JSON `apodictic.feedback_item.v1` block (same HTML-comment envelope and schema engine as `apodictic.finding.v1`) inside a `[Project]_Feedback_Triage_[runlabel].md` artifact:

```markdown
<!-- apodictic:feedback_item
{
  "schema": "apodictic.feedback_item.v1",
  "id": "FB-01",
  "source": "Beta reader A",
  "claim": "The middle third drags and the midpoint doesn't land.",
  "assessment": "validated",
  "triage": "act-now",
  "conflicts_with": [],
  "evidence_refs": ["Pass 5 §Pacing", "Ch. 9"],
  "disposition": "Matches the Pass 5 pacing-collapse finding; revise the middle third first."
}
-->
```

**Two orthogonal axes, deliberately kept separate** (mirroring the v2.0.0 severity / confidence / readiness discipline):
- **`assessment`** — did *APODICTIC's own analysis* confirm the external claim? `validated` / `partly-validated` / `refuted` / `unverifiable` / `pending`. This is the truth axis.
- **`triage`** — what we will *do*: `act-now` / `act-later` / `monitor` / `decline`. This is the disposition axis. It is intentionally **not** the canonical Must-Fix/Should-Fix/Could-Fix severity scale — a feedback item is a claim about the manuscript, not a finding; its severity (if validated) lives on the finding it maps to.

`conflicts_with` lists the IDs of feedback items this one contradicts. `id` is `FB-<NN>` (unique per triage). `maps_to` (Increment 2, optional) is the Finding-Lifecycle id (`F-<ORIGIN>-<NN>`) this item points at in the Findings Ledger — the structured successor to the prose "maps to F-…" link. The field set is canonical in `schemas/apodictic.feedback_item.v1.schema.json`, not in prose.

## The `feedback-triage` validator

`validate.sh feedback-triage <run_folder>` (or explicit files: `<triage.md> [<ledger.md>]`). Resolves the `*_Feedback_Triage_*.md` artifact, parses its `feedback_item` blocks via the shared `apodictic_artifacts` engine, and checks the workflow's machine-checkable invariants. Increment 2 adds an **optional second file — the Findings Ledger** (`*_Findings_Ledger_*.md`, or an explicit file with `apodictic.finding.v1` blocks); when it is present the `maps_to` cross-check (E5/W4) engages, exactly like `finding-trace` / `ledger-consolidation` take a paired artifact. When no ledger is supplied (or it carries no finding blocks) the cross-check is skipped and only the self-contained schema + conflict checks run — a clean degrade, never a false failure. Degrades to an advisory `WARN` without `python3`.

| ID | Severity | Rule |
|---|---|---|
| **E1 — invalid item** | ERROR | A `feedback_item` block fails its schema (bad `assessment`/`triage` enum, malformed `id`, missing required field, or broken JSON). Delegated to the schema engine. |
| **E2 — duplicate id** | ERROR | Two items share an `FB-NN` id. IDs must be unique per triage so `conflicts_with` references are unambiguous. |
| **E3 — dangling conflict** | ERROR | An id in some item's `conflicts_with` does not resolve to a real item in the artifact — a typo or a deleted item leaves a broken contradiction reference. |
| **E4 — self conflict** | ERROR | An item lists its own id in `conflicts_with`. |
| **W1 — unresolved conflict** | WARN (ERROR under `--strict`) | Two items contradict (`conflicts_with`, treated as an **undirected** graph — one-sided declaration counts) but **both** remain actionable (`act-now`/`act-later`). The contradiction was never resolved; acting on both would produce incompatible revisions. Resolution = decline or park (`monitor`) one side. This is the roadmap's "conflict resolution when feedback contradicts itself," made checkable. |
| **W2 — act-on-unvalidated** | WARN (ERROR under `--strict`) | An item triaged `act-now` whose `assessment` is not `validated`/`partly-validated`. Spending revision time *now* on a claim our own analysis hasn't confirmed. Advisory because a writer may legitimately act on a trusted-source claim ahead of formal validation; `--strict` makes it a gate. |
| **W3 — unreconciled decline** | WARN (ERROR under `--strict`) | An item triaged `decline` whose `evidence_refs` contain a ledger `F-…` id, with no disposition marker for that id in the same artifact — "declined feedback maps to engine finding F-… but no disposition was recorded — the decline lives only in this artifact." The mechanical nudge behind the decline-reconciliation flow (below; `docs/finding-dispositions.md`). **Ownership boundary (W3 vs disposition-check DP2.2):** W3 is feedback-triage-**artifact**-scoped advisory — it never reads the sidecar; DP2.2 is **sidecar**-scoped ledger-integrity — it never reads triage artifacts. |
| **E5 — dangling maps_to** (Increment 2) | ERROR | An item's `maps_to` finding-id does not resolve to a real `apodictic.finding.v1` in the paired Findings Ledger — a phantom or typo'd finding reference. Cross-artifact referential integrity, assessment-independent (a recorded `maps_to` must always resolve), mirroring `finding-trace` E1. Requires the ledger; skipped entirely when none is supplied. |
| **W4 — unmapped validated** (Increment 2) | WARN (ERROR under `--strict`) | A `validated` item (the truth axis, not `partly-validated`) that carries no `maps_to` — the spec's "a validated feedback item must point at a real `F-…`", made checkable. **Advisory by default** so an item validated *ahead of* its ledger entry, and every pre-Increment-2 artifact, stays valid; `--strict` is the finalize/CI gate. Like E5, it engages only in the two-file cross-check mode (a ledger is present). |

**Report.** One line per item — `id · source · assessment · triage · conflicts` — so the writer (and `/coach`) sees the whole triage at a glance. Exit `0` clean / WARN-only, `1` on any ERROR (or WARN under `--strict`), `2` usage.

**Ownership boundary.** `feedback-triage` owns *contract hygiene + conflict referential integrity + the contradiction-coherence gap + (Increment 2) feedback→ledger `maps_to` referential integrity* — classes no other validator raises. It does **not** judge severity (a validated item that maps to a finding is governed by the finding/severity validators once it enters the ledger) and it does **not** re-diagnose (validating a claim is a Core Editor targeted pass, not this validator's job).

### The `maps_to` cross-check (Increment 2)

Increment 1 links a validated claim to its finding in prose ("Matches the Pass 5 pacing-collapse finding"). Increment 2 makes that link **structured and checkable**: an optional `maps_to: "F-<ORIGIN>-<NN>"` on the feedback item, cross-checked against the paired Findings Ledger.

- **E5 (dangling `maps_to`) — hard ERROR, referential integrity.** A recorded `maps_to` must resolve to a real ledger finding, *regardless of assessment* — a phantom finding reference is broken whether the item is validated, refuted, or pending. This mirrors `finding-trace` E1 exactly (letter→ledger citation integrity) and is the unambiguous half of the spec.
- **W4 (`validated` without `maps_to`) — advisory presence gate.** The spec reads "a `validated` feedback item must point at a real `F-…`." The **required-vs-optional** question — is a validated item that carries *no* `maps_to` a failure? — is genuinely ambiguous in that wording. The safe reading, chosen here: **presence is checked but advisory by default**, an ERROR only under `--strict`. This keeps the schema field additive (every pre-Increment-2 artifact stays valid) and lets a writer mark a claim `validated` *before* its ledger finding is locked (the coach's step 2 "Validate" precedes step 3 "Map to findings"), while still gating the miss at finalize/CI. W4 keys on `assessment == "validated"` exactly — not `partly-validated` — matching the spec's word. (If a stricter default is later wanted, W4 becomes a hard error with no other change.)
- **Degrade.** Both E5 and W4 engage **only in the two-file cross-check mode** — a ledger with findings is supplied. Without it, the referential dimension is skipped and only the self-contained checks run, so single-file Increment-1 usage is byte-for-byte unchanged.

## Workflow (revision-coach)

`/triage-feedback` (or `/coach` routing to Feedback Triage mode) drives the conversation; full protocol in `revision-coach/references/feedback-triage.md`:

1. **Intake & structure.** Capture each external note as a `feedback_item` block with `source` and `claim`; `assessment: pending`, `triage: monitor` until checked.
2. **Validate (route to Core Editor).** For each claim, run or recommend a **targeted** pass to confirm/refute it (the coach never runs passes itself — candidate findings go back to core-editor). Set `assessment` from the result.
3. **Map to findings.** A `validated` claim that names a real defect becomes (or links to) an `apodictic.finding.v1` in the ledger, where its severity is governed normally; record the link structurally as `maps_to: "F-…"` on the feedback item (Increment 2). `feedback-triage` then cross-checks it against the ledger (E5 catches a phantom id; W4 nudges a validated item still missing its link).
4. **Resolve conflicts.** For each `conflicts_with` pair, decide — keep one, decline the other, or park both; never leave both actionable.
5. **Triage & sequence.** Set `triage` per item; produce the prioritized list (and hand off to Session Planning for the act-now set).
6. **Reconcile declines with the engine (`docs/finding-dispositions.md`).** An item triaged `decline` whose `evidence_refs` cite a ledger `F-…` id gets the offer to record an engine finding disposition — `{disposition: declined, source: triage, reason: <item claim + assessment>}` — via the dual-writer path (marker in the triage artifact itself; non-governed sidecar write direct, governed folds at the next `revision_round` clear). Author-decided, never automatic. The FB-item decline alone (external feedback about no engine finding) records nothing — dispositions attach to ledger findings only. W3 nudges the miss.
7. **Gate.** `validate.sh feedback-triage <run_folder>` (or `--strict` in CI) before the plan is finalized. A run folder that also holds the `*_Findings_Ledger_*.md` auto-pairs it, so the `maps_to` cross-check runs alongside the conflict checks.

## Self-review

- *Why a new validator rather than reusing `structured-findings`* — `structured-findings` validates any `apodictic:*` block against its schema, so it would catch E1; but E2/E3/E4 (id uniqueness scoped to the triage; conflict **referential integrity**; self-conflict) and W1/W2 (the contradiction-coherence and act-on-unvalidated gaps) are workflow-specific classes that have no home there. `feedback-triage` is the thin orthogonal layer, exactly like `finding-trace` relative to `structured-findings`.
- *Two-axis design* — keeping `assessment` (truth) and `triage` (disposition) separate, and keeping `triage` off the canonical severity scale, prevents the regression the v2.0.0 normalization fixed: a single field conflating "is the claim true" with "how bad is it" with "what will we do." A feedback item's severity, once validated, lives on the finding it maps to.
- *Undirected conflicts* — W1 treats `conflicts_with` as undirected so a writer only has to record the contradiction once; the pair is flagged from either side. The cost is that a deliberately one-sided "supersedes" relationship can't be expressed — acceptable, because a true contradiction is symmetric by nature.
- *Advisory-by-default posture* — W1/W2 are advisory with `--strict` as the opt-in gate, matching `finding-trace`/`escalation-check`: a coherence signal mid-triage, a hard gate at finalize/CI. Only ERRORs (broken contract / broken references) block by default.
- *Firewall* — the workflow routes validation to Core Editor passes and never re-diagnoses in the coach, consistent with the revision-coach delegation principle.
- *`maps_to` split — hard reference, soft presence (Increment 2)* — the two halves of "a validated item must point at a real `F-…`" are deliberately different severities. A **dangling** reference (E5) is a broken pointer, unambiguously wrong, so it is a hard ERROR like every referential-integrity check in the fleet (`finding-trace` E1, retcon E6). Whether a validated item is **required** to carry `maps_to` is the ambiguous half, so its presence is an **advisory** W4 — the safer reading, keeping the field additive and letting `validated` precede the ledger write (coach step 2 before step 3), with `--strict` as the finalize gate. This also mirrors `finding-trace`'s own split (dangling = E, coverage = W). *Reviewer note:* if project policy later wants validated-without-`maps_to` to hard-block by default, W4 flips to an ERROR with no other code change; the canonical example keeps FB-02 at `partly-validated` precisely so a policy flip there is a one-line assessment edit, not a restructure.

## Out of scope (later increments)

- **Sidecar lifecycle for feedback items.** A `feedback_states` map (like `finding_states`) advancing items `pending → assessed → resolved`, audited across sessions. Deferred until the workflow has run on real returns.
- ~~**Auto-mapping feedback items to findings by ID.**~~ **Built (Increment 2).** The structured `maps_to` field is now cross-checked against the Findings Ledger: a dangling `maps_to` is an ERROR (E5) and a `validated` item carrying no `maps_to` is an advisory W4 (ERROR under `--strict`). See "The `maps_to` cross-check" above. Wiring the Core Editor to *auto-create* a ledger finding from a validated item (rather than the author linking an existing one) remains a Runner-Governed Execution concern.
- **Targeted-pass automation.** Increment 1 *recommends* the validation pass; wiring the Core Editor to run the specific pass for a claim and write the result back is a Runner-Governed Execution concern.
