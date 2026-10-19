"""Attach every preferred 2024 original named-candidate field to the working dispatch.

The two older SEMS publications remain separate, nonadditive source views. This
does not establish 2026 native identities, method fields, or dispatch approval.
"""
import gzip
import json
from collections import Counter, defaultdict

from acquire_sources import OUT, savejson, sha

PRES = ('Kamala D. Harris', 'Chase Oliver', 'Jill Stein', 'Randall Terry',
        'Donald J. Trump', 'Shiva Ayyadurai', 'Claudia De la Cruz',
        'Robert F. Kennedy Jr.', 'Peter Sonski')
SEN = ('Ty Pinkins', 'Roger F. Wicker')
ALTERNATIVES = {'sos-2024-county-coahoma', 'sos-2024-county-pike'}


def build(contract):
    readings = {}
    pins = {}
    filenames = [f'batch{n}-presidential-original-readings.json' for n in range(2, 34)]
    filenames += ['hinds-presidential-original-readings.json',
                  'small-presidential-original-readings.json',
                  'tunica-presidential-original-readings.json',
                  'perry-presidential-original-readings.json',
                  'winston-allfield-original-readings.json']
    for name in filenames:
        path = OUT/name
        body = json.loads(path.read_text())
        sources = body.get('sources', [body])
        if isinstance(sources, dict):
            sources = list(sources.values())
        for source in sources:
            sid = source['source_id']
            assert sid not in pins, sid
            assert len(source['candidate_checks']) >= 9
            assert all(source['candidate_checks'][candidate]['passes'] for candidate in PRES)
            pins[sid] = {'path': f'data/turnout/{name}', 'sha256': sha(path.read_bytes()),
                         'source_raw_sha256': source['source_raw_sha256'],
                         'candidate_checks': {c: source['candidate_checks'][c] for c in PRES}}
            for row in source['rows']:
                if row['candidate'] not in PRES:
                    continue
                key = (sid, row['source_page'], row['source_column'], row['candidate'])
                assert key not in readings, key
                readings[key] = row
    two_path = OUT/'native-allfield-readings.json'
    two = json.loads(two_path.read_text())
    controls = {c['source_id']: c for c in json.loads((OUT/'native-allfield-controls.json').read_text())['checks']}
    for sid in ('sos-2024-county-alcorn', 'sos-2024-county-coahoma-updated'):
        source = two['sources'][sid]
        assert controls[sid]['all11_candidates_reconcile']
        pins[sid] = {'path': 'data/turnout/native-allfield-readings.json',
                     'sha256': sha(two_path.read_bytes()),
                     'source_raw_sha256': source['raw_sha256'],
                     'candidate_checks': {c: {'native_sum': controls[sid]['native_sums'][c],
                                               'printed_TOTAL': controls[sid]['printed_TOTAL_values'][c],
                                               'passes': True} for c in PRES}}
    preferred = [u for u in contract['source_native_constituents'] if u['source_id'] not in ALTERNATIVES]
    assert len(preferred) == 2266 and len(pins) == 82
    assert Counter(u['role'] for u in preferred) == Counter(native_reporting_constituent=1736,
                                                            unused_template_column=437,
                                                            source_TOTAL=82,
                                                            parallel_native_observation=11)
    columns = []
    explicit_unprinted_slots = []
    for u in preferred:
        sid, page, col = u['source_id'], u['source_page'], u['source_column']
        assert pins[sid]['source_raw_sha256'] == u['source_raw_sha256']
        president = {}
        reading_basis = None
        if sid in two['sources']:
            scoped = u.get('separately_scoped_contests', {}).get('2024-president')
            assert scoped and set(scoped['candidate_votes']) == set(PRES)
            president = dict(scoped['candidate_votes'])
            reading_basis = 'complete_original_allfield_ledger_and_existing_embedded_source_column'
        else:
            for candidate in PRES:
                row = readings.get((sid, page, col, candidate))
                if row is None:
                    assert sid in ('sos-2024-county-tunica', 'sos-2024-county-perry')
                    assert u['role'] == 'unused_template_column'
                    president[candidate] = None
                    explicit_unprinted_slots.append((u['key'], candidate))
                    continue
                assert row['role'] == u['role'] and row['label_literal'] == u['label_literal']
                assert row['source_raw_sha256'] == u['source_raw_sha256']
                president[candidate] = row.get('direct_original_value', row.get('direct_original_visual_value'))
            reading_basis = ('direct_original_nine_candidate_ledger_with_explicit_visible_blank_template_slots'
                             if sid in ('sos-2024-county-tunica', 'sos-2024-county-perry')
                             else 'direct_original_nine_candidate_ledger')
            scoped = u.setdefault('separately_scoped_contests', {}).setdefault('2024-president', {})
            assert not scoped.get('candidate_votes') or scoped['candidate_votes'] == president
            scoped.update(candidate_votes=president, raw_sha256=u['source_raw_sha256'],
                          source_reading_path=pins[sid]['path'],
                          source_reading_sha256=pins[sid]['sha256'],
                          generic_write_in_marks=None, ballots=None, blank=None, under=None, over=None,
                          scope='Nine named presidential candidates in this original SEMS source column; missing source fields unavailable, not zero.')
        assert set(president) == set(PRES)
        assert set(u['candidate_votes']) == set(SEN)
        if u['role'] == 'unused_template_column':
            assert all(value is None for value in president.values())
            assert all(value is None for value in u['candidate_votes'].values())
        else:
            assert all(type(value) is int and value >= 0 for value in president.values())
            assert all(type(value) is int and value >= 0 for value in u['candidate_votes'].values())
        columns.append({'key': u['key'], 'source_id': sid, 'source_raw_sha256': u['source_raw_sha256'],
                        'parent_county_fips': u['parent_county_fips'], 'source_page': page,
                        'source_column': col, 'role': u['role'], 'label_literal': u['label_literal'],
                        'Senate_candidate_votes': u['candidate_votes'],
                        'president_candidate_votes': president,
                        'presidential_original_reading_basis': reading_basis,
                        'presidential_original_reading_path': pins[sid]['path'],
                        'presidential_original_reading_sha256': pins[sid]['sha256']})
    assert len(columns) == len({x['key'] for x in columns}) == 2266
    assert len(explicit_unprinted_slots) == 126
    assert Counter(key.split(':')[1] for key, _ in explicit_unprinted_slots) == Counter({
        'sos-2024-county-tunica': 81, 'sos-2024-county-perry': 45})
    source_checks = []
    by_source = defaultdict(list)
    for column in columns:
        by_source[column['source_id']].append(column)
    for sid, units in sorted(by_source.items()):
        totals = [u for u in units if u['role'] == 'source_TOTAL']
        assert len(totals) == 1, sid
        native = [u for u in units if u['role'] == 'native_reporting_constituent']
        for candidate in PRES:
            actual = sum(u['president_candidate_votes'][candidate] for u in native)
            expected = pins[sid]['candidate_checks'][candidate]['native_sum']
            printed = totals[0]['president_candidate_votes'][candidate]
            assert actual == printed == expected, (sid, candidate, actual, printed, expected)
        source_checks.append({'source_id': sid, 'native_count': len(native),
                              'all_nine_native_sums_equal_printed_TOTAL_and_original_control': True})
    native_pres = sum(sum(u['president_candidate_votes'].values()) for u in columns
                      if u['role'] == 'native_reporting_constituent')
    assert native_pres == 1228007
    doc = {'schema_version': 1,
           'scope': '2024 preferred82 SEMS source columns only. Two old county publication alternatives nonadditive; no 2026 ID/geometry or method allocation.',
           'source_views': 82, 'source_columns': 2266, 'native_constituents': 1736,
           'Senate_candidate_fields': 4532, 'presidential_candidate_fields': 20394,
           'presidential_native_named_vote_sum': native_pres,
           'signed_presidential_named_vote_sum': 1228008,
           'Tunica_Harris_source_minus_signed': -1,
           'explicit_unprinted_template_positions_absent_from_two_older_direct_ledgers': 126,
           'explicit_unprinted_template_positions_by_source': {'sos-2024-county-tunica': 81,
                                                                 'sos-2024-county-perry': 45},
           'original_reading_pins': pins, 'source_checks': source_checks, 'columns': columns}
    raw = (json.dumps(doc, separators=(',', ':'), ensure_ascii=False, sort_keys=True)+'\n').encode()
    stored = gzip.compress(raw, compresslevel=9, mtime=0)
    path = OUT/'source/2024-preferred-all11-source-fields-v1.json.gz'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(stored)
    assert path.stat().st_size < 40_000_000
    contract['preferred_2024_all11_source_fields_dependency'] = {
        'path': 'data/turnout/source/2024-preferred-all11-source-fields-v1.json.gz',
        'stored_sha256': sha(stored), 'stored_bytes': len(stored),
        'raw_sha256': sha(raw), 'raw_bytes': len(raw),
        'source_views': 82, 'source_columns': 2266, 'native_constituents': 1736,
        'Senate_candidate_fields': 4532, 'presidential_candidate_fields': 20394,
        'missing_source_fields_are_null_not_zero': True,
        'unprinted_template_positions_added_as_explicit_nulls': 126,
        'source_scope': 'Preferred82 original SEMS source publications; old Pike and Coahoma alternatives nonadditive.'}
    savejson(OUT/'2024-all11-contract-dependency-audit.json', {
        'dependency': contract['preferred_2024_all11_source_fields_dependency'],
        'source_checks': source_checks,
        'original_reading_pins': pins,
        'status': 'complete_preferred_2024_named_fields_only_other_gates_open'})
    return contract
