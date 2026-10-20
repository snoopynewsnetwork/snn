"""Bounded navigation plan; only literal observed anchors, no invented endpoints."""
import json,re
from html_tools import ROOT,latest,links,receipts

def plan():
    discovery=json.loads((ROOT/'county-site-discovery.json').read_bytes())
    jobs=[];audit=[]; seen={r['requested_url'] for _,r in receipts()}
    for d in discovery:
        n,r=next((n,r) for n,r in reversed(receipts()) if r['requested_url']==d['url'])
        ls=links(n) if r['hops'] else [];chosen=[];known=set()
        for x in sorted(ls,key=lambda x:(-('result' in (x['text']+' '+x['url']).lower()),-('elect' in (x['text']+' '+x['url']).lower()))):
            combined=(x['text']+' '+x['url']).lower()
            if re.search(r'elect|probat',combined) and not re.search(r'contact|login|wp-admin|partner|register|registration|facebook|twitter|mailto:|tel:',combined) and x['url'].startswith(('http://','https://')) and x['url'] not in known:
                known.add(x['url']);chosen.append(x)
            if len(chosen)>=3:break
        for x in chosen:
            if x['url'] not in seen:
                jobs.append({'url':x['url'],'parent':dict(x,county=d['text'].strip())});seen.add(x['url'])
        audit.append({'county':d['text'].strip(),'authority_receipt':n,'all_published_links':ls,'selected_election_probate_links':chosen,'bounded_depth':1})
    for u,pattern in [('https://www2.alabamavotes.gov/electionNight/statewideResultsByContest.aspx?ecode=1001290','chooseCounty.aspx'),('https://alison.legislature.state.al.us/law-institute-election-handbook-extended','Alabama_Election_Handbook_22nd_Edition.pdf')]:
        n,r=latest(u)
        for x in links(n):
            if pattern in x['url'] and x['url'] not in seen:
                jobs.append({'url':x['url'],'parent':x});seen.add(x['url'])
    extras=['https://www.marioncountyal.org/home/departments/probate-office/elections/','https://www.barbourcountyal.gov/172/Probate-Office','https://www.winstoncountyprobate.org/Default.asp','https://washprobate.com/','https://jeffcoprobatecourt.com/elections/','https://elections.mobilecountyal.gov/',
            'https://bullockal.com/','https://www.halecountyal.gov/courts','https://clay.alacourt.gov/']
    for u in extras:
        if u not in seen:jobs.append({'url':u,'parent':'Observed primary official office search result; no guessed IDs'})
    (ROOT/'county-chain-level1.json').write_text(json.dumps(audit,indent=2)+'\n')
    (ROOT/'chain1-jobs.json').write_text(json.dumps(jobs,indent=2)+'\n')
    print('jobs',len(jobs))
if __name__=='__main__':plan()
