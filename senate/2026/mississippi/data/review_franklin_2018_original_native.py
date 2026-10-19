"""Check original Franklin special/runoff grids, independently of other offices."""
from pathlib import Path
import csv,gzip,hashlib,io,json
DATA=Path(__file__).resolve().parent
ROOT=DATA.parent
QA=DATA/'coordinator-qa/franklin-2018-original-native'
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(ROOT)),bytes=len(b),sha256=sha(b))
def freeze(p):
 q=QA/(p.name+'.gz')
 if q.exists():b=gzip.decompress(q.read_bytes())
 else:b=p.read_bytes();q.write_bytes(gzip.compress(b,mtime=0))
 return b,dict(original=dict(path=str(p.relative_to(ROOT)),bytes=len(b),sha256=sha(b)),lossless_copy=pin(q))
def main():
 jb,jpin=freeze(DATA/'turnout/2018-franklin-two-stage-native-original-readings.json');cb,cpin=freeze(DATA/'turnout/2018-franklin-two-stage-native-original-cells.csv');ledger=json.loads(jb);flat=list(csv.DictReader(io.StringIO(cb.decode())));assert len(flat)==132
 headers=['Antioch','Bad Bayou','Bude','Cains','Eddiceton','Hamburg','Knoxville','Lucien','McCall','Meadville','Pine Grove','Roxie','Wesley Chapel','Whittington','TOTAL']+['']*7
 vectors=[('sos-2018-county-franklin','29d595e1503b8a6223e23a03b49ee127a22d10fd0139d09e2db9b9b2a35531a4',{'Tobey Bernard Bartee':[3,1,8,3,3,7,2,1,0,2,3,12,2,0,47],'Mike Espy':[150,11,292,41,29,136,37,16,46,51,7,198,46,24,1084],'Cindy Hyde-Smith':[116,199,139,114,163,36,45,101,165,178,63,68,27,128,1542],'Chris McDaniel':[30,64,54,30,81,23,30,7,34,64,22,39,6,66,550]}),('sos-2018-runoff-county-franklin','9431e3542e1da39ec565233bc058ac2c219341b1db1bf6be1bd2d62275fedbed',{'Mike Espy':[165,13,350,43,36,154,44,20,49,55,7,233,49,26,1244],'Cindy Hyde-Smith':[139,252,171,138,227,36,80,110,195,219,80,97,28,185,1957]})]
 findings=[]
 for sid,expected,rows in vectors:
  a=next(s for s in ledger['sources']if s['source_id']==sid);p=ROOT/a['source_original_path'];pdf=gzip.decompress(p.read_bytes());assert sha(pdf)==expected==a['source_raw_sha256'];assert a['native_constituents']==14 and a['physical_TOTAL_page']==3 and a['physical_TOTAL_column']==4
  renders=[dict(actual_PDFpage=n,render=pin(QA/f'{sid}-p{n}.png'))for n in [2,3]]
  for name,values in rows.items():
   assert sum(values[:14])==values[14];values=values+[None]*7
   source_rows=[r for r in a['rows']if r['candidate']==name];csv_rows=[r for r in flat if r['source_id']==sid and r['candidate']==name];assert len(source_rows)==len(csv_rows)==22
   assert [r['literal_source_header']for r in source_rows]==headers
   assert [r['votes']for r in source_rows]==values
   assert [(r['source_pdf_page'],r['physical_source_column'])for r in source_rows]==[(n,c)for n in [2,3]for c in range(1,12)]
   for i,(r,c,v)in enumerate(zip(source_rows,csv_rows,values)):
    role='source_native_reporting_constituent'if i<14 else'source_TOTAL'if i==14 else'unused_template_column'
    assert r['role']==c['role']==role
    assert r['party_field_literal']==c['party_field_literal']==''
    assert c['literal_source_header']==headers[i]and(None if c['votes']==''else int(c['votes']))==v
    assert int(c['source_pdf_page'])==r['source_pdf_page']and int(c['physical_source_column'])==r['physical_source_column']
   assert a['candidate_checks'][name]['native_sum']==a['candidate_checks'][name]['printed_TOTAL']==values[14]
  findings.append(dict(source_id=sid,stored_original=pin(p),raw_PDF_sha256=expected,raw_PDF_bytes=len(pdf),actual_PDFpages=[2,3],fresh_full_original_renders=renders,render_parameters=dict(renderer='pdftoppm',DPI=130,deskew_rotation_enhancement='none'),source_native_columns=14,physical_TOTAL=dict(actual_PDFpage=3,column=4),unused_template_columns=dict(actual_PDFpage=3,columns=list(range(5,12))),literal_headers=headers,direct_original_candidate_vectors={k:v+[None]*7 for k,v in rows.items()},unprinted_party_fields=None))
 out=dict(status='pass_bounded_direct_original_Franklin2018_two_stages',frozen_worker_inputs=[jpin,cpin],original_findings=findings,numeric_candidate_positions=90,unused_null_positions=42,source_native_observations_across_stages=28,qualification='Every selected Senate special/runoff field was reread from four fresh complete original PDF2/3 renders. Source transcript/count controls were already known, so no prior-blind claim. Nov6 separately printed ClassI regular Senate and other offices are excluded. Native headers remain literal per source; unprinted selected-office parties stay unknown. Neither matching labels across stages nor physical ordinal gives a geographic/backend ID or current join. This is not a full164-grid history/method/dispatch approval.',whole2018_native_complete=False,formal_native887_dispatch_accepted=False,current_geography_approved=False)
 p=DATA/'coordinator-franklin-2018-original-native-review.json';b=(json.dumps(out,indent=2)+'\n').encode()
 if p.exists():assert p.read_bytes()==b,'Immutable original review changed'
 else:p.write_bytes(b)
 print(json.dumps(pin(p)))
if __name__=='__main__':main()
