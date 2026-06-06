#!/usr/bin/env python3
"""argument-spine — structural integrity for the Nonfiction Pre-Draft Pathway (Increment 1).

`validate.sh argument-spine <run_folder|files>` shells out here. Before a draft exists, a writer
plans the argument: the thesis, the claim ladder, and the opposing view the argument must defeat.
That plan is one apodictic.argument_spine.v1 block, and it SEEDS the shared Argument_State.md
artifact (docs/argument-state-schema.md) — thesis -> §2 C0; subclaims -> §2 ladder; anti_thesis ->
§6 Objection 1; the §1 classification fields. The Dialectical Clarity audit fills the
draft-dependent sections later. This validator owns the pre-draft contract AND mechanizes the
seed-Argument_State integration.

  A1 invalid spine    the argument_spine block fails its schema (bad argument_type / burden_level /
                      audience_* / stakes_type enum, missing required field, <1 subclaim, bad JSON).
  A2 unseeded         a spine block is present but the artifact is not a seeded Argument_State — it
                      lacks the canonical '## 1. Context and Classification' / '## 2. Claim
                      Architecture' headings. The spine must seed the shared artifact, not float free.
  A3 thesis/C0 drift  the seeded §2 'C0 (main claim):' line does not carry the spine's `thesis` — the
                      structured spine and the human-readable Argument_State disagree.
  W1 anti-thesis echo the `anti_thesis` is empty or a normalized echo of the `thesis` (advisory;
                      ERROR --strict). A pre-draft plan must name a GENUINE opposing view, not a
                      restatement. Override: <!-- override: argument-spine-antithesis — <reason> -->.

A2 and A3 are the signature checks: they verify the spine actually populated Argument_State (the
chosen integration). Reuses apodictic_artifacts (block grammar + schema engine). An artifact with
no spine block is a no-op. See docs/nonfiction-pre-draft.md.

  argument_spine.py argument-spine <run_folder|files...> [--strict]
  argument_spine.py --self-test

Exit: 0 clean / WARN-only, 1 ERROR (or WARN under --strict), 2 usage.
"""
import glob
import os
import re
import sys

try:
    import apodictic_artifacts as art
except ImportError:
    art = None

_SCHEMA_ID = "apodictic.argument_spine.v1"
_STATE_GLOB = "Argument_State*.md"
_SCORE_ENUMS = ("argument_type", "burden_level", "audience_expertise", "audience_receptivity")
# Canonical Argument_State headings the spine must seed (docs/argument-state-schema.md §1/§2).
_SEC1_RE = re.compile(r"^##\s+1\.\s+Context and Classification", re.IGNORECASE | re.MULTILINE)
_SEC2_RE = re.compile(r"^##\s+2\.\s+Claim Architecture", re.IGNORECASE | re.MULTILINE)
# The §2 main-claim line: "C0 (main claim): <thesis>".
_C0_RE = re.compile(r"^\s*C0\s*\(main claim\)\s*:\s*(.+?)\s*$", re.IGNORECASE | re.MULTILINE)
_ANTITHESIS_OVERRIDE_RE = re.compile(r"<!--\s*override:\s*argument-spine-antithesis\b", re.IGNORECASE)


def _read(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return None


def _norm(s):
    return re.sub(r"\s+", " ", (s or "").strip()).lower()


def _echo_norm(s):
    """Normalization for the W1 echo check: lowercase, collapse whitespace, drop punctuation — so a
    restated thesis ('Fund ramps now.') still reads as an echo of the thesis ('fund ramps now')."""
    return re.sub(r"[^a-z0-9 ]", "", _norm(s)).strip()


def parse_spine(text):
    """(obj_or_None, schema_errs) for the FIRST apodictic:argument_spine block ('' errs if absent)."""
    if not text or art is None:
        return None, []
    schema = art.load_schema(_SCHEMA_ID)
    for btype, obj, jerr in art.parse_blocks(text):
        if btype != "argument_spine":
            continue
        if jerr:
            return None, ["invalid JSON — %s" % jerr]
        return obj, art.validate_obj(obj, schema, "argument_spine")
    return None, []


def check(text, strict=False):
    """Run the argument-spine integrity checks. Returns (code, lines)."""
    lines, errs, warns = [], [], []
    obj, schema_errs = parse_spine(text)
    if obj is None and not schema_errs:
        return 0, ["argument-spine: no argument_spine block found — nothing to check"]

    # A1 — schema / JSON validity
    for e in schema_errs:
        errs.append("A1 invalid spine: %s" % e)

    if obj is not None and not schema_errs:
        # A2 — the spine must seed Argument_State (the chosen integration), not float free
        seeded_1 = bool(_SEC1_RE.search(text))
        seeded_2 = bool(_SEC2_RE.search(text))
        if not (seeded_1 and seeded_2):
            missing = " + ".join(
                h for h, ok in (("## 1. Context and Classification", seeded_1),
                                ("## 2. Claim Architecture", seeded_2)) if not ok)
            errs.append("A2 unseeded: spine present but the artifact is not a seeded Argument_State "
                        "(missing heading: %s) — the spine must seed the shared artifact" % missing)
        else:
            # A3 — the seeded §2 C0 line must carry the spine's thesis
            m = _C0_RE.search(text)
            if not m:
                errs.append("A3 thesis/C0 drift: §2 has no 'C0 (main claim):' line to carry the "
                            "spine's thesis")
            elif _norm(obj.get("thesis")) not in _norm(m.group(1)):
                errs.append("A3 thesis/C0 drift: the seeded C0 (main claim) does not carry the "
                            "spine's thesis — the spine and Argument_State disagree")

        # W1 — anti-thesis must name a genuine opposing view, not echo the thesis
        anti, thesis = _echo_norm(obj.get("anti_thesis")), _echo_norm(obj.get("thesis"))
        if (not anti or anti == thesis) and not _ANTITHESIS_OVERRIDE_RE.search(text):
            warns.append("W1 anti-thesis echo: the anti_thesis is empty or restates the thesis — "
                         "name the genuine opposing view the argument must defeat")

    # Report
    if obj is not None and not schema_errs:
        lines.append("argument-spine: %s / burden=%s / audience=%s,%s; %d subclaim(s)"
                     % (obj.get("argument_type"), obj.get("burden_level"),
                        obj.get("audience_expertise"), obj.get("audience_receptivity"),
                        len(obj.get("subclaims") or [])))
    for e in errs:
        lines.append("  ERROR: %s" % e)
    for w in warns:
        lines.append("  %s: %s" % ("ERROR (--strict)" if strict else "WARN", w))

    if errs or (strict and warns):
        lines.append("argument-spine: FAIL (%d error(s)%s)"
                     % (len(errs), ", %d strict warn(s)" % len(warns) if (strict and warns) else ""))
        return 1, lines
    if warns:
        lines.append("WARN: argument-spine: %d advisory gap(s) — see W1 above" % len(warns))
    else:
        lines.append("argument-spine: PASS (contract + seeds Argument_State §1/§2 + anti-thesis)")
    return 0, lines


# ---------------------------------------------------------------- resolution

def _newest(paths):
    return max(paths, key=os.path.getmtime) if paths else None


def resolve(paths):
    if len(paths) == 1 and os.path.isdir(paths[0]):
        return _newest(glob.glob(os.path.join(paths[0], _STATE_GLOB)))
    for p in paths:
        if "apodictic:argument_spine" in (_read(p) or ""):
            return p
    return paths[0] if paths else None


def run(paths, strict=False):
    path = resolve(paths)
    if not path:
        return 2, ["argument-spine: no pre-draft Argument_State found (need an Argument_State*.md or "
                   "a file with an apodictic:argument_spine block)"]
    text = _read(path)
    if text is None:
        return 2, ["argument-spine: cannot read %s" % path]
    return check(text, strict=strict)


# ---------------------------------------------------------------- self-test

def run_self_test():
    import json as _j
    rc = {"v": 0}

    def chk(name, cond):
        print("  %s: %s" % (name, "OK" if cond else "FAIL"))
        if not cond:
            rc["v"] = 1

    def spine(thesis="the city should fund curb-cut ramps citywide",
              subclaims=("C1: ramps remove a documented mobility barrier",),
              anti="ramps are a low priority next to road repair", **over):
        obj = {"schema": _SCHEMA_ID, "form": "op-ed", "goal": "persuade the council to fund ramps",
               "argument_type": "AT3", "burden_level": "HIGH", "audience_expertise": "MIXED",
               "audience_receptivity": "HOSTILE", "thesis": thesis, "subclaims": list(subclaims),
               "anti_thesis": anti}
        obj.update(over)
        return "<!-- apodictic:argument_spine\n%s\n-->" % _j.dumps(obj)

    def seeded(thesis="the city should fund curb-cut ramps citywide", block=None):
        # a seeded Argument_State.md: canonical §1/§2 headings + a C0 line carrying the thesis
        return ("# Argument State\n\n## 1. Context and Classification\n\nForm: op-ed\n\n"
                "## 2. Claim Architecture\n\nC0 (main claim): %s\n\n## 6. Objection and "
                "Dialectical Integrity Map\n\nObjection 1: ramps are a low priority\n\n%s\n"
                % (thesis, block if block is not None else spine(thesis=thesis)))

    # clean: a well-formed spine that seeds Argument_State §1/§2 with a matching C0
    chk("clean", check(seeded())[0] == 0)
    # no block -> no-op
    chk("no_block_noop", check("# notes\nno spine yet\n")[0] == 0)

    # A1 — bad enum / missing field / empty ladder / JSON
    chk("a1_bad_argument_type", check(seeded(block=spine(argument_type="AT9")))[0] == 1)
    chk("a1_bad_burden", check(seeded(block=spine(burden_level="EXTREME")))[0] == 1)
    chk("a1_bad_audience", check(seeded(block=spine(audience_receptivity="WARM")))[0] == 1)
    chk("a1_empty_ladder", check(seeded(block=spine(subclaims=())))[0] == 1)
    chk("a1_missing_field",
        check(seeded(block=spine().replace('"anti_thesis"', '"anti"')))[0] == 1)
    code, lines = check('<!-- apodictic:argument_spine\n{"schema":"apodictic.argument_spine.v1"\n-->')
    chk("a1_bad_json", code == 1 and any("A1 invalid spine" in ln for ln in lines))

    # A2 — spine present but artifact is not a seeded Argument_State (no §1/§2 headings)
    code, lines = check(spine())   # the block alone, no Argument_State scaffolding
    chk("a2_unseeded", code == 1 and any("A2 unseeded" in ln for ln in lines))
    # only §1 present, §2 missing -> still A2
    code, lines = check("## 1. Context and Classification\n\n" + spine())
    chk("a2_partial_seed", code == 1 and any("A2 unseeded" in ln and "Claim Architecture" in ln for ln in lines))

    # A3 — C0 line does not carry the spine's thesis (drift between block and seeded markdown)
    code, lines = check(seeded(thesis="ramps citywide").replace(
        "C0 (main claim): ramps citywide", "C0 (main claim): something entirely different"))
    chk("a3_thesis_drift", code == 1 and any("A3 thesis/C0 drift" in ln for ln in lines))
    # §2 present but no C0 line at all -> A3
    code, lines = check("## 1. Context and Classification\n## 2. Claim Architecture\nno c0 line\n" + spine())
    chk("a3_no_c0_line", code == 1 and any("A3 thesis/C0 drift" in ln for ln in lines))

    # W1 — anti-thesis echoes the thesis (advisory; ERROR --strict; override silences)
    code, lines = check(seeded(block=spine(thesis="fund ramps now", anti="Fund ramps now."),
                               thesis="fund ramps now"))
    chk("w1_antithesis_echo", code == 0 and any("W1 anti-thesis echo" in ln for ln in lines))
    chk("w1_echo_strict_fails",
        check(seeded(block=spine(thesis="fund ramps now", anti="fund ramps now"),
                     thesis="fund ramps now"), strict=True)[0] == 1)
    ov = "<!-- override: argument-spine-antithesis — the inverse is genuinely the live debate -->\n"
    code, lines = check(seeded(block=ov + spine(thesis="fund ramps now", anti="fund ramps now"),
                               thesis="fund ramps now"))
    chk("w1_override", code == 0 and not any("WARN" in ln and "anti-thesis" in ln for ln in lines))
    # a genuine (non-echo) anti-thesis does not trip W1
    chk("w1_genuine_clean", not any("W1" in ln for ln in check(seeded())[1]))

    # resolution: run-folder (Argument_State*.md) + explicit file
    import tempfile
    import shutil
    d = tempfile.mkdtemp()
    try:
        p = os.path.join(d, "Argument_State.md")
        with open(p, "w") as fh:
            fh.write(seeded())
        chk("run_folder_resolution", run([d])[0] == 0)
        chk("explicit_file_resolution", run([p])[0] == 0)
        chk("missing_artifact_usage", run([os.path.join(d, "nope.md")])[0] == 2)
    finally:
        shutil.rmtree(d, ignore_errors=True)

    print("Self-test: PASS" if rc["v"] == 0 else "Self-test: FAIL")
    return rc["v"]


def main(argv):
    if "--self-test" in argv:
        return run_self_test()
    args = [a for a in argv[1:] if a != "argument-spine"]
    strict = "--strict" in args
    paths = [a for a in args if not a.startswith("--")]
    if not paths:
        print("Usage: argument_spine.py argument-spine <run_folder|files...> [--strict] | --self-test")
        return 2
    code, lines = run(paths, strict=strict)
    for ln in lines:
        print(ln)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
