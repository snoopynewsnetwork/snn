#!/usr/bin/env python3
"""Bounded discovery from actual constructors, never enumerate race/unit IDs."""
import json,gzip,re,sys,urllib.parse,zlib
from pathlib import Path
from inspect_sources import read_receipt
ROOT=Path(__file__).resolve().parent
rs=json.loads((ROOT/'acquisition.json').read_text());pages=json.loads(gzip.decompress((ROOT/'observed-pages.json.gz').read_bytes()));done={r.get('requested_url',r['url']).split('#')[0] for r in rs};by={r['id']:r for r in rs};plan=[]
def add(u,parent,county,basis,proof):
 if not u.startswith(('http://','https://')) or u in done:return
 done.add(u);plan.append(dict(id='feed-'+str(len(rs))+'-'+str(len(plan)+1),url=u,parent=parent,county=county,basis=basis,constructor=proof))
def text(r):
 b=read_receipt(r);enc=next((v for k,v in r['headers'].items() if k.lower()=='content-encoding'),'');return (gzip.decompress(b) if enc=='gzip' else zlib.decompress(b) if enc=='deflate' else b).decode(errors='replace')
for r in rs:
 v=pages.get(r['id']);id=r['id']
 if v and 'clarityelections.com' in r['final_url']:
  for sc in v['scripts']:
   body=sc['body'];src=dict(sc['attributes']).get('src','')
   m=re.search(r"originalUrlArray\[0\] \+ '(web\.[0-9]+)'",body)
   if m:
    vr=next((z for z in rs if z['url']==urllib.parse.urljoin(r['final_url'],'versions.txt')),None)
    if vr and vr['status']==404:add(r['final_url']+m[1]+'/',id,r['county'],'Actual root redirect default after versions.txt 404',body)
   if re.search(r'(?:^|/)main[^/]*\.js$',src):
    u=urllib.parse.urljoin(r['final_url'],src);sr=next((z for z in rs if z['url']==u and z['status']==200),None)
    if sr:
     t=text(sr)
     if 'web.json' in t and 'WebConfig' in t:add(urllib.parse.urljoin(r['final_url'],'web.json'),sr['id'],r['county'],'Public app WebConfig constructor',{'leaf_receipt':id,'app_receipt':sr['id'],'literal':'web.json'})
    else:add(u,id,r['county'],'Literal public main script',sc)
 if r['url'].endswith('web.json') and r['status']==200:
  conf=json.loads(text(r));path='/{State}{county}/{EID}/current_ver.txt'.format(county=('/'+conf['County']) if conf['County'] else '',**conf);u=conf['jsonUri'].rstrip('/')+path
  # Scope from web.json itself; filenames and getBaseUri are observed in parent script.
  add(u,id,r['county'],'Actual getBaseUri(State, County, EID, FileName.Version); current_ver.txt literal in script',{'web_config_receipt':id,'web_config_complete':conf,'constructor_script':r['parent'],'literal':'current_ver.txt'})
 if r['url'].endswith('current_ver.txt') and r['status']==200:
  vr=text(r).strip();assert vr.isdigit(),(id,vr)
  u=r['url'].rsplit('/',1)[0]+'/'+vr+'/json/config.json'
  add(u,id,r['county'],'Actual getUri(State,County,EID,version,FileName.Config); observed version body',{'version_receipt':id,'version_literal':vr,'constructor_script':by[r['parent']]['parent']})
 if r['url'].endswith('/json/config.json') and r['status']==200:
  conf=json.loads(text(r));print('CONFIG',id,conf)
  lang=conf.get('lang');assert isinstance(lang,str)
  for filename in ['electionsettings.json','summary.json','status.json','details.json']:
   # Only files literally enumerated in inspected vendor script; selected complete products.
   add(r['url'].rsplit('/',1)[0]+('/'+lang if filename in ['electionsettings.json','summary.json'] else '')+'/'+filename,id,r['county'],'Actual getUri: config.lang for electionsettings/summary; no lang for status/details; literal filename enum',{'configuration_receipt':id,'lang_literal':lang,'filename_literal':filename})
# Actual Denver main RequireJS dependency and default header XHR, no route ID supplied.
r=by['deep3-23']
add('https://denvergov.org/electionresults/App/services/datacontext.js','deep3-23','Denver','RequireJS literal services/datacontext module relative to data-main',{'literal':'services/datacontext'})
add('https://denvergov.org/electionresults/Home/GetElectionHeaderinfo','deep3-23','Denver','Actual LoadHeader $.ajax URL constructor for observed default page',{'test':'https://denvergov.org/electionresults','literal':'/Home/GetElectionHeaderinfo','method':'GET default'})
(ROOT/'requests-feed.json').write_text(json.dumps(plan,indent=2)+'\n');print('requests',len(plan))
