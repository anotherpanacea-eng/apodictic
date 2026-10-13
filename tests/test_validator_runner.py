"""Behavioral contract tests using only invented text/public validator fixtures."""
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
PYTHON = sys.executable


def validation(id="r1", text="The pacing needs work.", validator="tone-check"):
    return {"protocol": 1, "type": "validate", "id": id, "validator": validator, "text": text}


def cancel(target="r1", id="c1"):
    return {"protocol": 1, "type": "cancel", "id": id, "target": target}


def frame(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode() + b"\n"


class Client:
    def __init__(self, script=SCRIPT, env=None, cwd=None, launcher=None):
        self.child = subprocess.Popen([PYTHON, "-I", "-S", str(launcher or script)],
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
        for name in ("validator_runner.py", "letter_checks.py", "override_marker.py", "validate.sh"):
            shutil.copyfile(SCRIPT.parent / name, self.scripts / name)
        self.metadata = self.schemas / "validator-runtime-inventory.json"
        shutil.copyfile(SCRIPT.parent.parent / "schemas/validator-runtime-inventory.json", self.metadata)
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

    def sleeping(self):
        self.pidfile = self.root / "synthetic-worker.pid"
        (self.scripts / "letter_checks.py").write_text(
            "import os,time,signal\n"
            "def tone_check(text):\n"
            " if text == 'sleep':\n"
            "  open(%r,'w').write(str(os.getpid()))\n"
            "  signal.signal(signal.SIGTERM,signal.SIG_IGN)\n"
            "  time.sleep(30)\n"
            " return [],[], 'synthetic OK', 'synthetic FAILED'\n"
            "synthesis_sections = severity_floor = decision_layer_check = tone_check\n" % str(self.pidfile))

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

    def test_usage_and_foreign_empty_path_session(self):
        bad = subprocess.run([PYTHON, str(SCRIPT)], input=b"", capture_output=True)
        self.assertEqual(bad.returncode, 2)
        self.assertEqual(bad.stdout, b"")
        env = dict(os.environ, PATH="", PYTHONPATH=str(self.root), OPENAI_API_KEY="synthetic-not-a-key", HTTPS_PROXY="http://invalid.example")
        (self.root / "letter_checks.py").write_text("raise RuntimeError('cwd injection')\n")
        (self.root / "sitecustomize.py").write_text("raise RuntimeError('site injection')\n")
        c = self.client(env=env, cwd=self.root)
        for i, text in enumerate(("", "Needs revision.", "masterpiece")):
            c.send(validation(str(i), text))
            result = c.next()
            self.assertTrue(result["available"])
            self.assertEqual(result["result"]["exit_code"], int(text == "masterpiece"))
        self.assertEqual(c.end(), (0, [], b""))

    def test_exact_legacy_oracle_parity(self):
        c = self.client()
        fixtures = list((ROOT / "tests/fixtures/validators").glob("lc.*.tone-check.*.md"))
        self.assertEqual(len(fixtures), 3)
        texts = [p.read_bytes().decode() for p in fixtures]
        texts += ["# Development Edit\nThe pacing needs work; the voice is distinctive.\n",
                  "# Development Edit\nThis is a flawless masterpiece.\n",
                  "# Development Edit\n## What Needs Work\nPacing needs work.\n## Appendix A\nThe jacket copy calls it a masterpiece.\n",
                  "# Development Edit\n## What Needs Work\nAvoid words like `masterpiece` in the letter.\n",
                  "# Development Edit\n## What Needs Work\nBlocked list:\n```\nmasterpiece\nflawless\n```\nProse stays clean.\n",
                  "# Development Edit\n## What Needs Work\nPacing needs work.\n> The author's blurb calls it a triumph.\n"]
        texts += ["", "The pacing needs work.", "masterpiece", "STUNNING", "`flawless`",
                  "> triumph", "# Appendix A\nperfection", "masterpiece stunning flawless clean bill tour de force triumph perfection " * 2,
                  "MASTERPIECE Stunning FLAWLESS Clean Bill TOUR DE FORCE Triumph PERFECTION",
                  "雪 😀\r\nflawless\r> triumph\n", "````\n```\nflawless\n````\ntriumph",
                  "~~~\r\nmasterpiece\r\n~~~\r\nSTUNNING", "# Appendixes A\nperfection",
                  "An Appendix A mentioned mid-line\nmasterpiece", " > clean bill\rflawless"]
        for i, text in enumerate(texts):
            with self.subTest(case=i):
                source = self.root / "invented-tone.txt"
                source.write_bytes(text.encode())
                oracle = subprocess.run(["bash", str(ROOT / "scripts/validate.sh"), "tone-check", str(source)], capture_output=True)
                c.send(validation(str(i), text))
                got = c.next()["result"]
                self.assertEqual((got["exit_code"], got["stdout"].encode(), got["stderr"].encode()),
                                 (oracle.returncode, oracle.stdout, oracle.stderr))
        self.assertEqual(c.end(), (0, [], b""))

    def test_synthesis_exact_legacy_oracle_parity(self):
        names = ("Development Edit", "The Short Version", "What the Book Does Best",
                 "What Needs Work", "Additional Observations", "Revision Checklist",
                 "Protected Elements", "Author Decisions", "Control Questions",
                 "The Strongest Case Against", "Stress Test", "Appendix A", "Appendix B", "Appendix C")
        full = "".join("## %s\n\nbody\n\n" % h for h in names)
        fixtures = list((ROOT / "tests/fixtures/validators").glob("lc.*.synthesis-sections.*.md"))
        self.assertEqual(len(fixtures), 3)
        texts = [p.read_bytes().decode() for p in fixtures]
        # The helper's five shipped synthetic cases, followed by hostile boundaries.
        texts += [full, full.replace("## Stress Test\n\nbody\n\n", ""),
                  full.replace("## Development Edit\n", "# Development Edit — Worked Example\n")
                      .replace("## Stress Test\n", "## **Stress Test**\n")
                      .replace("## Appendix A\n", "## Appendix A — Diagnostic Detail\n"),
                  full.replace("## Stress Test\n", "## Notes on the Stress Test approach\n"),
                  full.replace("## Appendix A\n", "## Appendix Alpha\n"),
                  "", full.upper(), full.lower(), "雪 😀\n" + full,
                  "\n".join(names), full.replace("## ", "##\t"),
                  full.replace("## Stress Test\n", "## \nStress Test\n"),
                  full.replace("## Stress Test\n", " ## Stress Test\n"),
                  full.replace("\n", "\r\n"), full.replace("\n", "\r")]
        texts += [full.replace("## Appendix A\n", "## Appendix A" + suffix + "\n")
                  for suffix in ("_", "2", "é", "雪", "\u0301", "!", " — Detail", "lpha")]
        texts += [full.replace("## ", "#" * level + " ") for level in (1, 3, 4, 5)]
        texts += ["## Appendix Alpha\n" * 8191,
                  ("## Appendix Alpha" + "x" * 14 + "\n") * 8191 + "x" * 32,
                  "x" * 262144, "\n" * 8191]
        c = self.client()
        for i, text in enumerate(texts):
            with self.subTest(case=i):
                source = self.root / "invented-synthesis.txt"
                source.write_bytes(text.encode())
                oracle = subprocess.run(["bash", str(ROOT / "scripts/validate.sh"),
                                         "synthesis-sections", str(source)], capture_output=True)
                c.send(validation(str(i), text, "synthesis-sections"))
                value = c.next()
                self.assertEqual((value["id"], value["validator"], value["available"]),
                                 (str(i), "synthesis-sections", True))
                got = value["result"]
                self.assertEqual((got["exit_code"], got["stdout"].encode(), got["stderr"].encode()),
                                 (oracle.returncode, oracle.stdout, oracle.stderr))
                if text == "":
                    self.assertEqual((got["exit_code"], len(got["stdout"].encode())), (1, 898))
                elif text == full:
                    self.assertEqual((got["exit_code"], len(got["stdout"].encode())), (0, 66))
        for i, text in enumerate(("x" * 262145, "\n" * 8192, "\r\n" * 8192)):
            c.send(validation("over" + str(i), text, "synthesis-sections"))
            self.error(c.next(), "input_limit")
        self.assertEqual(c.end(), (0, [], b""))

    def test_severity_exact_legacy_oracle_parity(self):
        fixtures = list((ROOT / "tests/fixtures/validators").glob("lc.*.severity-floor.*.md"))
        self.assertEqual(len(fixtures), 7)
        weak = "Weak at High"
        systemic = "Systemic Must-Fix Strong Fit"
        band = "Strong Fit Should-Fix Should-Fix Should-Fix"
        marker = "<!-- override:severity-floor-weak-axis -->"
        texts = [p.read_bytes().decode() for p in fixtures]
        texts += ["", weak, "Weak at Medium", "Weak at Low", systemic, band,
                  band + " justification", weak + "\n" + marker,
                  weak + "\n## Appendix A\n" + marker,
                  weak + "\n`" + marker + "`",
                  weak + "\n```\n" + marker + "\n```",
                  weak + "\n~~~\n" + marker + "\n```",
                  weak + "\n" + marker.replace("override:", "Override:"),
                  weak + "\n" + marker.replace(" -->", "_extra -->"),
                  weak + "\n" + marker.replace(" -->", "suffix -->"),
                  weak + "\n" + marker.replace("override:", "overridе:"),
                  weak + "\n" + marker.replace(" -->", " — reason -->"),
                  weak + "\n" + marker.replace(" -->", "\u2003reason -->"),
                  weak + "\n<!-- override:severity-floor-weak-axis",
                  "Systemic Must-Fix Strong Fit " + band,
                  band + " `justification`", "Must-Fix " + weak,
                  "# Appendix A\n" + weak, "Should-Fixed Strong Fit Should-Fix Should-Fix",
                  "Wеak at High", "雪 😀\r\n" + weak + "\r" + systemic,
                  weak.replace(" ", "\u2028", 1), weak.replace("\n", "\r\n"),
                  systemic.replace(" ", "\n", 1),
                  "Must-Fix " * 29120 + systemic, "\n" * 8191,
                  weak + "x" * (262144 - len(weak))]
        c = self.client()
        for i, text in enumerate(texts):
            with self.subTest(case=i):
                source = self.root / "invented-severity.txt"
                source.write_bytes(text.encode())
                oracle = subprocess.run(["bash", str(ROOT / "scripts/validate.sh"),
                                         "severity-floor", str(source)], capture_output=True)
                c.send(validation(str(i), text, "severity-floor"))
                value = c.next()
                self.assertEqual((value["id"], value["validator"], value["available"]),
                                 (str(i), "severity-floor", True))
                got = value["result"]
                self.assertEqual((got["exit_code"], got["stdout"].encode(), got["stderr"].encode()),
                                 (oracle.returncode, oracle.stdout, oracle.stderr))
                if text == "":
                    self.assertEqual((got["exit_code"], len(got["stdout"].encode())), (0, 73))
        for i, text in enumerate(("x" * 262145, "\n" * 8192, "\r" * 8192)):
            c.send(validation("over" + str(i), text, "severity-floor"))
            self.error(c.next(), "input_limit")
        self.assertEqual(c.end(), (0, [], b""))

    def test_decision_layer_exact_legacy_oracle_parity(self):
        fixtures = list((ROOT / "tests/fixtures/validators").glob("lc.*.decision-layer-check.*.md"))
        self.assertEqual(len(fixtures), 12)
        valid = (ROOT / "tests/fixtures/validators/lc.pass.decision-layer-check.pos.md").read_text()
        sections = "## Protected Elements\n- Keep one\n- Keep two\n- Keep three\n## Author Decisions\n- Keep one\n- Cut two\n- Defer three\n"
        absent_questions = sections + "## Appendix A\nExample.\n"
        marker = "Claim Ladder"
        thin = "## What Needs Work\nMust-Fix: invented pacing gap.\n"
        texts = [p.read_bytes().decode() for p in fixtures]
        texts += ["", valid, valid.replace("\n", "\r\n"), valid.replace("\n", "\r"),
                  "雪 😀\r\n" + valid, sections, absent_questions,
                  absent_questions + marker, absent_questions + "```\n" + marker + "\n```",
                  sections + marker, valid.replace("1. What", "- What"),
                  valid.replace("7. What is the book's controlling idea?\n", ""),
                  valid.replace("## Appendix C — Framework Notes\n", "## Appendix Sea\n"),
                  valid.replace("## Author Decisions\n", "## Editorial-Dispute Territory\n"),
                  valid.replace("## Protected Elements\n", "## Coalition-Partner Ground-Truth\n"),
                  valid.replace("## Protected Elements\n", "## Notes on Protected Elements\n"),
                  valid.replace("## Protected Elements\n", "## Protected Elements\n\n**Keep**\n\n**Cut**\n\n**Defer**\n"),
                  valid.replace("## What Needs Work\n", thin),
                  valid.replace("Must-Fix: pacing collapse", "Prose mentions Must-Fix: pacing collapse"),
                  valid.replace("Must-Fix: pacing collapse", "Must-Fix: gap\n\n## Next Section\nChapter 7, line 142. Chapter 9, line 220.\n\nMust-Fix: pacing collapse"),
                  valid + "\n## Appendix A\nMust-Fix: no references\n",
                  valid + "\n```\n<!-- override:decision-layer-control-questions -->\n```\n",
                  valid.replace("7. What is the book's controlling idea?\n", "") + "\n<!-- override:decision-layer-control-questions -->\n",
                  valid.replace("7. What is the book's controlling idea?\n", "") + "\n## Appendix A\n<!-- override:decision-layer-control-questions -->\n",
                  "\n" * 8191, "x" * 262144]
        c = self.client()
        for i, text in enumerate(texts):
            with self.subTest(case=i):
                source = self.root / "invented-decision.txt"
                source.write_bytes(text.encode())
                oracle = subprocess.run(["bash", str(ROOT / "scripts/validate.sh"),
                                         "decision-layer-check", str(source)], capture_output=True)
                c.send(validation(str(i), text, "decision-layer-check"))
                value = c.next()
                self.assertEqual((value["id"], value["validator"], value["available"]),
                                 (str(i), "decision-layer-check", True))
                got = value["result"]
                self.assertEqual((got["exit_code"], got["stdout"].encode(), got["stderr"].encode()),
                                 (oracle.returncode, oracle.stdout, oracle.stderr))
                if text == absent_questions:
                    self.assertIn("Check 3", got["stdout"])
                    self.assertIn("Check 4", got["stdout"])
                elif text in (absent_questions + marker, absent_questions + "```\n" + marker + "\n```"):
                    self.assertEqual(got["exit_code"], 0)
                    self.assertIn("Checks 3-4 skipped", got["stdout"])
        for i, text in enumerate(("x" * 262145, "\n" * 8192, "\r" * 8192)):
            c.send(validation("over" + str(i), text, "decision-layer-check"))
            self.error(c.next(), "input_limit")
        self.assertEqual(c.end(), (0, [], b""))

    def test_mixed_leaves_foreign_cwd_and_closed_worker_routes(self):
        clean = (ROOT / "tests/fixtures/validators/lc.pass.synthesis-sections.all-headings.md").read_text()
        c = self.client(cwd=self.root, env=dict(os.environ, PATH="", PYTHONPATH=str(self.root)))
        for i, (leaf, text, rc) in enumerate((("tone-check", "", 0),
                ("synthesis-sections", clean, 0), ("tone-check", "masterpiece", 1),
                ("synthesis-sections", "", 1), ("severity-floor", "", 0),
                ("severity-floor", "Weak at High", 1),
                ("decision-layer-check", "", 1),
                ("decision-layer-check", "## Control Questions\n1. One\n", 1))):
            c.send(validation(str(i), text, leaf)); got = c.next()
            self.assertEqual((got["id"], got["validator"], got["available"], got["result"]["exit_code"]),
                             (str(i), leaf, True, rc))
        c.send(cancel("unknown")); self.assertFalse(c.next()["cancelled"])
        self.assertEqual(c.end(), (0, [], b""))
        for argv in (("--worker-other",), ("--worker-synthesis-sections", "extra"),
                     ("--worker-severity-floor", "extra"),
                     ("--worker-decision-layer-check", "extra"),
                     ("--worker", "--worker-synthesis-sections")):
            result = subprocess.run([PYTHON, "-I", "-S", str(SCRIPT), *argv], capture_output=True)
            self.assertEqual((result.returncode, result.stdout), (2, b""))

    def test_closed_schemas_and_ids(self):
        cases = []
        for request in (validation(), cancel()):
            for key in request:
                absent = dict(request); del absent[key]; cases.append(absent)
                wrong = dict(request); wrong[key] = [] ; cases.append(wrong)
            extra = dict(request, path="/synthetic/path"); cases.append(extra)
        for v in (True, 1.0):
            cases.append(dict(validation(), protocol=v))
        for target in ("", "a" * 65, "../path", 3, None):
            cases.append(cancel(target))
        cases += [[], 5, None, dict(validation(), id="x " ), dict(validation(), validator="x/evil")]
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

    def test_framing_is_not_forgiving(self):
        valid = frame(validation())
        cases = [b"\n", b" \n", b"\xef\xbb\xbf" + valid, valid[:-1] + b"\r\n",
                 valid[:-1], b"\xff\n", b'{"protocol":1,"protocol":1}\n',
                 b'{"text":"\\ud800"}\n', b'{"text":"\xed\xa0\x80"}\n',
                 b'{"value":NaN}\n', b'{"value":Infinity}\n', b'{} garbage\n',
                 b'{"a":{"x":1,"x":2}}\n', b'[' * 9 + b'0' + b']' * 9 + b'\n',
                 b'[' * 2000 + b'0' + b']' * 2000 + b'\n']
        for data in cases:
            with self.subTest(data=data):
                c = self.client(); c.raw(data)
                if not data.endswith(b"\n"):
                    c.child.stdin.close()
                result = c.next()
                self.assertEqual(result["error"]["code"], "invalid_frame")
                self.assertIsNone(result["id"])
                self.assertEqual(c.end(), (2, [], b""))

    def test_admission_order_and_text_limits(self):
        c = self.client()
        c.send(validation("other", "x" * 262145, "other")); self.error(c.next(), "validator_unavailable")
        for i, text in enumerate(("x" * 262144, "😀" * 65536, "\n" * 8191, "\r\n" * 8191)):
            c.send(validation("at" + str(i), text)); self.assertTrue(c.next()["available"])
        for i, text in enumerate(("x" * 262145, "😀" * 65536 + "x", "\n" * 8192, "\r" * 8192)):
            c.send(validation("over" + str(i), text)); self.error(c.next(), "input_limit")
        self.assertEqual(c.end(), (0, [], b""))

    def test_frame_and_frame_count_limits(self):
        for extra in (0, 1):
            c = self.client()
            base = frame(cancel())[:-1]
            c.raw(base + b" " * (1048576 - len(base) + extra) + b"\n")
            got = c.next()
            self.assertEqual(got["type"], "cancel_result" if not extra else "protocol_error")
            self.assertEqual(c.end()[0], 0 if not extra else 2)
        c = self.client()
        for i in range(64):
            c.send(cancel("unknown", str(i))); self.assertFalse(c.next()["cancelled"])
        c.send(cancel("unknown", "over"))
        self.assertEqual(c.next()["error"]["code"], "session_limit")
        self.assertEqual(c.end(), (2, [], b""))

    def test_session_byte_limit(self):
        c = self.client()
        for i in range(16):
            base = frame(cancel("unknown", str(i)))[:-1]
            c.raw(base + b" " * (1048575 - len(base)) + b"\n")
            self.assertFalse(c.next()["cancelled"])
        c.raw(b"x")  # Exactly 16MiB accepted; the next byte is refused before admission.
        self.assertEqual(c.next()["error"]["code"], "session_limit")
        self.assertEqual(c.end(), (2, [], b""))

    def test_session_byte_boundary_preserves_identical_stream_prefix(self):
        outcomes = []
        for split in (False, True):
            c = self.client(script=self.script)
            prefix_responses = []
            for i in range(16):
                base = frame(cancel("unknown", str(i)))[:-1]
                length = 1048576 - (128 if i == 15 else 0)
                c.raw(base + b" " * (length - 1 - len(base)) + b"\n")
                prefix_responses.append(c.next())
            edge = frame(cancel("unknown", "edge"))
            padding = b" " * (129 - len(edge))
            if split:
                c.raw(edge)
                response = c.next()
                c.raw(padding)
            else:
                c.raw(edge + padding)
                response = c.next()
            self.assertEqual(response, {"protocol": 1, "type": "cancel_result", "id": "edge",
                "target": "unknown", "cancelled": False, "error": None})
            fatal = c.next()
            self.assertEqual(fatal["error"]["code"], "session_limit")
            self.assertEqual(c.end(), (2, [], b""))
            outcomes.append(prefix_responses + [response, fatal])
        self.assertEqual(*outcomes)

    @unittest.skipUnless(os.name == "posix", "POSIX development-host death/reaping evidence")
    def test_cancel_busy_race_and_reuse(self):
        self.sleeping(); c = self.client(script=self.script)
        c.send(validation(text="sleep")); pid = self.pid()
        c.send(validation("busy")); self.error(c.next(), "busy")
        c.send(validation("busy-synth", "", "synthesis-sections"))
        got = c.next(); self.error(got, "busy")
        self.assertEqual((got["id"], got["validator"]), ("busy-synth", "synthesis-sections"))
        c.send(validation("other", validator="other")); self.error(c.next(), "validator_unavailable")
        c.send(validation("limit", "\n" * 8192)); self.error(c.next(), "input_limit")
        c.send(cancel()); self.error(c.next(), "cancelled")
        self.assertTrue(c.next()["cancelled"]); self.dead(pid)
        c.send(validation("healthy")); self.assertTrue(c.next()["available"])
        c.send(cancel("healthy", "late")); self.assertFalse(c.next()["cancelled"])
        self.assertEqual(c.end(), (0, [], b""))

    @unittest.skipUnless(os.name == "posix", "POSIX development-host death/reaping evidence")
    def test_in_budget_synthesis_cancel_precedes_excess_session_byte(self):
        self.sleeping(); c = self.client(script=self.script)
        used = 0
        for i in range(15):
            base = frame(cancel("unknown", str(i)))[:-1]
            c.raw(base + b" " * (1048575 - len(base)) + b"\n")
            self.assertFalse(c.next()["cancelled"]); used += 1048576
        request = frame(validation("synth", "sleep", "synthesis-sections"))
        c.raw(request); used += len(request); pid = self.pid()
        base = frame(cancel("unknown", "padding"))[:-1]
        length = 16777216 - used - 128
        c.raw(base + b" " * (length - 1 - len(base)) + b"\n")
        self.assertFalse(c.next()["cancelled"])
        edge = frame(cancel("synth", "edge"))
        c.raw(edge + b" " * (129 - len(edge)))
        got = c.next(); self.error(got, "cancelled")
        self.assertEqual((got["id"], got["validator"]), ("synth", "synthesis-sections"))
        self.assertTrue(c.next()["cancelled"])
        self.assertEqual(c.next()["error"]["code"], "session_limit")
        self.assertEqual(c.end(), (2, [], b"")); self.dead(pid)

    @unittest.skipUnless(os.name == "posix", "POSIX development-host death/reaping evidence")
    def test_exact_cancel_target_boundary_and_invalid_active_targets(self):
        for target in ("x" * 64, "", "x" * 65, "bad/target", None, 2):
            with self.subTest(target=target):
                self.sleeping(); self.pidfile.unlink(missing_ok=True)
                c = self.client(script=self.script)
                c.send(validation("x" * 64, "sleep")); pid = self.pid()
                c.send(cancel(target))
                self.error(c.next(), "cancelled" if target == "x" * 64 else "session_ended")
                response = c.next()
                if target == "x" * 64:
                    self.assertTrue(response["cancelled"])
                else:
                    self.assertEqual(response["error"]["code"], "invalid_request")
                    self.assertIsNone(response["id"])
                self.assertEqual(c.end(), (0 if target == "x" * 64 else 2, [], b""))
                self.dead(pid)

    @unittest.skipUnless(os.name == "posix", "POSIX development-host death/reaping evidence")
    def test_real_fixed_timeout_and_reuse(self):
        self.sleeping(); c = self.client(script=self.script)
        start = time.monotonic(); c.send(validation(text="sleep")); pid = self.pid()
        self.error(c.next(), "timeout")
        elapsed = time.monotonic() - start
        self.assertGreaterEqual(elapsed, 5); self.assertLess(elapsed, 7)
        self.dead(pid)
        c.send(validation("healthy")); self.assertTrue(c.next()["available"])
        self.assertEqual(c.end(), (0, [], b""))

    @unittest.skipUnless(os.name == "posix", "POSIX development-host pipe/death evidence")
    def test_saturated_stderr_and_output_failure_share_cleanup_budget(self):
        # Actual inherited pipes, unmodified deadlines, and a SIGTERM-ignoring worker.
        for action, leaf in ((action, leaf) for leaf in ("tone-check", "synthesis-sections")
                             for action in ("blocked", "broken", "cancel", "fatal")):
            with self.subTest(action=action, leaf=leaf):
                self.sleeping(); self.pidfile.unlink(missing_ok=True)
                out_r, out_w = os.pipe(); err_r, err_w = os.pipe()
                def fill(fd):
                    os.set_blocking(fd, False)
                    count = 0
                    try:
                        while True:
                            count += os.write(fd, b"x" * 4096)
                    except BlockingIOError:
                        pass
                    os.set_blocking(fd, True)
                    return count
                fill(err_w)  # Never drained while the coordinator is alive.
                prefix = b""
                first = None
                if action == "broken":
                    os.close(out_r)
                else:
                    capacity = fill(out_w)
                    if action in ("cancel", "fatal"):
                        code = "cancelled" if action == "cancel" else "session_ended"
                        first = {"protocol": 1, "type": "result", "id": "r1",
                            "validator": leaf, "available": False, "result": None,
                            "error": {"code": code, "message": "Validator unavailable: " + code + "."}}
                        # Leave room for exactly the first terminal envelope, forcing
                        # the subsequent control/fatal write onto the same deadline.
                        left = capacity
                        while left:
                            left -= len(os.read(out_r, left))
                        prefix = b"x" * (capacity - len(frame(first)) - 1) + b"\n"
                        self.assertEqual(os.write(out_w, prefix), len(prefix))
                p = subprocess.Popen([PYTHON, "-I", "-S", str(self.script)],
                    stdin=subprocess.PIPE, stdout=out_w, stderr=err_w)
                os.close(out_w); os.close(err_w)
                try:
                    p.stdin.write(frame(validation(text="sleep", validator=leaf))); p.stdin.flush(); pid = self.pid()
                    started = time.monotonic()
                    request = (frame(cancel()) if action == "cancel" else b"{}\n"
                        if action == "fatal" else frame(validation("busy")))
                    p.stdin.write(request); p.stdin.flush()
                    self.assertEqual(p.wait(timeout=2.2), 2)
                    self.assertLess(time.monotonic() - started, 2.2)  # Parent scheduling allowance only.
                    self.dead(pid)  # Absence also excludes an unreaped zombie.
                    if first is not None:
                        delivered = bytearray()
                        while True:
                            data = os.read(out_r, 4096)
                            if not data: break
                            delivered.extend(data)
                        self.assertEqual(bytes(delivered), prefix + frame(first))
                finally:
                    if p.poll() is None: p.kill(); p.wait()
                    p.stdin.close(); os.close(err_r)
                    if action != "broken": os.close(out_r)

    @unittest.skipUnless(os.name == "posix", "POSIX development-host death/reaping evidence")
    def test_synthesis_lifecycle_shared_slot_and_other_leaf_reuse(self):
        for action in ("cancel", "bad_target", "partial", "eof", "SIGTERM", "SIGINT", "timeout"):
            with self.subTest(action=action):
                self.sleeping(); self.pidfile.unlink(missing_ok=True)
                c = self.client(script=self.script)
                started = time.monotonic()
                c.send(validation("synth", "sleep", "synthesis-sections")); pid = self.pid()
                # Both leaves share one slot, with unsupported/limits preceding busy.
                for id, leaf, text, code in (("busy-tone", "tone-check", "", "busy"),
                        ("busy-synth", "synthesis-sections", "", "busy"),
                        ("unknown", "other", "x" * 262145, "validator_unavailable"),
                        ("limit", "synthesis-sections", "x" * 262145, "input_limit")):
                    c.send(validation(id, text, leaf)); got = c.next(); self.error(got, code)
                    self.assertEqual((got["id"], got["validator"]), (id, leaf))
                if action == "cancel": c.send(cancel("synth"))
                elif action == "bad_target": c.send(cancel("x" * 65))
                elif action == "partial": c.raw(b"{}"); c.child.stdin.close()
                elif action == "eof": c.child.stdin.close()
                elif action != "timeout": c.child.send_signal(getattr(signal, action))
                got = c.next()
                self.error(got, "cancelled" if action == "cancel" else "timeout" if action == "timeout" else "session_ended")
                self.assertEqual((got["id"], got["validator"]), ("synth", "synthesis-sections"))
                self.dead(pid)
                if action == "timeout":
                    self.assertGreaterEqual(time.monotonic() - started, 5)
                    self.assertLess(time.monotonic() - started, 7)
                if action == "cancel": self.assertTrue(c.next()["cancelled"])
                elif action in ("bad_target", "partial"):
                    self.assertEqual(c.next()["error"]["code"], "invalid_request" if action == "bad_target" else "invalid_frame")
                if action in ("cancel", "timeout"):
                    c.send(validation("healthy", "", "tone-check")); got = c.next()
                    self.assertEqual((got["id"], got["validator"], got["available"]), ("healthy", "tone-check", True))
                    c.send(cancel("synth", "late")); self.assertFalse(c.next()["cancelled"])
                self.assertEqual(c.end(), (0 if action in ("cancel", "timeout", "eof") else 2, [], b""))

    @unittest.skipUnless(os.name == "posix", "POSIX development-host death/reaping evidence")
    def test_severity_lifecycle_shared_slot_and_recovery(self):
        for action in ("cancel", "eof", "fatal", "SIGTERM", "timeout"):
            with self.subTest(action=action):
                self.sleeping(); self.pidfile.unlink(missing_ok=True)
                c = self.client(script=self.script)
                started = time.monotonic()
                c.send(validation("sev", "sleep", "severity-floor")); pid = self.pid()
                for id, leaf, text, code in (("busy-tone", "tone-check", "", "busy"),
                        ("busy-synth", "synthesis-sections", "", "busy"),
                        ("busy-sev", "severity-floor", "", "busy"),
                        ("unknown", "other", "x" * 262145, "validator_unavailable"),
                        ("limit", "severity-floor", "x" * 262145, "input_limit")):
                    c.send(validation(id, text, leaf)); got = c.next(); self.error(got, code)
                    self.assertEqual((got["id"], got["validator"]), (id, leaf))
                if action == "cancel": c.send(cancel("sev"))
                elif action == "eof": c.child.stdin.close()
                elif action == "fatal": c.raw(b"{}\n")
                elif action == "SIGTERM": c.child.send_signal(signal.SIGTERM)
                got = c.next()
                self.error(got, "cancelled" if action == "cancel" else "timeout" if action == "timeout" else "session_ended")
                self.assertEqual((got["id"], got["validator"]), ("sev", "severity-floor"))
                self.dead(pid)
                if action == "timeout":
                    self.assertGreaterEqual(time.monotonic() - started, 5)
                    self.assertLess(time.monotonic() - started, 7)
                if action == "cancel": self.assertTrue(c.next()["cancelled"])
                elif action == "fatal": self.assertEqual(c.next()["error"]["code"], "invalid_request")
                if action in ("cancel", "timeout"):
                    c.send(validation("healthy", "", "synthesis-sections")); got = c.next()
                    self.assertEqual((got["id"], got["validator"], got["available"]),
                                     ("healthy", "synthesis-sections", True))
                    c.send(cancel("sev", "late")); self.assertFalse(c.next()["cancelled"])
                self.assertEqual(c.end(), (0 if action in ("cancel", "timeout", "eof") else 2, [], b""))

    @unittest.skipUnless(os.name == "posix", "POSIX development-host death/reaping evidence")
    def test_decision_layer_lifecycle_shared_slot_and_recovery(self):
        for action in ("cancel", "eof", "partial", "fatal", "SIGTERM", "timeout"):
            with self.subTest(action=action):
                self.sleeping(); self.pidfile.unlink(missing_ok=True)
                c = self.client(script=self.script)
                started = time.monotonic()
                c.send(validation("decision", "sleep", "decision-layer-check")); pid = self.pid()
                for id, leaf, text, code in (("busy-tone", "tone-check", "", "busy"),
                        ("busy-synth", "synthesis-sections", "", "busy"),
                        ("busy-severity", "severity-floor", "", "busy"),
                        ("busy-decision", "decision-layer-check", "", "busy"),
                        ("unknown", "other", "x" * 262145, "validator_unavailable"),
                        ("limit", "decision-layer-check", "x" * 262145, "input_limit")):
                    c.send(validation(id, text, leaf)); got = c.next(); self.error(got, code)
                    self.assertEqual((got["id"], got["validator"]), (id, leaf))
                c.send(cancel("unknown", "unknown-cancel"))
                self.assertFalse(c.next()["cancelled"])
                if action == "cancel": c.send(cancel("decision"))
                elif action == "eof": c.child.stdin.close()
                elif action == "partial": c.raw(b"{}"); c.child.stdin.close()
                elif action == "fatal": c.raw(b"{}\n")
                elif action == "SIGTERM": c.child.send_signal(signal.SIGTERM)
                got = c.next()
                self.error(got, "cancelled" if action == "cancel" else "timeout" if action == "timeout" else "session_ended")
                self.assertEqual((got["id"], got["validator"]), ("decision", "decision-layer-check"))
                self.dead(pid)
                if action == "timeout":
                    self.assertGreaterEqual(time.monotonic() - started, 5)
                    self.assertLess(time.monotonic() - started, 7)
                if action == "cancel": self.assertTrue(c.next()["cancelled"])
                elif action in ("partial", "fatal"):
                    self.assertEqual(c.next()["error"]["code"],
                                     "invalid_frame" if action == "partial" else "invalid_request")
                if action in ("cancel", "timeout"):
                    c.send(validation("healthy", "", "severity-floor")); got = c.next()
                    self.assertEqual((got["id"], got["validator"], got["available"]),
                                     ("healthy", "severity-floor", True))
                    c.send(cancel("decision", "late")); self.assertFalse(c.next()["cancelled"])
                self.assertEqual(c.end(), (0 if action in ("cancel", "timeout", "eof") else 2, [], b""))

    def test_fixed_idle_and_session_deadlines_with_test_only_clock(self):
        # A disposable test launcher accelerates monotonic time, not protocol limits.
        # The production script and request schema have no clock/limit override.
        launcher = self.root / "synthetic-clock-launcher.py"
        launcher.write_text("import runpy,sys,time\n"
            "real=time.monotonic\norigin=real()\n"
            "time.monotonic=lambda: origin+(real()-origin)*100\n"
            "sys.argv=[%r]\nrunpy.run_path(%r,run_name='__main__')\n" % (str(self.script), str(self.script)))
        c = self.client(script=self.script, launcher=launcher)
        started = time.monotonic(); c.raw(b"{")
        self.assertEqual(c.next()["error"]["code"], "session_limit")
        self.assertGreaterEqual(time.monotonic() - started, .6)
        self.assertEqual(c.end(), (2, [], b""))
        c = self.client(script=self.script, launcher=launcher)
        started = time.monotonic()
        while c.child.poll() is None and time.monotonic() - started < 8:
            try: c.raw(b" ")
            except BrokenPipeError: break
            time.sleep(.1)
        self.assertEqual(c.next()["error"]["code"], "session_limit")
        self.assertGreaterEqual(time.monotonic() - started, 6)
        self.assertLess(time.monotonic() - started, 8)
        self.assertEqual(c.end(), (2, [], b""))

    @unittest.skipUnless(os.name == "posix", "POSIX development-host death/reaping evidence")
    def test_fatal_active_target_eof_and_termination_cleanup(self):
        for action in ("bad_target", "partial", "eof", "SIGTERM", "SIGINT"):
            with self.subTest(action=action):
                self.sleeping(); self.pidfile.unlink(missing_ok=True)
                c = self.client(script=self.script); c.send(validation(text="sleep")); pid = self.pid()
                if action == "bad_target": c.send(cancel("x" * 65))
                elif action == "partial": c.raw(b"{}"); c.child.stdin.close()
                elif action == "eof": c.child.stdin.close()
                else: c.child.send_signal(getattr(signal, action))
                self.error(c.next(), "session_ended")
                if action in ("bad_target", "partial"):
                    self.assertEqual(c.next()["error"]["code"], "invalid_request" if action == "bad_target" else "invalid_frame")
                status, remainder, stderr = c.end()
                self.assertEqual(status, 0 if action == "eof" else 2)
                self.assertEqual((remainder, stderr), ([], b"")); self.dead(pid)

    def test_dependency_and_worker_failures_are_unavailable(self):
        for code in ("raise ImportError('synthetic')\n", "def tone_check(text): raise RuntimeError(text)\n",
                     "import os\ndef tone_check(text): os._exit(3)\n",
                     "def tone_check(text): return []\n", "def tone_check(text): print(text); return [],[],'OK','FAIL'\n",
                     "import sys\ndef tone_check(text): sys.stderr.write(text); return [],[],'OK','FAIL'\n"):
            with self.subTest(code=code):
                (self.scripts / "letter_checks.py").write_text(code)
                before = set(p.relative_to(self.root) for p in self.root.rglob('*') if p.is_file())
                c = self.client(script=self.script); c.send(validation(text="SYNTHETIC_SENTINEL"))
                got = c.next(); self.error(got, "runner_dependency_unavailable" if "ImportError" in code else "worker_failed")
                self.assertNotIn("SYNTHETIC_SENTINEL", json.dumps(got))
                self.assertEqual(c.end(), (0, [], b""))
                self.assertEqual(before, set(p.relative_to(self.root) for p in self.root.rglob('*') if p.is_file()))
                self.assertTrue(all(b'SYNTHETIC_SENTINEL' not in p.read_bytes() for p in self.root.rglob('*') if p.is_file()))
        (self.scripts / "letter_checks.py").unlink()
        c = self.client(script=self.script); c.send(validation()); self.error(c.next(), "runner_dependency_unavailable")
        self.assertEqual(c.end(), (0, [], b""))

    def test_synthesis_dependency_malformed_child_and_death_are_unavailable(self):
        self.pidfile = self.root / "dead-worker.pid"
        bodies = ("raise ImportError('synthetic')\n", "def synthesis_sections(text): raise RuntimeError(text)\n",
                  "import os\ndef synthesis_sections(text):\n"
                  " open(%r,'w').write(str(os.getpid()))\n os._exit(3)\n" % str(self.pidfile),
                  "def synthesis_sections(text): return []\n",
                  "def synthesis_sections(text): print(text); return [],[],'OK','FAIL'\n",
                  "import sys\ndef synthesis_sections(text): sys.stderr.write(text); return [],[],'OK','FAIL'\n",
                  "import json,os\ndef synthesis_sections(text):\n"
                  " os.write(1,(json.dumps({'exit_code':0,'stdout':'OK','stderr':'','validator':'tone-check','id':'forged'})+'\\n').encode())\n"
                  " return [],[],'OK','FAIL'\n")
        for body in bodies:
            with self.subTest(body=body):
                (self.scripts / "letter_checks.py").write_text(body + "\ndef tone_check(text): return [],[],'tone OK','FAIL'\n")
                before = set(p.relative_to(self.root) for p in self.root.rglob('*') if p.is_file())
                c = self.client(script=self.script)
                c.send(validation("synth", "SYNTHETIC_SENTINEL", "synthesis-sections")); got = c.next()
                self.error(got, "runner_dependency_unavailable" if "ImportError" in body else "worker_failed")
                self.assertEqual((got["id"], got["validator"]), ("synth", "synthesis-sections"))
                self.assertNotIn("SYNTHETIC_SENTINEL", json.dumps(got))
                if "os._exit" in body:
                    if os.name == "posix": self.dead(self.pid())
                    self.pidfile.unlink()  # Remove the test harness's deliberate PID marker.
                if "ImportError" not in body:
                    c.send(validation("healthy")); self.assertTrue(c.next()["available"])
                self.assertEqual(c.end(), (0, [], b""))
                self.assertEqual(before, set(p.relative_to(self.root) for p in self.root.rglob('*') if p.is_file()))
                self.assertTrue(all(b'SYNTHETIC_SENTINEL' not in p.read_bytes() for p in self.root.rglob('*') if p.is_file()))
        (self.scripts / "letter_checks.py").unlink()
        c = self.client(script=self.script)
        c.send(validation("synth", "", "synthesis-sections")); self.error(c.next(), "runner_dependency_unavailable")
        self.assertEqual(c.end(), (0, [], b""))

    def test_severity_dependency_malformed_child_and_death_are_unavailable(self):
        self.pidfile = self.root / "dead-worker.pid"
        bodies = ("raise ImportError('synthetic')\n",
                  "def severity_floor(text): raise RuntimeError(text)\n",
                  "import os\ndef severity_floor(text):\n"
                  " open(%r,'w').write(str(os.getpid()))\n os._exit(3)\n" % str(self.pidfile),
                  "def severity_floor(text): return []\n",
                  "def severity_floor(text): print(text); return [],[],'OK','FAIL'\n",
                  "import sys\ndef severity_floor(text): sys.stderr.write(text); return [],[],'OK','FAIL'\n")
        for body in bodies:
            with self.subTest(body=body):
                (self.scripts / "letter_checks.py").write_text(body + "\ndef tone_check(text): return [],[],'tone OK','FAIL'\n")
                c = self.client(script=self.script)
                c.send(validation("sev", "SYNTHETIC_SENTINEL", "severity-floor")); got = c.next()
                self.error(got, "runner_dependency_unavailable" if "ImportError" in body else "worker_failed")
                self.assertEqual((got["id"], got["validator"]), ("sev", "severity-floor"))
                self.assertNotIn("SYNTHETIC_SENTINEL", json.dumps(got))
                if "os._exit" in body:
                    if os.name == "posix": self.dead(self.pid())
                    self.pidfile.unlink()
                if "ImportError" not in body:
                    c.send(validation("healthy")); self.assertTrue(c.next()["available"])
                self.assertEqual(c.end(), (0, [], b""))
        (self.scripts / "letter_checks.py").unlink()
        c = self.client(script=self.script)
        c.send(validation("sev", "", "severity-floor")); self.error(c.next(), "runner_dependency_unavailable")
        self.assertEqual(c.end(), (0, [], b""))
        # The fixed sibling dependency fails at import, never becomes a pass.
        shutil.copyfile(SCRIPT.parent / "letter_checks.py", self.scripts / "letter_checks.py")
        (self.scripts / "override_marker.py").unlink()
        c = self.client(script=self.script)
        c.send(validation("sev2", "", "severity-floor")); self.error(c.next(), "runner_dependency_unavailable")
        self.assertEqual(c.end(), (0, [], b""))

    def test_decision_layer_dependency_child_output_and_death_are_unavailable(self):
        self.pidfile = self.root / "dead-worker.pid"
        bodies = ("raise ImportError('synthetic')\n",
                  "def decision_layer_check(text): raise RuntimeError(text)\n",
                  "import os\ndef decision_layer_check(text):\n"
                  " open(%r,'w').write(str(os.getpid()))\n os._exit(3)\n" % str(self.pidfile),
                  "def decision_layer_check(text): return []\n",
                  "def decision_layer_check(text): print(text); return [],[],'OK','FAIL'\n",
                  "import sys\ndef decision_layer_check(text): sys.stderr.write(text); return [],[],'OK','FAIL'\n",
                  "import json,os\ndef decision_layer_check(text):\n"
                  " os.write(1,(json.dumps({'exit_code':0,'stdout':'OK','stderr':'','id':'forged'})+'\\n').encode())\n"
                  " return [],[],'OK','FAIL'\n")
        for body in bodies:
            with self.subTest(body=body):
                (self.scripts / "letter_checks.py").write_text(body + "\ndef tone_check(text): return [],[],'tone OK','FAIL'\n")
                c = self.client(script=self.script)
                c.send(validation("decision", "SYNTHETIC_SENTINEL", "decision-layer-check")); got = c.next()
                self.error(got, "runner_dependency_unavailable" if "ImportError" in body else "worker_failed")
                self.assertEqual((got["id"], got["validator"]), ("decision", "decision-layer-check"))
                self.assertNotIn("SYNTHETIC_SENTINEL", json.dumps(got))
                if "os._exit" in body:
                    if os.name == "posix": self.dead(self.pid())
                    self.pidfile.unlink()
                if "ImportError" not in body:
                    c.send(validation("healthy")); self.assertTrue(c.next()["available"])
                self.assertEqual(c.end(), (0, [], b""))
        (self.scripts / "letter_checks.py").unlink()
        c = self.client(script=self.script)
        c.send(validation("decision", "", "decision-layer-check"))
        self.error(c.next(), "runner_dependency_unavailable")
        self.assertEqual(c.end(), (0, [], b""))
        shutil.copyfile(SCRIPT.parent / "letter_checks.py", self.scripts / "letter_checks.py")
        (self.scripts / "override_marker.py").unlink()
        c = self.client(script=self.script)
        c.send(validation("decision2", "", "decision-layer-check"))
        self.error(c.next(), "runner_dependency_unavailable")
        self.assertEqual(c.end(), (0, [], b""))

    def test_environment_scrubbing_and_socket_guard(self):
        (self.scripts / "letter_checks.py").write_text(
            "import os,socket,subprocess,sys\ndef tone_check(text):\n"
            " assert 'OPENAI_API_KEY' not in os.environ and 'HTTPS_PROXY' not in os.environ\n"
            " assert 'PYTHONPATH' not in os.environ and os.environ['TZ']=='UTC'\n"
            " try: socket.socket()\n"
            " except PermissionError: pass\n"
            " else: raise AssertionError('socket allowed')\n"
            " try: subprocess.Popen([sys.executable,'-c','pass'])\n"
            " except PermissionError: return [],[],'socket and spawn denied','FAIL'\n"
            " raise AssertionError('spawn allowed')\n"
            "synthesis_sections = decision_layer_check = tone_check\n")
        c = self.client(script=self.script, env=dict(os.environ, OPENAI_API_KEY="synthetic", HTTPS_PROXY="synthetic", PYTHONPATH="synthetic"))
        c.send(validation()); self.assertEqual(c.next()["result"]["stdout"], "socket and spawn denied\n")
        c.send(validation("synth", "", "synthesis-sections"))
        self.assertEqual(c.next()["result"]["stdout"], "socket and spawn denied\n")
        c.send(validation("decision", "", "decision-layer-check"))
        self.assertEqual(c.next()["result"]["stdout"], "socket and spawn denied\n")
        self.assertEqual(c.end(), (0, [], b""))

    def test_output_limit_exact_and_over(self):
        # Derive real envelope boundaries, including escaped LF and the final delimiter.
        for leaf, over in ((leaf, over) for leaf in ("tone-check", "synthesis-sections", "decision-layer-check") for over in (False, True)):
            request = validation(validator=leaf)
            prototype = {"protocol":1,"type":"result","id":"r1","validator":leaf,"available":True,
                         "result":{"exit_code":0,"stdout":"\n","stderr":""},"error":None}
            size = 32768 - len(frame(prototype)) + int(over)
            (self.scripts / "letter_checks.py").write_text("def tone_check(text): return [],[], 'x'*%d, 'FAIL'\nsynthesis_sections = decision_layer_check = tone_check\n" % size)
            c = self.client(script=self.script); c.send(request); got = c.next()
            if over: self.error(got, "output_limit")
            else: self.assertEqual(len(frame(got)), 32768)
            self.assertEqual(c.end(), (0, [], b""))

    def inventory_check(self):
        return subprocess.run([PYTHON, "-I", "-S", str(self.script), "--check-inventory"], capture_output=True)

    def test_inventory_actual_registry_drift_and_closed_metadata(self):
        baseline = json.loads(self.metadata.read_text())
        self.assertEqual(self.inventory_check().returncode, 0)
        registry = self.scripts / "validate.sh"; original = registry.read_text()
        for replacement in ("invented-tone", "tone-check tone-check", "", "tone-check invented"):
            registry.write_text(original.replace("tone-check", replacement, 1))
            self.assertEqual(self.inventory_check().returncode, 1)
        registry.write_text(original + '\nAGG_VALIDATORS="$DYNAMIC"\n')
        self.assertEqual(self.inventory_check().returncode, 1)
        registry.write_text(original)
        for change in ("omit", "add", "duplicate", "class", "reason", "desktop", "development", "extra", "version"):
            value = copy.deepcopy(baseline)
            if change == "omit": value["validators"].pop()
            elif change == "add": value["validators"].append(dict(value["validators"][0], id="invented"))
            elif change == "duplicate": value["validators"].append(value["validators"][0])
            elif change == "class": value["validators"][0]["desktop_disposition"] = "unknown"
            elif change == "reason": value["validators"][0]["omitted_capability"] = ""
            elif change == "desktop": value["validators"][0]["desktop_disposition"] = "desktop-supported"
            elif change == "development": value["validators"][0]["development_support"] = "tone-check-v1"
            elif change == "extra": value["extra"] = True
            else: value["version"] = True
            self.metadata.write_text(json.dumps(value))
            self.assertEqual(self.inventory_check().returncode, 1, change)
        value = copy.deepcopy(baseline)
        value["validators"].append(dict(value["validators"][6], id="invented-support-none"))
        self.metadata.write_text(json.dumps(value))
        self.assertEqual(self.inventory_check().returncode, 1)
        c = self.client(script=self.script)
        for id, leaf in (("tone", "tone-check"), ("synth", "synthesis-sections"),
                         ("sev", "severity-floor"), ("decision", "decision-layer-check")):
            c.send(validation(id, "", leaf)); self.assertTrue(c.next()["available"])
        c.send(validation("invented", "", "invented-support-none"))
        self.error(c.next(), "validator_unavailable")
        self.assertEqual(c.end(), (0, [], b""))
        for change in ("duplicate", "bad-id", "empty-reason", "false-desktop"):
            value = copy.deepcopy(baseline)
            sev = next(r for r in value["validators"] if r["id"] == "severity-floor")
            if change == "duplicate": value["validators"].append(copy.deepcopy(sev))
            elif change == "bad-id": sev["id"] = "bad/id"
            elif change == "empty-reason": sev["omitted_capability"] = ""
            else: sev["desktop_disposition"] = "desktop-supported"
            self.metadata.write_text(json.dumps(value))
            self.assertEqual(self.inventory_check().returncode, 1)
            c = self.client(script=self.script)
            for id, leaf in (("tone", "tone-check"), ("synth", "synthesis-sections"),
                             ("sev", "severity-floor"), ("decision", "decision-layer-check")):
                c.send(validation(id, "", leaf))
                self.error(c.next(), "runner_dependency_unavailable")
            self.assertEqual(c.end(), (0, [], b""))

    def test_missing_bad_or_oversized_metadata_disables_leaf(self):
        for data in (None, b"{}", b" " * 65537, b'{"version":1,"version":1,"validators":[]}'):
            if data is None: self.metadata.unlink(missing_ok=True)
            else: self.metadata.write_bytes(data)
            c = self.client(script=self.script)
            c.send(validation()); self.error(c.next(), "runner_dependency_unavailable")
            c.send(validation("synth", "", "synthesis-sections")); self.error(c.next(), "runner_dependency_unavailable")
            c.send(validation("sev", "", "severity-floor")); self.error(c.next(), "runner_dependency_unavailable")
            c.send(validation("decision", "", "decision-layer-check")); self.error(c.next(), "runner_dependency_unavailable")
            c.send(validation("other", validator="other")); self.error(c.next(), "validator_unavailable")
            self.assertEqual(c.end(), (0, [], b""))
            self.assertEqual(self.inventory_check().returncode, 1)

    def test_four_exact_inventory_mappings_required_at_runtime_and_check(self):
        baseline = json.loads(self.metadata.read_text())
        for change in ("swap", "swap-sev", "unknown", "unknown-sev", "omit-tone", "omit-synth",
                       "omit-sev", "omit-decision", "disable-tone", "disable-synth", "disable-sev",
                       "disable-decision", "swap-decision", "unknown-decision", "desktop", "desktop-sev",
                       "desktop-decision"):
            with self.subTest(change=change):
                value = copy.deepcopy(baseline)
                tone = next(r for r in value["validators"] if r["id"] == "tone-check")
                synth = next(r for r in value["validators"] if r["id"] == "synthesis-sections")
                sev = next(r for r in value["validators"] if r["id"] == "severity-floor")
                decision = next(r for r in value["validators"] if r["id"] == "decision-layer-check")
                if change == "swap":
                    tone["development_support"], synth["development_support"] = synth["development_support"], tone["development_support"]
                elif change == "swap-sev":
                    synth["development_support"], sev["development_support"] = sev["development_support"], synth["development_support"]
                elif change == "swap-decision":
                    sev["development_support"], decision["development_support"] = decision["development_support"], sev["development_support"]
                elif change == "unknown": synth["development_support"] = "synthesis-v2"
                elif change == "unknown-sev": sev["development_support"] = "severity-v2"
                elif change == "unknown-decision": decision["development_support"] = "decision-v2"
                elif change.startswith("omit-"):
                    value["validators"].remove({"omit-tone": tone, "omit-synth": synth, "omit-sev": sev,
                                                "omit-decision": decision}[change])
                elif change.startswith("disable-"):
                    {"disable-tone": tone, "disable-synth": synth, "disable-sev": sev,
                     "disable-decision": decision}[change]["development_support"] = "none"
                else: {"desktop": synth, "desktop-sev": sev,
                       "desktop-decision": decision}[change]["desktop_disposition"] = "desktop-supported"
                self.metadata.write_text(json.dumps(value)); self.assertEqual(self.inventory_check().returncode, 1)
                c = self.client(script=self.script)
                for id, leaf, text, code in (("unknown", "other", "x" * 262145, "validator_unavailable"),
                        ("limit", "synthesis-sections", "x" * 262145, "input_limit"),
                        ("tone", "tone-check", "", "runner_dependency_unavailable"),
                        ("synth", "synthesis-sections", "", "runner_dependency_unavailable"),
                        ("sev", "severity-floor", "", "runner_dependency_unavailable"),
                        ("decision", "decision-layer-check", "", "runner_dependency_unavailable")):
                    c.send(validation(id, text, leaf)); got = c.next(); self.error(got, code)
                    self.assertEqual((got["id"], got["validator"]), (id, leaf))
                self.assertEqual(c.end(), (0, [], b""))
        self.metadata.write_text(json.dumps(baseline)); self.assertEqual(self.inventory_check().returncode, 0)
        c = self.client(script=self.script); c.send(validation(validator="cost_floor"))
        self.error(c.next(), "validator_unavailable"); self.assertEqual(c.end(), (0, [], b""))

    def test_metadata_byte_and_reason_scalar_boundaries(self):
        value = json.loads(self.metadata.read_text())
        for length in (1, 256, 257):
            value["validators"][0]["omitted_capability"] = "😀" * length
            self.metadata.write_text(json.dumps(value))
            self.assertEqual(self.inventory_check().returncode, int(length > 256))
        value["validators"][0]["omitted_capability"] = "synthetic omission"
        raw = json.dumps(value).encode()
        self.metadata.write_bytes(raw + b" " * (65536 - len(raw)))
        self.assertEqual(self.inventory_check().returncode, 0)
        self.metadata.write_bytes(raw + b" " * (65537 - len(raw)))
        self.assertEqual(self.inventory_check().returncode, 1)

    def test_inventory_row_limit_and_no_bash_execution(self):
        registry = self.scripts / "validate.sh"
        for count in (512, 513):
            rows = [{"id": "tone-check" if i == 0 else "synthesis-sections" if i == 1 else "severity-floor" if i == 2 else "decision-layer-check" if i == 3 else "v%d" % i,
                     "desktop_disposition": "not-yet-supported",
                     "development_support": "tone-check-v1" if i == 0 else "synthesis-sections-v1" if i == 1 else "severity-floor-v1" if i == 2 else "decision-layer-check-v1" if i == 3 else "none",
                     "omitted_capability": "Synthetic unavailable validation."} for i in range(count)]
            self.metadata.write_text(json.dumps({"version":1,"validators":rows}, separators=(",",":")))
            # Keep the raw metadata inside its independent byte bound.
            if self.metadata.stat().st_size > 65536:
                for row in rows: row['omitted_capability'] = 'Unavailable.'
                self.metadata.write_text(json.dumps({"version":1,"validators":rows}, separators=(",",":")))
            self.assertLessEqual(self.metadata.stat().st_size, 65536)
            registry.write_text('AGG_VALIDATORS="' + ' '.join(r['id'] for r in rows) + '"\n')
            self.assertEqual(self.inventory_check().returncode, int(count > 512))
        marker = self.root / "must-not-exist"
        registry.write_text('AGG_VALIDATORS="$(touch %s) tone-check"\n' % marker)
        self.assertEqual(self.inventory_check().returncode, 1)
        self.assertFalse(marker.exists())


if __name__ == "__main__":
    unittest.main()
