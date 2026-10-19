"""Direct source-native reads of both separate 2018 Issaquena special stages.

Nov6 PDF also prints a regular Class I Senate contest. Only the distinct
special-election four-candidate block is transcribed here; the complete
source PDF retains the other office without mixing candidate pools.
"""
import csv,gzip,io,json
from PIL import Image
import fitz
from acquire_sources import BASE,OUT,receipts,sha,savejson

LABELS=['Addie Voting Precinct','Grace Voting Precinct','Mayersville Courthouse','Tallula Community Center','Valley Park Community Center','TOTAL']+['']*5
STAGES=[
 dict(source_id='sos-2018-county-issaquena',date='2018-11-06',office='United States-Senate Special',candidate_values={
  'Tobey Bernard Bartee':[0,1,3,0,1,5]+[None]*5,
  'Mike Espy':[75,40,115,57,18,305]+[None]*5,
  'Cindy Hyde-Smith':[41,60,10,57,49,217]+[None]*5,
  'Chris McDaniel':[6,8,1,9,9,33]+[None]*5},old_machine_total_ordinal=4),
 dict(source_id='sos-2018-runoff-county-issaquena',date='2018-11-27',office='United States-Senate Unexpired Term',candidate_values={
  'Mike Espy':[70,38,120,54,23,305]+[None]*5,
  'Cindy Hyde-Smith':[42,60,9,60,56,227]+[None]*5},old_machine_total_ordinal=6),
]

def build():
    controls=[r for r in csv.DictReader((OUT/'historical-county-candidate-votes.csv').open()) if r['fips']=='28055' and r['election_date'] in ('2018-11-06','2018-11-27')]
    sources=[];flat=[]
    for stage in STAGES:
        sid=stage['source_id'];receipt=next(r for r in receipts if r['id']==sid)
        raw=gzip.decompress((BASE/receipt['path']).read_bytes());assert sha(raw)==receipt['raw_sha256']
        doc=fitz.open(stream=raw,filetype='pdf');page=doc[1]
        im=Image.open(io.BytesIO(page.get_pixmap(matrix=fitz.Matrix(2.2,2.2),colorspace=fitz.csGRAY).tobytes('png')))
        raster=OUT/'qa/2018-native-original-probe'/sid/'p0002-original.png';raster.parent.mkdir(parents=True,exist_ok=True);im.save(raster)
        rows=[];candidate_checks={}
        for candidate,values in stage['candidate_values'].items():
            assert len(values)==11 and all(isinstance(v,int) for v in values[:6]) and values[6:]==[None]*5
            native_sum=sum(values[:5]);printed_total=values[5]
            assert native_sum==printed_total
            ctl=next(r for r in controls if r['source_id']==sid and r['candidate']==candidate)
            assert int(ctl['votes'])==printed_total and ctl['raw_sha256']==receipt['raw_sha256'] and int(ctl['source_page'])==2
            candidate_checks[candidate]=dict(native_sum=native_sum,printed_TOTAL=printed_total,county_control=ctl['votes'],passes=True)
            for j,(label,v) in enumerate(zip(LABELS,values),1):
                role='source_native_reporting_constituent' if j<=5 else 'source_TOTAL' if j==6 else 'unused_template_column'
                rows.append(dict(source_id=sid,election_date=stage['date'],county='Issaquena',county_fips='28055',source_raw_sha256=receipt['raw_sha256'],source_pdf_page=2,physical_source_column=j,source_native_key=f'28055:{sid}:p2:c{j}',literal_source_header=label,role=role,office_context_literal=stage['office'],candidate=candidate,party_field_literal='',votes=v,original_raster=str(raster.relative_to(BASE)),reading_basis='direct_complete_original_page_visual' if v is not None else 'visibly_unprinted_template_cell'))
        assert len(rows)==11*len(stage['candidate_values'])
        assert all(c['passes'] for c in candidate_checks.values())
        sources.append(dict(source_id=sid,election_date=stage['date'],contest=stage['office'],source_raw_sha256=receipt['raw_sha256'],source_original_path=receipt['path'],source_pdf_page=2,source_pdf_page_count=len(doc),full_original_raster=str(raster.relative_to(BASE)),full_original_raster_sha256=sha(raster.read_bytes()),render_size=list(im.size),physical_source_columns=11,native_constituents=5,physical_TOTAL_column=6,unused_template_columns=[7,8,9,10,11],prior_county_control_machine_TOTAL_ordinal=stage['old_machine_total_ordinal'],machine_vs_physical_qualification='Nov6 native-v4 raw aid merged three adjacent headers, so old machine ordinal4 targets the same actual physical TOTAL column6. Runoff source independently prints physical6.',candidate_checks=candidate_checks,rows=rows))
        flat.extend(rows)
    savejson(OUT/'2018-issaquena-two-stage-native-original-readings.json',dict(scope='Two distinct 2018 ClassII special-election stages; Nov6 ClassI regular Senate pool stays only in complete original PDF. Physical native positions are stage/source-specific and do not imply cross-stage/current identity.',sources=sources,total_candidate_positions=len(flat),native_constituents_per_stage=5))
    with (OUT/'2018-issaquena-two-stage-native-original-cells.csv').open('w',newline='') as f:
        fields=list(flat[0]);w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(flat)
    print('2018 Issaquena distinct special stages',len(flat),'candidate positions; original physical TOTAL column6 each, Nov6 old machine ordinal4 separately qualified')

if __name__=='__main__':build()
