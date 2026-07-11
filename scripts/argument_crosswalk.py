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

SF_REFS = {
    "family:vagueness", "family:ambiguity", "family:relevance", "family:vacuity",
    "refutation:premise", "refutation:conclusion", "refutation:inference", "refutation:begging",
    "standard:validity", "standard:strength", "standard:soundness",
}

WACHSMUTH_SUB = {
    "logic": {"LAc", "LRe", "LSu"},
    "rhetoric": {"arrangement", "appropriateness", "clarity", "credibility", "emotional-appeal"},
    "dialectic": {"GAc", "GRe", "GSu", "reasonableness"},
}

VOCABS = {"AIF", "WALTON", "SF", "WACHSMUTH"}
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
_SCHEME_HEADER_RE = re.compile(r"^\|\s*Scheme Hint\s*\|", re.IGNORECASE)
_TABLE_CELL1_BOLD_RE = re.compile(r"^\|\s*\*\*([^*|]+?)\*\*\s*\|")


def parse_dc_codes(registry_text):
    """Structural: DC code = a bolded leaf token at a table-row start. Returns a set."""
    codes = set()
    for line in registry_text.splitlines():
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
        scheme = ref.split("#", 1)[0]
        return scheme in WALTON_SCHEMES
    if vocab == "SF":
        return ref in SF_REFS
    if vocab == "WACHSMUTH":
        if ":" not in ref:
            return ref in WACHSMUTH_SUB          # bare dimension (logic|rhetoric|dialectic)
        dim, _, sub = ref.partition(":")
        if dim not in WACHSMUTH_SUB:
            return False
        return sub in WACHSMUTH_SUB[dim]         # a trailing colon with empty sub is rejected
    return False


# --------------------------------------------------------------------------
# Core validation
# --------------------------------------------------------------------------
def validate(cross, dc_codes, schemes, verdicts, flags, fm_max):
    """Returns a list of error strings ([] == clean). Pure over its inputs."""
    errors = []
    if not isinstance(cross, dict) or not isinstance(cross.get("entries"), list):
        return ["Check 10 (JSON hygiene) — top-level must be an object with an 'entries' list."]
    entries = cross["entries"]
    derived = derived_id_set(dc_codes, schemes, verdicts, flags, fm_max)

    # Check 1 — membership completeness (against the DERIVED set)
    ids = []
    for r in entries:
        cid = r.get("id") if isinstance(r, dict) else None
        ids.append(cid)
        if not isinstance(cid, str) or not cid.strip():
            errors.append("Check 1 (membership) — every entry needs a non-empty string id (got %r)." % cid)
            continue
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
        cid = r.get("id", "<no-id>")
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

        # Check 3 — cardinality enum (row)
        if card not in ROW_CARDS:
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
                present = [tt.get("cardinality") for tt in targets if tt.get("cardinality") in _CARD_PREC]
                if present:
                    strongest = max(present, key=lambda c: _CARD_PREC[c])
                    if card != strongest:
                        errors.append("Check 4 (roll-up) — id %r row cardinality %r != strongest target %r."
                                      % (cid, card, strongest))

        # Per-target checks (6, 8a) + ref hit accounting (8b)
        for tt in targets:
            vocab = tt.get("vocab")
            ref = tt.get("ref")
            tcard = tt.get("cardinality")
            prov = tt.get("prov")
            if tcard not in TARGET_CARDS:
                errors.append("Check 3 (cardinality) — id %r target cardinality %r not in target enum." % (cid, tcard))
            # Check 6 — target well-formedness
            if vocab not in VOCABS:
                errors.append("Check 6 (target) — id %r target vocab %r not in {AIF,WALTON,SF,WACHSMUTH}." % (cid, vocab))
            elif not (isinstance(ref, str) and _ref_ok(vocab, ref)):
                errors.append("Check 6 (target) — id %r %s ref %r outside the closed value-space." % (cid, vocab, ref))
            # Check 8a — provenance locator present
            if not (isinstance(prov, dict) and prov.get("work") and prov.get("loc") and prov.get("id")):
                errors.append("Check 8a (provenance) — id %r target (%s %r) lacks a full prov {work,loc,id}." % (cid, vocab, ref))
            if vocab in VOCABS and isinstance(ref, str):
                seen_refs.setdefault((vocab, ref), set()).add(cid)

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

    # Check 9 — count tripwires (guard the source docs' stale self-counts)
    if len(dc_codes) != 46:
        errors.append("Check 9 (tripwire) — derived DC code count is %d, expected 46 "
                      "(registry header's stale '45' must not propagate)." % len(dc_codes))
    if "OB5" not in dc_codes:
        errors.append("Check 9 (tripwire) — OB5 (Decoy strongest objection) missing from the derived DC set.")
    for fam, n in DC_FAMILY_COUNTS.items():
        got = sum(1 for c in dc_codes if c[:2] == fam)
        if got != n:
            errors.append("Check 9 (tripwire) — DC family %s has %d codes, expected %d." % (fam, got, n))
    if fm_max != 20:
        errors.append("Check 9 (tripwire) — _FM_A_MAX is %r, expected 20 (intro's stale 'nineteen' must not propagate)." % fm_max)
    if "FM-A20" not in derived:
        errors.append("Check 9 (tripwire) — FM-A20 (Self-Undermining Remedy) missing from the derived set.")
    if len(schemes) != 8:
        errors.append("Check 9 (tripwire) — derived scheme-hint count is %d, expected 8." % len(schemes))

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
    return list(_GT7_CLASSES), set(_GT8_ROW_FLAG_TYPES), int(_FM_A_MAX)


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
        verdicts, flags, fm_max = _load_owners()
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
    if errors:
        print("argument-crosswalk-check: FAIL (%d)" % len(errors))
        for e in errors:
            print("  - %s" % e)
        return 1
    n = len(cross["entries"])
    unmapped = sum(1 for r in cross["entries"] if r.get("cardinality") == "unmapped")
    print("argument-crosswalk-check: PASS — %d entries (%d populated, %d unmapped); "
          "derived set 46 DC + %d FM-A + %d schemes + %d verdicts + %d flags."
          % (n, n - unmapped, unmapped, fm_max, len(schemes), len(verdicts), len(flags)))
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

    valid = {"version": "0.1.0", "entries": full_entries(dc_codes, schemes, verdicts, flags)}
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
          any("scheme-hint count" in e for e in validate(
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
