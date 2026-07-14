#!/usr/bin/env python3
"""Hermetic end-to-end test for the closed packet response compiler."""

from __future__ import annotations

import csv
import subprocess
import sys
import tempfile
from pathlib import Path

from panel_schema import ARGUMENT_UNITS, FIELDS, FICTION_UNITS, FLAG_TYPES

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="apodictic-panel-self-test-") as raw:
        root = Path(raw)
        source_map = root / "SOURCE-MAP.csv"
        with source_map.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(("unit_id", "paragraph_count"))
            for unit in ARGUMENT_UNITS + FICTION_UNITS:
                writer.writerow((unit, 20))

        responses = []
        layers = ("CLAIM", "SUPPORT", "WARRANT", "SCOPE", "OBJECTION")
        targets = ("CLAIM", "SUPPORT", "WARRANT", "SCOPE", "OBJECTION")
        expertise = ("GENERAL", "MIXED", "SPECIALIST", "MIXED", "GENERAL")
        receptivity = ("HOSTILE", "MIXED", "SYMPATHETIC", "MIXED", "HOSTILE")
        consequence = ("LOW", "MEDIUM", "HIGH", "MEDIUM", "LOW")
        verdicts = ("WARRANTED", "UNWARRANTED", "UNCONVENTIONAL-BUT-WARRANTED", "WARRANTED", "UNWARRANTED")
        arcs = ("STEADY_GROWTH", "FALL", "CIRCULAR_RETURN", "FLAT_NO_REVERSAL",
                "DENIAL_STAGED_CONFRONTATION_REVERSAL", "OTHER", "STEADY_GROWTH")
        patterns = ("FORMAL_DIVISIONS", "VISITATION_OR_ENCOUNTER", "CAUSAL_TURNS",
                    "HYBRID", "OTHER_RECURRENT", "NO_STABLE_PATTERN", "FORMAL_DIVISIONS")
        for editor in ("E01", "E02", "E03"):
            path = root / f"{editor}.csv"
            responses.append(path)
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=FIELDS)
                writer.writeheader()
                for index, unit in enumerate(ARGUMENT_UNITS):
                    row = {field: "" for field in FIELDS}
                    row.update(
                        editor_id=editor, unit_id=unit, domain="argument", recognized="NO",
                        gt2_layer=layers[index], gt2_locus_1=str(index + 1),
                        gt4_expertise=expertise[index], gt4_receptivity=receptivity[index],
                        gt4_consequence=consequence[index], gt5_family=targets[index],
                        gt5_locus_1=str(index + 2), gt6_target=targets[index],
                        gt6_locus_1=str(index + 3), gt6_dependency="BEFORE_SUPPORT",
                        gt7_verdict=verdicts[index],
                        gt8_presence="FLAG_PRESENT" if index % 2 else "NONE_REGISTERED",
                        gt8_locus_1=str(index + 4) if index % 2 else "",
                        gt8_flag_types=FLAG_TYPES[index % len(FLAG_TYPES)] if index % 2 else "",
                    )
                    writer.writerow(row)
                for index, unit in enumerate(FICTION_UNITS):
                    row = {field: "" for field in FIELDS}
                    row.update(
                        editor_id=editor, unit_id=unit, domain="fiction", recognized="NO",
                        fgt1_movement_count=str(index % 7 + 1),
                        fgt1_boundary_pattern=patterns[index], fgt5_arc=arcs[index],
                    )
                    for slot in range(1, index % 7 + 1):
                        row[f"fgt1_boundary_{slot}"] = str(slot + index)
                    writer.writerow(row)

        out = root / "ratings"
        command = [sys.executable, str(HERE / "compile_responses.py"), "--source-map",
                   str(source_map), "--responses", *(str(path) for path in responses),
                   "--out", str(out)]
        subprocess.run(command, check=True, capture_output=True, text=True)
        files = sorted(out.glob("*.csv"))
        if not files:
            raise SystemExit("FAILED: compiler emitted no pairable dimensions")
        for path in files:
            metric = "ordinal" if path.stem.endswith("_ordinal") else "nominal"
            result = subprocess.run(
                ["bash", str(REPO / "scripts/validate.sh"), "agreement-alpha", str(path),
                 "--metric", metric, "--resamples", "1000"],
                capture_output=True, text=True,
            )
            if result.returncode != 0:
                raise SystemExit(f"FAILED: {path.name}:\n{result.stdout}{result.stderr}")
        adjudication = root / "adjudication"
        subprocess.run(
            [sys.executable, str(HERE / "adjudicate_panel.py"), "--ratings-dir", str(out),
             "--key-projection", str(HERE / "key-projection.csv"), "--output", str(adjudication)],
            check=True, capture_output=True, text=True,
        )
        if not (adjudication / "ANCHOR-SUMMARY.csv").is_file():
            raise SystemExit("FAILED: adjudication did not emit anchor summary")

        hostile = (
            ("fiction-domain-garbage", "F01", "gt2_layer", "GARBAGE"),
            ("flag-without-type", "A02", "gt8_flag_types", ""),
            ("none-plus-locus", "A01", "gt2_layer", "NONE"),
            ("missing-required-locus", "A01", "gt5_locus_1", ""),
            ("noninteger-locus", "A01", "gt2_locus_1", "P3"),
            ("noncontiguous-boundary", "F03", "fgt1_boundary_1", ""),
        )
        with responses[0].open(newline="", encoding="utf-8") as handle:
            base_rows = list(csv.DictReader(handle))
        for label, unit, field, value in hostile:
            bad = root / f"bad-{label}.csv"
            rows = [dict(row) for row in base_rows]
            next(row for row in rows if row["unit_id"] == unit)[field] = value
            with bad.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=FIELDS); writer.writeheader(); writer.writerows(rows)
            result = subprocess.run(
                [sys.executable, str(HERE / "compile_responses.py"), "--source-map", str(source_map),
                 "--responses", str(bad), str(responses[1]), str(responses[2]),
                 "--out", str(root / f"bad-out-{label}")],
                capture_output=True, text=True,
            )
            if result.returncode == 0:
                raise SystemExit(f"FAILED: hostile case accepted: {label}")
        print(f"Self-test: PASS ({len(files)} populated dimensions + {len(hostile)} hostile arms)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
