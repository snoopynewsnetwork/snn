from common import *
from acquire import *
import concurrent.futures,re,sys

def initial():
 # Discover once during research; offline build reads only these fixed individual receipt pins.
 selected=[]
 for p in sorted((S/'data/results-sources/requests').glob('*.json')):
  k=p.stem
  if k.startswith('bluebook-') or k in ['sos-county-bluebook','sos-county-directory','sos-history'] or (k.startswith('county-') and not any(x in k for x in ['publication','chain-link','result'])):
   r=reuse(str(p.relative_to(S)));selected.append('maps/references/'+k+'.json')
 save('maps/references/navigation-fixed.json',selected)

def candidates():
 out=[]
 for name in load('maps/references/navigation-fixed.json'):
  r=load(name)['receipt']
  for l in links_of(r):
   if re.search(r'precinct|district.map|vot.*map|map.*vot|\bgis\b|mapping|geographic|district.*boundar',l['text']+' '+l['url'],re.I):out.append({'parent':r['key'],**l})
 save('maps/history/initial-map-links.json',out)
 for x in out:print(x['parent'],x['text'].strip()[:90],x['url'])

def batch(plan):
 def one(x):
  r=fetch(x['key'],x['url'],x['parent'],x.get('role','map authority navigation'))
  return {'key':x['key'],'statuses':[e['status'] for e in r['entities']],'error':r['error'],'bytes':sum(e['body']['raw_bytes'] for e in r['entities'] if e.get('body'))}
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
  for r in pool.map(one,plan):print(json.dumps(r),flush=True)
if __name__=='__main__':
 if sys.argv[1]=='initial':initial();candidates()
 else:batch(load(sys.argv[1]))
