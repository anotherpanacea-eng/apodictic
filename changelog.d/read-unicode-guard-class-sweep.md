### Non-UTF8 artifacts degrade instead of crashing (repo-wide reader class sweep)

PR #162's build review found `disposition_check.py`'s `_read()` crashed with a raw
UnicodeDecodeError traceback on a non-UTF8 artifact — and the idiom is a class, not an instance.
Swept every OSError-only artifact reader in `scripts/`: the shared `_read()` helper in 25
validators (annotation-manifest through world-bible/viz-manifest, incl. the `Path.read_text`
variant in `schema_coverage.py`), both CLI read sites in `honesty_check.py`,
`structured_findings.validate_file`, two `run_gate.py` sites (`_ledger_finding_ids` and the
disposition-marker sources loop), `lifecycle_node._read_json` (whose
`(OSError, JSONDecodeError)` did NOT cover UnicodeDecodeError — it subclasses ValueError, not
JSONDecodeError), `refutation_check._read_file` (the shared letter/ledger/record CLI reader — the
Codex #164 P2 miss; its `_read_bytes` sibling is binary and cannot decode-fault), and
`disposition_check._read` itself (the module that ORIGINATED the class in PR #162 was left
OSError-only — the earlier note that it was "already guarded on PR #162" was incorrect and is
corrected here). Each now catches `(OSError, UnicodeDecodeError)` and degrades to its existing
unreadable-artifact path (skip / `None` / `[]` / error-line) instead of a traceback. One non-UTF8
self-test case added per touched validator (32 new cases). Already safe and untouched: the
previously guarded readers (`annotation_export`, `editor_scaffolding`, `reanchor`,
`regression_diff`), the `errors="replace"` family
(`config_checks`, `timeline_checks`, `letter_checks`, `meta_lint`, `argument_groundtruth`), the
`except (OSError, ValueError)` sites in `run_gate.py` (ValueError covers UnicodeDecodeError), and
the repo-internal fail-loud readers (`run_gate._load_manifest`, `apodictic_artifacts` schema
loads, `sync_setec`), which never see user-supplied artifact paths.
