"""Independent arithmetic and bounded original-page review; not native acceptance."""
from pathlib import Path
import gzip
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    summaries = json.loads((DATA / 'turnout/canvass-summary-readings.json').read_bytes())['sources']
    statistics = json.loads((DATA / 'turnout/canvass-statistics-readings.json').read_bytes())
    refs = json.loads((DATA / 'baselines/source/references.json').read_bytes())
    primary = json.loads((DATA / 'coordinator-county-primary-review.json').read_bytes())
    counties = {x['county_literal'].lower(): x['source_candidates'] for x in primary['full82_descending_order']}
    summary_by = {x['source_id']: x for x in summaries}
    stat_by = {x['source_id']: x for x in statistics}
    original_pins = []
    method_vectors = 0
    comparisons = []
    for x in summaries:
        sid = x['source_id']
        r = next(y for y in refs if y['id'] == sid)
        stored = (ROOT / r['path']).read_bytes()
        raw = gzip.decompress(stored)
        assert sha(raw) == r['raw_sha256'] and sha(stored) == r['stored_sha256']
        original_pins.append(dict(r))
        county = sid.replace('sos-2024-county-', '')
        delta = {k: x['senate'][k][0] - counties[county][k] for k in ['Ty Pinkins', 'Roger F. Wicker']}
        expected = {'Ty Pinkins': -1232, 'Roger F. Wicker': -1486} if county == 'pike' else {'Ty Pinkins': 0, 'Roger F. Wicker': 0}
        assert delta == expected
        comparisons.append({'source_id': sid, 'page': x['page'], 'named_original_minus_final_state': delta})
        for office in ['senate', 'president']:
            for label, values in x[office].items():
                if values is None:
                    continue
                assert len(values) == len(x['methods']), (sid, office, label)
                if len(values) > 1:
                    assert values[0] == sum(values[1:]), (sid, office, label, values)
                    method_vectors += 1
    for x in statistics:
        if x['ballots_cast_by_method'] is not None:
            assert len(x['methods_literal']) == len(x['ballots_cast_by_method'])
            assert x['ballots_cast_total'] == sum(x['ballots_cast_by_method'])
    laud = summary_by['sos-2024-county-lauderdale']['senate']
    assert laud['Write-In Totals'] == [79, 64, 14, 1, 0, 0]
    for i, total in enumerate(laud['Contest Totals']):
        assert total == sum(laud[k][i] for k in ['Ty Pinkins', 'Roger F. Wicker', 'Write-In Totals', 'Overvotes', 'Undervotes'])
    assert stat_by['sos-2024-county-lauderdale']['ballots_cast_total'] == 27597
    assert laud['Contest Totals'][0] == 27593
    quitman = summary_by['sos-2024-county-quitman']['senate']
    assert quitman['Ballots Cast'] == [2737, 2729, 8]
    for i, total in enumerate(quitman['Ballots Cast']):
        assert total == sum(quitman[k][i] for k in ['Ty Pinkins', 'Roger F. Wicker', 'Write-In', 'Overvotes', 'Undervotes'])
    assert summary_by['sos-2024-county-quitman']['separate_county_voting_method_ballots']
    assert stat_by['sos-2024-county-pike']['ballots_cast_total'] == 12824
    assert summary_by['sos-2024-county-pike']['senate']['Contest Totals'] == [12824]
    visual = json.loads((DATA / 'coordinator-qa/summary-page-renders.json').read_bytes())
    assert {(x['source_id'], x['page']) for x in visual} == {
        ('sos-2024-county-lauderdale', 2), ('sos-2024-county-lauderdale', 3),
        ('sos-2024-county-pike', 12), ('sos-2024-county-pike', 13), ('sos-2024-county-quitman', 6)}
    for x in visual:
        b = (ROOT / x['path']).read_bytes()
        assert sha(b) == x['sha256'] and len(b) == x['bytes']
    out = {
        'status': 'pass_bounded_summary_arithmetic_with_retained_source_scope_differences',
        'summary_sources': len(summaries), 'statistics_panels': len(statistics),
        'checked_method_vectors': method_vectors, 'named_candidate_comparisons': comparisons,
        'original_sources_reused_read_only': original_pins,
        'summary_reading_snapshot': summaries, 'statistics_reading_snapshot': statistics,
        'independently_rendered_and_visually_read_complete_pages': visual,
        'material_scopes': {
            'Lauderdale': '79 generic write-in marks; 27593 Senate contest versus 27597 county ballots; 4 difference retained, no cause/allocation.',
            'Quitman': '2739 county voting-method ballots versus 2737 Senate contest ballots; scanned/manual is a different dimension from absentee/precinct.',
            'Pike': 'Original certified report 12824 ballots and 12617 named Senate votes; separate updated county source has 15335 named votes. Do not splice these vintages.',
            'registration': 'Literal zero values in selected original panels remain source values; no eligibility/population claim.',
        },
        'scope': '14 summary and 12 statistics readings at this observation, with five complete primary pages independently rendered/read. Other reading transcriptions receive arithmetic and exact-source hash checks here, not a claim of independent visual reading of every cell. Whole-state native/generic/method extraction, peer agreement and current geographic/reporting approval remain separate open gates.'
    }
    (DATA / 'coordinator-summary-scope-review.json').write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({k: out[k] for k in ['status', 'summary_sources', 'statistics_panels', 'checked_method_vectors']}))


if __name__ == '__main__':
    main()
