#!/usr/bin/env python3
"""Validate argument-register / rhetorical-stance calibration records.

This is a shape-and-join gate. It never decides whether a rhetorical move is earned.

  stance_calibration.py stance-calibration <ledger.md> --argument-state <Argument_State.md>
  stance_calibration.py --self-test
"""
import re
import sys
from pathlib import Path

try:
    import apodictic_artifacts as art
except ImportError:
    art = None

from argument_groundtruth import _GT8_ROW_FLAG_TYPES as _PREMISE_FLAG_MECHANISMS


_REGISTER_RE = re.compile(r"^Register:\s*(asserted|generative)\s*$", re.MULTILINE)
_CONFIRM_RE = re.compile(
    r"^Register confirmation:\s*(DEFAULT-ASSERTED|WRITER-CONFIRMED|FORCED-ASSERTED)\s*$",
    re.MULTILINE,
)
_HIGH_RE = re.compile(
    r"^High-stakes gate:\s*(ACTIVE|INACTIVE)\s+[—-]\s*(\S.*)$", re.MULTILINE
)
_CO_ROW_RE = re.compile(
    r"^\s*-\s*(CO[1-9][0-9]*)\s*\|\s*Location:\s*(\S.*?)\s*\|\s*"
    r"Kind:\s*(ASSERTION|PRESCRIPTION)\s*\|\s*Press:\s*(LIGHT|MEDIUM|HARD)\s*\|\s*"
    r"Consequence:\s*(LOW|MEDIUM|HIGH)\s*$",
    re.MULTILINE,
)
_CO_ATTEMPT_RE = re.compile(r"^\s*-\s*CO\S*.*$", re.MULTILINE)

_EARNED = {"earned", "earned-by-frame"}
_EFFECTS = {
    "register-floor",
    "stance-demotion",
    "blocked-high-stakes",
    "blocked-cash-out",
}


def _is_premise_flag_mechanism(mechanism):
    if not isinstance(mechanism, str):
        return False
    token = mechanism.strip()
    return token.upper() in _PREMISE_FLAG_MECHANISMS or re.match(
        r"^GT8\b", token, re.IGNORECASE
    ) is not None


def _read(path):
    try:
        return Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise ValueError("cannot read %s as UTF-8: %s" % (path, exc))


def parse_state(text):
    errors = []
    reg = _REGISTER_RE.findall(text)
    conf = _CONFIRM_RE.findall(text)
    high = _HIGH_RE.findall(text)
    if len(reg) != 1:
        errors.append("S1 state: expected exactly one Register: asserted|generative field")
    if len(conf) != 1:
        errors.append("S1 state: expected exactly one Register confirmation field")
    if len(high) != 1:
        errors.append("S1 state: expected exactly one High-stakes gate: ACTIVE|INACTIVE — source field")

    register = reg[0] if len(reg) == 1 else None
    confirmation = conf[0] if len(conf) == 1 else None
    high_gate = high[0][0] if len(high) == 1 else None
    if register == "generative" and confirmation != "WRITER-CONFIRMED":
        errors.append("S1 state: generative register requires WRITER-CONFIRMED")
    if register == "generative" and high_gate == "ACTIVE":
        errors.append("S1 state: an ACTIVE high-stakes gate forces asserted register")
    if high_gate == "ACTIVE" and confirmation != "FORCED-ASSERTED":
        errors.append("S1 state: ACTIVE high-stakes gate requires FORCED-ASSERTED")
    if confirmation == "FORCED-ASSERTED" and register != "asserted":
        errors.append("S1 state: FORCED-ASSERTED requires asserted register")
    if confirmation == "FORCED-ASSERTED" and high_gate != "ACTIVE":
        errors.append("S1 state: FORCED-ASSERTED requires an ACTIVE high-stakes gate")

    rows = list(_CO_ROW_RE.finditer(text))
    attempts = _CO_ATTEMPT_RE.findall(text)
    if len(attempts) != len(rows):
        errors.append("S2 cash-out: malformed CO row; expected CO# | Location | Kind | Press | Consequence")
    cashouts = {}
    for row in rows:
        cid, location, kind, press, consequence = row.groups()
        if cid in cashouts:
            errors.append("S2 cash-out: duplicate id %s" % cid)
        cashouts[cid] = {
            "location": location,
            "kind": kind,
            "press": press,
            "consequence": consequence,
        }
    none_sentinel = "Cash-out inventory:\n  - NONE" in text
    if none_sentinel and cashouts:
        errors.append("S2 cash-out: NONE sentinel cannot coexist with CO rows")
    if register == "generative" and not cashouts and not none_sentinel:
        errors.append("S2 cash-out: generative state requires an exact inventory or '- NONE'")
    if high_gate == "ACTIVE" and len(high) == 1 and high[0][1].strip().upper() == "NONE":
        errors.append("S1 state: ACTIVE high-stakes gate requires a non-NONE intake source")
    return {
        "register": register,
        "confirmation": confirmation,
        "high_gate": high_gate,
        "cashouts": cashouts,
    }, errors


def check(ledger_text, state_text=None):
    errors = []
    if art is None:
        return ["S0 runtime: apodictic_artifacts.py unavailable"]
    schema = art.load_schema("apodictic.finding.v1")
    if schema is None:
        return ["S0 runtime: apodictic.finding.v1 schema unavailable"]

    state = None
    if state_text is not None:
        state, state_errors = parse_state(state_text)
        errors.extend(state_errors)

    findings = []
    for btype, obj, jerr in art.parse_blocks(ledger_text):
        if btype != "finding":
            continue
        if jerr:
            errors.append("S3 finding: malformed JSON: %s" % jerr)
            continue
        where = "finding %s" % (obj.get("id", "<missing>") if isinstance(obj, dict) else "<invalid>")
        shape = art.validate_obj(obj, schema, where)
        errors.extend("S3 schema: %s" % err for err in shape)
        if isinstance(obj, dict):
            findings.append(obj)
    if not findings:
        errors.append("S3 finding: no apodictic:finding blocks found")
        return errors

    for f in findings:
        fid = str(f.get("id", "<missing>"))
        register = f.get("register")
        stance = f.get("stance")
        verdict = f.get("stance_verdict")
        effect = f.get("calibration_effect")
        co_ref = f.get("cash_out_ref")
        severity = f.get("severity")
        mechanism = f.get("mechanism")

        if (stance is None) != (verdict is None):
            errors.append("S4 %s: stance and stance_verdict must appear together" % fid)
        if effect is not None and effect not in _EFFECTS:
            errors.append("S4 %s: unknown calibration_effect %r" % (fid, effect))
        if effect is not None and state is None:
            errors.append("S4 %s: calibration_effect requires --argument-state" % fid)
            continue
        if _is_premise_flag_mechanism(mechanism) and any(
                value is not None for value in (register, stance, verdict, effect, co_ref)):
            errors.append("S4 %s: GT8 premise-plausibility flags cannot carry stance calibration" % fid)
            continue

        co = None
        if co_ref is not None:
            if state is None:
                errors.append("S5 %s: cash_out_ref requires --argument-state" % fid)
            elif co_ref not in state["cashouts"]:
                errors.append("S5 %s: cash_out_ref %s does not resolve" % (fid, co_ref))
            else:
                co = state["cashouts"][co_ref]

        if state is not None and state["high_gate"] == "ACTIVE" and register == "generative":
            errors.append("S6 %s: ACTIVE high-stakes gate forbids register=generative" % fid)

        would_demote = verdict in _EARNED or effect in {"register-floor", "stance-demotion"}
        recorded_register_floor = register == "generative" and severity == "Could-Fix"
        expected_block = None
        if state is not None and state["high_gate"] == "ACTIVE" and would_demote:
            expected_block = "blocked-high-stakes"
        elif co is not None and co["kind"] == "PRESCRIPTION" and (
                would_demote or recorded_register_floor):
            expected_block = "blocked-cash-out"

        if expected_block:
            if effect != expected_block:
                errors.append("S6 %s: precedence requires calibration_effect=%s" % (fid, expected_block))
            if register == "generative" and severity == "Could-Fix":
                errors.append("S6 %s: blocked finding cannot use the generative Could-Fix floor" % fid)
        elif effect == "blocked-high-stakes":
            errors.append("S6 %s: blocked-high-stakes requires an earned would-be demotion under an ACTIVE gate" % fid)
        elif effect == "blocked-cash-out":
            errors.append("S6 %s: blocked-cash-out requires an earned would-be demotion at a joined PRESCRIPTION row" % fid)

        if effect == "blocked-high-stakes" and (stance is None or verdict not in _EARNED):
            errors.append("S6 %s: blocked-high-stakes requires stance + earned verdict" % fid)
        if effect == "blocked-cash-out" and not (register == "generative" or verdict in _EARNED):
            errors.append("S6 %s: blocked-cash-out requires generative register or an earned stance verdict" % fid)

        if effect == "register-floor":
            if register != "generative" or severity != "Could-Fix":
                errors.append("S7 %s: register-floor requires register=generative and severity=Could-Fix" % fid)
            if co is not None:
                errors.append("S7 %s: register-floor is a non-cash-out mechanism and forbids cash_out_ref" % fid)
        if effect == "stance-demotion":
            if stance is None or verdict not in _EARNED or severity != "Could-Fix":
                errors.append("S7 %s: stance-demotion requires stance + earned verdict + Could-Fix" % fid)
        if verdict in _EARNED and not expected_block:
            applied_register = register or (state["register"] if state is not None else None)
            expected_effect = (
                "register-floor" if applied_register == "generative" and co is None
                else "stance-demotion"
            )
            if severity != "Could-Fix" or effect != expected_effect:
                errors.append("S7 %s: earned verdict requires severity=Could-Fix and calibration_effect=%s" %
                              (fid, expected_effect))
        if register == "generative" and severity == "Could-Fix" and co is None and not expected_block \
                and effect != "register-floor":
            errors.append("S7 %s: generative Could-Fix requires calibration_effect=register-floor" % fid)

    return errors


def run_self_test():
    failures = []

    def finding(**updates):
        obj = {
            "schema": "apodictic.finding.v1", "id": "F-DC-01", "mechanism": "WR0",
            "severity": "Could-Fix", "confidence": "HIGH", "evidence_refs": ["Ch 1"],
            "fix_class": "structural", "risk_if_fixed": "flattening",
            "register": "generative", "stance": "S2", "stance_verdict": "earned-by-frame",
            "calibration_effect": "register-floor",
        }
        obj.update(updates)
        obj = {key: value for key, value in obj.items() if value is not None}
        import json
        return "<!-- apodictic:finding\n%s\n-->" % json.dumps(obj)

    base_state = """## 1. Context and Classification
Register: generative
Register confirmation: WRITER-CONFIRMED
High-stakes gate: INACTIVE — NONE
Cash-out inventory:
  - CO1 | Location: paragraph 9 | Kind: PRESCRIPTION | Press: HARD | Consequence: HIGH
"""

    def expect(name, ledger, state, passes):
        errs = check(ledger, state)
        ok = not errs
        print("  %s: %s%s" % (name, "OK" if ok == passes else "FAIL",
                              "" if ok == passes else " (%s)" % "; ".join(errs)))
        if ok != passes:
            failures.append(name)

    expect("register_floor_valid", finding(), base_state, True)
    expect("missing_stance_rejected", finding(stance=None), base_state, False)
    expect("bad_enum_rejected", finding(stance="S9"), base_state, False)
    expect("unresolved_cashout_rejected", finding(cash_out_ref="CO9"), base_state, False)
    expect("prescriptive_demotion_rejected", finding(cash_out_ref="CO1"), base_state, False)
    expect("bare_generative_floor_at_prescriptive_cashout_rejected",
           finding(stance=None, stance_verdict=None, calibration_effect=None,
                   cash_out_ref="CO1"), base_state, False)
    expect("prescriptive_block_valid",
           finding(severity="Should-Fix", cash_out_ref="CO1", calibration_effect="blocked-cash-out"),
           base_state, True)
    asserted_prescriptive_state = base_state.replace("Register: generative", "Register: asserted").replace(
        "WRITER-CONFIRMED", "DEFAULT-ASSERTED")
    expect("asserted_unearned_prescriptive_full_strength_valid",
           finding(severity="Should-Fix", register="asserted", stance="S3",
                   stance_verdict="unearned", calibration_effect=None, cash_out_ref="CO1"),
           asserted_prescriptive_state, True)
    expect("asserted_earned_prescriptive_block_valid",
           finding(severity="Should-Fix", register="asserted", stance="S3",
                   stance_verdict="earned", calibration_effect="blocked-cash-out",
                   cash_out_ref="CO1"), asserted_prescriptive_state, True)
    high_state = base_state.replace("Register: generative", "Register: asserted").replace(
        "WRITER-CONFIRMED", "FORCED-ASSERTED").replace("INACTIVE — NONE", "ACTIVE — testimony")
    expect("high_gate_block_valid",
           finding(severity="Should-Fix", register="asserted", calibration_effect="blocked-high-stakes"),
           high_state, True)
    expect("high_gate_wrong_effect_rejected", finding(), high_state, False)
    expect("high_gate_unearned_full_strength_valid",
           finding(severity="Should-Fix", register="asserted", stance="S3",
                   stance_verdict="unearned", calibration_effect=None), high_state, True)
    expect("high_gate_divergent_full_strength_valid",
           finding(severity="Should-Fix", register="asserted", stance="S3",
                   stance_verdict="divergent", calibration_effect=None), high_state, True)
    expect("high_gate_native_could_block_valid",
           finding(severity="Could-Fix", register="asserted", stance="S3",
                   stance_verdict="earned", calibration_effect="blocked-high-stakes"),
           high_state, True)
    expect("high_gate_generative_finding_rejected",
           finding(severity="Should-Fix", register="generative",
                   calibration_effect="blocked-high-stakes"), high_state, False)
    expect("generative_unconfirmed_rejected", finding(), base_state.replace(
        "WRITER-CONFIRMED", "DEFAULT-ASSERTED"), False)
    expect("forced_asserted_inactive_rejected", finding(severity="Should-Fix", register="asserted",
           stance_verdict="unearned", calibration_effect=None), asserted_prescriptive_state.replace(
           "DEFAULT-ASSERTED", "FORCED-ASSERTED"), False)
    expect("active_lowercase_none_source_rejected", finding(severity="Should-Fix",
           register="asserted", calibration_effect="blocked-high-stakes"),
           high_state.replace("testimony", "none"), False)
    expect("malformed_cashout_rejected", finding(), base_state.replace("Kind: PRESCRIPTION", "PRESCRIPTION"), False)
    expect("mistyped_cashout_id_rejected", finding(), base_state.replace("CO1", "COX"), False)
    expect("duplicate_cashout_rejected", finding(), base_state +
           "  - CO1 | Location: paragraph 10 | Kind: ASSERTION | Press: LIGHT | Consequence: LOW\n", False)
    expect("none_plus_row_rejected", finding(), base_state.replace(
        "Cash-out inventory:", "Cash-out inventory:\n  - NONE"), False)
    expect("lookalike_cashout_id_rejected", finding(cash_out_ref="CO1-extra"), base_state, False)
    assertion_state = base_state.replace("Register: generative", "Register: asserted").replace(
        "WRITER-CONFIRMED", "DEFAULT-ASSERTED").replace("Kind: PRESCRIPTION", "Kind: ASSERTION")
    expect("assertion_stance_demotion_valid",
           finding(register="asserted", cash_out_ref="CO1", calibration_effect="stance-demotion"),
           assertion_state, True)
    expect("earned_should_without_demotion_rejected",
           finding(severity="Should-Fix", register="asserted", calibration_effect=None),
           assertion_state, False)
    expect("earned_must_without_demotion_rejected",
           finding(severity="Must-Fix", register="asserted", calibration_effect=None),
           assertion_state, False)
    expect("earned_by_frame_generative_should_without_floor_rejected",
           finding(severity="Should-Fix", calibration_effect=None), base_state, False)
    expect("register_floor_with_cashout_ref_rejected",
           finding(cash_out_ref="CO1"), assertion_state, False)
    expect("gt8_premise_flag_stance_rejected",
           finding(mechanism="CONTESTABLE"), base_state, False)
    expect("gt8_prefixed_mechanism_stance_rejected",
           finding(mechanism="GT8 — premise plausibility: contestable ground"),
           base_state, False)
    expect("generative_unearned_register_floor_valid",
           finding(stance_verdict="unearned"), base_state, True)
    expect("generative_earned_missing_register_rejected",
           finding(register=None, calibration_effect="stance-demotion"), base_state, False)
    expect("effect_without_state_rejected", finding(), None, False)
    expect("cashout_ref_without_state_rejected",
           finding(severity="Should-Fix", register="asserted", stance="S3",
                   stance_verdict="unearned", calibration_effect=None, cash_out_ref="CO1"),
           None, False)
    legacy = finding()
    for field in ("register", "stance", "stance_verdict", "calibration_effect"):
        import json as _json
        marker = art.parse_blocks(legacy)[0][1]
        marker.pop(field, None)
        legacy = "<!-- apodictic:finding\n%s\n-->" % _json.dumps(marker)
    expect("legacy_finding_compatible", legacy, assertion_state, True)

    if failures:
        print("Self-test: FAIL (%d): %s" % (len(failures), ", ".join(failures)))
        return 1
    print("Self-test: PASS (stance-calibration; schema + joins + precedence + blocking)")
    return 0


def main(argv):
    if "--self-test" in argv:
        return run_self_test()
    args = list(argv[1:])
    if args and args[0] == "stance-calibration":
        args.pop(0)
    if not args:
        sys.stderr.write("Usage: stance_calibration.py stance-calibration <ledger.md> --argument-state <Argument_State.md> | --self-test\n")
        return 2
    ledger = args.pop(0)
    state_path = None
    if "--argument-state" in args:
        i = args.index("--argument-state")
        if i + 1 >= len(args):
            sys.stderr.write("ERROR: --argument-state requires a path\n")
            return 2
        state_path = args[i + 1]
        del args[i:i + 2]
    if args:
        sys.stderr.write("ERROR: unknown arguments: %s\n" % " ".join(args))
        return 2
    try:
        ledger_text = _read(ledger)
        state_text = _read(state_path) if state_path else None
    except ValueError as exc:
        sys.stderr.write("stance-calibration: FAIL — %s\n" % exc)
        return 2
    errors = check(ledger_text, state_text)
    if errors:
        print("stance-calibration: FAIL (%d)" % len(errors))
        for error in errors:
            print("  - %s" % error)
        return 1
    print("stance-calibration: PASS (%s)" % ledger)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
