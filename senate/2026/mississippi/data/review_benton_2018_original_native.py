"""Preserve direct original two-stage readings, without a cross-stage join."""
from pathlib import Path
import csv,gzip,hashlib,io,json
DATA=Path(__file__).resolve().parent
ROOT=DATA.parent
QA=DATA/'coordinator-qa/benton-2018-original-native'
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(ROOT)),bytes=len(b),sha256=sha(b))
def freeze(p):
 q=QA/(p.name+'.gz')
 if q.exists():b=gzip.decompress(q.read_bytes())
 else:b=p.read_bytes();q.write_bytes(gzip.compress(b,mtime=0))
 return b,dict(original=dict(path=str(p.relative_to(ROOT)),bytes=len(b),sha256=sha(b)),lossless_copy=pin(q))
def main():
 raw,jpin=freeze(DATA/'turnout/2018-benton-two-stage-native-original-readings.json')
 flat,cpin=freeze(DATA/'turnout/2018-benton-two-stage-native-original-cells.csv')
 ledger=json.loads(raw);flat=list(csv.DictReader(io.StringIO(flat.decode())));assert len(flat)==66
 headers=['Ashland Precinct District 3','Canaan Precinct District 1','Floyd Precinct Dist 4','Hickory Flat Prec Dist 5','Lamar Precinct District 2','TOTAL','','','','','']
 inputs=[('sos-2018-county-benton','b0e55e9b8b19164409e9447e51c5feef9966c7a6ec1fab932971f7031c56b50b',{'Tobey Bernard Bartee':[12,12,12,5,18,59],'Mike Espy':[240,273,123,77,369,1082],'Cindy Hyde-Smith':[237,167,278,354,106,1142],'Chris McDaniel':[95,68,126,125,44,458]}),('sos-2018-runoff-county-benton','4a7e229da033f7232e9f533a38ff5f9fb6594a6779d8c27c891d2f2f87119fff',{'Mike Espy':[246,336,141,81,420,1224],'Cindy Hyde-Smith':[282,194,362,434,115,1387]})]
 findings=[]
 for sid,expected,vectors in inputs:
  a=next(s for s in ledger['sources']if s['source_id']==sid);p=ROOT/a['source_original_path'];pdf=gzip.decompress(p.read_bytes());assert sha(pdf)==expected==a['source_raw_sha256'];assert a['source_pdf_page']==2 and a['native_constituents']==5 and a['physical_TOTAL_column']==6
  assert a['unused_template_columns']==list(range(7,12));assert pin(ROOT/a['full_original_raster'])['sha256']==a['full_original_raster_sha256']
  rows=[r for r in flat if r['source_id']==sid];assert len(rows)==11*len(vectors)
  for candidate,values in vectors.items():
   assert sum(values[:5])==values[5];values=values+[None]*5
   own=[r for r in a['rows']if r['candidate']==candidate];export=[r for r in rows if r['candidate']==candidate]
   assert [r['physical_source_column']for r in own]==list(range(1,12))
   assert [r['literal_source_header']for r in own]==headers
   assert [r['votes']for r in own]==values
   for col,(r,f,v)in enumerate(zip(own,export,values),1):
    assert r['party_field_literal']=='' and f['party_field_literal']==''
    assert int(f['physical_source_column'])==col and(None if f['votes']==''else int(f['votes']))==v
    assert f['literal_source_header']==headers[col-1] and f['role']==r['role']
    expected_role='source_native_reporting_constituent'if col<6 else'source_TOTAL'if col==6 else'unused_template_column'
    assert r['role']==expected_role
   assert a['candidate_checks'][candidate]['native_sum']==a['candidate_checks'][candidate]['printed_TOTAL']==values[5]
  findings.append(dict(source_id=sid,raw_PDF_sha256=expected,stored_original=pin(p),actual_PDFpage=2,printed_footer_page=2,complete_fresh_coordinator_original_render=pin(QA/(sid+'.png')),render_parameters=dict(renderer='pdftoppm',DPI=130,deskew_rotation_enhancement='none'),physical_headers_in_order=headers,physical_TOTAL_column=6,direct_complete_original_vectors={k:v+[None]*5 for k,v in vectors.items()},unprinted_special_or_runoff_party_fields=None,source_native_columns=5,unused_template_columns=5))
 out=dict(status='pass_bounded_direct_original_Benton2018_two_stages',frozen_worker_inputs=[jpin,cpin],original_findings=findings,numeric_candidate_positions=36,unused_null_positions=30,source_native_observations_across_stages=10,qualification='Fresh complete original PDF2 renders confirm each stage independently. Nov6 regular ClassI Senate above the four-candidate ClassII special is excluded; no party from that other contest is imported into the unprinted special/runoff party fields. Five separately ruled native columns then TOTAL at physical6 and five unused columns are retained. The source-bound worker values were available before this coordinator reread; no prior-blind claim, geographic identity, exact raster/numeric-box equivalence or cross-stage/current join follows.',whole2018_native_complete=False,formal_native887_dispatch_accepted=False,current_geography_approved=False)
 p=DATA/'coordinator-benton-2018-original-native-review.json';b=(json.dumps(out,indent=2)+'\n').encode()
 if p.exists():assert p.read_bytes()==b,'Immutable original review changed'
 else:p.write_bytes(b)
 print(json.dumps(pin(p)))
if __name__=='__main__':main()
