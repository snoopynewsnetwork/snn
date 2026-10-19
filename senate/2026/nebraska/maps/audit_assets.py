#!/usr/bin/env python3
"""Full owned asset manifest; self only excluded; external originals referenced, never copied."""
import json,pathlib,csv
from acquire import ROOT,STATE,sha,save_json

def files():
 ps=[STATE/'precinct-maps.md']+[p for p in ROOT.rglob('*') if p.is_file() and p.name!='asset-manifest.json']
 assert not any('__pycache__' in p.parts or '.pyc'==p.suffix or 'node_modules' in p.parts for p in ps)
 return sorted(ps)
def manifest():
 entries=[]
 for p in files():
  b=p.read_bytes();assert len(b)<40_000_000,str(p);entries.append({'path':str(p.relative_to(STATE)),'bytes':len(b),'sha256':sha(b)})
 f=json.loads((ROOT/'frozen-references.json').read_text());s=json.loads((ROOT/'source-references.json').read_text());refs={x['path']:x for x in f['files']}
 for x in s['references']:refs[x['path']]={k:x[k] for k in ['path','bytes','sha256']}
 return {'schema':'NE-maps-full-assets-v1','hash_algorithm':'SHA256','owned_artifacts':entries,'external_original_references':sorted(refs.values(),key=lambda x:x['path']),'external_historical_authority_path':'data/coordinator-priority-acceptance.json','excluded_self_only':['maps/asset-manifest.json'],'no_cycle':'Validation result does not pin the manifest. Manifest self is externally byte-pinned by coordinator finish/review. No reverse acceptance hash or mutable coordinator aggregate dependency.','maximum_owned_bytes':max(x['bytes'] for x in entries),'all_owned_assets_strictly_below_40000000':True}
if __name__=='__main__':
 j=manifest();save_json(ROOT/'asset-manifest.json',j);print(len(j['owned_artifacts']),'owned assets;',len(j['external_original_references']),'external exact references; max',j['maximum_owned_bytes'])
