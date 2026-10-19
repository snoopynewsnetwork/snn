"""Reconcile all104 actual county publications without assuming a uniform vintage.

Manual original readings remain immutable inputs. This compares county TOTALs;
it does not establish complete native sums, chronology or current geography.
"""
import csv,json
from collections import Counter,defaultdict
from sources import OUT,BASE,references,original,sha,save
from build_counties import writecsv
NAMES=['Mike Espy','Cindy Hyde-Smith','Jimmy L. Edwards']
def main():
    refs=references();inputs=['county-2020-readings.json','county-2020-repair-readings.json'];rows=[]
    for fn in inputs:
        p=OUT/fn;x=json.loads(p.read_text())
        for r in x['readings']:
            key=r['source_id'];assert sha(original(key))==r['raw_sha256'];assert len(r['candidate_values'])==3
            evidence=OUT/r['evidence_path'];assert sha(evidence.read_bytes())==r['evidence_sha256']
            label=key.removeprefix('sos-2020-county-').removesuffix('-amended');label='jeff-davis' if label=='jefferson-davis' else label
            rows.append(dict(source_id=key,county_key=label,publication_label=refs[key]['source_label'],publication_variant='Amended' if key.endswith('-amended') else 'original county-index publication',requested_url=refs[key]['url'],final_url=refs[key]['final_url'],parent_source_id=refs[key]['parent_source_id'],raw_sha256=r['raw_sha256'],raw_bytes=refs[key]['raw_bytes'],source_page=r['page'],source_column_accepted=r.get('source_column_accepted'),source_column_proposed=r.get('source_column_proposed'),source_column_qualification='Accepted physical TOTAL ordinal from complete original header' if r.get('source_column_accepted') is not None else 'Numeric TOTAL cells visually read; physical ordinal remains unaccepted targeting proposal',candidate_values=r['candidate_values'],county_csv_control=r['county_csv_control'],county_csv_difference=r['county_csv_difference'],manual_input=fn,manual_input_sha256=sha(p.read_bytes()),evidence_path=r['evidence_path'],evidence_sha256=r['evidence_sha256'],original_positions={k:r[k] for k in ['original_header_box','original_candidate_block_box','raster_path','raster_sha256','render_size','rotation_ccw','deskew_angle_ccw','candidate_rows','total_bounds'] if k in r}))
    ids=[r['source_id'] for r in rows];assert len(ids)==len(set(ids))==104
    expected={k for k in refs if k.startswith('sos-2020-county-') and k!='sos-2020-county-index'};assert set(ids)==expected
    groups=defaultdict(list)
    for r in rows:groups[r['county_key']].append(r)
    assert len(groups)==82 and sum(len(v)==2 for v in groups.values())==22
    selected=[];originals=[];changes=[]
    for county,views in sorted(groups.items()):
        before=next(r for r in views if r['publication_variant']=='original county-index publication');originals.append(before)
        after=next((r for r in views if r['publication_variant']=='Amended'),before);selected.append(after)
        assert after['candidate_values']==after['county_csv_control'],(county,after['candidate_values'],after['county_csv_control'])
        if len(views)==2:
            delta={n:after['candidate_values'][n]-before['candidate_values'][n] for n in NAMES}
            changes.append(dict(county_key=county,original_source_id=before['source_id'],amended_source_id=after['source_id'],original_page=before['source_page'],amended_page=after['source_page'],original_candidate_values=before['candidate_values'],amended_candidate_values=after['candidate_values'],amended_minus_original=delta,changed=any(delta.values())))
    def totals(rs):return {n:sum(r['candidate_values'][n] for r in rs) for n in NAMES}
    states=json.loads((OUT/'source/primary-state-readings.json').read_text());origstate=states['2020-senate-original']['candidates'];amstate=states['2020-senate']['candidates'];a=totals(originals);b=totals(selected);assert b==amstate
    controls=dict(source_publications=104,county_coverage=82,amended_alternatives=22,original_read_candidate_fields=312,accepted_physical_TOTAL_ordinals=sum(r['source_column_accepted'] is not None for r in rows),unaccepted_physical_TOTAL_ordinals=sum(r['source_column_accepted'] is None for r in rows),all_original_county_publications_candidate_sum=a,all_original_county_publications_minus_original_state_summary={n:a[n]-origstate[n] for n in NAMES},amended_where_explicit_otherwise_original_candidate_sum=b,amended_where_explicit_otherwise_original_minus_amended_state_summary={n:b[n]-amstate[n] for n in NAMES},all82_selected_publications_match_each_county_CSV=True,changed_county_publications=[r for r in changes if r['changed']],state_summary_original_to_amended={n:amstate[n]-origstate[n] for n in NAMES},source_vintage_warning='Coahoma alone equals the statewide summary change vector, but Adams and Prentiss are additional explicit county publication changes. All-original county publications do not balance to the original statewide summary. No chronology, residual allocation or common vintage is inferred.',county_TOTAL_only_scope=True,complete_historical_native_review=False)
    save(OUT/'county-2020-publication-controls.json',dict(qualification='Complete actual104-publication three-candidate printed countyTOTAL audit. Original/Amended versions retained separately. Numeric acceptance is separate from physical ordinal acceptance and from full native/method coverage.',controls=controls,all22_original_amended_comparisons=changes,readings=sorted(rows,key=lambda r:r['source_id'])))
    flat=[]
    for r in rows:
        for n in NAMES:flat.append({k:v for k,v in r.items() if k not in ['candidate_values','county_csv_control','county_csv_difference','original_positions']}|dict(candidate=n,votes=r['candidate_values'][n],county_csv_votes=r['county_csv_control'][n],county_csv_difference=r['county_csv_difference'][n],original_positions=json.dumps(r['original_positions'],ensure_ascii=False)))
    writecsv(OUT/'county-2020-publication-candidate-votes.csv',flat);print(json.dumps(controls,indent=2))
if __name__=='__main__':main()
