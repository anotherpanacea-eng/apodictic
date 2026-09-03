# Draft-first integration trains

**Status:** Spec — ready for independent review; unbuilt.
<!-- built-when: tools/check_merge_train.py -->

## Decision

APODICTIC will accumulate ordinary work as unarmed draft pull requests and
periodically clear a fresh, disposable `train/` branch.  The train is built from
the current exact `origin/main`, contains the independently reviewed constituent
heads as `--no-ff` merges, receives the repository's full hosted validation once,
and is the only PR merged for that batch.

This is repository policy and mechanically checked workflow behavior.  It does
not depend on a paid GitHub ruleset or on GitHub Merge Queue.  The existing
classic `main` protection may continue to require the `validate` context, but the
correctness boundary is the closed train inventory, independent exact-head
reviews, one full run, live receipts from that run, and a compare-and-swap
landing against the unchanged base.

## Why

The current workflow creates four hosted jobs for every non-draft PR and repeats
them after every synchronization.  It also repeats the same validation after a
merge to `main`.  The fourth job is only an aggregation runner: it checks the
three preceding conclusions but performs no repository validation of its own.
This is a poor cost shape for agent-authored work, where several draft PRs may be
refined during a week.

Drafts already suppress job execution, but convention alone leaves gaps:

- marking an ordinary branch ready immediately spends a full run;
- automated SETEC sync PRs are created ready by default;
- unrelated label activity can duplicate or cancel a clearance run;
- a green check name does not prove that every job tested the current PR's exact
  base, head, and synthetic merge;
- independently merging constituents repeats CI and can land a combination that
  was never tested.

The train model closes those gaps while preserving full validation at the
integration boundary.

## Cost shape

The PR workflow becomes PR-only: remove `push: main`.  A successful train landing
therefore does not start a second copy of the same validation.

The three current validation lanes are consolidated into one required
`validate` job.  It retains every existing command in deterministic order:

1. byte-compile and manifest parsing;
2. version parity and research-reliability self-tests;
3. changelog, status, inventory, registry-generation, host-build, and SETEC
   contract checks;
4. validator self-tests; and
5. canonical-framework validation.

The present fourth aggregation runner is removed.  The consolidated job is
exactly `ubuntu-latest` with `timeout-minutes: 10`; recent successful runs use
roughly one minute across the three substantive lanes, so the existing per-lane
hang cap remains ample after consolidation.  The existing protected context name
`validate` remains unchanged, so no ruleset or branch-protection migration is
required.  Consolidation trades a small amount of wall-clock parallelism for
fewer runner startups, less hosted compute/queue noise, and fleet-policy
consistency.  APODICTIC is public, so its standard GitHub-hosted jobs do not
consume plan minutes; actual billed-minute savings accrue in the private fleet
repos.  No test, generator, mirror check, consumer-contract check, or
canonical-framework gate may disappear.

Release, release-readiness, and scheduled SETEC synchronization remain separate
workflows with their existing triggers and permissions.  Before updating its
fixed PR branch, the sync workflow uniquely resolves any open same-repository
`chore/sync-setec-contract` → `main` PR (zero or one only), removes exact
`ci-ready` when present, converts a ready PR back to draft, and reads the PR back
as draft with no `ci-ready`; ambiguity or failed readback refuses before a push.
These `GITHUB_TOKEN` state mutations do not themselves create downstream Actions
workflow runs, so the pre-push state proof is mandatory rather than relying on a
later cancellation occurrence.

The updater then upgrades from `peter-evans/create-pull-request@v6` to a reviewed
full commit SHA from v7 and uses `draft: always-true`, the v7+ create-and-update
mode.  After the updater, the workflow again uniquely resolves any open fixed-
branch PR, forces it to draft when necessary, removes exact `ci-ready` when
present, and reads back draft/no-label state.  This post-action enforcement is
mandatory even when the updater reports no content change, because
`draft: always-true` only re-drafts a PR that the action actually updates.  The
fixed sync branch is also explicitly excluded from standalone
authorization even if a human later adds `ci-ready`.  Pre-disarm, authorization
exclusion, `always-true`, and post-action enforcement are independent belts;
automation receives no CI bypass.

## PR state machine

Every constituent defaults to draft.  Draft workflow occurrences may exist as
completed/skipped metadata, but no hosted job may start.

A same-repository PR is armed only in one of two ways:

1. **Train:** its head branch starts with the exact prefix `train/`, it is not a
   draft, and the action is explicitly one of `opened`, `synchronize`, `reopened`,
   or `ready_for_review`.
2. **Standalone exception:** it is not a train, is not the fixed
   `chore/sync-setec-contract` automation branch, it is not a draft, and it
   carries the exact `ci-ready` label.  It arms only for `opened`, `synchronize`,
   `reopened`, or `ready_for_review`, plus a `labeled` event whose event label is
   exactly `ci-ready`; unrelated label events never start work.

Fork PRs may use only the standalone path; a fork cannot obtain train authority
by naming its branch `train/*`.  Converting any candidate to draft revokes
authorization.  Removing `ci-ready` revokes standalone authorization.

The workflow event list is closed to `opened`, `synchronize`, `reopened`,
`ready_for_review`, `converted_to_draft`, `labeled`, `unlabeled`, and `closed`.  Its
bounded run name records PR number, action, same-repository train classification,
and whether the event label is exactly `ci-ready`; it never reflects arbitrary
branch or label text.

Concurrency has a closed activity table.  The four armable non-label actions
share the canonical clearance group for a PR and cancel an obsolete clearance.
Adding the exact `ci-ready` label also uses that group.  `converted_to_draft`,
`closed`, and removal of exact `ci-ready` use the canonical group so they cancel
in-flight work but remain unarmed.  Every train label event and every unrelated
standalone label event gets a unique run-id-suffixed noise group and remains
unarmed; such noise can neither start work nor cancel clearance.  Tests cover
add, remove, unrelated label, train-label, head synchronization, draft conversion,
closure, and reopening transitions.  The automated sync pre-disarm is separately
state-verified because `GITHUB_TOKEN` mutations do not create downstream runs.

The repository creates and reads back one exact `ci-ready` label:

> Explicitly authorize hosted CI for a non-train standalone PR

## Constituent admission

A PR may enter a train only when all of the following are recorded:

- PR number, title, exact 40-hex remote head, and dependency order;
- the written contract for non-trivial work;
- independent generic and fleet-posture reviews of that exact diff, with every
  P1/P2 repaired and re-reviewed;
- scope-appropriate local validation plus the combined repository gate
  `bash scripts/validate.sh --check-all` when applicable;
- clean `git diff --check`, no unresolved review thread, no active owner
  mutation, and no uncommitted integration fix; and
- preserved SETEC consumer boundaries, mirrored-script parity, generated-tree
  discipline, and private-data exclusions.

The train PR names both **Included** and **Explicitly excluded** sets.  Silence is
not disposition.

## Closed train construction

1. Fetch and freeze exact `refs/remotes/origin/main` as `BASE` in a clean,
   isolated worktree.
2. Create a new disposable `train/<date>-<slug>` branch from `BASE`.
3. Merge each admitted remote head with `--no-ff` in recorded order.  Never
   squash, cherry-pick, or reconstruct an advertised constituent.
4. Record each resulting two-parent merge commit in an external JSON inventory.
   A clean merge's tree must equal Git's independently computed automatic merge
   tree for those exact parents.  All object resolution and merge plumbing runs
   in a sanitized Git environment that drops ambient `GIT_*` variables and
   restores only fixed safe values (`GIT_CONFIG_GLOBAL` to the platform null
   device, `GIT_CONFIG_NOSYSTEM=1`, `GIT_NO_REPLACE_OBJECTS=1`,
   `GIT_OPTIONAL_LOCKS=0`, and `GIT_TERMINAL_PROMPT=0`).  Any graft file or
   replacement ref refuses the train.
5. A real conflict may be resolved only inside that constituent merge commit.
   The resolution may change only Git-reported conflict paths and receives its
   own tests plus independent exact-commit review.  Conflict-marker width is
   derived from Git's automatic conflict blob, including a versioned
   `conflict-marker-size` attribute, so non-default marker widths cannot evade
   detection.  A conflict path left tree-identical to Git's automatic
   intermediate entry is valid only when that entry is byte-identical to a
   materialized parent side (including deletion); otherwise the synthetic blob
   refuses.  Modify/delete conflicts are covered explicitly.  No final conflict
   path may retain a complete start/separator/end marker triplet.
6. A one-parent train-only commit is permitted only for a separately described,
   reviewed integration adjustment.  It cannot hide a conflict repair or replace
   a constituent.
7. A standard-library checker validates the entire first-parent chain against
   schema `apodictic-merge-train/1`.  It rejects moved base, replacements/grafts,
   malformed or duplicate objects, wrong parents/order, omitted or extra commits,
   base-contained heads, octopus merges, false clean/conflict claims, unbounded
   conflict edits, and a head commit carrying a CI-skip instruction.  At least one
   constituent step is mandatory: an empty inventory or a train containing only
   train-only commits refuses.
8. Run the combined local validation and repository gates, then obtain generic
   and fleet-posture reviews over the exact `BASE..HEAD` train diff.
9. Open the train as draft with its endpoints, ordered inventory, reviews,
   integration resolutions, local receipts, exclusions, and landing protocol.

## Exact merge binding

The first repository-aware action in the billed `validate` job, after a default
depth-1 checkout and before language setup or validation, runs a standard-library
binding check.  It requires:

- the clean checkout's exact `HEAD` equals `github.sha`;
- `HEAD` is a two-parent merge commit whose parent header is read directly with
  `git cat-file -p HEAD`, without resolving or downloading shallow parent
  objects;
- parent 1 is the PR's advertised base SHA;
- parent 2 is the PR's advertised head SHA;
- all three advertised ids are nonzero full 40-hex values; and
- job name, run id, and run attempt are bounded canonical values.

It prints one canonical JSON receipt binding repository, workflow run/attempt,
job, base, head, and synthetic merge.  A missing or malformed binding refuses
before substantive work.

## Promotion and hosted clearance

Immediately before promotion:

1. fetch and require live `origin/main == BASE`;
2. read the train and every constituent from GitHub and require exact heads,
   target `main`, expected draft/disposition, same-repository identity, and no
   unresolved review thread;
3. rerun the closed-topology checker and `git diff --check`; and
4. require independent generic and fleet-posture approval of exact `BASE..HEAD`.

Make the frozen train ready once.  Any head change invalidates the clearance and
requires returning to draft, rebuilding/reviewing as needed, and promoting the
new exact head.

The single `validate` job must complete successfully and non-skipped on the
unchanged exact base/head synthetic merge.  A live receipt verifier reads the PR,
workflow runs/attempts, job conclusions, and job log through authenticated `gh`.
It binds exact repository, PR number, current base ref and SHA, workflow path
`.github/workflows/ci.yml`, `pull_request` event, head SHA, same-repository/head
branch, and bounded activity class.  It chooses the newest run for that identity
and that run's latest attempt, then requires exactly one completed-success,
non-skipped `validate` job with exactly one valid receipt.  A green badge without
the in-job receipt is insufficient.  Any later failed, cancelled, or pending
clearance occurrence on the head invalidates an earlier green.  Only a verified
completed/skipped train-label or unrelated-label noise run may be ignored, and
only when its exact `validate` record is also completed/skipped.  Draft
conversion and `ci-ready` removal revoke current authorization even if an older
green exists; removal's canonical concurrency occurrence cancels an in-flight
standalone clearance without arming replacement work.

## Landing without a paid ruleset

Immediately before landing, repeat the live base/head/constituent read-back and
receipt verification.

Use GitHub's merge-commit path with an expected-head guard when it reliably
honors the protected current base.  If the OAuth workflow scope blocks a PR that
changes `.github/workflows/ci.yml`, use the tested-synthetic-merge fallback:

1. fetch the PR's tested synthetic merge ref;
2. require its parents are exact `BASE` then exact train `HEAD`;
3. construct a local two-parent merge with the same tree and a commit message
   that contains no recognized CI-skip instruction;
4. re-read all live state; and
5. update `main` with `--force-with-lease=refs/heads/main:<BASE>`.

The lease is compare-and-swap, not permission to rewrite history.  The same
sanitized Git environment is mandatory through synthetic-ref verification and
local commit construction; ambient `GIT_DIR`, `GIT_WORK_TREE`, object-directory,
alternates, namespace, index, and config-injection variables cannot rebound the
operation.  Replacement refs and grafts are refused.  A moved base
must reject and force a rebuild/retest.  After landing, prove `main` contains the
train and every constituent exact head.  Let GitHub mark unchanged constituent
PRs indirectly merged; a constituent whose head moved is new work and remains
open.  Delete the remote train branch, remove its clean disposable worktree, and
verify no post-merge `main` CI run was created.

## Repository-policy reconciliation

The build updates `AGENTS.md`; this spec cannot coexist with its current
PR-per-change auto-merge and direct-main exceptions.  The authoritative policy
must say:

- every ordinary code, docs, and tiny-fix PR defaults to draft and accumulates
  for a periodic train;
- docs-only and one-line corrections do not receive a direct-main bypass;
- dual-review auto-merge applies only to a frozen, cleared train or an explicitly
  `ci-ready` standalone exception; and
- no constituent is promoted or merged separately once admitted to a train.

The same edit removes stale descriptions of CI as parallel validator and
canonical-framework jobs from `AGENTS.md` and `.github/workflows/ci.yml`, because
the new topology is one ordered job.  The synchronization workflow description
must say it opens or updates a **draft** bump PR, never imply a ready PR.

The pull-request template adds draft-first guidance plus train-only sections for
Included, Explicitly excluded, exact base/head, ordered inventory, conflict or
train-only fixes, local/review receipts, and promotion/landing protocol.  The
template must not imply that an ordinary constituent should be made ready merely
because its local checks pass.

## Repository-policy enforcement

The build includes behavior-focused negative tests for:

- every draft and unauthorized ready event producing a skipped job;
- exact train/standalone authorization, fork refusal, and label-noise closure;
- PR-only triggering, bounded run metadata, the closed concurrency state table,
  permissions, one exact `validate` job, exact runner/10-minute timeout,
  binding-first order, and the complete existing command inventory;
- exact `validate` job keys, rejecting matrix/strategy, services, container,
  reusable-workflow `uses`, `continue-on-error`, or any hidden second job; closed
  normalized step order, action inputs, and run-command bodies;
- extension-aware workflow inventory over both `.github/workflows/*.yml` and
  `*.yaml`, requiring exactly `ci.yml`, `release.yml`,
  `release-readiness.yml`, and `sync-setec.yml` and refusing a fifth workflow;
- unchanged normalized digests and exact trigger/permission/job topology for
  `.github/workflows/release.yml` and
  `.github/workflows/release-readiness.yml`;
- exact final trigger/permission/job/step/command topology for
  `.github/workflows/sync-setec.yml`, whose intended changes are the ordered
  pre-updater disarm/readback step, the reviewed v6→full-SHA-v7 action upgrade,
  `draft: always-true`, and ordered post-updater draft/no-label enforcement;
  tests model a ready+labeled existing PR including the no-content-update case,
  prove no branch update occurs before successful disarm/readback, prove the
  pinned action supports `always-true`, and prove the fixed sync branch cannot
  arm;
- malformed, moved-base, reordered, substituted, extra-step, replacement/graft,
  false-resolution, custom-width conflict-marker, synthetic automatic-entry,
  modify/delete, graft/replacement, and skip-instruction train failures;
- empty inventory and only-train-step shallow-population failures;
- ambient Git-environment rebound attempts covering `GIT_DIR`, `GIT_WORK_TREE`,
  `GIT_OBJECT_DIRECTORY`, alternates, namespace/index, and config injection;
- shallow object-store binding acceptance; malformed/mixed/stale/wrong-workflow
  live receipts, latest-attempt selection, and arming-state revocation; and
- the happy path for clean and bounded-conflict trains.

Tests may pin workflow topology and commands because this is a stable negative
cost/security boundary, not incidental implementation structure.  They must
normalize comments and whitespace where those do not affect behavior.

## Acceptance criteria

- The spec receives independent review before implementation.
- `ci-ready` is created and read back without arming any PR.
- Existing open PRs, if any appear during the build, remain draft/unarmed and are
  either reviewed into the rollout train or explicitly excluded.
- The implementation receives independent generic and fleet-posture review at
  its final exact head.
- Local policy/tool self-tests, `bash scripts/validate.sh --check-all`, release
  digest, status-drift, mirror, generated-build, and `git diff --check` gates pass.
- `AGENTS.md` and `.github/pull_request_template.md` are reconciled to the
  draft-first/one-train policy with no direct-main or constituent auto-merge
  contradiction.
- Repository and workflow prose contains no stale parallel-CI or ready sync-PR
  description.
- `changelog.d/draft-first-integration-trains.md` records the repository-policy
  and CI behavior change.
- A draft policy PR creates one skipped `validate` record and no hosted runner.
- A fresh rollout train is promoted once; its one `validate` job and live receipt
  pass on an unchanged base/head; the train lands as a merge commit.
- Every admitted constituent head is on `main`, no duplicate post-main CI runs,
  and the disposable remote train branch is removed.
