#!/usr/bin/env python3
"""Bounded municipal link-following, driven only by captured primary hrefs.
Usage: discover.py homes | clerks | elections. Inspect all candidates before interpretation.
"""
import concurrent.futures, json, re, sys
from urllib.parse import urlparse
from acquire import ROOT, acquire, dump
from inspect_html import inspect
STATE=ROOT.parent.parent
def slug(s): return re.sub('[^a-z0-9]+','-',s.lower()).strip('-')
def run(job):
    sid,url,parent=job
    m=acquire(sid,url,parent)
    x=inspect(sid)
    return {'source_id':sid,'url':url,'http_status':m['http_status'],'curl_exit':m['curl_exit'],
            'links':len(x['links']) if x else None}
def batch(jobs):
    out=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
        for x in ex.map(run,jobs): out.append(x); print(json.dumps(x),flush=True)
    return out
if __name__=='__main__':
    mode=sys.argv[1]
    contract=json.loads((STATE/'data/turnout/priority-set.json').read_text())
    parents=sorted({x['municipal_parent_label'] for x in contract['all_units'][:143]})
    if mode=='homes':
        directory=json.loads((ROOT/'derived/state-municipal-directory.json').read_text())
        jobs=[]; refs=[]
        for name in parents:
            found=[x for x in directory['links'] if x['text']==name]
            refs.append({'municipality':name,'directory_links':found})
            if found: jobs.append(('municipal-'+slug(name)+'-home',found[0]['url'],'state-municipal-directory'))
        dump(ROOT/'municipal-directory-matches.json',refs)
    else:
        jobs=[]; choices=[]
        for name in parents:
            pref='municipal-'+slug(name)
            sources=[ROOT/'derived'/(pref+'-home.json')]+list((ROOT/'derived').glob(pref+'-departments*.json'))+list((ROOT/'derived').glob(pref+'-alternate*.json'))
            if mode=='elections': sources=list((ROOT/'derived').glob(pref+'-clerk*.json'))+sources
            links=[]
            for source in sources:
                if not source.exists(): continue
                p=json.loads(source.read_text())
                if p['http_status']!=200: continue
                for a in p['links']:
                    if not a['url'].startswith(('http://','https://')): continue
                    t=a['text']+' '+urlparse(a['url']).path
                    if mode=='departments': score=10*bool(re.fullmatch(r'\s*(Departments|Town Departments|City Departments|Government|Town Government)\s*',a['text'],re.I))
                    elif mode=='clerks': score=10*bool(re.search(r'\b(city|town)[ -_]?clerk',t,re.I))+3*bool(re.search('election|voting',t,re.I))
                    else: score=15*bool(re.search(r'election.results|results.election|results.*202[246]',t,re.I))+5*bool(re.search('election|voting',t,re.I))
                    if score and not re.search(r'\.(pdf|xls|xlsx)$|/DocumentCenter/View/|/Archive.aspx',a['url'],re.I): links.append({**a,'score':score,'parent_source_id':p['source_id']})
            unique={a['url']:a for a in sorted(links,key=lambda a:a['score'])}
            ranked=sorted(unique.values(),key=lambda a:(-a['score'],len(a['url'])))
            picks=ranked[:(1 if mode in ('clerks','departments') else 2)]
            choices.append({'municipality':name,'candidates':ranked,'selected':picks})
            for i,a in enumerate(picks):
                tag={'clerks':'clerk-deep','departments':'departments','elections':'elections'}[mode]
                if name=='Strafford' and 'stratford' in a['url']: continue
                jobs.append((pref+'-'+tag+str(i+1),a['url'],a['parent_source_id']))
        dump(ROOT/(mode+'-link-review.json'),choices)
    batch(jobs)
