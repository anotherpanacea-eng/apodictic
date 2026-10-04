#!/usr/bin/env python3
"""Invented-prose behavioral controls for Increment 3's deterministic boundary."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import run_cases as fixtures

ROOT = Path(__file__).resolve().parents[3]


def load(path):
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location('reconstruction_draft', path)
    mod = importlib.util.module_from_spec(spec); sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def run(tool):
    e = tool.engine
    context = ('# Argument State\n\n## 1. Context and Classification\n'
               'Form: essay\nGoal: Describe invented lanterns.\nAudience:\n'
               '  Expertise: GENERAL\n  Receptivity: MIXED\n  Consequence context: LOW\n\n'
               '## 2. Propositions\nPrivate context remainder.\n')
    tests = 0
    with tempfile.TemporaryDirectory(prefix='inc3-') as tmp:
        base = Path(tmp)
        def project(name):
            root = base / name; root.mkdir()
            head, ids, edges = fixtures.mint(e, root, texts=('The invented lantern glows.', 'The invented shell rests.'), edges=(('SUPPORTS', 0, 1, '—'),))
            head = fixtures.decisions(e, root, head, ids + edges)['head']
            (root / 'Argument_State.md').write_text(context, encoding='utf-8')
            return root, ids, edges
        def expect(code, fn):
            nonlocal tests
            try:
                fn()
            except e.ApprovalGraphError as exc:
                assert exc.code == code, (exc.code, code)
            else:
                raise AssertionError('expected refusal ' + code)
            tests += 1
        def inputs(root, ids, suffix=''):
            draft = base / ('draft' + root.name + suffix); mapping = base / ('map' + root.name + suffix)
            draft.write_bytes(('Invented fresh prose.' + suffix + '\n').encode())
            mapping.write_text('### Passage p-1\nSpan: paragraphs 1–1\nKind: MAPPED\nRealizes: ' + ', '.join(ids) + '\n', encoding='utf-8')
            return draft, mapping
        def emit(root, snapshot, draft, mapping):
            return tool.emit(root, draft, mapping, snapshot.ledger_count, snapshot.ledger_hash, hashlib.sha256(snapshot.packet_bytes).hexdigest())
        root, ids, edges = project('normal')
        snap = tool.export_snapshot(root); packet = json.loads(snap.packet_bytes)
        assert tuple(packet) == ('context', 'nodes', 'edges', 'style_brief')
        assert tuple(packet['nodes'][0]) == ('ID', 'Type', 'Text', 'Inclusion')
        assert tuple(packet['edges'][0]) == ('ID', 'Type', 'From', 'To', 'Carried typing')
        assert b'Private context' not in snap.packet_bytes and b'provenance' not in snap.packet_bytes and b'source_sha256' not in snap.packet_bytes
        tests += 1
        draft, mapping = inputs(root, ids)
        result = emit(root, snap, draft, mapping)
        assert result['verdict'] == 'ACTION-REQUIRED'
        identity = e._receipt_identity(root / 'Reconstruction_Receipt.md')
        assert identity['draft_sha256'] == hashlib.sha256(draft.read_bytes()).hexdigest()
        assert identity['graph_sha256'] == hashlib.sha256((root / 'Approval_Graph.md').read_bytes()).hexdigest()
        assert identity['record_ids'] == sorted(ids + edges)
        assert {f['code'] for f in result['findings']} == {'SEMANTIC-NOT-RUN', 'I5-COMPARATOR-UNAVAILABLE'}
        findings = e.validate_project(root, 'acceptance')['findings']
        assert [f['code'] for f in findings] == ['I5-COMPARATOR-UNAVAILABLE'], findings
        tests += 1
        old = [(root / name).read_bytes() for name in ('Reconstruction_Draft.md', 'Reconstruction_Receipt.md')]
        draft2, map2 = inputs(root, ids, ' new')
        emit(root, snap, draft2, map2)
        assert [(root / name).read_bytes() for name in ('Reconstruction_Draft_v1.md', 'Reconstruction_Receipt_v1.md')] == old
        tests += 1
        expect('STALE-HEAD', lambda: tool.emit(root, draft, mapping, 0, 'GENESIS', hashlib.sha256(snap.packet_bytes).hexdigest()))
        (root / 'Style_Brief.md').write_text('Use measured cadence.', encoding='utf-8')
        expect('PACKET-STALE', lambda: emit(root, snap, draft, mapping))
        (root / 'Style_Brief.md').unlink()
        (root / 'Argument_State.md').write_text(context.replace('essay', 'letter'), encoding='utf-8')
        expect('PACKET-STALE', lambda: emit(root, snap, draft, mapping))
        (root / 'Argument_State.md').write_text(context, encoding='utf-8')
        # Active structure, not examples/comments, owns context fields and headings.
        malformed = [
            context.replace('Form: essay', '```text\nForm: essay\n```'),
            context.replace('Form: essay', 'Form: essay\nForm:letter'),
            context.replace('Form: essay', '<!--\nForm: essay\n-->'),
            context.replace('Form: essay', '<!--\n```text\n-->\n<!--\nForm: essay\n-->'),
            context.replace('Audience:', 'Audience:invalid'),
        ]
        for hostile_context in malformed:
            (root / 'Argument_State.md').write_text(hostile_context, encoding='utf-8')
            expect('CONTEXT-GRAMMAR', lambda: tool.export_snapshot(root))
        decorated = ('~~~text\n## 1. Decoy heading\nForm: decoy\n~~~\n<!--\n## 1. Another decoy\nForm: hidden\n-->\n' +
                     context.replace('Goal: Describe invented lanterns.', 'Goal: Describe `invented lanterns`.').replace('Form: essay', 'Form: essay\n<!-- Form: decoy -->\n```text\nForm: decoy\n```'))
        (root / 'Argument_State.md').write_text(decorated, encoding='utf-8')
        decorated_packet = json.loads(tool.export_snapshot(root).packet_bytes)
        assert decorated_packet['context']['Goal'] == 'Describe `invented lanterns`.'
        assert decorated_packet['context']['Form'] == 'essay'
        tests += 1
        (root / 'Argument_State.md').write_text(context, encoding='utf-8')
        escaped_audience = context.replace('  Consequence context: LOW\n', '')
        escaped_audience = escaped_audience.replace('\n## 2.', '\nCash-out inventory:\n  Consequence context: HIGH\n\n## 2.')
        (root / 'Argument_State.md').write_text(escaped_audience, encoding='utf-8')
        expect('CONTEXT-GRAMMAR', lambda: tool.export_snapshot(root))
        scoped = context.replace('\n## 2.', '\nCash-out inventory:\n  Form: hostile hidden form\n  Consequence context: HIGH\n\n## 2.')
        (root / 'Argument_State.md').write_text(scoped, encoding='utf-8')
        scoped_packet = json.loads(tool.export_snapshot(root).packet_bytes)
        assert scoped_packet['context']['Audience']['Consequence context'] == 'LOW'
        assert scoped_packet['context']['Form'] == 'essay'
        tests += 1
        (root / 'Argument_State.md').write_text(context, encoding='utf-8')
        for bad in ('', '### Passage p-1\nSpan: paragraphs 1–2\nKind: DE-MINIMIS\n', '### Passage p-1\nSpan: paragraphs 1–1\nKind: MAPPED\nRealizes: ' + ids[0] + '\n', mapping.read_text(encoding='utf-8') * 2):
            mapping.write_text(bad, encoding='utf-8')
            expect('PASSAGE-MAP-INVALID', lambda: emit(root, snap, draft, mapping))
        mapping.write_text('### Passage p-1\nSpan: paragraphs ' + '1' * 4301 + '–1\nKind: MAPPED\nRealizes: ' + ', '.join(ids) + '\n', encoding='utf-8')
        retained = {path: path.read_bytes() for path in (draft, mapping, root / 'Reconstruction_Draft.md', root / 'Reconstruction_Receipt.md')}
        expect('PASSAGE-MAP-INVALID', lambda: emit(root, snap, draft, mapping))
        assert retained == {path: path.read_bytes() for path in retained}
        draft.write_bytes(b'\xff')
        expect('INVALID-UTF8', lambda: emit(root, snap, draft, mapping))
        for bad in (context.replace('Form: essay', 'Form: essay\nForm: letter'), context + '\n## 1. Context and Classification\nForm: other\n', context.replace('Audience:', 'Register: asserted\nAudience:')):
            (root / 'Argument_State.md').write_text(bad, encoding='utf-8')
            expect('CONTEXT-GRAMMAR', lambda: tool.export_snapshot(root))
        (root / 'Argument_State.md').write_text(context.replace('Audience:', 'Register: generative\nHigh-stakes gate: INACTIVE — secret suffix\nAudience:'), encoding='utf-8')
        assert json.loads(tool.export_snapshot(root).packet_bytes)['context']['High-stakes gate'] == 'INACTIVE'
        assert b'secret suffix' not in tool.export_snapshot(root).packet_bytes
        tests += 1
        # Ordinary regular-file custody applies to style and returned inputs.
        style = root / 'Style_Brief.md'
        style.mkdir()
        expect('ARTIFACT-MISSING', lambda: tool.export_snapshot(root))
        style.rmdir()
        style.write_bytes(b'\xff')
        expect('INVALID-UTF8', lambda: tool.export_snapshot(root))
        style.unlink()
        try:
            style.symlink_to(root / 'Argument_State.md')
        except OSError:
            pass  # Windows may withhold symlink creation from the account.
        else:
            expect('LINK-ARTIFACT', lambda: tool.export_snapshot(root))
            style.unlink()
        # Exact archive resolution ignores a newer current context.
        (root / 'Argument_State_v1.md').write_text(context, encoding='utf-8')
        assert json.loads(tool.export_snapshot(root).packet_bytes)['context']['Form'] == 'essay'
        tests += 1
        # Invalid paired-history states preserve every existing byte.
        for defect in ('missing-current', 'missing-archive', 'collision', 'bad-pair', 'bad-map'):
            broken, bids, _ = project('broken-' + defect)
            bs = tool.export_snapshot(broken); bd, bm = inputs(broken, bids)
            emit(broken, bs, bd, bm)
            nd, nm = inputs(broken, bids, ' next')
            if defect == 'missing-current':
                (broken / 'Reconstruction_Draft.md').unlink()
            elif defect == 'missing-archive':
                (broken / 'Reconstruction_Draft_v1.md').write_bytes(bd.read_bytes())
            elif defect == 'collision':
                (broken / 'Reconstruction_Draft_v01.md').write_bytes(b'collision')
            elif defect == 'bad-pair':
                (broken / 'Reconstruction_Draft.md').write_bytes(b'wrong draft')
            else:
                receipt = broken / 'Reconstruction_Receipt.md'
                receipt.write_bytes(receipt.read_bytes().replace(b'Kind: MAPPED', b'Kind: UNKNOWN'))
            preserved = {p.name: p.read_bytes() for p in broken.glob('Reconstruction_*')}
            expect('PAIRED-RECOVERY-REQUIRED', lambda: emit(broken, bs, nd, nm))
            assert preserved == {p.name: p.read_bytes() for p in broken.glob('Reconstruction_*')}
        empty, empty_ids, _ = project('empty-draft')
        es = tool.export_snapshot(empty); ed, em = inputs(empty, empty_ids)
        ed.write_bytes(b' \n\n')
        expect('PASSAGE-MAP-INVALID', lambda: emit(empty, es, ed, em))
        expect('ENGINE-OWNED-INPUT', lambda: tool.emit(empty, empty / 'Argument_State.md', em, es.ledger_count, es.ledger_hash, hashlib.sha256(es.packet_bytes).hexdigest()))
        # H2 endpoint closure and withheld prose boundary.
        root2, ids2, edges2 = project('withheld')
        state = fixtures.state(e, root2)
        ev = fixtures.event('DECISION', 'author', ids2[1], af='APPROVED', at='REJECTED', incf='REQUIRED')
        # Engine requires cascade construction; use its author operation.
        e.adjudicate(root2, {'action': 'reject', 'record_id': ids2[1], 'expected_head': state['head'], 'timestamp': fixtures.STAMP})
        st2 = fixtures.state(e, root2)
        e.adjudicate(root2, {'action': 'reject', 'record_id': edges2[0], 'expected_head': st2['head'], 'timestamp': fixtures.STAMP})
        leaked = tool.export_snapshot(root2).packet_bytes
        assert b'The invented shell rests.' not in leaked and not json.loads(leaked)['edges']
        tests += 1
        # Every interruption retains bytes and restart refuses the ambiguous pair.
        for stop in (2, 4):
            interrupted, iids, _ = project('interrupt' + str(stop))
            ss = tool.export_snapshot(interrupted); d, m = inputs(interrupted, iids)
            emit(interrupted, ss, d, m)
            originals = [(interrupted / n).read_bytes() for n in ('Reconstruction_Draft.md', 'Reconstruction_Receipt.md')]
            d2, m2 = inputs(interrupted, iids, ' changed')
            writer = e._atomic_write; counter = 0
            def fail(path, raw):
                nonlocal counter
                if path.name.startswith('Reconstruction_'):
                    counter += 1
                    writer(path, raw)
                    if counter == stop:
                        raise OSError('invented interruption')
                else:
                    writer(path, raw)
            e._atomic_write = fail
            try:
                emit(interrupted, ss, d2, m2)
            except OSError:
                pass
            finally:
                e._atomic_write = writer
            assert d2.read_bytes() and m2.read_bytes()
            if stop < 4:
                expect('PAIRED-RECOVERY-REQUIRED', lambda: emit(interrupted, ss, d2, m2))
            else:
                assert e._receipt_identity(interrupted / 'Reconstruction_Receipt.md')['draft_sha256'] == hashlib.sha256(d2.read_bytes()).hexdigest()
                tests += 1
            assert (interrupted / 'Reconstruction_Draft_v1.md').read_bytes() == originals[0]
        return tests


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--engine', type=Path, default=ROOT / 'plugins/apodictic/scripts/reconstruction_draft.py')
    args = parser.parse_args()
    print('Increment 3 engine controls passed:', run(load(args.engine.resolve())))
