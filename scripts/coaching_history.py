#!/usr/bin/env python3
"""coaching-history — Coaching History & Pattern Recognition (Coaching Deepening).

`validate.sh coaching-history <project_root> [--strict]` shells out here. Over multiple revision
cycles the coach can surface a cross-session PROCESS pattern — "you tend to defer character-agency
work; the same finding was deferred across three consecutive sessions" — as a rolling, opt-in,
local-only artifact of DESCRIPTIVE observations, each MECHANICALLY derived from recorded session
history (a count over the finding_disposition / finding_states records, never a vibe). A coaching
observation is a claim about the writer's process, so it carries NO editorial severity (no
Must/Should/Could token, no apodictic:finding block); the intensity scale of a manuscript defect is
orthogonal to a process observation (the Author-Voice / Content-Advisory orthogonal-severity
discipline). Each observation is an apodictic.coaching_observation.v1 block; this validator owns the
artifact's contract and its two ethics gates.

This is APODICTIC's ONE ethically-sensitive surface — the two Fable conditions (2026-07-05) are
mechanized here as the load-bearing gates, "mechanical, or don't build":

  H1 schema + unique  a coaching_observation block fails its schema (bad pattern enum, malformed CH-NN
                      id, missing field, broken JSON, dup id within the artifact), OR a per-pattern
                      count floor (deferral-recurrence >=3, phase-incompletion >=2 — Fable-verdict).
  H2 provenance /     every `evidence` reference resolves against the recorded records — each F-id
     anti-fabrication matches ^F-[A-Za-z0-9]+-[0-9]{2,}$ AND a finding_disposition record with
                      disposition=='deferred' exists at the cited session; len(evidence) >= count; the
                      cited session ordinals are ACTUALLY CONSECUTIVE (a gap fails). No fabricated
                      streak. (The author_fingerprint F2 anti-fabrication posture.)
                      SCOPE (Codex review F2): the anti-fabrication GUARANTEE is fabrication-RESISTANT
                      ONLY on GOVERNED projects — the multi-session run is reconstructed from the
                      independent per-session `gate_events[].disposition_deltas` event records the
                      engine wrote at each clear. On NON-GOVERNED projects the session history is
                      SELF-REPORTED by /coach (the folded record's `sessions` list) and is NOT
                      independently verified; so a non-governed deferral-recurrence must carry a
                      VISIBLE honesty caveat that its streak is from the coach's own notes, not a
                      checked record (WARN, ERROR --strict, per-id override) — the writer is never
                      shown an unverified pattern as if it were verified (the H7 principle).
  H3 descriptive,     the observation prose carries a prescriptive directive (author_fingerprint
     not judgmental   _PRESCRIPTIVE_RE) OR a trait-blame construction ("you always / you avoid / you
                      fail to / you're bad at …"). WARN; ERROR --strict; per-id override
                      <!-- override: coaching-observation CH-NN — <why> -->. (KNOWN LIMIT: a lexicon
                      gate catches token framing, not passive trait-attribution — "the pattern
                      suggests reluctance"; semantic validation deferred to v2.)
  H4 no-severity-leak the artifact carries an editorial Must/Should/Could-Fix token (severity_vocab
                      SSoT, M8) or an apodictic:finding block. A process observation is off the
                      editorial scale. ERROR.
  W1 local-only       an external http(s) URL / telemetry reference (author_fingerprint W2). Advisory;
                      ERROR --strict.
  H7 tentative-       (transference-health, operator-directed.) The count is the coach's PRIVATE
     framing          evidence; what reaches the writer is the coach's NOTICING — confident about the
                      pattern, tentative about its MEANING. ENFORCEABLE FLOOR (shape checks over the
                      human-facing `observation`): (a) no third-person trait-attribution VERDICT
                      ("Writer defers endings", "she is an ending-avoider"); (b) no bare-scoreboard
                      rendering (a lone `<label>: <int>` tally with no interpretive prose); (c) the
                      observation offers SOME invitation to the writer's reading (a question / "does
                      that land?"). WARN; ERROR --strict; shares the H3 per-id override slug. HONEST
                      LIMIT: the full "confident about the seeing, open about the meaning" property is a
                      SKILL-contract obligation (the human terminus) — a lexicon/shape gate catches the
                      scoreboard and the bald verdict, not a fluent-but-diagnostic paraphrase; §6a.
  H5 single-home /    (Fable condition a — writer-visible, no coach-only shadow.) Coaching observations
     no-shadow        may persist in EXACTLY ONE writer-facing artifact. H5 scans the project root +
                      runs/* archives over the APODICTIC-authored artifacts PLUS the machine-facing
                      Diagnostic_State.meta.json sidecar (NOT the manuscript). ERROR (non-overridable)
                      on: (i) a parsed coaching_observation block outside the one Coaching_History
                      file; (ii) the literal schema-id outside it; (iii) an evidence-grammar string
                      (`deferred @ session <n>` / `phase <label> incomplete @ session <n>`) outside
                      it; (iv) >1 Coaching_History file; (v) any coaching material in the sidecar
                      beyond exactly `coaching_history_seq: <int>` (recursive JSON walk). WARN
                      (ERROR --strict; override <!-- override: coaching-residue <token> — <why> -->):
                      a bare boundary-guarded CH-NN token elsewhere (chapter-shorthand false-positive).
  H6 deletion-honored (Fable condition b — the record is the writer's, not the tool's.) Under the
     (RECOMPUTE)      `<!-- coaching-history: deleted -->` tombstone the validator RECOMPUTES deletion
                      from artifacts (never trusts the marker — the PR #161 recorded-field rule,
                      disposition_check DP2.6): the full H5 scan must be empty AND no surviving
                      Coaching_History file AND no coaching_history_seq in the sidecar. Any residue =
                      ERROR, NO override accepted. `opted-in` + `deleted` both present = ERROR.

The `delete <project_root>` subcommand honors the deletion in one move: removes every
Coaching_History file (root + runs/*), drops coaching_history_seq from the sidecar, and flips the
Diagnostic_State.md consent marker to `<!-- coaching-history: deleted -->` (deletion revokes consent
— no silent re-derivation). Because H5's always-on projection ban means observations only ever live
in the one deletable artifact, deleting it is complete BY CONSTRUCTION — and H6 re-verifies anyway.

Opt-in: the artifact is only produced under `<!-- coaching-history: opted-in -->`, whose home is
Diagnostic_State.md (writer-visible; the coach reads it at session start); the artifact also
self-carries the marker (content_advisory W2 style; content_advisory._OPT_IN_RE precedent). No marker
anywhere → the validator no-ops (exit 0/2), like content-advisory / legal-risk; tombstone → H6 mode.

Reuses apodictic_artifacts (block grammar + schema engine + parse_blocks + FID_RE) and the shared
override_marker / severity_vocab / author_fingerprint firewall regexes (single-sourced, never
re-derived). Stdlib-only; degrades to an advisory WARN without python3. See docs/coaching-history.md.

  coaching_history.py coaching-history <project_root|files...> [--strict]
  coaching_history.py delete <project_root>
  coaching_history.py --self-test

Exit: 0 clean / WARN-only, 1 ERROR (or WARN under --strict), 2 usage / no artifact.
"""
import glob
import json
import os
import re
import sys

from override_marker import override_targets  # SSoT: code-span-stripped, boundary-matched override scan
from severity_vocab import SEVERITY_TOKEN_RE   # SSoT: the editorial Must/Should/Could-Fix leak token

try:
    import apodictic_artifacts as art
except ImportError:
    art = None

# H3 firewall — reuse the author_fingerprint prescriptive-directive regex (single-sourced; the module
# describes, never prescribes). Imported, never re-derived. Degrades to None if the sibling is absent.
try:
    from author_fingerprint import _PRESCRIPTIVE_RE as _AF_PRESCRIPTIVE_RE
except ImportError:
    _AF_PRESCRIPTIVE_RE = None

_SCHEMA_ID = "apodictic.coaching_observation.v1"
_HISTORY_GLOB = "*_Coaching_History_*.md"
_SIDECAR_NAME = "Diagnostic_State.meta.json"
_STATE_MD = "Diagnostic_State.md"

# The one sidecar key coaching-history is permitted to write (a scalar-in-sidecar, like
# execution.state_version — run_gate.py). Everything else coaching-shaped in the sidecar is a shadow.
_SEQ_KEY = "coaching_history_seq"

# Per-pattern count floors (Fable verdict 2026-07-05; ROADMAP §8.2 CLOSED). The schema keeps only the
# global minimum >=2; H1 enforces these.
_COUNT_FLOOR = {"deferral-recurrence": 3, "phase-incompletion": 2}

# Consent markers (home: Diagnostic_State.md; the artifact self-carries the opt-in too). The opt-in
# pattern mirrors content_advisory._OPT_IN_RE.
_OPT_IN_RE = re.compile(r"<!--\s*coaching-history:\s*opted-in\s*-->", re.IGNORECASE)
_DELETED_RE = re.compile(r"<!--\s*coaching-history:\s*deleted\s*-->", re.IGNORECASE)

# The editorial Must/Should/Could-Fix leak token — the shared severity_vocab SSoT (M8), never a local
# re.compile. Alias kept so the H4 call site reads like the sibling firewalls.
_SEVERITY_RE = SEVERITY_TOKEN_RE

# H3 trait-blame — a coaching-specific lexicon on TOP of the reused prescriptive regex. Catches the
# "you always / you avoid / you fail to / you're bad at / you keep / you never / you can't" framing the
# posture forbids (a claim ABOUT the writer, not a description of a mechanical pattern). Deliberately a
# lexicon gate (the documented limit: it catches token framing, not passive trait-attribution like
# "the pattern suggests reluctance" — semantic validation is a v2 item, same class as F4/W1's).
_TRAIT_BLAME_RE = re.compile(
    r"\byou\s+(?:always|never|constantly|habitually|chronically|keep(?:\s+on)?|tend\s+to\s+always)\b"
    r"|\byou\s+(?:avoid|dodge|evade|shy\s+away\s+from|refuse\s+to|fail\s+to|can'?t\s+seem\s+to|"
    r"struggle\s+to|are\s+unable\s+to|are\s+incapable\s+of)\b"
    r"|\byou'?re\s+(?:bad|weak|hopeless|terrible|lazy|undisciplined|avoidant)\b"
    r"|\byou\s+have\s+(?:a\s+)?(?:problem|weakness|blind\s?spot|habit)\s+(?:with|of)\b",
    re.IGNORECASE)

# H7 trait-verdict — a THIRD-PERSON trait-attribution verdict about the writer ("Writer defers
# endings", "the writer IS an ending-avoider", "she always parks the hard work"). The transference-
# health complement to H3's second-person blame: the meaning must be handed to the writer, never
# asserted as a trait/verdict. Deliberately a lexicon gate (the documented limit — passive attribution
# like "the pattern suggests reluctance" is a SKILL-contract concern, not statically catchable).
_TRAIT_VERDICT_RE = re.compile(
    # "she is an ending-avoider", "the author remains a procrastinator"
    r"\b(?:the\s+writer|writer|author|the\s+author|she|he|they)\s+"
    r"(?:is|are|has\s+become|remains?)\s+(?:an?\s+)?"
    r"(?:\w+[- ]?)?(?:avoid(?:er|ant)|procrastinat(?:or|ing)|deferrer|ducker|shirker|quitter)\b"
    # "writer always/keeps/tends-to-always <verb>"
    r"|\b(?:the\s+writer|writer|author|the\s+author|she|he|they)\s+"
    r"(?:always|never|constantly|habitually|chronically|keeps?|tends?\s+to\s+always)\s+\w+"
    # a bald third-person present-tense process verdict: "Writer defers endings", "the author parks
    # the hard work", "she sets aside structure" — subject + a deferral/avoidance verb, asserted flat.
    r"|\b(?:the\s+writer|writer|the\s+author|author)\s+"
    r"(?:defers?|parks?|avoids?|dodges?|ducks?|shelves?|postpones?|sidesteps?|"
    r"sets?\s+aside|puts?\s+off|backs?\s+away\s+from)\b",
    re.IGNORECASE)
# H7 anti-scoreboard — the human-facing `observation` must be the coach's remembered-attention-plus-
# open-question form, not a bare `<label>: <int>` / `<label> (×N)` tally the writer confronts alone.
# We fire ONLY on the unambiguous scoreboard SHAPE: prose that is (essentially) just a label and a
# number with no interpretive/invitational tissue. `_is_scoreboard` decides; WARN-tier + override,
# because "brief but real prose" must not be punished.
_SCOREBOARD_RE = re.compile(
    r"^\s*[\w '\-]{0,40}?[:\-]?\s*(?:[x×]\s*\d+|\d+\s*(?:times?|sessions?|x)?|\(\s*[x×]?\s*\d+\s*\))\s*\.?\s*$",
    re.IGNORECASE)
# The invitational half (property 2): a question, or an invitation-to-read lexicon. Its ABSENCE on an
# otherwise-terse observation is the WARN signal (the meaning was asserted, not handed over).
_INVITATION_RE = re.compile(
    r"\?"  # an actual question handed to the writer
    r"|\b(?:does\s+that|is\s+that|what\s+do\s+you|how\s+does\s+that|worth\s+a\s+look|"
    r"curious\s+(?:if|whether)|wonder(?:ing)?\s+(?:if|whether)|does\s+it\s+(?:feel|land|track)|"
    r"your\s+(?:read|sense|call)|see\s+it\s+the\s+same|if\s+that\s+(?:fits|lands|tracks|resonates))\b",
    re.IGNORECASE)

# H5 (iii) — the coaching-history evidence grammar, as a bare string signature scanned OUTSIDE the
# artifact. The `@ session <n>` token is coaching-history-specific: it does NOT collide with the pinned
# finding-disposition marker grammar (`<!-- deferred: F-… until: … -->`,
# apodictic_artifacts._DISPOSITION_RE), so a legitimate Coaching-Log disposition marker never trips it.
_EVIDENCE_GRAMMAR_RE = re.compile(
    r"(?:F-[A-Za-z0-9]+-[0-9]{2,}\s+deferred\s+@\s+session\s+\d+"
    r"|phase\s+.+?\s+incomplete\s+@\s+session\s+\d+)",
    re.IGNORECASE)

# H5 WARN — a bare boundary-guarded CH-NN token (the FID_RE boundary style). The guard `(?<![\w-])`
# already excludes an F-CH-01 finding id (the `-` before `CH` is a boundary char that fails the
# lookbehind), so this is the SIGNATURE that can false-positive on chapter shorthand ("CH-12") — hence
# WARN-tier + overridable, while (i)-(iii)/(iv)/(v) stay non-overridable.
_CH_TOKEN_RE = re.compile(r"(?<![\w-])CH-[0-9]{2,}(?![\w-])")

# Per-evidence-item parse grammars (H2). Anchored so a well-formed item resolves cleanly.
_EV_DEFERRAL_RE = re.compile(
    r"^\s*(F-[A-Za-z0-9]+-[0-9]{2,})\s+deferred\s+@\s+session\s+(\d+)\s*$", re.IGNORECASE)
_EV_PHASE_RE = re.compile(
    r"^\s*phase\s+(.+?)\s+incomplete\s+@\s+session\s+(\d+)\s*$", re.IGNORECASE)

_HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)

# F2 (Codex review) — H2's anti-fabrication GUARANTEE holds only on GOVERNED projects (the per-session
# gate_events[].disposition_deltas are independent event records the engine wrote at each clear). On
# NON-GOVERNED projects the multi-session history is a self-reported field on the folded record (the
# `sessions` list /coach persists) — NOT independently verified (the mode-11 recorded-field-without-
# verifier antipattern the spec itself forbids for H6's recompute). So a non-governed `deferral-
# recurrence` observation must carry a VISIBLE honest caveat that its streak came from the coach's own
# session notes, not an independently checked record — the writer must never be shown an unverified
# pattern as if it were verified (the H7 transference-health principle). Cleanly mechanizable as a
# shape check (WARN + per-id override): the observation prose OR the artifact carries a caveat token.
_NONGOVERNED_CAVEAT_RE = re.compile(
    r"from\s+(?:my|the\s+coach'?s?)\s+(?:own\s+)?(?:session\s+)?notes"
    r"|not\s+(?:an?\s+)?independently\s+(?:verified|checked)"
    r"|coach'?s?\s+(?:own\s+)?record|my\s+own\s+notes|unverified\s+(?:against|by)"
    r"|(?:i\s+)?(?:have\s+)?been\s+tracking|from\s+what\s+i(?:'?ve)?\s+(?:been\s+)?track"
    r"|from\s+my\s+notes\s+across",
    re.IGNORECASE)

# H5 scan scope (Codex review F1 — the projection-ban is only as good as its coverage). A project root
# has ~46 tool-authored artifact types (output-structure.md: the pass artifacts, SYNTHESIS.md,
# *_Core_DE_Synthesis_*, *_Editorial_Letter_*, README.md, session plans, …). An allowlist of a handful
# of globs let a projection into any UNLISTED artifact (the editorial letter, the synthesis) escape H5
# AND survive `delete` — a false "deletion honored" — breaking BOTH Fable gates. So:
#
#   (i) parsed apodictic:coaching_observation block + (ii) the literal schema-id string are
#   SELF-IDENTIFYING apodictic markers with ZERO false-positive risk on any legitimate non-coaching
#   file (no editorial letter / session plan / manuscript legitimately carries a coaching_observation
#   block or the schema-id). These are scanned over EVERY *.md in scope, minus the one Coaching_History
#   artifact — the exhaustive net that catches the real projection (a projected block carries both).
#
#   (iii) the evidence-grammar (`@ session <n>`) standalone scan + the bare CH-NN WARN token DO carry
#   manuscript false-positive risk (chapter "CH-12" refs; prose "@ session"), so they stay MANUSCRIPT-
#   EXCLUDED — but the manuscript is excluded POSITIVELY (the frozen `*_Manuscript_Snapshot_*.md` the
#   intake protocol persists; annotation_manifest._SNAPSHOT_GLOB), NOT via an authored-artifact
#   allowlist. A real projection is already caught by (i)/(ii) over all .md; (iii) is the secondary net
#   for grammar-without-block leakage (the §6a paraphrase class).
_MANUSCRIPT_SNAPSHOT_GLOB = "*_Manuscript_Snapshot_*.md"  # the persisted frozen manuscript (positive id)


def _read(path):
    # UnicodeDecodeError included: a non-UTF8 artifact (an archived report) must degrade to the honest
    # skip path (None), never a traceback — the disposition_check adjacent-exception class swept repo-wide.
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except (OSError, UnicodeDecodeError):
        return None


def _newest(paths):
    return max(paths, key=os.path.getmtime) if paths else None


def _glob_multi(dirs, pattern):
    out = []
    for d in dirs:
        out.extend(glob.glob(os.path.join(d, pattern)))
    return sorted(set(out))


def _scan_dirs(project_root):
    """The H5/H6 scan scope: the project root + each runs/* archive dir (the disposition_check DP2.6
    reachable-evidence scope)."""
    dirs = [project_root]
    dirs.extend(sorted(d for d in glob.glob(os.path.join(project_root, "runs", "*")) if os.path.isdir(d)))
    return dirs


def _history_files(project_root):
    """Every *_Coaching_History_*.md in scope (root + runs/*), sorted+deduped."""
    return _glob_multi(_scan_dirs(project_root), _HISTORY_GLOB)


# --------------------------------------------------------------------------- parsing

def parse_observations(text):
    """[(obj_or_None, schema_errs, index), ...] for each apodictic:coaching_observation block."""
    out = []
    if not text or art is None:
        return out
    schema = art.load_schema(_SCHEMA_ID)
    idx = 0
    for btype, obj, jerr in art.parse_blocks(text):
        if btype != "coaching_observation":
            continue
        idx += 1
        where = "coaching_observation #%d" % idx
        if jerr:
            out.append((None, ["%s: invalid JSON — %s" % (where, jerr)], idx))
            continue
        errs = art.validate_obj(obj, schema, where)
        out.append((obj, errs, idx))
    return out


def _overrides(text, slug, target):
    """Overridden ids/tokens for `slug` — via the shared override_marker SSoT (code spans stripped,
    slug boundary-matched), so a marker quoted in a code span is not honored as a live directive."""
    return {t[0] for t in override_targets(text or "", slug, target)}


def _load_sidecar(project_root):
    """Return (obj_or_None, parse_ok). A missing sidecar is (None, True) — not an error here (H5 walks
    it only when present). A present-but-unparseable sidecar is (None, False)."""
    path = os.path.join(project_root, _SIDECAR_NAME)
    if not os.path.exists(path):
        return None, True
    raw = _read(path)
    if raw is None:
        return None, False
    try:
        return json.loads(raw), True
    except json.JSONDecodeError:
        return None, False


def _walk_json_strings(node):
    """Yield every string VALUE anywhere in a parsed-JSON tree (recursive; keys handled by the caller)."""
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for v in node.values():
            yield from _walk_json_strings(v)
    elif isinstance(node, list):
        for v in node:
            yield from _walk_json_strings(v)


def _walk_json_keys(node):
    """Yield every KEY string anywhere in a parsed-JSON tree (recursive)."""
    if isinstance(node, dict):
        for k, v in node.items():
            yield k
            yield from _walk_json_keys(v)
    elif isinstance(node, list):
        for v in node:
            yield from _walk_json_keys(v)


def _sidecar_seq(sidecar_obj):
    """The recorded coaching_history_seq (an int) if present anywhere the loaders write it, else None.
    v1 home: top-level `coaching_history_seq`. Also accept execution.coaching_history_seq (a governed
    sidecar may nest scalars under execution, like state_version) — either is the ONE permitted key."""
    if not isinstance(sidecar_obj, dict):
        return None
    if isinstance(sidecar_obj.get(_SEQ_KEY), int) and not isinstance(sidecar_obj.get(_SEQ_KEY), bool):
        return sidecar_obj[_SEQ_KEY]
    ex = sidecar_obj.get("execution")
    if isinstance(ex, dict) and isinstance(ex.get(_SEQ_KEY), int) and not isinstance(ex.get(_SEQ_KEY), bool):
        return ex[_SEQ_KEY]
    return None


# --------------------------------------------------------------------------- H2 provenance

def _is_governed(sidecar_obj):
    """True iff the sidecar carries a non-empty execution.gate_events log (the state-lifecycle dual-
    writer split; the same test disposition_check.check uses). On a governed project the per-session
    disposition_deltas are independent event records — H2's anti-fabrication guarantee holds; on a
    non-governed project the multi-session history is self-reported (F2)."""
    if not isinstance(sidecar_obj, dict):
        return False
    ex = sidecar_obj.get("execution")
    return isinstance(ex, dict) and bool(ex.get("gate_events"))


def _deferred_history(sidecar_obj):
    """{F-id: set(session ordinals at which the finding was `deferred`)} — reconstructed from BOTH
    disposition surfaces (spec §4):

      * NON-GOVERNED — the folded `execution.finding_dispositions` map is last-event-wins (docs/finding-
        dispositions.md), so it attests at most ONE deferred session per finding directly. A richer
        writer may also keep the full history on the record under `sessions`/`deferred_sessions`
        (accepted defensively).
      * GOVERNED — each `execution.gate_events[]` event carries `disposition_deltas` (the full per-run
        disposition records, each with its OWN `session` ordinal — run_gate._disposition_deltas), so the
        UNBROKEN multi-session deferral run reconstructs from the event log even though the fold keeps
        only the latest. This is the surface H2's consecutive-run proof needs on governed projects.

    A malformed/absent surface contributes nothing (H2 then reports the reference unresolved — fail-
    closed). This is the ONLY provenance read; a session H2 cannot find HERE is a fabricated streak
    member, no matter what the observation asserts."""
    hist = {}

    def _add(fid, session):
        if isinstance(fid, str) and isinstance(session, int) and not isinstance(session, bool):
            hist.setdefault(fid, set()).add(session)

    if not isinstance(sidecar_obj, dict):
        return hist
    ex = sidecar_obj.get("execution")
    if not isinstance(ex, dict):
        return hist

    # non-governed / folded surface (+ any defensive history list)
    recs = ex.get("finding_dispositions")
    if isinstance(recs, dict):
        for fid, rec in recs.items():
            if isinstance(rec, dict) and rec.get("disposition") == "deferred":
                _add(rec.get("id") or fid, rec.get("session"))
                for key in ("sessions", "deferred_sessions"):
                    for x in (rec.get(key) or []) if isinstance(rec.get(key), list) else []:
                        _add(rec.get("id") or fid, x)

    # governed surface: the full per-event delta log (each delta carries its own session ordinal)
    events = ex.get("gate_events")
    if isinstance(events, list):
        for ev in events:
            if not isinstance(ev, dict):
                continue
            dd = ev.get("disposition_deltas")
            if not isinstance(dd, dict):
                continue
            for fid, rec in dd.items():
                if isinstance(rec, dict) and rec.get("disposition") == "deferred":
                    _add(rec.get("id") or fid, rec.get("session"))
    return hist


# --------------------------------------------------------------------------- the core check

def check(text, project_root=None, sidecar_obj=None, strict=False, *, scan_root=None,
          consent="opted-in"):
    """Run the coaching-history integrity checks over an already-read artifact `text`.

    `consent` ∈ {"opted-in", "deleted", "none"} is resolved by the caller from Diagnostic_State.md +
    the artifact self-marker. `scan_root` (defaults to project_root) is the H5/H6 scan scope. Returns
    (code, lines)."""
    lines, errs, warns = [], [], []
    if art is None:
        return 2, ["coaching-history: apodictic_artifacts unavailable — cannot run"]
    root = scan_root or project_root

    # ---- H6 short-circuits: a tombstone means RECOMPUTE deletion; opted-in artifact checks do not run.
    if consent == "deleted":
        return _h6_recompute(root, sidecar_obj, strict)

    observations = parse_observations(text)
    if not observations:
        lines.append("coaching-history: no coaching_observation blocks found — prose-level checks only")

    # ---- H1 — schema / JSON / per-pattern count floor / unique id
    for obj, schema_errs, _idx in observations:
        for e in schema_errs:
            errs.append("H1 schema: %s" % e)
    valid = [(obj, idx) for obj, schema_errs, idx in observations
             if isinstance(obj, dict) and not schema_errs]
    seen = {}
    for obj, idx in valid:
        seen.setdefault(art.fid_key(obj.get("id")), []).append(idx)
    for cid, where in sorted(seen.items(), key=lambda kv: str(kv[0])):
        if len(where) > 1:
            errs.append("H1 schema: %s appears %d times (ids must be unique)" % (cid, len(where)))
    for obj, _idx in valid:
        floor = _COUNT_FLOOR.get(obj.get("pattern"))
        cnt = obj.get("count")
        if floor is not None and isinstance(cnt, int) and not isinstance(cnt, bool) and cnt < floor:
            errs.append("H1 count floor: %s is a %s with count=%d — the Fable-verdict floor is >=%d"
                        % (obj.get("id"), obj.get("pattern"), cnt, floor))

    # ---- H2 — provenance / anti-fabrication
    deferred_hist = _deferred_history(sidecar_obj)
    for obj, _idx in valid:
        errs.extend(_h2_check(obj, deferred_hist))

    # ---- H2 non-governed honesty caveat (Codex F2). On a NON-governed project the deferral streak's
    #      multi-session history is self-reported (not independently verified), so a `deferral-recurrence`
    #      observation must carry a VISIBLE caveat that the streak is from the coach's own notes — the
    #      writer must never see an unverified pattern as if it were checked (the H7 principle). WARN;
    #      ERROR --strict; per-id override (shares the coaching-observation slug). Governed projects are
    #      exempt (their per-session event records ARE the independent verification).
    ov_caveat_ids = _overrides(text, "coaching-observation", r"(CH-[0-9]+)")
    if not _is_governed(sidecar_obj):
        for obj, _idx in valid:
            cid = obj.get("id")
            if obj.get("pattern") != "deferral-recurrence" or cid in ov_caveat_ids:
                continue
            carrier = (obj.get("observation") or "") + "\n" + (text or "")
            if not _NONGOVERNED_CAVEAT_RE.search(carrier):
                warns.append("H2 non-governed caveat: %s is a deferral-recurrence on a NON-governed "
                             "project (no gate_events) — its streak is from the coach's own session "
                             "notes, not an independently verified record. State that honestly in the "
                             "observation (e.g. 'from what I've been tracking across sessions') so the "
                             "writer never sees an unverified pattern as if it were checked" % cid)

    # ---- H4 — no editorial-severity leak (the observation is off the editorial scale)
    #      Scan the WHOLE artifact (blocks + prose): a severity token or a finding block anywhere leaks.
    if _SEVERITY_RE.search(text or ""):
        errs.append("H4 severity leak: the Coaching History carries an editorial Must/Should/Could-Fix "
                    "token — a process observation is off the editorial severity scale")
    if _has_block(text, "finding"):
        errs.append("H4 severity leak: the Coaching History contains an apodictic:finding block — a "
                    "coaching observation is not a finding")

    # ---- H3 — descriptive, not judgmental (per-id override)
    ov_ids = _overrides(text, "coaching-observation", r"(CH-[0-9]+)")
    for obj, _idx in valid:
        cid = obj.get("id")
        prose = obj.get("observation") or ""
        if cid in ov_ids:
            continue
        if (_AF_PRESCRIPTIVE_RE is not None and _AF_PRESCRIPTIVE_RE.search(prose)) \
                or _TRAIT_BLAME_RE.search(prose):
            warns.append("H3 descriptive: %s's observation prescribes or blames a trait ('you always / "
                         "you fail to / fix your …') — the coach surfaces a pattern, it does not judge "
                         "the writer" % cid)

    # ---- H7 — transference-health / tentative framing (the count is the coach's private EVIDENCE;
    #      what reaches the writer is the coach's noticing — confident about the pattern, open about
    #      its meaning). ENFORCEABLE FLOOR (shape checks); the full confident-observation + writer-owns-
    #      the-meaning property is a SKILL-contract obligation (the human terminus), stated in §6a/docs.
    #      Shares the per-id override slug with H3 (one framing override per observation).
    for obj, _idx in valid:
        cid = obj.get("id")
        prose = (obj.get("observation") or "").strip()
        if cid in ov_ids:
            continue
        # (a) a third-person trait-attribution VERDICT ("Writer defers endings", "she is an avoider")
        if _TRAIT_VERDICT_RE.search(prose):
            warns.append("H7 tentative-framing: %s's observation asserts a trait VERDICT about the "
                         "writer ('writer defers …', 'is an … -avoider') — hand the meaning to the "
                         "writer as an open question, do not assert it as a trait" % cid)
        # (b) a bare-scoreboard rendering (a lone `<label>: <int>` tally, no interpretive prose)
        elif _is_scoreboard(prose):
            warns.append("H7 anti-scoreboard: %s's observation renders as a bare `<label>: <count>` "
                         "scoreboard — the count is the coach's evidence, not the writer's tally; state "
                         "it as remembered attention plus an open question" % cid)
        # (c) confident-observation with NO invitational half (the meaning was asserted, not handed over)
        elif prose and not _INVITATION_RE.search(prose):
            warns.append("H7 tentative-framing: %s's observation offers no invitation to the writer's "
                         "reading (a question / 'does that land?') — be confident about the pattern but "
                         "hand its meaning to the writer" % cid)

    # ---- W1 — local-only hygiene (no external/telemetry reference)
    visible = _HTML_COMMENT_RE.sub("", text or "")
    if re.search(r"https?://", visible, re.IGNORECASE):
        warns.append("W1 local-only: the Coaching History references an external http(s) URL — the "
                     "artifact is local-only and makes no external call")

    # ---- H5 — single-home / no coach-only shadow (Fable condition a). Non-overridable (i)-(v).
    if root is not None:
        h5_errs, h5_warns = _h5_scan(root, sidecar_obj, strict, self_history_text=text)
        errs.extend(h5_errs)
        warns.extend(h5_warns)

    # ---- Report
    lines.append("coaching-history: %d observation(s)%s" % (
        len(observations), "" if len(valid) == len(observations)
        else " (%d well-formed)" % len(valid)))
    for obj, _idx in valid:
        lines.append("  %-7s %-20s count=%s" % (obj.get("id"), obj.get("pattern"), obj.get("count")))
    for e in errs:
        lines.append("  ERROR: %s" % e)
    for w in warns:
        lines.append("  %s: %s" % ("ERROR (--strict)" if strict else "WARN", w))

    if errs or (strict and warns):
        lines.append("coaching-history: FAIL (%d error(s)%s)"
                     % (len(errs), ", %d strict warn(s)" % len(warns) if (strict and warns) else ""))
        return 1, lines
    if warns:
        lines.append("WARN: coaching-history: %d advisory gap(s) — see H3/H7/W1/H5 above" % len(warns))
    else:
        lines.append("coaching-history: PASS (schema + provenance + descriptive + tentative-framing + "
                     "no-severity-leak + single-home + local-only)")
    return 0, lines


def _h2_check(obj, deferred_hist):
    """H2 for one valid observation: len(evidence) >= count, each reference resolves and (for
    deferral-recurrence) corroborates a recorded deferred disposition at the cited session
    (`deferred_hist` = {F-id: set(sessions)} from _deferred_history), and the cited sessions are
    ACTUALLY CONSECUTIVE (a gap fails). Returns a list of error strings."""
    errs = []
    cid = obj.get("id")
    pattern = obj.get("pattern")
    count = obj.get("count")
    evidence = obj.get("evidence")
    if not isinstance(evidence, list):
        return errs  # a non-array evidence is already an H1 schema type error
    if isinstance(count, int) and not isinstance(count, bool) and len(evidence) < count:
        errs.append("H2 provenance: %s has len(evidence)=%d < count=%d — the streak is not fully "
                    "evidenced" % (cid, len(evidence), count))
    sessions = []
    for item in evidence:
        if not isinstance(item, str):
            errs.append("H2 provenance: %s has a non-string evidence item %r" % (cid, item))
            continue
        if pattern == "deferral-recurrence":
            m = _EV_DEFERRAL_RE.match(item)
            if not m:
                errs.append("H2 provenance: %s evidence %r does not match the grammar "
                            "`<F-id> deferred @ session <n>`" % (cid, item))
                continue
            fid, sess = m.group(1), int(m.group(2))
            if not art.FID_RE.fullmatch(fid):
                errs.append("H2 provenance: %s cites a malformed finding id %r" % (cid, fid))
                continue
            recorded = deferred_hist.get(fid, set())
            if sess not in recorded:
                errs.append("H2 provenance: %s cites `%s deferred @ session %d` but no recorded "
                            "deferred disposition for %s at session %d — a fabricated streak member"
                            % (cid, fid, sess, fid, sess))
            sessions.append(sess)
        elif pattern == "phase-incompletion":
            m = _EV_PHASE_RE.match(item)
            if not m:
                errs.append("H2 provenance: %s evidence %r does not match the grammar "
                            "`phase <label> incomplete @ session <n>`" % (cid, item))
                continue
            sessions.append(int(m.group(2)))
        else:
            continue  # pattern already refused by H1
    # consecutive-session proof: the cited ordinals must form an unbroken run (no gap, no dup)
    if sessions:
        uniq = sorted(set(sessions))
        if len(uniq) != len(sessions):
            errs.append("H2 provenance: %s cites a session ordinal twice — a streak member is not "
                        "distinct" % cid)
        elif uniq != list(range(uniq[0], uniq[0] + len(uniq))):
            errs.append("H2 provenance: %s cites non-consecutive sessions %s — a gap resets the streak"
                        % (cid, uniq))
    return errs


def _has_block(text, btype):
    """True if `text` carries a real apodictic:<btype> block (a parsed carrier, not a prose mention) —
    the content_advisory._has_block discipline (meta-linter M2)."""
    if art is None:
        return ("apodictic:%s" % btype) in (text or "")
    return any(bt == btype for bt, _o, _e in art.parse_blocks(text or ""))


def _is_scoreboard(prose):
    """True if the human-facing `observation` reads as a bare scoreboard tally — a lone
    `<label>: <int>` / `<label> (×N)` / `<label> — N times` with no interpretive/invitational tissue —
    rather than the coach's remembered-attention-plus-open-question form. Conservative: fires only when
    EVERY non-empty line matches the scoreboard shape (so real prose that merely contains a number is
    never flagged), or when the whole thing is a single short scoreboard clause. The transference-health
    rule's enforceable floor (the count is the coach's private evidence, never the writer's scoreboard)."""
    text = (prose or "").strip()
    if not text:
        return False
    lines = [ln for ln in text.splitlines() if ln.strip()]
    return bool(lines) and all(_SCOREBOARD_RE.match(ln) for ln in lines)


# --------------------------------------------------------------------------- H5 single-home scan

def _h5_scan(project_root, sidecar_obj, strict, self_history_text=None):
    """H5 (Fable condition a): scan project root + runs/* for a projected coaching observation, plus the
    sidecar. Returns (errs, warns). `self_history_text` is unused here — the ONE Coaching_History
    artifact is identified by the glob and excluded from the projection scan (it IS the single home).

    Codex F1: the projection scan covers EVERY *.md in scope (not a fragile authored-artifact allowlist
    that let a projection into the editorial letter / synthesis escape and survive `delete`):
      * (i) a parsed apodictic:coaching_observation block and (ii) the literal schema-id string are
        self-identifying apodictic markers — scanned over ALL *.md minus the one Coaching_History file
        (incl. the frozen manuscript snapshot: the writer's prose never legitimately carries a
        coaching_observation block or the schema-id, so a hit there IS a pasted projection). ERROR.
      * (iii) the evidence-grammar standalone scan + the bare CH-NN WARN token carry manuscript
        false-positive risk (chapter "CH-12"; prose "@ session"), so they are scanned over all *.md
        MINUS the positively-identified manuscript snapshot(s). A real projection is already caught by
        (i)/(ii); (iii) is the secondary net for grammar-without-block leakage (§6a paraphrase)."""
    errs, warns = [], []
    dirs = _scan_dirs(project_root)

    # (iv) — exactly one Coaching_History file in scope. A second file IS the shadow artifact.
    hist_files = _glob_multi(dirs, _HISTORY_GLOB)
    if len(hist_files) > 1:
        errs.append("H5.iv single-home: %d *_Coaching_History_*.md files in scope (%s) — single-home "
                    "means exactly one; a second file is the shadow artifact"
                    % (len(hist_files), ", ".join(os.path.basename(f) for f in hist_files)))

    hist_abs = {os.path.abspath(f) for f in hist_files}
    manuscript_abs = {os.path.abspath(f) for f in _glob_multi(dirs, _MANUSCRIPT_SNAPSHOT_GLOB)}

    # EVERY *.md in scope, minus the one Coaching_History artifact (the single home is exempt from its
    # own content). This is the exhaustive net Codex F1 requires — no artifact-type escapes it.
    for path in _glob_multi(dirs, "*.md"):
        ap = os.path.abspath(path)
        if ap in hist_abs:
            continue
        body = _read(path)
        if body is None:
            continue
        name = os.path.basename(path)
        # (i) a parsed coaching_observation block anywhere but the one history file — ALL .md, no
        #     manuscript exclusion (a block in the manuscript snapshot IS a pasted projection).
        if _has_block(body, "coaching_observation"):
            errs.append("H5.i single-home: %s carries an apodictic:coaching_observation block — "
                        "observations live ONLY in the Coaching History artifact (no projection)"
                        % name)
        # (ii) the literal schema-id string outside the artifact — ALL .md, no manuscript exclusion.
        if _SCHEMA_ID in body:
            errs.append("H5.ii single-home: %s carries the literal schema-id %r outside the "
                        "Coaching History artifact" % (name, _SCHEMA_ID))
        # (iii)/(CH-token) carry manuscript false-positive risk — SKIP the frozen manuscript snapshot.
        if ap in manuscript_abs:
            continue
        # (iii) an evidence-grammar string outside the artifact (the secondary grammar-leak net)
        if _EVIDENCE_GRAMMAR_RE.search(body):
            errs.append("H5.iii single-home: %s carries a coaching-history evidence-grammar string "
                        "(`… @ session <n>`) outside the Coaching History artifact" % name)
        # WARN (overridable) — a bare boundary-guarded CH-NN token (chapter-shorthand false-positive)
        for tok in set(_CH_TOKEN_RE.findall(body)):
            if not override_targets(body, "coaching-residue", re.escape(tok)):
                warns.append("H5 bare CH-token: %s references %s outside the Coaching History "
                             "artifact (bare-token; chapter-shorthand false-positive risk — "
                             "override <!-- override: coaching-residue %s — <why> --> if intended)"
                             % (name, tok, tok))

    # (v) — sidecar walk: NO coaching material beyond exactly `coaching_history_seq: <int>`.
    if sidecar_obj is not None:
        errs.extend(_h5_sidecar_walk(sidecar_obj))

    return errs, warns


def _h5_sidecar_walk(sidecar_obj):
    """H5 (v): a recursive key/value walk over the parsed sidecar JSON. The machine-facing sidecar is
    exactly where a coach-only shadow would accumulate invisibly, so this is strict: ERROR on any key
    matching `coaching*` OTHER than exactly `coaching_history_seq` (an int), or any string VALUE anywhere
    matching the CH-id regex, the schema-id, or the evidence grammar. Returns a list of errors."""
    errs = []
    for key in _walk_json_keys(sidecar_obj):
        low = key.lower()
        if low.startswith("coaching") and key != _SEQ_KEY:
            errs.append("H5.v sidecar shadow: the sidecar carries a coaching-shaped key %r — the ONLY "
                        "permitted coaching-history key is %r (an int)" % (key, _SEQ_KEY))
    # the permitted key, if present, must be an int (not a shadow payload smuggled under the blessed name)
    seq_holders = []
    if isinstance(sidecar_obj, dict):
        if _SEQ_KEY in sidecar_obj:
            seq_holders.append(sidecar_obj[_SEQ_KEY])
        ex = sidecar_obj.get("execution")
        if isinstance(ex, dict) and _SEQ_KEY in ex:
            seq_holders.append(ex[_SEQ_KEY])
    for v in seq_holders:
        if not (isinstance(v, int) and not isinstance(v, bool)):
            errs.append("H5.v sidecar shadow: %r must be an integer, not %r (a non-int under the "
                        "blessed key is a smuggled shadow)" % (_SEQ_KEY, v))
    for val in _walk_json_strings(sidecar_obj):
        if _CH_TOKEN_RE.search(val) or (_SCHEMA_ID in val) or _EVIDENCE_GRAMMAR_RE.search(val):
            errs.append("H5.v sidecar shadow: the sidecar carries coaching-observation material in a "
                        "string value (%r) — the sidecar is machine-facing; observations live ONLY in "
                        "the writer-visible Coaching History artifact" % (val[:80]))
    return errs


# --------------------------------------------------------------------------- H6 recompute

def _h6_recompute(project_root, sidecar_obj, strict):
    """H6 (Fable condition b): under the `<!-- coaching-history: deleted -->` tombstone, RECOMPUTE the
    deletion from artifacts — never trust the marker (the PR #161 recorded-field rule, disposition_check
    DP2.6). Deletion is honored iff: the full H5 scan is empty AND no surviving Coaching_History file AND
    no coaching_history_seq in the sidecar. Any residue = ERROR, NO override accepted (deletion honoring
    grants no override relief — the laundering-firewall posture). Returns (code, lines)."""
    lines, errs = [], []
    lines.append("coaching-history: tombstone present — RECOMPUTING deletion from artifacts "
                 "(marker not trusted)")
    dirs = _scan_dirs(project_root)

    # (1) no surviving Coaching_History file
    hist = _glob_multi(dirs, _HISTORY_GLOB)
    for f in hist:
        errs.append("H6 residue: a Coaching History artifact survives deletion — %s (delete removes "
                    "every *_Coaching_History_*.md from the root and runs/*)" % os.path.basename(f))

    # (2) no coaching_history_seq in the sidecar
    if sidecar_obj is not None:
        seq = _sidecar_seq(sidecar_obj)
        if seq is not None:
            errs.append("H6 residue: coaching_history_seq=%r survives in the sidecar — deletion drops "
                        "the seq (a surviving counter is a re-derivation seed)" % seq)

    # (3) the full H5 scan must come up empty — a projection surviving in ANY authored artifact or the
    #     sidecar is residue. Under the tombstone even the bare-token WARN escalates to ERROR ONLY via
    #     --strict; the (i)-(iii)/(iv)/(v) signatures are hard-FAIL regardless.
    h5_errs, h5_warns = _h5_scan(project_root, sidecar_obj, strict)
    for e in h5_errs:
        errs.append("H6 residue: %s" % e)
    if strict:
        for w in h5_warns:
            errs.append("H6 residue (--strict): %s" % w)
    elif h5_warns:
        for w in h5_warns:
            lines.append("  WARN: %s" % w)

    for e in errs:
        lines.append("  ERROR: %s" % e)
    if errs:
        lines.append("coaching-history: FAIL (%d deletion-residue error(s) — no override accepted)"
                     % len(errs))
        return 1, lines
    lines.append("coaching-history: PASS (deletion honored — recomputed clean: no artifact, no seq, "
                 "no projection)")
    return 0, lines


# --------------------------------------------------------------------------- consent resolution

def _resolve_consent(project_root, artifact_text=None):
    """Resolve the consent state from Diagnostic_State.md (the marker home) + the artifact self-marker.
    Returns "deleted" | "opted-in" | "none". `opted-in` + `deleted` co-present anywhere = raise a flag
    the caller turns into an ERROR (contradictory consent state)."""
    state_md = _read(os.path.join(project_root, _STATE_MD)) or ""
    art_text = artifact_text or ""
    opted = bool(_OPT_IN_RE.search(state_md) or _OPT_IN_RE.search(art_text))
    deleted = bool(_DELETED_RE.search(state_md) or _DELETED_RE.search(art_text))
    if opted and deleted:
        return "contradiction"
    if deleted:
        return "deleted"
    if opted:
        return "opted-in"
    return "none"


# --------------------------------------------------------------------------- resolution / run

def resolve(paths):
    """Resolve the CLI paths to (project_root, artifact_or_None). One dir arg = the project root
    (H5/H6 scan scope); the artifact is the newest *_Coaching_History_*.md in scope. Explicit files:
    the project_root is the artifact's dir and the artifact is the first file carrying a parsed
    coaching_observation block (or, failing that, the first *_Coaching_History_* name)."""
    if len(paths) == 1 and os.path.isdir(paths[0]):
        root = paths[0]
        return root, _newest(_history_files(root))
    # explicit files
    artifact = None
    for p in paths:
        if _has_block(_read(p) or "", "coaching_observation"):
            artifact = p
            break
    if artifact is None:
        for p in paths:
            if re.search(r"_Coaching_History_", os.path.basename(p)):
                artifact = p
                break
    root = os.path.dirname(artifact) or "." if artifact else (os.path.dirname(paths[0]) or ".")
    return root, artifact


def run(paths, strict=False):
    if art is None:
        return 2, ["coaching-history: apodictic_artifacts unavailable — cannot run"]
    project_root, artifact = resolve(paths)
    sidecar_obj, sidecar_ok = _load_sidecar(project_root)
    artifact_text = _read(artifact) if artifact else None

    consent = _resolve_consent(project_root, artifact_text)
    if consent == "contradiction":
        return 1, ["coaching-history: FAIL (1 error(s))",
                   "  ERROR: H6 consent contradiction: Diagnostic_State.md carries BOTH "
                   "`<!-- coaching-history: opted-in -->` and `<!-- coaching-history: deleted -->` — "
                   "deletion revokes consent; the two states cannot coexist"]

    if not sidecar_ok:
        # a present-but-unparseable sidecar is fail-closed under any consent state (H5.v cannot be
        # verified, H2 provenance cannot resolve).
        return 1, ["coaching-history: FAIL (1 error(s))",
                   "  ERROR: H0 unparseable sidecar: %s is present but not valid JSON — the single-home "
                   "walk and provenance cannot be verified" % _SIDECAR_NAME]

    if consent == "deleted":
        return _h6_recompute(project_root, sidecar_obj, strict)

    if consent == "none":
        return 2, ["coaching-history: no opt-in marker (`<!-- coaching-history: opted-in -->` in "
                   "%s or the artifact) and no tombstone — the surface is opt-in; nothing to check"
                   % _STATE_MD]

    # opted-in: the artifact must exist to check.
    if artifact is None or artifact_text is None:
        return 2, ["coaching-history: opted-in but no *_Coaching_History_*.md artifact resolved — "
                   "nothing to check yet"]
    return check(artifact_text, project_root=project_root, sidecar_obj=sidecar_obj, strict=strict,
                 consent="opted-in")


# --------------------------------------------------------------------------- the `delete` command

def delete(project_root):
    """`coaching_history.py delete <project_root>` — honor the writer's deletion in one move:
      (1) remove every *_Coaching_History_*.md from the project root AND runs/* archives;
      (2) drop coaching_history_seq from the sidecar (top-level and execution.*);
      (3) flip the Diagnostic_State.md consent marker to `<!-- coaching-history: deleted -->`
          (deletion revokes consent — no silent re-derivation; regeneration needs a fresh opt-in).
    Returns (code, lines). Idempotent: re-running on an already-deleted project is a clean no-op."""
    lines = []
    if not os.path.isdir(project_root):
        return 2, ["coaching-history delete: %s is not a directory" % project_root]
    dirs = _scan_dirs(project_root)

    # (1) remove the artifact(s)
    removed = []
    for f in _glob_multi(dirs, _HISTORY_GLOB):
        try:
            os.remove(f)
            removed.append(os.path.basename(f))
        except OSError as ex:
            return 1, ["coaching-history delete: FAIL — could not remove %s (%s)" % (f, ex)]
    lines.append("  removed %d Coaching History artifact(s): %s"
                 % (len(removed), ", ".join(removed) if removed else "(none)"))

    # (2) drop coaching_history_seq from the sidecar
    sc_path = os.path.join(project_root, _SIDECAR_NAME)
    if os.path.exists(sc_path):
        raw = _read(sc_path)
        if raw is None:
            return 1, ["coaching-history delete: FAIL — %s is present but unreadable" % _SIDECAR_NAME]
        try:
            sc = json.loads(raw)
        except json.JSONDecodeError as ex:
            return 1, ["coaching-history delete: FAIL — %s is not valid JSON (%s); refusing to write"
                       % (_SIDECAR_NAME, ex)]
        dropped = False
        if isinstance(sc, dict):
            if _SEQ_KEY in sc:
                del sc[_SEQ_KEY]
                dropped = True
            ex = sc.get("execution")
            if isinstance(ex, dict) and _SEQ_KEY in ex:
                del ex[_SEQ_KEY]
                dropped = True
        if dropped:
            with open(sc_path, "w", encoding="utf-8", newline="\n") as fh:
                json.dump(sc, fh, indent=2, ensure_ascii=False)
                fh.write("\n")
            lines.append("  dropped %s from the sidecar" % _SEQ_KEY)
        else:
            lines.append("  no %s in the sidecar (nothing to drop)" % _SEQ_KEY)
    else:
        lines.append("  no sidecar present (nothing to drop)")

    # (3) flip the Diagnostic_State.md consent marker to the tombstone
    state_path = os.path.join(project_root, _STATE_MD)
    state = _read(state_path) if os.path.exists(state_path) else None
    if state is None:
        # no state file — write a minimal one carrying the tombstone so the deletion is discoverable
        state = ""
    tombstone = "<!-- coaching-history: deleted -->"
    if _OPT_IN_RE.search(state):
        state = _OPT_IN_RE.sub(tombstone, state)
    elif not _DELETED_RE.search(state):
        # no opt-in and no existing tombstone — append the tombstone
        state = (state.rstrip("\n") + "\n\n" + tombstone + "\n") if state.strip() else (tombstone + "\n")
    # if a tombstone already present and no opt-in, leave as-is (idempotent)
    with open(state_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(state)
    lines.append("  flipped %s consent marker to the tombstone (deletion revokes consent)" % _STATE_MD)

    lines.append("coaching-history delete: DONE — the record is the writer's; re-run "
                 "`coaching-history <project_root>` to verify the H6 recompute is clean")
    return 0, lines


# --------------------------------------------------------------------------- self-test

def run_self_test():
    import json as _j
    import shutil
    import tempfile
    rc = {"v": 0}

    def chk(name, cond):
        print("  %s: %s" % (name, "OK" if cond else "FAIL"))
        if not cond:
            rc["v"] = 1

    # non-UTF8 read degrades to None (never a traceback) — the swept adjacent-exception class
    _fd, _nu = tempfile.mkstemp(suffix=".md")
    with os.fdopen(_fd, "wb") as _fh:
        _fh.write(b"\xff\xfenot utf-8\xff")
    chk("non_utf8_read_returns_none", _read(_nu) is None)
    os.unlink(_nu)

    OPT = "<!-- coaching-history: opted-in -->\n\n"

    def obs(cid="CH-01", pattern="deferral-recurrence", count=3,
            evidence=None, observation="From what I've been tracking across our sessions, the same "
                                        "thread got set aside the last three running. Does that match "
                                        "how it feels from where you sit, or is something else pulling "
                                        "first?"):
        if evidence is None:
            evidence = ["F-P5-01 deferred @ session 1", "F-P5-01 deferred @ session 2",
                        "F-P5-01 deferred @ session 3"]
        o = {"schema": _SCHEMA_ID, "id": cid, "pattern": pattern, "count": count,
             "evidence": list(evidence), "observation": observation}
        return "<!-- apodictic:coaching_observation\n%s\n-->" % _j.dumps(o)

    # a sidecar carrying the recorded deferred dispositions H2 corroborates against. The folded map is
    # last-event-wins, so we attach the full deferral history for the consecutive-run proof.
    def sidecar(seq=1, deferred=None):
        recs = {}
        if deferred:
            for fid, sessions in deferred.items():
                recs[fid] = {"schema": "apodictic.finding_disposition.v1", "id": fid,
                             "disposition": "deferred", "reason": "held", "source": "author",
                             "session": sessions[-1], "ts": "2026-01-01", "trigger": "next pass",
                             "sessions": list(sessions)}
        sc = {"project": "P", _SEQ_KEY: seq, "execution": {"finding_dispositions": recs}}
        return sc

    DEF3 = {"F-P5-01": [1, 2, 3]}

    # ---- H1 / H2 clean (the canonical good observation)
    code, _ = check(OPT + obs(), project_root=None, sidecar_obj=sidecar(deferred=DEF3),
                    scan_root=None)
    chk("clean_deferral_recurrence", code == 0)

    # phase-incompletion floor is 2
    phase_obs = obs(cid="CH-02", pattern="phase-incompletion", count=2,
                    evidence=["phase Structural Root Causes incomplete @ session 4",
                              "phase Structural Root Causes incomplete @ session 5"],
                    observation="The structural-root-causes phase has stayed open the last two "
                                "sessions. Does that reflect the plan, or is it asking for attention?")
    chk("clean_phase_incompletion",
        check(OPT + phase_obs, sidecar_obj=sidecar(deferred=DEF3))[0] == 0)

    # ---- H1 — schema
    chk("h1_bad_pattern", check(OPT + obs(pattern="stuck-point-cluster"), sidecar_obj=sidecar(deferred=DEF3))[0] == 1)
    chk("h1_bad_id", check(OPT + obs(cid="CH-1"), sidecar_obj=sidecar(deferred=DEF3))[0] == 1)
    chk("h1_bad_json",
        check(OPT + '<!-- apodictic:coaching_observation\n{"schema":"apodictic.coaching_observation.v1"\n-->',
              sidecar_obj=sidecar(deferred=DEF3))[0] == 1)
    chk("h1_dup_id",
        check(OPT + obs() + "\n" + obs(), sidecar_obj=sidecar(deferred=DEF3))[0] == 1)
    # per-pattern count floor: deferral-recurrence with count=2 fails (floor is 3)
    chk("h1_deferral_floor",
        check(OPT + obs(count=2, evidence=["F-P5-01 deferred @ session 1", "F-P5-01 deferred @ session 2"]),
              sidecar_obj=sidecar(deferred={"F-P5-01": [1, 2]}))[0] == 1)

    # ---- H2 — provenance / anti-fabrication
    # a streak with a session GAP (1,2,4) fails
    gap = obs(count=3, evidence=["F-P5-01 deferred @ session 1", "F-P5-01 deferred @ session 2",
                                 "F-P5-01 deferred @ session 4"])
    chk("h2_session_gap",
        check(OPT + gap, sidecar_obj=sidecar(deferred={"F-P5-01": [1, 2, 4]}))[0] == 1)
    # len(evidence) < count fails
    short = obs(count=3, evidence=["F-P5-01 deferred @ session 1", "F-P5-01 deferred @ session 2"])
    chk("h2_evidence_lt_count",
        check(OPT + short, sidecar_obj=sidecar(deferred=DEF3))[0] == 1)
    # a cited session with NO recorded deferred disposition = fabricated streak member
    chk("h2_fabricated_member",
        check(OPT + obs(), sidecar_obj=sidecar(deferred={"F-P5-01": [1, 2]}))[0] == 1)
    # malformed evidence grammar fails
    chk("h2_bad_grammar",
        check(OPT + obs(evidence=["F-P5-01 was deferred sometimes", "F-P5-01 deferred @ session 2",
                                  "F-P5-01 deferred @ session 3"]),
              sidecar_obj=sidecar(deferred=DEF3))[0] == 1)
    # GOVERNED surface: the full deferral run reconstructs from gate_events[].disposition_deltas even
    # though the fold keeps only the latest — a 3-session streak with NO `sessions` history list on the
    # folded record still resolves from the event log (spec §4 governed path).
    def gov_sidecar():
        def delta(sess):
            return {"disposition_deltas": {"F-P5-01": {
                "schema": "apodictic.finding_disposition.v1", "id": "F-P5-01",
                "disposition": "deferred", "reason": "held", "source": "author",
                "session": sess, "ts": "2026-01-0%d" % sess, "trigger": "next pass"}}}
        return {"project": "P", _SEQ_KEY: 1, "execution": {
            "gate_events": [delta(1), delta(2), delta(3)],
            # the fold keeps only the last-event-wins record (session 3, no history list)
            "finding_dispositions": {"F-P5-01": {
                "schema": "apodictic.finding_disposition.v1", "id": "F-P5-01",
                "disposition": "deferred", "reason": "held", "source": "author",
                "session": 3, "ts": "2026-01-03", "trigger": "next pass"}}}}
    chk("h2_governed_gate_events_reconstructs_streak",
        check(OPT + obs(), sidecar_obj=gov_sidecar())[0] == 0)

    # ---- F2 — the non-governed honesty caveat. A non-governed deferral-recurrence WITHOUT a caveat
    #      WARNs (its streak is self-reported, not independently verified); WITH the caveat is clean;
    #      a GOVERNED project is exempt; a per-id override silences it.
    no_caveat = obs(observation="The same thread got set aside the last three sessions running. "
                                "Does that track for you?")  # confident + invitation, but NO caveat
    code, lines = check(OPT + no_caveat, sidecar_obj=sidecar(deferred=DEF3))
    chk("f2_nongoverned_no_caveat_warns", code == 0 and any("H2 non-governed caveat" in ln for ln in lines))
    chk("f2_nongoverned_no_caveat_strict_fails",
        check(OPT + no_caveat, sidecar_obj=sidecar(deferred=DEF3), strict=True)[0] == 1)
    # WITH the caveat (the default obs() carries "From what I've been tracking across our sessions") clean
    chk("f2_nongoverned_with_caveat_clean",
        not any("H2 non-governed caveat" in ln for ln in check(OPT + obs(), sidecar_obj=sidecar(deferred=DEF3))[1]))
    # GOVERNED project: the caveat is NOT required (the per-session event records ARE the verification)
    chk("f2_governed_exempt_from_caveat",
        not any("H2 non-governed caveat" in ln for ln in check(OPT + no_caveat, sidecar_obj=gov_sidecar())[1]))
    # a per-id override silences the caveat WARN (the writer accepted the honest framing another way)
    ovc = "<!-- override: coaching-observation CH-01 — caveat stated in the artifact preamble -->\n"
    chk("f2_caveat_override_silences",
        not any("H2 non-governed caveat" in ln for ln in
                check(OPT + ovc + no_caveat, sidecar_obj=sidecar(deferred=DEF3), strict=True)[1]))
    # phase-incompletion is NOT subject to the deferral caveat (it's not a deferral streak)
    chk("f2_phase_incompletion_no_caveat_needed",
        not any("H2 non-governed caveat" in ln for ln in check(OPT + phase_obs, sidecar_obj=sidecar(deferred=DEF3))[1]))

    # ---- H3 — descriptive, not judgmental (WARN; ERROR --strict; per-id override)
    blame = obs(observation="You always avoid the hard structural work — you fail to finish it.")
    code, lines = check(OPT + blame, sidecar_obj=sidecar(deferred=DEF3))
    chk("h3_trait_blame_warn", code == 0 and any("H3 descriptive" in ln for ln in lines))
    chk("h3_trait_blame_strict_fails", check(OPT + blame, sidecar_obj=sidecar(deferred=DEF3), strict=True)[0] == 1)
    ov = "<!-- override: coaching-observation CH-01 — the writer asked for blunt framing -->\n"
    chk("h3_override_silences",
        not any("H3 descriptive" in ln for ln in
                check(OPT + ov + blame, sidecar_obj=sidecar(deferred=DEF3), strict=True)[1]))
    # the reused author_fingerprint prescriptive regex also fires
    presc = obs(observation="You should fix your prose and tighten your range this week.")
    chk("h3_prescriptive_fires",
        any("H3 descriptive" in ln for ln in check(OPT + presc, sidecar_obj=sidecar(deferred=DEF3))[1]))

    # ---- H4 — no editorial-severity leak
    sev = OPT + obs() + "\n## Notes\n\nThis is a Must-Fix.\n"
    chk("h4_severity_leak", check(sev, sidecar_obj=sidecar(deferred=DEF3))[0] == 1)
    finding = ('<!-- apodictic:finding\n{"schema":"apodictic.finding.v1","id":"F-P5-01","mechanism":"m",'
               '"severity":"Must-Fix","confidence":"HIGH","evidence_refs":["c"],"fix_class":"x",'
               '"risk_if_fixed":"y"}\n-->')
    chk("h4_finding_block", check(OPT + obs() + "\n" + finding, sidecar_obj=sidecar(deferred=DEF3))[0] == 1)

    # ---- W1 — local-only
    chk("w1_external_url",
        any("W1 local-only" in ln for ln in
            check(OPT + obs() + "\nSee https://example.com/tracker\n", sidecar_obj=sidecar(deferred=DEF3))[1]))

    # ---- H7 — transference-health / tentative framing (WARN; ERROR --strict; H3 per-id override)
    # (a) a third-person trait VERDICT fires
    verdict = obs(observation="Writer defers endings. The author is an ending-avoider.")
    code, lines = check(OPT + verdict, sidecar_obj=sidecar(deferred=DEF3))
    chk("h7_trait_verdict_warn", code == 0 and any("H7 tentative-framing" in ln for ln in lines))
    chk("h7_trait_verdict_strict_fails",
        check(OPT + verdict, sidecar_obj=sidecar(deferred=DEF3), strict=True)[0] == 1)
    # (b) a bare-scoreboard rendering fires
    board = obs(observation="deferral-recurrence: 3")
    chk("h7_scoreboard_warn",
        any("H7 anti-scoreboard" in ln for ln in check(OPT + board, sidecar_obj=sidecar(deferred=DEF3))[1]))
    board2 = obs(observation="Ending work (×3)")
    chk("h7_scoreboard_xn_warn",
        any("H7 anti-scoreboard" in ln for ln in check(OPT + board2, sidecar_obj=sidecar(deferred=DEF3))[1]))
    # (c) a confident observation with NO invitation fires (the meaning was asserted, not handed over)
    noinvite = obs(observation="The same thread was set aside three sessions running.")
    chk("h7_no_invitation_warn",
        any("H7 tentative-framing" in ln for ln in check(OPT + noinvite, sidecar_obj=sidecar(deferred=DEF3))[1]))
    # the canonical confident-observation + open-question form (with the caveat) is CLEAN (no H7 warn)
    chk("h7_tentative_form_clean",
        not any("H7 " in ln for ln in check(OPT + obs(), sidecar_obj=sidecar(deferred=DEF3))[1]))
    # the H3 per-id override also silences an H7 framing warn (one framing override per observation)
    ovh7 = "<!-- override: coaching-observation CH-01 — the writer asked for the raw count -->\n"
    chk("h7_override_silences",
        not any("H7 " in ln for ln in
                check(OPT + ovh7 + board, sidecar_obj=sidecar(deferred=DEF3), strict=True)[1]))
    # a brief-but-real observation with an invitation (+ the non-governed caveat) must NOT be punished
    # as a scoreboard. Match the H7 finding-LINE ("H7 " with the trailing space), not the summary line
    # "see H3/H7/W1/H5 above" (which always contains "H7" as a substring).
    chk("h7_brief_real_prose_clean",
        not any("H7 " in ln for ln in
                check(OPT + obs(observation="From my notes across our sessions, it slid three times "
                                            "running — does that track?"),
                      sidecar_obj=sidecar(deferred=DEF3))[1]))

    # =========================================================================================
    # H5 / H6 — the two Fable ethics gates, exercised against the spec's HOSTILE fixtures on disk.
    # =========================================================================================
    def build_project(d, seq=1, opted=True, tombstone=False, deferred=DEF3):
        """A minimal valid opted-in project: Diagnostic_State.md (+ marker), the sidecar, one
        Coaching_History artifact."""
        state = ""
        if opted:
            state += "<!-- coaching-history: opted-in -->\n"
        if tombstone:
            state += "<!-- coaching-history: deleted -->\n"
        state += "# Diagnostic State\n\nSession 5. See the Coaching Log.\n"
        with open(os.path.join(d, _STATE_MD), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(state)
        with open(os.path.join(d, _SIDECAR_NAME), "w", encoding="utf-8", newline="\n") as fh:
            _j.dump(sidecar(seq=seq, deferred=deferred), fh, indent=2)
            fh.write("\n")
        hp = os.path.join(d, "P_Coaching_History_run5.md")
        with open(hp, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("# Coaching History\n\n" + OPT + obs() + "\n")
        return hp

    # ---- positive: a clean opted-in project passes end to end
    d = tempfile.mkdtemp()
    try:
        build_project(d)
        chk("h5_clean_project_passes", run([d], strict=True)[0] == 0)
    finally:
        shutil.rmtree(d, ignore_errors=True)

    # ---- H5.i — a Session_Plan carrying a projected observation block FAILS (the projection leak)
    d = tempfile.mkdtemp()
    try:
        build_project(d)
        with open(os.path.join(d, "Session_Plan_01.md"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write("# Session Plan\n\n" + obs() + "\n")
        code, lines = run([d])
        chk("h5i_projection_leak_fails", code == 1 and any("H5.i" in ln for ln in lines))
    finally:
        shutil.rmtree(d, ignore_errors=True)

    # ---- H5.iii — a Session_Plan carrying a bare evidence-grammar string FAILS (no block, just grammar)
    d = tempfile.mkdtemp()
    try:
        build_project(d)
        with open(os.path.join(d, "Session_Plan_02.md"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write("# Session Plan\n\nRecall: F-P5-01 deferred @ session 2, keep it in mind.\n")
        code, lines = run([d])
        chk("h5iii_evidence_grammar_leak_fails", code == 1 and any("H5.iii" in ln for ln in lines))
    finally:
        shutil.rmtree(d, ignore_errors=True)

    # ==== Codex F1 REGRESSION: a projection into an UNLISTED artifact type (editorial letter, the
    #      synthesis) must FAIL H5 — the old authored-artifact allowlist let these escape and survive
    #      `delete`. Now every *.md in scope is scanned for (i)/(ii). ====
    # (F1-a) an observation block projected into *_Core_DE_Synthesis_* FAILS H5 (was escaping)
    d = tempfile.mkdtemp()
    try:
        build_project(d)
        with open(os.path.join(d, "P_Core_DE_Synthesis_run5.md"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write("# Core DE Synthesis\n\n" + obs() + "\n")
        code, lines = run([d])
        chk("f1_synthesis_projection_fails", code == 1
            and any("H5.i" in ln and "Synthesis" in ln for ln in lines))
    finally:
        shutil.rmtree(d, ignore_errors=True)

    # (F1-b) an observation block projected into the editorial letter FAILS H5, AND after `delete` the
    #        H6 recompute CATCHES the surviving projection (does NOT falsely report "deletion honored").
    d = tempfile.mkdtemp()
    try:
        build_project(d)
        with open(os.path.join(d, "P_Editorial_Letter_run5.md"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write("# Editorial Letter\n\n" + obs() + "\n")
        chk("f1_letter_projection_fails", run([d])[0] == 1)
        # delete removes the Coaching_History file + seq + tombstone, but NOT the letter projection
        delete(d)
        code, lines = run([d])
        chk("f1_letter_projection_caught_by_h6_recompute",
            code == 1 and any("H6 residue" in ln for ln in lines)
            and not any("deletion honored" in ln for ln in lines))
    finally:
        shutil.rmtree(d, ignore_errors=True)

    # (F1-c) the frozen manuscript snapshot is POSITIVELY excluded from (iii)/CH-token — a chapter
    #        "CH-12" ref and prose "@ session" in the writer's manuscript must NOT trip H5 (--strict).
    #        (i)/(ii) still apply to it — but a real manuscript carries neither a block nor the schema-id.
    d = tempfile.mkdtemp()
    try:
        build_project(d)
        with open(os.path.join(d, "P_Manuscript_Snapshot_run5.md"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write("# Chapter 12\n\nThe council met CH-12. He arrived @ session's end at the hall.\n")
        chk("f1_manuscript_snapshot_not_tripped", run([d], strict=True)[0] == 0)
        # …but a block ACTUALLY pasted into the snapshot (a projection, not prose) IS caught (i)
        with open(os.path.join(d, "P_Manuscript_Snapshot_run5.md"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write("# Chapter 12\n\n" + obs() + "\n")
        chk("f1_manuscript_block_still_caught", run([d])[0] == 1)
    finally:
        shutil.rmtree(d, ignore_errors=True)

    # ---- H5.v — a sidecar shadow field (execution.coaching_notes) FAILS (the coach-only shadow)
    d = tempfile.mkdtemp()
    try:
        build_project(d)
        sc_path = os.path.join(d, _SIDECAR_NAME)
        sc = _j.loads(_read(sc_path))
        sc["execution"]["coaching_notes"] = {"CH-01": "the writer keeps deferring"}
        with open(sc_path, "w", encoding="utf-8", newline="\n") as fh:
            _j.dump(sc, fh, indent=2)
        code, lines = run([d])
        chk("h5v_sidecar_shadow_field_fails", code == 1 and any("H5.v" in ln for ln in lines))
    finally:
        shutil.rmtree(d, ignore_errors=True)

    # ---- H5.v — a shadow smuggled as a STRING VALUE anywhere in the sidecar (no coaching* key) FAILS
    d = tempfile.mkdtemp()
    try:
        build_project(d)
        sc_path = os.path.join(d, _SIDECAR_NAME)
        sc = _j.loads(_read(sc_path))
        sc["last_session"] = {"focus": "CH-01 pattern: F-P5-01 deferred @ session 2"}
        with open(sc_path, "w", encoding="utf-8", newline="\n") as fh:
            _j.dump(sc, fh, indent=2)
        code, lines = run([d])
        chk("h5v_sidecar_string_value_shadow_fails", code == 1 and any("H5.v" in ln for ln in lines))
    finally:
        shutil.rmtree(d, ignore_errors=True)

    # ---- H5.iv — TWO Coaching_History files FAIL (the shadow artifact)
    d = tempfile.mkdtemp()
    try:
        build_project(d)
        with open(os.path.join(d, "P_Coaching_History_run4.md"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write("# Coaching History (older)\n\n" + OPT + obs() + "\n")
        code, lines = run([d])
        chk("h5iv_two_artifacts_fails", code == 1 and any("H5.iv" in ln for ln in lines))
    finally:
        shutil.rmtree(d, ignore_errors=True)

    # ---- H5 WARN — a bare CH-token in coach prose is WARN (chapter-shorthand false-positive), overridable
    d = tempfile.mkdtemp()
    try:
        build_project(d)
        with open(os.path.join(d, "Session_Plan_03.md"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write("# Session Plan\n\nSee CH-12 for the scene we discussed.\n")
        code, lines = run([d])
        chk("h5_bare_token_warn_not_error", code == 0 and any("bare CH-token" in ln for ln in lines))
        # under --strict the bare token escalates to ERROR
        chk("h5_bare_token_strict_fails", run([d], strict=True)[0] == 1)
        # …and an override silences it
        with open(os.path.join(d, "Session_Plan_03.md"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write("# Session Plan\n\nSee CH-12 for the scene.\n"
                     "<!-- override: coaching-residue CH-12 — chapter shorthand, not a coaching id -->\n")
        chk("h5_bare_token_override_silences", run([d], strict=True)[0] == 0)
    finally:
        shutil.rmtree(d, ignore_errors=True)

    # ---- H5.iii boundary — a legitimate finding-disposition marker must NOT trip H5.iii
    d = tempfile.mkdtemp()
    try:
        build_project(d)
        with open(os.path.join(d, "P_Coaching_Log_run5.md"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write("# Coaching Log\n\n<!-- deferred: F-P5-01 until: beta reads — waiting on reader -->\n")
        code, lines = run([d], strict=True)
        chk("h5iii_disposition_marker_not_a_leak", code == 0)
    finally:
        shutil.rmtree(d, ignore_errors=True)

    # =========================================================================================
    # H6 — deletion honored, RECOMPUTE not trust. Hostile fixtures + a positive + the delete round-trip.
    # =========================================================================================
    # ---- H6 — tombstoned but an archived session plan still carries `deferred @ session 4` (residue)
    d = tempfile.mkdtemp()
    try:
        build_project(d, tombstone=True, opted=False)
        os.remove(os.path.join(d, "P_Coaching_History_run5.md"))  # artifact gone…
        # …but the sidecar seq is dropped for THIS fixture so only the archived residue trips H6
        sc_path = os.path.join(d, _SIDECAR_NAME)
        sc = _j.loads(_read(sc_path)); sc.pop(_SEQ_KEY, None)
        with open(sc_path, "w", encoding="utf-8", newline="\n") as fh:
            _j.dump(sc, fh, indent=2)
        runs = os.path.join(d, "runs", "r5_coaching"); os.makedirs(runs)
        with open(os.path.join(runs, "Session_Plan_03.md"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write("# Archived Session Plan\n\nF-P5-01 deferred @ session 4\n")
        code, lines = run([d])
        chk("h6_archived_residue_fails", code == 1 and any("H6 residue" in ln for ln in lines))
        # H6 accepts NO override — a coaching-residue override must NOT rescue the (iii) signature
        with open(os.path.join(runs, "Session_Plan_03.md"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write("# Archived Session Plan\n\nF-P5-01 deferred @ session 4\n"
                     "<!-- override: coaching-residue F-P5-01 — nope -->\n")
        chk("h6_no_override_accepted", run([d])[0] == 1)
    finally:
        shutil.rmtree(d, ignore_errors=True)

    # ---- H6 — tombstoned but coaching_history_seq survives in the sidecar (residue)
    d = tempfile.mkdtemp()
    try:
        build_project(d, tombstone=True, opted=False, seq=7)
        os.remove(os.path.join(d, "P_Coaching_History_run5.md"))
        code, lines = run([d])
        chk("h6_surviving_seq_fails", code == 1 and any("coaching_history_seq" in ln for ln in lines))
    finally:
        shutil.rmtree(d, ignore_errors=True)

    # ---- opted-in + deleted both present = contradiction ERROR
    d = tempfile.mkdtemp()
    try:
        build_project(d, tombstone=True, opted=True)
        code, lines = run([d])
        chk("h6_consent_contradiction_fails", code == 1 and any("consent contradiction" in ln for ln in lines))
    finally:
        shutil.rmtree(d, ignore_errors=True)

    # ---- positive: a cleanly deleted project (no artifact, no seq, tombstone) RECOMPUTES clean
    d = tempfile.mkdtemp()
    try:
        build_project(d, tombstone=True, opted=False)
        os.remove(os.path.join(d, "P_Coaching_History_run5.md"))
        sc_path = os.path.join(d, _SIDECAR_NAME)
        sc = _j.loads(_read(sc_path)); sc.pop(_SEQ_KEY, None)
        with open(sc_path, "w", encoding="utf-8", newline="\n") as fh:
            _j.dump(sc, fh, indent=2)
        code, lines = run([d])
        chk("h6_clean_delete_passes", code == 0 and any("deletion honored" in ln for ln in lines))
    finally:
        shutil.rmtree(d, ignore_errors=True)

    # ---- the delete-command ROUND-TRIP: build a valid project, run delete, assert H6 recompute passes
    d = tempfile.mkdtemp()
    try:
        build_project(d, seq=3)
        # also stage an archived artifact + an archived projection to prove delete reaches runs/*
        runs = os.path.join(d, "runs", "r4_coaching"); os.makedirs(runs)
        with open(os.path.join(runs, "P_Coaching_History_run4.md"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write("# Archived Coaching History\n\n" + OPT + obs() + "\n")
        # pre-delete: opted-in with TWO artifacts is an H5.iv fail (sanity: the project has residue)
        chk("roundtrip_predelete_has_artifacts", len(_history_files(d)) == 2)
        dcode, dlines = delete(d)
        chk("roundtrip_delete_ok", dcode == 0)
        chk("roundtrip_artifacts_gone", len(_history_files(d)) == 0)
        chk("roundtrip_seq_dropped", _sidecar_seq(_j.loads(_read(os.path.join(d, _SIDECAR_NAME)))) is None)
        state = _read(os.path.join(d, _STATE_MD))
        chk("roundtrip_tombstone_set", bool(_DELETED_RE.search(state)) and not _OPT_IN_RE.search(state))
        # the validator now RECOMPUTES the deletion as honored
        code, lines = run([d])
        chk("roundtrip_h6_recompute_passes", code == 0 and any("deletion honored" in ln for ln in lines))
        # idempotent: a second delete is a clean no-op that still recomputes clean
        chk("roundtrip_delete_idempotent", delete(d)[0] == 0 and run([d])[0] == 0)
    finally:
        shutil.rmtree(d, ignore_errors=True)

    # ---- opt-in gate: no marker anywhere → no-op exit 2 (nothing to check), like content-advisory
    d = tempfile.mkdtemp()
    try:
        with open(os.path.join(d, _STATE_MD), "w", encoding="utf-8", newline="\n") as fh:
            fh.write("# Diagnostic State\n\nNo coaching-history consent here.\n")
        chk("optin_gate_noop_exit2", run([d])[0] == 2)
    finally:
        shutil.rmtree(d, ignore_errors=True)

    # ---- unparseable sidecar is fail-closed
    d = tempfile.mkdtemp()
    try:
        build_project(d)
        with open(os.path.join(d, _SIDECAR_NAME), "w", encoding="utf-8", newline="\n") as fh:
            fh.write("{not json")
        chk("unparseable_sidecar_fail_closed", run([d])[0] == 1)
    finally:
        shutil.rmtree(d, ignore_errors=True)

    print("Self-test: PASS" if rc["v"] == 0 else "Self-test: FAIL")
    return rc["v"]


def main(argv):
    if "--self-test" in argv:
        return run_self_test()
    args = [a for a in argv[1:] if a != "coaching-history"]
    if args and args[0] == "delete":
        targets = [a for a in args[1:] if not a.startswith("--")]
        if len(targets) != 1:
            print("Usage: coaching_history.py delete <project_root>")
            return 2
        code, lines = delete(targets[0])
        for ln in lines:
            print(ln)
        return code
    strict = "--strict" in args
    paths = [a for a in args if not a.startswith("--")]
    if not paths:
        print("Usage: coaching_history.py coaching-history <project_root|files...> [--strict] "
              "| delete <project_root> | --self-test")
        return 2
    code, lines = run(paths, strict=strict)
    for ln in lines:
        print(ln)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
