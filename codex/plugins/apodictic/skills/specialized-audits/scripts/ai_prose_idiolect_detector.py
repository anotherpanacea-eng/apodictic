#!/usr/bin/env python3
"""
ai_prose_idiolect_detector.py — SETEC subprocess shim.

Idiolect detection + preservation list: surfaces the keyness-distinctive
words and collocations a writer uses idiosyncratically relative to a
reference corpus. The preservation list (`--preservation-output`) tells
downstream revision work which phrases NOT to normalize away.

Drives the /coach revision-coaching path: when a revision plan is built,
the coach can show this list so line-editing passes don't sand off
signature moves. Forwards to SETEC Voiceprint's `idiolect_detector.py`;
see ai-prose-calibration.md and the idiolect-preservation reference for
the audit-level contract.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from setec_discovery import SetecDiscoveryError, run_setec_script  # noqa: E402


def main(argv: list[str]) -> int:
    try:
        result = run_setec_script("idiolect_detector.py", argv)
    except SetecDiscoveryError as e:
        print(str(e), file=sys.stderr)
        return 2
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
