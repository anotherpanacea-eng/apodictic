# Promise-Contract Fidelity (workflow)

**Status:** v1 (document-fidelity layer; consumes Shelf & Positioning).
**When:** the author has marketing copy — a query letter, synopsis, jacket blurb, or logline — and a manuscript whose Contract has been inferred. Run alongside or after Submission Readiness, when the author is heading toward submission.
**Home:** core-editor (manuscript-content analysis). Design + lineage: [`docs/promise-contract-audit.md`](../../../../../docs/promise-contract-audit.md).

---

## Purpose & firewall

APODICTIC's foundational move is **contract inference** — read the manuscript, predict its Contract (genre, reader promise, controlling idea, ending type), and treat the gap between inferred and intended as the signal. This module points that same move at the author's **marketing copy.** A query foregrounds a subplot the book treats as minor; a blurb discloses a reveal the manuscript protects; the controlling idea the book is built on never appears in the pitch at all. Each is a **promise the copy makes — or fails to make — that the contract does not keep.**

**The firewall: diagnose the copy; never draft it.** The module identifies a mismatch and a *class* of repair ("the query leads with the subplot; the kept promise is the central conflict — consider leading there") and **never writes the replacement query, blurb, logline, or synopsis.** (Shelf & Positioning's Reframe Protocol *does* rewrite pitches; this is the diagnostic-only sibling.) **No manuscript-content invention** either: PCF3 flags the copy's over-reach; the fix is never "add the scene to satisfy the copy."

---

## Consume Shelf & Positioning — do not duplicate (prerequisite)

The [Shelf & Positioning audit](../../specialized-audits/references/craft/shelf-positioning.md) already owns **genre-promise mismatch**, **comp misrepresentation** (the Vibe-Only Comp test), and **tone-shelf mismatch** — and even *rewrites* pitches in its Reframe Protocol. This module therefore **does not re-flag genre, comp, or tone.** Where those matter it is a **prerequisite**: if Shelf & Positioning has run, consume and cite its findings; if it has not, recommend running it and record reduced coverage rather than re-deriving positioning. What's left — the non-overlapping residue — is **document-level fidelity**: emphasis, disclosure, over/under-promise, cross-document consistency. That is this module's whole job.

---

## Inputs

1. **The inferred Contract** (`core-editor/references/contract-template.md`) — the flags cite the specific schema fields they measure against: `READER PROMISE`, `CONTROLLING IDEA`, `ENDING TYPE` (and `NON-NEGOTIABLES`). `CONTROLLING IDEA` is now a first-class colon-delimited contract field (it resolves to that schema field directly — no section-parsing special case). Genre/tone/comps are Shelf & Positioning's territory, not measured here.
2. **The persisted pitch copy** — a first-class, durable input (not a runtime paste): `[Project]_Pitch_Copy_[runlabel].md` carrying one `apodictic.pitch_copy.v1` block per document, each with a declared `copy_type` and the **verbatim** text. Persisting it is what makes the firewall guard (W1) and the form gate (P3) mechanically checkable.
3. **Reused, if present** — Shelf & Positioning findings (genre/comp/tone) and the Pass-8 reveal **timeline** (prose, in the Ledger) for the disclosure judgment.

---

## The artifact: `[Project]_Pitch_Copy_[runlabel].md`

A set of `apodictic.pitch_copy.v1` blocks — one per persisted marketing document:

```markdown
<!-- apodictic:pitch_copy
{"schema":"apodictic.pitch_copy.v1","id":"PC-01","copy_type":"query",
 "text":"<the verbatim query letter, byte-for-byte as the author wrote it>"}
-->
```

- **`copy_type`** — `query` | `synopsis` | `blurb` | `logline`. Form-calibrates the flags (see Mode Calibration).
- **`text`** — the **verbatim** copy. The module diagnoses it and never drafts it; W1 checks that any multi-sentence quoted block in the report is a verbatim substring of this text.

Field set canonical in `schemas/apodictic.pitch_copy.v1.schema.json` (single-sourced, **not** mirrored). Worked example: `core-editor/references/example-promise-contract.md`.

---

## Named diagnostic flags (`PCF`, net-new only)

Origin code is **`PCF`** (Promise-Contract Fidelity) — *not `PC`*, which is Stakes System's "Personal Coupling". Findings are `apodictic.finding.v1` blocks (`F-PCF-NN`). Every flag is a **two-sided gap** and must cite both sides via the namespaced-ref convention below.

- **PCF1 — Emphasis distortion.** The copy foregrounds what the manuscript backgrounds, or omits the actual central conflict. *Measured against:* `READER PROMISE` + `CONTROLLING IDEA`.
- **PCF2 — Reveal leak.** A no-spoiler copy type discloses a reveal the manuscript protects. *Measured against:* the reveal timeline (Pass 8) + `ENDING TYPE`. **Form-calibrated:** a synopsis is *meant* to disclose, so PCF2 never fires on `synopsis` (P3).
- **PCF3 — Over-promise.** The copy promises content/scenes/payoff the manuscript does not contain. *Measured against:* the manuscript. (Fix class is always *bring the copy back to the book*, never *add to the book*.)
- **PCF4 — Under-sell.** The manuscript's strongest kept promise — the thing the book is built on — is absent from the copy. *Measured against:* `CONTROLLING IDEA` + `READER PROMISE`.
- **PCF5 — Cross-document inconsistency.** Query, synopsis, and blurb promise *different books*. *Measured across:* the `pitch_copy.v1` documents.

To make PCF2's form gate (P3) mechanical, name the flag in the finding's `mechanism` (e.g. "PCF2 reveal leak: …").

---

## The namespaced evidence-ref convention (makes the two-sided check real)

`apodictic.finding.v1.evidence_refs` is a flat array of untyped strings, so a validator cannot otherwise tell a copy-side ref from a contract-side ref. **`PCF` findings prefix each ref:**

- `copy:<copy_type>¶<n>` — a span in the persisted pitch copy (e.g. `copy:query¶2`).
- `contract:<FIELD>` — a Contract field (e.g. `contract:CONTROLLING IDEA`).
- `ms:<locus>` — a manuscript locus (e.g. `ms:Ch 9`).

P1 enforces that every `F-PCF` finding carries **≥1 `copy:` ref and ≥1 `contract:`/`ms:` ref** — the two-sidedness that makes a gap a gap. This is a constrained convention on the shared schema, declared here and checked **only for `PCF`-origin findings**; it does not change behavior for any other origin.

---

## Distinguish — intentional angle vs. accidental break

A pitch legitimately *chooses an angle*; not every divergence is a defect. Applying the canonical Severity Honesty Protocol (`output-policy.md §Severity Honesty Protocol`, the same lock-then-classify the Deficit Lock uses): a **deliberate positioning choice** the author can articulate, that emphasizes a *real* thread, is an **Author Decision**, not a flag; an **unintended misrepresentation** is the flag. **Lock-then-classify:** the gap's severity is locked before the intentionality reframing, so a deliberate choice cannot launder a genuine over-promise into a "choice."

## Severity & the #14 boundary

Findings use the canonical Must/Should/Could scale, where severity = **fidelity risk** (how badly promise and book diverge), never market outcome. The module **never predicts sales** — that lens is the separate Positioning-Risk Lens (Horizon item 14). W2 guards the seam with a concrete prohibited-phrase set ("won't sell", "agents will pass", "no market for", "unmarketable", "won't find an audience").

---

## Mode calibration (by copy type)

| copy_type | PCF2 reveal leak | PCF1/PCF4 emphasis | Notes |
|---|---|---|---|
| query | fires | full | the core case |
| synopsis | **suppressed** (P3) | full | synopses disclose by design |
| blurb | fires | full | |
| logline | fires | PCF1 only | brevity calibration |

---

## The `promise-contract` validator

`validate.sh promise-contract <run_folder|files>` resolves the `apodictic.pitch_copy.v1` input (newest `*_Pitch_Copy_*.md` wins) and the `F-PCF` findings. Delegates to `scripts/promise_contract.py`; degrades to advisory `WARN` without `python3`.

| ID | Severity | Rule |
|---|---|---|
| **P1 — two-sided gap** | ERROR | Every `F-PCF-NN` finding carries ≥1 `copy:` ref and ≥1 `contract:`/`ms:` ref. A one-sided "gap" is an unsupported assertion. |
| **P2 — pitch copy persisted & typed** | ERROR | An `apodictic.pitch_copy.v1` input exists and every document declares a valid `copy_type`. |
| **P3 — reveal-leak form gate** | ERROR | A PCF2 finding's `copy:` ref must not point at a `synopsis` (a synopsis discloses by design). |
| **W1 — drafted-copy leak (firewall)** | WARN (ERROR `--strict`) | A multi-sentence quoted block in the report that is **not** a verbatim substring of the persisted pitch copy → authored replacement copy. Override is **snippet-keyed** (a leaked quote isn't attributable to one finding id): `<!-- override: drafted-copy <snippet of the leaked text> — <rationale> -->` silences only the leak its snippet matches — one override can't blanket-silence the firewall. |
| **W2 — market-prediction drift (#14 boundary)** | WARN (ERROR `--strict`) | A `PCF` finding matches the prohibited sales-prediction phrase set. Override `<!-- override: market-prediction PCF-NN — <rationale> -->`. |

**Ownership boundary.** `promise-contract` owns the **pitch↔contract fidelity contract**: two-sided gap integrity, copy persistence/typing, the disclosure form gate, and the two firewall/scope guards. It does **not** compute positioning or flag genre/comp/tone (`shelf-positioning` owns those), validate the reveal economy itself (Pass 8), judge readiness (Submission Readiness), or re-check finding severity fidelity (`softness-check`).
