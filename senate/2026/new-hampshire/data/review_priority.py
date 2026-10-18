#!/usr/bin/env python3
"""Independent original-cell conservation and historical dispatch arithmetic."""
from pathlib import Path
import csv
import datetime
import gzip
import hashlib
import io
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile
from urllib.parse import quote

sys.path.insert(0, '/tmp/snn-xls-reading-libs')
import xlrd

ROOT = Path(__file__).resolve().parents[1]
TURN = ROOT / 'data/turnout'
sha = lambda b: hashlib.sha256(b).hexdigest()
load = lambda p: json.loads(p.read_text())
shared = {r['id']: r for r in load(TURN / 'source/shared-originals.json')}
originals = {}
source_hashes = {}
def original(id):
    if id not in originals:
        own = TURN / 'source' / (id + '.json')
        m = load(own) if own.exists() else shared[id]
        p = TURN / m['shared_path'] if 'shared_path' in m else TURN / 'source' / m['body_path']
        b = p.read_bytes()
        assert sha(b) == m['stored_sha256']
        raw = gzip.decompress(b)
        if m.get('http_content_decoding') == 'gzip':
            raw = gzip.decompress(raw)
        expected = m.get('decoded_original_sha256', m.get('original_sha256', m.get('raw_sha256')))
        assert sha(raw) == expected, id
        source_hashes[id] = {'sha256': sha(raw), 'bytes': len(raw), 'stored_sha256': sha(b)}
        originals[id] = raw
    return originals[id]

NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def letters(n):
    s = ''
    while n:
        n, x = divmod(n - 1, 26)
        s = chr(65 + x) + s
    return s
def xml_workbook(raw):
    z = zipfile.ZipFile(io.BytesIO(raw))
    assert z.testzip() is None
    shared_strings = []
    if 'xl/sharedStrings.xml' in z.namelist():
        shared_strings = [''.join(x.itertext()) for x in ET.fromstring(z.read('xl/sharedStrings.xml'))]
    rel = {x.get('Id'): x.get('Target') for x in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
    out = {}
    for s in ET.fromstring(z.read('xl/workbook.xml')).findall('m:sheets/m:sheet', NS):
        id = s.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
        member = rel[id].lstrip('/')
        if not member.startswith('xl/'):
            member = 'xl/' + member
        rows = {}
        for r in ET.fromstring(z.read(member)).findall('.//m:row', NS):
            cells = {}
            for c in r:
                k = re.sub(r'\d+$', '', c.get('r'))
                v = c.find('m:v', NS)
                value = v.text if v is not None else ''
                if c.get('t') == 's':
                    value = shared_strings[int(value)]
                elif c.get('t') == 'inlineStr':
                    value = ''.join(c.find('m:is', NS).itertext())
                elif value and c.get('t') not in ['str', 'e']:
                    value = float(value)
                cells[k] = value
            rows[int(r.get('r'))] = [cells.get(letters(i), '') for i in range(1, 30)]
        out[s.get('name')] = rows
    return out

books = {}
pdf_pages = {}
records = {}
field_checks = 0
for path in sorted((TURN / 'native').glob('*.jsonl.gz')):
    roster = [json.loads(s) for s in gzip.decompress(path.read_bytes()).decode().splitlines()]
    assert len(roster) == 320
    id = roster[0]['source_id']
    raw = original(id)
    if raw.startswith(b'%PDF-'):
        text = subprocess.run(['pdftotext', '-layout', '-', '-'], input=raw, capture_output=True, check=True).stdout.decode()
        pdf_pages[id] = text.split('\f')
    elif raw[:2] == b'PK':
        books[id] = xml_workbook(raw)
    else:
        books[id] = xlrd.open_workbook(file_contents=raw, formatting_info=True)
    for r in roster:
        assert r['source_native_id'] is None
        if r['sheet'] is not None:
            book = books[id]
            if isinstance(book, dict):
                values = book[r['sheet']][r['source_row']]
            else:
                sheet = book.sheet_by_name(r['sheet'])
                values = sheet.row_values(r['source_row'] - 1)
            possible = [i for i, v in enumerate(values) if str(v).strip() == r['native_label'].strip()]
            expected = list(r['raw_fields'].values())
            offsets = list(range(1, len(expected) + 1))
            if 'names-on-checklist' in id:
                headers = [(n, v) for n, v in book[r['sheet']].items()
                           if n < r['source_row'] and all(k in v for k in ['Republican', 'Democratic', 'Undeclared', 'Total'])]
                header = max(headers)[1]
                columns = [header.index(k) for k in ['Republican', 'Democratic', 'Undeclared', 'Total']]
                columns += [header.index(float(k)) for k in range(1, len(expected) - 3)]
                assert [values[c] for c in columns] == expected, (id, r['native_label'], columns)
                offsets = [c - possible[0] for c in columns]
            matches = [i for i in possible if [values[i + j] for j in offsets] == expected]
            assert len(matches) == 1, (id, r['native_label'], values, expected)
            if 'cell_types' in r:
                types = list(sheet.row_types(r['source_row'] - 1))[matches[0] + 1:matches[0] + 1 + len(expected)]
                assert types == r['cell_types']
        else:
            line = pdf_pages[id][r['page'] - 1].splitlines()[r['line'] - 1]
            assert line.strip().startswith(r['native_label'].strip()), (id, r, line)
            after = line.strip()[len(r['native_label'].strip()):].split()
            expected = [str(v) for v in r['raw_fields'].values() if str(v)]
            assert after == expected, (id, r['native_label'], after, expected)
        for k, value in r['fields'].items():
            raw_value = r['raw_fields'][k]
            if isinstance(raw_value, (int, float)):
                assert int(raw_value) == raw_value == value
            elif str(raw_value).strip() in ['', '-', '–', '—']:
                assert value is None
            else:
                assert int(str(raw_value).replace(',', '')) == value
            field_checks += 1
    records[id] = roster
assert len(records) == 23 and sum(map(len, records.values())) == 7360

# Primary leaf controls are derived independently from the original BIFF rows.
pres = records['sos-2024-president-archived-original']
county_fips = {'Belknap': '33001', 'Carroll': '33003', 'Cheshire': '33005', 'Coos': '33007',
               'Grafton': '33009', 'Hillsborough': '33011', 'Merrimack': '33013',
               'Rockingham': '33015', 'Strafford': '33017', 'Sullivan': '33019'}
for r in pres:
    assert r['county_fips'] == county_fips[r['county']]
    r['key'] = 'nh-2024-pres:' + r['county_fips'] + ':' + quote(r['native_label'].strip(), safe='')
    r['votes'] = sum(r['fields'][k] for k in ['harris_walz', 'trump_vance', 'oliver_ter_maat', 'stein_ware', 'generic_write_ins'] if r['fields'][k] is not None)
ordered = sorted(pres, key=lambda r: (-r['votes'], r['county_fips'], r['native_label'].strip()))
assert len({r['key'] for r in ordered}) == 320
assert sum(r['votes'] for r in ordered) == 826189
assert sum(r['votes'] for r in ordered[:15]) == 185659
assert sum(r['votes'] for r in ordered[:142]) == 660378
assert sum(r['votes'] for r in ordered[:143]) == 662624
assert 5 * 660378 < 4 * 826189 <= 5 * 662624
assert ordered[142]['native_label'] == 'Tilton' and ordered[142]['votes'] == 2246
contract_bytes = (TURN / 'priority-set.json').read_bytes()
contract = json.loads(contract_bytes)
assert [r['key'] for r in ordered] == contract['full_ordered_keys']
assert contract['ordered_priority_keys'] == [r['key'] for r in ordered[:143]]
assert contract['remainder_ordered_keys'] == [r['key'] for r in ordered[143:]]
for a, b in zip(ordered, contract['all_units']):
    assert a['key'] == b['geography_key'] and a['native_label'] == b['native_label']
    assert a['source_row'] == b['source_locator']['source_row'] and a['sheet'] == b['source_locator']['sheet']
    assert all(v == b[k] for k, v in a['fields'].items())
assert len(contract['source_native_coverage']) == 23
for family in contract['source_native_coverage']:
    rows = records[family['source_id']]
    assert len(rows) == family['native_rows'] == len(family['constituents']) == 320
    assert sha((TURN / family['path']).read_bytes()) == family['sha256']
    for a, b in zip(rows, family['constituents']):
        assert a['native_label'] == b['native_label'] and a['county'] == b['county']
        assert a['source_locator'] == b['locator']
csv_rows = list(csv.DictReader((ROOT / 'data/county-turnout.csv').open()))
assert len(csv_rows) == 320
assert [r['geography_key'] for r in csv_rows] == contract['full_ordered_keys']
out = {
    'status': 'pass_historical_dispatch_contract_review',
    'reviewed_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'independent_extraction': 'Original BIFF/OOXML cells and fresh PDF page/line text; no worker parser imported.',
    'source_rosters': len(records), 'source_scoped_records': sum(map(len, records.values())),
    'original_field_checks': field_checks, 'source_hashes': source_hashes,
    'ranked_native_rows': 320, 'denominator': 826189, 'top15_votes': 185659,
    'priority_count': 143, 'priority_votes': 662624, 'preceding_votes': 660378,
    'crossing': {'native_label': 'Tilton', 'votes': 2246}, 'remainder_count': 177,
    'contract_sha256': sha(contract_bytes), 'contract_bytes': len(contract_bytes),
    'scope': 'Reported candidate plus generic-write-in volume; blanks/dashes remain null. No current geography, clerk authority, valid named write-in allocation or live feed approval.'
}
target = ROOT / 'data/coordinator-native-contract-review.json'
if target.exists():
    previous = load(target)
    if {k: v for k, v in previous.items() if k != 'reviewed_utc'} == {k: v for k, v in out.items() if k != 'reviewed_utc'}:
        out['reviewed_utc'] = previous['reviewed_utc']
target.write_text(json.dumps(out, indent=2) + '\n')
print(json.dumps({k: v for k, v in out.items() if k != 'source_hashes'}, indent=2))
