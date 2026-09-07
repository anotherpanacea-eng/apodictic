"""Protect experiment custody and the treatment boundary, not model behavior."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import os

SPEC = importlib.util.spec_from_file_location("experiment", Path(__file__).with_name("experiment.py"))
EXP = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(EXP)


class ExperimentTests(unittest.TestCase):
    def test_full_factorial_and_reproducible_order(self):
        rows = EXP.create_plan()
        self.assertEqual(rows, EXP.create_plan())
        keys = {(r["family"], r["member"], r["arm"], r["model"], r["repeat"]) for r in rows}
        expected = {(f, c, a, m, n) for f in EXP.FAMILIES for c in ("clean", "broken")
                    for a in ("baseline", "corrective") for m in EXP.MODELS for n in (1, 2)}
        self.assertEqual(keys, expected)
        self.assertEqual(len(rows), len(keys))
        self.assertEqual(len({r["id"] for r in rows}), len(rows))

    def test_treatment_changes_only_instruction(self):
        header = b"The identical diagnostic task."
        body = "A scene with cafÃ© and a clock.\n".encode()
        baseline = EXP.packet_bytes(header, body, "baseline")
        treatment = EXP.packet_bytes(header, body, "corrective")
        self.assertEqual(treatment.replace(EXP.CORRECTIVE.encode() + b"\n\n", b"", 1), baseline)
        self.assertEqual(baseline.split(b"<submission>\n")[1], treatment.split(b"<submission>\n")[1])

    def test_tampered_output_cannot_resume_as_complete(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / "output.txt").write_bytes(b"sealed")
            EXP.write_json(folder / "receipt.json", {"status": "complete", "hashes": {"output.txt": EXP.digest(b"sealed")}})
            self.assertEqual(EXP.verified_completion(folder)["status"], "complete")
            (folder / "output.txt").write_bytes(b"changed")
            with self.assertRaisesRegex(ValueError, "changed"):
                EXP.verified_completion(folder)

    def test_missing_receipt_is_not_completion(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / "output.txt").write_bytes(b"plausible answer")
            self.assertIsNone(EXP.verified_completion(folder))

    def test_tool_use_and_malformed_events_are_visible(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "events.jsonl"
            lines = [{"type": "item.completed", "item": {"type": "command_execution"}},
                     {"type": "turn.completed", "usage": {"input_tokens": 3, "output_tokens": 4}}]
            path.write_text("\n".join(json.dumps(e) for e in lines) + "\nnot json\n", encoding="utf-8")
            info = EXP.inspect_events(path)
            self.assertEqual(info["tool_events"], ["command_execution"])
            self.assertEqual(info["invalid_event_lines"], 1)
            self.assertTrue(info["turn_completed"])

    def test_manifest_and_frozen_bytes_are_bound(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "prompt.txt").write_bytes(b"frozen")
            manifest = {"runs": EXP.create_plan(), "artifacts": {"prompt.txt": EXP.digest(b"frozen")}}
            EXP.write_json(root / "manifest.json", manifest)
            EXP.write_json(root / "preregistration.json", {"manifest_sha256": EXP.digest((root / "manifest.json").read_bytes())})
            EXP.verify_freeze(root)
            (root / "prompt.txt").write_bytes(b"tuned")
            with self.assertRaisesRegex(ValueError, "artifact changed"):
                EXP.verify_freeze(root)
            (root / "prompt.txt").write_bytes(b"frozen")
            manifest["runs"].pop()
            EXP.write_json(root / "manifest.json", manifest)
            with self.assertRaisesRegex(ValueError, "Manifest changed"):
                EXP.verify_freeze(root)


    def test_process_check_recognizes_current_process(self):
        self.assertTrue(EXP.process_alive(os.getpid()))

    def test_live_controller_blocks_recovery(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            EXP.write_json(root / "run.lock", {"pid": os.getpid()})
            with patch.object(EXP, "verify_freeze", return_value={"runs": [{"id": "r001"}]}):
                with self.assertRaisesRegex(ValueError, "controller is live"):
                    EXP.recover(root, "r001")
            self.assertTrue((root / "run.lock").exists())

    def test_recovery_preserves_unsealed_bytes_and_does_not_claim_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = root / "outputs/r001"
            folder.mkdir(parents=True)
            EXP.write_json(root / "run.lock", {"pid": 999999})
            EXP.write_json(folder / "started.json", {"parent_pid": 999999, "started_utc": "2026-09-07T00:00:00Z"})
            (folder / "output.txt").write_bytes(b"partial")
            row = {"id": "r001", "model": "example", "prompt_sha256": "a" * 64}
            with patch.object(EXP, "verify_freeze", return_value={"runs": [row]}), patch.object(EXP, "process_alive", return_value=False):
                EXP.recover(root, "r001")
            self.assertEqual(EXP.verified_completion(folder)["status"], "interrupted")
            self.assertEqual((folder / "output.txt").read_bytes(), b"partial")
            self.assertFalse((root / "run.lock").exists())
            self.assertTrue((root / "stale-lock-r001.json").exists())

    def test_completed_answer_cannot_be_retried(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = root / "outputs/r001"
            folder.mkdir(parents=True)
            EXP.write_json(folder / "receipt.json", {"status": "complete", "hashes": {}})
            with self.assertRaisesRegex(ValueError, "Only one transport"):
                EXP.execute_one(root, {}, {"id": "r001"}, retry=True)

    def test_dispatch_stops_scheduling_after_transport_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rows = [{"id": f"r{i:03d}"} for i in range(64)]
            manifest = {"cli": "unused", "cli_version": "v1", "runs": rows}
            def fake(root, manifest, row, retry):
                return {"id": row["id"], "status": "failed"}
            with patch.object(EXP, "verify_freeze", return_value=manifest), patch.object(EXP.subprocess, "check_output", return_value="v1"), patch.object(EXP, "execute_one", side_effect=fake) as called:
                with self.assertRaisesRegex(RuntimeError, "Dispatch stopped"):
                    EXP.run(root)
                self.assertLessEqual(called.call_count, 2)
            self.assertFalse((root / "run.lock").exists())


if __name__ == "__main__":
    unittest.main()
