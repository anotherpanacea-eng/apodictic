"""Black-box tests for the finite offline citation extraction contract."""

import builtins
import hashlib
import importlib.util
import json
from pathlib import Path
import socket
import subprocess
import sys
import unittest
from unittest.mock import patch


MODULE = (Path(__file__).resolve().parents[1] / "plugins" / "apodictic"
          / "skills" / "research-verification" / "scripts" / "citation_extract.py")
SPEC = importlib.util.spec_from_file_location("citation_extract", MODULE)
api = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(api)

TOP_KEYS = {"schema_version", "grammar", "status", "coverage", "citations"}
RECORD_KEYS = {"kind", "status", "reason", "span", "raw_citation_text",
               "normalized_citation", "definition_span", "quote_span",
               "claim_corridor_span", "attachment_method"}
NORMAL_KEYS = {"doi", "url", "title", "author", "year"}


def result(records, status=None):
    return {"schema_version": 1, "grammar": "m1-local-v1",
            "status": status or ("recognized_surfaces" if records else "no_matches"),
            "coverage": "admitted_syntax_only", "citations": records}


def record(kind, text, start, end, *, doi=None, url=None, title=None,
           author=None, year=None, definition=None, quote=None, corridor=None,
           status="extracted", reason=None):
    span = lambda pair: None if pair is None else {
        "start": pair[0], "end": pair[1]}
    return {
        "kind": kind, "status": status, "reason": reason,
        "span": {"start": start, "end": end},
        "raw_citation_text": text[start:end],
        "normalized_citation": {"doi": doi, "url": url, "title": title,
                                "author": author, "year": year},
        "definition_span": span(definition), "quote_span": span(quote),
        "claim_corridor_span": span(corridor),
        "attachment_method": "paragraph" if corridor else "none",
    }


class CitationExtractionTests(unittest.TestCase):
    def assert_spans(self, text, output):
        self.assertEqual(set(output), TOP_KEYS)
        self.assertEqual(output["coverage"], "admitted_syntax_only")
        self.assertEqual(output["citations"], sorted(
            output["citations"], key=lambda row: (
                row["span"]["start"], row["span"]["end"])))
        last_end = 0
        for row in output["citations"]:
            self.assertEqual(set(row), RECORD_KEYS)
            self.assertEqual(set(row["normalized_citation"]), NORMAL_KEYS)
            start, end = row["span"]["start"], row["span"]["end"]
            self.assertTrue(0 <= start < end <= len(text))
            self.assertGreaterEqual(start, last_end)
            self.assertEqual(row["raw_citation_text"], text[start:end])
            last_end = end
            for name in ("definition_span", "quote_span", "claim_corridor_span"):
                if row[name] is not None:
                    span = row[name]
                    self.assertEqual(set(span), {"start", "end"})
                    self.assertTrue(0 <= span["start"] < span["end"] <= len(text))
                    self.assertTrue(text[span["start"]:span["end"]])
        json.dumps(output)

    def test_four_exact_goldens(self):
        footnote = "A result.[^n]\n\n[^n]: doi:10.1234/alpha\n"
        author = ("A result (Smith, 2020).\n\nReferences\n"
                  "Smith, A. (2020). Alpha. doi:10.1234/alpha\n")
        link = "“A result” [study](https://example.org/a).\n"
        none = "In the discussion (Smith, 2020), the date is mentioned.\n"
        expectations = (
            (footnote, result([record("footnote", footnote, 9, 13,
                                      doi="10.1234/alpha", definition=(15, 38))])),
            (author, result([record("author_year", author, 9, 22,
                                    doi="10.1234/alpha", title="Alpha",
                                    author="Smith", year="2020",
                                    definition=(36, 78), corridor=(0, 23))])),
            (link, result([record("markdown_link", link, 11, 41,
                                  url="https://example.org/a", quote=(1, 9),
                                  corridor=(0, 42))])),
            (none, result([])),
        )
        for text, expected in expectations:
            with self.subTest(text=text):
                self.assertEqual(api.extract_citations(text), expected)
                self.assertEqual(api.extract_citations(text, media_type="text/plain"),
                                 expected)
                self.assert_spans(text, expected)

    def test_closed_status_and_fresh_results(self):
        self.assertEqual(api.extract_citations(""), result([]))
        self.assertEqual(api.extract_citations("10.1234/a", media_type="text/html"),
                         result([], "unsupported_format"))
        first = api.extract_citations("10.1234/a")
        first["citations"][0]["normalized_citation"]["doi"] = "mutated"
        first["citations"].append({})
        self.assertEqual(api.extract_citations("10.1234/a")["citations"][0]
                         ["normalized_citation"]["doi"], "10.1234/a")
        self.assertEqual(len(api.extract_citations("10.1234/a")["citations"]), 1)

    def test_boundary_validation_order_and_source_free_errors(self):
        cases = [
            (None, None, TypeError, "text must be str"),
            ("10.1234/a", None, TypeError, "media_type must be str"),
            ("x" * 1_000_001, "text/html", api.CitationExtractionError,
             "text exceeds extraction limit"),
            ("secret\rtext", "text/html", api.CitationExtractionError,
             "text must be LF-normalized Unicode scalar content"),
            ("secret\ud800", "text/plain", api.CitationExtractionError,
             "text must be LF-normalized Unicode scalar content"),
        ]
        for text, media_type, exc, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(exc, "^" + message + "$"):
                    api.extract_citations(text, media_type=media_type)
        self.assertEqual(api.extract_citations("x" * 1_000_000), result([]))

    def test_bare_locators_repeats_and_unicode_corridors(self):
        text = "É😀 10.1234/Alpha, 10.1234/Alpha.\n \t\nHTTPS://Example.org/A"
        output = api.extract_citations(text)
        self.assertEqual([r["kind"] for r in output["citations"]],
                         ["doi", "doi", "url"])
        self.assertEqual([r["normalized_citation"]["doi"] for r in
                          output["citations"][:2]], ["10.1234/alpha"] * 2)
        self.assertEqual(output["citations"][2]["normalized_citation"]["url"],
                         "HTTPS://Example.org/A")
        self.assertEqual(output["citations"][0]["claim_corridor_span"],
                         {"start": 0, "end": text.index("\n")})
        self.assertEqual(output["citations"][2]["claim_corridor_span"],
                         {"start": text.index("HTTPS"), "end": len(text)})
        self.assert_spans(text, output)

    def test_footnote_ambiguity_and_definitions(self):
        cases = [
            ("x [^n]", "missing_definition"),
            ("x [^n]\n\n[^n]: doi:10.1234/a\n[^n]: doi:10.1234/a",
             "multiple_definitions"),
            ("x [^n]\n\n[^n]:  doi:10.1234/a", "unsupported_definition"),
            ("x [^n]\n\n[^n]: doi:10.1234/a\n    continuation",
             "unsupported_definition"),
        ]
        for text, reason in cases:
            with self.subTest(reason=reason):
                rows = api.extract_citations(text)["citations"]
                self.assertEqual(len(rows), 1)
                self.assertEqual(rows[0]["reason"], reason)
                self.assertEqual(rows[0]["status"], "ambiguous")
                self.assertEqual(rows[0]["normalized_citation"],
                                 dict.fromkeys(NORMAL_KEYS))
                self.assertIsNone(rows[0]["definition_span"])
                self.assertIsNone(rows[0]["quote_span"])
                self.assertIsNone(rows[0]["claim_corridor_span"])
                self.assertEqual(rows[0]["attachment_method"], "none")
        for text in ("[^bad label]: https://example.org/a",
                     "[^" + "a" * 33 + "]: https://example.org/a",
                     " [^n]: https://example.org/a",
                     "[ref]: https://example.org/a",
                     "[ref]:\n    https://example.org/a"):
            with self.subTest(definition=text):
                self.assertEqual(api.extract_citations(text)["citations"], [])
        text = "x [^a][^b]\n\n[^a]: 10.1234/a\n[^b]: 10.1234/b"
        rows = api.extract_citations(text)["citations"]
        self.assertEqual([r["raw_citation_text"] for r in rows], ["[^a]", "[^b]"])
        self.assertEqual([r["normalized_citation"]["doi"] for r in rows],
                         ["10.1234/a", "10.1234/b"])

    def test_author_year_exact_keys_and_supported_entry(self):
        text = ("(Émile, 2020a) (Émile, 2020)\n\nReferences\n"
                "Émile, A. (2020a). A. complex title. 10.1234/A\n")
        rows = api.extract_citations(text)["citations"]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["normalized_citation"],
                         {"doi": "10.1234/a", "url": None,
                          "title": "A. complex title", "author": "Émile",
                          "year": "2020a"})
        for entries, reason in (
            ("Smith, A. (2020). Alpha. 10.1234/a\n"
             "Smith, B. (2020). Beta. 10.1234/b", "multiple_definitions"),
            ("Smith, A. (2020). unsupported", "unsupported_definition"),
        ):
            source = "(Smith, 2020)\n\nReferences\n" + entries
            row = api.extract_citations(source)["citations"][0]
            self.assertEqual((row["status"], row["reason"]),
                             ("ambiguous", reason))
            self.assertEqual(row["normalized_citation"],
                             {"doi": None, "url": None, "title": None,
                              "author": "Smith", "year": "2020"})
            self.assertIsNone(row["definition_span"])
            self.assertIsNone(row["claim_corridor_span"])
        for text in ("(Smith, 2020)", "Smith (2020)",
                     "(Smith, 2020a)\n\nReferences\nSmith, A. (2020). X. 10.1234/a",
                     "(smith, 2020)\n\nReferences\nSmith, A. (2020). X. 10.1234/a",
                     "(Smith, 2020)\n\n## Bibliography\nSmith, A. (2020). X."):
            self.assertEqual(api.extract_citations(text)["citations"], [])

    def test_code_brackets_and_opaque_fallback(self):
        malformed = (
            "[x](bad(inner) https://example.org/a)",
            "[[x]text](https://example.org/a)",
            "[broken https://example.org/x",
            "[LABEL][ID https://example.org/x",
            "[x](https://example.org/a\\) https://example.org/b)",
            "\\[study](https://example.org/a)",
            "\\doi:10.1234/a;https://example.org/x",
            "![x](https://example.org/a)",
            "[x](https://example.org/a https://example.org/b)",
            "[x](https://example.org/a",
            "[x](https://example.org/a(b))",
            "[x](https://user:pass@example.org/a)",
            "[x](https://example.org:/a)",
            "[x](https://example.org/a')",
            "http://example.org/a[broken]",
            "10.1234/a%2Fb",
            "https://example.org/a{bad}",
            "10.1234/a(b",
            "10.1234/a(((b)))",
        )
        for text in malformed:
            with self.subTest(text=text):
                self.assertEqual(api.extract_citations(text)["citations"], [])
        for text in ("\x60\x60\x60\n10.1234/a\n\x60\x60\x60",
                     "~~~ title\nhttps://example.org/a\n~~~",
                     "  \x60\x60\x60\x60\n10.1234/a\n  \x60\x60\x60",
                     "before \x60code 10.1234/a\x60 after",
                     "before \x60\x60code 10.1234/a\x60 after",
                     "before \x60unclosed 10.1234/a"):
            with self.subTest(code=text):
                self.assertEqual(api.extract_citations(text)["citations"], [])
        self.assertEqual(len(api.extract_citations(
            "\\\\10.1234/a")["citations"]), 1)

    def test_code_masked_bracket_closer_cannot_expose_destination(self):
        later = "https://example.org/b"
        for earlier in ("[x `]`](https://example.org/a)",
                        "[x `foo`](https://example.org/a)",
                        "[x](https://example.org/`)`)"):
            with self.subTest(earlier=earlier):
                text = earlier + " " + later
                self.assertEqual([row["raw_citation_text"] for row in
                                  api.extract_citations(text)["citations"]], [later])

    def test_doi_parentheses_and_whole_locator_rules(self):
        doi = "10.1016/s0140-6736(97)11096-0"
        for text, kind in (
            (doi, "doi"),
            ("[^n]\n\n[^n]: " + doi, "footnote"),
            ("(Smith, 2020)\n\nReferences\nSmith, A. (2020). X. " + doi,
             "author_year"),
            ("[paper](https://doi.org/" + doi + ")", "markdown_link"),
            ("10.1234/a(b(c)d)", "doi"),
        ):
            with self.subTest(text=text):
                rows = api.extract_citations(text)["citations"]
                self.assertEqual(len(rows), 1)
                self.assertEqual(rows[0]["kind"], kind)
                self.assertEqual(rows[0]["normalized_citation"]["doi"],
                                 doi if doi in text else "10.1234/a(b(c)d)")
        text = "10.1234/a). https://example.org/a]"
        self.assertEqual([r["raw_citation_text"] for r in
                          api.extract_citations(text)["citations"]],
                         ["10.1234/a", "https://example.org/a"])
        for text in ("10.1234/a(b(c(d)e)f)", "10.1234/a(b",
                     "[x](https://doi.org/10.1234/a(b)",
                     "https://example.org/a(b)",
                     "https://doi.org:443/10.1234/a(b)"):
            with self.subTest(invalid=text):
                self.assertEqual(api.extract_citations(text)["citations"], [])
        unsupported = api.extract_citations(
            "[^n]\n\n[^n]: 10.1234/a)")["citations"]
        self.assertEqual(len(unsupported), 1)
        self.assertEqual((unsupported[0]["status"], unsupported[0]["reason"]),
                         ("ambiguous", "unsupported_definition"))

    def test_quote_association_and_clusters(self):
        for text, expected in (
            ('"q" [a](https://a.example)', (1, 2)),
            ('“q” [a](https://a.example)', (1, 2)),
            ('"q"[a](https://a.example)', (1, 2)),
            ('"q", [a](https://a.example)', None),
            ('"q" words [a](https://a.example)', None),
            ('"q" [a](https://a.example); [b](https://b.example)', None),
            ('"q" [a](https://a.example); [b][ref]', None),
            ('"q" [a](https://a.example); (Smith, 2020)', None),
            ('"q" [a](https://a.example).', (1, 2)),
        ):
            with self.subTest(text=text):
                rows = api.extract_citations(text)["citations"]
                self.assertGreaterEqual(len(rows), 1)
                actual = rows[0]["quote_span"]
                self.assertEqual(actual, None if expected is None else
                                 {"start": expected[0], "end": expected[1]})
        for text in ('"10.1234/a"', '“10.1234/a”',
                     '"q https://a.example', '“q" https://a.example',
                     '"" 10.1234/a'):
            rows = api.extract_citations(text)["citations"]
            self.assertTrue(all(r["quote_span"] is None for r in rows))
            if text.startswith(('"10.', '“10.')):
                self.assertEqual(rows, [])
        text = '"q"\n[a](https://a.example)'
        self.assertIsNone(api.extract_citations(text)["citations"][0]["quote_span"])
        text = '"q" [^a]\n\n[^a]: 10.1234/a'
        row = api.extract_citations(text)["citations"][0]
        self.assertEqual(row["quote_span"], {"start": 1, "end": 2})
        self.assertEqual(row["attachment_method"], "none")

    def test_long_escape_run_inside_quote_is_bounded(self):
        slashes = "\\" * 20_000
        url = "https://example.org/a"
        text = '"' + slashes + '" ' + url
        rows = api.extract_citations(text)["citations"]
        self.assertEqual([row["raw_citation_text"] for row in rows], [url])
        self.assertEqual(rows[0]["quote_span"],
                         {"start": 1, "end": 1 + len(slashes)})

    def test_external_character_to_byte_boundaries(self):
        cases = (
            ("c3a90d0a31302e313233342f61", "é\n10.1234/a",
             (0, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13),
             (2, 11), (4, 13),
             "2b765b0ef7c67496e7910bb391737c23eecb89fa7a8a85d3e8b609d864804ca9"),
            ("f09f988065cc810d31302e313233342f61", "😀e\u0301\n10.1234/a",
             (0, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17),
             (4, 13), (8, 17),
             "fd810b2c25b69e2eb15eeb7cde4ae98faf42ea5527242f94fd7b07d250ff20e1"),
        )
        for source_hex, text, boundary, chars, byte_span, raw_hash in cases:
            with self.subTest(chars=chars):
                raw = bytes.fromhex(source_hex)
                self.assertEqual(hashlib.sha256(raw).hexdigest(), raw_hash)
                output = api.extract_citations(text)
                self.assertEqual(len(output["citations"]), 1)
                span = output["citations"][0]["span"]
                self.assertEqual((span["start"], span["end"]), chars)
                self.assertEqual((boundary[span["start"]], boundary[span["end"]]),
                                 byte_span)
                self.assertEqual(raw[byte_span[0]:byte_span[1]], b"10.1234/a")
                self.assert_spans(text, output)

    def test_dense_delimiters_and_long_input(self):
        for text in ("[" * 100_000 + " https://example.org/x",
                     "[x](" * 20_000 + " https://example.org/x",
                     "\x60\x60\x60\n" + "x" * 100_000 + " 10.1234/a"):
            self.assertEqual(api.extract_citations(text)["citations"], [])
        text = ("[x](bad) " * 10_000) + "https://example.org/ok"
        rows = api.extract_citations(text)["citations"]
        self.assertEqual([row["raw_citation_text"] for row in rows],
                         ["https://example.org/ok"])
        self.assertEqual(api.extract_citations("x" * 1_000_000), result([]))

    def test_bare_copy_import_and_no_runtime_io(self):
        script = ("import sys; sys.path.insert(0, sys.argv[1]); "
                  "from citation_extract import extract_citations; "
                  "assert extract_citations('10.1234/a')['citations'][0]"
                  "['raw_citation_text'] == '10.1234/a'")
        completed = subprocess.run(
            [sys.executable, "-S", "-c", script, str(MODULE.parent)],
            capture_output=True, text=True, check=False)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        with patch.object(builtins, "open", side_effect=AssertionError("file")), \
             patch.object(socket, "socket", side_effect=AssertionError("socket")), \
             patch.object(subprocess, "run", side_effect=AssertionError("process")):
            output = api.extract_citations(
                '"q" [paper](https://doi.org/10.1234/a)')
        self.assertEqual(len(output["citations"]), 1)


if __name__ == "__main__":
    unittest.main()
