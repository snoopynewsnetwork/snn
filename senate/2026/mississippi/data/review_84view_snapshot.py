"""Audit the frozen84-packet two-field source ledger without allocating gaps."""
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
SNAP = DATA / 'turnout/qa/milestones/native-2024-84views'
NAMES = {'Ty_Pinkins': 'Ty Pinkins', 'Roger_F_Wicker': 'Roger F. Wicker'}
EXPECTED = {'native_reporting_constituent': 1779, 'source_TOTAL': 84,
            'unused_template_column': 447, 'parallel_native_observation': 11}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def pin(path):
    b = path.read_bytes()
    return {'path': str(path.relative_to(ROOT)), 'bytes': len(b), 'sha256': sha(b)}


def main():
    snapshot = json.loads((SNAP / 'snapshot.json').read_bytes())
    initial = json.loads((SNAP / 'snapshot-initial-counts.json').read_bytes())
    assert snapshot['pins'] == initial['pins']
    assert initial['counts'] == {k: v for k, v in EXPECTED.items() if k != 'parallel_native_observation'}
    assert snapshot['counts'] == EXPECTED
    assert snapshot['source_columns_including_parallel_observations'] == 2321
    assert snapshot['candidate_numeric_or_null_positions'] == 4642
    files = {}
    for p in snapshot['pins']:
        b = (ROOT / p['path']).read_bytes()
        assert (len(b), sha(b)) == (p['bytes'], p['sha256'])
        files[Path(p['path']).name] = b
    ledger = json.loads(files['native-reviewed-2024.json'])
    controls = json.loads(files['native-reviewed-controls.json'])
    rows = list(csv.DictReader(io.StringIO(files['native-candidate-votes-reviewed.csv'].decode(), newline='')))
    units = json.loads(gzip.decompress(files['native-constituents-reviewed.json.gz']))
    acquisition = {r['id']: r for r in json.loads((DATA / 'turnout/source/acquisition.json').read_bytes())}
    links = json.loads((DATA / 'news/county-2024-links.json').read_bytes())['links']
    county_by_url = {unquote(r['url']): r['county_literal'] for r in links}
    primary = json.loads((DATA / 'coordinator-county-primary-review.json').read_bytes())
    counties = {r['county_literal']: r['source_candidates'] for r in primary['full82_descending_order']}
    source_controls = {r['source_id']: r for r in controls['source_view_checks']}
    assert len(ledger['sources']) == len(source_controls) == controls['source_views'] == 84
    positions = {}
    roles = Counter()
    source_checks = []
    preferred = {}
    source_pins = []
    for sid, source in ledger['sources'].items():
        meta = acquisition[sid]
        stored = (ROOT / meta['path']).read_bytes()
        raw = gzip.decompress(stored)
        assert sha(stored) == meta['stored_sha256'] and sha(raw) == meta['raw_sha256'] == source['raw_sha256']
        assert len(stored) < 40000000 and raw.startswith(b'%PDF-')
        source_pins.append(meta)
        county = county_by_url[unquote(meta['url'])].removesuffix(' Updated')
        assert county in counties
        sums = dict.fromkeys(NAMES.values(), 0)
        totals = []
        local_roles = Counter()
        for page in source['pages']:
            for c in page['columns']:
                for box in [c['header_bounds']] + list(c['candidate_bounds'].values()):
                    assert len(box) == 4 and 0 <= box[0] < box[2] <= page['render_size'][0] + 1
                    assert 0 <= box[1] < box[3] <= page['render_size'][1] + 1
                key = (sid, page['page'], c['source_column'])
                assert key not in positions
                positions[key] = (source, page, c)
                roles[c['role']] += 1
                local_roles[c['role']] += 1
                values = {name: c[key] for key, name in NAMES.items()}
                if c['role'] == 'unused_template_column':
                    assert all(v is None for v in values.values())
                else:
                    assert all(type(v) is int and v >= 0 for v in values.values())
                if c['role'] == 'native_reporting_constituent':
                    for name, value in values.items():
                        sums[name] += value
                elif c['role'] == 'source_TOTAL':
                    totals.append(values)
        assert totals == [sums]
        control = source_controls[sid]
        assert control['candidate_sums'] == control['printed_TOTAL_values'] == sums
        assert control['county_primary_controls'] == counties[county]
        delta = {n: sums[n] - counties[county][n] for n in sums}
        assert control['source_minus_county_primary'] == delta
        assert control['county_primary_balance'] == (not any(delta.values()))
        assert control['all_candidate_balances'] is True
        assert control['native_constituents'] == local_roles['native_reporting_constituent']
        assert control['parallel_observations'] == local_roles['parallel_native_observation']
        if any(delta.values()):
            assert source.get('county_control_qualification') == control['county_control_qualification']
            assert (sid, delta) in [
                ('sos-2024-county-tunica', {'Ty Pinkins': -1, 'Roger F. Wicker': 0}),
                ('sos-2024-county-pike', {'Ty Pinkins': -1232, 'Roger F. Wicker': -1486})]
        if sid not in ['sos-2024-county-pike', 'sos-2024-county-coahoma']:
            assert county not in preferred
            preferred[county] = {'source_id': sid, 'native': local_roles['native_reporting_constituent'],
                                 'candidate_sums': sums, 'delta': delta}
        source_checks.append({'source_id': sid, 'county_literal': county,
                              'role_counts': dict(local_roles), 'candidate_sums': sums,
                              'county_primary_controls': counties[county], 'source_minus_county_primary': delta})
    assert roles == EXPECTED and len(positions) == len(units) == 2321 and len(rows) == 4642
    seen = set()
    for unit in units:
        key = (unit['source_id'], unit['source_page'], unit['source_column'])
        assert key in positions and key not in seen
        seen.add(key)
        source, page, c = positions[key]
        assert unit['source_raw_sha256'] == source['raw_sha256']
        assert unit['parent_county_fips'] == source_controls[key[0]]['parent_county_fips']
        assert unit['role'] == c['role'] and unit['label_literal'] == c['label_literal']
        assert unit['printed_native_id'] == c.get('printed_native_id')
        assert unit['header_bounds'] == c['header_bounds'] and unit['candidate_bounds'] == c['candidate_bounds']
        assert unit['candidate_votes'] == {name: c[field] for field, name in NAMES.items()}
        assert unit['render_size'] == page['render_size']
        assert unit['current_2026_identity_or_boundary_approval'] is False
        for field in ['generic_write_in_votes', 'blank', 'undervotes', 'overvotes', 'ballots_cast', 'registration']:
            assert unit[field] is None
    assert seen == set(positions)
    seen = set()
    for row in rows:
        key = (row['source_id'], int(row['source_page']), int(row['source_column']))
        source, page, c = positions[key]
        assert row['candidate'] in NAMES.values()
        full = key + (row['candidate'],)
        assert full not in seen
        seen.add(full)
        assert row['source_raw_sha256'] == source['raw_sha256']
        assert row['parent_county_fips'] == source_controls[key[0]]['parent_county_fips']
        assert row['role'] == c['role'] and row['label_literal'] == c['label_literal']
        assert row['printed_native_id'] == ('' if c.get('printed_native_id') is None else str(c['printed_native_id']))
        value = c[next(k for k, n in NAMES.items() if n == row['candidate'])]
        assert row['votes'] == ('' if value is None else str(value))
    assert len(seen) == 4642 and set(preferred) == set(counties)
    preferred_sums = {n: sum(r['candidate_sums'][n] for r in preferred.values()) for n in NAMES.values()}
    assert sum(r['native'] for r in preferred.values()) == 1736
    assert preferred_sums == {'Ty Pinkins': 451980, 'Roger F. Wicker': 763420}
    assert {n: sum(r[n] for r in counties.values()) for n in NAMES.values()} == {'Ty Pinkins': 451981, 'Roger F. Wicker': 763420}
    kemper = ledger['sources']['sos-2024-county-kemper']
    p6, p7, p8 = kemper['pages']
    assert [p['page'] for p in kemper['pages']] == [6, 7, 8]
    assert len(p6['columns']) == 11
    for parallel, actual in zip(p6['columns'], p7['columns']):
        assert parallel['role'] == 'parallel_native_observation'
        assert actual['role'] == 'native_reporting_constituent'
        for field in ['label_literal', 'Ty_Pinkins', 'Roger_F_Wicker']:
            assert parallel[field] == actual[field]
    lincoln = next(p for p in ledger['sources']['sos-2024-county-lincoln']['pages'] if p['page'] == 3)
    assert next(c for c in lincoln['columns'] if c['source_column'] == 11)['label_literal'] == 'Forrestry'
    frozen60 = DATA / 'turnout/qa/milestones/native-2024-60views/native-reviewed-2024.json'
    old = json.loads(frozen60.read_bytes())
    old_lincoln = next(p for p in old['sources']['sos-2024-county-lincoln']['pages'] if p['page'] == 3)
    assert next(c for c in old_lincoln['columns'] if c['source_column'] == 11)['label_literal'] == 'Forestry'
    out = {
        'status': 'pass_84_source_packet_controls_with_explicit_primary_disagreements_no_allocation',
        'snapshot_manifest': pin(SNAP / 'snapshot.json'), 'initial_count_only_manifest': pin(SNAP / 'snapshot-initial-counts.json'),
        'all_four_asset_pins_unchanged_after_count_metadata_repair': True, 'frozen_file_pins': snapshot['pins'],
        'source_views': 84, 'county_parent_coverage': 82, 'role_counts': dict(roles),
        'full_source_column_objects': len(units), 'CSV_numeric_or_null_candidate_positions': len(rows),
        'source_checks': source_checks, 'original_PDF_source_pins': source_pins,
        'preferred82_sources': preferred, 'preferred82_native_constituents': 1736,
        'preferred82_candidate_sums': preferred_sums,
        'preferred82_source_total': sum(preferred_sums.values()), 'selected_county_primary_total': 1215401,
        'preferred_minus_county_primary': {'Ty Pinkins': -1, 'Roger F. Wicker': 0},
        'nonadditive_alternatives': ['sos-2024-county-coahoma', 'sos-2024-county-pike'],
        'Kemper_parallel_candidate_positions': 22,
        'prior60_source_literal_snapshot': pin(frozen60),
        'box_check_scope': 'Within-render rectangular bounds only; no independent glyph-coverage or accepted-reading-box equivalence is asserted.',
        'scope': 'All84 source hashes/parent links, full2321 source-column objects and4642 two-Senate-field CSV positions agree. Every additive view closes its own printed TOTAL; Tunica and old Pike county differences remain explicit. Kemper PDF6 observations and two old packets are non-additive. Preferred82 sums are1215400, one Pinkins vote below county controls, without imputation. Lincoln literal repair and old60 snapshot remain separately retained. This coordinator source/control audit is not a fresh original-glyph replay. Presidential, generic-write-in/method, historical native and current geographic/reporting gates remain separate.'}
    (DATA / 'coordinator-native-84view-snapshot-review.json').write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({k: out[k] for k in ['status', 'role_counts', 'full_source_column_objects',
          'CSV_numeric_or_null_candidate_positions', 'preferred82_native_constituents', 'preferred82_candidate_sums']}))


if __name__ == '__main__':
    main()
