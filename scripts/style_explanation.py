#!/usr/bin/env python3
"""style-explanation — structural integrity for the Interpretable Stylometric Explanation overlay.

`validate.sh style-explanation <author_root|files>` shells out here. The Author Voice Fingerprint
(#9) measures how distinctive a writer's voice is and persists it across a career — but only as
NUMBERS. This capability is the LABELLING LAYER: it attaches a natural-language description to an
already-measured stylistic feature ("the prose leans hard on the definite article", "function-word
profile concentrated in the/and/but"), each label bound by provenance to the exact measured feature
it glosses. It is a reading aid for the fingerprint, not a new measurement and not advice. It does NO
new stylometry — it CONSUMES the SETEC voice_profile per-family feature inventory
(families.<family>.top_features[].{feature, mean, sd, cv}) and adds only the LABEL text plus its
binding back to a measured feature. Each label is an apodictic.style_label.v1 block.

The module is strictly DESCRIPTIVE. The whole design is built so the prescriptive sentence ("write
more like X", "vary your function-word profile") is UNREPRESENTABLE in the structured fields — there
is no target/goal/recommendation/rewrite/compare_to_author field, `frame` and `direction` admit only
descriptive values — and the one residual free-text surface (`label`) is scanned by X4. The profile is
local-only (no external call). It is the riskiest of its wave: one preposition from a Firewall breach.

  X1 schema        a style_label block fails its schema (bad feature_family/frame/direction/magnitude
                   enum, malformed SL-NN id, missing required field, broken JSON, or a duplicate id).
                   ERROR.
  X2 provenance    a label whose `feature_ref` is empty or absent — a style claim with no measured
                   feature behind it is treated as FABRICATED and rejected (the module consumes; an
                   un-sourced label can't be traced — the #9 F2 / centroid_ref discipline). ERROR.
  X3 no-severity   the reader-facing prose or any `label` carries an editorial Must/Should/Could-Fix
                   token, OR an apodictic:finding block is present in the artifact. A style label is
                   not a defect (the Content-Advisory A3 orthogonal-severity discipline). ERROR.
  X4 descriptive   a `label` or the visible prose matches a PRESCRIPTIVE construction aimed at the
                   voice (a modal/imperative verb governing a style change) OR a COMPARISON-TO-EMULATE
                   construction ("write/sound more like …", "emulate …", "model your prose on …"). The
                   bare descriptive adjective ("the prose is terse", "elevated use of the definite
                   article") does NOT fire — only the directive. Advisory; ERROR under --strict.
                   Override per id: <!-- override: style-frame SL-NN — <why> --> (label-level matches);
                   the bare <!-- override: style-frame — <why> --> silences prose-level (non-id) matches
                   — the Content-Advisory W1 prose-vs-label split.
  X5 same-register a `describes-cluster` label referencing >= 2 labels (a cluster claim) whose
                   referenced labels do not all share a `register` — a cross-register cluster is a
                   comparability error the AI-prose domain-shift caution forbids (the #9 F3 shape).
                   ERROR.
  X6 local-only    the artifact lacks a `<!-- author-style-explanation: local-only -->` marker, or it
                   references an external http(s) URL — a labelled voice profile must never be
                   transmitted. Advisory WARN ONLY, never escalated under --strict (a self-attestation
                   hygiene check; the binding guarantee is the module's no-external-call rule, #9 W2).
  W1 seed/coverage no style_label blocks resolved => no-op; OR only one feature glossed => the overlay
                   is thin. Advisory; ERROR under --strict for the THIN case only, never the no-op.

Reuses apodictic_artifacts (block grammar + schema engine). The labels live in #9's existing
Author_Voice_Profile.md (composing with voice_fingerprint blocks) OR a sibling
Author_Style_Explanation*.md; the resolver handles both via parsed-block detection. The
embedding/scoring model that GENERATES the labels is a deferred M2 lazy-import + skipif seam — this
M1 validator never calls a model and enforces the firewall regardless of who authored the labels.
See docs/interpretable-stylometric-explanation.md.

  style_explanation.py style-explanation <author_root|files...> [--strict]
  style_explanation.py --self-test

Exit: 0 clean / WARN-only, 1 ERROR (or WARN under --strict, EXCEPT X6 which stays WARN), 2 usage.
"""
import glob
import os
import re
import sys

try:
    import apodictic_artifacts as art
except ImportError:
    art = None

_SCHEMA_ID = "apodictic.style_label.v1"
_PROFILE_GLOBS = ("Author_Style_Explanation*.md", "Author_Voice_Profile*.md")

_SL_REF_RE = re.compile(r"\bSL-[0-9]+\b")
_HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
_LOCAL_ONLY_RE = re.compile(r"<!--\s*author-style-explanation:\s*local-only\s*-->", re.IGNORECASE)
_EXTERNAL_URL_RE = re.compile(r"https?://", re.IGNORECASE)
_SEVERITY_RE = re.compile(r"\b(?:Must|Should|Could)-Fix\b")

# X4 — a PRESCRIPTIVE construction aimed at the author's voice: a modal/imperative verb governing a
# STYLE change ("you should vary your function-word profile", "tighten your sentences"). This is the
# author_fingerprint.py F4 directive shape, broadened to the style-feature vocabulary this module
# names. A bare descriptive adjective ("the prose is terse", "elevated use of the definite article")
# does NOT match — only a directive verb + a voice/style object.
#
# _STYLE_OBJ — a style/voice OBJECT the directive can govern, the vocabulary this module names. Broad
# enough to catch "reduce your reliance on the definite article" / "increase your lexical diversity";
# the verb arm is what makes it prescriptive, so a bare descriptive use of any of these nouns does NOT
# fire on its own.
_STYLE_OBJ = (r"(?:voice|cadence|prose|styl(?:e|istic)|sentences?|function[\s-]words?|"
              r"diction|syntax|vocabulary|rhythm|range|register|reliance|"
              r"(?:lexical[\s-])?diversity|distinctiveness|repetition|profile)")
# Directive verbs split by adjective-ambiguity (the #9 DC6 risk: elevated/reduced/lower are also the
# DESCRIPTIVE `direction` words). UNAMBIGUOUS imperatives ("vary/tighten/diversify the cadence") may
# govern a `the`/`your`/`its` object. ADJECTIVE-AMBIGUOUS verbs ("reduce/lower/increase/elevate …")
# share a surface with the descriptive participle/comparative ("reduced diversity", "lower
# diversity"), so they only fire when they govern a possessive `your`/`its` object — the
# instruction-at-the-author signature a bare descriptive use never carries.
_DV_IMPERATIVE = (r"(?:vary|tighten|loosen|expand|broaden|chang(?:e|ing)|diversify|fix|"
                  r"cut\s+back|dial\s+(?:back|down)|lean\s+(?:less|more))")
_DV_AMBIGUOUS = (r"(?:increas\w*|reduc\w*|rais\w*|lower\w*|shorten\w*|lengthen\w*|simplif\w+|elevat\w*)")
# Both arms allow a direct object or a "<noun> on/in <object>" bridge ("reduce your reliance ON the …").
_OBJ_TAIL = r"(?:" + _STYLE_OBJ + r"\b|\w+\s+(?:on|in)\s+(?:your\s+|the\s+|its\s+)?" + _STYLE_OBJ + r"\b)"
_PRESCRIPTIVE_RE = re.compile(
    r"\byou\s+(?:should|must|need\s+to|ought\s+to|have\s+to|'?d\s+better)\b"
    r"|\b" + _DV_IMPERATIVE + r"\s+(?:your\s+|the\s+|its\s+)?" + _OBJ_TAIL +
    r"|\b" + _DV_AMBIGUOUS + r"\s+(?:your|its)\s+" + _OBJ_TAIL +
    r"|\b(?:should|recommend(?:ed|ing|s)?|consider|advise[sd]?|suggest(?:ed|ing|s)?)\b"
    r"[^.;\n]{0,40}?\b(?:" + _DV_IMPERATIVE + r"|" + _DV_AMBIGUOUS + r")\b",
    re.IGNORECASE)
# X4 — a COMPARISON-TO-EMULATE construction ("write more like Hemingway", "sound more like X",
# "emulate …", "model your prose on …"). A first-class match, distinct from the generic prescriptive
# verb (DC5): the firewall blocks naming a target author to imitate, not just generic style advice.
_EMULATE_RE = re.compile(
    r"\b(?:write|sound|read)\s+(?:more\s+|just\s+)?like\b"
    r"|\bemulat\w+\b"
    r"|\bmodel\s+(?:your|the|its)?\s*" + _STYLE_OBJ + r"?\s*\bon\b"
    r"|\bimitat\w+\s+(?:the\s+)?" + _STYLE_OBJ,
    re.IGNORECASE)
# X4 override: per-id (`style-frame SL-NN`) silences a LABEL match; the bare `style-frame` (id-less)
# silences PROSE-level matches — a per-id override must never suppress unrelated prose (the
# content_advisory.py advisory-eval / advisory-eval-prose split, Codex P1).
_OVERRIDE_ID_RE = re.compile(r"<!--\s*override:\s*style-frame\s+(SL-[0-9]+)\b", re.IGNORECASE)
_OVERRIDE_PROSE_RE = re.compile(r"<!--\s*override:\s*style-frame\s*(?:—|--|-)", re.IGNORECASE)


def _read(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return None


def _id_overrides(text):
    """The set of SL-ids carrying a per-id `style-frame SL-NN` override."""
    return {m.group(1).upper() for m in _OVERRIDE_ID_RE.finditer(text or "")}


def _prescribes(text):
    """True if `text` carries a prescriptive voice-directive or a comparison-to-emulate construction."""
    text = text or ""
    return bool(_PRESCRIPTIVE_RE.search(text) or _EMULATE_RE.search(text))


def parse_labels(text):
    """[(obj_or_None, schema_errs, index), ...] for each apodictic:style_label block."""
    out = []
    if not text or art is None:
        return out
    schema = art.load_schema(_SCHEMA_ID)
    idx = 0
    for btype, obj, jerr in art.parse_blocks(text):
        if btype != "style_label":
            continue
        idx += 1
        where = "style_label #%d" % idx
        if jerr:
            out.append((None, ["%s: invalid JSON — %s" % (where, jerr)], idx))
            continue
        errs = art.validate_obj(obj, schema, where)
        out.append((obj, errs, idx))
    return out


def _cluster_refs(obj):
    """The SL-ids a describes-cluster label references (in label text + feature_ref), excluding self."""
    if not isinstance(obj, dict):
        return []
    text = "%s %s" % (obj.get("label") or "", obj.get("feature_ref") or "")
    refs, self_id = [], obj.get("id")
    for r in _SL_REF_RE.findall(text):
        if r != self_id and r not in refs:
            refs.append(r)
    return refs


def explain_profile(text, strict=False):
    """Run the Interpretable Stylometric Explanation integrity checks. Returns (code, lines)."""
    lines, errs, warns, x6 = [], [], [], []
    labels = parse_labels(text)
    if not labels:
        return 0, ["style-explanation: no style_label blocks found — nothing to check"]

    # X1 — schema / JSON validity
    for _obj, schema_errs, _idx in labels:
        for e in schema_errs:
            errs.append("X1 schema: %s" % e)

    valid = [(obj, idx) for obj, schema_errs, idx in labels if obj is not None and not schema_errs]
    by_id, seen = {}, {}
    for obj, idx in valid:
        seen.setdefault(obj.get("id"), []).append(idx)
        by_id.setdefault(obj.get("id"), obj)
    for sid, where in sorted(seen.items()):
        if len(where) > 1:
            errs.append("X1 schema: %s appears %d times (ids must be unique)" % (sid, len(where)))

    # X2 — provenance / anti-fabrication: every label names a consumed measured feature via feature_ref
    for obj, _idx in valid:
        if not (obj.get("feature_ref") or "").strip():
            errs.append("X2 provenance: %s has an empty/absent feature_ref — a style claim with no "
                        "measured feature behind it is fabricated; the module consumes existing "
                        "measurements, it does not invent features" % obj.get("id"))

    visible = _HTML_COMMENT_RE.sub("", text or "")  # reader-facing prose (label blocks stripped)
    label_texts = [(obj.get("id"), obj.get("label") or "") for obj, _ in valid]

    # X3 — no editorial-severity leak (a style label is not a defect)
    if _SEVERITY_RE.search(visible):
        errs.append("X3 no-severity: the explanation's reader-facing prose carries an editorial "
                    "Must/Should/Could-Fix token — a style label is a description, not a defect")
    for sid, label in label_texts:
        if _SEVERITY_RE.search(label):
            errs.append("X3 no-severity: %s's label carries an editorial severity token — a style "
                        "label takes no editorial severity" % sid)
    if _has_block(text, "finding"):
        errs.append("X3 no-severity: the explanation artifact contains an apodictic:finding block — "
                    "a style explanation must not carry findings")

    # X5 — same-register cluster (a describes-cluster label referencing >= 2 labels must share register)
    for obj, _idx in valid:
        if obj.get("frame") != "describes-cluster":
            continue
        refs = _cluster_refs(obj)
        if len(refs) < 2:
            continue
        unknown = [r for r in refs if r not in by_id]
        if unknown:
            errs.append("X5 same-register: %s is a describes-cluster claim referencing unknown label "
                        "id(s) %s — every SL-… in a cluster must resolve (a typo can otherwise hide a "
                        "cross-register cluster)" % (obj.get("id"), ", ".join(sorted(unknown))))
            continue
        registers = {(by_id[r].get("register") or "").strip().lower() for r in refs}
        registers.add((obj.get("register") or "").strip().lower())
        if len([r for r in registers if r]) > 1 or "" in registers:
            named = ", ".join(sorted(r for r in registers if r)) or "(blank)"
            errs.append("X5 same-register: %s clusters labels across registers (%s) — a cluster is "
                        "only comparable within a register (the AI-prose domain-shift guard)"
                        % (obj.get("id"), named))

    # X4 — descriptive, not prescriptive (the signature firewall gate; advisory, ERROR --strict)
    for sid, label in label_texts:
        if _prescribes(label) and sid not in _id_overrides(text):
            warns.append("X4 descriptive: %s's label prescribes a voice change or names a model to "
                         "emulate ('vary your …', 'write more like X') — the overlay describes a "
                         "measured feature, it never prescribes" % sid)
    # prose-level prescription (not id-bound): silenced ONLY by the bare `style-frame` prose override,
    # never by a per-id `style-frame SL-NN` (a per-label override must not suppress unrelated prose).
    if not _OVERRIDE_PROSE_RE.search(text or ""):
        if _prescribes(visible):
            warns.append("X4 descriptive: the explanation prose prescribes a voice change or names a "
                         "model to emulate ('vary your …', 'write more like X') — describe the "
                         "measured feature, do not prescribe")

    # X6 — local-only hygiene (advisory WARN ONLY, never escalated under --strict)
    if not _LOCAL_ONLY_RE.search(text or ""):
        x6.append("X6 local-only: the artifact lacks a `<!-- author-style-explanation: local-only -->` "
                  "marker — a labelled voice profile is voice-cloning-adjacent and never transmitted")
    # The URL scan must cover the STRUCTURED label fields, not just the reader-facing prose: a style_label
    # block is an HTML comment, so it is stripped from `visible` — a URL hidden in a label's
    # `label`/`feature_ref`/etc. would otherwise evade X6 (mirrors the X3 no-severity prose+label split).
    url_scan = [visible] + [v for obj, _e, _i in labels if isinstance(obj, dict)
                            for v in obj.values() if isinstance(v, str)]
    if any(_EXTERNAL_URL_RE.search(s) for s in url_scan):
        x6.append("X6 local-only: the artifact references an external http(s) URL (in the reader-facing "
                  "prose or a structured label field) — a labelled voice profile is local-only and makes "
                  "no external call")

    # W1 — seed / coverage (single glossed feature => thin overlay; advisory, ERROR --strict)
    if len(valid) == 1:
        warns.append("W1 seed/coverage: only one feature is glossed — the overlay is thin; a "
                     "descriptive explanation reads better across the handful of salient features")

    # Report
    lines.append("style-explanation: %d label(s)%s" % (
        len(labels), "" if len(valid) == len(labels) else " (%d well-formed)" % len(valid)))
    for obj, _idx in valid:
        lines.append("  %-8s %-20s %s/%s" % (obj.get("id"), obj.get("feature_family"),
                                             obj.get("direction"), obj.get("magnitude")))
    for e in errs:
        lines.append("  ERROR: %s" % e)
    for w in warns:
        lines.append("  %s: %s" % ("ERROR (--strict)" if strict else "WARN", w))
    for w in x6:
        lines.append("  WARN: %s" % w)  # X6 stays WARN even under --strict

    if errs or (strict and warns):
        lines.append("style-explanation: FAIL (%d error(s)%s)"
                     % (len(errs), ", %d strict warn(s)" % len(warns) if (strict and warns) else ""))
        return 1, lines
    if warns or x6:
        lines.append("WARN: style-explanation: %d advisory gap(s) — see X4/X6/W1 above"
                     % (len(warns) + len(x6)))
    else:
        lines.append("style-explanation: PASS (schema + provenance + no-severity + "
                     "descriptive-not-prescriptive + same-register)")
    return 0, lines


# ---------------------------------------------------------------- resolution

def _newest(paths):
    return max(paths, key=os.path.getmtime) if paths else None


def _has_block(text, btype):
    """True if `text` carries a real apodictic:<btype> block (a parsed carrier, not a prose mention).

    Classifying on parsed blocks — not a raw substring — keeps a docs/spec file that merely *names*
    `apodictic:style_label` in prose from winning resolution over the real profile (the M2 anti-pattern)."""
    if art is None:
        return ("apodictic:%s" % btype) in (text or "")  # degraded: no engine to parse with
    return any(bt == btype for bt, _o, _e in art.parse_blocks(text or ""))


def resolve(paths):
    if len(paths) == 1 and os.path.isdir(paths[0]):
        hits = []
        for g in _PROFILE_GLOBS:
            hits.extend(glob.glob(os.path.join(paths[0], g)))
        # Prefer a folder file that actually carries style_label blocks (the sibling
        # Author_Voice_Profile.md may only hold voice_fingerprint blocks).
        with_blocks = [p for p in hits if _has_block(_read(p) or "", "style_label")]
        return _newest(with_blocks) or _newest(hits)
    for p in paths:
        if _has_block(_read(p) or "", "style_label"):
            return p
    return paths[0] if paths else None


def run(paths, strict=False):
    path = resolve(paths)
    if not path:
        return 2, ["style-explanation: no style-explanation artifact found (need an "
                   "Author_Style_Explanation*.md / Author_Voice_Profile*.md or a file with "
                   "apodictic:style_label blocks)"]
    text = _read(path)
    if text is None:
        return 2, ["style-explanation: cannot read %s" % path]
    return explain_profile(text, strict=strict)


# ---------------------------------------------------------------- self-test

def run_self_test():
    import json as _j
    rc = {"v": 0}

    def chk(name, cond):
        print("  %s: %s" % (name, "OK" if cond else "FAIL"))
        if not cond:
            rc["v"] = 1

    LOCAL = "<!-- author-style-explanation: local-only -->\n\n"

    def sl(sid, feature_family="function-words", frame="describes-feature", direction="elevated",
           magnitude="moderate", feature_ref="families.function_words.top_features[the]",
           label="The prose leans on the definite article.", register="literary-fiction",
           feature_tokens=None, extra=None):
        obj = {"schema": _SCHEMA_ID, "id": sid, "feature_family": feature_family, "frame": frame,
               "direction": direction, "magnitude": magnitude, "feature_ref": feature_ref,
               "label": label, "register": register}
        if feature_tokens is not None:
            obj["feature_tokens"] = feature_tokens
        if extra:
            obj.update(extra)
        return "<!-- apodictic:style_label\n%s\n-->" % _j.dumps(obj)

    TWO = (sl("SL-01", feature_ref="families.function_words.top_features[the]",
              label="The prose leans on the definite article.")
           + "\n" + sl("SL-02", feature_ref="families.function_words.top_features[and]",
                       label="Short coordinating runs on 'and' recur.",
                       feature_tokens=["and", "but"]))

    # clean: two same-register function-word labels + local-only marker, no prescriptive prose
    chk("clean_two_same_register", explain_profile(LOCAL + TWO)[0] == 0)

    # X1 — schema
    chk("x1_bad_family", explain_profile(LOCAL + sl("SL-01", feature_family="emoji") + "\n" + sl("SL-02"))[0] == 1)
    chk("x1_bad_frame", explain_profile(LOCAL + sl("SL-01", frame="prescribes-feature") + "\n" + sl("SL-02"))[0] == 1)
    chk("x1_bad_direction", explain_profile(LOCAL + sl("SL-01", direction="increase") + "\n" + sl("SL-02"))[0] == 1)
    chk("x1_bad_magnitude", explain_profile(LOCAL + sl("SL-01", magnitude="severe") + "\n" + sl("SL-02"))[0] == 1)
    chk("x1_bad_id", explain_profile(LOCAL + sl("SL-1") + "\n" + sl("SL-02"))[0] == 1)
    chk("x1_missing_field", explain_profile(LOCAL + sl("SL-01").replace('"frame"', '"frm"') + "\n" + sl("SL-02"))[0] == 1)
    code, lines = explain_profile(LOCAL + '<!-- apodictic:style_label\n{"schema":"apodictic.style_label.v1"\n-->')
    chk("x1_bad_json", code == 1 and any("X1 schema" in ln for ln in lines))
    code, lines = explain_profile(LOCAL + sl("SL-01") + "\n" + sl("SL-01", label="dup"))
    chk("x1_duplicate_id", code == 1 and any("appears 2 times" in ln for ln in lines))

    # X2 — provenance / anti-fabrication (empty / absent feature_ref)
    code, lines = explain_profile(LOCAL + sl("SL-01", feature_ref="") + "\n" + sl("SL-02"))
    chk("x2_empty_feature_ref", code == 1 and any("X2 provenance" in ln for ln in lines))
    # an ABSENT feature_ref (the field removed) is rejected too — first by X1 (it is `required`)
    absent = ('<!-- apodictic:style_label\n'
              + _j.dumps({"schema": _SCHEMA_ID, "id": "SL-01", "feature_family": "function-words",
                          "frame": "describes-feature", "direction": "elevated", "magnitude": "moderate",
                          "label": "no ref here", "register": "literary-fiction"})
              + "\n-->")
    chk("x2_absent_feature_ref_rejected", explain_profile(LOCAL + absent + "\n" + sl("SL-02"))[0] == 1)
    # absent feature_ref is first a schema (X1 required) failure, then X2 if it slips a blank through;
    # the blank-string case above is the X2 anti-fabrication floor.
    chk("x2_present_clean", not any("X2 provenance" in ln for ln in explain_profile(LOCAL + TWO)[1]))

    # X3 — no-severity (severity token in prose, in a label, embedded finding block)
    sev_prose = LOCAL + TWO + "\n## Notes\n\n- The definite-article lean is a Must-Fix.\n"
    code, lines = explain_profile(sev_prose)
    chk("x3_severity_in_prose", code == 1 and any("X3 no-severity" in ln for ln in lines))
    code, lines = explain_profile(LOCAL + sl("SL-01", label="This is a Should-Fix overuse.") + "\n" + sl("SL-02"))
    chk("x3_severity_in_label", code == 1 and any("X3 no-severity" in ln for ln in lines))
    fnd = ('\n<!-- apodictic:finding\n{"schema":"apodictic.finding.v1","id":"F-P5-01","mechanism":"m",'
           '"severity":"Must-Fix","confidence":"HIGH","evidence_refs":["c"],"fix_class":"x",'
           '"risk_if_fixed":"y"}\n-->\n')
    code, lines = explain_profile(LOCAL + TWO + fnd)
    chk("x3_embedded_finding_block", code == 1 and any("apodictic:finding block" in ln for ln in lines))

    # X4 — descriptive, not prescriptive (advisory; ERROR --strict; per-id + prose override)
    presc = LOCAL + sl("SL-01", label="You should vary your function-word profile.") + "\n" + sl("SL-02")
    code, lines = explain_profile(presc)
    chk("x4_prescriptive_label_advisory", code == 0 and any("X4 descriptive" in ln for ln in lines))
    chk("x4_prescriptive_label_strict_fails", explain_profile(presc, strict=True)[0] == 1)
    emulate = LOCAL + sl("SL-01", label="Write more like Hemingway here.") + "\n" + sl("SL-02")
    chk("x4_emulate_label_advisory", any("X4 descriptive" in ln for ln in explain_profile(emulate)[1]))
    chk("x4_emulate_label_strict_fails", explain_profile(emulate, strict=True)[0] == 1)
    # the bare descriptive label does NOT fire X4
    chk("x4_bare_descriptive_clean",
        not any("X4" in ln for ln in explain_profile(
            LOCAL + sl("SL-01", label="Elevated use of the definite article.") + "\n" + sl("SL-02"))[1]))
    # the DESCRIPTIVE direction adjectives (reduced/lower/elevated/increased) must NOT read as a
    # directive — the #9 DC6 risk: a participle/comparative gloss is indicative, not imperative
    chk("x4_reduced_adjective_clean",
        not any("X4" in ln for ln in explain_profile(
            LOCAL + sl("SL-01", direction="reduced", label="Reduced lexical diversity vs the author baseline.")
            + "\n" + sl("SL-02"))[1]))
    chk("x4_lower_comparative_clean",
        not any("X4" in ln for ln in explain_profile(
            LOCAL + sl("SL-01", direction="reduced", label="Lower lexical diversity than the author centroid.")
            + "\n" + sl("SL-02"))[1]))
    # but the same verb as an instruction-at-the-author (governing a possessive object) DOES fire
    chk("x4_reduce_your_imperative_fires",
        any("X4 descriptive" in ln for ln in explain_profile(
            LOCAL + sl("SL-01", label="Reduce your reliance on the definite article.") + "\n" + sl("SL-02"))[1]))
    # comparison-to-emulate via 'model your prose on …'
    chk("x4_model_prose_on_fires",
        any("X4 descriptive" in ln for ln in explain_profile(
            LOCAL + sl("SL-01", label="Model your prose on a leaner register.") + "\n" + sl("SL-02"))[1]))
    # per-id override silences the label match; prose-override does NOT silence a label match
    ov_id = "<!-- override: style-frame SL-01 — quoting the author's own stated revision goal -->\n"
    chk("x4_id_override_silences_label", not any("X4" in ln for ln in explain_profile(ov_id + presc)[1]))
    # prose-level prescription: bare prose override silences it; a per-id override does NOT
    presc_prose = LOCAL + TWO + "\n## Notes\n\n- You should tighten your sentences next book.\n"
    chk("x4_prose_prescription_advisory", any("X4 descriptive" in ln for ln in explain_profile(presc_prose)[1]))
    ov_prose = "<!-- override: style-frame — quoting the author's own stated goal -->\n"
    chk("x4_prose_override_silences", not any("X4" in ln for ln in explain_profile(ov_prose + presc_prose)[1]))
    chk("x4_id_override_does_not_silence_prose",
        any("X4 descriptive" in ln for ln in explain_profile(ov_id + presc_prose)[1]))

    # the describes-baseline-position frame is a valid DESCRIPTIVE stance — must pass clean
    chk("x4_baseline_position_frame_clean",
        explain_profile(LOCAL + sl("SL-01", frame="describes-baseline-position",
                                    label="The voice sits 0.7 from the author centroid.")
                        + "\n" + sl("SL-02"))[0] == 0)
    # a label legitimately CONTAINING a style-object noun used descriptively must NOT fire X4
    chk("x4_descriptive_noun_clean",
        not any("X4" in ln for ln in explain_profile(
            LOCAL + sl("SL-01", label="The diction holds an even, formal register throughout.")
            + "\n" + sl("SL-02"))[1]))

    # X5 — same-register cluster (a describes-cluster referencing >= 2 labels must share register)
    cross = (sl("SL-01", register="literary-fiction") + "\n"
             + sl("SL-02", register="memoir", feature_ref="families.function_words.top_features[and]")
             + "\n" + sl("SL-03", frame="describes-cluster", register="literary-fiction",
                         feature_ref="families.function_words cluster",
                         label="SL-01 and SL-02 form a coordinating-function-word cluster."))
    code, lines = explain_profile(LOCAL + cross)
    chk("x5_cross_register_cluster", code == 1 and any("X5 same-register" in ln for ln in lines))
    same = (sl("SL-01", register="literary-fiction") + "\n"
            + sl("SL-02", register="literary-fiction", feature_ref="families.function_words.top_features[and]")
            + "\n" + sl("SL-03", frame="describes-cluster", register="literary-fiction",
                        feature_ref="families.function_words cluster",
                        label="SL-01 and SL-02 form a same-register coordinating cluster."))
    chk("x5_same_register_cluster_clean", not any("X5" in ln for ln in explain_profile(LOCAL + same)[1]))
    # a describes-cluster referencing an UNKNOWN id is an integrity error, not a silent skip
    typo = (sl("SL-01", register="literary-fiction") + "\n"
            + sl("SL-03", frame="describes-cluster", register="literary-fiction",
                 feature_ref="families.function_words cluster",
                 label="SL-01 and SL-99 form a cluster."))
    code, lines = explain_profile(LOCAL + typo)
    chk("x5_dangling_ref_errors", code == 1 and any("X5 same-register" in ln for ln in lines))
    # a describes-cluster referencing only ONE other label is not a cluster claim — X5 needs >= 2 refs
    one_ref = (sl("SL-01", register="literary-fiction") + "\n"
               + sl("SL-03", frame="describes-cluster", register="memoir",
                    feature_ref="cluster of SL-01", label="SL-01 alone — not a multi-label cluster."))
    chk("x5_single_ref_no_trigger", not any("X5" in ln for ln in explain_profile(LOCAL + one_ref)[1]))

    # X6 — local-only hygiene (advisory WARN only, NEVER escalated under --strict)
    code, lines = explain_profile(TWO)  # no local-only marker
    chk("x6_missing_marker_advisory", code == 0 and any("X6 local-only" in ln for ln in lines))
    chk("x6_never_strict_escalates", explain_profile(TWO, strict=True)[0] == 0)
    url = LOCAL + TWO + "\n\nSee https://example.com/profile for the hosted copy.\n"
    chk("x6_external_url", any("external http(s) URL" in ln for ln in explain_profile(url)[1]))
    # Codex #140 P2: a URL hidden INSIDE a structured label field evaded X6 — the style_label block is an
    # HTML comment, stripped from the reader-facing prose the scan used. The scan now covers label fields.
    in_label = LOCAL + sl("SL-01", label="The prose leans on the definite article — https://evil.example/x") \
        + "\n" + sl("SL-02")
    chk("x6_external_url_in_label", any("external http(s) URL" in ln for ln in explain_profile(in_label)[1]))
    # negative control: a clean profile (no URL anywhere) must NOT trip the X6 URL scan (no false positive)
    chk("x6_no_url_clean", not any("external http(s) URL" in ln for ln in explain_profile(LOCAL + TWO)[1]))

    # W1 — seed/coverage (single feature => thin; no blocks => no-op)
    code, lines = explain_profile(LOCAL + sl("SL-01"))
    chk("w1_single_feature_thin_advisory", code == 0 and any("W1 seed/coverage" in ln for ln in lines))
    chk("w1_single_feature_strict_fails", explain_profile(LOCAL + sl("SL-01"), strict=True)[0] == 1)
    chk("w1_two_features_clean", not any("W1" in ln for ln in explain_profile(LOCAL + TWO)[1]))
    chk("no_labels_noop", explain_profile("# Notes\nnothing structured\n")[0] == 0)

    # resolution: run-folder, explicit-file, missing-artifact usage exit 2, and the DECOY case
    import tempfile
    import shutil
    d = tempfile.mkdtemp()
    try:
        p = os.path.join(d, "Author_Style_Explanation.md")
        with open(p, "w", encoding="utf-8", newline="") as fh:
            fh.write("# Author Style Explanation\n" + LOCAL + TWO + "\n")
        chk("run_folder_resolution", run([d])[0] == 0)
        chk("explicit_file_resolution", run([p])[0] == 0)
        chk("missing_artifact_usage", run([os.path.join(d, "nope.md")])[0] == 2)
        # a decoy file that only NAMES apodictic:style_label in prose must not win resolution over the
        # real profile (classify on parsed blocks, not a raw substring — the M2 discipline)
        decoy = os.path.join(d, "spec_mention.md")
        with open(decoy, "w", encoding="utf-8", newline="") as fh:
            fh.write("# Notes\nThis spec describes the apodictic:style_label block format.\n")
        chk("resolver_skips_prose_mention", run([decoy, p])[0] == 0 and resolve([decoy, p]) == p)
        # in a run-folder with BOTH a voice profile (fingerprints only) and a style explanation, the
        # style-explanation resolver must pick the file that actually carries style_label blocks
        vp = os.path.join(d, "Author_Voice_Profile.md")
        with open(vp, "w", encoding="utf-8", newline="") as fh:
            fh.write("# Author Voice Profile\n<!-- author-voice-profile: local-only -->\n"
                     '<!-- apodictic:voice_fingerprint\n{"schema":"apodictic.voice_fingerprint.v1",'
                     '"id":"VF-01","work_label":"W (2026)","register":"literary-fiction",'
                     '"source":"ai-prose-baseline","metrics":{"mattr_z":"-0.4"}}\n-->\n')
        chk("resolver_prefers_style_label_file", resolve([d]) == p)
    finally:
        shutil.rmtree(d, ignore_errors=True)

    print("Self-test: PASS" if rc["v"] == 0 else "Self-test: FAIL")
    return rc["v"]


def main(argv):
    if "--self-test" in argv:
        return run_self_test()
    args = [a for a in argv[1:] if a != "style-explanation"]
    strict = "--strict" in args
    paths = [a for a in args if not a.startswith("--")]
    if not paths:
        print("Usage: style_explanation.py style-explanation <author_root|files...> [--strict] | --self-test")
        return 2
    code, lines = run(paths, strict=strict)
    for ln in lines:
        print(ln)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
