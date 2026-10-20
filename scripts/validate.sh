#!/usr/bin/env bash
# Compatibility shim to the shipped native validator entrypoint.
set -euo pipefail
case "${BASH_SOURCE[0]}" in
  */*) script_dir="${BASH_SOURCE[0]%/*}" ;;
  *) script_dir=. ;;
esac
script_dir=$(cd "$script_dir" && pwd)
exec "$BASH" "$script_dir/../plugins/apodictic/scripts/validate.sh" "$@"
