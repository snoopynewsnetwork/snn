"""Freeze independently original-read two-stage derivatives and recompute comparison."""
from pathlib import Path
import argparse,collections,csv,gzip,hashlib,io,json,struct
DATA=Path(__file__).resolve().parent
ROOT=DATA.parent
QA=DATA/'coordinator-qa/turnout-2018-two-stage-replays'
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(ROOT)),bytes=len(b),sha256=sha(b))
def freeze(p):
 q=QA/(p.name+'.gz')
 if q.exists():b=gzip.decompress(q.read_bytes())
 else:b=p.read_bytes();q.write_bytes(gzip.compress(b,mtime=0))
 return b,dict(original=dict(path=str(p.relative_to(ROOT)),bytes=len(b),sha256=sha(b)),lossless_copy=pin(q))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--county',required=True);ap.add_argument('--views',type=int,required=True);ap.add_argument('--peer-version',type=int,default=1);ap.add_argument('--native',type=int,required=True);ap.add_argument('--TOTALpage',type=int,required=True);ap.add_argument('--TOTALcolumn',type=int,required=True);args=ap.parse_args();assert args.county.isalpha();QA.mkdir(parents=True,exist_ok=True)
 j=DATA/f'turnout/2018-{args.county}-two-stage-native-original-readings.json';c=DATA/f'turnout/2018-{args.county}-two-stage-native-original-cells.csv';r=DATA/f'turnout/2018-{args.county}-native-peer-reconciliation.json';jb,jpin=freeze(j);cb,cpin=freeze(c);rb,rpin=freeze(r);own=json.loads(jb);rec=json.loads(rb);assert rec['own_sha256']==sha(jb)and not rec['disagreements']
 sp=DATA/f'baselines/source/native-2018-{args.views}views-v{args.peer_version}/snapshot.json';snap=json.loads(sp.read_bytes());assert sha(sp.read_bytes())==rec['peer_snapshot_sha256'];cp=next(p for p in snap['pins']if p['original_path'].endswith('native-2018-original-candidate-votes.csv'));z=(ROOT/cp['stored_path']).read_bytes();pb=gzip.decompress(z);assert len(z)==cp['stored_bytes']and sha(z)==cp['stored_sha256']and len(pb)==cp['original_bytes']and sha(pb)==cp['original_sha256']==rec['peer_flat_original_sha256']
 key=lambda s,p,c,n:(s,int(p),int(c),n)
 peer={key(r['source_id'],r['source_page'],r['source_column'],r['candidate']):r for r in csv.DictReader(io.StringIO(pb.decode()))};flat={key(r['source_id'],r['source_pdf_page'],r['physical_source_column'],r['candidate']):r for r in csv.DictReader(io.StringIO(cb.decode()))};counts=collections.Counter();findings=[];rasters=[];aliases=[]
 rolemap={'source_native_reporting_constituent':'native','source_TOTAL':'TOTAL','unused_template_column':'unused'}
 for s in own['sources']:
  assert s['native_constituents']==args.native and s['physical_TOTAL_page']==args.TOTALpage and s['physical_TOTAL_column']==args.TOTALcolumn
  pdf=gzip.decompress((ROOT/s['source_original_path']).read_bytes());assert sha(pdf)==s['source_raw_sha256'];sums=collections.Counter();totals={};units={}
  for p in s['pages']:
   rp=ROOT/p['original_raster'];b=rp.read_bytes();assert sha(b)==p['raster_sha256']and list(struct.unpack('>II',b[16:24]))==p['render_size'];rasters.append(pin(rp))
  literal_exceptions=[]
  for r in s['rows']:
   k=key(s['source_id'],r['source_pdf_page'],r['physical_source_column'],r['candidate']);f=flat[k];p=peer[k];assert r['source_raw_sha256']==f['source_raw_sha256']==p['source_raw_sha256']==s['source_raw_sha256']and r['county_fips']==f['county_fips']==p['county_fips'];assert r['role']==f['role']and rolemap[r['role']]==p['role']
   assert r['literal_source_header']==f['literal_source_header']
   if ' '.join(r['literal_source_header'].split())!=' '.join(p['literal_native_label'].split()):
    if args.county=='greene':
     assert k[1:3]==(3,1)and r['literal_source_header']=='Mclain'and p['literal_native_label']=='McLain'
     glyph=json.loads((DATA/'coordinator-greene-2018-original-header-review.json').read_bytes());assert glyph['original_stage_candidate_values'][s['source_id']][r['candidate']]==r['votes']
     literal_exceptions.append(dict(source_id=s['source_id'],page=k[1],physical_column=k[2],candidate=r['candidate'],own_original_literal='Mclain',peer_derivative_literal='McLain',value=r['votes'],role=r['role']))
    else:
     assert args.county=='tunica'and k[1:3]==(2,2)and r['literal_source_header']=='Mhoon Landing'and p['literal_native_label']=='Moon Landing'
     glyph=json.loads((DATA/'coordinator-tunica-2018-original-header-review.json').read_bytes());assert glyph['candidate_values_by_source'][s['source_id']][r['candidate']]==r['votes']
     literal_exceptions.append(dict(source_id=s['source_id'],source_pdf_page=2,physical_source_column=2,candidate=r['candidate'],original_literal='Mhoon Landing',peer_derivative_literal='Moon Landing',votes=r['votes']))
   elif r['literal_source_header']!=p['literal_native_label']:aliases.append(dict(source_key=list(k),turnout_literal=r['literal_source_header'],baseline_literal=p['literal_native_label']))
   assert r['votes']==(None if f['votes']==''else int(f['votes']))==(None if p['votes']==''else int(p['votes']))and not p.get('raw_source_mark');units[r['source_pdf_page'],r['physical_source_column']]=r['role']
   if r['role']=='unused_template_column':assert r['votes']is None;counts['unused_null_positions']+=1
   else:
    assert type(r['votes'])is int and r['votes']>=0;counts['numeric_positions']+=1
    if r['role']=='source_native_reporting_constituent':sums[r['candidate']]+=r['votes']
    else:totals[r['candidate']]=r['votes']
  assert dict(sums)==totals=={n:v['printed_TOTAL']for n,v in s['candidate_checks'].items()};assert sum(v=='source_native_reporting_constituent'for v in units.values())==args.native
  finding=dict(source_id=s['source_id'],raw_original_sha256=sha(pdf),raw_original_bytes=len(pdf),stored_original=pin(ROOT/s['source_original_path']),native_constituents=args.native,physical_TOTAL=dict(actual_PDFpage=args.TOTALpage,column=args.TOTALcolumn),source_candidate_sums_and_TOTALs=totals)
  if literal_exceptions:finding['literal_header_differences_confirmed_from_original']=literal_exceptions
  findings.append(finding)
 assert len(own['sources'])==2 and len(flat)==sum(counts.values())==rec['source_position_count']
 out=dict(status='pass_bounded_independent_original2018_two_stage_source_replay',county=args.county,frozen_worker_bodies=[jpin,cpin,rpin],immutable_peer_snapshot=pin(sp),source_findings=findings,original_worker_raster_pins=rasters,compared_positions=len(flat),counts=dict(counts),whitespace_only_header_representations=aliases,qualification='All original-reading and flat source fields recompute against immutable peer evidence after the worker original transcript: candidate values/roles/original hash/page/physical column/FIPS and whitespace-folded literal headers. Whole source rasters survive by hash, not pixel/reading-window/parsedID identity. This is not fresh coordinator visual reading of all new glyphs, shared current geography, same cross-stage electorate or whole164-stage historical-method/native887 approval. Source native fields are never replaced by county controls or another year/stage.',formal_native887_dispatch_accepted=False,current_geography_approved=False)
 if args.county=='greene':
  differences=[r for f in findings for r in f.get('literal_header_differences_confirmed_from_original',[])]
  assert len(differences)==6 and differences==rec['accepted_literal_differences']
  out['original_header_exception_review']=pin(DATA/'coordinator-greene-2018-original-header-review.json')
  out['qualification']=out['qualification'].replace('and whitespace-folded literal headers.','and literal headers with six explicit original Mclain versus older derivative McLain case differences. These are not whitespace aliases or normalized geographic identities.')
 if args.county=='tunica':
  differences=[r for f in findings for r in f.get('literal_header_differences_confirmed_from_original',[])]
  assert len(differences)==6 and differences==rec['accepted_literal_differences']
  out['original_header_exception_review']=pin(DATA/'coordinator-tunica-2018-original-header-review.json')
  out['qualification']=out['qualification'].replace('and whitespace-folded literal headers.','and literal headers with six explicit original MhoonLanding versus older derivative MoonLanding spelling differences. These are not whitespace aliases or normalized geographic identities; later142v2 corrects only those two source-header objects with prior bytes retained.')
 p=DATA/f'coordinator-turnout-2018-{args.county}-two-stage-review.json';body=(json.dumps(out,indent=2)+'\n').encode()
 if p.exists():assert p.read_bytes()==body
 else:p.write_bytes(body)
 print(json.dumps(dict(output=pin(p),counts=dict(counts))))
if __name__=='__main__':main()
