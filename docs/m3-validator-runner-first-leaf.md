# M3 validator runner: first leaf

**Status:** Built as a source-development tone-check, synthesis-sections, severity-floor, decision-layer-check, author-facing-lint, and ledger-check runner. Signed desktop availability and native Windows process qualification remain unestablished.
<!-- built-when: plugins/apodictic/scripts/validator_runner.py -->

## 1. Deliverable and boundary

Implement the first owner-admitted CB-1(b) runner capability: a stdlib Python process accepting closed JSON-lines requests over inherited stdin/stdout and executing `letter_checks.tone_check(text)`. The bounded second-leaf amendment in §7 adds only `letter_checks.synthesis_sections(text)` after independent review and a separately granted build. The bounded third-leaf amendment in §8 adds `letter_checks.severity_floor(text)` under the same development protocol. The bounded fourth-leaf amendment in §9 adds `letter_checks.decision_layer_check(text)`. The bounded fifth-leaf amendment in §10 adds `letter_checks.author_facing_lint(text)`. This is a development runner, not a signed desktop runtime. It produces the same validator exit code and stdout as the canonical Python-backed `validate.sh tone-check` route for the same decoded text. It never invokes Bash or the partial `validate.py` dispatcher.

Source baseline: apodictic main `217d2f08f3fd90c09880764d6547f576e0cdd560`. Authority: Fleet `BURN-DOWN-BOARD.md` §5l CB-1(b), and `handoffs/CODE-MAC-APODICTIC-LOCAL-CUTOVER-2026-07-21.md` §M3 (281–321). July M0 inventory is dependency history, not current runtime proof. Current `AGENTS.md` single-sources validators in the plugin: **no root Python mirror**. This document lives in `docs/`, matching current specs; no new `docs/specs/` hierarchy.

Signing, embedded/dependency-locked Python, Tauri broker, desktop staged-path authority, native sandbox qualification, SBOM/locks, full validator port and desktop clean-machine acceptance remain outside this increment and owner-gated where the board says so. This leaf does not establish complete `--check-all` equivalence. No provider, model, SETEC or network operation, private manuscript, shell, generic command/module/plugin dispatch, release workflow, current `validate.py` or helper edit belongs here.

## 2. Existing behavior reused

At the baseline, `plugins/apodictic/scripts/letter_checks.py:1136`, `tone_check(text)`, returns `(errors, warnings, ok_line, failed_line)`. It scans the synthesis body before the first Appendix heading, uses the existing `override_marker.strip_code_spans`, skips blockquoted lines, and reports at most seven distinct blocked superlatives in the helper's existing order. Reuse this function and unchanged helper; do not port the logic into the adapter.

The adapter formats that tuple exactly like `letter_checks.py:1250`, `run_check`: warnings, then errors, each followed by LF; when errors exist, one additional LF, then `failed_line` and LF, exit code 1; otherwise `ok_line` and LF, exit code 0. Preserve the FAILED line's embedded LF and NOTE. `stderr` is the empty string on a successful invocation, including a validator failure. Empty text retains the helper's existing successful result; do not add a minimum-length rule. Input line endings are translated `CRLF -> LF`, then remaining `CR -> LF`, reproducing the canonical helper's text-file universal-newline reading before calling the pure function. No trimming, Unicode normalization, replacement decoding or added headings.

Three existing public fixtures under `tests/fixtures/validators/` cover clean text, body superlatives and appendix/code exemption. Exact-main helper self-test currently has six synthetic checks plus those three fixtures, all passing. These establish seam viability, not runner or desktop acceptance.

## 3. Closed version 1 protocol

Launch explicitly with a developer-selected Python 3.10+ interpreter: `python -I -S <canonical-script>/validator_runner.py`. This is a source-development invocation, never discovery of an installed desktop interpreter. The runner refuses startup if isolated/no-site interpreter flags are absent; the usage error contains no input. Trusted fixed sibling imports are resolved from the canonical script location, never cwd, `PATH`, user site or `PYTHONPATH`. Any worker uses the same executable and isolation flags, solely to execute one coordinator-selected fixed leaf (§7). No module, executable, path or argv comes from a request.

Framing is binary UTF-8, exactly one JSON object followed by LF per frame. CRLF framing, BOM, blank lines, trailing non-JSON bytes, duplicate object keys at any depth, NaN/Infinity, invalid UTF-8, lone surrogate escapes, arrays/scalars, nesting deeper than eight containers, unknown keys and unsupported protocol versions are refused. Parser overflow/recursion failure is caught and refused, never a traceback. JSON whitespace within the LF-delimited record is legal; literal newlines in strings must be escaped. Integer fields require an integer JSON token, not a bool or float. `protocol` is exactly integer 1; no implicit negotiation or downgrade. No handshake or extensible capability dispatch.

Every request has a unique session id matching `[A-Za-z0-9_-]{1,64}`. Ids are public correlation tokens, not manuscript locators. Reuse of any accepted request id is a fatal protocol error; retained ids are bounded by the session ceiling. Only these two shapes are accepted, with every shown field required and no extra field:

```json
{"protocol":1,"type":"validate","id":"r1","validator":"tone-check","text":"The pacing needs work.\n"}
{"protocol":1,"type":"cancel","id":"c1","target":"r1"}
```

`validator` must be a bounded 1–64-character id using the same alphabet. Only the literals `tone-check`, `synthesis-sections` (§7), `severity-floor` (§8), `decision-layer-check` (§9), `author-facing-lint` (§10), and `ledger-check` (§11) are admitted. A well-shaped request naming any other id receives `validator_unavailable`; it never loads that validator. `text` must be a JSON string; no file, directory, URL, workspace, resource or output path is accepted. The only file authority is loading trusted shipped Python and ordinary inventory metadata. Manuscript text is never persisted, logged, echoed into error messages, used as a name, or sent outside this process and its fixed worker.

Cancel `target` must be a JSON string matching the same `[A-Za-z0-9_-]{1,64}` correlation-id grammar. Reject a wrong type, empty string, invalid alphabet or more than 64 characters as fatal `invalid_request` before target lookup or echo, using the existing active-leaf shutdown rule below. A valid bounded target that is unknown or already terminal retains `cancelled:false`.

A completed leaf emits exactly this result shape (all keys required, extra keys forbidden):

```json
{"protocol":1,"type":"result","id":"r1","validator":"tone-check","available":true,"result":{"exit_code":0,"stdout":"OK: No blocked superlatives found. Severity tone is compliant.\n","stderr":""},"error":null}
```

A validator finding uses the same shape, `available:true`, `exit_code:1`, and exact legacy stdout. `available` means the leaf executed, not that the text passed. The result exit code is only 0 or 1. No inferred verdict or separate pass boolean is introduced.

Unavailability uses the same outer result shape with `available:false`, `result:null`, and `error:{"code":CODE,"message":MESSAGE}`. For every result error, message is exactly `Validator unavailable: <code>.` with the literal closed code substituted. Consumers branch on code, never message wording. No exception text is included. Closed codes: `validator_unavailable`, `runner_dependency_unavailable`, `input_limit`, `cancelled`, `timeout`, `worker_failed`, `output_limit`, `session_ended`. Missing/unreadable shipped helper, import/dependency failure or absent capability metadata maps to dependency unavailable, never a successful empty check. Unexpected tuple shape, exception, child exit, nonempty worker diagnostic stdout/stderr, or malformed worker result maps to `worker_failed`. Output overflow maps to `output_limit`; no truncation into a success. These states contain no legacy result/exit code. No retry or fallback to Bash/native dispatcher.

Cancellation emits a control response of exactly:

```json
{"protocol":1,"type":"cancel_result","id":"c1","target":"r1","cancelled":true,"error":null}
```

`cancelled:true` means an active target was stopped and reaped, or a queued target was removed before it started, and its sole validation terminal result is `available:false/error.code:cancelled`. `cancelled:false` means no active or queued target at processing time (unknown or already terminal); it does not reverse or repeat an earlier result. Validation terminal precedes a successful cancel response. These controls have their own unique ids and do not count as validation results.

For fatal framing/schema/version/id errors, emit one final shape `{"protocol":1,"type":"protocol_error","id":null,"error":{"code":CODE,"message":MESSAGE}}`, with closed code `invalid_frame`, `invalid_request`, `unsupported_protocol`, or `duplicate_id`. For every protocol error, message is exactly `Protocol refused: <code>.` with the literal closed code substituted. Do not salvage or echo an unvalidated id. Stop/reap any active worker, then emit the sole `session_ended` result for the active request and each queued request, in admission order, before the fatal response, when stdout remains writable. Exit 2. A malformed request is not a validator pass or ordinary finding.

## 4. Finite limits and lifecycle

These v1 limits address concrete untrusted-stream risks: unbounded framing allocations, pathological regex work, a blocked consumer, and an abandoned child. They are protocol limits, not tunable performance advice. Changing them requires reviewed protocol acceptance; no request or environment variable can increase them.

| Bound | Limit and measurement |
| --- | --- |
| Input frame | 1,048,576 bytes before its LF; bounded incremental read, do not allocate an unbounded line |
| Text | 262,144 UTF-8 bytes before newline translation; at most 8,192 logical lines after translation (LF count plus one, including an empty final line) |
| Response | 32,768 encoded UTF-8 bytes including final LF; serialize/check before writing, never partial success |
| Execution | 5 seconds monotonic wall time per leaf, from worker start through validated result receipt |
| Concurrent work | One active leaf; another valid validation waits in a first-in, first-out queue and starts when the slot frees |
| Cleanup/write | 2 seconds total after cancellation/timeout/end to stop/reap the worker and finish the bounded response write |

After full framing/schema/version/id validation, admission order is unsupported validator, text limits, dependency, then queued worker execution. Each well-shaped request id is retained even for a refused leaf. Valid oversized supported-leaf text returns `input_limit` without calling the helper. Oversized framing cannot safely parse a request, so it is fatal `invalid_frame`. There is no session-wide frame, byte, wall-time or idle limit: a client may hold a session open and send any number of requests, each bounded by the per-frame, text, execution and response limits. All output is compact JSON plus LF; no banner, progress line or self-test text contaminates protocol stdout. Work diagnostics go to bounded fixed stderr messages only. Response-limit failure must itself fit a small fixed error envelope; control/error envelopes are subject to the same limit.

The coordinator must continue receiving cancellation while the helper is running; calling the pure function synchronously in the stdin loop is insufficient. Use a single disposable fixed leaf worker with only bounded text/result pipes; this is process isolation for cancellation and work time, not a generic broker. No child-created descendants or discretionary files are allowed. Stop, force-terminate if needed, and reap/close worker resources within the cleanup bound on cancel, timeout, fatal request, EOF, output failure and coordinator termination. Do not emit a cancellation success before cleanup succeeds. If cleanup cannot be confirmed, terminate the session with nonzero status; never claim a reusable worker or successful check.

Race rule: if a validated worker result has been accepted by the coordinator before cancel processing, it remains the terminal result and cancel reports false. Otherwise cancel wins; discard all subsequent worker output. Every well-shaped admitted validate request gets one terminal result, including unsupported/limit refusals and queued requests cancelled or ended before starting. Never emit both timeout/cancel and a later successful result for the same id.

Clean EOF between frames admits no further input; the coordinator finishes the active and every queued validation in order, each under its own five-second execution limit, emits their terminal results, then exits 0, so a piped batch returns every result. EOF with an unterminated frame is fatal `invalid_frame`, even if its bytes form complete JSON. Broken stdout or a blocked writer exceeding the cleanup/write deadline requires cleanup and process exit 2; delivery cannot be guaranteed to a disconnected reader and is not claimed. Handled termination (SIGTERM/SIGINT on POSIX, supported console termination on Windows) must enter the same bounded cleanup path, ending the active and queued requests as `session_ended`. Uncatchable coordinator death, host shutdown and native process-tree containment require the future broker/platform work; this development leaf must not claim to solve them. Workers run no grandchildren. Test handled termination on the development host and disclose any unqualified Windows termination behavior. No text-bearing temporary file, cache, log or recovery record exists to clean up.

Environment: fixed UTC timezone and UTF-8 encoding, deterministic C locale where available, no environment-dependent thresholds or clocks in results. Scrub inherited provider credentials, proxy variables, Python injection variables and user configuration from workers rather than copying the parent's environment; forward only the minimal platform variables needed to start the fixed interpreter, plus the deterministic values. The host interpreter's stdlib remains a development prerequisite. The coordinator/worker exposes no network-capable request path; install a small socket-audit denial before importing the trusted leaf, and test attempted socket use is refused. This is a bounded trusted-code development guard, not a claim of native OS sandboxing or safe execution of arbitrary Python. No arbitrary source or request-driven import is evaluated.

Process status is 0 for a clean protocol session, whether leaf findings pass or fail; 2 for usage/protocol/lifecycle/transport failure. A consumer uses the per-request envelope, never process exit 0 or empty output as validation success. Missing result, wrong schema/version/id/type, duplicate terminal result, EOF during a response and an unavailable envelope must remain unavailable. There is no automatic retry.

## 5. One inventory coupled to the actual leaf

The first implementation includes ordinary capability rows under `plugins/apodictic/schemas/validator-runtime-inventory.json` and a source-side `validator_runner.py --check-inventory` mode. This small check is shipped with the actual runner; do not introduce a separate checker service, registry, hash, lock, signature or release identity framework. The metadata is a disposition inventory, not another command dispatch source. The runtime has the six finite hardwired leaves specified here and in §§7–11 and refuses all other validator ids.

Closed file shape: `{"version":1,"validators":[ROW,...]}`; ROW has only `id`, `desktop_disposition`, `development_support`, `omitted_capability`. Id uniqueness and exact equality with current canonical `AGG_VALIDATORS` are required. Read the single literal assignment in `plugins/apodictic/scripts/validate.sh` without executing/importing Bash. Missing, ambiguous, dynamic or duplicate registry contents fail the check; do not guess. All metadata is bounded to 65,536 bytes before reading, and at most 512 rows. `desktop_disposition` is exactly `ci-only` or `not-yet-supported` in this unsigned increment; `development_support` is exactly `tone-check-v1`, `synthesis-sections-v1` (§7), `severity-floor-v1` (§8), `decision-layer-check-v1` (§9), `author-facing-lint-v1` (§10), `ledger-check-v1` (§11), or `none`. Omission reason is a nonempty bounded string (1–256 Unicode scalars) identifying the corresponding unavailable product capability, not “source copied.” Unknown fields/enums, ids or unsupported development mappings fail. Each non-none support value is allowed only for its identically named leaf; no desktop-supported rows are allowed in this unsigned increment. Source check success is a checked inventory, not desktop availability.

`--check-inventory` is an exclusive source-tool mode (no JSONL input, no validation), printing one bounded PASS/FAIL summary and returning 0/1. The runner validates the bounded metadata and its own exact supported-leaf mappings at startup; missing/malformed metadata disables all six leaves for that session. It may still process bounded valid protocol requests, but every otherwise admissible supported-leaf request receives `runner_dependency_unavailable`, with no helper execution. The source inventory check returns FAIL; startup failure never supplies a pass or claims availability. Registry exact-set conservation is the source check's responsibility, tested in the implementation. Generated host bundles recursively include canonical scripts/schemas; verify their actual output, do not create mirrors or modify generators by default.

All current ids are explicitly dispositioned below. `N` means `not-yet-supported`, with omitted capability “<id> validation is unavailable in desktop: no signed, brokered leaf.” `C` means `ci-only`, with the named source/repository check excluded from the desktop product. Every row is `development_support:none` except tone-check (`tone-check-v1`), synthesis-sections (`synthesis-sections-v1`), severity-floor (`severity-floor-v1`), decision-layer-check (`decision-layer-check-v1`), author-facing-lint (`author-facing-lint-v1`), and ledger-check (`ledger-check-v1`). All six product dispositions stay N even after development parity passes. Counts are diagnostic; the gate compares sets, not a fixed 84 literal.

| Canonical id | Desktop disposition | Omitted product capability / development exception |
| --- | --- | --- |
| `contract-hash` | N | contract-hash validation unavailable in desktop; no signed, brokered leaf. |
| `contract-check` | N | contract-check validation unavailable in desktop; no signed, brokered leaf. |
| `ledger-check` | N | ledger-check validation unavailable in desktop; no signed, brokered leaf. Development only: ledger-check-v1 (§11). |
| `artifact-names` | N | artifact-names validation unavailable in desktop; no signed, brokered leaf. |
| `synthesis-sections` | N | synthesis-sections validation unavailable in desktop; no signed, brokered leaf. Development only after §7 build: synthesis-sections-v1. |
| `tone-check` | N | tone-check validation unavailable in desktop; no signed, brokered leaf. Development only: tone-check-v1. |
| `state-lines` | N | state-lines validation unavailable in desktop; no signed, brokered leaf. |
| `severity-floor` | N | severity-floor validation unavailable in desktop; no signed, brokered leaf. Development only after §8 build: severity-floor-v1. |
| `audit-signal-propagation` | N | audit-signal-propagation validation unavailable in desktop; no signed, brokered leaf. |
| `underdiagnosis-triggers` | N | underdiagnosis-triggers validation unavailable in desktop; no signed, brokered leaf. |
| `ledger-consolidation` | N | ledger-consolidation validation unavailable in desktop; no signed, brokered leaf. |
| `decision-layer-check` | N | decision-layer-check validation unavailable in desktop; no signed, brokered leaf. Development only: decision-layer-check-v1 (§9). |
| `author-facing-lint` | N | author-facing-lint validation unavailable in desktop; no signed, brokered leaf. Development only: author-facing-lint-v1 (§10). |
| `quality-risk-triggers` | N | quality-risk-triggers validation unavailable in desktop; no signed, brokered leaf. |
| `cost-floor` | N | cost-floor validation unavailable in desktop; no signed, brokered leaf. |
| `timeline-diff` | N | timeline-diff validation unavailable in desktop; no signed, brokered leaf. |
| `timeline-arithmetic` | N | timeline-arithmetic validation unavailable in desktop; no signed, brokered leaf. |
| `timeline-anchor-conflict` | N | timeline-anchor-conflict validation unavailable in desktop; no signed, brokered leaf. |
| `audit-tier-criterion` | N | audit-tier-criterion validation unavailable in desktop; no signed, brokered leaf. |
| `pass-header` | N | pass-header validation unavailable in desktop; no signed, brokered leaf. |
| `argument-recon-prerequisite` | N | argument-recon-prerequisite validation unavailable in desktop; no signed, brokered leaf. |
| `structured-findings` | N | structured-findings validation unavailable in desktop; no signed, brokered leaf. |
| `softness-check` | N | softness-check validation unavailable in desktop; no signed, brokered leaf. |
| `deficit-lock` | N | deficit-lock validation unavailable in desktop; no signed, brokered leaf. |
| `artifacts-schema` | N | artifacts-schema validation unavailable in desktop; no signed, brokered leaf. |
| `gate` | N | gate validation unavailable in desktop; no signed, brokered leaf. |
| `gate-state` | N | gate-state validation unavailable in desktop; no signed, brokered leaf. |
| `finding-trace` | N | finding-trace validation unavailable in desktop; no signed, brokered leaf. |
| `escalation-check` | N | escalation-check validation unavailable in desktop; no signed, brokered leaf. |
| `feedback-triage` | N | feedback-triage validation unavailable in desktop; no signed, brokered leaf. |
| `editor-scaffolding` | N | editor-scaffolding validation unavailable in desktop; no signed, brokered leaf. |
| `diagnostic-vocabulary` | N | diagnostic-vocabulary validation unavailable in desktop; no signed, brokered leaf. |
| `retcon-plan` | N | retcon-plan validation unavailable in desktop; no signed, brokered leaf. |
| `state-card-diff` | N | state-card-diff validation unavailable in desktop; no signed, brokered leaf. |
| `revision-arc` | N | revision-arc validation unavailable in desktop; no signed, brokered leaf. |
| `regression-diff` | N | regression-diff validation unavailable in desktop; no signed, brokered leaf. |
| `legal-risk` | N | legal-risk validation unavailable in desktop; no signed, brokered leaf. |
| `promise-contract` | N | promise-contract validation unavailable in desktop; no signed, brokered leaf. |
| `continuity-bible` | N | continuity-bible validation unavailable in desktop; no signed, brokered leaf. |
| `setup-payoff` | N | setup-payoff validation unavailable in desktop; no signed, brokered leaf. |
| `world-bible` | N | world-bible validation unavailable in desktop; no signed, brokered leaf. |
| `intake-interview` | N | intake-interview validation unavailable in desktop; no signed, brokered leaf. |
| `author-fingerprint` | N | author-fingerprint validation unavailable in desktop; no signed, brokered leaf. |
| `content-advisory` | N | content-advisory validation unavailable in desktop; no signed, brokered leaf. |
| `coaching-history` | N | coaching-history validation unavailable in desktop; no signed, brokered leaf. |
| `style-explanation` | N | style-explanation validation unavailable in desktop; no signed, brokered leaf. |
| `persona-divergence` | N | persona-divergence validation unavailable in desktop; no signed, brokered leaf. |
| `argument-spine` | N | argument-spine validation unavailable in desktop; no signed, brokered leaf. |
| `scene-ethics` | N | scene-ethics validation unavailable in desktop; no signed, brokered leaf. |
| `argument-groundtruth-check` | N | argument-groundtruth-check validation unavailable in desktop; no signed, brokered leaf. |
| `fiction-groundtruth-check` | N | fiction-groundtruth-check validation unavailable in desktop; no signed, brokered leaf. |
| `agreement-alpha` | N | agreement-alpha validation unavailable in desktop; no signed, brokered leaf. |
| `argument-crosswalk-check` | N | argument-crosswalk-check validation unavailable in desktop; no signed, brokered leaf. |
| `argument-agd` | N | argument-agd validation unavailable in desktop; no signed, brokered leaf. |
| `argument-aif-check` | N | argument-aif-check validation unavailable in desktop; no signed, brokered leaf. |
| `argument-reconstruction` | N | argument-reconstruction validation unavailable in desktop; no signed, brokered leaf. |
| `argument-reconstruction-draft` | N | argument-reconstruction-draft validation unavailable in desktop; no signed, brokered leaf. |
| `registry-check` | N | registry-check validation unavailable in desktop; no signed, brokered leaf. |
| `schema-coverage` | C | Repository schema coverage is a source/CI check, excluded from desktop. |
| `lifecycle-node` | N | lifecycle-node validation unavailable in desktop; no signed, brokered leaf. |
| `reader-instrument` | N | reader-instrument validation unavailable in desktop; no signed, brokered leaf. |
| `manuscript-viz` | N | manuscript-viz validation unavailable in desktop; no signed, brokered leaf. |
| `annotated-manuscript` | N | annotated-manuscript validation unavailable in desktop; no signed, brokered leaf. |
| `crosslink` | N | crosslink validation unavailable in desktop; no signed, brokered leaf. |
| `reanchor` | N | reanchor validation unavailable in desktop; no signed, brokered leaf. |
| `roundtrip-disposition` | N | roundtrip-disposition validation unavailable in desktop; no signed, brokered leaf. |
| `disposition-check` | N | disposition-check validation unavailable in desktop; no signed, brokered leaf. |
| `synthesis-coverage` | N | synthesis-coverage validation unavailable in desktop; no signed, brokered leaf. |
| `dispatch-record` | N | dispatch-record validation unavailable in desktop; no signed, brokered leaf. |
| `specificity-floor` | N | specificity-floor validation unavailable in desktop; no signed, brokered leaf. |
| `refutation-coverage` | N | refutation-coverage validation unavailable in desktop; no signed, brokered leaf. |
| `refutation-evidence` | N | refutation-evidence validation unavailable in desktop; no signed, brokered leaf. |
| `refutation-write-scope` | N | refutation-write-scope validation unavailable in desktop; no signed, brokered leaf. |
| `obsidian-export` | N | obsidian-export validation unavailable in desktop; no signed, brokered leaf. |
| `html-export` | N | html-export validation unavailable in desktop; no signed, brokered leaf. |
| `docx-export` | N | docx-export validation unavailable in desktop; no signed, brokered leaf. |
| `pdf-export` | N | pdf-export validation unavailable in desktop; no signed, brokered leaf. |
| `results-guide` | N | results-guide validation unavailable in desktop; no signed, brokered leaf. |
| `position-pair-register` | N | position-pair-register validation unavailable in desktop; no signed, brokered leaf. |
| `reader-contract-outline` | N | reader-contract-outline validation unavailable in desktop; no signed, brokered leaf. |
| `calibration-honesty` | N | calibration-honesty validation unavailable in desktop; no signed, brokered leaf. |
| `stance-calibration` | N | stance-calibration validation unavailable in desktop; no signed, brokered leaf. |
| `validator-conventions` | C | Validator source conventions are a source/CI check, excluded from desktop. |
| `argument-carve-behavior-preservation` | C | Repository argument-carve fixture composite is a source/CI check, excluded from desktop. |

Compared with July M0's 83 rows, add argument-reconstruction and argument-reconstruction-draft; check-mirror is a nonaggregate developer command and is not an omitted AGG row. The baseline has 84 unique ids: three CI-only, 81 not yet desktop-supported, zero desktop-supported. Metadata reasons may later become more specific when the corresponding leaf is reviewed; no eligibility is inferred from Python source or helper availability.

## 6. Implementation unit and acceptance

First-leaf implementation scope (built): canonical `plugins/apodictic/scripts/validator_runner.py`; `plugins/apodictic/schemas/validator-runtime-inventory.json`; focused `tests/test_validator_runner.py`; this doc's built status; `changelog.d/m3-tone-check-runner.md`. Closed schemas above are normative and validated in stdlib code; a separate JSON Schema file is not needed to add a runtime dependency or duplicate validation. Preserve existing Bash/Python helper/registry/other-schema/fixture/workflow bytes and separately owned dispatcher/parity/port-document paths. Obtain fresh exact custody, independently review the committed implementation, then publish only an unarmed draft constituent. Owner-gated signed/brokered runtime remains owed.

Required behavioral evidence:

1. Real subprocess JSONL invocation from foreign cwd and empty PATH in isolated/no-site mode, repeated requests, exactly one compact response per accepted request, no shell/Bash/provider/network requirement. Both generator outputs contain and can invoke the canonical leaf with a supplied development interpreter. This is portability evidence, not an embedded runtime claim.
2. Differential code/stdout/stderr parity against the unchanged canonical Python-backed Bash tone route for all three shipped tone fixtures, the six existing synthetic cases, all seven blocked phrases together/repeated/in mixed case, empty text, Unicode, LF/CRLF/bare-CR and Appendix/code/blockquote boundary adversaries. Match UTF-8 output bytes exactly after JSON decoding; no whitespace normalization. Run exact-main helper self-test and canonical combined `bash scripts/validate.sh --check-all` before build review. No full-validator or native-Windows parity claim from these leaf checks.
3. Closed framing/schema rejection: every extra/missing/wrong-typed field, duplicate key/id, arrays/scalars, booleans/floats for version, unsupported version, malformed UTF-8/JSON, BOM, CRLF delimiter, unterminated EOF, literal/present surrogate, NaN/Infinity, injected paths/argv/modules and unsupported validator. Cancel-target acceptance covers exactly 64 valid characters, 65 characters, empty string, wrong JSON type, invalid alphabet and an unknown valid bounded target; invalid targets cause fatal `invalid_request` before lookup/echo, including stopping/reaping an active leaf and its sole `session_ended` result under the existing fatal rule. Unknown valid targets return `cancelled:false`. Boundary values and one over for every frame/text/line/output limit; blocked writer; a long sequential session and a piped batch ending at EOF. Unsupported/malformed/unavailable never converts to pass.
4. Real fixed-worker timeout/cancel/EOF and handled coordinator-termination tests with bounded synthetic sleeping/failing worker seams confined to tests, no production request option for those seams. Assert worker dead/reaped, no late successful result, cancel race behavior, queued order, queued-request cancellation and subsequent healthy request after reusable failures. Simulate missing helper/dependency/malformed child output and verify fixed unavailable mappings without text-bearing errors. Socket denial, hostile inherited cwd/environment/PYTHONPATH/site settings cannot change the leaf or trigger a network request. Input text never appears in stderr, temp files or error messages.
5. Inventory test changes the actual registry input to add/remove/rename/duplicate an id, and metadata to omit/add/duplicate/unknown-class/empty-reason/false-desktop-support/invalid-development-mapping rows. Each fails; all current explicit dispositions pass without executing the registry. Do not pin a permanent count or sorted-id hash. A check success cannot enable an unsupported validator.
6. Applicable local compilation, changelog/status-drift and existing generator self-checks; whitespace checks. Readiness holds until independent substantive spec review and exact-head implementation review resolve findings. Report platform/process-termination limitations precisely rather than claiming signed/native sandbox completion.

No new owner policy decision is needed to implement this development leaf after review. Protocol ceilings and mappings here are this increment's engineering contract, not an expansion of product authority. A request to enable desktop-supported status, add path-based input, expand leaves, use real user material, change provider/network behavior or integrate signing/broker/packaging must return to its appropriate separately admitted scope.

## 7. Bounded second-leaf amendment: synthesis-sections

Amendment baseline: independently cleared, durably published held draft PR332, `d545ddc70bb55266234c5a2c6736bda58b9dbc26`, on spec PR329 `4bb61612e17cc16963f47385e24e7490828ba3ad`. Fleet730 custody is released; Fleet737 is the separate one-path spec task. Amendment build status: implemented as a development-only leaf under the separate five-path Fleet739 grant, following independent spec clearance. Development evidence does not qualify signed desktop availability or native Windows behavior.

### Fixed worker binding and legacy result

The additional public validator id is exactly `synthesis-sections`. Its validate/result envelopes have the unchanged §3 shapes, with that literal in `validator`; neither protocol version nor request/result/control/error fields change. In mixed sessions every success, finding, refusal and lifecycle terminal envelope keeps the originating validate request's exact `id` and `validator`. The coordinator retains that identity independently of worker output; never hardcode `tone-check` into a successful second-leaf response or trust a child-selected identity. Cancellation still targets the correlation id and has no validator selector. The active-worker slot is shared by both leaves.

Bind each admitted literal to one fixed worker invocation, preserving the existing tone worker route: `--worker` calls `letter_checks.tone_check(text)`; the sole added private route `--worker-synthesis-sections` calls `letter_checks.synthesis_sections(text)`. These are exact internal argv forms selected by the coordinator, using the same fixed sibling script, interpreter and isolation flags. The worker input remains the existing bounded JSON text string, not a command or module descriptor. Unknown/extra worker argv is usage failure, never another route. Resolve only the fixed sibling `letter_checks` import and explicitly named helper in code; no generic `CHECKS` lookup, `getattr`, dynamic module/import/executable selection, metadata dispatch, path dispatch or configurable routing. Inventory grants no import or execution authority. The tone worker's helper, input handling and result formatting remain unchanged.

Reuse the existing pure `letter_checks.synthesis_sections(text)` and its `(errors, warnings, ok_line, failed_line)` tuple; apply precisely the §2 formatter and universal-newline translation. Warnings precede errors with LF; failures add the separating LF, preserve the FAILED line's embedded LF and NOTE, and return exit 1; success returns exit 0 and the helper's exact ok line plus LF. Validator findings have empty stderr and `available:true`. Dependency/import failures, malformed tuple/result, unexpected diagnostic output, exceptions, worker death and output overflow retain the §3 closed mappings. Do not add a minimum length: empty text fails with all 14 fixed missing-heading errors in helper order and 898 UTF-8 stdout bytes. Success emits 66 bytes. Output contains no input prose and stays inside the existing response ceiling.

The helper scans heading titles using its existing levels 1–4 matcher, leading emphasis handling, existing `lower()` comparison and Unicode alphanumeric/underscore trailing-boundary behavior. Preserve its actual regex semantics, including whitespace and heading boundaries; no replacement Markdown parser, heading extraction, normalization or helper edits. It checks the fixed 14-name tuple in existing order. It performs no I/O. `cost_floor` reads paths and has a different return shape; it and every other validator remain unavailable.

### Inventory and inherited lifecycle

Change only the existing synthesis-sections row from `development_support:none` to `synthesis-sections-v1`; retain its `not-yet-supported` desktop disposition and omission reason. Tone-check retains its exact mapping and row. The two support values are valid only on their respective ids, both required with their exact not-yet-supported dispositions at startup and in `--check-inventory`. Swapped values, unknown support values, either missing/disabled supported mapping or any malformed inventory fail the existing checker and disable both leaves for the session; otherwise admissible supported requests receive `runner_dependency_unavailable`. Unsupported ids still receive `validator_unavailable` first, regardless of inventory failure. No metadata value can enable a third leaf or desktop support. Keep the same bounded file/rows, closed schema and exact real canonical-set comparison. The current 84 unique identities and 3 CI-only/81 not-yet-supported/zero desktop-supported dispositions are diagnostic observations, never fixed-count substitutes for set equality.

All §3–4 framing, schema, id retention, admission ordering, one-worker concurrency, fixed limits, environment/socket denial, cancel/result races, deadlines, EOF, fatal behavior, transport failure and process status apply unchanged to either leaf. Preserve the predecessor's single absolute two-second cleanup/write budget: stopping/reaping, all related terminal/control/fatal writes and failure diagnostics share that deadline; no fresh budget per write or diagnostic, including blocked/broken stdout or saturated stderr. No production sleep seam, adjustable ceiling, new session mode, retries or worker reuse is added.

### Separately granted build scope and acceptance

The sole spec-edit path is this existing document. The later minimum implementation is exactly five paths: `plugins/apodictic/scripts/validator_runner.py`, existing `plugins/apodictic/schemas/validator-runtime-inventory.json`, existing `tests/test_validator_runner.py`, this document's amendment built status, and new `changelog.d/m3-synthesis-sections-runner.md`. Helper, Bash, `validate.py`, registry, other schemas, fixtures, generators and workflows remain unchanged. Extend the existing runner/tests/checker; no separate routing or inventory framework. Commit the candidate, complete independent exact-head implementation review and resolve findings before an unarmed stacked draft publication. No merge, ready/CI arming, tag or product release belongs to this unit.

Required evidence supplements and preserves every §6 gate:

1. Use real isolated/no-site JSONL subprocess execution and compare each decoded result's exit code plus UTF-8 stdout/stderr bytes exactly to the unchanged Python-backed canonical Bash/helper route. Cover all three shipped synthesis fixtures (`lc.fail.synthesis-sections.midheading-mention.md`, `lc.fail.synthesis-sections.missing-heading.md`, `lc.pass.synthesis-sections.all-headings.md`) and all five existing synthetic cases (all headings, missing heading, subtitles/emphasis, midheading mention, lookalike prefix). A helper self-test PASS alone does not establish runner parity. Add empty text, case and Unicode/lookalike prefixes, underscore/alphanumeric/punctuation boundaries, levels 1–4 versus level 5, prose/midheading mentions, whitespace/heading boundaries, LF/CRLF/bare-CR and bounded heading-heavy inputs up to the existing text/line ceilings. Compare exact raw output after decoding, with no wording or whitespace normalization. Over-limit text retains `input_limit` without helper execution.
2. Alternate tone/synthesis successes and findings in real mixed sessions, including distinct ids and shared-slot queueing, to prove exact leaf binding in successful and unavailable results and unchanged tone behavior. Preserve unsupported-leaf, input-limit and dependency admission order, unknown cancel targets and one terminal result per validate id. Test missing helper and malformed child results for the new leaf as unavailable, with no false pass or text-bearing diagnostics.
3. Extend the existing test-confined synthetic worker harness for the synthesis route to exercise real cancellation, handled coordinator termination, EOF/fatal shutdown, worker death/reaping and no late results. A normal synthesis input finishing quickly is not timeout evidence: use the existing sleeping worker seam confined to a temporary copied test installation, keep the actual five-second execution and shared two-second cleanup/write limits, observe timeout and death/reaping, then a healthy request from the other leaf. Preserve the inherited blocked/broken writer, saturated-stderr, result/cancel race protections; do not add test configuration or worker delays to production code.
4. Exercise actual inventory mutations: swapped tone/synthesis support, unknown support, missing/none supported mapping, duplicate/unknown ids, empty omission reason, false desktop support and real canonical registry add/remove/rename/duplicate drift. Checker failure and runtime refusal must agree on invalid mappings; checker success must leave unsupported leaves unavailable. Preserve the canonical identities/dispositions rather than accepting a matching row count.
5. Run existing focused runner tests, both unchanged helper self-tests, canonical combined `bash scripts/validate.sh --check-all`, applicable compilation/doc-status/changelog/release-generator checks, both build self-checks and `git diff --check` before exact-head build review. Invoke the actual runner and inventory checker from both actual generated Codex and Antigravity outputs with the supplied isolated development interpreter, from a foreign cwd/empty PATH; execute both leaves and a mixed session with correct identities. Source-file presence and generator self-check alone are insufficient generated-host invocation evidence. All fixture text is invented or already public. Development-host parity and process evidence establish no signed desktop, native Windows or full-validator qualification.

## 8. Bounded third-leaf amendment: severity-floor

Build status: implemented as a development-only third leaf under the separate five-path Fleet743 grant, after the independently cleared and published synthesis predecessor. This amendment adds no desktop admission, severity policy, native Windows qualification or signed runtime claim.

The sole new public literal is `severity-floor`. The coordinator binds it to the sole new private `--worker-severity-floor` argv form, whose fixed sibling import explicitly names `letter_checks.severity_floor`; `--worker` and `--worker-synthesis-sections` remain unchanged. No request or inventory row selects an import, executable, path, formatter or output destination. The worker receives only the bounded JSON text string. The coordinator retains the originating request's `id` and `validator` for every terminal result. All three leaves share the one active-worker slot and the unchanged admission order. Cancel targets the correlation id without a validator selector.

The existing helper actually returns `(errors, warnings, ok_line, failed_line)`. Reuse it and the unchanged override helper. Apply §2's universal-newline translation and formatter byte for byte: warnings then errors with LF, a separating LF before the failed summary when errors exist, otherwise the exact OK line with LF. Findings retain `available:true`, exit 1 and empty stderr; successful empty text retains its 73 UTF-8 stdout bytes. The helper's three fixed rule branches, whole-letter severity/justification search, body-only override search, regex/substring behavior and fixed diagnostics are inherited exactly. A live override or whole-letter justification match is a mechanical helper result, not proof of narrative adequacy, Deficit Lock, or an Appendix B rationale. No helper or policy rewrite is included.

The existing severity inventory row alone changes from `development_support:none` to `severity-floor-v1`; its `not-yet-supported` desktop disposition and omission reason remain. All three exact id/support pairs and their dispositions are required by startup and `--check-inventory`. Malformed, swapped, disabled or missing supported mappings disable all three leaves; unsupported request ids still refuse as `validator_unavailable` before dependency admission. A well-shaped unknown support-none row does not enable a new literal at runtime, while exact canonical `AGG_VALIDATORS` set conservation remains the source check's responsibility. Counts are observations, not acceptance constants, and startup does not parse or execute Bash.

All inherited §3–4 limits and lifecycle behavior apply: fixed isolated worker, one active slot, five-second execution, cancellation/result race, EOF/fatal/handled termination, and one absolute two-second cleanup/write/diagnostic budget with the active-worker reserve. Dependency/import failure, malformed output, child death, diagnostics and overflow remain closed unavailable/error results without retry or Bash fallback. No production test knob, new protocol mode or worker reuse is added. The bounded build changes only runner, existing inventory, runner tests, this document and its severity changelog fragment. Development-host and generated-source tests do not qualify signed desktop execution, native Windows process containment, or full-validator parity.

## 9. Bounded fourth-leaf amendment: decision-layer-check

Build status: implemented as a development-only fourth leaf under separate Fleet issue 746, worker grant 6139853178, on released PR336 head `900109785d8ea8a8aab70168446ff94db75f5c3d`. The existing desktop disposition remains `not-yet-supported`; this development route supplies no signed desktop or native Windows qualification.

The sole new public literal is `decision-layer-check`. It selects the private fixed `--worker-decision-layer-check` route and explicit sibling `letter_checks.decision_layer_check(text)` import. Its bounded text, isolated interpreter, four-tuple formatting, universal-newline input translation, empty result stderr, retained request identity, one active slot, admission order, fixed deadlines, cancellation, cleanup and closed failure mappings are inherited unchanged from §§2–4 and §§7–8. Inventory requires all four exact id/support pairs, including `decision-layer-check` / `decision-layer-check-v1`, with `not-yet-supported` dispositions. Startup validates bounded metadata; source `--check-inventory` separately checks the literal canonical `AGG_VALIDATORS` identity set. Metadata grants no fifth route or desktop capability.

The helper's five mechanical checks remain exactly its current count, heading, appendix and paragraph-reference rules. Protected Elements requires 3–6 entries; Author Decisions 3–7; standard letters require exactly seven Control Questions and Appendix A/B/C headings; labeled body Must-Fix blocks need at least two matches to fixed reference patterns. Missing sections may warn rather than fail. Body override markers can downgrade errors to warnings under the unchanged helper. These mechanical results do not establish argument quality or evidence adequacy.

**Inherited policy limitation:** argument-DE detection searches the whole letter for five fixed markers, including appendices and fenced code. A marker only there can make Checks 3–4 skip, although policy prose describes body detection. This adapter preserves and tests that legacy behavior through the real JSONL route for exact Python-backed Bash parity. It does not establish semantic argument classification or repair the helper/policy discrepancy. That repair needs a separate decision and scope.

This candidate changes only the runner, runtime inventory, focused tests, this document and its changelog fragment. Public fixtures and invented text establish development-host behavior; signed desktop execution, native Windows process containment and complete validator qualification remain outstanding.

## 10. Bounded fifth-leaf amendment: author-facing-lint

Build status: implemented as a development-only fifth leaf under Fleet issue 750 and worker grant 6140263193, on released PR338 head `7c5236199fbc127236ea0c983c9f12b36ca0cc9e`. Its desktop disposition remains `not-yet-supported`; signed desktop execution, native Windows containment, full-validator parity and hosted qualification remain outstanding.

The sole new public literal is `author-facing-lint`. It selects private `--worker-author-facing-lint` and the explicitly named fixed sibling `letter_checks.author_facing_lint(text)` import. Inventory requires its exact `author-facing-lint-v1` mapping alongside the four earlier exact mappings. The shared v1 input limits, universal-newline translation, four-tuple formatter, id retention, one active slot, admission order, fixed deadlines, cancellation, two-second cleanup budget and closed failure mapping remain unchanged. The source checker still compares the actual canonical `AGG_VALIDATORS` literal; inventory metadata grants no dynamic route or desktop capability.

This helper is advisory. Its errors list is always empty, so a bounded warning result has exit 0, warnings followed by the exact OK line, and empty stderr. It scans body before the first level-1–4 Appendix heading. The inherited code-stripped, slug-boundary override matcher suppresses all warnings, including when the marker is blockquoted or unterminated; it does not validate HTML or rationale. Otherwise it scans body lines literally, including ordinary quoted and fenced examples, except lines whose left-stripped form begins with an HTML comment. It judges the first occurrence of each uppercase code key. Only its mechanical adjacent parenthetical, dash-led, or phrase-before-parenthesis descriptive-word tests exempt a code; they do not judge translation quality. Warnings repeat the matched code token and line number without surrounding prose. Skill-slug conventions remain outside this check.

The existing 32,768-byte encoded response ceiling applies to the full JSONL envelope, including id, validator and LF. A valid text can produce more than that because each warning repeats its code twice; a long numeric code or many distinct short codes yields `output_limit`, with no partial success or truncation. Bounded outputs retain exact Python-backed Bash bytes. No larger ceiling, new numeric-token limit or universal parity claim is introduced.

## 11. Bounded sixth-leaf amendment: ledger-check

Build status: implemented as a development-only sixth leaf under Fleet issue 756 and worker grant 6141103451, on released PR341 head `9da3a48e0defb0004ac14ae92ff02b436c4e9b19`. Its desktop disposition remains `not-yet-supported`; signed desktop execution, native Windows containment and full-validator qualification remain outstanding.

The public literal `ledger-check` selects only private `--worker-ledger-check` and the explicitly named sibling `letter_checks.ledger_check(text)` import. Inventory requires its exact `ledger-check-v1` mapping and `not-yet-supported` disposition alongside the five earlier exact pairs. The same bounded text, universal-newline translation, coordinator-owned id and validator, one active slot, admission order, five-second worker deadline, two-second cleanup budget, closed errors and canonical `AGG_VALIDATORS` set check apply. Inventory remains disposition metadata, never a dynamic dispatcher.

This helper alone returns `(exit_code, lines)`: an exact integer 0 or 1 and a list of strings. Its worker prints each line with a trailing LF, including empty lines, and returns empty stderr. The five required subsection names are checked in fixed diagnostic order within each recognized pass; headings may occur in any order. Missing headings in literal Pass 0 or 10 yield `NOTE:` while 00 and 010 are strict. A strict miss ends in an empty separator and `FAILED:` count; no recognized passes produce `WARNING:` and exit 1. These are mechanical heading checks, not proof of ledger content, evidence quality or structured findings. The four-tuple formatter for other leaves is unchanged.

Exact Python-backed Bash exit and UTF-8 stdout/stderr parity applies when the full encoded JSONL response fits 32,768 bytes. A valid ledger can generate a much larger result by repeating pass headings or long digit tokens. It reaps the worker before emitting one unavailable `output_limit` result, with no partial success. No response ceiling or input authority changes.

## 12. Session amendment: queue and EOF drain

Review of the six-leaf stack found that session-wide limits ended well-behaved clients (a 65th sequential request or 60 idle seconds was fatal) and that piped batches returned `busy` or `session_ended` instead of results. None of those limits came from the owner's admitted requirement, which is per-input and per-output ceilings, cancellation, no network, closed schemas, fail-closed unavailability and an inventory. This amendment removes the session frame, byte, wall-time and idle limits with their `session_limit` code, replaces the `busy` refusal with a first-in, first-out queue behind the one active worker, and drains active and queued work at clean EOF. Per-frame, text, response, five-second execution and two-second cleanup limits are unchanged.

The queue is held in coordinator memory and grows only with requests the client itself sends; each queued text is already bounded by the text limit. Cancelling a queued request removes it before it starts. Fatal errors and handled termination end the active and every queued request as `session_ended` when stdout is writable; transport failure cannot deliver them.

CI now runs `validator_runner.py --check-inventory` in the existing inventory-parity step, so an undispositioned registry change fails the hosted gate as the owner's done-check requires. `tests/test_ci_train_policy.py` carries the updated workflow digest. The runner test file stays local; it is not added to CI.
