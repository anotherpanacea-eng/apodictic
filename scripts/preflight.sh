#!/usr/bin/env bash
#
# preflight.sh — Gather manuscript metadata for APODICTIC dispatch decisions.
#
# Usage: ./scripts/preflight.sh <manuscript_path> [output_path]
#
# Produces a metadata packet the parent orchestrator uses to:
#   - Select execution mode (single-context / hybrid / swarm)
#   - Set max_turns for the triage subagent
#   - Pass calibration data to analytical passes
#
# If output_path is omitted, writes to stdout.
# If output_path is provided, writes to that file.

set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: $0 <manuscript_path> [output_path]"
  echo "Example: $0 manuscript.md preflight-output.md"
  exit 1
fi

MANUSCRIPT="$1"
OUTPUT="${2:-/dev/stdout}"

if [ ! -f "$MANUSCRIPT" ]; then
  echo "Error: File not found: $MANUSCRIPT" >&2
  exit 1
fi

# ── Measurements ──────────────────────────────────────────

TOTAL_LINES=$(wc -l < "$MANUSCRIPT")
TOTAL_WORDS=$(wc -w < "$MANUSCRIPT")
ESTIMATED_PAGES=$(( (TOTAL_WORDS + 249) / 250 ))

# Section/chapter boundaries
# Looks for: chapter/part/interlude headers, horizontal rules, large whitespace gaps
BOUNDARIES=$(grep -n -i \
  '^\s*\(CHAPTER\|PART\|INTERLUDE\|BOOK\|PROLOGUE\|EPILOGUE\|ACT\)\b\|^---$\|^===\|^##' \
  "$MANUSCRIPT" 2>/dev/null || echo "(none detected)")

BOUNDARY_COUNT=$(echo "$BOUNDARIES" | grep -c -v '(none' 2>/dev/null || echo "0")

# POV detection — sample start, middle, and end
sample_pov() {
  local label="$1" start="$2" count="$3"
  local first_person third_person
  first_person=$(sed -n "${start},$((start + count - 1))p" "$MANUSCRIPT" \
    | grep -o -i '\bI \b\|\bI was\b\|\bI had\b\|\bI could\b\|\bmy \b' \
    | wc -l)
  third_person=$(sed -n "${start},$((start + count - 1))p" "$MANUSCRIPT" \
    | grep -o -i '\bhe was\b\|\bshe was\b\|\bhe had\b\|\bshe had\b\|\bthey were\b' \
    | wc -l)
  echo "  ${label}: first-person=${first_person}, third-person=${third_person}"
}

MID_START=$(( TOTAL_LINES / 2 - 100 ))
END_START=$(( TOTAL_LINES - 200 ))
if [ "$MID_START" -lt 1 ]; then MID_START=1; fi
if [ "$END_START" -lt 1 ]; then END_START=1; fi

# Dialogue ratio
LINES_WITH_QUOTES=$(grep -c '"' "$MANUSCRIPT" 2>/dev/null || echo "0")
if [ "$TOTAL_LINES" -gt 0 ]; then
  DIALOGUE_RATIO=$(echo "scale=1; $LINES_WITH_QUOTES * 100 / $TOTAL_LINES" | bc)
else
  DIALOGUE_RATIO="0"
fi

# Paragraph stats
NON_EMPTY_LINES=$(grep -c -v '^\s*$' "$MANUSCRIPT" 2>/dev/null || echo "1")
if [ "$NON_EMPTY_LINES" -gt 0 ]; then
  MEAN_WORDS_PER_LINE=$(echo "scale=1; $TOTAL_WORDS / $NON_EMPTY_LINES" | bc)
else
  MEAN_WORDS_PER_LINE="0"
fi

# ── Derived values ────────────────────────────────────────

# Execution mode recommendation
if [ "$TOTAL_WORDS" -lt 60000 ]; then
  RECOMMENDED_MODE="sequential"
elif [ "$TOTAL_WORDS" -lt 100000 ]; then
  RECOMMENDED_MODE="hybrid"
else
  RECOMMENDED_MODE="swarm"
fi

# Triage max_turns: ceil(total_lines / 500) + 20
# The +20 buffer covers: output file writes (~4 turns), reasoning between
# reads (~3-5 turns), and headroom for complex structural decisions.
TRIAGE_MAX_TURNS=$(( (TOTAL_LINES + 499) / 500 + 20 ))

# ── Output ────────────────────────────────────────────────

cat > "$OUTPUT" <<PREFLIGHT
# APODICTIC Pre-flight Metadata

## Manuscript
- **File:** ${MANUSCRIPT}
- **Total lines:** ${TOTAL_LINES}
- **Estimated words:** ${TOTAL_WORDS}
- **Estimated pages** (at 250 w/p): ${ESTIMATED_PAGES}

## Section Boundaries
- **Detected breaks:** ${BOUNDARY_COUNT}
${BOUNDARIES}

## POV Detection (200-line samples)
$(sample_pov "Start (lines 1-200)" 1 200)
$(sample_pov "Middle (lines ${MID_START}-$((MID_START+200)))" "$MID_START" 200)
$(sample_pov "End (lines ${END_START}-$((END_START+200)))" "$END_START" 200)

## Dialogue Ratio
- Lines with quotation marks: ${LINES_WITH_QUOTES} / ${TOTAL_LINES}
- **Approximate dialogue ratio:** ${DIALOGUE_RATIO}%

## Paragraph Statistics
- Non-empty lines: ${NON_EMPTY_LINES}
- **Mean words per non-empty line:** ${MEAN_WORDS_PER_LINE}

## Dispatch Recommendations
- **Recommended execution mode:** ${RECOMMENDED_MODE}
- **Triage subagent max_turns:** ${TRIAGE_MAX_TURNS}
- **Mode thresholds:** <60K words → sequential; 60-100K → hybrid; >100K → swarm
- **max_turns formula:** ceil(total_lines / 500) + 20

## Notes
- If section boundary count is low relative to word count, chapter structure
  may have been lost in file conversion. The triage subagent should identify
  scene boundaries from narrative content rather than relying on headers.
- POV detection uses pronoun frequency as a heuristic. Mixed results across
  samples may indicate alternating POV, framing device, or epistolary structure.
- Dialogue ratio is approximate (counts lines containing quotation marks,
  not dialogue-only lines).
PREFLIGHT

if [ "$OUTPUT" != "/dev/stdout" ]; then
  echo "Pre-flight metadata written to: $OUTPUT"
fi
