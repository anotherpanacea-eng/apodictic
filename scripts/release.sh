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
GEMINI_PUBLIC_DIR="$REPO_ROOT/../APODICTIC-Gemini/public/apodictic-plugin"

if [ ! -d "$PLUGIN_DIR" ]; then
  echo "Missing plugin directory: $PLUGIN_DIR"
  exit 1
fi

if [ ! -d "$GEMINI_PUBLIC_DIR" ]; then
  echo "Missing Gemini public plugin directory: $GEMINI_PUBLIC_DIR"
  exit 1
fi

echo "Release pipeline starting for v${NEW_VERSION}"
echo "────────────────────────────────────"

echo "[1/9] Bump version fields"
"$REPO_ROOT/scripts/bump-version.sh" "$NEW_VERSION"

echo "[2/9] Generate derived files from release-registry.json"
node "$REPO_ROOT/scripts/release-generate.mjs"

echo "[3/9] Build generated Codex workspace and package"
node "$REPO_ROOT/scripts/build-codex.mjs"

echo "[4/9] Build generated Antigravity workspace"
node "$REPO_ROOT/scripts/build-antigravity.mjs"

echo "[5/9] Verify repository consistency"
node "$REPO_ROOT/scripts/release-verify.mjs"

echo "[6/9] Sync plugin -> APODICTIC-Gemini public mirror"
rsync -a --delete --exclude ".git/" --exclude ".DS_Store" "$PLUGIN_DIR/" "$GEMINI_PUBLIC_DIR/"

echo "[7/9] Verify mirror parity"
node "$REPO_ROOT/scripts/release-verify.mjs" --check-sync

echo "[8/9] Package Claude plugin artifact"
(
  cd "$PLUGIN_DIR"
  zip -r "$REPO_ROOT/apodictic.plugin" . -x ".git/*" >/dev/null
)

echo "[9/9] Tag + GitHub release"
if [ -n "$(git -C "$REPO_ROOT" status --porcelain)" ]; then
  echo "  Skipped: working tree dirty. After committing all release changes, run:"
  echo "    git tag v${NEW_VERSION} && git push origin v${NEW_VERSION}"
  echo "    gh release create v${NEW_VERSION} --generate-notes"
elif git -C "$REPO_ROOT" rev-parse "v${NEW_VERSION}" >/dev/null 2>&1; then
  echo "  Skipped: tag v${NEW_VERSION} already exists."
else
  git -C "$REPO_ROOT" tag "v${NEW_VERSION}"
  git -C "$REPO_ROOT" push origin "v${NEW_VERSION}"
  gh -R "anotherpanacea-eng/apodictic" release create "v${NEW_VERSION}" --generate-notes
  echo "  Created tag v${NEW_VERSION} and GitHub release."
fi

echo "────────────────────────────────────"
echo "Release pipeline complete for v${NEW_VERSION}."
echo "Codex package: $REPO_ROOT/dist/apodictic-codex-marketplace.zip"
echo ""
echo "Manual external follow-ups:"
echo "  1. Custom GPT: update published instructions/knowledge if behavior changed."
echo "  2. Website: update public feature copy if capability messaging changed."
