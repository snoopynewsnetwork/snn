"""Literal primary relations; no guessed map item identifiers."""
from common import *
import concurrent.futures,re

def inventory():
 c=json.loads((S/'data/turnout/priority-set.json').read_bytes());parents=c['county_contexts'];d=document('sos-clerks');directory={};current=None
 for n in d.nodes:
  if n['tag']=='h3':current=n['text'].strip();directory[current]=[]
  elif current:directory[current].append(n)
 maps={};d=document('sos-base')
 for i,n in enumerate(d.nodes):
  if n['tag']=='tr'and 'Open File'in n['text']:
   ns=d.descendants(i);cells=[x for x in ns if x['tag']=='td'];name=cells[0]['text'].strip();aa=[x for x in ns if x['tag']=='a'];maps[name]=[{'href':x['attrs']['href'],'text':x['text'],'attrs':x['attrs'],'position':x['position']}for x in aa]
 out=[]
 for p in parents:
  name=p['source_label'];key='Doña Ana'if name=='Dona Ana'else name;ns=directory[key];aa=[n for n in ns if n['tag']=='a'and n['attrs'].get('href','').startswith(('http:','https:'))]
  out.append({'parent':p,'directory_header_literal':key,'directory_nodes':ns,'directory_links':aa,'state_map_links':maps[name]})
 write(M/'directory-inventory.json',out);return out

def stage1():
 inv=inventory();jobs=[]
 for row in inv:
  f=row['parent']['fips']
  if row['directory_links']:
   a=row['directory_links'][0];jobs.append((f'county-{f}',a['attrs']['href'],'sos-clerks',a))
  a=row['state_map_links'][0];jobs.append((f'base-{f}',a['href'],'sos-base',a))
 for i,l in enumerate(links('sos-gis')):
  if l['text'].startswith('Click'):jobs.append((f'gis-link-{i}',l['url'],'sos-gis',l))
 with concurrent.futures.ThreadPoolExecutor(max_workers=6)as pool:
  for r in pool.map(lambda x:fetch(*x,timeout=35),jobs):print(r['id'],r.get('status'),r.get('error'),r.get('body',{}).get('raw_bytes'),flush=True)

def stage2():
 jobs=[];selected={}
 for row in json.loads((M/'directory-inventory.json').read_bytes()):
  f=row['parent']['fips'];name='county-'+f
  ls=links(name)if (M/'receipts'/(name+'.json')).exists() and original(name)else[]
  relevant=[l for l in ls if re.search(r'precinct|district.{0,12}map|maps.{0,15}district|\bGIS\b|polling.{0,20}(location|place)|voting.{0,12}location',l['text']+' '+l['url'],re.I)and not re.search(r'facebook|twitter|instagram|youtube|mailto:|\.jpg|\.png',l['url'],re.I)]
  # Prefer precinct/map sources over generic election navigation, retaining every observed link.
  ranked=sorted(enumerate(relevant),key=lambda il:(0 if re.search('precinct',il[1]['text'],re.I)else 1,il[0]))
  seen=set();chosen=[]
  for _,l in ranked:
   if l['url']not in seen:chosen.append(l);seen.add(l['url'])
   if len(chosen)>=3:break
  if not chosen:
   for l in ls:
    if re.search(r'^Elections?$|Election Information|Voting Information',l['text'],re.I)and l['url']not in seen:chosen.append(l);seen.add(l['url'])
    if len(chosen)>=1:break
  selected[f]={'complete_map_related_links':relevant,'selected_links':chosen,'all_landing_links':ls}
  for j,l in enumerate(chosen):jobs.append((f'local-{f}-{j+1}',l['url'],name,l))
 write(M/'county-link-research.json',selected)
 with concurrent.futures.ThreadPoolExecutor(max_workers=6)as pool:
  for r in pool.map(lambda x:fetch(*x,timeout=30),jobs):print(r['id'],r.get('status'),r.get('error'),r.get('body',{}).get('raw_bytes'),flush=True)
if __name__=='__main__':
 import sys
 stage1()if sys.argv[-1]=='1'else stage2()
