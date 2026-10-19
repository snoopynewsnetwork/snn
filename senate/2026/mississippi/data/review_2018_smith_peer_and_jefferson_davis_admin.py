"""Bounded independent Smith comparison and fresh original admin-column check."""
from pathlib import Path
import collections,csv,gzip,hashlib,io,json,struct
DATA=Path(__file__).resolve().parent
ROOT=DATA.parent
QA=DATA/'coordinator-qa/smith-2018-independent-replay'
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(ROOT)),bytes=len(b),sha256=sha(b))
def freeze(p):
 q=QA/(p.name+'.gz')
 if q.exists():b=gzip.decompress(q.read_bytes())
 else:b=p.read_bytes();q.write_bytes(gzip.compress(b,mtime=0))
 return b,dict(original=dict(path=str(p.relative_to(ROOT)),bytes=len(b),sha256=sha(b)),lossless_copy=pin(q))
def snapshot(n):
 p=DATA/f'baselines/source/native-2018-{n}views-v1/snapshot.json';s=json.loads(p.read_bytes());out={}
 for a in s['pins']:
  z=(ROOT/a['stored_path']).read_bytes();b=gzip.decompress(z);assert len(z)==a['stored_bytes']and sha(z)==a['stored_sha256']and len(b)==a['original_bytes']and sha(b)==a['original_sha256'];out[Path(a['original_path']).name]=b
 return p,out
def write(name,out):
 p=DATA/name;b=(json.dumps(out,indent=2)+'\n').encode()
 if p.exists():assert p.read_bytes()==b
 else:p.write_bytes(b)
 print(json.dumps(pin(p)))
def main():
 QA.mkdir(parents=True,exist_ok=True)
 jb,jpin=freeze(DATA/'turnout/2018-smith-two-stage-native-original-readings.json');cb,cpin=freeze(DATA/'turnout/2018-smith-two-stage-native-original-cells.csv');rb,rpin=freeze(DATA/'turnout/2018-smith-native-peer-reconciliation.json');a=json.loads(jb);rec=json.loads(rb)
 assert sha(jb)==rec['own_sha256']and not rec['disagreements']and rec['source_position_count']==132
 sp,items=snapshot(40);assert pin(sp)['sha256']==rec['peer_snapshot_sha256']=='59d10972abc73a936ddf6c77d62258b6a9d7d62298cc46bd570ae6c1ad83895f';assert sha(items['native-2018-original-candidate-votes.csv'])==rec['peer_flat_original_sha256']
 flat=list(csv.DictReader(io.StringIO(cb.decode())));peers={(r['source_id'],int(r['source_page']),int(r['source_column']),r['candidate']):r for r in csv.DictReader(io.StringIO(items['native-2018-original-candidate-votes.csv'].decode()))};own={(r['source_id'],int(r['source_pdf_page']),int(r['physical_source_column']),r['candidate']):r for r in flat};assert len(own)==132
 counts=collections.Counter();findings=[];rasters=[]
 roles={'source_native_reporting_constituent':'native','source_TOTAL':'TOTAL','unused_template_column':'unused'}
 for s in a['sources']:
  assert s['native_constituents']==18 and s['physical_TOTAL_page']==3 and s['physical_TOTAL_column']==8
  pdf=gzip.decompress((ROOT/s['source_original_path']).read_bytes());assert sha(pdf)==s['source_raw_sha256']==rec['original_source_hashes'][s['source_id']]
  sums=collections.Counter();totals={}
  for p in s['pages']:
   rp=ROOT/p['original_raster'];b=rp.read_bytes();assert sha(b)==p['raster_sha256']and list(struct.unpack('>II',b[16:24]))==p['render_size'];rasters.append(pin(rp))
  for r in s['rows']:
   key=(s['source_id'],r['source_pdf_page'],r['physical_source_column'],r['candidate']);f=own[key];peer=peers[key]
   assert r['source_raw_sha256']==f['source_raw_sha256']==peer['source_raw_sha256']==s['source_raw_sha256']
   assert r['county_fips']==f['county_fips']==peer['county_fips']=='28129'
   assert r['literal_source_header']==f['literal_source_header']==peer['literal_native_label']and roles[r['role']]==peer['role']
   assert r['role']==f['role']and r['votes']==(None if f['votes']==''else int(f['votes']))==(None if peer['votes']==''else int(peer['votes']))
   assert not peer.get('raw_source_mark')
   if r['role']=='unused_template_column':assert r['votes']is None;counts['unused_null_positions']+=1
   else:
    assert type(r['votes'])is int;counts['numeric_positions']+=1
    if r['role']=='source_native_reporting_constituent':sums[r['candidate']]+=r['votes']
    else:totals[r['candidate']]=r['votes']
  assert dict(sums)==totals=={n:v['printed_TOTAL']for n,v in s['candidate_checks'].items()}
  findings.append(dict(source_id=s['source_id'],stored_original=pin(ROOT/s['source_original_path']),raw_original_sha256=sha(pdf),raw_original_bytes=len(pdf),native_constituents=18,physical_TOTAL=dict(actual_PDFpage=3,column=8),source_candidate_sums_and_TOTALs=totals))
 assert dict(counts)==dict(numeric_positions=114,unused_null_positions=18)
 write('coordinator-smith-2018-independent-native-review.json',dict(status='pass_bounded_independent_Smith2018_two_stage_source_fields',frozen_worker_bodies=[jpin,cpin,rpin],immutable_peer40_snapshot=pin(sp),source_findings=findings,worker_original_raster_pins=rasters,compared_positions=132,numeric_positions=114,unused_null_positions=18,source_native_observations_across_stages=36,qualification='Every original-reading source hash/page/physical-column/candidate value/role/literal-header/FIPS field agrees the frozen independent40-stage source CSV. Worker full-original rasters survive by hash. This is a recomputed source/pin comparison, not fresh coordinator reading of all Smith glyphs or equal raster/numeric polygon/parsedID/current geography. Special four-candidate and runoff two-candidate electorates remain distinct; separately printed ClassI office is excluded. Earlier Franklin corrected-source and old witness bodies remain separate. Not whole164-stage history/method or native887 acceptance.',formal_native887_dispatch_accepted=False,current_geography_approved=False))
 sp,items=snapshot(46);s=next(s for s in json.loads(items['native-2018-original-readings.json'])['sources']if s['source_id']=='sos-2018-runoff-county-jefferson-davis');ref=next(r for r in json.loads((DATA/'baselines/source/references.json').read_bytes())if r['id']==s['source_id']);pdf=gzip.decompress((ROOT/ref['path']).read_bytes());assert sha(pdf)==s['raw_sha256']=='81b8d4e9aceb5b72540d8261eb2ca11959068972c4ac95b809a0cb79119e8408'
 p=next(p for p in s['pages']if p['page']==3);c=p['columns'][0];assert(c['source_column'],c['label_literal'],c['role'])==(1,'PURGED VOTERS','administrative');assert [(f['candidate'],f['values'][0])for f in p['fields']]==[('Mike Espy',0),('Cindy Hyde-Smith',0)]
 write('coordinator-jefferson-davis-2018-runoff-admin-review.json',dict(status='pass_bounded_fresh_original_JeffDavis2018_admin_column',stored_original=pin(ROOT/ref['path']),raw_original_sha256=sha(pdf),fresh_complete_original_render=pin(DATA/'coordinator-qa/jefferson-davis-2018-runoff-admin/pdf3-complete-original.png'),render_parameters=dict(renderer='pdftoppm',DPI=160,deskew_rotation_enhancement='none'),immutable_source46_snapshot=pin(sp),actual_PDFpage=3,physical_column=1,literal_header='PURGED VOTERS',printed_candidate_values={'Mike Espy':0,'Cindy Hyde-Smith':0},source_role='administrative',native=False,unused_blank=False,qualification='The coordinator freshly rendered/read complete actual PDF3 after the source exception was known. The explicitly printed PURGED VOTERS0/0 column precedes six native columns and TOTALphysical8, retained outside native and unused-template counts. No more administrative meaning, publication chronology, cross-stage/2020/2024/current identity or whole native-method/887dispatch approval is inferred.',formal_native887_dispatch_accepted=False,current_geography_approved=False))
if __name__=='__main__':main()
