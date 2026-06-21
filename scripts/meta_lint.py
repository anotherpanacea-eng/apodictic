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
import os
import re
import sys

try:
    import apodictic_artifacts as art
except ImportError:
    art = None

# A raw marker-substring membership test used for classification — the M2 anti-pattern. A literal
# "apodictic:<type>" immediately tested with `in`. The safe `_has_block` degraded fallback uses a
# FORMAT string (`"apodictic:%s" % btype`), which this literal pattern deliberately does NOT match.
_SUBSTRING_CLASSIFY_RE = re.compile(r'"apodictic:[A-Za-z_]+"\s+in\b')
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
    try:
        sh_text = open(sh_path, encoding="utf-8").read()
    except OSError:
        return 2, ["validator-conventions: cannot read %s" % sh_path]

    py_files = {}
    for fn in sorted(os.listdir(d)):
        if fn.endswith(".py"):
            try:
                py_files[fn] = open(os.path.join(d, fn), encoding="utf-8").read()
            except OSError:
                pass
    all_py = "\n".join(py_files.values())
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
