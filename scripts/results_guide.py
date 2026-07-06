#!/usr/bin/env python3
"""results-guide — Results Guide navigation-index integrity (Writer-Question Surface Hardening #5).

`validate.sh results-guide <run_folder> [--strict]` (or explicit files) shells out here.

The Results Guide (`[Project]_Results_Guide_[runlabel].md`, SKILL.md §Results Guide Artifact) is
the first file after the editorial letter — a plain-language MAP from each writer question the run
produced to the run-folder artifacts behind it. It is a *navigation index*, not a second letter:
it points, it never diagnoses. This validator owns its structural integrity in ONE arm — three
checks, R2 load-bearing:

  R1 membership   every `### <question>` heading matches one of §3's canonical User Questions
                  (`pass-dependencies.md §3`, the SSoT for the 8 macro blocks). An UNKNOWN question
                  is the defect (an invented block); a run that produced only some blocks is legal
                  (the Guide lists only what ran — absence is fine, invention is not). Cheap.
  R2 referential  (LOAD-BEARING) every cited run-folder filename resolves to a file IN the run
                  folder. A backtick token is a CITATION only if it ends in .md/.json (the guide's
                  "What to do next" section carries `/coach` / `/audit [name]` command tokens that
                  are NOT files — the extension guard excludes them so they never false-fail R2).
                  A citation still carrying an un-substituted `[...]` placeholder is a defect (the
                  template was copied but not filled). A dangling citation (no such file) is the
                  finding-trace E1 analogue — the guide points at a file that isn't there. Citations
                  must also stay INSIDE the run folder: an absolute path or a traversal/subdir path
                  (`../outside.md`, `/etc/x`) FAILS — it could otherwise resolve to a file outside
                  the folder and falsely PASS (the run folder is flat; citations are bare filenames).
  R3 hygiene      the guide must not leak editorial severity (`Must/Should/Could-Fix`) or masquerade
                  as a second letter (no `apodictic:finding` block). It indexes, never diagnoses.
                  (Rides along, cheap; the same posture content_advisory's A3 enforces.)

Each dimension degrades cleanly: a missing/unparseable §3 reference doc skips R1 (environment skip,
never a false FAIL); an unreadable run folder fails closed with a named error (finding-trace E0
shape). The Guide is a Synthesis-tier deliverable, NOT a Core DE pass artifact, so it carries no
`> **Macro block:**` header and no JSON schema (pass-header / artifacts-schema do not apply).

  results_guide.py results-guide <run_folder> [--strict]
  results_guide.py results-guide <guide.md> [<run_folder_dir>] [--strict]
  results_guide.py --self-test

Exit: 0 clean / WARN-only, 1 ERROR (or WARN under --strict), 2 usage.
"""
import glob
import os
import re
import sys

from severity_vocab import SEVERITY_TOKEN_RE  # SSoT: the editorial Must/Should/Could-Fix leak token

try:
    import apodictic_artifacts as art
except ImportError:
    art = None

# Guide filename glob (SKILL.md naming: `[Project]_Results_Guide_[runlabel].md`).
_GUIDE_GLOB = "*_Results_Guide_*.md"
# A3-style editorial-severity leak guard — the shared severity_vocab SSoT (M8). The guide is a
# navigation index, not a defect list: a Must/Should/Could-Fix token means it started diagnosing.
_SEVERITY_RE = SEVERITY_TOKEN_RE
# A backtick token is a run-folder CITATION only when it ends in a run-artifact extension (.md/.json).
# This EXTENSION GUARD is deliberate: the "What to do next" section legitimately carries command
# tokens in backticks — `/coach`, `/audit [name]` — which are NOT files and must not be traced as
# citations. Anchoring on the .md/.json suffix is the mechanical line between "cites an artifact" and
# "names a command"; a command token has no such suffix, so it is silently ignored (never an R2 fail).
_CITED_RE = re.compile(r"`([^`]+\.(?:md|json))`")
# An UN-SUBSTITUTED template placeholder — a backtick token carrying `[...]` and NAMING a file
# ("filename" / "artifact" / a .md/.json extension inside it). The template's citation slots read
# `[pass artifact filename]` (no resolved extension), so the extension-guarded _CITED_RE alone would
# SILENTLY PASS an unfilled template. This catches that class explicitly WITHOUT snaring a legitimate
# command token like `/audit [name]`: the `[...]` token must also mention file/artifact/filename or a
# run-artifact extension — a bare `[name]` in a command line does not qualify.
_PLACEHOLDER_RE = re.compile(
    r"`([^`]*\[[^`]*\][^`]*)`")
_PLACEHOLDER_FILE_HINT_RE = re.compile(
    r"filename|artifact|\.(?:md|json)\b", re.IGNORECASE)
# A `### <question>` section heading (the per-question index rows). Level-3 exactly (## groups, #### would
# be sub-detail); the heading text is the writer question to match against §3.
_QUESTION_HEADING_RE = re.compile(r"^###\s+(?P<q>.+?)\s*$", re.MULTILINE)


def _read(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except (OSError, UnicodeDecodeError):
        return None


def _has_block(text, btype):
    """True if `text` carries a real apodictic:<btype> block (a parsed carrier, not a prose mention).

    Classifying on parsed blocks — not a raw substring — keeps a file that merely *names* the marker
    in prose from being misrouted (the 2026-06-20 resolver-hardening sweep). Gated by
    validate.sh validator-conventions (M2)."""
    if art is None:
        return ("apodictic:%s" % btype) in (text or "")
    return any(bt == btype for bt, _o, _e in art.parse_blocks(text or ""))


# ---------------------------------------------------------------- §3 canonical questions

def _resolve_pd_path(root):
    """Locate pass-dependencies.md — the §3 SSoT — for R1. Returns a path or None (None -> R1
    degrades to a skip; a missing SSoT is an environment skip, never a false FAIL).

    Three resolution strategies, in order:
      1. Walk UP from the run folder (finding_trace._walk_up_sidecar idiom): the run folder itself,
         then its parents up to 3 levels. A run folder nested under `.../references/<folder>/` finds
         the shipped `references/pass-dependencies.md` one level up — this is how the canonical
         fixture resolves §3 from EITHER mirror copy (the fixture lives beside the SSoT).
      2. The shipped references copy relative to THIS script's dir (plugins/apodictic/scripts ->
         ../skills/core-editor/references) — the live path when run from the plugin install.
    """
    if root:
        d = os.path.abspath(root)
        for _ in range(4):
            cand = os.path.join(d, "pass-dependencies.md")
            if os.path.isfile(cand):
                return cand
            parent = os.path.dirname(d)
            if parent == d:
                break
            d = parent
    here = os.path.dirname(os.path.abspath(__file__))
    cand2 = os.path.join(here, "..", "skills", "core-editor", "references",
                         "pass-dependencies.md")
    return cand2 if os.path.isfile(cand2) else None


def section3_questions(pd_text):
    """The set of canonical §3 User Question strings (quotes stripped), or None if §3 won't parse.

    Reuses config_checks._parse_section3 (the pass-header SSoT parser) — no second §3 grammar. When
    config_checks can't be imported (art-less / path issue) returns None so R1 degrades rather than
    inventing a question set."""
    try:
        import config_checks
    except ImportError:
        return None
    try:
        _p2b, block_to_question, blocks = config_checks._parse_section3(pd_text or "")
    except Exception:
        return None
    if not blocks:
        return None
    return {q for q in block_to_question.values() if q}


# ---------------------------------------------------------------- the arm

def check(guide_text, run_folder, pd_text=None, strict=False):
    """Run the Results Guide integrity arm. Returns (code, lines).

    guide_text  = the Results Guide markdown.
    run_folder  = the directory citations resolve against (flat — no subdir walk).
    pd_text     = pass-dependencies.md contents for R1 (None -> R1 skipped/degraded).
    """
    lines, errs, warns = [], [], []

    if guide_text is None:
        return 1, ["results-guide: ERROR: guide file unreadable"]

    # R1 — membership: every `### question` heading is a canonical §3 User Question.
    q_set = section3_questions(pd_text) if pd_text is not None else None
    headings = [m.group("q").strip() for m in _QUESTION_HEADING_RE.finditer(guide_text)]
    if q_set is None:
        r1_note = " (R1 skipped — §3 source unavailable)"
    else:
        r1_note = ""
        for h in headings:
            if h not in q_set:
                errs.append("R1 unknown question: '### %s' — not a §3 User Question (an invented "
                            "block; the guide lists only questions the run's passes produced)" % h)

    # R2 — referential integrity (LOAD-BEARING): every cited run-folder filename resolves.
    folder_ok = run_folder is not None and os.path.isdir(run_folder)
    if not folder_ok:
        errs.append("R2 unreadable run folder: '%s' — citation trace cannot run (fail-closed)"
                    % run_folder)
    # Un-substituted template placeholders are a defect regardless of whether the run folder is
    # readable (the template was copied but not filled) — checked independent of folder_ok.
    for ph in _PLACEHOLDER_RE.findall(guide_text):
        if _PLACEHOLDER_FILE_HINT_RE.search(ph):
            errs.append("R2 placeholder citation: `%s` — the guide cites an un-substituted "
                        "placeholder filename (the template was copied but not filled)" % ph)
    # Resolved citations (extension-guarded) must resolve to a run-folder file — and must be a
    # plain, run-folder-CONTAINED reference. The run folder is FLAT (no subdir walk, per this
    # function's contract): a citation is a bare filename, never a path. So the stricter, simpler
    # rule consistent with that convention is to reject any citation that (a) is an absolute path,
    # or (b) carries a path separator or a `..` traversal segment — either would let a citation
    # like `../outside.md` (or `/etc/passwd`) resolve to a file OUTSIDE the run folder and PASS
    # R2, silently breaking the R2 guarantee ("every cited artifact is a real file in the run
    # folder"). Belt-and-suspenders: after the syntactic reject, a realpath CONTAINMENT check
    # guards against symlink games (a bare filename that is itself a symlink escaping the folder).
    cited = _CITED_RE.findall(guide_text)
    if folder_ok:
        run_root = os.path.realpath(run_folder)
        for c in cited:
            if "[" in c or "]" in c:
                continue  # an un-substituted slot — already reported by the placeholder pass
            if os.path.isabs(c):
                errs.append("R2 escaping citation: `%s` — an absolute path; the guide may cite "
                            "only bare run-folder filenames (flat run folder)" % c)
                continue
            if os.sep in c or (os.altsep and os.altsep in c) or ".." in c.split("/"):
                errs.append("R2 escaping citation: `%s` — a traversal/subdir path; citations must "
                            "not escape the run folder (flat run folder, bare filenames only)" % c)
                continue
            resolved = os.path.realpath(os.path.join(run_folder, c))
            if resolved != run_root and not resolved.startswith(run_root + os.sep):
                errs.append("R2 escaping citation: `%s` — resolves outside the run folder "
                            "(symlink escape); citations must stay in the run folder" % c)
                continue
            if not os.path.isfile(os.path.join(run_folder, c)):
                errs.append("R2 dangling citation: `%s` — no such file in the run folder" % c)

    # R3 — hygiene (rides along): no severity leak, no finding block.
    if _SEVERITY_RE.search(guide_text):
        errs.append("R3 severity leak: the guide carries a Must/Should/Could-Fix token — it "
                    "indexes, never diagnoses (the diagnosis lives in the editorial letter)")
    if _has_block(guide_text, "finding"):
        errs.append("R3 finding block: the guide carries an apodictic:finding block — a navigation "
                    "index must not masquerade as a second editorial letter")

    # Report
    lines.append("results-guide: %d question section(s), %d citation(s)%s"
                 % (len(headings), len(cited), r1_note))
    for e in errs:
        lines.append("  ERROR: %s" % e)
    for w in warns:
        lines.append("  %s: %s" % ("ERROR (--strict)" if strict else "WARN", w))

    if errs or (strict and warns):
        lines.append("results-guide: FAIL (%d error(s)%s)"
                     % (len(errs), ", %d strict warn(s)" % len(warns) if (strict and warns) else ""))
        return 1, lines
    if warns:
        lines.append("WARN: results-guide: %d advisory gap(s)" % len(warns))
    else:
        lines.append("results-guide: PASS (referential integrity + membership + hygiene)")
    return 0, lines


# ---------------------------------------------------------------- artifact resolution

def _newest(paths):
    return max(paths, key=os.path.getmtime) if paths else None


def resolve_guide_and_folder(paths):
    """(guide_path, run_folder) from CLI paths.

    One dir arg  -> glob the newest _GUIDE_GLOB inside it; the run folder is that dir.
    Explicit args -> the first arg is the guide file; the run folder is the SECOND arg if given
                     (a dir), else the guide's own directory (the flat run folder).
    Returns (None, folder) when a dir carries no guide (usage error upstream)."""
    if len(paths) == 1 and os.path.isdir(paths[0]):
        folder = paths[0]
        guide = _newest(glob.glob(os.path.join(folder, _GUIDE_GLOB)))
        return guide, folder
    guide = paths[0] if paths else None
    folder = None
    if len(paths) > 1 and os.path.isdir(paths[1]):
        folder = paths[1]
    elif guide:
        folder = os.path.dirname(os.path.abspath(guide))
    return guide, folder


def run(paths, strict=False):
    guide, folder = resolve_guide_and_folder(paths)
    if not guide:
        return 2, ["results-guide: no Results Guide found (need a *_Results_Guide_*.md in the run "
                   "folder, or an explicit guide file)"]
    # R1 source: pass-dependencies.md relative to the run folder, else the shipped references copy.
    pd_path = _resolve_pd_path(folder if folder else os.path.dirname(os.path.abspath(guide)))
    pd_text = _read(pd_path) if pd_path else None
    return check(_read(guide), folder, pd_text=pd_text, strict=strict)


# ---------------------------------------------------------------- self-test

def run_self_test():
    import tempfile
    import shutil
    rc = {"v": 0}
    made = []

    def check_case(name, cond):
        print("  %s: %s" % (name, "OK" if cond else "FAIL"))
        if not cond:
            rc["v"] = 1

    # non-UTF8 artifact: _read must degrade to None, never a traceback.
    _fd, _nu = tempfile.mkstemp(suffix=".md")
    with os.fdopen(_fd, "wb") as _fh:
        _fh.write(b"\xff\xfenot utf-8\xff")
    check_case("non_utf8_read_returns_none", _read(_nu) is None)
    os.unlink(_nu)

    # Two canonical §3 questions (BYTE-IDENTICAL to pass-dependencies.md §3, quotes stripped).
    Q_STRUCT = "Is the structure working?"
    Q_CHAR = "Are my characters landing?"
    # Minimal §3 table so section3_questions has a real SSoT to parse (reuses config_checks).
    PD = ("## §3. Macro Block Definitions\n\n"
          "| Macro Block | Internal Passes | User Question |\n"
          "|---|---|---|\n"
          "| Structure Map | 0 + 2 | \"%s\" |\n"
          "| Character Architecture | 5 + 7 | \"%s\" |\n"
          "\n## §4. next\n" % (Q_STRUCT, Q_CHAR))

    check_case("section3_parses",
               section3_questions(PD) == {Q_STRUCT, Q_CHAR})
    check_case("section3_degrades_on_junk", section3_questions("no table here") is None)

    def guide(sections, extra=""):
        body = ("# Results Guide — Proj\n_Run: run_\n\n## How to use this guide\n"
                "Start with the Editorial Letter.\n\n---\n\n## Your results by question\n\n")
        body += sections
        body += ("\n## State files\n- Diagnostic State: `Diagnostic_State.md`\n"
                 "- Findings Ledger: `Proj_Findings_Ledger_run.md`\n\n"
                 "## What to do next\n- `/coach` — plan revision sessions\n"
                 "- `/audit [name]` — run a focused deep-dive\n")
        return body + extra

    d = tempfile.mkdtemp()
    made.append(d)
    # Real files backing the positive citations.
    for fn in ("Proj_Pass2_Structural_Mapping_run.md", "Proj_Pass5_Character_Audit_run.md",
               "Diagnostic_State.md", "Proj_Findings_Ledger_run.md"):
        with open(os.path.join(d, fn), "w", encoding="utf-8", newline="") as fh:
            fh.write("x\n")

    sec_pos = ("### %s\n- Editorial Letter § Structure Map\n"
               "- Detail: `Proj_Pass2_Structural_Mapping_run.md`\n\n"
               "### %s\n- Editorial Letter § Character Architecture\n"
               "- Detail: `Proj_Pass5_Character_Audit_run.md`\n" % (Q_STRUCT, Q_CHAR))

    # rg_pos — all cited files exist, both questions canonical, command tokens present -> 0
    code, lines = check(guide(sec_pos), d, pd_text=PD)
    check_case("rg_pos", code == 0 and any("PASS" in ln for ln in lines))
    # ...and the /coach and /audit [name] command tokens did NOT false-fail R2 (extension guard)
    check_case("rg_command_tokens_not_dangling",
               not any("R2 dangling" in ln or "R2 placeholder" in ln for ln in lines))

    # rg_r1_unknown_question — a heading that is not a §3 User Question -> 1
    sec_bad_q = sec_pos + "### Is the vibe good?\n- Detail: `Proj_Pass2_Structural_Mapping_run.md`\n"
    code, lines = check(guide(sec_bad_q), d, pd_text=PD)
    check_case("rg_r1_unknown_question",
               code == 1 and any("R1 unknown question" in ln and "vibe" in ln for ln in lines))

    # rg_r2_dangling — cites a file not on disk -> 1
    sec_dangling = ("### %s\n- Detail: `Proj_Pass2_Structural_Mapping_run.md`\n"
                    "- Detail: `Proj_Nonexistent_run.md`\n" % Q_STRUCT)
    code, lines = check(guide(sec_dangling), d, pd_text=PD)
    check_case("rg_r2_dangling",
               code == 1 and any("R2 dangling" in ln and "Nonexistent" in ln for ln in lines))

    # rg_r2_escape_traversal — THE Codex P1 repro: a real file OUTSIDE the run folder, cited via
    # `../<file>.md`, must FAIL (escape) and NOT resolve-then-PASS. Create the outside file in the
    # run folder's parent so `../` would otherwise land on a real file.
    _outside = os.path.join(os.path.dirname(os.path.abspath(d)), "rg_outside_probe.md")
    with open(_outside, "w", encoding="utf-8", newline="") as fh:
        fh.write("outside\n")
    try:
        sec_escape = ("### %s\n- Detail: `../rg_outside_probe.md`\n" % Q_STRUCT)
        code, lines = check(guide(sec_escape), d, pd_text=PD)
        check_case("rg_r2_escape_traversal",
                   code == 1 and any("R2 escaping citation" in ln and "rg_outside_probe" in ln
                                     for ln in lines)
                   and not any("PASS" in ln for ln in lines))
    finally:
        os.unlink(_outside)

    # rg_r2_escape_absolute — an absolute-path citation must FAIL (escape), never PASS. Point it at
    # a file that really exists (a run-folder artifact by absolute path) so the failure is the
    # escape rule, not a dangling-file coincidence.
    sec_abs = ("### %s\n- Detail: `%s`\n"
               % (Q_STRUCT, os.path.join(d, "Proj_Pass2_Structural_Mapping_run.md")))
    code, lines = check(guide(sec_abs), d, pd_text=PD)
    check_case("rg_r2_escape_absolute",
               code == 1 and any("R2 escaping citation" in ln for ln in lines)
               and not any("PASS" in ln for ln in lines))

    # rg_r2_placeholder — an un-substituted `[pass artifact filename]` left in -> 1
    sec_ph = "### %s\n- Detail: `[pass artifact filename]`\n" % Q_STRUCT
    code, lines = check(guide(sec_ph), d, pd_text=PD)
    check_case("rg_r2_placeholder",
               code == 1 and any("R2 placeholder" in ln for ln in lines))
    # the placeholder must NOT be matched as a plain .md citation (extension is inside the brackets)
    check_case("rg_placeholder_not_dangling",
               not any("R2 dangling" in ln for ln in lines))

    # rg_r3_severity_token — a Must-Fix token in prose -> 1
    code, lines = check(guide(sec_pos, extra="\nThis is a Must-Fix issue.\n"), d, pd_text=PD)
    check_case("rg_r3_severity_token",
               code == 1 and any("R3 severity leak" in ln for ln in lines))

    # rg_r3_finding_block — an apodictic:finding block -> 1
    fblock = ('\n<!-- apodictic:finding\n{"schema":"apodictic.finding.v1","id":"F-P5-01",'
              '"mechanism":"m","severity":"Must-Fix","confidence":"HIGH","evidence_refs":["c"],'
              '"fix_class":"x","risk_if_fixed":"y"}\n-->\n')
    code, lines = check(guide(sec_pos, extra=fblock), d, pd_text=PD)
    check_case("rg_r3_finding_block",
               code == 1 and any("R3 finding block" in ln for ln in lines))

    # rg_targeted_run_omits_blocks — only ONE of the two questions, all files present -> 0
    # (absence is legal; the guide lists only the blocks the run produced)
    sec_one = ("### %s\n- Detail: `Proj_Pass2_Structural_Mapping_run.md`\n" % Q_STRUCT)
    code, lines = check(guide(sec_one), d, pd_text=PD)
    check_case("rg_targeted_run_omits_blocks", code == 0)

    # R1 degrades (not fails) when §3 is unavailable — an unknown question passes with a skip note
    code, lines = check(guide(sec_bad_q), d, pd_text=None)
    check_case("rg_r1_degrades_no_section3",
               code == 0 and any("R1 skipped" in ln for ln in lines))

    # R2 fail-closed: unreadable run folder -> non-zero, named error
    code, lines = check(guide(sec_pos), os.path.join(d, "nope"), pd_text=PD)
    check_case("rg_r2_unreadable_folder",
               code == 1 and any("R2 unreadable run folder" in ln for ln in lines))

    # run(): dir arg globs the newest guide + resolves the folder
    with open(os.path.join(d, "Proj_Results_Guide_run.md"), "w", encoding="utf-8", newline="") as fh:
        fh.write(guide(sec_pos))
    # a sibling pass-dependencies.md so run()'s R1 engages against the real §3 parser
    with open(os.path.join(d, "pass-dependencies.md"), "w", encoding="utf-8", newline="") as fh:
        fh.write(PD)
    code, lines = run([d])
    check_case("run_folder_resolution", code == 0 and any("PASS" in ln for ln in lines))

    # explicit-file classification: guide file + its dir
    code, _ = run([os.path.join(d, "Proj_Results_Guide_run.md"), d])
    check_case("explicit_files_classify", code == 0)

    # no guide in a dir -> usage error (exit 2)
    d2 = tempfile.mkdtemp()
    made.append(d2)
    check_case("missing_guide_usage_error", run([d2])[0] == 2)

    for d in made:
        shutil.rmtree(d, ignore_errors=True)
    print("Self-test: PASS" if rc["v"] == 0 else "Self-test: FAIL")
    return rc["v"]


def main(argv):
    if "--self-test" in argv:
        return run_self_test()
    args = [a for a in argv[1:] if a not in ("results-guide",)]
    strict = "--strict" in args
    paths = [a for a in args if not a.startswith("--")]
    if not paths:
        print("Usage: results_guide.py results-guide <run_folder|files...> [--strict] | --self-test")
        return 2
    code, lines = run(paths, strict=strict)
    for ln in lines:
        print(ln)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
