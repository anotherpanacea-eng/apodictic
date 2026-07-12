#!/usr/bin/env python3
"""argument-agd — the AGD Move Audit validator (R3A).

Validates an `Argument_State.md` §10.9 "AGD Move Audit" block (the companion audit defined in
plugins/apodictic/skills/specialized-audits/references/craft/argument-agd-audit.md): the coverage
manifest, the typed M-records, the total family×challenge×result matrix, the neutrality firewall
(candidates licensed ONLY by failed function), the candidate namespace + reconciliation grammar,
the DISCOUNTING cross-ref contract, and — when a source text is supplied — Source-anchor
resolution via NORMALIZED substring matching (greenfield: whitespace runs folded, quote chars and
dashes normalized, otherwise case-sensitive; near-misses like paraphrase or elision must FAIL).

Structural parse throughout (heading walk + line grammar) — no doc-wide regex scope. The candidate
namespace is DERIVED, never hardcoded: the Dialectical Clarity codes come from argument_crosswalk's
scoped table-walk of dialectical-clarity.md, minus the AT1-AT4 type labels (classifications, not
diagnoses; AT0 stays), plus FM-A1..FM-A20 from argument_groundtruth._FM_A_MAX = 62 codes.

Usage:
  argument_agd.py --self-test
  argument_agd.py argument-agd <argument_state.md> [--source <source.md>] [--strict]
"""
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
COMPLETIONS = {"COMPLETE", "PARTIAL"}
STATUSES = ("PENDING", "CONFIRMED", "DECLINED")

_M_HEADER_RE = re.compile(r"^M(\d+):\s+([A-Z-]+)\s+at\s+(.+?)\s*$")
_SPAN_TOKEN_RE = re.compile(r"^(C\d+(\.(warrant|support))?|C0)$")
_OBJ_REF_RE = re.compile(r"^→\s*Objection\s+\d+$")
_CAND_RE = re.compile(r"^([A-Z][A-Z0-9-]*)\s+\((PENDING|CONFIRMED\s+—\s+[^,]+,\s+[^)]+|"
                      r"DECLINED\s+—\s+[^)]+)\)$")


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
    ns = (set(dc) - {"AT1", "AT2", "AT3", "AT4"}) | {"FM-A%d" % i for i in range(1, _FM_A_MAX + 1)}
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
    """Objection indices from '## 6. Objection and Dialectical Integrity Map' ('Objection N:'
    lines). None if no §6 section (degrade-not-fail, the parse_ladder convention)."""
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
            m = re.match(r"^Objection\s+(\d+)\s*:", s)
            if m:
                idxs.add(int(m.group(1)))
    return idxs if found else None


def parse_block(body):
    """(manifest, records, parse_errs). Manifest = dict; records = list of dicts (ordered fields)."""
    manifest = {"spans": [], "excluded": [], "move_count": None, "completion": None}
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
    return manifest, records, errs


# --------------------------------------------------------------------------
# Core validation (pure over inputs)
# --------------------------------------------------------------------------
def validate(body, namespace, ladder_cns=None, source_text=None, objection_idxs=None):
    """Returns (errors, warns)."""
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
    span_loci = {l for _, l in manifest["spans"]}
    for tok in span_tokens:
        if not _SPAN_TOKEN_RE.match(tok):
            errors.append("Check 5 (coverage) — bad span token %r (C0 | Cn[.warrant|.support])." % tok)
    if isinstance(manifest["move_count"], int):
        if manifest["move_count"] != len(records):
            errors.append("Check 5 (coverage) — Move count %d != %d records present."
                          % (manifest["move_count"], len(records)))
    else:
        errors.append("Check 5 (coverage) — Move count must be an integer (got %r)." % manifest["move_count"])
    if completion == "COMPLETE" and ladder_cns is not None:
        covered = {t.split(".", 1)[0] for t in span_tokens}
        missing = sorted(cn for cn in ladder_cns if cn not in covered)
        if "C0" not in covered:
            errors.append("Check 5 (coverage) — COMPLETE but C0 is not a declared span.")
        if missing:
            errors.append("Check 5 (coverage) — COMPLETE but ladder subclaims uncovered: %s." % missing)
    elif ladder_cns is None:
        warns.append("Check 5 (coverage) — no §2 Claim Architecture in the artifact; "
                     "ladder cross-check SKIPPED (degrade, not fail).")

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
        disappearing = bool(trajectory and trajectory.startswith("DISAPPEARING"))
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
        if result in {"SURVIVES", "NOT-CHALLENGED", "INDETERMINATE"} and cand_entries:
            if disappearing and fam == "GUARDING":
                bad = [c for c in cand_entries if c not in DISAPPEARING_WHITELIST]
                if bad:
                    errors.append("%s (Check 2) — DISAPPEARING whitelist is exactly %s; %s not licensed."
                                  % (rid, sorted(DISAPPEARING_WHITELIST), bad))
            else:
                errors.append("%s (Check 2) — Result %s licenses NO candidates (got %s); "
                              "Candidates: NONE required." % (rid, result, cand_entries))
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
                errors.append("%s (Check 3) — candidate %r not in the derived 62-code namespace "
                              "(DC minus AT1-AT4, plus FM-A1-20)." % (rid, c))

        # ---- Check 6: per-family fields + the DISCOUNTING cross-ref contract ----
        if trajectory and not (trajectory == "STABLE" or trajectory.startswith("DISAPPEARING")):
            errors.append("%s (Check 6) — Trajectory must be STABLE or DISAPPEARING (early locus → "
                          "late locus); got %r." % (rid, trajectory))
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
def run_check(state_path, source_path=None, strict=False):
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
    try:
        ns = candidate_namespace()
    except Exception as exc:
        print("ERROR: cannot derive the candidate namespace: %s" % exc)
        return 1
    ladder = parse_ladder(text)
    objs = parse_objections(text)
    errors, warns = validate(body, ns, ladder_cns=ladder, source_text=source_text,
                             objection_idxs=objs)
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

    def block(records, spans=None, completion="COMPLETE", count=None, excluded=""):
        spans = spans if spans is not None else ["Span: C0 — the thesis paragraph",
                                                 "Span: C1.warrant — the studies sentence"]
        n = count if count is not None else len(records)
        head = "\n".join(spans) + ("\n" + excluded if excluded else "")
        return "%s\nMove count: %d\nCompletion: %s\n\n%s" % (head, n, completion, "\n\n".join(records))

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
    check("candidates on survives rejected", any("licenses NO candidates" in e for e in errs))
    errs, _ = v(block([rec(result="INDETERMINATE")]))
    check("candidates on indeterminate rejected", any("licenses NO candidates" in e for e in errs))
    errs, _ = v(block([rec(result="SURVIVES", cands="NONE")]))
    check("survives with NONE clean", errs == [])
    # Check 2: DISAPPEARING whitelist (pass + reject), any result
    g_extra = ("Trajectory: DISAPPEARING (para 2 → para 9)",)
    errs, _ = v(block([rec(fam="GUARDING", result="SURVIVES", cue="may",
                           constructed="Residents WILL benefit within a year.",
                           extra=g_extra, cands="FM-A16 (PENDING); WR3 (PENDING)")]))
    check("disappearing whitelist passes", errs == [])
    errs, _ = v(block([rec(fam="GUARDING", result="SURVIVES", cue="may",
                           constructed="x", extra=g_extra, cands="OB5 (PENDING)")]))
    check("disappearing non-whitelist rejected", any("whitelist is exactly" in e for e in errs))
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
    errs, _ = v(block([rec(cands="WR1 (CONFIRMED)")]))
    check("confirmed needs adjudicator+target", any("bad candidate entry" in e for e in errs))
    errs, _ = v(block([rec(cands="WR1 (CONFIRMED — editor, §4 C1 Codes)")]))
    check("confirmed full form clean", errs == [])
    # Check 5: manifest
    errs, _ = v(block([rec()], spans=[]))
    check("missing manifest", any("no Span: lines" in e for e in errs))
    errs, _ = v(block([rec()], completion="PARTIAL"))
    check("partial needs excluded", any("PARTIAL requires" in e for e in errs))
    _, warns = v(block([rec()], completion="PARTIAL",
                       excluded="Excluded: C2.support — quoted-source span, out of audit scope"))
    check("partial warns", any("PARTIAL" in w for w in warns))
    errs, _ = v(block([rec()], count=5))
    check("move count mismatch", any("Move count 5 != 1" in e for e in errs))
    errs, _ = v(block([rec()]), ladder={"C1", "C2"})
    check("complete ladder uncovered", any("uncovered: ['C2']" in e for e in errs))
    errs, _ = v(block([rec(locus="an undeclared locus")]))
    check("record locus outside spans", any("not a declared Span locus" in e for e in errs))
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
        check("derived namespace = 62", len(ns) == 62)
        check("derived excludes AT2", "AT2" not in ns and "AT0" in ns and "FM-A20" in ns)
    except Exception:
        check("derived namespace available", False)

    if fails:
        print("Self-test: FAIL")
        for f in fails:
            print("  - %s" % f)
        return 1
    print("Self-test: PASS (argument-agd; matrix totality + firewall + namespace + anchors + "
          "coverage + cross-ref contract, hostile arms)")
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
                         "[--source <source.md>] [--strict] | --self-test\n")
        return 2
    state = argv[0]
    source = None
    strict = "--strict" in argv
    if "--source" in argv:
        i = argv.index("--source")
        if i + 1 >= len(argv):
            sys.stderr.write("--source needs a path\n")
            return 2
        source = argv[i + 1]
    return run_check(state, source_path=source, strict=strict)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
