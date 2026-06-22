#!/usr/bin/env python3
"""editor-scaffolding — Editor Scaffolding operator-mode presentation contract (Operators).

`validate.sh editor-scaffolding <editorial_letter|run_folder> [--strict]` shells out here.
Editor Scaffolding (`operator:editor`) re-aims the Core DE editorial letter at a human
developmental editor using APODICTIC as analytical assist: an Editor Brief addressee, a
"What You Might Have Missed" blind-spot section, and an "Intervention Menu" that hands the
prescription to the human editor. The mode is a SUPERSET overlay on the standard letter, so
the standard gates (decision-layer-check, severity-floor, softness-check) still apply; this
validator owns only the operator-mode presentation contract no other validator raises.

CONDITIONAL ENFORCEMENT: the contract is enforced only when the letter DECLARES the mode
(`<!-- mode: editor-scaffolding -->`). A letter without the marker is an ordinary
author-facing letter — reported as a no-op and exit 0 — so this is safe to run over every
letter (e.g. in a batch gate) without false positives on author-facing runs.

Checks (see docs/editor-scaffolding.md):
  E1  mode marker present AND a non-empty `## Editor Brief` (addressee = editor)
  E2  non-empty `## What You Might Have Missed` blind-spot section
  E3  an `## Intervention Menu` heading (prescription deferred to the editor)
      override: <!-- override: scaffolding-checklist — <rationale> -->
  E4  >= 1 canonical severity token (Must-Fix/Should-Fix/Could-Fix) survives in the body
  W1  author-directed second-person prescriptive imperatives in the body (advisory; ERROR
      under --strict) — `you (should|must|need to|...) (rewrite|add|cut|...)`
      override: <!-- override: scaffolding-prescription — <rationale> -->

  editor_scaffolding.py editor-scaffolding <editorial_letter|run_folder> [--strict]
  editor_scaffolding.py --self-test

Exit: 0 clean / WARN-only / not-in-mode, 1 on ERROR (or WARN under --strict), 2 usage.
"""
import glob
import os
import re
import sys

from override_marker import has_override

MODE_MARKER_RE = re.compile(r"<!--\s*mode:\s*editor-scaffolding\s*-->", re.IGNORECASE)
SEVERITY_RE = re.compile(r"(?<![\w-])(Must-Fix|Should-Fix|Could-Fix)(?![\w-])")
_LEVEL2_RE = re.compile(r"^##\s")
_HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
_LETTER_GLOB = ("*_Editorial_Letter_*.md", "*_Synthesis_*.md")

# E1/E2/E3 required headings (substring of a level-1..4 heading, case-insensitive).
_EDITOR_BRIEF_PAT = "Editor Brief"
_BLIND_SPOT_PAT = "What You Might Have Missed"
_INTERVENTION_PAT = "Intervention Menu"

# W1: author-directed second-person prescription. "you" addresses someone; in scaffolding the
# reader is the editor, so a directive to *rewrite/cut/add* manuscript content (something neither
# the editor nor the framework does — the author does) is out of register. The modal must be
# immediately followed by a manuscript-mutation verb, so "you should suggest the author ..." and
# "you should flag ..." do NOT match (suggest/flag are editor acts, not in the verb set).
_PRESCRIPTION_RE = re.compile(
    r"\byou\s+(?:should|must|need to|have to|ought to)\s+"
    r"(?:rewrite|revise|add|cut|delete|remove|expand|trim|reorder|restructure|insert)\b",
    re.IGNORECASE)
# W1 also catches a BARE imperative mutation directive at a line / list-item start ("Add a scene
# where ...", "Cut the prologue", "Rewrite the climax") — author-facing revision-checklist phrasing
# the modal form above misses. Anchored to a line start (after an optional list marker / emphasis)
# so it can't fire on a random mid-sentence substring. The Keep/Cut/Unsure Author-Decisions labels
# and intervention CLASSES (Restore / Redistribute / Compress / Source ...) are deliberately NOT in
# the verb set — only direct manuscript-mutation verbs that read as an author-facing checklist item.
_BARE_PRESCRIPTION_RE = re.compile(
    r"^[ \t>]*(?:[-*+]|\d+[.)])?[ \t]*(?:\*\*|\*|_|`)?[ \t]*"
    r"(?:rewrite|revise|add|cut|delete|remove|expand|trim|reorder|restructure|insert)\b",
    re.IGNORECASE | re.MULTILINE)


def _read(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except (OSError, UnicodeDecodeError):
        return None


def _lines(text):
    out = text.split("\n")
    if out and out[-1] == "":
        out = out[:-1]
    return out


# `has_override` is imported from the shared `override_marker` module (boundary-matched + code-spans
# stripped, identical to every letter-family gate). The legacy local bare-substring definition — which
# honored a suffixed slug and a backtick'd documentation example — is retired (meta_lint.py M5 gates it).


def _body(text):
    """Synthesis body = everything before the first 'Appendix A' heading (same boundary
    softness-check uses). Prose scans run over the body only, so appendix evidence and the
    Severity Calibration block don't trip the W1 lexicon."""
    lines = _lines(text)
    for i, ln in enumerate(lines):
        if re.search(r"^#{1,4}\s+.*Appendix\s+A\b", ln, re.IGNORECASE):
            return "\n".join(lines[:i])
    return "\n".join(lines)


def _strip_comments(text):
    return _HTML_COMMENT_RE.sub(" ", text)


def _has_heading(lines, pat):
    rx = re.compile(r"^#{1,4}\s+.*" + re.escape(pat), re.IGNORECASE)
    return any(rx.search(ln) for ln in lines)


def _section_nonempty(lines, pat):
    """True iff a heading matching `pat` exists and has >= 1 non-blank, non-comment content
    line before the next level-2 heading."""
    rx = re.compile(r"^#{1,4}\s+.*" + re.escape(pat), re.IGNORECASE)
    start = next((i for i, ln in enumerate(lines) if rx.search(ln)), None)
    if start is None:
        return None  # absent
    for j in range(start + 1, len(lines)):
        if _LEVEL2_RE.match(lines[j]):
            break
        stripped = _HTML_COMMENT_RE.sub("", lines[j]).strip()
        if stripped:
            return True
    return False  # present but empty


def check(letter_text, strict=False):
    """Return (exit_code, report_lines)."""
    lines = _lines(letter_text)
    out = []

    if not MODE_MARKER_RE.search(letter_text):
        out.append("editor-scaffolding: not in editor-scaffolding mode "
                   "(no <!-- mode: editor-scaffolding --> marker) — nothing to enforce.")
        return 0, out

    out.append("editor-scaffolding: mode declared — enforcing the operator:editor contract.")
    body = _body(letter_text)
    # The scaffold sections (E1/E2/E3) are BODY-level by contract — discover them in the body
    # only, so a section under Appendix A/C can't satisfy a required body section.
    body_lines = _lines(body)
    errors, warns = [], []

    # E1 — mode marker (already true) + a non-empty Editor Brief addressee section.
    brief = _section_nonempty(body_lines, _EDITOR_BRIEF_PAT)
    if brief is None:
        errors.append("E1: missing the '%s' section (the editor addressee). The marker is "
                      "present but the letter still opens to the author." % _EDITOR_BRIEF_PAT)
    elif brief is False:
        errors.append("E1: '%s' section is present but empty." % _EDITOR_BRIEF_PAT)
    else:
        out.append("  E1 mode+addressee: OK")

    # E2 — non-empty blind-spot section.
    blind = _section_nonempty(body_lines, _BLIND_SPOT_PAT)
    if blind is None:
        errors.append("E2: missing the '%s' blind-spot section (the scaffolding value-add)."
                      % _BLIND_SPOT_PAT)
    elif blind is False:
        errors.append("E2: '%s' section is present but empty." % _BLIND_SPOT_PAT)
    else:
        out.append("  E2 blind-spot: OK")

    # E3 — Intervention Menu (prescription deferred), or an explicit override.
    if _has_heading(body_lines, _INTERVENTION_PAT):
        out.append("  E3 prescription-deferral: OK")
    elif has_override(body, "scaffolding-checklist"):
        warns.append("E3: no '%s' heading, but an override marker is present "
                     "(author-facing checklist kept deliberately)." % _INTERVENTION_PAT)
    else:
        errors.append("E3: missing the '%s' heading. Scaffolding reframes the revision "
                      "guidance as editor-discretion option-classes; the human editor owns "
                      "the author-facing prescription. Override: "
                      "<!-- override: scaffolding-checklist — <rationale> -->."
                      % _INTERVENTION_PAT)

    # E4 — severity vocabulary survives the reframe.
    if SEVERITY_RE.search(body):
        out.append("  E4 severity-preserved: OK")
    else:
        errors.append("E4: no canonical severity token (Must-Fix/Should-Fix/Could-Fix) in the "
                      "body. Scaffolding reframes the addressee, it does not strip severity.")

    # W1 — author-directed prescription leak (advisory; ERROR under --strict). Two forms: the
    # modal second-person ("you should rewrite ...") and a bare line-start imperative ("Add a
    # scene where ...", "Cut the prologue").
    body_prose = _strip_comments(body)
    m = _PRESCRIPTION_RE.search(body_prose) or _BARE_PRESCRIPTION_RE.search(body_prose)
    if m and not has_override(body, "scaffolding-prescription"):
        ls = body_prose.rfind("\n", 0, m.start()) + 1
        le = body_prose.find("\n", m.start())
        snippet = body_prose[ls:(le if le != -1 else len(body_prose))].strip()
        if len(snippet) > 80:
            snippet = snippet[:77] + "..."
        warns.append("W1: author-directed prescription leak — '%s' in the body. In scaffolding "
                     "mode the prescription belongs to the human editor. Override: "
                     "<!-- override: scaffolding-prescription — <rationale> -->." % snippet)

    for e in errors:
        out.append("  ERROR: " + e)
    for w in warns:
        out.append("  %s: %s" % ("ERROR (--strict)" if strict else "WARN", w))

    if errors or (strict and warns):
        out.append("FAILED: editor-scaffolding contract not satisfied. See docs/editor-scaffolding.md.")
        return 1, out
    out.append("OK: editor-scaffolding contract satisfied.")
    return 0, out


def _newest(paths):
    paths = [p for p in paths if p and os.path.isfile(p)]
    return max(paths, key=os.path.getmtime) if paths else None


def run(paths, strict=False):
    letter = None
    if len(paths) == 1 and os.path.isdir(paths[0]):
        for pat in _LETTER_GLOB:
            letter = _newest(glob.glob(os.path.join(paths[0], pat)))
            if letter:
                break
    else:
        letter = paths[0] if paths else None
    if letter is None:
        return 2, ["editor-scaffolding: need an editorial letter file or a run folder "
                   "containing an *_Editorial_Letter_*.md / *_Synthesis_*.md"]
    text = _read(letter)
    if text is None:
        return 2, ["editor-scaffolding: cannot read %s" % letter]
    return check(text, strict=strict)


# ---------------------------------------------------------------- self-test

def run_self_test():
    rc = {"v": 0}

    def chk(name, cond):
        print("  %s: %s" % (name, "OK" if cond else "FAIL"))
        if not cond:
            rc["v"] = 1

    marker = "<!-- mode: editor-scaffolding -->"

    def letter(brief=True, blind=True, menu=True, severity=True, prescription=False, bare=False,
               brief_empty=False, blind_empty=False, mode=True,
               menu_override=False, presc_override=False, sections_in_appendix=False):
        s = ["# Development Edit: Test\n"]
        if mode:
            s.append(marker + "\n")
        if menu_override:
            s.append("<!-- override: scaffolding-checklist — short fiction; kept author checklist -->\n")
        if presc_override:
            s.append("<!-- override: scaffolding-prescription — quoting the author's own note -->\n")
        if brief:
            s.append("## Editor Brief\n")
            s.append("" if brief_empty else "Where your read and mine most diverge: the middle third.\n")
        if severity:
            s.append("## What Needs Work\n- **Must-Fix:** Pacing collapse (Ch. 7, lines 142-160).\n")
        if blind:
            s.append("## What You Might Have Missed\n")
            s.append("" if blind_empty else "The prose polish in Part I masks a missing causal link (Ch. 3).\n")
        if menu:
            s.append("## Intervention Menu — editor's discretion\n- Option: compress the aftermath beats.\n")
        if bare:  # author-facing checklist leak — bare imperative at a list start, in the body
            s.append("- Add a scene where the consequence lands.\n")
        if prescription:  # modal second-person leak, in the body
            s.append("\nYou should rewrite the climax to raise the stakes.\n")
        s.append("## Appendix A — Diagnostic Detail\n")
        # Appendix prose carries both leak forms AND a scaffold heading; the body scan stops at
        # Appendix A, so none of this should satisfy a body section or trip W1.
        s.append("You should add a scene here, then cut the prologue (appendix prose, not scanned).\n")
        if sections_in_appendix:
            s.append("### What You Might Have Missed\nblind-spot text smuggled into the appendix.\n")
        return "".join(s)

    # No marker -> no-op pass.
    code, lines = check(letter(mode=False))
    chk("no_marker_is_noop", code == 0 and any("not in editor-scaffolding mode" in l for l in lines))

    # Full, clean scaffolded letter -> pass.
    code, lines = check(letter())
    chk("clean_scaffolded_passes",
        code == 0 and any("contract satisfied" in l for l in lines)
        and any("E1 mode+addressee: OK" in l for l in lines)
        and any("E2 blind-spot: OK" in l for l in lines)
        and any("E3 prescription-deferral: OK" in l for l in lines)
        and any("E4 severity-preserved: OK" in l for l in lines))

    # E1: missing Editor Brief.
    code, lines = check(letter(brief=False))
    chk("e1_missing_brief", code == 1 and any("E1: missing" in l for l in lines))
    # E1: empty Editor Brief.
    code, lines = check(letter(brief_empty=True))
    chk("e1_empty_brief", code == 1 and any("E1:" in l and "empty" in l for l in lines))

    # E2: missing / empty blind-spot.
    code, lines = check(letter(blind=False))
    chk("e2_missing_blind", code == 1 and any("E2: missing" in l for l in lines))
    code, lines = check(letter(blind_empty=True))
    chk("e2_empty_blind", code == 1 and any("E2:" in l and "empty" in l for l in lines))

    # E3: missing Intervention Menu -> ERROR; with override -> WARN (pass).
    code, lines = check(letter(menu=False))
    chk("e3_missing_menu", code == 1 and any("E3: missing" in l for l in lines))
    code, lines = check(letter(menu=False, menu_override=True))
    chk("e3_override_warns_not_errors",
        code == 0 and any("override marker is present" in l for l in lines))
    # 2026-06-20 override-substring hardening (shared override_marker.has_override): a CODE-SPAN decoy
    # and a SUFFIX-COLLISION slug must NOT silence E3 -> still ERROR.
    e3_decoy = letter(menu=False).replace(
        "# Development Edit: Test\n",
        "# Development Edit: Test\nUse `<!-- override: scaffolding-checklist -->` to keep the author checklist.\n")
    code, lines = check(e3_decoy)
    chk("e3_override_codespan_decoy_errors", code == 1 and any("E3: missing" in l for l in lines))
    e3_suffix = letter(menu=False).replace(
        "# Development Edit: Test\n",
        "# Development Edit: Test\n<!-- override: scaffolding-checklist-not-really — decoy. -->\n")
    code, lines = check(e3_suffix)
    chk("e3_override_suffix_collision_errors", code == 1 and any("E3: missing" in l for l in lines))

    # E4: severity stripped.
    code, lines = check(letter(severity=False))
    chk("e4_severity_stripped", code == 1 and any("E4: no canonical severity" in l for l in lines))

    # W1: author-directed prescription in body -> WARN by default, ERROR under --strict.
    code, lines = check(letter(prescription=True))
    chk("w1_advisory_warn", code == 0 and any("WARN: W1" in l for l in lines))
    code_s, lines_s = check(letter(prescription=True), strict=True)
    chk("w1_strict_errors", code_s == 1 and any("ERROR (--strict): W1" in l for l in lines_s))
    # W1 override silences it.
    code, lines = check(letter(prescription=True, presc_override=True))
    chk("w1_override_silences", code == 0 and not any("W1" in l for l in lines))
    # W1 must NOT fire on appendix prose ("you should add a scene" lives in Appendix A).
    code, lines = check(letter(prescription=False))
    chk("w1_ignores_appendix", code == 0 and not any("W1" in l for l in lines))
    # W1 must NOT fire on an editor act ("you should flag ... to the author").
    edl = letter().replace("Where your read and mine most diverge: the middle third.",
                           "You should flag the pacing to the author and suggest options.")
    code, lines = check(edl)
    chk("w1_ignores_editor_acts", code == 0 and not any("W1" in l for l in lines))

    # W1 BARE imperative leak (PR #34 review P2): "Add a scene where ..." at a list start in the
    # body — the modal form misses it, but the bare-imperative pattern catches it.
    code, lines = check(letter(bare=True))
    chk("w1_bare_imperative_warn",
        code == 0 and any("WARN: W1" in l for l in lines)
        and any("Add a scene" in l for l in lines))
    code_s, _ls = check(letter(bare=True), strict=True)
    chk("w1_bare_imperative_strict_errors", code_s == 1)
    # "Cut the prologue ..." at a list start also leaks.
    code, lines = check(letter().replace("- Option: compress the aftermath beats.",
                                         "- Cut the prologue."))
    chk("w1_bare_cut_flagged", any("WARN: W1" in l for l in lines))
    # Bare imperative confined to the appendix must NOT fire (body scan stops at Appendix A).
    code, lines = check(letter(bare=False))
    chk("w1_bare_ignores_appendix", code == 0 and not any("W1" in l for l in lines))
    # Intervention CLASSES and Keep/Unsure decision labels are not in the verb set -> no leak.
    code, lines = check(letter().replace(
        "- Option: compress the aftermath beats.",
        "- Restore the causal beat on-page.\n- Redistribute the aftermath across the span."))
    chk("w1_intervention_classes_clean", code == 0 and not any("W1" in l for l in lines))

    # Fix B (PR #34 review P2): a required body section satisfied only from an appendix must FAIL.
    # blind-spot present only as '### What You Might Have Missed' under '## Appendix A'.
    code, lines = check(letter(blind=False, sections_in_appendix=True))
    chk("e2_appendix_section_does_not_satisfy",
        code == 1 and any("E2: missing" in l for l in lines))
    code_s, _ls = check(letter(blind=False, sections_in_appendix=True), strict=True)
    chk("e2_appendix_section_strict_fails", code_s == 1)

    print("Self-test: PASS" if rc["v"] == 0 else "Self-test: FAIL")
    return rc["v"]


def main(argv):
    if "--self-test" in argv:
        return run_self_test()
    args = [a for a in argv[1:] if a != "editor-scaffolding"]
    strict = "--strict" in args
    paths = [a for a in args if not a.startswith("--")]
    if not paths:
        print("Usage: editor_scaffolding.py editor-scaffolding <editorial_letter|run_folder> "
              "[--strict] | --self-test")
        return 2
    code, lines = run(paths, strict=strict)
    for ln in lines:
        print(ln)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
