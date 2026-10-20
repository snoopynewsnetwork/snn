from acquire import fetch,R
from inspect_sources import inspect
from pathlib import Path
import gzip,json,re,concurrent.futures
items=[]
for p in sorted((R/'structures').glob('bluebook-*.json.gz')):
 d=json.loads(gzip.decompress(p.read_bytes()));slug=p.name.removeprefix('bluebook-').removesuffix('.json.gz')
 a=[x for x in d['links'] if re.fullmatch(r'(www\.)?[a-zA-Z0-9.-]+\.(gov|org|us|net|com)/?',x['label'].strip())]
 assert len(a)==1,(slug,a)
 items.append(('county-'+slug+'-root',a[0]['resolved_url'],'bluebook-'+slug))
(R/'county-root-navigation.json').write_text(json.dumps(items,indent=2)+'\n')
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
 for r in ex.map(lambda x:fetch(*x),items):
  d=inspect(r);print(d['key'],d['status'],d['error'],flush=True)
