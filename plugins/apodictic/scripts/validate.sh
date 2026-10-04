#!/usr/bin/env bash
#
# validate.sh — Mechanical validation for APODICTIC core invariants.
#
# Usage: ./scripts/validate.sh <command> [args...]
#
# Commands:
#   argument-reconstruction <PROJECT> --stage graph|draft-ready|acceptance
#       Verify/recover the approval ledger and rebuild graph/session projections.
#       Acceptance remains fail-closed until the semantic comparator is built.
#       Pass --self-test for standalone deterministic smoke checks.
#
#   argument-reconstruction-draft <PROJECT> --packet|--emit [args...]
#       Export the approved packet or validate and publish a paired draft/receipt.
#       Semantic comparison remains unavailable; pass --self-test for synthetic checks.
#
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
#   cost-floor <contract_file> [<preflight_packet>] [<meta_json>] [--strict]
#       Record-integrity gate for a user-declared budget cap that caps the run
#       BELOW the token-fit floor (run-core.md §Cost-floor override). Checks
#       CF1 marker integrity (bidirectional orphan-token check), CF2 marker<->
#       token sync, CF3 single-agent context-tier + mandatory-packet load bound
#       (+ a below-floor WARN for a sequential/hybrid cap under the packet's
#       token-fit floor), CF4 no silent quality-risk demotion (every fired
#       Q-trigger above the cap needs its own override marker). Marker family:
#       <!-- override: cost-floor-{single-agent,sequential,hybrid} — <why> -->;
#       token: cost_floor_override: <mode>[; context_tier: standard|large] —
#       <why>. Reports + gates record integrity; does NOT select the mode.
#       Pass --self-test for built-in cases.
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

# Keep validator output deterministic on Windows consoles and Unix hosts.
export PYTHONUTF8=1
export PYTHONIOENCODING=utf-8

# Single source of truth for the self-testable validator set. Every displayed count below is
# DERIVED from this list (AGG_COUNT) — never hard-code the number (a PR adding a validator edits
# only this line, so the count strings can't go stale or collide on merge).
AGG_VALIDATORS="contract-hash contract-check ledger-check artifact-names synthesis-sections tone-check state-lines severity-floor audit-signal-propagation underdiagnosis-triggers ledger-consolidation decision-layer-check author-facing-lint quality-risk-triggers cost-floor timeline-diff timeline-arithmetic timeline-anchor-conflict audit-tier-criterion pass-header argument-recon-prerequisite structured-findings softness-check deficit-lock artifacts-schema gate gate-state finding-trace escalation-check feedback-triage editor-scaffolding diagnostic-vocabulary retcon-plan state-card-diff revision-arc regression-diff legal-risk promise-contract continuity-bible setup-payoff world-bible intake-interview author-fingerprint content-advisory coaching-history style-explanation persona-divergence argument-spine scene-ethics argument-groundtruth-check fiction-groundtruth-check agreement-alpha argument-crosswalk-check argument-agd argument-aif-check argument-reconstruction argument-reconstruction-draft registry-check schema-coverage lifecycle-node reader-instrument manuscript-viz annotated-manuscript crosslink reanchor roundtrip-disposition disposition-check synthesis-coverage dispatch-record specificity-floor refutation-coverage refutation-evidence refutation-write-scope obsidian-export html-export docx-export pdf-export results-guide position-pair-register reader-contract-outline calibration-honesty stance-calibration validator-conventions argument-carve-behavior-preservation"
# shellcheck disable=SC2086  # intentional word-splitting to count list entries
AGG_COUNT=$(set -- $AGG_VALIDATORS; echo $#)

# --------------------------------------------------------------------------
# Shared hardened override-marker detection (2026-06-20 override-substring class).
#
# The bash gates honor an author/orchestrator escape hatch `<!-- override: <slug> — <rationale> -->`.
# The legacy `grep -F "<!-- override: <slug>"` bare-prefix test had two proven bypasses (the same the
# Python `override_marker.has_override` helper closes, so both arms accept the SAME marker set):
#   1. SUFFIX COLLISION — a bare-prefix match honors a longer slug (`<slug>-but-not-really`).
#   2. CODE-SPAN DECOY  — a marker quoted as documentation inside a backtick span — inline `` `…` `` OR
#                         a fenced ```...``` block — is honored as if live. (Group 4: the old per-line
#                         `sed` stripped inline only, so a marker inside a FENCED block was honored by
#                         bash though the Python path rejected it — bash was wrongly MORE permissive.)
# `_has_override <slug>` reads the body on stdin, strips fenced code blocks (awk fence toggle) AND
# inline code spans (sed), then requires the EXACT slug followed by a boundary delimiter — whitespace,
# an em-/en-dash, the comment close `-->`, or EOL — mirroring the Python helper. Whitespace after
# `<!--` and `override:` is flexible to match Python's `\s*`. Returns 0 (found) / 1 (not found).
# meta_lint.py's M5 gate flags the legacy bare-substring AND compiled/inline-regex forms (and M6 flags a
# local code-span stripper), so the override-bypass class cannot re-enter.
_has_override() {
  _ho_slug="$1"
  # AUTHORITATIVE path: delegate to override_marker.py — the SINGLE robust code-span stripper (handles
  # multiline inline spans, fence char/length, etc.). The fleet's validators already require python3, so
  # this is the live path. (Avoids a second hand-rolled CommonMark parser in awk/sed — that divergence
  # was the source of repeated Codex rounds.)
  _ho_om="$(cd "$(dirname "$0")" && pwd)/override_marker.py"
  if command -v python3 >/dev/null 2>&1 && [ -f "$_ho_om" ]; then
    python3 "$_ho_om" --has-override "$_ho_slug"
    return $?
  fi
  # DEGRADED best-effort fallback (python3 unavailable only): line-wise fence strip that tracks the fence
  # CHARACTER — a ``` line inside a ~~~ fence (or vice-versa) is content, not a premature close (Codex
  # P1) — plus inline-span blanking + boundary-match. Multiline inline spans are NOT handled here; the
  # python3 path above is authoritative. LC_ALL=C is NOT set: the em-/en-dash class needs UTF-8.
  awk '
    function lead(s){ sub(/^[[:space:]]*/,"",s); return s }
    { t=lead($0)
      if (infence) { if ((fc=="`" && t ~ /^```+/) || (fc=="~" && t ~ /^~~~+/)) infence=0; next }
      if (t ~ /^```+/) { infence=1; fc="`"; next }
      if (t ~ /^~~~+/) { infence=1; fc="~"; next }
      print }
  ' \
    | sed 's/```[^`]*```//g; s/``[^`]*``//g; s/`[^`]*`//g' \
    | grep -E "<!--[[:space:]]*override:[[:space:]]*${_ho_slug}([[:space:]]|—|–|-->|$)" >/dev/null 2>&1
}

usage() {
  echo "Usage: $0 <command> [args...]"
  echo "Commands: contract-hash, contract-check, ledger-check, artifact-names, synthesis-sections, tone-check, state-lines, severity-floor, audit-signal-propagation, underdiagnosis-triggers, ledger-consolidation, decision-layer-check, author-facing-lint, quality-risk-triggers, cost-floor, timeline-diff, timeline-arithmetic, timeline-anchor-conflict, audit-tier-criterion, pass-header, argument-recon-prerequisite, structured-findings, softness-check, deficit-lock, artifacts-schema, gate, finding-trace, feedback-triage, editor-scaffolding, diagnostic-vocabulary, retcon-plan, state-card-diff, revision-arc, regression-diff, legal-risk, promise-contract, continuity-bible, setup-payoff, world-bible, intake-interview, author-fingerprint, content-advisory, coaching-history, style-explanation, persona-divergence, argument-spine, scene-ethics, argument-groundtruth-check, fiction-groundtruth-check, agreement-alpha, argument-crosswalk-check, argument-agd, argument-aif-export, argument-aif-check, argument-reconstruction, argument-reconstruction-draft, registry-check, schema-coverage, lifecycle-node, reader-instrument, manuscript-viz, annotated-manuscript, crosslink, reanchor, roundtrip-disposition, disposition-check, synthesis-coverage, dispatch-record, specificity-floor, refutation-coverage, refutation-evidence, refutation-write-scope, obsidian-export, html-export, docx-export, pdf-export, results-guide, position-pair-register, reader-contract-outline, calibration-honesty, stance-calibration, validator-conventions, argument-carve-behavior-preservation"
  echo "Aggregate: --self-test-all (runs --self-test on all $AGG_COUNT self-testable validators; exit 0 only if every validator's self-test passes)"
  echo "Aggregate: --check-canonical (runs only the real-file invariant portion of --check-all)"
  echo "Aggregate: --check-all (runs --self-test-all PLUS real-file invariants: audit-signal-propagation --check-registry, structured-findings on the shipped templates, audit-tier-criterion vs the real pass-dependencies.md, pass-header vs the canonical example-pass-artifact-header.md checked against the real pass-dependencies.md §3, the ported letter/timeline validators vs the canonical worked examples (incl. underdiagnosis-triggers + ledger-consolidation), finding-trace + softness-check + deficit-lock vs the canonical example ledger<->letter pair (both directions), feedback-triage vs the canonical example Feedback Triage paired with its Findings Ledger under --strict (contract + conflict integrity + the Increment-2 maps_to cross-check: FB-01.maps_to=F-RR-01 resolves E5-clean, no fully-validated item left unmapped W4-clean), editor-scaffolding + decision-layer-check + severity-floor vs the canonical scaffolded editorial letter (plus the editor↔author dual-output pair — editor-scaffolding --dual over the scaffolded letter + its author-facing companion: D1 editor side E1-E4, D2 author register no-leak + Revision Checklist anchor, D3 top-severity-band consistency; plus the per-pass arm — editor-scaffolding --per-pass over the canonical scaffolded PASS artifact under --strict: P1 Editor Note addressee, P2 What-You-Might-Have-Missed, clean W1 firewall), diagnostic-vocabulary vs the canonical Vocabulary Guide, retcon-plan vs the canonical Retcon Plan, state-card-diff vs the canonical State Card, revision-arc vs the canonical Revision Arc + its Findings Ledger (A1 schema/nested-phase shape, A2 provenance closure, A3 self-consistency — one-phase-per-finding + Must-Fix-root-cause-not-in-polish, A4 non-empty rationale; clean W1 firewall-drift + W2 orphan under --strict), regression-diff vs the paired two-round example run folders (round linkage + the recurrence / quiet-chapter candidates under --strict), legal-risk vs the canonical Legal Risk Register, promise-contract vs the canonical Promise-Contract Fidelity example (two-sided-ref integrity P1, copy typing P2, the disclosing-synopsis-does-not-raise-PCF2 negative P3, and a clean firewall substring scan W1), continuity-bible vs the canonical Continuity Bible example + its Timeline (C1 schema, C2 locus shape, C3 contradiction integrity, a clean C4 chronology-consume + W1 coverage under --strict), setup-payoff vs the canonical Setup–Payoff Ledger example (SP1 schema over both block kinds, SP2 referential integrity — SP-01.payoff_ref=PO-03 resolves, SP3 open rationale — SP-02 carries one, SP4 derived-state agreement, clean X1 firewall; the three valid states pass and the abandoned SP-03 row is surfaced for prose citation), world-bible vs the canonical Worldbuilding Bible example (W1 schema + closed-key, WD unique ids, WB-R1 rule consistency, WB-C1/WB-C2 cost accounting, WB-G1 distance within a unit class, WB-G2 chronology cycle + anchor-drift, and the WF surface-don't-resolve firewall scan — clean under --strict with the staged contradictions overridden), intake-interview vs the canonical Intake Interview example + its Ledger (I1 schema, I2 no-contract-dup, I3 grounded ambiguity via ref + source_note, I4 calibrate-not-suppress under --strict), author-fingerprint vs the canonical Author Voice Profile (F1 schema, F2 provenance, F3 same-register comparison, F4 descriptive-not-prescriptive, clean W1/W2 under --strict), content-advisory vs the canonical Content Advisory (A1 schema, A2 locus shape, A3 no-severity-leak, descriptive W1, opt-in W2 under --strict), style-explanation vs the canonical Author Style Explanation (X1 schema, X2 provenance, X3 no-severity-leak, X4 descriptive-not-prescriptive incl. the comparison-to-emulate firewall, X5 same-register cluster, clean X6/W1 under --strict), persona-divergence vs the canonical Persona Divergence Map + its Ledger (D1 schema incl. nested experiences enum, D2 grounded prediction, D3 target-severity anchoring, D4 anti-fabrication, D5 closed-key persona under --strict), argument-spine vs the canonical pre-draft Argument_State + the three genre-profiled Argument_States (Increment 5: B1-B4 + W4-W5 over grant / academic / pitch, --strict; the genre examples each carry a non-empty reviewer_objections pre-list so W5 stays green), scene-ethics vs the canonical Scene-Ethics Plan, reader-instrument vs the canonical Beta-Reader Instrument + paired uncertainty ledger, manuscript-viz vs the canonical Structure Map manifest + its Timeline/Ledger sources + the pre-draft Argument_State spine (the claim-ladder X1/X5/X6/X7 gates) + the scene-roster producer (the co-presence X2 gate), annotated-manuscript vs the canonical annotated-manuscript fixture (snapshot + manifest + annotated copy + Ledger/Timeline), crosslink vs the canonical letter + crosslinked letter + manifest, the producer chain (build -> A1-A6 -> render -> X1-X4 on a temp copy of the canonical inputs, asserting the fresh build is byte-identical to the committed fixture), reanchor vs the canonical manifest re-anchored onto a revised-draft snapshot (held / moved / vanished / ambiguous / not-re-anchorable; RA1-RA3 + W1/W2 under --strict), roundtrip-disposition vs the canonical Roundtrip Disposition record + companion Revision Report staged with the glue-chain fixtures (RT1 recompute alignment + RT2 confirmation-record + RT3 confirmed-writes-only + RT4 partition coverage, plus hostile arms — a token-stripped copy must FAIL RT2, an extra unconfirmed resolved marker must FAIL RT3, and a copy with one finding's disposition row dropped must WARN RT4 by default and FAIL under --strict), disposition-check vs the canonical example-run-folder-dispositions (a non-governed sidecar + Coaching Log markers + readiness-caveat excerpt: DP0 record shape incl. trigger-iff-deferred, DP1 declined/deferred-Must-Fix caveat coverage, DP2 no-laundering incl. the bidirectional marker/sidecar sync — plus hostile arms: an assessment stripped of its Declined caveat line must FAIL DP1 (the severity-laundering attempt), a deferred record stripped of its trigger must FAIL DP0, a sidecar with one record dropped must WARN DP2.5 by default and FAIL under --strict, and a declined id's finding_states flipped to 'revised' with no corroborating completion artifact must FAIL DP1 + name DP2.6 — supersedence is recomputed from resolved markers, never trusted), synthesis-coverage vs the canonical coverage run folders (green hybrid dispatch-derived + degraded-and-disclosed, both PASS incl. --strict — V1 presence, V2 disk<->manifest row bijection, V3 note/sidecar/marker projection, V4 provenance/mode agreement, V5 D1-D4 degrade recompute; plus hostile arms — a manifest row removed for an on-disk pass artifact must FAIL V2, a letter marker flipped against the sidecar must FAIL V3, and a degraded run masked to ok in marker+sidecar must WARN V5 by default and FAIL under --strict), specificity-floor vs the canonical re-grounded letter<->ledger pair (docs/synthesis-regrounding.md M2: the restored 'nine belief failures' + Ch 12 anchor letter PASSES clean incl. --strict; plus hostile arms — decaying 'nine' to 'several' must FAIL the count floor, stripping the Ch 12 anchor from the Must-Fix window must FAIL the anchor floor, and removing the <!-- regrounding: done --> marker must WARN by default and FAIL under --strict; the smuggled-finding reverse-ID check is finding-trace E1's, not re-fixtured here), refutation-coverage + refutation-evidence + refutation-write-scope vs the canonical example-run-folder Refutation Record (docs/finding-disconfirmation.md §8: V1 no-HIGH-without-survived-refutation incl. the cap-bound disclosure-marker rules, V2 verbatim single-line snapshot-anchored counter-evidence + snapshot_sha256 binding + budget arithmetic, V3 no-severity-channel + exact confidence transcription per the outcome caps; plus hostile arms — a record stripped of its survived block must FAIL refutation-coverage, a fabricated not-in-snapshot quote must FAIL refutation-evidence, an injected severity key must FAIL refutation-write-scope, and a fabricated bound:true budget with eligible/processed numbers that don't recompute from the ledger/record must FAIL refutation-coverage (the cap-bound exemption recomputes, never trusts) + refutation-evidence), obsidian-export vs the canonical manifest projected to native footnotes — copy + Inc-2 letter (O1 round-trip + O2 footnote resolution + O3 comment fidelity + O4 link resolution + O5 letter prose fidelity, asserting both fresh Obsidian outputs are byte-identical to the committed obsidian/ fixtures), html-export vs the canonical manifest projected to a self-contained read-only HTML (H1 round-trip + H2 anchor resolution + H3 comment fidelity, asserting the fresh html/ export is byte-identical to the committed fixture), docx-export vs the canonical manifest projected to a .docx with anchored comments (D1 artifact integrity + D2 text round-trip + D3 comment resolution, asserting the fresh byte-deterministic docx/ export is byte-identical to the committed fixture), pdf-export vs the canonical manifest projected to a self-contained .pdf (hand-written PDF objects, base-14 Helvetica, an inline [finding_id] marker at each locus + a Findings section — P1 artifact integrity + P2 text round-trip + P3 comment resolution, asserting the fresh byte-deterministic pdf/ export is byte-identical to the committed fixture), results-guide vs the canonical example-results-guide run folder (the navigation-index integrity arm — R1 every `### question` heading is a canonical §3 User Question resolved against the real pass-dependencies.md, R2 every backtick .md/.json citation resolves to a run-folder file and no un-substituted `[…]` placeholder survives while `/coach` / `/audit [name]` command tokens are exempt, R3 no Must/Should/Could-Fix severity leak and no apodictic:finding block — the guide indexes, never diagnoses), position-pair-register vs the canonical example-position-pair-register fixture (artifact + envelope + manuscript under --strict — Q1 the two-layer banned-key walk (relation keys whole-envelope, generic verdict keys scoped to results.pairs; claim_license VALUES with relation words do NOT trip it), Q2 the verbatim re-check with the F1 punctuation-fold (a paraphrased quote DROPS the pair with an inspectable log + WARN, --strict FAILs), A3 no severity/finding leak, F5 the framing-prose relation-vocabulary scan excluding `>`-blockquote evidence lines, and the document-order check), and the run-folder validators (gate-state, escalation-check, argument-recon-prerequisite, and the gate engine on a temp copy) vs the canonical example run folder, quality-risk-triggers vs the canonical clean Contract (example-quality-risk-contract.md raises no Q1-Q5 pre-pass trigger, plus a hostile arm — a darkness rating flipped to the top setting must raise the Q1 consent/governance trigger and exit non-zero), cost-floor vs the canonical cost-floor cap (example-cost-floor-contract.md + example-cost-floor-preflight.md: a sequential cap below the token-fit floor is record-integrity clean, plus three hostile arms — a token-stripped copy must FAIL CF2, a submit-goal-appended copy must FAIL CF4 naming Q5, and a marker-stripped-token-kept copy must WARN the CF1 reverse orphan-token check by default and FAIL under --strict), schema-coverage vs the real schemas/ dir (every apodictic.*.schema.json bound + canonically exercised + closed-key table<->file agreement — Harness Contracts v2), calibration-honesty vs a canonical decision-audit editorial letter (whole-letter paragraph scan: CS1-CS4 claim shapes fire WARN / --strict-ERROR when an uncalibrated SETEC band is rendered as a verdict with no uncalibrated/provenance-only qualifier co-present; the mandated boilerplate + vendored bundle labels + the :157 fair-summary sentence PASS; a severity-floor readiness verdict does not fire — D5 disjoint; the override marker silences per-paragraph), plus validator-conventions (the fleet meta-linter — M1 every AGG validator has a --self-test dispatcher case, M2 resolvers classify on parsed blocks not raw apodictic:<type> marker scans, M3 derived count, M4 no orphan schema, M5 no bare/compiled override-marker scan + M6 no local code-span stripper — overrides use the override_marker SSoT, M7 exactly one canonical Firewall definition in the plugin tree, M8 no local re.compile of the Must/Should/Could-Fix severity token — leak-guards import severity_vocab.SEVERITY_TOKEN_RE))"
  exit 2
}

if [ $# -lt 1 ]; then usage; fi

# Aggregate self-test dispatcher (v1.8.4). Runs --self-test on every
# self-testable validator and exits 0 only if every per-validator
# self-test exits 0. Added per Codex P2 finding: the E1 final report
# referred to an aggregate command that did not exist; this closes the
# documentation-vs-implementation mismatch and simplifies CI invocation.
# The seven early utility commands (contract-hash, contract-check, ledger-check,
# artifact-names, synthesis-sections, tone-check, state-lines) now carry
# fixture-driven self-tests too (Validator Architecture Hardening — they
# previously had none), so every command in the suite is exercised here.
# Four of the seven (ledger-check, synthesis-sections, tone-check → letter_checks.py;
# artifact-names → config_checks.py) were ported to real parsers in Increment 8;
# their bash bodies below are retained as the no-python3 degrade path. The three
# genuinely pure utilities (contract-hash, contract-check, state-lines — sha256 /
# line-count, no markdown parsing) stay bash-only.
if [ "$1" = "--self-test-all" ]; then
  AGG_FAIL=0
  AGG_PASS_COUNT=0
  AGG_FAIL_COUNT=0
  echo "Aggregate self-test dispatcher (v1.8.4) — running --self-test on all $AGG_COUNT validators:"
  ST_GATE_SHARED_OK=1
  for v in $AGG_VALIDATORS; do
    # gate and gate-state are two CLI surfaces backed by the same run_gate.py
    # run_self_test() suite. Run it once through gate; preserve gate-state's
    # standalone --self-test surface, but avoid repeating it in the aggregate.
    if [ "$v" = "gate-state" ]; then
      if [ "$ST_GATE_SHARED_OK" -eq 0 ]; then
        echo "  $v: PASS (covered by gate shared suite)"
        AGG_PASS_COUNT=$((AGG_PASS_COUNT + 1))
      else
        echo "  $v: FAIL (gate shared suite failed)"
        AGG_FAIL_COUNT=$((AGG_FAIL_COUNT + 1))
        AGG_FAIL=1
      fi
      continue
    fi
    if "$0" "$v" --self-test >/dev/null 2>&1; then
      echo "  $v: PASS"
      AGG_PASS_COUNT=$((AGG_PASS_COUNT + 1))
      if [ "$v" = "gate" ]; then ST_GATE_SHARED_OK=0; fi
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
CA_SKIP_SELF_TESTS=0
if [ "$1" = "--check-canonical" ]; then
  # Normalize the CI shard onto the literal --check-all block so schema-coverage
  # can continue proving its canonical invocations from source. This shell-local
  # switch is deliberately not exported to nested validation processes.
  CA_SKIP_SELF_TESTS=1
  set -- --check-all
fi
# validate.sh is split across validate.d/ so no single file exceeds the Claude plugin
# directory's 256 KiB per-file limit. The parts are sourced, not executed, so \$0, \$@, shift and
# set -euo pipefail behave exactly as they did in the single-file script.
VALIDATE_D="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/validate.d"
. "$VALIDATE_D/check-all.sh"

COMMAND="$1"
shift

# ----------------------------------------------------------------------
# Early-utility self-tests (Validator Architecture Hardening). The seven
# early commands below (contract-hash, contract-check, ledger-check,
# artifact-names, synthesis-sections, tone-check, state-lines) previously
# carried no self-tests. These functions give each one regression coverage
# and let them join --self-test-all. Each prints per-case OK/FAIL, sets
# PU_FAIL on any failure, and the caller exits PU_FAIL. Invoked as
# `validate.sh <utility> --self-test`. NOTE: the four ported arms
# (ledger-check, synthesis-sections, tone-check, artifact-names) delegate
# their --self-test to the Python parser when python3 is present; these bash
# functions are the no-python3 degrade-path self-tests for them.
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

# Command dispatch: validate.d/commands-a.sh and commands-b.sh each hold one half of the case arms.
# commands-a.sh sets _V_UNMATCHED=1 for a command it does not define; commands-b.sh owns the
# unknown-command default.
_V_UNMATCHED=0
. "$VALIDATE_D/commands-a.sh"
if [ "$_V_UNMATCHED" -eq 0 ]; then exit 0; fi
. "$VALIDATE_D/commands-b.sh"
