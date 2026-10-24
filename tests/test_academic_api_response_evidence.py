"""Offline checks for opt-in response evidence: every tier the resolver reads is kept."""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugins/apodictic"
                       / "skills/research-verification/scripts"))
import academic_apis as api
from provenance import ProvenanceStore
from response_cache import ResponseCache

TITLE = "Synthetic Source"
EMPTY = {
    "crossref.org/works?": {"message": {"items": []}},
    "semanticscholar.org/graph/v1/paper/search?": {"data": []},
    "openalex.org/works?": {"results": []},
    "core.ac.uk/v3/search/works?": {"results": []},
    "unpaywall.org": {},
}


def _network(routes):
    def network(url, headers=None, timeout=15):
        for needle, response in routes.items():
            if needle in url:
                return response
        raise AssertionError(f"unexpected provider URL: {url}")
    return network


class ResponseEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.cache = ResponseCache(self.tmp.name)

    def resolve(self, citation, store, overrides=None):
        routes = {**EMPTY, **(overrides or {})}
        with patch.object(api, "_fetch_json_network", side_effect=_network(routes)), \
                patch.object(api.time, "sleep"):
            return api.resolve_citation(citation, self.cache, store)

    def test_unresolved_search_keeps_every_tier_response(self):
        store = ProvenanceStore(record_responses=True)
        result = self.resolve({"ref_id": "r1", "title": TITLE}, store)
        self.assertEqual(result["resolution_status"], "not-found")
        seen = [(r["source"], r["outcome"]) for r in store.responses]
        self.assertEqual(seen, [("crossref-search", "no-match"),
                                ("semantic-scholar", "no-match"),
                                ("openalex", "no-match"),
                                ("core", "no-match")])
        self.assertEqual(store.responses[1]["response"], {"data": []})
        self.assertEqual(store.entries, [])  # legacy provenance is unchanged

    def test_malformed_tier_is_recorded_as_not_checked_with_its_body(self):
        store = ProvenanceStore(record_responses=True)
        bad = {"data": None}
        result = self.resolve({"ref_id": "r2", "title": TITLE}, store,
                              {"semanticscholar.org/graph/v1/paper/search?": bad})
        self.assertEqual(result["resolution_status"], "not-checked")
        s2 = [r for r in store.responses if r["source"] == "semantic-scholar"]
        self.assertEqual(s2[0]["outcome"], "not-checked")
        self.assertEqual(s2[0]["response"], bad)

    def test_used_response_is_a_detached_copy_linked_to_its_provenance_entry(self):
        store = ProvenanceStore(record_responses=True)
        prov_ref = store.store("r3", "crossref", {"message": {"DOI": "10.1/x", "title": ["T"]}})
        self.assertEqual(store.responses[0]["outcome"], "used")
        self.assertEqual(store.responses[0]["prov_ref"], prov_ref)
        original = {"message": {"items": []}}
        store.record("r3", "crossref-search", original, "no-match")
        original["message"]["items"].append("later mutation")
        self.assertEqual(store.responses[1]["response"], {"message": {"items": []}})

    def test_recording_is_off_by_default(self):
        store = ProvenanceStore()
        self.resolve({"ref_id": "r4", "title": TITLE}, store)
        self.assertEqual(store.responses, [])
        with self.assertRaises(RuntimeError):
            store.save_responses(str(Path(self.tmp.name) / "nope.json"))

    def test_batch_cli_writes_the_evidence_file_only_when_asked(self):
        citations = Path(self.tmp.name) / "citations.json"
        citations.write_text(json.dumps([{"ref_id": "b1", "title": TITLE}]))
        evidence = Path(self.tmp.name) / "evidence.json"
        output = Path(self.tmp.name) / "out.json"
        argv = ["academic_apis.py", "batch", "--input", str(citations),
                "--output", str(output), "--response-evidence", str(evidence)]
        with patch.object(api, "_default_cache_dir", return_value=self.tmp.name), \
                patch.object(api, "_fetch_json_network", side_effect=_network(EMPTY)), \
                patch.object(api.time, "sleep"), patch.object(sys, "argv", argv), \
                patch.dict("os.environ", {"APODICTIC_RELIABILITY": "off"}):
            api.main()
        doc = json.loads(evidence.read_text())
        self.assertEqual([r["source"] for r in doc["responses"]],
                         ["crossref-search", "semantic-scholar", "openalex", "core"])
        self.assertNotIn("responses", json.loads(output.read_text()))


if __name__ == "__main__":
    unittest.main()
