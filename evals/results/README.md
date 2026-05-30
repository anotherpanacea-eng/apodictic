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
