#!/usr/bin/env python3
"""
stylometry_core.py
Reusable stylometric feature extraction and baseline-distance utilities.

This module is intentionally separate from variance_audit.py. The variance
audit asks "is this prose distributionally smoothed?" These helpers ask
"how far is this text from a writer/register baseline?"
"""

from __future__ import annotations

import json
import math
import re
import statistics
from collections import Counter
from pathlib import Path
from typing import Any

from ai_prose_variance_audit import (  # type: ignore
    FUNCTION_WORDS,
    HAS_SPACY,
    _NLP,
    split_sentences,
    split_words,
)


WORD_RE = re.compile(r"[A-Za-z']+")
CONTRACTION_RE = re.compile(
    r"\b(?:"
    r"[a-z]+(?:n't|'re|'ve|'ll|'d|'m)"
    r"|(?:it|that|there|here|what|who|where|when|why|how|let)'s"
    r"|(?:he|she|one|everyone|everybody|someone|somebody|anyone|anybody|nobody|nothing)'s"
    r"|can't|cannot|won't|shan't"
    r")\b",
    re.I,
)
DOUBLE_QUOTE_RE = re.compile(r'"([^"]+)"')
CURLY_QUOTE_RE = re.compile(r"\u201c([^\u201d]+)\u201d")

FIRST_PERSON_SINGULAR = {"i", "me", "my", "mine", "myself"}
FIRST_PERSON_PLURAL = {"we", "us", "our", "ours", "ourselves"}
SECOND_PERSON = {"you", "your", "yours", "yourself", "yourselves"}
THIRD_PERSON_SINGULAR = {
    "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself"
}
THIRD_PERSON_PLURAL = {"they", "them", "their", "theirs", "themselves"}
MODALS = {"can", "could", "may", "might", "must", "shall", "should", "will", "would"}
NEGATIONS = {
    "no", "not", "never", "none", "nothing", "neither", "nor", "cannot",
    "can't", "won't", "shan't", "isn't", "aren't", "wasn't", "weren't",
    "don't", "doesn't", "didn't", "haven't", "hasn't", "hadn't", "wouldn't",
    "couldn't", "shouldn't", "mightn't", "mustn't",
}
HEDGES = {
    "almost", "apparently", "arguably", "basically", "fairly", "generally",
    "kind", "likely", "maybe", "mostly", "perhaps", "possibly", "probably",
    "quite", "rather", "relatively", "seem", "seemed", "seeming", "seems",
    "somewhat", "sort", "tend", "tended", "tends",
}

FIXED_FAMILIES = {
    "punctuation",
    "paragraph_dialogue",
    "pronoun_modal_negation",
}

DEFAULT_LIMITS = {
    "function_words": 100,
    "char_ngrams": 500,
    "pos_trigrams": 300,
    "dependency_ngrams": 300,
}

FAMILY_WEIGHTS = {
    "function_words": 2.0,
    "char_ngrams": 1.5,
    "punctuation": 1.0,
    "paragraph_dialogue": 1.0,
    "pronoun_modal_negation": 1.0,
    "pos_trigrams": 1.0,
    "dependency_ngrams": 1.0,
}

OVERALL_FAMILY_DELTA_CAP = 5.0
PROVISIONAL_BAND_NOTE = "provisional thresholds; calibration pending"


def read_text(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8", errors="ignore")


def word_tokens(text: str) -> list[str]:
    return [w.lower() for w in WORD_RE.findall(text)]


def paragraphs(text: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n+", text) if p.strip()]


def per_1000(count: float, total: int) -> float:
    if total <= 0:
        return 0.0
    return (count / total) * 1000.0


def per_100(count: float, total: int) -> float:
    if total <= 0:
        return 0.0
    return (count / total) * 100.0


def safe_mean(values: list[float]) -> float:
    return statistics.mean(values) if values else 0.0


def safe_sd(values: list[float]) -> float:
    return statistics.stdev(values) if len(values) > 1 else 0.0


def normalize_for_char_ngrams(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def frequencies(counter: Counter[str], total: int) -> dict[str, float]:
    if total <= 0:
        return {}
    return {k: v / total for k, v in counter.items()}


def function_word_features(words: list[str]) -> dict[str, float]:
    total = len(words)
    counts = Counter(w for w in words if w in FUNCTION_WORDS)
    return {w: counts.get(w, 0) / total if total else 0.0 for w in sorted(FUNCTION_WORDS)}


def char_ngram_features(text: str, ns: tuple[int, ...] = (3, 4, 5)) -> dict[str, float]:
    normalized = normalize_for_char_ngrams(text)
    counts: Counter[str] = Counter()
    total = 0
    for n in ns:
        if len(normalized) < n:
            continue
        for i in range(0, len(normalized) - n + 1):
            gram = normalized[i:i + n]
            counts[f"ch{n}:{gram}"] += 1
            total += 1
    return frequencies(counts, total)


def punctuation_features(text: str, words: list[str], sentences: list[str]) -> dict[str, float]:
    n_words = len(words)
    n_sentences = max(len(sentences), 1)
    dash_count = text.count("--") + text.count("\u2014") + text.count("\u2013")
    ellipsis_count = text.count("...") + text.count("\u2026")
    quote_marks = text.count('"') + text.count("\u201c") + text.count("\u201d")
    terminal = text.count(".") + text.count("?") + text.count("!")
    punct_total = sum(1 for ch in text if ch in ".,;:!?()[]{}\"'")
    punct_total += dash_count + ellipsis_count
    return {
        "punct_per_100_words": per_100(punct_total, n_words),
        "comma_per_100_words": per_100(text.count(","), n_words),
        "semicolon_per_100_words": per_100(text.count(";"), n_words),
        "colon_per_100_words": per_100(text.count(":"), n_words),
        "dash_per_100_words": per_100(dash_count, n_words),
        "ellipsis_per_100_words": per_100(ellipsis_count, n_words),
        "paren_pair_per_100_words": per_100(min(text.count("("), text.count(")")), n_words),
        "quote_mark_per_100_words": per_100(quote_marks, n_words),
        "question_per_100_sentences": per_100(text.count("?"), n_sentences),
        "exclamation_per_100_sentences": per_100(text.count("!"), n_sentences),
        "terminal_punct_per_sentence": terminal / n_sentences if n_sentences else 0.0,
    }


def quoted_spans(text: str) -> list[str]:
    spans = [m.group(1) for m in DOUBLE_QUOTE_RE.finditer(text)]
    spans.extend(m.group(1) for m in CURLY_QUOTE_RE.finditer(text))
    return spans


def paragraph_dialogue_features(text: str, words: list[str], paras: list[str]) -> dict[str, float]:
    n_words = len(words)
    para_lengths = [len(split_words(p)) for p in paras]
    dialogue_paras = []
    for p in paras:
        p_words = split_words(p)
        p_quoted_words = sum(len(split_words(s)) for s in quoted_spans(p))
        quoted_ratio = p_quoted_words / len(p_words) if p_words else 0.0
        if p.lstrip().startswith(('"', "\u201c", "'")) or quoted_ratio >= 0.6:
            dialogue_paras.append(p)
    spans = quoted_spans(text)
    quoted_words = sum(len(split_words(s)) for s in spans)
    return {
        "paragraph_count_per_1000_words": per_1000(len(paras), n_words),
        "paragraph_words_mean": safe_mean([float(x) for x in para_lengths]),
        "paragraph_words_sd": safe_sd([float(x) for x in para_lengths]),
        "short_paragraph_ratio": (
            sum(1 for x in para_lengths if x <= 25) / len(para_lengths) if para_lengths else 0.0
        ),
        "dialogue_paragraph_ratio": (
            len(dialogue_paras) / len(paras) if paras else 0.0
        ),
        "quoted_word_ratio": quoted_words / n_words if n_words else 0.0,
        "quote_span_words_mean": safe_mean([float(len(split_words(s))) for s in spans]),
    }


def pronoun_modal_negation_features(text: str, words: list[str]) -> dict[str, float]:
    counts = Counter(words)
    n_words = len(words)
    contraction_count = len(CONTRACTION_RE.findall(text.lower()))
    return {
        "contractions_per_1000": per_1000(contraction_count, n_words),
        "first_person_singular_per_1000": per_1000(
            sum(counts.get(w, 0) for w in FIRST_PERSON_SINGULAR), n_words
        ),
        "first_person_plural_per_1000": per_1000(
            sum(counts.get(w, 0) for w in FIRST_PERSON_PLURAL), n_words
        ),
        "second_person_per_1000": per_1000(
            sum(counts.get(w, 0) for w in SECOND_PERSON), n_words
        ),
        "third_person_singular_per_1000": per_1000(
            sum(counts.get(w, 0) for w in THIRD_PERSON_SINGULAR), n_words
        ),
        "third_person_plural_per_1000": per_1000(
            sum(counts.get(w, 0) for w in THIRD_PERSON_PLURAL), n_words
        ),
        "modal_per_1000": per_1000(sum(counts.get(w, 0) for w in MODALS), n_words),
        "negation_per_1000": per_1000(sum(counts.get(w, 0) for w in NEGATIONS), n_words),
        "hedge_per_1000": per_1000(sum(counts.get(w, 0) for w in HEDGES), n_words),
    }


def pos_trigram_features(text: str) -> dict[str, float]:
    if not HAS_SPACY or _NLP is None:
        return {}
    doc = _NLP(text)
    counts: Counter[str] = Counter()
    total = 0
    for sent in doc.sents:
        tags = [t.pos_ for t in sent if not t.is_space]
        for a, b, c in zip(tags, tags[1:], tags[2:]):
            counts[f"pos:{a}-{b}-{c}"] += 1
            total += 1
    return frequencies(counts, total)


def dependency_ngram_features(text: str, ns: tuple[int, ...] = (2, 3)) -> dict[str, float]:
    if not HAS_SPACY or _NLP is None:
        return {}
    doc = _NLP(text)
    counts: Counter[str] = Counter()
    total = 0
    for sent in doc.sents:
        labels = [t.dep_ for t in sent if not t.is_space]
        for n in ns:
            for gram in zip(*(labels[i:] for i in range(n))):
                counts[f"dep{n}:{'-'.join(gram)}"] += 1
                total += 1
    return frequencies(counts, total)


def extract_features(text: str, *, include_spacy: bool = True) -> dict[str, Any]:
    words = word_tokens(text)
    sentences = split_sentences(text)
    paras = paragraphs(text)
    features = {
        "function_words": function_word_features(words),
        "char_ngrams": char_ngram_features(text),
        "punctuation": punctuation_features(text, words, sentences),
        "paragraph_dialogue": paragraph_dialogue_features(text, words, paras),
        "pronoun_modal_negation": pronoun_modal_negation_features(text, words),
    }
    if include_spacy:
        pos = pos_trigram_features(text)
        dep = dependency_ngram_features(text)
        if pos:
            features["pos_trigrams"] = pos
        if dep:
            features["dependency_ngrams"] = dep
    return {
        "summary": {
            "n_words": len(words),
            "n_sentences": len(sentences),
            "n_paragraphs": len(paras),
            "spacy_available": HAS_SPACY,
        },
        "features": features,
    }


def load_entries_from_dir(directory: str | Path) -> list[dict[str, Any]]:
    base = Path(directory)
    paths = sorted(base.glob("*.txt")) + sorted(base.glob("*.md"))
    entries = []
    for path in paths:
        if path.name.startswith(".") or path.name.lower().startswith("readme"):
            continue
        entries.append({
            "id": path.stem,
            "path": str(path),
            "text": read_text(path),
            "metadata": {"source": "directory"},
        })
    return entries


def _matches_filter(value: Any, expected: str | None) -> bool:
    if expected is None:
        return True
    if isinstance(value, list):
        return expected in {str(v) for v in value}
    return str(value) == expected


def load_entries_from_manifest(
    manifest_path: str | Path,
    *,
    use: str | None = "baseline",
    split: str | None = None,
    register: str | None = None,
    persona: str | None = None,
    ai_status: str | None = "pre_ai_human",
) -> list[dict[str, Any]]:
    manifest = Path(manifest_path)
    entries = []
    for lineno, line in enumerate(manifest.read_text(encoding="utf-8").splitlines(), start=1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        item = json.loads(line)
        if not _matches_filter(item.get("use"), use):
            continue
        if not _matches_filter(item.get("split"), split):
            continue
        if not _matches_filter(item.get("register"), register):
            continue
        if not _matches_filter(item.get("persona"), persona):
            continue
        if not _matches_filter(item.get("ai_status"), ai_status):
            continue
        raw_path = item.get("path")
        if not raw_path:
            raise ValueError(f"Manifest line {lineno} is missing path")
        path = resolve_manifest_path(manifest, raw_path)
        entries.append({
            "id": item.get("id") or path.stem,
            "path": str(path),
            "text": read_text(path),
            "metadata": item,
        })
    return entries


def resolve_manifest_path(manifest: Path, raw_path: str) -> Path:
    path = Path(raw_path)
    if path.is_absolute():
        return path

    candidates = [
        manifest.parent / path,
        manifest.parent.parent / path,
        Path.cwd() / path,
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


def load_entries(
    *,
    baseline_dir: str | None = None,
    manifest: str | None = None,
    use: str | None = "baseline",
    split: str | None = None,
    register: str | None = None,
    persona: str | None = None,
    ai_status: str | None = "pre_ai_human",
) -> list[dict[str, Any]]:
    if manifest:
        return load_entries_from_manifest(
            manifest,
            use=use,
            split=split,
            register=register,
            persona=persona,
            ai_status=ai_status,
        )
    if baseline_dir:
        return load_entries_from_dir(baseline_dir)
    raise ValueError("Provide either baseline_dir or manifest")


def extract_entry_features(entries: list[dict[str, Any]], *, include_spacy: bool = True) -> list[dict[str, Any]]:
    out = []
    for entry in entries:
        feat = extract_features(entry["text"], include_spacy=include_spacy)
        out.append({
            "id": entry["id"],
            "path": entry["path"],
            "metadata": entry.get("metadata", {}),
            "summary": feat["summary"],
            "features": feat["features"],
        })
    return out


def select_feature_names(
    baseline_features: list[dict[str, Any]],
    *,
    limits: dict[str, int] | None = None,
) -> dict[str, list[str]]:
    limits = {**DEFAULT_LIMITS, **(limits or {})}
    families: set[str] = set()
    for item in baseline_features:
        families.update(item.get("features", {}).keys())

    selected: dict[str, list[str]] = {}
    for family in sorted(families):
        aggregate: Counter[str] = Counter()
        for item in baseline_features:
            aggregate.update(item.get("features", {}).get(family, {}))
        if not aggregate:
            continue
        if family in FIXED_FAMILIES:
            selected[family] = sorted(aggregate.keys())
        else:
            limit = limits.get(family, 300)
            selected[family] = [name for name, _value in aggregate.most_common(limit)]
    return selected


def feature_vector(item: dict[str, Any], family: str, names: list[str]) -> dict[str, float]:
    data = item.get("features", {}).get(family, {})
    return {name: float(data.get(name, 0.0)) for name in names}


def vector_stats(vectors: list[dict[str, float]], names: list[str]) -> dict[str, dict[str, float]]:
    stats: dict[str, dict[str, float]] = {}
    for name in names:
        values = [float(v.get(name, 0.0)) for v in vectors]
        stats[name] = {
            "mean": safe_mean(values),
            "sd": safe_sd(values),
            "n": len(values),
        }
    return stats


def cosine_distance(a: dict[str, float], b: dict[str, float], names: list[str]) -> float | None:
    dot = 0.0
    norm_a = 0.0
    norm_b = 0.0
    for name in names:
        av = float(a.get(name, 0.0))
        bv = float(b.get(name, 0.0))
        dot += av * bv
        norm_a += av * av
        norm_b += bv * bv
    if norm_a == 0 or norm_b == 0:
        return None
    return 1.0 - (dot / (math.sqrt(norm_a) * math.sqrt(norm_b)))


def family_distance(
    target: dict[str, Any],
    baseline_items: list[dict[str, Any]],
    family: str,
    names: list[str],
) -> dict[str, Any]:
    target_vec = feature_vector(target, family, names)
    baseline_vectors = [feature_vector(item, family, names) for item in baseline_items]
    stats = vector_stats(baseline_vectors, names)

    deviations = []
    z_values = []
    for name in names:
        info = stats[name]
        value = target_vec.get(name, 0.0)
        z = None
        if info["sd"] > 0:
            z = (value - info["mean"]) / info["sd"]
            z_values.append(abs(z))
        deviations.append({
            "feature": name,
            "value": value,
            "baseline_mean": info["mean"],
            "baseline_sd": info["sd"],
            "z": z,
            "abs_z": abs(z) if z is not None else None,
        })

    centroid = {name: stats[name]["mean"] for name in names}
    cosine_to_centroid = cosine_distance(target_vec, centroid, names)
    baseline_cosines = [
        c for c in (cosine_distance(target_vec, vec, names) for vec in baseline_vectors)
        if c is not None
    ]
    deviations.sort(
        key=lambda x: x["abs_z"] if x["abs_z"] is not None else -1.0,
        reverse=True,
    )
    return {
        "n_features": len(names),
        "burrows_delta": safe_mean(z_values),
        "cosine_distance_to_centroid": cosine_to_centroid,
        "cosine_distance_to_baseline_mean": safe_mean(baseline_cosines),
        "cosine_distance_to_baseline_min": min(baseline_cosines) if baseline_cosines else None,
        "top_deviations": deviations[:25],
    }


def compare_to_baseline(
    target_text: str,
    baseline_entries: list[dict[str, Any]],
    *,
    include_spacy: bool = True,
    limits: dict[str, int] | None = None,
) -> dict[str, Any]:
    if not baseline_entries:
        raise ValueError("Baseline contains no usable entries")

    target_features = extract_features(target_text, include_spacy=include_spacy)
    baseline_features = extract_entry_features(baseline_entries, include_spacy=include_spacy)
    selected = select_feature_names(baseline_features, limits=limits)
    target_item = {
        "id": "target",
        "path": None,
        "summary": target_features["summary"],
        "features": target_features["features"],
    }

    families = {}
    weighted_total = 0.0
    weight_sum = 0.0
    for family, names in selected.items():
        if family not in target_item["features"]:
            continue
        dist = family_distance(target_item, baseline_features, family, names)
        dist["overall_delta_contribution_cap"] = OVERALL_FAMILY_DELTA_CAP
        dist["capped_in_overall"] = dist["burrows_delta"] > OVERALL_FAMILY_DELTA_CAP
        families[family] = dist
        if dist["burrows_delta"] > 0:
            weight = FAMILY_WEIGHTS.get(family, 1.0)
            # One feature family can explode when source formatting differs
            # (especially paragraph preservation). Cap contributions to keep
            # the overall score a synthesis rather than a single-family veto.
            weighted_total += min(dist["burrows_delta"], OVERALL_FAMILY_DELTA_CAP) * weight
            weight_sum += weight

    overall_delta = weighted_total / weight_sum if weight_sum else 0.0
    warnings = comparison_warnings(target_features["summary"], baseline_entries, baseline_features)
    return {
        "target_summary": target_features["summary"],
        "baseline_summary": summarize_entries(baseline_features),
        "selected_features": {k: len(v) for k, v in selected.items()},
        "families": families,
        "warnings": warnings,
        "overall": {
            "weighted_delta": overall_delta,
            "band": voice_distance_band(overall_delta),
            "interpretation": voice_distance_interpretation(overall_delta),
            "threshold_note": PROVISIONAL_BAND_NOTE,
        },
    }


def summarize_entries(entries: list[dict[str, Any]]) -> dict[str, Any]:
    word_counts = [e.get("summary", {}).get("n_words", 0) for e in entries]
    metadata = [e.get("metadata", {}) for e in entries]
    registers = sorted({m.get("register") for m in metadata if m.get("register")})
    personas = sorted({m.get("persona") for m in metadata if m.get("persona")})
    privacy_values = sorted({m.get("privacy") for m in metadata if m.get("privacy")})
    return {
        "n_files": len(entries),
        "total_words": sum(word_counts),
        "mean_words": safe_mean([float(x) for x in word_counts]),
        "min_words": min(word_counts) if word_counts else 0,
        "max_words": max(word_counts) if word_counts else 0,
        "registers": registers,
        "personas": personas,
        "privacy_values": privacy_values,
        "files": [{"id": e["id"], "path": e["path"], "n_words": e["summary"]["n_words"]} for e in entries],
    }


def comparison_warnings(
    target_summary: dict[str, Any],
    baseline_entries: list[dict[str, Any]],
    baseline_features: list[dict[str, Any]],
) -> list[str]:
    warnings = []
    target_words = int(target_summary.get("n_words", 0) or 0)
    if target_words < 500:
        warnings.append(
            "Target below 500 words; voice-distance z-scores are unstable. "
            "Read top deviations as inspection leads, not verdicts."
        )
    elif target_words < 1000:
        warnings.append(
            "Target below 1,000 words; character n-grams and function-word distances "
            "remain length-sensitive."
        )

    if len(baseline_entries) < 5:
        warnings.append("Fewer than 5 baseline files; baseline standard deviations can be unstable.")

    metadata = [entry.get("metadata", {}) for entry in baseline_entries]
    registers = sorted({m.get("register") for m in metadata if m.get("register")})
    personas = sorted({m.get("persona") for m in metadata if m.get("persona")})
    privacy_values = sorted({m.get("privacy") for m in metadata if m.get("privacy")})
    if len(registers) > 1:
        warnings.append(
            "Baseline mixes registers: " + ", ".join(registers) +
            ". Register mismatch can dominate voice-distance scores."
        )
    if len(personas) > 1:
        warnings.append(
            "Baseline mixes personas: " + ", ".join(personas) +
            ". Persona mixing can blur the voice profile."
        )
    if len(privacy_values) > 1:
        warnings.append(
            "Baseline mixes privacy classes: " + ", ".join(privacy_values) +
            ". Keep generated profiles and reports private unless every source is shareable."
        )

    short_baselines = [
        e["id"] for e in baseline_features
        if int(e.get("summary", {}).get("n_words", 0) or 0) < 1000
    ]
    if short_baselines:
        warnings.append(
            "Some baseline files are under 1,000 words: " + ", ".join(short_baselines[:5]) +
            ("..." if len(short_baselines) > 5 else "") + "."
        )
    return warnings


def voice_distance_band(score: float) -> str:
    if score < 0.75:
        return f"Close to baseline ({PROVISIONAL_BAND_NOTE})"
    if score < 1.25:
        return f"Light drift ({PROVISIONAL_BAND_NOTE})"
    if score < 2.0:
        return f"Strong drift ({PROVISIONAL_BAND_NOTE})"
    return f"Off-baseline ({PROVISIONAL_BAND_NOTE})"


def voice_distance_interpretation(score: float) -> str:
    if score < 0.75:
        return "The target sits inside the writer/register baseline on most measured features."
    if score < 1.25:
        return "The target is recognizably related to the baseline, with a few meaningful departures."
    if score < 2.0:
        return "The target departs from the baseline across multiple feature families."
    return "The target is far from the supplied baseline; check register mismatch before inferring voice loss."


def build_profile(
    baseline_entries: list[dict[str, Any]],
    *,
    include_spacy: bool = True,
    limits: dict[str, int] | None = None,
) -> dict[str, Any]:
    if not baseline_entries:
        raise ValueError("Baseline contains no usable entries")
    baseline_features = extract_entry_features(baseline_entries, include_spacy=include_spacy)
    selected = select_feature_names(baseline_features, limits=limits)

    families = {}
    for family, names in selected.items():
        vectors = [feature_vector(item, family, names) for item in baseline_features]
        stats = vector_stats(vectors, names)
        ranked_by_mean = sorted(
            (
                {
                    "feature": name,
                    "mean": info["mean"],
                    "sd": info["sd"],
                    "cv": (info["sd"] / info["mean"]) if info["mean"] else None,
                }
                for name, info in stats.items()
            ),
            key=lambda x: x["mean"],
            reverse=True,
        )
        stable = sorted(
            [x for x in ranked_by_mean if x["mean"] > 0 and x["cv"] is not None],
            key=lambda x: x["cv"],
        )
        families[family] = {
            "n_features": len(names),
            "top_features": ranked_by_mean[:40],
            "most_stable_features": stable[:40],
        }

    return {
        "privacy": "PRIVATE - DO NOT SHARE. A voice profile is a voice-cloning input.",
        "baseline_summary": summarize_entries(baseline_features),
        "selected_features": {k: len(v) for k, v in selected.items()},
        "warnings": profile_warnings(baseline_entries, baseline_features),
        "families": families,
    }


def profile_warnings(
    baseline_entries: list[dict[str, Any]],
    baseline_features: list[dict[str, Any]],
) -> list[str]:
    baseline_summary = summarize_entries(baseline_features)
    warnings = []
    if baseline_summary["n_files"] < 5:
        warnings.append("Fewer than 5 files. Treat stable-feature claims as provisional.")
    if len(baseline_summary["registers"]) > 1:
        warnings.append(
            "Profile mixes registers: " + ", ".join(baseline_summary["registers"]) +
            ". Build separate profiles per register for voiceprint work."
        )
    if len(baseline_summary["personas"]) > 1:
        warnings.append(
            "Profile mixes personas: " + ", ".join(baseline_summary["personas"]) +
            ". Build separate profiles per persona."
        )
    if len(baseline_summary["privacy_values"]) > 1:
        warnings.append(
            "Profile mixes privacy classes: " + ", ".join(baseline_summary["privacy_values"]) +
            ". Treat the output as private unless every source is shareable."
        )
    short_files = [
        e["id"] for e in baseline_features
        if int(e.get("summary", {}).get("n_words", 0) or 0) < 1000
    ]
    if short_files:
        warnings.append(
            "Some baseline files are under 1,000 words: " + ", ".join(short_files[:5]) +
            ("..." if len(short_files) > 5 else "") + "."
        )
    return warnings
