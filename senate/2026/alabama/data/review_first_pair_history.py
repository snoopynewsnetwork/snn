"""Read-only whole archive/source-witness review; no producer imports or writers."""
from pathlib import Path
import gzip,hashlib,io,json,tarfile,sys
S=Path(__file__).resolve().parents[1];B=S/'data/baselines';T=S/'data/turnout';checks=0

def sha(b):return hashlib.sha256(b).hexdigest()
def ck(v,label):
 global checks
 checks+=1
 if not v:raise AssertionError(label)
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
current={str(p.relative_to(B)):p.read_bytes()for p in B.rglob('*')if p.is_file()};old={};archives=[]
for p in sorted(B.rglob('*.tar.gz')):
 archive=[]
 with tarfile.open(p,'r:gz')as tf:
  for m in tf:
   ck(m.isfile(),'regular archive member only')
   b=tf.extractfile(m).read();ck(len(b)==m.size,'whole archive member length')
   old[(m.name,sha(b))]=b;archive.append({'member':m.name,'bytes':len(b),'sha256':sha(b)})
 archives.append({'path':str(p.relative_to(S)),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes()),'all_members':archive})
index={**{(k,sha(v)):v for k,v in current.items()},**old}
# Original-first witnesses retain original bodies rather than resolve to newer paths.
witnesses=[]
for key,body in sorted(index.items()):
 if key[0]!='source/original-first-witness.json':continue
 obj=json.loads(body);files=obj['files']
 for r in files:
  ck((r['path'],r['sha256'])in index,'every exact historical witness body resolvable')
  ck(len(index[(r['path'],r['sha256'])])==r['bytes'],'whole original witness body length')
 witnesses.append({'path':key[0],'sha256':key[1],'phase':obj['phase'],'whole_bodies':len(files)})
ck(len(witnesses)>=3,'initial/admin-expansion/literal-aggregation phases preserved')
# Candidate rows were already literal/correct in the original-first phase.
with tarfile.open(B/'history/original-first-v1.tar.gz')as tf:
 original_native=json.loads(gzip.decompress(tf.extractfile('source/native-observations.json.gz').read()))
 original_witness=tf.extractfile('source/original-first-witness.json').read()
ck(sha(original_witness)=='941f8c78065a55966c2514b6e99bc1e148ec200d9cc1b269cf461146e83b940d','exact pre-peer witness')
now={r['key']:r for r in read(B/'source/native-observations.json.gz')}
ck(len(original_native)==len(now)==6270,'full pre-peer native universe')
for r in original_native:
 n=now[r['key']]
 for field in ['candidate_rows','native_header_literal','source_column','member','member_sha256','reported_contest_votes','complete_contest_votes']:
  ck(r[field]==n[field],'pre-peer literal candidate/native/source key unchanged')
# Validate all frozen turnout145 targets using archive members or immutable originals.
with tarfile.open(B/'source/frozen-turnout-peer.tar.gz')as tf:
 members={m.name:tf.extractfile(m).read()for m in tf if m.isfile()}
 mf=members['data/turnout/asset-manifest.json'];ck(sha(mf)=='4e2a1f5ab3c66508444c112f9e6430006dce94f795a172837c7b95eaee557207','frozen peer exact original manifest')
 for r in json.loads(mf)['assets']:
  body=members[r['path']]if r['path']in members else(S/r['path']).read_bytes()
  ck(sha(body)==r['sha256']and len(body)==r['bytes'],'every complete frozen turnout body')
for p in sorted((T/'history').glob('*.json')):
 r=read(p);body=gzip.decompress((p.parent/r['stored_body']).read_bytes());ck(len(body)==r['original_bytes']and sha(body)==r['sha256'],'every old turnout body')
seal=read(B/'final-seal.json');ck(seal['validation_sha256']==sha((B/'validation.json').read_bytes()),'sealed validation exact')
ck(seal['manifest_hash_in_seal']is None and seal['manifest_excludes_only_itself'],'no current manifest reverse digest cycle')
out={'status':'pass_complete_first_pair_original_history_reconstruction','checks':checks,'complete_baseline_archives':len(archives),'complete_archive_members':sum(len(a['all_members'])for a in archives),'original_first_native_records':6270,'original_first_candidate_source_identity_unchanged':True,'preserved_original_witnesses':witnesses,'all_exact_archive_members':archives,'peer_comparison_scope':'Captured145 turnout targets and original-first source objects; no new current/future peer/scenario outcome equality inferred','producer_writes':False}
body=(json.dumps(out,indent=2)+'\n').encode();p=S/'data/coordinator-first-pair-history-review.json'
if '--check'in sys.argv:ck(p.read_bytes()==body,'same frozen history review')
else:p.write_bytes(body)
print(json.dumps({k:v for k,v in out.items()if k not in ['all_exact_archive_members','preserved_original_witnesses']}))
