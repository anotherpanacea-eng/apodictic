# Existing audit-fixture confirmation

Status: completed collection and model scoring; mixed outcomes, not an all-pass confirmation. Eight fresh reader contexts produced eight sealed responses, followed by one separate fresh model scorer. Runtime model assignments were unavailable; no model-comparison claim follows. Source head: `66c59bea3091e1e6990aafc3d86418da44e3a414`.

## Scope and provenance

The frozen design comprises two excerpt-level AI-prose scans, three explicitly activated tag diagnoses, and three separate automatic-trigger checks of a shared baseline. Positive tag cases do not establish automatic activation performance. The three baseline checks reuse one passage and are not three independent literary samples. Inputs are registered synthetic fixtures; expected findings are authored fixture expectations, not editorial truth. No source, fixture, prompt or key bytes are republished separately.

Eight reader contexts and one separate scorer context were used, with no replacement readers/scorers or paid APIs. Instruction blinding constrained permitted reads; it did not provide technical filesystem isolation. Full manuscript context, author/market metadata, omitted companion references and upstream passes remained unavailable. No automatic acceptance or promotion follows from model agreement.

## Model-scored findings

The following describes the preserved scorer assessment, not a second editorial judgment or a human scorecard:

- The clean-control principal check and separate earned-negation guardrail agreed with the authored expectations. All three baseline trigger checks returned dormant without a forced diagnostic audit.
- AI-prose AIC-2 and AIC-6 were detected with lower severity than authored expectations; AIC-4 and the umbrella finding were partial. Canonical scope/severity restrictions and the authored AIC-8 naming conflict remain explicit.
- Queer-romance pronoun ambiguity, trope review and protected community texture were detected; audience-orientation findings had qualifications about identity and intended audience.
- Cozy cruelty, trapdoor, recovery and fit expectations were detected; the prop/skin expectation was missed, with canonical ambiguity preserved.
- Philosophical PH-7 was detected, PH-4 was partial without firing, and PH-1/PH-5 were missed. Partial fit disagreed with authored Mismatch while complying with the canonical Partial-or-lower ceiling.

All 31 scorecard table rows are retained in SCORES.json, including activation, composite-control and record-only observations. Exactly 30 rows use the frozen categorical vocabulary: 23 found-with-evidence, four partial and three missed. One record-only row uses the scorer's literal `not-assessable for target coverage` and is excluded from categorical counts without recoding. These heterogeneous rows are not independent trials; the counts are neither accuracy nor a pass rate. Fixture agreement, severity/fit agreement and canonical compliance remain separate verbatim cells. Quotation-fidelity defects and unexpected findings remain in the scorecard; underlying shorter exact fragments do not repair longer inaccurate quotations.

## Publication and conservation

The eight files under outputs/ are byte-exact sealed reader responses. MODEL-SCORECARD.md is an explicitly disclosed mechanical publication projection, not the byte-exact original raw scorecard. Only original lines 3-21, the entire private provenance/custody section containing agent/task identifiers, were removed. Every scoring section and all 31 scored rows remain unchanged. The private original is 35,464 bytes, SHA-256 `186e80ba6672b7cfc1a04548a3284afee7f912deb329d74628166ba1c6c9f7ad`. RUN-MANIFEST.json records original/projection hashes, removed-byte hash, range, source/preparation anchors, custody timestamps and hashed task identities. Original scorecard references to `raw/<packet>.md` correspond to this package's `outputs/<packet>.md`.

The scorer reported one oversized write command failed before execution, followed by a successful file write. No replacement scorer or reader rescoring occurred. The failed tool payload was not independently compared. The scorer also records a failed Python launcher attempt followed by quotation checks in PowerShell. These are operational limitations, not evidence repairs.

SCORES.json is a deterministic extraction of every Markdown score-table data row, preserving its full original line, line number, individual cells and table header. Only exact categorical statuses contribute to counts; no outcome interpretation, normalization or threshold is added. The verifier regenerates the entire ledger and compares it for equality, detecting missing, duplicated, reordered or edited rows/cells and changed aggregate counts.

## Verification and limits

Run `python evals/results/audit-fixture-confirmation-20260922/verify_package.py` from the repository root. Default verification checks package inventory, eight raw-output hashes/custody lengths, scorecard/ledger hashes, full mechanical row conservation, public source/reference hashes and byte-preserving extraction. It checks the declared frozen source head and source bytes, not current Git HEAD equality: this result package is a later commit by design. UTF-8 fixture bytes after the first standalone `---` delimiter and its terminating newline are retained exactly, including blank lines, internal headings and source newline convention.

Default verification does not reconstruct full prompt bytes: private templates and dispatch wrappers are deliberately not published. Optional `--private-run DIRECTORY` verifies the preparation manifest and all frozen artifact hashes, exact packet/template/dispatch-wrapper hashes, reader-seal hash and all eight sealed response/binding records joined to published bytes, hashed task/response identities and custody metadata, and exact original-to-published scorecard transformation without copying private evidence. Hash verification does not independently rerun prompt construction or prove wrapper execution. Without private evidence, original-scorecard redaction provenance and exact prompt bytes remain unverified; only the published evidence is directly checked. Hashes are custody evidence, not independent authentication of the operator or model.

This bounded synthetic run does not establish full plugin execution, general editorial validity, real-manuscript precision/recall, model-authorship detection, manuscript readiness or a revised production rule. No keys, thresholds, references or fixtures were changed in response to the outcomes.

Package-author validation: default and private-evidence verification passed. Five disposable mutation checks refused a missing reader output, changed raw bytes, a dropped score row despite an updated artifact hash, an altered score cell despite an updated artifact hash, and a pending reader census. These checks test conservation and completeness, not editorial correctness.

Repository validation limit: the combined gate passed 82 of 84 self-tests. The two contract-hash/check failures require unavailable `shasum` and were independently reproduced at clean base `66c59be`; all subsequent canonical checks passed. An explicit Python 3 wrapper selected the Python 3.12 interpreter for the reported run; an earlier invocation without Python 3 did not constitute a valid gate run. This is not a fully green combined gate.

Private-custody regression checks also refused a changed published raw byte with both public hashes updated while private evidence stayed unchanged, and separately refused altered public task-identity and response-identity hashes.
