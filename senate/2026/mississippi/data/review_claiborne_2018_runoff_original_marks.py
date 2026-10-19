"""Direct complete-original check of four literal X cells and distinct precincts."""
from pathlib import Path
import gzip,hashlib,json
DATA=Path(__file__).resolve().parent
ROOT=DATA.parent
QA=DATA/'coordinator-qa/claiborne-2018-runoff-source-marks'
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(ROOT)),bytes=len(b),sha256=sha(b))
def main():
 sid='sos-2018-runoff-county-claiborne';expected='9818491065e1d3d9fcd0825c1060881018d4474dbd7989d6ecd305f727bada5e'
 ref=next(x for x in json.loads((DATA/'baselines/source/references.json').read_bytes())if x['id']==sid);original=ROOT/ref['path'];pdf=gzip.decompress(original.read_bytes());assert sha(pdf)==expected and len(pdf)==706253
 labels=['County Precinct '+x for x in ['1-A','1-B','1-C','2-A','2-B','3-A','3-B','4-A','4-B','4-C','4-D','5-A','5-B']]
 vectors={'Mike Espy':[469,192,None,331,170,557,17,268,366,None,19,363,343],'Cindy Hyde-Smith':[75,0,None,53,20,119,17,15,34,None,58,19,43]}
 totals={'Mike Espy':3095,'Cindy Hyde-Smith':453}
 assert {n:sum(v for v in vs if v is not None)for n,vs in vectors.items()}==totals
 snap=DATA/'baselines/source/native-2018-40views-v1/snapshot.json';manifest=json.loads(snap.read_bytes());a=next(x for x in manifest['pins']if x['original_path'].endswith('native-2018-original-readings.json'));raw=gzip.decompress((ROOT/a['stored_path']).read_bytes());assert sha(raw)==a['original_sha256'];s=next(s for s in json.loads(raw)['sources']if s['source_id']==sid)
 source_positions=[]
 for n,vs in vectors.items():
  represented=[]
  for p in s['pages']:
   f=next(f for f in p['fields']if f['candidate']==n)
   for c,v in zip(p['columns'],f['values']):
    if c['role']=='native':represented.append((p['page'],c['source_column'],c['label_literal'],v,f.get('source_marks',{}).get(str(c['source_column']))))
    elif c['role']=='TOTAL':assert v==totals[n]
    else:assert c['role']=='unused' and v is None
  assert len(represented)==13
  for i,(page,col,label,value,mark)in enumerate(represented):
   assert label==labels[i] and value==vs[i]
   assert (page,col)==((2,i+1)if i<11 else(3,i-10))
   assert mark==('X'if i in[2,9]else None)
   source_positions.append(dict(candidate=n,actual_PDFpage=page,physical_column=col,literal_source_header=labels[i],numerical_value=vs[i],raw_source_mark=mark))
 out=dict(status='pass_bounded_direct_original_Claiborne2018_runoff_X_marks_and_vectors',source_id=sid,raw_original_bytes=len(pdf),raw_original_sha256=expected,stored_original=pin(original),fresh_complete_original_renders=[pin(QA/f'pdf{p}-complete-original.png')for p in[2,3]],render_parameters=dict(renderer='pdftoppm',DPI=160,deskew_rotation_enhancement='none'),immutable_worker40_snapshot=pin(snap),literal_source_native_headers=labels,source_candidate_positions=source_positions,printed_TOTAL=dict(actual_PDFpage=3,physical_column=3,values=totals),source_native_observations=13,numerically_observed_native_columns=11,marked_native_columns=2,marked_candidate_positions=4,numeric_candidate_positions_including_TOTAL=24,unused_null_positions=16,source_page_margin_clocks=[dict(actual_PDFpage=2,literal_time='10:03:54 p.m.',literal_date='12-06-2018',timezone=None),dict(actual_PDFpage=3,literal_time='10:04:17 p.m.',literal_date='12-06-2018',timezone=None)],qualification='Both complete hash-checked actual PDF2/3 originals were freshly rendered and visually read after the worker exception was known. CountyPrecinct1-C and4-C are actual separately printed source columns with literal X in both Senate rows; numerical null preserves the unproved value/meaning rather than assigning zero or a status. The eleven other numeric native columns close3095/453 without allocating the marks. Source margin clocks are not established publication/retrieval clocks. No native identity across Nov6/runoff/current geography, exact numeric polygon, whole164-grid history/method or native887dispatch acceptance follows.',formal_native887_dispatch_accepted=False,current_geography_approved=False)
 p=DATA/'coordinator-claiborne-2018-runoff-original-marks-review.json';b=(json.dumps(out,indent=2)+'\n').encode()
 if p.exists():assert p.read_bytes()==b
 else:p.write_bytes(b)
 print(json.dumps(pin(p)))
if __name__=='__main__':main()
