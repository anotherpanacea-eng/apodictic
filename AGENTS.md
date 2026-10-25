# Agent workflow — apodictic

APODICTIC is solo-maintained (`anotherpanacea-eng`) but multi-agent: Claude,
Codex, and Antigravity sessions all contribute. This document records the
internal workflow they follow. External contributions are email-based — see
`CONTRIBUTING.md`; this file governs the maintainer's own agent sessions, not
outside PRs.

## Fleet / cross-repo context

This repo is one of four maintained together (all `github.com/anotherpanacea-eng`):
`setec-voiceprint` (producer · public · Python), `apodictic` (consumer + producer ·
public · Python — **this repo**), `setec-voicewright` (consumer · private · Python),
`APODICTIC-Gemini` (consumer · private · TS app).

**This repo's dependency contract (both directions):**
- **Consumes** `setec-voiceprint` via its normalized-entrypoint dispatcher
  (`setec run <surface> --json`), pinned in `setec-plugin.lock`, drift-gated offline
  in `tests/setec-contract/` (the weekly `.github/workflows/sync-setec.yml` draft
  auto-PRs the version bump). **Don't hand-edit the lock or the vendored fixtures — run
  `scripts/sync_setec.py`.**
- **Produces** `release-registry.json`, which `APODICTIC-Gemini` *pulls* (it vendors
  the registry and regenerates its UI from it); changing the capability catalog
  ripples to that app on its next weekly pull.

**Shared workflow:** spec → review → build → review → periodic merge train.
**Both reviews (spec and build) are subagent passes — iterate until everything is
fixed.** Ordinary code, docs, and tiny fixes all default to draft PRs. Periodically,
merge their exact reviewed heads into one disposable `train/` branch, clear that
combination once, and merge only the train. Merge commits, never squash; version
bumps, if any, are reviewed train-only commits made before the train freezes.
(Full detail below.)

**Cloud-reachable coordination hub** (added 2026-07-19):
[`anotherpanacea-eng/fleet-coordination`](https://github.com/anotherpanacea-eng/fleet-coordination)
carries the fleet's code-safe cross-machine layer — task handoff packets
(`handoffs/`), the live code-safe status board (`STATUS.md`), the portable
fleet briefing (`PROJECT-SUMMARY.md`), and the sanitized build/review
preflight. Unlike the Dropbox hub, **cloud threads can read it** — check its
`STATUS.md` and `handoffs/` before flagging missing cross-repo context. Hard
data boundary (CI-enforced leak gate): branch/commit refs, aggregates, and
whole-artifact hashes only — never corpus prose, per-unit identifiers,
private machine paths, or keys.

**Fuller cross-repo context** (backlog, topology, deep lessons) lives in the
maintainer's private fleet hub in Dropbox at `80-89 Projects/81 Software & tools/81.11 Repo fleet/`
(moved from the retired `Cowork/repo-fleet/` on 2026-10-11). Local agents reach it through the
Dropbox folder; cloud sessions reach it only when the Dropbox connector is attached. Never copy
private hub content into this repo. If you're a cloud session without the connector and need cross-repo
context beyond this section, flag it rather than guessing.

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
6. **Admit.** Keep the reviewed PR draft and admit its exact head to the next
   disposable train (see "PRs and merges").

### Review practices

The spec/code reviews (steps 2, 4) earn their keep when the reviewer does more than read for plausibility. These passes have caught real bugs that reasoning-about-the-code missed, plus one doc-hygiene discipline:

- **Hostile fixtures.** Construct inputs the spec and self-tests *don't* cover — wrong-shaped sidecars, colliding/lookalike filenames (a `*_Revision_Calendar_*` satisfying a `*_Revision_*` glob meant for the Report), empty/partial state, malformed-but-valid JSON, a field in a shape the spec merely documents (a bare-string `next_action`). Self-tests only test what the author already thought of; the worst bugs live in the inputs they didn't.
- **Run the combined validation gate first.** Step one of a code review is `python plugins/apodictic/scripts/validate.py --check-all` — the local equivalent of CI's ordered validator self-test + canonical-framework phases — not a proxy. A change applied to only one script copy (see "Platform parity") is green locally and CI-blind. (The full CI gate set is broader — also `release-generate.mjs --check`, `build-codex`/`build-antigravity --self-check`, `assemble-changelog --check`; run them when you touch generated/paired docs.)
- **Distrust count-shaped claims.** "2× findings," "nine rows removed," "total/exhaustive," "all N covered" — re-enumerate from scratch; never accept the number.
- **Flip the status when you build.** A build PR flips its spec doc's `**Status:**` line (and its ROADMAP entry) in the same PR. Status drift recurred across #66/#70/#74; check it by hand in review.
- **Re-sync the inventory surfaces when the registry moves.** When you change the signal-emitting audit registry (`audit-routing-table.md`) or the research modes (`commands/research.md`), re-sync the dashboards/matrix inventory in the same PR.

## Test value convention

Every test must justify its maintenance cost by protecting at least one of:
observable behavior, a public or consumer contract, a reproduced bug, a
safety/security property, or a stable architectural prohibition. Coverage,
test count, and "this is how the source is written" are not sufficient reasons.

Use this litmus test: **if behavior and contracts stay unchanged, could a
reasonable refactor make the test fail?** If yes, the test is probably asserting
implementation rather than behavior. Usually delete or rewrite tests that pin
source/AST shape, hashes of implementation files, symbol location, exact internal
inventories, workflow or documentation text, oversized internal snapshots, or a
mock/monkeypatch seam that production would not otherwise need. Prefer black-box,
metamorphic, adversarial, and bug-regression tests. Do not keep two tests that
protect the same failure at different fidelity unless each catches a distinct
regression class.

Static inspection is justified only when it enforces a stable **negative** property
that is impractical to observe dynamically--for example anti-Goodhart separation,
held-out isolation, no forbidden dependency/network path, a security boundary, or
canonical/generated parity. Such a test must name the prohibited coupling and
should not pin incidental lines, helper names, or file layout. Frozen fixtures are
appropriate for genuinely external compatibility contracts, not internal
refactoring receipts.

When deleting a test, inspect the production code for seams, wrappers, indirection,
or exported helpers that existed only to satisfy it; simplify those in the same
change when safe. Preserve or replace behavior coverage before deletion. In the PR,
state why each deleted class was low-value and report the behavioral checks that
remain.

**Monthly sweep.** Once per month, audit the suite for source-reading tests, exact
inventories/hashes, duplicate coverage, large brittle snapshots, and test-only
production seams. Classify candidates as KEEP / REWRITE / DELETE with a one-line
justification; there is no deletion quota. Make changes in a per-repo branch, run
the relevant behavioral checks, and open a draft PR. Never merge sweep findings
without review; after the required reviews and green checks, follow this repo's
normal merge policy.

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
3. **A chat brief** — for trivial changes that still land through a draft PR.

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

**Validators live in one place.** `validate.py`, `validate_canonical.py`, `preflight.sh`, and the Python validators live in `plugins/apodictic/scripts/`. Invoke the native dispatcher with Python 3.10+; children use that same interpreter. Plugin and root `validate.sh` are small optional POSIX compatibility launchers, with a named exit 127 if Python is missing. The old `validate.d` parts are removed. Root `scripts/` otherwise holds repository release/build tooling. Validator fixtures live in `tests/fixtures/validators/`. Keep canonical plugin files under 256 KiB and the folder at 512 files or fewer. Package generators exclude Python caches, verify native entries, and check the canonical source against these limits; the changelog stays at the repository root.


## Changelog

Don't edit `CHANGELOG.md` directly. Add one `changelog.d/<slug>.md` fragment per
change — a single freeform thematic `### ` section. `scripts/release.sh` assembles
the fragments into a dated `## vX.Y.Z` section at release time (and deletes them);
`scripts/assemble-changelog.mjs --check` gates fragment validity in CI. See
`changelog.d/README.md`.

## PRs and merges

- **Default every change to a draft PR.** Drafts start no CI.
- **Batch reviewed drafts into a `train/` branch** with `--no-ff` merges of their
  exact reviewed heads, mark the train PR ready, and merge it with a merge
  commit once CI is green. Never squash. Delete the train branch after merge.
- **Codex 5.5 is the standing PR reviewer; don't merge out from under it.** Make
  the obvious fixes, then let its pass run. If only one agent has reviewed or a
  comment is unresolved, hold.
- **`gh` OAuth workflow-scope merge block (public repo).** A PR that touches
  `.github/workflows/` can't be merged with the `gh` OAuth token (403 "refusing to
  allow an OAuth App to create or update workflow"). Use GitHub's merge button or
  the connector's merge-commit API instead.

### Branch naming

- `feat/<surface>` for new audits/modules
- `fix/<short-description>` for fixes
- `chore/<short-description>` or `docs/<short-description>` for ancillary work
- `codex/<short-description>` for Codex-authored proposals

### Standalone exception

A change that cannot wait for the next train may be marked ready on its own after
both reviews and local validation; CI then runs on it like a train.

## CI

`.github/workflows/ci.yml` runs on non-draft PRs only. The `validate` job on
`ubuntu-latest` byte-compiles `plugins/` + `scripts/` (syntax gate), validates that
the plugin / marketplace / release-registry manifests parse, runs the validator
self-tests (`validate.sh --self-test-all`) and canonical-framework checks
(`validate.sh --check-canonical`), and runs the generator/parity gates
(`assemble-changelog.mjs --check`, `release-generate.mjs --check`, both build
`--self-check`s) and the SETEC contract drift gate. Beside it, a
`validate-windows` job on `windows-latest` runs
`python plugins/apodictic/scripts/validate.py --check-all` with only Python on
`PATH`, so the gate cannot use Bash. A small pytest suite guards the `@claude`
workflow's safety boundaries and the native aggregate contracts. The `evals/`
fixtures are the behavioral ground-truth track. `.github/workflows/release.yml`
builds + publishes the per-host bundles on `v*` tags. Follow the fleet CI budget
rule (fleet-coordination `PATTERNS.md` §14) before adding a job, step or gate.

## Co-authorship

Commits authored end-to-end by one agent carry that agent's trailer; pair-
authored commits carry both. Example:

```
Co-Authored-By: Claude <noreply@anthropic.com>
```

## When this document is wrong

Update it. It's a working document, not a contract. The goal is for any future
agent session to read this file and know what shape the work should take.
