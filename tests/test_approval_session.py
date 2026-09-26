"""Author-visible session behavior over real on-disk synthetic ledgers."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import approval_graph as engine

spec = importlib.util.spec_from_file_location("reconstruction_cases", ROOT / "evals/fixtures/argument-reconstruction/run_cases.py")
cases = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cases)


def decide(project, rid, action, **fields):
    return engine.adjudicate(project, {
        "action": action, "record_id": rid,
        "expected_head": engine.session_snapshot(project)["head"],
        "timestamp": cases.STAMP, **fields,
    })


def records(project):
    return {r["id"]: r for r in engine.session_snapshot(project)["records"]}


def test_resume_rebuilds_caches_and_retains_author_note(tmp_path):
    _, nodes, edges = cases.mint(engine, tmp_path, texts=("A is present.", "B is present."), edges=(("SUPPORTS", 0, 1, "—"),))
    snap = engine.session_snapshot(tmp_path)
    assert snap["session"]["next_record"] == min(nodes)
    decide(tmp_path, min(nodes), "approve", inclusion="OPTIONAL", note="Not a fact verdict.")
    before = engine.session_snapshot(tmp_path)
    (tmp_path / "Approval_Graph.md").write_text("stale", encoding="utf-8")
    (tmp_path / "Adjudication_Session.json").unlink()
    after = engine.session_snapshot(tmp_path)
    assert after["head"] == before["head"]
    assert after["progress"] == before["progress"]
    assert after["session"] == before["session"]
    assert records(tmp_path)[min(nodes)]["notes"][-1]["text"] == "Not a fact verdict."
    assert after["progress"]["adjudicated"] == 1


def test_stale_decision_does_not_append(tmp_path):
    head, nodes, _ = cases.mint(engine, tmp_path)
    decide(tmp_path, nodes[0], "approve", inclusion="REQUIRED")
    before = (tmp_path / "Approval_Events.jsonl").read_bytes()
    with pytest.raises(engine.ApprovalGraphError) as error:
        engine.adjudicate(tmp_path, {"action": "reject", "record_id": nodes[0], "expected_head": head, "timestamp": cases.STAMP})
    assert error.value.code == "STALE-HEAD"
    assert (tmp_path / "Approval_Events.jsonl").read_bytes() == before


@pytest.mark.parametrize("action", ["reject", "withdraw", "revise"])
def test_decision_cascades_approved_edges_atomically(tmp_path, action):
    _, nodes, edges = cases.mint(engine, tmp_path, texts=("A is present.", "B is present."), edges=(("SUPPORTS", 0, 1, "—"),))
    for rid in nodes:
        decide(tmp_path, rid, "approve", inclusion="REQUIRED")
    decide(tmp_path, edges[0], "approve")
    before = engine.session_snapshot(tmp_path)["head"]["bundle_count"]
    extra = {"replacement": {"type": "CLAIM", "text": "The author supplies a new claim."}} if action == "revise" else {}
    decide(tmp_path, nodes[0], action, **extra)
    snap = engine.session_snapshot(tmp_path)
    assert snap["head"]["bundle_count"] == before + 1
    assert records(tmp_path)[edges[0]]["approval"] == "PENDING"
    if action == "revise":
        successor = engine.node_id("CLAIM", extra["replacement"]["text"])
        assert records(tmp_path)[successor]["approval"] == "PENDING"
        assert records(tmp_path)[nodes[0]]["approval"] == "SUPERSEDED"


def test_author_must_supply_inclusion_and_finish_endpoints(tmp_path):
    _, nodes, edges = cases.mint(engine, tmp_path, texts=("A is present.", "B is present."), edges=(("SUPPORTS", 0, 1, "—"),))
    before = (tmp_path / "Approval_Events.jsonl").read_bytes()
    for rid, action, extra in [(nodes[0], "approve", {}), (edges[0], "approve", {}), (edges[0], "reject", {})]:
        with pytest.raises(engine.ApprovalGraphError):
            decide(tmp_path, rid, action, **extra)
        assert (tmp_path / "Approval_Events.jsonl").read_bytes() == before


def test_rejection_blocks_approval_until_explicit_unreject(tmp_path):
    _, nodes, _ = cases.mint(engine, tmp_path, texts=("A is present.", "B is present."))
    decide(tmp_path, nodes[0], "reject", note="Author declines.")
    before = (tmp_path / "Approval_Events.jsonl").read_bytes()
    with pytest.raises(engine.ApprovalGraphError) as error:
        decide(tmp_path, nodes[1], "approve", inclusion="OPTIONAL")
    assert error.value.code == "EXCLUSION-SCREEN-UNAVAILABLE"
    with pytest.raises(engine.ApprovalGraphError):
        decide(tmp_path, nodes[0], "revise", replacement={"type": "CLAIM", "text": "Replacement."})
    with pytest.raises(engine.ApprovalGraphError):
        decide(tmp_path, nodes[0], "unreject")
    assert (tmp_path / "Approval_Events.jsonl").read_bytes() == before
    decide(tmp_path, nodes[0], "unreject", reason="The author reconsidered the scope.")
    assert records(tmp_path)[nodes[0]]["approval"] == "PENDING"
    assert records(tmp_path)[nodes[0]]["history"][-1]["reason"] == "The author reconsidered the scope."
    decide(tmp_path, nodes[1], "approve", inclusion="OPTIONAL")


def test_orphaned_rejection_stays_visible_and_blocking(tmp_path):
    _, nodes, _ = cases.mint(engine, tmp_path, texts=("A is present.", "B is present."))
    decide(tmp_path, nodes[0], "reject")
    snap = engine.session_snapshot(tmp_path)
    engine.reconcile(tmp_path, {"nodes": [cases.node(engine, "B is present.")], "edges": []},
                     snap["context"], snap["head"], cases.STAMP)
    assert records(tmp_path)[nodes[0]]["presence"] == "ORPHANED"
    assert nodes[0] in engine.session_snapshot(tmp_path)["exclusions"]
    with pytest.raises(engine.ApprovalGraphError) as error:
        decide(tmp_path, nodes[1], "approve", inclusion="OPTIONAL")
    assert error.value.code == "EXCLUSION-SCREEN-UNAVAILABLE"


def test_closed_is_not_draft_ready_and_inclusion_needs_reason(tmp_path):
    _, nodes, _ = cases.mint(engine, tmp_path)
    decide(tmp_path, nodes[0], "approve", inclusion="REQUIRED")
    snap = engine.session_snapshot(tmp_path)
    engine.reconcile(tmp_path, {"nodes": [], "edges": []}, snap["context"], snap["head"], cases.STAMP)
    assert engine.session_snapshot(tmp_path)["session"]["status"] == "CLOSED"
    assert engine.validate_project(tmp_path, "draft-ready")["verdict"] == "ACTION-REQUIRED"
    with pytest.raises(engine.ApprovalGraphError):
        decide(tmp_path, nodes[0], "inclusion", inclusion="OPTIONAL")
    decide(tmp_path, nodes[0], "inclusion", inclusion="OPTIONAL", reason="The author no longer requires it.")
    assert engine.validate_project(tmp_path, "draft-ready")["verdict"] == "PASS"
    assert engine.validate_project(tmp_path, "acceptance")["verdict"] == "ACTION-REQUIRED"


def test_torn_suffix_recovers_but_committed_corruption_does_not(tmp_path):
    cases.mint(engine, tmp_path)
    path = tmp_path / "Approval_Events.jsonl"
    original = path.read_bytes()
    path.write_bytes(original + b'{"partial":')
    assert engine.session_snapshot(tmp_path)["recovered_bytes"] > 0
    assert path.read_bytes() == original
    path.write_bytes(original + b'{}\n')
    with pytest.raises(engine.ApprovalGraphError):
        engine.session_snapshot(tmp_path)
    assert path.read_bytes() == original + b'{}\n'


def test_empty_session_is_unstarted(tmp_path):
    (tmp_path / "Approval_Events.jsonl").write_bytes(b"")
    snap = engine.session_snapshot(tmp_path)
    assert snap["progress"]["total"] == 0
    assert snap["session"] == {"schema": "approval-session/1", "status": "SUSPENDED", "next_record": None}
    assert engine.validate_project(tmp_path, "draft-ready")["verdict"] == "ACTION-REQUIRED"


def test_snapshot_preserves_each_reconcile_reason_in_order(tmp_path):
    _, nodes, _ = cases.mint(engine, tmp_path)
    snap = engine.session_snapshot(tmp_path)
    engine.reconcile(tmp_path, {"nodes": [], "edges": []}, snap["context"], snap["head"], cases.STAMP)
    incoming = cases.node(engine, "A is present.")
    incoming["provenance"] = ["STATE:Argument_State_v1:C2", "STATE:Argument_State_v1:C3"]
    snap = engine.session_snapshot(tmp_path)
    engine.reconcile(tmp_path, {"nodes": [incoming], "edges": []}, snap["context"], snap["head"], cases.STAMP)
    history = records(tmp_path)[nodes[0]]["history"]
    latest = [entry for entry in history if entry["bundle"] == history[-1]["bundle"]]
    assert [entry["reason"] for entry in latest] == [None, "STATE:Argument_State_v1:C2", "STATE:Argument_State_v1:C3"]
    assert latest[0]["presence"] == ("ORPHANED", "CURRENT")


def test_cli_rejects_duplicate_keys_and_preserves_unicode_note(tmp_path):
    head, nodes, _ = cases.mint(engine, tmp_path)
    request = tmp_path / "decision.json"
    request.write_text('{"action":"approve","action":"reject"}', encoding="utf-8")
    cmd = [sys.executable, str(ROOT / "scripts/approval_session.py"), str(tmp_path), "--decision", str(request)]
    bad = subprocess.run(cmd, capture_output=True, text=True)
    assert bad.returncode == 1
    assert json.loads(bad.stdout)["error"] == "INVALID-REQUEST"
    request.write_text(json.dumps({"action": "approve", "record_id": nodes[0], "expected_head": head,
                                  "timestamp": cases.STAMP, "inclusion": "REQUIRED", "note": "Why—café?"}), encoding="utf-8")
    good = subprocess.run(cmd, capture_output=True, text=True)
    assert good.returncode == 0, good.stdout + good.stderr
    assert json.loads(good.stdout)["status"] == "COMMITTED"
    assert records(tmp_path)[nodes[0]]["notes"][-1]["text"] == "Why—café?"
