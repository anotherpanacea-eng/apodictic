#!/usr/bin/env bash

set -euo pipefail

if [ $# -ne 1 ]; then
  echo "Usage: $0 <new-version>"
  echo "Example: $0 1.0.10"
  exit 1
fi

NEW_VERSION="$1"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PLUGIN_DIR="$REPO_ROOT/plugins/apodictic"

if [ ! -d "$PLUGIN_DIR" ]; then
  echo "Missing plugin directory: $PLUGIN_DIR"
  exit 1
fi

echo "[0/7] Preflight host package builders before mutating release files"
node "$REPO_ROOT/scripts/build-codex.mjs" --self-check
node "$REPO_ROOT/scripts/build-antigravity.mjs" --self-check

echo "Release pipeline starting for v${NEW_VERSION}"
echo "────────────────────────────────────"

echo "[1/7] Bump version fields"
"$REPO_ROOT/scripts/bump-version.sh" "$NEW_VERSION"

echo "[2/7] Assemble changelog.d/ fragments into the v${NEW_VERSION} section"
node "$REPO_ROOT/scripts/assemble-changelog.mjs" "$NEW_VERSION"

echo "[3/7] Generate derived files from release-registry.json"
node "$REPO_ROOT/scripts/release-generate.mjs"

echo "[4/7] Build generated Codex workspace and package"
node "$REPO_ROOT/scripts/build-codex.mjs"

echo "[5/7] Build generated Antigravity workspace and package"
node "$REPO_ROOT/scripts/build-antigravity.mjs"

echo "[6/7] Verify repository consistency"
node "$REPO_ROOT/scripts/release-verify.mjs"

echo "[7/7] Owner merge + tag handoff"
echo "  The generated codex/ + antigravity/ trees are NOT committed (GitHub #52);"
echo "  the release workflow (.github/workflows/release.yml) rebuilds them on the"
echo "  pushed tag and attaches the per-host bundles to the GitHub release, with"
echo "  notes taken from the assembled changelog section."
echo ""
if ! RELEASE_STATUS="$(git -C "$REPO_ROOT" status --porcelain)"; then
  echo "REFUSED: unable to inspect the release working tree." >&2
  exit 1
fi
if [ -n "$RELEASE_STATUS" ]; then
  echo "  Working tree dirty. Commit the release changes and merge the release PR."
else
  echo "  Release files are already committed. Merge the release PR before tagging."
fi
echo "  After updating a clean main checkout to origin/main, the owner runs:"
echo "    bash scripts/tag-release.sh ${NEW_VERSION}"
echo "  The guarded tag helper verifies branch, remote-main identity, version, and tag absence."

echo "────────────────────────────────────"
echo "Release pipeline complete for v${NEW_VERSION}."
echo ""
echo "Release assets (published by .github/workflows/release.yml on the tag):"
echo "  - dist/apodictic-codex-marketplace.zip"
echo "  - dist/apodictic-antigravity.zip"
echo "  - apodictic.plugin"
echo ""
echo "Manual external follow-ups:"
echo "  1. Custom GPT: update published instructions/knowledge if behavior changed."
echo "  2. Website: update public feature copy if capability messaging changed."
