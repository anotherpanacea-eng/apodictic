#!/usr/bin/env python3
"""promise-contract — Promise-Contract Fidelity: does the pitch keep the promise the book makes?

`validate.sh promise-contract <run_folder|files>` shells out here. APODICTIC's foundational move is
contract inference; this module points it at the author's own marketing COPY. It diagnoses the gap
between the persisted pitch (query / synopsis / blurb / logline) and the inferred Contract — emphasis
distortion, reveal leak, over/under-promise, cross-document inconsistency — and never drafts the
replacement copy (the Firewall: diagnose the copy, never write it). It CONSUMES Shelf & Positioning
(genre / comp / tone) rather than re-deriving it; this module owns only the document-fidelity layer.

Findings are apodictic.finding.v1 blocks with origin PCF (id F-PCF-NN). Each PCF flag is a two-sided
GAP, so it must cite both sides via a namespaced evidence-ref convention scoped to PCF findings:
  copy:<copy_type>¶<n>   a span in the persisted pitch copy (e.g. copy:query¶2)
  contract:<FIELD>       a Contract field (e.g. contract:CONTROLLING IDEA, contract:READER PROMISE)
  ms:<locus>             a manuscript locus (e.g. ms:Ch 9)
The persisted pitch copy is apodictic.pitch_copy.v1 (a first-class durable input, NOT a runtime
paste); persisting it is what makes the firewall guard (W1) a substring check and the form gate (P3)
mechanical.

  P1 two-sided gap     every F-PCF-NN finding carries >=1 copy: ref AND >=1 contract:/ms: ref. A
                       one-sided "gap" is an unsupported assertion — the signature integrity check.
  P2 copy persisted    an apodictic.pitch_copy.v1 input exists and every document declares a valid
                       & typed       copy_type. Flags are form-calibrated; an undeclared/absent copy makes
                       PCF2/PCF5 ungovernable.
  P3 reveal-leak       a PCF2 finding's copy: ref must NOT point at a synopsis. A synopsis discloses
                       form gate     by design, so a PCF2 raised against one is a calibration error and fails.
  W1 drafted-copy      a multi-sentence quoted block in the report that is NOT a verbatim substring
                       leak (firewall)  of the persisted pitch copy => authored replacement copy (the Firewall
                       leak). Concrete substring check, not a vibe heuristic. Advisory; ERROR --strict.
                       Override (per id): <!-- override: drafted-copy PCF-NN — <rationale> -->.
  W2 market-prediction a PCF finding matching the prohibited sales-prediction phrase set ("won't
                       drift (#14)      sell", "agents will pass", "no market for", "unmarketable", "won't find
                       an audience"). Keeps the module on the fidelity side of the §Not Planned line.
                       Advisory; ERROR --strict. Override: <!-- override: market-prediction PCF-NN — … -->.

severity is the editorial Must/Should/Could scale, where severity = fidelity risk (how badly promise
and book diverge), never market outcome. Reuses apodictic_artifacts (block grammar + schema engine).
Each artifact is optional; an empty/absent one is a no-op. See docs/promise-contract-audit.md.

  promise_contract.py promise-contract <run_folder|files...> [--strict]
  promise_contract.py --self-test

Exit: 0 clean / WARN-only, 1 ERROR (or WARN under --strict), 2 usage.
"""
import glob
import os
import re
import sys

from override_marker import override_targets, override_payloads  # SSoT: code-span-stripped override scan

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

_PITCH_SCHEMA_ID = "apodictic.pitch_copy.v1"
_FINDING_SCHEMA_ID = "apodictic.finding.v1"
_PITCH_GLOB = "*_Pitch_Copy_*.md"
_ORIGIN = "PCF"

# A well-formed PCF finding id: F-PCF-NN. The short form used in override markers is PCF-NN.
_PCF_ID_RE = re.compile(r"^F-PCF-[0-9]{2,}$")
# PCF-ORIGIN attribution (looser than the well-formed id): any F-PCF-* claims this module, so a
# malformed digit count (F-PCF-1) is still attributed to PCF and caught by the schema pattern (P1),
# rather than silently dropped by the origin filter.
_PCF_ORIGIN_RE = re.compile(r"^F-PCF-", re.IGNORECASE)
# Map an F-PCF-NN finding id to its short PCF-NN override token.
_SHORT_RE = re.compile(r"^F-(PCF-[0-9]+)$")

# Namespaced evidence-ref convention (PCF-scoped). A ref is prefix-typed; optional whitespace after
# the colon is tolerated (the ref is also .strip()ed in _ref_kind) so a stray space can't drop a real
# two-sided ref into the unknown bucket and falsely fail P1.
# copy:<copy_type>¶<n> — the FULL grammar: a copy_type AND a non-empty paragraph locus (¶<n>, range
# ok). A locus-less `copy:query`, a malformed `copy:query-does-not-exist` (no ¶), or a bare `copy:`
# names no span and must NOT satisfy P1's copy side; the captured copy_type is then checked for
# membership in the PERSISTED copy in check() (a `copy:<absent-type>¶n` is dangling). (Codex P1.)
_COPY_REF_RE = re.compile(r"^copy:\s*([A-Za-z]+)\s*¶\s*[0-9]+(?:\s*-\s*[0-9]+)?\s*$", re.IGNORECASE)
# contract:/ms: must carry a NON-EMPTY target (a field name / a locus). A bare `contract:` or `ms:`
# (or whitespace-only) names no side and must NOT satisfy the two-sided P1 check (Codex P1, 2026-06-19).
_CONTRACT_REF_RE = re.compile(r"^contract:\s*\S", re.IGNORECASE)
_MS_REF_RE = re.compile(r"^ms:\s*\S", re.IGNORECASE)

# Override markers naming a finding's short id ("<!-- override: market-prediction PCF-01 — ... -->")
# route through the shared override_marker SSoT — code spans stripped, slug boundary-matched.

# W1's drafted-copy override is SNIPPET-keyed, not id-keyed: a report's leaked quote isn't
# attributable to one finding id, so the override quotes a snippet of the leaked text and silences
# ONLY a leak that snippet matches — "<!-- override: drafted-copy <snippet> — <rationale> -->".
# This stops one override from blanket-silencing the firewall and stops an override for absent text
# from silencing a real leak.
# The drafted-copy snippet is the free-text PAYLOAD of a `drafted-copy` marker; it is read via the
# shared override_marker SSoT (override_payloads) so a backtick'd example is not honored.

# HTML comments (incl. the apodictic:* blocks and the override markers) are stripped before the W1
# prose scan, so the persisted-copy blocks and impl notes are not themselves mistaken for report prose.
_HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)

# W2 — the prohibited sales-prediction phrase set (the #14 boundary guard). Concrete, not a vibe set.
_MARKET_RE = re.compile(
    r"won'?t\s+sell"
    r"|agents?\s+will\s+pass"
    r"|no\s+market\s+for"
    r"|unmarketable"
    r"|won'?t\s+find\s+an\s+audience",
    re.IGNORECASE)


def _read(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return None


def _overrides(text, slug):
    """The set of PCF-NN ids overridden for `slug` — via the shared SSoT, so a marker quoted inside a
    code span is not honored as a live directive."""
    return {t[0] for t in override_targets(text, slug, r"(PCF-[0-9]+)")}


def _drafted_override_snippets(text):
    """Snippets from `<!-- override: drafted-copy <snippet> — <rationale> -->` markers (W1). The
    captured group is split on the em-/en-/hyphen rationale separator and de-quoted; a leak is
    silenced only when one of these snippets is a substring of (or contains) the leaked block."""
    out = []
    for payload in override_payloads(text or "", "drafted-copy"):
        snip = re.split(r"\s+[—–-]\s+", payload, 1)[0].strip().strip('"“”')
        if snip:
            out.append(snip)
    return out


def _short(fid):
    m = _SHORT_RE.match(fid or "")
    return m.group(1) if m else (fid or "")


def parse_pitch(text):
    """[(obj_or_None, schema_errs, index), ...] for each apodictic:pitch_copy block."""
    items = []
    if not text or art is None:
        return items
    schema = art.load_schema(_PITCH_SCHEMA_ID)
    idx = 0
    for btype, obj, jerr in art.parse_blocks(text):
        if btype != "pitch_copy":
            continue
        idx += 1
        where = "pitch_copy #%d" % idx
        if jerr:
            items.append((None, ["%s: invalid JSON — %s" % (where, jerr)], idx))
            continue
        items.append((obj, art.validate_obj(obj, schema, where), idx))
    return items


def parse_findings(text):
    """[(obj_or_None, schema_errs, index), ...] for each apodictic:finding block with origin PCF."""
    items = []
    if not text or art is None:
        return items
    schema = art.load_schema(_FINDING_SCHEMA_ID)
    idx = 0
    for btype, obj, jerr in art.parse_blocks(text):
        if btype != "finding":
            continue
        # PCF owns only PCF-origin findings; another origin's finding in the same corpus is ignored.
        # Attribution is by the F-PCF- prefix (loose), so a malformed PCF id is still validated (P1).
        if isinstance(obj, dict) and not _PCF_ORIGIN_RE.match(str(obj.get("id") or "")):
            continue  # non-PCF-origin finding ignored; a non-dict payload falls through to validate_obj (P1)
        if jerr:
            # A malformed finding JSON can't be attributed to an origin; skip rather than mis-claim it.
            continue
        idx += 1
        where = "finding %s" % (obj.get("id") if isinstance(obj, dict) else "#%d" % idx)
        items.append((obj, art.validate_obj(obj, schema, where), idx))
    return items


def _ref_kind(ref):
    """Classify a namespaced evidence-ref. Returns ('copy', copy_type) | ('contract', None) |
    ('ms', None) | (None, None)."""
    s = str(ref or "").strip()
    m = _COPY_REF_RE.match(s)
    if m:
        return "copy", m.group(1).lower()
    if _CONTRACT_REF_RE.match(s):
        return "contract", None
    if _MS_REF_RE.match(s):
        return "ms", None
    return None, None


def _is_pcf2(obj):
    """A PCF2 (reveal leak) finding — identified by the flag DECLARED at the head of its mechanism
    (the "PCFn <name>: …" convention), not a mere mention of PCF2 elsewhere in the prose. A PCF1/PCF4
    finding may contrast itself against PCF2 ("…distinct from PCF2 reveal leak…") while legitimately
    citing a synopsis ref; anchoring to the leading flag stops that from tripping the P3 form gate."""
    return bool(re.match(r"\s*PCF2\b", obj.get("mechanism") or ""))


# Multi-sentence quoted-block detection for W1. A "quoted block" is a run inside straight or curly
# double quotes whose content holds >=2 sentence terminators — i.e. authored multi-sentence prose, the
# shape a drafted replacement query/blurb takes. A single quoted phrase (a label, a cited span) is not.
_QUOTED_BLOCK_RE = re.compile(r"[\"“]([^\"“”]{2,}?)[\"”]", re.DOTALL)
_SENT_TERM_RE = re.compile(r"[.!?](?:\s|$)")


def _multi_sentence_quotes(report_text):
    """Multi-sentence quoted blocks in report prose (HTML comments/blocks stripped first)."""
    visible = _HTML_COMMENT_RE.sub("", report_text or "")
    out = []
    for m in _QUOTED_BLOCK_RE.finditer(visible):
        body = m.group(1).strip()
        if len(_SENT_TERM_RE.findall(body)) >= 2:
            out.append(body)
    return out


def check(pitch_text, report_text, strict=False):
    """Run the Promise-Contract Fidelity checks. Returns (code, lines).

    pitch_text  — the persisted pitch-copy corpus (apodictic.pitch_copy.v1 blocks).
    report_text — the findings / report corpus (apodictic.finding.v1 F-PCF blocks + report prose).
    (For a single combined file the two are the same text; resolution passes them in.)
    """
    lines, errs, warns = [], [], []
    pitch_items = parse_pitch(pitch_text)
    findings = parse_findings(report_text)

    if not pitch_items and not findings:
        return 0, ["promise-contract: no pitch_copy blocks or F-PCF findings found — nothing to check"]

    # ---- pitch copy validity (feeds P2) ----
    for _obj, schema_errs, _idx in pitch_items:
        for e in schema_errs:
            errs.append("P2 invalid pitch copy: %s" % e)
    valid_pitch = [obj for obj, schema_errs, _idx in pitch_items
                   if obj is not None and not schema_errs]
    copy_types = {obj.get("copy_type") for obj in valid_pitch}
    # The verbatim corpus W1 checks the report's quoted blocks against.
    persisted_text = "\n".join(obj.get("text") or "" for obj in valid_pitch)

    # ---- finding validity (feeds P1/P3) ----
    for _obj, schema_errs, _idx in findings:
        for e in schema_errs:
            errs.append("P1 invalid finding: %s" % e)
    valid_findings = [obj for obj, schema_errs, _idx in findings
                      if obj is not None and not schema_errs]

    # ---- P2 — an apodictic.pitch_copy.v1 input exists and every doc declares a valid copy_type ----
    # (Schema validity already covers copy_type membership; P2 also requires the input to EXIST when
    # there are PCF findings to govern — a finding with no persisted copy is ungovernable.)
    if valid_findings and not valid_pitch:
        errs.append("P2 pitch copy not persisted: F-PCF findings exist but no valid "
                    "apodictic.pitch_copy.v1 input was found — PCF2/PCF5 are ungovernable without it")

    # ---- P1 — two-sided gap: each F-PCF finding cites >=1 copy: ref AND >=1 contract:/ms: ref ----
    for obj in valid_findings:
        fid = obj.get("id")
        refs = obj.get("evidence_refs") or []
        has_copy = False           # a well-formed copy: ref that links to PERSISTED copy
        saw_copy_ref = False       # any well-formed copy: ref (incl. one naming an absent copy_type)
        has_contract_or_ms = False
        for r in refs:
            kind, ct = _ref_kind(r)
            if kind == "copy":
                saw_copy_ref = True
                # A copy: ref is evidence only when it names a copy_type ACTUALLY persisted; a
                # fabricated `copy:<absent-type>¶n` must not satisfy the two-sided gate with no copy
                # behind it (Codex P1, 2026-06-19). When NO copy is persisted at all, P2 owns that
                # error — don't also dangling-flag every ref here.
                if copy_types and ct not in copy_types:
                    errs.append("P1 dangling copy ref: %s cites %r but no persisted "
                                "apodictic.pitch_copy.v1 document declares copy_type %r — a copy: ref "
                                "must name a span of persisted copy" % (fid, r, ct))
                else:
                    has_copy = True
            elif kind in ("contract", "ms"):
                has_contract_or_ms = True
        if not (has_copy and has_contract_or_ms):
            missing = []
            # a dangling copy ref is already reported above; only call the copy side "missing" when NO
            # copy: ref was cited at all (else the message would contradict the dangling-ref error).
            if not has_copy and not saw_copy_ref:
                missing.append("a copy: ref")
            if not has_contract_or_ms:
                missing.append("a contract:/ms: ref")
            if missing:
                errs.append("P1 one-sided gap: %s is missing %s — a PCF flag is a two-sided gap and "
                            "must cite both the copy side and the contract/manuscript side "
                            "(namespaced refs)" % (fid, " and ".join(missing)))

    # ---- P3 — reveal-leak form gate: a PCF2 finding's copy: ref must not point at a synopsis ----
    for obj in valid_findings:
        if not _is_pcf2(obj):
            continue
        for r in obj.get("evidence_refs") or []:
            kind, ct = _ref_kind(r)
            if kind == "copy" and ct == "synopsis":
                errs.append("P3 reveal-leak miscalibration: %s is a PCF2 (reveal leak) but its copy "
                            "ref %r points at a synopsis — a synopsis discloses by design, so PCF2 "
                            "never fires on one" % (obj.get("id"), r))
                break

    # ---- W1 — drafted-copy leak (the Firewall): a multi-sentence quoted block in the report that is
    # NOT a verbatim substring of the persisted pitch copy is authored replacement copy. Overrides are
    # SNIPPET-keyed (see _drafted_override_snippets): a leak is silenced only by an override whose
    # snippet matches THAT leak — so one override can't blanket-silence the firewall, and an override
    # for absent text silences nothing. Skipped when no pitch is persisted (P2 already fails, and every
    # quote would otherwise "leak" against an empty corpus — spurious noise on top of the P2 error).
    if valid_pitch:
        override_snips = _drafted_override_snippets(report_text)
        for q in _multi_sentence_quotes(report_text):
            if q in persisted_text:
                continue
            if any(s and (s in q or q in s) for s in override_snips):
                continue
            preview = (q[:60] + "…") if len(q) > 60 else q
            warns.append("W1 drafted-copy leak: a multi-sentence quoted block in the report is not a "
                         "verbatim substring of the persisted pitch copy (authored replacement copy "
                         "— the Firewall): \"%s\"" % preview)

    # ---- W2 — market-prediction drift: a PCF finding matching the prohibited phrase set ----
    market_overrides = _overrides(report_text, "market-prediction")
    for obj in valid_findings:
        fid = obj.get("id")
        short = _short(fid)
        blob = "%s %s %s" % (obj.get("mechanism") or "", obj.get("fix_class") or "",
                             obj.get("risk_if_fixed") or "")
        if _MARKET_RE.search(blob) and short not in market_overrides:
            warns.append("W2 market-prediction drift: %s predicts a sales / market outcome (the #14 "
                         "boundary) — severity is fidelity risk, never market outcome; describe the "
                         "promise↔book gap, don't forecast the market" % fid)

    # ---- Report ----
    lines.append("promise-contract: %d pitch doc(s), %d F-PCF finding(s)%s" % (
        len(valid_pitch), len(valid_findings),
        "" if len(valid_pitch) == len(pitch_items) and len(valid_findings) == len(findings)
        else " (%d/%d pitch, %d/%d findings well-formed)"
        % (len(valid_pitch), len(pitch_items), len(valid_findings), len(findings))))
    for obj in valid_pitch:
        lines.append("  %-6s copy_type=%s" % (obj.get("id"), obj.get("copy_type")))
    for obj in valid_findings:
        lines.append("  %-9s severity=%s" % (obj.get("id"), obj.get("severity")))
    if copy_types:
        lines.append("  copy types present: %s" % ", ".join(sorted(t for t in copy_types if t)))
    for e in errs:
        lines.append("  ERROR: %s" % e)
    for w in warns:
        lines.append("  %s: %s" % ("ERROR (--strict)" if strict else "WARN", w))

    if errs or (strict and warns):
        lines.append("promise-contract: FAIL (%d error(s)%s)"
                     % (len(errs), ", %d strict warn(s)" % len(warns) if (strict and warns) else ""))
        return 1, lines
    if warns:
        lines.append("WARN: promise-contract: %d advisory gap(s) — see W1/W2 above" % len(warns))
    else:
        lines.append("promise-contract: PASS (two-sided gap + copy typing + reveal form gate + "
                     "firewall/scope guards)")
    return 0, lines


# ---------------------------------------------------------------- resolution

def _newest(paths):
    return max(paths, key=os.path.getmtime) if paths else None


def resolve(paths):
    """Resolve (pitch_text, report_text) from a run folder or explicit files.

    A run folder: pitch copy = newest *_Pitch_Copy_*.md (newest-wins on the glob); report = the whole
    folder concatenated (so F-PCF findings in a letter/ledger are seen alongside the persisted copy).
    Explicit files: each is read; a file carrying apodictic:pitch_copy contributes to the pitch corpus,
    and every file contributes to the report corpus (a single combined file is both).
    """
    if len(paths) == 1 and os.path.isdir(paths[0]):
        d = paths[0]
        pitch_path = _newest(glob.glob(os.path.join(d, _PITCH_GLOB)))
        pitch_text = _read(pitch_path) if pitch_path else ""
        report_parts = []
        for p in sorted(glob.glob(os.path.join(d, "*.md"))):
            t = _read(p)
            if t is not None:
                report_parts.append(t)
        return (pitch_text or ""), "\n".join(report_parts)
    pitch_parts, report_parts, found = [], [], False
    for p in paths:
        t = _read(p)
        if t is None:
            continue
        found = True
        report_parts.append(t)
        if _has_block(t, "pitch_copy"):
            pitch_parts.append(t)
    if not found:
        return None, None
    return "\n".join(pitch_parts), "\n".join(report_parts)


def run(paths, strict=False):
    pitch_text, report_text = resolve(paths)
    if pitch_text is None and report_text is None:
        return 2, ["promise-contract: no readable artifact found (need a run folder, a "
                   "*_Pitch_Copy_*.md, or files with apodictic:pitch_copy / F-PCF finding blocks)"]
    return check(pitch_text, report_text, strict=strict)


# ---------------------------------------------------------------- self-test

def run_self_test():
    import json as _j
    rc = {"v": 0}

    def chk(name, cond):
        print("  %s: %s" % (name, "OK" if cond else "FAIL"))
        if not cond:
            rc["v"] = 1

    def pitch(pid="PC-01", ctype="query", text="A grieving cartographer maps a city that keeps "
              "redrawing itself."):
        obj = {"schema": _PITCH_SCHEMA_ID, "id": pid, "copy_type": ctype, "text": text}
        return "<!-- apodictic:pitch_copy\n%s\n-->" % _j.dumps(obj)

    def finding(fid="F-PCF-01", mech="PCF1 emphasis distortion: the query leads with a minor subplot",
                refs=None, sev="Should-Fix", fix="bring the copy back to the kept promise",
                risk="the lead reframes the book", conf="HIGH"):
        if refs is None:
            refs = ["copy:query¶1", "contract:CONTROLLING IDEA"]
        obj = {"schema": _FINDING_SCHEMA_ID, "id": fid, "mechanism": mech, "severity": sev,
               "confidence": conf, "evidence_refs": refs, "fix_class": fix, "risk_if_fixed": risk}
        return "<!-- apodictic:finding\n%s\n-->" % _j.dumps(obj)

    def C(pitch_text, report_text=None, strict=False):
        return check(pitch_text, pitch_text if report_text is None else report_text, strict=strict)

    # clean: one typed pitch + one two-sided PCF finding
    chk("clean_basic", C(pitch() + "\n" + finding())[0] == 0)

    # P1 — one-sided gap (copy-only) => ERROR; (contract-only) => ERROR; both sides => clean
    chk("p1_copy_only_fails",
        C(pitch() + "\n" + finding(refs=["copy:query¶1"]))[0] == 1)
    chk("p1_contract_only_fails",
        C(pitch() + "\n" + finding(refs=["contract:READER PROMISE"]))[0] == 1)
    chk("p1_ms_satisfies_second_side",
        C(pitch() + "\n" + finding(refs=["copy:query¶2", "ms:Ch 9"]))[0] == 0)
    # stray whitespace (leading space; space after the colon) must not drop a real two-sided ref
    chk("p1_whitespace_ref_ok",
        C(pitch() + "\n" + finding(refs=[" copy:query¶1", "contract: CONTROLLING IDEA"]))[0] == 0)
    code, ls = C(pitch() + "\n" + finding(refs=["copy:query¶1"]))
    chk("p1_message", any("P1 one-sided gap" in ln for ln in ls))

    # P1 — schema-invalid finding (empty refs, bad id) is an ERROR
    chk("p1_empty_refs_fails", C(pitch() + "\n" + finding(refs=[]))[0] == 1)
    chk("p1_bad_id_fails", C(pitch() + "\n" + finding(fid="F-PCF-1"))[0] == 1)
    # P1 — a ref with the right prefix but an EMPTY target (bare `contract:`, `ms:`) names no side and
    # must NOT satisfy two-sidedness (Codex P1) — this finding is then one-sided -> ERROR.
    chk("p1_empty_target_contract_fails",
        C(pitch() + "\n" + finding(refs=["copy:query¶1", "contract:"]))[0] == 1)
    chk("p1_empty_target_ms_fails",
        C(pitch() + "\n" + finding(refs=["copy:query¶1", "ms:   "]))[0] == 1)
    # P1 — a copy: ref must carry the FULL grammar (a ¶<n> locus) AND name a PERSISTED copy_type. A
    # locus-less `copy:query`, a malformed `copy:query-does-not-exist` (no ¶), or a well-formed ref
    # naming an absent copy_type is NO evidence and must not satisfy the two-sided gate even when a
    # contract:/ms: ref is present (Codex P1, 2026-06-19 — the copy-side half of the gap).
    chk("p1_copy_ref_without_locus_fails",
        C(pitch() + "\n" + finding(refs=["copy:query", "contract:CONTROLLING IDEA"]))[0] == 1)
    chk("p1_copy_ref_malformed_no_locus_fails",
        C(pitch() + "\n" + finding(refs=["copy:query-does-not-exist", "contract:READER PROMISE"]))[0] == 1)
    code, ls = C(pitch() + "\n" + finding(refs=["copy:synopsis¶2", "contract:CONTROLLING IDEA"]))
    chk("p1_copy_ref_absent_copytype_fails", code == 1)
    chk("p1_dangling_copy_ref_message", any("P1 dangling copy ref" in ln for ln in ls))

    # P2 — a finding with no persisted pitch copy => ERROR; pitch present => clean
    code, ls = C(finding())  # finding alone, no pitch_copy block
    chk("p2_no_copy_fails", code == 1 and any("P2 pitch copy not persisted" in ln for ln in ls))
    chk("p2_copy_present_ok", C(pitch() + "\n" + finding())[0] == 0)
    # P2 — invalid copy_type (bad enum) fails schema
    chk("p2_bad_copy_type_fails", C(pitch(ctype="tagline") + "\n" + finding())[0] == 1)
    chk("p2_bad_pitch_id_fails", C(pitch(pid="PC-1") + "\n" + finding())[0] == 1)
    # P2 — empty / whitespace-only pitch text is not real copy and must fail the schema (Codex P1)
    chk("p2_empty_text_fails", C(pitch(text="") + "\n" + finding())[0] == 1)
    chk("p2_whitespace_text_fails", C(pitch(text="   ") + "\n" + finding())[0] == 1)

    # P3 — a PCF2 whose copy ref is a synopsis => ERROR; the same PCF2 against a query => clean;
    #      a NON-PCF2 finding citing a synopsis (the disclosing-synopsis negative) => clean.
    pcf2_syn = finding(fid="F-PCF-02", mech="PCF2 reveal leak: discloses the ending",
                       refs=["copy:synopsis¶3", "contract:ENDING TYPE"])
    pcf2_query = finding(fid="F-PCF-02", mech="PCF2 reveal leak: the blurb discloses the twist",
                         refs=["copy:query¶3", "contract:ENDING TYPE"])
    chk("p3_pcf2_on_synopsis_fails",
        C(pitch(ctype="synopsis") + "\n" + pcf2_syn)[0] == 1)
    code, ls = C(pitch(ctype="synopsis") + "\n" + pcf2_syn)
    chk("p3_message", any("P3 reveal-leak miscalibration" in ln for ln in ls))
    chk("p3_pcf2_on_query_ok",
        C(pitch(ctype="query") + "\n" + pcf2_query)[0] == 0)
    # the P3 NEGATIVE assertion: a disclosing synopsis with a NON-PCF2 finding must NOT raise P3
    non_pcf2_syn = finding(fid="F-PCF-03", mech="PCF4 under-sell: the synopsis omits the kept promise",
                           refs=["copy:synopsis¶1", "contract:CONTROLLING IDEA"])
    chk("p3_disclosing_synopsis_no_false_positive",
        C(pitch(ctype="synopsis") + "\n" + non_pcf2_syn)[0] == 0)
    # a NON-PCF2 finding that merely MENTIONS "PCF2" in prose (and cites a synopsis) must NOT trip P3
    sibling = finding(fid="F-PCF-05",
                      mech="PCF1 emphasis distortion (distinct from PCF2 reveal leak): the synopsis "
                           "leads with a subplot the book backgrounds",
                      refs=["copy:synopsis¶1", "contract:READER PROMISE"])
    chk("p3_sibling_mention_no_false_positive",
        C(pitch(ctype="synopsis") + "\n" + sibling)[0] == 0)

    # W1 — a multi-sentence quoted block NOT in the persisted copy => advisory; ERROR --strict; a
    #      multi-sentence quote that IS a verbatim substring => clean; override silences.
    persisted = "A grieving cartographer maps a city that keeps redrawing itself. She learns the map is her own grief."
    report_leak = (pitch(text=persisted) + "\n" + finding()
                   + "\n\nConsider this instead: \"A bold thriller about a cartographer. "
                   + "Everyone will love it.\"\n")
    code, ls = C(report_leak)
    chk("w1_leak_advisory", code == 0 and any("W1 drafted-copy leak" in ln for ln in ls))
    chk("w1_leak_strict_fails", C(report_leak, strict=True)[0] == 1)
    # quoting the author's OWN copy verbatim (a multi-sentence substring of persisted) is clean
    report_quote = (pitch(text=persisted) + "\n" + finding()
                    + "\n\nThe query says: \"" + persisted + "\"\n")
    chk("w1_verbatim_quote_clean",
        not any("W1" in ln for ln in C(report_quote)[1]))
    # a single-sentence quoted phrase is not a multi-sentence block => no W1
    report_single = (pitch(text=persisted) + "\n" + finding()
                     + "\n\nThe phrase \"a bold thriller\" overstates the genre.\n")
    chk("w1_single_phrase_clean",
        not any("W1" in ln for ln in C(report_single)[1]))
    # a snippet-keyed override silences ONLY the leak it matches; a non-matching snippet silences none
    ov = "<!-- override: drafted-copy A bold thriller about a cartographer — author drafted this herself -->\n"
    chk("w1_override_snippet_silences",
        not any("W1" in ln for ln in C(ov + report_leak)[1]))
    ov_nomatch = "<!-- override: drafted-copy something unrelated entirely — n/a -->\n"
    chk("w1_override_nonmatching_no_silence",
        any("W1" in ln for ln in C(ov_nomatch + report_leak)[1]))

    # W2 — a PCF finding predicting a market outcome => advisory; ERROR --strict; override silences;
    #      a fidelity-only finding is clean.
    market = finding(mech="PCF1 emphasis: the query leads with the subplot; agents will pass on this",
                     refs=["copy:query¶1", "contract:READER PROMISE"])
    code, ls = C(pitch() + "\n" + market)
    chk("w2_market_advisory", code == 0 and any("W2 market-prediction drift" in ln for ln in ls))
    chk("w2_market_strict_fails", C(pitch() + "\n" + market, strict=True)[0] == 1)
    chk("w2_each_phrase_fires", all(
        any("W2" in ln for ln in C(pitch() + "\n" + finding(
            mech="PCF3 over-promise: %s" % phrase,
            refs=["copy:query¶1", "ms:Ch 1"]))[1])
        for phrase in ("won't sell", "no market for this", "unmarketable", "won't find an audience")))
    ov2 = "<!-- override: market-prediction PCF-01 — quoting the author's own Pass-11 prediction -->\n"
    chk("w2_override", not any("W2" in ln for ln in C(ov2 + pitch() + "\n" + market)[1]))
    chk("w2_fidelity_only_clean", not any("W2" in ln for ln in C(pitch() + "\n" + finding())[1]))

    # no blocks => no-op
    chk("no_blocks_noop", C("# Notes\nnothing structured\n")[0] == 0)

    # run-folder + explicit-file + missing-artifact resolution
    import tempfile
    import shutil
    d = tempfile.mkdtemp()
    try:
        pc = os.path.join(d, "Proj_Pitch_Copy_run.md")
        with open(pc, "w", encoding="utf-8", newline="") as fh:
            fh.write("# Pitch Copy\n" + pitch() + "\n")
        ltr = os.path.join(d, "Proj_Editorial_Letter_run.md")
        with open(ltr, "w", encoding="utf-8", newline="") as fh:
            fh.write("# Promise-Contract Findings\n" + finding() + "\n")
        chk("run_folder_resolution", run([d])[0] == 0)
        chk("explicit_files_resolution", run([pc, ltr])[0] == 0)
        chk("missing_artifact_usage", run([os.path.join(d, "nope.md")])[0] == 2)
        # run-folder: pitch present but P1 one-sided finding still fails
        bad = os.path.join(d, "Proj_Bad_Letter_run.md")
        with open(bad, "w", encoding="utf-8", newline="") as fh:
            fh.write(finding(fid="F-PCF-09", refs=["copy:query¶1"]) + "\n")
        chk("run_folder_p1_fails", run([d])[0] == 1)
    finally:
        shutil.rmtree(d, ignore_errors=True)

    # regression: a non-dict finding payload must not crash parse_findings (2026-06-20 sweep)
    chk("crash_nondict_finding", C(pitch() + "\n" + '<!-- apodictic:finding\n[1,2,3]\n-->')[0] == 1)
    print("Self-test: PASS" if rc["v"] == 0 else "Self-test: FAIL")
    return rc["v"]


def main(argv):
    if "--self-test" in argv:
        return run_self_test()
    args = [a for a in argv[1:] if a != "promise-contract"]
    strict = "--strict" in args
    paths = [a for a in args if not a.startswith("--")]
    if not paths:
        print("Usage: promise_contract.py promise-contract <run_folder|files...> [--strict] | --self-test")
        return 2
    code, lines = run(paths, strict=strict)
    for ln in lines:
        print(ln)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
