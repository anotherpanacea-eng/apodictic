#!/usr/bin/env python3
"""persona-divergence — structural integrity for Reader-Persona Simulation.

`validate.sh persona-divergence <run_folder|files>` shells out here. Pass 1 maps the experience of
ONE composite reader; a manuscript meets an audience with different tolerances. Persona simulation
runs the reader-experience lens through several declared reading DISPOSITIONS and surfaces where the
predicted experience DIVERGES — divergence is the diagnostic signal, as contract-mismatch is. This
validator owns the divergence-prediction contract and the three mechanical guards that keep it a
LENS, never the non-viable Simulated Reader Focus Group (Horizon item 17): predictions are grounded
(D2), personas are closed-key disposition vectors (D5), and fabricated testimony is scanned (D4).

  D1 schema            a persona / divergence block fails its schema (bad disposition enum, bad
                       target type, malformed P-NN / D-NN id, missing anchor/magnitude/experiences,
                       broken JSON, duplicate id); a nested `experiences` value is not one of
                       engaged|neutral|friction|disengage, or names a persona id that was not declared.
  D2 grounded          a divergence `anchor` resolves to NEITHER a real apodictic.finding.v1 id in the
     prediction       Ledger NOR a real Timeline scene id (locus). An ungrounded prediction is a
                       fabricated one — the signature firewall gate (ERROR).
  D3 target-severity   not exactly one persona is target:true; OR a divergence's optional
     anchoring         `asserted_severity` is LOWER than its anchored finding's locked Ledger severity.
                       Segmentation may not downgrade the target-audience verdict (ERROR).
  D4 no fabricated     the map presents a first-person reader-reaction QUOTE ("I got bored …") as data
     testimony        — invented reader testimony, the #17 boundary. Advisory; ERROR under --strict.
                       Override: <!-- override: persona-quote D-NN — quoting the manuscript -->, where
                       D-NN must be a DECLARED divergence id (a bogus id does not silence the scan).
  D5 disposition,      a persona block carries ANY key outside {schema, id, target, the five
     not character     disposition axes} — a persona is a parameterization, never an invented
                       character. A closed-key ERROR, NON-overridable (one of the three #17 guards;
                       the subset engine silently allows unknown keys, so this is the real guarantee).
  W1 coverage          fewer than two personas, or no disposition axis varies across them — there is no
                       contrast for divergence to surface. Advisory; ERROR under --strict.

The map (persona + divergence blocks) is read with the Findings Ledger (anchor resolution + locked
severities) and optionally the Timeline (locus anchors). Reuses apodictic_artifacts. See
docs/reader-persona-simulation.md.

  persona_divergence.py persona-divergence <run_folder|files...> [--strict]
  persona_divergence.py --self-test

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

_PERSONA_SCHEMA = "apodictic.persona.v1"
_DIVERGENCE_SCHEMA = "apodictic.divergence.v1"
_FINDING_SCHEMA = "apodictic.finding.v1"
_MAP_GLOB = "*_Persona_Divergence_Map_*.md"
_LEDGER_GLOB = "*_Findings_Ledger_*.md"

# D5 — the closed set of keys a persona block may carry. Anything else makes it a character, not a
# disposition vector. This is the real guarantee (the subset engine allows unknown keys).
_PERSONA_KEYS = {"schema", "id", "target", "pace_tolerance", "genre_familiarity",
                 "content_sensitivity", "thematic_receptivity", "continuity_attention"}
_DISPOSITION_AXES = _PERSONA_KEYS - {"schema", "id", "target"}
_EXPERIENCE_ENUM = {"engaged", "neutral", "friction", "disengage"}
_RANK = {"Could-Fix": 1, "Should-Fix": 2, "Must-Fix": 3}

# Finding Lifecycle-ID token (mirrors finding_trace._ID_RE) — for the finding-anchor path of D2.
_FINDING_ID_RE = re.compile(r"^F-[A-Za-z0-9]+-[0-9]{2,}$")
# D4 — a first-person reader-reaction quote presented as data (the fabricated-testimony signature).
_QUOTE_RE = re.compile(
    r'["“]\s*I\s+(?:got|felt|was|wasn\'?t|couldn\'?t|did\s?n\'?t|started|stopped|loved|hated|'
    r'skimmed|skipped|put\s+it\s+down|put\s+the\s+book\s+down|gave\s+up|lost\s+interest|'
    r'wanted|found\s+myself|kept\s+reading|raced\s+through)\b',
    re.IGNORECASE)
_OVERRIDE_RE = re.compile(r"<!--\s*override:\s*([a-z-]+)\s+(D-[0-9]+)\b", re.IGNORECASE)
# A divergence-id reference in reader-facing PROSE (e.g. a "### D-NN" section heading) — used to scope
# a persona-quote override to the divergence whose section a quote sits under (D4).
_DIV_ID_RE = re.compile(r"\bD-[0-9]+\b")
_HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)


def _read(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return None


def _overrides(text, slug):
    return {m.group(2) for m in _OVERRIDE_RE.finditer(text) if m.group(1).lower() == slug}


def _parse(text, btype, schema_id):
    """[(obj_or_None, schema_errs, index), ...] for each apodictic:<btype> block."""
    out = []
    if not text or art is None:
        return out
    schema = art.load_schema(schema_id)
    idx = 0
    for bt, obj, jerr in art.parse_blocks(text):
        if bt != btype:
            continue
        idx += 1
        where = "%s #%d" % (btype, idx)
        if jerr:
            out.append((None, ["%s: invalid JSON — %s" % (where, jerr)], idx))
            continue
        out.append((obj, art.validate_obj(obj, schema, where), idx))
    return out


def ledger_index(ledger_text):
    """{finding_id: obj} for the ledger's SCHEMA-VALID apodictic.finding.v1 blocks. A malformed finding
    (invalid JSON, bad/missing severity, missing required field) is NOT indexed — it cannot ground a
    prediction (D2) nor anchor a severity (D3), so a divergence anchored to one surfaces as ungrounded
    instead of silently passing D2 while escaping D3 (Codex P1)."""
    out = {}
    if not ledger_text or art is None:
        return out
    schema = art.load_schema(_FINDING_SCHEMA)
    for bt, obj, jerr in art.parse_blocks(ledger_text):
        if bt != "finding" or jerr or not isinstance(obj, dict) or not obj.get("id"):
            continue
        if schema is not None and art.validate_obj(obj, schema, "finding %s" % obj.get("id")):
            continue  # schema-invalid finding is not a valid anchor
        out[obj["id"]] = obj
    return out


def timeline_scene_ids(timeline_text):
    """The set of Scene IDs in a Timeline Event Ledger (the addressable locus set)."""
    ids = set()
    if not timeline_text:
        return ids
    header = None
    for ln in timeline_text.split("\n"):
        if not ln.lstrip().startswith("|"):
            header = None
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if all(set(c) <= set("-: ") for c in cells):
            continue
        low = [c.lower() for c in cells]
        if any("scene id" in c for c in low):
            header = low
            continue
        if header is None:
            continue
        for i, c in enumerate(cells):
            if i < len(header) and "scene id" in header[i] and c and c.lower() != "n/a":
                ids.add(c.strip())
    return ids


def divergence(map_text, ledger_text=None, timeline_text=None, strict=False):
    """Run the Persona Divergence integrity checks. Returns (code, lines)."""
    lines, errs, warns = [], [], []
    personas = _parse(map_text, "persona", _PERSONA_SCHEMA)
    divergences = _parse(map_text, "divergence", _DIVERGENCE_SCHEMA)
    # A map with no parsed persona/divergence blocks (prose-only, or truncated/malformed so the blocks
    # don't parse) is NOT a free pass: D4 anti-fabrication scans the reader-facing PROSE and must still
    # run — a prose-only map presenting "I got bored …" as data would bypass it otherwise (Codex P1).
    # The block-bound checks (D1/D2/D3/D5/W1) no-op naturally on the empty lists below.
    if not personas and not divergences:
        lines.append("persona-divergence: no persona / divergence blocks found — prose-level D4 only")

    index = ledger_index(ledger_text)
    scene_ids = timeline_scene_ids(timeline_text)

    # D1 — schema (per block) + duplicate ids
    for _o, schema_errs, _i in personas + divergences:
        for e in schema_errs:
            errs.append("D1 schema: %s" % e)
    valid_personas = [(o, i) for o, se, i in personas if o is not None and not se]
    valid_divs = [(o, i) for o, se, i in divergences if o is not None and not se]
    seen = {}
    for o, i in valid_personas + valid_divs:
        seen.setdefault(o.get("id"), []).append(i)
    for bid, where in sorted(seen.items()):
        if len(where) > 1:
            errs.append("D1 schema: %s appears %d times (ids must be unique)" % (bid, len(where)))

    persona_ids = {o.get("id") for o, _ in valid_personas}

    # D5 — persona is a disposition, not a character (closed-key; non-overridable ERROR)
    for o, _i in valid_personas:
        extra = sorted(k for k in o.keys() if k not in _PERSONA_KEYS)
        if extra:
            errs.append("D5 disposition-not-character: persona %s carries key(s) outside the closed "
                        "disposition set: %s — a persona is a parameterization, not a character"
                        % (o.get("id"), ", ".join(extra)))

    # D1 (nested) — experiences enum membership + keys resolve to a declared persona
    for o, _i in valid_divs:
        exp = o.get("experiences")
        if not isinstance(exp, dict):
            continue  # the schema's type:object check already reported a non-object
        if not exp:
            errs.append("D1 schema: divergence %s has an empty `experiences` map" % o.get("id"))
        for pid, val in exp.items():
            if not isinstance(val, str) or val not in _EXPERIENCE_ENUM:
                errs.append("D1 schema: divergence %s experiences[%s]=%r not in %s"
                            % (o.get("id"), pid, val, sorted(_EXPERIENCE_ENUM)))
            if pid not in persona_ids:
                errs.append("D1 schema: divergence %s experiences references undeclared persona %r"
                            % (o.get("id"), pid))

    # D2 — grounded prediction (anchor resolves to a real finding id OR a real Timeline scene id)
    for o, _i in valid_divs:
        anchor = (o.get("anchor") or "").strip()
        grounded = anchor in index or anchor in scene_ids
        if not grounded:
            hint = (" (looks like a finding id but is not in the Ledger)"
                    if _FINDING_ID_RE.match(anchor) else "")
            errs.append("D2 grounded-prediction: divergence %s anchor %r resolves to neither a "
                        "Ledger finding nor a Timeline scene id%s — an ungrounded prediction is a "
                        "fabricated one" % (o.get("id"), anchor, hint))

    # D3 — target-severity anchoring (exactly one target; no asserted_severity below the locked one)
    targets = [o.get("id") for o, _ in valid_personas if o.get("target") is True]
    if valid_personas and len(targets) != 1:
        errs.append("D3 target-severity: exactly one persona must be target:true (found %d: %s) — "
                    "severity anchors to the target audience" % (len(targets), ", ".join(targets) or "none"))
    for o, _i in valid_divs:
        asserted = o.get("asserted_severity")
        anchor = (o.get("anchor") or "").strip()
        locked = index.get(anchor, {}).get("severity")
        if asserted in _RANK and locked in _RANK and _RANK[asserted] < _RANK[locked]:
            errs.append("D3 target-severity: divergence %s asserts %s, lower than the anchored "
                        "finding's locked %s — segmentation may not downgrade the verdict"
                        % (o.get("id"), asserted, locked))

    # D3b — a divergence must actually DIVERGE across personas, anchored to the target. An
    # experiences map that omits the target persona, or assigns every persona the SAME experience,
    # predicts no cross-persona divergence at all — the whole point of the block (Codex P1). Only
    # meaningful when a contrast is structurally possible (>= 2 personas); with fewer, W1 coverage
    # advises instead.
    target_id = targets[0] if len(targets) == 1 else None
    for o, _i in (valid_divs if len(valid_personas) >= 2 else []):
        exp = o.get("experiences")
        if not isinstance(exp, dict) or not exp:
            continue  # an empty/non-object experiences map is already a D1 error
        if target_id is not None and target_id not in exp:
            errs.append("D3 divergence-content: divergence %s omits the target persona %s from its "
                        "experiences — divergence anchors to the target audience's experience"
                        % (o.get("id"), target_id))
        # …and a divergence should predict EVERY declared persona, not only some — an omitted persona
        # is an incomplete prediction (Codex P2). Advisory (ERROR --strict); the target omission above
        # is the harder ERROR, so don't double-report it here.
        missing = [pid for pid in sorted(persona_ids) if pid not in exp and pid != target_id]
        if missing:
            warns.append("D3 coverage: divergence %s omits declared persona(s) %s from its experiences "
                         "— predict every declared persona's experience" % (o.get("id"), ", ".join(missing)))
        vals = [v for v in exp.values() if isinstance(v, str)]
        if len(vals) == len(exp) and len(set(vals)) < 2:
            only = ", ".join(sorted(set(vals))) or "—"
            errs.append("D3 divergence-content: divergence %s assigns every persona the same "
                        "experience (%s) — there is no cross-persona divergence to surface"
                        % (o.get("id"), only))

    # D4 — no fabricated testimony (advisory; ERROR --strict). A persona-quote override silences a
    # quote ONLY when it names a REAL divergence id AND that divergence SCOPES the quote — i.e. its
    # D-NN is the divergence-id reference most recently preceding the quote in the prose (e.g. the quote
    # sits under that divergence's "### D-NN" section). So a D-01 override never silences a D-02 quote,
    # and a bogus id silences nothing (Codex P2). Scan the VISIBLE prose only — the persona/divergence
    # blocks (and any explanatory note, incl. the override markers) are HTML comments stripped here;
    # fabricated testimony presented *as data* lives in the reader-facing prose.
    visible = _HTML_COMMENT_RE.sub("", map_text or "")
    divergence_ids = {o.get("id") for o, _ in valid_divs}
    q_overrides = _overrides(map_text, "persona-quote") & divergence_ids
    for m in _QUOTE_RE.finditer(visible):
        preceding = _DIV_ID_RE.findall(visible[:m.start()])
        if preceding and preceding[-1] in q_overrides:
            continue  # the quote sits in the prose scope of an overridden divergence
        warns.append("D4 no-fabricated-testimony: the map presents a first-person reader-reaction "
                     "quote ('I got bored …') as data — reason about reader experience structurally, "
                     "never manufacture reader testimony (the #17 boundary)")
        break

    # W1 — coverage (need >=2 personas AND some disposition axis that varies)
    if valid_personas:
        if len(valid_personas) < 2:
            warns.append("W1 coverage: only %d persona — there is no contrast for divergence to "
                         "surface (declare at least one contrasting disposition)" % len(valid_personas))
        else:
            varies = any(len({o.get(axis) for o, _ in valid_personas if axis in o}) > 1
                         for axis in _DISPOSITION_AXES)
            if not varies:
                warns.append("W1 coverage: no disposition axis varies across the personas — they are "
                             "the same reader, so nothing can diverge")

    # Report
    lines.append("persona-divergence: %d persona(s), %d divergence(s)"
                 % (len(personas), len(divergences)))
    for o, _i in valid_personas:
        lines.append("  %-6s target=%s %s" % (o.get("id"), o.get("target"),
                     " ".join("%s=%s" % (a, o[a]) for a in sorted(_DISPOSITION_AXES) if a in o)))
    for e in errs:
        lines.append("  ERROR: %s" % e)
    for w in warns:
        lines.append("  %s: %s" % ("ERROR (--strict)" if strict else "WARN", w))

    if errs or (strict and warns):
        lines.append("persona-divergence: FAIL (%d error(s)%s)"
                     % (len(errs), ", %d strict warn(s)" % len(warns) if (strict and warns) else ""))
        return 1, lines
    if warns:
        lines.append("WARN: persona-divergence: %d advisory gap(s) — see D4/W1 above" % len(warns))
    else:
        lines.append("persona-divergence: PASS (schema + grounded prediction + target-severity "
                     "anchoring + closed-key persona + anti-fabrication)")
    return 0, lines


# ---------------------------------------------------------------- resolution

def _newest(paths):
    return max(paths, key=os.path.getmtime) if paths else None


def _has_block(text, btype):
    if art is None:
        return ("apodictic:%s" % btype) in (text or "")
    return any(bt == btype for bt, _o, _e in art.parse_blocks(text or ""))


def resolve(paths):
    """Return (map_path, ledger_path_or_None, timeline_path_or_None)."""
    if len(paths) == 1 and os.path.isdir(paths[0]):
        d = paths[0]
        return (_newest(glob.glob(os.path.join(d, _MAP_GLOB))),
                _newest(glob.glob(os.path.join(d, _LEDGER_GLOB))),
                os.path.join(d, "Timeline.md") if os.path.isfile(os.path.join(d, "Timeline.md")) else None)
    map_path = ledger_path = timeline_path = None
    for p in paths:
        text = _read(p) or ""
        if _has_block(text, "persona") or _has_block(text, "divergence"):
            map_path = map_path or p
        elif _has_block(text, "finding") or "Findings Ledger" in text:
            ledger_path = ledger_path or p
        elif "Scene ID" in text or "timeline" in os.path.basename(p).lower():
            timeline_path = timeline_path or p
    if map_path is None and paths:
        map_path = paths[0]
    return map_path, ledger_path, timeline_path


def run(paths, strict=False):
    map_path, ledger_path, timeline_path = resolve(paths)
    if not map_path:
        return 2, ["persona-divergence: no Persona Divergence Map found (need a "
                   "*_Persona_Divergence_Map_*.md or a file with apodictic:persona/divergence blocks)"]
    text = _read(map_path)
    if text is None:
        return 2, ["persona-divergence: cannot read %s" % map_path]
    return divergence(text, ledger_text=_read(ledger_path) if ledger_path else None,
                      timeline_text=_read(timeline_path) if timeline_path else None, strict=strict)


# ---------------------------------------------------------------- self-test

def run_self_test():
    import json as _j
    rc = {"v": 0}

    def chk(name, cond):
        print("  %s: %s" % (name, "OK" if cond else "FAIL"))
        if not cond:
            rc["v"] = 1

    def persona(pid, target=False, **axes):
        obj = {"schema": _PERSONA_SCHEMA, "id": pid, "target": target}
        obj.update(axes)
        return "<!-- apodictic:persona\n%s\n-->" % _j.dumps(obj)

    def div(did, anchor="F-P1-04", experiences=None, magnitude="high", asserted=None):
        obj = {"schema": _DIVERGENCE_SCHEMA, "id": did, "anchor": anchor, "magnitude": magnitude,
               "experiences": experiences if experiences is not None else {"P-01": "disengage", "P-02": "engaged"}}
        if asserted is not None:
            obj["asserted_severity"] = asserted
        return "<!-- apodictic:divergence\n%s\n-->" % _j.dumps(obj)

    def finding(fid, severity="Must-Fix", conf="HIGH"):
        obj = {"schema": _FINDING_SCHEMA, "id": fid, "mechanism": "m", "severity": severity,
               "confidence": conf, "evidence_refs": ["Ch 3"], "fix_class": "x", "risk_if_fixed": "y"}
        return "<!-- apodictic:finding\n%s\n-->" % _j.dumps(obj)

    LEDGER = finding("F-P1-04", "Must-Fix")
    TARGET = persona("P-01", target=True, pace_tolerance="low", genre_familiarity="newcomer")
    EXPERT = persona("P-02", target=False, pace_tolerance="high", genre_familiarity="expert")
    MAP = TARGET + "\n" + EXPERT + "\n" + div("D-01")

    # clean
    chk("clean", divergence(MAP, LEDGER)[0] == 0)

    # D1 — schema
    chk("d1_bad_axis_enum", divergence(persona("P-01", target=True, pace_tolerance="glacial") + EXPERT + div("D-01"), LEDGER)[0] == 1)
    chk("d1_bad_target_type", divergence(persona("P-01", target="yes") + EXPERT + div("D-01"), LEDGER)[0] == 1)
    chk("d1_bad_persona_id", divergence(persona("P1", target=True) + EXPERT + div("D-01"), LEDGER)[0] == 1)
    chk("d1_div_missing_anchor",
        divergence(TARGET + EXPERT + '<!-- apodictic:divergence\n{"schema":"apodictic.divergence.v1",'
                   '"id":"D-01","magnitude":"high","experiences":{"P-01":"friction","P-02":"engaged"}}\n-->',
                   LEDGER)[0] == 1)
    chk("d1_bad_experience_enum",
        divergence(TARGET + EXPERT + div("D-01", experiences={"P-01": "bored", "P-02": "engaged"}), LEDGER)[0] == 1)
    chk("d1_experience_undeclared_persona",
        any("undeclared persona" in ln for ln in divergence(TARGET + EXPERT + div("D-01", experiences={"P-99": "friction"}), LEDGER)[1]))
    code, lines = divergence(TARGET + EXPERT + div("D-01") + "\n" + div("D-01"), LEDGER)
    chk("d1_duplicate_id", code == 1 and any("appears 2 times" in ln for ln in lines))

    # D2 — grounded prediction
    code, lines = divergence(TARGET + EXPERT + div("D-01", anchor="F-P9-99"), LEDGER)
    chk("d2_dangling_finding_anchor", code == 1 and any("D2 grounded-prediction" in ln for ln in lines))
    code, lines = divergence(TARGET + EXPERT + div("D-01", anchor="nowhere"), LEDGER)
    chk("d2_unground_anchor", code == 1 and any("D2 grounded-prediction" in ln for ln in lines))
    # a Timeline scene-id anchor resolves
    TL = "## Section 1: Event Ledger\n| Scene ID | POV |\n|---|---|\n| Ch 4 §2 | Mara |\n"
    chk("d2_timeline_locus_resolves",
        divergence(TARGET + EXPERT + div("D-01", anchor="Ch 4 §2"), LEDGER, TL)[0] == 0)

    # D3 — target-severity anchoring
    chk("d3_zero_targets", divergence(persona("P-01") + EXPERT + div("D-01"), LEDGER)[0] == 1)
    chk("d3_two_targets", divergence(TARGET + persona("P-02", target=True) + div("D-01"), LEDGER)[0] == 1)
    code, lines = divergence(MAP.replace(div("D-01"), div("D-01", asserted="Could-Fix")), LEDGER)
    chk("d3_downgrade_blocked", code == 1 and any("D3 target-severity" in ln and "lower than" in ln for ln in lines))
    # asserting the SAME (or higher) severity is fine
    chk("d3_equal_severity_ok",
        divergence(MAP.replace(div("D-01"), div("D-01", asserted="Must-Fix")), LEDGER)[0] == 0)
    # D3b — a divergence must include the target persona AND actually diverge (Codex P1)
    chk("d3b_omits_target",
        any("omits the target" in ln for ln in
            divergence(TARGET + EXPERT + div("D-01", experiences={"P-02": "engaged"}), LEDGER)[1]))
    chk("d3b_no_divergence",
        any("no cross-persona divergence" in ln for ln in
            divergence(TARGET + EXPERT + div("D-01", experiences={"P-01": "friction", "P-02": "friction"}),
                       LEDGER)[1]))
    # a non-hashable experiences value must not crash D3b's set() — D1 owns that error (Codex P2 sibling)
    chk("d3b_nonhashable_experiences_no_crash",
        divergence(TARGET + EXPERT + div("D-01", experiences={"P-01": ["a"], "P-02": "engaged"}), LEDGER)[0] == 1)

    # D4 — no fabricated testimony (advisory; ERROR --strict; override)
    quote = MAP + '\n\nP-01: "I got bored in chapter 3 and put it down."\n'
    code, lines = divergence(quote, LEDGER)
    chk("d4_quote_advisory", code == 0 and any("D4 no-fabricated-testimony" in ln for ln in lines))
    chk("d4_quote_strict_fails", divergence(quote, LEDGER, strict=True)[0] == 1)
    ov = "<!-- override: persona-quote D-01 — quoting the manuscript, not a fabricated reader -->\n"
    # an override silences a quote ONLY within its divergence's prose scope (under "### D-NN")
    scoped_d01 = MAP + '\n\n### D-01\nP-01: "I got bored in chapter 3 and put it down."\n'
    chk("d4_override_silences", not any("D4" in ln for ln in divergence(ov + scoped_d01, LEDGER)[1]))
    # Codex P2 repro: a D-01 override must NOT silence a quote scoped to a DIFFERENT divergence (D-02)
    MAP2 = TARGET + "\n" + EXPERT + "\n" + div("D-01") + "\n" + div("D-02", experiences={"P-01": "engaged", "P-02": "friction"})
    cross = ov + MAP2 + '\n\n### D-02\nP-02: "I got bored and stopped reading."\n'
    chk("d4_override_scoped_other_div_fires", any("D4" in ln for ln in divergence(cross, LEDGER)[1]))
    chk("d4_override_scoped_other_div_strict_fails", divergence(cross, LEDGER, strict=True)[0] == 1)
    # a structural prediction (no first-person quote) is clean
    chk("d4_structural_clean",
        not any("D4" in ln for ln in divergence(MAP + "\n\nA pace-sensitive disposition is at elevated disengagement risk across Ch 3.\n", LEDGER)[1]))
    # a quote INSIDE an HTML comment (an explanatory note, not reader-facing data) is clean
    chk("d4_quote_in_comment_clean",
        not any("D4" in ln for ln in divergence(MAP + '\n<!-- note: D4 catches "I got bored" quotes -->\n', LEDGER)[1]))

    # --- Codex round 2 ---
    # P1: a prose-only / truncated map (NO parsed blocks) must still run D4 — it bypassed it entirely.
    prose_only = 'P-01: "I got bored in chapter 3 and put it down."\n'
    chk("d4_prose_only_fires", any("D4" in ln for ln in divergence(prose_only, LEDGER)[1]))
    chk("d4_prose_only_strict_fails", divergence(prose_only, LEDGER, strict=True)[0] == 1)
    # P1: a MALFORMED finding (invalid severity enum) must NOT satisfy D2 grounding — so it cannot
    # silently pass D2 while escaping D3's severity anchoring. Anchoring to it surfaces as ungrounded.
    bad_ledger = finding("F-P1-04", severity="Whatever")
    code, lines = divergence(MAP, bad_ledger)
    chk("d2_malformed_finding_not_grounded", code == 1 and any("D2 grounded-prediction" in ln for ln in lines))
    chk("d2_malformed_finding_downgrade_not_masked",
        divergence(MAP.replace(div("D-01"), div("D-01", asserted="Could-Fix")), bad_ledger)[0] == 1)
    # P2: a divergence that omits a declared (non-target) persona is incomplete coverage.
    THIRD = persona("P-03", target=False, pace_tolerance="high", genre_familiarity="newcomer")
    omit3 = TARGET + EXPERT + THIRD + div("D-01", experiences={"P-01": "friction", "P-02": "engaged"})
    chk("d3_omits_declared_persona_warns", any("D3 coverage" in ln and "P-03" in ln for ln in divergence(omit3, LEDGER)[1]))
    chk("d3_omits_declared_persona_strict_fails", divergence(omit3, LEDGER, strict=True)[0] == 1)
    # P2: a bogus persona-quote override (id not a declared divergence) must NOT disable D4 globally;
    # the real-id override still silences.
    bogus_ov = "<!-- override: persona-quote D-99 — no such divergence -->\n"
    chk("d4_bogus_override_still_fires", any("D4" in ln for ln in divergence(bogus_ov + quote, LEDGER)[1]))
    chk("d4_bogus_override_strict_fails", divergence(bogus_ov + quote, LEDGER, strict=True)[0] == 1)
    chk("d4_real_override_still_silences", not any("D4" in ln for ln in divergence(ov + scoped_d01, LEDGER)[1]))

    # D5 — closed-key (non-overridable)
    code, lines = divergence(persona("P-01", target=True, name="Sarah, 34, a teacher") + EXPERT + div("D-01"), LEDGER)
    chk("d5_stray_key", code == 1 and any("D5 disposition-not-character" in ln and "name" in ln for ln in lines))
    # D5 is non-overridable: even with a (wrong) override marker it still fails
    chk("d5_non_overridable",
        divergence("<!-- override: persona-quote D-01 — x -->\n" + persona("P-01", target=True, backstory="orphan") + EXPERT + div("D-01"), LEDGER)[0] == 1)

    # W1 — coverage (advisory)
    code, lines = divergence(TARGET + div("D-01", experiences={"P-01": "friction"}), LEDGER)
    chk("w1_single_persona", code == 0 and any("W1 coverage" in ln for ln in lines))
    same = persona("P-01", target=True, pace_tolerance="low") + persona("P-02", target=False, pace_tolerance="low")
    chk("w1_no_variation",
        any("W1 coverage" in ln and "no disposition axis varies" in ln for ln in divergence(same + div("D-01"), LEDGER)[1]))
    chk("w1_strict_fails", divergence(same + div("D-01"), LEDGER, strict=True)[0] == 1)

    # no blocks -> no-op
    chk("no_blocks_noop", divergence("# Notes\nnothing\n")[0] == 0)

    # resolution
    import tempfile
    import shutil
    d = tempfile.mkdtemp()
    try:
        mp = os.path.join(d, "Proj_Persona_Divergence_Map_run.md")
        with open(mp, "w", encoding="utf-8", newline="") as fh:
            fh.write("# Persona Divergence Map\n" + MAP + "\n")
        lp = os.path.join(d, "Proj_Findings_Ledger_run.md")
        with open(lp, "w", encoding="utf-8", newline="") as fh:
            fh.write("# Findings Ledger\n" + LEDGER + "\n")
        chk("run_folder_resolution", run([d])[0] == 0)
        chk("explicit_files_resolution", run([mp, lp])[0] == 0)
        chk("explicit_files_order_independent", run([lp, mp])[0] == 0)
        chk("missing_artifact_usage", run([os.path.join(d, "nope.md")])[0] == 2)
    finally:
        shutil.rmtree(d, ignore_errors=True)

    print("Self-test: PASS" if rc["v"] == 0 else "Self-test: FAIL")
    return rc["v"]


def main(argv):
    if "--self-test" in argv:
        return run_self_test()
    args = [a for a in argv[1:] if a != "persona-divergence"]
    strict = "--strict" in args
    paths = [a for a in args if not a.startswith("--")]
    if not paths:
        print("Usage: persona_divergence.py persona-divergence <run_folder|files...> [--strict] | --self-test")
        return 2
    code, lines = run(paths, strict=strict)
    for ln in lines:
        print(ln)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
