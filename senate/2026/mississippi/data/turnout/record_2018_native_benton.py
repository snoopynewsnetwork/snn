"""Separate direct-original Benton 2018 special and runoff native grids."""
import csv,gzip,io,json
from PIL import Image
import fitz
from acquire_sources import BASE,OUT,receipts,sha,savejson

LABELS=['Ashland Precinct District 3','Canaan Precinct District 1','Floyd Precinct Dist 4','Hickory Flat Prec Dist 5','Lamar Precinct District 2','TOTAL']+['']*5
STAGES=[
 dict(source_id='sos-2018-county-benton',date='2018-11-06',office='United States-Senate Special',candidate_values={
  'Tobey Bernard Bartee':[12,12,12,5,18,59]+[None]*5,
  'Mike Espy':[240,273,123,77,369,1082]+[None]*5,
  'Cindy Hyde-Smith':[237,167,278,354,106,1142]+[None]*5,
  'Chris McDaniel':[95,68,126,125,44,458]+[None]*5}),
 dict(source_id='sos-2018-runoff-county-benton',date='2018-11-27',office='United States-Senate Unexpired Term',candidate_values={
  'Mike Espy':[246,336,141,81,420,1224]+[None]*5,
  'Cindy Hyde-Smith':[282,194,362,434,115,1387]+[None]*5}),
]

def build():
    controls=[r for r in csv.DictReader((OUT/'historical-county-candidate-votes.csv').open()) if r['fips']=='28009' and r['election_date'] in ('2018-11-06','2018-11-27')]
    sources=[];flat=[]
    for stage in STAGES:
        sid=stage['source_id'];receipt=next(r for r in receipts if r['id']==sid)
        raw=gzip.decompress((BASE/receipt['path']).read_bytes());assert sha(raw)==receipt['raw_sha256']
        doc=fitz.open(stream=raw,filetype='pdf');im=Image.open(io.BytesIO(doc[1].get_pixmap(matrix=fitz.Matrix(2.2,2.2),colorspace=fitz.csGRAY).tobytes('png')))
        raster=OUT/'qa/2018-native-original-probe'/sid/'p0002-original.png';raster.parent.mkdir(parents=True,exist_ok=True);im.save(raster)
        rows=[];candidate_checks={}
        for candidate,values in stage['candidate_values'].items():
            assert len(values)==11 and all(isinstance(v,int) for v in values[:6]) and values[6:]==[None]*5
            native_sum=sum(values[:5]);printed_total=values[5];assert native_sum==printed_total
            ctl=next(r for r in controls if r['source_id']==sid and r['candidate']==candidate)
            assert int(ctl['votes'])==printed_total and ctl['raw_sha256']==receipt['raw_sha256'] and int(ctl['source_page'])==2
            candidate_checks[candidate]=dict(native_sum=native_sum,printed_TOTAL=printed_total,county_control=ctl['votes'],passes=True)
            for j,(label,v) in enumerate(zip(LABELS,values),1):
                role='source_native_reporting_constituent' if j<=5 else 'source_TOTAL' if j==6 else 'unused_template_column'
                rows.append(dict(source_id=sid,election_date=stage['date'],county='Benton',county_fips='28009',source_raw_sha256=receipt['raw_sha256'],source_pdf_page=2,physical_source_column=j,source_native_key=f'28009:{sid}:p2:c{j}',literal_source_header=label,role=role,office_context_literal=stage['office'],candidate=candidate,party_field_literal='',votes=v,original_raster=str(raster.relative_to(BASE)),reading_basis='direct_complete_original_page_visual' if v is not None else 'visibly_unprinted_template_cell'))
        assert len(rows)==11*len(stage['candidate_values']) and all(c['passes'] for c in candidate_checks.values())
        sources.append(dict(source_id=sid,election_date=stage['date'],contest=stage['office'],source_raw_sha256=receipt['raw_sha256'],source_original_path=receipt['path'],source_pdf_page=2,source_pdf_page_count=len(doc),full_original_raster=str(raster.relative_to(BASE)),full_original_raster_sha256=sha(raster.read_bytes()),render_size=list(im.size),physical_source_columns=11,native_constituents=5,physical_TOTAL_column=6,unused_template_columns=[7,8,9,10,11],candidate_checks=candidate_checks,rows=rows,scope='Source-native identities only; no cross-stage or current geographic join. Nov6 regular ClassI Wicker/Baria pool is separate on the same original page.'))
        flat.extend(rows)
    savejson(OUT/'2018-benton-two-stage-native-original-readings.json',dict(scope='Two distinct 2018 ClassII special-election stages; Nov6 regular ClassI Senate pool stays only in complete original PDF.',sources=sources,total_candidate_positions=len(flat),native_constituents_per_stage=5))
    with (OUT/'2018-benton-two-stage-native-original-cells.csv').open('w',newline='') as f:
        fields=list(flat[0]);w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(flat)
    print('2018 Benton distinct special stages',len(flat),'candidate positions; physical TOTAL column6 each')

if __name__=='__main__':build()
