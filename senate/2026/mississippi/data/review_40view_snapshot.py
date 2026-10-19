"""Verify the frozen partial40-view snapshot without implying statewide coverage."""
from pathlib import Path
from collections import Counter
from urllib.parse import unquote
import csv
import gzip
import hashlib
import io
import json

DATA = Path(__file__).resolve().parent
ROOT = DATA.parent


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--views', type=int, choices=[40,60], default=40)
    views = parser.parse_args().views
    native, unused = (985,196) if views == 40 else (1373,305)
    manifest_path = DATA / f'turnout/qa/milestones/native-2024-{views}views/snapshot.json'
    manifest_bytes = manifest_path.read_bytes()
    snapshot = json.loads(manifest_bytes)
    files = {}
    for pin in snapshot['pins']:
        b = (ROOT / pin['path']).read_bytes()
        assert len(b) == pin['bytes'] and hashlib.sha256(b).hexdigest() == pin['sha256']
        files[Path(pin['path']).name] = b
    ledger = json.loads(files['native-reviewed-2024.json'])
    controls = json.loads(files['native-reviewed-controls.json'])
    csv_rows = list(csv.DictReader(io.StringIO(files['native-candidate-votes-reviewed.csv'].decode(), newline='')))
    source_units = json.loads(gzip.decompress(files['native-constituents-reviewed.json.gz']))
    roles = Counter(c['role'] for s in ledger['sources'].values() for p in s['pages'] for c in p['columns'])
    assert dict(roles) == snapshot.get('roles',snapshot.get('counts')) == {
        'native_reporting_constituent':native,'source_TOTAL':views,'unused_template_column':unused}
    assert len(ledger['sources']) == controls['source_views'] == views
    assert len(source_units) == native+views+unused and len(csv_rows) == 2*(native+views+unused)
    positions = {}
    acquisition = {r['id']:r for r in json.loads((DATA/'turnout/source/acquisition.json').read_bytes())}
    links = json.loads((DATA/'news/county-2024-links.json').read_bytes())['links']
    county_by_url = {unquote(r['url']):r['county_literal'] for r in links}
    primary = json.loads((DATA/'coordinator-county-primary-review.json').read_bytes())
    county_controls = {r['county_literal']:r['source_candidates'] for r in primary['full82_descending_order']}
    source_controls = {r['source_id']:r for r in controls['source_view_checks']}
    county_names = set()
    for sid, source in ledger['sources'].items():
        meta = acquisition[sid]
        stored = (ROOT/meta['path']).read_bytes()
        raw = gzip.decompress(stored)
        assert hashlib.sha256(stored).hexdigest() == meta['stored_sha256']
        assert hashlib.sha256(raw).hexdigest() == meta['raw_sha256'] == source['raw_sha256']
        county = county_by_url[unquote(meta['url'])]
        if sid in ['sos-2024-county-coahoma-updated','sos-2024-county-pike-updated']:
            assert county.endswith(' Updated')
            county = county.removesuffix(' Updated')
        county_names.add(county)
        sums = {'Ty Pinkins':0,'Roger F. Wicker':0}
        totals = []
        for page in source['pages']:
            for column in page['columns']:
                for box in [column['header_bounds']]+list(column['candidate_bounds'].values()):
                    assert len(box) == 4
                    assert 0 <= box[0] < box[2] <= page['render_size'][0]+1
                    assert 0 <= box[1] < box[3] <= page['render_size'][1]+1
                key = (sid,page['page'],column['source_column'])
                assert key not in positions
                positions[key] = column
                values = {'Ty Pinkins':column['Ty_Pinkins'],'Roger F. Wicker':column['Roger_F_Wicker']}
                if column['role'] == 'native_reporting_constituent':
                    for candidate,value in values.items():
                        assert type(value) is int and value >= 0
                        sums[candidate] += value
                elif column['role'] == 'source_TOTAL':
                    totals.append(values)
                else:
                    assert all(v is None for v in values.values())
        assert sums == county_controls[county] and totals == [sums]
        assert source_controls[sid]['candidate_sums'] == source_controls[sid]['county_primary_controls'] == sums
    seen = set()
    for row in csv_rows:
        key = (row['source_id'],int(row['source_page']),int(row['source_column']))
        column = positions[key]
        full_key = key+(row['candidate'],)
        assert full_key not in seen
        seen.add(full_key)
        assert row['source_raw_sha256'] == ledger['sources'][row['source_id']]['raw_sha256']
        assert row['label_literal'] == column['label_literal'] and row['role'] == column['role']
        assert row['parent_county_fips'] == source_controls[row['source_id']]['parent_county_fips']
        value = column['Ty_Pinkins' if row['candidate'] == 'Ty Pinkins' else 'Roger_F_Wicker']
        assert row['candidate'] in ['Ty Pinkins','Roger F. Wicker']
        assert row['votes'] == ('' if value is None else str(value))
    top15 = {r['county_literal'] for r in primary['full82_descending_order'][:15]}
    assert top15 <= county_names
    output = {
        'status':f'pass_frozen_{views}view_partial_source_controls_no_statewide_acceptance',
        'snapshot_manifest_pin':{'path':str(manifest_path.relative_to(ROOT)),
            'bytes':len(manifest_bytes),'sha256':hashlib.sha256(manifest_bytes).hexdigest()},
        'frozen_file_pins':snapshot['pins'],'source_views':views,'native_constituents':native,
        'role_counts':dict(roles),'complete_CSV_candidate_positions':len(csv_rows),
        'box_check_scope':'Rectangles are well formed and within the recorded render extent only; this is not glyph-coverage validation or agreement with independently expanded reading boxes.',
        'all_top15_county_source_views_present':True,'covered_county_parent_labels':sorted(county_names),
        'scope':'Original hashes, source parent links, all selected named county controls, source TOTALs, disjoint within-view roles and all CSV numeric/null positions verify. This is not coordinator visual verification of every source grid or a completed independent second extraction. Frozen snapshots stay unchanged; later working metadata or cell-reading revisions require separate evidence. Two Senate candidates only; nine presidential fields, complete statewide source/native agreement and current geographic/reporting approval remain open.'}
    dest = DATA/f'coordinator-native-{views}view-snapshot-review.json'
    if views == 60:
        initial = DATA/'coordinator-native-60view-snapshot-review-initial.json'
        if dest.exists() and not initial.exists():
            initial.write_bytes(dest.read_bytes())
        output['later_original_reading_findings'] = {
            'review_path':'data/coordinator-native-source-exceptions-review.json',
            'Itawamba':'Six independent accepted reading boxes expand or reposition frozen target hints. The44 original-row candidate values agree, including Clay49/Kirkville36; exact accepted-box agreement is not claimed.',
            'Lincoln':'Original PDF3/column11 prints Forrestry versus frozen Forestry. This is an explicit source-literal discrepancy, not an assumed alias. Frozen source files remain unchanged.'}
        if initial.exists():
            b = initial.read_bytes()
            output['initial_bounded_snapshot_audit'] = {'path':str(initial.relative_to(ROOT)),
                'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
    dest.write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps({k:output[k] for k in ['status','source_views','native_constituents',
        'role_counts','complete_CSV_candidate_positions','all_top15_county_source_views_present']}))


if __name__ == '__main__':
    main()
