"""Offline public-contract regressions for opt-in parsed response evidence."""

import copy
import io
import json
import math
import os
import sys
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugins/apodictic"
                       / "skills/research-verification/scripts"))
import academic_apis as api
from api_reliability import ProviderBudget, ReliabilityLedger
from provenance import ProvenanceStore, json_value_sha256
from response_cache import ResponseCache

TITLE = "Synthetic Source"
DOI = "10.1234/synthetic"
EMPTY = {
    "crossref.org/works?": {"message": {"items": []}},
    "semanticscholar.org/graph/v1/paper/search?": {"data": []},
    "openalex.org/works?": {"results": []},
    "core.ac.uk/v3/search/works?": {"results": []},
    "unpaywall.org": {},
    "archive.org/wayback/available?": {"archived_snapshots": {}},
}


def fake_network(routes, calls):
    def network(url, headers=None, timeout=15, _observe=None):
        calls.append(url)
        for needle, value in routes.items():
            if needle in url:
                value = copy.deepcopy(value)  # each request parses a distinct object
                if _observe is not None:
                    _observe("parsed", value, "2026-01-01T00:00:00Z", None, None)
                return value
        raise AssertionError(f"unexpected network URL: {url}")
    return network


class ResponseEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def resolve(self, citation, routes=None, *, cache=None, provenance=None, ledger=None):
        cache = cache if cache is not None else ResponseCache()
        provenance = provenance if provenance is not None else ProvenanceStore(record_responses=True)
        calls = []
        with patch.object(api, "_fetch_json_network",
                          side_effect=fake_network({**EMPTY, **(routes or {})}, calls)), \
             patch.object(api.time, "sleep"):
            result = api.resolve_citation(citation, cache, provenance, ledger=ledger)
        return result, provenance.response_evidence()["events"], calls

    def test_disabled_store_and_selected_original_json_detachment(self):
        disabled = ProvenanceStore()
        with self.assertRaises(RuntimeError):
            disabled.response_evidence()
        with self.assertRaises(RuntimeError):
            disabled.save_response_evidence(str(Path(self.tmp.name) / "disabled.json"))
        enabled = ProvenanceStore(record_responses=True)
        self.assertEqual(enabled.response_evidence()["events"], [])

        answer = {"message": {"DOI": DOI, "title": [TITLE],
                              "updated-by": [{"DOI": "10.1234/update", "type": "correction"}],
                              "nested": {"a": [1, None, True]}}}
        result, events, _ = self.resolve({"ref_id": "r", "doi": DOI},
                                         {"crossref.org/works/": answer}, provenance=enabled)
        self.assertEqual(result["source_tier"], "crossref-doi")
        first = events[0]
        self.assertEqual((first["kind"], first["outcome"], first["origin"]),
                         ("json_value", "selected", "fresh"))
        self.assertEqual(first["payload"], answer)
        self.assertEqual(first["prov_ref"], result["provenance_refs"][0])
        self.assertEqual(first["payload_sha256"], json_value_sha256(answer))
        answer["message"]["nested"]["a"].append("changed")
        first["payload"]["message"]["title"][0] = "mutated return"
        saved = Path(self.tmp.name) / "evidence.json"
        enabled.save_response_evidence(str(saved))
        exported = json.loads(saved.read_text())
        self.assertEqual(exported["events"][0]["payload"]["message"]["title"], [TITLE])
        self.assertEqual(exported["events"][0]["payload"]["message"]["nested"]["a"],
                         [1, None, True])
        self.assertEqual(exported["events"][0]["payload_sha256"],
                         json_value_sha256(exported["events"][0]["payload"]))

    def test_empty_nonmatch_and_duplicate_batch_indices(self):
        nonmatch = {"message": {"items": [{"title": ["Unrelated publication"]}]}}
        result, events, calls = self.resolve({"ref_id": "r", "title": TITLE},
                                             {"crossref.org/works?": nonmatch})
        self.assertEqual(result["resolution_status"], "not-found")
        self.assertEqual([e["outcome"] for e in events],
                         ["no_match", "empty", "empty", "empty"])
        self.assertEqual(len(calls), 4)

        output = Path(self.tmp.name) / "batch.json"
        evidence = Path(self.tmp.name) / "evidence.json"
        with patch.object(api, "_default_cache_dir", return_value=str(Path(self.tmp.name) / "cache")), \
             patch.object(api, "_fetch_json_network",
                          side_effect=fake_network(EMPTY, [])), \
             patch.object(api.time, "sleep"):
            batch = api.resolve_batch([{"ref_id": "r", "title": TITLE},
                                       {"ref_id": "r", "title": TITLE}],
                                      str(output), response_evidence_path=str(evidence))
        exported = json.loads(evidence.read_text())
        self.assertEqual(batch["summary"]["not_found"], 2)
        self.assertEqual(len(exported["events"]), 8)
        self.assertEqual([e["citation_index"] for e in exported["events"]], [0] * 4 + [1] * 4)
        self.assertEqual([e["event_id"] for e in exported["events"]],
                         [f"response-{i}" for i in range(1, 9)])
        self.assertTrue(all(e["prov_ref"] is None for e in exported["events"]))
        self.assertNotIn("response_evidence", batch)

    def test_later_selected_tiers_and_unpaywall_enrichment(self):
        for endpoint, envelope, source in (
            ("semanticscholar.org/graph/v1/paper/search?", "data", "semantic-scholar"),
            ("openalex.org/works?", "results", "openalex"),
            ("core.ac.uk/v3/search/works?", "results", "core"),
        ):
            with self.subTest(source=source):
                answer = {envelope: [{"title": TITLE}]}
                result, events, _ = self.resolve({"ref_id": "r", "title": TITLE},
                                                 {endpoint: answer})
                self.assertEqual(result["source_tier"], source)
                selected = events[-1]
                self.assertEqual((selected["kind"], selected["outcome"],
                                  selected["payload"], selected["prov_ref"]),
                                 ("json_value", "selected", answer,
                                  result["provenance_refs"][0]))

        answer = {"message": {"DOI": DOI, "title": [TITLE]}}
        oa = {"best_oa_location": {"url_for_pdf": "https://example.org/paper.pdf"}}
        result, events, _ = self.resolve({"ref_id": "r", "doi": DOI},
                                         {"crossref.org/works/": answer,
                                          "unpaywall.org": oa})
        self.assertEqual(result["oa_url"], "https://example.org/paper.pdf")
        self.assertEqual([(event["source"], event["outcome"]) for event in events],
                         [("crossref-doi", "selected"), ("unpaywall", "selected")])
        self.assertEqual(events[1]["prov_ref"], result["provenance_refs"][1])

    def test_opt_in_preserves_admitted_resolution_and_legacy_provenance(self):
        routes = {**EMPTY, "semanticscholar.org/graph/v1/paper/search?":
                  {"data": [{"title": TITLE, "citationCount": None}]}}
        outputs = []
        for enabled in (False, True):
            cache = ResponseCache()
            store = ProvenanceStore(record_responses=enabled)
            calls = []
            with patch.object(api, "_fetch_json_network", side_effect=fake_network(routes, calls)), \
                 patch.object(api.time, "sleep"):
                result = api.resolve_citation({"ref_id": "r", "title": TITLE}, cache, store)
            entries = [{key: value for key, value in entry.items() if key != "timestamp"}
                       for entry in store.entries]
            outputs.append((result, entries, len(calls)))
        self.assertEqual(outputs[0], outputs[1])

    def test_full_domain_invalid_is_uniform_and_not_a_negative_cache_fact(self):
        invalid = {"message": {"items": []}, "unused": math.nan}
        for enabled in (False, True):
            for cached in (False, True):
                with self.subTest(enabled=enabled, cached=cached):
                    cache = ResponseCache()
                    if cached:
                        cache.set(f"crossref:search:{TITLE}:", invalid)
                    provenance = ProvenanceStore(record_responses=enabled)
                    ledger = ReliabilityLedger()
                    calls = []
                    with patch.object(api, "_fetch_json_network",
                                      side_effect=fake_network({**EMPTY,
                                          "crossref.org/works?": invalid}, calls)), \
                         patch.object(api.time, "sleep"):
                        result = api.resolve_citation({"ref_id": "r", "title": TITLE},
                                                      cache, provenance, ledger=ledger)
                    self.assertEqual(result["resolution_status"], "not-checked")
                    self.assertIn("crossref", result["not_checked_providers"])
                    self.assertEqual(sum("crossref.org/works?" in call for call in calls),
                                     0 if cached else 1)
                    if not cached:
                        self.assertIsNone(cache.get(f"crossref:search:{TITLE}:"))
                        self.assertEqual(ledger.snapshot()["providers"]["crossref"]["ok"], 1)
                    else:
                        self.assertEqual(ledger.snapshot()["providers"].get("crossref", {}).get("calls", 0), 0)
                    if enabled:
                        first = provenance.response_evidence()["events"][0]
                        self.assertEqual(first["kind"],
                                         "cache_invalid" if cached else "request_failure")
                        self.assertNotIn("payload", first)

    def test_cache_origin_binding_and_legacy_marker_gap(self):
        directory = str(Path(self.tmp.name) / "cache")
        cache = ResponseCache(directory)
        provenance = ProvenanceStore(record_responses=True)
        answer = {"message": {"items": []}}
        _, fresh, _ = self.resolve({"ref_id": "r", "title": TITLE},
                                   {"crossref.org/works?": answer},
                                   cache=cache, provenance=provenance)
        second_cache = ResponseCache(directory)
        _, reused, calls = self.resolve({"ref_id": "r2", "title": TITLE},
                                        cache=second_cache)
        self.assertEqual(sum("crossref.org/works?" in call for call in calls), 0)
        self.assertEqual((reused[0]["origin"], reused[0]["observed_at"]),
                         ("cache", fresh[0]["observed_at"]))
        self.assertEqual(reused[0]["payload_sha256"], fresh[0]["payload_sha256"])
        second_cache.get(f"crossref:search:{TITLE}:")["message"]["items"].append(
            {"title": ["Other"]})
        _, mutated, _ = self.resolve({"ref_id": "r3", "title": TITLE},
                                     cache=second_cache)
        self.assertEqual((mutated[0]["origin"], mutated[0]["observed_at"]),
                         ("legacy_cache", None))
        legacy = ResponseCache()
        legacy.set(f"crossref:search:{TITLE}:",
                   {"_error": "diagnostic", "_url": "https://example.org/?email=private"})
        result, events, calls = self.resolve({"ref_id": "r", "title": TITLE}, cache=legacy)
        self.assertEqual(result["resolution_status"], "not-checked")
        self.assertEqual((events[0]["kind"], events[0]["outcome"]),
                         ("cache_unclassified", "unclassified"))
        self.assertNotIn("payload", events[0])
        self.assertNotIn("private", json.dumps(events[0]))
        self.assertEqual(sum("crossref.org/works?" in call for call in calls), 0)

        tagged_dir = str(Path(self.tmp.name) / "tagged-cache")
        tagged = ResponseCache(tagged_dir)
        sentinel = {"_error": "failure", "_url": "https://example.org/?email=private"}
        tagged.set(f"crossref:search:{TITLE}:", sentinel,
                   evidence_meta={"kind": "local_failure", "category": "http-error",
                                  "payload_sha256": json_value_sha256(sentinel)})
        _, tagged_events, calls = self.resolve({"ref_id": "r", "title": TITLE}, cache=tagged)
        self.assertEqual((tagged_events[0]["kind"], tagged_events[0]["origin"],
                          tagged_events[0]["category"]),
                         ("request_failure", "cache", "http-error"))
        self.assertNotIn("private", json.dumps(tagged_events[0]))
        self.assertEqual(sum("crossref.org/works?" in call for call in calls), 0)
        self.assertIsNone(ResponseCache(tagged_dir).get(f"crossref:search:{TITLE}:"))

    def test_wayback_cache_rejection_and_probe_receipts(self):
        dead_probe = {"url": "https://example.org/x", "status": 404, "live": False,
                      "check_status": "not-found", "method": "HEAD",
                      "attempts": [{"method": "HEAD", "status": 404,
                                    "final_url": "https://example.org/x", "redirects": 0}],
                      "final_url": "https://example.org/x", "wayback_allowed": True}
        cache = ResponseCache()
        cache.set("wayback:https://example.org/x", {"archived_snapshots": None})
        calls = []
        with patch.object(api, "_check_url", return_value=dead_probe), \
             patch.object(api, "_fetch_json_network", side_effect=fake_network(EMPTY, calls)), \
             patch.object(api.time, "sleep"):
            provenance = ProvenanceStore(record_responses=True)
            result = api.resolve_citation({"ref_id": "r", "url": "https://example.org/x"},
                                          cache, provenance)
        self.assertEqual(result["resolution_status"], "not-found")
        events = provenance.response_evidence()["events"]
        self.assertEqual([(e["source"], e["outcome"]) for e in events],
                         [("url-check", "probe_dead"), ("wayback", "invalid"),
                          ("wayback", "empty")])
        self.assertEqual(sum("archive.org" in call for call in calls), 1)
        self.assertNotIn("https://example.org/x", json.dumps(events[0]))

        extra = {"archived_snapshots": {}, "unused": math.nan}
        cache = ResponseCache()
        cache.set("wayback:https://example.org/x", extra)
        with patch.object(api, "_check_url", return_value=dead_probe):
            result, events, calls = self.resolve({"ref_id": "r", "url": "https://example.org/x"},
                                                 cache=cache)
        self.assertEqual(result["resolution_status"], "not-checked")
        self.assertEqual(sum("archive.org" in call for call in calls), 0)
        self.assertEqual(events[1]["kind"], "cache_invalid")

        available = {"archived_snapshots": {"closest": {
            "available": True, "url": "https://web.archive.org/web/20260101/https://example.org/x"}}}
        with patch.object(api, "_check_url", return_value=dead_probe):
            resolved, selected, _ = self.resolve({"ref_id": "r", "url": "https://example.org/x"},
                                                 {"archive.org/wayback/available?": available})
        self.assertEqual(resolved["source_tier"], "wayback")
        self.assertEqual((selected[1]["outcome"], selected[1]["payload"],
                          selected[1]["prov_ref"]),
                         ("selected", available, resolved["provenance_refs"][1]))

    def test_real_requester_failures_marker_json_and_budget_skip(self):
        class Body:
            def __init__(self, raw):
                self.raw = raw
                self.reads = 0

            def __enter__(self):
                return self

            def __exit__(self, *_):
                return False

            def read(self):
                self.reads += 1
                return self.raw

        for raw, category in ((b"\xff", "utf8-decode-failure"),
                              (b"not JSON", "json-parse-failure"),
                              (b'{"extra":' + b"9" * 5000 + b"}",
                               "json-parse-failure")):
            with self.subTest(category=category):
                body = Body(raw)
                ledger = ReliabilityLedger()
                store = ProvenanceStore(record_responses=True)
                with patch.object(api.urllib.request, "urlopen", return_value=body), \
                     patch.object(api, "_HTTP_MAX_RETRIES", 0), \
                     patch.object(api.time, "sleep"):
                    result = api.resolve_citation({"ref_id": "r", "doi": DOI},
                                                  ResponseCache(), store, ledger)
                self.assertEqual(result["resolution_status"], "not-checked")
                self.assertEqual(body.reads, 1)
                self.assertEqual(ledger.snapshot()["providers"]["crossref"]["errors"], 1)
                event = store.response_evidence()["events"][0]
                self.assertEqual((event["kind"], event["outcome"], event["category"]),
                                 ("request_failure", "invalid", category))
                self.assertNotIn("payload", event)

        body = Body(b'{"message":{"items":[]},"extra":NaN}')
        ledger = ReliabilityLedger()
        store = ProvenanceStore(record_responses=True)
        cache = ResponseCache()
        with patch.object(api.urllib.request, "urlopen", return_value=body), \
             patch.object(api.time, "sleep"):
            result = api.resolve_citation({"ref_id": "r", "title": TITLE},
                                          cache, store, ledger)
        self.assertEqual(result["resolution_status"], "not-checked")
        self.assertEqual(body.reads, 4)  # one read for each visited search tier
        self.assertEqual(ledger.snapshot()["providers"]["crossref"]["ok"], 1)
        self.assertIsNone(cache.get(f"crossref:search:{TITLE}:"))
        self.assertEqual(store.response_evidence()["events"][0]["kind"], "request_failure")

        marker = {"_error": "provider field", "_skipped": True, "nested": [1, None]}
        body = Body(json.dumps(marker).encode())
        store = ProvenanceStore(record_responses=True)
        with patch.object(api.urllib.request, "urlopen", return_value=body), \
             patch.object(api.time, "sleep"):
            result = api.resolve_citation({"ref_id": "r", "doi": DOI}, ResponseCache(), store)
        self.assertEqual(result["resolution_status"], "not-checked")
        event = store.response_evidence()["events"][0]
        self.assertEqual((event["kind"], event["payload"]), ("json_value", marker))
        self.assertEqual(body.reads, 1)

        store = ProvenanceStore(record_responses=True)
        ledger = ReliabilityLedger(budget=ProviderBudget({"crossref": 0}))
        with patch.object(api, "_fetch_json_network", side_effect=AssertionError("network")):
            result = api.resolve_citation({"ref_id": "r", "doi": DOI},
                                          ResponseCache(), store, ledger)
        self.assertEqual(result["resolution_status"], "not-checked")
        event = store.response_evidence()["events"][0]
        self.assertEqual((event["kind"], event["outcome"], event["origin"]),
                         ("skip", "skipped", "local"))
        self.assertEqual(ledger.snapshot()["providers"].get("crossref", {}).get("calls", 0), 0)

    def test_invalid_received_values_and_fail_closed_collection(self):
        invalids = (math.nan, "\ud800", (1, 2), {1: "coercible"})
        cycle = []
        cycle.append(cycle)
        for value in (*invalids, cycle):
            with self.subTest(value=type(value).__name__):
                result, events, _ = self.resolve({"ref_id": "r", "title": TITLE},
                                                 {"crossref.org/works?":
                                                  {"message": {"items": []}, "extra": value}})
                self.assertEqual(result["resolution_status"], "not-checked")
                self.assertEqual(events[0]["kind"], "request_failure")
                self.assertNotIn("payload_sha256", events[0])

        store = ProvenanceStore(record_responses=True)
        self.resolve({"ref_id": "r", "title": TITLE}, provenance=store)
        with patch("provenance.json_value_sha256", side_effect=RuntimeError("hash failed")):
            with self.assertRaisesRegex(RuntimeError, "hash failed"):
                self.resolve({"ref_id": "second", "doi": DOI},
                             {"crossref.org/works/": {"message": {"DOI": DOI}}},
                             provenance=store)
        with self.assertRaisesRegex(RuntimeError, "incomplete"):
            store.response_evidence()
        with self.assertRaisesRegex(RuntimeError, "incomplete"):
            store.save_response_evidence(str(Path(self.tmp.name) / "partial.json"))

    def test_observer_errors_do_not_retry_as_transport_failures(self):
        class Body:
            def __init__(self, raw):
                self.raw = raw
                self.reads = 0

            def __enter__(self):
                return self

            def __exit__(self, *_):
                return False

            def read(self):
                self.reads += 1
                return self.raw

        for error in (TimeoutError("collector failed"),
                      urllib.error.URLError("collector failed")):
            with self.subTest(error=type(error).__name__):
                body = Body(b'{"message":{"DOI":"10.1234/synthetic"}}')
                store = ProvenanceStore(record_responses=True)
                ledger = ReliabilityLedger()
                with patch.object(api.urllib.request, "urlopen", return_value=body) as opened, \
                     patch.object(api, "_HTTP_MAX_RETRIES", 1), \
                     patch("provenance.json_value_sha256", side_effect=error), \
                     patch.object(api.time, "sleep"):
                    with self.assertRaises(type(error)):
                        api.resolve_citation({"ref_id": "r", "doi": DOI},
                                             ResponseCache(), store, ledger)
                self.assertEqual((opened.call_count, body.reads), (1, 1))
                self.assertEqual(ledger.snapshot()["providers"].get("crossref", {}).get("calls", 0), 0)
                self.assertEqual(ledger.budget.spent()["crossref"], 1)
                with self.assertRaisesRegex(RuntimeError, "incomplete"):
                    store.response_evidence()

        body = Body(b"not JSON")
        store = ProvenanceStore(record_responses=True)
        with patch.object(api.urllib.request, "urlopen", return_value=body) as opened, \
             patch.object(api, "_HTTP_MAX_RETRIES", 1), \
             patch("provenance._utc_now", side_effect=TimeoutError("receipt failed")), \
             patch.object(api.time, "sleep"):
            with self.assertRaises(TimeoutError):
                api.resolve_citation({"ref_id": "r", "doi": DOI}, ResponseCache(), store)
        self.assertEqual((opened.call_count, body.reads), (1, 1))
        with self.assertRaisesRegex(RuntimeError, "incomplete"):
            store.response_evidence()

    def test_cache_origin_hash_failure_closes_prior_evidence(self):
        cache = ResponseCache()
        store = ProvenanceStore(record_responses=True)
        self.resolve({"ref_id": "first", "title": TITLE}, cache=cache, provenance=store)
        cache.get(f"crossref:search:{TITLE}:")["extra"] = 10 ** 5000
        with self.assertRaises(ValueError):
            self.resolve({"ref_id": "second", "title": TITLE},
                         cache=cache, provenance=store)
        with self.assertRaisesRegex(RuntimeError, "incomplete"):
            store.response_evidence()
        with self.assertRaisesRegex(RuntimeError, "incomplete"):
            store.save_response_evidence(str(Path(self.tmp.name) / "partial-cache.json"))

    def test_wayback_existing_shape_failure_keeps_circuit_accounting(self):
        dead_probe = {"status": 404, "live": False, "check_status": "not-found",
                      "method": "HEAD", "attempts": [], "wayback_allowed": True}
        invalid = {"archived_snapshots": None, "extra": math.nan}
        for enabled in (False, True):
            with self.subTest(enabled=enabled):
                ledger = ReliabilityLedger()
                store = ProvenanceStore(record_responses=enabled)
                for number in range(3):
                    with patch.object(api, "_check_url", return_value=dead_probe), \
                         patch.object(api, "_fetch_json_network",
                                      side_effect=fake_network({**EMPTY,
                                          "archive.org/wayback/available?": invalid}, [])), \
                         patch.object(api.time, "sleep"):
                        api.resolve_citation({"ref_id": str(number),
                                              "url": f"https://example.org/{number}"},
                                             ResponseCache(), store, ledger=ledger)
                wayback = ledger.snapshot()["providers"]["wayback"]
                self.assertEqual((wayback["errors"], wayback["ok"], wayback["circuit"]),
                                 (3, 0, "open"))

    def test_export_aliases_and_atomic_failure(self):
        target = Path(self.tmp.name) / "existing.json"
        target.write_text("old")
        alias = Path(self.tmp.name) / "alias.json"
        os.link(target, alias)
        with patch.object(api, "_default_cache_dir", return_value=str(Path(self.tmp.name) / "cache")):
            with self.assertRaises(ValueError):
                api.resolve_batch([], str(target), response_evidence_path=str(alias))
        self.assertEqual(target.read_text(), "old")
        sidecar = Path(self.tmp.name) / "Citation_Reliability.json"
        sidecar.symlink_to(target)
        with patch.object(api, "_default_cache_dir", return_value=str(Path(self.tmp.name) / "cache")):
            with self.assertRaises(ValueError):
                api.resolve_batch([], sidecar_dir=self.tmp.name,
                                  response_evidence_path=str(target))

        provenance = ProvenanceStore(record_responses=True)
        with patch("provenance.os.replace", side_effect=OSError("replace refused")):
            with self.assertRaises(OSError):
                provenance.save_response_evidence(str(target))
        self.assertEqual(target.read_text(), "old")
        self.assertEqual(list(Path(self.tmp.name).glob(".existing.json.*.tmp")), [])
        with patch("provenance.tempfile.NamedTemporaryFile", side_effect=OSError("write refused")):
            with self.assertRaises(OSError):
                provenance.save_response_evidence(str(target))
        self.assertEqual(target.read_text(), "old")
        with patch("provenance.json.dumps", side_effect=TypeError("serialize refused")):
            with self.assertRaises(TypeError):
                provenance.save_response_evidence(str(target))
        self.assertEqual(target.read_text(), "old")
        with self.assertRaisesRegex(RuntimeError, "incomplete"):
            provenance.response_evidence()

        output = Path(self.tmp.name) / "batch-old.json"
        output.write_text("old batch")
        with patch.object(api, "_default_cache_dir", return_value=str(Path(self.tmp.name) / "cache")), \
             patch("provenance.os.replace", side_effect=OSError("replace refused")):
            with self.assertRaises(OSError):
                api.resolve_batch([], str(output),
                                  response_evidence_path=str(Path(self.tmp.name) / "not-written.json"))
        self.assertEqual(output.read_text(), "old batch")

        evidence = Path(self.tmp.name) / "committed.json"
        missing_output = Path(self.tmp.name) / "missing" / "result.json"
        with patch.object(api, "_default_cache_dir", return_value=str(Path(self.tmp.name) / "cache")):
            with self.assertRaises(FileNotFoundError):
                api.resolve_batch([], str(missing_output),
                                  response_evidence_path=str(evidence))
        self.assertEqual(json.loads(evidence.read_text()),
                         {"schema": "apodictic.response-evidence.v1", "events": []})


if __name__ == "__main__":
    unittest.main()
