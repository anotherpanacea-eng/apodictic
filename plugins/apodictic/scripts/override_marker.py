#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Shared, hardened override-marker detection for the APODICTIC validator fleet.

The fleet's editorial gates honor an author/orchestrator escape hatch written as an HTML comment:

    <!-- override: <slug> — <rationale> -->

The naive detector — `("<!-- override: %s" % slug) in body` — has TWO proven bypasses (the
2026-06-20 sweep; the same class #128 hardened for timeline / softness):

  1. SUFFIX COLLISION   — a bare-prefix substring test matches a *longer* slug, so a marker for
                          `<slug>-but-not-really` is wrongly read as a marker for `<slug>`. (And,
                          symmetrically, a `<slug>` test fires inside `<longer-slug>`.)
  2. CODE-SPAN DECOY    — a marker quoted as a documentation EXAMPLE inside a backtick code span
                          (inline `` `…` `` or a fenced ```` ``` ```` block) is honored as if it
                          were a live directive.

`has_override` closes both for every Python site fleet-wide (centralized, so behavior is identical
everywhere) — code spans are stripped first, then the EXACT slug must be followed by a boundary
delimiter (whitespace / em- or en-dash / the comment close / EOL). This mirrors
`timeline_checks._has_override` and `honesty_check.soft_overrides` byte-for-byte in intent.

`meta_lint.py`'s M5 gate flags the bare-substring anti-pattern this module replaces, so the class
cannot silently re-enter. See docs/validator-conventions.md.
"""
import re

# Code spans — a marker quoted inside one is a documentation EXAMPLE, not a live directive, so it is
# stripped before the override scan. CommonMark has two forms; we handle them with a small STATE MACHINE
# rather than one clever regex (successive regex patches kept breeding siblings — multiline inline spans,
# a ``` line inside a ~~~ fence, …; Codex P1 xN). `strip_code_spans` is the SINGLE source of truth — the
# bash gates delegate to it via the CLI below, so there is exactly one implementation to keep correct.
# A fence OPENER: 0–3 leading spaces (4+ or a tab is indented code, not a fence) + a run of 3+ backticks
# or tildes; group 2 is the info string (an opener may carry one). CommonMark forbids backticks in a
# BACKTICK opener's info string — that check is applied in strip_code_spans (a tilde info is unrestricted).
_FENCE_OPEN_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
# A fence CLOSER: in CommonMark a closing fence is ONLY the fence run + optional trailing whitespace —
# nothing else. A same-run line with other text (`~~~not-a-close`, ` ```python`) is CONTENT, not a
# closer, so it must not end the block early and expose a later marker (Codex P1).
_FENCE_CLOSE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})[ \t]*$")
# An inline span: a run of N backticks, then the shortest content NOT containing the closing run, then a
# matching run of N. DOTALL — CommonMark inline spans may contain line endings (the multiline form). A
# run with no matching close is NOT a span, so a stray backtick never over-strips.
_INLINE_SPAN_RE = re.compile(r"(`+)(?:(?!\1).)*?\1", re.DOTALL)

# After `<!-- override: <slug>` the slug must end at a real delimiter — whitespace, an em-/en-dash
# (the `— <rationale>` form), a hyphen-minus reason separator, the comment close `-->`, or EOL — so a
# SUFFIXED slug (`<slug>-extra`) does NOT satisfy a request for `<slug>`.
_BOUNDARY = r"(?=\s|—|–|-->|$)"


def strip_code_spans(body):
    """`body` with fenced blocks and inline code spans blanked, so a marker quoted as a documentation
    EXAMPLE is not honored as a live directive. Fenced blocks are removed line-wise — a fence closes ONLY
    on a line of the SAME fence character at length >= the opener, so a ``` line inside a ~~~ fence (or
    vice-versa) is content, not a premature close (Codex P1). Inline spans are then removed by
    matching-length backtick runs (multiline-aware)."""
    out, fence = [], None  # fence = (char, length) while inside a fenced block
    for line in (body or "").split("\n"):
        if fence is None:
            mo = _FENCE_OPEN_RE.match(line)
            # CommonMark forbids a backtick in the INFO STRING of a backtick opener, so `` ```info` `` is
            # NOT a fence (it is inline code / text) and must not open a block that swallows a LATER live
            # marker (Codex P2). A tilde opener's info string is unrestricted.
            if mo and not (mo.group(1)[0] == "`" and "`" in mo.group(2)):
                fence = (mo.group(1)[0], len(mo.group(1)))
                out.append("")             # drop the opening fence line
            else:
                out.append(line)
        else:
            mc = _FENCE_CLOSE_RE.match(line)  # a SYNTACTICALLY VALID closer only (same char, >= len, ws-only tail)
            if mc and mc.group(1)[0] == fence[0] and len(mc.group(1)) >= fence[1]:
                fence = None
            out.append("")                 # drop everything between the fences (and the fences)
    return _INLINE_SPAN_RE.sub(" ", "\n".join(out))


def has_override(body, slug):
    """True iff a GENUINE `<!-- override: <slug> ... -->` marker is present in `body`.

    Hardened against both bypasses: code spans are stripped first, and the slug is boundary-matched
    (a suffixed slug does NOT match). `slug` is matched literally (regex-escaped)."""
    region = strip_code_spans(body)
    return re.search(r"<!--\s*override:\s*" + re.escape(slug) + _BOUNDARY, region) is not None


def override_slugs(body, prefix):
    """The set of slugs present as `<!-- override: <prefix><slug> -->` markers in `body`.

    Used where the concrete slug is data-driven (e.g. per-audit `audit-propagation-<audit-slug>`):
    the caller passes the fixed `<prefix>` and gets back each `<slug>` that actually follows it in a
    live (code-span-stripped) marker. The captured `<slug>` is the lowercase-id tail
    (`[a-z0-9][a-z0-9-]*`) and — like `has_override` — must END at a real marker boundary, so a
    suffixed/malformed marker (`<prefix>foo_extra`) does NOT yield `foo` and acknowledge the real
    `foo` audit (Codex P1; kept in parity with the bash `PER_AUDIT_OVERRIDES` extraction)."""
    region = strip_code_spans(body)
    pat = re.compile(r"<!--\s*override:\s*" + re.escape(prefix) + r"([a-z0-9][a-z0-9-]*)" + _BOUNDARY)
    return set(pat.findall(region))


def override_targets(body, slug, target=None):
    """The set of finding-id tuples carried by LIVE `<!-- override: <slug> ... -->` markers in `body`.

    The id-/pair-scoped override forms `has_override` cannot express — a per-finding `<slug> <id>` or a
    `<slug> <id-a>/<id-b>` pair — used by the content-advisory / persona-divergence / intake-interview /
    author-fingerprint / world-bible gates. Each of those previously carried its OWN
    `re.compile(r"<!--\\s*override: …")` that did NOT strip code spans (the code-span-decoy bypass this
    helper closes); routing them here gives every such gate the one SSoT stripper + boundary discipline.

      * `target=None` — a PRESENCE form: the slug may stand alone (`<!-- override: world-firewall -->`)
        or carry a `— <rationale>`; returns `{()}` (truthy) if a live marker exists, else `set()`. As in
        `has_override`, `slug` must END at a real boundary, so a SUFFIXED slug does not match.
      * `target=<regex>` — the slug is followed by whitespace then the `target` payload; EACH capturing
        group in `target` becomes one element of the returned tuple (`r"(CN-[0-9]+)"` -> 1-tuples;
        `r"(WF-[0-9]+)\\s*/\\s*(WF-[0-9]+)"` -> 2-tuples). The payload must END at a real boundary.

    Like `has_override`, code spans are stripped first and the slug is matched literally (regex-escaped).
    Matching is case-sensitive — the documented marker is lowercase `override:` and every shipped slug
    and finding-id is fixed-case, so this is byte-for-byte the SSoT discipline (and the fail-closed
    direction: an off-spec mixed-case marker does not silence a finding)."""
    region = strip_code_spans(body)
    head = r"<!--\s*override:\s*" + re.escape(slug)
    if target is None:
        pat = re.compile(head + _BOUNDARY)
    else:
        pat = re.compile(head + r"\s+(?:" + target + r")" + _BOUNDARY)
    return {m.groups() for m in pat.finditer(region)}


def override_payloads(body, slug):
    """The raw `<payload>` of each LIVE `<!-- override: <slug><payload>-->` marker in `body` — the text
    between the slug boundary and the closing `-->`.

    For BESPOKE gates that PARSE the payload themselves, where a fixed id/pair `target` does not fit:
    promise-contract's drafted-copy snippet (`<!-- override: drafted-copy <snippet> — <why> -->`) and
    regression-diff's `<runlabel>:<chapter>` tokens (`<!-- override: regression-cleared Ch 3 — … -->`).
    Code spans are stripped first (a quoted example is not a live marker) and the slug is boundary-matched
    (a suffixed slug does not match). The payload is returned RAW — callers strip / split / tokenize it
    exactly as they did against their old local regex; an empty payload yields `""`."""
    region = strip_code_spans(body)
    pat = re.compile(r"<!--\s*override:\s*" + re.escape(slug) + _BOUNDARY + r"(.*?)-->", re.DOTALL)
    return [m.group(1) for m in pat.finditer(region)]


# --------------------------------------------------------------------------------------------------
# Self-test. (Each consuming validator also exercises has_override through its own decoy+suffix cases;
# this gives the shared helper direct, fast coverage of the two bypasses + the boundary forms.)
# --------------------------------------------------------------------------------------------------

def _self_test():
    rc = 0

    def chk(name, cond):
        nonlocal rc
        print("  %s: %s" % (name, "OK" if cond else "FAIL"))
        if not cond:
            rc = 1

    S = "my-slug"
    # genuine markers are honored
    chk("genuine_emdash", has_override("<!-- override: my-slug — reason -->", S))
    chk("genuine_no_reason", has_override("<!-- override: my-slug -->", S))
    chk("genuine_nospace_dash", has_override("<!-- override: my-slug—reason -->", S))
    chk("genuine_endash", has_override("<!-- override: my-slug – reason -->", S))
    chk("flexible_whitespace", has_override("<!--  override:  my-slug  -->", S))
    # bypass 1 — suffix collision is rejected
    chk("suffix_collision_rejected", not has_override("<!-- override: my-slug-but-not-really — x -->", S))
    # bypass 2 — code-span decoys are rejected, in EVERY CommonMark form (Codex P1):
    chk("inline_codespan_rejected", not has_override("Use `<!-- override: my-slug -->` to skip.", S))
    chk("fenced_block_rejected",
        not has_override("before\n```\n<!-- override: my-slug -->\n```\nafter", S))
    chk("multi_backtick_inline_rejected", not has_override("``<!-- override: my-slug -->``", S))
    chk("tilde_fence_rejected", not has_override("~~~\n<!-- override: my-slug -->\n~~~", S))
    # a MULTILINE inline span (a backtick run whose content spans lines) hides the marker too (Codex P1)
    chk("multiline_inline_rejected",
        not has_override("text `inline open\n<!-- override: my-slug -->\ninline close` more", S))
    # a ``` line INSIDE a ~~~ fence must NOT close the fence early and expose the marker (Codex P1)
    chk("tilde_fence_with_backtick_line_rejected",
        not has_override("~~~\n```\n<!-- override: my-slug -->\n```\n~~~", S))
    # a same-character run with TRAILING text is NOT a valid closer (a closing fence is fence-chars +
    # whitespace only); it must not end the block early and expose a later marker (Codex P1)
    chk("malformed_tilde_closer_rejected",
        not has_override("~~~lang\n~~~not-a-close\n<!-- override: my-slug -->\n~~~", S))
    chk("backtick_info_string_line_not_a_closer",
        not has_override("```\n```python\n<!-- override: my-slug -->\n```", S))
    # a 4-space-indented fence line is INDENTED CODE, not a real fence (opener indent capped at 3
    # spaces), so it cannot suppress a later LIVE marker (Codex P1)
    chk("indented_code_tilde_is_not_a_fence",
        has_override("    ~~~\n<!-- override: my-slug -->\n    ~~~", S))
    # a BACKTICK opener whose INFO STRING contains a backtick is NOT a valid fence (CommonMark); it must
    # not open a block that suppresses a LATER live marker (Codex P2). A tilde info string is fine.
    chk("invalid_backtick_info_string_not_a_fence",
        has_override("```info`\n<!-- override: my-slug -->\nplain", S))
    chk("tilde_info_string_with_backtick_still_a_fence",
        not has_override("~~~info`tick\n<!-- override: my-slug -->\n~~~", S))
    # …and after a fenced block CLOSES, a genuine marker is honored again (the close re-enables scanning)
    chk("genuine_after_fenced_block",
        has_override("```\n<!-- override: my-slug -->\n```\n\nReal: <!-- override: my-slug -->", S))
    # a genuinely-absent slug is not found
    chk("absent_slug", not has_override("<!-- override: other-slug -->", S))
    # override_slugs: data-driven extraction, code spans stripped
    chk("slugs_extract", override_slugs("<!-- override: ap-foo --> <!-- override: ap-bar -->", "ap-")
        == {"foo", "bar"})
    chk("slugs_skip_codespan",
        override_slugs("`<!-- override: ap-decoy -->` <!-- override: ap-real -->", "ap-") == {"real"})
    # bypass 1 in the data-driven path — a suffixed/malformed marker must NOT yield the real slug (P1):
    chk("slugs_suffix_rejected", override_slugs("<!-- override: ap-foo_extra -->", "ap-") == set())
    chk("slugs_genuine_hyphenated", override_slugs("<!-- override: ap-foo-bar -->", "ap-") == {"foo-bar"})
    # override_targets: id-/pair-scoped extraction, code spans stripped + boundary-matched
    CN = r"(CN-[0-9]+)"
    chk("targets_per_id",
        override_targets("<!-- override: advisory-eval CN-03 — why -->", "advisory-eval", CN) == {("CN-03",)})
    chk("targets_skip_inline_codespan",
        override_targets("`<!-- override: advisory-eval CN-03 -->`", "advisory-eval", CN) == set())
    chk("targets_skip_fenced_codespan",
        override_targets("```\n<!-- override: advisory-eval CN-03 -->\n```", "advisory-eval", CN) == set())
    # bypass 1 in the id path — a per-id slug must not fire for a LONGER slug (advisory-eval vs -prose)
    chk("targets_slug_boundary",
        override_targets("<!-- override: advisory-eval-prose CN-03 -->", "advisory-eval", CN) == set())
    chk("targets_pair",
        override_targets("<!-- override: world-rule WF-01/WF-02 — staged -->", "world-rule",
                         r"(WF-[0-9]+)\s*/\s*(WF-[0-9]+)") == {("WF-01", "WF-02")})
    chk("targets_multi",
        override_targets("<!-- override: persona-quote D-01 --> a <!-- override: persona-quote D-02 -->",
                         "persona-quote", r"(D-[0-9]+)") == {("D-01",), ("D-02",)})
    # presence form (target=None) — id-less slugs (world-firewall / advisory-eval-prose)
    chk("targets_presence", override_targets("<!-- override: world-firewall — x -->", "world-firewall") == {()})
    chk("targets_presence_no_reason", override_targets("<!-- override: world-firewall -->", "world-firewall") == {()})
    chk("targets_presence_skip_codespan",
        override_targets("`<!-- override: world-firewall -->`", "world-firewall") == set())
    chk("targets_presence_suffix_rejected",
        override_targets("<!-- override: world-firewall-ish -->", "world-firewall") == set())
    chk("targets_absent", override_targets("<!-- override: other CN-03 -->", "advisory-eval", CN) == set())
    # override_payloads: bespoke free-text capture, code spans stripped + slug boundary-matched
    chk("payloads_basic",
        override_payloads("<!-- override: drafted-copy the quick fox — why -->", "drafted-copy")
        == [" the quick fox — why "])
    chk("payloads_skip_inline_codespan",
        override_payloads("`<!-- override: drafted-copy x -->`", "drafted-copy") == [])
    chk("payloads_skip_fenced_codespan",
        override_payloads("```\n<!-- override: regression-cleared Ch 3 -->\n```", "regression-cleared") == [])
    chk("payloads_slug_boundary",
        override_payloads("<!-- override: drafted-copy-extra x -->", "drafted-copy") == [])
    chk("payloads_empty", override_payloads("<!-- override: drafted-copy-->", "drafted-copy") == [""])
    chk("payloads_multi",
        override_payloads("<!-- override: regression-cleared a --> b <!-- override: regression-cleared c -->",
                          "regression-cleared") == [" a ", " c "])

    print("Self-test: PASS" if rc == 0 else "Self-test: FAIL")
    return rc


if __name__ == "__main__":
    import sys
    if "--self-test" in sys.argv:
        sys.exit(_self_test())
    # Delegation entry points for the bash gates (body read from stdin) so the bash path uses THIS one
    # robust stripper instead of a parallel awk/sed reimplementation:
    #   --has-override <slug>     -> exit 0 if a live override for <slug> exists in stdin, else 1
    #   --override-slugs <prefix> -> print each live <slug> following <prefix> in stdin (one per line)
    if "--has-override" in sys.argv:
        _i = sys.argv.index("--has-override")
        _slug = sys.argv[_i + 1] if _i + 1 < len(sys.argv) else ""
        sys.exit(0 if has_override(sys.stdin.read(), _slug) else 1)
    if "--override-slugs" in sys.argv:
        _i = sys.argv.index("--override-slugs")
        _prefix = sys.argv[_i + 1] if _i + 1 < len(sys.argv) else ""
        sys.stdout.write("\n".join(sorted(override_slugs(sys.stdin.read(), _prefix))))
        sys.exit(0)
    sys.exit(0)
