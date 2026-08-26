#!/usr/bin/env bash

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TMP_ROOT="$(mktemp -d)"
trap 'rm -rf "$TMP_ROOT"' EXIT
FAKE_BIN="$TMP_ROOT/bin"
LOG="$TMP_ROOT/git.log"
mkdir -p "$FAKE_BIN"

cat >"$FAKE_BIN/git" <<'EOF'
#!/usr/bin/env bash
set -eu
printf '%s\n' "$*" >>"$FAKE_GIT_LOG"
case "$*" in
  *" branch --show-current") printf 'main\n' ;;
  *" status --porcelain")
    [ "${FAKE_STATUS_MODE:-ok}" = error ] && exit 2
    :
    ;;
  *" fetch --quiet origin main") : ;;
  *" rev-parse HEAD"|*" rev-parse refs/remotes/origin/main") printf 'same-head\n' ;;
  *" rev-parse v"*) exit 1 ;;
  *" ls-remote --tags origin "*)
    case "$FAKE_LS_REMOTE_MODE" in
      absent) : ;;
      present) printf 'same-head\trefs/tags/test\n' ;;
      error) exit 2 ;;
      *) exit 99 ;;
    esac
    ;;
  *" tag -d v"*) : ;;
  *" tag v"*) : ;;
  *" push origin refs/tags/v"*)
    [ "${FAKE_PUSH_MODE:-ok}" = error ] && exit 3
    :
    ;;
  *) printf 'unexpected fake git call: %s\n' "$*" >&2; exit 98 ;;
esac
EOF
chmod +x "$FAKE_BIN/git"

VERSION="$(grep -m1 '"version"' "$REPO_ROOT/plugin.json" \
  | sed -E 's/.*"version"[[:space:]]*:[[:space:]]*"([^"]+)".*/\1/')"
[ -n "$VERSION" ]
cat >"$FAKE_BIN/node" <<'EOF'
#!/usr/bin/env bash
printf '%s' "$FAKE_PLUGIN_VERSION"
EOF
chmod +x "$FAKE_BIN/node"

run_case() {
  local mode="$1"
  local status_mode="${2:-ok}"
  local push_mode="${3:-ok}"
  : >"$LOG"
  set +e
  OUTPUT="$(PATH="$FAKE_BIN:$PATH" FAKE_GIT_LOG="$LOG" FAKE_LS_REMOTE_MODE="$mode" \
    FAKE_STATUS_MODE="$status_mode" FAKE_PUSH_MODE="$push_mode" \
    FAKE_PLUGIN_VERSION="$VERSION" \
    bash "$REPO_ROOT/scripts/tag-release.sh" "$VERSION" 2>&1)"
  STATUS=$?
  set -e
}

run_case absent error
[ "$STATUS" -eq 1 ]
grep -q 'unable to verify that the working tree is clean' <<<"$OUTPUT"
! grep -Eq ' tag v| push origin refs/tags/v' "$LOG"

run_case error
[ "$STATUS" -eq 1 ]
grep -q 'unable to verify whether remote tag' <<<"$OUTPUT"
! grep -Eq ' tag v| push origin refs/tags/v' "$LOG"

run_case present
[ "$STATUS" -eq 1 ]
grep -q 'remote tag .* already exists' <<<"$OUTPUT"
! grep -Eq ' tag v| push origin refs/tags/v' "$LOG"

run_case absent
[ "$STATUS" -eq 0 ]
grep -Eq ' tag v' "$LOG"
grep -Eq ' push origin refs/tags/v' "$LOG"

run_case absent ok error
[ "$STATUS" -eq 1 ]
grep -q 'tag push failed; removed local' <<<"$OUTPUT"
grep -Eq ' tag v' "$LOG"
grep -Eq ' push origin refs/tags/v' "$LOG"
grep -Eq ' tag -d v' "$LOG"

echo 'tag-release remote inspection self-test: PASS'
