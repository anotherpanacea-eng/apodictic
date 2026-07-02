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
corrected here), and `specificity_floor._read` (added by PR #163 after this sweep's branch was cut,
so the class sweep couldn't see it; its letter/ledger CLI reader was OSError-only — a non-UTF8
letter/ledger via `validate.sh specificity-floor` raw-tracebacked — and is folded in on the
main-merge here). Each now catches `(OSError, UnicodeDecodeError)`. The advisory readers degrade to
their existing unreadable-artifact path (skip / `None` / `[]` / error-line) instead of a traceback.
**`specificity_floor` is the exception: it is a BLOCKING gate, so it FAILS CLOSED.** Its `_read`
still returns `None` on a read/decode failure, but `main()` no longer collapses that `None` to `""`
— an unreadable letter or ledger now prints a named `Error:` and exits 2 (mirroring
`refutation_check._read_file`'s `(None, msg) -> Error -> exit-2` shape), rather than degrading an
unreadable letter to a vacuous "0 delivered / PASS" and an unreadable ledger to "no findings —
nothing to hold" — either of which silently bypassed the count/anchor floor with a real ledger
(Codex #164 P2, a fail-OPEN on a blocking gate). A legitimately-empty-but-readable artifact still
reads as `""` (not `None`) and runs unchanged. One non-UTF8 self-test case added per touched
validator, plus — for specificity_floor — fail-CLOSED pins on both the letter-read and ledger-read
failure paths and a readable-empty-stays-green regression pin. Already safe and untouched: the
previously guarded readers (`annotation_export`, `editor_scaffolding`, `reanchor`,
`regression_diff`), the `errors="replace"` family
(`config_checks`, `timeline_checks`, `letter_checks`, `meta_lint`, `argument_groundtruth`), the
`except (OSError, ValueError)` sites in `run_gate.py` (ValueError covers UnicodeDecodeError), and
the repo-internal fail-loud readers (`run_gate._load_manifest`, `apodictic_artifacts` schema
loads, `sync_setec`), which never see user-supplied artifact paths.
