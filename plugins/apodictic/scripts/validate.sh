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
#   severity-floor <editorial_letter_file> [<ledger_file>]
#       Mechanical check of the three Severity Floor Rules canonical in
#       core-editor/references/output-policy.md §Severity Floor Rules.
#       Heuristic-parse: ledger optional. Pass --self-test to run built-in cases.
#
#   audit-signal-propagation <editorial_letter_file> [<ledger_file>]
#       Mechanical check that audit-internal severity signals (Must-Fix floors,
#       hard gates, HIGH ratings) propagate to synthesis-layer Must-Fix /
#       Should-Fix per the canonical rule in
#       core-editor/references/run-synthesis.md §Step 2 — Canonical
#       Audit-Signal Propagation Rule. Pass --self-test for built-in cases.
#
#   underdiagnosis-triggers <editorial_letter_file> [<ledger_file>]
#       Detect the six enumerated underdiagnosis triggers canonical in
#       core-editor/references/run-synthesis.md §Step 9 (Conditional
#       Underdiagnosis Retry Loop). For each fired trigger, the synthesis
#       layer must either upgrade the affected finding or document an
#       override via marker <!-- override: underdiagnosis-trigger-<id> -->
#       in the letter body. Pass --self-test for built-in cases.
#
#   ledger-consolidation <consolidated_ledger_file> [<raw_ledger_file>]
#       Mechanical check that a consolidated Findings Ledger satisfies the
#       canonical Findings Ledger Consolidation Contract in
#       core-editor/references/run-synthesis.md §Step 2. Verifies that raw
#       pass headers do not appear in unbroken concatenation, that
#       cross-pass convergence is annotated, that severity collation is
#       documented, and (if raw provided) that consolidation reduced entry
#       count by ≥30%. Pass --self-test for built-in cases.
#
#   decision-layer-check <editorial_letter_file>
#       Mechanical check of Decision-Layer Consolidation counts and
#       Mandatory Appendices presence per
#       core-editor/references/run-synthesis.md §Step 7 and
#       core-editor/references/output-policy.md §Mandatory Appendices /
#       §Evidence Density Self-Check. Verifies Protected Elements (3-6),
#       Author Decisions (3-7), Control Questions (exactly 7), Appendices
#       A/B/C present, and per-Must-Fix evidence density (≥2 references).
#       Pass --self-test for built-in cases.
#
#   quality-risk-triggers <contract_file> [<diagnostic_state_meta_file>]
#       Detect the five enumerated quality-risk mode-selection triggers
#       canonical in core-editor/references/run-core.md
#       §Quality-Risk Mode Selection. Reads contract artifact for genre,
#       audit recommendations, darkness level, POV count, structural notes,
#       and submission-readiness signals. Reads Diagnostic_State.meta.json
#       (if present) for prior-run thin-synthesis flags (Q4). Emits the
#       fired Q1-Q5 trigger set, the per-trigger rationale, and the
#       recommended escalation target (hybrid or swarm). Override marker
#       support: <!-- override: quality-risk-Q[1-5] — <rationale> --> in
#       contract or sidecar markdown notes. Pass --self-test for built-in
#       cases.
#
#   timeline-diff <prior_timeline> <current_timeline>
#       Surface every event added/removed/changed and every anchor changed
#       between two Timeline.md artifacts (Pass-10-Class rolling structured
#       artifact per core-editor/references/pass-10.md). Exit 0 if Section 8
#       (Diff Notes) of the current Timeline annotates each diff or no diff
#       exists; exit 1 if undocumented diff present. Honors body-only
#       override marker <!-- override: timeline-diff-undocumented -->.
#       Pass --self-test for built-in cases.
#
#   timeline-arithmetic <timeline_file>
#       Marker-hygiene check only (v1.7.9 honest reframing). Surfaces
#       rows with a negative gap-from-previous numeric value or with
#       a pre-labeled "(conflicts ...)" / "(contradicts ...)" parenthetical.
#       Does NOT independently compute span arithmetic — true arithmetic
#       verification (span sums, anchor-format normalization) requires
#       structured Timeline parsing and is deferred to a Phase 7 Python
#       helper. Exit 0 if no marker-hygiene candidates; exit 1 if surfaced.
#       Honors body-only override marker
#       <!-- override: timeline-arithmetic-conflict -->. Pass --self-test
#       for built-in cases.
#
#   timeline-anchor-conflict <timeline_file>
#       Pre-labeled-conflict surfacing only (v1.7.9 honest reframing).
#       Counts parenthetical "(contradicts ...)", "(paradox with ...)",
#       and "(conflicts with ...)" annotations in the Timeline body —
#       i.e., Pass 10 model judgment has already pre-labeled the conflict.
#       Does NOT independently parse temporal anchors per scene/chapter
#       and reason about same-anchor-different-time conflicts; true
#       anchor-format parsing is deferred to a Phase 7 Python helper.
#       Exit 0 if no candidates; exit 1 if candidates surfaced. Honors
#       body-only override marker
#       <!-- override: timeline-anchor-conflict -->. Pass --self-test for
#       built-in cases.
#
#   audit-tier-criterion <pass_dependencies_file> [<audits_root_dir>]
#       Verify audit tier assignments in pass-dependencies.md §4a/§4b
#       satisfy criterion 1 (named hard gates / Must-Fix floor) of the
#       §4c Audit Tier Promotion Criteria for any audit at Hard
#       Prerequisite / Pre-DE Prerequisite / Auto-run / Auto-recommend
#       before synthesis tier. Criteria 2 (undetectable-by-passes) and
#       3 (disclosure-non-equivalence) require model judgment and are
#       not mechanically verified. Per-audit override marker:
#       <!-- override: audit-tier-criterion-<audit-slug> -->. Pass
#       --self-test for built-in cases.
#
#   argument-recon-prerequisite <run_folder> [<editorial_letter_file>]
#       Verify argument-shaped runs satisfy the Field Reconnaissance
#       prerequisite per pass-dependencies.md §4a (Hard Prerequisite or
#       Auto-recommend before synthesis) and v1.7.9 wiring. When
#       argument-engine artifacts (Argument_State.md, Red_Team_Memo.md,
#       Argument_Evidence.md, etc.) are present in the run folder, the
#       validator requires either (a) Field_Reconnaissance_Report.md in
#       the run folder, or (b) the canonical blind-spot disclosure
#       ("literature-counterevidence not surveyed") in the editorial
#       letter per run-synthesis.md §Step 3. Body-only override marker:
#       <!-- override: argument-recon-prerequisite -->. Pass --self-test
#       for built-in cases.
#
# Exit codes:
#   0 — all checks pass
#   1 — validation failure (details on stdout)
#   2 — usage error

set -euo pipefail

usage() {
  echo "Usage: $0 <command> [args...]"
  echo "Commands: contract-hash, contract-check, ledger-check, artifact-names, synthesis-sections, tone-check, state-lines, severity-floor, audit-signal-propagation, underdiagnosis-triggers, ledger-consolidation, decision-layer-check, quality-risk-triggers, timeline-diff, timeline-arithmetic, timeline-anchor-conflict, audit-tier-criterion, argument-recon-prerequisite"
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

  tone-check)
    if [ $# -lt 1 ]; then echo "Usage: $0 tone-check <editorial_letter_file>"; exit 2; fi
    if [ ! -f "$1" ]; then echo "Error: File not found: $1" >&2; exit 2; fi
    LETTER="$1"
    ERRORS=0

    declare -a BLOCKED=(
      "masterpiece"
      "stunning"
      "flawless"
      "clean bill"
      "tour de force"
      "triumph"
      "perfection"
    )

    for word in "${BLOCKED[@]}"; do
      # Case insensitive word boundary match
      if grep -iq "\b${word}\b" "$LETTER"; then
        echo "ERROR: Blocked superlative found: '${word}'"
        ERRORS=$((ERRORS + 1))
      fi
    done

    if [ "$ERRORS" -gt 0 ]; then
      echo ""
      echo "FAILED: ${ERRORS} blocked superlative(s) found in editorial letter."
      echo "NOTE: The framework enforces rigorous diagnosis; sycophantic praise is not permitted."
      exit 1
    else
      echo "OK: No blocked superlatives found. Severity tone is compliant."
      exit 0
    fi
    ;;

  state-lines)
    if [ $# -lt 1 ]; then echo "Usage: $0 state-lines <diagnostic_state_file>"; exit 2; fi
    if [ ! -f "$1" ]; then echo "Error: File not found: $1" >&2; exit 2; fi
    wc -l < "$1"
    ;;

  # ----------------------------------------------------------------------
  # severity-floor — canonical home: output-policy.md §Severity Floor Rules.
  #
  # Mechanically checks the three rules:
  #   Rule 1: A core-promise axis rated Weak (High or Medium intensity)
  #           must produce at least one Must-Fix flag.
  #   Rule 2: A Must-Fix flag with Systemic blast radius caps the verdict
  #           at Partial Fit (no "publishable as-is"-tier verdicts).
  #   Rule 3: Three or more Should-Fix-or-above flags require explicit
  #           justification before assigning the highest positive verdict band.
  #
  # Override-with-rationale: structured HTML-comment markers placed in the
  # letter body (above the first Appendix heading) downgrade a per-rule
  # failure to a WARN. Marker syntax (one per rule):
  #   <!-- override: severity-floor-weak-axis — <rationale> -->
  #   <!-- override: severity-floor-systemic — <rationale> -->
  #   <!-- override: severity-floor-band-cap — <rationale> -->
  # Markers in appendix bodies are ignored (synthesis body is canonical for
  # findings; appendices hold evidence). Validator surfaces; model owns the
  # final decision.
  #
  # Self-test: pass --self-test as the only argument to run built-in cases.
  # ----------------------------------------------------------------------
  severity-floor)
    if [ $# -lt 1 ]; then echo "Usage: $0 severity-floor <editorial_letter_file> [<ledger_file>] | --self-test"; exit 2; fi

    if [ "$1" = "--self-test" ]; then
      TMPDIR=$(mktemp -d)
      trap 'rm -rf "$TMPDIR"' EXIT
      # Positive: clean letter — no Weak axes, no Systemic, < 3 Should-Fix.
      cat > "$TMPDIR/pos.md" <<'EOF'
# Development Edit
## What Needs Work
Pacing Should-Fix flag in Part I.
## Appendix B
Severity Calibration: tested upward and downward.
EOF
      # Negative 1: Weak axis, no Must-Fix, no marker.
      cat > "$TMPDIR/neg1.md" <<'EOF'
# Development Edit
## What the Book Does Best
Voice axis rated Weak at High intensity.
## What Needs Work
Pacing Should-Fix flag.
## Appendix B
Severity Calibration: tested.
EOF
      # Negative 2: Systemic Must-Fix paired with Strong Fit verdict, no marker.
      cat > "$TMPDIR/neg2.md" <<'EOF'
# Development Edit
## The Short Version
Verdict: Strong Fit.
## What Needs Work
Must-Fix: structural pattern with Systemic blast radius.
EOF
      # Negative 3: 4 Should-Fix flags + highest band, no justification, no marker.
      cat > "$TMPDIR/neg3.md" <<'EOF'
# Development Edit
## The Short Version
Verdict: publishable as-is.
## What Needs Work
Should-Fix one. Should-Fix two. Should-Fix three. Should-Fix four.
EOF
      # Override 1: Weak axis with body-placed marker → WARN, exit 0.
      cat > "$TMPDIR/over1.md" <<'EOF'
# Development Edit
## What the Book Does Best
Voice axis rated Weak at High intensity.
<!-- override: severity-floor-weak-axis — Weak rating reflects editorial-stance, not craft failure; documented in Appendix B. -->
## What Needs Work
Pacing Should-Fix flag.
## Appendix B
Severity Calibration: tested.
EOF
      # Override-in-appendix only: marker outside body → still ERROR.
      cat > "$TMPDIR/over_appx.md" <<'EOF'
# Development Edit
## What the Book Does Best
Voice axis rated Weak at High intensity.
## What Needs Work
Pacing Should-Fix flag.
## Appendix B
Severity Calibration: tested.
<!-- override: severity-floor-weak-axis — Marker placed in appendix only. -->
EOF
      RESULTS=0
      "$0" severity-floor "$TMPDIR/pos.md" >/dev/null 2>&1 && echo "  pos: OK" || { echo "  pos: FAIL (expected OK)"; RESULTS=1; }
      "$0" severity-floor "$TMPDIR/neg1.md" >/dev/null 2>&1 && { echo "  neg1: FAIL (expected ERROR)"; RESULTS=1; } || echo "  neg1: OK (caught)"
      "$0" severity-floor "$TMPDIR/neg2.md" >/dev/null 2>&1 && { echo "  neg2: FAIL (expected ERROR)"; RESULTS=1; } || echo "  neg2: OK (caught)"
      "$0" severity-floor "$TMPDIR/neg3.md" >/dev/null 2>&1 && { echo "  neg3: FAIL (expected ERROR)"; RESULTS=1; } || echo "  neg3: OK (caught)"
      "$0" severity-floor "$TMPDIR/over1.md" >/dev/null 2>&1 && echo "  over1: OK (marker in body downgraded ERROR→WARN)" || { echo "  over1: FAIL (expected OK after override)"; RESULTS=1; }
      "$0" severity-floor "$TMPDIR/over_appx.md" >/dev/null 2>&1 && { echo "  over_appx: FAIL (appendix-only marker should not downgrade)"; RESULTS=1; } || echo "  over_appx: OK (caught — marker in appendix is non-canonical)"
      [ "$RESULTS" -eq 0 ] && { echo "Self-test: PASS"; exit 0; } || { echo "Self-test: FAIL"; exit 1; }
    fi

    if [ ! -f "$1" ]; then echo "Error: File not found: $1" >&2; exit 2; fi
    LETTER="$1"
    ERRORS=0

    # Split letter into body (above first Appendix heading) and appendix.
    # Markers in appendix bodies are ignored — synthesis body is canonical
    # for findings; appendices hold evidence.
    APPENDIX_LINE=$(grep -niE "^#{1,4}.*Appendix [A-C]" "$LETTER" 2>/dev/null | head -1 | cut -d: -f1 || true)
    if [ -n "$APPENDIX_LINE" ]; then
      BODY=$(sed -n "1,$((APPENDIX_LINE - 1))p" "$LETTER")
    else
      BODY=$(cat "$LETTER")
    fi

    # Per-rule marker detection — body only.
    OVERRIDE_WEAK_AXIS=0
    OVERRIDE_SYSTEMIC=0
    OVERRIDE_BAND_CAP=0
    echo "$BODY" | grep -F "<!-- override: severity-floor-weak-axis" > /dev/null 2>&1 && OVERRIDE_WEAK_AXIS=1
    echo "$BODY" | grep -F "<!-- override: severity-floor-systemic" > /dev/null 2>&1 && OVERRIDE_SYSTEMIC=1
    echo "$BODY" | grep -F "<!-- override: severity-floor-band-cap" > /dev/null 2>&1 && OVERRIDE_BAND_CAP=1

    # Rule 1: Weak axis at High/Medium intensity → ≥1 Must-Fix.
    if grep -iE "Weak (at )?(High|Medium)" "$LETTER" > /dev/null 2>&1; then
      MUSTFIX_COUNT=$( { grep -oiE "Must-Fix" "$LETTER" || true; } | wc -l | tr -d ' ')
      MUSTFIX_COUNT=${MUSTFIX_COUNT:-0}
      if [ "$MUSTFIX_COUNT" -lt 1 ]; then
        if [ "$OVERRIDE_WEAK_AXIS" -eq 1 ]; then
          echo "WARN: Rule 1 — Weak axis present at High/Medium intensity with no Must-Fix flag (override marker detected in letter body)."
        else
          echo "ERROR: Rule 1 — Weak core-promise axis at High/Medium intensity but no Must-Fix flag (no override marker in body)."
          ERRORS=$((ERRORS + 1))
        fi
      fi
    fi

    # Rule 2: Systemic Must-Fix → verdict ≤ Partial Fit.
    if grep -iE "Systemic" "$LETTER" > /dev/null 2>&1 && grep -iE "Must-Fix" "$LETTER" > /dev/null 2>&1; then
      if grep -iE "(Strong Fit|publishable as[- ]is|Highest Band|Excellent Fit)" "$LETTER" > /dev/null 2>&1; then
        if [ "$OVERRIDE_SYSTEMIC" -eq 1 ]; then
          echo "WARN: Rule 2 — Systemic Must-Fix paired with high verdict band (override marker detected in letter body)."
        else
          echo "ERROR: Rule 2 — Systemic Must-Fix flag present but verdict exceeds Partial Fit ceiling (no override marker in body)."
          ERRORS=$((ERRORS + 1))
        fi
      fi
    fi

    # Rule 3: ≥3 Should-Fix-or-above → highest positive band needs justification.
    SHOULDFIX_COUNT=$( { grep -oiE "Should-Fix" "$LETTER" || true; } | wc -l | tr -d ' ')
    SHOULDFIX_COUNT=${SHOULDFIX_COUNT:-0}
    MUSTFIX_COUNT=$( { grep -oiE "Must-Fix" "$LETTER" || true; } | wc -l | tr -d ' ')
    MUSTFIX_COUNT=${MUSTFIX_COUNT:-0}
    SF_TOTAL=$((SHOULDFIX_COUNT + MUSTFIX_COUNT))
    if [ "$SF_TOTAL" -ge 3 ]; then
      if grep -iE "(Strong Fit|publishable as[- ]is|Highest Band|Excellent Fit)" "$LETTER" > /dev/null 2>&1; then
        if grep -iE "(flag volume|justification|justified|does not impair)" "$LETTER" > /dev/null 2>&1; then
          : # justification present
        elif [ "$OVERRIDE_BAND_CAP" -eq 1 ]; then
          echo "WARN: Rule 3 — ≥3 Should-Fix-or-above flags with highest verdict band (override marker detected in letter body)."
        else
          echo "ERROR: Rule 3 — ${SF_TOTAL} Should-Fix-or-above flags with highest verdict band and no explicit justification (no override marker in body)."
          ERRORS=$((ERRORS + 1))
        fi
      fi
    fi

    if [ "$ERRORS" -gt 0 ]; then
      echo ""
      echo "FAILED: ${ERRORS} severity-floor rule failure(s). Canonical rules: core-editor/references/output-policy.md §Severity Floor Rules."
      exit 1
    else
      echo "OK: Severity-floor rules satisfied (or override marker present in body)."
      exit 0
    fi
    ;;

  # ----------------------------------------------------------------------
  # audit-signal-propagation — canonical rule:
  #   core-editor/references/run-synthesis.md §Step 2 — Canonical Audit-Signal
  #   Propagation Rule. Per-audit operationalization in
  #   pass-dependencies.md §4e (Audit-Signal Propagation Table).
  #
  # Verifies per-audit that audit-internal severity signals propagate to
  # synthesis-layer severity per this taxonomy:
  #   audit-internal Must-Fix floor   → synthesis Must-Fix
  #   audit-internal hard gate        → synthesis Must-Fix
  #   audit-internal HIGH (Alert)     → synthesis Must-Fix or Should-Fix
  #   audit-internal MEDIUM (Flag)    → synthesis Should-Fix
  #   audit-internal LOW (Note)       → synthesis Could-Fix
  #
  # Mechanics (v1.7.9): the validator no longer accepts a generic synthesis-
  # body Must-Fix / Should-Fix mention as evidence of propagation. For each
  # detected audit (named in any appendix subsection), each detected signal
  # class for that audit must reach the synthesis body either as a finding
  # that names the audit by name (e.g., "Reception Risk Alert at L2956") OR
  # as a finding tied to the audit's evidence (a manuscript line number from
  # the audit's appendix that also appears in a synthesis-body Must-Fix /
  # Should-Fix item). A letter that contains an unrelated Must-Fix in body
  # and a Reception Risk hard gate buried in Appendix A no longer passes.
  #
  # Override-with-rationale: structured HTML-comment markers placed in the
  # synthesis body (above the first Appendix heading) downgrade per-class
  # failures to WARN. Marker syntax (one per propagation class):
  #   <!-- override: audit-propagation-must-fix — <rationale> -->
  #   <!-- override: audit-propagation-hard-gate — <rationale> -->
  #   <!-- override: audit-propagation-high — <rationale> -->
  # A per-audit override marker form is also honored:
  #   <!-- override: audit-propagation-<audit-slug> — <rationale> -->
  # where <audit-slug> is the lowercase hyphenated audit name (e.g.
  # `reception-risk`, `compression`, `banister`). Markers in appendix
  # bodies are ignored (synthesis body is canonical for findings).
  # Validator surfaces; model owns the final decision.
  #
  # Self-test: pass --self-test as the only argument to run built-in cases.
  # ----------------------------------------------------------------------
  audit-signal-propagation)
    if [ $# -lt 1 ]; then echo "Usage: $0 audit-signal-propagation <editorial_letter_file> [<ledger_file>] | --self-test"; exit 2; fi

    if [ "$1" = "--self-test" ]; then
      TMPDIR=$(mktemp -d)
      trap 'rm -rf "$TMPDIR"' EXIT
      # Positive: audit hard gate present, audit named in synthesis Must-Fix.
      cat > "$TMPDIR/pos.md" <<'EOF'
# Development Edit
## What Needs Work
Reception Risk audit fired a hard gate at L2956; this surfaces as Must-Fix.
## Appendix A: Reception Risk Audit
Hard Gate triggered on Alert concentration at L2956.
EOF
      # Positive 2: audit hard gate present, evidence-line-shared between
      # appendix and synthesis body Must-Fix item (audit not named in body).
      cat > "$TMPDIR/pos2.md" <<'EOF'
# Development Edit
## What Needs Work
Must-Fix: aftermath compression at L2956 collapses the climax beat.
## Appendix A: Reception Risk Audit
Hard Gate triggered at L2956.
EOF
      # Negative 1: Hard gate from Reception Risk audit, no Must-Fix in
      # synthesis, no marker. Joshua's canonical false-pass case.
      cat > "$TMPDIR/neg1.md" <<'EOF'
# Development Edit
## What Needs Work
Some Should-Fix observations on pacing at L1200.
## Appendix A: Reception Risk Audit
Hard Gate triggered on Alert concentration at L2956.
EOF
      # Negative 1b: Joshua's exact canonical case — body Must-Fix exists
      # but is unrelated (different audit, different evidence). Phase 4-6
      # validator passed this; v1.7.9 catches it.
      cat > "$TMPDIR/neg1b.md" <<'EOF'
# Development Edit
## What Needs Work
- Must-Fix: Decision Pressure AV-1 at L500 (option suppression in Ch 1 §2).
## Appendix A: Reception Risk Audit
Hard Gate triggered on Alert concentration at L2956.
EOF
      # Negative 2: Audit Alert (HIGH) signal not surfaced at MF/SF, no marker.
      cat > "$TMPDIR/neg2.md" <<'EOF'
# Development Edit
## What Needs Work
Could-Fix items only at L100.
## Appendix A: Banister Audit
HIGH-confidence rhetorical-fairness failure at L1500.
EOF
      # Negative 3: Compression Must-Fix floor in audit, dropped to Could-Fix, no marker.
      cat > "$TMPDIR/neg3.md" <<'EOF'
# Development Edit
## What Needs Work
Could-Fix observations on prose tightening at L300.
## Appendix A: Compression Audit
Must-Fix floor fired on systemic compression failure at L4200.
EOF
      # Override: hard gate signal with body marker → WARN, exit 0.
      cat > "$TMPDIR/over1.md" <<'EOF'
# Development Edit
## What Needs Work
Some Should-Fix observations on pacing.
<!-- override: audit-propagation-hard-gate — Hard gate fired on a passage the manuscript already retracts; documented in Appendix B. -->
## Appendix A: Reception Risk Audit
Hard Gate triggered on Alert concentration at L2956.
EOF
      # Per-audit override: per-audit marker form.
      cat > "$TMPDIR/over2.md" <<'EOF'
# Development Edit
## What Needs Work
Should-Fix on pacing at L800.
<!-- override: audit-propagation-reception-risk — Calibration verified; alert is artifact-of-method per Appendix B. -->
## Appendix A: Reception Risk Audit
Hard Gate triggered at L2956.
EOF
      # Override-in-appendix only: marker outside body → still ERROR.
      cat > "$TMPDIR/over_appx.md" <<'EOF'
# Development Edit
## What Needs Work
Some Should-Fix observations on pacing.
## Appendix A: Reception Risk Audit
Hard Gate triggered on Alert concentration at L2956.
<!-- override: audit-propagation-hard-gate — Marker placed in appendix only. -->
EOF
      RESULTS=0
      "$0" audit-signal-propagation "$TMPDIR/pos.md" >/dev/null 2>&1 && echo "  pos: OK (audit named in body)" || { echo "  pos: FAIL (expected OK)"; RESULTS=1; }
      "$0" audit-signal-propagation "$TMPDIR/pos2.md" >/dev/null 2>&1 && echo "  pos2: OK (evidence line shared)" || { echo "  pos2: FAIL (expected OK — evidence-line propagation)"; RESULTS=1; }
      "$0" audit-signal-propagation "$TMPDIR/neg1.md" >/dev/null 2>&1 && { echo "  neg1: FAIL (expected ERROR — no MF in body)"; RESULTS=1; } || echo "  neg1: OK (caught — no Must-Fix at all)"
      "$0" audit-signal-propagation "$TMPDIR/neg1b.md" >/dev/null 2>&1 && { echo "  neg1b: FAIL (Joshua's canonical case — unrelated MF must not satisfy)"; RESULTS=1; } || echo "  neg1b: OK (caught — unrelated Must-Fix doesn't satisfy Reception Risk hard gate)"
      "$0" audit-signal-propagation "$TMPDIR/neg2.md" >/dev/null 2>&1 && { echo "  neg2: FAIL (expected ERROR — Banister HIGH not propagated)"; RESULTS=1; } || echo "  neg2: OK (caught — Banister HIGH not propagated)"
      "$0" audit-signal-propagation "$TMPDIR/neg3.md" >/dev/null 2>&1 && { echo "  neg3: FAIL (expected ERROR — Compression Must-Fix floor not propagated)"; RESULTS=1; } || echo "  neg3: OK (caught — Compression floor not propagated)"
      "$0" audit-signal-propagation "$TMPDIR/over1.md" >/dev/null 2>&1 && echo "  over1: OK (class marker downgraded ERROR→WARN)" || { echo "  over1: FAIL (expected OK after override)"; RESULTS=1; }
      "$0" audit-signal-propagation "$TMPDIR/over2.md" >/dev/null 2>&1 && echo "  over2: OK (per-audit marker downgraded ERROR→WARN)" || { echo "  over2: FAIL (expected OK after per-audit override)"; RESULTS=1; }
      "$0" audit-signal-propagation "$TMPDIR/over_appx.md" >/dev/null 2>&1 && { echo "  over_appx: FAIL (appendix-only marker should not downgrade)"; RESULTS=1; } || echo "  over_appx: OK (caught — marker in appendix is non-canonical)"
      [ "$RESULTS" -eq 0 ] && { echo "Self-test: PASS"; exit 0; } || { echo "Self-test: FAIL"; exit 1; }
    fi

    if [ ! -f "$1" ]; then echo "Error: File not found: $1" >&2; exit 2; fi
    LETTER="$1"
    ERRORS=0

    # Split letter into synthesis body (before Appendix) and audit appendix
    # (Appendix A onward, where audit findings typically live). This lets us
    # distinguish synthesis-layer severity tiers from audit-internal mentions
    # AND restrict override markers to the canonical-body region.
    APPENDIX_LINE=$(grep -niE "^#{1,4}.*Appendix [A-C]" "$LETTER" 2>/dev/null | head -1 | cut -d: -f1 || true)
    if [ -n "$APPENDIX_LINE" ]; then
      SYNTH_BODY=$(sed -n "1,$((APPENDIX_LINE - 1))p" "$LETTER")
      APPX_BODY=$(sed -n "${APPENDIX_LINE},\$p" "$LETTER")
    else
      SYNTH_BODY=$(cat "$LETTER")
      APPX_BODY=""
    fi

    # Per-class override marker detection — body only.
    OVERRIDE_MUST_FIX=0
    OVERRIDE_HARD_GATE=0
    OVERRIDE_HIGH=0
    echo "$SYNTH_BODY" | grep -F "<!-- override: audit-propagation-must-fix" > /dev/null 2>&1 && OVERRIDE_MUST_FIX=1
    echo "$SYNTH_BODY" | grep -F "<!-- override: audit-propagation-hard-gate" > /dev/null 2>&1 && OVERRIDE_HARD_GATE=1
    echo "$SYNTH_BODY" | grep -F "<!-- override: audit-propagation-high" > /dev/null 2>&1 && OVERRIDE_HIGH=1

    # Per-audit override marker detection — body only. The marker form is
    # `<!-- override: audit-propagation-<audit-slug> — <rationale> -->` where
    # <audit-slug> is the lowercase-hyphenated audit name. Captured into
    # PER_AUDIT_OVERRIDES as a space-delimited list.
    PER_AUDIT_OVERRIDES=$(echo "$SYNTH_BODY" \
      | grep -oE "<!-- override: audit-propagation-[a-z][a-z0-9-]*" \
      | sed -E 's/<!-- override: audit-propagation-//' \
      | tr '\n' ' ' || true)

    # Helper: check whether a per-audit override slug matches a given audit
    # slug. Used below.
    has_per_audit_override() {
      local needle="$1"
      case " $PER_AUDIT_OVERRIDES " in
        *" $needle "*) return 0 ;;
        *) return 1 ;;
      esac
    }

    # Detect audit appendices. Heuristic: appendix headings or subsection
    # headings that contain "<Audit Name> Audit" or "<Audit Name> audit"
    # (case-insensitive). The audit name token is captured. Also detect
    # in-appendix prose mentions like "Compression audit reported".
    # We look across the appendix body only (ignore body mentions of
    # "Reception Risk audit" since those are the synthesis-layer references
    # we are testing for).
    #
    # Audits enumerated in pass-dependencies.md §4e are recognized; un-
    # enumerated audits fall back to the canonical default mapping (per
    # §4e footer). The recognizer is pattern-based, not table-driven —
    # the canonical table itself is the source of truth.
    AUDIT_NAMES=$(echo "$APPX_BODY" \
      | grep -oiE "([A-Z][A-Za-z/&-]+( [A-Z][A-Za-z/&-]+){0,3}) [Aa]udit" \
      | sed -E 's/ [Aa]udit$//' \
      | sort -u \
      | tr '\n' '|' || true)
    # Strip trailing pipe.
    AUDIT_NAMES=${AUDIT_NAMES%|}

    # Helper: convert an audit display name to its canonical slug
    # (lowercase, spaces → hyphens, slashes → hyphens, ampersands dropped).
    audit_slug() {
      echo "$1" \
        | tr '[:upper:]' '[:lower:]' \
        | sed -E 's/&//g; s/[[:space:]/]+/-/g; s/-+/-/g; s/^-//; s/-$//'
    }

    # Helper: extract evidence line numbers (e.g., "L2956", "line 2956") from
    # a chunk of text. Returns sorted unique list.
    extract_evidence_lines() {
      echo "$1" \
        | grep -oiE "(L|line )[0-9]+" \
        | sed -E 's/^(L|line )//I' \
        | sort -u
    }

    # Helper: per-audit propagation check. Args: audit-display-name,
    # signal-class (must-fix-floor|hard-gate|high|medium|low), required-
    # synthesis-tier (must-fix|must-or-should|should-fix|could-fix).
    #
    # A signal is "propagated" when at least one of:
    #   (a) the synthesis body contains a Must-Fix / Should-Fix / Could-Fix
    #       item that names the audit by name (case-insensitive substring
    #       match) at the required tier, OR
    #   (b) the synthesis body contains a Must-Fix / Should-Fix / Could-Fix
    #       item that cites at least one evidence line number that also
    #       appears in this audit's appendix subsection.
    #
    # If neither holds, the signal is un-propagated. Honors per-class
    # override markers AND per-audit override markers (body only).
    check_audit_signal() {
      local audit_name="$1"
      local signal_class="$2"
      local required_tier="$3"
      local audit_slug
      audit_slug=$(audit_slug "$audit_name")

      # Extract this audit's appendix subsection (heuristic: from the
      # heading containing the audit name through the next heading or
      # end of file).
      local subsection
      subsection=$(echo "$APPX_BODY" \
        | awk -v name="$audit_name" '
            BEGIN { in_section = 0 }
            tolower($0) ~ tolower(name) " audit" && /^#/ { in_section = 1; print; next }
            in_section && /^#/ { exit }
            in_section { print }
          ')
      # Fallback: if no heading match, treat the appendix-wide mentions
      # of this audit as its evidence pool.
      if [ -z "$subsection" ]; then
        subsection=$(echo "$APPX_BODY" \
          | grep -iE "${audit_name} audit" -A 5 || true)
      fi

      local audit_lines
      audit_lines=$(extract_evidence_lines "$subsection")

      # Build the body's severity-tier item list per required tier.
      local body_items
      case "$required_tier" in
        must-fix)
          body_items=$(echo "$SYNTH_BODY" | grep -iE "Must-Fix" || true)
          ;;
        must-or-should)
          body_items=$(echo "$SYNTH_BODY" | grep -iE "Must-Fix|Should-Fix" || true)
          ;;
        should-fix)
          body_items=$(echo "$SYNTH_BODY" | grep -iE "Should-Fix" || true)
          ;;
        could-fix)
          body_items=$(echo "$SYNTH_BODY" | grep -iE "Could-Fix" || true)
          ;;
      esac

      # (a) Audit-name match in any qualifying body item.
      local name_match=0
      if [ -n "$body_items" ] && echo "$body_items" | grep -iE "${audit_name}" > /dev/null 2>&1; then
        name_match=1
      fi

      # (b) Evidence-line match in any qualifying body item.
      local line_match=0
      if [ -n "$audit_lines" ] && [ -n "$body_items" ]; then
        local body_lines
        body_lines=$(extract_evidence_lines "$body_items")
        if [ -n "$body_lines" ]; then
          local shared
          shared=$(comm -12 <(echo "$audit_lines") <(echo "$body_lines") 2>/dev/null | head -1)
          [ -n "$shared" ] && line_match=1
        fi
      fi

      if [ "$name_match" -eq 1 ] || [ "$line_match" -eq 1 ]; then
        return 0
      fi

      # Not propagated. Check per-class and per-audit overrides.
      local class_override=0
      case "$signal_class" in
        must-fix-floor) [ "$OVERRIDE_MUST_FIX" -eq 1 ] && class_override=1 ;;
        hard-gate)      [ "$OVERRIDE_HARD_GATE" -eq 1 ] && class_override=1 ;;
        high)           [ "$OVERRIDE_HIGH" -eq 1 ]      && class_override=1 ;;
      esac
      local per_audit_override=0
      has_per_audit_override "$audit_slug" && per_audit_override=1

      if [ "$class_override" -eq 1 ] || [ "$per_audit_override" -eq 1 ]; then
        local marker_kind="class"
        [ "$per_audit_override" -eq 1 ] && marker_kind="per-audit (audit-propagation-${audit_slug})"
        echo "WARN: ${audit_name} ${signal_class} signal not propagated to synthesis body (override marker present in body — ${marker_kind})."
        return 0
      fi

      echo "ERROR: ${audit_name} ${signal_class} signal in appendix did not propagate to synthesis-body ${required_tier} item (no audit-name reference and no shared evidence-line; no override marker in body)."
      return 1
    }

    # If no audit appendix subsections detected, fall back to the legacy
    # whole-letter taxonomy check (preserves Phase 4 behavior for letters
    # that mention severity signals without a dedicated audit appendix).
    if [ -z "$AUDIT_NAMES" ]; then
      SYNTH_MUSTFIX=0
      SYNTH_SHOULDFIX=0
      echo "$SYNTH_BODY" | grep -iE "Must-Fix" > /dev/null 2>&1 && SYNTH_MUSTFIX=1
      echo "$SYNTH_BODY" | grep -iE "Should-Fix" > /dev/null 2>&1 && SYNTH_SHOULDFIX=1

      if grep -iE "hard gate" "$LETTER" > /dev/null 2>&1; then
        if [ "$SYNTH_MUSTFIX" -eq 0 ]; then
          if [ "$OVERRIDE_HARD_GATE" -eq 1 ]; then
            echo "WARN: Audit hard gate present without synthesis-layer Must-Fix (override marker detected in body)."
          else
            echo "ERROR: Audit hard gate present but no synthesis-layer Must-Fix flag (no override marker in body)."
            ERRORS=$((ERRORS + 1))
          fi
        fi
      fi
      if grep -iE "Must-Fix floor" "$LETTER" > /dev/null 2>&1; then
        if [ "$SYNTH_MUSTFIX" -eq 0 ]; then
          if [ "$OVERRIDE_MUST_FIX" -eq 1 ]; then
            echo "WARN: Audit Must-Fix floor present without synthesis-layer Must-Fix (override marker detected in body)."
          else
            echo "ERROR: Audit Must-Fix floor present but no synthesis-layer Must-Fix flag (no override marker in body)."
            ERRORS=$((ERRORS + 1))
          fi
        fi
      fi
      if grep -iE "(HIGH[- ]severity|Alert finding|Alert concentration|HIGH signal|HIGH rating)" "$LETTER" > /dev/null 2>&1; then
        if [ "$SYNTH_MUSTFIX" -eq 0 ] && [ "$SYNTH_SHOULDFIX" -eq 0 ]; then
          if [ "$OVERRIDE_HIGH" -eq 1 ]; then
            echo "WARN: Audit HIGH/Alert signal present without synthesis Must-Fix or Should-Fix (override marker detected in body)."
          else
            echo "ERROR: Audit HIGH/Alert signal present but no synthesis Must-Fix or Should-Fix (no override marker in body)."
            ERRORS=$((ERRORS + 1))
          fi
        fi
      fi
    else
      # Per-audit propagation check (v1.7.9 tightening).
      OLDIFS=$IFS
      IFS='|'
      for audit_name in $AUDIT_NAMES; do
        IFS=$OLDIFS
        [ -z "$audit_name" ] && continue
        # Extract this audit's appendix subsection text once.
        subsection_text=$(echo "$APPX_BODY" \
          | awk -v name="$audit_name" '
              BEGIN { in_section = 0 }
              tolower($0) ~ tolower(name) " audit" && /^#/ { in_section = 1; print; next }
              in_section && /^#/ { exit }
              in_section { print }
            ')
        if [ -z "$subsection_text" ]; then
          subsection_text=$(echo "$APPX_BODY" | grep -iE "${audit_name} audit" -A 8 || true)
        fi

        # Detect per-audit signal classes in this subsection. Hard-gate
        # and Must-Fix-floor are the strongest signals; if either fires,
        # any HIGH/Alert mention in the same subsection is treated as
        # part of the strong signal's context, not as a separate signal
        # (Reception Risk hard gates typically describe themselves as
        # "Hard Gate triggered on Alert concentration" — one signal, two
        # words).
        SAW_STRONG=0
        if echo "$subsection_text" | grep -iE "(hard gate|hard-gate)" > /dev/null 2>&1; then
          check_audit_signal "$audit_name" "hard-gate" "must-fix" || ERRORS=$((ERRORS + 1))
          SAW_STRONG=1
        fi
        if echo "$subsection_text" | grep -iE "Must-Fix floor" > /dev/null 2>&1; then
          check_audit_signal "$audit_name" "must-fix-floor" "must-fix" || ERRORS=$((ERRORS + 1))
          SAW_STRONG=1
        fi
        if [ "$SAW_STRONG" -eq 0 ] && echo "$subsection_text" | grep -iE "(HIGH[- ]severity|Alert finding|Alert concentration|HIGH signal|HIGH rating|HIGH-severity|HIGH-confidence)" > /dev/null 2>&1; then
          check_audit_signal "$audit_name" "high" "must-or-should" || ERRORS=$((ERRORS + 1))
        fi
        IFS='|'
      done
      IFS=$OLDIFS
    fi

    if [ "$ERRORS" -gt 0 ]; then
      echo ""
      echo "FAILED: ${ERRORS} audit-signal propagation failure(s). Canonical rule: core-editor/references/run-synthesis.md §Step 2; per-audit table: pass-dependencies.md §4e."
      exit 1
    else
      echo "OK: Audit-internal severity signals propagated to synthesis layer (per-audit; or override marker present in body)."
      exit 0
    fi
    ;;

  # ----------------------------------------------------------------------
  # underdiagnosis-triggers — canonical home: run-synthesis.md §Step 9
  # (Conditional Underdiagnosis Retry Loop).
  #
  # Detects six enumerated triggers. Validator surfaces; the model still
  # owns the upgrade-or-override decision and must either re-tier the
  # affected finding(s) or document an override via:
  #   <!-- override: underdiagnosis-trigger-<id> — <rationale> -->
  # placed in the letter body (above the first Appendix heading).
  #
  # Trigger IDs:
  #   convergence       — same concern in 3+ pass/audit artifacts
  #   hard-gate         — any high-risk audit Alert or hard gate
  #   final-third       — final-third concern in both character + structure passes
  #   multi-axis        — concern spans 2+ severity classes (series/representation/trust)
  #   severity-floor    — `validate.sh severity-floor` returned WARN or FAIL
  #   propagation       — `validate.sh audit-signal-propagation` returned ERROR/WARN
  #
  # Self-test: pass --self-test as the only argument to run built-in cases.
  # ----------------------------------------------------------------------
  underdiagnosis-triggers)
    if [ $# -lt 1 ]; then echo "Usage: $0 underdiagnosis-triggers <editorial_letter_file> [<ledger_file>] | --self-test"; exit 2; fi

    if [ "$1" = "--self-test" ]; then
      TMPDIR=$(mktemp -d)
      trap 'rm -rf "$TMPDIR"' EXIT
      # Positive: clean letter, no triggers fire.
      cat > "$TMPDIR/pos.md" <<'EOF'
# Development Edit
## What the Book Does Best
Voice is strong throughout.
## What Needs Work
A single Should-Fix on Part II pacing.
## Appendix A
Pass 1 noted pacing in Part II. No further convergence.
EOF
      # Negative 1: convergence — same mechanism named in 3+ artifacts, no upgrade.
      cat > "$TMPDIR/neg1.md" <<'EOF'
# Development Edit
## What Needs Work
A Should-Fix on aftermath compression.
## Appendix A
Pass 1: aftermath compression observed.
Pass 5: aftermath compression contributes to character-arc collapse.
Pass 8: aftermath compression named again at the climax.
Reception Risk audit also flagged aftermath compression.
EOF
      # Negative 2: hard-gate — audit Alert/hard gate present, no synthesis Must-Fix.
      cat > "$TMPDIR/neg2.md" <<'EOF'
# Development Edit
## What Needs Work
Could-Fix items only.
## Appendix A
Reception Risk audit: hard gate triggered on Alert concentration.
EOF
      # Negative 3: final-third — character + structure passes both flag final third.
      cat > "$TMPDIR/neg3.md" <<'EOF'
# Development Edit
## What Needs Work
A Could-Fix on minor pacing in the close.
## Appendix A
Character pass flagged final-third arc collapse.
Structure pass flagged final-third compression.
EOF
      # Override: convergence trigger fires but body marker present → WARN, exit 0.
      cat > "$TMPDIR/over1.md" <<'EOF'
# Development Edit
## What Needs Work
A Should-Fix on aftermath compression.
<!-- override: underdiagnosis-trigger-convergence — Three convergent flags name the same Should-Fix; severity stands per Appendix B rationale. -->
## Appendix A
Pass 1: aftermath compression observed.
Pass 5: aftermath compression contributes to character-arc collapse.
Pass 8: aftermath compression named again at the climax.
EOF
      RESULTS=0
      "$0" underdiagnosis-triggers "$TMPDIR/pos.md" >/dev/null 2>&1 && echo "  pos: OK" || { echo "  pos: FAIL (expected OK)"; RESULTS=1; }
      "$0" underdiagnosis-triggers "$TMPDIR/neg1.md" >/dev/null 2>&1 && { echo "  neg1: FAIL (expected ERROR — convergence)"; RESULTS=1; } || echo "  neg1: OK (convergence trigger caught)"
      "$0" underdiagnosis-triggers "$TMPDIR/neg2.md" >/dev/null 2>&1 && { echo "  neg2: FAIL (expected ERROR — hard-gate)"; RESULTS=1; } || echo "  neg2: OK (hard-gate trigger caught)"
      "$0" underdiagnosis-triggers "$TMPDIR/neg3.md" >/dev/null 2>&1 && { echo "  neg3: FAIL (expected ERROR — final-third)"; RESULTS=1; } || echo "  neg3: OK (final-third trigger caught)"
      "$0" underdiagnosis-triggers "$TMPDIR/over1.md" >/dev/null 2>&1 && echo "  over1: OK (marker in body downgraded ERROR→WARN)" || { echo "  over1: FAIL (expected OK after override)"; RESULTS=1; }
      [ "$RESULTS" -eq 0 ] && { echo "Self-test: PASS"; exit 0; } || { echo "Self-test: FAIL"; exit 1; }
    fi

    if [ ! -f "$1" ]; then echo "Error: File not found: $1" >&2; exit 2; fi
    LETTER="$1"
    LEDGER="${2:-}"
    ERRORS=0
    FIRED=""

    # Split letter into body (above first Appendix) and appendix (Appendix
    # A onward). Synthesis body is canonical for findings AND for override
    # markers; appendix holds evidence and audit findings.
    APPENDIX_LINE=$(grep -niE "^#{1,4}.*Appendix [A-C]" "$LETTER" 2>/dev/null | head -1 | cut -d: -f1 || true)
    if [ -n "$APPENDIX_LINE" ]; then
      BODY=$(sed -n "1,$((APPENDIX_LINE - 1))p" "$LETTER")
    else
      BODY=$(cat "$LETTER")
    fi

    # Per-trigger marker detection — body only.
    OV_CONV=0; OV_HG=0; OV_FT=0; OV_MA=0; OV_SF=0; OV_PROP=0
    echo "$BODY" | grep -F "<!-- override: underdiagnosis-trigger-convergence" > /dev/null 2>&1 && OV_CONV=1
    echo "$BODY" | grep -F "<!-- override: underdiagnosis-trigger-hard-gate" > /dev/null 2>&1 && OV_HG=1
    echo "$BODY" | grep -F "<!-- override: underdiagnosis-trigger-final-third" > /dev/null 2>&1 && OV_FT=1
    echo "$BODY" | grep -F "<!-- override: underdiagnosis-trigger-multi-axis" > /dev/null 2>&1 && OV_MA=1
    echo "$BODY" | grep -F "<!-- override: underdiagnosis-trigger-severity-floor" > /dev/null 2>&1 && OV_SF=1
    echo "$BODY" | grep -F "<!-- override: underdiagnosis-trigger-propagation" > /dev/null 2>&1 && OV_PROP=1

    BODY_MUSTFIX=0
    echo "$BODY" | grep -iE "Must-Fix" > /dev/null 2>&1 && BODY_MUSTFIX=1

    # Trigger 1: convergence. Heuristic: at least 3 occurrences of a shared
    # mechanism keyword across passes/audits in the letter (or in the
    # ledger if provided), with no synthesis-layer Must-Fix on it.
    # Mechanism keywords scanned: aftermath, compression, status, thread,
    # final-third, coercion, agency, opacity. Threshold: ≥3 occurrences of
    # the same keyword across the whole letter.
    CONV_HIT=""
    for kw in aftermath compression status thread "final-third" coercion agency opacity; do
      COUNT=$( { grep -oiE "$kw" "$LETTER" || true; } | wc -l | tr -d ' ')
      COUNT=${COUNT:-0}
      if [ "$COUNT" -ge 3 ] && [ "$BODY_MUSTFIX" -eq 0 ]; then
        CONV_HIT="$kw"
        break
      fi
    done
    if [ -n "$CONV_HIT" ]; then
      if [ "$OV_CONV" -eq 1 ]; then
        echo "WARN: Trigger #1 (convergence) — '${CONV_HIT}' appears in 3+ artifacts with no synthesis Must-Fix (override marker detected in body)."
      else
        echo "ERROR: Trigger #1 (convergence) — '${CONV_HIT}' appears in 3+ artifacts with no synthesis Must-Fix and no override marker in body."
        ERRORS=$((ERRORS + 1))
      fi
      FIRED="${FIRED}convergence "
    fi

    # Trigger 2: hard-gate. Heuristic: any "hard gate" or "Alert" reference in
    # the letter (typically in audit appendix) with no synthesis Must-Fix.
    if grep -iE "(hard gate|Alert (concentration|finding))" "$LETTER" > /dev/null 2>&1; then
      if [ "$BODY_MUSTFIX" -eq 0 ]; then
        if [ "$OV_HG" -eq 1 ]; then
          echo "WARN: Trigger #2 (hard-gate) — high-risk audit Alert/hard gate present without synthesis Must-Fix (override marker detected in body)."
        else
          echo "ERROR: Trigger #2 (hard-gate) — high-risk audit Alert/hard gate present without synthesis Must-Fix and no override marker in body."
          ERRORS=$((ERRORS + 1))
        fi
        FIRED="${FIRED}hard-gate "
      fi
    fi

    # Trigger 3: final-third complication — character pass + structure pass
    # both flag the final third with no synthesis Must-Fix on it.
    if grep -iE "(character pass|character audit).*(final[- ]third|act[- ]?(III|3)|close|climax)" "$LETTER" > /dev/null 2>&1 \
       && grep -iE "(structure pass|structural pass|structure audit).*(final[- ]third|act[- ]?(III|3)|close|climax)" "$LETTER" > /dev/null 2>&1; then
      if [ "$BODY_MUSTFIX" -eq 0 ]; then
        if [ "$OV_FT" -eq 1 ]; then
          echo "WARN: Trigger #3 (final-third) — final-third concern flagged by both character + structure passes without synthesis Must-Fix (override marker in body)."
        else
          echo "ERROR: Trigger #3 (final-third) — final-third concern flagged by both character + structure passes without synthesis Must-Fix and no override marker in body."
          ERRORS=$((ERRORS + 1))
        fi
        FIRED="${FIRED}final-third "
      fi
    fi

    # Trigger 4: multi-axis severity. Heuristic: at least 2 of {series,
    # representation, reader-trust} severity classes are mentioned in the
    # letter on the same finding cluster, with no synthesis Must-Fix.
    AXIS_COUNT=0
    grep -iE "series" "$LETTER" > /dev/null 2>&1 && AXIS_COUNT=$((AXIS_COUNT + 1))
    grep -iE "representation" "$LETTER" > /dev/null 2>&1 && AXIS_COUNT=$((AXIS_COUNT + 1))
    grep -iE "reader[- ]trust" "$LETTER" > /dev/null 2>&1 && AXIS_COUNT=$((AXIS_COUNT + 1))
    if [ "$AXIS_COUNT" -ge 2 ] && [ "$BODY_MUSTFIX" -eq 0 ]; then
      if [ "$OV_MA" -eq 1 ]; then
        echo "WARN: Trigger #4 (multi-axis) — concern spans ${AXIS_COUNT}+ severity classes without synthesis Must-Fix (override marker in body)."
      else
        echo "ERROR: Trigger #4 (multi-axis) — concern spans ${AXIS_COUNT}+ severity classes (series/representation/reader-trust) without synthesis Must-Fix and no override marker in body."
        ERRORS=$((ERRORS + 1))
      fi
      FIRED="${FIRED}multi-axis "
    fi

    # Trigger 5: severity-floor — invoke validate.sh severity-floor; if it
    # returns ≠0 (FAIL) or emits WARN, fire trigger.
    SF_OUT=$("$0" severity-floor "$LETTER" 2>&1 || true)
    SF_RC=$?
    if echo "$SF_OUT" | grep -E "^(WARN|ERROR|FAILED)" > /dev/null 2>&1; then
      if [ "$OV_SF" -eq 1 ]; then
        echo "WARN: Trigger #5 (severity-floor) — severity-floor validator surfaced WARN/ERROR (override marker in body)."
      else
        echo "ERROR: Trigger #5 (severity-floor) — severity-floor validator surfaced WARN/ERROR with no override marker in body."
        ERRORS=$((ERRORS + 1))
      fi
      FIRED="${FIRED}severity-floor "
    fi

    # Trigger 6: propagation — invoke validate.sh audit-signal-propagation;
    # if it surfaces ERROR/WARN, fire trigger.
    AP_OUT=$("$0" audit-signal-propagation "$LETTER" 2>&1 || true)
    if echo "$AP_OUT" | grep -E "^(WARN|ERROR|FAILED)" > /dev/null 2>&1; then
      if [ "$OV_PROP" -eq 1 ]; then
        echo "WARN: Trigger #6 (propagation) — audit-signal-propagation validator surfaced un-propagated signal (override marker in body)."
      else
        echo "ERROR: Trigger #6 (propagation) — audit-signal-propagation validator surfaced un-propagated signal with no override marker in body."
        ERRORS=$((ERRORS + 1))
      fi
      FIRED="${FIRED}propagation "
    fi

    if [ "$ERRORS" -gt 0 ]; then
      echo ""
      echo "FAILED: ${ERRORS} underdiagnosis trigger(s) fired. Triggers: ${FIRED}"
      echo "Synthesis must either upgrade the affected finding's severity OR insert an override marker in the letter body. Canonical home: core-editor/references/run-synthesis.md §Step 9."
      exit 1
    else
      if [ -n "$FIRED" ]; then
        echo "OK: Triggers fired (${FIRED}); all addressed via override markers in body."
      else
        echo "OK: No underdiagnosis triggers fired."
      fi
      exit 0
    fi
    ;;

  # ----------------------------------------------------------------------
  # ledger-consolidation — canonical home: run-synthesis.md §Step 2
  # (Findings Ledger Consolidation Contract).
  #
  # Verifies that a consolidated Findings Ledger satisfies the contract:
  #   1. Consolidation actually happened (raw "Pass N Findings" headers do
  #      not appear in unbroken ≥3 consecutive concatenation).
  #   2. Cross-pass convergence preserved as annotation (entries that came
  #      from multiple sources include "(confirmed by ...)" or
  #      "(Pass X, Pass Y, ...)" or equivalent annotation).
  #   3. Severity collation present (when conflicting severities exist,
  #      consolidated entry shows resolution — keyword "collated" or
  #      "highest severity" or "downgrade"/"upgrade").
  #   4. Reduction ratio (if raw ledger provided): consolidated entry count
  #      ≤ 70% of raw entry count.
  #   5. Override marker support: <!-- override: ledger-consolidation-... -->
  #      downgrades a per-check failure to WARN.
  #
  # Self-test: pass --self-test as the only argument to run built-in cases.
  # ----------------------------------------------------------------------
  ledger-consolidation)
    if [ $# -lt 1 ]; then echo "Usage: $0 ledger-consolidation <consolidated_ledger_file> [<raw_ledger_file>] | --self-test"; exit 2; fi

    if [ "$1" = "--self-test" ]; then
      TMPDIR=$(mktemp -d)
      trap 'rm -rf "$TMPDIR"' EXIT
      # Positive: consolidated by mechanism, convergence annotated, severity collated.
      cat > "$TMPDIR/pos.md" <<'EOF'
# Findings Ledger (Consolidated)

## Mechanism: Aftermath Compression
Severity: Should-Fix (collated; Pass 5 had Must-Fix, downgraded after
adversarial self-check).
(Confirmed by Pass 1, Pass 5, Reception Risk audit.)

## Mechanism: Status Opacity
Severity: Should-Fix.
(Confirmed by Pass 2, Pass 8.)
EOF
      # Negative 1: raw concatenation — three Pass N Findings headers in a row.
      cat > "$TMPDIR/neg1.md" <<'EOF'
# Findings Ledger

## Pass 1 Findings
- finding A
- finding B

## Pass 2 Findings
- finding C
- finding D

## Pass 5 Findings
- finding E
- finding F
EOF
      # Negative 2: no convergence annotation, no severity collation.
      cat > "$TMPDIR/neg2.md" <<'EOF'
# Findings Ledger (Consolidated)

## Mechanism: Aftermath
Severity: Should-Fix.

## Mechanism: Status
Severity: Should-Fix.
EOF
      # Override: raw concatenation but body marker present → WARN.
      cat > "$TMPDIR/over1.md" <<'EOF'
# Findings Ledger

<!-- override: ledger-consolidation-raw-aggregate — Single-pass run; consolidation deferred per Appendix B rationale. -->

## Pass 1 Findings
- finding A

## Pass 2 Findings
- finding C

## Pass 5 Findings
- finding E
EOF
      RESULTS=0
      "$0" ledger-consolidation "$TMPDIR/pos.md" >/dev/null 2>&1 && echo "  pos: OK" || { echo "  pos: FAIL (expected OK)"; RESULTS=1; }
      "$0" ledger-consolidation "$TMPDIR/neg1.md" >/dev/null 2>&1 && { echo "  neg1: FAIL (expected ERROR — raw concatenation)"; RESULTS=1; } || echo "  neg1: OK (raw-concatenation caught)"
      "$0" ledger-consolidation "$TMPDIR/neg2.md" >/dev/null 2>&1 && { echo "  neg2: FAIL (expected ERROR — no convergence)"; RESULTS=1; } || echo "  neg2: OK (no-convergence caught)"
      "$0" ledger-consolidation "$TMPDIR/over1.md" >/dev/null 2>&1 && echo "  over1: OK (marker downgraded ERROR→WARN)" || { echo "  over1: FAIL (expected OK after override)"; RESULTS=1; }
      [ "$RESULTS" -eq 0 ] && { echo "Self-test: PASS"; exit 0; } || { echo "Self-test: FAIL"; exit 1; }
    fi

    if [ ! -f "$1" ]; then echo "Error: File not found: $1" >&2; exit 2; fi
    LEDGER="$1"
    RAW_LEDGER="${2:-}"
    ERRORS=0

    # Per-check marker detection (markers may appear anywhere in
    # consolidated ledger; ledger does not have appendix-body distinction).
    OV_RAW=0; OV_CONV=0; OV_COLLATE=0; OV_REDUCTION=0
    grep -F "<!-- override: ledger-consolidation-raw-aggregate" "$LEDGER" > /dev/null 2>&1 && OV_RAW=1
    grep -F "<!-- override: ledger-consolidation-no-convergence" "$LEDGER" > /dev/null 2>&1 && OV_CONV=1
    grep -F "<!-- override: ledger-consolidation-no-collation" "$LEDGER" > /dev/null 2>&1 && OV_COLLATE=1
    grep -F "<!-- override: ledger-consolidation-no-reduction" "$LEDGER" > /dev/null 2>&1 && OV_REDUCTION=1

    # Check 1: raw concatenation. Count "Pass N Findings"-style headers; if
    # ≥3 appear consecutively without intervening synthesis text (>10 lines
    # between them), flag.
    RAW_COUNT=$( { grep -cE "^##+ Pass [0-9]+ Findings" "$LEDGER" 2>/dev/null || true; } | head -1 | tr -d ' \n')
    RAW_COUNT=${RAW_COUNT:-0}
    if [ "$RAW_COUNT" -ge 3 ]; then
      if [ "$OV_RAW" -eq 1 ]; then
        echo "WARN: Check 1 (raw-aggregate) — ${RAW_COUNT} 'Pass N Findings' headers detected (override marker present)."
      else
        echo "ERROR: Check 1 (raw-aggregate) — ${RAW_COUNT} 'Pass N Findings' headers detected; raw concatenation pattern (no override marker)."
        ERRORS=$((ERRORS + 1))
      fi
    fi

    # Check 2: convergence annotation. If consolidated entries exist (any
    # "## Mechanism" or "## Finding" or similar), require at least one
    # "(confirmed by..." / "(Pass X, Pass Y..." / "(also flagged by..."
    # annotation.
    CONSOL_HEADERS=$( { grep -cE "^##+ (Mechanism|Finding|Cluster|Concern):" "$LEDGER" 2>/dev/null || true; } | head -1 | tr -d ' \n')
    CONSOL_HEADERS=${CONSOL_HEADERS:-0}
    if [ "$CONSOL_HEADERS" -gt 0 ]; then
      if ! grep -iE "(confirmed by|also flagged|cross[- ]pass|Pass [0-9].*Pass [0-9]|appears in [0-9]+ pass)" "$LEDGER" > /dev/null 2>&1; then
        if [ "$OV_CONV" -eq 1 ]; then
          echo "WARN: Check 2 (convergence) — consolidated entries present but no convergence annotation found (override marker present)."
        else
          echo "ERROR: Check 2 (convergence) — consolidated entries present but no convergence annotation found (no override marker). Add '(confirmed by Pass N, ...)' to multi-source entries."
          ERRORS=$((ERRORS + 1))
        fi
      fi
    fi

    # Check 3: severity collation. If multiple severity tiers appear in the
    # ledger AND consolidated entries exist, require collation language
    # (keyword: "collated", "downgrade", "upgrade", "highest severity wins",
    # "resolved").
    SEV_TIERS=0
    grep -iE "Must-Fix" "$LEDGER" > /dev/null 2>&1 && SEV_TIERS=$((SEV_TIERS + 1))
    grep -iE "Should-Fix" "$LEDGER" > /dev/null 2>&1 && SEV_TIERS=$((SEV_TIERS + 1))
    grep -iE "Could-Fix" "$LEDGER" > /dev/null 2>&1 && SEV_TIERS=$((SEV_TIERS + 1))
    if [ "$SEV_TIERS" -ge 2 ] && [ "$CONSOL_HEADERS" -gt 0 ]; then
      if ! grep -iE "(collated|highest severity|downgrad|upgrad|resolved)" "$LEDGER" > /dev/null 2>&1; then
        if [ "$OV_COLLATE" -eq 1 ]; then
          echo "WARN: Check 3 (severity-collation) — multiple severity tiers present without collation annotation (override marker present)."
        else
          echo "ERROR: Check 3 (severity-collation) — multiple severity tiers present in consolidated entries but no collation annotation (collated/downgrade/upgrade/resolved). No override marker."
          ERRORS=$((ERRORS + 1))
        fi
      fi
    fi

    # Check 4: reduction ratio (only if raw ledger provided). Heuristic:
    # count "- " bullet items in each; consolidated should be ≤ 70% of raw.
    if [ -n "$RAW_LEDGER" ] && [ -f "$RAW_LEDGER" ]; then
      RAW_ITEMS=$( { grep -cE "^- " "$RAW_LEDGER" 2>/dev/null || true; } | head -1 | tr -d ' \n')
      RAW_ITEMS=${RAW_ITEMS:-0}
      CONS_ITEMS=$( { grep -cE "^- " "$LEDGER" 2>/dev/null || true; } | head -1 | tr -d ' \n')
      CONS_ITEMS=${CONS_ITEMS:-0}
      if [ "$RAW_ITEMS" -gt 0 ]; then
        # Consolidated should be at most 70% of raw (i.e., ≥30% reduction).
        THRESHOLD=$((RAW_ITEMS * 70 / 100))
        if [ "$CONS_ITEMS" -gt "$THRESHOLD" ]; then
          if [ "$OV_REDUCTION" -eq 1 ]; then
            echo "WARN: Check 4 (reduction) — consolidated items (${CONS_ITEMS}) exceed 70% of raw items (${RAW_ITEMS}; threshold ${THRESHOLD}); insufficient reduction (override marker present)."
          else
            echo "ERROR: Check 4 (reduction) — consolidated items (${CONS_ITEMS}) exceed 70% of raw items (${RAW_ITEMS}; threshold ${THRESHOLD}); insufficient reduction. No override marker."
            ERRORS=$((ERRORS + 1))
          fi
        fi
      fi
    fi

    if [ "$ERRORS" -gt 0 ]; then
      echo ""
      echo "FAILED: ${ERRORS} ledger-consolidation contract failure(s). Canonical contract: core-editor/references/run-synthesis.md §Step 2 — Findings Ledger Consolidation Contract."
      exit 1
    else
      echo "OK: Findings Ledger consolidation contract satisfied (or override markers present)."
      exit 0
    fi
    ;;

  # ----------------------------------------------------------------------
  # decision-layer-check — canonical homes:
  #   core-editor/references/run-synthesis.md §Step 7 (Decision-Layer
  #     Consolidation) — count contract.
  #   core-editor/references/output-policy.md §Mandatory Appendices —
  #     A/B/C presence contract.
  #   core-editor/references/output-policy.md §Evidence Density
  #     Self-Check — ≥2 references per Must-Fix.
  #
  # Verifies five mechanical checks:
  #   1. Protected Elements — 3-6 entries (count list items / paragraphs
  #      under the "Protected Elements" heading; argument-DE variant
  #      "Strengths / Protected Elements" or "Coalition-Partner
  #      Ground-Truth Recommendations" also accepted — see C3 below).
  #   2. Author Decisions — 3-7 entries (count Keep/Cut/Unsure subhead
  #      clusters when subheads present, or list items under the heading
  #      otherwise; see C1 below).
  #   3. Control Questions — exactly 7 entries (skipped for argument-DE
  #      class; see C3 below).
  #   4. Mandatory Appendices A, B, C — each present as a heading with a
  #      non-empty body (skipped for argument-DE class; see C3).
  #   5. Must-Fix evidence density — every Must-Fix entry has ≥2
  #      references in a paragraph-block window scanning until next
  #      Must-Fix or section header (see C4 below).
  #
  # Phase 7 Wave 1 calibration (C1-C4 from Phase 4 Wave 3 eval coverage):
  #   C1 — When the Author Decisions section has Keep/Cut/Unsure subheads,
  #        count subhead clusters (3) rather than the sub-bullets within
  #        them. The contract intent is "3-7 distinct decision categories"
  #        and Keep/Cut/Unsure naturally produces 2-3 categories with
  #        sub-bullets as evidence. Subhead-cluster mode is detected when
  #        any of `### Keep`, `### Cut`, `### Unsure` headings appears
  #        within the Author Decisions section.
  #   C2 — When neither list items nor bolded paragraphs are detected,
  #        fall back to paragraph-form detection: count blank-line-
  #        separated paragraphs whose first sentence begins with one of
  #        the canonical decision verbs (Protect, Keep, Cut, Defer,
  #        Decide, Unsure) or contains an opening bolded keyword
  #        (`**Decision:**`, `**Question:**`). Risk-controlled fallback —
  #        only fires when the first two heuristics return zero.
  #   C3 — Detect argument-DE letter class via marker presence:
  #        "Coalition-Partner Ground-Truth Recommendations",
  #        "Editorial-Dispute Territory", "Argument_State", "Claim
  #        Ladder", or "Argument Engine". When detected, swap to argument-
  #        DE schema: skip Check 3 (Control Questions) and Check 4
  #        (Appendices A/B/C); for Check 1, accept argument-DE variant
  #        names ("Strengths / Protected Elements", "Coalition-Partner
  #        Ground-Truth Recommendations") in addition to the canonical
  #        "Protected Elements".
  #   C4 — Evidence-density window widened from a fixed 6-line span to
  #        a paragraph-block window: scan from the Must-Fix line until
  #        the next Must-Fix occurrence OR the next section header
  #        (^## or ^### at column 0), whichever comes first. Trade-off:
  #        wider window reduces false-positive density flags but makes
  #        the validator slightly less strict on truly under-evidenced
  #        Must-Fixes — the surrounding paragraph must still contain
  #        2+ references, just within the section block rather than the
  #        immediate 6-line trail.
  #
  # Override markers (per Wave 2 pattern; body-only honored, appendix-only
  # ignored): one per check ID.
  #   <!-- override: decision-layer-protected-elements — <rationale> -->
  #   <!-- override: decision-layer-author-decisions — <rationale> -->
  #   <!-- override: decision-layer-control-questions — <rationale> -->
  #   <!-- override: decision-layer-appendices — <rationale> -->
  #   <!-- override: decision-layer-evidence-density — <rationale> -->
  #
  # Self-test: pass --self-test as the only argument to run built-in cases.
  # ----------------------------------------------------------------------
  decision-layer-check)
    if [ $# -lt 1 ]; then echo "Usage: $0 decision-layer-check <editorial_letter_file> | --self-test"; exit 2; fi

    if [ "$1" = "--self-test" ]; then
      TMPDIR=$(mktemp -d)
      trap 'rm -rf "$TMPDIR"' EXIT
      # Positive: 4 Protected Elements, 4 Author Decisions, 7 Control Questions,
      # all three appendices, Must-Fix with 2+ refs.
      cat > "$TMPDIR/pos.md" <<'EOF'
# Development Edit
## What Needs Work
Must-Fix: pacing collapse in Chapter 7, lines 142-160; also Chapter 9, line 220.
## Protected Elements
- Voice consistency in Part I.
- Scene 4 pivot from Chapter 3.
- Sister relationship arc.
- Final image of Chapter 12.
## Author Decisions
### Keep
- Keep the dual POV.
- Keep the unreliable narrator frame.
### Cut
- Cut the prologue.
### Unsure
- Unsure whether Chapter 5 stays.
## Control Questions
1. What does the protagonist learn in the final third?
2. Whose POV closes Part II?
3. Does the prologue earn its place?
4. What is the cost of Chapter 7's choice?
5. Is Chapter 5 working?
6. Does the final image land?
7. What is the book's controlling idea?
## Appendix A — Diagnostic Detail
Pointers to pass artifacts.
## Appendix B — Severity Calibration
Tested upward and downward.
## Appendix C — Framework Notes
Run metadata.
EOF
      # Negative 1: only 5 Control Questions.
      cat > "$TMPDIR/neg1.md" <<'EOF'
# Development Edit
## Protected Elements
- One.
- Two.
- Three.
## Author Decisions
### Keep
- A.
- B.
- C.
## Control Questions
1. Q one.
2. Q two.
3. Q three.
4. Q four.
5. Q five.
## Appendix A
detail
## Appendix B
calibration
## Appendix C
notes
EOF
      # Negative 2: missing Appendix B.
      cat > "$TMPDIR/neg2.md" <<'EOF'
# Development Edit
## Protected Elements
- One.
- Two.
- Three.
## Author Decisions
### Keep
- A.
- B.
- C.
## Control Questions
1. Q1
2. Q2
3. Q3
4. Q4
5. Q5
6. Q6
7. Q7
## Appendix A
detail
## Appendix C
notes
EOF
      # Negative 3: 8 Author Decisions in non-subheaded list form.
      # Phase 7 calibration: when no Keep/Cut/Unsure subheads are
      # present, the validator falls back to list-item count, and 8
      # items still exceed the 3-7 range. (Subhead-cluster mode would
      # mask this case if the test used subheads — see C1 fixture
      # which deliberately uses 3 subheads with sub-bullets.)
      cat > "$TMPDIR/neg3.md" <<'EOF'
# Development Edit
## Protected Elements
- One.
- Two.
- Three.
## Author Decisions
- D1
- D2
- D3
- D4
- D5
- D6
- D7
- D8
## Control Questions
1. Q1
2. Q2
3. Q3
4. Q4
5. Q5
6. Q6
7. Q7
## Appendix A
detail
## Appendix B
calibration
## Appendix C
notes
EOF
      # Negative 4: Must-Fix with only 1 reference.
      cat > "$TMPDIR/neg4.md" <<'EOF'
# Development Edit
## What Needs Work
Must-Fix: voice problem in Chapter 3 only.
## Protected Elements
- One.
- Two.
- Three.
## Author Decisions
### Keep
- A.
- B.
- C.
## Control Questions
1. Q1
2. Q2
3. Q3
4. Q4
5. Q5
6. Q6
7. Q7
## Appendix A
detail
## Appendix B
calibration
## Appendix C
notes
EOF
      # Override: only 5 Control Questions but body marker present → WARN.
      # Author Decisions uses 4 list items (no subheads) so subhead-cluster
      # mode does not mask it; falls into list-item count = 4 (in range).
      cat > "$TMPDIR/over1.md" <<'EOF'
# Development Edit
## Protected Elements
- One.
- Two.
- Three.
## Author Decisions
- Keep the dual POV.
- Cut the prologue.
- Unsure on Chapter 5.
- Decide pacing of Part II.
<!-- override: decision-layer-control-questions — Short-fiction tier; 5 questions documented in Appendix B. -->
## Control Questions
1. Q one.
2. Q two.
3. Q three.
4. Q four.
5. Q five.
## Appendix A
detail
## Appendix B
calibration
## Appendix C
notes
EOF
      # Override-in-appendix only: marker outside body → still ERROR.
      cat > "$TMPDIR/over_appx.md" <<'EOF'
# Development Edit
## Protected Elements
- One.
- Two.
- Three.
## Author Decisions
- Keep the dual POV.
- Cut the prologue.
- Unsure on Chapter 5.
- Decide pacing of Part II.
## Control Questions
1. Q one.
2. Q two.
3. Q three.
4. Q four.
5. Q five.
## Appendix A
detail
## Appendix B
<!-- override: decision-layer-control-questions — Marker placed in appendix only. -->
calibration
## Appendix C
notes
EOF
      # C1 case: Author Decisions with Keep/Cut/Unsure subheads + many
      # sub-bullets. Phase 4-6 validator counted 13 sub-bullets and FAILed
      # on the 3-7 range; Phase 7 calibration counts 3 subhead clusters
      # and PASSes. Mirrors the canonical Regrets Only Opus / Dinner Party
      # fixture pattern.
      cat > "$TMPDIR/c1_subhead_clusters.md" <<'EOF'
# Development Edit
## What Needs Work
Must-Fix: pacing collapse in Chapter 7, lines 142-160; also Chapter 9, line 220.
## Protected Elements
- Voice consistency in Part I.
- Scene 4 pivot from Chapter 3.
- Sister relationship arc.
- Final image of Chapter 12.
## Author Decisions
### Keep
- Keep the dual POV throughout Part II.
- Keep the unreliable narrator frame.
- Keep the prologue's epistolary form.
- Keep the time-jump between Parts I and II.
- Keep the sibling reconciliation thread.
- Keep the ambiguous final image.
### Cut
- Cut the secondary romance subplot.
- Cut the dream sequence in Chapter 4.
- Cut the third epigraph.
- Cut the metafictional aside in Chapter 9.
### Unsure
- Unsure whether Chapter 5 stays in Part I or moves to Part II.
- Unsure whether the antagonist's POV chapter survives.
- Unsure whether the dedication should be removed.
## Control Questions
1. What does the protagonist learn in the final third?
2. Whose POV closes Part II?
3. Does the prologue earn its place?
4. What is the cost of Chapter 7's choice?
5. Is Chapter 5 working in its current position?
6. Does the final image land?
7. What is the book's controlling idea?
## Appendix A — Diagnostic Detail
Pointers to pass artifacts.
## Appendix B — Severity Calibration
Tested upward and downward.
## Appendix C — Framework Notes
Run metadata.
EOF
      # C2 case: Codex-style paragraph form (no bullets, no bold) for
      # Protected Elements and Author Decisions. Phase 4-6 validator
      # counted 0 and FAILed; Phase 7 calibration's paragraph-form
      # fallback detects verb-leading paragraphs.
      cat > "$TMPDIR/c2_paragraph_form.md" <<'EOF'
# Development Edit
## What Needs Work
Must-Fix: voice drift in Chapter 3 (lines 80-95) and Chapter 7 (lines 200-215).
## Protected Elements
Protect the dual-narrator structure across Parts I and II. The shifting POV is the book's load-bearing architecture and revision should not flatten it.

Protect the slow opening in Chapter 1. Its pacing rewards the patient reader and survives multiple test passes without losing tension.

Protect the sibling reconciliation in Chapter 11. This is the emotional spine of the closing third and any cut here will undo the climax.

Protect the metafictional epigraph. It cues the unreliable-narrator frame readers need.

## Author Decisions
Keep the prologue. The distance frame it establishes is doing work the body cannot do without it.

Cut the third dream sequence. It duplicates the second and dilutes thematic charge.

Decide whether Chapter 5 stays in Part I. The decision determines whether Part I lands on the sister scene or the road scene; both are defensible but only one survives.

Unsure on the chapter break between 7 and 8. Either an explicit break or a soft fade works structurally; this is a craft decision the author owns.

## Control Questions
1. What does the protagonist learn in the final third?
2. Whose POV closes Part II?
3. Does the prologue earn its place?
4. What is the cost of Chapter 7's choice?
5. Is Chapter 5 working in its current position?
6. Does the final image land?
7. What is the book's controlling idea?
## Appendix A — Diagnostic Detail
Pointers to pass artifacts. Chapter 3 lines 80-95 cited; Chapter 7 lines 200-215 cited; Scene 4 cross-reference noted.
## Appendix B — Severity Calibration
Tested upward and downward.
## Appendix C — Framework Notes
Run metadata.
EOF
      # C3 case: argument-DE letter using Coalition-Partner Ground-Truth
      # Recommendations + Editorial-Dispute Territory headings, no
      # canonical Control Questions, no Appendix A/B/C. Phase 4-6
      # validator FAILed Check 4 (missing appendices) and WARNed Check 3
      # (missing Control Questions); Phase 7 calibration detects the
      # argument-DE class and skips Checks 3-4.
      cat > "$TMPDIR/c3_argument_de.md" <<'EOF'
# Editorial Letter — Argument-Shaped Run
## What Needs Work
Must-Fix: warrant gap on §3 claim (page 14, lines 320-340); Must-Fix: missing counterevidence on §5 (page 22, lines 580-600).
## Coalition-Partner Ground-Truth Recommendations
- Center the lived-experience testimony in §2 before introducing the statistical frame in §3.
- Cite the 2024 longitudinal study (page 8) before pivoting to policy implications in §4.
- Replace the abstract case in §6 with the named program example partners flagged.
- Re-sequence §7 conclusions to lead with coalition-partner recommendations rather than authorial conclusions.
## Editorial-Dispute Territory
Decide whether the methodology critique in §4 stays at its current scope. Reviewers split on this — three readers wanted it expanded to address replication failures; two wanted it cut as scope creep.

Cut the second example in §6 if the methodology critique stays at current scope; keep it if the methodology critique expands.

Defer the call-to-action framing decision until after Field Reconnaissance returns. The literature-counterevidence may shift the policy frame.

Decide whether the regulatory recommendations in §8 belong in the body or in an annex. Argument_State analysis suggests body placement strengthens the claim ladder.

Decide on the executive summary's length cap (current 1 page; partner asked for 2).
## Stress Test
Hostile-reader attack 1: scope creep in §4.
Hostile-reader attack 2: cherry-picked sample in §3 (lines 320-340 vulnerable).
EOF
      # C4 case: Must-Fix with paragraph-form evidence (references in
      # the surrounding paragraph block, not in the immediate 6-line
      # window). Phase 4-6 validator FAILed; Phase 7 paragraph-window
      # passes.
      cat > "$TMPDIR/c4_paragraph_evidence.md" <<'EOF'
# Development Edit
## What Needs Work

Must-Fix: pacing collapse in the middle third.

The Compression audit flagged this at Pattern severity — see Chapter 7 (lines 142-160) where the text summarizes three days in two sentences while the surrounding scenes operate at scene-level granularity. The same compression appears in Chapter 9 around line 220, and the Compression audit's §7 hard gate fires on the cumulative pattern. Page 88 contains the load-bearing scene that should anchor the middle third's pacing recovery; instead it's compressed into a paragraph.

Must-Fix: voice drift in Chapter 3.

Scene 4 (line 95) shows the first drift; the AI-Prose Calibration audit flagged AIC-2 voice flattening at Pattern severity. The drift recurs at Chapter 5 line 180 and Chapter 7 lines 200-215, producing a manuscript-wide pattern the audit elevated from Spot to Pattern.

## Protected Elements
- Voice consistency in Part I.
- Scene 4 pivot from Chapter 3.
- Sister relationship arc.
- Final image of Chapter 12.
## Author Decisions
### Keep
- Keep the dual POV.
### Cut
- Cut the prologue.
### Unsure
- Unsure whether Chapter 5 stays.
## Control Questions
1. Q1
2. Q2
3. Q3
4. Q4
5. Q5
6. Q6
7. Q7
## Appendix A
detail
## Appendix B
calibration
## Appendix C
notes
EOF
      RESULTS=0
      "$0" decision-layer-check "$TMPDIR/pos.md" >/dev/null 2>&1 && echo "  pos: OK" || { echo "  pos: FAIL (expected OK)"; RESULTS=1; }
      "$0" decision-layer-check "$TMPDIR/neg1.md" >/dev/null 2>&1 && { echo "  neg1: FAIL (expected ERROR — 5 Control Questions)"; RESULTS=1; } || echo "  neg1: OK (caught)"
      "$0" decision-layer-check "$TMPDIR/neg2.md" >/dev/null 2>&1 && { echo "  neg2: FAIL (expected ERROR — missing Appendix B)"; RESULTS=1; } || echo "  neg2: OK (caught)"
      "$0" decision-layer-check "$TMPDIR/neg3.md" >/dev/null 2>&1 && { echo "  neg3: FAIL (expected ERROR — 8 Author Decisions)"; RESULTS=1; } || echo "  neg3: OK (caught)"
      "$0" decision-layer-check "$TMPDIR/neg4.md" >/dev/null 2>&1 && { echo "  neg4: FAIL (expected ERROR — Must-Fix with <2 refs)"; RESULTS=1; } || echo "  neg4: OK (caught)"
      "$0" decision-layer-check "$TMPDIR/over1.md" >/dev/null 2>&1 && echo "  over1: OK (marker in body downgraded ERROR→WARN)" || { echo "  over1: FAIL (expected OK after override)"; RESULTS=1; }
      "$0" decision-layer-check "$TMPDIR/over_appx.md" >/dev/null 2>&1 && { echo "  over_appx: FAIL (appendix-only marker should not downgrade)"; RESULTS=1; } || echo "  over_appx: OK (caught — marker in appendix is non-canonical)"
      "$0" decision-layer-check "$TMPDIR/c1_subhead_clusters.md" >/dev/null 2>&1 && echo "  c1_subhead_clusters: OK (3 Keep/Cut/Unsure subhead clusters counted, not 13 sub-bullets)" || { echo "  c1_subhead_clusters: FAIL (Phase 7 C1 calibration regression — subhead-cluster counting expected)"; RESULTS=1; }
      "$0" decision-layer-check "$TMPDIR/c2_paragraph_form.md" >/dev/null 2>&1 && echo "  c2_paragraph_form: OK (paragraph-form decision verbs counted via fallback)" || { echo "  c2_paragraph_form: FAIL (Phase 7 C2 calibration regression — paragraph-form fallback expected)"; RESULTS=1; }
      "$0" decision-layer-check "$TMPDIR/c3_argument_de.md" >/dev/null 2>&1 && echo "  c3_argument_de: OK (argument-DE class detected; Checks 3-4 skipped)" || { echo "  c3_argument_de: FAIL (Phase 7 C3 calibration regression — argument-DE schema expected)"; RESULTS=1; }
      "$0" decision-layer-check "$TMPDIR/c4_paragraph_evidence.md" >/dev/null 2>&1 && echo "  c4_paragraph_evidence: OK (paragraph-block window finds inline-prose evidence)" || { echo "  c4_paragraph_evidence: FAIL (Phase 7 C4 calibration regression — paragraph-block window expected)"; RESULTS=1; }
      [ "$RESULTS" -eq 0 ] && { echo "Self-test: PASS"; exit 0; } || { echo "Self-test: FAIL"; exit 1; }
    fi

    if [ ! -f "$1" ]; then echo "Error: File not found: $1" >&2; exit 2; fi
    LETTER="$1"
    ERRORS=0

    # Split letter into body (above first Appendix heading) and appendix.
    # Markers in appendix bodies are ignored.
    APPENDIX_LINE=$(grep -niE "^#{1,4}.*Appendix [A-C]" "$LETTER" 2>/dev/null | head -1 | cut -d: -f1 || true)
    if [ -n "$APPENDIX_LINE" ]; then
      BODY=$(sed -n "1,$((APPENDIX_LINE - 1))p" "$LETTER")
    else
      BODY=$(cat "$LETTER")
    fi

    # Per-check marker detection — body only.
    OV_PE=0; OV_AD=0; OV_CQ=0; OV_APP=0; OV_ED=0
    echo "$BODY" | grep -F "<!-- override: decision-layer-protected-elements" > /dev/null 2>&1 && OV_PE=1
    echo "$BODY" | grep -F "<!-- override: decision-layer-author-decisions" > /dev/null 2>&1 && OV_AD=1
    echo "$BODY" | grep -F "<!-- override: decision-layer-control-questions" > /dev/null 2>&1 && OV_CQ=1
    echo "$BODY" | grep -F "<!-- override: decision-layer-appendices" > /dev/null 2>&1 && OV_APP=1
    echo "$BODY" | grep -F "<!-- override: decision-layer-evidence-density" > /dev/null 2>&1 && OV_ED=1

    # ----- C3: argument-DE class detection -----
    # Detect argument-DE letter class via marker presence anywhere in
    # the letter. When detected, swap to argument-DE schema:
    #   - Check 1 accepts "Coalition-Partner Ground-Truth Recommendations"
    #     and "Strengths / Protected Elements" as Protected Elements
    #     equivalents; Author Decisions accepts "Editorial-Dispute
    #     Territory" as the equivalent decision section.
    #   - Check 3 (Control Questions) is skipped (argument-DE class does
    #     not require canonical 7 Control Questions).
    #   - Check 4 (Appendices A/B/C) is skipped (argument-DE class does
    #     not require canonical Appendix A/B/C).
    ARGUMENT_DE=0
    if grep -iE "(Coalition-Partner Ground-Truth|Editorial-Dispute Territory|Argument_State|Claim Ladder|Argument Engine)" "$LETTER" > /dev/null 2>&1; then
      ARGUMENT_DE=1
    fi

    # Helper: extract section text between a heading (matching one of
    # several alternative patterns) and the next level-2 heading.
    # Returns the section body text on stdout; empty string + return 1
    # if no matching heading found.
    extract_section() {
      local file="$1"
      shift
      local start_line=""
      for pat in "$@"; do
        start_line=$(grep -niE "^#{1,4}[[:space:]]+.*${pat}" "$file" 2>/dev/null | head -1 | cut -d: -f1 || true)
        [ -n "$start_line" ] && break
      done
      if [ -z "$start_line" ]; then return 1; fi
      local next_line
      next_line=$(awk -v s="$start_line" 'NR > s && /^##[^#]/ {print NR; exit}' "$file" 2>/dev/null)
      if [ -z "$next_line" ]; then
        next_line=$(wc -l < "$file" | tr -d ' ')
      fi
      sed -n "$((start_line + 1)),${next_line}p" "$file"
      return 0
    }

    # Helper: count decision-layer entries within a section using a
    # three-tier heuristic with C1 (subhead-cluster) and C2 (paragraph-
    # form) extensions. Returns count on stdout; -1 if section absent.
    #
    # Args: $1 = file path; $2... = alternative heading patterns.
    #
    # Heuristic order:
    #   (a) C1 — if section contains Keep/Cut/Unsure (case-insensitive)
    #       level-3 subheads, count the subhead clusters (typical 1-3).
    #       This implements the "3-7 distinct decision categories"
    #       contract intent for fixtures with many sub-bullets per
    #       subhead.
    #   (b) Default — count list items ("- ", "* ", "<n>. ").
    #   (c) Bolded-paragraph fallback — when (a) and (b) return zero,
    #       count "^**...**" paragraph leaders.
    #   (d) C2 — when (a), (b), (c) return zero, count blank-line-
    #       separated paragraphs whose first sentence begins with a
    #       canonical decision verb (Protect, Keep, Cut, Defer, Decide,
    #       Unsure) or contains an opening bolded keyword
    #       (**Decision:**, **Question:**, **Element:**).
    count_decision_entries() {
      local file="$1"
      shift
      local section
      if ! section=$(extract_section "$file" "$@"); then
        echo "-1"
        return
      fi

      # (a) C1: subhead-cluster count.
      # Count distinct level-3 subheads matching Keep/Cut/Unsure (case-
      # insensitive). Each subhead is one cluster regardless of how many
      # sub-bullets it contains.
      local subhead_count
      subhead_count=$( { echo "$section" | grep -cE "^###[[:space:]]+(Keep|Cut|Unsure|Defer|Decide)[[:space:]:]*" 2>/dev/null || true; } | head -1 | tr -d ' \n')
      subhead_count=${subhead_count:-0}
      if [ "$subhead_count" -ge 1 ]; then
        echo "$subhead_count"
        return
      fi

      # (b) Default: list-item count.
      local list_items
      list_items=$( { echo "$section" | grep -cE "^([-*]|[0-9]+\.) " 2>/dev/null || true; } | head -1 | tr -d ' \n')
      list_items=${list_items:-0}
      if [ "$list_items" -gt 0 ]; then
        echo "$list_items"
        return
      fi

      # (c) Bolded-paragraph fallback.
      local bold_paras
      bold_paras=$( { echo "$section" | grep -cE "^\*\*[^*]" 2>/dev/null || true; } | head -1 | tr -d ' \n')
      bold_paras=${bold_paras:-0}
      if [ "$bold_paras" -gt 0 ]; then
        echo "$bold_paras"
        return
      fi

      # (d) C2: paragraph-form fallback.
      # Count blank-line-separated paragraphs whose first non-blank line
      # starts with a canonical decision verb. Implementation: walk
      # lines, increment count when a non-blank line starts a new
      # paragraph (previous line was blank OR is the first line) AND
      # matches the verb pattern.
      local para_count
      para_count=$(echo "$section" | awk '
        BEGIN { count = 0; prev_blank = 1 }
        {
          if (NF == 0) { prev_blank = 1; next }
          if (prev_blank == 1) {
            if (match($0, /^[[:space:]]*(Protect|Keep|Cut|Defer|Decide|Unsure)[[:space:]:.,]/) ||
                match($0, /^[[:space:]]*\*\*(Decision|Question|Element|Protect|Keep|Cut|Defer|Decide|Unsure)/)) {
              count++
            }
          }
          prev_blank = 0
        }
        END { print count }
      ')
      para_count=${para_count:-0}
      echo "$para_count"
    }

    # Check 1: Protected Elements — 3-6 items.
    # Argument-DE accepts variant heading names per C3.
    if [ "$ARGUMENT_DE" -eq 1 ]; then
      PE_COUNT=$(count_decision_entries "$LETTER" "Coalition-Partner Ground-Truth" "Strengths.*Protected Elements" "Protected Elements")
    else
      PE_COUNT=$(count_decision_entries "$LETTER" "Protected Elements")
    fi
    if [ "$PE_COUNT" -ge 0 ]; then
      if [ "$PE_COUNT" -lt 3 ] || [ "$PE_COUNT" -gt 6 ]; then
        if [ "$OV_PE" -eq 1 ]; then
          echo "WARN: Check 1 (protected-elements) — count ${PE_COUNT} outside 3-6 range (override marker present)."
        else
          echo "ERROR: Check 1 (protected-elements) — count ${PE_COUNT} outside 3-6 range (no override marker in body)."
          ERRORS=$((ERRORS + 1))
        fi
      fi
    fi
    if [ "$PE_COUNT" = "-1" ]; then
      echo "WARN: Check 1 (protected-elements) — 'Protected Elements' (or argument-DE variant) heading not found."
    fi

    # Check 2: Author Decisions — 3-7 items.
    # Argument-DE accepts "Editorial-Dispute Territory" as the equivalent.
    if [ "$ARGUMENT_DE" -eq 1 ]; then
      AD_COUNT=$(count_decision_entries "$LETTER" "Editorial-Dispute Territory" "Author Decisions")
    else
      AD_COUNT=$(count_decision_entries "$LETTER" "Author Decisions")
    fi
    if [ "$AD_COUNT" -ge 0 ]; then
      if [ "$AD_COUNT" -lt 3 ] || [ "$AD_COUNT" -gt 7 ]; then
        if [ "$OV_AD" -eq 1 ]; then
          echo "WARN: Check 2 (author-decisions) — count ${AD_COUNT} outside 3-7 range (override marker present)."
        else
          echo "ERROR: Check 2 (author-decisions) — count ${AD_COUNT} outside 3-7 range (no override marker in body)."
          ERRORS=$((ERRORS + 1))
        fi
      fi
    fi
    if [ "$AD_COUNT" = "-1" ]; then
      echo "WARN: Check 2 (author-decisions) — 'Author Decisions' (or argument-DE variant) heading not found."
    fi

    # Check 3: Control Questions — exactly 7. Skipped for argument-DE.
    if [ "$ARGUMENT_DE" -eq 0 ]; then
      CQ_COUNT=$(count_decision_entries "$LETTER" "Control Questions")
      if [ "$CQ_COUNT" -ge 0 ]; then
        if [ "$CQ_COUNT" -ne 7 ]; then
          if [ "$OV_CQ" -eq 1 ]; then
            echo "WARN: Check 3 (control-questions) — count ${CQ_COUNT} (expected exactly 7; override marker present)."
          else
            echo "ERROR: Check 3 (control-questions) — count ${CQ_COUNT} (expected exactly 7; no override marker in body)."
            ERRORS=$((ERRORS + 1))
          fi
        fi
      fi
      if [ "$CQ_COUNT" = "-1" ]; then
        echo "WARN: Check 3 (control-questions) — 'Control Questions' heading not found."
      fi
    fi

    # Check 4: Appendices A, B, C all present as headings. Skipped for
    # argument-DE class (argument-shaped letters use different appendix
    # conventions per the argument-DE schema).
    if [ "$ARGUMENT_DE" -eq 0 ]; then
      MISSING_APPS=""
      for app in "Appendix A" "Appendix B" "Appendix C"; do
        if ! grep -iE "^#{1,4}[[:space:]]+.*${app}" "$LETTER" > /dev/null 2>&1; then
          MISSING_APPS="${MISSING_APPS}${app}, "
        fi
      done
      if [ -n "$MISSING_APPS" ]; then
        if [ "$OV_APP" -eq 1 ]; then
          echo "WARN: Check 4 (appendices) — missing: ${MISSING_APPS%, } (override marker present)."
        else
          echo "ERROR: Check 4 (appendices) — missing: ${MISSING_APPS%, } (no override marker in body)."
          ERRORS=$((ERRORS + 1))
        fi
      fi
    fi

    # Check 5: Must-Fix evidence density (C4 calibration).
    # For each line containing "Must-Fix" (case-insensitive), scan a
    # paragraph-block window from the Must-Fix line until the next
    # Must-Fix occurrence OR the next section header (^## at column 0),
    # whichever comes first. Within that window, count reference
    # patterns. This widens the Phase 4-6 fixed 6-line window so that
    # paragraph-form evidence (references in surrounding prose, not in
    # an immediate trailing list) is detected.
    MF_LINES=$( { grep -niE "Must-Fix" "$LETTER" 2>/dev/null || true; } | cut -d: -f1)
    MF_THIN=0
    if [ -n "$MF_LINES" ]; then
      # Build sorted unique list of Must-Fix line numbers + section
      # boundary line numbers for paragraph-block delimitation.
      ALL_MF=$(echo "$MF_LINES" | sort -n -u)
      # Section boundaries: lines starting with ## (level-2 heading).
      SECTION_LINES=$(grep -nE "^##[^#]" "$LETTER" 2>/dev/null | cut -d: -f1 || true)
      TOTAL_LINES=$(wc -l < "$LETTER" | tr -d ' ')
      while IFS= read -r ln; do
        [ -z "$ln" ] && continue
        # Find the next Must-Fix line strictly greater than ln.
        NEXT_MF=$(echo "$ALL_MF" | awk -v c="$ln" '$1 > c {print; exit}')
        # Find the next section boundary strictly greater than ln.
        NEXT_SEC=$(echo "$SECTION_LINES" | awk -v c="$ln" '$1 > c {print; exit}')
        # End of window = min(NEXT_MF, NEXT_SEC, TOTAL_LINES). If
        # nothing found, use TOTAL_LINES.
        END="$TOTAL_LINES"
        if [ -n "$NEXT_MF" ] && [ "$NEXT_MF" -lt "$END" ]; then END="$NEXT_MF"; fi
        if [ -n "$NEXT_SEC" ] && [ "$NEXT_SEC" -lt "$END" ]; then END="$NEXT_SEC"; fi
        # Subtract 1 to stay before the next boundary (exclusive end).
        if [ "$END" -gt "$ln" ]; then END=$((END - 1)); fi
        BLOCK=$(sed -n "${ln},${END}p" "$LETTER")
        # Count distinct reference patterns within block.
        REF_COUNT=$( { echo "$BLOCK" | grep -oiE "(Chapter\s+[0-9]+|Ch\.\s*[0-9]+|Scene\s+[0-9]+|lines?\s+[0-9]+|L[0-9]+|page\s+[0-9]+|p\.\s*[0-9]+|§\s*[A-Za-z0-9.-]+|[A-Z]{2,5}-[0-9]+)" 2>/dev/null || true; } | wc -l | tr -d ' ')
        REF_COUNT=${REF_COUNT:-0}
        if [ "$REF_COUNT" -lt 2 ]; then
          MF_THIN=$((MF_THIN + 1))
        fi
      done <<< "$MF_LINES"
    fi
    if [ "$MF_THIN" -gt 0 ]; then
      if [ "$OV_ED" -eq 1 ]; then
        echo "WARN: Check 5 (evidence-density) — ${MF_THIN} Must-Fix mention(s) with <2 references in paragraph-block window (override marker present)."
      else
        echo "ERROR: Check 5 (evidence-density) — ${MF_THIN} Must-Fix mention(s) with <2 references in paragraph-block window (no override marker in body)."
        ERRORS=$((ERRORS + 1))
      fi
    fi

    if [ "$ERRORS" -gt 0 ]; then
      echo ""
      if [ "$ARGUMENT_DE" -eq 1 ]; then
        echo "FAILED: ${ERRORS} decision-layer-check failure(s) (argument-DE class — Checks 3-4 skipped). Canonical homes: core-editor/references/run-synthesis.md §Step 7 + core-editor/references/output-policy.md §Mandatory Appendices / §Evidence Density Self-Check."
      else
        echo "FAILED: ${ERRORS} decision-layer-check failure(s). Canonical homes: core-editor/references/run-synthesis.md §Step 7 + core-editor/references/output-policy.md §Mandatory Appendices / §Evidence Density Self-Check."
      fi
      exit 1
    else
      if [ "$ARGUMENT_DE" -eq 1 ]; then
        echo "OK: Decision-Layer Consolidation contract satisfied (argument-DE class — Checks 3-4 skipped per C3 calibration; or override markers present)."
      else
        echo "OK: Decision-Layer Consolidation contract satisfied (or override markers present)."
      fi
      exit 0
    fi
    ;;

  # ----------------------------------------------------------------------
  # quality-risk-triggers — canonical home: run-core.md §Quality-Risk Mode
  # Selection. Detects the five enumerated triggers (Q1-Q5) from contract
  # artifact + optional Diagnostic_State.meta.json. Pre-pass mode-selection
  # check; complements underdiagnosis-triggers (synthesis-time).
  #
  # Triggers:
  #   Q1 Consent/governance — Horror/Erotic genre OR Consent Complexity
  #     audit recommended OR Reception Risk audit recommended OR
  #     darkness level HIGH. Escalation: hybrid (or swarm if final-round).
  #   Q2 Argument-shaped nonfiction high stakes — nonfiction constraint
  #     AND form is policy/testimony/op-ed/white-paper/academic/open-letter
  #     OR Dialectical Clarity audit recommended with submission readiness.
  #     Escalation: hybrid (swarm if Field Recon required).
  #   Q3 Many POVs / non-linear — POV count ≥3 OR non-linear structure
  #     flagged. Escalation: hybrid (≥6 POVs → swarm).
  #   Q4 Prior thin synthesis — Diagnostic_State.meta.json shows
  #     underdiagnosis loop fired in prior runs. Escalation: swarm.
  #   Q5 Submission readiness — goal=submit OR Pass 11 in pass set OR
  #     contract notes "final round before submission." Escalation: swarm.
  #
  # Override marker syntax (in contract body):
  #   <!-- override: quality-risk-Q1 — <rationale> -->
  #   <!-- override: quality-risk-Q2 — <rationale> -->
  #   <!-- override: quality-risk-Q3 — <rationale> -->
  #   <!-- override: quality-risk-Q4 — <rationale> -->
  #   <!-- override: quality-risk-Q5 — <rationale> -->
  #
  # Self-test: pass --self-test as the only argument to run built-in cases.
  # ----------------------------------------------------------------------
  quality-risk-triggers)
    if [ $# -lt 1 ]; then echo "Usage: $0 quality-risk-triggers <contract_file> [<diagnostic_state_meta_file>] | --self-test"; exit 2; fi

    if [ "$1" = "--self-test" ]; then
      TMPDIR=$(mktemp -d)
      trap 'rm -rf "$TMPDIR"' EXIT
      # Positive: clean fiction contract, no triggers fire.
      cat > "$TMPDIR/pos.md" <<'EOF'
# Contract
GENRE/SUBGENRE: Literary fiction
DARKNESS LEVEL: low
POV count: 1
GOAL: repair
RECOMMENDED AUDITS: Scene Turn, Emotional Craft
EOF
      # Negative Q1: Horror genre + Consent Complexity audit recommended.
      cat > "$TMPDIR/neg_q1.md" <<'EOF'
# Contract
GENRE/SUBGENRE: Horror
DARKNESS LEVEL: HIGH
POV count: 2
GOAL: repair
RECOMMENDED AUDITS: Consent Complexity, Reception Risk, Stakes System
EOF
      # Negative Q2: nonfiction policy brief, submission readiness.
      cat > "$TMPDIR/neg_q2.md" <<'EOF'
# Contract
GENRE/SUBGENRE: Nonfiction — policy brief
constraint: nonfiction
FORM: policy brief
GOAL: submit
RECOMMENDED AUDITS: Dialectical Clarity, Argument Red-Team
EOF
      # Negative Q3: 4 POVs.
      cat > "$TMPDIR/neg_q3.md" <<'EOF'
# Contract
GENRE/SUBGENRE: Literary fiction
POV count: 4
GOAL: repair
RECOMMENDED AUDITS: Scene Turn
EOF
      # Negative Q5: submission readiness (goal=submit + Pass 11 in set).
      cat > "$TMPDIR/neg_q5.md" <<'EOF'
# Contract
GENRE/SUBGENRE: Literary fiction
POV count: 1
GOAL: submit
PASS SET: 0, 1, 2, 5, 8, 11
RECOMMENDED AUDITS: Scene Turn, Emotional Craft
EOF
      # Negative Q4: requires sidecar with prior underdiagnosis flag.
      cat > "$TMPDIR/neg_q4_contract.md" <<'EOF'
# Contract
GENRE/SUBGENRE: Literary fiction
POV count: 1
GOAL: repair
RECOMMENDED AUDITS: Scene Turn
EOF
      cat > "$TMPDIR/neg_q4_meta.json" <<'EOF'
{
  "contract_hash": "abc123",
  "underdiagnosis_flag": "fired",
  "prior_runs": [{"label": "round-1", "underdiagnosis_triggers": ["convergence"]}]
}
EOF
      # Override Q1: Horror trigger but body marker present → WARN, exit 0.
      cat > "$TMPDIR/over_q1.md" <<'EOF'
# Contract
GENRE/SUBGENRE: Horror
DARKNESS LEVEL: HIGH
POV count: 2
GOAL: repair
RECOMMENDED AUDITS: Consent Complexity, Reception Risk
<!-- override: quality-risk-Q1 — Author requests baseline mode; this is an exploratory mid-draft pass, not final-round. -->
EOF
      RESULTS=0
      "$0" quality-risk-triggers "$TMPDIR/pos.md" >/dev/null 2>&1 && echo "  pos: OK (no triggers fired)" || { echo "  pos: FAIL (expected OK)"; RESULTS=1; }
      "$0" quality-risk-triggers "$TMPDIR/neg_q1.md" >/dev/null 2>&1 && { echo "  neg_q1: FAIL (expected ERROR — Q1 consent)"; RESULTS=1; } || echo "  neg_q1: OK (Q1 consent trigger caught)"
      "$0" quality-risk-triggers "$TMPDIR/neg_q2.md" >/dev/null 2>&1 && { echo "  neg_q2: FAIL (expected ERROR — Q2 argument-shaped)"; RESULTS=1; } || echo "  neg_q2: OK (Q2 argument-shaped trigger caught)"
      "$0" quality-risk-triggers "$TMPDIR/neg_q3.md" >/dev/null 2>&1 && { echo "  neg_q3: FAIL (expected ERROR — Q3 many POVs)"; RESULTS=1; } || echo "  neg_q3: OK (Q3 many-POVs trigger caught)"
      "$0" quality-risk-triggers "$TMPDIR/neg_q4_contract.md" "$TMPDIR/neg_q4_meta.json" >/dev/null 2>&1 && { echo "  neg_q4: FAIL (expected ERROR — Q4 prior thin)"; RESULTS=1; } || echo "  neg_q4: OK (Q4 prior-thin trigger caught)"
      "$0" quality-risk-triggers "$TMPDIR/neg_q5.md" >/dev/null 2>&1 && { echo "  neg_q5: FAIL (expected ERROR — Q5 submission)"; RESULTS=1; } || echo "  neg_q5: OK (Q5 submission trigger caught)"
      "$0" quality-risk-triggers "$TMPDIR/over_q1.md" >/dev/null 2>&1 && echo "  over_q1: OK (Q1 marker downgraded ERROR→WARN)" || { echo "  over_q1: FAIL (expected OK after override)"; RESULTS=1; }
      [ "$RESULTS" -eq 0 ] && { echo "Self-test: PASS"; exit 0; } || { echo "Self-test: FAIL"; exit 1; }
    fi

    if [ ! -f "$1" ]; then echo "Error: File not found: $1" >&2; exit 2; fi
    CONTRACT="$1"
    META="${2:-}"
    ERRORS=0
    FIRED=""
    ESCALATION="none"

    # Per-trigger override marker detection (contract body).
    OV_Q1=0; OV_Q2=0; OV_Q3=0; OV_Q4=0; OV_Q5=0
    grep -F "<!-- override: quality-risk-Q1" "$CONTRACT" > /dev/null 2>&1 && OV_Q1=1
    grep -F "<!-- override: quality-risk-Q2" "$CONTRACT" > /dev/null 2>&1 && OV_Q2=1
    grep -F "<!-- override: quality-risk-Q3" "$CONTRACT" > /dev/null 2>&1 && OV_Q3=1
    grep -F "<!-- override: quality-risk-Q4" "$CONTRACT" > /dev/null 2>&1 && OV_Q4=1
    grep -F "<!-- override: quality-risk-Q5" "$CONTRACT" > /dev/null 2>&1 && OV_Q5=1

    # raise_escalation <target> — promote ESCALATION to higher tier (ceiling=swarm).
    raise_escalation() {
      local target="$1"
      case "$ESCALATION" in
        none) ESCALATION="$target" ;;
        hybrid) [ "$target" = "swarm" ] && ESCALATION="swarm" ;;
        swarm) ;; # ceiling
      esac
    }

    # Trigger Q1: consent/governance risk.
    Q1_HIT=""
    if grep -iE "^(genre|GENRE/SUBGENRE):.*(Horror|Erotic)" "$CONTRACT" > /dev/null 2>&1; then
      Q1_HIT="genre=Horror/Erotic"
    fi
    if grep -iE "(Consent Complexity|Reception Risk)" "$CONTRACT" > /dev/null 2>&1; then
      [ -n "$Q1_HIT" ] && Q1_HIT="${Q1_HIT}; consent/reception audit recommended" || Q1_HIT="consent/reception audit recommended"
    fi
    if grep -iE "(darkness[ -]level|DARKNESS LEVEL)\s*:?\s*HIGH" "$CONTRACT" > /dev/null 2>&1; then
      [ -n "$Q1_HIT" ] && Q1_HIT="${Q1_HIT}; darkness=HIGH" || Q1_HIT="darkness=HIGH"
    fi
    if grep -iE "power[ -]dynamics.*central" "$CONTRACT" > /dev/null 2>&1; then
      [ -n "$Q1_HIT" ] && Q1_HIT="${Q1_HIT}; power-dynamics-central" || Q1_HIT="power-dynamics-central"
    fi
    if [ -n "$Q1_HIT" ]; then
      if [ "$OV_Q1" -eq 1 ]; then
        echo "WARN: Q1 (consent/governance) — fired: ${Q1_HIT} (override marker present)."
      else
        echo "ERROR: Q1 (consent/governance) — fired: ${Q1_HIT}. Recommended escalation: hybrid. Rationale: structural+reception lenses warrant architectural isolation."
        ERRORS=$((ERRORS + 1))
      fi
      FIRED="${FIRED}Q1 "
      raise_escalation "hybrid"
    fi

    # Trigger Q2: argument-shaped nonfiction with high stakes.
    Q2_HIT=""
    if grep -iE "constraint:\s*nonfiction|^constraint:nonfiction" "$CONTRACT" > /dev/null 2>&1 \
       || grep -iE "^(GENRE/SUBGENRE|GENRE):.*(nonfiction|policy|testimony|op-ed|white paper|white-paper|academic|open letter|open-letter)" "$CONTRACT" > /dev/null 2>&1; then
      if grep -iE "(policy brief|testimony|op-ed|white[- ]paper|academic argument|open letter|recommendation memo)" "$CONTRACT" > /dev/null 2>&1; then
        Q2_HIT="nonfiction + argument-shaped form"
      fi
    fi
    if grep -iE "Dialectical Clarity" "$CONTRACT" > /dev/null 2>&1 \
       && grep -iE "(submission readiness|GOAL:\s*submit|goal:\s*submit)" "$CONTRACT" > /dev/null 2>&1; then
      [ -n "$Q2_HIT" ] && Q2_HIT="${Q2_HIT}; Dialectical Clarity + submission readiness" || Q2_HIT="Dialectical Clarity + submission readiness"
    fi
    if [ -n "$Q2_HIT" ]; then
      if [ "$OV_Q2" -eq 1 ]; then
        echo "WARN: Q2 (argument-shaped + high stakes) — fired: ${Q2_HIT} (override marker present)."
      else
        echo "ERROR: Q2 (argument-shaped + high stakes) — fired: ${Q2_HIT}. Recommended escalation: hybrid (swarm if Field Recon required). Rationale: claim/evidence/audience lenses warrant independent stress-testing."
        ERRORS=$((ERRORS + 1))
      fi
      FIRED="${FIRED}Q2 "
      raise_escalation "hybrid"
    fi

    # Trigger Q3: many POVs or non-linear structure.
    Q3_HIT=""
    POV_COUNT=0
    POV_LINE=$(grep -iE "POV(\s+count)?:\s*[0-9]+" "$CONTRACT" 2>/dev/null | head -1 || true)
    if [ -n "$POV_LINE" ]; then
      POV_COUNT=$(echo "$POV_LINE" | grep -oE "[0-9]+" | head -1)
      POV_COUNT=${POV_COUNT:-0}
    fi
    if [ "$POV_COUNT" -ge 3 ]; then
      Q3_HIT="POV count=${POV_COUNT}"
    fi
    if grep -iE "(non-linear|nonlinear|fragmented structure|nested narrative|temporal complexity)" "$CONTRACT" > /dev/null 2>&1; then
      [ -n "$Q3_HIT" ] && Q3_HIT="${Q3_HIT}; non-linear/fragmented structure" || Q3_HIT="non-linear/fragmented structure"
    fi
    if [ -n "$Q3_HIT" ]; then
      Q3_TARGET="hybrid"
      [ "$POV_COUNT" -ge 6 ] && Q3_TARGET="swarm"
      if [ "$OV_Q3" -eq 1 ]; then
        echo "WARN: Q3 (many POVs / non-linear) — fired: ${Q3_HIT} (override marker present)."
      else
        echo "ERROR: Q3 (many POVs / non-linear) — fired: ${Q3_HIT}. Recommended escalation: ${Q3_TARGET}. Rationale: cross-POV coherence and information-flow tracking degrade under single-context analysis."
        ERRORS=$((ERRORS + 1))
      fi
      FIRED="${FIRED}Q3 "
      raise_escalation "$Q3_TARGET"
    fi

    # Trigger Q4: prior thin synthesis — read sidecar meta JSON if provided.
    Q4_HIT=""
    if [ -n "$META" ] && [ -f "$META" ]; then
      if grep -iE "\"underdiagnosis_flag\"\s*:\s*\"(fired|true)\"" "$META" > /dev/null 2>&1; then
        Q4_HIT="prior-run underdiagnosis flag fired"
      elif grep -iE "underdiagnosis_triggers.*\[.*[a-z]" "$META" > /dev/null 2>&1; then
        Q4_HIT="prior-run underdiagnosis triggers in meta"
      fi
    fi
    if grep -iE "(last round.*(thin|soft|underdiagnosed)|prior thin synthesis)" "$CONTRACT" > /dev/null 2>&1; then
      [ -n "$Q4_HIT" ] && Q4_HIT="${Q4_HIT}; user-stated prior-round thinness" || Q4_HIT="user-stated prior-round thinness"
    fi
    if [ -n "$Q4_HIT" ]; then
      if [ "$OV_Q4" -eq 1 ]; then
        echo "WARN: Q4 (prior thin synthesis) — fired: ${Q4_HIT} (override marker present)."
      else
        echo "ERROR: Q4 (prior thin synthesis) — fired: ${Q4_HIT}. Recommended escalation: swarm. Rationale: prior-run thinness is direct evidence the previously selected mode underdiagnoses this manuscript class."
        ERRORS=$((ERRORS + 1))
      fi
      FIRED="${FIRED}Q4 "
      raise_escalation "swarm"
    fi

    # Trigger Q5: submission readiness.
    Q5_HIT=""
    if grep -iE "GOAL:\s*submit|goal:\s*submit" "$CONTRACT" > /dev/null 2>&1; then
      Q5_HIT="goal=submit"
    fi
    if grep -iE "(Pass\s*11|PASS SET:.*\b11\b|Submission Readiness)" "$CONTRACT" > /dev/null 2>&1; then
      [ -n "$Q5_HIT" ] && Q5_HIT="${Q5_HIT}; Pass 11 in set" || Q5_HIT="Pass 11 in set"
    fi
    if grep -iE "final round before submission" "$CONTRACT" > /dev/null 2>&1; then
      [ -n "$Q5_HIT" ] && Q5_HIT="${Q5_HIT}; contract: final round before submission" || Q5_HIT="contract: final round before submission"
    fi
    if [ -n "$Q5_HIT" ]; then
      if [ "$OV_Q5" -eq 1 ]; then
        echo "WARN: Q5 (submission readiness) — fired: ${Q5_HIT} (override marker present)."
      else
        echo "ERROR: Q5 (submission readiness) — fired: ${Q5_HIT}. Recommended escalation: swarm. Rationale: highest-stakes diagnosis class; cost differential justified by consequence of missed finding."
        ERRORS=$((ERRORS + 1))
      fi
      FIRED="${FIRED}Q5 "
      raise_escalation "swarm"
    fi

    if [ "$ERRORS" -gt 0 ]; then
      echo ""
      echo "TRIGGERS: ${FIRED}; ESCALATION: ${ESCALATION}"
      echo "FAILED: ${ERRORS} quality-risk trigger(s) fired without override marker. Orchestrator must apply escalation per run-core.md §Quality-Risk Mode Selection (final mode = max(token-fit-floor, ${ESCALATION})) OR record an explicit user override marker (<!-- override: quality-risk-Q[1-5] — <rationale> -->)."
      exit 1
    else
      if [ -n "$FIRED" ]; then
        echo "OK: Triggers fired (${FIRED}) — all addressed via override markers; recommended escalation was: ${ESCALATION}."
      else
        echo "OK: No quality-risk triggers fired. Token-fit recommendation applies."
      fi
      exit 0
    fi
    ;;

  # ----------------------------------------------------------------------
  # timeline-diff <prior_timeline> <current_timeline>
  #
  # Surface every event added/removed/changed and every anchor changed
  # between two Timeline.md artifacts (Pass-10-Class rolling structured
  # artifact per core-editor/references/pass-10.md). The validator extracts
  # Section 1 (Event Ledger) pipe-table rows AND Section 3 (Temporal Marker
  # Inventory) bullet items from each file, computes a structural diff,
  # and verifies that the bullet-counts in Section 8 (Diff Notes) cover
  # the structural totals (v1.7.9 tightening: count-match, not just
  # presence-of-keyword).
  #
  # Sections 2 (Master Calendar) and 4 (Inconsistency Ledger) are largely
  # freeform prose. The bash validator does not item-diff them; true
  # item-level diffing for those sections is deferred to a Phase 7 Python
  # helper. Pass 10 model judgment still owns classification of any
  # surfaced diff.
  #
  # Exit 0: no diff exists, OR every diff is annotated in Section 8 with
  #         counts that cover the structural totals, OR a body-placed
  #         override marker is present.
  # Exit 1: diff exists and Section 8 does not document it / does not
  #         cover the totals (and no override).
  #
  # Override marker: <!-- override: timeline-diff-undocumented — <reason> -->
  # placed in the body of the current Timeline (above Section 8).
  #
  # Self-test: pass --self-test as the only argument to run built-in cases.
  # ----------------------------------------------------------------------
  timeline-diff)
    if [ $# -lt 1 ]; then echo "Usage: $0 timeline-diff <prior_timeline> <current_timeline> | --self-test"; exit 2; fi

    if [ "$1" = "--self-test" ]; then
      TMPDIR=$(mktemp -d)
      trap 'rm -rf "$TMPDIR"' EXIT
      # Positive: identical timelines → no diff.
      cat > "$TMPDIR/prior_pos.md" <<'EOF'
# Timeline
## Section 1: Event Ledger
| Scene ID | Anchor text | Span |
|---|---|---|
| Ch 1 §1 | Monday morning | 3 hours |
| Ch 1 §2 | Tuesday afternoon | 2 hours |
## Section 8: Diff Notes
n/a — first Timeline run.
EOF
      cat > "$TMPDIR/current_pos.md" <<'EOF'
# Timeline
## Section 1: Event Ledger
| Scene ID | Anchor text | Span |
|---|---|---|
| Ch 1 §1 | Monday morning | 3 hours |
| Ch 1 §2 | Tuesday afternoon | 2 hours |
## Section 8: Diff Notes
n/a — no changes since prior run.
EOF
      # Negative: scene added, but Section 8 says no changes.
      cat > "$TMPDIR/current_neg.md" <<'EOF'
# Timeline
## Section 1: Event Ledger
| Scene ID | Anchor text | Span |
|---|---|---|
| Ch 1 §1 | Monday morning | 3 hours |
| Ch 1 §2 | Tuesday afternoon | 2 hours |
| Ch 2 §1 | Wednesday morning | 1 hour |
## Section 8: Diff Notes
n/a — no changes since prior run.
EOF
      # Documented: scene added AND Section 8 documents it.
      cat > "$TMPDIR/current_doc.md" <<'EOF'
# Timeline
## Section 1: Event Ledger
| Scene ID | Anchor text | Span |
|---|---|---|
| Ch 1 §1 | Monday morning | 3 hours |
| Ch 1 §2 | Tuesday afternoon | 2 hours |
| Ch 2 §1 | Wednesday morning | 1 hour |
## Section 8: Diff Notes
- Added: Ch 2 §1 (Wednesday morning anchor) — new scene from revision round 2.
EOF
      # Override: undocumented diff but body marker present.
      cat > "$TMPDIR/current_over.md" <<'EOF'
# Timeline
<!-- override: timeline-diff-undocumented — Section 8 reorganization deferred to next run. -->
## Section 1: Event Ledger
| Scene ID | Anchor text | Span |
|---|---|---|
| Ch 1 §1 | Monday morning | 3 hours |
| Ch 1 §2 | Tuesday afternoon | 2 hours |
| Ch 2 §1 | Wednesday morning | 1 hour |
## Section 8: Diff Notes
n/a — no changes since prior run.
EOF
      # Override-in-Section-8 (appendix-equivalent) only: marker outside body → still ERROR.
      cat > "$TMPDIR/current_over_appx.md" <<'EOF'
# Timeline
## Section 1: Event Ledger
| Scene ID | Anchor text | Span |
|---|---|---|
| Ch 1 §1 | Monday morning | 3 hours |
| Ch 1 §2 | Tuesday afternoon | 2 hours |
| Ch 2 §1 | Wednesday morning | 1 hour |
## Section 8: Diff Notes
<!-- override: timeline-diff-undocumented — Marker placed in Section 8 only. -->
n/a — no changes since prior run.
EOF
      # Section 3 marker change (v1.7.9): prior has 2 markers, current
      # has 3, no Section 8 documentation. Phase 4-6 validator missed
      # this; v1.7.9 catches it.
      cat > "$TMPDIR/prior_s3.md" <<'EOF'
# Timeline
## Section 1: Event Ledger
| Scene ID | Anchor text | Span |
|---|---|---|
| Ch 1 §1 | Monday morning | 3 hours |
## Section 3: Temporal Marker Inventory
- Ch 1 §1: "Monday morning" → Day 1
- Ch 1 §2: "Tuesday afternoon" → Day 2
## Section 8: Diff Notes
n/a — first Timeline run.
EOF
      cat > "$TMPDIR/current_s3_neg.md" <<'EOF'
# Timeline
## Section 1: Event Ledger
| Scene ID | Anchor text | Span |
|---|---|---|
| Ch 1 §1 | Monday morning | 3 hours |
## Section 3: Temporal Marker Inventory
- Ch 1 §1: "Monday morning" → Day 1
- Ch 1 §2: "Tuesday afternoon" → Day 2
- Ch 2 §1: "the following Friday" → Day 5
## Section 8: Diff Notes
n/a — no changes since prior run.
EOF
      cat > "$TMPDIR/current_s3_doc.md" <<'EOF'
# Timeline
## Section 1: Event Ledger
| Scene ID | Anchor text | Span |
|---|---|---|
| Ch 1 §1 | Monday morning | 3 hours |
## Section 3: Temporal Marker Inventory
- Ch 1 §1: "Monday morning" → Day 1
- Ch 1 §2: "Tuesday afternoon" → Day 2
- Ch 2 §1: "the following Friday" → Day 5
## Section 8: Diff Notes
- Added: Ch 2 §1 marker ("the following Friday" → Day 5) — new anchor surfaced in revision round 2.
EOF
      # Count-mismatch case (v1.7.9): 3 added in §1+§3 but Section 8
      # documents only 1. Phase 4-6 validator passed; v1.7.9 catches.
      cat > "$TMPDIR/current_count_mismatch.md" <<'EOF'
# Timeline
## Section 1: Event Ledger
| Scene ID | Anchor text | Span |
|---|---|---|
| Ch 1 §1 | Monday morning | 3 hours |
| Ch 2 §1 | Wednesday morning | 1 hour |
| Ch 3 §1 | Thursday afternoon | 2 hours |
## Section 3: Temporal Marker Inventory
- Ch 1 §1: "Monday morning" → Day 1
- Ch 1 §2: "Tuesday afternoon" → Day 2
- Ch 2 §1: "the following Friday" → Day 5
## Section 8: Diff Notes
- Added: Ch 2 §1 marker — new anchor surfaced in revision.
EOF
      RESULTS=0
      "$0" timeline-diff "$TMPDIR/prior_pos.md" "$TMPDIR/current_pos.md" >/dev/null 2>&1 && echo "  pos: OK (no diff)" || { echo "  pos: FAIL (expected OK — identical timelines)"; RESULTS=1; }
      "$0" timeline-diff "$TMPDIR/prior_pos.md" "$TMPDIR/current_neg.md" >/dev/null 2>&1 && { echo "  neg: FAIL (expected ERROR — undocumented §1 diff)"; RESULTS=1; } || echo "  neg: OK (caught — undocumented §1 diff)"
      "$0" timeline-diff "$TMPDIR/prior_pos.md" "$TMPDIR/current_doc.md" >/dev/null 2>&1 && echo "  doc: OK (diff documented in Section 8)" || { echo "  doc: FAIL (expected OK — diff documented)"; RESULTS=1; }
      "$0" timeline-diff "$TMPDIR/prior_pos.md" "$TMPDIR/current_over.md" >/dev/null 2>&1 && echo "  over: OK (body marker downgraded ERROR→WARN)" || { echo "  over: FAIL (expected OK after override)"; RESULTS=1; }
      "$0" timeline-diff "$TMPDIR/prior_pos.md" "$TMPDIR/current_over_appx.md" >/dev/null 2>&1 && { echo "  over_appx: FAIL (Section-8 marker should not downgrade)"; RESULTS=1; } || echo "  over_appx: OK (caught — marker in Section 8 is non-canonical)"
      "$0" timeline-diff "$TMPDIR/prior_s3.md" "$TMPDIR/current_s3_neg.md" >/dev/null 2>&1 && { echo "  s3_neg: FAIL (expected ERROR — undocumented Section 3 marker change)"; RESULTS=1; } || echo "  s3_neg: OK (caught — Section 3 marker change)"
      "$0" timeline-diff "$TMPDIR/prior_s3.md" "$TMPDIR/current_s3_doc.md" >/dev/null 2>&1 && echo "  s3_doc: OK (Section 3 change documented)" || { echo "  s3_doc: FAIL (expected OK — Section 3 change documented)"; RESULTS=1; }
      "$0" timeline-diff "$TMPDIR/prior_s3.md" "$TMPDIR/current_count_mismatch.md" >/dev/null 2>&1 && { echo "  count_mismatch: FAIL (expected ERROR — Section 8 count below structural totals)"; RESULTS=1; } || echo "  count_mismatch: OK (caught — Section 8 documented count below structural totals)"
      [ "$RESULTS" -eq 0 ] && { echo "Self-test: PASS"; exit 0; } || { echo "Self-test: FAIL"; exit 1; }
    fi

    if [ $# -lt 2 ]; then echo "Usage: $0 timeline-diff <prior_timeline> <current_timeline>"; exit 2; fi
    if [ ! -f "$1" ]; then echo "Error: File not found: $1" >&2; exit 2; fi
    if [ ! -f "$2" ]; then echo "Error: File not found: $2" >&2; exit 2; fi
    PRIOR="$1"
    CURRENT="$2"

    # Split current Timeline into body (above Section 8) and Section 8.
    # Markers in Section 8 are non-canonical (Section 8 is the appendix-equivalent).
    SECTION8_LINE=$(grep -niE "^#{1,4}.*Section 8" "$CURRENT" 2>/dev/null | head -1 | cut -d: -f1 || true)
    if [ -n "$SECTION8_LINE" ]; then
      BODY=$(sed -n "1,$((SECTION8_LINE - 1))p" "$CURRENT")
      SECTION8=$(sed -n "${SECTION8_LINE},\$p" "$CURRENT")
    else
      BODY=$(cat "$CURRENT")
      SECTION8=""
    fi

    # Override marker detection — body only.
    OV_DIFF=0
    echo "$BODY" | grep -F "<!-- override: timeline-diff-undocumented" > /dev/null 2>&1 && OV_DIFF=1

    # Extract Event Ledger table rows from each file.
    # Heuristic: pipe-table rows (starting with |) that are not the header
    # row and not the alignment row (containing only --- and |).
    extract_event_rows() {
      local file="$1"
      grep -E "^\|" "$file" 2>/dev/null \
        | grep -vE "^\|[[:space:]]*---" \
        | grep -vE "^\|[[:space:]]*Scene ID" \
        | sort -u
    }

    # Extract Section 3 (Temporal Marker Inventory) bullet items.
    # Heuristic: bullet lines (`- ...`) inside the Section 3 territory
    # (from the Section 3 heading to the next `^## ` heading or EOF).
    # v1.7.9: added per pass-10.md §Section 3 and the Phase 6 review
    # finding that Section 3 marker changes were silently missed.
    extract_section3_markers() {
      local file="$1"
      awk '
        /^## .*Section 3/ { in_s3 = 1; next }
        /^## / { in_s3 = 0 }
        in_s3 && /^- / { print }
      ' "$file" 2>/dev/null \
        | sort -u
    }

    PRIOR_ROWS=$(extract_event_rows "$PRIOR")
    CURRENT_ROWS=$(extract_event_rows "$CURRENT")
    PRIOR_S3=$(extract_section3_markers "$PRIOR")
    CURRENT_S3=$(extract_section3_markers "$CURRENT")

    # Compute additions and removals via comm — Section 1 Event Ledger.
    PRIOR_TMP=$(mktemp); CURRENT_TMP=$(mktemp)
    echo "$PRIOR_ROWS" > "$PRIOR_TMP"
    echo "$CURRENT_ROWS" > "$CURRENT_TMP"
    ADDED=$(comm -13 "$PRIOR_TMP" "$CURRENT_TMP" | grep -cE "^\|" || true)
    REMOVED=$(comm -23 "$PRIOR_TMP" "$CURRENT_TMP" | grep -cE "^\|" || true)
    rm -f "$PRIOR_TMP" "$CURRENT_TMP"
    ADDED=${ADDED:-0}
    REMOVED=${REMOVED:-0}

    # Compute additions and removals — Section 3 Temporal Marker Inventory.
    PRIOR_S3_TMP=$(mktemp); CURRENT_S3_TMP=$(mktemp)
    echo "$PRIOR_S3" > "$PRIOR_S3_TMP"
    echo "$CURRENT_S3" > "$CURRENT_S3_TMP"
    S3_ADDED=$(comm -13 "$PRIOR_S3_TMP" "$CURRENT_S3_TMP" | grep -cE "^- " || true)
    S3_REMOVED=$(comm -23 "$PRIOR_S3_TMP" "$CURRENT_S3_TMP" | grep -cE "^- " || true)
    rm -f "$PRIOR_S3_TMP" "$CURRENT_S3_TMP"
    S3_ADDED=${S3_ADDED:-0}
    S3_REMOVED=${S3_REMOVED:-0}

    DIFF_TOTAL=$((ADDED + REMOVED + S3_ADDED + S3_REMOVED))
    EXPECTED_ADDED=$((ADDED + S3_ADDED))
    EXPECTED_REMOVED=$((REMOVED + S3_REMOVED))

    if [ "$DIFF_TOTAL" -eq 0 ]; then
      echo "OK: No structural diff between prior and current Timeline (Section 1 + Section 3 checked)."
      exit 0
    fi

    # Diff exists. Check if Section 8 documents it.
    # Heuristic: Section 8 must contain at least one of the documented-
    # change markers AND the count of "Added:" / "Removed:" / "Changed:"
    # bullets must match the structural diff totals (count match per
    # v1.7.9 tightening — placeholder text alone is not sufficient).
    DOCUMENTED=0
    DOC_ADDED=0
    DOC_REMOVED=0
    if [ -n "$SECTION8" ]; then
      if echo "$SECTION8" | grep -iE "(Added|Removed|Changed|Anchors changed|Calculations changed|Paradoxes (resolved|introduced))" > /dev/null 2>&1; then
        DOCUMENTED=1
        DOC_ADDED=$( { echo "$SECTION8" | grep -cE "^[-*][[:space:]]+(Added|Anchors? added)" 2>/dev/null || true; } | head -1 | tr -d ' \n')
        DOC_REMOVED=$( { echo "$SECTION8" | grep -cE "^[-*][[:space:]]+(Removed|Anchors? removed)" 2>/dev/null || true; } | head -1 | tr -d ' \n')
        DOC_ADDED=${DOC_ADDED:-0}
        DOC_REMOVED=${DOC_REMOVED:-0}
      fi
    fi

    # If Section 8 has documented-change markers but no bulleted entries,
    # we cannot do count matching; treat it as documented (legacy behavior).
    # If bulleted entries are present, require the counts to be plausible
    # (≥ structural totals, allowing for grouped entries).
    if [ "$DOCUMENTED" -eq 1 ]; then
      COUNT_OK=1
      if [ "$DOC_ADDED" -gt 0 ] || [ "$DOC_REMOVED" -gt 0 ]; then
        # Bullet-form documentation; compare to structural totals.
        if [ "$DOC_ADDED" -lt "$EXPECTED_ADDED" ] || [ "$DOC_REMOVED" -lt "$EXPECTED_REMOVED" ]; then
          COUNT_OK=0
        fi
      fi
      if [ "$COUNT_OK" -eq 1 ]; then
        echo "OK: Diff detected (${DIFF_TOTAL} change(s); §1: ${ADDED} added, ${REMOVED} removed; §3: ${S3_ADDED} added, ${S3_REMOVED} removed) and documented in Section 8."
        exit 0
      fi
      if [ "$OV_DIFF" -eq 1 ]; then
        echo "WARN: Section 8 documented-entry counts (${DOC_ADDED} added, ${DOC_REMOVED} removed) below structural totals (${EXPECTED_ADDED} added, ${EXPECTED_REMOVED} removed); body override marker present."
        exit 0
      fi
      echo "ERROR: Section 8 documented-entry counts (${DOC_ADDED} added, ${DOC_REMOVED} removed) do not cover structural diff (${EXPECTED_ADDED} added, ${EXPECTED_REMOVED} removed) across §1 + §3. Add missing entries in Section 8 or place a body override marker. Canonical home: core-editor/references/pass-10.md §Section 8."
      exit 1
    fi

    if [ "$OV_DIFF" -eq 1 ]; then
      echo "WARN: Diff detected (${DIFF_TOTAL} change(s); §1: ${ADDED} added, ${REMOVED} removed; §3: ${S3_ADDED} added, ${S3_REMOVED} removed); Section 8 does not document, but body override marker present."
      exit 0
    fi

    echo "ERROR: Diff detected (${DIFF_TOTAL} change(s); §1: ${ADDED} added, ${REMOVED} removed; §3: ${S3_ADDED} added, ${S3_REMOVED} removed). Section 8 (Diff Notes) does not document the change. Add an entry in Section 8 or place a body override marker <!-- override: timeline-diff-undocumented — <reason> --> above Section 8. Note: Sections 2 (Master Calendar) and 4 (Inconsistency Ledger) are diffed at section-presence level only — true item-level diffing for those freeform sections is deferred to a Phase 7 Python helper. Canonical home: core-editor/references/pass-10.md §Section 8."
    exit 1
    ;;

  # ----------------------------------------------------------------------
  # timeline-arithmetic <timeline_file>
  #
  # MARKER HYGIENE CHECK ONLY (v1.7.9 honest reframing).
  #
  # This validator does NOT independently compute span arithmetic. True
  # arithmetic verification requires structured Timeline parsing — date
  # math across heterogeneous anchor formats ("Day 1 morning", "the
  # following Friday", "January 14"), span normalization, and overlap
  # detection — which is not feasible in bash. That work is deferred to
  # a Phase 7 Python helper.
  #
  # What this validator actually does:
  #   (a) Surfaces rows whose gap-from-previous cell carries a negative
  #       numeric value (text matching /\|[[:space:]]*-\d+/ in a pipe-row).
  #       This catches the visible-after-revision case where the author
  #       has already noticed the ordering broke and recorded the
  #       negative gap explicitly.
  #   (b) Surfaces rows that carry an in-line "(conflicts ...)" or
  #       "(contradicts ...)" parenthetical — i.e., the Pass 10 model
  #       has already pre-labeled the conflict.
  #
  # What this validator does NOT do (Phase 7 work):
  #   - Independently compute that "Day 1 morning + 30-hour span" is
  #     incompatible with "Day 1 afternoon" being the next scene.
  #   - Detect anchor conflicts that the Pass 10 model failed to pre-label.
  #   - Normalize anchor formats and reason about elapsed time.
  #
  # Real arithmetic violations that pass through unflagged include any
  # case where the model wrote consistent-looking pipe rows whose spans
  # don't actually sum. Pass 10 model judgment is still the primary
  # classifier; this validator is a safety net for the cases where the
  # model already did the work.
  #
  # Exit 0: no marker-hygiene candidates surfaced.
  # Exit 1: candidates surfaced and no body override marker present.
  #
  # Override marker: <!-- override: timeline-arithmetic-conflict — <reason> -->
  # placed in the body of the Timeline (above Section 8).
  #
  # Self-test: pass --self-test as the only argument to run built-in cases.
  # ----------------------------------------------------------------------
  timeline-arithmetic)
    if [ $# -lt 1 ]; then echo "Usage: $0 timeline-arithmetic <timeline_file> | --self-test"; exit 2; fi

    if [ "$1" = "--self-test" ]; then
      TMPDIR=$(mktemp -d)
      trap 'rm -rf "$TMPDIR"' EXIT
      # Positive: clean spans, sequential days.
      cat > "$TMPDIR/pos.md" <<'EOF'
# Timeline
## Section 1: Event Ledger
| Scene ID | Anchor | Span | Gap from previous |
|---|---|---|---|
| Ch 1 §1 | Day 1 morning | 3 hours | n/a |
| Ch 1 §2 | Day 1 afternoon | 2 hours | 4 hours |
| Ch 2 §1 | Day 2 morning | 1 hour | 16 hours |
## Section 8: Diff Notes
n/a — first run.
EOF
      # Negative 1: negative gap (revision broke ordering).
      cat > "$TMPDIR/neg1.md" <<'EOF'
# Timeline
## Section 1: Event Ledger
| Scene ID | Anchor | Span | Gap from previous |
|---|---|---|---|
| Ch 1 §1 | Day 5 morning | 2 hours | n/a |
| Ch 1 §2 | Day 3 afternoon | 1 hour | -2 days |
## Section 8: Diff Notes
n/a.
EOF
      # Negative 2: two scenes share Day-N anchor with explicit conflict marker.
      cat > "$TMPDIR/neg2.md" <<'EOF'
# Timeline
## Section 1: Event Ledger
| Scene ID | Anchor | Span | Gap from previous |
|---|---|---|---|
| Ch 1 §1 | Day 4 morning | 6 hours | n/a |
| Ch 5 §2 | Day 4 morning (conflicts with Ch 1 §1 6-hour span) | 8 hours | 0 |
## Section 8: Diff Notes
n/a.
EOF
      # Override: negative gap with body marker → WARN, exit 0.
      cat > "$TMPDIR/over.md" <<'EOF'
# Timeline
<!-- override: timeline-arithmetic-conflict — Negative gap is intentional flashback in Ch 1 §2. -->
## Section 1: Event Ledger
| Scene ID | Anchor | Span | Gap from previous |
|---|---|---|---|
| Ch 1 §1 | Day 5 morning | 2 hours | n/a |
| Ch 1 §2 | Day 3 afternoon (flashback) | 1 hour | -2 days |
## Section 8: Diff Notes
n/a.
EOF
      # Override-in-Section-8 only: should still error.
      cat > "$TMPDIR/over_appx.md" <<'EOF'
# Timeline
## Section 1: Event Ledger
| Scene ID | Anchor | Span | Gap from previous |
|---|---|---|---|
| Ch 1 §1 | Day 5 morning | 2 hours | n/a |
| Ch 1 §2 | Day 3 afternoon | 1 hour | -2 days |
## Section 8: Diff Notes
<!-- override: timeline-arithmetic-conflict — Marker in Section 8 only. -->
n/a.
EOF
      # v1.7.9 honest-reframing case: a true arithmetic violation that
      # the model wrote without pre-labeling. Day 1 morning + 30 hr span
      # is incompatible with Day 1 afternoon being the next scene, but
      # the spans look syntactically clean. The bash validator cannot
      # detect this; it passes. Phase 7 Python helper would catch it.
      cat > "$TMPDIR/silent_arithmetic.md" <<'EOF'
# Timeline
## Section 1: Event Ledger
| Scene ID | Anchor | Span | Gap from previous |
|---|---|---|---|
| Ch 1 §1 | Day 1 morning | 30 hours | n/a |
| Ch 1 §2 | Day 1 afternoon | 2 hours | 4 hours |
## Section 8: Diff Notes
n/a.
EOF
      RESULTS=0
      "$0" timeline-arithmetic "$TMPDIR/pos.md" >/dev/null 2>&1 && echo "  pos: OK (marker hygiene clean)" || { echo "  pos: FAIL (expected OK)"; RESULTS=1; }
      "$0" timeline-arithmetic "$TMPDIR/neg1.md" >/dev/null 2>&1 && { echo "  neg1: FAIL (expected ERROR — negative gap surfaced)"; RESULTS=1; } || echo "  neg1: OK (caught — negative gap surfaced)"
      "$0" timeline-arithmetic "$TMPDIR/neg2.md" >/dev/null 2>&1 && { echo "  neg2: FAIL (expected ERROR — pre-labeled anchor conflict)"; RESULTS=1; } || echo "  neg2: OK (caught — pre-labeled anchor conflict)"
      "$0" timeline-arithmetic "$TMPDIR/over.md" >/dev/null 2>&1 && echo "  over: OK (body marker downgraded ERROR→WARN)" || { echo "  over: FAIL (expected OK after override)"; RESULTS=1; }
      "$0" timeline-arithmetic "$TMPDIR/over_appx.md" >/dev/null 2>&1 && { echo "  over_appx: FAIL (Section-8 marker should not downgrade)"; RESULTS=1; } || echo "  over_appx: OK (caught — marker in Section 8 is non-canonical)"
      "$0" timeline-arithmetic "$TMPDIR/silent_arithmetic.md" >/dev/null 2>&1 && echo "  silent_arithmetic: PASSES (documented Phase 7 limitation — bash cannot independently sum spans; true arithmetic verification deferred)" || { echo "  silent_arithmetic: UNEXPECTED — bash claims to detect silent span violation; investigate"; RESULTS=1; }
      [ "$RESULTS" -eq 0 ] && { echo "Self-test: PASS (marker hygiene only — see Phase 7 deferral note)"; exit 0; } || { echo "Self-test: FAIL"; exit 1; }
    fi

    if [ ! -f "$1" ]; then echo "Error: File not found: $1" >&2; exit 2; fi
    TIMELINE="$1"

    # Split body vs Section 8.
    SECTION8_LINE=$(grep -niE "^#{1,4}.*Section 8" "$TIMELINE" 2>/dev/null | head -1 | cut -d: -f1 || true)
    if [ -n "$SECTION8_LINE" ]; then
      BODY=$(sed -n "1,$((SECTION8_LINE - 1))p" "$TIMELINE")
    else
      BODY=$(cat "$TIMELINE")
    fi

    # Override marker — body only.
    OV_AR=0
    echo "$BODY" | grep -F "<!-- override: timeline-arithmetic-conflict" > /dev/null 2>&1 && OV_AR=1

    # Check (a): negative gap. Match table cells containing /^[[:space:]]*-[0-9]/
    # within a pipe-row, or the literal phrase "negative" or "negative gap".
    NEG_GAPS=$( { echo "$BODY" | grep -cE "\|[[:space:]]*-[0-9]+[[:space:]]*(hours?|days?|minutes?|weeks?|months?|years?)" 2>/dev/null || true; } | head -1 | tr -d ' \n')
    NEG_GAPS=${NEG_GAPS:-0}

    # Check (b): explicit conflict / contradiction marker in event ledger rows.
    CONFLICT_MARKERS=$( { echo "$BODY" | grep -cE "\|.*\((conflicts|contradicts)" 2>/dev/null || true; } | head -1 | tr -d ' \n')
    CONFLICT_MARKERS=${CONFLICT_MARKERS:-0}

    TOTAL_CONFLICTS=$((NEG_GAPS + CONFLICT_MARKERS))

    if [ "$TOTAL_CONFLICTS" -eq 0 ]; then
      echo "OK: Marker hygiene clean (no negative gaps, no pre-labeled anchor conflicts). Note: this is a marker-hygiene check only — true arithmetic verification (span sums, anchor-format normalization) is deferred to a Phase 7 Python helper."
      exit 0
    fi

    if [ "$OV_AR" -eq 1 ]; then
      echo "WARN: ${TOTAL_CONFLICTS} marker-hygiene candidate(s) detected (${NEG_GAPS} negative gap(s); ${CONFLICT_MARKERS} pre-labeled conflict(s)); body override marker present. Marker hygiene only — true arithmetic verification deferred to Phase 7."
      exit 0
    fi

    echo "ERROR: ${TOTAL_CONFLICTS} marker-hygiene candidate(s) surfaced (${NEG_GAPS} negative gap(s); ${CONFLICT_MARKERS} pre-labeled conflict(s)). Surface these in Section 4 (Inconsistency Ledger), classify each, or place a body override marker <!-- override: timeline-arithmetic-conflict — <reason> --> above Section 8. Marker hygiene only — true arithmetic verification (span sums, anchor-format normalization) is deferred to a Phase 7 Python helper. Canonical home: core-editor/references/pass-10.md §Section 4."
    exit 1
    ;;

  # ----------------------------------------------------------------------
  # timeline-anchor-conflict <timeline_file>
  #
  # PRE-LABELED CONFLICT SURFACING ONLY (v1.7.9 honest reframing).
  #
  # This validator does NOT independently parse temporal anchors per
  # scene/chapter and reason about same-anchor-different-time conflicts.
  # True anchor conflict detection requires structured Timeline parsing —
  # anchor extraction per scene, format normalization across heterogeneous
  # marker types ("Monday morning" vs "March 14" vs "the day after the
  # half marathon"), and pairwise compatibility reasoning — which is not
  # feasible in bash. That work is deferred to a Phase 7 Python helper.
  #
  # What this validator actually does:
  #   - Counts parenthetical "(contradicts ...)", "(paradox with ...)",
  #     and "(conflicts with ...)" annotations anywhere in the Timeline
  #     body. These are pre-flagged candidates the Pass 10 model has
  #     already identified — the validator surfaces them so the model
  #     must explicitly classify each in Section 4.
  #
  # What this validator does NOT do (Phase 7 work):
  #   - Detect that Ch 1 §1 says "Monday morning" and Ch 1 §2 says
  #     "Tuesday morning" but the spans imply they are the same day.
  #   - Reason about anchor compatibility across chapter ordering.
  #   - Detect drift that the Pass 10 model failed to pre-label.
  #
  # A model that wrote inconsistent anchors but didn't notice the
  # conflict will pass this validator. Pass 10 model judgment is still
  # the primary classifier; this validator is a safety net for the
  # cases where the model already noticed.
  #
  # Exit 0: no pre-labeled conflict candidates surfaced.
  # Exit 1: candidates surfaced and no body override marker present.
  #
  # Override marker: <!-- override: timeline-anchor-conflict — <reason> -->
  # placed in the body of the Timeline (above Section 8).
  #
  # Self-test: pass --self-test as the only argument to run built-in cases.
  # ----------------------------------------------------------------------
  timeline-anchor-conflict)
    if [ $# -lt 1 ]; then echo "Usage: $0 timeline-anchor-conflict <timeline_file> | --self-test"; exit 2; fi

    if [ "$1" = "--self-test" ]; then
      TMPDIR=$(mktemp -d)
      trap 'rm -rf "$TMPDIR"' EXIT
      # Positive: distinct anchors, no conflicts.
      cat > "$TMPDIR/pos.md" <<'EOF'
# Timeline
## Section 3: Temporal Marker Inventory
- Ch 1 §1: "Monday morning" → Day 1
- Ch 1 §2: "Tuesday afternoon" → Day 2
- Ch 2 §1: "the following Friday" → Day 5
## Section 8: Diff Notes
n/a.
EOF
      # Negative 1: pre-flagged contradiction marker in entry text.
      cat > "$TMPDIR/neg1.md" <<'EOF'
# Timeline
## Section 3: Temporal Marker Inventory
- Ch 1 §1: "Monday morning" → Day 1
- Ch 5 §3: "Tuesday afternoon" → Day 9 (contradicts Ch 1 §1 Monday-anchor calculation)
## Section 8: Diff Notes
n/a.
EOF
      # Negative 2: pre-flagged paradox marker in entry text.
      cat > "$TMPDIR/neg2.md" <<'EOF'
# Timeline
## Section 3: Temporal Marker Inventory
- Ch 1 §1: "March 14" → Day 1
- Ch 4 §1: "January 2 of the same year" → (paradox with Ch 1 §1 timeline)
## Section 8: Diff Notes
n/a.
EOF
      # Override: contradiction marker but body override → WARN, exit 0.
      cat > "$TMPDIR/over.md" <<'EOF'
# Timeline
<!-- override: timeline-anchor-conflict — Intentional dream-sequence in Ch 5 §3; classified in Section 4 as ambiguous-by-design. -->
## Section 3: Temporal Marker Inventory
- Ch 1 §1: "Monday morning" → Day 1
- Ch 5 §3: "Tuesday afternoon" → Day 9 (contradicts Ch 1 §1 Monday-anchor calculation)
## Section 8: Diff Notes
n/a.
EOF
      # Override-in-Section-8 only.
      cat > "$TMPDIR/over_appx.md" <<'EOF'
# Timeline
## Section 3: Temporal Marker Inventory
- Ch 1 §1: "Monday morning" → Day 1
- Ch 5 §3: "Tuesday afternoon" → Day 9 (contradicts Ch 1 §1 Monday-anchor calculation)
## Section 8: Diff Notes
<!-- override: timeline-anchor-conflict — Marker in Section 8 only. -->
n/a.
EOF
      # v1.7.9 honest-reframing case: same Ch 1 §1 with both "Monday
      # morning" and "Tuesday morning" anchors but no parenthetical
      # pre-labeling. Phase 4-6 validator passed; v1.7.9 still passes
      # (this is the documented Phase 7 limitation — true anchor parsing
      # is deferred).
      cat > "$TMPDIR/silent_anchor.md" <<'EOF'
# Timeline
## Section 3: Temporal Marker Inventory
- Ch 1 §1: "Monday morning" → Day 1
- Ch 1 §1: "Tuesday morning" → Day 2
## Section 8: Diff Notes
n/a.
EOF
      RESULTS=0
      "$0" timeline-anchor-conflict "$TMPDIR/pos.md" >/dev/null 2>&1 && echo "  pos: OK (no pre-labeled conflicts)" || { echo "  pos: FAIL (expected OK)"; RESULTS=1; }
      "$0" timeline-anchor-conflict "$TMPDIR/neg1.md" >/dev/null 2>&1 && { echo "  neg1: FAIL (expected ERROR — pre-labeled contradiction)"; RESULTS=1; } || echo "  neg1: OK (caught — pre-labeled contradiction)"
      "$0" timeline-anchor-conflict "$TMPDIR/neg2.md" >/dev/null 2>&1 && { echo "  neg2: FAIL (expected ERROR — pre-labeled paradox)"; RESULTS=1; } || echo "  neg2: OK (caught — pre-labeled paradox)"
      "$0" timeline-anchor-conflict "$TMPDIR/over.md" >/dev/null 2>&1 && echo "  over: OK (body marker downgraded ERROR→WARN)" || { echo "  over: FAIL (expected OK after override)"; RESULTS=1; }
      "$0" timeline-anchor-conflict "$TMPDIR/over_appx.md" >/dev/null 2>&1 && { echo "  over_appx: FAIL (Section-8 marker should not downgrade)"; RESULTS=1; } || echo "  over_appx: OK (caught — marker in Section 8 is non-canonical)"
      "$0" timeline-anchor-conflict "$TMPDIR/silent_anchor.md" >/dev/null 2>&1 && echo "  silent_anchor: PASSES (documented Phase 7 limitation — bash cannot independently parse anchor formats; true conflict detection deferred)" || { echo "  silent_anchor: UNEXPECTED — bash claims to detect un-pre-labeled drift; investigate"; RESULTS=1; }
      [ "$RESULTS" -eq 0 ] && { echo "Self-test: PASS (pre-labeled surfacing only — see Phase 7 deferral note)"; exit 0; } || { echo "Self-test: FAIL"; exit 1; }
    fi

    if [ ! -f "$1" ]; then echo "Error: File not found: $1" >&2; exit 2; fi
    TIMELINE="$1"

    # Split body vs Section 8.
    SECTION8_LINE=$(grep -niE "^#{1,4}.*Section 8" "$TIMELINE" 2>/dev/null | head -1 | cut -d: -f1 || true)
    if [ -n "$SECTION8_LINE" ]; then
      BODY=$(sed -n "1,$((SECTION8_LINE - 1))p" "$TIMELINE")
    else
      BODY=$(cat "$TIMELINE")
    fi

    # Override marker — body only.
    OV_AC=0
    echo "$BODY" | grep -F "<!-- override: timeline-anchor-conflict" > /dev/null 2>&1 && OV_AC=1

    # Detect pre-flagged contradiction / paradox annotations in Section 3.
    # Heuristic: parenthetical "(contradicts ...)" or "(paradox with ...)" or
    # "(conflicts with ...)" anywhere in the body's Section 3 territory.
    # We don't try to bound exactly to Section 3 — these annotations are
    # legitimate signals wherever they appear in the body.
    CANDIDATES=$( { echo "$BODY" | grep -ciE "\((contradicts|paradox with|conflicts with)" 2>/dev/null || true; } | head -1 | tr -d ' \n')
    CANDIDATES=${CANDIDATES:-0}

    if [ "$CANDIDATES" -eq 0 ]; then
      echo "OK: No pre-labeled anchor-conflict candidates surfaced. Note: this is a pre-labeled-conflict surfacing check only — true anchor parsing for unlabeled drift is deferred to a Phase 7 Python helper."
      exit 0
    fi

    if [ "$OV_AC" -eq 1 ]; then
      echo "WARN: ${CANDIDATES} pre-labeled anchor-conflict candidate(s) surfaced; body override marker present. Pre-labeled conflict surfacing only — true anchor parsing deferred to Phase 7."
      exit 0
    fi

    echo "ERROR: ${CANDIDATES} pre-labeled anchor-conflict candidate(s) surfaced. Pass 10 model judgment must classify each as paradox / drift / ambiguity / intentional-feature in Section 4 (Inconsistency Ledger), or place a body override marker <!-- override: timeline-anchor-conflict — <reason> --> above Section 8. Pre-labeled conflict surfacing only — true anchor parsing for unlabeled drift is deferred to a Phase 7 Python helper. Canonical home: core-editor/references/pass-10.md §Section 4."
    exit 1
    ;;

  # ----------------------------------------------------------------------
  # audit-tier-criterion <pass_dependencies_file> [<audits_root_dir>]
  #
  # Mechanical check that audit tier assignments in pass-dependencies.md
  # §4a/§4b match the §4c Audit Tier Promotion Criteria documented in
  # the same file (Phase 6 Wave 2 added the criteria).
  #
  # Three criteria from §4c (per the canonical home):
  #   1. The audit produces named hard gates or audit-internal Must-Fix
  #      floors (severity signals strong enough to gate synthesis).
  #   2. The audit catches a class of issue undetectable by passes
  #      alone (the audit's absence creates a blind spot, not just
  #      lower-resolution coverage).
  #   3. Disclosure is non-equivalent to running the audit (blind-spot
  #      disclosure cannot reasonably substitute for the audit's
  #      output).
  #
  # The validator scans §4a + §4b for tier assignments per audit and,
  # for each audit at Auto-run / Auto-recommend before synthesis /
  # Pre-DE Prerequisite / Hard Prerequisite tier, looks for hard-gate
  # / Must-Fix-floor language in the audit's reference file. Audits
  # at high tiers without named hard gates / Must-Fix floors are
  # surfaced as candidates for tier review.
  #
  # IMPORTANT — capability ceiling. This validator can only verify
  # criterion 1 mechanically (named hard gates / Must-Fix floors are
  # detectable by reference-file pattern matching). Criteria 2 and 3
  # require model judgment about the manuscript / fixture corpus and
  # cannot be verified by bash. The validator surfaces criterion-1
  # gaps; criteria 2 and 3 remain in the §4a/§4b verification
  # subsection prose.
  #
  # Override marker: <!-- override: audit-tier-criterion-<audit-slug>
  # — <rationale> --> placed in pass-dependencies.md body. One marker
  # per audit; rationale must name which criterion is overridden and
  # why.
  #
  # Self-test: pass --self-test as the only argument to run built-in
  # cases.
  # ----------------------------------------------------------------------
  audit-tier-criterion)
    if [ $# -lt 1 ]; then echo "Usage: $0 audit-tier-criterion <pass_dependencies_file> [<audits_root_dir>] | --self-test"; exit 2; fi

    if [ "$1" = "--self-test" ]; then
      TMPDIR=$(mktemp -d)
      trap 'rm -rf "$TMPDIR"' EXIT
      mkdir -p "$TMPDIR/audits"
      # Positive case: pass-dependencies references audits at high
      # tiers that ALL document hard gates / Must-Fix floors in their
      # reference files.
      cat > "$TMPDIR/pos_pd.md" <<'EOF'
## §4a. Router-triggered audits
| Trigger | Audit | Tier | Reference |
|---|---|---|---|
| Erotic content flagged at intake | Erotic Content | Auto-run (bundled with workflow) | `audits/erotic-content.md` |
| Representation or reception sensitivity disclosed at intake | Reception Risk | Auto-recommend before synthesis | `audits/reception-risk.md` |
## §4b. Finding-triggered audits
| Layer | Trigger | Audit | Tier |
|---|---|---|---|
| 1 (Reader Experience) | Pacing stalls | Compression | Auto-recommend before synthesis |
EOF
      cat > "$TMPDIR/audits/erotic-content.md" <<'EOF'
# Erotic Content Audit
## Hard Gates
- EC-1 hard gate: explicit non-consensual content without aftercare framing.
## Must-Fix floor
Any §Hard Gate firing produces audit-internal Must-Fix floor.
EOF
      cat > "$TMPDIR/audits/reception-risk.md" <<'EOF'
# Reception Risk Audit
## §7 Severity Hard Gates
Five hard gates: extractable hate, minor exploitation, etc.
Must-Fix floor when any hard gate fires.
EOF
      cat > "$TMPDIR/audits/compression-audit.md" <<'EOF'
# Compression Audit
## §7 Hard Gates
Compression hard gate fires on systematic narrative summary.
Must-Fix floor: any §7 hard gate triggers audit-internal Must-Fix.
EOF
      # Negative case: an audit at Auto-recommend before synthesis tier
      # whose reference file documents only Recommend/Note-class output
      # (no hard gates, no Must-Fix floor).
      cat > "$TMPDIR/neg_pd.md" <<'EOF'
## §4a. Router-triggered audits
| Trigger | Audit | Tier | Reference |
|---|---|---|---|
| Some trigger | Soft Audit | Auto-recommend before synthesis | `audits/soft-audit.md` |
EOF
      cat > "$TMPDIR/audits/soft-audit.md" <<'EOF'
# Soft Audit
## Output
Produces only Note-class observations. Surfaces patterns for editorial review. Severity outputs: Recommend / Note / Suggestion.
EOF
      # Override case: same as neg_pd but with override marker present.
      cat > "$TMPDIR/over_pd.md" <<'EOF'
## §4a. Router-triggered audits
| Trigger | Audit | Tier | Reference |
|---|---|---|---|
| Some trigger | Soft Audit | Auto-recommend before synthesis | `audits/soft-audit.md` |

<!-- override: audit-tier-criterion-soft-audit — Promoted on cross-fixture material findings (criterion 2); criterion 1 deliberately waived per Phase 7 Wave 2 plan. -->
EOF
      # Edge case: audit at Recommend tier (low tier — no criterion check
      # applies). Should pass regardless of reference-file content.
      cat > "$TMPDIR/edge_pd.md" <<'EOF'
## §4b. Finding-triggered audits
| Layer | Trigger | Audit | Tier |
|---|---|---|---|
| 9 (Thematic Coherence) | Some pattern | Some Recommend Audit | Recommend |
EOF
      RESULTS=0
      "$0" audit-tier-criterion "$TMPDIR/pos_pd.md" "$TMPDIR/audits" >/dev/null 2>&1 && echo "  pos: OK (high-tier audits document hard gates / Must-Fix floors)" || { echo "  pos: FAIL (expected OK)"; RESULTS=1; }
      "$0" audit-tier-criterion "$TMPDIR/neg_pd.md" "$TMPDIR/audits" >/dev/null 2>&1 && { echo "  neg: FAIL (expected ERROR — high-tier audit lacks criterion-1 hard-gate language)"; RESULTS=1; } || echo "  neg: OK (caught — soft audit at Auto-recommend before synthesis tier)"
      "$0" audit-tier-criterion "$TMPDIR/over_pd.md" "$TMPDIR/audits" >/dev/null 2>&1 && echo "  over: OK (override marker downgrades ERROR→WARN)" || { echo "  over: FAIL (expected OK after override)"; RESULTS=1; }
      "$0" audit-tier-criterion "$TMPDIR/edge_pd.md" "$TMPDIR/audits" >/dev/null 2>&1 && echo "  edge: OK (Recommend-tier audit not subject to criterion-1 check)" || { echo "  edge: FAIL (expected OK — Recommend tier exempt)"; RESULTS=1; }
      [ "$RESULTS" -eq 0 ] && { echo "Self-test: PASS"; exit 0; } || { echo "Self-test: FAIL"; exit 1; }
    fi

    if [ ! -f "$1" ]; then echo "Error: File not found: $1" >&2; exit 2; fi
    PD_FILE="$1"
    AUDIT_ROOT="${2:-}"
    # Default audit root: try the conventional layout if not provided.
    if [ -z "$AUDIT_ROOT" ]; then
      PD_DIR=$(dirname "$PD_FILE")
      # Common layout: pass-dependencies.md is in core-editor/references;
      # audits live in ../../specialized-audits/references/.
      if [ -d "$PD_DIR/../../specialized-audits/references" ]; then
        AUDIT_ROOT="$PD_DIR/../../specialized-audits/references"
      else
        AUDIT_ROOT="$PD_DIR"
      fi
    fi

    ERRORS=0
    WARNS=0

    # Tiers that require the criterion-1 (hard-gate / Must-Fix floor)
    # check. Recommend / Auto-recommend tiers are exempt.
    HIGH_TIER_PATTERN="(Hard Prerequisite|Pre-DE Prerequisite|Auto-run|Auto-recommend before synthesis)"

    # Extract pipe-table rows that mention a high-tier assignment.
    # Each row format (in §4a / §4b): | <trigger> | <audit name> | <tier> | <reference> |
    # We scan all pipe rows and try to extract audit name + tier + reference.
    HIGH_TIER_ROWS=$(grep -E "^\|" "$PD_FILE" 2>/dev/null | grep -E "$HIGH_TIER_PATTERN" || true)

    if [ -z "$HIGH_TIER_ROWS" ]; then
      echo "OK: No high-tier audit assignments detected in pipe-table rows of ${PD_FILE}."
      exit 0
    fi

    # For each high-tier row, extract audit name and reference path.
    while IFS= read -r row; do
      [ -z "$row" ] && continue
      # Parse pipe-separated cells; trim surrounding whitespace.
      AUDIT_NAME=$(echo "$row" | awk -F'|' '{gsub(/^[ \t]+|[ \t]+$/, "", $3); print $3}')
      REF_CELL=$(echo "$row" | awk -F'|' '{gsub(/^[ \t]+|[ \t]+$/, "", $5); print $5}')
      # Reference path is in backticks like `craft/foo.md` or `audits/foo.md`.
      REF_PATH=$(echo "$REF_CELL" | grep -oE '`[^`]+\.md`' | head -1 | tr -d '`' || true)

      [ -z "$AUDIT_NAME" ] && continue
      [ -z "$REF_PATH" ] && continue

      # Compute slug for override marker matching: lowercase audit name,
      # spaces and slashes to hyphens, strip non-alphanumerics.
      AUDIT_SLUG=$(echo "$AUDIT_NAME" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-//; s/-$//')

      # Per-audit override check: marker in the body of pass-dependencies.
      OV_AUDIT=0
      if grep -F "<!-- override: audit-tier-criterion-${AUDIT_SLUG}" "$PD_FILE" > /dev/null 2>&1; then
        OV_AUDIT=1
      fi

      # Locate the reference file. Try AUDIT_ROOT/REF_PATH; fall back to
      # walking AUDIT_ROOT for any file matching the basename.
      REF_FILE=""
      if [ -f "$AUDIT_ROOT/$REF_PATH" ]; then
        REF_FILE="$AUDIT_ROOT/$REF_PATH"
      else
        BASENAME=$(basename "$REF_PATH")
        FOUND=$(find "$AUDIT_ROOT" -name "$BASENAME" -type f 2>/dev/null | head -1 || true)
        [ -n "$FOUND" ] && REF_FILE="$FOUND"
      fi

      if [ -z "$REF_FILE" ]; then
        echo "WARN: '${AUDIT_NAME}' — reference file '${REF_PATH}' not found under '${AUDIT_ROOT}'; cannot verify criterion 1."
        WARNS=$((WARNS + 1))
        continue
      fi

      # Criterion 1: reference file must mention hard gates OR Must-Fix
      # floor language. Pattern: "hard gate", "Hard Gate", "Must-Fix
      # floor", "Must-Fix-floor".
      if grep -iE "(hard[ -]?gate|must-?fix[ -]?floor)" "$REF_FILE" > /dev/null 2>&1; then
        : # criterion-1 satisfied
      else
        if [ "$OV_AUDIT" -eq 1 ]; then
          echo "WARN: '${AUDIT_NAME}' — reference file '${REF_PATH}' does not document hard gates / Must-Fix floor (criterion 1 unmet); audit-tier-criterion-${AUDIT_SLUG} override marker present."
          WARNS=$((WARNS + 1))
        else
          echo "ERROR: '${AUDIT_NAME}' — reference file '${REF_PATH}' does not document hard gates / Must-Fix floor (criterion 1 unmet for high-tier assignment). Add hard-gate / Must-Fix-floor language to the audit reference, demote the tier, or add <!-- override: audit-tier-criterion-${AUDIT_SLUG} — <rationale> --> in pass-dependencies body."
          ERRORS=$((ERRORS + 1))
        fi
      fi
    done <<< "$HIGH_TIER_ROWS"

    if [ "$ERRORS" -gt 0 ]; then
      echo ""
      echo "FAILED: ${ERRORS} audit-tier-criterion failure(s); ${WARNS} warning(s). Capability ceiling: criterion 1 (hard gates / Must-Fix floor) is mechanically verified; criteria 2 (undetectable-by-passes) and 3 (disclosure-non-equivalence) require model judgment and remain in the §4a/§4b verification subsection prose. Canonical home: core-editor/references/pass-dependencies.md §4c Audit Tier Promotion Criteria."
      exit 1
    else
      echo "OK: All high-tier audit assignments satisfy criterion 1 (named hard gates / Must-Fix floor in reference file) or carry override markers. ${WARNS} warning(s) surfaced. Capability ceiling: criteria 2 + 3 remain prose-verified."
      exit 0
    fi
    ;;

  # ----------------------------------------------------------------------
  # argument-recon-prerequisite <run_folder> [<editorial_letter_file>]
  #
  # Mechanical check that argument-shaped runs satisfy the Field
  # Reconnaissance prerequisite per pass-dependencies.md §4a (Hard
  # Prerequisite or Auto-recommend before synthesis tier) and v1.7.9
  # Hard Prerequisite tier wiring.
  #
  # Behavior: scan the run folder for argument-engine artifacts
  # (Argument_State.md, Red_Team_Memo.md, Argument_Evidence.md, or
  # editorial-letter mentions of Dialectical Clarity / Argument Red
  # Team / Argument Evidence Deep-Dive / argument-engine pass output).
  # If argument-engine artifacts are present, verify that EITHER:
  #   (a) Field_Reconnaissance_Report.md exists in the run folder, OR
  #   (b) the editorial letter records the canonical blind-spot
  #       disclosure per run-synthesis.md §Step 3 (Phase 6 Wave 3 /
  #       CR-4): "literature-counterevidence not surveyed" naming what
  #       is unsurveyed and what the absence implies for synthesis
  #       confidence.
  #
  # If neither (a) nor (b) holds, the validator fails — Hard
  # Prerequisite policy forbids silent omission.
  #
  # Run folders without argument-engine artifacts (fiction runs;
  # narrative-NF runs; non-argument-shaped runs) are exempt and the
  # validator returns OK.
  #
  # Override marker: <!-- override: argument-recon-prerequisite —
  # <rationale> --> in the editorial letter body (e.g., "argument-
  # engine artifacts present pre-date Phase 6 Wave 3 prerequisite
  # policy; back-fill blind-spot disclosure scheduled for next
  # revision round").
  #
  # Self-test: pass --self-test as the only argument to run built-in
  # cases.
  # ----------------------------------------------------------------------
  argument-recon-prerequisite)
    if [ $# -lt 1 ]; then echo "Usage: $0 argument-recon-prerequisite <run_folder> [<editorial_letter_file>] | --self-test"; exit 2; fi

    if [ "$1" = "--self-test" ]; then
      TMPDIR=$(mktemp -d)
      trap 'rm -rf "$TMPDIR"' EXIT

      # Positive case 1: argument-engine artifacts present + Field
      # Reconnaissance report present. Should pass.
      mkdir -p "$TMPDIR/run_pos1"
      touch "$TMPDIR/run_pos1/Argument_State.md"
      touch "$TMPDIR/run_pos1/Field_Reconnaissance_Report.md"
      cat > "$TMPDIR/run_pos1/Editorial_Letter.md" <<'EOF'
# Editorial Letter
## §1 What Needs Work
Must-Fix: warrant gap on §3 claim.
EOF

      # Positive case 2: argument-engine artifacts present + no Field
      # Recon, but editorial letter records canonical blind-spot
      # disclosure. Should pass.
      mkdir -p "$TMPDIR/run_pos2"
      touch "$TMPDIR/run_pos2/Red_Team_Memo.md"
      cat > "$TMPDIR/run_pos2/Editorial_Letter.md" <<'EOF'
# Editorial Letter
## §3 Blind Spot / Absence Inventory
Field Reconnaissance was declined at intake. The synthesis layer records "literature-counterevidence not surveyed" as a confidence-limiting blind spot: competing studies, counter-citations, replication failures, and opposing scholarly positions in the literature were not surfaced. Dialectical Clarity, Argument Red Team, and Argument Evidence Deep-Dive operated against a manuscript-internal claim graph rather than a literature-aware one.
EOF

      # Positive case 3: no argument-engine artifacts (fiction run).
      # Should pass — validator exempt.
      mkdir -p "$TMPDIR/run_pos3"
      cat > "$TMPDIR/run_pos3/Editorial_Letter.md" <<'EOF'
# Editorial Letter
## §1 What Needs Work
Must-Fix: pacing collapse in Chapter 7.
EOF

      # Negative case: argument-engine artifacts present + no Field
      # Recon report + no blind-spot disclosure in editorial letter.
      # Should fail.
      mkdir -p "$TMPDIR/run_neg"
      touch "$TMPDIR/run_neg/Argument_State.md"
      touch "$TMPDIR/run_neg/Red_Team_Memo.md"
      cat > "$TMPDIR/run_neg/Editorial_Letter.md" <<'EOF'
# Editorial Letter
## §1 What Needs Work
Must-Fix: warrant gap on §3 claim.
## §3 Absence Inventory
The pass artifacts are complete; no missing structural elements identified.
EOF

      # Override case: same setup as neg, but with override marker in
      # editorial letter body. Should pass with WARN.
      mkdir -p "$TMPDIR/run_over"
      touch "$TMPDIR/run_over/Argument_State.md"
      cat > "$TMPDIR/run_over/Editorial_Letter.md" <<'EOF'
# Editorial Letter
## §1 What Needs Work
Must-Fix: warrant gap on §3 claim.
<!-- override: argument-recon-prerequisite — Argument-engine artifacts present pre-date Phase 6 Wave 3 prerequisite policy; back-fill blind-spot disclosure scheduled for next revision round. -->
EOF

      RESULTS=0
      "$0" argument-recon-prerequisite "$TMPDIR/run_pos1" >/dev/null 2>&1 && echo "  pos1: OK (argument-engine + Field Recon report)" || { echo "  pos1: FAIL (expected OK)"; RESULTS=1; }
      "$0" argument-recon-prerequisite "$TMPDIR/run_pos2" >/dev/null 2>&1 && echo "  pos2: OK (argument-engine + canonical blind-spot disclosure)" || { echo "  pos2: FAIL (expected OK)"; RESULTS=1; }
      "$0" argument-recon-prerequisite "$TMPDIR/run_pos3" >/dev/null 2>&1 && echo "  pos3: OK (fiction run — no argument-engine artifacts; exempt)" || { echo "  pos3: FAIL (expected OK)"; RESULTS=1; }
      "$0" argument-recon-prerequisite "$TMPDIR/run_neg" >/dev/null 2>&1 && { echo "  neg: FAIL (expected ERROR — argument-engine present, no Field Recon, no disclosure)"; RESULTS=1; } || echo "  neg: OK (caught — silent omission of Hard Prerequisite)"
      "$0" argument-recon-prerequisite "$TMPDIR/run_over" >/dev/null 2>&1 && echo "  over: OK (override marker downgrades ERROR→WARN)" || { echo "  over: FAIL (expected OK after override)"; RESULTS=1; }
      [ "$RESULTS" -eq 0 ] && { echo "Self-test: PASS"; exit 0; } || { echo "Self-test: FAIL"; exit 1; }
    fi

    if [ ! -d "$1" ]; then echo "Error: Run folder not found: $1" >&2; exit 2; fi
    RUN_FOLDER="$1"
    LETTER="${2:-}"

    # Auto-detect editorial letter if not provided: look for
    # *Editorial_Letter*.md or *editorial_letter*.md in run folder.
    if [ -z "$LETTER" ]; then
      LETTER=$(find "$RUN_FOLDER" -maxdepth 2 -type f \( -iname "*editorial_letter*.md" -o -iname "*_de*.md" \) 2>/dev/null | head -1 || true)
    fi

    # Detect argument-engine artifacts by filename pattern.
    ARG_ARTIFACTS=$(find "$RUN_FOLDER" -maxdepth 3 -type f \( -iname "Argument_State*.md" -o -iname "Red_Team_Memo*.md" -o -iname "Argument_Evidence*.md" -o -iname "Argument_Red_Team*.md" -o -iname "Argument_Persuasion*.md" -o -iname "Adversarial_Evidence*.md" \) 2>/dev/null | head -5 || true)

    # Also check editorial letter body for argument-engine pass mentions.
    ARG_LETTER_MENTION=0
    if [ -n "$LETTER" ] && [ -f "$LETTER" ]; then
      if grep -iE "(Dialectical Clarity|Argument Red Team|Argument Evidence Deep-Dive|argument-engine|Argument_State|Claim Ladder)" "$LETTER" > /dev/null 2>&1; then
        ARG_LETTER_MENTION=1
      fi
    fi

    if [ -z "$ARG_ARTIFACTS" ] && [ "$ARG_LETTER_MENTION" -eq 0 ]; then
      echo "OK: No argument-engine artifacts detected in '${RUN_FOLDER}'; Field Reconnaissance prerequisite does not apply (non-argument-shaped run)."
      exit 0
    fi

    # Argument-engine present. Check (a): Field Recon report exists.
    FIELD_RECON=$(find "$RUN_FOLDER" -maxdepth 3 -type f -iname "Field_Reconnaissance_Report*.md" 2>/dev/null | head -1 || true)

    if [ -n "$FIELD_RECON" ]; then
      echo "OK: Argument-engine artifacts detected; Field_Reconnaissance_Report.md present at '${FIELD_RECON}'."
      exit 0
    fi

    # Check (b): canonical blind-spot disclosure in editorial letter.
    DISCLOSURE_OK=0
    if [ -n "$LETTER" ] && [ -f "$LETTER" ]; then
      if grep -iE "literature[- ]counterevidence[- ]not[- ]surveyed" "$LETTER" > /dev/null 2>&1; then
        DISCLOSURE_OK=1
      fi
    fi

    # Override marker check (in editorial letter body, above appendices).
    OV_ARP=0
    if [ -n "$LETTER" ] && [ -f "$LETTER" ]; then
      APPENDIX_LINE=$(grep -niE "^#{1,4}.*Appendix [A-C]" "$LETTER" 2>/dev/null | head -1 | cut -d: -f1 || true)
      if [ -n "$APPENDIX_LINE" ]; then
        BODY=$(sed -n "1,$((APPENDIX_LINE - 1))p" "$LETTER")
      else
        BODY=$(cat "$LETTER")
      fi
      if echo "$BODY" | grep -F "<!-- override: argument-recon-prerequisite" > /dev/null 2>&1; then
        OV_ARP=1
      fi
    fi

    if [ "$DISCLOSURE_OK" -eq 1 ]; then
      echo "OK: Argument-engine artifacts detected; canonical blind-spot disclosure ('literature-counterevidence not surveyed') present in editorial letter."
      exit 0
    fi

    if [ "$OV_ARP" -eq 1 ]; then
      echo "WARN: Argument-engine artifacts detected; no Field_Reconnaissance_Report.md and no canonical blind-spot disclosure found, but override marker present in editorial letter body. Phase 6 Wave 3 / CR-4 Hard Prerequisite policy: this run carries documented exception rationale."
      exit 0
    fi

    echo "ERROR: Argument-engine artifacts detected in '${RUN_FOLDER}' (no Field_Reconnaissance_Report.md present), but the editorial letter does not record the canonical blind-spot disclosure ('literature-counterevidence not surveyed'). Per pass-dependencies.md §4a (Hard Prerequisite) + run-synthesis.md §Step 3 (Phase 6 Wave 3 / CR-4): silent omission is forbidden. Either (a) run Field Reconnaissance and produce Field_Reconnaissance_Report.md, (b) record the canonical blind-spot disclosure in the editorial letter naming what is unsurveyed and what the absence implies for synthesis confidence, or (c) place a body override marker <!-- override: argument-recon-prerequisite — <rationale> --> in the editorial letter."
    exit 1
    ;;

  *)
    echo "Unknown command: $COMMAND"
    usage
    ;;
esac
