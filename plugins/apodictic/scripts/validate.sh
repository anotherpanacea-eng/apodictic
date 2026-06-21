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
#   author-facing-lint <editorial_letter_file>
#       ADVISORY (warn-only) lint of author-facing language per
#       core-editor/references/output-policy.md §Author-Facing Language.
#       Surfaces framework shorthand — pass codes (Pass 11F), [.. CONFIDENCE]
#       tags, QF-/CR-/FM- finding codes, P0-P5 tier labels — used as an
#       un-glossed PRIMARY LABEL in the synthesis body. Appendices are exempt;
#       a code glossed inline on first use ("plain language (CODE)" or
#       "CODE (gloss)") is exempt; only the first use of each code is judged.
#       Every hit is a WARN — the arm NEVER fails the build (exit 0); promote to
#       a gate once proven quiet. Body override marker:
#       <!-- override: author-facing-lint -->. Pass --self-test for built-in cases.
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
#   structured-findings <file> [<file>...]
#       Validate embedded apodictic:* JSON blocks (apodictic.finding.v1,
#       audit_trigger.v1, readiness.v1) in ledger/letter markdown and the
#       Diagnostic_State.meta.json sidecar (findings[] severities must tally to
#       triage_summary). Delegates to scripts/structured_findings.py (real JSON
#       parser); degrades to a presence check without python3. Pass --self-test
#       for built-in cases.
#
#   softness-check <editorial_letter> <findings_ledger>
#       Deficit-Lock softness gate (Phase 4). Compares the delivered letter
#       against the Triage-locked apodictic.finding.v1 findings in the ledger;
#       ERROR on an unmarked downgrade/drop of a locked Must-Fix/Should-Fix,
#       WARN on hedged delivery. Body-only override marker:
#       <!-- override: softness-downgrade — <rationale> -->. Weak-axis coherence
#       stays in severity-floor. Delegates to scripts/honesty_check.py.
#
#   deficit-lock <findings_ledger>
#       Verify the Deficit Lock was recorded structurally (ledger carries
#       apodictic.finding.v1 locks). Delegates to honesty_check.py. Pass
#       --self-test for built-in cases.
#
# Exit codes:
#   0 — all checks pass
#   1 — validation failure (details on stdout)
#   2 — usage error

set -euo pipefail

# Single source of truth for the self-testable validator set. Every displayed count below is
# DERIVED from this list (AGG_COUNT) — never hard-code the number (a PR adding a validator edits
# only this line, so the count strings can't go stale or collide on merge).
AGG_VALIDATORS="contract-hash contract-check ledger-check artifact-names synthesis-sections tone-check state-lines severity-floor audit-signal-propagation underdiagnosis-triggers ledger-consolidation decision-layer-check author-facing-lint quality-risk-triggers timeline-diff timeline-arithmetic timeline-anchor-conflict audit-tier-criterion argument-recon-prerequisite structured-findings softness-check deficit-lock artifacts-schema gate gate-state finding-trace escalation-check feedback-triage editor-scaffolding diagnostic-vocabulary retcon-plan state-card-diff regression-diff legal-risk promise-contract continuity-bible world-bible intake-interview author-fingerprint content-advisory persona-divergence argument-spine scene-ethics argument-groundtruth-check registry-check lifecycle-node reader-instrument manuscript-viz annotated-manuscript crosslink reanchor obsidian-export html-export docx-export check-mirror"
# shellcheck disable=SC2086  # intentional word-splitting to count list entries
AGG_COUNT=$(set -- $AGG_VALIDATORS; echo $#)

usage() {
  echo "Usage: $0 <command> [args...]"
  echo "Commands: contract-hash, contract-check, ledger-check, artifact-names, synthesis-sections, tone-check, state-lines, severity-floor, audit-signal-propagation, underdiagnosis-triggers, ledger-consolidation, decision-layer-check, author-facing-lint, quality-risk-triggers, timeline-diff, timeline-arithmetic, timeline-anchor-conflict, audit-tier-criterion, argument-recon-prerequisite, structured-findings, softness-check, deficit-lock, artifacts-schema, gate, finding-trace, feedback-triage, editor-scaffolding, diagnostic-vocabulary, retcon-plan, state-card-diff, regression-diff, legal-risk, promise-contract, continuity-bible, world-bible, intake-interview, author-fingerprint, content-advisory, persona-divergence, argument-spine, scene-ethics, argument-groundtruth-check, registry-check, lifecycle-node, reader-instrument, manuscript-viz, annotated-manuscript, crosslink, reanchor, obsidian-export, html-export, docx-export, check-mirror"
  echo "Aggregate: --self-test-all (runs --self-test on all $AGG_COUNT self-testable validators; exit 0 only if every validator's self-test passes)"
  echo "Aggregate: --check-all (runs --self-test-all PLUS real-file invariants: audit-signal-propagation --check-registry, structured-findings on the shipped templates, audit-tier-criterion vs the real pass-dependencies.md, the ported letter/timeline validators vs the canonical worked examples (incl. underdiagnosis-triggers + ledger-consolidation), finding-trace + softness-check + deficit-lock vs the canonical example ledger<->letter pair (both directions), feedback-triage vs the canonical example Feedback Triage, editor-scaffolding + decision-layer-check + severity-floor vs the canonical scaffolded editorial letter, diagnostic-vocabulary vs the canonical Vocabulary Guide, retcon-plan vs the canonical Retcon Plan, state-card-diff vs the canonical State Card, regression-diff vs the paired two-round example run folders (round linkage + the recurrence / quiet-chapter candidates under --strict), legal-risk vs the canonical Legal Risk Register, promise-contract vs the canonical Promise-Contract Fidelity example (two-sided-ref integrity P1, copy typing P2, the disclosing-synopsis-does-not-raise-PCF2 negative P3, and a clean firewall substring scan W1), continuity-bible vs the canonical Continuity Bible example + its Timeline (C1 schema, C2 locus shape, C3 contradiction integrity, a clean C4 chronology-consume + W1 coverage under --strict), world-bible vs the canonical Worldbuilding Bible example (W1 schema + closed-key, WD unique ids, WB-R1 rule consistency, WB-C1/WB-C2 cost accounting, WB-G1 distance within a unit class, WB-G2 chronology cycle + anchor-drift, and the WF surface-don't-resolve firewall scan — clean under --strict with the staged contradictions overridden), intake-interview vs the canonical Intake Interview example + its Ledger (I1 schema, I2 no-contract-dup, I3 grounded ambiguity via ref + source_note, I4 calibrate-not-suppress under --strict), author-fingerprint vs the canonical Author Voice Profile (F1 schema, F2 provenance, F3 same-register comparison, F4 descriptive-not-prescriptive, clean W1/W2 under --strict), content-advisory vs the canonical Content Advisory (A1 schema, A2 locus shape, A3 no-severity-leak, descriptive W1, opt-in W2 under --strict), persona-divergence vs the canonical Persona Divergence Map + its Ledger (D1 schema incl. nested experiences enum, D2 grounded prediction, D3 target-severity anchoring, D4 anti-fabrication, D5 closed-key persona under --strict), argument-spine vs the canonical pre-draft Argument_State + the three genre-profiled Argument_States (Increment 5: B1-B4 + W4 over grant / academic / pitch, --strict), scene-ethics vs the canonical Scene-Ethics Plan, reader-instrument vs the canonical Beta-Reader Instrument + paired uncertainty ledger, manuscript-viz vs the canonical Structure Map manifest + its Timeline/Ledger sources, annotated-manuscript vs the canonical annotated-manuscript fixture (snapshot + manifest + annotated copy + Ledger/Timeline), crosslink vs the canonical letter + crosslinked letter + manifest, the producer chain (build -> A1-A6 -> render -> X1-X4 on a temp copy of the canonical inputs, asserting the fresh build is byte-identical to the committed fixture), reanchor vs the canonical manifest re-anchored onto a revised-draft snapshot (held / moved / vanished / ambiguous / not-re-anchorable; RA1-RA3 + W1/W2 under --strict), obsidian-export vs the canonical manifest projected to native footnotes — copy + Inc-2 letter (O1 round-trip + O2 footnote resolution + O3 comment fidelity + O4 link resolution + O5 letter prose fidelity, asserting both fresh Obsidian outputs are byte-identical to the committed obsidian/ fixtures), html-export vs the canonical manifest projected to a self-contained read-only HTML (H1 round-trip + H2 anchor resolution + H3 comment fidelity, asserting the fresh html/ export is byte-identical to the committed fixture), docx-export vs the canonical manifest projected to a .docx with anchored comments (D1 artifact integrity + D2 text round-trip + D3 comment resolution, asserting the fresh byte-deterministic docx/ export is byte-identical to the committed fixture), and the run-folder validators (gate-state, escalation-check, argument-recon-prerequisite, and the gate engine on a temp copy) vs the canonical example run folder, plus check-mirror — scripts/ <-> plugins/apodictic/scripts/ byte-identical for the mirrored set)"
  exit 2
}

if [ $# -lt 1 ]; then usage; fi

# Aggregate self-test dispatcher (v1.8.4). Runs --self-test on every
# self-testable validator and exits 0 only if every per-validator
# self-test exits 0. Added per Codex P2 finding: the E1 final report
# referred to an aggregate command that did not exist; this closes the
# documentation-vs-implementation mismatch and simplifies CI invocation.
# The seven pure-utility commands (contract-hash, contract-check, ledger-check,
# artifact-names, synthesis-sections, tone-check, state-lines) now carry
# fixture-driven self-tests too (Validator Architecture Hardening — they
# previously had none), so every command in the suite is exercised here.
if [ "$1" = "--self-test-all" ]; then
  AGG_FAIL=0
  AGG_PASS_COUNT=0
  AGG_FAIL_COUNT=0
  echo "Aggregate self-test dispatcher (v1.8.4) — running --self-test on all $AGG_COUNT validators:"
  for v in $AGG_VALIDATORS; do
    if "$0" "$v" --self-test >/dev/null 2>&1; then
      echo "  $v: PASS"
      AGG_PASS_COUNT=$((AGG_PASS_COUNT + 1))
    else
      echo "  $v: FAIL"
      AGG_FAIL_COUNT=$((AGG_FAIL_COUNT + 1))
      AGG_FAIL=1
    fi
  done
  echo ""
  if [ "$AGG_FAIL" -eq 0 ]; then
    echo "Aggregate self-test: PASS ($AGG_PASS_COUNT/$AGG_COUNT validators)"
    exit 0
  else
    echo "Aggregate self-test: FAIL ($AGG_FAIL_COUNT/$AGG_COUNT validators failed; rerun individually with --self-test for details)"
    exit 1
  fi
fi

# Standard verification path (Phase 3): hermetic self-tests PLUS the real-file
# invariants that --self-test-all (synthetic fixtures only) does not cover — the
# audit-signal-propagation registry-vs-§4e check and structured-findings
# validation of the shipped artifact templates. Closes the gap where a future
# change could pass --self-test-all while breaking a real-file invariant.
if [ "$1" = "--check-all" ]; then
  CA_SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
  CA_FAIL=0
  echo "== --self-test-all =="
  "$0" --self-test-all || CA_FAIL=1
  echo ""
  echo "== audit-signal-propagation --check-registry (real registry vs §4e) =="
  "$0" audit-signal-propagation --check-registry || CA_FAIL=1
  echo ""
  echo "== structured-findings (shipped artifact templates) =="
  CA_DONE=0
  for base in "$CA_SCRIPT_DIR/../skills/core-editor/references" "$CA_SCRIPT_DIR/../plugins/apodictic/skills/core-editor/references"; do
    if [ -f "$base/diagnostic-state-meta-template.json" ]; then
      "$0" structured-findings "$base/diagnostic-state-meta-template.json" "$base/findings-ledger-format.md" || CA_FAIL=1
      CA_DONE=1
      break
    fi
  done
  [ "$CA_DONE" -eq 0 ] && { echo "ERROR: could not locate reference templates for structured-findings — --check-all cannot verify the real-file invariant"; CA_FAIL=1; }
  echo ""

  # Canonical-framework validator runs (Inc.6 / Track B). Resolve the references dir once,
  # then run the ported validators against the actual shipped framework files and the
  # canonical worked examples, so a drift in pass-dependencies.md tiers, the letter contracts,
  # or the Timeline schema is caught at release time (not only against synthetic fixtures).
  CA_BASE=""
  for base in "$CA_SCRIPT_DIR/../skills/core-editor/references" "$CA_SCRIPT_DIR/../plugins/apodictic/skills/core-editor/references"; do
    if [ -d "$base" ]; then CA_BASE="$base"; break; fi
  done
  if [ -z "$CA_BASE" ]; then
    echo "ERROR: could not locate core-editor/references for canonical validator runs"; CA_FAIL=1
  else
    echo "== audit-tier-criterion (real pass-dependencies.md) =="
    if [ -f "$CA_BASE/pass-dependencies.md" ]; then
      "$0" audit-tier-criterion "$CA_BASE/pass-dependencies.md" || CA_FAIL=1
    else
      echo "ERROR: $CA_BASE/pass-dependencies.md not found"; CA_FAIL=1
    fi
    echo ""
    echo "== canonical editorial letter (decision-layer-check, audit-signal-propagation, severity-floor, structured-findings, underdiagnosis-triggers, ledger-consolidation) =="
    if [ -f "$CA_BASE/example-editorial-letter.md" ]; then
      "$0" decision-layer-check "$CA_BASE/example-editorial-letter.md" || CA_FAIL=1
      "$0" audit-signal-propagation "$CA_BASE/example-editorial-letter.md" || CA_FAIL=1
      "$0" severity-floor "$CA_BASE/example-editorial-letter.md" || CA_FAIL=1
      "$0" structured-findings "$CA_BASE/example-editorial-letter.md" || CA_FAIL=1
      "$0" underdiagnosis-triggers "$CA_BASE/example-editorial-letter.md" || CA_FAIL=1
      "$0" ledger-consolidation "$CA_BASE/example-editorial-letter.md" || CA_FAIL=1
    else
      echo "ERROR: $CA_BASE/example-editorial-letter.md not found"; CA_FAIL=1
    fi
    echo ""
    echo "== canonical scaffolded letter (editor-scaffolding + decision-layer-check + severity-floor compose) =="
    if [ -f "$CA_BASE/example-editorial-letter-scaffolded.md" ]; then
      "$0" editor-scaffolding "$CA_BASE/example-editorial-letter-scaffolded.md" || CA_FAIL=1
      "$0" decision-layer-check "$CA_BASE/example-editorial-letter-scaffolded.md" || CA_FAIL=1
      "$0" severity-floor "$CA_BASE/example-editorial-letter-scaffolded.md" || CA_FAIL=1
    else
      echo "ERROR: $CA_BASE/example-editorial-letter-scaffolded.md not found"; CA_FAIL=1
    fi
    echo ""
    echo "== canonical Vocabulary Guide (diagnostic-vocabulary: glossary grounding + question framing) =="
    if [ -f "$CA_BASE/example-vocabulary-guide.md" ]; then
      "$0" diagnostic-vocabulary "$CA_BASE/example-vocabulary-guide.md" || CA_FAIL=1
    else
      echo "ERROR: $CA_BASE/example-vocabulary-guide.md not found"; CA_FAIL=1
    fi
    echo ""
    echo "== canonical example ledger <-> letter (both directions: finding-trace forward refs + softness-check reverse delivery; deficit-lock structured locks) =="
    if [ -f "$CA_BASE/example-findings-ledger.md" ]; then
      "$0" finding-trace "$CA_BASE/example-findings-ledger.md" "$CA_BASE/example-editorial-letter.md" || CA_FAIL=1
      "$0" softness-check "$CA_BASE/example-editorial-letter.md" "$CA_BASE/example-findings-ledger.md" || CA_FAIL=1
      "$0" deficit-lock "$CA_BASE/example-findings-ledger.md" || CA_FAIL=1
    else
      echo "ERROR: $CA_BASE/example-findings-ledger.md not found"; CA_FAIL=1
    fi
    echo ""
    echo "== canonical Feedback Triage (feedback-triage: contract + conflict integrity) =="
    if [ -f "$CA_BASE/example-feedback-triage.md" ]; then
      "$0" feedback-triage "$CA_BASE/example-feedback-triage.md" || CA_FAIL=1
    else
      echo "ERROR: $CA_BASE/example-feedback-triage.md not found"; CA_FAIL=1
    fi
    echo ""
    echo "== canonical Retcon Plan (retcon-plan: commitment-budget + fair-play + target integrity + ranked selection) =="
    if [ -f "$CA_BASE/example-retcon-plan.md" ]; then
      "$0" retcon-plan "$CA_BASE/example-retcon-plan.md" || CA_FAIL=1
    else
      echo "ERROR: $CA_BASE/example-retcon-plan.md not found"; CA_FAIL=1
    fi
    echo ""
    echo "== canonical Legal Risk Register (legal-risk: contract + disclaimer gate + flag-don't-adjudicate) =="
    if [ -f "$CA_BASE/example-legal-risk-register.md" ]; then
      "$0" legal-risk "$CA_BASE/example-legal-risk-register.md" || CA_FAIL=1
    else
      echo "ERROR: $CA_BASE/example-legal-risk-register.md not found"; CA_FAIL=1
    fi
    echo ""
    echo "== canonical Promise-Contract Fidelity (promise-contract: two-sided gap P1 + copy typing P2 + reveal form gate P3 + firewall W1) =="
    if [ -f "$CA_BASE/example-promise-contract.md" ]; then
      "$0" promise-contract "$CA_BASE/example-promise-contract.md" || CA_FAIL=1
    else
      echo "ERROR: $CA_BASE/example-promise-contract.md not found"; CA_FAIL=1
    fi
    echo ""
    echo "== canonical Continuity Bible (continuity-bible: schema C1 + locus shape C2 + contradiction integrity C3 + clean chronology-consume C4 + coverage W1, paired with the Timeline, under --strict) =="
    if [ -f "$CA_BASE/example-continuity-bible.md" ] && [ -f "$CA_BASE/example-timeline.md" ]; then
      "$0" continuity-bible "$CA_BASE/example-continuity-bible.md" "$CA_BASE/example-timeline.md" --strict || CA_FAIL=1
    else
      echo "ERROR: $CA_BASE/example-continuity-bible.md or example-timeline.md not found"; CA_FAIL=1
    fi
    echo ""
    echo "== canonical Intake Interview (intake-interview: schema I1 + no-contract-dup I2 + grounded ambiguity I3 (ref + source_note) + calibrate-not-suppress I4, paired with the Ledger, under --strict) =="
    if [ -f "$CA_BASE/example-intake-interview.md" ] && [ -f "$CA_BASE/example-intake-interview-ledger.md" ]; then
      "$0" intake-interview "$CA_BASE/example-intake-interview.md" "$CA_BASE/example-intake-interview-ledger.md" --strict || CA_FAIL=1
    else
      echo "ERROR: $CA_BASE/example-intake-interview.md or example-intake-interview-ledger.md not found"; CA_FAIL=1
    fi
    echo ""
    echo "== canonical Author Voice Profile (author-fingerprint: schema F1 + provenance F2 + same-register F3 + descriptive-not-prescriptive F4 + clean W1/W2, under --strict) =="
    if [ -f "$CA_BASE/example-author-voice-profile.md" ]; then
      "$0" author-fingerprint "$CA_BASE/example-author-voice-profile.md" --strict || CA_FAIL=1
    else
      echo "ERROR: $CA_BASE/example-author-voice-profile.md not found"; CA_FAIL=1
    fi
    echo ""
    echo "== canonical Content Advisory (content-advisory: schema A1 + locus shape A2 + no-severity-leak A3 + descriptive W1 + opt-in W2, under --strict) =="
    if [ -f "$CA_BASE/example-content-advisory.md" ]; then
      "$0" content-advisory "$CA_BASE/example-content-advisory.md" --strict || CA_FAIL=1
    else
      echo "ERROR: $CA_BASE/example-content-advisory.md not found"; CA_FAIL=1
    fi
    echo ""
    echo "== canonical Persona Divergence Map (persona-divergence: schema D1 + grounded prediction D2 + target-severity D3 + anti-fabrication D4 + closed-key D5, paired with the Ledger, under --strict) =="
    if [ -f "$CA_BASE/example-persona-divergence-map.md" ] && [ -f "$CA_BASE/example-persona-divergence-ledger.md" ]; then
      "$0" persona-divergence "$CA_BASE/example-persona-divergence-map.md" "$CA_BASE/example-persona-divergence-ledger.md" --strict || CA_FAIL=1
    else
      echo "ERROR: $CA_BASE/example-persona-divergence-map.md or example-persona-divergence-ledger.md not found"; CA_FAIL=1
    fi
    echo ""
    echo "== canonical Worldbuilding Bible (world-bible: schema W1 + closed-key + unique ids WD + rule WB-R1 + cost WB-C1/C2 + distance WB-G1 + chronology WB-G2 + firewall WF, staged contradictions overridden, under --strict) =="
    if [ -f "$CA_BASE/example-worldbuilding-bible.md" ]; then
      "$0" world-bible "$CA_BASE/example-worldbuilding-bible.md" --strict || CA_FAIL=1
    else
      echo "ERROR: $CA_BASE/example-worldbuilding-bible.md not found"; CA_FAIL=1
    fi
    echo ""
    echo "== canonical State Card (state-card-diff: cross-round coherence; self-diff + round-2 diff) =="
    if [ -f "$CA_BASE/example-state-card.md" ]; then
      "$0" state-card-diff "$CA_BASE/example-state-card.md" || CA_FAIL=1
      if [ -f "$CA_BASE/example-state-card-round2.md" ]; then
        "$0" state-card-diff "$CA_BASE/example-state-card.md" "$CA_BASE/example-state-card-round2.md" || CA_FAIL=1
      else
        echo "ERROR: $CA_BASE/example-state-card-round2.md not found"; CA_FAIL=1
      fi
    else
      echo "ERROR: $CA_BASE/example-state-card.md not found"; CA_FAIL=1
    fi
    echo ""
    echo "== canonical regression-diff (draft-over-draft: cross-round recurrence + quiet-chapter candidates) =="
    if [ -d "$CA_BASE/example-run-folder-r1" ] && [ -d "$CA_BASE/example-run-folder-r2" ]; then
      # default mode is advisory: the two regression candidates are WARN, exit 0.
      "$0" regression-diff "$CA_BASE/example-run-folder-r1" "$CA_BASE/example-run-folder-r2" >/dev/null 2>&1 || CA_FAIL=1
      # --strict must FAIL (exit non-zero) AND the matcher must RAISE the recurrence (W1) + quiet-chapter
      # (W2) candidates by heuristic match — non-vacuous proof the cross-round matcher actually fires.
      if RGD_OUT=$("$0" regression-diff --strict "$CA_BASE/example-run-folder-r1" "$CA_BASE/example-run-folder-r2" 2>&1); then
        echo "regression-diff (paired fixture): FAIL (expected --strict to exit non-zero on the candidates)"; CA_FAIL=1
      elif printf '%s' "$RGD_OUT" | grep -q "W1 recurrence-candidate" && printf '%s' "$RGD_OUT" | grep -q "W2 quiet-chapter breakage"; then
        echo "regression-diff (paired fixture): PASS"
      else
        echo "regression-diff (paired fixture): FAIL (--strict ran but W1/W2 candidates not raised)"; CA_FAIL=1
      fi
    else
      echo "ERROR: $CA_BASE/example-run-folder-r1 / -r2 not found"; CA_FAIL=1
    fi
    echo ""
    echo "== canonical pre-draft Argument_State (argument-spine: spine + support + warrant maps seed §1-§4) =="
    if [ -f "$CA_BASE/example-argument-state-predraft.md" ]; then
      "$0" argument-spine "$CA_BASE/example-argument-state-predraft.md" || CA_FAIL=1
    else
      echo "ERROR: $CA_BASE/example-argument-state-predraft.md not found"; CA_FAIL=1
    fi
    echo ""
    echo "== canonical genre-profiled Argument_States (argument-spine Inc 5: B1-B4 + W4 over grant / academic / pitch; --strict) =="
    for GENRE_FIX in grant academic pitch; do
      GENRE_F="$CA_BASE/example-argument-state-genre-$GENRE_FIX.md"
      if [ -f "$GENRE_F" ]; then
        "$0" argument-spine "$GENRE_F" --strict || CA_FAIL=1
      else
        echo "ERROR: $GENRE_F not found"; CA_FAIL=1
      fi
    done
    echo ""
    echo "== canonical Scene-Ethics Plan (scene-ethics: ethics-plan contract + resolved depictions) =="
    if [ -f "$CA_BASE/example-scene-ethics-plan.md" ]; then
      "$0" scene-ethics "$CA_BASE/example-scene-ethics-plan.md" || CA_FAIL=1
    else
      echo "ERROR: $CA_BASE/example-scene-ethics-plan.md not found"; CA_FAIL=1
    fi
    echo ""
    echo "== canonical Beta-Reader Instrument (reader-instrument: question-contract + provenance + firewall + anti-relitigation) =="
    if [ -f "$CA_BASE/example-beta-reader-instrument.md" ] && [ -f "$CA_BASE/example-uncertainty-ledger.md" ]; then
      "$0" reader-instrument "$CA_BASE/example-beta-reader-instrument.md" "$CA_BASE/example-uncertainty-ledger.md" || CA_FAIL=1
    else
      echo "ERROR: $CA_BASE/example-beta-reader-instrument.md / example-uncertainty-ledger.md not found"; CA_FAIL=1
    fi
    echo ""
    echo "== canonical Structure Map manifest (manuscript-viz: manifest<->source provenance vs Timeline + Ledger) =="
    if [ -f "$CA_BASE/example-structure-map-manifest.md" ] && [ -f "$CA_BASE/example-timeline.md" ] && [ -f "$CA_BASE/example-findings-ledger.md" ]; then
      "$0" manuscript-viz "$CA_BASE/example-structure-map-manifest.md" "$CA_BASE/example-timeline.md" "$CA_BASE/example-findings-ledger.md" --require-block || CA_FAIL=1
    else
      echo "ERROR: $CA_BASE/example-structure-map-manifest.md / example-timeline.md / example-findings-ledger.md not found"; CA_FAIL=1
    fi
    echo ""
    echo "== canonical annotated manuscript (annotated-manuscript: no-mutation + anchor ladder + Must-Fix rendered) =="
    if [ -d "$CA_BASE/example-annotated-manuscript" ]; then
      "$0" annotated-manuscript "$CA_BASE/example-annotated-manuscript" || CA_FAIL=1
    else
      echo "ERROR: $CA_BASE/example-annotated-manuscript not found"; CA_FAIL=1
    fi
    echo ""
    echo "== canonical crosslink (crosslink: letter<->margin bidirectional integrity + no letter mutation) =="
    if [ -d "$CA_BASE/example-annotated-manuscript" ]; then
      "$0" crosslink "$CA_BASE/example-annotated-manuscript" || CA_FAIL=1
    else
      echo "ERROR: $CA_BASE/example-annotated-manuscript not found"; CA_FAIL=1
    fi
    echo ""
    echo "== producer chain (build -> A1-A6 -> render -> X1-X4 on a temp copy; verified-or-absent) =="
    # The producer (docs/annotated-manuscript-producer.md, Increment 1) wires the generators into the
    # run flow: build the manifest + annotated copy and render the crosslinked letter from the run-folder
    # INPUTS, gating each, and move only verified artifacts into place. Exercise that chain end-to-end on
    # a temp copy of the canonical INPUTS (snapshot + ledger + editorial letter + timeline) — never in
    # place, since build/render WRITE outputs (a dirty-tree, non-idempotent gate otherwise; same
    # temp-copy discipline as the gate engine below). Also assert the fresh build is byte-identical to the
    # committed fixture, so the committed outputs are provably "what a fresh build emits" (no hand drift).
    if [ -d "$CA_BASE/example-annotated-manuscript" ] && command -v python3 >/dev/null 2>&1; then
      CA_PC_SRC="$CA_BASE/example-annotated-manuscript"
      CA_PC=$(mktemp -d)
      cp "$CA_PC_SRC"/*_Manuscript_Snapshot_*.md "$CA_PC_SRC"/*_Findings_Ledger_*.md \
         "$CA_PC_SRC"/*_Timeline_*.md "$CA_PC"/ 2>/dev/null
      # Stage the editorial letter under the PRODUCTION filename (*_Core_DE_Synthesis_*, what a real
      # Core/Full run writes), not the fixture's *_Editorial_Letter_* — so the chain exercises the first,
      # production branch of crosslink._LETTER_GLOBS in both render and the crosslink gate. The crosslinked
      # output's name + content derive from the letter body + runlabel (not the letter's infix), so the
      # byte-identity assertion below still holds against the committed *_Crosslinked_Letter_* fixture.
      CA_PC_LETTER=$(basename "$(ls "$CA_PC_SRC"/*_Editorial_Letter_*.md 2>/dev/null | head -1)")
      cp "$CA_PC_SRC/$CA_PC_LETTER" "$CA_PC/${CA_PC_LETTER/_Editorial_Letter_/_Core_DE_Synthesis_}" 2>/dev/null
      CA_PC_OK=1
      python3 "$CA_SCRIPT_DIR/annotation_manifest.py" build "$CA_PC" >/dev/null 2>&1 || CA_PC_OK=0
      "$0" annotated-manuscript "$CA_PC" >/dev/null 2>&1 || CA_PC_OK=0
      python3 "$CA_SCRIPT_DIR/crosslink.py" render "$CA_PC" >/dev/null 2>&1 || CA_PC_OK=0
      "$0" crosslink "$CA_PC" >/dev/null 2>&1 || CA_PC_OK=0
      # fresh build == committed fixture, byte-for-byte, for each generated artifact; the count guard
      # keeps the assertion non-vacuous even if a future global `nullglob` made an unmatched glob vanish.
      CA_PC_N=0
      for CA_PC_F in "$CA_PC"/*_Annotation_Manifest_*.md "$CA_PC"/*_Annotated_Manuscript_*.md "$CA_PC"/*_Crosslinked_Letter_*.md; do
        if [ -f "$CA_PC_F" ]; then
          CA_PC_N=$((CA_PC_N + 1))
          cmp -s "$CA_PC_F" "$CA_PC_SRC/$(basename "$CA_PC_F")" || CA_PC_OK=0
        else
          CA_PC_OK=0
        fi
      done
      [ "$CA_PC_N" -eq 3 ] || CA_PC_OK=0
      if [ "$CA_PC_OK" -eq 1 ]; then
        echo "producer chain (temp copy): PASS"
      else
        echo "producer chain (temp copy): FAIL"; CA_FAIL=1
      fi
      rm -rf "$CA_PC"
    elif [ ! -d "$CA_BASE/example-annotated-manuscript" ]; then
      echo "ERROR: $CA_BASE/example-annotated-manuscript not found"; CA_FAIL=1
    fi
    echo ""
    echo "== canonical reanchor (round-trip: held/moved/vanished/ambiguous/not-re-anchorable + RA1-RA3) =="
    if [ -d "$CA_BASE/example-annotated-manuscript" ] && [ -f "$CA_BASE/example-reanchor-revised.md" ] && command -v python3 >/dev/null 2>&1; then
      # Re-anchor the canonical N manifest onto a REVISED-draft snapshot. Default mode is advisory
      # (W1 vanished + W2 ambiguous/line-range), exit 0 — and RA1-RA3 (the hard re-anchor contract) must
      # pass. --strict must FAIL, and the classifier must raise ALL FIVE classes — non-vacuous proof the
      # re-anchorer actually fires (a held quote, a moved quote, a vanished chapter, an ambiguous chapter,
      # a not-re-anchorable line-range).
      "$0" reanchor "$CA_BASE/example-annotated-manuscript" "$CA_BASE/example-reanchor-revised.md" >/dev/null 2>&1 || CA_FAIL=1
      if RAN_OUT=$("$0" reanchor --strict "$CA_BASE/example-annotated-manuscript" "$CA_BASE/example-reanchor-revised.md" 2>&1); then
        echo "reanchor (revised-draft fixture): FAIL (expected --strict to exit non-zero on the refusals)"; CA_FAIL=1
      elif printf '%s' "$RAN_OUT" | grep -q "reanchor:held" && printf '%s' "$RAN_OUT" | grep -q "reanchor:moved" \
           && printf '%s' "$RAN_OUT" | grep -q "reanchor:vanished" && printf '%s' "$RAN_OUT" | grep -q "reanchor:ambiguous" \
           && printf '%s' "$RAN_OUT" | grep -q "reanchor:not-re-anchorable"; then
        echo "reanchor (revised-draft fixture): PASS"
      else
        echo "reanchor (revised-draft fixture): FAIL (--strict ran but the five classes not all raised)"; CA_FAIL=1
      fi
    elif [ ! -f "$CA_BASE/example-reanchor-revised.md" ]; then
      echo "ERROR: $CA_BASE/example-reanchor-revised.md not found"; CA_FAIL=1
    fi
    echo ""
    echo "== round-trip glue chain (emit -> A-gate the revised copy -> crossref; on a temp copy) =="
    # The round-trip GLUE (docs/annotated-manuscript-reanchoring.md §The artifacts; ROADMAP "truly great"
    # #2) wires reanchor into a revision-aware flow: emit the re-anchored manifest + the rendered annotated
    # copy of the REVISED draft, gate that copy against the revised snapshot (A1-A6, ledger-optional), then
    # cross-reference the anchor classes against regression-diff's finding classes by finding_id. Exercise
    # the chain end-to-end on a temp copy — emit WRITES outputs (never in place; same discipline as the
    # producer chain above) — and assert: emit exits 0 and wrote both artifacts, the emitted copy passes
    # the A-gate, and crossref runs clean (advisory). Non-vacuous: the emitted copy must round-trip the
    # revised snapshot byte-for-byte (A2 no-mutation) under the gate.
    if [ -d "$CA_BASE/example-annotated-manuscript" ] && [ -f "$CA_BASE/example-reanchor-revised.md" ] && command -v python3 >/dev/null 2>&1; then
      CA_RT_SRC="$CA_BASE/example-annotated-manuscript"
      CA_RT=$(mktemp -d)
      # Stage the prior run folder's manifest + a properly-named revised snapshot (so emit derives a clean
      # runlabel from the *_Manuscript_Snapshot_* infix), then emit into the same temp folder.
      cp "$CA_RT_SRC"/*_Annotation_Manifest_*.md "$CA_RT"/ 2>/dev/null
      cp "$CA_BASE/example-reanchor-revised.md" "$CA_RT/Example_Manuscript_Snapshot_reanchor-r2.md"
      CA_RT_OK=1
      python3 "$CA_SCRIPT_DIR/reanchor.py" emit "$CA_RT" "$CA_RT/Example_Manuscript_Snapshot_reanchor-r2.md" -o "$CA_RT" >/dev/null 2>&1 || CA_RT_OK=0
      CA_RT_MAN="$CA_RT/Example_Reanchored_Manifest_reanchor-r2.md"
      CA_RT_ANN="$CA_RT/Example_Reanchored_Annotated_Manuscript_reanchor-r2.md"
      CA_RT_SNAP="$CA_RT/Example_Manuscript_Snapshot_reanchor-r2.md"
      [ -f "$CA_RT_MAN" ] && [ -f "$CA_RT_ANN" ] || CA_RT_OK=0
      # Gate the EMITTED revised-draft copy against the revised snapshot with the SAME ledger-optional
      # A-gate the reanchor contract uses (A1+A2+A3+A4-multiset+A6; the A4/A5 cross-ledger arms are inert
      # for a re-anchored copy — there is no re-diagnosed N+1 ledger, by construction). The plain
      # `annotated-manuscript` validator would (correctly) demand a ledger, so gate via am.check(...,
      # ledger_optional=True) — proving the written copy round-trips the revised snapshot (A2 no-mutation)
      # and every carried anchor resolves, on the files emit actually wrote.
      if [ -f "$CA_RT_MAN" ] && [ -f "$CA_RT_ANN" ]; then
        CA_SCRIPT_DIR="$CA_SCRIPT_DIR" python3 - "$CA_RT_SNAP" "$CA_RT_MAN" "$CA_RT_ANN" <<'PY' >/dev/null 2>&1 || CA_RT_OK=0
import os, sys
sys.path.insert(0, os.environ["CA_SCRIPT_DIR"])
import annotation_manifest as am
snap = am.normalize_snapshot(open(sys.argv[1], encoding="utf-8").read())
man = open(sys.argv[2], encoding="utf-8").read()
ann = open(sys.argv[3], encoding="utf-8").read()
code, _ = am.check(snap, man, ann, ledger_text=None, ledger_optional=True)
sys.exit(code)
PY
      fi
      # crossref joins by finding_id against a current round folder (advisory, exit 0); use the paired
      # regression fixture as the "this round" ledger — it need not share ids (a clean no-contradiction join).
      python3 "$CA_SCRIPT_DIR/reanchor.py" crossref "$CA_RT" "$CA_RT/Example_Manuscript_Snapshot_reanchor-r2.md" "$CA_BASE/example-run-folder-r2" >/dev/null 2>&1 || CA_RT_OK=0
      if [ "$CA_RT_OK" -eq 1 ]; then
        echo "round-trip glue chain (temp copy): PASS"
      else
        echo "round-trip glue chain (temp copy): FAIL"; CA_FAIL=1
      fi
      rm -rf "$CA_RT"
    elif [ ! -f "$CA_BASE/example-reanchor-revised.md" ]; then
      echo "ERROR: $CA_BASE/example-reanchor-revised.md not found (round-trip glue chain)"; CA_FAIL=1
    fi
    echo ""
    echo "== canonical obsidian-export (manifest -> native footnotes; O1-O3 + byte-identical to committed) =="
    if [ -d "$CA_BASE/example-annotated-manuscript" ] && command -v python3 >/dev/null 2>&1; then
      # Project the canonical manifest + snapshot to Obsidian-native footnotes on a temp copy (generate
      # WRITES obsidian/<copy>, so never in place), gate it (O1-O3), and assert the fresh export is
      # byte-identical to the committed obsidian/ fixture (same discipline as the producer chain).
      CA_OBE_SRC="$CA_BASE/example-annotated-manuscript"
      CA_OBE=$(mktemp -d)
      cp "$CA_OBE_SRC"/*_Manuscript_Snapshot_*.md "$CA_OBE_SRC"/*_Annotation_Manifest_*.md \
         "$CA_OBE_SRC"/*_Crosslinked_Letter_*.md "$CA_OBE"/ 2>/dev/null
      CA_OBE_OK=1
      python3 "$CA_SCRIPT_DIR/annotation_export.py" obsidian "$CA_OBE" >/dev/null 2>&1 || CA_OBE_OK=0
      "$0" obsidian-export "$CA_OBE" >/dev/null 2>&1 || CA_OBE_OK=0
      # both Obsidian outputs (the copy + the Inc-2 letter) must be byte-identical to the committed fixtures.
      CA_OBE_N=0
      for CA_OBE_F in "$CA_OBE"/obsidian/*.md; do
        if [ -f "$CA_OBE_F" ]; then
          CA_OBE_N=$((CA_OBE_N + 1))
          cmp -s "$CA_OBE_F" "$CA_OBE_SRC/obsidian/$(basename "$CA_OBE_F")" || CA_OBE_OK=0
        else
          CA_OBE_OK=0
        fi
      done
      [ "$CA_OBE_N" -eq 2 ] || CA_OBE_OK=0
      if [ "$CA_OBE_OK" -eq 1 ]; then
        echo "obsidian-export (temp copy): PASS"
      else
        echo "obsidian-export (temp copy): FAIL"; CA_FAIL=1
      fi
      rm -rf "$CA_OBE"
    else
      echo "ERROR: $CA_BASE/example-annotated-manuscript not found (obsidian-export)"; CA_FAIL=1
    fi
    echo ""
    echo "== canonical html-export (manifest -> self-contained read-only HTML; H1-H3 + byte-identical) =="
    if [ -d "$CA_BASE/example-annotated-manuscript" ] && command -v python3 >/dev/null 2>&1; then
      # Project the canonical manifest + snapshot to a self-contained .html on a temp copy (generate WRITES
      # html/<copy>.html, so never in place), gate it (H1-H3), and assert the fresh export is byte-identical
      # to the committed html/ fixture (the producer-chain / obsidian-export discipline).
      CA_HXE_SRC="$CA_BASE/example-annotated-manuscript"
      CA_HXE=$(mktemp -d)
      cp "$CA_HXE_SRC"/*_Manuscript_Snapshot_*.md "$CA_HXE_SRC"/*_Annotation_Manifest_*.md "$CA_HXE"/ 2>/dev/null
      CA_HXE_OK=1
      python3 "$CA_SCRIPT_DIR/annotation_export.py" html "$CA_HXE" >/dev/null 2>&1 || CA_HXE_OK=0
      "$0" html-export "$CA_HXE" >/dev/null 2>&1 || CA_HXE_OK=0
      CA_HXE_N=0
      for CA_HXE_F in "$CA_HXE"/html/*.html; do
        if [ -f "$CA_HXE_F" ]; then
          CA_HXE_N=$((CA_HXE_N + 1))
          cmp -s "$CA_HXE_F" "$CA_HXE_SRC/html/$(basename "$CA_HXE_F")" || CA_HXE_OK=0
        else
          CA_HXE_OK=0
        fi
      done
      [ "$CA_HXE_N" -eq 1 ] || CA_HXE_OK=0
      if [ "$CA_HXE_OK" -eq 1 ]; then
        echo "html-export (temp copy): PASS"
      else
        echo "html-export (temp copy): FAIL"; CA_FAIL=1
      fi
      rm -rf "$CA_HXE"
    else
      echo "ERROR: $CA_BASE/example-annotated-manuscript not found (html-export)"; CA_FAIL=1
    fi
    echo ""
    echo "== canonical docx-export (manifest -> .docx with anchored comments; D1-D3 + byte-identical) =="
    if [ -d "$CA_BASE/example-annotated-manuscript" ] && command -v python3 >/dev/null 2>&1; then
      # Project the canonical manifest + snapshot to a .docx on a temp copy (generate WRITES
      # docx/<copy>.docx, never in place), gate it (D1-D3), and assert the fresh byte-deterministic export
      # is byte-identical to the committed docx/ fixture.
      CA_DXE_SRC="$CA_BASE/example-annotated-manuscript"
      CA_DXE=$(mktemp -d)
      cp "$CA_DXE_SRC"/*_Manuscript_Snapshot_*.md "$CA_DXE_SRC"/*_Annotation_Manifest_*.md "$CA_DXE"/ 2>/dev/null
      CA_DXE_OK=1
      python3 "$CA_SCRIPT_DIR/annotation_export.py" docx "$CA_DXE" >/dev/null 2>&1 || CA_DXE_OK=0
      "$0" docx-export "$CA_DXE" >/dev/null 2>&1 || CA_DXE_OK=0
      CA_DXE_N=0
      for CA_DXE_F in "$CA_DXE"/docx/*.docx; do
        if [ -f "$CA_DXE_F" ]; then
          CA_DXE_N=$((CA_DXE_N + 1))
          cmp -s "$CA_DXE_F" "$CA_DXE_SRC/docx/$(basename "$CA_DXE_F")" || CA_DXE_OK=0
        else
          CA_DXE_OK=0
        fi
      done
      [ "$CA_DXE_N" -eq 1 ] || CA_DXE_OK=0
      if [ "$CA_DXE_OK" -eq 1 ]; then
        echo "docx-export (temp copy): PASS"
      else
        echo "docx-export (temp copy): FAIL"; CA_FAIL=1
      fi
      rm -rf "$CA_DXE"
    else
      echo "ERROR: $CA_BASE/example-annotated-manuscript not found (docx-export)"; CA_FAIL=1
    fi
    echo ""
    echo "== canonical Timeline (timeline-arithmetic, timeline-anchor-conflict, timeline-diff self) =="
    if [ -f "$CA_BASE/example-timeline.md" ]; then
      "$0" timeline-arithmetic "$CA_BASE/example-timeline.md" || CA_FAIL=1
      "$0" timeline-anchor-conflict "$CA_BASE/example-timeline.md" || CA_FAIL=1
      "$0" timeline-diff "$CA_BASE/example-timeline.md" "$CA_BASE/example-timeline.md" || CA_FAIL=1
    else
      echo "ERROR: $CA_BASE/example-timeline.md not found"; CA_FAIL=1
    fi
    echo ""
    echo "== canonical run folder (gate-state, escalation-check, argument-recon-prerequisite; gate engine on a temp copy) =="
    if [ -d "$CA_BASE/example-run-folder" ]; then
      CA_RUNDIR="$CA_BASE/example-run-folder"
      "$0" gate-state "$CA_RUNDIR/Diagnostic_State.meta.json" || CA_FAIL=1
      "$0" escalation-check "$CA_RUNDIR" || CA_FAIL=1
      "$0" argument-recon-prerequisite "$CA_RUNDIR" || CA_FAIL=1
      # the gate engine APPENDS an event to the sidecar, so exercise it on a throwaway copy to keep
      # the committed fixture immutable (the read-only validators above run against it directly).
      if command -v python3 >/dev/null 2>&1; then
        CA_TMP=$(mktemp -d)
        cp "$CA_RUNDIR"/* "$CA_TMP"/ 2>/dev/null
        if "$0" gate run_synthesis "$CA_TMP" >/dev/null 2>&1; then
          echo "gate run_synthesis (temp copy): PASS"
        else
          echo "gate run_synthesis (temp copy): FAIL"; CA_FAIL=1
        fi
        rm -rf "$CA_TMP"
      fi
    else
      echo "ERROR: $CA_BASE/example-run-folder not found"; CA_FAIL=1
    fi
    echo ""
  fi

  # Argument Benchmark ground-truth corpus — only present in the repo (evals/ is not shipped to
  # the generated host workspaces), so resolve-and-skip when absent rather than fail.
  CA_EVALS=""
  for cand in "$CA_SCRIPT_DIR/../../../evals/fixtures/argument-benchmark" "$CA_SCRIPT_DIR/../evals/fixtures/argument-benchmark"; do
    if [ -d "$cand" ]; then CA_EVALS="$cand"; break; fi
  done
  if [ -n "$CA_EVALS" ]; then
    echo "== argument-groundtruth-check (registered GT corpus) =="
    for gt in "$CA_EVALS"/*/groundtruth.md; do
      [ -f "$gt" ] || continue
      "$0" argument-groundtruth-check "$gt" >/dev/null 2>&1 && echo "  ok $(basename "$(dirname "$gt")")" || { echo "  FAIL $(basename "$(dirname "$gt")")"; "$0" argument-groundtruth-check "$gt"; CA_FAIL=1; }
    done
    echo ""
  fi

  # Dual-script-mirror invariant: the root scripts/ copy (what CI runs) and the canonical
  # plugins/apodictic/scripts/ copy must be byte-identical for the shared mirrored set, or a
  # validator change passes against one copy while CI runs the stale other (AGENTS.md § parity).
  echo "== check-mirror (scripts/ <-> plugins/apodictic/scripts/ byte-identical) =="
  "$0" check-mirror >/dev/null 2>&1 && echo "  ok (mirrored set identical)" || { echo "  FAIL"; "$0" check-mirror || true; CA_FAIL=1; }
  echo ""

  if [ "$CA_FAIL" -eq 0 ]; then
    echo "check-all: PASS (self-tests + real-file invariants)"
    exit 0
  else
    echo "check-all: FAIL (one or more checks failed; rerun individually for details)"
    exit 1
  fi
fi

COMMAND="$1"
shift

# ----------------------------------------------------------------------
# Pure-utility self-tests (Validator Architecture Hardening). The seven
# count/format utilities below (contract-hash, contract-check, ledger-check,
# artifact-names, synthesis-sections, tone-check, state-lines) previously
# carried no self-tests. These fixture-driven functions give each one
# regression coverage and let them join --self-test-all. Each prints
# per-case OK/FAIL, sets PU_FAIL on any failure, and the caller exits PU_FAIL.
# Invoked as `validate.sh <utility> --self-test`.
# ----------------------------------------------------------------------
_pu_rc() {  # _pu_rc <name> <want_rc> -- <cmd...>   asserts the command's exit code
  local name="$1" want="$2"; shift 3
  local rc=0
  "$@" >/dev/null 2>&1 || rc=$?   # `|| ` keeps errexit from firing on the tested non-zero exit
  if [ "$rc" -eq "$want" ]; then echo "  $name: OK"; else echo "  $name: FAIL (rc=$rc want $want)"; PU_FAIL=1; fi
}
_pu_eq() {  # _pu_eq <name> <actual> <expected>     asserts string equality
  if [ "$2" = "$3" ]; then echo "  $1: OK"; else echo "  $1: FAIL ('$2' != '$3')"; PU_FAIL=1; fi
}

_selftest_contract_hash() {
  PU_FAIL=0; local d; d=$(mktemp -d); printf 'controlling idea\n' > "$d/c.md"
  local h; h=$("$0" contract-hash "$d/c.md")
  if printf '%s' "$h" | grep -qE '^[0-9a-f]{64}$'; then echo "  hash_is_64hex: OK"; else echo "  hash_is_64hex: FAIL ($h)"; PU_FAIL=1; fi
  _pu_eq deterministic "$h" "$("$0" contract-hash "$d/c.md")"
  _pu_rc missing_file_exit2 2 -- "$0" contract-hash "$d/nope.md"
  _pu_rc no_arg_exit2 2 -- "$0" contract-hash
  rm -rf "$d"; [ "$PU_FAIL" -eq 0 ] && echo "Self-test: PASS" || echo "Self-test: FAIL"; return "$PU_FAIL"
}

_selftest_contract_check() {
  PU_FAIL=0; local d; d=$(mktemp -d); printf 'contract body\n' > "$d/c.md"
  local h; h=$("$0" contract-hash "$d/c.md")
  _pu_rc match_exit0 0 -- "$0" contract-check "$d/c.md" "$h"
  _pu_rc mismatch_exit1 1 -- "$0" contract-check "$d/c.md" "0000000000000000000000000000000000000000000000000000000000000000"
  _pu_rc missing_file_exit2 2 -- "$0" contract-check "$d/nope.md" "$h"
  _pu_rc missing_arg_exit2 2 -- "$0" contract-check "$d/c.md"
  rm -rf "$d"; [ "$PU_FAIL" -eq 0 ] && echo "Self-test: PASS" || echo "Self-test: FAIL"; return "$PU_FAIL"
}

_selftest_ledger_check() {
  PU_FAIL=0; local d; d=$(mktemp -d)
  local SECT='### Notable Findings
x
### Data Artifacts for Letter Reference
x
### Cross-Pass Connections
x
### Unresolved Questions
x
### Audit Triggers
x'
  printf '## Pass 5 — Character\n%s\n' "$SECT" > "$d/ok.md"
  _pu_rc complete_pass_exit0 0 -- "$0" ledger-check "$d/ok.md"
  # Pass 5 missing one required section -> ERROR
  printf '## Pass 5 — Character\n### Notable Findings\nx\n### Cross-Pass Connections\nx\n### Unresolved Questions\nx\n### Audit Triggers\nx\n' > "$d/missing.md"
  _pu_rc missing_section_exit1 1 -- "$0" ledger-check "$d/missing.md"
  # Pass 0 missing a section -> NOTE (acceptable), not error
  printf '## Pass 0 — Structure\n### Notable Findings\nx\n' > "$d/p0.md"
  _pu_rc pass0_lenient_exit0 0 -- "$0" ledger-check "$d/p0.md"
  # No pass entries -> WARNING exit 1
  printf '# Ledger\nno passes here\n' > "$d/empty.md"
  _pu_rc no_passes_exit1 1 -- "$0" ledger-check "$d/empty.md"
  _pu_rc missing_file_exit2 2 -- "$0" ledger-check "$d/nope.md"
  rm -rf "$d"; [ "$PU_FAIL" -eq 0 ] && echo "Self-test: PASS" || echo "Self-test: FAIL"; return "$PU_FAIL"
}

_selftest_artifact_names() {
  PU_FAIL=0; local d; d=$(mktemp -d)
  : > "$d/Proj_Pass1_Reader_Experience_r1.md"
  : > "$d/Proj_Pass5_Character_r1.md"
  _pu_rc conforming_exit0 0 -- "$0" artifact-names "$d" Proj r1
  : > "$d/Proj_Pass2_Structure_WRONGLABEL.md"   # wrong runlabel
  _pu_rc nonconforming_exit1 1 -- "$0" artifact-names "$d" Proj r1
  local e; e=$(mktemp -d)   # no Pass artifacts -> vacuously OK
  _pu_rc no_artifacts_exit0 0 -- "$0" artifact-names "$e" Proj r1
  _pu_rc missing_dir_exit2 2 -- "$0" artifact-names "$d/nope" Proj r1
  rm -rf "$d" "$e"; [ "$PU_FAIL" -eq 0 ] && echo "Self-test: PASS" || echo "Self-test: FAIL"; return "$PU_FAIL"
}

_selftest_synthesis_sections() {
  PU_FAIL=0; local d; d=$(mktemp -d)
  local H="Development Edit|The Short Version|What the Book Does Best|What Needs Work|Additional Observations|Revision Checklist|Protected Elements|Author Decisions|Control Questions|The Strongest Case Against|Stress Test|Appendix A|Appendix B|Appendix C"
  : > "$d/full.md"; local IFS='|'; for h in $H; do printf '## %s\n\nbody\n\n' "$h" >> "$d/full.md"; done; unset IFS
  _pu_rc all_headings_exit0 0 -- "$0" synthesis-sections "$d/full.md"
  grep -v '^## Stress Test$' "$d/full.md" > "$d/partial.md"   # drop one required heading
  _pu_rc missing_heading_exit1 1 -- "$0" synthesis-sections "$d/partial.md"
  _pu_rc missing_file_exit2 2 -- "$0" synthesis-sections "$d/nope.md"
  rm -rf "$d"; [ "$PU_FAIL" -eq 0 ] && echo "Self-test: PASS" || echo "Self-test: FAIL"; return "$PU_FAIL"
}

_selftest_tone_check() {
  PU_FAIL=0; local d; d=$(mktemp -d)
  printf '# Edit\nThe pacing needs work; the voice is distinctive.\n' > "$d/clean.md"
  _pu_rc clean_exit0 0 -- "$0" tone-check "$d/clean.md"
  printf '# Edit\nThis is a flawless masterpiece.\n' > "$d/super.md"
  _pu_rc superlative_exit1 1 -- "$0" tone-check "$d/super.md"
  _pu_rc missing_file_exit2 2 -- "$0" tone-check "$d/nope.md"
  rm -rf "$d"; [ "$PU_FAIL" -eq 0 ] && echo "Self-test: PASS" || echo "Self-test: FAIL"; return "$PU_FAIL"
}

_selftest_state_lines() {
  PU_FAIL=0; local d; d=$(mktemp -d)
  seq 1 5 > "$d/five.md";  _pu_eq counts_five "$("$0" state-lines "$d/five.md" | tr -d '[:space:]')" "5"
  # state-lifecycle gardening-threshold fixtures (corpus-expansion candidate): the count the
  # 300 (warning) / 500 (forced gardening) gardening triggers in state-lifecycle.md read.
  seq 1 300 > "$d/w.md"; _pu_eq counts_300_warn_threshold "$("$0" state-lines "$d/w.md" | tr -d '[:space:]')" "300"
  seq 1 500 > "$d/g.md"; _pu_eq counts_500_forced_threshold "$("$0" state-lines "$d/g.md" | tr -d '[:space:]')" "500"
  _pu_rc missing_file_exit2 2 -- "$0" state-lines "$d/nope.md"
  _pu_rc no_arg_exit2 2 -- "$0" state-lines
  rm -rf "$d"; [ "$PU_FAIL" -eq 0 ] && echo "Self-test: PASS" || echo "Self-test: FAIL"; return "$PU_FAIL"
}

case "$COMMAND" in

  contract-hash)
    if [ "${1:-}" = "--self-test" ]; then _selftest_contract_hash; exit $?; fi
    if [ $# -lt 1 ]; then echo "Usage: $0 contract-hash <contract_file>"; exit 2; fi
    if [ ! -f "$1" ]; then echo "Error: File not found: $1" >&2; exit 2; fi
    shasum -a 256 "$1" | awk '{print $1}'
    ;;

  contract-check)
    if [ "${1:-}" = "--self-test" ]; then _selftest_contract_check; exit $?; fi
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
    if [ "${1:-}" = "--self-test" ]; then _selftest_ledger_check; exit $?; fi
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
    if [ "${1:-}" = "--self-test" ]; then _selftest_artifact_names; exit $?; fi
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
    if [ "${1:-}" = "--self-test" ]; then _selftest_synthesis_sections; exit $?; fi
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
    if [ "${1:-}" = "--self-test" ]; then _selftest_tone_check; exit $?; fi
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
    if [ "${1:-}" = "--self-test" ]; then _selftest_state_lines; exit $?; fi
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
  author-facing-lint)
    # #16 — advisory, warn-only. Surfaces framework shorthand (pass codes,
    # confidence tags, QF-/CR-/FM- codes, P0-P5 tier labels) used as an
    # un-glossed PRIMARY LABEL in the author-facing letter body. Appendices are
    # exempt, and a code glossed inline on first use ("plain language (CODE)" or
    # "CODE (gloss)") is exempt. NEVER fails the build — every hit is a WARN and
    # the arm exits 0 (promote to blocking once proven quiet). Enforces
    # output-policy.md §Author-Facing Language. Body override marker:
    # <!-- override: author-facing-lint -->.
    if [ $# -lt 1 ]; then echo "Usage: $0 author-facing-lint <editorial_letter_file> | --self-test"; exit 2; fi
    AFL_DIR=$(cd "$(dirname "$0")" && pwd)
    LC_HELPER="$AFL_DIR/letter_checks.py"

    if [ "$1" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$LC_HELPER" ]; then python3 "$LC_HELPER" --self-test author-facing-lint; exit $?; fi
      # Degraded self-test (no python3): the bash fallback below is advisory and
      # always exits 0; assert it runs clean on a trivial input.
      AFL_TMP=$(mktemp -d); trap 'rm -rf "$AFL_TMP"' EXIT
      printf '# Development Edit\nClean prose.\n' > "$AFL_TMP/clean.md"
      if "$0" author-facing-lint "$AFL_TMP/clean.md" >/dev/null 2>&1; then echo "  afl_bash_fallback: OK"; echo "Self-test: PASS"; exit 0; else echo "  afl_bash_fallback: FAIL"; echo "Self-test: FAIL"; exit 1; fi
    fi

    # Real-file invocation: delegate to the parser when python3 is present.
    if command -v python3 >/dev/null 2>&1 && [ -f "$LC_HELPER" ]; then
      python3 "$LC_HELPER" author-facing-lint "$@"; exit $?
    fi

    # Degraded path (no python3): coarser body-only grep, advisory, always exit 0
    # (no first-use / gloss exemption — the python parser is the precise path).
    if [ ! -f "$1" ]; then echo "Error: File not found: $1" >&2; exit 2; fi
    AFL_APPX=$(grep -niE "^#{1,4}.*Appendix [A-Za-z]" "$1" 2>/dev/null | head -1 | cut -d: -f1 || true)
    if [ -n "$AFL_APPX" ]; then AFL_BODY=$(sed -n "1,$((AFL_APPX - 1))p" "$1"); else AFL_BODY=$(cat "$1"); fi
    AFL_HITS=$(printf '%s\n' "$AFL_BODY" | grep -nE "\bPass [0-9]+[A-Z]?\b|\[(HIGH|MEDIUM|MODERATE|LOW) CONFIDENCE\]|\[UNCERTAIN\]|\b(QF|CR|FM)-[A-Z]?[0-9]+\b|\bP[0-5]\b" 2>/dev/null || true)
    if [ -n "$AFL_HITS" ]; then
      printf '%s\n' "$AFL_HITS" | while IFS= read -r ln; do echo "WARN: author-facing-lint — framework code in body (advisory, coarse): $ln"; done
    fi
    echo "OK: author-facing-lint complete (advisory; warnings do not fail the build)."
    exit 0
    ;;

  severity-floor)
    if [ $# -lt 1 ]; then echo "Usage: $0 severity-floor <editorial_letter_file> [<ledger_file>] | --self-test"; exit 2; fi
    # Primary path: real parser in scripts/letter_checks.py (Validator Architecture
    # Hardening) — token-boundary matching + body/appendix split, replacing the brittle
    # shell regex below. Degrades to the bash implementation when python3 is unavailable.
    SF_DIR=$(cd "$(dirname "$0")" && pwd)
    LC_HELPER="$SF_DIR/letter_checks.py"

    if [ "$1" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$LC_HELPER" ]; then python3 "$LC_HELPER" --self-test severity-floor; exit $?; fi
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

    # Real-file invocation: delegate to the parser when python3 is present.
    if command -v python3 >/dev/null 2>&1 && [ -f "$LC_HELPER" ]; then
      python3 "$LC_HELPER" severity-floor "$@"; exit $?
    fi

    # Degraded path (no python3): bash regex implementation (kept for python-less hosts).
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
    if [ $# -lt 1 ]; then echo "Usage: $0 audit-signal-propagation <editorial_letter_file> [<ledger_file>] | --self-test | --check-registry [<registry_file> <pass_deps_file>]"; exit 2; fi
    # Primary path: real parser in scripts/letter_checks.py (Validator Architecture
    # Hardening). Degrades to the bash implementation below when python3 is unavailable.
    ASP_DIR=$(cd "$(dirname "$0")" && pwd)
    LC_HELPER="$ASP_DIR/letter_checks.py"

    # Registry completeness check (Phase 2): every signal-emitting audit listed in
    # the registry (audit-routing-table.md §Signal-Emitting Audit Registry) must
    # have a §4e propagation row in pass-dependencies.md, so its internal signal
    # reaches the Canonical Severity Scale instead of dying in the findings file.
    # With no file args, the real files are auto-located relative to this script
    # (works from both the plugin copy and the repo-root copy of validate.sh).
    if [ "$1" = "--check-registry" ]; then
      SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
      REG="${2:-}"; DEP="${3:-}"
      if [ -z "$REG" ]; then
        for base in "$SCRIPT_DIR/../skills/core-editor/references" "$SCRIPT_DIR/../plugins/apodictic/skills/core-editor/references"; do
          if [ -f "$base/audit-routing-table.md" ]; then REG="$base/audit-routing-table.md"; DEP="$base/pass-dependencies.md"; break; fi
        done
      fi
      if [ ! -f "$REG" ] || [ ! -f "$DEP" ]; then echo "Error: registry or pass-dependencies file not found (REG=$REG DEP=$DEP)" >&2; exit 2; fi
      # Delegate parsing to the helper when python3 is present (bash resolves paths).
      if command -v python3 >/dev/null 2>&1 && [ -f "$LC_HELPER" ]; then
        python3 "$LC_HELPER" check-registry "$REG" "$DEP"; exit $?
      fi
      TMPREG=$(mktemp)
      sed -n '/registry:signal-emitting-audits:begin/,/registry:signal-emitting-audits:end/p' "$REG" | grep '^- ' | sed 's/^- //' > "$TMPREG"
      if [ ! -s "$TMPREG" ]; then echo "Error: no registry entries found in $REG" >&2; rm -f "$TMPREG"; exit 2; fi
      REG_MISSING=0; REG_TOTAL=0
      while IFS= read -r AUDIT; do
        [ -z "$AUDIT" ] && continue
        REG_TOTAL=$((REG_TOTAL + 1))
        if ! grep -Fq "| $AUDIT |" "$DEP"; then
          echo "ERROR: signal-emitting audit '$AUDIT' has no §4e propagation row in $(basename "$DEP")"
          REG_MISSING=$((REG_MISSING + 1))
        fi
      done < "$TMPREG"
      rm -f "$TMPREG"
      if [ "$REG_MISSING" -eq 0 ]; then
        echo "Registry check: PASS ($REG_TOTAL signal-emitting audits all have §4e rows)"; exit 0
      else
        echo "Registry check: FAIL ($REG_MISSING of $REG_TOTAL registry audits missing a §4e row)"; exit 1
      fi
    fi

    if [ "$1" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$LC_HELPER" ]; then python3 "$LC_HELPER" --self-test audit-signal-propagation; exit $?; fi
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
      # Registry completeness sub-test (Phase 2): synthetic registry + §4e fixtures.
      cat > "$TMPDIR/reg_ok.md" <<'EOF'
## Signal-Emitting Audit Registry
<!-- registry:signal-emitting-audits:begin -->
- Foo Audit
- Bar Audit
<!-- registry:signal-emitting-audits:end -->
EOF
      cat > "$TMPDIR/reg_missing.md" <<'EOF'
## Signal-Emitting Audit Registry
<!-- registry:signal-emitting-audits:begin -->
- Foo Audit
- Bar Audit
- Ghost Audit
<!-- registry:signal-emitting-audits:end -->
EOF
      cat > "$TMPDIR/dep_fixture.md" <<'EOF'
### §4e. Audit-Signal Propagation Table
| Foo Audit | hard gate | Must-Fix | — | src | — |
| Bar Audit | flag | Should-Fix | — | src | — |
EOF
      "$0" audit-signal-propagation --check-registry "$TMPDIR/reg_ok.md" "$TMPDIR/dep_fixture.md" >/dev/null 2>&1 && echo "  registry_ok: OK (all registry audits have §4e rows)" || { echo "  registry_ok: FAIL (expected PASS)"; RESULTS=1; }
      "$0" audit-signal-propagation --check-registry "$TMPDIR/reg_missing.md" "$TMPDIR/dep_fixture.md" >/dev/null 2>&1 && { echo "  registry_missing: FAIL (Ghost Audit has no §4e row — expected FAIL)"; RESULTS=1; } || echo "  registry_missing: OK (caught — registry-listed audit missing §4e row)"
      [ "$RESULTS" -eq 0 ] && { echo "Self-test: PASS"; exit 0; } || { echo "Self-test: FAIL"; exit 1; }
    fi

    # Real-file invocation: delegate to the parser when python3 is present.
    if command -v python3 >/dev/null 2>&1 && [ -f "$LC_HELPER" ]; then
      python3 "$LC_HELPER" audit-signal-propagation "$@"; exit $?
    fi

    # Degraded path (no python3): bash regex implementation (kept for python-less hosts).
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
    # The optional trailing "( ... )" group recognizes registry names that carry a
    # parenthetical, e.g. "Banister (Epistemic Humility)", "Narrative-Decision
    # (StoryScope)", "Timeline (Pass 10)". The standalone "&" / "/" connector tokens
    # recognize spaced-connector names, e.g. "Series & Composite Novel", "Memoir /
    # Creative NF". Title-case-only (no -i) keeps lowercase connector words like "and"
    # from being captured across two audit mentions on one line. Without these the names
    # go undetected/truncated and the validator falls through to the permissive legacy
    # whole-letter check (false pass) or computes a wrong override slug.
    # The trailing 's/^(The|An?|This|That|These|Those) //' drops a sentence-initial
    # determiner that prose puts before an audit name ("The Reception Risk Audit ...") so a
    # prose mention collapses onto the heading-derived name rather than inventing a phantom.
    AUDIT_NAMES=$(echo "$APPX_BODY" \
      | grep -oE "([A-Z][A-Za-z/&-]*( ([&/]|[A-Z][A-Za-z/&-]*)){0,6}( \([^)]+\))?) [Aa]udit" \
      | sed -E 's/ [Aa]udit$//' \
      | sed -E 's/^(The|An?|This|That|These|Those) //' \
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
    # Primary path: real parser in scripts/letter_checks.py (Validator Architecture
    # Hardening). Degrades to the bash implementation below when python3 is unavailable.
    UDT_DIR=$(cd "$(dirname "$0")" && pwd)
    LC_HELPER="$UDT_DIR/letter_checks.py"

    if [ "$1" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$LC_HELPER" ]; then python3 "$LC_HELPER" --self-test underdiagnosis-triggers; exit $?; fi
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

    # Real-file invocation: delegate to the parser when python3 is present.
    if command -v python3 >/dev/null 2>&1 && [ -f "$LC_HELPER" ]; then
      python3 "$LC_HELPER" underdiagnosis-triggers "$@"; exit $?
    fi

    # Degraded path (no python3): bash regex implementation (kept for python-less hosts).
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
    # Primary path: real parser in scripts/letter_checks.py (Validator Architecture
    # Hardening). Degrades to the bash implementation below when python3 is unavailable.
    LCONS_DIR=$(cd "$(dirname "$0")" && pwd)
    LC_HELPER="$LCONS_DIR/letter_checks.py"

    if [ "$1" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$LC_HELPER" ]; then python3 "$LC_HELPER" --self-test ledger-consolidation; exit $?; fi
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

    # Real-file invocation: delegate to the parser when python3 is present.
    if command -v python3 >/dev/null 2>&1 && [ -f "$LC_HELPER" ]; then
      python3 "$LC_HELPER" ledger-consolidation "$@"; exit $?
    fi

    # Degraded path (no python3): bash regex implementation (kept for python-less hosts).
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
    # Primary path: real parser in scripts/letter_checks.py (Validator Architecture
    # Hardening). Degrades to the bash implementation below when python3 is unavailable.
    DLC_DIR=$(cd "$(dirname "$0")" && pwd)
    LC_HELPER="$DLC_DIR/letter_checks.py"

    if [ "$1" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$LC_HELPER" ]; then python3 "$LC_HELPER" --self-test decision-layer-check; exit $?; fi
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
      # Updated for Phase 7 Wave 2 B3 entry-form filter: the Must-Fix
      # mention must be in label form (heading, list-item leader,
      # Severity label, or MF-N anchor) for the validator to count it
      # as a labeled finding. Bare prose "Must-Fix:" at line start is
      # treated as discussion, not a labeled entry.
      # Author Decisions section uses bare bullet form (no subhead) to
      # avoid C1 subhead-cluster collapse and exercise Check 5 in
      # isolation.
      cat > "$TMPDIR/neg4.md" <<'EOF'
# Development Edit
## What Needs Work
### Must-Fix: voice problem in Chapter 3 only.
The voice flattens in places throughout the manuscript.
## Protected Elements
- One.
- Two.
- Three.
## Author Decisions
- Keep the dual POV.
- Cut the prologue.
- Unsure on Chapter 5 placement.
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
      # and PASSes. Mirrors canonical fixture F1 / F3 patterns.
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
      # C1b case (Phase 7 Wave 2 B3 extension): subhead clusters
      # expressed as bold-paragraph leaders (`**Keep**`, `**Cut /
      # Release**`, `**Unsure — decide before revision**`) rather than
      # level-3 markdown subheads. Mirrors canonical fixture F1
      # pattern that initially failed Wave 1's C1 calibration.
      cat > "$TMPDIR/c1b_bold_subhead_clusters.md" <<'EOF'
# Development Edit
## What Needs Work
Must-Fix: pacing collapse in Chapter 7, lines 142-160; also Chapter 9, line 220.
## Protected Elements
- Voice consistency in Part I.
- Scene 4 pivot from Chapter 3.
- Sister relationship arc.
- Final image of Chapter 12.
## Author Decisions

Translate diagnosis into commitments before revision.

**Keep**
- Keep the dual POV throughout Part II.
- Keep the unreliable narrator frame.
- Keep the prologue's epistolary form.
- Keep the time-jump between Parts I and II.
- Keep the sibling reconciliation thread.
- Keep the ambiguous final image.

**Cut / Release**
- Cut the secondary romance subplot.
- Cut the dream sequence in Chapter 4.
- Cut the third epigraph.
- Cut the metafictional aside in Chapter 9.

**Unsure — decide before revision**
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
      "$0" decision-layer-check "$TMPDIR/c1b_bold_subhead_clusters.md" >/dev/null 2>&1 && echo "  c1b_bold_subhead_clusters: OK (3 bold-paragraph Keep/Cut/Unsure subheads counted, not 13 sub-bullets)" || { echo "  c1b_bold_subhead_clusters: FAIL (Phase 7 Wave 2 B3 calibration regression — bold-paragraph subhead form expected)"; RESULTS=1; }
      "$0" decision-layer-check "$TMPDIR/c2_paragraph_form.md" >/dev/null 2>&1 && echo "  c2_paragraph_form: OK (paragraph-form decision verbs counted via fallback)" || { echo "  c2_paragraph_form: FAIL (Phase 7 C2 calibration regression — paragraph-form fallback expected)"; RESULTS=1; }
      "$0" decision-layer-check "$TMPDIR/c3_argument_de.md" >/dev/null 2>&1 && echo "  c3_argument_de: OK (argument-DE class detected; Checks 3-4 skipped)" || { echo "  c3_argument_de: FAIL (Phase 7 C3 calibration regression — argument-DE schema expected)"; RESULTS=1; }
      "$0" decision-layer-check "$TMPDIR/c4_paragraph_evidence.md" >/dev/null 2>&1 && echo "  c4_paragraph_evidence: OK (paragraph-block window finds inline-prose evidence)" || { echo "  c4_paragraph_evidence: FAIL (Phase 7 C4 calibration regression — paragraph-block window expected)"; RESULTS=1; }
      [ "$RESULTS" -eq 0 ] && { echo "Self-test: PASS"; exit 0; } || { echo "Self-test: FAIL"; exit 1; }
    fi

    # Real-file invocation: delegate to the parser when python3 is present.
    if command -v python3 >/dev/null 2>&1 && [ -f "$LC_HELPER" ]; then
      python3 "$LC_HELPER" decision-layer-check "$@"; exit $?
    fi

    # Degraded path (no python3): bash regex implementation (kept for python-less hosts).
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
      # Count distinct subheads matching Keep/Cut/Unsure (case-
      # insensitive). Two recognized subhead forms:
      #   - Level-3 markdown subheads: `### Keep`, `### Cut`, etc.
      #   - Bold-paragraph subheads: `**Keep**`, `**Cut / Release**`,
      #     `**Unsure — decide before revision**`, etc. (bolded short
      #     leader as a section divider, common in Opus 4.7-style
      #     editorial letters).
      # Each subhead is one cluster regardless of how many sub-bullets
      # it contains. (Phase 7 Wave 2 B3 extension: F1 fixture used
      # bold-paragraph form; subhead detection extended accordingly.)
      local subhead_count_l3 subhead_count_bold subhead_count
      subhead_count_l3=$( { echo "$section" | grep -cE "^###[[:space:]]+(Keep|Cut|Unsure|Defer|Decide)[[:space:]:]*" 2>/dev/null || true; } | head -1 | tr -d ' \n')
      subhead_count_l3=${subhead_count_l3:-0}
      subhead_count_bold=$( { echo "$section" | grep -cE "^\*\*(Keep|Cut|Unsure|Defer|Decide)([[:space:]/—–-]|\*\*$)" 2>/dev/null || true; } | head -1 | tr -d ' \n')
      subhead_count_bold=${subhead_count_bold:-0}
      subhead_count=$((subhead_count_l3 + subhead_count_bold))
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

    # Check 5: Must-Fix evidence density (C4 calibration + B3 entry-form
    # filter).
    # For each *labeled* Must-Fix entry (heading, list-item severity
    # label, "Severity:" label, or MF-N anchor), scan a paragraph-block
    # window from the Must-Fix line until the next Must-Fix occurrence
    # OR the next section header (^## at column 0), whichever comes
    # first. Within that window, count reference patterns. This widens
    # the Phase 4-6 fixed 6-line window so that paragraph-form evidence
    # (references in surrounding prose, not in an immediate trailing
    # list) is detected.
    #
    # Phase 7 Wave 2 B3 entry-form filter: prose discussion that
    # mentions Must-Fix is not a labeled finding. The filter accepts
    # only lines that look like entry labels:
    #   - heading: ^#{1,6}.*Must-Fix
    #   - list-item severity leader: ^[[:space:]]*[-*][[:space:]].*Must-Fix
    #     within the first ~80 chars (i.e., the label position, not
    #     deep prose).
    #   - severity-label line: ^.*\*\*Severity:\*\* .*Must-Fix or
    #     ^Severity: .*Must-Fix.
    #   - MF-N anchor: a line where Must-Fix is co-located with the
    #     finding-id pattern (MF-[0-9]+) within 30 chars.
    # Prose discussion (deep-in-paragraph mentions) is excluded from
    # the count to avoid false-positive evidence-density failures on
    # editorial letters that discuss findings extensively in body
    # prose.
    # Determine body-only line range for MF labeling. Appendix-only
    # mentions are severity-calibration discussion (not labeled
    # findings) and excluded.
    if [ -n "$APPENDIX_LINE" ]; then
      BODY_END=$((APPENDIX_LINE - 1))
    else
      BODY_END=$(wc -l < "$LETTER" | tr -d ' ')
    fi
    MF_LINES=$(awk -v body_end="$BODY_END" '
      NR > body_end { exit }
      {
        line = $0
        ll = tolower(line)
        # Must-Fix marker must literally be present (case-insensitive
        # via tolower; awk regex /i flag is not POSIX-portable).
        if (index(ll, "must-fix") == 0) next
        head80 = substr(line, 1, 80)
        head80_l = tolower(head80)
        # heading (markdown #-prefix)
        if (match(line, /^#+[[:space:]]/) && index(ll, "must-fix") > 0) { print NR; next }
        # list-item leader within first 80 chars
        if (match(line, /^[[:space:]]*[-*][[:space:]]/) && index(head80_l, "must-fix") > 0) { print NR; next }
        # numbered list-item leader within first 80 chars
        if (match(line, /^[[:space:]]*[0-9]+\.[[:space:]]/) && index(head80_l, "must-fix") > 0) { print NR; next }
        # **Severity:** label form
        if (match(line, /\*\*[Ss]everity:?\*\*/) && index(ll, "must-fix") > 0) { print NR; next }
        # bare Severity: label form at start of line
        if (match(line, /^[[:space:]]*[Ss]everity:[[:space:]]/) && index(ll, "must-fix") > 0) { print NR; next }
        # MF-N anchor co-located with Must-Fix label in same line
        if (match(line, /MF-[0-9]+/) && index(ll, "must-fix") > 0) { print NR; next }
        # table row severity column (pipe-delimited cell containing
        # Must-Fix label form, not embedded in long prose)
        if (match(line, /^[[:space:]]*\|/) && match(line, /\|[[:space:]]*[Mm]ust-[Ff]ix[[:space:]]*\|/)) { print NR; next }
      }
    ' "$LETTER")
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
    # Primary path: real parser in scripts/config_checks.py (Validator Architecture
    # Hardening Inc.5). Degrades to the bash implementation below when python3 is absent.
    CFG_DIR=$(cd "$(dirname "$0")" && pwd)
    CFG_HELPER="$CFG_DIR/config_checks.py"

    if [ "$1" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$CFG_HELPER" ]; then python3 "$CFG_HELPER" --self-test quality-risk-triggers; exit $?; fi
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

    # Real-file invocation: delegate to the parser when python3 is present.
    if command -v python3 >/dev/null 2>&1 && [ -f "$CFG_HELPER" ]; then
      python3 "$CFG_HELPER" quality-risk-triggers "$@"; exit $?
    fi

    # Degraded path (no python3): bash regex implementation.
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
    # Primary path: real Timeline parser in scripts/timeline_checks.py (Validator
    # Architecture Hardening Inc.4). Degrades to the bash implementation below when
    # python3 is unavailable.
    TL_DIR=$(cd "$(dirname "$0")" && pwd)
    TL_HELPER="$TL_DIR/timeline_checks.py"

    if [ "$1" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$TL_HELPER" ]; then python3 "$TL_HELPER" --self-test timeline-diff; exit $?; fi
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

    # Real-file invocation: delegate to the parser when python3 is present.
    if [ $# -lt 2 ]; then echo "Usage: $0 timeline-diff <prior_timeline> <current_timeline>"; exit 2; fi
    if command -v python3 >/dev/null 2>&1 && [ -f "$TL_HELPER" ]; then
      python3 "$TL_HELPER" timeline-diff "$@"; exit $?
    fi

    # Degraded path (no python3): bash structural-diff implementation.
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
    # Primary path: real Timeline parser (Inc.4) — adds TRUE span arithmetic on top of
    # the bash marker-hygiene check below (which is kept as the no-python3 degrade path).
    TL_DIR=$(cd "$(dirname "$0")" && pwd)
    TL_HELPER="$TL_DIR/timeline_checks.py"

    if [ "$1" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$TL_HELPER" ]; then python3 "$TL_HELPER" --self-test timeline-arithmetic; exit $?; fi
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

    # Real-file invocation: delegate to the parser when python3 is present (adds true
    # span-overrun arithmetic). The bash marker-hygiene check below is the degrade path.
    if command -v python3 >/dev/null 2>&1 && [ -f "$TL_HELPER" ]; then
      python3 "$TL_HELPER" timeline-arithmetic "$@"; exit $?
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
    # Primary path: real Timeline parser (Inc.4) — adds TRUE same-scene anchor-drift
    # detection on top of the bash pre-labeled surfacing below (the degrade path).
    TL_DIR=$(cd "$(dirname "$0")" && pwd)
    TL_HELPER="$TL_DIR/timeline_checks.py"

    if [ "$1" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$TL_HELPER" ]; then python3 "$TL_HELPER" --self-test timeline-anchor-conflict; exit $?; fi
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

    # Real-file invocation: delegate to the parser when python3 is present (adds true
    # same-scene anchor-drift detection). The bash surfacing check below is the degrade path.
    if command -v python3 >/dev/null 2>&1 && [ -f "$TL_HELPER" ]; then
      python3 "$TL_HELPER" timeline-anchor-conflict "$@"; exit $?
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
    # duplicate id, E3 dangling conflict reference, E4 self conflict, W1 unresolved conflict (both
    # sides still actionable), W2 acting now on an unvalidated claim (W1/W2 advisory; ERROR under
    # --strict). Owns conflict referential integrity + the "contradiction kept live" coherence gap.
    # Takes a run folder (globs *_Feedback_Triage_*.md) or explicit files. Delegates to
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
    # advisory, ERROR under --strict. --require-block makes a missing/invalid manifest a hard failure (the
    # canonical-example gate uses it so it can't pass vacuously). The severity->encoding map is hardcoded
    # in the render-only SVG layer (charts 1-3), not the manifest, so a run cannot recolor a Must-Fix.
    # Takes a run folder (globs the manifest + Timeline + Findings Ledger) or explicit files. Delegates to
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
    echo "WARN: python3 unavailable — manuscript-viz skipped; check inline that the viz_manifest copies Timeline/finding values verbatim, carries no visual-style fields, places findings only by the Chapter-N evidence_refs parse (else 'unplaced'), and includes every Must-Fix. See docs/manuscript-visualizations.md."
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

  argument-groundtruth-check)
    # Argument Benchmark ground-truth answer-key validator (docs/argument-benchmark-spec.md
    # §Mechanical validator): GT1-GT7 presence; DC code-namespace resolution; GT2 locus<->code
    # consistency; GT7 Distinguish classification. Delegates to scripts/argument_groundtruth.py;
    # degrades to an advisory WARN without python3 (the GT contract is prose in the template + spec).
    AGT_DIR=$(cd "$(dirname "$0")" && pwd)
    AGT_HELPER="$AGT_DIR/argument_groundtruth.py"
    if [ "${1:-}" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$AGT_HELPER" ]; then python3 "$AGT_HELPER" --self-test; exit $?; fi
      echo "Self-test: PASS (degraded — python3 unavailable; argument-groundtruth-check is advisory without it)"; exit 0
    fi
    if command -v python3 >/dev/null 2>&1 && [ -f "$AGT_HELPER" ]; then
      if [ $# -lt 1 ]; then echo "Usage: $0 argument-groundtruth-check <groundtruth_file> | --self-test"; exit 2; fi
      python3 "$AGT_HELPER" argument-groundtruth-check "$@"; exit $?
    fi
    echo "WARN: python3 unavailable — argument-groundtruth-check skipped; the GT template + spec define the contract. Install python3 for the mechanical check."
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
    # letter. Delegates to scripts/editor_scaffolding.py; degrades to an advisory WARN without python3.
    ES_DIR=$(cd "$(dirname "$0")" && pwd)
    ES_HELPER="$ES_DIR/editor_scaffolding.py"
    if [ "${1:-}" = "--self-test" ]; then
      if command -v python3 >/dev/null 2>&1 && [ -f "$ES_HELPER" ]; then python3 "$ES_HELPER" --self-test; exit $?; fi
      echo "Self-test: PASS (degraded — python3 unavailable; editor-scaffolding is advisory without it)"; exit 0
    fi
    if command -v python3 >/dev/null 2>&1 && [ -f "$ES_HELPER" ]; then
      if [ $# -lt 1 ]; then echo "Usage: $0 editor-scaffolding <editorial_letter|run_folder> [--strict] | --self-test"; exit 2; fi
      python3 "$ES_HELPER" editor-scaffolding "$@"; exit $?
    fi
    echo "WARN: python3 unavailable — editor-scaffolding skipped; if the letter declares editor-scaffolding mode, verify inline that it carries an Editor Brief, a 'What You Might Have Missed' section, an Intervention Menu, and that severity tokens survive. See docs/editor-scaffolding.md."
    exit 0
    ;;

  check-mirror)
    # Mirror-parity gate (QoL infra; docs/mirror-parity-check.md): mechanizes the AGENTS.md
    # dual-script-mirror invariant. validate.sh, preflight.sh, and every *.py exist in TWO committed
    # copies — root scripts/ (what CI runs) and plugins/apodictic/scripts/ (canonical) — that must be
    # kept byte-identical BY HAND; a stale copy passes locally while CI runs the other blind. This
    # asserts the shared mirrored set matches. Root-only build/release scripts (*.mjs, release.sh,
    # bump-version.sh) and the plugin-only test_fixtures/ are NOT mirrored; schemas are single-sourced.
    # Detection only — never auto-syncs (mirroring stays a deliberate cp). Pure shell; needs no python3.
    if [ "${1:-}" = "--self-test" ]; then
      CM_T=$(mktemp -d); CM_R=0
      mkdir -p "$CM_T/a" "$CM_T/b"
      printf 'x\n' > "$CM_T/a/validate.sh"; printf 'x\n' > "$CM_T/b/validate.sh"
      printf 'p\n' > "$CM_T/a/m.py";        printf 'p\n' > "$CM_T/b/m.py"
      "$0" check-mirror "$CM_T/a" "$CM_T/b" >/dev/null 2>&1 && echo "  identical: OK" || { echo "  identical: FAIL (expected PASS)"; CM_R=1; }
      printf 'p2\n' > "$CM_T/b/m.py"
      "$0" check-mirror "$CM_T/a" "$CM_T/b" >/dev/null 2>&1 && { echo "  content_drift: FAIL (one-byte diff not caught)"; CM_R=1; } || echo "  content_drift: OK (caught)"
      printf 'p\n' > "$CM_T/b/m.py"; printf 'q\n' > "$CM_T/a/only.py"
      "$0" check-mirror "$CM_T/a" "$CM_T/b" >/dev/null 2>&1 && { echo "  missing_file_a: FAIL (one-sided file in dirA not caught)"; CM_R=1; } || echo "  missing_file_a: OK (caught)"
      rm -f "$CM_T/a/only.py"; printf 'q\n' > "$CM_T/b/only.py"
      "$0" check-mirror "$CM_T/a" "$CM_T/b" >/dev/null 2>&1 && { echo "  missing_file_b: FAIL (one-sided file in dirB not caught)"; CM_R=1; } || echo "  missing_file_b: OK (caught)"
      rm -f "$CM_T/b/only.py"
      printf 's\n' > "$CM_T/a/sync_setec.py"   # a root-only util present on the (non-plugin) root side only must NOT fail
      "$0" check-mirror "$CM_T/a" "$CM_T/b" >/dev/null 2>&1 && echo "  root_only_excluded: OK (root-side-only root-only file ignored)" || { echo "  root_only_excluded: FAIL (root-only exclusion not honored)"; CM_R=1; }
      rm -f "$CM_T/a/sync_setec.py"
      # a root-only util that STRAYED to the plugin side (path ends in plugins/apodictic/scripts) must FAIL.
      # Make the two dirs otherwise byte-identical (validate.sh + m.py) so the stray is the ONLY possible
      # failure, and assert on the STRAY *message* (not just exit code) — removing the STRAY branch would
      # make check-mirror PASS here, which must then fail this test rather than slip through on exit code.
      CM_PG="$CM_T/plugins/apodictic/scripts"; mkdir -p "$CM_PG"
      printf 'x\n' > "$CM_PG/validate.sh"; printf 'p\n' > "$CM_PG/m.py"; printf 's\n' > "$CM_PG/sync_setec.py"
      CM_SOUT=$("$0" check-mirror "$CM_T/a" "$CM_PG" 2>&1 || true)   # || true: check-mirror exits 1 on STRAY; don't let that abort under set -e
      echo "$CM_SOUT" | grep -q "STRAY:.*sync_setec.py" && echo "  root_only_stray: OK (caught)" || { echo "  root_only_stray: FAIL (plugin-side root-only copy not flagged STRAY)"; CM_R=1; }
      rm -rf "$CM_T"
      if [ "$CM_R" -eq 0 ]; then echo "Self-test: PASS"; exit 0; else echo "Self-test: FAIL"; exit 1; fi
    fi
    CM_DIR=$(cd "$(dirname "$0")" && pwd)
    if [ $# -ge 2 ]; then
      CM_A="$1"; CM_B="$2"
    elif [ $# -eq 1 ]; then
      echo "Usage: $0 check-mirror [<dirA> <dirB>]  (no args = auto-detect the script-dir pair; two args = compare them). A single dir argument is ambiguous." >&2
      exit 2
    else
      CM_A="$CM_DIR"; CM_B=""
      for cand in "$CM_DIR/../plugins/apodictic/scripts" "$CM_DIR/../../../scripts"; do
        if [ -d "$cand" ]; then rp=$(cd "$cand" && pwd); [ "$rp" != "$CM_DIR" ] && { CM_B="$rp"; break; }; fi
      done
      if [ -z "$CM_B" ]; then echo "WARN: mirror sibling not found from $CM_DIR — single-copy workspace, nothing to mirror; skipped."; exit 0; fi
    fi
    CM_FAIL=0
    # Root-only utilities live ONLY in root scripts/ (release-engineering, like the *.mjs scripts) and
    # are intentionally NOT mirrored to the plugin copy — exclude them or check-mirror false-positives.
    # Space-padded for whole-word matching. (sync_setec.py: the SETEC vendoring/sync utility.)
    CM_ROOT_ONLY=" sync_setec.py "
    # Identify the PLUGIN-side dir (root-only utilities must NOT appear there). Path-based; trailing
    # slash stripped and the bare-relative form covered so a two-arg invocation with `.../scripts/` or
    # a relative path still matches. In the synthetic two-arg case neither matches and CM_PLUGIN stays
    # empty (the cmp fallback below).
    CM_PLUGIN=""
    case "${CM_A%/}" in */plugins/apodictic/scripts|plugins/apodictic/scripts) CM_PLUGIN="$CM_A" ;; esac
    case "${CM_B%/}" in */plugins/apodictic/scripts|plugins/apodictic/scripts) CM_PLUGIN="$CM_B" ;; esac
    # Mirrored set = validate.sh, preflight.sh, and every *.py present in EITHER dir (sorted, deduped).
    # `|| true`: a no-match grep exits 1, which would abort under `set -e`.
    CM_NAMES=$( { ls -1 "$CM_A" 2>/dev/null; ls -1 "$CM_B" 2>/dev/null; } | grep -E '\.py$|^validate\.sh$|^preflight\.sh$' | sort -u || true )
    for name in $CM_NAMES; do
      case "$CM_ROOT_ONLY" in *" $name "*)
        # A root-only utility is legitimate ONLY as root-present / plugin-absent. Don't silently skip a
        # plugin-side copy (wrong side, or accidentally mirrored then divergent) — that is exactly the
        # drift this gate exists to catch. Flag it if it's on the plugin side; when the plugin side
        # isn't identifiable (synthetic dirs), still catch a both-copies divergence via cmp.
        if [ -n "$CM_PLUGIN" ] && [ -f "$CM_PLUGIN/$name" ]; then
          echo "  STRAY: $name is root-only (CM_ROOT_ONLY) but a copy exists in $CM_PLUGIN — remove it; root-only files must not be mirrored"; CM_FAIL=1
        elif [ -z "$CM_PLUGIN" ] && [ -f "$CM_A/$name" ] && [ -f "$CM_B/$name" ]; then
          cmp -s "$CM_A/$name" "$CM_B/$name" || { echo "  DIFFER: $name (root-only utility present in both copies and divergent)"; CM_FAIL=1; }
        fi
        continue ;;
      esac
      fa="$CM_A/$name"; fb="$CM_B/$name"
      if [ ! -f "$fa" ]; then echo "  MISSING in $CM_A: $name"; CM_FAIL=1; continue; fi
      if [ ! -f "$fb" ]; then echo "  MISSING in $CM_B: $name"; CM_FAIL=1; continue; fi
      cmp -s "$fa" "$fb" || { echo "  DIFFER: $name"; CM_FAIL=1; }
    done
    if [ "$CM_FAIL" -eq 0 ]; then
      echo "check-mirror: PASS (root scripts/ <-> plugins/apodictic/scripts/ byte-identical for the mirrored set)"; exit 0
    fi
    echo "check-mirror: FAIL — sync the two copies by hand (cp the intended-canonical file between scripts/ and plugins/apodictic/scripts/), then re-run. A 'DIFFER: validate.sh' on first run of a new check means the copies aren't synced yet, not a logic bug."
    exit 1
    ;;

  *)
    echo "Unknown command: $COMMAND"
    usage
    ;;
esac
