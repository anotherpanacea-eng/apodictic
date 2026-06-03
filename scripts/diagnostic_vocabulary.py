#!/usr/bin/env python3
"""diagnostic-vocabulary — Diagnostic Vocabulary Mode teaching-aid contract (Operators).

`validate.sh diagnostic-vocabulary <vocab_guide|run_folder> [--strict]` shells out here.
Diagnostic Vocabulary Mode (`operator:facilitator`) produces a Vocabulary Guide for a
writing-group facilitator: a Glossary of the structural concepts the diagnosis used —
defined in plain language and GROUNDED in this manuscript — plus Discussion Prompts that
turn findings into questions for the group. It is the sibling of editor-scaffolding
(`operator:editor`); see docs/diagnostic-vocabulary.md. This validator owns the teaching-aid
contract no other validator raises; it does NOT carry severity (the editorial letter does).

CONDITIONAL ENFORCEMENT: the contract is enforced only when the artifact DECLARES the mode
(`<!-- mode: diagnostic-vocabulary -->`). Without it the validator reports a no-op and exits 0,
so it is safe to run over any file. All section checks are BODY-scoped (before a first
'Appendix A' heading, if any), so an appendix can't satisfy a required section.

Checks (see docs/diagnostic-vocabulary.md):
  V1  mode marker + a non-empty `## Glossary` section with >= 3 entries
  V2  every Glossary entry is `term <— / – / :> definition` shaped (term + real definition)
  V3  >= 3 Glossary entries carry a manuscript anchor (Ch./scene/line/§ ref) — grounding
      override: <!-- override: vocabulary-grounding — <rationale> -->
  V4  a `## Discussion Prompts` section with >= 3 prompts, ALL phrased as questions (end '?')
  W1  author-directed prescription in the body — modal ("you should rewrite") or a bare
      line-start imperative ("Add a scene…", "Cut the prologue"); advisory, ERROR under --strict
      override: <!-- override: vocabulary-prescription — <rationale> -->

  diagnostic_vocabulary.py diagnostic-vocabulary <vocab_guide|run_folder> [--strict]
  diagnostic_vocabulary.py --self-test

Exit: 0 clean / WARN-only / not-in-mode, 1 on ERROR (or WARN under --strict), 2 usage.
"""
import glob
import os
import re
import sys

MODE_MARKER_RE = re.compile(r"<!--\s*mode:\s*diagnostic-vocabulary\s*-->", re.IGNORECASE)
_LEVEL2_RE = re.compile(r"^##\s")
_HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
_LETTER_GLOB = ("*_Vocabulary_Guide_*.md",)

_GLOSSARY_PAT = "Glossary"
_PROMPTS_PAT = "Discussion Prompts"

# A glossary entry list item: a leading list marker, a term, a separator (em/en dash or colon),
# then the definition. Plain "-" is NOT a separator (it collides with the list marker), so a real
# em/en dash or a colon is required between term and definition.
_GLOSSARY_ENTRY_RE = re.compile(r"^\s*[-*+]\s+(?P<term>.+?)\s*[—–:]\s*(?P<defn>\S.*)$")
# A manuscript anchor (grounding) — shared shape with letter_checks._REF_RE.
_REF_RE = re.compile(
    r"(Chapter\s+[0-9]+|Ch\.\s*[0-9]+|Scene\s+[0-9]+|lines?\s+[0-9]+|L[0-9]+|"
    r"page\s+[0-9]+|p\.\s*[0-9]+|§\s*[A-Za-z0-9.\-]+|[A-Z]{2,5}-[0-9]+)", re.IGNORECASE)
_LIST_ITEM_RE = re.compile(r"^\s*(?:[-*+]|[0-9]+[.)])\s+(?P<text>\S.*)$")

# W1 — author-directed prescription, the two forms editor-scaffolding established. Modal
# second-person, and a bare imperative anchored at a line / list start (so it can't fire on a
# mid-sentence substring). Verb set is direct manuscript-mutation verbs only.
_PRESCRIPTION_RE = re.compile(
    r"\byou\s+(?:should|must|need to|have to|ought to)\s+"
    r"(?:rewrite|revise|add|cut|delete|remove|expand|trim|reorder|restructure|insert)\b",
    re.IGNORECASE)
_BARE_PRESCRIPTION_RE = re.compile(
    r"^[ \t>]*(?:[-*+]|\d+[.)])?[ \t]*(?:\*\*|\*|_|`)?[ \t]*"
    r"(?:rewrite|revise|add|cut|delete|remove|expand|trim|reorder|restructure|insert)\b",
    re.IGNORECASE | re.MULTILINE)


def _read(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return None


def _lines(text):
    out = text.split("\n")
    if out and out[-1] == "":
        out = out[:-1]
    return out


def has_override(body, slug):
    """Plain-substring override detection, matching the shared codebase convention
    (letter_checks.has_override / honesty_check.SOFT_MARKER)."""
    return ("<!-- override: %s" % slug) in body


def _body(text):
    """Everything before the first 'Appendix A' heading (the boundary softness-check uses).
    A Vocabulary Guide normally has no appendices, in which case the body is the whole doc."""
    lines = _lines(text)
    for i, ln in enumerate(lines):
        if re.search(r"^#{1,4}\s+.*Appendix\s+A\b", ln, re.IGNORECASE):
            return "\n".join(lines[:i])
    return "\n".join(lines)


def _strip_comments(text):
    return _HTML_COMMENT_RE.sub(" ", text)


def _section(lines, pat):
    """Lines under the first heading matching `pat`, up to the next level-2 heading; None if
    the heading is absent."""
    rx = re.compile(r"^#{1,4}\s+.*" + re.escape(pat), re.IGNORECASE)
    start = next((i for i, ln in enumerate(lines) if rx.search(ln)), None)
    if start is None:
        return None
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if _LEVEL2_RE.match(lines[j]):
            end = j
            break
    return lines[start + 1:end]


def _entry_blocks(section):
    """Group a section's lines into list-item blocks: each block is a list-item line plus its
    following non-list, non-blank, non-heading continuation lines. So a definition, a manuscript
    anchor, or a trailing '?' on a wrapped continuation line still belongs to its entry/prompt."""
    blocks, cur = [], None
    for ln in section:
        if _LIST_ITEM_RE.match(ln):
            if cur is not None:
                blocks.append(cur)
            cur = [ln]
        elif cur is not None:
            if ln.strip() == "" or ln.lstrip().startswith("#"):
                blocks.append(cur)
                cur = None
            else:
                cur.append(ln)
    if cur is not None:
        blocks.append(cur)
    return blocks


def check(guide_text, strict=False):
    """Return (exit_code, report_lines)."""
    out = []
    if not MODE_MARKER_RE.search(guide_text):
        out.append("diagnostic-vocabulary: not in diagnostic-vocabulary mode "
                   "(no <!-- mode: diagnostic-vocabulary --> marker) — nothing to enforce.")
        return 0, out

    out.append("diagnostic-vocabulary: mode declared — enforcing the operator:facilitator contract.")
    body = _body(guide_text)
    body_lines = _lines(body)
    errors, warns = [], []

    # ---- Glossary (V1/V2/V3)
    gloss = _section(body_lines, _GLOSSARY_PAT)
    if gloss is None:
        errors.append("V1: missing the '%s' section in the body." % _GLOSSARY_PAT)
    else:
        blocks = _entry_blocks(gloss)
        entries = [b for b in blocks if _GLOSSARY_ENTRY_RE.match(b[0])]
        bare_items = [b[0] for b in blocks if not _GLOSSARY_ENTRY_RE.match(b[0])]
        if len(entries) < 3:
            errors.append("V1: Glossary has %d well-formed entr%s (need >= 3 'term — definition' "
                          "entries)." % (len(entries), "y" if len(entries) == 1 else "ies"))
        else:
            out.append("  V1 glossary present (%d entries): OK" % len(entries))
        # V2 — no list item that looks like an entry but lacks a definition.
        if bare_items:
            errors.append("V2: %d Glossary list item(s) have no 'term — definition' separator "
                          "(a bare term with no definition): e.g. %r"
                          % (len(bare_items), bare_items[0].strip()[:60]))
        elif entries:
            out.append("  V2 entries defined: OK")
        # V3 — grounding: >= 3 entries cite a manuscript anchor (anywhere in the entry block).
        grounded = sum(1 for b in entries if _REF_RE.search(" ".join(b)))
        if grounded < 3 and not has_override(body, "vocabulary-grounding"):
            errors.append("V3: only %d Glossary entr%s grounded in the manuscript (need >= 3 with "
                          "a chapter/scene/line/§ anchor). The teaching value is grounding the "
                          "term in THIS text. Override: "
                          "<!-- override: vocabulary-grounding — <rationale> -->."
                          % (grounded, "y is" if grounded == 1 else "ies are"))
        elif grounded < 3:
            warns.append("V3: only %d grounded Glossary entr%s (override marker present)."
                         % (grounded, "y" if grounded == 1 else "ies"))
        else:
            out.append("  V3 grounding (%d grounded entries): OK" % grounded)

    # ---- Discussion Prompts (V4)
    prompts_sec = _section(body_lines, _PROMPTS_PAT)
    if prompts_sec is None:
        errors.append("V4: missing the '%s' section in the body." % _PROMPTS_PAT)
    else:
        # A prompt is a list-item block; its trailing '?' may sit on a wrapped continuation line,
        # so test the joined block, not just the list-item line.
        prompts = [" ".join(b).strip() for b in _entry_blocks(prompts_sec)]
        if len(prompts) < 3:
            errors.append("V4: %d discussion prompt(s) (need >= 3)." % len(prompts))
        else:
            non_q = [p for p in prompts if not p.rstrip().endswith("?")]
            if non_q:
                errors.append("V4: %d discussion prompt(s) are not phrased as questions "
                              "(must end with '?'): e.g. %r" % (len(non_q), non_q[0][:60]))
            else:
                out.append("  V4 prompts are questions (%d): OK" % len(prompts))

    # ---- W1 prescription leak (advisory; ERROR under --strict)
    body_prose = _strip_comments(body)
    m = _PRESCRIPTION_RE.search(body_prose) or _BARE_PRESCRIPTION_RE.search(body_prose)
    if m and not has_override(body, "vocabulary-prescription"):
        ls = body_prose.rfind("\n", 0, m.start()) + 1
        le = body_prose.find("\n", m.start())
        snippet = body_prose[ls:(le if le != -1 else len(body_prose))].strip()
        if len(snippet) > 80:
            snippet = snippet[:77] + "..."
        warns.append("W1: author-directed prescription leak — '%s' in the body. A facilitator "
                     "teaches and prompts; the group draws its own conclusions. Override: "
                     "<!-- override: vocabulary-prescription — <rationale> -->." % snippet)

    for e in errors:
        out.append("  ERROR: " + e)
    for w in warns:
        out.append("  %s: %s" % ("ERROR (--strict)" if strict else "WARN", w))

    if errors or (strict and warns):
        out.append("FAILED: diagnostic-vocabulary contract not satisfied. "
                   "See docs/diagnostic-vocabulary.md.")
        return 1, out
    out.append("OK: diagnostic-vocabulary contract satisfied.")
    return 0, out


def _newest(paths):
    paths = [p for p in paths if p and os.path.isfile(p)]
    return max(paths, key=os.path.getmtime) if paths else None


def run(paths, strict=False):
    guide = None
    if len(paths) == 1 and os.path.isdir(paths[0]):
        for pat in _LETTER_GLOB:
            guide = _newest(glob.glob(os.path.join(paths[0], pat)))
            if guide:
                break
    else:
        guide = paths[0] if paths else None
    if guide is None:
        return 2, ["diagnostic-vocabulary: need a Vocabulary Guide file or a run folder "
                   "containing a *_Vocabulary_Guide_*.md"]
    text = _read(guide)
    if text is None:
        return 2, ["diagnostic-vocabulary: cannot read %s" % guide]
    return check(text, strict=strict)


# ---------------------------------------------------------------- self-test

def run_self_test():
    rc = {"v": 0}

    def chk(name, cond):
        print("  %s: %s" % (name, "OK" if cond else "FAIL"))
        if not cond:
            rc["v"] = 1

    marker = "<!-- mode: diagnostic-vocabulary -->"

    def guide(mode=True, n_entries=4, n_grounded=4, defined=True, n_prompts=3,
              all_questions=True, prescription=False, bare=False,
              grounding_override=False, presc_override=False, prompts_section=True,
              glossary_in_appendix=False):
        s = ["# Vocabulary Guide: Test\n"]
        if mode:
            s.append(marker + "\n")
        if grounding_override:
            s.append("<!-- override: vocabulary-grounding — conceptual glossary by design -->\n")
        if presc_override:
            s.append("<!-- override: vocabulary-prescription — quoting a craft text -->\n")
        terms = ["Controlling idea", "Reveal economy", "Causal gap", "Character agency",
                 "Pacing", "POV discipline"]
        anchors = ["(Ch. 3)", "(Chapter 7, lines 142-160)", "(§Reader Knowledge)",
                   "(Scene 4)", "(L220)", "(Ch. 9)"]
        s.append("## Glossary\n")
        for i in range(n_entries):
            term = terms[i % len(terms)]
            anchor = (" — shows up here " + anchors[i % len(anchors)]) if i < n_grounded else ""
            if defined:
                s.append("- **%s** — the plain-language definition of the concept%s.\n"
                         % (term, anchor))
            else:  # bare term, no definition separator
                s.append("- **%s**\n" % term)
        if glossary_in_appendix:
            s.append("## Appendix A — Notes\n### Glossary\n- **Smuggled** — def (Ch. 2).\n")
        if prompts_section:
            s.append("## Discussion Prompts\n")
            for i in range(n_prompts):
                q = "?" if (all_questions or i < n_prompts - 1) else "."
                s.append("- Where does the controlling idea come into focus%s\n" % q)
        if prescription:
            s.append("\nYou should rewrite the climax to raise the stakes.\n")
        if bare:  # body prose (not a prompt list item) so this isolates W1, not V4
            s.append("\n## Facilitator Notes\nAdd a scene where the consequence lands.\n")
        return "".join(s)

    # No marker -> no-op.
    code, lines = check(guide(mode=False))
    chk("no_marker_is_noop", code == 0 and any("not in diagnostic-vocabulary mode" in l for l in lines))

    # Clean guide -> pass.
    code, lines = check(guide())
    chk("clean_passes", code == 0 and any("contract satisfied" in l for l in lines)
        and any("V1 glossary" in l for l in lines) and any("V2 entries defined" in l for l in lines)
        and any("V3 grounding" in l for l in lines) and any("V4 prompts" in l for l in lines))

    # V1: too few entries.
    code, lines = check(guide(n_entries=2, n_grounded=2))
    chk("v1_too_few_entries", code == 1 and any("V1: Glossary has 2" in l for l in lines))
    # V1: missing glossary entirely.
    code, lines = check(guide().replace("## Glossary", "## Words"))
    chk("v1_missing_glossary", code == 1 and any("V1: missing" in l for l in lines))

    # V2: a bare term with no definition.
    code, lines = check(guide(defined=False))
    chk("v2_bare_term", code == 1 and any("V2:" in l for l in lines))

    # V3: under-grounded -> ERROR; with override -> pass(WARN).
    code, lines = check(guide(n_grounded=1))
    chk("v3_undergrounded", code == 1 and any("V3: only 1" in l for l in lines))
    code, lines = check(guide(n_grounded=1, grounding_override=True))
    chk("v3_override", code == 0 and any("override marker present" in l for l in lines))

    # V4: missing section.
    code, lines = check(guide(prompts_section=False))
    chk("v4_missing_prompts", code == 1 and any("V4: missing" in l for l in lines))
    # V4: too few prompts.
    code, lines = check(guide(n_prompts=2))
    chk("v4_too_few", code == 1 and any("V4: 2 discussion" in l for l in lines))
    # V4: a prompt not phrased as a question.
    code, lines = check(guide(all_questions=False))
    chk("v4_not_question", code == 1 and any("not phrased as questions" in l for l in lines))
    # V4: a WRAPPED prompt with the '?' on a continuation line is still a valid question.
    wrapped = guide().replace(
        "- Where does the controlling idea come into focus?",
        "- Where does the controlling idea come into focus, and where does it\n"
        "  blur across the middle third?")
    code, lines = check(wrapped)
    chk("v4_wrapped_prompt_ok", code == 0 and any("V4 prompts are questions" in l for l in lines))

    # W1: modal + bare leaks (advisory; --strict ERROR); override silences.
    code, lines = check(guide(prescription=True))
    chk("w1_modal_warn", code == 0 and any("WARN: W1" in l for l in lines))
    code_s, _ls = check(guide(prescription=True), strict=True)
    chk("w1_strict_errors", code_s == 1 and any("ERROR (--strict): W1" in l for l in _ls))
    code, lines = check(guide(bare=True))
    chk("w1_bare_warn", code == 0 and any("WARN: W1" in l for l in lines)
        and any("Add a scene" in l for l in lines))
    code, lines = check(guide(prescription=True, presc_override=True))
    chk("w1_override_silences", code == 0 and not any("W1" in l for l in lines))

    # Body scope: a Glossary only under Appendix A must NOT satisfy V1.
    code, lines = check(guide().replace("## Glossary", "## Words", 1).replace(
        "## Words", "## Glossary", 0))  # no-op guard
    code, lines = check(guide(glossary_in_appendix=True).replace("## Glossary\n- **Controlling",
                                                                 "## Words\n- **Controlling", 1))
    chk("body_scope_glossary_in_appendix",
        code == 1 and any("V1: missing" in l for l in lines))

    print("Self-test: PASS" if rc["v"] == 0 else "Self-test: FAIL")
    return rc["v"]


def main(argv):
    if "--self-test" in argv:
        return run_self_test()
    args = [a for a in argv[1:] if a != "diagnostic-vocabulary"]
    strict = "--strict" in args
    paths = [a for a in args if not a.startswith("--")]
    if not paths:
        print("Usage: diagnostic_vocabulary.py diagnostic-vocabulary "
              "<vocab_guide|run_folder> [--strict] | --self-test")
        return 2
    code, lines = run(paths, strict=strict)
    for ln in lines:
        print(ln)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
