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

echo "[7/7] Commit, tag + push"
echo "  The generated codex/ + antigravity/ trees are NOT committed (GitHub #52);"
echo "  the release workflow (.github/workflows/release.yml) rebuilds them on the"
echo "  pushed tag and attaches the per-host bundles to the GitHub release, with"
echo "  notes taken from the assembled changelog section."
echo ""
if [ -n "$(git -C "$REPO_ROOT" status --porcelain)" ]; then
  echo "  Working tree dirty. Commit the release changes, then run:"
  echo "    git tag v${NEW_VERSION} && git push origin v${NEW_VERSION}"
  echo "  The release workflow takes over from the pushed tag."
elif git -C "$REPO_ROOT" rev-parse "v${NEW_VERSION}" >/dev/null 2>&1; then
  echo "  Skipped: tag v${NEW_VERSION} already exists."
else
  git -C "$REPO_ROOT" tag "v${NEW_VERSION}"
  git -C "$REPO_ROOT" push origin "v${NEW_VERSION}"
  echo "  Pushed tag v${NEW_VERSION}. The release workflow will publish the bundles."
fi

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
