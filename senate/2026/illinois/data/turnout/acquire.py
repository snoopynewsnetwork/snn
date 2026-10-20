#!/usr/bin/env python3
"""Retain public official responses; never write outside this assignment.

Requires requests and beautifulsoup4. Original shared bodies are read-only inputs.
No guessed election/candidate IDs: detail links come from original statewide HTML.
Run with --details / --controls; previously recorded successful captures are reused.
"""
from pathlib import Path
import argparse, datetime, gzip, hashlib, json
from urllib.parse import urljoin
import requests
from concurrent.futures import ThreadPoolExecutor
import sys
sys.dont_write_bytecode=True
from bs4 import BeautifulSoup

D = Path(__file__).resolve().parent
S = D/'source'
N = D.parent/'news'
UA='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
def sha(b): return hashlib.sha256(b).hexdigest()
def shared(sid):
    m = next(x for x in json.loads((N/'manifest.json').read_text()) if x['id']==sid)
    z=(N/m['asset']).read_bytes(); b=gzip.decompress(z)
    assert sha(z)==m['stored_sha256'] and sha(b)==m['raw_sha256'] and len(b)==m['bytes']
    return m,b
def capture(sid,url,parent,method='GET',data=None):
    S.mkdir(exist_ok=True)
    p=S/(sid+'.receipt.json')
    if p.exists():
        a=json.loads(p.read_text())
        if a.get('status')==200:
            z=(S/a['asset']).read_bytes(); assert sha(z)==a['stored_sha256']
            b=gzip.decompress(z); assert sha(b)==a['raw_sha256']
            return a,b
        history=S/'attempts';history.mkdir(exist_ok=True)
        (history/(sid+'-'+sha(p.read_bytes())[:16]+'.receipt.json')).write_bytes(p.read_bytes())
    a={'id':sid,'requested_url':url,'parent':parent,'method':method,'retrieved_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    if data is not None:a['public_form_fields']=data
    try:
        r=requests.request(method,url,data=data,headers={'User-Agent':UA},timeout=(45,90))
        b=r.content; z=gzip.compress(b,mtime=0); asset=sid+'-'+sha(b)[:16]+'.body.gz'; (S/asset).write_bytes(z)
        a.update(status=r.status_code,final_url=r.url,request_headers=dict(r.request.headers),headers=dict(r.headers),redirects=[{'url':h.url,'status':h.status_code,'headers':dict(h.headers)} for h in r.history],asset=asset,raw_sha256=sha(b),stored_sha256=sha(z),raw_bytes=len(b),stored_bytes=len(z))
    except requests.RequestException as e:
        b=b'';a['error']=str(e)
    a['finished_at_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();p.write_text(json.dumps(a,indent=2)+'\n')
    print(sid,a.get('status'),len(b),flush=True)
    return a,b
def contest_table(body,year):
    soup=BeautifulSoup(body,'html.parser')
    name='PRESIDENT AND VICE PRESIDENT' if year==2024 else 'UNITED STATES SENATOR'
    label=soup.find(string=lambda x:x and x.strip()==name)
    assert label is not None
    return label.find_parent('div').find_next('table')
def select_form(sid,a,b,name,value):
    s=BeautifulSoup(b,'html.parser');sel=s.find('select',attrs={'name':name});assert sel is not None
    assert sel.find('option',value=value) is not None
    assert '__doPostBack' in sel.get('onchange','') and name in sel['onchange'],sel
    form=sel.find_parent('form');payload={x['name']:x.get('value','') for x in form.select('input[type=hidden][name]')}
    for x in form.select('select[name]'):
        o=x.find('option',selected=True) or x.find('option');payload[x['name']]=o.get('value',o.get_text())
    payload[name]=value;payload['__EVENTTARGET']=name;payload['__EVENTARGUMENT']=''
    out,raw=capture(sid,urljoin(a['final_url'],form.get('action')or a['final_url']),{'source':a['id'],'selector':name,'option':value,'observed_event':sel['onchange']},'POST',payload)
    assert out.get('status')==200,(sid,out.get('error'))
    ss=BeautifulSoup(raw,'html.parser');assert ss.find('select',attrs={'name':name}).find('option',selected=True)['value']==value
    return out,raw
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--details',action='store_true');ap.add_argument('--controls',action='store_true');ap.add_argument('--linked-controls',action='store_true');ap.add_argument('--election-controls',action='store_true');ap.add_argument('--authority-pages',action='store_true');ap.add_argument('--replay-receipts',action='store_true');args=ap.parse_args()
    if args.replay_receipts:
        # Reproduce ad-hoc literal-link followups too. Successful originals are
        # immutable inputs and reused. Copy the source tree before refreshing.
        for p in sorted(S.glob('*.receipt.json')):
            a=json.loads(p.read_text())
            capture(a['id'],a.get('requested_url',a.get('url')),a.get('parent'),a.get('method','GET'),a.get('public_form_fields'))
    if args.details:
        for year in [2024,2020,2022]:
            sid=f'sos-observed-{year}-federal-statewide-page';a,b=shared(sid)
            for i,tr in enumerate(contest_table(b,year).find_all('tr')):
                anchor=tr.find('a',href=True)
                if anchor:capture(f'detail-{year}-{i:02}',urljoin(a['final_url'],anchor['href']),{'shared_source':sid,'row':i,'literal_href':anchor['href']})
    if args.controls:
        for sid,url,parent in [
            ('turnout-index','https://www.elections.il.gov/ElectionOperations/VoterTurnout.aspx?MID=fVf30XCcBCY%3D&T=637204911330922199','web primary search result'),
            ('registration-counts','https://www.elections.il.gov/VotingAndRegistrationSystems/RegistrationCounts.aspx','web primary search result'),
            ('registration-voting','https://www.elections.il.gov/ElectionOperations/RegistrationAndVoting.aspx','web primary search result'),
            ('candidate-list-2024','https://www.elections.il.gov/ElectionOperations/CandidateList.aspx?ElectionID=9huvqbsiUWA%3D&OfficeID=u1Q%2F9tNM5DS2IFp9lLcghg%3D%3D','web primary search result'),
            ('nara-vote-2024','https://www.archives.gov/files/electoral-college/2024/vote-illinois.pdf','NARA primary search result'),
        ]:capture(sid,url,parent)
    if args.linked_controls:
        a=json.loads((S/'registration-counts.receipt.json').read_text());b=gzip.decompress((S/a['asset']).read_bytes());s=BeautifulSoup(b,'html.parser')
        link=s.find('a',string='ASCII Comma Delimited');assert link
        capture('registration-current-csv',urljoin(a['final_url'],link['href']),{'source':'registration-counts','href':link['href']})
        a=json.loads((S/'candidate-list-2024.receipt.json').read_text());b=gzip.decompress((S/a['asset']).read_bytes());s=BeautifulSoup(b,'html.parser')
        link=s.find('a',string='Print This List');assert link
        capture('candidate-list-2024-print',urljoin(a['final_url'],link['href']),{'source':'candidate-list-2024','href':link['href']})
        capture('masterpage-js','https://www.elections.il.gov/Scripts/MasterPage.js',{'source':'turnout-index','literal_script_src':'/Scripts/MasterPage.js'})
    if args.election_controls:
        a,b=capture('turnout-selector-UA','https://www.elections.il.gov/ElectionOperations/VoterTurnout.aspx?MID=fVf30XCcBCY%3D&T=637204911330922199','turnout-index with normal browser UA')
        for year,value in [(2024,'66'),(2022,'62'),(2020,'58')]:
            out,raw=select_form(f'turnout-{year}',a,b,'ctl00$ContentPlaceHolder1$ddlElections',value)
            for i,link in enumerate(BeautifulSoup(raw,'html.parser').select('a[href]')):
                if any(w in link.get_text().lower() for w in ['download','comma','excel','pdf','adobe']):
                    capture(f'turnout-{year}-linked-{i}',urljoin(out['final_url'],link['href']),{'source':out['id'],'literal_href':link['href'],'label':link.get_text(' ',strip=True)})
    if args.authority_pages:
        for year in [2024,2020,2022]:
            parent='sos-2024-county-totals' if year==2024 else f'sos-observed-{year}-county-page'
            orig,_=shared(parent);a,b=capture(f'county-selector-{year}-UA',orig['final_url'],{'shared_source':parent})
            sel=BeautifulSoup(b,'html.parser').find('select',attrs={'name':'ctl00$ContentPlaceHolder1$ddlJurisdictions'})
            def fetch(o):
                return select_form(f'authority-{year}-{int(o["value"]):03}',a,b,sel['name'],o['value'])
            # Independent public read-only requests, bounded to three at once.
            with ThreadPoolExecutor(max_workers=3) as pool:
                futures=[pool.submit(fetch,o) for o in sel.find_all('option')]
                errors=[]
                for f in futures:
                    try:f.result()
                    except Exception as e:errors.append(repr(e))
                if errors:print('SOURCE ERRORS',year,errors,flush=True)
if __name__=='__main__':main()
