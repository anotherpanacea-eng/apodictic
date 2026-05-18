#!/usr/bin/env python3
"""
ai_prose_voice_distance.py — SETEC subprocess shim.

Voice-coherence diagnostic: Burrows Delta + per-feature cosine against a
baseline or manifest. Forwards to SETEC Voiceprint's `voice_distance.py`.
See ai-prose-calibration.md for the audit-level contract.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from setec_discovery import SetecDiscoveryError, run_setec_script  # noqa: E402


def main(argv: list[str]) -> int:
    try:
        result = run_setec_script("voice_distance.py", argv)
    except SetecDiscoveryError as e:
        print(str(e), file=sys.stderr)
        return 2
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
