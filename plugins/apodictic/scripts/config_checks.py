#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validators for APODICTIC's non-letter artifact types (validate.sh contract/config arms).

These three arms do not take an editorial letter or ledger — they validate different
artifact types — so they live here rather than in letter_checks.py:

  * quality-risk-triggers      — pre-pass mode selection from a CONTRACT artifact (+ optional
                                 Diagnostic_State.meta.json sidecar). Five triggers Q1-Q5.
  * audit-tier-criterion       — pass-dependencies.md §4a/§4b high-tier rows must point at an
                                 audit reference file that documents hard gates / Must-Fix
                                 floors (criterion 1). Walks an audits directory tree.
  * argument-recon-prerequisite— an argument-shaped run folder must carry a Field
                                 Reconnaissance report OR the canonical blind-spot disclosure.

Faithful re-implementations of the bash arms (verified by oracle-diff against the pre-port
arm: identical exit codes). validate.sh stays the command surface and degrades to its prior
bash path when python3 is absent. Output keeps the legacy WARN: / ERROR: / FAILED: / OK:
prefixes and exit codes (0 ok, 1 fail, 2 usage).

CLI:
  config_checks.py quality-risk-triggers <contract_file> [<meta_json>]
  config_checks.py audit-tier-criterion <pass_dependencies_file> [<audits_root_dir>]
  config_checks.py argument-recon-prerequisite <run_folder> [<editorial_letter_file>]
  config_checks.py --self-test [<check-name>]
"""

import fnmatch
import os
import re
import sys


def _read(path):
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read()


# --------------------------------------------------------------------------
# quality-risk-triggers — run-core.md §Quality-Risk Mode Selection.
# --------------------------------------------------------------------------

def _raise_escalation(current, target):
    """Promote escalation toward the swarm ceiling: none < hybrid < swarm."""
    if current == "none":
        return target
    if current == "hybrid":
        return "swarm" if target == "swarm" else "hybrid"
    return "swarm"  # ceiling


def quality_risk_triggers(contract_path, meta_path=None):
    contract = _read(contract_path)
    lines, errors, fired, escalation = [], 0, [], "none"
    ov = {q: ("<!-- override: quality-risk-Q%d" % q) in contract for q in range(1, 6)}

    def fire(q, hit, rationale, target):
        nonlocal errors, escalation
        if ov[q]:
            lines.append("WARN: %s — fired: %s (override marker present)." % (_QR_LABEL[q], hit))
        else:
            lines.append("ERROR: %s — fired: %s. %s" % (_QR_LABEL[q], hit, rationale))
            errors += 1
        fired.append("Q%d" % q)
        escalation = _raise_escalation(escalation, target)

    # Q1: consent/governance risk.
    q1 = []
    if re.search(r"^(genre|GENRE/SUBGENRE):.*(Horror|Erotic)", contract, re.IGNORECASE | re.MULTILINE):
        q1.append("genre=Horror/Erotic")
    if re.search(r"(Consent Complexity|Reception Risk)", contract, re.IGNORECASE):
        q1.append("consent/reception audit recommended")
    if re.search(r"(darkness[ -]level|DARKNESS LEVEL)\s*:?\s*HIGH", contract, re.IGNORECASE):
        q1.append("darkness=HIGH")
    if re.search(r"power[ -]dynamics.*central", contract, re.IGNORECASE):
        q1.append("power-dynamics-central")
    if q1:
        fire(1, "; ".join(q1),
             "Recommended escalation: hybrid. Rationale: structural+reception lenses warrant "
             "architectural isolation.", "hybrid")

    # Q2: argument-shaped nonfiction with high stakes.
    q2 = []
    if (re.search(r"constraint:\s*nonfiction|^constraint:nonfiction", contract, re.IGNORECASE | re.MULTILINE)
            or re.search(r"^(GENRE/SUBGENRE|GENRE):.*(nonfiction|policy|testimony|op-ed|white paper|"
                         r"white-paper|academic|open letter|open-letter)", contract,
                         re.IGNORECASE | re.MULTILINE)):
        if re.search(r"(policy brief|testimony|op-ed|white[- ]paper|academic argument|open letter|"
                     r"recommendation memo)", contract, re.IGNORECASE):
            q2.append("nonfiction + argument-shaped form")
    if (re.search(r"Dialectical Clarity", contract, re.IGNORECASE)
            and re.search(r"(submission readiness|GOAL:\s*submit|goal:\s*submit)", contract, re.IGNORECASE)):
        q2.append("Dialectical Clarity + submission readiness")
    if q2:
        fire(2, "; ".join(q2),
             "Recommended escalation: hybrid (swarm if Field Recon required). Rationale: "
             "claim/evidence/audience lenses warrant independent stress-testing.", "hybrid")

    # Q3: many POVs or non-linear structure.
    q3, pov_count = [], 0
    for ln in contract.split("\n"):
        if re.search(r"POV(\s+count)?:\s*[0-9]+", ln, re.IGNORECASE):
            m = re.search(r"[0-9]+", ln)
            pov_count = int(m.group()) if m else 0
            break
    if pov_count >= 3:
        q3.append("POV count=%d" % pov_count)
    if re.search(r"(non-linear|nonlinear|fragmented structure|nested narrative|temporal complexity)",
                 contract, re.IGNORECASE):
        q3.append("non-linear/fragmented structure")
    if q3:
        target = "swarm" if pov_count >= 6 else "hybrid"
        fire(3, "; ".join(q3),
             "Recommended escalation: %s. Rationale: cross-POV coherence and information-flow "
             "tracking degrade under single-context analysis." % target, target)

    # Q4: prior thin synthesis (sidecar meta JSON, grep-faithful).
    q4 = []
    if meta_path and os.path.isfile(meta_path):
        meta = _read(meta_path)
        if re.search(r'"underdiagnosis_flag"\s*:\s*"(fired|true)"', meta, re.IGNORECASE):
            q4.append("prior-run underdiagnosis flag fired")
        elif re.search(r"underdiagnosis_triggers.*\[.*[a-z]", meta, re.IGNORECASE):
            q4.append("prior-run underdiagnosis triggers in meta")
    if re.search(r"(last round.*(thin|soft|underdiagnosed)|prior thin synthesis)", contract, re.IGNORECASE):
        q4.append("user-stated prior-round thinness")
    if q4:
        fire(4, "; ".join(q4),
             "Recommended escalation: swarm. Rationale: prior-run thinness is direct evidence the "
             "previously selected mode underdiagnoses this manuscript class.", "swarm")

    # Q5: submission readiness.
    q5 = []
    if re.search(r"GOAL:\s*submit|goal:\s*submit", contract, re.IGNORECASE):
        q5.append("goal=submit")
    if re.search(r"(Pass\s*11|PASS SET:.*\b11\b|Submission Readiness)", contract, re.IGNORECASE):
        q5.append("Pass 11 in set")
    if re.search(r"final round before submission", contract, re.IGNORECASE):
        q5.append("contract: final round before submission")
    if q5:
        fire(5, "; ".join(q5),
             "Recommended escalation: swarm. Rationale: highest-stakes diagnosis class; cost "
             "differential justified by consequence of missed finding.", "swarm")

    fired_str = "".join(f + " " for f in fired)
    if errors > 0:
        lines.append("")
        lines.append("TRIGGERS: %s; ESCALATION: %s" % (fired_str, escalation))
        lines.append("FAILED: %d quality-risk trigger(s) fired without override marker. Orchestrator "
                     "must apply escalation per run-core.md §Quality-Risk Mode Selection (final mode "
                     "= max(token-fit-floor, %s)) OR record an explicit user override marker "
                     "(<!-- override: quality-risk-Q[1-5] — <rationale> -->)." % (errors, escalation))
        return 1, lines
    if fired:
        lines.append("OK: Triggers fired (%s) — all addressed via override markers; recommended "
                     "escalation was: %s." % (fired_str, escalation))
    else:
        lines.append("OK: No quality-risk triggers fired. Token-fit recommendation applies.")
    return 0, lines


_QR_LABEL = {
    1: "Q1 (consent/governance)",
    2: "Q2 (argument-shaped + high stakes)",
    3: "Q3 (many POVs / non-linear)",
    4: "Q4 (prior thin synthesis)",
    5: "Q5 (submission readiness)",
}


# --------------------------------------------------------------------------
# audit-tier-criterion — pass-dependencies.md §4c criterion 1.
# --------------------------------------------------------------------------

_HIGH_TIER_RE = re.compile(r"(Hard Prerequisite|Pre-DE Prerequisite|Auto-run|Auto-recommend before synthesis)")


def _audit_tier_slug(name):
    s = re.sub(r"[^a-z0-9]", "-", name.lower())
    s = re.sub(r"-+", "-", s)
    return s.strip("-")


def audit_tier_criterion(pd_path, audit_root=None):
    pd_text = _read(pd_path)
    if not audit_root:
        pd_dir = os.path.dirname(pd_path)
        cand = os.path.join(pd_dir, "..", "..", "specialized-audits", "references")
        audit_root = cand if os.path.isdir(cand) else (pd_dir or ".")

    lines, errors, warns = [], 0, 0
    high_rows = [ln for ln in pd_text.split("\n") if ln.startswith("|") and _HIGH_TIER_RE.search(ln)]
    if not high_rows:
        return 0, ["OK: No high-tier audit assignments detected in pipe-table rows of %s." % pd_path]

    for row in high_rows:
        # awk -F'|' field semantics: leading "|" makes field 1 empty, so audit name = field 3,
        # reference cell = field 5.
        cells = row.split("|")
        audit_name = cells[2].strip() if len(cells) > 2 else ""
        ref_cell = cells[4].strip() if len(cells) > 4 else ""
        m = re.search(r"`([^`]+\.md)`", ref_cell)
        ref_path = m.group(1) if m else ""
        if not audit_name or not ref_path:
            continue

        slug = _audit_tier_slug(audit_name)
        ov_audit = ("<!-- override: audit-tier-criterion-%s" % slug) in pd_text

        ref_file = None
        direct = os.path.join(audit_root, ref_path)
        if os.path.isfile(direct):
            ref_file = direct
        else:
            base = os.path.basename(ref_path)
            for dp, _dn, fns in os.walk(audit_root):
                if base in fns:
                    ref_file = os.path.join(dp, base)
                    break
        if not ref_file:
            lines.append("WARN: '%s' — reference file '%s' not found under '%s'; cannot verify "
                         "criterion 1." % (audit_name, ref_path, audit_root))
            warns += 1
            continue

        if re.search(r"(hard[ -]?gate|must-?fix[ -]?floor)", _read(ref_file), re.IGNORECASE):
            continue  # criterion-1 satisfied
        if ov_audit:
            lines.append("WARN: '%s' — reference file '%s' does not document hard gates / Must-Fix "
                         "floor (criterion 1 unmet); audit-tier-criterion-%s override marker present."
                         % (audit_name, ref_path, slug))
            warns += 1
        else:
            lines.append("ERROR: '%s' — reference file '%s' does not document hard gates / Must-Fix "
                         "floor (criterion 1 unmet for high-tier assignment). Add hard-gate / "
                         "Must-Fix-floor language to the audit reference, demote the tier, or add "
                         "<!-- override: audit-tier-criterion-%s — <rationale> --> in pass-dependencies "
                         "body." % (audit_name, ref_path, slug))
            errors += 1

    if errors > 0:
        lines.append("")
        lines.append("FAILED: %d audit-tier-criterion failure(s); %d warning(s). Capability ceiling: "
                     "criterion 1 (hard gates / Must-Fix floor) is mechanically verified; criteria 2 "
                     "(undetectable-by-passes) and 3 (disclosure-non-equivalence) require model "
                     "judgment and remain in the §4a/§4b verification subsection prose. Canonical home: "
                     "core-editor/references/pass-dependencies.md §4c Audit Tier Promotion Criteria."
                     % (errors, warns))
        return 1, lines
    lines.append("OK: All high-tier audit assignments satisfy criterion 1 (named hard gates / Must-Fix "
                 "floor in reference file) or carry override markers. %d warning(s) surfaced. "
                 "Capability ceiling: criteria 2 + 3 remain prose-verified." % warns)
    return 0, lines


# --------------------------------------------------------------------------
# argument-recon-prerequisite — pass-dependencies.md §4a Hard Prerequisite.
# --------------------------------------------------------------------------

def _find_files(root, maxdepth, patterns, limit=None):
    """find <root> -maxdepth <maxdepth> -type f -iname <patterns> (sorted, case-insensitive)."""
    out = []
    for dp, _dn, fns in os.walk(root):
        for fn in fns:
            full = os.path.join(dp, fn)
            depth = os.path.relpath(full, root).count(os.sep) + 1
            if depth <= maxdepth and any(fnmatch.fnmatch(fn.lower(), p.lower()) for p in patterns):
                out.append(full)
    out.sort()
    return out[:limit] if limit else out


def _letter_body(text):
    lines = text.split("\n")
    for i, ln in enumerate(lines):
        if re.search(r"^#{1,4}.*Appendix [A-C]", ln, re.IGNORECASE):
            return "\n".join(lines[:i])
    return text


def argument_recon_prerequisite(run_folder, letter_path=None):
    if not letter_path:
        found = _find_files(run_folder, 2, ["*editorial_letter*.md", "*_de*.md"], limit=1)
        letter_path = found[0] if found else None

    arg_artifacts = _find_files(run_folder, 3, [
        "Argument_State*.md", "Red_Team_Memo*.md", "Argument_Evidence*.md",
        "Argument_Red_Team*.md", "Argument_Persuasion*.md", "Adversarial_Evidence*.md"], limit=5)

    letter_text = _read(letter_path) if (letter_path and os.path.isfile(letter_path)) else ""
    arg_letter_mention = bool(letter_text) and re.search(
        r"(Dialectical Clarity|Argument Red Team|Argument Evidence Deep-Dive|argument-engine|"
        r"Argument_State|Claim Ladder)", letter_text, re.IGNORECASE) is not None

    if not arg_artifacts and not arg_letter_mention:
        return 0, ["OK: No argument-engine artifacts detected in '%s'; Field Reconnaissance "
                   "prerequisite does not apply (non-argument-shaped run)." % run_folder]

    field_recon = _find_files(run_folder, 3, ["Field_Reconnaissance_Report*.md"], limit=1)
    if field_recon:
        return 0, ["OK: Argument-engine artifacts detected; Field_Reconnaissance_Report.md present "
                   "at '%s'." % field_recon[0]]

    if letter_text and re.search(r"literature[- ]counterevidence[- ]not[- ]surveyed", letter_text, re.IGNORECASE):
        return 0, ["OK: Argument-engine artifacts detected; canonical blind-spot disclosure "
                   "('literature-counterevidence not surveyed') present in editorial letter."]

    if letter_text and "<!-- override: argument-recon-prerequisite" in _letter_body(letter_text):
        return 0, ["WARN: Argument-engine artifacts detected; no Field_Reconnaissance_Report.md and "
                   "no canonical blind-spot disclosure found, but override marker present in editorial "
                   "letter body. Phase 6 Wave 3 / CR-4 Hard Prerequisite policy: this run carries "
                   "documented exception rationale."]

    return 1, ["ERROR: Argument-engine artifacts detected in '%s' (no Field_Reconnaissance_Report.md "
               "present), but the editorial letter does not record the canonical blind-spot disclosure "
               "('literature-counterevidence not surveyed'). Per pass-dependencies.md §4a (Hard "
               "Prerequisite) + run-synthesis.md §Step 3 (Phase 6 Wave 3 / CR-4): silent omission is "
               "forbidden. Either (a) run Field Reconnaissance and produce "
               "Field_Reconnaissance_Report.md, (b) record the canonical blind-spot disclosure in the "
               "editorial letter naming what is unsurveyed and what the absence implies for synthesis "
               "confidence, or (c) place a body override marker "
               "<!-- override: argument-recon-prerequisite — <rationale> --> in the editorial letter."
               % run_folder]


# --------------------------------------------------------------------------
# CLI + self-test.
# --------------------------------------------------------------------------

def _emit(rc, lines):
    for ln in lines:
        print(ln)
    return rc


def run_self_test(which=None):
    import tempfile
    rc = {"v": 0}

    def expect(name, got, want):
        if got == want:
            print("  %s: OK" % name)
        else:
            print("  %s: FAIL (rc=%s, expected %s)" % (name, got, want))
            rc["v"] = 1

    if which in (None, "quality-risk-triggers"):
        with tempfile.TemporaryDirectory() as td:
            def w(n, s):
                p = os.path.join(td, n)
                with open(p, "w", encoding="utf-8") as fh:
                    fh.write(s)
                return p
            pos = w("pos.md", "# Contract\nGENRE/SUBGENRE: Literary fiction\nDARKNESS LEVEL: low\n"
                              "POV count: 1\nGOAL: repair\nRECOMMENDED AUDITS: Scene Turn, Emotional Craft\n")
            q1 = w("q1.md", "# Contract\nGENRE/SUBGENRE: Horror\nDARKNESS LEVEL: HIGH\nPOV count: 2\n"
                            "GOAL: repair\nRECOMMENDED AUDITS: Consent Complexity, Reception Risk, Stakes System\n")
            q2 = w("q2.md", "# Contract\nGENRE/SUBGENRE: Nonfiction — policy brief\nconstraint: nonfiction\n"
                            "FORM: policy brief\nGOAL: submit\nRECOMMENDED AUDITS: Dialectical Clarity, Argument Red-Team\n")
            q3 = w("q3.md", "# Contract\nGENRE/SUBGENRE: Literary fiction\nPOV count: 4\nGOAL: repair\n"
                            "RECOMMENDED AUDITS: Scene Turn\n")
            q5 = w("q5.md", "# Contract\nGENRE/SUBGENRE: Literary fiction\nPOV count: 1\nGOAL: submit\n"
                            "PASS SET: 0, 1, 2, 5, 8, 11\nRECOMMENDED AUDITS: Scene Turn, Emotional Craft\n")
            q4c = w("q4c.md", "# Contract\nGENRE/SUBGENRE: Literary fiction\nPOV count: 1\nGOAL: repair\n"
                              "RECOMMENDED AUDITS: Scene Turn\n")
            q4m = w("q4.json", '{\n  "contract_hash": "abc123",\n  "underdiagnosis_flag": "fired",\n'
                               '  "prior_runs": [{"label": "round-1", "underdiagnosis_triggers": ["convergence"]}]\n}\n')
            ovq1 = w("ovq1.md", "# Contract\nGENRE/SUBGENRE: Horror\nDARKNESS LEVEL: HIGH\nPOV count: 2\n"
                                "GOAL: repair\nRECOMMENDED AUDITS: Consent Complexity, Reception Risk\n"
                                "<!-- override: quality-risk-Q1 — Author requests baseline mode; exploratory mid-draft. -->\n")
            expect("qr_pos", quality_risk_triggers(pos)[0], 0)
            expect("qr_neg_q1", quality_risk_triggers(q1)[0], 1)
            expect("qr_neg_q2", quality_risk_triggers(q2)[0], 1)
            expect("qr_neg_q3", quality_risk_triggers(q3)[0], 1)
            expect("qr_neg_q4", quality_risk_triggers(q4c, q4m)[0], 1)
            expect("qr_neg_q5", quality_risk_triggers(q5)[0], 1)
            expect("qr_over_q1", quality_risk_triggers(ovq1)[0], 0)

    if which in (None, "audit-tier-criterion"):
        with tempfile.TemporaryDirectory() as td:
            audits = os.path.join(td, "audits")
            os.makedirs(audits)

            def wa(n, s):
                with open(os.path.join(audits, n), "w", encoding="utf-8") as fh:
                    fh.write(s)

            def wp(n, s):
                p = os.path.join(td, n)
                with open(p, "w", encoding="utf-8") as fh:
                    fh.write(s)
                return p
            wa("erotic-content.md", "# Erotic Content Audit\n## Hard Gates\n- EC-1 hard gate.\n## Must-Fix floor\nAny gate firing.\n")
            wa("reception-risk.md", "# Reception Risk Audit\n## §7 Severity Hard Gates\nFive hard gates.\nMust-Fix floor when any hard gate fires.\n")
            wa("soft-audit.md", "# Soft Audit\n## Output\nProduces only Note-class observations. Severity outputs: Recommend / Note / Suggestion.\n")
            wa("definitional-memoir.md", "# Definitional Memoir Audit\n## Diagnostic Flags\n### Must-Fix Floor — Hard Gates\nTwo audit-internal hard gates.\n**\"Memory Fraud\"** (Hard Gate) — invented scenes.\n")
            pos = wp("pos_pd.md", "## §4a. Router-triggered audits\n| Trigger | Audit | Tier | Reference |\n|---|---|---|---|\n"
                                  "| Erotic content flagged | Erotic Content | Auto-run (bundled with workflow) | `audits/erotic-content.md` |\n"
                                  "| Representation sensitivity | Reception Risk | Auto-recommend before synthesis | `audits/reception-risk.md` |\n")
            neg = wp("neg_pd.md", "## §4a. Router-triggered audits\n| Trigger | Audit | Tier | Reference |\n|---|---|---|---|\n"
                                  "| Some trigger | Soft Audit | Auto-recommend before synthesis | `audits/soft-audit.md` |\n")
            over = wp("over_pd.md", "## §4a. Router-triggered audits\n| Trigger | Audit | Tier | Reference |\n|---|---|---|---|\n"
                                    "| Some trigger | Soft Audit | Auto-recommend before synthesis | `audits/soft-audit.md` |\n\n"
                                    "<!-- override: audit-tier-criterion-soft-audit — Promoted on cross-fixture findings; criterion 1 waived. -->\n")
            edge = wp("edge_pd.md", "## §4b. Finding-triggered audits\n| Layer | Trigger | Audit | Tier |\n|---|---|---|---|\n"
                                    "| 9 (Thematic Coherence) | Some pattern | Some Recommend Audit | Recommend |\n")
            autorun = wp("autorun_pd.md", "## §4a. Router-triggered audits\n| Trigger | Audit | Tier | Reference |\n|---|---|---|---|\n"
                                          "| Memoir-shape disclosed | Definitional Memoir Audit | Auto-run (bundled) | `audits/definitional-memoir.md` |\n")
            findingtrig = wp("findingtrig_pd.md", "## §4b. Finding-triggered audits\n| Pass | Finding pattern | Audit(s) | Policy |\n"
                                                  "|------|----------------|----------|--------|\n"
                                                  "| 1 (Reader Experience) | Uniform fluency | AI-Prose Calibration | Auto-recommend before synthesis (if not already loaded) |\n")
            expect("atc_pos", audit_tier_criterion(pos, audits)[0], 0)
            expect("atc_neg", audit_tier_criterion(neg, audits)[0], 1)
            expect("atc_over", audit_tier_criterion(over, audits)[0], 0)
            expect("atc_edge", audit_tier_criterion(edge, audits)[0], 0)
            expect("atc_autorun", audit_tier_criterion(autorun, audits)[0], 0)
            expect("atc_findingtrig", audit_tier_criterion(findingtrig, audits)[0], 0)

    if which in (None, "argument-recon-prerequisite"):
        with tempfile.TemporaryDirectory() as td:
            def mkrun(name, files, letter=None):
                d = os.path.join(td, name)
                os.makedirs(d)
                for f in files:
                    open(os.path.join(d, f), "w").close()
                if letter is not None:
                    with open(os.path.join(d, "Editorial_Letter.md"), "w", encoding="utf-8") as fh:
                        fh.write(letter)
                return d
            pos1 = mkrun("run_pos1", ["Argument_State.md", "Field_Reconnaissance_Report.md"],
                         "# Editorial Letter\n## §1 What Needs Work\nMust-Fix: warrant gap on §3 claim.\n")
            pos2 = mkrun("run_pos2", ["Red_Team_Memo.md"],
                         "# Editorial Letter\n## §3 Blind Spot\nField Reconnaissance was declined. The synthesis layer "
                         "records \"literature-counterevidence not surveyed\" as a confidence-limiting blind spot.\n")
            pos3 = mkrun("run_pos3", [], "# Editorial Letter\n## §1 What Needs Work\nMust-Fix: pacing collapse in Chapter 7.\n")
            neg = mkrun("run_neg", ["Argument_State.md", "Red_Team_Memo.md"],
                        "# Editorial Letter\n## §1 What Needs Work\nMust-Fix: warrant gap.\n## §3 Absence Inventory\n"
                        "The pass artifacts are complete; no missing structural elements identified.\n")
            over = mkrun("run_over", ["Argument_State.md"],
                         "# Editorial Letter\n## §1 What Needs Work\nMust-Fix: warrant gap.\n"
                         "<!-- override: argument-recon-prerequisite — Artifacts pre-date the policy; back-fill scheduled. -->\n")
            expect("arp_pos1", argument_recon_prerequisite(pos1)[0], 0)
            expect("arp_pos2", argument_recon_prerequisite(pos2)[0], 0)
            expect("arp_pos3", argument_recon_prerequisite(pos3)[0], 0)
            expect("arp_neg", argument_recon_prerequisite(neg)[0], 1)
            expect("arp_over", argument_recon_prerequisite(over)[0], 0)

    print("Self-test: PASS" if rc["v"] == 0 else "Self-test: FAIL")
    return rc["v"]


_CHECKS = {
    "quality-risk-triggers": (quality_risk_triggers, True),       # (fn, file-must-exist)
    "audit-tier-criterion": (audit_tier_criterion, True),
    "argument-recon-prerequisite": (argument_recon_prerequisite, False),  # arg is a directory
}


def main(argv):
    if len(argv) < 2:
        sys.stderr.write("Usage: config_checks.py <quality-risk-triggers|audit-tier-criterion|"
                         "argument-recon-prerequisite|--self-test> ...\n")
        return 2
    if argv[1] == "--self-test":
        return run_self_test(argv[2] if len(argv) > 2 else None)
    if argv[1] in _CHECKS:
        if len(argv) < 3:
            sys.stderr.write("Usage: config_checks.py %s <path> [<extra>]\n" % argv[1])
            return 2
        fn, is_file = _CHECKS[argv[1]]
        primary = argv[2]
        if is_file and not os.path.isfile(primary):
            sys.stderr.write("Error: File not found: %s\n" % primary)
            return 2
        if not is_file and not os.path.isdir(primary):
            sys.stderr.write("Error: Run folder not found: %s\n" % primary)
            return 2
        extra = argv[3] if len(argv) > 3 else None
        return _emit(*fn(primary, extra))
    sys.stderr.write("Error: unknown command: %s\n" % argv[1])
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
