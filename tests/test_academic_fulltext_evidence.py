"""Locator-only resolution cannot claim that source content was read."""

import io
import json
import os
import socket
import sys
import tempfile
import unittest
import urllib.request
import urllib.response
from email.message import Message
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugins/apodictic"
                       / "skills/research-verification/scripts"))
import academic_apis as api
from provenance import ProvenanceStore
from response_cache import ResponseCache

DOI = "10.1234/synthetic"
OA = "https://example.org/synthetic.pdf"
DIRECT = "https://example.org/direct"
FALLBACK = "https://example.org/fallback"
ARCHIVE_SOURCE = "https://example.org/archived"
SNAPSHOT = "https://web.archive.org/web/20200101/https://example.org/archived"
CROSSREF = {"message": {"DOI": DOI, "title": ["Synthetic study"]}}
SEARCH = {"message": {"items": [{"DOI": DOI, "title": ["Synthetic study"]}]}}
UNPAYWALL = {"best_oa_location": {"url_for_pdf": OA}}
WAYBACK = {"archived_snapshots": {"closest": {"available": True, "url": SNAPSHOT}}}


class Body(io.BytesIO):
    def __init__(self):
        super().__init__(b"synthetic content that must remain unread")
        self.reads = 0

    def read(self, *args):
        self.reads += 1
        return super().read(*args)


class Transport(urllib.request.HTTPHandler, urllib.request.HTTPSHandler):
    """Only transport is synthetic; urllib still processes HTTP status and redirects."""

    def __init__(self, routes):
        super().__init__()
        self.routes = list(routes)
        self.requests = []
        self.bodies = []

    def http_open(self, req):
        self.requests.append((req.get_method(), req.full_url))
        if not self.routes:
            raise AssertionError("unexpected network request")
        method, url, status = self.routes.pop(0)
        if (req.get_method(), req.full_url) != (method, url):
            raise AssertionError((req.get_method(), req.full_url, method, url))
        body = Body()
        self.bodies.append(body)
        response = urllib.response.addinfourl(body, Message(), req.full_url, status)
        response.msg = "synthetic"
        return response

    https_open = http_open


class FullTextEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.cache = ResponseCache(self.temp.name)
        self.provenance = ProvenanceStore()

    def resolve(self, citation, routes=(), wayback=WAYBACK):
        transport = Transport(routes)
        build_opener = urllib.request.build_opener

        def offline_opener(*handlers):
            return build_opener(*handlers, transport, urllib.request.ProxyHandler({}))

        with (patch.object(urllib.request, "build_opener", offline_opener),
              patch.object(urllib.request, "urlopen", side_effect=AssertionError("live API")),
              patch.object(socket.socket, "connect", side_effect=AssertionError("live socket")),
              patch.object(api, "resolve_crossref_doi", return_value=CROSSREF),
              patch.object(api, "search_crossref", return_value=SEARCH),
              patch.object(api, "check_unpaywall", return_value=UNPAYWALL),
              patch.object(api, "check_wayback", return_value=wayback),
              patch.object(api.time, "sleep")):
            result = api.resolve_citation(citation, self.cache, self.provenance)
        self.assertEqual(transport.routes, [])
        self.assertTrue(all(body.reads == 0 for body in transport.bodies))
        return result, transport

    def assert_locator(self, result, source_tier):
        self.assertIs(result["resolved"], True)
        self.assertEqual(result["resolution_status"], "resolved")
        self.assertEqual(result["source_tier"], source_tier)
        self.assertEqual(result["confidence"], "metadata-only verified")
        self.assertNotEqual(result["confidence"], "full-text verified")
        self.assertTrue(result["provenance_refs"])
        self.assertIsInstance(result["metadata"], dict)
        self.assertIn("oa_url", result)

    def test_doi_and_title_search_oa_link_keep_metadata_evidence(self):
        for citation, tier, provenance_source in (
                ({"ref_id": "doi", "doi": DOI}, "crossref-doi", "crossref"),
                ({"ref_id": "search", "title": "Synthetic study"},
                 "crossref-search", "crossref-search")):
            with self.subTest(tier=tier):
                result, transport = self.resolve(citation)
                self.assert_locator(result, tier)
                self.assertEqual(transport.requests, [])
                self.assertEqual(result["oa_url"], OA)
                sources = {e["source"] for e in self.provenance.verify(citation["ref_id"])}
                self.assertEqual(sources, {provenance_source, "unpaywall"})

    def test_direct_url_head_and_get_fallback_are_liveness_only(self):
        for url, routes, methods in (
                (DIRECT, [("HEAD", DIRECT, 200)], ["HEAD"]),
                (FALLBACK, [("HEAD", FALLBACK, 405), ("GET", FALLBACK, 200)],
                 ["HEAD", "GET"])):
            with self.subTest(url=url):
                result, transport = self.resolve({"ref_id": url, "url": url}, routes)
                self.assert_locator(result, "direct-url")
                self.assertEqual(result["metadata"], {"url": url})
                self.assertEqual(result["url_check"]["check_status"], "live")
                self.assertEqual(result["url_check"]["method"], methods[-1])
                self.assertEqual([r[0] for r in transport.requests], methods)
                self.assertEqual([a["method"] for a in result["url_check"]["attempts"]], methods)
                self.assertEqual({e["source"] for e in self.provenance.verify(url)},
                                 {"url-check"})

    def test_wayback_availability_is_liveness_only(self):
        result, transport = self.resolve(
            {"ref_id": "wayback", "url": ARCHIVE_SOURCE},
            [("HEAD", ARCHIVE_SOURCE, 404)])
        self.assert_locator(result, "wayback")
        self.assertEqual(transport.requests, [("HEAD", ARCHIVE_SOURCE)])
        self.assertEqual(result["url_check"]["check_status"], "not-found")
        self.assertEqual(result["metadata"], {"url": ARCHIVE_SOURCE,
                                              "wayback_url": SNAPSHOT})
        self.assertEqual({e["source"] for e in self.provenance.verify("wayback")},
                         {"url-check", "wayback"})

    def test_serialized_batch_preserves_keys_counts_and_incomplete_url(self):
        routes = [("HEAD", DIRECT, 200), ("HEAD", FALLBACK, 405),
                  ("GET", FALLBACK, 200), ("HEAD", ARCHIVE_SOURCE, 404)]
        transport = Transport(routes)
        build_opener = urllib.request.build_opener

        def offline_opener(*handlers):
            return build_opener(*handlers, transport, urllib.request.ProxyHandler({}))

        citations = [{"ref_id": "doi", "doi": DOI},
                     {"ref_id": "search", "title": "Synthetic study"},
                     {"ref_id": "direct", "url": DIRECT},
                     {"ref_id": "fallback", "url": FALLBACK},
                     {"ref_id": "wayback", "url": ARCHIVE_SOURCE},
                     {"ref_id": "incomplete", "url": "not-a-url"}]
        out_path = Path(self.temp.name) / "result.json"
        with (patch.dict(os.environ, {"APODICTIC_CACHE_DIR": self.temp.name}),
              patch.object(urllib.request, "build_opener", offline_opener),
              patch.object(urllib.request, "urlopen", side_effect=AssertionError("live API")),
              patch.object(socket.socket, "connect", side_effect=AssertionError("live socket")),
              patch.object(api, "resolve_crossref_doi", return_value=CROSSREF),
              patch.object(api, "search_crossref", return_value=SEARCH),
              patch.object(api, "check_unpaywall", return_value=UNPAYWALL),
              patch.object(api, "check_wayback", return_value=WAYBACK),
              patch.object(api.time, "sleep")):
            output = api.resolve_batch(citations, str(out_path), strict=True)
        self.assertEqual(output, json.loads(out_path.read_text()))
        self.assertEqual(transport.routes, [])
        self.assertTrue(all(body.reads == 0 for body in transport.bodies))
        self.assertTrue({"summary", "results", "provenance", "cache_stats", "reliability"}
                        <= output.keys())
        summary = output["summary"]
        self.assertEqual(summary["total"], len(citations))
        self.assertEqual(summary["resolved"], 5)
        self.assertEqual(summary["full_text"], 0)
        self.assertEqual(summary["metadata_only"], 5)
        self.assertEqual(summary["not_checked"], 1)
        self.assertEqual(summary["not_found"], 0)
        self.assertEqual(summary["unretrievable"], 1)
        self.assertEqual(summary["resolved"], summary["full_text"] +
                         summary["abstract_only"] + summary["metadata_only"])
        self.assertEqual(summary["unretrievable"], summary["not_found"] +
                         summary["not_checked"])
        self.assertEqual(summary["total"], summary["resolved"] + summary["unretrievable"])
        self.assertEqual(output["results"][-1]["resolution_status"], "not-checked")
        self.assertIn("url-check", output["results"][-1]["not_checked_providers"])
        self.assertIs(output["reliability"]["strict"]["halt"], False)
        for result in output["results"][:5]:
            self.assert_locator(result, result["source_tier"])
            self.assertTrue({"ref_id", "oa_url", "metadata", "provenance_refs",
                             "resolved", "resolution_status", "source_tier", "confidence"}
                            <= result.keys())


if __name__ == "__main__":
    unittest.main()
