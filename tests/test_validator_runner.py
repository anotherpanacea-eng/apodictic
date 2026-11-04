"""Behavioral contract tests using only invented text/public validator fixtures."""
import ast
import copy
import json
import os
from pathlib import Path
import queue
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "plugins/apodictic/scripts/validator_runner.py"
FIXTURES = ROOT / "tests/fixtures/validators"
PYTHON = sys.executable
LEAVES = ("tone-check", "synthesis-sections", "severity-floor", "decision-layer-check",
          "author-facing-lint", "ledger-check", "ledger-consolidation", "audit-signal-propagation",
          "underdiagnosis-triggers", "timeline-arithmetic", "timeline-anchor-conflict", "calibration-honesty", "legal-risk", "scene-ethics", "fiction-groundtruth-check", "deficit-lock")
REFERENCE = Path("skills/core-editor/references/pass-dependencies.md")
SIGNAL_APPENDIX = "\n## Appendix A\n### Reception Risk Audit\nhard gate at L42\n"
SIGNAL_SHOULD = "Should-Fix: Reception Risk needs revision.\n" + SIGNAL_APPENDIX
SIGNAL_TWO = SIGNAL_APPENDIX + "### Compression Audit\nhard gate at L71\n"
SIGNAL_MARKER = "<!-- override:audit-propagation-reception-risk -->"
SIGNAL_CASES = [
    ("hard-gate-should", SIGNAL_SHOULD, 1),
    ("hard-gate-must", SIGNAL_SHOULD.replace("Should-Fix", "Must-Fix"), 0),
    ("shared-evidence", "Must-Fix: revise L42.\n" + SIGNAL_APPENDIX, 0),
    ("wrong-evidence", "Must-Fix: revise L43.\n" + SIGNAL_APPENDIX, 1),
    ("wrong-audit", "Must-Fix: Compression needs revision.\n" + SIGNAL_APPENDIX, 1),
    ("floor-should", SIGNAL_SHOULD.replace("hard gate", "Must-Fix floor"), 1),
    ("high-satisfied", SIGNAL_SHOULD.replace("hard gate", "HIGH signal"), 0),
    ("high-absent", SIGNAL_APPENDIX.replace("hard gate", "HIGH signal"), 1),
    ("live-override", SIGNAL_MARKER + SIGNAL_APPENDIX, 0),
    ("inline-override", "`" + SIGNAL_MARKER + "`" + SIGNAL_APPENDIX, 1),
    ("fenced-override", "```\n" + SIGNAL_MARKER + "\n```" + SIGNAL_APPENDIX, 1),
    ("appendix-override", SIGNAL_APPENDIX + SIGNAL_MARKER, 1),
    ("suffix-override", SIGNAL_MARKER.replace("risk", "risk-suffix") + SIGNAL_APPENDIX, 1),
    ("one-of-two-overridden", SIGNAL_MARKER + SIGNAL_TWO, 1),
    ("legacy-absent", "hard gate\n", 1),
    ("legacy-satisfied", "hard gate\nMust-Fix: revise the opening.\n", 0),
]
SYNTHESIS = "".join("## %s\n\nbody\n\n" % h for h in (
    "Development Edit", "The Short Version", "What the Book Does Best", "What Needs Work",
    "Additional Observations", "Revision Checklist", "Protected Elements", "Author Decisions",
    "Control Questions", "The Strongest Case Against", "Stress Test", "Appendix A",
    "Appendix B", "Appendix C"))
LEDGER = "## Pass 2\n" + "".join("### %s\n" % h for h in (
    "Notable Findings", "Data Artifacts for Letter Reference", "Cross-Pass Connections",
    "Unresolved Questions", "Audit Triggers"))
WEAK = "Weak at High"
CONVERGENCE = "opacity opacity opacity"
CONVERGENCE_MARKER = "<!-- override:underdiagnosis-trigger-convergence -->"
SEVERITY_CHILD_MARKER = "<!-- override:severity-floor-weak-axis -->"
SEVERITY_PARENT_MARKER = "<!-- override:underdiagnosis-trigger-severity-floor -->"
PROPAGATION_PARENT_MARKER = "<!-- override:underdiagnosis-trigger-propagation -->"
UNDERDIAGNOSIS_BODY = "Must-Fix: unrelated L99.\nShould-Fix: Reception Risk L42.\n"
# Expected warning/error prefixes protect the six actual paths and composition,
# independently of the native parity oracle. These are invented text controls.
UNDERDIAGNOSIS_CASES = [
    ("two-occurrences", "opacity opacity", 0, []),
    ("three-occurrences", CONVERGENCE, 1, ["ERROR: Trigger #1 (convergence)"]),
    ("convergence-body-must", CONVERGENCE + "\nMust-Fix: revise.", 0, []),
    ("alert-should", "Should-Fix: revise pacing.\nAlert finding", 1, ["ERROR: Trigger #2 (hard-gate)"]),
    ("alert-must", "Must-Fix: revise pacing.\nAlert finding", 0, []),
    ("character-only", "Character pass climax", 0, []),
    ("character-and-structure", "Character pass climax\nStructure pass climax", 1,
     ["ERROR: Trigger #3 (final-third)"]),
    ("one-axis", "series", 0, []),
    ("two-axes", "series representation", 1, ["ERROR: Trigger #4 (multi-axis)"]),
    ("severity-error", WEAK, 1, ["ERROR: Trigger #5 (severity-floor)"]),
    ("severity-child-only", WEAK + "\n" + SEVERITY_CHILD_MARKER, 1,
     ["ERROR: Trigger #5 (severity-floor)"]),
    ("severity-parent-only", WEAK + "\n" + SEVERITY_PARENT_MARKER, 0,
     ["WARN: Trigger #5 (severity-floor)"]),
    ("severity-both", WEAK + "\n" + SEVERITY_CHILD_MARKER + "\n" + SEVERITY_PARENT_MARKER, 0,
     ["WARN: Trigger #5 (severity-floor)"]),
    ("severity-appendix-must", WEAK + "\n## Appendix A\nMust-Fix", 0, []),
    ("propagation-error", UNDERDIAGNOSIS_BODY + SIGNAL_APPENDIX, 1,
     ["ERROR: Trigger #6 (propagation)"]),
    ("propagation-child-only", UNDERDIAGNOSIS_BODY + SIGNAL_MARKER + SIGNAL_APPENDIX, 1,
     ["ERROR: Trigger #6 (propagation)"]),
    ("propagation-parent-only", UNDERDIAGNOSIS_BODY + PROPAGATION_PARENT_MARKER + SIGNAL_APPENDIX, 0,
     ["WARN: Trigger #6 (propagation)"]),
    ("propagation-both", UNDERDIAGNOSIS_BODY + SIGNAL_MARKER + "\n" +
     PROPAGATION_PARENT_MARKER + SIGNAL_APPENDIX, 0, ["WARN: Trigger #6 (propagation)"]),
    ("propagation-matched-evidence", "Must-Fix: revise L42.\n" + SIGNAL_APPENDIX, 0, []),
    ("mixed-warning-and-error", CONVERGENCE + "\nseries representation\n" + CONVERGENCE_MARKER, 1,
     ["WARN: Trigger #1 (convergence)", "ERROR: Trigger #4 (multi-axis)"]),
    ("live-parent", CONVERGENCE + "\n" + CONVERGENCE_MARKER, 0,
     ["WARN: Trigger #1 (convergence)"]),
] + [
    (label, CONVERGENCE + "\n" + marker, 1, ["ERROR: Trigger #1 (convergence)"])
    for label, marker in (
        ("inline-parent", "`" + CONVERGENCE_MARKER + "`"),
        ("fenced-parent", "~~~\n" + CONVERGENCE_MARKER + "\n~~~"),
        ("appendix-parent", "## Appendix A\n" + CONVERGENCE_MARKER),
        ("suffix-parent", CONVERGENCE_MARKER.replace("convergence", "convergence-suffix")))
]
# Invented adversarial inputs per leaf; shipped fixtures and SHARED are added to each.
CASES = {
    "tone-check": [
        "The pacing needs work.", "STUNNING", "`flawless`", "> triumph", "# Appendix A\nperfection",
        "MASTERPIECE Stunning FLAWLESS Clean Bill TOUR DE FORCE Triumph PERFECTION " * 2,
        "````\n```\nflawless\n````\ntriumph", "~~~\r\nmasterpiece\r\n~~~\r\nSTUNNING",
        "# Appendixes A\nperfection", " > clean bill\rflawless"],
    "synthesis-sections": [
        SYNTHESIS, SYNTHESIS.replace("## Stress Test\n\nbody\n\n", ""), SYNTHESIS.upper(),
        SYNTHESIS.replace("## Stress Test\n", "## **Stress Test**\n"),
        SYNTHESIS.replace("## Stress Test\n", "## Notes on the Stress Test approach\n"),
        SYNTHESIS.replace("## ", "##\t"), SYNTHESIS.replace("## ", "##### "),
        SYNTHESIS.replace("## Appendix A\n", "## Appendix Alpha\n"),
        SYNTHESIS.replace("## Appendix A\n", "## Appendix A_\n"),
        SYNTHESIS.replace("## Appendix A\n", "## Appendix A\u0301\n"),
        SYNTHESIS.replace("\n", "\r\n"), "## Appendix Alpha\n" * 8191],
    "severity-floor": [
        WEAK, "Weak at Medium", "Systemic Must-Fix Strong Fit",
        "Strong Fit Should-Fix Should-Fix Should-Fix justification",
        WEAK + "\n<!-- override:severity-floor-weak-axis -->",
        WEAK + "\n## Appendix A\n<!-- override:severity-floor-weak-axis -->",
        WEAK + "\n`<!-- override:severity-floor-weak-axis -->`",
        WEAK + "\n<!-- override:severity-floor-weak-axis-suffix -->",
        "Wеak at High", "Must-Fix " * 29120 + "Systemic Must-Fix Strong Fit"],
    "decision-layer-check": [
        "## Protected Elements\n- One\n- Two\n- Three\n## Author Decisions\n- Keep\n- Cut\n"
        "- Defer\n## Appendix A\nExample.\n" + suffix for suffix in ("", "Claim Ladder",
                                                                      "```\nClaim Ladder\n```")] + [
        "## What Needs Work\nMust-Fix: invented pacing gap.\n",
        "## Control Questions\n1. One\n<!-- override:decision-layer-control-questions -->\n"],
    "author-facing-lint": [
        "Pass 11F\nQF-7\n[HIGH CONFIDENCE]\nP3", "weak motivation (QF-7)\nQF-7",
        "Pass 11F — weak motivation\nPass 11F", "Pass ١٢F\nFM-A١٠\n[UNCERTAIN]",
        "QF-7\n## Appendix A\nCR-8", "  <!-- QF-7 -->\n> CR-8\n```\nP4\n```",
        "QF-7\n<!-- override: author-facing-lint -->",
        "QF-7\n`<!-- override: author-facing-lint -->`"],
    "ledger-check": [
        LEDGER, "## Pass 2\n### Audit Triggers\n### Notable Findings\n", LEDGER.rstrip("\n"),
        "## Pass 0\n", "## Pass 10\n", "## Pass 00\n", "## Pass 2\nprose ### Notable Findings\n",
        "## Pass 2\n#### **Notable Findings**\n", "## Pass ١\n", "Unrecognized text"],
    "ledger-consolidation": [
        # The unchanged helper recognizes convergence annotations anywhere in the text.
        "## Mechanism: recurring delay\nMust-Fix\n"
        "## Mechanism: repeated detour\nMust-Fix\n" + annotation
        for annotation in ("", "(confirmed by Pass 1, Pass 2)\n")
    ] + [
        "## Mechanism: recurring delay\n(confirmed by Pass 1, Pass 2)\n"
        "Must-Fix\nShould-Fix\n" + annotation for annotation in ("", "collated\n")
    ] + [
        # Only the marker representation changes; raw aggregation fails without it.
        "## Pass 1 Findings\n## Pass 2 Findings\n## Pass 3 Findings\n" + marker
        for marker in ("<!-- override:ledger-consolidation-raw-aggregate -->",
                       "`<!-- override:ledger-consolidation-raw-aggregate -->`",
                       "<!-- override:ledger-consolidation-raw-aggregate-suffix -->")
    ] + [
        # One text supplies no raw-ledger item count for the optional reduction check.
        "## Mechanism: recurring delay\n(confirmed by Pass 1, Pass 2)\nMust-Fix\n"
        "- Invented opening delay.\n- Invented middle delay.\n- Invented closing delay.\n"],
    "audit-signal-propagation": [text for _, text, _ in SIGNAL_CASES],
    "underdiagnosis-triggers": [text for _, text, _, _ in UNDERDIAGNOSIS_CASES],
}
# Preserve override warnings exactly: timeline summaries can be empty.
TIMELINE_CASES = {}
for leaf, conflict, slug in (
    ("timeline-arithmetic", "| Scene | -2 hours |\n", "timeline-arithmetic-conflict"),
    ("timeline-anchor-conflict", "Anchor (contradicts another)\n", "timeline-anchor-conflict"),
):
    marker = "<!-- override: %s -->" % slug
    TIMELINE_CASES[leaf] = [(conflict, 1), (marker + "\n" + conflict, 0)] + [
        (wrapped + "\n" + conflict, 1) for wrapped in
        ("`" + marker + "`", "~~~\n" + marker + "\n~~~", marker.replace(slug, slug + "-suffix"))
    ] + [(conflict + "## Section 8: Diff Notes\n" + marker, 1),
         ("## Section 8: Diff Notes\n" + conflict, 0)]
    CASES[leaf] = [text for text, _ in TIMELINE_CASES[leaf]]

# Grouped day numbers must stay numeric, and uncertainty/nonlinearity remains
# the canonical helper's decision rather than a runner-side interpretation.
for leaf, fixture in (("timeline-arithmetic", "silent_arithmetic"),
                      ("timeline-anchor-conflict", "silent_anchor")):
    example = (FIXTURES / ("tl.fail.%s.%s.md" % (leaf, fixture))).read_text()
    CASES[leaf] += [example.replace("Day 1", "Day 1,000").replace("Day 2", "Day 1,001"),
                    example.replace("\n", "\r\n"), example.replace("\n", "\r")]

# Public canonical self-test phrases; these test rendered claim syntax, not a detector.
CALIBRATION_CLAIMS = [
    "the manuscript scores in the AI-elevated band",
    "this is a calibrated band for the work",
    "the story sits above the threshold",
    "the aggregate score confirms the draft is AI-patterned",
]
CALIBRATION_OVERRIDE = "<!-- override: calibration-honesty -->"
CALIBRATION_CASES = [(text, 1) for text in CALIBRATION_CLAIMS] + [
    (text + " — uncalibrated, provenance only", 0) for text in CALIBRATION_CLAIMS
] + [
    ("`" + CALIBRATION_CLAIMS[0] + "`", 0),
    ("~~~\n" + CALIBRATION_CLAIMS[0] + "\n~~~", 0),
    ("<!-- " + CALIBRATION_CLAIMS[0] + " -->", 0),
    (CALIBRATION_CLAIMS[0] + "\n" + CALIBRATION_OVERRIDE, 0),
    (CALIBRATION_CLAIMS[0] + "\n`" + CALIBRATION_OVERRIDE + "`", 1),
    (CALIBRATION_CLAIMS[0] + "\n" + CALIBRATION_OVERRIDE.replace("honesty", "honesty-suffix"), 1),
    ("\n\n".join(CALIBRATION_CLAIMS), 4),
    (CALIBRATION_CLAIMS[0] + "\n\nuncalibrated, provenance only", 1),
    ("**Verdict:** Excellent Fit for the target market.", 0),
]
CALIBRATION_CASES += [(text.replace("\n", "\r\n"), count)
                      for text, count in list(CALIBRATION_CASES) if "\n" in text]
CASES["calibration-honesty"] = [text for text, _ in CALIBRATION_CASES]

def artifact_block(kind, obj):
    return "<!-- apodictic:%s\n%s\n-->" % (kind, json.dumps(obj, ensure_ascii=False))


LEGAL_ITEM = dict(schema="apodictic.legal_risk.v1", id="LR-01", risk_class="privacy",
                  severity="monitor", concern="Invented example", escalation_trigger="review",
                  disposition="flag for legal review")
ETHICS_ITEM = dict(schema="apodictic.scene_ethics.v1", id="EP-01", subject="Invented person",
                   depiction="Invented encounter", consent_status="obtained", handling="anonymize")
SCHEMA_CASES = {}
for leaf, kind, obj, prefix in (
    ("legal-risk", "legal_risk", LEGAL_ITEM, "This is not legal advice.\n"),
    ("scene-ethics", "scene_ethics", ETHICS_ITEM, ""),
):
    block = artifact_block(kind, obj)
    SCHEMA_CASES[leaf] = [(prefix + block, 0), (prefix + block + "\n" + block, 1),
        (prefix + artifact_block(kind, dict(obj, id="bad")), 1),
        (prefix + artifact_block(kind, {k: v for k, v in obj.items() if k != "id"}), 1),
        (prefix + artifact_block(kind, []), 1),
        (prefix + "<!-- apodictic:%s\n{broken\n-->" % kind, 1)]
SCHEMA_CASES["legal-risk"] += [
    (artifact_block("legal_risk", LEGAL_ITEM), 1),
    ("<!-- not legal advice -->\n" + artifact_block("legal_risk", LEGAL_ITEM), 1),
    ("Not legal advice.\n" + artifact_block("legal_risk", dict(LEGAL_ITEM, severity="review-now",
                                                              disposition="hold", concern="fair use")), 0),
]
for consent in ("obtained", "sought-pending", "not-sought", "not-applicable"):
    for fairness in ("", "Invented fairness rationale"):
        SCHEMA_CASES["scene-ethics"].append((artifact_block("scene_ethics", dict(
            ETHICS_ITEM, handling="as-is", consent_status=consent, fairness_check=fairness)), 0))
for leaf, kind, obj, slug in (
    ("legal-risk", "legal_risk", dict(LEGAL_ITEM, disposition="this is not defamatory"), "legal-advice-drift"),
    ("scene-ethics", "scene_ethics", dict(ETHICS_ITEM, handling="as-is", consent_status="not-sought"),
     "scene-ethics-unresolved"),
):
    marker = "<!-- override: %s %s -->" % (slug, obj["id"])
    for override in (marker, "`" + marker + "`", marker.replace(slug, slug + "-suffix"),
                     marker.replace(obj["id"], obj["id"] + "1"), "~~~\n" + marker + "\n~~~"):
        SCHEMA_CASES[leaf].append(("Not legal advice.\n" + override + "\n" + artifact_block(kind, obj), 0))
for leaf, cases in SCHEMA_CASES.items():
    cases += [(text.replace("\n", "\r\n"), code) for text, code in list(cases)]
    CASES[leaf] = [text for text, _ in cases]

# Public benchmark answer-key fixtures exercise the text-only mechanical contract.
FICTION_ROOT = ROOT / "evals/fixtures/fiction-benchmark"
FICTION_BROKEN = (FICTION_ROOT / "pov-break/broken/groundtruth.md").read_text(encoding="utf-8")
FICTION_CASES = [(FICTION_BROKEN, 0)] + [
    ((FICTION_ROOT / name / "groundtruth.md").read_text(encoding="utf-8"), 0)
    for name in ("pov-break/clean", "yellow-wallpaper-voice-control")
] + [(FICTION_BROKEN.replace(old, new), 1) for old, new in (
    ("## FGT5", "## Missing5"),
    ("[gt_class: A]", "[gt_class: C]"),
    ("[reliability_status: deterministic]", "[reliability_status: provisional_author]"),
    ("DEFECT-AS-PLANTED", "SOUND"),
)] + [(FICTION_BROKEN.replace("F-P7-*", "F-P10-*").replace("F-P5-*", "F-P10-*"), 1)]
FICTION_CASES += [(text.replace("\n", "\r\n"), code) for text, code in list(FICTION_CASES)]
CASES["fiction-groundtruth-check"] = [text for text, _ in FICTION_CASES]
FINDING_ITEM = dict(schema="apodictic.finding.v1", id="F-P5-01", mechanism="Invented pacing gap",
                    severity="Must-Fix", confidence="HIGH", evidence_refs=["Ch 1"],
                    fix_class="review", risk_if_fixed="Invented tradeoff")
DEFICIT_PROSE = "- Must-Fix: invented pacing gap.\n"
DEFICIT_CASES = [("", 0), (DEFICIT_PROSE, 1),
    (DEFICIT_PROSE + artifact_block("finding", FINDING_ITEM), 0),
    (DEFICIT_PROSE * 2 + artifact_block("finding", FINDING_ITEM), 1),
    (DEFICIT_PROSE + "<!-- apodictic:finding\n{broken\n-->", 1),
] + [(DEFICIT_PROSE + artifact_block("finding", obj), 1) for obj in (
    {k: v for k, v in FINDING_ITEM.items() if k != "id"},
    dict(FINDING_ITEM, schema="apodictic.finding.v2"),
    dict(FINDING_ITEM, severity="Could-Fix"),
    dict(FINDING_ITEM, evidence_refs=[]),
)]
DEFICIT_CASES += [(text.replace("\n", "\r"), code) for text, code in list(DEFICIT_CASES)]
CASES["deficit-lock"] = [text for text, _ in DEFICIT_CASES]

SHARED = ["", "masterpiece", "雪 😀\r\n" + WEAK + "\rQF-7\n" + LEDGER, "x" * 262144, "\n" * 8191]


def validation(id="r1", text="The pacing needs work.", validator="tone-check"):
    return {"protocol": 1, "type": "validate", "id": id, "validator": validator, "text": text}


def cancel(target="r1", id="c1"):
    return {"protocol": 1, "type": "cancel", "id": id, "target": target}


def frame(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode() + b"\n"


class Client:
    def __init__(self, script=SCRIPT, env=None, cwd=None):
        self.child = subprocess.Popen([PYTHON, "-I", "-S", str(script)],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            env=env, cwd=cwd)
        self.lines = queue.Queue()
        self.finished = None
        def read():
            for line in self.child.stdout:
                self.lines.put(line)
            self.lines.put(None)
        self.reader = threading.Thread(target=read, daemon=True)
        self.reader.start()

    def send(self, value):
        self.raw(frame(value))

    def raw(self, value):
        self.child.stdin.write(value)
        self.child.stdin.flush()

    def next(self, timeout=8):
        value = self.lines.get(timeout=timeout)
        if value is None:
            raise AssertionError("Missing protocol result")
        assert value.endswith(b"\n") and len(value) <= 32768
        return json.loads(value)

    def end(self):
        if self.finished is not None:
            return self.finished
        if not self.child.stdin.closed:
            self.child.stdin.close()
        status = self.child.wait(timeout=5)
        self.reader.join(timeout=2)
        remainder = []
        while not self.lines.empty():
            item = self.lines.get_nowait()
            if item is not None:
                remainder.append(json.loads(item))
        stderr = self.child.stderr.read()
        self.child.stdout.close()
        self.child.stderr.close()
        self.finished = (status, remainder, stderr)
        return self.finished

    def close(self):
        if self.finished is not None:
            return
        if self.child.poll() is None:
            self.child.terminate()
        try:
            self.end()
        except (OSError, subprocess.TimeoutExpired):
            self.child.kill()
            self.child.wait()


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="m3-synthetic-")
        self.root = Path(self.tmp.name)
        self.scripts = self.root / "plugins/apodictic/scripts"
        self.schemas = self.scripts.parent / "schemas"
        self.scripts.mkdir(parents=True)
        self.schemas.mkdir()
        for name in ("validator_runner.py", "letter_checks.py", "timeline_checks.py", "calibration_honesty.py", "legal_risk.py", "scene_ethics.py",
                     "apodictic_artifacts.py", "fiction_groundtruth.py", "honesty_check.py",
                     "severity_vocab.py", "override_marker.py", "validate.py"):
            shutil.copyfile(SCRIPT.parent / name, self.scripts / name)
        for schema_id in ("apodictic.legal_risk.v1", "apodictic.scene_ethics.v1", "apodictic.finding.v1"):
            name = schema_id + ".schema.json"
            shutil.copyfile(SCRIPT.parent.parent / "schemas" / name, self.schemas / name)
        self.metadata = self.schemas / "validator-runtime-inventory.json"
        shutil.copyfile(SCRIPT.parent.parent / "schemas/validator-runtime-inventory.json", self.metadata)
        self.reference = self.scripts.parent / REFERENCE
        self.reference.parent.mkdir(parents=True)
        shutil.copyfile(SCRIPT.parent.parent / REFERENCE, self.reference)
        self.script = self.scripts / "validator_runner.py"
        self.clients = []

    def tearDown(self):
        for client in self.clients:
            client.close()
        self.tmp.cleanup()

    def client(self, **kwargs):
        c = Client(**kwargs)
        self.clients.append(c)
        return c

    def error(self, value, code):
        self.assertEqual(value["available"], False)
        self.assertIsNone(value["result"])
        self.assertEqual(value["error"], {"code": code, "message": "Validator unavailable: %s." % code})

    def helper(self, body):
        """Replace the copied installation's helper with a synthetic one for every leaf."""
        (self.scripts / "letter_checks.py").write_text(
            body + "\nCHECKS = dict.fromkeys(%r, check)\nRAW_CHECKS = {'ledger-check': "
            "lambda text: (lambda r: (int(bool(r[0])), r[1] + [r[2]]))(check(text))}\n" % (tuple(leaf for leaf in LEAVES if leaf != "ledger-check"),))

        (self.scripts / "timeline_checks.py").write_text(
            body + "\nSINGLE_FILE_CHECKS = dict.fromkeys(%r, check)\n" %
            (("timeline-arithmetic", "timeline-anchor-conflict"),))

        (self.scripts / "calibration_honesty.py").write_text(
            body + "\ndef scan(text):\n r = check(text)\n return int(bool(r[0])), r[1] + [r[2]]\n")

        for name, entry in (("legal_risk.py", "register"), ("scene_ethics.py", "plan")):
            (self.scripts / name).write_text(body +
                "\ndef %s(text):\n r = check(text)\n return int(bool(r[0])), r[1] + [r[2]]\n" % entry)

        (self.scripts / "fiction_groundtruth.py").write_text(body + "\nfiction_groundtruth_check = check\n")
        (self.scripts / "honesty_check.py").write_text(body + "\ndef deficit_lock(text):\n return check(text)[:2]\n")

    def sleeping(self):
        self.pidfile = self.root / "synthetic-worker.pid"
        self.pidfile.unlink(missing_ok=True)
        self.helper("import os,time\ndef check(text):\n"
                    " if text == 'sleep':\n"
                    "  open(%r,'w').write(str(os.getpid()))\n"
                    "  time.sleep(30)\n"
                    " return [],[], 'synthetic OK', 'synthetic FAILED'\n" % str(self.pidfile))

    def pid(self):
        until = time.monotonic() + 3
        while time.monotonic() < until:
            if self.pidfile.exists() and self.pidfile.read_text():
                return int(self.pidfile.read_text())
            time.sleep(.01)
        self.fail("Synthetic worker did not start")

    def dead(self, pid):
        # On the development POSIX host kill(0) also sees zombies: absence proves reaping.
        with self.assertRaises(ProcessLookupError):
            os.kill(pid, 0)

    def inventory_check(self):
        return subprocess.run([PYTHON, "-I", "-S", str(self.script), "--check-inventory"],
                              capture_output=True, cwd=self.root,
                              env=dict(os.environ, PATH="", PYTHONPATH=str(self.root))).returncode

    def test_every_leaf_matches_the_native_cli(self):
        # Foreign cwd, empty PATH and injected PYTHONPATH/site files cannot change a leaf.
        (self.root / "letter_checks.py").write_text("raise RuntimeError('cwd injection')\n")
        (self.root / "timeline_checks.py").write_text("raise RuntimeError('cwd injection')\n")
        (self.root / "calibration_honesty.py").write_text("raise RuntimeError('cwd injection')\n")
        for name in ("legal_risk.py", "scene_ethics.py", "apodictic_artifacts.py",
                     "fiction_groundtruth.py", "honesty_check.py", "severity_vocab.py"):
            (self.root / name).write_text("raise RuntimeError('cwd injection')\n")
        (self.root / "sitecustomize.py").write_text("raise RuntimeError('site injection')\n")
        c = self.client(cwd=self.root, env=dict(os.environ, PATH="", PYTHONPATH=str(self.root)))
        source = self.root / "invented.txt"
        n = 0
        for leaf in LEAVES:
            texts = [p.read_bytes().decode() for p in sorted(FIXTURES.glob("%s.*.%s.*.md" % ("tl" if leaf.startswith("timeline-") else "lc", leaf)))]
            for text in texts + SHARED + CASES[leaf]:
                with self.subTest(leaf=leaf, case=n):
                    source.write_bytes(text.encode())
                    oracle = subprocess.run([sys.executable, str(ROOT / "plugins/apodictic/scripts/validate.py"), leaf,
                                             str(source)], capture_output=True)
                    c.send(validation(str(n), text, leaf))
                    got = c.next()
                    self.assertEqual((got["id"], got["validator"], got["available"], got["error"]),
                                     (str(n), leaf, True, None))
                    result = got["result"]
                    self.assertEqual((result["exit_code"], result["stdout"].encode(), result["stderr"].encode()),
                                     (oracle.returncode, oracle.stdout, oracle.stderr))
                    if leaf in ("deficit-lock", "fiction-groundtruth-check"):
                        expected = dict(DEFICIT_CASES if leaf == "deficit-lock" else FICTION_CASES)
                        if text in expected:
                            self.assertEqual(result["exit_code"], expected[text])
                    if leaf in SCHEMA_CASES:
                        expected = dict(SCHEMA_CASES[leaf])
                        if text in expected:
                            self.assertEqual(result["exit_code"], expected[text])
                    if leaf == "calibration-honesty":
                        self.assertEqual(result["exit_code"], 0)
                        expected = dict(CALIBRATION_CASES)
                        if text in expected:
                            self.assertEqual(sum(line.startswith("  WARN:") for line in
                                                 result["stdout"].splitlines()), expected[text])
                    if leaf in TIMELINE_CASES:
                        expected = dict(TIMELINE_CASES[leaf])
                        if text in expected:
                            self.assertEqual(result["exit_code"], expected[text])
                        if result["stdout"].startswith("WARN:"):
                            self.assertFalse(result["stdout"].endswith("\n\n"))
                    if leaf == "audit-signal-propagation":
                        expected = {t: decision for _, t, decision in SIGNAL_CASES}
                        if text in expected:
                            self.assertEqual(result["exit_code"], expected[text])
                    if leaf == "underdiagnosis-triggers":
                        expected = {t: (decision, triggers) for _, t, decision, triggers in UNDERDIAGNOSIS_CASES}
                        if text in expected:
                            decision, triggers = expected[text]
                            self.assertEqual(result["exit_code"], decision)
                            self.assertEqual([line.partition(" — ")[0] for line in result["stdout"].splitlines()
                                              if line.startswith(("WARN: Trigger #", "ERROR: Trigger #"))], triggers)
                            if text == CONVERGENCE + "\nseries representation\n" + CONVERGENCE_MARKER:
                                self.assertIn("\n\nFAILED: 1 underdiagnosis trigger(s) fired. "
                                              "Triggers: convergence multi-axis \n", result["stdout"])
                n += 1
        self.assertEqual(c.end(), (0, [], b""))

    def test_underdiagnosis_reference_context_matches_copied_native_cli(self):
        # The wrapper always calls the real propagation child, even for empty text.
        # Await each response before changing the same copy's installed reference.
        original = self.reference.read_text(encoding="utf-8")
        changed = ("#### Default mapping\n"
                   "- Audit-internal Must-Fix floor -> Synthesis Must-Fix\n"
                   "- Audit-internal hard gate -> Synthesis Should-Fix\n"
                   "- Audit-internal HIGH / Alert -> Synthesis Must-Fix or Should-Fix\n")
        contexts = [
            ("packaged-original", original, UNDERDIAGNOSIS_BODY + SIGNAL_APPENDIX, 1,
             ["ERROR: Trigger #6 (propagation)"]),
            ("default-changed", changed, UNDERDIAGNOSIS_BODY + SIGNAL_APPENDIX, 0, []),
            ("missing-fallback", None, UNDERDIAGNOSIS_BODY + SIGNAL_APPENDIX, 1,
             ["ERROR: Trigger #6 (propagation)"]),
            ("malformed-empty", "# No mapping\n", "", 1, ["ERROR: Trigger #6 (propagation)"]),
            ("malformed-parent-override", "# No mapping\n", PROPAGATION_PARENT_MARKER, 0,
             ["WARN: Trigger #6 (propagation)"]),
            ("restored-matched-evidence", original, "Must-Fix: revise L42.\n" + SIGNAL_APPENDIX, 0, []),
        ]
        c = self.client(script=self.script, cwd=self.root)
        source = self.root / "invented-underdiagnosis.txt"
        for label, reference, text, decision, triggers in contexts:
            with self.subTest(context=label):
                if reference is None:
                    self.reference.unlink()
                else:
                    self.reference.write_text(reference, encoding="utf-8")
                source.write_bytes(text.encode())
                oracle = subprocess.run([PYTHON, "-I", "-S", "-B", str(self.scripts / "validate.py"),
                                         "underdiagnosis-triggers", str(source)],
                                        capture_output=True, cwd=self.root, timeout=8)
                c.send(validation(label, text, "underdiagnosis-triggers"))
                got = c.next()
                self.assertEqual((got["id"], got["validator"], got["available"], got["error"]),
                                 (label, "underdiagnosis-triggers", True, None))
                result = got["result"]
                self.assertEqual((result["exit_code"], result["stdout"].encode(), result["stderr"].encode()),
                                 (oracle.returncode, oracle.stdout, oracle.stderr))
                self.assertEqual(result["exit_code"], decision)
                self.assertEqual([line.partition(" — ")[0] for line in result["stdout"].splitlines()
                                  if line.startswith(("WARN: Trigger #", "ERROR: Trigger #"))], triggers)
                self.assertNotIn("mapping is malformed", result["stdout"])
        self.assertEqual(c.end(), (0, [], b""))

    def test_signal_reference_context_matches_copied_native_cli(self):
        # Exercise the real helper's fixed installed-file lookup, with both consumers
        # in this same copy. Inline dep_text and synthetic helpers cannot prove this.
        original = self.reference.read_text(encoding="utf-8")
        default = ("#### Default mapping\n"
                   "- Audit-internal Must-Fix floor -> Synthesis Must-Fix\n"
                   "- Audit-internal hard gate -> Synthesis Must-Fix\n"
                   "- Audit-internal HIGH / Alert -> Synthesis Must-Fix or Should-Fix\n")
        override = default + ("| Reception Risk | hard gate | Should-Fix | context | source | "
                              "propagate-override: hard-gate -> Should-Fix |\n")
        contexts = [
            ("packaged-original", original, SIGNAL_SHOULD, 1, False),
            ("default-changed", default.replace("hard gate -> Synthesis Must-Fix",
                                               "hard gate -> Synthesis Should-Fix"),
             SIGNAL_SHOULD, 0, False),
            # Removing the changed map returns built-in policy, rather than refusal.
            ("missing-fallback", None, SIGNAL_SHOULD, 1, False),
            ("per-audit-changed", override, SIGNAL_SHOULD, 0, False),
            ("per-audit-unrelated", override, SIGNAL_SHOULD.replace("Reception Risk", "Compression"), 1, False),
            ("missing-default-block", "# No mapping\n", "", 1, True),
            ("missing-required-class", default.replace(
                "- Audit-internal hard gate -> Synthesis Must-Fix\n", ""), "", 1, True),
            ("malformed-default", default.replace("hard gate -> Synthesis Must-Fix",
                                                  "hard gate -> Synthesis unknown"), "", 1, True),
            ("malformed-override-tier", override.replace("hard-gate -> Should-Fix",
                                                         "hard-gate -> unknown"), "", 1, True),
            ("malformed-override-class", override.replace("hard-gate -> Should-Fix",
                                                          "invented -> Should-Fix"), "", 1, True),
            ("restored-original", original, SIGNAL_SHOULD.replace("Should-Fix", "Must-Fix"), 0, False),
        ]
        c = self.client(script=self.script, cwd=self.root)
        source = self.root / "invented-signal.txt"
        for label, reference, text, decision, malformed in contexts:
            with self.subTest(context=label):
                if reference is None:
                    self.reference.unlink()
                else:
                    self.reference.write_text(reference, encoding="utf-8")
                source.write_bytes(text.encode())
                oracle = subprocess.run([PYTHON, "-I", "-S", "-B", str(self.scripts / "validate.py"),
                                         "audit-signal-propagation", str(source)],
                                        capture_output=True, cwd=self.root, timeout=8)
                c.send(validation(label, text, "audit-signal-propagation"))
                got = c.next()
                self.assertEqual((got["id"], got["validator"], got["available"], got["error"]),
                                 (label, "audit-signal-propagation", True, None))
                result = got["result"]
                self.assertEqual((result["exit_code"], result["stdout"].encode(), result["stderr"].encode()),
                                 (oracle.returncode, oracle.stdout, oracle.stderr))
                self.assertEqual(result["exit_code"], decision)
                self.assertEqual("mapping is malformed" in result["stdout"], malformed)
        self.assertEqual(c.end(), (0, [], b""))

    def test_output_limit_exact_and_over(self):
        c = self.client()
        # A natural ledger result far over the response ceiling, then recovery.
        c.send(validation("u" * 64, "\n".join(["## Pass 9999999999"] * 8191), "ledger-check"))
        got = c.next()
        self.error(got, "output_limit")
        self.assertNotIn("9999999999", json.dumps(got))
        c.send(validation("healthy")); self.assertTrue(c.next()["available"])
        self.assertEqual(c.end(), (0, [], b""))
        # The full encoded envelope, including escaped LF and the delimiter, is bounded.
        prototype = {"protocol": 1, "type": "result", "id": "r1", "validator": "tone-check",
                     "available": True, "result": {"exit_code": 0, "stdout": "\n", "stderr": ""},
                     "error": None}
        for over in (0, 1):
            self.helper("def check(text): return [], [], 'x' * %d, ''\n"
                        % (32768 - len(frame(prototype)) + over))
            c = self.client(script=self.script); c.send(validation()); got = c.next()
            if over: self.error(got, "output_limit")
            else: self.assertEqual(len(frame(got)), 32768)
            self.assertEqual(c.end(), (0, [], b""))

    @unittest.skipUnless(os.name == "posix", "POSIX development-host death/reaping evidence")
    def test_lifecycle_is_shared_by_every_leaf(self):
        actions = ("cancel", "timeout", "eof", "fatal", "partial", "bad_target", "SIGTERM", "SIGINT")
        for i, action in enumerate(actions):
            leaf, queued = LEAVES[i % len(LEAVES)], LEAVES[(i + 1) % len(LEAVES)]
            with self.subTest(action=action, leaf=leaf):
                self.sleeping()
                c = self.client(script=self.script)
                started = time.monotonic()
                c.send(validation("active", "sleep", leaf)); pid = self.pid()
                # One active worker; later valid requests wait in order, refusals answer at once.
                c.send(validation("queued", "", queued))
                c.send(validation("dropped", "", leaf))
                c.send(validation("other", "", "other")); self.error(c.next(), "validator_unavailable")
                c.send(validation("limit", "\n" * 8192, leaf)); self.error(c.next(), "input_limit")
                c.send(cancel("dropped", "c0")); got = c.next(); self.error(got, "cancelled")
                self.assertEqual((got["id"], got["validator"]), ("dropped", leaf))
                self.assertTrue(c.next()["cancelled"])
                os.kill(pid, 0)
                if action == "cancel": c.send(cancel("active"))
                elif action == "eof": c.child.stdin.close()
                elif action == "fatal": c.raw(b"{}\n")
                elif action == "partial": c.raw(b"{}"); c.child.stdin.close()
                elif action == "bad_target": c.send(cancel("x" * 65))
                elif action.startswith("SIG"): c.child.send_signal(getattr(signal, action))
                drains = action in ("cancel", "timeout", "eof")
                got = c.next()
                self.error(got, "cancelled" if action == "cancel" else "timeout" if drains else "session_ended")
                self.assertEqual((got["id"], got["validator"]), ("active", leaf))
                self.dead(pid)
                if action in ("timeout", "eof"):
                    self.assertTrue(5 <= time.monotonic() - started < 7)
                if action == "cancel": self.assertTrue(c.next()["cancelled"])
                got = c.next()
                self.assertEqual((got["id"], got["validator"]), ("queued", queued))
                if drains: self.assertEqual(got["result"]["stdout"], "synthetic OK\n")
                else: self.error(got, "session_ended")
                if action in ("fatal", "partial", "bad_target"):
                    self.assertEqual(c.next()["error"]["code"],
                                     "invalid_frame" if action == "partial" else "invalid_request")
                if action in ("cancel", "timeout"):
                    c.send(cancel("active", "late")); self.assertFalse(c.next()["cancelled"])
                    c.send(validation("healthy", "", leaf)); self.assertTrue(c.next()["available"])
                self.assertEqual(c.end(), (0 if drains else 2, [], b""))

    def test_dependency_and_worker_failures_are_unavailable(self):
        cases = (("raise ImportError('synthetic')\n", "runner_dependency_unavailable"),
                 ("def check(text): raise RuntimeError(text)\n", "worker_failed"),
                 ("import os\ndef check(text): os._exit(3)\n", "worker_failed"),
                 ("def check(text): return []\n", "worker_failed"),
                 ("def check(text): print(text); return [],[],'OK','FAIL'\n", "worker_failed"),
                 ("import sys\ndef check(text): sys.stderr.write(text); return [],[],'OK','FAIL'\n",
                  "worker_failed"),
                 ("import json,os\ndef check(text):\n os.write(1, (json.dumps({'exit_code': 0, "
                  "'stdout': 'OK', 'stderr': '', 'id': 'forged'}) + '\\n').encode())\n"
                  " return [],[],'OK','FAIL'\n", "worker_failed"),
                 (None, "runner_dependency_unavailable"), ("transitive", "runner_dependency_unavailable"))
        for body, code in cases:
            with self.subTest(body=body):
                if body is None:
                    (self.scripts / "letter_checks.py").unlink()
                elif body == "transitive":
                    shutil.copyfile(SCRIPT.parent / "letter_checks.py", self.scripts / "letter_checks.py")
                    (self.scripts / "override_marker.py").unlink()
                else:
                    self.helper(body)
                before = sorted(self.root.rglob("*"))
                c = self.client(script=self.script)
                c.send(validation("bad", "SYNTHETIC_SENTINEL", "ledger-check"))
                got = c.next(); self.error(got, code)
                self.assertEqual((got["id"], got["validator"]), ("bad", "ledger-check"))
                self.assertNotIn("SYNTHETIC_SENTINEL", json.dumps(got))
                self.assertEqual(c.end(), (0, [], b""))
                self.assertEqual(before, sorted(self.root.rglob("*")))

    def test_timeline_dependency_refusals_and_two_input_leaf_unavailable(self):
        module = self.scripts / "timeline_checks.py"
        for body in (None, "SINGLE_FILE_CHECKS = {}\n"):
            if body is None:
                module.unlink()
            else:
                module.write_text(body)
            c = self.client(script=self.script)
            for i, leaf in enumerate(("timeline-arithmetic", "timeline-anchor-conflict")):
                c.send(validation(str(i), "SYNTHETIC_SENTINEL", leaf))
                got = c.next()
                self.error(got, "runner_dependency_unavailable")
                self.assertNotIn("SYNTHETIC_SENTINEL", json.dumps(got))
            c.send(validation("diff", "", "timeline-diff"))
            self.error(c.next(), "validator_unavailable")
            self.assertEqual(c.end(), (0, [], b""))

    def test_calibration_refusals_and_output_ceiling(self):
        c = self.client()
        c.send(validation("large", (CALIBRATION_CLAIMS[0] + "\n\n") * 200,
                          "calibration-honesty"))
        self.error(c.next(), "output_limit")
        c.send(dict(validation("strict", CALIBRATION_CLAIMS[0], "calibration-honesty"), strict=True))
        self.assertEqual(c.next()["error"]["code"], "invalid_request")
        self.assertEqual(c.end(), (2, [], b""))
        module = self.scripts / "calibration_honesty.py"
        for body in (None, "# scan is missing\n"):
            if body is None:
                module.unlink()
            else:
                module.write_text(body)
            c = self.client(script=self.script)
            c.send(validation("bad", "SYNTHETIC_SENTINEL", "calibration-honesty"))
            got = c.next()
            self.error(got, "runner_dependency_unavailable")
            self.assertNotIn("SYNTHETIC_SENTINEL", json.dumps(got))
            self.assertEqual(c.end(), (0, [], b""))

    def test_schema_dependencies_are_required_even_for_empty_text(self):
        for leaf, schema_id in (("legal-risk", "apodictic.legal_risk.v1"),
                                ("scene-ethics", "apodictic.scene_ethics.v1"),
                                ("deficit-lock", "apodictic.finding.v1")):
            path = self.schemas / (schema_id + ".schema.json")
            original = path.read_bytes()
            schema = json.loads(original)
            faults = [None, b"{broken", b"[]", b"null", b"\xff", json.dumps(dict(schema, **{"$id": "wrong"})).encode()]
            faults += [json.dumps(dict(schema, **{key: value})).encode() for key, value in
                       (("type", "array"), ("required", "id"), ("required", [3]),
                        ("properties", []), ("properties", {"id": "string"}))]
            for fault in faults:
                with self.subTest(leaf=leaf, fault=fault):
                    if fault is None:
                        path.unlink()
                    else:
                        path.write_bytes(fault)
                    c = self.client(script=self.script)
                    c.send(validation("missing", "", leaf))
                    self.error(c.next(), "runner_dependency_unavailable")
                    self.assertEqual(c.end(), (0, [], b""))
                    path.write_bytes(original)
        artifact = self.scripts / "apodictic_artifacts.py"
        artifact.unlink()
        c = self.client(script=self.script)
        for leaf in ("legal-risk", "scene-ethics", "deficit-lock"):
            c.send(validation(leaf, "", leaf))
            self.error(c.next(), "runner_dependency_unavailable")
        self.assertEqual(c.end(), (0, [], b""))

    def test_schema_leaf_helpers_must_be_present(self):
        for leaf, module in (("legal-risk", "legal_risk.py"), ("scene-ethics", "scene_ethics.py"),
                             ("deficit-lock", "honesty_check.py"),
                             ("fiction-groundtruth-check", "fiction_groundtruth.py")):
            path = self.scripts / module
            original = path.read_bytes()
            for body in (None, b"# entrypoint missing\n"):
                if body is None:
                    path.unlink()
                else:
                    path.write_bytes(body)
                c = self.client(script=self.script)
                c.send(validation("helper", "", leaf))
                self.error(c.next(), "runner_dependency_unavailable")
                self.assertEqual(c.end(), (0, [], b""))
                path.write_bytes(original)

    def test_installed_schema_is_authoritative_and_environment_override_is_ignored(self):
        source = self.root / "invented.md"
        alternate = self.root / "alternate"
        alternate.mkdir()
        for leaf, schema_id, kind, obj in (
            ("legal-risk", "apodictic.legal_risk.v1", "legal_risk", LEGAL_ITEM),
            ("scene-ethics", "apodictic.scene_ethics.v1", "scene_ethics", ETHICS_ITEM),
            ("deficit-lock", "apodictic.finding.v1", "finding", FINDING_ITEM),
        ):
            path = self.schemas / (schema_id + ".schema.json")
            schema = json.loads(path.read_text())
            (alternate / path.name).write_text(json.dumps(schema))
            schema["required"].append("synthetic_required")
            schema["properties"]["synthetic_required"] = {"type": "string"}
            path.write_text(json.dumps(schema))
            text = (DEFICIT_PROSE if leaf == "deficit-lock" else "Not legal advice.\n") + artifact_block(kind, obj)
            source.write_text(text)
            oracle = subprocess.run([PYTHON, "-I", "-S", str(self.scripts / "validate.py"),
                                     leaf, str(source)], capture_output=True)
            c = self.client(script=self.script, env=dict(os.environ, APODICTIC_SCHEMA_DIR=str(alternate)))
            c.send(validation("schema", text, leaf))
            result = c.next()["result"]
            self.assertEqual((result["exit_code"], result["stdout"].encode(), result["stderr"].encode()),
                             (oracle.returncode, oracle.stdout, oracle.stderr))
            self.assertEqual(result["exit_code"], 1)
            if leaf != "deficit-lock":
                self.assertIn("synthetic_required", result["stdout"])
            self.assertEqual(c.end(), (0, [], b""))

    def test_groundtruth_dependency_and_deficit_exception_boundaries(self):
        (self.scripts / "severity_vocab.py").unlink()
        c = self.client(script=self.script)
        c.send(validation("missing", "", "fiction-groundtruth-check"))
        self.error(c.next(), "runner_dependency_unavailable")
        self.assertEqual(c.end(), (0, [], b""))
        c = self.client()
        for i, severity in enumerate(([], {})):
            text = artifact_block("finding", dict(FINDING_ITEM, severity=severity,
                                                  mechanism="SYNTHETIC_SENTINEL"))
            c.send(validation(str(i), text, "deficit-lock"))
            got = c.next()
            self.error(got, "worker_failed")
            self.assertNotIn("SYNTHETIC_SENTINEL", json.dumps(got))
        c.send(validation("healthy", DEFICIT_PROSE + artifact_block("finding", FINDING_ITEM), "deficit-lock"))
        self.assertEqual(c.next()["result"]["exit_code"], 0)
        c.send(validation("two-input", "", "softness-check"))
        self.error(c.next(), "validator_unavailable")
        self.assertEqual(c.end(), (0, [], b""))

    def test_closed_schemas_and_ids(self):
        cases = []
        for request in (validation(), cancel()):
            for key in request:
                absent = dict(request); del absent[key]; cases.append(absent)
                cases.append(dict(request, **{key: []}))
            cases.append(dict(request, path="/synthetic/path"))
        cases += [dict(validation(), protocol=v) for v in (True, 1.0)]
        cases += [cancel(target) for target in ("", "a" * 65, "../path", 3, None)]
        cases += [[], 5, None, dict(validation(), id="x "), dict(validation(), validator="x/evil")]
        for request in cases:
            with self.subTest(request=request):
                c = self.client(); c.send(request)
                self.assertEqual(c.next()["error"]["code"], "invalid_request")
                self.assertEqual(c.end(), (2, [], b""))
        c = self.client(); c.send(dict(validation(), protocol=2))
        self.assertEqual(c.next()["error"]["code"], "unsupported_protocol")
        self.assertEqual(c.end()[0], 2)
        c = self.client(); c.send(cancel("x" * 64)); self.assertFalse(c.next()["cancelled"])
        c.send(cancel("unknown", "c2")); self.assertFalse(c.next()["cancelled"])
        c.send(cancel("unknown", "c2")); self.assertEqual(c.next()["error"]["code"], "duplicate_id")
        self.assertEqual(c.end(), (2, [], b""))
        for argv in (["extra"], ["--worker"], ["--worker", "other"], ["--worker", "tone-check", "x"]):
            run = subprocess.run([PYTHON, "-I", "-S", str(SCRIPT), *argv], capture_output=True)
            self.assertEqual((run.returncode, run.stdout), (2, b""))

    def test_framing_is_not_forgiving(self):
        valid = frame(validation())
        for data in (b"\n", b" \n", b"\xef\xbb\xbf" + valid, valid[:-1] + b"\r\n", valid[:-1],
                     b"\xff\n", b'{"text":"\\ud800"}\n', b'{"text":"\xed\xa0\x80"}\n',
                     b'{"value":NaN}\n', b'{"value":Infinity}\n', b'{} garbage\n',
                     b'[' * 100000 + b']' * 100000 + b'\n'):
            with self.subTest(data=data[:40]):
                c = self.client(); c.raw(data)
                if not data.endswith(b"\n"):
                    c.child.stdin.close()
                result = c.next()
                self.assertEqual((result["error"]["code"], result["id"]), ("invalid_frame", None))
                self.assertEqual(c.end(), (2, [], b""))
        for extra in (0, 1):
            c = self.client()
            base = frame(cancel())[:-1]
            c.raw(base + b" " * (1048576 - len(base) + extra) + b"\n")
            self.assertEqual(c.next()["type"], "protocol_error" if extra else "cancel_result")
            self.assertEqual(c.end()[0], 2 if extra else 0)

    def test_admission_order_text_limits_and_long_session(self):
        c = self.client()
        c.send(validation("other", "x" * 262145, "other")); self.error(c.next(), "validator_unavailable")
        for i, text in enumerate(("x" * 262144, "😀" * 65536, "\n" * 8191, "\r\n" * 8191)):
            c.send(validation("at" + str(i), text)); self.assertTrue(c.next()["available"])
        for i, text in enumerate(("x" * 262145, "😀" * 65536 + "x", "\n" * 8192, "\r" * 8192)):
            c.send(validation("over" + str(i), text)); self.error(c.next(), "input_limit")
        # A well-behaved client is not cut off after any number of requests.
        for i in range(70):
            c.send(validation(str(i), "", LEAVES[i % len(LEAVES)])); got = c.next()
            self.assertEqual((got["id"], got["available"]), (str(i), True))
        self.assertEqual(c.end(), (0, [], b""))

    def test_piped_batch_drains_at_eof(self):
        requests = [validation("a"), validation("b", "## Pass 2\n", "ledger-check"),
                    validation("c", "masterpiece")]
        run = subprocess.run([PYTHON, "-I", "-S", str(SCRIPT)], capture_output=True, timeout=30,
                             input=b"".join(frame(r) for r in requests))
        self.assertEqual((run.returncode, run.stderr), (0, b""))
        got = [json.loads(line) for line in run.stdout.splitlines()]
        self.assertEqual([(g["id"], g["validator"], g["available"], g["result"]["exit_code"]) for g in got],
                         [("a", "tone-check", True, 0), ("b", "ledger-check", True, 1),
                          ("c", "tone-check", True, 1)])

    def test_fixed_locale_time_and_no_network_imports(self):
        self.helper("import os\ndef check(text): return [], [], "
                    "'%s %s' % (os.environ['TZ'], os.environ['LC_ALL']), ''\n")
        c = self.client(script=self.script, env=dict(os.environ, TZ="America/New_York", LC_ALL="en_US.UTF-8"))
        c.send(validation()); self.assertEqual(c.next()["result"]["stdout"], "UTC C\n")
        self.assertEqual(c.end(), (0, [], b""))
        # Leaves are trusted local text code: no network-capable module is imported.
        network = {"socket", "ssl", "http", "urllib", "ftplib", "smtplib", "asyncio", "requests"}
        for name in ("validator_runner.py", "letter_checks.py", "timeline_checks.py", "calibration_honesty.py", "legal_risk.py", "scene_ethics.py",
                     "apodictic_artifacts.py", "fiction_groundtruth.py", "honesty_check.py",
                     "severity_vocab.py", "override_marker.py"):
            tree = ast.parse((SCRIPT.parent / name).read_text())
            imported = {alias.name.split(".")[0] for node in ast.walk(tree)
                        if isinstance(node, ast.Import) for alias in node.names}
            imported |= {node.module.split(".")[0] for node in ast.walk(tree)
                         if isinstance(node, ast.ImportFrom) and node.module}
            self.assertFalse(imported & network, name)

    def test_inventory_gate_requires_one_disposition_per_registry_id(self):
        self.assertEqual(self.inventory_check(), 0)
        registry = self.scripts / "validate.py"; original = registry.read_text(encoding="utf-8")
        baseline = json.loads(self.metadata.read_text())
        # Registry drift: an undispositioned addition, removal, rename or duplicate fails.
        declaration = next(n for n in ast.parse(original).body if isinstance(n, ast.Assign)
                           and any(isinstance(t, ast.Name) and t.id == "AGG_VALIDATORS" for t in n.targets))
        ids = ast.literal_eval(declaration.value)
        lines = original.splitlines(keepends=True)
        def replaced(expression):
            return ("".join(lines[:declaration.lineno - 1]) + "AGG_VALIDATORS = " + expression + "\n"
                    + "".join(lines[declaration.end_lineno:]))
        for changed in (replaced(repr(("invented-new", *ids))),
                        replaced(repr(tuple(v for v in ids if v != "tone-check"))),
                        replaced(repr(tuple("invented-tone" if v == "tone-check" else v for v in ids))),
                        replaced(repr((*ids, "tone-check")))):
            registry.write_text(changed, encoding="utf-8")
            self.assertNotEqual(changed, original)
            self.assertEqual(self.inventory_check(), 1)
        # Metadata drift: closed row/file shape, exact set, known dispositions, nonempty reasons.
        registry.write_text(original, encoding="utf-8")
        for change in ("omit", "add", "duplicate", "class", "reason", "extra-row-key", "extra",
                       "leaf-not-registered"):
            value = copy.deepcopy(baseline)
            rows = value["validators"]
            if change == "omit": rows.pop()
            elif change == "add": rows.append(dict(rows[0], id="invented"))
            elif change == "duplicate": rows.append(rows[0])
            elif change == "class": rows[0]["desktop_disposition"] = "desktop-supported"
            elif change == "reason": rows[0]["omitted_capability"] = " "
            elif change == "extra-row-key": rows[0]["development_support"] = "none"
            elif change == "extra": value["extra"] = True
            else:
                next(r for r in rows if r["id"] == "tone-check")["id"] = "invented-tone"
                registry.write_text(original.replace("tone-check", "invented-tone", 1))
            self.metadata.write_text(json.dumps(value))
            self.assertEqual(self.inventory_check(), 1, change)
        registry.write_text(original, encoding="utf-8")
        self.metadata.write_text(json.dumps(baseline))
        self.assertEqual(self.inventory_check(), 0)

    def test_inventory_missing_dispatcher_fails_closed(self):
        path = self.scripts / "validate.py"
        moved = path.with_suffix(".held")
        path.rename(moved)
        try:
            self.assertEqual(self.inventory_check(), 1)
        finally:
            moved.rename(path)


if __name__ == "__main__":
    unittest.main()
