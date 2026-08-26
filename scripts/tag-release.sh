#!/usr/bin/env bash

set -euo pipefail

if [ $# -ne 1 ]; then
  echo "Usage: $0 <version>" >&2
  exit 2
fi

VERSION="${1#v}"
if ! [[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "Invalid release version: $1" >&2
  exit 2
fi

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TAG="v${VERSION}"
CURRENT_BRANCH="$(git -C "$REPO_ROOT" branch --show-current)"
if [ "$CURRENT_BRANCH" != "main" ]; then
  echo "REFUSED: release tags may only be cut from main (current branch: ${CURRENT_BRANCH:-detached})." >&2
  exit 1
fi
if ! WORKTREE_STATUS="$(git -C "$REPO_ROOT" status --porcelain)"; then
  echo "REFUSED: unable to verify that the working tree is clean." >&2
  exit 1
fi
if [ -n "$WORKTREE_STATUS" ]; then
  echo "REFUSED: release tags require a clean working tree." >&2
  exit 1
fi

git -C "$REPO_ROOT" fetch --quiet origin main
HEAD_COMMIT="$(git -C "$REPO_ROOT" rev-parse HEAD)"
REMOTE_MAIN="$(git -C "$REPO_ROOT" rev-parse refs/remotes/origin/main)"
if [ "$HEAD_COMMIT" != "$REMOTE_MAIN" ]; then
  echo "REFUSED: HEAD ($HEAD_COMMIT) is not the freshly fetched origin/main ($REMOTE_MAIN)." >&2
  exit 1
fi

PLUGIN_VERSION="$(
  node -e '
    const fs = require("node:fs");
    const manifest = JSON.parse(fs.readFileSync(process.argv[1], "utf8"));
    process.stdout.write(String(manifest.version || ""));
  ' "$REPO_ROOT/plugin.json"
)"
if [ "$PLUGIN_VERSION" != "$VERSION" ]; then
  echo "REFUSED: plugin.json version is $PLUGIN_VERSION, expected $VERSION." >&2
  exit 1
fi
if git -C "$REPO_ROOT" rev-parse "$TAG" >/dev/null 2>&1; then
  echo "REFUSED: local tag $TAG already exists." >&2
  exit 1
fi
if ! REMOTE_TAG="$(git -C "$REPO_ROOT" ls-remote --tags origin "refs/tags/$TAG")"; then
  echo "REFUSED: unable to verify whether remote tag $TAG already exists." >&2
  exit 1
fi
if [ -n "$REMOTE_TAG" ]; then
  echo "REFUSED: remote tag $TAG already exists." >&2
  exit 1
fi

git -C "$REPO_ROOT" tag "$TAG"
if ! git -C "$REPO_ROOT" push origin "refs/tags/$TAG"; then
  if ! REMOTE_AFTER_FAILURE="$(git -C "$REPO_ROOT" ls-remote --tags origin "refs/tags/$TAG")"; then
    echo "REFUSED: tag push failed and remote state is indeterminate; preserving local $TAG for manual recovery." >&2
    exit 1
  fi
  if [ -n "$REMOTE_AFTER_FAILURE" ]; then
    echo "REFUSED: tag push reported failure but remote $TAG now exists; preserving the matching local tag for manual verification." >&2
    exit 1
  fi
  if ! git -C "$REPO_ROOT" tag -d "$TAG" >/dev/null; then
    echo "REFUSED: tag push failed and cleanup of local $TAG also failed; manual recovery is required." >&2
    exit 1
  fi
  echo "REFUSED: tag push failed; removed local $TAG because the remote tag is absent." >&2
  exit 1
fi
echo "Pushed $TAG from verified origin/main $HEAD_COMMIT."
