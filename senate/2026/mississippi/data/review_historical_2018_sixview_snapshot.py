"""Compare six frozen stage grids with the coordinator's direct originals."""
from pathlib import Path
import collections,csv,gzip,hashlib,io,json
DATA=Path(__file__).resolve().parent
ROOT=DATA.parent
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(ROOT)),bytes=len(b),sha256=sha(b))
def load(p):
 a=json.loads(p.read_bytes());out={}
 for i in a['pins']:
  z=(ROOT/i['stored_path']).read_bytes();b=gzip.decompress(z);assert len(z)==i['stored_bytes']and sha(z)==i['stored_sha256']and len(b)==i['original_bytes']and sha(b)==i['original_sha256'];out[Path(i['original_path']).name]=b
 return a,out
def main():
 sp=DATA/'baselines/source/native-2018-6views-v1/snapshot.json';assert pin(sp)['sha256']=='9c19f176d9ba6be6a18d63167ee10beb33211496e2fdd8ef6eed0251b21c6f46';snap,items=load(sp);ledger=json.loads(items['native-2018-original-readings.json']);sources={s['source_id']:s for s in ledger['sources']};assert len(sources)==6 and len(ledger['all164_source_status'])==164
 oldsp=DATA/'baselines/source/native-2018-2views-v1/snapshot.json';_,olditems=load(oldsp);olds=json.loads(olditems['native-2018-original-readings.json'])['sources'];assert len(olds)==2 and all(sources[s['source_id']]==s for s in olds)
 manual={};proofs=[]
 for name,expected,vector_key,header_key in [('coordinator-issaquena-2018-physical-column-review.json','9fb0346d32220c5cb7371490cef25f7da244b54e1011fdc31cb1a4940c08d124','direct_original_candidate_vectors_in_physical_order','physical_headers_in_original_order'),('coordinator-benton-2018-original-native-review.json','b8d0825fcc8d8402c447667419b330aa847a4ffde0e69be1ef05bf0155a2e60a','direct_complete_original_vectors','physical_headers_in_order'),('coordinator-franklin-2018-original-native-review.json','c39e7ccc9f4e4a2b8c3be7df4768cf3b6e1560c8cd3492dec58c1a8a0c7dde19','direct_original_candidate_vectors','literal_headers')]:
  p=DATA/name;assert pin(p)['sha256']==expected;proofs.append(pin(p));a=json.loads(p.read_bytes())
  for r in a['original_findings']:manual[r['source_id']]=(r,r[vector_key],r[header_key])
 casepath=DATA/'coordinator-franklin-2018-header-case-correction.json';assert pin(casepath)['sha256']=='414360063ec68c693e46a31ff934ff613eaff904b6b7e85b083b88b4dd7f4321';case=json.loads(casepath.read_bytes());caseids={r['source_id']for r in case['findings']}
 counts=collections.Counter();allfields={};rasterpins=[];findings=[]
 for sid,s in sources.items():
  original,vectors,headers=manual[sid];headers=list(headers)
  if sid in caseids:assert headers[8]=='McCall';headers[8]='Mccall'
  assert s['raw_sha256']==original['raw_PDF_sha256'];sourcepath=ROOT/original.get('original_stored_pin',original.get('stored_original'))['path'];assert sha(gzip.decompress(sourcepath.read_bytes()))==s['raw_sha256'];columns=[c for p in s['pages']for c in p['columns']];assert [' '.join(c['label_literal'].split())for c in columns]==[' '.join(h.split())for h in headers]
  for p in s['pages']:
   rp=ROOT/p['full_original_render_path'];assert pin(rp)['sha256']==p['render_sha256'];rasterpins.append(pin(rp))
   for c in p['columns']:counts[{'native':'native_constituents_across_separate_stages','TOTAL':'TOTAL_columns','unused':'unused_columns'}[c['role']]]+=1
   for f in p['fields']:
    assert f['party_literal']is None
    for col,value in zip(p['columns'],f['values']):
     key=(sid,p['page'],col['source_column'],f['candidate']);assert key not in allfields;allfields[key]=(col,value);counts['unused_null_positions'if col['role']=='unused'else'numeric_positions']+=1;assert(value is None)if col['role']=='unused'else type(value)is int
  for candidate,expected in vectors.items():
   actual=[v for p in s['pages']for f in p['fields']if f['candidate']==candidate for v in f['values']];assert actual==expected
   total=next(v for k,(col,v)in allfields.items()if k[0]==sid and k[3]==candidate and col['role']=='TOTAL');summed=sum(v for k,(col,v)in allfields.items()if k[0]==sid and k[3]==candidate and col['role']=='native');assert summed==total==s['controls']['printed_TOTAL'][candidate]
  findings.append(dict(source_id=sid,raw_PDF_sha256=s['raw_sha256'],actual_PDFpages=[p['page']for p in s['pages']],source_bound_candidate_TOTALs=s['controls']['printed_TOTAL'],source_only_printed_party_fields=None))
 flat=list(csv.DictReader(io.StringIO(items['native-2018-original-candidate-votes.csv'].decode())));assert len(flat)==len(allfields)==264
 for r in flat:
  key=(r['source_id'],int(r['source_page']),int(r['source_column']),r['candidate']);c,v=allfields[key];assert(None if r['votes']==''else int(r['votes']))==v and r['role']==c['role'];assert ' '.join(r['literal_native_label'].split())==' '.join(c['label_literal'].split())
 counts['source_views']=len(sources);assert dict(counts)==snap['counts']==ledger['counts']
 log=DATA/'baselines/qa/reproduction-104views-2018six.log';raw=log.read_bytes();assert len(raw)==25827 and sha(raw)=='6906612160258d073863968d08b74e69261b60a336c9a026b64ac7526f514e67';lp=DATA/'coordinator-qa/reproduction-104views-2018six.log.gz'
 if lp.exists():assert gzip.decompress(lp.read_bytes())==raw
 else:lp.write_bytes(gzip.compress(raw,mtime=0))
 out=dict(status='pass_bounded_six_original2018_stage_grids_and_frozen_reproduction_log',immutable_snapshot=pin(sp),prior_two_view_snapshot=pin(oldsp),prior_two_source_ledgers_unchanged=True,coordinator_fresh_original_reading_proofs=proofs,coordinator_original_header_case_correction=pin(casepath),counts=dict(counts),flat_candidate_positions=264,source_findings=findings,baseline_original_render_pins=rasterpins,reproduction_log=dict(original_path=str(log.relative_to(ROOT)),original_bytes=len(raw),original_sha256=sha(raw),lossless_copy=pin(lp),worker_reported_exit_code=0,worker_reported_bounded_checks=23,coordinator_reran_mutating_worker_reproduction=False),qualification='All six frozen stage grids agree with fresh coordinator complete-original readings and independent source controls at162 numeric/102 unusednull positions. Two earlier Franklin coordinator header transcriptions McCall have an explicit original-crop case correction to Mccall; the earlier witness and all counts remain unchanged. Special four-candidate and runoff two-candidate contexts remain separate, with unrelated ClassI rows excluded and unprinted parties unknown. Prior two-source witness is unchanged. Source/raster/flat checks do not imply equal numeric polygons or cross-stage/current geography. The verified log is the worker-reported successful104-publication/2018six replay, not a coordinator rerun of worker-owned writes. The earlier failed witness-folder matcher log remains worker evidence. Remaining158 historical stage-native grids and full method/current identity/dispatch remain open.',whole2018_native_complete=False,formal_native887_dispatch_accepted=False,current_geography_approved=False)
 target=DATA/'coordinator-2018-sixview-original-snapshot-review.json';b=(json.dumps(out,indent=2)+'\n').encode()
 if target.exists():assert target.read_bytes()==b
 else:target.write_bytes(b)
 print(json.dumps(pin(target)))
if __name__=='__main__':main()
