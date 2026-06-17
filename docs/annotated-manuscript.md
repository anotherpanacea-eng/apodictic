# Annotated-Manuscript Deliverable — the letter's findings, anchored in the margin

**Status:** Increment 1 **Built** (2026-06-16; promoted the same day from Horizon Capacities Tier 1, item 2). Roadmap: `ROADMAP.md` → [§Annotated-Manuscript Deliverable](../ROADMAP.md#annotated-manuscript-deliverable). Shipped surface: `scripts/annotation_manifest.py` (anchor resolver + CriticMarkup renderer + validator, with `build`/`render`/`annotated-manuscript` modes), `schemas/apodictic.annotation.v1.schema.json`, the `validate.sh annotated-manuscript` arm (+ `--check-all` gate), the shared `apodictic_artifacts.chapter_token` parser, the reference module `core-editor/references/annotated-manuscript.md`, and the canonical fixture `core-editor/references/example-annotated-manuscript/`. `--self-test-all` 41 → 42; `--check-all` green.
<!-- built-when: scripts/annotation_manifest.py -->

Ask a human developmental editor what you get back and the first answer is almost never "a letter." It is **the manuscript itself, marked up** — margin comments anchored where the problem lives — *plus* the letter that contextualizes them. The standard trade deliverable set is editorial letter **+ in-manuscript margin comments + book map + style sheet**. APODICTIC ships the letter and references loci inside it ("Chapter 9 collapses three days…"), but it never hands the writer a copy of their manuscript with the findings sitting next to the prose that triggered them. For a writer revising at the desk, the annotated copy is the working surface; the letter is the briefing.

This deliverable is firewall-bound **and** synergistic with shipped work: findings already carry durable IDs and loci ([Finding Lifecycle IDs](finding-lifecycle-ids.md)), so this is fundamentally an *anchor-and-export* problem, not a reasoning one. The hard part is not "what to say" — the findings already say it — but **where exactly it attaches, and how we prove the prose was never touched.** Both turned out to require more machinery than a first pass assumed; this spec makes that machinery explicit.

## What this is not

- **Not** tracked changes or suggested rewrites. A human DE sometimes "drafts alternative versions of weak sections"; APODICTIC must not. Inserting suggested prose is **content invention** — a Firewall violation and the explicitly-out-of-scope "prose execution mode" (`ROADMAP.md` §Not Planned). This deliverable produces **comments only** (`A2`, `A5`).
- **Not** line/copyediting. Comments anchor to *structural* findings, not sentence mechanics. Copyediting stays out of scope (`ROADMAP.md` §Not Planned).
- **Not** a replacement for the letter. The annotated copy carries the per-locus findings; the editorial letter remains the artifact of record for the synthesis, the decision layer, and the appendices.

## Prerequisite: the manuscript snapshot

The author's manuscript is an *external* file — it is not currently a tracked run artifact and the framework persists no line-numbering for it. Anchoring and the no-mutation proof both require a **frozen, normalized reference**, so this capability adds one explicit step:

On invocation, the manuscript is copied into the run folder as `[Project]_Manuscript_Snapshot_[runlabel].md` with normalization recorded: line endings forced to LF, a trailing newline ensured, no other transformation. The snapshot's line count is recorded in the manifest. **All anchoring, all line numbers, and the no-mutation diff are against this immutable snapshot — never the author's live file.** This makes the line-range ladder well-defined (the snapshot *is* the line index) and gives the no-mutation check a fixed left-hand side. (Timeline line ranges are model-recorded judgments *about* the manuscript; the snapshot is what makes a line number a real index. Where a Timeline range and the snapshot disagree at the boundary, the snapshot wins and the discrepancy is a W1 advisory.)

**Ownership and binding (the snapshot is identified, not "newest").** Writing the snapshot belongs to the APODICTIC run harness (the renderer command may create it on first invocation, but the validator never does — a validator that writes its own left-hand side cannot prove no-mutation). The manifest **binds the snapshot it was rendered against** by `snapshot_path` + `snapshot_sha256` + `snapshot_line_count`, and `validate.sh annotated-manuscript` resolves the snapshot **from that binding**, not by a `*_Snapshot_*` "newest" glob — so a run folder holding an `r1` manifest/annotated-copy beside an `r2` snapshot can never be checked against the wrong pair (the binding hash won't match `r2`, which is a loud A2 failure, not a silent mis-compare). A rerun on a revised manuscript takes a **new runlabel**; a manifest whose `snapshot_sha256` no longer matches any snapshot in the folder is stale and fails rather than degrading.

## The anchoring problem (named honestly)

Findings encode loci as free strings inside `evidence_refs`, and the real corpus is heterogeneous: `["Chapter 9"]`, `["Ch. 12"]`, `["Ch.3 p.40"]`, mixed refs like `["Pass 4 §Scene Turns", "Ch. 12"]`, and **refs that point at a pass artifact, not the manuscript at all** (`["Pass 1 §Orientation"]`). A finding's `evidence_refs` is an **array**, and the framework attaches **no** scene-id field to a finding — so the resolver works **per token**, classifies each token as manuscript-scoped or artifact-scoped, and takes the **finest rung any *manuscript-scoped* token supports**. A `Pass N §…` / bare `§…` audit-or-pass token is **artifact-scoped** and is *never* consumed by the line-range / section / chapter rungs; it contributes only `document` if no manuscript-scoped token resolves. (So `["Pass 4 §Scene Turns", "Ch. 12"]` resolves to **chapter `Ch 12`** — the pass token cannot win a finer `section` anchor; `["Pass 1 §Orientation"]` resolves to **`document`**.) Finest reliable rung first:

1. **`line-range`** — only when an `evidence_refs` token **exactly equals** a `Timeline.md` Section-1 scene-id whose row carries a line range that lies within the snapshot's line count. Because findings carry no scene-id, exact token↔scene-id equality is the **only** permitted line-range key — a finding that merely shares a chapter with a scene (`["Ch. 12"]` vs. scene `Ch 12 §1`) does **not** get a line-range anchor; it falls through to `chapter`. (A negative fixture proves this no-fabrication path.)
2. **`section`** — when a **manuscript-scoped** token names a section heading that exists in the snapshot (heading semantics per `A3`). Artifact-scoped `Pass N §…` / `§…` tokens are excluded here — this is the rung most prone to fabricating precision from a pass-artifact ref.
3. **`chapter`** — when a token yields a chapter token under the **normalization rule** (`Chapter N` / `Ch. N` / `Ch.N` / `Ch N` → canonical `chapter N`) that matches a chapter heading in the snapshot. This rule is **broader** than `viz_manifest.py`'s current `_CHAPTER_RE` (`\b(?:Chapter|Ch)\s*(\d+)\b`, which matches `Chapter 9` / `Ch 12` but **not** `Ch. 12` or `Ch.3 p.40`). The two must not diverge: extract a shared `chapter_token(ref)` helper, broaden it to all four forms, and have **both** `viz_manifest.py` and `annotation_manifest.py` import it (see §Increment plan — this is a behavior change to the shipped viz parser with its own fixture ripple, not a private copy). A page suffix (`p.40`) is **ignored**, never promoted to precision.
4. **`document`** — no manuscript-scoped token resolved (e.g., `Pass 1 §Orientation`, or a chapter token with no matching heading). The finding is still surfaced, as a document-level general note at the head of the annotated copy, honestly *not* positioned in the margin.

The resolver **never fabricates precision**: a chapter-level finding gets a chapter anchor; a non-locatable finding gets a `document` anchor; nothing is guessed to a sentence. Character-precise anchoring (a validated `evidence → sentence` quote match) is a future increment with its **own** integrity surface (see §Increment plan and the A3 scope note).

## The artifact

Three files, so the manuscript is never mutated in place:

1. **The snapshot** — `[Project]_Manuscript_Snapshot_[runlabel].md` (above), the immutable reference.
2. **The annotation manifest** — a **single** `apodictic.annotation.v1` real-JSON block (the posture of `apodictic.viz_manifest.v1`: one block, nested arrays validated in code), with the top-level shape pinned now so it is not a dead-end for the future quote-locator gate:

   ```
   { "schema": "apodictic.annotation.v1",
     "project": "<name>", "runlabel": "<label>",
     "snapshot_path": "<file>", "snapshot_sha256": "<hex>", "snapshot_line_count": <int>,
     "annotations": [ { "finding_id": "F-…", "anchor": { "kind": "<rung>", "value": "<resolved>" },
                        "comment": "<verbatim field projection>" }, … ] }
   ```

   The `snapshot_*` fields are the binding from §Prerequisite (the validator resolves *that* snapshot, not "newest"). Each `annotations[]` entry's `comment` is a **verbatim projection of the finding's fields** (see Firewall). The manifest is the contract the validator checks.
3. **The annotated copy** — a render that injects CriticMarkup comments (`{>> … <<}`) into a copy of the snapshot. CriticMarkup because it is plain text, diff-friendly, and uses a *bounded, documented* marker syntax whose removal is reversible (see `A2`).

The manifest→render split is the posture of [Manuscript-Structure Visualizations](manuscript-visualizations.md): the structured artifact is the source of truth, the human-facing surface is a pure function of it (Harness Contracts v2 direction).

## Firewall compliance

- **Comment text is a fixed template over verbatim finding fields.** A comment is exactly:
  `[<severity> · <finding_id>] <mechanism> — fix class: <fix_class>. (See letter §<finding_id>.)`
  where `<severity>`, `<finding_id>`, `<mechanism>`, `<fix_class>` are the finding's **verbatim** field values and the rest is fixed boilerplate. There is **no free-text slot**, so the renderer cannot author, abbreviate, paraphrase, or smuggle content. (This resolves the earlier tension between "scannable margin" and "provenance-checkable": scannability comes from the leading `[severity · id]` and the letter link, not from paraphrase. Full context lives in the letter, reached by ID.)
- **Field safety — the "no free-text slot" claim is necessary but not sufficient.** `apodictic.finding.v1` permits `mechanism` / `fix_class` to be *any* string, so a verbatim projection can still carry a newline, a `{>>`/`<<}` sigil, or a markdown table pipe straight into the margin — producing a malformed CriticMarkup span or a multi-line injection while `A5`'s field-equality still passes. So a field used inside the comment must be an **inline-CriticMarkup-safe string** — no `\r`, `\n`, `{>>`, `<<}`, or `|`. Increment 1 does **not** sanitize or escape (escaping would be a reversible transform the spec has not defined); it **fails loudly** (`A5` sub-rule + the `A2` precondition below), directing to a finding-hygiene fix. A schema-valid-but-unrenderable Must-Fix is surfaced as an error, never silently dropped (severity honesty).
- **No prose mutation.** The annotated copy, run through the **specified reverse transform** (remove every `{>> … <<}` span), must equal the snapshot exactly (`A2`).
- **No anchor invention.** Every anchor resolves against the snapshot, or is an honest `document` note (`A3`).

These make the deliverable firewall-disciplined for **Increment 1's comment-only render**. They do **not** by themselves cover the future quote-locator increment, whose content-matching introduces a new failure mode (a fabricated quote match); that increment ships its own gate (§Increment plan). The spec claims discipline for what it builds, not for what it defers.

## Severity honesty

- **Every locked Must-Fix is surfaced.** Each body Must-Fix in the Ledger must appear as an annotation — line-anchored if locatable, a `document` note if not (`A4`). The margin analogue of `softness-check`'s locked→delivered rule: a Must-Fix cannot quietly fail to reach the marked-up copy.
- **Severity travels verbatim.** The comment template leads with the canonical `<severity>` token, copied from the finding; the renderer cannot drop or soften it (it has no slot to do so).

## The `annotated-manuscript` validator

`validate.sh annotated-manuscript <run_folder>` resolves the newest manifest, the annotated copy, and the Findings Ledger, then resolves the **snapshot by the manifest's `snapshot_path`/`snapshot_sha256` binding** (not a "newest snapshot" glob — see §Prerequisite). Delegates to `scripts/annotation_manifest.py`. **Degrade posture (house style):** the bare `validate.sh annotated-manuscript …` command emits a `WARN` and exits `0` without `python3` (advisory only); but where `python3` is present the Python validator hard-gates — `--self-test-all` and `--check-all` **fail** if it exists and fails. Report lines are namespaced `annotated-manuscript:<ID>` so cross-validator `--check-all` output stays unambiguous.

| ID | Severity | Rule |
|---|---|---|
| **A1 — manifest schema** | ERROR | The single `apodictic.annotation.v1` block parses and is well-formed: the top-level binding fields (`schema`, `project`, `runlabel`, `snapshot_path`, `snapshot_sha256`, `snapshot_line_count`, `annotations[]`) are present and typed, and each `annotations[]` entry has `finding_id`, `anchor {kind, value}`, `comment`. (The shared schema engine validates the **subset** it supports — `required`/`const`/`enum`/`type`/`minItems`/`pattern`; the *nested* `anchor.kind ∈ {line-range, section, chapter, document}` enum and per-entry shape are enforced in `annotation_manifest.py`, like every other nested-field check.) **`finding_id` is unique across `annotations[]`** — a duplicate (e.g. one `document` and one `chapter` entry for the same finding, which a per-ID check would pass while the render double-comments it) is an ERROR. |
| **A2 — no prose mutation (signature gate)** | ERROR | Applying the specified reverse transform — delete every `{>> … <<}` span — to the annotated copy yields a byte string **identical to the bound snapshot** (the one named by `snapshot_path`/`snapshot_sha256`; a mismatch between binding and the resolved file is itself an A2 failure). **Two-sided hard precondition, checked before render:** the transform is reversible only if **neither** the snapshot **nor** any finding field projected into a comment contains a CriticMarkup sigil (`{>>`, `<<}`). Either side containing one is a loud failure (snapshot → escaping pass; field → finding-hygiene fix), never a guess. This is the firewall made checkable for the comment-only render. |
| **A3 — anchor integrity** | ERROR | Every `anchor` resolves against the bound snapshot: a `line-range` within the snapshot line count whose token exactly equals a Timeline scene-id (per the ladder); a `section`/`chapter` heading that exists; or the literal `document` kind. **Heading semantics:** headings are **Markdown ATX only** (`#…`), matched on normalized (trimmed, case-insensitive) text; a `chapter`/`section` anchor whose heading is **ambiguous** (the same heading appears more than once in the snapshot) is **not** precise enough — it must degrade to `document` or hard-fail, never silently first-match. A non-locatable ref resolving to `document` is **not** an A3 error (honest degradation); a `line-range`/`section`/`chapter` that does **not** resolve **is**. *Scope note: A3 validates anchor existence only; no evidence-to-prose matching, and it does not cover the future character-precise increment's failure mode.* |
| **A4 — Must-Fix reaches the marked-up copy** | ERROR | The rendered comment-span multiset **equals** the manifest comment multiset (both directions), then every body Must-Fix is present. "Body Must-Fix" = every `apodictic.finding.v1` block in the selected Findings Ledger whose `severity == "Must-Fix"` (not prose bullets, not letter citations, not sidecar findings) — the set from **reusing `finding_trace.py`'s ledger-inventory primitive**, by ID. **Forward:** each manifest comment must render as **exactly one** CriticMarkup span (a Must-Fix present in the manifest but **not rendered** — annotated copy byte-identical to the snapshot — **fails**, the gap a manifest-only check misses). **Inverse:** **no** rendered span may be absent from `annotations[]` — an extra *authored* CriticMarkup note passes A2 (the reverse transform deletes it) and every per-manifest check, smuggling un-projected content into the deliverable; it is a Firewall violation and **fails** here. (The margin analogue of `softness-check`'s locked→delivered rule.) |
| **A5 — comment is a verbatim, renderable field projection** | ERROR | Each `comment` equals the fixed template applied to its finding's verbatim `severity`/`id`/`mechanism`/`fix_class` (field-equality, not substring — it neither false-fails on legitimate abbreviation, of which there is none, nor passes invented prose that merely contains the finding's tokens). **Sub-rule (renderability):** each projected field must be an inline-CriticMarkup-safe string — no `\r`, `\n`, `{>>`, `<<}`, or `|`. The mechanical proof that the renderer *projected* (it did not author) **and** that what it projected is a well-formed inline span. |
| **W1 — coverage / drift / normalization** | WARN (ERROR under `--strict`) | A Should/Could finding with a locatable ref left un-anchored; **or** a Timeline line-range that overruns the snapshot at a boundary; **or** a snapshot that is not LF-normalized with a trailing newline (the harness owns normalization — the validator never rewrites the snapshot, so this is advisory, not an A2 break). Advisory: a Must-Fix-only annotated pass is legitimate, and a one-line boundary drift is usually benign. Override `<!-- override: annotation-coverage <F-…> — <rationale> -->`. |

**Report & exit.** One line per annotation — `finding_id · anchor.kind · anchor.value` — plus the check summary. Exit `0` clean / WARN-only, `1` on any ERROR (or WARN under `--strict`), `2` usage. Override markers (`<!-- override: … -->`) are honored for W1, matching `editor-scaffolding` / `feedback-triage`.

**Ownership boundary.** `annotated-manuscript` owns the **manuscript-copy annotation contract**: the no-mutation transform, anchor existence/degradation, verbatim comment projection, and Must-Fix presence *in the marked-up copy*. It traces **ledger→manifest→rendered-span by ID** (the un-owned dimension), reusing `finding-trace`'s ledger-inventory primitive for the Must-Fix set rather than reimplementing it; it does **not** re-check letter↔ledger integrity (`finding-trace`), severity fidelity in the letter (`softness-check`), or Timeline arithmetic (`timeline-*`). It *consumes* Timeline ranges for anchoring; it does not validate them.

## Canonical `--check-all` gate

Three worked fixtures, so the gate exercises more than the coarsest rung *and* proves the no-fabrication path:

1. The shipped `example-findings-ledger.md` (`F-RR-01`, a `Chapter 9` Must-Fix) → exercises the **`chapter`** rung + `A4`'s rendered-span bijection (the Must-Fix actually appears as a CriticMarkup span in the annotated copy).
2. A dedicated fixture: a tiny snapshot manuscript **with chapter headings and a paired `example-timeline.md`-style line range**, plus a finding whose `evidence_refs` token **exactly equals** that Timeline scene-id → exercises the **`line-range`** rung, `A2` (reverse-transform identity against the *bound* snapshot), and `A5` (verbatim projection).
3. A **negative** fixture: a finding whose ref shares a *chapter* with a scene but matches no scene-id (`["Ch. 12"]` against scene `Ch 12 §1`) → proves the resolver does **not** fabricate a `line-range`, degrading to `chapter` (the no-fabricate-precision guarantee, made into a gate rather than a claim).

`validate.sh --check-all` runs `annotated-manuscript` against all three, proving no-mutation, line-range *and* chapter anchoring, rendered Must-Fix completeness, and the no-fabrication degrade on canonical artifacts (the "canonical-framework validator runs as release gate" discipline, `ROADMAP.md` §Deferred). Without fixtures 2–3 the line-range/A2 mechanics and the no-fabricate guarantee would ship unexercised by the gate — the failure the §Deferred discipline exists to prevent.

## Increment plan

**Increment 1 (this spec):** the snapshot step, `apodictic.annotation.v1` schema (added to `schemas/`, auto-discovered by `apodictic_artifacts.known_schema_ids()`, which globs the directory), `scripts/annotation_manifest.py` (anchor resolver + reverse-transform diff + validator), `validate.sh annotated-manuscript`, the CriticMarkup renderer (fixed comment template), the three worked fixtures, and the `--check-all` gate. Anchor granularity = line-range / section / chapter / document; no character-precise anchoring.

Two cross-cutting build obligations that are easy to miss:
- **Dual script mirror.** `annotation_manifest.py` and the `validate.sh` arm exist as **two committed, byte-identical copies** — `plugins/apodictic/scripts/` (canonical) and root `scripts/` (what CI runs) — and `annotation_manifest.py` joins the `check-mirror` set. The same PR updates the `validate.sh` command list, the aggregate validator list + count, `--self-test-all`, and the `--check-all` text.
- **Shared chapter parser.** The chapter rung's `chapter_token(ref)` helper is **extracted and shared** with `viz_manifest.py` (broadening its old `_CHAPTER_RE` to the four forms `Chapter N` / `Ch. N` / `Ch.N` / `Ch N`). This broadens a shipped validator's chapter binning — but **verified at build, no fixture re-bin was needed**: viz `--check-all` validates `example-structure-map-manifest.md` against `example-findings-ledger.md` (both `Chapter 9` / `Ch N`, unaffected by the broadening), and the only shipped `Ch.N`-form ref — `example-run-folder`'s `["Ch.3 p.40"]` — never flows into a viz manifest, so E2 provenance is not exercised against it and viz's `--check-all` stays green. (Latent: a future Structure Map generated from a `Ch.N` / page-suffixed ledger would now bin where it previously read `unplaced`.)

**Future increments (not built):**
- **DOCX / Google Docs / Obsidian comment export** — render targets over the same manifest; each must preserve `A2` semantics in its native comment model (and define its own reverse transform).
- **Character-precise anchoring** — a quote-locator narrowing an anchor to the exact sentence by matching the finding's evidence against the snapshot, *only when the match is unambiguous*. **Ships its own integrity gate** (A-something: the matched quote must occur verbatim and uniquely in the snapshot) because A3 does not cover content matching.
- **Letter ↔ margin cross-links** — bidirectional `F-…` links between letter and annotated copy.
- **Round-trip re-anchoring** — when the writer revises, detect which anchors moved or resolved (pairs with [Draft-over-Draft Structural Regression Testing](../ROADMAP.md#horizon-capacities), Horizon item 6). Increment 1 treats the annotated copy as a *snapshot* of one run, exactly like the letter.

## Increment 2 — Character-precise anchoring (quote-locator)

**Status:** Proposed (unbuilt). The natural successor to Increment 1: narrow an anchor from a line-range/chapter down to the **exact span of prose** the finding is about, so the margin note sits on the sentence, not the top of the scene. This is the first increment that changes the *firewall surface*, so it ships its **own** integrity gate.

### The problem Increment 1 left open

Increment 1's finest rung is `line-range` — a whole Timeline scene, often dozens of lines. A developmental finding frequently points at one sentence ("this exchange reads as small talk when the stakes should be highest"); the annotated copy should put the note on *that exchange*. Increment 1 stopped at line granularity on purpose: going finer introduces a failure mode A1–A5 do **not** cover — a **fabricated quote**, an anchor that claims to sit on manuscript text that isn't actually there, or is there in several places so "the exact spot" is a guess. A3 validates that an anchor *resolves* (a heading exists, a line is in bounds); it has no concept of *content matching*. So character-precise anchoring is an anchor-**plus-content** problem, and it needs a content-integrity gate.

### Where the quote comes from (the prerequisite, named honestly)

A character-precise anchor needs a **verbatim manuscript substring** to locate against. `apodictic.finding.v1` does not carry one: its `evidence_refs` are *loci* (`"Chapter 9"`, `"Ch.3 p.40"`) and its `mechanism` is a *diagnosis* (`"the want never forces a sacrifice"`) — neither is manuscript prose, so neither can be matched against the snapshot. So this increment adds one optional field:

- **`evidence_quote`** (optional, `apodictic.finding.v1`): a **verbatim** substring copied from the manuscript that the finding is about. **Optional by design** — a finding without it behaves exactly as in Increment 1 (the new rung simply does not apply), so the change is fully backward-compatible and the existing corpus is untouched. A diagnostic pass populates it only when it has an exact textual locus, else omits it. The field is **manuscript bytes, never authored** — and that claim is what the new gate (A6) *proves*, the same way A5 proves the comment is a projection.

> **Bounded scope.** Populating `evidence_quote` at scale across the diagnostic passes is **upstream** pass work — a separate, demand-gated effort. Increment 2 builds the **consumer**: the locator + the rung + the kind + the gate + the schema field, so the capability exists and is gate-proven on fixtures the moment any pass emits a quote. It does **not** require retrofitting every pass; a corpus with no `evidence_quote` is a no-op for the new rung.

### The ladder gains a finest rung

The per-token ladder (Increment 1: `line-range` > `section` > `chapter` > `document`) gains **`quote`** as the new finest rung (rank 5, above `line-range`):

- **`quote`** — when the finding carries an `evidence_quote` that occurs in the bound snapshot **verbatim and exactly once**. The anchor is the character span of that single occurrence.
- Quote occurs **zero times** (absent from the snapshot) → **not** a quote anchor; the resolver **falls through** to the Increment-1 ladder *and the build refuses to emit a quote anchor* (a suspect/fabricated quote is never anchored). Never fabricates a span.
- Quote occurs **more than once** (ambiguous) → **not** a quote anchor; falls through to the coarser rung — the Increment-1 "never fabricate precision" rule, now at the sentence level. A `quote` anchor is emitted **only** on a unique verbatim match.

The Increment-1 per-token rules (artifact-scoping; "finest rung any manuscript-scoped token supports") are unchanged; `quote` simply outranks `line-range` when an unambiguous quote is available.

### The anchor value

A `quote` anchor records both the span and the text, so the gate and the renderer are deterministic and don't re-derive each other:

```
{ "kind": "quote", "value": "<start>-<end>", "quote": "<verbatim matched text>" }
```

`<start>-<end>` is the **0-based, half-open character offset range** into the **normalized snapshot** (`snapshot[start:end] == quote`), and `quote` is the verbatim matched substring. The offsets make placement and the no-mutation diff exact; the `quote` field makes A6 checkable without trusting the offsets in isolation.

### Render placement

The comment span is injected **immediately after `<end>`** — no surrounding whitespace, exactly like every Increment-1 span — so the CriticMarkup note sits at the close of the quoted sentence. **A2 is unchanged and still holds**: deleting every `{>> … <<}` span yields the snapshot byte-for-byte, because a span inserted at a character offset is removed by the same reverse transform. Character precision does not weaken the no-mutation proof.

### The new gate — A6 (quote integrity)

`quote` anchoring introduces exactly one new failure mode, so it gets exactly one new gate:

| ID | Severity | Rule |
|---|---|---|
| **A6 — quote integrity (the increment's signature gate)** | ERROR | For every `quote` anchor: (a) the recorded `quote` text occurs in the bound snapshot **verbatim and exactly once** — **zero** occurrences is a *fabricated* quote (the failure A3 cannot see); **>1** is an *ambiguous* quote that must have degraded, not anchored; and (b) the offsets delimit exactly that occurrence (`snapshot[start:end] == quote`, and that is the sole occurrence). A `quote` anchor failing either half is an ERROR — the renderer must not place a sentence-level note on text the manuscript does not *uniquely* contain. |

A6 is the character-level analogue of A3 (anchor existence), but for **content**, which A3 explicitly does not cover. Division of labour holds: **A6** proves the *quote* is a real, unique manuscript span; **A5 is unchanged** and still proves the *comment* is a verbatim finding-field projection. The quote (manuscript bytes, gated by A6) and the comment (finding-field projection, gated by A5) are separately proven — neither is authored.

All Increment-1 gates still apply to a quote-anchored manifest: A1 (schema — now allowing the `quote` anchor kind + optional `evidence_quote`/`quote` fields), A2 (no mutation — unchanged), A3 (validates the non-quote anchors; a `quote` anchor is A6's job, not A3's — A3 skips `kind == "quote"`), A4 (multiset equality — unchanged), A5 (verbatim comment projection — unchanged).

### Backward compatibility

A manifest with no `quote` anchors validates exactly as in Increment 1 (A6 is a no-op when no quote anchor is present). A finding with no `evidence_quote` resolves on the Increment-1 ladder. The `quote` kind is *added* to the `anchor.kind` enum; `evidence_quote` is an *optional* finding field. No existing fixture changes behaviour, and the canonical Increment-1 `--check-all` fixture still passes untouched.

### Canonical `--check-all` gate (the fixtures Increment 2 adds)

Three new fixtures exercise the rung and **both** halves of the no-fabrication guarantee:
1. **Positive** — a finding whose `evidence_quote` occurs verbatim-once → a `quote` anchor on the exact span; A6 passes; the rendered span sits at the sentence; A2 reverse-transform identity holds.
2. **Ambiguous-degrade (negative)** — a finding whose `evidence_quote` appears **twice** in the snapshot → resolver degrades to the coarser rung; **no** `quote` anchor fabricated.
3. **Fabricated-quote (negative)** — a manifest carrying a `quote` anchor whose text is **absent** from the snapshot → **A6 ERROR** (the fabrication guard — the whole reason this increment ships its own gate).

### Increment boundary

**In:** the optional `evidence_quote` finding field; the `quote` anchor rung + kind; the unique-verbatim locator (in `build`); offset-precise render placement; the **A6** integrity gate; backward-compatibility (Increment-1 manifests + the existing gate fixture unchanged); the three new `--check-all` fixtures.

**Not in (still future):** retrofitting diagnostic passes to *emit* `evidence_quote` at scale (upstream, demand-gated); DOCX / Google-Docs / Obsidian export; letter↔margin cross-links; round-trip re-anchoring.

## Self-review (Increment 1)

- *Why a snapshot, not the live file* — anchoring and the no-mutation proof need a frozen, line-stable left-hand side the framework does not otherwise persist. Snapshotting is the smallest honest fix; it also makes the deliverable reproducible.
- *Why verbatim projection instead of a heuristic provenance check* — a substring/token check is simultaneously gameable (invented prose that contains the finding's tokens) and false-failing (legitimate abbreviation). A fixed template with no free-text slot removes both failure modes and makes `A5` an equality, not a guess.
- *Why `document` is not an A3 error* — many real `evidence_refs` point at pass artifacts, not manuscript loci. Forcing them to a fabricated line would violate "never guess precision"; surfacing them as honest document notes keeps `A4` (Must-Fix completeness) satisfiable without inventing anchors.
- *Why `A2` fails loudly on sigil collision* — silently mishandling a manuscript that already uses `{>>`/`<<}` would break the one guarantee the whole deliverable rests on. Better a loud failure with an escaping path than a wrong "no mutation" pass.
