"""Direct complete-original Franklin 2018 special and runoff native grids."""
import csv,gzip,io,json
from PIL import Image
import fitz
from acquire_sources import BASE,OUT,receipts,sha,savejson

LABELS={2:['Antioch','Bad Bayou','Bude','Cains','Eddiceton','Hamburg','Knoxville','Lucien','Mccall','Meadville','Pine Grove'],3:['Roxie','Wesley Chapel','Whittington','TOTAL']+['']*7}
STAGES=[
 dict(source_id='sos-2018-county-franklin',date='2018-11-06',office='United States-Senate Special',candidate_values={
  'Tobey Bernard Bartee':{2:[3,1,8,3,3,7,2,1,0,2,3],3:[12,2,0,47]+[None]*7},
  'Mike Espy':{2:[150,11,292,41,29,136,37,16,46,51,7],3:[198,46,24,1084]+[None]*7},
  'Cindy Hyde-Smith':{2:[116,199,139,114,163,36,45,101,165,178,63],3:[68,27,128,1542]+[None]*7},
  'Chris McDaniel':{2:[30,64,54,30,81,23,30,7,34,64,22],3:[39,6,66,550]+[None]*7}}),
 dict(source_id='sos-2018-runoff-county-franklin',date='2018-11-27',office='United States-Senate Unexpired Term',candidate_values={
  'Mike Espy':{2:[165,13,350,43,36,154,44,20,49,55,7],3:[233,49,26,1244]+[None]*7},
  'Cindy Hyde-Smith':{2:[139,252,171,138,227,36,80,110,195,219,80],3:[97,28,185,1957]+[None]*7}}),
]

def build():
    controls=[r for r in csv.DictReader((OUT/'historical-county-candidate-votes.csv').open()) if r['fips']=='28037' and r['election_date'] in ('2018-11-06','2018-11-27')]
    sources=[];flat=[]
    for stage in STAGES:
        sid=stage['source_id'];receipt=next(r for r in receipts if r['id']==sid)
        raw=gzip.decompress((BASE/receipt['path']).read_bytes());assert sha(raw)==receipt['raw_sha256']
        doc=fitz.open(stream=raw,filetype='pdf');assert len(doc)>=3
        pages={}
        for page in (2,3):
            im=Image.open(io.BytesIO(doc[page-1].get_pixmap(matrix=fitz.Matrix(2.2,2.2),colorspace=fitz.csGRAY).tobytes('png')))
            raster=OUT/'qa/2018-native-original-probe'/sid/f'p{page:04d}-original.png';raster.parent.mkdir(parents=True,exist_ok=True);im.save(raster)
            pages[page]=dict(source_pdf_page=page,original_raster=str(raster.relative_to(BASE)),raster_sha256=sha(raster.read_bytes()),render_size=list(im.size))
        rows=[];candidate_checks={}
        for candidate,by_page in stage['candidate_values'].items():
            assert set(by_page)=={2,3} and all(len(by_page[p])==11 for p in (2,3))
            native_sum=sum(by_page[2])+sum(by_page[3][:3]);printed_total=by_page[3][3]
            assert by_page[3][4:]==[None]*7 and native_sum==printed_total,(sid,candidate,native_sum,printed_total)
            ctl=next(r for r in controls if r['source_id']==sid and r['candidate']==candidate)
            assert int(ctl['votes'])==printed_total and ctl['raw_sha256']==receipt['raw_sha256'] and int(ctl['source_page'])==3,(sid,candidate,ctl)
            candidate_checks[candidate]=dict(native_sum=native_sum,printed_TOTAL=printed_total,county_control=ctl['votes'],passes=True)
            for page in (2,3):
                for j,(label,v) in enumerate(zip(LABELS[page],by_page[page]),1):
                    role='source_native_reporting_constituent' if page==2 or j<=3 else 'source_TOTAL' if j==4 else 'unused_template_column'
                    assert (role=='unused_template_column' and label=='' and v is None) or (role!='unused_template_column' and label and isinstance(v,int))
                    rows.append(dict(source_id=sid,election_date=stage['date'],county='Franklin',county_fips='28037',source_raw_sha256=receipt['raw_sha256'],source_pdf_page=page,physical_source_column=j,source_native_key=f'28037:{sid}:p{page}:c{j}',literal_source_header=label,role=role,office_context_literal=stage['office'],candidate=candidate,party_field_literal='',votes=v,original_raster=pages[page]['original_raster'],reading_basis='direct_complete_original_page_visual' if v is not None else 'visibly_unprinted_template_cell'))
        assert len(rows)==22*len(stage['candidate_values']) and all(c['passes'] for c in candidate_checks.values())
        sources.append(dict(source_id=sid,election_date=stage['date'],contest=stage['office'],source_raw_sha256=receipt['raw_sha256'],source_original_path=receipt['path'],source_pdf_page_count=len(doc),pages=[pages[p] for p in (2,3)],physical_source_columns_per_page=11,native_constituents=14,physical_TOTAL_page=3,physical_TOTAL_column=4,unused_template_columns_page3=[5,6,7,8,9,10,11],candidate_checks=candidate_checks,rows=rows,scope='Source-native identities only; no cross-stage or current geographic join. Nov6 regular ClassI Wicker/Baria contest remains separate on the complete original.'))
        flat.extend(rows)
    savejson(OUT/'2018-franklin-two-stage-native-original-readings.json',dict(scope='Two distinct 2018 ClassII special-election stages; Nov6 regular ClassI Senate pool stays only in complete original PDF.',sources=sources,total_candidate_positions=len(flat),native_constituents_per_stage=14))
    with (OUT/'2018-franklin-two-stage-native-original-cells.csv').open('w',newline='') as f:
        fields=list(flat[0]);w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(flat)
    print('2018 Franklin distinct special stages',len(flat),'candidate positions; physical TOTAL page3 column4 each')

if __name__=='__main__':build()
