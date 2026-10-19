"""Inventory own original presidential aids; never acceptance from closure."""
import csv,gzip,json
from collections import Counter,defaultdict
from sources import OUT,BASE,save,sha
from build_counties import writecsv
from extract_replay_president import NAMES
from extract_native import cell_key
REPAIRED={'sos-2024-county-'+s for s in ['itawamba','scott','amite','webster','winston']}
def main():
    ledger=json.loads((OUT/'native-2024-senate-reviewed-84views.json').read_text());controls=defaultdict(dict)
    for r in csv.DictReader((OUT/'candidate-votes.csv').open()):
        if r['contest']=='2024-president':
            name=cell_key(r['candidate_literal']);assert name not in controls[r['county']];controls[r['county']][name]=int(r['votes'])
    rawpike=next(r for r in json.loads((OUT/'canvass-readings.json').read_text())['readings'] if r['source_id']=='sos-2024-county-pike');sources=[];flat=[];allstatus=Counter()
    for source in ledger['sources']:
        key=source['source_id'];tag='v5' if key in REPAIRED else 'v4';directory=OUT/'extracts/reviewed-replay'/key;preferred=next((directory/f'independent-presidential-cells-{v}.json.gz' for v in ['v7','v6',tag] if (directory/f'independent-presidential-cells-{v}.json.gz').exists()),None);assert preferred is not None;raw=json.loads(gzip.decompress(preferred.read_bytes()));assert raw['raw_sha256']==source['raw_sha256'];sums=Counter();missing=Counter();conflicts=Counter();totals={};statuses=Counter();native=0;roles=Counter()
        for p in raw['pages']:
            assert sha((BASE/p['raster_path']).read_bytes())==p['raster_sha256']
            for c in p['columns']:
                roles[c['role']]+=1
                if c['role']=='source_native_reporting_constituent':native+=1
                for name,f in c['fields'].items():
                    v=f.get('value');st=f['status'];statuses[st]+=1;allstatus[st]+=1
                    if c['role']=='source_native_reporting_constituent':
                        if v is None:missing[name]+=1
                        else:sums[name]+=v
                        if st=='conflicting_independent_engines_pending_original_review':conflicts[name]+=1
                    elif c['role']=='source_TOTAL':totals[name]=v
                    flat.append(dict(source_id=key,raw_sha256=source['raw_sha256'],county_fips=source['county_fips'],source_page=p['page'],source_column=c['source_column'],literal_native_label=c['native_label_literal'],role=c['role'],candidate=name,OCR_proposal_value=v,accepted_native_transcription=False,status=st,source_full_cell_box_pixels=json.dumps(f.get('full_source_cell_box')),render_size=json.dumps(p['render_size']),full_original_render_path=p['raster_path'],render_sha256=p['raster_sha256'],two_segmentation_readings=json.dumps(f.get('readings')),separate_whole_page_value=f.get('whole_page_vision_value'),raw_aid_path=str(preferred.relative_to(BASE)),raw_aid_sha256=sha(preferred.read_bytes())))
        expected=controls[source['county']]
        if key=='sos-2024-county-pike':expected=dict(zip(NAMES,[a[0] for a in rawpike['president']['candidates']]))
        rows=[]
        for name in NAMES:
            e=expected[name];m=missing[name];s=sums[name];t=totals.get(name);rows.append(dict(candidate=name,numeric_proposal_partial_sum=s,unresolved_native_cells=m,engine_conflicts=conflicts[name],native_sum_complete_as_OCR_proposal=m==0,printed_TOTAL_OCR_proposal=t,source_scoped_named_county_control=e,proposal_minus_county_control=s-e if not m else None,proposal_minus_printed_TOTAL=s-t if not m and t is not None else None,qualification='Partial proposal sums do not treat missing as zero. Even a complete matching OCR sum is not accepted original transcription. Original Pike control differs from updated publication; Tunica printed SEMS disagreement retained, never allocated.'))
        sources.append(dict(source_id=key,raw_sha256=source['raw_sha256'],raw_aid_path=str(preferred.relative_to(BASE)),raw_aid_sha256=sha(preferred.read_bytes()),source_pages=len(raw['pages']),native_columns=native,role_counts=dict(roles),status_counts=dict(statuses),candidate_controls=rows))
    writecsv(OUT/'presidential-original-workbench.csv',flat);save(OUT/'presidential-original-workbench-controls.json',dict(qualification='Own independent original-only workbench, not accepted statewide presidential data. Original Senate source-page partition only, no inferred absence of presidential-only/vendor/method pages; every unresolved/engine-conflict remains explicit. No peer values used or county residual allocated. No current geography join.',source_views=len(sources),original_page_views=sum(s['source_pages'] for s in sources),candidate_numeric_or_null_positions=len(flat),status_counts=dict(allstatus),sources=sources,complete_statewide_nine_presidential_native=False))
    print('Original presidential workbench:',len(sources),'sources;',len(flat),'positions;',dict(allstatus))
if __name__=='__main__':main()
