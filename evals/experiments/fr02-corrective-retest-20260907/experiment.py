"""Frozen, local FR-02 experiment. Stdlib only; no key file is read here."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import random
import re
import shutil
import subprocess
import sys
import time

SOURCE_PIN = "20b8ca6219e649b2743866b9ffaba0e77ab208a5"
FAMILIES = ("continuity-contradiction", "pov-break", "orphan-scene", "unpaid-setup")
MODELS = ("gpt-6-astra", "gpt-5.6-terra")
CORRECTIVE = """Before asserting a continuity contradiction, identify the manuscript commitments,
their textual loci, referents, and relevant story times. Separate explicit facts
and necessary calculations from plausible but unstated assumptions. Require an
asserted contradiction to survive removing those assumptions. A consistent
assignment compatible with the stated text defeats an impossibility claim;
invented events or unestablished narrator unreliability cannot rescue an explicit
collision. Preserve contradictions established by explicit facts or necessary
calculation. Leave any choice of canon or repair to the author."""
DISABLED = ("shell_tool", "apps", "plugins", "skill_search", "multi_agent",
            "browser_use", "computer_use", "image_generation", "memories",
            "hooks", "remote_plugin", "workspace_dependencies", "in_app_browser", "goals")


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path, value):
    data = (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    temp = path.with_name(path.name + ".tmp")
    temp.write_bytes(data)
    temp.replace(path)


def tracked_bytes(repo, relative):
    return subprocess.check_output(["git", "-C", str(repo), "show", f"{SOURCE_PIN}:{relative}"])


def packet_bytes(header, body, arm):
    addition = b"" if arm == "baseline" else CORRECTIVE.encode("utf-8") + b"\n\n"
    return header + b"\n\n" + addition + b"<submission>\n" + body.rstrip(b"\n") + b"\n</submission>\n"


def create_plan():
    rows = [{"family": f, "member": member, "arm": arm, "model": model, "repeat": repeat}
            for f in FAMILIES for member in ("clean", "broken")
            for arm in ("baseline", "corrective") for model in MODELS for repeat in (1, 2)]
    random.Random(20260907).shuffle(rows)
    for index, row in enumerate(rows, 1):
        row["id"] = f"r{index:03d}"
    return rows


def freeze(repo, root, codex):
    if root.exists():
        raise ValueError("Freeze requires a new result directory; existing evidence is never overwritten")
    source = "evals/fixtures/fiction-benchmark/"
    script = tracked_bytes(repo, source + "run.sh").replace(b"\r\n", b"\n")
    match = re.search(rb"read -r -d '' HEADER <<'EOF'\n(.*?)\nEOF", script, re.S)
    if not match:
        raise ValueError("Pinned runner HEADER not found")
    header = match[1]
    sources = tracked_bytes(repo, source + "SOURCES.md").decode("utf-8")
    hashes = dict(re.findall(r"^### ([\w-]+).*?\*\*RECORDED:\*\* sha256: ([0-9a-f]{64})", sources, re.M | re.S))
    artifacts = {}
    artifacts["frozen/baseline-header.txt"] = header
    artifacts["frozen/corrective.txt"] = CORRECTIVE.encode("utf-8")
    artifacts["frozen/PROTOCOL.md"] = Path(__file__).with_name("PROTOCOL.md").read_bytes()
    artifacts["frozen/experiment.py"] = Path(__file__).read_bytes()
    for f in FAMILIES:
        for member in ("clean", "broken"):
            body = tracked_bytes(repo, source + f"{f}/{member}/fixture.md").replace(b"\r\n", b"\n")
            body = body.rstrip(b"\n") + b"\n"
            expected = hashes[f"{f}-{member}"]
            if digest(body) != expected:
                raise ValueError(f"Pinned fixture hash mismatch: {f}-{member}")
            for arm in ("baseline", "corrective"):
                artifacts[f"prompts/{f}-{member}-{arm}.txt"] = packet_bytes(header, body, arm)
    plan = create_plan()
    for row in plan:
        row["prompt"] = f"prompts/{row['family']}-{row['member']}-{row['arm']}.txt"
        row["prompt_sha256"] = digest(artifacts[row["prompt"]])
    version = subprocess.check_output([codex, "--version"], text=True).strip()
    root.mkdir(parents=True)
    for name, data in artifacts.items():
        dest = root / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
    manifest = {"schema": "fr02-freeze/1", "created_utc": now(), "source_pin": SOURCE_PIN,
                "cli_version": version, "cli": str(Path(codex).resolve()),
                "artifacts": {p: digest(b) for p, b in artifacts.items()}, "runs": plan,
                "settings": {"effort": "high", "disabled_features": list(DISABLED),
                             "max_tokens": None, "max_tokens_reason": "CLI exposes no output token cap",
                             "launch_deadline_utc": "2026-09-08T01:00:00+00:00", "workers": 2}}
    write_json(root / "manifest.json", manifest)
    write_json(root / "preregistration.json", {"frozen_utc": now(), "planned_runs": len(plan),
               "manifest_sha256": digest((root / "manifest.json").read_bytes()),
               "protocol_sha256": manifest["artifacts"]["frozen/PROTOCOL.md"]})
    print(json.dumps({"frozen": str(root), "runs": len(plan), "manifest_sha256": digest((root / "manifest.json").read_bytes())}))


def verify_freeze(root):
    registration = read_json(root / "preregistration.json")
    if digest((root / "manifest.json").read_bytes()) != registration["manifest_sha256"]:
        raise ValueError("Manifest changed after preregistration")
    manifest = read_json(root / "manifest.json")
    for name, expected in manifest["artifacts"].items():
        if digest((root / name).read_bytes()) != expected:
            raise ValueError(f"Frozen artifact changed: {name}")
    if len(manifest["runs"]) != 64 or len({r["id"] for r in manifest["runs"]}) != 64:
        raise ValueError("Invalid production population")
    return manifest


def command(codex, model, output):
    args = [codex, "exec", "--model", model, "--ephemeral", "--ignore-user-config",
            "--sandbox", "read-only", "--skip-git-repo-check", "--json", "--color", "never",
            "-c", 'model_reasoning_effort="high"', "-c", "project_doc_max_bytes=0",
            "-c", 'web_search="disabled"', "-o", str(output)]
    for feature in DISABLED:
        args.extend(["--disable", feature])
    return args + ["-"]


def inspect_events(path):
    events, usage, tools, invalid = [], None, [], 0
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            invalid += 1
            continue
        events.append(item)
        if item.get("type") == "turn.completed":
            usage = item.get("usage")
        kind = item.get("item", {}).get("type")
        if kind and kind not in ("agent_message", "reasoning", "error"):
            tools.append(kind)
    return {"usage": usage, "tool_events": tools, "invalid_event_lines": invalid,
            "turn_completed": any(e.get("type") == "turn.completed" for e in events),
            "thread_id": next((e.get("thread_id") for e in events if e.get("type") == "thread.started"), None)}


def verified_completion(folder):
    receipt = folder / "receipt.json"
    if not receipt.exists():
        return None
    data = read_json(receipt)
    for filename, expected in data["hashes"].items():
        if digest((folder / filename).read_bytes()) != expected:
            raise ValueError(f"Completion artifact changed: {folder.name}/{filename}")
    return data


def process_alive(pid):
    if sys.platform == "win32":
        import ctypes
        from ctypes import wintypes
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        kernel.OpenProcess.restype = wintypes.HANDLE
        kernel.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
        kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        handle = kernel.OpenProcess(0x1000, False, pid)
        if not handle:
            return ctypes.get_last_error() != 87
        try:
            code = wintypes.DWORD()
            return not kernel.GetExitCodeProcess(handle, ctypes.byref(code)) or code.value == 259
        finally:
            kernel.CloseHandle(handle)
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def selected_folder(root, row):
    base = root / "outputs" / row["id"]
    retry = base / "retry-1"
    return retry if retry.exists() else base


def recover(root, run_id):
    manifest = verify_freeze(root)
    row = next(r for r in manifest["runs"] if r["id"] == run_id)
    lock = root / "run.lock"
    if lock.exists() and process_alive(read_json(lock)["pid"]):
        raise ValueError("Recorded controller is live; do not recover or relaunch")
    folder = selected_folder(root, row)
    if verified_completion(folder):
        raise ValueError("Receipt already sealed; recovery cannot overwrite it")
    started = read_json(folder / "started.json")
    process = read_json(folder / "process.json") if (folder / "process.json").exists() else None
    if process_alive(started["parent_pid"]) or (process and process_alive(process["pid"])):
        raise ValueError("Recorded invocation process is live; observation timeout is not termination")
    files = [p for p in folder.iterdir() if p.is_file()]
    receipt = {"schema": "fr02-completion/1", "id": run_id, "status": "interrupted",
               "started_utc": started["started_utc"], "ended_utc": now(), "return_code": None,
               "requested_model": row["model"], "prompt_sha256": row["prompt_sha256"],
               "reason": "Recorded parent and child handles are absent or terminal; no output correctness inference",
               "hashes": {p.name: digest(p.read_bytes()) for p in files}}
    write_json(folder / "receipt.json", receipt)
    if lock.exists():
        lock.replace(root / ("stale-lock-" + run_id + ".json"))
    print(json.dumps({"recovered": run_id, "status": "interrupted"}))


def execute_one(root, manifest, row, retry=False):
    destination = selected_folder(root, row)
    prior = verified_completion(destination)
    if prior and retry:
        if prior["status"] not in ("failed", "interrupted") or destination.name == "retry-1":
            raise ValueError("Only one transport/interruption retry is allowed; no answer-quality retries")
        destination = destination / "retry-1"
        prior = None
    if prior:
        if prior["prompt_sha256"] != row["prompt_sha256"] or prior["requested_model"] != row["model"]:
            raise ValueError("Completed row identity no longer matches manifest")
        return {"id": row["id"], "status": prior["status"], "resumed": True}
    if destination.exists():
        raise ValueError(f"Unsealed attempt exists for {row['id']}; inspect its live process before recovery")
    deadline = datetime.fromisoformat(manifest["settings"]["launch_deadline_utc"])
    if datetime.now(timezone.utc) >= deadline:
        return {"id": row["id"], "status": "not_launched_deadline"}
    destination.mkdir(parents=True)
    neutral = destination / "neutral"
    neutral.mkdir()
    output = destination / "output.txt"
    args = command(manifest["cli"], row["model"], output)
    prompt = (root / row["prompt"]).read_bytes()
    if digest(prompt) != row["prompt_sha256"]:
        raise ValueError("Prompt changed immediately before dispatch")
    env = os.environ.copy()
    for key in ("OPENAI_API_KEY", "CODEX_API_KEY", "ANTHROPIC_API_KEY"):
        env.pop(key, None)
    start = now()
    clock_start = time.monotonic()
    write_json(destination / "started.json", {"started_utc": start, "requested_model": row["model"],
                "prompt_sha256": row["prompt_sha256"], "command": args, "parent_pid": os.getpid()})
    with (destination / "events.jsonl").open("wb") as events, (destination / "stderr.txt").open("wb") as errors:
        child = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=events, stderr=errors, cwd=neutral,
                                 env=env, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        write_json(destination / "process.json", {"pid": child.pid, "started_utc": now()})
        child.communicate(prompt)
    observed = inspect_events(destination / "events.jsonl")
    nonempty = output.exists() and bool(output.read_bytes().strip())
    status = "complete" if child.returncode == 0 and nonempty and observed["turn_completed"] else "failed"
    if observed["tool_events"] or observed["invalid_event_lines"]:
        status = "contaminated"
    files = ["started.json", "process.json", "events.jsonl", "stderr.txt"]
    if output.exists():
        files.append("output.txt")
    receipt = {"schema": "fr02-completion/1", "id": row["id"], "status": status,
               "started_utc": start, "ended_utc": now(), "elapsed_seconds": time.monotonic() - clock_start,
               "return_code": child.returncode, "requested_model": row["model"],
               "served_model": None, "served_model_reason": "Not exposed by CLI event schema",
               "prompt_sha256": row["prompt_sha256"], **observed,
               "cost_usd": None, "cost_reason": "Subscription invocation; no per-call invoice",
               "hashes": {n: digest((destination / n).read_bytes()) for n in files}}
    write_json(destination / "receipt.json", receipt)
    return {"id": row["id"], "status": status, "seconds": round(receipt["elapsed_seconds"])}


def run(root, limit=None, retry_row=None):
    manifest = verify_freeze(root)
    current_version = subprocess.check_output([manifest["cli"], "--version"], text=True).strip()
    if current_version != manifest["cli_version"]:
        raise ValueError("CLI version changed after freeze")
    rows = [r for r in manifest["runs"] if r["id"] == retry_row] if retry_row else manifest["runs"][:limit] if limit else manifest["runs"]
    if not rows:
        raise ValueError("No matching planned runs")
    lock = root / "run.lock"
    # A stale lock is evidence to inspect, never authority to restart a live process.
    with lock.open("x", encoding="utf-8") as handle:
        json.dump({"pid": os.getpid(), "started_utc": now()}, handle)
    try:
        todo = iter(rows)
        stopped = False
        with ThreadPoolExecutor(max_workers=2) as pool:
            active = {}
            for row in list(next(todo, None) for _ in range(2)):
                if row is not None:
                    active[pool.submit(execute_one, root, manifest, row, bool(retry_row))] = row["id"]
            while active:
                finished, _ = wait(active, return_when=FIRST_COMPLETED)
                for future in finished:
                    active.pop(future)
                    result = future.result()
                    print(json.dumps(result), flush=True)
                    if result["status"] not in ("complete",):
                        stopped = True
                if not stopped:
                    for _ in range(2 - len(active)):
                        row = next(todo, None)
                        if row is not None:
                            active[pool.submit(execute_one, root, manifest, row, bool(retry_row))] = row["id"]
        if stopped:
            raise RuntimeError("Dispatch stopped after non-completion; inspect retained receipts")
    finally:
        lock.unlink()


def status(root):
    manifest = verify_freeze(root)
    counts = {}
    active = []
    for row in manifest["runs"]:
        folder = selected_folder(root, row)
        receipt = verified_completion(folder)
        state = receipt["status"] if receipt else "unsealed" if folder.exists() else "pending"
        counts[state] = counts.get(state, 0) + 1
        if state == "unsealed":
            active.append({"id": row["id"], "process": read_json(folder / "process.json") if (folder / "process.json").exists() else None})
    print(json.dumps({"planned": len(manifest["runs"]), "counts": counts, "unsealed": active}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("freeze", "verify", "run", "status", "recover"))
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--repo", type=Path)
    parser.add_argument("--codex", default=shutil.which("codex.cmd") or shutil.which("codex"))
    parser.add_argument("--limit", type=int)
    parser.add_argument("--row", help="Required for recover; with run, one permitted failed transport retry")
    args = parser.parse_args()
    if args.action == "freeze":
        if not args.repo or not args.codex:
            parser.error("freeze needs --repo and a Codex executable")
        freeze(args.repo.resolve(), args.root.resolve(), args.codex)
    elif args.action == "run":
        run(args.root.resolve(), args.limit, args.row)
    elif args.action == "recover":
        if not args.row:
            parser.error("recover requires --row")
        recover(args.root.resolve(), args.row)
    elif args.action == "status":
        status(args.root.resolve())
    else:
        manifest = verify_freeze(args.root.resolve())
        print(json.dumps({"verified": len(manifest["runs"])}))


if __name__ == "__main__":
    main()
