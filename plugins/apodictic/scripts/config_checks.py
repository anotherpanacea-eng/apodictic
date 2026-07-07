#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validators for APODICTIC's non-letter artifact types (validate.sh contract/config arms).

These arms do not take an editorial letter or ledger — they validate different
artifact types (contracts, directory trees, run folders, filename conventions) — so
they live here rather than in letter_checks.py:

  * quality-risk-triggers      — pre-pass mode selection from a CONTRACT artifact (+ optional
                                 Diagnostic_State.meta.json sidecar). Five triggers Q1-Q5.
  * cost-floor                 — record-integrity gate for a user-declared budget cap that caps the
                                 run BELOW the token-fit floor (CF1 marker integrity incl. the
                                 bidirectional orphan-token check, CF2 marker<->token sync, CF3
                                 single-agent context-tier + mandatory-packet load bound, CF4 no
                                 silent quality-risk demotion). Shares the Q1-Q5 detection SSoT
                                 (`_fired_triggers`) with quality-risk-triggers. Reports + gates
                                 record integrity; it does NOT select the mode (the orchestrator owns
                                 selection). run-core.md §Cost-floor override (budget cap).
  * audit-tier-criterion       — pass-dependencies.md §4a/§4b high-tier rows must point at an
                                 audit reference file that documents hard gates / Must-Fix
                                 floors (criterion 1). Walks an audits directory tree.
  * argument-recon-prerequisite— an argument-shaped run folder must carry a Field
                                 Reconnaissance report OR the canonical blind-spot disclosure.
  * artifact-names             — pass artifacts in an output DIRECTORY must match the
                                 <Project>_Pass<N>_<Name>_<runlabel>.md filename convention
                                 (Increment 8; project/runlabel matched as literals).
  * pass-header                — a Core DE pass artifact must carry a §3-sourced header
                                 (Macro block · Writer question · Legacy pass id). Values are
                                 read from pass-dependencies.md §3; header-less legacy artifacts
                                 WARN (H1), block/question/pass mismatches vs §3 ERROR (H2/H3).

Faithful re-implementations of the bash arms (verified by oracle-diff against the pre-port
arm: identical exit codes). validate.sh stays the command surface; when python3 is absent the
pass-header arm degrades to the fleet advisory-WARN convention (skip + inline-check guidance,
rc 0), NOT a bash reimplementation. Output keeps the legacy WARN: / ERROR: / FAILED: / OK:
prefixes and exit codes (0 ok, 1 fail, 2 usage).

CLI:
  config_checks.py quality-risk-triggers <contract_file> [<meta_json>]
  config_checks.py cost-floor <contract_or_run_metadata_file> [<preflight_packet.md>] [<meta_json>] [--strict]
  config_checks.py audit-tier-criterion <pass_dependencies_file> [<audits_root_dir>]
  config_checks.py argument-recon-prerequisite <run_folder> [<editorial_letter_file>]
  config_checks.py artifact-names <output_dir> <project> <runlabel>
  config_checks.py pass-header <pass_artifact_file> [<pass_dependencies_file>]
  config_checks.py --self-test [<check-name>]
"""

import fnmatch
import os
import re
import sys

from override_marker import has_override, override_payloads, strip_code_spans


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


def _fired_triggers(contract, meta_path=None):
    """The fired quality-risk triggers as `(q, target, hit, rationale)` tuples in Q1..Q5 order — the
    SHARED detection SSoT that both `quality_risk_triggers` (which aggregates via `_raise_escalation`
    and renders the WARN/ERROR lines) and `cost_floor` (CF4, which reads the per-trigger `(q, target)`
    mapping) call. The leading `(q, target)` of each tuple IS the spec's shared-enumerator contract;
    `hit`/`rationale` ride alongside so `quality_risk_triggers` renders byte-identical output without
    a second detection copy (the extract is behavior-preserving). `contract` is the contract TEXT;
    `meta_path` the optional Diagnostic_State.meta.json path (Q4's sidecar branch)."""
    out = []

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
        out.append((1, "hybrid", "; ".join(q1),
                    "Recommended escalation: hybrid. Rationale: structural+reception lenses warrant "
                    "architectural isolation."))

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
        out.append((2, "hybrid", "; ".join(q2),
                    "Recommended escalation: hybrid (swarm if Field Recon required). Rationale: "
                    "claim/evidence/audience lenses warrant independent stress-testing."))

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
        out.append((3, target, "; ".join(q3),
                    "Recommended escalation: %s. Rationale: cross-POV coherence and information-flow "
                    "tracking degrade under single-context analysis." % target))

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
        out.append((4, "swarm", "; ".join(q4),
                    "Recommended escalation: swarm. Rationale: prior-run thinness is direct evidence the "
                    "previously selected mode underdiagnoses this manuscript class."))

    # Q5: submission readiness.
    q5 = []
    if re.search(r"GOAL:\s*submit|goal:\s*submit", contract, re.IGNORECASE):
        q5.append("goal=submit")
    if re.search(r"(Pass\s*11|PASS SET:.*\b11\b|Submission Readiness)", contract, re.IGNORECASE):
        q5.append("Pass 11 in set")
    if re.search(r"final round before submission", contract, re.IGNORECASE):
        q5.append("contract: final round before submission")
    if q5:
        out.append((5, "swarm", "; ".join(q5),
                    "Recommended escalation: swarm. Rationale: highest-stakes diagnosis class; cost "
                    "differential justified by consequence of missed finding."))

    return out


def quality_risk_triggers(contract_path, meta_path=None):
    contract = _read(contract_path)
    lines, errors, fired, escalation = [], 0, [], "none"
    ov = {q: has_override(contract, "quality-risk-Q%d" % q) for q in range(1, 6)}

    # Enumerate via the shared SSoT, then aggregate/render exactly as the inline `fire()` closure did.
    for q, target, hit, rationale in _fired_triggers(contract, meta_path):
        if ov[q]:
            lines.append("WARN: %s — fired: %s (override marker present)." % (_QR_LABEL[q], hit))
        else:
            lines.append("ERROR: %s — fired: %s. %s" % (_QR_LABEL[q], hit, rationale))
            errors += 1
        fired.append("Q%d" % q)
        escalation = _raise_escalation(escalation, target)

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
# cost-floor — run-core.md §Cost-floor override (budget cap).
#
# A user-declared cap that caps the run BELOW the token-fit floor at the cheapest
# load-viable mode with honest tradeoff disclosure. This validator gates RECORD
# INTEGRITY (marker<->token sync, viability bound, no silent quality-risk demotion);
# it does NOT select the mode — the orchestrator owns selection, exactly as the
# quality-risk-triggers sibling. Four mechanical predicates over parsed artifacts:
#
#   CF1  marker integrity (bidirectional)  — scan the three slugs via override_marker
#        (SSoT, never a local marker regex — meta-lint M5/M6) + the token via
#        _CFO_TOKEN_RE over strip_code_spans output. Zero markers AND zero live tokens
#        -> inert PASS. >1 distinct mode slug -> ERROR (conflicting caps). Empty
#        rationale -> ERROR. A bare/unsuffixed `cost-floor` marker -> ERROR + hint.
#        Reverse orphan-token check (DP2.5 precedent): a live token with NO matching
#        live marker -> WARN default / ERROR under --strict.
#   CF2  marker<->record sync (forward)     — when a live marker exists, the
#        `cost_floor_override: <mode> … — <rationale>` token must be present (code-span
#        stripped) and its mode must equal the marker's mode. Missing/mismatched -> ERROR.
#   CF3  viability bound (single-agent)     — a single-agent cap must declare
#        `context_tier: large` (standard OR absent -> ERROR) AND its MANDATORY preflight
#        packet's `Estimated single-agent load:` must be < 600000 (packet-absent -> ERROR,
#        load >= bound -> ERROR). Sequential/hybrid carry no context/load requirement, but a
#        sequential/hybrid cap below the packet's own token-fit floor -> below-floor WARN.
#   CF4  no silent quality-risk demotion    — recompute fired Q1-Q5 via _fired_triggers
#        (from artifacts, never a recorded field — the 7085daa rule). Every fired trigger
#        whose per-trigger target exceeds the cap under the total mode order
#        single-agent < sequential < hybrid < swarm requires the matching
#        `<!-- override: quality-risk-Q[n] — … -->` marker; missing -> ERROR naming the
#        trigger. When the optional meta sidecar is withheld and the cap is below swarm,
#        Q4's meta branch is unevaluable -> WARN (CF4-unevaluable).
#
# `context_tier` is DECLARED, not platform-verified (like dispatch_log provenance): the
# validator gates the declaration's presence + consistency, not the true host window.
# --------------------------------------------------------------------------

_MODE_ORDER = {"single-agent": 0, "sequential": 1, "hybrid": 2, "swarm": 3}
_CF_MODES = ("single-agent", "sequential", "hybrid")  # no cost-floor-swarm slug (swarm is the ceiling)
_CF_SINGLE_AGENT_LOAD_CEILING = 600000  # the published run-core/preflight bound

# A field-read token modeled on dispatch_record._QRO_TOKEN_RE: it reads the metadata TOKEN
# (`cost_floor_override: …`), NOT an override marker (`<!-- override: … -->`), so it is
# meta-lint M5-inert. Captures the mode, the OPTIONAL context_tier sub-field (a
# sequential/hybrid token with no context_tier still parses — the field is inert there), and
# the rationale.
_CFO_TOKEN_RE = re.compile(
    r"cost_floor_override:\s*(single-agent|sequential|hybrid)"
    r"(?:\s*;\s*context_tier:\s*(standard|large))?"
    r"\s*[—–-]\s*(.+)", re.IGNORECASE)
# preflight-packet field reads (the single-agent load bound + the standard-context floor line
# the packet already prints). Plain field reads, not marker scans.
_CF_LOAD_RE = re.compile(r"Estimated single-agent load:\D*([0-9][0-9,]*)", re.IGNORECASE)
_CF_FLOOR_RE = re.compile(r"Standard-context mode[^:\n]*:\s*\**\s*(single-agent|sequential|hybrid|swarm)",
                          re.IGNORECASE)


def _cfo_tokens(contract):
    """[(mode, context_tier_or_None)] for each LIVE cost_floor_override token — code spans stripped
    via the override_marker SSoT, so a token quoted as a documentation example is not honored."""
    out = []
    for m in _CFO_TOKEN_RE.finditer(strip_code_spans(contract)):
        out.append((m.group(1).lower(), m.group(2).lower() if m.group(2) else None))
    return out


def cost_floor(contract_path, preflight_path=None, meta_path=None, strict=False):
    """CF1-CF4 over a contract / run-metadata artifact carrying a cost-floor cap. Reports + gates
    record integrity; does NOT select the mode. Returns (rc, lines)."""
    contract = _read(contract_path)
    errors, warns, orphan_warns = [], [], []

    # ---- CF1 marker + token scan (all marker reads via the override_marker SSoT) --------------
    marker_modes = [m for m in _CF_MODES if has_override(contract, "cost-floor-%s" % m)]
    bare_marker = has_override(contract, "cost-floor")  # a truly bare/unsuffixed slug (boundary-matched)
    tokens = _cfo_tokens(contract)
    token_modes = sorted({mode for (mode, _ctx) in tokens})
    token_ctx = {}
    for (mode, ctx) in tokens:
        token_ctx.setdefault(mode, ctx)

    # Inert: nothing recorded -> the arm passes clean on an uncapped run.
    if not marker_modes and not bare_marker and not token_modes:
        return 0, ["OK: no cost-floor cap recorded (arm inert on an uncapped run)."]

    if bare_marker:
        errors.append("CF1: bare/unsuffixed `<!-- override: cost-floor -->` marker — the cap target "
                      "must be machine-readable; use a mode-suffixed slug (cost-floor-single-agent, "
                      "cost-floor-sequential, or cost-floor-hybrid; no cost-floor-swarm — swarm is the "
                      "ceiling).")

    if len(marker_modes) > 1:
        errors.append("CF1: conflicting cost-floor caps — %d distinct mode slugs present (%s); exactly "
                      "one cap may be honored." % (len(marker_modes), ", ".join(marker_modes)))

    for m in marker_modes:
        payloads = override_payloads(contract, "cost-floor-%s" % m)
        if any(not p.strip().lstrip("—–-").strip() for p in payloads):
            errors.append("CF1: cost-floor-%s marker carries an empty rationale — the override rationale "
                          "should reference a specific reason (budget window, exploratory round)." % m)

    cap_mode = marker_modes[0] if len(marker_modes) == 1 else None

    if cap_mode is not None:
        # ---- CF2 forward marker<->token sync ---------------------------------------------------
        if not token_modes:
            errors.append("CF2: cost-floor-%s marker present but no `cost_floor_override: %s — "
                          "<rationale>` token found — both records are required and must agree on the "
                          "mode." % (cap_mode, cap_mode))
        elif cap_mode not in token_modes:
            errors.append("CF2: marker mode (%s) does not match token mode(s) (%s) — the marker and the "
                          "cost_floor_override token must agree on the capped mode."
                          % (cap_mode, ", ".join(token_modes)))
        elif token_modes != [cap_mode]:
            errors.append("CF2: extra cost_floor_override token mode(s) (%s) disagree with the "
                          "cost-floor-%s marker." % (", ".join(token_modes), cap_mode))

        # ---- CF3 viability bound (single-agent) ------------------------------------------------
        if cap_mode == "single-agent":
            ctx = token_ctx.get("single-agent")
            if ctx is None:
                errors.append("CF3: single-agent cap does not declare `context_tier` — single-agent "
                              "viability is unevaluable without it; declare `context_tier: large` (a "
                              "single-agent cap is only viable on a >=1M-context host).")
            elif ctx == "standard":
                errors.append("CF3: single-agent cap declares `context_tier: standard` — single-agent is "
                              "the compaction-prone config below a 1M window; a single-agent cap requires "
                              "`context_tier: large`.")
            if preflight_path and os.path.isfile(preflight_path):
                pf = _read(preflight_path)
                lm = _CF_LOAD_RE.search(pf)
                if lm:
                    load = int(lm.group(1).replace(",", ""))
                    if load >= _CF_SINGLE_AGENT_LOAD_CEILING:
                        errors.append("CF3: single-agent cap but the preflight `Estimated single-agent "
                                      "load` (%d) is >= the %d bound — single-agent is not load-viable; the "
                                      "token-fit floor is sequential or higher."
                                      % (load, _CF_SINGLE_AGENT_LOAD_CEILING))
                else:
                    errors.append("CF3: single-agent cap but the preflight packet carries no `Estimated "
                                  "single-agent load:` line to bound the load against %d."
                                  % _CF_SINGLE_AGENT_LOAD_CEILING)
            else:
                errors.append("CF3: single-agent cap but NO preflight packet provided — the packet is "
                              "MANDATORY for a single-agent cap (its `Estimated single-agent load` must be "
                              "< %d)." % _CF_SINGLE_AGENT_LOAD_CEILING)

        # ---- CF3 below-floor WARN (sequential / hybrid caps) -----------------------------------
        if cap_mode in ("sequential", "hybrid") and preflight_path and os.path.isfile(preflight_path):
            fm = _CF_FLOOR_RE.search(_read(preflight_path))
            if fm:
                floor = fm.group(1).lower()
                if floor in _MODE_ORDER and _MODE_ORDER[cap_mode] < _MODE_ORDER[floor]:
                    warns.append("CF3: cost-floor-%s cap sits below the packet's token-fit floor (%s) — "
                                 "compaction/salience trade accepted per disclosure." % (cap_mode, floor))

        # ---- CF4 no silent quality-risk demotion -----------------------------------------------
        for (q, target, _hit, _rat) in _fired_triggers(contract, meta_path):
            if _MODE_ORDER.get(target, 0) > _MODE_ORDER[cap_mode]:
                if not has_override(contract, "quality-risk-Q%d" % q):
                    errors.append("CF4: quality-risk Q%d fired (target %s) exceeds the cost-floor cap "
                                  "(%s) but carries no `<!-- override: quality-risk-Q%d — … -->` marker — "
                                  "a cost cap may not silently demote a fired quality-risk decision; walk "
                                  "the named-acknowledgment path for Q%d or raise the cap."
                                  % (q, target, cap_mode, q, q))
        # CF4-unevaluable: Q4's meta branch is invisible without the sidecar.
        if (meta_path is None or not os.path.isfile(meta_path)) \
                and _MODE_ORDER[cap_mode] < _MODE_ORDER["swarm"]:
            warns.append("CF4: Q4 (prior-thin->swarm) unevaluable — meta sidecar withheld; confirm no "
                         "prior-thin escalation is being demoted by the %s cap." % cap_mode)

    # ---- CF1 reverse orphan-token check (token present, no live marker) -----------------------
    if token_modes and not marker_modes and not bare_marker:
        orphan_warns.append("CF1: cost_floor_override token(s) present (%s) with NO matching live "
                            "cost-floor marker — a recorded cap must not silently vanish because the "
                            "marker half is missing." % ", ".join(token_modes))

    # ---- assemble -----------------------------------------------------------------------------
    lines = []
    for e in errors:
        lines.append("ERROR: %s" % e)
    for w in orphan_warns:
        lines.append("%s: %s" % ("ERROR" if strict else "WARN", w))
    for w in warns:
        lines.append("WARN: %s" % w)

    n_err = len(errors) + (len(orphan_warns) if strict else 0)
    cap_str = cap_mode if cap_mode else (", ".join(token_modes) or "unresolved")
    if n_err:
        lines.append("")
        lines.append("FAILED: %d cost-floor integrity error(s). See run-core.md §Cost-floor override "
                     "(budget cap) + docs/cost-floor-dispatch.md." % n_err)
        return 1, lines
    n_warn = len(orphan_warns) + len(warns)
    if n_warn:
        lines.append("OK: cost-floor cap (%s) — record integrity holds; %d advisory warning(s) surfaced."
                     % (cap_str, n_warn))
    else:
        lines.append("OK: cost-floor cap (%s) — CF1-CF4 clean (marker<->token sync, viability bound, no "
                     "silent quality-risk demotion)." % cap_str)
    return 0, lines


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
        ov_audit = has_override(pd_text, "audit-tier-criterion-%s" % slug)

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

    if letter_text and has_override(_letter_body(letter_text), "argument-recon-prerequisite"):
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
# artifact-names — pass-artifact filename convention.
#
# Pass artifacts in an output dir must match  <Project>_Pass<N>_<Name>_<runlabel>.md.
# Faithful re-implementation of the bash glob+regex arm; the hardening is that the
# project and runlabel are matched as LITERALS (re.escape) rather than interpolated
# raw into the pattern, so a project/runlabel carrying a regex metacharacter can no
# longer distort the convention check.
# --------------------------------------------------------------------------

def artifact_names(output_dir, project, runlabel):
    pattern = re.compile(r"^%s_Pass\d+_[A-Za-z_]+_%s\.md$"
                         % (re.escape(project), re.escape(runlabel)))
    lines, errors = [], 0
    pass_files = sorted(f for f in os.listdir(output_dir)
                        if "Pass" in f and f.endswith(".md")
                        and os.path.isfile(os.path.join(output_dir, f)))
    for base in pass_files:
        if not pattern.match(base):
            lines.append("WARNING: Artifact name doesn't match convention: %s" % base)
            lines.append("  Expected pattern: %s_Pass[N]_[Name]_%s.md" % (project, runlabel))
            errors += 1

    if errors > 0:
        lines.append("")
        lines.append("FAILED: %d artifact(s) with non-standard names." % errors)
        return 1, lines
    lines.append("OK: All pass artifacts match naming convention.")
    return 0, lines


# --------------------------------------------------------------------------
# pass-header — Core DE pass-artifact §3-sourced header.
#
# Each Core DE pass artifact carries a one-line blockquote header:
#   > **Macro block:** <one of the 8> · **Writer question:** <§3 User Question>
#   · **Legacy pass id:** Pass <N>
#
# The three values are READ from pass-dependencies.md §3 (Macro Block Definitions),
# never authored. §3 is the single source of truth: the 8 blocks, each block's
# Internal Passes, and each block's User Question. This validator parses §3 into a
# pass -> (block, question) map and checks the artifact header against it.
#
#   H1  header present                     (header-less LEGACY artifact -> WARN, not ERROR)
#   H2  Macro block in the 8 AND matches §3's pass->block map for the Legacy pass id,
#       AND Writer question matches §3's User Question for that block   (ERROR)
#   H3  all three fields present + non-empty                            (ERROR)
#
# Concern-driven-run case: a run may pull a dependency pass OUTSIDE its canonical
# block (e.g., Pass 0/1 in a Characters-concern run). The header still declares the
# pass's OWN canonical §3 block — the pass->block map is by pass, not by run — so H2
# checks against §3, never against the run's concern.
# --------------------------------------------------------------------------

# A §3 row: | <Macro Block> | <Internal Passes e.g. "5 + 7"> | "<User Question>" |
# The header line the artifact carries.
_PH_HEADER_RE = re.compile(
    r"^\s*>\s*\*\*Macro block:\*\*\s*(?P<block>.*?)\s*(?:·|\|)\s*"
    r"\*\*Writer question:\*\*\s*(?P<question>.*?)\s*(?:·|\|)\s*"
    r"\*\*Legacy pass id:\*\*\s*Pass\s*(?P<pass>[0-9A-Za-z]+)\s*$"
)
# Detect a header line by its leading anchor even when malformed (so an empty-field
# header is caught by H3, not silently treated as "no header" -> WARN).
_PH_ANCHOR_RE = re.compile(r"^\s*>\s*\*\*Macro block:\*\*")


def _parse_section3(pd_text):
    """Parse pass-dependencies.md §3 into (pass_to_block, block_to_question, blocks).

    Returns:
      pass_to_block  : {pass_id_str: macro_block}
      block_to_question : {macro_block: user_question}
      blocks         : set of the macro-block names (the canonical 8)
    Only the §3 table is read (the "## §3" heading through the next "## " heading).
    """
    lines = pd_text.split("\n")
    in_s3 = False
    pass_to_block, block_to_question, blocks = {}, {}, set()
    for ln in lines:
        if re.match(r"^##\s+§3\b", ln) or re.match(r"^##\s+§3\.", ln):
            in_s3 = True
            continue
        if in_s3 and re.match(r"^##\s", ln):
            break  # left §3
        if not in_s3 or not ln.lstrip().startswith("|"):
            continue
        cells = [c.strip() for c in ln.split("|")]
        # Leading "|" => cells[0] == ""; row is | block | passes | question |
        if len(cells) < 4:
            continue
        block, passes_cell, question = cells[1], cells[2], cells[3]
        # Skip the header row and the separator row.
        if not block or block == "Macro Block" or set(block) <= set("-: "):
            continue
        # Pull integer pass ids from the Internal Passes cell (e.g. "5 + 7", "9 + 10").
        pass_ids = re.findall(r"\d+", passes_cell)
        if not pass_ids:
            continue
        question = question.strip().strip('"').strip("'")
        blocks.add(block)
        block_to_question[block] = question
        for pid in pass_ids:
            pass_to_block[pid] = block
    return pass_to_block, block_to_question, blocks


def pass_header(artifact_path, pd_path=None):
    """Validate a Core DE pass artifact's §3-sourced header (H1/H2/H3)."""
    if not pd_path:
        art_dir = os.path.dirname(artifact_path)
        cand = os.path.join(art_dir, "pass-dependencies.md")
        if os.path.isfile(cand):
            pd_path = cand
        else:
            cand2 = os.path.join(art_dir, "..", "skills", "core-editor",
                                 "references", "pass-dependencies.md")
            pd_path = cand2 if os.path.isfile(cand2) else cand
    if not os.path.isfile(pd_path):
        return 2, ["ERROR: pass-dependencies.md (§3 source of truth) not found at '%s'. "
                   "pass-header cannot validate without §3." % pd_path]

    pass_to_block, block_to_question, blocks = _parse_section3(_read(pd_path))
    if not blocks:
        return 2, ["ERROR: could not parse §3 Macro Block Definitions from '%s' — no blocks "
                   "extracted. pass-header cannot validate." % pd_path]

    art_text = _read(artifact_path)
    art_lines = art_text.split("\n")

    header_line = None
    for ln in art_lines:
        if _PH_ANCHOR_RE.match(ln):
            header_line = ln
            break

    lines, errors = [], 0

    if header_line is None:
        # H1 miss on a legacy/header-less artifact is a WARN, not an ERROR —
        # historical runs must not break.
        return 0, ["WARN: '%s' — no §3 pass header found (H1). A header-less legacy artifact "
                   "is tolerated; new pass artifacts must carry "
                   "'> **Macro block:** <block> · **Writer question:** <question> · "
                   "**Legacy pass id:** Pass <N>'." % artifact_path]

    m = _PH_HEADER_RE.match(header_line)
    if not m:
        # The anchor is present but the header is malformed / a field is missing.
        return 1, ["ERROR: '%s' — pass header present but malformed or a field is empty (H3). "
                   "Expected all three non-empty fields in "
                   "'> **Macro block:** <block> · **Writer question:** <question> · "
                   "**Legacy pass id:** Pass <N>'. Got: %s" % (artifact_path, header_line.strip())]

    block = m.group("block").strip()
    question = m.group("question").strip()
    pass_id = m.group("pass").strip()

    # H3 — all three fields non-empty.
    if not block or not question or not pass_id:
        return 1, ["ERROR: '%s' — pass header has an empty field (H3): "
                   "block=%r question=%r pass=%r." % (artifact_path, block, question, pass_id)]

    # H2 — block in the 8.
    if block not in blocks:
        lines.append("ERROR: '%s' — Macro block '%s' is not one of the 8 §3 blocks (H2). "
                     "The 8: %s." % (artifact_path, block, ", ".join(sorted(blocks))))
        errors += 1
    else:
        # H2 — block matches §3's pass->block map for this Legacy pass id.
        # An unmapped pass id is WRONG by the SSoT contract (not merely
        # uncheckable): either the header names a pass §3 doesn't define, or §3
        # is out of date. Per R4, a WARN marks ABSENCE (a header-less legacy
        # artifact, H1) — never a present-but-wrong value like this. So ERROR.
        canonical_block = pass_to_block.get(pass_id)
        if canonical_block is None:
            lines.append("ERROR: '%s' — Pass %s is not mapped in §3 — either the header is "
                         "wrong or §3 must be updated in the same change (H2). §3 maps passes: %s."
                         % (artifact_path, pass_id, ", ".join(sorted(pass_to_block, key=lambda p: int(p) if p.isdigit() else 0))))
            errors += 1
        elif canonical_block != block:
            lines.append("ERROR: '%s' — Macro block '%s' does not match §3's canonical block "
                         "for Pass %s, which is '%s' (H2). The pass↔block map is by pass, not by "
                         "run — a concern-driven run still declares the pass's own §3 block."
                         % (artifact_path, block, pass_id, canonical_block))
            errors += 1
        # H2 — Writer question matches §3's User Question for the declared block.
        expected_q = block_to_question.get(block)
        if expected_q is not None and question != expected_q:
            lines.append("ERROR: '%s' — Writer question '%s' does not match §3's User Question "
                         "for block '%s', which is '%s' (H2). Values are read from §3, never "
                         "authored." % (artifact_path, question, block, expected_q))
            errors += 1

    if errors > 0:
        lines.append("")
        lines.append("FAILED: %d pass-header failure(s). §3 (Macro Block "
                     "Definitions) in pass-dependencies.md is the single source of truth for the "
                     "block, the pass↔block map, and the User Question." % (errors,))
        return 1, lines
    lines.append("OK: pass header for '%s' agrees with §3 (block ∈ 8, block↔pass map, User "
                 "Question)." % (artifact_path,))
    return 0, lines


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
                with open(p, "w", encoding="utf-8", newline="") as fh:
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
            # 2026-06-20 override-substring hardening (override_marker.has_override): a CODE-SPAN decoy
            # and a SUFFIX-COLLISION slug must NOT suppress the Q1 trigger -> still ERROR (rc 1).
            ovq1_decoy = w("ovq1_decoy.md", "# Contract\nGENRE/SUBGENRE: Horror\nDARKNESS LEVEL: HIGH\n"
                           "POV count: 2\nGOAL: repair\nRECOMMENDED AUDITS: Consent Complexity, Reception Risk\n"
                           "Use `<!-- override: quality-risk-Q1 -->` to suppress.\n")
            ovq1_suffix = w("ovq1_suffix.md", "# Contract\nGENRE/SUBGENRE: Horror\nDARKNESS LEVEL: HIGH\n"
                            "POV count: 2\nGOAL: repair\nRECOMMENDED AUDITS: Consent Complexity, Reception Risk\n"
                            "<!-- override: quality-risk-Q1x — decoy. -->\n")
            expect("qr_over_q1_codespan_decoy_errors", quality_risk_triggers(ovq1_decoy)[0], 1)
            expect("qr_over_q1_suffix_collision_errors", quality_risk_triggers(ovq1_suffix)[0], 1)

    if which in (None, "audit-tier-criterion"):
        with tempfile.TemporaryDirectory() as td:
            audits = os.path.join(td, "audits")
            os.makedirs(audits)

            def wa(n, s):
                with open(os.path.join(audits, n), "w", encoding="utf-8", newline="") as fh:
                    fh.write(s)

            def wp(n, s):
                p = os.path.join(td, n)
                with open(p, "w", encoding="utf-8", newline="") as fh:
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
            # 2026-06-20 override-substring hardening: a CODE-SPAN decoy and a SUFFIX-COLLISION slug
            # must NOT satisfy the audit-tier-criterion override -> still ERROR (rc 1).
            over_decoy = wp("over_decoy_pd.md", "## §4a. Router-triggered audits\n| Trigger | Audit | Tier | Reference |\n|---|---|---|---|\n"
                            "| Some trigger | Soft Audit | Auto-recommend before synthesis | `audits/soft-audit.md` |\n\n"
                            "Use `<!-- override: audit-tier-criterion-soft-audit -->` to waive.\n")
            over_suffix = wp("over_suffix_pd.md", "## §4a. Router-triggered audits\n| Trigger | Audit | Tier | Reference |\n|---|---|---|---|\n"
                             "| Some trigger | Soft Audit | Auto-recommend before synthesis | `audits/soft-audit.md` |\n\n"
                             "<!-- override: audit-tier-criterion-soft-audit-not-really — decoy. -->\n")
            expect("atc_over_codespan_decoy_errors", audit_tier_criterion(over_decoy, audits)[0], 1)
            expect("atc_over_suffix_collision_errors", audit_tier_criterion(over_suffix, audits)[0], 1)
            expect("atc_edge", audit_tier_criterion(edge, audits)[0], 0)
            expect("atc_autorun", audit_tier_criterion(autorun, audits)[0], 0)
            expect("atc_findingtrig", audit_tier_criterion(findingtrig, audits)[0], 0)

    if which in (None, "argument-recon-prerequisite"):
        with tempfile.TemporaryDirectory() as td:
            def mkrun(name, files, letter=None):
                d = os.path.join(td, name)
                os.makedirs(d)
                for f in files:
                    open(os.path.join(d, f), "w", encoding="utf-8", newline="").close()
                if letter is not None:
                    with open(os.path.join(d, "Editorial_Letter.md"), "w", encoding="utf-8", newline="") as fh:
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
            # 2026-06-20 override-substring hardening: a CODE-SPAN decoy and a SUFFIX-COLLISION slug
            # must NOT satisfy the argument-recon-prerequisite override -> still ERROR (rc 1).
            over_decoy = mkrun("run_over_decoy", ["Argument_State.md"],
                               "# Editorial Letter\n## §1 What Needs Work\nMust-Fix: warrant gap.\n"
                               "Use `<!-- override: argument-recon-prerequisite -->` to waive.\n")
            over_suffix = mkrun("run_over_suffix", ["Argument_State.md"],
                                "# Editorial Letter\n## §1 What Needs Work\nMust-Fix: warrant gap.\n"
                                "<!-- override: argument-recon-prerequisite-later — decoy. -->\n")
            expect("arp_over_codespan_decoy_errors", argument_recon_prerequisite(over_decoy)[0], 1)
            expect("arp_over_suffix_collision_errors", argument_recon_prerequisite(over_suffix)[0], 1)

    if which in (None, "artifact-names"):
        with tempfile.TemporaryDirectory() as td:
            def touch(d, *names):
                os.makedirs(d, exist_ok=True)
                for n in names:
                    open(os.path.join(d, n), "w", encoding="utf-8", newline="").close()
                return d
            good = touch(os.path.join(td, "good"),
                         "Proj_Pass1_Reader_Experience_r1.md", "Proj_Pass5_Character_r1.md")
            expect("an_conforming", artifact_names(good, "Proj", "r1")[0], 0)
            touch(good, "Proj_Pass2_Structure_WRONGLABEL.md")   # wrong runlabel -> non-conforming
            expect("an_nonconforming", artifact_names(good, "Proj", "r1")[0], 1)
            empty = touch(os.path.join(td, "empty"))            # no Pass artifacts -> vacuously OK
            expect("an_no_artifacts", artifact_names(empty, "Proj", "r1")[0], 0)
            # Hardening: a project name carrying a regex metacharacter is matched as a literal,
            # so a lookalike that would satisfy an un-escaped pattern is still flagged.
            meta = touch(os.path.join(td, "meta"), "A.B_Pass1_Scene_r1.md", "AXB_Pass1_Scene_r1.md")
            expect("an_literal_project_escaped", artifact_names(meta, "A.B", "r1")[0], 1)

    if which in (None, "pass-header"):
        with tempfile.TemporaryDirectory() as td:
            def wf(n, s):
                p = os.path.join(td, n)
                with open(p, "w", encoding="utf-8", newline="") as fh:
                    fh.write(s)
                return p
            # Minimal §3 fixture (a strict subset of the canonical table shape):
            # | Macro Block | Internal Passes | User Question |
            pd = wf("pass-dependencies.md",
                    "## §3. Macro Block Definitions\n\n"
                    "| Macro Block | Internal Passes | User Question |\n"
                    "|-------------|----------------|---------------|\n"
                    "| Structure Map | 0 + 2 | \"Is the structure working?\" |\n"
                    "| Character Architecture | 5 + 7 | \"Are my characters landing?\" |\n"
                    "| Emotional Dynamics | 4 | \"Are the emotional beats earning their weight?\" |\n"
                    "| Reveal Economy | 8 | \"Is the information flow right?\" |\n\n"
                    "## §4. Audit Resolver\n")
            hdr = ("> **Macro block:** %s · **Writer question:** %s · "
                   "**Legacy pass id:** Pass %s\n\n# Body\ntext\n")
            # Positive: correct §3-sourced header (Pass 2 -> Structure Map).
            pos = wf("pos.md", hdr % ("Structure Map", "Is the structure working?", "2"))
            # Concern-driven positive: Pass 0 pulled outside its block still declares
            # its OWN canonical §3 block (Structure Map) — must PASS.
            posc = wf("posc.md", hdr % ("Structure Map", "Is the structure working?", "0"))
            # H1 WARN: no header at all -> WARN, rc 0 (legacy tolerance).
            missing = wf("missing.md", "# Pass 5 — Character Audit\n\nJust body, no header.\n")
            # H2 FAIL: Macro block not one of the 8.
            notin8 = wf("notin8.md", hdr % ("Vibes Map", "Is the structure working?", "2"))
            # H2 FAIL: block↔pass mismatch (Pass 4 is Emotional Dynamics, not Structure Map).
            mismatch = wf("mismatch.md", hdr % ("Structure Map", "Is the structure working?", "4"))
            # H2 FAIL: wrong Writer question for the (valid) block.
            wrongq = wf("wrongq.md", hdr % ("Structure Map", "Does the pacing hold?", "2"))
            # H3 FAIL: an empty field (empty Writer question).
            emptyq = wf("emptyq.md",
                        "> **Macro block:** Structure Map · **Writer question:**  · "
                        "**Legacy pass id:** Pass 2\n\n# Body\n")
            # H2 FAIL (R2): a valid block + its own question, but a Legacy pass id
            # §3 does not map (Pass 3 is not in the fixture's 0/2/5/7/4/8 set). An
            # unmapped pass is present-but-wrong by the SSoT contract -> ERROR, not
            # WARN (R4: WARN marks absence, never a present-but-wrong value).
            notmapped = wf("notmapped.md", hdr % ("Structure Map", "Is the structure working?", "3"))
            expect("ph_pos", pass_header(pos, pd)[0], 0)
            expect("ph_pos_concern_driven", pass_header(posc, pd)[0], 0)
            expect("ph_missing_header_warns", pass_header(missing, pd)[0], 0)
            expect("ph_block_not_in_8", pass_header(notin8, pd)[0], 1)
            expect("ph_block_pass_mismatch", pass_header(mismatch, pd)[0], 1)
            expect("ph_wrong_question", pass_header(wrongq, pd)[0], 1)
            expect("ph_empty_field", pass_header(emptyq, pd)[0], 1)
            expect("ph_pass_not_mapped", pass_header(notmapped, pd)[0], 1)

    if which in (None, "cost-floor"):
        with tempfile.TemporaryDirectory() as td:
            def wc(n, s):
                p = os.path.join(td, n)
                with open(p, "w", encoding="utf-8", newline="") as fh:
                    fh.write(s)
                return p

            def cf_has(res, needle):
                return any(needle in ln for ln in res[1])

            # A preflight packet whose standard-context floor is `sequential` and single-agent load is
            # well under the 600K bound (so a sequential cap is AT the floor and a single-agent cap is
            # load-viable).
            pf = wc("pf.md",
                    "# Pre-flight\n## Token Load Estimate\n"
                    "- **Estimated manuscript tokens:** 65000\n"
                    "- **Estimated single-agent load:** 140000 (manuscript + ~75K overhead)\n\n"
                    "## Dispatch Recommendations\n"
                    "- **Large-context mode (>=1M tokens):** single-agent\n"
                    "- **Standard-context mode (<1M tokens):** sequential\n")
            # A preflight whose standard-context floor is `swarm` (so a sequential cap is BELOW it) and
            # whose single-agent load exceeds the bound (so a single-agent cap is not load-viable).
            pf_swarm = wc("pf_swarm.md",
                          "# Pre-flight\n## Token Load Estimate\n"
                          "- **Estimated single-agent load:** 720000 (manuscript + ~75K overhead)\n\n"
                          "## Dispatch Recommendations\n"
                          "- **Standard-context mode (<1M tokens):** swarm\n")
            benign_meta = wc("benign.json", '{"underdiagnosis_flag": "cleared"}\n')

            hdr = "# Contract / run-metadata\nGENRE/SUBGENRE: Literary fiction\nDARKNESS LEVEL: Low\nPOV count: 1\n"
            seq = wc("seq.md", hdr + "GOAL: repair\n"
                     "<!-- override: cost-floor-sequential — $20-plan usage window; exploratory mid-draft round -->\n"
                     "cost_floor_override: sequential — $20-plan usage window; exploratory mid-draft round\n")
            # inert: no cap recorded at all
            inert = wc("inert.md", hdr + "GOAL: repair\n")
            # code-span decoy: the marker is quoted inside a code span (no live token) — must NOT be
            # honored (if it were, CF2 would fire for the missing token).
            decoy = wc("decoy.md", hdr + "GOAL: repair\n"
                       "Use `<!-- override: cost-floor-sequential — reason -->` to cap.\n")
            # suffix collision: cost-floor-single-agentx must NOT satisfy cost-floor-single-agent.
            suffix = wc("suffix.md", hdr + "GOAL: repair\n"
                        "<!-- override: cost-floor-single-agentx — decoy -->\n")
            # Q5 fires (goal=submit) + cap sequential + no Q5 marker -> CF4 ERROR naming Q5.
            q5 = wc("q5.md", "# Contract\nGENRE/SUBGENRE: Literary fiction\nPOV count: 1\nGOAL: submit\n"
                    "<!-- override: cost-floor-sequential — budget window -->\n"
                    "cost_floor_override: sequential — budget window\n")
            # …same but with the paired Q5 override marker -> exit 0.
            q5_ok = wc("q5_ok.md", "# Contract\nGENRE/SUBGENRE: Literary fiction\nPOV count: 1\nGOAL: submit\n"
                       "<!-- override: cost-floor-sequential — budget window -->\n"
                       "cost_floor_override: sequential — budget window\n"
                       "<!-- override: quality-risk-Q5 — final polish; accept single-context risk -->\n")
            # orphan token, no marker.
            orphan = wc("orphan.md", "# run-metadata\ncost_floor_override: sequential — budget window\n")
            # single-agent caps.
            sa_std = wc("sa_std.md", hdr + "GOAL: repair\n"
                        "<!-- override: cost-floor-single-agent — 1M host, cheap run -->\n"
                        "cost_floor_override: single-agent; context_tier: standard — 1M host, cheap run\n")
            sa_noctx = wc("sa_noctx.md", hdr + "GOAL: repair\n"
                          "<!-- override: cost-floor-single-agent — cheap run -->\n"
                          "cost_floor_override: single-agent — cheap run\n")
            sa_large = wc("sa_large.md", hdr + "GOAL: repair\n"
                          "<!-- override: cost-floor-single-agent — 1M host -->\n"
                          "cost_floor_override: single-agent; context_tier: large — 1M host\n")
            # conflicting dual-mode markers.
            conflict = wc("conflict.md", hdr + "GOAL: repair\n"
                          "<!-- override: cost-floor-sequential — a -->\n"
                          "<!-- override: cost-floor-hybrid — b -->\n"
                          "cost_floor_override: sequential — a\n")
            # empty rationale on the marker.
            empty = wc("empty.md", hdr + "GOAL: repair\n"
                       "<!-- override: cost-floor-sequential -->\n"
                       "cost_floor_override: sequential — reason\n")
            # marker<->token mode mismatch.
            mismatch = wc("mismatch.md", hdr + "GOAL: repair\n"
                          "<!-- override: cost-floor-sequential — a -->\n"
                          "cost_floor_override: hybrid — a\n")
            # bare/unsuffixed marker.
            bare = wc("bare.md", hdr + "GOAL: repair\n"
                      "<!-- override: cost-floor — no mode -->\n")

            expect("cf_clean", cost_floor(seq, pf, benign_meta)[0], 0)
            expect("cf_inert", cost_floor(inert)[0], 0)
            expect("cf_codespan_decoy_not_honored", cost_floor(decoy)[0], 0)
            expect("cf_suffix_collision_not_honored", cost_floor(suffix)[0], 0)
            expect("cf_q5_demotion_errors", cost_floor(q5, pf)[0], 1)
            expect("cf_q5_names_q5", cf_has(cost_floor(q5, pf), "Q5"), True)
            expect("cf_q5_with_marker_ok", cost_floor(q5_ok, pf)[0], 0)
            expect("cf_orphan_warn_default", cost_floor(orphan)[0], 0)
            expect("cf_orphan_error_strict", cost_floor(orphan, strict=True)[0], 1)
            expect("cf_sa_context_standard_errors", cost_floor(sa_std, pf)[0], 1)
            expect("cf_sa_context_absent_errors", cost_floor(sa_noctx, pf)[0], 1)
            expect("cf_sa_no_packet_errors", cost_floor(sa_large, None)[0], 1)
            expect("cf_sa_large_ok", cost_floor(sa_large, pf)[0], 0)
            expect("cf_sa_heavy_load_errors", cost_floor(sa_large, pf_swarm)[0], 1)
            expect("cf_seq_below_floor_warn",
                   cf_has(cost_floor(seq, pf_swarm, benign_meta), "below the packet's token-fit floor"), True)
            expect("cf_seq_below_floor_still_pass", cost_floor(seq, pf_swarm, benign_meta)[0], 0)
            expect("cf_q4_unevaluable_warn", cf_has(cost_floor(seq, pf), "Q4 (prior-thin"), True)
            expect("cf_conflict_errors", cost_floor(conflict)[0], 1)
            expect("cf_empty_rationale_errors", cost_floor(empty)[0], 1)
            expect("cf_mismatch_errors", cost_floor(mismatch)[0], 1)
            expect("cf_bare_marker_errors", cost_floor(bare)[0], 1)

            # _fired_triggers per-trigger (q, target) mapping — CF4 is driven by THESE, never the
            # aggregate escalation string or parsed report text.
            def qt(text):
                return [(q, t) for (q, t, _h, _r) in _fired_triggers(text)]
            expect("ft_q1_hybrid",
                   qt("GENRE/SUBGENRE: Horror\nDARKNESS LEVEL: HIGH\nPOV count: 1\nGOAL: repair\n"),
                   [(1, "hybrid")])
            expect("ft_q5_swarm",
                   qt("GENRE/SUBGENRE: Literary fiction\nPOV count: 1\nGOAL: submit\n"), [(5, "swarm")])
            expect("ft_q3_swarm_6pov",
                   (3, "swarm") in qt("GENRE/SUBGENRE: Literary fiction\nPOV count: 7\nGOAL: repair\n"),
                   True)

    print("Self-test: PASS" if rc["v"] == 0 else "Self-test: FAIL")
    return rc["v"]


_CHECKS = {
    "quality-risk-triggers": (quality_risk_triggers, True),       # (fn, file-must-exist)
    "cost-floor": (cost_floor, True),   # registered for the dispatch map; multi-arg (preflight + meta
                                        # + --strict) is handled by the dedicated main() branch below.
    "audit-tier-criterion": (audit_tier_criterion, True),
    "argument-recon-prerequisite": (argument_recon_prerequisite, False),  # arg is a directory
    "pass-header": (pass_header, True),
}


def main(argv):
    if len(argv) < 2:
        sys.stderr.write("Usage: config_checks.py <quality-risk-triggers|cost-floor|"
                         "audit-tier-criterion|argument-recon-prerequisite|pass-header|--self-test> ...\n")
        return 2
    if argv[1] == "--self-test":
        return run_self_test(argv[2] if len(argv) > 2 else None)
    if argv[1] == "cost-floor":
        # Dedicated multi-arg branch (the generic _CHECKS dispatch passes a single extra arg, which
        # cannot carry both the preflight packet and the meta sidecar plus --strict).
        rest = argv[2:]
        strict = "--strict" in rest
        pos = [a for a in rest if not a.startswith("--")]
        if not pos:
            sys.stderr.write("Usage: config_checks.py cost-floor <contract_or_run_metadata_file> "
                             "[<preflight_packet.md>] [<diagnostic_state_meta.json>] [--strict]\n")
            return 2
        contract = pos[0]
        if not os.path.isfile(contract):
            sys.stderr.write("Error: File not found: %s\n" % contract)
            return 2
        preflight = pos[1] if len(pos) > 1 else None
        meta = pos[2] if len(pos) > 2 else None
        return _emit(*cost_floor(contract, preflight, meta, strict=strict))
    if argv[1] == "artifact-names":
        if len(argv) < 5:
            sys.stderr.write("Usage: config_checks.py artifact-names <output_dir> <project> <runlabel>\n")
            return 2
        out_dir = argv[2]
        if not os.path.isdir(out_dir):
            sys.stderr.write("Error: Directory not found: %s\n" % out_dir)
            return 2
        return _emit(*artifact_names(out_dir, argv[3], argv[4]))
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
