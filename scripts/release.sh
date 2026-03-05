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

echo "[1/6] Bump version fields"
"$REPO_ROOT/scripts/bump-version.sh" "$NEW_VERSION"

echo "[2/6] Generate derived files from release-registry.json"
node "$REPO_ROOT/scripts/release-generate.mjs"

echo "[3/6] Verify repository consistency"
node "$REPO_ROOT/scripts/release-verify.mjs"

echo "[4/6] Sync plugin -> APODICTIC-Gemini public mirror"
rsync -a --delete --exclude ".git/" --exclude ".DS_Store" "$PLUGIN_DIR/" "$GEMINI_PUBLIC_DIR/"

echo "[5/6] Verify mirror parity"
node "$REPO_ROOT/scripts/release-verify.mjs" --check-sync

echo "[6/6] Package plugin artifact"
(
  cd "$PLUGIN_DIR"
  zip -r "$REPO_ROOT/apodictic.plugin" . -x ".git/*" >/dev/null
)

echo "────────────────────────────────────"
echo "Release pipeline complete for v${NEW_VERSION}."
echo ""
echo "Manual external follow-ups:"
echo "  1. Custom GPT: update published instructions/knowledge if behavior changed."
echo "  2. Website: update public feature copy if capability messaging changed."
