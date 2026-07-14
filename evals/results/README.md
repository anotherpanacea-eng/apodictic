# Eval Results

Run outputs from eval and benchmark runs (editorial letters, `Argument_State.md`,
companion-module artifacts, scoring sheets).

**This directory is gitignored by default.** Everything here is ignored except
this README (`evals/results/*` + `!README.md` in [`.gitignore`](../../.gitignore)).
Run outputs may contain private-fixture text or model artifacts that the
fixture-provenance policy does not permit in-repo, so the safe default is: they
stay local.

## Committing a permitted result

A result may be committed **only** when the fixture's provenance policy permits
it (synthetic or public-domain fixtures; see
[`../fixtures/argument-benchmark/README.md`](../fixtures/argument-benchmark/README.md)
and the local-only `docs/eval-harness-spec.md §Fixture Provenance Policy`). To
commit a permitted output, force-add it past the ignore rule:

```bash
git add -f evals/results/<path-to-permitted-output>
```

Joshua-authored material and any private/third-party fixture output is **never**
committed, regardless of location.

## Reconstructable benchmark packages

A permitted benchmark evidence package should contain only the artifacts needed
to audit the result without republishing its inputs: a run manifest with prompt
and output hashes, raw model outputs, tidy scores, the human scorecard, and a
stdlib verifier. Do not package prompts, provider stderr, fixture/source bytes,
credentials, or private run state.

The fiction M2a Terra/Opus package follows that form at
`fiction-m2a-20260714-terra-opus/`. Its verifier checks the committed outputs and
score exclusions directly, then reconstructs prompt bytes from locally available
registered fixtures without copying those bytes into the package:

```bash
python3 evals/results/fiction-m2a-20260714-terra-opus/verify_package.py
```
