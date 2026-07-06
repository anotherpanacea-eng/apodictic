#!/usr/bin/env python3
"""position-pair-register — consumer-side firewall gates for the Position-Pair Register
(stance-consistency PR 2; SPEC setec-scratch/apo-stance-consistency/SPEC.md, contract v4+v5).

`validate.sh position-pair-register <artifact.md> <envelope.json> <manuscript> [--strict]`
(or `--self-test`) shells out here.

The Position-Pair Register is APODICTIC's consumer of SETEC's `position_pair_register`
surface. That surface reads ONE nonfiction argument-shaped work and emits a register of passage
PAIRS that address the SAME question Q — each pair carrying a neutral interrogative `question` and
both passages' verbatim loci (`{doc, start_char, end_char, quote}`), in DOCUMENT ORDER. It asserts
NO relation between the passages; the HUMAN reads both and owns 100% of the conflict call. APODICTIC
renders the register to a markdown artifact and presents it — adding no severity, disposition, or
finding of its own. This validator carries the posture MECHANICALLY (not rhetorically): it is the
"claim-surface-asserts-it" enforcement of every claim the consumer's reference doc makes about the
register artifact.

Five checks, each degrading cleanly (an unreadable input fails CLOSED with a named error, never a
false PASS):

  Q1 no-relation register  A two-layer recursive banned-KEY walk over the parsed envelope
                           (walk shape from PR #298's `test_envelope_carries_no_verdict_keys_recursive`
                           in setec-voiceprint — the shape, NOT its key list; the stance set is
                           net-new). (i) RELATION keys — never legitimate ANYWHERE in the envelope
                           (whole-envelope walk): a relation key means the model asserted the
                           opposition the human is supposed to own. (ii) GENERIC verdict keys — banned
                           only inside the `results.pairs` SUBTREE (payload-scoped): a whole-envelope
                           ban would false-ERROR on framework-standard metadata (calibration blocks /
                           judge provenance carry `label`/`score` legitimately). KEYS ONLY — the
                           claim_license VALUES legitimately CONTAIN relation words (the F10 refusals
                           say "does NOT license that the passages are in conflict"), so scanning
                           values would guarantee a false ERROR.

  Q2 verbatim (drift)      Re-verify every `quote` against the manuscript THE CONSUMER holds (a drift
                           catch — the producer quoted the manuscript IT saw; the consumer must confirm
                           against ITS copy). Match = exact substring AFTER the F1 punctuation-fold on
                           BOTH sides (NFC → typographic quotes to straight → all Unicode dashes to '-'
                           → '…' to '...' → Zs-category spaces to U+0020 → newline to space →
                           whitespace-run collapse). A failed match DROPS the pair with an INSPECTABLE
                           log line (the offending quote verbatim + its claimed locus, so a human can
                           see whether the drop hid a real pair) and increments the counted disclosure
                           `pairs_dropped_quote_mismatch`; >=1 drop also WARNs. A fabricated or
                           paraphrased quote therefore can never reach the human as evidence.

  A3 X-gate (Firewall)     The register artifact must not leak editorial severity
                           (`Must/Should/Could-Fix`) or masquerade as a finding list (no
                           `apodictic:finding` block). The register never carries severity or findings
                           — `disposition: pre_flag` posture. Same content_advisory A3 firewall. ERROR.

  F5 presentation-prose    The consumer's OWN human-facing framing text in the artifact must itself
                           carry no relation VOCABULARY (a case-folded substring scan, the F4 stem set
                           incl. the v5 stems). The firewall's terminus text cannot be the one
                           unscanned channel. The scan EXCLUDES the verbatim-quote spans (blockquote
                           lines beginning `>`): the quotes are the AUTHOR's text and may legitimately
                           contain these words — the gate targets the CONSUMER's framing, not the
                           evidence. Structural exemption (a `>`-prefixed line), never a per-token
                           allowlist. ERROR.

  Order (document order)   The artifact presents pairs in the SAME order the envelope does. Any
                           re-ranking is an ERROR — truncation/selection by anything but document order
                           is a ranking channel the posture forbids (the producer already enforces
                           this at emit; the consumer re-checks that RENDERING preserved it).

Inputs are three explicit file args (artifact.md, envelope.json, manuscript) — no run-folder
resolution, so the absolute/traversal/symlink containment triple does not apply here (there is no
join of a resolved run-folder against a cited bare filename). If a run-folder mode is ever added, that
triple applies, per the results_guide.py precedent.

  position_pair_gates.py position-pair-register <artifact.md> <envelope.json> <manuscript> [--strict]
  position_pair_gates.py --self-test

Exit: 0 clean / WARN-only, 1 ERROR (or WARN under --strict), 2 usage.
"""
import json
import re
import sys
import unicodedata

try:
    import apodictic_artifacts as art
except ImportError:
    art = None

from severity_vocab import SEVERITY_TOKEN_RE  # SSoT: the editorial Must/Should/Could-Fix leak token

# ---------------------------------------------------------------- A3 / X-gate idioms (content_advisory)
# A3-style editorial-severity leak guard — the shared severity_vocab SSoT (M8); the local alias keeps
# the A3 call sites byte-identical. The register is a relation-free pointer, not a defect list: a
# Must/Should/Could-Fix token means it started diagnosing.
_SEVERITY_RE = SEVERITY_TOKEN_RE

# ---------------------------------------------------------------- Q1 the banned-key frozensets (F3)
# (i) RELATION keys — never legitimate ANYWHERE in the envelope (whole-envelope walk). Case-folded
#     SUBSTRING per key (so `stance_delta`, `has_conflict`, `is_inconsistent` are all caught). The
#     claim_license VALUES legitimately CONTAIN these words; the walk bans KEYS, never values.
_BANNED_RELATION_KEYS = frozenset({
    "contradiction", "contradicts", "opposes", "opposition", "conflict",
    "conflicting", "tension", "stance", "stance_delta", "polarity",
    "agreement", "disagreement", "inconsistent", "inconsistency",
})
# (ii) GENERIC verdict keys — banned ONLY inside the `results.pairs` SUBTREE (payload-scoped). A
#      whole-envelope ban here would false-ERROR on framework-standard metadata (calibration blocks /
#      judge provenance carry `label`/`score` legitimately). Exact-key match, case-folded (a substring
#      rule would snare legitimate pair keys like `end_char` on "…"; the generic tokens are whole keys).
_BANNED_VERDICT_KEYS = frozenset({
    "verdict", "label", "score", "decision", "prediction",
    "classification", "relation",
})

# ---------------------------------------------------------------- F5 the relation-VOCAB scan set (F4 + v5 stems)
# A case-folded SUBSTRING scan over the consumer's framing prose (blockquote-evidence lines excluded).
# Substring (not word-boundary) is deliberate — matches the producer's Q-gate guard; the known
# conservative false-refusals ("counterargument", "encounter", "conflict of interest") are accepted by
# design (the framing text is short and author-controlled, so an honest neutral framing avoids them).
_RELATION_VOCAB = (
    # F4 base
    "tension", "contradict", "conflict", "inconsisten", "incompatib",
    "at odds", "versus", " vs ", "flip-flop", "disagree",
    # v5 stems
    "oppos", "revers", "undercut", "undermin", "counter", "repudiat",
    "recant", "backtrack", "diverg", "discrepanc", "at variance",
    "square with",
)


def _read(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except (OSError, UnicodeDecodeError):
        return None


def _read_json(path):
    """Return (obj, err). A missing/unreadable/invalid-JSON envelope yields (None, reason) so the
    caller fails CLOSED with a named error (never a false PASS)."""
    text = _read(path)
    if text is None:
        return None, "unreadable or not UTF-8"
    try:
        return json.loads(text), None
    except ValueError as exc:  # json.JSONDecodeError is a ValueError subclass
        return None, "invalid JSON — %s" % exc


def _has_block(text, btype):
    """True if `text` carries a real apodictic:<btype> block (a parsed carrier, not a prose mention).

    Classifying on parsed blocks — not a raw substring — keeps a file that merely *names* the marker
    in prose from being misrouted (the 2026-06-20 resolver-hardening sweep). Gated by
    validate.sh validator-conventions (M2)."""
    if art is None:
        return ("apodictic:%s" % btype) in (text or "")
    return any(bt == btype for bt, _o, _e in art.parse_blocks(text or ""))


# ---------------------------------------------------------------- Q1 the recursive key walk

def _walk_keys(obj, banned, path="", hits=None):
    """Recursive key walk (shape from #298's `test_envelope_carries_no_verdict_keys_recursive`): at
    every dict depth, case-folded-substring-check each KEY against `banned`; recurse dict values and
    list/tuple items. Appends "<banned> at <path>" strings to `hits` (never raises — the consumer
    REPORTS, it does not crash on a hostile envelope)."""
    if hits is None:
        hits = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            here = ("%s.%s" % (path, k)) if path else str(k)
            low = str(k).casefold()
            for b in banned:
                if b in low:
                    hits.append("%s (key %r at %r)" % (b, str(k), here))
            _walk_keys(v, banned, here, hits)
    elif isinstance(obj, (list, tuple)):
        for i, item in enumerate(obj):
            _walk_keys(item, banned, "%s[%d]" % (path, i), hits)
    return hits


def _walk_exact_keys(obj, banned, path="", hits=None):
    """Like `_walk_keys` but the KEY must EQUAL a banned token (case-folded), not merely contain it —
    for the generic verdict tokens, which are whole keys (`label`, `score`, …). A substring rule would
    snare legitimate pair keys (e.g. nothing here today, but `end_char`/etc. must never trip on a
    generic token), so scope the generic set to exact keys."""
    if hits is None:
        hits = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            here = ("%s.%s" % (path, k)) if path else str(k)
            if str(k).casefold() in banned:
                hits.append("%s (key %r at %r)" % (str(k).casefold(), str(k), here))
            _walk_exact_keys(v, banned, here, hits)
    elif isinstance(obj, (list, tuple)):
        for i, item in enumerate(obj):
            _walk_exact_keys(item, banned, "%s[%d]" % (path, i), hits)
    return hits


# ---------------------------------------------------------------- Q2 the F1 punctuation-fold

# Typographic / curly quote glyphs -> straight. (Left/right double + low/high double -> ";
#  left/right single + single low + prime-ish -> '.)
_QUOTE_MAP = {
    "“": '"', "”": '"', "„": '"', "‟": '"', "«": '"', "»": '"',
    "‘": "'", "’": "'", "‚": "'", "‛": "'", "‹": "'", "›": "'",
}
# All Unicode dashes (en / em / horizontal bar / figure / minus / non-breaking hyphen / hyphen point)
# -> ASCII '-'.
_DASH_CHARS = "‐‑‒–—―−⁃﹘﹣－"


def _fold(text):
    """The F1 canonicalization, applied identically to BOTH the quote and the manuscript before the
    substring match: NFC -> typographic quotes to straight -> all Unicode dashes to '-' -> '…' to
    '...' -> every Zs-category space (NBSP / thin / …) to U+0020 -> newline to space -> whitespace-run
    collapse. These are exactly the glyph classes an LLM rewrites when quoting; without the fold, a
    faithful quote silently drops (a false negative) and a one-glyph perturbation becomes a
    pair-suppression vector."""
    if text is None:
        return ""
    text = unicodedata.normalize("NFC", text)
    out = []
    for ch in text:
        if ch in _QUOTE_MAP:
            out.append(_QUOTE_MAP[ch])
        elif ch in _DASH_CHARS:
            out.append("-")
        elif ch == "…":  # horizontal ellipsis
            out.append("...")
        elif ch == "\n":
            out.append(" ")
        elif unicodedata.category(ch) == "Zs":  # any Unicode space separator -> plain space
            out.append(" ")
        else:
            out.append(ch)
    folded = "".join(out)
    # Collapse any whitespace run (spaces + surviving tabs / other control whitespace) to one space.
    return re.sub(r"\s+", " ", folded).strip()


# ---------------------------------------------------------------- the arm

def _envelope_pairs(envelope):
    """The `results.pairs` list (or [] if absent/mis-shaped). Never raises."""
    if not isinstance(envelope, dict):
        return []
    results = envelope.get("results")
    if not isinstance(results, dict):
        return []
    pairs = results.get("pairs")
    return pairs if isinstance(pairs, list) else []


def _artifact_question_list(artifact_text):
    """The ordered list of `### <n>. Q: <question>` headings the register renderer writes, for the
    order check. Matches the producer's render_markdown shape (`### {i}. Q: {question}`)."""
    out = []
    if not artifact_text:
        return out
    for m in re.finditer(r"^###\s+\d+\.\s+Q:\s+(.+?)\s*$", artifact_text, re.MULTILINE):
        q = m.group(1).strip()
        if q:
            out.append(q)
    return out


def check(artifact_text, envelope, manuscript_text, envelope_err=None,
          manuscript_err=None, strict=False):
    """Run the position-pair-register gate arm. Returns (code, lines).

    artifact_text   = the rendered register markdown (None -> fail-closed).
    envelope        = the parsed envelope dict (None + envelope_err -> fail-closed).
    manuscript_text = the manuscript the consumer holds (None + manuscript_err -> fail-closed).
    """
    lines, errs, warns = [], [], []

    # Fail-closed on any unreadable input (a named error, never a false PASS).
    if artifact_text is None:
        return 1, ["position-pair-register: ERROR: register artifact unreadable"]
    if envelope is None:
        return 1, ["position-pair-register: ERROR: envelope %s" % (envelope_err or "unreadable")]
    if manuscript_text is None:
        return 1, ["position-pair-register: ERROR: manuscript %s" % (manuscript_err or "unreadable")]

    pairs = _envelope_pairs(envelope)

    # Q1 — no-relation register: two-layer banned-KEY walk over the envelope.
    relation_hits = _walk_keys(envelope, _BANNED_RELATION_KEYS)
    for h in relation_hits:
        errs.append("Q1 relation key: %s — the register asserts NO relation between passages "
                    "(the human owns the conflict call); a relation key must never appear in the "
                    "envelope" % h)
    results = envelope.get("results") if isinstance(envelope, dict) else None
    if isinstance(results, dict):
        pairs_subtree = results.get("pairs")
        if pairs_subtree is not None:
            verdict_hits = _walk_exact_keys(pairs_subtree, _BANNED_VERDICT_KEYS, path="results.pairs")
            for h in verdict_hits:
                errs.append("Q1 verdict key: %s — a generic verdict key inside results.pairs smuggles "
                            "a judgment the register must not carry" % h)

    # Q2 — verbatim (drift) re-check with the F1 fold. A failed match DROPS the pair with an
    # INSPECTABLE log line + counted disclosure; >=1 drop WARNs. A DROP IS A DISCLOSURE, NOT AN ERROR:
    # it clears (code 0) by default and only FAILs under --strict — a suppressed pair (from a
    # fabricated/paraphrased quote or manuscript drift) is surfaced for human inspection, never a hard
    # gate failure. (A MALFORMED pair — missing locus / empty quote / non-object — IS an error: it is a
    # broken envelope, not a legitimately-quoted-but-unmatched pair.)
    folded_manuscript = _fold(manuscript_text)
    pairs_dropped_quote_mismatch = 0
    quote_mismatch_logs = []
    for i, p in enumerate(pairs, 1):
        if not isinstance(p, dict):
            errs.append("Q2 pair shape: results.pairs[%d] is not an object" % (i - 1))
            continue
        for side in ("a", "b"):
            loc = p.get(side)
            if not isinstance(loc, dict):
                errs.append("Q2 pair shape: pair %d side %r has no locus object" % (i, side))
                continue
            quote = loc.get("quote")
            if not isinstance(quote, str) or not quote.strip():
                errs.append("Q2 empty quote: pair %d side %r carries no quote" % (i, side))
                continue
            if _fold(quote) not in folded_manuscript:
                pairs_dropped_quote_mismatch += 1
                # INSPECTABLE: the offending quote verbatim + its claimed locus, so a human can check
                # whether the drop hid a real pair (F1's inspectable-drop requirement). Reported in the
                # WARN tier (a drop is a disclosure), not the ERROR tier.
                loc_desc = "doc=%r start_char=%r end_char=%r" % (
                    loc.get("doc"), loc.get("start_char"), loc.get("end_char"))
                quote_mismatch_logs.append(
                    "Q2 quote mismatch: pair %d side %r — quote is NOT a verbatim substring of the "
                    "manuscript (pair DROPPED). Claimed locus: %s. Offending quote: %r"
                    % (i, side, loc_desc, quote))
    if pairs_dropped_quote_mismatch:
        warns.append("pairs_dropped_quote_mismatch=%d — at least one quote failed the verbatim "
                     "re-check against the manuscript the consumer holds (a fabricated/paraphrased "
                     "quote, or manuscript drift); the offending quote(s) + loci are logged below"
                     % pairs_dropped_quote_mismatch)
        warns.extend(quote_mismatch_logs)

    # A3 / X-gate — the register artifact must not leak editorial severity or a finding block.
    if _SEVERITY_RE.search(artifact_text):
        errs.append("A3 severity leak: the register carries a Must/Should/Could-Fix token — it points "
                    "at passages, it never diagnoses (no severity, disposition: pre_flag)")
    if _has_block(artifact_text, "finding"):
        errs.append("A3 finding block: the register carries an apodictic:finding block — a relation-"
                    "free pointer must not masquerade as an editorial finding")

    # F5 — presentation-prose gate: the consumer's framing text must carry no relation vocabulary.
    # A `>`-blockquote line is exempt ONLY if its folded text is a verbatim substring of the folded
    # manuscript — i.e. it really is the author's quoted evidence. A `>` line that is NOT verbatim
    # manuscript text is FRAMING DRESSED AS EVIDENCE and falls back into the scan (else a fabricated
    # "> these passages plainly contradict each other" line would be both F5-exempt and Q2-unverified
    # — the review-panel P1). Empty `>` separators are harmless and stay exempt.
    framing_parts = []
    for ln in artifact_text.split("\n"):
        stripped = ln.lstrip()
        if stripped.startswith(">"):
            quoted_text = stripped.lstrip(">").strip()
            # The canonical template labels evidence lines `> A: <quote>` / `> B: <quote>` —
            # strip that side label before the verbatim match (the label is renderer scaffolding,
            # not manuscript text).
            label = re.match(r"^[AB]:\s*(.*)$", quoted_text)
            candidate = label.group(1) if label else quoted_text
            if not candidate or _fold(candidate) in folded_manuscript:
                continue  # a real (verbatim) evidence line, or an empty separator — exempt
            # not manuscript text: scan it as framing (and say so if it trips)
        framing_parts.append(ln)
    framing = " ".join(framing_parts).casefold()
    for vocab in _RELATION_VOCAB:
        if vocab in framing:
            errs.append("F5 presentation prose: the register's framing text carries the relation "
                        "term %r — the consumer's terminus prose must assert NO relation. (Only "
                        "`>`-blockquote lines whose text is verbatim manuscript evidence are exempt; "
                        "a non-verbatim blockquote line is framing dressed as evidence and is "
                        "scanned.)" % vocab.strip())

    # Order — the artifact presents pairs in envelope (document) order. When the artifact carries
    # NO parseable `### <n>. Q:` headings but the envelope has pairs, the order is UNVERIFIABLE —
    # that is a WARN (surfaced, --strict-escalated), never a silent skip (the silent-skip was the
    # review panel's P2: the document-order guarantee held only when the renderer matched one regex).
    env_qs = [p.get("question") for p in pairs
              if isinstance(p, dict) and isinstance(p.get("question"), str)]
    art_qs = _artifact_question_list(artifact_text)
    if env_qs and not art_qs:
        warns.append("Order unverifiable: the artifact carries no parseable `### <n>. Q: <question>` "
                     "headings, so document order cannot be checked against the envelope — render "
                     "with the canonical heading form (see position-pair-register.md)")
    elif art_qs and env_qs and art_qs != env_qs:
        errs.append("Order: the register artifact presents pairs in a DIFFERENT order than the "
                    "envelope (document order) — re-ranking is a judgment channel the posture forbids. "
                    "Artifact Q order: %r; envelope Q order: %r" % (art_qs, env_qs))

    # Report
    lines.append("position-pair-register: %d pair(s), %d quote-mismatch drop(s)"
                 % (len(pairs), pairs_dropped_quote_mismatch))
    for e in errs:
        lines.append("  ERROR: %s" % e)
    for w in warns:
        lines.append("  %s: %s" % ("ERROR (--strict)" if strict else "WARN", w))

    if errs or (strict and warns):
        lines.append("position-pair-register: FAIL (%d error(s)%s)"
                     % (len(errs), ", %d strict warn(s)" % len(warns) if (strict and warns) else ""))
        return 1, lines
    if warns:
        lines.append("WARN: position-pair-register: %d disclosure(s)" % len(warns))
    else:
        lines.append("position-pair-register: PASS (no-relation register + verbatim + firewall "
                     "+ framing prose + document order)")
    return 0, lines


# ---------------------------------------------------------------- artifact resolution

def run(paths, strict=False):
    """paths = [artifact.md, envelope.json, manuscript]. Explicit file args only (no run-folder
    resolution — the register is a three-file consumer input)."""
    if len(paths) < 3:
        return 2, ["position-pair-register: need three files — <artifact.md> <envelope.json> "
                   "<manuscript>"]
    artifact_path, envelope_path, manuscript_path = paths[0], paths[1], paths[2]
    artifact_text = _read(artifact_path)
    envelope, envelope_err = _read_json(envelope_path)
    manuscript_text = _read(manuscript_path)
    manuscript_err = None if manuscript_text is not None else "unreadable or not UTF-8"
    return check(artifact_text, envelope, manuscript_text,
                 envelope_err=envelope_err, manuscript_err=manuscript_err, strict=strict)


# ---------------------------------------------------------------- self-test

def run_self_test():
    import os
    import shutil
    import tempfile
    rc = {"v": 0}
    made = []

    def check_case(name, cond):
        print("  %s: %s" % (name, "OK" if cond else "FAIL"))
        if not cond:
            rc["v"] = 1

    # A manuscript whose passages the pairs quote verbatim. The two Q-pairs each quote a substring.
    MANUSCRIPT = (
        "A well-designed carbon price is the most efficient lever available to a modern state. "
        "Later in the brief: Pricing carbon directly is the single most effective policy a "
        "government can adopt. On transit funding: Dedicated fuel levies should underwrite the bulk "
        "of new transit capacity. And elsewhere: General revenue, not user fees, ought to carry the "
        "cost of expanding transit.\n"
    )

    def envelope(pairs, extra_results=None, extra_top=None):
        results = {
            "calibration_status": "uncalibrated",
            "pairs": pairs,
            "pairs_refused_q_gate": 0,
            "pairs_refused_q_gate_reasons": [],
            "pairs_dropped_cap": 0,
            "pairs_dropped_cap_loci": [],
        }
        if extra_results:
            results.update(extra_results)
        env = {
            "schema_version": "1.0",
            "task_surface": "position_pair_register",
            "tool": "position_pair_register",
            "available": True,
            # The claim_license VALUES legitimately contain relation words — Q1 must NOT flag them.
            "claim_license": {
                "task_surface": "position_pair_register",
                "does_not_license": "It does NOT license any claim that the two passages ARE in "
                                    "conflict, contradiction, tension, or opposition.",
            },
            "results": results,
        }
        if extra_top:
            env.update(extra_top)
        return env

    def pair(q, qa, qb):
        return {
            "question": q,
            "a": {"doc": "target", "start_char": 0, "end_char": 0, "quote": qa},
            "b": {"doc": "target", "start_char": 0, "end_char": 0, "quote": qb},
        }

    Q1 = "What is the author's position on carbon pricing?"
    Q2 = "How should new transit capacity be funded?"
    QA_A = "A well-designed carbon price is the most efficient lever available to a modern state."
    QA_B = "Pricing carbon directly is the single most effective policy a government can adopt."
    QB_A = "Dedicated fuel levies should underwrite the bulk of new transit capacity."
    QB_B = "General revenue, not user fees, ought to carry the cost of expanding transit."

    HAPPY_PAIRS = [pair(Q1, QA_A, QA_B), pair(Q2, QB_A, QB_B)]

    NEUTRAL_FRAMING = (
        "_These passages address the same question. Read both — the reading is yours._"
    )

    def artifact(pairs, framing=NEUTRAL_FRAMING, extra="", quote_override=None):
        """Render a register artifact mirroring the producer's shape: `### {i}. Q: {q}` headings and
        the two quotes as `>` blockquote evidence lines."""
        body = ["# Position-Pair Register (same-question passage pairs)", "", framing, "",
                "## Pairs (document order)", ""]
        for i, p in enumerate(pairs, 1):
            aq = quote_override.get((i, "a")) if quote_override else p["a"]["quote"]
            bq = quote_override.get((i, "b")) if quote_override else p["b"]["quote"]
            body += ["### %d. Q: %s" % (i, p["question"]), "",
                     "> A: %s" % aq, "> B: %s" % bq, ""]
        return "\n".join(body) + extra

    # ------- (happy) full happy path -> PASS
    env = envelope(HAPPY_PAIRS)
    code, lines = check(artifact(HAPPY_PAIRS), env, MANUSCRIPT)
    check_case("happy_path_pass", code == 0 and any("PASS" in ln for ln in lines))

    # ------- (5) paraphrased quote -> DROPPED + inspectable log + WARN (default), FAIL under --strict
    para = [pair(Q1, "A carbon price is a very efficient lever for the modern state.", QA_B)]
    env = envelope(para)
    code, lines = check(artifact(para), env, MANUSCRIPT)
    check_case("paraphrase_dropped_warn",
               code == 0 and any("Q2 quote mismatch" in ln for ln in lines)
               and any("WARN" in ln and "pairs_dropped_quote_mismatch=1" in ln for ln in lines))
    # inspectable: the offending quote verbatim appears in the log
    check_case("paraphrase_inspectable_log",
               any("very efficient lever" in ln for ln in lines))
    code_s, lines_s = check(artifact(para), env, MANUSCRIPT, strict=True)
    check_case("paraphrase_strict_fail",
               code_s == 1 and any("FAIL" in ln for ln in lines_s))

    # ------- (7) smart-quote / em-dash / ellipsis / NBSP variants -> MATCH after the F1 fold -> PASS
    # Manuscript span (straight/ASCII); the QUOTE carries curly quotes, an em-dash, an ellipsis glyph,
    # and an NBSP — all folded away so the substring still matches.
    MS_F1 = ('The report is blunt: "the levy is the lever" - it says - and nothing else ... '
             'the rest is commentary.\n')
    q_f1 = ("“the levy is the lever” — it says — and nothing else … "
            "the rest is commentary.")
    f1_pairs = [pair("What does the report conclude about the levy?", q_f1, q_f1)]
    env = envelope(f1_pairs)
    code, lines = check(artifact(f1_pairs), env, MS_F1)
    check_case("f1_fold_matches", code == 0 and any("PASS" in ln for ln in lines))

    # ------- planted Must-Fix token in the artifact -> FAIL
    code, lines = check(artifact(HAPPY_PAIRS, extra="\n\nThis is a Must-Fix issue.\n"),
                        envelope(HAPPY_PAIRS), MANUSCRIPT)
    check_case("planted_must_fix_fail",
               code == 1 and any("A3 severity leak" in ln for ln in lines))

    # ------- planted apodictic:finding block -> FAIL
    fblock = ('\n<!-- apodictic:finding\n{"schema":"apodictic.finding.v1","id":"F-P5-01",'
              '"mechanism":"m","severity":"Must-Fix","confidence":"HIGH","evidence_refs":["c"],'
              '"fix_class":"x","risk_if_fixed":"y"}\n-->\n')
    code, lines = check(artifact(HAPPY_PAIRS, extra=fblock), envelope(HAPPY_PAIRS), MANUSCRIPT)
    check_case("planted_finding_block_fail",
               code == 1 and any("A3 finding block" in ln for ln in lines))

    # ------- injected relation KEY whole-envelope -> FAIL
    env = envelope(HAPPY_PAIRS, extra_top={"tension_summary": "n/a"})
    code, lines = check(artifact(HAPPY_PAIRS), env, MANUSCRIPT)
    check_case("relation_key_whole_envelope_fail",
               code == 1 and any("Q1 relation key" in ln and "tension" in ln for ln in lines))
    # …and a relation key NESTED inside a pair is caught too (whole-envelope walk).
    rp = [pair(Q1, QA_A, QA_B)]
    rp[0]["stance"] = "for"
    code, lines = check(artifact(rp), envelope(rp), MANUSCRIPT)
    check_case("relation_key_in_pair_fail",
               code == 1 and any("Q1 relation key" in ln and "stance" in ln for ln in lines))

    # ------- injected generic verdict key under results.pairs -> FAIL (payload-scoped)
    vp = [pair(Q1, QA_A, QA_B)]
    vp[0]["label"] = "opposing"
    code, lines = check(artifact(vp), envelope(vp), MANUSCRIPT)
    check_case("verdict_key_under_pairs_fail",
               code == 1 and any("Q1 verdict key" in ln and "label" in ln for ln in lines))
    # …but a `label`/`score` OUTSIDE results.pairs (framework metadata) must NOT trip Q1 (scoped).
    env = envelope(HAPPY_PAIRS, extra_top={"judge": {"label": "calib-block", "score": 0.9}})
    code, lines = check(artifact(HAPPY_PAIRS), env, MANUSCRIPT)
    check_case("verdict_key_outside_pairs_ok",
               code == 0 and not any("Q1 verdict key" in ln for ln in lines))

    # ------- framing prose "these passages conflict" -> F5 FAIL
    env = envelope(HAPPY_PAIRS)
    code, lines = check(artifact(HAPPY_PAIRS, framing="_These passages conflict; read both._"),
                        env, MANUSCRIPT)
    check_case("framing_relation_vocab_f5_fail",
               code == 1 and any("F5 presentation prose" in ln and "conflict" in ln for ln in lines))
    # …but a relation word INSIDE a `>` blockquote-evidence line is exempt (the author's quote).
    conflict_quote_ms = ("The author writes: The parties remain in open conflict over the border. "
                         "And also: A durable ceasefire is now within reach.\n")
    qq_a = "The parties remain in open conflict over the border."
    qq_b = "A durable ceasefire is now within reach."
    ev_pairs = [pair("What does the author say about the border situation?", qq_a, qq_b)]
    code, lines = check(artifact(ev_pairs), envelope(ev_pairs), conflict_quote_ms)
    check_case("relation_word_in_blockquote_exempt",
               code == 0 and any("PASS" in ln for ln in lines))
    # ------- THE PANEL P1 REPRO: a FABRICATED `>` line (not verbatim manuscript text) carrying a
    # relation assertion is NOT exempt — it is framing dressed as evidence and F5 catches it.
    fabricated = ("\n> NOTE: these two passages plainly contradict each other and the author "
                  "reverses position.\n")
    code, lines = check(artifact(HAPPY_PAIRS) + fabricated, envelope(HAPPY_PAIRS), MANUSCRIPT)
    check_case("fabricated_blockquote_framing_f5_fail",
               code == 1 and any("F5 presentation prose" in ln for ln in lines))

    # ------- re-ranked pairs (artifact order != envelope order) -> FAIL
    env = envelope(HAPPY_PAIRS)  # envelope: Q1 then Q2
    reranked = list(reversed(HAPPY_PAIRS))  # artifact: Q2 then Q1
    code, lines = check(artifact(reranked), env, MANUSCRIPT)
    check_case("reranked_order_fail",
               code == 1 and any("Order:" in ln for ln in lines))
    # ------- THE PANEL P2 REPRO: headings not in the canonical `### <n>. Q:` form -> order is
    # UNVERIFIABLE -> WARN (never a silent skip), escalating to FAIL under --strict.
    unparseable = artifact(HAPPY_PAIRS).replace("### 1. Q: ", "## First question — ").replace(
        "### 2. Q: ", "## Second question — ")
    code, lines = check(unparseable, envelope(HAPPY_PAIRS), MANUSCRIPT)
    check_case("order_unverifiable_warns",
               code == 0 and any("Order unverifiable" in ln and "WARN" in ln for ln in lines))
    code, lines = check(unparseable, envelope(HAPPY_PAIRS), MANUSCRIPT, strict=True)
    check_case("order_unverifiable_strict_fails", code == 1)

    # ------- unreadable manuscript -> fail-closed
    code, lines = check(artifact(HAPPY_PAIRS), envelope(HAPPY_PAIRS), None,
                        manuscript_err="unreadable or not UTF-8")
    check_case("unreadable_manuscript_failclosed",
               code == 1 and any("manuscript" in ln and "ERROR" in ln for ln in lines))
    # ------- unreadable / invalid envelope -> fail-closed
    code, lines = check(artifact(HAPPY_PAIRS), None, MANUSCRIPT, envelope_err="invalid JSON — x")
    check_case("unreadable_envelope_failclosed",
               code == 1 and any("envelope" in ln and "ERROR" in ln for ln in lines))
    # ------- unreadable artifact -> fail-closed
    code, lines = check(None, envelope(HAPPY_PAIRS), MANUSCRIPT)
    check_case("unreadable_artifact_failclosed",
               code == 1 and any("artifact" in ln and "ERROR" in ln for ln in lines))

    # ------- non-UTF8 file: _read must degrade to None, never a traceback (fail-closed via run())
    d = tempfile.mkdtemp()
    made.append(d)
    nu = os.path.join(d, "bad.txt")
    with open(nu, "wb") as fh:
        fh.write(b"\xff\xfenot utf-8\xff")
    check_case("non_utf8_read_returns_none", _read(nu) is None)

    # ------- run() end-to-end over real files on disk (happy) -> PASS
    ap = os.path.join(d, "register.md")
    ep = os.path.join(d, "envelope.json")
    mp = os.path.join(d, "manuscript.txt")
    with open(ap, "w", encoding="utf-8") as fh:
        fh.write(artifact(HAPPY_PAIRS))
    with open(ep, "w", encoding="utf-8") as fh:
        json.dump(envelope(HAPPY_PAIRS), fh)
    with open(mp, "w", encoding="utf-8") as fh:
        fh.write(MANUSCRIPT)
    code, lines = run([ap, ep, mp])
    check_case("run_end_to_end_pass", code == 0 and any("PASS" in ln for ln in lines))
    # ------- run() with too few args -> usage exit 2
    check_case("run_usage_error", run([ap, ep])[0] == 2)
    # ------- run() with a missing envelope file on disk -> fail-closed (exit 1, named)
    code, lines = run([ap, os.path.join(d, "nope.json"), mp])
    check_case("run_missing_envelope_failclosed",
               code == 1 and any("envelope" in ln and "ERROR" in ln for ln in lines))

    for dd in made:
        shutil.rmtree(dd, ignore_errors=True)
    print("Self-test: PASS" if rc["v"] == 0 else "Self-test: FAIL")
    return rc["v"]


def main(argv):
    if "--self-test" in argv:
        return run_self_test()
    args = [a for a in argv[1:] if a not in ("position-pair-register",)]
    strict = "--strict" in args
    paths = [a for a in args if not a.startswith("--")]
    if not paths:
        print("Usage: position_pair_gates.py position-pair-register <artifact.md> <envelope.json> "
              "<manuscript> [--strict] | --self-test")
        return 2
    code, lines = run(paths, strict=strict)
    for ln in lines:
        print(ln)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
