#!/usr/bin/env python3
"""Offline Claude CLI protocol fixture. It never imports a provider or uses a key."""
import json
import os
from pathlib import Path
import sys


def event(value):
    sys.stdout.buffer.write((json.dumps(value, ensure_ascii=False) + "\n").encode("utf-8"))


def main():
    # The runner copies this invented fixture under a case name. This changes
    # synthetic behavior without forwarding any fixture settings into the child.
    mode = Path(__file__).stem
    if sys.argv[-1] == "--version":
        print("2.1.285 (Claude Code)" if mode == "old" else "2.1.288 (Claude Code)")
        return
    flags = ("--bare --tools --disallowedTools --strict-mcp-config --setting-sources "
             "--disable-slash-commands --no-session-persistence --system-prompt "
             "--output-format --no-chrome")
    if sys.argv[-1] == "--help":
        print(flags.replace("--bare", "") if mode == "unsupported" else flags)
        return
    Path(__file__).with_suffix(".invoked").write_text("synthetic drafting was invoked", encoding="utf-8")
    raw = sys.stdin.buffer.read()
    captured = {"argv": sys.argv[1:], "stdin": raw.decode("utf-8"),
                "environment": dict(os.environ), "cwd": os.getcwd(),
                "cwd_files": sorted(path.name for path in Path.cwd().iterdir())}
    initialization = {"type": "system", "subtype": "init", "tools": [], "mcp_servers": [], "plugins": [], "skills": []}
    if mode == "leaky":
        initialization["tools"] = ["Read"]
    if mode != "missinginit":
        event(initialization)
    if mode == "hook":
        event({"type": "system", "subtype": "hook_started"})
    if mode == "tool":
        event({"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Read"}]}})
    if mode == "delegate":
        event({"type": "assistant", "parent_tool_use_id": "synthetic-delegation", "message": {"content": []}})
    draft = json.dumps(captured, ensure_ascii=False)
    passage_map = "### Passage p-1\nSpan: paragraphs 1\u20131\nKind: DE-MINIMIS\n"
    if mode == "draft":
        packet = json.loads(raw)
        nodes = packet["nodes"]
        draft = "\n\n".join(node["Text"] for node in nodes)
        passage_map = "\n".join(
            f"### Passage p-{number}\nSpan: paragraphs {number}\u2013{number}\nKind: MAPPED\nRealizes: {node['ID']}\n"
            for number, node in enumerate(nodes, 1))
    response = json.dumps({"draft": draft, "passage_map": passage_map}, ensure_ascii=False)
    if mode == "duplicates":
        response = '{"draft":"Invented prose.","draft":"Other invented prose.","passage_map":"map"}'
    elif mode == "surrogate":
        response = '{"draft":"\\ud800","passage_map":"map"}'
    elif mode == "extra":
        response = '{"draft":"Invented prose.","passage_map":"map","receipt":"PASS"}'
    elif mode == "markdown":
        response = "```json\n" + response + "\n```"
    elif mode == "wrongtype":
        response = '{"draft":[],"passage_map":"map"}'
    elif mode == "nonfinite":
        response = '{"draft":NaN,"passage_map":"map"}'
    if mode == "duplicateinit":
        event(initialization)
    result = {"type": "result", "subtype": "success", "is_error": False, "result": response}
    if mode == "apierror":
        result.update(subtype="error_during_execution", is_error=True)
    event(result)
    if mode == "twice":
        event(result)


if __name__ == "__main__":
    main()
