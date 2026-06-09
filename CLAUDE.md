# CLAUDE.md — working notes for this repo

Project memory for APODICTIC (a developmental-editing plugin: LLM-followed skill specs + Python validators). Auto-loaded each session.

## Adversarial review practices

Learned across the Project Addressability arc (Increments 1–4). When reviewing a build — your own or another agent's — run these as explicit passes. They caught the bugs that reasoning-about-the-code missed; the self-tests only test what the author already thought of.

1. **Hostile fixtures.** Spend one pass building inputs the spec and self-tests *don't* cover: wrong-shaped sidecars, colliding/lookalike filenames (e.g. `*_Revision_Calendar_*` satisfying a `*_Revision_*` glob meant for the Report), empty/partial state, malformed-but-valid JSON, a field in a shape the spec merely documents (a bare-string `next_action`). The two worst bugs in the arc were exactly this class and only a from-scratch hostile input found them.
2. **Run the real CI command first.** Step one of any build review is `bash scripts/validate.sh --check-all` — the command CI actually runs — not a proxy or a single validator. A change applied to only one script copy (see gotcha below) is green locally and CI-blind.
3. **Distrust count-shaped claims.** "2× findings," "nine rows removed," "total / exhaustive," "all N covered" — make the reviewer *enumerate from scratch*, never accept the number. The nine-row-removal and the lifecycle-node totality checks held only because they were re-counted, not trusted.

## Build gotcha — the dual script mirror

`validate.sh` and every Python validator exist in **two committed copies**: `plugins/apodictic/scripts/` (canonical) and root `scripts/` (**what CI runs**, per `.github/workflows/ci.yml`). Any validator/engine change must be mirrored to **both, byte-identical**, or CI passes while being blind to the change. Verify with `diff -q scripts/<f> plugins/apodictic/scripts/<f>`. Schemas/manifests in `plugins/apodictic/schemas/` are single-sourced (resolved from either script dir), so they don't need mirroring.

## Validator culture

Adding a validator means: the Python module + its `validate.sh` case + a `--self-test` + registration in the command list and `AGG_VALIDATORS` + bumping the hard-coded `N/N` count strings (and the `ci.yml` comment) + mirroring to root `scripts/`. `--self-test-all` must report `N/N`; `--check-all` adds real-file invariants. A new mechanical artifact gets a JSON schema in `plugins/apodictic/schemas/` and (where the repo has one) a canonical worked example gated by `--check-all`.
