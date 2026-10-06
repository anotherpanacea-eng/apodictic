#!/usr/bin/env python3
"""Reproduce the pinned, offline WinAnsi Helvetica metric table.

Original source files are retained unchanged with their licenses and notices.
This derived table normalizes PDF's nbspace/sfthyphen names to the corresponding
Helvetica space/hyphen metrics. Undefined CP1252 bytes and controls are excluded.
"""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parent
SOURCES = {
    "Helvetica.afm": "da33f1870474c8e68bfe3e2353ff107ab6c6eea1f9836ce2aaf1e1a07b17982f",
    "ADOBE-LICENSE": "8618df77fef76491116b941327bfeddf4976ab7ca98f24fe97385761ba8e09f9",
    "WinAnsiEncoding.java": "3f490da5a07c01f3301e7ec418a434d36854182208216f42a30a61d31863019a",
    "APACHE-LICENSE": "1301d8415a4868d82aeeec594849cf7679f1ead4636a9603dc46875f5713157e",
    "APACHE-NOTICE": "40741b4ab76d77ba4fbc5e8759277169fb0ce281859d273075de6fd3a3588458",
}


def generate():
    raw = {}
    for name, expected in SOURCES.items():
        data = (ROOT / name).read_bytes()
        if hashlib.sha256(data).hexdigest() != expected:
            raise ValueError("pinned metrics source mismatch: " + name)
        raw[name] = data.decode("ascii")
    metrics = {}
    for line in raw["Helvetica.afm"].splitlines():
        if not line.startswith("C "):
            continue
        fields = dict(part.strip().split(" ", 1) for part in line.split(";") if part.strip())
        name = fields["N"]
        if name in metrics:
            raise ValueError("duplicate AFM glyph")
        metrics[name] = [int(fields["WX"]), [int(n) for n in fields["B"].split()]]
    mapping = re.findall(r'\{(0[0-7]+), "([A-Za-z0-9]+)"\}', raw["WinAnsiEncoding.java"])
    table = {}
    for octal, name in mapping:
        code = int(octal, 8)
        try:
            char = bytes([code]).decode("cp1252")
        except UnicodeDecodeError:
            continue
        if code < 32 or code == 127:
            continue
        metric_name = {"nbspace": "space", "sfthyphen": "hyphen"}.get(name, name)
        advance, box = metrics[metric_name]
        if str(code) in table:
            raise ValueError("duplicate WinAnsi mapping")
        table[str(code)] = {"name": name, "advance": advance, "box": box,
                            "whitespace": char in (" ", "\u00a0")}
    if len(table) != 218:
        raise ValueError("unexpected WinAnsi coverage: %d" % len(table))
    return {"schema": "apodictic.helvetica-winansi-metrics.v1", "sources": SOURCES,
            "notice": "Modified by APODICTIC: derived from Adobe Helvetica AFM and Apache PDFBox WinAnsiEncoding; normalized nbspace/sfthyphen to Helvetica space/hyphen metrics and excluded controls and undefined CP1252 bytes. Original licenses and notices accompany this table.",
            "glyphs": table}


if __name__ == "__main__":
    data = (json.dumps(generate(), sort_keys=True, indent=2) + "\n").encode("ascii")
    (ROOT / "helvetica-winansi.json").write_bytes(data)
