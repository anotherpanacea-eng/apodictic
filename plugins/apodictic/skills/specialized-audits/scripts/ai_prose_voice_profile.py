#!/usr/bin/env python3
"""
voice_profile.py
Produce a private, human-readable stylometric profile from a writer/register
baseline corpus.

The output should be treated as private. A voice profile is useful for
protecting a writer's idiolect during revision, but it is also a voice-cloning
input if shared carelessly.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from ai_prose_stylometry_core import build_profile, load_entries


def fmt(value: Any, digits: int = 6) -> str:
    if value is None:
        return "--"
    if isinstance(value, (int, float)):
        return f"{value:.{digits}f}"
    return str(value)


def md_cell(value: Any) -> str:
    return str(value).replace("\n", " ").replace("|", "\\|")


def build_limits(args: argparse.Namespace) -> dict[str, int]:
    return {
        "function_words": args.function_top,
        "char_ngrams": args.char_top,
        "pos_trigrams": args.pos_top,
        "dependency_ngrams": args.dep_top,
    }


def render_feature_table(items: list[dict[str, Any]], *, value_label: str, top_n: int) -> list[str]:
    lines = []
    lines.append(f"| feature | {value_label} | sd | cv |")
    lines.append("|---|---:|---:|---:|")
    for item in items[:top_n]:
        lines.append(
            f"| `{md_cell(item['feature'])}` | "
            f"{fmt(item['mean'])} | {fmt(item['sd'])} | {fmt(item.get('cv'), 4)} |"
        )
    return lines


def render_report(profile: dict[str, Any], top_n: int) -> str:
    baseline = profile["baseline_summary"]
    lines = []
    lines.append("# Private Voice Profile")
    lines.append("")
    lines.append(f"**{profile['privacy']}**")
    lines.append("")
    lines.append(
        "This profile describes the supplied baseline corpus. It is not an authorship "
        "certificate and should not be shared outside the local workspace."
    )
    lines.append("")
    lines.append("## Corpus")
    lines.append("")
    lines.append(f"**Files:** {baseline.get('n_files', 0)}")
    lines.append(f"**Total words:** {baseline.get('total_words', 0)}")
    lines.append(
        f"**Words per file:** mean {baseline.get('mean_words', 0):.0f}, "
        f"range {baseline.get('min_words', 0)}-{baseline.get('max_words', 0)}"
    )
    if profile.get("warnings"):
        lines.append("")
        lines.append("**Warnings:**")
        for warning in profile["warnings"]:
            lines.append(f"- {warning}")
    lines.append("")
    lines.append("## Feature Families")
    lines.append("")
    lines.append("| family | features retained |")
    lines.append("|---|---:|")
    for family, count in sorted(profile["selected_features"].items()):
        lines.append(f"| {family} | {count} |")
    lines.append("")

    for family, info in sorted(profile["families"].items()):
        lines.append(f"## {family}")
        lines.append("")
        lines.append("Most frequent or highest-valued baseline features:")
        lines.append("")
        lines.extend(render_feature_table(info["top_features"], value_label="mean", top_n=top_n))
        lines.append("")
        lines.append("Most stable nonzero baseline features:")
        lines.append("")
        lines.extend(render_feature_table(info["most_stable_features"], value_label="mean", top_n=top_n))
        lines.append("")

    return "\n".join(lines)


def is_private_output_path(path: str | None) -> bool:
    if not path:
        return True
    resolved_parts = Path(path).expanduser().resolve().parts
    return "ai-prose-baselines-private" in resolved_parts


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create a private stylometric profile from a baseline corpus."
    )
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
    parser.add_argument("--top", type=int, default=20,
                        help="Rows to show per table (default 20).")
    parser.add_argument("--no-spacy", action="store_true",
                        help="Skip POS and dependency feature families.")
    parser.add_argument("--json", action="store_true", help="Output JSON.")
    parser.add_argument("--out", help="Write report to file instead of stdout.")
    parser.add_argument(
        "--allow-public-output",
        action="store_true",
        help="Allow writing a voice profile outside ai-prose-baselines-private/.",
    )
    args = parser.parse_args()

    if not args.baseline_dir and not args.manifest:
        parser.error("Provide either --baseline-dir or --manifest.")

    entries = load_entries(
        baseline_dir=args.baseline_dir,
        manifest=args.manifest,
        use=args.use,
        split=args.split,
        register=args.register,
        persona=args.persona,
        ai_status=args.ai_status,
    )
    if not entries:
        print("No baseline entries matched the requested filters.", file=sys.stderr)
        return 1

    profile = build_profile(
        entries,
        include_spacy=not args.no_spacy,
        limits=build_limits(args),
    )

    if args.json:
        output = json.dumps(profile, indent=2, default=str)
    else:
        output = render_report(profile, args.top)

    if args.out and not args.allow_public_output and not is_private_output_path(args.out):
        print(
            "Refusing to write a voice profile outside ai-prose-baselines-private/. "
            "Pass --allow-public-output to override.",
            file=sys.stderr,
        )
        return 2

    if args.out:
        Path(args.out).write_text(output, encoding="utf-8")
        print(f"Written to {args.out}", file=sys.stderr)
    else:
        print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
