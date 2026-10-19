"""Diagnostic comparison after fresh original OCR, with no value promotion."""
import gzip
import json
from acquire_sources import BASE, OUT, sha, savejson

SNAP = BASE / 'data/baselines/source/native-2018-78views-v1/snapshot.json'
SNAP_SHA = '4df50caded4d9a1cdfd46081422e36002439b10aea28cfab1fb6dcf00f34621c'
VALID = OUT / '2018-frozen78-original-pixels-validation.json'


def norm(s): return ' '.join(s.split())


def main():
    v_raw = VALID.read_bytes(); v = json.loads(v_raw)
    assert v['source_views'] == 78 and v['original_pages'] == 144
    for pin in v['assets']:
        raw=(BASE/pin['path']).read_bytes()
        assert len(raw)==pin['bytes'] and sha(raw)==pin['sha256']
    snap_raw = SNAP.read_bytes(); assert sha(snap_raw) == SNAP_SHA
    snap=json.loads(snap_raw)
    pin=next(x for x in snap['pins'] if x['original_path']==
             'data/baselines/native-2018-original-readings.json')
    stored=(BASE/pin['stored_path']).read_bytes();peer_raw=gzip.decompress(stored)
    assert len(stored)==pin['stored_bytes'] and sha(stored)==pin['stored_sha256']
    assert len(peer_raw)==pin['original_bytes'] and sha(peer_raw)==pin['original_sha256']
    peer=json.loads(peer_raw)
    numbers=dict(expected_printed_numeric=0,exact_numeric_OCR=0,
                 numeric_OCR_disagree=0,expected_source_X=0,exact_X_OCR=0,
                 source_X_OCR_disagree=0,expected_unprinted_null=0,
                 blank_OCR_on_unprinted=0,nonblank_OCR_on_unprinted=0,
                 original_header_positions=0,header_OCR_fold_match=0,
                 header_OCR_disagree=0,geometry_mismatch_pages=0)
    numerical_exceptions=[];header_exceptions=[];source_summary=[]
    for s in peer['sources']:
        sid=s['source_id'];path=OUT/f'qa/2018-frozen78-original-pixels/{sid}/diagnostic.json'
        d=json.loads(path.read_text());assert d['source_raw_sha256']==s['raw_sha256']
        assert len(d['pages'])==len(s['pages'])
        local=dict.fromkeys(numbers,0)
        for p,q in zip(s['pages'],d['pages']):
            assert p['page']==q['source_pdf_page']
            if q['status']=='source_target_geometry_mismatch_no_values_interpreted':
                local['geometry_mismatch_pages']+=1
                continue
            assert len(p['columns'])==len(q['headers'])
            assert len(p['fields'])==len(q['fields'])
            for c,h in zip(p['columns'],q['headers']):
                assert c['source_column']==h['source_column']
                local['original_header_positions']+=1
                if norm(c['label_literal'])==norm(h['raw_original_header_ocr']):
                    local['header_OCR_fold_match']+=1
                else:
                    local['header_OCR_disagree']+=1
                    header_exceptions.append(dict(source_id=sid,page=p['page'],
                        source_column=c['source_column'],
                        original_OCR_literal=h['raw_original_header_ocr'],
                        peer_literal=c['label_literal'],
                        original_upright_crop_sha256=h['upright_crop_png_sha256']))
            for f,field in zip(p['fields'],q['fields']):
                assert len(f['values'])==len(field['cells'])==len(p['columns'])
                for col,c in enumerate(field['cells'],1):
                    assert c['source_column']==col
                    expected=f['values'][col-1]
                    raw_ocr=c.get('raw_original_ocr','')
                    observed=c.get('value_if_numeric_unaccepted')
                    if isinstance(expected,int):
                        local['expected_printed_numeric']+=1
                        if observed==expected:
                            local['exact_numeric_OCR']+=1
                        else:
                            local['numeric_OCR_disagree']+=1
                            numerical_exceptions.append(dict(source_id=sid,page=p['page'],
                                source_column=col,source_row_ordinal=field['source_row_ordinal'],
                                peer_candidate=f['candidate'],peer_printed_value=expected,
                                raw_original_OCR=raw_ocr,original_crop_sha256=c.get('crop_png_sha256'),
                                original_full_render=q['original_render_path'],
                                original_full_render_sha256=q['original_render_sha256'],
                                provisional_crop_box=c['provisional_crop_box'],
                                reason='original_OCR_disagrees_with_independent_peer_printed_value'))
                    elif str(col) in f.get('source_marks',{}):
                        assert expected is None and f['source_marks'][str(col)]=='X'
                        local['expected_source_X']+=1
                        if raw_ocr in ('X','x'):local['exact_X_OCR']+=1
                        else:
                            local['source_X_OCR_disagree']+=1
                            numerical_exceptions.append(dict(source_id=sid,page=p['page'],
                                source_column=col,source_row_ordinal=field['source_row_ordinal'],
                                peer_candidate=f['candidate'],peer_source_mark='X',
                                raw_original_OCR=raw_ocr,original_crop_sha256=c.get('crop_png_sha256'),
                                original_full_render=q['original_render_path'],
                                original_full_render_sha256=q['original_render_sha256'],
                                provisional_crop_box=c['provisional_crop_box'],
                                reason='source_X_mark_not_recognized_exactly_by_OCR'))
                    else:
                        assert expected is None
                        local['expected_unprinted_null']+=1
                        if raw_ocr=='':local['blank_OCR_on_unprinted']+=1
                        else:
                            local['nonblank_OCR_on_unprinted']+=1
                            numerical_exceptions.append(dict(source_id=sid,page=p['page'],
                                source_column=col,source_row_ordinal=field['source_row_ordinal'],
                                peer_candidate=f['candidate'],
                                raw_original_OCR=raw_ocr,original_crop_sha256=c.get('crop_png_sha256'),
                                original_full_render=q['original_render_path'],
                                original_full_render_sha256=q['original_render_sha256'],
                                provisional_crop_box=c['provisional_crop_box'],
                                reason='OCR_token_in_peer_unprinted_or_unvalued_position'))
        for k in numbers:numbers[k]+=local[k]
        source_summary.append(dict(source_id=sid,source_raw_sha256=s['raw_sha256'],
                                   comparisons=local))
    compared=numbers['expected_printed_numeric']+numbers['expected_source_X']+numbers['expected_unprinted_null']
    if numbers['geometry_mismatch_pages']==0:assert compared==4752
    else:assert compared<4752
    assert len(numerical_exceptions)==numbers['numeric_OCR_disagree']+numbers['source_X_OCR_disagree']+numbers['nonblank_OCR_on_unprinted']
    assert len(header_exceptions)==numbers['header_OCR_disagree']
    result=dict(scope='Post-extraction diagnostic comparison of immutable original-pixel OCR to frozen independent source values/headers. Matching OCR is evidence, not an accepted native transcription; every exception remains unresolved until direct original-page review. No peer values entered the OCR input.',
                original_OCR_validation_path=str(VALID.relative_to(BASE)),
                original_OCR_validation_sha256=sha(v_raw),
                peer_snapshot_path=str(SNAP.relative_to(BASE)),
                peer_snapshot_sha256=SNAP_SHA,
                peer_ledger_original_sha256=sha(peer_raw),
                peer_ledger_stored_sha256=sha(stored),
                source_views=len(source_summary),counts=numbers,
                source_comparisons=source_summary,
                numerical_or_source_mark_OCR_exceptions=numerical_exceptions,
                header_OCR_exceptions=header_exceptions,
                accepted_native_field_count_from_this_comparison=0)
    savejson(OUT/'2018-frozen78-original-ocr-peer-diagnostic.json',result)
    print('Frozen78 OCR vs peer DIAGNOSTIC ONLY:',numbers,
          len(numerical_exceptions),'numeric/mark exceptions,',
          len(header_exceptions),'header OCR exceptions')


if __name__=='__main__':main()
