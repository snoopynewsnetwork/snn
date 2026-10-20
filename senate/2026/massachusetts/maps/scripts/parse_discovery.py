from acquire import *
import re,json
S=M.parent

def lines(glob):
 d={}
 for f in sorted((M/'web').glob(glob)):
  s=f.read_text()
  for m in re.finditer(r'\bL(\d+):\s?([\s\S]*?)(?=\bL\d+:|\Z)',s):
   n=int(m[1]);t=m[2].strip();d[n]=t
 return d

def expand(n):
 for a,b in [('W. ','West '),('E. ','East '),('N. ','North '),('S. ','South ')]:
  if n.startswith(a):return b+n[len(a):]
 return n
c=json.loads((S/'data/turnout/priority-set.json').read_bytes());priority=set(x['literal_tuple'][0]for x in c['all_unit_order']if x['in_minimum80']);allnames=set(x['literal_tuple'][0]for x in c['all_unit_order'])
d=lines('directory-*.txt');entries=[];heads=[(n,t[4:])for n,t in sorted(d.items())if t.startswith('### ')and t[4:]!='Connect with Us']
for i,(n,name)in enumerate(heads):
 end=heads[i+1][0]if i+1<len(heads)else 2624;block='\n'.join(d.get(j,'')for j in range(n,end));links=[dict(id=int(k),text=t,domain=dom)for k,t,dom in re.findall(r'\ue200cite\ue202(\d+)†([^†\ue201]+)†([^\ue201]+)\ue201',block)]
 if links:entries.append(dict(name=name,start_line=n,raw_block=block,links=links))
# Preserve duplicate Harvard and wrong Lynn homepage as source observations, no repairs.
dump(M/'municipal-directory.json',dict(source='https://www.sec.state.ma.us/divisions/cis/contact/town-contact.htm',representation='numbered research-web text, NOT original HTML; original direct response is challenge shell',entries=entries))
maplines=lines('state-maps*.txt');maps=[]
for n,t in sorted(maplines.items()):
 if n<369:continue
 m=re.search(r'^(.*?)\s*\|\s*\ue200cite\ue202(\d+)†View Maps?',t)
 if m:maps.append(dict(name=m[1].strip(),link_id=int(m[2]),line=n))
dump(M/'state-map-links.json',maps)
requests=[]
for name in sorted(priority):
 ex=expand(name)
 if name=='Manchester-by-the-Sea':ex='Manchester By The Sea'
 for x in maps:
  if x['name'].lower()==ex.lower()or x['name'].lower().startswith(ex.lower()+' with subprecincts'):
   requests.append(dict(parent_literal=name,**x))
dump(M/'state-map-requests.json',requests)
print('directory entries',len(entries),'names',len(set(x['name']for x in entries)),'maps',len(maps),'priority map requests',len(requests),'missing',[n for n in priority if not any(x['parent_literal']==n for x in requests)])
local=[]
for name in sorted(allnames):
 hits=[x for x in entries if x['name']==expand(name)]
 local.append(dict(parent_literal=name,in_priority=name in priority,directory_entries=hits,requested_link_id=next((z['id']for x in hits for z in x['links']if 'Department Directory'in z['text']),None)))
dump(M/'local-requests.json',local);print('all directory parents',len(local),'missing',[x['parent_literal']for x in local if not x['directory_entries']])
