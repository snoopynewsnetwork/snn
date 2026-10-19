"""Independent original Winston all11 native vectors, including explicit zeros.

Two complete original pages read directly; no peer values or residual fitting.
Original gray scan/failed OCR aids remain untouched. All null columns observed.
"""
import csv,json
from collections import Counter
from sources import OUT,BASE,save,sha,original
from extract_replay_president import NAMES,manual_row
from extract_native import cell_key
from build_counties import writecsv
NAMES=NAMES+['Ty Pinkins','Roger F. Wicker']
P2=[
[557,721,143,419,146,200,342,151,95,200,92],
[1,1,1,2,0,0,2,0,0,0,1],
[1,1,1,4,1,1,3,0,0,0,0],
[2,2,1,1,0,0,0,1,0,0,0],
[139,168,395,956,187,356,713,903,265,522,261],
[2,0,0,0,1,0,0,3,0,0,0],
[0,0,0,0,0,0,1,0,0,0,0],
[2,7,2,3,2,2,4,3,2,1,2],
[0,0,0,2,0,1,1,0,0,0,0],
[560,730,149,436,152,198,344,161,95,203,94],
[148,168,394,952,188,361,722,890,263,517,264]]
P3=[[326,3392],[0,8],[0,12],[1,8],[57,4922],[0,6],[0,1],[1,31],[0,4],[317,3439],[70,4937]]
LABELS=['American Legion','County Agent','East Winston','Fairground','Lovorn Tractor','Mars Hill','Mill Creek','Nanih Waiya','New National Guard','Noxapater','Shiloh']
def main():
    sid='sos-2024-county-winston';ledger=json.loads((OUT/'native-2024-senate-reviewed-84views.json').read_text());s=next(s for s in ledger['sources'] if s['source_id']==sid);assert sha(original(sid))==s['raw_sha256'];pages=[];flat=[];sums=Counter();total={};null=0
    for p,values in zip(s['pages'],[P2,[v+[None]*9 for v in P3]]):
        assert p['page'] in [2,3];path=OUT/'extracts/reviewed-replay'/sid/f'p{p["page"]:04d}-original.png';raw=json.loads(__import__('gzip').decompress((path.with_name(f'p{p["page"]:04d}.json.gz')).read_bytes()));assert sha(path.read_bytes())==raw['raster_sha256'];fields=[];labels=LABELS if p['page']==2 else ['Zion Ridge','TOTAL']+['']*9;roles=['source_native_reporting_constituent']*11 if p['page']==2 else ['source_native_reporting_constituent','source_TOTAL']+['unused_template_column']*9
        for name,vs in zip(NAMES,values):
            assert len(vs)==11
            row=manual_row(sid,p['page'],name,'v5') if name not in ['Ty Pinkins','Roger F. Wicker'] else None;fields.append(dict(candidate=name,values=vs,whole_original_row_window=row['row_bounds'] if row else None,row_window_scope='Original visually reviewed complete-field window, not exact source-boundary polygon' if row else 'Senate source candidate boxes retained per native column in frozen source ledger',basis='Every printed numeric glyph directly read from complete original page; explicit printed zero or unused blank, never a county residual or peer derivative'))
            for i,(v,label,role,c) in enumerate(zip(vs,labels,roles,p['columns']),1):
                assert label==c['label_literal'];assert role==c['role']
                if role=='source_native_reporting_constituent':assert isinstance(v,int);sums[name]+=v
                elif role=='source_TOTAL':assert isinstance(v,int);total[name]=v
                else:assert v is None;null+=1
                box=[c['header_bounds'][0],row['row_bounds'][1],c['header_bounds'][2],row['row_bounds'][3]] if row else c['fields'][name]['source_box'];flat.append(dict(key=f'28159:{sid}:p{p["page"]}:c{i}',source_id=sid,raw_sha256=s['raw_sha256'],county_fips='28159',source_page=p['page'],source_column=i,label_literal=label,role=role,candidate=name,value=v,source_reading_box_pixels=json.dumps(box),render_size=json.dumps(p['render_size']),full_original_render_path=str(path.relative_to(BASE)),render_sha256=raw['raster_sha256'],basis='Independent direct full-original page reading; whole-row field windows approximate, no current identity inference'))
        pages.append(dict(page=p['page'],render_size=p['render_size'],rotation_ccw=p['rotation_ccw'],deskew_angle_ccw=p['deskew_angle_ccw'],full_original_render_path=str(path.relative_to(BASE)),render_sha256=raw['raster_sha256'],labels_literal=labels,roles=roles,fields=fields,generic_write_in_marks=None,under_over_blank_ballots_registration=None,qualification='Unprinted controls remain unknown, not zeros or inferred from named votes.'))
    controls={}
    for r in csv.DictReader((OUT/'candidate-votes.csv').open()):
        if r['county']=='Winston' and r['contest'] in ['2024-president','2024-senate']:controls[cell_key(r['candidate_literal'])]=int(r['votes'])
    assert len(controls)==11 and dict(sums)==total==controls,(sums,total,controls);assert null==99
    save(OUT/'winston-native-allfield-readings.json',dict(source_id=sid,raw_sha256=s['raw_sha256'],county_fips='28159',qualification='Complete two original SEMS pages independently visually read: all11 candidate vectors,12 native constituents,one nonadditive TOTAL,nine unused blank columns. Native candidates132+TOTAL11=143numeric;99 unused/null positions. This is a separate accepted original reading, not numerical acceptance of failed gray-scan OCR derivatives. No generic write-in or turnout/reg field is assumed absent elsewhere. No current geography or full-state acceptance.',pages=pages,controls=dict(native_constituents=12,candidate_numeric_positions=143,unused_null_positions=99,native_candidate_sums=dict(sums),printed_TOTAL=total,source_scoped_named_county_controls=controls,all11_vectors_close=True)))
    writecsv(OUT/'winston-native-allfield-candidate-votes.csv',flat);print('Winston original12native,11candidate vectors;143numeric+99null; all11 primary county controls close')
if __name__=='__main__':main()
