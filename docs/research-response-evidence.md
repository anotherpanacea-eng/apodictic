# Research response evidence

**Status:** Built.
<!-- built-when: plugins/apodictic/skills/research-verification/scripts/provenance.py contains "def save_responses" -->

The Citation Verifier reference asks that every API response used in resolution be stored as JSON, and that an "unretrievable" verdict trace to what each tier actually returned. `ProvenanceStore` summaries alone cannot reproduce those responses, so this adds an opt-in record.

## Use

- `ProvenanceStore(record_responses=True)` keeps a deep copy of each parsed response `resolve_citation` reads. Default is off, and nothing else about the store changes.
- `resolve_batch(citations, ..., response_evidence_path=PATH)` turns it on for a batch and writes the file after resolution.
- `academic_apis.py batch --input IN --output OUT --response-evidence PATH` does the same from the command line.

## File

```json
{"responses": [
  {"ref_id": "r1", "source": "semantic-scholar", "outcome": "no-match",
   "prov_ref": null, "recorded_at": "2026-10-24T14:00:00Z", "response": {"data": []}}
]}
```

`outcome` is `used` (accepted metadata, enrichment or a live URL/snapshot), `no-match` (a valid answer with no accepted candidate) or `not-checked` (a budget or circuit skip, a request failure, or a malformed answer). `prov_ref` links to a legacy provenance entry when one exists, regardless of outcome. A malformed cached Wayback answer is recorded before its replacement request. Tiers the resolver never reached have no entry.

## Limits

- `response` is the parsed JSON (or the resolver's local `_error`/`_skipped` sentinel), not the HTTP body. A cache hit records the cached value, whose original fetch time is unknown.
- The file is written once, to the caller's path, with no atomic replace and no check that it differs from the other outputs.
- Standalone helpers (`check-url`, `retraction-check`, direct provider calls) are not covered.
