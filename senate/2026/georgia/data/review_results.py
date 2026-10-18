#!/usr/bin/env python3
"""Coordinator's offline review of originals; imports no worker code."""
from pathlib import Path
import collections
import csv
import datetime
import gzip
import hashlib
import io
import json
import re
import subprocess
import xml.etree.ElementTree as ET
import zipfile

GA = Path(__file__).resolve().parents[1]
ROOT = GA / 'data/results-sources'
digest = lambda b: hashlib.sha256(b).hexdigest()
load = lambda p: json.loads(p.read_text())
lines = lambda p: [json.loads(s) for s in gzip.decompress(p.read_bytes()).decode().splitlines()]
manifest_bytes = (ROOT / 'asset-manifest.json').read_bytes()
manifest = json.loads(manifest_bytes)
for r in manifest['owned']:
    b = (GA / r['path']).read_bytes()
    assert len(b) == r['bytes'] and digest(b) == r['sha256'], r['path']
    assert len(b) < 40_000_000
for r in load(ROOT / 'shared-inputs.json'):
    b = (GA / r['path']).read_bytes()
    assert len(b) == r['stored_bytes'] and digest(b) == r['stored_sha256']
    raw = gzip.decompress(b) if b[:2] == b'\x1f\x8b' else b
    assert digest(raw) == r['raw_sha256']
receipts = {p.stem.removesuffix('.http'): load(p) for p in (ROOT / 'raw').glob('*.http.json')}
assert len(receipts) == 417
def entity(r):
    p = GA / r['shared_path'] if 'shared_path' in r else ROOT / r['path']
    b = p.read_bytes()
    raw = gzip.decompress(b) if b[:2] == b'\x1f\x8b' else b
    assert len(b) == r['stored_bytes'] and digest(b) == r['stored_sha256']
    assert len(raw) == r['raw_bytes'] and digest(raw) == r['raw_sha256']
    return raw
for r in receipts.values():
    assert r['url'] and r['retrieved_at_utc'] and r['completed_at_utc'] and 'redirects' in r
    if r.get('status') is not None:
        entity(r)
assert set(receipts) == {r['id'] for r in load(ROOT / 'requests.json')}

originals = {}
def source(path):
    if path not in originals:
        b = (GA / path).read_bytes()
        originals[path] = json.loads(gzip.decompress(b) if b[:2] == b'\x1f\x8b' else b)
    return originals[path]
def pointer(obj, path):
    for k in path.lstrip('/').split('/'):
        k = k.replace('~1', '/').replace('~0', '~')
        obj = obj[int(k)] if isinstance(obj, list) else obj[k]
    return obj
def english(obj):
    return next(x['text'] for x in obj if x['languageId'] == 'en')

positions = lines(ROOT / 'extracts/source-positions.jsonl.gz')
seen = set()
for r in positions:
    k = (r['source_path'], r['source_pointer'])
    assert k not in seen
    seen.add(k)
    node = pointer(source(k[0]), k[1])
    assert node['voteCount'] == r['votes'] and type(node['voteCount']).__name__ == r['raw_vote_type']
    if r['kind'] == 'TOTAL':
        for a, b in [('id', 'candidate_id'), ('nativeId', 'nativeId'), ('name', 'name'), ('party', 'party'),
                     ('isWriteIn', 'isWriteIn'), ('isQualifiedWriteIn', 'isQualifiedWriteIn'), ('isWinner', 'isWinner')]:
            assert node.get(a) == r[b], (k, a)
    else:
        assert node['groupId'] == r['group_id'] and node['groupName'] == r['group_name']
assert len(positions) == 76_400
controls = lines(ROOT / 'extracts/county-controls.jsonl.gz')
for r in controls:
    obj = source(r['source_path'])
    assert obj['election'] == r['election']
    assert obj['ballotItemWithBreakdown']['id'] == r['response_ballot_id']
    assert obj['jurisdiction']['id'] == r['jurisdiction_id']
assert len(controls) == 795
native = lines(ROOT / 'extracts/native-identities.jsonl.gz')
for r in native:
    obj = source(r['source_path'])
    assert obj['precincts'][r['inventory_ordinal']] == r['inventory_object']
    assert obj['ballotItemWithBreakdown']['breakdownResults'][r['breakdown_ordinal']]['precinct'] == r['breakdown_precinct_object']
    assert obj['voterTurnout'][r['turnout_ordinal']] == r['turnout_object']
assert len(native) == 2701
inventory = list(csv.DictReader((GA / 'data/official-results-sources.csv').open()))
counties = inventory[1:]
assert len(inventory) == 160 and len({r['county_fips'] for r in counties}) == 159
accepted = load(GA / 'data/coordinator-priority-acceptance.json')
assert [r['county_key'] for r in counties[:44]] == accepted['ordered_dispatch_keys']
assert sum(int(r['native_count_2024']) for r in counties) == 2701
assert sum(int(r['native_count_2024']) for r in counties[:44]) == 1938
for r in counties:
    current = json.loads(entity(receipts['current-tenant-' + r['county_fips']]))
    assert current['id'] is None and current['redirectToShortName'] == 'Georgia' and current['elections'] == []
    assert r['current_general_election_id'] == r['current_senate_contest_id'] == r['current_candidate_ids'] == ''
current = json.loads(entity(receipts['fresh-jurisdiction']))
assert len(current['elections']) == 117
assert not any(x['electionDate'] == '2026-11-03' for x in current['elections'])

# Parse OOXML directly by cell address. This does not use the worker's XLSX derivative/parser.
NS = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def workbook(r):
    z = zipfile.ZipFile(io.BytesIO(entity(r)))
    assert z.testzip() is None
    ss = []
    if 'xl/sharedStrings.xml' in z.namelist():
        ss = [''.join(x.itertext()) for x in ET.fromstring(z.read('xl/sharedStrings.xml'))]
    sheets = {}
    for member in z.namelist():
        if re.fullmatch(r'xl/worksheets/sheet\d+\.xml', member):
            rows = []
            for x in ET.fromstring(z.read(member)).findall('.//s:row', NS):
                row = {}
                for c in x:
                    v = c.find('s:v', NS)
                    value = v.text if v is not None else None
                    if c.get('t') == 's' and value is not None:
                        value = ss[int(value)]
                    if c.get('t') == 'inlineStr':
                        value = ''.join(c.find('s:is', NS).itertext())
                    row[re.sub(r'\d+$', '', c.get('r'))] = value
                rows.append((int(x.get('r')), row))
            sheets[member] = rows
    return sheets
exports = load(ROOT / 'extracts/export-controls.json')
assert len(exports) == 6
export_reviews = []
fulton_rows = None
for export in exports:
    sheets = workbook(receipts[export['source_id']])
    for sheet in export['sheets']:
        rows = dict(sheets[sheet['member']])
        for r in sheet['selected_rows']:
            assert rows[r['row']] == r['cells'], (export['source_id'], sheet['member'], r['row'])
    scope = export['scope']
    if scope == 'state':
        obj = source(load(ROOT / 'extracts/state-controls.json')[export['election_key']]['source_path'])
        expected = {english(o['name']): o['voteCount'] for o in obj['ballotItemWithBreakdown']['summaryResults']['ballotOptions']}
        selected = [r for n, r in sheets['xl/worksheets/sheet1.xml'] if r.get('A') == export['office']]
        assert {r['C']: int(r['F']) for r in selected if r['C'] != 'Total Votes'} == expected
        assert next(int(r['F']) for r in selected if r['C'] == 'Total Votes') == sum(expected.values())
        actual = [r for n, r in sheets['xl/worksheets/sheet3.xml'] if r.get('B') == export['office']]
        assert len({r['A'] for r in actual}) == 159
        if export['election_key'] == '2024NovGen':
            assert len(actual) == 954
            assert {r['D'] for r in actual} == set(expected) | {'Ballots Cast', 'Total Votes'}
    else:
        fulton_rows = sheets['xl/worksheets/sheet3.xml']
    export_reviews.append({'id': export['source_id'], 'raw_sha256': receipts[export['source_id']]['raw_sha256'],
                           'selected_rows': sum(len(s['selected_rows']) for s in export['sheets'])})

alt = load(ROOT / 'extracts/fulton-alternative-native-nulls.json')
fulton = source(alt['app_source'])
lookup = {(r['A'], r['D']): (n, int(r['G'])) for n, r in fulton_rows
          if r.get('B') == 'President of the US' and r.get('D') not in ['Ballots Cast', 'Total Votes']}
assert len(lookup) == 1864
known = 0
nulls = []
by_candidate = collections.Counter()
for j, unit in enumerate(fulton['ballotItemWithBreakdown']['breakdownResults']):
    for i, option in enumerate(unit['ballotOptions']):
        n, value = lookup[(english(unit['precinct']['name']), english(option['name']))]
        if option['voteCount'] is None:
            nulls.append((unit['precinct']['id'], option['id'], n, value))
            by_candidate[english(option['name'])] += value
        else:
            assert option['voteCount'] == value
            known += 1
assert known == 1824 and len(nulls) == 40 and sum(x[3] for x in nulls) == 18
assert nulls == [(x['native_GUID'], x['candidate_id'], x['xlsx_row'], x['xlsx_value']) for x in alt['null_cells']]
assert by_candidate == alt['alternative_candidate_sums']

# Fresh extraction of acquired primary PDFs, with bounded content checks and explicit scope.
def pdf_text(id):
    raw = entity(receipts[id])
    assert raw.startswith(b'%PDF-')
    result = subprocess.run(['pdftotext', '-layout', '-', '-'], input=raw, capture_output=True, check=True)
    return result.stdout.decode()
law = pdf_text('sb3ex-signed')
qualified = re.search(r"term 'qualified contest' shall mean a(.*?)Commissioner of Labor\.", law, re.S).group(1)
assert 'United States Senate' not in qualified
assert all(x in law for x in ['Governor', 'Lieutenant Governor', 'Secretary of State', 'Attorney General'])
la = pdf_text('cobb-november-la')
assert 'L&A 11/3/2026' in la and '918' in la and 'Mike Collins' in la and 'Jon Ossoff' in la
walton = pdf_text('local-13297-1-child-0')
assert '0 of 19 (0.00%)' in walton and '58,734' in walton
wi = pdf_text('follow-local-13297-2-38')
assert all(x in wi for x in ['FINAL LIST OF CERTIFIED WRITE-IN CANDIDATES', 'Elbert Arthur Bartell', 'Christina Clement', 'Cassandra Easton'])

assert (ROOT / 'asset-manifest.json').read_bytes() == manifest_bytes
out = {
    'status': 'pass_with_retained_source_gaps',
    'reviewed_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'independence': 'Standalone original JSON/ZIP/OOXML parsing and fresh primary PDF text extraction; imports no worker code.',
    'official_report_sha256': digest((GA / 'official-results.md').read_bytes()),
    'official_manifest_sha256': digest(manifest_bytes),
    'owned_assets': len(manifest['owned']), 'shared_originals': len(load(ROOT / 'shared-inputs.json')),
    'http_receipts': len(receipts), 'source_positions': len(positions), 'county_controls': len(controls),
    'native_identities': len(native), 'authority_inventory': len(inventory), 'priority_counties': 44,
    'priority_native_identities': 1938, 'current_redirect_stubs_excluded': 159,
    'current_elections_list': 117, 'november_count_admissions': 0,
    'independently_parsed_exports': export_reviews,
    'fulton_known_cells': known, 'fulton_distinct_export_numeric_alternatives': len(nulls),
    'fulton_distinct_export_alternative_votes': sum(x[3] for x in nulls),
    'primary_pdf_exclusions': ['Cobb L&A nonzero November test; Walton 0/19 with populated votes; SB3EX mandatory manual provision excludes Senate'],
    'current_writein_names': ['Elbert Arthur Bartell', 'Christina Clement', 'Cassandra Easton'],
    'scope': 'Historical/current-source research, not November feed admission, geometric approval, exact outstanding votes or probability calibration.'
}
(GA / 'data/coordinator-results-review.json').write_text(json.dumps(out, indent=2) + '\n')
print(json.dumps(out, indent=2))
