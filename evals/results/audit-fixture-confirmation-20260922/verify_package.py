"""Verify evidence integrity; this does not validate editorial judgments."""
import argparse
from collections import Counter
import hashlib
import json
import re
import sys
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
REPO = PACKAGE.parents[2]
ANCHOR = 'b51f862df1afba20f24841c9ab1791da225b4b4e113a170a002f5b56e6093b63'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def child(root, name):
    path = (root / name).resolve()
    require(path.is_relative_to(root.resolve()), 'Path escapes evidence root')
    return path


def checked(root, name, expected):
    data = child(root, name).read_bytes()
    require(digest(data) == expected, 'Hash mismatch: ' + name)
    return data


def extract_scores(data):
    """Lossless table-row projection; no category inference or score repair."""
    rows, tables, unparsed = [], [], []
    section, headers = '', None
    for number, line in enumerate(data.decode('utf-8').splitlines(), 1):
        if line.startswith('## '):
            section, headers = line[3:], None
        if not line.startswith('|'):
            continue
        cells = [cell.strip() for cell in line.strip()[1:-1].split('|')]
        if all(re.fullmatch(r':?-+:?', cell) for cell in cells):
            continue
        if len(cells) == 8 and cells[4] == 'Status':
            headers = cells
            tables.append({'section': section, 'line_number': number, 'raw_line': line, 'columns': cells})
            continue
        if headers is None or len(cells) != 8:
            unparsed.append({'line_number': number, 'raw_line': line})
            continue
        packet = re.search(r'p-[a-f0-9]{4}', section)
        if packet is None:
            packet = re.search(r'p-[a-f0-9]{4}', cells[0])
        if packet is None:
            unparsed.append({'line_number': number, 'raw_line': line})
            continue
        rows.append({'packet': packet.group(), 'section': section,
                     'line_number': number, 'raw_line': line,
                     'expectation': cells[0], 'response_evidence': cells[1],
                     'passage_evidence': cells[2], 'subconditions': cells[3],
                     'finding_status': cells[4], 'fixture_agreement': cells[5],
                     'severity_fit_agreement': cells[6], 'canonical_compliance': cells[7]})
    categories = {'found-with-evidence', 'missed', 'unsupported', 'partial', 'not-assessable'}
    categorical = [row for row in rows if row['finding_status'] in categories]
    return {'source_sha256': digest(data),
            'status': 'mechanically-extracted' if not unparsed else 'unparsed-rows-retained',
            'tables': tables, 'rows': rows, 'unparsed_rows': unparsed,
            'categorical_counts': dict(sorted(Counter(row['finding_status'] for row in categorical).items())),
            'excluded_noncanonical_status_rows': [row['line_number'] for row in rows if row['finding_status'] not in categories]}


def check_private_custody(private, package, manifest, packets):
    sealed = json.loads(checked(private, 'sealed-response-manifest.json', manifest['sealed_response_manifest_sha256']))
    census = sealed['census']
    require(sealed['complete'] is True and sealed['sealed_utc'] == manifest['sealed_utc'], 'Private seal state differs')
    require(len(census) == 8 and {row['packet'] for row in census} == packets, 'Private census is incomplete')
    require(len({row['task'] for row in census}) == len({row['response_id'] for row in census}) == 8, 'Private custody identities reused')
    readers = manifest['readers']
    require(len(readers) == 8 and {row['packet'] for row in readers} == packets, 'Public census is incomplete')
    public = {row['packet']: row for row in readers}
    expected_files = {folder + '/' + packet + suffix for packet in packets
                      for folder, suffix in [('bindings', '.json'), ('responses', '.json'), ('raw', '.md')]}
    require(set(sealed['files']) == expected_files, 'Private seal inventory differs')
    data = {name: checked(private, name, wanted) for name, wanted in sealed['files'].items()}
    for row in census:
        packet = row['packet']
        binding = json.loads(data['bindings/' + packet + '.json'])
        response = json.loads(data['responses/' + packet + '.json'])
        raw = data['raw/' + packet + '.md']
        require(response == row, 'Private response envelope differs from census')
        require(binding['packet'] == packet and binding['task'] == row['task'] and binding['role'] == 'reader', 'Private task binding differs')
        require(row['status'] == 'completed' and len(raw) == row['bytes'] and digest(raw) == row['sha256'], 'Private raw response differs from census')
        expected = {key: row[key] for key in ('packet', 'status', 'sha256', 'bytes', 'received_utc')}
        expected.update(task_identity_sha256=digest(row['task'].encode('utf-8')),
                        response_identity_sha256=digest(row['response_id'].encode('utf-8')),
                        runtime=binding['runtime'], registered_utc=binding['registered_utc'])
        require(public[packet] == expected, 'Published reader custody differs from private seal: ' + packet)
        require((package / 'outputs' / (packet + '.md')).read_bytes() == raw, 'Published reader bytes differ from private seal: ' + packet)
    print('OK: all eight private sealed responses, task/response identities, custody metadata and published bytes agree')


def verify(package=PACKAGE, repo=REPO, private=None):
    manifest = json.loads((package / 'RUN-MANIFEST.json').read_bytes())
    require(manifest['preparation_manifest_sha256'] == ANCHOR, 'Preparation anchor changed')
    require(manifest['source_head'] == '66c59bea3091e1e6990aafc3d86418da44e3a414', 'Source head changed')
    rows = manifest['mapping']
    packets = {r['packet'] for r in rows}
    require(len(rows) == len(packets) == 8, 'Expected eight unique packet rows')
    require(sorted(r['mode'] for r in rows) == ['excerpt'] * 2 + ['positive'] * 3 + ['trigger'] * 3,
            'Mode census changed')
    for row in rows:
        source = checked(repo, 'evals/fixtures/' + row['fixture'], row['source_sha256'])
        checked(repo, 'plugins/apodictic/skills/specialized-audits/references/' + row['reference'], row['reference_sha256'])
        match = re.search(rb'(?m)^---(?:\r\n|\n)', source)
        require(match is not None, 'Missing complete source delimiter')
        body = source[match.end():]
        body.decode('utf-8', errors='strict')
        require(match.end() == row['body_offset'] and source[:match.end()].count(b'\n') == row['delimiter_line'], 'Extraction boundary changed')
        require(digest(body) == row['passage_sha256'], 'Passage hash mismatch')
        require(('CRLF' if b'\r\n' in body else 'LF') == row['newline'], 'Newline declaration mismatch')
    print('OK: eight public fixture/reference hashes and byte-preserving extractions')
    if private is not None:
        frozen = json.loads(checked(private, 'manifest.json', ANCHOR))
        require(frozen['mapping'] == rows and frozen['source_head'] == manifest['source_head'], 'Private preparation mapping differs')
        require(frozen['files'] == manifest['frozen_artifact_hashes'], 'Frozen inventory differs')
        for name, wanted in frozen['files'].items():
            checked(private, name, wanted)
        if manifest.get('scorer'):
            scorer = manifest['scorer']
            original = checked(private, 'scorer-raw.md', scorer['original_sha256'])
            lines = original.splitlines(keepends=True)
            first, last = scorer['removed_original_line_range']
            require(digest(b''.join(lines[first - 1:last])) == scorer['removed_bytes_sha256'], 'Removed custody section changed')
            projected = b''.join(lines[:first - 1] + lines[last:])
            require(projected == (package / 'MODEL-SCORECARD.md').read_bytes(), 'Scorecard projection differs')
            print('OK: exact private-original to published-scorecard projection')
        check_private_custody(private, package, manifest, packets)
        print('OK: private preparation inventory, exact frozen packets, template and dispatch-wrapper hashes')
        print('LIMIT: hash verification does not independently reconstruct wrapper execution or establish tool isolation')
    else:
        print('SKIP: exact prompt/template/dispatch-wrapper bytes unavailable without --private-run')
        print('SKIP: private-original scorecard projection and reader-seal verification')
    require(manifest['status'] == 'completed', 'Run pending: sealed responses and scorer evidence not yet packaged')
    readers = manifest['readers']
    require(len(readers) == 8 and {r['packet'] for r in readers} == packets, 'Incomplete reader census')
    require(all(r['status'] == 'completed' for r in readers), 'Invalid or pending response')
    artifacts = manifest['artifacts']
    required = {'outputs/' + packet + '.md' for packet in packets} | {'MODEL-SCORECARD.md', 'SCORES.json'}
    require(set(artifacts) == required, 'Evidence artifact inventory mismatch')
    actual = {p.relative_to(package).as_posix() for p in package.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    require(actual == required | {'RUN-MANIFEST.json', 'COVERAGE.md', 'verify_package.py'}, 'Uninventoried or missing package file')
    for name, wanted in artifacts.items():
        require(bool(checked(package, name, wanted)), 'Empty evidence artifact')
    for row in readers:
        name = 'outputs/' + row['packet'] + '.md'
        require(row['sha256'] == artifacts[name] and child(package, name).stat().st_size == row['bytes'], 'Reader custody mismatch')
    require(manifest['scorer']['sha256'] == artifacts['MODEL-SCORECARD.md'], 'Scorer custody mismatch')
    ledger = json.loads((package / 'SCORES.json').read_bytes())
    raw = (package / 'MODEL-SCORECARD.md').read_bytes()
    require(ledger == extract_scores(raw), 'Score rows, cells, headers or categorical aggregates not conserved')
    require(ledger['status'] == 'mechanically-extracted', 'Score extraction has unparsed rows; inspect retained rows')
    require(bool(ledger['rows']) and {row['packet'] for row in ledger['rows']} == packets, 'Incomplete score packet coverage')
    require(manifest['score_ledger'] == {'row_count': len(ledger['rows']), 'categorical_counts': ledger['categorical_counts'], 'excluded_noncanonical_status_rows': ledger['excluded_noncanonical_status_rows']}, 'Manifest score summary differs')
    print('OK: eight raw reader outputs, projected model scorecard and mechanically conserved score rows')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--private-run', type=Path, help='Optional original private preparation directory; never copied')
    args = parser.parse_args()
    try:
        verify(private=args.private_run)
    except (OSError, UnicodeError, ValueError, KeyError, TypeError, IndexError) as error:
        print('FAILED: ' + str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
