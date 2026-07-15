#!/usr/bin/env python3
"""argument-agd — the AGD Move Audit validator (R3A).

Validates an `Argument_State.md` §10.9 "AGD Move Audit" block (the companion audit defined in
plugins/apodictic/skills/specialized-audits/references/craft/argument-agd-audit.md): the coverage
manifest, the typed M-records, the total family×challenge×result matrix, the neutrality firewall
(candidates licensed ONLY by failed function), the candidate namespace + reconciliation grammar,
the DISCOUNTING cross-ref contract, the OPTIONAL §1b `Scan:` scan-consumption coverage line (R3B
AGD producer/consumer seam — integers; k+m=n; m == the count of `Declined:` lines; the not-consulted
reason enum is `absent | error` only; lookalike spellings and duplicate `Scan:` lines are errors,
never silently ignored; and, with `--scan <agd_move_scan.json>`, n == len(results.observations),
FAILING CLOSED on an unreadable artifact — while a READABLE supplied artifact REQUIRES a
consulted line: a denied or missing line with the artifact present would skip the cross-check
entirely), and — when a source text is supplied — Source-anchor resolution via
NORMALIZED substring matching (greenfield: whitespace runs folded, quote chars and dashes
normalized, otherwise case-sensitive; near-misses like paraphrase or elision must FAIL).

Structural parse throughout (heading walk + line grammar) — no doc-wide regex scope. The candidate
namespace is DERIVED, never hardcoded: the Dialectical Clarity codes come from argument_crosswalk's
scoped table-walk of dialectical-clarity.md, minus the AT1-AT5 type labels (classifications, not
diagnoses; AT0 stays), plus FM-A1..FM-A20 from argument_groundtruth._FM_A_MAX = 67 codes.

Usage:
  argument_agd.py --self-test
  argument_agd.py argument-agd <argument_state.md> [--source <source.md>] [--scan <agd_move_scan.json>] [--strict]
"""
import json
import os
import re
import sys

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

# --------------------------------------------------------------------------
# Vocabulary (mirrors the audit doc; the validator is the mechanical gate)
# --------------------------------------------------------------------------
FAMILIES = ("ASSURING", "GUARDING", "DISCOUNTING")
CHALLENGE_OF = {"ASSURING": "STRIP", "GUARDING": "COMMITMENT", "DISCOUNTING": "ENGAGEMENT"}
# Total family x result matrix (NOT-CHALLENGED legal for every family).
RESULTS_OF = {
    "ASSURING": {"SURVIVES", "COLLAPSES", "INDETERMINATE", "NOT-CHALLENGED"},
    "GUARDING": {"SURVIVES", "COLLAPSES", "SELF-SEALS", "INDETERMINATE", "NOT-CHALLENGED"},
    "DISCOUNTING": {"SURVIVES", "COLLAPSES-DECOY", "COLLAPSES-COSTLESS", "INDETERMINATE",
                    "NOT-CHALLENGED"},
}
# Results that license candidates (failed function). Everything else => Candidates: NONE,
# except the GUARDING Trajectory: DISAPPEARING whitelist below.
FAILED_RESULTS = {"COLLAPSES", "SELF-SEALS", "COLLAPSES-DECOY", "COLLAPSES-COSTLESS"}
DISAPPEARING_WHITELIST = {"FM-A16", "WR3", "BP4"}
CANDIDATES_OF = {
    ("ASSURING", "COLLAPSES"): {"WR1", "DI0", "FM-A19", "SM4", "FM-A11"},
    ("GUARDING", "COLLAPSES"): {"DI3", "WR3"},
    ("GUARDING", "SELF-SEALS"): {"DI3", "BP0"},
    ("DISCOUNTING", "COLLAPSES-DECOY"): {"OB5", "OB1"},
    ("DISCOUNTING", "COLLAPSES-COSTLESS"): {"OB4"},
}
COMPLETIONS = {"COMPLETE", "PARTIAL"}
STATUSES = ("PENDING", "CONFIRMED", "DECLINED")

_M_HEADER_RE = re.compile(r"^M(\d+):\s+([A-Z-]+)\s+at\s+(.+?)\s*$")
_SPAN_TOKEN_RE = re.compile(r"^(C\d+(\.(warrant|support))?|C0)$")
_OBJ_REF_RE = re.compile(r"^→\s*Objection\s+\d+$")
_DISAPPEARING_RE = re.compile(r"^DISAPPEARING\s+\((.+?)\s+→\s+(.+?)\)$")
_CAND_RE = re.compile(r"^([A-Z][A-Z0-9-]*)\s+\((PENDING|CONFIRMED\s+—\s+[^,]+,\s+[^)]+|"
                      r"DECLINED\s+—\s+[^)]+)\)$")

# --------------------------------------------------------------------------
# §1b scan-consumption coverage line (R3B AGD producer/consumer seam). The
# AGD Move Scan (setec agd_move_scan) emits LOCATED observations; the audit
# consumes them in its Layer-1 pre-pass and records the outcome as a §10.9
# coverage line. Structural line parse throughout; bounded leaf regexes on the
# count / reason tokens ONLY (the fleet gt-validator rule). The audit alone
# assigns codes (R4A ADR D5) — a scan observation is a pointer, never a finding.
# --------------------------------------------------------------------------
_SCAN_CONSULTED_RE = re.compile(
    r"^consulted \((\d+) observations?; (\d+) inventoried, (\d+) declined\)$")
_SCAN_NOT_CONSULTED_RE = re.compile(r"^not consulted \((absent|error)\)$")
_DECLINED_LINE_RE = re.compile(r'^Declined:\s+"(.+)"\s+—\s+(.+)$')


def _parse_scan_line(s, manifest, errs):
    """Recognize + shape-parse the §10.9 'Scan:' coverage line. Today an
    unrecognized column-0 line is silently ignored; this teaches the manifest
    parser the line so its counts are shape-checked (the two-value not-consulted
    reason enum is `absent | error` ONLY)."""
    rest = s[len("Scan:"):].strip()
    cm = _SCAN_CONSULTED_RE.match(rest)
    if cm:
        manifest["scan"] = {"kind": "consulted", "n": int(cm.group(1)),
                            "k": int(cm.group(2)), "m": int(cm.group(3))}
        return
    nm = _SCAN_NOT_CONSULTED_RE.match(rest)
    if nm:
        manifest["scan"] = {"kind": "not_consulted", "reason": nm.group(1)}
        return
    manifest["scan"] = {"kind": "malformed"}
    if rest.startswith("not consulted"):
        errs.append("Scan: not-consulted reason must be exactly (absent) or (error) — that "
                    "two-value enum only (got %r)." % s)
    else:
        errs.append("Scan: line malformed — expected 'Scan: consulted (<n> observations; "
                    "<k> inventoried, <m> declined)' or 'Scan: not consulted (absent|error)' "
                    "(got %r)." % s)


def _parse_declined_line(s, manifest, errs):
    """Recognize + shape-parse an indented 'Declined:' line under a consulted
    Scan. Every 'Declined:' line counts toward m (well-formed or not); a
    malformed one also raises its own error."""
    dm = _DECLINED_LINE_RE.match(s)
    if dm:
        manifest["scan_declined"].append((dm.group(1).strip(), dm.group(2).strip()))
    else:
        manifest["scan_declined"].append(None)
        errs.append('Scan: %r malformed — expected \'Declined: "<span fragment>" — '
                    "<one-clause reason>'." % s)


# --------------------------------------------------------------------------
# Candidate namespace — DERIVED (argument_crosswalk's scoped parse + _FM_A_MAX)
# --------------------------------------------------------------------------
def candidate_namespace():
    import argument_crosswalk as xw
    from argument_groundtruth import _FM_A_MAX
    reg = xw._registry_path()
    if reg is None:
        raise RuntimeError("dialectical-clarity.md registry not found; cannot derive the namespace")
    with open(reg, "r", encoding="utf-8") as fh:
        dc = xw.parse_dc_codes(fh.read())
    ns = (set(dc) - {"AT1", "AT2", "AT3", "AT4", "AT5"}) | {"FM-A%d" % i for i in range(1, _FM_A_MAX + 1)}
    return ns


# --------------------------------------------------------------------------
# Anchor normalization (greenfield — near-misses must FAIL)
# --------------------------------------------------------------------------
def _norm(s):
    s = s.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
    s = s.replace("—", "-").replace("–", "-")
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def anchor_resolves(quote, source_text):
    """Normalized substring: whitespace folded, quotes/dashes normalized, case-sensitive."""
    return _norm(quote) in _norm(source_text)


# --------------------------------------------------------------------------
# Structural parse of the §10.9 section
# --------------------------------------------------------------------------
def extract_section(text):
    """Return the §10.9 body (heading walk: from '### 10.9 AGD Move Audit' to the next heading)."""
    lines = text.splitlines()
    start = None
    for i, ln in enumerate(lines):
        if ln.strip() == "### 10.9 AGD Move Audit":
            start = i + 1
            break
    if start is None:
        return None
    body = []
    for ln in lines[start:]:
        if ln.startswith("### ") or ln.startswith("## "):
            break
        body.append(ln)
    return "\n".join(body)


def parse_ladder(text):
    """Cn ids from '## 2. Claim Architecture' ('C1:' ladder lines). None if no §2 section."""
    lines = text.splitlines()
    in2 = False
    found_section = False
    ids = set()
    for ln in lines:
        s = ln.strip()
        if s.startswith("## 2."):
            in2, found_section = True, True
            continue
        if in2 and s.startswith("## "):
            break
        if in2:
            m = re.match(r"^(C\d+)\s*[:(]", s)
            if m and m.group(1) != "C0":
                ids.add(m.group(1))
    return ids if found_section else None


def parse_objections(text):
    """Objection indices from §6 ('Objection N:' or producer-form 'OBJECTION N:').
    None if no §6 section (degrade-not-fail, the parse_ladder convention)."""
    lines = text.splitlines()
    in6, found = False, False
    idxs = set()
    for ln in lines:
        s = ln.strip()
        if s.startswith("## 6."):
            in6, found = True, True
            continue
        if in6 and s.startswith("## "):
            break
        if in6:
            m = re.match(r"^Objection\s+(\d+)\s*:", s, re.IGNORECASE)
            if m:
                idxs.add(int(m.group(1)))
    return idxs if found else None


def parse_block(body):
    """(manifest, records, parse_errs). Manifest = dict; records = list of dicts (ordered fields)."""
    manifest = {"spans": [], "excluded": [], "move_count": None, "completion": None,
                "scan": None, "scan_declined": []}
    records, errs = [], []
    cur = None
    for raw in body.splitlines():
        line = raw.rstrip()
        s = line.strip()
        if not s or s.startswith("_Status") or s.startswith("["):
            continue
        if re.match(r"^M\d+\s*:", s) and not _M_HEADER_RE.match(s):
            errs.append("malformed M-record header (expected 'M<k>: <FAMILY> at <locus>'): %r" % s)
            cur = None  # do NOT absorb the malformed record's fields into the previous record
            continue
        m = _M_HEADER_RE.match(s)
        if m:
            cur = {"idx": int(m.group(1)), "family": m.group(2), "locus": m.group(3).strip(),
                   "fields": {}}
            records.append(cur)
            continue
        if cur is not None and line.startswith("  ") and ":" in s:
            key, _, val = s.partition(":")
            cur["fields"][key.strip()] = val.strip()
            continue
        if cur is None:
            if s.startswith("Span:"):
                rest = s[len("Span:"):].strip()
                tok, sep, locus = rest.partition("—")
                if not sep:
                    errs.append("manifest: Span line lacks the '—' separator: %r" % s)
                else:
                    manifest["spans"].append((tok.strip(), locus.strip()))
            elif s.startswith("Excluded:"):
                rest = s[len("Excluded:"):].strip()
                span, sep, reason = rest.partition("—")
                if not sep or not reason.strip():
                    errs.append("manifest: Excluded line needs '<span> — <reason>': %r" % s)
                else:
                    manifest["excluded"].append((span.strip(), reason.strip()))
            elif s.startswith("Move count:"):
                v = s[len("Move count:"):].strip()
                manifest["move_count"] = int(v) if re.fullmatch(r"\d+", v) else v
            elif s.startswith("Completion:"):
                manifest["completion"] = s[len("Completion:"):].strip()
            elif s.startswith("Scan:"):
                if manifest["scan"] is not None:
                    errs.append("Scan: duplicate line — the coverage manifest carries at most "
                                "one 'Scan:' line (first kept, %r rejected)." % s)
                else:
                    _parse_scan_line(s, manifest, errs)
            elif s.startswith("Declined:"):
                _parse_declined_line(s, manifest, errs)
            elif re.match(r"(?i)(scan|declined)\s*:", s):
                # Lookalike tripwire: an absent Scan: line is VALID (pre-R3B), so a
                # case/spacing variant would otherwise vanish as an ignored
                # unrecognized line — masquerading as the pre-R3B case.
                errs.append("Scan: lookalike line %r — the canonical spellings are exactly "
                            "'Scan:' and 'Declined:' (case-sensitive, no space before the "
                            "colon); an absent Scan: line is the only valid omission." % s)
    return manifest, records, errs


# --------------------------------------------------------------------------
# Core validation (pure over inputs)
# --------------------------------------------------------------------------
def validate(body, namespace, ladder_cns=None, source_text=None, objection_idxs=None,
             scan_observations=None):
    """Returns (errors, warns). `scan_observations` (int | None) is the number
    of observations in the consumed agd_move_scan artifact, supplied in
    fixture/--check-all mode so `Scan: consulted (<n> …)` can be cross-checked
    against `len(results.observations)`; None leaves that one arm unchecked."""
    errors, warns = [], []
    manifest, records, perrs = parse_block(body)
    errors.extend(perrs)

    # ---- Check 5: coverage manifest ----
    if not manifest["spans"]:
        errors.append("Check 5 (coverage) — no Span: lines; the manifest is required.")
    completion = manifest["completion"]
    if completion not in COMPLETIONS:
        errors.append("Check 5 (coverage) — Completion must be COMPLETE|PARTIAL (got %r)." % completion)
    if completion == "PARTIAL":
        if not manifest["excluded"]:
            errors.append("Check 5 (coverage) — PARTIAL requires >=1 'Excluded: <span> — <reason>' line.")
        warns.append("Check 5 (coverage) — Completion: PARTIAL (declared-scope audit; "
                     "excluded: %s)." % (", ".join(t for t, _ in manifest["excluded"]) or "?"))
    span_tokens = [t for t, _ in manifest["spans"]]
    excluded_tokens = [t for t, _ in manifest["excluded"]]
    span_loci = {l for _, l in manifest["spans"]}
    for tok in span_tokens:
        if not _SPAN_TOKEN_RE.match(tok):
            errors.append("Check 5 (coverage) — bad span token %r (C0 | Cn[.warrant|.support])." % tok)
    for tok in excluded_tokens:
        if not _SPAN_TOKEN_RE.match(tok):
            errors.append("Check 5 (coverage) — bad excluded token %r "
                          "(C0 | Cn[.warrant|.support])." % tok)
    if isinstance(manifest["move_count"], int):
        if manifest["move_count"] != len(records):
            errors.append("Check 5 (coverage) — Move count %d != %d records present."
                          % (manifest["move_count"], len(records)))
    else:
        errors.append("Check 5 (coverage) — Move count must be an integer (got %r)." % manifest["move_count"])
    if ladder_cns is not None:
        expected = {"C0"} | set(ladder_cns)
        covered = {t.split(".", 1)[0] for t in span_tokens if _SPAN_TOKEN_RE.match(t)}
        excluded = {t.split(".", 1)[0] for t in excluded_tokens if _SPAN_TOKEN_RE.match(t)}
        unknown = sorted((covered | excluded) - expected)
        overlap = sorted(covered & excluded)
        missing = sorted(expected - covered - excluded)
        if unknown:
            errors.append("Check 5 (coverage) — manifest names claims absent from the §2 ladder: %s."
                          % unknown)
        if overlap:
            errors.append("Check 5 (coverage) — claims cannot be both included and excluded: %s."
                          % overlap)
        if "C0" not in covered:
            errors.append("Check 5 (coverage) — C0 must be a declared included Span.")
        if missing:
            errors.append("Check 5 (coverage) — ladder claims neither included nor excluded: %s."
                          % missing)
        if completion == "COMPLETE" and excluded:
            errors.append("Check 5 (coverage) — COMPLETE cannot carry Excluded claims: %s." %
                          sorted(excluded))
    elif ladder_cns is None:
        warns.append("Check 5 (coverage) — no §2 Claim Architecture in the artifact; "
                     "ladder cross-check SKIPPED (degrade, not fail).")

    # ---- Check 5c: §1b scan-consumption coverage line (R3B AGD seam) ----
    # OPTIONAL: an absent Scan: line is the valid pre-R3B case (no check). A
    # present line is shape-checked: integers (guaranteed by the leaf regex);
    # k + m == n; m == the count of Declined: lines; and — with the scan
    # artifact supplied (fixture/--check-all) — n == len(results.observations).
    # The scan is a POINTER: this validates the coverage bookkeeping only; it
    # never adjudicates a move (the audit's own M-records do that, R4A ADR D5).
    scan = manifest.get("scan")
    declined_lines = manifest.get("scan_declined", [])
    # A supplied, READABLE artifact requires a consulted line: §1b routes a
    # readable artifact to the cross-check, and 'not consulted (error)' is
    # reserved for an absent/malformed capture (which --scan fails closed on
    # before reaching here). A denied or missing line with the artifact present
    # would let a fixture ship the artifact and skip the cross-check entirely —
    # defeating the consumption gate. (kind == "malformed" already errored in
    # the parser; real audit runs without --scan are unaffected.)
    if scan_observations is not None and (
            scan is None or scan.get("kind") == "not_consulted"):
        errors.append("Check 5 (scan) — a readable scan artifact was supplied (%d observations) "
                      "but the manifest %s; with the artifact present and parseable the coverage "
                      "line must be 'Scan: consulted (…)' recording the cross-check."
                      % (scan_observations,
                         "claims 'Scan: not consulted'" if scan is not None
                         else "carries no 'Scan:' line"))
    if scan is not None and scan.get("kind") == "consulted":
        n, k, m = scan["n"], scan["k"], scan["m"]
        if k + m != n:
            errors.append("Check 5 (scan) — inventoried + declined must equal observations "
                          "(%d inventoried + %d declined != %d observations)." % (k, m, n))
        if m != len(declined_lines):
            errors.append("Check 5 (scan) — declined count %d != %d 'Declined:' line(s)."
                          % (m, len(declined_lines)))
        if scan_observations is not None and n != scan_observations:
            errors.append("Check 5 (scan) — Scan: reports %d observations but the scan artifact "
                          "carries %d (results.observations)." % (n, scan_observations))
    elif scan is not None and scan.get("kind") == "not_consulted":
        if declined_lines:
            errors.append("Check 5 (scan) — 'not consulted' carries %d 'Declined:' line(s); "
                          "declines belong only to a consulted scan." % len(declined_lines))
    elif scan is None and declined_lines:
        errors.append("Check 5 (scan) — 'Declined:' line(s) present with no 'Scan:' line.")
    # scan.kind == "malformed": _parse_scan_line already appended the parse error.

    seen_idx = set()
    for r in records:
        rid = "M%d" % r["idx"]
        f = r["fields"]
        fam, locus = r["family"], r["locus"]
        if r["idx"] in seen_idx:
            errors.append("%s — duplicate record index." % rid)
        seen_idx.add(r["idx"])

        # ---- Check 1: matrix totality ----
        if fam not in FAMILIES:
            errors.append("%s — unknown family %r." % (rid, fam))
            continue
        challenge = f.get("Challenge")
        result = f.get("Result")
        if challenge != CHALLENGE_OF[fam]:
            errors.append("%s (Check 1) — %s requires Challenge: %s (got %r)."
                          % (rid, fam, CHALLENGE_OF[fam], challenge))
        if result not in RESULTS_OF[fam]:
            errors.append("%s (Check 1) — Result %r not legal for %s (legal: %s)."
                          % (rid, result, fam, sorted(RESULTS_OF[fam])))
            continue

        # ---- Check 4: anchor discipline ----
        anchor = f.get("Source anchor", "")
        am = re.match(r'^"(.+)"\s+@\s+(.+)$', anchor)
        if not am:
            errors.append('%s (Check 4) — Source anchor must be "<verbatim quote>" @ <locus> (got %r).'
                          % (rid, anchor))
        elif source_text is not None and not anchor_resolves(am.group(1), source_text):
            errors.append("%s (Check 4) — Source anchor does not resolve in the source text: %r"
                          % (rid, am.group(1)))
        if "Cue" not in f or not f.get("Cue"):
            errors.append("%s (Check 4) — Cue is required (a surface cue, or the first-class NONE)." % rid)

        # ---- Check 5b: record locus within declared spans ----
        if span_loci and locus not in span_loci:
            errors.append("%s (Check 5) — record locus %r is not a declared Span locus." % (rid, locus))

        # ---- Check 2: firewall (both directions) + construction discipline ----
        cands_raw = f.get("Candidates", "")
        constructed = f.get("Constructed challenge")
        basis = f.get("Assessment basis")
        trajectory = f.get("Trajectory")
        trajectory_match = _DISAPPEARING_RE.fullmatch(trajectory or "")
        disappearing = bool(trajectory_match)
        cand_entries = []
        if cands_raw and cands_raw != "NONE":
            for part in cands_raw.split(";"):
                part = part.strip()
                if not part:
                    continue
                cm = _CAND_RE.match(part)
                if not cm:
                    errors.append("%s (Check 3) — bad candidate entry %r (grammar: CODE (PENDING) | "
                                  "CODE (CONFIRMED — <adjudicator>, <target ref>) | "
                                  "CODE (DECLINED — <basis>))." % (rid, part))
                else:
                    cand_entries.append(cm.group(1))
        allowed_candidates = set(CANDIDATES_OF.get((fam, result), set()))
        if disappearing and fam == "GUARDING":
            allowed_candidates |= DISAPPEARING_WHITELIST
        bad_candidates = [c for c in cand_entries if c not in allowed_candidates]
        if bad_candidates:
            errors.append("%s (Check 2) — %s × %s%s licenses only %s; got %s."
                          % (rid, fam, result,
                             " + DISAPPEARING" if disappearing and fam == "GUARDING" else "",
                             sorted(allowed_candidates) or "NONE", bad_candidates))
        if not cands_raw:
            errors.append("%s (Check 2) — Candidates field is required (use NONE)." % rid)
        if result == "NOT-CHALLENGED" and constructed:
            errors.append("%s (Check 2) — NOT-CHALLENGED carries a Constructed challenge; "
                          "an un-run challenge has no construction." % rid)
        if challenge in ("STRIP", "COMMITMENT") and result not in (None, "NOT-CHALLENGED"):
            if not constructed:
                errors.append("%s (Check 2) — a run %s challenge requires its Constructed challenge."
                              % (rid, challenge))
            if not basis:
                errors.append("%s (Check 2) — a run challenge requires an Assessment basis." % rid)
        if challenge == "ENGAGEMENT":
            if constructed:
                errors.append("%s (Check 2) — ENGAGEMENT constructs no text; remove the "
                              "Constructed challenge field." % rid)
            if result not in (None, "NOT-CHALLENGED") and not basis:
                errors.append("%s (Check 2) — a run challenge requires an Assessment basis." % rid)

        # ---- Check 3: candidate namespace ----
        for c in cand_entries:
            if c not in namespace:
                errors.append("%s (Check 3) — candidate %r not in the derived 67-code namespace "
                              "(DC minus AT1-AT5, plus FM-A1-20)." % (rid, c))

        # ---- Check 6: per-family fields + the DISCOUNTING cross-ref contract ----
        if trajectory and not (trajectory == "STABLE" or trajectory_match):
            errors.append("%s (Check 6) — Trajectory must be STABLE or DISAPPEARING (early locus → "
                          "late locus); got %r." % (rid, trajectory))
        if trajectory_match:
            early, late = (trajectory_match.group(1).strip(), trajectory_match.group(2).strip())
            if early == late:
                errors.append("%s (Check 6) — DISAPPEARING trajectory needs distinct early and late "
                              "loci." % rid)
            unresolved = [loc for loc in (early, late) if span_loci and loc not in span_loci]
            if unresolved:
                errors.append("%s (Check 6) — DISAPPEARING trajectory loci are not declared Spans: %s."
                              % (rid, unresolved))
        if trajectory and fam != "GUARDING":
            errors.append("%s (Check 6) — Trajectory is GUARDING-only." % rid)
        discounted = f.get("Discounted")
        displaced = f.get("Displaced strongest")
        if (discounted or displaced) and fam != "DISCOUNTING":
            errors.append("%s (Check 6) — Discounted / Displaced strongest are DISCOUNTING-only." % rid)
        if fam == "DISCOUNTING":
            if result != "NOT-CHALLENGED" and not discounted:
                errors.append("%s (Check 6) — a run DISCOUNTING record requires Discounted: "
                              "(→ Objection N | NOT-INVENTORIED)." % rid)
            if discounted and discounted != "NOT-INVENTORIED" and not _OBJ_REF_RE.match(discounted):
                errors.append("%s (Check 6) — Discounted must be '→ Objection N' or NOT-INVENTORIED "
                              "(got %r)." % (rid, discounted))
            # resolution (degrade-not-fail when §6 absent): a '→ Objection N' ref must exist in §6
            if objection_idxs is not None:
                for label, ref in (("Discounted", discounted), ("Displaced strongest", displaced)):
                    if ref and _OBJ_REF_RE.match(ref):
                        n = int(re.search(r"(\d+)$", ref).group(1))
                        if n not in objection_idxs:
                            errors.append("%s (Check 6) — %s references Objection %d, which is not "
                                          "in the §6 inventory." % (rid, label, n))
            if result == "COLLAPSES-DECOY":
                if not displaced or not _OBJ_REF_RE.match(displaced):
                    errors.append("%s (Check 6) — COLLAPSES-DECOY requires Displaced strongest: "
                                  "→ Objection N (the §6 STRONGEST OBJECTION)." % rid)
                elif objection_idxs is not None:
                    displaced_n = int(re.search(r"(\d+)$", displaced).group(1))
                    if displaced_n != 1:
                        errors.append("%s (Check 6) — Displaced strongest must reference Objection 1, "
                                      "the §6 strongest-objection slot (got Objection %d)."
                                      % (rid, displaced_n))
            elif displaced:
                errors.append("%s (Check 6) — Displaced strongest is COLLAPSES-DECOY-only." % rid)
            if result == "COLLAPSES-DECOY" and discounted == "NOT-INVENTORIED":
                errors.append("%s (Check 6) — a DECOY result names the engaged (inventoried) decoy "
                              "objection; Discounted: NOT-INVENTORIED is self-contradictory here "
                              "(legal only on SURVIVES/INDETERMINATE)." % rid)
            if result == "COLLAPSES-COSTLESS" and discounted == "NOT-INVENTORIED":
                errors.append("%s (Check 6) — COLLAPSES-COSTLESS requires a RESOLVING Discounted "
                              "cross-ref (Step 6's sweep adds the objection; the grading delegation "
                              "needs a target). NOT-INVENTORIED is legal only on SURVIVES/INDETERMINATE."
                              % rid)
        if fam == "GUARDING" and result != "NOT-CHALLENGED" and not trajectory:
            errors.append("%s (Check 6) — a run GUARDING record requires Trajectory: STABLE | "
                          "DISAPPEARING (early locus → late locus)." % rid)

    return errors, warns


# --------------------------------------------------------------------------
# CLI + real-file mode
# --------------------------------------------------------------------------
def run_check(state_path, source_path=None, strict=False, scan_path=None):
    if not os.path.exists(state_path):
        print("ERROR: artifact not found: %s" % state_path)
        return 1
    with open(state_path, "r", encoding="utf-8") as fh:
        text = fh.read()
    body = extract_section(text)
    if body is None:
        print("ERROR: no '### 10.9 AGD Move Audit' section in %s" % state_path)
        return 1
    source_text = None
    if source_path:
        if not os.path.exists(source_path):
            print("ERROR: source text not found: %s" % source_path)
            return 1
        with open(source_path, "r", encoding="utf-8") as fh:
            source_text = fh.read()
    # --scan: the consumed agd_move_scan artifact. Read results.observations
    # only (the count); the audit's §10.9 M-records — never the scan — carry the
    # adjudication. FAIL CLOSED on a present-but-unreadable artifact: --scan is
    # supplied exactly when the caller (a fixture / --check-all) expects a valid
    # committed artifact, and the n-cross-check is a BLOCKING gate — degrading
    # it to a warning would let a corrupted artifact pass. (An audit run that
    # itself hit a malformed artifact records 'Scan: not consulted (error)' and
    # is validated WITHOUT --scan.)
    scan_observations = None
    if scan_path:
        if not os.path.exists(scan_path):
            print("ERROR: scan artifact not found: %s" % scan_path)
            return 1
        try:
            with open(scan_path, "r", encoding="utf-8") as fh:
                scan_env = json.load(fh)
        except (ValueError, OSError) as exc:
            print("ERROR: scan artifact %s could not be parsed (%s) — a malformed "
                  "artifact fails the check; it is not an empty inventory." % (scan_path, exc))
            return 1
        obs = (scan_env.get("results") or {}).get("observations")
        if not isinstance(obs, list):
            print("ERROR: scan artifact %s has no results.observations list — a malformed "
                  "artifact fails the check; it is not an empty inventory." % scan_path)
            return 1
        scan_observations = len(obs)
    try:
        ns = candidate_namespace()
    except Exception as exc:
        print("ERROR: cannot derive the candidate namespace: %s" % exc)
        return 1
    ladder = parse_ladder(text)
    objs = parse_objections(text)
    errors, warns = validate(body, ns, ladder_cns=ladder, source_text=source_text,
                             objection_idxs=objs, scan_observations=scan_observations)
    if objs is None:
        warns.append("Check 6 — no §6 inventory in the artifact; objection-ref resolution "
                     "SKIPPED (degrade, not fail).")
    for w in warns:
        print("WARN: %s" % w)
    if errors:
        print("argument-agd: FAIL (%d)" % len(errors))
        for e in errors:
            print("  - %s" % e)
        return 1
    if strict and warns:
        print("argument-agd: FAIL (--strict: %d warning(s) promoted)" % len(warns))
        return 1
    print("argument-agd: PASS (coverage manifest + %d record(s); namespace %d codes%s)"
          % (len(parse_block(body)[1]), len(ns),
             "; anchors resolved" if source_text is not None else ""))
    return 0


# --------------------------------------------------------------------------
# Hermetic self-test
# --------------------------------------------------------------------------
def _selftest():
    fails = []

    def check(name, cond):
        if not cond:
            fails.append(name)

    NS = {"WR1", "WR3", "DI0", "DI3", "BP0", "BP4", "OB1", "OB4", "OB5", "SM4", "AT0",
          "FM-A11", "FM-A16", "FM-A19"}
    SRC = ('The council should fund curb-cut ramps. Studies have shown that ramps '
           'reduce injuries — and some residents may benefit within a year. '
           'Although opponents cite cost, the budget already covers it.')

    def block(records, spans=None, completion="COMPLETE", count=None, excluded="", scan=""):
        spans = spans if spans is not None else ["Span: C0 — the thesis paragraph",
                                                 "Span: C1.warrant — the studies sentence"]
        n = count if count is not None else len(records)
        head = "\n".join(spans) + ("\n" + excluded if excluded else "")
        tail = ("\n" + scan) if scan else ""
        return "%s\nMove count: %d\nCompletion: %s%s\n\n%s" % (
            head, n, completion, tail, "\n\n".join(records))

    def rec(idx=1, fam="ASSURING", locus="the studies sentence", anchor='"Studies have shown" @ the studies sentence',
            cue="studies have shown", challenge=None, result="COLLAPSES",
            constructed="Ramps reduce injuries.", basis="no independent support remains",
            extra=(), cands="WR1 (PENDING)"):
        ch = challenge or CHALLENGE_OF[fam]
        lines = ["M%d: %s at %s" % (idx, fam, locus),
                 "  Source anchor: %s" % anchor,
                 "  Cue: %s" % cue,
                 "  Challenge: %s" % ch,
                 "  Result: %s" % result]
        if constructed is not None:
            lines.append("  Constructed challenge: %s" % constructed)
        if basis is not None:
            lines.append("  Assessment basis: %s" % basis)
        lines.extend("  %s" % e for e in extra)
        lines.append("  Candidates: %s" % cands)
        return "\n".join(lines)

    def v(body, ladder=None, source=None):
        return validate(body, NS, ladder_cns=ladder, source_text=source)

    # valid: ASSURING x COLLAPSES with a PENDING candidate
    errs, _ = v(block([rec()]))
    check("valid assuring collapses", errs == [])
    # valid: anchors resolve against source (normalized: em-dash + wrapped whitespace)
    errs, _ = v(block([rec(anchor='"ramps reduce injuries — and some" @ the studies sentence',
                           cue="NONE")]), source=SRC)
    check("anchor resolves normalized", errs == [])
    # hostile: paraphrase anchor must FAIL
    errs, _ = v(block([rec(anchor='"research demonstrates ramps cut injuries" @ x')]), source=SRC)
    check("anchor paraphrase rejected", any("does not resolve" in e for e in errs))
    # hostile: elided-words anchor must FAIL
    errs, _ = v(block([rec(anchor='"Studies have that ramps" @ x')]), source=SRC)
    check("anchor elision rejected", any("does not resolve" in e for e in errs))
    # Check 1: illegal matrix cells
    errs, _ = v(block([rec(result="SELF-SEALS")]))
    check("assuring self-seals illegal", any("Check 1" in e and "SELF-SEALS" in e for e in errs))
    errs, _ = v(block([rec(challenge="COMMITMENT")]))
    check("assuring commitment illegal", any("requires Challenge: STRIP" in e for e in errs))
    # Check 2: candidates on SURVIVES / INDETERMINATE rejected; NONE required field
    errs, _ = v(block([rec(result="SURVIVES")]))
    check("candidates on survives rejected", any("licenses only NONE" in e for e in errs))
    errs, _ = v(block([rec(result="INDETERMINATE")]))
    check("candidates on indeterminate rejected", any("licenses only NONE" in e for e in errs))
    errs, _ = v(block([rec(result="SURVIVES", cands="NONE")]))
    check("survives with NONE clean", errs == [])
    # Check 2: DISAPPEARING whitelist (pass + reject), any result
    g_extra = ("Trajectory: DISAPPEARING (the thesis paragraph → the studies sentence)",)
    errs, _ = v(block([rec(fam="GUARDING", result="SURVIVES", cue="may",
                           constructed="Residents WILL benefit within a year.",
                           extra=g_extra, cands="FM-A16 (PENDING); WR3 (PENDING)")]))
    check("disappearing whitelist passes", errs == [])
    errs, _ = v(block([rec(fam="GUARDING", result="SURVIVES", cue="may",
                           constructed="x", extra=g_extra, cands="OB5 (PENDING)")]))
    check("disappearing non-whitelist rejected", any("licenses only" in e for e in errs))
    # Check 2: NOT-CHALLENGED with a construction; run STRIP missing construction
    errs, _ = v(block([rec(result="NOT-CHALLENGED", cands="NONE")]))
    check("not-challenged w/ construction rejected", any("no construction" in e for e in errs))
    errs, _ = v(block([rec(constructed=None, cands="NONE", result="SURVIVES")]))
    check("run strip missing construction", any("requires its Constructed challenge" in e for e in errs))
    # Check 2: ENGAGEMENT must not construct
    errs, _ = v(block([rec(fam="DISCOUNTING", result="SURVIVES", cue="although",
                           constructed="x", cands="NONE",
                           extra=("Discounted: NOT-INVENTORIED",))]))
    check("engagement constructs-no-text", any("constructs no text" in e for e in errs))
    # Check 3: namespace + grammar
    errs, _ = v(block([rec(cands="AT2 (PENDING)")]))
    check("AT2 out of namespace", any("not in the derived" in e for e in errs))
    errs, _ = v(block([rec(cands="OB4 (PENDING)")]))
    check("valid-global wrong-cell candidate rejected",
          any("ASSURING × COLLAPSES" in e and "OB4" in e for e in errs))
    errs, _ = v(block([rec(cands="WR1 (CONFIRMED)")]))
    check("confirmed needs adjudicator+target", any("bad candidate entry" in e for e in errs))
    errs, _ = v(block([rec(cands="WR1 (CONFIRMED — editor, §4 C1 Codes)")]))
    check("confirmed full form clean", errs == [])
    # Check 5: manifest
    errs, _ = v(block([rec()], spans=[]))
    check("missing manifest", any("no Span: lines" in e for e in errs))
    errs, _ = v(block([rec()], completion="PARTIAL"))
    check("partial needs excluded", any("PARTIAL requires" in e for e in errs))
    errs, warns = v(block([rec()], completion="PARTIAL",
                          excluded="Excluded: C2.support — quoted-source span, out of audit scope"),
                    ladder={"C1", "C2"})
    check("valid partial warns without errors", errs == [] and any("PARTIAL" in w for w in warns))
    errs, _ = v(block([rec()], spans=["Span: C0 — the thesis paragraph"], completion="PARTIAL",
                      excluded="Excluded: C99 — unrelated"), ladder={"C1"})
    check("partial rejects unknown exclusion and omitted ladder claim",
          any("absent from the §2 ladder" in e for e in errs) and
          any("neither included nor excluded" in e for e in errs))
    errs, _ = v(block([rec()], completion="COMPLETE",
                      excluded="Excluded: C2.support — out of scope"), ladder={"C1", "C2"})
    check("complete rejects exclusions", any("COMPLETE cannot carry Excluded" in e for e in errs))
    errs, _ = v(block([rec()], count=5))
    check("move count mismatch", any("Move count 5 != 1" in e for e in errs))
    errs, _ = v(block([rec()]), ladder={"C1", "C2"})
    check("complete ladder uncovered", any("neither included nor excluded: ['C2']" in e for e in errs))
    errs, _ = v(block([rec(locus="an undeclared locus")]))
    check("record locus outside spans", any("not a declared Span locus" in e for e in errs))
    # Check 5c: the §1b scan-consumption coverage line (R3B AGD seam)
    SCAN_OK = ('Scan: consulted (2 observations; 1 inventoried, 1 declined)\n'
               '  Declined: "the studies sentence" — descriptive data report, no strippable assurance span')
    errs, _ = v(block([rec()], scan=SCAN_OK))
    check("valid consulted scan clean", errs == [])
    errs, _ = v(block([rec()], scan="Scan: not consulted (absent)"))
    check("valid not-consulted (absent) clean", errs == [])
    errs, _ = v(block([rec()], scan="Scan: not consulted (error)"))
    check("valid not-consulted (error) clean", errs == [])
    # absent Scan: line (the pre-R3B case) is valid — no scan key, no error
    errs, _ = v(block([rec()]))
    check("absent Scan: line clean (pre-R3B)", not any("scan" in e.lower() for e in errs))
    # hostile: k + m != n
    errs, _ = v(block([rec()], scan=('Scan: consulted (2 observations; 1 inventoried, 2 declined)\n'
                                     '  Declined: "x" — a\n  Declined: "y" — b')))
    check("scan k+m != n rejected", any("must equal observations" in e for e in errs))
    # hostile: m != count of Declined: lines
    errs, _ = v(block([rec()], scan="Scan: consulted (2 observations; 1 inventoried, 1 declined)"))
    check("scan m != Declined-lines rejected", any("declined count 1 != 0" in e for e in errs))
    # hostile: bad not-consulted reason value (the enum is absent|error ONLY)
    errs, _ = v(block([rec()], scan="Scan: not consulted (pre-R3B)"))
    check("scan bad reason value rejected", any("reason must be exactly" in e for e in errs))
    # hostile: malformed Declined line (no quoted span fragment)
    errs, _ = v(block([rec()], scan=('Scan: consulted (1 observations; 0 inventoried, 1 declined)\n'
                                     '  Declined: missing the quoted span and separator')))
    check("scan malformed Declined line rejected",
          any("malformed" in e and "Declined" in e for e in errs))
    # hostile: bad counts (non-integer token) => malformed Scan line
    errs, _ = v(block([rec()], scan="Scan: consulted (two observations; 1 inventoried, 1 declined)"))
    check("scan non-integer counts rejected", any("line malformed" in e for e in errs))
    # hostile: a Declined: line with no Scan: line
    errs, _ = v(block([rec()], scan='  Declined: "x" — a'))
    check("Declined without Scan rejected", any("no 'Scan:' line" in e for e in errs))
    # hostile: a not-consulted scan carrying a Declined: line
    errs, _ = v(block([rec()], scan='Scan: not consulted (error)\n  Declined: "x" — a'))
    check("not-consulted with Declined rejected",
          any("declines belong only to a consulted" in e for e in errs))
    # the artifact cross-check: n == len(results.observations) when the scan artifact is supplied
    errs, _ = validate(block([rec()], scan=SCAN_OK), NS, scan_observations=2)
    check("scan n == observations clean", errs == [])
    errs, _ = validate(block([rec()], scan=SCAN_OK), NS, scan_observations=3)
    check("scan n != artifact-observations rejected",
          any("Scan: reports 2 observations but the scan artifact carries 3" in e for e in errs))
    # hostile (Codex P1): a readable artifact was supplied but the manifest
    # DENIES consumption — 'not consulted' is reserved for an absent/malformed
    # capture, so a denied line with the artifact present skips the cross-check
    # and defeats the consumption gate. Both reason values, and the silent
    # sibling (no Scan: line at all), must fail.
    errs, _ = validate(block([rec()], scan="Scan: not consulted (error)"), NS,
                       scan_observations=2)
    check("supplied artifact + 'not consulted (error)' rejected",
          any("must be 'Scan: consulted" in e for e in errs))
    errs, _ = validate(block([rec()], scan="Scan: not consulted (absent)"), NS,
                       scan_observations=2)
    check("supplied artifact + 'not consulted (absent)' rejected",
          any("must be 'Scan: consulted" in e for e in errs))
    errs, _ = validate(block([rec()]), NS, scan_observations=2)
    check("supplied artifact + missing Scan: line rejected",
          any("carries no 'Scan:' line" in e for e in errs))
    # hostile: lookalike spellings must ERROR, not vanish as ignored lines (an
    # absent Scan: line is VALID pre-R3B, so a silently-dropped variant would
    # masquerade as that case)
    errs, _ = v(block([rec()], scan="scan: consulted (2 observations; 1 inventoried, 1 declined)"))
    check("lowercase scan: lookalike rejected", any("lookalike" in e for e in errs))
    errs, _ = v(block([rec()], scan="Scan : not consulted (absent)"))
    check("spaced 'Scan :' lookalike rejected", any("lookalike" in e for e in errs))
    errs, _ = v(block([rec()], scan=('Scan: consulted (1 observations; 1 inventoried, 0 declined)\n'
                                     '  declined: "x" — a')))
    check("lowercase declined: lookalike rejected", any("lookalike" in e for e in errs))
    # hostile: duplicate Scan: lines (first kept, second rejected)
    errs, _ = v(block([rec()], scan=('Scan: not consulted (absent)\n'
                                     'Scan: consulted (0 observations; 0 inventoried, 0 declined)')))
    check("duplicate Scan: line rejected", any("duplicate" in e for e in errs))
    # file-level fail-closed: a present-but-unreadable scan artifact FAILS the
    # check (exit 1 naming the artifact) — never degrades to a warning (the
    # n-cross-check is a blocking gate; --scan is passed exactly when a valid
    # committed artifact is expected)
    import contextlib
    import io
    import tempfile
    with tempfile.TemporaryDirectory(prefix="agd_scan_selftest_") as td:
        state_p = os.path.join(td, "argument-state.md")
        with open(state_p, "w", encoding="utf-8") as fh:
            fh.write("### 10.9 AGD Move Audit\n\nMove count: 0\nCompletion: COMPLETE\n")
        corrupt_p = os.path.join(td, "corrupt.json")
        with open(corrupt_p, "w", encoding="utf-8") as fh:
            fh.write("{not json")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = run_check(state_p, scan_path=corrupt_p)
        check("corrupt scan artifact fails closed",
              rc == 1 and "scan artifact" in buf.getvalue() and "could not be parsed" in buf.getvalue())
        null_obs_p = os.path.join(td, "null-obs.json")
        with open(null_obs_p, "w", encoding="utf-8") as fh:
            fh.write('{"results": {"observations": null}}')
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = run_check(state_p, scan_path=null_obs_p)
        check("scan artifact without observations list fails closed",
              rc == 1 and "no results.observations list" in buf.getvalue())
    # Check 6: per-family fields + cross-ref contract
    errs, _ = v(block([rec(extra=("Trajectory: STABLE",))]))
    check("trajectory on assuring rejected", any("GUARDING-only" in e for e in errs))
    errs, _ = v(block([rec(fam="GUARDING", cue="may", result="COLLAPSES",
                           constructed="x", cands="DI3 (PENDING)")]))
    check("run guarding needs trajectory", any("requires Trajectory" in e for e in errs))
    errs, _ = v(block([rec(fam="DISCOUNTING", cue="although", result="COLLAPSES-DECOY",
                           constructed=None, cands="OB5 (PENDING)",
                           extra=("Discounted: → Objection 2",))]))
    check("decoy requires displaced", any("requires Displaced strongest" in e for e in errs))
    errs, _ = v(block([rec(fam="DISCOUNTING", cue="although", result="COLLAPSES-DECOY",
                           constructed=None, cands="OB5 (PENDING)",
                           extra=("Discounted: → Objection 2", "Displaced strongest: → Objection 1"))]))
    check("decoy full form clean", errs == [])
    # Supply a real two-objection inventory directly: Objection 1 is the strongest slot.
    errs, _ = validate(block([rec(fam="DISCOUNTING", cue="although", result="COLLAPSES-DECOY",
                                  constructed=None, cands="OB5 (PENDING)",
                                  extra=("Discounted: → Objection 1",
                                         "Displaced strongest: → Objection 2"))]),
                       NS, objection_idxs={1, 2})
    check("decoy rejects non-strongest displaced ref",
          any("must reference Objection 1" in e for e in errs))
    errs, _ = v(block([rec(fam="DISCOUNTING", cue="although", result="COLLAPSES-COSTLESS",
                           constructed=None, cands="OB4 (PENDING)",
                           extra=("Discounted: NOT-INVENTORIED",))]))
    check("costless not-inventoried rejected", any("RESOLVING Discounted" in e for e in errs))
    errs, _ = v(block([rec(fam="DISCOUNTING", cue="NONE", result="SURVIVES", cands="NONE",
                           constructed=None, extra=("Discounted: NOT-INVENTORIED",))]))
    check("survives not-inventoried clean (structural discounting, cue-free)", errs == [])
    # Opus pre-PR fold arms
    errs, _ = v(block([rec(fam="DISCOUNTING", cue="NONE", result="COLLAPSES-DECOY",
                           constructed=None, cands="OB5 (PENDING)",
                           extra=("Discounted: NOT-INVENTORIED", "Displaced strongest: → Objection 1"))]))
    check("decoy not-inventoried rejected", any("self-contradictory" in e for e in errs))
    errs, _ = v(block([rec()], count=None).replace("Move count: 1", "Move count: \u00b2"))
    check("unicode move count clean error (no crash)", any("must be an integer" in e for e in errs))
    body_bad = block([rec()]).replace("M1: ASSURING at", "M1: assuring at")
    errs, _ = v(body_bad)
    check("malformed M-header clean error", any("malformed M-record header" in e for e in errs))
    errs, _ = v(block([rec(fam="GUARDING", cue="may", result="COLLAPSES", constructed="x",
                           cands="DI3 (PENDING)", extra=("Trajectory: WOBBLY",))]))
    check("trajectory enum enforced", any("Trajectory must be STABLE or DISAPPEARING" in e for e in errs))
    errs, _ = v(block([rec(fam="GUARDING", cue="may", result="INDETERMINATE", constructed="x",
                           cands="FM-A16 (PENDING)", extra=("Trajectory: DISAPPEARING banana",))]))
    check("malformed disappearing cannot license candidate",
          any("Trajectory must be" in e for e in errs) and any("licenses only" in e for e in errs))
    errs, _ = v(block([rec(fam="GUARDING", cue="may", result="INDETERMINATE", constructed="x",
                           cands="FM-A16 (PENDING)",
                           extra=("Trajectory: DISAPPEARING (unknown early → unknown late)",))]))
    check("disappearing loci must resolve to declared spans",
          any("not declared Spans" in e for e in errs))
    producer_form = """## 6. Objection and Dialectical Integrity Map\n\nOBJECTION 1: first\nOBJECTION 2: second\n\n## 7. End\n"""
    check("uppercase producer objections parsed", parse_objections(producer_form) == {1, 2})
    # §6 resolution: dangling ref rejected when inventory given; skipped when None
    errs, _ = validate(block([rec(fam="DISCOUNTING", cue="although", result="COLLAPSES-COSTLESS",
                                  constructed=None, cands="OB4 (PENDING)",
                                  extra=("Discounted: → Objection 9",))]),
                       NS, objection_idxs={1, 2})
    check("dangling objection ref rejected", any("not \u2028in the §6 inventory".replace("\u2028","") in e or "not in the §6 inventory" in e for e in errs))
    errs, _ = validate(block([rec(fam="DISCOUNTING", cue="although", result="COLLAPSES-COSTLESS",
                                  constructed=None, cands="OB4 (PENDING)",
                                  extra=("Discounted: → Objection 9",))]),
                       NS, objection_idxs=None)
    check("objection resolution degrades without §6", not any("§6 inventory" in e for e in errs))
    # namespace derivation smoke (real repo files, when present)
    try:
        ns = candidate_namespace()
        check("derived namespace = 67", len(ns) == 67)
        check("derived excludes AT2", "AT2" not in ns and "AT0" in ns and "FM-A20" in ns)
    except Exception:
        check("derived namespace available", False)

    if fails:
        print("Self-test: FAIL")
        for f in fails:
            print("  - %s" % f)
        return 1
    print("Self-test: PASS (argument-agd; matrix totality + firewall + namespace + anchors + "
          "coverage + cross-ref contract + scan-consumption line, hostile arms)")
    return 0


def main(argv):
    if "--self-test" in argv:
        return _selftest()
    if argv and argv[0] == "argument-agd":
        argv = argv[1:]
    if argv and argv[0] == "--self-test":
        return _selftest()
    if not argv:
        sys.stderr.write("Usage: argument_agd.py argument-agd <argument_state.md> "
                         "[--source <source.md>] [--scan <agd_move_scan.json>] [--strict] "
                         "| --self-test\n")
        return 2
    state = argv[0]
    source = None
    scan = None
    strict = "--strict" in argv
    if "--source" in argv:
        i = argv.index("--source")
        if i + 1 >= len(argv):
            sys.stderr.write("--source needs a path\n")
            return 2
        source = argv[i + 1]
    if "--scan" in argv:
        i = argv.index("--scan")
        if i + 1 >= len(argv):
            sys.stderr.write("--scan needs a path\n")
            return 2
        scan = argv[i + 1]
    return run_check(state, source_path=source, strict=strict, scan_path=scan)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
