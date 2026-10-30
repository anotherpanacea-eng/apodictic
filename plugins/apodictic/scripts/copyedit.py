#!/usr/bin/env python3
"""copyedit — Voice-Aware Copyedit, Increment 1: style-sheet harvest and the query-only gate.

`validate.py copyedit <run_folder|queries_file> [--strict]` delegates here. Increment 1 ships no
replacement text: the pass emits only queries (`apodictic.copyedit_item.v1`, `disposition: query`),
and the author's answers build a voice ledger (`apodictic.voice_ledger.v1` blocks in
`[Project]_Style_Sheet.md`). See docs/voice-aware-copyediting.md.

  harvest     `copyedit.py harvest <snapshot> [--json]` inventories the competing forms a
              copyeditor would query: closed / hyphenated / open compounds (email, e-mail, e mail),
              mid-sentence capitalization variants (god, God), -ise/-ize and -our/-or pairs. Counts
              and paragraph loci only; it proposes nothing and changes nothing.

  E1 schema       a copyedit_item or voice_ledger block fails its schema; duplicate ids; an item id
                  whose P<paragraph> is not the paragraph of its first instance.
  E2 provenance   an instance's `original` is not the snapshot's UTF-8 bytes at its offsets, the
                  offsets split a code point, or the instance crosses a paragraph break.
  E3 ledger guard an item touches a form under an enforceable author entry (book, chapter,
                  paragraph range, instance), i.e. re-asks a question the author answered; or it
                  touches an inferred or declared (speaker/zone-scoped) entry without naming it in
                  `ledger_refs`, which is the possible-voice label.
  W1 never-flag   best-effort: an item whose reason names a never-flag rule (split infinitive,
                  sentence-final preposition, sentence-initial conjunction, singular they, fragment,
                  contraction). The real guard is the list in the pass prompt. ERROR under --strict.

Paragraphs are the snapshot's blank-line-separated blocks, numbered from 1; a block starting with
`# ` starts a chapter. Offsets are UTF-8 byte offsets over the snapshot.

  copyedit.py copyedit <run_folder|queries_file> [--strict]
  copyedit.py harvest <snapshot> [--json]
  copyedit.py --self-test

Exit: 0 clean / WARN-only, 1 ERROR (or WARN under --strict), 2 usage.
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

_ITEM_SCHEMA = "apodictic.copyedit_item.v1"
_LEDGER_SCHEMA = "apodictic.voice_ledger.v1"
_QUERIES_GLOB = "*_Copyedit_Queries_*.md"
_STYLE_GLOB = "*_Style_Sheet.md"
_ENFORCEABLE = re.compile(r"^(book|chapter:\d+|paragraphs:\d+-\d+|instance:P\d+\.\d+)$")
_NEVER_FLAG = (
    ("split infinitive", r"split(?:ting)?\s+(?:an?\s+|the\s+)?infinitive"),
    ("sentence-final preposition", r"(?:end|ends|ending)\s+(?:a\s+sentence\s+|the\s+sentence\s+)?(?:with|in|on)\s+a\s+preposition"),
    ("sentence-initial conjunction", r"(?:begin|begins|beginning|start|starts|starting|open|opens|opening)\s+(?:a\s+sentence\s+|the\s+sentence\s+)?with\s+(?:a\s+)?(?:conjunction|['\"]?(?:and|but|or|so)\b)"),
    ("singular they", r"singular\s+['\"]?they"),
    ("fragment", r"\b(?:sentence\s+)?fragment\b"),
    ("contraction", r"\bcontractions?\b"),
)


# ------------------------------------------------------------------ snapshot geometry

def paragraphs(data):
    """[(start_byte, end_byte, chapter)] for each blank-line-separated block of `data` (bytes)."""
    out, chapter = [], 0
    for m in re.finditer(rb"[^\n]+(?:\n[^\n]+)*", data):
        block = m.group(0)
        if not block.strip():
            continue
        if block.startswith(b"# "):
            chapter += 1
        out.append((m.start(), m.end(), chapter))
    return out


def paragraph_of(paras, start, end):
    """1-based paragraph number holding [start, end), or None if it crosses a block boundary."""
    for n, (a, b, _ch) in enumerate(paras, 1):
        if a <= start and end <= b:
            return n
    return None


def _mentions(text, form):
    return re.search(r"(?<!\w)%s(?!\w)" % re.escape(form), text) is not None


def _scope_covers(scope, para_no, chapter, item_id):
    if scope == "book":
        return True
    kind, _, arg = scope.partition(":")
    if kind == "chapter":
        return chapter == int(arg)
    if kind == "paragraphs":
        lo, hi = (int(x) for x in arg.split("-"))
        return lo <= para_no <= hi
    if kind == "instance":
        return item_id == arg
    return True  # speaker / zone: declared, cannot be narrowed mechanically


# ------------------------------------------------------------------ parsing

def _blocks(text, btype, schema_id):
    out = []
    if art is None:
        return out
    schema = art.load_schema(schema_id)
    idx = 0
    for bt, obj, jerr in art.parse_blocks(text or ""):
        if bt != btype:
            continue
        idx += 1
        where = "%s #%d" % (btype, idx)
        if jerr:
            out.append((None, ["%s: invalid JSON — %s" % (where, jerr)]))
        else:
            out.append((obj, art.validate_obj(obj, schema, where)))
    return out


def _read(path, mode="r"):
    try:
        with open(path, mode, **({} if "b" in mode else {"encoding": "utf-8"})) as fh:
            return fh.read()
    except OSError:
        return None


def check(items_text, snapshot, ledger_text, strict=False):
    """Return (errors, warns) for a queries file against its snapshot (bytes) and style sheet."""
    errors, warns = [], []
    paras = paragraphs(snapshot) if snapshot is not None else []
    if snapshot is None:
        errors.append("E2: no snapshot to prove instances against")

    ledger, seen_vl = [], set()
    for obj, errs in _blocks(ledger_text, "voice_ledger", _LEDGER_SCHEMA):
        errors.extend("E1 %s" % e for e in errs)
        if obj is None or errs:
            continue
        if obj["id"] in seen_vl:
            errors.append("E1: duplicate ledger id %s" % obj["id"])
        seen_vl.add(obj["id"])
        ledger.append(obj)

    seen = set()
    for obj, errs in _blocks(items_text, "copyedit_item", _ITEM_SCHEMA):
        errors.extend("E1 %s" % e for e in errs)
        if obj is None or errs:
            continue
        iid = obj["id"]
        if iid in seen:
            errors.append("E1: duplicate item id %s" % iid)
        seen.add(iid)
        if obj.get("replacement") is not None:
            errors.append("E1 %s: a query carries no replacement text (Increment 1 is queries only)" % iid)
        located = []
        for k, inst in enumerate(obj["instances"]):
            s, e, orig = inst.get("start_byte"), inst.get("end_byte"), inst.get("original")
            if not (isinstance(s, int) and isinstance(e, int) and isinstance(orig, str)
                    and not isinstance(s, bool) and not isinstance(e, bool) and 0 <= s < e):
                errors.append("E1 %s: instance %d needs integer start_byte < end_byte and a string original" % (iid, k))
                continue
            if snapshot is None:
                continue
            if e > len(snapshot):
                errors.append("E2 %s: instance %d runs past the end of the snapshot" % (iid, k))
                continue
            try:
                text = snapshot[s:e].decode("utf-8")
            except UnicodeDecodeError:
                errors.append("E2 %s: instance %d splits a UTF-8 code point" % (iid, k))
                continue
            if text != orig:
                errors.append("E2 %s: instance %d original %r is not the snapshot text %r" % (iid, k, orig, text))
                continue
            p = paragraph_of(paras, s, e)
            if p is None:
                errors.append("E2 %s: instance %d crosses a paragraph break" % (iid, k))
                continue
            located.append((orig, p, paras[p - 1][2]))
        if located and int(iid[1:].split(".")[0]) != located[0][1]:
            errors.append("E1 %s: id names paragraph %s but its first instance is in paragraph %d"
                          % (iid, iid[1:].split(".")[0], located[0][1]))
        refs = set(obj.get("ledger_refs") or [])
        for entry in ledger:
            touched = [(o, p, ch) for o, p, ch in located if _mentions(o, entry["form"])]
            touched = [t for t in touched if _scope_covers(entry["scope"], t[1], t[2], iid)]
            if not touched:
                continue
            if entry["origin"] == "author" and _ENFORCEABLE.match(entry["scope"]):
                errors.append("E3 %s: touches %r, which the author settled in %s (%s)"
                              % (iid, entry["form"], entry["id"], entry["scope"]))
            elif entry["id"] not in refs:
                errors.append("E3 %s: touches %r (%s, %s %s) without naming it in ledger_refs"
                              % (iid, entry["form"], entry["id"], entry["origin"], entry["scope"]))
        reason = obj.get("reason", "")
        for label, pat in _NEVER_FLAG:
            if re.search(pat, reason, re.I):
                warns.append("W1 %s: reason invokes a never-flag rule (%s)" % (iid, label))
    if art is None:
        errors.append("E1: apodictic_artifacts unavailable; cannot check schemas")
    return errors, warns


def _runlabel(path):
    m = re.search(r"_Copyedit_Queries_(.+)\.md$", os.path.basename(path))
    return m.group(1) if m else None


def resolve(path):
    """(queries, snapshot, style_sheet) paths for a run folder or a queries file."""
    if os.path.isdir(path):
        found = glob.glob(os.path.join(path, _QUERIES_GLOB))
        queries = max(found, key=os.path.getmtime) if found else None
    else:
        queries = path if os.path.isfile(path) else None
    if not queries:
        return None, None, None
    folder = os.path.dirname(os.path.abspath(queries))
    label = _runlabel(queries)
    snaps = glob.glob(os.path.join(folder, "*_Manuscript_Snapshot_%s.md" % glob.escape(label or ""))) if label else []
    styles = glob.glob(os.path.join(folder, _STYLE_GLOB)) or glob.glob(os.path.join(os.path.dirname(folder), _STYLE_GLOB))
    return queries, (snaps[0] if len(snaps) == 1 else None), (styles[0] if len(styles) == 1 else None)


def run(path, strict=False):
    queries, snap, style = resolve(path)
    if not queries:
        return 2, ["copyedit: no Copyedit_Queries file found (need *_Copyedit_Queries_<runlabel>.md)"]
    errors, warns = check(_read(queries), _read(snap, "rb") if snap else None,
                          _read(style) if style else "", strict)
    lines = ["copyedit: %s (snapshot: %s; style sheet: %s)" % (
        os.path.basename(queries), os.path.basename(snap) if snap else "none",
        os.path.basename(style) if style else "none")]
    lines += ["  ERROR: %s" % m for m in errors]
    lines += ["  %s: %s" % ("ERROR (--strict)" if strict else "WARN", m) for m in warns]
    bad = bool(errors) or (strict and bool(warns))
    lines.append("  %s" % ("FAIL" if bad else "OK"))
    return (1 if bad else 0), lines


# ------------------------------------------------------------------ harvest

_ALIASES = {"allright": "alright"}  # spelled-out pairs whose letters differ
_WORD = re.compile(r"[A-Za-z]+(?:[-'][A-Za-z]+)*")


def harvest(data):
    """Competing-form groups: [{"class", "forms": {form: [paragraph, ...]}}]."""
    text = data.decode("utf-8")
    loci = {}  # form -> [paragraph numbers]
    caps = {}  # lower -> {"lower": [...], "cap": [...]}
    for n, (a, b, _ch) in enumerate(paragraphs(data), 1):
        block = data[a:b].decode("utf-8")
        if block.startswith("#"):
            continue
        words = list(_WORD.finditer(block))
        for i, m in enumerate(words):
            w = m.group(0)
            loci.setdefault(w.lower(), []).append(n)
            if i + 1 < len(words) and block[m.end():words[i + 1].start()] == " ":
                loci.setdefault((w + " " + words[i + 1].group(0)).lower(), []).append(n)
            before = block[:m.start()].rstrip()
            sentence_start = not before or before[-1] in ".!?:\"“'‘(—"
            if not sentence_start and w.isalpha():
                slot = caps.setdefault(w.lower(), {"lower": [], "cap": []})
                slot["cap" if w[0].isupper() else "lower"].append(n)
    groups = []
    by_key = {}
    for form in loci:
        key = form.replace("-", "").replace(" ", "")
        by_key.setdefault(_ALIASES.get(key, key), set()).add(form)
    for key, forms in sorted(by_key.items()):
        if len(forms) > 1 and any(" " not in f for f in forms):
            groups.append({"class": "compound", "forms": {f: loci[f] for f in sorted(forms)}})
    for w, slot in sorted(caps.items()):
        if slot["lower"] and slot["cap"]:
            groups.append({"class": "capitalization",
                           "forms": {w: slot["lower"], w[0].upper() + w[1:]: slot["cap"]}})
    for w in sorted(loci):
        for a, b, cls in (("ise", "ize", "ise/ize"), ("our", "or", "our/or")):
            if w.isalpha() and a in w:
                other = w[::-1].replace(a[::-1], b[::-1], 1)[::-1]
                if other in loci and other != w:
                    groups.append({"class": cls, "forms": {w: loci[w], other: loci[other]}})
    return groups


def harvest_lines(groups):
    if not groups:
        return ["No competing forms found."]
    lines = ["Competing forms (counts, paragraphs). Ask the author which form the book uses; "
             "a form used one way throughout may be voice."]
    for g in groups:
        parts = ["%s ×%d (¶ %s)" % (f, len(ps), ", ".join(str(p) for p in ps[:8]) + (" …" if len(ps) > 8 else ""))
                 for f, ps in g["forms"].items()]
        lines.append("- %s: %s" % (g["class"], "; ".join(parts)))
    return lines


# ------------------------------------------------------------------ self-test

def run_self_test():
    fails = []

    def chk(name, cond):
        if not cond:
            fails.append(name)

    snap = ("# One\n\nIt was alright by him. She sent an e-mail.\n\n"
            "\"We was there,\" said Jim. The email came.\n\n"
            "# Two\n\nAll right, she said. Thank God; god help us. Café.\n").encode("utf-8")

    def at(s):
        i = snap.index(s.encode("utf-8"))
        return {"start_byte": i, "end_byte": i + len(s.encode("utf-8")), "original": s}

    def item(iid, *forms, **kw):
        obj = {"schema": _ITEM_SCHEMA, "id": iid, "instances": [at(f) for f in forms],
               "kind": "consistency", "disposition": "query", "level": 2, "zone": "narration",
               "ledger_refs": [], "style_ref": None, "reason": "Which form does the book use?"}
        obj.update(kw)
        return "<!-- apodictic:copyedit_item %s -->\n" % json.dumps(obj)

    def entry(eid, form, scope, origin="author"):
        return "<!-- apodictic:voice_ledger %s -->\n" % json.dumps(
            {"schema": _LEDGER_SCHEMA, "id": eid, "form": form, "scope": scope, "origin": origin,
             "evidence": ["¶2"], "run": "t1"})

    ok = item("P2.1", "e-mail", "email")
    e, w = check(ok, snap, "")
    chk("clean_query_passes", not e and not w)

    bad = dict(at("e-mail"))
    bad["original"] = "email"
    e, _ = check("<!-- apodictic:copyedit_item %s -->" % json.dumps(
        {"schema": _ITEM_SCHEMA, "id": "P2.1", "instances": [bad], "kind": "spelling",
         "disposition": "query", "level": 1, "zone": "narration", "ledger_refs": [],
         "style_ref": None, "reason": "?"}), snap, "")
    chk("e2_wrong_original", any(x.startswith("E2") for x in e))

    cafe = at("Café")
    split = dict(cafe, end_byte=cafe["end_byte"] - 1, original="Caf")
    e, _ = check(item("P5.1", "Café").replace(json.dumps(cafe), json.dumps(split)), snap, "")
    chk("e2_split_codepoint", any("code point" in x for x in e))

    cross = {"start_byte": snap.index(b"e-mail"), "end_byte": snap.index(b"The email") + 3,
             "original": snap[snap.index(b"e-mail"):snap.index(b"The email") + 3].decode()}
    e, _ = check(item("P2.1", "e-mail").replace(json.dumps(at("e-mail")), json.dumps(cross)), snap, "")
    chk("e2_crosses_paragraph", any("paragraph break" in x for x in e))

    e, _ = check(item("P3.1", "e-mail"), snap, "")
    chk("e1_id_paragraph_mismatch", any("names paragraph" in x for x in e))

    e, _ = check(ok + ok, snap, "")
    chk("e1_duplicate_id", any("duplicate item id" in x for x in e))

    e, _ = check(item("P2.1", "e-mail", disposition="suggest"), snap, "")
    chk("e1_increment1_query_only", any(x.startswith("E1") for x in e))

    e, _ = check(item("P2.1", "e-mail", replacement="email"), snap, "")
    chk("e1_query_has_no_replacement", any("no replacement" in x for x in e))

    e, _ = check(ok, snap, entry("VL-01", "e-mail", "book"))
    chk("e3_author_stet_blocks_requery", any(x.startswith("E3") and "settled" in x for x in e))

    e, _ = check(ok, snap, entry("VL-01", "e-mail", "chapter:2"))
    chk("e3_scope_outside_chapter_is_free", not e)

    e, _ = check(item("P5.1", "god"), snap, entry("VL-02", "god", "speaker:Jim"))
    chk("e3_declared_scope_needs_label", any("without naming" in x for x in e))
    e, _ = check(item("P5.1", "god", ledger_refs=["VL-02"]), snap, entry("VL-02", "god", "speaker:Jim"))
    chk("e3_declared_scope_labelled_passes", not e)

    e, _ = check(item("P5.1", "god"), snap, entry("VL-03", "god", "book", "inferred"))
    chk("e3_inferred_needs_label", any("without naming" in x for x in e))

    e, _ = check(ok, snap, entry("VL-01", "e-mail", "book") + entry("VL-01", "x", "book"))
    chk("e1_duplicate_ledger_id", any("duplicate ledger id" in x for x in e))

    e, w = check(item("P2.1", "e-mail", reason="This sentence fragment should be completed."), snap, "")
    chk("w1_never_flag_fragment", any("fragment" in x for x in w) and not e)
    e, w = check(item("P2.1", "e-mail", reason="Avoid ending a sentence with a preposition."), snap, "")
    chk("w1_never_flag_preposition", bool(w))

    groups = harvest(snap)
    classes = {(g["class"], tuple(sorted(g["forms"]))) for g in groups}
    chk("harvest_compound", ("compound", ("e-mail", "email")) in classes)
    chk("harvest_alright", ("compound", ("all right", "alright")) in classes)
    chk("harvest_capitalization", ("capitalization", ("God", "god")) in classes)

    if fails:
        print("copyedit self-test FAILED: %s" % ", ".join(fails))
        return 1
    print("copyedit self-test: all checks passed")
    return 0


def _usage():
    print("Usage: copyedit.py copyedit <run_folder|queries_file> [--strict] | harvest <snapshot> [--json] | --self-test")
    return 2


def main(argv):
    if "--self-test" in argv:
        return run_self_test()
    args = argv[1:]
    if not args:
        return _usage()
    cmd, rest = args[0], args[1:]
    flags = [a for a in rest if a.startswith("--")]
    pos = [a for a in rest if not a.startswith("--")]
    if cmd == "copyedit" and len(pos) == 1 and set(flags) <= {"--strict"}:
        code, lines = run(pos[0], strict="--strict" in flags)
    elif cmd == "harvest" and len(pos) == 1 and set(flags) <= {"--json"}:
        data = _read(pos[0], "rb")
        if data is None:
            print("copyedit harvest: cannot read %s" % pos[0])
            return 2
        groups = harvest(data)
        if "--json" in flags:
            print(json.dumps(groups, ensure_ascii=False, indent=1))
            return 0
        code, lines = 0, harvest_lines(groups)
    else:
        return _usage()
    for ln in lines:
        print(ln)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
