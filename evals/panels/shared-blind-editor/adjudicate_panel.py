#!/usr/bin/env python3
"""Compute alpha licensing and frozen key compatibility for panel dimensions."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import os
import statistics
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = Path(os.environ.get("APODICTIC_REPO", HERE.parents[2])).resolve()

spec = importlib.util.spec_from_file_location("agreement_alpha", REPO / "scripts/agreement_alpha.py")
if spec is None or spec.loader is None:
    raise SystemExit("ERROR: cannot load scripts/agreement_alpha.py")
alpha_lib = importlib.util.module_from_spec(spec)
spec.loader.exec_module(alpha_lib)

DIMENSIONS = {
    ("GT2", "layer"): "argument_gt2_layer_nominal",
    ("GT2", "locus_1"): "argument_gt2_locus_1_ordinal",
    ("GT2", "locus_2"): "argument_gt2_locus_2_ordinal",
    ("GT4", "expertise"): "argument_gt4_expertise_ordinal",
    ("GT4", "receptivity"): "argument_gt4_receptivity_ordinal",
    ("GT4", "consequence"): "argument_gt4_consequence_ordinal",
    ("GT5", "family"): "argument_gt5_family_nominal",
    ("GT5", "locus_1"): "argument_gt5_locus_1_ordinal",
    ("GT5", "locus_2"): "argument_gt5_locus_2_ordinal",
    ("GT6", "target"): "argument_gt6_target_nominal",
    ("GT6", "locus_1"): "argument_gt6_locus_1_ordinal",
    ("GT6", "locus_2"): "argument_gt6_locus_2_ordinal",
    ("GT6", "dependency"): "argument_gt6_dependency_nominal",
    ("GT7", "verdict"): "argument_gt7_verdict_nominal",
    ("GT8", "presence"): "argument_gt8_presence_nominal",
    ("GT8", "locus_1"): "argument_gt8_locus_1_ordinal",
    ("GT8", "locus_2"): "argument_gt8_locus_2_ordinal",
    **{("GT8", f"type_{flag}"): f"argument_gt8_type_{flag}_nominal" for flag in
       ("contestable", "unearned", "overloaded", "external-verify", "definitional")},
    ("FGT1", "movement_count"): "fiction_fgt1_movement_count_ordinal",
    ("FGT1", "boundary_pattern"): "fiction_fgt1_boundary_pattern_nominal",
    **{("FGT1", f"boundary_{slot}"): f"fiction_fgt1_boundary_{slot}_ordinal" for slot in range(1, 9)},
    ("FGT5", "arc"): "fiction_fgt5_arc_nominal",
}


def load_ratings(path: Path, metric: str):
    rows, error = alpha_lib.read_ratings(path.read_text(encoding="utf-8"))
    if error:
        raise ValueError(error)
    order, by_unit, raters = alpha_lib.units_from_rows(rows)
    values = alpha_lib._coerce_for_metric(by_unit, order, metric)
    return rows, order, by_unit, raters, values


def panel_value(values: list[str], metric: str):
    if not values:
        return None, None, None, "missing"
    if metric == "nominal":
        counts = Counter(values)
        top = max(counts.values())
        modes = sorted(value for value, count in counts.items() if count == top)
        if len(modes) != 1:
            return None, None, None, "tie"
        return modes[0], "", "", "unique-mode"
    numeric = [float(value) for value in values]
    return statistics.median(numeric), min(numeric), max(numeric), "median"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ratings-dir", type=Path, required=True)
    parser.add_argument("--key-projection", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=alpha_lib._DEFAULT_SEED)
    parser.add_argument("--resamples", type=int, default=alpha_lib._DEFAULT_RESAMPLES)
    args = parser.parse_args()
    if args.resamples < alpha_lib._DEFAULT_RESAMPLES:
        raise SystemExit(f"ERROR: resamples must be >= {alpha_lib._DEFAULT_RESAMPLES}")
    with args.key_projection.open(newline="", encoding="utf-8") as handle:
        projections = list(csv.DictReader(handle))
    required = {"unit_id", "anchor", "subdimension", "accepted_tokens", "accepted_min", "accepted_max"}
    if not projections or not required.issubset(projections[0]):
        raise SystemExit("ERROR: malformed key projection header")

    output_rows = []
    anchor_states: dict[tuple[str, str], list[str]] = {}
    cache = {}
    for projection in projections:
        unit, anchor, sub = projection["unit_id"], projection["anchor"], projection["subdimension"]
        dimension = DIMENSIONS.get((anchor, sub))
        if dimension is None:
            raise SystemExit(f"ERROR: no frozen dimension mapping for {anchor}/{sub}")
        metric = "ordinal" if dimension.endswith("_ordinal") else "nominal"
        path = args.ratings_dir / f"{dimension}.csv"
        alpha = lo = hi = None
        value = low = high = None
        compatible = False
        reason = ""
        if not path.is_file():
            state, reason = "PROVISIONAL", "missing-ratings-file"
        else:
            if path not in cache:
                rows, order, by_unit, raters, unit_values = load_ratings(path, metric)
                point, _n, _do, _de = alpha_lib.alpha_from_unit_values(unit_values, metric)
                pairable = sum(1 for values_ in unit_values if len(values_) >= 2)
                rating_editors = len({r for r, _u, v in rows if v is not None})
                if point is not None:
                    lo_, hi_, _defined = alpha_lib.bootstrap_ci(unit_values, metric, args.seed, args.resamples)
                else:
                    lo_ = hi_ = None
                cache[path] = (rows, by_unit, point, lo_, hi_, pairable, rating_editors)
            rows, by_unit, alpha, lo, hi, pairable, rating_editors = cache[path]
            unit_ratings = [value_ for r, u, value_ in rows if u == unit and value_ is not None]
            value, low, high, value_reason = panel_value(unit_ratings, metric)
            if rating_editors < 3:
                state, reason = "PROVISIONAL", "fewer-than-3-editors"
            elif pairable < 4:
                state, reason = "PROVISIONAL", "fewer-than-4-pairable-units"
            elif alpha is None or lo is None:
                state, reason = "PROVISIONAL", "undefined-alpha-or-ci"
            elif lo < .667:
                state, reason = "LOW_AGREEMENT", "ci-lower-below-.667"
            elif lo < .800:
                state, reason = "PROVISIONAL", "ci-lower-below-.800"
            elif value is None:
                state, reason = "PROVISIONAL", value_reason
            else:
                tokens = set(filter(None, projection["accepted_tokens"].split("|")))
                if metric == "nominal":
                    compatible = str(value) in tokens
                else:
                    compatible = (projection["accepted_min"] != "" and projection["accepted_max"] != ""
                                  and float(projection["accepted_min"]) <= float(value)
                                  <= float(projection["accepted_max"]))
                state = "SUBDIMENSION_CLEAR" if compatible else "KEY_REVIEW"
                reason = "compatible" if compatible else "panel-value-outside-frozen-projection"
        anchor_states.setdefault((unit, anchor), []).append(state)
        output_rows.append({
            "unit_id": unit, "anchor": anchor, "subdimension": sub, "dimension_file": path.name,
            "metric": metric, "alpha": "" if alpha is None else f"{alpha:.6f}",
            "ci_lower": "" if lo is None else f"{lo:.6f}", "ci_upper": "" if hi is None else f"{hi:.6f}",
            "panel_value": "" if value is None else str(value), "observed_min": "" if low is None else str(low),
            "observed_max": "" if high is None else str(high), "compatible": str(compatible).lower(),
            "subdimension_state": state, "reason": reason,
        })

    summary = []
    for (unit, anchor), states in sorted(anchor_states.items()):
        if "KEY_REVIEW" in states:
            result = "KEY_REVIEW"
        elif "LOW_AGREEMENT" in states:
            result = "LOW_AGREEMENT"
        elif all(state == "SUBDIMENSION_CLEAR" for state in states):
            result = "LICENSE_CANDIDATE"
        else:
            result = "PROVISIONAL"
        summary.append((unit, anchor, result, "|".join(states)))

    args.output.mkdir(parents=True, exist_ok=True)
    with (args.output / "SUBDIMENSIONS.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=output_rows[0].keys())
        writer.writeheader(); writer.writerows(output_rows)
    with (args.output / "ANCHOR-SUMMARY.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle); writer.writerow(("unit_id", "anchor", "result", "subdimension_states")); writer.writerows(summary)
    print(f"OK: adjudicated {len(output_rows)} frozen subdimensions across {len(summary)} anchors")
    for unit, anchor, result, _states in summary:
        print(f"  {unit} {anchor}: {result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
