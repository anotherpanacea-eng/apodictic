"""Offline Crossref update-direction regressions for standalone and DOI resolution."""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "plugins/apodictic/skills/research-verification/scripts"))
import academic_apis as api
from provenance import ProvenanceStore
from response_cache import ResponseCache

FIXTURES = ROOT / "tests/fixtures/research"
ARTICLE = json.loads((FIXTURES / "crossref-retraction-live.json").read_text())
NOTICE = json.loads((FIXTURES / "crossref-retraction-notice-live.json").read_text())
ARTICLE_DOI = ARTICLE["message"]["DOI"]
NOTICE_DOI = NOTICE["message"]["DOI"]


class RetractionDirectionTests(unittest.TestCase):
    def standalone(self, doi, response):
        with patch.object(api, "resolve_crossref_doi", return_value=response):
            return api.check_retraction(doi)

    def pipeline(self, doi, response, cache=None):
        with tempfile.TemporaryDirectory() as tmp:
            cache = cache or ResponseCache(tmp)
            provenance = ProvenanceStore()
            with (patch.object(api, "resolve_crossref_doi", return_value=response) as crossref,
                  patch.object(api, "check_unpaywall", return_value={}),
                  patch.object(api.time, "sleep")):
                result = api.resolve_citation({"ref_id": "synthetic", "doi": doi}, cache, provenance)
            return result, provenance, crossref.call_count

    def test_live_article_and_notice_direction(self):
        article = self.standalone(ARTICLE_DOI, ARTICLE)
        self.assertIs(article["retracted"], True)
        self.assertIs(article["corrected"], True)
        self.assertEqual(article["updates"], [])
        self.assertEqual({u["DOI"] for u in article["updated_by"]},
                         {"10.1016/s0140-6736(04)15715-2", NOTICE_DOI})
        notice = self.standalone(NOTICE_DOI, NOTICE)
        self.assertIs(notice["retracted"], False)
        self.assertIs(notice["corrected"], False)
        self.assertEqual(notice["updates"], notice["update_to"])
        self.assertEqual(notice["update_to"][0]["DOI"], ARTICLE_DOI)

        for doi, response, retracted, corrected in (
                (ARTICLE_DOI, ARTICLE, True, True),
                (NOTICE_DOI, NOTICE, False, False)):
            with self.subTest(doi=doi):
                result, provenance, calls = self.pipeline(doi, response)
                self.assertEqual(calls, 1)
                self.assertEqual(result["resolution_status"], "resolved")
                self.assertIs(result.get("retracted", False), retracted)
                self.assertIs(result.get("corrected", False), corrected)
                self.assertEqual(result["updated_by"], response["message"].get("updated-by") or [])
                self.assertEqual(result["update_to"], response["message"].get("update-to") or [])
                self.assertEqual(len(provenance.verify("synthetic")), 1)
                self.assertEqual("retraction_note" in result, retracted)

    def test_correction_erratum_and_mixed_bad_relations(self):
        doi = "10.1234/synthetic"
        base = {"message": {"DOI": doi, "title": ["Synthetic work"]}}
        for kind in ("correction", "erratum"):
            with self.subTest(kind=kind):
                base["message"]["updated-by"] = [{"DOI": "10.1234/notice", "type": kind}]
                self.assertEqual((self.standalone(doi, base)["retracted"],
                                  self.standalone(doi, base)["corrected"]), (False, True))
        base["message"]["updated-by"] = [
            {"DOI": "10.1234/notice", "type": "retraction"}, {"type": "correction"}]
        health = self.standalone(doi, base)
        self.assertIs(health["retracted"], True)
        self.assertIsNone(health["corrected"])
        result, _, _ = self.pipeline(doi, base)
        self.assertIs(result["retracted"], True)
        self.assertIsNone(result["corrected"])
        self.assertEqual(len(result["updated_by"]), 2)

        base["message"].pop("updated-by")
        self.assertEqual((self.standalone(doi, base)["retracted"],
                          self.standalone(doi, base)["corrected"]), (False, False))
        base["message"]["updated-by"] = [{"DOI": "10.1234/notice", "type": "unknown"}]
        self.assertIsNone(self.standalone(doi, base)["retracted"])

    def test_invalid_metadata_remains_unknown_and_does_not_crash(self):
        doi = "10.1234/synthetic"
        for response in ({}, {"_error": "503"}, {"_skipped": True},
                         {"message": None}, {"message": []}, {"message": "bad"},
                         {"message": {}}, {"message": {"DOI": "10.1234/other"}}):
            with self.subTest(response=response):
                status = self.standalone(doi, response)
                self.assertIsNone(status["retracted"])
                self.assertIsNone(status["corrected"])
                self.assertIn("error", status)
                result, provenance, calls = self.pipeline(doi, response)
                self.assertEqual(calls, 1)
                self.assertIs(result["resolved"], False)
                self.assertEqual(result["resolution_status"], "not-checked")
                self.assertNotIn("retracted", result)
                self.assertEqual(provenance.verify("synthetic"), [])

    def test_blank_requested_and_response_doi_are_not_identity(self):
        response = {"message": {"DOI": " \t ", "title": ["Synthetic work"]}}
        for doi in (" ", "10.1234/synthetic"):
            with self.subTest(doi=doi):
                status = self.standalone(doi, response)
                self.assertIsNone(status["retracted"])
                self.assertIsNone(status["corrected"])
                self.assertIn("error", status)
                result, provenance, calls = self.pipeline(doi, response)
                self.assertEqual(calls, 1)
                self.assertIs(result["resolved"], False)
                self.assertEqual(result["resolution_status"], "not-checked")
                self.assertEqual(provenance.verify("synthetic"), [])

    def test_malformed_relation_and_cache_hit_do_not_fetch_again(self):
        doi = "10.1234/synthetic"
        response = {"message": {"DOI": doi, "title": ["Synthetic work"],
                                "updated-by": [{"DOI": "10.1234/n", "type": "correction"}, 7]}}
        health = self.standalone(doi, response)
        self.assertIsNone(health["retracted"])
        self.assertIs(health["corrected"], True)
        with tempfile.TemporaryDirectory() as tmp:
            cache = ResponseCache(tmp)
            cache.set(f"crossref:doi:{doi}", response)
            result, provenance, calls = self.pipeline(doi, None, cache)
        self.assertEqual(calls, 0)
        self.assertIsNone(result["retracted"])
        self.assertIs(result["corrected"], True)
        self.assertEqual(len(provenance.verify("synthetic")), 1)


if __name__ == "__main__":
    unittest.main()
