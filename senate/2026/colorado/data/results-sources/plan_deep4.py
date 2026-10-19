#!/usr/bin/env python3
import json,gzip,re,urllib.parse,zlib
from pathlib import Path
from inspect_sources import read_receipt
ROOT=Path(__file__).resolve().parent;STATE=ROOT.parents[1]
rs=json.loads((ROOT/'acquisition.json').read_text());pages=json.loads(gzip.decompress((ROOT/'observed-pages.json.gz').read_bytes()));done={r.get('requested_url',r['url']).split('#')[0] for r in rs};by={r['id']:r for r in rs};plan=[]
def add(u,parent,county,basis,proof):
 if not u.startswith(('http://','https://')) or u in done:return
 done.add(u);plan.append(dict(id='deep4-'+str(len(plan)+1),url=u,parent=parent,county=county,basis=basis,constructor=proof))
for r in rs:
 v=pages.get(r['id']);id=r['id']
 if not v:continue
 if 'clarityelections.com' in r['final_url']:
  for sc in v['scripts']:
   body=sc['body'];src=dict(sc['attributes']).get('src','')
   if re.search(r'(?:^|/)main[^/]*\.js$',src):
    u=urllib.parse.urljoin(r['final_url'],src)
    sr=next((z for z in rs if z['url']==u and z['status']==200),None)
    if sr:
     b=read_receipt(sr);enc=next((v for k,v in sr['headers'].items() if k.lower()=='content-encoding'),'');b=gzip.decompress(b) if enc=='gzip' else zlib.decompress(b) if enc=='deflate' else b;s=b.decode(errors='replace')
     if 'web.json' in s and 'WebConfig' in s:add(urllib.parse.urljoin(r['final_url'],'web.json'),sr['id'],r['county'],'Actual public app ./WebConfig constructor, literal WebConfig web.json; original observed leaf IDs only',{'app_receipt':sr['id'],'leaf_receipt':id,'literal':'web.json','construction':'./${FileName.WebConfig}'})
    else:add(u,id,r['county'],'Literal app main script needed to inspect constructor',sc)
   m=re.search(r"var url=\s*'([^']+)'",body)
   if m:add(urllib.parse.urljoin(r['final_url'],m[1]),id,r['county'],'Literal version XHR GET from actual root constructor',body)
 elif id=='deep3-23':pass
 elif id in ['deep3-39','deep3-41']:
  for a in v['links']:
   if re.search('clarityelections|Final.Official|Statement.of.Votes',a['resolved_url']+' '+a['text'],re.I):add(a['resolved_url'].split('#')[0],id,r['county'],'Literal county archive result/export link',a)
 elif id=='deep2-92':
  for a in v['links']:
   if a['text'] in ['Unofficial Results – June 30 at 9 p.m.','Final Official Results – July 21 at 8 a.m.']:add(a['resolved_url'],id,r['county'],'Literal dated complete result release: '+a['text'],a)
# RequireJS data-main is an actual constructor; inspect module dependencies without private APIs.
r=by['deep3-23'];s=read_receipt(r).decode();print('Denver module',s)
for a in ['sos-main','sos-linked-65','state-follow-136']:
 for link in pages[a]['links']:
  if re.search('mailBallotsFAQ|countmyballot|signature|court|federal|UOCAVA.*Manual|overseas.*manual',link['text']+' '+link['resolved_url'],re.I):add(link['resolved_url'],a,'STATE','Literal current guidance link',link)
for id,url in [('court-current','https://www.supremecourt.gov/opinions/25pdf/26a305_4g15.pdf'),('clerks-current','https://www.clerkandrecorder.org/2026-general-election')]:add(url,None,'STATE','Existing qualified primary original URL; independently rechecked current response',None)
(ROOT/'requests-deep4.json').write_text(json.dumps(plan,indent=2)+'\n');print('requests',len(plan))
