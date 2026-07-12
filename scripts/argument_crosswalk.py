#!/usr/bin/env python3
"""argument-crosswalk-check — R4A wellformedness gate for the argument-taxonomy crosswalk.

Validates `evals/argument-crosswalk/crosswalk.json` against the layer-boundary ADR
(`docs/adr/0001-argument-layer-boundary.md`). Stdlib-only.

The gate certifies SHAPE, not scholarly correctness (see the ADR "firewall" section):
membership completeness against a DERIVED registry set (never a re-typed 4th copy),
family well-typing, the closed cardinality enum, the unmapped<->no-targets equivalence,
a non-empty rationale on every unmapped row, a provenance locator on every populated
target, a global non-injectivity floor, the closed external-ref value-spaces, and the
drift-binding. The correctness of each mapping is human/Codex-adjudicated.

Drift-binding (ADR): the authoritative 82-ID set is derived at check time — the verdict,
premise-flag, and FM-A slices are imported from the live owners in argument_groundtruth.py
(_GT7_CLASSES / _GT8_ROW_FLAG_TYPES / _FM_A_MAX); the 46 Dialectical Clarity codes and 8
scheme hints — which have no machine-readable owner — are parsed structurally out of
dialectical-clarity.md (heading/table walk, bounded leaf tokens; the structural discipline,
not a doc-wide regex).

Usage:
  argument_crosswalk.py --self-test
  argument_crosswalk.py --check [<crosswalk.json>]
  argument_crosswalk.py argument-crosswalk-check [<crosswalk.json>]
"""
import json
import os
import re
import sys

# --------------------------------------------------------------------------
# Closed external-ref value-spaces (ADR / SPEC §3a). Inline for R4A.
# --------------------------------------------------------------------------
AIF_NODES = {"I-node", "RA-node", "CA-node", "PA-node"}

WALTON_SCHEMES = {
    "Expert Opinion", "Consequences", "Cause to Effect", "Correlation to Cause",
    "Analogy", "Example", "Witness Testimony", "Position to Know",
    "Practical Reasoning", "Sign", "Popular Opinion", "Slippery Slope",
    "Ad Hominem", "Verbal Classification",
}
# Schemes whose `#CQ<n>` critical-question suffix is bounded (Walton & Macagno). A scheme
# absent from this map rejects ANY `#` suffix — so `Expert Opinion#CQ999` / `#garbage` / a bare
# trailing `#` fail rather than silently pass. Argument from Expert Opinion has six basic CQs
# (Expertise / Field / Opinion / Trustworthiness / Consistency / Backup-Evidence).
WALTON_CQ_MAX = {"Expert Opinion": 6}
_WALTON_CQ_RE = re.compile(r"CQ(\d+)$")

SF_REFS = {
    "family:vagueness", "family:ambiguity", "family:relevance", "family:vacuity",
    "refutation:premise", "refutation:conclusion", "refutation:inference", "refutation:begging",
    "standard:validity", "standard:strength", "standard:soundness",
    "move:assuring", "move:guarding", "move:discounting",
}
TOULMIN_REFS = {"claim", "grounds", "warrant", "backing", "qualifier", "rebuttal"}

WACHSMUTH_SUB = {
    "logic": {"LAc", "LRe", "LSu"},
    "rhetoric": {"arrangement", "appropriateness", "clarity", "credibility", "emotional-appeal"},
    "dialectic": {"GAc", "GRe", "GSu", "reasonableness"},
}

VOCABS = {"AIF", "WALTON", "SF", "WACHSMUTH", "TOULMIN"}
ENTRY_KEYS = {"id", "family", "internal_name", "cardinality", "targets", "rationale"}
CONCEPT_KEYS = {"id", "kind", "cardinality", "targets", "rationale"}
TARGET_REQUIRED_KEYS = {"vocab", "ref", "cardinality", "prov"}
TARGET_ALLOWED_KEYS = TARGET_REQUIRED_KEYS | {"note"}
PROV_KEYS = {"work", "loc", "id"}
ROW_CARDS = {"exact", "broader", "narrower", "related", "unmapped"}
TARGET_CARDS = {"exact", "broader", "narrower", "related"}
_CARD_PREC = {"exact": 4, "narrower": 3, "broader": 2, "related": 1}

DC_PREFIXES = ("AT", "AC", "CL", "SM", "WR", "BP", "OB", "DI", "NE")
DC_FAMILY_COUNTS = {"AT": 5, "AC": 5, "CL": 5, "SM": 5, "WR": 4,
                    "BP": 7, "OB": 6, "DI": 5, "NE": 4}
NONPREFIX_FAMILIES = {"SCHEME", "VERDICT", "PREMISE-FLAG"}

# --------------------------------------------------------------------------
# Structural registry parse (drift-binding, bounded leaf tokens)
# --------------------------------------------------------------------------
_DC_ROW_RE = re.compile(r"^\|\s*\*\*(" + "|".join(DC_PREFIXES) + r")(\d+)\*\*")
# A canonical code-definition table has `Code` as its FIRST column. Two header shapes exist:
# the 8 failure-code families + AT0 use `| Code | Name | Description |`, and the argument-type
# table (AT1-AT4) uses `| Code | Type | Promise to Reader | Burden Level |`. Anchoring on the
# first column being exactly `Code` captures both while excluding the support-type
# (`| Support Type | ... |`), scheme-hint, and objection-expectation (`| Type | ... |`) tables.
_CODE_TABLE_HEADER_RE = re.compile(r"^\|\s*Code\s*\|", re.IGNORECASE)
_SCHEME_HEADER_RE = re.compile(r"^\|\s*Scheme Hint\s*\|", re.IGNORECASE)
_TABLE_CELL1_BOLD_RE = re.compile(r"^\|\s*\*\*([^*|]+?)\*\*\s*\|")


def parse_dc_codes(registry_text):
    """Structural table walk: a DC code is a bolded leaf token at the start of a row
    INSIDE a canonical code-definition table (one whose FIRST column header is `Code`).
    Scoping to that header excludes the support-type and scheme tables that also carry
    bold column-1 tokens (e.g. a stray `| **AC5** |` row in an unrelated table is NOT
    counted). Check 9's exact-contiguous-set assertion backstops any residual tamper.
    Returns a set."""
    codes = set()
    in_code_table = False
    for line in registry_text.splitlines():
        if _CODE_TABLE_HEADER_RE.match(line):
            in_code_table = True
            continue
        if in_code_table:
            if not line.lstrip().startswith("|"):
                in_code_table = False          # table ended at the first non-table line
                continue
            m = _DC_ROW_RE.match(line)
            if m:
                codes.add(m.group(1) + m.group(2))
    return codes


def parse_schemes(registry_text):
    """Structural: locate the 'Scheme Hint | ...' table by its header, then read the
    bolded column-1 leaf token of each following table row until the table ends."""
    schemes = []
    lines = registry_text.splitlines()
    in_table = False
    seen_sep = False
    for line in lines:
        if not in_table:
            if _SCHEME_HEADER_RE.match(line):
                in_table = True
                seen_sep = False
            continue
        # inside the scheme table
        if not line.lstrip().startswith("|"):
            break  # table ended
        if not seen_sep:
            # the |---|---| separator row follows the header
            if set(line.replace("|", "").strip()) <= set("-: "):
                seen_sep = True
                continue
        m = _TABLE_CELL1_BOLD_RE.match(line)
        if m:
            schemes.append(m.group(1).strip())
    return schemes


def derived_id_set(dc_codes, schemes, verdicts, flags, fm_max):
    ids = set(dc_codes)
    ids |= {"FM-A%d" % i for i in range(1, fm_max + 1)}
    ids |= set(schemes)
    ids |= set(verdicts)
    ids |= set(flags)
    return ids


def family_of(cid, schemes, verdicts, flags):
    if cid in schemes:
        return "SCHEME"
    if cid in verdicts:
        return "VERDICT"
    if cid in flags:
        return "PREMISE-FLAG"
    if cid.startswith("FM-A"):
        return "FM-A"
    if len(cid) >= 3 and cid[:2] in DC_FAMILY_COUNTS and cid[2:].isdigit():
        return cid[:2]
    return None


def _ref_ok(vocab, ref):
    if vocab == "AIF":
        return ref in AIF_NODES
    if vocab == "WALTON":
        scheme, sep, cq = ref.partition("#")
        if scheme not in WALTON_SCHEMES:
            return False
        if not sep:
            return True                              # bare scheme
        m = _WALTON_CQ_RE.fullmatch(cq)              # a `#` suffix must be a bounded CQ<n>
        if not m:
            return False
        return 1 <= int(m.group(1)) <= WALTON_CQ_MAX.get(scheme, 0)
    if vocab == "SF":
        return ref in SF_REFS
    if vocab == "WACHSMUTH":
        if ":" not in ref:
            return ref in WACHSMUTH_SUB          # bare dimension (logic|rhetoric|dialectic)
        dim, _, sub = ref.partition(":")
        if dim not in WACHSMUTH_SUB:
            return False
        return sub in WACHSMUTH_SUB[dim]         # a trailing colon with empty sub is rejected
    if vocab == "TOULMIN":
        return ref in TOULMIN_REFS
    return False


def validate_concepts(cross, relations, agd_families):
    """Validate R2/R3 concepts separately from the closed 82-code layer."""
    errors = []
    rows = cross.get("concept_entries") if isinstance(cross, dict) else None
    if not isinstance(rows, list):
        return ["Check 11 (concepts) — concept_entries must be a list."]
    expected = {"R2:" + x for x in relations} | {"R3:" + x for x in agd_families}
    ids = [r.get("id") for r in rows if isinstance(r, dict)]
    string_ids = [x for x in ids if isinstance(x, str)]
    if len(rows) != len(ids) or len(string_ids) != len(ids) or set(string_ids) != expected or len(string_ids) != len(set(string_ids)):
        errors.append("Check 11 (concepts) — ids must equal the derived R2/R3 set (expected=%r got=%r)." % (sorted(expected), sorted(str(x) for x in ids)))
    for r in rows:
        if not isinstance(r, dict):
            errors.append("Check 11 (concepts) — every concept row must be an object."); continue
        if set(r) != CONCEPT_KEYS:
            errors.append("Check 11 (concepts) — concept row %r must have the closed row shape." % r.get("id"))
        cid = r.get("id"); kind = r.get("kind"); card = r.get("cardinality"); tgts = r.get("targets"); rationale = r.get("rationale")
        exp_kind = "objection-relation" if isinstance(cid, str) and cid.startswith("R2:") else "agd-move"
        if kind != exp_kind: errors.append("Check 11 (concepts) — %r kind must be %r." % (cid, exp_kind))
        if not isinstance(card, str) or card not in ROW_CARDS: errors.append("Check 11 (concepts) — %r bad cardinality." % cid)
        if not isinstance(tgts, list): errors.append("Check 11 (concepts) — %r targets must be a list." % cid); continue
        if (card == "unmapped") != (not tgts): errors.append("Check 11 (concepts) — %r unmapped equivalence failed." % cid)
        if card == "unmapped" and not (isinstance(rationale, str) and rationale.strip()): errors.append("Check 11 (concepts) — %r unmapped rationale required." % cid)
        present = []
        target_ids = []
        for t in tgts:
            if not isinstance(t, dict): errors.append("Check 11 (concepts) — %r target must be object." % cid); continue
            if not TARGET_REQUIRED_KEYS <= set(t) <= TARGET_ALLOWED_KEYS: errors.append("Check 11 (concepts) — %r target must have the closed target shape." % cid)
            v, ref, tc, prov = t.get("vocab"), t.get("ref"), t.get("cardinality"), t.get("prov")
            target_ids.append((repr(v), repr(ref)))
            if not isinstance(v, str) or v not in VOCABS or not isinstance(ref, str) or not _ref_ok(v, ref): errors.append("Check 11 (concepts) — %r target %r:%r outside closed refs." % (cid, v, ref))
            if not isinstance(tc, str) or tc not in TARGET_CARDS: errors.append("Check 11 (concepts) — %r bad target cardinality." % cid)
            else: present.append(tc)
            if not (isinstance(prov, dict) and set(prov) == PROV_KEYS and all(isinstance(prov.get(k), str) and prov[k].strip() for k in PROV_KEYS)): errors.append("Check 11 (concepts) — %r target provenance must have the closed complete shape." % cid)
            if isinstance(cid, str) and cid.startswith("R3:") and v == "AIF": errors.append("Check 11 (policy) — AGD moves are AIF-unmapped.")
            if cid == "R2:ALTERNATIVE" and v == "AIF": errors.append("Check 11 (policy) — ALTERNATIVE has no AIF conflict criterion.")
        if present and card != max(present, key=lambda c: _CARD_PREC[c]): errors.append("Check 11 (concepts) — %r roll-up mismatch." % cid)
        if len(target_ids) != len(set(target_ids)): errors.append("Check 11 (concepts) — %r has a duplicate vocab/ref target." % cid)
    return errors


def validate_stable_rationales(cross):
    errors = []
    stale = re.compile(r"\bR(?:3|4B)\b|\brevisit\b|\badjudicat(?:e|ion)\b|\bdeferred\b", re.I)
    for row in cross.get("entries", []) if isinstance(cross, dict) else []:
        if isinstance(row, dict) and row.get("cardinality") == "unmapped" and stale.search(str(row.get("rationale", ""))):
            errors.append("Check 13 (stable rationale) — %r retains a future-work placeholder." % row.get("id"))
    return errors


# --------------------------------------------------------------------------
# Core validation
# --------------------------------------------------------------------------
def validate(cross, dc_codes, schemes, verdicts, flags, fm_max):
    """Returns a list of error strings ([] == clean). Pure over its inputs."""
    errors = []
    if not isinstance(cross, dict) or not isinstance(cross.get("entries"), list):
        return ["Check 10 (JSON hygiene) — top-level must be an object with an 'entries' list."]
    if cross.get("version") != "0.2.0":
        errors.append("Check 10 (JSON hygiene) — crosswalk version must be exactly 0.2.0.")
    entries = cross["entries"]
    derived = derived_id_set(dc_codes, schemes, verdicts, flags, fm_max)

    # Check 1 — membership completeness (against the DERIVED set)
    ids = []
    for r in entries:
        cid = r.get("id") if isinstance(r, dict) else None
        if not isinstance(cid, str) or not cid.strip():
            errors.append("Check 1 (membership) — every entry needs a non-empty string id (got %r)." % (cid,))
            ids.append(None)            # hashable proxy: a JSON list/dict id must not crash set()/sorted
            continue
        ids.append(cid)
        if re.fullmatch(r"P\d+", cid):
            errors.append("Check 1 (membership) — %r is a premise-INSTANCE label, not a "
                          "premise-flag TYPE; valid PREMISE-FLAG ids are the five types." % cid)
    # sort with a total order that tolerates None / non-string ids (a malformed row must not crash the gate)
    _key = lambda x: (x is None, str(type(x)), str(x))
    dup = sorted({c for c in ids if ids.count(c) > 1}, key=_key)
    for c in dup:
        errors.append("Check 1 (membership) — duplicate id %r." % c)
    idset = set(ids)
    for missing in sorted(derived - idset, key=_key):
        errors.append("Check 1 (membership) — missing required id %r (in derived registry set)." % missing)
    for extra in sorted(idset - derived, key=_key):
        if not (isinstance(extra, str) and re.fullmatch(r"P\d+", extra)):
            errors.append("Check 1 (membership) — unknown id %r (not in derived registry set)." % extra)

    # Per-row structural checks
    seen_refs = {}
    for r in entries:
        if not isinstance(r, dict):
            errors.append("Check 10 (JSON hygiene) — every entry must be an object (got %r)." % type(r).__name__)
            continue
        if set(r) != ENTRY_KEYS:
            errors.append("Check 10 (JSON hygiene) — entry %r must have the closed row shape." % r.get("id"))
        cid = r.get("id", "<no-id>")
        if not isinstance(cid, str):
            # hashable proxy: a JSON list/dict id must not crash downstream set inserts
            # (seen_refs). Check 1 already reported the real bad value.
            cid = "<non-string-id>"
        fam = r.get("family")
        card = r.get("cardinality")
        targets = r.get("targets", [])
        rationale = r.get("rationale")

        # Check 2 — family well-typing
        exp_fam = family_of(cid, schemes, verdicts, flags) if isinstance(cid, str) else None
        if exp_fam is None:
            errors.append("Check 2 (family) — id %r does not resolve to a known family." % cid)
        elif fam != exp_fam:
            errors.append("Check 2 (family) — id %r has family %r, expected %r." % (cid, fam, exp_fam))

        # Check 3 — cardinality enum (row) — isinstance-guard so an unhashable JSON scalar
        # (e.g. a list) yields a clean error instead of a `TypeError: unhashable type`.
        if not isinstance(card, str) or card not in ROW_CARDS:
            errors.append("Check 3 (cardinality) — id %r row cardinality %r not in enum." % (cid, card))
        if not isinstance(targets, list):
            errors.append("Check 10 (JSON hygiene) — id %r 'targets' must be a list." % cid)
            continue
        if any(not isinstance(x, dict) for x in targets):
            errors.append("Check 10 (JSON hygiene) — id %r has a non-object target element." % cid)
            targets = [x for x in targets if isinstance(x, dict)]

        # Check 4 — roll-up equivalence
        if card == "unmapped":
            if targets:
                errors.append("Check 4 (roll-up) — id %r is 'unmapped' but has targets." % cid)
            # Check 5 — unmapped rationale non-empty
            if not (isinstance(rationale, str) and rationale.strip()):
                errors.append("Check 5 (unmapped rationale) — id %r is 'unmapped' but rationale is empty." % cid)
        else:
            if not targets:
                errors.append("Check 4 (roll-up) — id %r is %r but has no targets (should be 'unmapped')." % (cid, card))
            else:
                present = [tt.get("cardinality") for tt in targets
                           if isinstance(tt.get("cardinality"), str) and tt.get("cardinality") in _CARD_PREC]
                if present:
                    strongest = max(present, key=lambda c: _CARD_PREC[c])
                    if card != strongest:
                        errors.append("Check 4 (roll-up) — id %r row cardinality %r != strongest target %r."
                                      % (cid, card, strongest))

        # Per-target checks (6, 8a) + ref hit accounting (8b)
        target_ids = []
        for tt in targets:
            if not TARGET_REQUIRED_KEYS <= set(tt) <= TARGET_ALLOWED_KEYS:
                errors.append("Check 10 (JSON hygiene) — id %r target must have the closed target shape." % cid)
            vocab = tt.get("vocab")
            ref = tt.get("ref")
            target_ids.append((repr(vocab), repr(ref)))
            tcard = tt.get("cardinality")
            prov = tt.get("prov")
            if not isinstance(tcard, str) or tcard not in TARGET_CARDS:
                errors.append("Check 3 (cardinality) — id %r target cardinality %r not in target enum." % (cid, tcard))
            # Check 6 — target well-formedness (isinstance-guard so a non-string vocab/ref can't crash)
            if not isinstance(vocab, str) or vocab not in VOCABS:
                errors.append("Check 6 (target) — id %r target vocab %r not in {AIF,WALTON,SF,WACHSMUTH}." % (cid, vocab))
            elif not (isinstance(ref, str) and _ref_ok(vocab, ref)):
                errors.append("Check 6 (target) — id %r %s ref %r outside the closed value-space." % (cid, vocab, ref))
            # Check 8a — provenance locator: all three fields must be NON-EMPTY STRINGS
            # (a numeric/boolean/empty locator is unusable and must not pass on truthiness alone).
            if not (isinstance(prov, dict) and set(prov) == PROV_KEYS and all(
                    isinstance(prov.get(k), str) and prov.get(k).strip() for k in ("work", "loc", "id"))):
                errors.append("Check 8a (provenance) — id %r target (%s %r) lacks the closed string prov {work,loc,id}." % (cid, vocab, ref))
            if isinstance(vocab, str) and vocab in VOCABS and isinstance(ref, str):
                seen_refs.setdefault((vocab, ref), set()).add(cid)
        if len(target_ids) != len(set(target_ids)):
            errors.append("Check 10 (JSON hygiene) — id %r has a duplicate vocab/ref target." % cid)

    # Check 7 — no dangling Walton + every scheme-hint row maps to a Walton scheme
    for r in entries:
        if not isinstance(r, dict):
            continue
        cid = r.get("id")
        if cid in schemes:
            tgts = r.get("targets", [])
            tgts = tgts if isinstance(tgts, list) else []
            walton = [tt for tt in tgts if isinstance(tt, dict) and tt.get("vocab") == "WALTON"]
            if not walton:
                errors.append("Check 7 (walton) — scheme-hint row %r maps to no Walton scheme." % cid)

    # Check 8b — global non-injectivity floor
    many_to_one = {k: v for k, v in seen_refs.items() if len(v) >= 2}
    if not many_to_one:
        errors.append("Check 8b (arity) — no external ref is the target of >=2 internal rows; "
                      "a globally 1:1 crosswalk is the exact overclaim the ADR forbids.")

    # Check 9 — shape tripwires. The derived set must match the canonical taxonomy shape, so a parse
    # miscount OR a registry tamper (a code renamed within its table, a stray code-shaped row elsewhere,
    # a duplicated scheme) fails LOUDLY instead of silently certifying the wrong 82-set.
    # (a) DC codes must be EXACTLY the canonical contiguous per-family set — this catches e.g. AC4->AC5
    #     (AC4 missing + AC5 extra), which a per-family COUNT check would have missed.
    expected_dc = {"%s%d" % (fam, i) for fam, n in DC_FAMILY_COUNTS.items() for i in range(n)}
    if dc_codes != expected_dc:
        missing = sorted(expected_dc - dc_codes)
        extra = sorted(dc_codes - expected_dc)
        errors.append("Check 9 (tripwire) — derived DC set is not the canonical contiguous set "
                      "(missing=%s extra=%s); the registry's stale '45' or a renamed/stray code must not "
                      "propagate. Expected 46 incl. OB5." % (missing, extra))
    # (b) FM-A owner
    if fm_max != 20:
        errors.append("Check 9 (tripwire) — _FM_A_MAX is %r, expected 20 (intro's stale 'nineteen' must not propagate)." % fm_max)
    if "FM-A20" not in derived:
        errors.append("Check 9 (tripwire) — FM-A20 (Self-Undermining Remedy) missing from the derived set.")
    # (c) schemes — 8 and UNIQUE (parse_schemes returns a list; a duplicated scheme dedups in the set
    #     union and would otherwise pass a bare length check).
    if len(schemes) != 8 or len(set(schemes)) != 8:
        errors.append("Check 9 (tripwire) — expected 8 unique scheme hints, got %d (%d unique): %r."
                      % (len(schemes), len(set(schemes)), schemes))
    # (d) the unique derived union must total exactly 82 (backstops any slice miscount).
    if len(derived) != 82:
        errors.append("Check 9 (tripwire) — derived unique id union is %d, expected 82." % len(derived))

    return errors


# --------------------------------------------------------------------------
# File / owner resolution (real-file mode)
# --------------------------------------------------------------------------
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def _resolve(cands):
    for c in cands:
        if os.path.exists(c):
            return c
    return None


def _default_crosswalk():
    return _resolve([
        os.path.join(_SCRIPT_DIR, "..", "evals", "argument-crosswalk", "crosswalk.json"),
        os.path.join(_SCRIPT_DIR, "..", "..", "..", "evals", "argument-crosswalk", "crosswalk.json"),
    ])


def _registry_path():
    return _resolve([
        os.path.join(_SCRIPT_DIR, "..", "plugins", "apodictic", "skills",
                     "specialized-audits", "references", "craft", "dialectical-clarity.md"),
        os.path.join(_SCRIPT_DIR, "..", "skills", "specialized-audits",
                     "references", "craft", "dialectical-clarity.md"),
    ])


def _no_dupes_hook(pairs):
    seen = {}
    for k, v in pairs:
        if k in seen:
            raise ValueError("duplicate JSON key %r" % k)
        seen[k] = v
    return seen


def _load_json_no_dupes(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh, object_pairs_hook=_no_dupes_hook)


def _load_owners():
    """Import the live upstream enum owners (drift-binding)."""
    if _SCRIPT_DIR not in sys.path:
        sys.path.insert(0, _SCRIPT_DIR)
    from argument_groundtruth import _GT7_CLASSES, _GT8_ROW_FLAG_TYPES, _FM_A_MAX  # noqa
    from argument_spine import _OBJECTION_RELATIONS  # noqa
    from argument_agd import FAMILIES  # noqa
    return list(_GT7_CLASSES), set(_GT8_ROW_FLAG_TYPES), int(_FM_A_MAX), tuple(_OBJECTION_RELATIONS), tuple(FAMILIES)


def _vocabulary_migration_errors():
    """R4B active-surface allowlist: preserve history, reject partial live migration."""
    roots = [os.path.abspath(os.path.join(_SCRIPT_DIR, "..")),
             os.path.abspath(os.path.join(_SCRIPT_DIR, "..", "..", ".."))]
    root = next((r for r in roots if os.path.exists(os.path.join(r, "sample-dialectical-clarity-letter.html"))), None)
    if root is None:
        return []  # host bundle lacks repo-only active examples
    rels = [
        "plugins/apodictic/skills/specialized-audits/references/craft/dialectical-clarity.md",
        "plugins/apodictic/skills/specialized-audits/references/craft/dialectical-clarity-level-setting.md",
        "evals/fixtures/argument-benchmark/personal-essay-narrative-arg/groundtruth.md",
        "docs/argument-benchmark-calibration-round.md",
        "sample-dialectical-clarity-letter.html",
    ]
    errors = []
    texts = {}
    for rel in rels:
        p = os.path.join(root, rel)
        if not os.path.exists(p): errors.append("Check 12 (vocabulary) — active file missing: %s" % rel); continue
        with open(p, encoding="utf-8") as fh: texts[rel] = fh.read()
        if re.search(r"warrant-recoverability", texts[rel], re.I): errors.append("Check 12 (vocabulary) — retired token remains in %s" % rel)
    main = texts.get(rels[0], "")
    if not main.startswith("# Specialized Audit: Dialectical Clarity\n## Version 2.1\n*Previous version: 2.0 (March 2026)*"):
        errors.append("Check 12 (vocabulary) — live v2.1/previous-v2.0 header mismatch.")
    expected_counts = [3, 1, 1, 1, 1]
    for rel, expected in zip(rels, expected_counts):
        if len(re.findall(r"bridge-recoverability", texts.get(rel, ""), re.I)) != expected:
            errors.append("Check 12 (vocabulary) — Bridge-recoverability occurrence count drifted in %s" % rel)
    question = "Can the inferential bridge be recovered without importing a private argument the draft never gives?"
    if main.count("| **Bridge-recoverability** | " + question + " |") != 1 or main.count("| Bridge-recoverability | [pass/fail] | [detail] |") != 1:
        errors.append("Check 12 (vocabulary) — the two emitted Bridge-recoverability rows are not exact/unique.")
    expected_rows = ["Claim-accessibility", "Evidence-evaluability", "Bridge-recoverability", "Scope-honesty", "Objection-awareness", "Form-fit"]
    ordered = [name for name in re.findall(r"(?m)^\| \*\*([^*]+)\*\* \| (?:Can|Does|Is) ", main)
               if name in expected_rows]
    if ordered[:6] != expected_rows or len(ordered) != 6:
        errors.append("Check 12 (vocabulary) — six decision-test rows are missing, duplicated, or out of order.")
    return errors


def run_check(path):
    if path is None:
        path = _default_crosswalk()
        if path is None:
            print("SKIP: crosswalk.json not found (evals/ not shipped to this workspace) — advisory.")
            return 0
    if not os.path.exists(path):
        print("ERROR: crosswalk file not found: %s" % path)
        return 1
    reg = _registry_path()
    if reg is None:
        print("ERROR: dialectical-clarity.md registry not found; cannot derive the drift-bound code set.")
        return 1
    try:
        verdicts, flags, fm_max, relations, agd_families = _load_owners()
    except Exception as exc:  # pragma: no cover
        print("ERROR: could not import upstream owners from argument_groundtruth.py: %s" % exc)
        return 1
    with open(reg, "r", encoding="utf-8") as fh:
        registry_text = fh.read()
    dc_codes = parse_dc_codes(registry_text)
    schemes = parse_schemes(registry_text)
    try:
        cross = _load_json_no_dupes(path)
    except ValueError as exc:
        print("Check 10 (JSON hygiene) — %s" % exc)
        return 1
    except json.JSONDecodeError as exc:
        print("Check 10 (JSON hygiene) — crosswalk.json does not parse: %s" % exc)
        return 1
    errors = validate(cross, dc_codes, schemes, verdicts, flags, fm_max)
    errors.extend(validate_concepts(cross, relations, agd_families))
    errors.extend(validate_stable_rationales(cross))
    errors.extend(_vocabulary_migration_errors())
    if errors:
        print("argument-crosswalk-check: FAIL (%d)" % len(errors))
        for e in errors:
            print("  - %s" % e)
        return 1
    n = len(cross["entries"])
    unmapped = sum(1 for r in cross["entries"] if r.get("cardinality") == "unmapped")
    print("argument-crosswalk-check: PASS — %d code entries (%d populated, %d unmapped) + %d concepts; "
          "derived set 46 DC + %d FM-A + %d schemes + %d verdicts + %d flags."
          % (n, n - unmapped, unmapped, len(cross["concept_entries"]), fm_max, len(schemes), len(verdicts), len(flags)))
    return 0


# --------------------------------------------------------------------------
# Hermetic self-test
# --------------------------------------------------------------------------
def _selftest():
    fails = []

    def check(name, cond):
        if not cond:
            fails.append(name)

    # --- synthetic registry parse arms (the structural drift-parse itself) ---
    mini_registry = "\n".join([
        "### objection codes",
        "| Code | Name | Description |",
        "|------|------|-------------|",
        "| **OB0** | No objections | x |",
        "| **OB5** | Decoy strongest objection | x |",
        "some prose",
        "| Scheme Hint | Practical First Question |",
        "|-------------|--------------------------|",
        "| **Authority** | q |",
        "| **Practical Reasoning** | q |",
        "",
        "| **Sign** | not-in-scheme-table (after blank, table ended) |",
    ])
    dc = parse_dc_codes(mini_registry)
    check("parse_dc: finds OB0/OB5", dc == {"OB0", "OB5"})
    sch = parse_schemes(mini_registry)
    check("parse_schemes: scoped to the Scheme-Hint table", sch == ["Authority", "Practical Reasoning"])
    check("parse_schemes: excludes post-table Sign row", "Sign" not in sch)

    # --- controlled derived sets + a valid mini crosswalk ---
    dc_codes = {"%s%d" % (f, i) for f, n in DC_FAMILY_COUNTS.items() for i in range(n)}
    schemes = ["Authority", "Consequence", "Causal", "Analogy", "Example",
               "Testimony", "Practical Reasoning", "Sign"]
    verdicts = ["WARRANTED", "UNCONVENTIONAL-BUT-WARRANTED", "UNWARRANTED"]
    flags = {"CONTESTABLE", "UNEARNED", "OVERLOADED", "EXTERNAL-VERIFY", "DEFINITIONAL"}
    fm_max = 20

    def prov(ref):
        return {"work": "W", "loc": "L", "id": ref}

    def full_entries(dc_codes, schemes, verdicts, flags):
        ents = []
        # every DC code + FM-A + verdict + flag: unmapped (valid)
        for cid in list(dc_codes) + ["FM-A%d" % i for i in range(1, fm_max + 1)] + list(verdicts) + list(flags):
            fam = family_of(cid, schemes, verdicts, flags)
            ents.append({"id": cid, "family": fam, "internal_name": cid,
                         "cardinality": "unmapped", "targets": [], "rationale": "R4B"})
        # the 8 scheme rows: map to Walton (satisfies check 7) + give arity via a shared ref
        for s in schemes:
            ents.append({"id": s, "family": "SCHEME", "internal_name": s, "cardinality": "narrower",
                         "targets": [
                             {"vocab": "WALTON", "ref": "Expert Opinion", "cardinality": "exact", "prov": prov("Expert Opinion")},
                             {"vocab": "AIF", "ref": "RA-node", "cardinality": "narrower", "prov": prov("RA-node")},
                         ], "rationale": None})
        return ents

    valid = {"version": "0.2.0", "entries": full_entries(dc_codes, schemes, verdicts, flags)}
    # roll-up for scheme rows: strongest of exact/narrower = exact
    for r in valid["entries"]:
        if r["family"] == "SCHEME":
            r["cardinality"] = "exact"
    check("valid crosswalk passes clean", validate(valid, dc_codes, schemes, verdicts, flags, fm_max) == [])

    def mutate(fn):
        import copy
        c = copy.deepcopy(valid)
        fn(c)
        return validate(c, dc_codes, schemes, verdicts, flags, fm_max)

    # Check 1 — missing id
    check("hostile: missing id -> Check 1",
          any("missing required id" in e for e in mutate(lambda c: c["entries"].pop(0))))
    # Check 1 — P<n> instance label
    check("hostile: P1 instance label -> Check 1",
          any("premise-INSTANCE" in e for e in mutate(
              lambda c: c["entries"].append({"id": "P1", "family": "PREMISE-FLAG",
                                             "internal_name": "x", "cardinality": "unmapped",
                                             "targets": [], "rationale": "r"}))))
    # Check 1 — duplicate id
    check("hostile: duplicate id -> Check 1",
          any("duplicate id" in e for e in mutate(lambda c: c["entries"].append(dict(c["entries"][0])))))
    # Check 2 — wrong family
    check("hostile: wrong family -> Check 2",
          any("Check 2" in e for e in mutate(lambda c: c["entries"][0].update({"family": "ZZ"}))))
    # Check 3 — bad cardinality
    check("hostile: bad row cardinality -> Check 3",
          any("Check 3" in e for e in mutate(lambda c: c["entries"][0].update({"cardinality": "sorta"}))))

    def first_scheme(c):
        return next(r for r in c["entries"] if r["family"] == "SCHEME")

    # Check 4 — unmapped with targets
    check("hostile: unmapped+targets -> Check 4",
          any("Check 4" in e for e in mutate(
              lambda c: c["entries"][0].update({"targets": [{"vocab": "AIF", "ref": "RA-node",
                                               "cardinality": "related", "prov": prov("RA-node")}]}))))
    # Check 4 — roll-up mismatch (row 'related' but a target is 'exact')
    check("hostile: roll-up mismatch -> Check 4",
          any("!= strongest target" in e for e in mutate(
              lambda c: first_scheme(c).update({"cardinality": "related"}))))
    # Check 5 — unmapped empty rationale
    check("hostile: empty rationale -> Check 5",
          any("Check 5" in e for e in mutate(lambda c: c["entries"][0].update({"rationale": "  "}))))
    # Check 6 — bad vocab
    check("hostile: bad vocab -> Check 6",
          any("Check 6" in e for e in mutate(
              lambda c: first_scheme(c)["targets"].__setitem__(0, {"vocab": "NOPE", "ref": "x",
                                               "cardinality": "exact", "prov": prov("x")}))))
    # Check 6 — bad ref (Walton scheme not in registry)
    check("hostile: dangling walton ref -> Check 6",
          any("outside the closed value-space" in e for e in mutate(
              lambda c: first_scheme(c)["targets"][0].update({"ref": "Made Up Scheme"}))))
    # Check 6 — bad Wachsmuth sub-criterion
    check("hostile: bad wachsmuth sub -> Check 6",
          any("Check 6" in e for e in mutate(
              lambda c: first_scheme(c)["targets"].__setitem__(0, {"vocab": "WACHSMUTH", "ref": "logic:ZZ",
                                               "cardinality": "related", "prov": prov("logic:ZZ")}))))
    # Check 7 — scheme row without a Walton target
    check("hostile: scheme without walton -> Check 7",
          any("Check 7" in e for e in mutate(
              lambda c: first_scheme(c).update({"cardinality": "narrower",
                  "targets": [{"vocab": "AIF", "ref": "RA-node", "cardinality": "narrower", "prov": prov("RA-node")}]}))))
    # Check 8a — missing provenance
    check("hostile: missing prov -> Check 8a",
          any("Check 8a" in e for e in mutate(
              lambda c: first_scheme(c)["targets"][0].pop("prov"))))

    # Check 8b — globally 1:1 (all-injective) -> arity floor
    def all_injective():
        dcc = dict(dc_codes=dc_codes)
        c = {"version": "x", "entries": []}
        for cid in list(dc_codes) + ["FM-A%d" % i for i in range(1, 21)] + list(verdicts) + list(flags):
            fam = family_of(cid, schemes, verdicts, flags)
            c["entries"].append({"id": cid, "family": fam, "internal_name": cid,
                                 "cardinality": "unmapped", "targets": [], "rationale": "r"})
        # give each scheme a UNIQUE walton scheme (injective) so no ref repeats
        uniq = ["Expert Opinion", "Consequences", "Cause to Effect", "Analogy",
                "Example", "Witness Testimony", "Practical Reasoning", "Sign"]
        for s, w in zip(schemes, uniq):
            c["entries"].append({"id": s, "family": "SCHEME", "internal_name": s, "cardinality": "exact",
                                 "targets": [{"vocab": "WALTON", "ref": w, "cardinality": "exact", "prov": prov(w)}],
                                 "rationale": None})
        return validate(c, dc_codes, schemes, verdicts, flags, fm_max)
    check("hostile: globally 1:1 -> Check 8b", any("Check 8b" in e for e in all_injective()))

    # Check 9 — tripwires
    check("hostile: DC missing OB5 -> Check 9",
          any("OB5" in e for e in validate(valid, dc_codes - {"OB5"}, schemes, verdicts, flags, fm_max)))
    check("hostile: FM max 19 -> Check 9",
          any("_FM_A_MAX" in e for e in validate(valid, dc_codes, schemes, verdicts, flags, 19)))
    check("hostile: 7 schemes -> Check 9",
          any("unique scheme hints" in e for e in validate(
              valid, dc_codes, schemes[:7], verdicts, flags, fm_max)))

    # Check 10 — shape
    check("hostile: no entries list -> Check 10",
          any("Check 10" in e for e in [*(validate({"nope": 1}, dc_codes, schemes, verdicts, flags, fm_max))]))
    # Check 10 — a non-object target element must be flagged, not crash (review P2 #1/#11)
    check("hostile: non-dict target -> Check 10 (no crash)",
          any("non-object target" in e for e in mutate(
              lambda c: first_scheme(c)["targets"].append("not-a-dict"))))
    # Check 10 — a non-object ENTRY must be flagged, not crash
    check("hostile: non-dict entry -> Check 10 (no crash)",
          any("must be an object" in e for e in mutate(lambda c: c["entries"].append("not-a-dict"))))
    # Check 10 — the duplicate-key hook (the object_pairs_hook path) raises
    dup_ok = False
    try:
        json.loads('{"id": 1, "id": 2}', object_pairs_hook=_no_dupes_hook)
    except ValueError:
        dup_ok = True
    check("hostile: duplicate JSON key -> _no_dupes_hook raises", dup_ok)
    # Check 1 — a row missing 'id' (cid=None) must flag, not crash the sort (review P3 #4)
    check("hostile: missing id -> Check 1 (no sort crash)",
          any("non-empty string id" in e for e in mutate(
              lambda c: c["entries"].append({"family": "OB", "internal_name": "x",
                                             "cardinality": "unmapped", "targets": [], "rationale": "r"}))))
    # Check 6 — WACHSMUTH ref hygiene: bare dim ok, trailing colon rejected (review P3 #5)
    check("wachsmuth bare dimension ok", _ref_ok("WACHSMUTH", "logic"))
    check("wachsmuth trailing-colon rejected", not _ref_ok("WACHSMUTH", "logic:"))
    check("wachsmuth valid sub ok", _ref_ok("WACHSMUTH", "logic:LAc"))
    check("wachsmuth bad sub rejected", not _ref_ok("WACHSMUTH", "logic:ZZ"))
    check("hostile: trailing-colon wachsmuth target -> Check 6",
          any("Check 6" in e for e in mutate(
              lambda c: first_scheme(c)["targets"].__setitem__(0, {"vocab": "WACHSMUTH", "ref": "logic:",
                                               "cardinality": "related", "prov": prov("logic:")}))))

    # ---- Codex round arms (PR #200): P1 drift-binding scoping + P2/P3 hardening ----
    # P1a — parse_dc_codes must SCOPE to canonical `| Code | Name | Description |` tables; a
    # code-shaped row in an UNRELATED table must NOT be counted as a DC code.
    stray_reg = "\n".join([
        "| Support Type | Meaning |", "|----|----|",
        "| **AC5** | a support-type row that is NOT a DC code |",
        "prose gap",
        "| Code | Name | Description |", "|----|----|----|",
        "| **OB0** | a real code | x |", "| **OB1** | another | y |",
    ])
    dc_scoped = parse_dc_codes(stray_reg)
    check("P1a: stray AC5 outside a code table is NOT counted", dc_scoped == {"OB0", "OB1"})
    # P1a — a code renamed within its family (AC4->AC5) breaks the canonical contiguous set.
    check("P1a: AC4->AC5 -> Check 9 canonical-set",
          any("canonical contiguous set" in e for e in validate(
              valid, (dc_codes - {"AC4"}) | {"AC5"}, schemes, verdicts, flags, fm_max)))
    # P1b — a DUPLICATED scheme (list len 8 but 7 unique) must fail, though the set-union dedups.
    check("P1b: duplicate scheme (Sign->Authority) -> Check 9",
          any("unique scheme hints" in e for e in validate(
              valid, dc_codes, schemes[:7] + ["Authority"], verdicts, flags, fm_max)))
    check("P1b: derived-union tripwire fires at !=82",
          any("expected 82" in e for e in validate(
              valid, dc_codes, schemes[:7], verdicts, flags, fm_max)))
    # P2a — unhashable JSON scalars (a list where a string is expected) must yield a clean error, not a TypeError.
    check("P2a: list id -> clean error (no crash)",
          any("non-empty string id" in e for e in mutate(lambda c: c["entries"][0].update({"id": []}))))
    # P2a (Codex re-review) — a POPULATED row (with targets) whose id is a list must not crash
    # the per-target seen_refs set insert. entries[0] above is unmapped/no-targets, so it missed this.
    check("P2a: list id on POPULATED row -> clean error (no crash)",
          any("non-empty string id" in e for e in mutate(lambda c: first_scheme(c).update({"id": []}))))
    check("P2a: list cardinality -> clean error (no crash)",
          any("Check 3" in e for e in mutate(lambda c: c["entries"][0].update({"cardinality": []}))))
    check("P2a: list vocab -> clean error (no crash)",
          any("Check 6" in e for e in mutate(lambda c: first_scheme(c)["targets"][0].update({"vocab": []}))))
    # P2b — Walton `#CQ<n>` suffix is bounded; bare scheme ok, over-max/garbage/empty/unmapped-scheme suffix rejected.
    check("P2b: walton bare scheme ok", _ref_ok("WALTON", "Expert Opinion"))
    check("P2b: walton valid CQ2 ok", _ref_ok("WALTON", "Expert Opinion#CQ2"))
    check("P2b: walton CQ over max rejected", not _ref_ok("WALTON", "Expert Opinion#CQ999"))
    check("P2b: walton garbage suffix rejected", not _ref_ok("WALTON", "Expert Opinion#garbage"))
    check("P2b: walton empty suffix rejected", not _ref_ok("WALTON", "Expert Opinion#"))
    check("P2b: walton CQ on scheme w/o CQ map rejected", not _ref_ok("WALTON", "Practical Reasoning#CQ2"))
    check("P2b: walton bare Practical Reasoning ok", _ref_ok("WALTON", "Practical Reasoning"))
    # P3 — Check 8a requires non-empty STRING prov fields (numeric locators are unusable).
    check("P3: numeric prov -> Check 8a",
          any("Check 8a" in e for e in mutate(
              lambda c: first_scheme(c)["targets"][0].update({"prov": {"work": 1, "loc": 2, "id": 3}}))))

    concepts = [
        {"id":"R2:"+x,"kind":"objection-relation","cardinality":"unmapped","targets":[],"rationale":"stable"}
        for x in ("WARRANT-DEFEATER","CLAIM-CHALLENGE","EVIDENCE-CHALLENGE","VALUE-CONFLICT","ALTERNATIVE")
    ] + [
        {"id":"R3:"+x,"kind":"agd-move","cardinality":"narrower","targets":[{"vocab":"SF","ref":"move:"+x.lower(),"cardinality":"narrower","prov":prov("move:"+x.lower())}],"rationale":None}
        for x in ("ASSURING","GUARDING","DISCOUNTING")
    ]
    cv = {"concept_entries": concepts}
    check("R4B concepts: exact derived set passes", validate_concepts(cv, ("WARRANT-DEFEATER","CLAIM-CHALLENGE","EVIDENCE-CHALLENGE","VALUE-CONFLICT","ALTERNATIVE"), ("ASSURING","GUARDING","DISCOUNTING")) == [])
    import copy
    badc = copy.deepcopy(cv); badc["concept_entries"][5]["targets"] = [{"vocab":"AIF","ref":"RA-node","cardinality":"related","prov":prov("RA-node")}]; badc["concept_entries"][5]["cardinality"]="related"
    check("R4B concepts: AGD->AIF rejected", any("AGD moves" in e for e in validate_concepts(badc, ("WARRANT-DEFEATER","CLAIM-CHALLENGE","EVIDENCE-CHALLENGE","VALUE-CONFLICT","ALTERNATIVE"), ("ASSURING","GUARDING","DISCOUNTING"))))
    badc = copy.deepcopy(cv); badc["concept_entries"][4]["targets"] = [{"vocab":"AIF","ref":"CA-node","cardinality":"related","prov":prov("CA-node")}]; badc["concept_entries"][4]["cardinality"]="related"
    check("R4B concepts: ALTERNATIVE->AIF rejected", any("ALTERNATIVE" in e for e in validate_concepts(badc, ("WARRANT-DEFEATER","CLAIM-CHALLENGE","EVIDENCE-CHALLENGE","VALUE-CONFLICT","ALTERNATIVE"), ("ASSURING","GUARDING","DISCOUNTING"))))
    check("R4B rationales: future placeholder rejected", bool(validate_stable_rationales({"entries":[{"id":"X","cardinality":"unmapped","rationale":"revisit R4B"}]})))

    if fails:
        print("Self-test: FAIL")
        for f in fails:
            print("  - %s" % f)
        return 1
    print("Self-test: PASS (argument-crosswalk-check; structural parse + 10 checks, hostile arms)")
    return 0


def main(argv):
    if len(argv) >= 1 and argv[0] == "--self-test":
        return _selftest()
    if len(argv) >= 1 and argv[0] == "--check":
        return run_check(argv[1] if len(argv) > 1 else None)
    if len(argv) >= 1 and argv[0] == "argument-crosswalk-check":
        rest = argv[1:]
        if rest and rest[0] == "--self-test":
            return _selftest()
        if rest and rest[0] == "--check":
            rest = rest[1:]
        path = rest[0] if rest else None
        return run_check(path)
    # bare invocation: real-file check on the default crosswalk
    if not argv:
        return run_check(None)
    sys.stderr.write("Usage: argument_crosswalk.py --self-test | --check [<crosswalk.json>] | "
                     "argument-crosswalk-check [<crosswalk.json>]\n")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
