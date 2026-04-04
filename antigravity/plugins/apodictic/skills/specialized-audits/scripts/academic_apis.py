#!/usr/bin/env python3
"""
Academic API client for APODICTIC Citation Verifier and Field Reconnaissance.

Provides batch resolution against CrossRef, Semantic Scholar, OpenAlex, CORE,
Unpaywall, PubMed, and Wayback Machine. Handles rate limiting, response caching,
and provenance tracking.

Usage:
    python academic_apis.py resolve --title "Attention Is All You Need" --author "Vaswani"
    python academic_apis.py resolve --doi "10.1234/example"
    python academic_apis.py resolve --url "https://example.com/report.pdf"
    python academic_apis.py batch --input citations.json --output results.json
    python academic_apis.py check-url --url "https://example.com/page"
    python academic_apis.py retraction-check --doi "10.1234/example"
"""

import argparse
import json
import os
import sys
import time
import urllib.parse
import urllib.request
import urllib.error
from pathlib import Path

from response_cache import ResponseCache
from provenance import ProvenanceStore

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CROSSREF_MAILTO = os.environ.get("CROSSREF_MAILTO", "apodictic@example.com")
S2_API_KEY = os.environ.get("S2_API_KEY", "")
OPENALEX_MAILTO = os.environ.get("OPENALEX_MAILTO", CROSSREF_MAILTO)

RATE_LIMIT_DELAY = 1.0  # seconds between API calls

# ---------------------------------------------------------------------------
# HTTP helper
# ---------------------------------------------------------------------------

def _fetch_json(url: str, headers: dict | None = None, timeout: int = 15) -> dict | None:
    """Fetch a URL and parse as JSON. Returns None on failure."""
    req_headers = {"User-Agent": f"APODICTIC/1.0 (mailto:{CROSSREF_MAILTO})"}
    if headers:
        req_headers.update(headers)
    if S2_API_KEY and "semanticscholar" in url:
        req_headers["x-api-key"] = S2_API_KEY

    req = urllib.request.Request(url, headers=req_headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, TimeoutError) as e:
        return {"_error": str(e), "_url": url}


def _check_url(url: str, timeout: int = 10) -> dict:
    """Check whether a URL is live. Returns status info."""
    req = urllib.request.Request(url, method="HEAD",
                                headers={"User-Agent": "APODICTIC/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return {"url": url, "status": resp.status, "live": True}
    except urllib.error.HTTPError as e:
        return {"url": url, "status": e.code, "live": False}
    except Exception as e:
        return {"url": url, "status": None, "live": False, "error": str(e)}

# ---------------------------------------------------------------------------
# Individual API resolvers
# ---------------------------------------------------------------------------

def resolve_crossref_doi(doi: str) -> dict:
    """Resolve a DOI via CrossRef."""
    url = f"https://api.crossref.org/works/{urllib.parse.quote(doi, safe='')}"
    return _fetch_json(url) or {}


def search_crossref(title: str, author: str = "", rows: int = 5) -> dict:
    """Search CrossRef by bibliographic query."""
    params = {"query.bibliographic": title, "rows": str(rows)}
    if author:
        params["query.author"] = author
    qs = urllib.parse.urlencode(params)
    return _fetch_json(f"https://api.crossref.org/works?{qs}") or {}


def search_semantic_scholar(query: str, limit: int = 5) -> dict:
    """Search Semantic Scholar."""
    params = {
        "query": query,
        "limit": str(limit),
        "fields": "title,authors,year,externalIds,venue,citationCount,abstract"
    }
    qs = urllib.parse.urlencode(params)
    return _fetch_json(f"https://api.semanticscholar.org/graph/v1/paper/search?{qs}") or {}


def get_s2_citations(paper_id: str, direction: str = "citations", limit: int = 20) -> dict:
    """Get citations or references for a paper via Semantic Scholar."""
    params = {"fields": "title,authors,year,venue,citationCount", "limit": str(limit)}
    qs = urllib.parse.urlencode(params)
    return _fetch_json(
        f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}/{direction}?{qs}"
    ) or {}


def search_openalex(query: str, author: str = "", per_page: int = 5) -> dict:
    """Search OpenAlex."""
    params = {
        "search": query,
        "per_page": str(per_page),
        "mailto": OPENALEX_MAILTO
    }
    if author:
        params["filter"] = f"author.search:{author}"
    qs = urllib.parse.urlencode(params)
    return _fetch_json(f"https://api.openalex.org/works?{qs}") or {}


def search_core(query: str, limit: int = 5) -> dict:
    """Search CORE (431M papers)."""
    params = {"q": query, "limit": str(limit)}
    qs = urllib.parse.urlencode(params)
    return _fetch_json(f"https://api.core.ac.uk/v3/search/works?{qs}") or {}


def check_unpaywall(doi: str) -> dict:
    """Check Unpaywall for OA access."""
    url = f"https://api.unpaywall.org/v2/{urllib.parse.quote(doi, safe='')}?email={OPENALEX_MAILTO}"
    return _fetch_json(url) or {}


def search_pubmed(query: str, retmax: int = 5) -> dict:
    """Search PubMed."""
    params = {"db": "pubmed", "term": query, "retmax": str(retmax), "retmode": "json"}
    qs = urllib.parse.urlencode(params)
    return _fetch_json(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?{qs}") or {}


def check_wayback(url: str) -> dict:
    """Check Wayback Machine for archived version."""
    encoded = urllib.parse.quote(url, safe="")
    return _fetch_json(f"https://archive.org/wayback/available?url={encoded}") or {}


def check_retraction(doi: str) -> dict:
    """Check CrossRef metadata for retraction or correction notices."""
    result = resolve_crossref_doi(doi)
    if not result or "_error" in result:
        return {"doi": doi, "retracted": None, "error": "Could not resolve DOI"}

    message = result.get("message", {})
    updates = message.get("update-to", [])
    retracted = any(u.get("type") == "retraction" for u in updates)
    corrected = any(u.get("type") in ("correction", "erratum") for u in updates)

    return {
        "doi": doi,
        "retracted": retracted,
        "corrected": corrected,
        "updates": updates
    }

# ---------------------------------------------------------------------------
# Resolution pipeline
# ---------------------------------------------------------------------------

def resolve_citation(citation: dict, cache: ResponseCache, provenance: ProvenanceStore) -> dict:
    """
    Resolve a single citation through the trust hierarchy.

    citation should have at least some of: title, author, year, doi, url

    Returns a resolution result with confidence level and stored provenance refs.
    """
    ref_id = citation.get("ref_id", "unknown")
    doi = citation.get("doi", "")
    url = citation.get("url", "")
    title = citation.get("title", "")
    author = citation.get("author", "")
    year = citation.get("year", "")

    result = {
        "ref_id": ref_id,
        "resolved": False,
        "confidence": "unretrievable",
        "source_tier": None,
        "metadata": {},
        "oa_url": None,
        "provenance_refs": []
    }

    # --- Tier 2: DOI resolution ---
    if doi:
        cache_key = f"crossref:doi:{doi}"
        cr_result = cache.get(cache_key)
        if cr_result is None:
            cr_result = resolve_crossref_doi(doi)
            cache.set(cache_key, cr_result)
            time.sleep(RATE_LIMIT_DELAY)

        if cr_result and "_error" not in cr_result and "message" in cr_result:
            prov_ref = provenance.store(ref_id, "crossref", cr_result)
            result["provenance_refs"].append(prov_ref)
            msg = cr_result["message"]
            result["resolved"] = True
            result["confidence"] = "metadata-only verified"
            result["source_tier"] = "crossref-doi"
            result["metadata"] = {
                "title": msg.get("title", [""])[0] if isinstance(msg.get("title"), list) else msg.get("title", ""),
                "authors": [a.get("family", "") + ", " + a.get("given", "") for a in msg.get("author", [])],
                "year": str(msg.get("published-print", {}).get("date-parts", [[""]])[0][0]
                         or msg.get("published-online", {}).get("date-parts", [[""]])[0][0] or ""),
                "venue": msg.get("container-title", [""])[0] if isinstance(msg.get("container-title"), list) else msg.get("container-title", ""),
                "doi": msg.get("DOI", doi)
            }

            # Check Unpaywall for OA PDF
            up_key = f"unpaywall:{doi}"
            up_result = cache.get(up_key)
            if up_result is None:
                up_result = check_unpaywall(doi)
                cache.set(up_key, up_result)
                time.sleep(RATE_LIMIT_DELAY)

            if up_result and "_error" not in up_result:
                prov_ref = provenance.store(ref_id, "unpaywall", up_result)
                result["provenance_refs"].append(prov_ref)
                best_oa = up_result.get("best_oa_location", {})
                if best_oa and best_oa.get("url_for_pdf"):
                    result["oa_url"] = best_oa["url_for_pdf"]
                    result["confidence"] = "full-text verified"

            return result

    # --- Tier 3: Search by title + author ---
    if title:
        # CrossRef search
        cache_key = f"crossref:search:{title}:{author}"
        cr_result = cache.get(cache_key)
        if cr_result is None:
            cr_result = search_crossref(title, author)
            cache.set(cache_key, cr_result)
            time.sleep(RATE_LIMIT_DELAY)

        if cr_result and "_error" not in cr_result:
            items = cr_result.get("message", {}).get("items", [])
            from fuzzy_match import best_match
            match = best_match(title, author, year, items, source="crossref")
            if match:
                prov_ref = provenance.store(ref_id, "crossref-search", cr_result)
                result["provenance_refs"].append(prov_ref)
                result["resolved"] = True
                result["confidence"] = "metadata-only verified"
                result["source_tier"] = "crossref-search"
                result["metadata"] = match
                # Try Unpaywall if DOI found
                found_doi = match.get("doi", "")
                if found_doi:
                    up_key = f"unpaywall:{found_doi}"
                    up_result = cache.get(up_key)
                    if up_result is None:
                        up_result = check_unpaywall(found_doi)
                        cache.set(up_key, up_result)
                        time.sleep(RATE_LIMIT_DELAY)
                    if up_result and "_error" not in up_result:
                        prov_ref = provenance.store(ref_id, "unpaywall", up_result)
                        result["provenance_refs"].append(prov_ref)
                        best_oa = up_result.get("best_oa_location", {})
                        if best_oa and best_oa.get("url_for_pdf"):
                            result["oa_url"] = best_oa["url_for_pdf"]
                            result["confidence"] = "full-text verified"
                return result

        # Semantic Scholar search
        cache_key = f"s2:search:{title}:{author}"
        s2_result = cache.get(cache_key)
        if s2_result is None:
            s2_result = search_semantic_scholar(f"{title} {author}".strip())
            cache.set(cache_key, s2_result)
            time.sleep(RATE_LIMIT_DELAY)

        if s2_result and "_error" not in s2_result:
            papers = s2_result.get("data", [])
            from fuzzy_match import best_match
            match = best_match(title, author, year, papers, source="s2")
            if match:
                prov_ref = provenance.store(ref_id, "semantic-scholar", s2_result)
                result["provenance_refs"].append(prov_ref)
                result["resolved"] = True
                result["confidence"] = "abstract-only verified" if match.get("abstract") else "metadata-only verified"
                result["source_tier"] = "semantic-scholar"
                result["metadata"] = match
                return result

        # OpenAlex search
        cache_key = f"openalex:search:{title}:{author}"
        oa_result = cache.get(cache_key)
        if oa_result is None:
            oa_result = search_openalex(title, author)
            cache.set(cache_key, oa_result)
            time.sleep(RATE_LIMIT_DELAY)

        if oa_result and "_error" not in oa_result:
            works = oa_result.get("results", [])
            from fuzzy_match import best_match
            match = best_match(title, author, year, works, source="openalex")
            if match:
                prov_ref = provenance.store(ref_id, "openalex", oa_result)
                result["provenance_refs"].append(prov_ref)
                result["resolved"] = True
                result["confidence"] = "metadata-only verified"
                result["source_tier"] = "openalex"
                result["metadata"] = match
                return result

        # CORE search
        cache_key = f"core:search:{title}"
        core_result = cache.get(cache_key)
        if core_result is None:
            core_result = search_core(title)
            cache.set(cache_key, core_result)
            time.sleep(RATE_LIMIT_DELAY)

        if core_result and "_error" not in core_result:
            hits = core_result.get("results", [])
            if hits:
                prov_ref = provenance.store(ref_id, "core", core_result)
                result["provenance_refs"].append(prov_ref)
                result["resolved"] = True
                result["confidence"] = "abstract-only verified" if hits[0].get("abstract") else "metadata-only verified"
                result["source_tier"] = "core"
                result["metadata"] = {
                    "title": hits[0].get("title", ""),
                    "authors": [a.get("name", "") for a in hits[0].get("authors", [])],
                    "year": str(hits[0].get("yearPublished", "")),
                }
                return result

    # --- Tier 4: URL check + Wayback ---
    if url:
        url_status = _check_url(url)
        if url_status.get("live"):
            result["resolved"] = True
            result["confidence"] = "full-text verified"
            result["source_tier"] = "direct-url"
            result["metadata"] = {"url": url}
            prov_ref = provenance.store(ref_id, "url-check", url_status)
            result["provenance_refs"].append(prov_ref)
            return result
        else:
            # Try Wayback
            cache_key = f"wayback:{url}"
            wb_result = cache.get(cache_key)
            if wb_result is None:
                wb_result = check_wayback(url)
                cache.set(cache_key, wb_result)
                time.sleep(RATE_LIMIT_DELAY)

            snapshots = wb_result.get("archived_snapshots", {})
            closest = snapshots.get("closest", {})
            if closest.get("available"):
                result["resolved"] = True
                result["confidence"] = "full-text verified"
                result["source_tier"] = "wayback"
                result["metadata"] = {"url": url, "wayback_url": closest.get("url", "")}
                prov_ref = provenance.store(ref_id, "wayback", wb_result)
                result["provenance_refs"].append(prov_ref)
                return result

    return result


def resolve_batch(citations: list[dict], output_path: str | None = None) -> list[dict]:
    """Resolve a batch of citations. Returns list of results."""
    cache = ResponseCache()
    provenance = ProvenanceStore()
    results = []

    for i, citation in enumerate(citations):
        print(f"Resolving {i+1}/{len(citations)}: {citation.get('title', citation.get('doi', citation.get('url', '?')))[:60]}...",
              file=sys.stderr)
        result = resolve_citation(citation, cache, provenance)
        results.append(result)

    summary = {
        "total": len(results),
        "resolved": sum(1 for r in results if r["resolved"]),
        "full_text": sum(1 for r in results if r["confidence"] == "full-text verified"),
        "abstract_only": sum(1 for r in results if r["confidence"] == "abstract-only verified"),
        "metadata_only": sum(1 for r in results if r["confidence"] == "metadata-only verified"),
        "unretrievable": sum(1 for r in results if r["confidence"] == "unretrievable"),
    }

    output = {
        "summary": summary,
        "results": results,
        "provenance": provenance.entries,
        "cache_stats": cache.stats()
    }

    if output_path:
        Path(output_path).write_text(json.dumps(output, indent=2, default=str))
        print(f"Results written to {output_path}", file=sys.stderr)
    else:
        print(json.dumps(output, indent=2, default=str))

    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="APODICTIC Academic API Client")
    sub = parser.add_subparsers(dest="command")

    # resolve
    res = sub.add_parser("resolve", help="Resolve a single citation")
    res.add_argument("--title", default="")
    res.add_argument("--author", default="")
    res.add_argument("--year", default="")
    res.add_argument("--doi", default="")
    res.add_argument("--url", default="")

    # batch
    batch = sub.add_parser("batch", help="Resolve a batch of citations from JSON")
    batch.add_argument("--input", required=True, help="Input JSON file (array of citation objects)")
    batch.add_argument("--output", default=None, help="Output JSON file")

    # check-url
    curl = sub.add_parser("check-url", help="Check if a URL is live")
    curl.add_argument("--url", required=True)

    # retraction-check
    ret = sub.add_parser("retraction-check", help="Check for retractions via CrossRef")
    ret.add_argument("--doi", required=True)

    args = parser.parse_args()

    if args.command == "resolve":
        cache = ResponseCache()
        provenance = ProvenanceStore()
        citation = {
            "ref_id": "cli-1",
            "title": args.title,
            "author": args.author,
            "year": args.year,
            "doi": args.doi,
            "url": args.url
        }
        result = resolve_citation(citation, cache, provenance)
        print(json.dumps(result, indent=2, default=str))

    elif args.command == "batch":
        citations = json.loads(Path(args.input).read_text())
        resolve_batch(citations, args.output)

    elif args.command == "check-url":
        result = _check_url(args.url)
        print(json.dumps(result, indent=2))

    elif args.command == "retraction-check":
        result = check_retraction(args.doi)
        print(json.dumps(result, indent=2, default=str))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
