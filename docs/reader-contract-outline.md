# Reader-Contract Reverse Outline — design & gate reference

The third finalized third-party developmental-edit deliverable. Design of record: SPEC v3.1 (the Fable
re-spec; 6-lens `/spec-review` verdict BUILD-READY-WITH-FIXES). This doc records the Firewall
reconciliation, the artifact/schema shapes, and the R1–R7 gate contract. Author-facing overview:
`plugins/apodictic/skills/core-editor/references/reader-contract-outline.md`.

## Why this survives the Firewall

APODICTIC's red line: **the model never authors manuscript prose or invents interpretation in a
deliverable.** The two prior deliverables honor it differently — the Annotated Manuscript is *pure
mechanical projection* (its finding→anchor localization pre-exists in the Ledger), the Letter is
*authored synthesis under discipline*. The reverse outline needs one piece of judgment that exists
nowhere else: **which scenes establish and pay off each contract promise.** No deterministic script can
semantically match a prose promise clause to the scenes that carry it, and that localization lives in no
current artifact.

The resolution (SPEC D5): house that judgment in a model-authored, closed-key, mechanically gated
**Contract Map block** (`apodictic.contract_map.v1`) — the established house pattern (persona-divergence
`apodictic.persona.v1`, the setup-payoff ledger, canon facts): the model authors structured, ids-only
data → a validator gates it → the renderer projects it. The Map is authored **at offer time** from
artifacts already in the run folder, carries **no free-prose field**, and is gated (R7) before the
projector will consume it. Deliverable assembly stays byte-deterministic. Rendered cells carry the cited
scene's Pass 0 "what the reader now knows" line **verbatim** as displayed evidence, so a wrong
localization is *visible evidence*, never a trusted assertion.

## Artifacts

### Contract Map — `[Project]_Contract_Map_[runlabel].md`

One fenced `apodictic.contract_map.v1` block (+ a one-line human note that the file is machine-read
plumbing). Closed-key schema:

```
{
  "schema": "apodictic.contract_map.v1",
  "inputs": {"pass0_sha256": "…", "contract_sha256": "…", "ledger_sha256": "…"},
  "clauses": [
    {
      "clause_id": "C1",
      "source_field": "READER PROMISE",          // a field present in the Contract schema block
      "clause_text": "<verbatim substring of that field's value>",
      "established": ["S3", "S5"],                // Pass 0 scene ids, or []
      "paid_off": ["S41"],                        // Pass 0 scene ids, or []
      "not_localizable": false,                   // true ⇒ established/paid_off MUST be []
      "gap_finding_id": "F-PCF-02"                // or null (renders as the literal `none logged`)
    }
  ]
}
```

**clause_id assignment (mechanical, R7-checked):** ids are `C1..Cn`, assigned in order of appearance in
the Contract schema block — `READER PROMISE` clause rows first (in the order their `clause_text`
substrings occur in the field), then exactly one row for `CONTROLLING IDEA` (or `CENTRAL QUESTION` for
narrative nf), then one row per `NON-NEGOTIABLES` list item (in list order).

**Denominator recompute (what a validator can and can't count):** R7 enforces the field-level *floors*
from the **Contract artifact**, never the Map — ≥1 row for `READER PROMISE`, exactly 1 for the idea
field, exactly 1 per enumerable `NON-NEGOTIABLES` item. The *splitting* of `READER PROMISE` prose into
multiple clauses is model judgment, bounded mechanically by the verbatim-substring rule and non-overlap;
whether the split jointly covers the whole promise is **R6's advisory question (WARN)**, never R7's — a
validator cannot semantically segment prose.

### Outline — `[Project]_Reader_Contract_Outline_[runlabel].md`

Fixed section order: (1) header (project · runlabel · one-line framing, a code constant); (2) The Reader
Contract — verbatim projection of every Contract schema-block field, empty fields as their literal state;
(3) Scene Spine — one entry per Pass 0 scene (`id · what happens · what the reader now knows`, verbatim);
(4) Contract Map — one block per clause, `established`/`paid off` at scene ids each followed by that
scene's Pass 0 evidence line verbatim, `not localizable to a scene` when declared, and the gap cell;
(5) Coverage note (advisory; R6). The connective boilerplate is a **code constant** in
`scripts/reader_contract_outline.py` (the `annotation_export.py` precedent), never a resource file.

## Gates (R1–R7)

| Gate | Name | Check |
|------|------|-------|
| **R1** | spine projection integrity | §Scene Spine round-trips to Pass 0 — ids + count + text verbatim. |
| **R2** | contract fidelity | Two-sided: every Contract schema-block field is projected into §2; no §2 field is absent from the artifact. Empty fields render `—`, never reworded. |
| **R3** | anchor + map round-trip | Every scene id in the rendered map resolves in Pass 0; the rendered map ↔ Map block is a bijection; every rendered evidence line byte-matches the cited scene's Pass 0 line. |
| **R4** | no fabricated gap | Every gap cell is `none logged` or a verbatim projection of the Ledger entry whose `finding_id` the Map names. `none logged` is a valid, non-degraded state. |
| **R5** | author-facing language | No untranslated framework shorthand in the rendered outline (the letter's author-facing-lint families, applied to a projection). |
| **R6** | contract coverage (advisory WARN; ERROR `--strict`) | The READER PROMISE clause split jointly covers the whole promise. **WARN marks absence only** — a present-but-wrong entry is R7's ERROR. Override: `<!-- override: reader-contract-coverage — <rationale> -->` via the `override_marker.py` SSoT (no bare scan — M5/M6). |
| **R7** | map integrity (Mode-11: untrusted input) | Closed-key `apodictic.contract_map.v1` (unknown key = ERROR); `inputs.*_sha256` match the staged artifacts (a stale Map fails loudly); every `clause_text` a verbatim substring of its named `source_field`; every `source_field` present in the Contract; `not_localizable` ⇒ empty scene lists; every scene id resolves in Pass 0; every `gap_finding_id` resolves in the Ledger; the clause denominator recomputed from the Contract, never trusted. |

**Validator architecture:** one `AGG_VALIDATORS` entry, `reader-contract-outline`, whose single arm runs
R1–R7 (the `annotated-manuscript` A1–A6 precedent). Dual-script mirror (`scripts/` ↔
`plugins/apodictic/scripts/`, byte-identical, in the `check-mirror` set). `--self-test` +
`--self-test-all`; `--check-all` builds a fresh outline from the committed fixture inputs and asserts it
is **byte-identical** to the committed outline, then runs the four hostile arms in-place. Absent
`python3`: advisory WARN-skip + inline-check guidance, never a bash reimplementation (the no-second-parser
rule). Exit codes 0/1/2.

## Delivery & regeneration

Offered at run-end (sibling to the Annotated Manuscript, `run-synthesis.md §Reader-Contract Reverse
Outline`), gated on a `*_DE_Synthesis_*` letter + `*_Pass0_Reverse_Outline_*` + `*_Contract_*` all
present (absent any one → the offer is silently not surfaced; an explicit regeneration request with a
missing input → fail loud). Regenerable from `/start`'s `diagnosed` node (`commands/start.md §Step 0.5`),
condition = the letter-present-and-inputs-present-and-no-`*_Reader_Contract_Outline_*` glob (never a
`next_action` value). **Map state at regeneration:** present + hashes match → reuse frozen; absent →
re-author + re-gate; present but stale → fail loud (name the drifted input, stop).

## Scope

v1 = fiction + narrative nonfiction. Fiction uses the full 10-field contract schema; narrative nonfiction
adds the optional `CENTRAL QUESTION` / `PROMISE TYPE` block, whose `CENTRAL QUESTION` drives the single
idea clause in place of `CONTROLLING IDEA`. Argument-shaped nonfiction is deferred (a separate
argument-spine analog).
