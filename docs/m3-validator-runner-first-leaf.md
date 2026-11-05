# M3 validator runner: first leaf

**Status:** Built as a source-development runner for eighteen fixed leaves: tone-check, synthesis-sections, severity-floor, decision-layer-check, author-facing-lint, ledger-check, ledger-consolidation, audit-signal-propagation, underdiagnosis-triggers, timeline-arithmetic, timeline-anchor-conflict, calibration-honesty, legal-risk, scene-ethics, fiction-groundtruth-check, deficit-lock, timeline-diff and softness-check. The protocol lifecycle is covered on native Windows and POSIX; signed desktop availability and abrupt Windows coordinator-death containment are not established.
<!-- built-when: plugins/apodictic/scripts/validator_runner.py -->

## 1. Deliverable and boundary

This implements the owner-admitted CB-1(b) runner capability. It is a stdlib Python process that accepts closed JSON-lines requests on stdin, writes responses on stdout, and runs one of the fixed text leaves listed in §7. For the same decoded text and trusted package-reference context, each leaf returns the same exit code and stdout/stderr bytes as the canonical native `validate.py <leaf>` route with one file for single-text leaves or two ordered files for paired leaves. The runner never invokes Bash or the `validate.py` dispatcher. This is a development runner, not a signed desktop runtime.

The owner's requirement (Fleet `BURN-DOWN-BOARD.md` §5l CB-1(b)) lists closed schemas, input and output ceilings, cancellation, no network, fixed locale and time, fail-closed unavailability, and an inventory that gives every registry entry a disposition. The done-check is that runner output matches `--check-all` and that the inventory gate fails on an undispositioned registry change. Other authority: `handoffs/CODE-MAC-APODICTIC-LOCAL-CUTOVER-2026-07-21.md` §M3. The source baseline is apodictic main `217d2f08f3fd90c09880764d6547f576e0cdd560`. Validators are single-sourced in the plugin, so there is no root Python mirror.

The future Tauri broker owns signing, embedded or dependency-locked Python, environment scrubbing, resource ceilings, process-tree containment, desktop staged-path authority, native sandboxing, SBOMs and locks, and desktop acceptance. This increment does not claim them. It also does not claim full `--check-all` equivalence. Providers, models, SETEC, network operations, private manuscripts, shells, path input, and generic command, module or plugin dispatch are out of scope.

## 2. Existing behavior reused

Each leaf calls an unchanged canonical helper (`letter_checks`, `timeline_checks`, `calibration_honesty`, `legal_risk`, `scene_ethics`, `fiction_groundtruth`, `honesty_check`) in its default non-strict mode and reproduces that helper's CLI stdout and exit code with a one-line formatter. `stderr` is empty for every executed leaf. Input line endings are translated `CRLF -> LF`, then `CR -> LF`, to match the helper's universal-newline file read; there is no other normalization. The parity tests in `tests/test_validator_runner.py` compare every leaf with `validate.py <leaf>` and are the authority on per-leaf output. The runner adds no dependency checks of its own: a helper that fails to import maps to `runner_dependency_unavailable`, and a helper exception maps to `worker_failed` with no traceback or input text. Strict modes, directory discovery and path-sensitive checks are not exposed.

**Scope freeze (2026-11-04):** no app consumes this runner yet. Add leaves only when the desktop shell starts calling it.

## 3. Closed version 1 protocol

Launch: `python -I -S <canonical-script>/validator_runner.py` with a developer-selected Python 3.10+ interpreter. Workers use the same interpreter image with `-I -S -B` and run from the script directory. On Windows, `GetModuleFileNameW(NULL)` resolves the executable image already loaded by the coordinator, rather than relaunching a virtual-environment redirector. The fixed 32,768-WCHAR lookup must return a complete, nonempty absolute path; API, truncation or path failures yield `runner_dependency_unavailable`, with no launcher, environment or `PATH` fallback. This keeps the worker itself a direct child, so killing and waiting for a redirector cannot acknowledge completion before the actual interpreter exits. See the [Python venv behavior](https://docs.python.org/3.12/library/venv.html) and [Windows API contract](https://learn.microsoft.com/en-us/windows/win32/api/libloaderapi/nf-libloaderapi-getmodulefilenamew). Imports resolve from the script location, never from cwd, `PATH`, user site or `PYTHONPATH`. No request supplies a module, executable, path or argv.

Framing is UTF-8, with exactly one JSON object followed by LF per frame. The runner refuses a CR before the LF, invalid UTF-8, BOM, blank lines, trailing bytes, NaN/Infinity, lone surrogates, and parser recursion failure. Any of these is a fatal `invalid_frame`. Integer fields require an integer token, not a bool or float. `protocol` is exactly 1. Three shapes are accepted, with every field required and no extra field:

```json
{"protocol":1,"type":"validate","id":"r1","validator":"tone-check","text":"The pacing needs work.\n"}
{"protocol":1,"type":"validate_pair","id":"r2","validator":"timeline-diff","texts":["prior timeline","current timeline"]}
{"protocol":1,"type":"cancel","id":"c1","target":"r1"}
```

`id`, `validator` and `target` match `[A-Za-z0-9_-]{1,64}`. Ids are unique per session, and reusing one is fatal `duplicate_id`. `text` is a JSON string. `texts` is exactly two JSON strings in a JSON array, ordered prior/current for `timeline-diff` and letter/ledger for `softness-check`. Malformed pair containers, arity or element types are fatal `invalid_request`. A well-shaped request in the wrong mode (a paired leaf via `validate`, or a single-text leaf via `validate_pair`) returns `validator_unavailable`. The additive `validate_pair` extension retains protocol 1 and all existing request/response shapes; older runners reject this new request type with fatal `invalid_request`, so new clients must use a runner that supports it. A well-shaped request for an id outside the §7 table gets `validator_unavailable`. Manuscript text is never logged, persisted, echoed in errors, or sent anywhere except the worker.

A completed leaf returns:

```json
{"protocol":1,"type":"result","id":"r1","validator":"tone-check","available":true,"result":{"exit_code":0,"stdout":"OK: No blocked superlatives found. Severity tone is compliant.\n","stderr":""},"error":null}
```

A finding uses the same shape with `exit_code:1`. `available` means the leaf executed, not that the text passed. When a leaf is unavailable, the response uses the same outer shape with `available:false`, `result:null` and `error:{"code":CODE,"message":"Validator unavailable: CODE."}`. The closed codes are `validator_unavailable`, `runner_dependency_unavailable`, `input_limit`, `cancelled`, `timeout`, `worker_failed`, `output_limit` and `session_ended`. An import failure, or a missing helper or registry entry, maps to dependency unavailable. Any of the following maps to `worker_failed`: an exception, the wrong return shape, a nonzero worker exit, extra worker stdout or any stderr, or a malformed worker result. There is no retry, and no fallback to Bash.

A cancel returns `{"protocol":1,"type":"cancel_result","id":"c1","target":"r1","cancelled":BOOL,"error":null}`. `true` means an active target was killed and reaped, or a queued target was removed. In either case the target's sole terminal result, `cancelled`, is emitted first. `false` means the target is unknown or already terminal. A result that the coordinator has already accepted wins over a later cancel.

Fatal framing, schema, version and id errors emit `{"protocol":1,"type":"protocol_error","id":null,"error":{"code":CODE,"message":"Protocol refused: CODE."}}`. The codes are `invalid_frame`, `invalid_request`, `unsupported_protocol` and `duplicate_id`. Before that response, the runner reaps the active worker and ends the active and queued requests as `session_ended`, in order. The process then exits 2.

## 4. Limits and lifecycle

| Bound | Limit |
| --- | --- |
| Input frame | 1,048,576 bytes before LF, read incrementally; over is fatal `invalid_frame` |
| Text | 262,144 combined UTF-8 bytes before newline translation; each text has at most 8,191 LF characters after translation (8,192 lines); over is `input_limit` |
| Response | 32,768 encoded bytes including LF; over is `output_limit`, with no truncation |
| Execution | 5 seconds of monotonic time per leaf; over is `timeout` |
| Concurrency | One active worker, with later validations in a first-in, first-out queue |
| Cleanup | 2 seconds to kill and reap a worker; failure exits 2 |

No request or environment variable can change these limits. The session has no frame, byte, wall-time or idle limit. Admission checks come in this order: validator id and input mode, then text limits, then the queue. Every admitted validation gets exactly one terminal result. Refusals are answered at once, and queued work answers in order. Stdout carries only compact JSON lines.

Each validation runs in a fresh worker with the leaf id as its only argv input (`--worker <id>`) and the text string or ordered pair as JSON on stdin. The coordinator keeps reading stdin while a worker runs, so cancellation stays live. On cancel, timeout or a worker failure, the coordinator kills and reaps the worker, discards that worker's later output, and starts the next queued request. Clean EOF finishes the active and queued work, then the process exits 0. EOF in the middle of a frame is fatal `invalid_frame`. On POSIX, SIGTERM and SIGINT reap the worker, end the active and queued requests as `session_ended`, and exit 2. Abrupt Windows coordinator termination is not graceful JSONL cancellation; its containment remains a native-broker requirement. Responses are written directly to stdout. If stdout is broken, the runner reaps the worker and exits 2. A blocked consumer stays the parent's to resolve. Uncatchable death and process-tree containment belong to the broker.

The worker environment contains only `TZ=UTC`, `LC_ALL=C`, `LANG=C` and `PYTHONIOENCODING=utf-8`, plus `SystemRoot`/`WINDIR` on Windows. The leaves are trusted local code with no network-capable imports, and a static test enforces that. Audit-signal propagation and its underdiagnosis wrapper also read the trusted installed reference described in §7; they are not pure text functions. This is not a sandbox for arbitrary Python.

The process exits 0 for a clean session, whether leaves pass or fail, and 2 for usage, protocol, cleanup or transport failure. Consumers use the per-request envelope, never the process status.

## 5. Inventory

`plugins/apodictic/schemas/validator-runtime-inventory.json` is a closed file of the form `{"version":1,"validators":[ROW,...]}`. Each ROW has exactly `id`, `desktop_disposition` (`ci-only` or `not-yet-supported`) and a nonempty `omitted_capability` reason. `validator_runner.py --check-inventory` is a source and CI gate, run in the CI inventory-parity step. It prints one PASS or FAIL line and returns 0 or 1. It fails in any of these cases:

- the row ids are not unique;
- the row ids differ from the single literal `AGG_VALIDATORS` assignment in `plugins/apodictic/scripts/validate.py`, imported from the fixed sibling path (the import has no side effects and works with `-I -S` from a foreign cwd);
- a §7 leaf id is missing;
- a row or the file is malformed.

So any undispositioned registry addition, removal or rename fails the hosted gate. The runtime does not read the inventory. It grants no execution authority, and desktop support stays disabled. At baseline, three ids are `ci-only` (`schema-coverage`, `validator-conventions`, `argument-carve-behavior-preservation`), and every other id, including the eighteen leaves, is `not-yet-supported`. The JSON file is the source of truth for the per-id reasons. The gate compares sets, not counts; every `LEAVES` id must be registered.

## 6. Acceptance evidence

`tests/test_validator_runner.py` runs locally and is not in CI. It covers:

1. **Parity.** One table runs leaves × cases (shipped `lc.*.<leaf>.*.md` and `tl.*.<leaf>.*.md` fixtures, shared empty/Unicode/mixed-line-ending/text-ceiling cases, and invented per-leaf adversaries) through one real JSONL session. The session runs from a foreign cwd with an empty `PATH` and injected `PYTHONPATH`/site files. Each result's exit code and UTF-8 stdout/stderr bytes must equal the native `validate.py <leaf>` oracle.
   A second table runs the runner and the native CLI from the same disposable installation against changed, missing and malformed `pass-dependencies.md` maps, for `audit-signal-propagation` and `underdiagnosis-triggers`.
2. **Lifecycle.** One leaf-agnostic test uses a synthetic sleeping helper in a copied installation. On both Windows and POSIX it covers cancel (active and queued), timeout, EOF drain, fatal schema and frame errors, and an invalid cancel target. POSIX additionally retains SIGTERM and SIGINT. Windows runs through the configured interpreter and, when different, its base interpreter. A handle opened while the synthetic Windows worker is alive must already be signaled when its terminal response arrives; the test never uses `os.kill(pid, 0)` on Windows. Failure cleanup runs after that assertion and targets only the held synthetic-worker handle. POSIX retains absence-after-reaping evidence. It asserts the worker is reaped, there is no late result, the queue keeps its order, and healthy reuse works. It also covers dependency and worker failures, which must be unavailable with no text in errors and no files written.
Paired parity cases additionally cover ordered additions/removals, calibration precedence, exact-ID overrides and mixed line endings against two-file native calls. Mixed pair/single lifecycle scenarios share the existing queue, cancellation and worker cleanup tests.
3. **Protocol.** Closed request schemas, framing refusals, the frame, text and response ceilings at the limit and one over, a 70-request session, a three-request piped batch drained at EOF, fixed worker locale and time, and no network imports. Windows copied-installation faults also prove that missing/failed interpreter-image APIs, zero/truncated/empty results and relative paths yield unavailable responses without a launcher fallback or private text in errors.
4. **Inventory.** The gate passes on the real tree and fails on registry addition, removal, rename or duplicate, on an unregistered leaf, and on metadata omission, addition, duplicate, unknown class, blank reason or extra key. It never executes Bash.

Also run `python plugins/apodictic/scripts/validate.py --check-all`, compile, changelog, status-drift and release-generate checks, both build self-checks, and `git diff --check`.

## 7. Leaves

The runner admits exactly the keys of the literal `LEAVES` table in `validator_runner.py`; the `PAIRED` set marks the two leaves that take `validate_pair`. Each row names a fixed module, entrypoint, optional registry key and formatter. To add a leaf, add one row and its parity cases. No request, inventory value or argv selects a module, path, executable or formatter.

| Leaf | Helper result | Inherited behavior preserved for parity |
| --- | --- | --- |
| `timeline-diff` | paired four-tuple, empty summary omitted | Ordered prior/current structural changes and Section 8 coverage; body-only overrides. |
| `softness-check` | paired fixed-label error/warning report | Ordered letter/ledger delivery, locked severity, ID-scoped overrides and structured calibration precedence; no new finding-schema checks. |
| `fiction-groundtruth-check` | four-tuple | Mechanical answer-key completeness, lane/gate honesty and role/surface consistency; no semantic judgment or scoring. |
| `deficit-lock` | fixed-label error/warning report | Synthesis-bound prose labels require enough schema-valid finding locks; inherited helper exceptions are unavailable. |
| `legal-risk` | raw exit/lines | Schema and duplicate-ID errors, visible disclaimer, advisory legal-conclusion/counsel warnings and per-ID overrides. |
| `scene-ethics` | raw exit/lines | Schema and duplicate-ID errors, consent/fairness and legal-reference warnings; ethical decisions remain the writer’s. |
| `calibration-honesty` | raw exit/lines | Four claim shapes, paragraph-local qualifications and overrides; advisory only; native bounded diagnostic excerpts. |
| `timeline-arithmetic` | four-tuple, empty summary omitted | Negative gaps, labeled conflicts and computed span overruns; low-confidence/nonlinear exemptions and body-only overrides. |
| `timeline-anchor-conflict` | four-tuple, empty summary omitted | Labeled conflicts and same-scene anchor drift; Section 8 excluded and body-only overrides. |
| `tone-check` | four-tuple | Body before the first Appendix heading; code spans and blockquotes exempt; at most seven distinct blocked superlatives. |
| `synthesis-sections` | four-tuple | Fixed 14 heading names at levels 1–4, matched by the helper's own prefix and word-boundary rules; empty text fails with 14 errors. |
| `severity-floor` | four-tuple | Three mechanical rules; whole-letter justification search; overrides only in the body. Not proof of narrative adequacy. |
| `decision-layer-check` | four-tuple | Count, heading, appendix and reference checks. Argument-DE detection searches the whole letter, including appendices and code, so a marker there can skip Checks 3–4. A separate decision must repair that helper/policy discrepancy. |
| `author-facing-lint` | four-tuple | Advisory: errors are always empty, so exit is 0 with warnings. Warnings repeat codes, so valid text can exceed the response ceiling and return `output_limit`. |
| `ledger-check` | `(exit_code, lines)` | Five required subsections for each recognized pass; literal Pass 0 or 10 yields `NOTE:`; no passes yields `WARNING:` and exit 1. Repeated long pass headings can exceed the response ceiling. |
| `ledger-consolidation` | four-tuple | One-text raw-aggregation, convergence and severity-collation checks, including existing keyword and override semantics. The optional raw-ledger reduction comparison is not run. |
| `audit-signal-propagation` | four-tuple | One-text propagation check using the trusted installed `pass-dependencies.md` map, with inherited silent defaults when no reference is found. Located malformed parsed maps yield executed failures. Registry-check mode and argument-fragment expansion are excluded. |
| `underdiagnosis-triggers` | four-tuple | One-text composition of six textual trigger paths, including severity-floor and installed-map propagation child warnings/errors. Each parent trigger has its own body override. No ledger, seventh softness trigger or editorial retry is run. |

Build history: spec PR #329 and tone-check PR #332 (Fleet 730); the synthesis-sections spec (#333, Fleet 737) and build (#335, Fleet 739); severity-floor (#336, Fleet 743); decision-layer-check (#338, Fleet 746); author-facing-lint (#341, Fleet 750); ledger-check with the queue/EOF session fixes and the table-driven reshape (#342, Fleet 756); then ledger-consolidation (#357), audit-signal-propagation (#358) and underdiagnosis-triggers (#359). All development-leaf desktop dispositions remain `not-yet-supported`.

`ledger-consolidation` calls the unchanged helper with its default `raw_text=None`, matching the one-file `validate.py ledger-consolidation <file>` route. This leaf accepts only a single-text request, so the optional reduction-ratio check against a raw ledger never runs.

`audit-signal-propagation` and `underdiagnosis-triggers` (whose Trigger #6 calls propagation on every input, including empty text) are not pure text functions: the helper reads `pass-dependencies.md` from its fixed installed location. Parity with the native CLI holds only for the same installed reference. If the reference is missing, the helper silently uses its built-in defaults, so a result from a broken install does not show packaged policy. A malformed map is an executed failure (`exit_code:1`); through `underdiagnosis-triggers` it appears as a generic Trigger #6 and loses the `mapping is malformed` detail, and a live parent propagation marker can downgrade it to a warning. No request, cwd or environment value selects the reference.
