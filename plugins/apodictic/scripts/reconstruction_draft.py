#!/usr/bin/env python3
"""Deterministic packet export and truthful pre-semantic receipt emission."""
import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

import approval_graph as engine
from override_marker import mask_code_spans


@dataclass(frozen=True)
class Snapshot:
    packet_bytes: bytes
    ledger_count: int
    ledger_hash: str


def _read(path):
    engine._reject_linked_components(path, str(path))
    if not path.is_file():
        raise engine._err('ARTIFACT-MISSING', f'regular file required: {path.name}')
    raw = path.read_bytes()
    try:
        raw.decode('utf-8')
    except UnicodeError as exc:
        raise engine._err('INVALID-UTF8', f'strict UTF-8 required: {path.name}') from exc
    return raw


def _prepare(root):
    bundles, _ = engine._read_ledger(root)
    state = engine.replay(bundles)
    findings, _ = engine._prepare_locked(root, state)
    if findings:
        raise engine._err('DRAFT-NOT-READY', json.dumps(findings, ensure_ascii=False))
    return state


def _context_fields(text):
    """Scan active section-1 field lines with root/Audience block ownership.

    The shared Markdown mask owns code syntax. A positional comment mask keeps
    section and field recognition separate from their verbatim inline values.
    """
    source = text; cursor = 0
    while True:
        # Recompute after each comment: fences quoted inside an HTML comment
        # must not hide the next live comment or influence subsequent fields.
        opener = mask_code_spans(source).find('<!--', cursor)
        if opener < 0:
            break
        closer = source.find('-->', opener + 4)
        end = len(source) if closer < 0 else closer + 3
        blank = ''.join('\n' if char == '\n' else ' ' for char in source[opener:end])
        source = source[:opener] + blank + source[end:]
        cursor = end
    active_lines = mask_code_spans(source).split('\n')
    source_lines = source.split('\n')
    root_names = ('Form', 'Goal', 'Register', 'High-stakes gate', 'Audience')
    audience_names = ('Expertise', 'Receptivity', 'Consequence context')
    fields, audience = {}, {}
    section_count = 0; in_section = False; in_audience = False; audience_count = 0
    for active, raw in zip(active_lines, source_lines):
        if active.startswith('## '):
            in_section = bool(re.fullmatch(r'## 1\. \S.*', active))
            if in_section:
                section_count += 1
            in_audience = False
            continue
        if not in_section or not active.strip():
            continue
        indented = active.startswith((' ', '\t'))
        if not indented:
            in_audience = False
        names = audience_names if in_audience and indented else root_names if not indented else ()
        line = active.lstrip(' \t') if indented else active
        original = raw.lstrip(' \t') if indented else raw
        name = next((name for name in names if line == name or any(line.startswith(name + separator) for separator in (':', ' ', '\t'))), None)
        if name is None:
            continue
        if name == 'Audience':
            audience_count += 1
            if audience_count != 1 or original.rstrip(' \t') != 'Audience:':
                raise engine._err('CONTEXT-GRAMMAR', 'duplicate or malformed Audience block')
            in_audience = True
            continue
        target = audience if in_audience else fields
        if name in target or not original.startswith(name + ': '):
            raise engine._err('CONTEXT-GRAMMAR', f'duplicate or malformed {name}')
        value = original[len(name) + 2:].rstrip(' \t')
        if not value.strip() or value != value.lstrip(' \t'):
            raise engine._err('CONTEXT-GRAMMAR', f'empty or malformed {name}')
        target[name] = value
    if section_count != 1 or audience_count != 1:
        raise engine._err('CONTEXT-GRAMMAR', 'exactly one active section 1 and Audience block required')
    return fields, audience


def _context(root, state):
    identity = state['context']['argument_state']
    archives = []
    for path in root.glob('Argument_State_v*.md'):
        if not re.fullmatch(r'Argument_State_v[1-9][0-9]*\.md', path.name):
            raise engine._err('CONTEXT-ARTIFACT', 'malformed state archive name')
        _read(path)
        archives.append(int(path.stem.rsplit('_v', 1)[1]))
    n = int(identity.rsplit('_v', 1)[1])
    current = 1 + max(archives or [0])
    path = engine._inside(root, 'Argument_State.md' if n == current else identity + '.md')
    text = _read(path).decode('utf-8').replace('\r\n', '\n').replace('\r', '\n')
    fields, audience_fields = _context_fields(text)
    def field(name, optional=False, audience_field=False):
        scope = audience_fields if audience_field else fields
        if optional and name not in scope:
            return None
        if name not in scope:
            raise engine._err('CONTEXT-GRAMMAR', f'missing {name}')
        return scope[name]
    context = {'Form': field('Form'), 'Goal': field('Goal'), 'Audience': {
        'Expertise': field('Expertise', audience_field=True), 'Receptivity': field('Receptivity', audience_field=True),
        'Consequence context': field('Consequence context', audience_field=True)}}
    for name, modes in (('Expertise', 'GENERAL|MIXED|EXPERT'), ('Receptivity', 'SYMPATHETIC|MIXED|HOSTILE'), ('Consequence context', 'LOW|MEDIUM|HIGH')):
        if not re.fullmatch(r'(?:' + modes + r')(?: \([^\n]+\))?', context['Audience'][name]):
            raise engine._err('CONTEXT-GRAMMAR', f'malformed Audience {name}')
    register, stakes = field('Register', True), field('High-stakes gate', True)
    if register is not None or stakes is not None:
        match = re.fullmatch(r'(ACTIVE|INACTIVE) — \S.*', stakes or '')
        if register not in {'asserted', 'generative'} or not match:
            raise engine._err('CONTEXT-GRAMMAR', 'invalid modern Register/High-stakes pair')
        context['Register'] = register
        context['High-stakes gate'] = match.group(1)
    return context


def _packet(root, state):
    nodes, edges = [], []
    for rid in sorted(engine.eligible_ids(state)):
        rec = state['records'][rid]; content = rec['content']
        if rec['kind'] == 'node':
            nodes.append({'ID': rid, 'Type': content['type'], 'Text': content['text'], 'Inclusion': rec['inclusion']})
        else:
            edges.append({'ID': rid, 'Type': content['type'], 'From': content['source'], 'To': content['target'], 'Carried typing': content['carried_typing']})
    style = engine._inside(root, 'Style_Brief.md')
    packet = {'context': _context(root, state), 'nodes': nodes, 'edges': edges,
              'style_brief': _read(style).decode('utf-8') if engine._lexists(style) else None}
    return (json.dumps(packet, ensure_ascii=False, separators=(',', ':')) + '\n').encode('utf-8')


def export_snapshot(project):
    root = engine._project_root(project)
    with engine._ProjectLock(root):
        state = _prepare(root)
        return Snapshot(_packet(root, state), state['head']['bundle_count'], state['head']['terminal_hash'])


def _map(raw, draft, state):
    lines = raw.decode('utf-8').replace('\r\n', '\n').replace('\r', '\n').split('\n')
    findings = []; mapped = set(); spans = []; seen = set()
    headers = [(i, engine._STAGE_C_PASSAGE.fullmatch(line)) for i, line in enumerate(lines) if line.startswith('### ')]
    owned = set()
    for pos, (i, match) in enumerate(headers):
        if not match:
            raise engine._err('PASSAGE-GRAMMAR', 'map contains a non-passage block')
        pid = match.group(1)
        if pid in seen:
            findings.append(engine._finding('PASSAGE-ID-DUPLICATE', pid))
        seen.add(pid)
        stop = headers[pos + 1][0] if pos + 1 < len(headers) else len(lines)
        owned.update(range(i, stop))
        fields = engine._stage_c_parse_block_fields(lines, i + 1, stop, ('Span', 'Kind', 'Realizes'), findings, 'PASSAGE', pid, ('Span', 'Kind'))
        engine._stage_c_parse_passage(pid, fields, engine.eligible_ids(state), mapped, spans, findings)
    if any(line.strip() and i not in owned for i, line in enumerate(lines)):
        findings.append(engine._finding('PASSAGE-GRAMMAR', 'unexpected map content'))
    engine._check_passage_coverage(draft, state['records'], mapped, spans, findings)
    if findings:
        raise engine._err('PASSAGE-MAP-INVALID', json.dumps(findings, ensure_ascii=False))
    return '\n'.join(lines).rstrip('\n') + '\n'


def _pairs(root, state):
    inventories = []
    for stem in ('Reconstruction_Draft', 'Reconstruction_Receipt'):
        versions = {}
        for path in root.glob(stem + '_v*.md'):
            match = re.fullmatch(re.escape(stem) + r'_v([1-9][0-9]*)\.md', path.name)
            if not match:
                raise engine._err('PAIRED-RECOVERY-REQUIRED', 'conflicting archive name: ' + path.name)
            _read(path); versions[int(match.group(1))] = path
        inventories.append(versions)
    if inventories[0].keys() != inventories[1].keys():
        raise engine._err('PAIRED-RECOVERY-REQUIRED', 'unpaired archives; preserve all recovery bytes')
    def check(draft, receipt):
        raw = _read(draft); _read(receipt)
        identity = engine._receipt_identity(receipt)
        if hashlib.sha256(raw).hexdigest() != identity['draft_sha256']:
            raise engine._err('PAIRED-RECOVERY-REQUIRED', 'receipt does not bind paired draft: ' + receipt.name)
        prefix = engine.replay(state['bundles'][:identity['bundle_count']])
        findings = []
        engine._stage_c(root, prefix, findings, receipt_path=receipt, draft_path=draft, graph_bytes=engine.project_graph(prefix))
        defects = [f for f in findings if f['code'] not in {'I5-COMPARATOR-UNAVAILABLE', 'OPEN-VIOLATION'}]
        if defects:
            raise engine._err('PAIRED-RECOVERY-REQUIRED', json.dumps(defects, ensure_ascii=False))
    for n in inventories[0]:
        check(inventories[0][n], inventories[1][n])
    draft = engine._inside(root, 'Reconstruction_Draft.md'); receipt = engine._inside(root, 'Reconstruction_Receipt.md')
    if engine._lexists(draft) != engine._lexists(receipt):
        raise engine._err('PAIRED-RECOVERY-REQUIRED', 'current pair has missing member')
    if not engine._lexists(draft):
        if inventories[0]:
            raise engine._err('PAIRED-RECOVERY-REQUIRED', 'archives without current pair')
        return None
    check(draft, receipt)
    n = max(inventories[0] or [0])
    if n and _read(draft) == _read(inventories[0][n]) and _read(receipt) == _read(inventories[1][n]):
        raise engine._err('PAIRED-RECOVERY-REQUIRED', 'current pair repeats greatest archive after interrupted copy')
    return n + 1


def emit(project, draft_file, map_file, expected_count, expected_hash, expected_packet_sha256):
    root = engine._project_root(project)
    inputs = [Path(draft_file).absolute(), Path(map_file).absolute()]
    for path in inputs:
        engine._reject_linked_components(path, str(path))
        if (root / 'Approval_Sources') in path.resolve().parents or (path.parent.resolve() == root and (path.name in {'Approval_Events.jsonl', 'Approval_Graph.md', 'Adjudication_Session.json', 'Style_Brief.md', 'Argument_State.md'} or re.fullmatch(r'(?:Reconstruction_(?:Draft|Receipt)(?:_v.*)?|Argument_State_v.*)\.md', path.name))):
            raise engine._err('ENGINE-OWNED-INPUT', 'returned input must be outside engine-owned artifacts')
    draft, passage = (_read(path) for path in inputs)
    with engine._ProjectLock(root):
        state = _prepare(root)
        engine._head_equal({'bundle_count': expected_count, 'terminal_hash': expected_hash}, state['head'])
        engine._hex(expected_packet_sha256, 'expected_packet_sha256')
        if hashlib.sha256(_packet(root, state)).hexdigest() != expected_packet_sha256:
            raise engine._err('PACKET-STALE', 'context/style changed; generate a fresh packet and draft')
        blocks = _map(passage, draft, state)
        version = _pairs(root, state)
        identity = {'draft_filename': 'Reconstruction_Draft.md', 'draft_sha256': hashlib.sha256(draft).hexdigest(),
                    'graph_sha256': hashlib.sha256(engine.project_graph(state)).hexdigest(), **state['head'],
                    'record_ids': sorted(state['records']), 'rejected_ids': sorted(rid for rid, rec in state['records'].items() if rec['approval'] == 'REJECTED')}
        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        receipt = ('# Reconstruction Receipt\nIdentity: ' + engine.canonical_json(identity) + '\nVerdict: ACTION-REQUIRED\n\n' + blocks +
                   f'\n### Gate Run {version + 1 if version else 1}\nTimestamp: {timestamp}\nJudge: UNAVAILABLE\nConfig schema: UNAVAILABLE\nConfig: I5-COMPARATOR-UNAVAILABLE\nPrior config refs: NONE\nAuthor relaxation: NONE\nVerdict: ACTION-REQUIRED\n\n#### Violations\n').encode('utf-8')
        if version:
            for stem in ('Reconstruction_Draft', 'Reconstruction_Receipt'):
                current = engine._inside(root, stem + '.md'); archive = engine._inside(root, f'{stem}_v{version}.md')
                if engine._lexists(archive):
                    raise engine._err('PAIRED-RECOVERY-REQUIRED', 'archive collision: ' + archive.name)
                raw = _read(current)
                engine._atomic_write(archive, raw)
                if _read(archive) != raw:
                    raise engine._err('PAIRED-RECOVERY-REQUIRED', 'archive copy verification failed')
        engine._atomic_write(engine._inside(root, 'Reconstruction_Draft.md'), draft)
        engine._atomic_write(engine._inside(root, 'Reconstruction_Receipt.md'), receipt)
        return {'verdict': 'ACTION-REQUIRED', 'head': state['head'], 'findings': [
            engine._finding('I5-COMPARATOR-UNAVAILABLE', 'structured gate configuration comparator is unavailable before Increment 4'),
            engine._finding('SEMANTIC-NOT-RUN', 'semantic judging is unavailable before Increment 4')],
            'artifacts': ['Reconstruction_Draft.md', 'Reconstruction_Receipt.md']}


def _self_test():
    """Portable shipped smoke test; check-all runs the repository fixture suite."""
    import tempfile
    with tempfile.TemporaryDirectory(prefix='reconstruction-self-test-') as td:
        base = Path(td); root = base / 'project'; root.mkdir()
        source = root / 'manuscript.md'; source.write_bytes(b'The invented lamp glows.\n')
        context = {'source_filename': 'manuscript.md', 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(), 'argument_state': 'Argument_State_v1'}
        content = {'type': 'CLAIM', 'text': 'The invented lamp glows.', 'anchors': [{'quote': 'The invented lamp glows.', 'location': 'p1'}], 'origin': 'MANUSCRIPT', 'provenance': ['STATE:Argument_State_v1:C1'], 'flags': ['NONE']}
        rid = engine.node_id(content['type'], content['text'])
        event = dict.fromkeys(engine.EVENT_KEYS)
        event.update(event='MINTED', actor='normalizer', record_id=rid, content=content, approval_to='PENDING', presence_to='CURRENT')
        bundle = engine.seal_bundle({'shape': 'MINT', 'prev_hash': 'GENESIS', 'timestamp': '2026-01-01T00:00:00Z', 'context': context, 'events': [event]})
        head = engine.append_bundle(root, bundle, {'bundle_count': 0, 'terminal_hash': 'GENESIS'})['head']
        engine.adjudicate(root, {'action': 'approve', 'record_id': rid, 'expected_head': head, 'timestamp': '2026-01-01T00:00:01Z', 'inclusion': 'REQUIRED'})
        (root / 'Argument_State.md').write_text('## 1. Context and Classification\nForm: essay\nGoal: Explain invented lamps.\nAudience:\n  Expertise: GENERAL\n  Receptivity: MIXED\n  Consequence context: LOW\n', encoding='utf-8')
        snapshot = export_snapshot(root)
        assert json.loads(snapshot.packet_bytes)['nodes'][0]['ID'] == rid
        draft = base / 'returned-draft.md'; mapping = base / 'returned-map.md'
        draft.write_bytes(b'An invented lamp shines.\n')
        mapping.write_text(f'### Passage p-1\nSpan: paragraphs 1–1\nKind: MAPPED\nRealizes: {rid}\n', encoding='utf-8')
        result = emit(root, draft, mapping, snapshot.ledger_count, snapshot.ledger_hash, hashlib.sha256(snapshot.packet_bytes).hexdigest())
        assert result['verdict'] == 'ACTION-REQUIRED'
        assert [f['code'] for f in engine.validate_project(root, 'acceptance')['findings']] == ['I5-COMPARATOR-UNAVAILABLE']
        assert engine._receipt_identity(root / 'Reconstruction_Receipt.md')['draft_sha256'] == hashlib.sha256(draft.read_bytes()).hexdigest()
    print('reconstruction_draft portable self-test: PASS')
    return 0

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project', nargs='?')
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--packet', action='store_true'); mode.add_argument('--emit', action='store_true'); mode.add_argument('--self-test', action='store_true')
    parser.add_argument('--draft-file'); parser.add_argument('--map-file'); parser.add_argument('--expected-count', type=int)
    parser.add_argument('--expected-hash'); parser.add_argument('--expected-packet-sha256')
    args = parser.parse_args(argv)
    if args.self_test:
        return _self_test()
    if not args.project:
        parser.error('PROJECT is required')
    extra = [args.draft_file, args.map_file, args.expected_count, args.expected_hash, args.expected_packet_sha256]
    if args.packet and any(v is not None for v in extra):
        parser.error('--packet does not accept emission options')
    if args.emit and any(v is None for v in extra):
        parser.error('--emit requires all draft/map/head/packet options')
    try:
        if args.packet:
            sys.stdout.buffer.write(export_snapshot(args.project).packet_bytes)
        else:
            print(json.dumps(emit(args.project, *extra), ensure_ascii=False))
        return 0
    except (engine.ApprovalGraphError, OSError, UnicodeError) as exc:
        print(f'{getattr(exc, "code", "OPERATION-FAILED")}: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
