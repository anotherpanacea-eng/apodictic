#!/usr/bin/env python3
"""content-advisory — structural integrity for the Content-Advisory / Sensitivity-Surface Derivation.

`validate.sh content-advisory <run_folder|files>` shells out here. A writer preparing to publish often
needs a content advisory — a map of where the manuscript depicts intense material (violence, sexual
content, self-harm, abuse), at what intensity, on- or off-page — for front-matter, marketing metadata,
sensitivity-reader handoff, or their own awareness. APODICTIC's existing audits *assess* such content
for craft/harm; none DERIVES a reader/marketing-facing advisory artifact. This is that derivation:
pure extraction over depicted content, anchored to loci. Each note is an apodictic.content_note.v1
block; this validator owns the advisory's contract.

It is OPT-IN by design (some authors decline content warnings on principle), and DESCRIPTIVE, never
evaluative: a note records *that* content is depicted and at what intensity ("on-page graphic
violence — Ch 7"); it never calls it gratuitous or recommends cutting it. A content note is NOT a
defect — no Must/Should/Could severity; its intensity scale is orthogonal to the editorial scale.

  A1 schema           a content_note block fails its schema (bad category/intensity/depiction enum,
                      malformed CN-NN id, missing field, empty/non-string loci, broken JSON, dup id),
                      OR category=='other' with an empty `label` (a conditional the schema can't express).
  A2 locus shape      a note carries a locus that is empty or not a coarse locus (no chapter / §section
                      / ¶ / line / page token). A precondition, NOT a firewall proof — resolution is
                      deferred to the shared snapshot layer.
  A3 severity leak    the advisory's reader-facing prose or any note `label` carries an editorial
                      Must/Should/Could-Fix token, OR an apodictic:finding block is present in the
                      artifact. Content notes are advisories, not findings (the Legal-Risk orthogonal-
                      severity discipline). ERROR.
  W1 prescriptive     a note label or the advisory prose matches a PRESCRIPTIVE construction
     drift            ("should/recommend/consider … cut/remove/soften/tone down/reduce") — not bare
                      adjectives like "excessive" which legitimately describe depicted content. The
                      advisory describes; it does not prescribe. Advisory; ERROR under --strict.
                      Override a note LABEL (per id): <!-- override: advisory-eval CN-NN — <why> -->.
                      Override the reader-facing PROSE (id-less, so a per-id override never silences
                      unrelated prose): <!-- override: advisory-eval-prose — <why> -->.
  W2 opt-in marker    a resolved advisory artifact lacks the `<!-- content-advisory: opted-in -->`
                      marker (generated only on request). Advisory; ERROR under --strict.

Reuses apodictic_artifacts (block grammar + schema engine). The artifact is optional; if none is
resolved the command no-ops with exit 2 ("no advisory artifact"), like legal-risk. See
docs/content-advisory.md.

  content_advisory.py content-advisory <run_folder|files...> [--strict]
  content_advisory.py --self-test

Exit: 0 clean / WARN-only, 1 ERROR (or WARN under --strict), 2 usage / no artifact.
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

_SCHEMA_ID = "apodictic.content_note.v1"
_ADVISORY_GLOB = "*_Content_Advisory_*.md"

# A2 — the coarse locus shape (shared with continuity-bible C2): chapter / §section / ¶ / line / page.
_LOCUS_RE = re.compile(
    r"\bch(?:apter)?\.?\s*\d+|§|¶|\blines?\s+\d+|\bp(?:g|ag\.?|\.)?\s*\d+|\bpara(?:graph)?\.?\s*\d+",
    re.IGNORECASE)
# A3 — editorial severity tokens must not leak into the advisory (it is not a defect list).
_SEVERITY_RE = re.compile(r"\b(?:Must|Should|Could)-Fix\b")
# W1 — a PRESCRIPTIVE construction: a modal/recommend verb governing a revision action ("should cut
# this scene") — NOT a bare descriptive adjective ("excessive blood loss"). `_PRESCRIPTIVE_RE` finds
# the bare `<modal> … <action>` shape; `_prescribes()` then drops NEGATED instances. Negation scope is
# a HEURISTIC, not a parser (cf. intake_interview I4): we look only at the two places a negator can
# actually flip this construction — directly before the MODAL ("do not / never / can't recommend …";
# also across a comma-bracketed aside "do not, in good conscience, recommend …"), or directly before
# the ACTION ("recommends NO cut", "should NOT cut"). A negator binding an UNRELATED word mid-gap
# ("recommend, with no hesitation, cutting") does not negate the action, so it still fires. Failure
# direction is toward NOT firing (W1 is advisory; ERROR only under --strict, and the prose override
# `advisory-eval-prose` is the escape). KNOWN LIMIT: a negator separated from the modal by a
# coordinator or a second clause ("no one objected, we recommend cutting") is read as governing the
# modal here only when within the bracket/adverb window; deeper scope needs a parser, not this rule.
_PRESCRIPTIVE_RE = re.compile(
    r"\b(?:should|recommend(?:ed|ing|s)?|consider|advise[sd]?|suggest(?:ed|ing|s)?|ought\s+to|"
    r"needs?\s+to|must|might\s+want\s+to)\b"
    r"(?P<gap>[^.;\n]{0,40}?)"
    r"\b(?:cut(?:ting|s)?|remov\w+|delet\w+|soften\w*|tone\s+(?:it\s+)?down|reduc\w+|"
    r"trim\w*|excis\w+|edit\w*\s+out|rework\w*)\b",
    re.IGNORECASE)
# A negator that GOVERNS the modal: directly before it (+ ≤2 adverbs), across a comma-bracketed aside,
# an `n't`/`cannot` contraction, or "against" ("we are against recommending …"). Anchored to the end
# of the pre-modal text.
_NEG_MODAL_RE = re.compile(
    r"\b(?:not|never|no|against)\b(?:\s+\w+){0,2}\s*$"  # "do not [really] recommend", "against recommending"
    r"|\bnot\b\s*,[^.;\n]{0,30}?,\s*$"             # "do not, in good conscience, recommend"
    r"|n['’]t\b(?:\s*,[^.;\n]{0,30}?,)?\s*$"       # "don't [, …,] recommend"
    r"|\bcan(?:not|['’]t)\b\s*$",                  # "cannot / can't recommend"
    re.IGNORECASE)
# A negator that GOVERNS the action: no/not/never immediately before it (gap ENDS in the negator), OR
# "against" + the gerund phrase it heads ("recommend against cutting", "advise against ever removing")
# — but NOT a comma-closed aside ("recommend, against all odds, cutting" still prescribes the cut).
_NEG_ACTION_RE = re.compile(r"\b(?:no|not|never)\s+$|\bagainst\b(?:\s+\w+){0,2}\s*$", re.IGNORECASE)


def _prescribes(text):
    """True if `text` carries a genuine prescriptive construction (a modal governing a revision
    action), excluding NEGATED ones — a negated modal ("do not recommend cutting") or a negated action
    ("recommends no cut", "should not cut"). A negator binding an unrelated word mid-gap ("recommend,
    with no hesitation, cutting") does not negate the action, so it still fires."""
    text = text or ""
    for m in _PRESCRIPTIVE_RE.finditer(text):
        if _NEG_MODAL_RE.search(text[:m.start()]):
            continue                              # the modal itself is negated
        if _NEG_ACTION_RE.search(m.group("gap")):
            continue                              # the action is directly negated
        return True
    return False
_OPT_IN_RE = re.compile(r"<!--\s*content-advisory:\s*opted-in\s*-->", re.IGNORECASE)
_HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
# Override markers route through the shared `override_marker` SSoT (code spans stripped, slug
# boundary-matched). Two distinct forms: the per-id `advisory-eval CN-NN` (silences one note's label)
# and the id-less `advisory-eval-prose` (silences the reader-facing prose). They are kept DISTINCT so a
# per-note override never silences unrelated prose (Codex P1); the slug boundary in `override_targets`
# is what keeps `advisory-eval` from firing on an `advisory-eval-prose` marker.


def _read(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except (OSError, UnicodeDecodeError):
        return None


def _overrides(text, slug):
    """The set of CN-NN ids overridden for `slug` (e.g. `advisory-eval`) — via the shared SSoT, so a
    marker quoted inside a code span is not honored and a per-id override does not bleed across slugs."""
    return {t[0] for t in override_targets(text, slug, r"(CN-[0-9]+)")}


def _has_block(text, btype):
    """True if `text` carries a real apodictic:<btype> block (a parsed carrier, not a prose mention)."""
    if art is None:
        return ("apodictic:%s" % btype) in (text or "")
    return any(bt == btype for bt, _o, _e in art.parse_blocks(text or ""))


def parse_notes(text):
    """[(obj_or_None, schema_errs, index), ...] for each apodictic:content_note block."""
    out = []
    if not text or art is None:
        return out
    schema = art.load_schema(_SCHEMA_ID)
    idx = 0
    for btype, obj, jerr in art.parse_blocks(text):
        if btype != "content_note":
            continue
        idx += 1
        where = "content_note #%d" % idx
        if jerr:
            out.append((None, ["%s: invalid JSON — %s" % (where, jerr)], idx))
            continue
        errs = art.validate_obj(obj, schema, where)
        if isinstance(obj, dict):
            # conditional: category 'other' needs a non-empty label (subset engine can't express it)
            if obj.get("category") == "other" and not (obj.get("label") or "").strip():
                errs.append("%s: category 'other' requires a non-empty 'label'" % where)
            # non-empty-string loci elements (the schema only checks they are strings).
            # Guard on list: a non-array `loci` (e.g. a bare string) is already a schema type error;
            # iterating it here would walk its characters and emit spurious "loci[n] is empty" noise.
            loci = obj.get("loci")
            if isinstance(loci, list):
                for j, locus in enumerate(loci):
                    if isinstance(locus, str) and not locus.strip():
                        errs.append("%s: loci[%d] is empty" % (where, j))
        out.append((obj, errs, idx))
    return out


def advisory(text, strict=False):
    """Run the Content-Advisory integrity checks. Returns (code, lines)."""
    lines, errs, warns = [], [], []
    notes = parse_notes(text)
    # A filename-matched advisory with NO parsed note blocks is not a free pass: the reader-facing
    # PROSE checks below (A3 severity leak, W1 prescriptive drift, W2 opt-in) must still run on `text` —
    # an advisory carrying "Must-Fix; should cut this scene" in prose with no structured note must still
    # fail under --strict (Codex P1). Only the note-bound checks (A1/A2 + the per-id label scans) skip,
    # which they do naturally by iterating the empty list.
    if not notes:
        lines.append("content-advisory: no content_note blocks found — prose-level checks only")

    # A1 — schema / JSON / conditional validity
    for _obj, schema_errs, _idx in notes:
        for e in schema_errs:
            errs.append("A1 schema: %s" % e)

    valid = [(obj, idx) for obj, schema_errs, idx in notes if obj is not None and not schema_errs]
    seen = {}
    for obj, idx in valid:
        seen.setdefault(obj.get("id"), []).append(idx)
    for cid, where in sorted(seen.items()):
        if len(where) > 1:
            errs.append("A1 schema: %s appears %d times (ids must be unique)" % (cid, len(where)))

    # A2 — locus presence & shape
    for obj, _idx in valid:
        for locus in obj.get("loci") or []:
            if not isinstance(locus, str) or not locus.strip() or not _LOCUS_RE.search(locus):
                errs.append("A2 locus shape: %s has a malformed / non-locus entry %r (need a chapter "
                            "/ §section / ¶ / line / page token)" % (obj.get("id"), locus))

    visible = _HTML_COMMENT_RE.sub("", text or "")  # reader-facing prose (note blocks stripped)
    note_labels = [(obj.get("id"), obj.get("label") or "") for obj, _ in valid]

    # A3 — no editorial-severity leak (the advisory is not a defect list)
    if _SEVERITY_RE.search(visible):
        errs.append("A3 severity leak: the advisory's reader-facing prose carries an editorial "
                    "Must/Should/Could-Fix token — content notes are advisories, not findings")
    for cid, label in note_labels:
        if _SEVERITY_RE.search(label):
            errs.append("A3 severity leak: %s's label carries an editorial severity token" % cid)
    if _has_block(text, "finding"):
        errs.append("A3 severity leak: the advisory artifact contains an apodictic:finding block — "
                    "a content advisory must not carry findings")

    # W1 — prescriptive drift (firewall; advisory, ERROR --strict; per-id / prose override)
    eval_overrides = _overrides(text, "advisory-eval")
    for cid, label in note_labels:
        if _prescribes(label) and cid not in eval_overrides:
            warns.append("W1 prescriptive drift: %s's label prescribes a revision ('should cut/soften "
                         "…') — the advisory describes depicted content, it does not prescribe" % cid)
    # prose-level prescription (not id-bound): silenced ONLY by the prose-scoped override, never by a
    # per-id `advisory-eval CN-NN` (a note-specific override must not suppress unrelated prose, Codex P1)
    if not override_targets(text or "", "advisory-eval-prose"):
        # scan prose minus the note labels already handled
        if _prescribes(visible):
            warns.append("W1 prescriptive drift: the advisory prose prescribes a revision "
                         "('should cut/soften …') — describe the depicted content, do not prescribe")

    # W2 — opt-in marker (generated only on request)
    if not _OPT_IN_RE.search(text or ""):
        warns.append("W2 opt-in marker: the advisory lacks the `<!-- content-advisory: opted-in -->` "
                     "marker — a content advisory is generated only on author request")

    # Report
    lines.append("content-advisory: %d note(s)%s" % (
        len(notes), "" if len(valid) == len(notes) else " (%d well-formed)" % len(valid)))
    for obj, _idx in valid:
        lines.append("  %-7s %-18s %s/%s" % (obj.get("id"), obj.get("category"),
                                             obj.get("intensity"), obj.get("depiction")))
    for e in errs:
        lines.append("  ERROR: %s" % e)
    for w in warns:
        lines.append("  %s: %s" % ("ERROR (--strict)" if strict else "WARN", w))

    if errs or (strict and warns):
        lines.append("content-advisory: FAIL (%d error(s)%s)"
                     % (len(errs), ", %d strict warn(s)" % len(warns) if (strict and warns) else ""))
        return 1, lines
    if warns:
        lines.append("WARN: content-advisory: %d advisory gap(s) — see W1/W2 above" % len(warns))
    else:
        lines.append("content-advisory: PASS (schema + locus shape + no-severity-leak + descriptive "
                     "+ opt-in)")
    return 0, lines


# ---------------------------------------------------------------- resolution

def _newest(paths):
    return max(paths, key=os.path.getmtime) if paths else None


def resolve(paths):
    if len(paths) == 1 and os.path.isdir(paths[0]):
        return _newest(glob.glob(os.path.join(paths[0], _ADVISORY_GLOB)))
    for p in paths:
        if _has_block(_read(p) or "", "content_note"):
            return p
    return None


def run(paths, strict=False):
    path = resolve(paths)
    if not path:
        return 2, ["content-advisory: no advisory artifact found (need a *_Content_Advisory_*.md or a "
                   "file with apodictic:content_note blocks) — nothing to check"]
    text = _read(path)
    if text is None:
        return 2, ["content-advisory: cannot read %s" % path]
    return advisory(text, strict=strict)


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

    OPT = "<!-- content-advisory: opted-in -->\n\n"

    def note(cid, category="violence", intensity="high", depiction="on-page", label="", loci=("Ch 7 ¶12-18",)):
        obj = {"schema": _SCHEMA_ID, "id": cid, "category": category, "intensity": intensity,
               "depiction": depiction, "label": label, "loci": list(loci)}
        return "<!-- apodictic:content_note\n%s\n-->" % _j.dumps(obj)

    # clean: opted-in advisory with two notes
    TWO = note("CN-01") + "\n" + note("CN-02", category="death-grief", intensity="low", depiction="referenced", loci=["Ch 2"])
    chk("clean_two_notes", advisory(OPT + TWO)[0] == 0)

    # A1 — schema
    chk("a1_bad_category", advisory(OPT + note("CN-01", category="gore"))[0] == 1)
    chk("a1_bad_intensity", advisory(OPT + note("CN-01", intensity="extreme"))[0] == 1)
    chk("a1_bad_depiction", advisory(OPT + note("CN-01", depiction="implied"))[0] == 1)
    chk("a1_bad_id", advisory(OPT + note("CN-1"))[0] == 1)
    chk("a1_empty_loci", advisory(OPT + note("CN-01", loci=[]))[0] == 1)
    chk("a1_empty_loci_element", advisory(OPT + note("CN-01", loci=[""]))[0] == 1)
    # a non-array loci (bare string) is a schema type error, NOT a char-by-char "loci[n] empty" walk
    code, lines = advisory(OPT + '<!-- apodictic:content_note\n{"schema":"apodictic.content_note.v1",'
                           '"id":"CN-01","category":"violence","intensity":"high","depiction":"on-page",'
                           '"label":"","loci":"Ch 7"}\n-->')
    chk("a1_loci_string_no_char_walk",
        code == 1 and any("must be type array" in ln for ln in lines)
        and not any("loci[" in ln for ln in lines))
    chk("a1_other_needs_label", advisory(OPT + note("CN-01", category="other", label=""))[0] == 1)
    chk("a1_other_with_label_ok", advisory(OPT + note("CN-01", category="other", label="body horror"))[0] == 0)
    code, lines = advisory(OPT + '<!-- apodictic:content_note\n{"schema":"apodictic.content_note.v1"\n-->')
    chk("a1_bad_json", code == 1 and any("A1 schema" in ln for ln in lines))
    code, lines = advisory(OPT + note("CN-01") + "\n" + note("CN-01", category="abuse"))
    chk("a1_duplicate_id", code == 1 and any("appears 2 times" in ln for ln in lines))

    # A2 — locus shape
    chk("a2_non_locus", advisory(OPT + note("CN-01", loci=["the battlefield"]))[0] == 1)
    chk("a2_section_locus_ok", advisory(OPT + note("CN-01", loci=["Ch 7 §2"]))[0] == 0)

    # A3 — no editorial-severity leak
    code, lines = advisory(OPT + TWO + "\n## Notes\n\n- The Ch 7 violence is a Must-Fix.\n")
    chk("a3_severity_in_prose", code == 1 and any("A3 severity leak" in ln for ln in lines))
    chk("a3_severity_in_label",
        advisory(OPT + note("CN-01", category="other", label="graphic — Should-Fix"))[0] == 1)
    finding = '<!-- apodictic:finding\n{"schema":"apodictic.finding.v1","id":"F-P5-01","mechanism":"m","severity":"Must-Fix","confidence":"HIGH","evidence_refs":["c"],"fix_class":"x","risk_if_fixed":"y"}\n-->'
    code, lines = advisory(OPT + TWO + "\n" + finding)
    chk("a3_finding_block_present", code == 1 and any("apodictic:finding block" in ln for ln in lines))

    # W1 — prescriptive drift (advisory; ERROR --strict; override; not bare adjectives)
    presc = OPT + TWO + "\n## Notes\n\n- The reader should cut this scene to lower the intensity.\n"
    code, lines = advisory(presc)
    chk("w1_prescriptive_advisory", code == 0 and any("W1 prescriptive drift" in ln for ln in lines))
    chk("w1_prescriptive_strict_fails", advisory(presc, strict=True)[0] == 1)
    # a bare descriptive adjective ("excessive") must NOT trip W1
    chk("w1_descriptive_adjective_clean",
        not any("W1" in ln for ln in advisory(OPT + note("CN-01", category="other", label="excessive blood loss, graphic"))[1]))
    # an innocent "should be aware" prose line must NOT trip W1
    chk("w1_should_be_aware_clean",
        not any("W1" in ln for ln in advisory(OPT + TWO + "\n\nReaders should be aware the violence is graphic and frequent.\n")[1]))
    # label-level prescription with per-id override is silenced
    ov = "<!-- override: advisory-eval CN-03 — quoting the author's own marketing note -->\n"
    chk("w1_label_override",
        not any("W1" in ln for ln in advisory(OPT + ov + note("CN-03", category="other", label="should soften the torture depiction"))[1]))
    # a per-id override must NOT silence UNRELATED prescriptive PROSE (Codex P1)
    presc_prose = "\n## Notes\n\n- The reader should cut this scene to lower the intensity.\n"
    chk("w1_per_id_override_keeps_unrelated_prose",
        any("W1 prescriptive" in ln for ln in advisory(OPT + ov + note("CN-03") + presc_prose)[1]))
    # the prose-scoped override (id-less) DOES silence prose prescription
    prose_ov = "<!-- override: advisory-eval-prose — author's own jacket copy -->\n"
    chk("w1_prose_override_silences_prose",
        not any("W1 prescriptive" in ln for ln in advisory(OPT + prose_ov + TWO + presc_prose)[1]))
    # code-span decoy (the bypass this migration closes): an override quoted INSIDE a code span is a
    # documentation example, not a live directive — it must NOT silence W1, in EITHER CommonMark form.
    presc_label = note("CN-03", category="other", label="should soften the torture depiction")
    chk("w1_inline_codespan_override_does_not_silence",
        any("W1" in ln for ln in advisory(OPT + "`" + ov.strip() + "`\n" + presc_label)[1]))
    chk("w1_fenced_codespan_override_does_not_silence",
        any("W1" in ln for ln in advisory(OPT + "```\n" + ov.strip() + "\n```\n" + presc_label)[1]))
    chk("w1_prose_codespan_override_does_not_silence",
        any("W1 prescriptive" in ln for ln in advisory(OPT + "`" + prose_ov.strip() + "`\n" + TWO + presc_prose)[1]))

    # W2 — opt-in marker
    code, lines = advisory(TWO)  # no opt-in marker
    chk("w2_missing_marker_advisory", code == 0 and any("W2 opt-in marker" in ln for ln in lines))
    chk("w2_missing_marker_strict_fails", advisory(TWO, strict=True)[0] == 1)

    # no blocks -> prose-level checks still run (Codex P1): a no-notes advisory is NOT a free pass.
    # Clean prose (with opt-in) still passes; but severity/prescriptive prose must be caught.
    chk("no_notes_clean_with_optin_ok", advisory(OPT + "Descriptive prose about the depicted content.\n")[0] == 0)
    chk("no_notes_severity_prose_fails",   # A3 fires (hard ERROR) even with zero parsed notes
        advisory("This chapter is a Must-Fix.\n")[0] == 1)
    chk("no_notes_prescriptive_prose_strict_fails",  # W1 fires under --strict with zero notes
        advisory("We should cut this scene.\n", strict=True)[0] == 1)
    chk("no_notes_codex_repro_strict_fails",  # Codex's exact P1 repro
        advisory("Must-Fix; should cut this scene", strict=True)[0] == 1)
    # …and the old "no notes, no severity/prescription, no opt-in" path still returns 0 (W2 is a
    # non-strict WARN, not an error).
    chk("no_notes_noop", advisory("# Notes\nnothing structured\n")[0] == 0)

    # W1 P2 (Codex): ordinary prescriptions the prior regex missed — gerund action ("recommend
    # cutting") and the `must` modal ("must cut") — must fire W1.
    chk("w1_recommend_cutting_fires",
        any("W1 prescriptive" in ln for ln in advisory(OPT + TWO + "\nWe recommend cutting the torture passage.\n")[1]))
    chk("w1_must_cut_fires",
        any("W1 prescriptive" in ln for ln in advisory(OPT + TWO + "\nThe editor says you must cut this scene.\n")[1]))
    # …but a NEGATED construction describes, it does not prescribe. Negation can sit on the ACTION
    # ("recommends no cut", "should not cut", "recommend not cutting") or on the MODAL ("do not /
    # don't / never / cannot recommend cutting", incl. across a comma aside) — all must stay clean.
    for clean in ("the advisory recommends no cut to this scene",     # action negated
                  "the editor should not cut this passage",
                  "we recommend not cutting this passage",
                  "we do not recommend cutting this scene",           # modal negated (Codex P2 FP)
                  "we don't recommend cutting this scene",
                  "we never recommend cutting a scene",
                  "we cannot recommend cutting this scene",
                  "we do not, in good conscience, recommend cutting this scene"):  # negator across an aside
        chk("w1_negated_prescription_clean::%s" % clean[:24],
            not any("W1 prescriptive" in ln for ln in advisory(OPT + TWO + "\n" + clean + "\n")[1]))
    # …and a negator binding an UNRELATED word mid-gap does NOT negate the action — "recommend, with no
    # hesitation, cutting" is still a prescription and must fire (Codex P2 false-negative).
    chk("w1_unrelated_no_still_fires",
        any("W1 prescriptive" in ln for ln in
            advisory(OPT + TWO + "\nWe recommend, with no hesitation, cutting this scene.\n")[1]))
    # "against" is a negator too: "recommend against cutting" / "advise against removing" prescribe
    # NOT doing the action — they must stay clean (Codex P2). Also handles "against ever removing" and
    # "against recommending …".
    for clean in ("we recommend against cutting this scene",
                  "we advise against removing the passage",
                  "the guidance advises against ever removing it",
                  "we are against recommending cutting here"):
        chk("w1_against_negation_clean::%s" % clean[:24],
            not any("W1 prescriptive" in ln for ln in advisory(OPT + TWO + "\n" + clean + "\n")[1]))
    # …but "against" in a comma-closed aside does NOT negate the action — "recommend, against all odds,
    # cutting" still prescribes the cut and must fire.
    chk("w1_against_aside_still_fires",
        any("W1 prescriptive" in ln for ln in
            advisory(OPT + TWO + "\nWe recommend, against all odds, cutting this scene.\n")[1]))

    # resolution: glob, explicit file, no-artifact exit 2, decoy prose mention skipped
    import tempfile
    import shutil
    d = tempfile.mkdtemp()
    try:
        p = os.path.join(d, "Proj_Content_Advisory_run.md")
        with open(p, "w", encoding="utf-8", newline="") as fh:
            fh.write("# Content Advisory\n" + OPT + TWO + "\n")
        chk("run_folder_resolution", run([d])[0] == 0)
        chk("explicit_file_resolution", run([p])[0] == 0)
        chk("no_artifact_exit2", run([os.path.join(d, "nope.md")])[0] == 2)
        decoy = os.path.join(d, "spec.md")
        with open(decoy, "w", encoding="utf-8", newline="") as fh:
            fh.write("# Spec\nThe apodictic:content_note block format is described here.\n")
        chk("resolver_skips_prose_mention", resolve([decoy, p]) == p)
    finally:
        shutil.rmtree(d, ignore_errors=True)

    print("Self-test: PASS" if rc["v"] == 0 else "Self-test: FAIL")
    return rc["v"]


def main(argv):
    if "--self-test" in argv:
        return run_self_test()
    args = [a for a in argv[1:] if a != "content-advisory"]
    strict = "--strict" in args
    paths = [a for a in args if not a.startswith("--")]
    if not paths:
        print("Usage: content_advisory.py content-advisory <run_folder|files...> [--strict] | --self-test")
        return 2
    code, lines = run(paths, strict=strict)
    for ln in lines:
        print(ln)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
