"""Compare independent direct-original Union BP-009 transcriptions read-only."""
import json

from acquire_sources import BASE, OUT, savejson, sha


def main():
    own_path = OUT / '2024-union-ballot-styles-original-reading.json'
    peer_path = BASE / 'data/baselines/union-split-ballot-style-readings.json'
    own = json.loads(own_path.read_text())
    peer = json.loads(peer_path.read_text())
    assert own['source_raw_sha256'] == peer['raw_sha256']
    assert len(own['split_rows']) == len(peer['split_rows']) == 58
    assert len(own['parent_TOTAL_rows']) == len(peer['parents']) == 20
    diffs = []
    own_rows = {(r['pdf_page'], r['printed_precinct_code'], r['split_ordinal_within_parent']): r for r in own['split_rows']}
    peer_rows = {(r['PDFpage'], r['precinct_code_literal'], r['split_row_within_printed_parent']): r for r in peer['split_rows']}
    assert len(own_rows) == len(peer_rows) == 58
    for key in sorted(set(own_rows) | set(peer_rows)):
        a, b = own_rows.get(key), peer_rows.get(key)
        if a is None or b is None:
            diffs.append({'key': key, 'missing_side': 'own' if a is None else 'peer'})
            continue
        for af, bf in [('printed_precinct_name', 'precinct_name_literal'),
                       ('printed_split_literal', 'split_literal'),
                       ('printed_ballot_style_literal', 'ballot_style_literal'),
                       ('printed_party_literal', 'party_literal'),
                       ('printed_total_voters', 'total_voters')]:
            if a[af] != b[bf]:
                diffs.append({'key': key, 'field': af, 'own': a[af], 'peer': b[bf]})
    own_parents = {(r['pdf_page'], r['printed_precinct_code']): r for r in own['parent_TOTAL_rows']}
    peer_parents = {(r['PDFpage'], r['precinct_code_literal']): r for r in peer['parents']}
    assert len(own_parents) == len(peer_parents) == 20
    for key in sorted(set(own_parents) | set(peer_parents)):
        a, b = own_parents.get(key), peer_parents.get(key)
        if a is None or b is None:
            diffs.append({'parent_key': key, 'missing_side': 'own' if a is None else 'peer'})
        else:
            for af, bf in [('printed_precinct_name', 'precinct_name_literal'),
                           ('printed_TOTAL_voters', 'printed_TOTAL_voters')]:
                if a[af] != b[bf]:
                    diffs.append({'parent_key': key, 'field': af, 'own': a[af], 'peer': b[bf]})
    assert own['printed_Grand_Total_voters'] == peer['printed_grand_TOTAL_voters'] == 17058
    result = {'status': 'agree_all_original_source_rows' if not diffs else 'differences_require_original_review',
              'source_id': own['source_id'], 'source_raw_sha256': own['source_raw_sha256'],
              'own_path': str(own_path.relative_to(BASE)), 'own_sha256': sha(own_path.read_bytes()),
              'peer_path': str(peer_path.relative_to(BASE)), 'peer_sha256': sha(peer_path.read_bytes()),
              'split_rows_compared': 58, 'parent_TOTAL_rows_compared': 20,
              'differences': diffs,
              'qualification': 'Original source row values/labels are compared after separate original reading. Raster pixel, crop polygon, SEMS/native profile identity, and candidate allocations are not inferred.'}
    savejson(OUT / '2024-union-ballot-styles-peer-reconciliation.json', result)
    print(result['status'], len(diffs), 'differences')


if __name__ == '__main__':
    main()
