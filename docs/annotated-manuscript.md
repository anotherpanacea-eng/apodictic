# Annotated-Manuscript Deliverable — the letter's findings, anchored in the margin

**Status:** Proposed (unbuilt). Roadmap: `ROADMAP.md` → [Horizon Capacities](../ROADMAP.md#horizon-capacities) Tier 1, item 2. Proposed implementation surface: a reference module under `core-editor/references/annotated-manuscript.md`, a `scripts/annotation_manifest.py` extractor/validator, `validate.sh annotated-manuscript`, a CriticMarkup renderer, and a worked example under `core-editor/references/`.

Ask a human developmental editor what you get back and the first answer is almost never "a letter." It is **the manuscript itself, marked up** — margin comments anchored where the problem lives — *plus* the letter that contextualizes them. The standard trade deliverable set is editorial letter **+ in-manuscript margin comments + book map + style sheet**. APODICTIC ships the letter and references loci inside it ("Chapter 9 collapses three days…"), but it never hands the writer a copy of their manuscript with the findings sitting next to the prose that triggered them. For a writer revising at the desk, the annotated copy is the working surface; the letter is the briefing.

This deliverable is firewall-bound **and** synergistic with shipped work: findings already carry durable IDs and loci ([Finding Lifecycle IDs](finding-lifecycle-ids.md)), so this is fundamentally an *anchor-and-export* problem, not a reasoning one. The hard part is not "what to say" — the findings already say it — but **where exactly it attaches, and how we prove the prose was never touched.** Both turned out to require more machinery than a first pass assumed; this spec makes that machinery explicit.

## What this is not

- **Not** tracked changes or suggested rewrites. A human DE sometimes "drafts alternative versions of weak sections"; APODICTIC must not. Inserting suggested prose is **content invention** — a Firewall violation and the explicitly-out-of-scope "prose execution mode" (`ROADMAP.md` §Not Planned). This deliverable produces **comments only** (`A2`, `A5`).
- **Not** line/copyediting. Comments anchor to *structural* findings, not sentence mechanics. Copyediting stays out of scope (`ROADMAP.md` §Not Planned).
- **Not** a replacement for the letter. The annotated copy carries the per-locus findings; the editorial letter remains the artifact of record for the synthesis, the decision layer, and the appendices.

## Prerequisite: the manuscript snapshot

The author's manuscript is an *external* file — it is not currently a tracked run artifact and the framework persists no line-numbering for it. Anchoring and the no-mutation proof both require a **frozen, normalized reference**, so this capability adds one explicit step:

On invocation, the manuscript is copied into the run folder as `[Project]_Manuscript_Snapshot_[runlabel].md` with normalization recorded: line endings forced to LF, a trailing newline ensured, no other transformation. The snapshot's line count is recorded in the manifest. **All anchoring, all line numbers, and the no-mutation diff are against this immutable snapshot — never the author's live file.** This makes the line-range ladder well-defined (the snapshot *is* the line index) and gives the no-mutation check a fixed left-hand side. (Timeline line ranges are model-recorded judgments *about* the manuscript; the snapshot is what makes a line number a real index. Where a Timeline range and the snapshot disagree at the boundary, the snapshot wins and the discrepancy is a W1 advisory.)

## The anchoring problem (named honestly)

Findings encode loci as free strings inside `evidence_refs`, and the real corpus is heterogeneous: `["Chapter 9"]`, `["Ch. 12"]`, `["Ch.3 p.40"]`, mixed refs like `["Pass 4 §Scene Turns", "Ch. 12"]`, and **refs that point at a pass artifact, not the manuscript at all** (`["Pass 1 §Orientation"]`). The anchor resolver therefore normalizes and degrades, finest reliable rung first:

1. **`line-range`** — when `Timeline.md` Section 1 maps the finding's scene to a line range *and* that range lies within the snapshot's line count.
2. **`section`** — when the ref names a section heading that exists verbatim in the snapshot.
3. **`chapter`** — when the ref yields a chapter token under a **normalization rule** (`Chapter N` / `Ch. N` / `Ch.N` / `Ch N` → canonical `chapter N`) that matches a chapter heading in the snapshot.
4. **`document`** — the ref is **not manuscript-locatable** (e.g., `Pass 1 §Orientation`, or a chapter token with no matching heading). The finding is still surfaced, as a document-level general note at the head of the annotated copy, honestly *not* positioned in the margin.

The resolver **never fabricates precision**: a chapter-level finding gets a chapter anchor; a non-locatable finding gets a `document` anchor; nothing is guessed to a sentence. Character-precise anchoring (a validated `evidence → sentence` quote match) is a future increment with its **own** integrity surface (see §Increment plan and the A3 scope note).

## The artifact

Three files, so the manuscript is never mutated in place:

1. **The snapshot** — `[Project]_Manuscript_Snapshot_[runlabel].md` (above), the immutable reference.
2. **The annotation manifest** (`apodictic.annotation.v1`, real-JSON blocks) — one entry per surfaced finding: `finding_id`, resolved `anchor` (`{kind, value}` per the ladder), and a `comment` that is a **verbatim projection of the finding's fields** (see Firewall). The manifest is the contract the validator checks.
3. **The annotated copy** — a render that injects CriticMarkup comments (`{>> … <<}`) into a copy of the snapshot. CriticMarkup because it is plain text, diff-friendly, and uses a *bounded, documented* marker syntax whose removal is reversible (see `A2`).

The manifest→render split is the posture of [Manuscript-Structure Visualizations](manuscript-visualizations.md): the structured artifact is the source of truth, the human-facing surface is a pure function of it (Harness Contracts v2 direction).

## Firewall compliance

- **Comment text is a fixed template over verbatim finding fields.** A comment is exactly:
  `[<severity> · <finding_id>] <mechanism> — fix class: <fix_class>. (See letter §<finding_id>.)`
  where `<severity>`, `<finding_id>`, `<mechanism>`, `<fix_class>` are the finding's **verbatim** field values and the rest is fixed boilerplate. There is **no free-text slot**, so the renderer cannot author, abbreviate, paraphrase, or smuggle content. (This resolves the earlier tension between "scannable margin" and "provenance-checkable": scannability comes from the leading `[severity · id]` and the letter link, not from paraphrase. Full context lives in the letter, reached by ID.)
- **No prose mutation.** The annotated copy, run through the **specified reverse transform** (remove every `{>> … <<}` span), must equal the snapshot exactly (`A2`).
- **No anchor invention.** Every anchor resolves against the snapshot, or is an honest `document` note (`A3`).

These make the deliverable firewall-disciplined for **Increment 1's comment-only render**. They do **not** by themselves cover the future quote-locator increment, whose content-matching introduces a new failure mode (a fabricated quote match); that increment ships its own gate (§Increment plan). The spec claims discipline for what it builds, not for what it defers.

## Severity honesty

- **Every locked Must-Fix is surfaced.** Each body Must-Fix in the Ledger must appear as an annotation — line-anchored if locatable, a `document` note if not (`A4`). The margin analogue of `softness-check`'s locked→delivered rule: a Must-Fix cannot quietly fail to reach the marked-up copy.
- **Severity travels verbatim.** The comment template leads with the canonical `<severity>` token, copied from the finding; the renderer cannot drop or soften it (it has no slot to do so).

## The `annotated-manuscript` validator

`validate.sh annotated-manuscript <run_folder>` resolves the newest snapshot, manifest, annotated copy, and Findings Ledger. Delegates to `scripts/annotation_manifest.py`; degrades to advisory `WARN` without `python3`. Report lines are namespaced `annotated-manuscript:<ID>` so cross-validator `--check-all` output stays unambiguous.

| ID | Severity | Rule |
|---|---|---|
| **A1 — manifest schema** | ERROR | Each `apodictic.annotation.v1` block parses and is well-formed. (The shared schema engine validates the **subset** it supports — `required`/`const`/`enum`/`type`/`minItems`/`pattern`; the *nested* `anchor.kind ∈ {line-range, section, chapter, document}` enum is **not** schema-engine-checkable and is enforced in `annotation_manifest.py`, like every other nested-field check.) |
| **A2 — no prose mutation (signature gate)** | ERROR | Applying the specified reverse transform — delete every `{>> … <<}` span — to the annotated copy yields a byte string **identical to the snapshot**. **Hard precondition:** if the *snapshot* already contains a CriticMarkup sigil (`{>>`, `<<}`), the transform is not reversible and the validator fails loudly, directing to an escaping pass rather than guessing. This is the firewall made checkable for the comment-only render. |
| **A3 — anchor integrity** | ERROR | Every `anchor` resolves against the snapshot: a `line-range` within the snapshot line count; a `section`/`chapter` heading that exists (chapter under the normalization rule); or the literal `document` kind. A non-locatable ref must be `document` — it is **not** an A3 error (it is honest degradation), but a `line-range`/`section`/`chapter` that does **not** resolve **is**. *Scope note: A3 validates anchor existence only; it has no concept of evidence-to-prose matching and does not cover the future character-precise increment's failure mode.* |
| **A4 — Must-Fix completeness** | ERROR | Every body Must-Fix `apodictic.finding.v1` in the Ledger has a corresponding annotation (any anchor kind, incl. `document`). Implemented by **reusing `finding_trace.py`'s ledger-inventory primitive** (the synthesis-bound Must-Fix set, by ID) rather than a fresh matcher — the dimension this validator adds is ledger→manifest by ID. |
| **A5 — comment is a verbatim field projection** | ERROR | Each `comment` equals the fixed template applied to its finding's verbatim `severity`/`id`/`mechanism`/`fix_class`. Field-equality, not substring — so it neither false-fails on legitimate abbreviation (there is none) nor passes invented prose that merely contains the finding's tokens. The mechanical proof that the renderer projected, it did not author. |
| **W1 — coverage & boundary drift** | WARN (ERROR under `--strict`) | A Should/Could finding with a locatable ref is left un-anchored, **or** a Timeline line-range disagrees with the snapshot at a boundary. Advisory: a Must-Fix-only annotated pass is legitimate, and a one-line boundary drift is usually benign. Override `<!-- override: annotation-coverage <F-…> — <rationale> -->`. |

**Report & exit.** One line per annotation — `finding_id · anchor.kind · anchor.value` — plus the check summary. Exit `0` clean / WARN-only, `1` on any ERROR (or WARN under `--strict`), `2` usage. Override markers (`<!-- override: … -->`) are honored for W1, matching `editor-scaffolding` / `feedback-triage`.

**Ownership boundary.** `annotated-manuscript` owns the **manuscript-copy annotation contract**: the no-mutation transform, anchor existence/degradation, verbatim comment projection, and Must-Fix presence *in the marked-up copy*. It traces **ledger→manifest by ID** (the un-owned dimension), reusing `finding-trace`'s ledger-inventory primitive rather than reimplementing it; it does **not** re-check letter↔ledger integrity (`finding-trace`), severity fidelity in the letter (`softness-check`), or Timeline arithmetic (`timeline-*`). It *consumes* Timeline ranges for anchoring; it does not validate them.

## Canonical `--check-all` gate

Two worked fixtures, so the gate exercises more than the coarsest rung:

1. The shipped `example-findings-ledger.md` (`F-RR-01`, a `Chapter 9` Must-Fix) → exercises the **`chapter`** rung + `A4`.
2. A dedicated fixture: a tiny snapshot manuscript **with chapter headings and a paired `example-timeline.md`-style line range**, plus a finding whose scene resolves to that range → exercises the **`line-range`** rung, `A2` (reverse-transform identity), and `A5` (verbatim projection).

`validate.sh --check-all` runs `annotated-manuscript` against both, proving no-mutation, line-range *and* chapter anchoring, and Must-Fix completeness on canonical artifacts (the "canonical-framework validator runs as release gate" discipline, `ROADMAP.md` §Deferred). Without the second fixture the line-range/A2 mechanics would ship unexercised by the gate — the failure the §Deferred discipline exists to prevent.

## Increment plan

**Increment 1 (this spec):** the snapshot step, `apodictic.annotation.v1` schema (added to `schemas/`, registered in `apodictic_artifacts.known_schema_ids()`), `scripts/annotation_manifest.py` (anchor resolver + reverse-transform diff + validator), `validate.sh annotated-manuscript`, the CriticMarkup renderer (fixed comment template), both worked fixtures, and the `--check-all` gate. Anchor granularity = line-range / section / chapter / document; no character-precise anchoring.

**Future increments (not built):**
- **DOCX / Google Docs / Obsidian comment export** — render targets over the same manifest; each must preserve `A2` semantics in its native comment model (and define its own reverse transform).
- **Character-precise anchoring** — a quote-locator narrowing an anchor to the exact sentence by matching the finding's evidence against the snapshot, *only when the match is unambiguous*. **Ships its own integrity gate** (A-something: the matched quote must occur verbatim and uniquely in the snapshot) because A3 does not cover content matching.
- **Letter ↔ margin cross-links** — bidirectional `F-…` links between letter and annotated copy.
- **Round-trip re-anchoring** — when the writer revises, detect which anchors moved or resolved (pairs with [Draft-over-Draft Structural Regression Testing](../ROADMAP.md#horizon-capacities), Horizon item 6). Increment 1 treats the annotated copy as a *snapshot* of one run, exactly like the letter.

## Self-review (Increment 1)

- *Why a snapshot, not the live file* — anchoring and the no-mutation proof need a frozen, line-stable left-hand side the framework does not otherwise persist. Snapshotting is the smallest honest fix; it also makes the deliverable reproducible.
- *Why verbatim projection instead of a heuristic provenance check* — a substring/token check is simultaneously gameable (invented prose that contains the finding's tokens) and false-failing (legitimate abbreviation). A fixed template with no free-text slot removes both failure modes and makes `A5` an equality, not a guess.
- *Why `document` is not an A3 error* — many real `evidence_refs` point at pass artifacts, not manuscript loci. Forcing them to a fabricated line would violate "never guess precision"; surfacing them as honest document notes keeps `A4` (Must-Fix completeness) satisfiable without inventing anchors.
- *Why `A2` fails loudly on sigil collision* — silently mishandling a manuscript that already uses `{>>`/`<<}` would break the one guarantee the whole deliverable rests on. Better a loud failure with an escaping path than a wrong "no mutation" pass.
