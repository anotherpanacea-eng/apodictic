#!/usr/bin/env python3
"""dispatch-record — dispatch observability validator (Model-Capacity Exploitation M1).

`validate.sh dispatch-record <run_folder> [--strict]` shells out here. A run that dispatched
delegated agents records WHICH model each dispatched step was issued to in the additive
`dispatch_log` sidecar array (Diagnostic_State.meta.json) — the single join key between model
identity and every outcome signal the framework already writes to disk. This validator is the
advisory reconciler for that record.

PROVENANCE HONESTY (pinned, binding on every consumer — schema $comment, docs, this validator,
and any future M2/M3): a `dispatch-derived` entry attests the dispatch INSTRUCTION — the model
parameter the parent requested — it is PARENT-REQUESTED, NOT PLATFORM-VERIFIED. No host API
attests which model actually served the subagent. This is deliberately weaker than
synthesis_coverage's dispatch-derived manifest (whose rows are checkable file paths reconciled by
V2-V4); dispatch_log has no equivalent reconciliation substrate, and neither this validator nor
its docs claims one.

Checks (spec §M1.2):

  R1 presence         a run folder with pass artifacts should carry a `dispatch_log` with >= 1
                      entry. GRANDFATHER: the key being ABSENT is the pre-adoption marker
                      (silent PASS — same move as synthesis_coverage's unfilled-stub-reads-as-
                      absent). A present-but-EMPTY [] is a post-adoption recording failure and
                      FIRES (WARN default / FAIL under --strict). Advisory-first.
  R2 coverage         bidirectional-with-asymmetry, reconciled per step kind, against the
                      pass-artifact glob family (`_Pass[N]_`) + synthesis-letter globs
                      (`*_Core_DE_Synthesis_*` / `*_Full_DE_Synthesis_*` — the detection the
                      annotated-manuscript offer uses, run-synthesis.md:534). Satisfaction map:
                      `pass<N>` -> Pass N; `pass0+1` -> BOTH Pass0 and Pass1; `all-passes` ->
                      every pass artifact (and is EXCLUSIVE — may not coexist with pass<N>/
                      pass0+1); `synthesis` -> the letter. Deferred-extension ids
                      (audit:*/prerequisite:*/refutation) are recorded-but-not-reconciled (R2
                      skips them both directions). DIRECTION ASYMMETRY: an enumerated artifact
                      with no satisfying entry = FAIL under --strict, WARN otherwise (the record
                      can't shrink); an entry with no matching artifact = WARN with a note,
                      never FAIL (a dispatched-then-failed subagent is a legitimate, informative
                      record). BOUNDARY: dispatch-record CONSUMES the enumeration; filename
                      grammar stays artifact-names' concern (no second runlabel parser).
  R3 tag vocabulary   `model_tag` must appear in the model-tag table parsed from
                      output-structure.md (SSoT-by-reference, the pass-header-reads-§3 precedent),
                      OR be the literal `unknown` (the documented derivation fallback,
                      output-structure.md:183 — a sanctioned PASS, never a WARN). Any other tag =
                      WARN naming the table as the fix. FAIL-LOUD PARSE FLOOR: if the table parses
                      to ZERO rows, exit 2 with `model-tag-table-unparseable` — never a vacuous
                      accept-everything degrade.
  R4 shape            `execution_mode` in {single-agent, sequential, hybrid, swarm};
                      `provenance` in {dispatch-derived, declared}; `seq` strictly increasing;
                      malformed entries (bare string, missing required field, bad enum,
                      duplicate seq) = FAIL; unknown step kind (outside v1 grammar + deferred-
                      extension grammar) = WARN. NO mode-based provenance FAIL: provenance tracks
                      the host's PER-ENTRY dispatch capability, not the run's mode — a no-shell
                      host legitimately records all-`declared` entries under
                      `execution_mode: sequential`.
  R5 escalation       cross-check using only the log + `last_session.execution_mode` (updated on
                      a confirmed switch, run-core.md:315/321): (a) the execution_mode values in
                      seq order may change AT MOST ONCE (the Mid-Run Escalation Check runs once,
                      at the Tier-1/2 seam — a thrashing log is flagged); (b) when
                      last_session.execution_mode is present, the FINAL entry's execution_mode
                      must equal it (a post-escalation entry carrying the stale pre-switch mode is
                      flagged). WARN by default for one release, --strict promotes (same adoption
                      ramp as R1).

  --report <project_dir>   read-only cross-run scan (fold S-3). Prints, gating nothing: runs
                      scanned; per-model-tag dispatch tallies from every dispatch_log; and the M2
                      DEMAND-SIGNAL line — the count of `quality_risk_override` records
                      (run-core.md:171 run-metadata token + the :175 override-marker syntax,
                      matched via the shared override_marker helper, meta-lint M5) and how many
                      carry a budget-flavored rationale. Nothing else reads quality_risk_override
                      across runs; without this the M2 trigger would be recorded-but-invisible
                      (the CR-6 detectability discipline, docs/adaptive-mode-escalation.md).

LAUNCH POSTURE: R2/R3/R4 blocking shapes are ERROR (exit 1) once fired; R1/R5 are ADVISORY-FIRST
for one release (WARN at exit 0, the escalation-check posture); --strict promotes R1/R5 (and the
R2 shrink direction) to ERROR. A zero-row model-tag-table parse is a hard exit 2 regardless.

Usage:
  dispatch_record.py dispatch-record <run_folder> [--strict]
  dispatch_record.py dispatch-record --report <project_dir>
  dispatch_record.py --self-test

Exit: 0 clean / WARN-only, 1 ERROR (or advisory WARN under --strict), 2 usage / parse floor.
"""

import glob
import json
import os
import re
import sys

try:
    from override_marker import override_payloads, strip_code_spans
except ImportError:  # degraded: no override scan (in-repo the shared helper always ships)
    def override_payloads(body, slug):
        return []

    def strip_code_spans(body):
        return body

# ---------------------------------------------------------------- pinned vocabulary

_MODES = ("single-agent", "sequential", "hybrid", "swarm")
_PROVENANCES = ("dispatch-derived", "declared")

# v1 step grammar (exactly what M1 wires): pass<N> | pass0+1 | synthesis | all-passes.
_STEP_PASSN_RE = re.compile(r"^pass(\d+)$")
_STEP_PASS01 = "pass0+1"
_STEP_SYNTHESIS = "synthesis"
_STEP_ALLPASSES = "all-passes"
# Deferred extension (accepted-if-recorded, NOT reconciled by R2): audit:<id> | prerequisite:<id>
# | refutation. Recording sentences for these live at seams M1 does not touch.
_STEP_DEFERRED_PREFIXES = ("audit:", "prerequisite:")
_STEP_DEFERRED_EXACT = ("refutation",)

_UNKNOWN_TAG = "unknown"   # the documented derivation fallback (output-structure.md:183) — PASS

# Disk enumeration (spec §M1.2 denominator): pass-artifact glob family + synthesis-letter globs.
# We CONSUME this enumeration; the runlabel/filename grammar stays artifact-names' concern.
_PASS_RE = re.compile(r"_Pass(\d+)_")
_LETTER_GLOBS = ("*_Core_DE_Synthesis_*.md", "*_Full_DE_Synthesis_*.md")

# Model-tag table (output-structure.md): a `| Model family | Tag |` pipe table whose Tag cell is a
# backticked token. SSoT-by-reference — parsed at runtime, never a hardcoded constant that drifts.
_TAG_CELL_RE = re.compile(r"`([A-Za-z0-9._-]+)`")

# --report demand signal: the quality_risk_override records. Two legitimate shapes —
#   (a) the run-metadata / intake-notes token   `quality_risk_override: Q[n] — <rationale>`
#   (b) the override marker                       `<!-- override: quality-risk-Q[1-5] — <why> -->`
# The marker form is matched via override_marker (M5-clean, no bare/compiled marker scan here). The
# metadata-token form is a plain field read, not an override-marker scan, so it does not trip M5.
_QRO_TOKEN_RE = re.compile(r"quality_risk_override:\s*Q\d+\s*[—–-]\s*(.+)", re.IGNORECASE)
_BUDGET_RE = re.compile(r"\b(budget|cost|token|expensive|cheap|afford|spend|price|pric)\w*",
                        re.IGNORECASE)
# cost_floor_override records (CR-6 detectability): a run-metadata token sibling of _QRO_TOKEN_RE.
# The marker form is counted via the shared override_marker helper (M5-clean, over the three
# cost-floor-* slugs); this token form is a plain field read (not an override-marker scan, so it does
# not trip M5), code-span stripped so a documentation example is not miscounted.
_CFO_TOKEN_RE = re.compile(
    r"cost_floor_override:\s*(?:single-agent|sequential|hybrid)"
    r"(?:\s*;\s*context_tier:\s*(?:standard|large))?"
    r"\s*[—–-]\s*(.+)", re.IGNORECASE)
_CFO_SLUGS = ("cost-floor-single-agent", "cost-floor-sequential", "cost-floor-hybrid")


# ---------------------------------------------------------------- io helpers

def _read(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except (OSError, UnicodeDecodeError):
        return None


def _load_sidecar(run_folder):
    """Find + parse Diagnostic_State.meta.json at or above run_folder (bounded walk). Returns
    (obj_or_None, path_or_None, parse_error_or_None)."""
    d = os.path.abspath(run_folder if os.path.isdir(run_folder) else os.path.dirname(run_folder))
    for _ in range(4):
        p = os.path.join(d, "Diagnostic_State.meta.json")
        if os.path.exists(p):
            raw = _read(p)
            if raw is None:
                return None, p, "unreadable"
            try:
                return json.loads(raw), p, None
            except (ValueError, json.JSONDecodeError) as exc:
                return None, p, str(exc)
        d = os.path.dirname(d)
    return None, None, None


def _find_output_structure(start_dir):
    """Locate output-structure.md (SSoT for the model-tag table). A run-folder-LOCAL copy takes
    precedence (self-test fixtures ship their own table; a real run folder never carries one, so
    this falls through to the script's reference tree). Then the script's own reference tree, then
    a broader upward walk from the run folder."""
    candidates = []
    d = os.path.abspath(start_dir if os.path.isdir(start_dir) else os.path.dirname(start_dir))
    # run-folder-local first (fixtures)
    for _ in range(4):
        candidates.append(os.path.join(d, "output-structure.md"))
        d = os.path.dirname(d)
        if d == os.path.dirname(d):
            break
    # the script's own shipped reference tree (canonical SSoT for real runs)
    here = os.path.dirname(os.path.abspath(__file__))
    candidates.append(os.path.join(here, "..", "skills", "core-editor", "references",
                                   "output-structure.md"))
    candidates.append(os.path.join(here, "..", "plugins", "apodictic", "skills", "core-editor",
                                   "references", "output-structure.md"))
    # a broader upward walk (installed layouts)
    d = os.path.abspath(start_dir if os.path.isdir(start_dir) else os.path.dirname(start_dir))
    for _ in range(8):
        candidates.append(os.path.join(d, "plugins", "apodictic", "skills", "core-editor",
                                       "references", "output-structure.md"))
        d = os.path.dirname(d)
        if d == os.path.dirname(d):
            break
    for c in candidates:
        if os.path.exists(c):
            return os.path.abspath(c)
    return None


# ---------------------------------------------------------------- model-tag table parse

def parse_model_tag_table(output_structure_text):
    """Extract the sanctioned model tags from the output-structure.md `| Model family | Tag |`
    table. Returns a set of tags (backticked Tag cells). The literal `unknown` is NOT required in
    the table — R3 accepts it as a separate sanctioned value. Callers must treat an EMPTY return
    as the fail-loud floor (exit 2), never as accept-everything."""
    tags = set()
    in_table = False
    header_seen = False
    for raw in (output_structure_text or "").split("\n"):
        line = raw.strip()
        if not line.startswith("|"):
            if in_table and header_seen:
                # a blank / non-pipe line ends the table we were reading
                in_table = False
                header_seen = False
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        low = [c.lower() for c in cells]
        # header row of the model-tag table: `| Model family | Tag |`
        if "tag" in low and any("model" in c for c in low):
            in_table = True
            header_seen = True
            continue
        if not in_table:
            continue
        # separator row (---|---) — skip, stay in table
        if all(re.fullmatch(r"[-: ]*", c) for c in cells) and any("-" in c for c in cells):
            continue
        # data row: the last cell carries the backticked tag
        m = _TAG_CELL_RE.search(cells[-1]) if cells else None
        if m:
            tags.add(m.group(1))
    return tags


# ---------------------------------------------------------------- disk enumeration (R2 denominator)

def enumerate_pass_numbers(run_folder):
    """Set of pass NUMBERS present as artifacts on disk (`_Pass[N]_`). Consumes artifact-names'
    glob family; does not parse the runlabel."""
    nums = set()
    for p in glob.glob(os.path.join(run_folder, "*.md")):
        m = _PASS_RE.search(os.path.basename(p))
        if m:
            nums.add(int(m.group(1)))
    return nums


def has_letter(run_folder):
    for g in _LETTER_GLOBS:
        if glob.glob(os.path.join(run_folder, g)):
            return True
    return False


# ---------------------------------------------------------------- step classification

def classify_step(step):
    """Return one of: 'passN' (with the int in a tuple), 'pass0+1', 'synthesis', 'all-passes',
    'deferred', 'unknown'. Never raises on a non-string (caller shape-checks first)."""
    if not isinstance(step, str):
        return ("unknown", None)
    if step == _STEP_PASS01:
        return ("pass0+1", None)
    if step == _STEP_SYNTHESIS:
        return ("synthesis", None)
    if step == _STEP_ALLPASSES:
        return ("all-passes", None)
    m = _STEP_PASSN_RE.match(step)
    if m:
        return ("passN", int(m.group(1)))
    if step in _STEP_DEFERRED_EXACT or any(step.startswith(p) for p in _STEP_DEFERRED_PREFIXES):
        return ("deferred", None)
    return ("unknown", None)


# ---------------------------------------------------------------- the validator

class Result(object):
    def __init__(self):
        self.errors = []    # (check, msg) — ERROR (exit 1)
        self.warns = []     # (check, msg) — advisory (exit 0 unless --strict promotes)

    def err(self, check, msg):
        self.errors.append((check, msg))

    def warn(self, check, msg):
        self.warns.append((check, msg))


# checks whose WARNs promote to ERROR under --strict (adoption-ramp: R1, R5, and the R2 shrink
# direction). R2/R3/R4 blocking shapes are already errors.
_ADVISORY_PROMOTE = ("R1", "R5", "R2-shrink")


def check_dispatch_record(run_folder, strict=False):
    """Returns (exit_code, lines). exit_code: 0 clean/WARN-only, 1 ERROR (or promoted advisory
    under --strict), 2 the model-tag-table parse floor."""
    lines = []
    res = Result()

    if not os.path.isdir(run_folder):
        return 2, ["Usage: dispatch_record.py dispatch-record <run_folder> [--strict]",
                   "  (not a directory: %s)" % run_folder]

    sidecar, sc_path, parse_err = _load_sidecar(run_folder)
    if parse_err:
        # a malformed sidecar is a hard shape error (not a silent pass)
        return 1, ["dispatch-record: ERROR sidecar — Diagnostic_State.meta.json unparseable "
                   "(%s): %s" % (sc_path, parse_err)]

    pass_nums = enumerate_pass_numbers(run_folder)
    letter = has_letter(run_folder)
    has_artifacts = bool(pass_nums) or letter

    # ---- R1 presence (grandfather) -------------------------------------------------------------
    if sidecar is None or "dispatch_log" not in sidecar:
        # key absent = pre-adoption grandfather -> silent PASS (no obligation)
        lines.append("dispatch-record: PASS (no dispatch_log — pre-adoption grandfather; the "
                     "key's absence is the grandfather marker)")
        return 0, lines

    dlog = sidecar["dispatch_log"]
    if not isinstance(dlog, list):
        return 1, ["dispatch-record: ERROR R4 — dispatch_log must be an array, got %s"
                   % type(dlog).__name__]

    if len(dlog) == 0:
        # present-but-[] = post-adoption recording failure (NOT a grandfather)
        if has_artifacts:
            res.warn("R1", "dispatch_log is present but EMPTY — a post-adoption recording "
                           "failure (an empty array is never a grandfather; the key's ABSENCE "
                           "is). Pass artifacts exist but no dispatch was recorded.")
        else:
            res.warn("R1", "dispatch_log is present but EMPTY and no pass artifacts are on disk.")

    # ---- R4 shape (per entry) + R3 tag vocabulary ---------------------------------------------
    # Parse the model-tag table ONCE (fail-loud floor).
    ostruct = _find_output_structure(run_folder)
    tags = parse_model_tag_table(_read(ostruct) if ostruct else "")
    if ostruct is None:
        return 2, ["dispatch-record: EXIT 2 model-tag-table-unparseable — could not locate "
                   "output-structure.md to parse the model-tag table (SSoT-by-reference); "
                   "refusing to vacuously accept every tag"]
    if not tags:
        return 2, ["dispatch-record: EXIT 2 model-tag-table-unparseable — the model-tag table in "
                   "%s parsed to ZERO rows; refusing to degrade to accept-everything" % ostruct]

    seen_seq = []
    entries = []   # (index, entry, kind, num) for valid-shaped entries used by R2/R5
    for i, e in enumerate(dlog):
        loc = "entry[%d]" % i
        if not isinstance(e, dict):
            res.err("R4", "%s is not an object (bare value %r) — malformed entry" % (loc, e))
            continue
        # required fields
        missing = [k for k in ("seq", "step", "model_tag", "execution_mode", "provenance")
                   if k not in e]
        if missing:
            res.err("R4", "%s missing required field(s): %s" % (loc, ", ".join(missing)))
            # continue collecting other shape errors where possible, but don't use it downstream
        seq = e.get("seq")
        if not isinstance(seq, int) or isinstance(seq, bool):
            res.err("R4", "%s seq must be an integer, got %r" % (loc, seq))
        else:
            seen_seq.append(seq)
        mode = e.get("execution_mode")
        if mode not in _MODES:
            res.err("R4", "%s execution_mode %r not in %s" % (loc, mode, list(_MODES)))
        prov = e.get("provenance")
        if prov not in _PROVENANCES:
            res.err("R4", "%s provenance %r not in %s (NB: no mode-based provenance FAIL — "
                          "provenance tracks per-entry dispatch capability, not the run's mode)"
                    % (loc, prov, list(_PROVENANCES)))
        if "max_turns" in e and e["max_turns"] is not None and (
                not isinstance(e["max_turns"], int) or isinstance(e["max_turns"], bool)):
            res.err("R4", "%s max_turns must be an integer or null, got %r"
                    % (loc, e["max_turns"]))
        # step kind
        step = e.get("step")
        kind, num = classify_step(step)
        if kind == "unknown":
            res.warn("R4", "%s unknown step kind %r (outside the v1 grammar "
                           "pass<N>/pass0+1/synthesis/all-passes and the deferred extension "
                           "audit:*/prerequisite:*/refutation)" % (loc, step))
        # R3 tag vocabulary — only meaningful when model_tag is a string
        mt = e.get("model_tag")
        if isinstance(mt, str):
            if mt == _UNKNOWN_TAG:
                pass  # sanctioned PASS (output-structure.md:183) — never a WARN
            elif mt not in tags:
                res.warn("R3", "%s model_tag %r not in the output-structure.md model-tag table "
                               "(fix: add the row to the table, not the validator)" % (loc, mt))
        elif "model_tag" not in missing:
            res.err("R4", "%s model_tag must be a string, got %r" % (loc, mt))

        # record for R2/R5 only if minimally well-shaped (dict with a usable step + mode)
        if isinstance(step, str) and mode in _MODES:
            entries.append((i, e, kind, num, seq if isinstance(seq, int)
                            and not isinstance(seq, bool) else None))

    # seq strictly increasing (over the integer seqs, in list order)
    prev = None
    for i, e in enumerate(dlog):
        if isinstance(e, dict) and isinstance(e.get("seq"), int) and not isinstance(e["seq"], bool):
            s = e["seq"]
            if prev is not None and s <= prev:
                res.err("R4", "seq not strictly increasing at entry[%d]: %d after %d" % (i, s, prev))
            prev = s
    # duplicate seq
    dupes = sorted({s for s in seen_seq if seen_seq.count(s) > 1})
    for s in dupes:
        res.err("R4", "duplicate seq value %d" % s)

    # ---- R2 coverage (bidirectional-with-asymmetry) -------------------------------------------
    if len(dlog) > 0:
        _r2(entries, pass_nums, letter, res)

    # ---- R5 escalation reconciliation ---------------------------------------------------------
    _r5(entries, sidecar, res)

    # ---- assemble output ----------------------------------------------------------------------
    return _emit(res, strict, lines)


def _r2(entries, pass_nums, letter, res):
    """Reconcile the satisfaction map. entries: [(idx, entry, kind, num, seq)]."""
    has_all_passes = any(k == "all-passes" for (_, _, k, _, _) in entries)
    has_pass_entries = any(k in ("passN", "pass0+1") for (_, _, k, _, _) in entries)

    # consistency: all-passes is exclusive
    if has_all_passes and has_pass_entries:
        res.err("R2", "`all-passes` may not coexist with pass<N>/pass0+1 entries — single-agent "
                      "is one dispatch by definition (satisfaction-map exclusivity)")

    # satisfied pass numbers (disk side) from entries
    satisfied = set()
    letter_satisfied = False
    for (_, _, kind, num, _) in entries:
        if kind == "all-passes":
            satisfied |= set(pass_nums)   # satisfies every pass artifact on disk
        elif kind == "pass0+1":
            satisfied |= {0, 1}           # satisfies BOTH Pass0 and Pass1
        elif kind == "passN":
            satisfied.add(num)
        elif kind == "synthesis":
            letter_satisfied = True
        # 'deferred' / 'unknown' contribute nothing to R2 (recorded-but-not-reconciled)

    # direction A: enumerated artifact with no satisfying entry (record can't shrink)
    unsatisfied_passes = sorted(n for n in pass_nums if n not in satisfied)
    for n in unsatisfied_passes:
        res.warn("R2-shrink", "Pass %d artifact on disk has no satisfying dispatch_log entry "
                              "(the record can't shrink; FAIL under --strict)" % n)
    if letter and not letter_satisfied:
        res.warn("R2-shrink", "a synthesis letter is on disk but no `synthesis` dispatch_log "
                              "entry satisfies it (FAIL under --strict)")

    # direction B: entry with no matching artifact = WARN, never FAIL (fail-open, honest direction)
    for (idx, _, kind, num, _) in entries:
        if kind == "passN" and num not in pass_nums:
            res.warn("R2", "entry[%d] records `pass%d` but no Pass %d artifact is on disk — a "
                           "dispatched-then-failed subagent is a legitimate, informative record "
                           "(WARN, never FAIL)" % (idx, num, num))
        elif kind == "pass0+1" and not ({0, 1} & pass_nums):
            res.warn("R2", "entry[%d] records `pass0+1` but neither Pass0 nor Pass1 is on disk "
                           "(WARN, never FAIL)" % idx)
        elif kind == "synthesis" and not letter:
            res.warn("R2", "entry[%d] records `synthesis` but no synthesis letter is on disk "
                           "(WARN, never FAIL)" % idx)


def _r5(entries, sidecar, res):
    """Escalation reconciliation from the log + last_session.execution_mode."""
    # ordered modes over valid entries with an integer seq (fall back to list order)
    ordered = [e for e in entries if e[4] is not None]
    ordered.sort(key=lambda t: t[4])
    if not ordered:
        ordered = list(entries)
    modes = [e[1].get("execution_mode") for e in ordered]

    # (a) at most one transition
    transitions = sum(1 for a, b in zip(modes, modes[1:]) if a != b)
    if transitions > 1:
        res.warn("R5", "execution_mode changes %d times across the log (%s) — the Mid-Run "
                       "Escalation Check runs ONCE, at the Tier-1/2 seam; a thrashing log is "
                       "flagged (WARN, FAIL under --strict)"
                 % (transitions, " -> ".join(str(m) for m in modes)))

    # (b) final entry mode must equal last_session.execution_mode when present
    ls = sidecar.get("last_session") if isinstance(sidecar, dict) else None
    ls_mode = ls.get("execution_mode") if isinstance(ls, dict) else None
    if ls_mode and modes:
        final = modes[-1]
        if final != ls_mode:
            res.warn("R5", "the final dispatch_log entry's execution_mode (%r) != "
                           "last_session.execution_mode (%r) — a post-escalation entry carrying "
                           "the stale pre-switch mode is flagged (WARN, FAIL under --strict)"
                     % (final, ls_mode))


def _emit(res, strict, lines):
    promoted = []
    hard_errors = list(res.errors)
    surviving_warns = []
    for (check, msg) in res.warns:
        if strict and check in _ADVISORY_PROMOTE:
            promoted.append((check, msg))
        else:
            surviving_warns.append((check, msg))

    for (check, msg) in hard_errors:
        lines.append("  ERROR %s: %s" % (check, msg))
    for (check, msg) in promoted:
        lines.append("  ERROR %s (advisory, promoted by --strict): %s" % (check, msg))
    for (check, msg) in surviving_warns:
        lines.append("  WARN %s: %s" % (check, msg))

    n_err = len(hard_errors) + len(promoted)
    n_warn = len(surviving_warns)
    if n_err:
        lines.append("dispatch-record: FAIL (%d error%s, %d warn)"
                     % (n_err, "" if n_err == 1 else "s", n_warn))
        return 1, lines
    if n_warn:
        lines.append("dispatch-record: PASS with %d WARN (advisory-first: R1/R5 and the R2 shrink "
                     "direction are WARN this release; --strict promotes them)" % n_warn)
        return 0, lines
    lines.append("dispatch-record: PASS")
    return 0, lines


# ---------------------------------------------------------------- --report (cross-run, read-only)

def run_report(project_dir):
    """Read-only cross-run scan. Prints runs scanned, per-model-tag dispatch tallies, and the M2
    demand-signal line. Gates nothing (always exit 0 unless the dir is unusable)."""
    lines = []
    if not os.path.isdir(project_dir):
        return 2, ["Usage: dispatch_record.py dispatch-record --report <project_dir>",
                   "  (not a directory: %s)" % project_dir]

    # Find every run folder = any directory containing a Diagnostic_State.meta.json, plus the
    # project root itself. Read-only, one operator-named directory (no cross-project harvesting).
    sidecar_paths = []
    for dirpath, _dirnames, filenames in os.walk(project_dir):
        if "Diagnostic_State.meta.json" in filenames:
            sidecar_paths.append(os.path.join(dirpath, "Diagnostic_State.meta.json"))

    runs_scanned = 0
    tag_tally = {}
    qro_count = 0
    qro_budget = 0
    cfo_count = 0

    # quality_risk_override lives in run metadata / intake notes — scan every .md in each run
    # folder plus the sidecar's own JSON string (the run-metadata token form).
    scanned_dirs = set()
    for sc_path in sidecar_paths:
        d = os.path.dirname(sc_path)
        raw = _read(sc_path)
        obj = None
        if raw is not None:
            try:
                obj = json.loads(raw)
            except (ValueError, json.JSONDecodeError):
                obj = None
        if isinstance(obj, dict):
            runs_scanned += 1
            dlog = obj.get("dispatch_log")
            if isinstance(dlog, list):
                for e in dlog:
                    if isinstance(e, dict) and isinstance(e.get("model_tag"), str):
                        tag_tally[e["model_tag"]] = tag_tally.get(e["model_tag"], 0) + 1
        scanned_dirs.add(d)

    # demand signal: quality_risk_override records across the project's markdown + sidecars.
    md_bodies = []
    for d in scanned_dirs:
        for p in glob.glob(os.path.join(d, "*.md")):
            b = _read(p)
            if b is not None:
                md_bodies.append(b)
    for sc_path in sidecar_paths:
        b = _read(sc_path)
        if b is not None:
            md_bodies.append(b)

    for body in md_bodies:
        # (a) override-marker form — via the shared override_marker helper (M5-clean)
        for q in range(1, 6):
            for payload in override_payloads(body, "quality-risk-Q%d" % q):
                qro_count += 1
                if _BUDGET_RE.search(payload or ""):
                    qro_budget += 1
        # (b) run-metadata / intake-notes token form: `quality_risk_override: Q[n] — <rationale>`.
        # Strip code spans first (the shared SSoT, as the marker form does via override_payloads) so a
        # doc that merely QUOTES `quality_risk_override: Q3 — …` as an example is not miscounted as a
        # real declined-escalation record.
        for m in _QRO_TOKEN_RE.finditer(strip_code_spans(body)):
            qro_count += 1
            if _BUDGET_RE.search(m.group(1) or ""):
                qro_budget += 1
        # cost_floor_override records (CR-6 detectability): nothing else reads these across runs, so
        # without this line a recorded cost cap would be recorded-but-invisible. Marker form via the
        # shared override_marker helper (code spans stripped) over the three slugs; token form via
        # _CFO_TOKEN_RE over strip_code_spans, so a code-span-quoted example is not counted.
        for slug in _CFO_SLUGS:
            cfo_count += len(override_payloads(body, slug))
        cfo_count += sum(1 for _ in _CFO_TOKEN_RE.finditer(strip_code_spans(body)))

    lines.append("dispatch-record --report (read-only cross-run; gates nothing)")
    lines.append("  project: %s" % os.path.abspath(project_dir))
    lines.append("  runs scanned (Diagnostic_State.meta.json): %d" % runs_scanned)
    if tag_tally:
        lines.append("  per-model-tag dispatch tallies:")
        for tag in sorted(tag_tally):
            lines.append("    %-12s %d" % (tag, tag_tally[tag]))
    else:
        lines.append("  per-model-tag dispatch tallies: (none — no populated dispatch_log found)")
    lines.append("  M2 demand signal — quality_risk_override records: %d (of which "
                 "budget-flavored rationale: %d)" % (qro_count, qro_budget))
    lines.append("  cost_floor_override records: %d (marker + token forms; a code-span-quoted example "
                 "is not counted)" % cfo_count)
    lines.append("  (dispatch_log provenance is dispatch-derived = parent-requested, NOT "
                 "platform-verified.)")
    return 0, lines


# ---------------------------------------------------------------- self-test

def _write(path, text):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


_TABLE_MD = """# output-structure.md (fixture)

| Model family | Tag |
|-------------|-----|
| Codex 5.4 | `codex54` |
| ChatGPT o3 | `o3` |
| Gemini 3.1 | `gemini31` |
| Claude Opus 4.6 | `opus46` |
| Claude Sonnet 4.6 | `sonnet46` |
| Claude Haiku 4.5 | `haiku45` |

**Derivation:** If the model identifier is unavailable, use `unknown`.
"""

_TABLE_ZERO_MD = """# output-structure.md (no parseable table)

No model-tag table here at all.
"""


def _mk_run(tmp, name, sidecar_obj, pass_files=(), letter=False, table=True,
            table_text=None):
    """Build a run folder with a sidecar, optional pass artifacts, and the model-tag table."""
    d = os.path.join(tmp, name)
    os.makedirs(d, exist_ok=True)
    _write(os.path.join(d, "Diagnostic_State.meta.json"), json.dumps(sidecar_obj))
    for n in pass_files:
        _write(os.path.join(d, "Proj_Pass%d_Lens_2026-01-01_opus46.md" % n), "pass %d\n" % n)
    if letter:
        _write(os.path.join(d, "Proj_Core_DE_Synthesis_2026-01-01_opus46.md"),
               "letter\n<!-- coverage: ok -->\n")
    if table:
        _write(os.path.join(d, "output-structure.md"), table_text or _TABLE_MD)
    return d


def _entry(seq, step, tag="opus46", mode="hybrid", prov="dispatch-derived", max_turns=None):
    return {"seq": seq, "step": step, "model_tag": tag, "execution_mode": mode,
            "max_turns": max_turns, "provenance": prov}


def run_self_test():
    import tempfile
    rc = 0

    def chk(name, cond):
        nonlocal rc
        print("  %s: %s" % (name, "OK" if cond else "FAIL"))
        if not cond:
            rc = 1

    def run(d, strict=False):
        return check_dispatch_record(d, strict=strict)

    def has(lines, needle):
        return any(needle in ln for ln in lines)

    with tempfile.TemporaryDirectory() as tmp:
        # 1. key-absent grandfather -> silent PASS
        d = _mk_run(tmp, "grandfather", {"project": "P"}, pass_files=(1, 5), letter=True)
        code, lines = run(d)
        chk("grandfather_absent_pass", code == 0 and has(lines, "grandfather"))

        # 2. clean hybrid: pass0+1 (->Pass1), pass5, synthesis; Pass1+Pass5 on disk + letter
        side = {"last_session": {"execution_mode": "hybrid"},
                "dispatch_log": [_entry(1, "pass0+1", max_turns=32),
                                 _entry(2, "pass5"),
                                 _entry(3, "synthesis")]}
        d = _mk_run(tmp, "clean", side, pass_files=(1, 5), letter=True)
        code, lines = run(d)
        chk("clean_hybrid_pass", code == 0 and not has(lines, "WARN") and not has(lines, "ERROR"))
        code, lines = run(d, strict=True)
        chk("clean_hybrid_pass_strict", code == 0)

        # 3. present-but-[] -> R1 WARN (default), FAIL under --strict
        side = {"dispatch_log": []}
        d = _mk_run(tmp, "empty", side, pass_files=(1,), letter=True)
        code, lines = run(d)
        chk("empty_r1_warn", code == 0 and has(lines, "WARN R1"))
        code, lines = run(d, strict=True)
        chk("empty_r1_strict_fail", code == 1 and has(lines, "ERROR R1"))

        # 4. unknown-tag literal -> PASS (sanctioned)
        side = {"last_session": {"execution_mode": "single-agent"},
                "dispatch_log": [_entry(1, "all-passes", tag="unknown",
                                        mode="single-agent", prov="declared")]}
        d = _mk_run(tmp, "unknown_tag", side, pass_files=(1, 5))
        code, lines = run(d)
        chk("unknown_tag_pass", code == 0 and not has(lines, "R3"))

        # 5. unknown (not in table) tag -> R3 WARN
        side = {"dispatch_log": [_entry(1, "all-passes", tag="gpt6000", mode="single-agent")]}
        d = _mk_run(tmp, "bad_tag", side, pass_files=(1,))
        code, lines = run(d)
        chk("bad_tag_r3_warn", code == 0 and has(lines, "WARN R3"))

        # 6. zero-row table parse -> exit 2
        side = {"dispatch_log": [_entry(1, "all-passes")]}
        d = _mk_run(tmp, "zero_table", side, pass_files=(1,), table_text=_TABLE_ZERO_MD)
        code, lines = run(d)
        chk("zero_table_exit2", code == 2 and has(lines, "model-tag-table-unparseable"))

        # 7. no-shell all-`declared` under execution_mode: sequential -> PASS (R4 per-entry)
        side = {"last_session": {"execution_mode": "sequential"},
                "dispatch_log": [_entry(1, "pass0+1", mode="sequential", prov="declared"),
                                 _entry(2, "pass5", mode="sequential", prov="declared"),
                                 _entry(3, "synthesis", mode="sequential", prov="declared")]}
        d = _mk_run(tmp, "noshell", side, pass_files=(1, 5), letter=True)
        code, lines = run(d)
        chk("noshell_declared_sequential_pass", code == 0 and not has(lines, "ERROR"))

        # 8. all-passes coexisting with pass2 -> R2 FAIL (exclusivity)
        side = {"dispatch_log": [_entry(1, "all-passes", mode="single-agent"),
                                 _entry(2, "pass2", mode="single-agent")]}
        d = _mk_run(tmp, "exclusive", side, pass_files=(2,))
        code, lines = run(d)
        chk("all_passes_exclusive_fail", code == 1 and has(lines, "ERROR R2")
            and has(lines, "exclusiv"))

        # 9. entry-without-artifact -> WARN not FAIL
        side = {"dispatch_log": [_entry(1, "pass0+1"), _entry(2, "pass5"),
                                 _entry(3, "pass8"), _entry(4, "synthesis")]}
        d = _mk_run(tmp, "entry_no_art", side, pass_files=(1, 5), letter=True)  # no Pass8 on disk
        code, lines = run(d)
        chk("entry_without_artifact_warn", code == 0 and has(lines, "WARN R2")
            and has(lines, "pass8"))

        # 10. artifact-without-entry -> WARN default, FAIL under --strict (shrink direction)
        side = {"dispatch_log": [_entry(1, "pass0+1"), _entry(2, "synthesis")]}
        d = _mk_run(tmp, "art_no_entry", side, pass_files=(1, 5), letter=True)  # Pass5 unmatched
        code, lines = run(d)
        chk("artifact_without_entry_warn", code == 0 and has(lines, "WARN R2-shrink"))
        code, lines = run(d, strict=True)
        chk("artifact_without_entry_strict_fail", code == 1 and has(lines, "ERROR R2-shrink"))

        # 11. pass0+1 with BOTH Pass0 and Pass1 on disk -> PASS (satisfies both)
        side = {"dispatch_log": [_entry(1, "pass0+1"), _entry(2, "synthesis")]}
        d = _mk_run(tmp, "pass01_both", side, pass_files=(0, 1), letter=True)
        code, lines = run(d)
        chk("pass01_satisfies_both", code == 0 and not has(lines, "R2-shrink"))

        # 12. lookalike step names -> R4 WARN (unknown step kind)
        side = {"dispatch_log": [_entry(1, "pass02"), _entry(2, "synthesis-draft")]}
        d = _mk_run(tmp, "lookalike", side, pass_files=(2,), letter=True)
        code, lines = run(d)
        chk("lookalike_r4_warn", code == 0 and has(lines, "WARN R4")
            and has(lines, "unknown step kind"))

        # 13. malformed: bare string entry -> R4 FAIL
        side = {"dispatch_log": ["just a string"]}
        d = _mk_run(tmp, "bare", side, pass_files=(1,))
        code, lines = run(d)
        chk("bare_string_r4_fail", code == 1 and has(lines, "ERROR R4") and has(lines, "not an object"))

        # 14. malformed: missing model_tag -> R4 FAIL
        side = {"dispatch_log": [{"seq": 1, "step": "pass0+1", "execution_mode": "hybrid",
                                  "provenance": "dispatch-derived"}]}
        d = _mk_run(tmp, "missing_tag", side, pass_files=(1,))
        code, lines = run(d)
        chk("missing_model_tag_r4_fail", code == 1 and has(lines, "ERROR R4")
            and has(lines, "model_tag"))

        # 15. bad enum: execution_mode -> R4 FAIL
        side = {"dispatch_log": [_entry(1, "pass0+1", mode="turbo")]}
        d = _mk_run(tmp, "bad_mode", side, pass_files=(1,))
        code, lines = run(d)
        chk("bad_mode_r4_fail", code == 1 and has(lines, "ERROR R4") and has(lines, "execution_mode"))

        # 16. duplicate seq -> R4 FAIL
        side = {"dispatch_log": [_entry(1, "pass0+1"), _entry(1, "pass5")]}
        d = _mk_run(tmp, "dup_seq", side, pass_files=(1, 5))
        code, lines = run(d)
        chk("duplicate_seq_r4_fail", code == 1 and has(lines, "ERROR R4") and has(lines, "duplicate seq"))

        # 17. seq not strictly increasing -> R4 FAIL
        side = {"dispatch_log": [_entry(2, "pass0+1"), _entry(1, "pass5")]}
        d = _mk_run(tmp, "seq_order", side, pass_files=(1, 5))
        code, lines = run(d)
        chk("seq_not_increasing_fail", code == 1 and has(lines, "not strictly increasing"))

        # 18. R5 stale-mode: final entry mode != last_session.execution_mode -> WARN, FAIL strict
        side = {"last_session": {"execution_mode": "swarm"},
                "dispatch_log": [_entry(1, "pass0+1", mode="hybrid"),
                                 _entry(2, "synthesis", mode="hybrid")]}
        d = _mk_run(tmp, "stale_mode", side, pass_files=(1,), letter=True)
        code, lines = run(d)
        chk("r5_stale_mode_warn", code == 0 and has(lines, "WARN R5") and has(lines, "stale"))
        code, lines = run(d, strict=True)
        chk("r5_stale_mode_strict_fail", code == 1 and has(lines, "ERROR R5"))

        # 19. R5 mode thrash: seq->hybrid->seq -> WARN
        side = {"dispatch_log": [_entry(1, "pass0+1", mode="sequential"),
                                 _entry(2, "pass5", mode="hybrid"),
                                 _entry(3, "synthesis", mode="sequential")]}
        d = _mk_run(tmp, "thrash", side, pass_files=(1, 5), letter=True)
        code, lines = run(d)
        chk("r5_thrash_warn", code == 0 and has(lines, "WARN R5") and has(lines, "thrash"))

        # 20. single legitimate escalation (hybrid->swarm once) matching last_session -> PASS
        side = {"last_session": {"execution_mode": "swarm"},
                "dispatch_log": [_entry(1, "pass0+1", mode="hybrid"),
                                 _entry(2, "pass5", mode="swarm"),
                                 _entry(3, "synthesis", mode="swarm")]}
        d = _mk_run(tmp, "one_transition", side, pass_files=(1, 5), letter=True)
        code, lines = run(d)
        chk("r5_one_transition_pass", code == 0 and not has(lines, "R5"))

        # 21. bad provenance enum -> R4 FAIL (no mode-based provenance FAIL, but bad enum fails)
        side = {"dispatch_log": [_entry(1, "pass0+1", prov="assumed")]}
        d = _mk_run(tmp, "bad_prov", side, pass_files=(1,))
        code, lines = run(d)
        chk("bad_provenance_r4_fail", code == 1 and has(lines, "ERROR R4") and has(lines, "provenance"))

        # 22. deferred-extension id recorded -> accepted, not reconciled (no R2/R4 fire on it)
        side = {"dispatch_log": [_entry(1, "pass0+1"), _entry(2, "audit:consent-complexity"),
                                 _entry(3, "prerequisite:field-recon"),
                                 _entry(4, "refutation"), _entry(5, "synthesis")]}
        d = _mk_run(tmp, "deferred", side, pass_files=(1,), letter=True)
        code, lines = run(d)
        chk("deferred_ids_accepted", code == 0 and not has(lines, "unknown step kind"))

        # 23. malformed sidecar JSON -> hard ERROR (not silent pass)
        d = os.path.join(tmp, "bad_json")
        os.makedirs(d, exist_ok=True)
        _write(os.path.join(d, "Diagnostic_State.meta.json"), "{ not json")
        _write(os.path.join(d, "output-structure.md"), _TABLE_MD)
        code, lines = run(d)
        chk("malformed_sidecar_error", code == 1 and has(lines, "ERROR sidecar"))

    # 24. --report smoke: a project dir with two runs, one budget-rationale override
    with tempfile.TemporaryDirectory() as tmp:
        proj = os.path.join(tmp, "MyProject")
        r1 = os.path.join(proj, "runs", "run1")
        r2 = os.path.join(proj, "runs", "run2")
        os.makedirs(r1); os.makedirs(r2)
        _write(os.path.join(r1, "Diagnostic_State.meta.json"),
               json.dumps({"dispatch_log": [_entry(1, "pass0+1", tag="opus46"),
                                            _entry(2, "pass5", tag="sonnet46")]}))
        _write(os.path.join(r2, "Diagnostic_State.meta.json"),
               json.dumps({"dispatch_log": [_entry(1, "all-passes", tag="opus46",
                                                   mode="single-agent")]}))
        # a budget-flavored override marker + a plain token form; plus a cost_floor_override marker
        # (r1) and token (r2) so the CR-6 cost-floor report line counts both forms once each.
        _write(os.path.join(r1, "Contract.md"),
               "notes\n<!-- override: quality-risk-Q2 — budget constraint, exploratory -->\n"
               "<!-- override: cost-floor-sequential — $20-plan usage window -->\n")
        _write(os.path.join(r2, "run-meta.md"),
               "quality_risk_override: Q5 — time pressure this round\n"
               "cost_floor_override: sequential — $20-plan usage window\n")
        # a doc that merely QUOTES the token forms in a code span must NOT count (code-span strip) —
        # each count stays 2, not 3.
        _write(os.path.join(r2, "how-to.md"),
               "To decline for cost, write `quality_risk_override: Q3 — budget` in run metadata.\n"
               "To cap below the floor, write `cost_floor_override: hybrid — budget window` instead.\n")
        code, lines = run_report(proj)
        chk("report_runs_scanned", code == 0 and has(lines, "runs scanned"))
        chk("report_tag_tally_opus", any("opus46" in ln and "2" in ln for ln in lines))
        chk("report_qro_count", any("quality_risk_override records: 2" in ln for ln in lines))
        chk("report_quoted_token_not_counted",  # the code-span-quoted example did not inflate to 3
            not any("quality_risk_override records: 3" in ln for ln in lines))
        chk("report_budget_flavored", any("budget-flavored rationale: 1" in ln for ln in lines))
        chk("report_cfo_count",  # one cost-floor marker (r1) + one token (r2) counted once each
            any("cost_floor_override records: 2" in ln for ln in lines))
        chk("report_cfo_quoted_not_counted",  # the code-span-quoted cost_floor_override did not inflate
            not any("cost_floor_override records: 3" in ln for ln in lines))

    print("Self-test: %s" % ("PASS" if rc == 0 else "FAIL"))
    return rc


# ---------------------------------------------------------------- main

def main(argv):
    if "--self-test" in argv:
        return run_self_test()
    args = [a for a in argv[1:] if a != "dispatch-record"]
    if "--report" in args:
        i = args.index("--report")
        rest = [a for a in args if a != "--report"]
        if not rest:
            print("Usage: dispatch_record.py dispatch-record --report <project_dir>")
            return 2
        code, lines = run_report(rest[0])
        for ln in lines:
            print(ln)
        return code
    strict = "--strict" in args
    positional = [a for a in args if not a.startswith("--")]
    if not positional:
        print("Usage: dispatch_record.py dispatch-record <run_folder> [--strict] | "
              "dispatch-record --report <project_dir> | --self-test")
        return 2
    code, lines = check_dispatch_record(positional[0], strict=strict)
    for ln in lines:
        print(ln)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
