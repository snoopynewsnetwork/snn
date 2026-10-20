import json,re
from html_tools import ROOT,links,receipts

def plan():
    jobs=[];audit=[];seen={r['requested_url'].split('#')[0] for _,r in receipts()}
    inputs=json.loads((ROOT/'chain1-jobs.json').read_bytes())
    for j in inputs:
        n,r=next((n,r) for n,r in reversed(receipts()) if r['requested_url']==j['url'])
        if not r['hops'] or r['hops'][-1]['status']!=200:continue
        if not any('text/html' in v for k,v in r['hops'][-1]['headers'] if k.lower()=='content-type'):continue
        ls=links(n);chosen=[];known=set()
        for x in sorted(ls,key=lambda x:(-('result' in (x['text']+' '+x['url']).lower()),-('elect' in x['text'].lower()))):
            label=(x['text']+' '+x['url'].split('://')[-1].partition('/')[2]).lower()
            if re.search(r'result|election|voting',label) and not re.search(r'contact|login|admin/|partner|register|registration|facebook|twitter|mailto:|tel:|form|application|myinfo|map|polling',label) and x['url'].startswith(('http://','https://')) and x['url'].split('#')[0] not in seen and x['url'] not in known:
                chosen.append(x);known.add(x['url']);seen.add(x['url'].split('#')[0])
            if len(chosen)>=3:break
        for x in chosen:
            jobs.append({'url':x['url'],'parent':dict(x,county=j['parent'].get('county') if isinstance(j['parent'],dict) else None)})
        audit.append({'receipt':n,'all_published_links':ls,'selected_results_election_links':chosen,'bounded_depth':2})
    extra=['https://www.sos.alabama.gov/alabama-votes/voter/election-laws','https://www.sos.alabama.gov/ballot-harvesting-prohibition','https://media.ca11.uscourts.gov/opinions/pub/files/202413111.cert.pdf','https://www.supremecourt.gov/opinions/25pdf/24-1260_g3cn.pdf']
    for u in extra:jobs.append({'url':u,'parent':'Observed exact primary law/order search result; full original body required'})
    (ROOT/'county-chain-level2.json').write_text(json.dumps(audit,indent=2)+'\n')
    (ROOT/'chain2-jobs.json').write_text(json.dumps(jobs,indent=2)+'\n')
    print('jobs',len(jobs))
if __name__=='__main__':plan()
