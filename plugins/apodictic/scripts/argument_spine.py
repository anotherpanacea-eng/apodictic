#!/usr/bin/env python3
"""argument-spine — structural integrity for the Nonfiction Pre-Draft Pathway (Increments 1–2).

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

Increment 2 — the source/evidence map, planned per subclaim as apodictic.support_plan.v1 blocks
that SEED §3 Support Map:
  A4 invalid support  a support_plan block fails its schema (bad support_type / scheme_hint / status
                      enum, malformed subclaim_id, missing field, bad JSON).
  A5 dangling subclaim a support_plan's subclaim_id is not a Cn declared in the spine's ladder.
  A6 support unseeded  support_plan blocks are present but the artifact has no '## 3. Support Map'
                      heading (the support map must seed §3 — parallel to A2).
  W2 bare assertion   once support planning has started (>=1 support_plan), a declared subclaim with
                      NO planned support (advisory; ERROR --strict). Staged, so a spine-only
                      (Increment 1) artifact is never nagged.

Increment 3 — the warrant pre-check, planned per subclaim as apodictic.warrant_plan.v1 blocks that
SEED §4 Warrant and Inference Map:
  A7 invalid warrant  a warrant_plan block fails its schema (bad warrant_status / backing / qualifier
                      enum, malformed subclaim_id, missing field, bad JSON).
  A8 dangling subclaim a warrant_plan's subclaim_id is not a Cn declared in the spine's ladder.
  A9 warrant unseeded warrant_plan blocks present but no '## 4. Warrant and Inference Map' heading.
  W3 implicit warrant for a HOSTILE audience (per the spine's audience_receptivity), a warrant that
                      is not EXPLICIT or has ABSENT backing — make it explicit and back it before
                      drafting (advisory; ERROR --strict). Audience-calibrated. Override:
                      <!-- override: argument-spine-warrant — <reason> -->.

A2/A3 (spine) and the seeding checks verify the plan actually populated Argument_State (the chosen
integration). Reuses apodictic_artifacts (block grammar + schema engine). An artifact with no spine
/ support_plan / warrant_plan block is a no-op. See docs/nonfiction-pre-draft.md.

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


def _has_block(text, btype):
    """True if `text` carries a real apodictic:<btype> block (a parsed carrier, not a prose mention).

    Classifying on parsed blocks — not a raw substring — keeps a file that merely *names* the marker
    in prose from being misrouted/skipped (the 2026-06-20 resolver-hardening sweep). Gated by
    validate.sh validator-conventions (M2)."""
    if art is None:
        return ("apodictic:%s" % btype) in (text or "")
    return any(bt == btype for bt, _o, _e in art.parse_blocks(text or ""))

_SCHEMA_ID = "apodictic.argument_spine.v1"
_SUPPORT_SCHEMA_ID = "apodictic.support_plan.v1"   # Increment 2: source/evidence map (seeds §3)
_WARRANT_SCHEMA_ID = "apodictic.warrant_plan.v1"   # Increment 3: warrant pre-check (seeds §4)
_STATE_GLOB = "Argument_State*.md"
_SCORE_ENUMS = ("argument_type", "burden_level", "audience_expertise", "audience_receptivity")
# Canonical Argument_State headings the spine must seed (docs/argument-state-schema.md §1–§4).
_SEC1_RE = re.compile(r"^##\s+1\.\s+Context and Classification", re.IGNORECASE | re.MULTILINE)
_SEC2_RE = re.compile(r"^##\s+2\.\s+Claim Architecture", re.IGNORECASE | re.MULTILINE)
_SEC3_RE = re.compile(r"^##\s+3\.\s+Support Map", re.IGNORECASE | re.MULTILINE)
_SEC4_RE = re.compile(r"^##\s+4\.\s+Warrant and Inference Map", re.IGNORECASE | re.MULTILINE)
# The §2 main-claim line: "C0 (main claim): <thesis>".
_C0_RE = re.compile(r"^\s*C0\s*\(main claim\)\s*:\s*(.+?)\s*$", re.IGNORECASE | re.MULTILINE)
# A subclaim string carries a leading Cn id ("C1: …") — the link target for a support plan.
_SUBCLAIM_ID_RE = re.compile(r"^\s*(C[0-9]+)\b")
_ANTITHESIS_OVERRIDE_RE = re.compile(r"<!--\s*override:\s*argument-spine-antithesis\b", re.IGNORECASE)
_WARRANT_OVERRIDE_RE = re.compile(r"<!--\s*override:\s*argument-spine-warrant\b", re.IGNORECASE)


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


def spine_subclaim_ids(obj):
    """Set of Cn ids declared in the spine's subclaim ladder ('C1: …' -> 'C1'). The link targets a
    support plan resolves against (Increment 2)."""
    ids = set()
    if isinstance(obj, dict):
        for s in (obj.get("subclaims") or []):
            if isinstance(s, str):
                m = _SUBCLAIM_ID_RE.match(s)
                if m:
                    ids.add(m.group(1))
    return ids


def parse_support_plans(text):
    """[(obj_or_None, schema_errs, index), ...] for each apodictic:support_plan block (Increment 2)."""
    plans = []
    if not text or art is None:
        return plans
    schema = art.load_schema(_SUPPORT_SCHEMA_ID)
    idx = 0
    for btype, obj, jerr in art.parse_blocks(text):
        if btype != "support_plan":
            continue
        idx += 1
        where = "support_plan #%d" % idx
        if jerr:
            plans.append((None, ["%s: invalid JSON — %s" % (where, jerr)], idx))
            continue
        plans.append((obj, art.validate_obj(obj, schema, where), idx))
    return plans


def parse_warrant_plans(text):
    """[(obj_or_None, schema_errs, index), ...] for each apodictic:warrant_plan block (Increment 3)."""
    plans = []
    if not text or art is None:
        return plans
    schema = art.load_schema(_WARRANT_SCHEMA_ID)
    idx = 0
    for btype, obj, jerr in art.parse_blocks(text):
        if btype != "warrant_plan":
            continue
        idx += 1
        where = "warrant_plan #%d" % idx
        if jerr:
            plans.append((None, ["%s: invalid JSON — %s" % (where, jerr)], idx))
            continue
        plans.append((obj, art.validate_obj(obj, schema, where), idx))
    return plans


def check(text, strict=False):
    """Run the argument-spine integrity checks. Returns (code, lines)."""
    lines, errs, warns = [], [], []
    obj, schema_errs = parse_spine(text)
    supports = parse_support_plans(text)
    warrants = parse_warrant_plans(text)
    if obj is None and not schema_errs and not supports and not warrants:
        return 0, ["argument-spine: no argument_spine / support_plan / warrant_plan blocks found — "
                   "nothing to check"]

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

    # ---- Increment 2: source/evidence map (seeds §3 Support Map) ----
    # A4 — schema validity per support_plan
    for _o, serrs, _i in supports:
        for e in serrs:
            errs.append("A4 invalid support plan: %s" % e)
    valid_supports = [o for o, serrs, _i in supports if o is not None and not serrs]
    if valid_supports:
        # A6 — support plans must seed §3 Support Map (parallel to A2's seeding discipline)
        if not _SEC3_RE.search(text):
            errs.append("A6 support not seeded: support_plan blocks present but no '## 3. Support "
                        "Map' heading — the support map must seed Argument_State §3")
        declared = spine_subclaim_ids(obj) if (obj is not None and not schema_errs) else set()
        planned_ids = set()
        # A5 — dangling subclaim_id (a support plan that doesn't attach to a declared spine subclaim)
        for o in valid_supports:
            sid = o.get("subclaim_id")
            planned_ids.add(sid)
            if sid not in declared:
                errs.append("A5 dangling subclaim_id: support_plan references %s — not a declared "
                            "spine subclaim (declared: %s)" % (sid, ", ".join(sorted(declared)) or "none"))
        # W2 — bare assertion: a declared subclaim with no planned support. Staged — only once support
        # planning has started (>=1 plan), so a spine-only (Increment 1) artifact is never nagged.
        for sid in sorted(declared - planned_ids):
            warns.append("W2 bare assertion: %s has no planned support — name the intended support, "
                         "or mark it a known gap, before drafting" % sid)

    # ---- Increment 3: warrant pre-check (seeds §4 Warrant and Inference Map) ----
    # A7 — schema validity per warrant_plan
    for _o, werrs, _i in warrants:
        for e in werrs:
            errs.append("A7 invalid warrant plan: %s" % e)
    valid_warrants = [o for o, werrs, _i in warrants if o is not None and not werrs]
    if valid_warrants:
        # A9 — warrant plans must seed §4 Warrant and Inference Map (parallel to A2/A6)
        if not _SEC4_RE.search(text):
            errs.append("A9 warrant unseeded: warrant_plan blocks present but no '## 4. Warrant and "
                        "Inference Map' heading — the warrant map must seed Argument_State §4")
        declared = spine_subclaim_ids(obj) if (obj is not None and not schema_errs) else set()
        hostile = (obj.get("audience_receptivity") == "HOSTILE") if (obj is not None and not schema_errs) else False
        # A8 — dangling subclaim_id
        for o in valid_warrants:
            if o.get("subclaim_id") not in declared:
                errs.append("A8 dangling subclaim_id: warrant_plan references %s — not a declared "
                            "spine subclaim (declared: %s)"
                            % (o.get("subclaim_id"), ", ".join(sorted(declared)) or "none"))
        # W3 — for a HOSTILE audience, an implicit (non-EXPLICIT) or unbacked (ABSENT) warrant must be
        # made explicit and backed before drafting. Audience-calibrated against the spine. Override.
        if hostile and not _WARRANT_OVERRIDE_RE.search(text):
            for o in valid_warrants:
                ws, bk = o.get("warrant_status"), o.get("backing")
                if ws != "EXPLICIT" or bk == "ABSENT":
                    reason = ("status=%s" % ws if ws != "EXPLICIT" else "") + (
                        (", " if ws != "EXPLICIT" else "") + "backing=ABSENT" if bk == "ABSENT" else "")
                    warns.append("W3 implicit warrant for hostile audience: %s (%s) — a HOSTILE "
                                 "audience won't grant it; make the warrant explicit and back it before "
                                 "drafting" % (o.get("subclaim_id"), reason))

    # Report
    if obj is not None and not schema_errs:
        lines.append("argument-spine: %s / burden=%s / audience=%s,%s; %d subclaim(s)"
                     % (obj.get("argument_type"), obj.get("burden_level"),
                        obj.get("audience_expertise"), obj.get("audience_receptivity"),
                        len(obj.get("subclaims") or [])))
    if valid_supports:
        lines.append("argument-spine: %d support plan(s) over %d declared subclaim(s)"
                     % (len(valid_supports), len(spine_subclaim_ids(obj))))
    if valid_warrants:
        lines.append("argument-spine: %d warrant plan(s)" % len(valid_warrants))
    for e in errs:
        lines.append("  ERROR: %s" % e)
    for w in warns:
        lines.append("  %s: %s" % ("ERROR (--strict)" if strict else "WARN", w))

    if errs or (strict and warns):
        lines.append("argument-spine: FAIL (%d error(s)%s)"
                     % (len(errs), ", %d strict warn(s)" % len(warns) if (strict and warns) else ""))
        return 1, lines
    if warns:
        lines.append("WARN: argument-spine: %d advisory gap(s) — see W1/W2/W3 above" % len(warns))
    else:
        seeded = "§1/§2" + ("/§3" if valid_supports else "") + ("/§4" if valid_warrants else "")
        lines.append("argument-spine: PASS (contract + seeds Argument_State %s + anti-thesis)" % seeded)
    return 0, lines


# ---------------------------------------------------------------- resolution

def _newest(paths):
    return max(paths, key=os.path.getmtime) if paths else None


def resolve(paths):
    if len(paths) == 1 and os.path.isdir(paths[0]):
        return _newest(glob.glob(os.path.join(paths[0], _STATE_GLOB)))
    for p in paths:
        if _has_block(_read(p) or "", "argument_spine"):
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

    def support(sub="C1", stype="DATA", planned="city accessibility audit counts",
                status="to-acquire", **over):
        o = {"schema": _SUPPORT_SCHEMA_ID, "subclaim_id": sub, "support_type": stype,
             "planned_support": planned, "status": status}
        o.update(over)
        return "<!-- apodictic:support_plan\n%s\n-->" % _j.dumps(o)

    def seeded3(subclaims, supports, thesis="the city should fund curb-cut ramps citywide"):
        # a seeded Argument_State with §1/§2/§3, a spine whose ladder = subclaims, + support blocks
        return ("# Argument State\n## 1. Context and Classification\nForm: op-ed\n"
                "## 2. Claim Architecture\nC0 (main claim): %s\n## 3. Support Map\n%s\n"
                "## 6. Objection and Dialectical Integrity Map\nObjection 1: low priority\n%s\n"
                % (thesis, supports, spine(thesis=thesis, subclaims=subclaims)))

    def warrant(sub="C1", ws="EXPLICIT", bk="PRESENT", q="MATCHED",
                w="removing a documented barrier is a legitimate use of public funds", **over):
        o = {"schema": _WARRANT_SCHEMA_ID, "subclaim_id": sub, "warrant": w,
             "warrant_status": ws, "backing": bk, "qualifier": q}
        o.update(over)
        return "<!-- apodictic:warrant_plan\n%s\n-->" % _j.dumps(o)

    def seeded4(subclaims, warrants, receptivity="HOSTILE",
                thesis="the city should fund curb-cut ramps citywide"):
        # a seeded Argument_State with §1/§2/§4 + a spine whose ladder = subclaims, + warrant blocks
        return ("# Argument State\n## 1. Context and Classification\nForm: op-ed\n"
                "## 2. Claim Architecture\nC0 (main claim): %s\n"
                "## 4. Warrant and Inference Map\n%s\n"
                "## 6. Objection and Dialectical Integrity Map\nObjection 1: low priority\n%s\n"
                % (thesis, warrants, spine(thesis=thesis, subclaims=subclaims,
                                          audience_receptivity=receptivity)))

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

    # ---- Increment 2: source/evidence map (support plans seed §3) ----
    TWO = ("C1: ramps remove a documented mobility barrier", "C2: the phased cost fits the budget")
    # clean: both subclaims have a support plan, §3 present
    chk("inc2_clean", check(seeded3(TWO, support("C1") + "\n" + support("C2")))[0] == 0)
    # A4 — bad support_type / status / subclaim_id format
    chk("a4_bad_support_type", check(seeded3(TWO, support("C1", stype="VIBES") + support("C2")))[0] == 1)
    chk("a4_bad_status", check(seeded3(TWO, support("C1", status="someday") + support("C2")))[0] == 1)
    chk("a4_bad_subclaim_fmt", check(seeded3(TWO, support("C1x") + support("C2")))[0] == 1)
    code, lines = check(seeded3(TWO, '<!-- apodictic:support_plan\n{"schema":"apodictic.support_plan.v1"\n-->'))
    chk("a4_bad_json", code == 1 and any("A4 invalid support plan" in ln for ln in lines))
    # A5 — dangling subclaim_id (C9 not declared in the spine ladder)
    code, lines = check(seeded3(TWO, support("C9")))
    chk("a5_dangling_subclaim", code == 1 and any("A5 dangling subclaim_id" in ln and "C9" in ln for ln in lines))
    # A6 — support plans present but no §3 heading (inject a support block into the §3-less seeded())
    code, lines = check(seeded().replace("## 6.", support("C1") + "\n## 6.", 1))
    chk("a6_support_unseeded", code == 1 and any("A6 support not seeded" in ln for ln in lines))
    # W2 — bare assertion: C2 has no support plan (staged ON; advisory; ERROR --strict)
    code, lines = check(seeded3(TWO, support("C1")))
    chk("w2_bare_assertion", code == 0 and any("W2 bare assertion" in ln and "C2" in ln for ln in lines))
    chk("w2_bare_strict_fails", check(seeded3(TWO, support("C1")), strict=True)[0] == 1)
    # W2 staged OFF: a spine with two subclaims but NO support plans -> no W2 (don't nag Increment 1)
    code, lines = check(seeded(block=spine(subclaims=TWO)))
    chk("w2_staged_off", code == 0 and not any("W2" in ln for ln in lines))

    # ---- Increment 3: warrant pre-check (warrant plans seed §4) ----
    ONE = ("C1: ramps remove a documented mobility barrier",)
    # clean: an explicit, backed warrant is fine even for a HOSTILE audience -> no W3
    chk("inc3_clean", check(seeded4(ONE, warrant("C1", ws="EXPLICIT", bk="PRESENT")))[0] == 0)
    # A7 — bad enum
    chk("a7_bad_status", check(seeded4(ONE, warrant("C1", ws="VAGUE")))[0] == 1)
    chk("a7_bad_backing", check(seeded4(ONE, warrant("C1", bk="SOME")))[0] == 1)
    # A8 — dangling subclaim_id
    code, lines = check(seeded4(ONE, warrant("C9")))
    chk("a8_dangling", code == 1 and any("A8 dangling subclaim_id" in ln and "C9" in ln for ln in lines))
    # A9 — warrants present but no §4 heading (inject into the §4-less seeded())
    code, lines = check(seeded().replace("## 6.", warrant("C1") + "\n## 6.", 1))
    chk("a9_warrant_unseeded", code == 1 and any("A9 warrant unseeded" in ln for ln in lines))
    # W3 — HOSTILE audience + implicit (RECOVERABLE) warrant -> advisory; ERROR --strict
    code, lines = check(seeded4(ONE, warrant("C1", ws="RECOVERABLE"), receptivity="HOSTILE"))
    chk("w3_implicit_hostile", code == 0 and any("W3 implicit warrant" in ln and "C1" in ln for ln in lines))
    chk("w3_implicit_strict_fails",
        check(seeded4(ONE, warrant("C1", ws="RECOVERABLE"), receptivity="HOSTILE"), strict=True)[0] == 1)
    # W3 — ABSENT backing also fires for HOSTILE (even when EXPLICIT)
    chk("w3_absent_backing_hostile",
        any("W3 implicit warrant" in ln
            for ln in check(seeded4(ONE, warrant("C1", ws="EXPLICIT", bk="ABSENT")))[1]))
    # W3 audience-calibrated OFF: same implicit warrant for a SYMPATHETIC audience -> no W3
    code, lines = check(seeded4(ONE, warrant("C1", ws="RECOVERABLE"), receptivity="SYMPATHETIC"))
    chk("w3_sympathetic_no_warn", code == 0 and not any("W3" in ln for ln in lines))
    # W3 override silences
    ovw = "<!-- override: argument-spine-warrant — the implicit warrant is shared ground here -->\n"
    code, lines = check(seeded4(ONE, ovw + warrant("C1", ws="RECOVERABLE"), receptivity="HOSTILE"))
    chk("w3_override", code == 0 and not any("W3" in ln for ln in lines))

    # resolution: run-folder (Argument_State*.md) + explicit file
    import tempfile
    import shutil
    d = tempfile.mkdtemp()
    try:
        p = os.path.join(d, "Argument_State.md")
        with open(p, "w", encoding="utf-8", newline="") as fh:
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
