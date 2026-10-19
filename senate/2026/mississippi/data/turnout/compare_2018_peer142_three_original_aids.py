"""Compare three completed, original-only OCR aids with frozen source readings.

Peer values are read only after all original-byte OCR passes have been saved.
This diagnostic does not accept cropped geometry, votes, blanks, or X marks.
"""
import gzip
import json
from collections import Counter
from acquire_sources import BASE, OUT, savejson, sha

SNAP=BASE/'data/baselines/source/native-2018-142views-v2/snapshot.json'
SNAP_SHA='9fba26e5f69b1e844b62e1b262b48701daf0ddef3cf747c83d610d12202036fe'
HINT=OUT/'source/2018-peer142-new64-vote-free-position-hints-v1.json'
HINT_SHA='7fc12ad227424e27687945661d5c58e86075bac612b146600ed5d290c9fde93e'


def rows(path):
    raw=path.read_bytes()
    return json.loads(raw),sha(raw)


def main():
    snap_raw=SNAP.read_bytes();assert sha(snap_raw)==SNAP_SHA
    snap=json.loads(snap_raw)
    pin=next(x for x in snap['pins'] if x['original_path']=='data/baselines/native-2018-original-readings.json')
    stored=(BASE/pin['stored_path']).read_bytes();raw=gzip.decompress(stored)
    assert sha(stored)==pin['stored_sha256'] and sha(raw)==pin['original_sha256']
    peer={s['source_id']:s for s in json.loads(raw)['sources']}
    assert sha(HINT.read_bytes())==HINT_SHA
    hints=json.loads(HINT.read_text())['sources'];assert len(hints)==64
    checks=[];counts=Counter();exceptions=[]
    for hint in hints:
        sid=hint['source_id'];source=peer[sid]
        assert hint['source_raw_sha256']==source['raw_sha256']
        root=OUT/f'qa/2018-peer142-original-tsv/{sid}'
        first,h1=rows(root/'diagnostic.json')
        second,h2=rows(root/'ambiguous-original-cell-recheck.json')
        third,h3=rows(root/'denoised-original-cell-diagnostic.json')
        assert first['source_raw_sha256']==second['source_raw_sha256']==third['source_raw_sha256']==source['raw_sha256']
        assert second['first_original_diagnostic_sha256']==h1 and third['initial_recheck_sha256']==h2
        second_cells={(x['source_page'],x['source_row_ordinal'],x['source_column']):x for x in second['rows']}
        third_cells={(x['source_page'],x['source_row_ordinal'],x['source_column']):x for x in third['rows']}
        assert second_cells.keys()==third_cells.keys()
        local=Counter()
        for p,fp in zip(source['pages'],first['pages']):
            assert p['page']==fp['source_pdf_page']
            assert len(p['fields'])==len(fp['fields'])
            assert sha((BASE/fp['original_render_path']).read_bytes())==fp['original_render_sha256']
            for field,aid in zip(p['fields'],fp['fields']):
                assert len(field['values'])==len(aid['cells'])
                for i,cell in enumerate(aid['cells']):
                    k=(p['page'],aid['source_row_ordinal'],i+1)
                    assert cell['source_column']==i+1
                    vals=[cell['parsed_single_number_diagnostic']]
                    texts=[' '.join(t['text'] for t in cell['original_page_tsv_tokens'])]
                    if k in second_cells:
                        assert vals[0] is None
                        vals.append(second_cells[k]['parsed_single_number_diagnostic'])
                        vals.append(third_cells[k]['parsed_single_number_diagnostic'])
                        texts.extend([second_cells[k]['raw_original_OCR_PSM6'],third_cells[k]['raw_OCR_PSM11']])
                    expected=field['values'][i]
                    mark=field.get('source_marks',{}).get(str(i+1))
                    if isinstance(expected,int):
                        kind='numeric'
                        status='some_original_OCR_agrees' if expected in vals else 'all_OCR_unresolved_or_disagrees'
                    elif mark=='X':
                        kind='literal_X'
                        status='some_original_OCR_reads_X' if any(t.strip().upper()=='X' for t in texts) else 'all_OCR_unresolved_X'
                    else:
                        assert expected is None and mark is None
                        kind='unprinted_null'
                        status='all_OCR_blank' if all(not t.strip() for t in texts) else 'OCR_nonblank_at_source_null'
                    local[kind]+=1;local[status]+=1
                    if status in ('all_OCR_unresolved_or_disagrees','all_OCR_unresolved_X','OCR_nonblank_at_source_null'):
                        exceptions.append({'source_id':sid,'source_raw_sha256':source['raw_sha256'],
                                           'page':p['page'],'row':aid['source_row_ordinal'],'physical_column':i+1,
                                           'candidate_literal':field['candidate'],'source_value':expected,'source_mark':mark,
                                           'original_aid_numeric_values':vals,'original_aid_raw_texts':texts,
                                           'render_path':fp['original_render_path'],
                                           'render_sha256':fp['original_render_sha256'],
                                           'status':status,
                                           'qualification':'Original-OCR targeting only; complete-original visual reading still required.'})
        counts.update(local)
        checks.append({'source_id':sid,'source_raw_sha256':source['raw_sha256'],
                       'first_original_diagnostic_sha256':h1,'second_original_diagnostic_sha256':h2,
                       'third_original_diagnostic_sha256':h3,'counts':dict(local)})
    assert len(checks)==64
    assert counts['numeric']+counts['literal_X']+counts['unprinted_null']==5544
    savejson(OUT/'2018-peer142-three-original-aids-diagnostic.json',{
        'scope':'Three independent original-pixel OCR routes for the64 sources added after our frozen78. A matching token is a diagnostic, not an accepted direct read or approved crop geometry.',
        'peer_snapshot':str(SNAP.relative_to(BASE)),'peer_snapshot_sha256':SNAP_SHA,
        'peer_ledger_original_sha256':sha(raw),'value_free_hint_sha256':HINT_SHA,
        'source_views':64,'field_positions':5544,'counts':dict(counts),
        'source_checks':checks,'exceptions':exceptions,
        'accepted_native_fields_from_this_diagnostic':0})
    print('three original aids, diagnostic only',dict(counts),'exceptions',len(exceptions))


if __name__=='__main__':main()
