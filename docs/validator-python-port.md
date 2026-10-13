# Native Python validator migration

**Status:** Groups 1–3 built; groups 4–14 queued. The Bash dispatcher remains the
full validator entrypoint during this migration.
<!-- built-when: plugins/apodictic/scripts/validate.py -->

Fleet board CB-1(a) ports the validator dispatcher command group by command group.
Group 1 implements seven early utilities:

```text
python plugins/apodictic/scripts/validate.py contract-hash <contract_file>
python plugins/apodictic/scripts/validate.py contract-check <contract_file> <expected_hash>
python plugins/apodictic/scripts/validate.py ledger-check <ledger_file>
python plugins/apodictic/scripts/validate.py artifact-names <output_dir> <project_name> <runlabel>
python plugins/apodictic/scripts/validate.py synthesis-sections <editorial_letter_file>
python plugins/apodictic/scripts/validate.py tone-check <editorial_letter_file>
python plugins/apodictic/scripts/validate.py state-lines <diagnostic_state_file>
```

Each command accepts `--self-test`. Hashing uses raw bytes with SHA-256; line
counting counts LF bytes, including those in CRLF pairs, and excludes an
unterminated final line. These three utilities require only Python's standard
library. The other four call the existing shipped Python parser through the active
interpreter, preserving its output and the Bash wrapper's argument slicing.

Group 2 adds `author-facing-lint`, `severity-floor`, `audit-signal-propagation`,
`underdiagnosis-triggers`, `ledger-consolidation` and `decision-layer-check` using
the same invocation pattern. These six commands forward their original arguments
to the existing letter parser, which owns file errors and advisory behavior.
`ledger-consolidation` consumes an optional raw ledger when it exists; missing
optional files and further arguments retain the existing parser behavior.
First-position `--self-test` selects the corresponding existing helper suite.

`audit-signal-propagation --check-registry` locates the canonical registry and
dependencies relative to the script. Explicit nonempty registry input requires an
explicit dependencies file; absent/empty registry input defaults both files.
Explicit path spelling, lexical default paths, candidate order and the helper's
argument-propagation fragment discovery are preserved. Extra registry arguments
are ignored as before.

Group 3 adds `quality-risk-triggers`, `cost-floor`, `audit-tier-criterion`,
`pass-header`, `argument-recon-prerequisite`, `timeline-diff`, `timeline-arithmetic`
and `timeline-anchor-conflict`. Existing config and timeline parsers own all
defaults, file errors, optional inputs and ignored extras. Cost-floor retains its
helper's positional filtering and `--strict` behavior. Timeline-diff preserves
the distinct no-argument and one-argument usage messages; other calls forward the
original arguments. Each route supports its existing `--self-test` suite.

Exit codes remain 0 for success, 1 for a validation failure, and 2 for usage or an
invalid/inaccessible input path. For the three raw-byte utilities, a regular file
that is found but cannot be read returns 1 with empty stdout and a named
application error on stderr. The parser-backed commands retain their helper's
failure behavior.
Migrated-command usage errors deliberately retain the sibling
`validate.sh` name, including its invocation path, for compatibility. General
Python help identifies the partial migration. Unported commands, including
`--self-test-all`, `--check-canonical` and `--check-all`, return 2 with an explicit
partial-migration message. Python does not fall back to Bash.

## Differential acceptance

`tests/test_validate_python_parity.py` compares exit codes and stdout bytes against
the independent Bash dispatcher without output normalization. Application-generated
stderr bytes are compared exactly except for the accepted logical/physical cwd
prefix limitation noted below. For shell/OS-generated read-redirection
errors, the native CLI retains the exit/stdout contract and emits a named file-read
error; it does not reproduce shell source paths, line numbers or platform wording. It
exercises every migrated self-test, all applicable shipped validator fixtures,
binary/empty/CRLF/unterminated files, literal project/run labels, Unicode/space/
leading-dash paths, missing arguments and paths, wrong path types, hash drift and
ignored extra arguments, invalid path components, inaccessible parents and
unreadable regular files. Group 2 additionally exercises all six self-tests and
42 shipped fixtures, advisory/override behavior, parser-owned errors, optional
inputs and explicit/default/fragment/empty-registry routes. POSIX permission
regressions require an unprivileged
account and are explicitly skipped when the host can bypass mode restrictions.
Independent native assertions cover the raw-byte utility
contract with an empty `PATH`, including files larger than a read chunk. Native
self-tests, fixture behavior and invalid-input checks also run without Bash.

```text
python -m pytest -q tests/test_validate_python_parity.py tests/test_contract_hash_portability.py
bash scripts/validate.sh --check-all
node scripts/assemble-changelog.mjs --check
git diff --check
```

When Bash is absent, differential-only cases are explicitly skipped. Native
checks still run; this is not full native Windows acceptance. The final acceptance
requires the whole Python `--check-all` suite green on `windows-latest` and exact
differential results over every command self-test and all validator fixtures.

Group 3 adds eight self-test routes, all 15 applicable shipped timeline fixtures,
canonical config/timeline inputs and temporary strict/default/optional-file and
two-timeline cases. The accepted Group 2 P3 remains bounded: relative invocation
from a symlinked cwd can show a physical cwd prefix in an empty-registry stderr
diagnostic where Bash shows the logical prefix. File selection, exit code and
stdout match. The dispatcher does not emulate shell `PWD` behavior.

## Continuation groups

These provisional groups give each subsequent increment its own PR. Refresh the
inventory against current `origin/main` before reserving a group. At the initial
baseline there are 84 aggregate validators and 73 validator fixture files;
`argument-aif-export` is an additional command outside the self-test aggregate.

| Group | Commands or deliverable | State |
| --- | --- | --- |
| 1 | contract-hash, contract-check, ledger-check, artifact-names, synthesis-sections, tone-check, state-lines | Built |
| 2 | author-facing-lint, severity-floor, audit-signal-propagation (including registry route), underdiagnosis-triggers, ledger-consolidation, decision-layer-check | Built |
| 3 | quality-risk-triggers, cost-floor, audit-tier-criterion, pass-header, argument-recon-prerequisite, timeline-diff, timeline-arithmetic, timeline-anchor-conflict | Built |
| 4 | structured-findings, softness-check, deficit-lock, artifacts-schema, finding-trace, feedback-triage, editor-scaffolding, diagnostic-vocabulary | Queued |
| 5 | gate, gate-state, escalation-check, dispatch-record, disposition-check, synthesis-coverage, specificity-floor | Queued |
| 6 | retcon-plan, state-card-diff, revision-arc, regression-diff, refutation-coverage, refutation-evidence, refutation-write-scope | Queued |
| 7 | legal-risk, promise-contract, continuity-bible, setup-payoff, world-bible, argument-spine, scene-ethics | Queued |
| 8 | intake-interview, author-fingerprint, content-advisory, coaching-history, style-explanation, persona-divergence | Queued |
| 9 | lifecycle-node, reader-instrument, manuscript-viz, annotated-manuscript, crosslink, reanchor, roundtrip-disposition, reader-contract-outline, results-guide, position-pair-register | Queued |
| 10 | argument-groundtruth-check, fiction-groundtruth-check, agreement-alpha, argument-crosswalk-check, argument-agd, argument-aif-export, argument-aif-check | Queued |
| 11 | argument-reconstruction, argument-reconstruction-draft | Queued |
| 12 | obsidian-export, html-export, docx-export, pdf-export | Queued |
| 13 | registry-check, schema-coverage, validator-conventions, calibration-honesty, stance-calibration, argument-carve-behavior-preservation | Queued |
| 14 | Native aggregate/canonical workflow, complete usage routing, Bash shim cutover, references, and native Windows full-suite acceptance | Queued |

Groups 2–13 preserve wrapper-specific optional/default arguments, strict flags,
repo-only fixture discovery and special self-test routes. Group 14 preserves
canonical hostile checks, export byte comparisons, derived aggregate counts and
the shared gate/gate-state self-test disposition. It migrates the Bash-source
introspection in `meta_lint.py` and `schema_coverage.py` while retaining schema
binding, canonical exercise and hygiene checks. Final differential verification
must use an external pre-cutover reference checkout; comparing the Bash shim to
Python itself cannot establish parity.

The M3 JSON-lines runner is CB-1(b), a later workflow outside these port groups.
