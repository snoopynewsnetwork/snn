"""Audit104 publication-bound readings, preserving mixed-vintage disagreements."""
from pathlib import Path
from collections import defaultdict
from html.parser import HTMLParser
from urllib.parse import urljoin, unquote
import csv
import gzip
import hashlib
import io
import json
import re

DATA = Path(__file__).resolve().parent
ROOT = DATA.parent
NAMES = ['Mike Espy', 'Cindy Hyde-Smith', 'Jimmy L. Edwards']
MANUAL = {
    'sos-2020-county-prentiss': {'page': 3, 'TOTAL_column': 5,
        'last_native_labels': ['Thrasher', 'Tuscumbia-New\nCandler', 'West Booneville', 'Wheeler'],
        'rows_native_then_TOTAL': [[146,120,345,158,2694], [316,478,1249,563,7603], [13,17,26,15,227]]},
    'sos-2020-county-prentiss-amended': {'page': 3, 'TOTAL_column': 5,
        'last_native_labels': ['Thrasher', 'Tuscumbia-New\nCandler', 'West Booneville', 'Wheeler'],
        'rows_native_then_TOTAL': [[146,120,348,160,2714], [316,478,1257,568,7651], [13,17,27,15,229]]},
    'sos-2020-county-hancock': {'page': 4, 'TOTAL_column': 4,
        'last_native_labels': ['Waveland East', 'Waveland West', 'West Shoreline Park'],
        'rows_native_then_TOTAL': [[379,408,113,5651], [595,752,249,14537], [25,37,13,573]]}}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def pin(path):
    b = path.read_bytes()
    return {'path': str(path.relative_to(ROOT)), 'bytes': len(b), 'sha256': sha(b)}


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a' and dict(attrs).get('href'):
            self.hrefs.append(dict(attrs)['href'])


def original(meta):
    path = ROOT / meta['path'] if 'path' in meta else DATA / 'news' / meta['asset']
    stored = path.read_bytes()
    assert sha(stored) == meta['stored_sha256'] and len(stored) < 40000000
    raw = gzip.decompress(stored)
    assert sha(raw) == meta['raw_sha256']
    return raw


def snapshot(path):
    target = DATA / 'coordinator-qa' / (path.name + '.gz')
    if not target.exists():
        b = path.read_bytes()
        assert path.read_bytes() == b
        target.write_bytes(gzip.compress(b, mtime=0))
    return gzip.decompress(target.read_bytes()), pin(target)


def main():
    raw, ledger_pin = snapshot(DATA / 'baselines/county-2020-publication-controls.json')
    ledger = json.loads(raw)
    raw_csv, csv_pin = snapshot(DATA / 'baselines/county-2020-publication-candidate-votes.csv')
    flat = list(csv.DictReader(io.StringIO(raw_csv.decode(), newline='')))
    refs = {s['id']: s for s in json.loads((DATA / 'baselines/source/references.json').read_bytes())}
    parent = refs['sos-2020-county-index']
    html = original(parent)
    parser = Links()
    parser.feed(html.decode())
    urls = {unquote(urljoin(parent['final_url'], href)) for href in parser.hrefs}
    expected = {sid for sid in refs if sid.startswith('sos-2020-county-') and sid != 'sos-2020-county-index'}
    readings = {s['source_id']: s for s in ledger['readings']}
    assert set(readings) == expected and len(readings) == 104
    groups = defaultdict(list)
    original_pins, evidence_pins = [], {}
    accepted = 0
    for sid, row in readings.items():
        meta = refs[sid]
        assert unquote(meta['url']) in urls
        assert row['requested_url'] == meta['url'] and row['final_url'] == meta['final_url']
        b = original(meta)
        assert b.startswith(b'%PDF-') and sha(b) == row['raw_sha256'] and len(b) == row['raw_bytes']
        assert row['parent_source_id'] == meta['parent_source_id'] == parent['id']
        assert set(row['candidate_values']) == set(NAMES)
        assert all(type(v) is int and v >= 0 for v in row['candidate_values'].values())
        for n in NAMES:
            assert row['county_csv_difference'][n] == row['candidate_values'][n] - row['county_csv_control'][n]
        input_path = DATA / 'baselines' / row['manual_input']
        assert pin(input_path)['sha256'] == row['manual_input_sha256']
        evidence = DATA / 'baselines' / row['evidence_path']
        evidence_pins[str(evidence.relative_to(ROOT))] = pin(evidence)
        assert evidence_pins[str(evidence.relative_to(ROOT))]['sha256'] == row['evidence_sha256']
        positions = row['original_positions']
        if positions.get('raster_path'):
            raster = ROOT / positions['raster_path']
            assert pin(raster)['sha256'] == positions['raster_sha256']
            evidence_pins[str(raster.relative_to(ROOT))] = pin(raster)
        if row['source_column_accepted'] is not None:
            assert type(row['source_column_accepted']) is int and row['source_column_accepted'] > 0
            accepted += 1
        else:
            assert 'unaccepted' in row['source_column_qualification']
        assert row['source_page'] > 0
        groups[row['county_key']].append(row)
        original_pins.append(meta)
    assert len(groups) == 82 and sum(len(g) == 2 for g in groups.values()) == 22
    assert accepted == 51
    manifest = json.loads((DATA / 'news/manifest.json').read_bytes())
    csv_source = next(s for s in manifest if s['id'] == 'sos-2020-recap-csv')
    candidate_rows = [r for r in csv.DictReader(io.StringIO(original(csv_source).decode('utf-8-sig')))
                      if r['Office'] == 'United States-Senate ']
    assert len(candidate_rows) == 246
    csv_controls = defaultdict(dict)
    aliases = {'Jefferson Davis': 'jeff-davis', 'DeSoto': 'desoto'}
    for r in candidate_rows:
        key = aliases.get(r['County'], re.sub(r'[^a-z0-9]+', '-', r['County'].lower()).strip('-'))
        assert r['Candidate'] not in csv_controls[key]
        csv_controls[key][r['Candidate']] = int(r['County Total'])
    assert csv_controls.keys() == groups.keys()
    before, selected, changes = [], [], []
    for county, rows in groups.items():
        base = next(r for r in rows if r['publication_variant'] == 'original county-index publication')
        after = next((r for r in rows if r['publication_variant'] == 'Amended'), base)
        before.append(base)
        selected.append(after)
        assert after['candidate_values'] == csv_controls[county]
        assert all(r['county_csv_control'] == csv_controls[county] for r in rows)
        if len(rows) == 2:
            changes.append({'county_key': county, 'original_source_id': base['source_id'],
                            'amended_source_id': after['source_id'],
                            'original': base['candidate_values'], 'amended': after['candidate_values'],
                            'delta': {n: after['candidate_values'][n] - base['candidate_values'][n] for n in NAMES}})
    def total(rows):
        return {n: sum(r['candidate_values'][n] for r in rows) for n in NAMES}
    before_sum, selected_sum = total(before), total(selected)
    assert before_sum == {'Mike Espy':578332, 'Cindy Hyde-Smith':709491, 'Jimmy L. Edwards':23150}
    assert selected_sum == {'Mike Espy':578691, 'Cindy Hyde-Smith':709511, 'Jimmy L. Edwards':23152}
    changed = {r['county_key']: r for r in changes if any(r['delta'].values())}
    assert set(changed) == {'adams', 'coahoma', 'prentiss'}
    assert changed['adams']['delta'] == dict(zip(NAMES, [454,0,0]))
    assert changed['coahoma']['delta'] == dict(zip(NAMES, [-115,-28,0]))
    assert changed['prentiss']['delta'] == dict(zip(NAMES, [20,48,2]))
    assert len(flat) == 312
    seen = set()
    for row in flat:
        key = (row['source_id'], row['candidate'])
        assert key not in seen
        seen.add(key)
        target = readings[row['source_id']]
        assert row['candidate'] in NAMES and int(row['votes']) == target['candidate_values'][row['candidate']]
        assert int(row['county_csv_votes']) == target['county_csv_control'][row['candidate']]
        assert int(row['county_csv_difference']) == target['county_csv_difference'][row['candidate']]
        assert row['raw_sha256'] == target['raw_sha256'] and int(row['source_page']) == target['source_page']
        assert row['source_column_accepted'] == ('' if target['source_column_accepted'] is None else str(target['source_column_accepted']))
        assert json.loads(row['original_positions']) == target['original_positions']
    renders = json.loads((DATA / 'coordinator-qa/2020-prentiss-hancock-independent-renders.json').read_bytes())
    for r in renders:
        assert pin(ROOT / r['path'])['sha256'] == r['sha256']
        manual = MANUAL[r['source_id']]
        target = readings[r['source_id']]
        assert manual['page'] == target['source_page']
        assert manual['TOTAL_column'] == target['source_column_accepted']
        assert dict(zip(NAMES, [v[-1] for v in manual['rows_native_then_TOTAL']])) == target['candidate_values']
    assert ledger['controls']['source_publications'] == 104
    assert ledger['controls']['all_original_county_publications_candidate_sum'] == before_sum
    assert ledger['controls']['amended_where_explicit_otherwise_original_candidate_sum'] == selected_sum
    output = {
        'status':'pass_104_source_publication_and_CSV_controls_with_original_state_vintage_disagreement',
        'worker_ledger_snapshot': ledger_pin, 'worker_CSV_snapshot': csv_pin,
        'source_publications':104, 'county_coverage':82, 'amended_alternatives':22,
        'candidate_TOTAL_positions':312, 'independent_raw_CSV_candidate_positions':246,
        'worker_accepted_physical_TOTAL_ordinals':51, 'worker_unaccepted_physical_TOTAL_ordinals':53,
        'original_county_publication_sums':before_sum,
        'original_state_summary':dict(zip(NAMES,[578806,709539,23152])),
        'original_county_minus_original_state':dict(zip(NAMES,[-474,-48,-2])),
        'amended_where_explicit_otherwise_original_sums':selected_sum,
        'all22_publication_comparisons':changes, 'three_changed_county_publications':changed,
        'direct_coordinator_original_readings':MANUAL, 'direct_coordinator_numeric_positions':42,
        'direct_coordinator_TOTAL_positions':9, 'direct_coordinator_renders':renders,
        'parent_source_pin':parent, 'county_original_source_pins':original_pins,
        'CSV_source_pin':csv_source, 'worker_original_evidence_pins':evidence_pins,
        'scope':'All104 actual index-linked original hashes and312 worker-read TOTAL fields are source-bound, CSV-checked and kept as separate publications.51 ordinal acceptances are worker metadata;53 remain proposals, not approved locators. Coordinator directly re-read the complete Prentiss original/amended final pages and Hancock PDF4,42 endpoint native/TOTAL cells including9 TOTALs; earlier independent Adams/Coahoma reviews remain separate. No fresh coordinator visual reading of every one of312 glyphs is claimed. Selected82 publication totals match every CSV county; original county publication sums disagree with the original state summary. Coahoma net matching state change does not establish a sole changed county or common publication vintage. Native sums, all historical/method fields, release chronology and current geography are not approved.'}
    (DATA / 'coordinator-2020-publication-controls-review.json').write_text(json.dumps(output, indent=2) + '\n')
    print(json.dumps({k:output[k] for k in ['status','source_publications','candidate_TOTAL_positions',
        'worker_accepted_physical_TOTAL_ordinals','worker_unaccepted_physical_TOTAL_ordinals','original_county_publication_sums']}))


if __name__ == '__main__':
    main()
