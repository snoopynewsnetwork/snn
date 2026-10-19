"""Retain official originals; reuse shared news assets only after both hash checks.
Run from any directory. No Git or shared-file mutations. Python stdlib + requests.
"""
from pathlib import Path
import csv, datetime, gzip, hashlib, html, io, json, re, sys, urllib.parse
import requests

BASE=Path(__file__).resolve().parents[2]
OUT=BASE/'data/turnout'
NEWS=BASE/'data/news'
MANIFEST=OUT/'source/acquisition.json'
def sha(b): return hashlib.sha256(b).hexdigest()
def savejson(p,d): p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
receipts=json.loads(MANIFEST.read_text()) if MANIFEST.exists() else []
shared=json.loads((NEWS/'manifest.json').read_text())
def source(key,url=None,parent=None):
    found=next((r for r in receipts if r['id']==key),None)
    if found:
        b=gzip.decompress((BASE/found['path']).read_bytes());assert sha(b)==found['raw_sha256'];return b
    old=next((r for r in shared if r['id']==key),None)
    if old:
        stored=(NEWS/old['asset']).read_bytes();b=gzip.decompress(stored)
        assert sha(stored)==old['stored_sha256'] and sha(b)==old['raw_sha256']
        r=dict(old,path='data/news/'+old['asset'],storage='shared_read_only',parent_source_id=parent)
    else:
        start=datetime.datetime.now(datetime.timezone.utc).isoformat()
        response=requests.get(url,timeout=120)
        b=response.content;stored=gzip.compress(b,mtime=0)
        assert len(stored)<40_000_000
        p=OUT/'source'/(key+'.body.gz');p.write_bytes(stored)
        r=dict(id=key,url=url,final_url=response.url,retrieved_at_utc=start,status=response.status_code,
               headers=dict(response.headers),redirects=[dict(status=x.status_code,url=x.url,headers=dict(x.headers)) for x in response.history],
               raw_sha256=sha(b),stored_sha256=sha(stored),bytes=len(b),stored_bytes=len(stored),path=str(p.relative_to(BASE)),
               storage='owned',parent_source_id=parent)
    receipts.append(r);savejson(MANIFEST,receipts)
    assert r['status']==200,(key,r['status'])
    print(key,len(b),flush=True);return b
def links(b,url):
    s=b.decode('utf-8-sig',errors='replace')
    return [(html.unescape(re.sub('<[^>]+>','',t)).strip(),urllib.parse.urljoin(url,html.unescape(h))) for h,t in re.findall(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>',s,re.S|re.I)]

def main():
    # Original requested/final URL and headers remain in each shared receipt.
    for r in shared:
        if r['id'].startswith('sos-'): source(r['id'])
    for year,idx in [('2024','sos-2024-county-recap-index'),('2018','sos-2018-general-county-index')]:
        entry=next(r for r in receipts if r['id']==idx)
        ll=links(source(idx),entry['final_url'])
        inventory=[]
        for literal,url in ll:
            if '.pdf' not in url.lower():continue
            key='sos-'+year+'-county-'+re.sub('[^a-z0-9]+','-',literal.lower()).strip('-')
            inventory.append(dict(literal=literal,url=url,source_id=key))
            if year=='2024': source(key,url,idx)
        savejson(OUT/'source'/('county-links-'+year+'.json'),inventory)
    for key,url,parent in [
      ('sos-2020-county-index','https://www.sos.ms.gov/elections/electionresults_aspx/elections_results_2020_county.aspx','sos-2020-iframe'),
      ('sos-2018-runoff-county-index','https://www.sos.ms.gov/elections/electionresults_aspx/elections_results_2018_countyrunoff.aspx','sos-2018-runoff-iframe'),
      ('sos-2022-general-iframe','https://www.sos.ms.gov/elections/electionresults_aspx/elections_results_2022_general.aspx','sos-results'),
      ('sos-2022-county-index','https://www.sos.ms.gov/elections/electionresults_aspx/elections_results_2022_county.aspx','sos-2022-general-iframe'),
      ('sos-active-voter-count-index','https://www.sos.ms.gov/elections-voting/active-voter-count-reports','sos-results'),
      ('sos-elections-current','https://www.sos.ms.gov/elections-voting','sos-results')]:
        source(key,url,parent)

if __name__=='__main__':main()
