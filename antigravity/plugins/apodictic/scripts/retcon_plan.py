#!/usr/bin/env python3
"""retcon-plan — structural integrity for the Retcon Planning coaching track (Coaching Deepening).

`validate.sh retcon-plan <run_folder> [--strict]` (or explicit files) shells out here. A returning
author planning a retroactive-continuity revision records each commitment as a structured
`apodictic.retcon_item.v1` block in a Retcon Plan artifact. Two axes are kept orthogonal:
`mutability` (the commitment budget — locked=observed canon the reader has used; costly=exposed
consequences; free=unused latent) and `retcon_type` (the fair-play axis — dramatic=recontextualize
for meaning; evidential=change the evidence the reader reasoned from). This validator owns the
retcon-planning contract — and mechanizes the two disciplines the method insists on.

  R1 invalid item     a retcon_item block fails its schema (bad enum / id / missing field / JSON).
  R2 duplicate id     two items share an RX-NN id.
  R3 evidential lock  retcon_type=evidential AND mutability=locked — changing a clue the reader has
                      already reasoned from (fair-play violation). The signature check.
                      Override: <!-- override: retcon-evidential RX-NN — <rationale> --> (per id).
  R4 dangling target  an item's target_id is not declared in the '## Retcon Targets' list.
  W1 blast unaccounted a locked/costly item with an empty blast_radius — a costly retcon planned
                      without naming what it endangers (advisory; ERROR under --strict).
  W2 firewall drift   intervention_class/disposition reads like invented prose, not a class —
                      the Firewall line (advisory; ERROR --strict). Override: retcon-firewall RX-NN.

Reuses apodictic_artifacts (one block grammar + the schema engine). Each artifact is optional; an
empty/absent one is a no-op. See docs/retcon-planning.md.

  retcon_plan.py retcon-plan <run_folder|files...> [--strict]
  retcon_plan.py --self-test

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

_SCHEMA_ID = "apodictic.retcon_item.v1"
_PLAN_GLOB = "*_Retcon_Plan_*.md"
_MUTABLE_COSTLY = ("locked", "costly")

# A target declared as a list item in the Retcon Targets section: "- T1: ..." / "- **T1** ...".
_TARGET_DECL_RE = re.compile(r"^\s*(?:[-*]|[0-9]+\.)\s+\*{0,2}(T[0-9]+)\b", re.MULTILINE)
# Override markers naming an item id: "<!-- override: <slug> RX-01 — ... -->".
_OVERRIDE_RE = re.compile(r"<!--\s*override:\s*([a-z-]+)\s+(RX-[0-9]+)\b", re.IGNORECASE)
# W2 firewall-drift heuristics: a long quoted span (likely invented prose), or a directive to
# write specific content rather than name a class.
_INVENTED_QUOTE_RE = re.compile(r"[\"“][^\"”]{25,}[\"”]|['‘][^'’]{25,}['’]")
# Verb must directly govern the object ("write the line", "draft a scene") so the manuscript-
# revision noun "the draft" / "the draft's opening scene" does not false-trigger.
_GHOSTWRITE_RE = re.compile(
    r"\b(?:write|draft|ghost-?write|pen)\s+(?:the|a|an|some|her|his|their)\s+"
    r"(?:line|sentence|paragraph|dialogue|prose|passage|scene)\b",
    re.IGNORECASE)


def _read(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return None


def _section(text, heading):
    """The substring under the first '## <heading>' up to the next level-2 heading; '' if absent."""
    rx = re.compile(r"^##\s+.*" + re.escape(heading), re.IGNORECASE | re.MULTILINE)
    m = rx.search(text)
    if not m:
        return ""
    rest = text[m.end():]
    nxt = re.search(r"^##\s", rest, re.MULTILINE)
    return rest[:nxt.start()] if nxt else rest


def declared_targets(text):
    """Set of target ids (T1, T2, …) declared as list items under the Retcon Targets section.
    Falls back to the whole doc if no such section heading is present."""
    scope = _section(text, "Retcon Targets") or text
    return set(_TARGET_DECL_RE.findall(scope))


def _overrides(text, slug):
    return {m.group(2) for m in _OVERRIDE_RE.finditer(text) if m.group(1).lower() == slug}


def parse_items(text):
    """[(obj_or_None, schema_errs, index), ...] for each apodictic:retcon_item block."""
    items = []
    if not text or art is None:
        return items
    schema = art.load_schema(_SCHEMA_ID)
    idx = 0
    for btype, obj, jerr in art.parse_blocks(text):
        if btype != "retcon_item":
            continue
        idx += 1
        where = "retcon_item #%d" % idx
        if jerr:
            items.append((None, ["%s: invalid JSON — %s" % (where, jerr)], idx))
            continue
        errs = art.validate_obj(obj, schema, where)
        items.append((obj, errs, idx))
    return items


def plan(text, strict=False):
    """Run the Retcon Plan integrity checks. Returns (code, lines)."""
    lines, errs, warns = [], [], []
    items = parse_items(text)
    if not items:
        return 0, ["retcon-plan: no retcon_item blocks found — nothing to check"]

    # R1 — schema/JSON validity (per block)
    for _obj, schema_errs, _idx in items:
        for e in schema_errs:
            errs.append("R1 invalid item: %s" % e)

    valid = [(obj, idx) for obj, schema_errs, idx in items if obj is not None and not schema_errs]

    # R2 — duplicate id
    seen = {}
    for obj, idx in valid:
        seen.setdefault(obj.get("id"), []).append(idx)
    by_id = {}
    for rid, where in sorted(seen.items()):
        if len(where) > 1:
            errs.append("R2 duplicate id: %s appears %d times (ids must be unique)" % (rid, len(where)))
        by_id[rid] = next(o for o, _ in valid if o.get("id") == rid)

    targets = declared_targets(text)
    ev_overrides = _overrides(text, "retcon-evidential")
    fw_overrides = _overrides(text, "retcon-firewall")

    for rid, obj in sorted(by_id.items()):
        # R3 — evidential retcon of locked canon (fair play)
        if obj.get("retcon_type") == "evidential" and obj.get("mutability") == "locked":
            if rid in ev_overrides:
                warns.append("R3 evidential-lock (override): %s changes evidence in locked canon "
                             "(override marker present)" % rid)
            else:
                errs.append("R3 evidential-lock: %s is evidential AND locked — changing a clue the "
                            "reader has already reasoned from (fair-play violation). Recontextualize "
                            "for meaning (dramatic), or override: "
                            "<!-- override: retcon-evidential %s — <rationale> -->" % (rid, rid))
        # R4 — dangling target
        tid = obj.get("target_id")
        if tid not in targets:
            errs.append("R4 dangling target: %s.target_id=%s not declared in '## Retcon Targets'" % (rid, tid))
        # W1 — unaccounted blast radius on a locked/costly item
        if obj.get("mutability") in _MUTABLE_COSTLY and not (obj.get("blast_radius") or []):
            warns.append("W1 blast unaccounted: %s is %s but names no blast_radius — what does this "
                         "retcon endanger?" % (rid, obj.get("mutability")))
        # W2 — firewall drift (invented prose where a class belongs)
        blob = "%s %s" % (obj.get("intervention_class") or "", obj.get("disposition") or "")
        if (_INVENTED_QUOTE_RE.search(blob) or _GHOSTWRITE_RE.search(blob)) and rid not in fw_overrides:
            warns.append("W2 firewall drift: %s reads like invented prose, not an intervention "
                         "class — plan the class; the author writes the tissue" % rid)

    # Report
    lines.append("retcon-plan: %d item(s)%s; %d target(s) declared" % (
        len(items), "" if len(valid) == len(items) else " (%d well-formed)" % len(valid), len(targets)))
    for obj, _idx in valid:
        lines.append("  %-7s target=%-3s kind=%-14s mut=%-6s type=%s"
                     % (obj.get("id"), obj.get("target_id"), obj.get("kind"),
                        obj.get("mutability"), obj.get("retcon_type")))
    for e in errs:
        lines.append("  ERROR: %s" % e)
    for w in warns:
        lines.append("  %s: %s" % ("ERROR (--strict)" if strict else "WARN", w))

    if errs or (strict and warns):
        lines.append("retcon-plan: FAIL (%d error(s)%s)"
                     % (len(errs), ", %d strict warn(s)" % len(warns) if (strict and warns) else ""))
        return 1, lines
    if warns:
        lines.append("WARN: retcon-plan: %d advisory gap(s) — see W1/W2 above" % len(warns))
    else:
        lines.append("retcon-plan: PASS (commitment-budget + fair-play + target integrity)")
    return 0, lines


# ---------------------------------------------------------------- resolution

def _newest(paths):
    return max(paths, key=os.path.getmtime) if paths else None


def resolve(paths):
    if len(paths) == 1 and os.path.isdir(paths[0]):
        return _newest(glob.glob(os.path.join(paths[0], _PLAN_GLOB)))
    for p in paths:
        if "apodictic:retcon_item" in (_read(p) or ""):
            return p
    return paths[0] if paths else None


def run(paths, strict=False):
    path = resolve(paths)
    if not path:
        return 2, ["retcon-plan: no Retcon Plan artifact found (need a *_Retcon_Plan_*.md or a file "
                   "with apodictic:retcon_item blocks)"]
    text = _read(path)
    if text is None:
        return 2, ["retcon-plan: cannot read %s" % path]
    return plan(text, strict=strict)


# ---------------------------------------------------------------- self-test

def run_self_test():
    import json as _j
    import tempfile
    import shutil
    rc = {"v": 0}
    made = []

    def chk(name, cond):
        print("  %s: %s" % (name, "OK" if cond else "FAIL"))
        if not cond:
            rc["v"] = 1

    def item(rid, target="T1", kind="setup-debt", mut="free", rtype="dramatic",
             iclass="plant a recontextualizable detail", disp="author seeds it",
             blast=None, locations=None):
        obj = {"schema": _SCHEMA_ID, "id": rid, "target_id": target, "kind": kind,
               "mutability": mut, "retcon_type": rtype, "intervention_class": iclass,
               "disposition": disp}
        if blast is not None:
            obj["blast_radius"] = blast
        if locations is not None:
            obj["locations"] = locations
        return "<!-- apodictic:retcon_item\n%s\n-->" % _j.dumps(obj)

    TARGETS = "## Retcon Targets\n- T1: the sister was complicit\n- T2: the prologue is the theme\n\n"

    # clean single item (free + dramatic, declared target)
    chk("clean_single", plan(TARGETS + item("RX-01"))[0] == 0)

    # R1 bad enum / id / missing field / JSON
    chk("r1_bad_mutability", plan(TARGETS + item("RX-01", mut="soft"))[0] == 1)
    chk("r1_bad_rtype", plan(TARGETS + item("RX-01", rtype="evidentiary"))[0] == 1)
    chk("r1_bad_id", plan(TARGETS + item("RX-1"))[0] == 1)
    chk("r1_missing_field",
        plan(TARGETS + item("RX-01").replace('"disposition"', '"disp"'))[0] == 1)
    code, lines = plan(TARGETS + '<!-- apodictic:retcon_item\n{"schema":"apodictic.retcon_item.v1"\n-->')
    chk("r1_bad_json", code == 1 and any("R1 invalid item" in ln for ln in lines))

    # R2 duplicate id
    code, lines = plan(TARGETS + item("RX-01") + "\n" + item("RX-01", kind="contradiction"))
    chk("r2_duplicate_id", code == 1 and any("R2 duplicate" in ln for ln in lines))

    # R3 — evidential + locked => ERROR (the signature gate)
    code, lines = plan(TARGETS + item("RX-01", mut="locked", rtype="evidential",
                                      blast=["Protected: Ch.12"]))
    chk("r3_evidential_lock", code == 1 and any("R3 evidential-lock" in ln for ln in lines))
    # dramatic + locked is fine (recontextualize for meaning)
    chk("r3_dramatic_lock_ok",
        plan(TARGETS + item("RX-01", mut="locked", rtype="dramatic", blast=["x"]))[0] == 0)
    # evidential + free is fine (unused latent)
    chk("r3_evidential_free_ok",
        plan(TARGETS + item("RX-01", mut="free", rtype="evidential"))[0] == 0)
    # per-id override downgrades R3 to advisory
    ov = "<!-- override: retcon-evidential RX-01 — the 'clue' was never load-bearing -->\n"
    code, lines = plan(TARGETS + ov + item("RX-01", mut="locked", rtype="evidential", blast=["x"]))
    chk("r3_override", code == 0 and any("evidential-lock (override)" in ln for ln in lines))

    # R4 dangling target
    code, lines = plan(TARGETS + item("RX-01", target="T9"))
    chk("r4_dangling_target", code == 1 and any("R4 dangling target" in ln and "T9" in ln for ln in lines))

    # W1 — locked/costly with no blast_radius => advisory, ERROR --strict
    code_w, lines_w = plan(TARGETS + item("RX-01", mut="costly", rtype="dramatic"))
    chk("w1_blast_advisory", code_w == 0 and any("W1 blast unaccounted" in ln for ln in lines_w))
    chk("w1_blast_strict_fails",
        plan(TARGETS + item("RX-01", mut="costly", rtype="dramatic"), strict=True)[0] == 1)
    # free item needs no blast_radius
    chk("w1_free_no_blast_clean", plan(TARGETS + item("RX-01", mut="free"))[0] == 0)

    # W2 — firewall drift (invented quote / ghostwrite directive) => advisory; override silences
    code_w, lines_w = plan(TARGETS + item("RX-01", disp='have her say "I always knew it was you, dear sister"'))
    chk("w2_invented_quote", code_w == 0 and any("W2 firewall drift" in ln for ln in lines_w))
    code_w, lines_w = plan(TARGETS + item("RX-01", iclass="write the line where she confesses"))
    chk("w2_ghostwrite", code_w == 0 and any("W2 firewall drift" in ln for ln in lines_w))
    chk("w2_strict_fails",
        plan(TARGETS + item("RX-01", iclass="write the dialogue for the reveal"), strict=True)[0] == 1)
    ovf = "<!-- override: retcon-firewall RX-01 — quoting the author's own draft line -->\n"
    chk("w2_override",
        plan(TARGETS + ovf + item("RX-01", iclass="write the line where she confesses"))[0] == 0)
    # "draft"/"scene" as revision NOUNS must not false-trigger W2 (verb must govern the object)
    code_w, lines_w = plan(TARGETS + item("RX-01", iclass="recontextualize the draft's opening scene"))
    chk("w2_noun_no_falsetrigger", code_w == 0 and not any("W2 firewall drift" in ln for ln in lines_w))

    # no blocks -> no-op
    chk("no_items_noop", plan("# Retcon Plan\nNothing structured yet.\n")[0] == 0)

    # run-folder + explicit-file resolution
    d = tempfile.mkdtemp()
    made.append(d)
    with open(os.path.join(d, "Proj_Retcon_Plan_run.md"), "w") as fh:
        fh.write("# Retcon Plan\n" + TARGETS + item("RX-01", blast=["Protected: close"]) + "\n")
    chk("run_folder_resolution", run([d])[0] == 0)
    chk("explicit_file_resolution", run([os.path.join(d, "Proj_Retcon_Plan_run.md")])[0] == 0)
    chk("missing_artifact_usage", run([d + "/nope.md"])[0] == 2)

    for d in made:
        shutil.rmtree(d, ignore_errors=True)
    print("Self-test: PASS" if rc["v"] == 0 else "Self-test: FAIL")
    return rc["v"]


def main(argv):
    if "--self-test" in argv:
        return run_self_test()
    args = [a for a in argv[1:] if a != "retcon-plan"]
    strict = "--strict" in args
    paths = [a for a in args if not a.startswith("--")]
    if not paths:
        print("Usage: retcon_plan.py retcon-plan <run_folder|files...> [--strict] | --self-test")
        return 2
    code, lines = run(paths, strict=strict)
    for ln in lines:
        print(ln)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
