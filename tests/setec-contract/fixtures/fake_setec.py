#!/usr/bin/env python3
"""fake_setec.py — stdlib-only reference fake for SETEC consumers (R5).

Implements the consumer-facing half of R5 in
``references/setec-normalized-entrypoint-spec.md`` §6.

APODICTIC (and any other consumer) vendors a pinned copy of this file
alongside the golden fixtures next to it. It lets the consumer's CI
exercise its envelope parser against a REAL ``schema_version: 1.0``
envelope per surface **without installing SETEC's heavy dependencies**
(spaCy / torch / scipy / sentence-transformers). It is import- and
dependency-free on purpose: stdlib ``json`` + ``pathlib`` only.

The envelopes it prints are the committed golden fixtures in this same
directory — the producer-owned contract. They carry normalization
sentinels for volatile fields (``version``, ``target.path``, timestamps,
fingerprints; see the directory ``README.md``), so a consumer parser
tested against them must tolerate those sentinel values exactly as it
tolerates real runtime values.

Usage::

    python3 fake_setec.py <surface>          # print that surface's envelope
    python3 fake_setec.py --list             # enumerate available surfaces
    python3 fake_setec.py <surface> | python3 -m json.tool   # validate JSON

Exit codes::

    0  envelope printed / list printed
    2  unknown surface (the message names the valid surfaces)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

FIXTURES_DIR = Path(__file__).resolve().parent


def available_surfaces() -> list[str]:
    """Sorted list of surfaces with a committed golden in this directory."""
    return sorted(
        p.stem for p in FIXTURES_DIR.glob("*.json")
    )


def envelope_for(surface: str) -> dict:
    """Return the golden envelope dict for *surface*.

    Raises ``KeyError`` with a helpful message when the surface has no
    committed golden.
    """
    path = FIXTURES_DIR / f"{surface}.json"
    if not path.exists():
        raise KeyError(surface)
    return json.loads(path.read_text(encoding="utf-8"))


def _usage() -> str:
    surfaces = ", ".join(available_surfaces())
    return (
        "usage: python3 fake_setec.py <surface> | --list\n"
        f"surfaces: {surfaces}"
    )


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args[0] in {"-h", "--help"}:
        print(_usage())
        return 0
    if args[0] in {"--list", "-l"}:
        for surface in available_surfaces():
            print(surface)
        return 0

    surface = args[0]
    try:
        envelope = envelope_for(surface)
    except KeyError:
        print(
            f"fake_setec: unknown surface {surface!r}.\n"
            f"available: {', '.join(available_surfaces())}",
            file=sys.stderr,
        )
        return 2
    # Pretty + sorted so piping into `python3 -m json.tool` is a no-op and
    # the printed form matches the committed golden byte-for-byte.
    print(json.dumps(envelope, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
