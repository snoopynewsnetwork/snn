"""Direct complete-original 2018 special/runoff native readings, separate electorates.

Literal candidate glyphs/headers below are independently typed from complete
retained originals. Positions restore actual physical columns, never merged
machine-grid ordinals. Other offices remain in complete original bytes.
"""
import csv,gzip,json
from collections import Counter
from sources import OUT,BASE,original,save,sha
from build_counties import writecsv

NAMES={'special':['Tobey Bernard Bartee','Mike Espy','Cindy Hyde-Smith','Chris McDaniel'],'runoff':['Mike Espy','Cindy Hyde-Smith']}
LABELS=['Addie Voting Precinct','Grace Voting Precinct','Mayersville\nCourthouse','Tallula Community\nCenter','Valley Park\nCommunity Center','TOTAL','','','','','']
VALUES={
 'sos-2018-county-issaquena':dict(stage='special',page=2,x=[728,848,967,1088,1206,1326,1445,1565,1685,1805,1923,2034],header_y=[262,492],row_y=[[837,898],[898,953],[953,1007],[1007,1063]],values=[[0,1,3,0,1,5],[75,40,115,57,18,305],[41,60,10,57,49,217],[6,8,1,9,9,33]],prior_machine_TOTAL_column=4),
 'sos-2018-runoff-county-issaquena':dict(stage='runoff',page=2,x=[726,847,964,1084,1204,1324,1444,1562,1681,1801,1920,2034],header_y=[259,490],row_y=[[550,612],[612,667]],values=[[70,38,120,54,23,305],[42,60,9,60,56,227]],prior_machine_TOTAL_column=6)}

def main():
    priorpin=json.loads((OUT/'source/2018-physical-column-corrections-v1/prior-ledger-pin.json').read_text());stored=(BASE/priorpin['stored_path']).read_bytes();assert sha(stored)==priorpin['stored']['sha256'];prior=gzip.decompress(stored);assert sha(prior)==priorpin['original']['sha256'];controls={r['source_id']:r for r in json.loads(prior)['readings']}
    readings=[];rows=[];counts=Counter();reviewed={}
    for sid,p in VALUES.items():
        stage=p['stage'];names=NAMES[stage];raw=original(sid);pg=p['page'];receipt=json.loads((OUT/'qa/historical-native-originals'/sid/f'p{pg:04d}-render.json').read_text());raster=BASE/receipt['full_original_render_path'];assert sha(raw)==receipt['raw_sha256'] and sha(raster.read_bytes())==receipt['render_sha256'];w,h=receipt['render_size'];xs=p['x'];assert len(xs)==12 and 0<=xs[0]<xs[-1]<=w
        columns=[dict(source_column=i+1,label_literal=label,literal_printed_id=None,role='native' if i<5 else 'TOTAL' if i==5 else 'unused',header_bounds=[xs[i],p['header_y'][0],xs[i+1],p['header_y'][1]]) for i,label in enumerate(LABELS)];fields=[];sums={}
        for name,vs,ys in zip(names,p['values'],p['row_y']):
            assert sum(vs[:5])==vs[5];sums[name]=vs[5];vs=vs+[None]*5;fields.append(dict(candidate=name,party_literal=None,party_qualification='No party label printed beside the selected special/runoff candidate row; candidate identity retained without merging party pools.',values=vs,row_bounds=[xs[0],ys[0],xs[-1],ys[1]],basis='Direct complete original page glyph reading'))
            for col,v in zip(columns,vs):
                counts['numeric_positions' if v is not None else 'unused_null_positions']+=1
                rows.append(dict(source_id=sid,source_raw_sha256=sha(raw),county_fips='28055',stage=stage,source_page=pg,source_column=col['source_column'],source_key=f'{sid}:p{pg}:c{col["source_column"]}',role=col['role'],literal_native_label=col['label_literal'],literal_printed_id=None,candidate=name,party_literal=None,votes=v,header_bounds_pixels=json.dumps(col['header_bounds']),candidate_reading_window_pixels=json.dumps([col['header_bounds'][0],ys[0],col['header_bounds'][2],ys[1]]),full_original_render_path=receipt['full_original_render_path'],render_sha256=receipt['render_sha256']))
        assert sums==controls[sid]['candidate_values'];counts['source_views']+=1;counts['native_constituents_across_separate_stages']+=5;counts['TOTAL_columns']+=1;counts['unused_columns']+=5
        page=dict(page=pg,render_size=receipt['render_size'],full_original_render_path=receipt['full_original_render_path'],render_sha256=receipt['render_sha256'],columns=columns,fields=fields,source_position_qualification='Five independently visible named columns thenTOTALphysical6. Source-specific reading windows, not geographic boundaries/current IDs. Same labels in two stages do not establish a joined electorate or identity crosswalk.')
        readings.append(dict(source_id=sid,raw_sha256=sha(raw),stage=stage,pages=[page],controls=dict(native_candidate_sums=sums,printed_TOTAL=sums,all_vectors_close=True),physical_TOTAL_column=6,prior_machine_TOTAL_column=p['prior_machine_TOTAL_column'],qualification='Special four-candidate and runoff two-candidate electorates retained separately. All unprinted generic/method/ballot/registration fields unknown. Complete original includes unrelated offices.'));reviewed[sid]=True
    inventory=[]
    for sid,c in controls.items():
        inventory.append(dict(source_id=sid,stage=c['stage'],native_original_review_complete=sid in reviewed,reviewed_native_count=5 if sid in reviewed else None,qualification='Source-specific original scope' if sid in reviewed else 'Native count/fields unknown until original review; not zero, county replacement or another-stage/year join'))
    assert len(inventory)==164
    save(OUT/'native-2018-original-readings.json',dict(sources=readings,counts=dict(counts),all164_source_status=inventory,complete2018_native=False,current2026_geography_approved=False));writecsv(OUT/'native-2018-original-candidate-votes.csv',rows)
    print('2018 bounded original-native',dict(counts))
if __name__=='__main__':main()
