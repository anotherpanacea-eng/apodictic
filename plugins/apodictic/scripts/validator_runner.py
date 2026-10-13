#!/usr/bin/env python3
"""Development JSONL adapter for fixed text validator leaves (stdlib only).

Run with a supplied interpreter: python -I -S validator_runner.py. Each validation
runs in a disposable worker. This source tool supplies neither a desktop
interpreter nor a native sandbox.
"""
import collections
import json
import os
from pathlib import Path
import queue
import re
import signal
import subprocess
import sys
import threading
import time

FRAME_BYTES = 1048576
TEXT_BYTES = 262144
TEXT_LINES = 8192
RESPONSE_BYTES = 32768
WORK_SECONDS = 5
CLEANUP_SECONDS = 2
SCRIPT = Path(__file__).resolve()
HERE = SCRIPT.parent
IDENTIFIER = re.compile(r"[A-Za-z0-9_-]{1,64}\Z")


def four_tuple(errors, warnings, ok_line, failed_line):
    """letter_checks.run_check's stdout lines and exit code."""
    return int(bool(errors)), warnings + errors + (["", failed_line] if errors else [ok_line])


def raw(exit_code, lines):
    """letter_checks.run_raw_check's stdout lines and exit code."""
    return exit_code, lines


# The only runnable leaves: validator id -> (letter_checks registry, result formatter).
# Adding a leaf is one row here; --check-inventory requires its registry id.
LEAVES = {
    "tone-check": ("CHECKS", four_tuple),
    "synthesis-sections": ("CHECKS", four_tuple),
    "severity-floor": ("CHECKS", four_tuple),
    "decision-layer-check": ("CHECKS", four_tuple),
    "author-facing-lint": ("CHECKS", four_tuple),
    "ledger-check": ("RAW_CHECKS", raw),
}
WORKER_ERRORS = ("runner_dependency_unavailable", "worker_failed", "output_limit")


class Refused(ValueError):
    pass


class CleanupFailed(Exception):
    pass


def refuse(_):
    raise Refused()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, separators=(",", ":"),
                       allow_nan=False) + "\n").encode("utf-8")


def closed_json(data):
    """Strict UTF-8 JSON without NaN/Infinity or lone surrogates."""
    try:
        value = json.loads(data.decode("utf-8"), parse_constant=refuse)
        encoded(value)  # A lone surrogate cannot be re-encoded as UTF-8.
        return value
    except (ValueError, RecursionError):
        raise Refused() from None


def unavailable(request, code):
    return {"protocol": 1, "type": "result", "id": request["id"],
            "validator": request["validator"], "available": False, "result": None,
            "error": {"code": code, "message": "Validator unavailable: %s." % code}}


def protocol_error(code):
    return {"protocol": 1, "type": "protocol_error", "id": None,
            "error": {"code": code, "message": "Protocol refused: %s." % code}}


def check_inventory():
    """Source/CI gate: every canonical AGG_VALIDATORS id has exactly one disposition."""
    try:
        value = json.loads((HERE.parent / "schemas" / "validator-runtime-inventory.json")
                           .read_text(encoding="utf-8"))
        rows = value["validators"]
        ids = [row["id"] for row in rows]
        assignments = re.findall(r"^\s*(?:export\s+)?AGG_VALIDATORS\b.*$",
                                 (HERE / "validate.sh").read_text(encoding="utf-8"), re.M)
        literal = len(assignments) == 1 and re.fullmatch(
            r"AGG_VALIDATORS=([\"'])([^\"'$`\\\n]*)\1\s*", assignments[0])
        registry = literal[2].split() if literal else []
        ok = (set(value) == {"version", "validators"} and value["version"] == 1
              and registry and len(set(registry)) == len(registry)
              and len(set(ids)) == len(ids) and set(ids) == set(registry)
              and set(LEAVES) <= set(ids)
              and all(set(row) == {"id", "desktop_disposition", "omitted_capability"}
                      and row["desktop_disposition"] in ("ci-only", "not-yet-supported")
                      and isinstance(row["omitted_capability"], str)
                      and row["omitted_capability"].strip() for row in rows))
    except (OSError, ValueError, TypeError, KeyError):
        ok = False
    if not ok:
        print("FAIL: Validator runtime inventory unavailable or inconsistent.")
        return 1
    print("PASS: Validator runtime inventory matches canonical registry (development only).")
    return 0


def request_shape(value):
    if not isinstance(value, dict) or type(value.get("protocol")) is not int:
        return "invalid_request"
    if value["protocol"] != 1:
        return "unsupported_protocol"
    kind = value.get("type")
    keys = ({"protocol", "type", "id", "validator", "text"} if kind == "validate"
            else {"protocol", "type", "id", "target"} if kind == "cancel" else set())
    if not keys or set(value) != keys:
        return "invalid_request"
    field = "validator" if kind == "validate" else "target"
    if not all(isinstance(value[k], str) and IDENTIFIER.fullmatch(value[k]) for k in ("id", field)):
        return "invalid_request"
    if kind == "validate" and not isinstance(value["text"], str):
        return "invalid_request"
    return None


def worker_environment():
    env = {"TZ": "UTC", "LC_ALL": "C", "LANG": "C", "PYTHONIOENCODING": "utf-8"}
    if os.name == "nt":
        for name in ("SystemRoot", "WINDIR"):
            if name in os.environ:
                env[name] = os.environ[name]
    return env


def worker(leaf):
    """Run one leaf on the coordinator's already bounded, LF-normalized text."""
    try:
        text = json.loads(sys.stdin.buffer.read())
        registry, formatter = LEAVES[leaf]
        sys.path.insert(0, str(HERE))
        try:
            import letter_checks
            check = getattr(letter_checks, registry)[leaf]
        except Exception:
            result = {"error": "runner_dependency_unavailable"}
        else:
            code, lines = formatter(*check(text))
            result = {"exit_code": code, "stdout": "".join(line + "\n" for line in lines),
                      "stderr": ""}
        payload = encoded(result)
        if len(payload) > RESPONSE_BYTES:
            payload = encoded({"error": "output_limit"})
    except Exception:
        payload = encoded({"error": "worker_failed"})
    os.write(sys.stdout.fileno(), payload)
    return 0


class Session:
    def __init__(self):
        self.inputs = queue.Queue(maxsize=2)  # Backpressure on stdin.
        self.events = queue.Queue()
        self.wakeup = threading.Event()
        self.active = None
        self.pending = collections.deque()  # Admitted validations, in order.
        self.eof = False
        self.terminated = False
        self.ids = set()
        self.frame = bytearray()

    def notify(self, target, event):
        target.put(event)
        self.wakeup.set()

    def read_input(self):
        try:
            while True:
                data = os.read(sys.stdin.fileno(), 4096)
                self.notify(self.inputs, ("input", None, data))
                if not data:
                    return
        except OSError:
            self.notify(self.inputs, ("input_error", None, b""))

    def emit(self, value):
        payload = encoded(value)
        if len(payload) > RESPONSE_BYTES:
            payload = encoded(unavailable(value, "output_limit"))
        view = memoryview(payload)
        while view:
            view = view[os.write(sys.stdout.fileno(), view):]

    def start(self, request):
        try:
            child = subprocess.Popen(
                [sys.executable, "-I", "-S", "-B", str(SCRIPT), "--worker", request["validator"]],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                env=worker_environment(), cwd=str(HERE), close_fds=True)
        except OSError:
            self.emit(unavailable(request, "runner_dependency_unavailable"))
            return
        active = self.active = {"request": request, "child": child, "started": time.monotonic(),
                                "stdout": bytearray(), "closed": set(), "threads": []}
        def pump(name, stream):
            try:
                while True:
                    data = os.read(stream.fileno(), 4096)
                    self.notify(self.events, (name, active, data))
                    if not data:
                        return
            except OSError:
                self.notify(self.events, ("child_error", active, b""))
        def send():
            try:
                with child.stdin:
                    child.stdin.write(encoded(request["text"]))
            except OSError:
                self.notify(self.events, ("child_error", active, b""))
        for target, args in ((pump, ("stdout", child.stdout)), (pump, ("stderr", child.stderr)),
                             (send, ())):
            thread = threading.Thread(target=target, args=args, daemon=True)
            active["threads"].append(thread)
            thread.start()

    def stop(self):
        """Kill and reap the active worker; later output from it is discarded."""
        active, self.active = self.active, None
        if active is None:
            return
        deadline = time.monotonic() + CLEANUP_SECONDS
        child = active["child"]
        try:
            child.kill()
            child.wait(timeout=CLEANUP_SECONDS)
            for thread in active["threads"]:
                thread.join(max(0, deadline - time.monotonic()))
        except (OSError, subprocess.TimeoutExpired):
            raise CleanupFailed() from None
        if any(thread.is_alive() for thread in active["threads"]):
            raise CleanupFailed()
        for stream in (child.stdin, child.stdout, child.stderr):
            stream.close()

    def finish(self, code):
        request = self.active["request"]
        self.stop()
        self.emit(unavailable(request, code))

    def end_all(self):
        if self.active:
            self.finish("session_ended")
        while self.pending:
            self.emit(unavailable(self.pending.popleft(), "session_ended"))

    def fatal(self, code):
        self.end_all()
        self.emit(protocol_error(code))
        return 2

    def cancel(self, request):
        target = request["target"]
        if self.active and self.active["request"]["id"] == target:
            victim = self.active["request"]
            self.stop()
        else:
            victim = next((r for r in self.pending if r["id"] == target), None)
            if victim:
                self.pending.remove(victim)
        if victim:
            self.emit(unavailable(victim, "cancelled"))
        self.emit({"protocol": 1, "type": "cancel_result", "id": request["id"],
                   "target": target, "cancelled": victim is not None, "error": None})

    def admit(self, data):
        try:
            if data.endswith(b"\r"):  # LF framing only.
                raise Refused()
            request = closed_json(data)
        except Refused:
            return self.fatal("invalid_frame")
        error = request_shape(request)
        if error:
            return self.fatal(error)
        if request["id"] in self.ids:
            return self.fatal("duplicate_id")
        self.ids.add(request["id"])
        if request["type"] == "cancel":
            self.cancel(request)
            return None
        # Reproduce the canonical helper's universal-newline file reading.
        text = request["text"].replace("\r\n", "\n").replace("\r", "\n")
        if request["validator"] not in LEAVES:
            self.emit(unavailable(request, "validator_unavailable"))
        elif len(request["text"].encode("utf-8")) > TEXT_BYTES or text.count("\n") >= TEXT_LINES:
            self.emit(unavailable(request, "input_limit"))
        else:
            self.pending.append(dict(request, text=text))
        return None

    def receive(self, data):
        if not data:
            if self.frame:
                return self.fatal("invalid_frame")
            self.eof = True  # Finish active and queued work, then exit 0.
            return None
        # Only LF frames: never use universal splitlines for transport.
        pieces = data.split(b"\n")
        for i, piece in enumerate(pieces):
            self.frame.extend(piece)
            if len(self.frame) > FRAME_BYTES:
                return self.fatal("invalid_frame")
            if i < len(pieces) - 1:
                record = bytes(self.frame)
                self.frame.clear()
                status = self.admit(record)
                if status is not None:
                    return status
        return None

    def child_event(self, name, active, data):
        if active is not self.active:
            return
        if name == "child_error" or (name == "stderr" and data):
            self.finish("worker_failed")
        elif data:
            active["stdout"].extend(data)
            if len(active["stdout"]) > RESPONSE_BYTES:
                self.finish("output_limit")
        else:
            active["closed"].add(name)

    def accept_result(self):
        active = self.active
        if not active or len(active["closed"]) < 2 or active["child"].poll() is None:
            return
        request = active["request"]
        try:
            if active["child"].returncode != 0:
                raise Refused()
            result = closed_json(bytes(active["stdout"]))
            if isinstance(result, dict) and set(result) == {"error"}:
                if result["error"] not in WORKER_ERRORS:
                    raise Refused()
                value = unavailable(request, result["error"])
            elif (isinstance(result, dict) and set(result) == {"exit_code", "stdout", "stderr"}
                    and type(result["exit_code"]) is int and result["exit_code"] in (0, 1)
                    and isinstance(result["stdout"], str) and result["stderr"] == ""):
                value = {"protocol": 1, "type": "result", "id": request["id"],
                         "validator": request["validator"], "available": True,
                         "result": result, "error": None}
            else:
                raise Refused()
        except Refused:
            self.finish("worker_failed")
            return
        self.stop()
        self.emit(value)

    def next_event(self):
        self.wakeup.clear()
        for source in (self.inputs, self.events):
            try:
                return source.get_nowait()
            except queue.Empty:
                pass
        self.wakeup.wait(.02)
        return None

    def run(self):
        threading.Thread(target=self.read_input, daemon=True).start()
        for sig in (signal.SIGINT, signal.SIGTERM):
            signal.signal(sig, lambda *_: setattr(self, "terminated", True))
        try:
            while True:
                if self.terminated:
                    self.end_all()
                    return 2
                if self.active and time.monotonic() - self.active["started"] >= WORK_SECONDS:
                    self.finish("timeout")
                self.accept_result()
                if not self.active and self.pending:
                    self.start(self.pending.popleft())
                    continue
                if self.eof and not self.active:
                    return 0
                event = self.next_event()
                if event is None:
                    continue
                name, active, data = event
                if name == "input_error":
                    raise OSError()
                if name != "input":
                    self.child_event(name, active, data)
                    continue
                status = self.receive(data)
                if status is not None:
                    return status
        except (CleanupFailed, OSError):
            # Broken stdout/stdin or an unreapable worker: reap if possible, exit 2.
            try:
                self.stop()
            except (CleanupFailed, OSError):
                pass
            return 2


def main():
    args = sys.argv[1:]
    if args == ["--check-inventory"]:
        return check_inventory()
    if len(args) == 2 and args[0] == "--worker" and args[1] in LEAVES:
        return worker(args[1])
    if args:
        sys.stderr.write("Unsupported validator runner usage.\n")
        return 2
    return Session().run()


if __name__ == "__main__":
    raise SystemExit(main())
