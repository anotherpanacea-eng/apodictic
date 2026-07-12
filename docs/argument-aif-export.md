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
With `--source`, the checker rebuilds the graph and loss ledger and requires byte
identity.

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
