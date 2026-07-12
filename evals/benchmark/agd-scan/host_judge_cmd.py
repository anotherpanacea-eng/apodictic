#!/usr/bin/env python3
"""host_judge_cmd.py — SETEC_HOST_JUDGE_CMD transport for the R3B AGD-scan benchmark.

The producer's `agent_host` judge backend (setec-voiceprint `judge_backends.py`,
spec 35) pipes a request JSON to this command's stdin — ``{"system", "content",
"response_format", "no_verdict"}`` — and reads the model's JSON text from stdout.
This wrapper runs the vendor CLI named by ``$JUDGE_VENDOR`` in a FRESH process:
the blind-runner discipline (the judge sees only the producer's rendered prompt +
numbered passage, never the fixture's §10.9 keys) is what a fresh subprocess buys.

Vendors (the R3B §4 pinning):
  JUDGE_VENDOR=fable  ->  claude -p --model claude-fable-5           (Claude Code CLI)
  JUDGE_VENDOR=codex  ->  codex exec -m gpt-5.6-sol
                          -c model_reasoning_effort="xhigh"          (Codex CLI, Sol extra-high)

Used via (see acquire.py):
  SETEC_HOST_JUDGE_CMD="python3 evals/benchmark/agd-scan/host_judge_cmd.py"
  SETEC_HOST_JUDGE_TIMEOUT=900
"""
import json
import os
import subprocess
import sys
import tempfile

SUBPROC_TIMEOUT = 840  # < SETEC_HOST_JUDGE_TIMEOUT=900, so this layer times out first


def main() -> int:
    req = json.load(sys.stdin)
    prompt = "%s\n\n%s\n\n%s" % (
        req.get("system", ""), req.get("no_verdict", ""), req.get("content", ""))
    vendor = os.environ.get("JUDGE_VENDOR", "")
    if vendor == "fable":
        # --tools "" disables ALL built-in tools: the judge works from the
        # prompt alone (mechanical blindness, not just an instruction). NOTE:
        # `claude` refuses to launch NESTED inside a running Claude Code
        # session — the committed 2026-07-12 manifests therefore used the
        # host's subagent adapter instead (fresh no-tools-instructed subagents;
        # 0 tool uses observed per rep — see acquisition-log.md + README).
        # This branch is the standalone/headless path for future re-acquisition.
        proc = subprocess.run(
            ["claude", "-p", "--model", "claude-fable-5", "--tools", ""],
            input=prompt, capture_output=True, text=True, timeout=SUBPROC_TIMEOUT)
        if proc.returncode != 0:
            sys.stderr.write((proc.stderr or proc.stdout)[:400])
            return proc.returncode or 1
        sys.stdout.write(proc.stdout)
        return 0
    if vendor == "codex":
        fd, out_path = tempfile.mkstemp(suffix=".txt")
        os.close(fd)
        try:
            # cwd = an EMPTY temp dir, never the repo: the read-only sandbox can
            # read files, and the fixture keys (argument-state.md) live in-repo —
            # the blind-runner discipline demands the judge see only the prompt.
            with tempfile.TemporaryDirectory(prefix="agd_judge_") as blind_cwd:
                proc = subprocess.run(
                    ["codex", "exec", "-m", "gpt-5.6-sol",
                     "-c", 'model_reasoning_effort="xhigh"',
                     "-s", "read-only", "--skip-git-repo-check",
                     "--output-last-message", out_path],
                    input=prompt, capture_output=True, text=True,
                    timeout=SUBPROC_TIMEOUT, cwd=blind_cwd)
            if proc.returncode != 0:
                sys.stderr.write((proc.stderr or proc.stdout)[:400])
                return proc.returncode or 1
            with open(out_path, "r", encoding="utf-8") as fh:
                sys.stdout.write(fh.read())
            return 0
        finally:
            os.unlink(out_path)
    sys.stderr.write("JUDGE_VENDOR must be 'fable' or 'codex'\n")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
