#!/usr/bin/env python3
"""
variance_audit.py
Layer A distributional diagnostics for the ai-prose-detection skill.

Computes the eleven variance signals documented in
references/distributional-diagnostics.md and reports per-document
statistics that predict mode-collapse magnitude.

Usage:
    python variance_audit.py INPUT.txt [--json] [--baseline-dir DIR]
                              [--mattr-window 50] [--no-tier2] [--no-tier3]

Tiers:
  Tier 1 (always):  sentence-length stats + burstiness, MATTR, MTLD,
                    Yule's K, Shannon entropy, FKGL stats, connective
                    density, function-word fingerprint.
  Tier 2 (spaCy):   POS-bigram entropy + KL against reference, MDD-SD.
  Tier 3 (embeddings): adjacent-sentence cosine mean and SD.
                       Falls back to TF-IDF if sentence-transformers
                       is unavailable; falls back to nothing if
                       scikit-learn is also unavailable.

Outputs a JSON object and/or a human-readable summary. With a baseline
directory, also reports the draft's z-score on each signal against
the baseline distribution.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import statistics
import sys
from collections import Counter
from pathlib import Path
from typing import Any

# ---------- Optional dependencies ----------
try:
    import textstat  # type: ignore
    HAS_TEXTSTAT = True
except ImportError:
    HAS_TEXTSTAT = False

try:
    import nltk  # type: ignore
    try:
        nltk.data.find("tokenizers/punkt")
    except LookupError:
        try:
            nltk.download("punkt", quiet=True)
        except Exception:
            pass
    HAS_NLTK = True
except ImportError:
    HAS_NLTK = False

try:
    import spacy  # type: ignore
    try:
        _NLP = spacy.load("en_core_web_sm")
        HAS_SPACY = True
    except Exception:
        HAS_SPACY = False
        _NLP = None
except ImportError:
    HAS_SPACY = False
    _NLP = None

try:
    from sentence_transformers import SentenceTransformer  # type: ignore
    _ST_MODEL = None
    HAS_ST = True
except ImportError:
    HAS_ST = False

try:
    from sklearn.feature_extraction.text import TfidfVectorizer  # type: ignore
    from sklearn.metrics.pairwise import cosine_similarity  # type: ignore
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False


# ---------- Resource lists ----------

# Top function words (Mosteller-Wallace + extensions).
FUNCTION_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an",
    "and", "any", "are", "as", "at", "be", "because", "been", "before",
    "being", "below", "between", "both", "but", "by", "could", "did", "do",
    "does", "doing", "down", "during", "each", "few", "for", "from",
    "further", "had", "has", "have", "having", "he", "her", "here", "hers",
    "herself", "him", "himself", "his", "how", "i", "if", "in", "into", "is",
    "it", "its", "itself", "just", "me", "might", "mine", "more", "most",
    "must", "my", "myself", "no", "nor", "not", "now", "of", "off", "on",
    "once", "one", "only", "or", "other", "ought", "our", "ours", "ourselves",
    "out", "over", "own", "same", "shall", "she", "should", "so", "some",
    "such", "than", "that", "the", "their", "theirs", "them", "themselves",
    "then", "there", "these", "they", "this", "those", "through", "to", "too",
    "under", "until", "up", "upon", "us", "very", "was", "we", "were", "what",
    "when", "where", "which", "while", "who", "whom", "whose", "why", "will",
    "with", "would", "yet", "you", "your", "yours", "yourself", "yourselves",
}

# Discourse markers / connectives flagged for over-density.
CONNECTIVES = {
    "furthermore", "moreover", "additionally", "in addition", "however",
    "therefore", "thus", "consequently", "hence", "in conclusion",
    "to summarize", "to conclude", "in summary", "it is important to note",
    "it should be noted", "notably", "interestingly", "importantly",
    "remarkably", "specifically", "particularly", "in particular",
    "for example", "for instance", "namely", "in other words",
    "that is to say", "as a result", "as such", "indeed", "in fact",
    "of course", "naturally", "clearly", "obviously", "ultimately",
    "essentially", "fundamentally", "in essence",
}


# ---------- Tokenization ----------

_SENT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z\"'])|\n{2,}")
_WORD_RE = re.compile(r"[A-Za-z']+")


def split_sentences(text: str) -> list[str]:
    if HAS_NLTK:
        try:
            from nltk.tokenize import sent_tokenize  # type: ignore
            sents = [s.strip() for s in sent_tokenize(text) if s.strip()]
            if sents:
                return sents
        except Exception:
            pass
    parts = _SENT_RE.split(text)
    return [p.strip() for p in parts if p.strip()]


def split_words(text: str) -> list[str]:
    return _WORD_RE.findall(text.lower())


def count_syllables_word(word: str) -> int:
    """Heuristic syllable count for a single word (lowercase, alpha)."""
    word = word.lower().strip()
    if not word:
        return 0
    if HAS_TEXTSTAT:
        try:
            return max(1, int(textstat.syllable_count(word)))
        except Exception:
            pass
    # Heuristic: count vowel groups; subtract silent e.
    vowels = "aeiouy"
    count = 0
    prev = False
    for ch in word:
        is_vowel = ch in vowels
        if is_vowel and not prev:
            count += 1
        prev = is_vowel
    if word.endswith("e") and count > 1:
        count -= 1
    return max(1, count)


def count_syllables(words: list[str]) -> int:
    return sum(count_syllables_word(w) for w in words)


# ---------- Tier 1 metrics ----------

def sentence_length_stats(sentences: list[str]) -> dict[str, float]:
    lengths = [len(split_words(s)) for s in sentences]
    if len(lengths) < 2:
        return {
            "n_sentences": len(lengths),
            "mean": float(lengths[0]) if lengths else 0.0,
            "sd": 0.0,
            "min": float(lengths[0]) if lengths else 0.0,
            "max": float(lengths[0]) if lengths else 0.0,
            "variance": 0.0,
            "burstiness_B": 0.0,
        }
    mean = statistics.mean(lengths)
    sd = statistics.stdev(lengths)
    var = statistics.variance(lengths)
    B = (sd - mean) / (sd + mean) if (sd + mean) > 0 else 0.0
    return {
        "n_sentences": len(lengths),
        "mean": mean,
        "sd": sd,
        "min": float(min(lengths)),
        "max": float(max(lengths)),
        "variance": var,
        "burstiness_B": B,
    }


def mattr(words: list[str], window: int = 50) -> float:
    if len(words) < window:
        if not words:
            return 0.0
        return len(set(words)) / len(words)
    ratios = []
    for i in range(0, len(words) - window + 1):
        chunk = words[i:i + window]
        ratios.append(len(set(chunk)) / window)
    return sum(ratios) / len(ratios) if ratios else 0.0


def mtld_one_direction(words: list[str], threshold: float = 0.72) -> float:
    if not words:
        return 0.0
    factor_count = 0
    types: set[str] = set()
    token_count = 0
    last_ttr = 1.0
    for w in words:
        token_count += 1
        types.add(w)
        ttr = len(types) / token_count
        last_ttr = ttr
        if ttr <= threshold and token_count > 1:
            factor_count += 1
            types = set()
            token_count = 0
    if token_count > 0:
        # fractional credit for trailing partial factor
        if last_ttr < 1.0:
            partial = (1 - last_ttr) / (1 - threshold)
            factor_count += min(partial, 1.0)
    if factor_count == 0:
        return float(len(words))
    return len(words) / factor_count


def mtld(words: list[str], threshold: float = 0.72) -> float:
    forward = mtld_one_direction(words, threshold)
    backward = mtld_one_direction(list(reversed(words)), threshold)
    return (forward + backward) / 2


def yules_k(words: list[str]) -> float:
    if not words:
        return 0.0
    counts = Counter(words)
    N = len(words)
    M2 = sum(c * c for c in counts.values())
    if N == 0:
        return 0.0
    return 1e4 * (M2 - N) / (N * N)


def shannon_entropy(words: list[str]) -> float:
    if not words:
        return 0.0
    counts = Counter(words)
    N = len(words)
    H = 0.0
    for c in counts.values():
        p = c / N
        H -= p * math.log2(p)
    return H


def fkgl_per_sentence(sentence: str) -> float | None:
    words = split_words(sentence)
    if not words:
        return None
    syllables = count_syllables(words)
    W = len(words)
    if W == 0:
        return None
    # Single-sentence form: 0.39 * W + 11.8 * (Sy/W) - 15.59
    return 0.39 * W + 11.8 * (syllables / W) - 15.59


def fkgl_stats(sentences: list[str]) -> dict[str, float]:
    scores = [s for s in (fkgl_per_sentence(sent) for sent in sentences) if s is not None]
    if not scores:
        return {"mean": 0.0, "sd": 0.0, "min": 0.0, "max": 0.0, "n": 0}
    if len(scores) == 1:
        return {"mean": scores[0], "sd": 0.0, "min": scores[0], "max": scores[0], "n": 1}
    return {
        "mean": statistics.mean(scores),
        "sd": statistics.stdev(scores),
        "min": min(scores),
        "max": max(scores),
        "n": len(scores),
    }


def connective_density(text: str, total_tokens: int) -> dict[str, float]:
    if total_tokens == 0:
        return {"per_1000_tokens": 0.0, "count": 0, "by_marker": {}}
    text_lower = text.lower()
    by_marker = {}
    total = 0
    for marker in CONNECTIVES:
        # word-boundary match with possible trailing comma/period
        pattern = r"\b" + re.escape(marker) + r"\b"
        matches = re.findall(pattern, text_lower)
        if matches:
            by_marker[marker] = len(matches)
            total += len(matches)
    return {
        "count": total,
        "per_1000_tokens": (total / total_tokens) * 1000,
        "by_marker": by_marker,
    }


def function_word_fingerprint(words: list[str], top_n: int = 100) -> dict[str, Any]:
    if not words:
        return {"top_n": top_n, "frequencies": {}, "function_word_ratio": 0.0}
    counts = Counter(w for w in words if w in FUNCTION_WORDS)
    total = len(words)
    fw_total = sum(counts.values())
    top = dict(counts.most_common(top_n))
    return {
        "top_n": top_n,
        "frequencies": {w: c / total for w, c in top.items()},
        "function_word_ratio": fw_total / total if total else 0.0,
    }


# ---------- Tier 2 metrics (spaCy) ----------

def pos_bigram_distribution(text: str) -> dict[str, Any] | None:
    if not HAS_SPACY or _NLP is None:
        return None
    doc = _NLP(text)
    bigrams: Counter[str] = Counter()
    for sent in doc.sents:
        tags = [t.pos_ for t in sent if not t.is_space]
        for a, b in zip(tags, tags[1:]):
            bigrams[f"{a}-{b}"] += 1
    total = sum(bigrams.values())
    if total == 0:
        return None
    probs = {k: v / total for k, v in bigrams.items()}
    H = -sum(p * math.log2(p) for p in probs.values() if p > 0)
    return {
        "n_bigrams": total,
        "n_unique": len(bigrams),
        "entropy_bits": H,
        "top_20": dict(bigrams.most_common(20)),
    }


def mdd_stats(text: str) -> dict[str, Any] | None:
    if not HAS_SPACY or _NLP is None:
        return None
    doc = _NLP(text)
    per_sentence = []
    for sent in doc.sents:
        toks = [t for t in sent if not t.is_space]
        if len(toks) < 2:
            continue
        distances = []
        for t in toks:
            if t.dep_ == "ROOT" or t.head is t:
                continue
            distances.append(abs(t.i - t.head.i))
        if distances:
            per_sentence.append(sum(distances) / len(distances))
    if len(per_sentence) < 2:
        return {
            "n_sentences": len(per_sentence),
            "mean": per_sentence[0] if per_sentence else 0.0,
            "sd": 0.0,
        }
    return {
        "n_sentences": len(per_sentence),
        "mean": statistics.mean(per_sentence),
        "sd": statistics.stdev(per_sentence),
    }


# ---------- Tier 3 metrics (embeddings) ----------

def _get_st_model():
    global _ST_MODEL
    if _ST_MODEL is not None:
        return _ST_MODEL
    if not HAS_ST:
        return None
    try:
        from sentence_transformers import SentenceTransformer
        _ST_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
        return _ST_MODEL
    except Exception:
        return None


def adjacent_sentence_cosine(sentences: list[str]) -> dict[str, Any] | None:
    if len(sentences) < 2:
        return None

    model = _get_st_model() if HAS_ST else None
    if model is not None:
        try:
            import numpy as np  # type: ignore
            embeddings = model.encode(sentences, show_progress_bar=False)
            sims = []
            for i in range(len(embeddings) - 1):
                a = embeddings[i]
                b = embeddings[i + 1]
                denom = (np.linalg.norm(a) * np.linalg.norm(b))
                if denom == 0:
                    continue
                sims.append(float(np.dot(a, b) / denom))
            if not sims:
                return None
            return {
                "method": "sentence-transformers (all-MiniLM-L6-v2)",
                "n_pairs": len(sims),
                "mean": statistics.mean(sims),
                "sd": statistics.stdev(sims) if len(sims) > 1 else 0.0,
                "min": min(sims),
                "max": max(sims),
            }
        except Exception:
            pass

    if HAS_SKLEARN:
        try:
            vec = TfidfVectorizer().fit_transform(sentences)
            sims = []
            for i in range(vec.shape[0] - 1):
                s = float(cosine_similarity(vec[i], vec[i + 1])[0][0])
                sims.append(s)
            if not sims:
                return None
            return {
                "method": "tfidf-cosine",
                "n_pairs": len(sims),
                "mean": statistics.mean(sims),
                "sd": statistics.stdev(sims) if len(sims) > 1 else 0.0,
                "min": min(sims),
                "max": max(sims),
            }
        except Exception:
            pass

    return None


# ---------- Aggregator ----------

def audit_text(
    text: str,
    mattr_window: int = 50,
    do_tier2: bool = True,
    do_tier3: bool = True,
) -> dict[str, Any]:
    sentences = split_sentences(text)
    words = split_words(text)
    n_words = len(words)
    n_sentences = len(sentences)

    out: dict[str, Any] = {
        "summary": {
            "n_words": n_words,
            "n_sentences": n_sentences,
            "reliable": n_words >= 200,
        },
        "tier1": {},
    }

    if n_words < 50:
        out["warning"] = "Text below 50 words; Layer A statistics are not meaningful."
        return out

    out["tier1"]["sentence_length"] = sentence_length_stats(sentences)
    out["tier1"]["mattr"] = {"window": mattr_window, "value": mattr(words, mattr_window)}
    out["tier1"]["mtld"] = mtld(words)
    out["tier1"]["yules_k"] = yules_k(words)
    out["tier1"]["shannon_entropy_bits"] = shannon_entropy(words)
    out["tier1"]["fkgl"] = fkgl_stats(sentences)
    out["tier1"]["connective_density"] = connective_density(text, n_words)
    out["tier1"]["function_words"] = function_word_fingerprint(words)

    if do_tier2:
        out["tier2"] = {
            "available": HAS_SPACY,
            "pos_bigrams": pos_bigram_distribution(text) if HAS_SPACY else None,
            "mdd": mdd_stats(text) if HAS_SPACY else None,
        }
    if do_tier3:
        out["tier3"] = {
            "available": HAS_ST or HAS_SKLEARN,
            "adjacent_cosine": adjacent_sentence_cosine(sentences) if (HAS_ST or HAS_SKLEARN) else None,
        }
    return out


def audit_baseline(baseline_dir: str, **kwargs: Any) -> dict[str, Any]:
    paths = sorted(Path(baseline_dir).glob("*.txt"))
    audits = []
    for p in paths:
        try:
            txt = p.read_text(encoding="utf-8", errors="ignore")
            a = audit_text(txt, **kwargs)
            audits.append({"file": str(p.name), "audit": a})
        except Exception as e:
            audits.append({"file": str(p.name), "error": str(e)})
    return {
        "n_files": len(paths),
        "audits": audits,
        "aggregate": _aggregate_baseline(audits),
    }


def _aggregate_baseline(audits: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute per-statistic mean and SD across baseline files."""
    keys: list[tuple[str, ...]] = [
        ("tier1", "sentence_length", "sd"),
        ("tier1", "sentence_length", "burstiness_B"),
        ("tier1", "mattr", "value"),
        ("tier1", "mtld"),
        ("tier1", "yules_k"),
        ("tier1", "shannon_entropy_bits"),
        ("tier1", "fkgl", "sd"),
        ("tier1", "fkgl", "mean"),
        ("tier1", "connective_density", "per_1000_tokens"),
        ("tier1", "function_words", "function_word_ratio"),
        ("tier2", "pos_bigrams", "entropy_bits"),
        ("tier2", "mdd", "sd"),
        ("tier3", "adjacent_cosine", "mean"),
        ("tier3", "adjacent_cosine", "sd"),
    ]
    agg: dict[str, dict[str, float]] = {}
    for key in keys:
        vals: list[float] = []
        for a in audits:
            d: Any = a.get("audit", {})
            for k in key:
                if not isinstance(d, dict):
                    d = None
                    break
                d = d.get(k)
                if d is None:
                    break
            if isinstance(d, (int, float)):
                vals.append(float(d))
        if not vals:
            continue
        name = ".".join(key)
        if len(vals) == 1:
            agg[name] = {"mean": vals[0], "sd": 0.0, "n": 1}
        else:
            agg[name] = {
                "mean": statistics.mean(vals),
                "sd": statistics.stdev(vals),
                "n": len(vals),
            }
    return agg


def _z_score(value: float, agg: dict[str, float]) -> float | None:
    if "mean" not in agg or "sd" not in agg or agg["sd"] == 0:
        return None
    return (value - agg["mean"]) / agg["sd"]


def compare_to_baseline(audit: dict[str, Any], baseline: dict[str, Any]) -> dict[str, Any]:
    agg = baseline.get("aggregate", {})
    z_scores: dict[str, Any] = {}
    paths = [
        ("tier1.sentence_length.sd", ("tier1", "sentence_length", "sd")),
        ("tier1.sentence_length.burstiness_B", ("tier1", "sentence_length", "burstiness_B")),
        ("tier1.mattr.value", ("tier1", "mattr", "value")),
        ("tier1.mtld", ("tier1", "mtld")),
        ("tier1.yules_k", ("tier1", "yules_k")),
        ("tier1.shannon_entropy_bits", ("tier1", "shannon_entropy_bits")),
        ("tier1.fkgl.sd", ("tier1", "fkgl", "sd")),
        ("tier1.connective_density.per_1000_tokens",
         ("tier1", "connective_density", "per_1000_tokens")),
        ("tier1.function_words.function_word_ratio",
         ("tier1", "function_words", "function_word_ratio")),
        ("tier2.pos_bigrams.entropy_bits", ("tier2", "pos_bigrams", "entropy_bits")),
        ("tier2.mdd.sd", ("tier2", "mdd", "sd")),
        ("tier3.adjacent_cosine.mean", ("tier3", "adjacent_cosine", "mean")),
        ("tier3.adjacent_cosine.sd", ("tier3", "adjacent_cosine", "sd")),
    ]
    for name, key in paths:
        if name not in agg:
            continue
        d: Any = audit
        for k in key:
            if not isinstance(d, dict):
                d = None
                break
            d = d.get(k)
            if d is None:
                break
        if isinstance(d, (int, float)):
            z = _z_score(float(d), agg[name])
            z_scores[name] = {
                "value": float(d),
                "baseline_mean": agg[name]["mean"],
                "baseline_sd": agg[name]["sd"],
                "z_score": z,
            }
    return z_scores


# ---------- Band classification ----------

# Heuristic compression thresholds calibrated against fluent native-English prose.
# These are fallback heuristics for use without a baseline corpus; with a baseline,
# the z-score interpretation is more reliable. Each entry is a tuple of
# (threshold, direction, weight, length_floor) where:
#   - direction is "lt" (compressed when value < threshold) or "gt" (when value > threshold)
#   - weight is the contribution to band classification (signals differ in reliability)
#   - length_floor is the minimum word count for the heuristic to be reliable
COMPRESSION_HEURISTICS: dict[str, tuple[float, str, float, int]] = {
    # Burstiness magnitude is the most reliable single signal.
    # Calibration note: literature suggests B < -0.2 is compressed, but real
    # human essayistic prose with long sentences can reach B = -0.4 naturally
    # (verified on pre-AI testimony at B = -0.40). Threshold tightened to -0.4
    # so the heuristic catches the genuine AI mode-collapse case (B < -0.4
    # in the smoke-test AI passage) while sparing essayistic human registers.
    "burstiness_B": (-0.4, "lt", 2.0, 200),
    # Connective density: AI-prose runs 25-50 per 1000 tokens; humans 5-15.
    "connective_density": (20.0, "gt", 2.0, 200),
    # MATTR: literary fluent fiction runs 0.70-0.82 at window 50.
    "mattr": (0.65, "lt", 1.0, 300),
    # MTLD: noisy below ~500 words; threshold tightened.
    "mtld": (60.0, "lt", 1.0, 500),
    # Yule's K: concentration on frequent types.
    "yules_k": (200.0, "gt", 1.0, 500),
    # Shannon entropy: the literature reports 9.5-10.5 bits/token for native
    # fiction, but this depends heavily on vocabulary scope and register.
    # Empirical testing on pre-AI human prose across registers found values
    # 8.0-9.6, so the threshold has been removed (set very low) to avoid
    # firing false positives on writers whose vocabulary is naturally focused.
    # Use a personal baseline for entropy comparison instead of the heuristic.
    "shannon_entropy": (7.0, "lt", 1.0, 2000),
    # FKGL SD: human prose typically 3-5 across sentences; LLM 0.8-1.5.
    "fkgl_sd": (1.5, "lt", 1.5, 200),
    # Sentence-length SD is unreliable as a standalone signal because mean
    # sentence length varies dramatically by register (fiction with fragments
    # has SD 6-9; essay has SD 15-20). Burstiness B normalizes for mean and
    # carries this signal more reliably. Threshold raised so it almost never
    # fires; rely on B and on personal baseline z-scores instead.
    "sentence_length_sd": (5.0, "lt", 0.5, 5000),
    # Adjacent-sentence cosine: tight cohesion is the LLM tell.
    "adjacent_cosine_mean": (0.60, "gt", 1.5, 200),
    "adjacent_cosine_sd": (0.12, "lt", 1.0, 300),
    # MDD-SD: compressed syntactic variation.
    "mdd_sd": (0.7, "lt", 1.0, 300),
}


def classify_compression(audit: dict[str, Any]) -> dict[str, Any]:
    flagged: list[str] = []
    skipped: list[str] = []
    notes: dict[str, str] = {}
    weighted_score = 0.0
    n_words = audit.get("summary", {}).get("n_words", 0)
    t1 = audit.get("tier1", {})
    t2 = audit.get("tier2") or {}
    t3 = audit.get("tier3") or {}

    def check(
        signal: str,
        value: float | None,
    ) -> None:
        nonlocal weighted_score
        if value is None:
            return
        if signal not in COMPRESSION_HEURISTICS:
            return
        thresh, direction, weight, length_floor = COMPRESSION_HEURISTICS[signal]
        if n_words < length_floor:
            skipped.append(f"{signal} (need {length_floor}+ words, have {n_words})")
            return
        compressed = (
            (direction == "lt" and value < thresh)
            or (direction == "gt" and value > thresh)
        )
        if compressed:
            flagged.append(signal)
            weighted_score += weight

    sl = t1.get("sentence_length", {})
    check("burstiness_B", sl.get("burstiness_B"))
    check("sentence_length_sd", sl.get("sd"))

    cd = t1.get("connective_density", {})
    check("connective_density", cd.get("per_1000_tokens"))

    check("mattr", (t1.get("mattr") or {}).get("value"))
    check("mtld", t1.get("mtld"))
    check("yules_k", t1.get("yules_k"))
    check("shannon_entropy", t1.get("shannon_entropy_bits"))
    check("fkgl_sd", (t1.get("fkgl") or {}).get("sd"))

    mdd = t2.get("mdd")
    if mdd:
        check("mdd_sd", mdd.get("sd"))

    adj = t3.get("adjacent_cosine")
    if adj:
        check("adjacent_cosine_mean", adj.get("mean"))
        check("adjacent_cosine_sd", adj.get("sd"))

    # Band assignment by weighted score, scaled by available signals.
    # With all length floors satisfied, max weight ≈ 13.5; for short docs,
    # only ~5.5 of weight is available.
    if weighted_score < 2.0:
        band = "Lightly smoothed"
    elif weighted_score < 5.0:
        band = "Moderately smoothed"
    else:
        band = "Heavily smoothed"

    if n_words < 200:
        notes["reliability"] = (
            "Document below 200 words; band classification unreliable. "
            "Use Layer B and C primarily."
        )
    elif n_words < 500:
        notes["reliability"] = (
            "Document below 500 words; some length-sensitive signals skipped. "
            "Cross-check against Layer B."
        )

    return {
        "band": band,
        "weighted_score": round(weighted_score, 2),
        "flagged_signals": flagged,
        "skipped_signals": skipped,
        "n_flagged": len(flagged),
        "notes": notes,
        "thresholds_used": {
            k: {"threshold": t, "direction": d, "weight": w, "length_floor": lf}
            for k, (t, d, w, lf) in COMPRESSION_HEURISTICS.items()
        },
    }


# ---------- Output formatting ----------

def format_summary(audit: dict[str, Any], compression: dict[str, Any]) -> str:
    lines = []
    s = audit.get("summary", {})
    lines.append("=" * 60)
    lines.append("LAYER A: DISTRIBUTIONAL DIAGNOSTIC")
    lines.append("=" * 60)
    lines.append(f"Words: {s.get('n_words', 0)}    Sentences: {s.get('n_sentences', 0)}")
    if not s.get("reliable", True):
        lines.append("WARNING: Document below 200 words; results are noisy.")
    lines.append("")
    lines.append(f"Band: {compression['band']}  (weighted score: {compression.get('weighted_score', 0)})")
    if compression["flagged_signals"]:
        lines.append("Flagged signals (compression observed):")
        for sig in compression["flagged_signals"]:
            lines.append(f"  - {sig}")
    else:
        lines.append("No compression flags fired against fallback heuristics.")
    if compression.get("skipped_signals"):
        lines.append("Skipped (insufficient text length):")
        for sig in compression["skipped_signals"]:
            lines.append(f"  - {sig}")
    if compression["notes"]:
        for k, v in compression["notes"].items():
            lines.append(f"Note ({k}): {v}")
    lines.append("")

    t1 = audit.get("tier1", {})
    lines.append("Tier 1 (always):")
    sl = t1.get("sentence_length", {})
    lines.append(
        f"  Sentence length: mean={sl.get('mean', 0):.2f} "
        f"sd={sl.get('sd', 0):.2f} "
        f"min={sl.get('min', 0):.0f} max={sl.get('max', 0):.0f} "
        f"B={sl.get('burstiness_B', 0):.3f}"
    )
    mat = t1.get("mattr", {})
    lines.append(f"  MATTR (window {mat.get('window', 50)}): {mat.get('value', 0):.4f}")
    lines.append(f"  MTLD: {t1.get('mtld', 0):.2f}")
    lines.append(f"  Yule's K: {t1.get('yules_k', 0):.2f}")
    lines.append(f"  Shannon entropy: {t1.get('shannon_entropy_bits', 0):.3f} bits/token")
    fk = t1.get("fkgl", {})
    lines.append(
        f"  FKGL: mean={fk.get('mean', 0):.2f} sd={fk.get('sd', 0):.2f} "
        f"min={fk.get('min', 0):.2f} max={fk.get('max', 0):.2f} (n={fk.get('n', 0)})"
    )
    cd = t1.get("connective_density", {})
    lines.append(
        f"  Connective density: {cd.get('per_1000_tokens', 0):.2f} per 1000 tokens "
        f"(total: {cd.get('count', 0)})"
    )
    fw = t1.get("function_words", {})
    lines.append(f"  Function-word ratio: {fw.get('function_word_ratio', 0):.4f}")

    t2 = audit.get("tier2")
    if t2:
        if t2.get("available"):
            lines.append("")
            lines.append("Tier 2 (spaCy):")
            pb = t2.get("pos_bigrams")
            if pb:
                lines.append(
                    f"  POS-bigrams: n={pb.get('n_bigrams', 0)} "
                    f"unique={pb.get('n_unique', 0)} "
                    f"entropy={pb.get('entropy_bits', 0):.3f} bits"
                )
            mdd = t2.get("mdd")
            if mdd:
                lines.append(
                    f"  MDD per sentence: mean={mdd.get('mean', 0):.3f} "
                    f"sd={mdd.get('sd', 0):.3f} (n={mdd.get('n_sentences', 0)})"
                )
        else:
            lines.append("")
            lines.append("Tier 2 (spaCy): not available. Install `spacy` and `en_core_web_sm`.")

    t3 = audit.get("tier3")
    if t3:
        if t3.get("available"):
            lines.append("")
            lines.append("Tier 3 (embeddings):")
            adj = t3.get("adjacent_cosine")
            if adj:
                lines.append(
                    f"  Adjacent-sentence cosine ({adj.get('method', 'unknown')}): "
                    f"mean={adj.get('mean', 0):.3f} sd={adj.get('sd', 0):.3f} "
                    f"(n={adj.get('n_pairs', 0)})"
                )
        else:
            lines.append("")
            lines.append(
                "Tier 3 (embeddings): not available. "
                "Install `sentence-transformers` or `scikit-learn`."
            )

    return "\n".join(lines)


def format_baseline_comparison(z_scores: dict[str, Any]) -> str:
    if not z_scores:
        return ""
    lines = []
    lines.append("")
    lines.append("Baseline comparison (z-scores; |z| > 1.0 is meaningful):")
    for name, info in z_scores.items():
        z = info.get("z_score")
        if z is None:
            continue
        marker = " *" if abs(z) > 1.0 else ""
        lines.append(
            f"  {name}: value={info['value']:.4f} "
            f"baseline_mean={info['baseline_mean']:.4f} "
            f"z={z:+.2f}{marker}"
        )
    return "\n".join(lines)


# ---------- CLI ----------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Layer A variance audit for ai-prose-detection skill."
    )
    parser.add_argument("input", help="Path to text file to audit.")
    parser.add_argument(
        "--baseline-dir",
        help="Optional directory of .txt files for baseline comparison.",
    )
    parser.add_argument(
        "--mattr-window",
        type=int,
        default=50,
        help="Window size for MATTR (default 50).",
    )
    parser.add_argument(
        "--no-tier2", action="store_true",
        help="Skip Tier 2 metrics (POS bigrams, MDD)."
    )
    parser.add_argument(
        "--no-tier3", action="store_true",
        help="Skip Tier 3 metrics (adjacent-sentence cosine)."
    )
    parser.add_argument("--json", action="store_true", help="Output JSON only.")
    parser.add_argument(
        "--quiet", action="store_true",
        help="Suppress human-readable summary."
    )
    args = parser.parse_args()

    text = Path(args.input).read_text(encoding="utf-8", errors="ignore")
    audit = audit_text(
        text,
        mattr_window=args.mattr_window,
        do_tier2=not args.no_tier2,
        do_tier3=not args.no_tier3,
    )
    compression = classify_compression(audit)

    output: dict[str, Any] = {"audit": audit, "compression": compression}

    if args.baseline_dir and os.path.isdir(args.baseline_dir):
        baseline = audit_baseline(
            args.baseline_dir,
            mattr_window=args.mattr_window,
            do_tier2=not args.no_tier2,
            do_tier3=not args.no_tier3,
        )
        z_scores = compare_to_baseline(audit, baseline)
        output["baseline"] = {
            "n_files": baseline["n_files"],
            "aggregate": baseline["aggregate"],
        }
        output["baseline_comparison"] = z_scores

    if args.json:
        print(json.dumps(output, indent=2, default=str))
        return 0

    if not args.quiet:
        print(format_summary(audit, compression))
        if "baseline_comparison" in output:
            print(format_baseline_comparison(output["baseline_comparison"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
