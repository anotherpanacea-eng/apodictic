#!/usr/bin/env bash
#
# bump-version.sh — Update APODICTIC version in all canonical locations.
#
# Usage: ./scripts/bump-version.sh 1.0.0
#
# Canonical source: plugins/apodictic/.claude-plugin/plugin.json
# Also updates:     .claude-plugin/marketplace.json (both version fields)
#                   4 SKILL.md frontmatter version: fields
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

# 2. marketplace.json (both metadata.version and plugin entry version)
MARKETPLACE_JSON="$REPO_ROOT/.claude-plugin/marketplace.json"
if [ -f "$MARKETPLACE_JSON" ]; then
  sedi "s/\"version\": \"[^\"]*\"/\"version\": \"${NEW_VERSION}\"/g" "$MARKETPLACE_JSON"
  echo "  updated  $MARKETPLACE_JSON"
else
  echo "  MISSING  $MARKETPLACE_JSON"
fi

# 3. SKILL.md frontmatter (4 files)
SKILL_FILES=(
  "$PLUGIN_DIR/skills/core-editor/SKILL.md"
  "$PLUGIN_DIR/skills/pre-writing-pathway/SKILL.md"
  "$PLUGIN_DIR/skills/plot-architecture/SKILL.md"
  "$PLUGIN_DIR/skills/specialized-audits/SKILL.md"
)

for f in "${SKILL_FILES[@]}"; do
  if [ -f "$f" ]; then
    sedi "s/^version: .*/version: ${NEW_VERSION}/" "$f"
    echo "  updated  $f"
  else
    echo "  MISSING  $f"
  fi
done

echo "────────────────────────────────────"
echo "Done. 6 files updated to v${NEW_VERSION}."
echo ""
echo "Next steps:"
echo "  1. Add a changelog entry in references/changelog.md"
echo "  2. git add -A && git commit"
echo "  3. git tag v${NEW_VERSION}"
echo "  4. Repackage: cd plugins/apodictic && zip -r ../../apodictic.plugin . -x '.git/*'"
