from common import *
from concurrent.futures import ThreadPoolExecutor
m=json.loads((HERE/'receipts/state-directory.json').read_bytes());h=HTML(body(m).decode());data={x['name']:x.get('value','') for x in h.inputs if x.get('type')=='hidden'}
s=h.selects[0];data[s['attrs']['name']]='-1';data.update(__EVENTTARGET=s['attrs']['name'],__EVENTARGUMENT='')
x=fetch('state-directory-all',m['url'],m['id'],basis='actual public selector All Election Authorities=-1; complete form state',method='POST',data=data);inspect(x);print('directory',x.get('status'))
seeds=[]
for parent in ['state-november','state-home']:
 m=json.loads((HERE/'receipts'/f'{parent}.json').read_bytes());h=HTML(body(m).decode())
 for a in h.links:
  t=a['text'].strip();hr=a['literal_href']
  if t in ['Unofficial Election Results','Search Filed Candidates','Candidate Filing and Results']:
   seeds.append(({'Unofficial Election Results':'state-unofficial','Search Filed Candidates':'state-candidates','Candidate Filing and Results':'state-filing-menu'}[t],urljoin(m['final_url'],hr),parent,hr))
seen=set()
for id,url,p,hr in seeds:
 if id in seen:continue
 seen.add(id);m=fetch(id,url,p,hr,basis='literal current navigation link');inspect(m);print(id,m.get('status'))
