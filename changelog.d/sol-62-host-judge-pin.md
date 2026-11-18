### Evals: AGD-scan host judge

The standalone `codex` transport in `evals/benchmark/agd-scan/host_judge_cmd.py`
now defaults to `gpt-6.2-sol` (medium) in place of `gpt-6.1-sol`, following the
fleet's 2026-11-17 Sol 6.2 screen. `SETEC_HOST_MODEL` and
`SETEC_HOST_REASONING_EFFORT` still override it, the frozen R3B driver keeps its
historical pins, and existing manifests keep their recorded models. Sol 6.2 on a
ChatGPT account needs Codex CLI 0.169.1 or newer.
