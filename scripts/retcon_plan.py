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

Door-B Selection step (F1) — ranked candidate latent readings as apodictic.retcon_reading.v1 blocks:
  R5 invalid reading  a retcon_reading block fails its schema, or `scores` is missing one of the five
                      named 1-5 dimensions / carries an out-of-range value (range enforced in code,
                      since the subset schema checker can't express nested required keys or bounds).
  R6 duplicate id     two readings share a CR-NN id.
  R7 dangling target  a reading's implied_targets names a target not declared in '## Retcon Targets'.
  W3 uncosted reading a surfaced reading carries no coincidence_note — the non-insane-coincidence-rate
                      over-fitting guard (advisory; ERROR --strict). The signature F1 check.
  W4 unpruned shortlist  more than 3 candidate readings (the Selection step returns the top 1-3).

F3 (Pass-8 auto-seeding): a retcon_item may carry an optional `source` finding-ref (F-<ORIGIN>-<NN>,
primarily a Pass-8 Reveal-Economy finding) recording what it was seeded from. Its format is checked
here (R1, via the schema), shown in the item line, and resolved against the ledger by finding-trace
(E6 dangling retcon source) — the cross-artifact provenance check.

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


def _has_block(text, btype):
    """True if `text` carries a real apodictic:<btype> block (a parsed carrier, not a prose mention).

    Classifying on parsed blocks — not a raw substring — keeps a file that merely *names* the marker
    in prose from being misrouted/skipped (the 2026-06-20 resolver-hardening sweep). Gated by
    validate.sh validator-conventions (M2)."""
    if art is None:
        return ("apodictic:%s" % btype) in (text or "")
    return any(bt == btype for bt, _o, _e in art.parse_blocks(text or ""))

_SCHEMA_ID = "apodictic.retcon_item.v1"
_READING_SCHEMA_ID = "apodictic.retcon_reading.v1"
_PLAN_GLOB = "*_Retcon_Plan_*.md"
_MUTABLE_COSTLY = ("locked", "costly")
# The Door-B Selection rubric (F1): five named dimensions, integer 1-5, higher is better.
# coincidence_resistance: 5 = no forced coincidences; 1 = rubber-reality over-fit (the essay's
# failure mode). The subset schema checker can't express nested required keys or numeric bounds,
# so dimension completeness + range live here in code (part of R5), as the R3 gate does.
_SCORE_DIMS = ("canon_coherence", "payoff_density", "agency_preservation",
               "genre_fit", "coincidence_resistance")
_SCORE_MIN, _SCORE_MAX = 1, 5

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
# Content-invention by specifying what happens in a NEW unit: "add/insert a scene where <events>".
# The "where <events>" clause is the tell (it names the content); a content-ADDING verb is required,
# so "remove/cut the scene where …" (legitimate classes) do not match.
_INVENTED_SCENE_RE = re.compile(
    r"\b(?:add|create|insert|write|draft|put\s+in)\s+(?:a|an|the|another|some)\s+"
    r"(?:scene|beat|moment|flashback|line|exchange|chapter|passage|paragraph)\s+where\b",
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


def _score_errors(obj, where):
    """The five-dimension completeness + 1-5 range checks the subset schema checker cannot express
    (nested required keys, numeric bounds). Part of R5. Returns a list of error strings."""
    errs = []
    if not isinstance(obj, dict):
        return errs  # a non-dict block is already reported by validate_obj ('expected a JSON object')
    scores = obj.get("scores")
    if not isinstance(scores, dict):
        return errs  # a non-object `scores` is already reported by the schema's type:object check
    for dim in _SCORE_DIMS:
        if dim not in scores:
            errs.append("%s: scores missing '%s' (need all of: %s)"
                        % (where, dim, ", ".join(_SCORE_DIMS)))
            continue
        v = scores[dim]
        if not isinstance(v, int) or isinstance(v, bool):
            errs.append("%s: scores.%s=%r must be an integer %d-%d"
                        % (where, dim, v, _SCORE_MIN, _SCORE_MAX))
        elif not (_SCORE_MIN <= v <= _SCORE_MAX):
            errs.append("%s: scores.%s=%d out of range %d-%d"
                        % (where, dim, v, _SCORE_MIN, _SCORE_MAX))
    return errs


def parse_readings(text):
    """[(obj_or_None, schema_errs, index), ...] for each apodictic:retcon_reading block.
    Door-B Selection step (F1): one scored candidate latent reading per block."""
    readings = []
    if not text or art is None:
        return readings
    schema = art.load_schema(_READING_SCHEMA_ID)
    idx = 0
    for btype, obj, jerr in art.parse_blocks(text):
        if btype != "retcon_reading":
            continue
        idx += 1
        where = "retcon_reading #%d" % idx
        if jerr:
            readings.append((None, ["%s: invalid JSON — %s" % (where, jerr)], idx))
            continue
        errs = art.validate_obj(obj, schema, where) + _score_errors(obj, where)
        readings.append((obj, errs, idx))
    return readings


def _score_total(obj):
    """Sum of the five Selection dimensions (max 25). Higher = a stronger reading."""
    s = obj.get("scores") or {}
    return sum(s[d] for d in _SCORE_DIMS
               if isinstance(s.get(d), int) and not isinstance(s.get(d), bool))


def plan(text, strict=False):
    """Run the Retcon Plan integrity checks. Returns (code, lines)."""
    lines, errs, warns = [], [], []
    items = parse_items(text)
    readings = parse_readings(text)
    if not items and not readings:
        return 0, ["retcon-plan: no retcon_item or retcon_reading blocks found — nothing to check"]

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
        if ((_INVENTED_QUOTE_RE.search(blob) or _GHOSTWRITE_RE.search(blob)
             or _INVENTED_SCENE_RE.search(blob)) and rid not in fw_overrides):
            warns.append("W2 firewall drift: %s reads like invented prose, not an intervention "
                         "class — plan the class; the author writes the tissue" % rid)

    # ---- Door-B Selection step (F1): ranked candidate readings ----
    # R5 — schema / JSON / score-rubric validity (per reading)
    for _obj, reading_errs, _idx in readings:
        for e in reading_errs:
            errs.append("R5 invalid reading: %s" % e)

    valid_readings = [(o, i) for o, rerrs, i in readings if o is not None and not rerrs]

    # R6 — duplicate reading id
    seen_r = {}
    for obj, idx in valid_readings:
        seen_r.setdefault(obj.get("id"), []).append(idx)
    reading_by_id = {}
    for crid, where in sorted(seen_r.items()):
        if len(where) > 1:
            errs.append("R6 duplicate reading id: %s appears %d times (ids must be unique)"
                        % (crid, len(where)))
        reading_by_id[crid] = next(o for o, _ in valid_readings if o.get("id") == crid)

    for crid, obj in sorted(reading_by_id.items()):
        # R7 — dangling implied target (mirrors R4; implied_targets lists DECLARED targets)
        for tid in (obj.get("implied_targets") or []):
            if tid not in targets:
                errs.append("R7 dangling reading target: %s.implied_targets has %s, not declared in "
                            "'## Retcon Targets'" % (crid, tid))
        # W3 — uncosted reading (the non-insane-coincidence-rate guard; the signature F1 check)
        if not (obj.get("coincidence_note") or "").strip():
            warns.append("W3 uncosted reading: %s carries no coincidence_note — show which incidental "
                         "details the reading makes load-bearing (the over-fitting guard)" % crid)

    # W4 — unpruned shortlist (the Selection step returns the top 1-3, not a flat menu)
    if len(valid_readings) > 3:
        warns.append("W4 unpruned shortlist: %d candidate readings surfaced — the Selection step "
                     "returns the top 1-3; prune to the ranked shortlist" % len(valid_readings))

    # Report
    head = "retcon-plan: %d item(s)%s; %d target(s) declared" % (
        len(items), "" if len(valid) == len(items) else " (%d well-formed)" % len(valid), len(targets))
    if readings:
        head += "; %d reading(s)%s" % (
            len(readings),
            "" if len(valid_readings) == len(readings) else " (%d well-formed)" % len(valid_readings))
    lines.append(head)
    for obj, _idx in valid:
        lines.append("  %-7s target=%-3s kind=%-14s mut=%-6s type=%s%s"
                     % (obj.get("id"), obj.get("target_id"), obj.get("kind"),
                        obj.get("mutability"), obj.get("retcon_type"),
                        "  source=%s" % obj.get("source") if obj.get("source") else ""))
    # Ranked candidate readings: highest score total first (the Selection step, made visible)
    for obj, _idx in sorted(valid_readings, key=lambda t: (-_score_total(t[0]), t[0].get("id"))):
        s = obj["scores"]
        lines.append("  %-7s score=%2d/25 (coh=%d pay=%d agy=%d gen=%d coin=%d)%s"
                     % (obj.get("id"), _score_total(obj), s["canon_coherence"], s["payoff_density"],
                        s["agency_preservation"], s["genre_fit"], s["coincidence_resistance"],
                        " -> %s" % ",".join(obj["implied_targets"]) if obj.get("implied_targets") else ""))
    for e in errs:
        lines.append("  ERROR: %s" % e)
    for w in warns:
        lines.append("  %s: %s" % ("ERROR (--strict)" if strict else "WARN", w))

    if errs or (strict and warns):
        lines.append("retcon-plan: FAIL (%d error(s)%s)"
                     % (len(errs), ", %d strict warn(s)" % len(warns) if (strict and warns) else ""))
        return 1, lines
    if warns:
        lines.append("WARN: retcon-plan: %d advisory gap(s) — see W1-W4 above" % len(warns))
    else:
        lines.append("retcon-plan: PASS (commitment-budget + fair-play + target integrity%s)"
                     % (" + ranked selection" if readings else ""))
    return 0, lines


# ---------------------------------------------------------------- resolution

def _newest(paths):
    return max(paths, key=os.path.getmtime) if paths else None


def resolve(paths):
    if len(paths) == 1 and os.path.isdir(paths[0]):
        return _newest(glob.glob(os.path.join(paths[0], _PLAN_GLOB)))
    for p in paths:
        body = _read(p) or ""
        if _has_block(body, "retcon_item") or _has_block(body, "retcon_reading"):
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
             blast=None, locations=None, source=None):
        obj = {"schema": _SCHEMA_ID, "id": rid, "target_id": target, "kind": kind,
               "mutability": mut, "retcon_type": rtype, "intervention_class": iclass,
               "disposition": disp}
        if blast is not None:
            obj["blast_radius"] = blast
        if locations is not None:
            obj["locations"] = locations
        if source is not None:
            obj["source"] = source
        return "<!-- apodictic:retcon_item\n%s\n-->" % _j.dumps(obj)

    def reading(crid, scores=None, note="treats one incidental detail as load-bearing",
                implied=None, label="the sister was complicit all along"):
        obj = {"schema": _READING_SCHEMA_ID, "id": crid, "reading": label,
               "scores": scores if scores is not None else {
                   "canon_coherence": 4, "payoff_density": 3, "agency_preservation": 4,
                   "genre_fit": 4, "coincidence_resistance": 4}}
        if note is not None:
            obj["coincidence_note"] = note
        if implied is not None:
            obj["implied_targets"] = implied
        return "<!-- apodictic:retcon_reading\n%s\n-->" % _j.dumps(obj)

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
    # "add a scene where <events>" — the documented content-invention form (PR #38 review P2)
    code_w, lines_w = plan(TARGETS + item("RX-01", iclass="add a scene where Maya confesses to hiding the letter"))
    chk("w2_add_scene_where", code_w == 0 and any("W2 firewall drift" in ln for ln in lines_w))
    chk("w2_add_scene_strict_fails",
        plan(TARGETS + item("RX-01", iclass="insert a beat where she admits it"), strict=True)[0] == 1)
    # removing/cutting an existing scene is a legit class — must NOT trigger
    code_w, lines_w = plan(TARGETS + item("RX-02", target="T2", iclass="cut the scene where she lies"))
    chk("w2_remove_scene_no_falsetrigger",
        code_w == 0 and not any("W2 firewall drift" in ln for ln in lines_w))

    # ---- Door-B Selection step (F1): candidate readings ----
    # clean single reading (all 5 dims, note present); a pure Door-B plan (no items) is valid
    chk("reading_clean", plan(TARGETS + reading("CR-01"))[0] == 0)

    # R5 — bad id / missing dim / out-of-range / non-int / bad JSON
    chk("r5_bad_id", plan(TARGETS + reading("CR-1"))[0] == 1)
    chk("r5_missing_dim",
        plan(TARGETS + reading("CR-01", scores={"canon_coherence": 4, "payoff_density": 3,
             "agency_preservation": 4, "genre_fit": 4}))[0] == 1)
    chk("r5_out_of_range",
        plan(TARGETS + reading("CR-01", scores={"canon_coherence": 7, "payoff_density": 3,
             "agency_preservation": 4, "genre_fit": 4, "coincidence_resistance": 4}))[0] == 1)
    chk("r5_non_int",
        plan(TARGETS + reading("CR-01", scores={"canon_coherence": "hi", "payoff_density": 3,
             "agency_preservation": 4, "genre_fit": 4, "coincidence_resistance": 4}))[0] == 1)
    code, lines = plan(TARGETS + '<!-- apodictic:retcon_reading\n{"schema":"apodictic.retcon_reading.v1"\n-->')
    chk("r5_bad_json", code == 1 and any("R5 invalid reading" in ln for ln in lines))

    # R6 — duplicate reading id
    code, lines = plan(TARGETS + reading("CR-01") + "\n" + reading("CR-01", label="other"))
    chk("r6_duplicate_id", code == 1 and any("R6 duplicate reading id" in ln for ln in lines))

    # R7 — dangling implied target (mirrors R4); a declared target is the legit Door-B->Door-A handoff
    code, lines = plan(TARGETS + reading("CR-01", implied=["T9"]))
    chk("r7_dangling_target", code == 1 and any("R7 dangling reading target" in ln and "T9" in ln for ln in lines))
    chk("r7_declared_target_ok", plan(TARGETS + reading("CR-01", implied=["T1"]))[0] == 0)

    # W3 — uncosted reading (no/empty coincidence_note) => advisory, ERROR --strict (the signature check)
    code_w, lines_w = plan(TARGETS + reading("CR-01", note=None))
    chk("w3_uncosted_advisory", code_w == 0 and any("W3 uncosted reading" in ln for ln in lines_w))
    chk("w3_uncosted_strict_fails", plan(TARGETS + reading("CR-01", note=None), strict=True)[0] == 1)
    code_w, lines_w = plan(TARGETS + reading("CR-01", note="   "))
    chk("w3_empty_note_triggers", code_w == 0 and any("W3 uncosted reading" in ln for ln in lines_w))

    # W4 — unpruned shortlist (>3 readings) => advisory, ERROR --strict; exactly 3 is clean
    four = "".join(reading("CR-0%d" % n) for n in range(1, 5))
    code_w, lines_w = plan(TARGETS + four)
    chk("w4_unpruned_advisory", code_w == 0 and any("W4 unpruned shortlist" in ln for ln in lines_w))
    chk("w4_unpruned_strict_fails", plan(TARGETS + four, strict=True)[0] == 1)
    chk("w4_three_ok", plan(TARGETS + "".join(reading("CR-0%d" % n) for n in range(1, 4)))[0] == 0)

    # ranked display: highest score total printed first (the Selection step made visible)
    hi = reading("CR-01", scores={"canon_coherence": 5, "payoff_density": 5, "agency_preservation": 5,
                                  "genre_fit": 5, "coincidence_resistance": 5})
    lo = reading("CR-02", scores={"canon_coherence": 2, "payoff_density": 2, "agency_preservation": 2,
                                  "genre_fit": 2, "coincidence_resistance": 2})
    _c, dlines = plan(TARGETS + lo + hi)
    order = [ln for ln in dlines if "score=" in ln]
    chk("ranked_display_order", len(order) == 2 and "CR-01" in order[0] and "CR-02" in order[1])

    # items + readings compose cleanly in one plan
    chk("items_and_readings_clean",
        plan(TARGETS + item("RX-01") + reading("CR-01", implied=["T1"]))[0] == 0)

    # ---- F3: Pass-8 source provenance on a retcon item ----
    # a well-formed source is clean and shown in the item line
    code, lines = plan(TARGETS + item("RX-01", source="F-P8-03"))
    chk("f3_source_clean", code == 0 and any("source=F-P8-03" in ln for ln in lines))
    # a malformed source (one-digit suffix) fails its schema pattern -> R1
    chk("f3_source_malformed_r1", plan(TARGETS + item("RX-01", source="F-P8-3"))[0] == 1)

    # no blocks -> no-op
    chk("no_items_noop", plan("# Retcon Plan\nNothing structured yet.\n")[0] == 0)

    # run-folder + explicit-file resolution
    d = tempfile.mkdtemp()
    made.append(d)
    with open(os.path.join(d, "Proj_Retcon_Plan_run.md"), "w", encoding="utf-8", newline="") as fh:
        fh.write("# Retcon Plan\n" + TARGETS + item("RX-01", blast=["Protected: close"]) + "\n")
    chk("run_folder_resolution", run([d])[0] == 0)
    chk("explicit_file_resolution", run([os.path.join(d, "Proj_Retcon_Plan_run.md")])[0] == 0)
    chk("missing_artifact_usage", run([d + "/nope.md"])[0] == 2)

    for d in made:
        shutil.rmtree(d, ignore_errors=True)
    # regression: a non-dict retcon_reading payload must not crash _score_errors (2026-06-20 sweep)
    chk("crash_nondict_reading", plan('<!-- apodictic:retcon_reading\n"juststring"\n-->')[0] == 1)
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
