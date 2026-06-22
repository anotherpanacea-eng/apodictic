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
_FENCE_OPEN_RE = re.compile(r"^[ \t]*(`{3,}|~{3,})")
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
        m = _FENCE_OPEN_RE.match(line)
        run = m.group(1) if m else ""
        if fence is None:
            if run:
                fence = (run[0], len(run))
                out.append("")             # drop the opening fence line
            else:
                out.append(line)
        else:
            if run and run[0] == fence[0] and len(run) >= fence[1]:
                fence = None               # a matching-character, long-enough closer
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
