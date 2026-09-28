# shellcheck shell=bash
# Sourced by ../validate.sh; not runnable on its own.
if [ "$1" = "--check-all" ]; then
  CA_SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
  CA_FAIL=0
  # CI runs the hermetic self-tests in a parallel job. The ordinary command
  # remains the full, source-inspectable local/release gate.
  if [ "$CA_SKIP_SELF_TESTS" -ne 1 ]; then
    echo "== --self-test-all =="
    "$0" --self-test-all || CA_FAIL=1
    echo ""
  fi
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
    echo "== pass-header (canonical pass artifact vs real pass-dependencies.md §3) =="
    if [ -f "$CA_BASE/example-pass-artifact-header.md" ] && [ -f "$CA_BASE/pass-dependencies.md" ]; then
      "$0" pass-header "$CA_BASE/example-pass-artifact-header.md" "$CA_BASE/pass-dependencies.md" || CA_FAIL=1
    else
      echo "ERROR: $CA_BASE/example-pass-artifact-header.md or pass-dependencies.md not found"; CA_FAIL=1
    fi
    echo ""
    echo "== results-guide (canonical example-results-guide run folder vs real §3) =="
    if [ -d "$CA_BASE/example-results-guide" ]; then
      "$0" results-guide "$CA_BASE/example-results-guide" || CA_FAIL=1
    else
      echo "ERROR: $CA_BASE/example-results-guide not found"; CA_FAIL=1
    fi
    echo ""
    echo "== position-pair-register (canonical example-position-pair-register fixture) =="
    # The consumer fixture lives beside the shim, under specialized-audits/references (NOT core-editor).
    # Resolve either mirror root the same way CA_BASE does.
    PPR_BASE=""
    for base in "$CA_SCRIPT_DIR/../skills/specialized-audits/references" \
                "$CA_SCRIPT_DIR/../plugins/apodictic/skills/specialized-audits/references"; do
      if [ -d "$base/example-position-pair-register" ]; then PPR_BASE="$base/example-position-pair-register"; break; fi
    done
    if [ -n "$PPR_BASE" ]; then
      "$0" position-pair-register \
        "$PPR_BASE/Example_Position_Pair_Register_run.md" \
        "$PPR_BASE/envelope.json" \
        "$PPR_BASE/manuscript.txt" --strict || CA_FAIL=1
    else
      echo "ERROR: example-position-pair-register fixture not found"; CA_FAIL=1
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
      # editor↔author dual-output (docs/editor-scaffolding.md §Dual-output): the same diagnosis
      # emitted as the scaffolded editor letter AND its author-facing companion — D1 editor side
      # (E1-E4), D2 author register (no editor marker / no editor-only sections + a Revision
      # Checklist anchor), D3 top-severity-band consistency (both Must-Fix).
      if [ -f "$CA_BASE/example-editorial-letter-dual-author.md" ]; then
        "$0" editor-scaffolding --dual "$CA_BASE/example-editorial-letter-scaffolded.md" "$CA_BASE/example-editorial-letter-dual-author.md" || CA_FAIL=1
      else
        echo "ERROR: $CA_BASE/example-editorial-letter-dual-author.md not found"; CA_FAIL=1
      fi
      # per-pass scaffolding (docs/editor-scaffolding.md §Per-pass scaffolding): the SAME reframe
      # over an individual PASS artifact (not the letter) — P1 Editor Note, P2 What-You-Might-Have-
      # Missed, clean W1 firewall under --strict. The pass example is coherent with the letter above
      # (same manuscript, same middle-third Must-Fix).
      if [ -f "$CA_BASE/example-pass-scaffolded.md" ]; then
        "$0" editor-scaffolding --per-pass "$CA_BASE/example-pass-scaffolded.md" --strict || CA_FAIL=1
      else
        echo "ERROR: $CA_BASE/example-pass-scaffolded.md not found"; CA_FAIL=1
      fi
    else
      echo "ERROR: $CA_BASE/example-editorial-letter-scaffolded.md not found"; CA_FAIL=1
    fi
    echo ""
    echo "== canonical blind-spot ordering (editor-scaffolding ranked E2, verified vs the run folder's Ledger) =="
    # docs/editor-scaffolding.md §Future increments -> built: the opt-in <!-- blindspot-ranked -->
    # "What You Might Have Missed" section, ordered by severity band desc then fewer distinct
    # evidence_refs first, verified against the folder's Findings Ledger (B1 anchored+resolvable,
    # B2 order, B3 severity fidelity, B4 no duplicate anchor) under --strict.
    if [ -d "$CA_BASE/example-blindspot-ranked" ]; then
      "$0" editor-scaffolding "$CA_BASE/example-blindspot-ranked" --strict || CA_FAIL=1
    else
      echo "ERROR: $CA_BASE/example-blindspot-ranked not found"; CA_FAIL=1
    fi
    echo ""
    echo "== canonical Vocabulary Guide (diagnostic-vocabulary: glossary grounding + question framing) =="
    if [ -f "$CA_BASE/example-vocabulary-guide.md" ]; then
      "$0" diagnostic-vocabulary "$CA_BASE/example-vocabulary-guide.md" || CA_FAIL=1
    else
      echo "ERROR: $CA_BASE/example-vocabulary-guide.md not found"; CA_FAIL=1
    fi
    echo ""
    echo "== canonical example ledger <-> letter (both directions: structured-findings on the ledger + finding-trace forward refs + softness-check reverse delivery; deficit-lock structured locks) =="
    if [ -f "$CA_BASE/example-findings-ledger.md" ]; then
      "$0" structured-findings "$CA_BASE/example-findings-ledger.md" || CA_FAIL=1
      "$0" finding-trace "$CA_BASE/example-findings-ledger.md" "$CA_BASE/example-editorial-letter.md" || CA_FAIL=1
      "$0" softness-check "$CA_BASE/example-editorial-letter.md" "$CA_BASE/example-findings-ledger.md" || CA_FAIL=1
      "$0" deficit-lock "$CA_BASE/example-findings-ledger.md" || CA_FAIL=1
    else
      echo "ERROR: $CA_BASE/example-findings-ledger.md not found"; CA_FAIL=1
    fi
    echo ""
    echo "== canonical Feedback Triage (feedback-triage: contract + conflict integrity + maps_to cross-check vs the ledger) =="
    if [ -f "$CA_BASE/example-feedback-triage.md" ] && [ -f "$CA_BASE/example-findings-ledger.md" ]; then
      # Increment 2: paired with the canonical Findings Ledger so the maps_to cross-check engages —
      # FB-01.maps_to=F-RR-01 resolves (no E5) and no fully-validated item is left unmapped (no W4).
      "$0" feedback-triage "$CA_BASE/example-feedback-triage.md" "$CA_BASE/example-findings-ledger.md" --strict || CA_FAIL=1
    else
      echo "ERROR: $CA_BASE/example-feedback-triage.md or example-findings-ledger.md not found"; CA_FAIL=1
    fi
    echo ""
    echo "== canonical Retcon Plan (retcon-plan: commitment-budget + fair-play + target integrity + ranked selection) =="
    if [ -f "$CA_BASE/example-retcon-plan.md" ]; then
      "$0" retcon-plan "$CA_BASE/example-retcon-plan.md" || CA_FAIL=1
    else
      echo "ERROR: $CA_BASE/example-retcon-plan.md not found"; CA_FAIL=1
    fi
    echo ""
    echo "== canonical Revision Arc (revision-arc: self-consistency + provenance + firewall over the phased multi-week arc) =="
    if [ -f "$CA_BASE/example-revision-arc.md" ]; then
      "$0" revision-arc "$CA_BASE/example-revision-arc.md" --strict || CA_FAIL=1
    else
      echo "ERROR: $CA_BASE/example-revision-arc.md not found"; CA_FAIL=1
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
    echo "== canonical Setup–Payoff Ledger (setup-payoff: SP1 schema over both block kinds + SP2 referential integrity + SP3 open rationale + SP4 derived-state agreement + clean X1 firewall; three valid states pass, abandoned row surfaced for prose citation) =="
    if [ -f "$CA_BASE/example-setup-payoff-ledger.md" ]; then
      "$0" setup-payoff "$CA_BASE/example-setup-payoff-ledger.md" --strict || CA_FAIL=1
    else
      echo "ERROR: $CA_BASE/example-setup-payoff-ledger.md not found"; CA_FAIL=1
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
    echo "== canonical Coaching History (coaching-history: H1 schema+floor + H2 provenance/consecutive + H3 descriptive + H4 no-severity-leak + H7 tentative-framing + H5 single-home + H6 deletion-honored, under --strict) =="
    if [ -d "$CA_BASE/example-coaching-history" ]; then
      # Positive: the opted-in project (one Coaching_History artifact, grounded observations, clean
      # sidecar) PASSES clean under --strict — this is the C5 canonical-gate invocation.
      "$0" coaching-history "$CA_BASE/example-coaching-history" --strict || { echo "ERROR: canonical coaching-history did not PASS"; CA_FAIL=1; }
      # Hostile arms — the two Fable ethics gates against the spec's hostile fixtures, built as temp
      # copies of the canonical project and mutated (the disposition-check hostile-arm pattern). Each
      # MUST FAIL; a PASS is a firewall breach. `|| true` guards the intended-nonzero exit under set -e.
      CHH_HIST="Example_Coaching_History_2026-03-01_opus48.md"
      # (H5.i) a Session_Plan carrying a projected observation block — the projection leak
      CHH_T=$(mktemp -d); cp -R "$CA_BASE/example-coaching-history/." "$CHH_T/"
      printf '# Session Plan\n\n<!-- apodictic:coaching_observation\n{"schema": "apodictic.coaching_observation.v1", "id": "CH-01", "pattern": "deferral-recurrence", "count": 3, "evidence": ["F-P2-03 deferred @ session 1", "F-P2-03 deferred @ session 2", "F-P2-03 deferred @ session 3"], "observation": "leaked"}\n-->\n' > "$CHH_T/Session_Plan_01.md"
      if "$0" coaching-history "$CHH_T" >/dev/null 2>&1; then echo "ERROR: H5.i projection leak (Session_Plan observation block) did not FAIL"; CA_FAIL=1; else echo "  H5.i projection-leak fixture: FAIL as required (OK)"; fi
      rm -rf "$CHH_T"
      # (Codex F1 REGRESSION) a projection into an UNLISTED artifact type (the editorial letter — the old
      # authored-artifact allowlist covered 6 of ~46 types, so this ESCAPED H5 and survived `delete`).
      # Now every *.md in scope is scanned: the projection must FAIL H5, and after `delete` the H6
      # recompute must CATCH the surviving projection (NOT falsely report "deletion honored").
      CHH_T=$(mktemp -d); cp -R "$CA_BASE/example-coaching-history/." "$CHH_T/"
      printf '# Editorial Letter\n\n<!-- apodictic:coaching_observation\n{"schema": "apodictic.coaching_observation.v1", "id": "CH-01", "pattern": "deferral-recurrence", "count": 3, "evidence": ["F-P2-03 deferred @ session 1", "F-P2-03 deferred @ session 2", "F-P2-03 deferred @ session 3"], "observation": "leaked into the letter"}\n-->\n' > "$CHH_T/Example_Editorial_Letter_2026-03-01_opus48.md"
      if "$0" coaching-history "$CHH_T" >/dev/null 2>&1; then echo "ERROR: F1 editorial-letter projection did not FAIL H5"; CA_FAIL=1; else echo "  F1 editorial-letter projection: FAIL as required (OK)"; fi
      "$0" coaching-history delete "$CHH_T" >/dev/null 2>&1 || true   # delete removes the artifact+seq+tombstone, NOT the letter projection
      if "$0" coaching-history "$CHH_T" >/dev/null 2>&1; then echo "ERROR: F1 H6 recompute falsely reported deletion honored with a surviving letter projection"; CA_FAIL=1; else echo "  F1 H6 recompute catches surviving letter projection: FAIL as required (OK)"; fi
      rm -rf "$CHH_T"
      # (H5.v) a sidecar coach-only shadow field — execution.coaching_notes
      CHH_T=$(mktemp -d); cp -R "$CA_BASE/example-coaching-history/." "$CHH_T/"
      python3 - "$CHH_T/Diagnostic_State.meta.json" <<'PY' 2>/dev/null || true
import json,sys
p=sys.argv[1]; sc=json.load(open(p)); sc.setdefault("execution",{})["coaching_notes"]={"CH-01":"the writer keeps deferring"}
json.dump(sc,open(p,"w"),indent=2)
PY
      if "$0" coaching-history "$CHH_T" >/dev/null 2>&1; then echo "ERROR: H5.v sidecar shadow field (coaching_notes) did not FAIL"; CA_FAIL=1; else echo "  H5.v sidecar-shadow fixture: FAIL as required (OK)"; fi
      rm -rf "$CHH_T"
      # (H5.iv) TWO Coaching_History artifacts — the shadow artifact
      CHH_T=$(mktemp -d); cp -R "$CA_BASE/example-coaching-history/." "$CHH_T/"
      cp "$CHH_T/$CHH_HIST" "$CHH_T/Example_Coaching_History_2026-02-01_opus47.md"
      if "$0" coaching-history "$CHH_T" >/dev/null 2>&1; then echo "ERROR: H5.iv two Coaching_History artifacts did not FAIL"; CA_FAIL=1; else echo "  H5.iv two-artifact fixture: FAIL as required (OK)"; fi
      rm -rf "$CHH_T"
      # (H6) a tombstoned project with an archived session plan still carrying the evidence grammar
      CHH_T=$(mktemp -d); cp -R "$CA_BASE/example-coaching-history/." "$CHH_T/"
      rm -f "$CHH_T/$CHH_HIST"
      python3 - "$CHH_T/Diagnostic_State.md" "$CHH_T/Diagnostic_State.meta.json" <<'PY' 2>/dev/null || true
import json,re,sys
sm=sys.argv[1]; t=open(sm).read()
open(sm,"w").write(re.sub(r"<!--\s*coaching-history:\s*opted-in\s*-->","<!-- coaching-history: deleted -->",t))
p=sys.argv[2]; sc=json.load(open(p)); sc.pop("coaching_history_seq",None); json.dump(sc,open(p,"w"),indent=2)
PY
      mkdir -p "$CHH_T/runs/r4_coaching"
      printf '# Archived Session Plan\n\nF-P2-03 deferred @ session 2\n' > "$CHH_T/runs/r4_coaching/Session_Plan_03.md"
      if "$0" coaching-history "$CHH_T" >/dev/null 2>&1; then echo "ERROR: H6 archived deletion-residue did not FAIL"; CA_FAIL=1; else echo "  H6 archived-residue fixture: FAIL as required (OK)"; fi
      rm -rf "$CHH_T"
      # (H6) opted-in + deleted both present = contradictory consent state
      CHH_T=$(mktemp -d); cp -R "$CA_BASE/example-coaching-history/." "$CHH_T/"
      printf '\n<!-- coaching-history: deleted -->\n' >> "$CHH_T/Diagnostic_State.md"
      if "$0" coaching-history "$CHH_T" >/dev/null 2>&1; then echo "ERROR: H6 opted-in+deleted contradiction did not FAIL"; CA_FAIL=1; else echo "  H6 consent-contradiction fixture: FAIL as required (OK)"; fi
      rm -rf "$CHH_T"
      # (H6 positive + delete round-trip) run `delete` on a fresh copy, then the recompute must PASS
      CHH_T=$(mktemp -d); cp -R "$CA_BASE/example-coaching-history/." "$CHH_T/"
      "$0" coaching-history delete "$CHH_T" >/dev/null 2>&1 || { echo "ERROR: coaching-history delete failed"; CA_FAIL=1; }
      "$0" coaching-history "$CHH_T" >/dev/null 2>&1 && echo "  H6 delete-round-trip recompute: PASS as required (OK)" || { echo "ERROR: H6 recompute after delete did not PASS (a clean deletion must recompute honored)"; CA_FAIL=1; }
      rm -rf "$CHH_T"
      # (Codex round-1 P1) a FABRICATED phase-incompletion at non-existent sessions 101/102 with NO
      # honesty caveat — phase-incompletion has no governed verification path, so it is self-reported and
      # MUST carry the caveat. Without it, --strict must FAIL (the exact Codex repro).
      CHH_T=$(mktemp -d); cp -R "$CA_BASE/example-coaching-history/." "$CHH_T/"
      printf '# Coaching History\n<!-- coaching-history: opted-in -->\n<!-- apodictic:coaching_observation\n{"schema": "apodictic.coaching_observation.v1", "id": "CH-01", "pattern": "phase-incompletion", "count": 2, "evidence": ["phase Structural Root Causes incomplete @ session 101", "phase Structural Root Causes incomplete @ session 102"], "observation": "The structural phase stayed open. Does that track?"}\n-->\n' > "$CHH_T/$CHH_HIST"
      if "$0" coaching-history "$CHH_T" --strict >/dev/null 2>&1; then echo "ERROR: P1 fabricated phase-incompletion (101/102, no caveat) did not FAIL --strict"; CA_FAIL=1; else echo "  P1 fabricated phase-incompletion (no caveat): FAIL --strict as required (OK)"; fi
      rm -rf "$CHH_T"
      # (Codex round-1 P2) a coaching_history_seq nested at a NON-HOME depth (last_session.*) survives
      # `delete` in the naive two-home strip and the H6 recompute falsely honors. The recursive strip +
      # depth-complete recompute must (a) remove it on delete and (b) CATCH it if it survives.
      CHH_T=$(mktemp -d); cp -R "$CA_BASE/example-coaching-history/." "$CHH_T/"
      python3 - "$CHH_T/Diagnostic_State.md" "$CHH_T/Diagnostic_State.meta.json" "$CHH_T/$CHH_HIST" <<'PY' 2>/dev/null || true
import json,re,sys
sm=sys.argv[1]; t=open(sm).read()
open(sm,"w").write(re.sub(r"<!--\s*coaching-history:\s*opted-in\s*-->","<!-- coaching-history: deleted -->",t))
p=sys.argv[2]; sc=json.load(open(p)); sc.pop("coaching_history_seq",None); sc.setdefault("last_session",{})["coaching_history_seq"]=9
json.dump(sc,open(p,"w"),indent=2)
import os; os.remove(sys.argv[3])
PY
      if "$0" coaching-history "$CHH_T" >/dev/null 2>&1; then echo "ERROR: P2 nested-depth seq residue survived delete and H6 falsely honored"; CA_FAIL=1; else echo "  P2 nested-depth seq residue caught by H6 recompute: FAIL as required (OK)"; fi
      rm -rf "$CHH_T"
    else
      echo "ERROR: $CA_BASE/example-coaching-history not found"; CA_FAIL=1
    fi
    echo ""
    echo "== canonical Author Style Explanation (style-explanation: schema X1 + provenance X2 + no-severity X3 + descriptive-not-prescriptive X4 + same-register cluster X5 + clean X6/W1, under --strict) =="
    if [ -f "$CA_BASE/example-author-style-explanation.md" ]; then
      "$0" style-explanation "$CA_BASE/example-author-style-explanation.md" --strict || CA_FAIL=1
    else
      echo "ERROR: $CA_BASE/example-author-style-explanation.md not found"; CA_FAIL=1
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
    echo "== canonical genre-profiled Argument_States (argument-spine Inc 5: B1-B4 + W4-W5 over grant / academic / pitch; --strict) =="
    # grant runs via an explicit LITERAL path (not the $GENRE_FIX loop) so schema-coverage's C5 can trace
    # example-argument-state-genre-grant.md to a real argument-spine invocation: it is the
    # apodictic.genre_profile.v1 canonical_gate (the predraft Argument_State carries no genre_profile
    # block; the genre files do — C5's one-hop resolver can't see through the loop's double variable).
    if [ -f "$CA_BASE/example-argument-state-genre-grant.md" ]; then
      "$0" argument-spine "$CA_BASE/example-argument-state-genre-grant.md" --strict || CA_FAIL=1
    else
      echo "ERROR: $CA_BASE/example-argument-state-genre-grant.md not found"; CA_FAIL=1
    fi
    for GENRE_FIX in academic pitch; do
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
    echo "== canonical Structure Map manifest (manuscript-viz: manifest<->source provenance vs Timeline + Ledger + claim-ladder spine + co-presence roster + scene-function producer + tension-point producer + story-spine producer) =="
    if [ -f "$CA_BASE/example-structure-map-manifest.md" ] && [ -f "$CA_BASE/example-timeline.md" ] && [ -f "$CA_BASE/example-findings-ledger.md" ] && [ -f "$CA_BASE/example-argument-state-predraft.md" ] && [ -f "$CA_BASE/example-scene-roster.md" ] && [ -f "$CA_BASE/example-scene-function.md" ] && [ -f "$CA_BASE/example-tension-points.md" ] && [ -f "$CA_BASE/example-story-spine.md" ]; then
      "$0" manuscript-viz "$CA_BASE/example-structure-map-manifest.md" "$CA_BASE/example-timeline.md" "$CA_BASE/example-findings-ledger.md" "$CA_BASE/example-argument-state-predraft.md" "$CA_BASE/example-scene-roster.md" "$CA_BASE/example-scene-function.md" "$CA_BASE/example-tension-points.md" "$CA_BASE/example-story-spine.md" --require-block || CA_FAIL=1
    else
      echo "ERROR: $CA_BASE/example-structure-map-manifest.md / example-timeline.md / example-findings-ledger.md / example-argument-state-predraft.md / example-scene-roster.md / example-scene-function.md / example-tension-points.md / example-story-spine.md not found"; CA_FAIL=1
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
    echo "== canonical roundtrip-disposition (record vs live recompute: RT1-RT4 + hostile arms) =="
    if [ -d "$CA_BASE/example-annotated-manuscript" ] && [ -f "$CA_BASE/example-reanchor-revised.md" ] \
       && [ -f "$CA_BASE/example-roundtrip-disposition.md" ] && [ -f "$CA_BASE/example-roundtrip-revision-report.md" ] \
       && command -v python3 >/dev/null 2>&1; then
      # Stage the disposition round-close on temp copies (extending the round-trip glue chain above):
      # a prior folder holding the canonical manifest + ledger, the revised snapshot (runlabel
      # reanchor-r2), and a "this round" folder holding the round-2 ledger + the canonical disposition
      # record + companion Revision Report. The committed fixture rows are RECOMPUTE-CONSISTENT with
      # these exact inputs, so `roundtrip-disposition` must PASS with no W1. Then the HOSTILE arms
      # (AGENTS.md review practice): a token-stripped copy must FAIL RT2, an extra unconfirmed
      # resolved marker in the report copy must FAIL RT3, and a copy with one finding's disposition
      # row dropped must WARN RT4 by default (exit 0, missing id named) and FAIL under --strict —
      # asserted on exit codes + the RT ids in stdout (the reanchor-fixture pattern).
      CA_RTD=$(mktemp -d)
      CA_RTD_PRI="$CA_RTD/prior"; CA_RTD_CUR="$CA_RTD/current"
      mkdir "$CA_RTD_PRI" "$CA_RTD_CUR"
      cp "$CA_BASE/example-annotated-manuscript"/*_Annotation_Manifest_*.md "$CA_RTD_PRI"/ 2>/dev/null
      cp "$CA_BASE/example-annotated-manuscript"/*_Findings_Ledger_*.md "$CA_RTD_PRI"/ 2>/dev/null
      cp "$CA_BASE/example-reanchor-revised.md" "$CA_RTD/Example_Manuscript_Snapshot_reanchor-r2.md"
      cp "$CA_BASE/example-run-folder-r2"/*_Findings_Ledger_*.md "$CA_RTD_CUR"/ 2>/dev/null
      cp "$CA_BASE/example-roundtrip-disposition.md" "$CA_RTD_CUR/Example_Roundtrip_Disposition_reanchor-r2.md"
      cp "$CA_BASE/example-roundtrip-revision-report.md" "$CA_RTD_CUR/Example_Revision_Report_reanchor-r2.md"
      CA_RTD_OK=1
      CA_RTD_SNAP="$CA_RTD/Example_Manuscript_Snapshot_reanchor-r2.md"
      if RTD_OUT=$("$0" roundtrip-disposition "$CA_RTD_PRI" "$CA_RTD_SNAP" "$CA_RTD_CUR" 2>&1); then
        printf '%s' "$RTD_OUT" | grep -q "disposition:confirm-resolved F-RR-01" || CA_RTD_OK=0
        printf '%s' "$RTD_OUT" | grep -q "record of confirmation present and consistent" || CA_RTD_OK=0
        if printf '%s' "$RTD_OUT" | grep -q "W1"; then CA_RTD_OK=0; fi
      else
        CA_RTD_OK=0
      fi
      # Hostile arm 1: strip the confirmation token -> RT2 must FAIL (decided rows, no recorded token).
      CA_RTD_H1="$CA_RTD/hostile-rt2"
      mkdir "$CA_RTD_H1"
      cp "$CA_RTD_CUR"/*_Findings_Ledger_*.md "$CA_RTD_H1"/ 2>/dev/null
      cp "$CA_RTD_CUR/Example_Revision_Report_reanchor-r2.md" "$CA_RTD_H1"/
      grep -v "disposition-confirmed:" "$CA_RTD_CUR/Example_Roundtrip_Disposition_reanchor-r2.md" \
        > "$CA_RTD_H1/Example_Roundtrip_Disposition_reanchor-r2.md"
      if RTD_OUT=$("$0" roundtrip-disposition "$CA_RTD_PRI" "$CA_RTD_SNAP" "$CA_RTD_H1" 2>&1); then
        CA_RTD_OK=0
      else
        printf '%s' "$RTD_OUT" | grep -q "RT2" || CA_RTD_OK=0
      fi
      # Hostile arm 2: an extra resolved marker for a keep-open finding -> RT3 must FAIL (the
      # vanished-anchor auto-close class this gate exists to prevent).
      CA_RTD_H2="$CA_RTD/hostile-rt3"
      mkdir "$CA_RTD_H2"
      cp "$CA_RTD_CUR"/*_Findings_Ledger_*.md "$CA_RTD_H2"/ 2>/dev/null
      cp "$CA_RTD_CUR/Example_Roundtrip_Disposition_reanchor-r2.md" "$CA_RTD_H2"/
      { cat "$CA_RTD_CUR/Example_Revision_Report_reanchor-r2.md"; echo "<!-- resolved: F-QT-01 -->"; } \
        > "$CA_RTD_H2/Example_Revision_Report_reanchor-r2.md"
      if RTD_OUT=$("$0" roundtrip-disposition "$CA_RTD_PRI" "$CA_RTD_SNAP" "$CA_RTD_H2" 2>&1); then
        CA_RTD_OK=0
      else
        printf '%s' "$RTD_OUT" | grep -q "RT3" || CA_RTD_OK=0
      fi
      # Hostile arm 3: drop one finding's disposition row entirely (the silently-omitted-finding
      # hole) -> RT4 must WARN by default (exit 0, the missing id named) and FAIL under --strict —
      # a partial record must never read as round-close clean.
      CA_RTD_H3="$CA_RTD/hostile-rt4"
      mkdir "$CA_RTD_H3"
      cp "$CA_RTD_CUR"/*_Findings_Ledger_*.md "$CA_RTD_H3"/ 2>/dev/null
      cp "$CA_RTD_CUR/Example_Revision_Report_reanchor-r2.md" "$CA_RTD_H3"/
      grep -v "disposition: F-QT-01" "$CA_RTD_CUR/Example_Roundtrip_Disposition_reanchor-r2.md" \
        > "$CA_RTD_H3/Example_Roundtrip_Disposition_reanchor-r2.md"
      if RTD_OUT=$("$0" roundtrip-disposition "$CA_RTD_PRI" "$CA_RTD_SNAP" "$CA_RTD_H3" 2>&1); then
        printf '%s' "$RTD_OUT" | grep -q "RT4 partition coverage: F-QT-01" || CA_RTD_OK=0
      else
        CA_RTD_OK=0
      fi
      if RTD_OUT=$("$0" roundtrip-disposition "$CA_RTD_PRI" "$CA_RTD_SNAP" "$CA_RTD_H3" --strict 2>&1); then
        CA_RTD_OK=0
      else
        printf '%s' "$RTD_OUT" | grep -q "RT4" || CA_RTD_OK=0
      fi
      if [ "$CA_RTD_OK" -eq 1 ]; then
        echo "roundtrip-disposition (canonical + hostile arms): PASS"
      else
        echo "roundtrip-disposition (canonical + hostile arms): FAIL"; CA_FAIL=1
      fi
      rm -rf "$CA_RTD"
    elif [ ! -f "$CA_BASE/example-roundtrip-disposition.md" ] || [ ! -f "$CA_BASE/example-roundtrip-revision-report.md" ]; then
      echo "ERROR: $CA_BASE/example-roundtrip-disposition.md + example-roundtrip-revision-report.md not found (roundtrip-disposition)"; CA_FAIL=1
    fi
    echo ""
    echo "== canonical disposition-check (finding dispositions: DP0 shape + DP1 caveat + DP2 no-laundering + hostile arms) =="
    if [ -d "$CA_BASE/example-run-folder-dispositions" ] && command -v python3 >/dev/null 2>&1; then
      # The committed fixture (a NON-governed sidecar + Coaching Log markers + a readiness-caveat
      # excerpt) must PASS clean — including --strict (the marker/sidecar sync holds). Then the
      # HOSTILE arms (AGENTS.md review practice), each on a temp copy: (1) the severity-laundering
      # attempt — strip the Declined caveat line from the assessment; a declined Must-Fix must
      # still force the /ready caveat, so DP1 must FAIL naming F-P5-01; (2) deferred-without-
      # trigger refused — drop the trigger from the deferred record; DP0 must FAIL; (3) marker/
      # sidecar desync caught — drop one record; DP2.5 must WARN by default (exit 0, id named)
      # and FAIL under --strict; (4) fabricated supersedence — flip the declined id's
      # finding_states to 'revised' (no completion artifact corroborates it) and strip its caveat
      # line; the recompute must keep the disposition ACTIVE, so DP1 must FAIL naming F-P5-01 and
      # DP2.6 must name the uncorroborated supersedence (pre-recompute this exact shape exited 0
      # — the PR #161 recorded-field class, docs/disposition-supersedence-recompute.md).
      CA_DPC_SRC="$CA_BASE/example-run-folder-dispositions"
      CA_DPC_OK=1
      "$0" disposition-check "$CA_DPC_SRC" >/dev/null 2>&1 || CA_DPC_OK=0
      "$0" disposition-check "$CA_DPC_SRC" --strict >/dev/null 2>&1 || CA_DPC_OK=0
      CA_DPC=$(mktemp -d)
      # Hostile arm 1 (DP1 severity-laundering): assessment without the Declined caveat line.
      cp -R "$CA_DPC_SRC" "$CA_DPC/h1"
      grep -v '^\*\*Declined Must-Fixes:\*\*' "$CA_DPC_SRC/Submission_Readiness_Assessment_2026-03-01.md" \
        > "$CA_DPC/h1/Submission_Readiness_Assessment_2026-03-01.md"
      if DPC_OUT=$("$0" disposition-check "$CA_DPC/h1" 2>&1); then
        CA_DPC_OK=0
      else
        printf '%s' "$DPC_OUT" | grep -q "DP1 declined Must-Fix F-P5-01" || CA_DPC_OK=0
      fi
      # Hostile arm 2 (DP0): the deferred record stripped of its trigger.
      cp -R "$CA_DPC_SRC" "$CA_DPC/h2"
      python3 - "$CA_DPC/h2/Diagnostic_State.meta.json" <<'PY' >/dev/null 2>&1 || CA_DPC_OK=0
import json, sys
p = sys.argv[1]
m = json.load(open(p, encoding="utf-8"))
del m["execution"]["finding_dispositions"]["F-DP-02"]["trigger"]
json.dump(m, open(p, "w", encoding="utf-8"), indent=2)
PY
      if DPC_OUT=$("$0" disposition-check "$CA_DPC/h2" 2>&1); then
        CA_DPC_OK=0
      else
        printf '%s' "$DPC_OUT" | grep -q "DP0" || CA_DPC_OK=0
      fi
      # Hostile arm 3 (DP2.5): one record dropped -> WARN by default (id named), FAIL --strict.
      cp -R "$CA_DPC_SRC" "$CA_DPC/h3"
      python3 - "$CA_DPC/h3/Diagnostic_State.meta.json" <<'PY' >/dev/null 2>&1 || CA_DPC_OK=0
import json, sys
p = sys.argv[1]
m = json.load(open(p, encoding="utf-8"))
del m["execution"]["finding_dispositions"]["F-P5-01"]
json.dump(m, open(p, "w", encoding="utf-8"), indent=2)
PY
      if DPC_OUT=$("$0" disposition-check "$CA_DPC/h3" 2>&1); then
        printf '%s' "$DPC_OUT" | grep -q "DP2.5 marker without record.*F-P5-01" || CA_DPC_OK=0
      else
        CA_DPC_OK=0
      fi
      "$0" disposition-check "$CA_DPC/h3" --strict >/dev/null 2>&1 && CA_DPC_OK=0 || true
      # Hostile arm 4 (DP2.6/DP1 fabricated supersedence): sidecar-only 'revised' + stripped caveat.
      cp -R "$CA_DPC_SRC" "$CA_DPC/h4"
      python3 - "$CA_DPC/h4/Diagnostic_State.meta.json" <<'PY' >/dev/null 2>&1 || CA_DPC_OK=0
import json, sys
p = sys.argv[1]
m = json.load(open(p, encoding="utf-8"))
m["execution"]["finding_states"]["F-P5-01"] = "revised"
json.dump(m, open(p, "w", encoding="utf-8"), indent=2)
PY
      grep -v '^\*\*Declined Must-Fixes:\*\*' "$CA_DPC_SRC/Submission_Readiness_Assessment_2026-03-01.md" \
        > "$CA_DPC/h4/Submission_Readiness_Assessment_2026-03-01.md"
      if DPC_OUT=$("$0" disposition-check "$CA_DPC/h4" 2>&1); then
        CA_DPC_OK=0
      else
        printf '%s' "$DPC_OUT" | grep -q "DP1 declined Must-Fix F-P5-01" || CA_DPC_OK=0
        printf '%s' "$DPC_OUT" | grep -q "DP2.6" || CA_DPC_OK=0
      fi
      if [ "$CA_DPC_OK" -eq 1 ]; then
        echo "disposition-check (canonical + hostile arms): PASS"
      else
        echo "disposition-check (canonical + hostile arms): FAIL"; CA_FAIL=1
      fi
      rm -rf "$CA_DPC"
    elif [ ! -d "$CA_BASE/example-run-folder-dispositions" ]; then
      echo "ERROR: $CA_BASE/example-run-folder-dispositions not found (disposition-check)"; CA_FAIL=1
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
      # The committed .docx golden lives in evals/ (binaries stay out of the plugin folder, which the
      # Claude plugin directory holds for review). Inside the repo the golden is required (a missing one
      # fails the cmp below); only a standalone plugin install, with no evals/ at all, skips the byte-compare.
      CA_DXE_GOLD=""
      for cand in "$CA_SCRIPT_DIR/../../../evals" "$CA_SCRIPT_DIR/../evals"; do
        if [ -d "$cand" ]; then CA_DXE_GOLD="$cand/fixtures/annotation-export/docx"; break; fi
      done
      CA_DXE=$(mktemp -d)
      cp "$CA_DXE_SRC"/*_Manuscript_Snapshot_*.md "$CA_DXE_SRC"/*_Annotation_Manifest_*.md "$CA_DXE"/ 2>/dev/null
      CA_DXE_OK=1
      python3 "$CA_SCRIPT_DIR/annotation_export.py" docx "$CA_DXE" >/dev/null 2>&1 || CA_DXE_OK=0
      "$0" docx-export "$CA_DXE" >/dev/null 2>&1 || CA_DXE_OK=0
      CA_DXE_N=0
      for CA_DXE_F in "$CA_DXE"/docx/*.docx; do
        if [ -f "$CA_DXE_F" ]; then
          CA_DXE_N=$((CA_DXE_N + 1))
          if [ -n "$CA_DXE_GOLD" ]; then
            cmp -s "$CA_DXE_F" "$CA_DXE_GOLD/$(basename "$CA_DXE_F")" || CA_DXE_OK=0
          fi
        else
          CA_DXE_OK=0
        fi
      done
      [ "$CA_DXE_N" -eq 1 ] || CA_DXE_OK=0
      if [ "$CA_DXE_OK" -eq 1 ]; then
        if [ -n "$CA_DXE_GOLD" ]; then echo "docx-export (temp copy): PASS"; else echo "docx-export (temp copy): PASS (golden not found; byte-compare skipped)"; fi
      else
        echo "docx-export (temp copy): FAIL"; CA_FAIL=1
      fi
      rm -rf "$CA_DXE"
    else
      echo "ERROR: $CA_BASE/example-annotated-manuscript not found (docx-export)"; CA_FAIL=1
    fi
    echo ""
    echo "== canonical pdf-export (manifest -> self-contained .pdf; P1-P3 + byte-identical) =="
    if [ -d "$CA_BASE/example-annotated-manuscript" ] && command -v python3 >/dev/null 2>&1; then
      # Project the canonical manifest + snapshot to a .pdf on a temp copy (generate WRITES
      # pdf/<copy>.pdf, never in place), gate it (P1-P3), and assert the fresh byte-deterministic export
      # is byte-identical to the committed pdf/ fixture.
      CA_PXE_SRC="$CA_BASE/example-annotated-manuscript"
      # The committed .pdf golden lives in evals/ (binaries stay out of the plugin folder, which the
      # Claude plugin directory holds for review). Inside the repo the golden is required (a missing one
      # fails the cmp below); only a standalone plugin install, with no evals/ at all, skips the byte-compare.
      CA_PXE_GOLD=""
      for cand in "$CA_SCRIPT_DIR/../../../evals" "$CA_SCRIPT_DIR/../evals"; do
        if [ -d "$cand" ]; then CA_PXE_GOLD="$cand/fixtures/annotation-export/pdf"; break; fi
      done
      CA_PXE=$(mktemp -d)
      cp "$CA_PXE_SRC"/*_Manuscript_Snapshot_*.md "$CA_PXE_SRC"/*_Annotation_Manifest_*.md "$CA_PXE"/ 2>/dev/null
      CA_PXE_OK=1
      python3 "$CA_SCRIPT_DIR/annotation_export.py" pdf "$CA_PXE" >/dev/null 2>&1 || CA_PXE_OK=0
      "$0" pdf-export "$CA_PXE" >/dev/null 2>&1 || CA_PXE_OK=0
      CA_PXE_N=0
      for CA_PXE_F in "$CA_PXE"/pdf/*.pdf; do
        if [ -f "$CA_PXE_F" ]; then
          CA_PXE_N=$((CA_PXE_N + 1))
          if [ -n "$CA_PXE_GOLD" ]; then
            cmp -s "$CA_PXE_F" "$CA_PXE_GOLD/$(basename "$CA_PXE_F")" || CA_PXE_OK=0
          fi
        else
          CA_PXE_OK=0
        fi
      done
      [ "$CA_PXE_N" -eq 1 ] || CA_PXE_OK=0
      if [ "$CA_PXE_OK" -eq 1 ]; then
        if [ -n "$CA_PXE_GOLD" ]; then echo "pdf-export (temp copy): PASS"; else echo "pdf-export (temp copy): PASS (golden not found; byte-compare skipped)"; fi
      else
        echo "pdf-export (temp copy): FAIL"; CA_FAIL=1
      fi
      rm -rf "$CA_PXE"
    else
      echo "ERROR: $CA_BASE/example-annotated-manuscript not found (pdf-export)"; CA_FAIL=1
    fi
    echo ""
    echo "== canonical reader-contract-outline (R1-R7 over fiction + narrative-nf fixtures; producer chain; hostile arms) =="
    # Reader-Contract Reverse Outline deliverable (docs/reader-contract-outline.md, SPEC v3.1): the book
    # scene by scene mapped against its reader contract — a byte-deterministic PROJECTION of four inputs
    # (Pass 0, Contract, Ledger, Map), the model's only authored bytes the gated ids-only Contract Map.
    # The fixture dir holds TWO projects (Example = fiction, ExampleNF = narrative nf), so each is
    # validated on its own single-project staging copy (a real run folder holds one project; staging
    # keeps the newest-glob resolver from mixing the two). The canonical `example-reader-contract-outline`
    # token is passed to the `reader-contract-outline` validator (schema-coverage C5 reachability).
    if [ -d "$CA_BASE/example-reader-contract-outline" ] && command -v python3 >/dev/null 2>&1; then
      CA_RCO_SRC="$CA_BASE/example-reader-contract-outline"
      CA_RCO_OK=1
      CA_RCO_HELPER="$CA_SCRIPT_DIR/reader_contract_outline.py"
      # Canonical gate against the committed fixture, addressed through the canonical
      # `example-reader-contract-outline` path component (schema-coverage C5 reachability — the token
      # must reach a real, SINGLE-LINE invocation of the bound `reader-contract-outline` validator).
      # The validator's run resolver is project-aware, so pointing it at the two-project fixture dir
      # validates the fiction (Example) project deterministically without the ExampleNF files colliding.
      "$0" reader-contract-outline "$CA_RCO_SRC" >/dev/null 2>&1 || CA_RCO_OK=0
      for CA_RCO_PROJ in Example ExampleNF; do
        CA_RCO=$(mktemp -d)
        # stage only THIS project's four inputs (no committed outline — build regenerates it)
        cp "$CA_RCO_SRC/${CA_RCO_PROJ}_Pass0_Reverse_Outline_2026-01-01.md" \
           "$CA_RCO_SRC/${CA_RCO_PROJ}_Contract_2026-01-01.md" \
           "$CA_RCO_SRC/${CA_RCO_PROJ}_Findings_Ledger_2026-01-01.md" \
           "$CA_RCO_SRC/${CA_RCO_PROJ}_Contract_Map_2026-01-01.md" "$CA_RCO"/ 2>/dev/null
        # build (R7-gate the Map, then project the outline) + validate the fresh outline
        python3 "$CA_RCO_HELPER" build "$CA_RCO" >/dev/null 2>&1 || CA_RCO_OK=0
        "$0" reader-contract-outline "$CA_RCO" >/dev/null 2>&1 || CA_RCO_OK=0
        # fresh build == committed outline, byte-for-byte (proves the committed fixture is what a fresh
        # build emits — no hand drift)
        if [ -f "$CA_RCO/${CA_RCO_PROJ}_Reader_Contract_Outline_2026-01-01.md" ]; then
          cmp -s "$CA_RCO/${CA_RCO_PROJ}_Reader_Contract_Outline_2026-01-01.md" \
                 "$CA_RCO_SRC/${CA_RCO_PROJ}_Reader_Contract_Outline_2026-01-01.md" || CA_RCO_OK=0
        else
          CA_RCO_OK=0
        fi
        rm -rf "$CA_RCO"
      done
      # Also drive the C5 canonical-gate token through the validator against the fiction project via a
      # single-project staging dir under the canonical basename (the token schema-coverage C5 requires).
      # Hostile arms (derived in-place from the fiction fixture; never committed — the disposition-check
      # precedent). Each MUST fail; a passing hostile means the gate went blind.
      CA_RCO_H=$(mktemp -d)
      cp "$CA_RCO_SRC"/Example_Pass0_Reverse_Outline_2026-01-01.md \
         "$CA_RCO_SRC"/Example_Contract_2026-01-01.md \
         "$CA_RCO_SRC"/Example_Findings_Ledger_2026-01-01.md \
         "$CA_RCO_SRC"/Example_Contract_Map_2026-01-01.md \
         "$CA_RCO_SRC"/Example_Reader_Contract_Outline_2026-01-01.md "$CA_RCO_H"/ 2>/dev/null
      # clean baseline passes (via the canonical example-reader-contract-outline dir token for C5)
      "$0" reader-contract-outline "$CA_RCO_H" >/dev/null 2>&1 || CA_RCO_OK=0
      CA_RCO_MAP="$CA_RCO_H/Example_Contract_Map_2026-01-01.md"
      CA_RCO_OUT="$CA_RCO_H/Example_Reader_Contract_Outline_2026-01-01.md"
      # Hostile R7: doctor inputs.contract_sha256 -> stale Map must FAIL (recompute-not-trust)
      CA_RCO_H7=$(mktemp -d); cp "$CA_RCO_H"/* "$CA_RCO_H7"/ 2>/dev/null
      python3 - "$CA_RCO_H7/Example_Contract_Map_2026-01-01.md" <<'PY'
import re, sys
p = sys.argv[1]
s = open(p).read()
s = re.sub(r'"contract_sha256": "[0-9a-f]{64}"', '"contract_sha256": "%s"' % ("0"*64), s)
open(p, "w").write(s)
PY
      if "$0" reader-contract-outline "$CA_RCO_H7" >/dev/null 2>&1; then
        echo "reader-contract-outline hostile R7 (stale sha256) did NOT fail"; CA_RCO_OK=0
      fi
      rm -rf "$CA_RCO_H7"
      # Hostile R3/R7: cite a nonexistent scene id in the Map -> must FAIL
      CA_RCO_H3=$(mktemp -d); cp "$CA_RCO_H"/* "$CA_RCO_H3"/ 2>/dev/null
      python3 - "$CA_RCO_H3/Example_Contract_Map_2026-01-01.md" <<'PY'
import sys
p = sys.argv[1]
s = open(p).read().replace('"established": ["S1"],', '"established": ["S99"],', 1)
open(p, "w").write(s)
PY
      if "$0" reader-contract-outline "$CA_RCO_H3" >/dev/null 2>&1; then
        echo "reader-contract-outline hostile R3 (nonexistent scene) did NOT fail"; CA_RCO_OK=0
      fi
      rm -rf "$CA_RCO_H3"
      # Hostile R4: paraphrase a gap cell in the rendered outline (not byte-matching the Ledger) -> FAIL
      CA_RCO_H4=$(mktemp -d); cp "$CA_RCO_H"/* "$CA_RCO_H4"/ 2>/dev/null
      python3 - "$CA_RCO_H4/Example_Reader_Contract_Outline_2026-01-01.md" <<'PY'
import sys
p = sys.argv[1]
s = open(p).read().replace("stated in the keeper's dialogue but never dramatized",
                           "not shown on the page", 1)
open(p, "w").write(s)
PY
      if "$0" reader-contract-outline "$CA_RCO_H4" >/dev/null 2>&1; then
        echo "reader-contract-outline hostile R4 (paraphrased gap) did NOT fail"; CA_RCO_OK=0
      fi
      rm -rf "$CA_RCO_H4"
      # Hostile R6: drop the 2nd READER PROMISE clause (renumber C1..C4) -> promise split incomplete;
      # WARN by default (exit 0), FAIL under --strict. Rebuild the outline from the mutated Map first.
      CA_RCO_H6=$(mktemp -d); cp "$CA_RCO_H"/* "$CA_RCO_H6"/ 2>/dev/null
      rm -f "$CA_RCO_H6/Example_Reader_Contract_Outline_2026-01-01.md"
      python3 - "$CA_RCO_H6/Example_Contract_Map_2026-01-01.md" <<'PY'
import json, re, sys
p = sys.argv[1]
s = open(p).read()
m = re.search(r"<!-- apodictic:contract_map\n(.*?)\n-->", s, re.DOTALL)
obj = json.loads(m.group(1))
obj["clauses"] = [c for c in obj["clauses"] if c["clause_id"] != "C2"]
for i, c in enumerate(obj["clauses"]):
    c["clause_id"] = "C%d" % (i + 1)
s = s[:m.start(1)] + json.dumps(obj, indent=2) + s[m.end(1):]
open(p, "w").write(s)
PY
      python3 "$CA_RCO_HELPER" build "$CA_RCO_H6" >/dev/null 2>&1 || CA_RCO_OK=0
      if "$0" reader-contract-outline "$CA_RCO_H6" >/dev/null 2>&1; then
        : # default WARN -> exit 0 expected
      else
        echo "reader-contract-outline hostile R6 (dropped promise clause) FAILED by default (should WARN)"; CA_RCO_OK=0
      fi
      if "$0" reader-contract-outline --strict "$CA_RCO_H6" >/dev/null 2>&1; then
        echo "reader-contract-outline hostile R6 did NOT fail under --strict"; CA_RCO_OK=0
      fi
      rm -rf "$CA_RCO_H6"
      rm -rf "$CA_RCO_H"
      if [ "$CA_RCO_OK" -eq 1 ]; then
        echo "reader-contract-outline (fiction + narrative-nf + producer chain + hostile arms): PASS"
      else
        echo "reader-contract-outline (fiction + narrative-nf + producer chain + hostile arms): FAIL"; CA_FAIL=1
      fi
    elif [ ! -d "$CA_BASE/example-reader-contract-outline" ]; then
      echo "ERROR: $CA_BASE/example-reader-contract-outline not found"; CA_FAIL=1
    fi
    echo ""
    echo "== calibration-honesty (canonical decision-audit letter: clean band w/ qualifier PASSES; a band-as-verdict WARNs default / FAILs --strict; allowlist labels + boilerplate + readiness verdict do not fire; override silences) =="
    # The scaffolded letter carries no decision-audit prose (a region-scoped guard would pass vacuously
    # forever — D2), so a DEDICATED letter exercises the arm non-vacuously. It carries a clean
    # narrative-decision finding (band + provenance-only qualifier) AND a violating argument-decision
    # finding (band-as-verdict, no qualifier). Default run WARNs (exit 0, exactly one WARN attributed to
    # the violation); the hostile --strict arm must FAIL. The bundle labels, mandated boilerplate, the
    # fair-summary sentence, and the severity-floor readiness verdict (D5 disjoint) all stay clean.
    if [ -f "$CA_BASE/example-decision-audit-letter.md" ]; then
      CA_CH_OK=1
      # default: WARN-only, exit 0
      "$0" calibration-honesty "$CA_BASE/example-decision-audit-letter.md" >/dev/null 2>&1 || CA_CH_OK=0
      # exactly one WARN, attributed to the violating argument-decision paragraph, clean one not fired
      CA_CH_OUT=$("$0" calibration-honesty "$CA_BASE/example-decision-audit-letter.md" 2>&1)
      if [ "$(printf '%s\n' "$CA_CH_OUT" | grep -c 'WARN: CS')" -ne 1 ]; then
        echo "calibration-honesty: expected exactly one CS WARN on the canonical letter"; CA_CH_OK=0
      fi
      printf '%s\n' "$CA_CH_OUT" | grep -q 'op-ed scores in the AI-elevated band' || { echo "calibration-honesty: the WARN is not attributed to the violating argument-decision paragraph"; CA_CH_OK=0; }
      # hostile --strict arm: must FAIL
      if "$0" calibration-honesty "$CA_BASE/example-decision-audit-letter.md" --strict >/dev/null 2>&1; then
        echo "calibration-honesty hostile --strict (band-as-verdict) did NOT fail"; CA_CH_OK=0
      fi
      if [ "$CA_CH_OK" -eq 1 ]; then
        echo "calibration-honesty (canonical decision-audit letter + hostile --strict arm): PASS"
      else
        echo "calibration-honesty (canonical decision-audit letter + hostile --strict arm): FAIL"; CA_FAIL=1
      fi
    else
      echo "ERROR: $CA_BASE/example-decision-audit-letter.md not found"; CA_FAIL=1
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
        # FLI increment 4 M1a — the finding-trace row in run_spot_check. ROUTE (spec OQ #6): the
        # committed example letter is a deliberately-minimal gate-state fixture (11 missing §-headings),
        # so run_spot_check's letter-shape rows (synthesis-sections / decision-layer-check) block the
        # WHOLE gate regardless of M1a — topping the fixture up to a full canonical letter is the heavy
        # path the docs/revision-round-gate.md:7 precedent declined. So we assert the NEW ROW SPECIFICALLY:
        # `gate run_spot_check` runs `finding-trace` and it reports `ok` (referential integrity holds —
        # F-P5-01 cited + locked, no dangling/phantom), with NO finding-trace ERROR line. The row's full
        # E1/E2/E3/W1 matrix is carried by the run_gate.py --self-test m1a_* cases (run here via
        # --self-test-all). We also confirm `gate --attest run_spot_check` runs finding-trace fresh.
        # || true: the WHOLE gate exits 1 (BLOCKED) on the minimal fixture's letter-shape rows;
        # under `set -euo pipefail` an assignment from a failing command-sub aborts the script, so
        # swallow the exit and assert on the captured finding-trace ROW line instead.
        SPOT_OUT=$("$0" gate run_spot_check "$CA_TMP" 2>&1 || true)
        if printf '%s' "$SPOT_OUT" | grep -qE 'finding-trace +ok' \
           && ! printf '%s' "$SPOT_OUT" | grep -qE 'finding-trace +ERROR'; then
          echo "gate run_spot_check finding-trace row (temp copy): PASS (integrity ok; other letter rows fail on the minimal fixture by design)"
        else
          echo "gate run_spot_check finding-trace row (temp copy): FAIL"; CA_FAIL=1
        fi
        ATTEST_OUT=$("$0" gate --attest run_spot_check "$CA_TMP" 2>&1 || true)
        if printf '%s' "$ATTEST_OUT" | grep -qE 'finding-trace +ok'; then
          echo "gate --attest run_spot_check finding-trace row (temp copy): PASS"
        else
          echo "gate --attest run_spot_check finding-trace row (temp copy): FAIL"; CA_FAIL=1
        fi
        rm -rf "$CA_TMP"
      fi
    else
      echo "ERROR: $CA_BASE/example-run-folder not found"; CA_FAIL=1
    fi
    echo ""
    echo "== canonical clean contract (quality-risk-triggers: no Q1-Q5 fires; hostile Q1 darkness arm) =="
    if [ -f "$CA_BASE/example-quality-risk-contract.md" ]; then
      # clean arm: the canonical well-formed, low-risk Contract raises none of the five pre-pass
      # quality-risk triggers (Q1-Q5) and exits 0 — the release-gate proof that the canonical
      # framework's own worked-example contract satisfies the validator, not just synthetic fixtures.
      "$0" quality-risk-triggers "$CA_BASE/example-quality-risk-contract.md" || CA_FAIL=1
      # hostile arm: the SAME contract with its darkness rating flipped from Moderate to the top
      # setting must raise the Q1 consent/governance trigger and exit non-zero — non-vacuous proof
      # the gate has teeth (a sed no-op, were the fixture to stop carrying the Moderate rating,
      # leaves the copy identical to the clean one and so trips the FAIL branch below). Mutated on a
      # throwaway copy so the committed fixture stays clean.
      CA_QR=$(mktemp)
      sed 's/DARKNESS LEVEL: Moderate/DARKNESS LEVEL: HIGH/' "$CA_BASE/example-quality-risk-contract.md" > "$CA_QR"
      if QR_OUT=$("$0" quality-risk-triggers "$CA_QR" 2>&1); then
        echo "quality-risk-triggers (hostile darkness arm): FAIL (expected Q1 to fire and exit non-zero)"; CA_FAIL=1
      elif printf '%s' "$QR_OUT" | grep -q "Q1 (consent/governance)"; then
        echo "quality-risk-triggers (hostile darkness arm): PASS"
      else
        echo "quality-risk-triggers (hostile darkness arm): FAIL (exited non-zero but Q1 not raised)"; CA_FAIL=1
      fi
      rm -f "$CA_QR"
    else
      echo "ERROR: $CA_BASE/example-quality-risk-contract.md not found"; CA_FAIL=1
    fi
    echo ""
    echo "== canonical cost-floor cap (clean over contract+preflight; hostile CF2 token-strip / CF4 goal=submit / CF1 marker-strip arms) =="
    if [ -f "$CA_BASE/example-cost-floor-contract.md" ] && [ -f "$CA_BASE/example-cost-floor-preflight.md" ]; then
      CA_CF_CONTRACT="$CA_BASE/example-cost-floor-contract.md"
      CA_CF_PREFLIGHT="$CA_BASE/example-cost-floor-preflight.md"
      # clean arm: the canonical cap (sequential marker + token, no Q1-Q5 fired) over both fixtures is
      # record-integrity clean and exits 0. Advisory WARNs (the below-floor tradeoff + Q4-unevaluable
      # without a meta sidecar) are exit-0 by design — the release-gate proof that the framework's own
      # worked-example cap satisfies the validator, not just synthetic fixtures.
      "$0" cost-floor "$CA_CF_CONTRACT" "$CA_CF_PREFLIGHT" || CA_FAIL=1
      # hostile arm 1 (CF2 token-strip): delete the cost_floor_override token line -> the marker is
      # orphaned forward -> must FAIL naming CF2. Mutated on a throwaway copy (committed fixture stays
      # clean); a sed/grep no-op (were the fixture to stop carrying the token) leaves the copy identical
      # to clean, which then exits 0 and trips the FAIL branch — the darkness-arm discipline.
      CA_CF1=$(mktemp)
      grep -v '^cost_floor_override:' "$CA_CF_CONTRACT" > "$CA_CF1"
      if CF_OUT=$("$0" cost-floor "$CA_CF1" "$CA_CF_PREFLIGHT" 2>&1); then
        echo "cost-floor (hostile CF2 token-strip arm): FAIL (expected CF2 to fire and exit non-zero)"; CA_FAIL=1
      elif printf '%s' "$CF_OUT" | grep -q "CF2"; then
        echo "cost-floor (hostile CF2 token-strip arm): PASS"
      else
        echo "cost-floor (hostile CF2 token-strip arm): FAIL (exited non-zero but CF2 not named)"; CA_FAIL=1
      fi
      rm -f "$CA_CF1"
      # hostile arm 2 (CF4 goal=submit): append a submit goal -> Q5 fires (target swarm > the sequential
      # cap) with no paired quality-risk-Q5 override marker -> must FAIL naming Q5.
      CA_CF2=$(mktemp)
      cat "$CA_CF_CONTRACT" > "$CA_CF2"; printf '\nGOAL: submit\n' >> "$CA_CF2"
      if CF_OUT=$("$0" cost-floor "$CA_CF2" "$CA_CF_PREFLIGHT" 2>&1); then
        echo "cost-floor (hostile CF4 goal=submit arm): FAIL (expected Q5 demotion to fire and exit non-zero)"; CA_FAIL=1
      elif printf '%s' "$CF_OUT" | grep -q "Q5"; then
        echo "cost-floor (hostile CF4 goal=submit arm): PASS"
      else
        echo "cost-floor (hostile CF4 goal=submit arm): FAIL (exited non-zero but Q5 not named)"; CA_FAIL=1
      fi
      rm -f "$CA_CF2"
      # hostile arm 3 (CF1 reverse orphan): strip the cost-floor marker line but KEEP the token -> the
      # cap record is half-present -> must WARN (CF1) by default (exit 0) AND FAIL under --strict (exit
      # 1). A grep no-op (marker gone from the fixture) leaves the copy clean with no CF1 line, tripping
      # the FAIL branch below.
      CA_CF3=$(mktemp)
      grep -v 'override: cost-floor-' "$CA_CF_CONTRACT" > "$CA_CF3"
      CF_OUT=$("$0" cost-floor "$CA_CF3" "$CA_CF_PREFLIGHT" 2>&1)
      if printf '%s' "$CF_OUT" | grep -q "CF1" && printf '%s' "$CF_OUT" | grep -q "WARN: CF1"; then
        if "$0" cost-floor "$CA_CF3" "$CA_CF_PREFLIGHT" --strict >/dev/null 2>&1; then
          echo "cost-floor (hostile CF1 marker-strip arm): FAIL (expected --strict to promote the orphan WARN to ERROR)"; CA_FAIL=1
        else
          echo "cost-floor (hostile CF1 marker-strip arm): PASS"
        fi
      else
        echo "cost-floor (hostile CF1 marker-strip arm): FAIL (expected default CF1 orphan-token WARN)"; CA_FAIL=1
      fi
      rm -f "$CA_CF3"
    else
      echo "ERROR: $CA_BASE/example-cost-floor-contract.md or example-cost-floor-preflight.md not found"; CA_FAIL=1
    fi
    echo ""
    echo "== canonical synthesis coverage (green + degraded-and-disclosed run folders; V2/V3 hostile arms; V5 masking arm) =="
    if [ -d "$CA_BASE/example-run-folder-coverage" ] && [ -d "$CA_BASE/example-run-folder-coverage-degraded" ]; then
      CA_SCV_SRC="$CA_BASE/example-run-folder-coverage"
      CA_SCVD_SRC="$CA_BASE/example-run-folder-coverage-degraded"
      CA_SCV_OK=1
      # Both canonical folders are clean under the default AND --strict postures: the green hybrid
      # dispatch-derived run, and the degraded run that DISCLOSES its degrade (the note fires and
      # passes — the boy-who-cried-degraded guard's positive case).
      "$0" synthesis-coverage "$CA_SCV_SRC" >/dev/null 2>&1 || CA_SCV_OK=0
      "$0" synthesis-coverage "$CA_SCV_SRC" --strict >/dev/null 2>&1 || CA_SCV_OK=0
      "$0" synthesis-coverage "$CA_SCVD_SRC" >/dev/null 2>&1 || CA_SCV_OK=0
      "$0" synthesis-coverage "$CA_SCVD_SRC" --strict >/dev/null 2>&1 || CA_SCV_OK=0
      [ "$CA_SCV_OK" -eq 1 ] || echo "  canonical coverage folders: FAIL (expected clean PASS incl. --strict)"
      if command -v python3 >/dev/null 2>&1; then
        CA_SCV=$(mktemp -d)
        # h1 — shrunk denominator: drop the Pass 5 row from the manifest while the artifact stays
        # on disk => V2 FAIL (blocking day one; the manifest cannot shrink the denominator).
        mkdir -p "$CA_SCV/h1"; cp "$CA_SCV_SRC"/* "$CA_SCV/h1/"
        grep -v "Example_Pass5_Character_Audit" "$CA_SCV/h1/Example_Synthesis_Read_Manifest_2026-01-01_opus46.md" > "$CA_SCV/h1/m.tmp" \
          && mv "$CA_SCV/h1/m.tmp" "$CA_SCV/h1/Example_Synthesis_Read_Manifest_2026-01-01_opus46.md"
        if SCV_OUT=$("$0" synthesis-coverage "$CA_SCV/h1" 2>&1); then
          echo "  h1 shrunk-denominator: FAIL (expected V2 exit 1)"; CA_SCV_OK=0
        else
          echo "$SCV_OUT" | grep -q "ERROR V2" && echo "  h1 shrunk-denominator: OK (V2 caught)" \
            || { echo "  h1 shrunk-denominator: FAIL (exit 1 but no V2 finding)"; CA_SCV_OK=0; }
        fi
        # h2 — marker flipped against the sidecar: one declaration, one place => V3 FAIL.
        mkdir -p "$CA_SCV/h2"; cp "$CA_SCV_SRC"/* "$CA_SCV/h2/"
        sed 's/<!-- coverage: ok -->/<!-- coverage: degraded -->/' "$CA_SCV/h2/Example_Core_DE_Synthesis_2026-01-01_opus46.md" > "$CA_SCV/h2/l.tmp" \
          && mv "$CA_SCV/h2/l.tmp" "$CA_SCV/h2/Example_Core_DE_Synthesis_2026-01-01_opus46.md"
        if SCV_OUT=$("$0" synthesis-coverage "$CA_SCV/h2" 2>&1); then
          echo "  h2 marker-vs-sidecar: FAIL (expected V3 exit 1)"; CA_SCV_OK=0
        else
          echo "$SCV_OUT" | grep -q "ERROR V3" && echo "  h2 marker-vs-sidecar: OK (V3 caught)" \
            || { echo "  h2 marker-vs-sidecar: FAIL (exit 1 but no V3 finding)"; CA_SCV_OK=0; }
        fi
        # h3 — masking (spec fixture M1-2 letter B): the degraded run's marker AND sidecar flipped
        # to ok while the manifest still computes degraded => V5 WARN by default (advisory-first
        # launch posture, gate pass-with-warn), FAIL under --strict.
        mkdir -p "$CA_SCV/h3"; cp "$CA_SCVD_SRC"/* "$CA_SCV/h3/"
        sed 's/<!-- coverage: degraded -->/<!-- coverage: ok -->/' "$CA_SCV/h3/Example_Core_DE_Synthesis_2026-01-01_opus46.md" > "$CA_SCV/h3/l.tmp" \
          && mv "$CA_SCV/h3/l.tmp" "$CA_SCV/h3/Example_Core_DE_Synthesis_2026-01-01_opus46.md"
        sed 's/"coverage": "degraded"/"coverage": "ok"/' "$CA_SCV/h3/Diagnostic_State.meta.json" > "$CA_SCV/h3/s.tmp" \
          && mv "$CA_SCV/h3/s.tmp" "$CA_SCV/h3/Diagnostic_State.meta.json"
        if SCV_OUT=$("$0" synthesis-coverage "$CA_SCV/h3" 2>&1); then
          echo "$SCV_OUT" | grep -q "WARN V5" && echo "  h3 masking-default: OK (V5 surfaced as WARN)" \
            || { echo "  h3 masking-default: FAIL (exit 0 but no V5 WARN)"; CA_SCV_OK=0; }
        else
          echo "  h3 masking-default: FAIL (expected advisory exit 0 with V5 WARN)"; CA_SCV_OK=0
        fi
        "$0" synthesis-coverage "$CA_SCV/h3" --strict >/dev/null 2>&1 \
          && { echo "  h3 masking-strict: FAIL (expected exit 1 under --strict)"; CA_SCV_OK=0; } \
          || echo "  h3 masking-strict: OK (caught)"
        rm -rf "$CA_SCV"
      fi
      if [ "$CA_SCV_OK" -eq 1 ]; then
        echo "synthesis-coverage (canonical + hostile arms): PASS"
      else
        echo "synthesis-coverage (canonical + hostile arms): FAIL"; CA_FAIL=1
      fi
    else
      echo "ERROR: $CA_BASE/example-run-folder-coverage(+-degraded) not found (synthesis-coverage)"; CA_FAIL=1
    fi
    echo ""
    echo "== canonical dispatch observability (dispatch-record: R1-R5 on the backfilled coverage run folders; parser-has-teeth; R5 hostile arm) =="
    # Model-Capacity Exploitation M1 (docs/model-capacity-dispatch-log.md): the two canonical
    # coverage run folders carry populated `dispatch_log` arrays (hybrid, dispatch-derived,
    # consistent with their on-disk pass artifacts) so R1-R4 run against REAL data at the release
    # gate. First the parser-has-teeth proof — the R3 model-tag table must parse the known tags from
    # the SHIPPED output-structure.md (a zero-row parse would exit 2, never accept-everything).
    if [ -d "$CA_BASE/example-run-folder-coverage" ] && [ -d "$CA_BASE/example-run-folder-coverage-degraded" ]; then
      CA_DR_SRC="$CA_BASE/example-run-folder-coverage"
      CA_DRD_SRC="$CA_BASE/example-run-folder-coverage-degraded"
      CA_DR_OK=1
      if command -v python3 >/dev/null 2>&1; then
        DR_SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"; export DR_SCRIPT_DIR
        DR_TAGS=$(python3 - "$CA_BASE/output-structure.md" <<'PYEOF'
import sys, os, importlib.util
here = os.environ["DR_SCRIPT_DIR"]
spec = importlib.util.spec_from_file_location("dispatch_record", os.path.join(here, "dispatch_record.py"))
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
tags = m.parse_model_tag_table(open(sys.argv[1], encoding="utf-8").read())
need = {"codex54", "o3", "gemini31", "opus46", "sonnet46", "haiku45"}
print("OK" if need <= tags and tags else "FAIL(%s)" % sorted(tags))
PYEOF
)
        if [ "$DR_TAGS" = "OK" ]; then echo "  parser-has-teeth: OK (6 known tags parsed from shipped output-structure.md)"; \
          else echo "  parser-has-teeth: FAIL ($DR_TAGS)"; CA_DR_OK=0; fi
      fi
      # both backfilled folders PASS clean under default AND --strict
      "$0" dispatch-record "$CA_DR_SRC" >/dev/null 2>&1 || { echo "  coverage folder default: FAIL"; CA_DR_OK=0; }
      "$0" dispatch-record "$CA_DR_SRC" --strict >/dev/null 2>&1 || { echo "  coverage folder --strict: FAIL"; CA_DR_OK=0; }
      "$0" dispatch-record "$CA_DRD_SRC" >/dev/null 2>&1 || { echo "  coverage-degraded folder default: FAIL"; CA_DR_OK=0; }
      "$0" dispatch-record "$CA_DRD_SRC" --strict >/dev/null 2>&1 || { echo "  coverage-degraded folder --strict: FAIL"; CA_DR_OK=0; }
      # R5 hostile arm: stale the final entry's mode against last_session.execution_mode ->
      # WARN by default (advisory-first), FAIL under --strict (the R5 tooth on real-shaped data).
      if command -v python3 >/dev/null 2>&1; then
        CA_DR=$(mktemp -d)
        mkdir -p "$CA_DR/stale"; cp "$CA_DR_SRC"/* "$CA_DR/stale/"
        python3 - "$CA_DR/stale/Diagnostic_State.meta.json" <<'PYEOF'
import sys, json
p = sys.argv[1]
obj = json.load(open(p, encoding="utf-8"))
# force a stale final-entry mode: last_session becomes swarm while entries stay hybrid
obj.setdefault("last_session", {})["execution_mode"] = "swarm"
json.dump(obj, open(p, "w", encoding="utf-8"))
PYEOF
        if DR_OUT=$("$0" dispatch-record "$CA_DR/stale" 2>&1); then
          echo "$DR_OUT" | grep -q "WARN R5" && echo "  R5 stale-mode default: OK (WARN surfaced)" \
            || { echo "  R5 stale-mode default: FAIL (exit 0 but no WARN R5)"; CA_DR_OK=0; }
        else
          echo "  R5 stale-mode default: FAIL (expected advisory exit 0 with WARN R5)"; CA_DR_OK=0
        fi
        "$0" dispatch-record "$CA_DR/stale" --strict >/dev/null 2>&1 \
          && { echo "  R5 stale-mode --strict: FAIL (expected exit 1 under --strict)"; CA_DR_OK=0; } \
          || echo "  R5 stale-mode --strict: OK (caught)"
        rm -rf "$CA_DR"
      fi
      if [ "$CA_DR_OK" -eq 1 ]; then
        echo "dispatch-record (canonical backfill + parser-has-teeth + R5 hostile arm): PASS"
      else
        echo "dispatch-record (canonical backfill + parser-has-teeth + R5 hostile arm): FAIL"; CA_FAIL=1
      fi
    else
      echo "ERROR: $CA_BASE/example-run-folder-coverage(+-degraded) not found (dispatch-record)"; CA_FAIL=1
    fi
    echo ""
    echo "== canonical Pre-Letter Re-Grounding (specificity-floor: count floor + anchor floor; hostile arms) =="
    # docs/synthesis-regrounding.md M2: the re-grounded letter (F-P5-01 restored "nine belief
    # failures" + Ch 12 anchor, F-P1-02 delivered) must PASS clean under the default AND --strict
    # postures — the founding salience-decay example, RESTORED. Then the HOSTILE arms (AGENTS.md
    # review practice), each on a temp copy: (1) decay "nine" -> "several" in the letter -> the
    # count floor must FAIL; (2) strip the Ch 12 anchor from the Must-Fix window -> the anchor floor
    # must FAIL; (3) remove the <!-- regrounding: done --> marker -> WARN by default (advisory),
    # ERROR under --strict. The smuggled-finding reverse-ID check is finding-trace E1's (spec
    # §M2.3, single ownership) — exercised by finding-trace's own e1_dangling_ref self-test, not
    # re-fixtured here.
    if [ -f "$CA_BASE/example-regrounded-letter.md" ] && [ -f "$CA_BASE/example-regrounded-ledger.md" ]; then
      CA_SPF_LET="$CA_BASE/example-regrounded-letter.md"
      CA_SPF_LED="$CA_BASE/example-regrounded-ledger.md"
      CA_SPF_OK=1
      "$0" specificity-floor "$CA_SPF_LET" "$CA_SPF_LED" >/dev/null 2>&1 || CA_SPF_OK=0
      "$0" specificity-floor "$CA_SPF_LET" "$CA_SPF_LED" --strict >/dev/null 2>&1 || CA_SPF_OK=0
      [ "$CA_SPF_OK" -eq 1 ] || echo "  canonical re-grounded pair: FAIL (expected clean PASS incl. --strict)"
      if command -v python3 >/dev/null 2>&1; then
        CA_SPF=$(mktemp -d)
        # h1 — salience decay: the restored count "nine belief failures" smeared back to "several"
        # => count-floor FAIL (blocking; the delivered letter may not decay a locked count).
        sed 's/\*\*nine belief failures\*\*/several belief failures/' "$CA_SPF_LET" > "$CA_SPF/decay.md"
        if SPF_OUT=$("$0" specificity-floor "$CA_SPF/decay.md" "$CA_SPF_LED" 2>&1); then
          echo "  h1 salience-decay: FAIL (expected count-floor exit 1)"; CA_SPF_OK=0
        else
          echo "$SPF_OUT" | grep -q "count floor" && echo "  h1 salience-decay: OK (count floor caught)" \
            || { echo "  h1 salience-decay: FAIL (exit 1 but no count-floor finding)"; CA_SPF_OK=0; }
        fi
        # h2 — anchor drift: the Ch 12 anchor removed from the Must-Fix window (F-P5-01's "Ch 12
        # confession" prose block) => the window carries no chapter matching the locked
        # evidence_ref "Ch 12 (sc. 30-31)" => anchor-floor FAIL. (The Short Version's separate
        # "Ch 12" line is in a different section window, so it does not re-anchor F-P5-01.)
        sed 's/Ch 12 confession (sc. 30-31)/that confession scene/' "$CA_SPF_LET" > "$CA_SPF/drift.md"
        if SPF_OUT=$("$0" specificity-floor "$CA_SPF/drift.md" "$CA_SPF_LED" 2>&1); then
          echo "  h2 anchor-drift: FAIL (expected anchor-floor exit 1)"; CA_SPF_OK=0
        else
          echo "$SPF_OUT" | grep -q "anchor floor" && echo "  h2 anchor-drift: OK (anchor floor caught)" \
            || { echo "  h2 anchor-drift: FAIL (exit 1 but no anchor-floor finding)"; CA_SPF_OK=0; }
        fi
        # h3 — regrounding-trace stripped: WARN by default (advisory-first, gate pass-with-warn),
        # ERROR under --strict.
        grep -v "regrounding: done" "$CA_SPF_LET" > "$CA_SPF/notrace.md"
        if SPF_OUT=$("$0" specificity-floor "$CA_SPF/notrace.md" "$CA_SPF_LED" 2>&1); then
          echo "$SPF_OUT" | grep -q "WARN" && echo "  h3 no-trace-default: OK (regrounding trace surfaced as WARN)" \
            || { echo "  h3 no-trace-default: FAIL (exit 0 but no WARN)"; CA_SPF_OK=0; }
        else
          echo "  h3 no-trace-default: FAIL (expected advisory exit 0 with WARN)"; CA_SPF_OK=0
        fi
        "$0" specificity-floor "$CA_SPF/notrace.md" "$CA_SPF_LED" --strict >/dev/null 2>&1 \
          && { echo "  h3 no-trace-strict: FAIL (expected exit 1 under --strict)"; CA_SPF_OK=0; } \
          || echo "  h3 no-trace-strict: OK (caught)"
        rm -rf "$CA_SPF"
      fi
      if [ "$CA_SPF_OK" -eq 1 ]; then
        echo "specificity-floor (canonical + hostile arms): PASS"
      else
        echo "specificity-floor (canonical + hostile arms): FAIL"; CA_FAIL=1
      fi
    else
      echo "ERROR: $CA_BASE/example-regrounded-letter.md / example-regrounded-ledger.md not found (specificity-floor)"; CA_FAIL=1
    fi
    echo ""
    echo "== canonical Refutation Record (refutation-coverage + refutation-evidence + refutation-write-scope + hostile arms) =="
    # Finding disconfirmation (docs/finding-disconfirmation.md §8/§12): the committed
    # example-run-folder Refutation Record — recompute-consistent with the fixture's ledger
    # (F-P5-01 Must-Fix HIGH) and Manuscript Snapshot — must PASS all three arms; the
    # canonical letter marks the folder core-de, so the snapshot requirement is live both by
    # flag and by run-shape detection. Then the HOSTILE arms (AGENTS.md review practice), each
    # on a temp copy: (1) HIGH-without-survived — strip the survived refutation block (budget
    # kept) so the HIGH Must-Fix has no record; refutation-coverage must FAIL naming F-P5-01;
    # (2) fabricated quote — rewrite the counter-evidence quote to a line absent from the
    # snapshot; refutation-evidence must FAIL (not-found-verbatim, the anti-rubber-stamp
    # tooth); (3) severity write — inject a severity key into the refutation block (schema is
    # open-keyed, so only the write-scope arm can catch it); refutation-write-scope must FAIL;
    # (4) fabricated budget (Codex P1, PR #161 discussion_r3512685648) — an untested HIGH
    # Should-Fix shipped as "cap-bound" by inventing budget numbers (bound:true, eligible/
    # processed lies) plus a disclosure marker; refutation-coverage must FAIL (the recomputed
    # budget does not bind — the exemption recomputes, never trusts) and refutation-evidence
    # must FAIL (processed exceeds the schema-valid block count).
    CA_RFU_SRC="$CA_BASE/example-run-folder"
    if [ -d "$CA_RFU_SRC" ] && [ -f "$CA_RFU_SRC/Example_Refutation_Record_2026-01-01_opus46.md" ] && command -v python3 >/dev/null 2>&1; then
      CA_RFU_OK=1
      "$0" refutation-coverage "$CA_RFU_SRC/Example_Core_DE_Synthesis_2026-01-01_opus46.md" "$CA_RFU_SRC/Example_Findings_Ledger_2026-01-01_opus46.md" "$CA_RFU_SRC/Example_Refutation_Record_2026-01-01_opus46.md" >/dev/null 2>&1 || CA_RFU_OK=0
      "$0" refutation-evidence "$CA_RFU_SRC/Example_Refutation_Record_2026-01-01_opus46.md" "$CA_RFU_SRC/Example_Manuscript_Snapshot_2026-01-01_opus46.md" --require-snapshot >/dev/null 2>&1 || CA_RFU_OK=0
      "$0" refutation-evidence "$CA_RFU_SRC/Example_Refutation_Record_2026-01-01_opus46.md" >/dev/null 2>&1 || CA_RFU_OK=0
      "$0" refutation-write-scope "$CA_RFU_SRC/Example_Findings_Ledger_2026-01-01_opus46.md" "$CA_RFU_SRC/Example_Refutation_Record_2026-01-01_opus46.md" >/dev/null 2>&1 || CA_RFU_OK=0
      [ "$CA_RFU_OK" -eq 1 ] || echo "  canonical record: FAIL (expected clean PASS on all three arms)"
      CA_RFU=$(mktemp -d)
      cp "$CA_RFU_SRC"/Example_Core_DE_Synthesis_2026-01-01_opus46.md "$CA_RFU_SRC"/Example_Findings_Ledger_2026-01-01_opus46.md \
         "$CA_RFU_SRC"/Example_Manuscript_Snapshot_2026-01-01_opus46.md "$CA_RFU_SRC"/Example_Refutation_Record_2026-01-01_opus46.md "$CA_RFU"/ 2>/dev/null
      # Hostile arm 1: strip the refutation block (keep the budget) -> the HIGH Must-Fix has
      # no record; refutation-coverage must FAIL naming F-P5-01.
      python3 - "$CA_RFU/Example_Refutation_Record_2026-01-01_opus46.md" "$CA_RFU/record-h1.md" <<'PY' || CA_RFU_OK=0
import re, sys
text = open(sys.argv[1], encoding="utf-8").read()
stripped = re.sub(r"<!--\s*apodictic:refutation(?![\w]).*?-->\n?", "", text, flags=re.DOTALL)
open(sys.argv[2], "w", encoding="utf-8", newline="").write(stripped)
PY
      if RFU_OUT=$("$0" refutation-coverage "$CA_RFU/Example_Core_DE_Synthesis_2026-01-01_opus46.md" "$CA_RFU/Example_Findings_Ledger_2026-01-01_opus46.md" "$CA_RFU/record-h1.md" 2>&1); then
        echo "  h1 high-without-survived: FAIL (expected exit 1)"; CA_RFU_OK=0
      else
        [[ "$RFU_OUT" == *"Must-Fix finding F-P5-01"* ]] && echo "  h1 high-without-survived: OK (caught)" \
          || { echo "  h1 high-without-survived: FAIL (exit 1 but F-P5-01 not named)"; CA_RFU_OK=0; }
      fi
      # Hostile arm 2: fabricated quote (absent from the snapshot) -> refutation-evidence FAIL.
      sed 's/For a moment she almost chooses the orchard over the debt./This sentence does not occur in the snapshot./' \
        "$CA_RFU/Example_Refutation_Record_2026-01-01_opus46.md" > "$CA_RFU/record-h2.md"
      if RFU_OUT=$("$0" refutation-evidence "$CA_RFU/record-h2.md" "$CA_RFU/Example_Manuscript_Snapshot_2026-01-01_opus46.md" --require-snapshot 2>&1); then
        echo "  h2 fabricated-quote: FAIL (expected exit 1)"; CA_RFU_OK=0
      else
        [[ "$RFU_OUT" == *"not found verbatim"* ]] && echo "  h2 fabricated-quote: OK (caught)" \
          || { echo "  h2 fabricated-quote: FAIL (exit 1 but no verbatim finding)"; CA_RFU_OK=0; }
      fi
      # Hostile arm 3: severity key injected into the refutation block -> write-scope FAIL.
      sed 's/{"schema":"apodictic.refutation.v1",/{"schema":"apodictic.refutation.v1","severity":"Should-Fix",/' \
        "$CA_RFU/Example_Refutation_Record_2026-01-01_opus46.md" > "$CA_RFU/record-h3.md"
      if RFU_OUT=$("$0" refutation-write-scope "$CA_RFU/Example_Findings_Ledger_2026-01-01_opus46.md" "$CA_RFU/record-h3.md" 2>&1); then
        echo "  h3 severity-write: FAIL (expected exit 1)"; CA_RFU_OK=0
      else
        [[ "$RFU_OUT" == *"severity key"* ]] && echo "  h3 severity-write: OK (caught)" \
          || { echo "  h3 severity-write: FAIL (exit 1 but no severity-key finding)"; CA_RFU_OK=0; }
      fi
      # Hostile arm 4: fabricated budget -> an untested HIGH must not ship as "cap-bound".
      # Append a HIGH Should-Fix to the temp ledger (eligible recomputes to 2), swap the
      # budget block to the lie {cap:15,eligible:16,processed:15,bound:true}, and add the
      # not-attempted-budget marker for the new HIGH to the letter body. Coverage must FAIL
      # on the recompute keystone; evidence must FAIL on the processed/block-count pin.
      cp "$CA_RFU/Example_Findings_Ledger_2026-01-01_opus46.md" "$CA_RFU/ledger-h4.md"
      printf '%s\n%s\n%s\n' '<!-- apodictic:finding' '{"schema":"apodictic.finding.v1","id":"F-P8-01","mechanism":"the subplot stalls without payoff","severity":"Should-Fix","confidence":"HIGH","evidence_refs":["Ch. 8"],"fix_class":"targeted revision","risk_if_fixed":"adjacent-scene ripple"}' '-->' >> "$CA_RFU/ledger-h4.md"
      sed 's/"cap":15,"eligible":1,"processed":1,"bound":false/"cap":15,"eligible":16,"processed":15,"bound":true/' \
        "$CA_RFU/Example_Refutation_Record_2026-01-01_opus46.md" > "$CA_RFU/record-h4.md"
      awk 'NR==1{print; print "<!-- refutation: not-attempted-budget F-P8-01 -->"; next} {print}' \
        "$CA_RFU/Example_Core_DE_Synthesis_2026-01-01_opus46.md" > "$CA_RFU/letter-h4.md"
      if RFU_OUT=$("$0" refutation-coverage "$CA_RFU/letter-h4.md" "$CA_RFU/ledger-h4.md" "$CA_RFU/record-h4.md" 2>&1); then
        echo "  h4 fabricated-budget: FAIL (expected exit 1)"; CA_RFU_OK=0
      else
        [[ "$RFU_OUT" == *"does NOT bind"* ]] && echo "  h4 fabricated-budget: OK (caught)" \
          || { echo "  h4 fabricated-budget: FAIL (exit 1 but the recompute keystone not named)"; CA_RFU_OK=0; }
      fi
      if RFU_OUT=$("$0" refutation-evidence "$CA_RFU/record-h4.md" "$CA_RFU/Example_Manuscript_Snapshot_2026-01-01_opus46.md" --require-snapshot 2>&1); then
        echo "  h4 fabricated-budget (evidence): FAIL (expected exit 1)"; CA_RFU_OK=0
      else
        [[ "$RFU_OUT" == *"schema-valid refutation block"* ]] && echo "  h4 fabricated-budget (evidence): OK (caught)" \
          || { echo "  h4 fabricated-budget (evidence): FAIL (exit 1 but the processed/count pin not named)"; CA_RFU_OK=0; }
      fi
      rm -rf "$CA_RFU"
      if [ "$CA_RFU_OK" -eq 1 ]; then
        echo "refutation validators (canonical + hostile arms): PASS"
      else
        echo "refutation validators (canonical + hostile arms): FAIL"; CA_FAIL=1
      fi
    elif [ ! -f "$CA_RFU_SRC/Example_Refutation_Record_2026-01-01_opus46.md" ]; then
      echo "ERROR: $CA_RFU_SRC/Example_Refutation_Record_2026-01-01_opus46.md not found (refutation validators)"; CA_FAIL=1
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
    # Matched pairs nest one level deeper (<pair>/{clean,broken}/groundtruth.md) than the flat
    # fixtures (<slug>/groundtruth.md), so glob BOTH depths (mirrors the fiction loop below) — else
    # nested pair members are silently unvalidated by --check-all. Flat fixtures print by slug;
    # nested members print by <pair>/<member>.
    for gt in "$CA_EVALS"/*/groundtruth.md "$CA_EVALS"/*/*/groundtruth.md; do
      [ -f "$gt" ] || continue
      CA_ADIR="$(basename "$(dirname "$gt")")"
      CA_APARENT="$(basename "$(dirname "$(dirname "$gt")")")"
      if [ "$CA_APARENT" = "argument-benchmark" ]; then CA_ASLUG="$CA_ADIR"; else CA_ASLUG="$CA_APARENT/$CA_ADIR"; fi
      "$0" argument-groundtruth-check "$gt" >/dev/null 2>&1 && echo "  ok $CA_ASLUG" || { echo "  FAIL $CA_ASLUG"; "$0" argument-groundtruth-check "$gt"; CA_FAIL=1; }
    done
    # Orphan-twin completeness (the corpus-level half of the pairing contract; Check 7 rule 5 closes
    # the wrong-twin hole in-file, this closes the missing-twin hole): every matched-pair member
    # requires BOTH its own artifacts (fixture.md + groundtruth.md) AND a complete complement twin
    # (<pair>/clean ⇄ <pair>/broken, each carrying both files). Driven off the member DIRECTORIES
    # (`<pair>/{clean,broken}`), NOT off a groundtruth.md glob: every other corpus loop is keyed on
    # groundtruth.md, so a FIXTURE-ONLY member directory (a fixture.md with no groundtruth.md) would
    # otherwise be invisible to all of them and evade completeness validation entirely (Codex #196
    # P1). A missing artifact or missing/incomplete twin is a loud FAIL. (This completeness pass is
    # the argument-side addition the fiction loop lacks — backport is a separate chore, out of scope.)
    for CA_MDIR in "$CA_EVALS"/*/clean "$CA_EVALS"/*/broken; do
      [ -d "$CA_MDIR" ] || continue
      CA_PAIRDIR="$(dirname "$CA_MDIR")"
      CA_MEMBER="$(basename "$CA_MDIR")"
      if [ "$CA_MEMBER" = "clean" ]; then CA_TWIN="broken"; else CA_TWIN="clean"; fi
      # This member directory must carry BOTH artifacts (a fixture-only OR groundtruth-only member
      # is incomplete and would otherwise slip past the groundtruth-keyed loops above/below).
      [ -f "$CA_MDIR/fixture.md" ] || { echo "  FAIL $(basename "$CA_PAIRDIR")/$CA_MEMBER — incomplete member: missing fixture.md"; CA_FAIL=1; }
      [ -f "$CA_MDIR/groundtruth.md" ] || { echo "  FAIL $(basename "$CA_PAIRDIR")/$CA_MEMBER — incomplete member: missing groundtruth.md"; CA_FAIL=1; }
      # ...and its complement twin must exist with BOTH artifacts.
      if [ ! -f "$CA_PAIRDIR/$CA_TWIN/fixture.md" ] || [ ! -f "$CA_PAIRDIR/$CA_TWIN/groundtruth.md" ]; then
        echo "  FAIL $(basename "$CA_PAIRDIR")/$CA_MEMBER — orphan twin: complement $CA_TWIN/ missing fixture.md or groundtruth.md"; CA_FAIL=1
      fi
    done
    # Repair-diff acceptance gate (Check 7 build-step-8; the run-side seam of the matched-pair
    # guarantee): for each pair, the clean fixture.md must be the broken fixture.md with insertions
    # ONLY (zero deletions) and the insertion-hunk count must map 1:1 to the clean key's enumerated
    # `Base text + repair record` loci. Prose-only until now (Codex #196 P1) — this wires it. Iterate
    # the clean members (one per pair); the orphan pass above already guaranteed both fixtures exist.
    for CA_CLEAN_GT in "$CA_EVALS"/*/clean/groundtruth.md; do
      [ -f "$CA_CLEAN_GT" ] || continue
      CA_PAIRDIR="$(dirname "$(dirname "$CA_CLEAN_GT")")"
      CA_PSLUG="$(basename "$CA_PAIRDIR")"
      CA_BF="$CA_PAIRDIR/broken/fixture.md"
      CA_CF="$CA_PAIRDIR/clean/fixture.md"
      if [ -f "$CA_BF" ] && [ -f "$CA_CF" ]; then
        "$0" argument-groundtruth-check --repair-diff "$CA_BF" "$CA_CF" "$CA_CLEAN_GT" >/dev/null 2>&1 \
          && echo "  ok $CA_PSLUG repair-diff" \
          || { echo "  FAIL $CA_PSLUG repair-diff"; "$0" argument-groundtruth-check --repair-diff "$CA_BF" "$CA_CF" "$CA_CLEAN_GT"; CA_FAIL=1; }
      else
        echo "  FAIL $CA_PSLUG repair-diff — missing broken/clean fixture.md"; CA_FAIL=1
      fi
    done
    # Round-record conformance (Check 6's run-side seam): every booked ENGINE-fault in the
    # calibration round must cite an anchor its Reliability ledger licenses. The doc lives at repo
    # root (docs/, not shipped to host workspaces) — resolve-and-skip when absent, same convention
    # as the corpus above. Vacuously green until the first post-M1 round books a fault.
    CA_ROUND="$CA_EVALS/../../../docs/argument-benchmark-calibration-round.md"
    if [ -f "$CA_ROUND" ]; then
      "$0" argument-groundtruth-check --round-record "$CA_ROUND" --fixtures-dir "$CA_EVALS" >/dev/null 2>&1 \
        && echo "  ok round-record (argument-benchmark-calibration-round.md)" \
        || { echo "  FAIL round-record"; "$0" argument-groundtruth-check --round-record "$CA_ROUND" --fixtures-dir "$CA_EVALS"; CA_FAIL=1; }
    fi
    echo ""
  fi

  # Argument-taxonomy crosswalk (R4A) — evals/ is not shipped to host workspaces, so resolve-and-skip
  # when absent, same convention as the GT corpus above. The validator also reads dialectical-clarity.md
  # (in the plugin tree, which IS shipped) to derive the drift-bound code set.
  CA_XWALK=""
  for cand in "$CA_SCRIPT_DIR/../../../evals/argument-crosswalk/crosswalk.json" "$CA_SCRIPT_DIR/../evals/argument-crosswalk/crosswalk.json"; do
    if [ -f "$cand" ]; then CA_XWALK="$cand"; break; fi
  done
  if [ -n "$CA_XWALK" ]; then
    echo "== argument-crosswalk-check (shipped crosswalk.json) =="
    "$0" argument-crosswalk-check "$CA_XWALK" >/dev/null 2>&1 && echo "  ok crosswalk.json" || { echo "  FAIL crosswalk.json"; "$0" argument-crosswalk-check "$CA_XWALK"; CA_FAIL=1; }
    echo ""
  fi

  CA_AIF=""
  for cand in "$CA_SCRIPT_DIR/../../../evals/fixtures/argument-aif/final-audit" "$CA_SCRIPT_DIR/../evals/fixtures/argument-aif/final-audit"; do
    if [ -d "$cand" ]; then CA_AIF="$cand"; break; fi
  done
  if [ -n "$CA_AIF" ]; then
    echo "== argument-aif-check (canonical final-audit export + source closure) =="
    "$0" argument-aif-check "$CA_AIF/export.json" --source "$CA_AIF/argument-state.md" >/dev/null 2>&1 \
      && echo "  ok final-audit/export.json" \
      || { echo "  FAIL final-audit/export.json"; "$0" argument-aif-check "$CA_AIF/export.json" --source "$CA_AIF/argument-state.md"; CA_FAIL=1; }
    CA_AIF_ROOT=$(dirname "$CA_AIF")
    CA_AIF_TMP=$(mktemp "${TMPDIR:-/tmp}/apodictic-aif.XXXXXX")
    for fx in final-over-predraft predraft-complete predraft-partial; do
      "$0" argument-aif-export "$CA_AIF_ROOT/$fx/argument-state.md" --state-schema 0.2.0 --out "$CA_AIF_TMP" >/dev/null 2>&1 \
        && "$0" argument-aif-check "$CA_AIF_TMP" --source "$CA_AIF_ROOT/$fx/argument-state.md" >/dev/null 2>&1 \
        && echo "  ok $fx" \
        || { echo "  FAIL $fx"; CA_FAIL=1; }
    done
    "$0" argument-spine "$CA_AIF_ROOT/predraft-complete/argument-state.md" --strict >/dev/null 2>&1 \
      && echo "  ok predraft-complete (argument-spine --strict)" \
      || { echo "  FAIL predraft-complete (argument-spine --strict)"; CA_FAIL=1; }
    for fx in mixed-support mixed-warrant carrier-disagreement bad-carrier-missing bad-carrier-enum bad-carrier-extra fallback-c99 extra-final-record; do
      if "$0" argument-aif-export "$CA_AIF_ROOT/$fx/argument-state.md" --state-schema 0.2.0 --out "$CA_AIF_TMP" >/dev/null 2>&1; then
        echo "  FAIL $fx (hostile mixed population unexpectedly exported)"; CA_FAIL=1
      else
        echo "  ok $fx (rejected)"
      fi
    done
    rm -f "$CA_AIF_TMP"
    echo ""
  fi
  CA_AIF_REF=""
  for cand in "$CA_SCRIPT_DIR/../plugins/apodictic/skills/core-editor/references" "$CA_SCRIPT_DIR/../skills/core-editor/references"; do
    if [ -f "$cand/example-argument-aif-export.json" ]; then CA_AIF_REF="$cand"; break; fi
  done
  if [ -n "$CA_AIF_REF" ]; then
    "$0" argument-aif-check "$CA_AIF_REF/example-argument-aif-export.json" --source "$CA_AIF_REF/example-argument-aif-state.md" >/dev/null 2>&1 \
      || { echo "  FAIL example-argument-aif-export.json"; "$0" argument-aif-check "$CA_AIF_REF/example-argument-aif-export.json" --source "$CA_AIF_REF/example-argument-aif-state.md"; CA_FAIL=1; }
  fi

  # AGD Move Audit worked fixtures (R3A) — evals/ is not shipped to host workspaces, so
  # resolve-and-skip, same convention as the corpora above. Each fixture dir carries source.md +
  # argument-state.md; anchors are resolved against the source under --strict.
  CA_AGD=""
  for cand in "$CA_SCRIPT_DIR/../../../evals/fixtures/argument-agd" "$CA_SCRIPT_DIR/../evals/fixtures/argument-agd"; do
    if [ -d "$cand" ]; then CA_AGD="$cand"; break; fi
  done
  if [ -n "$CA_AGD" ]; then
    echo "== argument-agd (worked fixtures, anchors resolved, --strict) =="
    for fx in "$CA_AGD"/*/; do
      [ -f "$fx/argument-state.md" ] || continue
      # R3B AGD seam: when a fixture ships a consumed agd_move_scan.json, pass it so the §10.9
      # Scan: line's n is cross-checked against len(results.observations); absent for pre-R3B fixtures.
      # The claim and the artifact must agree in BOTH directions: a shipped artifact with a denied/
      # missing Scan: line fails inside the validator; a 'Scan: consulted' claim with NO shipped
      # artifact fails here (otherwise the n-cross-check silently skips — the same defeat mirrored).
      CA_SCAN=""
      [ -f "$fx/agd_move_scan.json" ] && CA_SCAN="--scan $fx/agd_move_scan.json"
      if [ -z "$CA_SCAN" ] && grep -q '^Scan: consulted' "$fx/argument-state.md"; then
        echo "  FAIL $(basename "$fx") — 'Scan: consulted' claimed but no agd_move_scan.json shipped (the n-cross-check would silently skip)"; CA_FAIL=1; continue
      fi
      "$0" argument-agd "$fx/argument-state.md" --source "$fx/source.md" $CA_SCAN --strict >/dev/null 2>&1         && echo "  ok $(basename "$fx")"         || { echo "  FAIL $(basename "$fx")"; "$0" argument-agd "$fx/argument-state.md" --source "$fx/source.md" $CA_SCAN --strict; CA_FAIL=1; }
    done
    echo ""
  fi

  # Fiction Benchmark GT corpus (docs/fiction-benchmark-spec.md §Registration): resolve-and-skip when
  # absent (evals/ is not shipped to host workspaces) — same convention as the argument block above.
  # The matched pairs nest one level deeper (<pair>/{clean,broken}/groundtruth.md) than the standalone
  # controls (<control>/groundtruth.md), so glob BOTH depths.
  CA_FEVALS=""
  for cand in "$CA_SCRIPT_DIR/../../../evals/fixtures/fiction-benchmark" "$CA_SCRIPT_DIR/../evals/fixtures/fiction-benchmark"; do
    if [ -d "$cand" ]; then CA_FEVALS="$cand"; break; fi
  done
  if [ -n "$CA_FEVALS" ]; then
    echo "== fiction-groundtruth-check (registered GT corpus) =="
    for gt in "$CA_FEVALS"/*/groundtruth.md "$CA_FEVALS"/*/*/groundtruth.md; do
      [ -f "$gt" ] || continue
      CA_FSLUG="$(basename "$(dirname "$(dirname "$gt")")")/$(basename "$(dirname "$gt")")"
      "$0" fiction-groundtruth-check "$gt" >/dev/null 2>&1 && echo "  ok $CA_FSLUG" || { echo "  FAIL $CA_FSLUG"; "$0" fiction-groundtruth-check "$gt"; CA_FAIL=1; }
    done
    echo ""
  fi

  # Carve-equivalence gate (Workstream A Phase A): prove the nonfiction-argument-engine modularization
  # is behavior-preserving — mechanical resolvers produce golden outputs on the pre-carve fixture.
  echo "== argument-carve-behavior-preservation (carve-equivalence: pre-carve fixture vs goldens) =="
  "$0" argument-carve-behavior-preservation || CA_FAIL=1
  echo ""

  # Schema-coverage invariant (Harness Contracts v2): run the gate against the REAL schemas/ dir
  # (not only its synthetic self-test), so a new/renamed/orphaned schema, an unproven binding, a
  # canonical file --check-all no longer runs, or a closed-key drift between a schema file and the
  # _coverage.json table is caught at release time. C2/C5 only have teeth against disk reality.
  echo "== schema-coverage (real schemas dir) =="
  "$0" schema-coverage || CA_FAIL=1
  echo ""

  # Register/stance calibration contract: exercise a real AT5 state + ledger pair, including
  # the exact prescriptive cash-out join and the recorded blocked-cash-out precedence.
  CA_SC_FIX=""
  for cand in "$CA_SCRIPT_DIR/../../../evals/fixtures/stance-calibration/clean" "$CA_SCRIPT_DIR/../evals/fixtures/stance-calibration/clean"; do
    if [ -d "$cand" ]; then CA_SC_FIX="$cand"; break; fi
  done
  echo "== stance-calibration (canonical AT5 ledger + Argument_State join) =="
  if [ -n "$CA_SC_FIX" ]; then
    "$0" stance-calibration "$CA_SC_FIX/Findings_Ledger.md" --argument-state "$CA_SC_FIX/Argument_State.md" >/dev/null 2>&1 \
      && echo "  ok (register floor + prescriptive cash-out block)" \
      || { echo "  FAIL"; "$0" stance-calibration "$CA_SC_FIX/Findings_Ledger.md" --argument-state "$CA_SC_FIX/Argument_State.md" || true; CA_FAIL=1; }
  else
    echo "  FAIL (fixture directory not found)"; CA_FAIL=1
  fi
  echo ""

  # E7 strict evidence is ground truth for the built register/stance layer, not a one-off
  # review artifact. Exercise both independently produced machine-conformant pairs so later
  # validator or fixture drift cannot leave the declared E7 closure green by accident.
  CA_E7_ROOT=""
  for cand in "$CA_SCRIPT_DIR/../../../evals/register-stance-pilot" "$CA_SCRIPT_DIR/../evals/register-stance-pilot"; do
    if [ -d "$cand" ]; then CA_E7_ROOT="$cand"; break; fi
  done
  echo "== stance-calibration (E7 strict blind pairs) =="
  if [ -n "$CA_E7_ROOT" ]; then
    for pair in e7-strict-a e7-strict-b; do
      "$0" stance-calibration "$CA_E7_ROOT/$pair/Findings_Ledger.md" --argument-state "$CA_E7_ROOT/$pair/Argument_State.md" >/dev/null 2>&1 \
        && echo "  ok $pair" \
        || { echo "  FAIL $pair"; "$0" stance-calibration "$CA_E7_ROOT/$pair/Findings_Ledger.md" --argument-state "$CA_E7_ROOT/$pair/Argument_State.md" || true; CA_FAIL=1; }
    done
  else
    echo "  FAIL (E7 strict fixture root not found)"; CA_FAIL=1
  fi
  echo ""

  # Fleet-convention invariant: the meta-linter gates the whole validator fleet against the recurring
  # bug classes (resolver-substring, count-drift, unwired self-test, orphan schema) found by the
  # 2026-06-20 sweep, so they cannot silently re-enter.
  # Executable synthetic reconstruction histories use the actual selected mirror.
  CA_RECON=""
  for cand in "$CA_SCRIPT_DIR/../../../evals/fixtures/argument-reconstruction" "$CA_SCRIPT_DIR/../evals/fixtures/argument-reconstruction"; do
    if [ -f "$cand/run_cases.py" ]; then CA_RECON="$cand"; break; fi
  done
  if [ -n "$CA_RECON" ]; then
    echo "== argument-reconstruction (synthetic ledger and recovery histories) =="
    python3 "$CA_RECON/run_cases.py" --engine "$CA_SCRIPT_DIR/approval_graph.py" || CA_FAIL=1
    echo ""
  elif [ -d "$CA_SCRIPT_DIR/../evals" ] || [ -d "$CA_SCRIPT_DIR/../../../evals" ]; then
    echo "FAIL: reconstruction behavioral suite missing from repository checkout"
    CA_FAIL=1
  fi

  echo "== validator-conventions (meta-linter: M1 dispatch+self-test, M2 resolver hygiene, M3 derived count, M4 no orphan schema, M5 override hygiene, M6 code-span hygiene, M7 single-Firewall, M8 severity-vocab SSoT) =="
  "$0" validator-conventions >/dev/null 2>&1 && echo "  ok (fleet conventions hold)" || { echo "  FAIL"; "$0" validator-conventions || true; CA_FAIL=1; }
  echo ""
  # Dual-script-mirror invariant: the root scripts/ copy (what CI runs) and the canonical
  # plugins/apodictic/scripts/ copy must be byte-identical for the shared mirrored set, or a
  # validator change passes against one copy while CI runs the stale other (AGENTS.md § parity).
  echo "== check-mirror (scripts/ <-> plugins/apodictic/scripts/ byte-identical) =="
  "$0" check-mirror >/dev/null 2>&1 && echo "  ok (mirrored set identical)" || { echo "  FAIL"; "$0" check-mirror || true; CA_FAIL=1; }
  echo ""

  if [ "$CA_FAIL" -eq 0 ]; then
    if [ "$CA_SKIP_SELF_TESTS" -eq 1 ]; then
      echo "check-all canonical shard: PASS (real-file invariants)"
    else
      echo "check-all: PASS (self-tests + real-file invariants)"
    fi
    exit 0
  else
    if [ "$CA_SKIP_SELF_TESTS" -eq 1 ]; then
      echo "check-all canonical shard: FAIL (one or more real-file checks failed)"
    else
      echo "check-all: FAIL (one or more checks failed; rerun individually for details)"
    fi
    exit 1
  fi
fi
