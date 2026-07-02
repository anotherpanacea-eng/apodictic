#!/usr/bin/env python3
"""scene-ethics — structural integrity for the Scene-Ethics Plan (Nonfiction Pre-Draft, Increment 4).

`validate.sh scene-ethics <run_folder|files>` shells out here. For narrative nonfiction / memoir that
depicts identifiable real people, the writer plans — before drafting — how each depiction will be
handled ethically: consent status, the handling decision (as-is / anonymize / composite / seek
consent / omit), and the fairness reasoning. Each is an apodictic.scene_ethics.v1 block. This is the
writer's ETHICAL plan, kept distinct from the Legal Risk Register (which owns LEGAL exposure); the
two cross-reference via an optional `legal_ref`. This validator owns the ethics-plan contract and
surfaces unresolved depictions.

  E1 invalid item     a scene_ethics block fails its schema (bad consent_status / handling enum,
                      malformed EP-NN id or legal_ref, missing required field, broken JSON).
  E2 duplicate id     two items share an EP-NN id.
  W1 unresolved depiction  handling=as-is AND consent not yet OBTAINED (not-sought OR sought-pending)
                      AND no fairness_check — an identifiable person depicted as-is with neither
                      consent in hand nor a fairness rationale (pending consent can still be refused,
                      with no fallback) (advisory; ERROR --strict). The signature ethics check.
                      Override (per id): <!-- override: scene-ethics-unresolved EP-NN — <rationale> -->.
  W2 no legal cross-check  an as-is depiction of an identifiable person (consent not not-applicable)
                      with no legal_ref — check it against the Legal Risk Register (advisory; ERROR
                      --strict). Realizes the ethics<->legal cross-reference.

The Firewall holds: the writer makes the ethical decisions; this surfaces what needs one. It is not
ethical adjudication and not legal advice (the Legal Risk Register owns legal exposure). Reuses
apodictic_artifacts. An artifact with no scene_ethics block is a no-op. See docs/nonfiction-pre-draft.md.

  scene_ethics.py scene-ethics <run_folder|files...> [--strict]
  scene_ethics.py --self-test

Exit: 0 clean / WARN-only, 1 ERROR (or WARN under --strict), 2 usage.
"""
import glob
import os
import re
import sys

from override_marker import override_targets  # SSoT: code-span-stripped, boundary-matched override scan

try:
    import apodictic_artifacts as art
except ImportError:
    art = None


def _has_block(text, btype):
    """True if `text` carries a real apodictic:<btype> block (a parsed carrier, not a prose mention).

    Classifying on parsed blocks — not a raw substring — keeps a file that merely *names* the marker
    in prose from being misrouted/skipped (the 2026-06-20 resolver-hardening sweep). Gated by
    validate.sh validator-conventions (M2)."""
    if art is None:
        return ("apodictic:%s" % btype) in (text or "")
    return any(bt == btype for bt, _o, _e in art.parse_blocks(text or ""))

_SCHEMA_ID = "apodictic.scene_ethics.v1"
_PLAN_GLOB = "*_Scene_Ethics_Plan_*.md"
# Override markers naming an EP id route through the shared override_marker SSoT (code spans stripped,
# slug boundary-matched): "<!-- override: scene-ethics-unresolved EP-01 — ... -->".


def _read(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except (OSError, UnicodeDecodeError):
        return None


def _overrides(text, slug):
    """The set of EP-NN ids overridden for `slug` — via the shared SSoT, so a marker quoted inside a
    code span is not honored as a live directive."""
    return {t[0] for t in override_targets(text, slug, r"(EP-[0-9]+)")}


def parse_items(text):
    """[(obj_or_None, schema_errs, index), ...] for each apodictic:scene_ethics block."""
    items = []
    if not text or art is None:
        return items
    schema = art.load_schema(_SCHEMA_ID)
    idx = 0
    for btype, obj, jerr in art.parse_blocks(text):
        if btype != "scene_ethics":
            continue
        idx += 1
        where = "scene_ethics #%d" % idx
        if jerr:
            items.append((None, ["%s: invalid JSON — %s" % (where, jerr)], idx))
            continue
        items.append((obj, art.validate_obj(obj, schema, where), idx))
    return items


def plan(text, strict=False):
    """Run the Scene-Ethics Plan integrity checks. Returns (code, lines)."""
    lines, errs, warns = [], [], []
    items = parse_items(text)
    if not items:
        return 0, ["scene-ethics: no scene_ethics blocks found — nothing to check"]

    # E1 — schema / JSON validity
    for _obj, schema_errs, _idx in items:
        for e in schema_errs:
            errs.append("E1 invalid item: %s" % e)
    valid = [(obj, idx) for obj, schema_errs, idx in items if obj is not None and not schema_errs]

    # E2 — duplicate id
    seen = {}
    for obj, idx in valid:
        seen.setdefault(obj.get("id"), []).append(idx)
    by_id = {}
    for eid, where in sorted(seen.items()):
        if len(where) > 1:
            errs.append("E2 duplicate id: %s appears %d times (ids must be unique)" % (eid, len(where)))
        by_id[eid] = next(o for o, _ in valid if o.get("id") == eid)

    unresolved_overrides = _overrides(text, "scene-ethics-unresolved")
    legalcheck_overrides = _overrides(text, "scene-ethics-legalcheck")
    for eid, obj in sorted(by_id.items()):
        as_is = obj.get("handling") == "as-is"
        consent = obj.get("consent_status")
        has_fairness = bool((obj.get("fairness_check") or "").strip())
        # W1 — unresolved depiction (the ethics signature). An as-is depiction is unresolved while
        # consent is not yet OBTAINED — both not-sought AND sought-pending count (pending can still be
        # refused, with no fallback), unless a fairness rationale is given. (PR #45 review.)
        if (as_is and consent in ("not-sought", "sought-pending") and not has_fairness
                and eid not in unresolved_overrides):
            warns.append("W1 unresolved depiction: %s is depicted as-is with consent %s (not obtained) "
                         "and no fairness rationale — resolve it (obtain consent, add a fairness "
                         "rationale, or choose a fallback: anonymize / composite / seek-consent / "
                         "omit) before drafting" % (eid, consent))
        # W2 — no legal cross-check on an as-is identifiable depiction
        if (as_is and consent != "not-applicable" and not obj.get("legal_ref")
                and eid not in legalcheck_overrides):
            warns.append("W2 no legal cross-check: %s is an as-is depiction with no legal_ref — "
                         "check it against the Legal Risk Register (defamation / privacy / rights)" % eid)

    # Report
    lines.append("scene-ethics: %d depiction(s)%s" % (
        len(items), "" if len(valid) == len(items) else " (%d well-formed)" % len(valid)))
    for obj, _idx in valid:
        lines.append("  %-7s consent=%-13s handling=%s" % (obj.get("id"), obj.get("consent_status"),
                                                           obj.get("handling")))
    for e in errs:
        lines.append("  ERROR: %s" % e)
    for w in warns:
        lines.append("  %s: %s" % ("ERROR (--strict)" if strict else "WARN", w))

    if errs or (strict and warns):
        lines.append("scene-ethics: FAIL (%d error(s)%s)"
                     % (len(errs), ", %d strict warn(s)" % len(warns) if (strict and warns) else ""))
        return 1, lines
    if warns:
        lines.append("WARN: scene-ethics: %d advisory gap(s) — see W1/W2 above" % len(warns))
    else:
        lines.append("scene-ethics: PASS (ethics-plan contract + resolved depictions)")
    return 0, lines


# ---------------------------------------------------------------- resolution

def _newest(paths):
    return max(paths, key=os.path.getmtime) if paths else None


def resolve(paths):
    if len(paths) == 1 and os.path.isdir(paths[0]):
        return _newest(glob.glob(os.path.join(paths[0], _PLAN_GLOB)))
    for p in paths:
        if _has_block(_read(p) or "", "scene_ethics"):
            return p
    return paths[0] if paths else None


def run(paths, strict=False):
    path = resolve(paths)
    if not path:
        return 2, ["scene-ethics: no Scene-Ethics Plan artifact found (need a *_Scene_Ethics_Plan_*.md "
                   "or a file with apodictic:scene_ethics blocks)"]
    text = _read(path)
    if text is None:
        return 2, ["scene-ethics: cannot read %s" % path]
    return plan(text, strict=strict)


# ---------------------------------------------------------------- self-test

def run_self_test():
    import json as _j
    rc = {"v": 0}

    def chk(name, cond):
        print("  %s: %s" % (name, "OK" if cond else "FAIL"))
        if not cond:
            rc["v"] = 1

    # non-UTF8 artifact: _read must degrade to the unreadable path (None), never
    # a traceback (the disposition_check adjacent-exception class, swept repo-wide)
    import tempfile as _tf
    _fd, _nu = _tf.mkstemp(suffix=".md")
    with os.fdopen(_fd, "wb") as _fh:
        _fh.write(b"\xff\xfenot utf-8\xff")
    chk("non_utf8_read_returns_none", _read(_nu) is None)
    os.unlink(_nu)

    def item(eid, subject="the narrator's former manager (named)", depiction="portrayed making a remark",
             consent="not-sought", handling="anonymize", fairness=None, legal=None):
        obj = {"schema": _SCHEMA_ID, "id": eid, "subject": subject, "depiction": depiction,
               "consent_status": consent, "handling": handling}
        if fairness is not None:
            obj["fairness_check"] = fairness
        if legal is not None:
            obj["legal_ref"] = legal
        return "<!-- apodictic:scene_ethics\n%s\n-->" % _j.dumps(obj)

    # clean: anonymized (mitigated) -> no W1/W2
    chk("clean_anonymize", plan(item("EP-01", handling="anonymize"))[0] == 0)
    # no block -> no-op
    chk("no_items_noop", plan("# notes\nno depictions\n")[0] == 0)

    # E1 — bad enum / id / missing field / bad legal_ref / JSON
    chk("e1_bad_consent", plan(item("EP-01", consent="maybe"))[0] == 1)
    chk("e1_bad_handling", plan(item("EP-01", handling="publish"))[0] == 1)
    chk("e1_bad_id", plan(item("EP-1"))[0] == 1)
    chk("e1_bad_legal_ref", plan(item("EP-01", legal="LR1"))[0] == 1)
    chk("e1_missing_field", plan(item("EP-01").replace('"depiction"', '"depic"'))[0] == 1)
    code, lines = plan('<!-- apodictic:scene_ethics\n{"schema":"apodictic.scene_ethics.v1"\n-->')
    chk("e1_bad_json", code == 1 and any("E1 invalid item" in ln for ln in lines))

    # E2 — duplicate id
    code, lines = plan(item("EP-01", handling="omit") + "\n" + item("EP-01", handling="composite"))
    chk("e2_duplicate_id", code == 1 and any("E2 duplicate" in ln for ln in lines))

    # W1 — unresolved depiction: as-is + not-sought + no fairness => advisory; ERROR --strict; override
    code, lines = plan(item("EP-01", handling="as-is", consent="not-sought"))
    chk("w1_unresolved", code == 0 and any("W1 unresolved depiction" in ln for ln in lines))
    chk("w1_unresolved_strict_fails",
        plan(item("EP-01", handling="as-is", consent="not-sought"), strict=True)[0] == 1)
    # a fairness rationale resolves W1 (but W2 still wants a legal_ref — provide one to be clean)
    chk("w1_fairness_resolves",
        not any("W1" in ln for ln in plan(item("EP-01", handling="as-is", consent="not-sought",
                                               fairness="shown in full context with the subject's rationale",
                                               legal="LR-01"))[1]))
    # consent obtained resolves W1
    chk("w1_consent_resolves",
        not any("W1" in ln for ln in plan(item("EP-01", handling="as-is", consent="obtained", legal="LR-02"))[1]))
    # sought-pending is NOT resolved for an as-is depiction (PR #45 review) — even with a legal_ref
    # clearing W2, W1 must still fire (consent can be refused, with no fallback)
    code, lines = plan(item("EP-01", handling="as-is", consent="sought-pending", legal="LR-01"))
    chk("w1_pending_unresolved", code == 0 and any("W1 unresolved depiction" in ln for ln in lines))
    chk("w1_pending_strict_fails",
        plan(item("EP-01", handling="as-is", consent="sought-pending", legal="LR-01"), strict=True)[0] == 1)
    # a fairness rationale resolves a pending as-is depiction
    chk("w1_pending_fairness_resolves",
        not any("W1" in ln for ln in plan(item("EP-01", handling="as-is", consent="sought-pending",
                                               fairness="context + the subject's rationale shown", legal="LR-02"))[1]))
    ov = "<!-- override: scene-ethics-unresolved EP-01 — public-record quote, fairness in the draft -->\n"
    chk("w1_override",
        not any("W1" in ln for ln in plan(ov + item("EP-01", handling="as-is", consent="not-sought", legal="LR-03"))[1]))

    # W2 — as-is identifiable depiction with no legal_ref => advisory; override; cleared by legal_ref
    code, lines = plan(item("EP-01", handling="as-is", consent="obtained"))   # resolved ethically, but no legal_ref
    chk("w2_no_legal_ref", code == 0 and any("W2 no legal cross-check" in ln for ln in lines))
    chk("w2_legal_ref_clears",
        not any("W2" in ln for ln in plan(item("EP-01", handling="as-is", consent="obtained", legal="LR-01"))[1]))
    # not-applicable consent (public figure acting publicly) as-is needs no legal cross-check
    chk("w2_not_applicable_ok",
        not any("W2" in ln for ln in plan(item("EP-01", handling="as-is", consent="not-applicable"))[1]))
    chk("w2_strict_fails",
        plan(item("EP-01", handling="as-is", consent="obtained"), strict=True)[0] == 1)
    # anonymized handling needs no legal cross-check (mitigated)
    chk("w2_anonymize_no_w2",
        not any("W2" in ln for ln in plan(item("EP-01", handling="anonymize"))[1]))

    # run-folder + explicit-file resolution
    import tempfile
    import shutil
    d = tempfile.mkdtemp()
    try:
        p = os.path.join(d, "Proj_Scene_Ethics_Plan_run.md")
        with open(p, "w", encoding="utf-8", newline="") as fh:
            fh.write("# Scene Ethics Plan\n" + item("EP-01", handling="anonymize") + "\n")
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
    args = [a for a in argv[1:] if a != "scene-ethics"]
    strict = "--strict" in args
    paths = [a for a in args if not a.startswith("--")]
    if not paths:
        print("Usage: scene_ethics.py scene-ethics <run_folder|files...> [--strict] | --self-test")
        return 2
    code, lines = run(paths, strict=strict)
    for ln in lines:
        print(ln)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
