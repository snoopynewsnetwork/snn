from common import *
owned=[]
paths=[p for p in ROOT.rglob('*') if p.is_file() and p.name!='asset-manifest.json']+[GA/'official-results.md',GA/'data/official-results-sources.csv']
for p in sorted(paths):
 b=p.read_bytes();assert len(b)<40000000;owned.append({'path':str(p.relative_to(GA)),'bytes':len(b),'sha256':sha(b)})
save(ROOT/'asset-manifest.json',{'schema':'ga-official-results-manifest-v1','hash_scope':'owned excludes this manifest; external read-only pins have no reverse dependency','owned':owned,'external_originals':js(ROOT/'shared-inputs.json'),'external_frozen':js(ROOT/'frozen-inputs.json'),'external_derived':js(ROOT/'shared-derived-inputs.json')})
print('Manifest owned files',len(owned))
