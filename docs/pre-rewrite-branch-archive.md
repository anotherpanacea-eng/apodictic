# Pre-rewrite branch lineage: archive and prune

**Status:** tooling shipped (`tools/archive_and_prune_branches.sh`); the remote
prune is a one-time manual run.

## The finding

This repo's `main` history was rebuilt around 2026-07-06. `main` has **seven
root commits**, all dated that day, and reaches nothing earlier:

```
git rev-list --max-parents=0 origin/main     # seven roots, all 2026-07-06
```

Nineteen branches still descend from the **original** root `c3cb118`
("Initial release: APODICTIC v0.4.15", 2026-02-20). They share **no common
ancestor** with `main`:

```
git merge-base origin/main origin/claude/phase-5-plumbing   # empty, exit 1
```

Two consequences worth not re-deriving:

1. **They can never enter a merge train.** A train is `--no-ff` merges of
   reviewed heads onto a shared base (`AGENTS.md` § PRs and merges). With no
   merge base, a merge would apply an unrelated tree — the diffs run to ~100k
   deletions — rather than integrate a change. These are a severed lineage, not
   stale PRs.
2. **They hold the only copy of the pre-2026-07-06 history** — 795 commits.
   Deleting the refs makes those commits unreachable and eventually
   collectable.

## What is and isn't stranded on them

Nothing pending. Measured against `main`, the two most recent pre-rewrite
branches carry only 16 and 5 files `main` lacks, and each is accounted for:

| Left behind | Why it isn't loss |
| --- | --- |
| 10 `changelog.d/*.md` fragments | consumed and deleted at release assembly, by design |
| `op-ed-warrant-leap`, `policy-brief-uncompared` fixtures | present in `main`, restructured into `broken/` + `clean/` pairs |
| `tests/skill-registration/test_content_advisory_registration.py` | superseded by `meta_lint.py`'s M1–M8 registration checks |
| `apodictic.blind_spot_ranking.v1.schema.json` | no counterpart, but `main` passes `schema-coverage` with no orphan or phantom binding |

So the tags preserve **provenance**, not pending work.

## The four dead branches

Separate from the lineage above, four branches are safe to remove. Each has its
own gate in the tool, and a gate that does not hold skips rather than proceeds:

| Branch | Gate | Basis |
| --- | --- | --- |
| `claude/pr-235-review-d89w6l` | contained in `main` | 0 unique commits; it is PR #235's head |
| `tmp-perm-probe` | 0 commits uncovered by archive tags | its whole history is shared with the tagged branches |
| `claude/open-pr-code-review-m545i2` | exactly 1 unique commit | an older ADR 0002 draft; `main` carries a later revision (D1–D7, "resolved design points") |
| `fix/sync-setec-selftest-env` | exactly 1 unique commit | the fix landed; only a stale `PINNED_WORKFLOWS` hash differs |

## Running it

```bash
bash tools/archive_and_prune_branches.sh            # dry run: report only
bash tools/archive_and_prune_branches.sh --apply    # tag, push, then prune
```

Order is load-bearing: the tool tags and pushes **first**, re-reads the remote
to confirm every `archive/<branch>` tag actually landed, and aborts without
deleting anything if one did not. The disjoint set is derived from the remote
on each run, never hardcoded, so it stays correct as branches come and go.

**Push rights required.** A cloud session whose git credential is read-only
gets `HTTP 403` on any ref write — tag push and branch delete alike — while the
GitHub REST API (and so PR merges) still succeeds. That asymmetry is why this
is a checked-in runbook instead of something a web session finished inline.

## Afterwards

The archived history stays reachable by tag:

```bash
git fetch origin --tags
git log archive/claude/phase-5-plumbing
```

Nothing else in the repo references these branches; `main` is unaffected.
