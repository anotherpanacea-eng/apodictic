#!/usr/bin/env python3
"""argument-spine — structural integrity for the Nonfiction Pre-Draft Pathway (Increments 1–3 + 5).

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

Increment 5 — the genre layer: a genre holds itself to its GENRE-REQUIRED argument structure. One
apodictic.genre_profile.v1 block names the genre (grant-proposal / academic-article / pitch-deck) and
declares the genre-required section ROLES the pre-draft Argument_State must seed (as ### sub-headings
under the canonical §1–§6 — no new top-level section, so argument-state-schema.md stays v0.1.1):
  B1 invalid genre profile  a genre_profile block fails its schema (bad genre / evaluator / seeded_by
                      enum, empty required_sections, missing field, bad per-section shape, bad JSON).
  B2 section unseeded a declared required_sections[].heading has no matching heading in the artifact —
                      the genre's structural skeleton must be SEEDED, not merely declared (parallels
                      A2/A6/A9, the seed-don't-float-free signature).
  B3 genre/form mismatch the genre_profile.genre is incompatible with the argument_spine.form (the
                      genre and the spine disagree about what the piece is). Parallels A3 thesis/C0
                      drift. ONLY fires when a spine block is also present (a genre profile may exist in
                      an early pre-draft before the full spine; absent spine -> skip, not fail).
                      Compatibility is normalized (lowercase, collapse spaces/hyphens) so the spaced
                      doc-enum spelling ('grant proposal') matches the hyphenated genre ('grant-proposal').
  B4 duplicate genre profile  more than one genre_profile block (the piece is one genre; parallels E2).
  W4 thin genre skeleton  a declared genre's CANONICAL required section is missing from
                      required_sections (e.g. a grant-proposal that omits approach). Advisory (ERROR
                      --strict): the writer may be working a non-standard variant. Override:
                      <!-- override: argument-spine-genre <genre> — <rationale> -->.

A2/A3 (spine), B2/B3 (genre), and the seeding checks verify the plan actually populated Argument_State
(the chosen integration). Reuses apodictic_artifacts (block grammar + schema engine). An artifact with
no spine / support_plan / warrant_plan / genre_profile block is a no-op. See docs/nonfiction-pre-draft.md.

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
_SUPPORT_SCHEMA_ID = "apodictic.support_plan.v1"   # Increment 2: source/evidence map (seeds §3)
_WARRANT_SCHEMA_ID = "apodictic.warrant_plan.v1"   # Increment 3: warrant pre-check (seeds §4)
_GENRE_SCHEMA_ID = "apodictic.genre_profile.v1"    # Increment 5: genre layer (seeds the genre skeleton)
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
_GENRE_OVERRIDE_RE = re.compile(r"<!--\s*override:\s*argument-spine-genre\b", re.IGNORECASE)

# Increment 5 — the genre layer (apodictic.genre_profile.v1). Per-section seeded_by enum (the stdlib
# subset validator type-checks array items but does not recurse into object items, so B1 enforces the
# per-section {role, heading, seeded_by} shape here). Mirrors the schema's seeded_by enum.
_GENRE_SEEDED_BY = ("C0+ladder", "stakes", "subclaim", "support_plan", "warrant_plan", "objection", "none")
# The genre-canonical required-section ROLE sets — the small in-validator table W4 advises against
# (a declared genre whose required_sections omit a canonical role). Roles, not headings (headings are
# writer-declared per funder/venue; D2). Drawn from convention; deliberately MINIMAL (the writer may
# carry more, and W4 only nudges on a missing canonical role, overridably).
_GENRE_CANONICAL = {
    "grant-proposal": ("specific-aims", "significance", "innovation", "approach"),
    "academic-article": ("contribution", "related-work", "method", "limitations"),
    "pitch-deck": ("problem", "solution", "traction"),
}


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


def _genre_norm(s):
    """Normalization for the B3 genre/form compatibility check: lowercase, then collapse any run of
    whitespace OR hyphens to a single space. So the spaced doc-enum spelling ('grant proposal',
    'academic article') matches the hyphenated genre token ('grant-proposal') without a brittle
    exact-match."""
    return re.sub(r"[\s-]+", " ", (s or "").strip().lower()).strip()


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


def _genre_section_errs(obj, where):
    """Per-section shape validation for required_sections (B1). The stdlib subset validator
    (apodictic_artifacts.validate_obj) type-checks array items but does NOT recurse into object items,
    so the {role, heading, seeded_by} contract — incl. the seeded_by enum — is enforced here, returning
    the same flat list of strings the schema engine returns. Only run on an already-schema-valid block
    (required_sections is a non-empty list of something)."""
    errs = []
    for i, sec in enumerate((obj.get("required_sections") or [])):
        at = "%s required_sections[%d]" % (where, i)
        if not isinstance(sec, dict):
            errs.append("%s: must be an object" % at)
            continue
        for k in ("role", "heading", "seeded_by"):
            if k not in sec:
                errs.append("%s: missing required field '%s'" % (at, k))
        if "role" in sec and not isinstance(sec["role"], str):
            errs.append("%s: 'role' must be type string" % at)
        if "heading" in sec and not isinstance(sec["heading"], str):
            errs.append("%s: 'heading' must be type string" % at)
        if "seeded_by" in sec and sec["seeded_by"] not in _GENRE_SEEDED_BY:
            errs.append("%s: 'seeded_by'=%r not in %s" % (at, sec.get("seeded_by"), list(_GENRE_SEEDED_BY)))
    return errs


def parse_genre_profiles(text):
    """[(obj_or_None, schema_errs, index), ...] for each apodictic:genre_profile block (Increment 5).

    Returns ALL genre_profile blocks (B4 fires on >1). schema_errs folds the subset-schema errors
    (B1: genre / evaluator enum, empty required_sections, missing field, bad JSON) AND the per-section
    {role, heading, seeded_by} shape the subset validator can't reach (also B1)."""
    plans = []
    if not text or art is None:
        return plans
    schema = art.load_schema(_GENRE_SCHEMA_ID)
    idx = 0
    for btype, obj, jerr in art.parse_blocks(text):
        if btype != "genre_profile":
            continue
        idx += 1
        where = "genre_profile #%d" % idx
        if jerr:
            plans.append((None, ["%s: invalid JSON — %s" % (where, jerr)], idx))
            continue
        serrs = art.validate_obj(obj, schema, where)
        if not serrs:
            serrs = _genre_section_errs(obj, where)   # per-section shape, only when the container is valid
        plans.append((obj, serrs, idx))
    return plans


def check(text, strict=False):
    """Run the argument-spine integrity checks. Returns (code, lines)."""
    lines, errs, warns = [], [], []
    obj, schema_errs = parse_spine(text)
    supports = parse_support_plans(text)
    warrants = parse_warrant_plans(text)
    genres = parse_genre_profiles(text)
    if obj is None and not schema_errs and not supports and not warrants and not genres:
        return 0, ["argument-spine: no argument_spine / support_plan / warrant_plan / genre_profile "
                   "blocks found — nothing to check"]

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

    # ---- Increment 5: the genre layer (genre_profile seeds the genre's required-section skeleton) ----
    # B4 — duplicate genre profile (the piece is one genre). Parallels scene-ethics E2. Fires on the
    # COUNT, independent of per-block validity, so two malformed blocks still surface the duplication.
    if len(genres) > 1:
        errs.append("B4 duplicate genre profile: %d genre_profile blocks present — a pre-draft is one "
                    "genre; keep exactly one" % len(genres))
    # B1 — schema / per-section / JSON validity, per genre_profile block
    for _o, gerrs, _i in genres:
        for e in gerrs:
            errs.append("B1 invalid genre profile: %s" % e)
    valid_genres = [o for o, gerrs, _i in genres if o is not None and not gerrs]
    for gobj in valid_genres:
        sections = gobj.get("required_sections") or []
        # B2 — each declared required section must be SEEDED (a matching heading present in the artifact),
        # not merely declared. The genre analogue of A2/A6/A9's seed-don't-float-free signature. Headings
        # seed as ### sub-headings under the canonical §1–§6 (D3), so we match the heading TEXT anywhere a
        # markdown heading carries it (case-insensitive), not a fixed §-number.
        for sec in sections:
            heading = (sec.get("heading") or "").strip()
            if not heading:
                continue
            hre = re.compile(r"^#{1,6}\s+.*%s" % re.escape(heading), re.IGNORECASE | re.MULTILINE)
            if not hre.search(text):
                errs.append("B2 section unseeded: declared genre section '%s' (role %s) has no matching "
                            "heading in the artifact — the genre skeleton must be seeded, not just "
                            "declared" % (heading, sec.get("role")))
        # B3 — the genre and the spine must agree about what the piece is. ONLY when a valid spine is
        # also present (a genre profile may precede the full spine in an early pre-draft -> skip, not
        # fail). Compatibility is normalized (spaces/hyphens, case), so the spaced doc-enum form
        # ('grant proposal') matches the hyphenated genre ('grant-proposal').
        if obj is not None and not schema_errs:
            if _genre_norm(gobj.get("genre")) != _genre_norm(obj.get("form")):
                errs.append("B3 genre/form mismatch: genre_profile.genre=%r is incompatible with the "
                            "spine's form=%r — the genre and the spine disagree about what the piece is"
                            % (gobj.get("genre"), obj.get("form")))
        # W4 — thin genre skeleton: a declared genre's CANONICAL required role is missing from
        # required_sections (advisory; ERROR --strict; override silences). Genre conventions vary, so
        # this only nudges; the hard B-codes carry structural integrity.
        if not _GENRE_OVERRIDE_RE.search(text):
            declared_roles = {_genre_norm(s.get("role")) for s in sections}
            for canon in _GENRE_CANONICAL.get(gobj.get("genre"), ()):
                if _genre_norm(canon) not in declared_roles:
                    warns.append("W4 thin genre skeleton: a %s profile omits the canonical section "
                                 "'%s' — add it, or override if this is a non-standard variant"
                                 % (gobj.get("genre"), canon))

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
    if valid_genres:
        g = valid_genres[0]
        lines.append("argument-spine: genre=%s / evaluator=%s; %d required section(s)"
                     % (g.get("genre"), g.get("evaluator"), len(g.get("required_sections") or [])))
    for e in errs:
        lines.append("  ERROR: %s" % e)
    for w in warns:
        lines.append("  %s: %s" % ("ERROR (--strict)" if strict else "WARN", w))

    if errs or (strict and warns):
        lines.append("argument-spine: FAIL (%d error(s)%s)"
                     % (len(errs), ", %d strict warn(s)" % len(warns) if (strict and warns) else ""))
        return 1, lines
    if warns:
        lines.append("WARN: argument-spine: %d advisory gap(s) — see W1/W2/W3/W4 above" % len(warns))
    else:
        seeded = "§1/§2" + ("/§3" if valid_supports else "") + ("/§4" if valid_warrants else "")
        genre_tag = (" + genre %s" % valid_genres[0].get("genre")) if valid_genres else ""
        lines.append("argument-spine: PASS (contract + seeds Argument_State %s + anti-thesis%s)"
                     % (seeded, genre_tag))
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

    # ---- Increment 5: the genre layer (genre_profile seeds the genre's required-section skeleton) ----
    # canonical role->heading per genre (the full canonical set; a clean profile carries all of them)
    _G_SECTIONS = {
        "grant-proposal": [("specific-aims", "Specific Aims", "C0+ladder"),
                           ("significance", "Significance", "stakes"),
                           ("innovation", "Innovation", "subclaim"),
                           ("approach", "Approach", "support_plan")],
        "academic-article": [("contribution", "Contribution Claim", "C0+ladder"),
                             ("related-work", "Related-Work Positioning", "subclaim"),
                             ("method", "Method and Evidence", "support_plan"),
                             ("limitations", "Limitations and Scope", "none")],
        "pitch-deck": [("problem", "Problem", "stakes"),
                       ("solution", "Solution", "C0+ladder"),
                       ("traction", "Traction", "support_plan")],
    }

    def genre(g="grant-proposal", evaluator="panel-reviewer", sections=None, **over):
        secs = [{"role": r, "heading": h, "seeded_by": s}
                for (r, h, s) in (sections if sections is not None else _G_SECTIONS[g])]
        o = {"schema": _GENRE_SCHEMA_ID, "genre": g, "required_sections": secs, "evaluator": evaluator}
        o.update(over)
        return "<!-- apodictic:genre_profile\n%s\n-->" % _j.dumps(o)

    def seededG(g="grant-proposal", evaluator="panel-reviewer", form=None, sections=None,
                thesis="the city should fund curb-cut ramps citywide", extra="", **gover):
        # a seeded Argument_State whose spine form = the genre, whose §1/§2 carry the genre's required
        # section headings (as ### sub-headings), + a spine + the genre_profile block. `form` defaults
        # to the genre token so B3 passes; pass form= to force a mismatch (B3 reads the SPINE's form,
        # so the spine block carries form_val, not just the §1 markdown line).
        secs = sections if sections is not None else _G_SECTIONS[g]
        form_val = form if form is not None else g
        heads = "".join("### %s\n\n_seeded_\n\n" % h for (_r, h, _s) in secs)
        gblock = genre(g=g, evaluator=evaluator, sections=sections, **gover)
        return ("# Argument State\n## 1. Context and Classification\nForm: %s\n%s"
                "## 2. Claim Architecture\nC0 (main claim): %s\n%s"
                "## 6. Objection and Dialectical Integrity Map\nObjection 1: low priority\n%s\n"
                % (form_val, heads, thesis, extra,
                   gblock + "\n" + spine(thesis=thesis, form=form_val)))

    # clean: all three genres, fully seeded, form == genre -> PASS, no B/W
    for _g in ("grant-proposal", "academic-article", "pitch-deck"):
        code, lines = check(seededG(_g, evaluator={"grant-proposal": "panel-reviewer",
                                                   "academic-article": "peer-reviewer",
                                                   "pitch-deck": "investor"}[_g]))
        chk("genre_clean_%s" % _g, code == 0 and not any("B1" in ln or "B2" in ln or "B3" in ln
                                                         or "B4" in ln or "W4" in ln for ln in lines))
    # genre layer staged OFF: a plain spine (no genre_profile) behaves exactly as today -> no B/W codes
    chk("genre_staged_off", not any(("B1" in ln or "B2" in ln or "B3" in ln or "B4" in ln or "W4" in ln)
                                    for ln in check(seeded())[1]))
    # genre_profile alone (no spine) still no-op-resolves the spine but checks the genre -> not a crash;
    # B3 is SKIPPED when no valid spine is present
    code, lines = check("# notes\n### Specific Aims\n_x_\n### Significance\n_x_\n### Innovation\n_x_\n"
                        "### Approach\n_x_\n" + genre("grant-proposal"))
    chk("genre_no_spine_skips_b3", code == 0 and not any("B3" in ln for ln in lines))

    # B1 — bad genre enum / bad evaluator enum / empty required_sections / bad seeded_by / missing field / JSON
    # (swap the genre token inside the genre_profile JSON to an out-of-enum value; B3 also fires, but B1 is the point)
    chk("b1_bad_genre", check(seededG().replace('"genre": "grant-proposal"', '"genre": "white-paper"', 1))[0] == 1)
    chk("b1_bad_evaluator", check(seededG(evaluator="czar"))[0] == 1)
    code, lines = check(seededG(sections=[]))
    chk("b1_empty_sections", code == 1 and any("B1 invalid genre profile" in ln for ln in lines))
    code, lines = check(seededG(sections=[("specific-aims", "Specific Aims", "telepathy")]))
    chk("b1_bad_seeded_by", code == 1 and any("B1 invalid genre profile" in ln and "seeded_by" in ln for ln in lines))
    # missing a per-section field (drop heading) -> B1 (the per-section shape enforced in-validator)
    bad_sec_block = ('<!-- apodictic:genre_profile\n'
                     '{"schema":"apodictic.genre_profile.v1","genre":"pitch-deck","evaluator":"investor",'
                     '"required_sections":[{"role":"problem","seeded_by":"stakes"}]}\n-->')
    code, lines = check("# Argument State\n## 1. Context and Classification\nForm: pitch-deck\n"
                        "## 2. Claim Architecture\nC0 (main claim): x\n" + bad_sec_block)
    chk("b1_section_missing_field", code == 1 and any("B1 invalid genre profile" in ln and "heading" in ln for ln in lines))
    code, lines = check("## 1. Context and Classification\n## 2. Claim Architecture\n"
                        '<!-- apodictic:genre_profile\n{"schema":"apodictic.genre_profile.v1"\n-->')
    chk("b1_bad_json", code == 1 and any("B1 invalid genre profile" in ln for ln in lines))

    # B2 — a declared section heading is absent from the artifact (declared but not seeded)
    code, lines = check(seededG("grant-proposal").replace("### Approach\n\n_seeded_\n\n", "", 1))
    chk("b2_section_unseeded", code == 1 and any("B2 section unseeded" in ln and "Approach" in ln for ln in lines))
    # B2 lookalike guard: a heading that merely CONTAINS the word elsewhere as prose (not a heading) is
    # still unseeded — drop the §heading but leave a prose mention
    code, lines = check(seededG("pitch-deck").replace("### Traction\n\n_seeded_\n\n",
                                                      "We will discuss Traction in the deck.\n\n", 1))
    chk("b2_prose_not_heading", code == 1 and any("B2 section unseeded" in ln and "Traction" in ln for ln in lines))

    # B3 — genre/form mismatch (genre says grant-proposal, the spine's form says pitch-deck)
    code, lines = check(seededG("grant-proposal", form="pitch-deck"))
    chk("b3_genre_form_mismatch", code == 1 and any("B3 genre/form mismatch" in ln for ln in lines))
    # B3 normalization: the spaced doc-enum form 'grant proposal' is COMPATIBLE with 'grant-proposal'
    code, lines = check(seededG("grant-proposal", form="grant proposal"))
    chk("b3_spaced_form_ok", code == 0 and not any("B3" in ln for ln in lines))
    # B3 normalization: 'academic article' (spaced) vs 'academic-article' -> compatible
    code, lines = check(seededG("academic-article", evaluator="peer-reviewer", form="Academic Article"))
    chk("b3_spaced_academic_ok", code == 0 and not any("B3" in ln for ln in lines))

    # B4 — two genre_profile blocks (the piece is one genre)
    code, lines = check(seededG("grant-proposal", extra=genre("grant-proposal") + "\n"))
    chk("b4_duplicate", code == 1 and any("B4 duplicate genre profile" in ln for ln in lines))

    # W4 — a declared genre omits a canonical role (grant without 'approach') -> advisory; ERROR --strict; override
    GRANT_NO_APPROACH = [("specific-aims", "Specific Aims", "C0+ladder"),
                         ("significance", "Significance", "stakes"),
                         ("innovation", "Innovation", "subclaim")]
    code, lines = check(seededG("grant-proposal", sections=GRANT_NO_APPROACH))
    chk("w4_thin_skeleton", code == 0 and any("W4 thin genre skeleton" in ln and "approach" in ln for ln in lines))
    chk("w4_strict_fails", check(seededG("grant-proposal", sections=GRANT_NO_APPROACH), strict=True)[0] == 1)
    ovg = "<!-- override: argument-spine-genre grant-proposal — LOI variant has no Approach section -->\n"
    code, lines = check(seededG("grant-proposal", sections=GRANT_NO_APPROACH, extra=ovg))
    chk("w4_override", code == 0 and not any("W4" in ln for ln in lines))
    # W4 academic: a contribution claim with NO related-work positioning is the academic signature thin-skeleton
    ACAD_NO_RELWORK = [("contribution", "Contribution Claim", "C0+ladder"),
                       ("method", "Method and Evidence", "support_plan"),
                       ("limitations", "Limitations and Scope", "none")]
    code, lines = check(seededG("academic-article", evaluator="peer-reviewer", sections=ACAD_NO_RELWORK))
    chk("w4_academic_no_relwork",
        code == 0 and any("W4 thin genre skeleton" in ln and "related-work" in ln for ln in lines))

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
