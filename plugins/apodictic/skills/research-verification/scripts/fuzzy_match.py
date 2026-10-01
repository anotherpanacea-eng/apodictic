#!/usr/bin/env python3
"""
Fuzzy matching for citation metadata resolution.

Handles imprecise citations: misspelled author names, approximate titles,
wrong years, partial titles, subtitle inclusion/omission.

Thresholds:
- Title: >=80% word-token similarity
- Author: surname match (case-insensitive)
- Year: +-1 tolerance (online-first vs. print dates)
"""

import re
from difflib import SequenceMatcher


def _normalize_title(title: str) -> str:
    """Normalize a title for comparison: lowercase, strip punctuation, collapse whitespace."""
    t = title.lower()
    t = re.sub(r'[^\w\s]', ' ', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t


def _title_similarity(t1: str, t2: str) -> float:
    """Word-token similarity between two titles."""
    n1 = _normalize_title(t1)
    n2 = _normalize_title(t2)
    if not n1 or not n2:
        return 0.0
    return SequenceMatcher(None, n1, n2).ratio()


def _extract_surname(name: str) -> str:
    """Extract surname from various name formats."""
    name = name.strip()
    if ',' in name:
        return name.split(',')[0].strip().lower()
    parts = name.split()
    if parts:
        # Handle prefixes: van, von, de, etc.
        prefixes = {'van', 'von', 'de', 'del', 'der', 'di', 'la', 'le', 'el'}
        if len(parts) >= 2 and parts[-2].lower() in prefixes:
            return f"{parts[-2]} {parts[-1]}".lower()
        return parts[-1].lower()
    return name.lower()


def _author_match(query_author: str, candidate_authors: list[str]) -> bool:
    """Check if any candidate author surname matches the query author surname."""
    if not query_author:
        return True  # No author constraint
    q_surname = _extract_surname(query_author)
    for ca in candidate_authors:
        if _extract_surname(ca) == q_surname:
            return True
    return False


def _year_match(query_year: str, candidate_year: str, tolerance: int = 1) -> bool:
    """Check if years match within tolerance."""
    if not query_year or not candidate_year:
        return True  # No year constraint
    try:
        qy = int(str(query_year)[:4])
        cy = int(str(candidate_year)[:4])
        return abs(qy - cy) <= tolerance
    except (ValueError, TypeError):
        return True


def _extract_metadata_crossref(item: dict) -> dict:
    """Extract normalized metadata from a CrossRef result item."""
    title_list = item.get("title", [])
    title = title_list[0] if isinstance(title_list, list) and title_list else str(title_list) if title_list else ""

    authors = []
    for a in item.get("author", []):
        family = a.get("family", "")
        given = a.get("given", "")
        authors.append(f"{family}, {given}" if given else family)

    # Year from various date fields
    year = ""
    for date_field in ["published-print", "published-online", "created"]:
        dp = item.get(date_field, {}).get("date-parts", [[]])
        if dp and dp[0] and dp[0][0]:
            year = str(dp[0][0])
            break

    container = item.get("container-title", [])
    venue = container[0] if isinstance(container, list) and container else str(container) if container else ""

    return {
        "title": title,
        "authors": authors,
        "year": year,
        "venue": venue,
        "doi": item.get("DOI", ""),
        "abstract": item.get("abstract", ""),
    }


def _extract_metadata_s2(paper: dict) -> dict:
    """Extract normalized metadata from a Semantic Scholar result."""
    authors = [a.get("name", "") for a in paper.get("authors", [])]
    ext_ids = paper.get("externalIds", {}) or {}

    return {
        "title": paper.get("title", ""),
        "authors": authors,
        "year": str(paper.get("year", "")),
        "venue": paper.get("venue", ""),
        "doi": ext_ids.get("DOI", ""),
        "abstract": paper.get("abstract", ""),
        "citation_count": paper.get("citationCount", 0),
        "s2_id": paper.get("paperId", ""),
    }


def _extract_metadata_openalex(work: dict) -> dict:
    """Extract normalized metadata from an OpenAlex result."""
    authors = []
    for authorship in work.get("authorships", []):
        author_obj = authorship.get("author", {})
        name = author_obj.get("display_name", "")
        if name:
            authors.append(name)

    return {
        "title": work.get("title", ""),
        "authors": authors,
        "year": str(work.get("publication_year", "")),
        "venue": work.get("primary_location", {}).get("source", {}).get("display_name", "") if work.get("primary_location") else "",
        "doi": (work.get("doi", "") or "").replace("https://doi.org/", ""),
        "abstract": "",  # OpenAlex abstracts require separate inverted-index reconstruction
        "citation_count": work.get("cited_by_count", 0),
        "openalex_id": work.get("id", ""),
    }


EXTRACTORS = {
    "crossref": _extract_metadata_crossref,
    "s2": _extract_metadata_s2,
    "openalex": _extract_metadata_openalex,
}


def best_match(
    query_title: str,
    query_author: str,
    query_year: str,
    candidates: list[dict],
    source: str = "crossref",
    threshold: float = 0.80,
) -> dict | None:
    """
    Find the best matching candidate for a citation query.

    Returns normalized metadata dict for the best match, or None if no match
    meets the threshold.
    """
    extractor = EXTRACTORS.get(source, lambda x: x)
    best = None
    best_score = 0.0

    for item in candidates:
        meta = extractor(item)
        title_score = _title_similarity(query_title, meta.get("title", ""))

        if title_score < threshold:
            continue

        if not _author_match(query_author, meta.get("authors", [])):
            continue

        if not _year_match(query_year, meta.get("year", "")):
            continue

        # Score: title similarity is primary, author and year are pass/fail
        if title_score > best_score:
            best_score = title_score
            best = meta
            best["_match_score"] = round(title_score, 3)
            best["_match_source"] = source

    return best


# ---------------------------------------------------------------------------
# CLI for testing
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python fuzzy_match.py 'title to match' 'author surname'")
        sys.exit(1)

    title = sys.argv[1]
    author = sys.argv[2] if len(sys.argv) > 2 else ""

    # Demo with fake candidates
    candidates = [
        {"title": [title.upper()], "author": [{"family": author, "given": "A."}], "DOI": "10.1234/test",
         "published-print": {"date-parts": [[2024]]}, "container-title": ["Test Journal"]}
    ]
    result = best_match(title, author, "", candidates, source="crossref")
    print(f"Match: {result}")
