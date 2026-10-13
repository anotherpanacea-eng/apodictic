# Native Python validator migration

**Status:** Groups 1–4, 5a and 6–8 built; self-test output stabilized. The gate pair
and groups 9–14 remain queued. The Bash dispatcher remains the
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

Group 4 adds `structured-findings`, `softness-check`, `deficit-lock`,
`artifacts-schema`, `finding-trace`, `feedback-triage`, `editor-scaffolding` and
`diagnostic-vocabulary`. Structured-findings forwards raw file arguments without
a command prefix or wrapper arity check, including its existing helper help and
read-error output. Softness/deficit retain their shared honesty self-test suite,
wrapper arities and positional file reads. Artifacts-schema accepts only
first-position `--self-test`; other input remains a usage refusal.

The other four helpers retain their own late-self-test, strict, mode and path
filtering. Their run-folder discovery, parsed-block classification, newest-file
selection, sidecar ascent and optional ledger behavior stay in the existing
helpers. Editor dual mode keeps precedence over per-pass mode and their exact
path arities. The dispatcher adds no file probes or second input resolver.

Group 5a adds `escalation-check`, `dispatch-record`, `disposition-check`,
`synthesis-coverage` and `specificity-floor`. Original tagged arguments go to the
existing helpers after the Bash wrapper's raw minimum-argument check. First-position
`--self-test` forwards only that flag; the helpers retain late self-test handling,
flag filtering, discovery, defaults and strict behavior. Dispatch report mode
selects its path before normal strict/flag filtering, preserving argument order.
Synthesis requires exactly one directory and specificity exactly two regular files.
Specificity's named unreadable/non-UTF-8 errors remain blocking usage failures.

`gate` and `gate-state` remain unported. Their shared helper still launches Bash
for child checks and its shared self-test. The gate manifest has 18 unique child
validators; 15 are native after 5a and Group 6 supplies the final three refutation
routes. The launcher transition remains held for the coordinated Group 14
cutover under a fresh scope and independent review.

Group 6 adds `retcon-plan`, `state-card-diff`, `revision-arc`, `regression-diff`,
`refutation-coverage`, `refutation-evidence` and `refutation-write-scope`.
Planning/diff helpers retain late-self-test and strict/flag filtering, parsed
artifact classification, newest-file discovery, prior/current ordering and
optional ledger/marker sources. The three refutation routes retain distinct
positional dispatch. Only evidence mode removes `--require-snapshot`; it keeps
explicit versus implicit snapshot selection, contained read-only paths, raw-byte
hashes, run-shape requirements and voided-demotion behavior in the existing helper.
No generic wrapper flag parser or filesystem preflight is added.

All 18 official gate child validators now have native routes. Both gate surfaces
still require the separate launcher transition; child availability alone does
not make them native. Custom manifests can reach other commands such as
`schema-coverage` and aggregate switches that remain unported. Changing the
shared Bash gate default now would regress those existing calls. Groups 9–13
follow Group 8; full aggregate dispatch and gate migration stay
coordinated in Group 14 unless a separate reviewed design preserves all behavior.

Group 7 adds `legal-risk`, `promise-contract`, `continuity-bible`, `setup-payoff`,
`world-bible`, `argument-spine` and `scene-ethics`. The wrapper preserves first
self-test trimming, raw minimum arity and command-tagged original arguments.
Helpers retain late self-tests, exact command-token filtering, strict/override
behavior, parsed-carrier classification and newest-file discovery. Promise selects
the newest pitch while consuming all sorted Markdown reports; mixed unreadable
inputs retain its partial-read behavior and wholly unreadable inputs retain its
generic refusal. Continuity preserves the first recognized timeline and local
`Timeline.md` before parent lookup, including missing/unreadable coverage limits.

Group 8 adds `intake-interview`, `author-fingerprint`, `content-advisory`,
`coaching-history`, `style-explanation` and `persona-divergence`. Unchanged helpers
own consent, parsed-carrier selection, newest files, optional ledger/timeline
reads, strictness and overrides. Persona discovers only a local Timeline; style
prefers parsed style labels over a newer fingerprint-only file. Coaching retains
recursive whole-project checks and its root-local sidecar.

First-position `coaching-history delete` forwards exactly `delete` and the second
raw argument, dropping all later tokens. A retained `--self-test` still invokes
the helper suite. A missing second token preserves Bash's exit 1 and empty stdout,
but emits `Error: coaching-history delete requires <project_root>` on stderr;
the native CLI does not reproduce Bash's sourced-file path/line diagnostic.
Ordinary coaching calls retain original arguments, including command tokens the
helper later removes. Deletion can remove histories before refusing a malformed
sidecar; the existing helper does not promise atomic rollback.

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
the independent Bash dispatcher without output normalization. All 54 migrated
self-test surfaces now compare exact stdout bytes, including specificity and
the three shared refutation routes. Their self-tests formerly printed random
temporary paths while exercising expected negative CLI reads. The separate
stabilizer captures only those three internal calls, asserts exit 2 and the
complete named role/path boundary and read/decode reason, and rejects false PASS
output. Reason, line-count and PASS checks inspect only the payload after the
complete expected role/path and delimiter, preserving valid temporary roots
containing PASS, BYPASS or newlines. The named fail-closed checks and complete
suites still run. Ordinary
commands, including their named decode errors, retain byte-identical output.
Application-generated
stderr bytes are compared exactly except for the accepted logical/physical cwd
prefix limitation noted below. Coaching’s shell-fatal missing-delete-target
case preserves exit/stdout with the named native stderr described above.
For shell/OS-generated read-redirection
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
The final independent pre-cutover Bash reference includes the separately reviewed
specificity/refutation helper stabilization. Its intentional self-test-only
output change removes the two specificity fixture diagnostic lines and the one
shared refutation fixture diagnostic line; no pre-stabilization self-test
byte-equivalence claim is made. Output from readable-empty and other checks,
ordinary helper dispatch and unrelated exception propagation remain unchanged.
The shared refutation suite retains an unrelated synthetic-JSON failure when a
temporary-root path contains a newline; its negative read checks still pass.

Group 3 adds eight self-test routes, all 15 applicable shipped timeline fixtures,
canonical config/timeline inputs and temporary strict/default/optional-file and
two-timeline cases. The accepted Group 2 P3 remains bounded: relative invocation
from a symlinked cwd can show a physical cwd prefix in an empty-registry stderr
diagnostic where Bash shows the logical prefix. File selection, exit code and
stdout match. The dispatcher does not emulate shell `PWD` behavior.

Group 4 exercises eight added self-test surfaces and the seven remaining `sf.*`
fixtures, including both JSON files, so all 73 validator fixture files now have
migrated command coverage. Additional controls cover canonical structured and
operator-mode inputs, raw/mixed file errors, schema refusal, helper-owned late
self-tests, editor mode arity/precedence, latest-file selection and sidecar ascent.
Native aggregate coverage and full-suite Windows acceptance remain queued.

Group 5a adds five helper self-test surfaces, canonical run folders and the
re-grounded letter/ledger pair, advisory/strict controls, model-tag source
precedence and parse refusal, report flag ordering, malformed sidecars, exact
path arities and named UTF-8 read errors. Both deferred gate routes have explicit
partial-migration refusal checks. All earlier native tests and 73 fixtures remain.

Group 6 adds seven helper self-test surfaces, canonical plans/cards/arc, single
and paired regression rounds, canonical refutation inputs and temporary hostile
records. Controls cover planning discovery, parsed carriers, ledger precedence,
advisory/strict behavior, positional refutation flags, optional/required snapshots,
containment and named decode errors. Its 41 migrated command self-test surfaces
compare exact stdout bytes after the separate helper stabilizer.
All 73 earlier validator fixture cases remain intact.

Group 7 adds seven exact self-test surfaces and ten canonical strict cases. Compact
controls cover raw argv/filtered-token differences, literal command filenames,
read refusals, first parsed carrier/newest file, Promise report scope, Continuity
timeline order/fallback and an advisory/strict/scoped-override transition. All
earlier native cases, including the stabilizer's temp-root regressions, remain.

Group 8 adds six exact self-test surfaces, six canonical strict inputs and compact
raw-token, discovery, optional-role, read, strict and override controls. Synthetic
temporary coaching trees are restored to identical paths/bytes/modes before each
Bash/native deletion; comparisons include output and resulting file membership,
bytes and modes, recursive sequence removal, tombstones, H6 residue recomputation,
idempotence and partial failure. Canonical inputs are never deleted. Coaching's
bare-token warnings inherit unsorted set iteration: raw differential comparisons
use the same recorded `PYTHONHASHSEED` (1, 2 and 3) for each pair. Output is not
sorted or normalized, production does not set a seed, and ordinary unseeded
output determinism is not claimed. Fingerprint W2/style X6 remain nonblocking
under strict while coaching URL W1 remains blocking.

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
| 4 | structured-findings, softness-check, deficit-lock, artifacts-schema, finding-trace, feedback-triage, editor-scaffolding, diagnostic-vocabulary | Built |
| 5a | escalation-check, dispatch-record, disposition-check, synthesis-coverage, specificity-floor | Built |
| 5b | gate, gate-state; coherent live/shared-self-test nested launcher transition | Held for coordinated Group 14; official children available, custom/aggregate dispatch still incomplete |
| 6 | retcon-plan, state-card-diff, revision-arc, regression-diff, refutation-coverage, refutation-evidence, refutation-write-scope | Built |
| Self-test stability | Specificity/refutation expected-negative diagnostic capture and four restored exact-output surfaces | Built |
| 7 | legal-risk, promise-contract, continuity-bible, setup-payoff, world-bible, argument-spine, scene-ethics | Built |
| 8 | intake-interview, author-fingerprint, content-advisory, coaching-history, style-explanation, persona-divergence | Built |
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
