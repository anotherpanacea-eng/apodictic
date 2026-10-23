"""Offline URL completeness checks with urllib's real error/redirect stack."""

import io
import http.client
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
from api_reliability import ReliabilityLedger


class Transport(urllib.request.HTTPHandler, urllib.request.HTTPSHandler):
    """Replace only transport; leave urllib's redirects/error processing real."""

    def __init__(self, routes):
        super().__init__()
        self.routes = list(routes)
        self.requests = []

    def http_open(self, req):
        self.requests.append(req)
        if not self.routes:
            raise AssertionError("unexpected network request")
        method, url, status, location = self.routes.pop(0)
        if req.full_url != url or method not in (None, req.get_method()):
            raise AssertionError((req.get_method(), req.full_url, method, url))
        if isinstance(status, BaseException):
            raise status
        headers = Message()
        if location:
            headers["Location"] = location
        response = urllib.response.addinfourl(io.BytesIO(b"synthetic"), headers,
                                              req.full_url, status)
        response.msg = "synthetic"
        return response

    https_open = http_open


class UrlStatusTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.cache = ResponseCache(self.temp.name)
        self.prov = ProvenanceStore()
        self.delay = patch.object(api, "RATE_LIMIT_DELAY", 0)
        self.delay.start()
        self.addCleanup(self.delay.stop)

    def probe(self, url, routes):
        transport = Transport(routes)
        original = urllib.request.build_opener

        def offline_opener(*handlers):
            return original(*handlers, transport, urllib.request.ProxyHandler({}))

        with patch.object(urllib.request, "build_opener", offline_opener):
            with patch.object(urllib.request, "urlopen", side_effect=AssertionError("live network")):
                with patch.object(socket.socket, "connect", side_effect=AssertionError("live socket")):
                    result = api._check_url(url)
        self.assertEqual(transport.routes, [])
        return result, transport

    def resolve(self, url, direct, wayback, ledger=None):
        with patch.object(api, "_check_url", return_value=direct):
            with patch.object(api, "_fetch_json_network", return_value=wayback) as network:
                result = api.resolve_citation({"ref_id": "u1", "url": url},
                                              self.cache, self.prov, ledger=ledger)
        return result, network

    def test_head_success_and_fallback_get(self):
        url = "https://example.org/item"
        result, t = self.probe(url, [("HEAD", url, 200, None)])
        self.assertEqual(result["check_status"], "live")
        self.assertEqual([r.get_method() for r in t.requests], ["HEAD"])
        for head_status in (405, 501):
            result, t = self.probe(url, [("HEAD", url, head_status, None),
                                         ("GET", url, 200, None)])
            self.assertEqual(result["check_status"], "live")
            self.assertEqual([r.get_method() for r in t.requests], ["HEAD", "GET"])
        for status in (403, 405):
            result, _ = self.probe(url, [("HEAD", url, status, None),
                                         ("GET", url, status, None)])
            self.assertEqual(result["check_status"], "not-checked")
            self.assertEqual(result["status"], status)
        result, _ = self.probe(url, [("HEAD", url, 403, None),
                                     ("GET", url, 410, None)])
        self.assertEqual(result["check_status"], "not-found")

    def test_unimplemented_head_uses_get_terminal_outcome(self):
        url = "https://example.org/item"
        for terminal, expected in ((404, "not-found"),
                                   (TimeoutError("synthetic timeout"), "not-checked")):
            with self.subTest(terminal=terminal):
                result, t = self.probe(url, [("HEAD", url, 501, None),
                                             ("GET", url, terminal, None)])
                self.assertEqual(result["check_status"], expected)
                self.assertEqual([r.get_method() for r in t.requests], ["HEAD", "GET"])

    def test_redirect_outcome_is_the_target_outcome(self):
        start = "https://one.example/item"
        target = "https://two.example/item"
        for status, expected in ((200, "live"), (404, "not-found")):
            with self.subTest(status=status):
                # None: urllib picks the follow-up method for a redirected HEAD.
                result, _ = self.probe(start, [("HEAD", start, 302, target),
                                               (None, target, status, None)])
                self.assertEqual(result["check_status"], expected)
                self.assertEqual(result["final_url"], target)
        result, _ = self.probe(start, [("HEAD", start, 302, "file:///etc/passwd")])
        self.assertEqual(result["check_status"], "not-checked")

    def test_rate_server_and_transport_failures_are_incomplete(self):
        url = "https://example.org/item"
        for status in (429, 500, 503):
            with self.subTest(status=status):
                result, t = self.probe(url, [("HEAD", url, status, None)])
                self.assertEqual(result["check_status"], "not-checked")
                self.assertEqual(len(t.requests), 1)
        result, _ = self.probe(url, [("HEAD", url, TimeoutError("synthetic"), None)])
        self.assertEqual(result["check_status"], "not-checked")
        self.assertEqual(result["_error"], "transport-error")
        result, _ = self.probe(url, [("HEAD", url, 403, None),
                                     ("GET", url, TimeoutError("synthetic"), None)])
        self.assertEqual(result["check_status"], "not-checked")

    def test_malformed_http_status_and_header_are_incomplete(self):
        class FakeSocket:
            def __init__(self, raw):
                self.raw = raw

            def makefile(self, *args, **kwargs):
                return io.BytesIO(self.raw)

            def sendall(self, data):
                pass

            def close(self):
                pass

        original = urllib.request.build_opener
        for raw in (b"BROKEN status\r\n\r\n",
                    b"HTTP/9.0 200 OK\r\n\r\n",
                    b"HTTP/1.1 200 OK\r\nX: " + b"x" * 70000 + b"\r\n\r\n"):
            with self.subTest(raw=raw[:20]):
                with patch.object(http.client.HTTPConnection, "connect",
                                  lambda conn: setattr(conn, "sock", FakeSocket(raw))):
                    with patch.object(urllib.request, "build_opener",
                                      lambda *handlers: original(*handlers,
                                          urllib.request.ProxyHandler({}))):
                        with patch.object(socket.socket, "connect",
                                          side_effect=AssertionError("live socket")):
                            result = api._check_url("http://example.org/item")
                self.assertEqual(result["check_status"], "not-checked")
                self.assertEqual(result["_error"], "transport-error")

    def test_invalid_input_never_probed_or_archived(self):
        for url in ("file:///etc/passwd", "https://user:pass@example.org/",
                    "https://example.org/\x00item", "https://example.org:bad/item"):
            with self.subTest(url=url):
                direct = api._check_url(url)
                self.assertEqual(direct["check_status"], "not-checked")
                self.assertFalse(direct["wayback_allowed"])
                result, network = self.resolve(url, direct, {"archived_snapshots": {}})
                network.assert_not_called()
                self.assertEqual(result["resolution_status"], "not-checked")
                self.assertIn("url-check", result["not_checked_providers"])

    def test_url_timeout_vs_observed_absence_and_snapshot(self):
        url = "https://example.org/item"
        incomplete = {"url": url, "status": None, "live": False,
                      "check_status": "not-checked", "wayback_allowed": True,
                      "_error": "transport-error"}
        missing = {"url": url, "status": 404, "live": False,
                   "check_status": "not-found", "wayback_allowed": True}
        result, _ = self.resolve(url, incomplete, {"archived_snapshots": {}})
        self.assertEqual(result["resolution_status"], "not-checked")
        self.assertEqual(result["not_checked_providers"], ["url-check"])
        self.assertEqual(len(result["provenance_refs"]), 2)
        self.assertEqual(len(self.prov.entries), 2)
        self.assertEqual(result["url_check"]["_error"], "transport-error")
        result, _ = self.resolve(url, missing, {"archived_snapshots": {}})
        self.assertEqual(result["resolution_status"], "not-found")
        self.assertEqual(result["not_checked_providers"], [])
        # A successful archive wins despite an incomplete direct check.
        snap = {"archived_snapshots": {"closest": {"available": True,
                 "url": "https://web.archive.org/web/20200101/https://example.org/item"}}}
        result, _ = self.resolve(url + "/new", incomplete, snap)
        self.assertEqual(result["resolution_status"], "resolved")
        self.assertEqual(result["source_tier"], "wayback")
        self.assertEqual(len(result["provenance_refs"]), 2)

    def test_wayback_contract_and_single_ledger_outcome(self):
        url = "https://example.org/item"
        valid = ({"archived_snapshots": {}},
                 {"archived_snapshots": {"closest": {"available": False}}},
                 {"archived_snapshots": {"closest": {"available": True,
                     "url": "https://web.archive.org/web/20200101/https://example.org/item"}}})
        invalid = (None, {}, [], {"archived_snapshots": None},
                   {"archived_snapshots": {"closest": {}}},
                   {"archived_snapshots": {"closest": {"available": 1}}},
                   {"archived_snapshots": {"closest": {"available": True}}},
                   {"archived_snapshots": {"closest": {"available": True, "url": "file:///x"}}},
                   {"archived_snapshots": {"closest": {"available": False, "url": None}}},
                   {"_error": "synthetic", "archived_snapshots": {}},
                   {"_error": "synthetic", "archived_snapshots": {"closest": {"available": True,
                    "url": "https://web.archive.org/web/20200101/https://example.org/item"}}},
                   {"_skipped": True, "archived_snapshots": {"closest": {"available": True,
                    "url": "https://web.archive.org/web/20200101/https://example.org/item"}}})
        for payload in valid + invalid:
            with self.subTest(payload=payload):
                led = ReliabilityLedger()
                with patch.object(api, "_fetch_json_network", return_value=payload):
                    answer = api.check_wayback(url, ledger=led)
                counts = led.snapshot()["providers"]["wayback"]
                self.assertEqual(counts["calls"], 1)
                if payload in valid:
                    self.assertNotIn("_error", answer)
                    self.assertEqual(counts["ok"], 1)
                else:
                    self.assertIn("_error", answer)
                    self.assertEqual(counts["errors"], 1)

    def test_malformed_cached_wayback_is_retried_not_accepted(self):
        url = "https://example.org/cache"
        key = f"wayback:{url}"
        self.cache.set(key, {})  # legacy malformed negative
        missing = {"url": url, "status": 404, "live": False,
                   "check_status": "not-found", "wayback_allowed": True}
        valid = {"archived_snapshots": {"closest": {"available": False}}}
        result, network = self.resolve(url, missing, valid)
        network.assert_called_once()
        self.assertEqual(result["resolution_status"], "not-found")
        self.assertEqual(self.cache.get(key), valid)

    def test_cached_error_markers_cannot_become_negative_or_snapshot(self):
        missing = {"status": 404, "live": False, "check_status": "not-found",
                   "wayback_allowed": True}
        snapshot = {"archived_snapshots": {"closest": {"available": True,
            "url": "https://web.archive.org/web/20200101/https://example.org/item"}}}
        for marker in ("_error", "_skipped"):
            for payload in ({"archived_snapshots": {}}, snapshot):
                url = f"https://example.org/{marker}/{bool(payload['archived_snapshots'])}"
                with self.subTest(url=url):
                    self.cache.set(f"wayback:{url}",
                                   {marker: True if marker == "_skipped" else "synthetic",
                                    **payload})
                    direct = {"url": url, **missing}
                    result, network = self.resolve(url, direct, {"_error": "synthetic-retry"})
                    network.assert_called_once()
                    self.assertEqual(result["resolution_status"], "not-checked")
                    self.assertIn("wayback", result["not_checked_providers"])

    def test_valid_cached_wayback_skips_provider_charge(self):
        for suffix, response, expected in (
            ("negative", {"archived_snapshots": {}}, "not-found"),
            ("snapshot", {"archived_snapshots": {"closest": {"available": True,
                "url": "https://web.archive.org/web/20200101/https://example.org/item"}}},
             "resolved"),
        ):
            with self.subTest(suffix=suffix):
                url = f"https://example.org/{suffix}"
                self.cache.set(f"wayback:{url}", response)
                missing = {"url": url, "status": 404, "live": False,
                           "check_status": "not-found", "wayback_allowed": True}
                result, network = self.resolve(url, missing, {"_error": "must-not-call"},
                                               ledger=ReliabilityLedger())
                network.assert_not_called()
                self.assertEqual(result["resolution_status"], expected)

    def test_earlier_failed_index_is_not_erased_by_negative_url(self):
        url = "https://example.org/unknown"
        missing = {"url": url, "status": 404, "live": False,
                   "check_status": "not-found", "wayback_allowed": True}
        def network(endpoint, *args, **kwargs):
            if "archive.org" in endpoint:
                return {"archived_snapshots": {}}
            return {"_error": "synthetic-provider-unavailable"}
        with patch.object(api, "_check_url", return_value=missing):
            with patch.object(api, "_fetch_json_network", side_effect=network):
                result = api.resolve_citation({"ref_id": "both", "title": "Unknown Paper",
                                               "url": url}, self.cache, self.prov)
        self.assertEqual(result["resolution_status"], "not-checked")
        self.assertIn("crossref", result["not_checked_providers"])
        self.assertNotIn("url-check", result["not_checked_providers"])
        self.assertNotIn("wayback", result["not_checked_providers"])

    def test_reliability_off_preserves_url_incomplete_status(self):
        url = "https://example.org/unavailable"
        incomplete = {"url": url, "status": None, "live": False,
                      "check_status": "not-checked", "wayback_allowed": True,
                      "_error": "transport-error"}
        with patch.dict(os.environ, {"APODICTIC_RELIABILITY": "off"}):
            with patch.object(api, "_default_cache_dir", return_value=self.temp.name):
                with patch.object(api, "_check_url", return_value=incomplete):
                    with patch.object(api, "_fetch_json_network",
                                      return_value={"archived_snapshots": {}}):
                        out = api.resolve_batch([{"ref_id": "u", "url": url}],
                            str(Path(self.temp.name) / "off.json"), strict=True)
        self.assertNotIn("reliability", out)
        self.assertEqual(out["summary"]["not_checked"], 1)
        self.assertEqual(out["results"][0]["not_checked_providers"], ["url-check"])

    def test_strict_uses_causal_degraded_subset(self):
        # First isolate direct URL failure with clean index coverage.
        url = "https://example.org/item"
        incomplete = {"url": url, "status": None, "live": False,
                      "check_status": "not-checked", "wayback_allowed": True,
                      "_error": "transport-error"}
        def batch(citations, response, direct=incomplete):
            with patch.object(api, "_default_cache_dir", return_value=self.temp.name):
                with patch.object(api, "_check_url", return_value=direct):
                    with patch.object(api, "_fetch_json_network", side_effect=response):
                        return api.resolve_batch(citations,
                                                 str(Path(self.temp.name) / "out.json"),
                                                 strict=True,
                                                 sidecar_dir=str(Path(self.temp.name) / "side"))

        out = batch([{"ref_id": "u", "url": url}],
                    lambda endpoint, *args, **kwargs: {"archived_snapshots": {}})
        self.assertEqual(out["summary"]["not_checked"], 1)
        self.assertFalse(out["reliability"]["strict"]["halt"])
        self.assertEqual(out["reliability"]["strict"]["not_checked"], 0)
        side = json.loads((Path(self.temp.name) / "side"
                                         / "Citation_Reliability.json").read_text())
        self.assertEqual(side["resolution_summary"]["not_checked"], 1)

        # Crossref is degraded, but its title-only citation resolves by S2.
        # The separate URL-only incomplete cannot supply the causal strict input.
        def matched_or_empty(endpoint, *args, **kwargs):
            if "semanticscholar" in endpoint:
                return {"data": [{"title": "Synthetic Paper", "authors": [], "year": 2020}]}
            return {"archived_snapshots": {}}

        with patch.dict(os.environ, {"APODICTIC_BUDGET_CROSSREF": "0"}):
            out = batch([{"ref_id": "title", "title": "Synthetic Paper"},
                         {"ref_id": "url", "url": url + "/mixed"}], matched_or_empty)
        self.assertEqual(out["results"][0]["resolution_status"], "resolved")
        self.assertEqual(out["results"][1]["resolution_status"], "not-checked")
        self.assertIn("crossref", out["reliability"]["coverage"]["degraded_providers"])
        self.assertEqual(out["summary"]["not_checked"], 1)
        self.assertFalse(out["reliability"]["strict"]["halt"])
        self.assertEqual(out["reliability"]["strict"]["not_checked"], 0)

        # A URL citation actually blocked by degraded Wayback must halt.
        causal_url = url + "/causal"
        missing = {"url": causal_url, "status": 404, "live": False,
                   "check_status": "not-found", "wayback_allowed": True}
        with patch.dict(os.environ, {"APODICTIC_BUDGET_WAYBACK": "0"}):
            out = batch([{"ref_id": "causal", "url": causal_url}],
                        lambda endpoint, *args, **kwargs: self.fail("skipped provider called"),
                        direct=missing)
        self.assertEqual(out["results"][0]["not_checked_providers"], ["wayback"])
        self.assertEqual(out["summary"]["not_checked"], 1)
        self.assertTrue(out["reliability"]["strict"]["halt"])
        self.assertEqual(out["reliability"]["strict"]["not_checked"], 1)


if __name__ == "__main__":
    unittest.main()
