#!/usr/bin/env python3
"""Bounded development JSONL adapter for the fixed tone and synthesis leaves (stdlib only).

Invoke with a supplied interpreter: python -I -S validator_runner.py.
This source tool supplies neither a desktop interpreter nor a native sandbox.
"""
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
SESSION_FRAMES = 64
SESSION_BYTES = 16777216
SESSION_SECONDS = 600
IDLE_SECONDS = 60
CLEANUP_SECONDS = 2
METADATA_BYTES = 65536
HERE = Path(__file__).resolve().parent
IDENTIFIER = re.compile(r"[A-Za-z0-9_-]{1,64}\Z")


class Refused(ValueError):
    pass


def closed_json(data):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise Refused()
            result[key] = value
        return result

    def constant(_):
        raise Refused()

    def inspect(value, depth=0):
        if isinstance(value, (dict, list)):
            depth += 1
            if depth > 8:
                raise Refused()
            for item in (list(value.keys()) + list(value.values())
                         if isinstance(value, dict) else value):
                inspect(item, depth)
        elif isinstance(value, str) and any(0xD800 <= ord(c) <= 0xDFFF for c in value):
            raise Refused()

    try:
        if data.startswith(b"\xef\xbb\xbf"):
            raise Refused()
        value = json.loads(data.decode("utf-8", "strict"), object_pairs_hook=pairs,
                           parse_constant=constant)
        inspect(value)
        return value
    except (ValueError, UnicodeError, RecursionError, OverflowError):
        raise Refused() from None


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, separators=(",", ":"),
                       allow_nan=False) + "\n").encode("utf-8")


def unavailable(request, code):
    return {"protocol": 1, "type": "result", "id": request["id"],
            "validator": request["validator"], "available": False,
            "result": None, "error": {"code": code,
            "message": "Validator unavailable: %s." % code}}


def protocol_error(code):
    return {"protocol": 1, "type": "protocol_error", "id": None,
            "error": {"code": code, "message": "Protocol refused: %s." % code}}


def bounded_file(path, limit):
    with path.open("rb") as source:
        data = source.read(limit + 1)
    if len(data) > limit:
        raise Refused()
    return data


def inventory():
    value = closed_json(bounded_file(HERE.parent / "schemas" /
                                    "validator-runtime-inventory.json", METADATA_BYTES))
    if (not isinstance(value, dict) or set(value) != {"version", "validators"}
            or type(value["version"]) is not int or value["version"] != 1
            or not isinstance(value["validators"], list)
            or not 1 <= len(value["validators"]) <= 512):
        raise Refused()
    rows = {}
    for row in value["validators"]:
        if (not isinstance(row, dict) or set(row) != {"id", "desktop_disposition",
                "development_support", "omitted_capability"}
                or not isinstance(row["id"], str) or not IDENTIFIER.fullmatch(row["id"])
                or row["id"] in rows
                or row["desktop_disposition"] not in ("ci-only", "not-yet-supported")
                or row["development_support"] not in ("none", "tone-check-v1", "synthesis-sections-v1")
                or not isinstance(row["omitted_capability"], str)
                or not 1 <= len(row["omitted_capability"]) <= 256
                or not row["omitted_capability"].strip()
                or (row["development_support"] == "tone-check-v1" and row["id"] != "tone-check")
                or (row["development_support"] == "synthesis-sections-v1" and row["id"] != "synthesis-sections")):
            raise Refused()
        rows[row["id"]] = row
    for leaf, support in (("tone-check", "tone-check-v1"),
                          ("synthesis-sections", "synthesis-sections-v1")):
        if (leaf not in rows or rows[leaf]["development_support"] != support
                or rows[leaf]["desktop_disposition"] != "not-yet-supported"):
            raise Refused()
    return rows


def check_inventory():
    try:
        rows = inventory()
        registry = bounded_file(HERE / "validate.sh", METADATA_BYTES * 4).decode("utf-8")
        assignments = [line for line in registry.splitlines()
                       if re.match(r"^\s*(?:export\s+)?AGG_VALIDATORS\b", line)]
        if len(assignments) != 1:
            raise Refused()
        literal = re.fullmatch(r"AGG_VALIDATORS=([\"'])([^\"'$`\\\n]*)\1\s*", assignments[0])
        if not literal:
            raise Refused()
        ids = literal[2].split()
        if (not ids or len(ids) != len(set(ids)) or set(ids) != set(rows)
                or any(not IDENTIFIER.fullmatch(x) for x in ids)):
            raise Refused()
    except (OSError, Refused, UnicodeError, TypeError):
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
    if not isinstance(value["id"], str) or not IDENTIFIER.fullmatch(value["id"]):
        return "invalid_request"
    field = "validator" if kind == "validate" else "target"
    if not isinstance(value[field], str) or not IDENTIFIER.fullmatch(value[field]):
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


def worker_main(synthesis=False):
    # Install the denial before importing the trusted leaf, with no configurable path.
    def deny(event, _):
        if (event.startswith("socket.") or event in ("subprocess.Popen", "os.system",
                "os.fork", "os.forkpty", "os.posix_spawn", "os.exec")):
            raise PermissionError("Development leaf operation refused.")
    sys.addaudithook(deny)
    sys.dont_write_bytecode = True
    try:
        data = sys.stdin.buffer.read(FRAME_BYTES + 1)
        text = closed_json(data)
        if not isinstance(text, str) or len(text.encode("utf-8")) > TEXT_BYTES:
            raise Refused()
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        if text.count("\n") + 1 > TEXT_LINES:
            raise Refused()
        sys.path.insert(0, str(HERE))
        try:
            if synthesis:
                from letter_checks import synthesis_sections as check
            else:
                from letter_checks import tone_check as check
        except Exception:
            result = {"error": "runner_dependency_unavailable"}
        else:
            value = check(text)
            if (not isinstance(value, tuple) or len(value) != 4
                    or not all(isinstance(x, list) for x in value[:2])
                    or not all(isinstance(x, str) for group in value[:2] for x in group)
                    or not all(isinstance(x, str) for x in value[2:])):
                raise Refused()
            errors, warnings, ok, failed = value
            stdout = "".join(x + "\n" for x in warnings + errors)
            stdout += ("\n" + failed if errors else ok) + "\n"
            result = {"exit_code": int(bool(errors)), "stdout": stdout, "stderr": ""}
        payload = encoded(result)
        if len(payload) > RESPONSE_BYTES:
            payload = encoded({"error": "output_limit"})
    except Exception:
        payload = encoded({"error": "worker_failed"})
    os.write(sys.stdout.fileno(), payload)
    return 0


class TransportFailure(Exception):
    def __init__(self, deadline=None):
        self.deadline = deadline


def failure_diagnostic(deadline):
    # Inherited stderr can be full too: diagnostics never extend shutdown.
    if time.monotonic() >= deadline:
        return
    done = threading.Event()
    def write():
        try:
            os.write(sys.stderr.fileno(), b"Validator runner transport or cleanup failed.\n")
        except OSError:
            pass
        finally:
            done.set()
    threading.Thread(target=write, daemon=True).start()
    done.wait(max(0, deadline - time.monotonic()))


class Session:
    def __init__(self):
        self.events = queue.Queue(maxsize=8)
        self.inputs = queue.Queue(maxsize=2)
        self.wakeup = threading.Event()
        self.active = None
        self.ids = set()
        self.frame = bytearray()
        self.frames = self.bytes = 0
        self.started = self.last_input = time.monotonic()
        self.termination = None
        try:
            inventory()
            self.dependency = True
        except (OSError, Refused, TypeError, UnicodeError):
            self.dependency = False

    def terminate(self, *_):
        if self.termination is None:
            self.termination = time.monotonic()

    def input_reader(self):
        try:
            while True:
                data = os.read(sys.stdin.fileno(), 4096)
                self.inputs.put(("input", None, data, time.monotonic()))
                self.wakeup.set()
                if not data:
                    return
        except OSError:
            self.inputs.put(("input_error", None, b"", time.monotonic()))
            self.wakeup.set()

    def emit(self, value, deadline=None):
        deadline = time.monotonic() + CLEANUP_SECONDS if deadline is None else deadline
        payload = encoded(value)
        if len(payload) > RESPONSE_BYTES:
            if value["type"] != "result":
                raise TransportFailure(deadline)
            payload = encoded(unavailable(value, "output_limit"))
        # Reserve part of this same budget to kill/reap an active worker if
        # output fails. Waiting until the absolute deadline would leave no reap time.
        write_deadline = deadline - .25 if self.active else deadline
        done = threading.Event()
        failures = []
        def write():
            try:
                view = memoryview(payload)
                while view:
                    n = os.write(sys.stdout.fileno(), view)
                    if n <= 0:
                        raise OSError()
                    view = view[n:]
            except OSError:
                failures.append(True)
            finally:
                done.set()
        threading.Thread(target=write, daemon=True).start()
        while not done.wait(min(.02, max(0, write_deadline - time.monotonic()))):
            if time.monotonic() >= write_deadline or self.termination is not None:
                raise TransportFailure(deadline)
        if failures:
            raise TransportFailure(deadline)

    def start(self, request):
        started = time.monotonic()
        route = "--worker-synthesis-sections" if request["validator"] == "synthesis-sections" else "--worker"
        try:
            child = subprocess.Popen([sys.executable, "-I", "-S", "-B", str(HERE / "validator_runner.py"), route],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                env=worker_environment(), cwd=str(HERE), close_fds=True)
        except OSError:
            self.emit(unavailable(request, "runner_dependency_unavailable"))
            return
        active = {"request": request, "child": child, "started": started,
                  "stdout": bytearray(), "closed": set(), "threads": []}
        self.active = active
        def read(name, stream):
            try:
                while True:
                    data = os.read(stream.fileno(), 1024)
                    self.events.put((name, active, data, None))
                    self.wakeup.set()
                    if not data:
                        return
            except OSError:
                self.events.put(("child_error", active, b"", None))
                self.wakeup.set()
        def write():
            try:
                payload = encoded(request["text"])
                view = memoryview(payload)
                while view:
                    n = os.write(child.stdin.fileno(), view)
                    if n <= 0:
                        raise OSError()
                    view = view[n:]
            except OSError:
                self.events.put(("child_error", active, b"", None))
                self.wakeup.set()
            finally:
                child.stdin.close()
        for name, stream in (("stdout", child.stdout), ("stderr", child.stderr)):
            thread = threading.Thread(target=read, args=(name, stream), daemon=True)
            active["threads"].append(thread)
            thread.start()
        thread = threading.Thread(target=write, daemon=True)
        active["threads"].append(thread)
        thread.start()

    def stop(self, deadline):
        active = self.active
        if active is None:
            return
        self.active = None  # Any queued output is now stale and must be discarded.
        try:
            child = active["child"]
            if child.poll() is None:
                child.terminate()
                try:
                    child.wait(timeout=min(.1, max(0, deadline - time.monotonic())))
                except subprocess.TimeoutExpired:
                    child.kill()
            try:
                child.wait(timeout=max(0, deadline - time.monotonic()))
            except subprocess.TimeoutExpired:
                raise TransportFailure(deadline) from None
            # Readers can be blocked putting stale bounded events; drain until joined.
            while any(t.is_alive() for t in active["threads"]):
                if time.monotonic() >= deadline:
                    raise TransportFailure(deadline)
                try:
                    self.events.get(timeout=.01)
                except queue.Empty:
                    pass
            for stream in (child.stdin, child.stdout, child.stderr):
                stream.close()
        except OSError:
            raise TransportFailure(deadline) from None

    def finish(self, code):
        request = self.active["request"]
        deadline = time.monotonic() + CLEANUP_SECONDS
        self.stop(deadline)
        self.emit(unavailable(request, code), deadline)

    def fatal(self, code):
        deadline = time.monotonic() + CLEANUP_SECONDS
        if self.active:
            request = self.active["request"]
            self.stop(deadline)
            self.emit(unavailable(request, "session_ended"), deadline)
        self.emit(protocol_error(code), deadline)
        return 2

    def admit(self, data):
        self.frames += 1
        if self.frames > SESSION_FRAMES:
            return self.fatal("session_limit")
        if data.endswith(b"\r"):
            return self.fatal("invalid_frame")
        try:
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
            cancelled = bool(self.active and self.active["request"]["id"] == request["target"])
            deadline = time.monotonic() + CLEANUP_SECONDS
            if cancelled:
                target = self.active["request"]
                self.stop(deadline)
                self.emit(unavailable(target, "cancelled"), deadline)
            self.emit({"protocol": 1, "type": "cancel_result", "id": request["id"],
                       "target": request["target"], "cancelled": cancelled, "error": None}, deadline)
        elif request["validator"] not in ("tone-check", "synthesis-sections"):
            self.emit(unavailable(request, "validator_unavailable"))
        elif (len(request["text"].encode("utf-8")) > TEXT_BYTES
              or request["text"].replace("\r\n", "\n").replace("\r", "\n").count("\n") + 1 > TEXT_LINES):
            self.emit(unavailable(request, "input_limit"))
        elif self.active:
            self.emit(unavailable(request, "busy"))
        elif not self.dependency:
            self.emit(unavailable(request, "runner_dependency_unavailable"))
        else:
            self.start(request)
        return None

    def child_event(self, event):
        name, active, data, _ = event
        if active is not self.active:
            return
        if name == "child_error" or (name == "stderr" and data):
            self.finish("worker_failed")
            return
        if name == "stdout" and data:
            active["stdout"].extend(data)
            if len(active["stdout"]) > RESPONSE_BYTES:
                self.finish("output_limit")
            return
        if not data:
            active["closed"].add(name)

    def accept_result(self):
        active = self.active
        if not active or active["closed"] != {"stdout", "stderr"} or active["child"].poll() is None:
            return
        try:
            if active["child"].returncode != 0:
                raise Refused()
            data = active["stdout"]
            if not data.endswith(b"\n") or b"\n" in data[:-1]:
                raise Refused()
            result = closed_json(bytes(data[:-1]))
            if isinstance(result, dict) and set(result) == {"error"}:
                if result["error"] not in ("runner_dependency_unavailable", "worker_failed", "output_limit"):
                    raise Refused()
                value = unavailable(active["request"], result["error"])
            elif (isinstance(result, dict) and set(result) == {"exit_code", "stdout", "stderr"}
                    and type(result["exit_code"]) is int and result["exit_code"] in (0, 1)
                    and isinstance(result["stdout"], str) and result["stderr"] == ""):
                value = {"protocol": 1, "type": "result", "id": active["request"]["id"],
                         "validator": active["request"]["validator"], "available": True, "result": result, "error": None}
            else:
                raise Refused()
        except (Refused, TypeError):
            self.finish("worker_failed")
            return
        deadline = time.monotonic() + CLEANUP_SECONDS
        self.stop(deadline)
        self.emit(value, deadline)

    def run(self):
        threading.Thread(target=self.input_reader, daemon=True).start()
        for sig in (signal.SIGINT, signal.SIGTERM):
            signal.signal(sig, self.terminate)
        try:
            while True:
                now = time.monotonic()
                if self.termination is not None:
                    deadline = self.termination + CLEANUP_SECONDS
                    if self.active:
                        request = self.active["request"]
                        self.stop(deadline)
                        self.emit(unavailable(request, "session_ended"), deadline)
                    return 2
                if now - self.started >= SESSION_SECONDS or now - self.last_input >= IDLE_SECONDS:
                    return self.fatal("session_limit")
                if self.active and now - self.active["started"] >= WORK_SECONDS:
                    self.finish("timeout")
                self.accept_result()
                self.wakeup.clear()
                try:
                    try:
                        event = self.inputs.get_nowait()
                    except queue.Empty:
                        event = self.events.get_nowait()
                except queue.Empty:
                    self.wakeup.wait(.02)
                    continue
                name, _, data, timestamp = event
                if name == "input_error":
                    raise TransportFailure()
                if name != "input":
                    self.child_event(event)
                    continue
                if not data:
                    if self.frame:
                        return self.fatal("invalid_frame")
                    if self.active:
                        self.finish("session_ended")
                    return 0
                self.last_input = timestamp
                remaining = SESSION_BYTES - self.bytes
                prefix = data[:remaining]
                self.bytes += len(prefix)
                # Only LF frames: never use universal splitlines for transport.
                pieces = prefix.split(b"\n")
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
                if len(prefix) < len(data):
                    return self.fatal("session_limit")
        except (TransportFailure, BrokenPipeError, OSError) as exc:
            deadline = getattr(exc, "deadline", None)
            if deadline is None:
                deadline = time.monotonic() + CLEANUP_SECONDS
            if self.termination is not None:
                deadline = min(deadline, self.termination + CLEANUP_SECONDS)
            try:
                self.stop(deadline)
            except (TransportFailure, OSError):
                pass
            failure_diagnostic(deadline)
            return 2


def main():
    sys.dont_write_bytecode = True
    if not sys.flags.isolated or not sys.flags.no_site:
        sys.stderr.write("Use an isolated no-site development interpreter (-I -S).\n")
        return 2
    if sys.argv[1:] == ["--check-inventory"]:
        return check_inventory()
    if sys.argv[1:] == ["--worker"]:
        return worker_main()
    if sys.argv[1:] == ["--worker-synthesis-sections"]:
        return worker_main(synthesis=True)
    if sys.argv[1:]:
        sys.stderr.write("Unsupported validator runner usage.\n")
        return 2
    return Session().run()


if __name__ == "__main__":
    raise SystemExit(main())
