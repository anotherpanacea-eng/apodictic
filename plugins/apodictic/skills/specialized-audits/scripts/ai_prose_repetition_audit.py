#!/usr/bin/env python3
"""
repetition_audit.py
Vocabulary repetition diagnostic.

Surfaces words a writer is using more than expected against their own
baseline, plus within-text clustering. Designed to support the
vocabulary-restoration revision pass when Layer A flags lexical
compression (MATTR / MTLD against personal baseline).

Usage:
    python3 repetition_audit.py TARGET.md --baseline-dir BASELINE_DIR
    python3 repetition_audit.py TARGET.md --baseline-dir BASELINE_DIR --top 50
    python3 repetition_audit.py TARGET.md --baseline-dir BASELINE_DIR \\
        --anchors anchors.txt --json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

# Common English function words (excluded by default; not vocabulary-restoration targets)
DEFAULT_FUNCTION_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an",
    "and", "any", "are", "as", "at", "back", "be", "because", "been",
    "before", "being", "below", "between", "both", "but", "by", "came",
    "can", "come", "could", "did", "do", "does", "doing", "done", "down",
    "during", "each", "even", "every", "few", "for", "from", "further",
    "get", "go", "got", "had", "has", "have", "having", "he", "her",
    "here", "hers", "herself", "him", "himself", "his", "how", "i", "if",
    "in", "into", "is", "it", "its", "itself", "just", "know", "like",
    "made", "make", "many", "me", "might", "mine", "more", "most", "must",
    "my", "myself", "no", "nor", "not", "now", "of", "off", "on", "once",
    "one", "only", "or", "other", "ought", "our", "ours", "ourselves",
    "out", "over", "own", "right", "said", "same", "say", "says", "see",
    "she", "should", "so", "some", "such", "than", "that", "the", "their",
    "theirs", "them", "themselves", "then", "there", "these", "they",
    "this", "those", "through", "to", "too", "under", "until", "up",
    "upon", "us", "very", "was", "we", "well", "were", "what", "when",
    "where", "which", "while", "who", "whom", "whose", "why", "will",
    "with", "would", "yet", "you", "your", "yours", "yourself",
    "yourselves", "also", "ever", "still", "never", "always", "often",
    "much", "two", "three", "first", "second", "third", "last", "new",
    "old", "good", "fine", "okay", "yeah", "oh", "ah", "hm", "mm", "uh",
    "um", "yes", "nothing", "something", "someone", "anyone", "everyone",
    "everything", "anything", "way", "time", "day", "night", "year",
    "years", "thing", "things", "going", "gonna", "want", "wanted",
    "wanting", "wants", "need", "needed", "needs", "needing", "take",
    "took", "taken", "taking", "takes", "seem", "seemed", "seems",
    "seeming", "look", "looked", "looking", "looks", "feel", "felt",
    "feels", "feeling", "makes", "making", "sit", "sat", "sitting",
    "stood", "stand", "standing", "stands", "walked", "walks", "walking",
    "walk", "getting", "gets", "gave", "give", "giving", "gives", "kept",
    "keep", "keeping", "keeps", "let", "letting", "lets", "put",
    "putting", "puts", "told", "tell", "telling", "tells", "saying",
    "asked", "asks", "asking", "ask", "comes", "coming", "went", "goes",
    "turned", "turning", "turns", "turn", "moved", "moves", "moving",
    "move", "watched", "watching", "watches", "watch", "heard", "hears",
    "hearing", "hear", "saw", "seen", "sees", "seeing", "big", "small",
    "little", "long", "short", "high", "low", "real", "maybe",
}

WORD_RE = re.compile(r"[A-Za-z']+")


def tokenize(text: str) -> list[str]:
    return [w.lower() for w in WORD_RE.findall(text)]


def load_anchors(path: str | None) -> set[str]:
    if not path:
        return set()
    text = Path(path).read_text(encoding="utf-8", errors="ignore")
    return {w.strip().lower() for w in re.split(r"[,\s]+", text) if w.strip()}


def cluster_max(tokens: list[str], target: str, window: int = 300) -> int:
    """Maximum occurrences of target in any sliding window of `window` tokens."""
    if not tokens:
        return 0
    indicators = [1 if w == target else 0 for w in tokens]
    if len(indicators) < window:
        return sum(indicators)
    cur = sum(indicators[:window])
    best = cur
    for i in range(window, len(indicators)):
        cur += indicators[i] - indicators[i - window]
        if cur > best:
            best = cur
    return best


def find_repetitions(
    target_text: str,
    baseline_paths: list[Path],
    *,
    function_words: set[str],
    anchor_words: set[str],
    min_count: int = 3,
    min_word_len: int = 4,
    cluster_window: int = 300,
    smoothing: float = 0.05,
    per: float = 1000.0,
) -> list[dict]:
    """Find words over-represented in target vs. baseline corpus."""
    target_tokens = tokenize(target_text)
    target_n = len(target_tokens)
    if target_n == 0:
        return []
    target_counts = Counter(target_tokens)

    # Aggregate baseline
    base_tokens: list[str] = []
    for p in baseline_paths:
        try:
            base_tokens.extend(tokenize(p.read_text(encoding="utf-8", errors="ignore")))
        except Exception:
            continue
    base_n = len(base_tokens)
    base_counts = Counter(base_tokens)

    skip = function_words | anchor_words
    candidates = []
    for word, c in target_counts.items():
        if word in skip:
            continue
        if len(word) < min_word_len:
            continue
        if c < min_count:
            continue
        target_freq = (c / target_n) * per
        base_freq = (base_counts.get(word, 0) / max(base_n, 1)) * per
        smoothed_base = max(base_freq, smoothing)
        ratio = target_freq / smoothed_base
        cmax = cluster_max(target_tokens, word, cluster_window)
        candidates.append({
            "word": word,
            "count": c,
            "per_1000": round(target_freq, 3),
            "baseline_per_1000": round(base_freq, 3),
            "ratio": round(ratio, 1),
            "cluster_max": cmax,
            "cluster_window": cluster_window,
        })
    candidates.sort(key=lambda x: (x["ratio"], x["count"]), reverse=True)
    return candidates


def render_report(
    candidates: list[dict],
    target_label: str,
    target_words: int,
    top_n: int,
) -> str:
    lines = []
    lines.append(f"# Vocabulary Repetition Audit: {target_label}")
    lines.append("")
    lines.append(f"**Target word count:** {target_words}")
    lines.append(f"**Candidates surfaced:** {len(candidates)} (showing top {top_n})")
    lines.append("")
    lines.append("## Words over-represented vs. baseline")
    lines.append("")
    lines.append(
        "Higher `ratio` = more over-represented relative to baseline. "
        "Higher `cluster_max` = more occurrences in a single sliding window. "
        "Words appearing in both lists are the strongest candidates for varying."
    )
    lines.append("")
    lines.append("| word | count | per_1k | base_per_1k | ratio | cluster_max |")
    lines.append("|---|---|---|---|---|---|")
    for c in candidates[:top_n]:
        lines.append(
            f"| {c['word']} | {c['count']} | {c['per_1000']} | "
            f"{c['baseline_per_1000']} | {c['ratio']:.1f} | {c['cluster_max']} |"
        )
    lines.append("")

    # Cluster-sorted view
    cluster_sorted = sorted(candidates, key=lambda x: x["cluster_max"], reverse=True)
    cluster_window = candidates[0]["cluster_window"] if candidates else 300
    clustered = [c for c in cluster_sorted if c["cluster_max"] >= 3][:15]
    if clustered:
        lines.append(f"## Words clustering within a {cluster_window}-token window")
        lines.append("")
        lines.append("Words that recur within a single passage rather than spread evenly. "
                     "Strongest candidates for varying within local context.")
        lines.append("")
        lines.append("| word | cluster_max | total_count | ratio |")
        lines.append("|---|---|---|---|")
        for c in clustered:
            lines.append(
                f"| {c['word']} | {c['cluster_max']} | {c['count']} | {c['ratio']:.1f} |"
            )
        lines.append("")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Surface vocabulary over-representation and clustering vs. a baseline."
    )
    parser.add_argument("target", help="Target text file (.md or .txt).")
    parser.add_argument(
        "--baseline-dir",
        required=True,
        help="Baseline corpus directory (.txt or .md files)."
    )
    parser.add_argument("--top", type=int, default=30,
                        help="How many candidates to display (default 30).")
    parser.add_argument("--min-count", type=int, default=3,
                        help="Minimum occurrences in target for a word to be considered.")
    parser.add_argument("--min-word-len", type=int, default=4,
                        help="Minimum word length to consider (default 4; skips short words).")
    parser.add_argument("--cluster-window", type=int, default=300,
                        help="Token window for clustering check (default 300).")
    parser.add_argument(
        "--anchors",
        help="Path to a file listing project-anchor words to exclude (one per line "
             "or whitespace/comma-separated). Use this for character names, "
             "scene-anchored objects, etc."
    )
    parser.add_argument("--json", action="store_true", help="Output JSON.")
    parser.add_argument("--out", help="Write output to file instead of stdout.")
    parser.add_argument(
        "--include-function-words", action="store_true",
        help="Don't filter common function words (rarely useful)."
    )
    args = parser.parse_args()

    target_path = Path(args.target)
    target_text = target_path.read_text(encoding="utf-8", errors="ignore")
    target_words = len(tokenize(target_text))

    baseline_paths = sorted(Path(args.baseline_dir).glob("*.txt")) + \
                     sorted(Path(args.baseline_dir).glob("*.md"))
    if not baseline_paths:
        print(f"No .txt or .md files in {args.baseline_dir}", file=sys.stderr)
        return 1

    function_words = set() if args.include_function_words else DEFAULT_FUNCTION_WORDS
    anchor_words = load_anchors(args.anchors)

    candidates = find_repetitions(
        target_text,
        baseline_paths,
        function_words=function_words,
        anchor_words=anchor_words,
        min_count=args.min_count,
        min_word_len=args.min_word_len,
        cluster_window=args.cluster_window,
    )

    if args.json:
        output = json.dumps({
            "target": str(target_path),
            "target_words": target_words,
            "baseline_files": [str(p) for p in baseline_paths],
            "candidates": candidates,
        }, indent=2)
    else:
        output = render_report(candidates, target_path.name, target_words, args.top)

    if args.out:
        Path(args.out).write_text(output, encoding="utf-8")
        print(f"Written to {args.out}", file=sys.stderr)
    else:
        print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
