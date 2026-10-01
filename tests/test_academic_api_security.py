"""Offline credential-boundary regressions using urllib's real redirect stack."""

import io
import sys
import unittest
import urllib.request
import urllib.response
from email.message import Message
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugins/apodictic"
                       / "skills/research-verification/scripts"))
import academic_apis as api


class OfflineTransport(urllib.request.HTTPHandler, urllib.request.HTTPSHandler):
    """Replace only transport; urllib still builds and follows real redirects."""

    def __init__(self, redirect=None):
        super().__init__()
        self.redirect = redirect
        self.requests = []

    def http_open(self, req):
        self.requests.append(req)
        headers = Message()
        status = 200
        if self.redirect and len(self.requests) == 1:
            status = 302
            headers["Location"] = self.redirect
        response = urllib.response.addinfourl(io.BytesIO(b'{}'), headers,
                                             req.full_url, status)
        response.msg = "Found" if status == 302 else "OK"
        return response

    https_open = http_open


class CredentialBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.key_patch = patch.object(api, "S2_API_KEY", "synthetic-key-only")
        self.key_patch.start()
        self.addCleanup(self.key_patch.stop)

    def fetch(self, url, redirect=None):
        transport = OfflineTransport(redirect)
        opener = urllib.request.build_opener(transport, urllib.request.ProxyHandler({}))
        with patch.object(urllib.request, "urlopen", opener.open):
            self.assertEqual(api._fetch_json(url), {})
        return transport.requests

    def test_key_only_on_exact_https_api_origin(self):
        for url in ("https://api.semanticscholar.org/graph/v1/paper/search",
                    "https://api.semanticscholar.org:443/graph/v1/paper/search"):
            with self.subTest(url=url):
                self.assertEqual(self.fetch(url)[0].get_header("X-api-key"),
                                 "synthetic-key-only")
        for url in ("https://example.org/semanticscholar",
                    "https://api.semanticscholar.org.example.org/",
                    "https://semanticscholar.org/",
                    "http://api.semanticscholar.org/",
                    "https://api.semanticscholar.org:8443/",
                    "https://user@api.semanticscholar.org/",
                    "https://api.semanticscholar.org@example.org/"):
            with self.subTest(url=url):
                self.assertIsNone(self.fetch(url)[0].get_header("X-api-key"))

    def test_public_search_and_wayback_do_not_receive_key(self):
        transport = OfflineTransport()
        opener = urllib.request.build_opener(transport, urllib.request.ProxyHandler({}))
        with patch.object(urllib.request, "urlopen", opener.open):
            api.search_crossref("semanticscholar")
            api.check_wayback("https://semanticscholar.org/paper/example")
        self.assertEqual(len(transport.requests), 2)
        self.assertTrue(all(req.get_header("X-api-key") is None
                            for req in transport.requests))

    def test_redirects_never_forward_key(self):
        for target in ("https://example.org/redirected",
                       "http://api.semanticscholar.org/redirected",
                       "https://api.semanticscholar.org/redirected"):
            with self.subTest(target=target):
                requests = self.fetch("https://api.semanticscholar.org/start", target)
                self.assertEqual(len(requests), 2)
                self.assertEqual(requests[0].get_header("X-api-key"), "synthetic-key-only")
                self.assertIsNone(requests[1].get_header("X-api-key"))


if __name__ == "__main__":
    unittest.main()
