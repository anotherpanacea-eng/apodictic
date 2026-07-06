#!/usr/bin/env python3
"""reader-contract-outline — the book, scene by scene, mapped against the promise it makes its reader.

`validate.sh reader-contract-outline <run_folder|files...> [--strict]` shells out here. A finalized
third-party developmental edit hands back three things: the editorial letter, the marked-up manuscript
(Annotated Manuscript), and — this deliverable — a reverse outline that lays the book out scene by
scene and maps it against the reader contract it implicitly makes. Like the Annotated Manuscript, this
builds no new analysis inside deliverable assembly: the outline is a byte-deterministic PROJECTION of
four inputs already in the run folder. The one piece of judgment that exists nowhere else — WHICH
scenes establish and pay off each contract promise — is housed in a model-authored, closed-key,
mechanically gated Contract Map block (`apodictic.contract_map.v1`, the persona-divergence D5
precedent): the model authors ids-only structured data, R7 gates it (recompute-not-trust), then the
projector consumes it. The Map is the ONLY authored contribution anywhere in the deliverable, and even
that is ids only — no prose (SPEC v3.1 D5).

Four inputs (all already in the resolved run folder):
  Pass 0      `*_Pass0_Reverse_Outline_*.md`  — the scene spine (id · what happens · what the reader
              now knows). Projected verbatim into §Scene Spine; the "what the reader now knows" line is
              the displayed evidence rendered beside every Map localization cell.
  Contract    `*_Contract_*.md`               — the reader contract schema block (fiction 10-field, +
              the optional narrative-nf CENTRAL QUESTION / PROMISE TYPE block). Projected verbatim into
              §The Reader Contract; the clause denominator is recomputed from it, never from the Map.
  Ledger      `*_Findings_Ledger_*.md`        — apodictic.finding.v1 blocks. A gap cell projects the
              verbatim matched finding, or the literal `none logged`.
  Map         `*_Contract_Map_*.md`           — one apodictic.contract_map.v1 block, authored at offer
              time. UNTRUSTED input (Mode-11): R7 binds it to the staged Pass 0/Contract/Ledger by
              sha256 and recomputes coverage from the Contract.

The outline (`*_Reader_Contract_Outline_*.md`), fixed section order (SPEC v3.1 §4b):
  1. Header               project · runlabel · one-line framing (a code constant, never free prose).
  2. The Reader Contract  verbatim projection of every Contract schema-block field (two-sided, R2);
                          an empty field renders its literal state (`HEAT LEVEL: —`), never omitted.
  3. Scene Spine          one entry per Pass 0 scene: `scene id · what happens · what the reader now
                          knows`, verbatim (R1).
  4. Contract Map         one block per clause: `established @ <ids>` / `paid off @ <ids>`, each id
                          followed by that scene's Pass 0 "what the reader now knows" line VERBATIM
                          (displayed evidence, R3); `not localizable to a scene` when declared; `gap:`
                          = `none logged` or the verbatim Ledger projection (R4).
  5. Coverage note        every recomputed clause mapped or explicitly `not localizable to a scene`
                          (advisory; R6).

Validator (`reader-contract-outline`), gates R1-R7 (SPEC v3.1 §5):
  R1 spine projection    §Scene Spine round-trips to Pass 0 — ids + count + text verbatim.
  R2 contract fidelity   two-sided: every Contract field is in §The Reader Contract and vice versa.
  R3 anchor + map        every scene id in the rendered Map resolves in Pass 0 AND the rendered map <->
     round-trip          Map block is a bijection (no clause dropped/added/reordered; every rendered
                         evidence line byte-matches the cited scene's Pass 0 line).
  R4 no fabricated gap   every gap cell is `none logged` or a verbatim projection of the Ledger entry
                         whose finding_id the Map names; `none logged` is a valid, non-degraded state.
  R5 author-facing       no untranslated framework shorthand in the rendered outline (reuses the
     (advisory WARN)     letter's author-facing-lint families, at the letter's warn-only tier; ERROR
                         --strict; NO override slug — every content section is a verbatim projection,
                         so a hit means the UPSTREAM artifact carried the shorthand: fix it there).
  R6 contract coverage   every recomputed clause (denominator from the Contract, per §4a) appears in
     (advisory WARN)     the Map/outline or carries the literal `not localizable to a scene`. WARN
                         marks ABSENCE only — a present-but-wrong entry is R7's ERROR. ERROR --strict.
                         Override: `<!-- override: reader-contract-coverage — <rationale> -->` via the
                         override_marker SSoT.
  R7 map integrity       closed-key apodictic.contract_map.v1 (unknown key = ERROR); inputs.*_sha256
     (Mode-11)           match the staged artifacts (a stale Map fails loudly); every clause_text a
                         verbatim substring of its named source_field, every source_field present in
                         the Contract; not_localizable ⇒ empty scene lists; every gap_finding_id
                         resolves in the Ledger; clause denominator recomputed from the Contract.
                         NON-NEGOTIABLES items are `;`-separated — the shipped contract convention
                         (example-quality-risk-contract.md separates items whose prose carries
                         internal commas with `;`); the denominator counts one clause per item.

Reuses apodictic_artifacts (block grammar + closed-key schema engine), letter_checks
(author-facing-lint families), override_marker (the override SSoT). See docs/reader-contract-outline.md.

  reader_contract_outline.py build <staging> [-o-]                 # gate the Map (R7) then project the outline; writes it
  reader_contract_outline.py reader-contract-outline <run_folder|files...> [--strict]
  reader_contract_outline.py --self-test

Exit: 0 clean / WARN-only, 1 ERROR (or WARN under --strict), 2 usage.
"""
import glob
import hashlib
import json
import os
import re
import sys

from override_marker import has_override  # SSoT: code-span-stripped, boundary-matched override scan

try:
    import apodictic_artifacts as art
except ImportError:
    art = None
try:
    import letter_checks as lc
except ImportError:
    lc = None

_MAP_SCHEMA = "apodictic.contract_map.v1"
_FINDING_SCHEMA = "apodictic.finding.v1"

_PASS0_GLOB = "*_Pass0_Reverse_Outline_*.md"
_CONTRACT_GLOB = "*_Contract_*.md"
_LEDGER_GLOB = "*_Findings_Ledger_*.md"
_MAP_GLOB = "*_Contract_Map_*.md"
_OUTLINE_GLOB = "*_Reader_Contract_Outline_*.md"

# The Contract schema-block fields, in canonical order (contract-template.md §Contract Schema). The
# fiction block is the base; the narrative-nf block (CENTRAL QUESTION / PROMISE TYPE) is optional and
# appended. These are the fields §The Reader Contract projects (two-sided R2) and the fields the
# clause denominator recomputes from (R7 / §4a).
_FICTION_FIELDS = ("GENRE/SUBGENRE", "READER PROMISE", "CONTROLLING IDEA", "HEAT LEVEL",
                   "DARKNESS LEVEL", "PRIMARY TENSION TYPE", "ENDING TYPE", "TONE COMPS",
                   "STRUCTURE COMPS", "NON-NEGOTIABLES")
_NNF_FIELDS = ("CENTRAL QUESTION", "PROMISE TYPE")
# The one field whose single clause is the controlling idea (fiction) or its narrative-nf analog.
# The clause_id algorithm (§4a) uses CENTRAL QUESTION in place of CONTROLLING IDEA when the nf block
# is present. Both may be present; the nf analog wins the denominator's "exactly one" idea row.
_IDEA_FIELD_FICTION = "CONTROLLING IDEA"
_IDEA_FIELD_NNF = "CENTRAL QUESTION"
_PROMISE_FIELD = "READER PROMISE"
_NONNEG_FIELD = "NON-NEGOTIABLES"

# A field label line in the Contract schema block: `LABEL: value` (label uppercase, may contain
# `/`, `-`, and spaces — e.g. GENRE/SUBGENRE, NON-NEGOTIABLES). Anchored so a colon inside a value
# never splits a new field.
_FIELD_RE = re.compile(r"^([A-Z][A-Z0-9 /-]*[A-Z0-9]):[ \t]?(.*)$")
# The literal an empty Contract field renders as (never omit the field — R2 two-sided).
_EMPTY_RENDER = "—"
# Displayed literals.
_NOT_LOCALIZABLE = "not localizable to a scene"
_NONE_LOGGED = "none logged"
# R6 override slug (the override_marker SSoT; no bare scan — M5/M6).
_COVERAGE_SLUG = "reader-contract-coverage"

# The CLOSED key set a clause object may carry (the subset engine only types `clauses` as an array, so
# per-clause closed-key is hand-checked in R7 — the annotation.v1 annotations[] / divergence.v1
# experiences precedent). Any other key makes the Map carry unaudited data — an R7 ERROR.
_CLAUSE_KEYS = {"clause_id", "source_field", "clause_text", "established", "paid_off",
                "not_localizable", "gap_finding_id"}
_INPUTS_KEYS = {"pass0_sha256", "contract_sha256", "ledger_sha256"}

# ---------------------------------------------------------------- the code-constant template

# The connective boilerplate is a code CONSTANT (the annotation_export.py precedent), never a resource
# file that could drift. Every literal the renderer emits lives here so the outline is a pure function
# of (Pass 0, Contract, Ledger, Map).
_OUTLINE_FRAMING = ("Your book laid out scene by scene, mapped against the promise it implicitly makes "
                    "to its reader. Every line below is projected verbatim from the run's own "
                    "artifacts — the reverse outline, the contract, and the findings ledger; nothing "
                    "here is newly authored.")
_MAP_NOTE = ("This file is machine-read plumbing for the reader-contract reverse outline. It carries "
             "one apodictic.contract_map.v1 block: the ids-only localization of each contract clause "
             "to the scenes that establish and pay it off. It is gated (R7) before the outline "
             "projector consumes it; do not edit by hand.")


def _read(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except (OSError, UnicodeDecodeError):
        return None


def sha256(text):
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


# ---------------------------------------------------------------- Contract parsing (schema block)

def parse_contract_fields(contract_text):
    """[(label, value), ...] for every schema-block field, in file order. The schema block is the run
    of `LABEL: value` lines under a heading; we collect every matching line (contract-template.md keeps
    the schema block near the top, and no author-facing prose line matches the ALL-CAPS `LABEL:` shape).

    Only the FIRST occurrence of each label is kept (the canonical schema block); a later restatement
    in prose does not add a second field. Returns [] when the text is None."""
    out, seen = [], set()
    for line in (contract_text or "").split("\n"):
        m = _FIELD_RE.match(line)
        if not m:
            continue
        label = m.group(1).strip()
        if label not in (_FICTION_FIELDS + _NNF_FIELDS):
            continue  # only the known contract fields — a stray ALL-CAPS prose line is not a field
        if label in seen:
            continue
        seen.add(label)
        out.append((label, m.group(2).rstrip()))
    return out


def contract_field_map(contract_text):
    """{label: value} for the schema-block fields (first occurrence wins)."""
    return dict(parse_contract_fields(contract_text))


def _split_promise_substrings(value):
    """The model splits READER PROMISE prose into clauses; a validator cannot semantically segment
    prose (§4a). This helper is used ONLY by the fixture/self-test author's convenience, NOT by any
    gate: it splits on `;` for a canonical multi-clause promise. Gates never call it — they read the
    Map's clause_text substrings and check verbatim-substring + non-overlap (R7)."""
    return [s.strip() for s in (value or "").split(";") if s.strip()]


# ---------------------------------------------------------------- Pass 0 parsing (scene spine)

# A Pass 0 scene entry (the format these fixtures establish — the repo's first Pass 0 examples). Each
# scene is a `### <scene_id>` heading followed by exactly these three labeled lines, in this order:
#   What happens: <one line, verbatim>
#   What the reader now knows: <one line, verbatim>   <- the displayed-evidence line (R3)
# (Word count / ratio / transition fields from run-core.md §Pass 0 are recorded elsewhere in the Pass 0
# file for the human; the spine projection consumes only id + happens + knows, per SPEC §4b.3.)
_SCENE_HEAD_RE = re.compile(r"^###[ \t]+(\S+)[ \t]*$")
_HAPPENS_RE = re.compile(r"^What happens:[ \t]?(.*)$")
_KNOWS_RE = re.compile(r"^What the reader now knows:[ \t]?(.*)$")


def parse_pass0_scenes(pass0_text):
    """[(scene_id, happens, knows), ...] in file order. A scene is a `### <id>` heading with a
    `What happens:` line and a `What the reader now knows:` line beneath it (the first of each after
    the heading, before the next heading). Malformed scenes (missing either line) are returned with the
    missing field as None so R1 can report them rather than silently dropping. Returns [] for None."""
    scenes = []
    sid = None
    happens = knows = None
    def flush():
        if sid is not None:
            scenes.append((sid, happens, knows))
    for line in (pass0_text or "").split("\n"):
        mh = _SCENE_HEAD_RE.match(line)
        if mh:
            flush()
            sid = mh.group(1)
            happens = knows = None
            continue
        if sid is None:
            continue
        m = _HAPPENS_RE.match(line)
        if m and happens is None:
            happens = m.group(1).rstrip()
            continue
        m = _KNOWS_RE.match(line)
        if m and knows is None:
            knows = m.group(1).rstrip()
            continue
    flush()
    return scenes


def scene_knows_map(pass0_text):
    """{scene_id: knows_line} — the displayed-evidence lookup R3 renders verbatim. Last write wins on a
    duplicate id (R1 will already have flagged the duplicate)."""
    return {sid: knows for sid, _h, knows in parse_pass0_scenes(pass0_text)}


# ---------------------------------------------------------------- Ledger parsing

def _fid(value):
    """art.fid_key when the shared lib is available, else the same trivial coercion inline — so the
    R7/gap-cell finding-id joins DEGRADE (never AttributeError) when apodictic_artifacts is absent,
    consistent with the module's never-traceback posture (`_read` -> None, `parse_map` -> block-missing).
    The coercion is fid_key's own: a malformed non-string id (JSON list/object/number) is str()-coerced
    so it can never crash a dict key — the swept non-hashable-id crash class."""
    if art is not None:
        return art.fid_key(value)
    return value if value is None or isinstance(value, str) else str(value)


def ledger_findings(ledger_text):
    """{finding_id: finding_obj} for every apodictic.finding.v1 block. fid_key-normalized keys so a
    malformed non-string id never crashes the dict (the swept crash class)."""
    out = {}
    if not ledger_text or art is None:
        return out
    for bt, obj, _e in art.parse_blocks(ledger_text):
        if bt == "finding" and isinstance(obj, dict) and obj.get("id") is not None:
            out[art.fid_key(obj["id"])] = obj
    return out


def gap_projection(finding):
    """The verbatim gap-cell projection of a matched Ledger finding (finding_id-only provenance, D4).
    A fixed single-line template over the finding's verbatim fields — no free-text slot."""
    return "%s [%s] %s" % (finding.get("id"), finding.get("severity"), finding.get("mechanism"))


# ---------------------------------------------------------------- clause denominator (recompute)

def recompute_clauses(contract_text):
    """The clause DENOMINATOR, recomputed from the Contract artifact (never the Map) — SPEC §4a.

    Returns (expected_source_fields, errors) where expected_source_fields is the ordered list of
    `source_field` values every clause_id C1..Cn must carry, in id order:
      - one row per READER PROMISE clause (>=1; the model splits, so we require the field present +
        non-empty and count the Map's promise rows against a floor of 1, not an exact number);
      - exactly one CONTROLLING IDEA row (or CENTRAL QUESTION if the narrative-nf block is present);
      - exactly one row per enumerable NON-NEGOTIABLES item.
    The promise SPLIT count is model judgment (R6's advisory question), so the denominator here encodes
    the field-level FLOORS the validator can mechanically enforce, returned as (min_promise_rows,
    idea_field, nonneg_items). errors names a missing mandatory field."""
    fields = contract_field_map(contract_text)
    errs = []
    # idea field: narrative-nf analog wins if present + non-empty
    idea_field = _IDEA_FIELD_FICTION
    if fields.get(_IDEA_FIELD_NNF, "").strip():
        idea_field = _IDEA_FIELD_NNF
    elif not fields.get(_IDEA_FIELD_FICTION, "").strip():
        errs.append("Contract has neither a non-empty %s nor %s field (the deliverable needs one idea "
                    "clause)" % (_IDEA_FIELD_FICTION, _IDEA_FIELD_NNF))
    if not fields.get(_PROMISE_FIELD, "").strip():
        errs.append("Contract %s field is empty (the deliverable needs >=1 promise clause)" % _PROMISE_FIELD)
    nonneg_items = enumerate_nonnegotiables(fields.get(_NONNEG_FIELD, ""))
    return {"min_promise_rows": 1, "idea_field": idea_field, "nonneg_items": nonneg_items}, errs


def enumerate_nonnegotiables(value):
    """The enumerable NON-NEGOTIABLES items — split on `;` (the canonical list separator, matching the
    promise-split convention). An empty/whitespace value yields [] (zero mandatory nonneg rows, a valid
    thin contract). Each item is stripped."""
    return [s.strip() for s in (value or "").split(";") if s.strip()]


# ---------------------------------------------------------------- Map parsing + R7

def parse_map(map_text):
    """(obj_or_None, schema_errs) for the single apodictic:contract_map block."""
    if not map_text or art is None:
        return None, ["no contract_map block found"]
    schema = art.load_schema(_MAP_SCHEMA)
    for bt, obj, jerr in art.parse_blocks(map_text):
        if bt != "contract_map":
            continue
        if jerr:
            return None, ["contract_map: invalid JSON — %s" % jerr]
        return obj, art.validate_obj(obj, schema, "contract_map")
    return None, ["no contract_map block found"]


def check_map_integrity(map_obj, schema_errs, pass0_text, contract_text, ledger_text):
    """R7 (Mode-11: the Map is untrusted). Returns a list of ERROR strings (empty == clean).

    Every claim recomputes from the artifacts, never trusts the Map:
      - closed-key schema (schema_errs already carries the unknown-key errors from validate_obj);
      - inputs.*_sha256 match the staged Pass 0 / Contract / Ledger, byte-for-byte (stale = ERROR);
      - every clause_text is a verbatim substring of its named source_field, and source_field is a real
        Contract field; the promise substrings are non-overlapping;
      - clause_id sequence is C1..Cn with the §4a source_field ordering, count against the recomputed
        denominator floors;
      - not_localizable ⇒ established/paid_off empty;
      - every established/paid_off id resolves to a Pass 0 scene;
      - every gap_finding_id resolves in the Ledger."""
    errs = ["R7 map integrity: %s" % e for e in schema_errs]
    if not isinstance(map_obj, dict):
        return errs or ["R7 map integrity: contract_map block is not a JSON object"]

    # --- input binding (recompute-not-trust: the Map declares hashes; we recompute + compare)
    inputs = map_obj.get("inputs")
    if not isinstance(inputs, dict):
        errs.append("R7 map integrity: `inputs` must be an object carrying pass0/contract/ledger sha256")
        inputs = {}
    else:
        for k in set(inputs) - _INPUTS_KEYS:
            errs.append("R7 map integrity: inputs carries unknown key %r (closed set: %s)"
                        % (k, ", ".join(sorted(_INPUTS_KEYS))))
    for key, txt, name in (("pass0_sha256", pass0_text, "Pass 0"),
                           ("contract_sha256", contract_text, "Contract"),
                           ("ledger_sha256", ledger_text, "Ledger")):
        want = sha256(txt) if txt is not None else None
        got = inputs.get(key)
        if txt is None:
            errs.append("R7 map integrity: cannot verify inputs.%s — the %s artifact is absent" % (key, name))
        elif got != want:
            errs.append("R7 map integrity: inputs.%s=%r does not match the staged %s (%s) — the Map is "
                        "stale or bound to different inputs; re-author or re-stage, never trust it"
                        % (key, got, name, want))

    # --- clause structure (recompute the denominator from the Contract, never the Map)
    denom, denom_errs = recompute_clauses(contract_text)
    for e in denom_errs:
        errs.append("R7 map integrity: %s" % e)
    fields = contract_field_map(contract_text)
    scene_ids = {sid for sid, _h, _k in parse_pass0_scenes(pass0_text)}
    led = ledger_findings(ledger_text)

    clauses = map_obj.get("clauses")
    if not isinstance(clauses, list):
        errs.append("R7 map integrity: `clauses` must be an array")
        return errs
    # per-source_field verbatim-substring + non-overlap of promise substrings
    promise_spans = []          # (start, end) of each promise clause_text inside READER PROMISE
    promise_value = fields.get(_PROMISE_FIELD, "")
    id_seq, source_seq = [], []
    for i, cl in enumerate(clauses):
        where = "clauses[%d]" % i
        if not isinstance(cl, dict):
            errs.append("R7 map integrity: %s must be an object" % where)
            id_seq.append(None)
            source_seq.append(None)
            continue
        for k in set(cl) - _CLAUSE_KEYS:
            errs.append("R7 map integrity: %s carries unknown key %r (a clause is ids-only, closed "
                        "set: %s)" % (where, k, ", ".join(sorted(_CLAUSE_KEYS))))
        cid = cl.get("clause_id")
        id_seq.append(cid)
        sf = cl.get("source_field")
        source_seq.append(sf)
        ct = cl.get("clause_text")
        if sf not in fields:
            errs.append("R7 map integrity: %s source_field %r is not a field present in the Contract"
                        % (where, sf))
        elif not (isinstance(ct, str) and ct and ct in fields[sf]):
            errs.append("R7 map integrity: %s clause_text is not a verbatim substring of its %s field"
                        % (where, sf))
        elif sf == _PROMISE_FIELD:
            start = promise_value.find(ct)
            promise_spans.append((start, start + len(ct)))
        # localization integrity
        nl = cl.get("not_localizable")
        est = cl.get("established") if isinstance(cl.get("established"), list) else []
        paid = cl.get("paid_off") if isinstance(cl.get("paid_off"), list) else []
        if nl is True and (est or paid):
            errs.append("R7 map integrity: %s not_localizable is true but established/paid_off are "
                        "non-empty (a not-localizable clause pins no scene)" % where)
        for sid in list(est) + list(paid):
            if sid not in scene_ids:
                errs.append("R7 map integrity: %s cites scene id %r, which is not a Pass 0 scene"
                            % (where, sid))
        gfid = cl.get("gap_finding_id")
        if gfid is not None and _fid(gfid) not in led:
            errs.append("R7 map integrity: %s gap_finding_id %r does not resolve in the Findings Ledger"
                        % (where, gfid))

    # promise clauses must not overlap (the mechanical bound on the model's split; §4a)
    spans = sorted(s for s in promise_spans if s[0] >= 0)
    for a, b in zip(spans, spans[1:]):
        if a[1] > b[0]:
            errs.append("R7 map integrity: two READER PROMISE clause_text substrings overlap "
                        "(%s and %s in the promise field) — the split must partition, not double-cover"
                        % (a, b))
            break

    # clause_id sequence C1..Cn (§4a: assigned in order of appearance in the schema block)
    expected_ids = ["C%d" % (n + 1) for n in range(len(clauses))]
    if id_seq != expected_ids:
        errs.append("R7 map integrity: clause_id sequence %r is not the required %r (ids are C1..Cn in "
                    "schema-block order)" % (id_seq, expected_ids))

    # source_field ORDERING (§4a): all READER PROMISE rows first, then exactly one idea row, then one
    # row per NON-NEGOTIABLES item — checked against the recomputed denominator floors.
    idea_field = denom["idea_field"]
    n_promise = sum(1 for sf in source_seq if sf == _PROMISE_FIELD)
    n_idea = sum(1 for sf in source_seq if sf == idea_field)
    n_nonneg = sum(1 for sf in source_seq if sf == _NONNEG_FIELD)
    if n_promise < denom["min_promise_rows"]:
        errs.append("R7 map integrity: %d READER PROMISE clause(s); the Contract's non-empty promise "
                    "needs at least %d" % (n_promise, denom["min_promise_rows"]))
    if n_idea != 1:
        errs.append("R7 map integrity: %d %s clause(s); the deliverable needs exactly 1 idea clause"
                    % (n_idea, idea_field))
    if n_nonneg != len(denom["nonneg_items"]):
        errs.append("R7 map integrity: %d NON-NEGOTIABLES clause(s); the Contract enumerates %d "
                    "non-negotiable item(s) (items are `;`-separated; recomputed from the artifact, "
                    "never the Map)" % (n_nonneg, len(denom["nonneg_items"])))
    # ordering: promise block, then the single idea row, then the nonneg rows
    expected_order = ([_PROMISE_FIELD] * n_promise + [idea_field] * min(n_idea, 1)
                      + [_NONNEG_FIELD] * n_nonneg)
    # only assert order when the counts are internally consistent (else the count errors above lead)
    if (n_promise >= denom["min_promise_rows"] and n_idea == 1
            and n_nonneg == len(denom["nonneg_items"]) and source_seq != expected_order):
        errs.append("R7 map integrity: clause source_field ordering %r is not the required "
                    "READER-PROMISE* -> idea -> NON-NEGOTIABLES* order" % (source_seq,))
    return errs


# ---------------------------------------------------------------- rendering (the projector)

def render_outline(pass0_text, contract_text, ledger_text, map_obj, project, runlabel):
    """Project the outline from the four inputs + the gated Map. Pure function; byte-deterministic.

    Called ONLY after R7 has gated map_obj (build stages it that way). Renders §1-§5 in fixed order."""
    scenes = parse_pass0_scenes(pass0_text)
    knows = scene_knows_map(pass0_text)
    fields = parse_contract_fields(contract_text)
    led = ledger_findings(ledger_text)
    out = []
    # §1 Header
    out.append("# Reader-Contract Reverse Outline — %s" % project)
    out.append("")
    out.append("_%s_" % _OUTLINE_FRAMING)
    out.append("")
    out.append("Run: %s" % runlabel)
    out.append("")
    # §2 The Reader Contract (verbatim projection; empty fields render their literal state)
    out.append("## The Reader Contract")
    out.append("")
    for label, value in fields:
        out.append("- %s: %s" % (label, value if value.strip() else _EMPTY_RENDER))
    out.append("")
    # §3 Scene Spine (verbatim)
    out.append("## Scene Spine")
    out.append("")
    for sid, happens, know in scenes:
        out.append("- %s · %s · %s" % (sid, happens, know))
    out.append("")
    # §4 Contract Map (one block per clause)
    out.append("## Contract Map")
    out.append("")
    for cl in (map_obj.get("clauses") or []):
        cid = cl.get("clause_id")
        sf = cl.get("source_field")
        ct = cl.get("clause_text")
        out.append("### %s — %s" % (cid, sf))
        out.append("")
        out.append("> %s" % ct)
        out.append("")
        if cl.get("not_localizable") is True:
            out.append("- %s" % _NOT_LOCALIZABLE)
        else:
            for role, key in (("established", "established"), ("paid off", "paid_off")):
                ids = cl.get(key) if isinstance(cl.get(key), list) else []
                if ids:
                    out.append("- %s @ %s" % (role, ", ".join(ids)))
                    for sid in ids:
                        out.append("  - %s: %s" % (sid, knows.get(sid, "")))
                else:
                    out.append("- %s @ (none)" % role)
        gfid = cl.get("gap_finding_id")
        if gfid is None:
            out.append("- gap: %s" % _NONE_LOGGED)
        else:
            f = led.get(_fid(gfid))
            out.append("- gap: %s" % (gap_projection(f) if f else gfid))
        out.append("")
    # §5 Coverage note (advisory; every clause mapped or explicitly not-localizable)
    out.append("## Coverage note")
    out.append("")
    n = len(map_obj.get("clauses") or [])
    out.append("Every contract clause below is mapped to the scenes that establish and pay it off, or "
               "marked `%s`. %d clause(s) recomputed from the contract." % (_NOT_LOCALIZABLE, n))
    out.append("")
    return "\n".join(out).rstrip("\n") + "\n"


# ---------------------------------------------------------------- the validator (R1-R7)

def _render_scene_line(sid, happens, know):
    return "- %s · %s · %s" % (sid, happens, know)


def check(pass0_text, contract_text, ledger_text, map_text, outline_text, strict=False):
    """Run R1-R7. Returns (code, lines). Each input may be None (resolution reports the gap)."""
    lines, errs, warns = [], [], []
    map_obj, schema_errs = parse_map(map_text)
    if not isinstance(map_obj, dict):
        if map_obj is not None or any("invalid JSON" in e for e in schema_errs):
            return 1, ["reader-contract-outline: %s" % (schema_errs[0] if schema_errs else "map block is not a JSON object"),
                       "reader-contract-outline: FAIL (R7 map integrity)"]
        return 1, ["reader-contract-outline: no apodictic.contract_map block found in the Map",
                   "reader-contract-outline: FAIL (R7 — Map block missing)"]
    if pass0_text is None or contract_text is None or outline_text is None:
        missing = [n for n, t in (("Pass 0", pass0_text), ("Contract", contract_text),
                                  ("outline", outline_text)) if t is None]
        return 2, ["reader-contract-outline: need Pass 0 + Contract + the rendered outline to validate "
                   "(missing %s)" % " + ".join(missing)]

    # R7 first (gate the untrusted Map before trusting any of its cells downstream)
    errs += check_map_integrity(map_obj, schema_errs, pass0_text, contract_text, ledger_text)

    scenes = parse_pass0_scenes(pass0_text)
    knows = scene_knows_map(pass0_text)
    contract_fields = parse_contract_fields(contract_text)
    led = ledger_findings(ledger_text)

    # ---- R1 spine projection integrity: rendered §Scene Spine round-trips to Pass 0
    want_spine = []
    seen_sid = {}
    for sid, happens, know in scenes:
        seen_sid[sid] = seen_sid.get(sid, 0) + 1
        if happens is None or know is None:
            errs.append("R1 spine projection: Pass 0 scene %r is missing a `What happens:` or `What the "
                        "reader now knows:` line (cannot project it)" % sid)
        want_spine.append(_render_scene_line(sid, happens or "", know or ""))
    for sid, c in sorted(k for k in seen_sid.items() if k[1] > 1):
        errs.append("R1 spine projection: Pass 0 scene id %r appears %d times (ids must be unique)" % (sid, c))
    got_spine = _section_lines(outline_text, "Scene Spine")
    if got_spine != want_spine:
        errs.append("R1 spine projection: §Scene Spine does not round-trip to Pass 0 (ids/count/text "
                    "must be verbatim; %d rendered vs %d Pass 0 scene(s))" % (len(got_spine), len(want_spine)))

    # ---- R2 contract fidelity: two-sided field projection
    rendered_contract = _section_lines(outline_text, "The Reader Contract")
    want_contract = ["- %s: %s" % (label, value if value.strip() else _EMPTY_RENDER)
                     for label, value in contract_fields]
    rc_labels = set()
    for ln in rendered_contract:
        m = re.match(r"^- ([A-Z][A-Z0-9 /-]*[A-Z0-9]): ", ln)
        if m:
            rc_labels.add(m.group(1))
    contract_labels = {label for label, _v in contract_fields}
    for label in contract_labels - rc_labels:
        errs.append("R2 contract fidelity: Contract field %r is absent from §The Reader Contract "
                    "(no field may be dropped)" % label)
    for label in rc_labels - contract_labels:
        errs.append("R2 contract fidelity: §The Reader Contract carries field %r absent from the "
                    "Contract artifact (no field may be invented)" % label)
    if rc_labels == contract_labels and rendered_contract != want_contract:
        errs.append("R2 contract fidelity: §The Reader Contract values are not the verbatim Contract "
                    "projection (empty fields must render `%s`, never be reworded)" % _EMPTY_RENDER)

    # ---- R2 (header integrity): the header block (title + framing constant + Run line) must be the
    #      exact code-constant header for the extracted project/runlabel. project/runlabel are free
    #      author-facing metadata (not a projection of any input), but the framing sentence and header
    #      STRUCTURE are a code constant — so a tampered framing / injected header prose is caught here,
    #      not silently absorbed by re-deriving project/runlabel from the tampered outline downstream.
    proj, rl = _project_of(outline_text), _runlabel_of(outline_text)
    # the header block is everything the renderer emits before `## The Reader Contract` — the title, the
    # framing constant, the Run line, and the blank-line separator the section heading sits after.
    want_header = "# Reader-Contract Reverse Outline — %s\n\n_%s_\n\nRun: %s\n\n" % (
        proj, _OUTLINE_FRAMING, rl)
    got_header = outline_text.split("## The Reader Contract")[0]
    if got_header != want_header:
        errs.append("R2 contract fidelity: the outline header is not the exact code-constant header "
                    "(title + framing + Run line) — the framing boilerplate is fixed, never editable prose")

    # ---- R3 anchor + map round-trip: rendered Map <-> Map block bijection + verbatim evidence lines
    #      Only meaningful once R7 confirmed the Map's structural integrity; still computed (an R7
    #      failure already fails the run, and R3 adds locus detail on the render side).
    want_outline = render_outline(pass0_text, contract_text, ledger_text, map_obj, proj, rl)
    # The whole outline is a byte-deterministic projection: the strongest R3/R1/R2 statement is that the
    # committed outline equals a fresh render. But we keep the per-section messages above for locus, and
    # add the global determinism assertion here (it subsumes R3's bijection + evidence-line byte-match).
    if outline_text != want_outline:
        # localize: is it the Map section (R3) or elsewhere?
        got_map = _section_block(outline_text, "Contract Map")
        want_map = _section_block(want_outline, "Contract Map")
        if got_map != want_map:
            errs.append("R3 anchor + map round-trip: the rendered §Contract Map is not the byte-exact "
                        "projection of the Map block (a clause row dropped/added/reordered, or an "
                        "evidence line does not byte-match the cited scene's Pass 0 line)")
        elif not any(e.startswith("R1") or e.startswith("R2") for e in errs):
            errs.append("reader-contract-outline: the rendered outline is not the byte-exact projection "
                        "of (Pass 0, Contract, Ledger, Map) — regeneration is not deterministic")

    # ---- R4 no fabricated gap: every rendered gap cell is `none logged` or the verbatim Ledger projection
    for cl in (map_obj.get("clauses") or []):
        gfid = cl.get("gap_finding_id")
        if gfid is None:
            continue
        f = led.get(_fid(gfid))
        if f is None:
            errs.append("R4 no fabricated gap: clause %s names gap_finding_id %r, absent from the "
                        "Ledger (a gap cell must project a real finding or be `%s`)"
                        % (cl.get("clause_id"), gfid, _NONE_LOGGED))
            continue
        want_cell = "- gap: %s" % gap_projection(f)
        if want_cell not in outline_text:
            errs.append("R4 no fabricated gap: clause %s gap cell is not the verbatim projection of "
                        "finding %s (paraphrase is fabrication)" % (cl.get("clause_id"), gfid))

    # ---- R5 author-facing language (advisory WARN; ERROR --strict; NO override slug): untranslated
    #      framework shorthand in the rendered outline, via the letter's author-facing-lint families —
    #      the spec's words are "reuse the letter's check", and the letter's lint is warn-only BY
    #      DESIGN. Every content section of this outline is a VERBATIM PROJECTION of upstream artifacts
    #      (contract fields via R2, spine via R1, evidence lines via R3, gap cells via R4), so a lint
    #      hit here always means the UPSTREAM artifact contained the shorthand — a legibility advisory
    #      this deliverable cannot fix and did not author, never a Firewall breach (R1-R4/R7 own
    #      integrity). A hard ERROR here would deadlock a legitimate run whose Ledger mechanism names a
    #      pass ("Pass 5 found…") with no escape. Deliberately NO override slug: the fix is to gloss or
    #      reword the shorthand in the upstream artifact, not to silence the flag at the projection.
    if lc is not None:
        _e5, afl_w = lc.author_facing_lint(outline_text)[:2]
        for w in afl_w:
            # the lint's own messages open with "WARN: " — strip it so the tier prefix isn't doubled
            warns.append("R5 author-facing language: %s" % (w[6:] if w.startswith("WARN: ") else w))

    # ---- R6 contract coverage (advisory WARN; ERROR --strict). This is the SPLIT-completeness question
    #      §4a explicitly assigns to R6, NOT R7: the field-level floors (>=1 promise row, exactly 1 idea,
    #      exactly 1 per NON-NEGOTIABLES item) are R7's mechanical ERRORs; whether the model's READER
    #      PROMISE split JOINTLY COVERS the whole promise prose is what a validator can only advise on.
    #      WARN marks ABSENCE only — an uncovered stretch of the promise. A present-but-wrong clause is
    #      R7's ERROR, never a WARN. Override via the reader-contract-coverage SSoT slug.
    if not has_override(outline_text or "", _COVERAGE_SLUG) and not has_override(map_text or "", _COVERAGE_SLUG):
        promise_value = contract_field_map(contract_text).get(_PROMISE_FIELD, "")
        # the char stretches of the promise field the (non-overlapping, verbatim) clause substrings cover
        covered = [False] * len(promise_value)
        for cl in (map_obj.get("clauses") or []):
            if cl.get("source_field") != _PROMISE_FIELD:
                continue
            ct = cl.get("clause_text")
            if isinstance(ct, str) and ct:
                start = promise_value.find(ct)
                if start >= 0:
                    for i in range(start, start + len(ct)):
                        covered[i] = False if i >= len(covered) else True
        # A gap = an uncovered ALPHANUMERIC promise character (whitespace + punctuation between clauses —
        # the `; ` a canonical split leaves — is not "missing coverage"; only substantive word content
        # is). If any word character is unmapped, the split is incomplete — the advisory absence R6 owns.
        gap = any((not covered[i]) and promise_value[i].isalnum()
                  for i in range(len(promise_value)))
        if promise_value.strip() and gap:
            warns.append("R6 contract coverage: the READER PROMISE split does not jointly cover the "
                         "whole promise — some of the promise prose is mapped to no clause (advisory; "
                         "override `<!-- override: reader-contract-coverage — <why> -->` if intentional)")

    # ---- Report
    n_clauses = len(map_obj.get("clauses") or [])
    lines.append("reader-contract-outline: %s [%s] — %d scene(s), %d clause(s)"
                 % (_project_of(outline_text), _runlabel_of(outline_text), len(scenes), n_clauses))
    for e in errs:
        lines.append("  ERROR: %s" % e)
    for w in warns:
        lines.append("  %s: %s" % ("ERROR (--strict)" if strict else "WARN", w))
    if errs or (strict and warns):
        lines.append("reader-contract-outline: FAIL (%d error(s)%s)"
                     % (len(errs), ", %d strict warn(s)" % len(warns) if (strict and warns) else ""))
        return 1, lines
    if warns:
        lines.append("WARN: reader-contract-outline: %d advisory flag(s) — see R5/R6 above" % len(warns))
    else:
        lines.append("reader-contract-outline: PASS (spine + contract fidelity + map round-trip + "
                     "no fabricated gap + map integrity)")
    return 0, lines


# ---------------------------------------------------------------- outline section helpers

def _outline_meta_line(outline_text, prefix, default):
    for ln in (outline_text or "").split("\n"):
        if ln.startswith(prefix):
            return ln[len(prefix):].strip()
    return default


def _project_of(outline_text):
    hdr = _outline_meta_line(outline_text, "# Reader-Contract Reverse Outline — ", None)
    return hdr if hdr else "Manuscript"


def _runlabel_of(outline_text):
    return _outline_meta_line(outline_text, "Run: ", "run")


def _section_lines(outline_text, heading):
    """The list-item / content lines of a `## <heading>` section (up to the next `## ` heading),
    excluding blank lines. For §Scene Spine / §The Reader Contract these are the `- ...` rows."""
    return [ln for ln in _section_block(outline_text, heading).split("\n") if ln.strip()]


def _section_block(outline_text, heading):
    """The raw text between `## <heading>` and the next `## ` heading (exclusive)."""
    lines = (outline_text or "").split("\n")
    out, capture = [], False
    for ln in lines:
        if re.match(r"^## ", ln):
            if capture:
                break
            capture = (ln == "## %s" % heading)
            continue
        if capture:
            out.append(ln)
    return "\n".join(out).strip("\n")


# ---------------------------------------------------------------- resolution + build

def _newest(paths):
    return max(paths, key=os.path.getmtime) if paths else None


# The infix that separates a project prefix from an artifact kind, per artifact glob. Used to derive a
# project prefix so a fixture directory holding more than one project (Example + ExampleNF) resolves to
# ONE coherent project rather than mixing artifacts across projects (a real run folder holds exactly one
# project; this only matters for the shared canonical-fixture dir).
_INFIX = {"pass0": "_Pass0_Reverse_Outline_", "contract": "_Contract_", "ledger": "_Findings_Ledger_",
          "map": "_Contract_Map_", "outline": "_Reader_Contract_Outline_"}


def _project_prefix(basename, infix):
    return basename.split(infix)[0] if infix in basename else None


def resolve_run_folder(folder):
    """Resolve the four inputs + the outline for a SINGLE project in `folder`. Project-aware: when the
    folder holds more than one project prefix (the shared fixture dir), the project chosen is the one
    with the most complete artifact set (ties broken lexicographically) — deterministic, never mixing
    a Pass 0 from one project with a Contract from another."""
    def kind_files(kind):
        glob_pat = {"pass0": _PASS0_GLOB, "contract": _CONTRACT_GLOB, "ledger": _LEDGER_GLOB,
                    "map": _MAP_GLOB, "outline": _OUTLINE_GLOB}[kind]
        paths = glob.glob(os.path.join(folder, glob_pat))
        if kind == "contract":
            # *_Contract_* also matches the Map (*_Contract_Map_*) and the Outline
            # (*_Reader_Contract_Outline_*); exclude both so the Contract artifact is never masqueraded.
            paths = [p for p in paths if "_Contract_Map_" not in os.path.basename(p)
                     and "_Reader_Contract_Outline_" not in os.path.basename(p)]
        return paths
    kinds = {k: kind_files(k) for k in _INFIX}
    # collect candidate project prefixes across all kinds
    prefixes = set()
    for kind, paths in kinds.items():
        for p in paths:
            pre = _project_prefix(os.path.basename(p), _INFIX[kind])
            if pre is not None:
                prefixes.add(pre)
    if not prefixes:
        return None, None, None, None, None

    def pick(kind, prefix):
        cands = [p for p in kinds[kind]
                 if _project_prefix(os.path.basename(p), _INFIX[kind]) == prefix]
        return _newest(cands)
    # score each prefix by how many of the four inputs (+ outline) it has; pick the best (lex/tie).
    def score(prefix):
        return sum(1 for kind in _INFIX if pick(kind, prefix) is not None)
    best = sorted(prefixes, key=lambda pre: (-score(pre), pre))[0]
    return (pick("pass0", best), pick("contract", best), pick("ledger", best),
            pick("map", best), pick("outline", best))


def classify_files(paths):
    p0 = con = led = mp = out = None
    for p in paths:
        base = os.path.basename(p)
        body = _read(p) or ""
        if "_Pass0_Reverse_Outline_" in base:
            p0 = p
        elif "_Contract_Map_" in base or _has_block(body, "contract_map"):
            mp = p
        elif "_Reader_Contract_Outline_" in base:
            out = p
        elif "_Contract_" in base:
            con = p
        elif _has_block(body, "finding"):
            led = p
    return p0, con, led, mp, out


def _has_block(text, btype):
    """True if `text` carries a real apodictic:<btype> block (parsed, not a raw substring) — the
    resolver-hardening rule (M2), so a file that merely names the marker in prose is not misrouted."""
    if art is None:
        return ("apodictic:%s" % btype) in (text or "")
    return any(bt == btype for bt, _o, _e in art.parse_blocks(text or ""))


def run(paths, strict=False):
    if len(paths) == 1 and os.path.isdir(paths[0]):
        p0, con, led, mp, out = resolve_run_folder(paths[0])
    else:
        p0, con, led, mp, out = classify_files(paths)
    if not mp:
        return 2, ["reader-contract-outline: no Contract Map found (need a *_Contract_Map_*.md or a "
                   "file with an apodictic:contract_map block)"]
    if not out:
        return 2, ["reader-contract-outline: no Reader Contract Outline found (need a "
                   "*_Reader_Contract_Outline_*.md); run `build <staging>` first"]
    return check(_read(p0) if p0 else None, _read(con) if con else None,
                 _read(led) if led else None, _read(mp), _read(out), strict=strict)


def build(folder, out_stream=None):
    """Gate the Map (R7) then project the outline from the four staged inputs. Writes the outline into
    `folder` (or to out_stream if given). Returns code. Verified-or-absent: on R7 failure, names the
    gate and writes NOTHING."""
    p0, con, led, mp, _out = resolve_run_folder(folder)
    missing = [n for n, p in (("Pass 0", p0), ("Contract", con), ("Contract Map", mp)) if not p]
    if missing:
        print("reader-contract-outline: cannot build — missing %s in %s" % (" + ".join(missing), folder),
              file=sys.stderr)
        return 2
    pass0_text, contract_text = _read(p0), _read(con)
    ledger_text = _read(led) if led else None
    map_text = _read(mp)
    map_obj, schema_errs = parse_map(map_text)
    if not isinstance(map_obj, dict):
        print("reader-contract-outline: %s — writing nothing"
              % (schema_errs[0] if schema_errs else "no contract_map block"), file=sys.stderr)
        return 1
    # R7 gate the Map FIRST — the projector must not consume an untrusted Map.
    r7 = check_map_integrity(map_obj, schema_errs, pass0_text, contract_text, ledger_text)
    if r7:
        for e in r7:
            print("reader-contract-outline: %s" % e, file=sys.stderr)
        print("reader-contract-outline: Map failed R7 — writing nothing (fix the Map, re-run)", file=sys.stderr)
        return 1
    project = os.path.basename(p0).split("_Pass0_Reverse_Outline_")[0] or "Manuscript"
    runlabel = os.path.splitext(os.path.basename(p0).split("_Pass0_Reverse_Outline_")[-1])[0] or "run"
    outline = render_outline(pass0_text, contract_text, ledger_text, map_obj, project, runlabel)
    if out_stream is not None:
        out_stream.write(outline)
        return 0
    # Containment invariant: `project` and `runlabel` derive from os.path.basename(p0) BEFORE any
    # splitting, and a basename cannot contain a path separator — so neither component can carry one
    # and this join cannot escape `folder` (no traversal surface; no sanitization needed).
    out_path = os.path.join(folder, "%s_Reader_Contract_Outline_%s.md" % (project, runlabel))
    with open(out_path, "w", encoding="utf-8", newline="") as fh:
        fh.write(outline)
    print("reader-contract-outline: wrote %s" % os.path.basename(out_path))
    return 0


# ---------------------------------------------------------------- self-test

def run_self_test():
    import tempfile
    import shutil
    rc = {"v": 0}
    made = []

    def chk(name, cond):
        print("  %s: %s" % (name, "OK" if cond else "FAIL"))
        if not cond:
            rc["v"] = 1

    # non-UTF8 artifact: _read must degrade to None, never traceback (the swept crash class)
    _fd, _nu = tempfile.mkstemp(suffix=".md")
    with os.fdopen(_fd, "wb") as _fh:
        _fh.write(b"\xff\xfenot utf-8\xff")
    chk("non_utf8_read_returns_none", _read(_nu) is None)
    os.unlink(_nu)

    # ---- canonical fiction inputs (self-contained, minimal)
    pass0 = (
        "# Pass 0 — Reverse Outline (worked example)\n\n"
        "### S1\n"
        "What happens: Mara misses the northbound train and burns her ticket.\n"
        "What the reader now knows: Mara wants out of the valley and has cut her own line of retreat.\n\n"
        "### S2\n"
        "What happens: Mara takes work at the lighthouse to earn a new fare.\n"
        "What the reader now knows: the cost of leaving is measured in months, not miles.\n\n"
        "### S3\n"
        "What happens: the keeper confesses he has never lit the lamp.\n"
        "What the reader now knows: the valley's one landmark is a lie the town agreed to keep.\n\n"
        "Total word count: 42 (measured).\n")
    contract = (
        "# Contract and Controlling Idea — Example\n\n"
        "## Contract Schema\n\n"
        "GENRE/SUBGENRE: literary fiction\n"
        "READER PROMISE: a woman escapes a dying town; the town's secret is exposed\n"
        "CONTROLLING IDEA: leaving costs more than staying, but staying costs the truth\n"
        "HEAT LEVEL: \n"
        "DARKNESS LEVEL: moderate\n"
        "PRIMARY TENSION TYPE: moral\n"
        "ENDING TYPE: open\n"
        "TONE COMPS: quiet, elegiac\n"
        "STRUCTURE COMPS: linear\n"
        "NON-NEGOTIABLES: the lighthouse stays unlit; Mara does not return\n")
    ledger = (
        "# Findings Ledger — Example\n\n"
        "<!-- apodictic:finding\n" + json.dumps({
            "schema": _FINDING_SCHEMA, "id": "F-PCF-02",
            "mechanism": "the town's secret is stated in dialogue but never dramatized",
            "severity": "Should-Fix", "confidence": "HIGH", "evidence_refs": ["S3"],
            "fix_class": "stage the reveal", "risk_if_fixed": "may slow the ending"}) + "\n-->\n")

    def contract_map(clauses, inputs=None):
        obj = {"schema": _MAP_SCHEMA,
               "inputs": inputs if inputs is not None else {
                   "pass0_sha256": sha256(pass0), "contract_sha256": sha256(contract),
                   "ledger_sha256": sha256(ledger)},
               "clauses": clauses}
        return "# Contract Map — Example\n\n_%s_\n\n<!-- apodictic:contract_map\n%s\n-->\n" % (
            _MAP_NOTE, json.dumps(obj, indent=2))

    # the canonical clause set: two promise clauses (split on `;`), one idea, two non-negotiables
    clauses = [
        {"clause_id": "C1", "source_field": "READER PROMISE",
         "clause_text": "a woman escapes a dying town", "established": ["S1"], "paid_off": ["S2"],
         "not_localizable": False, "gap_finding_id": None},
        {"clause_id": "C2", "source_field": "READER PROMISE",
         "clause_text": "the town's secret is exposed", "established": ["S3"], "paid_off": [],
         "not_localizable": False, "gap_finding_id": "F-PCF-02"},
        {"clause_id": "C3", "source_field": "CONTROLLING IDEA",
         "clause_text": "leaving costs more than staying", "established": ["S1", "S2"], "paid_off": [],
         "not_localizable": False, "gap_finding_id": None},
        {"clause_id": "C4", "source_field": "NON-NEGOTIABLES",
         "clause_text": "the lighthouse stays unlit", "established": ["S3"], "paid_off": [],
         "not_localizable": False, "gap_finding_id": None},
        {"clause_id": "C5", "source_field": "NON-NEGOTIABLES",
         "clause_text": "Mara does not return", "established": [], "paid_off": [],
         "not_localizable": True, "gap_finding_id": None},
    ]
    map_text = contract_map(clauses)
    map_obj, schema_errs = parse_map(map_text)

    # parsing sanity
    chk("parse_pass0_3_scenes", len(parse_pass0_scenes(pass0)) == 3)
    chk("parse_contract_fields", contract_field_map(contract).get("PRIMARY TENSION TYPE") == "moral")
    chk("empty_field_parsed", contract_field_map(contract).get("HEAT LEVEL") == "")
    chk("nonneg_enumerates_2", len(enumerate_nonnegotiables(
        contract_field_map(contract)["NON-NEGOTIABLES"])) == 2)

    # R7 clean
    chk("r7_clean", check_map_integrity(map_obj, schema_errs, pass0, contract, ledger) == [])

    # regression (Fable-review fold, 2026-07-06): the R7/gap finding-id joins must DEGRADE (never
    # AttributeError) when apodictic_artifacts is unavailable — _fid falls back to the inline coercion.
    # parse_map and ledger_findings already guard `art is None`; these were the three unguarded sites.
    _saved_art = globals()["art"]
    globals()["art"] = None
    try:
        chk("fid_degrades_without_art", _fid("F-X-01") == "F-X-01" and _fid([1, 2]) == "[1, 2]"
            and _fid(None) is None)
        try:
            _r7na = check_map_integrity(map_obj, [], pass0, contract, ledger)
            chk("r7_no_traceback_without_art", isinstance(_r7na, list))
        except AttributeError:
            chk("r7_no_traceback_without_art", False)
    finally:
        globals()["art"] = _saved_art

    # build -> render, then validate the fresh outline is clean + deterministic
    outline = render_outline(pass0, contract, ledger, map_obj, "Example", "r")
    code, ls = check(pass0, contract, ledger, map_text, outline)
    chk("clean_validate", code == 0)
    # empty HEAT LEVEL rendered as the literal em-dash state
    chk("empty_field_renders_dash", "- HEAT LEVEL: —" in outline)
    # evidence line rendered verbatim beside a cited scene
    chk("evidence_line_verbatim",
        "  - S1: Mara wants out of the valley and has cut her own line of retreat." in outline)
    # not-localizable clause renders the literal
    chk("not_localizable_literal", _NOT_LOCALIZABLE in outline)
    # gap cell = verbatim ledger projection
    chk("gap_cell_verbatim", "- gap: F-PCF-02 [Should-Fix] the town's secret is stated in dialogue but never dramatized" in outline)
    # none-logged gap cell
    chk("none_logged_present", "- gap: %s" % _NONE_LOGGED in outline)
    # determinism: a second render is byte-identical
    chk("render_deterministic", render_outline(pass0, contract, ledger, map_obj, "Example", "r") == outline)

    # ---- R7 hostiles
    # R7: doctored contract_sha256 (stale map)
    bad_hash = contract_map(clauses, inputs={
        "pass0_sha256": sha256(pass0), "contract_sha256": "deadbeef" * 8, "ledger_sha256": sha256(ledger)})
    mo, se = parse_map(bad_hash)
    r7 = check_map_integrity(mo, se, pass0, contract, ledger)
    chk("r7_stale_contract_sha", any("contract_sha256" in e for e in r7))
    code, ls = check(pass0, contract, ledger, bad_hash, render_outline(pass0, contract, ledger, mo, "Example", "r"))
    chk("r7_stale_fails_check", code == 1 and any("R7 map integrity" in x and "contract_sha256" in x for x in ls))

    # R7: clause_text not a verbatim substring of source_field
    para = json.loads(json.dumps(clauses))
    para[0]["clause_text"] = "a lady flees a doomed village"   # paraphrase, not a substring
    mp2 = contract_map(para)
    mo2, se2 = parse_map(mp2)
    chk("r7_non_substring_clause", any("verbatim substring" in e for e in check_map_integrity(mo2, se2, pass0, contract, ledger)))

    # R7: unknown key (closed-key schema) — schema_errs must carry it
    unk = json.loads(json.dumps(clauses))
    unk_obj = {"schema": _MAP_SCHEMA,
               "inputs": {"pass0_sha256": sha256(pass0), "contract_sha256": sha256(contract), "ledger_sha256": sha256(ledger)},
               "clauses": unk, "bogus_key": 1}
    unk_text = "# M\n<!-- apodictic:contract_map\n%s\n-->\n" % json.dumps(unk_obj)
    mo3, se3 = parse_map(unk_text)
    chk("r7_closed_key_unknown", any("unknown field" in e or "closed" in e for e in se3))

    # R7: clause_id out of sequence
    seq = json.loads(json.dumps(clauses))
    seq[2]["clause_id"] = "C9"
    chk("r7_bad_id_sequence", any("clause_id sequence" in e for e in
        check_map_integrity(parse_map(contract_map(seq))[0], [], pass0, contract, ledger)))

    # R7: not_localizable with non-empty scene list
    nlbad = json.loads(json.dumps(clauses))
    nlbad[4]["not_localizable"] = True
    nlbad[4]["established"] = ["S1"]
    chk("r7_not_localizable_nonempty", any("not_localizable" in e for e in
        check_map_integrity(parse_map(contract_map(nlbad))[0], [], pass0, contract, ledger)))

    # R7: gap_finding_id that does not resolve in the ledger
    gapbad = json.loads(json.dumps(clauses))
    gapbad[0]["gap_finding_id"] = "F-XXX-99"
    chk("r7_gap_unresolved", any("does not resolve in the Findings Ledger" in e for e in
        check_map_integrity(parse_map(contract_map(gapbad))[0], [], pass0, contract, ledger)))

    # R7: wrong NON-NEGOTIABLES count (denominator recomputed from Contract, not Map)
    dropnn = json.loads(json.dumps(clauses))[:4]   # drop C5 -> 1 nonneg row, contract has 2
    dropnn_text = contract_map([dict(c) for c in dropnn])
    # renumber to C1..C4 so the id-sequence check isn't what fails
    chk("r7_nonneg_count", any("NON-NEGOTIABLES clause" in e for e in
        check_map_integrity(parse_map(dropnn_text)[0], [], pass0, contract, ledger)))

    # ---- R3 hostile: a Map citing a nonexistent scene id (caught by R7 too, and by R3 at render)
    ghost = json.loads(json.dumps(clauses))
    ghost[0]["established"] = ["S99"]
    ghost_text = contract_map(ghost)
    go, ge = parse_map(ghost_text)
    r7g = check_map_integrity(go, ge, pass0, contract, ledger)
    chk("r3_nonexistent_scene_r7", any("not a Pass 0 scene" in e for e in r7g))

    # ---- R1 hostile: outline whose Scene Spine dropped a scene
    good_outline = render_outline(pass0, contract, ledger, map_obj, "Example", "r")
    dropped_spine = good_outline.replace(
        "- S3 · the keeper confesses he has never lit the lamp. · the valley's one landmark is a lie the town agreed to keep.\n", "")
    code, ls = check(pass0, contract, ledger, map_text, dropped_spine)
    chk("r1_dropped_scene", code == 1 and any("R1 spine projection" in x for x in ls))

    # ---- R2 hostile: outline dropping a contract field
    dropped_field = good_outline.replace("- ENDING TYPE: open\n", "")
    code, ls = check(pass0, contract, ledger, map_text, dropped_field)
    chk("r2_dropped_field", code == 1 and any("R2 contract fidelity" in x and "ENDING TYPE" in x for x in ls))

    # ---- R4 hostile: a gap cell paraphrasing (not byte-matching) its ledger entry
    para_gap = good_outline.replace(
        "- gap: F-PCF-02 [Should-Fix] the town's secret is stated in dialogue but never dramatized",
        "- gap: F-PCF-02 [Should-Fix] the secret isn't shown on the page")
    code, ls = check(pass0, contract, ledger, map_text, para_gap)
    chk("r4_paraphrased_gap", code == 1 and any("R4 no fabricated gap" in x for x in ls))

    # ---- R5: framework shorthand arriving VERBATIM from an upstream artifact — the only way shorthand
    #      can legitimately appear in a projection — is a WARN by default, ERROR under --strict, with NO
    #      override slug (Fable-review fold, 2026-07-06: R5 reuses the letter's warn-only lint
    #      semantics; R1-R4/R7 own integrity, so a lint hit is a legibility advisory about the upstream
    #      artifact, not a breach). Mirror of the R6 arm's shape: default exit 0 + WARN, --strict exit 1.
    if lc is not None:
        con5 = contract.replace("TONE COMPS: quiet, elegiac", "TONE COMPS: quiet, per Pass 11F")
        map5 = contract_map(clauses, inputs={
            "pass0_sha256": sha256(pass0), "contract_sha256": sha256(con5), "ledger_sha256": sha256(ledger)})
        mo5 = parse_map(map5)[0]
        out5 = render_outline(pass0, con5, ledger, mo5, "Example", "r")
        code5, ls5 = check(pass0, con5, ledger, map5, out5)
        chk("r5_upstream_shorthand_warns", code5 == 0 and any("R5 author-facing" in x for x in ls5))
        chk("r5_strict_fails", check(pass0, con5, ledger, map5, out5, strict=True)[0] == 1)
        # shorthand INJECTED into the rendered outline (not from an input) is not R5's business — the
        # byte-determinism gate owns authored-in-the-deliverable text and still hard-fails it.
        leaked = good_outline.replace("## Coverage note", "## Coverage note\n\nPass 11F flagged this.")
        code, ls = check(pass0, contract, ledger, map_text, leaked)
        chk("r5_injected_prose_fails_determinism", code == 1 and any("byte-exact projection" in x for x in ls))

    # ---- R6 hostile: a DROPPED PROMISE CLAUSE leaves the promise prose partly unmapped -> WARN by
    #      default, FAIL under --strict. This stays R7-clean: dropping the 2nd promise clause (and
    #      renumbering C1..C4) keeps 1 promise row (>= floor 1), 1 idea, 2 nonneg — the split-completeness
    #      question is R6's, not R7's (§4a). The remaining single promise clause covers only
    #      "a woman escapes a dying town"; "the town's secret is exposed" is now unmapped word content.
    r6drop = [c for c in json.loads(json.dumps(clauses)) if c["clause_id"] != "C2"]
    for i, c in enumerate(r6drop):
        c["clause_id"] = "C%d" % (i + 1)
    r6_map = contract_map(r6drop)
    r6_mo = parse_map(r6_map)[0]
    r6_outline = render_outline(pass0, contract, ledger, r6_mo, "Example", "r")
    code_default, ls_d = check(pass0, contract, ledger, r6_map, r6_outline)
    chk("r6_dropped_promise_warn", code_default == 0 and any("R6 contract coverage" in x for x in ls_d))
    code_strict, ls_s = check(pass0, contract, ledger, r6_map, r6_outline, strict=True)
    chk("r6_dropped_promise_strict_fails", code_strict == 1 and any("R6 contract coverage" in x for x in ls_s))
    # ...silenced by the reader-contract-coverage override (SSoT slug, no bare scan)
    ov_map = r6_map.replace("<!-- apodictic:contract_map",
                            "<!-- override: reader-contract-coverage — partial promise split is intentional -->\n<!-- apodictic:contract_map")
    code_ov, _ = check(pass0, contract, ledger, ov_map, render_outline(pass0, contract, ledger, parse_map(ov_map)[0], "Example", "r"), strict=True)
    chk("r6_override_silences", code_ov == 0)
    # code-span decoy: an override quoted inside a fenced block does NOT silence R6 (override_marker SSoT)
    decoy_map = r6_map.replace("<!-- apodictic:contract_map",
                               "```\n<!-- override: reader-contract-coverage — decoy -->\n```\n<!-- apodictic:contract_map")
    code_decoy, ls_decoy = check(pass0, contract, ledger, decoy_map, render_outline(pass0, contract, ledger, parse_map(decoy_map)[0], "Example", "r"), strict=True)
    chk("r6_codespan_decoy_not_silenced", code_decoy == 1 and any("R6 contract coverage" in x for x in ls_decoy))
    denom_ni, _ = recompute_clauses(contract)
    chk("r6_idea_denominator", denom_ni["idea_field"] == "CONTROLLING IDEA")

    # ---- narrative-nf fixture: the CENTRAL QUESTION / PROMISE TYPE block drives the idea clause
    nf_contract = (
        "# Contract — NF Example\n\n## Contract Schema\n\n"
        "GENRE/SUBGENRE: narrative nonfiction\n"
        "READER PROMISE: the reader learns how the dam failed and who knew\n"
        "CONTROLLING IDEA: \n"
        "HEAT LEVEL: \n"
        "DARKNESS LEVEL: \n"
        "PRIMARY TENSION TYPE: epistemic\n"
        "ENDING TYPE: closed\n"
        "TONE COMPS: investigative\n"
        "STRUCTURE COMPS: braided\n"
        "NON-NEGOTIABLES: the engineer's warning is quoted verbatim\n"
        "CENTRAL QUESTION: why did the dam fail\n"
        "PROMISE TYPE: Reveal\n")
    nf_pass0 = (
        "# Pass 0 — NF\n\n"
        "### S1\nWhat happens: the dam cracks during the spring melt.\n"
        "What the reader now knows: the failure was sudden and public.\n\n"
        "### S2\nWhat happens: an engineer's buried memo surfaces.\n"
        "What the reader now knows: someone predicted this in writing.\n")
    nf_ledger = "# Ledger — NF\n"
    nf_denom, nf_err = recompute_clauses(nf_contract)
    chk("nf_idea_is_central_question", nf_denom["idea_field"] == "CENTRAL QUESTION" and not nf_err)
    nf_clauses = [
        {"clause_id": "C1", "source_field": "READER PROMISE",
         "clause_text": "the reader learns how the dam failed and who knew", "established": ["S1"],
         "paid_off": ["S2"], "not_localizable": False, "gap_finding_id": None},
        {"clause_id": "C2", "source_field": "CENTRAL QUESTION",
         "clause_text": "why did the dam fail", "established": ["S1"], "paid_off": ["S2"],
         "not_localizable": False, "gap_finding_id": None},
        {"clause_id": "C3", "source_field": "NON-NEGOTIABLES",
         "clause_text": "the engineer's warning is quoted verbatim", "established": [], "paid_off": [],
         "not_localizable": True, "gap_finding_id": None},
    ]
    nf_map = ("# Contract Map — NF\n\n<!-- apodictic:contract_map\n%s\n-->\n"
              % json.dumps({"schema": _MAP_SCHEMA,
                            "inputs": {"pass0_sha256": sha256(nf_pass0), "contract_sha256": sha256(nf_contract), "ledger_sha256": sha256(nf_ledger)},
                            "clauses": nf_clauses}, indent=2))
    nf_mo, nf_se = parse_map(nf_map)
    chk("nf_r7_clean", check_map_integrity(nf_mo, nf_se, nf_pass0, nf_contract, nf_ledger) == [])
    nf_outline = render_outline(nf_pass0, nf_contract, nf_ledger, nf_mo, "NF", "r")
    nfc, _nfl = check(nf_pass0, nf_contract, nf_ledger, nf_map, nf_outline)
    chk("nf_clean_validate", nfc == 0)
    chk("nf_central_question_projected", "- CENTRAL QUESTION: why did the dam fail" in nf_outline)

    # ---- resolution: a real run folder round-trips through build + validate
    d = tempfile.mkdtemp()
    made.append(d)
    for nm, body in (("Example_Pass0_Reverse_Outline_r.md", pass0),
                     ("Example_Contract_r.md", contract),
                     ("Example_Findings_Ledger_r.md", ledger),
                     ("Example_Contract_Map_r.md", map_text)):
        with open(os.path.join(d, nm), "w", encoding="utf-8", newline="") as fh:
            fh.write(body)
    chk("build_writes_outline", build(d) == 0)
    chk("run_folder_validates", run([d])[0] == 0)
    chk("missing_outline_usage", run([d + "/nope"])[0] == 2)
    # build refuses a stale map (writes nothing)
    with open(os.path.join(d, "Example_Contract_Map_r.md"), "w", encoding="utf-8", newline="") as fh:
        fh.write(bad_hash)
    os.remove(os.path.join(d, "Example_Reader_Contract_Outline_r.md"))
    chk("build_refuses_stale_map", build(d) == 1 and not os.path.exists(os.path.join(d, "Example_Reader_Contract_Outline_r.md")))

    for d in made:
        shutil.rmtree(d, ignore_errors=True)
    print("Self-test: PASS" if rc["v"] == 0 else "Self-test: FAIL")
    return rc["v"]


# ---------------------------------------------------------------- CLI

def main(argv):
    if "--self-test" in argv:
        return run_self_test()
    if len(argv) > 1 and argv[1] == "build":
        rest = [a for a in argv[2:] if not a.startswith("-")]
        to_stdout = "-o-" in argv[2:]
        if len(rest) != 1 or not os.path.isdir(rest[0]):
            print("Usage: reader_contract_outline.py build <staging> [-o-]")
            return 2
        return build(rest[0], out_stream=sys.stdout if to_stdout else None)
    args = [a for a in argv[1:] if a != "reader-contract-outline"]
    strict = "--strict" in args
    paths = [a for a in args if not a.startswith("--")]
    if not paths:
        print("Usage: reader_contract_outline.py reader-contract-outline <run_folder|files...> "
              "[--strict] | build <staging> | --self-test")
        return 2
    code, lines = run(paths, strict=strict)
    for ln in lines:
        print(ln)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
