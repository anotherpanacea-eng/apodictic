#!/usr/bin/env python3
"""Real-file validator workflow, including disposable producer and hostile checks.

Python 3.10+. Canonical inputs are never modified. Expected failures are checked
explicitly; an unguarded preparation or captured-child failure aborts as before.
"""

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from contextlib import contextmanager


HERE = Path(__file__).resolve().parent


class CanonicalAbort(SystemExit):
    """An original unguarded subprocess failed; do not print an aggregate verdict."""


def _line(text=""):
    sys.stdout.buffer.write((text + "\n").encode("utf-8", errors="surrogateescape"))
    sys.stdout.buffer.flush()


def run_validator(command, *arguments) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        [sys.executable, str(Path(__file__).resolve().parent / "validate.py"), command,
         *map(str, arguments)], capture_output=True,
        env=dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8"),
    )


def _producer(script, *arguments):
    return subprocess.run(
        [sys.executable, str(HERE / script), *map(str, arguments)], capture_output=True,
        env=dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8"),
    )


def _relay(result):
    for stream, data in ((sys.stdout.buffer, result.stdout), (sys.stderr.buffer, result.stderr)):
        stream.write(data.replace(b"\r\n", b"\n") if os.name == "nt" else data)
        stream.flush()
    return int(result.returncode != 0)


def _text(result):
    return (result.stdout + result.stderr).decode("utf-8", errors="surrogateescape")


def _captured(result):
    if result.returncode:
        raise CanonicalAbort(result.returncode)
    return _text(result).rstrip("\n")


def _summary(label, ok):
    _line(label + (": PASS" if ok else ": FAIL"))
    return int(not ok)


def _check(condition, success, failure):
    _line(success if condition else failure)
    return int(not condition)


def _write(path, text):
    path.write_bytes(text.encode("utf-8"))


def _rewrite(path, old, new):
    _write(path, path.read_text(encoding="utf-8").replace(old, new))


def _without_lines(source, target, pattern):
    _write(target, "".join(line for line in source.read_text(encoding="utf-8").splitlines(keepends=True)
                         if not re.search(pattern, line)))


def _copy_globs(source, target, *patterns):
    # Each original cp glob is required; an empty population is not a successful copy.
    for pattern in patterns:
        matches = sorted(source.glob(pattern))
        if not matches:
            raise OSError(f"required canonical input missing: {source / pattern}")
        for path in matches:
            shutil.copyfile(path, target / path.name)


@contextmanager
def _temporary(source=None):
    with tempfile.TemporaryDirectory(prefix="apodictic-canonical-") as directory:
        path = Path(directory)
        if source is not None:
            shutil.copytree(source, path, dirs_exist_ok=True)
        yield path


def _same_bytes(first, second):
    return first.is_file() and second.is_file() and first.read_bytes() == second.read_bytes()


def _evals():
    return next((path for path in (HERE / "../../../evals", HERE / "../evals") if path.is_dir()), None)


def _locate(relative, *, file=False):
    for root in (HERE / "../../../evals", HERE / "../evals"):
        path = root / relative
        if path.is_file() if file else path.is_dir():
            return path
    return None


def _framework(references):
    failed = 0
    _line('== audit-tier-criterion (real pass-dependencies.md) ==')
    if (references / 'pass-dependencies.md').is_file():
        result = run_validator('audit-tier-criterion', references / 'pass-dependencies.md')
        failed |= _relay(result)
    else:
        _line(f'ERROR: {references}/pass-dependencies.md not found')
        failed = 1
    _line('')
    _line('== pass-header (canonical pass artifact vs real pass-dependencies.md §3) ==')
    if (references / 'example-pass-artifact-header.md').is_file() and (references / 'pass-dependencies.md').is_file():
        result = run_validator('pass-header', references / 'example-pass-artifact-header.md', references / 'pass-dependencies.md')
        failed |= _relay(result)
    else:
        _line(f'ERROR: {references}/example-pass-artifact-header.md or pass-dependencies.md not found')
        failed = 1
    _line('')
    _line('== results-guide (canonical example-results-guide run folder vs real §3) ==')
    if (references / 'example-results-guide').is_dir():
        result = run_validator('results-guide', references / 'example-results-guide')
        failed |= _relay(result)
    else:
        _line(f'ERROR: {references}/example-results-guide not found')
        failed = 1
    _line('')
    return failed


def _letters(references):
    failed = 0
    _line('== canonical editorial letter (decision-layer-check, audit-signal-propagation, severity-floor, structured-findings, underdiagnosis-triggers, ledger-consolidation) ==')
    if (references / 'example-editorial-letter.md').is_file():
        result = run_validator('decision-layer-check', references / 'example-editorial-letter.md')
        failed |= _relay(result)
        result = run_validator('audit-signal-propagation', references / 'example-editorial-letter.md')
        failed |= _relay(result)
        result = run_validator('severity-floor', references / 'example-editorial-letter.md')
        failed |= _relay(result)
        result = run_validator('structured-findings', references / 'example-editorial-letter.md')
        failed |= _relay(result)
        result = run_validator('underdiagnosis-triggers', references / 'example-editorial-letter.md')
        failed |= _relay(result)
        result = run_validator('ledger-consolidation', references / 'example-editorial-letter.md')
        failed |= _relay(result)
    else:
        _line(f'ERROR: {references}/example-editorial-letter.md not found')
        failed = 1
    _line('')
    _line('== canonical scaffolded letter (editor-scaffolding + decision-layer-check + severity-floor compose) ==')
    if (references / 'example-editorial-letter-scaffolded.md').is_file():
        result = run_validator('editor-scaffolding', references / 'example-editorial-letter-scaffolded.md')
        failed |= _relay(result)
        result = run_validator('decision-layer-check', references / 'example-editorial-letter-scaffolded.md')
        failed |= _relay(result)
        result = run_validator('severity-floor', references / 'example-editorial-letter-scaffolded.md')
        failed |= _relay(result)
        if (references / 'example-editorial-letter-dual-author.md').is_file():
            result = run_validator('editor-scaffolding', '--dual', references / 'example-editorial-letter-scaffolded.md', references / 'example-editorial-letter-dual-author.md')
            failed |= _relay(result)
        else:
            _line(f'ERROR: {references}/example-editorial-letter-dual-author.md not found')
            failed = 1
        if (references / 'example-pass-scaffolded.md').is_file():
            result = run_validator('editor-scaffolding', '--per-pass', references / 'example-pass-scaffolded.md', '--strict')
            failed |= _relay(result)
        else:
            _line(f'ERROR: {references}/example-pass-scaffolded.md not found')
            failed = 1
    else:
        _line(f'ERROR: {references}/example-editorial-letter-scaffolded.md not found')
        failed = 1
    _line('')
    _line("== canonical blind-spot ordering (editor-scaffolding ranked E2, verified vs the run folder's Ledger) ==")
    if (references / 'example-blindspot-ranked').is_dir():
        result = run_validator('editor-scaffolding', references / 'example-blindspot-ranked', '--strict')
        failed |= _relay(result)
    else:
        _line(f'ERROR: {references}/example-blindspot-ranked not found')
        failed = 1
    _line('')
    _line('== canonical Vocabulary Guide (diagnostic-vocabulary: glossary grounding + question framing) ==')
    if (references / 'example-vocabulary-guide.md').is_file():
        result = run_validator('diagnostic-vocabulary', references / 'example-vocabulary-guide.md')
        failed |= _relay(result)
    else:
        _line(f'ERROR: {references}/example-vocabulary-guide.md not found')
        failed = 1
    _line('')
    _line('== canonical example ledger <-> letter (both directions: structured-findings on the ledger + finding-trace forward refs + softness-check reverse delivery; deficit-lock structured locks) ==')
    if (references / 'example-findings-ledger.md').is_file():
        result = run_validator('structured-findings', references / 'example-findings-ledger.md')
        failed |= _relay(result)
        result = run_validator('finding-trace', references / 'example-findings-ledger.md', references / 'example-editorial-letter.md')
        failed |= _relay(result)
        result = run_validator('softness-check', references / 'example-editorial-letter.md', references / 'example-findings-ledger.md')
        failed |= _relay(result)
        result = run_validator('deficit-lock', references / 'example-findings-ledger.md')
        failed |= _relay(result)
    else:
        _line(f'ERROR: {references}/example-findings-ledger.md not found')
        failed = 1
    _line('')
    _line('== canonical Feedback Triage (feedback-triage: contract + conflict integrity + maps_to cross-check vs the ledger) ==')
    if (references / 'example-feedback-triage.md').is_file() and (references / 'example-findings-ledger.md').is_file():
        result = run_validator('feedback-triage', references / 'example-feedback-triage.md', references / 'example-findings-ledger.md', '--strict')
        failed |= _relay(result)
    else:
        _line(f'ERROR: {references}/example-feedback-triage.md or example-findings-ledger.md not found')
        failed = 1
    _line('')
    _line('== canonical Retcon Plan (retcon-plan: commitment-budget + fair-play + target integrity + ranked selection) ==')
    if (references / 'example-retcon-plan.md').is_file():
        result = run_validator('retcon-plan', references / 'example-retcon-plan.md')
        failed |= _relay(result)
    else:
        _line(f'ERROR: {references}/example-retcon-plan.md not found')
        failed = 1
    _line('')
    _line('== canonical Revision Arc (revision-arc: self-consistency + provenance + firewall over the phased multi-week arc) ==')
    if (references / 'example-revision-arc.md').is_file():
        result = run_validator('revision-arc', references / 'example-revision-arc.md', '--strict')
        failed |= _relay(result)
    else:
        _line(f'ERROR: {references}/example-revision-arc.md not found')
        failed = 1
    _line('')
    _line("== canonical Legal Risk Register (legal-risk: contract + disclaimer gate + flag-don't-adjudicate) ==")
    if (references / 'example-legal-risk-register.md').is_file():
        result = run_validator('legal-risk', references / 'example-legal-risk-register.md')
        failed |= _relay(result)
    else:
        _line(f'ERROR: {references}/example-legal-risk-register.md not found')
        failed = 1
    _line('')
    _line('== canonical Promise-Contract Fidelity (promise-contract: two-sided gap P1 + copy typing P2 + reveal form gate P3 + firewall W1) ==')
    if (references / 'example-promise-contract.md').is_file():
        result = run_validator('promise-contract', references / 'example-promise-contract.md')
        failed |= _relay(result)
    else:
        _line(f'ERROR: {references}/example-promise-contract.md not found')
        failed = 1
    _line('')
    _line('== canonical Continuity Bible (continuity-bible: schema C1 + locus shape C2 + contradiction integrity C3 + clean chronology-consume C4 + coverage W1, paired with the Timeline, under --strict) ==')
    if (references / 'example-continuity-bible.md').is_file() and (references / 'example-timeline.md').is_file():
        result = run_validator('continuity-bible', references / 'example-continuity-bible.md', references / 'example-timeline.md', '--strict')
        failed |= _relay(result)
    else:
        _line(f'ERROR: {references}/example-continuity-bible.md or example-timeline.md not found')
        failed = 1
    _line('')
    _line('== canonical Setup–Payoff Ledger (setup-payoff: SP1 schema over both block kinds + SP2 referential integrity + SP3 open rationale + SP4 derived-state agreement + clean X1 firewall; three valid states pass, abandoned row surfaced for prose citation) ==')
    if (references / 'example-setup-payoff-ledger.md').is_file():
        result = run_validator('setup-payoff', references / 'example-setup-payoff-ledger.md', '--strict')
        failed |= _relay(result)
    else:
        _line(f'ERROR: {references}/example-setup-payoff-ledger.md not found')
        failed = 1
    _line('')
    _line('== canonical Intake Interview (intake-interview: schema I1 + no-contract-dup I2 + grounded ambiguity I3 (ref + source_note) + calibrate-not-suppress I4, paired with the Ledger, under --strict) ==')
    if (references / 'example-intake-interview.md').is_file() and (references / 'example-intake-interview-ledger.md').is_file():
        result = run_validator('intake-interview', references / 'example-intake-interview.md', references / 'example-intake-interview-ledger.md', '--strict')
        failed |= _relay(result)
    else:
        _line(f'ERROR: {references}/example-intake-interview.md or example-intake-interview-ledger.md not found')
        failed = 1
    _line('')
    _line('== canonical Author Voice Profile (author-fingerprint: schema F1 + provenance F2 + same-register F3 + descriptive-not-prescriptive F4 + clean W1/W2, under --strict) ==')
    if (references / 'example-author-voice-profile.md').is_file():
        result = run_validator('author-fingerprint', references / 'example-author-voice-profile.md', '--strict')
        failed |= _relay(result)
    else:
        _line(f'ERROR: {references}/example-author-voice-profile.md not found')
        failed = 1
    _line('')
    _line('== canonical Content Advisory (content-advisory: schema A1 + locus shape A2 + no-severity-leak A3 + descriptive W1 + opt-in W2, under --strict) ==')
    if (references / 'example-content-advisory.md').is_file():
        result = run_validator('content-advisory', references / 'example-content-advisory.md', '--strict')
        failed |= _relay(result)
    else:
        _line(f'ERROR: {references}/example-content-advisory.md not found')
        failed = 1
    _line('')
    return failed


def _voice_world_state(references):
    failed = 0
    _line('== canonical Author Style Explanation (style-explanation: schema X1 + provenance X2 + no-severity X3 + descriptive-not-prescriptive X4 + same-register cluster X5 + clean X6/W1, under --strict) ==')
    if (references / 'example-author-style-explanation.md').is_file():
        result = run_validator('style-explanation', references / 'example-author-style-explanation.md', '--strict')
        failed |= _relay(result)
    else:
        _line(f'ERROR: {references}/example-author-style-explanation.md not found')
        failed = 1
    _line('')
    _line('== canonical Persona Divergence Map (persona-divergence: schema D1 + grounded prediction D2 + target-severity D3 + anti-fabrication D4 + closed-key D5, paired with the Ledger, under --strict) ==')
    if (references / 'example-persona-divergence-map.md').is_file() and (references / 'example-persona-divergence-ledger.md').is_file():
        result = run_validator('persona-divergence', references / 'example-persona-divergence-map.md', references / 'example-persona-divergence-ledger.md', '--strict')
        failed |= _relay(result)
    else:
        _line(f'ERROR: {references}/example-persona-divergence-map.md or example-persona-divergence-ledger.md not found')
        failed = 1
    _line('')
    _line('== canonical Worldbuilding Bible (world-bible: schema W1 + closed-key + unique ids WD + rule WB-R1 + cost WB-C1/C2 + distance WB-G1 + chronology WB-G2 + firewall WF, staged contradictions overridden, under --strict) ==')
    if (references / 'example-worldbuilding-bible.md').is_file():
        result = run_validator('world-bible', references / 'example-worldbuilding-bible.md', '--strict')
        failed |= _relay(result)
    else:
        _line(f'ERROR: {references}/example-worldbuilding-bible.md not found')
        failed = 1
    _line('')
    _line('== canonical State Card (state-card-diff: cross-round coherence; self-diff + round-2 diff) ==')
    if (references / 'example-state-card.md').is_file():
        result = run_validator('state-card-diff', references / 'example-state-card.md')
        failed |= _relay(result)
        if (references / 'example-state-card-round2.md').is_file():
            result = run_validator('state-card-diff', references / 'example-state-card.md', references / 'example-state-card-round2.md')
            failed |= _relay(result)
        else:
            _line(f'ERROR: {references}/example-state-card-round2.md not found')
            failed = 1
    else:
        _line(f'ERROR: {references}/example-state-card.md not found')
        failed = 1
    _line('')
    return failed


def _predraft(references):
    failed = 0
    _line('== canonical pre-draft Argument_State (argument-spine: spine + support + warrant maps seed §1-§4) ==')
    if (references / 'example-argument-state-predraft.md').is_file():
        result = run_validator('argument-spine', references / 'example-argument-state-predraft.md')
        failed |= _relay(result)
    else:
        _line(f'ERROR: {references}/example-argument-state-predraft.md not found')
        failed = 1
    _line('')
    return failed


def _scene_reader_annotation(references):
    failed = 0
    _line('== canonical Scene-Ethics Plan (scene-ethics: ethics-plan contract + resolved depictions) ==')
    if (references / 'example-scene-ethics-plan.md').is_file():
        result = run_validator('scene-ethics', references / 'example-scene-ethics-plan.md')
        failed |= _relay(result)
    else:
        _line(f'ERROR: {references}/example-scene-ethics-plan.md not found')
        failed = 1
    _line('')
    _line('== canonical Beta-Reader Instrument (reader-instrument: question-contract + provenance + firewall + anti-relitigation) ==')
    if (references / 'example-beta-reader-instrument.md').is_file() and (references / 'example-uncertainty-ledger.md').is_file():
        result = run_validator('reader-instrument', references / 'example-beta-reader-instrument.md', references / 'example-uncertainty-ledger.md')
        failed |= _relay(result)
    else:
        _line(f'ERROR: {references}/example-beta-reader-instrument.md / example-uncertainty-ledger.md not found')
        failed = 1
    _line('')
    _line('== canonical Structure Map manifest (manuscript-viz: manifest<->source provenance vs Timeline + Ledger + claim-ladder spine + co-presence roster + scene-function producer + tension-point producer + story-spine producer) ==')
    if (references / 'example-structure-map-manifest.md').is_file() and (references / 'example-timeline.md').is_file() and (references / 'example-findings-ledger.md').is_file() and (references / 'example-argument-state-predraft.md').is_file() and (references / 'example-scene-roster.md').is_file() and (references / 'example-scene-function.md').is_file() and (references / 'example-tension-points.md').is_file() and (references / 'example-story-spine.md').is_file():
        result = run_validator('manuscript-viz', references / 'example-structure-map-manifest.md', references / 'example-timeline.md', references / 'example-findings-ledger.md', references / 'example-argument-state-predraft.md', references / 'example-scene-roster.md', references / 'example-scene-function.md', references / 'example-tension-points.md', references / 'example-story-spine.md', '--require-block')
        failed |= _relay(result)
    else:
        _line(f'ERROR: {references}/example-structure-map-manifest.md / example-timeline.md / example-findings-ledger.md / example-argument-state-predraft.md / example-scene-roster.md / example-scene-function.md / example-tension-points.md / example-story-spine.md not found')
        failed = 1
    _line('')
    _line('== canonical annotated manuscript (annotated-manuscript: no-mutation + anchor ladder + Must-Fix rendered) ==')
    if (references / 'example-annotated-manuscript').is_dir():
        result = run_validator('annotated-manuscript', references / 'example-annotated-manuscript')
        failed |= _relay(result)
    else:
        _line(f'ERROR: {references}/example-annotated-manuscript not found')
        failed = 1
    _line('')
    _line('== canonical crosslink (crosslink: letter<->margin bidirectional integrity + no letter mutation) ==')
    if (references / 'example-annotated-manuscript').is_dir():
        result = run_validator('crosslink', references / 'example-annotated-manuscript')
        failed |= _relay(result)
    else:
        _line(f'ERROR: {references}/example-annotated-manuscript not found')
        failed = 1
    _line('')
    return failed


def _timeline(references):
    failed = 0
    _line('== canonical Timeline (timeline-arithmetic, timeline-anchor-conflict, timeline-diff self) ==')
    if (references / 'example-timeline.md').is_file():
        result = run_validator('timeline-arithmetic', references / 'example-timeline.md')
        failed |= _relay(result)
        result = run_validator('timeline-anchor-conflict', references / 'example-timeline.md')
        failed |= _relay(result)
        result = run_validator('timeline-diff', references / 'example-timeline.md', references / 'example-timeline.md')
        failed |= _relay(result)
    else:
        _line(f'ERROR: {references}/example-timeline.md not found')
        failed = 1
    _line('')
    return failed


def _registry_templates(references):
    failed = 0
    _line('== audit-signal-propagation --check-registry (real registry vs §4e) ==')
    result = run_validator('audit-signal-propagation', '--check-registry')
    failed |= _relay(result)
    _line()
    _line('== structured-findings (shipped artifact templates) ==')
    if (references / 'diagnostic-state-meta-template.json').is_file():
        result = run_validator('structured-findings', references / 'diagnostic-state-meta-template.json',
                               references / 'findings-ledger-format.md')
        failed |= _relay(result)
    else:
        _line('ERROR: could not locate reference templates for structured-findings — --check-all cannot verify the real-file invariant')
        failed = 1
    _line()
    return failed


def _position_pair(references):
    _line('== position-pair-register (canonical example-position-pair-register fixture) ==')
    base = next((p for p in (HERE / '../skills/prose-measurements/references/example-position-pair-register',
                            HERE / '../plugins/apodictic/skills/prose-measurements/references/example-position-pair-register')
                 if p.is_dir()), None)
    failed = 0
    if base is not None:
        result = run_validator('position-pair-register', base / 'Example_Position_Pair_Register_run.md',
                               base / 'envelope.json', base / 'manuscript.txt', '--strict')
        failed |= _relay(result)
    else:
        _line('ERROR: example-position-pair-register fixture not found')
        failed = 1
    _line()
    return failed


def _coaching(references):
    _line('== canonical Coaching History (coaching-history: H1 schema+floor + H2 provenance/consecutive + H3 descriptive + H4 no-severity-leak + H7 tentative-framing + H5 single-home + H6 deletion-honored, under --strict) ==')
    failed = 0
    if (references / 'example-coaching-history').is_dir():
        result = run_validator('coaching-history', references / 'example-coaching-history', '--strict')
        if _relay(result):
            _line('ERROR: canonical coaching-history did not PASS')
            failed = 1
        source = references / 'example-coaching-history'
        history = 'Example_Coaching_History_2026-03-01_opus48.md'
        observation = {'schema': 'apodictic.coaching_observation.v1', 'id': 'CH-01',
                       'pattern': 'deferral-recurrence', 'count': 3,
                       'evidence': ['F-P2-03 deferred @ session 1', 'F-P2-03 deferred @ session 2',
                                    'F-P2-03 deferred @ session 3'], 'observation': 'leaked'}
        with _temporary(source) as temp:
            _write(temp / 'Session_Plan_01.md', '# Session Plan\n\n<!-- apodictic:coaching_observation\n' + json.dumps(observation) + '\n-->\n')
            result = run_validator('coaching-history', temp)
            failed |= _check(result.returncode != 0, '  H5.i projection-leak fixture: FAIL as required (OK)',
                             'ERROR: H5.i projection leak (Session_Plan observation block) did not FAIL')
        with _temporary(source) as temp:
            observation['observation'] = 'leaked into the letter'
            _write(temp / 'Example_Editorial_Letter_2026-03-01_opus48.md', '# Editorial Letter\n\n<!-- apodictic:coaching_observation\n' + json.dumps(observation) + '\n-->\n')
            result = run_validator('coaching-history', temp)
            failed |= _check(result.returncode != 0, '  F1 editorial-letter projection: FAIL as required (OK)',
                             'ERROR: F1 editorial-letter projection did not FAIL H5')
            run_validator('coaching-history', 'delete', temp)
            result = run_validator('coaching-history', temp)
            failed |= _check(result.returncode != 0, '  F1 H6 recompute catches surviving letter projection: FAIL as required (OK)',
                             'ERROR: F1 H6 recompute falsely reported deletion honored with a surviving letter projection')
        with _temporary(source) as temp:
            sidecar = temp / 'Diagnostic_State.meta.json'
            try:
                obj = json.loads(sidecar.read_text(encoding='utf-8'))
                obj.setdefault('execution', {})['coaching_notes'] = {'CH-01': 'the writer keeps deferring'}
                _write(sidecar, json.dumps(obj, indent=2))
            except Exception:
                pass  # Original guarded mutation; the hostile check below still runs.
            result = run_validator('coaching-history', temp)
            failed |= _check(result.returncode != 0, '  H5.v sidecar-shadow fixture: FAIL as required (OK)',
                             'ERROR: H5.v sidecar shadow field (coaching_notes) did not FAIL')
        with _temporary(source) as temp:
            shutil.copyfile(temp / history, temp / 'Example_Coaching_History_2026-02-01_opus47.md')
            result = run_validator('coaching-history', temp)
            failed |= _check(result.returncode != 0, '  H5.iv two-artifact fixture: FAIL as required (OK)',
                             'ERROR: H5.iv two Coaching_History artifacts did not FAIL')
        with _temporary(source) as temp:
            (temp / history).unlink()
            try:
                state = temp / 'Diagnostic_State.md'
                _write(state, re.sub(r'<!--\s*coaching-history:\s*opted-in\s*-->', '<!-- coaching-history: deleted -->', state.read_text(encoding='utf-8')))
                sidecar = temp / 'Diagnostic_State.meta.json'
                obj = json.loads(sidecar.read_text(encoding='utf-8')); obj.pop('coaching_history_seq', None)
                _write(sidecar, json.dumps(obj, indent=2))
            except Exception:
                pass  # Original guarded mutation; the recompute below still runs.
            (temp / 'runs/r4_coaching').mkdir(parents=True)
            _write(temp / 'runs/r4_coaching/Session_Plan_03.md', '# Archived Session Plan\n\nF-P2-03 deferred @ session 2\n')
            result = run_validator('coaching-history', temp)
            failed |= _check(result.returncode != 0, '  H6 archived-residue fixture: FAIL as required (OK)',
                             'ERROR: H6 archived deletion-residue did not FAIL')
        with _temporary(source) as temp:
            state = temp / 'Diagnostic_State.md'
            _write(state, state.read_text(encoding='utf-8') + '\n<!-- coaching-history: deleted -->\n')
            result = run_validator('coaching-history', temp)
            failed |= _check(result.returncode != 0, '  H6 consent-contradiction fixture: FAIL as required (OK)',
                             'ERROR: H6 opted-in+deleted contradiction did not FAIL')
        with _temporary(source) as temp:
            result = run_validator('coaching-history', 'delete', temp)
            if result.returncode:
                _line('ERROR: coaching-history delete failed'); failed = 1
            result = run_validator('coaching-history', temp)
            failed |= _check(result.returncode == 0, '  H6 delete-round-trip recompute: PASS as required (OK)',
                             'ERROR: H6 recompute after delete did not PASS (a clean deletion must recompute honored)')
        with _temporary(source) as temp:
            observation.update(pattern='phase-incompletion', count=2,
                               evidence=['phase Structural Root Causes incomplete @ session 101', 'phase Structural Root Causes incomplete @ session 102'],
                               observation='The structural phase stayed open. Does that track?')
            _write(temp / history, '# Coaching History\n<!-- coaching-history: opted-in -->\n<!-- apodictic:coaching_observation\n' + json.dumps(observation) + '\n-->\n')
            result = run_validator('coaching-history', temp, '--strict')
            failed |= _check(result.returncode != 0, '  P1 fabricated phase-incompletion (no caveat): FAIL --strict as required (OK)',
                             'ERROR: P1 fabricated phase-incompletion (101/102, no caveat) did not FAIL --strict')
        with _temporary(source) as temp:
            try:
                state = temp / 'Diagnostic_State.md'
                _write(state, re.sub(r'<!--\s*coaching-history:\s*opted-in\s*-->', '<!-- coaching-history: deleted -->', state.read_text(encoding='utf-8')))
                sidecar = temp / 'Diagnostic_State.meta.json'
                obj = json.loads(sidecar.read_text(encoding='utf-8')); obj.pop('coaching_history_seq', None)
                obj.setdefault('last_session', {})['coaching_history_seq'] = 9
                _write(sidecar, json.dumps(obj, indent=2)); (temp / history).unlink()
            except Exception:
                pass  # Original guarded mutation; the recompute below still runs.
            result = run_validator('coaching-history', temp)
            failed |= _check(result.returncode != 0, '  P2 nested-depth seq residue caught by H6 recompute: FAIL as required (OK)',
                             'ERROR: P2 nested-depth seq residue survived delete and H6 falsely honored')
    else:
        _line(f'ERROR: {references}/example-coaching-history not found'); failed = 1
    _line()
    return failed


def _regression(references):
    _line('== canonical regression-diff (draft-over-draft: cross-round recurrence + quiet-chapter candidates) ==')
    failed = 0
    if (references / 'example-run-folder-r1').is_dir() and (references / 'example-run-folder-r2').is_dir():
        result = run_validator('regression-diff', references / 'example-run-folder-r1', references / 'example-run-folder-r2')
        failed |= int(result.returncode != 0)
        result = run_validator('regression-diff', '--strict', references / 'example-run-folder-r1', references / 'example-run-folder-r2')
        if result.returncode == 0:
            _line('regression-diff (paired fixture): FAIL (expected --strict to exit non-zero on the candidates)'); failed = 1
        elif 'W1 recurrence-candidate' in _text(result) and 'W2 quiet-chapter breakage' in _text(result):
            _line('regression-diff (paired fixture): PASS')
        else:
            _line('regression-diff (paired fixture): FAIL (--strict ran but W1/W2 candidates not raised)'); failed = 1
    else:
        _line(f'ERROR: {references}/example-run-folder-r1 / -r2 not found'); failed = 1
    _line()
    return failed


def _genre(references):
    _line('== canonical genre-profiled Argument_States (argument-spine Inc 5: B1-B4 + W4-W5 over grant / academic / pitch; --strict) ==')
    failed = 0
    if (references / 'example-argument-state-genre-grant.md').is_file():
        result = run_validator('argument-spine', references / 'example-argument-state-genre-grant.md', '--strict')
        failed |= _relay(result)
    else:
        _line(f'ERROR: {references}/example-argument-state-genre-grant.md not found'); failed = 1
    for genre in ('academic', 'pitch'):
        path = references / f'example-argument-state-genre-{genre}.md'
        if path.is_file():
            failed |= _relay(run_validator('argument-spine', path, '--strict'))
        else:
            _line(f'ERROR: {path} not found'); failed = 1
    _line()
    return failed


def _producer_chain(references):
    _line('== producer chain (build -> A1-A6 -> render -> X1-X4 on a temp copy; verified-or-absent) ==')
    failed = 0
    source = references / 'example-annotated-manuscript'
    if source.is_dir():
        with _temporary() as temp:
            _copy_globs(source, temp, '*_Manuscript_Snapshot_*.md', '*_Findings_Ledger_*.md', '*_Timeline_*.md')
            letters = sorted(source.glob('*_Editorial_Letter_*.md'))
            if not letters:
                raise OSError(f'required canonical editorial letter missing: {source}')
            shutil.copyfile(letters[0], temp / letters[0].name.replace('_Editorial_Letter_', '_Core_DE_Synthesis_', 1))
            ok = _producer('annotation_manifest.py', 'build', temp).returncode == 0
            result = run_validator('annotated-manuscript', temp); ok &= result.returncode == 0
            result = _producer('crosslink.py', 'render', temp); ok &= result.returncode == 0
            result = run_validator('crosslink', temp); ok &= result.returncode == 0
            count = 0
            for pattern in ('*_Annotation_Manifest_*.md', '*_Annotated_Manuscript_*.md', '*_Crosslinked_Letter_*.md'):
                outputs = sorted(temp.glob(pattern))
                ok &= bool(outputs)
                for path in outputs:
                    count += 1
                    ok &= _same_bytes(path, source / path.name)
            ok &= count == 3
            failed |= _summary('producer chain (temp copy)', ok)
    else:
        _line(f'ERROR: {source} not found'); failed = 1
    _line()
    return failed


def _reanchor(references):
    _line('== canonical reanchor (round-trip: held/moved/vanished/ambiguous/not-re-anchorable + RA1-RA3) ==')
    failed = 0
    if (references / 'example-annotated-manuscript').is_dir() and (references / 'example-reanchor-revised.md').is_file():
        result = run_validator('reanchor', references / 'example-annotated-manuscript', references / 'example-reanchor-revised.md')
        failed |= int(result.returncode != 0)
        result = run_validator('reanchor', '--strict', references / 'example-annotated-manuscript', references / 'example-reanchor-revised.md')
        if result.returncode == 0:
            _line('reanchor (revised-draft fixture): FAIL (expected --strict to exit non-zero on the refusals)'); failed = 1
        elif all('reanchor:' + kind in _text(result) for kind in ('held', 'moved', 'vanished', 'ambiguous', 'not-re-anchorable')):
            _line('reanchor (revised-draft fixture): PASS')
        else:
            _line('reanchor (revised-draft fixture): FAIL (--strict ran but the five classes not all raised)'); failed = 1
    elif not (references / 'example-reanchor-revised.md').is_file():
        _line(f'ERROR: {references}/example-reanchor-revised.md not found'); failed = 1
    _line()
    _line('== round-trip glue chain (emit -> A-gate the revised copy -> crossref; on a temp copy) ==')
    if (references / 'example-annotated-manuscript').is_dir() and (references / 'example-reanchor-revised.md').is_file():
        with _temporary() as temp:
            _copy_globs(references / 'example-annotated-manuscript', temp, '*_Annotation_Manifest_*.md')
            snapshot = temp / 'Example_Manuscript_Snapshot_reanchor-r2.md'
            shutil.copyfile(references / 'example-reanchor-revised.md', snapshot)
            ok = _producer('reanchor.py', 'emit', temp, snapshot, '-o', temp).returncode == 0
            manifest = temp / 'Example_Reanchored_Manifest_reanchor-r2.md'
            annotated = temp / 'Example_Reanchored_Annotated_Manuscript_reanchor-r2.md'
            ok &= manifest.is_file() and annotated.is_file()
            if manifest.is_file() and annotated.is_file():
                # Gate the emitted files using the same public A-gate API as reanchor.
                try:
                    import annotation_manifest as am
                    snap = am.normalize_snapshot(snapshot.read_text(encoding='utf-8'))
                    code, _ = am.check(snap, manifest.read_text(encoding='utf-8'), annotated.read_text(encoding='utf-8'),
                                       ledger_text=None, ledger_optional=True)
                    ok &= code == 0
                except Exception:
                    # The old inline A-gate child was guarded and stream-suppressed.
                    # A helper/import/read failure marks this chain failed, then
                    # the crossref and later sections still run.
                    ok = False
            result = _producer('reanchor.py', 'crossref', temp, snapshot, references / 'example-run-folder-r2')
            ok &= result.returncode == 0
            failed |= _summary('round-trip glue chain (temp copy)', ok)
    elif not (references / 'example-reanchor-revised.md').is_file():
        _line(f'ERROR: {references}/example-reanchor-revised.md not found (round-trip glue chain)'); failed = 1
    _line()
    return failed


def _roundtrip(references):
    _line('== canonical roundtrip-disposition (record vs live recompute: RT1-RT4 + hostile arms) ==')
    failed = 0
    if ((references / 'example-annotated-manuscript').is_dir() and
            (references / 'example-reanchor-revised.md').is_file() and
            (references / 'example-roundtrip-disposition.md').is_file() and
            (references / 'example-roundtrip-revision-report.md').is_file()):
        with _temporary() as temp:
            prior = temp / 'prior'; prior.mkdir()
            current = temp / 'current'; current.mkdir()
            _copy_globs(references / 'example-annotated-manuscript', prior, '*_Annotation_Manifest_*.md', '*_Findings_Ledger_*.md')
            _copy_globs(references / 'example-run-folder-r2', current, '*_Findings_Ledger_*.md')
            snapshot = temp / 'Example_Manuscript_Snapshot_reanchor-r2.md'
            shutil.copyfile(references / 'example-reanchor-revised.md', snapshot)
            disposition = 'Example_Roundtrip_Disposition_reanchor-r2.md'
            report = 'Example_Revision_Report_reanchor-r2.md'
            shutil.copyfile(references / 'example-roundtrip-disposition.md', current / disposition)
            shutil.copyfile(references / 'example-roundtrip-revision-report.md', current / report)
            result = run_validator('roundtrip-disposition', prior, snapshot, current)
            out = _text(result)
            ok = (result.returncode == 0 and 'disposition:confirm-resolved F-RR-01' in out and
                  'record of confirmation present and consistent' in out and 'W1' not in out)
            h1 = temp / 'hostile-rt2'; shutil.copytree(current, h1)
            _without_lines(current / disposition, h1 / disposition, 'disposition-confirmed:')
            result = run_validator('roundtrip-disposition', prior, snapshot, h1)
            ok &= result.returncode != 0 and 'RT2' in _text(result)
            h2 = temp / 'hostile-rt3'; shutil.copytree(current, h2)
            _write(h2 / report, (current / report).read_text(encoding='utf-8') + '<!-- resolved: F-QT-01 -->\n')
            result = run_validator('roundtrip-disposition', prior, snapshot, h2)
            ok &= result.returncode != 0 and 'RT3' in _text(result)
            h3 = temp / 'hostile-rt4'; shutil.copytree(current, h3)
            _without_lines(current / disposition, h3 / disposition, 'disposition: F-QT-01')
            result = run_validator('roundtrip-disposition', prior, snapshot, h3)
            ok &= result.returncode == 0 and 'RT4 partition coverage: F-QT-01' in _text(result)
            result = run_validator('roundtrip-disposition', prior, snapshot, h3, '--strict')
            ok &= result.returncode != 0 and 'RT4' in _text(result)
            failed |= _summary('roundtrip-disposition (canonical + hostile arms)', ok)
    elif not (references / 'example-roundtrip-disposition.md').is_file() or not (references / 'example-roundtrip-revision-report.md').is_file():
        _line(f'ERROR: {references}/example-roundtrip-disposition.md + example-roundtrip-revision-report.md not found (roundtrip-disposition)'); failed = 1
    _line()
    return failed


def _dispositions(references):
    _line('== canonical disposition-check (finding dispositions: DP0 shape + DP1 caveat + DP2 no-laundering + hostile arms) ==')
    failed = 0
    if (references / 'example-run-folder-dispositions').is_dir():
        result = run_validator('disposition-check', references / 'example-run-folder-dispositions')
        ok = result.returncode == 0
        result = run_validator('disposition-check', references / 'example-run-folder-dispositions', '--strict')
        ok &= result.returncode == 0
        source = references / 'example-run-folder-dispositions'
        assessment = 'Submission_Readiness_Assessment_2026-03-01.md'
        with _temporary() as temp:
            h1 = temp / 'h1'; shutil.copytree(source, h1)
            _without_lines(source / assessment, h1 / assessment, r'^\*\*Declined Must-Fixes:\*\*')
            result = run_validator('disposition-check', h1)
            ok &= result.returncode != 0 and 'DP1 declined Must-Fix F-P5-01' in _text(result)
            h2 = temp / 'h2'; shutil.copytree(source, h2)
            sidecar = h2 / 'Diagnostic_State.meta.json'
            try:
                obj = json.loads(sidecar.read_text(encoding='utf-8'))
                del obj['execution']['finding_dispositions']['F-DP-02']['trigger']
                _write(sidecar, json.dumps(obj, indent=2))
            except Exception:
                ok = False
            result = run_validator('disposition-check', h2)
            ok &= result.returncode != 0 and 'DP0' in _text(result)
            h3 = temp / 'h3'; shutil.copytree(source, h3)
            sidecar = h3 / 'Diagnostic_State.meta.json'
            try:
                obj = json.loads(sidecar.read_text(encoding='utf-8'))
                del obj['execution']['finding_dispositions']['F-P5-01']
                _write(sidecar, json.dumps(obj, indent=2))
            except Exception:
                ok = False
            result = run_validator('disposition-check', h3)
            ok &= result.returncode == 0 and bool(re.search('DP2.5 marker without record.*F-P5-01', _text(result)))
            result = run_validator('disposition-check', h3, '--strict'); ok &= result.returncode != 0
            h4 = temp / 'h4'; shutil.copytree(source, h4)
            sidecar = h4 / 'Diagnostic_State.meta.json'
            try:
                obj = json.loads(sidecar.read_text(encoding='utf-8'))
                obj['execution']['finding_states']['F-P5-01'] = 'revised'
                _write(sidecar, json.dumps(obj, indent=2))
            except Exception:
                ok = False
            _without_lines(source / assessment, h4 / assessment, r'^\*\*Declined Must-Fixes:\*\*')
            result = run_validator('disposition-check', h4)
            ok &= result.returncode != 0 and 'DP1 declined Must-Fix F-P5-01' in _text(result) and 'DP2.6' in _text(result)
        failed |= _summary('disposition-check (canonical + hostile arms)', ok)
    else:
        _line(f'ERROR: {references}/example-run-folder-dispositions not found (disposition-check)'); failed = 1
    _line()
    return failed


def _exports(references):
    failed = 0
    # Each format retains its own generation, validation and exact artifact count.
    for verb, count, heading in (('obsidian', 2, '== canonical obsidian-export (manifest -> native footnotes; O1-O3 + byte-identical to committed) =='), ('html', 1, '== canonical html-export (manifest -> self-contained read-only HTML; H1-H3 + byte-identical) =='),
                                  ('docx', 1, '== canonical docx-export (manifest -> .docx with anchored comments; D1-D3 + byte-identical) =='), ('pdf', 1, '== canonical pdf-export (manifest -> self-contained .pdf; P1-P3 + byte-identical) ==')):
        _line(heading)
        source = references / 'example-annotated-manuscript'
        if source.is_dir():
            golden = source / verb
            if verb in ('docx', 'pdf'):
                evals = _evals()
                golden = evals / 'fixtures/annotation-export' / verb if evals is not None else None
            with _temporary() as temp:
                _copy_globs(source, temp, '*_Manuscript_Snapshot_*.md', '*_Annotation_Manifest_*.md')
                if verb == 'obsidian':
                    _copy_globs(source, temp, '*_Crosslinked_Letter_*.md')
                ok = _producer('annotation_export.py', verb, temp).returncode == 0
                result = run_validator(verb + '-export', temp); ok &= result.returncode == 0
                extension = 'md' if verb == 'obsidian' else verb
                outputs = sorted((temp / verb).glob('*.' + extension))
                ok &= len(outputs) == count
                for path in outputs:
                    if golden is not None:
                        ok &= _same_bytes(path, golden / path.name)
                if ok and golden is None:
                    _line(f'{verb}-export (temp copy): PASS (golden not found; byte-compare skipped)')
                else:
                    failed |= _summary(verb + '-export (temp copy)', ok)
        else:
            _line(f'ERROR: {source} not found ({verb}-export)'); failed = 1
        _line()
    return failed


def _reader_outline(references):
    _line('== canonical reader-contract-outline (R1-R7 over fiction + narrative-nf fixtures; producer chain; hostile arms) ==')
    failed = 0
    if (references / 'example-reader-contract-outline').is_dir():
        result = run_validator('reader-contract-outline', references / 'example-reader-contract-outline')
        ok = result.returncode == 0
        source = references / 'example-reader-contract-outline'
        for project in ('Example', 'ExampleNF'):
            with _temporary() as temp:
                for artifact in ('Pass0_Reverse_Outline', 'Contract', 'Findings_Ledger', 'Contract_Map'):
                    name = f'{project}_{artifact}_2026-01-01.md'
                    shutil.copyfile(source / name, temp / name)
                result = _producer('reader_contract_outline.py', 'build', temp); ok &= result.returncode == 0
                result = run_validator('reader-contract-outline', temp); ok &= result.returncode == 0
                name = f'{project}_Reader_Contract_Outline_2026-01-01.md'
                ok &= _same_bytes(temp / name, source / name)
        with _temporary() as baseline:
            for artifact in ('Pass0_Reverse_Outline', 'Contract', 'Findings_Ledger', 'Contract_Map', 'Reader_Contract_Outline'):
                name = f'Example_{artifact}_2026-01-01.md'
                shutil.copyfile(source / name, baseline / name)
            result = run_validator('reader-contract-outline', baseline); ok &= result.returncode == 0
            map_name = 'Example_Contract_Map_2026-01-01.md'
            outline = 'Example_Reader_Contract_Outline_2026-01-01.md'
            with _temporary(baseline) as temp:
                path = temp / map_name
                _write(path, re.sub(r'"contract_sha256": "[0-9a-f]{64}"', '"contract_sha256": "' + '0'*64 + '"', path.read_text(encoding='utf-8')))
                if run_validator('reader-contract-outline', temp).returncode == 0:
                    _line('reader-contract-outline hostile R7 (stale sha256) did NOT fail'); ok = False
            with _temporary(baseline) as temp:
                path = temp / map_name
                _write(path, path.read_text(encoding='utf-8').replace('"established": ["S1"],', '"established": ["S99"],', 1))
                if run_validator('reader-contract-outline', temp).returncode == 0:
                    _line('reader-contract-outline hostile R3 (nonexistent scene) did NOT fail'); ok = False
            with _temporary(baseline) as temp:
                path = temp / outline
                _write(path, path.read_text(encoding='utf-8').replace("stated in the keeper's dialogue but never dramatized", 'not shown on the page', 1))
                if run_validator('reader-contract-outline', temp).returncode == 0:
                    _line('reader-contract-outline hostile R4 (paraphrased gap) did NOT fail'); ok = False
            with _temporary(baseline) as temp:
                (temp / outline).unlink()
                path = temp / map_name
                text = path.read_text(encoding='utf-8')
                match = re.search(r'<!-- apodictic:contract_map\n(.*?)\n-->', text, re.DOTALL)
                obj = json.loads(match.group(1))
                obj['clauses'] = [clause for clause in obj['clauses'] if clause['clause_id'] != 'C2']
                for i, clause in enumerate(obj['clauses']):
                    clause['clause_id'] = f'C{i + 1}'
                _write(path, text[:match.start(1)] + json.dumps(obj, indent=2) + text[match.end(1):])
                result = _producer('reader_contract_outline.py', 'build', temp); ok &= result.returncode == 0
                if run_validator('reader-contract-outline', temp).returncode:
                    _line('reader-contract-outline hostile R6 (dropped promise clause) FAILED by default (should WARN)'); ok = False
                if run_validator('reader-contract-outline', '--strict', temp).returncode == 0:
                    _line('reader-contract-outline hostile R6 did NOT fail under --strict'); ok = False
        failed |= _summary('reader-contract-outline (fiction + narrative-nf + producer chain + hostile arms)', ok)
    else:
        _line(f'ERROR: {references}/example-reader-contract-outline not found'); failed = 1
    _line()
    return failed


def _calibration(references):
    _line('== calibration-honesty (canonical decision-audit letter: clean band w/ qualifier PASSES; a band-as-verdict WARNs default / FAILs --strict; allowlist labels + boilerplate + readiness verdict do not fire; override silences) ==')
    failed = 0
    if (references / 'example-decision-audit-letter.md').is_file():
        result = run_validator('calibration-honesty', references / 'example-decision-audit-letter.md')
        ok = result.returncode == 0
        result = run_validator('calibration-honesty', references / 'example-decision-audit-letter.md')
        output = _captured(result)  # This capture was unguarded under errexit.
        if sum('WARN: CS' in line for line in output.splitlines()) != 1:
            _line('calibration-honesty: expected exactly one CS WARN on the canonical letter'); ok = False
        if 'op-ed scores in the AI-elevated band' not in output:
            _line('calibration-honesty: the WARN is not attributed to the violating argument-decision paragraph'); ok = False
        result = run_validator('calibration-honesty', references / 'example-decision-audit-letter.md', '--strict')
        if result.returncode == 0:
            _line('calibration-honesty hostile --strict (band-as-verdict) did NOT fail'); ok = False
        failed |= _summary('calibration-honesty (canonical decision-audit letter + hostile --strict arm)', ok)
    else:
        _line(f'ERROR: {references}/example-decision-audit-letter.md not found'); failed = 1
    _line()
    return failed


def _gate_folder(references):
    _line('== canonical run folder (gate-state, escalation-check, argument-recon-prerequisite; gate engine on a temp copy) ==')
    failed = 0
    if (references / 'example-run-folder').is_dir():
        result = run_validator('gate-state', references / 'example-run-folder' / 'Diagnostic_State.meta.json')
        failed |= _relay(result)
        result = run_validator('escalation-check', references / 'example-run-folder')
        failed |= _relay(result)
        result = run_validator('argument-recon-prerequisite', references / 'example-run-folder')
        failed |= _relay(result)
        with _temporary(references / 'example-run-folder') as temp:
            result = run_validator('gate', 'run_synthesis', temp)
            failed |= _summary('gate run_synthesis (temp copy)', result.returncode == 0)
            result = run_validator('gate', 'run_spot_check', temp)
            output = _text(result)
            failed |= _check(bool(re.search(r'finding-trace +ok', output)) and not re.search(r'finding-trace +ERROR', output),
                             'gate run_spot_check finding-trace row (temp copy): PASS (integrity ok; other letter rows fail on the minimal fixture by design)',
                             'gate run_spot_check finding-trace row (temp copy): FAIL')
            result = run_validator('gate', '--attest', 'run_spot_check', temp)
            failed |= _summary('gate --attest run_spot_check finding-trace row (temp copy)',
                               bool(re.search(r'finding-trace +ok', _text(result))))
    else:
        _line(f'ERROR: {references}/example-run-folder not found'); failed = 1
    _line()
    return failed


def _risk_cost(references):
    _line('== canonical clean contract (quality-risk-triggers: no Q1-Q5 fires; hostile Q1 darkness arm) ==')
    failed = 0
    if (references / 'example-quality-risk-contract.md').is_file():
        result = run_validator('quality-risk-triggers', references / 'example-quality-risk-contract.md')
        failed |= _relay(result)
        with _temporary() as temp:
            path = temp / 'contract'
            _write(path, (references / 'example-quality-risk-contract.md').read_text(encoding='utf-8').replace('DARKNESS LEVEL: Moderate', 'DARKNESS LEVEL: HIGH'))
            result = run_validator('quality-risk-triggers', path)
            if result.returncode == 0:
                _line('quality-risk-triggers (hostile darkness arm): FAIL (expected Q1 to fire and exit non-zero)'); failed = 1
            elif 'Q1 (consent/governance)' in _text(result):
                _line('quality-risk-triggers (hostile darkness arm): PASS')
            else:
                _line('quality-risk-triggers (hostile darkness arm): FAIL (exited non-zero but Q1 not raised)'); failed = 1
    else:
        _line(f'ERROR: {references}/example-quality-risk-contract.md not found'); failed = 1
    _line()
    _line('== canonical cost-floor cap (clean over contract+preflight; hostile CF2 token-strip / CF4 goal=submit / CF1 marker-strip arms) ==')
    if (references / 'example-cost-floor-contract.md').is_file() and (references / 'example-cost-floor-preflight.md').is_file():
        result = run_validator('cost-floor', references / 'example-cost-floor-contract.md', references / 'example-cost-floor-preflight.md')
        failed |= _relay(result)
        contract = references / 'example-cost-floor-contract.md'
        preflight = references / 'example-cost-floor-preflight.md'
        with _temporary() as temp:
            path = temp / 'token-strip'
            _without_lines(contract, path, '^cost_floor_override:')
            result = run_validator('cost-floor', path, preflight)
            if result.returncode == 0:
                _line('cost-floor (hostile CF2 token-strip arm): FAIL (expected CF2 to fire and exit non-zero)'); failed = 1
            elif 'CF2' in _text(result):
                _line('cost-floor (hostile CF2 token-strip arm): PASS')
            else:
                _line('cost-floor (hostile CF2 token-strip arm): FAIL (exited non-zero but CF2 not named)'); failed = 1
            path = temp / 'submit'
            _write(path, contract.read_text(encoding='utf-8') + '\nGOAL: submit\n')
            result = run_validator('cost-floor', path, preflight)
            if result.returncode == 0:
                _line('cost-floor (hostile CF4 goal=submit arm): FAIL (expected Q5 demotion to fire and exit non-zero)'); failed = 1
            elif 'Q5' in _text(result):
                _line('cost-floor (hostile CF4 goal=submit arm): PASS')
            else:
                _line('cost-floor (hostile CF4 goal=submit arm): FAIL (exited non-zero but Q5 not named)'); failed = 1
            path = temp / 'marker-strip'
            _without_lines(contract, path, 'override: cost-floor-')
            output = _captured(run_validator('cost-floor', path, preflight))
            if 'CF1' in output and 'WARN: CF1' in output:
                result = run_validator('cost-floor', path, preflight, '--strict')
                failed |= _check(result.returncode != 0, 'cost-floor (hostile CF1 marker-strip arm): PASS',
                                 'cost-floor (hostile CF1 marker-strip arm): FAIL (expected --strict to promote the orphan WARN to ERROR)')
            else:
                _line('cost-floor (hostile CF1 marker-strip arm): FAIL (expected default CF1 orphan-token WARN)'); failed = 1
    else:
        _line(f'ERROR: {references}/example-cost-floor-contract.md or example-cost-floor-preflight.md not found'); failed = 1
    _line()
    return failed


def _coverage(references):
    _line('== canonical synthesis coverage (green + degraded-and-disclosed run folders; V2/V3 hostile arms; V5 masking arm) ==')
    failed = 0
    if (references / 'example-run-folder-coverage').is_dir() and (references / 'example-run-folder-coverage-degraded').is_dir():
        result = run_validator('synthesis-coverage', references / 'example-run-folder-coverage')
        ok = result.returncode == 0
        result = run_validator('synthesis-coverage', references / 'example-run-folder-coverage', '--strict'); ok &= result.returncode == 0
        result = run_validator('synthesis-coverage', references / 'example-run-folder-coverage-degraded'); ok &= result.returncode == 0
        result = run_validator('synthesis-coverage', references / 'example-run-folder-coverage-degraded', '--strict'); ok &= result.returncode == 0
        if not ok:
            _line('  canonical coverage folders: FAIL (expected clean PASS incl. --strict)')
        with _temporary() as temp:
            source = references / 'example-run-folder-coverage'
            h1 = temp / 'h1'; shutil.copytree(source, h1)
            path = h1 / 'Example_Synthesis_Read_Manifest_2026-01-01_opus46.md'
            _without_lines(path, path, 'Example_Pass5_Character_Audit')
            result = run_validator('synthesis-coverage', h1)
            if result.returncode == 0:
                _line('  h1 shrunk-denominator: FAIL (expected V2 exit 1)'); ok = False
            else:
                ok &= not _check('ERROR V2' in _text(result), '  h1 shrunk-denominator: OK (V2 caught)', '  h1 shrunk-denominator: FAIL (exit 1 but no V2 finding)')
            h2 = temp / 'h2'; shutil.copytree(source, h2)
            _rewrite(h2 / 'Example_Core_DE_Synthesis_2026-01-01_opus46.md', '<!-- coverage: ok -->', '<!-- coverage: degraded -->')
            result = run_validator('synthesis-coverage', h2)
            if result.returncode == 0:
                _line('  h2 marker-vs-sidecar: FAIL (expected V3 exit 1)'); ok = False
            else:
                ok &= not _check('ERROR V3' in _text(result), '  h2 marker-vs-sidecar: OK (V3 caught)', '  h2 marker-vs-sidecar: FAIL (exit 1 but no V3 finding)')
            h3 = temp / 'h3'; shutil.copytree(references / 'example-run-folder-coverage-degraded', h3)
            _rewrite(h3 / 'Example_Core_DE_Synthesis_2026-01-01_opus46.md', '<!-- coverage: degraded -->', '<!-- coverage: ok -->')
            _rewrite(h3 / 'Diagnostic_State.meta.json', '"coverage": "degraded"', '"coverage": "ok"')
            result = run_validator('synthesis-coverage', h3)
            if result.returncode == 0:
                ok &= not _check('WARN V5' in _text(result), '  h3 masking-default: OK (V5 surfaced as WARN)', '  h3 masking-default: FAIL (exit 0 but no V5 WARN)')
            else:
                _line('  h3 masking-default: FAIL (expected advisory exit 0 with V5 WARN)'); ok = False
            result = run_validator('synthesis-coverage', h3, '--strict')
            ok &= not _check(result.returncode != 0, '  h3 masking-strict: OK (caught)', '  h3 masking-strict: FAIL (expected exit 1 under --strict)')
        failed |= _summary('synthesis-coverage (canonical + hostile arms)', ok)
    else:
        _line(f'ERROR: {references}/example-run-folder-coverage(+-degraded) not found (synthesis-coverage)'); failed = 1
    _line()
    return failed


def _dispatch(references):
    _line('== canonical dispatch observability (dispatch-record: R1-R5 on the backfilled coverage run folders; parser-has-teeth; R5 hostile arm) ==')
    failed = 0
    if (references / 'example-run-folder-coverage').is_dir() and (references / 'example-run-folder-coverage-degraded').is_dir():
        import dispatch_record
        tags = dispatch_record.parse_model_tag_table((references / 'output-structure.md').read_text(encoding='utf-8'))
        ok = bool(tags) and {'codex54', 'o3', 'gemini31', 'opus46', 'sonnet46', 'haiku45'} <= tags
        _line('  parser-has-teeth: OK (6 known tags parsed from shipped output-structure.md)' if ok else f'  parser-has-teeth: FAIL (FAIL({sorted(tags)}))')
        result = run_validator('dispatch-record', references / 'example-run-folder-coverage')
        if result.returncode:
            _line('  coverage folder default: FAIL'); ok = False
        result = run_validator('dispatch-record', references / 'example-run-folder-coverage', '--strict')
        if result.returncode:
            _line('  coverage folder --strict: FAIL'); ok = False
        result = run_validator('dispatch-record', references / 'example-run-folder-coverage-degraded')
        if result.returncode:
            _line('  coverage-degraded folder default: FAIL'); ok = False
        result = run_validator('dispatch-record', references / 'example-run-folder-coverage-degraded', '--strict')
        if result.returncode:
            _line('  coverage-degraded folder --strict: FAIL'); ok = False
        with _temporary(references / 'example-run-folder-coverage') as temp:
            path = temp / 'Diagnostic_State.meta.json'
            obj = json.loads(path.read_text(encoding='utf-8')); obj.setdefault('last_session', {})['execution_mode'] = 'swarm'
            _write(path, json.dumps(obj))
            result = run_validator('dispatch-record', temp)
            if result.returncode == 0:
                ok &= not _check('WARN R5' in _text(result), '  R5 stale-mode default: OK (WARN surfaced)', '  R5 stale-mode default: FAIL (exit 0 but no WARN R5)')
            else:
                _line('  R5 stale-mode default: FAIL (expected advisory exit 0 with WARN R5)'); ok = False
            result = run_validator('dispatch-record', temp, '--strict')
            ok &= not _check(result.returncode != 0, '  R5 stale-mode --strict: OK (caught)', '  R5 stale-mode --strict: FAIL (expected exit 1 under --strict)')
        failed |= _summary('dispatch-record (canonical backfill + parser-has-teeth + R5 hostile arm)', ok)
    else:
        _line(f'ERROR: {references}/example-run-folder-coverage(+-degraded) not found (dispatch-record)'); failed = 1
    _line()
    return failed


def _specificity(references):
    _line('== canonical Pre-Letter Re-Grounding (specificity-floor: count floor + anchor floor; hostile arms) ==')
    failed = 0
    if (references / 'example-regrounded-letter.md').is_file() and (references / 'example-regrounded-ledger.md').is_file():
        result = run_validator('specificity-floor', references / 'example-regrounded-letter.md', references / 'example-regrounded-ledger.md')
        ok = result.returncode == 0
        result = run_validator('specificity-floor', references / 'example-regrounded-letter.md', references / 'example-regrounded-ledger.md', '--strict'); ok &= result.returncode == 0
        if not ok:
            _line('  canonical re-grounded pair: FAIL (expected clean PASS incl. --strict)')
        letter = references / 'example-regrounded-letter.md'; ledger = references / 'example-regrounded-ledger.md'
        with _temporary() as temp:
            path = temp / 'decay.md'
            _write(path, letter.read_text(encoding='utf-8').replace('**nine belief failures**', 'several belief failures'))
            result = run_validator('specificity-floor', path, ledger)
            if result.returncode == 0:
                _line('  h1 salience-decay: FAIL (expected count-floor exit 1)'); ok = False
            else:
                ok &= not _check('count floor' in _text(result), '  h1 salience-decay: OK (count floor caught)', '  h1 salience-decay: FAIL (exit 1 but no count-floor finding)')
            path = temp / 'drift.md'
            _write(path, letter.read_text(encoding='utf-8').replace('Ch 12 confession (sc. 30-31)', 'that confession scene'))
            result = run_validator('specificity-floor', path, ledger)
            if result.returncode == 0:
                _line('  h2 anchor-drift: FAIL (expected anchor-floor exit 1)'); ok = False
            else:
                ok &= not _check('anchor floor' in _text(result), '  h2 anchor-drift: OK (anchor floor caught)', '  h2 anchor-drift: FAIL (exit 1 but no anchor-floor finding)')
            path = temp / 'notrace.md'
            _without_lines(letter, path, 'regrounding: done')
            result = run_validator('specificity-floor', path, ledger)
            if result.returncode == 0:
                ok &= not _check('WARN' in _text(result), '  h3 no-trace-default: OK (regrounding trace surfaced as WARN)', '  h3 no-trace-default: FAIL (exit 0 but no WARN)')
            else:
                _line('  h3 no-trace-default: FAIL (expected advisory exit 0 with WARN)'); ok = False
            result = run_validator('specificity-floor', path, ledger, '--strict')
            ok &= not _check(result.returncode != 0, '  h3 no-trace-strict: OK (caught)', '  h3 no-trace-strict: FAIL (expected exit 1 under --strict)')
        failed |= _summary('specificity-floor (canonical + hostile arms)', ok)
    else:
        _line(f'ERROR: {references}/example-regrounded-letter.md / example-regrounded-ledger.md not found (specificity-floor)'); failed = 1
    _line()
    return failed



def _refutation(references):
    _line('== canonical Refutation Record (refutation-coverage + refutation-evidence + refutation-write-scope + hostile arms) ==')
    failed = 0
    if (references / 'example-run-folder').is_dir() and (references / 'example-run-folder' / 'Example_Refutation_Record_2026-01-01_opus46.md').is_file():
        result = run_validator('refutation-coverage', references / 'example-run-folder' / 'Example_Core_DE_Synthesis_2026-01-01_opus46.md', references / 'example-run-folder' / 'Example_Findings_Ledger_2026-01-01_opus46.md', references / 'example-run-folder' / 'Example_Refutation_Record_2026-01-01_opus46.md')
        ok = result.returncode == 0
        result = run_validator('refutation-evidence', references / 'example-run-folder' / 'Example_Refutation_Record_2026-01-01_opus46.md', references / 'example-run-folder' / 'Example_Manuscript_Snapshot_2026-01-01_opus46.md', '--require-snapshot'); ok &= result.returncode == 0
        result = run_validator('refutation-evidence', references / 'example-run-folder' / 'Example_Refutation_Record_2026-01-01_opus46.md'); ok &= result.returncode == 0
        result = run_validator('refutation-write-scope', references / 'example-run-folder' / 'Example_Findings_Ledger_2026-01-01_opus46.md', references / 'example-run-folder' / 'Example_Refutation_Record_2026-01-01_opus46.md'); ok &= result.returncode == 0
        if not ok:
            _line('  canonical record: FAIL (expected clean PASS on all three arms)')
        with _temporary() as temp:
            for artifact in ('Core_DE_Synthesis', 'Findings_Ledger', 'Manuscript_Snapshot', 'Refutation_Record'):
                name = f'Example_{artifact}_2026-01-01_opus46.md'
                shutil.copyfile(references / 'example-run-folder' / name, temp / name)
            letter = temp / 'Example_Core_DE_Synthesis_2026-01-01_opus46.md'
            ledger = temp / 'Example_Findings_Ledger_2026-01-01_opus46.md'
            snapshot = temp / 'Example_Manuscript_Snapshot_2026-01-01_opus46.md'
            record = temp / 'Example_Refutation_Record_2026-01-01_opus46.md'
            text = record.read_text(encoding='utf-8')
            _write(temp / 'record-h1.md', re.sub(r'<!--\s*apodictic:refutation(?![\w]).*?-->\n?', '', text, flags=re.DOTALL))
            result = run_validator('refutation-coverage', letter, ledger, temp / 'record-h1.md')
            if result.returncode == 0:
                _line('  h1 high-without-survived: FAIL (expected exit 1)'); ok = False
            else:
                ok &= not _check('Must-Fix finding F-P5-01' in _text(result), '  h1 high-without-survived: OK (caught)', '  h1 high-without-survived: FAIL (exit 1 but F-P5-01 not named)')
            _write(temp / 'record-h2.md', text.replace('For a moment she almost chooses the orchard over the debt.', 'This sentence does not occur in the snapshot.'))
            result = run_validator('refutation-evidence', temp / 'record-h2.md', snapshot, '--require-snapshot')
            if result.returncode == 0:
                _line('  h2 fabricated-quote: FAIL (expected exit 1)'); ok = False
            else:
                ok &= not _check('not found verbatim' in _text(result), '  h2 fabricated-quote: OK (caught)', '  h2 fabricated-quote: FAIL (exit 1 but no verbatim finding)')
            _write(temp / 'record-h3.md', text.replace('{"schema":"apodictic.refutation.v1",', '{"schema":"apodictic.refutation.v1","severity":"Should-Fix",'))
            result = run_validator('refutation-write-scope', ledger, temp / 'record-h3.md')
            if result.returncode == 0:
                _line('  h3 severity-write: FAIL (expected exit 1)'); ok = False
            else:
                ok &= not _check('severity key' in _text(result), '  h3 severity-write: OK (caught)', '  h3 severity-write: FAIL (exit 1 but no severity-key finding)')
            _write(temp / 'ledger-h4.md', ledger.read_text(encoding='utf-8') + '<!-- apodictic:finding\n{"schema":"apodictic.finding.v1","id":"F-P8-01","mechanism":"the subplot stalls without payoff","severity":"Should-Fix","confidence":"HIGH","evidence_refs":["Ch. 8"],"fix_class":"targeted revision","risk_if_fixed":"adjacent-scene ripple"}\n-->\n')
            _write(temp / 'record-h4.md', text.replace('"cap":15,"eligible":1,"processed":1,"bound":false', '"cap":15,"eligible":16,"processed":15,"bound":true'))
            lines = letter.read_text(encoding='utf-8').splitlines(keepends=True)
            _write(temp / 'letter-h4.md', ''.join(lines[:1]) + '<!-- refutation: not-attempted-budget F-P8-01 -->\n' + ''.join(lines[1:]))
            result = run_validator('refutation-coverage', temp / 'letter-h4.md', temp / 'ledger-h4.md', temp / 'record-h4.md')
            if result.returncode == 0:
                _line('  h4 fabricated-budget: FAIL (expected exit 1)'); ok = False
            else:
                ok &= not _check('does NOT bind' in _text(result), '  h4 fabricated-budget: OK (caught)', '  h4 fabricated-budget: FAIL (exit 1 but the recompute keystone not named)')
            result = run_validator('refutation-evidence', temp / 'record-h4.md', snapshot, '--require-snapshot')
            if result.returncode == 0:
                _line('  h4 fabricated-budget (evidence): FAIL (expected exit 1)'); ok = False
            else:
                ok &= not _check('schema-valid refutation block' in _text(result), '  h4 fabricated-budget (evidence): OK (caught)', '  h4 fabricated-budget (evidence): FAIL (exit 1 but the processed/count pin not named)')
        failed |= _summary('refutation validators (canonical + hostile arms)', ok)
    elif not (references / 'example-run-folder' / 'Example_Refutation_Record_2026-01-01_opus46.md').is_file():
        _line(f'ERROR: {references}/example-run-folder/Example_Refutation_Record_2026-01-01_opus46.md not found (refutation validators)'); failed = 1
    _line()
    return failed


def _corpus_result(command, arguments, label, *, abort=True):
    result = run_validator(command, *arguments)
    if result.returncode == 0:
        _line('  ok ' + label)
        return 0
    _line('  FAIL ' + label)
    repeated = run_validator(command, *arguments)
    _relay(repeated)
    if abort and repeated.returncode:
        raise CanonicalAbort(repeated.returncode)
    return 1


def _argument_corpus(references):
    failed = 0
    corpus = _locate('fixtures/argument-benchmark')
    if corpus is not None:
        _line('== argument-groundtruth-check (registered GT corpus) ==')
        population = sorted(corpus.glob('*/groundtruth.md')) + sorted(corpus.glob('*/*/groundtruth.md'))
        if not population:
            _line('  FAIL registered GT corpus is empty'); failed = 1
        for gt in population:
            if gt.is_file():
                slug = gt.parent.name if gt.parent.parent.name == 'argument-benchmark' else gt.parent.parent.name + '/' + gt.parent.name
                failed |= _corpus_result('argument-groundtruth-check', [gt], slug)
        for member in sorted(corpus.glob('*/clean')) + sorted(corpus.glob('*/broken')):
            if not member.is_dir():
                continue
            twin = 'broken' if member.name == 'clean' else 'clean'
            for name in ('fixture.md', 'groundtruth.md'):
                if not (member / name).is_file():
                    _line(f'  FAIL {member.parent.name}/{member.name} — incomplete member: missing {name}'); failed = 1
            if not (member.parent / twin / 'fixture.md').is_file() or not (member.parent / twin / 'groundtruth.md').is_file():
                _line(f'  FAIL {member.parent.name}/{member.name} — orphan twin: complement {twin}/ missing fixture.md or groundtruth.md'); failed = 1
        for gt in sorted(corpus.glob('*/clean/groundtruth.md')):
            if not gt.is_file():
                continue
            pair = gt.parent.parent
            broken = pair / 'broken/fixture.md'; clean = pair / 'clean/fixture.md'
            if broken.is_file() and clean.is_file():
                failed |= _corpus_result('argument-groundtruth-check', ['--repair-diff', broken, clean, gt], pair.name + ' repair-diff')
            else:
                _line(f'  FAIL {pair.name} repair-diff — missing broken/clean fixture.md'); failed = 1
        round_record = corpus / '../../../docs/argument-benchmark-calibration-round.md'
        if round_record.is_file():
            result = run_validator('argument-groundtruth-check', '--round-record', round_record, '--fixtures-dir', corpus)
            if result.returncode == 0:
                _line('  ok round-record (argument-benchmark-calibration-round.md)')
            else:
                _line('  FAIL round-record')
                result = run_validator('argument-groundtruth-check', '--round-record', round_record, '--fixtures-dir', corpus)
                _relay(result)
                if result.returncode:
                    raise CanonicalAbort(result.returncode)
                failed = 1
        _line()
    crosswalk = _locate('argument-crosswalk/crosswalk.json', file=True)
    if crosswalk is not None:
        _line('== argument-crosswalk-check (shipped crosswalk.json) ==')
        failed |= _corpus_result('argument-crosswalk-check', [crosswalk], 'crosswalk.json')
        _line()
    return failed


def _aif(references):
    failed = 0
    fixture = _locate('fixtures/argument-aif/final-audit')
    if fixture is not None:
        _line('== argument-aif-check (canonical final-audit export + source closure) ==')
        failed |= _corpus_result('argument-aif-check', [fixture / 'export.json', '--source', fixture / 'argument-state.md'], 'final-audit/export.json')
        with _temporary() as temp:
            output = temp / 'apodictic-aif.json'
            output.touch()
            for name in ('final-over-predraft', 'predraft-complete', 'predraft-partial'):
                source = fixture.parent / name / 'argument-state.md'
                result = run_validator('argument-aif-export', source, '--state-schema', '0.2.0', '--out', output)
                if result.returncode == 0:
                    result = run_validator('argument-aif-check', output, '--source', source)
                failed |= _check(result.returncode == 0, '  ok ' + name, '  FAIL ' + name)
            result = run_validator('argument-spine', fixture.parent / 'predraft-complete/argument-state.md', '--strict')
            failed |= _check(result.returncode == 0, '  ok predraft-complete (argument-spine --strict)', '  FAIL predraft-complete (argument-spine --strict)')
            for name in ('mixed-support', 'mixed-warrant', 'carrier-disagreement', 'bad-carrier-missing', 'bad-carrier-enum', 'bad-carrier-extra', 'fallback-c99', 'extra-final-record'):
                source = fixture.parent / name / 'argument-state.md'
                # A missing hostile is not evidence that its mixed population was rejected.
                if not source.is_file():
                    _line(f'  FAIL {name} (required hostile fixture missing)'); failed = 1
                    continue
                result = run_validator('argument-aif-export', source, '--state-schema', '0.2.0', '--out', output)
                failed |= _check(result.returncode != 0, f'  ok {name} (rejected)', f'  FAIL {name} (hostile mixed population unexpectedly exported)')
        _line()
    return failed


def _aif_reference(references):
    failed = 0
    if (references / 'example-argument-aif-export.json').is_file():
        result = run_validator('argument-aif-check', references / 'example-argument-aif-export.json', '--source', references / 'example-argument-aif-state.md')
        if result.returncode:
            _line('  FAIL example-argument-aif-export.json')
            result = run_validator('argument-aif-check', references / 'example-argument-aif-export.json', '--source', references / 'example-argument-aif-state.md')
            _relay(result)
            if result.returncode:
                raise CanonicalAbort(result.returncode)
            failed = 1
    return failed


def _agd_fiction(references):
    failed = 0
    corpus = _locate('fixtures/argument-agd')
    if corpus is not None:
        _line('== argument-agd (worked fixtures, anchors resolved, --strict) ==')
        population = sorted(corpus.glob('*/argument-state.md'))
        if not population:
            _line('  FAIL worked AGD fixture population is empty'); failed = 1
        for state in population:
            fixture = state.parent
            scan = fixture / 'agd_move_scan.json'
            if not scan.is_file() and re.search(r'^Scan: consulted', state.read_text(encoding='utf-8'), re.MULTILINE):
                _line(f"  FAIL {fixture.name} — 'Scan: consulted' claimed but no agd_move_scan.json shipped (the n-cross-check would silently skip)"); failed = 1
                continue
            arguments = [state, '--source', fixture / 'source.md']
            if scan.is_file():
                arguments.extend(['--scan', scan])
            arguments.append('--strict')
            failed |= _corpus_result('argument-agd', arguments, fixture.name)
        _line()
    corpus = _locate('fixtures/fiction-benchmark')
    if corpus is not None:
        _line('== fiction-groundtruth-check (registered GT corpus) ==')
        population = sorted(corpus.glob('*/groundtruth.md')) + sorted(corpus.glob('*/*/groundtruth.md'))
        if not population:
            _line('  FAIL registered fiction GT corpus is empty'); failed = 1
        for gt in population:
            if gt.is_file():
                failed |= _corpus_result('fiction-groundtruth-check', [gt], gt.parent.parent.name + '/' + gt.parent.name)
        _line()
    return failed


def _final_checks(references):
    failed = 0
    _line('== argument-carve-behavior-preservation (carve-equivalence: pre-carve fixture vs goldens) ==')
    result = run_validator('argument-carve-behavior-preservation')
    failed |= _relay(result)
    _line()
    _line('== schema-coverage (real schemas dir) ==')
    result = run_validator('schema-coverage')
    failed |= _relay(result)
    _line()
    fixture = _locate('fixtures/stance-calibration/clean')
    _line('== stance-calibration (canonical AT5 ledger + Argument_State join) ==')
    if fixture is not None:
        result = run_validator('stance-calibration', fixture / 'Findings_Ledger.md', '--argument-state', fixture / 'Argument_State.md')
        if result.returncode == 0:
            _line('  ok (register floor + prescriptive cash-out block)')
        else:
            _line('  FAIL')
            _relay(run_validator('stance-calibration', fixture / 'Findings_Ledger.md', '--argument-state', fixture / 'Argument_State.md'))
            failed = 1
    else:
        _line('  FAIL (fixture directory not found)'); failed = 1
    _line()
    fixture = _locate('register-stance-pilot')
    _line('== stance-calibration (E7 strict blind pairs) ==')
    if fixture is not None:
        for pair in ('e7-strict-a', 'e7-strict-b'):
            failed |= _corpus_result('stance-calibration', [fixture / pair / 'Findings_Ledger.md', '--argument-state', fixture / pair / 'Argument_State.md'], pair, abort=False)
    else:
        _line('  FAIL (E7 strict fixture root not found)'); failed = 1
    _line()
    suite = next((path for path in (HERE / '../../../evals/fixtures/argument-reconstruction',
                                    HERE / '../evals/fixtures/argument-reconstruction')
                  if (path / 'run_cases.py').is_file()), None)
    if suite is not None:
        _line('== argument-reconstruction (synthetic ledger and recovery histories) ==')
        failed |= _relay(_producer(suite / 'run_cases.py', '--engine', HERE / 'approval_graph.py'))
        _line('== argument-reconstruction-draft (packet, publication and isolated transport) ==')
        failed |= _relay(_producer(suite / 'run_increment3.py', '--engine', HERE / 'reconstruction_draft.py'))
        failed |= _relay(_producer(suite / 'run_drafter_transport.py', '--engine', HERE / 'reconstruction_drafter.py'))
        _line()
    elif _evals() is not None:
        _line('FAIL: reconstruction behavioral suite missing from repository checkout'); failed = 1
    _line('== validator-conventions (meta-linter: M2 resolver hygiene, M4 no orphan schema, M5 override hygiene, M6 code-span hygiene, M7 single-Firewall, M8 severity-vocab SSoT) ==')
    result = run_validator('validator-conventions')
    if result.returncode == 0:
        _line('  ok (fleet conventions hold)')
    else:
        _line('  FAIL'); _relay(run_validator('validator-conventions')); failed = 1
    _line()
    return failed


def run_canonical() -> int:
    references = next((path for path in (HERE / '../skills/core-editor/references',
                                        HERE / '../plugins/apodictic/skills/core-editor/references')
                       if path.is_dir()), HERE / '../skills/core-editor/references')
    failed = 0
    template_references = next((path for path in (HERE / '../skills/core-editor/references',
                                                 HERE / '../plugins/apodictic/skills/core-editor/references')
                                if (path / 'diagnostic-state-meta-template.json').is_file()), references)
    result = _registry_templates(template_references)
    failed |= result
    if references.is_dir():
        result = _framework(references)
        failed |= result
        result = _position_pair(references)
        failed |= result
        result = _letters(references)
        failed |= result
        result = _coaching(references)
        failed |= result
        result = _voice_world_state(references)
        failed |= result
        result = _regression(references)
        failed |= result
        result = _predraft(references)
        failed |= result
        result = _genre(references)
        failed |= result
        result = _scene_reader_annotation(references)
        failed |= result
        result = _producer_chain(references)
        failed |= result
        result = _reanchor(references)
        failed |= result
        result = _roundtrip(references)
        failed |= result
        result = _dispositions(references)
        failed |= result
        result = _exports(references)
        failed |= result
        result = _reader_outline(references)
        failed |= result
        result = _calibration(references)
        failed |= result
        result = _timeline(references)
        failed |= result
        result = _gate_folder(references)
        failed |= result
        result = _risk_cost(references)
        failed |= result
        result = _coverage(references)
        failed |= result
        result = _dispatch(references)
        failed |= result
        result = _specificity(references)
        failed |= result
        result = _refutation(references)
        failed |= result
    else:
        _line('ERROR: could not locate core-editor/references for canonical validator runs')
        failed = 1
    result = _argument_corpus(references)
    failed |= result
    result = _aif(references)
    failed |= result
    # The AIF example historically selects these mirrors in reverse order.
    aif_references = next((path for path in (HERE / '../plugins/apodictic/skills/core-editor/references',
                                            HERE / '../skills/core-editor/references')
                           if (path / 'example-argument-aif-export.json').is_file()), references)
    result = _aif_reference(aif_references)
    failed |= result
    result = _agd_fiction(references)
    failed |= result
    result = _final_checks(references)
    failed |= result
    return int(bool(failed))
