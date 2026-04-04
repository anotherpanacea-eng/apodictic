#!/usr/bin/env bash
#
# validate.sh — Mechanical validation for APODICTIC core invariants.
#
# Usage: ./scripts/validate.sh <command> [args...]
#
# Commands:
#   contract-hash <contract_file>
#       Print SHA-256 hash of the contract file (for storage in sidecar).
#
#   contract-check <contract_file> <expected_hash>
#       Verify contract file matches expected hash. Exit 0 if match, 1 if drift.
#
#   ledger-check <ledger_file>
#       Validate Findings Ledger structure. Checks that each pass entry contains
#       required sections. Reports missing sections per pass.
#
#   artifact-names <output_dir> <project_name> <runlabel>
#       Check that pass artifacts in output_dir match naming convention:
#       [Project]_Pass[N]_[Name]_[runlabel].md
#
#   synthesis-sections <editorial_letter_file>
#       Verify editorial letter contains all 11 required sections plus appendices.
#
#   state-lines <diagnostic_state_file>
#       Print line count (for state gardening threshold check).
#
# Exit codes:
#   0 — all checks pass
#   1 — validation failure (details on stdout)
#   2 — usage error

set -euo pipefail

usage() {
  echo "Usage: $0 <command> [args...]"
  echo "Commands: contract-hash, contract-check, ledger-check, artifact-names, synthesis-sections, state-lines"
  exit 2
}

if [ $# -lt 1 ]; then usage; fi

COMMAND="$1"
shift

case "$COMMAND" in

  contract-hash)
    if [ $# -lt 1 ]; then echo "Usage: $0 contract-hash <contract_file>"; exit 2; fi
    if [ ! -f "$1" ]; then echo "Error: File not found: $1" >&2; exit 2; fi
    shasum -a 256 "$1" | awk '{print $1}'
    ;;

  contract-check)
    if [ $# -lt 2 ]; then echo "Usage: $0 contract-check <contract_file> <expected_hash>"; exit 2; fi
    if [ ! -f "$1" ]; then echo "Error: File not found: $1" >&2; exit 2; fi
    ACTUAL=$(shasum -a 256 "$1" | awk '{print $1}')
    if [ "$ACTUAL" = "$2" ]; then
      echo "OK: Contract unchanged."
      exit 0
    else
      echo "WARNING: Contract has been modified since intake."
      echo "  Expected: $2"
      echo "  Actual:   $ACTUAL"
      echo "  If this was intentional (author-requested contract revision), update the"
      echo "  contract_hash in Diagnostic_State.meta.json. If unintentional, investigate."
      exit 1
    fi
    ;;

  ledger-check)
    if [ $# -lt 1 ]; then echo "Usage: $0 ledger-check <ledger_file>"; exit 2; fi
    if [ ! -f "$1" ]; then echo "Error: File not found: $1" >&2; exit 2; fi
    LEDGER="$1"
    ERRORS=0

    # Find all pass entries
    PASS_HEADERS=$(grep -n '^## Pass [0-9]' "$LEDGER" 2>/dev/null || true)
    if [ -z "$PASS_HEADERS" ]; then
      echo "WARNING: No pass entries found in ledger."
      exit 1
    fi

    # Required sections within each pass entry
    REQUIRED_SECTIONS=("Notable Findings" "Data Artifacts for Letter Reference" "Cross-Pass Connections" "Unresolved Questions" "Audit Triggers")

    # Get line numbers of each pass header
    while IFS= read -r header_line; do
      PASS_NUM=$(echo "$header_line" | grep -o 'Pass [0-9]\+' | head -1)
      LINE_NUM=$(echo "$header_line" | cut -d: -f1)

      # Find the next pass header (or end of file) to define this entry's range
      NEXT_HEADER_LINE=$(grep -n '^## Pass [0-9]' "$LEDGER" 2>/dev/null \
        | awk -F: -v cur="$LINE_NUM" '$1 > cur {print $1; exit}')
      if [ -z "$NEXT_HEADER_LINE" ]; then
        NEXT_HEADER_LINE=$(wc -l < "$LEDGER")
      fi

      # Extract this pass's section
      SECTION=$(sed -n "${LINE_NUM},${NEXT_HEADER_LINE}p" "$LEDGER")

      for req in "${REQUIRED_SECTIONS[@]}"; do
        if ! echo "$SECTION" | grep -q "### ${req}"; then
          # Pass 0 and Pass 10 are data-building passes — only warn, don't error
          PASS_N=$(echo "$PASS_NUM" | grep -o '[0-9]\+')
          if [ "$PASS_N" = "0" ] || [ "$PASS_N" = "10" ]; then
            echo "NOTE: ${PASS_NUM} missing '### ${req}' (acceptable for data-building pass)"
          else
            echo "ERROR: ${PASS_NUM} missing required section '### ${req}'"
            ERRORS=$((ERRORS + 1))
          fi
        fi
      done
    done <<< "$PASS_HEADERS"

    if [ "$ERRORS" -gt 0 ]; then
      echo ""
      echo "FAILED: ${ERRORS} missing required section(s) in ledger."
      exit 1
    else
      echo "OK: All pass entries contain required sections."
      exit 0
    fi
    ;;

  artifact-names)
    if [ $# -lt 3 ]; then echo "Usage: $0 artifact-names <output_dir> <project_name> <runlabel>"; exit 2; fi
    if [ ! -d "$1" ]; then echo "Error: Directory not found: $1" >&2; exit 2; fi
    OUTPUT_DIR="$1"
    PROJECT="$2"
    RUNLABEL="$3"
    ERRORS=0

    # Check for pass artifacts that don't match convention
    for f in "$OUTPUT_DIR"/*Pass*.md; do
      [ -e "$f" ] || continue
      BASENAME=$(basename "$f")
      # Expected: [Project]_Pass[N]_[Name]_[runlabel].md
      if ! echo "$BASENAME" | grep -qE "^${PROJECT}_Pass[0-9]+_[A-Za-z_]+_${RUNLABEL}\.md$"; then
        echo "WARNING: Artifact name doesn't match convention: $BASENAME"
        echo "  Expected pattern: ${PROJECT}_Pass[N]_[Name]_${RUNLABEL}.md"
        ERRORS=$((ERRORS + 1))
      fi
    done

    if [ "$ERRORS" -gt 0 ]; then
      echo ""
      echo "FAILED: ${ERRORS} artifact(s) with non-standard names."
      exit 1
    else
      echo "OK: All pass artifacts match naming convention."
      exit 0
    fi
    ;;

  synthesis-sections)
    if [ $# -lt 1 ]; then echo "Usage: $0 synthesis-sections <editorial_letter_file>"; exit 2; fi
    if [ ! -f "$1" ]; then echo "Error: File not found: $1" >&2; exit 2; fi
    LETTER="$1"
    ERRORS=0

    # 14 required sections per run-synthesis.md §Post-Write Section Validation.
    # Each must appear as a markdown heading (line starting with #).
    # Checks are case-insensitive and match headings only, not prose mentions.
    declare -a CHECKS=(
      "Development Edit"
      "The Short Version"
      "What the Book Does Best"
      "What Needs Work"
      "Additional Observations"
      "Revision Checklist"
      "Protected Elements"
      "Author Decisions"
      "Control Questions"
      "The Strongest Case Against"
      "Stress Test"
      "Appendix A"
      "Appendix B"
      "Appendix C"
    )

    for check in "${CHECKS[@]}"; do
      # Match lines that start with one or more # characters followed by the section name
      if ! grep -iE "^#{1,4}\s.*${check}" "$LETTER" > /dev/null 2>&1; then
        echo "ERROR: Missing required heading: '${check}'"
        ERRORS=$((ERRORS + 1))
      fi
    done

    if [ "$ERRORS" -gt 0 ]; then
      echo ""
      echo "FAILED: ${ERRORS} missing required heading(s) in editorial letter."
      echo "NOTE: Sections must appear as markdown headings (lines starting with #),"
      echo "not just as phrases in prose."
      exit 1
    else
      echo "OK: All 14 required section headings present in editorial letter."
      exit 0
    fi
    ;;

  state-lines)
    if [ $# -lt 1 ]; then echo "Usage: $0 state-lines <diagnostic_state_file>"; exit 2; fi
    if [ ! -f "$1" ]; then echo "Error: File not found: $1" >&2; exit 2; fi
    wc -l < "$1"
    ;;

  *)
    echo "Unknown command: $COMMAND"
    usage
    ;;
esac
