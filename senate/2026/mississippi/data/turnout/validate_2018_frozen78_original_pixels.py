"""Offline provenance and position validation for provisional frozen78 OCR.

This checks acquisition, source geometry and lossless original-pixel evidence;
it never promotes an OCR number, missing token, header or rectangle to an
accepted source-native field.
"""
import io
import json
from PIL import Image
from acquire_sources import BASE, OUT, receipts, sha, savejson

HINT = OUT / 'source/2018-frozen78-vote-free-position-hints-v1.json'
HINT_SHA = 'b30c6255643c90fa06465208ea310df4b9405a5268049f7ff760cbb76ef805f8'


def main():
    assert sha(HINT.read_bytes()) == HINT_SHA
    hint = json.loads(HINT.read_text())
    assert hint['source_views'] == len(hint['sources']) == 78
    assert hint['original_pages'] == 144
    assert hint['tentative_candidate_cell_positions'] == 4752
    receipts_by_id = {r['id']: r for r in receipts}
    counts = dict(pages=0,header_targets=0,candidate_cell_targets=0,
                  numeric_tokens=0,literal_X_tokens=0,unresolved_tokens=0,
                  geometry_mismatch_pages=0)
    pins = []
    mismatch = []
    crop_hashes_verified = dict(headers=0,cells=0)
    for source in hint['sources']:
        sid = source['source_id']
        path = OUT / f'qa/2018-frozen78-original-pixels/{sid}/diagnostic.json'
        raw = path.read_bytes(); d = json.loads(raw)
        receipt = receipts_by_id[sid]
        assert d['source_id'] == sid
        assert d['source_raw_sha256'] == source['source_raw_sha256'] == receipt['raw_sha256']
        assert d['source_original_path'] == receipt['path']
        assert d['value_free_hint_sha256'] == HINT_SHA
        assert len(d['pages']) == len(source['pages'])
        local = dict.fromkeys(counts, 0)
        for p_hint, page in zip(source['pages'], d['pages']):
            assert page['source_pdf_page'] == p_hint['source_pdf_page']
            assert page['target_render_size'] == p_hint['render_size']
            render = BASE / page['original_render_path']
            render_raw = render.read_bytes()
            assert len(render_raw) < 40_000_000
            assert sha(render_raw) == page['original_render_sha256']
            image = Image.open(io.BytesIO(render_raw)).convert('L')
            assert list(image.size) == page['render_size']
            pins.append(dict(path=page['original_render_path'], bytes=len(render_raw),
                             sha256=sha(render_raw)))
            local['pages'] += 1
            if page['status'] == 'source_target_geometry_mismatch_no_values_interpreted':
                assert page['render_size'] != p_hint['render_size']
                local['geometry_mismatch_pages'] += 1
                mismatch.append(dict(source_id=sid,page=p_hint['source_pdf_page']))
                continue
            assert page['status'] == 'original_OCR_diagnostic_only'
            assert page['render_size'] == p_hint['render_size']
            assert len(page['headers']) == len(p_hint['physical_columns'])
            assert len(page['fields']) == len(p_hint['candidate_row_positions'])
            for original_col, head in zip(p_hint['physical_columns'], page['headers']):
                assert original_col['source_column'] == head['source_column']
                assert original_col['header_bounds'] == head['target_header_box']
                assert isinstance(head['raw_original_header_ocr'], str)
                crop = image.crop(tuple(head['target_header_box'])).rotate(270,expand=True)
                crop = crop.resize((crop.width*2,crop.height*2))
                stream = io.BytesIO(); crop.save(stream,format='PNG')
                assert sha(stream.getvalue()) == head['upright_crop_png_sha256']
                crop_hashes_verified['headers'] += 1
                local['header_targets'] += 1
            for original_row, field in zip(p_hint['candidate_row_positions'], page['fields']):
                assert original_row['source_row_ordinal'] == field['source_row_ordinal']
                assert original_row['candidate_row_bounds'] == field['target_candidate_row_bounds']
                assert len(field['cells']) == len(p_hint['physical_columns'])
                for original_col, cell in zip(p_hint['physical_columns'], field['cells']):
                    assert cell['source_column'] == original_col['source_column']
                    local['candidate_cell_targets'] += 1
                    if cell['status'] == 'invalid_target_box_no_value':
                        local['unresolved_tokens'] += 1
                        continue
                    box = cell['provisional_crop_box']
                    assert box == [original_col['header_bounds'][0]+5,
                                   original_row['candidate_row_bounds'][1]+4,
                                   original_col['header_bounds'][2]-3,
                                   original_row['candidate_row_bounds'][3]-4]
                    crop = image.crop(tuple(box)).resize(((box[2]-box[0])*3,
                                                          (box[3]-box[1])*3))
                    stream = io.BytesIO(); crop.save(stream,format='PNG')
                    assert sha(stream.getvalue()) == cell['crop_png_sha256']
                    crop_hashes_verified['cells'] += 1
                    if cell['status'] == 'numeric_OCR_unaccepted':
                        assert isinstance(cell['value_if_numeric_unaccepted'], int)
                        local['numeric_tokens'] += 1
                    elif cell['status'] == 'literal_X_OCR_unaccepted':
                        assert cell['raw_original_ocr'] in ('X','x')
                        assert cell['value_if_numeric_unaccepted'] is None
                        local['literal_X_tokens'] += 1
                    else:
                        assert cell['status'] == 'unresolved_or_blank_OCR_unaccepted'
                        assert cell['value_if_numeric_unaccepted'] is None
                        local['unresolved_tokens'] += 1
        assert d['counts'] == local, (sid, d['counts'], local)
        for key in counts: counts[key] += local[key]
        assert len(raw) < 40_000_000
        pins.append(dict(path=str(path.relative_to(BASE)), bytes=len(raw),sha256=sha(raw)))
    assert counts['pages'] == 144
    assert counts['candidate_cell_targets'] + sum(
        len(p['physical_columns'])*len(p['candidate_row_positions'])
        for s in hint['sources'] for p in s['pages'] if
        {'source_id':s['source_id'],'page':p['source_pdf_page']} in mismatch) == 4752
    result = dict(scope='Hash/position validation of fresh SOS original-pixel OCR using a value-free frozen78 layout hint. No OCR number, X, blank or box becomes an accepted native value or geographic identity.',
                  hint_path=str(HINT.relative_to(BASE)),hint_sha256=HINT_SHA,
                  source_views=78,source_originals_hash_linked=78,
                  original_pages=144,counts=counts,render_geometry_mismatches=mismatch,
                  original_pixel_crop_hashes_verified=crop_hashes_verified,
                  asset_count=len(pins),assets=pins)
    savejson(OUT / '2018-frozen78-original-pixels-validation.json', result)
    print('Frozen78 original OCR diagnostic:',counts,'assets',len(pins))


if __name__ == '__main__': main()
