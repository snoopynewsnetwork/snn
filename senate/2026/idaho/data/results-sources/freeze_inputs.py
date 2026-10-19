#!/usr/bin/env python3
"""Freeze references to complete first-pair bodies; never write a producer file."""
from pathlib import Path
import csv,gzip,hashlib,io,json,os
D=Path(__file__).resolve().parent;S=D.parent.parent
A='data/coordinator-priority-acceptance.json'
def sha(b):return hashlib.sha256(b).hexdigest()
def semantic(x):return sha(json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode())
def pin(p):
 b=p.read_bytes();assert len(b)<40000000;v=dict(path=os.path.relpath(p,S),bytes=len(b),sha256=sha(b));raw=gzip.decompress(b) if p.suffix=='.gz' else b
 if p.suffix=='.gz':v.update(reconstructed_bytes=len(raw),reconstructed_sha256=sha(raw))
 name=p.name.removesuffix('.gz')
 if name.endswith('.json'):v.update(semantic_sha256=semantic(json.loads(raw)),complete_recursive_body=True)
 elif name.endswith('.csv'):v.update(complete_rows_semantic_sha256=semantic(list(csv.reader(io.StringIO(raw.decode())))),complete_recursive_body=True)
 return v

def main():
 a=json.loads((S/A).read_bytes());c=json.loads((S/a['frozen_contract']['path']).read_bytes());refs={}
 def add(p):
  p=p.resolve()
  # Old aggregate/review names remain preserved inside frozen provenance bodies, but are not active build dependencies.
  if p in {(S/x).resolve() for x in ['data/news/manifest.json','data/news/coordinator-oct19-recheck/acquisition-ballot-stage-v3.json','data/news/coordinator-oct19-recheck/current-ballot-original-review.json']}:return
  v=pin(p);refs[v['path']]=v
 for v in a['frozen_first_pair_assets']+a['complete_source_companion_files']+[a['frozen_contract']]:add(S/v['path'])
 for role in ['turnout','baselines']:
  root=S/'data'/role;m=json.loads((root/'asset-manifest.json').read_bytes());items=m.get('owned_assets',m.get('owned'))
  for v in items:add(S/v['path'])
  for v in m.get('read_only_references',[]):add((root/v['path']).resolve())
 # Every retained original source reference from both producers, independently pinned.
 for p in ['data/turnout/source/reused-originals.json','data/baselines/source/reused-originals.json','data/baselines/source/additional-reused-originals.json']:
  entries=json.loads((S/p).read_bytes());root=(S/p).parent.parent
  for e in entries:
   if e.get('reused_path'):add((root/e['reused_path']).resolve())
 # Individually snapshot only the relevant original ballot receipts, never depend on an appendable news aggregate.
 observations=json.loads((S/'data/news/coordinator-oct19-recheck/acquisition-ballot-stage-v3.json').read_bytes());selected=[r for r in observations if r['id'] in ['TwinFalls-SOS-linked-home','TwinFalls-linked-elections','TwinFalls-linked-sample-parent','TwinFalls-linked-LD24-ballot']]
 for r in selected:add(S/r['asset_path'])
 (D/'reused-ballot-receipts.json').write_text(json.dumps(selected,ensure_ascii=False,indent=2)+'\n')
 # Complete frozen primary/history object pointers, not vote-only projections.
 objects=[]
 for i,p in enumerate(c['all_county_constituents']):
  objects.append(dict(file=a['frozen_contract']['path'],pointer=f'/all_county_constituents/{i}',semantic_sha256=semantic(p),role='complete_parent',key=p['key']))
  for j,u in enumerate(p['president_contexts']):objects.append(dict(file=a['frozen_contract']['path'],pointer=f'/all_county_constituents/{i}/president_contexts/{j}',semantic_sha256=semantic(u),role='complete_native',key=u['key']))
 for name in ['historical-native.json.gz','historical-administrative-controls.json.gz']:
  p=S/'data/turnout'/name;xs=json.loads(gzip.decompress(p.read_bytes()))
  for i,u in enumerate(xs):objects.append(dict(file=str(p.relative_to(S)),pointer=f'/{i}',semantic_sha256=semantic(u),role=u['role'],key=u['key']))
 graph=dict(schema='idaho-official-complete-frozen-input-graph-v1',external_acceptance_path=A,contract_path=a['frozen_contract']['path'],root_fields=[dict(pointer='/'+k,semantic_sha256=semantic(v)) for k,v in c.items()],complete_source_companion_paths=[v['path'] for v in a['complete_source_companion_files']],immutable_complete_files=list(sorted(refs.values(),key=lambda x:x['path'])),complete_object_references=objects,qualification='All fields and complete bodies remain required. No field omission, inferred alias, method/polygon/current join or producer acceptance flag mutation.')
 (D/'historical-source-graph.json').write_text(json.dumps(graph,ensure_ascii=False,indent=2)+'\n');print('immutable references',len(refs),'complete object pointers',len(objects),'companions',len(graph['complete_source_companion_paths']))
if __name__=='__main__':main()
