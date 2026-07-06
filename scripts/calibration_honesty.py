#!/usr/bin/env python3
"""calibration-honesty — an uncalibrated SETEC band must never be rendered to a reader as a verdict.

`validate.sh calibration-honesty <run_folder|files...> [--strict]` shells out here. Both consumer
decision-audit surfaces — `narrative_decision_audit` (StoryScope) and `argument_decision_audit`
(ArgScope) — ship `handoff: experimental` with an envelope `aggregate.verdict_band: "uncalibrated"` and
`thresholds: {low: null, high: null}`. The consumer-side discipline (surface the band as PROVENANCE
only, never as a calibrated verdict) was enforced ENTIRELY in prose (the two audit docs' anti-verdict
sections + four pass-dependencies.md rows). No mechanical check existed that a decision-audit's
human-facing rendering doesn't present the uncalibrated band as calibrated. This is that check: the
house `claim-surface-asserts-it -> enforce-it` posture applied to a claim the audits already make.

WHAT IT CHECKS (D1). The guard scans the reader-facing editorial letter WHOLE (D2 — region-scoping was a
false foundation: the only per-audit sectioner scopes appendix bodies only, decision-audit findings land
in the unscoped synthesis body, and the canonical fixture carries no decision-audit region), per
PARAGRAPH (blank-line-delimited scan unit). A paragraph is flagged only when a CLAIM SHAPE matches AND no
QUALIFIER is co-present in that same paragraph. Bare token presence ("band", "threshold", "verdict")
never fires on its own — that is what keeps the mandated clean-path boilerplate and the vendored bundle
labels safe (they carry a qualifier or lack a claim shape).

  CS1 band-placement    "the manuscript scores in the AI-elevated band" — a subject + a placement verb +
                        `in/into/within/at` + `band`. The verdict form, no qualifier.
  CS2 calibrated-verdict "calibrated verdict/band/score", or a bare `verdict:` / `verdict =` assertion.
  CS3 threshold claim   "sits above the threshold" / "threshold of 0.4" — on a thresholds-null surface,
                        a comparative + `the/a/its threshold|cut-off`, or a numeric threshold.
  CS4 aggregate-verdict "the aggregate score confirms/proves/establishes/demonstrates …" — the score
                        promoted to a verdict.

SEVERITY (D4 — the honest class). This is an OPEN natural-language co-presence check, not a closed
literal scan, so its house class is content_advisory W1 (prescriptive drift) / stance-consistency F4:
WARN by default, ERROR only under --strict. Failure direction is toward NOT firing (a missed leak is
recoverable by the human reader who owns the reading; a false ERROR blocks a run on prose the doc itself
mandates). The HONEST CLAIM (stated here and in the validator's help): the guard closes the ENUMERATED
claim shapes when unqualified; it does NOT claim to close every way prose can imply calibration. Residual
semantic leakage that no vocabulary list can close is presented to a human. Layered mechanism + human
terminus, not a proof.

  Override: a per-instance prose override `<!-- override: calibration-honesty — <why> -->`, detected via
  the shared `override_marker` SSoT (code-span-stripped, boundary-matched — M5), never a bare substring.

OWNERSHIP (D5 — one new arm; the three-way boundary, disclaimed not latent).
  * `severity-floor` (letter_checks) owns whole-letter verdict-band-vs-flags honesty for the
    SUBMISSION-READINESS vocabulary (`_HIGH_VERDICT_RE` = Strong Fit | publishable as-is | Highest Band
    | Excellent Fit), policed against flag volume. NAMED OVERLAP + DISCLAIMER: both validators scan
    letter-wide verdict-adjacent vocabulary; the two vocabularies are and must remain DISJOINT — no CS
    pattern matches the four readiness tokens (the readiness-disjointness self-test asserts a legal
    readiness sentence does not fire calibration-honesty), and calibration-honesty never reads flag
    counts.
  * `honesty_check` (softness-check / deficit-lock) owns locked-severity delivery. It says nothing about
    calibration bands.
  * `calibration-honesty` (this arm) owns per-audit calibration-PROVENANCE rendering — an uncalibrated
    SETEC band presented as calibrated. It never reads severities, never gates tiers, never touches the
    §4e propagation logic.

CROSS-SURFACE (D6). The guard covers BOTH decision-audits and is surface-agnostic: nothing keys on the
audit name, so a future uncalibrated `handoff: experimental` consumer surface inherits it by
construction.

VOCABULARY HOME. The severity-token SSoT (`severity_vocab.SEVERITY_TOKEN_RE`, M8) is the Must/Should/
Could-Fix leak token — a DIFFERENT vocabulary that this guard does not use (it reads calibration-band
prose, not editorial-severity prose). The CS shapes, qualifier set, and allowlist are THIS guard's OWN
new vocabulary and live here; M8 does not apply (no `(?:Must|Should|Could)` alternation is re-compiled).
See docs/calibration-honesty.md.

  calibration_honesty.py calibration-honesty <run_folder|files...> [--strict]
  calibration_honesty.py --self-test

Exit: 0 clean / WARN-only, 1 ERROR (WARN under --strict), 2 usage / no artifact.
"""
import glob
import os
import re
import sys

from override_marker import has_override, strip_code_spans  # SSoT: code-span-stripped, boundary-matched

_OVERRIDE_SLUG = "calibration-honesty"

# The editorial letter — scanned whole (D2). Newest wins on a run-folder resolution.
_LETTER_GLOBS = ("*_Core_DE_Synthesis_*.md", "*_Full_DE_Synthesis_*.md")

# ------------------------------------------------------------------ CS family (D1)
# CS1 — band-placement claim: a subject, a placement verb, in/into/within/at, then `band` within a short
# same-line window. The `\bband\b` requirement is what keeps "scores high on structural_streamlining"
# (the :157 "fair" summary — no `band` token) and the bundle labels safe.
_CS1 = re.compile(
    r"(?:manuscript|document|essay|story|draft|work|text|chapter|prose|argument|op-ed|it|this)\b"
    r"[^.!?\n]{0,60}?"
    r"\b(?:scores?|falls?|lands?|sits?|places?|rates?|comes?\s+out|is)\s+"
    r"(?:in|into|within|at)\s+(?:the\s+|a\s+|an\s+)?"
    r"[^.!?\n]{0,40}?\bband\b",
    re.IGNORECASE)
# CS2 — calibrated / verdict assertion (two patterns).
_CS2 = (
    re.compile(r"\bcalibrated\s+(?:verdict|band|score|result|threshold)s?\b", re.IGNORECASE),
    re.compile(r"\bverdict\s*[:=]"),  # `verdict:` / `verdict =` — a rendered verdict field
)
# CS3 — threshold claim on a thresholds-null surface (two patterns).
_CS3 = (
    re.compile(r"\b(?:above|below|exceeds?|crosses?|meets?|over|under|past)\s+"
               r"(?:the|a|its)\s+(?:threshold|cut-?off)\b", re.IGNORECASE),
    re.compile(r"\bthreshold\s+(?:of|at)\s+[-+]?\d"),
)
# CS4 — aggregate-as-verdict.
_CS4 = re.compile(
    r"\baggregate(?:\s+|[-_])?score\b[^.!?\n]{0,80}"
    r"\b(?:verdict|confirms?|proves?|establishes?|demonstrates?)\b",
    re.IGNORECASE)

# D5 disjointness: the SUBMISSION-READINESS vocabulary is severity-floor's (`_HIGH_VERDICT_RE`), and the
# two vocabularies must remain DISJOINT. One readiness token — "Highest Band" — carries the `band` noun
# CS1 keys on, so a CS1 match whose ONLY band anchor is a readiness phrase is severity-floor's turf, not
# ours; excise those matches. (The other three readiness tokens carry no `band`/threshold/verdict shape,
# so no other CS rule can reach them.) Kept in lockstep with letter_checks._HIGH_VERDICT_RE by the
# readiness-disjointness self-test.
_READINESS_BAND_RE = re.compile(r"\b(?:Highest|Strong|Top|Excellent|Publishable)\s+Band\b", re.IGNORECASE)


def _cs1_hits(text):
    """CS1 matches on `text`, minus any whose `band` anchor is a submission-readiness phrase
    ("Highest Band") — that is severity-floor's vocabulary (D5). A CS1 hit counts only if a NON-readiness
    `band` occurrence backs it: strip the readiness-band phrases and re-test."""
    if not _CS1.search(text):
        return False
    stripped = _READINESS_BAND_RE.sub("", text)
    return bool(_CS1.search(stripped))


# (label, matcher) — a matcher is a compiled RE, a tuple of them (any match fires), or a callable.
_CS_RULES = (
    ("CS1 band-placement", _cs1_hits),
    ("CS2 calibrated-verdict", _CS2),
    ("CS3 threshold-claim", _CS3),
    ("CS4 aggregate-as-verdict", _CS4),
)

# ------------------------------------------------------------------ qualifier set (D1)
# Case-folded substring: co-presence in the SAME paragraph quenches the flag. Enumerated in full.
_QUALIFIERS = (
    "uncalibrated", "provenance only", "provenance-only", "not a verdict", "never a verdict",
    "no thresholds", "ships uncalibrated", "advisory", "does not license", "does_not_license",
    "experimental", "directional reference",
)


def _matches(matcher, text):
    if isinstance(matcher, tuple):
        return any(pat.search(text) for pat in matcher)
    if callable(matcher) and not hasattr(matcher, "search"):
        return bool(matcher(text))  # a predicate (e.g. _cs1_hits)
    return bool(matcher.search(text))


def _qualified(para_lower):
    """True if any qualifier substring is co-present in the (already lower-cased) paragraph."""
    return any(q in para_lower for q in _QUALIFIERS)


def _read(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except (OSError, UnicodeDecodeError):
        return None


def _paragraphs(text):
    """Blank-line-delimited scan units. HTML comments (override markers, apodictic blocks) are stripped
    from the SCANNED copy so an override marker's own text can't trip a CS pattern, but the raw paragraph
    is retained for the override lookup (which needs the marker) and for the report quote."""
    # Split on one-or-more blank lines (whitespace-only lines count as blank).
    return [p for p in re.split(r"\n[ \t]*\n", text or "") if p.strip()]


_HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)


def scan(text, strict=False):
    """Run the calibration-honesty scan over an editorial letter. Returns (code, lines).

    Whole-letter, per paragraph. A paragraph fires at most ONE WARN (the first CS rule to match on the
    unqualified, override-free paragraph); the WARN names the rule and quotes the offending paragraph."""
    lines, warns = [], []
    paras = _paragraphs(text)

    for para in paras:
        # Reader-facing prose only: strip HTML comments AND code spans before pattern-matching, so an
        # override marker or a fenced code example never trips a CS shape (the boilerplate/label safety
        # relies on the qualifier co-presence, but a marker quoting a CS phrase must not self-fire).
        scan_text = strip_code_spans(_HTML_COMMENT_RE.sub("", para))
        para_lower = scan_text.lower()
        if _qualified(para_lower):
            continue  # a co-present qualifier quenches every CS rule in this paragraph
        for label, matcher in _CS_RULES:
            if not _matches(matcher, scan_text):
                continue
            # A per-instance prose override silences THIS paragraph (M5: code-span-stripped, boundary-
            # matched via the shared SSoT — a suffixed slug / a backtick'd marker is not honored).
            if has_override(para, _OVERRIDE_SLUG):
                break
            # Quote the reader-facing prose (HTML comments stripped) so the report isn't polluted by
            # markers/meta-comments; the match was on scan_text anyway.
            quote = " ".join(_HTML_COMMENT_RE.sub("", para).split())
            if len(quote) > 160:
                quote = quote[:157] + "..."
            warns.append("%s: an uncalibrated SETEC band is rendered as a verdict, with no "
                         "uncalibrated/provenance-only/advisory qualifier in the paragraph — \"%s\""
                         % (label, quote))
            break  # one WARN per paragraph

    lines.append("calibration-honesty: %d paragraph(s) scanned" % len(paras))
    for w in warns:
        lines.append("  %s: %s" % ("ERROR (--strict)" if strict else "WARN", w))

    if strict and warns:
        lines.append("calibration-honesty: FAIL (%d strict warn(s))" % len(warns))
        return 1, lines
    if warns:
        lines.append("WARN: calibration-honesty: %d unqualified calibration-band claim(s) — the guard "
                     "closes the enumerated claim shapes; a human reader owns residual leakage" % len(warns))
    else:
        lines.append("calibration-honesty: PASS (no unqualified calibration-band verdict claim)")
    return 0, lines


# ------------------------------------------------------------------ resolution

def _newest(paths):
    return max(paths, key=os.path.getmtime) if paths else None


def resolve(paths):
    """A single directory resolves to the newest editorial-letter glob; explicit files are checked in
    order (first that reads). No block-membership probe — the letter is unstructured synthesis prose."""
    if len(paths) == 1 and os.path.isdir(paths[0]):
        cands = []
        for g in _LETTER_GLOBS:
            cands.extend(glob.glob(os.path.join(paths[0], g)))
        return _newest(cands)
    for p in paths:
        if os.path.isfile(p) and _read(p) is not None:
            return p
    return None


def run(paths, strict=False):
    path = resolve(paths)
    if not path:
        return 2, ["calibration-honesty: no editorial letter found (need a *_Core_DE_Synthesis_*.md / "
                   "*_Full_DE_Synthesis_*.md or an explicit letter file) — nothing to check"]
    text = _read(path)
    if text is None:
        return 2, ["calibration-honesty: cannot read %s" % path]
    return scan(text, strict=strict)


# ------------------------------------------------------------------ self-test

def run_self_test():
    rc = {"v": 0}

    def chk(name, cond):
        print("  %s: %s" % (name, "OK" if cond else "FAIL"))
        if not cond:
            rc["v"] = 1

    def warns_of(text, strict=False):
        # Only the per-paragraph finding lines (two-space indent + WARN:/ERROR (--strict):), NOT the
        # trailing WARN summary line (which also carries "WARN").
        return [ln for ln in scan(text, strict=strict)[1]
                if ln.startswith("  WARN:") or ln.startswith("  ERROR (--strict):")]

    # non-UTF8 read degrades to None, never a traceback (the adjacent-exception class, swept repo-wide).
    import tempfile as _tf
    _fd, _nu = _tf.mkstemp(suffix=".md")
    with os.fdopen(_fd, "wb") as _fh:
        _fh.write(b"\xff\xfenot utf-8\xff")
    chk("non_utf8_read_returns_none", _read(_nu) is None)
    os.unlink(_nu)

    # Fixture 1 — clean provenance-only rendering (PASS): band stated WITH a qualifier co-present.
    chk("fx1_clean_provenance_pass",
        scan("aggregate score -0.84; verdict band uncalibrated, provenance only")[0] == 0
        and warns_of("aggregate score -0.84; verdict band uncalibrated, provenance only") == [])

    # Fixture 2 — CS1 band-placement (WARN default; ERROR --strict): no qualifier in the paragraph.
    F2 = "the manuscript scores in the AI-elevated band"
    chk("fx2_cs1_warn_default", scan(F2)[0] == 0 and any("CS1" in w for w in warns_of(F2)))
    chk("fx2_cs1_strict_fails", scan(F2, strict=True)[0] == 1)

    # Fixture 3 — CS3 threshold claim on a thresholds-null surface.
    F3 = "the story sits above the threshold"
    chk("fx3_cs3_warn_default", scan(F3)[0] == 0 and any("CS3" in w for w in warns_of(F3)))
    chk("fx3_cs3_strict_fails", scan(F3, strict=True)[0] == 1)
    chk("fx3b_cs3_numeric", any("CS3" in w for w in warns_of("crossed a threshold of 0.42 in the run")))

    # Fixture 4 — CS4 aggregate-as-verdict.
    F4 = "the aggregate score confirms the draft is AI-patterned"
    chk("fx4_cs4_warn_default", scan(F4)[0] == 0 and any("CS4" in w for w in warns_of(F4)))
    chk("fx4_cs4_strict_fails", scan(F4, strict=True)[0] == 1)

    # CS2 — calibrated/verdict assertion (both patterns).
    chk("cs2_calibrated_band", any("CS2" in w for w in warns_of("this is a calibrated band for the work")))
    chk("cs2_verdict_field", any("CS2" in w for w in warns_of("verdict: AI-elevated")))

    # Fixture 5 — allowlist negatives (PASS, zero flags). Each must NOT fire.
    #   (a) the bundle-label literals (narrative-decision-audit.md:88 + argument-decision-audit.md:89,92)
    for label in ('"AI-elevated: Structural streamlining"',
                  '"B1 — Structural arc (paragraph-role transitions)"',
                  '"B2 — Discourse-mode mix"'):
        chk("fx5_bundle_label_clean::%s" % label[:22], warns_of(label) == [])
    #   (b) the three mandated boilerplate sentences (D1: :165 / :185 / :177)
    for boiler in ("Word count vs. bounds; verdict band `uncalibrated`; calibration status literature_anchored.",
                   "The surface ships uncalibrated, with no thresholds and an `uncalibrated` verdict band.",
                   "It is *not* a threshold, *not* a verdict, *not* shipped per-signal."):
        chk("fx5_boilerplate_clean::%s" % boiler[:22], warns_of(boiler) == [])
    #   (c) the :157 "fair" summary sentence — CS1 needs `band`, which this lacks
    chk("fx5_fair_summary_clean",
        warns_of("this story scores high on sensory_embodied_performativity and structural_streamlining") == [])

    # Fixture 6 — override respected (PASS): a flagged paragraph with the override marker is quiet; a
    # suffixed-slug decoy and a code-span-quoted marker are NOT honored (M5 via override_marker).
    OV = "<!-- override: %s — SETEC's own docstring quoted verbatim -->" % _OVERRIDE_SLUG
    chk("fx6_override_silences",
        warns_of("the manuscript scores in the AI-elevated band\n%s" % OV) == [])
    chk("fx6_suffixed_slug_decoy_not_honored",
        any("CS1" in w for w in warns_of(
            "the manuscript scores in the AI-elevated band\n"
            "<!-- override: %s-but-not-really — decoy -->" % _OVERRIDE_SLUG)))
    chk("fx6_codespan_marker_not_honored",
        any("CS1" in w for w in warns_of(
            "the manuscript scores in the AI-elevated band\n`%s`" % OV)))

    # Fixture 7 — readiness-verdict disjointness (PASS): a severity-floor-legal readiness sentence fires
    # NOTHING. The D5 boundary proof — no CS pattern may match the four _HIGH_VERDICT_RE readiness tokens.
    for ready in ("Strong Fit; publishable as-is after the Must-Fix items are addressed.",
                  "This lands in the Highest Band for submission readiness.",
                  "Excellent Fit for the target market."):
        chk("fx7_readiness_disjoint::%s" % ready[:20], warns_of(ready) == [])

    # Fixture 8 — cross-contamination (PASS+WARN, attributed): one letter with a CLEAN narrative-decision
    # paragraph AND a VIOLATING argument-decision paragraph. Exactly one WARN, attributed to the violating
    # paragraph (quoted); the clean one not false-fired.
    F8 = (
        "## Narrative-Decision (StoryScope)\n\n"
        "StoryScope aggregate score -0.84; verdict band uncalibrated, provenance only — the structural "
        "signals lean AI-elevated, but this is not a verdict.\n\n"
        "## Argument-Decision (ArgScope)\n\n"
        "the op-ed scores in the AI-elevated band, confirming the piece is machine-drafted."
    )
    w8 = warns_of(F8)
    chk("fx8_exactly_one_warn", len(w8) == 1)
    chk("fx8_attributed_to_violation", w8 and "op-ed scores in the AI-elevated band" in w8[0])
    chk("fx8_clean_narrative_not_fired", not any("StoryScope aggregate" in w for w in w8))
    chk("fx8_strict_fails", scan(F8, strict=True)[0] == 1)

    # A paragraph with NO decision-audit content simply has no CS match (the unconditional whole-letter
    # scan is safe because the CS family is specific).
    chk("no_cs_match_clean",
        warns_of("Chapter 3 needs a stronger midpoint reversal; the reader loses the thread here.") == [])
    # editorial-threshold prose (Open Q2): CS3 requires `the/a/its threshold|cut-off` after a comparative,
    # so "above the threshold where a beta round helps" DOES match the shape — but it is quenched only if a
    # qualifier is present. Without decision-audit context it can false-fire; the override is the relief
    # valve. We assert the SHAPE narrowness: a bare comparative with no `threshold`/`cut-off` noun is clean.
    chk("editorial_no_threshold_noun_clean",
        warns_of("the draft is above average for a debut in this category") == [])

    # resolution: glob (newest), explicit file, no-artifact exit 2.
    import shutil
    import tempfile
    d = tempfile.mkdtemp()
    try:
        p = os.path.join(d, "Proj_Core_DE_Synthesis_run.md")
        with open(p, "w", encoding="utf-8", newline="") as fh:
            fh.write("# Editorial Letter\n\nverdict band uncalibrated, provenance only.\n")
        chk("run_folder_resolution", run([d])[0] == 0)
        chk("explicit_file_resolution", run([p])[0] == 0)
        chk("no_artifact_exit2", run([os.path.join(d, "nope.md")])[0] == 2)
        # a run folder with a VIOLATING letter fails under --strict
        pv = os.path.join(d, "Proj_Full_DE_Synthesis_run.md")
        with open(pv, "w", encoding="utf-8", newline="") as fh:
            fh.write("# Letter\n\nthe manuscript scores in the AI-elevated band\n")
        chk("run_folder_violation_strict_fails", run([d], strict=True)[0] == 1)
    finally:
        shutil.rmtree(d, ignore_errors=True)

    print("Self-test: PASS" if rc["v"] == 0 else "Self-test: FAIL")
    return rc["v"]


def main(argv):
    if "--self-test" in argv:
        return run_self_test()
    args = [a for a in argv[1:] if a != "calibration-honesty"]
    strict = "--strict" in args
    paths = [a for a in args if not a.startswith("--")]
    if not paths:
        print("Usage: calibration_honesty.py calibration-honesty <run_folder|files...> [--strict] "
              "| --self-test")
        return 2
    code, lines = run(paths, strict=strict)
    for ln in lines:
        print(ln)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
