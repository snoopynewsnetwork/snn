#!/usr/bin/env python3
"""Second-level inspection: actual published election-results, current-election and polling links.
All selected links are retained for audit. No vendor endpoints are synthesized.
"""
import json,re,sys
from urllib.parse import urlparse,urldefrag,quote
from discover import ROOT,STATE,slug,batch,dump
contract=json.loads((STATE/'data/turnout/priority-set.json').read_text())
parents=sorted({x['municipal_parent_label'] for x in contract['all_units'][:143]})
mode=sys.argv[1] if len(sys.argv)>1 else 'pages'
jobs=[]; review=[]
for name in parents:
    pref='municipal-'+slug(name)
    links=[]
    for f in sorted((ROOT/'derived').glob(pref+'-*.json')):
        p=json.loads(f.read_text())
        if p['http_status']!=200 or (name=='Strafford' and 'stratford' in p['url']): continue
        host=urlparse(p['url']).hostname or ''
        for a in p['links']:
            if not a['url'].startswith(('http://','https://')):continue
            t=a['text']; path=urlparse(a['url']).path
            if 'stratford' in a['url'] and name=='Strafford':continue
            isdoc=bool(re.search(r'\.(pdf|xlsx?|csv)($|\?)|/DocumentCenter/View/|/Archive.aspx\?ADID=|docview.aspx',a['url'],re.I))
            if (mode=='documents')!=isdoc:continue
            if re.search(r'campaign|candidate.filing|register|registration|absentee|application|electioneering|traffic|warrant|job|bid.opportunities|minutes',t,re.I):continue
            score=0
            if mode=='documents':
                score=30*bool(re.search(r'2024.*(general|president).*(result|return)|(general|president).*2024.*(result|return)|result.*(november.5.*2024|2024.*general)',t,re.I))
                score+=22*bool(re.search(r'2026.*(state.primary|primary).*(result|return)|(primary).*(result|return).*2026',t,re.I))
                score+=18*bool(re.search(r'2026.*post.election.return',t,re.I))
            else:
                score=40*bool(re.fullmatch(r'\s*(Election Results|State Election Results|Elections Results|Past Election Results)\s*',t,re.I))
                score+=25*bool(re.search(r'2026.*general.election|general.election.*2026|polling.locations|polling.places|polling.hours|voting.locations',t,re.I))
                score+=15*bool(re.fullmatch(r'\s*(Town Clerk.*|City Clerk.*|Elections.*|Voting.*)\s*',t,re.I))
            if score:links.append({**a,'score':score,'parent_source_id':p['source_id']})
    unique={a['url']:a for a in sorted(links,key=lambda a:a['score'])}
    ranked=sorted(unique.values(),key=lambda a:(-a['score'],len(a['url'])))
    picks=ranked[:(1 if mode=='documents' else 3)]
    review.append({'municipality':name,'selected':picks,'all_candidates':ranked})
    for i,a in enumerate(picks,1):
        u=quote(urldefrag(a['url'])[0],safe=':/?&=%+#@!$,;()')
        jobs.append((pref+'-'+mode+str(i),u,a['parent_source_id']))
dump(ROOT/('follow-'+mode+'-review.json'),review)
batch(jobs)
