# Promise-Contract Fidelity — does the pitch keep the promise the book makes?

**Status:** Proposed (unbuilt). Roadmap: `ROADMAP.md` → [Horizon Capacities](../ROADMAP.md#horizon-capacities) Tier 1, item 4. Proposed implementation surface: a **core-editor workflow module** (homed like [Legal Risk Register](legal-risk-register.md) / Editor Scaffolding — *not* a craft audit), `core-editor/references/promise-contract.md`, an `apodictic.pitch_copy.v1` persisted input + `apodictic.finding.v1` findings with origin `PCF`, `scripts/promise_contract.py`, `validate.sh promise-contract`, and a worked example.
<!-- built-when: scripts/promise_contract.py -->

APODICTIC's foundational move is contract inference: read the manuscript, predict its **contract** (genre, reader promise, controlling idea, ending type), and treat the gap between inferred and intended as the signal. The same move applies to the author's **marketing copy**. A query foregrounds a subplot the book treats as minor; a back-cover blurb discloses a reveal the manuscript protects; the controlling idea the book is built on never appears in the pitch at all. Each is a **promise the copy makes — or fails to make — that the contract does not keep.** The writer usually can't see it, because they know what they meant.

This is a thin module, by design. The first version of this spec tried to be a standalone audit and **duplicated three things Shelf & Positioning already does** (genre mismatch, comp misrepresentation, tone mismatch). This version **consumes** Shelf & Positioning instead of competing with it, and contributes only the document-fidelity layer that no existing surface owns.

## Relationship to Shelf & Positioning (consume, don't duplicate)

The [Shelf & Positioning audit](../plugins/apodictic/skills/specialized-audits/references/craft/shelf-positioning.md) (built) already: computes the Evident Shelf from the text; runs **Signal-Structure Mismatch / Contract Violation** (≈ genre-promise mismatch), the **Vibe-Only Comp** test (≈ comp misrepresentation), and **Tone-Shelf Mismatch**; and even *rewrites* pitches in its Reframe Protocol. Promise-Contract Fidelity therefore **does not re-flag genre, comp, or tone mismatch.** Where those matter, it is a **prerequisite**: if Shelf & Positioning has run, this module *consumes and cites* its findings; if it has not, this module recommends running it and records reduced coverage, rather than re-deriving positioning.

What's left — the genuine, non-overlapping residue — is **document-level fidelity**: emphasis, disclosure, over/under-promise, and cross-document consistency. That is this module's whole job.

## Inputs

1. **The inferred Contract** (`core-editor/references/contract-template.md`), citing the *specific* fields each flag measures against: `READER PROMISE`, `CONTROLLING IDEA`, `ENDING TYPE` (and `NON-NEGOTIABLES`). Genre/tone/comps are Shelf & Positioning's territory, not measured here.
2. **The persisted pitch copy** — a first-class, durable input (not a runtime paste): `[Project]_Pitch_Copy_[runlabel].md` carrying one `apodictic.pitch_copy.v1` block per document, each with a declared `copy_type` (`query` / `synopsis` / `blurb` / `logline`) and the verbatim text. Persisting it is what makes the firewall guard (`W1`) and the form gate (`P3`) mechanically checkable — there has been no convention for an external pasted document, so this module establishes one.
3. **Reused, if present** — Shelf & Positioning findings (genre/comp/tone) and the reveal-economy map (Pass 8) for the disclosure gate.

## Named diagnostic flags (`PCF`, net-new only)

Origin code is **`PCF`** (Promise-Contract Fidelity). *Not `PC`* — `PC` is already taken by Stakes System's "Personal Coupling" (`PC-1…PC-4`, registered in `pass-dependencies.md §4e`), and `F-PC-NN` would collide and break per-run finding-ID uniqueness. Findings are `apodictic.finding.v1` blocks (`F-PCF-NN`). Every flag is a **two-sided gap** and must cite both sides via the namespaced-ref convention below (`P1`).

- **PCF1 — Emphasis distortion.** The copy foregrounds what the manuscript backgrounds, or omits the actual central conflict. *Measured against:* `READER PROMISE` + `CONTROLLING IDEA`.
- **PCF2 — Reveal leak.** A no-spoiler copy type discloses a reveal the manuscript protects. *Measured against:* reveal economy (Pass 8) + `ENDING TYPE`. **Form-calibrated:** a synopsis is *meant* to disclose, so PCF2 never fires on `synopsis` (`P3`).
- **PCF3 — Over-promise.** The copy promises content, scenes, or a payoff the manuscript does not contain. *Measured against:* the manuscript. (Fix class is always *bring the copy back to the book*, never *add to the book* — that would be content invention.)
- **PCF4 — Under-sell.** The manuscript's actual strongest kept promise — the thing the book is built on — is absent from the copy. *Measured against:* `CONTROLLING IDEA` + `READER PROMISE`.
- **PCF5 — Cross-document inconsistency.** Query, synopsis, and blurb promise *different books* (the query's central conflict isn't the blurb's). *Measured across:* the `pitch_copy.v1` documents.

## The namespaced evidence-ref convention (makes `P1` real)

`apodictic.finding.v1.evidence_refs` is a flat array of untyped strings, so a validator cannot otherwise tell a copy-side ref from a contract-side ref. `PCF` findings therefore adopt a documented ref convention: each ref is **prefixed** — `copy:<copy_type>¶<n>` (a span in the persisted pitch copy), `contract:<FIELD>` (a contract field), or `ms:<locus>` (a manuscript locus). `P1` enforces that every `F-PCF` finding carries **≥1 `copy:` ref and ≥1 `contract:` or `ms:` ref** — the two-sidedness that makes a gap a gap. (This is a constrained convention on the shared schema, declared here and checked only for `PCF`-origin findings; it does not change the schema for other origins.)

## Firewall compliance (the signature boundary)

- **Diagnose the copy; never draft it.** The module identifies a mismatch and a *class* of repair ("the query leads with the subplot; the kept promise is the central conflict — consider leading there") and **never writes the replacement query, comp, logline, or blurb.** (Shelf & Positioning's Reframe Protocol *does* rewrite pitches; this module deliberately does not — it is the diagnostic-only sibling.) `W1` is now a **concrete, robust** guard: a multi-sentence quoted block in the report that is **not a verbatim substring of the persisted pitch copy** is authored copy (firewall leak); a block that *is* a substring is the module legitimately quoting the author's own copy. Persisting the input is what turns this from a fuzzy heuristic into a substring check.
- **No manuscript-content invention.** PCF3 flags the copy's over-reach; the fix is never "add the scene to satisfy the copy." Intervention *classes* only (`SKILL.md §The Firewall`).

## Distinguish framework — intentional angle vs. accidental break

A pitch legitimately *chooses an angle*; not every divergence is a defect. Applying the canonical Severity Honesty Protocol (`output-policy.md §Severity Honesty Protocol`, the same lock-then-classify the Deficit Lock uses):

- A **deliberate positioning choice** the author can articulate, that emphasizes a *real* thread, is an **Author Decision**, not a flag.
- An **unintended misrepresentation** is the flag.
- **Lock-then-classify:** the gap's severity is locked before the intentionality reframing, so a deliberate choice cannot launder a genuine over-promise into a "choice."

## Severity & the #14 boundary

Findings use the canonical Must/Should/Could scale, where severity = **fidelity risk** (how badly promise and book diverge), never market outcome. The module **never predicts sales**. That lens is the separate [Positioning-Risk Lens](../ROADMAP.md#horizon-capacities) (Horizon item 14), kept apart so this stays clear of the §Not Planned "commercial viability guarantees" line. Narrowing to the document-fidelity flags (dropping genre/comp/tone to Shelf & Positioning) also removes the flags most prone to market-drift, so the remaining surface is fidelity-pure. `W2` guards the seam with a concrete prohibited-phrase set ("won't sell", "agents will pass", "no market for", "unmarketable", "won't find an audience").

## Mode calibration (by copy type)

| copy_type | PCF2 reveal leak | PCF1/PCF4 emphasis | Notes |
|---|---|---|---|
| query | fires | full | the core case |
| synopsis | **suppressed** (`P3`) | full | synopses disclose by design |
| blurb | fires | full | |
| logline | fires | PCF1 only | brevity calibration |

## The `promise-contract` validator

`validate.sh promise-contract <run_folder>` resolves the `apodictic.pitch_copy.v1` input, the `F-PCF` findings, and (if present) Shelf & Positioning findings. Delegates to `scripts/promise_contract.py`; degrades to advisory `WARN` without `python3`. Report lines namespaced `promise-contract:<ID>`.

| ID | Severity | Rule |
|---|---|---|
| **P1 — two-sided gap** | ERROR | Every `F-PCF-NN` finding carries ≥1 `copy:` ref and ≥1 `contract:`/`ms:` ref (the namespaced convention). A one-sided "gap" is an unsupported assertion. The signature integrity check — now mechanical because the refs are prefix-typed. |
| **P2 — pitch copy persisted & typed** | ERROR | An `apodictic.pitch_copy.v1` input exists and every document declares a valid `copy_type`. Flags are form-calibrated; an undeclared/absent copy makes PCF2/PCF5 ungovernable. |
| **P3 — reveal-leak form gate** | ERROR | A PCF2 finding's `copy:` ref points at a no-spoiler copy type. A PCF2 raised against a `synopsis` is a calibration error and fails. |
| **W1 — drafted-copy leak (firewall)** | WARN (ERROR under `--strict`) | A multi-sentence quoted block in the report is **not** a verbatim substring of the persisted pitch copy (→ authored replacement copy). Concrete substring check, not a vibe heuristic. Override `<!-- override: drafted-copy PCF-NN — <rationale> -->`. |
| **W2 — market-prediction drift (#14 boundary)** | WARN (ERROR under `--strict`) | A `PCF` finding matches the prohibited sales-prediction phrase set. Keeps the module on the fidelity side of the §Not Planned line. Overridable. |

**Ownership boundary.** `promise-contract` owns the **pitch↔contract fidelity contract**: two-sided gap integrity, copy persistence/typing, the disclosure form gate, and the two firewall/scope guards. It does **not** compute positioning or flag genre/comp/tone (`shelf-positioning` owns those — this consumes them), validate the reveal economy itself (Pass 8), judge readiness (Submission Readiness), or re-check finding severity fidelity (`softness-check`).

## Canonical `--check-all` gate

A worked example — a fixture Contract, an `apodictic.pitch_copy.v1` with a `query` that commits a PCF1 (emphasis) + PCF4 (under-sell) gap (each with namespaced two-sided refs), and a `synopsis` that discloses the ending — is added, and `validate.sh --check-all` runs `promise-contract` against it: proving two-sided-ref integrity (`P1`), copy typing (`P2`), a clean firewall substring scan (`W1`), and the **negative** that the disclosing synopsis must **not** raise PCF2 (`P3`). (The "canonical-framework validator runs as release gate" discipline, `ROADMAP.md` §Deferred.)

## Increment plan

**Increment 1 (this spec):** the module reference (PCF1–PCF5, Distinguish, Mode Calibration, the consume-Shelf-&-Positioning prerequisite), the `apodictic.pitch_copy.v1` persisted input + `PCF` finding origin + namespaced-ref convention, `scripts/promise_contract.py` + `validate.sh promise-contract`, the worked example, and the `--check-all` gate. Homed in core-editor (validators +1, running total fixed at build).

**Future increments (not built):**
- **Comp-experience cross-check** — deepen PCF1/PCF4 by pairing with the comp-validation research mode and Shelf & Positioning's comp set (not duplicating its Vibe-Only Comp test, extending it to the *document*).
- **Persona-targeted fidelity** — pair with [Reader-Persona Simulation](reader-persona-simulation.md): does the copy keep its promise for the segment it targets?
- **A `/promise-check` command + intake routing** (Increment 1 reaches it via audit routing only), mirroring Legal Risk Register's deferred command increment.

## Self-review (Increment 1)

- *Why a core-editor module, not a craft audit* — craft audits (e.g. `reception-risk.md`) ship prose + flags + a markdown map, **no validator and no finding blocks**. This module's value is the validatable fidelity contract (findings + `promise-contract` + `--check-all`), which is the convention of the newer core-editor workflow modules (legal-risk, editor-scaffolding), not of craft audits. Calling it a craft audit (as the first draft did) misrepresented both its home and its conventions.
- *Why it consumes Shelf & Positioning* — re-flagging genre/comp/tone would duplicate ~3 existing tests. The companion-module-reads-the-shared-artifact pattern (the Argument Engine's design principle) is the right shape: this reads positioning, it does not recompute it.
- *Why persist the pitch copy* — without a durable input there is nothing for `P2`/`P3` to check and `W1` stays a vibe heuristic. Persisting it makes the firewall guard a substring check and establishes the missing convention for an external pasted document.
- *Why the namespaced ref convention* — `evidence_refs` is untyped, so the signature two-sided check is impossible without it; prefix-typing the refs (scoped to `PCF` findings) is the smallest change that makes `P1` real.
