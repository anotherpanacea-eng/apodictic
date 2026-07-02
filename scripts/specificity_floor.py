#!/usr/bin/env python3
"""specificity-floor — pre-letter re-grounding fidelity gate (docs/synthesis-regrounding.md, M2).

`validate.sh specificity-floor <editorial_letter> <findings_ledger> [--strict]` shells out here.
The Pre-Letter Re-Grounding step (run-synthesis.md §Processing Protocol, after the step-9b
Synthesis Coverage Manifest, before the Step 10 pre-output gate) re-reads the consolidated
Findings Ledger verbatim from disk and re-reads bounded manuscript spans for synthesis-bound
findings, restoring the counts / names / quote anchors that context-salience decay smears into
vague prose ("nine belief failures" -> "several belief failures"). This validator is the
checkable half of that step: it holds the delivered letter to the SPECIFICITY the ledger already
locked. Re-grounding may only ADD specificity — never a new finding, never a severity/confidence
change (those are Step 5 / Step 6b property, enforced elsewhere).

  Count floor    for each delivered finding ID, the finding's LEDGER ENTRY (the Notable Finding
                 prose sentence + its structured apodictic.finding.v1 block) is scanned for count
                 tokens (digits 2-99 and number-words two..ninety-nine; matching is
                 CASE-INSENSITIVE — a sentence-initial "Nine" satisfies a ledger "nine"). FAIL when
                 that ledger entry carries >= 1 count token AND the finding's LETTER WINDOW carries
                 a vague quantifier from VAGUE_QUANTIFIERS AND the window carries NONE of the
                 ledger's count tokens — the decayed-to-vague case. Override: an ID-scoped
                 `<!-- override: specificity-floor F-... — <rationale> -->` (for legitimately
                 non-countable findings) + an Appendix B entry.
  Anchor floor   each delivered Must-Fix window must carry >= 1 evidence reference that
                 token-matches one of that finding's locked evidence_refs — so a restored number
                 rides a ledger-matching anchor, bounding count-hallucination. Override: same
                 ID-scoped marker.
  Presence       the `<!-- regrounding: done -->` marker (letter) and the manifest's `regrounded`
                 annotation are the bash-checkable degrade-path floor; here they surface as an
                 ADVISORY W when the re-grounding step ran on a full-letter run but left no trace
                 (never a hard FAIL — the count/anchor floors are the teeth; the marker is a hint).

NOT this validator's job (single-ownership, spec §M2.3): the reverse-direction
letter-ID-must-exist-in-ledger check is `finding-trace` E1's — the sole owner. specificity-floor
implements NO reverse ID check; two enforcers with subtly different ID grammars is the drift risk
single ownership exists to prevent. The smuggled-finding gate is `validate.sh finding-trace`.

Firewall (spec §M2.3): re-grounding is read-only on the ledger. This validator reads severity to
select synthesis-bound findings and Must-Fix windows; it NEVER emits, compares, or rewrites a
severity/confidence value. Deficit Lock + softness-check (downstream) remain the severity gates.

LAUNCH POSTURE: the count floor and anchor floor are BLOCKING (ERROR, exit 1) — they are the
mechanical restoration teeth, and a decayed count or an unanchored restored number is a fidelity
failure, not an advisory. The regrounding-trace presence check is ADVISORY (WARN, exit 0);
--strict promotes it. (Mirrors finding-trace: hard errors block, coverage W is advisory.)

Untrusted-input containment: nothing in the letter or ledger drives a filesystem read or write —
both paths are CLI args, read once; all matching is in-memory string work.

  specificity_floor.py specificity-floor <editorial_letter> <findings_ledger> [--strict]
  specificity_floor.py --self-test

Exit: 0 clean / WARN-only, 1 ERROR (or WARN under --strict), 2 usage.
"""
import json
import os
import re
import sys

try:
    import apodictic_artifacts as art
except ImportError:
    art = None

# override_marker is the SSoT for override detection (code-span-stripped, boundary-matched); it
# always ships in the mirrored script dir. If it is somehow unimportable, override detection is
# DISABLED (fail-closed: no marker is honored) rather than reintroducing the bare-substring
# anti-pattern the M5 meta-linter forbids — a missed override is a loud, fixable FAIL, never a
# silent bypass.
try:
    from override_marker import has_override, strip_code_spans
except ImportError:  # pragma: no cover — the shared helper always ships in-repo
    def strip_code_spans(body):
        return body or ""

    def has_override(body, slug):
        return False

# ---------------------------------------------------------------- pinned vocabulary

# The vague-quantifier list, PINNED and tunable in this ONE place (mirrored byte-identical in the
# root scripts/ copy per the dual-mirror rule). Spec §M2.2 initial value, verbatim. Order is not
# semantic; kept as the spec lists it. Multi-word entries ("a few") are matched as phrases.
VAGUE_QUANTIFIERS = ("several", "some", "many", "a few", "numerous", "various", "multiple",
                     "a number of", "a handful", "repeated", "repeatedly")

# Number-words two..ninety-nine (the count range the floor cares about; "one" and 0/1 are not
# counts worth restoring — a single belief failure does not decay to "several"). Case-insensitive
# matching is applied at scan time, so these are stored lowercase.
_ONES = {"two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven",
         "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen",
         "nineteen"}
_TENS = {"twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"}
# number-words as canonical count tokens: the ones/teens, the round tens, and "tens-ones"
# ("twenty-one", "twenty one"). Built once; all lowercase.
_NUMBER_WORDS = _ONES | _TENS | {
    "%s%s%s" % (t, sep, o) for t in _TENS for o in
    ("one", "two", "three", "four", "five", "six", "seven", "eight", "nine") for sep in ("-", " ")}

# A count token in prose is either a 2-99 integer or one of the number-words above. \b word
# boundaries keep "19" out of "1984"; "nine" matching inside "ninefold" is intentionally allowed
# (the count survives) — we only care that SOME ledger count re-appears.
_DIGIT_RE = re.compile(r"(?<!\d)([2-9]\d?)(?!\d)")            # 2..99, no leading/trailing digit
_NUMBER_WORD_RE = re.compile(
    r"\b(" + "|".join(sorted((re.escape(w) for w in _NUMBER_WORDS), key=len, reverse=True)) + r")\b",
    re.IGNORECASE)

# Evidence-LOCATOR numbers are not semantic counts: "Ch 12", "sc. 30-31", "p. 40", "line 220",
# "Pass 5", "Chapter 9". They must be stripped before count extraction, or a scene/page number in
# the window would masquerade as a "restored count" and let a decayed "nine -> several" slip the
# floor (the window "several belief failures (sc. 30-31)" would otherwise share {30,31} with the
# ledger and pass). Applied to BOTH the ledger entry and the letter window, symmetrically.
_LOCATOR_RE = re.compile(
    r"\b(?:ch(?:apter)?\.?|sc(?:ene)?\.?|p(?:ages?|p)?\.?|lines?|pass(?:es)?|vol(?:ume)?\.?"
    r"|book|part|act|section|§)\s*\.?\s*\d+(?:\s*[–—-]\s*\d+)?",
    re.IGNORECASE)

# The letter cites a delivered finding with the pinned canonical HTML-comment form
# `<!-- finding: F-... -->` (output-policy.md §Deficit Lock), placed at the END of the finding's
# descriptive prose (the in-repo convention: example-editorial-letter.md — "...two sentences.
# <!-- finding: F-RR-01 -->"). The window for a finding is therefore the prose BLOCK the marker
# belongs to: bounded on BOTH sides by the nearest other finding marker or `^##`/`###` column-0
# header. The evidence-density window rule (run-synthesis.md §Processing Protocol) is
# "from each marker to the next marker OR the next `^##` header"; because the descriptive text
# precedes the marker, the window is taken between the previous boundary and the next one, so it
# captures the sentence the marker terminates. IDs are the exact art.FID_RE token (F-P5-01 !=
# F-P5-011).
_FID_RE = art.FID_RE if art is not None else re.compile(r"(?<![\w-])F-[A-Za-z0-9]+-[0-9]{2,}(?![\w-])")
_FINDING_MARKER_RE = re.compile(r"<!--\s*finding:\s*(" + _FID_RE.pattern + r")\s*-->")
# A window boundary: a `##`/`###` column-0 section header. (Finding markers are the other
# boundary, handled directly in letter_windows.)
_SECTION_HEADER_RE = re.compile(r"^#{2,3}\s", re.MULTILINE)
_REGROUNDING_DONE_RE = re.compile(r"<!--\s*regrounding:\s*done\s*-->", re.IGNORECASE)
# Chapter references in the letter window, any surface form ("Chapter 9", "Ch 12", "Ch.3") — the
# anchor floor matches on the chapter NUMBER, so the letter's spelling need not equal the ledger's.
_WINDOW_CH_RE = re.compile(r"\bch(?:apter)?\.?\s*(\d+)\b", re.IGNORECASE)

# Full-letter detection (the coverage obligation shape, run-synthesis.md §Annotated-Manuscript
# offer) — used only to scope the advisory regrounding-trace check to runs that actually wrote a
# letter; it never gates the count/anchor floors, which apply to any letter passed in.
_LETTER_TITLE_RE = re.compile(r"^#\s", re.MULTILINE)


def _read(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return None


# ---------------------------------------------------------------- count-token extraction

def count_tokens(text):
    """The set of canonical SEMANTIC count tokens in `text`: integers 2-99 (as their str) and
    number-words two..ninety-nine (normalized lowercase, spaces->hyphens so "twenty one" ==
    "twenty-one"). Evidence-locator numbers (Ch 12, sc. 30-31, p. 40, Pass 5, line 220) are
    stripped FIRST so a scene/page number never masquerades as a restored count. Case-insensitive.
    Applied to BOTH the ledger entry and the letter window; a ledger count re-appears in the window
    iff the two sets intersect."""
    body = _LOCATOR_RE.sub(" ", text or "")
    toks = set()
    for m in _DIGIT_RE.finditer(body):
        toks.add(m.group(1))
    for m in _NUMBER_WORD_RE.finditer(body):
        toks.add(m.group(1).lower().replace(" ", "-"))
    return toks


def has_vague_quantifier(text):
    """The vague quantifiers present in `text` (case-insensitive, word-boundary; multi-word
    entries matched as whitespace-flexible phrases). Returns the matched surface list (for the
    error message), or []."""
    hits = []
    low = (text or "")
    for q in VAGUE_QUANTIFIERS:
        # whitespace-flexible phrase match, word-bounded, case-insensitive
        pat = r"\b" + r"\s+".join(re.escape(w) for w in q.split()) + r"\b"
        if re.search(pat, low, re.IGNORECASE):
            hits.append(q)
    return hits


# ---------------------------------------------------------------- ledger entry parsing

def ledger_entries(ledger_text):
    """{fid: entry_text} — for each apodictic.finding.v1 block in the ledger, the ENTRY text: the
    region from the nearest preceding `##`/`###` header (the Mechanism section, carrying the
    Notable Finding prose sentence) through the finding block itself, up to the next `##`/`###`
    header. So the count floor reads the ledger's count both from the prose ("nine belief
    failures") and from the structured block.

    Each block is located INDEPENDENTLY (its own regex span parsed to an id) rather than by zipping
    a filtered parse_blocks list against a filtered span list — so a malformed sibling block can
    never desync the id<->span pairing. A non-string id is fid_key-coerced (crash-class SSoT).
    Duplicate ids (author error; structured-findings owns that) union their sections so the floor
    never under-reads a count."""
    entries = {}
    if not ledger_text:
        return entries
    lines = ledger_text.split("\n")
    header_idx = [i for i, ln in enumerate(lines) if re.match(r"#{2,3}\s", ln)]

    def section_of_offset(char_pos):
        """The text of the `##`/`###` section containing char offset char_pos."""
        running, line_of = 0, len(lines) - 1
        for i, ln in enumerate(lines):
            if running + len(ln) >= char_pos:
                line_of = i
                break
            running += len(ln) + 1
        start, end = 0, len(lines)
        for h in header_idx:
            if h <= line_of:
                start = h
            elif h > line_of:
                end = h
                break
        return "\n".join(lines[start:end])

    # Each finding block, located by its own span; the id is parsed from that span's payload so
    # span and id always belong to the same block (no cross-list zip).
    for mo in re.finditer(r"<!--\s*apodictic:finding\s*(.*?)\s*-->", ledger_text, re.DOTALL):
        try:
            obj = json.loads(mo.group(1).strip())
        except (ValueError, TypeError):
            continue
        if not isinstance(obj, dict):
            continue
        fid = art.fid_key(obj.get("id")) if art is not None else (
            obj.get("id") if isinstance(obj.get("id"), str) else None)
        if not fid:
            continue
        entry = section_of_offset(mo.start())
        entries[fid] = (entries.get(fid, "") + "\n" + entry) if fid in entries else entry
    return entries


def ledger_severities(ledger_text):
    """{fid: severity} for the ledger's finding blocks (used to select synthesis-bound findings
    and Must-Fix windows). Severity is read here ONLY to CLASSIFY — never emitted or compared as a
    fidelity signal (the firewall: this validator does not touch severity)."""
    sev = {}
    if not ledger_text or art is None:
        return sev
    for bt, obj, _e in art.parse_blocks(ledger_text):
        if bt == "finding" and isinstance(obj, dict):
            fid = art.fid_key(obj.get("id"))
            if fid:
                sev[fid] = obj.get("severity")
    return sev


def ledger_evidence_refs(ledger_text):
    """{fid: [ref, ...]} — the locked evidence_refs of each finding (string entries only; a
    non-string ref is structured-findings' schema gate, skipped here)."""
    refs = {}
    if not ledger_text or art is None:
        return refs
    for bt, obj, _e in art.parse_blocks(ledger_text):
        if bt == "finding" and isinstance(obj, dict):
            fid = art.fid_key(obj.get("id"))
            if not fid:
                continue
            raw = obj.get("evidence_refs")
            refs[fid] = [r for r in raw if isinstance(r, str)] if isinstance(raw, list) else []
    return refs


# ---------------------------------------------------------------- letter window parsing

def letter_windows(letter_text):
    """{fid: window_text} — for each `<!-- finding: F-... -->` marker in the letter (code spans
    stripped, so a marker quoted as a doc example is not honored), the prose BLOCK the marker
    TERMINATES: from the nearest preceding boundary (the previous finding marker's END or the
    previous `^##`/`###` header, whichever is closer) up to and including THIS marker. Because the
    marker sits at the END of the finding's descriptive sentence (example-editorial-letter.md:
    "...two sentences. <!-- finding: F-RR-01 -->"), the window bounded on the RIGHT by the marker's
    own end captures exactly that finding's prose — and does NOT bleed into the NEXT finding's
    sentence (which the next marker terminates). A finding cited twice unions its windows (the
    floor must see every place a count could be restored)."""
    stripped = strip_code_spans(letter_text or "")
    markers = [(m.start(), m.end(), m.group(1)) for m in _FINDING_MARKER_RE.finditer(stripped)]
    headers = [m.start() for m in _SECTION_HEADER_RE.finditer(stripped)]
    marker_ends = [e for _s, e, _f in markers]
    windows = {}
    for start, end, fid in markers:
        # left boundary: the closest of {a header start before this marker, a PRIOR marker's end};
        # right boundary: this marker's own end (the marker terminates the finding's sentence).
        left = max([0] + [h for h in headers if h < start]
                   + [me for me in marker_ends if me <= start], default=0)
        w = stripped[left:end]
        windows[fid] = (windows.get(fid, "") + "\n" + w) if fid in windows else w
    return windows


def _window_chapters(text):
    """The set of chapter NUMBERS named anywhere in `text` (any surface form — "Chapter 9",
    "Ch 12", "Ch.3", "ch 4"). Compared against a ref's normalized chapter number, so the anchor
    floor matches on the chapter the ledger locked regardless of how the letter spelled it."""
    return {int(m.group(1)) for m in _WINDOW_CH_RE.finditer(text or "")}


def ref_token_match(window_text, refs):
    """True iff the window carries at least one evidence reference matching a locked evidence_ref.
    A chapter ref matches when its chapter NUMBER appears anywhere in the window (surface-form
    independent — "Chapter 9" in the letter matches a ledger ref "Chapter 9"/"Ch 9"). A ref with no
    chapter (a contract-artifact ref) matches on any distinctive >=4-char token. Conservative: the
    anchor floor only needs ONE ledger-matching anchor."""
    if not refs:
        return True  # no locked refs to tie to (schema requires minItems 1, but be graceful)
    win_chs = _window_chapters(window_text)
    low = window_text.lower()
    for r in refs:
        ch = art.chapter_token(r) if art is not None else None
        if ch is not None:
            m = re.search(r"(\d+)", ch)
            if m and int(m.group(1)) in win_chs:
                return True
        else:
            # non-chapter ref: match on any distinctive token of length >= 4
            for w in re.findall(r"[A-Za-z0-9][A-Za-z0-9-]{3,}", r):
                if w.lower() in low:
                    return True
    return False


# ---------------------------------------------------------------- the check

def check(letter_text, ledger_text, strict=False):
    """Run the count floor + anchor floor + regrounding-trace advisory. Returns (code, lines)."""
    lines, errs, warns = [], [], []

    sev = ledger_severities(ledger_text)
    if not sev:
        return 0, ["specificity-floor: no ledger findings found — nothing to hold to specificity"]

    entries = ledger_entries(ledger_text)
    refs = ledger_evidence_refs(ledger_text)
    windows = letter_windows(letter_text)
    letter_stripped = strip_code_spans(letter_text or "")

    delivered = sorted(windows)   # findings actually cited in the letter body
    for fid in delivered:
        window = windows[fid]
        # per-ID override (legitimately non-countable / non-anchorable) — code-span-stripped,
        # boundary-matched, ID-scoped via the shared helper (meta-lint M5).
        if _fid_override(letter_stripped, fid):
            continue

        # ---- count floor ----
        entry = entries.get(fid, "")
        ledger_counts = count_tokens(entry)
        if ledger_counts:
            window_counts = count_tokens(window)
            vague = has_vague_quantifier(window)
            if vague and not (ledger_counts & window_counts):
                errs.append("count floor: %s — the ledger locks count(s) {%s} but the delivered "
                            "window says %r with no restored count (re-grounding must restore the "
                            "exact number, not decay it to a vague quantifier). Override with "
                            "<!-- override: specificity-floor %s — <why non-countable> --> + an "
                            "Appendix B entry if this finding is legitimately non-countable."
                            % (fid, ", ".join(sorted(ledger_counts)), vague[0], fid))

        # ---- anchor floor (Must-Fix only) ----
        if sev.get(fid) == "Must-Fix":
            if not ref_token_match(window, refs.get(fid, [])):
                errs.append("anchor floor: Must-Fix %s — the delivered window carries no evidence "
                            "reference matching the finding's locked evidence_refs (%s); a restored "
                            "number must ride a ledger-matching anchor. Override with "
                            "<!-- override: specificity-floor %s — <why> --> + Appendix B."
                            % (fid, refs.get(fid, []), fid))

    # ---- regrounding-trace advisory (scoped to full-letter runs) ----
    is_full_letter = _LETTER_TITLE_RE.search(letter_stripped) is not None
    if is_full_letter and not _REGROUNDING_DONE_RE.search(letter_stripped):
        warns.append("regrounding trace: no `<!-- regrounding: done -->` marker in the letter — "
                     "the Pre-Letter Re-Grounding step writes it after re-reading the ledger and "
                     "restoring specificity (run-synthesis.md §Processing Protocol). Presence is "
                     "advisory; the count/anchor floors are the teeth.")

    # ---- report ----
    lines.append("specificity-floor: %d ledger finding(s), %d delivered in the letter"
                 % (len(sev), len(delivered)))
    for e in errs:
        lines.append("  ERROR: %s" % e)
    for w in warns:
        lines.append("  %s: %s" % ("ERROR (--strict)" if strict else "WARN", w))

    if errs or (strict and warns):
        lines.append("specificity-floor: FAIL (%d error(s)%s)"
                     % (len(errs), ", %d strict warn(s)" % len(warns) if (strict and warns) else ""))
        return 1, lines
    if warns:
        lines.append("specificity-floor: PASS with %d WARN (regrounding-trace advisory; --strict "
                     "promotes)" % len(warns))
        return 0, lines
    lines.append("specificity-floor: PASS (count floor + anchor floor clean)")
    return 0, lines


def _fid_override(letter_stripped, fid):
    """True iff a live ID-scoped `<!-- override: specificity-floor F-... -->` marker names `fid`.

    Uses the shared override_marker discipline (code spans already stripped by the caller, but
    has_override re-strips harmlessly) with the ID as part of the slug so the acknowledgement is
    finding-scoped: a bare `specificity-floor` marker acknowledges nothing (mirrors the
    softness-downgrade ID-scoping in run-synthesis.md §Deficit Lock)."""
    return has_override(letter_stripped, "specificity-floor %s" % fid)


# ---------------------------------------------------------------- self-test

def _finding(fid, severity, refs, mechanism="m"):
    return ('<!-- apodictic:finding\n{"schema":"apodictic.finding.v1","id":"%s","mechanism":"%s",'
            '"severity":"%s","confidence":"HIGH","evidence_refs":%s,"fix_class":"x",'
            '"risk_if_fixed":"y"}\n-->' % (fid, mechanism, severity, json.dumps(refs)))


# The founding example (docs/subagent-architecture-design.md:15): Pass 1's "nine belief failures".
_LEDGER = (
    "# Findings Ledger — Example (consolidated)\n\n"
    "## Mechanism: Unmotivated Confession\n\n### Notable Findings\n\n"
    "The narrator's Ch 12 confession (sc. 30-31) lands with no visible pressure — nine\n"
    "belief failures cluster here (confirmed by Pass 1, Pass 5).\n\n"
    + _finding("F-P5-01", "Must-Fix", ["Ch 12 (sc. 30-31)"], "unmotivated confession") + "\n\n"
    "## Mechanism: Opening Orientation Drag\n\n### Notable Findings\n\n"
    "Ch 3 opens without re-anchoring the timeline after the Ch 2 jump.\n\n"
    + _finding("F-P1-02", "Should-Fix", ["Ch 3"], "orientation drag") + "\n")


def _letter(short, whatneeds, regrounded=True):
    """A minimal letter: title block, optional regrounding marker, a Short Version, and a
    'What Needs Work' section carrying the finding windows."""
    rg = "<!-- regrounding: done -->\n" if regrounded else ""
    return ("# Development Edit: Example\n### A. Author | 118,000 words | Draft 3\n"
            "*APODICTIC Development Editor v2 — 2026-01-01*\n\n"
            "<!-- coverage: ok -->\n" + rg + "\n"
            "## The Short Version\n\n" + short + "\n\n"
            "## What Needs Work\n\n" + whatneeds + "\n")


def run_self_test():
    rc = {"v": 0}

    def chk(name, cond):
        print("  %s: %s" % (name, "OK" if cond else "FAIL"))
        if not cond:
            rc["v"] = 1

    def out_has(lines, token):
        return any(token in ln for ln in lines)

    # 1. GREEN: the restored letter names "nine belief failures" with the Ch 12 anchor
    green = _letter(
        "The book works; targeted revision.",
        "The Ch 12 confession triggers nine belief failures (sc. 30-31). "
        "<!-- finding: F-P5-01 -->\n\n"
        "Ch 3 opens without re-anchoring the timeline. <!-- finding: F-P1-02 -->")
    code, lines = check(green, _LEDGER)
    chk("green_restored_pass", code == 0 and out_has(lines, "count floor + anchor floor clean"))
    chk("green_restored_strict", check(green, _LEDGER, strict=True)[0] == 0)

    # 2. SALIENCE-DECAY (the headline, spec fixture M2-1): "several belief failures", no count
    decayed = _letter(
        "The book works; targeted revision.",
        "The Ch 12 confession triggers several belief failures (sc. 30-31). "
        "<!-- finding: F-P5-01 -->")
    code, lines = check(decayed, _LEDGER)
    chk("decay_count_floor_fail", code == 1 and out_has(lines, "ERROR: count floor")
        and out_has(lines, "F-P5-01") and out_has(lines, "several"))

    # 3. CASING (spec fixture M2-6): a sentence-initial "Nine" satisfies the ledger "nine"
    cased = _letter(
        "The book works.",
        "Nine belief failures cluster at the Ch 12 confession (sc. 30-31), even after several "
        "smaller beats. <!-- finding: F-P5-01 -->")
    code, lines = check(cased, _LEDGER)
    chk("casing_pass", code == 0 and out_has(lines, "count floor + anchor floor clean"))

    # 4. ANCHOR-DRIFT (spec fixture M2-2): a Must-Fix window with a vague quantifier avoided but no
    #    ledger-matching evidence reference -> anchor-floor FAIL
    drift = _letter(
        "The book works.",
        "The confession triggers nine belief failures, though the chapter is hard to place. "
        "<!-- finding: F-P5-01 -->")
    code, lines = check(drift, _LEDGER)
    chk("anchor_drift_fail", code == 1 and out_has(lines, "ERROR: anchor floor")
        and out_has(lines, "F-P5-01"))

    # 5. LEGITIMATE-VAGUENESS (spec fixture M2-5): ID-scoped override + (Appendix B is prose) -> pass
    overridden = _letter(
        "The book works.",
        "The confession triggers several belief failures at Ch 12 (sc. 30-31). "
        "<!-- finding: F-P5-01 --> "
        "<!-- override: specificity-floor F-P5-01 — the cluster count varies by reader; not a "
        "fixed number -->")
    code, lines = check(overridden, _LEDGER)
    chk("override_pass", code == 0 and out_has(lines, "count floor + anchor floor clean"))

    # 6. SMUGGLED FINDING is finding-trace E1's, NOT ours (spec §M2.3 / fixture M2-3): a letter
    #    citing an ID absent from the ledger is simply NOT a delivered window here — no false
    #    count/anchor failure, no reverse-ID enforcement duplicated.
    smuggled = _letter(
        "The book works.",
        "A new problem: several structural gaps. <!-- finding: F-P5-99 -->")
    code, lines = check(smuggled, _LEDGER)
    chk("smuggled_not_our_job", code == 0 and not out_has(lines, "F-P5-99"))

    # 7. MASKING is M1's V5, NOT ours (spec fixture M2-4): re-grounding cannot silence the coverage
    #    note. Here we only confirm specificity-floor does not spuriously pass/fail on a
    #    regrounding marker — the manifest/marker masking is synthesis-coverage's tooth.
    #    (specificity-floor is orthogonal: it holds counts, not coverage.)
    code, lines = check(green, _LEDGER)
    chk("masking_is_m1s_job", code == 0)

    # 8. no finding markers in the letter -> nothing delivered -> vacuous pass (a legacy/no-marker
    #    letter is graceful, not a failure — mirrors crosslink's no-marker handling)
    nomarkers = _letter("The book works.", "The Ch 12 confession needs pressure.")
    code, lines = check(nomarkers, _LEDGER)
    chk("no_markers_graceful", code == 0 and out_has(lines, "0 delivered"))

    # 9. REGROUNDING-TRACE advisory: a full letter with delivered findings but no regrounding
    #    marker -> WARN by default (exit 0), ERROR under --strict
    no_trace = _letter(
        "The book works.",
        "The confession triggers nine belief failures at Ch 12 (sc. 30-31). "
        "<!-- finding: F-P5-01 -->", regrounded=False)
    code, lines = check(no_trace, _LEDGER)
    chk("no_trace_warn", code == 0 and out_has(lines, "WARN") and out_has(lines, "regrounding trace"))
    chk("no_trace_strict_fails", check(no_trace, _LEDGER, strict=True)[0] == 1)

    # 10. VAGUE MULTI-WORD quantifier ("a number of") is caught
    multiword = _letter(
        "The book works.",
        "The confession triggers a number of belief failures at Ch 12 (sc. 30-31). "
        "<!-- finding: F-P5-01 -->")
    code, lines = check(multiword, _LEDGER)
    chk("multiword_vague_fail", code == 1 and out_has(lines, "count floor")
        and out_has(lines, "a number of"))

    # 11. HOSTILE: an override marker quoted inside a code fence must NOT be honored (M5 helper)
    fenced_override = _letter(
        "The book works.",
        "The confession triggers several belief failures at Ch 12 (sc. 30-31). "
        "<!-- finding: F-P5-01 -->\n\n```\n<!-- override: specificity-floor F-P5-01 — decoy -->\n```")
    code, lines = check(fenced_override, _LEDGER)
    chk("fenced_override_not_honored", code == 1 and out_has(lines, "count floor"))

    # 12. HOSTILE: a suffixed override slug (`specificity-floor-extra`) must NOT satisfy the
    #     ID-scoped override for F-P5-01 (boundary discipline via override_marker)
    suffixed = _letter(
        "The book works.",
        "The confession triggers several belief failures at Ch 12 (sc. 30-31). "
        "<!-- finding: F-P5-01 --> "
        "<!-- override: specificity-floor-extra F-P5-01 — not the right slug -->")
    code, lines = check(suffixed, _LEDGER)
    chk("suffixed_override_rejected", code == 1 and out_has(lines, "count floor"))

    # 13. HOSTILE: the count token appears only inside a manuscript QUOTE in the window — it still
    #     counts (the floor matches over the window's full text; documented). A restored quote that
    #     carries the number satisfies the floor.
    quoted_count = _letter(
        "The book works.",
        'The confession — "the nine of them each recanted" — lands unmotivated at Ch 12 '
        "(sc. 30-31). <!-- finding: F-P5-01 -->")
    code, lines = check(quoted_count, _LEDGER)
    chk("count_in_quote_counts", code == 0)

    # 14. FIREWALL: a finding delivered with a DIFFERENT severity word in its window must not be
    #     read as a severity signal — the validator only classifies from the ledger. A window that
    #     merely contains the word "Must-Fix" in prose changes nothing.
    sev_word = _letter(
        "The book works.",
        "The confession triggers nine belief failures at Ch 12 (sc. 30-31); this is Should-Fix "
        "at most. <!-- finding: F-P1-02 -->")
    code, lines = check(sev_word, _LEDGER)
    chk("severity_word_ignored", code == 0)

    # 15. digit form: the ledger prose could carry "9" and the letter "9" — digit restoration works
    led_digit = _LEDGER.replace("nine\nbelief", "9\nbelief")
    dig = _letter(
        "The book works.",
        "The confession triggers 9 belief failures at Ch 12 (sc. 30-31). <!-- finding: F-P5-01 -->")
    code, lines = check(dig, led_digit)
    chk("digit_restoration_pass", code == 0)
    dig_bad = _letter(
        "The book works.",
        "The confession triggers several belief failures at Ch 12 (sc. 30-31). "
        "<!-- finding: F-P5-01 -->")
    code, lines = check(dig_bad, led_digit)
    chk("digit_decay_fail", code == 1 and out_has(lines, "count floor"))

    # 16. a ledger finding with NO count token in its entry never fires the count floor even under
    #     a vague window (nothing to restore) — F-P1-02 has no count in prose or block
    no_count = _letter(
        "The book works.",
        "Ch 3 opens without re-anchoring after several jumps. <!-- finding: F-P1-02 -->")
    code, lines = check(no_count, _LEDGER)
    chk("no_ledger_count_no_fire", code == 0)

    # 17. empty ledger -> nothing to trace
    code, lines = check(green, "# empty ledger\n")
    chk("empty_ledger_noop", code == 0 and out_has(lines, "nothing to hold"))

    print("Self-test: PASS" if rc["v"] == 0 else "Self-test: FAIL")
    return rc["v"]


def main(argv):
    if "--self-test" in argv:
        return run_self_test()
    args = [a for a in argv[1:] if a != "specificity-floor"]
    strict = "--strict" in args
    paths = [a for a in args if not a.startswith("--")]
    if len(paths) != 2 or not os.path.isfile(paths[0]) or not os.path.isfile(paths[1]):
        print("Usage: specificity_floor.py specificity-floor <editorial_letter> <findings_ledger> "
              "[--strict] | --self-test")
        return 2
    letter_text = _read(paths[0]) or ""
    ledger_text = _read(paths[1]) or ""
    code, lines = check(letter_text, ledger_text, strict=strict)
    for ln in lines:
        print(ln)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
