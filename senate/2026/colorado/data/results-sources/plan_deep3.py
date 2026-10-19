#!/usr/bin/env python3
import json,gzip,re,sys,urllib.parse
from pathlib import Path
from inspect_sources import read_receipt,inspect
ROOT=Path(__file__).resolve().parent
rs=json.loads((ROOT/'acquisition.json').read_text());pages=json.loads(gzip.decompress((ROOT/'observed-pages.json.gz').read_bytes()));by={r['id']:r for r in rs};done={r.get('requested_url',r['url']).split('#')[0] for r in rs};plan=[]
def add(url,parent,county,basis,proof):
 if not url.startswith(('http://','https://')) or url in done:return
 done.add(url);plan.append(dict(id='deep3-'+str(len(plan)+1),url=url,parent=parent,county=county,basis=basis,constructor=proof))
for r in rs:
 v=pages.get(r['id']);id=r['id']
 if not v:continue
 if 'clarityelections.com' in r['final_url']:
  for sc in v['scripts']:
   body=sc['body'];m=re.search(r"originalUrlArray\[0\] \+ '(web\.[0-9]+)'",body)
   if m:
    version_url=urllib.parse.urljoin(r['final_url'],'versions.txt');vr=next((z for z in rs if z['url']==version_url),None)
    if vr and vr['status']==404:add(r['final_url']+m[1]+'/',id,r['county'],'Executed actual root redirect default branch after observed versions.txt 404',body)
   src=dict(sc['attributes']).get('src','')
   if re.search(r'(?:^|/)main[^/]*\.js$',src):add(urllib.parse.urljoin(r['final_url'],src),id,r['county'],'Literal public application script',sc)
 elif id in ['deep2-11','deep2-20','county-boulder-follow-3']:
  for a in v['links']:
   if 'ExportBallotReturns' in a['resolved_url']:add(a['resolved_url'],id,r['county'],'Literal administrative aggregate export link',a)
  for sc in v['scripts']:
   attrs=dict(sc['attributes'])
   if attrs.get('data-main'):add(urllib.parse.urljoin(r['final_url'],attrs['data-main']+'.js'),id,r['county'],'RequireJS actual data-main module resolution appends .js',sc)
 elif id in ['deep2-90','deep2-91','deep2-92','deep2-54','county-saguache-follow-2','county-san-miguel-follow-2','county-rio-blanco-follow-1','county-teller-follow-1','county-park-follow-1']:
  good=[]
  for a in v['links']:
   u=a['resolved_url'].split('#')[0];label=a['text']+' '+u
   if not a['text'] or u in done or re.search('Search/Results|CVR|Cast.Vote.Record|bid|200[0-9]|201[0-9]|202[0-3]|sample|judge|maps|candidates',label,re.I):continue
   if re.search('clarityelections|2026.primary|final.official|primary.*7.p.m|primary.*9.p.m|election.results',label,re.I):good.append(a)
  for a in good[:3]:add(a['resolved_url'].split('#')[0],id,r['county'],'Literal further result/document link: '+a['text'],a)
(ROOT/'requests-deep3.json').write_text(json.dumps(plan,indent=2)+'\n');print('requests',len(plan));print([(q['id'],q['county'],q['url']) for q in plan])
