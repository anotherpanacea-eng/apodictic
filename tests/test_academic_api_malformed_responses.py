"""Offline resolver regressions for incomplete parsed provider answers."""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugins/apodictic"
                       / "skills/research-verification/scripts"))
import academic_apis as api
from api_reliability import ProviderBudget, ReliabilityLedger
from provenance import ProvenanceStore
from response_cache import ResponseCache

TITLE = "Synthetic Source"
DOI = "10.1234/synthetic"
EMPTY = {
    "crossref.org/works?": {"message": {"items": []}},
    "semanticscholar.org/graph/v1/paper/search?": {"data": []},
    "openalex.org/works?": {"results": []},
    "core.ac.uk/v3/search/works?": {"results": []},
    "unpaywall.org": {},
}


class MalformedResponseTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.cache = ResponseCache(self.tmp.name)
        self.provenance = ProvenanceStore()

    def resolve(self, citation, overrides=None, ledger=None):
        routes = {**EMPTY, **(overrides or {})}
        calls = []

        def network(url, headers=None, timeout=15):
            calls.append(url)
            for needle, response in routes.items():
                if needle in url:
                    return response
            raise AssertionError(f"unexpected provider URL: {url}")

        with patch.object(api, "_fetch_json_network", side_effect=network), patch.object(api.time, "sleep"):
            result = api.resolve_citation(citation, self.cache, self.provenance, ledger=ledger)
        return result, calls

    def test_wrong_envelopes_are_incomplete_and_valid_empty_is_negative(self):
        bad = {
            "crossref.org/works?": (None, [], {}, {"message": None},
                                    {"message": {"items": None}},
                                    {"message": {"items": [None]}}),
            "semanticscholar.org/graph/v1/paper/search?": (None, {"data": None}, {"data": [42]}),
            "openalex.org/works?": ([], {"results": None}, {"results": [None]}),
            "core.ac.uk/v3/search/works?": ({}, {"results": None}, {"results": [{"title": ""}]}),
        }
        labels = {"crossref.org/works?": "crossref",
                  "semanticscholar.org/graph/v1/paper/search?": "semantic-scholar",
                  "openalex.org/works?": "openalex", "core.ac.uk/v3/search/works?": "core"}
        for endpoint, responses in bad.items():
            for response in responses:
                for with_ledger in (False, True):
                    with self.subTest(endpoint=endpoint, response=response, ledger=with_ledger):
                        self.cache = ResponseCache()
                        ledger = ReliabilityLedger() if with_ledger else None
                        result, calls = self.resolve({"ref_id": "s", "title": TITLE},
                                                     {endpoint: response}, ledger)
                        self.assertEqual(result["resolution_status"], "not-checked")
                        self.assertIn(labels[endpoint], result["not_checked_providers"])
                        self.assertEqual(sum(endpoint in url for url in calls), 1)
                        if ledger:
                            self.assertEqual(ledger.snapshot()["providers"][labels[endpoint]]["ok"], 1)
        self.cache = ResponseCache()
        result, _ = self.resolve({"ref_id": "s", "title": TITLE})
        self.assertEqual((result["resolution_status"], result["not_checked_providers"]),
                         ("not-found", []))
        self.cache = ResponseCache()
        result, _ = self.resolve({"ref_id": "s", "title": TITLE},
                                 {"crossref.org/works?": {"message": {"items": [{"title": []}]}}})
        self.assertEqual(result["resolution_status"], "not-found")

    def test_selected_mixed_original_and_optional_nulls(self):
        response = {"data": [None, {"title": TITLE, "authors": None,
                                    "externalIds": None, "year": None,
                                    "venue": None, "abstract": None}]}
        result, _ = self.resolve({"ref_id": "s", "title": TITLE},
                                 {"semanticscholar.org/graph/v1/paper/search?": response})
        self.assertEqual((result["source_tier"], result["confidence"]),
                         ("semantic-scholar", "metadata-only verified"))
        self.assertEqual(result["metadata"]["doi"], "")
        self.assertEqual(result["metadata"]["year"], "")
        self.assertEqual(self.provenance.verify("s")[0]["response_summary"], "S2: 2 results")
        self.assertIsNone(response["data"][0])  # matching did not rewrite the original
        self.assertIsNone(self.cache.get(f"s2:search:{TITLE}:"))  # mixed answer is not cached

        for answer, expected in (
            ({"results": [{"title": TITLE, "doi": None, "primary_location": {"source": None},
                           "authorships": None, "publication_year": None}], "meta": None}, "openalex"),
            ({"results": [{"title": TITLE, "authors": None, "yearPublished": None}]}, "core"),
        ):
            with self.subTest(expected=expected):
                self.cache = ResponseCache()
                self.provenance = ProvenanceStore()
                endpoint = "openalex.org/works?" if expected == "openalex" else "core.ac.uk/v3/search/works?"
                result, _ = self.resolve({"ref_id": "s", "title": TITLE}, {endpoint: answer})
                self.assertEqual(result["source_tier"], expected)
                self.assertEqual(result["metadata"]["year"], "")
                self.assertEqual(len(self.provenance.verify("s")), 1)

    def test_citation_count_preserves_explicit_null_fresh_and_cached(self):
        for endpoint, envelope, field, source in (
            ("semanticscholar.org/graph/v1/paper/search?", "data", "citationCount",
             "semantic-scholar"),
            ("openalex.org/works?", "results", "cited_by_count", "openalex"),
        ):
            for label, included, value, expected in (
                ("missing", False, None, 0),
                ("null", True, None, None),
                ("zero", True, 0, 0),
                ("positive", True, 17, 17),
            ):
                for with_ledger in (False, True):
                    with self.subTest(source=source, count=label, ledger=with_ledger):
                        self.cache = ResponseCache()
                        self.provenance = ProvenanceStore()
                        item = {"title": TITLE}
                        if included:
                            item[field] = value
                        response = {envelope: [item]}
                        ledger = ReliabilityLedger() if with_ledger else None
                        for cached in (False, True):
                            result, calls = self.resolve({"ref_id": "s", "title": TITLE},
                                                         {endpoint: response}, ledger)
                            self.assertEqual(result["source_tier"], source)
                            self.assertEqual(result["metadata"]["citation_count"], expected)
                            self.assertEqual(sum(endpoint in url for url in calls),
                                             0 if cached else 1)
                            self.assertEqual(len(self.provenance.verify("s")),
                                             2 if cached else 1)

    def test_valid_later_tier_and_core_first_usable_hit(self):
        self.cache = ResponseCache()
        s2 = {"data": [{"title": TITLE, "externalIds": {}, "abstract": None}]}
        result, calls = self.resolve({"ref_id": "s", "title": TITLE},
                                     {"crossref.org/works?": {"message": None},
                                      "semanticscholar.org/graph/v1/paper/search?": s2})
        self.assertEqual((result["resolution_status"], result["source_tier"]),
                         ("resolved", "semantic-scholar"))
        self.assertEqual(len(calls), 2)
        self.assertEqual(len(self.provenance.verify("s")), 1)

        self.cache = ResponseCache()
        self.provenance = ProvenanceStore()
        original = {"results": [{"title": ""}, {"title": TITLE, "authors": []}]}
        result, _ = self.resolve({"ref_id": "s", "title": TITLE},
                                 {"core.ac.uk/v3/search/works?": original})
        self.assertEqual(result["source_tier"], "core")
        self.assertEqual(result["metadata"]["title"], TITLE)
        self.assertIsNone(self.cache.get(f"core:search:{TITLE}"))

    def test_wrong_consumed_fields_do_not_match_or_invent_oa(self):
        for item in ({"title": [TITLE], "DOI": 42},
                     {"title": [TITLE], "author": [None]},
                     {"title": [TITLE], "published-print": {"date-parts": [None]}}):
            with self.subTest(item=item):
                self.cache = ResponseCache()
                result, _ = self.resolve({"ref_id": "s", "title": TITLE},
                                         {"crossref.org/works?": {"message": {"items": [item]}}})
                self.assertEqual(result["resolution_status"], "not-checked")
                self.assertIn("crossref", result["not_checked_providers"])
        self.cache = ResponseCache()
        result, _ = self.resolve({"ref_id": "s", "title": TITLE},
                                 {"semanticscholar.org/graph/v1/paper/search?":
                                  {"data": [{"title": TITLE, "abstract": True}]}})
        self.assertNotEqual(result["confidence"], "abstract-only verified")

    def test_doi_optional_metadata_and_unpaywall_enrichment(self):
        doi_response = {"message": {"DOI": DOI, "title": [], "author": [],
                                    "published-print": {"date-parts": []},
                                    "container-title": []}}
        for unpaywall in ({"best_oa_location": {"url_for_pdf": None}},
                          {"best_oa_location": {"url_for_pdf": 17}}):
            with self.subTest(unpaywall=unpaywall):
                self.cache = ResponseCache()
                self.provenance = ProvenanceStore()
                result, calls = self.resolve({"ref_id": "d", "doi": DOI},
                                             {"crossref.org/works/": doi_response,
                                              "unpaywall.org": unpaywall})
                self.assertEqual(result["resolution_status"], "resolved")
                self.assertEqual(result["metadata"]["title"], "")
                self.assertIsNone(result["oa_url"])
                self.assertEqual(len(calls), 2)
                self.assertEqual(len(self.provenance.verify("d")),
                                 2 if unpaywall["best_oa_location"]["url_for_pdf"] is None else 1)
        self.cache = ResponseCache()
        result, calls = self.resolve({"ref_id": "d", "doi": DOI},
                                     {"crossref.org/works/": {"message": {"DOI": DOI, "author": [42]}}})
        self.assertEqual((result["resolution_status"], result["not_checked_providers"]),
                         ("not-checked", ["crossref"]))
        self.assertEqual(len(calls), 1)

        self.cache = ResponseCache()
        self.provenance = ProvenanceStore()
        result, calls = self.resolve({"ref_id": "s", "title": TITLE},
                                     {"crossref.org/works?": {"message": {"items": [
                                         {"title": [TITLE], "DOI": DOI}]}},
                                      "unpaywall.org": {"best_oa_location": {"url_for_pdf": 17}}})
        self.assertEqual((result["resolution_status"], result["source_tier"], result["oa_url"]),
                         ("resolved", "crossref-search", None))
        self.assertEqual(len(calls), 2)
        self.assertEqual(len(self.provenance.verify("s")), 1)

    def test_legacy_cache_incomplete_without_same_tier_refetch(self):
        for payload in ({}, {"_error": "503"}, {"_skipped": True}):
            for with_ledger in (False, True):
                with self.subTest(payload=payload, ledger=with_ledger):
                    self.cache = ResponseCache()
                    self.cache.set(f"crossref:search:{TITLE}:", payload)
                    ledger = ReliabilityLedger() if with_ledger else None
                    result, calls = self.resolve({"ref_id": "s", "title": TITLE}, ledger=ledger)
                    self.assertEqual(result["resolution_status"], "not-checked")
                    self.assertIn("crossref", result["not_checked_providers"])
                    self.assertEqual(sum("crossref.org/works?" in url for url in calls), 0)
                    if ledger:
                        self.assertEqual(ledger.snapshot()["providers"].get("crossref", {}).get("calls", 0), 0)

    def test_fresh_malformed_answer_is_not_cached_as_negative(self):
        self.cache = ResponseCache()
        for _ in range(2):
            result, calls = self.resolve({"ref_id": "s", "title": TITLE},
                                         {"crossref.org/works?": {}})
            self.assertEqual(result["resolution_status"], "not-checked")
            self.assertEqual(sum("crossref.org/works?" in url for url in calls), 1)
            self.assertIsNone(self.cache.get(f"crossref:search:{TITLE}:"))

    def test_real_budget_skip_and_strict_causal_subset(self):
        ledger = ReliabilityLedger(budget=ProviderBudget({"crossref": 0}))
        result, calls = self.resolve({"ref_id": "d", "doi": DOI}, ledger=ledger)
        self.assertEqual((result["resolution_status"], calls), ("not-checked", []))
        self.assertEqual(ledger.snapshot()["providers"].get("crossref", {}).get("calls", 0), 0)

        with tempfile.TemporaryDirectory() as tmp:
            routes = {"/works/10.1234%2Fvalid": {"message": {"DOI": "10.1234/valid"}},
                      "/works/10.1234%2Finvalid": {"message": None}}

            def network(url, headers=None, timeout=15):
                for needle, response in routes.items():
                    if needle in url:
                        return response
                raise AssertionError(url)

            with patch.object(api, "_default_cache_dir", return_value=tmp), \
                 patch.object(api, "_fetch_json_network", side_effect=network), \
                 patch.object(api.time, "sleep"), \
                 patch.dict("os.environ", {"APODICTIC_BUDGET_UNPAYWALL": "0"}):
                output = api.resolve_batch([{"ref_id": "a", "doi": "10.1234/valid"},
                                            {"ref_id": "b", "doi": "10.1234/invalid"}],
                                           str(Path(tmp) / "out.json"), strict=True)
            self.assertEqual(output["summary"]["not_checked"], 1)
            self.assertEqual(output["results"][1]["not_checked_providers"], ["crossref"])
            self.assertFalse(output["reliability"]["strict"]["halt"])


if __name__ == "__main__":
    unittest.main()
