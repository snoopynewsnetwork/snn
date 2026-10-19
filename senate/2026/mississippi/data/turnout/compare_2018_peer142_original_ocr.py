"""Post-extraction diagnostic comparison of two independent OCR pipelines.

The immutable peer's published cells enter only after our original-page OCR
outputs already exist. OCR agreement is evidence, never final visual approval.
"""
import gzip
import json
from collections import Counter
from acquire_sources import BASE, OUT, savejson, sha

SNAP=BASE/'data/baselines/source/native-2018-142views-v2/snapshot.json'
SNAP_SHA='9fba26e5f69b1e844b62e1b262b48701daf0ddef3cf747c83d610d12202036fe'
OLD_HINT=OUT/'source/2018-frozen78-vote-free-position-hints-v1.json'
NEW_HINT=OUT/'source/2018-peer142-new64-vote-free-position-hints-v1.json'


def main():
    snap_raw=SNAP.read_bytes();assert sha(snap_raw)==SNAP_SHA
    snap=json.loads(snap_raw)
    pin=next(x for x in snap['pins'] if x['original_path']=='data/baselines/native-2018-original-readings.json')
    stored=(BASE/pin['stored_path']).read_bytes();raw=gzip.decompress(stored)
    assert len(stored)==pin['stored_bytes'] and sha(stored)==pin['stored_sha256']
    assert len(raw)==pin['original_bytes'] and sha(raw)==pin['original_sha256']
    peer=json.loads(raw);assert len(peer['sources'])==142
    old={s['source_id'] for s in json.loads(OLD_HINT.read_text())['sources']}
    newer={s['source_id'] for s in json.loads(NEW_HINT.read_text())['sources']}
    assert len(old)==78 and len(newer)==64 and not old&newer
    counts=Counter();mismatches=[];source_results=[]
    for source in peer['sources']:
        sid=source['source_id'];is_old=sid in old
        assert is_old or sid in newer
        path=(OUT/f'qa/2018-frozen78-original-pixels/{sid}/diagnostic.json' if is_old else
              OUT/f'qa/2018-peer142-original-tsv/{sid}/diagnostic.json')
        doc=json.loads(path.read_text())
        assert doc['source_raw_sha256']==source['raw_sha256']
        assert len(doc['pages'])==len(source['pages'])
        local=Counter()
        for page,reading in zip(source['pages'],doc['pages']):
            number=page['page']
            assert number==(reading['source_pdf_page'] if is_old else reading['source_pdf_page'])
            assert len(page['fields'])==len(reading['fields'])
            if is_old:
                assert reading['status']=='original_OCR_diagnostic_only'
            else:
                assert reading['render_size']==page['render_size']
                original=BASE/reading['original_render_path']
                assert original.exists() and sha(original.read_bytes())==reading['original_render_sha256']
                tsv=BASE/reading['original_full_page_tsv_path']
                saved=tsv.read_bytes();assert sha(saved)==reading['original_full_page_tsv_stored_sha256']
                assert len(saved)==reading['original_full_page_tsv_stored_bytes']
                assert sha(gzip.decompress(saved))==reading['original_full_page_tsv_raw_sha256']
            for field,read_field in zip(page['fields'],reading['fields']):
                assert len(field['values'])==len(read_field['cells'])==len(page['columns'])
                for i,cell in enumerate(read_field['cells']):
                    assert cell['source_column']==i+1
                    expected=field['values'][i]
                    observed=(cell.get('value_if_numeric_unaccepted') if is_old else
                              cell['parsed_single_number_diagnostic'])
                    text=(cell.get('raw_original_ocr','') if is_old else
                          ' '.join(t['text'] for t in cell['original_page_tsv_tokens']))
                    if isinstance(expected,int):
                        local['source_numeric']+=1
                        status='numeric_OCR_match' if observed==expected else 'numeric_OCR_unresolved_or_disagree'
                    elif str(i+1) in field.get('source_marks',{}):
                        assert expected is None and field['source_marks'][str(i+1)]=='X'
                        local['source_X']+=1
                        status='source_X_OCR_match' if text.strip().upper()=='X' else 'source_X_OCR_unresolved'
                    else:
                        assert expected is None
                        local['source_unprinted_null']+=1
                        status='source_null_OCR_blank' if not text.strip() else 'source_null_OCR_nonblank'
                    local[status]+=1
                    if status in ('numeric_OCR_unresolved_or_disagree','source_X_OCR_unresolved','source_null_OCR_nonblank'):
                        mismatches.append({'source_id':sid,'source_raw_sha256':source['raw_sha256'],
                                           'source_page':number,'source_row_ordinal':read_field['source_row_ordinal'],
                                           'source_column':i+1,'candidate':field['candidate'],
                                           'peer_source_value':expected,'peer_source_mark':field.get('source_marks',{}).get(str(i+1)),
                                           'independent_original_OCR_text':text,
                                           'independent_original_OCR_parsed_value':observed,
                                           'original_render_path':reading['original_render_path'],
                                           'original_render_sha256':reading['original_render_sha256'],
                                           'targeting_qualification':'provisional_OCR_cell_from_value_free_geometry_not_accepted_numeric_polygon',
                                           'diagnostic':status})
        counts.update(local)
        source_results.append({'source_id':sid,'raw_sha256':source['raw_sha256'],
                               'ocr_pipeline':'older_individual_original_cell' if is_old else 'new_full_original_page_TSV',
                               'diagnostic_path':str(path.relative_to(BASE)),
                               'diagnostic_sha256':sha(path.read_bytes()),
                               'counts':dict(local)})
    assert len(source_results)==142
    assert counts['source_numeric']+counts['source_X']+counts['source_unprinted_null']==4752+sum(
        len(p['physical_columns'])*len(p['candidate_row_positions'])
        for s in json.loads(NEW_HINT.read_text())['sources'] for p in s['pages'])
    savejson(OUT/'2018-peer142-original-ocr-diagnostic.json',{
        'scope':'Post-extraction diagnostic only: source bytes/hash/pages and original OCR compared with independent frozen peer values. Matching OCR is not final original visual acceptance; mismatches are not repaired or allocated.',
        'peer_snapshot_path':str(SNAP.relative_to(BASE)),
        'peer_snapshot_sha256':SNAP_SHA,
        'peer_ledger_original_sha256':sha(raw),
        'old78_value_free_hint_sha256':sha(OLD_HINT.read_bytes()),
        'new64_value_free_hint_sha256':sha(NEW_HINT.read_bytes()),
        'source_views':142,'counts':dict(counts),
        'source_results':source_results,'mismatches':mismatches,
        'accepted_native_field_count_from_this_comparison':0})
    print('142-source 2018 original OCR diagnostic',dict(counts),'exceptions',len(mismatches))


if __name__=='__main__':main()
