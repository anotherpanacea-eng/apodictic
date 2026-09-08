import copy
import json
from pathlib import Path
import tempfile
import os
import unittest
from unittest.mock import patch
import score


def sample():
    basis = {"output_quote": "", "submission_quotes": [], "rationale": "No planted issue applies."}
    grade = {"id": "s001", "planted_mechanism": "not_applicable", "planted_basis": basis,
             "unsupported_findings": [], "fabricated_content": [], "mandatory_invention": [],
             "central_key_ambiguity": False, "key_ambiguities": [],
             "components": dict(score.WEIGHTS), "component_rationales": {k: "Grounded rationale." for k in score.WEIGHTS},
             "recognition": "no", "summary": "No unsupported diagnosis."}
    packet = {"id": "s001", "submission": "The clock reads five.\nNo one leaves.",
              "diagnosis": "The clock reads five. This does not contradict the scene."}
    return grade, packet


class ScoreTests(unittest.TestCase):
    def test_complete_structured_grade(self):
        grade, packet = sample()
        self.assertEqual(score.validate_grade(grade, packet), grade)

    def test_identity_mismatch_refuses(self):
        grade, packet = sample()
        grade["id"] = "s002"
        with self.assertRaisesRegex(ValueError, "identity"):
            score.validate_grade(grade, packet)

    def test_invented_diagnosis_quote_refuses(self):
        grade, packet = sample()
        grade["unsupported_findings"] = [{"output_quote": "He dies at midnight.", "submission_quotes": [],
                                          "rationale": "Unsupported.", "severity": "Must-Fix", "kind": "continuity"}]
        with self.assertRaisesRegex(ValueError, "diagnosis quote"):
            score.validate_grade(grade, packet)

    def test_quote_normalization_only_whitespace(self):
        grade, packet = sample()
        grade["planted_mechanism"] = "yes"
        grade["planted_basis"] = {"output_quote": "The clock  reads five.",
                                  "submission_quotes": ["No one\nleaves."], "rationale": "Illustrative validation example."}
        score.validate_grade(grade, packet)
        grade["planted_basis"]["submission_quotes"] = ["Nobody leaves."]
        with self.assertRaisesRegex(ValueError, "submission quote"):
            score.validate_grade(grade, packet)

    def test_numeric_scale_rejects_nan_bool_and_nonanchor(self):
        for value in (float("nan"), True, 17):
            grade, packet = sample()
            grade["components"]["correctness"] = value
            with self.assertRaises(ValueError):
                score.validate_grade(grade, packet)

    def test_positive_hit_requires_submission_anchor(self):
        grade, packet = sample()
        grade["planted_mechanism"] = "yes"
        grade["planted_basis"]["output_quote"] = "The clock reads five."
        with self.assertRaisesRegex(ValueError, "submission evidence"):
            score.validate_grade(grade, packet)

    def test_keys_never_open_before_all_productions_sealed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with patch.object(score.exp, "verify_freeze", return_value={"runs": [{"id": "r001"}]}), patch.object(score.exp, "tracked_bytes") as reads:
                with self.assertRaisesRegex(ValueError, "All planned productions"):
                    score.assemble(root, root / "scoring", root)
                reads.assert_not_called()

    def test_extra_field_cannot_smuggle_metadata(self):
        grade, packet = sample()
        grade["model"] = "guessed model"
        with self.assertRaisesRegex(ValueError, "keys mismatch"):
            score.validate_grade(grade, packet)


    def test_invalid_grade_stops_new_dispatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = {"cli": "unused", "cli_version": "v1", "runs": [{"id": f"g{i:03d}"} for i in range(128)]}
            def fake(root, manifest, row, retry):
                return {"id": row["id"], "status": "complete"}
            with patch.object(score, "verify", return_value=manifest), patch.object(score.subprocess, "check_output", return_value="v1"), patch.object(score.exp, "execute_one", side_effect=fake) as calls, patch.object(score, "grade_receipt", return_value=(None, "bad quote")):
                with self.assertRaisesRegex(RuntimeError, "invalid grade"):
                    score.run(root)
                self.assertLessEqual(calls.call_count, 2)
            self.assertFalse((root / "run.lock").exists())

    def test_scoring_recovery_refuses_live_controller(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            score.exp.write_json(root / "run.lock", {"pid": os.getpid()})
            with patch.object(score, "verify", return_value={"runs": [{"id": "g001"}]}):
                with self.assertRaisesRegex(ValueError, "controller is live"):
                    score.recover(root, "g001")

    def test_scoring_recovery_preserves_partial_grade(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = root / "outputs/g001"
            folder.mkdir(parents=True)
            score.exp.write_json(root / "run.lock", {"pid": 999999})
            score.exp.write_json(folder / "started.json", {"parent_pid": 999999, "started_utc": "2026-09-07T00:00:00Z"})
            (folder / "output.txt").write_bytes(b"partial JSON")
            row = {"id": "g001", "model": "example", "prompt_sha256": "a" * 64}
            with patch.object(score, "verify", return_value={"runs": [row]}), patch.object(score.exp, "process_alive", return_value=False):
                score.recover(root, "g001")
            self.assertEqual(score.exp.verified_completion(folder)["status"], "interrupted")
            self.assertEqual((folder / "output.txt").read_bytes(), b"partial JSON")


    def test_negative_hit_submission_quotes_still_must_exist(self):
        grade, packet = sample()
        grade["planted_mechanism"] = "no"
        grade["planted_basis"]["submission_quotes"] = ["not in text"]
        with self.assertRaisesRegex(ValueError, "submission quote"):
            score.validate_grade(grade, packet)

    def test_negative_hit_may_cite_real_submission_without_output_quote(self):
        grade, packet = sample()
        grade["planted_mechanism"] = "no"
        grade["planted_basis"]["submission_quotes"] = ["No one leaves."]
        score.validate_grade(grade, packet)


if __name__ == "__main__":
    unittest.main()
