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

# Code spans — a fenced ```...``` block (DOTALL) OR an inline `...` span. A marker quoted inside one
# is a documentation EXAMPLE, not a live directive, so it is stripped before the override scan.
_CODE_SPAN_RE = re.compile(r"```.*?```|`[^`\n]*`", re.DOTALL)

# After `<!-- override: <slug>` the slug must end at a real delimiter — whitespace, an em-/en-dash
# (the `— <rationale>` form), a hyphen-minus reason separator, the comment close `-->`, or EOL — so a
# SUFFIXED slug (`<slug>-extra`) does NOT satisfy a request for `<slug>`.
_BOUNDARY = r"(?=\s|—|–|-->|$)"


def strip_code_spans(body):
    """`body` with fenced and inline code spans blanked (replaced by a space)."""
    return _CODE_SPAN_RE.sub(" ", body or "")


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
    (`[a-z0-9][a-z0-9-]*`), matching the legacy `re.findall` shape but on stripped prose."""
    region = strip_code_spans(body)
    pat = re.compile(r"<!--\s*override:\s*" + re.escape(prefix) + r"([a-z0-9][a-z0-9-]*)")
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
    # bypass 2 — code-span decoys (inline + fenced) are rejected
    chk("inline_codespan_rejected", not has_override("Use `<!-- override: my-slug -->` to skip.", S))
    chk("fenced_block_rejected",
        not has_override("before\n```\n<!-- override: my-slug -->\n```\nafter", S))
    # a genuinely-absent slug is not found
    chk("absent_slug", not has_override("<!-- override: other-slug -->", S))
    # override_slugs: data-driven extraction, code spans stripped
    chk("slugs_extract", override_slugs("<!-- override: ap-foo --> <!-- override: ap-bar -->", "ap-")
        == {"foo", "bar"})
    chk("slugs_skip_codespan",
        override_slugs("`<!-- override: ap-decoy -->` <!-- override: ap-real -->", "ap-") == {"real"})

    print("Self-test: PASS" if rc == 0 else "Self-test: FAIL")
    return rc


if __name__ == "__main__":
    import sys
    sys.exit(_self_test() if "--self-test" in sys.argv else 0)
