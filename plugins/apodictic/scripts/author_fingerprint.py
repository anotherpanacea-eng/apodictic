#!/usr/bin/env python3
"""author-fingerprint — structural integrity for the Cross-Manuscript Author Voice/Craft Fingerprint.

`validate.sh author-fingerprint <author_root|files>` shells out here. A writer's voice changes over a
career — by growth, by drift, or by an unconscious settling into the same cadence book after book.
APODICTIC measures voice WITHIN a manuscript but has no memory ACROSS works; this is that memory: a
persistent profile, collected under an operator-designated author-root, that surfaces movement. It
does NO new stylometry — it consumes the single-voice AI-prose machinery (voice_profile /
voice_distance + personal-baseline z-scores) and adds the persistence-and-diagnosis layer. Each work
is an apodictic.voice_fingerprint.v1 block; this validator owns the cross-work profile contract.

The module is descriptive (observations, not verdicts) and local-only (no external call). It compares
drift ONLY within a register (the AI-prose domain-shift guard) and never prescribes a voice change.

  F1 schema        a voice_fingerprint block fails its schema (bad source enum, malformed VF-… id,
                   missing work_label/register/source/metrics, broken JSON, duplicate id, or a
                   `metrics` that is empty or carries a non-scalar value).
  F2 provenance    a fingerprint with no `centroid_ref` naming a consumed audit output — the module
                   consumes; a fingerprint that names no source value cannot be traced (ERROR).
  F3 same-register a drift/range claim (a line referencing >= 2 fingerprint ids) whose fingerprints
                   do not all share a `register` — a cross-register comparison the domain-shift
                   caution forbids (ERROR). Bespoke prose-claim parse (the continuity-bible C3 shape).
  F4 descriptive   the reader-facing prose carries an editorial Must/Should/Could severity token or a
                   prescriptive voice-directive ("you should tighten your sentences", "fix your
                   voice") — a fingerprint reports movement, it never prescribes or grades. Advisory;
                   ERROR under --strict. Override: <!-- override: fingerprint-frame VF-… — <why> -->.
  W1 insufficient  no register has >= 2 fingerprints, so no drift/growth/self-imitation diagnosis is
     data         possible — the profile is seed-only (a first work legitimately just seeds).
                   Advisory; ERROR under --strict.
  W2 local-only    the profile lacks a `<!-- author-voice-profile: local-only -->` marker, or it
                   references an external http(s) URL. Advisory WARN ONLY (a self-attestation hygiene
                   check — it cannot detect a runtime call; the binding guarantee is the module's
                   no-external-call rule, not this scan), never escalated under --strict.

Reuses apodictic_artifacts (block grammar + schema engine). The profile is a single artifact (no
paired ledger); an empty/absent one is a no-op. See docs/author-voice-fingerprint.md.

  author_fingerprint.py author-fingerprint <author_root|files...> [--strict]
  author_fingerprint.py --self-test

Exit: 0 clean / WARN-only, 1 ERROR (or WARN under --strict, EXCEPT W2 which stays WARN), 2 usage.
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

_SCHEMA_ID = "apodictic.voice_fingerprint.v1"
_PROFILE_GLOB = "Author_Voice_Profile*.md"

_VF_REF_RE = re.compile(r"\bVF-[A-Za-z0-9-]+\b")
_HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
_LOCAL_ONLY_RE = re.compile(r"<!--\s*author-voice-profile:\s*local-only\s*-->", re.IGNORECASE)
_EXTERNAL_URL_RE = re.compile(r"https?://", re.IGNORECASE)
_SEVERITY_RE = re.compile(r"\b(?:Must|Should|Could)-Fix\b")
# F4 — a prescriptive directive aimed at the author's voice (the module describes, never prescribes).
_PRESCRIPTIVE_RE = re.compile(
    r"\byou\s+(?:should|must|need\s+to|ought\s+to|have\s+to|'?d\s+better)\b"
    r"|\bfix\s+your\s+(?:voice|cadence|prose|style|sentences)\b"
    r"|\b(?:vary|tighten|loosen|expand|broaden|change|diversify|fix)\s+your\s+(?:voice|cadence|prose|style|sentences|range)\b",
    re.IGNORECASE)
# Fingerprint-frame overrides (`<!-- override: fingerprint-frame VF-… -->`) route through the shared
# `override_marker` SSoT — code spans stripped, slug boundary-matched.


def _read(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return None


def _overrides(text, slug):
    """The set of VF-… ids overridden for `slug` (`fingerprint-frame`) — via the shared SSoT, so a
    marker quoted inside a code span is not honored as a live directive."""
    return {t[0] for t in override_targets(text, slug, r"(VF-[A-Za-z0-9-]+)")}


def parse_fingerprints(text):
    """[(obj_or_None, schema_errs, index), ...] for each apodictic:voice_fingerprint block."""
    out = []
    if not text or art is None:
        return out
    schema = art.load_schema(_SCHEMA_ID)
    idx = 0
    for btype, obj, jerr in art.parse_blocks(text):
        if btype != "voice_fingerprint":
            continue
        idx += 1
        where = "voice_fingerprint #%d" % idx
        if jerr:
            out.append((None, ["%s: invalid JSON — %s" % (where, jerr)], idx))
            continue
        errs = art.validate_obj(obj, schema, where)
        # metrics: non-empty map of scalar values (the subset engine only types the container). The
        # contract (schema $comment + F1) is scalar == str/number/bool; check it as an ALLOWLIST, not
        # a "not dict/list" blocklist — a blocklist passed JSON `null`, which is not a scalar and would
        # read as a valid-but-uninformative metric (and crash any consumer that does arithmetic on it).
        metrics = obj.get("metrics") if isinstance(obj, dict) else None
        if isinstance(metrics, dict):
            if not metrics:
                errs.append("%s: 'metrics' is empty (need >= 1 consumed metric)" % where)
            for k, v in metrics.items():
                if not isinstance(v, (str, int, float)):  # bool is an int subclass; null/dict/list out
                    errs.append("%s: metrics.%s must be a scalar value (str/number/bool), not %s"
                                % (where, k, type(v).__name__))
        out.append((obj, errs, idx))
    return out


def _claim_lines(text):
    """Visible-prose lines that reference >= 2 distinct fingerprint ids (a comparison claim)."""
    out = []
    visible = _HTML_COMMENT_RE.sub("", text or "")  # drop the fingerprint blocks (HTML comments)
    for raw in visible.splitlines():
        refs = []
        for r in _VF_REF_RE.findall(raw):
            if r not in refs:
                refs.append(r)
        if len(refs) >= 2:
            out.append(refs)
    return out


def fingerprint_profile(text, strict=False):
    """Run the Author Voice Profile integrity checks. Returns (code, lines)."""
    lines, errs, warns, w2 = [], [], [], []
    fps = parse_fingerprints(text)
    if not fps:
        return 0, ["author-fingerprint: no voice_fingerprint blocks found — nothing to check"]

    # F1 — schema / JSON / metrics validity
    for _obj, schema_errs, _idx in fps:
        for e in schema_errs:
            errs.append("F1 schema: %s" % e)

    valid = [(obj, idx) for obj, schema_errs, idx in fps if obj is not None and not schema_errs]
    # F1 — register (and work_label) must be non-blank. The schema's plain `type: string` accepts "",
    # and two blank-register fingerprints would collide as one register — suppressing W1 and passing
    # F3 with no comparability class actually supplied (Codex P1). A blank-field fingerprint is treated
    # as invalid so the same-register / coverage checks never run on it.
    nonblank = []
    for obj, idx in valid:
        blanks = [f for f in ("register", "work_label") if not (obj.get(f) or "").strip()]
        if blanks:
            errs.append("F1 schema: %s has a blank %s — required and non-empty (register names the "
                        "comparability class; an empty value silently collides with other blanks)"
                        % (obj.get("id"), "/".join(blanks)))
        else:
            nonblank.append((obj, idx))
    valid = nonblank
    by_id, seen = {}, {}
    for obj, idx in valid:
        seen.setdefault(obj.get("id"), []).append(idx)
        by_id.setdefault(obj.get("id"), obj)
    for vid, where in sorted(seen.items()):
        if len(where) > 1:
            errs.append("F1 schema: %s appears %d times (ids must be unique)" % (vid, len(where)))

    # F2 — provenance: every fingerprint names a consumed audit output via centroid_ref
    for obj, _idx in valid:
        if not (obj.get("centroid_ref") or "").strip():
            errs.append("F2 provenance: %s has no centroid_ref naming a consumed audit output — the "
                        "module consumes existing stylometry; an un-sourced fingerprint can't be traced"
                        % obj.get("id"))

    # F3 — same-register comparison (a claim referencing >= 2 fingerprints must share a register)
    for refs in _claim_lines(text):
        # A referenced-but-unknown VF-id is an integrity error, not a silent skip: discarding it let
        # a typo ("VF-lit differs from VF-typo") hide the intended cross-register comparison and still
        # PASS (Codex P1). Mirror continuity-bible C3's unknown-id guard; only run the same-register
        # check once every ref resolves.
        unknown = [r for r in refs if r not in by_id]
        if unknown:
            errs.append("F3 reference: a drift/range claim references unknown fingerprint id(s) %s — "
                        "every VF-… in a claim must resolve (a typo can otherwise hide the comparison)"
                        % ", ".join(sorted(unknown)))
            continue
        registers = {(by_id[r].get("register") or "").strip().lower() for r in refs}
        if len(registers) > 1:
            errs.append("F3 same-register: a drift/range claim compares fingerprints across registers "
                        "(%s) — drift is only meaningful within a register (the AI-prose domain-shift "
                        "guard)" % ", ".join(sorted(r for r in registers if r)))

    # F4 — descriptive, not prescriptive / defect (advisory; ERROR --strict; override silences)
    visible = _HTML_COMMENT_RE.sub("", text or "")
    if not _overrides(text, "fingerprint-frame"):
        if _SEVERITY_RE.search(visible):
            warns.append("F4 descriptive: the profile carries an editorial Must/Should/Could-Fix "
                         "severity token — a fingerprint is not a defect and takes no editorial severity")
        if _PRESCRIPTIVE_RE.search(visible):
            warns.append("F4 descriptive: the profile prescribes a voice change ('fix/vary your "
                         "voice', 'you should …') — the module reports movement, it never prescribes")

    # W1 — insufficient data (no register has >= 2 fingerprints → seed-only)
    reg_counts = {}
    for obj, _idx in valid:
        reg_counts[(obj.get("register") or "").strip().lower()] = \
            reg_counts.get((obj.get("register") or "").strip().lower(), 0) + 1
    if valid and max(reg_counts.values()) < 2:
        warns.append("W1 insufficient data: no register has >= 2 fingerprints — the profile is "
                     "seed-only; drift / growth / self-imitation diagnosis is suppressed")

    # W2 — local-only hygiene (advisory WARN ONLY, never escalated under --strict)
    if not _LOCAL_ONLY_RE.search(text or ""):
        w2.append("W2 local-only: the profile lacks a `<!-- author-voice-profile: local-only -->` "
                  "marker — a career voice profile must never be transmitted (hygiene attestation)")
    if _EXTERNAL_URL_RE.search(visible):
        w2.append("W2 local-only: the profile references an external http(s) URL — the profile is "
                  "local-only and makes no external call")

    # Report
    lines.append("author-fingerprint: %d fingerprint(s)%s" % (
        len(fps), "" if len(valid) == len(fps) else " (%d well-formed)" % len(valid)))
    for obj, _idx in valid:
        lines.append("  %-18s register=%-18s source=%s" % (obj.get("id"), obj.get("register"),
                                                           obj.get("source")))
    for e in errs:
        lines.append("  ERROR: %s" % e)
    for w in warns:
        lines.append("  %s: %s" % ("ERROR (--strict)" if strict else "WARN", w))
    for w in w2:
        lines.append("  WARN: %s" % w)  # W2 stays WARN even under --strict

    if errs or (strict and warns):
        lines.append("author-fingerprint: FAIL (%d error(s)%s)"
                     % (len(errs), ", %d strict warn(s)" % len(warns) if (strict and warns) else ""))
        return 1, lines
    if warns or w2:
        lines.append("WARN: author-fingerprint: %d advisory gap(s) — see F4/W1/W2 above"
                     % (len(warns) + len(w2)))
    else:
        lines.append("author-fingerprint: PASS (schema + provenance + same-register + "
                     "descriptive-not-prescriptive)")
    return 0, lines


# ---------------------------------------------------------------- resolution

def _newest(paths):
    return max(paths, key=os.path.getmtime) if paths else None


def _has_block(text, btype):
    """True if `text` carries a real apodictic:<btype> block (a parsed carrier, not a prose mention).

    Classifying on parsed blocks — not a raw substring — keeps a docs/spec file that merely *names*
    `apodictic:voice_fingerprint` in prose from winning resolution over the real profile."""
    if art is None:
        return ("apodictic:%s" % btype) in (text or "")  # degraded: no engine to parse with
    return any(bt == btype for bt, _o, _e in art.parse_blocks(text or ""))


def resolve(paths):
    if len(paths) == 1 and os.path.isdir(paths[0]):
        return _newest(glob.glob(os.path.join(paths[0], _PROFILE_GLOB)))
    for p in paths:
        if _has_block(_read(p) or "", "voice_fingerprint"):
            return p
    return paths[0] if paths else None


def run(paths, strict=False):
    path = resolve(paths)
    if not path:
        return 2, ["author-fingerprint: no Author Voice Profile found (need an Author_Voice_Profile*.md "
                   "or a file with apodictic:voice_fingerprint blocks)"]
    text = _read(path)
    if text is None:
        return 2, ["author-fingerprint: cannot read %s" % path]
    return fingerprint_profile(text, strict=strict)


# ---------------------------------------------------------------- self-test

def run_self_test():
    import json as _j
    rc = {"v": 0}

    def chk(name, cond):
        print("  %s: %s" % (name, "OK" if cond else "FAIL"))
        if not cond:
            rc["v"] = 1

    LOCAL = "<!-- author-voice-profile: local-only -->\n\n"

    def fp(vid, register="literary-fiction", source="ai-prose-baseline",
           centroid_ref="results.baseline_comparison", work_label="Thornfield (2026)",
           metrics=None):
        obj = {"schema": _SCHEMA_ID, "id": vid, "work_label": work_label, "register": register,
               "source": source, "centroid_ref": centroid_ref,
               "metrics": metrics if metrics is not None else {"mattr_z": "-0.4", "burrows_to_author_centroid": "0.7"}}
        return "<!-- apodictic:voice_fingerprint\n%s\n-->" % _j.dumps(obj)

    TWO = (fp("VF-2024-marsh", work_label="Marsh Light (2024)", metrics={"burrows_to_author_centroid": "0.2"})
           + "\n" + fp("VF-2026-thornfield", metrics={"burrows_to_author_centroid": "0.7"}))

    # clean: two same-register fingerprints + local-only marker, no prescriptive prose
    chk("clean_two_same_register", fingerprint_profile(LOCAL + TWO)[0] == 0)

    # F1 — schema
    chk("f1_bad_source", fingerprint_profile(LOCAL + fp("VF-01", source="pov-centroid"))[0] == 1)
    chk("f1_bad_id", fingerprint_profile(LOCAL + fp("VF 01"))[0] == 1)
    chk("f1_missing_field", fingerprint_profile(LOCAL + fp("VF-01").replace('"register"', '"reg"'))[0] == 1)
    chk("f1_metrics_empty", fingerprint_profile(LOCAL + fp("VF-01", metrics={}))[0] == 1)
    chk("f1_metrics_nonscalar", fingerprint_profile(LOCAL + fp("VF-01", metrics={"x": {"nested": 1}}))[0] == 1)
    chk("f1_metrics_nonscalar_list", fingerprint_profile(LOCAL + fp("VF-01", metrics={"x": [1, 2]}))[0] == 1)
    # a JSON `null` metric value is NOT a scalar (str/number/bool) — the contract is an allowlist, so
    # null must be rejected like dict/list (a blocklist "not dict/list" wrongly passed it — P2).
    chk("f1_metrics_null_rejected",
        fingerprint_profile(LOCAL + fp("VF-01", metrics={"x": None}))[0] == 1)
    # a numeric or bool scalar metric is valid (the allowlist must not over-reject legitimate scalars)
    chk("f1_metrics_numeric_scalar_clean",
        fingerprint_profile(LOCAL + fp("VF-01", metrics={"mattr_z": -0.4, "tic": True}) + "\n" + fp("VF-02"))[0] == 0)
    code, lines = fingerprint_profile(LOCAL + '<!-- apodictic:voice_fingerprint\n{"schema":"apodictic.voice_fingerprint.v1"\n-->')
    chk("f1_bad_json", code == 1 and any("F1 schema" in ln for ln in lines))
    code, lines = fingerprint_profile(LOCAL + fp("VF-01") + "\n" + fp("VF-01", register="memoir"))
    chk("f1_duplicate_id", code == 1 and any("appears 2 times" in ln for ln in lines))
    # two blank-register fingerprints must be REJECTED — empty registers would collide as one and
    # suppress W1 / pass F3 with no comparability class supplied (Codex P1)
    code, lines = fingerprint_profile(LOCAL + fp("VF-e1", register="")
                                      + "\n" + fp("VF-e2", register=""))
    chk("f1_blank_register_rejected", code == 1 and any("blank register" in ln for ln in lines))

    # F2 — provenance (centroid_ref present)
    code, lines = fingerprint_profile(LOCAL + fp("VF-01", centroid_ref="") + "\n" + fp("VF-02"))
    chk("f2_missing_centroid_ref", code == 1 and any("F2 provenance" in ln for ln in lines))

    # F3 — same-register (a claim referencing cross-register fingerprints)
    MIXED = (fp("VF-lit", register="literary-fiction") + "\n"
             + fp("VF-mem", register="memoir", work_label="A Quiet Year (2025)"))
    drift_cross = "\n## Drift\n\n- VF-lit has moved 0.8 from VF-mem across the two works.\n"
    code, lines = fingerprint_profile(LOCAL + MIXED + drift_cross)
    chk("f3_cross_register_claim", code == 1 and any("F3 same-register" in ln for ln in lines))
    # a same-register claim is clean
    drift_same = "\n## Drift\n\n- VF-2026-thornfield sits 0.5 further from the centroid than VF-2024-marsh.\n"
    chk("f3_same_register_claim_clean",
        not any("F3" in ln for ln in fingerprint_profile(LOCAL + TWO + drift_same)[1]))
    # a comparison naming an UNKNOWN id is an integrity error, not a silent skip: a typo must not hide
    # the intended cross-register comparison (Codex P1)
    typo = "\n## Drift\n\n- VF-lit differs from VF-typo across the two works.\n"
    code, lines = fingerprint_profile(LOCAL + MIXED + typo)
    chk("f3_dangling_ref_errors", code == 1 and any("F3 reference" in ln for ln in lines))

    # F4 — descriptive, not prescriptive (advisory; ERROR --strict; override silences)
    sev = LOCAL + TWO + "\n## Notes\n\n- This narrowing is a Must-Fix for the next book.\n"
    code, lines = fingerprint_profile(sev)
    chk("f4_severity_token_advisory", code == 0 and any("F4 descriptive" in ln for ln in lines))
    chk("f4_severity_token_strict_fails", fingerprint_profile(sev, strict=True)[0] == 1)
    presc = LOCAL + TWO + "\n## Notes\n\n- You should vary your cadence in the next book.\n"
    chk("f4_prescriptive_advisory", any("F4 descriptive" in ln for ln in fingerprint_profile(presc)[1]))
    ov = "<!-- override: fingerprint-frame VF-2026-thornfield — quoting the author's own goal -->\n"
    chk("f4_override_silences", not any("F4" in ln for ln in fingerprint_profile(ov + sev)[1]))
    # code-span decoy (bypass closed by the SSoT migration): an override quoted inside a code span is a
    # documentation example, not a live directive — F4 must still fire, in EITHER CommonMark form.
    chk("f4_inline_codespan_override_does_not_silence",
        any("F4" in ln for ln in fingerprint_profile("`" + ov.strip() + "`\n" + sev)[1]))
    chk("f4_fenced_codespan_override_does_not_silence",
        any("F4" in ln for ln in fingerprint_profile("```\n" + ov.strip() + "\n```\n" + sev)[1]))
    # a plain descriptive observation does not trip F4
    chk("f4_descriptive_clean",
        not any("F4" in ln for ln in fingerprint_profile(
            LOCAL + TWO + "\n## Drift\n\n- The voice has tightened across the two works — intended, or drift?\n")[1]))

    # W1 — insufficient data (one fingerprint, or two in different registers => no >=2 same-register)
    code, lines = fingerprint_profile(LOCAL + fp("VF-01"))
    chk("w1_single_seed_advisory", code == 0 and any("W1 insufficient data" in ln for ln in lines))
    chk("w1_two_different_registers_seed",
        any("W1 insufficient data" in ln for ln in fingerprint_profile(LOCAL + MIXED)[1]))
    chk("w1_strict_fails", fingerprint_profile(LOCAL + fp("VF-01"), strict=True)[0] == 1)
    chk("w1_two_same_register_clean", not any("W1" in ln for ln in fingerprint_profile(LOCAL + TWO)[1]))

    # W2 — local-only hygiene (advisory WARN only, NEVER escalated under --strict)
    code, lines = fingerprint_profile(TWO)  # no local-only marker
    chk("w2_missing_marker_advisory", code == 0 and any("W2 local-only" in ln for ln in lines))
    chk("w2_never_strict_escalates", fingerprint_profile(TWO, strict=True)[0] == 0)
    url = LOCAL + TWO + "\n\nSee https://example.com/profile for the hosted copy.\n"
    chk("w2_external_url", any("external http(s) URL" in ln for ln in fingerprint_profile(url)[1]))

    # no blocks -> no-op
    chk("no_fingerprints_noop", fingerprint_profile("# Notes\nnothing structured\n")[0] == 0)

    # run-folder + explicit-file resolution
    import tempfile
    import shutil
    d = tempfile.mkdtemp()
    try:
        p = os.path.join(d, "Author_Voice_Profile.md")
        with open(p, "w", encoding="utf-8", newline="") as fh:
            fh.write("# Author Voice Profile\n" + LOCAL + TWO + "\n")
        chk("run_folder_resolution", run([d])[0] == 0)
        chk("explicit_file_resolution", run([p])[0] == 0)
        chk("missing_artifact_usage", run([os.path.join(d, "nope.md")])[0] == 2)
        # a decoy file that only NAMES apodictic:voice_fingerprint in prose must not win resolution
        # over the real profile (classify on parsed blocks, not raw substring)
        decoy = os.path.join(d, "spec_mention.md")
        with open(decoy, "w", encoding="utf-8", newline="") as fh:
            fh.write("# Notes\nThis spec describes the apodictic:voice_fingerprint block format.\n")
        chk("resolver_skips_prose_mention", run([decoy, p])[0] == 0
            and resolve([decoy, p]) == p)
    finally:
        shutil.rmtree(d, ignore_errors=True)

    print("Self-test: PASS" if rc["v"] == 0 else "Self-test: FAIL")
    return rc["v"]


def main(argv):
    if "--self-test" in argv:
        return run_self_test()
    args = [a for a in argv[1:] if a != "author-fingerprint"]
    strict = "--strict" in args
    paths = [a for a in args if not a.startswith("--")]
    if not paths:
        print("Usage: author_fingerprint.py author-fingerprint <author_root|files...> [--strict] | --self-test")
        return 2
    code, lines = run(paths, strict=strict)
    for ln in lines:
        print(ln)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
