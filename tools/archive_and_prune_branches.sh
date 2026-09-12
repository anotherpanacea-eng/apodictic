#!/usr/bin/env bash
#
# archive_and_prune_branches.sh — preserve this repo's pre-rewrite branch
# lineage as tags, then delete branches that are provably dead.
#
# WHY THIS EXISTS
# ---------------
# This repo's `main` history was rebuilt around 2026-07-06: `main` has seven
# root commits all dated that day and reaches nothing earlier. Nineteen branches
# still descend from the ORIGINAL root `c3cb118` ("Initial release: APODICTIC
# v0.4.15", 2026-02-20) and share NO common ancestor with `main`.
#
# Two consequences a future session should not have to re-derive:
#
#   1. Those branches can never enter a merge train. `git merge-base main <b>`
#      is empty, so a merge would apply an unrelated tree (~100k deletions),
#      not integrate a change. They are not stale PRs; they are a severed
#      lineage.
#   2. They hold the ONLY copy of the repo's pre-2026-07-06 history (795
#      commits). Deleting the refs makes those commits unreachable and
#      eventually collectable. So this tool TAGS before it deletes, and refuses
#      to delete anything until the tags are confirmed on the remote.
#
# The branch content itself is not lost work: the surviving files were carried
# into the rebuilt `main` (fixtures restructured into broken/clean pairs, the
# bespoke registration test superseded by meta_lint's M1-M8 checks, and the
# changelog fragments consumed at release). The tags preserve provenance, not
# pending work.
#
# WHAT IT DOES
# ------------
#   1. Derives the disjoint-history set from the remote (never a hardcoded list).
#   2. Creates one annotated `archive/<branch>` tag per pre-rewrite branch.
#   3. Pushes the tags, then verifies each is really on the remote.
#   4. Deletes four dead branches, each behind its own gate:
#        claude/pr-235-review-d89w6l        contained in main (PR #235's head)
#        tmp-perm-probe                     0 commits not covered by the tags
#        claude/open-pr-code-review-m545i2  1 commit; main has a later ADR 0002
#        fix/sync-setec-selftest-env        1 commit; fix landed, only a stale
#                                           PINNED_WORKFLOWS hash differs
#      A gate that does not hold SKIPS with a reason — it never proceeds.
#
# USAGE
#   bash tools/archive_and_prune_branches.sh            # dry run (default)
#   bash tools/archive_and_prune_branches.sh --apply    # push tags, delete
#
# Requires push rights. Cloud sessions whose git credential is read-only get
# HTTP 403 on any ref write; run this from a local clone.
#
# Exit codes: 0 ok / 1 refused or a preservation check failed.

set -euo pipefail

APPLY=0
[ "${1:-}" = "--apply" ] && APPLY=1
run() { if [ "$APPLY" -eq 1 ]; then "$@"; else echo "      DRY RUN: $*"; fi; }

cd "$(git rev-parse --show-toplevel)"
case "$(git config --get remote.origin.url || true)" in
  *anotherpanacea-eng/apodictic*) ;;
  *) echo "refusing: origin is not anotherpanacea-eng/apodictic"; exit 1 ;;
esac

[ "$APPLY" -eq 1 ] || echo "== DRY RUN (pass --apply to make changes) =="
echo "== fetching =="
git fetch origin --prune --tags

# ---- 1. derive the disjoint-history set ------------------------------------
DISJOINT=()
N_DISJOINT=0
while read -r b; do
  [ "$b" = "main" ] && continue
  git merge-base origin/main "origin/$b" >/dev/null 2>&1 || { DISJOINT+=("$b"); N_DISJOINT=$((N_DISJOINT + 1)); }
done < <(git for-each-ref --format='%(refname:lstrip=3)' refs/remotes/origin)

if [ "$N_DISJOINT" -eq 0 ]; then
  echo "no pre-rewrite branches remain; nothing to archive"
else
  echo "== $N_DISJOINT branch(es) with no common ancestor with main =="
  printf '   %s\n' "${DISJOINT[@]}"
fi

# tmp-perm-probe is itself a delete candidate and carries no unique commits
TO_TAG=()
N_TAG=0
for b in ${DISJOINT[@]+"${DISJOINT[@]}"}; do
  if [ "$b" != "tmp-perm-probe" ]; then TO_TAG+=("$b"); N_TAG=$((N_TAG + 1)); fi
done

# ---- 2. tag ----------------------------------------------------------------
echo "== archive tags =="
for b in ${TO_TAG[@]+"${TO_TAG[@]}"}; do
  if git rev-parse -q --verify "refs/tags/archive/$b" >/dev/null; then
    echo "   exists: archive/$b"; continue
  fi
  sha=$(git rev-parse "origin/$b")
  run git tag -a "archive/$b" -m "Archived pre-rewrite branch '$b' (tip $(git log -1 --format=%cs "$sha")).

Preserved because this repo's main history was rebuilt around 2026-07-06 and has
no common ancestor with this lineage (original root c3cb118, 2026-02-20). This
tag keeps the commits reachable after the branch ref is removed." "$sha"
  echo "   tag: archive/$b -> ${sha:0:8}"
done

# ---- 3. push tags, then PROVE they landed before deleting anything ---------
if [ "$N_TAG" -gt 0 ]; then
  echo "== pushing archive tags =="
  run git push origin $(printf 'refs/tags/archive/%s ' "${TO_TAG[@]}")
  if [ "$APPLY" -eq 1 ]; then
    for b in "${TO_TAG[@]}"; do
      git ls-remote --tags origin "refs/tags/archive/$b" | grep -q . \
        || { echo "ABORT: archive/$b is not on the remote; deleting nothing"; exit 1; }
    done
    echo "   confirmed on remote: $N_TAG tag(s)"
  fi
fi

# ---- 4. gated deletions ----------------------------------------------------
have_branch() { git rev-parse -q --verify "refs/remotes/origin/$1" >/dev/null; }

delete_if_contained() {            # fully merged into main
  local b=$1; have_branch "$b" || { echo "   absent: $b"; return; }
  git merge-base --is-ancestor "origin/$b" origin/main \
    || { echo "   SKIP $b: not contained in main"; return; }
  echo "   delete $b (contained in main)"; run git push origin --delete "$b"
}
delete_if_covered() {              # every commit reachable from an archive tag
  local b=$1; have_branch "$b" || { echo "   absent: $b"; return; }
  local tags n
  tags=$(git tag -l 'archive/*' | sed 's|^|refs/tags/|')
  [ -n "$tags" ] || { echo "   SKIP $b: no archive tags to cover it"; return; }
  n=$(git rev-list "origin/$b" --not $tags | wc -l | tr -d ' ')
  [ "$n" -eq 0 ] || { echo "   SKIP $b: $n commit(s) not covered by archive tags"; return; }
  echo "   delete $b (0 uncovered commits)"; run git push origin --delete "$b"
}
delete_if_superseded() {           # exactly N unique commits, content carried in main
  local b=$1 expect=$2; have_branch "$b" || { echo "   absent: $b"; return; }
  local base n
  base=$(git merge-base origin/main "origin/$b" 2>/dev/null) \
    || { echo "   SKIP $b: no merge base with main"; return; }
  n=$(git rev-list "$base..origin/$b" | wc -l | tr -d ' ')
  [ "$n" -eq "$expect" ] || { echo "   SKIP $b: expected $expect unique commit(s), found $n"; return; }
  echo "   delete $b ($n superseded commit(s))"; run git push origin --delete "$b"
}

echo "== dead branches =="
delete_if_contained  claude/pr-235-review-d89w6l
delete_if_covered    tmp-perm-probe
delete_if_superseded claude/open-pr-code-review-m545i2 1
delete_if_superseded fix/sync-setec-selftest-env 1

echo "== done =="
[ "$APPLY" -eq 1 ] && git fetch origin --prune
exit 0
