#!/usr/bin/env bash
# Shim: the validators live only in plugins/apodictic/scripts/ (the shipped copy).
exec bash "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/../plugins/apodictic/scripts/validate.sh" "$@"
