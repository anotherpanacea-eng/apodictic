# Annotated-Manuscript Round-Trip Re-Anchoring — carry the margin notes across a revision

**Status:** Proposed (unbuilt). Spec for review. Depends on the [Annotated-Manuscript deliverable](annotated-manuscript.md) (Increments 1–3, in `main`), its [producer](annotated-manuscript-producer.md) (PR #104/#105), and [Draft-over-Draft Structural Regression](draft-regression-testing.md) (`regression-diff`, PR #106) — the finding-level cross-round diff this complements at the **anchor/text** level.

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
| `held` | the anchored span resolves to the **same** locus in N+1 (quote verbatim+unique at the same offset; chapter/section heading present and unique) | re-anchor unchanged |
| `moved` | the anchored span resolves **verbatim + unique** but at a **new** offset (quote) / the heading is present but shifted | re-anchor to the new offset; note the shift |
| `vanished` | the anchored span **no longer occurs** in N+1 (quote absent; heading gone) | candidate **resolved** — surfaced, not asserted (the writer may have rephrased, not fixed) |
| `ambiguous` | the span now occurs **more than once** (quote duplicated; heading duplicated), so re-anchoring can't pick a locus | degrade — re-anchor refused, flagged for editor |

**Per-rung honesty (don't oversell):** the `quote` rung re-anchors **mechanically and reliably** (verbatim+unique text search — the same A6 identity that built it). The `chapter`/`section` rungs re-anchor by **heading text match** (robust unless chapters renumber/retitle). The `line-range` rung **cannot** re-anchor across an edited draft (bare line numbers carry no text to find) — it degrades to `ambiguous`/`vanished` and is reported as *not mechanically re-anchorable*, never silently re-pointed at whatever now sits at those line numbers (that would be fabricated precision). `document` anchors are always `held` (no locus). So re-anchoring is **most powerful exactly where Producer Increment 2 lit the `quote` rung** — the two compound.

## The firewall

Re-anchoring is **pure text search over the new snapshot** — it invents nothing. A re-anchored `quote` must occur **verbatim and exactly once** in N+1 (the A6 identity, reused), or it is `vanished`/`ambiguous`; the margin comment text itself is **carried over verbatim** from the gated draft-N manifest (the finding-field projection — never re-authored). The system never "updates" a comment to fit the new prose; it only relocates an unchanged comment to where its unchanged anchor text now lives, or reports that it can't.

## The artifacts + the generator

- **`scripts/reanchor.py reanchor <prior_run_folder> <new_snapshot>`** (mirrored): reads draft N's gated manifest (anchors + comments) and draft N+1's snapshot, re-resolves each anchor, and emits **(a)** a **re-anchored manifest** bound to the new snapshot (`snapshot_path`/`sha256`/`line_count` of N+1) containing only the `held`/`moved` annotations (each re-pointed, comment verbatim) — which the existing `annotation_manifest render` then turns into a **fresh annotated copy of draft N+1**, gated by the existing A1–A6 — and **(b)** a re-anchoring report classifying every draft-N annotation (held/moved/vanished/ambiguous) with its evidence. The vanished/ambiguous notes are **not** dropped silently; they go to the report as candidate-resolved / needs-editor.
- The re-anchored manifest **reuses the existing manifest schema + A1–A6 gate** — a re-anchored copy is just an annotated copy of a different snapshot, so it inherits the whole firewall (A2 no-mutation, A6 quote integrity) for free. No new manifest format.

## The `reanchor` validator (proposed)

`validate.sh reanchor <prior_run_folder> <new_snapshot>` → delegates to `scripts/reanchor.py`; degrades to advisory `WARN` without `python3`. Gate IDs (by identity, the A/X discipline):

| ID | Severity | Rule |
|---|---|---|
| **RA1 — re-anchor integrity** | ERROR | Every `held`/`moved` annotation's anchor **actually resolves** in N+1's snapshot (quote verbatim+unique at the recorded new offset; heading unique) — i.e. the emitted re-anchored manifest passes A1–A6 against N+1. No re-anchor points at a locus that isn't really there. |
| **RA2 — comment fidelity** | ERROR | Each carried-over comment is **byte-identical** to its draft-N manifest comment (the firewall: relocate, never re-author). |
| **RA3 — partition completeness** | ERROR | Every draft-N annotation appears in **exactly one** class (held/moved/vanished/ambiguous); none silently dropped, none double-counted (the A4/X3 multiset discipline). |
| **W1 — candidate-resolved** | WARN (ERROR `--strict`) | One or more `vanished` annotations — anchored prose gone, a candidate the finding was addressed (cross-reference `regression-diff`'s `resolved-and-held`). |
| **W2 — re-anchor refused** | WARN (ERROR `--strict`) | One or more `ambiguous` / not-mechanically-re-anchorable (`line-range`) annotations needing editor placement. |

Only RA1–RA3 (the mechanical re-anchor contract) are hard; W1/W2 are advisory (a vanished anchor is a *candidate*, not proof of resolution — the writer may have reworded).

## Open questions for spec-review

- **Q1 — `moved` vs `held` for chapter/section.** A heading present in both drafts is "held" by text but its *line position* shifts; does `moved` even apply to non-quote rungs, or only to `quote` (the only rung with a precise offset)? Likely: chapter/section are binary present/absent (held/vanished/ambiguous), and `moved` is `quote`-only. Confirm and simplify the table if so.
- **Q2 — interplay artifact.** Should re-anchoring *emit* the cross-reference to `regression-diff` (e.g. "F-…'s anchor vanished AND regression-diff classed it resolved-and-held → high-confidence resolved"), or stay strictly anchor-level and leave the correlation to the orchestrator? Leaning: stay anchor-level; the orchestrator correlates. Confirm the boundary.
- **Q3 — input shape.** Re-anchor against a **new snapshot file** (the writer's revised draft, freshly snapshotted) vs. against a full **new run folder** (which would have its own fresh manifest). The former is lighter and is the true "carry the old notes onto the new draft" operation; the latter overlaps `regression-diff`. Confirm `<prior_run_folder> <new_snapshot>` is the right signature.
- **Q4 — fixture.** A paired fixture: draft-N snapshot + manifest (with a quote anchor, a chapter anchor, a line-range anchor) and a draft-N+1 snapshot where one quote is **held**, one **moved** (text shifted down), one **vanished** (sentence cut), and a heading **held** — proving each class mechanically. Constructible from the existing `example-annotated-manuscript/` snapshot + a hand-edited revision. Confirm scope.

## Increment boundary

**In (Increment 1):** `scripts/reanchor.py` + `validate.sh reanchor` (RA1–RA3 + W1/W2), reusing the manifest schema + A1–A6 and the regression-diff/diff-validator precedents; the re-anchored manifest → `render` → gated draft-N+1 annotated copy; the re-anchoring report; a paired fixture + `--check-all` gate; validators +1. **Out:** automatic correlation with `regression-diff` (orchestrator's job, Q2); fuzzy/semantic re-anchoring of vanished spans (the firewall forbids guessing where rephrased prose went); re-anchoring `line-range` across edits (degrades by design); any comment re-authoring.
