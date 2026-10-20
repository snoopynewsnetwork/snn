"""Coordinator direct original county/ED structure and source-vote audit."""
from pathlib import Path
from collections import Counter
import gzip
import hashlib
import json
import re
import subprocess
from review_native_originals import Tables

D = Path(__file__).resolve().parent
S = D.parent
T = D / 'turnout'


def sha(b):
    return hashlib.sha256(b).hexdigest()


def pin(p):
    b = p.read_bytes()
    return dict(path=str(p.relative_to(S)), bytes=len(b), sha256=sha(b))


def main():
    receipt = json.loads((T / 'source/district-structure.receipt.json').read_bytes())
    p = T / 'source' / receipt['body_path']
    stored = p.read_bytes()
    raw = gzip.decompress(stored)
    assert sha(stored) == receipt['stored_sha256'] and len(stored) == receipt['stored_bytes']
    assert sha(raw) == receipt['raw_sha256'] and len(raw) == receipt['raw_bytes'] == 621859
    assert receipt['http']['http_code'] == 200
    layout = subprocess.run(['pdftotext', '-layout', '-', '-'], input=raw, stdout=subprocess.PIPE, check=True).stdout.decode()
    structure = {}
    for line_number, line in enumerate(layout.splitlines(), 1):
        m = re.match(r'^\s*(NEW CASTLE|KENT|SUSSEX)\s+(\d\d)-(\d\d)([12]?)\s+(\d\d)(?:\s|$)', line)
        if m:
            county, rd, ed, foot, rep = m.groups()
            key = 'ElectionDistrict' + rd + ed
            assert key not in structure and rd == rep
            structure[key] = dict(source_key=key, county=county, rd=rd, ed=ed, literal_footnote=foot or None,
                                  original_layout_line=line, original_layout_line_number=line_number)
    assert len(structure) == 537
    worker = json.loads((T / 'extracts/structure-2024.json').read_bytes())
    assert set(worker) == set(structure)
    for k, e in structure.items():
        assert (e['county'], e['rd'], e['ed'], e['literal_footnote']) == (worker[k]['county'], worker[k]['rd'], worker[k]['ed'], worker[k]['footnote'])
    sourcepins = json.loads((D / 'coordinator-original-report-pins.json').read_bytes())
    report = gzip.decompress((D / 'news' / sourcepins['sos-2024-general-report']['asset']).read_bytes())
    parsed = Tables(report.decode('utf-8-sig')).tables
    county_tables = []
    for table in parsed:
        if 'USSenator' not in table['attrs'].get('class', '').split() or not table['rows']:
            continue
        header = [c['text'] for c in table['rows'][0]['cells']]
        if header == ['Candidate', 'Party', 'New Castle', 'Kent', 'Sussex', 'State', 'Percentage']:
            county_tables.append(table)
    assert len(county_tables) == 1
    literal_controls = county_tables[0]
    controls = {}
    for row in literal_controls['rows'][1:]:
        cells = [c['text'] for c in row['cells']]
        for county, v in zip(['NEW CASTLE', 'KENT', 'SUSSEX'], cells[2:5]):
            controls[(county, cells[0])] = int(v.replace(',', ''))
    original = json.loads((D / 'coordinator-native-original-review.json').read_bytes())['contexts']['2024_SEN']
    candidate_sums, county_totals = Counter(), Counter()
    admin_observations = []
    for u in original['full_native_units']:
        e = structure[u['source_key']]
        county_totals[e['county']] += u['votes']
        for r in u['rows']:
            candidate_sums[(e['county'], r['candidate'])] += r['methods']['Total Votes']
        if e['literal_footnote']:
            admin_observations.append(dict(**e, reported_candidate_votes=u['votes']))
    assert dict(candidate_sums) == controls
    assert dict(county_totals) == {'NEW CASTLE': 270005, 'KENT': 86268, 'SUSSEX': 144333}
    assert len(admin_observations) == 3
    visual = [pin(T / 'source/district-structure-05.png'), pin(T / 'source/district-structure-16.png')]
    out = dict(status='pass_original_printed_county_structure_and_native_candidate_controls',
               complete_original=pin(p), raw_original_bytes=len(raw), raw_original_sha256=sha(raw),
               receipt=pin(T / 'source/district-structure.receipt.json'),
               source_county_ED_rows=len(structure), complete_original_structure_rows=structure,
               original_county_candidate_controls=[dict(county=k[0], candidate=k[1], votes=v) for k, v in candidate_sums.items()],
               source_county_candidate_totals=dict(county_totals), original_county_table_start=literal_controls['start'],
               original_primary_Senate_administrative_observations=admin_observations,
               bounded_visual_review=visual,
               visual_scope='Actually viewed complete retained original page5 and16 renders:02-27/02-28 and41-16/41-17 carry distinct superscripts; page16 prints footnote1Title15Ch19section1901(b)(3), footnote2literal42USCsec1973aa-1. No legal-role/current-boundary inference from numbering.',
               qualifications='Actual printed county column supplies source parents, never numeric-range guessing. Header2022through2032/update2/13/2024 and its different through2030note remain distinct. No physical polling site, current reporting identity or polygon join approved.',
               current_geography_approved=False)
    target = D / 'coordinator-structure-original-review.json'
    value = (json.dumps(out, indent=2) + '\n').encode()
    if target.exists():
        assert target.read_bytes() == value
    else:
        target.write_bytes(value)
    print(json.dumps(dict(**pin(target), complete_structure=537, primary_source_native=530, actual_counties=3)))


if __name__ == '__main__':
    main()
