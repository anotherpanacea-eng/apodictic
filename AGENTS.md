# Agent workflow — apodictic

APODICTIC is solo-maintained (`anotherpanacea-eng`) but multi-agent: Claude,
Codex, and Antigravity sessions all contribute. This document records the
internal workflow they follow. External contributions are email-based — see
`CONTRIBUTING.md`; this file governs the maintainer's own agent sessions, not
outside PRs.

## The flow

```
spec  →  review  →  write  →  review  →  fix  →  merge
            ▲                    ▲
         reviewer             reviewer
```

1. **Spec.** What the change should do. Strategic/scheduled work lives in
   `ROADMAP.md`; non-trivial ad-hoc work gets a GitHub Issue (see below);
   trivial work can be a chat brief.
2. **Spec review.** A second agent surfaces gaps, dependency issues, or scope
   creep before writing starts.
3. **Write.** One agent implements against the canonical source in `plugins/`
   (the Claude plugin). Never hand-edit `codex/` or `antigravity/` — those are
   generated and no longer committed (see "Platform parity"). Don't edit the
   changelog directly either — add a `changelog.d/<slug>.md` fragment (see
   "Changelog").
4. **Code review.** The other agent reads the diff and flags issues.
5. **Fix.** The writing agent applies fixes.
6. **Merge.** Via PR + merge commit (see "PRs and merges").

### Review practices

The spec/code reviews (steps 2, 4) earn their keep when the reviewer does more than read for plausibility. Three passes that have caught real bugs reasoning-about-the-code missed:

- **Hostile fixtures.** Construct inputs the spec and self-tests *don't* cover — wrong-shaped sidecars, colliding/lookalike filenames (a `*_Revision_Calendar_*` satisfying a `*_Revision_*` glob meant for the Report), empty/partial state, malformed-but-valid JSON, a field in a shape the spec merely documents (a bare-string `next_action`). Self-tests only test what the author already thought of; the worst bugs live in the inputs they didn't.
- **Run the real CI command first.** Step one of a code review is `bash scripts/validate.sh --check-all` — what CI actually runs — not a proxy. A change applied to only one script copy (see "Platform parity") is green locally and CI-blind.
- **Distrust count-shaped claims.** "2× findings," "nine rows removed," "total/exhaustive," "all N covered" — re-enumerate from scratch; never accept the number.

## Where work comes from: roadmap, briefs, and Issues

Every change implements from a written contract, never from an unscoped
instruction like "improve the argument audit." Agents are prone to
plausible-adjacent work, and this plugin's audit surface is wide enough to make
that easy. The contract comes from, in order of formality:

1. **A `ROADMAP.md` item** — strategic/scheduled work; the entry is the brief.
2. **A GitHub Issue** (`Task brief` template: Goal / Acceptance criteria /
   Out of scope / Constraints) — the home for non-trivial ad-hoc work that
   isn't on the roadmap. The acceptance criteria are what the second reviewer
   checks the diff against; the PR closes the Issue (`Closes #N`).
3. **A chat brief** — for trivial changes that also qualify for direct push.

Roadmap and Issues do different jobs and should not duplicate each other: the
roadmap is strategic and narrative; an Issue is one bounded work order with a
definition of done. Diagnostic-flag constraints — name the flag, include a
false-positive warning, keep the diagnostic/rewrite firewall (`CONTRIBUTING.md`
→ Style) — belong in an Issue's acceptance criteria where the reviewer enforces
them, not only in a comment the review might skim past.

## Platform parity

`plugins/` is canonical (the Claude plugin). `codex/` and `antigravity/` are
**generated** by `node scripts/build-codex.mjs` / `build-antigravity.mjs` — do not
edit them by hand. As of GitHub #52 (Option B) the generated trees are **no longer
committed**: they are `.gitignore`d and published as release assets
(`apodictic-codex-marketplace.zip`, `apodictic-antigravity.zip`, `apodictic.plugin`)
by `.github/workflows/release.yml` on each `v*` tag. So feature PRs touch only
`plugins/` (and `changelog.d/`) — there is no parity tree to regenerate and commit.

CI verifies the generators instead of committed copies: `release-generate.mjs
--check` (registry-derived docs) and `build-codex.mjs --self-check` /
`build-antigravity.mjs --self-check` (regenerate in temp + validate). `release.sh`
runs the same self-checks via `release-verify.mjs`.

**Separate gotcha — the dual script mirror (committed, not generated).** `validate.sh`
and every Python validator exist in **two committed copies**: `plugins/apodictic/scripts/`
(canonical) and root `scripts/` (**what CI runs**, per `.github/workflows/ci.yml`). These
are *not* generated like `codex/` — they must be mirrored **by hand, byte-identical**, or
a validator/engine change passes locally while CI runs the stale copy blind to it. Sync the
copies by hand (`cp`), then verify with **`validate.sh check-mirror`** — it asserts the shared
mirrored set (`validate.sh`, `preflight.sh`, every `*.py`) is byte-identical and is wired into
`--check-all`, so drift is now CI-blocking. (It only *detects* drift; it never auto-syncs — the
by-hand `cp` stays deliberate. Sync as the **last** step before `--check-all`, else its own
`validate.sh` edit shows as `DIFFER: validate.sh` until both copies match.) (Schemas/manifests in
`plugins/apodictic/schemas/` are single-sourced — resolved from either script dir — so they
don't need mirroring.)

## Changelog

Don't edit `changelog.md` directly. Add one `changelog.d/<slug>.md` fragment per
change — a single freeform thematic `### ` section. `scripts/release.sh` assembles
the fragments into a dated `## vX.Y.Z` section at release time (and deletes them);
`scripts/assemble-changelog.mjs --check` gates fragment validity in CI. See
`changelog.d/README.md`.

## PRs and merges

- **Default to PR-per-change with a merge commit** (`gh pr merge <N> --merge`),
  not squash — this preserves the spec-review-fix structure on `main`.
- **Delete the branch on merge** (`--delete-branch`).
- **Bump the version at merge, not in the PR** — open PRs merge in unknown
  order. Version + `changelog.md` follow the patch/minor/major rules in
  `CONTRIBUTING.md`.

### Branch naming

- `feat/<surface>` for new audits/modules
- `fix/<short-description>` for fixes
- `chore/<short-description>` or `docs/<short-description>` for ancillary work
- `codex/<short-description>` for Codex-authored proposals

### When to skip the PR

Direct push to `main` is fine for typo fixes, `changelog.md` touch-ups, and
single-line non-behavioral corrections. Anything that changes diagnostic
behavior, output format, thresholds, flag definitions, or pass logic lands via
PR.

## CI

`.github/workflows/ci.yml` byte-compiles `plugins/` + `scripts/` (syntax gate),
validates that the plugin / marketplace / release-registry manifests parse, runs
the validator self-tests + canonical-framework gate (`validate.sh --check-all`),
and runs the generator/parity gates (`assemble-changelog.mjs --check`,
`release-generate.mjs --check`, both build `--self-check`s). There is no pytest
suite — the plugin is prompt/skill-based; the `evals/` fixtures are the behavioral
ground-truth track. `.github/workflows/release.yml` builds + publishes the per-host
bundles on `v*` tags.

## Co-authorship

Commits authored end-to-end by one agent carry that agent's trailer; pair-
authored commits carry both. Example:

```
Co-Authored-By: Claude <noreply@anthropic.com>
```

## When this document is wrong

Update it. It's a working document, not a contract. The goal is for any future
agent session to read this file and know what shape the work should take.
