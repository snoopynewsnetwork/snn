"""Exact bounded all11 original coverage, keeping every unreviewed parent visible."""
import json
from collections import Counter
from sources import OUT,BASE,save,sha,original
from extract_replay_president import NAMES
NAMES=NAMES+['Ty Pinkins','Roger F. Wicker']
def main():
    inputs=[];sources=[]
    for filename in ['alcorn-readings.json','coahoma-updated-readings.json','native-source-exception-readings.json','winston-native-allfield-readings.json','native-allfield-additional-readings.json']:
        path=OUT/filename;x=json.loads(path.read_text());inputs.append(dict(path=str(path.relative_to(BASE)),bytes=path.stat().st_size,sha256=sha(path.read_bytes())))
        if filename=='native-source-exception-readings.json':ss=x['sources']
        elif filename=='native-allfield-additional-readings.json':ss=x['sources']
        else:ss=[x]
        for s in ss:
            sid=s['source_id'];assert sha(original(sid))==s['raw_sha256'];native=0;total=0;unused=0;parallel=0;sums=Counter();totals={};numeric=0;null=0
            for p in s['pages']:
                if 'columns' in p:
                    roles=[('source_TOTAL' if c['unit_type']=='summary_TOTAL' else 'unused_template_column' if c['unit_type']=='unused' else 'source_native_reporting_constituent') for c in p['columns']]
                else:roles=['unused_template_column' if r=='unused_template_column' else r for r in p['roles']]
                assert len(p['fields'])==11;native+=roles.count('source_native_reporting_constituent');total+=roles.count('source_TOTAL');unused+=roles.count('unused_template_column');parallel+=roles.count('parallel_native_observation');seen=set()
                for f in p['fields']:
                    name=f.get('candidate',f.get('field'));assert name not in seen and name in NAMES;seen.add(name);assert len(f['values'])==len(roles)
                    for role,v in zip(roles,f['values']):
                        if role=='unused_template_column':assert v is None;null+=1
                        else:
                            assert isinstance(v,int) and v>=0;numeric+=1
                            if role=='source_native_reporting_constituent':sums[name]+=v
                            elif role=='source_TOTAL':totals[name]=v
                            else:assert role=='parallel_native_observation'
                assert len(seen)==11
            assert len(totals)==11 and dict(sums)==totals and total==1,(sid,sums,totals)
            sources.append(dict(source_id=sid,raw_sha256=s['raw_sha256'],own_original_readings_path=str(path.relative_to(BASE)),source_pages=len(s['pages']),native_constituents=native,source_TOTAL_columns=total,unused_blank_columns=unused,nonadditive_parallel_columns=parallel,numeric_positions=numeric,unused_null_positions=null,all11_source_native_sums=totals,all11_source_vectors_close_printed_TOTAL=True))
    assert len({s['source_id'] for s in sources})==len(sources);accepted={s['source_id']:s for s in sources};order=json.loads((OUT/'native-source-orders.json').read_text());preferred=order['preferred82_view'];parents=[]
    for sid,ss in __import__('itertools').groupby(sorted(preferred['full_descending_order'],key=lambda r:r['source_id']),key=lambda r:r['source_id']):
        rr=list(ss);p=accepted.get(sid)
        if p:assert len(rr)==p['native_constituents']
        parents.append(dict(source_id=sid,county_fips=rr[0]['parent_county_fips'],source_native_constituents=len(rr),all11_original_review_complete=bool(p),readings_path=p['own_original_readings_path'] if p else None,qualification='Selected SEMS source partition only; vendor/method/history/current geography gates remain separate' if p else 'Nine presidential original native vectors still pending; no missing/zero inference'))
    assert len(parents)==82;counts={k:sum(s[k] for s in sources) for k in ['source_pages','native_constituents','source_TOTAL_columns','unused_blank_columns','nonadditive_parallel_columns','numeric_positions','unused_null_positions']};counts['source_views']=len(sources);counts['preferred_unreviewed_native_constituents']=1736-counts['native_constituents'];counts['preferred_unreviewed_county_views']=82-len(sources)
    complete=all(p['all11_original_review_complete'] for p in parents)
    save(OUT/'native-allfield-coverage.json',dict(qualification='Independently original-read all11candidate preferred SEMS views only. All82 preferred source parents and1736 source-native positions remain in the scope inventory; any unreviewed presidential cells are unknown, never allocated or inferred zero. Multiple native/vendor views and repeated Kemper observations not additive. Source closure is validated after direct original numeric reading, not used to fit it. Completion of this named-candidate preferred partition does not establish complete historical, alternative-packet, vendor, method or current geographic coverage.',inputs=inputs,counts=counts,sources=sources,all82_preferred_source_parent_status=parents,complete_statewide_nine_presidential_native=complete,historical_native_complete=False,current2026_geography_approved=False));print('Original all11 preferred coverage',counts)
if __name__=='__main__':main()
