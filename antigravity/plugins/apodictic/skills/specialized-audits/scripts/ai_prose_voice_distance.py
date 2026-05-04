#!/usr/bin/env python3
"""
voice_distance.py
Compare a target text against a writer/register baseline using classic
stylometric feature families.

This is a voice-coherence tool, not an AI-provenance detector.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from ai_prose_stylometry_core import compare_to_baseline, load_entries, read_text


def fmt(value: Any, digits: int = 4) -> str:
    if value is None:
        return "--"
    if isinstance(value, (int, float)):
        return f"{value:.{digits}f}"
    return str(value)


def md_cell(value: Any) -> str:
    text = str(value).replace("\n", " ")
    text = text.replace("|", "\\|")
    return text


def build_limits(args: argparse.Namespace) -> dict[str, int]:
    return {
        "function_words": args.function_top,
        "char_ngrams": args.char_top,
        "pos_trigrams": args.pos_top,
        "dependency_ngrams": args.dep_top,
    }


def render_report(result: dict[str, Any], target_path: Path, top_n: int) -> str:
    lines = []
    target = result["target_summary"]
    baseline = result["baseline_summary"]
    overall = result["overall"]

    lines.append(f"# Voice Distance Audit: {target_path.name}")
    lines.append("")
    lines.append(
        "**Use:** stylometric distance from the supplied baseline. "
        "This is not an AI-provenance verdict."
    )
    lines.append("")
    lines.append(f"**Target words:** {target.get('n_words', 0)}")
    lines.append(
        f"**Baseline:** {baseline.get('n_files', 0)} files, "
        f"{baseline.get('total_words', 0)} words "
        f"(mean {baseline.get('mean_words', 0):.0f})"
    )
    if result.get("warnings"):
        lines.append("")
        lines.append("**Warnings:**")
        for warning in result["warnings"]:
            lines.append(f"- {warning}")
    lines.append("")
    lines.append(
        f"**Overall:** {overall['band']} "
        f"(weighted Delta {overall['weighted_delta']:.3f})"
    )
    lines.append("")
    lines.append(overall["interpretation"])
    lines.append("")

    lines.append("## Family Distances")
    lines.append("")
    lines.append("| family | features | Burrows-style Delta | cosine to centroid | mean cosine to files |")
    lines.append("|---|---:|---:|---:|---:|")
    for family, info in sorted(result["families"].items()):
        delta = fmt(info["burrows_delta"], 3)
        if info.get("capped_in_overall"):
            delta = f"{delta} (capped at {info['overall_delta_contribution_cap']:.1f} in overall)"
        lines.append(
            f"| {family} | {info['n_features']} | "
            f"{delta} | "
            f"{fmt(info['cosine_distance_to_centroid'], 4)} | "
            f"{fmt(info['cosine_distance_to_baseline_mean'], 4)} |"
        )
    lines.append("")

    lines.append("## Top Deviations")
    lines.append("")
    lines.append(
        "Largest absolute z-scores against the supplied baseline. "
        "Read these as drift candidates, not automatic errors."
    )
    for family, info in sorted(result["families"].items()):
        deviations = [d for d in info.get("top_deviations", []) if d.get("z") is not None]
        if not deviations:
            continue
        lines.append("")
        lines.append(f"### {family}")
        lines.append("")
        lines.append("| feature | z | target | baseline mean | baseline sd |")
        lines.append("|---|---:|---:|---:|---:|")
        for item in deviations[:top_n]:
            lines.append(
                f"| `{md_cell(item['feature'])}` | "
                f"{fmt(item['z'], 2)} | "
                f"{fmt(item['value'], 6)} | "
                f"{fmt(item['baseline_mean'], 6)} | "
                f"{fmt(item['baseline_sd'], 6)} |"
            )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare a target text to a writer/register stylometric baseline."
    )
    parser.add_argument("target", help="Target .txt or .md file.")
    parser.add_argument("--baseline-dir", help="Directory of baseline .txt/.md files.")
    parser.add_argument("--manifest", help="Optional JSONL corpus manifest.")
    parser.add_argument("--use", default="baseline",
                        help="Manifest filter: required use tag (default: baseline).")
    parser.add_argument("--split", help="Manifest filter: split value.")
    parser.add_argument("--register", help="Manifest filter: register value.")
    parser.add_argument("--persona", help="Manifest filter: persona value.")
    parser.add_argument("--ai-status", default="pre_ai_human",
                        help="Manifest filter: ai_status (default: pre_ai_human).")
    parser.add_argument("--function-top", type=int, default=100,
                        help="Top function words from baseline (default 100).")
    parser.add_argument("--char-top", type=int, default=500,
                        help="Top character n-grams from baseline (default 500).")
    parser.add_argument("--pos-top", type=int, default=300,
                        help="Top POS trigrams from baseline (default 300).")
    parser.add_argument("--dep-top", type=int, default=300,
                        help="Top dependency-label n-grams from baseline (default 300).")
    parser.add_argument("--top", type=int, default=12,
                        help="Top deviations to show per family (default 12).")
    parser.add_argument("--no-spacy", action="store_true",
                        help="Skip POS and dependency feature families.")
    parser.add_argument("--json", action="store_true", help="Output JSON.")
    parser.add_argument("--out", help="Write report to file instead of stdout.")
    args = parser.parse_args()

    if not args.baseline_dir and not args.manifest:
        parser.error("Provide either --baseline-dir or --manifest.")

    target_path = Path(args.target)
    baseline_entries = load_entries(
        baseline_dir=args.baseline_dir,
        manifest=args.manifest,
        use=args.use,
        split=args.split,
        register=args.register,
        persona=args.persona,
        ai_status=args.ai_status,
    )
    if not baseline_entries:
        print("No baseline entries matched the requested filters.", file=sys.stderr)
        return 1

    result = compare_to_baseline(
        read_text(target_path),
        baseline_entries,
        include_spacy=not args.no_spacy,
        limits=build_limits(args),
    )

    if args.json:
        output = json.dumps(result, indent=2, default=str)
    else:
        output = render_report(result, target_path, args.top)

    if args.out:
        Path(args.out).write_text(output, encoding="utf-8")
        print(f"Written to {args.out}", file=sys.stderr)
    else:
        print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
