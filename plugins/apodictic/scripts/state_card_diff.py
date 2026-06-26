#!/usr/bin/env python3
"""state-card-diff — cross-revision coherence for the Retcon Planning State Card (F2).

The State Card (Retcon Planning, Increment 1) compresses what a draft has committed to: the
controlling-idea hypothesis, active promises, unresolved tensions, and forbidden contradictions.
F2 promotes it to a standalone, rolling, project-root artifact ([Project]_State_Card_[runlabel].md)
carrying one apodictic.state_card.v1 block per round, diff'd across revision rounds (the
Pass-10-class rolling-structured-artifact pattern, modeled on timeline-diff). Tracked elements
(promises/tensions/contradictions) share a stable, kind-agnostic SE-NN id, so the SAME element is
followed across rounds even when it changes kind — the cross-revision-traceability lesson (don't
depend on prose matching).

Single-card checks (one file):
  S1 invalid card     a state_card block fails its schema, or a tracked element lacks a well-formed
                      'SE-NN: <text>' id prefix (the prefix format is enforced in code, since the
                      subset schema checker can't express it).
  S2 duplicate id     two tracked elements in one card share an SE-NN id (one namespace across
                      promises / tensions / contradictions).

Cross-round checks (prior + current — pair mode requires a parseable card on BOTH sides):
  S0 missing card     in a two-file pair diff, either side has no parseable state_card block — a hard
                      ERROR, so a wrong/misnamed file can never silently bypass the cross-round checks.
  S3 round backwards  current.round < prior.round (a stale or misordered diff).
  S4 promise->contradiction   an SE-NN that was an active_promise in prior is a
                      forbidden_contradiction in current — the draft has reasoned past a coherence
                      break. The signature F2 check.
                      Override: <!-- override: state-card-transition SE-NN — <reason> -->.
  W1 dropped promise  an SE-NN active_promise in prior is gone from current entirely (silently
                      dropped, not resolved). Advisory; ERROR --strict.
                      Override: <!-- override: state-card-drop SE-NN — <reason> -->.
  W2 idea shift       controlling_idea changed between rounds (reframing is legitimate but worth
                      surfacing). Advisory; ERROR --strict.
                      Override: <!-- override: state-card-idea-shift — <reason> -->.
  W3 same-round edit  current.round == prior.round but content differs (bump the round?).
                      Advisory; ERROR --strict.

Reuses apodictic_artifacts (block grammar + schema engine). Each artifact is optional; an
empty/absent one is a no-op. See docs/retcon-planning.md.

  state_card_diff.py state-card-diff <current>             # validate one card (S1-S2)
  state_card_diff.py state-card-diff <prior> <current>     # validate + cross-round diff (S1-W3)
  state_card_diff.py --self-test

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

_SCHEMA_ID = "apodictic.state_card.v1"
_CARD_GLOB = "*_State_Card_*.md"
# The three tracked lists share one SE-NN id namespace (kind-agnostic), so an element keeps its id
# when it changes kind across rounds. likely_next_pressures is ephemeral (no ids, not tracked).
_TRACKED = ("active_promises", "unresolved_tensions", "forbidden_contradictions")
_KIND = {"active_promises": "promise", "unresolved_tensions": "tension",
         "forbidden_contradictions": "contradiction"}
# A tracked element: "SE-01: the dual-POV will converge".
_ELEMENT_RE = re.compile(r"^\s*(SE-[0-9]{2,})\s*:\s*(.+\S)\s*$")
# Override markers route through the shared override_marker SSoT (code spans stripped, slug
# boundary-matched): a per-element "<!-- override: <slug> SE-01 — ... -->" (parsed via the SE target
# in _overrides) and the id-less controlling-idea-shift "<!-- override: state-card-idea-shift -->"
# (the presence form of override_targets).


def _read(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return None


def _norm(s):
    return re.sub(r"\s+", " ", (s or "").strip()).lower()


def _overrides(text, slug):
    """The set of SE-NN ids overridden for `slug` — via the shared SSoT, so a marker quoted inside a
    code span is not honored as a live directive."""
    return {t[0] for t in override_targets(text, slug, r"(SE-[0-9]+)")}


def parse_card(text):
    """(obj_or_None, schema_errs) for the FIRST apodictic:state_card block ('' errs if absent)."""
    if not text or art is None:
        return None, []
    schema = art.load_schema(_SCHEMA_ID)
    for btype, obj, jerr in art.parse_blocks(text):
        if btype != "state_card":
            continue
        if jerr:
            return None, ["invalid JSON — %s" % jerr]
        return obj, art.validate_obj(obj, schema, "state_card")
    return None, []


def card_elements(obj):
    """Map SE-id -> (kind, normalized_text) over the tracked lists. Returns (elems, fmt_errs,
    dup_errs): fmt_errs (S1) for entries lacking a well-formed SE-NN prefix, dup_errs (S2) for a
    repeated id within one card (one namespace across the three lists)."""
    elems, fmt_errs, seen = {}, [], {}
    for field in _TRACKED:
        val = obj.get(field)
        if not isinstance(val, list):
            continue  # a non-array field is already reported by the schema's type:array check
        for raw in val:
            if not isinstance(raw, str):
                continue  # the schema's items:string check already flagged a non-string entry
            m = _ELEMENT_RE.match(raw)
            if not m:
                fmt_errs.append("%s entry %r lacks an 'SE-NN: <text>' id prefix" % (field, raw))
                continue
            sid, txt = m.group(1), m.group(2)
            seen.setdefault(sid, []).append(field)
            elems[sid] = (_KIND[field], _norm(txt))
    dup_errs = ["%s appears %d times in one card (ids must be unique)" % (sid, len(where))
                for sid, where in sorted(seen.items()) if len(where) > 1]
    return elems, fmt_errs, dup_errs


def check_one(text):
    """Single-card S1+S2. Returns (errs, elems, obj)."""
    obj, schema_errs = parse_card(text)
    errs = ["S1 invalid card: %s" % e for e in schema_errs]
    if not isinstance(obj, dict):
        return errs, {}, None  # None or a non-dict payload (the latter already an S1 'expected a JSON object')
    elems, fmt_errs, dup_errs = card_elements(obj)
    errs += ["S1 invalid card: %s" % e for e in fmt_errs]
    errs += ["S2 duplicate id: %s" % e for e in dup_errs]
    return errs, elems, obj


def _finish(lines, errs, warns, strict, ok_msg):
    for e in errs:
        lines.append("  ERROR: %s" % e)
    for w in warns:
        lines.append("  %s: %s" % ("ERROR (--strict)" if strict else "WARN", w))
    if errs or (strict and warns):
        lines.append("state-card-diff: FAIL (%d error(s)%s)"
                     % (len(errs), ", %d strict warn(s)" % len(warns) if (strict and warns) else ""))
        return 1, lines
    if warns:
        lines.append("WARN: state-card-diff: %d advisory gap(s) — see W1-W3 above" % len(warns))
    else:
        lines.append("state-card-diff: PASS (%s)" % ok_msg)
    return 0, lines


def validate_single(text, strict=False):
    """One-card mode: schema + id integrity only (no cross-round diff)."""
    errs, elems, obj = check_one(text)
    if obj is None and not errs:
        return 0, ["state-card-diff: no state_card block found — nothing to check"]
    lines = ["state-card-diff: round=%s (%d tracked element(s)); single-card validate"
             % (obj.get("round") if obj else "?", len(elems))]
    return _finish(lines, errs, warns=[], strict=strict, ok_msg="schema + id integrity")


def diff_cards(prior_text, current_text, strict=False):
    """Two-card mode: single-card checks on each, then the cross-round diff."""
    lines, errs, warns = [], [], []
    p_errs, p_elems, p_obj = check_one(prior_text)
    c_errs, c_elems, c_obj = check_one(current_text)
    errs += ["[prior] " + e for e in p_errs]
    errs += ["[current] " + e for e in c_errs]

    if p_obj is None and c_obj is None and not errs:
        return 0, ["state-card-diff: no state_card blocks found — nothing to check"]

    # Pair mode (two explicit files): BOTH sides must carry a parseable state_card. A missing card on
    # either side is an ERROR (S0), not a silent single-card pass — otherwise a wrong/misnamed file
    # would bypass the cross-round checks (S3/S4/W1-W3) entirely. (PR #41 review.)
    if p_obj is None and not p_errs:
        errs.append("[prior] S0 missing card: no parseable state_card block — a pair diff needs a "
                    "card on both sides")
    if c_obj is None and not c_errs:
        errs.append("[current] S0 missing card: no parseable state_card block — a pair diff needs a "
                    "card on both sides")
    if p_obj is None or c_obj is None:
        lines.append("state-card-diff: pair diff requires a parseable state_card on both sides — "
                     "cross-round checks cannot run")
        return _finish(lines, errs, warns, strict, ok_msg="")

    pr, cr = p_obj.get("round"), c_obj.get("round")
    rounds_known = isinstance(pr, int) and isinstance(cr, int)

    # S3 — round backwards
    if rounds_known and cr < pr:
        errs.append("S3 round backwards: current round %d < prior round %d (stale or misordered diff)"
                    % (cr, pr))

    tr_over = _overrides(current_text, "state-card-transition")
    drop_over = _overrides(current_text, "state-card-drop")

    kept = added = 0
    for sid in sorted(c_elems):
        ckind = c_elems[sid][0]
        if sid in p_elems:
            kept += 1
            # S4 — promise -> contradiction (the signature transition)
            if p_elems[sid][0] == "promise" and ckind == "contradiction":
                if sid in tr_over:
                    warns.append("S4 promise->contradiction (override): %s flipped from active promise "
                                 "to forbidden contradiction (marker present)" % sid)
                else:
                    errs.append("S4 promise->contradiction: %s was an active promise and is now a "
                                "forbidden contradiction — the draft has reasoned past a coherence "
                                "break. Resolve it, or override: "
                                "<!-- override: state-card-transition %s — <reason> -->" % (sid, sid))
        else:
            added += 1

    # W1 — dropped promise (a prior active promise gone entirely from current)
    for sid in sorted(p_elems):
        if p_elems[sid][0] == "promise" and sid not in c_elems and sid not in drop_over:
            warns.append("W1 dropped promise: %s was an active promise in prior and is gone from "
                         "current — resolved, or silently dropped? Override: "
                         "<!-- override: state-card-drop %s — <reason> -->" % (sid, sid))

    # W2 — controlling-idea shift
    if _norm(p_obj.get("controlling_idea")) != _norm(c_obj.get("controlling_idea")):
        if override_targets(current_text, "state-card-idea-shift"):
            warns.append("W2 idea shift (override): controlling_idea changed between rounds (marker present)")
        else:
            warns.append("W2 idea shift: controlling_idea changed between rounds — reframing is "
                         "legitimate, but confirm it is intentional. Override: "
                         "<!-- override: state-card-idea-shift — <reason> -->")

    # W3 — same-round content change
    if rounds_known and pr == cr and (
            p_elems != c_elems
            or _norm(p_obj.get("controlling_idea")) != _norm(c_obj.get("controlling_idea"))):
        warns.append("W3 same-round edit: prior and current both declare round %d but differ — "
                     "bump the round when the card changes" % cr)

    resolved = sum(1 for sid in p_elems
                   if p_elems[sid][0] == "tension" and sid not in c_elems)
    lines.insert(0, "state-card-diff: round %s (%d elems) -> round %s (%d elems); "
                 "%d kept, %d added, %d resolved-tension"
                 % (pr, len(p_elems), cr, len(c_elems), kept, added, resolved))
    return _finish(lines, errs, warns, strict, ok_msg="cross-round coherence")


# ---------------------------------------------------------------- resolution

def _newest(paths):
    return max(paths, key=os.path.getmtime) if paths else None


def resolve(paths):
    """-> (prior_path_or_None, current_path). A lone dir resolves to its newest card."""
    if len(paths) == 1 and os.path.isdir(paths[0]):
        return None, _newest(glob.glob(os.path.join(paths[0], _CARD_GLOB)))
    if len(paths) >= 2:
        return paths[0], paths[1]
    if len(paths) == 1:
        return None, paths[0]
    return None, None


def run(paths, strict=False):
    prior, current = resolve(paths)
    if not current:
        return 2, ["state-card-diff: no State Card artifact found (need a *_State_Card_*.md, an "
                   "explicit file, or a <prior> <current> pair)"]
    cur_text = _read(current)
    if cur_text is None:
        return 2, ["state-card-diff: cannot read %s" % current]
    if prior is None:
        return validate_single(cur_text, strict=strict)
    prior_text = _read(prior)
    if prior_text is None:
        return 2, ["state-card-diff: cannot read %s" % prior]
    return diff_cards(prior_text, cur_text, strict=strict)


# ---------------------------------------------------------------- self-test

def run_self_test():
    import json as _j
    rc = {"v": 0}

    def chk(name, cond):
        print("  %s: %s" % (name, "OK" if cond else "FAIL"))
        if not cond:
            rc["v"] = 1

    def card(round_=2, idea="the cost of the silences we keep",
             promises=("SE-01: the dual-POV converges",),
             tensions=("SE-02: what Maya did not say in Ch.7",),
             contradictions=("SE-03: keep the sisters' warmth earned",),
             pressures=None):
        obj = {"schema": _SCHEMA_ID, "round": round_, "controlling_idea": idea,
               "active_promises": list(promises), "unresolved_tensions": list(tensions),
               "forbidden_contradictions": list(contradictions)}
        if pressures is not None:
            obj["likely_next_pressures"] = list(pressures)
        return "# State Card\n<!-- apodictic:state_card\n%s\n-->\n" % _j.dumps(obj)

    # --- single-card (S1/S2) ---
    chk("single_clean", validate_single(card())[0] == 0)
    chk("single_no_block_noop", validate_single("# State Card\nnothing structured\n")[0] == 0)
    # S1 schema: bad round type / missing field / bad JSON
    chk("s1_bad_round_type", validate_single(card().replace('"round": 2', '"round": "two"'))[0] == 1)
    chk("s1_missing_field",
        validate_single(card().replace('"controlling_idea"', '"idea"'))[0] == 1)
    code, lines = validate_single("<!-- apodictic:state_card\n{\"schema\":\"apodictic.state_card.v1\"\n-->")
    chk("s1_bad_json", code == 1 and any("S1 invalid card" in ln for ln in lines))
    # S1 id-prefix: a tracked element with no SE-NN prefix
    code, lines = validate_single(card(promises=("the dual-POV converges",)))
    chk("s1_missing_id_prefix", code == 1 and any("id prefix" in ln for ln in lines))
    # S2 duplicate id (same id in two lists — one namespace)
    code, lines = validate_single(card(promises=("SE-01: a",), tensions=("SE-01: b",)))
    chk("s2_duplicate_id", code == 1 and any("S2 duplicate id" in ln for ln in lines))
    # S1: a non-list tracked field is reported once (schema type:array), not iterated char-by-char
    bad_list = "# State Card\n<!-- apodictic:state_card\n%s\n-->\n" % _j.dumps(
        {"schema": _SCHEMA_ID, "round": 1, "controlling_idea": "x",
         "active_promises": "oops", "unresolved_tensions": [], "forbidden_contradictions": []})
    code, lines = validate_single(bad_list)
    chk("s1_non_list_field", code == 1 and sum("S1 invalid card" in ln for ln in lines) == 1)

    # --- identical self-diff is clean (the --check-all gate shape) ---
    c = card()
    chk("self_diff_clean", diff_cards(c, c)[0] == 0)

    # --- pair mode requires a parseable card on BOTH sides (PR #41 review) ---
    # a wrong/missing current file must FAIL (not silently single-card pass), so cross-round
    # checks can never be bypassed
    code, lines = diff_cards(card(), "# not a card\njust prose\n")
    chk("pair_missing_current_fails", code == 1 and any("S0 missing card" in ln for ln in lines))
    code, lines = diff_cards("# not a card\n", card())
    chk("pair_missing_prior_fails", code == 1 and any("S0 missing card" in ln for ln in lines))
    # a JSON-broken card on one side also fails (S1), never a single-card pass
    chk("pair_broken_card_fails",
        diff_cards(card(), '<!-- apodictic:state_card\n{"schema":"apodictic.state_card.v1"\n-->')[0] == 1)

    # --- cross-round ---
    # S3 round backwards
    chk("s3_round_backwards", diff_cards(card(round_=3), card(round_=2))[0] == 1)
    chk("s3_forward_ok", diff_cards(card(round_=2), card(round_=3))[0] == 0)

    # S4 promise -> contradiction (signature) — same SE id, kind flips
    prior = card(round_=1, promises=("SE-01: the sister-arc pays off",), contradictions=())
    cur = card(round_=2, promises=(), contradictions=("SE-01: the sister-arc cannot pay off as written",))
    code, lines = diff_cards(prior, cur)
    chk("s4_promise_to_contradiction",
        code == 1 and any("S4 promise->contradiction" in ln and "SE-01" in ln for ln in lines))
    # robust to rewording (matched by id, not text) — already reworded above; confirm it still fires
    chk("s4_text_reworded_still_fires", code == 1)
    # override downgrades S4 to advisory
    cur_ov = cur.replace("# State Card\n",
                         "# State Card\n<!-- override: state-card-transition SE-01 — intended pivot -->\n")
    code, lines = diff_cards(prior, cur_ov)
    chk("s4_override", code == 0 and any("promise->contradiction (override)" in ln for ln in lines))
    # a promise that stays a promise does NOT fire S4
    chk("s4_promise_kept_ok",
        diff_cards(card(round_=1, promises=("SE-01: x",)), card(round_=2, promises=("SE-01: x",)))[0] == 0)

    # W1 dropped promise (advisory; ERROR --strict; override silences)
    prior = card(round_=1, promises=("SE-01: keep this promise",))
    cur = card(round_=2, promises=())
    code, lines = diff_cards(prior, cur)
    chk("w1_dropped_promise_advisory", code == 0 and any("W1 dropped promise" in ln for ln in lines))
    chk("w1_dropped_promise_strict_fails", diff_cards(prior, cur, strict=True)[0] == 1)
    cur_ov = cur.replace("# State Card\n", "# State Card\n<!-- override: state-card-drop SE-01 — cut the subplot -->\n")
    chk("w1_dropped_override", diff_cards(prior, cur_ov)[0] == 0)
    # a resolved TENSION (not a promise) gone from current is fine, no W1
    chk("w1_resolved_tension_ok",
        diff_cards(card(round_=1, tensions=("SE-09: a tension",)),
                   card(round_=2, tensions=()))[0] == 0)

    # W2 controlling-idea shift (advisory; override silences)
    code, lines = diff_cards(card(round_=1, idea="idea A"), card(round_=2, idea="idea B"))
    chk("w2_idea_shift_advisory", code == 0 and any("W2 idea shift" in ln for ln in lines))
    chk("w2_idea_shift_strict_fails", diff_cards(card(round_=1, idea="A"), card(round_=2, idea="B"), strict=True)[0] == 1)
    cur_idea = card(round_=2, idea="idea B").replace(
        "# State Card\n", "# State Card\n<!-- override: state-card-idea-shift — deliberate reframe -->\n")
    chk("w2_idea_override", diff_cards(card(round_=1, idea="idea A"), cur_idea)[0] == 0)

    # W3 same-round content change (advisory) — ids unique across lists (SE-04 added, no collision)
    code, lines = diff_cards(
        card(round_=2, promises=("SE-01: a",), tensions=("SE-02: t",), contradictions=("SE-03: c",)),
        card(round_=2, promises=("SE-01: a", "SE-04: b"), tensions=("SE-02: t",), contradictions=("SE-03: c",)))
    chk("w3_same_round_edit", code == 0 and any("W3 same-round edit" in ln for ln in lines))

    # diff summary line present
    _c, sl = diff_cards(card(round_=1), card(round_=2, tensions=()))
    chk("summary_line", any("resolved-tension" in ln for ln in sl))

    # --- resolution (run-folder + explicit files) ---
    import tempfile
    import shutil
    d = tempfile.mkdtemp()
    try:
        p1 = os.path.join(d, "Proj_State_Card_r1.md")
        p2 = os.path.join(d, "Proj_State_Card_r2.md")
        with open(p1, "w", encoding="utf-8", newline="") as fh:
            fh.write(card(round_=1))
        with open(p2, "w", encoding="utf-8", newline="") as fh:
            fh.write(card(round_=2))
        chk("run_folder_single", run([d])[0] == 0)
        chk("explicit_pair_diff", run([p1, p2])[0] == 0)
        chk("missing_artifact_usage", run([os.path.join(d, "nope.md"), p2])[0] in (1, 2) or run(["/nope/x.md"])[0] == 2)
    finally:
        shutil.rmtree(d, ignore_errors=True)

    # regression: a non-dict state_card payload must not crash card_elements (2026-06-20 sweep)
    chk("crash_nondict_card", validate_single('<!-- apodictic:state_card\n[1,2]\n-->')[0] == 1)
    print("Self-test: %s" % ("PASS" if rc["v"] == 0 else "FAIL"))
    return rc["v"]


def main(argv):
    if "--self-test" in argv:
        return run_self_test()
    args = [a for a in argv[1:] if a != "state-card-diff"]
    strict = "--strict" in args
    paths = [a for a in args if not a.startswith("--")]
    if not paths:
        print("Usage: state_card_diff.py state-card-diff <current> | <prior> <current> [--strict] | --self-test")
        return 2
    code, lines = run(paths, strict=strict)
    for ln in lines:
        print(ln)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
