# shellcheck shell=bash
# Sourced by ../validate.sh; not runnable on its own.
_PDF_LINK_FLAGS=0
_PDF_LINK_INVALID=0
for _PDF_ARG in "$@"; do
  case "$_PDF_ARG" in
    --internal-links) _PDF_LINK_FLAGS=$((_PDF_LINK_FLAGS + 1)) ;;
    --internal-links*) _PDF_LINK_INVALID=1 ;;
  esac
done
if [ "$_PDF_LINK_FLAGS" -gt 0 ] || [ "$_PDF_LINK_INVALID" -ne 0 ]; then
  if [ "$COMMAND" != "pdf-export" ] || [ "$_PDF_LINK_FLAGS" -ne 1 ] || [ "$_PDF_LINK_INVALID" -ne 0 ] || [ "$#" -ne 2 ]; then
    echo "pdf-export: usage: pdf-export <run_folder> --internal-links (once)"; exit 2
  fi
  for _PDF_ARG in "$@"; do
    case "$_PDF_ARG" in
      --internal-links) ;;
      --*) echo "pdf-export: usage: misplaced navigation option"; exit 2 ;;
    esac
  done
fi
case "$COMMAND" in

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
    # Primary path: real parser in scripts/config_checks.py (Inc.5). Degrades to bash below.
    CFG_DIR=$(cd "$(dirname "$0")" && pwd)
    CFG_HELPER="$CFG_DIR/config_checks.py"

    if [ "$1" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$CFG_HELPER" ]; then python3 "$CFG_HELPER" --self-test audit-tier-criterion; exit $?; fi
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
      # Auto-run definitional case (v1.8.4 canonical-failure analogue):
      # mirrors the Memoir / Narrative-NF pattern surfaced when running
      # against canonical pass-dependencies.md. An Auto-run (definitional)
      # audit at high tier whose reference file documents named gates as
      # a §Hard Gates section header form (header line "## Hard Gates" or
      # bold-paragraph form) plus per-flag (Hard Gate) parenthetical
      # markers — the form Memoir / Series Continuity / Narrative NF /
      # Consent Complexity / AI-Prose now use. Should PASS.
      cat > "$TMPDIR/autorun_pd.md" <<'EOF'
## §4a. Router-triggered audits
| Trigger | Audit | Tier | Reference |
|---|---|---|---|
| Memoir-shape disclosed at intake | Definitional Memoir Audit | Auto-run (bundled) | `audits/definitional-memoir.md` |
EOF
      cat > "$TMPDIR/audits/definitional-memoir.md" <<'EOF'
# Definitional Memoir Audit
## Diagnostic Flags
### Must-Fix Floor — Hard Gates
The two flags below are audit-internal hard gates carrying an audit-internal Must-Fix floor that propagates to synthesis.
**"Memory Fraud"** (Hard Gate) — invented scenes presented as factual.
**"Living Person Harm"** (Hard Gate) — identifiable person damaged without consent.
EOF
      # Finding-triggered §4b high-tier case (v1.8.4): mirrors the
      # canonical Consent Complexity / AI-Prose / Series Continuity §4b
      # rows where the audit appears in §4b at Auto-recommend before
      # synthesis tier. Validator must extract audit name from §4b's
      # different column ordering (| Pass | Trigger | Audit | Policy |
      # vs. §4a's | Trigger | Audit | Tier | Reference |). Note: the §4b
      # column-3 cell holds the audit name and the canonical reference
      # path lives in the §4a row for the same audit. Self-test asserts
      # the validator does not error when §4b rows lack a backtick
      # reference path (which is the canonical pattern).
      cat > "$TMPDIR/findingtrig_pd.md" <<'EOF'
## §4b. Finding-triggered audits
| Pass | Finding pattern | Audit(s) | Policy |
|------|----------------|----------|--------|
| 1 (Reader Experience) | Uniform fluency | AI-Prose Calibration | Auto-recommend before synthesis (if not already loaded) |
EOF
      # Note: §4b row's column 5 is empty (no backtick reference path
      # cell). Validator's REF_PATH extraction returns empty; the row
      # is correctly skipped without erroring. This is canonical
      # behavior — §4a is the source of truth for reference paths.
      RESULTS=0
      "$0" audit-tier-criterion "$TMPDIR/pos_pd.md" "$TMPDIR/audits" >/dev/null 2>&1 && echo "  pos: OK (high-tier audits document hard gates / Must-Fix floors)" || { echo "  pos: FAIL (expected OK)"; RESULTS=1; }
      "$0" audit-tier-criterion "$TMPDIR/neg_pd.md" "$TMPDIR/audits" >/dev/null 2>&1 && { echo "  neg: FAIL (expected ERROR — high-tier audit lacks criterion-1 hard-gate language)"; RESULTS=1; } || echo "  neg: OK (caught — soft audit at Auto-recommend before synthesis tier)"
      "$0" audit-tier-criterion "$TMPDIR/over_pd.md" "$TMPDIR/audits" >/dev/null 2>&1 && echo "  over: OK (override marker downgrades ERROR→WARN)" || { echo "  over: FAIL (expected OK after override)"; RESULTS=1; }
      "$0" audit-tier-criterion "$TMPDIR/edge_pd.md" "$TMPDIR/audits" >/dev/null 2>&1 && echo "  edge: OK (Recommend-tier audit not subject to criterion-1 check)" || { echo "  edge: FAIL (expected OK — Recommend tier exempt)"; RESULTS=1; }
      "$0" audit-tier-criterion "$TMPDIR/autorun_pd.md" "$TMPDIR/audits" >/dev/null 2>&1 && echo "  autorun: OK (v1.8.4: Auto-run definitional audit with §Hard Gates section header + per-flag (Hard Gate) markers)" || { echo "  autorun: FAIL (expected OK — Auto-run definitional with hard-gate section-header form)"; RESULTS=1; }
      "$0" audit-tier-criterion "$TMPDIR/findingtrig_pd.md" "$TMPDIR/audits" >/dev/null 2>&1 && echo "  findingtrig: OK (v1.8.4: §4b finding-triggered row without ref-path cell skipped without error)" || { echo "  findingtrig: FAIL (expected OK — §4b without ref path should not error)"; RESULTS=1; }
      [ "$RESULTS" -eq 0 ] && { echo "Self-test: PASS"; exit 0; } || { echo "Self-test: FAIL"; exit 1; }
    fi

    # Real-file invocation: delegate to the parser when python3 is present.
    if command -v python3 >/dev/null 2>&1 && [ -f "$CFG_HELPER" ]; then
      python3 "$CFG_HELPER" audit-tier-criterion "$@"; exit $?
    fi

    # Degraded path (no python3): bash regex implementation.
    if [ ! -f "$1" ]; then echo "Error: File not found: $1" >&2; exit 2; fi
    PD_FILE="$1"
    AUDIT_ROOT="${2:-}"
    # Default audit root: try the conventional layout if not provided.
    if [ -z "$AUDIT_ROOT" ]; then
      PD_DIR=$(dirname "$PD_FILE")
      # Common layout: pass-dependencies.md is in core-editor/references;
      # audits live across sibling skill reference directories.
      if [ -d "$PD_DIR/../.." ]; then
        AUDIT_ROOT="$PD_DIR/../.."
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
      if _has_override "audit-tier-criterion-${AUDIT_SLUG}" < "$PD_FILE"; then
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
  # pass-header <pass_artifact_file> [<pass_dependencies_file>]
  #
  # A Core DE pass artifact must carry a §3-sourced header:
  #   > **Macro block:** <block> · **Writer question:** <question>
  #   · **Legacy pass id:** Pass <N>
  # The three values are READ from pass-dependencies.md §3 (the single source
  # of truth for the 8 blocks, the pass↔block map, and the User Question),
  # never authored. H1 header present (header-less legacy artifact = WARN, not
  # ERROR); H2 block ∈ 8 AND block matches §3's pass→block map for the Legacy
  # pass id AND Writer question matches §3's User Question; H3 all three fields
  # non-empty. Concern-driven runs declare the pass's OWN canonical §3 block
  # (the map is by pass, not by run).
  #
  # Primary path: scripts/config_checks.py. Degrades to bash when python3 is absent.
  # ----------------------------------------------------------------------
  pass-header)
    # Delegates to scripts/config_checks.py (the SSoT parser for §3 — block ∈ the 8,
    # block↔pass map, block→User Question). Per the fleet NEW-VALIDATOR convention,
    # it degrades to an advisory WARN without python3 — NOT a bash reimplementation
    # of the §3 parse (that duplicate drifts from the parser and, under set -euo
    # pipefail, mis-fires a hard failure on the header-absent WARN path). A header
    # comparison against §3 needs the real parser; there is no faithful bash stand-in.
    PH_DIR=$(cd "$(dirname "$0")" && pwd)
    PH_HELPER="$PH_DIR/config_checks.py"
    if [ "${1:-}" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$PH_HELPER" ]; then python3 "$PH_HELPER" --self-test pass-header; exit $?; fi
      echo "Self-test: PASS (degraded — python3 unavailable; pass-header is advisory without it)"; exit 0
    fi
    if command -v python3 >/dev/null 2>&1 && [ -f "$PH_HELPER" ]; then
      if [ $# -lt 1 ]; then echo "Usage: $0 pass-header <pass_artifact_file> [<pass_dependencies_file>] | --self-test"; exit 2; fi
      python3 "$PH_HELPER" pass-header "$@"; exit $?
    fi
    echo "WARN: python3 unavailable — pass-header skipped; check inline that the header's block/question/pass id agree with pass-dependencies.md §3 (block ∈ the 8, the block↔pass map is by pass not by run, and the Writer question is §3's User Question — never authored). See references/example-pass-artifact-header.md."
    exit 0
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
    # Primary path: real parser in scripts/config_checks.py (Inc.5). Degrades to bash below.
    CFG_DIR=$(cd "$(dirname "$0")" && pwd)
    CFG_HELPER="$CFG_DIR/config_checks.py"

    if [ "$1" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$CFG_HELPER" ]; then python3 "$CFG_HELPER" --self-test argument-recon-prerequisite; exit $?; fi
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

    # Real-folder invocation: delegate to the parser when python3 is present.
    if command -v python3 >/dev/null 2>&1 && [ -f "$CFG_HELPER" ]; then
      python3 "$CFG_HELPER" argument-recon-prerequisite "$@"; exit $?
    fi

    # Degraded path (no python3): bash regex implementation.
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
      if echo "$BODY" | _has_override "argument-recon-prerequisite"; then
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

  structured-findings)
    # Phase 3: validate embedded apodictic:* JSON blocks (in ledger/letter .md)
    # and the Diagnostic_State.meta.json sidecar. Delegates JSON parsing to
    # scripts/structured_findings.py (a real parser). On a host without python3,
    # degrade to a presence check so the block — which stays human-readable —
    # does not hard-block; full validation needs python3 (present on Cowork).
    SF_DIR=$(cd "$(dirname "$0")" && pwd)
    SF_HELPER="$SF_DIR/structured_findings.py"
    if command -v python3 >/dev/null 2>&1 && [ -f "$SF_HELPER" ]; then
      python3 "$SF_HELPER" "$@"
      exit $?
    fi
    # Degraded path (no python3).
    if [ "${1:-}" = "--self-test" ]; then
      SF_TMP=$(mktemp -d); trap 'rm -rf "$SF_TMP"' EXIT
      printf '<!-- apodictic:finding\n{"schema":"apodictic.finding.v1","severity":"Must-Fix"}\n-->\n' > "$SF_TMP/f.md"
      if grep -q 'apodictic:finding' "$SF_TMP/f.md" && grep -q '"schema"' "$SF_TMP/f.md"; then
        echo "Self-test: PASS (degraded — python3 unavailable; presence check only)"; exit 0
      else
        echo "Self-test: FAIL"; exit 1
      fi
    fi
    if [ $# -lt 1 ]; then echo "Usage: $0 structured-findings <file> [<file>...] | --self-test"; exit 2; fi
    SF_WARN=0
    for f in "$@"; do
      if [ ! -f "$f" ]; then echo "Error: File not found: $f" >&2; exit 2; fi
      if grep -q 'apodictic:' "$f" 2>/dev/null; then SF_WARN=1; fi
    done
    if [ "$SF_WARN" -eq 1 ]; then
      echo "WARN: python3 unavailable — presence check only; full JSON validation skipped (blocks remain human-readable). Install python3 for full structured-findings validation."
    else
      echo "structured-findings: PASS (degraded presence check; no structured blocks found)"
    fi
    exit 0
    ;;

  softness-check)
    # Phase 4 (Harden Honesty): compare the delivered letter against the
    # Triage-locked findings (Deficit Lock). Delegates to honesty_check.py;
    # degrades to advisory (WARN, exit 0) without python3 — the Deficit Lock
    # prose rule still applies.
    HC_DIR=$(cd "$(dirname "$0")" && pwd)
    HC_HELPER="$HC_DIR/honesty_check.py"
    if [ "${1:-}" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$HC_HELPER" ]; then python3 "$HC_HELPER" --self-test; exit $?; fi
      echo "Self-test: PASS (degraded — python3 unavailable; softness-check is advisory without it)"; exit 0
    fi
    if command -v python3 >/dev/null 2>&1 && [ -f "$HC_HELPER" ]; then
      if [ $# -lt 2 ]; then echo "Usage: $0 softness-check <editorial_letter> <findings_ledger> | --self-test"; exit 2; fi
      python3 "$HC_HELPER" softness-check "$@"
      exit $?
    fi
    echo "WARN: python3 unavailable — softness-check (delivered-vs-locked severity) skipped; the Deficit Lock prose rule still applies. Install python3 for the mechanical gate."
    exit 0
    ;;

  deficit-lock)
    # Phase 4: verify the Triage Deficit Lock was recorded structurally in the
    # ledger. Delegates to honesty_check.py; degrades to advisory without python3.
    HC_DIR=$(cd "$(dirname "$0")" && pwd)
    HC_HELPER="$HC_DIR/honesty_check.py"
    if [ "${1:-}" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$HC_HELPER" ]; then python3 "$HC_HELPER" --self-test; exit $?; fi
      echo "Self-test: PASS (degraded — python3 unavailable)"; exit 0
    fi
    if command -v python3 >/dev/null 2>&1 && [ -f "$HC_HELPER" ]; then
      if [ $# -lt 1 ]; then echo "Usage: $0 deficit-lock <findings_ledger> | --self-test"; exit 2; fi
      python3 "$HC_HELPER" deficit-lock "$@"
      exit $?
    fi
    echo "WARN: python3 unavailable — deficit-lock (structured-lock presence) skipped."
    exit 0
    ;;

  artifacts-schema)
    # Shared structured-artifact parser/validator (scripts/apodictic_artifacts.py) —
    # the source-of-truth schema engine behind structured-findings / softness-check /
    # deficit-lock. Only --self-test is meaningful here; it gates the shared module
    # in --self-test-all. Delegates to the module; degrades without python3.
    AS_DIR=$(cd "$(dirname "$0")" && pwd)
    AS_HELPER="$AS_DIR/apodictic_artifacts.py"
    if [ "${1:-}" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$AS_HELPER" ]; then python3 "$AS_HELPER" --self-test; exit $?; fi
      echo "Self-test: PASS (degraded — python3 unavailable)"; exit 0
    fi
    echo "Usage: $0 artifacts-schema --self-test"; exit 2
    ;;

  gate)
    # Runner-Governed Execution (increments 1-5): run the execution-gate engine for a
    # phase against a run folder — checks the manifest's required artifacts + mechanical
    # validators, prints the attested checklist, and records the decision as an append-only
    # event in execution.gate_events[]. Subcommands (passed through to run_gate.py):
    #   gate <phase> <run_folder> [--strict-warnings]   mechanical run (-> mechanical-passed
    #                                                    for a gate with attested items)
    #   gate --attest <phase> <run_folder>              re-run checks + record clearing pass
    #   gate --skip/--defer <phase> <run_folder> --reason ...   record an exception
    # Degrades without python3 (model performs the manifest's checks inline and hand-authors
    # the gate_events[] entry — see docs/runner-governed-execution.md §Degradation).
    GT_DIR=$(cd "$(dirname "$0")" && pwd)
    GT_HELPER="$GT_DIR/run_gate.py"
    if [ "${1:-}" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$GT_HELPER" ]; then python3 "$GT_HELPER" --self-test; exit $?; fi
      echo "Self-test: PASS (degraded — python3 unavailable)"; exit 0
    fi
    if command -v python3 >/dev/null 2>&1 && [ -f "$GT_HELPER" ]; then
      if [ $# -lt 2 ]; then echo "Usage: $0 gate <phase> <run_folder> [--strict-warnings] | gate --attest <phase> <run_folder> | gate --skip/--defer <phase> <run_folder> --reason ..."; exit 2; fi
      python3 "$GT_HELPER" "$@"
      exit $?
    fi
    echo "WARN: python3 unavailable — gate engine skipped; perform the phase's manifest checks inline and append the result as an event in the sidecar (execution.gate_events)."
    exit 0
    ;;

  gate-state)
    # Runner-Governed Execution (increment 5): gate-state validator — validate a sidecar's
    # execution.gate_events[] log (structural + the semantic invariants the stdlib subset
    # checker cannot express: attestation coverage, migration-prefix integrity, finding_deltas
    # clearing-only, pointer==fold) and assert pointer==fold. --strict is nonzero while any
    # open exception (non-clearing latest event) remains. Delegates to scripts/run_gate.py
    # --check-state; degrades to advisory without python3.
    GS_DIR=$(cd "$(dirname "$0")" && pwd)
    GS_HELPER="$GS_DIR/run_gate.py"
    if [ "${1:-}" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$GS_HELPER" ]; then python3 "$GS_HELPER" --self-test; exit $?; fi
      echo "Self-test: PASS (degraded — python3 unavailable; gate-state is advisory without it)"; exit 0
    fi
    if command -v python3 >/dev/null 2>&1 && [ -f "$GS_HELPER" ]; then
      if [ $# -lt 1 ]; then echo "Usage: $0 gate-state <Diagnostic_State.meta.json> [--strict]"; exit 2; fi
      python3 "$GS_HELPER" --check-state "$@"
      exit $?
    fi
    echo "WARN: python3 unavailable — gate-state skipped; the gate_events[] contract is documented in docs/runner-governed-execution.md. Install python3 for the mechanical check."
    exit 0
    ;;

  finding-trace)
    # Finding Lifecycle IDs cross-artifact trace (docs/finding-lifecycle-ids.md): referential
    # integrity + sidecar lifecycle coherence by Finding Lifecycle ID — E1 dangling letter
    # reference, E2 phantom sidecar finding_states key, E3 invalid state, E4 dangling revision
    # reference, E5 phantom completion (an in-scope report mentions a `revised` finding but carries
    # no `<!-- resolved: ID -->` marker for it), E6 dangling retcon source (a Retcon Plan retcon_item
    # `source` finding-ref that is not in the ledger — Retcon Planning F3); W1 lifecycle coverage,
    # W2 revision-plan follow-through, W3 completion follow-through (all advisory; ERROR under --strict).
    # Completion keys on the explicit resolved marker, not a bare mention. Complements softness-check
    # (severity fidelity) and structured-findings (intra-ledger ID hygiene) — raises only classes neither owns.
    # Takes a run folder (globs ledger/letter/revisions/retcon-plans, walks up for the sidecar) or explicit files.
    # Delegates to scripts/finding_trace.py; degrades to an advisory WARN without python3.
    FT_DIR=$(cd "$(dirname "$0")" && pwd)
    FT_HELPER="$FT_DIR/finding_trace.py"
    if [ "${1:-}" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$FT_HELPER" ]; then python3 "$FT_HELPER" --self-test; exit $?; fi
      echo "Self-test: PASS (degraded — python3 unavailable; finding-trace is advisory without it)"; exit 0
    fi
    if command -v python3 >/dev/null 2>&1 && [ -f "$FT_HELPER" ]; then
      if [ $# -lt 1 ]; then echo "Usage: $0 finding-trace <run_folder|files...> [--strict] | --self-test"; exit 2; fi
      python3 "$FT_HELPER" finding-trace "$@"; exit $?
    fi
    echo "WARN: python3 unavailable — finding-trace skipped; perform the cross-artifact ID trace inline (every cited F-... ID resolves to a ledger finding; finding_states keys are ledger IDs). See docs/finding-lifecycle-ids.md."
    exit 0
    ;;

  feedback-triage)
    # Feedback Triage workflow integrity (docs/feedback-triage.md): structural checks over the
    # apodictic.feedback_item.v1 blocks in a Feedback Triage artifact — E1 invalid item, E2
    # duplicate id, E3 dangling conflict reference, E4 self conflict, E5 dangling maps_to (a
    # finding-id ref not in the paired ledger; Increment 2), W1 unresolved conflict (both sides
    # still actionable), W2 acting now on an unvalidated claim, W4 unmapped validated (a `validated`
    # item carrying no maps_to; Increment 2). W1/W2/W4 advisory; ERROR under --strict. Owns conflict
    # referential integrity, the "contradiction kept live" coherence gap, and feedback->ledger
    # maps_to referential integrity. Takes a run folder (globs *_Feedback_Triage_*.md plus an
    # optional *_Findings_Ledger_*.md for the maps_to cross-check) or explicit files (triage +
    # optional ledger); without a ledger the maps_to check is skipped. Delegates to
    # scripts/feedback_triage.py; degrades to an advisory WARN without python3.
    FBT_DIR=$(cd "$(dirname "$0")" && pwd)
    FBT_HELPER="$FBT_DIR/feedback_triage.py"
    if [ "${1:-}" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$FBT_HELPER" ]; then python3 "$FBT_HELPER" --self-test; exit $?; fi
      echo "Self-test: PASS (degraded — python3 unavailable; feedback-triage is advisory without it)"; exit 0
    fi
    if command -v python3 >/dev/null 2>&1 && [ -f "$FBT_HELPER" ]; then
      if [ $# -lt 1 ]; then echo "Usage: $0 feedback-triage <run_folder|files...> [--strict] | --self-test"; exit 2; fi
      python3 "$FBT_HELPER" feedback-triage "$@"; exit $?
    fi
    echo "WARN: python3 unavailable — feedback-triage skipped; check inline that every conflicts_with id resolves to a real feedback item and no contradiction is left actionable on both sides. See docs/feedback-triage.md."
    exit 0
    ;;

  retcon-plan)
    # Retcon Planning coaching track (docs/retcon-planning.md): structural checks over the
    # apodictic.retcon_item.v1 blocks in a Retcon Plan — R1 invalid item, R2 duplicate id,
    # R3 evidential retcon of locked canon (fair-play violation; the signature gate), R4 dangling
    # target_id; W1 unaccounted blast radius on a locked/costly item, W2 firewall drift (invented
    # prose where a class belongs). The Door-B Selection step (F1) also checks apodictic.retcon_reading.v1
    # blocks — R5 invalid reading (schema + 1-5 score rubric), R6 duplicate reading id, R7 dangling
    # implied_target; W3 missing coincidence_note (over-fitting guard; the signature F1 check), W4
    # more than 3 candidate readings (top-1-3 shortlist). W1-W4 advisory, ERROR under --strict. Takes
    # a run folder (globs *_Retcon_Plan_*.md) or explicit files. Delegates to scripts/retcon_plan.py;
    # degrades to an advisory WARN without python3.
    RCP_DIR=$(cd "$(dirname "$0")" && pwd)
    RCP_HELPER="$RCP_DIR/retcon_plan.py"
    if [ "${1:-}" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$RCP_HELPER" ]; then python3 "$RCP_HELPER" --self-test; exit $?; fi
      echo "Self-test: PASS (degraded — python3 unavailable; retcon-plan is advisory without it)"; exit 0
    fi
    if command -v python3 >/dev/null 2>&1 && [ -f "$RCP_HELPER" ]; then
      if [ $# -lt 1 ]; then echo "Usage: $0 retcon-plan <run_folder|files...> [--strict] | --self-test"; exit 2; fi
      python3 "$RCP_HELPER" retcon-plan "$@"; exit $?
    fi
    echo "WARN: python3 unavailable — retcon-plan skipped; check inline that no evidential retcon touches locked canon, every target_id/implied_target is declared, intervention classes aren't invented prose, and each candidate reading is scored 1-5 with a coincidence_note. See docs/retcon-planning.md."
    exit 0
    ;;

  state-card-diff)
    # Retcon Planning State Card cross-revision diff (docs/retcon-planning.md, F2): the State Card
    # promoted to a standalone rolling artifact (apodictic.state_card.v1), diff'd across revision
    # rounds (Pass-10-class pattern, modeled on timeline-diff). One file = single-card validate
    # (S1 invalid card / id-prefix, S2 duplicate SE-NN id). Two files = <prior> <current> cross-round
    # diff adding S3 round-backwards, S4 promise->contradiction (the signature transition; override
    # <!-- override: state-card-transition SE-NN — … -->), W1 dropped promise, W2 controlling-idea
    # shift, W3 same-round edit. W1-W3 advisory, ERROR under --strict. Delegates to
    # scripts/state_card_diff.py; degrades to an advisory WARN without python3.
    SCD_DIR=$(cd "$(dirname "$0")" && pwd)
    SCD_HELPER="$SCD_DIR/state_card_diff.py"
    if [ "${1:-}" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$SCD_HELPER" ]; then python3 "$SCD_HELPER" --self-test; exit $?; fi
      echo "Self-test: PASS (degraded — python3 unavailable; state-card-diff is advisory without it)"; exit 0
    fi
    if command -v python3 >/dev/null 2>&1 && [ -f "$SCD_HELPER" ]; then
      if [ $# -lt 1 ]; then echo "Usage: $0 state-card-diff <current> | <prior> <current> [--strict] | --self-test"; exit 2; fi
      python3 "$SCD_HELPER" state-card-diff "$@"; exit $?
    fi
    echo "WARN: python3 unavailable — state-card-diff skipped; check inline that every tracked element carries a unique SE-NN id, no active promise has become a forbidden contradiction across rounds, and a shifted controlling idea is intentional. See docs/retcon-planning.md."
    exit 0
    ;;

  revision-arc)
    # Multi-Session Revision Arc Planning coaching track (docs/multi-session-arc-planning.md): structural
    # checks over the single apodictic.revision_arc.v1 block in a Revision Arc artifact — the phased
    # multi-week strategy (Phase 1 root causes -> Phase 2 consequences -> Phase 3 polish) that sequences
    # the Findings Ledger into per-session Loop Dispatch. HONEST POSTURE (the Retcon pattern: the coach
    # infers, the validator gates the PLAN): the Root-Cause mapping is NOT machine-readable, so this gates
    # the arc's self-consistency + provenance + firewall ONLY — NOT a true causal graph; the coach's
    # dependency reasoning is TRUSTED, not gated. A1 invalid arc (schema + nested phase shape: no empty
    # phases, finding_ref pattern, root_cause subset), A2 provenance closure (every finding_ref resolves to
    # a real Ledger finding), A3 SELF-CONSISTENCY ONLY (each finding in exactly one phase; a Must-Fix
    # finding the arc labels a structural root cause is not parked in the last/polish phase — NOT a causal-
    # structure check), A4 non-empty phase rationale; W1 firewall drift (a rationale that prescribes
    # execution; reuses the retcon-plan heuristics — advisory/best-effort), W2 orphan (a Must-Fix Ledger
    # finding absent from the arc). W1-W2 advisory, ERROR under --strict. Takes a run folder (globs
    # *_Revision_Arc_*.md + the paired *_Findings_Ledger_*.md) or explicit files (arc [ledger]). Delegates
    # to scripts/revision_arc.py; degrades to an advisory WARN without python3.
    RVA_DIR=$(cd "$(dirname "$0")" && pwd)
    RVA_HELPER="$RVA_DIR/revision_arc.py"
    if [ "${1:-}" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$RVA_HELPER" ]; then python3 "$RVA_HELPER" --self-test; exit $?; fi
      echo "Self-test: PASS (degraded — python3 unavailable; revision-arc is advisory without it)"; exit 0
    fi
    if command -v python3 >/dev/null 2>&1 && [ -f "$RVA_HELPER" ]; then
      if [ $# -lt 1 ]; then echo "Usage: $0 revision-arc <run_folder|files...> [--strict] | --self-test"; exit 2; fi
      python3 "$RVA_HELPER" revision-arc "$@"; exit $?
    fi
    echo "WARN: python3 unavailable — revision-arc skipped; check inline that every finding_ref resolves to a ledger finding, each finding sits in exactly one phase, no Must-Fix structural root cause is parked in the polish phase, every phase has a sequencing (not execution-prescribing) rationale, and no Must-Fix finding is left out of the arc. See docs/multi-session-arc-planning.md."
    exit 0
    ;;

  regression-diff)
    # Draft-over-Draft Structural Regression Testing (docs/draft-regression-testing.md): the cross-round
    # Findings-Ledger diff — did this revision resolve what it claimed, and did it break anything that was
    # working? Finding IDs are per-run (renumbered each round), so cross-round identity is a DETERMINISTIC
    # heuristic match (same origin code + equal chapter token + >=1 shared mechanism token; greedy stable
    # one-to-one) and every regression signal is a CANDIDATE for editor judgment. R1 round-linkage (ERROR:
    # both ledgers parse, non-empty, distinct rounds); W1 recurrence-candidate (a resolved/'revised' prior
    # finding matched in round N), W2 new-in-quiet-chapter (a current finding in a chapter quiet on the prior
    # record; override <!-- override: regression-cleared <runlabel>:<chapter> — … -->), W3 unexplained-drop.
    # W1-W3 advisory, ERROR under --strict. Prints to stdout (the diff-validator precedent — persists no
    # file); the Regression Report is orchestrator-written at round-close. Delegates to
    # scripts/regression_diff.py; degrades to an advisory WARN without python3.
    RGD_DIR=$(cd "$(dirname "$0")" && pwd)
    RGD_HELPER="$RGD_DIR/regression_diff.py"
    if [ "${1:-}" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$RGD_HELPER" ]; then python3 "$RGD_HELPER" --self-test; exit $?; fi
      echo "Self-test: PASS (degraded — python3 unavailable; regression-diff is advisory without it)"; exit 0
    fi
    if command -v python3 >/dev/null 2>&1 && [ -f "$RGD_HELPER" ]; then
      if [ $# -lt 1 ]; then echo "Usage: $0 regression-diff <prior_run_folder> <this_run_folder> [--strict] | <run_folder> | --self-test"; exit 2; fi
      python3 "$RGD_HELPER" regression-diff "$@"; exit $?
    fi
    echo "WARN: python3 unavailable — regression-diff skipped; check inline whether any finding the prior round marked resolved recurs (same origin/chapter/mechanism), and whether a chapter quiet on the prior record now carries findings. See docs/draft-regression-testing.md."
    exit 0
    ;;

  reanchor)
    # Annotated-Manuscript round-trip re-anchoring (docs/annotated-manuscript-reanchoring.md): carry
    # draft N's margin annotations onto a REVISED draft (N+1). Re-resolves each anchor against N+1's
    # snapshot by PURE TEXT SEARCH (the A6 identity reused; the quote offset is recomputed against N+1,
    # never carried forward) and classifies held / moved / vanished / ambiguous / not-re-anchorable.
    # RA1 re-anchor integrity (ERROR: the re-anchored manifest passes the structural A-gate — A1+A2+A3+
    # A4-multiset+A6 — against N+1; ledger arms inert, there is no re-diagnosed N+1 ledger); RA2 comment
    # fidelity (ERROR: comments carried byte-identical, never re-authored); RA3 partition completeness
    # (ERROR: every draft-N annotation in exactly one class). W1 candidate-resolved (a vanished anchor),
    # W2 re-anchor refused (ambiguous / line-range) — advisory, ERROR under --strict. Prints to stdout
    # (the diff-validator precedent). Delegates to scripts/reanchor.py; degrades to advisory WARN
    # without python3.
    RAN_DIR=$(cd "$(dirname "$0")" && pwd)
    RAN_HELPER="$RAN_DIR/reanchor.py"
    if [ "${1:-}" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$RAN_HELPER" ]; then python3 "$RAN_HELPER" --self-test; exit $?; fi
      echo "Self-test: PASS (degraded — python3 unavailable; reanchor is advisory without it)"; exit 0
    fi
    if command -v python3 >/dev/null 2>&1 && [ -f "$RAN_HELPER" ]; then
      if [ $# -lt 1 ]; then echo "Usage: $0 reanchor <prior_run_folder> <new_snapshot> [--strict] | --self-test"; exit 2; fi
      python3 "$RAN_HELPER" reanchor "$@"; exit $?
    fi
    echo "WARN: python3 unavailable — reanchor skipped; check inline that each draft-N margin note's anchored text still occurs verbatim+unique in the revised draft (held/moved), is gone (candidate-resolved), or is duplicated/line-range (refused). See docs/annotated-manuscript-reanchoring.md."
    exit 0
    ;;

  roundtrip-disposition)
    # Round-trip disposition record gate (the `/start` round-trip resume round-close;
    # docs/annotated-manuscript-reanchoring.md Increment 3): validate the operator disposition record
    # `[Project]_Roundtrip_Disposition_[runlabel].md` in <this_run_folder> against a LIVE recompute of
    # the anchor classes (reanchor's RA3 partition) and the crossref classes (regression_diff) — the
    # model proposes, the operator disposes, and this gate proves the record never asserts evidence
    # the recompute doesn't support. RT1 recompute alignment (ERROR: every row's finding_id is in the
    # prior manifest's partition, its anchor=/regression= classes equal the recomputed ones, the
    # `compares:` header names the actual runlabels); RT2 confirmation record present (ERROR: any
    # decided row requires the file-level disposition-confirmed token — this proves the RECORD of
    # confirmation exists and is consistent, never that a human confirmed; the human layer is rev-a4
    # at `gate --attest`); RT3 confirmed-writes-only (ERROR: a resolved marker in the folder's
    # Revision Report(s) for an annotated finding without a decision=confirm-resolved row is the
    # vanished-anchor auto-close this gate exists to prevent). RT4 partition coverage (WARN; ERROR
    # --strict: every finding id in the recomputed partition has a disposition row — a record that
    # exists is a round-close record, so a missing row is a finding silently omitted from round-close
    # review, reported by id). W1 unadjudicated/staged — advisory,
    # ERROR under --strict. Absent record -> PASS no-op (safe anywhere). Delegates to
    # scripts/reanchor.py disposition; degrades to advisory WARN without python3 (coherent: no
    # disposition record can have been produced on such a host).
    RTD_DIR=$(cd "$(dirname "$0")" && pwd)
    RTD_HELPER="$RTD_DIR/reanchor.py"
    if [ "${1:-}" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$RTD_HELPER" ]; then python3 "$RTD_HELPER" --self-test; exit $?; fi
      echo "Self-test: PASS (degraded — python3 unavailable; roundtrip-disposition is advisory without it)"; exit 0
    fi
    if command -v python3 >/dev/null 2>&1 && [ -f "$RTD_HELPER" ]; then
      if [ $# -lt 3 ]; then echo "Usage: $0 roundtrip-disposition <prior_run_folder> <new_snapshot> <this_run_folder> [--strict] | --self-test"; exit 2; fi
      python3 "$RTD_HELPER" disposition "$@"; exit $?
    fi
    echo "WARN: python3 unavailable — roundtrip-disposition skipped; check inline that every disposition row's classes match a fresh reanchor/crossref run, that decided rows carry the disposition-confirmed token, that every resolved marker in the Revision Report has a confirm-resolved disposition row, and that every prior annotated finding has a disposition row (none omitted). See docs/annotated-manuscript-reanchoring.md."
    exit 0
    ;;

  disposition-check)
    # Engine-level finding-disposition integrity (docs/finding-dispositions.md): the declined/
    # deferred OVERLAY on the finding lifecycle — execution.finding_dispositions records mirroring
    # the pinned `<!-- declined: F-… — reason -->` / `<!-- deferred: F-… until: trigger — reason -->`
    # markers (grammar SSoT: apodictic_artifacts.parse_disposition_markers). DP0 record shape
    # (schema + trigger-iff-deferred + non-empty reason); DP1 declined/deferred-Must-Fix caveat —
    # an active set-aside Must-Fix must be NAMED on the readiness assessment's pinned caveat
    # line(s) or the verdict is absorbing it (the /ready workflow runs this BEFORE delivering a
    # verdict; a DP1 ERROR blocks it); DP2 no-laundering — same-run resolved+declined
    # contradiction, phantom map key, ledger<->calibration severity mismatch, triage_summary
    # decrement below the ledger tally, and the bidirectional marker/sidecar sync (WARN; ERROR
    # under --strict; governed marker-lag exempt). Artifact-side audit; the log-side twin for
    # governed projects lives in gate-state (run_gate.py --check-state disposition_deltas checks).
    # Takes a run folder, the project sidecar (+ optional readiness assessment), or explicit
    # files. Delegates to scripts/disposition_check.py; degrades to an advisory WARN without
    # python3 (the finding-trace posture — never a false failure).
    DPC_DIR=$(cd "$(dirname "$0")" && pwd)
    DPC_HELPER="$DPC_DIR/disposition_check.py"
    if [ "${1:-}" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$DPC_HELPER" ]; then python3 "$DPC_HELPER" --self-test; exit $?; fi
      echo "Self-test: PASS (degraded — python3 unavailable; disposition-check is advisory without it)"; exit 0
    fi
    if command -v python3 >/dev/null 2>&1 && [ -f "$DPC_HELPER" ]; then
      if [ $# -lt 1 ]; then echo "Usage: $0 disposition-check <run_folder|sidecar> [readiness_assessment] [--strict] | --self-test"; exit 2; fi
      python3 "$DPC_HELPER" disposition-check "$@"; exit $?
    fi
    echo "WARN: python3 unavailable — disposition-check skipped; verify inline that every finding_dispositions record is schema-shaped (trigger iff deferred, non-empty reason), that every ACTIVE declined/deferred Must-Fix is named on the readiness assessment's '**Declined/Deferred Must-Fixes:**' caveat line(s), and that markers and sidecar records agree. See docs/finding-dispositions.md."
    exit 0
    ;;

  synthesis-coverage)
    # Synthesis coverage disclosure gate (docs/synthesis-regrounding.md, M1): a run that wrote a
    # full editorial letter (*_Core_DE_Synthesis_* / *_Full_DE_Synthesis_*) must disclose what the
    # synthesis step could actually see. The disclosure is computed FROM the artifact-read manifest
    # ([Project]_Synthesis_Read_Manifest_[runlabel].md, written BEFORE the letter — run-synthesis.md
    # §Processing Protocol step 9b), and the manifest's denominator is enumerated FROM DISK
    # (run-folder globs) — never from the letter's own prose. V1 presence (manifest, exact name — a
    # *_Manifest_Draft_* lookalike does not count; the Appendix C `### Synthesis Coverage`
    # subsection; the `<!-- coverage: ok|degraded -->` title-block marker; the sidecar
    # synthesis_coverage object). V2 completeness (disk<->manifest row bijection — the manifest can
    # neither shrink nor pad the denominator). V3 reconciliation (the note table + sidecar tallies
    # are exact projections of the manifest; coverage == the letter marker; one marker, one place).
    # V4 provenance/mode agreement (sequential/hybrid/swarm => dispatch-derived, `declared` FAILS —
    # the cheap lie is blocked; single-agent => declared + the pinned not-platform-verified sentence
    # verbatim). V5 degrade disclosure (ok|degraded RECOMPUTED from the D1-D4 truth table — absent
    # artifact rows, uncovered synthesis-bound findings, >60% single-agent context utilization,
    # zero excerpts under a Must-Fix — masking fails louder than degrading; normal multi-agent
    # outline-mediated coverage is NOT degraded). No override markers exist for any check —
    # disclosure is not overridable; the only escape is fixing the manifest. LAUNCH POSTURE
    # (operator call folded 2026-07-01, spec §Open questions #1): V2/V3/V4 fiction-checks are
    # BLOCKING day one (exit 1); V1/V5 — and so the overall gate — are ADVISORY-FIRST for one
    # release (print WARN at exit 0, the escalation-check posture; the run_spot_check gate records
    # pass-with-warn); --strict promotes V1/V5 to ERROR. Nothing in the manifest or sidecar ever
    # drives a filesystem read/write — row ids and paths are compared as strings against this
    # validator's own enumeration. Delegates to scripts/synthesis_coverage.py; degrades to an
    # advisory WARN without python3.
    SCV_DIR=$(cd "$(dirname "$0")" && pwd)
    SCV_HELPER="$SCV_DIR/synthesis_coverage.py"
    if [ "${1:-}" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$SCV_HELPER" ]; then python3 "$SCV_HELPER" --self-test; exit $?; fi
      echo "Self-test: PASS (degraded — python3 unavailable; synthesis-coverage is advisory without it)"; exit 0
    fi
    if command -v python3 >/dev/null 2>&1 && [ -f "$SCV_HELPER" ]; then
      if [ $# -lt 1 ]; then echo "Usage: $0 synthesis-coverage <run_folder> [--strict] | --self-test"; exit 2; fi
      python3 "$SCV_HELPER" synthesis-coverage "$@"; exit $?
    fi
    echo "WARN: python3 unavailable — synthesis-coverage skipped; verify inline that the Synthesis Read Manifest exists and covers every on-disk pass artifact / Findings Ledger / Contract / audit file with a closed-enum status, that the letter's Appendix C 'Synthesis Coverage' note and the sidecar synthesis_coverage object are exact projections of the manifest, that provenance matches the execution mode (multi-agent => dispatch-derived), and that the <!-- coverage: ok|degraded --> title-block marker matches the recomputed D1-D4 degrade state. See docs/synthesis-regrounding.md."
    exit 0
    ;;

  specificity-floor)
    # Pre-Letter Re-Grounding fidelity gate (docs/synthesis-regrounding.md, M2): the Pre-Letter
    # Re-Grounding step (run-synthesis.md §Processing Protocol, after the step-9b Synthesis
    # Coverage Manifest, before the Step 10 pre-output gate) re-reads the consolidated Findings
    # Ledger verbatim and restores the counts / names / quote anchors that context-salience decay
    # smears into vague prose ("nine belief failures" -> "several belief failures"). This validator
    # is the checkable half: it holds the delivered letter to the specificity the ledger locked.
    # COUNT FLOOR (blocking): for each finding cited in the letter (its `<!-- finding: F-... -->`
    # prose block), if the finding's ledger entry (Notable-Finding sentence + structured block)
    # carries a count (integer 2-99; number-words two..ninety-nine NORMALIZE to digit strings,
    # case-insensitively, so a ledger "nine" and a letter "9" are the same token in both
    # directions) and the delivered window uses a vague quantifier (VAGUE_QUANTIFIERS, pinned in
    # specificity_floor.py) with NONE of the ledger's counts, FAIL. Evidence-locator numbers
    # (Ch 12, sc./scenes 30-31, a spelled-out "Chapter Nine") are stripped, never counted; an
    # all-malformed ledger (finding blocks present, ZERO parse) REFUSES with a named error
    # (malformed-ledger refusal) instead of a vacuous pass.
    # ANCHOR FLOOR (blocking): each delivered Must-Fix window must carry an evidence
    # reference matching the finding's locked evidence_refs, so a restored number rides a
    # ledger-matching anchor (bounds count-hallucination). Both overridable per-ID with
    # `<!-- override: specificity-floor F-... — <why> -->` + an Appendix B entry (non-countable
    # findings). The `<!-- regrounding: done -->` marker presence is an ADVISORY WARN (--strict
    # promotes). The reverse-direction letter-ID-must-exist-in-ledger check is NOT here — it is
    # finding-trace E1's (spec §M2.3, single ownership); the smuggled-finding gate is
    # `validate.sh finding-trace`. Firewall: re-grounding may only ADD specificity — this validator
    # reads severity only to CLASSIFY (synthesis-bound / Must-Fix), never emits or rewrites it.
    # Delegates to scripts/specificity_floor.py; degrades to an advisory WARN without python3.
    SPF_DIR=$(cd "$(dirname "$0")" && pwd)
    SPF_HELPER="$SPF_DIR/specificity_floor.py"
    if [ "${1:-}" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$SPF_HELPER" ]; then python3 "$SPF_HELPER" --self-test; exit $?; fi
      echo "Self-test: PASS (degraded — python3 unavailable; specificity-floor is advisory without it)"; exit 0
    fi
    if command -v python3 >/dev/null 2>&1 && [ -f "$SPF_HELPER" ]; then
      if [ $# -lt 2 ]; then echo "Usage: $0 specificity-floor <editorial_letter> <findings_ledger> [--strict] | --self-test"; exit 2; fi
      python3 "$SPF_HELPER" specificity-floor "$@"; exit $?
    fi
    echo "WARN: python3 unavailable — specificity-floor skipped; verify inline that every delivered finding's count survived from the ledger (a ledger 'nine belief failures' must not read 'several belief failures' in the letter without an ID-scoped <!-- override: specificity-floor F-... --> + Appendix B), and that each Must-Fix window carries an evidence reference matching the finding's locked evidence_refs. The smuggled-finding check is finding-trace's, not this one. See docs/synthesis-regrounding.md."
    exit 0
    ;;

  refutation-coverage)
    # Finding disconfirmation V1 (docs/finding-disconfirmation.md §8): no HIGH without
    # survived refutation. Every synthesis-bound ledger finding at confidence HIGH needs an
    # apodictic.refutation.v1 record with attempted:true + outcome survived — or a letter-BODY
    # cap-bound disclosure marker <!-- refutation: not-attempted-budget F-… -->, honored ONLY
    # when the RECOMPUTED budget actually binds (eligible recomputed from the ledger > the
    # spec cap 15) under a bound:true budget for an unprocessed id (a marker on a processed
    # finding, under an unbound budget, or under a bound:true the recompute does not
    # corroborate, is an ERROR — the marker is a disclosure, not an exemption). The budget
    # block is the pass's self-report: eligible/bound/cap recompute against the ledger and
    # the §5 spec constant, mismatch = blocking ERROR (recompute, don't trust — Codex P1,
    # PR #161).
    # Every Must-Fix needs a record with attempted:true (the cap of 15 can never bind on
    # Must-Fix: their ceiling is 10 — a missing Must-Fix record is a silent skip). Every
    # record id must resolve to a locked ledger finding (dangling = ERROR). Findings carrying
    # a declined/deferred disposition marker are exempt (the author already ruled — spec §5).
    # Runs at Step 10 alongside deficit-lock/softness-check and in the run_spot_check gate.
    # Delegates to scripts/refutation_check.py; degrades to advisory (WARN, exit 0) without
    # python3 — the Step 6b prose contract still applies.
    RFC_DIR=$(cd "$(dirname "$0")" && pwd)
    RFC_HELPER="$RFC_DIR/refutation_check.py"
    if [ "${1:-}" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$RFC_HELPER" ]; then python3 "$RFC_HELPER" --self-test; exit $?; fi
      echo "Self-test: PASS (degraded — python3 unavailable; refutation-coverage is advisory without it)"; exit 0
    fi
    if command -v python3 >/dev/null 2>&1 && [ -f "$RFC_HELPER" ]; then
      if [ $# -lt 3 ]; then echo "Usage: $0 refutation-coverage <editorial_letter> <findings_ledger> <refutation_record> | --self-test"; exit 2; fi
      python3 "$RFC_HELPER" refutation-coverage "$@"; exit $?
    fi
    echo "WARN: python3 unavailable — refutation-coverage skipped; verify inline that every synthesis-bound HIGH finding has a survived apodictic.refutation.v1 record (or a cap-bound disclosure marker honored only when the budget RECOMPUTED from the ledger actually binds — bound:true is a claim to verify, never an input), every Must-Fix has an attempted record, and every record id resolves to a locked ledger finding. See docs/finding-disconfirmation.md."
    exit 0
    ;;

  refutation-evidence)
    # Finding disconfirmation V2 (docs/finding-disconfirmation.md §8): attempts without
    # quote-anchored counter-evidence don't count. counter_evidence_quotes /
    # alternative_explanations at minItems 1; each quote VERBATIM in the intake manuscript
    # snapshot (as-is bytes) and single-line — verbatim-presence only, count >= 1 (A6's
    # uniqueness/offsets deliberately dropped: a counter-evidence quote is evidence, not an
    # anchor); a fabricated quote is an ERROR (the anti-rubber-stamp tooth). Quote > 25 words
    # -> WARN; ungrounded alternative_explanations (no quote mark / Ch.-p. locator / contract
    # ref) -> WARN. The snapshot is REQUIRED (missing = ERROR) under --require-snapshot or
    # when the record's folder holds a *_Core_DE_Synthesis_*/*_Full_DE_Synthesis_* letter
    # (the annotated-manuscript offer's run-shape detection — pass the flag from Step 10 on
    # core-de/full-de runs); elsewhere missing = WARN and every demotion in the record is
    # VOID (weakened/refuted may not be transcribed; the letter must disclose). Each record's
    # snapshot_path/snapshot_sha256 must match the on-disk snapshot (as-is bytes, hashed) —
    # mismatch = ERROR. snapshot_path is model-written and READ-ONLY: resolved beside the
    # record, contained to that folder (realpath); absolute/escaping paths refused by name.
    # Budget arithmetic: processed == min(eligible, cap), bound == (eligible > processed),
    # cap == the §5 spec constant 15, and processed == the count of schema-valid refutation
    # blocks in the record — all blocking ERRORs (the processed/count cross-check was
    # promoted from WARN per the Codex P1 on PR #161: the budget block is a self-report).
    # Delegates to scripts/refutation_check.py; degrades to advisory WARN without python3.
    RFE_DIR=$(cd "$(dirname "$0")" && pwd)
    RFE_HELPER="$RFE_DIR/refutation_check.py"
    if [ "${1:-}" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$RFE_HELPER" ]; then python3 "$RFE_HELPER" --self-test; exit $?; fi
      echo "Self-test: PASS (degraded — python3 unavailable; refutation-evidence is advisory without it)"; exit 0
    fi
    if command -v python3 >/dev/null 2>&1 && [ -f "$RFE_HELPER" ]; then
      if [ $# -lt 1 ]; then echo "Usage: $0 refutation-evidence <refutation_record> [<manuscript_snapshot>] [--require-snapshot] | --self-test"; exit 2; fi
      python3 "$RFE_HELPER" refutation-evidence "$@"; exit $?
    fi
    echo "WARN: python3 unavailable — refutation-evidence skipped; verify inline that every counter-evidence quote occurs verbatim (single-line) in the intake snapshot, snapshot_sha256 matches the on-disk bytes, the budget arithmetic holds (cap is the spec constant 15; processed must equal the actual refutation-block count), and no demotion rides unverified quotes. See docs/finding-disconfirmation.md."
    exit 0
    ;;

  refutation-write-scope)
    # Finding disconfirmation V3 (docs/finding-disconfirmation.md §8): the pass may write
    # only refutation.* + confidence — any severity write fails the run. A severity key at
    # any depth, or a canonical severity token used as a field value, inside a
    # refutation/budget block is an ERROR (the schema omits the property; this arm enforces
    # it against the subset checker's unknown-key tolerance). For every processed id: ledger
    # confidence == record confidence_after, per the outcome caps (survived = unchanged and
    # never confidence-raising; weakened capped at MEDIUM; refuted = LOW/UNCERTAIN); the
    # equality assertion is skipped for records V2 voided for a missing snapshot (re-derived
    # from the record's snapshot_path beside the record). A pre-delivery fail-the-run gate,
    # not write prevention — the deficit-lock/softness-check posture; the letter-side
    # severity floor stays owned by deficit-lock + softness-check (no duplication).
    # Delegates to scripts/refutation_check.py; degrades to advisory WARN without python3.
    RFW_DIR=$(cd "$(dirname "$0")" && pwd)
    RFW_HELPER="$RFW_DIR/refutation_check.py"
    if [ "${1:-}" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$RFW_HELPER" ]; then python3 "$RFW_HELPER" --self-test; exit $?; fi
      echo "Self-test: PASS (degraded — python3 unavailable; refutation-write-scope is advisory without it)"; exit 0
    fi
    if command -v python3 >/dev/null 2>&1 && [ -f "$RFW_HELPER" ]; then
      if [ $# -lt 2 ]; then echo "Usage: $0 refutation-write-scope <findings_ledger> <refutation_record> | --self-test"; exit 2; fi
      python3 "$RFW_HELPER" refutation-write-scope "$@"; exit $?
    fi
    echo "WARN: python3 unavailable — refutation-write-scope skipped; verify inline that no refutation block carries a severity channel and that each processed finding's ledger confidence equals the record's confidence_after per the outcome caps table. See docs/finding-disconfirmation.md."
    exit 0
    ;;

  obsidian-export)
    # Annotated-Manuscript Obsidian export (docs/annotated-manuscript-export.md): project the gated
    # annotation manifest + snapshot into Obsidian-NATIVE Markdown (no plugin) — each finding becomes a
    # footnote [^<finding_id>] at its anchor locus whose definition carries the VERBATIM manifest comment
    # (Obsidian renders footnotes natively; CriticMarkup needs a plugin). A pure projection: the reverse
    # transform (strip the manifest-keyed [^id] refs + the trailing [^id]: block) reproduces the snapshot
    # byte-for-byte. O1 round-trip (ERROR, two-sided precondition), O2 footnote resolution (ERROR:
    # ref<->definition bijection == manifest id set), O3 comment fidelity (ERROR: definition == verbatim
    # comment). `obsidian <run_folder>` writes obsidian/<copy>; `obsidian-export <run_folder>` validates.
    # Delegates to scripts/annotation_export.py; degrades to an advisory WARN without python3.
    OBE_DIR=$(cd "$(dirname "$0")" && pwd)
    OBE_HELPER="$OBE_DIR/annotation_export.py"
    if [ "${1:-}" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$OBE_HELPER" ]; then python3 "$OBE_HELPER" --self-test; exit $?; fi
      echo "Self-test: PASS (degraded — python3 unavailable; obsidian-export is advisory without it)"; exit 0
    fi
    if command -v python3 >/dev/null 2>&1 && [ -f "$OBE_HELPER" ]; then
      if [ $# -lt 1 ]; then echo "Usage: $0 obsidian-export <run_folder> | (generate) $0 ... via annotation_export.py obsidian <run_folder>"; exit 2; fi
      python3 "$OBE_HELPER" obsidian-export "$@"; exit $?
    fi
    echo "WARN: python3 unavailable — obsidian-export skipped; check inline that each finding renders as a [^<finding_id>] footnote whose definition is the verbatim manifest comment, and that stripping the refs + definition block reproduces the snapshot. See docs/annotated-manuscript-export.md."
    exit 0
    ;;

  html-export)
    # Annotated-Manuscript read-only HTML export (docs/annotated-manuscript-export.md, Increment 3):
    # project the gated manifest + snapshot into a self-contained .html (faithful <pre>, escaped, with
    # <sup> footnote-style markers at each anchor + a findings section with bidirectional anchor links;
    # embedded CSS, no network). A pure projection: the reverse transform (strip the manifest-keyed
    # <sup id="ref-…"> markers + the exact 3-entity HTML-unescape) reproduces the snapshot byte-for-byte.
    # H1 round-trip (ERROR), H2 anchor resolution (ERROR: <sup>↔<li> bijection == manifest id set),
    # H3 comment fidelity (ERROR: <li> == escaped verbatim comment + exact back-ref). `html <run_folder>`
    # writes html/<copy>.html; `html-export <run_folder>` validates the on-disk artifact. Delegates to
    # scripts/annotation_export.py; degrades to an advisory WARN without python3.
    HXE_DIR=$(cd "$(dirname "$0")" && pwd)
    HXE_HELPER="$HXE_DIR/annotation_export.py"
    if [ "${1:-}" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$HXE_HELPER" ]; then python3 "$HXE_HELPER" --self-test; exit $?; fi
      echo "Self-test: PASS (degraded — python3 unavailable; html-export is advisory without it)"; exit 0
    fi
    if command -v python3 >/dev/null 2>&1 && [ -f "$HXE_HELPER" ]; then
      if [ $# -lt 1 ]; then echo "Usage: $0 html-export <run_folder> | (generate) via annotation_export.py html <run_folder>"; exit 2; fi
      python3 "$HXE_HELPER" html-export "$@"; exit $?
    fi
    echo "WARN: python3 unavailable — html-export skipped; check inline that the <pre> is the escaped snapshot with manifest-keyed <sup> markers, the findings <li> are verbatim comments, and stripping the markers + unescaping reproduces the snapshot. See docs/annotated-manuscript-export.md."
    exit 0
    ;;

  docx-export)
    # Annotated-Manuscript DOCX export (docs/annotated-manuscript-export.md, Increment 4): project the
    # gated manifest + snapshot into a .docx (OOXML zip) where each finding's manuscript span is wrapped
    # as an anchored Word comment (commentRangeStart/End + commentReference + comments.xml) — so Google
    # Docs imports it as a native ANCHORED comment. A pure projection (verbatim snapshot text +
    # verbatim comments, fixed OOXML boilerplate); the zip is byte-deterministic (ZIP_STORED, pinned
    # ZipInfo). D1 artifact integrity (ERROR: on-disk == fresh build byte-for-byte — the authoritative
    # lock for a binary), D2 text round-trip (ERROR: document.xml <w:t> -> snapshot), D3 comment
    # resolution + fidelity (ERROR: range/reference <-> comment bijection == manifest set; each comment
    # verbatim). `docx <run_folder>` writes docx/<copy>.docx; `docx-export <run_folder>` validates.
    # Delegates to scripts/annotation_export.py; degrades to an advisory WARN without python3.
    DXE_DIR=$(cd "$(dirname "$0")" && pwd)
    DXE_HELPER="$DXE_DIR/annotation_export.py"
    if [ "${1:-}" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$DXE_HELPER" ]; then python3 "$DXE_HELPER" --self-test; exit $?; fi
      echo "Self-test: PASS (degraded — python3 unavailable; docx-export is advisory without it)"; exit 0
    fi
    if command -v python3 >/dev/null 2>&1 && [ -f "$DXE_HELPER" ]; then
      if [ $# -lt 1 ]; then echo "Usage: $0 docx-export <run_folder> | (generate) via annotation_export.py docx <run_folder>"; exit 2; fi
      python3 "$DXE_HELPER" docx-export "$@"; exit $?
    fi
    echo "WARN: python3 unavailable — docx-export skipped; check inline that document.xml is the snapshot text in <w:p>/<w:t> with each finding's span wrapped commentRangeStart/End + commentReference, and comments.xml carries the verbatim comments. See docs/annotated-manuscript-export.md."
    exit 0
    ;;

  pdf-export)
    # Annotated-Manuscript PDF export (docs/annotated-manuscript-export.md, Increment 5): project the
    # gated manifest + snapshot into a self-contained .pdf hand-written from raw PDF objects (header,
    # body, xref, trailer — NO external libs). The snapshot prose renders as base-14 Helvetica text; each
    # finding drops an inline [<finding_id>] marker at its anchor locus (the HTML <sup> precedent) and its
    # verbatim comment lands in a trailing Findings section. A pure projection; the PDF is byte-
    # deterministic (no /Info, no dates, no /ID, no compression, octal-escaped ASCII text). P1 artifact
    # integrity (ERROR: on-disk == fresh build byte-for-byte — the authoritative lock for a binary), P2
    # text round-trip (ERROR: the manuscript text runs, markers stripped, -> snapshot), P3 marker
    # resolution + comment fidelity (ERROR: markers <-> comments bijection == manifest set; each comment
    # verbatim). `pdf <run_folder>` writes pdf/<copy>.pdf; `pdf-export <run_folder>` validates.
    # Delegates to scripts/annotation_export.py; degrades to an advisory WARN without python3.
    PXE_DIR=$(cd "$(dirname "$0")" && pwd)
    PXE_HELPER="$PXE_DIR/annotation_export.py"
    if [ "$_PDF_LINK_FLAGS" -eq 1 ] && { ! command -v python3 >/dev/null 2>&1 || [ ! -f "$PXE_HELPER" ]; }; then
      echo "pdf-export: N navigation validation unavailable (Python/helper missing)"; exit 2
    fi
    if [ "${1:-}" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$PXE_HELPER" ]; then
        python3 "$PXE_HELPER" --self-test || exit $?
        # Repository canonical gate also runs the behavioral navigation suite.
        # Installed standalone default-mode smoke tests retain their legacy path.
        PXE_REPO=$(cd "$PXE_DIR/../../.." && pwd)
        if [ -f "$PXE_REPO/AGENTS.md" ]; then
          if [ ! -f "$PXE_REPO/tests/test_pdf_navigation.py" ]; then
            echo "pdf-export: N repository navigation acceptance suite unavailable"; exit 2
          fi
          python3 "$PXE_REPO/tests/test_pdf_navigation.py" || exit $?
        fi
        exit 0
      fi
      echo "Self-test: PASS (degraded — python3 unavailable; pdf-export is advisory without it)"; exit 0
    fi
    if command -v python3 >/dev/null 2>&1 && [ -f "$PXE_HELPER" ]; then
      if [ $# -lt 1 ]; then echo "Usage: $0 pdf-export <run_folder> | (generate) via annotation_export.py pdf <run_folder>"; exit 2; fi
      python3 "$PXE_HELPER" pdf-export "$@"; exit $?
    fi
    echo "WARN: python3 unavailable — pdf-export skipped; check inline that the PDF text runs are the snapshot lines with a manifest-keyed [finding_id] marker at each locus, the Findings section carries the verbatim comments, and stripping the markers reproduces the snapshot. See docs/annotated-manuscript-export.md."
    exit 0
    ;;

  legal-risk)
    # Legal Risk Register workflow (docs/legal-risk-register.md): structural checks over the
    # apodictic.legal_risk.v1 blocks in a register — L1 invalid item, L2 duplicate id, L3 missing
    # not-a-lawyer disclaimer (the signature gate; the register must never read as legal advice);
    # W1 legal-advice drift (a legal CONCLUSION where a flag belongs — the module firewall; override
    # <!-- override: legal-advice-drift LR-NN — … -->), W2 a review-now item not routed to legal
    # counsel. W1/W2 advisory, ERROR under --strict. The register FLAGS areas for legal review; it
    # does not give legal advice. Takes a run folder (globs *_Legal_Risk_Register_*.md) or explicit
    # files. Delegates to scripts/legal_risk.py; degrades to an advisory WARN without python3.
    LRK_DIR=$(cd "$(dirname "$0")" && pwd)
    LRK_HELPER="$LRK_DIR/legal_risk.py"
    if [ "${1:-}" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$LRK_HELPER" ]; then python3 "$LRK_HELPER" --self-test; exit $?; fi
      echo "Self-test: PASS (degraded — python3 unavailable; legal-risk is advisory without it)"; exit 0
    fi
    if command -v python3 >/dev/null 2>&1 && [ -f "$LRK_HELPER" ]; then
      if [ $# -lt 1 ]; then echo "Usage: $0 legal-risk <run_folder|files...> [--strict] | --self-test"; exit 2; fi
      python3 "$LRK_HELPER" legal-risk "$@"; exit $?
    fi
    echo "WARN: python3 unavailable — legal-risk skipped; check inline that the register carries a not-a-lawyer disclaimer, every item flags (not adjudicates) the exposure, and each review-now item routes to counsel. See docs/legal-risk-register.md."
    exit 0
    ;;

  promise-contract)
    # Promise-Contract Fidelity workflow (docs/promise-contract-audit.md): does the pitch keep the
    # promise the book makes? Structural checks over the apodictic.pitch_copy.v1 input + the F-PCF
    # apodictic.finding.v1 blocks — P1 two-sided gap (every F-PCF-NN finding cites >=1 copy: ref AND
    # >=1 contract:/ms: ref, the namespaced convention), P2 pitch copy persisted & typed (a valid
    # apodictic.pitch_copy.v1 input exists, every doc declares a copy_type), P3 reveal-leak form gate
    # (a PCF2 finding's copy: ref must not point at a synopsis); W1 drafted-copy leak (a multi-sentence
    # quoted block in the report that is not a verbatim substring of the persisted pitch copy — the
    # Firewall; override <!-- override: drafted-copy PCF-NN — … -->), W2 market-prediction drift (a
    # finding matching the prohibited sales-prediction phrase set — the #14 boundary; override
    # <!-- override: market-prediction PCF-NN — … -->). W1/W2 advisory, ERROR under --strict. The
    # module FLAGS the pitch↔book gap and a class of repair; it never drafts the copy (diagnose, don't
    # write — Shelf & Positioning owns the rewrite). Takes a run folder (globs *_Pitch_Copy_*.md, plus
    # the folder's findings) or explicit files. Delegates to scripts/promise_contract.py; degrades to
    # an advisory WARN without python3.
    PCF_DIR=$(cd "$(dirname "$0")" && pwd)
    PCF_HELPER="$PCF_DIR/promise_contract.py"
    if [ "${1:-}" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$PCF_HELPER" ]; then python3 "$PCF_HELPER" --self-test; exit $?; fi
      echo "Self-test: PASS (degraded — python3 unavailable; promise-contract is advisory without it)"; exit 0
    fi
    if command -v python3 >/dev/null 2>&1 && [ -f "$PCF_HELPER" ]; then
      if [ $# -lt 1 ]; then echo "Usage: $0 promise-contract <run_folder|files...> [--strict] | --self-test"; exit 2; fi
      python3 "$PCF_HELPER" promise-contract "$@"; exit $?
    fi
    echo "WARN: python3 unavailable — promise-contract skipped; check inline that every F-PCF finding cites a two-sided namespaced ref (copy: + contract:/ms:), the pitch copy is persisted and typed, no PCF2 is raised against a synopsis, and the report quotes the author's own copy verbatim (never drafts a replacement). See docs/promise-contract-audit.md."
    exit 0
    ;;

  continuity-bible)
    # Auto-Derived Continuity Bible (docs/continuity-bible.md): the narrative half of a style sheet —
    # consolidate the canonical facts the manuscript commits to (identity/physical facts, named
    # objects, place details) and surface the contradictions. Structural checks over the
    # apodictic.canon_fact.v1 blocks — C1 schema (bad category enum, malformed CF-NN id, missing
    # field, unquoted-numeric value, empty loci, duplicate id), C2 locus presence & shape (a coarse
    # chapter/§/¶/line/page token; a precondition, NOT a firewall proof — locus resolution is deferred
    # to the shared snapshot layer), C3 contradiction integrity (a `## Contradiction Ledger` row must
    # pair >=2 real canon_facts that share entity+attribute but assert DIFFERENT values); C4 chronology
    # consume (a chronology fact that does not consolidate to a real Timeline scene id re-derives a
    # temporal fact the Timeline owns; override <!-- override: bible-rederive CF-NN — … -->), W1
    # coverage (a Timeline POV with no Cast entry, or a Timeline setting with no Places entry). C4/W1
    # advisory, ERROR under --strict. The module EXTRACTS the stated and SURFACES contradictions; it
    # never infers an unstated fact or resolves a conflict (the Firewall). Pass the project-root
    # Timeline.md as a second file so C4 can resolve scene ids and W1 can check coverage; without it C4
    # cannot confirm scene ids and W1 is skipped. Takes a run folder (globs *_Continuity_Bible_*.md) or
    # explicit files. Delegates to scripts/continuity_bible.py; degrades to an advisory WARN without
    # python3.
    CBL_DIR=$(cd "$(dirname "$0")" && pwd)
    CBL_HELPER="$CBL_DIR/continuity_bible.py"
    if [ "${1:-}" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$CBL_HELPER" ]; then python3 "$CBL_HELPER" --self-test; exit $?; fi
      echo "Self-test: PASS (degraded — python3 unavailable; continuity-bible is advisory without it)"; exit 0
    fi
    if command -v python3 >/dev/null 2>&1 && [ -f "$CBL_HELPER" ]; then
      if [ $# -lt 1 ]; then echo "Usage: $0 continuity-bible <run_folder|files...> [--strict] | --self-test"; exit 2; fi
      python3 "$CBL_HELPER" continuity-bible "$@"; exit $?
    fi
    echo "WARN: python3 unavailable — continuity-bible skipped; check inline that every canon_fact carries a well-shaped locus, the Contradiction Ledger pairs real conflicting facts, chronology facts consolidate to a Timeline scene id, and the Bible records stated facts only (never inferring or resolving canon). See docs/continuity-bible.md."
    exit 0
    ;;

  setup-payoff)
    # Setup–Payoff Ledger (docs/setup-payoff-ledger.md): the referential-completeness half of a style
    # sheet — the mechanical home for ConStory-Bench's "Abandoned Plot Elements" row (introduced
    # expectations never resolved). Records the author-marked Foreshadow → Trigger → Payoff triples
    # (Codified Foreshadowing-Payoff Text Generation, Yun et al., arXiv:2601.07033) and CHECKS every
    # foreshadow resolves. Structural checks over apodictic.setup_payoff.v1 (foreshadow) +
    # apodictic.payoff.v1 (resolving payoff) blocks — SP1 schema (SP-NN / PO-NN ids, required fields,
    # state enum, duplicate id, bad JSON), SP2 referential integrity (a non-empty payoff_ref must
    # id-match an existing payoff block; forward-only, N:1 allowed; a phantom ref FAILs), SP3 open
    # rationale (an `open` state must carry a non-empty open_rationale), SP4 derived state (the declared
    # `state` must match the mechanically-derived §D4 value over the resolved refs — the register never
    # overrides the derivation; NO model in the gate), X1 firewall (the Ledger carries no editorial
    # Must/Should/Could-Fix token and no apodictic:finding block — a fact register, not a defect list).
    # The model marks the triple; the validator DERIVES the state and checks completeness — it never
    # decides whether a passage "counts" as payoff (the deferred SETEC-consumer job). An `abandoned` row
    # is a SURFACED fact the editorial letter cites in prose, not a validation failure. Takes a run
    # folder (globs *_Setup_Payoff_Ledger_*.md) or explicit files. Delegates to
    # scripts/setup_payoff_checks.py; degrades to an advisory WARN without python3.
    SPL_DIR=$(cd "$(dirname "$0")" && pwd)
    SPL_HELPER="$SPL_DIR/setup_payoff_checks.py"
    if [ "${1:-}" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$SPL_HELPER" ]; then python3 "$SPL_HELPER" --self-test; exit $?; fi
      echo "Self-test: PASS (degraded — python3 unavailable; setup-payoff is advisory without it)"; exit 0
    fi
    if command -v python3 >/dev/null 2>&1 && [ -f "$SPL_HELPER" ]; then
      if [ $# -lt 1 ]; then echo "Usage: $0 setup-payoff <run_folder|files...> [--strict] | --self-test"; exit 2; fi
      python3 "$SPL_HELPER" setup-payoff "$@"; exit $?
    fi
    echo "WARN: python3 unavailable — setup-payoff skipped; check inline that every setup_payoff foreshadow carries a state, a non-empty payoff_ref resolves to a real payoff block, an `open` state carries a rationale, the declared state matches the refs, and the ledger carries no editorial severity token or finding block. See docs/setup-payoff-ledger.md."
    exit 0
    ;;

  intake-interview)
    # Uncertainty-Resolution Intake Interview (docs/uncertainty-intake-interview.md): at the
    # after-Pass-0/1 checkpoint, asks the author to resolve a specific structural ambiguity the
    # framework DETECTED but cannot settle from the text — and only that. Structural checks over the
    # apodictic.intake_query.v1 blocks — I1 schema (bad kind/confidence enum, malformed IQ-NN id,
    # missing current_inference/question, duplicate id), I2 no-contract-duplication (a question that
    # re-asks a contract element owned by the intake / Shelf — advisory, ERROR --strict; override
    # <!-- override: intake-dup IQ-NN — … -->), I3 grounded ambiguity (one of a resolving
    # ambiguity_ref (a real finding id in the Ledger) or a non-empty source_note; a dangling ref is an
    # error — a query grounded in neither is manufactured), I4 calibrate-not-suppress (treat_as_intended
    # may direct HOW a feature is assessed but never pre-empt a verdict — ERROR, the Deficit-Lock
    # guard), W1 coverage (a Pass-0/1 LOW/UNCERTAIN finding or an Unresolved-Questions bullet with no
    # query — advisory). Pass the Findings Ledger as a second file so I3 resolves ids and W1 checks
    # coverage. Takes a run folder (globs *_Intake_Interview_*.md) or explicit files. Delegates to
    # scripts/intake_interview.py; degrades to an advisory WARN without python3.
    IIV_DIR=$(cd "$(dirname "$0")" && pwd)
    IIV_HELPER="$IIV_DIR/intake_interview.py"
    if [ "${1:-}" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$IIV_HELPER" ]; then python3 "$IIV_HELPER" --self-test; exit $?; fi
      echo "Self-test: PASS (degraded — python3 unavailable; intake-interview is advisory without it)"; exit 0
    fi
    if command -v python3 >/dev/null 2>&1 && [ -f "$IIV_HELPER" ]; then
      if [ $# -lt 1 ]; then echo "Usage: $0 intake-interview <run_folder|files...> [--strict] | --self-test"; exit 2; fi
      python3 "$IIV_HELPER" intake-interview "$@"; exit $?
    fi
    echo "WARN: python3 unavailable — intake-interview skipped; check inline that every intake_query disambiguates a detected ambiguity (never re-asks the contract), is grounded in a real finding id or a source_note, and that treat_as_intended calibrates assessment without suppressing a finding. See docs/uncertainty-intake-interview.md."
    exit 0
    ;;

  author-fingerprint)
    # Cross-Manuscript Author Voice/Craft Fingerprint (docs/author-voice-fingerprint.md): the
    # persistent cross-work memory of a writer's voice, collected under an operator-designated
    # author-root. It does NO new stylometry — it consumes the single-voice AI-prose machinery
    # (voice_profile / voice_distance + personal-baseline z-scores) and persists/diagnoses. Structural
    # checks over the apodictic.voice_fingerprint.v1 blocks — F1 schema (bad source enum, malformed
    # VF-… id, missing field, empty/non-scalar metrics, duplicate id), F2 provenance (each fingerprint
    # cites a centroid_ref naming a consumed audit output), F3 same-register comparison (a drift/range
    # claim referencing >=2 fingerprints must share a register — the AI-prose domain-shift guard); F4
    # descriptive-not-prescriptive (no Must/Should/Could token, no "fix your voice" directive — the
    # module observes movement, it never prescribes or grades; advisory, ERROR --strict; override
    # <!-- override: fingerprint-frame VF-… — … -->), W1 insufficient data (no register has >=2
    # fingerprints — seed-only), W2 local-only hygiene (missing local-only marker or an external URL —
    # advisory WARN ONLY, never gate-blocking; the binding privacy guarantee is the module's runtime
    # no-external-call rule). Takes an author-root (globs Author_Voice_Profile*.md) or explicit files.
    # Delegates to scripts/author_fingerprint.py; degrades to an advisory WARN without python3.
    AVF_DIR=$(cd "$(dirname "$0")" && pwd)
    AVF_HELPER="$AVF_DIR/author_fingerprint.py"
    if [ "${1:-}" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$AVF_HELPER" ]; then python3 "$AVF_HELPER" --self-test; exit $?; fi
      echo "Self-test: PASS (degraded — python3 unavailable; author-fingerprint is advisory without it)"; exit 0
    fi
    if command -v python3 >/dev/null 2>&1 && [ -f "$AVF_HELPER" ]; then
      if [ $# -lt 1 ]; then echo "Usage: $0 author-fingerprint <author_root|files...> [--strict] | --self-test"; exit 2; fi
      python3 "$AVF_HELPER" author-fingerprint "$@"; exit $?
    fi
    echo "WARN: python3 unavailable — author-fingerprint skipped; check inline that every voice_fingerprint cites a source + centroid_ref, drift is compared only within a register, the profile is descriptive (no Must/Should/Could, no 'fix your voice'), and it carries a local-only marker. See docs/author-voice-fingerprint.md."
    exit 0
    ;;

  content-advisory)
    # Content-Advisory / Sensitivity-Surface Derivation (docs/content-advisory.md): derives a
    # reader/marketing-facing advisory — where the manuscript depicts intense material, at what
    # intensity, on- or off-page — generated ONLY under the opt-in marker. Structural checks over the
    # apodictic.content_note.v1 blocks — A1 schema (bad category/intensity/depiction enum, malformed
    # CN-NN id, missing field, empty loci, category 'other' with empty label, duplicate id), A2 locus
    # presence & shape (a coarse chapter/§/¶/line/page token; resolution deferred to the snapshot
    # layer), A3 no editorial-severity leak (no Must/Should/Could token in the prose or a label, no
    # apodictic:finding block — content notes are advisories, not findings, the Legal-Risk
    # orthogonal-severity discipline); W1 prescriptive drift (a "should cut/soften …" construction,
    # NOT a bare descriptive adjective — advisory, ERROR --strict; override
    # <!-- override: advisory-eval CN-NN — … -->), W2 opt-in marker present. The module DESCRIBES the
    # depicted; it never judges or prescribes. Takes a run folder (globs *_Content_Advisory_*.md) or
    # explicit files; if no advisory artifact is resolved it no-ops with exit 2. Delegates to
    # scripts/content_advisory.py; degrades to an advisory WARN without python3.
    CAD_DIR=$(cd "$(dirname "$0")" && pwd)
    CAD_HELPER="$CAD_DIR/content_advisory.py"
    if [ "${1:-}" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$CAD_HELPER" ]; then python3 "$CAD_HELPER" --self-test; exit $?; fi
      echo "Self-test: PASS (degraded — python3 unavailable; content-advisory is advisory without it)"; exit 0
    fi
    if command -v python3 >/dev/null 2>&1 && [ -f "$CAD_HELPER" ]; then
      if [ $# -lt 1 ]; then echo "Usage: $0 content-advisory <run_folder|files...> [--strict] | --self-test"; exit 2; fi
      python3 "$CAD_HELPER" content-advisory "$@"; exit $?
    fi
    echo "WARN: python3 unavailable — content-advisory skipped; check inline that every content_note carries a well-shaped locus, the advisory is descriptive (no Must/Should/Could, no 'should cut/soften'), carries no apodictic:finding block, and has the opt-in marker. See docs/content-advisory.md."
    exit 0
    ;;

  coaching-history)
    # Coaching History & Pattern Recognition (docs/coaching-history.md; ROADMAP §Coaching Deepening):
    # APODICTIC's ONE ethically-sensitive surface. Over multiple revision cycles the coach can surface
    # a cross-session PROCESS pattern — the same finding deferred across an unbroken run of sessions, or
    # a revision-arc phase left open across consecutive sessions — as a rolling, OPT-IN, local-only
    # artifact of DESCRIPTIVE observations, each MECHANICALLY derived from the recorded finding-
    # disposition / finding_states records (a count, never a vibe) and carrying NO editorial severity
    # (no Must/Should/Could token, no apodictic:finding block). Structural checks over the
    # apodictic.coaching_observation.v1 blocks in the ONE *_Coaching_History_*.md — H1 schema + unique
    # CH-NN + per-pattern count floor (deferral-recurrence >=3, phase-incompletion >=2), H2 provenance/
    # anti-fabrication (every `<F-id> deferred @ session <n>` resolves to a recorded deferred
    # disposition; len(evidence)>=count; the cited sessions are ACTUALLY CONSECUTIVE), H3 descriptive-
    # not-judgmental (reuses author_fingerprint._PRESCRIPTIVE_RE + a trait-blame lexicon; WARN, ERROR
    # --strict; per-id override <!-- override: coaching-observation CH-NN — … -->), H4 no-severity-leak,
    # H7 tentative-framing (no trait VERDICT / no bare-scoreboard rendering / carries an invitation —
    # the transference-health floor; WARN, ERROR --strict), W1 local-only. Plus the TWO Fable ethics
    # gates: H5 single-home / no coach-only shadow (scan project root + runs/* + the sidecar; a
    # projected observation block / schema-id / evidence-grammar string outside the one artifact, a
    # second artifact, or sidecar coaching material beyond `coaching_history_seq` = non-overridable
    # ERROR; a bare CH-NN token elsewhere = WARN + override), and H6 deletion-honored (under the
    # <!-- coaching-history: deleted --> tombstone, RECOMPUTE deletion from artifacts — the full H5 scan
    # empty + no surviving artifact + no seq; residue = ERROR, NO override; opted-in+deleted = ERROR).
    # The `delete <project_root>` subcommand removes every artifact (root + runs/*), drops the seq, and
    # flips the Diagnostic_State.md consent marker to the tombstone (deletion revokes consent). OPT-IN:
    # produced only under `<!-- coaching-history: opted-in -->` (home: Diagnostic_State.md); no marker →
    # no-op (exit 2). Takes the PROJECT ROOT (H5/H6 scan scope), not just the artifact. Delegates to
    # scripts/coaching_history.py; degrades to an advisory WARN without python3.
    CHH_DIR=$(cd "$(dirname "$0")" && pwd)
    CHH_HELPER="$CHH_DIR/coaching_history.py"
    if [ "${1:-}" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$CHH_HELPER" ]; then python3 "$CHH_HELPER" --self-test; exit $?; fi
      echo "Self-test: PASS (degraded — python3 unavailable; coaching-history is advisory without it)"; exit 0
    fi
    if command -v python3 >/dev/null 2>&1 && [ -f "$CHH_HELPER" ]; then
      if [ $# -lt 1 ]; then echo "Usage: $0 coaching-history <project_root|files...> [--strict] | coaching-history delete <project_root> | --self-test"; exit 2; fi
      if [ "${1:-}" = "delete" ]; then python3 "$CHH_HELPER" delete "$2"; exit $?; fi
      python3 "$CHH_HELPER" coaching-history "$@"; exit $?
    fi
    echo "WARN: python3 unavailable — coaching-history skipped; check inline that observations live in exactly ONE opted-in *_Coaching_History_*.md (no projection into session plans / the sidecar), every observation resolves to recorded consecutive deferrals, none carries a Must/Should/Could token or a trait verdict, and a tombstoned project has no surviving artifact/seq. See docs/coaching-history.md."
    exit 0
    ;;

  style-explanation)
    # Interpretable Stylometric Explanation (docs/interpretable-stylometric-explanation.md): the
    # DESCRIPTIVE labelling layer ON TOP of the Author Voice Fingerprint (#9). #9 measures how
    # distinctive a voice is and persists it as scalar z-scores; this overlay attaches a
    # natural-language gloss to a handful of the salient MEASURED features, each bound by provenance
    # (feature_ref) to the exact SETEC voice_profile feature it describes. It does NO new stylometry
    # and offers NO advice — it NAMES a measured feature, it never prescribes a voice change and never
    # fabricates a style claim. Structural checks over the apodictic.style_label.v1 blocks — X1 schema
    # (bad feature_family/frame/direction/magnitude enum, malformed SL-NN id, missing field, broken
    # JSON, duplicate id), X2 provenance/anti-fabrication (every label cites a non-empty feature_ref
    # into a consumed measurement — an un-sourced label is fabricated), X3 no-severity-leak (no
    # Must/Should/Could token in the prose or a label, no apodictic:finding block — a style label is
    # not a defect), X4 descriptive-not-prescriptive (no prescriptive voice-directive and no
    # comparison-to-emulate construction in a label or the prose — the signature firewall gate;
    # advisory, ERROR --strict; per-id override <!-- override: style-frame SL-NN — … -->, prose-level
    # override the bare <!-- override: style-frame — … -->), X5 same-register cluster (a
    # describes-cluster label referencing >=2 labels must share a register — the AI-prose domain-shift
    # guard); W1 seed/coverage (a single glossed feature is a thin overlay — advisory, ERROR --strict;
    # no blocks no-op), X6 local-only hygiene (missing local-only marker or an external URL — advisory
    # WARN ONLY, never gate-blocking; the binding privacy guarantee is the module's runtime
    # no-external-call rule). The schema itself is built so a "write more like X" directive is
    # unrepresentable (no target/goal/recommendation/rewrite field; closed descriptive enums). Takes an
    # author-root (globs Author_Style_Explanation*.md / Author_Voice_Profile*.md) or explicit files; if
    # no style-explanation artifact is resolved it no-ops with exit 2. The label-generating
    # embedding/scoring model is a deferred M2 lazy-import + skipif seam — this validator never calls a
    # model. Delegates to scripts/style_explanation.py; degrades to an advisory WARN without python3.
    SEX_DIR=$(cd "$(dirname "$0")" && pwd)
    SEX_HELPER="$SEX_DIR/style_explanation.py"
    if [ "${1:-}" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$SEX_HELPER" ]; then python3 "$SEX_HELPER" --self-test; exit $?; fi
      echo "Self-test: PASS (degraded — python3 unavailable; style-explanation is advisory without it)"; exit 0
    fi
    if command -v python3 >/dev/null 2>&1 && [ -f "$SEX_HELPER" ]; then
      if [ $# -lt 1 ]; then echo "Usage: $0 style-explanation <author_root|files...> [--strict] | --self-test"; exit 2; fi
      python3 "$SEX_HELPER" style-explanation "$@"; exit $?
    fi
    echo "WARN: python3 unavailable — style-explanation skipped; check inline that every style_label cites a non-empty feature_ref, the overlay is descriptive (no Must/Should/Could, no 'vary your voice', no 'write more like X'), carries no apodictic:finding block, a describes-cluster stays within one register, and the profile has a local-only marker. See docs/interpretable-stylometric-explanation.md."
    exit 0
    ;;

  persona-divergence)
    # Reader-Persona Simulation (docs/reader-persona-simulation.md): runs the reader-experience lens
    # through several declared reading DISPOSITIONS and surfaces where the predicted experience
    # DIVERGES. Structural checks over the apodictic.persona.v1 + apodictic.divergence.v1 blocks — D1
    # schema (bad disposition/target/experience enum, malformed P-NN/D-NN id, missing
    # anchor/magnitude/experiences, a nested experiences value not in engaged|neutral|friction|
    # disengage or naming an undeclared persona, duplicate id), D2 grounded prediction (a divergence
    # anchor must resolve to a real finding id in the Ledger or a real Timeline scene id — the
    # signature firewall gate; an ungrounded prediction is fabricated), D3 target-severity anchoring
    # (exactly one persona target:true, and no divergence asserted_severity below the anchored
    # finding's locked Ledger severity — segmentation may not downgrade the verdict); D4 no fabricated
    # testimony (a first-person reader-reaction quote presented as data — the #17 boundary; advisory,
    # ERROR --strict; override <!-- override: persona-quote D-NN — … -->), D5 disposition-not-character
    # (a persona block with any key outside the closed disposition set — ERROR, NON-overridable, the
    # real guarantee against #17), W1 coverage (>=2 personas with a varying disposition axis). Pass the
    # Findings Ledger (and optionally the Timeline) as additional files so D2/D3 resolve. Takes a run
    # folder (globs *_Persona_Divergence_Map_*.md) or explicit files. Delegates to
    # scripts/persona_divergence.py; degrades to an advisory WARN without python3.
    PDV_DIR=$(cd "$(dirname "$0")" && pwd)
    PDV_HELPER="$PDV_DIR/persona_divergence.py"
    if [ "${1:-}" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$PDV_HELPER" ]; then python3 "$PDV_HELPER" --self-test; exit $?; fi
      echo "Self-test: PASS (degraded — python3 unavailable; persona-divergence is advisory without it)"; exit 0
    fi
    if command -v python3 >/dev/null 2>&1 && [ -f "$PDV_HELPER" ]; then
      if [ $# -lt 1 ]; then echo "Usage: $0 persona-divergence <run_folder|files...> [--strict] | --self-test"; exit 2; fi
      python3 "$PDV_HELPER" persona-divergence "$@"; exit $?
    fi
    echo "WARN: python3 unavailable — persona-divergence skipped; check inline that every persona is a closed-key disposition (no character keys), every divergence anchors a real finding/locus, exactly one persona is target:true with no asserted severity below the locked verdict, and no fabricated reader quotes appear. See docs/reader-persona-simulation.md."
    exit 0
    ;;

  world-bible)
    # Standalone Worldbuilding Bible (docs/worldbuilding-bible.md): a pre-draft consistency check over
    # the author's OWN hand-authored worldbuilding bible — distinct from the manuscript-facing SFF
    # audits. Structural checks over the apodictic.world_fact.v1 blocks — W1 schema (bad category/
    # polarity enum, malformed WF-NN id, missing field, unquoted-numeric value, empty loci, broken
    # JSON) PLUS bespoke closed-key checking (the subset engine admits unknown keys, so a misspelled
    # field would otherwise pass — caught here or the closed-set guarantee is hollow), WD duplicate id,
    # and the three deterministic, stdlib-only, CONSERVATIVE contradiction arms: WB-R1 closed-set rule
    # consistency (same subject + normalized value, can vs cannot / requires vs cannot), WB-C1 cost
    # contradiction (two different stated costs for one subject) + WB-C2 free-then-costed (advisory,
    # ERROR --strict), WB-G1 distance contradiction (one edge, two parsed distances WITHIN a
    # commensurable unit class — spatial mile/league/km vs temporal travel-time day/hour are SEPARATE
    # axes that never collide-check against each other), WB-G2 chronology (a CYCLE in the happens-before
    # graph, or the same event at two Day anchors). Plus a WF firewall prose scan (a resolution/
    # invention verb leaking into the bible's prose; advisory, ERROR --strict). Each pair is overridable
    # per-pair: <!-- override: world-rule|world-cost|world-geo WF-NN/WF-MM — … --> (and
    # <!-- override: world-firewall — … --> for WF). The tool EXTRACTS the stated and SURFACES the
    # contradictions the bible has committed to; it never invents world content or resolves a conflict
    # (the Firewall). Takes a run folder (globs *_Worldbuilding_Bible_*.md) or explicit files.
    # Delegates to scripts/world_bible.py; degrades to an advisory WARN without python3.
    WBL_DIR=$(cd "$(dirname "$0")" && pwd)
    WBL_HELPER="$WBL_DIR/world_bible.py"
    if [ "${1:-}" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$WBL_HELPER" ]; then python3 "$WBL_HELPER" --self-test; exit $?; fi
      echo "Self-test: PASS (degraded — python3 unavailable; world-bible is advisory without it)"; exit 0
    fi
    if command -v python3 >/dev/null 2>&1 && [ -f "$WBL_HELPER" ]; then
      if [ $# -lt 1 ]; then echo "Usage: $0 world-bible <run_folder|files...> [--strict] | --self-test"; exit 2; fi
      python3 "$WBL_HELPER" world-bible "$@"; exit $?
    fi
    echo "WARN: python3 unavailable — world-bible skipped; check inline that every world_fact carries a well-shaped locus, no rule both can and cannot the same thing, no power is priced two ways or free-then-costed, no edge has two distances on one axis, the happens-before order has no cycle, and the bible records stated facts only (never inventing or resolving world content). See docs/worldbuilding-bible.md."
    exit 0
    ;;

  registry-check)
    # Project registry integrity (Project Addressability, Increment 2; docs/project-addressability.md):
    # structural checks over a workspace-relative .apodictic/registry.json (apodictic.project_registry.v1
    # + apodictic.project_entry.v1) — R1 invalid entry (envelope/per-entry schema, bad id/mode/JSON),
    # R2 missing root (no dir = ERROR; no sidecar = WARN), R3 drift between a denormalized field and the
    # canonical sidecar (WARN; ERROR --strict; sidecar always wins — the registry is a rebuildable cache),
    # R4 duplicate id. Takes a registry file or a workspace dir containing .apodictic/registry.json.
    # Delegates to scripts/registry_check.py; degrades to an advisory WARN without python3.
    RGC_DIR=$(cd "$(dirname "$0")" && pwd)
    RGC_HELPER="$RGC_DIR/registry_check.py"
    if [ "${1:-}" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$RGC_HELPER" ]; then python3 "$RGC_HELPER" --self-test; exit $?; fi
      echo "Self-test: PASS (degraded — python3 unavailable; registry-check is advisory without it)"; exit 0
    fi
    if command -v python3 >/dev/null 2>&1 && [ -f "$RGC_HELPER" ]; then
      if [ $# -lt 1 ]; then echo "Usage: $0 registry-check <registry.json | workspace_dir> [--strict] | --self-test"; exit 2; fi
      python3 "$RGC_HELPER" registry-check "$@"; exit $?
    fi
    echo "WARN: python3 unavailable — registry-check skipped; check inline that .apodictic/registry.json is valid apodictic.project_registry.v1, ids are unique, every root resolves, and denormalized mode/next_action match each project's sidecar (sidecar wins). See docs/project-addressability.md."
    exit 0
    ;;

  schema-coverage)
    # Harness Contracts v2 (docs/harness-contracts-v2.md): the schema-coverage gate — prove disk
    # reality matches the declarative schemas/_coverage.json binding table, so every apodictic.*.schema.json
    # stays bound to a validator (C2 no-orphan, C3 no-phantom) and stays exercised against a real canonical
    # file by --check-all (C4 binding-proven via grep of the BOUND script, C5 canonical-gate reachable),
    # and the closed-key (additionalProperties:false) contract in each schema file agrees with the manifest
    # (C1'). W1 (advisory; ERROR --strict) flags a dead non_artifact exclusion. --check-docs runs the
    # advisory docs-no-re-list prose lint. Delegates to scripts/schema_coverage.py; degrades to advisory
    # PASS without python3.
    SCV_DIR=$(cd "$(dirname "$0")" && pwd)
    SCV_HELPER="$SCV_DIR/schema_coverage.py"
    if [ "${1:-}" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$SCV_HELPER" ]; then python3 "$SCV_HELPER" --self-test; exit $?; fi
      echo "Self-test: PASS (degraded — python3 unavailable; schema-coverage is advisory without it)"; exit 0
    fi
    if command -v python3 >/dev/null 2>&1 && [ -f "$SCV_HELPER" ]; then
      python3 "$SCV_HELPER" schema-coverage "$@"; exit $?
    fi
    echo "WARN: python3 unavailable — schema-coverage skipped; check inline that every plugins/apodictic/schemas/apodictic.*.schema.json appears in schemas/_coverage.json bindings[] with a real validator + canonical file, and that each closed_keys:true schema carries additionalProperties:false. See docs/harness-contracts-v2.md."
    exit 0
    ;;

  lifecycle-node)
    # State-driven dispatch (Project Addressability, Increment 3; docs/project-addressability.md):
    # derive a bound project's lifecycle node from its Diagnostic_State.meta.json sidecar by a single
    # first-match precedence (cold -> blocked_gate -> execution -> pre_writing -> submission ->
    # revising -> diagnosed -> diagnosing). Total: every readable sidecar resolves to exactly one node,
    # with `diagnosing` the catch-all default. A tested primitive for /start, /projects, and the
    # Increment-4 loop dispatcher — no new stored state. `diagnosed` checks for a synthesis/editorial
    # letter relative to the sidecar's project root (optional run_folder = extra search location);
    # no letter -> diagnosing. Pure derivation (no FAIL verdict). Delegates to scripts/lifecycle_node.py.
    LCN_DIR=$(cd "$(dirname "$0")" && pwd)
    LCN_HELPER="$LCN_DIR/lifecycle_node.py"
    if [ "${1:-}" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$LCN_HELPER" ]; then python3 "$LCN_HELPER" --self-test; exit $?; fi
      echo "Self-test: PASS (degraded — python3 unavailable; lifecycle-node is advisory without it)"; exit 0
    fi
    if command -v python3 >/dev/null 2>&1 && [ -f "$LCN_HELPER" ]; then
      if [ $# -lt 1 ]; then echo "Usage: $0 lifecycle-node <sidecar> [run_folder] | --self-test"; exit 2; fi
      python3 "$LCN_HELPER" lifecycle-node "$@"; exit $?
    fi
    echo "WARN: python3 unavailable — lifecycle-node skipped; derive the node inline by the precedence in docs/project-addressability.md (cold -> blocked_gate -> execution -> pre_writing -> submission -> revising -> diagnosed -> diagnosing)."
    exit 0
    ;;

  argument-spine)
    # Nonfiction Pre-Draft Pathway, Increments 1-3 + 5 (docs/nonfiction-pre-draft.md): structural checks
    # over the apodictic.argument_spine.v1 block (the pre-draft argument plan that SEEDS the shared
    # Argument_State.md), the apodictic.support_plan.v1 blocks (source/evidence map, §3), the
    # apodictic.warrant_plan.v1 blocks (warrant pre-check, §4), and the apodictic.genre_profile.v1 block
    # (the genre layer — holds a genre to its required-section skeleton). A1 invalid spine; A2 unseeded
    # (spine must populate §1/§2 — signature); A3 thesis/C0 drift. Inc 2: A4 invalid support plan; A5
    # dangling subclaim_id; A6 support unseeded (no §3 heading). Inc 3: A7 invalid warrant plan; A8
    # dangling subclaim_id; A9 warrant unseeded (no §4 heading). Inc 5: B1 invalid genre profile; B2
    # section unseeded (a declared genre section has no heading — signature); B3 genre/form mismatch
    # (spine-present only; normalized); B4 duplicate genre profile. Advisory (ERROR --strict): W1
    # anti-thesis echo (override argument-spine-antithesis), W2 bare assertion (a subclaim with no
    # planned support), W3 implicit warrant for a HOSTILE audience (non-EXPLICIT / ABSENT-backed;
    # override argument-spine-warrant), W4 thin genre skeleton (a canonical genre section omitted;
    # override argument-spine-genre). Takes a run folder (globs Argument_State*.md) or explicit files.
    # Delegates to scripts/argument_spine.py; degrades to an advisory WARN without python3.
    AS_DIR=$(cd "$(dirname "$0")" && pwd)
    AS_HELPER="$AS_DIR/argument_spine.py"
    if [ "${1:-}" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$AS_HELPER" ]; then python3 "$AS_HELPER" --self-test; exit $?; fi
      echo "Self-test: PASS (degraded — python3 unavailable; argument-spine is advisory without it)"; exit 0
    fi
    if command -v python3 >/dev/null 2>&1 && [ -f "$AS_HELPER" ]; then
      if [ $# -lt 1 ]; then echo "Usage: $0 argument-spine <run_folder|files...> [--strict] | --self-test"; exit 2; fi
      python3 "$AS_HELPER" argument-spine "$@"; exit $?
    fi
    echo "WARN: python3 unavailable — argument-spine skipped; check inline that the spine seeds Argument_State §1/§2, the C0 main claim carries the thesis, and the anti-thesis names a genuine opposing view. See docs/nonfiction-pre-draft.md."
    exit 0
    ;;

  scene-ethics)
    # Scene-Ethics Plan (Nonfiction Pre-Draft, Increment 4; docs/nonfiction-pre-draft.md): structural
    # checks over the apodictic.scene_ethics.v1 blocks — the writer's pre-draft ETHICAL plan for each
    # identifiable real person depicted (consent_status, handling, fairness_check), distinct from the
    # Legal Risk Register (legal exposure) and cross-referencing it via legal_ref. E1 invalid item,
    # E2 duplicate id; W1 unresolved depiction (as-is + consent not-sought + no fairness rationale —
    # the signature; override scene-ethics-unresolved EP-NN), W2 no legal cross-check (an as-is
    # identifiable depiction with no legal_ref — check it against the Legal Risk Register; override
    # scene-ethics-legalcheck EP-NN). W1/W2 advisory, ERROR under --strict. Takes a run folder
    # (globs *_Scene_Ethics_Plan_*.md) or explicit files. Delegates to scripts/scene_ethics.py;
    # degrades to an advisory WARN without python3.
    SCE_DIR=$(cd "$(dirname "$0")" && pwd)
    SCE_HELPER="$SCE_DIR/scene_ethics.py"
    if [ "${1:-}" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$SCE_HELPER" ]; then python3 "$SCE_HELPER" --self-test; exit $?; fi
      echo "Self-test: PASS (degraded — python3 unavailable; scene-ethics is advisory without it)"; exit 0
    fi
    if command -v python3 >/dev/null 2>&1 && [ -f "$SCE_HELPER" ]; then
      if [ $# -lt 1 ]; then echo "Usage: $0 scene-ethics <run_folder|files...> [--strict] | --self-test"; exit 2; fi
      python3 "$SCE_HELPER" scene-ethics "$@"; exit $?
    fi
    echo "WARN: python3 unavailable — scene-ethics skipped; check inline that no identifiable person is depicted as-is without consent and without a fairness rationale, and that as-is depictions cross-check the Legal Risk Register. See docs/nonfiction-pre-draft.md."
    exit 0
    ;;

  reader-instrument)
    # Beta-Reader Instrument (Workflows / revision-coach; docs/beta-reader-instrument.md): the upstream
    # complement to feedback-triage. Structural checks over apodictic.reader_question.v1 blocks — reader
    # questions seeded from the diagnosis's OPEN uncertainties (LOW/UNCERTAIN findings, Unresolved-Questions
    # bullets, risk_if_fixed tradeoffs), read together with the Findings Ledger they target. B1 invalid
    # item; B2 duplicate id; B3 provenance integrity (finding source -> a `targets` resolving to a real
    # ledger finding; unresolved-question -> a `source_note` and no targets); B4 leading/invented content
    # (firewall scan — override reader-instrument leading-question RQ-NN); B5 relitigating a LOCKED verdict
    # (severity in {Must-Fix,Should-Fix} AND confidence in {HIGH,MEDIUM} — override how-to-fix RQ-NN); W1
    # coverage. B4/B5/W1 advisory, ERROR under --strict. Takes a run folder (globs the instrument +
    # *_Findings_Ledger_*.md) or explicit files. Delegates to scripts/reader_instrument.py; degrades to an
    # advisory WARN without python3.
    RDI_DIR=$(cd "$(dirname "$0")" && pwd)
    RDI_HELPER="$RDI_DIR/reader_instrument.py"
    if [ "${1:-}" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$RDI_HELPER" ]; then python3 "$RDI_HELPER" --self-test; exit $?; fi
      echo "Self-test: PASS (degraded — python3 unavailable; reader-instrument is advisory without it)"; exit 0
    fi
    if command -v python3 >/dev/null 2>&1 && [ -f "$RDI_HELPER" ]; then
      if [ $# -lt 1 ]; then echo "Usage: $0 reader-instrument <run_folder|files...> [--strict] | --self-test"; exit 2; fi
      python3 "$RDI_HELPER" reader-instrument "$@"; exit $?
    fi
    echo "WARN: python3 unavailable — reader-instrument skipped; check inline that each reader question is non-leading, content-neutral, sourced from a LOW/UNCERTAIN finding or an Unresolved Question (not a locked verdict), and carries an expected_signal. See docs/beta-reader-instrument.md."
    exit 0
    ;;

  manuscript-viz)
    # Manuscript-Structure Visualizations (Horizon Tier 1; docs/manuscript-visualizations.md): a
    # presentation layer that adds no analysis. Validates the apodictic.viz_manifest.v1 block (data
    # copied verbatim from the Timeline Event-Ledger + apodictic.finding.v1 blocks) against its sources:
    # E1 schema + no-visual-style allowlist, E2 provenance closure (scene_id -> Timeline row; finding id
    # -> ledger; finding chapter == the conservative Chapter-N/Ch-N evidence_refs parse, else 'unplaced'),
    # E3 every body Must-Fix appears, E4 byte-equal copy fidelity (no compute/embellish). W1 coverage
    # advisory, ERROR under --strict. Charts 4-7 (Manuscript-Visualization Completion) add four OPTIONAL
    # additive arrays; the M1 render-only chart is the NONFICTION CLAIM LADDER (claim_ladder[]) over the
    # apodictic.argument_spine.v1 + apodictic.support_plan.v1 producers: X1 new-array schema + no scene
    # axis (a scene_ids/scene_id/section key on a claim_ladder object is itself a failure), X5/X6
    # claim-ladder provenance (claim_id is a declared spine subclaim via spine_subclaim_ids; label is the
    # subclaim string minus its leading Cn token; support[] byte-copies support_plan.v1; an empty
    # support[] only for a bare assertion), X7 no duplicate rung, X8 producer-present (no producer, no
    # chart), W3 chart coverage. All four manifest arrays now have a producer: chart 5 (co_presence) over
    # apodictic.scene_roster.v1 (X2 — byte-checks each co_presence[].scene_id against a roster entry + a
    # Timeline row, every co_presence name against the scene's roster (canonical) names, the Timeline POV
    # against the roster (cross-check), and the producer's anchor-non-empty); chart 6 (scene_functions)
    # over apodictic.scene_function.v1 (X3 — manifest function == the producer's closed scene-turn
    # Unit-Classification, non-empty anchor, provenance closure); and chart 4 (reveal_points) over
    # apodictic.tension_point.v1 (X4 — manifest tension == the producer's closed 1-5 reader-intensity
    # level, non-empty anchor, provenance closure — keyed directly on scene_id, no evidence_ref
    # resolution). The one still-producer-gated chart is 7-fiction's beat-map (no manifest array here;
    # awaits apodictic.story_spine.v1). --require-block makes a missing/
    # invalid manifest a hard failure (the canonical-example gate uses it so it can't pass vacuously). The
    # severity->encoding map (and the co-presence weight->chord-thickness band, the scene-function colour
    # band, the tension level->y-position map) is hardcoded in the render-only SVG layer (charts 1-3 + the
    # claim ladder + the co-presence network + the scene-function heatmap + the tension timeline),
    # not the manifest, so a run cannot recolor a Must-Fix. Takes a run folder (globs the manifest +
    # Timeline + Findings Ledger + Argument_State spine + Scene_Roster + Scene_Function + Tension producers)
    # or explicit files. Delegates to
    # scripts/viz_manifest.py; degrades to an advisory WARN without python3. (`viz_manifest.py render ...`
    # emits the HTML.)
    MVZ_DIR=$(cd "$(dirname "$0")" && pwd)
    MVZ_HELPER="$MVZ_DIR/viz_manifest.py"
    if [ "${1:-}" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$MVZ_HELPER" ]; then python3 "$MVZ_HELPER" --self-test; exit $?; fi
      echo "Self-test: PASS (degraded — python3 unavailable; manuscript-viz is advisory without it)"; exit 0
    fi
    if command -v python3 >/dev/null 2>&1 && [ -f "$MVZ_HELPER" ]; then
      if [ $# -lt 1 ]; then echo "Usage: $0 manuscript-viz <run_folder|files...> [--strict] [--require-block] | --self-test"; exit 2; fi
      python3 "$MVZ_HELPER" manuscript-viz "$@"; exit $?
    fi
    echo "WARN: python3 unavailable — manuscript-viz skipped; check inline that the viz_manifest copies Timeline/finding values verbatim, carries no visual-style fields, places findings only by the Chapter-N evidence_refs parse (else 'unplaced'), includes every Must-Fix, and that any claim_ladder[] copies the argument_spine subclaims + support_plan coverage verbatim with no scene axis. See docs/manuscript-visualizations.md."
    exit 0
    ;;

  annotated-manuscript)
    # Annotated-Manuscript Deliverable (Horizon -> Planned; docs/annotated-manuscript.md): the editorial
    # letter's findings anchored in the margin of an immutable manuscript SNAPSHOT. Validates the
    # apodictic.annotation.v1 manifest + the annotated copy: A1 schema + finding_id uniqueness, A2
    # no-mutation (delete every {>> ... <<} CriticMarkup span == the bound snapshot, byte-for-byte; a
    # two-sided sigil precondition before render), A3 anchor integrity (line-range/section/chapter must
    # resolve to a unique heading; an honest `document` note is fine), A4 the rendered comment-span
    # multiset equals the manifest comment multiset both directions — every body Must-Fix renders, and
    # no un-manifested/authored span is present (reusing finding_trace's ledger inventory), A5 each
    # comment is a verbatim, inline-CriticMarkup-safe projection of the finding's fields. A6 (Increment 2)
    # quote integrity: a `quote` anchor's text (from a finding's optional verbatim evidence_quote) occurs
    # in the snapshot verbatim and EXACTLY once, the offsets pin it, and it matches the finding — the
    # fabricated/mis-placed-quote failure A3 cannot see. W1 coverage / Timeline-boundary drift
    # advisory, ERROR under --strict (override `<!-- override: annotation-coverage F-... -->`). Comments
    # only — never prose mutation (the Firewall). Takes a run folder (globs snapshot + manifest +
    # annotated copy + Findings Ledger + Timeline) or explicit files. Delegates to
    # scripts/annotation_manifest.py; degrades to an advisory WARN without python3.
    # (`annotation_manifest.py build <run_folder>` generates the manifest + annotated copy from the
    # snapshot + ledger + Timeline; `render <manifest> <snapshot>` re-renders the annotated copy.)
    AM_DIR=$(cd "$(dirname "$0")" && pwd)
    AM_HELPER="$AM_DIR/annotation_manifest.py"
    if [ "${1:-}" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$AM_HELPER" ]; then python3 "$AM_HELPER" --self-test; exit $?; fi
      echo "Self-test: PASS (degraded — python3 unavailable; annotated-manuscript is advisory without it)"; exit 0
    fi
    if command -v python3 >/dev/null 2>&1 && [ -f "$AM_HELPER" ]; then
      if [ $# -lt 1 ]; then echo "Usage: $0 annotated-manuscript <run_folder|files...> [--strict] | --self-test"; exit 2; fi
      python3 "$AM_HELPER" annotated-manuscript "$@"; exit $?
    fi
    echo "WARN: python3 unavailable — annotated-manuscript skipped; check inline that the annotated copy mutates no prose (deleting every {>> ... <<} span reproduces the snapshot), each comment is a verbatim finding-field projection, and every Must-Fix appears as a margin comment span. See docs/annotated-manuscript.md."
    exit 0
    ;;

  reader-contract-outline)
    # Reader-Contract Reverse Outline Deliverable (SPEC v3.1; docs/reader-contract-outline.md): the book
    # scene by scene, mapped against the reader contract it implicitly makes. A byte-deterministic
    # PROJECTION of four inputs (Pass 0 reverse outline, Contract, Findings Ledger, and the gated
    # Contract Map) — the model's ONLY authored bytes anywhere in the deliverable are the Map's ids-only
    # localization (apodictic.contract_map.v1, closed-key). Validates R1 spine projection round-trips to
    # Pass 0 (ids+count+text verbatim), R2 two-sided contract-field fidelity (none dropped/invented,
    # empty fields render their literal state), R3 the rendered Contract Map <-> Map-block bijection with
    # every evidence line byte-matching the cited scene's Pass 0 "what the reader now knows" line, R4 no
    # fabricated gap (each gap cell is `none logged` or the verbatim Ledger projection), R5 no
    # untranslated framework shorthand in the deliverable (the letter's author-facing families), R6
    # contract coverage (advisory WARN; ERROR --strict; the READER-PROMISE split-completeness question,
    # override `<!-- override: reader-contract-coverage — ... -->` via the override_marker SSoT), and R7
    # map integrity (Mode-11 untrusted input: closed-key schema, inputs.*_sha256 bound to the staged
    # artifacts so a stale Map fails loudly, every clause_text a verbatim substring of its named Contract
    # source_field, the clause denominator recomputed from the Contract — never trusted from the Map).
    # Takes a run folder (globs Pass 0 + Contract + Ledger + Map + the rendered outline) or explicit
    # files. Delegates to scripts/reader_contract_outline.py; degrades to an advisory WARN without
    # python3. (`reader_contract_outline.py build <staging>` R7-gates the Map then projects the outline.)
    RCO_DIR=$(cd "$(dirname "$0")" && pwd)
    RCO_HELPER="$RCO_DIR/reader_contract_outline.py"
    if [ "${1:-}" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$RCO_HELPER" ]; then python3 "$RCO_HELPER" --self-test; exit $?; fi
      echo "Self-test: PASS (degraded — python3 unavailable; reader-contract-outline is advisory without it)"; exit 0
    fi
    if command -v python3 >/dev/null 2>&1 && [ -f "$RCO_HELPER" ]; then
      if [ $# -lt 1 ]; then echo "Usage: $0 reader-contract-outline <run_folder|files...> [--strict] | --self-test"; exit 2; fi
      python3 "$RCO_HELPER" reader-contract-outline "$@"; exit $?
    fi
    echo "WARN: python3 unavailable — reader-contract-outline skipped; check inline that §Scene Spine round-trips to the Pass 0 reverse outline verbatim, §The Reader Contract projects every Contract schema field two-sided, each Contract-Map evidence line byte-matches the cited scene's Pass 0 'what the reader now knows' line, each gap cell is `none logged` or the verbatim Ledger entry, and the Map's inputs.*_sha256 bind to the staged Pass 0/Contract/Ledger. See docs/reader-contract-outline.md."
    exit 0
    ;;

  calibration-honesty)
    # Cross-surface uncalibrated-band calibration-honesty guard (SPEC narrative-decision-residue Inc c;
    # docs/calibration-honesty.md). Both decision-audit surfaces (narrative_decision_audit / StoryScope,
    # argument_decision_audit / ArgScope) ship an `uncalibrated` verdict band with null thresholds; the
    # discipline — render the band as PROVENANCE only, never as a calibrated verdict — was enforced
    # entirely in prose. This arm mechanizes it: a WHOLE-LETTER, per-PARAGRAPH scan (D2 — region-scoping
    # was a false foundation: the only per-audit sectioner is appendix-only, decision-audit findings land
    # in the unscoped synthesis body, and the canonical fixture carries no decision-audit region) that
    # flags a paragraph only when a CLAIM SHAPE (CS1 band-placement / CS2 calibrated-verdict / CS3
    # threshold-claim / CS4 aggregate-as-verdict) matches AND no QUALIFIER (uncalibrated / provenance-only
    # / advisory / not-a-verdict / …) is co-present in that paragraph — bare token presence never fires,
    # which is what keeps the mandated boilerplate + vendored bundle labels safe. WARN by default, ERROR
    # under --strict (D4 — the honest class: an OPEN natural-language co-presence check, content_advisory
    # W1 / stance-consistency F4, failure direction toward NOT firing). D5 disjoint from severity-floor:
    # the submission-readiness band vocabulary (Strong Fit / Highest Band / …) is excised from CS1, so a
    # legal readiness verdict does not fire here. Per-paragraph override via the shared override_marker
    # SSoT (`<!-- override: calibration-honesty — <why> -->`). Cross-surface + surface-agnostic (D6).
    # Delegates to scripts/calibration_honesty.py; degrades to an advisory WARN without python3.
    CH_DIR=$(cd "$(dirname "$0")" && pwd)
    CH_HELPER="$CH_DIR/calibration_honesty.py"
    if [ "${1:-}" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$CH_HELPER" ]; then python3 "$CH_HELPER" --self-test; exit $?; fi
      echo "Self-test: PASS (degraded — python3 unavailable; calibration-honesty is advisory without it)"; exit 0
    fi
    if command -v python3 >/dev/null 2>&1 && [ -f "$CH_HELPER" ]; then
      if [ $# -lt 1 ]; then echo "Usage: $0 calibration-honesty <run_folder|files...> [--strict] | --self-test"; exit 2; fi
      python3 "$CH_HELPER" calibration-honesty "$@"; exit $?
    fi
    echo "WARN: python3 unavailable — calibration-honesty skipped; check inline that no editorial-letter paragraph renders an uncalibrated SETEC decision-audit band as a verdict (a 'scores in the X band' / 'above the threshold' / 'aggregate score confirms …' claim) without an uncalibrated/provenance-only/advisory qualifier co-present in that paragraph. See docs/calibration-honesty.md."
    exit 0
    ;;

  crosslink)
    # Letter <-> margin cross-links (Annotated-Manuscript Increment 3; docs/annotated-manuscript.md
    # §Increment 3): the symmetric mirror of the annotated copy, pointed at the editorial letter. A
    # crosslink render injects a CriticMarkup back-link span ({>>-> marked-up copy: <id> @ kind:value<<})
    # after each letter `<!-- finding: F-... -->` marker whose finding has a manifest annotation, copying
    # the anchor VERBATIM from the gated manifest. The letter is a "second snapshot": the same reverse
    # transform + two-sided sigil precondition prove no letter mutation. Validates X1 forward link (each
    # margin comment carries (See letter §id)), X2 reverse-link consistency (back-link anchor == manifest,
    # no drift), X3 no dangling either way (no phantom back-link; no missing reverse link), X4 no letter
    # mutation; W1 annotated-but-uncited is advisory (ERROR under --strict, override
    # `<!-- override: crosslink-uncited F-... -->`). Takes a run folder (globs editorial letter + manifest
    # + crosslinked letter) or explicit files. Delegates to scripts/crosslink.py; degrades to advisory
    # WARN without python3. (`crosslink.py render <run_folder>` writes the crosslinked letter.)
    XL_DIR=$(cd "$(dirname "$0")" && pwd)
    XL_HELPER="$XL_DIR/crosslink.py"
    if [ "${1:-}" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$XL_HELPER" ]; then python3 "$XL_HELPER" --self-test; exit $?; fi
      echo "Self-test: PASS (degraded — python3 unavailable; crosslink is advisory without it)"; exit 0
    fi
    if command -v python3 >/dev/null 2>&1 && [ -f "$XL_HELPER" ]; then
      if [ $# -lt 1 ]; then echo "Usage: $0 crosslink <run_folder|files...> [--strict] | --self-test"; exit 2; fi
      python3 "$XL_HELPER" crosslink "$@"; exit $?
    fi
    echo "WARN: python3 unavailable — crosslink skipped; check inline that each letter finding marker has a back-link to the manifest anchor (no drift), no phantom/missing back-links, and deleting every {>> ... <<} span reproduces the letter. See docs/annotated-manuscript.md."
    exit 0
    ;;

  escalation-check)
    # Adaptive Mid-Run Mode Escalation detector (docs/adaptive-mode-escalation.md): a
    # CONDITION-TRIGGERED checkpoint after Tier 1 that compares revealed complexity (POV count,
    # nonlinear timeline, belief/orientation density, Tier-1 finding count from the ledger) against
    # the preflight estimate and recommends escalating the execution mode before Tier 2. The
    # symmetric case: when no trigger fires and every signal is in a 'clearly simple' band, it
    # recommends DE-escalating an over-provisioned expensive mode (hybrid/swarm) down to sequential
    # (conservatively — a missing/malformed signal blocks it). Advisory by default (a recommendation,
    # never automatic); --strict exits 1 on either recommendation. Delegates to
    # scripts/escalation_check.py; degrades to advisory WARN.
    EC_DIR=$(cd "$(dirname "$0")" && pwd)
    EC_HELPER="$EC_DIR/escalation_check.py"
    if [ "${1:-}" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$EC_HELPER" ]; then python3 "$EC_HELPER" --self-test; exit $?; fi
      echo "Self-test: PASS (degraded — python3 unavailable; escalation-check is advisory without it)"; exit 0
    fi
    if command -v python3 >/dev/null 2>&1 && [ -f "$EC_HELPER" ]; then
      if [ $# -lt 1 ]; then echo "Usage: $0 escalation-check <run_folder|files...> [--strict] | --self-test"; exit 2; fi
      python3 "$EC_HELPER" escalation-check "$@"; exit $?
    fi
    echo "WARN: python3 unavailable — escalation-check skipped; evaluate the escalation triggers inline (pov_count>3, nonlinear timeline, belief>5/orientation>3, Tier-1 findings>20). See docs/adaptive-mode-escalation.md."
    exit 0
    ;;

  dispatch-record)
    # Model-Capacity Exploitation M1 — dispatch observability validator (docs/model-capacity-
    # dispatch-log.md). A run that dispatched delegated agents records WHICH model each dispatched
    # step was issued to in the additive `dispatch_log` sidecar array (Diagnostic_State.meta.json) —
    # the join key between model identity and every outcome signal already on disk. PROVENANCE
    # HONESTY (binding): a `dispatch-derived` entry attests the dispatch INSTRUCTION — parent-
    # requested, NOT platform-verified; no host API attests which model actually served the
    # subagent (deliberately weaker than synthesis_coverage's manifest-reconciled V4). Checks:
    # R1 presence (advisory-first; key-ABSENT = pre-adoption grandfather / silent PASS, present-
    # but-[] = a post-adoption recording failure that fires). R2 coverage against the pass-artifact
    # glob family + synthesis-letter globs, per the satisfaction map (pass<N>->Pass N; pass0+1->
    # BOTH Pass0+Pass1; all-passes->every pass artifact AND exclusive; synthesis->letter; deferred
    # ids audit:*/prerequisite:*/refutation recorded-but-not-reconciled); artifact-with-no-entry =
    # FAIL under --strict / WARN otherwise, entry-with-no-artifact = WARN never FAIL. R3 tag
    # vocabulary parsed from the output-structure.md model-tag table (SSoT-by-reference; literal
    # `unknown` is a sanctioned PASS; a ZERO-row table parse EXITS 2 model-tag-table-unparseable,
    # never a vacuous accept-everything). R4 shape (modes/provenance enums, strictly-increasing
    # seq, malformed/dup = FAIL, unknown step kind = WARN; NO mode-based provenance FAIL — a
    # no-shell host legitimately records all-`declared` under execution_mode: sequential). R5
    # escalation cross-check from the log + last_session.execution_mode (at most one mode
    # transition; final entry mode == last_session.execution_mode) — WARN-first. R1/R5 and the R2
    # shrink direction are advisory-first for one release (--strict promotes). `--report
    # <project_dir>` is a read-only cross-run scan (gates nothing) that surfaces the M2 demand
    # signal — quality_risk_override records (the CR-6 detectability fold). Delegates to
    # scripts/dispatch_record.py; degrades to an advisory WARN without python3.
    DR_DIR=$(cd "$(dirname "$0")" && pwd)
    DR_HELPER="$DR_DIR/dispatch_record.py"
    if [ "${1:-}" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$DR_HELPER" ]; then python3 "$DR_HELPER" --self-test; exit $?; fi
      echo "Self-test: PASS (degraded — python3 unavailable; dispatch-record is advisory without it)"; exit 0
    fi
    if command -v python3 >/dev/null 2>&1 && [ -f "$DR_HELPER" ]; then
      if [ $# -lt 1 ]; then echo "Usage: $0 dispatch-record <run_folder> [--strict] | dispatch-record --report <project_dir> | --self-test"; exit 2; fi
      python3 "$DR_HELPER" dispatch-record "$@"; exit $?
    fi
    echo "WARN: python3 unavailable — dispatch-record skipped; verify inline that any dispatch_log in Diagnostic_State.meta.json carries one {seq, step, model_tag, execution_mode, max_turns, provenance} entry per dispatched step (pass<N>/pass0+1/synthesis/all-passes), model_tag is in the output-structure.md table or `unknown`, seq strictly increases, and the final entry's execution_mode matches last_session.execution_mode. See docs/model-capacity-dispatch-log.md."
    exit 0
    ;;

  argument-groundtruth-check)
    # Argument Benchmark ground-truth answer-key validator (docs/argument-benchmark-spec.md
    # §Mechanical validator): GT1-GT8 presence; DC code-namespace resolution; GT2 locus<->code
    # consistency; GT7 warrant verdict (the warrant-verdict enum introduced in GT schema v0.2.0; retired-label/token rejection);
    # GT8 premise-plausibility flags (leading-token parse + flag-type/Firewall check); Check 6 the
    # GT schema v0.3.0 Reliability ledger (per-anchor status + decision-use; gate requires a licensed status;
    # provisional confirm/report-only; low-agreement report-only; exact GT1-GT8 coverage; the
    # stale-heading cross-check that consumes the formerly-dead PROVISIONAL bool); Check 7 the
    # matched-pair provenance fields (Matched-pair member / Paired-with — the leading-token member
    # parse, the clean-side derivation-record + GT2 gates, and slug self-consistency; a deliberate
    # stricter superset of fiction's pairing grammar, absent-both-fields = unpaired legacy no-op).
    # This case also hosts the round-record conformance mode (--round-record <record.md> --fixtures-dir <dir>):
    # every booked ENGINE-fault must cite an anchor whose ledger licenses it (gate: any; confirm:
    # OVER-FIRE only; report: none). And the repair-diff acceptance gate
    # (--repair-diff <broken/fixture.md> <clean/fixture.md> <clean/groundtruth.md>): the clean twin
    # must be the broken fixture with insertions ONLY, mapping 1:1 to the clean key's enumerated
    # repair loci. Delegates to scripts/argument_groundtruth.py; degrades to an advisory WARN without
    # python3 (the GT contract is prose in the template + spec).
    AGT_DIR=$(cd "$(dirname "$0")" && pwd)
    AGT_HELPER="$AGT_DIR/argument_groundtruth.py"
    if [ "${1:-}" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$AGT_HELPER" ]; then python3 "$AGT_HELPER" --self-test; exit $?; fi
      echo "Self-test: PASS (degraded — python3 unavailable; argument-groundtruth-check is advisory without it)"; exit 0
    fi
    if command -v python3 >/dev/null 2>&1 && [ -f "$AGT_HELPER" ]; then
      if [ $# -lt 1 ]; then echo "Usage: $0 argument-groundtruth-check <groundtruth_file> | --round-record <record.md> --fixtures-dir <dir> | --repair-diff <broken/fixture.md> <clean/fixture.md> <clean/groundtruth.md> | --self-test"; exit 2; fi
      python3 "$AGT_HELPER" argument-groundtruth-check "$@"; exit $?
    fi
    echo "WARN: python3 unavailable — argument-groundtruth-check skipped; the GT template + spec define the contract. Install python3 for the mechanical check."
    exit 0
    ;;

  argument-crosswalk-check)
    # Argument-taxonomy layer-boundary crosswalk validator (R4A; docs/adr/0001-argument-layer-boundary.md):
    # wellformedness gate over evals/argument-crosswalk/crosswalk.json — membership completeness against a
    # DERIVED registry set (verdict/flag/FM-A owners imported from argument_groundtruth.py; the 46 DC codes
    # + 8 scheme hints parsed structurally from dialectical-clarity.md — never a 4th hardcoded copy), family
    # well-typing, the closed cardinality enum, the unmapped<->no-targets equivalence, a non-empty rationale
    # on every unmapped row, a provenance locator on every populated target, a global non-injectivity floor,
    # closed external-ref value-spaces, and the OB5/FM-A20 count tripwires. Certifies SHAPE only — mapping
    # correctness is human/Codex-adjudicated (see the ADR firewall). Delegates to scripts/argument_crosswalk.py;
    # degrades to an advisory WARN without python3 (the ADR + README define the contract in prose).
    AXW_DIR=$(cd "$(dirname "$0")" && pwd)
    AXW_HELPER="$AXW_DIR/argument_crosswalk.py"
    if [ "${1:-}" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$AXW_HELPER" ]; then python3 "$AXW_HELPER" --self-test; exit $?; fi
      echo "Self-test: PASS (degraded — python3 unavailable; argument-crosswalk-check is advisory without it)"; exit 0
    fi
    if command -v python3 >/dev/null 2>&1 && [ -f "$AXW_HELPER" ]; then
      python3 "$AXW_HELPER" argument-crosswalk-check "$@"; exit $?
    fi
    echo "WARN: python3 unavailable — argument-crosswalk-check skipped; the ADR + README define the contract. Install python3 for the mechanical check."
    exit 0
    ;;

  argument-aif-export)
    AIF_DIR=$(cd "$(dirname "$0")" && pwd)
    AIF_HELPER="$AIF_DIR/argument_aif.py"
    if [ "${1:-}" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$AIF_HELPER" ]; then python3 "$AIF_HELPER" --self-test; exit $?; fi
      echo "Self-test: PASS (degraded — python3 unavailable; argument-aif is advisory without it)"; exit 0
    fi
    if command -v python3 >/dev/null 2>&1 && [ -f "$AIF_HELPER" ]; then
      python3 "$AIF_HELPER" export "$@"; exit $?
    fi
    echo "WARN: python3 unavailable — argument-aif skipped; docs/argument-aif-export.md defines the contract."
    exit 0
    ;;

  argument-aif-check)
    AIF_DIR=$(cd "$(dirname "$0")" && pwd)
    AIF_HELPER="$AIF_DIR/argument_aif.py"
    if [ "${1:-}" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$AIF_HELPER" ]; then python3 "$AIF_HELPER" --self-test; exit $?; fi
      echo "Self-test: PASS (degraded — python3 unavailable; argument-aif is advisory without it)"; exit 0
    fi
    if command -v python3 >/dev/null 2>&1 && [ -f "$AIF_HELPER" ]; then
      python3 "$AIF_HELPER" check "$@"; exit $?
    fi
    echo "WARN: python3 unavailable — argument-aif skipped; docs/argument-aif-export.md defines the contract."
    exit 0
    ;;

  argument-reconstruction-draft)
    ARD_DIR=$(cd "$(dirname "$0")" && pwd)
    ARD_HELPER="$ARD_DIR/reconstruction_draft.py"
    if [ "${1:-}" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$ARD_HELPER" ]; then python3 "$ARD_HELPER" --self-test; exit $?; fi
      echo "ERROR: argument-reconstruction-draft requires python3 and reconstruction_draft.py" >&2; exit 1
    fi
    if command -v python3 >/dev/null 2>&1 && [ -f "$ARD_HELPER" ]; then
      python3 "$ARD_HELPER" "$@"; exit $?
    fi
    echo "ERROR: argument-reconstruction-draft requires python3 and reconstruction_draft.py" >&2
    exit 1
    ;;

  argument-reconstruction)
    AGR_DIR=$(cd "$(dirname "$0")" && pwd)
    AGR_HELPER="$AGR_DIR/approval_graph.py"
    if [ "${1:-}" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$AGR_HELPER" ]; then python3 "$AGR_HELPER" --self-test; exit $?; fi
      echo "ERROR: argument-reconstruction requires python3 and approval_graph.py" >&2; exit 1
    fi
    if command -v python3 >/dev/null 2>&1 && [ -f "$AGR_HELPER" ]; then
      python3 "$AGR_HELPER" "$@"; exit $?
    fi
    echo "ERROR: argument-reconstruction requires python3 and approval_graph.py" >&2
    exit 1
    ;;

  argument-agd)
    # AGD Move Audit validator (R3A; craft/argument-agd-audit.md): validates an Argument_State
    # §10.9 block — coverage manifest, typed M-records, the total family×challenge×result matrix,
    # the neutrality firewall (candidates only on failed function; DISAPPEARING whitelist), the
    # DERIVED 62-code candidate namespace (DC minus AT1-AT4 via argument_crosswalk's scoped parse,
    # + FM-A1-20), the DISCOUNTING cross-ref contract, and (with --source) normalized-substring
    # Source-anchor resolution. Delegates to scripts/argument_agd.py; degrades to an advisory WARN
    # without python3 (the audit doc defines the contract in prose).
    AGD_DIR=$(cd "$(dirname "$0")" && pwd)
    AGD_HELPER="$AGD_DIR/argument_agd.py"
    if [ "${1:-}" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$AGD_HELPER" ]; then python3 "$AGD_HELPER" --self-test; exit $?; fi
      echo "Self-test: PASS (degraded — python3 unavailable; argument-agd is advisory without it)"; exit 0
    fi
    if command -v python3 >/dev/null 2>&1 && [ -f "$AGD_HELPER" ]; then
      if [ $# -lt 1 ]; then echo "Usage: $0 argument-agd <argument_state.md> [--source <source.md>] [--scan <agd_move_scan.json>] [--strict] | --self-test"; exit 2; fi
      python3 "$AGD_HELPER" argument-agd "$@"; exit $?
    fi
    echo "WARN: python3 unavailable — argument-agd skipped; craft/argument-agd-audit.md defines the contract. Install python3 for the mechanical check."
    exit 0
    ;;

  fiction-groundtruth-check)
    # Fiction Benchmark ground-truth answer-key validator (docs/fiction-benchmark-spec.md
    # §Mechanical validator): FGT1-FGT7 presence; the multi-lane tag discipline (gt_class:C never
    # gates, gate requires deterministic/panel_confirmed, Lane-2 needs a band + alpha_metric);
    # broken-member completeness (plant record, well-shaped locus, defect family, Paired-with sibling);
    # the OPEN-namespace expected-surface shape + family consistency (F-P<n> open by shape/family,
    # CF/SP disjoint cross-artifact ids recognized only for continuity/reveal, the adapted fiction-grammar
    # decoy masks); FGT4 severity tokens (via severity_vocab, presence-delta regime); FGT7 classification.
    # KEY-CONFORMANCE ONLY — never a semantic judge, never scores an engine run. Delegates to
    # scripts/fiction_groundtruth.py; degrades to an advisory WARN without python3 (the GT contract is
    # prose in the template + spec).
    FGT_DIR=$(cd "$(dirname "$0")" && pwd)
    FGT_HELPER="$FGT_DIR/fiction_groundtruth.py"
    if [ "${1:-}" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$FGT_HELPER" ]; then python3 "$FGT_HELPER" --self-test; exit $?; fi
      echo "Self-test: PASS (degraded — python3 unavailable; fiction-groundtruth-check is advisory without it)"; exit 0
    fi
    if command -v python3 >/dev/null 2>&1 && [ -f "$FGT_HELPER" ]; then
      if [ $# -lt 1 ]; then echo "Usage: $0 fiction-groundtruth-check <groundtruth_file> | --self-test"; exit 2; fi
      python3 "$FGT_HELPER" fiction-groundtruth-check "$@"; exit $?
    fi
    echo "WARN: python3 unavailable — fiction-groundtruth-check skipped; the GT template + spec define the contract. Install python3 for the mechanical check."
    exit 0
    ;;

  agreement-alpha)
    # Krippendorff's alpha inter-rater reliability CLI (pure stdlib) — the mechanical half of the
    # Argument/Fiction Benchmark agreement-as-license promotion workflow (docs/argument-benchmark-spec.md
    # §GT schema; the psychometric frame: inter-rater agreement LICENSES a label, it never scores the
    # engine). Computes nominal + ordinal Krippendorff's alpha over a tidy `rater,unit,value` CSV with
    # a >=1000-resample UNIT-level bootstrap 95% CI (Hayes & Krippendorff 2007), a fixed default seed
    # (--seed / --resamples overrides; --resamples may only RAISE the 1000 floor), and the D_e=0 ->
    # alpha=UNDEFINED + WARN degenerate guard. Licensing is on the CI LOWER BOUND (the small-n
    # false-promotion guard), applied by the M2 round, not this tool. No --check-all corpus block:
    # panel ratings live outside git (Dropbox-only), so there is no in-repo ratings fixture to scan.
    # Delegates to scripts/agreement_alpha.py; degrades to an advisory WARN without python3.
    AA_DIR=$(cd "$(dirname "$0")" && pwd)
    AA_HELPER="$AA_DIR/agreement_alpha.py"
    if [ "${1:-}" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$AA_HELPER" ]; then python3 "$AA_HELPER" --self-test; exit $?; fi
      echo "Self-test: PASS (degraded — python3 unavailable; agreement-alpha is advisory without it)"; exit 0
    fi
    if command -v python3 >/dev/null 2>&1 && [ -f "$AA_HELPER" ]; then
      if [ $# -lt 1 ]; then echo "Usage: $0 agreement-alpha <ratings.csv> [--metric nominal|ordinal] [--seed <int>] [--resamples <int>=1000] | --self-test"; exit 2; fi
      python3 "$AA_HELPER" agreement-alpha "$@"; exit $?
    fi
    echo "WARN: python3 unavailable — agreement-alpha skipped; install python3 for the mechanical Krippendorff's-alpha computation. Ratings contract: a rater,unit,value CSV; see docs/argument-benchmark-spec.md."
    exit 0
    ;;

  diagnostic-vocabulary)
    # Diagnostic Vocabulary Mode teaching-aid contract (docs/diagnostic-vocabulary.md): when the
    # Vocabulary Guide declares `<!-- mode: diagnostic-vocabulary -->` (operator:facilitator),
    # enforce V1 Glossary present (>=3 entries), V2 entries defined, V3 >=3 entries grounded in the
    # manuscript, V4 Discussion Prompts (>=3, all questions); W1 author-directed prescription leak is
    # advisory (ERROR under --strict). A file WITHOUT the marker is a no-op pass, so this is safe over
    # any file. Delegates to scripts/diagnostic_vocabulary.py; degrades to an advisory WARN without python3.
    DV_DIR=$(cd "$(dirname "$0")" && pwd)
    DV_HELPER="$DV_DIR/diagnostic_vocabulary.py"
    if [ "${1:-}" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$DV_HELPER" ]; then python3 "$DV_HELPER" --self-test; exit $?; fi
      echo "Self-test: PASS (degraded — python3 unavailable; diagnostic-vocabulary is advisory without it)"; exit 0
    fi
    if command -v python3 >/dev/null 2>&1 && [ -f "$DV_HELPER" ]; then
      if [ $# -lt 1 ]; then echo "Usage: $0 diagnostic-vocabulary <vocab_guide|run_folder> [--strict] | --self-test"; exit 2; fi
      python3 "$DV_HELPER" diagnostic-vocabulary "$@"; exit $?
    fi
    echo "WARN: python3 unavailable — diagnostic-vocabulary skipped; if the file declares diagnostic-vocabulary mode, verify inline that it carries a grounded Glossary (>=3 entries) and a Discussion Prompts section (>=3 questions). See docs/diagnostic-vocabulary.md."
    exit 0
    ;;

  editor-scaffolding)
    # Editor Scaffolding operator-mode presentation contract (docs/editor-scaffolding.md): when
    # the editorial letter declares `<!-- mode: editor-scaffolding -->` (operator:editor),
    # enforce the editor-facing reframe — E1 Editor Brief addressee, E2 What-You-Might-Have-Missed
    # blind-spot section, E3 Intervention Menu (prescription deferred to the human editor),
    # E4 severity vocabulary preserved; W1 author-directed prescription leak is advisory (ERROR
    # under --strict). A letter WITHOUT the marker is a no-op pass, so this is safe over any
    # letter. DUAL-OUTPUT: `editor-scaffolding --dual <editor_letter> <author_letter>` validates
    # one diagnosis emitted as BOTH letters — D1 editor side (E1-E4), D2 author register (no editor
    # marker / no editor-only sections + a Revision Checklist anchor), D3 top-severity-band match.
    # PER-PASS: `editor-scaffolding --per-pass <pass_artifact>` applies the same reframe to an
    # individual PASS artifact (not the letter) — P1 Editor Note addressee, P2 What-You-Might-Have-
    # Missed blind-spot, W1 prescription firewall; a pass has no checklist so E3/E4 have no per-pass
    # analog. Delegates to scripts/editor_scaffolding.py; degrades to an advisory WARN without python3.
    ES_DIR=$(cd "$(dirname "$0")" && pwd)
    ES_HELPER="$ES_DIR/editor_scaffolding.py"
    if [ "${1:-}" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$ES_HELPER" ]; then python3 "$ES_HELPER" --self-test; exit $?; fi
      echo "Self-test: PASS (degraded — python3 unavailable; editor-scaffolding is advisory without it)"; exit 0
    fi
    if command -v python3 >/dev/null 2>&1 && [ -f "$ES_HELPER" ]; then
      if [ $# -lt 1 ]; then echo "Usage: $0 editor-scaffolding <editorial_letter|run_folder> [--strict] | editor-scaffolding --dual <editor_letter> <author_letter> [--strict] | editor-scaffolding --per-pass <pass_artifact> [--strict] | --self-test"; exit 2; fi
      python3 "$ES_HELPER" editor-scaffolding "$@"; exit $?
    fi
    echo "WARN: python3 unavailable — editor-scaffolding skipped; if the letter (or pass artifact) declares editor-scaffolding mode, verify inline that a letter carries an Editor Brief, a 'What You Might Have Missed' section, an Intervention Menu, and surviving severity tokens — or that a --per-pass artifact carries an Editor Note and a 'What You Might Have Missed' section. See docs/editor-scaffolding.md."
    exit 0
    ;;

  results-guide)
    # Results Guide navigation-index integrity (Writer-Question Surface Hardening #5;
    # SKILL.md §Results Guide Artifact). The Results Guide (`*_Results_Guide_*.md`) is the first
    # file after the editorial letter — a plain-language map from each writer question the run
    # produced to the run-folder artifacts behind it. It POINTS, it never DIAGNOSES. One arm, three
    # checks, R2 load-bearing: R1 membership (every `### question` heading is a canonical §3 User
    # Question from pass-dependencies.md — an invented block is the defect; a run that produced only
    # some blocks is legal), R2 referential integrity (LOAD-BEARING — every backtick .md/.json
    # citation resolves to a run-folder file; an un-substituted `[…]` placeholder or a dangling
    # citation ERRORs; `/coach` / `/audit [name]` command tokens are exempt via the extension guard),
    # R3 hygiene (no Must/Should/Could-Fix severity leak, no apodictic:finding block — it must not
    # masquerade as a second letter). Takes a run folder (globs *_Results_Guide_*.md; citations
    # resolve flat) or explicit files (the guide + an optional run-folder dir). R1 degrades to a skip
    # when §3 is unavailable; an unreadable run folder fails closed. Delegates to
    # scripts/results_guide.py; degrades to an advisory WARN without python3.
    RG_DIR=$(cd "$(dirname "$0")" && pwd)
    RG_HELPER="$RG_DIR/results_guide.py"
    if [ "${1:-}" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$RG_HELPER" ]; then python3 "$RG_HELPER" --self-test; exit $?; fi
      echo "Self-test: PASS (degraded — python3 unavailable; results-guide is advisory without it)"; exit 0
    fi
    if command -v python3 >/dev/null 2>&1 && [ -f "$RG_HELPER" ]; then
      if [ $# -lt 1 ]; then echo "Usage: $0 results-guide <run_folder|files...> [--strict] | --self-test"; exit 2; fi
      python3 "$RG_HELPER" results-guide "$@"; exit $?
    fi
    echo "WARN: python3 unavailable — results-guide skipped; perform the citation trace inline: every backtick .md/.json filename in the guide resolves to a run-folder file (no un-substituted [placeholder]); every '### question' heading is a §3 User Question; no Must/Should/Could-Fix token; no apodictic:finding block. See SKILL.md §Results Guide Artifact."
    exit 0
    ;;

  position-pair-register)
    # Position-Pair Register consumer firewall (stance-consistency PR 2; SPEC v4+v5). The consumer
    # renders SETEC's `position_pair_register` envelope — passage PAIRS that address the SAME question,
    # relation-free, in document order — to a markdown register and presents it. This arm carries the
    # no-relation posture MECHANICALLY over three inputs (the register artifact, the JSON envelope, and
    # the manuscript the consumer holds): Q1 a two-layer recursive banned-KEY walk over the envelope
    # (relation keys never legitimate anywhere; generic verdict keys scoped to results.pairs — KEYS
    # only, since claim_license VALUES legitimately carry relation words), Q2 a verbatim re-check of
    # every quote against the manuscript with the F1 punctuation-fold (a fabricated/paraphrased quote
    # DROPS the pair with an inspectable log line + a counted pairs_dropped_quote_mismatch disclosure +
    # WARN; --strict promotes to FAIL — a drop is a disclosure, not an error), the A3/X-gate (no
    # Must/Should/Could-Fix token, no apodictic:finding block — same content_advisory firewall), the F5
    # presentation-prose gate (the consumer's OWN framing text carries no relation vocabulary; the
    # `>`-blockquote evidence lines are exempt — the author's quotes may carry such words), and a
    # document-order check (the artifact must present pairs in envelope order — re-ranking is a
    # judgment channel the posture forbids). Explicit file args only (no run-folder resolution).
    # Delegates to scripts/position_pair_gates.py; degrades to an advisory WARN without python3.
    PPR_DIR=$(cd "$(dirname "$0")" && pwd)
    PPR_HELPER="$PPR_DIR/position_pair_gates.py"
    if [ "${1:-}" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$PPR_HELPER" ]; then python3 "$PPR_HELPER" --self-test; exit $?; fi
      echo "Self-test: PASS (degraded — python3 unavailable; position-pair-register is advisory without it)"; exit 0
    fi
    if command -v python3 >/dev/null 2>&1 && [ -f "$PPR_HELPER" ]; then
      if [ $# -lt 3 ]; then echo "Usage: $0 position-pair-register <artifact.md> <envelope.json> <manuscript> [--strict] | --self-test"; exit 2; fi
      python3 "$PPR_HELPER" position-pair-register "$@"; exit $?
    fi
    echo "WARN: python3 unavailable — position-pair-register skipped; verify inline that the envelope carries no relation/verdict KEY (contradiction/opposes/conflict/tension/stance/… anywhere; verdict/label/score/relation inside results.pairs), every quote is a verbatim substring of the manuscript, the register carries no Must/Should/Could-Fix token and no apodictic:finding block, its framing prose (outside the '>' quote lines) carries no relation vocabulary, and the pairs are in document order. See position-pair-register.md."
    exit 0
    ;;

  stance-calibration)
    # Argument-register / rhetorical-stance Triage record gate. Shape + exact Argument_State
    # joins only; the validator never decides whether a move is rhetorically earned.
    SC_DIR=$(cd "$(dirname "$0")" && pwd)
    SC_HELPER="$SC_DIR/stance_calibration.py"
    if [ "${1:-}" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$SC_HELPER" ]; then python3 "$SC_HELPER" --self-test; exit $?; fi
      echo "Self-test: PASS (degraded — python3 unavailable; stance-calibration is advisory without it)"; exit 0
    fi
    if command -v python3 >/dev/null 2>&1 && [ -f "$SC_HELPER" ]; then
      if [ $# -lt 3 ]; then echo "Usage: $0 stance-calibration <findings_ledger.md> --argument-state <Argument_State.md> | --self-test"; exit 2; fi
      python3 "$SC_HELPER" stance-calibration "$@"; exit $?
    fi
    echo "WARN: python3 unavailable — stance-calibration skipped; verify the optional register/stance/calibration_effect fields and exact cash_out_ref joins inline."
    exit 0
    ;;

  validator-conventions)
    # Fleet meta-linter (docs/validator-conventions.md): a validator that validates the validators.
    # M1 every AGG_VALIDATORS entry has a dispatcher case that handles --self-test; M2 no validator
    # classifies inputs by a raw marker scan/membership op on a literal apodictic:<type> (resolvers
    # must classify on parsed blocks — the _has_block / art.parse_blocks idiom — the signature
    # anti-pattern of the 2026-06-20 resolver-hardening sweep); M3 the advertised count is DERIVED from
    # AGG_VALIDATORS (never hand-typed); M4 every *.schema.json filename stem in the resolved schema dir
    # is referenced by some validator (degrades to WARN if the resolver is unavailable); M5 no validator
    # detects an override marker by a bare "<!-- override:" substring scan OR a local compiled/inline
    # override regex (the override-marker sibling of M2 — use override_marker.has_override /
    # override_targets / override_payloads / the _has_override bash helper); M6 no validator builds a
    # local code-span / fence stripper (delegate to override_marker.strip_code_spans). Mechanizes the
    # conventions that manual review left to drift. Reads validate.sh + the sibling *.py from its own
    # dir. Delegates to scripts/meta_lint.py; degrades to an advisory WARN without python3.
    MTL_DIR=$(cd "$(dirname "$0")" && pwd)
    MTL_HELPER="$MTL_DIR/meta_lint.py"
    if [ "${1:-}" = "--self-test" ]; then
      # Bash-side regression for the shared `_has_override` helper (M5's companion: M5 GATES the
      # anti-pattern, this proves the hardened REPLACEMENT). The Python override_marker.has_override is
      # covered by each validator's --self-test (severity-floor / quality-risk / etc. decoy+suffix
      # cases); this covers the bash arm — which the Python self-tests never reach — including the
      # fenced-block decoy (Group 4: bash used to be wrongly MORE permissive there).
      HO_R=0; HO_S="severity-floor-weak-axis"
      _ho_case() { # <label> <expect found|miss> <body>
        if printf '%b' "$3" | _has_override "$HO_S"; then _g=found; else _g=miss; fi
        if [ "$_g" = "$2" ]; then echo "  ho_$1: OK ($_g)"; else echo "  ho_$1: FAIL (got $_g want $2)"; HO_R=1; fi
      }
      _ho_case genuine_emdash  found "<!-- override: $HO_S — reason -->\n"
      _ho_case genuine_noreason found "<!-- override: $HO_S -->\n"
      _ho_case nospace_dash    found "<!-- override: ${HO_S}—reason -->\n"
      _ho_case flex_whitespace found "<!--  override:  $HO_S  -->\n"
      _ho_case suffix_collision miss "<!-- override: $HO_S-but-not-really — decoy -->\n"
      _ho_case inline_codespan_decoy miss "Use \`<!-- override: $HO_S -->\` here.\n"
      _ho_case fenced_block_decoy miss "before\n\`\`\`\n<!-- override: $HO_S -->\n\`\`\`\nafter\n"
      _ho_case indented_fenced_decoy miss "x\n    \`\`\`\n<!-- override: $HO_S -->\n    \`\`\`\ny\n"
      _ho_case multi_backtick_decoy miss "\`\`<!-- override: $HO_S -->\`\`\n"
      _ho_case tilde_fence_decoy miss "before\n~~~\n<!-- override: $HO_S -->\n~~~\nafter\n"
      _ho_case tilde_with_backtick_line_decoy miss "~~~\n\`\`\`\n<!-- override: $HO_S -->\n\`\`\`\n~~~\n"
      _ho_case multiline_inline_decoy miss "a \`open\n<!-- override: $HO_S -->\nclose\` b\n"
      if [ "$HO_R" -ne 0 ]; then echo "Self-test: FAIL (_has_override bash regression)"; exit 1; fi
      if command -v python3 >/dev/null 2>&1 && [ -f "$MTL_HELPER" ]; then python3 "$MTL_HELPER" --self-test; exit $?; fi
      echo "Self-test: PASS (degraded — python3 unavailable; validator-conventions is advisory without it; _has_override bash regression passed)"; exit 0
    fi
    if command -v python3 >/dev/null 2>&1 && [ -f "$MTL_HELPER" ]; then
      python3 "$MTL_HELPER" validator-conventions "$@"; exit $?
    fi
    echo "WARN: python3 unavailable — validator-conventions skipped; check inline that every AGG validator has a --self-test dispatcher case, resolvers classify on parsed blocks (no raw apodictic:<type> marker scan), the count is derived, no schema is orphaned, and no gate detects an override by a bare \"<!-- override:\" substring (use the _has_override helper). See docs/validator-conventions.md."
    exit 0
    ;;

  argument-carve-behavior-preservation)
    # Carve-equivalence SMOKE gate (Workstream A, §2.4): a lightweight regression guard that the
    # nonfiction-argument-engine modularization did not break the MECHANICAL resolvers (deterministic
    # Python only — the LLM editorial layer is non-deterministic and is not tested here).
    # Re-runs two resolvers on fixed pre-carve fixtures and diffs each SUMMARY line against a committed
    # golden: (1) audit-signal-propagation on argument-editorial-letter.md + argument-findings-ledger.md;
    # (2) decision-layer-check (Argument-DE class) on argument-editorial-letter.md.
    # SCOPE / HONESTY: this asserts the resolvers still classify the argument fixture as Argument-DE and
    # do not regress to error post-carve. It is NOT the full §2.4 field-level diff (no row-by-row
    # Findings-Ledger id/severity/evidence_refs diff, no annotation anchor-map diff); the propagation
    # summary line is invariant on this fixture, so treat this as a smoke check, not the proof.
    # The AUTHORITATIVE behavior-preservation guarantees (which have teeth) are elsewhere:
    #   - `audit-signal-propagation --check-registry` — all 45 signal-emitting audits still have §4e rows
    #     (FAILS if the split fragment is dropped); and
    #   - the byte-identical §4e extraction proof in evals/fixtures/argument-carve/4e-before-after.diff.
    # "Identical" = both summary diffs empty (exit 0). Skips when evals/ is absent (repo-only gate);
    # fails if a fixture is missing within a present evals/ or a golden drifts.
    # Pure shell + python3 (via validate.sh sub-calls). No helper script.
    ACB_DIR=$(cd "$(dirname "$0")" && pwd)
    # The argument-carve fixtures live only at repo root (evals/ is not shipped to host workspaces and
    # is not mirrored under plugins/apodictic/). Resolve from EITHER validate.sh mirror copy:
    # ../../../evals (plugins/apodictic/scripts/) or ../evals (root scripts/); resolve-and-skip when
    # absent rather than fail — matching the argument-groundtruth-check convention above.
    ACB_FIXTURE_DIR=""
    for ACB_CAND in "$ACB_DIR/../../../evals/fixtures/argument-carve/precarve" "$ACB_DIR/../evals/fixtures/argument-carve/precarve"; do
      if [ -d "$ACB_CAND" ]; then ACB_FIXTURE_DIR="$ACB_CAND"; break; fi
    done
    if [ -z "$ACB_FIXTURE_DIR" ]; then
      if [ "${1:-}" = "--self-test" ]; then
        echo "  fixture_present: SKIP (evals/ not present — repo-only gate)"; echo "Self-test: PASS"
      else
        echo "argument-carve-behavior-preservation: SKIP (evals/ not present — repo-only gate)"
      fi
      exit 0
    fi
    if [ "${1:-}" = "--self-test" ]; then
      ACB_R=0
      # Self-test: verify the fixture files exist and the validators produce the golden outputs.
      ACB_LETTER="$ACB_FIXTURE_DIR/argument-editorial-letter.md"
      ACB_LEDGER="$ACB_FIXTURE_DIR/argument-findings-ledger.md"
      ACB_PROP_GOLDEN="$ACB_FIXTURE_DIR/propagation-output.txt"
      ACB_DL_GOLDEN="$ACB_FIXTURE_DIR/decision-layer-output.txt"
      for ACB_F in "$ACB_LETTER" "$ACB_LEDGER" "$ACB_PROP_GOLDEN" "$ACB_DL_GOLDEN"; do
        if [ ! -f "$ACB_F" ]; then echo "  fixture_present: FAIL (missing: $ACB_F)"; ACB_R=1; fi
      done
      if [ "$ACB_R" -eq 0 ]; then
        echo "  fixture_present: OK (4 fixture files found)"
        # Run propagation check and diff against golden
        ACB_PROP_OUT=$("$0" audit-signal-propagation "$ACB_LETTER" "$ACB_LEDGER" 2>/dev/null | tail -1)
        ACB_PROP_EXPECTED=$(cat "$ACB_PROP_GOLDEN")
        if [ "$ACB_PROP_OUT" = "$ACB_PROP_EXPECTED" ]; then
          echo "  propagation_golden: OK"
        else
          echo "  propagation_golden: FAIL"
          echo "    expected: $ACB_PROP_EXPECTED"
          echo "    got:      $ACB_PROP_OUT"
          ACB_R=1
        fi
        # Run decision-layer-check and diff against golden
        ACB_DL_OUT=$("$0" decision-layer-check "$ACB_LETTER" 2>/dev/null | tail -1)
        ACB_DL_EXPECTED=$(cat "$ACB_DL_GOLDEN")
        if [ "$ACB_DL_OUT" = "$ACB_DL_EXPECTED" ]; then
          echo "  decision_layer_golden: OK"
        else
          echo "  decision_layer_golden: FAIL"
          echo "    expected: $ACB_DL_EXPECTED"
          echo "    got:      $ACB_DL_OUT"
          ACB_R=1
        fi
      fi
      if [ "$ACB_R" -eq 0 ]; then echo "Self-test: PASS"; exit 0; else echo "Self-test: FAIL"; exit 1; fi
    fi
    # Normal run (no args): runs both mechanical validators on the pre-carve fixture and diffs
    # outputs against the committed goldens. Usage as a gate: exit 0 = behavior preserved; exit 1 = drift.
    ACB_LETTER="$ACB_FIXTURE_DIR/argument-editorial-letter.md"
    ACB_LEDGER="$ACB_FIXTURE_DIR/argument-findings-ledger.md"
    ACB_PROP_GOLDEN="$ACB_FIXTURE_DIR/propagation-output.txt"
    ACB_DL_GOLDEN="$ACB_FIXTURE_DIR/decision-layer-output.txt"
    ACB_R=0
    for ACB_F in "$ACB_LETTER" "$ACB_LEDGER" "$ACB_PROP_GOLDEN" "$ACB_DL_GOLDEN"; do
      if [ ! -f "$ACB_F" ]; then
        echo "ERROR: argument-carve-behavior-preservation fixture missing: $ACB_F"
        exit 1
      fi
    done
    ACB_PROP_OUT=$("$0" audit-signal-propagation "$ACB_LETTER" "$ACB_LEDGER" 2>/dev/null | tail -1)
    ACB_PROP_EXPECTED=$(cat "$ACB_PROP_GOLDEN")
    if [ "$ACB_PROP_OUT" != "$ACB_PROP_EXPECTED" ]; then
      echo "ERROR: argument-carve-behavior-preservation: audit-signal-propagation output drifted from golden"
      echo "  expected: $ACB_PROP_EXPECTED"
      echo "  got:      $ACB_PROP_OUT"
      ACB_R=1
    fi
    ACB_DL_OUT=$("$0" decision-layer-check "$ACB_LETTER" 2>/dev/null | tail -1)
    ACB_DL_EXPECTED=$(cat "$ACB_DL_GOLDEN")
    if [ "$ACB_DL_OUT" != "$ACB_DL_EXPECTED" ]; then
      echo "ERROR: argument-carve-behavior-preservation: decision-layer-check output drifted from golden"
      echo "  expected: $ACB_DL_EXPECTED"
      echo "  got:      $ACB_DL_OUT"
      ACB_R=1
    fi
    if [ "$ACB_R" -eq 0 ]; then
      echo "argument-carve-behavior-preservation: PASS (smoke: resolvers still classify the argument fixture as Argument-DE post-carve; authoritative guarantee = audit-signal-propagation --check-registry + the byte-identical §4e diff)"
      exit 0
    fi
    echo "argument-carve-behavior-preservation: FAIL"
    exit 1
    ;;

  *)
    echo "Unknown command: $COMMAND"
    usage
    ;;
esac
