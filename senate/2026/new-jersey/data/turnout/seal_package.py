#!/usr/bin/env python3
"""Freeze own pre-peer research bodies once; refresh complete owned-asset manifest separately."""
from pathlib import Path
import hashlib,gzip,json,datetime,os,sys
D=Path(__file__).resolve().parent;STATE=D.parent.parent;FREEZE=D/'peer-review-freeze/original-first-v1'
def sha(b):return hashlib.sha256(b).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
def owned():return [STATE/'turnout.md',D.parent/'county-turnout.csv']+sorted(p for p in D.rglob('*') if p.is_file())
def freeze():
 witness=D/'pre-peer-witness.json'
 if witness.exists():
  w=json.loads(witness.read_text())
  for a in w['frozen_bodies']:
   z=(STATE/a['frozen_path']).read_bytes();assert sha(z)==a['stored_sha256'] and sha(gzip.decompress(z))==a['original_sha256']
  print('Existing immutable witness verified; no frozen body rewritten.');return
 bodies=[];pins=[]
 for p in owned():
  if p.name in ['asset-manifest.json','pre-peer-witness.json','validation.json'] or 'peer-review-freeze' in p.parts:continue
  b=p.read_bytes();rel=p.relative_to(STATE)
  if p.name.endswith('.body.gz'):
   pins.append({'path':str(rel),'sha256':sha(b),'bytes':len(b),'type':'original_download_stored_bytes'});continue
  dest=FREEZE/'bodies'/(str(rel)+'.gz');dest.parent.mkdir(parents=True,exist_ok=True);z=gzip.compress(b,mtime=0);assert len(z)<40000000;assert not dest.exists();dest.write_bytes(z)
  bodies.append({'path':str(rel),'original_sha256':sha(b),'original_bytes':len(b),'frozen_path':str(dest.relative_to(STATE)),'stored_sha256':sha(z),'stored_bytes':len(z)})
 # Shared originals stay read-only and are hash-pinned rather than duplicated.
 for p in sorted((D/'source').glob('shared-*.receipt.json')):
  a=json.loads(p.read_text());q=(p.parent/a['reference_path']).resolve();z=q.read_bytes();assert sha(z)==a['stored_sha256'];pins.append({'path':os.path.relpath(q,STATE),'sha256':sha(z),'bytes':len(z),'raw_sha256':a['raw_sha256'],'type':'read_only_shared_original'})
 a=json.loads((D/'source/clerk-2020-reference.json').read_text());q=((D/'source')/a['reference_path']).resolve();b=q.read_bytes();assert sha(b)==a['raw_sha256'];pins.append({'path':os.path.relpath(q,STATE),'sha256':sha(b),'bytes':len(b),'type':'read_only_shared_primary_pdf'})
 dump(witness,{'version':'original-first-v1','created_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'peer_agent_id':None,'peer_derivatives_read':False,'status':'immutable own pre-peer original-first witness; no coordinator acceptance','body_scope':'all owned research/report/acquisition/extraction/schema/receipt bodies; original download bodies pinned without duplication; final QA/asset manifest separately sealed','frozen_bodies':bodies,'original_pins':pins})
 print(json.dumps({'frozen_research_bodies':len(bodies),'original_pins':len(pins),'witness_sha256':sha(witness.read_bytes())}))
def manifest():
 target=D/'asset-manifest.json';assets=[]
 for p in owned():
  if p==target:continue
  b=p.read_bytes();assert len(b)<40000000
  assets.append({'path':str(p.relative_to(STATE)),'sha256':sha(b),'bytes':len(b)})
 dump(target,{'schema_version':'nj-turnout-owned-assets-v1','path_base':'senate/2026/new-jersey','excluded_self':'data/turnout/asset-manifest.json','original_reference_policy':'Read-only shared originals pinned by individual source receipts and pre-peer witness; not copied into owned artifacts.','assets':sorted(assets,key=lambda a:a['path'])})
 print(json.dumps({'owned_assets':len(assets),'manifest_sha256':sha(target.read_bytes()),'largest_bytes':max(a['bytes'] for a in assets)}))
if __name__=='__main__':
 if len(sys.argv)<2 or sys.argv[1] not in ['freeze','manifest']:raise SystemExit('Use freeze or manifest.')
 freeze() if sys.argv[1]=='freeze' else manifest()
