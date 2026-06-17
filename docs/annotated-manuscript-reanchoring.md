# Annotated-Manuscript Round-Trip Re-Anchoring — carry the margin notes across a revision

**Status:** **Built (Increment 1, 2026-06-17).** Shipped surface: `scripts/reanchor.py` (the re-resolver + classifier, `--self-test`), the `validate.sh reanchor <prior_run_folder> <new_snapshot>` validator (RA1–RA3 + W1/W2; +1 → 45 validators, mirrored), a `ledger_optional` mode added to `annotation_manifest.check` (so the re-anchored manifest is gated by A1–A3 + A4-multiset + A6 without a re-diagnosed N+1 ledger), and a revised-draft fixture (`example-reanchor-revised.md`) wired into `--check-all`. Depends on the [Annotated-Manuscript deliverable](annotated-manuscript.md) (Increments 1–3, in `main`), its [producer](annotated-manuscript-producer.md) (PR #104/#105), and [Draft-over-Draft Structural Regression](draft-regression-testing.md) (`regression-diff`, PR #106) — the finding-level cross-round diff this complements at the **anchor/text** level.
<!-- built-when: scripts/reanchor.py -->

## The gap

The annotated copy is a **one-run snapshot** (`docs/annotated-manuscript.md` §Prerequisite): every annotation anchors to *draft N's* frozen snapshot (a `quote` char-offset, a `chapter`/`section` heading, a `line-range`, or the `document` head). Increment 1 deliberately treats it that way — like the editorial letter, it's a record of one diagnosis. So when the writer **revises** (draft N+1), the marked-up copy is stale: nothing tells the writer which margin notes still apply to the new draft, which have moved, and which point at prose that no longer exists (the likely *wins*). Re-running the whole diagnosis re-annotates from scratch but **loses the through-line** — it can't say "this note is the same problem you saw last round, still here" vs. "this is gone."

Round-trip re-anchoring closes that: given **draft N's gated manifest** + **draft N+1's snapshot**, re-resolve each annotation against the new snapshot and classify what happened — so the annotated copy becomes **revision-aware** and feeds text-level evidence into the regression diff.

## What it is — and how it complements `regression-diff`

Two cross-round diffs at two altitudes, deliberately distinct:

- **`regression-diff` (PR #106) — finding level.** Heuristically matches *findings* across rounds by origin + chapter + mechanism tokens (no stable IDs). Answers "did a resolved finding recur? did a quiet chapter break?"
- **Re-anchoring (this) — anchor/text level.** Asks, for each *annotation's anchored span*, "does that exact text still exist in the new draft, and where?" It's **mechanical text matching**, not heuristic mechanism matching — and it is *strong, independent evidence* for the regression diff: an annotation whose anchored quote **vanished** is hard evidence the finding was addressed (corroborating `resolved-and-held`); one whose quote **persists verbatim** is hard evidence it was *not* (corroborating `recurrence-candidate`). Re-anchoring sharpens the heuristic signal with ground truth from the bytes.

## Classification (per annotation, against draft N+1's snapshot)

Re-resolution is **by the anchor's own evidence**, finest-first, mirroring the build ladder:

| Class | When | Result |
|---|---|---|
| `held` | the anchored span resolves to the **same** locus in N+1 (quote verbatim + unique at the **same** offset; chapter/section heading present and unique) | re-anchor unchanged |
| `moved` | **(`quote` only)** the quote resolves **verbatim + unique** but at a **new** offset | re-anchor to the recomputed offset; note the shift |
| `vanished` | the anchored span **no longer occurs** in N+1 (quote absent; heading gone) | candidate **resolved** — surfaced, not asserted (the writer may have rephrased, not fixed) |
| `ambiguous` | the span now occurs **more than once** in N+1 (quote duplicated; heading duplicated), so re-anchoring can't pick a locus | degrade — re-anchor refused, flagged for editor |
| `not-re-anchorable` | **(`line-range` only)** a bare line range carries no text to search for in an edited draft | refused by design — reported, never re-pointed at whatever now sits at those line numbers |

The five classes are an **exhaustive, mutually-exclusive partition** of draft-N's annotations (RA3 enforces it). Resolved by **Q1**: `moved` is **`quote`-only** — chapter/section anchors carry no offset (their `value` is the heading text; line position is re-derived at render time), so they are **binary** present/absent (`held` / `vanished` / `ambiguous`), never `moved`. `document` anchors are always `held` (no locus).

**Per-rung honesty (don't oversell):** the `quote` rung re-anchors **mechanically and reliably** — verbatim+unique text search, the same A6 identity that built it (the new offset is **recomputed** against N+1, see §The mechanism; never carried forward). The `chapter`/`section` rungs re-anchor by **heading text match** (robust unless chapters renumber/retitle). The `line-range` rung is **`not-re-anchorable`** across an edited draft (bare line numbers carry no text to find) — reported as such, never silently re-pointed (that would be fabricated precision). So re-anchoring is **most powerful exactly where Producer Increment 2 lit the `quote` rung** — the two compound.

## The mechanism (the load-bearing build rule — P1-A)

Re-anchoring a `quote` is **re-running the build-time locator** (`annotation_manifest.quote_anchor`) against N+1's snapshot: `count = snapshot_{N+1}.count(quote)`; if `count == 1`, `start = snapshot_{N+1}.find(quote)` and the new anchor is `start-(start+len)`. The offset is **always recomputed** — **never carried forward** from N's manifest. `held` vs `moved` is then simply whether that recomputed offset equals N's. This is not optional: if a builder copied N's stale offset into the N+1 manifest, **A6 fails on every moved quote** (its offset check `snapshot[start:end] == quote and start == snapshot.find(quote)` would not hold). Because re-anchoring *is* re-running `build` on the surviving subset of findings against a new snapshot, A6 passes by construction for `held`/`moved`. (Chapter/section headings have no offset — `held`/`vanished`/`ambiguous` is decided by heading presence/uniqueness alone.)

## The firewall

Re-anchoring is **pure text search over the new snapshot** — it invents nothing. A re-anchored `quote` must occur **verbatim and exactly once** in N+1 (the A6 identity, reused), or it is `vanished`/`ambiguous`; the margin comment text itself is **carried over verbatim** from the gated draft-N manifest (the finding-field projection — never re-authored). The system never "updates" a comment to fit the new prose; it only relocates an unchanged comment to where its unchanged anchor text now lives, or reports that it can't. **Note (P2-B):** A6's faithful-projection arm (`anchor.quote == finding.evidence_quote`) is **inert here** — there is no N+1 ledger to project from — so **RA2 (comment + quote carried byte-identical from the gated N manifest) is its replacement guard**: fidelity is proven against N, not re-projected from a non-existent N+1 finding.

## The artifacts + the generator

- **`scripts/reanchor.py reanchor <prior_run_folder> <new_snapshot>`** (mirrored): reads draft N's gated manifest (anchors + comments) — resolved via the manifest's own snapshot binding, as `annotation_manifest.run` already does — and draft N+1's **normalized** snapshot (LF + trailing newline, sha/line-count bound into the emitted manifest), re-resolves each anchor (§The mechanism), and emits **(a)** a **re-anchored manifest** bound to N+1 containing only the `held`/`moved` annotations (each re-pointed, comment verbatim) — which the existing `annotation_manifest render` turns into a **fresh annotated copy of draft N+1** — and **(b)** a re-anchoring report classifying **every** draft-N annotation (held / moved / vanished / ambiguous / not-re-anchorable) with its evidence. The vanished / ambiguous / not-re-anchorable notes are **not** dropped silently; they go to the report as candidate-resolved / needs-editor.
- **What "inherits the gate for free" precisely means (P1-B).** A re-anchored copy is structurally just an annotated copy of a different snapshot, so it inherits **A1 (schema), A2 (no-mutation), A3 (anchor resolution), A5 (projection), A6 (quote integrity), and A4's rendered-span *multiset* arm** for free (the surviving annotations are consistent in both the N+1 manifest and the N+1 rendered copy). It does **not** inherit **A4's cross-ledger Must-Fix-completeness arm** — that reads a Findings Ledger, and an un-re-diagnosed N+1 draft has **none**; a `vanished` Must-Fix would *false-fail* it. That obligation is **deliberately not carried**: the vanished Must-Fixes go to the re-anchoring report (RA3 guarantees none is silently lost), not to a phantom N+1 ledger. So the N+1 manifest is gated by A1–A3 + A5 + A6 + A4-multiset, with A4-ledger-completeness **out of scope by construction**. No new manifest format.

## The `reanchor` validator (proposed)

`validate.sh reanchor <prior_run_folder> <new_snapshot>` → delegates to `scripts/reanchor.py`; degrades to advisory `WARN` without `python3`. Gate IDs (by identity, the A/X discipline):

| ID | Severity | Rule |
|---|---|---|
| **RA1 — re-anchor integrity** | ERROR | Every `held`/`moved` annotation's anchor **actually resolves** in N+1's snapshot (quote verbatim+unique at the recorded new offset; heading unique) — i.e. the emitted re-anchored manifest passes A1–A6 against N+1. No re-anchor points at a locus that isn't really there. |
| **RA2 — comment fidelity** | ERROR | Each comment in the **emitted manifest** (serialized + re-parsed — the form that gets rendered/gated) is **byte-identical** to its draft-N manifest comment (the firewall: relocate, never re-author). The re-parse breaks in-memory aliasing, so a serialization/escaping corruption or any future non-verbatim carrying is caught here, independently of A4-multiset; it stands in for A6(a)'s projection arm, which is inert without an N+1 ledger. |
| **RA3 — partition completeness** | ERROR | Every draft-N annotation appears in **exactly one** of the five classes (held / moved / vanished / ambiguous / not-re-anchorable); none silently dropped, none double-counted (the A4/X3 multiset discipline). This is what guarantees a `vanished` Must-Fix is surfaced in the report rather than lost (since the N+1 manifest legitimately omits it — see §The artifacts). |
| **W1 — candidate-resolved** | WARN (ERROR `--strict`) | One or more `vanished` annotations — anchored prose gone, a candidate the finding was addressed (the orchestrator may cross-reference `regression-diff`'s `resolved-and-held`; this validator does not assert the join — Q2). |
| **W2 — re-anchor refused** | WARN (ERROR `--strict`) | One or more `ambiguous` or `not-re-anchorable` (`line-range`) annotations needing editor placement. |

Only RA1–RA3 (the mechanical re-anchor contract) are hard; W1/W2 are advisory (a vanished anchor is a *candidate*, not proof of resolution — the writer may have reworded). The WARN / `--strict`-ERROR posture matches `regression-diff`'s W1–W3 deliberately.

## Open questions — resolved by spec-review (2026-06-17)

- **Q1 — `moved` for chapter/section: NO, `moved` is `quote`-only.** Headings carry no offset (line position is re-derived at render); they are binary `held`/`vanished`/`ambiguous`. The classification table now reflects this.
- **Q2 — interplay artifact: stay strictly anchor-level.** `reanchor` and `regression-diff` share no join key (`reanchor` keys on `anchor.quote`/heading text; `regression-diff` on `origin + chapter + mechanism`), so any correlation is itself heuristic and belongs with the orchestrator (or a future Regression Report). `reanchor` emits per-annotation classes + evidence; the orchestrator joins by `finding_id`. W1's wording reflects this.
- **Q3 — input shape: `<prior_run_folder> <new_snapshot>` is correct.** It is the true "carry N's notes onto the new draft *before* a re-diagnosis exists" operation; a new-run-folder input would presuppose re-diagnosis (the `regression-diff` scenario) and overlap it. Mirrors the `state-card-diff <prior> <current>` two-arg dispatch.
- **Q4 — fixture: fully constructible from the existing snapshot.** The committed snapshot already has the lighthouse sentence at offset `250-315` (held), an insert-before shifts it (moved), a cut removes it (vanished), `"used to the dark"` is **already count-2** (ambiguous), `# Chapter 9`/`# Chapter 1` are unique headings (held), and N's manifest has `F-LR-01` at `3-4` (the `not-re-anchorable` line-range case). N+1 is a hand-edited revision; both manifests are gate-valid.

## Increment boundary

**In (Increment 1):** `scripts/reanchor.py` (mirrored; with a `--self-test` so it joins `--self-test-all`) + `validate.sh reanchor` (RA1–RA3 + W1/W2), reusing the manifest schema + A1–A6 and the regression-diff / diff-validator precedents; the re-anchored manifest → `render` → gated draft-N+1 annotated copy; the re-anchoring report; a paired fixture + `--check-all` gate. **Validators +1 → 45**: a lockstep bump in **both** `scripts/validate.sh` and `plugins/apodictic/scripts/validate.sh` (check-mirror byte-identity) of `AGG_VALIDATORS`, the `Commands:` usage list, and the `--check-all` description string, plus the new dispatch arm; `reanchor.py` joins the `check-mirror` set. **Out:** automatic correlation with `regression-diff` (orchestrator's job, Q2); fuzzy/semantic re-anchoring of vanished spans (the firewall forbids guessing where rephrased prose went); re-anchoring `line-range` across edits (`not-re-anchorable` by design); any comment re-authoring.
