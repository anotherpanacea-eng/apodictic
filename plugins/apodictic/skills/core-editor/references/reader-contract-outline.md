# Reader-Contract Reverse Outline — reference

The third leg of the trade developmental-edit deliverable set (alongside the editorial letter and the
Annotated Manuscript): a reverse outline that lays the book out **scene by scene** and maps it against
the **reader contract** it implicitly makes — where each promise is established, where it's paid off,
and where it breaks. Where the letter *argues* about the contract and the Annotated Manuscript marks up
the *prose*, this deliverable is the **structural** view: the promise, projected onto the spine.

Like the Annotated Manuscript, it is an **export/projection** capability — it invents nothing. The
outline is a byte-deterministic projection of four artifacts the run already holds (the Pass 0 reverse
outline, the Contract, the Findings Ledger) plus one gated, ids-only **Contract Map**. The Map is the
model's *only* authored contribution anywhere in the deliverable, and even that is ids only — no prose
(the Firewall's red line).

Spec + rule detail: [`docs/reader-contract-outline.md`](../../../../docs/reader-contract-outline.md).

## The two artifacts

1. **Contract Map** — `[Project]_Contract_Map_[runlabel].md`: one `apodictic.contract_map.v1` block —
   machine-read plumbing, closed-key, ids only. It binds its inputs (`inputs.pass0_sha256` /
   `contract_sha256` / `ledger_sha256`) and lists one clause per contract clause `{clause_id,
   source_field, clause_text, established[], paid_off[], not_localizable, gap_finding_id}`. `clause_text`
   is a **verbatim substring** of the named Contract field; `established`/`paid_off` are Pass 0 scene ids;
   `gap_finding_id` names a Findings-Ledger entry or is `null`.
2. **Reverse outline** — `[Project]_Reader_Contract_Outline_[runlabel].md`: the author-facing document,
   fixed section order — the reader contract (every Contract field, verbatim), the scene spine (every
   Pass 0 scene: `id · what happens · what the reader now knows`), the contract map (each clause,
   `established`/`paid off` at scene ids with that scene's Pass 0 "what the reader now knows" line shown
   verbatim as evidence, plus the gap cell), and an advisory coverage note.

## How to produce it

```
# (author the Contract Map block first — ids only, bound to the staged inputs)
scripts/reader_contract_outline.py build <run_folder>       # R7-gates the Map, then projects the outline
scripts/validate.sh reader-contract-outline <run_folder>    # gates R1–R7
```

Staged discipline: author/gate/render in a scratch copy; move the Map + outline into the run folder
**only** if every gate passes, else name the gate and write nothing (the deterministic-rebuild rule).

## What the gates guarantee

- **R1** the scene spine round-trips to Pass 0 (ids + count + text verbatim — nothing added/dropped/reworded).
- **R2** every Contract schema field is projected, two-sided (none dropped, none invented); an empty field
  renders its literal state (`HEAT LEVEL: —`), never omitted.
- **R3** every scene id in the rendered map resolves in Pass 0, the rendered map ↔ Map block is a bijection,
  and every evidence line byte-matches the cited scene's Pass 0 line.
- **R4** every gap cell is `none logged` or a verbatim projection of the named Ledger finding (paraphrase = fabrication).
- **R5** no untranslated framework shorthand leaks into the deliverable.
- **R6** (advisory WARN; ERROR under `--strict`) the READER PROMISE clause split jointly covers the whole
  promise. Override: `<!-- override: reader-contract-coverage — <rationale> -->` (the `override_marker` SSoT).
- **R7** map integrity (the untrusted-input firewall): closed-key schema, `inputs.*_sha256` bound to the
  staged artifacts (a stale Map fails loudly), every `clause_text` a verbatim substring of its Contract
  field, the clause denominator recomputed from the Contract — never trusted from the Map.

## Scope

Fiction (the full 10-field contract schema) and narrative nonfiction (the optional `CENTRAL QUESTION` /
`PROMISE TYPE` block, which drives the deliverable's single idea clause in place of `CONTROLLING IDEA`).
Argument-shaped nonfiction is deferred to a separate argument-spine analog — flag, don't build.

Canonical worked examples (fiction + narrative nonfiction) live under
`references/example-reader-contract-outline/`.
