# Native Python validator migration

**Status:** Group14 native cutover built as an unarmed draft. Local combined
qualification and independent review are required; final CB-1(a) acceptance
requires a green hosted `validate-windows` CI job (the full `--check-all` gate with
only Python on `PATH`). Earlier increment records below describe the migration
history.
<!-- built-when: plugins/apodictic/scripts/validate.py -->
<!-- built-when: plugins/apodictic/scripts/validate_canonical.py -->

The native entrypoint is `python plugins/apodictic/scripts/validate.py`. Python
3.10+ is required; CI pins 3.12. All public routes, including gate/gate-state and
`--self-test-all`, `--check-canonical`, and `--check-all`, use the active interpreter.
The immutable aggregate tuple is the inventory source. Gate-state accounts for
the actual gate suite once; full checks still run canonical checks after aggregate
failures. `validate.sh` remains an optional small POSIX launcher and returns 127
when Python is missing. There is no missing-runtime degraded PASS. Usage messages
name the `validate.py` script Python is running, including through the
`validate.sh` shims.

`validate.py` keeps one `ROUTES` table (command → handler, primary helper script)
and `main()` dispatches through it. Importing `validate.py` has no side effects, so
the runner inventory reads `AGG_VALIDATORS` and schema-coverage C4 reads each
route's helper from the module itself; C5 reads the `run_validator` calls in
`validate_canonical.py`. A misrouted helper fails `--check-all`: through its
self-test in `--self-test-all`, or, when the self-test does not reach the helper
(for example `dispatch-record` routed to `escalation_check.py`), through the
canonical checks in `--check-canonical`.

Both package generators exclude `__pycache__` and bytecode, including submission
archives, and require the native files and the compatibility shim in each archive.
They also check the canonical plugin source against the Claude plugin directory
limits (512 files, each under 256 KiB) before building. Standalone installs preserve the existing explicit skips:
missing eval-only export goldens can skip byte comparison, while required
stance/E7 inputs still fail. A standalone layout is not a claim that every full
canonical check passes without those inputs.

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

The only Group 9 helper edit captures the viz self-test's two positive render
calls so their random output paths no longer reach self-test stdout.

Exit codes remain 0 for success, 1 for a validation failure, and 2 for usage or an
invalid/inaccessible input path. For the three raw-byte utilities, a regular file
that is found but cannot be read returns 1 with empty stdout and a named
application error on stderr. The parser-backed commands retain their helper's
failure behavior.
Migrated-command usage errors deliberately retained the sibling
`validate.sh` name, including its invocation path, until Group 14 made them name
`validate.py`. General
Python help identifies the partial migration. Unported commands, including
`--self-test-all`, `--check-canonical` and `--check-all`, return 2 with an explicit
partial-migration message. Python does not fall back to Bash.

Group 10 adds seven argument evaluator routes. Each forwards the original raw
arguments to its existing helper after the Bash wrapper's minimum-arity and
first-position self-test rules; AIF export/check use distinct `export`/`check`
prefixes. GT repair/round modes, alpha options, crosswalk defaults, AGD optional
paths and AIF schema/loss rules remain helper-owned.

Group 11 adds the argument reconstruction validation and draft publication
routes. Both send zero-argument calls and ordinary raw arguments directly to
their unchanged helpers, without a command prefix. A first raw `--self-test`
sends only that flag. A missing or nonregular shipped helper retains its route's
hard rc1 error; a symlink to a regular helper remains available. Approval's
stage/append parser and draft's argparse packet/emit parser retain their
distinct outputs and errors. Real packet, append, projection and draft/receipt
effects remain helper-owned; a published draft retains `ACTION-REQUIRED` and
unavailable semantic-comparator markers.

Group 12 adds native `obsidian-export`, `html-export`, `docx-export`, and
`pdf-export` validators. Each sends its own command name and all original raw
arguments to the existing annotation export helper. First-position self-tests
send only `--self-test`; PDF then runs the actual repository navigation suite
when the repository marker is present. A nonzero helper or suite result remains
nonzero. The direct helper's `obsidian`, `html`, `docx`, and `pdf` verbs remain
producers; these four public routes check on-disk exports and do not create them.
Linked PDF keeps its separate normal-run authentication and reports that reader
behavior is unqualified.

The four annotation export routes first apply the `--internal-links*` refusal:
only `pdf-export <run_folder> --internal-links` (exactly once, no other `--`
option) passes; anything else exits 2 with the usage message, before self-test or
shortage handling. Under Bash every route in `commands-b.sh` applied this check
because of how the dispatcher files were split; after the Group 14 cutover only
the exporters do, matching the navigation spec's rule that the exporter option
does not set other utilities' option policy.

Group 13 adds `registry-check`, `schema-coverage`, `validator-conventions`,
`calibration-honesty`, `stance-calibration` and
`argument-carve-behavior-preservation`. The five helper routes preserve their
exact command prefixes, original ordinary tokens and distinct raw arities.
First-position selftests forward only that flag; helper-owned late selftests
retain wrapper arity checks.

Under Bash, the conventions first-selftest also ran twelve override-marker cases
through `override_marker.py --has-override` to cover the Bash `_has_override`
helper. Group 14 removed that companion and the stdin CLI it used; the same cases
run in-process in `override_marker.py --self-test`. At Group 13, meta-lint and
schema coverage still inspected the Bash dispatcher/parts; Group 14 moved them to
the native route table and `validate_canonical.py`.

Carve remains a repository-only summary smoke. It selects the first of the two
existing lexical fixture directories, skips when neither exists, and preserves
ordinary first-missing versus selftest all-missing reporting. It executes the
actual native propagation and decision children, serially capturing each child,
reading its golden, then comparing. A nonzero child immediately returns that
status with child streams captured/suppressed and only prior outer rows retained.
An unavailable golden read stops at that phase with rc1 and a named native read
error; only the shell/OS-generated `cat` stderr wording differs. Comparison drift
permits the next pair, but a later execution/read failure prevents the final row.
Successful comparisons retain LF-tail selection before NUL removal and
trailing-LF-only substitution, preserving CR, spaces, embedded LF and non-UTF-8
golden diagnostic bytes. Fixture paths are built from the logical script
directory, as in Bash. The smoke does not establish field-level or editorial
behavior preservation.

## Differential acceptance

During Groups 1 to 14 a differential suite compared native exit codes, stdout and
stderr bytes against the Bash dispatcher, optionally against an external
pre-cutover checkout. With the Bash dispatcher deleted it could only compare
Python with Python, so it was removed after the cutover. The behavior it guarded
that no other gate covers stays in `tests/test_validate_native_aggregates.py`,
which CI runs: the dispatcher keeps a helper's exit status, stdout and stderr
bytes, argv and stdin with an empty `PATH`; a missing helper never yields a
self-test PASS; and the carve smoke fails when a child fails or a golden drifts.
Native Windows acceptance is the `validate-windows` job, which runs the whole
`--check-all` gate with only Python on `PATH`.

```text
python -m pytest -q tests/test_validate_native_aggregates.py tests/test_contract_hash_portability.py
bash scripts/validate.sh --check-all
node scripts/assemble-changelog.mjs --check
git diff --check
```

## Windows helper text output

The native dispatcher relays shipped helper text streams with LF line endings on
Windows, including errors and nonzero helper results. Arguments, stdin and helper
file effects are preserved; canonical JSON packet output is unchanged. POSIX
hosts retain direct stream inheritance. Windows collects each helper's stdout and
stderr before relaying them, so live streaming and cross-stream interleaving are
not preserved and memory use includes both captured streams. This is a textual
CLI boundary, not an arbitrary binary-output transport. Nested helpers' own output
handling and the queued native aggregate migration remain separate.

## Divergences and known limitations

- Shell/OS-generated read errors (for example carve's golden `cat`) keep exit
  and stdout but emit a named native read error instead of shell wording.
- `coaching-history delete` without a target keeps Bash's exit 1 and empty
  stdout but emits `Error: coaching-history delete requires <project_root>`.
- Relative invocation from a symlinked cwd can show a physical cwd prefix in an
  empty-registry stderr diagnostic where Bash shows the logical prefix.
- BSD `wc` pads `state-lines` output under Bash; native output is unpadded.
- Missing native helpers fail as launch errors, never as Bash's advisory skip or
  degraded self-test PASS.
- Specificity, refutation and viz self-tests no longer print random temporary
  paths, so no pre-stabilization self-test byte-equivalence is claimed. The
  shared refutation suite still fails when a temporary root contains a newline.
- Coaching bare-token warnings and outline unknown-key ordering inherit unsorted
  set iteration; output order depends on `PYTHONHASHSEED` in both CLIs.
- The PDF navigation suite's stderr includes a varying elapsed time, and an
  empty-PATH run skips its two Bash-dependent cases.

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
| 5b | gate, gate-state; coherent live/shared-self-test nested launcher transition | Built in Group 14 |
| 6 | retcon-plan, state-card-diff, revision-arc, regression-diff, refutation-coverage, refutation-evidence, refutation-write-scope | Built |
| Self-test stability | Specificity/refutation expected-negative diagnostic capture and four restored exact-output surfaces | Built |
| 7 | legal-risk, promise-contract, continuity-bible, setup-payoff, world-bible, argument-spine, scene-ethics | Built |
| 8 | intake-interview, author-fingerprint, content-advisory, coaching-history, style-explanation, persona-divergence | Built |
| 9 | lifecycle-node, reader-instrument, manuscript-viz, annotated-manuscript, crosslink, reanchor, roundtrip-disposition, reader-contract-outline, results-guide, position-pair-register | Built |
| 10 | argument-groundtruth-check, fiction-groundtruth-check, agreement-alpha, argument-crosswalk-check, argument-agd, argument-aif-export, argument-aif-check | Built |
| 11 | argument-reconstruction, argument-reconstruction-draft | Built |
| 12 | obsidian-export, html-export, docx-export, pdf-export | Built |
| 13 | registry-check, schema-coverage, validator-conventions, calibration-honesty, stance-calibration, argument-carve-behavior-preservation | Built |
| 14 | Native aggregate/canonical workflow, complete usage routing, Bash shim cutover, references, and native Windows full-suite acceptance | Built as a draft; hosted `validate-windows` run pending |

Groups 2–13 preserve wrapper-specific optional/default arguments, strict flags,
repo-only fixture discovery and special self-test routes. Group 14 preserves
canonical hostile checks, export byte comparisons, derived aggregate counts and
the shared gate/gate-state self-test disposition. It migrates the Bash-source
introspection in `meta_lint.py` and `schema_coverage.py` while retaining schema
binding, canonical exercise and hygiene checks. Its differential verification ran
against an external pre-cutover reference checkout, because comparing the Bash
shim to Python itself cannot establish parity.

The M3 JSON-lines runner is CB-1(b), a later workflow outside these port groups.
