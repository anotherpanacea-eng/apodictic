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
  M2 resolver hygiene    no validator script classifies inputs by a raw marker scan/membership op (a
                         literal `apodictic:<type>` reached by `in`/`not in`/`.find`/`.count`/
                         `re.search`/… ) — the anti-pattern misroutes a file that merely NAMES the
                         marker in EXECUTABLE code, silently false-passing. Resolvers must classify on
                         parsed blocks (the `_has_block` / `art.parse_blocks` idiom). The signature
                         anti-pattern of the 2026-06-20 sweep.
  M3 derived count       validate.sh derives the validator count from AGG_VALIDATORS (AGG_COUNT via
                         `$#`) — never a hand-typed integer that can drift.
  M4 no orphan schema    every `*.schema.json` in the resolved schema dir is referenced (its filename
                         STEM — what `art.known_schema_ids()` returns — appears as a whole id) in at
                         least one validator script — a schema nothing consumes is dead or mis-wired.
                         Degrades to a WARN (not a clean PASS) when the resolver can't be imported or
                         resolves zero schemas.
  M5 override hygiene    no validator detects an override marker by a BARE `<!-- override: <slug>`
                         substring scan (Python `"<!-- override: %s" % slug in body` / bash
                         `grep -F "<!-- override:`) — that honors a SUFFIXED slug and a backtick'd
                         documentation example — NOR by a local COMPILED/inline regex
                         `re.compile(r"<!--\\s*override: …")` (boundary-matched, so it evaded the bare
                         form, but still skips code-span stripping). Use the shared
                         `override_marker.has_override` / `override_targets` (Python) / the
                         `_has_override` bash helper (boundary-matched, code-spans stripped). The
                         override-marker sibling of M2's resolver-substring class.
  M6 code-span hygiene   no validator builds a LOCAL code-span / fence stripper — a `re.compile`/`re.sub`
                         whose pattern carries a ``` / ~~~ fence run — instead of delegating to
                         `override_marker.strip_code_spans` (the single state-machine SSoT). Catches the
                         "helper exists but isn't used" drift that bypassable hand-rolled strippers
                         (the form #128 removed from timeline_checks / honesty_check) re-introduce.

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
            # Merge an implicit-concatenation run. NL / COMMENT tokens are TRANSPARENT inside it — a
            # parenthesized multiline constant (`SID = (\n "apodictic."\n "ghost.v1"\n)`) tokenizes the
            # pieces with NLs between, and Python concatenates them — but a logical NEWLINE (or any other
            # token) ends the run, so two separate string statements never merge (Codex P2 false orphan).
            while i < len(toks):
                t = toks[i]
                if t.type == tokenize.STRING:
                    if not run_is_docstring:
                        chunk.append(_str_token_value(t.string))
                    i += 1
                elif t.type in (tokenize.NL, tokenize.COMMENT):
                    i += 1
                else:
                    break
            if chunk:
                out.append("".join(chunk))
        else:
            out.append(toks[i].string)
            i += 1
    return " ".join(out)


def _blank_span(lines, start, end):
    """Overwrite the (start_row,start_col)..(end_row,end_col) token span in `lines` (1-based rows,
    0-based cols, end-exclusive per the tokenize convention) with spaces, PRESERVING every other
    byte's position — so the surviving code keeps exact adjacency (`.find(` stays `.find(`, not
    `. find (`). Newlines inside the span are kept so row numbering downstream is unchanged."""
    sr, sc = start
    er, ec = end
    for r in range(sr, er + 1):
        idx = r - 1
        if idx < 0 or idx >= len(lines):
            continue
        line = lines[idx]
        lo = sc if r == sr else 0
        hi = ec if r == er else len(line)
        lo = max(0, min(lo, len(line)))
        hi = max(0, min(hi, len(line)))
        lines[idx] = line[:lo] + (" " * (hi - lo)) + line[hi:]


def _strip_comments_keep_source(py_text):
    """For M2's SCAN-OP detection: blank `#` comments and bare string-expression statements
    (docstrings) IN PLACE — every other byte keeps its exact position — so the quoted-literal-plus-
    operator M2 patterns (`"apodictic:x" in`, `.find("apodictic:x")`, `re.search("apodictic:x", t)`)
    still match against faithfully-adjacent source. (`_strip_comments` strips the quotes off literals
    to reconstruct concatenated SCHEMA ids for M4, which would defeat the M2 regex; they are two
    deliberately different strippers.) A marker NAMED in a comment, in a docstring, or in an
    error-message string that is NOT in a scan-op context therefore cannot trip M2. Falls back to raw
    text if the file does not tokenize (over-flags rather than crashing — fail-loud)."""
    try:
        toks = list(tokenize.generate_tokens(io.StringIO(py_text).readline))
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return py_text
    docstring_starts = _docstring_starts(py_text)
    lines = py_text.split("\n")
    for t in toks:
        if t.type == tokenize.COMMENT or (t.type == tokenize.STRING and t.start in docstring_starts):
            _blank_span(lines, t.start, t.end)
    return "\n".join(lines)

# A raw marker-substring scan/membership test used for classification — the M2 anti-pattern. A
# literal `apodictic:<type>` (EITHER quote style; `<type>` may carry DIGITS — `apodictic:finding2` —
# or be an f-string interpolation `apodictic:{...}`) reached by ANY of the common scan ops the sweep
# missed when it only checked `... in`:
#   * membership      `"apodictic:x" in t`   /   `"apodictic:x" not in t`
#   * str scan method `t.find("apodictic:x")` / `.count` / `.index` / `.rfind` / `.startswith`
#                      / `.endswith` / `.partition` / `.split`
#   * re scan         `re.search("apodictic:x", t)` / `.match` / `.findall` / `.finditer` / `.fullmatch`
# The safe `_has_block` degraded fallback uses a FORMAT string (`"apodictic:%s" % btype`), whose `%s`
# is not a literal `<type>` and is deliberately NOT matched. An f-string `f"apodictic:{bt}"` IS the
# anti-pattern (it embeds the literal `apodictic:` prefix in a classification scan) and IS caught.
# `<type>`: a literal id `[A-Za-z0-9_]+` OR an f-string brace group `{...}` (optionally id-prefixed).
# The quote may carry ANY string prefix — `r`/`R` (the most natural regex form, `re.search(r"apodictic:…")`
# — Codex P2 that the f/fr/rf-only group missed), `b`/`u`/`f` and 2-letter combos (rb/rf/…).
# `_Q`: a string-literal quote — TRIPLE (`'''`/`\"\"\"`) tried before single (`'`/`"`), so a triple-quoted
# marker literal is matched, not evaded (Codex P2). Triple alts MUST precede the single class.
_Q = r"""(?:'''|\"\"\"|['"])"""
_MARKER_LIT = r"(?:[rRbBuUfF]{0,2})" + _Q + r"apodictic:(?:[A-Za-z0-9_]*\{[^}]*\}|[A-Za-z0-9_]+)" + _Q
# membership: `<lit> in` / `<lit> not in` (the literal is the left operand)
_MARKER_IN_PAT = _MARKER_LIT + r"\s+(?:not\s+)?in\b"
# scan op: `.find(<lit>` etc., or `re.search(<lit>` etc. — the literal is the (first) argument.
_SCAN_METHOD_PAT = (r"\.(?:find|rfind|index|rindex|count|startswith|endswith|partition|rpartition|split)"
                    r"\s*\(\s*" + _MARKER_LIT)
_RE_SCAN_PAT = (r"\bre\.(?:search|match|fullmatch|findall|finditer)\s*\(\s*" + _MARKER_LIT)
_SUBSTRING_CLASSIFY_RE = re.compile("(?:%s)|(?:%s)|(?:%s)"
                                    % (_MARKER_IN_PAT, _SCAN_METHOD_PAT, _RE_SCAN_PAT))
_HAS_BLOCK_DEF_RE = re.compile(r"^def _has_block\b", re.MULTILINE)
_AGG_RE = re.compile(r'^AGG_VALIDATORS="([^"]*)"', re.MULTILINE)
_CASE_RE = re.compile(r"^  ([a-z0-9][a-z0-9-]*)\)\s*$", re.MULTILINE)
_COUNT_DERIVE_RE = re.compile(r"AGG_COUNT=\$\(set -- \$AGG_VALIDATORS;\s*echo \$#\)")
# scripts that are not artifact validators (no resolver convention to hold)
_M2_EXEMPT = {"apodictic_artifacts.py", "meta_lint.py", "sync_setec.py", "config_checks.py"}

# ---- M5 override-hygiene -------------------------------------------------------------------------
# The bare override-substring anti-pattern (2026-06-20 sweep), the override-marker sibling of M2's
# resolver-substring class. A gate honors `<!-- override: <slug> — <rationale> -->`; testing for it by
# a BARE-PREFIX substring (Python `"<!-- override: %s" % slug in body` / `"<!-- override: x" in body`;
# bash `grep -F "<!-- override:`) honors a SUFFIXED slug AND a backtick'd documentation example. The
# hardened replacement is the shared `override_marker.has_override` (Python) / the `_has_override`
# helper (bash), which strip code spans and boundary-match. M5 flags the bare form so the class is
# gated going forward. Two marker spellings matter, and they are gated by two markers:
#   * `_OV_MARK` — the LITERAL form (`<!-- override:` one space, or `<!--override:` zero) used by the
#     SUBSTRING/MEMBERSHIP patterns (`in` / `.find` / format-`in`). A `<!--\s*override:` REGEX literal
#     does NOT contain that literal substring, so those patterns do not false-positive on a regex.
#   * `_OV_REGEX_MARK` — the REGEX form, used by the re-op pattern (`_OV_PY_RE_PAT`): it ALSO matches the
#     `\s`/`[[:space:]]` inter-token spelling a compiled pattern uses. A non-exempt `re.compile`/`re.search`
#     over the marker is boundary-matched yet skips code-span stripping unless it is override_marker's own
#     (exempt) — i.e. it is the decoy bypass — so it IS flagged.
#
# Python: a string/f-string literal carrying the marker reached by a scan/membership op. The marker is
# matched with FLEXIBLE whitespace after `<!--` (`<!--\s*override:`), so the zero-space `<!--override:`
# spelling the hardened parser also accepts is detected (Codex P2); any string prefix is allowed.
_OV_PFX = r"(?:[rRbBuUfF]{0,2})"
_OV_MARK = r"<!--\s*override:"
# The marker as written INSIDE a regex pattern literal: `<!--`, then a regex inter-token gap
# (`\s*` / `\s+` / `[[:space:]]*` / a literal space, or nothing), then `override:`. `\\s` matches a
# LITERAL backslash-s in the raw-string source (the form `_OV_MARK`'s whitespace `\s*` cannot match); the
# `\\\\s` alternative ALSO matches the NON-raw spelling `re.compile("<!--\\s*…")`, whose source carries
# two backslashes. Longer (two-backslash) alternative first so it wins where it applies.
_OV_REGEX_GAP = r"""(?:\\\\s[*+]?|\\s[*+]?|\[\[:space:\]\][*+]?|[ ]+)?"""
_OV_REGEX_MARK = r"<!--" + _OV_REGEX_GAP + r"override:"


def _ov_body(group):
    """A DELIMITER-AWARE marker-string body (Codex P2): capture the opening quote (a UNIQUE group name
    per call so the 4-way alternation in `_OV_PY_RE` does not collide), the override marker, then a run
    that does NOT begin the SAME closing delimiter — so an OPPOSITE quote INSIDE the literal
    (`"<!--override: author's note"`, `'<!--override: "quoted"'`, and their triple-quoted forms) cannot
    end the body early and let the bare scan evade the gate — then the matching close delimiter. The body
    uses `[\\s\\S]` (not `.`) so a MULTILINE triple-quoted literal still closes — `_OV_PY_RE` is not
    compiled DOTALL, and the closing backref bounds the run, so this stays per-alternative (Codex P2)."""
    return (_OV_PFX + (r"""(?P<%s>'''|\"\"\"|['"])""" % group) + _OV_MARK
            + (r"""(?:(?!(?P=%s))[\s\S])*?(?P=%s)""" % (group, group)))


_OV_PY_IN_PAT = _ov_body("ovq1") + r"""\s*\)?\s+(?:not\s+)?in\b"""
_OV_PY_FMT_IN_PAT = r"\(?\s*" + _ov_body("ovq2") + r"""\s*%[^)\n]*\)\s+(?:not\s+)?in\b"""
_OV_PY_SCAN_PAT = (r"""\.(?:find|rfind|index|rindex|count|startswith|endswith|partition|rpartition|split)"""
                   r"""\s*\(\s*""" + _OV_PFX + _Q + _OV_MARK)
# The re-op pattern uses `_OV_REGEX_MARK` (the `\s`/`[[:space:]]` spelling) and includes `compile`, so the
# COMPILED-REGEX form — `_OVERRIDE_RE = re.compile(r"<!--\s*override: …")` then `_OVERRIDE_RE.search(body)`
# — is gated. That form is boundary-matched (so it evaded the bare-substring patterns above) yet still
# skips code-span stripping (the decoy bypass); the id-/pair-scoped gates that carried it now route through
# override_marker.override_targets / .override_payloads. The canonical helper builds the same literal but
# lives in override_marker.py (M5-exempt).
_OV_PY_RE_PAT = (r"""\bre\.(?:search|match|fullmatch|findall|finditer|compile)\s*\(\s*""" + _OV_PFX + _Q + _OV_REGEX_MARK)
_OV_PY_RE = re.compile("(?:%s)|(?:%s)|(?:%s)|(?:%s)"
                       % (_OV_PY_IN_PAT, _OV_PY_FMT_IN_PAT, _OV_PY_SCAN_PAT, _OV_PY_RE_PAT))
# bash: a grep over the bare `<!-- override:` prefix (any whitespace), the form #128 replaced.
_OV_SH_RE = re.compile(r"""grep\b[^\n]*?['"]""" + _OV_MARK)
# override_marker.py legitimately DEFINES the hardened helper; meta_lint.py carries the M5 pattern
# literals themselves. Both are exempt from M5 (they are infra, not gates honoring overrides).
_M5_EXEMPT = {"override_marker.py", "meta_lint.py"}

# ---- M6 code-span-stripper hygiene --------------------------------------------------------------
# `override_marker.strip_code_spans` is the SINGLE state-machine code-span stripper — a marker quoted in
# a ``` fence / inline span is a documentation EXAMPLE, not a live directive. The hand-rolled form #128
# removed from timeline_checks / honesty_check (`re.compile(r"```...```|`...`")`) was bypassable by a
# multi-backtick / `~~~`-fenced / multiline / malformed-fence example (Codex P1 xN). M6 fails any
# validator that REINTRODUCES a local fence stripper — a `re.compile`/`re.sub` whose pattern literal
# carries a CommonMark FENCE run (3+ backticks or tildes) — so "the helper exists" can't drift from "the
# helper is used." Deliberately narrow to the fence form: the single-backtick INLINE matchers some
# validators use to pull a `field` / `file.md` token (no 3-run) are NOT fences and are NOT flagged, and a
# fence run living in a plain test-fixture STRING is not a re.compile/re.sub argument so it is not flagged.
# The op list mirrors M5's re-op set (compile/sub for building+stripping, plus search/match/findall/
# finditer/split for a stripper that matches or splits on the fence) so a local fence handler is gated
# however it is spelled.
_M6_FENCE = r"(?:`{3,}|~{3,})"
_M6_PY_RE = re.compile(r"""\bre\.(?:compile|sub|search|match|fullmatch|findall|finditer|split)\s*\(\s*"""
                       + _OV_PFX + _Q + r"""[^"'\n]*?""" + _M6_FENCE)
# override_marker.py legitimately DEFINES the canonical stripper; meta_lint.py carries the M6 literal.
_M6_EXEMPT = {"override_marker.py", "meta_lint.py"}


def agg_validators(sh_text):
    m = _AGG_RE.search(sh_text or "")
    return m.group(1).split() if m else []


# A case terminator: a `;;` alone on its line (any leading indent, optional trailing whitespace). The
# body runs up to the FIRST such line after the header — robust to ANY indent, where the old
# `text.find("\n    ;;")` hard-coded EXACTLY 4 spaces and would skip a `;;` at a different indent,
# over-capturing the body into the next case and silently weakening M1's --self-test membership check.
_CASE_END_RE = re.compile(r"^[ \t]*;;[ \t]*$", re.MULTILINE)


def dispatcher_cases(sh_text):
    """{case_name: body_text} for each `^  <name>)` case (body up to its terminating `;;`).

    The body ends at the first case-terminator line (`;;` alone, ANY indent) after the header — robust
    to a future case whose `;;` indent differs from the legacy 4-space form (which the old hard-coded
    `\\n    ;;` search would have skipped, over-capturing into the next case)."""
    out = {}
    text = sh_text or ""
    for m in _CASE_RE.finditer(text):
        name = m.group(1)
        endm = _CASE_END_RE.search(text, m.end())
        out[name] = text[m.end():endm.start() if endm else len(text)]
    return out


# A shell `#` comment to end-of-line, where `#` begins a line or follows whitespace (the common
# comment form). Stripped from a case body before the `--self-test` membership check so a `# TODO wire
# --self-test` comment does NOT falsely satisfy M1 (the old naive substring counted commented-out
# text). Over-stripping a `#` that sits inside a quoted string only makes M1 STRICTER, never laxer —
# the safe direction for a gate.
_SH_COMMENT_RE = re.compile(r"(?m)(^|[ \t])#.*$")


def _strip_sh_comments(body):
    return _SH_COMMENT_RE.sub(lambda m: m.group(1), body or "")


def check_m1(sh_text):
    """Every AGG validator has a dispatcher case that handles --self-test (in EXECUTABLE shell, not a
    comment)."""
    viol = []
    cases = dispatcher_cases(sh_text)
    for name in agg_validators(sh_text):
        if name not in cases:
            viol.append("M1 dispatch: AGG validator '%s' has no dispatcher case" % name)
        elif "--self-test" not in _strip_sh_comments(cases[name]):
            viol.append("M1 self-test: dispatcher case '%s' does not handle --self-test "
                        "(--self-test-all would skip or fail it)" % name)
    return viol


def check_m2(py_name, py_text):
    """A validator that classifies inputs by a raw marker scan/membership op instead of parsed blocks.

    Flags ANY literal `apodictic:<type>` reached by a membership (`in`/`not in`) OR str/re scan op (the
    classification anti-pattern), regardless of whether _has_block is also defined — a file must replace
    EVERY such test, not just add the helper. The safe _has_block fallback uses a `"apodictic:%s" %
    btype` FORMAT string, which the literal pattern deliberately does not match.

    `py_text` is scanned with `#` comments AND docstrings STRIPPED (via _strip_comments_keep_source,
    which preserves quotes + operator adjacency so the scan-op patterns still match) — symmetric with
    check_m4's comment-stripping — so a marker NAMED in a comment, a docstring, or an error-message
    string that is NOT itself a classification scan is NOT a false positive (the live anti-pattern is a
    classification test in EXECUTABLE code; e.g. content_advisory.py:340's
    `any("apodictic:finding block" in ln ...)` near-miss lives in a list-comp and IS flagged, but a
    marker mentioned in a `raise ValueError("... apodictic:finding ...")` message must not trip M2)."""
    if py_name in _M2_EXEMPT:
        return []
    if _SUBSTRING_CLASSIFY_RE.search(_strip_comments_keep_source(py_text or "")):
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


def _schema_referenced(sid, all_py_text):
    """True iff `sid` appears in `all_py_text` as a WHOLE id — not as a prefix of a longer id. A bare
    `sid in all_py_text` lets a referenced `apodictic.persona.v10` MASK an orphan `apodictic.persona.v1`
    (P3). Require an id boundary on both sides: the char adjacent to the match must not continue the id
    (`[0-9A-Za-z_.]`), so `...v1` does not match inside `...v10`."""
    return re.search(r"(?<![0-9A-Za-z_.])" + re.escape(sid) + r"(?![0-9A-Za-z_.])", all_py_text) is not None


def check_m4(schema_ids, all_py_text, degraded=False):
    """Every schema filename-stem id is referenced by some validator script.

    `degraded=True` (the resolver could not be imported, or zero schemas resolved) yields a WARN, not a
    clean PASS — the orphan-schema guarantee can't be asserted without the schema set, so it must not
    silently evaporate (mirrors the dispatch arm's python3-unavailable WARN precedent)."""
    if degraded:
        return ["M4 degraded: schema set unavailable (apodictic_artifacts not importable, or zero "
                "schemas resolved) — orphan-schema check SKIPPED, not asserted clean (WARN)"]
    viol = []
    for sid in schema_ids:
        if not _schema_referenced(sid, all_py_text):
            viol.append("M4 orphan-schema: %s (a *.schema.json filename stem in the resolved schema "
                        "dir) is referenced by no validator script (dead or mis-wired)" % sid)
    return viol


def check_m5_py(py_name, py_text):
    """A validator that detects an override marker by a BARE `<!-- override:` substring scan/membership
    op instead of the hardened `override_marker.has_override` (boundary-matched + code-spans stripped).

    Scanned with comments/docstrings stripped (so a marker NAMED in prose is not a false positive); the
    hardened helper writes `<!--\\s*override:` (no literal single space), so a `has_override(...)` call
    or the helper's own regex is not flagged."""
    if py_name in _M5_EXEMPT:
        return []
    if _OV_PY_RE.search(_strip_comments_keep_source(py_text or "")):
        return ["M5 override-hygiene: %s detects an override marker by a bare \"<!-- override: <slug>\" "
                "substring scan/membership op — honors a suffixed slug and a backtick'd documentation "
                "example; call override_marker.has_override (boundary-matched, code-spans stripped)"
                % py_name]
    return []


def check_m5_sh(sh_text):
    """validate.sh must not `grep` the bare `<!-- override:` prefix — use the shared `_has_override`
    bash helper (strips fenced + inline code spans, boundary-matches). Comment lines (`#`) are dropped
    first so the helper's documentation prose is not a false positive."""
    viol = []
    for ln in (sh_text or "").split("\n"):
        code = ln.split("#", 1)[0] if not ln.lstrip().startswith("#") else ""
        if _OV_SH_RE.search(code):
            viol.append("M5 override-hygiene: validate.sh greps the bare \"<!-- override:\" prefix "
                        "(`%s`) — honors a suffixed slug / fenced-block decoy; pipe through the shared "
                        "_has_override helper instead" % ln.strip())
    return viol


def check_m6_py(py_name, py_text):
    """A validator that builds a LOCAL code-span / fence stripper instead of delegating to the shared
    `override_marker.strip_code_spans`.

    Flags a `re.compile`/`re.sub` whose pattern literal carries a CommonMark FENCE run (3+ backticks or
    tildes) — the bypassable hand-rolled form #128 removed from timeline_checks / honesty_check ("the
    helper existing != the helper being used"). Scanned with comments/docstrings stripped, so the
    migration docstrings that QUOTE the old `re.compile(r"```…")` form in prose are not false positives;
    single-backtick inline matchers (no 3-run) and fence runs in plain test-fixture strings are not
    `re.compile`/`re.sub` arguments and are not flagged."""
    if py_name in _M6_EXEMPT:
        return []
    if _M6_PY_RE.search(_strip_comments_keep_source(py_text or "")):
        return ["M6 code-span-hygiene: %s builds a LOCAL code-fence stripper (a re.compile/re.sub whose "
                "pattern matches a ``` / ~~~ fence) — the hand-rolled form is bypassable; import and call "
                "override_marker.strip_code_spans (the single state-machine SSoT)" % py_name]
    return []


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
    # M4 degraded: the resolver could not be imported (`art is None`) OR resolved zero schemas — the
    # orphan-schema guarantee can't be asserted, so it WARNs rather than reporting a clean PASS.
    m4_degraded = art is None or not schema_ids

    viol, warn = [], []
    viol += check_m1(sh_text)
    for name, text in py_files.items():
        viol += check_m2(name, text)
    viol += check_m3(sh_text)
    m4 = check_m4(schema_ids, all_py, degraded=m4_degraded)
    if m4_degraded:
        warn += m4
    else:
        viol += m4
    # M5 override-hygiene (the override-substring sibling of M2's resolver-substring class).
    for name, text in py_files.items():
        viol += check_m5_py(name, text)
    viol += check_m5_sh(sh_text)
    # M6 code-span-stripper hygiene — no validator may carry a LOCAL fence stripper; delegate to
    # override_marker.strip_code_spans (the single state-machine SSoT) so the helper can't drift unused.
    for name, text in py_files.items():
        viol += check_m6_py(name, text)

    lines = ["validator-conventions: %d validator(s), %d schema(s) checked"
             % (len(agg_validators(sh_text)), len(schema_ids))]
    for w in warn:
        lines.append("  WARN: %s" % w)
    for v in viol:
        lines.append("  ERROR: %s" % v)
    if viol:
        lines.append("validator-conventions: FAIL (%d violation(s))" % len(viol))
        return 1, lines
    lines.append("validator-conventions: PASS (dispatch+self-test + resolver hygiene + derived count "
                 "+ no orphan schema + override hygiene + code-span hygiene%s)"
                 % (" — M4 degraded/skipped, see WARN" if m4_degraded else ""))
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
    # M1 comment false-pass: a `# TODO wire --self-test` comment must NOT satisfy M1 (the case has no
    # executable --self-test handling) — the case body is `#`-stripped before the membership check.
    chk("m1_commented_selftest_fails", any("does not handle --self-test" in v for v in
        check_m1('AGG_VALIDATORS="alpha"\n  alpha)\n    # TODO wire --self-test\n    python3 x run\n    ;;\n')))
    # M1 `;;` brittleness: a case whose terminator is at a NON-4-space indent (here 2 spaces) and which
    # LACKS --self-test must be flagged — the old hard-coded `\n    ;;` search skipped the 2-space `;;`
    # and over-captured the following compliant case's body, masking the violation.
    M1_TWOSPACE_SH = ('AGG_VALIDATORS="alpha beta"\n'
                      '  alpha)\n    python3 x run\n  ;;\n'
                      '  beta)\n    python3 y --self-test\n    ;;\n')
    chk("m1_twospace_terminator_not_over_captured",
        any("'alpha'" in v and "does not handle --self-test" in v for v in check_m1(M1_TWOSPACE_SH)))
    chk("m1_twospace_compliant_case_still_clean",
        not any("'beta'" in v for v in check_m1(M1_TWOSPACE_SH)))

    # M2
    chk("m2_substring_flagged", check_m2("bad.py", 'def resolve(p):\n    if "apodictic:finding" in t:\n        return p\n') != [])
    chk("m2_substring_single_quote_flagged", check_m2("bad.py", "def resolve(p):\n    if 'apodictic:finding' in t:\n        return p\n") != [])
    chk("m2_has_block_ok", check_m2("good.py", 'def _has_block(text, bt):\n    return any(b==bt for b in x)\ndef resolve(p):\n    if _has_block(t, "finding"):\n        return p\n') == [])
    chk("m2_format_fallback_ok", check_m2("ok.py", 'def _has_block(text, btype):\n    return ("apodictic:%s" % btype) in (text or "")\n') == [])
    chk("m2_no_marker_ok", check_m2("plain.py", 'def check(t):\n    return "scene id" in t\n') == [])
    chk("m2_exempt", check_m2("apodictic_artifacts.py", '"apodictic:finding" in t') == [])
    # M2 completeness (broadened beyond the `... in` form): the other common scan/membership ops the
    # sweep missed are ALL caught.
    chk("m2_not_in_flagged", check_m2("b.py", 'if "apodictic:finding" not in t:\n    pass\n') != [])
    chk("m2_find_flagged", check_m2("b.py", 'if t.find("apodictic:finding") >= 0:\n    pass\n') != [])
    chk("m2_count_flagged", check_m2("b.py", 'n = t.count("apodictic:finding")\n') != [])
    chk("m2_startswith_flagged", check_m2("b.py", 'if t.startswith("apodictic:finding"):\n    pass\n') != [])
    chk("m2_re_search_flagged", check_m2("b.py", 'import re\nif re.search("apodictic:finding", t):\n    pass\n') != [])
    chk("m2_re_findall_flagged", check_m2("b.py", 'import re\nxs = re.findall("apodictic:finding", t)\n') != [])
    chk("m2_re_raw_string_flagged",  # Codex P2: r"..." — the most natural regex form
        check_m2("b.py", 'import re\nif re.search(r"apodictic:finding", t):\n    pass\n') != [])
    chk("m2_triple_quote_flagged",  # Codex P2: a triple-quoted marker literal evaded the single-quote class
        check_m2("b.py", 'if """apodictic:finding""" in t:\n    pass\n') != [])
    # a marker TYPE bearing a digit (`apodictic:finding2`) — the old `[A-Za-z_]+` class missed it.
    chk("m2_digit_type_flagged", check_m2("b.py", 'if "apodictic:finding2" in t:\n    pass\n') != [])
    # an f-string marker literal in a scan still embeds the literal prefix — caught.
    chk("m2_fstring_flagged", check_m2("b.py", 'if f"apodictic:{bt}" in t:\n    pass\n') != [])
    # M2 false-positive guard (run against stripped source): a marker NAMED in a `#` comment, a
    # docstring, or an error-message string that is NOT a classification scan must NOT be flagged.
    chk("m2_comment_marker_ok", check_m2("c.py", 'def f(t):\n    # checks "apodictic:finding" in t\n    return _has_block(t, "finding")\n') == [])
    chk("m2_docstring_marker_ok", check_m2("c.py", '"""Resolves on "apodictic:finding" in the body."""\ndef f(t):\n    return _has_block(t, "finding")\n') == [])
    chk("m2_error_message_marker_ok", check_m2("c.py", 'def f(t):\n    raise ValueError("expected an apodictic:finding block in the input")\n') == [])

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
    # Codex P2: a parenthesized MULTILINE implicit concat (NL tokens between pieces) must still merge
    chk("m4_multiline_concat_referenced_ok",
        check_m4(["apodictic.ghost.v1"],
                 _strip_comments('SID = (\n    "apodictic."\n    "ghost.v1"\n)\n')) == [])
    # a schema id mentioned ONLY in a docstring (a bare string statement) is prose, not a reference
    chk("m4_docstring_only_is_orphan",
        any("orphan-schema" in v for v in
            check_m4(["apodictic.ghost.v1"], _strip_comments('"""Supports apodictic.ghost.v1."""'))))
    # ...but an executable literal in the SAME file still counts (docstring dropped, literal kept)
    chk("m4_executable_literal_with_docstring_ok",
        check_m4(["apodictic.ghost.v1"],
                 _strip_comments('"""doc."""\nSID = "apodictic.ghost.v1"\n')) == [])
    # M4 substring masking (P3): a referenced `apodictic.persona.v10` must NOT mask an orphan
    # `apodictic.persona.v1` — the id is matched on a boundary, not a bare substring.
    chk("m4_prefix_does_not_mask_orphan",
        any("orphan-schema" in v and "apodictic.persona.v1 " in (v + " ") for v in
            check_m4(["apodictic.persona.v1"], _strip_comments('SID = "apodictic.persona.v10"\n'))))
    chk("m4_whole_id_still_referenced_ok",
        check_m4(["apodictic.persona.v1"], _strip_comments('SID = "apodictic.persona.v1"\n')) == [])
    # M4 degraded: resolver unavailable / zero schemas -> a WARN (not a clean PASS), so the
    # orphan-schema guarantee does not silently evaporate.
    m4d = check_m4([], "", degraded=True)
    chk("m4_degraded_warns", len(m4d) == 1 and "degraded" in m4d[0])
    chk("m4_degraded_not_clean_pass", check_m4([], "", degraded=True) != [])

    # M5 override-hygiene (the override-substring sibling of M2). Python side:
    chk("m5_py_literal_in_flagged",
        check_m5_py("g.py", 'if "<!-- override: foo" in body:\n    pass\n') != [])
    chk("m5_py_format_in_flagged",
        check_m5_py("g.py", 'if ("<!-- override: %s" % slug) in body:\n    pass\n') != [])
    # Codex P2: an OPPOSITE-quote character inside the marker literal must not let the bare scan evade M5
    chk("m5_py_opposite_squote_in_dquote_flagged",
        check_m5_py("g.py", """if "<!--override: foo author's note" in body:\n    pass\n""") != [])
    chk("m5_py_opposite_dquote_in_squote_flagged",
        check_m5_py("g.py", """if '<!--override: foo "quoted" note' in body:\n    pass\n""") != [])
    chk("m5_py_opposite_quote_triplequoted_flagged",
        check_m5_py("g.py", 'if """<!--override: foo author\'s note""" in body:\n    pass\n') != [])
    # Codex P2: a MULTILINE triple-quoted membership literal must not evade M5 (`_OV_PY_RE` is not DOTALL;
    # the `[\s\S]` body lets the run cross the newline to its closing delimiter)
    chk("m5_py_multiline_triplequote_in_flagged",
        check_m5_py("g.py", 'if """<!--override: foo\nreason""" in body:\n    pass\n') != [])
    chk("m5_py_find_flagged",
        check_m5_py("g.py", 'if body.find("<!-- override: foo") >= 0:\n    pass\n') != [])
    chk("m5_py_re_findall_flagged",
        check_m5_py("g.py", 'import re\nxs = re.findall(r"<!-- override: ([a-z-]+)", body)\n') != [])
    # the hardened helper call is clean (it does not write the bare `<!-- override:` single-space form).
    chk("m5_py_has_override_call_ok",
        check_m5_py("g.py", 'from override_marker import has_override\nif has_override(body, "foo"):\n    pass\n') == [])
    # the INLINE regex form (`re.search(r"<!--\s*override:" …)` on raw text) is the decoy bypass in a
    # non-exempt file — now flagged (the only legitimate builder of this regex is override_marker, exempt).
    chk("m5_py_inline_regex_form_flagged",
        check_m5_py("g.py", 'import re\nif re.search(r"<!--\\s*override:\\s*" + slug, body):\n    pass\n') != [])
    # a marker NAMED in a comment / docstring is not a classification op -> not flagged.
    chk("m5_py_comment_marker_ok",
        check_m5_py("g.py", 'def f(b):\n    # honors <!-- override: foo -->\n    return has_override(b, "foo")\n') == [])
    chk("m5_py_exempt", check_m5_py("override_marker.py", '"<!-- override: foo" in body') == [])
    # M5 bash side:
    chk("m5_sh_grep_F_flagged",
        check_m5_sh('  case x)\n    grep -F "<!-- override: foo" "$F" && OV=1\n    ;;\n') != [])
    chk("m5_sh_grep_oE_flagged",
        check_m5_sh('    echo "$B" | grep -oE "<!-- override: foo-[a-z]+"\n') != [])
    # the hardened helper grep (`<!--[[:space:]]*override:`) is clean — no literal single-space form.
    chk("m5_sh_hardened_helper_ok",
        check_m5_sh('    grep -E "<!--[[:space:]]*override:[[:space:]]*${S}([[:space:]]|-->)"\n') == [])
    # a `<!-- override:` named in a `#` comment line is not an executable grep -> not flagged.
    chk("m5_sh_comment_ok",
        check_m5_sh('    # legacy: grep -F "<!-- override: foo" was the bare form\n') == [])
    # Codex P2: a bare scan in the zero-whitespace `<!--override:` spelling (which the hardened parser
    # also accepts) is a live bypass and must be flagged — Python and bash.
    chk("m5_py_zero_whitespace_flagged",
        check_m5_py("g.py", 'if "<!--override: foo" in body:\n    pass\n') != [])
    chk("m5_sh_zero_whitespace_flagged",
        check_m5_sh('  case x)\n    grep -F "<!--override: foo" "$F" && OV=1\n    ;;\n') != [])
    chk("m5_py_triple_quote_flagged",  # Codex P2: triple-quoted override literal evaded the single-quote class
        check_m5_py("g.py", 'if """<!-- override: foo""" in body:\n    pass\n') != [])
    # M5 extension: the COMPILED-regex form (boundary-matched but no code-span stripping) is now gated.
    chk("m5_py_compile_flagged",
        check_m5_py("g.py", 'import re\n_OV = re.compile(r"<!--\\s*override:\\s*([a-z-]+)\\s+(CN-[0-9]+)")\n') != [])
    chk("m5_py_compile_bracket_space_flagged",
        check_m5_py("g.py", 'import re\n_OV = re.compile(r"<!--[[:space:]]*override:foo")\n') != [])
    # …and the NON-raw string spelling (two backslashes in source) is gated too.
    chk("m5_py_compile_nonraw_string_flagged",
        check_m5_py("g.py", 'import re\n_OV = re.compile("<!--\\\\s*override: foo")\n') != [])
    # the migrated gates call override_targets (no `<!-- override:` literal) -> clean
    chk("m5_py_override_targets_call_ok",
        check_m5_py("g.py", 'from override_marker import override_targets\nx = override_targets(t, "advisory-eval", r"(CN-[0-9]+)")\n') == [])

    # M6 code-span-stripper hygiene — a LOCAL fence stripper must delegate to override_marker.
    chk("m6_compile_backtick_fence_flagged",
        check_m6_py("g.py", 'import re\n_F = re.compile(r"```[\\s\\S]*?```")\n') != [])
    chk("m6_compile_tilde_fence_flagged",
        check_m6_py("g.py", 'import re\n_F = re.compile(r"~~~.*?~~~", re.DOTALL)\n') != [])
    chk("m6_sub_fence_flagged",
        check_m6_py("g.py", 'import re\nx = re.sub(r"```.*?```", "", body)\n') != [])
    # a fence stripper spelled with search / split (not just compile/sub) is gated too
    chk("m6_search_fence_flagged",
        check_m6_py("g.py", 'import re\nm = re.search(r"```[\\s\\S]*?```", body)\n') != [])
    chk("m6_split_fence_flagged",
        check_m6_py("g.py", 'import re\nparts = re.split(r"~~~+", body)\n') != [])
    # single-backtick INLINE matchers (no 3-run) are legit token extractors -> NOT flagged
    chk("m6_inline_single_backtick_ok",
        check_m6_py("g.py", 'import re\nm = re.search(r"`([^`]+\\.md)`", cell)\n') == [])
    # a fence run inside a PLAIN test-fixture string (not a re.compile/re.sub arg) -> NOT flagged
    chk("m6_fixture_fence_string_ok",
        check_m6_py("g.py", 'def t():\n    return check("```\\n<!-- override: x -->\\n```")\n') == [])
    # the old form QUOTED in a docstring (a migration note) -> NOT flagged (docstrings stripped first)
    chk("m6_docstring_oldform_ok",
        check_m6_py("g.py", '"""Once a local re.compile(r"' + "`" * 3 + 'x' + "`" * 3 + '") stripper."""\nx = 1\n') == [])
    # the canonical stripper file is exempt
    chk("m6_exempt", check_m6_py("override_marker.py", 'import re\nr = re.compile(r"```")\n') == [])

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
