#!/usr/bin/env bash
# Compatibility entrypoint. Validation lives in the sibling native Python CLI.
set -euo pipefail
case "${BASH_SOURCE[0]}" in
  */*) script_dir="${BASH_SOURCE[0]%/*}" ;;
  *) script_dir=. ;;
esac
script_dir=$(cd "$script_dir" && pwd)
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8 APODICTIC_VALIDATE_ENTRY="$script_dir/validate.sh"
if command -v python3 >/dev/null 2>&1; then
  exec python3 "$script_dir/validate.py" "$@"
elif command -v python >/dev/null 2>&1; then
  exec python "$script_dir/validate.py" "$@"
fi
printf '%s\n' 'ERROR: validate.sh requires Python 3.10+ (python3 or python).' >&2
exit 127
