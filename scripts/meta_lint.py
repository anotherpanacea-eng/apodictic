#!/usr/bin/env python3
"""validator-conventions — a meta-linter that validates the APODICTIC validator FLEET.

`validate.sh validator-conventions` shells out here. The fleet's structural conventions — every
self-testable validator is wired into the dispatcher, file resolvers classify on PARSED BLOCKS not
raw substrings, the advertised count is DERIVED not hand-typed, every schema is actually consumed —
were enforced only by manual review, and the gaps caused real latent bugs (a fleet-wide adversarial
sweep, 2026-06-20, found a recurring resolver-substring class and others). This validator mechanizes
those conventions so the classes cannot recur: a validator that validates the validators.

  M1 dispatch+self-test  every name in validate.sh's AGG_VALIDATORS has a `<name>)` dispatcher case
                         whose body handles `--self-test` (so `--self-test-all` can run it).
  M2 resolver hygiene    no validator script classifies inputs by a raw `"apodictic:<type>" in <text>`
                         substring (which misroutes a file that merely NAMES the marker in prose,
                         silently false-passing). Resolvers must classify on parsed blocks (the
                         `_has_block` / `art.parse_blocks` idiom). The signature anti-pattern of the
                         2026-06-20 sweep.
  M3 derived count       validate.sh derives the validator count from AGG_VALIDATORS (AGG_COUNT via
                         `$#`) — never a hand-typed integer that can drift.
  M4 no orphan schema    every `*.schema.json` in schemas/ is referenced (its $id appears) in at least
                         one validator script — a schema nothing consumes is dead or mis-wired.

It reads validate.sh and the sibling `*.py` from its own directory and the schemas via the shared
resolver. No artifact input. See docs/validator-conventions.md.

  meta_lint.py validator-conventions
  meta_lint.py --self-test

Exit: 0 clean, 1 violation(s), 2 usage.
"""
import ast
import io
import os
import re
import sys
import tokenize

try:
    import apodictic_artifacts as art
except ImportError:
    art = None


def _read_text(path):
    """Read a file as UTF-8, REPLACING undecodable bytes — a stray non-UTF-8 source file must not
    crash the linter with `UnicodeDecodeError` (a `ValueError`, NOT an `OSError`, so the bare
    `except OSError` would not catch it). Returns None if the path can't be opened at all."""
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return None


def _str_token_value(tok_string):
    """The text content of a string-literal token (its prefix + surrounding quotes stripped).
    Best-effort — used only for substring scanning, so escape sequences need not be resolved."""
    j = 0
    while j < len(tok_string) and tok_string[j] in "rbufRBUF":
        j += 1
    body = tok_string[j:]
    for q in ('"""', "'''", '"', "'"):
        if body.startswith(q) and body.endswith(q) and len(body) >= 2 * len(q):
            return body[len(q):-len(q)]
    return tok_string


def _docstring_starts(py_text):
    """(row, col) start of every bare string-expression statement — module / class / function
    docstrings and stray string statements (an `ast.Expr` whose value is a str constant). These
    are PROSE, not executable references, so a schema id appearing only there must not satisfy
    M4's no-orphan gate (Codex P2). Returns an empty set if the source does not parse (then no
    docstring is dropped — the over-count fallback, never a crash)."""
    try:
        tree = ast.parse(py_text)
    except (SyntaxError, ValueError):
        return set()
    starts = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) \
                and isinstance(node.value.value, str):
            starts.add((node.value.lineno, node.value.col_offset))
    return starts


def _strip_comments(py_text):
    """Return `py_text` with `#` comments AND bare string-expression statements (docstrings)
    removed, but EXECUTABLE string literals kept — so a schema id is counted by M4 only when it's
    referenced in code (e.g. `load_schema("apodictic.x.v1")`), not when it's merely mentioned in a
    comment OR a docstring (Codex P2). Adjacent string literals are merged into their concatenated
    contents so an id split across implicit string concatenation (`"apodictic." "finding.v1"`) is
    still found. Falls back to the raw text if the file does not tokenize (over-counts, the pre-fix
    behavior, rather than crashing)."""
    try:
        toks = [t for t in tokenize.generate_tokens(io.StringIO(py_text).readline)
                if t.type != tokenize.COMMENT]
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return py_text
    docstring_starts = _docstring_starts(py_text)
    out, i = [], 0
    while i < len(toks):
        if toks[i].type == tokenize.STRING:
            # A run of adjacent string literals (implicit concatenation) is merged into one
            # contiguous value, so `"apodictic." "finding.v1"` resolves to `apodictic.finding.v1`.
            # If the run IS a bare string-expression statement (a docstring), drop it whole — its
            # text is prose, not a live reference.
            run_is_docstring = toks[i].start in docstring_starts
            chunk = []
            while i < len(toks) and toks[i].type == tokenize.STRING:
                if not run_is_docstring:
                    chunk.append(_str_token_value(toks[i].string))
                i += 1
            if chunk:
                out.append("".join(chunk))
        else:
            out.append(toks[i].string)
            i += 1
    return " ".join(out)

# A raw marker-substring membership test used for classification — the M2 anti-pattern. A literal
# "apodictic:<type>" immediately tested with `in`. The safe `_has_block` degraded fallback uses a
# FORMAT string (`"apodictic:%s" % btype`), which this literal pattern deliberately does NOT match.
# Matches EITHER quote style — `'apodictic:x' in` is the same anti-pattern as `"apodictic:x" in`
# (Codex P2: the double-quote-only pattern let the single-quoted equivalent through).
_SUBSTRING_CLASSIFY_RE = re.compile(r"""['"]apodictic:[A-Za-z_]+['"]\s+in\b""")
_HAS_BLOCK_DEF_RE = re.compile(r"^def _has_block\b", re.MULTILINE)
_AGG_RE = re.compile(r'^AGG_VALIDATORS="([^"]*)"', re.MULTILINE)
_CASE_RE = re.compile(r"^  ([a-z0-9][a-z0-9-]*)\)\s*$", re.MULTILINE)
_COUNT_DERIVE_RE = re.compile(r"AGG_COUNT=\$\(set -- \$AGG_VALIDATORS;\s*echo \$#\)")
# scripts that are not artifact validators (no resolver convention to hold)
_M2_EXEMPT = {"apodictic_artifacts.py", "meta_lint.py", "sync_setec.py", "config_checks.py"}


def agg_validators(sh_text):
    m = _AGG_RE.search(sh_text or "")
    return m.group(1).split() if m else []


def dispatcher_cases(sh_text):
    """{case_name: body_text} for each `^  <name>)` case (body up to the next `;;`)."""
    out = {}
    text = sh_text or ""
    for m in _CASE_RE.finditer(text):
        name = m.group(1)
        end = text.find("\n    ;;", m.end())
        out[name] = text[m.end():end if end != -1 else len(text)]
    return out


def check_m1(sh_text):
    """Every AGG validator has a dispatcher case that handles --self-test."""
    viol = []
    cases = dispatcher_cases(sh_text)
    for name in agg_validators(sh_text):
        if name not in cases:
            viol.append("M1 dispatch: AGG validator '%s' has no dispatcher case" % name)
        elif "--self-test" not in cases[name]:
            viol.append("M1 self-test: dispatcher case '%s' does not handle --self-test "
                        "(--self-test-all would skip or fail it)" % name)
    return viol


def check_m2(py_name, py_text):
    """A validator that classifies inputs by raw marker substring instead of parsed blocks.

    Flags ANY literal `"apodictic:<type>" in` membership test (the classification anti-pattern),
    regardless of whether _has_block is also defined — a file must replace EVERY such test, not just
    add the helper. The safe _has_block fallback uses a `"apodictic:%s" % btype` FORMAT string, which
    the literal pattern deliberately does not match."""
    if py_name in _M2_EXEMPT:
        return []
    if _SUBSTRING_CLASSIFY_RE.search(py_text or ""):
        return ["M2 resolver-hygiene: %s classifies inputs by a raw \"apodictic:<type>\" in <text> "
                "substring — a file that merely names the marker in prose misroutes and silently "
                "false-passes; classify on parsed blocks (the _has_block / art.parse_blocks idiom)"
                % py_name]
    return []


def check_m3(sh_text):
    """The validator count is derived from AGG_VALIDATORS, not hand-typed."""
    if not _COUNT_DERIVE_RE.search(sh_text or ""):
        return ["M3 derived-count: validate.sh does not derive AGG_COUNT from AGG_VALIDATORS "
                "(`AGG_COUNT=$(set -- $AGG_VALIDATORS; echo $#)`) — a hand-typed count can drift"]
    return []


def check_m4(schema_ids, all_py_text):
    """Every schema $id is referenced by some validator script."""
    viol = []
    for sid in schema_ids:
        if sid not in all_py_text:
            viol.append("M4 orphan-schema: %s is defined in schemas/ but referenced by no validator "
                        "script (dead or mis-wired)" % sid)
    return viol


# ---------------------------------------------------------------- live run

def _script_dir():
    return os.path.dirname(os.path.abspath(__file__))


def run():
    d = _script_dir()
    sh_path = os.path.join(d, "validate.sh")
    sh_text = _read_text(sh_path)
    if sh_text is None:
        return 2, ["validator-conventions: cannot read %s" % sh_path]

    py_files = {}
    for fn in sorted(os.listdir(d)):
        if fn.endswith(".py"):
            txt = _read_text(os.path.join(d, fn))
            if txt is not None:
                py_files[fn] = txt
    # M4 reads code, not comments: strip `#` comments so a schema id mentioned only in a comment is
    # not counted as referenced (Codex P2).
    all_py = "\n".join(_strip_comments(t) for t in py_files.values())
    schema_ids = art.known_schema_ids() if art else []

    viol = []
    viol += check_m1(sh_text)
    for name, text in py_files.items():
        viol += check_m2(name, text)
    viol += check_m3(sh_text)
    viol += check_m4(schema_ids, all_py)

    lines = ["validator-conventions: %d validator(s), %d schema(s) checked"
             % (len(agg_validators(sh_text)), len(schema_ids))]
    for v in viol:
        lines.append("  ERROR: %s" % v)
    if viol:
        lines.append("validator-conventions: FAIL (%d violation(s))" % len(viol))
        return 1, lines
    lines.append("validator-conventions: PASS (dispatch+self-test + resolver hygiene + derived count "
                 "+ no orphan schema)")
    return 0, lines


# ---------------------------------------------------------------- self-test

def run_self_test():
    rc = {"v": 0}

    def chk(name, cond):
        print("  %s: %s" % (name, "OK" if cond else "FAIL"))
        if not cond:
            rc["v"] = 1

    GOOD_SH = ('AGG_VALIDATORS="alpha beta"\n'
               'AGG_COUNT=$(set -- $AGG_VALIDATORS; echo $#)\n'
               '  alpha)\n    python3 x --self-test\n    ;;\n'
               '  beta)\n    if [ "${1:-}" = "--self-test" ]; then python3 y --self-test; fi\n    ;;\n')

    # M1
    chk("m1_clean", check_m1(GOOD_SH) == [])
    chk("m1_missing_case", any("no dispatcher case" in v for v in
        check_m1('AGG_VALIDATORS="alpha gamma"\n  alpha)\n    python3 x --self-test\n    ;;\n')))
    chk("m1_no_selftest", any("does not handle --self-test" in v for v in
        check_m1('AGG_VALIDATORS="alpha"\n  alpha)\n    python3 x foo\n    ;;\n')))

    # M2
    chk("m2_substring_flagged", check_m2("bad.py", 'def resolve(p):\n    if "apodictic:finding" in t:\n        return p\n') != [])
    chk("m2_substring_single_quote_flagged", check_m2("bad.py", "def resolve(p):\n    if 'apodictic:finding' in t:\n        return p\n") != [])
    chk("m2_has_block_ok", check_m2("good.py", 'def _has_block(text, bt):\n    return any(b==bt for b in x)\ndef resolve(p):\n    if _has_block(t, "finding"):\n        return p\n') == [])
    chk("m2_format_fallback_ok", check_m2("ok.py", 'def _has_block(text, btype):\n    return ("apodictic:%s" % btype) in (text or "")\n') == [])
    chk("m2_no_marker_ok", check_m2("plain.py", 'def check(t):\n    return "scene id" in t\n') == [])
    chk("m2_exempt", check_m2("apodictic_artifacts.py", '"apodictic:finding" in t') == [])

    # M3
    chk("m3_derived_ok", check_m3(GOOD_SH) == [])
    chk("m3_missing_fails", check_m3('AGG_VALIDATORS="a b"\necho "2 validators"\n') != [])

    # M4
    chk("m4_referenced_ok", check_m4(["apodictic.finding.v1"], 'load_schema("apodictic.finding.v1")') == [])
    chk("m4_orphan_fails", any("orphan-schema" in v for v in check_m4(["apodictic.ghost.v1"], "nothing here")))
    # M4 reads CODE, not comments: a schema id mentioned only in a `#` comment is an orphan (Codex P2),
    # while a string-literal reference still counts as consumed.
    chk("m4_comment_only_is_orphan",
        any("orphan-schema" in v for v in
            check_m4(["apodictic.ghost.v1"], _strip_comments("# wires apodictic.ghost.v1\nx = 1\n"))))
    chk("m4_string_literal_referenced_ok",
        check_m4(["apodictic.ghost.v1"], _strip_comments('SID = "apodictic.ghost.v1"\n')) == [])
    # an id split across implicit string concatenation is still found (adjacent literals merged)
    chk("m4_implicit_string_concat_referenced_ok",
        check_m4(["apodictic.ghost.v1"], _strip_comments('SID = "apodictic." "ghost.v1"\n')) == [])
    # a schema id mentioned ONLY in a docstring (a bare string statement) is prose, not a reference
    chk("m4_docstring_only_is_orphan",
        any("orphan-schema" in v for v in
            check_m4(["apodictic.ghost.v1"], _strip_comments('"""Supports apodictic.ghost.v1."""'))))
    # ...but an executable literal in the SAME file still counts (docstring dropped, literal kept)
    chk("m4_executable_literal_with_docstring_ok",
        check_m4(["apodictic.ghost.v1"],
                 _strip_comments('"""doc."""\nSID = "apodictic.ghost.v1"\n')) == [])

    # _read_text: a non-UTF-8 byte sequence must not crash the linter (UnicodeDecodeError is a
    # ValueError, not an OSError); errors="replace" keeps the ASCII references scannable.
    import tempfile
    fd, _tmp = tempfile.mkstemp(suffix=".py")
    os.write(fd, b'# \xff\xfe not utf-8\nSID = "apodictic.ghost.v1"\n')
    os.close(fd)
    try:
        chk("read_text_non_utf8_no_crash", "apodictic.ghost.v1" in (_read_text(_tmp) or ""))
    finally:
        os.unlink(_tmp)
    chk("read_text_missing_returns_none", _read_text(_tmp) is None)

    print("Self-test: PASS" if rc["v"] == 0 else "Self-test: FAIL")
    return rc["v"]


def main(argv):
    if "--self-test" in argv:
        return run_self_test()
    args = [a for a in argv[1:] if a != "validator-conventions" and not a.startswith("--")]
    code, lines = run()
    for ln in lines:
        print(ln)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
