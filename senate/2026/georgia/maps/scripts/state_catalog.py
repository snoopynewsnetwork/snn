#!/usr/bin/env python3
"""Reproduce the official anonymous-client catalog chain without overwriting evidence."""
import argparse, hashlib, json, re, time, urllib.parse
from acquire import capture, entity
p=argparse.ArgumentParser();p.add_argument('--prefix',required=True,help='New immutable observation ID prefix');a=p.parse_args()
def get(k,u,parent=None,**kwargs):return capture(a.prefix+k,u,a.prefix+parent if parent else None,**kwargs)
root='https://www.legis.ga.gov/'
s=get('shell',root+'joint-office/reapportionment');script=next(u for u in re.findall(r'<script[^>]+src="([^"]+)',entity(s).decode()) if u.startswith('main.'))
j=get('client',urllib.parse.urljoin(root,script),'shell');js=entity(j).decode()
api=re.search(r'apiUrl:"([^"]+)',js)[1];obscure=re.search(r'obscureKey:"([^"]+)',js)[1]
# Literal algorithm from refreshToken/getKey in the retained public main client.
salt=re.search(r'SHA512\("([^"]+)"\+\w+\.a\.obscureKey',js)[1]
ms=str(int(time.time()*1000));key=hashlib.sha512((salt+obscure+'letvarconst'+ms).encode()).hexdigest()
t=get('anonymous-bootstrap',api+'authentication/token?'+urllib.parse.urlencode({'key':key,'ms':ms}),'client',note='Published anonymous bootstrap; no account credentials')
token=json.loads(entity(t));c=get('catalog',api+'Reapportionment/Page','anonymous-bootstrap',headers={'Authorization':'Bearer '+token})
data=json.loads(entity(c))
def walk(x):
    if isinstance(x,dict):
        if x.get('title','')=='Statewide Voting Precincts (2024)':
            r=get('precinct2024',x['url'],'catalog');print(json.dumps({k:r[k] for k in ['id','status','entity_bytes','entity_sha256']}))
        for v in x.values():walk(v)
    elif isinstance(x,list):
        for v in x:walk(v)
walk(data)
