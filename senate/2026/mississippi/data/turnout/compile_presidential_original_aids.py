"""Compile independent original presidential OCR + visual reads for QA only.

This does not fill blanks from county controls or accept native geography. It
records each source-original pixel position and leaves invalid/missing rows null.
"""
import csv,gzip,json,collections
from acquire_sources import BASE,OUT,savejson,sha
from read_physical_native import PRES24

def main():
    ledger=json.loads((OUT/'native-reviewed-2024.json').read_text())
    roles={(sid,p['page'],c['source_column']):c for sid,s in ledger['sources'].items() for p in s['pages'] for c in p['columns']}
    contract=json.loads((OUT/'priority-set.json').read_text())
    native_keys={(u['source_id'],u['source_page'],u['source_column']):u['key'] for u in contract['source_native_constituents']}
    second=json.loads(gzip.decompress((OUT/'presidential-null-digit-region-aid.json.gz').read_bytes()))
    additional={(x['source_id'],x['page'],x['source_column'],x['candidate']):x for x in second['readings']}
    manual=json.loads((OUT/'presidential-unresolved-original-readings.json').read_text())
    direct={(x['source_id'],x['source_page'],x['source_column'],x['candidate']):x for x in manual['readings']}
    assert len(additional)==2618 and len(direct)==922
    rows=[];source_checks=[];manual2=json.loads((OUT/'native-allfield-readings.json').read_text())
    verified={(sid,p['page'],i,f['candidate']):v for sid,s in manual2['sources'].items() for p in s['pages'] for f in p['fields'] for i,v in enumerate(f['values'],1)}
    manual2_differences=[]
    for path in sorted((OUT/'extracts/physical-native-v3').glob('sos-2024-county-*.json.gz')):
        d=json.loads(gzip.decompress(path.read_bytes()));sid=d['source_id'];assert d['raw_sha256']==ledger['sources'][sid]['raw_sha256']
        tally=collections.defaultdict(lambda:dict(native_sum=0,native_count=0,unresolved=0,printed_TOTAL_values=[]))
        for p in d['pages']:
            for f in p['fields']:
                name=f['candidate_position_hint']
                if name not in PRES24:continue
                for c in f['cells']:
                    col=c['source_column'];k=(sid,p['page'],col,name);u=roles.get((sid,p['page'],col));role=u['role'] if u else 'unmatched_source_column'
                    first=c['value'];aid=additional.get(k);view=direct.get(k)
                    assert first is not None or role!='native_reporting_constituent' or aid is not None
                    if role=='unused_template_column':value=None;basis='verified_unused_source_template_column'
                    elif k in verified:value=verified[k];basis='independent_direct_full_original_allfield_read'
                    elif first is not None:value=first;basis='first_independent_original_cell_OCR_unaccepted'
                    elif view is not None:value=view['value'];basis=view['status']
                    elif aid is not None and aid['second_ocr']['value'] is not None:value=aid['second_ocr']['value'];basis='second_independent_original_digit_region_OCR_unaccepted'
                    else:value=None;basis='unresolved_original_cell'
                    if k in verified:
                        provisional=first if first is not None else (view['value'] if view else aid['second_ocr']['value'] if aid else None)
                        if provisional!=verified[k]:manual2_differences.append(dict(source_id=sid,page=p['page'],source_column=col,candidate=name,raw_OCR_or_atlas_provisional=provisional,original_visual_accepted=verified[k],accepted_basis='independent_direct_full_original_allfield_read'))
                    rec=dict(source_id=sid,source_raw_sha256=d['raw_sha256'],source_page=p['page'],source_column=col,candidate=name,role=role,source_native_key=native_keys.get((sid,p['page'],col)),original_cell_bounds=c['bounds'],original_value_first_OCR=first,original_raw_first_OCR=c['raw_ocr'],second_original_OCR=aid['second_ocr']['value'] if aid else None,second_original_raw_OCR=aid['second_ocr']['raw_ocr'] if aid else None,direct_visual_read=view['value'] if view else None,compiled_provisional_value=value,compiled_basis=basis)
                    rows.append(rec)
                    t=tally[name]
                    if role=='native_reporting_constituent':
                        if value is None:t['unresolved']+=1
                        else:t['native_sum']+=value;t['native_count']+=1
                    elif role=='source_TOTAL':t['printed_TOTAL_values'].append(value)
        source_checks.append(dict(source_id=sid,raw_sha256=d['raw_sha256'],candidates=dict(tally)))
    savejson(OUT/'presidential-original-aid-controls.json',dict(scope='Original-only provisional readings; neither whole-state acceptance nor county residual allocation. First/second OCR are reading aids. Direct original visual readings override unresolved OCR only. Candidate and source TOTAL balance is a separate gate.',source_views=len(source_checks),position_rows=len(rows),source_checks=source_checks,manual_two_view_differences=manual2_differences,unresolved_native_positions=[dict(source_id=r['source_id'],source_page=r['source_page'],source_column=r['source_column'],candidate=r['candidate'],basis=r['compiled_basis']) for r in rows if r['role']=='native_reporting_constituent' and r['compiled_provisional_value'] is None]))
    with (OUT/'presidential-original-aid-cells.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    print('Presidential original aid',len(source_checks),'views',len(rows),'positions; native unresolved',sum(x['candidates'].get(n,{}).get('unresolved',0) for x in source_checks for n in PRES24),'two original manual view differences',len(manual2_differences))

if __name__=='__main__':main()
