# Native Python validator migration

**Status:** Groups 1–4, 5a and 6–12 built; self-test output stabilized. The gate pair
and groups 13–14 remain queued. The Bash dispatcher remains the
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
shared Bash gate default now would regress those existing calls. Groups 10–13
follow Group 9; full aggregate dispatch and gate migration stay
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

Group 9 adds ten lifecycle, reader and manuscript routes. Original arguments go
to unchanged helpers after raw wrapper arity checks; `roundtrip-disposition`
uses the helper prefix `disposition`. Reanchor admits one raw argument, while
roundtrip and position-pair require three before a late self-test can reach the
helper. First-position self-tests retain their wrapper bypass. Direct helper
build/render/emit/crossref modes remain direct-only: mode-like wrapper tokens are
paths and do not enable writes. Discovery, optional reads, strictness, citation
containment and recorded-disposition checks remain helper-owned.

The only Group 9 helper edit captures two expected positive render calls inside
the viz self-test. Each named check still verifies return 0 and now also requires
the exact complete success stdout, including its actual output path and newline.
Only those two random-path stdout emissions are hidden. The negative render's
stable stderr, named rows, suite accounting, successful cleanup and ordinary
renderer output/artifacts remain unchanged; exceptions propagate with stdout
restored, without a new guarantee of directory cleanup on arbitrary exceptions.

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
the independent Bash dispatcher without output normalization. All 64 migrated
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
specificity/refutation helper stabilization and the narrow viz self-test capture.
Their intentional self-test-only output changes remove the two specificity fixture
diagnostic lines, the one shared refutation fixture diagnostic line and two
positive viz render output-path lines; no pre-stabilization self-test
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

Group 9 adds ten exact self-test surfaces, canonical default/strict behavior and
both explicit outline projects, including expected strict reanchor refusal.
Compact controls preserve raw wrapper minima/prefixes, distinct resolver roles,
optional/read/no-op behavior, strictness, direct-only producer modes and no-write
validation. Viz capture controls exercise real temporary roots with colon/PASS,
Unicode and newline spellings, per-site bad status/output and propagated
exceptions. Independent pre-edit ordinary render/refusal receipts compare raw
outputs and resulting artifact bytes/modes; two known full render emissions are
the only intentional self-test output delta. The stable nonempty viz/outline
self-test stderr remains compared exactly. Outline unknown-input/clause-key
ordering is inherited: raw differential controls pair the same seeds 1, 2 and 3
without sorting output or setting a production seed. Recorded confirmation checks
prove consistency of records, not independent human confirmation.

Group 10 adds seven argument evaluator routes. Each forwards the original raw
arguments to its existing helper after the Bash wrapper's minimum-arity and
first-position self-test rules; AIF export/check use distinct `export`/`check`
prefixes. GT repair/round modes, alpha options, crosswalk defaults, AGD optional
paths and AIF schema/loss rules remain helper-owned. AIF export is a public
producer: temporary output comparisons cover streams, complete artifact bytes,
directory membership and modes from identical starting states, including
overwrite and no-write refusals. Source closure is checked separately from
sourceless canonical shape. The global Bash `--internal-links*` scanner still
takes precedence over some route arguments; the native CLI does not emulate that
global scanner. Route-arm parity excludes those scanner-control invocations,
which remain part of the coordinated Group 14 cutover.

Group 11 adds the argument reconstruction validation and draft publication
routes. Both send zero-argument calls and ordinary raw arguments directly to
their unchanged helpers, without a command prefix. A first raw `--self-test`
sends only that flag. A missing or nonregular shipped helper retains its route's
hard rc1 error; a symlink to a regular helper remains available. Approval's
stage/append parser and draft's argparse packet/emit parser retain their
distinct outputs and errors. Real packet, append, projection and draft/receipt
effects remain helper-owned; a published draft retains `ACTION-REQUIRED` and
unavailable semantic-comparator markers. The inherited Bash scanner can still
reject `--internal-links*` before either arm, so Group 11 route-arm forwarding,
first-self-test and missing-helper parity exclude those scanner-control calls.
Group 14 owns the scanner's global reach and aggregate cutover.

Group 12 adds native `obsidian-export`, `html-export`, `docx-export`, and
`pdf-export` validators. Each sends its own command name and all original raw
arguments to the existing annotation export helper. First-position self-tests
send only `--self-test`; PDF then runs the actual repository navigation suite
when the repository marker is present. A nonzero helper or suite result remains
nonzero. The direct helper's `obsidian`, `html`, `docx`, and `pdf` verbs remain
producers; these four public routes check on-disk exports and do not create them.
The four routes reproduce the Bash wrapper's `--internal-links*` scan before
self-test or shortage handling. Earlier native routes still lack the global
scanner reach, which Group 14 must resolve with complete dispatch tests.

PDF first-self-test compares exact exit status and stdout. Its repository
navigation suite writes unittest progress and results to stderr; only the
elapsed decimal in `Ran N tests in <elapsed>s` varies between real executions.
Normal-PATH parity checks all remaining stderr bytes, count and result. An
empty-PATH native run executes the same suite but skips its two Bash-dependent
cases on the current POSIX host; that is partial coverage, not a no-skip result.
Default exports use the helper's existing independent newest-file discovery;
linked PDF keeps its separate normal-run authentication and reports that reader
behavior is unqualified. The aggregate gate, complete historical scanner reach,
native Windows acceptance and cutover remain Group 14 work.

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
| 9 | lifecycle-node, reader-instrument, manuscript-viz, annotated-manuscript, crosslink, reanchor, roundtrip-disposition, reader-contract-outline, results-guide, position-pair-register | Built |
| 10 | argument-groundtruth-check, fiction-groundtruth-check, agreement-alpha, argument-crosswalk-check, argument-agd, argument-aif-export, argument-aif-check | Built |
| 11 | argument-reconstruction, argument-reconstruction-draft | Built |
| 12 | obsidian-export, html-export, docx-export, pdf-export | Built |
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
