#!/usr/bin/env python3
"""Validate sealed panel returns and emit judgment-free agreement-alpha CSVs."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from panel_schema import (
    ARC, ARGUMENT_UNITS, BOUNDARY_PATTERN, CONSEQUENCE, DEPENDENCY, EXPERTISE,
    FIELDS, FICTION_UNITS, FLAG_PRESENCE, FLAG_TYPES, LAYER, RECEPTIVITY, TARGET,
    VERDICT, YES_NO, normalized_locus,
)


def die(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def enum(value: str, allowed, field: str, where: str, blank: bool = False) -> str:
    if blank and value == "":
        return value
    if value not in allowed:
        die(f"{where}: {field}={value!r}; expected one of {sorted(allowed)}")
    return value


def locus(value: str, count: int, field: str, where: str) -> str:
    try:
        return normalized_locus(value, count)
    except ValueError as exc:
        die(f"{where}: {field}: {exc}")


def load_counts(path: Path) -> dict[str, int]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    try:
        result = {row["unit_id"]: int(row["paragraph_count"]) for row in rows}
    except (KeyError, ValueError) as exc:
        die(f"malformed source map: {exc}")
    expected = set(ARGUMENT_UNITS + FICTION_UNITS)
    if set(result) != expected:
        die(f"source map units differ: got {sorted(result)}, expected {sorted(expected)}")
    return result


def emit(path: Path, rows: list[tuple[str, str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(("rater", "unit", "value"))
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-map", type=Path, required=True)
    parser.add_argument("--responses", type=Path, nargs="+", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    counts = load_counts(args.source_map)
    dimensions: dict[str, list[tuple[str, str, str]]] = {}
    seen: set[tuple[str, str]] = set()

    def add(name: str, rater: str, unit: str, value: str) -> None:
        dimensions.setdefault(name, []).append((rater, unit, value))

    for response in args.responses:
        file_rater = None
        with response.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            if tuple(reader.fieldnames or ()) != FIELDS:
                die(f"{response}: header does not exactly match the closed schema")
            for line_no, row in enumerate(reader, 2):
                where = f"{response}:{line_no}"
                rater, unit = row["editor_id"].strip(), row["unit_id"].strip()
                if not rater:
                    die(f"{where}: editor_id is required")
                if file_rater is None:
                    file_rater = rater
                elif rater != file_rater:
                    die(f"{where}: one sealed return file may contain only editor_id {file_rater}")
                if unit not in ARGUMENT_UNITS + FICTION_UNITS:
                    die(f"{where}: unknown unit_id {unit!r}")
                if (rater, unit) in seen:
                    die(f"{where}: duplicate rater/unit {rater}/{unit}")
                seen.add((rater, unit))
                domain = "argument" if unit in ARGUMENT_UNITS else "fiction"
                if row["domain"] != domain:
                    die(f"{where}: domain must be {domain}")
                enum(row["recognized"], YES_NO, "recognized", where)
                count = counts[unit]

                if domain == "argument":
                    for field in ("fgt1_movement_count", *(f"fgt1_boundary_{n}" for n in range(1, 9)),
                                  "fgt1_boundary_pattern", "fgt5_arc"):
                        if row[field] != "":
                            die(f"{where}: fiction-only field {field} must be blank on argument rows")
                    layer = enum(row["gt2_layer"], LAYER, "gt2_layer", where)
                    if layer == "NONE" and (row["gt2_locus_1"] or row["gt2_locus_2"]):
                        die(f"{where}: gt2_layer NONE forbids GT2 loci")
                    if layer != "NONE" and not row["gt2_locus_1"]:
                        die(f"{where}: non-NONE gt2_layer requires gt2_locus_1")
                    add("argument_gt2_layer_nominal", rater, unit, layer)
                    for slot in (1, 2):
                        for anchor in ("gt2", "gt5", "gt6", "gt8"):
                            field = f"{anchor}_locus_{slot}"
                            add(f"argument_{anchor}_locus_{slot}_ordinal", rater, unit,
                                locus(row[field], count, field, where))
                    add("argument_gt4_expertise_ordinal", rater, unit, enum(row["gt4_expertise"], EXPERTISE, "gt4_expertise", where) and EXPERTISE[row["gt4_expertise"]])
                    add("argument_gt4_receptivity_ordinal", rater, unit, enum(row["gt4_receptivity"], RECEPTIVITY, "gt4_receptivity", where) and RECEPTIVITY[row["gt4_receptivity"]])
                    add("argument_gt4_consequence_ordinal", rater, unit, enum(row["gt4_consequence"], CONSEQUENCE, "gt4_consequence", where) and CONSEQUENCE[row["gt4_consequence"]])
                    family = enum(row["gt5_family"], TARGET, "gt5_family", where)
                    if family == "NONE" and (row["gt5_locus_1"] or row["gt5_locus_2"]):
                        die(f"{where}: gt5_family NONE forbids GT5 loci")
                    if family != "NONE" and not row["gt5_locus_1"]:
                        die(f"{where}: non-NONE gt5_family requires gt5_locus_1")
                    add("argument_gt5_family_nominal", rater, unit, family)
                    target = enum(row["gt6_target"], TARGET, "gt6_target", where)
                    dependency = enum(row["gt6_dependency"], DEPENDENCY, "gt6_dependency", where)
                    if target == "NONE" and (row["gt6_locus_1"] or row["gt6_locus_2"] or dependency != "NONE"):
                        die(f"{where}: gt6_target NONE forbids loci and requires dependency NONE")
                    if target != "NONE" and (not row["gt6_locus_1"] or dependency == "NONE"):
                        die(f"{where}: non-NONE gt6_target requires locus_1 and a non-NONE dependency")
                    add("argument_gt6_target_nominal", rater, unit, target)
                    add("argument_gt6_dependency_nominal", rater, unit, dependency)
                    add("argument_gt7_verdict_nominal", rater, unit, enum(row["gt7_verdict"], VERDICT, "gt7_verdict", where))
                    presence = enum(row["gt8_presence"], FLAG_PRESENCE, "gt8_presence", where)
                    add("argument_gt8_presence_nominal", rater, unit, presence)
                    flags = set(filter(None, row["gt8_flag_types"].split(";")))
                    if not flags.issubset(FLAG_TYPES):
                        die(f"{where}: unknown gt8 flag type(s) {sorted(flags - set(FLAG_TYPES))}")
                    if presence == "NONE_REGISTERED" and (flags or row["gt8_locus_1"] or row["gt8_locus_2"]):
                        die(f"{where}: NONE_REGISTERED forbids GT8 loci/types")
                    if presence == "FLAG_PRESENT" and (not row["gt8_locus_1"] or not flags):
                        die(f"{where}: FLAG_PRESENT requires gt8_locus_1 and at least one flag type")
                    for flag in FLAG_TYPES:
                        add(f"argument_gt8_type_{flag.lower()}_nominal", rater, unit, "1" if flag in flags else "0")
                else:
                    for field in FIELDS[4:22]:
                        if row[field] != "":
                            die(f"{where}: argument-only field {field} must be blank on fiction rows")
                    movement = row["fgt1_movement_count"]
                    if movement not in {str(n) for n in range(1, 10)}:
                        die(f"{where}: fgt1_movement_count must be 1..9")
                    add("fiction_fgt1_movement_count_ordinal", rater, unit, movement)
                    boundary_values = [row[f"fgt1_boundary_{slot}"] for slot in range(1, 9)]
                    expected_boundaries = int(movement) - 1
                    if "" in boundary_values[:expected_boundaries] or any(boundary_values[expected_boundaries:]):
                        die(f"{where}: movement count {movement} requires exactly {expected_boundaries} contiguous boundary loci")
                    for slot in range(1, 9):
                        field = f"fgt1_boundary_{slot}"
                        add(f"fiction_fgt1_boundary_{slot}_ordinal", rater, unit,
                            locus(row[field], count, field, where))
                    add("fiction_fgt1_boundary_pattern_nominal", rater, unit,
                        enum(row["fgt1_boundary_pattern"], BOUNDARY_PATTERN, "fgt1_boundary_pattern", where))
                    add("fiction_fgt5_arc_nominal", rater, unit, enum(row["fgt5_arc"], ARC, "fgt5_arc", where))

    expected_units = set(ARGUMENT_UNITS + FICTION_UNITS)
    by_rater: dict[str, set[str]] = {}
    for rater, unit in seen:
        by_rater.setdefault(rater, set()).add(unit)
    for rater, units in by_rater.items():
        if units != expected_units:
            die(f"{rater}: incomplete sealed return; missing {sorted(expected_units - units)}")
    if len(by_rater) < 3:
        die("at least three participating editors are required")

    args.out.mkdir(parents=True, exist_ok=True)
    emitted = 0
    for name, rows in sorted(dimensions.items()):
        pairable_units = {unit for _rater, unit, value in rows if value != ""}
        if len(pairable_units) < 2:
            print(f"SKIP: {name} has fewer than two non-missing units; non-clearing")
            continue
        emit(args.out / f"{name}.csv", rows)
        emitted += 1
    print(f"OK: compiled {len(by_rater)} editors into {emitted} pairable tidy dimensions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
