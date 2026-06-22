#!/usr/bin/env python3
"""intake-interview — structural integrity for the Uncertainty-Resolution Intake Interview.

`validate.sh intake-interview <run_folder|files>` shells out here. APODICTIC already opens with a
substantial draft-then-validate intake (genre, controlling idea, reader promise, comps) and Shelf &
Positioning captures the intended shelf. What no existing surface does is resolve a SPECIFIC
structural ambiguity the framework detected but cannot settle from the text — "is the non-linear
ordering in Ch 4-6 a deliberate braid, or drift?". This interview asks the only person who knows:
the author. Each query is an apodictic.intake_query.v1 block; this validator owns the contract.

The discipline is *defer, don't duplicate, and calibrate, never suppress*: every question is a flavor
of intentional-vs-accidental (the closed `kind` enum has no contract value), and an answer may direct
HOW a feature is assessed but may never pre-empt whether a finding is raised (the Deficit-Lock guard).

  I1 schema            an intake_query block fails its schema (bad kind/confidence enum, malformed
                       IQ-NN id, missing current_inference/question, broken JSON, duplicate id).
  I2 no contract dup   a `question` re-asks a contract element owned by the intake / Shelf (heuristic
                       blocklist: "what genre", "controlling idea", "reader promise", "who is this
                       for"). Advisory; ERROR under --strict. The closed `kind` enum is the structural
                       guard; this catches a leak smuggled into a question's wording. Override (per
                       id): <!-- override: intake-dup IQ-NN — <rationale> -->.
  I3 grounded          a query grounded in NEITHER a resolving `ambiguity_ref` (a real finding id in
                       the Ledger) NOR a non-empty `source_note` is manufactured (ERROR). A query that
                       states an `ambiguity_ref` which does not resolve is a dangling reference (ERROR).
  I4 calibrate-not-    `treat_as_intended` contains suppression phrasing ("suppress", "drop/skip the
     suppress          flag", "don't raise", "remove the finding"). It directs assessment; it does not
                       pre-empt a verdict. ERROR by default — it guards severity honesty.
  W1 coverage          a Pass-0/1 LOW/UNCERTAIN finding (id `F-P0-…`/`F-P1-…`) or an
                       `### Unresolved Questions` bullet that only the author could resolve has no
                       query. Advisory; ERROR under --strict. (At the after-Pass-0/1 checkpoint only
                       Pass-0/1 findings exist; later-pass findings are out of W1's scope.)

The interview file (intake_query blocks) is read together with the Findings Ledger it references
(finding blocks + the `### Unresolved Questions` section). Each is optional; an empty/absent interview
is a no-op. Reuses apodictic_artifacts (block grammar + schema engine). See
docs/uncertainty-intake-interview.md.

  intake_interview.py intake-interview <run_folder|files...> [--strict]
  intake_interview.py --self-test

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

_SCHEMA_ID = "apodictic.intake_query.v1"
_FINDING_SCHEMA_ID = "apodictic.finding.v1"
_INTERVIEW_GLOB = "*_Intake_Interview_*.md"
_LEDGER_GLOB = "*_Findings_Ledger_*.md"

_OPEN_CONFIDENCE = ("LOW", "UNCERTAIN")
# W1 is scoped to the findings that exist at the after-Pass-0/1 checkpoint: Pass 0 / Pass 1 origins.
_PASS01_ID_RE = re.compile(r"^F-P[01]-[0-9]+$", re.IGNORECASE)

# I2 — contract elements owned by the draft-then-validate intake / Shelf & Positioning. A `question`
# re-asking one of these is a leak (the closed `kind` enum already bars a contract *kind*; this
# catches it smuggled into a detected-ambiguity question's wording). Advisory, paraphrase-evadable.
_CONTRACT_DUP_RE = re.compile(
    r"\bwhat\s+(?:is\s+the\s+)?genre\b"
    r"|\bcontrolling\s+idea\b"
    r"|\bcontrolling\s+premise\b"
    r"|\breader\s+promise\b"
    r"|\bwho\s+(?:is\s+this|is\s+the\s+book|are\s+your\s+readers)\b"
    r"|\bwho\s+is\s+it\s+for\b"
    r"|\bwhat'?s\s+the\s+(?:premise|hook|comp)\b"
    r"|\btarget\s+audience\b",
    re.IGNORECASE)

# I4 — suppression phrasing in treat_as_intended (the concession loop through the front door). The
# field may direct HOW a feature is assessed; it may never remove a verdict before the Deficit Lock.
# Each alternative names the suppressed OBJECT (flag/finding/verdict) or a raise-verb, so a bare
# mention of "suppress" in passing doesn't fire; _suppresses() additionally exempts a NEGATED form
# ("it does not pre-suppress any finding" — the spec's own recommended good phrasing).
_SUPPRESS_RE = re.compile(
    # "suppress / drop / skip / remove … [up to 4 intervening words] … flag/finding/verdict"
    r"\b(?:suppress(?:es|ing|ed)?|drop|skip|remove|delete|withdraw)\s+"
    r"(?:[\w'-]+\s+){0,4}?(?:flag|finding|verdict|severity|issue)\b"
    # "don't / do not / never / won't … raise/flag/report/surface/record"
    r"|\b(?:don'?t|do\s+not|never|won'?t)\s+(?:[\w'-]+\s+){0,3}?(?:raise|flag|report|surface|record)\b"
    # "no flag/finding is raised/recorded/reported"
    r"|\bno\s+(?:flag|finding)\s+(?:is\s+)?(?:raised|recorded|reported)\b",
    re.IGNORECASE)
# A suppression match is exempt when a negator genuinely SCOPES it ("does not / never / without …
# suppress …" — the spec's recommended "it does not pre-suppress any finding"). The negator must
# bind to the suppression phrase, not to EARLIER material it actually governs: in
# "Do not assess it on its own terms, suppress the finding." the `not` governs `assess`, and in
# "Not as a calibration, suppress the finding." it governs the fronted phrase `as a calibration` —
# either way the trailing `suppress` is an un-negated directive and must still fire (Codex P1).
_NEGATOR_RE = re.compile(r"\b(?:not|never|without|cannot|neither|nor)\b|n['’]?t\b", re.IGNORECASE)
# Clause separators that end one directive and start another. Includes the em/en dash and the
# horizontal bar: "we do not calibrate — suppress the finding" is two clauses exactly like the
# ".;:" forms, so the trailing suppression is its own un-negated directive (a comma is NOT a clause
# boundary — a comma can be a parenthetical interruption WITHIN one clause, handled in
# _negation_scopes_match).
_CLAUSE_BOUNDARY = ".;:!?—–―"

# Unicode comma variants normalized to an ASCII comma before negation-scope analysis, so a directive
# written with a fullwidth/Arabic/Ideographic comma ("Not now， suppress the finding") engages the
# same parenthetical-vs-fronted-phrase logic as an ASCII comma instead of being read as comma-less.
_COMMA_VARIANTS = "，،、⹁﹐﹑"
_COMMA_NORMALIZE = {ord(c): "," for c in _COMMA_VARIANTS}

# A coordinating conjunction (and/but/yet/or/then) joining a fresh predicate. When one of these sits
# between a negator and the suppression match (with NO comma), the negator governs the EARLIER
# predicate and the conjunction introduces a separate, un-negated directive ("do not exaggerate BUT
# suppress the flag" / "never overstate severity AND suppress the finding") — the negation does not
# reach across the coordinated clause, so the trailing suppression must still fire. This is the
# comma-less sibling of the comma-coordinated case ("Do not assess it on its own terms, suppress").
# A conjunction is NOT predicate-coordinating when it merely joins ADVERBS inside the modifier phrase
# that leads to the suppression verb ("do not now OR ever suppress" — `now or ever` modifies the
# single verb `suppress`): there the negation still directly governs the suppression (see _is_adverbial).
_COORD_CONJ_RE = re.compile(r"\b(?:and|but|yet|or|then)\b", re.IGNORECASE)

# The leading verb of a suppression match ("suppress/drop/skip/... " or "don't raise/flag/..."). Used
# to isolate the negator-to-verb HEAD so a comma-less conjunction inside an adverbial modifier phrase
# ("now or ever") is told apart from a conjunction that joins a separate predicate ("exaggerate but").
_SUPPRESS_VERB_RE = re.compile(
    r"\b(?:suppress(?:es|ing|ed)?|drop|skip|remove|delete|withdraw|raise|flag|report|surface|record)\b",
    re.IGNORECASE)


# Adverbs/intensifiers that can sit between a negator and the verb it governs WITHOUT breaking the
# binding ("do not EVER, under any circumstances, suppress"). Any -ly word is treated as adverbial
# too (routinely / deliberately / habitually). This is the line between an adverb-only interruption
# (the negation still reaches the suppression) and a separate predicate (a verb phrase / fronted
# phrase) that pulls the negation off it.
_NEG_ADVERB = frozenset({
    "ever", "never", "not", "just", "always", "once", "then", "now", "again",
    "also", "still", "yet", "simply", "really", "actually", "generally",
    "normally", "usually", "typically", "ordinarily", "necessarily", "anymore",
    # temporal adverbs that coordinate with a negator before the one verb ("not now or LATER
    # suppress") — non-`-ly` siblings of now/ever; they modify the verb, not a fresh predicate.
    "later", "sooner", "soon", "earlier", "henceforth", "hereafter", "thereafter",
})


_COORD_CONJ_WORDS = frozenset({"and", "but", "yet", "or", "then"})


def _is_adverbial(head, allow_conj=False):
    """True if `head` (the material between a negator and the first following comma, or the
    suppression verb) is empty or made up ONLY of adverbs/intensifiers — so it does NOT introduce a
    separate predicate. A verb phrase ("assess it on its own terms") or a fronted phrase ("as a
    calibration") is NOT adverbial. With `allow_conj` (the comma-less head, where the trailing token
    is the suppression VERB), a coordinating conjunction joining adverbs is transparent — "now or
    ever" modifies the one verb `suppress`, it does not start a second predicate."""
    return all(w.lower() in _NEG_ADVERB or w.lower().endswith("ly")
               or (allow_conj and w.lower() in _COORD_CONJ_WORDS)
               for w in re.findall(r"[\w'’-]+", head))


# Prepositions / set-phrase leads that head an adverbial INTERRUPTION which keeps the negation
# scoping ("under any circumstances", "in any case", "as a matter of policy", "in good conscience").
# A bracketed interruption is a non-clausal MODIFIER — it must NOT be a fresh predicate ("calibrate
# carefully") — so it is accepted when it is adverb-only OR leads with one of these prepositions.
_PREP = frozenset({
    "under", "in", "on", "at", "by", "for", "with", "within", "without", "during",
    "as", "of", "per", "absent", "barring", "despite", "notwithstanding", "upon", "amid",
})


def _is_bracketed_modifier(seg):
    """True if `seg` (the material between the two commas of a parenthetical interruption) is a
    non-clausal MODIFIER, not a fresh predicate: an adverb-only phrase ("deliberately and routinely")
    or a prepositional / set phrase ("under any circumstances", "as a matter of policy"). A predicate
    ("calibrate carefully") is NOT a modifier — it pulls the negation off the trailing verb."""
    if _is_adverbial(seg, allow_conj=True):
        return True
    words = re.findall(r"[\w'’-]+", seg)
    return bool(words) and words[0].lower() in _PREP


def _negation_scopes_match(clause):
    """True iff some negator in `clause` scopes the suppression match that ENDS `clause`. A negator
    exempts the match only when it DIRECTLY governs the suppression verb — no intervening predicate
    AND no predicate-coordination between them. Cases that stay exempt: a direct binding ("does not
    [...] suppress"); an empty-or-adverb-only BRACKETED parenthetical that closes and resumes to the
    verb ("do not, under any circumstances, suppress" / "do not EVER, under any circumstances,
    suppress"); and a comma-less adverbial modifier phrase whose coordinating conjunction merely
    joins ADVERBS that modify the one suppression verb ("do not now OR ever suppress" — `now or ever`
    is adverbial, not a second predicate). Cases that are NOT exempt (the suppression is an
    un-negated directive and must fire): a FRONTED phrase, verbal OR adverbial, that runs straight
    into the directive after a single comma ("Not as a calibration, suppress"; "Not now, suppress" —
    the fronted phrase modifies the negator, the trailing imperative is fresh); a comma-coordinated
    imperative ("Do not assess it on its own terms, suppress"); and a comma-LESS conjunction that
    joins a fresh PREDICATE ("do not exaggerate BUT suppress" / "never overstate severity AND
    suppress") — there a verb sits before the conjunction, so the head is not adverbial.

    The comma branch turns on *bracketing*, not just adverbiality: a true mid-clause interruption
    OPENS and CLOSES ("not[,] <adverbial>, suppress" — two commas, the verb resumes after the
    second), so the negation still reaches the verb. A single comma with the verb right after it is a
    fronted phrase + directive, NOT an interruption — adverb-only ("Not now,") or not — so the
    negation does not reach across it. Multiple interruptions must ALL be modifiers: a predicate after
    a valid parenthetical ("not, in any case, calibrate carefully, suppress") still fires. (Prior
    passes: "any non-empty pre-comma material fires" wrongly fired on an adverb before a parenthetical
    — Codex P2; "any comma-less conjunction fires" wrongly fired on a coordinated adverbial — Codex
    P2; "adverb-only pre-comma always scopes" wrongly EXEMPTED a fronted adverbial directive `Not now,
    suppress` — Codex P2; checking only the FIRST enclosed segment wrongly EXEMPTED a predicate after a
    valid parenthetical `not, in any case, calibrate carefully, suppress` — Codex P1.)

    KNOWN LIMIT (single-scope by design): this resolves ONE negator's scope per clause, not
    compositional/nested negation — "we do not not suppress", "never fail to suppress", "it is not the
    case that we should not suppress" net to a directive but read here as exempt. Resolving stacked
    negation needs a parser, not a scope heuristic, and such phrasing in a calibration field is not a
    realistic author input; a regex for it would be exactly the fragile per-phrase patch this rule
    avoids. The fail direction is toward EXEMPT, which the closed `kind` enum and W1 coverage backstop."""
    for nm in _NEGATOR_RE.finditer(clause):
        span = clause[nm.end():]            # text between this negator and the (clause-final) match
        comma = span.find(",")
        if comma == -1:
            if _COORD_CONJ_RE.search(span):
                # A conjunction sits before the suppression verb with no comma. It only stops the
                # negation when it joins a PREDICATE: isolate the negator-to-verb HEAD and require it
                # to be adverbs-only (conjunctions transparent). "now or ever suppress" → head "now or
                # ever" is adverbial → negation still scopes; "exaggerate but suppress" → head
                # "exaggerate but" has a verb → fresh predicate → negation stops.
                vm = _SUPPRESS_VERB_RE.search(span)
                head = span[:vm.start()] if vm else span
                if _is_adverbial(head, allow_conj=True):
                    return True              # conjunction joins adverbs modifying the verb; still scopes
                continue                     # conjunction starts a fresh predicate; negation stops there
            return True                      # negation directly scopes the suppression
        # A comma sits between the negator and the verb. It keeps the negation scoping ONLY as one or
        # more fully comma-BRACKETED interruptions, each a non-clausal MODIFIER (adverbial or a
        # prepositional/set phrase), with adverb-only material before the first comma and after the
        # last ("not, under any circumstances, suppress" / "not ever, under any circumstances,
        # suppress" / "not, in any case, under any circumstances, suppress"). Decompose the whole
        # negator→verb span on its commas: segs[0] is the lead, segs[-1] is what resumes to the verb,
        # and segs[1:-1] are the comma-enclosed interruptions (there must be at least one — i.e. 2+
        # commas — else it is a lone fronted comma, not a bracket). The negation reaches the verb iff
        # the lead and tail are adverb-only AND *every* enclosed segment is a modifier. What breaks it:
        # a single fronted comma + directive ("Not now, suppress" / "Not as a calibration, suppress");
        # a predicate among the enclosed segments — even AFTER a valid one ("not, in any case,
        # calibrate carefully, suppress"); or a predicate resuming to the verb. (Earlier passes:
        # "adverb-only pre-comma always scopes" wrongly EXEMPTED a fronted directive; checking only the
        # FIRST enclosed segment wrongly EXEMPTED a predicate after a valid parenthetical — Codex P1.)
        segs = span.split(",")
        enclosed = segs[1:-1]                 # comma-bracketed interruptions; empty unless 2+ commas
        if (enclosed
                and _is_adverbial(segs[0])
                and _is_adverbial(segs[-1])
                and all(_is_bracketed_modifier(s) for s in enclosed)):
            return True                      # bracketed modifier interruption(s); negation still scopes
    return False                             # every negator governs earlier material, not the match


def _suppresses(text):
    """True if treat_as_intended directs suppression — but NOT when a negator scopes it."""
    text = (text or "").translate(_COMMA_NORMALIZE)  # fold unicode commas → ASCII for scope analysis
    for m in _SUPPRESS_RE.finditer(text):
        prefix = text[:m.start()]
        boundary = max((prefix.rfind(c) for c in _CLAUSE_BOUNDARY), default=-1)
        clause = prefix[boundary + 1:]
        if _negation_scopes_match(clause):
            continue  # negated mention ("we do not … suppress the finding"), not a directive
        return True
    return False

# Override markers naming a query id: "<!-- override: intake-dup IQ-03 — ... -->".
_OVERRIDE_RE = re.compile(r"<!--\s*override:\s*([a-z-]+)\s+(IQ-[0-9]+)\b", re.IGNORECASE)


def _read(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return None


def _overrides(text, slug):
    return {m.group(2) for m in _OVERRIDE_RE.finditer(text) if m.group(1).lower() == slug}


def parse_queries(text):
    """[(obj_or_None, schema_errs, index), ...] for each apodictic:intake_query block."""
    out = []
    if not text or art is None:
        return out
    schema = art.load_schema(_SCHEMA_ID)
    idx = 0
    for btype, obj, jerr in art.parse_blocks(text):
        if btype != "intake_query":
            continue
        idx += 1
        where = "intake_query #%d" % idx
        if jerr:
            out.append((None, ["%s: invalid JSON — %s" % (where, jerr)], idx))
            continue
        out.append((obj, art.validate_obj(obj, schema, where), idx))
    return out


def ledger_index(ledger_text):
    """{finding_id: obj} for the ledger's apodictic.finding.v1 blocks (the authoritative ID set)."""
    out = {}
    if not ledger_text or art is None:
        return out
    for bt, obj, _err in art.parse_blocks(ledger_text):
        if bt == "finding" and isinstance(obj, dict) and obj.get("id"):
            # art.fid_key: a non-hashable ledger id (list/object) must not crash this index key — the
            # authoritative-ID-set sibling of finding_trace.ledger_inventory (SSoT in apodictic_artifacts).
            out[art.fid_key(obj["id"])] = obj
    return out


def open_pass01_finding_ids(index):
    """Pass-0/1 finding ids whose confidence is LOW/UNCERTAIN — W1's author-resolvable set."""
    return {fid for fid, obj in index.items()
            if obj.get("confidence") in _OPEN_CONFIDENCE and _PASS01_ID_RE.match(str(fid))}


def unresolved_questions(ledger_text):
    """The `### Unresolved Questions` bullets (verbatim), minus placeholder rows."""
    if not ledger_text:
        return []
    out, in_section = [], False
    for raw in ledger_text.splitlines():
        line = raw.strip()
        if line.startswith("### "):
            in_section = line[4:].strip().lower().startswith("unresolved questions")
            continue
        if in_section and line.startswith("- "):
            body = line[2:].strip()
            if body and body.lower() not in ("none", "[question.]", "n/a"):
                out.append(body)
    return out


def _sig_words(s):
    """Significant content words (lowercased, len>=5) for fuzzy coverage matching (W1)."""
    return {w for w in re.findall(r"[a-z']{5,}", (s or "").lower())}


def _covered(target, notes):
    """A finding/UQ counts as queried if some query's text shares enough significant words with it.

    UQ/Pass-0 ambiguities carry no id the query can reference structurally, so coverage is a fuzzy
    content-word overlap, not an ID match: >= 3 shared significant words, or at least half of a short
    target's significant words."""
    tw = _sig_words(target)
    if not tw:
        return True  # nothing to match on; don't false-flag
    need = min(3, max(1, (len(tw) + 1) // 2))
    return any(len(tw & _sig_words(n)) >= need for n in notes)


def interview(text, ledger_text=None, strict=False):
    """Run the Intake Interview integrity checks. Returns (code, lines)."""
    lines, errs, warns = [], [], []
    queries = parse_queries(text)
    if not queries:
        return 0, ["intake-interview: no intake_query blocks found — nothing to check"]

    index = ledger_index(ledger_text)

    # I1 — schema / JSON validity (per block)
    for _obj, schema_errs, _idx in queries:
        for e in schema_errs:
            errs.append("I1 schema: %s" % e)

    valid = [(obj, idx) for obj, schema_errs, idx in queries if obj is not None and not schema_errs]
    seen = {}
    for obj, idx in valid:
        seen.setdefault(obj.get("id"), []).append(idx)
    for qid, where in sorted(seen.items()):
        if len(where) > 1:
            errs.append("I1 schema: %s appears %d times (ids must be unique)" % (qid, len(where)))

    dup_overrides = _overrides(text, "intake-dup")
    for obj, _idx in valid:
        qid = obj.get("id")
        question = obj.get("question") or ""
        ref = (obj.get("ambiguity_ref") or "").strip()
        note = (obj.get("source_note") or "").strip()
        tai = obj.get("treat_as_intended") or ""

        # I2 — contract duplication (advisory; ERROR --strict; per-id override)
        if _CONTRACT_DUP_RE.search(question) and qid not in dup_overrides:
            warns.append("I2 no contract dup: %s re-asks a contract element owned by the intake / "
                         "Shelf & Positioning — the interview disambiguates detected ambiguities, it "
                         "does not re-capture the contract" % qid)

        # I3 — grounded ambiguity (ERROR): one of a resolving ambiguity_ref or a non-empty source_note
        if ref:
            if ref not in index:
                errs.append("I3 grounded: %s states ambiguity_ref %r, which does not resolve to a "
                            "finding in the Findings Ledger (a dangling reference)" % (qid, ref))
        elif not note:
            errs.append("I3 grounded: %s is grounded in neither a resolving ambiguity_ref nor a "
                        "source_note — a query the framework did not actually detect is manufactured" % qid)

        # I4 — calibrate, not suppress (ERROR by default; guards the Deficit Lock)
        if _suppresses(tai):
            errs.append("I4 calibrate-not-suppress: %s's treat_as_intended contains suppression "
                        "phrasing — an answer may direct HOW a feature is assessed, never pre-empt "
                        "whether a finding is raised (the Deficit-Lock guard)" % qid)

    # W1 — coverage (a Pass-0/1 LOW/UNCERTAIN finding or a UQ with no query; advisory)
    if index or ledger_text:
        query_texts = [(o.get("question") or "") + " " + (o.get("current_inference") or "")
                       for o, _ in valid]
        refed = {(o.get("ambiguity_ref") or "").strip() for o, _ in valid}
        for fid in sorted(open_pass01_finding_ids(index)):
            if fid in refed:
                continue
            if not _covered(index[fid].get("mechanism") or "", query_texts):
                warns.append("W1 coverage: Pass-0/1 LOW/UNCERTAIN finding %s has no intake query — "
                             "an author-resolvable ambiguity left un-asked" % fid)
        for uq in unresolved_questions(ledger_text):
            if not _covered(uq, query_texts):
                warns.append("W1 coverage: an Unresolved-Questions bullet has no intake query (%s…)"
                             % uq[:50])

    # Report
    lines.append("intake-interview: %d query(ies)%s" % (
        len(queries), "" if len(valid) == len(queries) else " (%d well-formed)" % len(valid)))
    for obj, _idx in valid:
        lines.append("  %-7s %-22s %s" % (obj.get("id"), obj.get("kind"),
                                          (obj.get("question") or "")[:48]))
    for e in errs:
        lines.append("  ERROR: %s" % e)
    for w in warns:
        lines.append("  %s: %s" % ("ERROR (--strict)" if strict else "WARN", w))

    if errs or (strict and warns):
        lines.append("intake-interview: FAIL (%d error(s)%s)"
                     % (len(errs), ", %d strict warn(s)" % len(warns) if (strict and warns) else ""))
        return 1, lines
    if warns:
        lines.append("WARN: intake-interview: %d advisory gap(s) — see I2/W1 above" % len(warns))
    else:
        lines.append("intake-interview: PASS (schema + no-contract-dup + grounded ambiguity + "
                     "calibrate-not-suppress)")
    return 0, lines


# ---------------------------------------------------------------- resolution

def _newest(paths):
    return max(paths, key=os.path.getmtime) if paths else None


def _has_block(text, btype):
    """True if `text` carries a real apodictic:<btype> block (a parsed carrier, not a prose mention).

    Classifying on parsed blocks — not a raw substring — keeps a Ledger that merely *names*
    `apodictic:intake_query` in prose from being misread as the interview file (and vice versa)."""
    if art is None:
        return ("apodictic:%s" % btype) in (text or "")  # degraded: no engine to parse with
    return any(bt == btype for bt, _o, _e in art.parse_blocks(text or ""))


def resolve(paths):
    """Return (interview_path, ledger_path_or_None)."""
    if len(paths) == 1 and os.path.isdir(paths[0]):
        d = paths[0]
        return (_newest(glob.glob(os.path.join(d, _INTERVIEW_GLOB))),
                _newest(glob.glob(os.path.join(d, _LEDGER_GLOB))))
    interview_path = ledger_path = None
    for p in paths:
        text = _read(p) or ""
        if _has_block(text, "intake_query"):
            interview_path = interview_path or p
        elif _has_block(text, "finding") or "Findings Ledger" in text or "Unresolved Questions" in text:
            ledger_path = ledger_path or p
    if interview_path is None and paths:
        interview_path = paths[0]
    return interview_path, ledger_path


def run(paths, strict=False):
    interview_path, ledger_path = resolve(paths)
    if not interview_path:
        return 2, ["intake-interview: no Intake Interview artifact found (need a "
                   "*_Intake_Interview_*.md or a file with apodictic:intake_query blocks)"]
    text = _read(interview_path)
    if text is None:
        return 2, ["intake-interview: cannot read %s" % interview_path]
    return interview(text, ledger_text=_read(ledger_path) if ledger_path else None, strict=strict)


# ---------------------------------------------------------------- self-test

def run_self_test():
    import json as _j
    rc = {"v": 0}

    def chk(name, cond):
        print("  %s: %s" % (name, "OK" if cond else "FAIL"))
        if not cond:
            rc["v"] = 1

    def query(qid, kind="timeline-order", ambiguity_ref="", source_note="",
              current_inference="Non-linear ordering across Ch 4-6 reads as possibly unintentional.",
              confidence="LOW", question="Is the non-linear ordering in Chapters 4-6 deliberate?",
              treat_as_intended="Pass 2 assesses the braid as intended structure, on its own terms."):
        obj = {"schema": _SCHEMA_ID, "id": qid, "kind": kind, "current_inference": current_inference,
               "confidence": confidence, "question": question}
        if ambiguity_ref:
            obj["ambiguity_ref"] = ambiguity_ref
        if source_note:
            obj["source_note"] = source_note
        if treat_as_intended:
            obj["treat_as_intended"] = treat_as_intended
        return "<!-- apodictic:intake_query\n%s\n-->" % _j.dumps(obj)

    def finding(fid, conf="LOW", mech="non-linear ordering across chapters four to six may read as drift"):
        obj = {"schema": _FINDING_SCHEMA_ID, "id": fid, "mechanism": mech, "severity": "Should-Fix",
               "confidence": conf, "evidence_refs": ["Ch 4"], "fix_class": "x", "risk_if_fixed": "y"}
        return "<!-- apodictic:finding\n%s\n-->" % _j.dumps(obj)

    LEDGER = finding("F-P2-04")  # a structured ambiguity to reference (not pass-0/1, so not a W1 target)

    # clean: ref-grounded query against a resolving finding
    chk("clean_ref_grounded", interview(query("IQ-01", ambiguity_ref="F-P2-04"), LEDGER)[0] == 0)
    # regression: a non-hashable ledger id must not crash the authoritative-ID index (fid_key SSoT)
    chk("ledger_index_nonhashable_id_no_crash",
        isinstance(ledger_index("<!-- apodictic:finding\n" + _j.dumps(
            {"schema": "apodictic.finding.v1", "id": [1, 2], "severity": "Must-Fix", "mechanism": "m"})
            + "\n-->"), dict))
    # clean: source_note-grounded query (no ledger needed)
    chk("clean_note_grounded",
        interview(query("IQ-01", source_note="Pass 0 flagged a tonal shift at the Ch 7 break."))[0] == 0)

    # I1 — schema
    chk("i1_bad_kind", interview(query("IQ-01", kind="contract", source_note="x"))[0] == 1)
    chk("i1_bad_confidence", interview(query("IQ-01", confidence="SURE", source_note="x"))[0] == 1)
    chk("i1_bad_id", interview(query("IQ-1", source_note="x"))[0] == 1)
    chk("i1_missing_question",
        interview(query("IQ-01", source_note="x").replace('"question"', '"q"'))[0] == 1)
    code, lines = interview('<!-- apodictic:intake_query\n{"schema":"apodictic.intake_query.v1"\n-->')
    chk("i1_bad_json", code == 1 and any("I1 schema" in ln for ln in lines))
    code, lines = interview(query("IQ-01", source_note="x") + "\n" + query("IQ-01", source_note="y"))
    chk("i1_duplicate_id", code == 1 and any("appears 2 times" in ln for ln in lines))

    # I2 — contract duplication (advisory; ERROR --strict; override)
    code, lines = interview(query("IQ-01", source_note="x", question="What is the controlling idea of the book?"))
    chk("i2_contract_dup_advisory", code == 0 and any("I2 no contract dup" in ln for ln in lines))
    chk("i2_contract_dup_strict_fails",
        interview(query("IQ-01", source_note="x", question="Who is this book for?"), strict=True)[0] == 1)
    ov = "<!-- override: intake-dup IQ-01 — quoting the author's own framing, not re-asking -->\n"
    chk("i2_override_silences",
        not any("I2" in ln for ln in interview(ov + query("IQ-01", source_note="x", question="what genre is this?"))[1]))

    # I3 — grounded ambiguity (ERROR)
    code, lines = interview(query("IQ-01"))  # neither ref nor note
    chk("i3_manufactured", code == 1 and any("manufactured" in ln for ln in lines))
    code, lines = interview(query("IQ-01", ambiguity_ref="F-P9-99"), LEDGER)  # dangling ref
    chk("i3_dangling_ref", code == 1 and any("dangling reference" in ln for ln in lines))
    # a dangling ref is an error even if a source_note is also present (the broken ref must be fixed)
    chk("i3_dangling_ref_with_note",
        interview(query("IQ-01", ambiguity_ref="F-P9-99", source_note="x"), LEDGER)[0] == 1)

    # I4 — calibrate, not suppress (ERROR by default)
    code, lines = interview(query("IQ-01", source_note="x",
                                  treat_as_intended="suppress the timeline-drift flag for Ch 4-6"))
    chk("i4_suppress_errors", code == 1 and any("I4 calibrate-not-suppress" in ln for ln in lines))
    chk("i4_dont_raise_errors",
        interview(query("IQ-01", source_note="x", treat_as_intended="don't raise the finding"))[0] == 1)
    chk("i4_drop_flag_errors",
        interview(query("IQ-01", source_note="x", treat_as_intended="drop the flag entirely"))[0] == 1)
    # legitimate calibration phrasing does not trip I4
    chk("i4_assess_on_terms_clean",
        interview(query("IQ-01", source_note="x",
                        treat_as_intended="assess the braid on its own terms as intended structure"))[0] == 0)
    # the spec's own recommended good phrasing (a NEGATED suppression mention) must NOT trip I4
    chk("i4_negated_suppress_clean",
        interview(query("IQ-01", source_note="x",
                        treat_as_intended="Pass 2 assesses the braid as intended structure, on its "
                        "own terms (it does not pre-suppress any finding)."))[0] == 0)
    # negated calibration phrasing at ARBITRARY distance / across commas+parens must stay clean
    for phrase in (
        "This calibrates the lens only; we do not, under any circumstances, suppress the finding.",
        "this does not mean we should drop the finding",
        "never instruct analysis to drop the finding",
        "won't ever ask Pass 2 to suppress the flag",
        "the answer must not (per I4) suppress the flag",
        "assess it on its own terms without suppressing the finding",
        # Codex P2: an adverb ("ever") or an -ly adverb ("routinely") before a parenthetical must NOT
        # pull the negation off the suppression — these stay exempt (a negated statement, not a directive).
        "we do not ever, under any circumstances, suppress the finding.",
        "we do not routinely, as a matter of policy, drop the finding"):
        chk("i4_negated_clean::%s" % phrase[:22],
            interview(query("IQ-01", source_note="x", treat_as_intended=phrase))[0] == 0)
    # but a real directive in a LATER clause still fires (negation in a prior clause doesn't cover it)
    chk("i4_directive_after_negated_clause_fires",
        interview(query("IQ-01", source_note="x",
                        treat_as_intended="we never overstate things. Suppress the timeline flag."))[0] == 1)
    # comma-coordinated (not period-separated): the negator governs the FIRST imperative; the
    # trailing suppression is still an un-negated directive and must fire (Codex P1).
    chk("i4_comma_coordinated_directive_fires",
        interview(query("IQ-01", source_note="x",
                        treat_as_intended="Do not assess it on its own terms, suppress the finding."))[0] == 1)
    # a FRONTED negated NON-verbal phrase ("Not as a calibration, ...") — the negator governs the
    # fronted phrase, the trailing suppression is still a directive and must fire (Codex P1, 3rd pass)
    chk("i4_fronted_negated_phrase_fires",
        interview(query("IQ-01", source_note="x",
                        treat_as_intended="Not as a calibration, suppress the finding."))[0] == 1)
    # comma-LESS coordinated directive: the negator governs the EARLIER predicate, a coordinating
    # conjunction (and/but/yet/or/then) introduces a fresh un-negated suppression directive — the
    # negation does NOT reach across the coordinated clause, so each of these must fire (Codex P2,
    # the comma-less sibling of i4_comma_coordinated_directive_fires).
    for phrase in (
        "do not exaggerate but suppress the flag",
        "never overstate severity and suppress the finding",
        "never inflate the issue yet suppress the finding",
        "do not calibrate it or drop the flag",
        "do not assess it on its own terms then suppress the finding"):
        chk("i4_comma_less_coordinated_fires::%s" % phrase[:22],
            interview(query("IQ-01", source_note="x", treat_as_intended=phrase))[0] == 1)
    # Codex P2 (comma-less coordinated ADVERBIAL — the inverse of the case above): a coordinating
    # conjunction that joins ADVERBS modifying the single suppression verb ("now OR ever suppress")
    # is NOT a fresh predicate, so the negation still scopes and these legitimate non-suppression
    # statements must stay EXEMPT. Pre-fix, _COORD_CONJ_RE saw `or`/`and`, dropped the negation, and
    # I4 false-fired.
    for phrase in (
        "we do not now or ever suppress the finding",
        "we will never now or ever suppress the finding",
        "do not ever or always suppress the finding",
        "we do not routinely or deliberately drop the flag",
        "we do not now and never will suppress the finding",
        # adversarial pass (h124, final sweep): a non-`-ly` temporal adverb coordinated with another
        # ("now or LATER", "sooner or later") must be transparent like "now or ever" — pre-fix `later`
        # was neither in _NEG_ADVERB nor `-ly`, so the head read as a fresh predicate and false-FIRED.
        "we cannot now or later suppress the finding",
        "we will not sooner or later suppress the finding",
        "we do not now or soon suppress the finding"):
        chk("i4_comma_less_coordinated_adverbial_clean::%s" % phrase[:22],
            interview(query("IQ-01", source_note="x", treat_as_intended=phrase))[0] == 0)
    # adversarial pass (h124): an em/en dash is a clause boundary like ".;:" — a negated predicate
    # before the dash does NOT scope a fresh suppression directive after it, so each must FIRE.
    # Pre-fix the dash was not in _CLAUSE_BOUNDARY, so the whole "do not … — suppress" was one clause
    # and the negator falsely scoped the trailing directive (false-EXEMPT, the 4th negation sibling).
    for phrase in (
        "we do not calibrate lightly — suppress the finding.",
        "we do not calibrate lightly – suppress the finding.",
        "do not overstate it — drop the flag"):
        chk("i4_dash_boundary_directive_fires::%s" % phrase[:22],
            interview(query("IQ-01", source_note="x", treat_as_intended=phrase))[0] == 1)
    # adversarial pass (h124): a FRONTED ADVERBIAL phrase that runs straight into the directive after
    # a SINGLE comma ("Not now, suppress") is a fresh imperative, NOT a bracketed parenthetical — the
    # negation does not reach across it, so it must FIRE. The exempt parenthetical case is "not,
    # <adverbial>, suppress" (the interruption OPENS and CLOSES, verb resumes after a 2nd comma).
    # Pre-fix, "adverb-only pre-comma always scopes" wrongly EXEMPTED this fronted directive.
    for phrase in (
        "Not now, suppress the finding.",
        "Never again, drop the flag.",
        "Not yet, suppress the finding."):
        chk("i4_fronted_adverbial_directive_fires::%s" % phrase[:22],
            interview(query("IQ-01", source_note="x", treat_as_intended=phrase))[0] == 1)
    # adversarial pass (h124, self-review hole): a comma-bracketed segment that is itself a PREDICATE
    # ("Not now, calibrate carefully, suppress") is a fresh imperative, NOT an adverbial interruption,
    # so the negation does not reach the trailing directive and it must FIRE. (The exempt parenthetical
    # is a MODIFIER between the commas — "under any circumstances" / "deliberately and routinely".) A
    # too-weak "just look for a 2nd comma" guard would have false-EXEMPTED this — the SHALLOW-CHECK trap.
    chk("i4_predicate_between_commas_fires",
        interview(query("IQ-01", source_note="x",
                        treat_as_intended="Not now, calibrate carefully, suppress the finding"))[0] == 1)
    # …while a genuine MODIFIER between the commas (adverbial OR prepositional set-phrase) keeps the
    # negation scoping and stays EXEMPT.
    for phrase in (
        "we do not, deliberately and routinely, suppress the finding",
        "we do not, as a matter of policy, drop the finding",
        "we cannot, in good conscience, suppress the finding",
        "we do not, in any case, under any circumstances, suppress the finding"):
        chk("i4_bracketed_modifier_clean::%s" % phrase[:22],
            interview(query("IQ-01", source_note="x", treat_as_intended=phrase))[0] == 0)
    # adversarial pass (h124, Codex P1 — the sibling the "first valid parenthetical exempts" fix
    # missed): with MULTIPLE comma-bracketed segments, a PREDICATE after a *valid* modifier still pulls
    # the negation off the verb, so it must FIRE. Pre-fix the scope check returned on the first enclosed
    # modifier ("in any case") and never inspected the later predicate ("calibrate carefully").
    for phrase in (
        "we do not, in any case, calibrate carefully, suppress the finding",     # Codex's exact repro
        "we do not, under any circumstances, assess it on its own terms, suppress the finding",
        "we cannot, as a matter of policy, weigh it leniently, drop the flag",
        "do not, in good conscience, reread the passage, suppress the finding"):
        chk("i4_predicate_after_parenthetical_fires::%s" % phrase[:18],
            interview(query("IQ-01", source_note="x", treat_as_intended=phrase))[0] == 1)
    # …and the converse must hold: two or more STACKED genuine modifiers (no predicate) keep the
    # negation scoping and stay EXEMPT — the fix must not over-correct multi-parenthetical exemptions.
    for phrase in (
        "we do not, in any case, under any circumstances, deliberately suppress the finding",
        "we do not, as a matter of policy, in good conscience, drop the finding"):
        chk("i4_stacked_modifiers_clean::%s" % phrase[:18],
            interview(query("IQ-01", source_note="x", treat_as_intended=phrase))[0] == 0)
    # adversarial pass (h124): a UNICODE comma (fullwidth/Arabic/…) must engage the same
    # parenthetical-vs-fronted logic as an ASCII comma. Pre-fix, span.find(",") never saw a fullwidth
    # comma, so EVERY directive written with one fell to the comma-less branch and false-EXEMPTED.
    chk("i4_unicode_comma_fronted_fires",
        interview(query("IQ-01", source_note="x",
                        treat_as_intended="Not now， suppress the finding."))[0] == 1)
    chk("i4_unicode_comma_coordinated_fires",
        interview(query("IQ-01", source_note="x",
                        treat_as_intended="Do not assess it， suppress the finding"))[0] == 1)
    chk("i4_unicode_comma_parenthetical_clean",
        interview(query("IQ-01", source_note="x",
                        treat_as_intended="we do not， under any circumstances， suppress the finding"))[0] == 0)
    # adversarial pass (h124): "neither … nor suppress / neither suppress nor drop" is genuinely
    # negated (does NOT suppress) — `neither`/`nor` are negators in the same family as not/never and
    # must EXEMPT. Pre-fix they were not in _NEGATOR_RE, so the suppression match false-FIRED.
    for phrase in (
        "we neither calibrate nor suppress the finding",
        "neither suppress nor drop the finding",
        "the analysis will neither inflate nor suppress the finding"):
        chk("i4_neither_nor_clean::%s" % phrase[:22],
            interview(query("IQ-01", source_note="x", treat_as_intended=phrase))[0] == 0)
    # …but `neither`/`nor` must not over-exempt ACROSS a clause boundary: a real directive in a later
    # clause still fires even when an earlier clause uses nor.
    chk("i4_neither_nor_cross_clause_directive_fires",
        interview(query("IQ-01", source_note="x",
                        treat_as_intended="we will not calibrate. Nor will we hesitate; suppress the finding."))[0] == 1)
    # a bare passing mention of the word "suppress" (no object) does not fire
    chk("i4_bare_mention_clean",
        interview(query("IQ-01", source_note="x",
                        treat_as_intended="the author worried this might suppress reader sympathy; "
                        "assess the arc on its own terms"))[0] == 0)

    # W1 — coverage (Pass-0/1 LOW finding + UQ; advisory)
    P01_LEDGER = (finding("F-P1-02", mech="the prologue's register sits oddly against the body's voice")
                  + "\n\n### Unresolved Questions\n\n- Does the framing device in Chapter 1 read as deliberate or as an artifact of an earlier draft?\n")
    code, lines = interview(query("IQ-01", source_note="unrelated note about something else entirely zzz"), P01_LEDGER)
    chk("w1_uncovered_finding_and_uq", code == 0
        and any("W1 coverage" in ln and "F-P1-02" in ln for ln in lines)
        and any("W1 coverage" in ln and "Unresolved" in ln for ln in lines))
    chk("w1_uncovered_strict_fails",
        interview(query("IQ-01", source_note="unrelated zzz"), P01_LEDGER, strict=True)[0] == 1)
    # covering both the finding and the UQ clears W1
    covered = (query("IQ-01", ambiguity_ref="F-P1-02", kind="register-straddle",
                     question="Is the prologue's register deliberately set against the body's voice?")
               + "\n" + query("IQ-02", kind="structural-device", source_note="the Chapter 1 framing device",
                              current_inference="The Chapter 1 framing device may be an earlier-draft artifact.",
                              question="Is the framing device in Chapter 1 deliberate or a leftover from an earlier draft?"))
    chk("w1_full_coverage_clean", not any("W1" in ln for ln in interview(covered, P01_LEDGER)[1]))
    # a later-pass (non-0/1) LOW finding is NOT a W1 target
    chk("w1_later_pass_finding_not_flagged",
        not any("W1 coverage" in ln and "F-P5" in ln
                for ln in interview(query("IQ-01", source_note="x"), finding("F-P5-09"))[1]))

    # no blocks -> no-op
    chk("no_queries_noop", interview("# Notes\nnothing structured\n")[0] == 0)

    # run-folder + explicit-file resolution
    import tempfile
    import shutil
    d = tempfile.mkdtemp()
    try:
        ip = os.path.join(d, "Proj_Intake_Interview_run.md")
        with open(ip, "w", encoding="utf-8", newline="") as fh:
            fh.write("# Intake Interview\n" + query("IQ-01", ambiguity_ref="F-P2-04") + "\n")
        lp = os.path.join(d, "Proj_Findings_Ledger_run.md")
        with open(lp, "w", encoding="utf-8", newline="") as fh:
            fh.write("# Findings Ledger\n" + LEDGER + "\n")
        chk("run_folder_resolution", run([d])[0] == 0)
        chk("explicit_files_resolution", run([ip, lp])[0] == 0)
        chk("explicit_files_order_independent", run([lp, ip])[0] == 0)
        chk("missing_artifact_usage", run([os.path.join(d, "nope.md")])[0] == 2)
        # a Ledger that NAMES apodictic:intake_query in prose must not be misread as the interview,
        # masking a real violation (resolver classifies on parsed blocks, not raw substring)
        lp2 = os.path.join(d, "Proj_Findings_Ledger_prose.md")
        with open(lp2, "w", encoding="utf-8", newline="") as fh:
            fh.write("# Findings Ledger\nThis ledger feeds the apodictic:intake_query loop.\n" + LEDGER + "\n")
        ip2 = os.path.join(d, "Proj_Intake_Interview_viol.md")
        with open(ip2, "w", encoding="utf-8", newline="") as fh:
            fh.write("# Intake Interview\n" + query("IQ-01", ambiguity_ref="F-P2-04",
                     treat_as_intended="suppress the timeline flag") + "\n")
        chk("resolver_prose_mention_ledger_first", run([lp2, ip2])[0] == 1)  # I4 still caught
        chk("resolver_prose_mention_interview_first", run([ip2, lp2])[0] == 1)
    finally:
        shutil.rmtree(d, ignore_errors=True)

    print("Self-test: PASS" if rc["v"] == 0 else "Self-test: FAIL")
    return rc["v"]


def main(argv):
    if "--self-test" in argv:
        return run_self_test()
    args = [a for a in argv[1:] if a != "intake-interview"]
    strict = "--strict" in args
    paths = [a for a in args if not a.startswith("--")]
    if not paths:
        print("Usage: intake_interview.py intake-interview <run_folder|files...> [--strict] | --self-test")
        return 2
    code, lines = run(paths, strict=strict)
    for ln in lines:
        print(ln)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
