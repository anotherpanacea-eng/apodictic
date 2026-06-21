#!/usr/bin/env python3
"""regression-diff — Draft-over-Draft Structural Regression Testing (cross-round Findings-Ledger diff).

Diffs the Findings Ledger across two revision rounds: did this revision resolve what it claimed,
and did it break anything that was working? Finding IDs are *unique per run* (renumbered each round),
so cross-round identity is established by a DETERMINISTIC heuristic match — every regression signal is
therefore a CANDIDATE for editor judgment, not a mechanical verdict. Prints classification + candidates
to stdout (the diff-validator precedent — timeline-diff / state-card-diff persist nothing); the
human-readable Regression Report is orchestrator-written at round-close.

Match rule (pinned, deterministic): a round-N finding matches a round-(N-1) finding iff same ORIGIN
code AND equal chapter token (apodictic_artifacts.chapter_token; chapter-less bins to 'unplaced' and
matches only 'unplaced') AND >=1 shared normalized mechanism token. Score = shared-token count.
Assignment is greedy + stable + one-to-one: prior findings in ascending-id order each take the
highest-scoring unconsumed current finding (tie -> lowest current NN, then lexical id).

Classes (all candidates): persisted, resolved-and-held, recurrence-candidate, new, new-in-quiet-chapter.

Validator (run-folder pair):
  R1 (ERROR)  round linkage — both ledgers resolve, parse, are non-empty, and are distinct rounds.
  W1 (WARN; ERROR --strict)  recurrence-candidate(s): a resolved/'revised' prior finding matched in N.
  W2 (WARN; ERROR --strict)  new-in-quiet-chapter(s): a current finding in a chapter the prior round
      left quiet (zero findings on record), unadjudicated. Override: `<!-- override: regression-cleared
      <runlabel>:<chapter> — investigated, not fix-induced -->`.
  W3 (WARN; ERROR --strict)  unexplained-drop: a prior finding with no current match and no resolution.
Only R1 (the diff's structural contract) is a hard error; the rest are advisory (re-diagnosing a
changed manuscript legitimately shifts findings) — the finding-trace / state-card-diff posture.

Usage:
  regression_diff.py regression-diff <prior_run_folder> <this_run_folder> [--strict]
  regression_diff.py regression-diff <run_folder>          # single round: nothing to diff (PASS)
  regression_diff.py --self-test
Exit: 0 clean / WARN-only, 1 ERROR (or WARN under --strict), 2 usage.
"""
import glob
import os
import re
import sys

try:
    import apodictic_artifacts as art
except ImportError:
    art = None

try:
    import finding_trace as ft
except ImportError:
    ft = None

_LEDGER_GLOB = "*_Findings_Ledger_*.md"
# Round N-1's resolution claims live in its completed-revision artifacts (state-lifecycle.md
# §Revision Round Output) and/or inline in its ledger — scan both for `<!-- resolved: F-… -->`.
_REVISION_GLOBS = ("*_Revision_Report_*.md", "*_Revision_*.md", "*_Session_Plan_*.md")

# `<!-- resolved: F-XX-NN -->` marker (fallback if finding_trace is unavailable).
_RESOLVED_RE = re.compile(r"<!--\s*resolved:(.*?)-->", re.DOTALL | re.IGNORECASE)
_ID_RE = re.compile(r"(?<![\w-])F-[A-Za-z0-9]+-[0-9]{2,}(?![\w-])")
# W2 adjudication: `<!-- override: regression-cleared <runlabel>:<chapter> — <rationale> -->`.
_CLEARED_RE = re.compile(r"<!--\s*override:\s*regression-cleared\b(.*?)-->", re.DOTALL | re.IGNORECASE)
_ID_SPLIT_RE = re.compile(r"^F-(.+)-([0-9]{2,})$")
# The classes `classify` keys by the PRIOR finding's id (vs. `new` / `new-in-quiet-chapter[ (cleared)]`,
# keyed by the CURRENT id). `crossref_classes` returns only these — the reanchor manifest carries prior ids.
_PRIOR_KEYED_CLASSES = frozenset(("persisted", "resolved-and-held", "recurrence-candidate", "unexplained-drop"))
# Mechanism tokenization: lowercase alnum tokens, drop a small fixed stopword set + tokens < 3 chars.
_STOP = frozenset((
    "the", "a", "an", "of", "to", "in", "is", "it", "so", "and", "that", "this", "for", "on", "at",
    "as", "but", "or", "its", "with", "by", "be", "are", "was", "not", "no", "into", "out", "up",
    "her", "his", "their", "they", "she", "he", "than", "then", "too", "via", "per",
))


def _read(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except (OSError, UnicodeDecodeError):
        return None


def _newest(paths):
    return max(paths, key=os.path.getmtime) if paths else None


def _origin_nn(fid):
    m = _ID_SPLIT_RE.match(fid or "")
    if not m:
        return (fid or "", 0)
    return (m.group(1), int(m.group(2)))


def _mech_tokens(mechanism):
    toks = set()
    for raw in re.split(r"[^A-Za-z0-9]+", (mechanism or "").lower()):
        if len(raw) >= 3 and raw not in _STOP:
            toks.add(raw)
    return toks


def _chapter_of(evidence_refs):
    """The finding's chapter token ('Ch N') from its first chapter-bearing ref, else 'unplaced'."""
    if art is None:
        return "unplaced"
    for ref in (evidence_refs or []):
        tok = art.chapter_token(ref)
        if tok:
            return tok
    return "unplaced"


def findings_of(ledger_text):
    """[{id, origin, nn, mechanism, severity, evidence_refs, chapter, tokens}] for the ledger's
    apodictic.finding.v1 blocks (parsed via the shared apodictic_artifacts.parse_blocks)."""
    out = []
    if not ledger_text or art is None:
        return out
    for bt, obj, _err in art.parse_blocks(ledger_text):
        if bt != "finding" or not isinstance(obj, dict) or not obj.get("id"):
            continue
        origin, nn = _origin_nn(obj["id"])
        refs = obj.get("evidence_refs") or []
        out.append({
            "id": obj["id"], "origin": origin, "nn": nn,
            "mechanism": obj.get("mechanism") or "", "severity": obj.get("severity"),
            "evidence_refs": refs, "chapter": _chapter_of(refs),
            "tokens": _mech_tokens(obj.get("mechanism")),
        })
    return out


def _resolved_ids(text):
    if ft is not None:
        return ft.resolved_cited_ids(text or "")
    ids = set()
    for body in _RESOLVED_RE.findall(text or ""):
        ids.update(_ID_RE.findall(body))
    return ids


def _cleared_chapters(text):
    """Chapter tokens cleared by `<!-- override: regression-cleared <runlabel>:<chapter> — … -->`.
    The chapter is the `Ch N` token in the `<runlabel>:<chapter>` head (before the em-dash rationale);
    chapter_token scans for it and ignores the runlabel prefix, so the canonical spaced form `Ch 3`
    parses correctly (splitting on whitespace would fragment `Ch`/`3` and match neither)."""
    chaps = set()
    if art is None:
        return chaps
    for body in _CLEARED_RE.findall(text or ""):
        head = body.split("—")[0]  # drop the rationale so a chapter named there isn't swept in
        tok = art.chapter_token(head)
        if tok:
            chaps.add(tok)
    return chaps


def match(prior, current):
    """Deterministic greedy one-to-one match. Returns {prior_id: current_finding}."""
    matched = {}
    consumed = set()
    for p in sorted(prior, key=lambda f: f["id"]):
        best = None  # (score, nn, id, finding)
        for c in current:
            if c["id"] in consumed:
                continue
            if c["origin"] != p["origin"] or c["chapter"] != p["chapter"]:
                continue
            shared = len(p["tokens"] & c["tokens"])
            if shared < 1:
                continue
            cand = (shared, -c["nn"], c["id"])  # high score, then low nn, then lexical id
            if best is None or cand[:2] > best[0][:2] or (cand[:2] == best[0][:2] and cand[2] < best[0][2]):
                best = (cand, c)
        if best is not None:
            matched[p["id"]] = best[1]
            consumed.add(best[1]["id"])
    return matched


def classify(prior, current, prior_resolved, cleared_chaps):
    """-> (rows, recurrence[], quiet[], drops[]). rows: (chapter, id, klass, basis, severity)."""
    matched = match(prior, current)
    pri_by_id = {p["id"]: p for p in prior}
    prior_chapters = set(p["chapter"] for p in prior if p["chapter"] != "unplaced")
    matched_current_ids = set(c["id"] for c in matched.values())

    rows, recurrence, quiet, drops = [], [], [], []

    for p in sorted(prior, key=lambda f: (f["chapter"], f["id"])):
        c = matched.get(p["id"])
        if c is not None:
            shared = sorted(p["tokens"] & c["tokens"])
            basis = "origin=%s chapter=%s shared=[%s]" % (p["origin"], p["chapter"], ",".join(shared))
            if p["id"] in prior_resolved:
                rows.append((p["chapter"], p["id"], "recurrence-candidate", basis, p["severity"]))
                recurrence.append((p, c, p["severity"], basis))
            else:
                rows.append((p["chapter"], p["id"], "persisted", basis, p["severity"]))
        else:
            if p["id"] in prior_resolved:
                rows.append((p["chapter"], p["id"], "resolved-and-held", "no current match", p["severity"]))
            else:
                rows.append((p["chapter"], p["id"], "unexplained-drop", "no current match", p["severity"]))
                drops.append(p)

    for c in sorted(current, key=lambda f: (f["chapter"], f["id"])):
        if c["id"] in matched_current_ids:
            continue
        if c["chapter"] != "unplaced" and c["chapter"] not in prior_chapters:
            if c["chapter"] in cleared_chaps:
                rows.append((c["chapter"], c["id"], "new-in-quiet-chapter (cleared)", "override", c["severity"]))
            else:
                rows.append((c["chapter"], c["id"], "new-in-quiet-chapter", "quiet on prior record", c["severity"]))
                quiet.append(c)
        else:
            rows.append((c["chapter"], c["id"], "new", "", c["severity"]))

    return rows, recurrence, quiet, drops


def diff_rounds(prior_text, current_text, prior_resolved, cleared_chaps, strict=False):
    lines, errs, warns = [], [], []
    prior = findings_of(prior_text)
    current = findings_of(current_text)

    # R1 — round linkage (the one mechanical invariant).
    if not prior:
        errs.append("R1 round linkage: prior round has no parseable findings")
    if not current:
        errs.append("R1 round linkage: current round has no parseable findings")
    if errs:
        return _finish(["regression-diff: cross-round diff"], errs, warns, strict, "")

    rows, recurrence, quiet, drops = classify(prior, current, prior_resolved, cleared_chaps)

    lines.append("regression-diff: %d prior finding(s) -> %d current finding(s)"
                 % (len(prior), len(current)))
    for chapter, fid, klass, basis, sev in rows:
        lines.append("  regression-diff:%s %s [%s%s]%s"
                     % (klass, fid, chapter, "" if sev is None else " %s" % sev,
                        " — %s" % basis if basis else ""))

    for p, c, sev, basis in recurrence:
        warns.append("W1 recurrence-candidate: prior %s (%s) matched by current %s — reverts to %s; %s"
                     % (p["id"], sev, c["id"], sev, basis))
    for c in quiet:
        warns.append("W2 quiet-chapter breakage candidate: current %s in %s (quiet on prior record) — "
                     "adjudicate or `<!-- override: regression-cleared %s — investigated -->`"
                     % (c["id"], c["chapter"], c["chapter"]))
    for p in drops:
        warns.append("W3 unexplained-drop candidate: prior %s (%s) has no current match and no resolution marker"
                     % (p["id"], p["severity"]))

    return _finish(lines, errs, warns, strict,
                   "%d persisted/new, no regression candidates" % len(rows))


def _finish(lines, errs, warns, strict, ok_msg):
    for e in errs:
        lines.append("  ERROR: %s" % e)
    for w in warns:
        lines.append("  %s: %s" % ("ERROR (--strict)" if strict else "WARN", w))
    if errs or (strict and warns):
        lines.append("regression-diff: FAIL (%d error(s)%s)"
                     % (len(errs), ", %d strict warn(s)" % len(warns) if (strict and warns) else ""))
        return 1, lines
    if warns:
        lines.append("WARN: regression-diff: %d regression candidate(s) — see W1-W3 above" % len(warns))
    else:
        lines.append("regression-diff: PASS (%s)" % ok_msg)
    return 0, lines


def _ledger_path(p):
    """A dir -> its newest ledger; a file -> itself."""
    if os.path.isdir(p):
        return _newest(glob.glob(os.path.join(p, _LEDGER_GLOB)))
    return p if os.path.isfile(p) else None


def _resolved_and_cleared(folder_or_file, want_resolved):
    """(resolved_ids, cleared_chapters) gathered from a round's artifacts. A dir scans its ledger AND
    revision artifacts (so a `<!-- resolved -->` / `regression-cleared` marker is found whether it lives
    inline in the ledger or in the Revision Report); resolved_ids computed only when want_resolved."""
    texts = []
    if os.path.isdir(folder_or_file):
        paths = list(glob.glob(os.path.join(folder_or_file, _LEDGER_GLOB)))
        for g in _REVISION_GLOBS:
            paths += glob.glob(os.path.join(folder_or_file, g))
        for p in paths:
            t = _read(p)
            if t:
                texts.append(t)
    else:
        t = _read(folder_or_file)
        if t:
            texts.append(t)
    joined = "\n".join(texts)
    return (_resolved_ids(joined) if want_resolved else set()), _cleared_chapters(joined)


def resolve(paths):
    """-> (prior, current) folder/file paths. A lone arg is single-round (no prior)."""
    if len(paths) >= 2:
        return paths[0], paths[1]
    if len(paths) == 1:
        return None, paths[0]
    return None, None


def run(paths, strict=False):
    prior, current = resolve(paths)
    if not current:
        return 2, ["regression-diff: usage: regression-diff <prior_run_folder> <this_run_folder>"]
    cur_ledger = _ledger_path(current)
    if not cur_ledger:
        return 2, ["regression-diff: no %s in %s" % (_LEDGER_GLOB, current)]
    if prior is None:
        # Single round: nothing to diff. Confirm the ledger parses, then PASS.
        n = len(findings_of(_read(cur_ledger) or ""))
        return 0, ["regression-diff: single round (%d finding(s)); no prior round to diff — PASS" % n]
    pri_ledger = _ledger_path(prior)
    if not pri_ledger:
        return 2, ["regression-diff: no %s in %s" % (_LEDGER_GLOB, prior)]
    if os.path.abspath(pri_ledger) == os.path.abspath(cur_ledger):
        return 1, ["regression-diff: cross-round diff", "  ERROR: R1 round linkage: prior and current "
                   "are the same round (%s)" % os.path.basename(cur_ledger),
                   "regression-diff: FAIL (1 error(s))"]
    prior_resolved, _ = _resolved_and_cleared(prior, want_resolved=True)
    _, cleared = _resolved_and_cleared(current, want_resolved=False)
    return diff_rounds(_read(pri_ledger), _read(cur_ledger), prior_resolved, cleared, strict=strict)


def crossref_classes(prior, current):
    """{prior_finding_id: class} for the PRIOR-round-keyed regression classes (persisted, resolved-and-held,
    recurrence-candidate, unexplained-drop) — the map `reanchor crossref` joins against by finding_id (the
    re-anchored manifest carries the prior round's ids). Current-only classes (new / new-in-quiet-chapter)
    have no prior id to join on and are omitted. Best-effort: returns {} when a ledger is missing/unparseable
    (the join simply finds no matches — it never raises), so it's safe to call from the orchestrator glue."""
    if prior is None or current is None:
        return {}
    pri_ledger, cur_ledger = _ledger_path(prior), _ledger_path(current)
    if not pri_ledger or not cur_ledger:
        return {}
    prior_findings = findings_of(_read(pri_ledger))
    if not prior_findings:
        return {}
    prior_resolved, _ = _resolved_and_cleared(prior, want_resolved=True)
    _, cleared = _resolved_and_cleared(current, want_resolved=False)
    rows, _rec, _quiet, _drops = classify(prior_findings, findings_of(_read(cur_ledger)),
                                          prior_resolved, cleared)
    # Keep only the PRIOR-keyed rows (their `id` is the prior finding's id — the join key). Filter by the
    # known prior-keyed class set, NOT by id membership: per-run renumbering means a current-only `new`
    # finding can share an id string with a prior finding (both rounds start at `-01`), and `classify`
    # emits the `new` row AFTER the prior rows — an id-membership filter would let that collision overwrite
    # the prior class. The class set is collision-proof and order-independent.
    out = {}
    for _chapter, fid, klass, _basis, _sev in rows:
        if klass in _PRIOR_KEYED_CLASSES:
            out[fid] = klass
    return out


# ---------------------------------------------------------------- self-test

def run_self_test():
    import json as _j
    import tempfile
    import shutil
    rc = {"v": 0}

    def chk(name, cond):
        print("  %s: %s" % (name, "OK" if cond else "FAIL"))
        if not cond:
            rc["v"] = 1

    def finding(fid, mech, refs, sev="Should-Fix"):
        return '<!-- apodictic:finding\n%s\n-->' % _j.dumps(
            {"schema": "apodictic.finding.v1", "id": fid, "mechanism": mech, "severity": sev,
             "confidence": "HIGH", "evidence_refs": list(refs), "fix_class": "x", "risk_if_fixed": "y"})

    def ledger(*blocks):
        return "# Ledger\n" + "\n".join(blocks) + "\n"

    # round 1: a flat-affect beat in Ch 7 (Must-Fix), a pacing seam in Ch 9.
    r1 = ledger(
        finding("F-P5-01", "the want never forces a sacrifice so stakes stay abstract", ["Ch 7"], "Must-Fix"),
        finding("F-RR-01", "three days collapse into one paragraph, a continuity seam", ["Ch 9"], "Should-Fix"),
    )
    # round 2: F-P5 recurs (renumbered, same origin/chapter, shared mechanism tokens); a NEW finding in
    # Ch 3 which round 1 left quiet; the Ch 9 seam is gone (matched -> not present -> drop/held).
    r2 = ledger(
        finding("F-P5-01", "the want still never forces a sacrifice; stakes remain abstract", ["Ch 7"], "Must-Fix"),
        finding("F-P5-02", "a new voice-drift sentence breaks POV discipline", ["Ch 3"], "Should-Fix"),
    )

    f1 = findings_of(r1)
    chk("findings_parsed", len(f1) == 2 and f1[0]["origin"] == "P5" and f1[0]["chapter"] == "Ch 7")
    chk("mech_tokens_drop_stopwords", "want" in f1[0]["tokens"] and "the" not in f1[0]["tokens"])

    # matcher: F-P5-01(r1) <-> F-P5-01(r2) by origin+chapter+shared tokens; F-RR-01 has no r2 match.
    m = match(f1, findings_of(r2))
    chk("match_one_to_one", m.get("F-P5-01", {}).get("id") == "F-P5-01" and "F-RR-01" not in m)

    # classify without resolution: F-P5 persisted, F-RR-01 unexplained-drop, F-P5-02 new-in-quiet-chapter.
    rows, rec, quiet, drops = classify(f1, findings_of(r2), set(), set())
    klass = {fid: k for (_ch, fid, k, _b, _s) in rows}
    chk("persisted", klass.get("F-P5-01") == "persisted")
    chk("unexplained_drop", klass.get("F-RR-01") == "unexplained-drop" and len(drops) == 1)
    chk("new_in_quiet_chapter", klass.get("F-P5-02") == "new-in-quiet-chapter" and len(quiet) == 1)
    chk("no_recurrence_without_resolution", not rec)

    # classify WITH F-P5-01 marked resolved in round 1 -> recurrence-candidate (the regression).
    rows2, rec2, _q2, _d2 = classify(f1, findings_of(r2), {"F-P5-01"}, set())
    klass2 = {fid: k for (_ch, fid, k, _b, _s) in rows2}
    chk("recurrence_candidate", klass2.get("F-P5-01") == "recurrence-candidate" and len(rec2) == 1)
    chk("recurrence_reverts_severity", rec2[0][2] == "Must-Fix")

    # a resolved finding with NO current match is resolved-and-held (the win).
    rows3, _r3, _q3, _d3 = classify(f1, findings_of(r2), {"F-RR-01"}, set())
    klass3 = {fid: k for (_ch, fid, k, _b, _s) in rows3}
    chk("resolved_and_held", klass3.get("F-RR-01") == "resolved-and-held")

    # diff_rounds: W1 (recurrence) + W2 (quiet chapter) advisory by default, ERROR under --strict.
    code, lines = diff_rounds(r1, r2, {"F-P5-01"}, set())
    chk("default_advisory", code == 0 and any("W1 recurrence" in x for x in lines)
        and any("W2 quiet-chapter" in x for x in lines))
    chk("strict_fails", diff_rounds(r1, r2, {"F-P5-01"}, set(), strict=True)[0] == 1)

    # determinism: identical inputs -> identical output lines.
    chk("deterministic", diff_rounds(r1, r2, {"F-P5-01"}, set())[1] == diff_rounds(r1, r2, {"F-P5-01"}, set())[1])

    # W2 override clears the quiet-chapter candidate.
    code, lines = diff_rounds(r1, r2, set(), {"Ch 3"})
    chk("w2_override_clears", code == 0 and not any("W2 quiet-chapter breakage" in x for x in lines)
        and any("new-in-quiet-chapter (cleared)" in x for x in lines))

    # _cleared_chapters parses the CANONICAL spaced override form end-to-end (regression: a per-token
    # whitespace split would fragment `Ch 3` and clear nothing).
    chk("cleared_canonical_spaced",
        _cleared_chapters("<!-- override: regression-cleared 2026-02-01_m:Ch 3 — investigated, not fix-induced -->")
        == {"Ch 3"})
    chk("cleared_runlabel_not_swept", "Ch 3" in
        _cleared_chapters("<!-- override: regression-cleared codex54:Ch 3 -->"))
    chk("cleared_none_when_absent", _cleared_chapters("no override markers here") == set())
    # the real marker, driven through _cleared_chapters into diff_rounds, clears W2.
    _ov = "<!-- override: regression-cleared 2026-02-01_m:Ch 3 — investigated -->"
    code, lines = diff_rounds(r1, r2, set(), _cleared_chapters(_ov))
    chk("w2_canonical_override_end_to_end",
        code == 0 and not any("W2 quiet-chapter breakage" in x for x in lines))

    # unplaced findings never classify as new-in-quiet-chapter.
    r2u = ledger(finding("F-P8-01", "a reveal lands flat with no felt beat", []))
    rows_u, _ru, quiet_u, _du = classify(f1, findings_of(r2u), set(), set())
    klass_u = {fid: k for (_ch, fid, k, _b, _s) in rows_u}
    chk("unplaced_is_new_not_quiet", klass_u.get("F-P8-01") == "new" and not quiet_u)

    # R1: a round with no parseable findings is a hard error.
    chk("r1_empty_prior_errors", diff_rounds("# empty\n", r2, set(), set())[0] == 1)

    # run(): folder pair, single-round, same-round.
    d = tempfile.mkdtemp()
    try:
        d1, d2 = os.path.join(d, "r1"), os.path.join(d, "r2")
        os.makedirs(d1)
        os.makedirs(d2)
        with open(os.path.join(d1, "P_Findings_Ledger_2026-01-01_m.md"), "w", encoding="utf-8", newline="") as fh:
            fh.write(r1)
        with open(os.path.join(d1, "P_Revision_Report_2026-01-02_m.md"), "w", encoding="utf-8", newline="") as fh:
            fh.write("# Revision Report\n<!-- resolved: F-P5-01 -->\n")
        with open(os.path.join(d2, "P_Findings_Ledger_2026-02-01_m.md"), "w", encoding="utf-8", newline="") as fh:
            fh.write(r2)
        # prior resolved F-P5-01 -> recurrence -> WARN (exit 0), ERROR under --strict.
        chk("run_pair_advisory", run([d1, d2])[0] == 0)
        chk("run_pair_strict_fails", run([d1, d2], strict=True)[0] == 1)
        chk("run_single_round_pass", run([d2])[0] == 0)
        chk("run_same_round_r1_fails", run([d2, d2])[0] == 1)
        chk("run_missing_ledger_usage", run([os.path.join(d, "nope"), d2])[0] == 2)
        # current-round override in a REVISION REPORT (not the ledger) is read and clears W2.
        d3 = os.path.join(d, "r3")
        os.makedirs(d3)
        with open(os.path.join(d3, "P_Findings_Ledger_2026-03-01_m.md"), "w", encoding="utf-8", newline="") as fh:
            fh.write(r2)
        with open(os.path.join(d3, "P_Revision_Report_2026-03-02_m.md"), "w", encoding="utf-8", newline="") as fh:
            fh.write("# Revision Report\n<!-- override: regression-cleared 2026-03-01_m:Ch 3 — investigated -->\n")
        _c3, l3 = run([d1, d3])
        chk("run_override_in_revision_report_clears_w2",
            not any("W2 quiet-chapter breakage" in x for x in l3)
            and any("new-in-quiet-chapter (cleared)" in x for x in l3))

        # crossref_classes: the prior-keyed class map the reanchor crossref glue joins against by id.
        # In d1->d2: F-P5-01 was resolved in d1 and recurs in d2 (recurrence-candidate); F-RR-01 has no
        # d2 match and no resolution (unexplained-drop). New/current-only classes carry no prior id and
        # are omitted; a missing-ledger folder yields {} (best-effort, never raises).
        cc = crossref_classes(d1, d2)
        chk("crossref_classes_recurrence", cc.get("F-P5-01") == "recurrence-candidate")
        chk("crossref_classes_drop", cc.get("F-RR-01") == "unexplained-drop")
        chk("crossref_classes_no_current_only", "F-P5-02" not in cc)
        chk("crossref_classes_missing_safe", crossref_classes(os.path.join(d, "nope"), d2) == {})

        # id-collision guard: per-run renumbering can make a current-only `new` finding SHARE an id with a
        # prior finding. The prior-keyed class must win (it's the join key the reanchor manifest carries) —
        # a class-set filter is collision-proof where an id-membership filter would let the later `new` row
        # overwrite it. Here d1's F-RR-01 (Ch 9, unexplained-drop) and a NEW Ch 2 finding both id'd F-RR-01.
        dcol = os.path.join(d, "rcol")
        os.makedirs(dcol)
        with open(os.path.join(dcol, "P_Findings_Ledger_2026-04-01_m.md"), "w",
                  encoding="utf-8", newline="") as fh:
            # a recurrence of F-P5 (Ch 7) + a NEW finding in Ch 2 that reuses the id string F-RR-01.
            fh.write(ledger(
                finding("F-P5-01", "the want still never forces a sacrifice; stakes remain abstract",
                        ["Ch 7"], "Must-Fix"),
                finding("F-RR-01", "a brand-new continuity wobble unrelated to the prior seam", ["Ch 2"])))
        ccol = crossref_classes(d1, dcol)
        # prior F-RR-01 (Ch 9) had no Ch-2 match -> unexplained-drop; the class set keeps THAT, not the
        # current-only `new` Ch-2 row that happens to reuse the id.
        chk("crossref_classes_id_collision_prior_wins", ccol.get("F-RR-01") == "unexplained-drop")
    finally:
        shutil.rmtree(d, ignore_errors=True)

    print("Self-test: %s" % ("PASS" if rc["v"] == 0 else "FAIL"))
    return rc["v"]


def main(argv):
    if "--self-test" in argv:
        return run_self_test()
    args = [a for a in argv[1:] if a != "regression-diff"]
    strict = "--strict" in args
    paths = [a for a in args if not a.startswith("--")]
    if not paths:
        print("Usage: regression_diff.py regression-diff <prior_run_folder> <this_run_folder> [--strict] "
              "| <run_folder> | --self-test")
        return 2
    code, lines = run(paths, strict=strict)
    for ln in lines:
        print(ln)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
