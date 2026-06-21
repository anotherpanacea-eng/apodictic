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
from api_reliability import (
    ProviderBudget,
    CircuitBreaker,
    ReliabilityLedger,
    TTL,
    PROVIDERS,
    reliability_enabled,
)

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

# HTTP retry policy (Phase 5). A rate-limit (429) or transient 5xx/timeout must not
# be swallowed into {_error} and mistaken for a ghost citation. Set
# APODICTIC_HTTP_RETRIES=0 to disable (e.g., offline tests).
_HTTP_MAX_RETRIES = int(os.environ.get("APODICTIC_HTTP_RETRIES", "3"))
_HTTP_BACKOFF_BASE = float(os.environ.get("APODICTIC_HTTP_BACKOFF", "2"))
_RETRYABLE_STATUS = {429, 500, 502, 503, 504}


def _default_cache_dir() -> str:
    """Run-local disk cache directory: $APODICTIC_CACHE_DIR or ./.apodictic_run/cache.
    Engaging disk persistence makes citation lookups idempotent across runs."""
    return os.environ.get("APODICTIC_CACHE_DIR") or str(Path(".apodictic_run") / "cache")


def _retry_after_delay(exc, fallback: float) -> float:
    """Seconds to wait before retry, honoring a Retry-After header (delta-seconds
    form) when present and sane; otherwise the exponential-backoff fallback."""
    hdrs = getattr(exc, "headers", None)
    retry_after = hdrs.get("Retry-After") if hdrs else None
    if retry_after:
        try:
            return min(float(retry_after), 60.0)
        except (TypeError, ValueError):
            pass  # HTTP-date form not parsed; fall back to backoff
    return fallback


def _fetch_json(url: str, headers: dict | None = None, timeout: int = 15,
                provider: str | None = None, ledger: "ReliabilityLedger | None" = None) -> dict | None:
    """Fetch a URL and parse as JSON. Retries 429/5xx and transient network errors
    with bounded exponential backoff (honoring Retry-After). On exhaustion returns
    the existing {_error} dict so callers are unchanged.

    Reliability layer (research-reliability-layer): when a `ledger` and a
    `provider` are supplied, the call is GATED first — an open circuit or an
    exhausted budget short-circuits BEFORE any network/budget cost and returns a
    `{_skipped}` sentinel so the resolver falls through to the next tier exactly
    as it does today for an `_error`, while resolve_citation can tell the tier was
    NOT-CHECKED (provider degraded) rather than NOT-FOUND. The outcome of a call
    that actually fires is recorded on the ledger (error vs ok), which feeds the
    circuit breaker. A bare `_fetch_json(url)` (no ledger) is byte-for-byte
    today's behavior (AC-13)."""
    if ledger is not None and provider is not None:
        if not ledger.allow_call(provider):
            return {"_skipped": True, "_provider": provider, "_url": url}

    result = _fetch_json_network(url, headers, timeout)

    # Record the outcome of a call that actually fired so the breaker can open on
    # consecutive failures. allow_call() already charged the budget above.
    if ledger is not None and provider is not None:
        ledger.record(provider, result)
    return result


def _fetch_json_network(url: str, headers: dict | None = None, timeout: int = 15) -> dict | None:
    """The Phase 5 network call (backoff / Retry-After / no-sticky-error shape),
    factored out so the reliability gate/record wraps a single body."""
    req_headers = {"User-Agent": f"APODICTIC/1.0 (mailto:{CROSSREF_MAILTO})"}
    if headers:
        req_headers.update(headers)
    if S2_API_KEY and "semanticscholar" in url:
        req_headers["x-api-key"] = S2_API_KEY

    req = urllib.request.Request(url, headers=req_headers)
    delay = _HTTP_BACKOFF_BASE
    last_error = None
    for attempt in range(_HTTP_MAX_RETRIES + 1):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            last_error = e
            if e.code in _RETRYABLE_STATUS and attempt < _HTTP_MAX_RETRIES:
                time.sleep(_retry_after_delay(e, delay))
                delay *= 2
                continue
            return {"_error": str(e), "_url": url, "_status": e.code}
        except (urllib.error.URLError, TimeoutError) as e:
            last_error = e
            if attempt < _HTTP_MAX_RETRIES:
                time.sleep(delay)
                delay *= 2
                continue
            return {"_error": str(e), "_url": url}
        except json.JSONDecodeError as e:
            return {"_error": str(e), "_url": url}
    return {"_error": str(last_error), "_url": url}


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

def resolve_crossref_doi(doi: str, ledger=None) -> dict:
    """Resolve a DOI via CrossRef."""
    url = f"https://api.crossref.org/works/{urllib.parse.quote(doi, safe='')}"
    return _fetch_json(url, provider="crossref", ledger=ledger) or {}


def search_crossref(title: str, author: str = "", rows: int = 5, ledger=None) -> dict:
    """Search CrossRef by bibliographic query."""
    params = {"query.bibliographic": title, "rows": str(rows)}
    if author:
        params["query.author"] = author
    qs = urllib.parse.urlencode(params)
    return _fetch_json(f"https://api.crossref.org/works?{qs}", provider="crossref", ledger=ledger) or {}


def search_semantic_scholar(query: str, limit: int = 5, ledger=None) -> dict:
    """Search Semantic Scholar."""
    params = {
        "query": query,
        "limit": str(limit),
        "fields": "title,authors,year,externalIds,venue,citationCount,abstract"
    }
    qs = urllib.parse.urlencode(params)
    return _fetch_json(f"https://api.semanticscholar.org/graph/v1/paper/search?{qs}",
                       provider="semantic-scholar", ledger=ledger) or {}


def get_s2_citations(paper_id: str, direction: str = "citations", limit: int = 20, ledger=None) -> dict:
    """Get citations or references for a paper via Semantic Scholar."""
    params = {"fields": "title,authors,year,venue,citationCount", "limit": str(limit)}
    qs = urllib.parse.urlencode(params)
    return _fetch_json(
        f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}/{direction}?{qs}",
        provider="semantic-scholar", ledger=ledger
    ) or {}


def search_openalex(query: str, author: str = "", per_page: int = 5, ledger=None) -> dict:
    """Search OpenAlex."""
    params = {
        "search": query,
        "per_page": str(per_page),
        "mailto": OPENALEX_MAILTO
    }
    if author:
        params["filter"] = f"author.search:{author}"
    qs = urllib.parse.urlencode(params)
    return _fetch_json(f"https://api.openalex.org/works?{qs}", provider="openalex", ledger=ledger) or {}


def search_core(query: str, limit: int = 5, ledger=None) -> dict:
    """Search CORE (431M papers)."""
    params = {"q": query, "limit": str(limit)}
    qs = urllib.parse.urlencode(params)
    return _fetch_json(f"https://api.core.ac.uk/v3/search/works?{qs}", provider="core", ledger=ledger) or {}


def check_unpaywall(doi: str, ledger=None) -> dict:
    """Check Unpaywall for OA access."""
    url = f"https://api.unpaywall.org/v2/{urllib.parse.quote(doi, safe='')}?email={OPENALEX_MAILTO}"
    return _fetch_json(url, provider="unpaywall", ledger=ledger) or {}


def search_pubmed(query: str, retmax: int = 5, ledger=None) -> dict:
    """Search PubMed."""
    params = {"db": "pubmed", "term": query, "retmax": str(retmax), "retmode": "json"}
    qs = urllib.parse.urlencode(params)
    return _fetch_json(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?{qs}",
                       provider="pubmed", ledger=ledger) or {}


def check_wayback(url: str, ledger=None) -> dict:
    """Check Wayback Machine for archived version."""
    encoded = urllib.parse.quote(url, safe="")
    return _fetch_json(f"https://archive.org/wayback/available?url={encoded}",
                       provider="wayback", ledger=ledger) or {}


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

def _is_skipped(resp) -> bool:
    """A `_skipped` sentinel from _fetch_json means the provider was degraded
    (circuit open / budget exhausted) and the tier was NOT-CHECKED, not
    NOT-FOUND."""
    return isinstance(resp, dict) and resp.get("_skipped") is True


def _is_error(resp) -> bool:
    """An `_error` dict from _fetch_json means the provider call FAILED
    (timeout / 429 / 5xx after retries exhausted). Like a `_skipped`, the tier
    was NOT-CHECKED (we couldn't get an answer), not NOT-FOUND (we looked,
    nothing there). Distinct from `_skipped`, which is a pre-call degradation
    (circuit open / budget exhausted)."""
    return isinstance(resp, dict) and "_error" in resp


def _unanswered(resp) -> bool:
    """True when a provider did not return a usable answer for this citation:
    either skipped before the call (degraded) or errored after retries. Both
    mean the tier is NOT-CHECKED for this citation, never NOT-FOUND."""
    return _is_skipped(resp) or _is_error(resp)


def resolve_citation(citation: dict, cache: ResponseCache, provenance: ProvenanceStore,
                     ledger: "ReliabilityLedger | None" = None) -> dict:
    """
    Resolve a single citation through the trust hierarchy.

    citation should have at least some of: title, author, year, doi, url

    Returns a resolution result with confidence level and stored provenance refs.

    When a `ledger` is supplied (research-reliability-layer), each tier's call is
    rationed by the per-provider budget and circuit breaker, and the result gains
    a `resolution_status ∈ {resolved, not-found, not-checked}`: a tier cut short
    by a degraded provider sets `not-checked` (so an `unretrievable` verdict can
    be reported honestly as NOT-CHECKED rather than NOT-FOUND). Without a ledger
    the result is today's shape plus `resolution_status` defaulting to the
    found/not-found split (AC-13 — additive, no behavior change).
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
    # Providers whose tier was NOT-CHECKED for this citation (degraded → skipped).
    not_checked: list[str] = []
    _meta_ttl = TTL.metadata_seconds()
    _wb_ttl = TTL.wayback_seconds()

    # --- Tier 2: DOI resolution ---
    if doi:
        cache_key = f"crossref:doi:{doi}"
        cr_result = cache.get(cache_key, ttl_seconds=_meta_ttl)
        if cr_result is None:
            cr_result = resolve_crossref_doi(doi, ledger=ledger)
            if _unanswered(cr_result):
                # Degraded (skip) OR failed (error after retries): the provider
                # did not answer → NOT-CHECKED for this citation, and do not
                # cache a non-answer (a transient 5xx/timeout is not a fact).
                not_checked.append("crossref")
            else:
                cache.set(cache_key, cr_result, ttl=_meta_ttl)
            time.sleep(RATE_LIMIT_DELAY)

        if cr_result and "_error" not in cr_result and "message" in cr_result:
            prov_ref = provenance.store(ref_id, "crossref", cr_result)
            result["provenance_refs"].append(prov_ref)
            msg = cr_result["message"]
            # Retraction (Phase 5) is derived from the SAME CrossRef metadata
            # (message.update-to) — no second CrossRef call. A retracted source is a
            # citation problem the audit must not silently pass.
            if any(u.get("type") == "retraction" for u in msg.get("update-to", [])):
                result["retracted"] = True
                result["retraction_note"] = "Source is retracted per CrossRef metadata."
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

            # Check Unpaywall for OA PDF. Unpaywall is an OA-enrichment of an
            # ALREADY-resolved citation, not a resolution provider, so a
            # skip/error here does not flip resolution_status to NOT-CHECKED —
            # but a transient non-answer must still not be cached as fact.
            up_key = f"unpaywall:{doi}"
            up_result = cache.get(up_key, ttl_seconds=_meta_ttl)
            if up_result is None:
                up_result = check_unpaywall(doi, ledger=ledger)
                if not _unanswered(up_result):
                    cache.set(up_key, up_result, ttl=_meta_ttl)
                time.sleep(RATE_LIMIT_DELAY)

            if up_result and not _unanswered(up_result):
                prov_ref = provenance.store(ref_id, "unpaywall", up_result)
                result["provenance_refs"].append(prov_ref)
                best_oa = up_result.get("best_oa_location", {})
                if best_oa and best_oa.get("url_for_pdf"):
                    result["oa_url"] = best_oa["url_for_pdf"]
                    result["confidence"] = "full-text verified"

            result["resolution_status"] = "resolved"
            result["degraded_providers"] = ledger.degraded_providers() if ledger else []
            return result

    # --- Tier 3: Search by title + author ---
    if title:
        # CrossRef search
        cache_key = f"crossref:search:{title}:{author}"
        cr_result = cache.get(cache_key, ttl_seconds=_meta_ttl)
        if cr_result is None:
            cr_result = search_crossref(title, author, ledger=ledger)
            if _unanswered(cr_result):
                not_checked.append("crossref")  # skip OR error → NOT-CHECKED; don't cache
            else:
                cache.set(cache_key, cr_result, ttl=_meta_ttl)
            time.sleep(RATE_LIMIT_DELAY)

        if cr_result and not _unanswered(cr_result):
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
                    up_result = cache.get(up_key, ttl_seconds=_meta_ttl)
                    if up_result is None:
                        up_result = check_unpaywall(found_doi, ledger=ledger)
                        if not _unanswered(up_result):
                            cache.set(up_key, up_result, ttl=_meta_ttl)
                        time.sleep(RATE_LIMIT_DELAY)
                    if up_result and not _unanswered(up_result):
                        prov_ref = provenance.store(ref_id, "unpaywall", up_result)
                        result["provenance_refs"].append(prov_ref)
                        best_oa = up_result.get("best_oa_location", {})
                        if best_oa and best_oa.get("url_for_pdf"):
                            result["oa_url"] = best_oa["url_for_pdf"]
                            result["confidence"] = "full-text verified"
                result["resolution_status"] = "resolved"
                result["degraded_providers"] = ledger.degraded_providers() if ledger else []
                return result

        # Semantic Scholar search
        cache_key = f"s2:search:{title}:{author}"
        s2_result = cache.get(cache_key, ttl_seconds=_meta_ttl)
        if s2_result is None:
            s2_result = search_semantic_scholar(f"{title} {author}".strip(), ledger=ledger)
            if _unanswered(s2_result):
                not_checked.append("semantic-scholar")  # skip OR error → NOT-CHECKED; don't cache
            else:
                cache.set(cache_key, s2_result, ttl=_meta_ttl)
            time.sleep(RATE_LIMIT_DELAY)

        if s2_result and not _unanswered(s2_result):
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
                result["resolution_status"] = "resolved"
                result["degraded_providers"] = ledger.degraded_providers() if ledger else []
                return result

        # OpenAlex search
        cache_key = f"openalex:search:{title}:{author}"
        oa_result = cache.get(cache_key, ttl_seconds=_meta_ttl)
        if oa_result is None:
            oa_result = search_openalex(title, author, ledger=ledger)
            if _unanswered(oa_result):
                not_checked.append("openalex")  # skip OR error → NOT-CHECKED; don't cache
            else:
                cache.set(cache_key, oa_result, ttl=_meta_ttl)
            time.sleep(RATE_LIMIT_DELAY)

        if oa_result and not _unanswered(oa_result):
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
                result["resolution_status"] = "resolved"
                result["degraded_providers"] = ledger.degraded_providers() if ledger else []
                return result

        # CORE search
        cache_key = f"core:search:{title}"
        core_result = cache.get(cache_key, ttl_seconds=_meta_ttl)
        if core_result is None:
            core_result = search_core(title, ledger=ledger)
            if _unanswered(core_result):
                not_checked.append("core")  # skip OR error → NOT-CHECKED; don't cache
            else:
                cache.set(cache_key, core_result, ttl=_meta_ttl)
            time.sleep(RATE_LIMIT_DELAY)

        if core_result and not _unanswered(core_result):
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
                result["resolution_status"] = "resolved"
                result["degraded_providers"] = ledger.degraded_providers() if ledger else []
                return result

    # --- Tier 4: URL check + Wayback ---
    if url:
        # URL liveness is not budget/breaker-gated (it is not one of the seven
        # index providers and is never disk-cached — a 404 today may be live
        # tomorrow). It remains run-local exactly as before.
        url_status = _check_url(url)
        if url_status.get("live"):
            result["resolved"] = True
            result["confidence"] = "full-text verified"
            result["source_tier"] = "direct-url"
            result["metadata"] = {"url": url}
            prov_ref = provenance.store(ref_id, "url-check", url_status)
            result["provenance_refs"].append(prov_ref)
            result["resolution_status"] = "resolved"
            result["degraded_providers"] = ledger.degraded_providers() if ledger else []
            return result
        else:
            # Try Wayback
            cache_key = f"wayback:{url}"
            wb_result = cache.get(cache_key, ttl_seconds=_wb_ttl)
            if wb_result is None:
                wb_result = check_wayback(url, ledger=ledger)
                if _unanswered(wb_result):
                    not_checked.append("wayback")  # skip OR error → NOT-CHECKED; don't cache
                else:
                    cache.set(cache_key, wb_result, ttl=_wb_ttl)
                time.sleep(RATE_LIMIT_DELAY)

            if wb_result and not _unanswered(wb_result):
                snapshots = wb_result.get("archived_snapshots", {})
                closest = snapshots.get("closest", {})
                if closest.get("available"):
                    result["resolved"] = True
                    result["confidence"] = "full-text verified"
                    result["source_tier"] = "wayback"
                    result["metadata"] = {"url": url, "wayback_url": closest.get("url", "")}
                    prov_ref = provenance.store(ref_id, "wayback", wb_result)
                    result["provenance_refs"].append(prov_ref)
                    result["resolution_status"] = "resolved"
                    result["degraded_providers"] = ledger.degraded_providers() if ledger else []
                    return result

    # Unresolved. Classify honesty: a tier cut short by a degraded provider makes
    # this NOT-CHECKED (we couldn't look), not NOT-FOUND (we looked, nothing
    # there). The Firewall is one-directional: resolution_status is never set to
    # "resolved" on an unresolved result.
    if not_checked:
        result["resolution_status"] = "not-checked"
    else:
        result["resolution_status"] = "not-found"
    result["not_checked_providers"] = sorted(set(not_checked))
    result["degraded_providers"] = ledger.degraded_providers() if ledger else []
    return result


def resolve_batch(citations: list[dict], output_path: str | None = None) -> list[dict]:
    """Resolve a batch of citations. Returns list of results.

    A per-run ReliabilityLedger (per-provider budget + circuit breaker) is
    constructed here — the same place that already constructs `cache` and
    `provenance` — and threaded through resolution. Its `snapshot()` is emitted
    as the `reliability` block alongside `cache_stats`. The ledger is default-on;
    APODICTIC_RELIABILITY=off omits the top-level `reliability` block. The
    additive per-result (`resolution_status`/`degraded_providers`) and summary
    (`not_checked`/`not_found`) keys remain — they are computed without a ledger
    (`degraded_providers` is then `[]`) and never alter a pre-existing value, so
    OFF leaves the legacy keys unchanged while staying additive — AC-13."""
    cache = ResponseCache(_default_cache_dir())
    provenance = ProvenanceStore()
    ledger = ReliabilityLedger() if reliability_enabled() else None
    results = []

    for i, citation in enumerate(citations):
        print(f"Resolving {i+1}/{len(citations)}: {citation.get('title', citation.get('doi', citation.get('url', '?')))[:60]}...",
              file=sys.stderr)
        result = resolve_citation(citation, cache, provenance, ledger=ledger)
        results.append(result)

    summary = {
        "total": len(results),
        "resolved": sum(1 for r in results if r["resolved"]),
        "full_text": sum(1 for r in results if r["confidence"] == "full-text verified"),
        "abstract_only": sum(1 for r in results if r["confidence"] == "abstract-only verified"),
        "metadata_only": sum(1 for r in results if r["confidence"] == "metadata-only verified"),
        "unretrievable": sum(1 for r in results if r["confidence"] == "unretrievable"),
        # How many unretrievables were NOT-CHECKED (provider degraded) vs
        # genuinely NOT-FOUND — the honesty payoff the ROADMAP named.
        "not_checked": sum(1 for r in results if r.get("resolution_status") == "not-checked"),
        "not_found": sum(1 for r in results if r.get("resolution_status") == "not-found"),
    }

    output = {
        "summary": summary,
        "results": results,
        "provenance": provenance.entries,
        "cache_stats": cache.stats(),
    }
    if ledger is not None:
        output["reliability"] = ledger.snapshot()

    if output_path:
        Path(output_path).write_text(json.dumps(output, indent=2, default=str))
        print(f"Results written to {output_path}", file=sys.stderr)
    else:
        print(json.dumps(output, indent=2, default=str))

    return results


# ---------------------------------------------------------------------------
# Self-test (introduced with the reliability layer). Fully OFFLINE: the network
# body (_fetch_json_network) is monkeypatched and APODICTIC_HTTP_RETRIES=0, so no
# socket is ever opened. AC-7 (resolution_status honesty) is the core claim and
# carries a dedicated negative fixture (not-checked vs not-found).
# ---------------------------------------------------------------------------

def run_self_test() -> int:
    import tempfile

    failures: list[str] = []
    passed = [0]

    def expect(name, got, want):
        if got == want:
            passed[0] += 1
        else:
            failures.append(f"{name}: got {got!r}, want {want!r}")

    def expect_true(name, cond):
        expect(name, bool(cond), True)

    os.environ["APODICTIC_HTTP_RETRIES"] = "0"
    # Canned CrossRef DOI hit (Tier 2 — no fuzzy match needed; just needs message).
    GOOD_DOI_RESP = {"message": {"DOI": "10.1/good", "title": ["A Real Paper"],
                                 "author": [{"family": "Vaswani", "given": "A"}]}}

    def make_network(routes: dict):
        """routes: substring → canned response (or an _error/_skipped dict)."""
        def fake(url, headers=None, timeout=15):
            for frag, resp in routes.items():
                if frag in url:
                    return resp
            return {}  # default: empty (a clean 0-match, NOT an error)
        return fake

    global _fetch_json_network
    orig_network = _fetch_json_network
    orig_check_url = globals()["_check_url"]
    # Neutralize URL liveness (no network) and rate-limit sleeps for the test.
    globals()["_check_url"] = lambda url, timeout=10: {"url": url, "status": None, "live": False}
    global RATE_LIMIT_DELAY
    orig_delay = RATE_LIMIT_DELAY
    RATE_LIMIT_DELAY = 0.0
    try:
        # --- AC-7 case A: clean resolve via CrossRef DOI → resolution_status=resolved
        with tempfile.TemporaryDirectory() as d:
            os.environ["APODICTIC_CACHE_DIR"] = d
            _fetch_json_network = make_network({
                "crossref.org/works/": GOOD_DOI_RESP,
                "unpaywall.org": {},  # no OA — fine
            })
            led = ReliabilityLedger()
            cache = ResponseCache(d)
            prov = ProvenanceStore()
            r = resolve_citation({"ref_id": "A", "doi": "10.1/good"}, cache, prov, ledger=led)
            expect_true("ac7_caseA_resolved", r["resolved"])
            expect("ac7_caseA_status", r.get("resolution_status"), "resolved")

        # --- AC-7 case B: genuinely 0-matches every HEALTHY provider → not-found
        with tempfile.TemporaryDirectory() as d:
            os.environ["APODICTIC_CACHE_DIR"] = d
            _fetch_json_network = make_network({})  # everything returns {} (clean empty)
            led = ReliabilityLedger()
            cache = ResponseCache(d)
            prov = ProvenanceStore()
            r = resolve_citation({"ref_id": "B", "title": "Nonexistent Paper Title XYZ",
                                  "author": "Nobody"}, cache, prov, ledger=led)
            expect_true("ac7_caseB_unresolved", r["resolved"] is False)
            expect("ac7_caseB_status", r.get("resolution_status"), "not-found")
            expect("ac7_caseB_no_not_checked", r.get("not_checked_providers"), [])

        # --- AC-7 case C: resolvable ONLY via a forced-degraded provider → not-checked
        # Force crossref AND openalex AND core AND s2 budgets to 0 so every search
        # tier is skipped (degraded), leaving the citation NOT-CHECKED, not NOT-FOUND.
        with tempfile.TemporaryDirectory() as d:
            os.environ["APODICTIC_CACHE_DIR"] = d
            # If a tier DID fire it would match; but budgets are 0 so it can't.
            _fetch_json_network = make_network({"semanticscholar": {
                "data": [{"title": "Findable Only In S2", "authors": [{"name": "Q"}],
                          "year": 2020, "abstract": "x"}]}})
            zero = ProviderBudget({p: 0 for p in PROVIDERS})
            led = ReliabilityLedger(budget=zero)
            cache = ResponseCache(d)
            prov = ProvenanceStore()
            r = resolve_citation({"ref_id": "C", "title": "Findable Only In S2",
                                  "author": "Q", "year": "2020"}, cache, prov, ledger=led)
            expect_true("ac7_caseC_unresolved", r["resolved"] is False)
            expect("ac7_caseC_status", r.get("resolution_status"), "not-checked")
            expect_true("ac7_caseC_names_providers", len(r.get("not_checked_providers", [])) > 0)
            # AC-12 firewall: an unresolved result is NEVER "resolved".
            expect_true("ac12_never_resolved_on_unresolved",
                        r.get("resolution_status") != "resolved")

        # --- AC-7 case D: every title-search provider ERRORS (timeout/429/5xx after
        # retries) → NOT-CHECKED, not NOT-FOUND. A real `_error` (not a `_skipped`)
        # must record the provider as not-checked for this citation, otherwise an
        # all-errored citation wrongly reports a confident `not-found` with an empty
        # not_checked list (Codex round-9 P1). Distinct from case C, where the gate
        # SKIPS the call pre-flight; here every call FIRES and returns `_error`.
        with tempfile.TemporaryDirectory() as d:
            os.environ["APODICTIC_CACHE_DIR"] = d
            # Every provider call that fires returns a hard error after retries.
            def _all_error(url, headers=None, timeout=15):
                return {"_error": "HTTP Error 503: Service Unavailable",
                        "_url": url, "_status": 503}
            _fetch_json_network = _all_error
            led = ReliabilityLedger()
            cache = ResponseCache(d)
            prov = ProvenanceStore()
            r = resolve_citation({"ref_id": "D", "title": "A Real Paper Nobody Could Reach",
                                  "author": "Smith", "year": "2021"}, cache, prov, ledger=led)
            expect_true("ac7_caseD_unresolved", r["resolved"] is False)
            # The core claim: an all-errored citation is NOT a confident not-found.
            expect("ac7_caseD_status", r.get("resolution_status"), "not-checked")
            expect_true("ac7_caseD_names_providers",
                        len(r.get("not_checked_providers", [])) > 0)
            expect_true("ac7_caseD_not_confidently_not_found",
                        r.get("resolution_status") != "not-found")

        # --- AC-8: batch output shape (reliability block present; legacy keys intact)
        with tempfile.TemporaryDirectory() as d:
            os.environ["APODICTIC_CACHE_DIR"] = d
            _fetch_json_network = make_network({"crossref.org/works/": GOOD_DOI_RESP})
            # capture stdout-free path by writing to a file
            out_path = str(Path(d) / "out.json")
            resolve_batch([{"ref_id": "1", "doi": "10.1/good"}], out_path)
            out = json.loads(Path(out_path).read_text())
            for k in ("summary", "results", "provenance", "cache_stats", "reliability"):
                expect_true(f"ac8_has_{k}", k in out)
            rel = out["reliability"]
            for k in ("providers", "events", "coverage"):
                expect_true(f"ac8_reliability_{k}", k in rel)
            expect_true("ac8_summary_has_not_checked", "not_checked" in out["summary"])

        # --- AC-13: APODICTIC_RELIABILITY=off → no reliability block, legacy shape
        with tempfile.TemporaryDirectory() as d:
            os.environ["APODICTIC_CACHE_DIR"] = d
            os.environ["APODICTIC_RELIABILITY"] = "off"
            _fetch_json_network = make_network({"crossref.org/works/": GOOD_DOI_RESP})
            out_path = str(Path(d) / "out.json")
            resolve_batch([{"ref_id": "1", "doi": "10.1/good"}], out_path)
            out = json.loads(Path(out_path).read_text())
            expect_true("ac13_off_no_reliability_block", "reliability" not in out)
            expect_true("ac13_off_still_resolves", out["summary"]["resolved"] == 1)
            os.environ.pop("APODICTIC_RELIABILITY", None)
    finally:
        _fetch_json_network = orig_network
        globals()["_check_url"] = orig_check_url
        RATE_LIMIT_DELAY = orig_delay
        os.environ.pop("APODICTIC_CACHE_DIR", None)
        os.environ.pop("APODICTIC_HTTP_RETRIES", None)

    total = passed[0] + len(failures)
    if failures:
        print(f"academic_apis self-test: FAIL ({len(failures)}/{total} checks failed)")
        for f in failures:
            print(f"  - {f}")
        return 1
    print(f"academic_apis self-test: PASS ({passed[0]}/{total} checks)")
    return 0


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
        cache = ResponseCache(_default_cache_dir())
        provenance = ProvenanceStore()
        ledger = ReliabilityLedger() if reliability_enabled() else None
        citation = {
            "ref_id": "cli-1",
            "title": args.title,
            "author": args.author,
            "year": args.year,
            "doi": args.doi,
            "url": args.url
        }
        result = resolve_citation(citation, cache, provenance, ledger=ledger)
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
    if len(sys.argv) >= 2 and sys.argv[1] == "--self-test":
        sys.exit(run_self_test())
    main()
