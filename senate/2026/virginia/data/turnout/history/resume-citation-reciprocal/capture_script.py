from pathlib import Path
import hashlib,json,gzip,tarfile,io,datetime
S=Path('/Users/tqbf/codebase/snn/senate/2026/virginia');T=S/'data/turnout';B=S/'data/baselines'
sha=lambda b:hashlib.sha256(b).hexdigest()
configs=[('turnout-original-first',T,'6eafa8cc1a897b40075d8234681b832282d871490043b98ef3c7f5c878fd2b50',389,[S/'turnout.md',S/'data/county-turnout.csv']),('baseline-final-peer',B,'9b93b5ebf5c4e6d20c7e1216b992886d265c343021f8a10c48f982ecd2e74cbf',300,[S/'county-partisanship.md',S/'data/county-baselines.csv'])]
ready=[]
for kind,base,pin,count,top in configs:
 mp=base/'asset-manifest.json';assert sha(mp.read_bytes())==pin;m=json.loads(mp.read_text());es=m.get('owned_assets',m.get('files'));assert len(es)+1==count
 actual={str(p.relative_to(S)) for p in base.rglob('*') if p.is_file()}|{str(p.relative_to(S)) for p in top}
 expected={e['path'] for e in es}|{str(mp.relative_to(S))};assert actual==expected,(kind,actual^expected)
 for e in es:
  b=(S/e['path']).read_bytes();assert len(b)==e['bytes'] and sha(b)==e['sha256'] and len(b)<40000000
 es=es+[{'path':str(mp.relative_to(S)),'bytes':mp.stat().st_size,'sha256':pin}];ready.append((kind,base,es,pin))
print('BOTH whole packages verified BEFORE first owned write',flush=True)
H=T/'history/resume-citation-reciprocal';H.mkdir(parents=True,exist_ok=False)
for kind,base,es,pin in ready:
 archive=H/f'{kind}.tar.gz';out=[]
 with archive.open('wb') as f:
  with gzip.GzipFile(fileobj=f,mode='wb',mtime=0,filename='') as gz:
   with tarfile.open(fileobj=gz,mode='w|') as tar:
    for e in es:
     p=S/e['path'];b=p.read_bytes()
     # Preserve original body entities once by exact immutable reference; all mutable outputs/scripts/MF/seals are copied.
     ref=('/source/' in e['path'] and p.suffix=='.gz') or p.name in ['pre-peer-bodies.tar.gz','pre-peer-original-bodies.tar.gz','peer-capture.tar.gz'] or '/history/' in e['path']
     entry={**e,'role':'exact retained reference (no primary/archive duplication)' if ref else 'captured exact member','reference_path':e['path'] if ref else None,'archive_name':None}
     if not ref:
      name='bodies/'+e['path'];info=tarfile.TarInfo(name);info.size=len(b);info.mtime=0;info.mode=0o644;tar.addfile(info,io.BytesIO(b));entry['archive_name']=name
     out.append(entry)
 assert archive.stat().st_size<40000000
 obj={'schema':'whole-package-before-review-capture-v1','captured_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'package':kind,'manifest_sha256':pin,'whole_membership_count':len(es),'all_manifest_targets_verified_before_owned_write':True,'archive_path':str(archive.relative_to(S)),'archive_bytes':archive.stat().st_size,'archive_sha256':sha(archive.read_bytes()),'bodies':out,'prior_inspection_error':'Initial read-only manifest metadata inspection recognized owned_assets but not peer files; exited before any writes/comparison. This capture handles both explicit schemas; no source values were compared at that stage.'}
 (H/f'{kind}.json').write_text(json.dumps(obj,indent=2)+'\n');print(kind,len(es),archive.stat().st_size,sha(archive.read_bytes()),flush=True)
# Exact coordinator failure evidence copied losslessly with complete hashes, without changing coordinator files.
F=S/'data/coordinator-turnout-citation-finding';finding=json.loads((F/'finding.json').read_text());ev=[]
for p in sorted(F.iterdir()):
 if p.is_file():
  b=p.read_bytes();q=H/('finding-'+p.name);q.write_bytes(b);ev.append({'original_readonly_path':str(p.relative_to(S)),'captured_path':str(q.relative_to(S)),'bytes':len(b),'sha256':sha(b)})
for e in finding['frozen_before_any_possible_repair']:
 b=gzip.decompress((S/e['stored_path']).read_bytes());assert len(b)==e['original_bytes'] and sha(b)==e['original_sha256'];assert (S/e['original_path']).read_bytes()==b
(H/'finding-capture.json').write_text(json.dumps(ev,indent=2)+'\n')
(H/'capture_script.py').write_bytes(Path(__file__).read_bytes())
