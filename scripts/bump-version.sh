#!/usr/bin/env bash
#
# bump-version.sh — Update APODICTIC version in all canonical locations.
#
# Usage: ./scripts/bump-version.sh 1.0.0
#
# Canonical source: plugins/apodictic/.claude-plugin/plugin.json
# Also updates:     plugins/apodictic/.codex-plugin/plugin.json
#                   marketplace.json (root, both version fields)
#                   .claude-plugin/marketplace.json (both version fields)
#                   plugins/apodictic/README.codex.md version callout
#                   5 SKILL.md frontmatter version: fields
#
# Does NOT touch: changelog entries, deprecated file banners,
# individual audit/genre provenance versions, output template footers,
# sample-editorial-letter.html (historical run label, not current version).

set -euo pipefail

if [ $# -ne 1 ]; then
  echo "Usage: $0 <new-version>"
  echo "Example: $0 1.0.0"
  exit 1
fi

NEW_VERSION="$1"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PLUGIN_DIR="$REPO_ROOT/plugins/apodictic"

# Portable in-place sed: macOS needs -i '', GNU/Linux needs -i
sedi() {
  if sed --version >/dev/null 2>&1; then
    # GNU sed
    sed -i "$@"
  else
    # BSD/macOS sed
    sed -i '' "$@"
  fi
}

echo "Bumping APODICTIC to v${NEW_VERSION}"
echo "────────────────────────────────────"

# 1. plugin.json (canonical)
PLUGIN_JSON="$PLUGIN_DIR/.claude-plugin/plugin.json"
if [ -f "$PLUGIN_JSON" ]; then
  sedi "s/\"version\": \"[^\"]*\"/\"version\": \"${NEW_VERSION}\"/" "$PLUGIN_JSON"
  echo "  updated  $PLUGIN_JSON"
else
  echo "  MISSING  $PLUGIN_JSON"
fi

# 2. plugin.json — root copy (marketplace pulls from here)
ROOT_PLUGIN_JSON="$REPO_ROOT/plugin.json"
if [ -f "$ROOT_PLUGIN_JSON" ]; then
  sedi "s/\"version\": \"[^\"]*\"/\"version\": \"${NEW_VERSION}\"/" "$ROOT_PLUGIN_JSON"
  echo "  updated  $ROOT_PLUGIN_JSON"
else
  echo "  MISSING  $ROOT_PLUGIN_JSON"
fi

# 3. plugin.json (Codex template)
CODEX_PLUGIN_JSON="$PLUGIN_DIR/.codex-plugin/plugin.json"
if [ -f "$CODEX_PLUGIN_JSON" ]; then
  sedi "s/\"version\": \"[^\"]*\"/\"version\": \"${NEW_VERSION}\"/" "$CODEX_PLUGIN_JSON"
  echo "  updated  $CODEX_PLUGIN_JSON"
else
  echo "  MISSING  $CODEX_PLUGIN_JSON"
fi

# 4. marketplace.json — root copy (primary)
ROOT_MARKETPLACE="$REPO_ROOT/marketplace.json"
if [ -f "$ROOT_MARKETPLACE" ]; then
  sedi "s/\"version\": \"[^\"]*\"/\"version\": \"${NEW_VERSION}\"/g" "$ROOT_MARKETPLACE"
  echo "  updated  $ROOT_MARKETPLACE"
else
  echo "  MISSING  $ROOT_MARKETPLACE"
fi

# 5. marketplace.json — .claude-plugin/ copy
CLAUDE_MARKETPLACE="$REPO_ROOT/.claude-plugin/marketplace.json"
if [ -f "$CLAUDE_MARKETPLACE" ]; then
  sedi "s/\"version\": \"[^\"]*\"/\"version\": \"${NEW_VERSION}\"/g" "$CLAUDE_MARKETPLACE"
  echo "  updated  $CLAUDE_MARKETPLACE"
else
  echo "  MISSING  $CLAUDE_MARKETPLACE"
fi

# 6. Codex README version callout
CODEX_README="$PLUGIN_DIR/README.codex.md"
if [ -f "$CODEX_README" ]; then
  sedi 's/Current Codex manifest version is `[^`]*`/Current Codex manifest version is `'"${NEW_VERSION}"'`/' "$CODEX_README"
  echo "  updated  $CODEX_README"
else
  echo "  MISSING  $CODEX_README"
fi

# 7. SKILL.md frontmatter (auto-discovered)
SKILL_COUNT=0
while IFS= read -r -d '' f; do
  sedi "s/^version: .*/version: ${NEW_VERSION}/" "$f"
  echo "  updated  $f"
  SKILL_COUNT=$((SKILL_COUNT + 1))
done < <(find "$PLUGIN_DIR/skills" -name "SKILL.md" -print0)

if [ "$SKILL_COUNT" -eq 0 ]; then
  echo "  WARNING  No SKILL.md files found under $PLUGIN_DIR/skills/"
fi

TOTAL=$((6 + SKILL_COUNT))
echo "────────────────────────────────────"
echo "Done. $TOTAL files updated to v${NEW_VERSION} (5 JSON + 1 README + ${SKILL_COUNT} SKILL.md)."
echo ""
echo "Next step:"
echo "  Run the full release pipeline:"
echo "    ./scripts/release.sh ${NEW_VERSION}"
echo ""
echo "Or run manually:"
echo "  1. node ./scripts/release-generate.mjs"
echo "  2. node ./scripts/build-codex.mjs"
echo "  3. node ./scripts/release-verify.mjs"
