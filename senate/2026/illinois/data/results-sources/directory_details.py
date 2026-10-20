from common import *
from concurrent.futures import ThreadPoolExecutor
m=json.loads((HERE/'receipts/state-directory.json').read_bytes());h=HTML(body(m).decode());s=h.selects[0];hidden={x['name']:x.get('value','') for x in h.inputs if x.get('type')=='hidden'}
opts=[x for x in s['options'] if int(x['attrs']['value'])>0 or x['attrs']['value']=='-2']
def work(x):
 id=x['attrs']['value'];d=dict(hidden);d[s['attrs']['name']]=id;d.update(__EVENTTARGET=s['attrs']['name'],__EVENTARGUMENT='')
 r=fetch('directory-detail-'+id,m['url'],m['id'],method='POST',data=d,basis='actual observed public authority selector '+x['text']+'='+id);inspect(r);return id,r.get('status')
with ThreadPoolExecutor(max_workers=3) as pool:
 for i,x in enumerate(pool.map(work,opts),1):
  if i%20==0 or i==len(opts):print(i,x,flush=True)
