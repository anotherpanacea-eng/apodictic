#!/usr/bin/env python3
"""reader-instrument — structural integrity for the Beta-Reader Instrument (Workflows track).

`validate.sh reader-instrument <run_folder> [--strict]` (or explicit files) shells out here.
The upstream complement to feedback-triage: it turns the diagnosis's own OPEN UNCERTAINTIES into a
targeted reader questionnaire, so the feedback that comes back is worth triaging. Each question is a
structured `apodictic.reader_question.v1` block in a Beta-Reader Instrument artifact, sourced from a
LOW/UNCERTAIN finding, an Unresolved-Questions bullet, or a finding's tradeoff (`risk_if_fixed`).
This validator owns the question-contract: schema hygiene, provenance integrity (where stable IDs
exist), the non-leading/content-neutral firewall scan, and the anti-relitigation severity gate.

  B1 invalid item        a reader_question block fails its schema (bad enum / id / missing field / JSON).
  B2 duplicate id        two questions share an RQ-NN id (ids must be unique per instrument).
  B3 provenance integrity provenance matches source_kind: low-confidence-finding/tradeoff carry a
                          `targets` that resolves to a real finding id in the Ledger and no source_note
                          dependency; unresolved-question carries a non-empty `source_note` and no targets.
                          Two advisories (WARN; ERROR under --strict): a low-confidence-finding probe
                          pointed at a non-LOW/UNCERTAIN finding (kind label disagrees with the Ledger —
                          tradeoff is exempt, it rides any finding); an unresolved-question whose
                          `source_note` matches no `### Unresolved Questions` bullet (fabricated provenance).
  B4 leading / invented   the question matches a leading construction (finite blocklist) OR introduces a
                          quoted/multi-word-capitalized phrase absent from the target finding's text
                          (coarse content-neutrality heuristic). Advisory; ERROR under --strict.
                          Override `<!-- override: leading-question RQ-NN — <rationale> -->`.
  B5 relitigating locked  a `targets` finding is LOCKED — severity in {Must-Fix, Should-Fix} AND
                          confidence in {HIGH, MEDIUM}. Testing a locked verdict by reader poll softens
                          by survey. Advisory; ERROR under --strict.
                          Override `<!-- override: how-to-fix RQ-NN — testing fix approach, not the verdict -->`.
  W1 coverage             a LOW/UNCERTAIN finding or an Unresolved-Questions bullet has no reader
                          question — a genuine uncertainty left untested (advisory; ERROR under --strict).

The instrument file (reader_question blocks) is read together with the Findings Ledger it targets
(finding blocks + the `### Unresolved Questions` section). Each is optional; an empty/absent
instrument is a no-op (no false failure). Reuses apodictic_artifacts (one block grammar + the schema
engine); the ledger index mirrors finding_trace.ledger_inventory but also keeps confidence for B5.
See docs/beta-reader-instrument.md.

  reader_instrument.py reader-instrument <run_folder|files...> [--strict]
  reader_instrument.py --self-test

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

_SCHEMA_ID = "apodictic.reader_question.v1"
_FINDING_SCHEMA_ID = "apodictic.finding.v1"
_INSTRUMENT_GLOB = "*_Beta_Reader_Instrument_*.md"
_LEDGER_GLOB = "*_Findings_Ledger_*.md"

_FROM_FINDING = ("low-confidence-finding", "tradeoff")  # source_kinds that require `targets`
_OPEN_CONFIDENCE = ("LOW", "UNCERTAIN")                  # freely testable
_LOCKED_SEVERITY = ("Must-Fix", "Should-Fix")
_LOCKED_CONFIDENCE = ("HIGH", "MEDIUM")

# B4 — finite blocklist of leading interrogative constructions (case-insensitive substring).
# Sound, like tone-check's superlative blocklist. Topic words ("confused", "drag") are intentionally
# NOT listed: "where did you feel confused?" is a legitimate comprehension probe, not a leading one.
_LEADING = (
    "don't you think", "do you agree", "don't you agree", "wouldn't it be",
    "wouldn't you", "isn't it", "isn't the", "didn't you", "did you like how",
    "wasn't it", "shouldn't the", "would it be better", "better if",
)
# Coarse content-neutrality: quoted spans and runs of 2+ capitalized words (proper-noun-like).
_QUOTED_RE = re.compile(r'"([^"]{2,})"|“([^”]{2,})”')
_CAPRUN_RE = re.compile(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b")


def _read(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return None


def parse_questions(text):
    """[(obj_or_None, schema_errs, index), ...] for each apodictic:reader_question block."""
    items = []
    if not text or art is None:
        return items
    schema = art.load_schema(_SCHEMA_ID)
    idx = 0
    for btype, obj, jerr in art.parse_blocks(text):
        if btype != "reader_question":
            continue
        idx += 1
        where = "reader_question #%d" % idx
        if jerr:
            items.append((None, ["%s: invalid JSON — %s" % (where, jerr)], idx))
            continue
        errs = art.validate_obj(obj, schema, where)
        items.append((obj, errs, idx))
    return items


def ledger_index(ledger_text):
    """{finding_id: obj} for the ledger's apodictic.finding.v1 blocks (the authoritative ID set).

    Mirrors finding_trace.ledger_inventory but keeps the whole finding object so B4 can read the
    finding's text (content-neutrality) and B5 can read severity + confidence (the lock check)."""
    out = {}
    if not ledger_text or art is None:
        return out
    for bt, obj, _err in art.parse_blocks(ledger_text):
        if bt == "finding" and isinstance(obj, dict) and obj.get("id"):
            out[obj["id"]] = obj
    return out


def open_finding_ids(index):
    """Finding ids whose confidence is LOW/UNCERTAIN — the freely-testable uncertainty set (W1)."""
    return {fid for fid, obj in index.items() if obj.get("confidence") in _OPEN_CONFIDENCE}


def unresolved_questions(ledger_text):
    """The `### Unresolved Questions` bullets (verbatim), minus the 'none' placeholder."""
    if not ledger_text:
        return []
    out, in_section = [], False
    for raw in ledger_text.splitlines():
        line = raw.strip()
        if line.startswith("### "):
            in_section = line[4:].strip().lower().startswith("unresolved questions")
            continue
        if in_section and line.startswith("- "):
            body = line[2:].strip()
            if body and body.lower() not in ("none", "[question.]", "n/a"):
                out.append(body)
    return out


def _sig_words(s):
    """Significant content words (lowercased, len>4) for the fuzzy UQ-coverage match (W1)."""
    return {w for w in re.findall(r"[a-z']{5,}", (s or "").lower())}


def _uq_covered(uq, source_notes):
    """A UQ bullet counts as tested if some source_note shares enough significant words with it.

    UQ targeting is non-referential by design (the ledger has no UQ id scheme — see spec), so
    coverage is a fuzzy content-word overlap, not an ID match: >= 3 shared significant words, or at
    least half of a short UQ's significant words."""
    uw = _sig_words(uq)
    if not uw:
        return True  # nothing to match on; don't false-flag
    need = min(3, max(1, (len(uw) + 1) // 2))
    return any(len(uw & _sig_words(n)) >= need for n in source_notes)


def _finding_text(obj):
    """Concatenated free-text of a finding, for the coarse content-neutrality check."""
    parts = [str(obj.get(k, "")) for k in ("mechanism", "fix_class", "risk_if_fixed")]
    parts += [str(x) for x in (obj.get("evidence_refs") or [])]
    return " ".join(parts)


def _content_offenders(question, finding_text):
    """Quoted spans / multi-word-capitalized phrases in `question` absent from the finding text."""
    hay = (finding_text or "").lower()
    offenders = []
    for m in _QUOTED_RE.finditer(question):
        phrase = (m.group(1) or m.group(2) or "").strip()
        if phrase and phrase.lower() not in hay and ('"%s"' % phrase) not in offenders:
            offenders.append('"%s"' % phrase)
    # Cap-run scan, per sentence with the sentence-initial word dropped: its capital is positional,
    # not a proper noun, so "When Sarah…" / "In Chapter 9…" don't fuse into a false proper-noun run.
    # A genuinely invented multi-word run mid-sentence ("…the Ice Dragon's breath…") still fires.
    for sent in re.split(r"(?<=[.?!])\s+", question):
        sent = re.sub(r"^\s*[A-Za-z][\w']*\s+", "", sent, count=1)
        for m in _CAPRUN_RE.finditer(sent):
            phrase = m.group(1).strip()
            if phrase.lower() not in hay and phrase not in offenders:
                offenders.append(phrase)
    return offenders


def _overrides(text, kind):
    """RQ ids carrying an override comment of the given kind."""
    out = set()
    if not text:
        return out
    pat = re.compile(r"<!--\s*override:\s*%s\s+(RQ-[0-9]+)\b" % re.escape(kind), re.IGNORECASE)
    for m in pat.finditer(text):
        out.add(m.group(1))
    return out


def check(instrument_text, ledger_text, strict=False):
    """Run the Beta-Reader Instrument integrity checks. Returns (code, lines)."""
    lines, errs, warns = [], [], []
    items = parse_questions(instrument_text)
    index = ledger_index(ledger_text)
    if not items:
        return 0, ["reader-instrument: no reader_question blocks found — nothing to validate"]

    # B1 — schema/JSON validity (per block)
    for _obj, schema_errs, _idx in items:
        for e in schema_errs:
            errs.append("B1 invalid item: %s" % e)

    valid = [(obj, idx) for obj, schema_errs, idx in items if obj is not None and not schema_errs]

    # B2 — duplicate id
    seen = {}
    for obj, idx in valid:
        seen.setdefault(obj.get("id"), []).append(idx)
    for rid, where in sorted(seen.items()):
        if len(where) > 1:
            errs.append("B2 duplicate id: %s appears %d times (ids must be unique per instrument)"
                        % (rid, len(where)))

    lead_ovr = _overrides(instrument_text, "leading-question")
    fix_ovr = _overrides(instrument_text, "how-to-fix")
    targeted_findings = set()
    sourced_uqs = []
    uqs = unresolved_questions(ledger_text)   # the Ledger's Unresolved-Questions bullets (for B3 + W1)

    for obj, _idx in valid:
        rid = obj.get("id")
        kind = obj.get("source_kind")
        targets = (obj.get("targets") or "").strip()
        note = (obj.get("source_note") or "").strip()

        # B3 — provenance integrity (conditional-required, enforced here not in the flat schema)
        if kind in _FROM_FINDING:
            if not targets:
                errs.append("B3 provenance integrity: %s is %s but has no `targets` finding id" % (rid, kind))
            elif targets not in index:
                errs.append("B3 provenance integrity: %s.targets cites %s — no such finding in the Ledger"
                            % (rid, targets))
            else:
                targeted_findings.add(targets)
                # B3 advisory: a low-confidence-finding probe should target an actually-open finding.
                # (A tradeoff legitimately rides any finding — its uncertainty is in `risk_if_fixed`.)
                if kind == "low-confidence-finding" and index[targets].get("confidence") not in _OPEN_CONFIDENCE:
                    warns.append("B3 source mismatch: %s is low-confidence-finding but targets %s "
                                 "(confidence %s, not LOW/UNCERTAIN) — the kind label should match the Ledger"
                                 % (rid, targets, index[targets].get("confidence")))
        elif kind == "unresolved-question":
            if not note:
                errs.append("B3 provenance integrity: %s is unresolved-question but has no `source_note`" % rid)
            if targets:
                errs.append("B3 provenance integrity: %s is unresolved-question but carries `targets`=%r "
                            "(unresolved questions have no finding id)" % (rid, targets))
            if note:
                sourced_uqs.append(note)
                # B3 advisory: the source_note should correspond to a real `### Unresolved Questions`
                # bullet. Coarse word-overlap (same heuristic as W1's coverage match), not an id match.
                if not uqs:
                    warns.append("B3 unsourced question: %s cites an Unresolved Question but the Ledger "
                                 "has no `### Unresolved Questions` bullets (verify the source is real): %s"
                                 % (rid, note[:60]))
                elif not any(_uq_covered(uqb, [note]) for uqb in uqs):
                    warns.append("B3 unsourced question: %s cites a source_note matching no Unresolved "
                                 "Questions bullet in the Ledger (coarse word-overlap — verify it is real): %s"
                                 % (rid, note[:60]))

        question = obj.get("question") or ""
        # B4 — leading construction (sound blocklist) + invented content (coarse heuristic)
        if rid not in lead_ovr:
            ql = question.lower()
            hits = [p for p in _LEADING if p in ql]
            offenders = []
            if kind in _FROM_FINDING and targets in index:
                offenders = _content_offenders(question, _finding_text(index[targets]))
            if hits:
                warns.append("B4 leading: %s uses a leading construction (%s) — pre-loads the answer"
                             % (rid, ", ".join('"%s"' % h for h in hits)))
            if offenders:
                warns.append("B4 invented content: %s introduces %s, absent from the target finding "
                             "(coarse heuristic — verify it is on the page)" % (rid, ", ".join(offenders)))

        # B5 — relitigating a locked verdict
        if kind in _FROM_FINDING and targets in index and rid not in fix_ovr:
            f = index[targets]
            if f.get("severity") in _LOCKED_SEVERITY and f.get("confidence") in _LOCKED_CONFIDENCE:
                warns.append("B5 relitigating locked verdict: %s targets %s (%s / %s) — a locked verdict "
                             "is not a reader poll; override how-to-fix if testing the fix approach"
                             % (rid, targets, f.get("severity"), f.get("confidence")))

    # W1 — coverage: a LOW/UNCERTAIN finding or a UQ bullet with no question
    for fid in sorted(open_finding_ids(index) - targeted_findings):
        warns.append("W1 coverage: finding %s is %s but no reader question tests it"
                     % (fid, index[fid].get("confidence")))
    for uq in uqs:
        if not _uq_covered(uq, sourced_uqs):
            warns.append("W1 coverage: unresolved question is untested — %s" % (uq[:72]))

    # Report
    lines.append("reader-instrument: %d question(s)%s" % (len(items),
                 "" if len(valid) == len(items) else " (%d well-formed)" % len(valid)))
    for obj, _idx in valid:
        prov = (obj.get("targets") or obj.get("source_note") or "—")
        lines.append("  %-7s %-22s prov=%-14s probe=%s"
                     % (obj.get("id"), obj.get("source_kind"), str(prov)[:14], obj.get("probe_type")))
    for e in errs:
        lines.append("  ERROR: %s" % e)
    for w in warns:
        lines.append("  %s: %s" % ("ERROR (--strict)" if strict else "WARN", w))

    if errs or (strict and warns):
        lines.append("reader-instrument: FAIL (%d error(s)%s)"
                     % (len(errs), ", %d strict warn(s)" % len(warns) if (strict and warns) else ""))
        return 1, lines
    if warns:
        lines.append("WARN: reader-instrument: %d advisory flag(s) — see B3/B4/B5/W1 above" % len(warns))
    else:
        lines.append("reader-instrument: PASS (contract + provenance + firewall + anti-relitigation)")
    return 0, lines


# ---------------------------------------------------------------- resolution

def _newest(paths):
    return max(paths, key=os.path.getmtime) if paths else None


def resolve(paths):
    """Return (instrument_path, ledger_path) from a run folder or explicit files."""
    if len(paths) == 1 and os.path.isdir(paths[0]):
        inst = _newest(glob.glob(os.path.join(paths[0], _INSTRUMENT_GLOB)))
        led = _newest(glob.glob(os.path.join(paths[0], _LEDGER_GLOB)))
        return inst, led
    inst = led = None
    for p in paths:
        body = _read(p) or ""
        if "apodictic:reader_question" in body and inst is None:
            inst = p
        elif ("apodictic:finding" in body or "Unresolved Questions" in body) and led is None:
            led = p
    # fall back to the first arg as the instrument so a clean empty file reports a no-op
    if inst is None and paths:
        inst = paths[0]
    return inst, led


def run(paths, strict=False):
    inst, led = resolve(paths)
    if not inst:
        return 2, ["reader-instrument: no Beta-Reader Instrument artifact found (need a "
                   "*_Beta_Reader_Instrument_*.md or a file with apodictic:reader_question blocks)"]
    itext = _read(inst)
    if itext is None:
        return 2, ["reader-instrument: cannot read %s" % inst]
    ltext = _read(led) if led else None
    return check(itext, ltext, strict=strict)


# ---------------------------------------------------------------- self-test

def run_self_test():
    import json as _j
    import tempfile
    import shutil
    rc = {"v": 0}
    made = []

    def chk(name, cond):
        print("  %s: %s" % (name, "OK" if cond else "FAIL"))
        if not cond:
            rc["v"] = 1

    def rq(rid="RQ-01", kind="low-confidence-finding", targets="F-P5-02", note="",
           probe="experiential", question="At the midway turn, what did you expect next?",
           signal="confirm vs refute", extra=None):
        obj = {"schema": _SCHEMA_ID, "id": rid, "source_kind": kind, "uncertainty": "u",
               "probe_type": probe, "question": question, "expected_signal": signal}
        if targets:
            obj["targets"] = targets
        if note:
            obj["source_note"] = note
        if extra:
            obj.update(extra)
        return "<!-- apodictic:reader_question\n%s\n-->" % _j.dumps(obj)

    def finding(fid="F-P5-02", severity="Should-Fix", confidence="LOW",
                mechanism="the midpoint reversal under-lands", risk="a sharper turn could feel abrupt"):
        obj = {"schema": _FINDING_SCHEMA_ID, "id": fid, "mechanism": mechanism, "severity": severity,
               "confidence": confidence, "evidence_refs": ["Ch. 7"], "fix_class": "sharpen the turn",
               "risk_if_fixed": risk}
        return "<!-- apodictic:finding\n%s\n-->" % _j.dumps(obj)

    def ledger(*findings, uqs=("none",)):
        body = "# Findings Ledger\n" + "\n".join(findings)
        body += "\n\n### Unresolved Questions\n\n" + "\n".join("- %s" % u for u in uqs) + "\n"
        return body

    led_low = ledger(finding())  # one LOW Should-Fix finding, no UQs

    # clean: a LOW finding tested by a non-leading experiential question
    chk("clean_low", check(rq(), led_low)[0] == 0)

    # B1 — bad enum / id / missing field / JSON
    chk("b1_bad_source_kind", check(rq(kind="rumor"), led_low)[0] == 1)
    chk("b1_bad_probe", check(rq(probe="vibes"), led_low)[0] == 1)
    chk("b1_bad_id", check(rq(rid="RQ-1"), led_low)[0] == 1)
    code, ls = check('<!-- apodictic:reader_question\n{"schema":"apodictic.reader_question.v1"\n-->', led_low)
    chk("b1_bad_json", code == 1 and any("B1 invalid item" in x for x in ls))

    # B2 — duplicate id
    code, ls = check(rq() + "\n" + rq(question="Another?"), led_low)
    chk("b2_dup", code == 1 and any("B2 duplicate" in x for x in ls))

    # B3 — finding source with missing / dangling targets
    chk("b3_missing_targets", check(rq(targets=""), led_low)[0] == 1)
    code, ls = check(rq(targets="F-NOPE-99"), led_low)
    chk("b3_dangling", code == 1 and any("B3" in x and "F-NOPE-99" in x for x in ls))
    # B3 — unresolved-question must carry source_note and NOT targets
    chk("b3_uq_needs_note", check(rq(kind="unresolved-question", targets="", note=""),
                                  ledger(finding(), uqs=("does the ending land?",)))[0] == 1)
    code, ls = check(rq(kind="unresolved-question", targets="F-P5-02", note="the ending"),
                     ledger(finding(), uqs=("the ending",)))
    chk("b3_uq_no_targets", code == 1 and any("B3" in x and "carries" in x for x in ls))
    # clean unresolved-question (note only, no targets)
    chk("uq_clean", check(rq(kind="unresolved-question", targets="", note="does the ending land?"),
                          ledger(finding(), uqs=("does the ending land?",)))[0] == 0)
    # B3 advisory — a low-confidence-finding probe pointed at a non-open (HIGH) finding (Could-Fix so B5
    # doesn't also fire): kind label disagrees with the Ledger → advisory WARN, not an error.
    code, ls = check(rq(targets="F-HI-01"),
                     ledger(finding(fid="F-HI-01", severity="Could-Fix", confidence="HIGH")))
    chk("b3_source_mismatch", code == 0 and any("B3 source mismatch" in x for x in ls))
    # ...but a tradeoff legitimately rides a HIGH finding — no mismatch flag.
    chk("b3_tradeoff_high_ok",
        not any("B3 source mismatch" in x for x in
                check(rq(kind="tradeoff", targets="F-HI-01"),
                      ledger(finding(fid="F-HI-01", severity="Could-Fix", confidence="HIGH")))[1]))
    # B3 advisory — an unresolved-question whose source_note matches no UQ bullet → fabrication WARN.
    code, ls = check(rq(kind="unresolved-question", targets="", note="something totally unrelated zebra"),
                     ledger(finding(), uqs=("does the ending land?",)))
    chk("b3_unsourced_uq", code == 0 and any("B3 unsourced question" in x for x in ls))
    # B3 advisory — an unresolved-question when the Ledger has NO UQ bullets at all → fabrication WARN.
    code, ls = check(rq(kind="unresolved-question", targets="", note="does the ending land?"),
                     ledger(finding(), uqs=("none",)))
    chk("b3_unsourced_uq_no_bullets", code == 0 and any("B3 unsourced question" in x and "no `###" in x for x in ls))
    # ...but a covered UQ with bullets present stays clean (no false fabrication WARN).
    chk("b3_sourced_uq_clean",
        not any("B3 unsourced" in x for x in
                check(rq(kind="unresolved-question", targets="", note="does the ending land?"),
                      ledger(finding(), uqs=("does the ending land?",)))[1]))

    # B4 — leading construction (advisory, ERROR --strict), and override clears it
    lead = rq(question="Don't you think the midpoint reversal lands?")
    code, ls = check(lead, led_low)
    chk("b4_leading_advisory", code == 0 and any("B4 leading" in x for x in ls))
    chk("b4_leading_strict_fails", check(lead, led_low, strict=True)[0] == 1)
    ovr = lead + "\n<!-- override: leading-question RQ-01 — quoting the author's own phrasing -->"
    chk("b4_leading_override", check(ovr, led_low, strict=True)[0] == 0)
    # B4 — invented content (capitalized phrase absent from finding)
    code, ls = check(rq(question="Did the Ice Dragon's breath feel powerful at the turn?"), led_low)
    chk("b4_invented_advisory", code == 0 and any("B4 invented" in x for x in ls))
    # B4 — sentence-initial capital + a name is NOT a false invented-content flag (P3-1 fix)
    code, ls = check(rq(question="When Donut leaves the scene, what did you expect to change?"), led_low)
    chk("b4_no_sentence_initial_fp", code == 0 and not any("B4 invented" in x for x in ls))

    # B5 — relitigating a locked verdict (Must-Fix/HIGH), advisory + override. Use a `tradeoff` probe:
    # the fix-approach of a locked verdict is a tradeoff question, not a low-confidence one — and a
    # tradeoff legitimately rides a non-LOW finding (so B3 source-mismatch does not also fire here).
    led_locked = ledger(finding(severity="Must-Fix", confidence="HIGH"))
    code, ls = check(rq(kind="tradeoff"), led_locked)
    chk("b5_locked_advisory", code == 0 and any("B5 relitigating" in x for x in ls))
    chk("b5_locked_strict_fails", check(rq(kind="tradeoff"), led_locked, strict=True)[0] == 1)
    # MEDIUM Must-Fix is still locked (the closed hole)
    chk("b5_medium_mustfix_locked",
        any("B5" in x for x in check(rq(kind="tradeoff"),
                                     ledger(finding(severity="Must-Fix", confidence="MEDIUM")))[1]))
    ovr5 = rq(kind="tradeoff") + "\n<!-- override: how-to-fix RQ-01 — testing the fix approach, not the verdict -->"
    chk("b5_how_to_fix_override", check(ovr5, led_locked, strict=True)[0] == 0)
    # a Could-Fix HIGH finding is NOT locked (severity gate)
    chk("b5_couldfix_not_locked",
        not any("B5" in x for x in check(rq(kind="tradeoff"),
                                         ledger(finding(severity="Could-Fix", confidence="HIGH")))[1]))

    # W1 — an untested LOW finding (advisory)
    code, ls = check(rq(kind="unresolved-question", targets="", note="x"),
                     ledger(finding(fid="F-A-01", confidence="LOW"), uqs=("x",)))
    chk("w1_uncovered_finding", code == 0 and any("W1 coverage" in x and "F-A-01" in x for x in ls))
    # W1 — an untested UQ bullet
    code, ls = check(rq(), ledger(finding(), uqs=("does the ending land?",)))
    chk("w1_uncovered_uq", code == 0 and any("W1 coverage" in x and "ending" in x for x in ls))

    # no blocks -> no-op
    chk("no_items_noop", check("# Instrument\nNo questions yet.\n", led_low)[0] == 0)

    # file + run-folder resolution
    d = tempfile.mkdtemp()
    made.append(d)
    with open(os.path.join(d, "Proj_Findings_Ledger_run.md"), "w") as fh:
        fh.write(led_low)
    with open(os.path.join(d, "Proj_Beta_Reader_Instrument_run.md"), "w") as fh:
        fh.write("# Instrument\n" + rq() + "\n")
    chk("run_folder_resolution", run([d])[0] == 0)
    chk("explicit_files_resolution",
        run([os.path.join(d, "Proj_Beta_Reader_Instrument_run.md"),
             os.path.join(d, "Proj_Findings_Ledger_run.md")])[0] == 0)
    chk("missing_artifact_usage", run([d + "/nope.md"])[0] in (2,))

    for d in made:
        shutil.rmtree(d, ignore_errors=True)
    print("Self-test: PASS" if rc["v"] == 0 else "Self-test: FAIL")
    return rc["v"]


def main(argv):
    if "--self-test" in argv:
        return run_self_test()
    args = [a for a in argv[1:] if a != "reader-instrument"]
    strict = "--strict" in args
    paths = [a for a in args if not a.startswith("--")]
    if not paths:
        print("Usage: reader_instrument.py reader-instrument <run_folder|files...> [--strict] | --self-test")
        return 2
    code, lines = run(paths, strict=strict)
    for ln in lines:
        print(ln)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
