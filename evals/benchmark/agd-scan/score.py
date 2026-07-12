#!/usr/bin/env python3
"""score.py — AGD-scan benchmark Phase-2 SCORING harness (R3B §4, offline).

Phase 1 (ACQUISITION) is committed: 20 run-manifests under ``manifests/``
(5 R3A fixtures x {fable, codex} x rep{1,2}), each a
``{fixture_id, vendor, model_id, prompt_fingerprint_sha256, rep, acquired_at,
values:{observations}}`` record produced against the live judge and never
regenerated here (READ-ONLY).

Phase 2 (this script) is deterministic and re-runnable forever OFFLINE. For
each manifest it:

  1. REPLAYS the manifest through the consumer channel — the same shim an
     APODICTIC audit would run — with the producer's manifest judge:

         ai_prose_agd_move_scan.py <fixture source> \\
             --judge manifest --judge-manifest <manifest> \\
             --expect-fingerprint <the manifest's own prompt_fingerprint_sha256> \\
             --json

     with ``SETEC_VOICEPRINT_DIR`` (taken from the environment; a scoring run
     ERRORS loudly if it is unset) pointing at the producer worktree. It then
     takes ``results.observations`` from the returned schema_version 1.0
     envelope. A non-available envelope or a fingerprint-drift refusal is a
     scoring ERROR for that cell — loudly reported, never silently skipped.

  2. COMPARES the located observations to the fixture's Argument_State.md
     §10.9 M-record inventory, using the §1b comparison coordinate and dedup
     rule (see the module docstring section "The §1b coordinate + match rule"
     and README.md). The M-record parsing / anchor normalization is reused
     from ``scripts/argument_agd.py`` (extract_section, parse_block, _norm,
     anchor_resolves) — imported, not forked.

  3. Assigns the §4 rep-outcome taxonomy PER M-RECORD (CORRECT / INCORRECT /
     SOFT), enumerates misses (records with no same-family overlapping
     observation) and extras (observations overlapping no M-record coordinate
     — CALIBRATION DATA, never an error), and applies the one hard gate.

Ownership rule (R4A ADR D5): this scorer measures scan-vs-audit AGREEMENT
only. It never adjudicates argument quality and never treats observation
COUNT as a quality signal. There is no aggregate beyond the agreement
bookkeeping itself.

The §1b coordinate + match rule (made mechanical here)
------------------------------------------------------
An M-record's machine-resolvable coordinate is its ``Source anchor``:

  * Resolve the anchor's verbatim quote in the source text via argument_agd's
    normalization (whitespace runs folded, quote/dash chars normalized,
    case-sensitive). It MUST resolve (it does under ``--check-all``); a
    non-resolving anchor is a loud error.
  * Split the source into blank-line-delimited paragraphs using the PRODUCER
    convention (``re.split(r"\\n\\s*\\n", text.strip())`` then strip + drop
    empties), normalize each, and find which normalized paragraph contains the
    normalized anchor. Exactly one must contain it: zero (unreachable given
    resolution) or more than one (ambiguous) is a loud error rather than a
    guess. That paragraph index is the record's derived paragraph.
  * Locate the anchor at its FIRST occurrence in that normalized paragraph as
    a half-open interval [start, end).

A scan observation MATCHES an M-record iff: same derived paragraph
(observation.paragraph_index == record's derived paragraph) AND same family
AND their normalized spans OVERLAP as intervals in that normalized paragraph
(each span located at its first occurrence; overlap = interval intersection
non-empty; adjacent-but-disjoint spans do NOT overlap).

Per-M-record outcome (§4 taxonomy):
  * CORRECT   — >=1 observation overlaps the record's coordinate with the SAME
                family.
  * INCORRECT — >=1 observation overlaps the coordinate with a DIFFERENT family
                and NONE with the same family.
  * SOFT      — no observation overlaps the coordinate at all.

CLI:
  score.py                 run the 20-cell scoring; print the results table +
                           the hard-gate verdict; exit 1 iff the gate fails.
  score.py --report        run the scoring; emit the §M-AGD markdown to stdout.
  score.py --write-report  run the scoring; append/replace the §M-AGD section
                           in docs/argument-benchmark-calibration-round.md.
  score.py --self-test     synthetic in-memory matcher arms; NO file IO.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile

# --------------------------------------------------------------------------
# Paths + reuse of the §10.9 validator machinery (imported, never forked)
# --------------------------------------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.abspath(os.path.join(_HERE, "..", "..", ".."))
_SCRIPTS_DIR = os.path.join(_REPO_ROOT, "scripts")
_MANIFESTS_DIR = os.path.join(_HERE, "manifests")
_FIXTURES_DIR = os.path.join(_REPO_ROOT, "evals", "fixtures", "argument-agd")
_SHIM = os.path.join(_REPO_ROOT, "plugins", "apodictic", "skills",
                     "specialized-audits", "scripts", "ai_prose_agd_move_scan.py")
_DOCS = os.path.join(_REPO_ROOT, "docs", "argument-benchmark-calibration-round.md")

if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

# argument_agd is the R3A §10.9 validator; reuse its parsing + Source-anchor
# normalization so the benchmark and the validator agree by construction.
import argument_agd as agd  # noqa: E402

# Source-anchor grammar mirrors argument_agd Check 4 (validate(): the
# `"<verbatim quote>" @ <locus>` shape). Bounded leaf regex on the quoted
# fragment only — the surrounding parse is structural (parse_block).
_ANCHOR_RE = re.compile(r'^"(.+)"\s+@\s+(.+)$')

# --------------------------------------------------------------------------
# Provenance (pinned; see README.md and the §M-AGD report). Fixtures are
# referenced BY NAME everywhere, never by ordinal (§4).
# --------------------------------------------------------------------------
PRODUCER = "setec-voiceprint v1.124.0"
PROMPT_FINGERPRINT = "f07f8f4adafaf9eebb47ff72dca640042c5bc4c576044d9f1d79002733c2bcf5"
CONSUMER_BASE = "apodictic v2.9.0"
ACQUIRED_ON = "2026-07-12"
VENDOR_PROSE = {
    "fable": "claude-fable-5 via fresh Claude-Code subagents (no tools, prompt-only)",
    "codex": ("gpt-5.6-sol at model_reasoning_effort=xhigh via codex exec in an "
              "empty-cwd read-only sandbox"),
}

# The one hard gate (§4 pass criteria; OQ4 — the wedge claim).
GATE_FIXTURE = "cue-free-structural-discounting"
GATE_RECORD_IDX = 1          # M1
GATE_FAMILY = "DISCOUNTING"

CORRECT, INCORRECT, SOFT = "CORRECT", "INCORRECT", "SOFT"


# --------------------------------------------------------------------------
# Paragraph segmentation (PRODUCER convention — must match the index space the
# observations' paragraph_index live in). Verbatim mirror of the producer's
# scripts/agd_move_scan.py:split_paragraphs (setec-voiceprint v1.124.0).
# --------------------------------------------------------------------------
def split_paragraphs(text):
    parts = re.split(r"\n\s*\n", text.strip())
    return [p.strip() for p in parts if p.strip()]


def normalized_paragraphs(source_text):
    """The blank-line paragraphs, each normalized by argument_agd._norm."""
    return [agd._norm(p) for p in split_paragraphs(source_text)]


def _interval(norm_para, raw_span):
    """Locate `raw_span` at its FIRST occurrence in `norm_para` (both under
    argument_agd normalization). Returns a half-open (start, end) interval, or
    None when the span does not occur in that paragraph."""
    ns = agd._norm(raw_span)
    if not ns:
        return None
    i = norm_para.find(ns)
    if i < 0:
        return None
    return (i, i + len(ns))


def _overlap(a, b):
    """Non-empty intersection of two half-open intervals. Adjacent-but-disjoint
    (e.g. (0,5) and (5,10)) do NOT overlap."""
    if a is None or b is None:
        return False
    return a[0] < b[1] and b[0] < a[1]


class AnchorError(Exception):
    """A Source anchor that fails to resolve, or resolves ambiguously."""


def derive_record_coord(anchor_quote, source_text, norm_paras=None):
    """Resolve an M-record's Source-anchor coordinate: (paragraph_index,
    (start, end) interval in that normalized paragraph).

    Loud errors (never a guess): the anchor does not resolve in the source at
    all; the anchor resolves in ZERO paragraphs (unreachable given whole-doc
    resolution, guarded anyway); or the anchor resolves in MORE THAN ONE
    paragraph (ambiguous)."""
    if norm_paras is None:
        norm_paras = normalized_paragraphs(source_text)
    if not agd.anchor_resolves(anchor_quote, source_text):
        raise AnchorError("anchor does not resolve in the source text: %r" % anchor_quote)
    norm_anchor = agd._norm(anchor_quote)
    hits = [idx for idx, np in enumerate(norm_paras) if norm_anchor in np]
    if len(hits) == 0:
        raise AnchorError(
            "anchor resolves in the document but in no single blank-line "
            "paragraph (paragraph-split mismatch): %r" % anchor_quote)
    if len(hits) > 1:
        raise AnchorError(
            "anchor resolves in %d paragraphs %s — ambiguous locus, refusing "
            "to guess: %r" % (len(hits), hits, anchor_quote))
    idx = hits[0]
    interval = _interval(norm_paras[idx], anchor_quote)
    if interval is None:                       # defensive; resolution proved it is there
        raise AnchorError(
            "anchor located in paragraph %d but its interval could not be "
            "computed: %r" % (idx, anchor_quote))
    return idx, interval


# --------------------------------------------------------------------------
# The matcher (pure; exercised directly by --self-test)
# --------------------------------------------------------------------------
def outcome_for_record(rec_coord, rec_family, located_obs):
    """The §4 taxonomy outcome for one M-record.

    rec_coord    = (paragraph_index, (start, end)) from derive_record_coord.
    rec_family   = the M-record's declared AGD family.
    located_obs  = list of dicts {family, paragraph_index, interval}, each
                   observation pre-located in its own paragraph.
    Returns (outcome, overlapping), where `overlapping` is the observations
    whose coordinate overlaps the record's (same paragraph + interval overlap;
    family-independent)."""
    rec_idx, rec_iv = rec_coord
    overlapping = [
        o for o in located_obs
        if o["paragraph_index"] == rec_idx and _overlap(o["interval"], rec_iv)
    ]
    if not overlapping:
        return SOFT, overlapping
    if any(o["family"] == rec_family for o in overlapping):
        return CORRECT, overlapping
    return INCORRECT, overlapping


def locate_observations(observations, norm_paras):
    """Attach a located interval to each observation (in its own paragraph).
    Returns (located, anomalies). An anomaly is an observation whose
    paragraph_index is out of range or whose span does not locate in its
    paragraph — producer span-integrity should preclude both, so any anomaly
    is reported loudly (it never silently drops the observation)."""
    located, anomalies = [], []
    for o in observations:
        pidx = o.get("paragraph_index")
        family = o.get("family")
        span = o.get("span", "")
        iv = None
        if not isinstance(pidx, int) or pidx < 0 or pidx >= len(norm_paras):
            anomalies.append("observation paragraph_index %r out of range [0,%d): %r"
                             % (pidx, len(norm_paras), span))
        else:
            iv = _interval(norm_paras[pidx], span)
            if iv is None:
                anomalies.append("observation span does not locate in paragraph %d: %r"
                                 % (pidx, span))
        located.append({"family": family, "paragraph_index": pidx,
                        "interval": iv, "span": span, "cue": o.get("cue")})
    return located, anomalies


# --------------------------------------------------------------------------
# Fixture M-record coordinates (fixture-level; shared by all 4 cells)
# --------------------------------------------------------------------------
def load_fixture_records(fixture_id):
    """Return (records, norm_paras, source_text). records = list of
    {idx, family, locus, quote, coord}. Raises loudly on a missing/parseless
    §10.9 section or a non-resolving/ambiguous anchor."""
    fx_dir = os.path.join(_FIXTURES_DIR, fixture_id)
    state_p = os.path.join(fx_dir, "argument-state.md")
    source_p = os.path.join(fx_dir, "source.md")
    with open(state_p, "r", encoding="utf-8") as fh:
        state_text = fh.read()
    with open(source_p, "r", encoding="utf-8") as fh:
        source_text = fh.read()
    body = agd.extract_section(state_text)
    if body is None:
        raise AnchorError("%s: no '### 10.9 AGD Move Audit' section" % state_p)
    _manifest, raw_records, perrs = agd.parse_block(body)
    if perrs:
        raise AnchorError("%s: §10.9 parse errors: %s" % (state_p, perrs))
    norm_paras = normalized_paragraphs(source_text)
    records = []
    for r in raw_records:
        anchor_field = r["fields"].get("Source anchor", "")
        m = _ANCHOR_RE.match(anchor_field)
        if not m:
            raise AnchorError("%s M%d: Source anchor is not '\"quote\" @ locus': %r"
                              % (fixture_id, r["idx"], anchor_field))
        quote = m.group(1)
        coord = derive_record_coord(quote, source_text, norm_paras)
        records.append({"idx": r["idx"], "family": r["family"], "locus": r["locus"],
                        "quote": quote, "coord": coord})
    return records, norm_paras, source_text


# --------------------------------------------------------------------------
# Offline replay of one manifest through the consumer shim
# --------------------------------------------------------------------------
class ReplayError(Exception):
    pass


def replay_manifest(source_path, manifest_path):
    """Run the shim OFFLINE against `source_path` with the manifest judge and
    the manifest's OWN prompt fingerprint. Returns results.observations.
    Raises ReplayError on a non-zero exit, an unavailable envelope, a
    fingerprint-drift refusal, or a missing observations list — never returns
    an empty inventory to mask an error."""
    with open(manifest_path, "r", encoding="utf-8") as fh:
        manifest = json.load(fh)
    fp = manifest.get("prompt_fingerprint_sha256")
    if not fp:
        raise ReplayError("manifest %s carries no prompt_fingerprint_sha256" % manifest_path)
    # The observations are read from stdout (--json). The producer ALSO writes a
    # sidecar envelope file, defaulting to `<source>.agd_move_scan.json` beside
    # the target on EVERY exit path (success and error). Redirect --out/--out-md
    # to a throwaway dir so scoring never writes into the read-only fixtures
    # tree; the redirect is a pure side-effect sink, not part of the comparison.
    with tempfile.TemporaryDirectory(prefix="agd_replay_") as sink:
        cmd = [sys.executable, _SHIM, source_path,
               "--judge", "manifest", "--judge-manifest", manifest_path,
               "--expect-fingerprint", fp, "--json",
               "--out", os.path.join(sink, "replay.json"),
               "--out-md", os.path.join(sink, "replay.md")]
        proc = subprocess.run(cmd, capture_output=True, text=True)
    envelope = None
    if proc.stdout.strip():
        try:
            envelope = json.loads(proc.stdout)
        except ValueError:
            envelope = None
    if proc.returncode != 0:
        reason = (envelope or {}).get("reason") if envelope else (proc.stderr.strip() or "no output")
        raise ReplayError("shim exit %d: %s" % (proc.returncode, reason))
    if envelope is None:
        raise ReplayError("shim produced no parseable envelope on stdout")
    if not envelope.get("available"):
        raise ReplayError("envelope available=false: %s"
                          % envelope.get("reason", "(no reason)"))
    obs = (envelope.get("results") or {}).get("observations")
    if not isinstance(obs, list):
        raise ReplayError("envelope has no results.observations list")
    return obs


# --------------------------------------------------------------------------
# Cells + the scoring pass
# --------------------------------------------------------------------------
def discover_cells():
    """Enumerate (fixture, vendor, rep, manifest_path) from manifests/, sorted
    deterministically."""
    cells = []
    for name in sorted(os.listdir(_MANIFESTS_DIR)):
        if not name.endswith(".json"):
            continue
        stem = name[:-len(".json")]
        parts = stem.split("--")
        if len(parts) != 3 or not parts[2].startswith("rep"):
            raise ReplayError("manifest filename does not match "
                              "<fixture>--<vendor>--rep<n>.json: %r" % name)
        fixture, vendor, reptok = parts
        rep = int(reptok[len("rep"):])
        cells.append({"fixture": fixture, "vendor": vendor, "rep": rep,
                      "manifest": os.path.join(_MANIFESTS_DIR, name)})
    order = {"fable": 0, "codex": 1}
    cells.sort(key=lambda c: (c["fixture"], order.get(c["vendor"], 9), c["rep"]))
    return cells


def score_cell(cell, fixture_cache):
    """Score one manifest cell. Returns a dict with per-record outcomes,
    misses, extras, and (on failure) an error string. Never raises; a replay
    or anchor failure is captured as the cell's ``error``."""
    fixture = cell["fixture"]
    result = {"fixture": fixture, "vendor": cell["vendor"], "rep": cell["rep"],
              "error": None, "records": [], "n_obs": 0, "extras": [],
              "misses": [], "anomalies": []}
    try:
        if fixture not in fixture_cache:
            fixture_cache[fixture] = load_fixture_records(fixture)
        records, norm_paras, _src = fixture_cache[fixture]
    except (AnchorError, OSError, ValueError) as exc:
        result["error"] = "fixture load: %s" % exc
        return result

    source_path = os.path.join(_FIXTURES_DIR, fixture, "source.md")
    try:
        observations = replay_manifest(source_path, cell["manifest"])
    except (ReplayError, OSError, ValueError) as exc:
        result["error"] = "replay: %s" % exc
        return result

    located, anomalies = locate_observations(observations, norm_paras)
    result["n_obs"] = len(observations)
    result["anomalies"] = anomalies

    # Per-M-record outcome + misses.
    for rec in records:
        outcome, overlapping = outcome_for_record(rec["coord"], rec["family"], located)
        result["records"].append({"idx": rec["idx"], "family": rec["family"],
                                  "locus": rec["locus"], "outcome": outcome})
        if outcome != CORRECT:
            result["misses"].append({"idx": rec["idx"], "family": rec["family"],
                                     "locus": rec["locus"], "outcome": outcome})

    # Extras: observations overlapping NO M-record coordinate (family-independent).
    coords = [rec["coord"] for rec in records]
    for o in located:
        overlaps_any = any(
            o["paragraph_index"] == c[0] and _overlap(o["interval"], c[1]) for c in coords)
        if not overlaps_any:
            result["extras"].append({"family": o["family"], "span": o["span"],
                                     "cue": o["cue"], "paragraph_index": o["paragraph_index"]})
    return result


def run_scoring():
    """Score all cells. Returns (cells_results, gate)."""
    if not os.environ.get("SETEC_VOICEPRINT_DIR"):
        sys.stderr.write(
            "ERROR: SETEC_VOICEPRINT_DIR is unset. Point it at the producer "
            "worktree's plugin dir, e.g.\n"
            "  export SETEC_VOICEPRINT_DIR=/path/to/setec-voiceprint/plugins/setec-voiceprint\n"
            "so the offline replay can resolve the agd_move_scan surface.\n")
        raise SystemExit(2)
    fixture_cache = {}
    results = [score_cell(c, fixture_cache) for c in discover_cells()]
    gate = evaluate_gate(results)
    return results, gate


def evaluate_gate(results):
    """The one hard gate (§4): cue-free-structural-discounting M1 (DISCOUNTING)
    reaches >=1 CORRECT rep PER VENDOR and 0 INCORRECT reps across all reps of
    that fixture. Returns a dict describing the verdict."""
    gate_cells = [r for r in results if r["fixture"] == GATE_FIXTURE]
    per_vendor_correct = {}
    incorrect_reps = []
    errored = []
    for r in gate_cells:
        if r["error"]:
            errored.append(r)
            continue
        rec = next((x for x in r["records"] if x["idx"] == GATE_RECORD_IDX), None)
        if rec is None:
            errored.append(r)
            continue
        outcome = rec["outcome"]
        per_vendor_correct.setdefault(r["vendor"], False)
        if outcome == CORRECT:
            per_vendor_correct[r["vendor"]] = True
        if outcome == INCORRECT:
            incorrect_reps.append(r)
    _vorder = {"fable": 0, "codex": 1}
    vendors = sorted({r["vendor"] for r in gate_cells},
                     key=lambda v: (_vorder.get(v, 9), v))
    all_vendors_have_correct = bool(vendors) and all(
        per_vendor_correct.get(v, False) for v in vendors)
    passed = (not errored) and all_vendors_have_correct and not incorrect_reps
    return {"passed": passed, "vendors": vendors,
            "per_vendor_correct": per_vendor_correct,
            "incorrect_reps": incorrect_reps, "errored": errored}


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------
def _rec_outcomes_str(r):
    if r["error"]:
        return "ERROR"
    return " · ".join("M%d:%s" % (rec["idx"], rec["outcome"]) for rec in r["records"])


def render_console(results, gate):
    lines = []
    lines.append("AGD-scan Phase-2 scoring — 20 cells "
                 "(5 fixtures x {fable,codex} x rep{1,2})")
    lines.append("")
    header = "%-32s %-6s %-4s %-5s %-28s %-6s" % (
        "fixture", "vendor", "rep", "obs", "M-record outcomes", "extras")
    lines.append(header)
    lines.append("-" * len(header))
    for r in results:
        lines.append("%-32s %-6s %-4d %-5s %-28s %-6s" % (
            r["fixture"], r["vendor"], r["rep"],
            "ERR" if r["error"] else r["n_obs"],
            _rec_outcomes_str(r),
            "ERR" if r["error"] else len(r["extras"])))
        if r["error"]:
            lines.append("    ERROR: %s" % r["error"])
        for a in r["anomalies"]:
            lines.append("    ANOMALY: %s" % a)
    lines.append("")
    lines.append(_gate_console(gate))
    return "\n".join(lines)


def _gate_console(gate):
    out = []
    out.append("HARD GATE (§4) — %s M%d (family %s): >=1 CORRECT rep per vendor "
               "AND 0 INCORRECT reps across all reps"
               % (GATE_FIXTURE, GATE_RECORD_IDX, GATE_FAMILY))
    for v in gate["vendors"]:
        out.append("  vendor %-6s: %s CORRECT rep present"
                   % (v, "yes" if gate["per_vendor_correct"].get(v) else "NO"))
    out.append("  INCORRECT reps on the gated record: %d" % len(gate["incorrect_reps"]))
    if gate["errored"]:
        out.append("  ERRORED gate cells: %d (a scoring error fails the gate)"
                   % len(gate["errored"]))
    out.append("HARD GATE VERDICT: %s" % ("PASS" if gate["passed"] else "FAIL"))
    return "\n".join(out)


def _short(span, n=60):
    # Fold whitespace runs (incl. the source's line-wrap newlines that survive
    # in verbatim spans) so a fragment renders cleanly inline; display-only.
    span = re.sub(r"\s+", " ", span or "").strip()
    return span if len(span) <= n else span[:n - 1].rstrip() + "…"


def render_report(results, gate):
    """The §M-AGD markdown section (docs/argument-benchmark-calibration-round.md
    convention). Generated by RUNNING the scorer — never hand-written cells."""
    L = []
    L.append("## §M-AGD — AGD scan/audit agreement benchmark (%s)" % ACQUIRED_ON)
    L.append("")
    L.append("**Increment:** R3B §4 Phase-2 SCORING — the offline, deterministic "
             "half of the AGD producer/consumer behavioral benchmark. Each of the "
             "20 committed Phase-1 run-manifests (5 R3A fixtures x {fable, codex} x "
             "rep{1,2}) is replayed through the consumer channel "
             "(`ai_prose_agd_move_scan.py --judge manifest`) and its located "
             "observations are compared to the fixture's §10.9 M-record inventory "
             "under the §1b coordinate + dedup rule. The scorer measures scan↔audit "
             "AGREEMENT only (R4A ADR D5: the producer observes, the audit alone "
             "adjudicates); observation COUNT is location data, never a quality "
             "signal, and there is no aggregate beyond this agreement bookkeeping.")
    L.append("")
    L.append("**Coordinate + match rule (mechanical §1b).** An M-record's coordinate "
             "is its resolved `Source anchor`: the anchor's verbatim quote is "
             "resolved in the source under argument_agd's normalization "
             "(whitespace folded, quote/dash chars normalized, case-sensitive), the "
             "source is split into the producer's blank-line paragraphs, and the one "
             "normalized paragraph containing the normalized anchor is the record's "
             "derived paragraph (zero or >1 = a loud error, never a guess). A scan "
             "observation matches iff **same derived paragraph AND same family AND "
             "normalized-span interval overlap** (first occurrence; adjacent-disjoint "
             "spans do not overlap). CORRECT = >=1 same-family overlapping "
             "observation; INCORRECT = >=1 overlapping observation, all a different "
             "family; SOFT = no overlapping observation. The prose locus label is "
             "never a comparison operand.")
    L.append("")
    L.append("**Results — 20 cells (per-M-record outcome + extras count).** Extras "
             "are observations overlapping no M-record coordinate: CALIBRATION DATA "
             "for the audit's decline path, never an error. Fixtures are named, "
             "never ordinal.")
    L.append("")
    L.append("| Fixture | Vendor | Rep | Obs | M-record outcomes | Extras |")
    L.append("|---|---|---|---:|---|---:|")
    for r in results:
        L.append("| %s | %s | %d | %s | %s | %s |" % (
            r["fixture"], r["vendor"], r["rep"],
            "ERR" if r["error"] else str(r["n_obs"]),
            "**ERROR**" if r["error"] else _rec_outcomes_str(r),
            "ERR" if r["error"] else str(len(r["extras"]))))
    L.append("")

    # Misses / extras enumeration.
    L.append("**Misses and extras (per cell).** A miss = an M-record with no "
             "same-family overlapping observation (SOFT or INCORRECT); an extra = an "
             "observation overlapping no M-record coordinate.")
    L.append("")
    any_detail = False
    for r in results:
        if r["error"]:
            L.append("- `%s / %s / rep%d` — **scoring ERROR**: %s"
                     % (r["fixture"], r["vendor"], r["rep"], r["error"]))
            any_detail = True
            continue
        frags = []
        if r["misses"]:
            frags.append("misses: " + ", ".join(
                "M%d (%s, %s)" % (m["idx"], m["family"], m["outcome"]) for m in r["misses"]))
        if r["extras"]:
            frags.append("extras: " + "; ".join(
                '%s "%s" (¶%s%s)' % (
                    e["family"], _short(e["span"]), e["paragraph_index"],
                    ", cue-free" if e["cue"] is None else ', cue "%s"' % _short(e["cue"], 24))
                for e in r["extras"]))
        for a in r["anomalies"]:
            frags.append("ANOMALY: " + a)
        if frags:
            L.append("- `%s / %s / rep%d` — %s"
                     % (r["fixture"], r["vendor"], r["rep"], "; ".join(frags)))
            any_detail = True
    if not any_detail:
        L.append("- (none — every M-record CORRECT and no extras across all 20 cells)")
    L.append("")

    # Hard-gate verdict.
    L.append("**Hard gate (§4 pass criteria — the wedge claim).** Fixture "
             "`%s`, M%d (family %s): >=1 CORRECT rep **per vendor** AND **0 "
             "INCORRECT** reps on that record across all reps of that fixture."
             % (GATE_FIXTURE, GATE_RECORD_IDX, GATE_FAMILY))
    L.append("")
    for v in gate["vendors"]:
        L.append("- vendor **%s**: %s"
                 % (v, "CORRECT rep present ✓" if gate["per_vendor_correct"].get(v)
                    else "NO CORRECT rep ✗"))
    L.append("- INCORRECT reps on the gated record across all reps: **%d**%s"
             % (len(gate["incorrect_reps"]),
                " ✓" if not gate["incorrect_reps"] else " ✗"))
    if gate["errored"]:
        L.append("- scoring ERRORs among the gate cells: **%d** (any error fails the gate)"
                 % len(gate["errored"]))
    L.append("")
    L.append("**HARD-GATE VERDICT: %s** — %s"
             % ("PASS ✅" if gate["passed"] else "FAIL ❌",
                "the scan finds the cue-free structural-discounting move (family "
                "DISCOUNTING) reliably per vendor with no family confusion on the "
                "gated record." if gate["passed"]
                else "the wedge claim is not met; see the per-vendor / INCORRECT "
                "lines above."))
    L.append("")

    # Provenance.
    L.append("**Provenance.** Producer **%s** (prompt fingerprint "
             "`%s`); consumer base **%s**. Phase-2 scoring replays each manifest "
             "OFFLINE through `ai_prose_agd_move_scan.py --judge manifest "
             "--judge-manifest <manifest> --expect-fingerprint <fp> --json` "
             "(`SETEC_VOICEPRINT_DIR` → the producer worktree), taking "
             "`results.observations` from the envelope; a non-available envelope or "
             "fingerprint drift is a scoring ERROR, never a silent skip. Vendors: "
             "**fable** = %s; **codex** = %s — both received the producer's exact "
             "rendered judge prompt plus a minimal transport preface. Acquisition "
             "%s; the run-manifests and the exact acquisition commands are in "
             "`evals/benchmark/agd-scan/manifests/` and "
             "`evals/benchmark/agd-scan/acquisition-log.md`. This section is "
             "generated by running `evals/benchmark/agd-scan/score.py --write-report`; "
             "the result cells are never hand-written."
             % (PRODUCER, PROMPT_FINGERPRINT, CONSUMER_BASE,
                VENDOR_PROSE["fable"], VENDOR_PROSE["codex"], ACQUIRED_ON))
    L.append("")
    return "\n".join(L)


_SECTION_MARKER = "## §M-AGD"


def write_report(report_md):
    """Append or replace the §M-AGD section in the docs file. Replacement is a
    structural heading walk (from the '## §M-AGD' line to the next '## ' or
    end-of-file), so re-running is idempotent."""
    with open(_DOCS, "r", encoding="utf-8") as fh:
        text = fh.read()
    lines = text.splitlines()
    start = None
    for i, ln in enumerate(lines):
        if ln.startswith(_SECTION_MARKER):
            start = i
            break
    report_md = report_md.rstrip("\n") + "\n"
    if start is None:
        new_text = text.rstrip("\n") + "\n\n" + report_md
    else:
        end = len(lines)
        for j in range(start + 1, len(lines)):
            if lines[j].startswith("## "):
                end = j
                break
        head = "\n".join(lines[:start]).rstrip("\n")
        tail = "\n".join(lines[end:]).lstrip("\n")
        new_text = head + "\n\n" + report_md
        if tail:
            new_text += "\n" + tail + "\n"
    with open(_DOCS, "w", encoding="utf-8") as fh:
        fh.write(new_text)
    return start is None


# --------------------------------------------------------------------------
# Self-test — synthetic, in-memory, NO file IO
# --------------------------------------------------------------------------
def _selftest():
    fails = []

    def check(name, cond):
        if not cond:
            fails.append(name)

    # A two-paragraph synthetic source. Paragraph 0 carries a DISCOUNTING move
    # ("Although X ...") and an unrelated clause; paragraph 1 carries a
    # duplicate phrase used for the ambiguity arm.
    src = ("Although critics raise the cost, the budget covers it. The plan "
           "should proceed.\n\n"
           "Although critics raise the cost, the review is due next spring.")
    norm_paras = normalized_paragraphs(src)
    check("two paragraphs split", len(norm_paras) == 2)

    # A record coordinate on paragraph 0 over "the budget covers it".
    rec_quote = "the budget covers it"
    rec_coord = derive_record_coord(rec_quote, src, norm_paras)
    check("record coord in paragraph 0", rec_coord[0] == 0)

    def obs(family, pidx, span):
        return {"family": family, "paragraph_index": pidx,
                "interval": _interval(norm_paras[pidx], span), "span": span,
                "cue": None}

    # (1) same-paragraph, same-family, overlapping span -> CORRECT.
    o_hit = obs("DISCOUNTING", 0, "the budget covers it. The plan")
    out, ov = outcome_for_record(rec_coord, "DISCOUNTING", [o_hit])
    check("same-para overlap -> CORRECT", out == CORRECT and len(ov) == 1)

    # (2) right span but WRONG paragraph -> no match -> SOFT.
    o_wrong_para = {"family": "DISCOUNTING", "paragraph_index": 1,
                    "interval": _interval(norm_paras[1], "the review is due"),
                    "span": "the review is due", "cue": None}
    out, _ = outcome_for_record(rec_coord, "DISCOUNTING", [o_wrong_para])
    check("wrong paragraph -> SOFT (reject)", out == SOFT)

    # (3) overlapping span, DIFFERENT family, none same-family -> INCORRECT.
    o_fammis = obs("ASSURING", 0, "the budget covers it")
    out, _ = outcome_for_record(rec_coord, "DISCOUNTING", [o_fammis])
    check("family mismatch -> INCORRECT", out == INCORRECT)

    # (3b) same coordinate with BOTH a wrong-family and a right-family obs ->
    #      the same-family hit wins (CORRECT).
    out, _ = outcome_for_record(rec_coord, "DISCOUNTING", [o_fammis, o_hit])
    check("same-family overrides mismatch -> CORRECT", out == CORRECT)

    # (4) same paragraph, same family, NON-overlapping span -> SOFT.
    o_nolap = obs("DISCOUNTING", 0, "The plan should proceed")
    out, _ = outcome_for_record(rec_coord, "DISCOUNTING", [o_nolap])
    check("no overlap -> SOFT", out == SOFT)

    # (5) multi-paragraph ambiguous anchor -> loud error.
    raised = False
    try:
        derive_record_coord("Although critics raise the cost", src, norm_paras)
    except AnchorError:
        raised = True
    check("ambiguous anchor -> AnchorError", raised)

    # (5b) an anchor that does not resolve at all -> loud error.
    raised = False
    try:
        derive_record_coord("no such phrase in the source", src, norm_paras)
    except AnchorError:
        raised = True
    check("non-resolving anchor -> AnchorError", raised)

    # (6) interval-overlap edge: adjacent-but-disjoint spans do NOT overlap.
    check("adjacent-disjoint intervals do not overlap",
          _overlap((0, 5), (5, 10)) is False)
    check("touching-by-one intervals overlap", _overlap((0, 6), (5, 10)) is True)
    check("identical intervals overlap", _overlap((3, 8), (3, 8)) is True)
    check("None interval never overlaps",
          _overlap(None, (0, 3)) is False and _overlap((0, 3), None) is False)

    # (7) extras logic (mirrors score_cell): an obs overlapping no record
    #     coordinate is an extra; one overlapping the coordinate is not.
    coords = [rec_coord]
    o_extra = obs("ASSURING", 1, "the review is due next spring")
    is_extra = not any(o_extra["paragraph_index"] == c[0]
                       and _overlap(o_extra["interval"], c[1]) for c in coords)
    check("non-overlapping obs is an extra", is_extra)
    not_extra = not any(o_hit["paragraph_index"] == c[0]
                        and _overlap(o_hit["interval"], c[1]) for c in coords)
    check("overlapping obs is not an extra", not_extra is False)

    # (8) gate evaluator: synthetic results — per-vendor CORRECT + 0 INCORRECT.
    def gcell(vendor, rep, outcome):
        return {"fixture": GATE_FIXTURE, "vendor": vendor, "rep": rep, "error": None,
                "records": [{"idx": GATE_RECORD_IDX, "family": GATE_FAMILY,
                             "locus": "x", "outcome": outcome}]}
    passing = [gcell("fable", 1, CORRECT), gcell("fable", 2, SOFT),
               gcell("codex", 1, CORRECT), gcell("codex", 2, CORRECT)]
    check("gate passes on per-vendor CORRECT + no INCORRECT",
          evaluate_gate(passing)["passed"] is True)
    # a single INCORRECT anywhere fails the gate
    failing = list(passing)
    failing[1] = gcell("fable", 2, INCORRECT)
    check("gate fails on one INCORRECT", evaluate_gate(failing)["passed"] is False)
    # a vendor with no CORRECT rep fails the gate
    no_codex = [gcell("fable", 1, CORRECT), gcell("fable", 2, CORRECT),
                gcell("codex", 1, SOFT), gcell("codex", 2, SOFT)]
    check("gate fails when a vendor has no CORRECT rep",
          evaluate_gate(no_codex)["passed"] is False)
    # an errored gate cell fails the gate
    err_cells = list(passing)
    err_cells[0] = {"fixture": GATE_FIXTURE, "vendor": "fable", "rep": 1,
                    "error": "replay boom", "records": []}
    check("gate fails on an errored cell", evaluate_gate(err_cells)["passed"] is False)

    if fails:
        print("Self-test: FAIL")
        for f in fails:
            print("  - %s" % f)
        return 1
    print("Self-test: PASS (score.py; coordinate derivation + interval matcher + "
          "taxonomy + extras + hard-gate evaluator, synthetic arms, no file IO)")
    return 0


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------
def main(argv):
    if "--self-test" in argv:
        return _selftest()
    do_report = "--report" in argv
    do_write = "--write-report" in argv
    results, gate = run_scoring()
    if do_write:
        report_md = render_report(results, gate)
        appended = write_report(report_md)
        print("§M-AGD %s in %s" % ("appended" if appended else "replaced", _DOCS))
        print(_gate_console(gate))
    elif do_report:
        sys.stdout.write(render_report(results, gate))
    else:
        print(render_console(results, gate))
    return 0 if gate["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
