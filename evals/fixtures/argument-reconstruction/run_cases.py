#!/usr/bin/env python3
"""Executable Increment-1 acceptance candidates H1-H21.

This is a black-box fixture runner.  It imports the public approval_graph module
from ``--engine`` and creates disposable project directories; no fixture project
is retained as authority.  The cases are synthetic deterministic controls, not
semantic calibration or benchmark truth.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from typing import Any, Callable


ROOT = pathlib.Path(__file__).resolve().parents[4]
STAMP = "2026-09-20T00:00:00Z"
_ACTIVE_ENGINE = None


def load_engine(path: pathlib.Path):
    spec = importlib.util.spec_from_file_location("approval_graph_fixture_engine", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import engine: {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def source(project: pathlib.Path, text: str, filename: str = "manuscript.md") -> dict[str, Any]:
    data = text.encode("utf-8")
    target = project / filename
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return {"source_filename": filename, "source_sha256": sha(data), "argument_state": "Argument_State_v1"}


def node(engine, text: str, *, typ: str = "CLAIM", quote: str | None = None, location: str = "C1") -> dict[str, Any]:
    q = text if quote is None else quote
    return {
        "type": typ,
        "text": text,
        "anchors": [{"quote": q, "location": location}],
        "origin": "MANUSCRIPT",
        "provenance": ["STATE:Argument_State_v1:C1"],
        "flags": ["NONE"],
    }


def edge(engine, typ: str, src: str, dst: str, carried: str = "—") -> dict[str, Any]:
    return {"type": typ, "source": src, "target": dst, "carried_typing": carried}


def event(kind: str, actor: str, record_id: str, *, af=None, at=None, pf=None, pt=None,
          incf=None, inct=None, related=None, content=None, reason=None, note=None) -> dict[str, Any]:
    return {"event": kind, "actor": actor, "record_id": record_id,
            "related_record_id": related, "content": content,
            "approval_from": af, "approval_to": at, "presence_from": pf,
            "presence_to": pt, "inclusion_from": incf, "inclusion_to": inct,
            "reason": reason, "note": note}


def bundle(engine, shape: str, prev: str, context: dict[str, Any] | None, events: list[dict[str, Any]]) -> dict[str, Any]:
    return engine.seal_bundle({"shape": shape, "prev_hash": prev, "timestamp": STAMP,
                               "context": context, "events": events})


def append(engine, project: pathlib.Path, b: dict[str, Any], head: dict[str, Any]) -> dict[str, Any]:
    return engine.append_bundle(str(project), b, head)


def mint(engine, project: pathlib.Path, *, texts=("A is present.",), edges=(), context=None) -> tuple[dict[str, Any], list[str], list[str]]:
    if context is None:
        context = source(project, "\n".join(texts) + "\n")
    nodes = [node(engine, t) for t in texts]
    ids = [engine.node_id(n["type"], n["text"]) for n in nodes]
    edge_payloads = []
    edge_ids = []
    for typ, i, j, carried in edges:
        p = edge(engine, typ, ids[i], ids[j], carried)
        edge_payloads.append(p)
        edge_ids.append(engine.edge_id(p["type"], p["source"], p["target"], p["carried_typing"]))
    events = [event("MINTED", "normalizer", rid, content=p, at="PENDING", pt="CURRENT")
              for rid, p in sorted(zip(ids, nodes))]
    events += [event("MINTED", "normalizer", rid, content=p, at="PENDING", pt="CURRENT")
               for rid, p in sorted(zip(edge_ids, edge_payloads))]
    b = bundle(engine, "MINT", "GENESIS", context, events)
    result = append(engine, project, b, {"bundle_count": 0, "terminal_hash": "GENESIS"})
    return result["head"], ids, edge_ids


def ledger(project: pathlib.Path) -> list[dict[str, Any]]:
    p = project / "Approval_Events.jsonl"
    raw = p.read_bytes() if p.exists() else b""
    if not raw:
        return []
    lines = raw.split(b"\n")
    if lines and lines[-1] == b"":
        lines.pop()
    return [json.loads(line) for line in lines]


def state(engine, project: pathlib.Path) -> dict[str, Any]:
    return engine.replay(ledger(project))


def validate(engine, project: pathlib.Path, stage: str) -> dict[str, Any]:
    return engine.validate_project(str(project), stage)


def decisions(engine, project: pathlib.Path, head: dict[str, Any], ids: list[str], *, approve=True, inclusion="REQUIRED") -> dict[str, Any]:
    result = {"head": head}
    for rid in ids:
        inc = inclusion if rid.startswith("n-") else None
        if approve:
            ev = event("DECISION", "author", rid, af="PENDING", at="APPROVED", inct=inc)
        else:
            ev = event("DECISION", "author", rid, af="PENDING", at="REJECTED")
        b = bundle(engine, "DECISION", result["head"]["terminal_hash"], None, [ev])
        result = append(engine, project, b, result["head"])
    return result


def write_receipt(project: pathlib.Path, engine, *, draft=b"draft\n", verdict="ACTION-REQUIRED", head=None, gate=True) -> None:
    (project / "Reconstruction_Draft.md").write_bytes(draft)
    st = state(engine, project)
    graph = project / "Approval_Graph.md"
    if head is None:
        hs = st.get("head", {"bundle_count": 0, "terminal_hash": "GENESIS"})
    else:
        hs = head
    records = st.get("records", {})
    ids = sorted(records)
    rejected = sorted(rid for rid, rec in records.items() if rec.get("approval") == "REJECTED")
    ident = {"draft_filename": "Reconstruction_Draft.md", "draft_sha256": sha(draft),
             "graph_sha256": sha(graph.read_bytes()) if graph.exists() else sha(b""),
             "bundle_count": hs["bundle_count"], "terminal_hash": hs["terminal_hash"],
             "record_ids": ids, "rejected_ids": rejected}
    lines = ["# Reconstruction Receipt", "Identity: " + json.dumps(ident, ensure_ascii=False, separators=(",", ":")),
             "Verdict: " + verdict, ""]
    if gate:
        lines += ["### Gate Run 1", "Timestamp: " + STAMP, "Judge: fixture-deterministic/1",
                  "Config schema: UNAVAILABLE", "Config: I5-COMPARATOR-UNAVAILABLE",
                  "Prior config refs: NONE", "Author relaxation: NONE", "Verdict: " + verdict,
                  "", "#### Violations", ""]
    (project / "Reconstruction_Receipt.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")


def err_code(exc: BaseException) -> str:
    return str(getattr(exc, "code", "")) or exc.__class__.__name__


def expect_error(fn: Callable[[], Any], *codes: str) -> BaseException:
    try:
        fn()
    except Exception as exc:
        error_type = getattr(_ACTIVE_ENGINE, "ApprovalGraphError", None)
        if error_type is None or not isinstance(exc, error_type):
            raise AssertionError(f"expected ApprovalGraphError, got {type(exc).__name__}: {exc}") from exc
        code = err_code(exc)
        if codes and code not in codes:
            raise AssertionError(f"wrong stable error code {code}; expected one of {codes}") from exc
        return exc
    raise AssertionError("operation unexpectedly succeeded")


def run_cases(engine) -> list[dict[str, Any]]:
    global _ACTIVE_ENGINE
    _ACTIVE_ENGINE = engine
    outcomes: list[dict[str, Any]] = []

    def case(name: str, fn: Callable[[pathlib.Path], None]):
        try:
            with tempfile.TemporaryDirectory(prefix="argument-reconstruction-") as td:
                fn(pathlib.Path(td))
        except Exception as exc:
            import traceback
            outcomes.append({"id": name, "status": "FAIL", "error": str(exc), "traceback": traceback.format_exc()})
            return
        outcomes.append({"id": name, "status": "PASS"})

    def h1(p):
        head, ids, _ = mint(engine, p)
        head = decisions(engine, p, head, ids)["head"]
        head = engine.reconcile(str(p), {"nodes": [], "edges": []}, source(p, "changed\n"), head, STAMP)["head"]
        result = validate(engine, p, "draft-ready")
        assert result["verdict"] == "ACTION-REQUIRED"
        assert any("REQUIRED" in f["code"] or "WITHHELD" in f["code"] or "ORPHAN" in f["code"] for f in result["findings"])
    def h2(p):
        head, ids, eids = mint(engine, p, texts=("A.", "B."), edges=(("SUPPORTS", 0, 1, "—"),))
        head = decisions(engine, p, head, ids + eids)["head"]
        head = engine.reconcile(str(p), {"nodes": [node(engine, "B.")], "edges": []}, source(p, "B.\n"), head, STAMP)["head"]
        eligible = engine.eligible_ids(state(engine, p))
        assert engine.node_id("CLAIM", "A.") not in eligible and eids[0] not in eligible
        result = validate(engine, p, "graph")
        assert result["verdict"] == "PASS", result
        write_receipt(p, engine)
        receipt_path = p / "Reconstruction_Receipt.md"
        template = receipt_path.read_text(encoding="utf-8")
        for withheld in (ids[0], eids[0]):
            passage = ("### Passage p-1\nSpan: paragraphs 1–1\nKind: MAPPED\n"
                       + "Realizes: " + withheld + "\n\n")
            receipt_path.write_text(template.replace("### Gate Run 1", passage + "### Gate Run 1"), encoding="utf-8", newline="\n")
            result = validate(engine, p, "acceptance")
            assert any(f["code"] == "PASSAGE-REALIZES-INELIGIBLE" and f["record_id"] == withheld
                       for f in result["findings"]), result
            assert "I5-COMPARATOR-UNAVAILABLE" in {f["code"] for f in result["findings"]}
    def h3(p):
        # Independent known-answer vector (synthetic smoke material): these
        # values are computed from the contract framing, not engine helpers.
        known_text = "Budget savings are documented."
        assert engine.node_id("CLAIM", known_text) == "n-7734dbc06051"
        known_source = b"Budget savings are documented.\n"
        assert sha(known_source) == "80df9db36f72d1504ecedb01a172bbb4814385b479c3047bd27b31c66f86d947"
        known_ctx = {"source_filename": "manuscript.md", "source_sha256": sha(known_source), "argument_state": "Argument_State_v1"}
        known_payload = node(engine, known_text, location="paragraph 1")
        known_payload["provenance"] = ["STATE:Argument_State_v1:C0"]
        known_id = engine.node_id(known_payload["type"], known_payload["text"])
        known_event = event("MINTED", "normalizer", known_id, content=known_payload, at="PENDING", pt="CURRENT")
        known_bundle = engine.seal_bundle({"shape": "MINT", "prev_hash": "GENESIS",
                                           "timestamp": "2026-09-20T02:00:00Z", "context": known_ctx,
                                           "events": [known_event]})
        assert known_bundle["bundle_hash"] == "639b8cf30a74d58be50f22198f8f22fa6c7c301992a3050bc874558c12219c0e"
        ctx = source(p, "A.\nB.\n")
        head, ids, eids = mint(engine, p, texts=("A.", "B."), edges=(("SUPPORTS", 0, 1, "—"),), context=ctx)
        same = {"nodes": [node(engine, "A."), node(engine, "B.")],
                "edges": [edge(engine, "SUPPORTS", ids[0], ids[1], "—")]}
        before = (p / "Approval_Events.jsonl").read_bytes()
        r = engine.reconcile(str(p), same, ctx, head, STAMP)
        assert r["status"] == "NO-CHANGE"
        assert (p / "Approval_Events.jsonl").read_bytes() == before
        assert all(e.get("event") != "RECONCILE" or e.get("record_id", "").startswith("n-") for b in ledger(p) for e in b["events"])
        # F2: line-significant free strings round-trip through the projection parser.
        q = pathlib.Path(tempfile.mkdtemp(prefix="projection-free-") )
        try:
            c = source(q, 'A "quoted"\nnext\n')
            qhead, qids, _ = mint(engine, q, texts=('A "quoted"\nnext',), context=c)
            note = 'quote "\n" heading ### \u2028'
            nb = bundle(engine, "DECISION", qhead["terminal_hash"], None,
                        [event("DECISION", "author", qids[0], af="PENDING", at="APPROVED", inct="REQUIRED", note=note)])
            append(engine, q, nb, qhead)
            parsed = engine.parse_graph((q / "Approval_Graph.md").read_bytes())
            def has_value(value, target):
                if isinstance(value, str):
                    return value == target
                if isinstance(value, dict):
                    return any(has_value(v, target) for v in value.values())
                if isinstance(value, list):
                    return any(has_value(v, target) for v in value)
                return False
            assert has_value(parsed, 'A "quoted"\nnext')
            assert has_value(parsed, note)
            expect_error(lambda: engine.canonical_json({"x": {1: "bad"}}), "UNSUPPORTED-VALUE")
            # Unicode line separators are data inside JSON strings, never framing.
            uq = q / "unicode"
            uq.mkdir()
            uc = source(uq, "U\u2028line\n")
            mint(engine, uq, texts=("U\u2028line",), context=uc)
            up = engine.parse_graph((uq / "Approval_Graph.md").read_bytes())
            assert has_value(up, "U\u2028line")
            # A changed source context with the same anchor/ref is a real refresh,
            # and must be accepted while retaining the new source binding.
            rq = q / "refresh"
            rq.mkdir()
            c1 = source(rq, "Refresh anchor.\n")
            rh, rids, _ = mint(engine, rq, texts=("Refresh anchor.",), context=c1)
            c2 = source(rq, "Refresh anchor.\nContext changed.\n")
            rr = engine.reconcile(str(rq), {"nodes": [node(engine, "Refresh anchor.")], "edges": []}, c2, rh, STAMP)
            assert rr["status"] == "COMMITTED"
            assert state(engine, rq)["records"][rids[0]]["anchor_context"] == c2
            assert validate(engine, rq, "graph")["verdict"] == "PASS"
            # Correcting evidence under the same context retains a supplied ref.
            corrected = node(engine, "Refresh anchor.", location="corrected paragraph 1")
            result = engine.reconcile(rq, {"nodes": [corrected], "edges": []}, c2, rr["head"], STAMP)
            assert result["status"] == "COMMITTED"
            final_event = ledger(rq)[-1]["events"][0]
            assert final_event["reason"] in corrected["provenance"]
            assert set(state(engine, rq)["records"][rids[0]]["content"]["provenance"]) == set(corrected["provenance"])
        finally:
            shutil.rmtree(q, ignore_errors=True)
    def h4(p):
        head, ids, manuscript_edges = mint(engine, p, texts=("A.", "B."), edges=(("SUPPORTS", 0, 1, "—"),))
        draft = b"draft\n"
        (p / "Reconstruction_Draft.md").write_bytes(draft)
        eb = edge(engine, "TARGETS", ids[0], ids[1], "NONE (legacy-untyped)")
        eid = engine.edge_id(eb["type"], eb["source"], eb["target"], eb["carried_typing"])
        b = bundle(engine, "QUARANTINE", head["terminal_hash"], {"draft_version": "v1", "draft_sha256": sha(draft)},
                   [event("MINTED", "system", eid, content=eb, at="PENDING", pt="CURRENT")])
        head = append(engine, p, b, head)["head"]
        head = engine.reconcile(str(p), {"nodes": [node(engine, "A."), node(engine, "B.")], "edges": []}, source(p, "A.\nB.\n"), head, STAMP)["head"]
        st = state(engine, p)["records"]
        assert st[manuscript_edges[0]]["presence"] == "ORPHANED"
        assert st[eid]["presence"] == "CURRENT"
    def h5(p):
        head, _, _ = mint(engine, p)
        ledger_path = p / "Approval_Events.jsonl"
        before = ledger_path.read_bytes()
        graph_before = (p / "Approval_Graph.md").read_bytes()
        session_before = (p / "Adjudication_Session.json").read_bytes()
        lock = p / ".Approval_Events.lock"
        ready = p / "lock.ready"
        if os.name == "nt":
            script = ("import msvcrt,sys,time,pathlib; f=open(sys.argv[1],'a+b'); f.seek(0); "
                      "msvcrt.locking(f.fileno(),msvcrt.LK_LOCK,1); pathlib.Path(sys.argv[2]).write_text('ready'); time.sleep(20)")
        else:
            script = ("import fcntl,sys,time,pathlib; f=open(sys.argv[1],'a+b'); "
                      "fcntl.flock(f,fcntl.LOCK_EX); pathlib.Path(sys.argv[2]).write_text('ready'); time.sleep(20)")
        proc = subprocess.Popen([sys.executable, "-c", script, str(lock), str(ready)])
        try:
            for _ in range(100):
                if ready.exists(): break
                time.sleep(.02)
            ledger_path.open("ab").write(b'{"shape":"MINT"')
            result = validate(engine, p, "graph")
            assert result["verdict"] == "ACTION-REQUIRED"
            assert any("PROJECT-BUSY" in f["code"] for f in result["findings"])
            assert ledger_path.read_bytes() == before + b'{"shape":"MINT"'
            assert (p / "Approval_Graph.md").read_bytes() == graph_before
            assert (p / "Adjudication_Session.json").read_bytes() == session_before
        finally:
            proc.terminate(); proc.wait(timeout=5)
        # A same-process writer paused at the real fsync boundary must also be
        # refused by public validation, without projection or ledger mutation.
        q = p / "thread-lock"
        q.mkdir()
        qhead, qids, _ = mint(engine, q)
        qgraph = (q / "Approval_Graph.md").read_bytes()
        qsession = (q / "Adjudication_Session.json").read_bytes()
        entered = threading.Event()
        release = threading.Event()
        worker_errors = []
        original_fsync = engine.os.fsync
        def gated_fsync(fd):
            if not entered.is_set():
                entered.set()
                if not release.wait(10):
                    raise OSError("fixture fsync gate timeout")
            return original_fsync(fd)
        engine.os.fsync = gated_fsync
        try:
            db = bundle(engine, "DECISION", qhead["terminal_hash"], None,
                        [event("DECISION", "author", qids[0], af="PENDING", at="APPROVED", inct="REQUIRED")])
            def writer():
                try:
                    append(engine, q, db, qhead)
                except Exception as exc:
                    worker_errors.append(exc)
            thread = threading.Thread(target=writer)
            thread.start()
            assert entered.wait(5), "writer did not reach fsync boundary"
            busy = validate(engine, q, "graph")
            assert busy["verdict"] == "ACTION-REQUIRED"
            assert any(f["code"] == "PROJECT-BUSY" for f in busy["findings"])
            assert (q / "Approval_Graph.md").read_bytes() == qgraph
            assert (q / "Adjudication_Session.json").read_bytes() == qsession
            release.set()
            thread.join(timeout=10)
            assert not thread.is_alive()
            assert not worker_errors, worker_errors
        finally:
            release.set()
            engine.os.fsync = original_fsync

    def h6(p):
        def one(label, replacement, prepare=None):
            q = p / label
            q.mkdir()
            head, ids, _ = mint(engine, q, texts=("A.", "B."))
            if prepare:
                head = prepare(q, head, ids)
            before = (q / "Approval_Events.jsonl").read_bytes()
            expect_error(lambda: engine.revise(str(q), ids[0], {"type": "CLAIM", "text": replacement}, head, STAMP), "EXISTING-IDENTITY")
            assert (q / "Approval_Events.jsonl").read_bytes() == before
        one("self", "A.")
        one("pending", "B.")
        one("rejected", "B.", lambda q, h, ids: decisions(engine, q, h, [ids[1]], approve=False)["head"])
        one("approved", "B.", lambda q, h, ids: decisions(engine, q, h, [ids[1]])["head"])
        def superseded(q, h, ids):
            return engine.revise(str(q), ids[0], {"type": "CLAIM", "text": "C."}, h, STAMP)["head"]
        def superseded_target(q, h, ids):
            return engine.revise(str(q), ids[1], {"type": "CLAIM", "text": "C."}, h, STAMP)["head"]
        one("superseded", "B.", superseded_target)
        # Controlled collisions exercise refusal without claiming a discovered hash collision.
        from unittest.mock import patch
        q = p / "node-collision"; q.mkdir()
        ctx = source(q, "A.\nB.\n")
        qh, qids, _ = mint(engine, q, texts=("A.",), context=ctx)
        qh = decisions(engine, q, qh, qids)["head"]
        before = (q / "Approval_Events.jsonl").read_bytes()
        a = node(engine, "A."); b = node(engine, "B.")
        original_node_id = engine.node_id
        def collide_node(typ, text):
            return qids[0] if text == "B." else original_node_id(typ, text)
        with patch.object(engine, "node_id", side_effect=collide_node):
            alias = node(engine, "  A.\n")
            assert engine.classify_existing_novelty(state(engine, q), [alias])["existing"] == [
                {"record_id": qids[0], "disposition": "AUTHORIZED"}]
            duplicate = bundle(engine, "RECONCILE", qh["terminal_hash"], ctx,
                               [event("MINTED", "reconciliation", qids[0], content=b, at="PENDING", pt="CURRENT")])
            for operation in (
                lambda: engine.classify_existing_novelty(state(engine, q), [b]),
                lambda: engine.replay(ledger(q) + [duplicate]),
                lambda: append(engine, q, duplicate, qh),
                lambda: engine.revise(q, qids[0], {"type": "CLAIM", "text": "B."}, qh, STAMP),
                lambda: engine.reconcile(q, {"nodes": [b], "edges": []}, ctx, qh, STAMP),
                lambda: engine.reconcile(q, {"nodes": [a, b], "edges": []}, ctx, qh, STAMP),
            ):
                expect_error(operation, "ID-COLLISION")
                assert (q / "Approval_Events.jsonl").read_bytes() == before
        q = p / "edge-collision"; q.mkdir()
        ctx = source(q, "A.\nB.\n")
        qh, qids, qeids = mint(engine, q, texts=("A.", "B."), edges=(("SUPPORTS", 0, 1, "—"),), context=ctx)
        qh = decisions(engine, q, qh, qids + qeids)["head"]
        before = (q / "Approval_Events.jsonl").read_bytes()
        existing = edge(engine, "SUPPORTS", qids[0], qids[1])
        reversed_edge = edge(engine, "SUPPORTS", qids[1], qids[0])
        original_edge_id = engine.edge_id
        def collide_edge(typ, src, dst, typing):
            if typ == "SUPPORTS" and src == qids[1] and dst == qids[0]:
                return qeids[0]
            return original_edge_id(typ, src, dst, typing)
        with patch.object(engine, "edge_id", side_effect=collide_edge):
            duplicate = bundle(engine, "RECONCILE", qh["terminal_hash"], ctx,
                               [event("MINTED", "reconciliation", qeids[0], content=reversed_edge, at="PENDING", pt="CURRENT")])
            for operation in (
                lambda: engine.classify_existing_novelty(state(engine, q), [reversed_edge]),
                lambda: engine.replay(ledger(q) + [duplicate]),
                lambda: append(engine, q, duplicate, qh),
                lambda: engine.reconcile(q, {"nodes": [node(engine, "A."), node(engine, "B.")], "edges": [reversed_edge]}, ctx, qh, STAMP),
                lambda: engine.reconcile(q, {"nodes": [node(engine, "A."), node(engine, "B.")], "edges": [existing, reversed_edge]}, ctx, qh, STAMP),
            ):
                expect_error(operation, "ID-COLLISION")
                assert (q / "Approval_Events.jsonl").read_bytes() == before
        for origin_kind in ("revision", "quarantine"):
            q = p / (origin_kind + "-collision"); q.mkdir()
            ctx = source(q, "A.\nCollision.\n")
            qh, qids, _ = mint(engine, q, texts=("A.",), context=ctx)
            novel = node(engine, "Novel.")
            novel_id = engine.node_id("CLAIM", "Novel.")
            if origin_kind == "revision":
                qh = engine.revise(q, qids[0], {"type": "CLAIM", "text": "Novel."}, qh, STAMP)["head"]
            else:
                draft = b"Novel draft.\n"; (q / "Reconstruction_Draft.md").write_bytes(draft)
                novel.update(anchors=[], origin="QUARANTINE (draft v1)", provenance=["QUARANTINE:v1:x-01"])
                qb = bundle(engine, "QUARANTINE", qh["terminal_hash"], {"draft_version": "v1", "draft_sha256": sha(draft)},
                            [event("MINTED", "system", novel_id, content=novel, at="PENDING", pt="CURRENT")])
                qh = append(engine, q, qb, qh)["head"]
            before = (q / "Approval_Events.jsonl").read_bytes()
            original_node_id = engine.node_id
            with patch.object(engine, "node_id", side_effect=lambda typ, text: novel_id if text == "Collision." else original_node_id(typ, text)):
                expect_error(lambda: engine.reconcile(q, {"nodes": [node(engine, "A."), node(engine, "Collision.")], "edges": []}, ctx, qh, STAMP), "ID-COLLISION")
            assert (q / "Approval_Events.jsonl").read_bytes() == before
    def h7(p):
        head, ids, _ = mint(engine, p, texts=("A is present.",))
        st = state(engine, p)
        got = engine.classify_existing_novelty(st, [node(engine, "A is present.")])
        assert not got["new"] and got["existing"][0]["record_id"] == ids[0]
        assert got["existing"][0]["disposition"] == "PENDING"
        fresh = node(engine, "Brand new.")
        classified = engine.classify_existing_novelty(st, [fresh])
        assert classified["existing"] == [] and classified["new"] == [fresh]
        # Repeated novelty preserves every prior disposition and cannot remint it.
        for label, expected in (("pending", "PENDING"), ("rejected", "REJECTED"),
                                ("approved", "AUTHORIZED"), ("orphan", "WITHHELD"),
                                ("superseded", "WITHHELD")):
            q = p / label; q.mkdir()
            qh, qids, _ = mint(engine, q, texts=("Retained identity.",))
            if label == "rejected":
                qh = decisions(engine, q, qh, qids, approve=False)["head"]
            elif label in {"approved", "orphan"}:
                qh = decisions(engine, q, qh, qids, inclusion="OPTIONAL")["head"]
                if label == "orphan":
                    qh = engine.reconcile(q, {"nodes": [], "edges": []}, source(q, "Gone.\n"), qh, STAMP)["head"]
            elif label == "superseded":
                qh = engine.revise(q, qids[0], {"type": "CLAIM", "text": "Replacement."}, qh, STAMP)["head"]
            before = (q / "Approval_Events.jsonl").read_bytes()
            candidate = node(engine, "Retained identity.")
            for _ in range(2):
                classified = engine.classify_existing_novelty(state(engine, q), [candidate])
                assert classified == {"new": [], "existing": [{"record_id": qids[0], "disposition": expected}]}
            draft = b"Draft evidence.\n"; (q / "Reconstruction_Draft.md").write_bytes(draft)
            candidate.update(anchors=[], origin="QUARANTINE (draft v1)", provenance=["QUARANTINE:v1:x-01"])
            context = {"draft_version": "v1", "draft_sha256": sha(draft)}
            duplicate = bundle(engine, "QUARANTINE", qh["terminal_hash"], context,
                               [event("MINTED", "system", qids[0], content=candidate, at="PENDING", pt="CURRENT")])
            expect_error(lambda: append(engine, q, duplicate, qh), "EXISTING-IDENTITY")
            empty = {"shape": "QUARANTINE", "prev_hash": qh["terminal_hash"], "timestamp": STAMP,
                     "context": context, "events": []}
            expect_error(lambda: append(engine, q, empty, qh), "INVALID-BUNDLE")
            assert (q / "Approval_Events.jsonl").read_bytes() == before
        # A valid split reference is accepted as provenance data when its source
        # anchor is present; the parser must still reject malformed split grammar.
        sq = p / "split"
        sq.mkdir()
        sc = source(sq, "Split child.\n")
        split = node(engine, "Split child.")
        split["provenance"] = ["STATE:Argument_State_v1:C1:SPLIT 1/2"]
        srid = engine.node_id(split["type"], split["text"])
        sb = bundle(engine, "MINT", "GENESIS", sc,
                    [event("MINTED", "normalizer", srid, content=split, at="PENDING", pt="CURRENT")])
        append(engine, sq, sb, {"bundle_count": 0, "terminal_hash": "GENESIS"})
        assert validate(engine, sq, "graph")["verdict"] == "PASS"
        bad_split = dict(split); bad_split["text"] = "Split child altered."; bad_split["provenance"] = ["STATE:Argument_State_v1:C1:SPLIT 2/1"]
        split_head = state(engine, sq)["head"]
        bad_rid = engine.node_id(bad_split["type"], bad_split["text"])
        bad_split_bundle = engine.seal_bundle({"shape": "RECONCILE", "prev_hash": split_head["terminal_hash"], "timestamp": STAMP,
                                                "context": sc, "events": [event("MINTED", "reconciliation", bad_rid, content=bad_split, at="PENDING", pt="CURRENT")]})
        expect_error(lambda: append(engine, sq, bad_split_bundle, split_head), "INVALID-PROVENANCE")
        expect_error(lambda: engine.canonical_json({"x": {1: "bad"}}), "UNSUPPORTED-VALUE")
    def h8(p):
        mint(engine, p)
        graph = (p / "Approval_Graph.md").read_bytes()
        session = (p / "Adjudication_Session.json").read_bytes()
        (p / "Approval_Graph.md").unlink()
        (p / "Adjudication_Session.json").unlink()
        result = validate(engine, p, "graph")
        assert result["verdict"] == "PASS"
        assert (p / "Approval_Graph.md").read_bytes() == graph
        assert (p / "Adjudication_Session.json").read_bytes() == session
    def h9(p):
        def one(label, maker):
            q = p / label
            q.mkdir()
            mint(engine, q)
            path = q / "Approval_Events.jsonl"
            before = path.read_bytes()
            suffix = maker(ledger(q)[0])
            path.open("ab").write(suffix)
            result = validate(engine, q, "graph")
            assert result["verdict"] == "PASS" and result["recovered_bytes"] == len(suffix)
            assert path.read_bytes() == before
            assert state(engine, q)["head"]["bundle_count"] == 1
        one("parseable", lambda b: engine.canonical_json(b).encode("utf-8"))
        def partial(b):
            raw = engine.canonical_json(b).encode("utf-8")
            return raw.rsplit(b',"bundle_hash"', 1)[0] + b',"bundle_hash":"deadbeef'
        one("partial-hash", partial)
        # Real publication failure: the ledger is durable, so the error must
        # carry committed=True and later validation must rebuild projections.
        q = p / "replace-failure"
        q.mkdir()
        qhead, qids, _ = mint(engine, q)
        db = bundle(engine, "DECISION", qhead["terminal_hash"], None,
                    [event("DECISION", "author", qids[0], af="PENDING", at="APPROVED", inct="REQUIRED")])
        original_replace = engine.os.replace
        def fail_replace(src, dst):
            raise OSError("fixture publication failure")
        engine.os.replace = fail_replace
        try:
            try:
                append(engine, q, db, qhead)
            except Exception as exc:
                assert isinstance(exc, engine.ApprovalGraphError)
                assert exc.code == "PROJECTION-PUBLISH-FAILED" and exc.committed is True
            else:
                raise AssertionError("publication failure unexpectedly succeeded")
        finally:
            engine.os.replace = original_replace
        assert state(engine, q)["head"]["bundle_count"] == 2
        assert validate(engine, q, "graph")["verdict"] == "PASS"
        # A real fsync failure has unknown append outcome; preserve the bytes
        # and do not claim rollback.
        q = p / "fsync-failure"
        q.mkdir()
        qhead, qids, _ = mint(engine, q)
        before = (q / "Approval_Events.jsonl").read_bytes()
        db = bundle(engine, "DECISION", qhead["terminal_hash"], None,
                    [event("DECISION", "author", qids[0], af="PENDING", at="APPROVED", inct="REQUIRED")])
        original_fsync = engine.os.fsync
        engine.os.fsync = lambda fd: (_ for _ in ()).throw(OSError("fixture fsync failure"))
        try:
            try:
                append(engine, q, db, qhead)
            except Exception as exc:
                assert isinstance(exc, engine.ApprovalGraphError)
                assert exc.code == "APPEND-OUTCOME-UNKNOWN" and exc.committed is None
            else:
                raise AssertionError("fsync failure unexpectedly succeeded")
        finally:
            engine.os.fsync = original_fsync
        uncertain = (q / "Approval_Events.jsonl").read_bytes()
        assert uncertain.startswith(before)
        validate(engine, q, "graph")
        # A short write at the real builtins.open boundary is retried until the
        # complete line is durable; it must not be mistaken for a silent no-op.
        import builtins
        original_open = builtins.open
        q = p / "short-write"
        q.mkdir()
        qhead, qids, _ = mint(engine, q)
        before = (q / "Approval_Events.jsonl").read_bytes()
        db = bundle(engine, "DECISION", qhead["terminal_hash"], None,
                    [event("DECISION", "author", qids[0], af="PENDING", at="APPROVED", inct="REQUIRED")])
        class ShortHandle:
            def __init__(self, fh):
                self.fh = fh
            def write(self, data):
                return self.fh.write(data[:max(1, len(data) // 3)])
            def __getattr__(self, name):
                return getattr(self.fh, name)
            def __enter__(self):
                self.fh.__enter__(); return self
            def __exit__(self, *args):
                return self.fh.__exit__(*args)
        def short_open(file, *args, **kwargs):
            fh = original_open(file, *args, **kwargs)
            mode = args[0] if args else kwargs.get("mode", "r")
            if pathlib.Path(file).name == "Approval_Events.jsonl" and "a" in mode:
                return ShortHandle(fh)
            return fh
        builtins.open = short_open
        try:
            result = append(engine, q, db, qhead)
            assert result["status"] == "COMMITTED"
        finally:
            builtins.open = original_open
        assert (q / "Approval_Events.jsonl").read_bytes().startswith(before)
        assert validate(engine, q, "draft-ready")["verdict"] == "PASS"
        # Releasing the OS lock can fail after a successful append; do not claim rollback.
        from unittest.mock import patch
        q = p / "unlock-failure"; q.mkdir()
        qh, qids, _ = mint(engine, q)
        if os.name == "nt":
            import msvcrt as locking_api
            operation_name, unlock_mode = "locking", locking_api.LK_UNLCK
        else:
            import fcntl as locking_api
            operation_name, unlock_mode = "flock", locking_api.LOCK_UN
        real_lock = getattr(locking_api, operation_name)
        def unlock_failure(fd, mode, *args):
            result = real_lock(fd, mode, *args)
            if mode == unlock_mode:
                raise OSError("injected lock-release failure")
            return result
        with patch.object(locking_api, operation_name, side_effect=unlock_failure):
            exc = expect_error(lambda: decisions(engine, q, qh, qids))
            assert exc.committed is True, (exc.code, exc.committed)
        result = validate(engine, q, "graph")
        assert result["verdict"] == "PASS" and result["head"]["bundle_count"] == qh["bundle_count"] + 1
        # Cleanup must not turn an uncertain append into a claimed refusal.
        q = p / "fsync-and-unlock-failure"; q.mkdir()
        qh, qids, _ = mint(engine, q)
        with patch.object(locking_api, operation_name, side_effect=unlock_failure), \
                patch.object(engine.os, "fsync", side_effect=OSError("injected fsync failure")):
            exc = expect_error(lambda: decisions(engine, q, qh, qids))
            assert exc.committed is None, (exc.code, exc.committed)
        result = validate(engine, q, "graph")
        assert result["verdict"] == "PASS" and result["head"]["bundle_count"] == qh["bundle_count"] + 1
    def h10(p):
        def malformed(q):
            mint(engine, q); path = q / "Approval_Events.jsonl"; before = path.read_bytes()
            path.open("ab").write(b"not-json\n")
            result = validate(engine, q, "graph")
            assert result["verdict"] == "ACTION-REQUIRED" and path.read_bytes() == before + b"not-json\n"
        q = p / "malformed"; q.mkdir(); malformed(q)
        q = p / "bad-hash"; q.mkdir(); mint(engine, q)
        path = q / "Approval_Events.jsonl"; before = path.read_bytes()
        obj = json.loads(before.decode().strip()); obj["bundle_hash"] = "0" * 64
        path.write_text(json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8", newline="")
        result = validate(engine, q, "graph")
        assert result["verdict"] == "ACTION-REQUIRED" and path.read_bytes() != b""
        q = p / "mid-chain"; q.mkdir(); head, ids, _ = mint(engine, q, texts=("A.", "B.")); decisions(engine, q, head, [ids[0]])
        path = q / "Approval_Events.jsonl"; before = path.read_bytes(); lines = before.splitlines(True)
        obj = json.loads(lines[1].decode()); obj["prev_hash"] = "0" * 64
        lines[1] = (json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "\n").encode()
        path.write_bytes(lines[0] + lines[1] + lines[2] if len(lines) > 2 else lines[0] + lines[1])
        path.open("ab").write(b'{"shape":"DECISION"')
        result = validate(engine, q, "graph")
        assert result["verdict"] == "ACTION-REQUIRED"
        assert path.read_bytes() != lines[0] and path.read_bytes().endswith(b'{"shape":"DECISION"')
    def h11(p):
        head, _, _ = mint(engine, p)
        write_receipt(p, engine, head=head)
        path = p / "Approval_Events.jsonl"
        path.write_bytes(b"")
        before = path.read_bytes()
        result = validate(engine, p, "graph")
        assert result["verdict"] == "ACTION-REQUIRED" and path.read_bytes() == before
        assert any("RECEIPT" in f["code"] for f in result["findings"])
    def h12(p):
        head, ids, _ = mint(engine, p)
        head = decisions(engine, p, head, ids, approve=False)["head"]
        head = engine.reconcile(str(p), {"nodes": [], "edges": []}, source(p, "gone\n"), head, STAMP)["head"]
        head = engine.reconcile(str(p), {"nodes": [node(engine, "A is present.")], "edges": []}, source(p, "A is present.\n"), head, STAMP)["head"]
        assert state(engine, p)["records"][ids[0]]["approval"] == "REJECTED"
        bad = bundle(engine, "DECISION", head["terminal_hash"], None,
                     [event("DECISION", "author", ids[0], af="PENDING", at="APPROVED", inct="REQUIRED")])
        expect_error(lambda: append(engine, p, bad, head), "ILLEGAL-TRANSITION")
        un = bundle(engine, "DECISION", head["terminal_hash"], None,
                    [event("UNREJECT", "author", ids[0], af="REJECTED", at="PENDING", reason="author review")])
        head = append(engine, p, un, head)["head"]
        appr = bundle(engine, "DECISION", head["terminal_hash"], None,
                      [event("DECISION", "author", ids[0], af="PENDING", at="APPROVED", inct="REQUIRED")])
        append(engine, p, appr, head)
        assert state(engine, p)["records"][ids[0]]["approval"] == "APPROVED"
    def h13(p):
        head, ids, eids = mint(engine, p, texts=("A.", "B.", "C."), edges=(("SUPPORTS", 0, 1, "—"), ("SUPPORTS", 1, 2, "—")))
        head = decisions(engine, p, head, ids + eids)["head"]
        wrong = bundle(engine, "DECISION", head["terminal_hash"], None,
                       [event("CASCADE", "system", eids[0], af="APPROVED", at="PENDING")])
        before = (p / "Approval_Events.jsonl").read_bytes()
        expect_error(lambda: append(engine, p, wrong, head), "ILLEGAL-TRANSITION")
        assert (p / "Approval_Events.jsonl").read_bytes() == before
        extra = bundle(engine, "DECISION", head["terminal_hash"], None,
                       [event("WITHDRAWAL", "author", ids[0], af="APPROVED", at="PENDING", incf="REQUIRED"),
                        event("CASCADE", "system", eids[0], af="APPROVED", at="PENDING"),
                        event("CASCADE", "system", eids[1], af="APPROVED", at="PENDING")])
        expect_error(lambda: append(engine, p, extra, head), "CASCADE-MISMATCH")
        assert (p / "Approval_Events.jsonl").read_bytes() == before
        ev = [event("WITHDRAWAL", "author", ids[0], af="APPROVED", at="PENDING", incf="REQUIRED"),
              event("CASCADE", "system", eids[0], af="APPROVED", at="PENDING")]
        result = append(engine, p, bundle(engine, "DECISION", head["terminal_hash"], None, ev), head)
        assert result["status"] == "COMMITTED"
        st = state(engine, p)["records"]
        assert st[ids[0]]["approval"] == "PENDING" and st[eids[0]]["approval"] == "PENDING"
        assert st[ids[1]]["approval"] == "APPROVED" and st[ids[2]]["approval"] == "APPROVED"
        assert st[eids[1]]["approval"] == "APPROVED"
    def h14(p):
        head, ids, _ = mint(engine, p)
        head = decisions(engine, p, head, ids)["head"]
        draft = b"Mapped paragraph one.\n\nMapped paragraph two.\n"
        (p / "Reconstruction_Draft.md").write_bytes(draft)
        graph = p / "Approval_Graph.md"
        ident = {"draft_filename": "Reconstruction_Draft.md", "draft_sha256": sha(draft),
                 "graph_sha256": sha(graph.read_bytes()), "bundle_count": head["bundle_count"],
                 "terminal_hash": head["terminal_hash"], "record_ids": sorted(ids), "rejected_ids": []}
        receipt = ["# Reconstruction Receipt", "Identity: " + json.dumps(ident, ensure_ascii=False, separators=(",", ":")),
                   "Verdict: ACTION-REQUIRED", "", "### Passage p-1", "Span: paragraphs 1–2", "Kind: MAPPED",
                   "Realizes: " + ids[0], "", "### Gate Run 1", "Timestamp: " + STAMP,
                   "Judge: fixture-deterministic/1", "Config schema: UNAVAILABLE",
                   "Config: I5-COMPARATOR-UNAVAILABLE", "Prior config refs: NONE", "Author relaxation: NONE",
                   "Verdict: ACTION-REQUIRED", "", "#### Violations", ""]
        receipt_path = p / "Reconstruction_Receipt.md"
        receipt_path.write_text("\n".join(receipt), encoding="utf-8", newline="\n")
        result = validate(engine, p, "acceptance")
        assert result["verdict"] == "ACTION-REQUIRED"
        assert {f["code"] for f in result["findings"]} == {"I5-COMPARATOR-UNAVAILABLE"}, result
        good = receipt_path.read_text(encoding="utf-8")
        # A malformed but otherwise retained envelope must identify the map defect.
        bad_map = good.replace("Realizes: " + ids[0], "Realizes: n-000000000000", 1)
        receipt_path.write_text(bad_map, encoding="utf-8", newline="\n")
        malformed = validate(engine, p, "acceptance")
        assert malformed["verdict"] == "ACTION-REQUIRED"
        assert any(code in {"PASSAGE-REALIZES-INELIGIBLE", "RECEIPT-PASSAGE-MAP"} or "REALIZES" in code for code in (f["code"] for f in malformed["findings"])), malformed
        # Gate-run grammar is independently guarded by its required violations marker.
        receipt_path.write_text(good.replace("#### Violations\n", ""), encoding="utf-8", newline="\n")
        bad_gate = validate(engine, p, "acceptance")
        assert bad_gate["verdict"] == "ACTION-REQUIRED"
        assert any("VIOLATION" in f["code"] or "GATE" in f["code"] for f in bad_gate["findings"]), bad_gate
        # Duplicate Identity lines are a receipt grammar error, not an I5-only case.
        receipt_path.write_text(good.replace("Identity: ", "Identity: {}\nIdentity: ", 1), encoding="utf-8", newline="\n")
        bad_identity = validate(engine, p, "acceptance")
        assert bad_identity["verdict"] == "ACTION-REQUIRED"
        assert any("RECEIPT" in f["code"] for f in bad_identity["findings"]), bad_identity
        q = p / "cli"
        q.mkdir()
        ctx = source(q, "CLI.\n")
        payload = node(engine, "CLI.")
        rid = engine.node_id(payload["type"], payload["text"])
        b = bundle(engine, "MINT", "GENESIS", ctx, [event("MINTED", "normalizer", rid, content=payload, at="PENDING", pt="CURRENT")])
        bf = q / "bundle.jsonl"
        bf.write_bytes(engine.canonical_json(b).encode("utf-8") + b"\n")
        cli = pathlib.Path(engine.__file__).resolve()
        run = subprocess.run([sys.executable, str(cli), str(q), "--append-bundle", str(bf), "--expected-count", "0", "--expected-hash", "GENESIS"], capture_output=True, text=True)
        assert run.returncode == 0, run.stdout + run.stderr
        before = (q / "Approval_Events.jsonl").read_bytes()
        stale = subprocess.run([sys.executable, str(cli), str(q), "--append-bundle", str(bf), "--expected-count", "0", "--expected-hash", "GENESIS"], capture_output=True, text=True)
        assert stale.returncode == 1 and "STALE-HEAD" in stale.stdout
        assert (q / "Approval_Events.jsonl").read_bytes() == before

    def h15(p):
        head, ids, _ = mint(engine, p)
        write_receipt(p, engine, head=head)
        decisions(engine, p, head, ids)
        result = validate(engine, p, "acceptance")
        assert result["verdict"] == "ACTION-REQUIRED"
        assert any("STALE" in f["code"] or "RECEIPT" in f["code"] for f in result["findings"])

    def h16(p):
        mint(engine, p)
        (p / "Reconstruction_Draft.md").write_bytes(b"draft\n")
        result = validate(engine, p, "acceptance")
        assert result["verdict"] == "ACTION-REQUIRED" and any("RECEIPT" in f["code"] for f in result["findings"])

    def h17(p):
        (p / "Approval_Events.jsonl").write_bytes(b"")
        result = validate(engine, p, "graph")
        assert result["verdict"] == "PASS", result
        assert validate(engine, p, "draft-ready")["verdict"] == "ACTION-REQUIRED"

    def h18(p):
        head, ids, _ = mint(engine, p, texts=("A.",))
        head = decisions(engine, p, head, ids, approve=False)["head"]
        v2 = source(p, "B.\n")
        head = engine.reconcile(str(p), {"nodes": [], "edges": []}, v2, head, STAMP)["head"]
        assert validate(engine, p, "graph")["verdict"] == "PASS"
        old_hash = sha(b"A.\n")
        old = p / "Approval_Sources" / f"{old_hash}.utf8"
        assert old.exists()
        old_bytes = old.read_bytes()
        old.unlink()
        result = validate(engine, p, "graph")
        assert result["verdict"] == "ACTION-REQUIRED" and any("SOURCE" in f["code"] for f in result["findings"])
        old.write_bytes(old_bytes + b"tampered")
        result = validate(engine, p, "graph")
        assert result["verdict"] == "ACTION-REQUIRED" and any("SOURCE" in f["code"] for f in result["findings"])
        assert state(engine, p)["records"][ids[0]]["approval"] == "REJECTED"
        q = p / "missing-anchor"
        q.mkdir()
        ctx = source(q, "present.\n")
        bad = node(engine, "present.", quote="absent")
        rid = engine.node_id(bad["type"], bad["text"])
        b = bundle(engine, "MINT", "GENESIS", ctx,
                   [event("MINTED", "normalizer", rid, content=bad, at="PENDING", pt="CURRENT")])
        expect_error(lambda: append(engine, q, b, {"bundle_count": 0, "terminal_hash": "GENESIS"}), "SOURCE-ANCHOR-MISMATCH")
        assert not (q / "Approval_Events.jsonl").exists() or (q / "Approval_Events.jsonl").read_bytes() == b""
        q2 = p / "reconcile-approval"
        q2.mkdir(); h2, ids2, _ = mint(engine, q2)
        bad2 = node(engine, "A is present."); bad2["approval"] = "APPROVED"
        before2 = (q2 / "Approval_Events.jsonl").read_bytes()
        expect_error(lambda: engine.reconcile(str(q2), {"nodes": [bad2], "edges": []}, source(q2, "A is present.\n"), h2, STAMP), "INVALID-MINT-CONTENT")
        assert (q2 / "Approval_Events.jsonl").read_bytes() == before2
        q3 = p / "quarantine-origin"
        q3.mkdir(); h3, ids3, _ = mint(engine, q3)
        draft = b"draft\n"; (q3 / "Reconstruction_Draft.md").write_bytes(draft)
        novel = node(engine, "Novel."); novel["anchors"] = []; novel["origin"] = "QUARANTINE (draft v1)"; novel["provenance"] = ["QUARANTINE:v1:x-01"]
        nid = engine.node_id(novel["type"], novel["text"])
        qb = bundle(engine, "QUARANTINE", h3["terminal_hash"], {"draft_version": "v2", "draft_sha256": sha(draft)},
                    [event("MINTED", "system", nid, content=novel, at="PENDING", pt="CURRENT")])
        before3 = (q3 / "Approval_Events.jsonl").read_bytes()
        expect_error(lambda: engine.replay(ledger(q3) + [qb]), "QUARANTINE-PROVENANCE-MISMATCH")
        expect_error(lambda: append(engine, q3, qb, h3), "QUARANTINE-PROVENANCE-MISMATCH")
        assert (q3 / "Approval_Events.jsonl").read_bytes() == before3
        # Existing custody failures block a later decision, before publication.
        for damage in ("missing", "corrupt"):
            q4 = p / ("prior-custody-" + damage); q4.mkdir()
            h4, ids4, _ = mint(engine, q4, texts=("Historical evidence.",))
            archive = q4 / "Approval_Sources" / (sha(b"Historical evidence.\n") + ".utf8")
            if damage == "missing":
                archive.unlink(); (q4 / "manuscript.md").unlink()
            else:
                archive.write_bytes(b"Wrong historical bytes.")
            before = {name: (q4 / name).read_bytes() for name in
                      ("Approval_Events.jsonl", "Approval_Graph.md", "Adjudication_Session.json")}
            exc = expect_error(lambda: decisions(engine, q4, h4, ids4))
            assert exc.committed is False
            assert before == {name: (q4 / name).read_bytes() for name in before}
        q5 = p / "invalid-utf8-source"; q5.mkdir()
        raw = b"\xff"; (q5 / "manuscript.md").write_bytes(raw)
        ctx = {"source_filename": "manuscript.md", "source_sha256": sha(raw), "argument_state": "Argument_State_v1"}
        payload = node(engine, "Invalid source.")
        rid = engine.node_id("CLAIM", payload["text"])
        invalid = bundle(engine, "MINT", "GENESIS", ctx,
                         [event("MINTED", "normalizer", rid, content=payload, at="PENDING", pt="CURRENT")])
        exc = expect_error(lambda: append(engine, q5, invalid, {"bundle_count": 0, "terminal_hash": "GENESIS"}))
        assert exc.committed is False
        assert not (q5 / "Approval_Events.jsonl").exists()
        # Native read failures are returned as validation findings, with I5 retained.
        from unittest.mock import patch
        real_read = pathlib.Path.read_bytes
        def unreadable_ledger(path):
            if path.name == "Approval_Events.jsonl":
                raise PermissionError("injected ledger read denial")
            return real_read(path)
        with patch.object(pathlib.Path, "read_bytes", unreadable_ledger):
            result = validate(engine, q3, "acceptance")
        assert result["verdict"] == "ACTION-REQUIRED"
        assert {f["code"] for f in result["findings"]} == {"OPERATION-FAILED", "I5-COMPARATOR-UNAVAILABLE"}
        result = validate(engine, p / "absent-project", "acceptance")
        assert result["verdict"] == "ACTION-REQUIRED" and result["head"] is None
        assert {f["code"] for f in result["findings"]} == {"PROJECT-MISSING", "I5-COMPARATOR-UNAVAILABLE"}

    def h19(p):
        # Presentation order: the session cursor sorted the merged node+edge list,
        # so an eligible "e-" id always pre-empted a still-pending "n-" id.
        head, ids, eids = mint(engine, p, texts=("A.", "B.", "C."),
                               edges=(("SUPPORTS", 0, 1, "\u2014"),))
        head = decisions(engine, p, head, [ids[0], ids[1]])["head"]
        session = json.loads((p / "Adjudication_Session.json").read_text(encoding="utf-8"))
        assert session["status"] == "SUSPENDED", session
        assert session["next_record"] == ids[2], (session, ids, eids)
        assert eids[0] < ids[2], "fixture must keep the edge id lexically first"
        # The eligible edge is presented only once no pending node remains.
        decisions(engine, p, head, [ids[2]])
        session = json.loads((p / "Adjudication_Session.json").read_text(encoding="utf-8"))
        assert session["next_record"] == eids[0], session

    def h20(p):
        # LOCK-UNSUPPORTED is raised inside the lock's try block but is not an
        # OSError, so it used to escape without releasing the per-project RLock.
        # The holding thread could not see it (an RLock is reentrant); any other
        # thread then got PROJECT-BUSY forever, masking the real cause.
        head, ids, _ = mint(engine, p)
        saved = (engine.fcntl, engine.msvcrt)
        engine.fcntl = None
        engine.msvcrt = None
        try:
            expect_error(lambda: decisions(engine, p, head, ids), "LOCK-UNSUPPORTED")
        finally:
            engine.fcntl, engine.msvcrt = saved
        # A different thread must still be able to take the lock afterwards.
        outcome = {}
        def worker():
            try:
                outcome["head"] = decisions(engine, p, head, ids)["head"]
            except Exception as exc:  # noqa: BLE001 - recorded, asserted below
                outcome["error"] = err_code(exc)
        t = threading.Thread(target=worker)
        t.start()
        t.join(60)
        assert not t.is_alive(), "second thread blocked on the leaked project lock"
        assert "error" not in outcome, outcome
        assert validate(engine, p, "graph")["verdict"] == "PASS"

    def h21(p):
        # An append advances the replayed state by one bundle instead of replaying
        # the prefix again, and records are copied on first write rather than up
        # front.  After every append, for every bundle shape, the projections it
        # publishes must equal the ones a full replay rebuilds from the ledger.
        def matches_full_replay(head):
            graph = (p / "Approval_Graph.md").read_bytes()
            session = (p / "Adjudication_Session.json").read_bytes()
            assert state(engine, p)["head"] == head, (state(engine, p)["head"], head)
            (p / "Approval_Graph.md").unlink()
            (p / "Adjudication_Session.json").unlink()
            assert validate(engine, p, "graph")["verdict"] == "PASS"
            assert (p / "Approval_Graph.md").read_bytes() == graph
            assert (p / "Adjudication_Session.json").read_bytes() == session

        head, ids, eids = mint(engine, p, texts=("A.", "B.", "C."),
                               edges=(("SUPPORTS", 0, 1, "\u2014"),))
        matches_full_replay(head)
        for rid in (ids[0], ids[1], eids[0], ids[2]):
            head = decisions(engine, p, head, [rid])["head"]
            matches_full_replay(head)
        # RECONCILE appends provenance inside record["content"], so a shallow
        # copy-on-write would leak the mutation into the pre-append state.
        head = engine.reconcile(str(p), {"nodes": [node(engine, "A."), node(engine, "B.")], "edges": []},
                                source(p, "A.\nB.\n"), head, STAMP)["head"]
        matches_full_replay(head)

    for name, fn in [("H1-required-orphan", h1), ("H2-edge-endpoint-eligibility", h2),
                     ("H3-unchanged-edge-no-provenance", h3), ("H4-novel-edge-origin", h4),
                     ("H5-live-lock-active-suffix", h5), ("H6-existing-identity-revision", h6),
                     ("H7-existing-novelty-reuse", h7), ("H8-projection-rebuild", h8),
                     ("H9-torn-tail-recovery", h9), ("H10-committed-corruption-fail-closed", h10),
                     ("H11-receipt-prefix-crossing", h11), ("H12-rejection-stickiness", h12),
                     ("H13-withdrawal-cascade", h13), ("H14-acceptance-envelope", h14),
                     ("H15-stale-receipt-head", h15), ("H16-missing-receipt", h16),
                     ("H17-empty-readiness", h17), ("H18-source-custody", h18),
                     ("H19-session-presentation-order", h19),
                     ("H20-lock-unsupported-release", h20),
                     ("H21-incremental-append-equivalence", h21)]:
        case(name, fn)
    return outcomes


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--engine", type=pathlib.Path, help="absolute path to approval_graph.py")
    args = ap.parse_args(argv)
    if not args.engine:
        ap.error("--engine is required; this fixture never imports a vendored engine")
    engine = load_engine(args.engine.resolve())
    outcomes = run_cases(engine)
    status = "PASS" if all(row["status"] in {"PASS", "DEFERRED"} for row in outcomes) else "FAIL"
    print(json.dumps({"status": status, "cases": outcomes}, ensure_ascii=False, separators=(",", ":")))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
