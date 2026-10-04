"""Invented navigation geometry fixtures; no corpus or reader qualification."""
from pathlib import Path
import sys
import unittest
import contextlib
import io
import json
import os
import subprocess
import tempfile
import shutil
from unittest.mock import patch
from decimal import Decimal

SCRIPTS = Path(__file__).resolve().parents[1] / "plugins" / "apodictic" / "scripts"
sys.path.insert(0, str(SCRIPTS))
import pdf_navigation as nav
import annotation_export as exporter


def block(kind, obj):
    return "<!-- apodictic:%s\n%s\n-->\n" % (kind, json.dumps(obj))


def normal_run(root, *, findings=True):
    """Produce real normal-run evidence through the existing manifest renderer."""
    snapshot = "# Chapter 1\nAn invented sentence.\n"
    ledger = "# Findings\n"
    if findings:
        ledger += block("finding", {"schema": "apodictic.finding.v1", "id": "F-TEST-01",
            "severity": "Must-Fix", "confidence": "HIGH", "mechanism": "Invented mechanism",
            "evidence_refs": ["Chapter 1"], "fix_class": "Invented class", "risk_if_fixed": "Invented risk"})
    timeline = "# Timeline\n"
    snapshot_name = "Invented_Manuscript_Snapshot_r.md"
    obj, errors = exporter.am.build_manifest(snapshot, ledger, timeline, project="Invented",
                                           runlabel="r", snapshot_path=snapshot_name)
    if errors:
        raise AssertionError(errors)
    files = {snapshot_name: snapshot, "Invented_Annotation_Manifest_r.md": block("annotation", obj),
             "Invented_Annotated_Manuscript_r.md": exporter.am.render(snapshot, obj),
             "Invented_Findings_Ledger_r.md": ledger, "Timeline.md": timeline}
    for name, text in files.items():
        (root / name).write_text(text, encoding="utf-8", newline="")
    return obj, snapshot, files


def serialize(value):
    """Test-side PDF serializer for semantically targeted hostile objects."""
    if isinstance(value, nav.Ref):
        return ("%d %d R" % value).encode()
    if isinstance(value, nav.Name):
        return b"/" + value.encode()
    if isinstance(value, nav.Stream):
        attributes = dict(value.attributes, Length=len(value.data))
        return serialize(attributes) + b"\nstream\n" + value.data + b"\nendstream"
    if isinstance(value, dict):
        return b"<< " + b" ".join(b"/" + str(k).encode() + b" " + serialize(v) for k, v in value.items()) + b" >>"
    if isinstance(value, list):
        return b"[" + b" ".join(serialize(v) for v in value) + b"]"
    if isinstance(value, bytes):
        return b"(" + value.replace(b"\\", b"\\\\").replace(b"(", b"\\(").replace(b")", b"\\)") + b")"
    if value is None:
        return b"null"
    if type(value) is bool:
        return b"true" if value else b"false"
    return str(value).encode()


def rewrite_pdf(pdf, edit):
    objects = nav.parse_pdf(pdf)
    edit(objects)
    data = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = []
    for number, value in sorted(objects.items()):
        offsets.append(len(data))
        data += ("%d 0 obj\n" % number).encode() + serialize(value) + b"\nendobj\n"
    start = len(data)
    data += ("xref\n0 %d\n" % (len(objects) + 1)).encode() + b"0000000000 65535 f\r\n"
    for offset in offsets:
        data += ("%010d 00000 n\r\n" % offset).encode()
    data += ("trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(objects) + 1, start)).encode()
    return bytes(data)


class ExactGeometryTests(unittest.TestCase):
    def test_unequal_prefixes_use_helvetica_advances(self):
        narrow = nav.ink_rectangle("[F-TEST-01]", "i", 2)
        wide = nav.ink_rectangle("[F-TEST-01]", "W", 2)
        self.assertEqual(wide[0] - narrow[0], 11 * (944 - 222))
        self.assertEqual(wide[2] - narrow[2], 11 * (944 - 222))

    def test_whitespace_advances_but_has_no_hit_box(self):
        self.assertIsNone(nav.ink_rectangle(" \u00a0 ", "", 3))
        self.assertEqual(nav.advance(" \u00a0"), 11 * 278 * 2)

    def test_mixed_euro_refuses_incomplete_ink(self):
        for text in ("€", "i€", "€i"):
            with self.subTest(text=text), self.assertRaises(nav.NavigationRefusal):
                nav.ink_rectangle(text, "", 0)

    def test_control_undefined_and_unicode_refuse(self):
        for text in ("\x00", "\t", "\x7f", "\x81", "雪"):
            with self.subTest(text=text), self.assertRaises(nav.NavigationRefusal):
                nav.ink_rectangle("marker", text, 0)

    def test_page_boundary_resets_baseline(self):
        first = nav.ink_rectangle("i", "", 0)
        last = nav.ink_rectangle("i", "", 44)
        next_page = nav.ink_rectangle("i", "", 45)
        self.assertEqual(first, next_page)
        self.assertEqual(first[1] - last[1], 44 * 14000)

    def test_outside_page_is_refused_without_clamping(self):
        with self.assertRaises(nav.NavigationRefusal):
            nav.ink_rectangle("marker", "W" * 80, 0)

    def test_exact_decimal_and_boundary_intersection(self):
        self.assertEqual([nav.decimal(x) for x in (0, 1000, 1010, -1001)],
                         ["0", "1", "1.01", "-1.001"])
        self.assertFalse(nav.overlaps((0, 0, 10, 10), (10, 0, 20, 10)))
        self.assertTrue(nav.overlaps((0, 0, 10, 10), (9, 0, 20, 10)))


class OwnershipLayoutTests(unittest.TestCase):
    def test_owned_sequence_preserves_default_text_and_page_partition(self):
        snapshot = "line\n" * 39
        annotations = [{"finding_id": "F-TEST-01", "comment": "i" * 270,
                        "anchor": {"kind": "document", "value": ""}}]
        manifest = {"project": "Invented", "annotations": annotations}
        default, errors = exporter.build_pdf(manifest, snapshot)
        self.assertEqual(errors, [])
        title = manifest["project"] + exporter._PDF_TITLE_SUFFIX
        items, _ = nav.layout(snapshot, annotations, title, [4], lambda fid: fid)
        expected_streams = [exporter._pdf_content(items[n:n + 45]) for n in range(0, len(items), 45)]
        self.assertEqual(exporter._pdf_content_streams(default), expected_streams)

    def test_colocated_markers_and_decoy_comments(self):
        annotations = [
            {"finding_id": "F-TEST-02", "comment": "Mentions [F-TEST-01]"},
            {"finding_id": "F-TEST-01", "comment": "No identity in this comment"},
        ]
        items, links = nav.layout("A line.\n", annotations, "Title", [7, 7], lambda fid: fid)
        self.assertEqual(items[2], ("show", "A line.[F-TEST-01][F-TEST-02]"))
        forward = {link[0]: link for link in links if link[1] == 2}
        self.assertEqual(items[forward["F-TEST-01"][3]][1], "No identity in this comment")
        self.assertEqual(items[forward["F-TEST-02"][3]][1], "Mentions [F-TEST-01]")
        self.assertEqual(len(links), 4)

    def test_comment_chunks_across_pages_return_to_owned_marker(self):
        annotation = {"finding_id": "F-TEST-01", "comment": "i" * 270}
        items, links = nav.layout("line\n" * 39, [annotation], "Title", [4], lambda fid: fid)
        self.assertEqual(len(links), 4)
        returns = [link for link in links if link[1] != 2]
        self.assertEqual({link[3] for link in returns}, {2})
        self.assertEqual({link[1] // 45 for link in returns}, {0, 1})

    def test_trailing_newline_marker_cannot_fabricate_a_line(self):
        annotation = {"finding_id": "F-TEST-01", "comment": "A comment"}
        with self.assertRaises(nav.NavigationRefusal):
            nav.layout("line\n", [annotation], "Title", [5], lambda fid: fid)

    def test_zero_findings_and_blank_chunks(self):
        _, zero = nav.layout("", [], "Title", [], lambda fid: fid)
        self.assertEqual(zero, [])
        annotation = {"finding_id": "F-TEST-01", "comment": " " * 90 + "ink"}
        _, links = nav.layout("line\n", [annotation], "Title", [4], lambda fid: fid)
        self.assertEqual(len(links), 2)
        self.assertEqual(links[0][3], 7)


class NavigationPDFTests(unittest.TestCase):
    def setUp(self):
        self.snapshot = "line\n" * 39
        self.obj = {"project": "Invented", "annotations": [{"finding_id": "F-TEST-01",
            "comment": "i" * 270, "anchor": {"kind": "document", "value": ""}}]}
        self.pdf, errors = exporter.build_pdf(self.obj, self.snapshot, internal_links=True)
        self.assertEqual(errors, [])
        items, self.links = exporter._pdf_navigation_layout(self.obj, self.snapshot)
        self.streams = [exporter._pdf_content(items[n:n + 45]).encode() for n in range(0, len(items), 45)]

    def test_deterministic_optin_and_default_bytes_unchanged(self):
        default = exporter.build_pdf(self.obj, self.snapshot)[0]
        self.assertEqual(default, exporter.build_pdf(self.obj, self.snapshot, internal_links=False)[0])
        self.assertEqual(self.pdf, exporter.build_pdf(self.obj, self.snapshot, internal_links=True)[0])
        self.assertEqual(exporter.check_pdf(self.obj, self.snapshot, self.pdf, internal_links=True), ([], []))
        self.assertTrue(exporter.check_pdf(self.obj, self.snapshot, default, internal_links=True)[0])
        self.assertTrue(exporter.check_pdf(self.obj, self.snapshot, self.pdf)[0])

    def test_link_tampering_fails_structurally_as_well_as_p1(self):
        def first_link(objects):
            return next(value for value in objects.values() if isinstance(value, dict) and value.get("Subtype") == nav.Name("Link"))
        def change_dest(objects):
            first_link(objects)["Dest"][0] = nav.Ref(999, 0)
        def change_rect(objects):
            first_link(objects)["Rect"][0] = Decimal("0.001")
        def inject_action(objects):
            first_link(objects)["A"] = {"S": nav.Name("JavaScript"), "JS": b"invented"}
        def duplicate_link(objects):
            objects[3]["Annots"].append(objects[3]["Annots"][0])
        def missing_link(objects):
            objects[3]["Annots"].pop()
        def wrong_owner(objects):
            objects[5]["Annots"] = objects[3].pop("Annots")
        def bool_box(objects):
            objects[3]["MediaBox"][0] = False
        for edit in (change_dest, change_rect, inject_action, duplicate_link, missing_link, wrong_owner, bool_box):
            with self.subTest(edit=edit.__name__):
                hostile = rewrite_pdf(self.pdf, edit)
                errors = exporter.check_pdf(self.obj, self.snapshot, hostile, internal_links=True)[0]
                self.assertTrue(any(error.startswith("P1") for error in errors))
                self.assertTrue(nav.check_structure(hostile, self.streams, self.links))

    def test_action_looking_prose_is_only_literal_text(self):
        obj = {"project": "Invented", "annotations": [{"finding_id": "F-TEST-01",
            "comment": r"/A /AA /JavaScript (endobj) \ /URI", "anchor": {"kind": "document", "value": ""}}]}
        pdf, errors = exporter.build_pdf(obj, "line\n", internal_links=True)
        self.assertEqual(errors, [])
        self.assertEqual(exporter.check_pdf(obj, "line\n", pdf, internal_links=True)[0], [])

    def test_stream_lengths_xref_and_duplicate_keys_are_validated(self):
        hostile = self.pdf.replace(b"/Length ", b"/Length 9", 1)
        self.assertTrue(nav.check_structure(hostile, self.streams, self.links))
        hostile = self.pdf.replace(b"00000 n\r\n", b"00001 n\r\n", 1)
        self.assertTrue(nav.check_structure(hostile, self.streams, self.links))
        hostile = self.pdf.replace(b"/Subtype /Link", b"/Subtype /Link /Subtype /Link", 1)
        self.assertTrue(nav.check_structure(hostile, self.streams, self.links))

    def test_fresh_build_refusal_blocks_p1(self):
        self.obj["annotations"][0]["comment"] = "i€"
        errors = exporter.check_pdf(self.obj, self.snapshot, self.pdf, internal_links=True)[0]
        self.assertTrue(any(error.startswith("P1") for error in errors))

    def test_overlapping_source_spans_and_cp1252_escapes(self):
        snapshot = "Wii (brackets) and \\ punctuation — £.\n"
        first, second = snapshot[:3], snapshot[1:3]
        annotations = [{"finding_id": "F-TEST-01", "comment": "§ ‘first’ (note) \\ end",
                        "anchor": {"kind": "quote", "value": "0-3", "quote": first}},
                       {"finding_id": "F-TEST-02", "comment": "No ID here",
                        "anchor": {"kind": "quote", "value": "1-3", "quote": second}}]
        obj = {"project": "Invented", "annotations": annotations}
        pdf, errors = exporter.build_pdf(obj, snapshot, internal_links=True)
        self.assertEqual(errors, [])
        self.assertEqual(exporter.check_pdf(obj, snapshot, pdf, internal_links=True)[0], [])

    def test_malformed_shapes_empty_comments_and_clipping_refuse(self):
        valid = {"finding_id": "F-TEST-01", "comment": "ink", "anchor": {"kind": "document", "value": ""}}
        for annotations in ([None], [dict(valid, finding_id=[])], [dict(valid, anchor=[])],
                            [dict(valid, comment=None)], [dict(valid, comment=" \u00a0 ")],
                            [dict(valid, comment="W" * 90)], [valid, valid]):
            with self.subTest(annotations=annotations):
                pdf, errors = exporter.build_pdf({"annotations": annotations}, "line\n", internal_links=True)
                self.assertIsNone(pdf)
                self.assertTrue(errors)
        pdf, errors = exporter.build_pdf({"annotations": [valid]}, "W" * 80 + "\n", internal_links=True)
        self.assertIsNone(pdf)
        self.assertTrue(errors)

    def test_scalar_annotations_refuse_before_checker_iteration(self):
        for annotations in (7, True, "invalid", {"wrong": "shape"}):
            with self.subTest(annotations=annotations):
                obj = {"annotations": annotations}
                pdf, errors = exporter.build_pdf(obj, "line\n", internal_links=True)
                self.assertIsNone(pdf)
                self.assertTrue(errors)
                errors = exporter.check_pdf(obj, "line\n", self.pdf, internal_links=True)[0]
                self.assertTrue(any(error.startswith("P1") for error in errors))

    def test_malformed_metrics_and_external_roster_refuse_without_external_reads(self):
        original = Path.read_bytes
        valid = json.loads((SCRIPTS / "pdf_metrics" / "helvetica-winansi.json").read_bytes())
        malformed = [[], {"schema": valid["schema"]}, dict(valid, sources={"../../outside": "invented"}),
                     dict(valid, glyphs={})]
        for table in malformed:
            with self.subTest(table_type=type(table).__name__):
                reads = []
                def read(path):
                    reads.append(path)
                    if path.name == "helvetica-winansi.json":
                        return json.dumps(table).encode()
                    return original(path)
                nav.metrics.cache_clear()
                try:
                    with patch.object(Path, "read_bytes", read):
                        pdf, errors = exporter.build_pdf(self.obj, self.snapshot, internal_links=True)
                    self.assertIsNone(pdf)
                    self.assertTrue(any("metrics" in error for error in errors))
                    self.assertTrue(all(path.is_relative_to(SCRIPTS / "pdf_metrics") for path in reads))
                finally:
                    nav.metrics.cache_clear()


class NavigationRunTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.obj, self.snapshot, self.files = normal_run(self.root)

    def tearDown(self):
        self.temp.cleanup()

    def test_real_normal_run_gate_and_separate_output(self):
        self.assertEqual(exporter.generate_pdf(str(self.root), internal_links=True)[0], 0)
        self.assertFalse((self.root / "pdf").exists())
        self.assertEqual(exporter.run_pdf([str(self.root)], internal_links=True)[0], 0)
        self.assertEqual(exporter.generate_pdf(str(self.root))[0], 0)
        self.assertEqual(exporter.run_pdf([str(self.root)])[0], 0)

    def test_requires_actual_copy_ledger_timeline_and_original_binding(self):
        for name in ("Invented_Annotated_Manuscript_r.md", "Invented_Findings_Ledger_r.md", "Timeline.md"):
            with self.subTest(name=name):
                (self.root / name).unlink()
                self.assertNotEqual(exporter.generate_pdf(str(self.root), internal_links=True)[0], 0)
                (self.root / name).write_text(self.files[name], encoding="utf-8", newline="")
        (self.root / "Invented_Annotated_Manuscript_r.md").write_text("changed\n", encoding="utf-8")
        self.assertEqual(exporter.generate_pdf(str(self.root), internal_links=True)[0], 1)

    def test_crlf_hash_is_not_normalized_before_authentication(self):
        name = self.root / "Invented_Manuscript_Snapshot_r.md"
        name.write_bytes(self.snapshot.replace("\n", "\r\n").encode())
        self.assertEqual(exporter.generate_pdf(str(self.root), internal_links=True)[0], 1)

    def test_same_hash_crlf_still_refuses_non_normalized_snapshot(self):
        raw = self.snapshot.replace("\n", "\r\n")
        (self.root / "Invented_Manuscript_Snapshot_r.md").write_bytes(raw.encode())
        self.obj["snapshot_sha256"] = exporter.am.sha256(raw)
        (self.root / "Invented_Annotation_Manifest_r.md").write_text(block("annotation", self.obj), encoding="utf-8")
        code, lines = exporter.generate_pdf(str(self.root), internal_links=True)
        self.assertEqual(code, 1)
        self.assertTrue(any("not already normalized" in line for line in lines))

    def test_manifest_filename_binding_and_unreadable_utf8_refuse(self):
        self.obj["snapshot_path"] = "missing.md"
        manifest = self.root / "Invented_Annotation_Manifest_r.md"
        manifest.write_text(block("annotation", self.obj), encoding="utf-8")
        self.assertNotEqual(exporter.generate_pdf(str(self.root), internal_links=True)[0], 0)
        manifest.write_bytes(b"\xff")
        self.assertEqual(exporter.generate_pdf(str(self.root), internal_links=True)[0], 2)

    def test_input_and_output_symlink_escapes_are_refused(self):
        with tempfile.TemporaryDirectory() as elsewhere:
            external = Path(elsewhere)
            for name in ("Invented_Manuscript_Snapshot_r.md", "Invented_Annotation_Manifest_r.md",
                         "Invented_Annotated_Manuscript_r.md", "Invented_Findings_Ledger_r.md", "Timeline.md"):
                path = self.root / name
                saved = path.read_bytes()
                target = external / name
                target.write_bytes(saved)
                path.unlink()
                try:
                    path.symlink_to(target)
                except OSError:
                    path.write_bytes(saved)
                    self.skipTest("native symlinks unavailable")
                self.assertEqual(exporter.generate_pdf(str(self.root), internal_links=True)[0], 2)
                path.unlink()
                path.write_bytes(saved)
            (self.root / "pdf-linked").symlink_to(external, target_is_directory=True)
            self.assertEqual(exporter.generate_pdf(str(self.root), internal_links=True)[0], 2)
            self.assertFalse(any(external.glob("*.pdf")))

    def test_default_pdf_survives_linked_output_aliases(self):
        default = self.root / "pdf"
        default.mkdir()
        target = default / "Invented_Annotated_Manuscript_r.pdf"
        target.write_bytes(b"existing default")
        linked = self.root / "pdf-linked"
        try:
            linked.symlink_to(default, target_is_directory=True)
        except OSError:
            self.skipTest("native symlinks unavailable")
        self.assertEqual(exporter.generate_pdf(str(self.root), internal_links=True)[0], 2)
        self.assertEqual(target.read_bytes(), b"existing default")
        linked.unlink()
        linked.mkdir()
        alias = linked / target.name
        alias.symlink_to(target)
        self.assertEqual(exporter.generate_pdf(str(self.root), internal_links=True)[0], 2)
        self.assertEqual(target.read_bytes(), b"existing default")
        alias.unlink()
        os.link(target, alias)
        self.assertEqual(exporter.generate_pdf(str(self.root), internal_links=True)[0], 2)
        self.assertEqual(target.read_bytes(), b"existing default")

    def test_nonbytes_artifact_is_named_refusal(self):
        for artifact in (None, "PDF", 7, True):
            errors, warnings = exporter.check_pdf(self.obj, (self.root / "Invented_Manuscript_Snapshot_r.md").read_text(encoding="utf-8"), artifact, internal_links=True)
            self.assertEqual(errors, ["N navigation artifact must be bytes"])
            self.assertEqual(warnings, [])

    def test_linked_pdf_selection_is_unique_and_contained(self):
        self.assertEqual(exporter.generate_pdf(str(self.root), internal_links=True)[0], 0)
        directory = self.root / "pdf-linked"
        source = next(directory.glob("*.pdf"))
        other = directory / "Other_Annotated_Manuscript_r.pdf"
        other.write_bytes(source.read_bytes())
        self.assertEqual(exporter.run_pdf([str(self.root)], internal_links=True)[0], 2)
        other.unlink()
        with tempfile.TemporaryDirectory() as elsewhere:
            target = Path(elsewhere) / source.name
            target.write_bytes(source.read_bytes())
            source.unlink()
            try:
                source.symlink_to(target)
            except OSError:
                self.skipTest("native symlinks unavailable")
            self.assertEqual(exporter.run_pdf([str(self.root)], internal_links=True)[0], 2)

    def test_w1_advisory_is_surfaced_without_prose(self):
        timeline = "# Timeline\n\n## 1. Event Ledger\n\n| Scene ID | Line range |\n|---|---|\n| S1 | 1-99 |\n"
        (self.root / "Timeline.md").write_text(timeline, encoding="utf-8")
        code, lines = exporter.generate_pdf(str(self.root), internal_links=True)
        self.assertEqual(code, 0)
        self.assertTrue(any("WARN W1 boundary drift" in line for line in lines))

    def test_second_parsed_manifest_block_and_ambiguous_snapshot_refuse(self):
        manifest = self.root / "Invented_Annotation_Manifest_r.md"
        for additional in (block("annotation", self.obj), "<!-- apodictic:annotation\nnot JSON\n-->\n"):
            with self.subTest(additional=additional[:24]):
                manifest.write_text(self.files[manifest.name] + additional, encoding="utf-8")
                self.assertEqual(exporter.generate_pdf(str(self.root), internal_links=True)[0], 1)
        manifest.write_text(self.files[manifest.name], encoding="utf-8")
        (self.root / "Other_Manuscript_Snapshot_r.md").write_text(self.snapshot, encoding="utf-8")
        self.assertEqual(exporter.generate_pdf(str(self.root), internal_links=True)[0], 2)

    def test_no_default_pdf_fallback(self):
        self.assertEqual(exporter.generate_pdf(str(self.root))[0], 0)
        self.assertEqual(exporter.run_pdf([str(self.root)], internal_links=True)[0], 2)

    def test_refusal_and_failed_replace_preserve_existing_output(self):
        self.assertEqual(exporter.generate_pdf(str(self.root), internal_links=True)[0], 0)
        output = next((self.root / "pdf-linked").glob("*.pdf"))
        before = output.read_bytes()
        with patch.object(exporter.os, "replace", side_effect=OSError("invented failure")):
            self.assertEqual(exporter.generate_pdf(str(self.root), internal_links=True)[0], 2)
        self.assertEqual(output.read_bytes(), before)
        self.assertEqual(list(output.parent.glob(".pdf-linked-*.tmp")), [])
        manifest = self.root / "Invented_Annotation_Manifest_r.md"
        self.obj["annotations"][0]["comment"] = "i€"
        manifest.write_text(block("annotation", self.obj), encoding="utf-8")
        self.assertEqual(exporter.generate_pdf(str(self.root), internal_links=True)[0], 1)
        self.assertEqual(output.read_bytes(), before)

    def test_zero_findings_needs_neither_missing_ledger_nor_timeline(self):
        normal_run(self.root, findings=False)
        (self.root / "Invented_Findings_Ledger_r.md").unlink()
        (self.root / "Timeline.md").unlink()
        code, lines = exporter.generate_pdf(str(self.root), internal_links=True)
        self.assertEqual(code, 0)
        self.assertTrue(any("0 finding(s)" in line for line in lines))
        output = next((self.root / "pdf-linked").glob("*.pdf"))
        objects = nav.parse_pdf(output.read_bytes())
        self.assertFalse(any(isinstance(value, dict) and "Annots" in value for value in objects.values()))

    def test_cli_flag_propagation_and_misplacement(self):
        def call(*args):
            with contextlib.redirect_stdout(io.StringIO()):
                return exporter.main(["annotation_export.py", *args])
        self.assertEqual(call("pdf", str(self.root), "--internal-links"), 0)
        self.assertEqual(call("pdf-export", "--internal-links", str(self.root)), 0)
        for args in (("html", str(self.root), "--internal-links"), ("--internal-links", "pdf", str(self.root)),
                     ("pdf", str(self.root), "--internal-links", "--internal-links"),
                     ("--self-test", "--internal-links"), ("pdf", str(self.root), "--internal-links=true")):
            with self.subTest(args=args):
                self.assertEqual(call(*args), 2)


class ShellNavigationTests(unittest.TestCase):
    def setUp(self):
        candidate = Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "Git" / "bin" / "bash.exe"
        self.bash = str(candidate) if candidate.is_file() else shutil.which("bash")
        if not self.bash:
            self.skipTest("Bash unavailable")
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        normal_run(self.root)

    def tearDown(self):
        if hasattr(self, "temp"):
            self.temp.cleanup()

    def shell(self, command, args, *, python=True, helper=True):
        # Source the actual command arm with an isolated public invocation argv;
        # missing-helper $0 is a fresh fixture path, never a deleted repo file.
        script = ("python3() { \"%s\" \"$@\"; }; " % Path(sys.executable).as_posix()) if python else (
            'command() { if [ "$1" = "-v" ] && [ "$2" = "python3" ]; then return 1; fi; builtin command "$@"; }; ')
        script += 'COMMAND="$1"; shift; . "%s"' % (SCRIPTS / "validate.d" / "commands-b.sh").as_posix()
        zero = SCRIPTS / "validate.sh" if helper else self.root / "missing-helper.sh"
        return subprocess.run([self.bash, "-c", script, zero.as_posix(), command, *args],
                              text=True, capture_output=True, timeout=30)

    def test_mode_propagation_and_missing_dependencies_fail_closed(self):
        self.assertEqual(exporter.generate_pdf(str(self.root), internal_links=True)[0], 0)
        args = [self.root.as_posix(), "--internal-links"]
        actual = self.shell("pdf-export", args)
        self.assertEqual(actual.returncode, 0, actual.stdout + actual.stderr)
        for python, helper in ((False, True), (True, False), (False, False)):
            with self.subTest(python=python, helper=helper):
                actual = self.shell("pdf-export", args, python=python, helper=helper)
                self.assertEqual(actual.returncode, 2, actual.stdout + actual.stderr)
                self.assertIn("navigation validation unavailable", actual.stdout)
        default = self.shell("pdf-export", [self.root.as_posix()], python=False)
        self.assertEqual(default.returncode, 0)
        self.assertIn("WARN", default.stdout)

    def test_misplaced_repeated_and_selftest_flags_refuse_without_python(self):
        cases = [("html-export", [self.root.as_posix(), "--internal-links"]),
                 ("docx-export", [self.root.as_posix(), "--internal-links"]),
                 ("obsidian-export", [self.root.as_posix(), "--internal-links"]),
                 ("pdf-export", [self.root.as_posix(), "--internal-links", "--internal-links"]),
                 ("pdf-export", ["--self-test", "--internal-links"]),
                 ("pdf-export", [self.root.as_posix(), "--internal-links=true"])]
        for command, args in cases:
            with self.subTest(command=command, args=args):
                actual = self.shell(command, args, python=False, helper=False)
                self.assertEqual(actual.returncode, 2, actual.stdout + actual.stderr)
                self.assertIn("usage", actual.stdout)


if __name__ == "__main__":
    unittest.main()
