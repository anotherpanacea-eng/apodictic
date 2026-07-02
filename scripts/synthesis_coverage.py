#!/usr/bin/env python3
"""synthesis-coverage — synthesis coverage disclosure gate (docs/synthesis-regrounding.md, M1).

`validate.sh synthesis-coverage <run_folder> [--strict]` shells out here. A run that wrote a
full editorial letter (`*_Core_DE_Synthesis_*` / `*_Full_DE_Synthesis_*` — the same detection
the annotated-manuscript offer uses) must disclose what the synthesis step could actually see
when it wrote the letter. The design rule that keeps the disclosure honest: **the note is
computed from the artifact-read manifest, and the manifest's denominator is enumerated from
disk** (run-folder globs) — never from the letter's own prose, never from a model's memory of
what it read.

Checks (spec §M1.5):

  V1 presence        a full-letter run must have the manifest file
                     (`[Project]_Synthesis_Read_Manifest_[runlabel].md`, EXACT name derived from
                     the letter's own project/runlabel — a `*_Manifest_Draft_*` lookalike is not
                     accepted), the Appendix C `### Synthesis Coverage` subsection, the
                     `<!-- coverage: ok|degraded -->` title-block marker, and the sidecar
                     `synthesis_coverage` object. Partial / fragment / triage runs (no full
                     letter) carry no coverage obligation.
  V2 completeness    the can't-be-fiction floor: disk<->manifest row BIJECTION. Every enumerated
                     run-folder artifact (pass artifacts `_Pass[N]_`, Findings Ledger, Contract,
                     audit files) has exactly one manifest row, and every artifact row's id
                     resolves to an enumerated file — the manifest can neither shrink nor pad
                     the denominator. At least one span row is required (the manuscript
                     dimension cannot be omitted).
  V3 reconciliation  the letter's Appendix C note table is an EXACT projection of the manifest
                     (same closed row grammar; synthesis_coverage.py is the only parser); the
                     sidecar tallies equal the manifest row counts; `coverage` equals the letter
                     marker; exactly one coverage marker exists; row-grammar violations
                     (unknown kind/status, any annotation other than `regrounded: true`) FAIL
                     here, never silently ignored.
  V4 provenance/mode sequential/hybrid/swarm => `dispatch-derived` (`declared` FAILS — the
                     cheap lie is blocked); single-agent => `declared` (a dispatch claim with no
                     dispatch FAILS) plus the pinned declared-not-platform-verified sentence
                     verbatim in the note.
  V5 degrade         `ok|degraded` is RECOMPUTED from the manifest + sidecar + ledger per the
                     D1-D4 truth table below; a run that computes degraded but declares ok FAILS
                     (masking fails louder than degrading), and a degraded run must carry the
                     pinned Short Version sentence. Normal multi-agent outline-mediated coverage
                     is NOT degraded — that is the architecture working as designed.

  D1  any artifact row `status: absent`                                  (all modes)
  D2  a synthesis-bound (Must-Fix/Should-Fix) ledger finding covered by no `verbatim` origin-pass
      artifact row and no chapter-matching `in-context` span row         (all modes; a finding
      whose evidence_refs carry no chapter tokens is reported unevaluable, never fired)
  D3  `estimated_context_utilization` > 60 (percent of the detected window) (single-agent only)
  D4  zero `in-context` span rows while the ledger carries >= 1 Must-Fix (multi-agent only)

No override markers exist for any check — disclosure is not overridable; the only legitimate
escape is fixing the manifest (spec: V2/V3/V5 "no override markers").

LAUNCH POSTURE (operator call folded 2026-07-01, spec §Open questions #1): the V2/V3/V4
fiction-checks are BLOCKING day one (ERROR, exit 1). V1/V5 — and therefore the overall gate —
are ADVISORY-FIRST for one release: they print WARN at exit 0 (the escalation-check posture, so
the `run_spot_check` gate records pass-with-warn instead of blocked); `--strict` promotes them
to ERROR. The flip to blocking-by-default lands once a few real runs confirm the D-table
thresholds don't over-fire.

Untrusted-path containment: nothing in the manifest or sidecar ever drives a filesystem read or
write. Artifact row ids are compared AS STRINGS against this validator's own run-folder
enumeration; the sidecar's `manifest` field is compared by basename string against the
independently-resolved manifest path.

  synthesis_coverage.py synthesis-coverage <run_folder> [--strict]
  synthesis_coverage.py --self-test

Exit: 0 clean / WARN-only, 1 ERROR (or advisory WARN under --strict), 2 usage.
"""
import glob
import json
import os
import re
import sys

try:
    import apodictic_artifacts as art
except ImportError:
    art = None

try:
    from override_marker import strip_code_spans
except ImportError:  # degraded: scan raw text (in-repo the shared stripper always ships)
    def strip_code_spans(body):
        return body or ""

# ---------------------------------------------------------------- pinned vocabulary

_MULTI_MODES = ("sequential", "hybrid", "swarm")
_ALL_MODES = ("single-agent",) + _MULTI_MODES
_ARTIFACT_STATUSES = ("verbatim", "summary", "absent")
_SPAN_STATUSES = ("in-context", "outside-active-context")
_ANNOTATION_REGROUNDED = "regrounded: true"   # the only annotation M1/M2 define; M1 never writes it

# Pinned letter language (run-synthesis.md §Appendix C — Synthesis Coverage; §The Short Version).
MODE_SENTENCE = "This letter was synthesized in %s mode."
SENT_DISPATCH = ("The coverage below is dispatch-derived: it lists exactly the artifacts and "
                 "excerpts the synthesis step received.")
SENT_DECLARED = ("The coverage below is declared by the model, not platform-verified: with a "
                 "single long context, what remained in active attention at letter time cannot "
                 "be mechanically observed.")
SENT_DEGRADED = ("Coverage note: synthesis-time contact with the manuscript was degraded; see "
                 "the Synthesis Coverage note in Appendix C.")

# D3: preflight's viability threshold family (execution-modes-reference.md — single-agent viable
# under 600K of a 1M window). Percent of the detected window.
UTILIZATION_THRESHOLD = 60.0

# Marker parse regex, pinned in the spec's V5 table: raw line, own line, nothing else on it.
_MARKER_RE = re.compile(r"^<!-- coverage: (ok|degraded) -->\s*$")
_NOTE_HEADING_RE = re.compile(r"^#{2,4}\s+Synthesis Coverage\s*$")
_HEADING_RE = re.compile(r"^#{1,4}\s")
_SHORT_VERSION_RE = re.compile(r"^#{1,4}\s.*The Short Version", re.IGNORECASE)

_LETTER_GLOBS = ("*_Core_DE_Synthesis_*.md", "*_Full_DE_Synthesis_*.md")
_LETTER_RE = re.compile(r"^(?P<project>.+?)_(?:Core|Full)_DE_Synthesis_(?P<runlabel>.+)\.md$")
_LEDGER_GLOB = "*_Findings_Ledger_*.md"
_PASS_RE = re.compile(r"_Pass\d+_")

# Chapter tokens in span ids / evidence_refs: "Ch 12", "ch. 3", "Chapter 7", ranges "Ch 1-2".
_CH_RE = re.compile(r"\b[Cc]h(?:apter)?\.?\s*(\d+)(?:\s*[–—-]\s*(\d+))?")
_FULL_MANUSCRIPT = "full manuscript"   # single-agent universal span label (run-synthesis.md 9b)

_BLOCKING = ("V2", "V3", "V4")   # fiction-checks — blocking day one (folded operator call)
_ADVISORY = ("V1", "V5")         # advisory-first for one release; --strict promotes


def _read(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return None


def _newest(paths):
    return max(paths, key=os.path.getmtime) if paths else None


def _walk_up_sidecar(start):
    d = os.path.abspath(start if os.path.isdir(start) else os.path.dirname(start))
    for _ in range(4):
        sc = os.path.join(d, "Diagnostic_State.meta.json")
        if os.path.exists(sc):
            return sc
        d = os.path.dirname(d)
    return None


# ---------------------------------------------------------------- manifest / note parsing

def parse_rows(text):
    """Parse the closed four-cell pipe-table grammar. Returns (rows, errors).

    rows: [{kind, id, status, annotations}, ...]. Header rows (first cell 'kind') and
    separator rows (dashes/colons) are skipped; every other pipe line must parse — a wrong
    cell count, unknown kind, out-of-enum status, or any annotation other than
    'regrounded: true' is an error (this is the only parser; nothing is silently ignored)."""
    rows, errors = [], []
    for raw in (text or "").split("\n"):
        line = raw.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if all(re.fullmatch(r"[-: ]*", c) and "-" in c for c in cells if c is not None) and cells:
            continue  # separator row
        if len(cells) != 4:
            errors.append("row has %d cells, expected 4 (| kind | id | status | annotations |): %r"
                          % (len(cells), line))
            continue
        kind, rid, status, annotations = cells
        if kind.lower() == "kind":
            continue  # header row
        if kind not in ("artifact", "span"):
            errors.append("unknown kind %r (closed enum: artifact | span): %r" % (kind, line))
            continue
        allowed = _ARTIFACT_STATUSES if kind == "artifact" else _SPAN_STATUSES
        if status not in allowed:
            errors.append("unknown status %r for kind %r (closed enum: %s)"
                          % (status, kind, " | ".join(allowed)))
            continue
        if annotations not in ("", _ANNOTATION_REGROUNDED):
            errors.append("unknown annotation %r (only %r is defined; anything else is a parse "
                          "FAIL, never silently ignored)" % (annotations, _ANNOTATION_REGROUNDED))
            continue
        rows.append({"kind": kind, "id": rid, "status": status, "annotations": annotations})
    return rows, errors


def _row_key(r):
    return (r["kind"], r["id"], r["status"], r["annotations"])


def extract_note_section(stripped_lines):
    """Lines of the `### Synthesis Coverage` subsection (heading to next heading), or None."""
    start = None
    for i, ln in enumerate(stripped_lines):
        if _NOTE_HEADING_RE.match(ln):
            start = i + 1
            break
    if start is None:
        return None
    end = len(stripped_lines)
    for j in range(start, len(stripped_lines)):
        if _HEADING_RE.match(stripped_lines[j]):
            end = j
            break
    return stripped_lines[start:end]


def _section_text(stripped_lines, heading_re):
    start = None
    for i, ln in enumerate(stripped_lines):
        if heading_re.match(ln):
            start = i + 1
            break
    if start is None:
        return None
    end = len(stripped_lines)
    for j in range(start, len(stripped_lines)):
        if _HEADING_RE.match(stripped_lines[j]):
            end = j
            break
    return "\n".join(stripped_lines[start:end])


def find_markers(stripped_lines):
    """[(line_index, value), ...] for every raw-line coverage marker (code spans pre-stripped)."""
    return [(i, m.group(1)) for i, ln in enumerate(stripped_lines)
            for m in [_MARKER_RE.match(ln)] if m]


def marker_placement_ok(stripped_lines, marker_idx):
    """Spec V5 placement: the first non-blank line immediately after the title block."""
    title = None
    for i, ln in enumerate(stripped_lines):
        if ln.startswith("# "):
            title = i
            break
    if title is None:
        return False
    i = title
    while (i + 1 < len(stripped_lines) and stripped_lines[i + 1].strip()
           and not _MARKER_RE.match(stripped_lines[i + 1])):
        i += 1  # the contiguous title block (### author line, *version* line)
    j = i + 1
    while j < len(stripped_lines) and not stripped_lines[j].strip():
        j += 1
    return j == marker_idx


# ---------------------------------------------------------------- disk enumeration

def enumerate_denominator(run_folder):
    """The artifact-row denominator, enumerated from disk (never model-supplied): pass
    artifacts (`_Pass[N]_`), Findings Ledger, Contract, and audit files (Audit Invocation Log +
    audit findings files). Basenames, sorted."""
    names = set()
    for p in glob.glob(os.path.join(run_folder, "*.md")):
        b = os.path.basename(p)
        if (_PASS_RE.search(b) or "_Findings_Ledger_" in b or "_Contract_" in b
                or "_Audit_" in b):
            names.add(b)
    return sorted(names)


def resolve_letter(run_folder):
    paths = []
    for g in _LETTER_GLOBS:
        paths.extend(glob.glob(os.path.join(run_folder, g)))
    return _newest(paths)


# ---------------------------------------------------------------- sidecar / ledger helpers

def _int_field(obj, key):
    v = obj.get(key)
    if isinstance(v, bool) or not isinstance(v, int):
        return None
    return v


def sidecar_coverage_obj(sidecar_text):
    """(obj_or_None, state) — state in 'ok' / 'absent' / 'stub' / 'malformed' / 'no-sidecar'.
    A template-fresh stub (empty provenance AND coverage) reads as absent — the step was
    skipped, a V1 matter — while a present-but-garbage value is a V3 (fiction-adjacent)."""
    if sidecar_text is None:
        return None, "no-sidecar"
    try:
        meta = json.loads(sidecar_text)
    except (ValueError, TypeError):
        return None, "malformed"
    if not isinstance(meta, dict):
        return None, "malformed"
    sc = meta.get("synthesis_coverage")
    if sc is None:
        return None, "absent"
    if not isinstance(sc, dict):
        return None, "malformed"
    if not sc.get("provenance") and not sc.get("coverage"):
        return None, "stub"
    return sc, "ok"


def ledger_findings(ledger_text):
    """Synthesis-bound (Must-Fix/Should-Fix) apodictic.finding.v1 blocks from the ledger.
    Parsed blocks, never raw marker scans (meta-lint M2)."""
    out = []
    if not ledger_text or art is None:
        return out
    for bt, obj, _e in art.parse_blocks(ledger_text):
        if bt == "finding" and isinstance(obj, dict) and obj.get("severity") in ("Must-Fix",
                                                                                 "Should-Fix"):
            out.append(obj)
    return out


def chapters(text):
    """Chapter numbers named in a span id / evidence_ref, ranges expanded ('Ch 4-11')."""
    out = set()
    for m in _CH_RE.finditer(text or ""):
        a = int(m.group(1))
        b = int(m.group(2)) if m.group(2) else a
        if a <= b and b - a <= 1000:
            out.update(range(a, b + 1))
    return out


# ---------------------------------------------------------------- degrade truth table

def compute_degrade(rows, sc_obj, findings, mode):
    """(fired, unevaluable) — fired is ['D1 ...', ...] per the exhaustive V5 truth table,
    recomputed from the manifest + sidecar + ledger only (never from letter prose)."""
    fired, uneval = [], []
    single = (mode == "single-agent")

    absent = [r for r in rows if r["kind"] == "artifact" and r["status"] == "absent"]
    if absent:
        fired.append("D1 artifact row(s) absent: %s" % ", ".join(r["id"] for r in absent))

    in_ctx_rows = [r for r in rows if r["kind"] == "span" and r["status"] == "in-context"]
    universal = any(r["id"].strip().lower() == _FULL_MANUSCRIPT for r in in_ctx_rows)
    in_ctx_chapters = set()
    for r in in_ctx_rows:
        in_ctx_chapters |= chapters(r["id"])
    verbatim_pass_nums = set()
    for r in rows:
        if r["kind"] == "artifact" and r["status"] == "verbatim":
            m = re.search(r"_Pass(\d+)_", r["id"])
            if m:
                verbatim_pass_nums.add(m.group(1))

    for f in findings:
        fid = f.get("id") if isinstance(f.get("id"), str) else "?"
        m = re.match(r"F-P(\d+)-", fid)
        if m and m.group(1) in verbatim_pass_nums:
            continue  # origin pass artifact re-read verbatim — covered
        if universal:
            continue
        refs = [r for r in (f.get("evidence_refs") or []) if isinstance(r, str)]
        ref_ch = set()
        for r in refs:
            ref_ch |= chapters(r)
        if not ref_ch:
            uneval.append("D2 unevaluable for %s (no chapter tokens in evidence_refs) — assess "
                          "coverage manually" % fid)
            continue
        if not (ref_ch & in_ctx_chapters):
            fired.append("D2 synthesis-bound finding %s (evidence chapters %s) covered by no "
                         "verbatim origin-pass row and no in-context span"
                         % (fid, ",".join(str(c) for c in sorted(ref_ch))))

    if single:
        util = (sc_obj or {}).get("estimated_context_utilization")
        if isinstance(util, bool):
            util = None
        if isinstance(util, (int, float)) and util > UTILIZATION_THRESHOLD:
            fired.append("D3 estimated_context_utilization=%s > %s%% of the detected window"
                         % (util, int(UTILIZATION_THRESHOLD)))
    else:
        must_fix = sum(1 for f in findings if f.get("severity") == "Must-Fix")
        if not in_ctx_rows and must_fix >= 1:
            fired.append("D4 zero in-context verification-excerpt spans while the ledger carries "
                         "%d Must-Fix finding(s)" % must_fix)

    return fired, uneval


# ---------------------------------------------------------------- the check

def check_run_folder(run_folder, strict=False):
    """Run V1-V5 against a run folder. Returns (code, lines)."""
    lines = []
    findings = []   # (check_id, message)

    def add(check, msg):
        findings.append((check, msg))

    letter_path = resolve_letter(run_folder)
    if letter_path is None:
        return 0, ["synthesis-coverage: no full editorial letter (*_Core_DE_Synthesis_* / "
                   "*_Full_DE_Synthesis_*) in %s — no coverage obligation (partial / fragment / "
                   "triage runs are out of scope)" % run_folder]

    letter_base = os.path.basename(letter_path)
    m = _LETTER_RE.match(letter_base)
    project = m.group("project") if m else None
    runlabel = m.group("runlabel") if m else None

    # Manifest: EXACT name constructed from the letter's own project/runlabel — a lookalike
    # (`*_Synthesis_Read_Manifest_Draft_*`) does not satisfy V1. Path built from our own
    # derivation, never from manifest/sidecar content (containment).
    manifest_path = None
    if project and runlabel:
        cand = os.path.join(run_folder, "%s_Synthesis_Read_Manifest_%s.md" % (project, runlabel))
        if os.path.isfile(cand):
            manifest_path = cand
    if manifest_path is None:
        add("V1", "manifest %s_Synthesis_Read_Manifest_%s.md not found in the run folder (exact "
            "name derived from the letter; a lookalike/draft name does not count)"
            % (project or "[Project]", runlabel or "[runlabel]"))

    letter_text = _read(letter_path) or ""
    stripped_lines = strip_code_spans(letter_text).split("\n")

    markers = find_markers(stripped_lines)
    declared = None
    if not markers:
        add("V1", "title-block coverage marker missing (pinned form: <!-- coverage: ok --> or "
            "<!-- coverage: degraded -->, own line, first non-blank line after the title block)")
    else:
        declared = markers[0][1]
        if len(markers) > 1:
            add("V3", "%d coverage markers found — one declaration, one place (first match wins; "
                "a second marker anywhere in the letter FAILS)" % len(markers))
        if not marker_placement_ok(stripped_lines, markers[0][0]):
            add("V5", "coverage marker present but not the first non-blank line after the title "
                "block (pinned placement)")

    note_lines = extract_note_section(stripped_lines)
    if note_lines is None:
        add("V1", "Appendix C subsection heading `### Synthesis Coverage` missing from the letter")

    sidecar_path = _walk_up_sidecar(run_folder)
    sc_obj, sc_state = sidecar_coverage_obj(_read(sidecar_path) if sidecar_path else None)
    if sc_state == "no-sidecar":
        add("V1", "no Diagnostic_State.meta.json found at or above the run folder — the sidecar "
            "synthesis_coverage object is required for a full-letter run")
    elif sc_state == "absent":
        add("V1", "sidecar synthesis_coverage object missing")
    elif sc_state == "stub":
        add("V1", "sidecar synthesis_coverage object is an unfilled template stub (empty "
            "provenance/coverage) — fill it at the Synthesis Coverage Manifest step")
    elif sc_state == "malformed":
        add("V3", "sidecar synthesis_coverage present but malformed (not a filled JSON object) — "
            "the reconciliation cannot be faked with a bare string")

    mode = (sc_obj or {}).get("execution_mode")
    provenance = (sc_obj or {}).get("provenance")

    # ---- V4 provenance/mode agreement ----
    if sc_obj is not None:
        if mode not in _ALL_MODES:
            add("V4", "execution_mode %r is not a known mode (%s)" % (mode, ", ".join(_ALL_MODES)))
        if provenance not in ("declared", "dispatch-derived"):
            add("V4", "provenance %r is not in the closed enum (declared | dispatch-derived)"
                % (provenance,))
        elif mode in _MULTI_MODES and provenance != "dispatch-derived":
            add("V4", "execution_mode %r requires provenance dispatch-derived; 'declared' in a "
                "multi-agent run is the cheap lie the gate blocks" % mode)
        elif mode == "single-agent" and provenance != "declared":
            add("V4", "single-agent runs have no dispatch record — provenance must be 'declared' "
                "(a dispatch-derived claim with no dispatch is fiction)")
        if note_lines is not None and mode in _ALL_MODES:
            note_text = "\n".join(note_lines)
            if (MODE_SENTENCE % mode) not in note_text:
                add("V4", "pinned mode sentence missing from the note: %r" % (MODE_SENTENCE % mode))
            want = SENT_DECLARED if mode == "single-agent" else SENT_DISPATCH
            if want not in note_text:
                add("V4", "pinned provenance sentence missing from the note (verbatim): %r" % want)

    # ---- manifest parse + V2 completeness ----
    rows = []
    if manifest_path is not None:
        rows, perrs = parse_rows(_read(manifest_path))
        for e in perrs:
            add("V3", "manifest parse: %s" % e)

        denom = enumerate_denominator(run_folder)
        art_rows = [r for r in rows if r["kind"] == "artifact"]
        span_rows = [r for r in rows if r["kind"] == "span"]
        by_id = {}
        for r in art_rows:
            by_id.setdefault(r["id"], []).append(r)
        for b in denom:
            n = len(by_id.get(b, []))
            if n == 0:
                add("V2", "on-disk artifact %s has no manifest row — the manifest cannot shrink "
                    "the denominator" % b)
            elif n > 1:
                add("V2", "artifact %s has %d manifest rows — exactly one row per enumerated "
                    "item" % (b, n))
        for rid in by_id:
            if rid not in denom:
                add("V2", "manifest artifact row %r does not resolve to an enumerated run-folder "
                    "file — the manifest cannot pad the denominator" % rid)
        if not span_rows:
            add("V2", "no span rows — the manuscript dimension cannot be omitted (at least one "
                "chapter/scene span row, or the single-agent 'full manuscript' row, is required)")
        span_ids = {}
        for r in span_rows:
            span_ids.setdefault(r["id"], []).append(r)
        for sid, rs in span_ids.items():
            if len(rs) > 1:
                add("V2", "span %r has %d manifest rows — exactly one row per span" % (sid, len(rs)))

    # ---- V3 reconciliation (note / sidecar / marker as projections of the manifest) ----
    if manifest_path is not None and note_lines is not None:
        note_rows, nerrs = parse_rows("\n".join(note_lines))
        for e in nerrs:
            add("V3", "note table parse: %s" % e)
        if not note_rows:
            add("V3", "the Synthesis Coverage note carries no projection table — the note must "
                "reproduce the manifest rows (same four-cell grammar)")
        elif sorted(map(_row_key, note_rows)) != sorted(map(_row_key, rows)):
            add("V3", "the note table is not an exact projection of the manifest — the letter "
                "may never claim broader (or different) coverage than the manifest records")

    if manifest_path is not None and sc_obj is not None:
        tallies = {"artifacts_verbatim": "verbatim", "artifacts_summary": "summary",
                   "artifacts_absent": "absent"}
        for field, status in tallies.items():
            want = sum(1 for r in rows if r["kind"] == "artifact" and r["status"] == status)
            got = _int_field(sc_obj, field)
            if got != want:
                add("V3", "sidecar %s=%r but the manifest tallies %d" % (field, sc_obj.get(field),
                                                                         want))
        want_out = sorted(r["id"] for r in rows
                          if r["kind"] == "span" and r["status"] == "outside-active-context")
        got_out = sc_obj.get("spans_outside_active_context")
        got_list = sorted(x for x in got_out if isinstance(x, str)) if isinstance(got_out, list) \
            else None
        if got_list != want_out:
            add("V3", "sidecar spans_outside_active_context %r does not equal the manifest's "
                "outside-active-context span ids %r" % (got_out, want_out))
        n_in_ctx = sum(1 for r in rows if r["kind"] == "span" and r["status"] == "in-context")
        vec = sc_obj.get("verification_excerpt_count")
        if mode in _MULTI_MODES:
            if _int_field(sc_obj, "verification_excerpt_count") != n_in_ctx:
                add("V3", "sidecar verification_excerpt_count=%r but the manifest has %d "
                    "in-context span row(s)" % (vec, n_in_ctx))
        elif mode == "single-agent" and vec is not None:
            add("V3", "verification_excerpt_count must be null in single-agent runs (no excerpt "
                "machinery); got %r" % (vec,))
        util = sc_obj.get("estimated_context_utilization")
        if isinstance(util, bool) or (util is not None and not isinstance(util, (int, float))):
            add("V3", "estimated_context_utilization must be a number or null; got %r" % (util,))
        elif mode in _MULTI_MODES and util is not None:
            add("V3", "estimated_context_utilization must be null in multi-agent runs (the field "
                "is single-agent only); got %r" % (util,))
        if mode == "single-agent" and note_lines is not None:
            note_text = "\n".join(note_lines)
            nm = re.search(r"estimated context utilization\s+([0-9]+(?:\.[0-9]+)?)%", note_text)
            if isinstance(util, (int, float)) and not isinstance(util, bool):
                if nm is None:
                    add("V3", "single-agent note must carry 'estimated context utilization NN% "
                        "per preflight' matching the sidecar (%r)" % (util,))
                elif abs(float(nm.group(1)) - float(util)) > 0.05:
                    add("V3", "note claims %s%% context utilization but the sidecar records %r"
                        % (nm.group(1), util))
            elif nm is not None:
                add("V3", "note claims %s%% context utilization but the sidecar records none"
                    % nm.group(1))

        cov = sc_obj.get("coverage")
        if cov not in ("ok", "degraded"):
            add("V3", "sidecar coverage %r is not in the closed enum (ok | degraded)" % (cov,))
        elif declared is not None and cov != declared:
            add("V3", "sidecar coverage=%r but the letter marker declares %r — the marker and "
                "the sidecar are one declaration" % (cov, declared))

        man_field = sc_obj.get("manifest")
        if manifest_path is not None:
            want_base = os.path.basename(manifest_path)
            if not isinstance(man_field, str) or os.path.basename(man_field) != want_base:
                add("V3", "sidecar manifest=%r does not name the run folder's manifest %s "
                    "(basename compare only — no path in the sidecar is ever dereferenced)"
                    % (man_field, want_base))

    # ---- V5 degrade recompute ----
    uneval = []
    if manifest_path is not None and sc_obj is not None:
        ledger_path = _newest(glob.glob(os.path.join(run_folder, _LEDGER_GLOB)))
        led_findings = ledger_findings(_read(ledger_path) if ledger_path else None)
        fired, uneval = compute_degrade(rows, sc_obj, led_findings,
                                        mode if mode in _ALL_MODES else None)
        computed = "degraded" if fired else "ok"
        if declared is not None:
            if computed == "degraded" and declared == "ok":
                add("V5", "recomputed coverage is DEGRADED (%s) but the letter declares 'ok' — "
                    "masking fails louder than degrading; there is no override, fix the "
                    "manifest or the marker" % "; ".join(fired))
            elif computed == "ok" and declared == "degraded":
                add("V5", "letter declares 'degraded' but no D1-D4 condition fires — the "
                    "recomputed state is 'ok' (boy-who-cried-degraded erodes the note)")
        if computed == "degraded":
            sv = _section_text(stripped_lines, _SHORT_VERSION_RE)
            if sv is None or SENT_DEGRADED not in sv:
                add("V5", "coverage is degraded but the pinned Short Version sentence is "
                    "missing: %r (body is canonical; appendices hold evidence)" % SENT_DEGRADED)

    # ---- report ----
    lines.append("synthesis-coverage: letter=%s manifest=%s mode=%s provenance=%s declared=%s"
                 % (letter_base,
                    os.path.basename(manifest_path) if manifest_path else "MISSING",
                    mode or "unknown", provenance or "unknown", declared or "none"))
    n_err = n_warn = 0
    for check, msg in findings:
        blocking = check in _BLOCKING or strict
        if blocking:
            n_err += 1
            lines.append("  ERROR %s: %s" % (check, msg))
        else:
            n_warn += 1
            lines.append("  WARN %s: %s" % (check, msg))
    for u in uneval:
        lines.append("  note: %s" % u)

    if n_err:
        lines.append("synthesis-coverage: FAIL (%d ERROR%s — V2/V3/V4 fiction-checks block day "
                     "one%s)" % (n_err, "" if n_err == 1 else "S",
                                 "; --strict promotes V1/V5" if strict else ""))
        return 1, lines
    if n_warn:
        lines.append("synthesis-coverage: PASS with %d WARN (advisory-first launch posture: "
                     "V1/V5 advisory for one release; --strict promotes)" % n_warn)
        return 0, lines
    lines.append("synthesis-coverage: PASS (V1-V5 clean; coverage: %s)" % (declared or "ok"))
    return 0, lines


# ---------------------------------------------------------------- self-test

def _finding(fid, severity, refs):
    return ('<!-- apodictic:finding\n{"schema":"apodictic.finding.v1","id":"%s","mechanism":"m",'
            '"severity":"%s","confidence":"HIGH","evidence_refs":%s,"fix_class":"x",'
            '"risk_if_fixed":"y"}\n-->' % (fid, severity, json.dumps(refs)))


_GREEN_ROWS = [
    ("artifact", "MyBook_Pass1_Reader_Experience_r3.md", "summary", ""),
    ("artifact", "MyBook_Pass5_Character_Audit_r3.md", "verbatim", ""),
    ("artifact", "MyBook_Findings_Ledger_r3.md", "verbatim", ""),
    ("artifact", "MyBook_Contract_r3.md", "verbatim", ""),
    ("artifact", "MyBook_Audit_Invocation_Log_r3.md", "summary", ""),
    ("span", "Ch 3 (sc. 7-8)", "in-context", ""),
    ("span", "Ch 12 (sc. 30-31)", "in-context", ""),
    ("span", "Ch 1-2", "outside-active-context", ""),
    ("span", "Ch 4-11", "outside-active-context", ""),
]


def _table(rows):
    out = ["| kind | id | status | annotations |", "|------|----|--------|-------------|"]
    for k, i, s, a in rows:
        out.append("| %s | %s | %s | %s |" % (k, i, s, a))
    return "\n".join(out)


def _letter(mode="hybrid", marker="ok", rows=_GREEN_ROWS, short_extra="", note_rows=None,
            util_note=None, extra_tail=""):
    prov = SENT_DECLARED if mode == "single-agent" else SENT_DISPATCH
    span_prose = ("full manuscript nominally in context (estimated context utilization %s%% "
                  "per preflight)." % util_note) if util_note is not None else \
        "In active context at letter time: the verification excerpts above."
    return "\n".join([
        "# Development Edit: MyBook",
        "### A. Author | 118,000 words | Draft 3",
        "*APODICTIC Development Editor v2 — 2026-07-01*",
        "",
        "<!-- coverage: %s -->" % marker,
        "",
        "## The Short Version",
        "",
        "The book works; targeted revision. " + short_extra,
        "",
        "## Appendix C: Framework Notes",
        "",
        "Version notes.",
        "",
        "### Synthesis Coverage",
        "",
        (MODE_SENTENCE % mode) + " " + prov,
        "",
        _table(note_rows if note_rows is not None else rows),
        "",
        span_prose,
        "",
        "If you want broader synthesis-time contact with the text, request more verification "
        "excerpts or swarm mode.",
        extra_tail,
    ])


def _sidecar(mode="hybrid", coverage="ok", rows=_GREEN_ROWS, vec="auto", util=None,
             manifest_base="MyBook_Synthesis_Read_Manifest_r3.md"):
    arts = [r for r in rows if r[0] == "artifact"]
    spans = [r for r in rows if r[0] == "span"]
    n_in = sum(1 for r in spans if r[2] == "in-context")
    obj = {
        "last_session": {"execution_mode": mode},
        "synthesis_coverage": {
            "provenance": "declared" if mode == "single-agent" else "dispatch-derived",
            "execution_mode": mode,
            "coverage": coverage,
            "manifest": "runs/x/" + manifest_base,
            "artifacts_verbatim": sum(1 for r in arts if r[2] == "verbatim"),
            "artifacts_summary": sum(1 for r in arts if r[2] == "summary"),
            "artifacts_absent": sum(1 for r in arts if r[2] == "absent"),
            "spans_outside_active_context": sorted(
                r[1] for r in spans if r[2] == "outside-active-context"),
            "verification_excerpt_count": (None if mode == "single-agent" else n_in)
            if vec == "auto" else vec,
            "estimated_context_utilization": util,
        },
    }
    return json.dumps(obj, indent=2)


def _write_run(d, letter=None, manifest_rows=_GREEN_ROWS, sidecar=None, ledger=None,
               manifest_name="MyBook_Synthesis_Read_Manifest_r3.md", extra_files=(),
               letter_name="MyBook_Core_DE_Synthesis_r3.md"):
    files = {
        "MyBook_Pass1_Reader_Experience_r3.md": "pass 1\n",
        "MyBook_Pass5_Character_Audit_r3.md": "pass 5\n",
        "MyBook_Contract_r3.md": "contract\n",
        "MyBook_Audit_Invocation_Log_r3.md": "audit log\n",
        "MyBook_Findings_Ledger_r3.md": ledger if ledger is not None else (
            "## Ledger\n%s\n%s\n" % (_finding("F-P5-01", "Must-Fix", ["Ch 12"]),
                                     _finding("F-P1-02", "Should-Fix", ["Ch 3"]))),
        letter_name: letter if letter is not None else _letter(),
    }
    if manifest_rows is not None:
        files[manifest_name] = "# Synthesis Read Manifest\n\n" + _table(manifest_rows) + "\n"
    for name, content in extra_files:
        files[name] = content
    for name, content in files.items():
        with open(os.path.join(d, name), "w", encoding="utf-8", newline="") as fh:
            fh.write(content)
    with open(os.path.join(d, "Diagnostic_State.meta.json"), "w", encoding="utf-8",
              newline="") as fh:
        fh.write(sidecar if sidecar is not None else _sidecar())


def run_self_test():
    import shutil
    import tempfile
    rc = {"v": 0}
    made = []

    def chk(name, cond):
        print("  %s: %s" % (name, "OK" if cond else "FAIL"))
        if not cond:
            rc["v"] = 1

    def build(**kw):
        d = tempfile.mkdtemp()
        made.append(d)
        _write_run(d, **kw)
        return d

    def out_has(lines, token):
        return any(token in ln for ln in lines)

    # 1-2. green hybrid dispatch-derived run — clean pass, default and --strict
    d = build()
    code, lines = check_run_folder(d)
    chk("green_hybrid_pass", code == 0 and out_has(lines, "PASS (V1-V5 clean")
        and not out_has(lines, "WARN"))
    chk("green_hybrid_strict_pass", check_run_folder(d, strict=True)[0] == 0)

    # 3. no letter -> no coverage obligation
    d = build()
    os.remove(os.path.join(d, "MyBook_Core_DE_Synthesis_r3.md"))
    os.remove(os.path.join(d, "MyBook_Synthesis_Read_Manifest_r3.md"))
    code, lines = check_run_folder(d)
    chk("no_letter_no_obligation", code == 0 and out_has(lines, "no coverage obligation"))

    # 4. missing manifest -> V1 advisory (WARN, exit 0); --strict promotes to exit 1
    d = build(manifest_rows=None)
    code, lines = check_run_folder(d)
    chk("missing_manifest_v1_warn", code == 0 and out_has(lines, "WARN V1"))
    chk("missing_manifest_strict_fails", check_run_folder(d, strict=True)[0] == 1)

    # 5. hostile: a lookalike Draft manifest does NOT satisfy V1 (exact-name resolution)
    d = build(manifest_rows=None,
              extra_files=[("MyBook_Synthesis_Read_Manifest_Draft_r3.md",
                            "# draft\n\n" + _table(_GREEN_ROWS) + "\n")])
    code, lines = check_run_folder(d)
    chk("draft_lookalike_rejected", code == 0 and out_has(lines, "WARN V1")
        and out_has(lines, "lookalike"))

    # 6. shrunk denominator: on-disk artifact with no row anywhere -> V2 ERROR
    shrunk = [r for r in _GREEN_ROWS if r[1] != "MyBook_Pass5_Character_Audit_r3.md"]
    d = build(manifest_rows=shrunk, letter=_letter(note_rows=shrunk),
              sidecar=_sidecar(rows=shrunk))
    code, lines = check_run_folder(d)
    chk("shrunk_denominator_v2", code == 1 and out_has(lines, "ERROR V2")
        and out_has(lines, "cannot shrink"))

    # 7. padded denominator: a row naming a file not on disk -> V2 ERROR
    padded = _GREEN_ROWS + [("artifact", "MyBook_Pass8_Reveal_Economy_r3.md", "verbatim", "")]
    d = build(manifest_rows=padded, letter=_letter(note_rows=padded),
              sidecar=_sidecar(rows=padded))
    code, lines = check_run_folder(d)
    chk("padded_denominator_v2", code == 1 and out_has(lines, "ERROR V2")
        and out_has(lines, "cannot pad"))

    # 8. self-reported fiction: the note table claims verbatim where the manifest says summary
    lied = [("artifact", "MyBook_Pass1_Reader_Experience_r3.md", "verbatim", "")] + _GREEN_ROWS[1:]
    d = build(letter=_letter(note_rows=lied))
    code, lines = check_run_folder(d)
    chk("note_fiction_v3", code == 1 and out_has(lines, "ERROR V3")
        and out_has(lines, "exact projection"))

    # 9. sidecar tally mismatch -> V3
    sc = json.loads(_sidecar())
    sc["synthesis_coverage"]["artifacts_summary"] = 1
    d = build(sidecar=json.dumps(sc))
    code, lines = check_run_folder(d)
    chk("sidecar_tally_v3", code == 1 and out_has(lines, "ERROR V3")
        and out_has(lines, "artifacts_summary"))

    # 10. marker != sidecar coverage -> V3
    d = build(letter=_letter(marker="degraded"))
    code, lines = check_run_folder(d)
    chk("marker_mismatch_v3", code == 1 and out_has(lines, "ERROR V3")
        and out_has(lines, "one declaration"))

    # 11. duplicate marker -> V3
    d = build(letter=_letter(extra_tail="\n<!-- coverage: ok -->"))
    code, lines = check_run_folder(d)
    chk("duplicate_marker_v3", code == 1 and out_has(lines, "ERROR V3")
        and out_has(lines, "2 coverage markers"))

    # 12. provenance laundering: swarm + declared -> V4 ERROR
    sc = json.loads(_sidecar(mode="swarm"))
    sc["synthesis_coverage"]["provenance"] = "declared"
    d = build(letter=_letter(mode="swarm"), sidecar=json.dumps(sc))
    code, lines = check_run_folder(d)
    chk("provenance_laundering_v4", code == 1 and out_has(lines, "ERROR V4")
        and out_has(lines, "cheap lie"))

    # 13. single-agent green: declared + pinned sentence + utilization + full-manuscript span
    single_rows = [r for r in _GREEN_ROWS if r[0] == "artifact"] + \
        [("span", "full manuscript", "in-context", "")]
    d = build(manifest_rows=single_rows,
              letter=_letter(mode="single-agent", rows=single_rows, util_note="45"),
              sidecar=_sidecar(mode="single-agent", rows=single_rows, util=45))
    code, lines = check_run_folder(d)
    chk("single_agent_green", code == 0 and out_has(lines, "PASS (V1-V5 clean")
        and not out_has(lines, "WARN"))
    chk("single_agent_green_strict", check_run_folder(d, strict=True)[0] == 0)

    # 14. single-agent claiming dispatch-derived -> V4
    sc = json.loads(_sidecar(mode="single-agent", rows=single_rows, util=45))
    sc["synthesis_coverage"]["provenance"] = "dispatch-derived"
    d = build(manifest_rows=single_rows,
              letter=_letter(mode="single-agent", rows=single_rows, util_note="45"),
              sidecar=json.dumps(sc))
    code, lines = check_run_folder(d)
    chk("single_dispatch_claim_v4", code == 1 and out_has(lines, "ERROR V4"))

    # 15. D3: utilization above the threshold with marker ok -> V5 advisory; strict promotes
    d = build(manifest_rows=single_rows,
              letter=_letter(mode="single-agent", rows=single_rows, util_note="75"),
              sidecar=_sidecar(mode="single-agent", rows=single_rows, util=75))
    code, lines = check_run_folder(d)
    chk("d3_utilization_v5_warn", code == 0 and out_has(lines, "WARN V5")
        and out_has(lines, "D3"))
    chk("d3_utilization_strict_fails", check_run_folder(d, strict=True)[0] == 1)

    # 16. degraded-and-disclosed (fixture M1-2 letter A): absent row + degraded marker +
    #     pinned Short Version sentence -> clean PASS even under --strict
    deg_rows = [("artifact", "MyBook_Pass1_Reader_Experience_r3.md", "summary", ""),
                ("artifact", "MyBook_Pass5_Character_Audit_r3.md", "verbatim", ""),
                ("artifact", "MyBook_Findings_Ledger_r3.md", "verbatim", ""),
                ("artifact", "MyBook_Contract_r3.md", "verbatim", ""),
                ("artifact", "MyBook_Audit_Invocation_Log_r3.md", "summary", ""),
                ("artifact", "MyBook_Pass8_Reveal_Economy_r3.md", "absent", "")] + \
        [r for r in _GREEN_ROWS if r[0] == "span"]
    deg_extra = [("MyBook_Pass8_Reveal_Economy_r3.md", "pass 8\n")]
    d = build(manifest_rows=deg_rows, extra_files=deg_extra,
              letter=_letter(marker="degraded", rows=deg_rows, short_extra=SENT_DEGRADED),
              sidecar=_sidecar(coverage="degraded", rows=deg_rows))
    code, lines = check_run_folder(d, strict=True)
    chk("degraded_disclosed_pass", code == 0 and out_has(lines, "coverage: degraded"))

    # 17. masking (fixture M1-2 letter B): same run, marker + sidecar say ok -> V5 fires
    d = build(manifest_rows=deg_rows, extra_files=deg_extra,
              letter=_letter(marker="ok", rows=deg_rows, short_extra=SENT_DEGRADED),
              sidecar=_sidecar(coverage="ok", rows=deg_rows))
    code, lines = check_run_folder(d)
    chk("masking_v5_warn", code == 0 and out_has(lines, "WARN V5")
        and out_has(lines, "masking fails louder"))
    chk("masking_v5_strict_fails", check_run_folder(d, strict=True)[0] == 1)

    # 18. degraded declared but the pinned Short Version sentence missing -> V5
    d = build(manifest_rows=deg_rows, extra_files=deg_extra,
              letter=_letter(marker="degraded", rows=deg_rows),
              sidecar=_sidecar(coverage="degraded", rows=deg_rows))
    code, lines = check_run_folder(d)
    chk("degraded_missing_sentence_v5", code == 0 and out_has(lines, "WARN V5")
        and out_has(lines, "Short Version"))

    # 19. D2: a Must-Fix finding with no verbatim origin row and no matching excerpt
    d2_rows = [("artifact", "MyBook_Pass1_Reader_Experience_r3.md", "summary", ""),
               ("artifact", "MyBook_Pass5_Character_Audit_r3.md", "summary", ""),
               ("artifact", "MyBook_Findings_Ledger_r3.md", "verbatim", ""),
               ("artifact", "MyBook_Contract_r3.md", "verbatim", ""),
               ("artifact", "MyBook_Audit_Invocation_Log_r3.md", "summary", "")] + \
        [r for r in _GREEN_ROWS if r[0] == "span"]
    d = build(manifest_rows=d2_rows, letter=_letter(rows=d2_rows),
              sidecar=_sidecar(rows=d2_rows),
              ledger="## Ledger\n%s\n" % _finding("F-P5-01", "Must-Fix", ["Ch 22"]))
    code, lines = check_run_folder(d)
    chk("d2_uncovered_v5", code == 0 and out_has(lines, "WARN V5") and out_has(lines, "D2"))

    # 20. D2 unevaluable refs are reported, never fired
    d = build(ledger="## Ledger\n%s\n%s\n"
                     % (_finding("F-P5-01", "Must-Fix", ["Ch 12"]),
                        _finding("F-P1-02", "Should-Fix", ["the middle section"])))
    code, lines = check_run_folder(d)
    chk("d2_unevaluable_not_fired", code == 0 and out_has(lines, "unevaluable")
        and not out_has(lines, "WARN V5"))

    # 21. D4: zero excerpts + a Must-Fix in a multi-agent run -> V5
    d4_rows = [r for r in _GREEN_ROWS if r[0] == "artifact"] + \
        [("span", "Ch 1-24", "outside-active-context", "")]
    d = build(manifest_rows=d4_rows, letter=_letter(rows=d4_rows),
              sidecar=_sidecar(rows=d4_rows))
    code, lines = check_run_folder(d)
    chk("d4_zero_excerpts_v5", code == 0 and out_has(lines, "WARN V5") and out_has(lines, "D4"))

    # 22. bare-string sidecar object (malformed-but-valid JSON) -> V3 ERROR
    sc = json.loads(_sidecar())
    sc["synthesis_coverage"] = "all good"
    d = build(sidecar=json.dumps(sc))
    code, lines = check_run_folder(d)
    chk("bare_string_sidecar_v3", code == 1 and out_has(lines, "ERROR V3")
        and out_has(lines, "bare string"))

    # 23. template-fresh stub reads as absent -> V1 advisory, not a V3 fiction
    sc = json.loads(_sidecar())
    sc["synthesis_coverage"] = {"provenance": "", "execution_mode": "", "coverage": "",
                                "manifest": "", "artifacts_verbatim": 0, "artifacts_summary": 0,
                                "artifacts_absent": 0, "spans_outside_active_context": [],
                                "verification_excerpt_count": None,
                                "estimated_context_utilization": None}
    d = build(sidecar=json.dumps(sc))
    code, lines = check_run_folder(d)
    chk("stub_sidecar_v1", code == 0 and out_has(lines, "WARN V1")
        and out_has(lines, "template stub") and not out_has(lines, "ERROR"))

    # 24. empty manifest (header only) -> V2 (denominator unmanifested + no span rows)
    d = build(manifest_rows=[])
    code, lines = check_run_folder(d)
    chk("empty_manifest_v2", code == 1 and out_has(lines, "ERROR V2")
        and out_has(lines, "span rows"))

    # 25. unknown annotation content -> V3 parse FAIL, never silently ignored
    bad = [("artifact", "MyBook_Pass1_Reader_Experience_r3.md", "summary", "regrounded: false")]\
        + _GREEN_ROWS[1:]
    d = build(manifest_rows=bad)
    code, lines = check_run_folder(d)
    chk("bad_annotation_v3", code == 1 and out_has(lines, "ERROR V3")
        and out_has(lines, "unknown annotation"))

    # 26. the reserved M2 annotation parses today (encode the field now, always false in M1)
    reg = [("artifact", "MyBook_Pass1_Reader_Experience_r3.md", "summary", "regrounded: true")]\
        + _GREEN_ROWS[1:]
    d = build(manifest_rows=reg, letter=_letter(note_rows=reg), sidecar=_sidecar(rows=reg))
    code, lines = check_run_folder(d)
    chk("regrounded_annotation_wellformed", code == 0 and out_has(lines, "PASS (V1-V5 clean"))

    # 27. unknown status -> V3 parse FAIL
    bad = [("artifact", "MyBook_Pass1_Reader_Experience_r3.md", "read-ish", "")] + _GREEN_ROWS[1:]
    d = build(manifest_rows=bad)
    code, lines = check_run_folder(d)
    chk("unknown_status_v3", code == 1 and out_has(lines, "ERROR V3")
        and out_has(lines, "unknown status"))

    # 28. a marker quoted inside a code fence is a documentation example, not a declaration
    fenced = _letter().replace("<!-- coverage: ok -->",
                               "```\n<!-- coverage: ok -->\n```")
    d = build(letter=fenced)
    code, lines = check_run_folder(d)
    chk("fenced_marker_not_honored", code == 0 and out_has(lines, "WARN V1")
        and out_has(lines, "marker missing"))

    # 29. marker present but misplaced -> V5 placement (advisory)
    misplaced = _letter().replace("<!-- coverage: ok -->\n\n## The Short Version",
                                  "## The Short Version\n\n<!-- coverage: ok -->")
    d = build(letter=misplaced)
    code, lines = check_run_folder(d)
    chk("misplaced_marker_v5", code == 0 and out_has(lines, "WARN V5")
        and out_has(lines, "placement"))

    # 30. sidecar object missing entirely -> V1 advisory; reconciliation skipped, no crash
    sc = json.loads(_sidecar())
    del sc["synthesis_coverage"]
    d = build(sidecar=json.dumps(sc))
    code, lines = check_run_folder(d)
    chk("missing_sidecar_object_v1", code == 0 and out_has(lines, "WARN V1")
        and out_has(lines, "object missing"))

    # 31. pinned mode/provenance sentences enforced verbatim -> V4
    noned = _letter().replace(MODE_SENTENCE % "hybrid", "This letter used hybrid mode.")
    d = build(letter=noned)
    code, lines = check_run_folder(d)
    chk("mode_sentence_missing_v4", code == 1 and out_has(lines, "ERROR V4")
        and out_has(lines, "mode sentence"))

    # 32. multi-agent verification_excerpt_count drift -> V3
    sc = json.loads(_sidecar())
    sc["synthesis_coverage"]["verification_excerpt_count"] = 7
    d = build(sidecar=json.dumps(sc))
    code, lines = check_run_folder(d)
    chk("excerpt_count_drift_v3", code == 1 and out_has(lines, "ERROR V3")
        and out_has(lines, "verification_excerpt_count"))

    # 33. sidecar manifest field must name the resolved manifest (basename string compare)
    sc = json.loads(_sidecar(manifest_base="Other_Manifest.md"))
    d = build(sidecar=json.dumps(sc))
    code, lines = check_run_folder(d)
    chk("sidecar_manifest_name_v3", code == 1 and out_has(lines, "ERROR V3")
        and out_has(lines, "basename compare"))

    # 34. multi-agent utilization must be null -> V3
    sc = json.loads(_sidecar())
    sc["synthesis_coverage"]["estimated_context_utilization"] = 40
    d = build(sidecar=json.dumps(sc))
    code, lines = check_run_folder(d)
    chk("multi_agent_utilization_v3", code == 1 and out_has(lines, "ERROR V3")
        and out_has(lines, "single-agent only"))

    for d in made:
        shutil.rmtree(d, ignore_errors=True)
    print("Self-test: PASS" if rc["v"] == 0 else "Self-test: FAIL")
    return rc["v"]


def main(argv):
    if "--self-test" in argv:
        return run_self_test()
    args = [a for a in argv[1:] if a != "synthesis-coverage"]
    strict = "--strict" in args
    paths = [a for a in args if not a.startswith("--")]
    if len(paths) != 1 or not os.path.isdir(paths[0]):
        print("Usage: synthesis_coverage.py synthesis-coverage <run_folder> [--strict] | --self-test")
        return 2
    code, lines = check_run_folder(paths[0], strict=strict)
    for ln in lines:
        print(ln)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
