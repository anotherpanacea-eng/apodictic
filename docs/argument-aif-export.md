# Optional Argument State → AIF-Core export (R4B)

`argument-aif-export` is a deterministic, one-way interoperability projection.
`Argument_State.md` v0.2.0 remains authoritative; exported JSON is never imported
to assign codes, severities, or verdicts.

The graph profile follows the ARG-tech *AIF Specification*, Definition 1.1. A
subclaim is an I-node. Its source-owned `Cn.support` is an I-node feeding one
RA-node whose required `scheme_text` preserves the selected warrant verbatim;
the RA concludes at the claim. The schema declares no claim-ladder incidence, so
none is invented. Typed objections become CA applications only for the four
relations with a licensed conflict target; `ALTERNATIVE` stays an I-node plus an
explicit loss. PA is never inferred from comparison prose.

## Commands

```text
bash scripts/validate.sh argument-aif-export Argument_State.md --state-schema 0.2.0 [--out export.json] [--strict]
bash scripts/validate.sh argument-aif-check export.json [--source Argument_State.md]
```

There is one canonical UTF-8 JSON encoding. Export builds and validates fully in
memory; blocking/strict failure writes no stdout JSON and never replaces `--out`.
Successful file output uses a same-directory temporary file and atomic replace.

Sourceless `check` enforces the full canonical byte-form: the closed schema shape
**and** the canonical JSON encoding, including canonical **key order** (the checker
re-emits the parsed object in the exporter's key order and compares bytes, so a
key-reordered artifact fails without a source). What sourceless `check` cannot
verify is **loss-set completeness** — whether every loss the source *should* have
disclosed is present — because that requires re-deriving the graph and loss ledger
from the original `Argument_State`. With `--source`, the checker rebuilds the graph
and loss ledger, binds the export's recorded `source.artifact` basename to the
supplied source filename, and requires byte identity; that is the only mode that
proves loss-set completeness.

## Loss contract

Each loss has exactly `code`, `source_ref`, `subject_id`, `detail`, and the derived
`blocking` boolean. The closed enum and blocking set live in the schema and
`argument_aif.py`; records sort/deduplicate by `(code, source_ref, subject_id,
detail)`. `UNRESOLVED-TARGET`, `FINAL-SECTION-INCOMPLETE`, and
`SOURCE-ID-COLLISION` are blocking and can never appear in a stored conforming
artifact. Non-blocking losses disclose claim-ladder topology, PA semantics,
untyped/alternative objections, APODICTIC-only metadata, superseded pre-draft
carriers, and partial pre-draft support/warrant gaps.

The adapter-generated metadata never records absolute local paths. Source-authored
claim/support/objection text and RA `scheme_text` remain verbatim, even when that
text itself contains path-like language.
