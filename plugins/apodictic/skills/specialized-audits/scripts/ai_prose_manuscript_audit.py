#!/usr/bin/env python3
"""
manuscript_audit.py
Cross-chapter aggregate of Layer A distributional diagnostics.

Runs variance_audit logic on every chapter of a manuscript (or every file
in a chapter directory) and produces a dashboard showing which chapters
deviate from baseline and on which signals. Surfaces manuscript-wide
patterns and outlier chapters that single-chapter audits miss.

Usage:
    python3 manuscript_audit.py MANUSCRIPT.md --baseline-dir BASELINE_DIR
    python3 manuscript_audit.py --chapter-dir CHAPTERS/ --baseline-dir BASELINE_DIR
    python3 manuscript_audit.py MANUSCRIPT.md --baseline-dir BASELINE_DIR --json
    python3 manuscript_audit.py MANUSCRIPT.md --baseline-dir BASELINE_DIR \\
        --chapter-pattern '^#+\s*Chapter\s*(\d+)'
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from pathlib import Path
from typing import Any

# Import variance_audit machinery from the same directory.
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from ai_prose_variance_audit import (  # type: ignore
    audit_text,
    audit_baseline,
    classify_compression,
)


def split_manuscript(text: str, pattern: str) -> list[dict[str, Any]]:
    """Split a manuscript on a chapter-marker regex. Returns list of dicts
    with keys 'label' (e.g. 'Chapter 4') and 'text'."""
    rx = re.compile(pattern, re.M)
    matches = list(rx.finditer(text))
    if not matches:
        return [{"label": "Whole text", "text": text}]
    chapters = []
    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        # Pull the full header line for label
        line_end = text.find("\n", start)
        header = text[start: line_end if line_end != -1 else end].strip().lstrip("#").strip()
        chapters.append({
            "label": header[:80],
            "text": text[start:end],
            "start_byte": start,
            "end_byte": end,
        })
    return chapters


def load_chapter_dir(directory: str) -> list[dict[str, Any]]:
    """Load every .txt or .md file from a directory as a chapter."""
    paths = sorted(Path(directory).glob("*.txt")) + sorted(Path(directory).glob("*.md"))
    chapters = []
    for p in paths:
        chapters.append({
            "label": p.name,
            "text": p.read_text(encoding="utf-8", errors="ignore"),
            "path": str(p),
        })
    return chapters


# Signals to track in the dashboard. Each maps a display name to the
# audit-result path; direction tells whether negative z = compression
# (lower is bad) or positive z = compression (higher is bad).
DASHBOARD_SIGNALS: list[tuple[str, tuple[str, ...], str]] = [
    ("burst_B",       ("tier1", "sentence_length", "burstiness_B"),       "lt"),
    ("sent_sd",       ("tier1", "sentence_length", "sd"),                 "lt"),
    ("MATTR",         ("tier1", "mattr", "value"),                        "lt"),
    ("MTLD",          ("tier1", "mtld",),                                 "lt"),
    ("Yule_K",        ("tier1", "yules_k",),                              "gt"),
    ("entropy",       ("tier1", "shannon_entropy_bits",),                 "lt"),
    ("FKGL_sd",       ("tier1", "fkgl", "sd"),                            "lt"),
    ("conn_dens",     ("tier1", "connective_density", "per_1000_tokens"), "gt"),
    ("fw_ratio",      ("tier1", "function_words", "function_word_ratio"), "gt"),
    ("MDD_sd",        ("tier2", "mdd", "sd"),                             "lt"),
    ("adj_cos_mean",  ("tier3", "adjacent_cosine", "mean"),               "gt"),
    ("adj_cos_sd",    ("tier3", "adjacent_cosine", "sd"),                 "lt"),
]


def get_path(d: Any, path: tuple[str, ...]) -> float | None:
    """Walk dict by tuple path; return None if any link missing."""
    cur: Any = d
    for k in path:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(k)
        if cur is None:
            return None
    if isinstance(cur, (int, float)):
        return float(cur)
    return None


def z_score(value: float, mean: float, sd: float) -> float | None:
    if sd == 0:
        return None
    return (value - mean) / sd


def aggregate_baseline_stats(baseline_audits: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    """For each dashboard signal, compute (mean, sd) across baseline files."""
    out: dict[str, dict[str, float]] = {}
    for name, path, _direction in DASHBOARD_SIGNALS:
        vals = []
        for entry in baseline_audits:
            v = get_path(entry.get("audit", {}), path)
            if v is not None:
                vals.append(v)
        if len(vals) >= 2:
            out[name] = {
                "mean": statistics.mean(vals),
                "sd": statistics.stdev(vals),
                "n": len(vals),
            }
        elif len(vals) == 1:
            out[name] = {"mean": vals[0], "sd": 0.0, "n": 1}
    return out


def audit_manuscript(
    chapters: list[dict[str, Any]],
    baseline_dir: str | None,
    *,
    do_tier2: bool = True,
    do_tier3: bool = True,
) -> dict[str, Any]:
    """Run audit_text on each chapter; aggregate baseline; compute z-scores."""
    chapter_audits = []
    for ch in chapters:
        a = audit_text(ch["text"], do_tier2=do_tier2, do_tier3=do_tier3)
        comp = classify_compression(a)
        chapter_audits.append({
            "label": ch["label"],
            "n_words": a.get("summary", {}).get("n_words", 0),
            "audit": a,
            "compression": comp,
        })

    baseline_stats: dict[str, dict[str, float]] = {}
    n_baseline_files = 0
    if baseline_dir:
        baseline_block = audit_baseline(baseline_dir, do_tier2=do_tier2, do_tier3=do_tier3)
        n_baseline_files = baseline_block.get("n_files", 0)
        baseline_stats = aggregate_baseline_stats(baseline_block.get("audits", []))

    # Per-chapter z-scores
    for ch in chapter_audits:
        z = {}
        for name, path, _direction in DASHBOARD_SIGNALS:
            val = get_path(ch["audit"], path)
            if val is None or name not in baseline_stats:
                continue
            stats = baseline_stats[name]
            if stats["sd"] == 0 or stats["n"] < 2:
                continue
            z[name] = {
                "value": val,
                "z": (val - stats["mean"]) / stats["sd"],
                "baseline_mean": stats["mean"],
                "baseline_sd": stats["sd"],
            }
        ch["z_scores"] = z

    return {
        "n_chapters": len(chapter_audits),
        "n_baseline_files": n_baseline_files,
        "chapters": chapter_audits,
        "baseline_stats": baseline_stats,
    }


def manuscript_summary(result: dict[str, Any]) -> dict[str, Any]:
    """Compute manuscript-wide observations: which signals deviate consistently,
    which chapters are outliers."""
    chapters = result["chapters"]
    chapter_count = len(chapters)
    if chapter_count == 0:
        return {"signal_summary": {}, "outliers": []}

    # For each signal: how many chapters had |z| > 1.0 in the compression direction?
    signal_summary: dict[str, dict[str, Any]] = {}
    for name, _path, direction in DASHBOARD_SIGNALS:
        compressed_count = 0
        z_values = []
        for ch in chapters:
            if name not in ch.get("z_scores", {}):
                continue
            z = ch["z_scores"][name]["z"]
            z_values.append(z)
            # Compression-direction check: lt means lower-than-baseline = compressed
            if direction == "lt" and z < -1.0:
                compressed_count += 1
            elif direction == "gt" and z > 1.0:
                compressed_count += 1
        if z_values:
            signal_summary[name] = {
                "compressed_chapters": compressed_count,
                "total_chapters": len(z_values),
                "fraction": compressed_count / len(z_values),
                "mean_z": statistics.mean(z_values),
                "max_abs_z": max(abs(z) for z in z_values),
            }

    # Outlier chapters: count number of |z| > 1.5 signals per chapter
    outliers = []
    for ch in chapters:
        flagged = []
        z_count = 0
        for name, _path, direction in DASHBOARD_SIGNALS:
            if name not in ch.get("z_scores", {}):
                continue
            z = ch["z_scores"][name]["z"]
            z_count += 1
            if direction == "lt" and z < -1.5:
                flagged.append((name, z, "compressed"))
            elif direction == "gt" and z > 1.5:
                flagged.append((name, z, "compressed"))
            elif direction == "lt" and z > 1.5:
                flagged.append((name, z, "elevated"))
            elif direction == "gt" and z < -1.5:
                flagged.append((name, z, "elevated"))
        outliers.append({
            "label": ch["label"],
            "n_words": ch["n_words"],
            "n_signals_evaluated": z_count,
            "flagged": flagged,
            "flag_count": len(flagged),
        })
    outliers.sort(key=lambda x: x["flag_count"], reverse=True)

    return {
        "signal_summary": signal_summary,
        "outliers": outliers,
    }


# ---------- Output formatting ----------

def fmt_z(z: float | None) -> str:
    if z is None:
        return "  --  "
    s = f"{z:+5.2f}"
    return s


def render_dashboard(result: dict[str, Any]) -> str:
    """Markdown dashboard: rows are chapters, columns are signals."""
    chapters = result["chapters"]
    if not chapters:
        return "No chapters found."

    lines = []
    lines.append("# Manuscript Variance Audit")
    lines.append("")
    lines.append(f"**Chapters analyzed:** {len(chapters)}")
    if result["n_baseline_files"]:
        lines.append(f"**Baseline files:** {result['n_baseline_files']}")
    lines.append("")
    lines.append("## Per-chapter signal dashboard")
    lines.append("")
    lines.append("Z-scores against personal baseline. Bold = |z| > 1.0 in the compression "
                 "direction. Negative z on `lt`-direction signals (MATTR, MTLD, FKGL_sd, "
                 "etc.) and positive z on `gt`-direction signals (Yule_K, conn_dens, "
                 "fw_ratio, adj_cos_mean) indicate compression vs. baseline.")
    lines.append("")

    # Header
    cols = [name for name, _, _ in DASHBOARD_SIGNALS]
    header = "| chapter | n_words | " + " | ".join(cols) + " |"
    lines.append(header)
    lines.append("|" + "---|" * (len(cols) + 2))

    direction_map = {name: direction for name, _, direction in DASHBOARD_SIGNALS}

    for ch in chapters:
        cells = [ch["label"], str(ch["n_words"])]
        for name in cols:
            zinfo = ch.get("z_scores", {}).get(name)
            if zinfo is None:
                cells.append("--")
                continue
            z = zinfo["z"]
            direction = direction_map[name]
            compressed = (direction == "lt" and z < -1.0) or (direction == "gt" and z > 1.0)
            cell = f"{z:+.2f}"
            if compressed:
                cell = f"**{cell}**"
            cells.append(cell)
        lines.append("| " + " | ".join(cells) + " |")
    lines.append("")

    # Manuscript-wide signal summary
    summary = manuscript_summary(result)
    lines.append("## Manuscript-wide patterns")
    lines.append("")
    lines.append("Signals that fire on multiple chapters indicate manuscript-wide "
                 "compression rather than chapter-specific issues.")
    lines.append("")
    lines.append("| signal | compressed_chapters / total | fraction | mean z | max |z| |")
    lines.append("|---|---|---|---|---|")
    sig_items = sorted(summary["signal_summary"].items(),
                       key=lambda x: x[1]["fraction"], reverse=True)
    for name, info in sig_items:
        if info["total_chapters"] == 0:
            continue
        marker = ""
        if info["fraction"] >= 0.5:
            marker = " ⚠"
        lines.append(
            f"| {name} | {info['compressed_chapters']} / {info['total_chapters']} | "
            f"{info['fraction']:.2f}{marker} | {info['mean_z']:+.2f} | "
            f"{info['max_abs_z']:.2f} |"
        )
    lines.append("")
    flagged_signals = [name for name, info in summary["signal_summary"].items()
                       if info["fraction"] >= 0.5]
    if flagged_signals:
        lines.append(
            f"**Manuscript-wide signal:** {', '.join(flagged_signals)} — these signals are "
            f"compressed in at least half of all chapters. Treat as a manuscript-level pattern, "
            f"not chapter-specific."
        )
        lines.append("")

    # Outlier chapters
    lines.append("## Outlier chapters")
    lines.append("")
    lines.append("Chapters with the most |z| > 1.5 signals. These chapters deviate "
                 "most from baseline and are first candidates for revision.")
    lines.append("")
    lines.append("| chapter | n_words | flag_count | top flagged signals |")
    lines.append("|---|---|---|---|")
    for ch in summary["outliers"][:10]:
        if ch["flag_count"] == 0:
            continue
        flagged = sorted(ch["flagged"], key=lambda x: abs(x[1]), reverse=True)
        flagged_str = ", ".join(f"{name} ({z:+.2f})" for name, z, _kind in flagged[:5])
        lines.append(f"| {ch['label']} | {ch['n_words']} | {ch['flag_count']} | {flagged_str} |")
    lines.append("")

    return "\n".join(lines)


# ---------- CLI ----------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Cross-chapter Layer A variance audit for a manuscript."
    )
    parser.add_argument(
        "manuscript",
        nargs="?",
        help="Path to a single manuscript file with chapter markers (.md, .txt)."
    )
    parser.add_argument(
        "--chapter-dir",
        help="Alternative: directory of chapter files (.txt or .md), one chapter per file."
    )
    parser.add_argument(
        "--baseline-dir",
        help="Optional baseline corpus directory for z-score comparison."
    )
    parser.add_argument(
        "--chapter-pattern",
        default=r"^#+\s*Chapter\s+\d+",
        help="Regex pattern for chapter markers (default: '^#+\\s*Chapter\\s+\\d+')."
    )
    parser.add_argument(
        "--no-tier2", action="store_true",
        help="Skip Tier 2 metrics (POS bigrams, MDD)."
    )
    parser.add_argument(
        "--no-tier3", action="store_true",
        help="Skip Tier 3 metrics (adjacent-sentence cosine)."
    )
    parser.add_argument("--json", action="store_true", help="Output JSON instead of markdown.")
    parser.add_argument("--out", help="Write output to file instead of stdout.")

    args = parser.parse_args()

    if not args.manuscript and not args.chapter_dir:
        parser.error("Provide either a manuscript file or --chapter-dir.")

    if args.manuscript:
        text = Path(args.manuscript).read_text(encoding="utf-8", errors="ignore")
        chapters = split_manuscript(text, args.chapter_pattern)
    else:
        chapters = load_chapter_dir(args.chapter_dir)

    if not chapters:
        print("No chapters detected.", file=sys.stderr)
        return 1

    result = audit_manuscript(
        chapters,
        args.baseline_dir,
        do_tier2=not args.no_tier2,
        do_tier3=not args.no_tier3,
    )

    if args.json:
        # Strip large nested audit fields for cleaner JSON output
        for ch in result["chapters"]:
            ch.pop("audit", None)
        output = json.dumps(result, indent=2, default=str)
    else:
        output = render_dashboard(result)

    if args.out:
        Path(args.out).write_text(output, encoding="utf-8")
        print(f"Written to {args.out}", file=sys.stderr)
    else:
        print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
