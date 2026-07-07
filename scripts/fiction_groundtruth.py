#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mechanical-honesty validator for APODICTIC Fiction Benchmark ground-truth files.

Backs `validate.sh fiction-groundtruth-check <groundtruth_file>`
(docs/fiction-benchmark-spec.md §Mechanical validator). The fiction sibling of
scripts/argument_groundtruth.py: a **mechanical-honesty layer over the answer
keys — never a semantic judge** of the engine or the fixtures.

SCOPE (honesty header — mirrors the spec's §Mechanical validator scope note):
every check below operates on **KEY TEXT ONLY** — the pre-registered
`groundtruth.md`. This validator never sees a run, never scores the engine, and
has no view of whether a finding actually landed. FQ2/FQ3/FQ6 run-fidelity,
FQ7's "no severity token attached to the device," the anti-recall / anti-seam
evidence-grounding reads, and the matched-pair delta are all HUMAN M2 rubric
work with zero mechanical backstop (the finding `mechanism` field is free text;
the schema enumerates no mechanisms). This validator only proves the *answer
key* is well-formed, lane-honest, and internally consistent.

Checks (FGT1-FGT7 keys):
  1. Section coverage. FGT1-FGT7 each covered by a heading and non-empty
     (range/list heading expansion + PROVISIONAL semantics reused from
     argument_groundtruth.py).
  2. Multi-lane tag discipline. Every in-scope FGT heading carries the five
     tags [gt_class][construct_lane][evidence_basis][decision_use]
     [reliability_status] from the §multi-lane enums. Mechanical rules:
       - gt_class:C may never carry decision_use:gate (Lane 3 never gates).
       - decision_use:gate requires reliability_status in
         {deterministic, panel_confirmed} (alpha licenses gating, not the author).
       - a consensus_alignment (Lane-2) anchor must carry a band + [alpha_metric].
  3. Defect-fixture completeness. A `broken` member (FGT2 not N/A) needs a
     non-empty plant record, a well-shaped registered locus token, a defect
     family in {POV,CONTINUITY,REVEAL,STRUCTURE}, and a `Paired-with` sibling.
     A `clean` member records "no mutation" and marks FGT2 N/A.
  4. Expected-surface shape + family consistency (the OPEN-namespace rule — a
     closed-enum port would be a defect). FGT2's Expected engine surface must
     name a surface whose shape is recognized and whose family matches the
     defect family. F-<ORIGIN>-<NN> is an OPEN namespace validated by
     shape + family-prefix; CF-<NN>/SP-<NN> are DISJOINT cross-artifact block
     ids recognized only for CONTINUITY/REVEAL. The negated/PASS decoy masks are
     ADAPTED to the fiction grammar (F-P<n>, CF-NN, SP-NN), not ported.
  5. Severity tokens. Every severity mentioned in FGT4 must be one of the three
     canonical tokens (via severity_vocab.SEVERITY_TOKEN_RE — never a local
     regex, per validator-conventions M8). A `presence-delta` FGT4 legitimately
     carries no token.
  6. FGT7 classification. One of SOUND / INTENTIONAL-AND-EFFECTIVE /
     DEFECT-AS-PLANTED (leading-token parse). Internal-consistency: a control /
     clean member (FGT2 N/A) claiming DEFECT-AS-PLANTED is an ERROR, as is a
     `broken` member claiming SOUND.

Output keeps the WARN: / ERROR: / OK: / FAILED: prefixes and exit codes
(0 ok, 1 fail, 2 usage) so it slots into --self-test-all.

CLI:
    fiction_groundtruth.py fiction-groundtruth-check <groundtruth_file>
    fiction_groundtruth.py --self-test
"""

import os
import re
import sys

# The severity leak token is the shared SSoT (validator-conventions M8): import,
# never re.compile locally. severity_vocab.py sits beside this file in both mirrors.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from severity_vocab import SEVERITY_TOKEN_RE  # noqa: E402

# --- Multi-lane tag enums (docs/fiction-benchmark-spec.md §The multi-lane schema) ----------------
_GT_CLASSES = {"A", "B", "C"}
_CONSTRUCT_LANES = {"fault_injection", "consensus_alignment", "reader_effect",
                    "editorial_preference"}
_EVIDENCE_BASES = {"planted_diff", "public_domain_control", "editor_panel",
                   "reader_study", "preference_pair"}
_DECISION_USES = {"gate", "report", "exploratory"}
_RELIABILITY = {"deterministic", "provisional_author", "panel_confirmed", "low_agreement"}
_ALPHA_METRICS = {"ordinal", "nominal"}
_GATE_OK_RELIABILITY = {"deterministic", "panel_confirmed"}

# --- Defect families + the Increment-1 open-namespace accept-set (§Check 4) -----------------------
_DEFECT_FAMILIES = {"POV", "CONTINUITY", "REVEAL", "STRUCTURE"}
# Accepted F-P<n> pass origins per defect family (Increment-1 four-family accept-set — extensible).
_FAMILY_FINDING_PASSES = {
    "POV": {"7", "5"},           # F-P7 primary; a P5 voice-mechanism finding also counts
    "CONTINUITY": {"10"},        # F-P10
    "REVEAL": {"8"},             # F-P8
    "STRUCTURE": {"0", "2", "6"},  # F-P0 / F-P2 / F-P6
}
# Cross-artifact block ids (DISJOINT namespaces) recognized only for these families.
_FAMILY_ARTIFACT = {
    "CONTINUITY": "CF",   # a continuity-bible CF-NN contradiction row
    "REVEAL": "SP",       # a setup-payoff SP-NN abandoned/open row
}

_FGT7_CLASSES = ["INTENTIONAL-AND-EFFECTIVE", "DEFECT-AS-PLANTED", "SOUND"]  # longest-first

# --- Regexes ------------------------------------------------------------------------------------
_HEADING_RE = re.compile(r"^#{1,4}\s")
# A fiction finding origin (open namespace): F-P<n> optionally -<NN>. Case per schema (F-P7-01).
_FINDING_RE = re.compile(r"\bF-P([0-9]+)(?:-([0-9]+))?\b")
# Cross-artifact block ids: CF-<NN> / SP-<NN> / PO-<NN>.
_ARTIFACT_RE = re.compile(r"\b(CF|SP|PO)-([0-9]+)\b")
# Leading verdict token of an FGT7 "Expected classification" value, skipping markdown emphasis.
_FGT7_VERDICT_RE = re.compile(r"[\s*`]*([A-Z][A-Z-]*)")
# A well-shaped locus token: a coarse chapter/scene/§/¶/line/page reference (C2 locus-shape wording,
# validate.sh continuity-bible) — a precondition, NOT a firewall proof.
_LOCUS_SHAPE_RE = re.compile(
    r"(?:\bchapter\b|\bscene\b|\bch\.?\s*\d|\bsc\.?\s*\d|§|¶|\bpara(?:graph)?\b|"
    r"\bline\b|\bpage\b|\bp\.?\s*\d|\bstave\b)", re.IGNORECASE)

# Decoy masks — ADAPTED to the fiction origin grammar (F-P<n>(-<NN>)?, CF-<NN>, SP-<NN>), NOT a
# literal port of argument_groundtruth's [A-Z]{2}[0-9]+ regex (which matches ZERO fiction origins).
# A surface named only to negate it ("not F-P7-01") or mark it passing ("F-P7-01 = PASS",
# "F-P7 (PASS)") must not satisfy a family. Both forms consume a whole grouped list so no leading
# positive token survives the mask.
_FICTION_TOKEN = r"(?:F-P[0-9]+(?:-[0-9]+)?|CF-[0-9]+|SP-[0-9]+|PO-[0-9]+)"
# Markdown emphasis chars that may wrap a token (`F-P7-01`, *F-P7-01*) — allowed between the token
# and its separator / PASS marker so `` `F-P7-01` (PASS) `` masks the same as `F-P7-01 (PASS)`.
_EMPH = r"[`*]*"
_NEGATED_SURFACE_RE = re.compile(
    r"\b[Nn][Oo][Tt]\s+" + _EMPH + r"((?:" + _FICTION_TOKEN + _EMPH + r"(?:\s*[/,]\s*" + _EMPH + r")?)+)")
_PASS_SURFACE_RE = re.compile(
    r"(?:" + _FICTION_TOKEN + _EMPH + r"\s*[/,]\s*" + _EMPH + r")*" + _FICTION_TOKEN + _EMPH +
    r"\s*(?:=\s*PASS\b|\(\s*PASS\s*\))")


def _positive_surface_text(text):
    """`text` with decoy (negated / PASS-marked) surface mentions removed, so only surfaces asserted
    as the actual expected engine surface remain for the Check-4 family-consistency check."""
    return _PASS_SURFACE_RE.sub(" ", _NEGATED_SURFACE_RE.sub(" ", text))


# --- Heading / section parsing (reused idiom from argument_groundtruth.py) ------------------------

def _fgt_numbers_in_heading(line):
    """All FGT section numbers a heading covers — a combined heading maps its body to every number,
    e.g. `## FGT4-FGT7 — *(PROVISIONAL)*` (a range) or `## FGT5 / FGT6 — …` (a list)."""
    nums = set()
    for a, b in re.findall(r"FGT([1-7])\s*[-–—]\s*(?:FGT\s*)?([1-7])", line):
        if int(a) <= int(b):
            nums.update(range(int(a), int(b) + 1))
    nums.update(int(n) for n in re.findall(r"FGT([1-7])", line))
    return sorted(nums)


def _parse_fgt_sections(text):
    """Return {n: {"heading": str, "body": str, "provisional": bool}} for each FGT<n> section."""
    sections = {}
    cur, heading, prov, buf = [], "", False, []

    def flush():
        if cur:
            body = "\n".join(buf).strip()
            for n in cur:
                sections[n] = {"heading": heading, "body": body, "provisional": prov}

    for ln in text.split("\n"):
        if _HEADING_RE.match(ln):
            nums = _fgt_numbers_in_heading(ln)
            flush()
            cur, heading, prov, buf = nums, ln, ("PROVISIONAL" in ln.upper()), []
            continue
        if cur:
            buf.append(ln)
    flush()
    return sections


# --- Multi-lane tag parsing ----------------------------------------------------------------------

def _parse_tags(block):
    """Parse the `[key: value]` tag bracket-run that trails an FGT heading (may span the heading line
    and the next line). Returns {key: [values...]} — gt_class may hold a compound `B/A` split on `/`.
    A tag may appear more than once (rare); we keep all values."""
    tags = {}
    for key, val in re.findall(r"\[\s*([a-z_]+)\s*:\s*([^\]]*?)\s*\]", block):
        vals = [v.strip() for v in val.split("/") if v.strip()] if key == "gt_class" else [val.strip()]
        tags.setdefault(key, [])
        tags[key].extend(vals)
    return tags


def _tag_head_region(section):
    """The text the tags live in: the heading line + the section body's first two lines (the template
    puts the tag run on the line immediately under the heading)."""
    body_head = "\n".join(section["body"].split("\n")[:2])
    return section["heading"] + "\n" + body_head


# --- The check ----------------------------------------------------------------------------------

def _provenance_field(text, label):
    """Value of a `- **<label>:** value` provenance line (first match), else ''."""
    m = re.search(r"\*\*\s*%s\s*:?\s*\*\*\s*(.+)" % re.escape(label), text)
    return m.group(1).strip() if m else ""


def fiction_groundtruth_check(text):
    errors, warnings = [], []
    sections = _parse_fgt_sections(text)

    # Provenance signals that drive control/clean exemptions and the broken-member requirements.
    member = _provenance_field(text, "Matched-pair member").lower()
    is_broken = "broken" in member
    is_clean = "clean" in member
    is_standalone = ("standalone" in member) or ("n/a" in member and not is_broken and not is_clean)

    # Check 1: FGT1-FGT7 each covered by a heading (combined headings OK) + non-empty.
    for n in range(1, 8):
        sec = sections.get(n)
        if sec is None:
            errors.append("Check 1 (sections) — FGT%d not covered by any heading." % n)
        elif not sec["body"].strip():
            errors.append("Check 1 (sections) — FGT%d section is empty." % n)

    # Check 2: multi-lane tag discipline (per FGT section present).
    for n in range(1, 8):
        sec = sections.get(n)
        if sec is None or not sec["body"].strip():
            continue
        region = _tag_head_region(sec)
        tags = _parse_tags(region)
        # A control / clean member may mark whole anchors N/A (positive control) — those carry no tags.
        body_upper = sec["body"].upper()
        if re.search(r"\bN/?A\b", region) and "N/A" in body_upper and not tags.get("gt_class"):
            continue
        missing = [k for k in ("gt_class", "construct_lane", "evidence_basis",
                               "decision_use", "reliability_status") if not tags.get(k)]
        if missing:
            errors.append("Check 2 (tags) — FGT%d missing tag(s): %s." % (n, ", ".join(missing)))
            continue
        gt_classes = tags["gt_class"]
        lanes = tags["construct_lane"]
        uses = tags["decision_use"]
        rels = tags["reliability_status"]
        for v, allowed, name in ((gt_classes, _GT_CLASSES, "gt_class"),
                                 (lanes, _CONSTRUCT_LANES, "construct_lane"),
                                 (tags["evidence_basis"], _EVIDENCE_BASES, "evidence_basis"),
                                 (uses, _DECISION_USES, "decision_use"),
                                 (rels, _RELIABILITY, "reliability_status")):
            for one in v:
                if one not in allowed:
                    errors.append("Check 2 (tags) — FGT%d %s value %r not in the enum." % (n, name, one))
        # gt_class:C may never gate (Lane 3 never gates — the one-line architecture guardrail).
        if "C" in gt_classes and "gate" in uses:
            errors.append("Check 2 (tags) — FGT%d is gt_class:C but carries decision_use:gate "
                          "(Lane 3 never gates)." % n)
        # decision_use:gate requires a deterministic/panel_confirmed reliability (alpha licenses gating).
        if "gate" in uses and not any(r in _GATE_OK_RELIABILITY for r in rels):
            errors.append("Check 2 (tags) — FGT%d claims decision_use:gate with reliability_status %s "
                          "(gate requires deterministic or panel_confirmed — alpha licenses gating, "
                          "not the author)." % (n, "/".join(rels)))
        # A Lane-2 (consensus_alignment) anchor must carry a band + an alpha_metric.
        if "consensus_alignment" in lanes:
            am = tags.get("alpha_metric", [])
            if not am:
                errors.append("Check 2 (tags) — FGT%d is consensus_alignment (Lane-2) but has no "
                              "[alpha_metric: ordinal|nominal] tag (a point-answer Lane-2 key is the "
                              "false-authority failure this spec exists to prevent)." % n)
            elif any(a not in _ALPHA_METRICS for a in am):
                errors.append("Check 2 (tags) — FGT%d alpha_metric value %s not ordinal|nominal."
                              % (n, "/".join(am)))
            if not re.search(r"\bband\b", sec["body"], re.IGNORECASE):
                errors.append("Check 2 (tags) — FGT%d is consensus_alignment (Lane-2) but its body "
                              "names no 'band' (a Lane-2 anchor must be banded, not a point answer)." % n)

    # --- FGT2 defect family + surface (used by checks 3 and 4) ---
    fgt2 = sections.get(2, {}).get("body", "")
    fgt2_na = bool(re.search(r"\bN/?A\b", fgt2)) and not re.search(r"POV|CONTINUITY|REVEAL|STRUCTURE", fgt2)
    family_m = re.search(r"\*\*\s*Defect family\s*:?\s*\*\*\s*([A-Za-z/ ]+)", fgt2)
    family = ""
    if family_m:
        for f in re.findall(r"POV|CONTINUITY|REVEAL|STRUCTURE", family_m.group(1).upper()):
            family = f
            break

    # Check 3: defect-fixture completeness (broken member) / control exemption (clean member).
    if is_broken:
        plant = _provenance_field(text, "Base text + plant record")
        if not plant or plant.upper().startswith("N/A") or "no mutation" in plant.lower():
            errors.append("Check 3 (completeness) — `broken` member has no plant record in Provenance "
                          "(Base text + plant record).")
        paired = _provenance_field(text, "Paired-with")
        if not paired or paired.lower().startswith("n/a"):
            errors.append("Check 3 (completeness) — `broken` member has no `Paired-with` sibling "
                          "(D-1: no unpaired derived-broken fixture in the slice).")
        if fgt2_na:
            errors.append("Check 3 (completeness) — `broken` member marks FGT2 N/A (a broken member "
                          "must register a planted defect locus).")
        else:
            if family not in _DEFECT_FAMILIES:
                errors.append("Check 3 (completeness) — FGT2 Defect family is not one of "
                              "POV/CONTINUITY/REVEAL/STRUCTURE.")
            loci = ""
            lm = re.search(r"\*\*\s*Registered loci\s*:?\s*\*\*\s*(.+)", fgt2)
            if lm:
                loci = lm.group(1)
            if not _LOCUS_SHAPE_RE.search(loci):
                errors.append("Check 3 (completeness) — FGT2 Registered loci carries no well-shaped "
                              "locus token (chapter/scene/§/¶/line/page — a precondition, not a "
                              "firewall proof).")
    elif is_clean:
        plant = _provenance_field(text, "Base text + plant record")
        if plant and "no mutation" not in plant.lower():
            warnings.append("Check 3 (completeness) — `clean` member should record 'no mutation' in "
                            "its plant-record field (it is the control).")
        if not fgt2_na:
            errors.append("Check 3 (completeness) — `clean` member must mark FGT2 `N/A` (it is the "
                          "positive control, no planted defect to locate).")

    # Check 4: expected-surface shape + family consistency (OPEN-namespace rule).
    # Only meaningful when a defect family is registered (broken members; standalone controls exempt).
    if family in _DEFECT_FAMILIES and not fgt2_na:
        surface_line = ""
        sm = re.search(r"\*\*\s*Expected engine surface\s*:?\s*\*\*\s*(.+(?:\n(?!\s*[-*]|#).+)*)", fgt2)
        if sm:
            surface_line = sm.group(1)
        pos = _positive_surface_text(surface_line)
        finding_hits = _FINDING_RE.findall(pos)          # [(n, nn), ...] passes asserted
        artifact_hits = _ARTIFACT_RE.findall(pos)        # [(kind, nn), ...]
        ok_passes = _FAMILY_FINDING_PASSES.get(family, set())
        finding_ok = any(n in ok_passes for (n, _nn) in finding_hits)
        art_kind = _FAMILY_ARTIFACT.get(family)          # 'CF' / 'SP' / None
        artifact_ok = bool(art_kind) and any(k == art_kind for (k, _nn) in artifact_hits)
        # A wrong-family artifact (e.g. CF on a POV key) is a positive assertion that must NOT satisfy.
        wrong_artifact = any(k in ("CF", "SP") and k != art_kind for (k, _nn) in artifact_hits)
        if not surface_line.strip():
            errors.append("Check 4 (surface) — FGT2 has no `Expected engine surface`.")
        elif not (finding_ok or artifact_ok):
            expect = "F-P" + "/".join(sorted(ok_passes)) + "-<NN>"
            if art_kind:
                expect += " or a %s-<NN> row" % art_kind
            errors.append("Check 4 (surface) — FGT2 defect family %s names no matching surface "
                          "(expected %s); asserted surfaces resolve to none of them." % (family, expect))
        elif wrong_artifact and not finding_ok and not artifact_ok:
            errors.append("Check 4 (surface) — FGT2 family %s names a cross-artifact row from the "
                          "wrong namespace." % family)

    # Check 5: severity tokens (FGT4) — via the shared SSoT, never a local regex (M8).
    fgt4 = sections.get(4, {}).get("body", "")
    if fgt4.strip():
        is_presence_delta = bool(re.search(r"presence[- ]delta", fgt4, re.IGNORECASE))
        # Any capitalized `<Word>-Fix` token that is NOT one of the three canonical severities is bad.
        for m in re.finditer(r"\b([A-Z][a-z]+)-Fix\b", fgt4):
            if not SEVERITY_TOKEN_RE.match(m.group(0)):
                errors.append("Check 5 (severity) — FGT4 names a non-canonical severity token %r "
                              "(canonical: Must-Fix / Should-Fix / Could-Fix)." % m.group(0))
        canonical = SEVERITY_TOKEN_RE.findall(fgt4) if hasattr(SEVERITY_TOKEN_RE, "findall") else []
        # SEVERITY_TOKEN_RE has no capture group -> findall returns the whole matches; count via finditer.
        canonical_count = len(list(SEVERITY_TOKEN_RE.finditer(fgt4)))
        if canonical_count == 0 and not is_presence_delta:
            warnings.append("Check 5 (severity) — FGT4 names no canonical severity token and is not "
                            "marked `presence-delta`; a Lane-1 severity band should state a token or "
                            "declare the severity-free presence-delta regime.")

    # Check 6: FGT7 classification (leading-token parse) + internal consistency.
    fgt7 = sections.get(7, {}).get("body", "")
    m = re.search(r"\*\*\s*Expected classification\s*:?\s*\*\*\s*(.+)", fgt7)
    if m:
        cls_line = m.group(1)
        vm = _FGT7_VERDICT_RE.match(cls_line)
        verdict = vm.group(1) if vm else ""
        cls = verdict if verdict in _FGT7_CLASSES else None
        if cls is None:
            errors.append("Check 6 (FGT7) — classification is not one of SOUND / "
                          "INTENTIONAL-AND-EFFECTIVE / DEFECT-AS-PLANTED (got %r)." % cls_line.strip())
        else:
            if cls == "INTENTIONAL-AND-EFFECTIVE":
                # Must name the device and the trap.
                names_device = bool(re.search(r"\bdevice\b", fgt7, re.IGNORECASE))
                names_trap = bool(re.search(r"\btrap\b", fgt7, re.IGNORECASE))
                if not (names_device and names_trap):
                    errors.append("Check 6 (FGT7) — INTENTIONAL-AND-EFFECTIVE must name the device and "
                                  "the false-positive trap; FGT7 names %s."
                                  % ("neither" if not (names_device or names_trap)
                                     else ("no device" if not names_device else "no trap")))
            # Internal consistency vs the fixture role.
            if (is_clean or is_standalone or fgt2_na) and cls == "DEFECT-AS-PLANTED":
                errors.append("Check 6 (FGT7) — a control / clean member (FGT2 N/A) cannot classify "
                              "FGT7 DEFECT-AS-PLANTED (there is no planted defect).")
            if is_broken and cls == "SOUND":
                errors.append("Check 6 (FGT7) — a `broken` member cannot classify FGT7 SOUND "
                              "(it carries a planted defect).")

    ok = ("OK: Fiction ground-truth contract satisfied (FGT1-FGT7 present; lane tags honest; "
          "surface shape/family consistent).")
    failed = ("FAILED: %d fiction-groundtruth-check failure(s). Canonical home: "
              "docs/fiction-benchmark-spec.md §Mechanical validator + "
              "evals/fiction-groundtruth-template.md." % len(errors))
    return errors, warnings, ok, failed


def _emit(errors, warnings, ok_line, failed_line):
    for w in warnings:
        print(w)
    for e in errors:
        print(e)
    if errors:
        print("")
        print(failed_line)
        return 1
    print(ok_line)
    return 0


# --------------------------------------------------------------------------
# Self-test (hermetic — built-in valid + hostile ground-truth fixtures).
# --------------------------------------------------------------------------

_VALID_BROKEN = """# Ground Truth: pov-break-broken

## Provenance
- **Fixture slug:** pov-break/broken · **Bucket:** P · **Source class:** synthetic-or-derived
- **Matched-pair member:** broken
- **Paired-with:** pov-break/clean
- **Text stored in-repo?:** yes
- **Base text + plant record:** base = low-recognition PD short story; planted 2 head-hops + 1
  POV-knowledge leak at ¶18, ¶24, ¶31 (before->after recorded).
- **Registered (date):** 2026-07-06

## FGT1 — Structure recovery *(FQ1)*
   [gt_class: B/A][construct_lane: consensus_alignment][evidence_basis: editor_panel][decision_use: report][reliability_status: provisional_author][alpha_metric: ordinal]
- **Expected scene inventory:** 5 scenes (agreement band: ±1 split/merge)
- **Expected act/movement boundaries:** loci + band (± one scene)

## FGT2 — Planted defect locus *(FQ2)*
   [gt_class: A][construct_lane: fault_injection][evidence_basis: planted_diff][decision_use: gate][reliability_status: deterministic]
- **Defect family:** POV
- **Registered loci:** ¶18, ¶24, ¶31
- **Expected engine surface:** `F-P7-01` (perspective slip). Not F-P10-01.

## FGT3 — Mechanism discrimination *(FQ3)*
   [gt_class: A][construct_lane: fault_injection][evidence_basis: planted_diff][decision_use: gate][reliability_status: deterministic][alpha_metric: nominal]
- **Expected mechanism family:** POV break, not a voice-drift style issue.

## FGT4 — Severity band *(FQ4)*
   [gt_class: A][construct_lane: fault_injection][evidence_basis: planted_diff][decision_use: gate][reliability_status: deterministic]
- **Expected severity band:** Must-Fix..Should-Fix.
- **Clean-member over-fire ceiling:** 0 Must-Fix on the POV mechanism.

## FGT5 — Arc recovery *(FQ5)*
   [gt_class: B][construct_lane: consensus_alignment][evidence_basis: editor_panel][decision_use: report][reliability_status: provisional_author][alpha_metric: ordinal]
- **Gross arc shape band:** N/A — not scored (not the arc pilot).

## FGT6 — Repair target *(FQ6)*
   [gt_class: A][construct_lane: fault_injection][evidence_basis: planted_diff][decision_use: gate][reliability_status: deterministic]
- **Correct first repair target:** restore single-POV discipline at the three loci.

## FGT7 — Form fairness *(FQ7)*
   [gt_class: A][construct_lane: fault_injection][evidence_basis: public_domain_control][decision_use: gate][reliability_status: deterministic]
- **Expected classification:** DEFECT-AS-PLANTED
- **False-positive trap:** N/A — scored on the clean member.

## Notes
free-form.
"""

_VALID_CLEAN = """# Ground Truth: pov-break-clean

## Provenance
- **Fixture slug:** pov-break/clean · **Bucket:** P · **Source class:** synthetic-or-derived
- **Matched-pair member:** clean
- **Paired-with:** pov-break/broken
- **Text stored in-repo?:** yes
- **Base text + plant record:** no mutation — this IS the control.
- **Registered (date):** 2026-07-06

## FGT1 — Structure recovery *(FQ1)*
   [gt_class: B/A][construct_lane: consensus_alignment][evidence_basis: editor_panel][decision_use: report][reliability_status: provisional_author][alpha_metric: ordinal]
- **Expected scene inventory:** 5 scenes (agreement band: ±1 split/merge)

## FGT2 — Planted defect locus *(FQ2)*
- **N/A — positive control.** No planted defect.

## FGT3 — Mechanism discrimination *(FQ3)*
- **N/A — positive control.**

## FGT4 — Severity band *(FQ4)*
- **N/A — positive control.** No plant to score; over-fire ceiling 0 Must-Fix.

## FGT5 — Arc recovery *(FQ5)*
   [gt_class: B][construct_lane: consensus_alignment][evidence_basis: editor_panel][decision_use: report][reliability_status: provisional_author][alpha_metric: ordinal]
- **Gross arc shape band:** N/A — not scored.

## FGT6 — Repair target *(FQ6)*
- **N/A — positive control.**

## FGT7 — Form fairness *(FQ7)*
   [gt_class: A][construct_lane: fault_injection][evidence_basis: public_domain_control][decision_use: gate][reliability_status: deterministic]
- **Expected classification:** SOUND
- **False-positive trap:** a naive Pass 7 distance-inconsistency Must-Fix on intact POV discipline.

## Notes
control member of the pov-break pair.
"""

_VALID_CONTINUITY_CF = """# Ground Truth: continuity-contradiction-broken

## Provenance
- **Fixture slug:** continuity-contradiction/broken · **Bucket:** C · **Source class:** synthetic-or-derived
- **Matched-pair member:** broken
- **Paired-with:** continuity-contradiction/clean
- **Base text + plant record:** base = low-recognition PD base; dual-mutated an entity fact at ch.2
  and ch.7 to novel conflicting values + one timeline-arithmetic error.
- **Registered (date):** 2026-07-06

## FGT1 — Structure recovery *(FQ1)*
   [gt_class: A][construct_lane: fault_injection][evidence_basis: planted_diff][decision_use: report][reliability_status: deterministic]
- **Expected scene inventory:** 6 scenes.

## FGT2 — Planted defect locus *(FQ2)*
   [gt_class: A][construct_lane: fault_injection][evidence_basis: planted_diff][decision_use: gate][reliability_status: deterministic]
- **Defect family:** CONTINUITY
- **Registered loci:** chapter 2 and chapter 7.
- **Expected engine surface:** a continuity-bible `CF-04` contradiction row (no F-<ORIGIN> required).

## FGT3 — Mechanism discrimination *(FQ3)*
   [gt_class: A][construct_lane: fault_injection][evidence_basis: planted_diff][decision_use: gate][reliability_status: deterministic][alpha_metric: nominal]
- **Expected mechanism family:** continuity contradiction, not a reveal-economy error.

## FGT4 — Severity band *(FQ4)*
   [gt_class: A][construct_lane: fault_injection][evidence_basis: planted_diff][decision_use: gate][reliability_status: deterministic]
- **Severity-free plant handling:** presence-delta — the CF-04 row present in broken, absent in clean.

## FGT5 — Arc recovery *(FQ5)*
   [gt_class: B][construct_lane: consensus_alignment][evidence_basis: editor_panel][decision_use: report][reliability_status: provisional_author][alpha_metric: ordinal]
- **Gross arc shape band:** N/A — not scored.

## FGT6 — Repair target *(FQ6)*
   [gt_class: A][construct_lane: fault_injection][evidence_basis: planted_diff][decision_use: gate][reliability_status: deterministic]
- **Correct first repair target:** locate the contradiction, then choose which fact wins.

## FGT7 — Form fairness *(FQ7)*
   [gt_class: A][construct_lane: fault_injection][evidence_basis: public_domain_control][decision_use: gate][reliability_status: deterministic]
- **Expected classification:** DEFECT-AS-PLANTED
- **False-positive trap:** N/A — scored on the clean member.

## Notes
CF-only surface is conformant for continuity.
"""

_VALID_CONTROL = """# Ground Truth: yellow-wallpaper-voice-control

## Provenance
- **Fixture slug:** yellow-wallpaper-voice-control · **Bucket:** P (+S) · **Source class:** public-domain
- **Matched-pair member:** n/a (standalone control)
- **Paired-with:** n/a
- **Text stored in-repo?:** yes
- **Registered (date):** 2026-07-06

## FGT1 — Structure recovery *(FQ1)*
   [gt_class: A][construct_lane: fault_injection][evidence_basis: public_domain_control][decision_use: report][reliability_status: deterministic]
- **Expected scene inventory:** journal entries as scene units.

## FGT2 — Planted defect locus *(FQ2)*
- **N/A — positive control.** No planted defect.

## FGT3 — Mechanism discrimination *(FQ3)*
- **N/A — positive control.**

## FGT4 — Severity band *(FQ4)*
- **N/A — positive control.**

## FGT5 — Arc recovery *(FQ5)*
   [gt_class: B][construct_lane: consensus_alignment][evidence_basis: editor_panel][decision_use: report][reliability_status: provisional_author][alpha_metric: ordinal]
- **Gross arc shape band:** N/A — not scored.

## FGT6 — Repair target *(FQ6)*
- **N/A — positive control.**

## FGT7 — Form fairness *(FQ7)*
   [gt_class: A][construct_lane: fault_injection][evidence_basis: public_domain_control][decision_use: gate][reliability_status: deterministic]
- **Expected classification:** INTENTIONAL-AND-EFFECTIVE
- **If intentional:** the device is a deliberately deteriorating unreliable first-person narrator.
- **False-positive trap:** a naive Pass 5 voice-drift Must-Fix on the intentional deterioration.

## Notes
recognition-flagged control.
"""


def run_self_test(which=None):
    rc = {"v": 0}

    def check(name, errs, expect_clean):
        ok = (len(errs) == 0) == expect_clean
        print("  %s: %s" % (name, "OK" if ok else "FAIL (errs=%s)" % errs))
        if not ok:
            rc["v"] = 1

    def errs_of(text):
        return fiction_groundtruth_check(text)[0]

    # Arm 1: valid broken + valid clean + valid CF-only continuity + valid control -> all clean.
    check("valid_broken", errs_of(_VALID_BROKEN), True)
    check("valid_clean", errs_of(_VALID_CLEAN), True)
    check("valid_continuity_cf_only", errs_of(_VALID_CONTINUITY_CF), True)
    check("valid_control", errs_of(_VALID_CONTROL), True)

    # Arm 2: missing / empty FGT section (check 1).
    check("missing_section", errs_of(_VALID_BROKEN.replace(
        "## FGT5 — Arc recovery *(FQ5)*\n"
        "   [gt_class: B][construct_lane: consensus_alignment][evidence_basis: editor_panel][decision_use: report][reliability_status: provisional_author][alpha_metric: ordinal]\n"
        "- **Gross arc shape band:** N/A — not scored (not the arc pilot).\n", "")), False)
    check("empty_section", errs_of(_VALID_BROKEN.replace(
        "   [gt_class: A][construct_lane: fault_injection][evidence_basis: planted_diff][decision_use: gate][reliability_status: deterministic][alpha_metric: nominal]\n"
        "- **Expected mechanism family:** POV break, not a voice-drift style issue.\n", "")), False)

    # Arm 3: gt_class:C carrying decision_use:gate (check 2 — the architecture guardrail).
    check("classC_gates", errs_of(_VALID_BROKEN.replace(
        "[gt_class: A][construct_lane: fault_injection][evidence_basis: planted_diff][decision_use: gate][reliability_status: deterministic]\n- **Defect family:** POV",
        "[gt_class: C][construct_lane: reader_effect][evidence_basis: reader_study][decision_use: gate][reliability_status: low_agreement]\n- **Defect family:** POV")), False)

    # Arm 4: decision_use:gate with provisional_author (check 2 — alpha licenses gating, not the author).
    check("gate_provisional", errs_of(_VALID_BROKEN.replace(
        "[gt_class: A][construct_lane: fault_injection][evidence_basis: planted_diff][decision_use: gate][reliability_status: deterministic]\n- **Defect family:** POV",
        "[gt_class: A][construct_lane: fault_injection][evidence_basis: planted_diff][decision_use: gate][reliability_status: provisional_author]\n- **Defect family:** POV")), False)

    # Arm 5: Lane-2 anchor with a point answer, no band -> FAIL; and missing alpha_metric -> FAIL.
    check("lane2_no_band", errs_of(_VALID_BROKEN.replace(
        "- **Expected scene inventory:** 5 scenes (agreement band: ±1 split/merge)\n"
        "- **Expected act/movement boundaries:** loci + band (± one scene)",
        "- **Expected scene inventory:** exactly 5 scenes.")), False)
    check("lane2_no_alpha", errs_of(_VALID_BROKEN.replace(
        "[gt_class: B/A][construct_lane: consensus_alignment][evidence_basis: editor_panel][decision_use: report][reliability_status: provisional_author][alpha_metric: ordinal]",
        "[gt_class: B/A][construct_lane: consensus_alignment][evidence_basis: editor_panel][decision_use: report][reliability_status: provisional_author]")), False)

    # Arm 6: broken member with no plant record (check 3); with no Paired-with (check 3, D-1).
    check("broken_no_plant", errs_of(_VALID_BROKEN.replace(
        "- **Base text + plant record:** base = low-recognition PD short story; planted 2 head-hops + 1\n"
        "  POV-knowledge leak at ¶18, ¶24, ¶31 (before->after recorded).",
        "- **Base text + plant record:** N/A")), False)
    check("broken_no_paired", errs_of(_VALID_BROKEN.replace(
        "- **Paired-with:** pov-break/clean", "- **Paired-with:** n/a")), False)

    # Arm 7: malformed locus token (no chapter/scene/¶ shape) -> FAIL (check 3).
    check("malformed_locus", errs_of(_VALID_BROKEN.replace(
        "- **Registered loci:** ¶18, ¶24, ¶31", "- **Registered loci:** somewhere near the middle")), False)

    # Arm 8: POV family with F-P10 surface (family mismatch) -> FAIL (check 4).
    check("pov_family_mismatch", errs_of(_VALID_BROKEN.replace(
        "- **Expected engine surface:** `F-P7-01` (perspective slip). Not F-P10-01.",
        "- **Expected engine surface:** `F-P10-01` (mis-keyed).")), False)

    # Arm 9: fiction-shaped decoy — the only asserted POV surface is a decoy F-P7-01 (PASS) / not
    # F-P7-01, with the actually-asserted surface F-P10-02 (wrong family) -> FAIL (check 4). A literal
    # argument-regex port would let this pass (that is the bug the adaptation fixes).
    check("fiction_decoy_mask", errs_of(_VALID_BROKEN.replace(
        "- **Expected engine surface:** `F-P7-01` (perspective slip). Not F-P10-01.",
        "- **Expected engine surface:** `F-P7-01` (PASS); not F-P7-02; actually `F-P10-02`.")), False)

    # Arm 10: CONTINUITY key whose expected surface is a bare CF-04 (no finding) -> clean; a POV key
    # whose only surface is CF-04 -> FAIL (check 4 — CF recognized only for continuity/reveal).
    check("continuity_cf_only_clean", errs_of(_VALID_CONTINUITY_CF), True)
    check("pov_cf_only_fail", errs_of(_VALID_BROKEN.replace(
        "- **Expected engine surface:** `F-P7-01` (perspective slip). Not F-P10-01.",
        "- **Expected engine surface:** a `CF-04` row.")), False)

    # Arm 11: non-canonical severity token (check 5); a presence-delta FGT4 with no token -> clean.
    check("bad_severity_token", errs_of(_VALID_BROKEN.replace(
        "- **Expected severity band:** Must-Fix..Should-Fix.",
        "- **Expected severity band:** Critical-Fix..Should-Fix.")), False)
    check("presence_delta_no_token_clean", errs_of(_VALID_CONTINUITY_CF), True)

    # Arm 12: FGT7 out of enum (check 6); SOUND glossed "…, not DEFECT-AS-PLANTED" -> clean; a
    # control (FGT2 N/A) whose FGT7 says DEFECT-AS-PLANTED -> FAIL; a control N/A on FGT2/3/6 -> clean.
    check("fgt7_out_of_enum", errs_of(_VALID_BROKEN.replace(
        "- **Expected classification:** DEFECT-AS-PLANTED", "- **Expected classification:** BROKEN")), False)
    check("fgt7_sound_gloss_clean", errs_of(_VALID_CLEAN.replace(
        "- **Expected classification:** SOUND",
        "- **Expected classification:** SOUND — intact discipline, not DEFECT-AS-PLANTED")), True)
    check("control_defect_as_planted_fail", errs_of(_VALID_CONTROL.replace(
        "- **Expected classification:** INTENTIONAL-AND-EFFECTIVE",
        "- **Expected classification:** DEFECT-AS-PLANTED")), False)
    check("broken_sound_fail", errs_of(_VALID_BROKEN.replace(
        "- **Expected classification:** DEFECT-AS-PLANTED", "- **Expected classification:** SOUND")), False)
    check("control_na_exemption_clean", errs_of(_VALID_CONTROL), True)

    print("Self-test: %s" % ("PASS" if rc["v"] == 0 else "FAIL"))
    return rc["v"]


def main(argv):
    if len(argv) < 2:
        sys.stderr.write("Usage: fiction_groundtruth.py fiction-groundtruth-check <file> | --self-test\n")
        return 2
    if argv[1] == "--self-test":
        return run_self_test()
    if argv[1] == "fiction-groundtruth-check":
        if len(argv) < 3:
            sys.stderr.write("Usage: fiction_groundtruth.py fiction-groundtruth-check <groundtruth_file>\n")
            return 2
        if not os.path.isfile(argv[2]):
            sys.stderr.write("Error: File not found: %s\n" % argv[2])
            return 2
        with open(argv[2], "r", encoding="utf-8", errors="replace") as fh:
            return _emit(*fiction_groundtruth_check(fh.read()))
    sys.stderr.write("Error: unknown command: %s\n" % argv[1])
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
