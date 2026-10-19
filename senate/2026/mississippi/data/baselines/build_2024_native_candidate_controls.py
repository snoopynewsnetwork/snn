"""Every preferred county/candidate native vector versus literal signed controls."""
import csv,json
from collections import Counter
from sources import OUT,BASE,save,sha
from extract_native import cell_key
from extract_replay_president import NAMES
from build_counties import writecsv
def main():
    cp=OUT/'native-allfield-coverage.json';x=json.loads(cp.read_text());assert x['complete_statewide_nine_presidential_native'] and x['counts']['source_views']==82;controls={};state=Counter();certstate=Counter();rows=[];diff=[]
    for r in csv.DictReader((OUT/'candidate-votes.csv').open()):
        if r['contest'] in ['2024-president','2024-senate']:controls[r['fips'],cell_key(r['candidate_literal'])]=r
    for s in x['sources']:
        fips=next(p['county_fips'] for p in x['all82_preferred_source_parent_status'] if p['source_id']==s['source_id'])
        for name,v in s['all11_source_native_sums'].items():
            c=controls[fips,name];cv=int(c['votes']);state[name]+=v;certstate[name]+=cv
            row=dict(county_fips=fips,source_id=s['source_id'],raw_sha256=s['raw_sha256'],candidate=name,source_native_sum=v,printed_TOTAL=v,certified_county_votes=cv,native_minus_certified=v-cv,county_control_source_id=c['source_id'],county_control_position=c['source_position'],original_readings_path=s['own_original_readings_path'],native_constituents=s['native_constituents'],residual_allocated=False);rows.append(row)
            if v!=cv:diff.append(row)
    assert len(rows)==902 and len(diff)==2 and all(r['source_id']=='sos-2024-county-tunica' and r['candidate'] in ['Kamala D. Harris','Ty Pinkins'] and r['native_minus_certified']==-1 for r in diff);alt=json.loads((OUT/'native-alternative-allfield-readings.json').read_text());assert alt['complete_two_alternative_views'] and alt['counts']['native_constituents']==43
    writecsv(OUT/'native-2024-candidate-controls.csv',rows)
    save(OUT/'native-2024-candidate-controls.json',dict(status='pass_all82_preferred_source_candidate_vectors_with_two_explicit_unallocated_primary_differences',coverage_pin=dict(path=str(cp.relative_to(BASE)),bytes=cp.stat().st_size,sha256=sha(cp.read_bytes())),preferred_source_views=82,preferred_native_constituents=1736,county_candidate_controls=902,source_state_candidate_sums=dict(state),signed_county_candidate_sums=dict(certstate),source_state_presidential_named_denominator=sum(state[n] for n in NAMES),certified_state_presidential_named_denominator=sum(certstate[n] for n in NAMES),source_state_Senate_named_denominator=state['Ty Pinkins']+state['Roger F. Wicker'],certified_state_Senate_named_denominator=certstate['Ty Pinkins']+certstate['Roger F. Wicker'],differences=diff,alternative_sources=[dict(source_id=s['source_id'],raw_sha256=s['raw_sha256'],controls=s['controls'],preferred82=False,additive=False) for s in alt['sources']],alternative_counts=alt['counts'],qualification='All11 named candidates in every preferred SEMS native source partition and two explicitly nonadditive earlier alternatives. Each source closes its own printed TOTAL. Tunica differences stay unallocated. This is not complete vendor/method/turnout/registration/history/current-geography or independent peer acceptance.'))
    print('2024 native candidate controls',len(rows),'explicit differences',len(diff),'sourcePres',sum(state[n] for n in NAMES))
if __name__=='__main__':main()
