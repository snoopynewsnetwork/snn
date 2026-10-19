"""Offline provenance/shape check for unaccepted 2018 original-pixel OCR aids.

The aids never supply an accepted vote, zero, source role, or geographic ID.
Re-run extract_2018_original_numeric_aid.py separately to reproduce OCR bytes.
"""
import gzip
import json
from acquire_sources import BASE, OUT, receipts, sha, savejson

TARGET = OUT / 'source/2018-vote-free-targets-v1.json'
TARGET_SHA = '10ae518a2a0c7925848f2dd7f1c55dca8b954e0c2bf0390a01eedf3cb3ea2e38'
STATUSES = ('single_numeric_token', 'no_token', 'ambiguous_or_noninteger')


def main():
    assert sha(TARGET.read_bytes()) == TARGET_SHA
    targets = json.loads(TARGET.read_text())['sources']
    assert len(targets) == 164 and len({s['source_id'] for s in targets}) == 164
    rec = {r['id']: r for r in receipts}
    counts = dict(targeted_cells=0, single_numeric_token=0, no_token=0,
                  ambiguous_or_noninteger=0)
    pins = []
    pages = 0
    empty = []
    geometry_mismatch = []
    for source in targets:
        sid = source['source_id']
        path = OUT / f'qa/2018-native-numeric-aid/{sid}/diagnostic.json'
        raw = path.read_bytes()
        diagnostic = json.loads(raw)
        r = rec[sid]
        assert diagnostic['source_id'] == sid
        assert diagnostic['source_original_path'] == r['path']
        assert diagnostic['source_raw_sha256'] == source['source_raw_sha256'] == r['raw_sha256']
        assert diagnostic['vote_free_target_sha256'] == TARGET_SHA
        assert len(diagnostic['pages']) == len(source['pages'])
        local = dict.fromkeys(counts, 0)
        if not diagnostic['counts']['targeted_cells']:
            empty.append(sid)
        for hint, page in zip(source['pages'], diagnostic['pages']):
            pages += 1
            assert page['source_pdf_page'] == hint['page']
            if page.get('status') == 'render_geometry_mismatch_no_cell_interpretation':
                assert page['render_size'] != hint['render_size']
                geometry_mismatch.append((sid, hint['page']))
                continue
            assert page['render_size'] == hint['render_size']
            assert len(page['fields']) == len(hint['fields'])
            tsv_path = BASE / page['tsv_stored_path']
            stored = tsv_path.read_bytes()
            assert len(stored) < 40_000_000 and sha(stored) == page['tsv_stored_sha256']
            assert sha(gzip.decompress(stored)) == page['tsv_raw_sha256']
            pins.append(dict(path=page['tsv_stored_path'], bytes=len(stored), sha256=sha(stored)))
            for original_field, field in zip(hint['fields'], page['fields']):
                assert original_field['candidate'] == field['candidate']
                assert original_field['row_source_ordinal'] == field['row_source_ordinal']
                assert original_field['candidate_label_box'] == field['candidate_label_target_box']
                assert len(original_field['cells']) == len(field['cells'])
                for original_cell, cell in zip(original_field['cells'], field['cells']):
                    assert original_cell['source_column'] == cell['source_column']
                    assert original_cell['box'] == cell['target_box']
                    status = cell['status']
                    assert status in ('single_numeric_token_unaccepted', 'no_token',
                                      'ambiguous_or_noninteger')
                    local['targeted_cells'] += 1
                    local['single_numeric_token' if status == 'single_numeric_token_unaccepted'
                          else status] += 1
                    if status == 'single_numeric_token_unaccepted':
                        assert isinstance(cell['value_if_unambiguous'], int)
                        assert len(cell['raw_original_ocr_tokens']) == 1
                    else:
                        assert cell['value_if_unambiguous'] is None
        assert local == diagnostic['counts'], (sid, local, diagnostic['counts'])
        for key, n in local.items():
            counts[key] += n
        assert len(raw) < 40_000_000
        pins.append(dict(path=str(path.relative_to(BASE)), bytes=len(raw), sha256=sha(raw)))
    assert pages == 381
    assert len(pins) == 545 - len(geometry_mismatch)
    assert counts == dict(targeted_cells=12476, single_numeric_token=7004,
                          no_token=4430, ambiguous_or_noninteger=1042), counts
    assert len(empty) == 8
    result = dict(scope='Unaccepted original-pixel OCR diagnostic of all164 actual 2018 county-stage publications. Machine vote-free target boxes may omit or clip digits and columns; no OCR value or missing position is an accepted native vote or zero.',
                  target_path=str(TARGET.relative_to(BASE)), target_sha256=TARGET_SHA,
                  source_views=len(targets), targeted_original_pages=pages,
                  source_originals_hash_linked=164, counts=counts,
                  empty_target_views=empty, render_geometry_mismatches=geometry_mismatch,
                  asset_count=len(pins), assets=pins)
    savejson(OUT / '2018-original-numeric-aid-validation.json', result)
    print('2018 diagnostic only:', len(targets), 'source views;', pages,
          'pages;', counts['targeted_cells'], 'tentative cells;',
          len(empty), 'empty machine layouts')


if __name__ == '__main__':
    main()
