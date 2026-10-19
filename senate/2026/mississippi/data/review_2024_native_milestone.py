"""Bounded source/role audit of the announced 25-view turnout milestone."""
from pathlib import Path
from collections import Counter
from urllib.parse import unquote
import gzip
import hashlib
import json
import csv
import io

DATA = Path(__file__).resolve().parent
ROOT = DATA.parent
ANNOUNCED = {
    'native-reviewed-2024.json': (576269, '2501822b1b432b8eaeb1257c47b0d002082089ef86281c0dfa7ff4030ab7015f'),
    'native-reviewed-controls.json': (9321, '028a63efe723053fc70d2543982528688f13539987627ab9fe4a5befa0068241'),
    'native-candidate-votes-reviewed.csv': (405864, 'ba1e23e9bc349c7cf946b912195568e48d8c83fdaeb6c0601ba09e47c993653a'),
}
FIELDS = [('Ty_Pinkins', 'Ty Pinkins'), ('Roger_F_Wicker', 'Roger F. Wicker')]


def main():
    frozen_dir = DATA / 'coordinator-qa/native-2024-25views'
    frozen_dir.mkdir(exist_ok=True)
    if not all((frozen_dir / (name + '.gz')).exists() for name in ANNOUNCED):
        # Work is ongoing. Recover the exact announced bytes from the later
        # append-only ledger only if all three announced SHA256 values match.
        current = {name: (DATA / 'turnout' / name).read_bytes() for name in ANNOUNCED}
        source_ledger = json.loads(current['native-reviewed-2024.json'])
        source_ledger['sources'] = dict(list(source_ledger['sources'].items())[:25])
        source_controls = json.loads(current['native-reviewed-controls.json'])
        source_controls.update(source_views=25, native_constituents=553)
        source_controls['source_view_checks'] = source_controls['source_view_checks'][:25]
        reconstructed = {
            'native-reviewed-2024.json': (json.dumps(source_ledger, indent=2) + '\n').encode(),
            'native-reviewed-controls.json': (json.dumps(source_controls, indent=2) + '\n').encode(),
        }
        reader = csv.DictReader(io.StringIO(current['native-candidate-votes-reviewed.csv'].decode(), newline=''))
        stream = io.StringIO(newline='')
        writer = csv.DictWriter(stream, fieldnames=reader.fieldnames)
        writer.writeheader()
        for row in reader:
            if row['source_id'] in source_ledger['sources']:
                writer.writerow(row)
        reconstructed['native-candidate-votes-reviewed.csv'] = stream.getvalue().encode()
        for name, (size, digest) in ANNOUNCED.items():
            b = reconstructed[name]
            assert len(b) == size and hashlib.sha256(b).hexdigest() == digest
            assert (DATA / 'turnout' / name).read_bytes() == current[name]
        for name, b in reconstructed.items():
            (frozen_dir / (name + '.gz')).write_bytes(gzip.compress(b, mtime=0))
        (frozen_dir / 'recovery-provenance.json').write_text(json.dumps({
            'scope': 'The active worker had appended a26th source before coordinator freezing. Selecting the first25 source objects/checks and their complete CSV rows reproduces every announced byte count and SHA256 exactly. This is an exact announced-derivative recovery, not a new original-source observation, repair or count allocation. Subsequent audits read these frozen copies and do not depend on mutable worker aggregates.',
            'input_pins_at_recovery': {name: {'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest()} for name, b in current.items()},
            'exact_expected_output_pins': ANNOUNCED,
        }, indent=2) + '\n')
    inputs = {}
    pins = []
    for filename, (size, digest) in ANNOUNCED.items():
        snapshot = frozen_dir / (filename + '.gz')
        b = gzip.decompress(snapshot.read_bytes())
        assert len(b) == size and hashlib.sha256(b).hexdigest() == digest
        inputs[filename] = b
        stored = snapshot.read_bytes()
        pins.append({'original_worker_path': 'data/turnout/' + filename,
                     'snapshot_path': str(snapshot.relative_to(ROOT)),
                     'original_bytes': size, 'original_sha256': digest,
                     'stored_bytes': len(stored), 'stored_sha256': hashlib.sha256(stored).hexdigest()})
    ledger = json.loads(inputs['native-reviewed-2024.json'])
    controls = json.loads(inputs['native-reviewed-controls.json'])
    assert len(ledger['sources']) == controls['source_views'] == 25
    acquisition = {r['id']: r for r in json.loads((DATA / 'turnout/source/acquisition.json').read_bytes())}
    parent_links = json.loads((DATA / 'news/county-2024-links.json').read_bytes())['links']
    names_by_url = {unquote(r['url']): r['county_literal'] for r in parent_links}
    primary = json.loads((DATA / 'coordinator-county-primary-review.json').read_bytes())
    named_controls = {r['county_literal']: r['source_candidates'] for r in primary['full82_descending_order']}
    milestone_controls = {r['source_id']: r for r in controls['source_view_checks']}
    roles = Counter()
    source_pins = []
    bounds_checked = 0
    counts = []
    for sid, source in ledger['sources'].items():
        meta = acquisition[sid]
        stored = (ROOT / meta['path']).read_bytes()
        raw = gzip.decompress(stored)
        assert hashlib.sha256(raw).hexdigest() == meta['raw_sha256'] == source['raw_sha256']
        assert hashlib.sha256(stored).hexdigest() == meta['stored_sha256']
        county_label = names_by_url[unquote(meta['url'])]
        if sid in ['sos-2024-county-coahoma-updated', 'sos-2024-county-pike-updated']:
            assert county_label.endswith(' Updated')
            county = county_label.removesuffix(' Updated')
        else:
            county = county_label
        expected = named_controls[county]
        sums = {name: 0 for _, name in FIELDS}
        totals = []
        source_natives = 0
        positions = set()
        for page in source['pages']:
            width, height = page['render_size']
            assert page['page'] >= 1
            for column in page['columns']:
                position = (page['page'], column['source_column'])
                assert position not in positions
                positions.add(position)
                role = column['role']
                roles[role] += 1
                values = {name: column[key] for key, name in FIELDS}
                if role == 'native_reporting_constituent':
                    assert column['label_literal'].strip() and column['label_literal'].strip() != 'TOTAL'
                    source_natives += 1
                    for name, value in values.items():
                        assert type(value) is int and value >= 0
                        sums[name] += value
                elif role == 'source_TOTAL':
                    totals.append(values)
                else:
                    assert role == 'unused_template_column'
                    assert all(value is None for value in values.values())
                for bounds in [column.get('header_bounds')] + list(column.get('candidate_bounds', {}).values()):
                    if bounds is None:
                        continue
                    x1, y1, x2, y2 = bounds
                    assert 0 <= x1 < x2 <= width and 0 <= y1 < y2 <= height, (sid, position, bounds, page['render_size'])
                    bounds_checked += 1
        assert totals == [expected] and sums == expected
        witness = milestone_controls[sid]
        assert witness['native_constituents'] == source_natives
        assert witness['candidate_sums'] == witness['county_primary_controls'] == expected
        counts.append({'source_id': sid, 'county_parent_link_label_literal': county_label,
                       'native_constituents': source_natives, 'candidate_sums': sums,
                       'source_pages': [p['page'] for p in source['pages']]})
        source_pins.append(meta)
    assert roles == {'native_reporting_constituent': 553, 'source_TOTAL': 25, 'unused_template_column': 115}
    assert controls['native_constituents'] == 553
    bounded = []
    for name, sid in [('alcorn', 'sos-2024-county-alcorn'), ('coahoma', 'sos-2024-county-coahoma-updated')]:
        p = DATA / ('coordinator-' + name + '-native-review.json')
        b = p.read_bytes()
        manual = json.loads(b)['independent_manual_values']
        source = ledger['sources'][sid]
        for page_index, page in enumerate(source['pages']):
            for ordinal, column in enumerate(page['columns']):
                if column['role'] != 'native_reporting_constituent':
                    continue
                for key, candidate in FIELDS:
                    assert column[key] == manual[candidate][page_index][ordinal]
        bounded.append({'path': str(p.relative_to(ROOT)), 'sha256': hashlib.sha256(b).hexdigest(),
                        'scope': 'Independent coordinator complete-page numeric readings; only two Senate fields are compared to this turnout milestone.'})
    output = {
        'status': 'pass_bounded_25_source_view_structure_hash_controls_no_statewide_acceptance',
        'frozen_announced_milestone_inputs': pins, 'original_source_pins': source_pins,
        'source_views': 25, 'source_pages': sum(len(s['pages']) for s in ledger['sources'].values()),
        'role_counts': dict(roles), 'native_Senate_candidate_cells': 553 * 2,
        'source_TOTAL_candidate_cells': 25 * 2, 'unused_null_candidate_cells': 115 * 2,
        'physical_bound_boxes_checked': bounds_checked,
        'independent_final_county_controls_and_native_sums': counts,
        'bounded_independent_original_reading_pins': bounded,
        'scope': 'The announced files measure553 actual native constituents, superseding the narrative551 count. This audit verifies exact original/source links and hashes, disjoint roles, physical-bound ranges,25 source TOTALs and county sums. It does not claim the coordinator visually reread all25 sources; independent full coordinator cell readings here cover Alcorn and Coahoma only. The two Senate fields do not stand for presidential/method/under/over/blank or complete valid-write-in coverage. Complete statewide native and current-geography gates remain open.',
    }
    (DATA / 'coordinator-native-2024-25view-review.json').write_text(json.dumps(output, indent=2) + '\n')
    print(json.dumps({k:output[k] for k in ['status','source_views','source_pages','role_counts',
          'native_Senate_candidate_cells','physical_bound_boxes_checked']}))


if __name__ == '__main__':
    main()
