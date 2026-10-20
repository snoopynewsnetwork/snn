#!/usr/bin/env python3
"""Freeze pre-peer full body witness, then final seal and manifest; no reverse manifest digest."""
import datetime,gzip,hashlib,io,json,tarfile
from pathlib import Path
HERE=Path(__file__).resolve().parent;STATE=HERE.parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def owned():return sorted([STATE/'turnout.md',STATE/'data/county-turnout.csv']+[p for p in HERE.rglob('*') if p.is_file()])
def write(p,o):p.write_text(json.dumps(o,indent=2)+'\n')
if __name__=='__main__':
 assert not (HERE/'final-seal.json').exists(),'seal already exists; frozen package'
 assert json.loads((HERE/'validation.json').read_text())['status']=='pass'
 assert json.loads((HERE/'offline-rebuild.json').read_text())['status']=='pass'
 contract=json.loads((HERE/'priority-set.json').read_text());assert contract['peer']['peer_agent_id'] is None
 files=[(p,str(p.relative_to(STATE))) for p in owned()]
 # Full byte witness also covers every exact shared original used as a read-only content-addressed reference.
 for r in json.loads((HERE/'source/pinned-originals.json').read_text()):
  p=STATE/r['body_path'];packed=p.read_bytes();assert sha(packed)==r['stored_sha256'];files.append((p,r['body_path']))
 assert len({str(p) for p,_ in files})==len(files)
 archive=HERE/'pre-peer-bodies.tar.gz';entries=[]
 with archive.open('wb') as outer:
  with gzip.GzipFile(fileobj=outer,mode='wb',mtime=0,filename='') as gz:
   with tarfile.open(fileobj=gz,mode='w|',format=tarfile.PAX_FORMAT) as tar:
    for p,name in sorted(files,key=lambda x:x[1]):
     b=p.read_bytes();assert len(b)<40000000;arc='bodies/'+name;info=tarfile.TarInfo(arc);info.size=len(b);info.mtime=0;info.mode=0o644;info.uid=0;info.gid=0;info.uname='';info.gname='';tar.addfile(info,io.BytesIO(b));entries.append({'original_path':name,'archive_name':arc,'bytes':len(b),'sha256':sha(b),'ownership':'exclusive worker body' if p in owned() else 'read-only exact shared original entity'})
 assert archive.stat().st_size<40000000
 witness={'schema':'complete-immutable-pre-peer-body-witness-v1','created_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'peer_agent_id':None,'peer_derivative_access_before_witness':False,'archive_path':archive.name,'archive_sha256':sha(archive.read_bytes()),'archive_bytes':archive.stat().st_size,'archive_storage':'gzip(mtime0) of deterministic tar headers and exact original member bytes; no truncation/simplification','bodies':entries,'witness_scope':'Every owned original, receipt, source index, script, extraction, control, order, report, CSV, offline proof and preseal validation existing before this witness; plus every exact referenced shared original. This witness/archive and later final-seal/manifest are subsequent proof objects, included by the complete final manifest.','does_not_claim':'independent peer agreement, coordinator acceptance, legal/native writein universe or geographic compatibility'}
 write(HERE/'pre-peer-witness.json',witness)
 seal={'schema':'va-turnout-final-prepeer-seal-v1','created_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'substantive source-known report and preseal QA complete; frozen for final read-only complete audit','witness_sha256':sha((HERE/'pre-peer-witness.json').read_bytes()),'witness_archive_sha256':witness['archive_sha256'],'preseal_validation_sha256':sha((HERE/'validation.json').read_bytes()),'offline_rebuild_sha256':sha((HERE/'offline-rebuild.json').read_bytes()),'report_sha256':sha((STATE/'turnout.md').read_bytes()),'contract_sha256':sha((HERE/'priority-set.json').read_bytes()),'native_csv_sha256':sha((STATE/'data/county-turnout.csv').read_bytes()),'peer_agent_id':None,'peer_derivative_access_before_seal':False,'peer_agreement':'pending actual independent worker launch and bounded reciprocal','coordinator_acceptance':'not claimed','raw_state_vector':[2417115,2019911,8509],'native_count':2669,'parent_count':133,'minimum80_count':1538,'integer_minimum80_votes':3557034,'preceding_count':1537,'preceding_votes':3555604,'stored_object_bound_exclusive':40000000,'proof_order':'preseal source/control validation -> complete pre-peer body archive/witness -> this seal -> manifest -> final read-only audit. No object digests the later manifest.'}
 write(HERE/'final-seal.json',seal)
 manifest={'schema':'va-turnout-complete-owned-asset-manifest-v1','excludes_only_itself':'data/turnout/asset-manifest.json','owned_assets':[],'read_only_original_references':[]}
 for p in owned():
  if p==HERE/'asset-manifest.json':continue
  b=p.read_bytes();assert len(b)<40000000;manifest['owned_assets'].append({'path':str(p.relative_to(STATE)),'bytes':len(b),'sha256':sha(b)})
 for r in json.loads((HERE/'source/pinned-originals.json').read_text()):manifest['read_only_original_references'].append({k:r[k] for k in ['id','body_path','raw_sha256','stored_sha256','raw_bytes','stored_bytes']})
 write(HERE/'asset-manifest.json',manifest)
 print(json.dumps({'sealed_owned_files':len(manifest['owned_assets']),'prepeer_witness_bodies':len(entries),'archive_bytes':archive.stat().st_size,'contract_sha256':seal['contract_sha256'],'next':'run validate_turnout.py read-only; no further writes'}))
