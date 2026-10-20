#!/usr/bin/env python3
"""Bounded public acquisition. Append complete receipts; never overwrite originals.
Original historical ZIP/PDF replay uses exact hashes in source/*references.json.
"""
import datetime,gzip,hashlib,json,pathlib,re,sys
from html.parser import HTMLParser
from urllib.parse import urljoin
import requests
BASE=pathlib.Path(__file__).resolve().parent
class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[]
    def handle_starttag(self,tag,attrs):
        if tag=='a':
            d=dict(attrs)
            if 'href' in d:self.links.append(d['href'])
def fetch(url,parent=None):
    now=datetime.datetime.now(datetime.timezone.utc).isoformat();r=requests.get(url,timeout=55);body=r.content;h=hashlib.sha256(body).hexdigest();out=BASE/'source/http';out.mkdir(exist_ok=True)
    # Reuse original shared immutable bodies by exact hash, including complete metadata.
    shared=BASE.parent/'turnout/source/http'/f'{h}.gz'
    if shared.exists() and hashlib.sha256(gzip.decompress(shared.read_bytes())).hexdigest()==h:
        p=shared;rel=str(pathlib.Path('../turnout/source/http')/p.name)
    else:
        p=out/(h+'.gz');p.write_bytes(gzip.compress(body,mtime=0));rel='source/http/'+p.name
    require=p.stat().st_size<40000000
    assert require
    d={'requested_url':url,'final_url':r.url,'retrieved_at_utc':now,'status':r.status_code,'headers':dict(r.headers),'redirects':[{'url':x.url,'status':x.status_code,'headers':dict(x.headers)} for x in r.history],'original_sha256':h,'original_bytes':len(body),'stored_path_relative_baselines':rel,'stored_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'stored_bytes':p.stat().st_size,'storage':'gzip.decompress entire stored body; requests-decoded entity','parent':parent}
    (out/(now.replace(':','')+'-'+h[:12]+'.receipt.json')).write_text(json.dumps(d,indent=2)+'\n');return body,d
def main():
    root='https://www.sos.alabama.gov/alabama-votes/voter/election-information/2026';body,d=fetch(root)
    l=Links();l.feed(body.decode());links=[urljoin(root,x) for x in l.links]
    targets=[x for x in links if any(s in x for s in ['2026GeneralElectionStateCertificationofDemocraticCandidates','2026GeneralElectionStateCertificationofRepublicanCandidates','2026GeneralElection-StateCertificationofIndependentCandidate','Amended_2026_Republican_Certification','ALGOPAmendedCertification-SD25'])]
    for url in dict.fromkeys(targets):fetch(url,root)
    # Existing controlling-law route; retain failures rather than substitute a bill.
    for sec in ['17-12-21','17-12-23']:
        fetch('https://alison.legislature.state.al.us/code-of-alabama?section='+sec,'https://alison.legislature.state.al.us/code-of-alabama')
    print(json.dumps({'parent':root,'selected_linked_publications':targets,'note':'bounded current certification check, not later-docket or statewide specimen exhaustion'}))
if __name__=='__main__':main()
